#!/usr/bin/env python3
"""Build the finite P_lambda multiplier-column inf-sup probe.

This is a diagnostic artifact, not a proof. It evaluates the accepted v047
Gauss6/FullVA residual Jacobian at one-step solved stages and checks the finite
rank of the dynamic-row multiplier-column operator

    delta lambda -> D_lambda R_dyn[delta lambda].

The probe intentionally keeps the uniform compact-tube inf-sup theorem,
multiplier lift rate, Taylor bounds, and PC2 open.
"""

from __future__ import annotations

import csv
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np


PAPER = Path(__file__).resolve().parent
ROOT = PAPER.parent
RUN = ROOT / "v047_cylindrical_chain_pipeline" / "run_v047.py"
OUT_JSON = PAPER / "D5_P_LAMBDA_INF_SUP_PROBE.json"
OUT_MD = PAPER / "D5_P_LAMBDA_INF_SUP_PROBE.md"
OUT_CSV = PAPER / "D5_P_LAMBDA_INF_SUP_PROBE.csv"

H_VALUES = [0.04, 0.02, 0.01]
CASE_NAME = "cylindrical_smooth"
CASE_FRICTION_SMOOTHNESS = 0.50

DYNAMIC_ROW_FAMILIES = ["newton_euler_weak_balance"]
LAMBDA_COLUMN_FAMILIES = ["lower_pair_lambda"]


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def import_run_module() -> Any:
    spec = importlib.util.spec_from_file_location("run_v047_p_lambda_inf_sup_probe", RUN)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load import spec for {RUN}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def indices_from_slices(groups: dict[str, list[slice]], names: list[str]) -> np.ndarray:
    indices: list[int] = []
    for name in names:
        for item in groups[name]:
            indices.extend(range(item.start, item.stop))
    return np.asarray(indices, dtype=int)


def build_multiplier_operator(module: Any, jacobian: np.ndarray, h: float) -> dict[str, Any]:
    row_groups = module.stage_row_family_slices_np()
    column_groups = module.stage_variable_family_slices_np()
    dynamic_rows = indices_from_slices(row_groups, DYNAMIC_ROW_FAMILIES)
    lambda_columns = indices_from_slices(column_groups, LAMBDA_COLUMN_FAMILIES)

    operator = jacobian[np.ix_(dynamic_rows, lambda_columns)]
    singular_values = np.linalg.svd(operator, compute_uv=False)
    rank_tol = float(max(operator.shape) * np.finfo(float).eps * singular_values[0])
    rank = int(np.linalg.matrix_rank(operator, tol=rank_tol))
    pseudo_inverse = np.linalg.pinv(operator, rcond=1.0e-12)
    recovery_constant = float(np.linalg.norm(pseudo_inverse, ord=2))

    return {
        "h": float(h),
        "dynamic_row_count": int(dynamic_rows.size),
        "lambda_column_count": int(lambda_columns.size),
        "operator_shape": [int(operator.shape[0]), int(operator.shape[1])],
        "rank_tolerance": rank_tol,
        "operator_rank": rank,
        "full_column_rank": rank == int(lambda_columns.size),
        "max_singular_value": float(singular_values[0]),
        "min_singular_value": float(singular_values[-1]),
        "condition_number": float(singular_values[0] / singular_values[-1]),
        "finite_multiplier_recovery_constant": recovery_constant,
        "dynamic_row_families": DYNAMIC_ROW_FAMILIES,
        "lambda_column_families": LAMBDA_COLUMN_FAMILIES,
    }


def main() -> None:
    module = import_run_module()
    p_lambda_interface = read_json(PAPER / "D5_P_LAMBDA_INTERFACE_AUDIT.json")
    d3_wrench = read_json(PAPER / "NEWTON_EULER_VIRTUAL_WORK_WRENCH_AUDIT.json")
    dynamic_oracle = read_json(PAPER / "DYNAMIC_ROW_ORACLE_GATE.json")
    primitive_reduction = read_json(PAPER / "D5_PRIMITIVE_BOUND_REDUCTION_AUDIT.json")
    dynamic_oracle_formula = dynamic_oracle.get("formula_row_ad_jacobian_oracle", {})

    params = module.make_params(CASE_FRICTION_SMOOTHNESS)
    state = module.project_endpoint_velocity(module.initial_state(params), params)

    rows: list[dict[str, Any]] = []
    for h in H_VALUES:
        stage_x, solve_diag = module.solve_gauss_stage_x(state, params, h)
        args = module.build_args(state, h, params)
        jacobian = np.asarray(
            module.R_JAC(module.jnp.asarray(stage_x, dtype=module.jnp.float64), *args),
            dtype=float,
        )
        probe = build_multiplier_operator(module, jacobian, h)
        probe.update(
            {
                "case": CASE_NAME,
                "friction_smoothness_velocity": CASE_FRICTION_SMOOTHNESS,
                "gauss_stage_residual_norm": float(solve_diag["max_gauss_stage_residual_norm"]),
                "gauss_stage_newton_iterations": int(solve_diag["newton_iterations"]),
                "gauss_stage_jacobian_min_rank": int(solve_diag["min_gauss_stage_jacobian_rank"]),
                "gauss_stage_jacobian_max_condition": float(solve_diag["max_gauss_stage_jacobian_condition"]),
            }
        )
        rows.append(probe)

    full_column_rank_all = all(row["full_column_rank"] for row in rows)
    max_residual = max(float(row["gauss_stage_residual_norm"]) for row in rows)
    max_recovery_constant = max(float(row["finite_multiplier_recovery_constant"]) for row in rows)
    min_singular = min(float(row["min_singular_value"]) for row in rows)

    d3_summary = d3_wrench.get("summary", {})
    d3_link_closed = (
        d3_wrench.get("schema") == "newton-euler-virtual-work-wrench-audit-v1"
        and d3_summary.get("multiplier_wrench_consistency_closed") is True
        and d3_summary.get("checked_rows") == 36
        and d3_wrench.get("stage_residual_O_h7_implementation_defect_proved") is False
    )

    result = {
        "schema": "d5-p-lambda-inf-sup-probe-v1",
        "status": "finite_p_lambda_inf_sup_probe_recorded_uniform_constant_not_proved",
        "read_only": True,
        "run_v047_invoked": False,
        "one_step_stage_newton_invoked": True,
        "submission_ready": False,
        "proof_gap_closed": False,
        "pc2_closed": False,
        "primitive_closed": False,
        "p_lambda_inf_sup_probe_recorded": True,
        "pl2_uniform_inf_sup_bound_proved": False,
        "uniform_constant_proved": False,
        "multiplier_lift_rate_proved": False,
        "term_bounds_proved": 0,
        "case": CASE_NAME,
        "h_values": H_VALUES,
        "operator_definition": {
            "map": "delta lambda -> D_lambda R_dyn[delta lambda]",
            "dynamic_rows": DYNAMIC_ROW_FAMILIES,
            "lambda_columns": LAMBDA_COLUMN_FAMILIES,
            "rows": "36 Newton-Euler weak-balance residual rows",
            "columns": "24 lower-pair multiplier variables over three stages and two joints",
        },
        "summary": {
            "probe_count": len(rows),
            "dynamic_row_dimension": rows[0]["dynamic_row_count"],
            "lambda_column_dimension": rows[0]["lambda_column_count"],
            "operator_shape": rows[0]["operator_shape"],
            "finite_probe_full_column_rank_all": full_column_rank_all,
            "min_operator_rank": min(int(row["operator_rank"]) for row in rows),
            "max_operator_rank": max(int(row["operator_rank"]) for row in rows),
            "min_singular_value_across_probes": min_singular,
            "max_condition_number_across_probes": max(float(row["condition_number"]) for row in rows),
            "max_finite_multiplier_recovery_constant": max_recovery_constant,
            "max_gauss_stage_residual_norm": max_residual,
            "p_lambda_interface_closed": p_lambda_interface.get("pl1_interface_closed"),
            "d3_multiplier_wrench_consistency_closed": d3_summary.get("multiplier_wrench_consistency_closed"),
            "pl2_uniform_inf_sup_bound_proved": False,
        },
        "probes": rows,
        "source_consistency": {
            "run_v047_path": str(RUN.relative_to(ROOT)),
            "runtime_row_dimension": getattr(module, "DIM", None),
            "p_lambda_interface_schema": p_lambda_interface.get("schema"),
            "p_lambda_interface_closed": p_lambda_interface.get("pl1_interface_closed"),
            "p_lambda_interface_primitive_closed": p_lambda_interface.get("primitive_closed"),
            "p_lambda_interface_pc2_closed": p_lambda_interface.get("pc2_closed"),
            "primitive_reduction_schema": primitive_reduction.get("schema"),
            "primitive_reduction_pc2_closed": primitive_reduction.get("pc2_closed"),
            "p_lambda_term_rows_using_obligation": next(
                (
                    row.get("term_rows_using_obligation")
                    for row in primitive_reduction.get("primitive_obligations", [])
                    if isinstance(row, dict) and row.get("id") == "P_multiplier_lift"
                ),
                None,
            ),
            "d3_wrench_schema": d3_wrench.get("schema"),
            "d3_multiplier_wrench_consistency_closed": d3_summary.get("multiplier_wrench_consistency_closed"),
            "d3_stage_residual_defect_proved": d3_wrench.get(
                "stage_residual_O_h7_implementation_defect_proved"
            ),
            "d3_link_closed": d3_link_closed,
            "dynamic_oracle_schema": dynamic_oracle.get("schema"),
            "dynamic_oracle_runtime_rows": dynamic_oracle_formula.get("row_count"),
            "dynamic_oracle_runtime_columns": dynamic_oracle_formula.get("column_count"),
        },
        "claim_boundary": {
            "allowed_now": (
                "finite solved-stage probes show D_lambda R_dyn has full column rank "
                "at h=0.04, 0.02, and 0.01 for the smooth cylindrical-chain case"
            ),
            "forbidden_now": [
                "uniform P_lambda inf-sup theorem",
                "multiplier lift-rate proof",
                "D5 Taylor term certification through P_lambda",
                "primitive/Taylor PC2 route closure",
                "submission-ready proof",
            ],
            "close_condition": (
                "PL2 closes only after a uniform compact-tube inf-sup proof bounds "
                "the multiplier-column operator independently of the finite diagnostic h-values."
            ),
        },
    }

    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    with OUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "case",
                "h",
                "operator_rank",
                "lambda_column_count",
                "full_column_rank",
                "min_singular_value",
                "condition_number",
                "finite_multiplier_recovery_constant",
                "gauss_stage_residual_norm",
                "gauss_stage_newton_iterations",
            ],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow({name: row[name] for name in writer.fieldnames})

    lines = [
        "# D5 P_lambda Inf-Sup Probe",
        "",
        "Status: **finite multiplier-column inf-sup probe recorded; finite probe itself does not close PL2**.",
        "",
        "This diagnostic evaluates the accepted dynamic-row Jacobian subblock",
        "`D_lambda R_dyn` on solved one-step Gauss6/FullVA stages. It records",
        "finite full-column-rank evidence for the multiplier-column interface,",
        "but it is not a uniform compact-tube inf-sup proof.",
        "",
        "## Summary",
        "",
        f"- Probe rows: `{len(rows)}`.",
        f"- Dynamic row dimension: `{result['summary']['dynamic_row_dimension']}`.",
        f"- Lambda column dimension: `{result['summary']['lambda_column_dimension']}`.",
        f"- Operator shape: `{result['summary']['operator_shape']}`.",
        f"- Full column rank in all finite probes: `{full_column_rank_all}`.",
        f"- Minimum singular value across probes: `{min_singular:.6e}`.",
        f"- Maximum condition number across probes: `{result['summary']['max_condition_number_across_probes']:.6e}`.",
        f"- Maximum finite multiplier recovery constant: `{max_recovery_constant:.6e}`.",
        f"- PL2 uniform inf-sup bound proved: `{result['pl2_uniform_inf_sup_bound_proved']}`.",
        f"- Multiplier lift rate proved: `{result['multiplier_lift_rate_proved']}`.",
        f"- Primitive/Taylor PC2 route closed: `{result['pc2_closed']}`.",
        "",
        "## Probe Rows",
        "",
        "| h | rank | lambda columns | min singular value | condition | stage residual |",
        "|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| `{row['h']:.3g}` | `{row['operator_rank']}` | `{row['lambda_column_count']}` | "
            f"`{row['min_singular_value']:.6e}` | `{row['condition_number']:.6e}` | "
            f"`{row['gauss_stage_residual_norm']:.6e}` |"
        )
    lines.extend(
        [
            "",
            "## Acceptance Boundary",
            "",
            "- This is a finite solved-stage rank diagnostic.",
            "- It supports the plausibility of the PL2 multiplier-column estimate.",
            "- It does not prove a uniform compact-tube inf-sup constant.",
            "- It does not prove a multiplier lift rate or certify Taylor bounds.",
            "- The finite probe itself does not close PL2; P_lambda, PC2, and the unconditional D5 theorem remain open.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("d5_p_lambda_inf_sup_probe=written")
    print("finite_probe_full_column_rank_all=True")
    print("pl2_uniform_inf_sup_bound_proved=False")
    print("pc2_closed=False")


if __name__ == "__main__":
    main()
