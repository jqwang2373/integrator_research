from __future__ import annotations

import csv
import importlib
import json
import os
import platform
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

os.environ.setdefault("MPLBACKEND", "Agg")
os.environ.setdefault("MPLCONFIGDIR", "/tmp/mplconfig")

import numpy as np


HERE = Path(__file__).resolve().parent
WORK_ROOT = HERE.parent
REPO_ROOT = WORK_ROOT.parent
RESULTS = HERE / "results"
SBEL_C2 = REPO_ROOT / "external/sbel-reproducibility/2021/ASME/rA-formulation/C2"

if str(SBEL_C2) not in sys.path:
    sys.path.insert(0, str(SBEL_C2))


@dataclass(frozen=True)
class ModelSpec:
    name: str
    module: str
    setup_name: str
    body_count: int


MODELS = {
    "single_pendulum": ModelSpec(
        name="single_pendulum",
        module="SimEngineMBD.example_models.single_pendulum",
        setup_name="setup_single_pendulum",
        body_count=1,
    ),
    "four_link": ModelSpec(
        name="four_link",
        module="SimEngineMBD.example_models.four_link",
        setup_name="setup_four_link",
        body_count=3,
    ),
}


def scalarize(value: object) -> float:
    arr = np.asarray(value)
    if arr.size != 1:
        raise ValueError(f"Expected scalar-like constraint value, got shape {arr.shape}")
    return float(arr.reshape(-1)[0])


def patch_modern_numpy_scalar_assignments() -> list[str]:
    """Patch ConGroup scalar stores without modifying the upstream SBEL checkout."""

    patched = []

    def patch_module(module_name: str) -> None:
        module = importlib.import_module(module_name)
        cls = module.ConGroup

        def get_phi(self, t):
            store = getattr(self, "\u03a6")
            for i, con in enumerate(self.cons):
                store[i, 0] = scalarize(con.get_phi(t))
            return store

        def get_gamma(self, t):
            store = getattr(self, "\u03b3")
            for i, con in enumerate(self.cons):
                store[i, 0] = scalarize(con.get_gamma(t))
            return store

        def get_nu(self, t):
            store = self.nu
            for i, con in enumerate(self.cons):
                store[i, 0] = scalarize(con.get_nu(t))
            return store

        cls.get_phi = get_phi
        cls.get_gamma = get_gamma
        cls.get_nu = get_nu
        patched.append(module_name)

    for name in (
        "SimEngineMBD.rA.gcons_ra",
        "SimEngineMBD.rp.gcons_rp",
        "SimEngineMBD.rEps.gcons_reps",
    ):
        patch_module(name)

    return patched


def setup_system(model: ModelSpec, form: str, mode: str, h: float, t_end: float, tol: float):
    setup_fn: Callable = getattr(importlib.import_module(model.module), model.setup_name)
    args = [
        "--form",
        form,
        "--mode",
        mode,
        "--step_size",
        str(h),
        "--end_time",
        str(t_end),
        "--tol",
        str(tol),
        "--log",
        "warning",
        "--no-plot",
    ]
    system, params = setup_fn(args)

    # Some SBEL examples set these in setup_*; single_pendulum does not. Force
    # consistency in the harness so the requested step size is actually tested.
    system.h = params.h
    system.tol = params.tol
    return system, params


def orthogonality_error(system) -> float:
    max_err = 0.0
    for body in system.bodies:
        max_err = max(max_err, float(np.linalg.norm(body.A.T @ body.A - np.eye(3), ord="fro")))
    return max_err


def simulate(model: ModelSpec, form: str, mode: str, h: float, t_end: float, tol: float) -> dict:
    system, params = setup_system(model, form, mode, h, t_end, tol)
    system.initialize()

    step_count = int(round(params.t_end / params.h))
    if not np.isclose(step_count * params.h, params.t_end):
        raise ValueError(f"t_end={params.t_end} is not an integer multiple of h={params.h}")

    t_grid = np.arange(step_count + 1, dtype=float) * params.h
    pos = np.zeros((system.nb, 3, len(t_grid)))
    vel = np.zeros_like(pos)
    acc = np.zeros_like(pos)
    iterations = np.zeros(len(t_grid))
    phi_norm = np.zeros(len(t_grid))
    so3_norm = np.zeros(len(t_grid))

    start = time.perf_counter()
    for i, t in enumerate(t_grid):
        system.do_step(i, float(t))
        iterations[i] = system.k
        phi_norm[i] = float(np.linalg.norm(system.g_cons.get_phi(float(t))))
        so3_norm[i] = orthogonality_error(system)
        for j, body in enumerate(system.bodies):
            pos[j, :, i] = body.r.reshape(3)
            vel[j, :, i] = body.dr.reshape(3)
            acc[j, :, i] = body.ddr.reshape(3)
    runtime = time.perf_counter() - start

    return {
        "model": model.name,
        "form": form,
        "mode": mode,
        "h": h,
        "t_end": t_end,
        "tol": tol,
        "steps": step_count,
        "pos": pos,
        "vel": vel,
        "acc": acc,
        "iterations": iterations,
        "max_iterations": float(np.max(iterations)),
        "avg_iterations": float(np.mean(iterations)),
        "max_phi_norm": float(np.max(phi_norm)),
        "max_so3_fro": float(np.max(so3_norm)),
        "runtime_sec": runtime,
    }


def final_error(reference: dict, candidate: dict) -> dict:
    out = {}
    for key in ("pos", "vel", "acc"):
        diff = reference[key][:, :, -1] - candidate[key][:, :, -1]
        out[f"{key}_final_linf"] = float(np.max(np.abs(diff)))
        out[f"{key}_final_l2"] = float(np.linalg.norm(diff.reshape(-1)))
    return out


def trajectory_error(reference: dict, candidate: dict) -> dict:
    ratio = candidate["h"] / reference["h"]
    stride = int(round(ratio))
    if not np.isclose(stride, ratio):
        raise ValueError(f"Reference h={reference['h']} is not nested in candidate h={candidate['h']}")
    ref_slice = {key: reference[key][:, :, ::stride] for key in ("pos", "vel", "acc")}
    out = {}
    for key in ("pos", "vel", "acc"):
        if ref_slice[key].shape != candidate[key].shape:
            raise ValueError(f"Mismatched {key} shape: {ref_slice[key].shape} vs {candidate[key].shape}")
        diff = ref_slice[key] - candidate[key]
        out[f"{key}_traj_linf"] = float(np.max(np.abs(diff)))
        out[f"{key}_traj_l2"] = float(np.linalg.norm(diff.reshape(-1)))
    return out


def estimate_order(hs: list[float], errors: list[float]) -> float:
    clean = [(h, e) for h, e in zip(hs, errors) if np.isfinite(e) and e > 0]
    if len(clean) < 2:
        return float("nan")
    x = np.log([item[0] for item in clean])
    y = np.log([item[1] for item in clean])
    slope, _ = np.polyfit(x, y, 1)
    return float(slope)


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def run_baseline() -> dict:
    rows = []
    summary: dict[str, dict] = {}
    t_end = 0.4
    hs = [0.04, 0.02, 0.01, 0.005]
    form = "rA"
    reference_h = 0.0005

    for model_name in ("single_pendulum", "four_link"):
        model = MODELS[model_name]
        reference = simulate(model, form, "kinematics", reference_h, t_end, 1e-12)
        velocity_errors = []
        acceleration_final_errors = []
        model_runs = []
        for h in hs:
            # Match the tolerance schedule used by SBEL's order_analysis.py.
            tol = 1e-10 / (h * h)
            try:
                run = simulate(model, form, "dynamics", h, t_end, tol)
                err = {**final_error(reference, run), **trajectory_error(reference, run)}
                status = "ok"
                velocity_error = err["vel_traj_linf"]
                acceleration_final_error = err["acc_final_linf"]
            except Exception as exc:  # Keep failed runs in the report.
                run = {
                    "steps": int(round(t_end / h)),
                    "avg_iterations": float("nan"),
                    "max_iterations": float("nan"),
                    "max_phi_norm": float("nan"),
                    "max_so3_fro": float("nan"),
                    "runtime_sec": float("nan"),
                }
                err = {
                    "pos_final_linf": float("nan"),
                    "pos_final_l2": float("nan"),
                    "vel_final_linf": float("nan"),
                    "vel_final_l2": float("nan"),
                    "acc_final_linf": float("nan"),
                    "acc_final_l2": float("nan"),
                    "pos_traj_linf": float("nan"),
                    "pos_traj_l2": float("nan"),
                    "vel_traj_linf": float("nan"),
                    "vel_traj_l2": float("nan"),
                    "acc_traj_linf": float("nan"),
                    "acc_traj_l2": float("nan"),
                }
                status = f"failed: {type(exc).__name__}: {exc}"
                velocity_error = float("nan")
                acceleration_final_error = float("nan")

            velocity_errors.append(velocity_error)
            acceleration_final_errors.append(acceleration_final_error)
            model_runs.append({"h": h, "status": status, **run, **err})
            rows.append(
                {
                    "model": model_name,
                    "form": form,
                    "h": f"{h:.10g}",
                    "steps": run["steps"],
                    "status": status,
                    "pos_final_linf": f"{err['pos_final_linf']:.16e}",
                    "vel_final_linf": f"{err['vel_final_linf']:.16e}",
                    "acc_final_linf": f"{err['acc_final_linf']:.16e}",
                    "pos_traj_linf": f"{err['pos_traj_linf']:.16e}",
                    "vel_traj_linf": f"{err['vel_traj_linf']:.16e}",
                    "acc_traj_linf": f"{err['acc_traj_linf']:.16e}",
                    "avg_iterations": f"{run['avg_iterations']:.8e}",
                    "max_iterations": f"{run['max_iterations']:.8e}",
                    "max_phi_norm": f"{run['max_phi_norm']:.16e}",
                    "max_so3_fro": f"{run['max_so3_fro']:.16e}",
                    "runtime_sec": f"{run['runtime_sec']:.8e}",
                }
            )

        summary[model_name] = {
            "reference": {
                "mode": "kinematics",
                "h": reference_h,
                "t_end": t_end,
                "max_phi_norm": reference["max_phi_norm"],
                "max_so3_fro": reference["max_so3_fro"],
                "runtime_sec": reference["runtime_sec"],
            },
            "dynamic_step_sizes": hs,
            "vel_traj_linf_observed_order": estimate_order(hs, velocity_errors),
            "acc_final_linf_observed_order": estimate_order(hs, acceleration_final_errors),
            "runs": [
                {
                    key: value
                    for key, value in item.items()
                    if key not in {"pos", "vel", "acc", "iterations"}
                }
                for item in model_runs
            ],
        }

    write_csv(RESULTS / "sbel_ra_convergence.csv", rows)
    return summary


def write_report(summary: dict) -> None:
    report = [
        "# v003 Experiment Report",
        "",
        "Generated by `run_v003.py`.",
        "",
        "## Environment",
        "",
        f"- Python: {summary['python']}",
        f"- NumPy: {summary['numpy']}",
        f"- SBEL C2 path: `{summary['sbel_c2']}`",
        f"- SBEL commit: `{summary['sbel_commit']}`",
        "",
        "## Compatibility Notes",
        "",
        "- Upstream SBEL files were not edited.",
        "- Current NumPy rejects assignment of 1x1 arrays into scalar slots in `ConGroup.get_phi/get_gamma/get_nu`; v003 patches those methods at runtime with scalar extraction.",
        "- The `single_pendulum` setup does not propagate parsed `step_size/tol` into `SystemRA`; v003 sets `system.h` and `system.tol` explicitly in the harness.",
        "",
        "## rA Baseline Results",
        "",
    ]
    for model, item in summary["baseline"].items():
        report.append(
            f"- `{model}`: trajectory velocity observed order "
            f"{item['vel_traj_linf_observed_order']:.3f}, final acceleration observed order "
            f"{item['acc_final_linf_observed_order']:.3f} over h={item['dynamic_step_sizes']}."
        )
        finest = item["runs"][-1]
        report.append(
            f"  Finest h={finest['h']}: velocity trajectory Linf {finest['vel_traj_linf']:.3e}, "
            f"final acceleration Linf {finest['acc_final_linf']:.3e}, "
            f"max constraint norm {finest['max_phi_norm']:.3e}, "
            f"max SO(3) Frobenius defect {finest['max_so3_fro']:.3e}."
        )

    report.extend(
        [
            "",
            "## Interpretation",
            "",
            "- The rA code path is a useful lab baseline because it evolves rotation matrices with a right-multiplied exponential map.",
            "- In `SystemRA`, `solver_order` is not consumed in the dynamics step; the code uses a single-step implicit Euler-like update for position, velocity, and orientation.",
            "- The dynamics tolerance schedule follows SBEL's `order_analysis.py` (`1e-10 / h^2`), which favors reproducing their harness over enforcing a uniform Newton residual.",
            "- This makes v003 a baseline for correctness and reproducibility, not yet a high-order competitor to the 2026 Lie-group TFE paper.",
            "- v004 should add a higher-order structure-preserving mechanical test, rather than only prescribed-omega SO(3) kinematics.",
            "",
        ]
    )
    (RESULTS / "v003_report.md").write_text("\n".join(report), encoding="utf-8")


def git_commit_for_sbel() -> str:
    import subprocess

    try:
        return subprocess.check_output(
            ["git", "-C", str(REPO_ROOT / "external/sbel-reproducibility"), "rev-parse", "HEAD"],
            text=True,
        ).strip()
    except Exception:
        return "unknown"


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    patched = patch_modern_numpy_scalar_assignments()
    started = time.perf_counter()
    summary = {
        "version": "v003_sbel_ra_repro",
        "python": platform.python_version(),
        "platform": platform.platform(),
        "numpy": np.__version__,
        "sbel_c2": str(SBEL_C2),
        "sbel_commit": git_commit_for_sbel(),
        "runtime_patches": patched,
        "baseline": run_baseline(),
    }
    summary["runtime_sec"] = time.perf_counter() - started
    with (RESULTS / "summary.json").open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, sort_keys=True)
    write_report(summary)


if __name__ == "__main__":
    main()
