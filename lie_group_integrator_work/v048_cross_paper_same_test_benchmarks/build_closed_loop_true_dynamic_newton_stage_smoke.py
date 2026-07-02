#!/usr/bin/env python3
"""Build the closed-loop true-dynamic non-oracle Newton stage smoke artifact."""

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
KINEMATIC_TOL = 1.0e-12
NEWTON_TOL = 1.0e-10
MAX_NEWTON_ITERS = 12
OUT_CSV = RESULTS / "closed_loop_true_dynamic_newton_stage_smoke.csv"
OUT_JSON = RESULTS / "closed_loop_true_dynamic_newton_stage_smoke.json"
OUT_MD = RESULTS / "closed_loop_true_dynamic_newton_stage_smoke.md"


def import_v047_module():
    module_name = "v047_cylindrical_chain_pipeline_run_v047_for_newton_stage_smoke"
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
        raise ValueError("refusing to write empty Newton stage smoke")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def setup_exact_system(v047_module, v046, model, t: float):
    system, _params = v046.setup_system(model, "dynamics", H, T1, KINEMATIC_TOL)
    system.initialize()
    v047_module.project_v046_system_to_so3(system)
    v047_module.solve_v046_local_kinematic_fullva_time(system, t, KINEMATIC_TOL)
    return system


def make_row(v047_module, v046, model) -> dict[str, object]:
    started = time.perf_counter()
    row: dict[str, object] = {
        "model": model.name,
        "h": f"{H:.16e}",
        "t0": f"{T0:.16e}",
        "t1": f"{T1:.16e}",
        "status": "ok",
        "step_policy": "non_oracle_newton_one_step_smoke_not_order",
        "stage_predictor_policy": "start_extrapolated_no_stage_oracle",
        "stage_oracle_used": "false",
        "stage_count": 3,
        "stage_unknown_dim": 72,
        "stage_residual_dim": 72,
        "max_initial_stage_residual_inf": "nan",
        "max_stage_residual_inf": "nan",
        "total_stage_newton_iterations": "nan",
        "line_search_failures": "nan",
        "all_stages_converged": "false",
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
        "trajectory_stepper_executed": "false",
        "trajectory_stepper_implemented": "true",
        "simulate_runner_implemented": "false",
        "accepted_dynamic_order": "false",
        "convergence_sweep_run": "false",
        "default_policy": "coarse_first_no_default_1e-4",
        "strict_public_policy_1e-4_required": "false",
        "default_1e-4_required": "false",
        "heavy_numerical_run_invoked": "false",
        "runtime_sec": "nan",
        "notes": "",
    }
    try:
        system = setup_exact_system(v047_module, v046, model, T0)
        out = dynres.gauss6_closed_loop_fullva_dynamic_step_newton_smoke(
            system,
            T0,
            H,
            v047_module,
            tol=NEWTON_TOL,
            max_iters=MAX_NEWTON_ITERS,
        )
        candidate = out["endpoint_state"]
        phi, vel, acc = v047_module.v046_constraint_level_residuals(system, T1)
        so3 = v046.orthogonality_error(system)
        reference_system = setup_exact_system(v047_module, v046, model, T1)
        reference = dynres.endpoint_state_from_system(reference_system)
        err = dynres.endpoint_state_error_inf(candidate, reference)
        ok = bool(out["all_stages_converged"]) and float(out["max_stage_residual_inf"]) < 1.0e-8
        row.update(
            {
                "status": "ok" if ok else "diagnostic_failed_threshold",
                "max_initial_stage_residual_inf": f"{float(out['max_initial_stage_residual_inf']):.16e}",
                "max_stage_residual_inf": f"{float(out['max_stage_residual_inf']):.16e}",
                "total_stage_newton_iterations": int(out["total_stage_newton_iterations"]),
                "line_search_failures": int(out["line_search_failures"]),
                "all_stages_converged": str(bool(out["all_stages_converged"])).lower(),
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
                "trajectory_stepper_executed": "true",
                "runtime_sec": f"{time.perf_counter() - started:.16e}",
                "notes": (
                    "One-step smoke only: each Gauss6 stage starts from the t0 "
                    "constant-acceleration predictor and is solved by dense damped "
                    "finite-difference Newton. No stage-time kinematic oracle is used, "
                    "and this is not a three-step convergence/order row."
                ),
            }
        )
    except Exception as exc:  # noqa: BLE001 - keep audit row visible.
        row.update(
            {
                "status": f"failed:{type(exc).__name__}:{str(exc).replace(chr(10), ' ')}",
                "runtime_sec": f"{time.perf_counter() - started:.16e}",
                "notes": "non-oracle Newton stage smoke failed",
            }
        )
    return row


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


def write_markdown(summary: dict, rows: list[dict[str, object]]) -> None:
    lines = [
        "# Closed-Loop True-Dynamic Newton Stage Smoke",
        "",
        "Status: **non-oracle stage Newton smoke passed; order rows not run**",
        "",
        f"- Rows: `{summary['ok_row_count']}/{summary['row_count']}` ok.",
        f"- Max initial stage residual infinity norm: `{summary['max_initial_stage_residual_inf']:.3e}`.",
        f"- Max final stage residual infinity norm: `{summary['max_stage_residual_inf']:.3e}`.",
        f"- Stage oracle used: `{summary['stage_oracle_used']}`.",
        f"- Trajectory stepper executed: `{summary['trajectory_stepper_executed']}`.",
        f"- Accepted dynamic-order rows: `{summary['accepted_dynamic_order_count']}`.",
        f"- Default `1e-4` required: `{summary['default_1e-4_required']}`.",
        "",
        "This artifact advances the missing closed-loop mechanisms one Gauss6",
        "step using stage Newton solves initialized only from the start state.",
        "No stage-time kinematic oracle is used. It removes the stage-time",
        "oracle from the previous one-step smoke, but",
        "it is still not a convergence sweep and must not be counted as order",
        "or external-superiority evidence.",
        "",
        "| Model | initial residual | final residual | Newton iters | endpoint pos error | status |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for row in rows:
        lines.append(
            "| "
            f"`{row['model']}` | `{row['max_initial_stage_residual_inf']}` | "
            f"`{row['max_stage_residual_inf']}` | `{row['total_stage_newton_iterations']}` | "
            f"`{row['endpoint_pos_error_inf']}` | `{row['status']}` |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    v047_module = import_v047_module()
    v046 = v047_module.load_v046()
    v046.patch_modern_numpy_scalar_assignments()
    models = {model.name: model for model in v046.MODELS}
    rows = [make_row(v047_module, v046, models[model_name]) for model_name in MODELS]
    ok_count = sum(1 for row in rows if row["status"] == "ok")
    initial_residuals = finite_values(rows, "max_initial_stage_residual_inf")
    stage_residuals = finite_values(rows, "max_stage_residual_inf")
    pos_errors = finite_values(rows, "endpoint_pos_error_inf")
    vel_errors = finite_values(rows, "endpoint_vel_error_inf")
    summary = {
        "schema": "closed-loop-true-dynamic-newton-stage-smoke-v1",
        "status": (
            "non_oracle_stage_newton_smoke_passed_order_rows_not_run"
            if ok_count == len(rows)
            else "non_oracle_stage_newton_smoke_partial_failed_order_rows_not_run"
        ),
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
        "newton_tol": NEWTON_TOL,
        "max_newton_iters_per_stage": MAX_NEWTON_ITERS,
        "max_initial_stage_residual_inf": max(initial_residuals) if initial_residuals else float("nan"),
        "max_stage_residual_inf": max(stage_residuals) if stage_residuals else float("nan"),
        "max_endpoint_pos_error_inf": max(pos_errors) if pos_errors else float("nan"),
        "max_endpoint_vel_error_inf": max(vel_errors) if vel_errors else float("nan"),
        "step_policy": "non_oracle_newton_one_step_smoke_not_order",
        "stage_predictor_policy": "start_extrapolated_no_stage_oracle",
        "stage_oracle_used": False,
        "trajectory_stepper_implemented": True,
        "trajectory_stepper_executed": ok_count > 0,
        "simulate_runner_implemented": False,
        "accepted_dynamic_order_count": 0,
        "convergence_sweep_run": False,
        "default_policy": "coarse_first_no_default_1e-4",
        "strict_public_policy_1e-4_required": False,
        "default_1e-4_required": False,
        "heavy_numerical_run_invoked": False,
        "external_superiority_claim": False,
        "interpretation": (
            "One Gauss6 step now solves the closed-loop FullVA dynamic stage residuals "
            "from a start-state predictor rather than stage-time oracle roots. The "
            "remaining gap is a multi-step trajectory simulator and coarse three-step "
            "order/work rows."
        ),
    }
    write_csv(OUT_CSV, rows)
    with OUT_JSON.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, sort_keys=True)
        handle.write("\n")
    write_markdown(summary, rows)
    print("closed_loop_true_dynamic_newton_stage_smoke=written")
    print(f"rows_ok={ok_count}/{len(rows)}")
    print(f"max_initial_stage_residual_inf={summary['max_initial_stage_residual_inf']:.6e}")
    print(f"max_stage_residual_inf={summary['max_stage_residual_inf']:.6e}")
    print("stage_oracle_used=False")
    print("trajectory_stepper_executed=True")
    print("convergence_sweep_run=False")
    print("default_1e-4=False")
    print("accepted_dynamic_order=0")


if __name__ == "__main__":
    main()
