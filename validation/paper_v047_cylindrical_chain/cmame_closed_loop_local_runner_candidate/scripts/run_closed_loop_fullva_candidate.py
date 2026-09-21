#!/usr/bin/env python3
"""Run the B6 closed-loop local Gauss6/FullVA candidate rows."""

from __future__ import annotations

import csv
import importlib
import json
import math
import sys
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
VENDOR = ROOT / "vendor"
RESULTS = ROOT / "results"
for path in (SRC, VENDOR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import closed_loop_fullva_dynamic_residual as dynres
import local_closed_loop_helpers as helpers


MODELS = ("four_link", "slider_crank")
STEP_SIZES = (0.1, 0.05, 0.025)
T0 = 0.0
T_END = 0.1
KINEMATIC_TOL = 1.0e-12
NEWTON_TOL = 1.0e-10
MAX_NEWTON_ITERS = 12
OUT_CSV = RESULTS / "closed_loop_local_rows.csv"
OUT_JSON = RESULTS / "closed_loop_local_summary.json"
OUT_MD = RESULTS / "closed_loop_local_summary.md"


@dataclass(frozen=True)
class ModelSpec:
    name: str
    module: str
    setup_name: str


MODEL_SPECS = {
    "four_link": ModelSpec("four_link", "SimEngineMBD.example_models.four_link", "setup_four_link"),
    "slider_crank": ModelSpec("slider_crank", "SimEngineMBD.example_models.slider_crank", "setup_slider_crank"),
}


class LocalV047Shim:
    reconstruct_v046_reaction_dynamics = staticmethod(helpers.reconstruct_v046_reaction_dynamics)


def scalarize(value: object) -> float:
    arr = np.asarray(value)
    if arr.size != 1:
        raise ValueError(f"expected scalar-like constraint value, got shape {arr.shape}")
    return float(arr.reshape(-1)[0])


def patch_modern_numpy_scalar_assignments() -> None:
    module = importlib.import_module("SimEngineMBD.rA.gcons_ra")
    cls = module.ConGroup

    def get_phi(self, t):
        store = getattr(self, "Φ")
        for i, con in enumerate(self.cons):
            store[i, 0] = scalarize(con.get_phi(t))
        return store

    def get_gamma(self, t):
        store = getattr(self, "γ")
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


def setup_system(model_name: str, mode: str, h: float, t_end: float, tol: float):
    spec = MODEL_SPECS[model_name]
    setup_fn = getattr(importlib.import_module(spec.module), spec.setup_name)
    args = [
        "--form",
        "rA",
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


def setup_exact_system(model_name: str, h: float, t: float):
    system, _params = setup_system(model_name, "dynamics", h, T_END, KINEMATIC_TOL)
    system.initialize()
    helpers.project_v046_system_to_so3(system)
    helpers.solve_v046_local_kinematic_fullva_time(system, t, KINEMATIC_TOL)
    return system


def finite(value: object) -> float | None:
    try:
        out = float(value)
    except Exception:
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


def simulate_model_h(model_name: str, h: float, reference: dict[str, np.ndarray]) -> dict[str, object]:
    started = time.perf_counter()
    steps = int(round((T_END - T0) / h))
    row: dict[str, object] = {
        "model": model_name,
        "method": "Gauss6/FullVA-local-closed-loop-true-dynamic-newton",
        "row_type": "self_contained_closed_loop_candidate",
        "h": f"{h:.16e}",
        "t0": f"{T0:.16e}",
        "t_end": f"{T_END:.16e}",
        "steps": steps,
        "status": "ok",
        "stage_oracle_used": "false",
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
        "source_policy_external_superiority_allowed": "false",
        "submission_ready": "false",
    }
    try:
        if not np.isclose(T0 + steps * h, T_END):
            raise ValueError(f"h={h} does not divide T_END={T_END}")
        system = setup_exact_system(model_name, h, T0)
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
                LocalV047Shim,
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
        phi, vel, acc = helpers.v046_constraint_level_residuals(system, T_END)
        so3 = helpers.orthogonality_error(system)
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
            }
        )
    except Exception as exc:
        row.update(
            {
                "status": f"failed:{type(exc).__name__}:{str(exc).replace(chr(10), ' ')}",
                "runtime_sec": f"{time.perf_counter() - started:.16e}",
            }
        )
    return row


def build_model_summary(model_name: str, rows: list[dict[str, object]]) -> dict[str, object]:
    pos_order, pos_pairwise = observed_order(rows, "endpoint_pos_error_inf")
    orientation_order, orientation_pairwise = observed_order(rows, "endpoint_orientation_error_inf")
    vel_order, vel_pairwise = observed_order(rows, "endpoint_vel_error_inf")
    omega_order, omega_pairwise = observed_order(rows, "endpoint_omega_error_inf")
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
        "pos_pairwise_orders": pos_pairwise,
        "orientation_pairwise_orders": orientation_pairwise,
        "vel_pairwise_orders": vel_pairwise,
        "omega_pairwise_orders": omega_pairwise,
        "min_primary_order": min_primary_order,
        "accepted_dynamic_order_candidate": accepted,
    }


def annotate_rows_with_orders(rows: list[dict[str, object]], summaries: dict[str, dict[str, object]]) -> None:
    for row in rows:
        summary = summaries[row["model"]]
        row["model_pos_observed_order"] = f"{float(summary['pos_observed_order']):.16e}"
        row["model_orientation_observed_order"] = f"{float(summary['orientation_observed_order']):.16e}"
        row["model_vel_observed_order"] = f"{float(summary['vel_observed_order']):.16e}"
        row["model_omega_observed_order"] = f"{float(summary['omega_observed_order']):.16e}"
        row["accepted_dynamic_order"] = str(bool(summary["accepted_dynamic_order_candidate"])).lower()


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError("refusing to write empty closed-loop rows")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    RESULTS.mkdir(parents=True, exist_ok=True)
    patch_modern_numpy_scalar_assignments()
    rows: list[dict[str, object]] = []
    for model_name in MODELS:
        reference_system = setup_exact_system(model_name, min(STEP_SIZES), T_END)
        reference = dynres.endpoint_state_from_system(reference_system)
        for h in STEP_SIZES:
            rows.append(simulate_model_h(model_name, h, reference))

    summaries = {
        model_name: build_model_summary(model_name, [row for row in rows if row["model"] == model_name])
        for model_name in MODELS
    }
    annotate_rows_with_orders(rows, summaries)
    ok_count = sum(1 for row in rows if row.get("status") == "ok")
    accepted_count = sum(1 for item in summaries.values() if item.get("accepted_dynamic_order_candidate") is True)
    summary = {
        "schema": "cmame-closed-loop-local-runner-candidate-summary-v1",
        "status": (
            "closed_loop_self_contained_candidate_rows_passed_not_source_policy"
            if ok_count == len(rows) and accepted_count == len(MODELS)
            else "closed_loop_self_contained_candidate_rows_incomplete"
        ),
        "self_contained_simulation_runner": True,
        "imports_v046_v047_v048": False,
        "submission_ready": False,
        "source_policy_external_superiority_allowed": False,
        "models": list(MODELS),
        "step_sizes": list(STEP_SIZES),
        "row_count": len(rows),
        "ok_row_count": ok_count,
        "accepted_dynamic_order_count": accepted_count,
        "model_summaries": summaries,
        "run_v047_invoked": False,
        "run_v048_invoked": False,
        "heavy_numerical_run_invoked": False,
    }
    write_csv(OUT_CSV, rows)
    OUT_JSON.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text(
        "\n".join(
            [
                "# Closed-Loop Local Runner Candidate",
                "",
                f"Status: **{summary['status']}**.",
                f"Self-contained simulation runner: `{summary['self_contained_simulation_runner']}`.",
                f"Rows ok: `{ok_count}/{len(rows)}`.",
                f"Accepted dynamic-order candidates: `{accepted_count}`.",
                f"Source-policy external superiority allowed: `{summary['source_policy_external_superiority_allowed']}`.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    print("cmame_closed_loop_local_runner_candidate=PASS" if summary["status"].endswith("not_source_policy") else "cmame_closed_loop_local_runner_candidate=FAIL")
    print(f"rows_ok={ok_count}/{len(rows)}")
    for model_name, model_summary in summaries.items():
        print(
            f"{model_name}_orders="
            f"{float(model_summary['pos_observed_order']):.6f}/"
            f"{float(model_summary['orientation_observed_order']):.6f}/"
            f"{float(model_summary['vel_observed_order']):.6f}/"
            f"{float(model_summary['omega_observed_order']):.6f}"
        )
    print("self_contained_simulation_runner=True")
    print("source_policy_external_superiority_allowed=False")
    return 0 if summary["status"].endswith("not_source_policy") else 1


if __name__ == "__main__":
    sys.exit(main())
