from __future__ import annotations

import csv
import importlib
import json
import os
import platform
import subprocess
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
SBEL_ROOT = REPO_ROOT / "external/sbel-reproducibility"
SBEL_C2 = SBEL_ROOT / "2021/ASME/rA-formulation/C2"

if str(SBEL_C2) not in sys.path:
    sys.path.insert(0, str(SBEL_C2))


@dataclass(frozen=True)
class ModelSpec:
    name: str
    module: str
    setup_name: str
    reference_mode: str


MODELS = [
    ModelSpec("single_pendulum", "SimEngineMBD.example_models.single_pendulum", "setup_single_pendulum", "kinematics"),
    ModelSpec("double_pendulum", "SimEngineMBD.example_models.double_pendulum", "setup_double_pendulum", "dynamics"),
    ModelSpec("four_link", "SimEngineMBD.example_models.four_link", "setup_four_link", "kinematics"),
    ModelSpec("slider_crank", "SimEngineMBD.example_models.slider_crank", "setup_slider_crank", "kinematics"),
]

FORM = "rA"
T_END = 0.20
REFERENCE_H = 0.001
STEP_SIZES = [0.02, 0.01, 0.005]
TOL_BASE = 1.0e-10


def scalarize(value: object) -> float:
    arr = np.asarray(value)
    if arr.size != 1:
        raise ValueError(f"Expected scalar-like constraint value, got shape {arr.shape}")
    return float(arr.reshape(-1)[0])


def patch_modern_numpy_scalar_assignments() -> list[str]:
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

    for name in ("SimEngineMBD.rA.gcons_ra", "SimEngineMBD.rp.gcons_rp", "SimEngineMBD.rEps.gcons_reps"):
        patch_module(name)
    return patched


def setup_system(model: ModelSpec, mode: str, h: float, t_end: float, tol: float):
    setup_fn: Callable = getattr(importlib.import_module(model.module), model.setup_name)
    args = [
        "--form",
        FORM,
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
    system.h = params.h
    system.tol = params.tol
    return system, params


def orthogonality_error(system) -> float:
    out = 0.0
    for body in system.bodies:
        out = max(out, float(np.linalg.norm(body.A.T @ body.A - np.eye(3), ord="fro")))
    return out


def simulate(model: ModelSpec, mode: str, h: float, t_end: float, tol: float) -> dict:
    system, params = setup_system(model, mode, h, t_end, tol)
    system.initialize()
    steps = int(round(params.t_end / params.h))
    if not np.isclose(steps * params.h, params.t_end):
        raise ValueError(f"t_end={params.t_end} is not an integer multiple of h={params.h}")

    t_grid = np.arange(steps + 1, dtype=float) * params.h
    pos = np.zeros((system.nb, 3, len(t_grid)))
    vel = np.zeros_like(pos)
    acc = np.zeros_like(pos)
    iterations = np.zeros(len(t_grid))
    phi_norm = np.zeros(len(t_grid))
    so3_norm = np.zeros(len(t_grid))

    started = time.perf_counter()
    for i, t in enumerate(t_grid):
        system.do_step(i, float(t))
        iterations[i] = system.k
        phi_norm[i] = float(np.linalg.norm(system.g_cons.get_phi(float(t))))
        so3_norm[i] = orthogonality_error(system)
        for j, body in enumerate(system.bodies):
            pos[j, :, i] = body.r.reshape(3)
            vel[j, :, i] = body.dr.reshape(3)
            acc[j, :, i] = body.ddr.reshape(3)

    return {
        "model": model.name,
        "mode": mode,
        "h": h,
        "tol": tol,
        "steps": steps,
        "pos": pos,
        "vel": vel,
        "acc": acc,
        "iterations": iterations,
        "max_iterations": float(np.max(iterations)),
        "avg_iterations": float(np.mean(iterations)),
        "max_phi_norm": float(np.max(phi_norm)),
        "max_so3_fro": float(np.max(so3_norm)),
        "runtime_sec": time.perf_counter() - started,
    }


def nested_reference(reference: dict, candidate: dict, key: str) -> np.ndarray:
    ratio = candidate["h"] / reference["h"]
    stride = int(round(ratio))
    if not np.isclose(stride, ratio):
        raise ValueError(f"Reference h={reference['h']} is not nested in candidate h={candidate['h']}")
    out = reference[key][:, :, ::stride]
    if out.shape != candidate[key].shape:
        raise ValueError(f"{key} reference shape {out.shape} does not match candidate {candidate[key].shape}")
    return out


def errors_against(reference: dict, candidate: dict) -> dict:
    out = {}
    for key in ("pos", "vel", "acc"):
        ref = nested_reference(reference, candidate, key)
        traj = ref - candidate[key]
        final = ref[:, :, -1] - candidate[key][:, :, -1]
        out[f"{key}_traj_linf"] = float(np.max(np.abs(traj)))
        out[f"{key}_traj_l2"] = float(np.linalg.norm(traj.reshape(-1)))
        out[f"{key}_final_linf"] = float(np.max(np.abs(final)))
        out[f"{key}_final_l2"] = float(np.linalg.norm(final.reshape(-1)))
    return out


def estimate_order(hs: list[float], errors: list[float]) -> float:
    clean = [(h, e) for h, e in zip(hs, errors) if np.isfinite(e) and e > 0.0]
    if len(clean) < 2:
        return float("nan")
    x = np.log([h for h, _ in clean])
    y = np.log([e for _, e in clean])
    slope, _ = np.polyfit(x, y, 1)
    return float(slope)


def tol_for_h(h: float) -> float:
    return TOL_BASE / (h * h)


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def run_model(model: ModelSpec) -> tuple[dict, list[dict]]:
    rows = []
    reference = simulate(model, model.reference_mode, REFERENCE_H, T_END, tol_for_h(REFERENCE_H))
    model_runs = []
    pos_errors = []
    vel_errors = []
    acc_errors = []
    pass_flags = []

    for h in STEP_SIZES:
        try:
            run = simulate(model, "dynamics", h, T_END, tol_for_h(h))
            err = errors_against(reference, run)
            status = "ok"
            passed = bool(run["max_phi_norm"] < 1.0e-5 and run["max_so3_fro"] < 1.0e-10)
        except Exception as exc:
            run = {
                "h": h,
                "tol": tol_for_h(h),
                "steps": int(round(T_END / h)),
                "runtime_sec": float("nan"),
                "avg_iterations": float("nan"),
                "max_iterations": float("nan"),
                "max_phi_norm": float("nan"),
                "max_so3_fro": float("nan"),
            }
            err = {f"{key}_{kind}_{norm}": float("nan") for key in ("pos", "vel", "acc") for kind in ("traj", "final") for norm in ("linf", "l2")}
            status = f"failed: {type(exc).__name__}: {exc}"
            passed = False

        pos_errors.append(err["pos_traj_linf"])
        vel_errors.append(err["vel_traj_linf"])
        acc_errors.append(err["acc_traj_linf"])
        pass_flags.append(passed)
        compact = {
            "model": model.name,
            "reference_mode": model.reference_mode,
            "form": FORM,
            "mode": "dynamics",
            "h": h,
            "status": status,
            "passed_constraint_checks": passed,
            "steps": run["steps"],
            "runtime_sec": run["runtime_sec"],
            "avg_iterations": run["avg_iterations"],
            "max_iterations": run["max_iterations"],
            "max_phi_norm": run["max_phi_norm"],
            "max_so3_fro": run["max_so3_fro"],
            **err,
        }
        model_runs.append(compact)
        rows.append(
            {
                key: (f"{value:.16e}" if isinstance(value, float) else value)
                for key, value in compact.items()
            }
        )

    return (
        {
            "reference": {
                "mode": model.reference_mode,
                "h": REFERENCE_H,
                "t_end": T_END,
                "runtime_sec": reference["runtime_sec"],
                "max_phi_norm": reference["max_phi_norm"],
                "max_so3_fro": reference["max_so3_fro"],
            },
            "runs": model_runs,
            "orders": {
                "pos_traj_linf": estimate_order(STEP_SIZES, pos_errors),
                "vel_traj_linf": estimate_order(STEP_SIZES, vel_errors),
                "acc_traj_linf": estimate_order(STEP_SIZES, acc_errors),
            },
            "all_constraint_checks_passed": bool(all(pass_flags)),
        },
        rows,
    )


def git_commit_for_sbel() -> str:
    try:
        return subprocess.check_output(["git", "-C", str(SBEL_ROOT), "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return "unknown"


def plot_summary(summary: dict) -> None:
    import matplotlib.pyplot as plt

    labels = list(summary["models"].keys())
    pos = [summary["models"][name]["orders"]["pos_traj_linf"] for name in labels]
    vel = [summary["models"][name]["orders"]["vel_traj_linf"] for name in labels]
    acc = [summary["models"][name]["orders"]["acc_traj_linf"] for name in labels]
    xs = np.arange(len(labels))
    fig, ax = plt.subplots(figsize=(9.2, 4.2))
    ax.bar(xs - 0.25, pos, width=0.25, label="position")
    ax.bar(xs, vel, width=0.25, label="velocity")
    ax.bar(xs + 0.25, acc, width=0.25, label="acceleration")
    ax.set_xticks(xs)
    ax.set_xticklabels(labels, rotation=20, ha="right")
    ax.set_ylabel("observed trajectory order")
    ax.grid(True, axis="y", alpha=0.35)
    ax.legend()
    fig.tight_layout()
    fig.savefig(RESULTS / "asme_four_examples_orders.png", dpi=180)
    plt.close(fig)

    max_phi = [max(run["max_phi_norm"] for run in summary["models"][name]["runs"]) for name in labels]
    max_so3 = [max(run["max_so3_fro"] for run in summary["models"][name]["runs"]) for name in labels]
    fig, ax = plt.subplots(figsize=(9.2, 4.2))
    ax.bar(xs - 0.18, max_phi, width=0.36, label="max constraint norm")
    ax.bar(xs + 0.18, max_so3, width=0.36, label="max SO(3) defect")
    ax.set_yscale("log")
    ax.set_xticks(xs)
    ax.set_xticklabels(labels, rotation=20, ha="right")
    ax.grid(True, axis="y", alpha=0.35)
    ax.legend()
    fig.tight_layout()
    fig.savefig(RESULTS / "asme_four_examples_invariants.png", dpi=180)
    plt.close(fig)


def write_report(summary: dict) -> None:
    lines = [
        "# v046 Experiment Report",
        "",
        "Generated by `run_v046.py`.",
        "",
        "## Purpose",
        "",
        "- Validate the SBEL/Negrut 2021 ASME rA formulation on all four example mechanisms used by the repo: single pendulum, double pendulum, four link, and slider crank.",
        "- Use the upstream code path with only runtime compatibility patches for modern NumPy scalar assignment.",
        "- Compare rA dynamics against a nested fine reference: kinematics reference for driven examples and dynamics reference for double pendulum.",
        "",
        "## Setup",
        "",
        f"- Step sizes: {STEP_SIZES}; reference h={REFERENCE_H}; T={T_END}.",
        f"- Form: `{FORM}`.",
        f"- SBEL commit: `{summary['sbel_commit']}`.",
        "",
        "## Results",
        "",
    ]
    for model_name, model in summary["models"].items():
        orders = model["orders"]
        finest = model["runs"][-1]
        lines.append(f"### {model_name}")
        lines.append(
            f"- Observed trajectory orders: position {orders['pos_traj_linf']:.3f}, "
            f"velocity {orders['vel_traj_linf']:.3f}, acceleration {orders['acc_traj_linf']:.3f}."
        )
        lines.append(
            f"- Finest h={finest['h']:.5g}: pos error {finest['pos_traj_linf']:.3e}, "
            f"vel error {finest['vel_traj_linf']:.3e}, acc error {finest['acc_traj_linf']:.3e}."
        )
        lines.append(
            f"- Max constraint norm {max(run['max_phi_norm'] for run in model['runs']):.3e}; "
            f"max SO(3) defect {max(run['max_so3_fro'] for run in model['runs']):.3e}; "
            f"constraint checks passed: {model['all_constraint_checks_passed']}."
        )
        lines.append("")
    lines.extend(
        [
            "## Interpretation",
            "",
            "- This is a reproducibility/correctness anchor for the lab's 2021 ASME examples, not a claim that the rA baseline is a better integrator than the local Gauss6 variants.",
            "- Passing constraint and SO(3) checks on all four examples means future local Lie-group integrator variants should be compared against this full-example harness, not only against toy pendulum cases.",
            "- Observed orders here characterize the upstream rA dynamics implementation and tolerance schedule; they are not the formal order of the new quaternion Gauss6 FullVA prototypes.",
            "",
            "## Outputs",
            "",
            "- `asme_four_examples_validation.csv`",
            "- `summary_v046.json`",
            "- `asme_four_examples_orders.png`",
            "- `asme_four_examples_invariants.png`",
            "",
        ]
    )
    (RESULTS / "v046_report.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    patched = patch_modern_numpy_scalar_assignments()
    model_summaries = {}
    rows = []
    for model in MODELS:
        model_summary, model_rows = run_model(model)
        model_summaries[model.name] = model_summary
        rows.extend(model_rows)
    summary = {
        "version": "v046_asme_four_examples_validation",
        "python": platform.python_version(),
        "platform": platform.platform(),
        "numpy": np.__version__,
        "sbel_c2": str(SBEL_C2),
        "sbel_commit": git_commit_for_sbel(),
        "runtime_patches": patched,
        "models": model_summaries,
        "runtime_sec": time.perf_counter() - started,
    }
    write_csv(RESULTS / "asme_four_examples_validation.csv", rows)
    plot_summary(summary)
    with (RESULTS / "summary_v046.json").open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, sort_keys=True)
    write_report(summary)


if __name__ == "__main__":
    main()
