#!/usr/bin/env python3
"""Build the finite PS2 weighted linearization probe for P_state.

This is a diagnostic artifact, not a proof.  It evaluates the accepted v047
Gauss6/FullVA residual Jacobian at one-step solved stages and checks the finite
rank of the weighted PS2 operator

    (delta S, delta A) -> (D N_h^nd[delta S, delta A], h delta A).

The probe intentionally keeps the uniform inverse/inf-sup theorem open.
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
OUT_JSON = PAPER / "D5_P_STATE_PS2_LINEARIZATION_PROBE.json"
OUT_MD = PAPER / "D5_P_STATE_PS2_LINEARIZATION_PROBE.md"
OUT_CSV = PAPER / "D5_P_STATE_PS2_LINEARIZATION_PROBE.csv"

H_VALUES = [0.04, 0.02, 0.01]
CASE_NAME = "cylindrical_smooth"
CASE_FRICTION_SMOOTHNESS = 0.50

NON_DYNAMIC_ROW_FAMILIES = [
    "translational_position_weak_defect",
    "rotational_lie_position_weak_defect",
    "translational_velocity_weak_defect",
    "angular_velocity_weak_defect",
    "lower_pair_index3_weak_constraints",
]
STATE_COLUMN_FAMILIES = [
    "translation_position_r",
    "lie_position_u",
    "translation_velocity_v",
    "angular_velocity_w",
]
ACCELERATION_COLUMN_FAMILIES = [
    "translation_acceleration_a",
    "angular_acceleration_alpha",
]


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def import_run_module() -> Any:
    spec = importlib.util.spec_from_file_location("run_v047_ps2_linearization_probe", RUN)
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


def build_weighted_operator(module: Any, jacobian: np.ndarray, h: float) -> dict[str, Any]:
    row_groups = module.stage_row_family_slices_np()
    column_groups = module.stage_variable_family_slices_np()
    non_dynamic_rows = indices_from_slices(row_groups, NON_DYNAMIC_ROW_FAMILIES)
    state_columns = indices_from_slices(column_groups, STATE_COLUMN_FAMILIES)
    acceleration_columns = indices_from_slices(column_groups, ACCELERATION_COLUMN_FAMILIES)
    domain_columns = np.concatenate([state_columns, acceleration_columns])

    state_dim = int(state_columns.size)
    acceleration_dim = int(acceleration_columns.size)
    row_dim = int(non_dynamic_rows.size)
    domain_dim = int(domain_columns.size)

    non_dynamic_jacobian = jacobian[np.ix_(non_dynamic_rows, domain_columns)]
    weighted_operator = np.zeros((row_dim + acceleration_dim, domain_dim), dtype=float)
    weighted_operator[:row_dim, :] = non_dynamic_jacobian
    weighted_operator[row_dim:, state_dim:] = float(h) * np.eye(acceleration_dim)

    singular_values = np.linalg.svd(weighted_operator, compute_uv=False)
    rank_tol = float(max(weighted_operator.shape) * np.finfo(float).eps * singular_values[0])
    rank = int(np.linalg.matrix_rank(weighted_operator, tol=rank_tol))
    pseudo_inverse = np.linalg.pinv(weighted_operator, rcond=1.0e-12)
    state_projection = np.zeros((state_dim, domain_dim), dtype=float)
    state_projection[:, :state_dim] = np.eye(state_dim)
    state_projection_constant = float(np.linalg.norm(state_projection @ pseudo_inverse, ord=2))

    return {
        "h": float(h),
        "non_dynamic_row_count": row_dim,
        "state_column_count": state_dim,
        "acceleration_column_count": acceleration_dim,
        "domain_column_count": domain_dim,
        "weighted_operator_shape": [int(weighted_operator.shape[0]), int(weighted_operator.shape[1])],
        "rank_tolerance": rank_tol,
        "weighted_operator_rank": rank,
        "full_column_rank": rank == domain_dim,
        "max_singular_value": float(singular_values[0]),
        "min_singular_value": float(singular_values[-1]),
        "condition_number": float(singular_values[0] / singular_values[-1]),
        "finite_state_projection_constant": state_projection_constant,
        "non_dynamic_jacobian_rank": int(np.linalg.matrix_rank(non_dynamic_jacobian, tol=rank_tol)),
        "non_dynamic_row_families": NON_DYNAMIC_ROW_FAMILIES,
        "state_column_families": STATE_COLUMN_FAMILIES,
        "acceleration_column_families": ACCELERATION_COLUMN_FAMILIES,
    }


def main() -> None:
    module = import_run_module()
    ps2_target = read_json(PAPER / "D5_P_STATE_PS2_WEIGHTED_TARGET_AUDIT.json")
    dynamic_oracle = read_json(PAPER / "DYNAMIC_ROW_ORACLE_GATE.json")
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
        probe = build_weighted_operator(module, jacobian, h)
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
    max_state_projection_constant = max(float(row["finite_state_projection_constant"]) for row in rows)
    min_singular = min(float(row["min_singular_value"]) for row in rows)

    result = {
        "schema": "d5-p-state-ps2-linearization-probe-v1",
        "status": "finite_ps2_weighted_linearization_probe_recorded_ps2_open",
        "read_only": True,
        "run_v047_invoked": False,
        "one_step_stage_newton_invoked": True,
        "submission_ready": False,
        "proof_gap_closed": False,
        "pc2_closed": False,
        "primitive_closed": False,
        "ps2_weighted_linearization_probe_recorded": True,
        "ps2_inverse_or_infsup_closed": False,
        "uniform_constant_proved": False,
        "p_state_lift_rate_proved": False,
        "case": CASE_NAME,
        "h_values": H_VALUES,
        "operator_definition": {
            "map": "(delta S, delta A) -> (D N_h^nd[delta S, delta A], h delta A)",
            "state_block": "S=(r,eta,v,omega) over three Gauss stages and two bodies",
            "acceleration_block": "A=(a,alpha) over three Gauss stages and two bodies",
            "lambda_columns_excluded": True,
            "non_dynamic_rows": NON_DYNAMIC_ROW_FAMILIES,
        },
        "summary": {
            "probe_count": len(rows),
            "state_block_dimension": rows[0]["state_column_count"],
            "auxiliary_acceleration_dimension": rows[0]["acceleration_column_count"],
            "domain_dimension": rows[0]["domain_column_count"],
            "non_dynamic_row_dimension": rows[0]["non_dynamic_row_count"],
            "weighted_operator_shape": rows[0]["weighted_operator_shape"],
            "finite_probe_full_column_rank_all": full_column_rank_all,
            "min_weighted_operator_rank": min(int(row["weighted_operator_rank"]) for row in rows),
            "max_weighted_operator_rank": max(int(row["weighted_operator_rank"]) for row in rows),
            "min_singular_value_across_probes": min_singular,
            "max_condition_number_across_probes": max(float(row["condition_number"]) for row in rows),
            "max_finite_state_projection_constant": max_state_projection_constant,
            "max_gauss_stage_residual_norm": max_residual,
            "ps2_weighted_target_spec_closed": ps2_target.get("ps2_target_spec_closed"),
            "ps2_inverse_or_infsup_closed": False,
        },
        "probes": rows,
        "source_consistency": {
            "run_v047_path": str(RUN.relative_to(ROOT)),
            "runtime_row_dimension": getattr(module, "DIM", None),
            "ps2_target_schema": ps2_target.get("schema"),
            "ps2_target_spec_closed": ps2_target.get("ps2_target_spec_closed"),
            "ps2_target_infsup_closed": ps2_target.get("ps2_inverse_or_infsup_closed"),
            "ps2_target_state_dim": ps2_target.get("summary", {}).get("state_block_dimension"),
            "ps2_target_acc_dim": ps2_target.get("summary", {}).get("auxiliary_acceleration_dimension"),
            "ps2_target_row_dim": ps2_target.get("summary", {}).get("non_dynamic_row_dimension"),
            "dynamic_oracle_schema": dynamic_oracle.get("schema"),
            "dynamic_oracle_runtime_rows": dynamic_oracle_formula.get("row_count"),
            "dynamic_oracle_runtime_columns": dynamic_oracle_formula.get("column_count"),
        },
        "claim_boundary": {
            "allowed_now": (
                "finite solved-stage probes show the weighted PS2 operator has full column rank "
                "at h=0.04, 0.02, and 0.01 for the smooth cylindrical-chain case"
            ),
            "forbidden_now": [
                "uniform PS2 inverse or inf-sup theorem",
                "P_state lift-rate proof",
                "D5 Taylor term certification through P_state",
                "primitive/Taylor PC2 route closure",
                "submission-ready proof",
            ],
            "close_condition": (
                "PS2 closes only after a uniform compact-tube inverse or inf-sup proof bounds "
                "the weighted operator independently of the finite diagnostic h-values."
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
                "weighted_operator_rank",
                "domain_column_count",
                "full_column_rank",
                "min_singular_value",
                "condition_number",
                "finite_state_projection_constant",
                "gauss_stage_residual_norm",
                "gauss_stage_newton_iterations",
            ],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow({name: row[name] for name in writer.fieldnames})

    lines = [
        "# D5 P_state PS2 Linearization Probe",
        "",
        "Status: **finite weighted linearization probe recorded; PS2 remains open**.",
        "",
        "This diagnostic evaluates the accepted v047 residual Jacobian at solved",
        "one-step Gauss stages. It forms the finite weighted operator",
        "`(delta S, delta A) -> (D N_h^nd[delta S, delta A], h delta A)`",
        "using the 96 non-dynamic rows and the state/acceleration columns. It",
        "does not prove a uniform compact-tube inverse or inf-sup constant.",
        "",
        "## Summary",
        "",
        f"- Case: `{CASE_NAME}`.",
        f"- Step sizes: `{', '.join(str(h) for h in H_VALUES)}`.",
        f"- State dimension: `{result['summary']['state_block_dimension']}`.",
        f"- Acceleration dimension: `{result['summary']['auxiliary_acceleration_dimension']}`.",
        f"- Non-dynamic row dimension: `{result['summary']['non_dynamic_row_dimension']}`.",
        f"- Weighted operator shape: `{result['summary']['weighted_operator_shape'][0]} x {result['summary']['weighted_operator_shape'][1]}`.",
        f"- Full column rank in all finite probes: `{result['summary']['finite_probe_full_column_rank_all']}`.",
        f"- Rank range: `{result['summary']['min_weighted_operator_rank']}..{result['summary']['max_weighted_operator_rank']}`.",
        f"- Minimum singular value across probes: `{result['summary']['min_singular_value_across_probes']:.6e}`.",
        f"- Maximum finite state projection constant: `{result['summary']['max_finite_state_projection_constant']:.6e}`.",
        f"- Maximum solved-stage residual norm: `{result['summary']['max_gauss_stage_residual_norm']:.6e}`.",
        f"- PS2 inverse or inf-sup closed: `{result['ps2_inverse_or_infsup_closed']}`.",
        f"- Primitive/Taylor PC2 route closed: `{result['pc2_closed']}`.",
        "",
        "## Probe Rows",
        "",
        "| h | rank | min singular | condition | state-projection constant | stage residual |",
        "|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| `{row['h']:.5f}` | `{row['weighted_operator_rank']}/{row['domain_column_count']}` | "
            f"`{row['min_singular_value']:.6e}` | `{row['condition_number']:.6e}` | "
            f"`{row['finite_state_projection_constant']:.6e}` | `{row['gauss_stage_residual_norm']:.6e}` |"
        )
    lines.extend(
        [
            "",
            "## Acceptance Boundary",
            "",
            "- The probe uses the implemented v047 Jacobian and the accepted row/column layout.",
            "- The finite weighted operator is full column rank on the recorded probes.",
            "- This is not a uniform compact-tube inverse or inf-sup proof.",
            "- P_state, PS2, PC2, and the unconditional D5 theorem remain open.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("d5_p_state_ps2_linearization_probe=written")
    print(f"finite_probe_full_column_rank_all={full_column_rank_all}")
    print("ps2_inverse_or_infsup_closed=False")
    print("pc2_closed=False")


if __name__ == "__main__":
    main()
