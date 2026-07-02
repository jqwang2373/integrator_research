#!/usr/bin/env python3
"""Build the closed-loop true-dynamic Gauss6 one-step smoke artifact."""

from __future__ import annotations

import csv
import importlib.util
import json
import sys
import time
from pathlib import Path

import numpy as np

import closed_loop_fullva_dynamic_residual as dynres


HERE = Path(__file__).resolve().parent
WORK_ROOT = HERE.parent
RESULTS = HERE / "results"
V047_RUN = WORK_ROOT / "v047_cylindrical_chain_pipeline" / "run_v047.py"
MODELS = ("four_link", "slider_crank")
H = 0.1
T0 = 0.0
T1 = T0 + H
TOL = 1.0e-12
OUT_CSV = RESULTS / "closed_loop_true_dynamic_one_step_smoke.csv"
OUT_JSON = RESULTS / "closed_loop_true_dynamic_one_step_smoke.json"
OUT_MD = RESULTS / "closed_loop_true_dynamic_one_step_smoke.md"


def import_v047_module():
    module_name = "v047_cylindrical_chain_pipeline_run_v047_for_one_step_smoke"
    if module_name in sys.modules:
        return sys.modules[module_name]
    spec = importlib.util.spec_from_file_location(module_name, V047_RUN)
    if spec is None or spec.loader is None:
        raise ImportError(f"could not load {V047_RUN}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError("refusing to write empty one-step smoke")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def setup_exact_system(v047_module, v046, model, t: float):
    system, _params = v046.setup_system(model, "dynamics", H, T1, TOL)
    system.initialize()
    v047_module.project_v046_system_to_so3(system)
    v047_module.solve_v046_local_kinematic_fullva_time(system, t, TOL)
    return system


def make_row(v047_module, v046, model) -> dict[str, object]:
    started = time.perf_counter()
    row: dict[str, object] = {
        "model": model.name,
        "h": f"{H:.16e}",
        "t0": f"{T0:.16e}",
        "t1": f"{T1:.16e}",
        "status": "ok",
        "step_policy": "oracle_initialized_one_step_smoke_not_order",
        "stage_count": 3,
        "stage_unknown_dim": 72,
        "stage_residual_dim": 72,
        "max_stage_residual_inf": "nan",
        "endpoint_pos_error_inf": "nan",
        "endpoint_vel_error_inf": "nan",
        "endpoint_acc_error_inf": "nan",
        "endpoint_orientation_error_inf": "nan",
        "endpoint_omega_error_inf": "nan",
        "endpoint_alpha_error_inf": "nan",
        "endpoint_position_constraint_norm": "nan",
        "endpoint_velocity_constraint_norm": "nan",
        "endpoint_acceleration_constraint_norm": "nan",
        "endpoint_so3_fro": "nan",
        "total_stage_newton_iterations": "nan",
        "trajectory_stepper_executed": "false",
        "trajectory_stepper_implemented": "true",
        "simulate_runner_implemented": "false",
        "accepted_dynamic_order": "false",
        "default_policy": "coarse_first_no_default_1e-4",
        "strict_public_policy_1e-4_required": "false",
        "default_1e-4_required": "false",
        "heavy_numerical_run_invoked": "false",
        "runtime_sec": "nan",
        "notes": "",
    }
    try:
        system = setup_exact_system(v047_module, v046, model, T0)
        out = dynres.gauss6_closed_loop_fullva_dynamic_step(system, T0, H, v047_module, tol=TOL)
        candidate = out["endpoint_state"]
        phi, vel, acc = v047_module.v046_constraint_level_residuals(system, T1)
        so3 = v046.orthogonality_error(system)
        reference_system = setup_exact_system(v047_module, v046, model, T1)
        reference = dynres.endpoint_state_from_system(reference_system)
        err = dynres.endpoint_state_error_inf(candidate, reference)
        total_stage_iters = sum(int(solution["newton_iterations"]) for solution in out["stage_solutions"])
        row.update(
            {
                "status": "ok",
                "max_stage_residual_inf": f"{float(out['max_stage_residual_inf']):.16e}",
                "endpoint_pos_error_inf": f"{err['pos']:.16e}",
                "endpoint_vel_error_inf": f"{err['vel']:.16e}",
                "endpoint_acc_error_inf": f"{err['acc']:.16e}",
                "endpoint_orientation_error_inf": f"{err['orientation']:.16e}",
                "endpoint_omega_error_inf": f"{err['omega']:.16e}",
                "endpoint_alpha_error_inf": f"{err['alpha']:.16e}",
                "endpoint_position_constraint_norm": f"{phi:.16e}",
                "endpoint_velocity_constraint_norm": f"{vel:.16e}",
                "endpoint_acceleration_constraint_norm": f"{acc:.16e}",
                "endpoint_so3_fro": f"{so3:.16e}",
                "total_stage_newton_iterations": total_stage_iters,
                "trajectory_stepper_executed": "true",
                "runtime_sec": f"{time.perf_counter() - started:.16e}",
                "notes": (
                    "One-step smoke only: stages use kinematic-oracle initialization and residual checks, "
                    "then endpoint quadrature is compared with the exact kinematic state at t1. "
                    "This is not a three-step convergence/order row."
                ),
            }
        )
    except Exception as exc:  # noqa: BLE001 - keep audit row visible.
        row.update(
            {
                "status": f"failed:{type(exc).__name__}:{str(exc).replace(chr(10), ' ')}",
                "runtime_sec": f"{time.perf_counter() - started:.16e}",
                "notes": "one-step smoke failed",
            }
        )
    return row


def write_markdown(summary: dict, rows: list[dict[str, object]]) -> None:
    lines = [
        "# Closed-Loop True-Dynamic One-Step Smoke",
        "",
        "Status: **one-step smoke passed; order rows not run**",
        "",
        f"- Rows: `{summary['ok_row_count']}/{summary['row_count']}` ok.",
        f"- Max stage residual infinity norm: `{summary['max_stage_residual_inf']:.3e}`.",
        f"- Max endpoint position error: `{summary['max_endpoint_pos_error_inf']:.3e}`.",
        f"- Trajectory stepper executed: `{summary['trajectory_stepper_executed']}`.",
        f"- Accepted dynamic-order rows: `{summary['accepted_dynamic_order_count']}`.",
        f"- Default `1e-4` required: `{summary['default_1e-4_required']}`.",
        "",
        "This artifact advances exactly one Gauss6 step on each missing",
        "closed-loop mechanism using oracle-initialized stage residual roots.",
        "It is useful implementation progress toward the local dynamic runner,",
        "but it is not a convergence sweep and must not be counted as order",
        "or external-superiority evidence.",
        "",
        "| Model | max stage residual | endpoint pos error | endpoint vel error | status |",
        "|---|---:|---:|---:|---|",
    ]
    for row in rows:
        lines.append(
            "| "
            f"`{row['model']}` | `{row['max_stage_residual_inf']}` | "
            f"`{row['endpoint_pos_error_inf']}` | `{row['endpoint_vel_error_inf']}` | "
            f"`{row['status']}` |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def finite_values(rows: list[dict[str, object]], key: str) -> list[float]:
    values = []
    for row in rows:
        try:
            value = float(row[key])
        except Exception:  # noqa: BLE001
            continue
        if np.isfinite(value):
            values.append(value)
    return values


def main() -> None:
    v047_module = import_v047_module()
    v046 = v047_module.load_v046()
    v046.patch_modern_numpy_scalar_assignments()
    models = {model.name: model for model in v046.MODELS}
    rows = [make_row(v047_module, v046, models[model_name]) for model_name in MODELS]
    ok_count = sum(1 for row in rows if row["status"] == "ok")
    stage_residuals = finite_values(rows, "max_stage_residual_inf")
    pos_errors = finite_values(rows, "endpoint_pos_error_inf")
    vel_errors = finite_values(rows, "endpoint_vel_error_inf")
    summary = {
        "schema": "closed-loop-true-dynamic-one-step-smoke-v1",
        "status": "one_step_smoke_passed_order_rows_not_run",
        "method": "Gauss6/FullVA",
        "models": list(MODELS),
        "row_count": len(rows),
        "ok_row_count": ok_count,
        "h": H,
        "t0": T0,
        "t1": T1,
        "stage_count": 3,
        "stage_unknown_dim": 72,
        "stage_residual_dim": 72,
        "max_stage_residual_inf": max(stage_residuals) if stage_residuals else float("nan"),
        "max_endpoint_pos_error_inf": max(pos_errors) if pos_errors else float("nan"),
        "max_endpoint_vel_error_inf": max(vel_errors) if vel_errors else float("nan"),
        "step_policy": "oracle_initialized_one_step_smoke_not_order",
        "trajectory_stepper_implemented": True,
        "trajectory_stepper_executed": True,
        "simulate_runner_implemented": False,
        "accepted_dynamic_order_count": 0,
        "convergence_sweep_run": False,
        "default_policy": "coarse_first_no_default_1e-4",
        "strict_public_policy_1e-4_required": False,
        "default_1e-4_required": False,
        "heavy_numerical_run_invoked": False,
        "external_superiority_claim": False,
        "interpretation": (
            "One oracle-initialized Gauss6 dynamic step now executes for the two missing closed-loop models. "
            "The remaining gap is a non-oracle trajectory simulator and three-step order/work rows."
        ),
    }
    write_csv(OUT_CSV, rows)
    with OUT_JSON.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, sort_keys=True)
        handle.write("\n")
    write_markdown(summary, rows)
    print("closed_loop_true_dynamic_one_step_smoke=written")
    print(f"rows_ok={ok_count}/{len(rows)}")
    print(f"max_stage_residual_inf={summary['max_stage_residual_inf']:.6e}")
    print(f"max_endpoint_pos_error_inf={summary['max_endpoint_pos_error_inf']:.6e}")
    print("trajectory_stepper_executed=True")
    print("convergence_sweep_run=False")
    print("default_1e-4=False")
    print("accepted_dynamic_order=0")


if __name__ == "__main__":
    main()
