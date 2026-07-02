#!/usr/bin/env python3
"""Build coarse true-dynamic Newton trajectory/order rows for closed-loop models."""

from __future__ import annotations

import csv
import importlib.util
import json
import math
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
STEP_SIZES = (0.1, 0.05, 0.025)
T0 = 0.0
T_END = 0.1
KINEMATIC_TOL = 1.0e-12
NEWTON_TOL = 1.0e-10
MAX_NEWTON_ITERS = 12
OUT_CSV = RESULTS / "closed_loop_true_dynamic_newton_coarse_order_rows.csv"
OUT_JSON = RESULTS / "closed_loop_true_dynamic_newton_coarse_order.json"
OUT_MD = RESULTS / "closed_loop_true_dynamic_newton_coarse_order.md"


def import_v047_module():
    module_name = "v047_cylindrical_chain_pipeline_run_v047_for_newton_coarse_order"
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
        raise ValueError("refusing to write empty coarse-order rows")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def setup_exact_system(v047_module, v046, model, h: float, t: float):
    system, _params = v046.setup_system(model, "dynamics", h, T_END, KINEMATIC_TOL)
    system.initialize()
    v047_module.project_v046_system_to_so3(system)
    v047_module.solve_v046_local_kinematic_fullva_time(system, t, KINEMATIC_TOL)
    return system


def finite(value: object) -> float | None:
    try:
        out = float(value)
    except Exception:  # noqa: BLE001
        return None
    return out if math.isfinite(out) else None


def observed_order(rows: list[dict[str, object]], key: str) -> tuple[float, list[float]]:
    pairs: list[tuple[float, float]] = []
    for row in rows:
        h = finite(row.get("h"))
        err = finite(row.get(key))
        if h is not None and err is not None and h > 0.0 and err > 0.0:
            pairs.append((h, err))
    pairs.sort(reverse=True)
    if len(pairs) < 3:
        return float("nan"), []
    logs_h = np.log([pair[0] for pair in pairs])
    logs_e = np.log([pair[1] for pair in pairs])
    fit_order = float(np.polyfit(logs_h, logs_e, 1)[0])
    pairwise = [
        float(np.log(pairs[i][1] / pairs[i + 1][1]) / np.log(pairs[i][0] / pairs[i + 1][0]))
        for i in range(len(pairs) - 1)
    ]
    return fit_order, pairwise


def simulate_model_h(v047_module, v046, model, h: float, reference: dict[str, np.ndarray]) -> dict[str, object]:
    started = time.perf_counter()
    steps = int(round((T_END - T0) / h))
    row: dict[str, object] = {
        "model": model.name,
        "method": "Gauss6/FullVA-local-closed-loop-true-dynamic-newton",
        "row_type": "coarse_true_dynamic_newton_trajectory_order_candidate",
        "h": f"{h:.16e}",
        "t0": f"{T0:.16e}",
        "t_end": f"{T_END:.16e}",
        "steps": steps,
        "status": "ok",
        "step_policy": "non_oracle_newton_multistep_coarse_order_candidate",
        "stage_predictor_policy": "start_extrapolated_no_stage_oracle",
        "stage_oracle_used": "false",
        "stage_count_per_step": 3,
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
        "runtime_sec": "nan",
        "trajectory_stepper_executed": "false",
        "simulate_runner_implemented": "true",
        "accepted_dynamic_order": "false",
        "convergence_sweep_run": "true",
        "default_policy": "coarse_first_no_default_1e-4",
        "strict_public_policy_1e-4_required": "false",
        "default_1e-4_required": "false",
        "heavy_numerical_run_invoked": "false",
        "notes": "",
    }
    try:
        if not np.isclose(T0 + steps * h, T_END):
            raise ValueError(f"h={h} does not divide T_END={T_END}")
        system = setup_exact_system(v047_module, v046, model, h, T0)
        max_initial = 0.0
        max_final = 0.0
        total_iters = 0
        line_search_failures = 0
        all_converged = True
        for step_index in range(steps):
            t_step = T0 + step_index * h
            out = dynres.gauss6_closed_loop_fullva_dynamic_step_newton_smoke(
                system,
                t_step,
                h,
                v047_module,
                tol=NEWTON_TOL,
                max_iters=MAX_NEWTON_ITERS,
            )
            max_initial = max(max_initial, float(out["max_initial_stage_residual_inf"]))
            max_final = max(max_final, float(out["max_stage_residual_inf"]))
            total_iters += int(out["total_stage_newton_iterations"])
            line_search_failures += int(out["line_search_failures"])
            all_converged = all_converged and bool(out["all_stages_converged"])

        candidate = dynres.endpoint_state_from_system(system)
        err = dynres.endpoint_state_error_inf(candidate, reference)
        phi, vel, acc = v047_module.v046_constraint_level_residuals(system, T_END)
        so3 = v046.orthogonality_error(system)
        ok = all_converged and max_final < 1.0e-8 and all(math.isfinite(err[key]) for key in err)
        row.update(
            {
                "status": "ok" if ok else "diagnostic_failed_threshold",
                "max_initial_stage_residual_inf": f"{max_initial:.16e}",
                "max_stage_residual_inf": f"{max_final:.16e}",
                "total_stage_newton_iterations": total_iters,
                "line_search_failures": line_search_failures,
                "all_stages_converged": str(all_converged).lower(),
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
                "runtime_sec": f"{time.perf_counter() - started:.16e}",
                "trajectory_stepper_executed": "true",
                "notes": (
                    "Coarse multistep true-dynamic candidate: every stage is solved "
                    "from the start-state extrapolated predictor with no stage-time "
                    "kinematic oracle. This row is local method evidence and does not "
                    "by itself claim external superiority."
                ),
            }
        )
    except Exception as exc:  # noqa: BLE001 - keep failure visible.
        row.update(
            {
                "status": f"failed:{type(exc).__name__}:{str(exc).replace(chr(10), ' ')}",
                "runtime_sec": f"{time.perf_counter() - started:.16e}",
                "notes": "coarse true-dynamic Newton trajectory failed",
            }
        )
    return row


def build_model_summary(model_name: str, rows: list[dict[str, object]]) -> dict[str, object]:
    pos_order, pos_pairwise = observed_order(rows, "endpoint_pos_error_inf")
    orientation_order, orientation_pairwise = observed_order(rows, "endpoint_orientation_error_inf")
    vel_order, vel_pairwise = observed_order(rows, "endpoint_vel_error_inf")
    omega_order, omega_pairwise = observed_order(rows, "endpoint_omega_error_inf")
    acc_order, acc_pairwise = observed_order(rows, "endpoint_acc_error_inf")
    ok_rows = [row for row in rows if row.get("status") == "ok"]
    primary_orders = [pos_order, orientation_order, vel_order, omega_order]
    min_primary_order = min(primary_orders) if all(math.isfinite(value) for value in primary_orders) else float("nan")
    accepted = len(ok_rows) == len(STEP_SIZES) and math.isfinite(min_primary_order) and min_primary_order >= 4.5
    return {
        "model": model_name,
        "row_count": len(rows),
        "ok_row_count": len(ok_rows),
        "pos_observed_order": pos_order,
        "orientation_observed_order": orientation_order,
        "vel_observed_order": vel_order,
        "omega_observed_order": omega_order,
        "acc_observed_order": acc_order,
        "pos_pairwise_orders": pos_pairwise,
        "orientation_pairwise_orders": orientation_pairwise,
        "vel_pairwise_orders": vel_pairwise,
        "omega_pairwise_orders": omega_pairwise,
        "acc_pairwise_orders": acc_pairwise,
        "min_primary_order": min_primary_order,
        "accepted_dynamic_order_candidate": accepted,
    }


def annotate_rows_with_orders(rows: list[dict[str, object]], model_summaries: dict[str, dict[str, object]]) -> None:
    for row in rows:
        summary = model_summaries[row["model"]]
        row["model_pos_observed_order"] = f"{float(summary['pos_observed_order']):.16e}"
        row["model_orientation_observed_order"] = f"{float(summary['orientation_observed_order']):.16e}"
        row["model_vel_observed_order"] = f"{float(summary['vel_observed_order']):.16e}"
        row["model_omega_observed_order"] = f"{float(summary['omega_observed_order']):.16e}"
        row["model_acc_observed_order"] = f"{float(summary['acc_observed_order']):.16e}"
        row["accepted_dynamic_order"] = str(bool(summary["accepted_dynamic_order_candidate"])).lower()


def write_markdown(summary: dict[str, object], rows: list[dict[str, object]]) -> None:
    lines = [
        "# Closed-Loop True-Dynamic Newton Coarse Order",
        "",
        f"Status: **{summary['status'].replace('_', ' ')}**",
        "",
        f"- Step sizes: `0.1|0.05|0.025`; time window: `{T_END}`.",
        f"- Rows: `{summary['ok_row_count']}/{summary['row_count']}` ok.",
        f"- Accepted dynamic-order candidates: `{summary['accepted_dynamic_order_count']}`.",
        f"- Stage oracle used: `{summary['stage_oracle_used']}`.",
        f"- Default `1e-4` required: `{summary['default_1e-4_required']}`.",
        f"- External superiority claim: `{summary['external_superiority_claim']}`.",
        "",
        "These rows use the non-oracle Newton stage solver on a short coarse",
        "trajectory window. They are local true-dynamic method rows; they still",
        "need public-baseline work/precision comparison before any external",
        "superiority claim is allowed.",
        "The acceptance gate uses position, orientation, linear velocity, and",
        "angular velocity orders; endpoint acceleration is reported only as a",
        "diagnostic because this runner does not yet construct a collocated",
        "endpoint acceleration state.",
        "",
        "| Model | h | pos err | orient err | vel err | pos order | orient order | vel order | omega order | Newton iters | status |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in rows:
        lines.append(
            "| "
            f"`{row['model']}` | `{row['h']}` | `{row['endpoint_pos_error_inf']}` | "
            f"`{row['endpoint_orientation_error_inf']}` | `{row['endpoint_vel_error_inf']}` | "
            f"`{row['model_pos_observed_order']}` | `{row['model_orientation_observed_order']}` | "
            f"`{row['model_vel_observed_order']}` | `{row['model_omega_observed_order']}` | "
            f"`{row['total_stage_newton_iterations']}` | "
            f"`{row['status']}` |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    v047_module = import_v047_module()
    v046 = v047_module.load_v046()
    v046.patch_modern_numpy_scalar_assignments()
    models = {model.name: model for model in v046.MODELS}
    rows: list[dict[str, object]] = []
    for model_name in MODELS:
        model = models[model_name]
        reference_system = setup_exact_system(v047_module, v046, model, min(STEP_SIZES), T_END)
        reference = dynres.endpoint_state_from_system(reference_system)
        for h in STEP_SIZES:
            rows.append(simulate_model_h(v047_module, v046, model, h, reference))

    model_summaries = {
        model_name: build_model_summary(model_name, [row for row in rows if row["model"] == model_name])
        for model_name in MODELS
    }
    annotate_rows_with_orders(rows, model_summaries)
    ok_count = sum(1 for row in rows if row["status"] == "ok")
    accepted_count = sum(1 for item in model_summaries.values() if item["accepted_dynamic_order_candidate"])
    summary = {
        "schema": "closed-loop-true-dynamic-newton-coarse-order-v1",
        "status": (
            "coarse_true_dynamic_order_candidates_available_not_external_superiority"
            if accepted_count == len(MODELS)
            else "coarse_true_dynamic_order_candidates_incomplete_not_external_superiority"
        ),
        "method": "Gauss6/FullVA",
        "models": list(MODELS),
        "row_count": len(rows),
        "ok_row_count": ok_count,
        "step_sizes": list(STEP_SIZES),
        "t0": T0,
        "t_end": T_END,
        "stage_count_per_step": 3,
        "stage_unknown_dim": 72,
        "stage_residual_dim": 72,
        "stage_predictor_policy": "start_extrapolated_no_stage_oracle",
        "stage_oracle_used": False,
        "model_summaries": model_summaries,
        "accepted_dynamic_order_count": accepted_count,
        "convergence_sweep_run": True,
        "simulate_runner_implemented": True,
        "default_policy": "coarse_first_no_default_1e-4",
        "strict_public_policy_1e-4_required": False,
        "default_1e-4_required": False,
        "heavy_numerical_run_invoked": False,
        "external_superiority_claim": False,
        "interpretation": (
            "This is the first non-oracle local true-dynamic coarse convergence sweep "
            "for the two missing closed-loop mechanisms. It can support local order "
            "discussion if the orders pass the gate, but public baseline comparison "
            "and work/precision rows remain necessary before external superiority."
        ),
    }
    write_csv(OUT_CSV, rows)
    with OUT_JSON.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, sort_keys=True)
        handle.write("\n")
    write_markdown(summary, rows)
    print("closed_loop_true_dynamic_newton_coarse_order=written")
    print(f"rows_ok={ok_count}/{len(rows)}")
    for model_name, model_summary in model_summaries.items():
        print(
            f"{model_name}_orders="
            f"{float(model_summary['pos_observed_order']):.3f}/"
            f"{float(model_summary['orientation_observed_order']):.3f}/"
            f"{float(model_summary['vel_observed_order']):.3f}/"
            f"{float(model_summary['omega_observed_order']):.3f}/"
            f"{float(model_summary['acc_observed_order']):.3f}"
        )
    print(f"accepted_dynamic_order={accepted_count}")
    print("stage_oracle_used=False")
    print("convergence_sweep_run=True")
    print("default_1e-4=False")
    print("external_superiority_claim=False")


if __name__ == "__main__":
    main()
