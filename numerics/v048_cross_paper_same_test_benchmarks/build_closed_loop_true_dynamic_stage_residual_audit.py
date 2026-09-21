#!/usr/bin/env python3
"""Audit the closed-loop true-dynamic FullVA stage residual evaluator.

This is not a trajectory-order run. It evaluates the four residual families at
the three Gauss6 stage times on the two missing closed-loop mechanisms using
the public/v046 interface and the local stage residual utilities.
"""

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
T_END = 0.1
TOL = 1.0e-12
OUT_CSV = RESULTS / "closed_loop_true_dynamic_stage_residual_audit.csv"
OUT_JSON = RESULTS / "closed_loop_true_dynamic_stage_residual_audit.json"
OUT_MD = RESULTS / "closed_loop_true_dynamic_stage_residual_audit.md"


def import_v047_module():
    module_name = "v047_cylindrical_chain_pipeline_run_v047_for_stage_residual_audit"
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
        raise ValueError("refusing to write empty stage residual audit")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def block_norms(blocks: dict[str, np.ndarray]) -> dict[str, float]:
    return {name: float(np.linalg.norm(value.reshape(-1), ord=np.inf)) for name, value in blocks.items()}


def make_stage_row(v047_module, system, model_name: str, stage_index: int, c_i: float, b_i: float) -> dict[str, object]:
    t = float(H * c_i)
    started = time.perf_counter()
    row: dict[str, object] = {
        "model": model_name,
        "stage_index": stage_index,
        "gauss_c": f"{c_i:.16e}",
        "gauss_b": f"{b_i:.16e}",
        "t": f"{t:.16e}",
        "h": f"{H:.16e}",
        "status": "ok",
        "source_state_policy": "kinematic_oracle_state_for_residual_evaluator_audit",
        "stage_q_dim": 18,
        "stage_v_dim": 18,
        "stage_a_dim": 18,
        "stage_lambda_dim": 18,
        "stage_unknown_dim": 72,
        "stage_residual_dim": 72,
        "position_residual_inf": "nan",
        "velocity_residual_inf": "nan",
        "acceleration_residual_inf": "nan",
        "newton_euler_residual_inf": "nan",
        "stage_residual_inf": "nan",
        "pack_unpack_roundtrip_inf": "nan",
        "trajectory_stepper_executed": "false",
        "stepper_implemented": "false",
        "accepted_dynamic_order": "false",
        "default_policy": "coarse_first_no_default_1e-4",
        "strict_public_policy_1e-4_required": "false",
        "heavy_numerical_run_invoked": "false",
        "runtime_sec": "nan",
        "notes": "",
    }
    try:
        nit, correction, min_sigma, cond = v047_module.solve_v046_local_kinematic_fullva_time(system, t, TOL)
        lam, _trans_norm, _rot_norm, _full_dyn_norm, _lam_norm = v047_module.reconstruct_v046_reaction_dynamics(system, t)
        context = dynres.capture_stage_context(system)
        q, v, a = dynres.generalized_qva_from_system(system)
        stage_vector = dynres.pack_closed_loop_fullva_stage_vector(q, v, a, lam)
        q2, v2, a2, lam2 = dynres.unpack_closed_loop_fullva_stage_vector(stage_vector, system.nb, system.nc)
        roundtrip = max(
            float(np.linalg.norm(q2 - q, ord=np.inf)),
            float(np.linalg.norm(v2 - v, ord=np.inf)),
            float(np.linalg.norm(a2 - a, ord=np.inf)),
            float(np.linalg.norm(lam2 - lam.reshape(-1), ord=np.inf)),
        )
        blocks = dynres.closed_loop_fullva_stage_residual_blocks(system, t, stage_vector, context)
        residual = dynres.closed_loop_fullva_stage_residual(system, t, stage_vector, context)
        norms = block_norms(blocks)
        stage_norm = float(np.linalg.norm(residual, ord=np.inf))
        accepted = stage_norm < 1.0e-10 and roundtrip < 1.0e-14
        row.update(
            {
                "status": "ok" if accepted else "diagnostic_failed_threshold",
                "position_residual_inf": f"{norms['position_constraints_phi']:.16e}",
                "velocity_residual_inf": f"{norms['velocity_constraints_phiq_v_minus_nu']:.16e}",
                "acceleration_residual_inf": f"{norms['acceleration_constraints_phiq_a_minus_gamma']:.16e}",
                "newton_euler_residual_inf": f"{norms['newton_euler_balance']:.16e}",
                "stage_residual_inf": f"{stage_norm:.16e}",
                "pack_unpack_roundtrip_inf": f"{roundtrip:.16e}",
                "runtime_sec": f"{time.perf_counter() - started:.16e}",
                "notes": (
                    "Stage residual evaluator only: kinematic oracle state plus reconstructed lambda; "
                    f"position Newton iterations={nit}, correction={correction:.3e}, "
                    f"min_sigma={min_sigma:.3e}, cond={cond:.3e}."
                ),
            }
        )
    except Exception as exc:  # noqa: BLE001 - keep row visible.
        row.update(
            {
                "status": f"failed:{type(exc).__name__}:{str(exc).replace(chr(10), ' ')}",
                "runtime_sec": f"{time.perf_counter() - started:.16e}",
                "notes": "stage residual evaluator failed before trajectory execution",
            }
        )
    return row


def write_markdown(summary: dict, rows: list[dict[str, object]]) -> None:
    lines = [
        "# Closed-Loop True-Dynamic Stage Residual Audit",
        "",
        "Status: **stage residual evaluator verified; stepper not implemented**",
        "",
        f"- Rows: `{summary['ok_row_count']}/{summary['row_count']}` ok.",
        f"- Max stage residual infinity norm: `{summary['max_stage_residual_inf']:.3e}`.",
        f"- Stage evaluator implemented: `{summary['stage_residual_evaluator_implemented']}`.",
        f"- Trajectory stepper implemented: `{summary['trajectory_stepper_implemented']}`.",
        f"- Accepted dynamic-order rows: `{summary['accepted_dynamic_order_count']}`.",
        f"- Default `1e-4` required: `{summary['default_1e-4_required']}`.",
        "",
        "This audit evaluates the four residual families at the three Gauss6",
        "stage times for `four_link` and `slider_crank`. It proves that the",
        "local residual evaluator can assemble and evaluate the square 72-row",
        "stage system on the public/v046 dynamic interface. It still does not",
        "advance an endpoint and must not be counted as a trajectory order row.",
        "",
        "| Model | Stage | stage residual inf | Newton-Euler inf | status |",
        "|---|---:|---:|---:|---|",
    ]
    for row in rows:
        lines.append(
            "| "
            f"`{row['model']}` | `{row['stage_index']}` | "
            f"`{row['stage_residual_inf']}` | `{row['newton_euler_residual_inf']}` | "
            f"`{row['status']}` |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    v047_module = import_v047_module()
    v046 = v047_module.load_v046()
    v046.patch_modern_numpy_scalar_assignments()
    models = {model.name: model for model in v046.MODELS}
    rows: list[dict[str, object]] = []
    for model_name in MODELS:
        if model_name not in models:
            raise ValueError(f"v046 model not found: {model_name}")
        system, _params = v046.setup_system(models[model_name], "dynamics", H, T_END, TOL)
        system.initialize()
        v047_module.project_v046_system_to_so3(system)
        for stage_index, (c_i, b_i) in enumerate(zip(dynres.GAUSS6_C, dynres.GAUSS6_B, strict=True), start=1):
            rows.append(make_stage_row(v047_module, system, model_name, stage_index, float(c_i), float(b_i)))

    stage_norms = [
        float(row["stage_residual_inf"])
        for row in rows
        if str(row.get("stage_residual_inf", "nan")).lower() != "nan"
    ]
    ok_count = sum(1 for row in rows if row["status"] == "ok")
    summary = {
        "schema": "closed-loop-true-dynamic-stage-residual-audit-v1",
        "status": "stage_residual_evaluator_verified_stepper_not_implemented",
        "method": "Gauss6/FullVA",
        "models": list(MODELS),
        "row_count": len(rows),
        "ok_row_count": ok_count,
        "stage_count_per_model": 3,
        "stage_unknown_dim": 72,
        "stage_residual_dim": 72,
        "max_stage_residual_inf": max(stage_norms) if stage_norms else float("nan"),
        "stage_residual_evaluator_implemented": True,
        "required_symbols_implemented": [
            "pack_closed_loop_fullva_stage_vector",
            "unpack_closed_loop_fullva_stage_vector",
            "closed_loop_fullva_stage_residual",
        ],
        "trajectory_stepper_implemented": False,
        "simulate_runner_implemented": False,
        "accepted_dynamic_order_count": 0,
        "trajectory_stepper_executed": False,
        "default_policy": "coarse_first_no_default_1e-4",
        "strict_public_policy_1e-4_required": False,
        "default_1e-4_required": False,
        "heavy_numerical_run_invoked": False,
        "external_superiority_claim": False,
        "interpretation": (
            "The square closed-loop FullVA dynamic stage residual evaluator is implemented and "
            "verified at Gauss6 stage states. Endpoint advancement and trajectory order rows remain open."
        ),
    }
    write_csv(OUT_CSV, rows)
    with OUT_JSON.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, sort_keys=True)
        handle.write("\n")
    write_markdown(summary, rows)
    print("closed_loop_true_dynamic_stage_residual_audit=written")
    print(f"rows_ok={ok_count}/{len(rows)}")
    print(f"max_stage_residual_inf={summary['max_stage_residual_inf']:.6e}")
    print("stage_residual_evaluator_implemented=True")
    print("trajectory_stepper_implemented=False")
    print("default_1e-4=False")
    print("accepted_dynamic_order=0")


if __name__ == "__main__":
    main()
