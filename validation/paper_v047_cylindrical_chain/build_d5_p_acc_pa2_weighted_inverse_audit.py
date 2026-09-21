#!/usr/bin/env python3
"""Build the D5 P_acc PA2 weighted-inverse audit.

This audit refines the PA2 acceleration-lift gap.  The existing PA2
obstruction shows that velocity-collocation alone loses one power of h when
solved for acceleration.  Here we evaluate the same finite weighted PS2
operator used for P_state and measure both the unweighted acceleration
projection and the weighted h*acceleration projection.  The artifact is a
diagnostic only; it does not prove a uniform compact-tube inverse, PA2, or
PC2.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np


PAPER = Path(__file__).resolve().parent
from paper_paths import LATEX, package_path as manuscript_path
ROOT = PAPER.parent
RUN = ROOT.parent / "numerics" / "v047_cylindrical_chain_pipeline" / "run_v047.py"
OUT_JSON = PAPER / "D5_P_ACC_PA2_WEIGHTED_INVERSE_AUDIT.json"
OUT_MD = PAPER / "D5_P_ACC_PA2_WEIGHTED_INVERSE_AUDIT.md"

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


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def contains_normalized(text: str, token: str) -> bool:
    return token in text or " ".join(token.split()) in " ".join(text.split())


def import_run_module() -> Any:
    spec = importlib.util.spec_from_file_location("run_v047_p_acc_pa2_weighted_inverse", RUN)
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


def projection_row(module: Any, jacobian: np.ndarray, h: float, residual_norm: float) -> dict[str, Any]:
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
    acceleration_projection = np.zeros((acceleration_dim, domain_dim), dtype=float)
    acceleration_projection[:, state_dim:] = np.eye(acceleration_dim)

    state_projection_constant = float(np.linalg.norm(state_projection @ pseudo_inverse, ord=2))
    acceleration_projection_constant = float(np.linalg.norm(acceleration_projection @ pseudo_inverse, ord=2))
    weighted_acceleration_projection_constant = float(
        np.linalg.norm(float(h) * acceleration_projection @ pseudo_inverse, ord=2)
    )

    return {
        "case": CASE_NAME,
        "h": float(h),
        "non_dynamic_row_count": row_dim,
        "state_column_count": state_dim,
        "acceleration_column_count": acceleration_dim,
        "domain_column_count": domain_dim,
        "weighted_operator_shape": [int(weighted_operator.shape[0]), int(weighted_operator.shape[1])],
        "weighted_operator_rank": rank,
        "full_column_rank": rank == domain_dim,
        "rank_tolerance": rank_tol,
        "min_singular_value": float(singular_values[-1]),
        "max_singular_value": float(singular_values[0]),
        "condition_number": float(singular_values[0] / singular_values[-1]),
        "state_projection_constant": state_projection_constant,
        "unweighted_acceleration_projection_constant": acceleration_projection_constant,
        "weighted_h_acceleration_projection_constant": weighted_acceleration_projection_constant,
        "h_times_unweighted_acceleration_projection_constant": float(h) * acceleration_projection_constant,
        "gauss_stage_residual_norm": float(residual_norm),
        "operator_definition": "(delta S, delta A) -> (D N_h^nd[delta S, delta A], h delta A)",
    }


def close_requirement_satisfied(manifest: dict[str, Any], requirement_id: str) -> bool | None:
    for row in manifest.get("close_requirements", []):
        if isinstance(row, dict) and row.get("id") == requirement_id:
            value = row.get("satisfied")
            return value if isinstance(value, bool) else None
    return None


def main() -> None:
    module = import_run_module()
    ps2_probe = read_json(PAPER / "D5_P_STATE_PS2_LINEARIZATION_PROBE.json")
    p_acc_lift_obstruction = read_json(PAPER / "D5_P_ACC_LIFT_OBSTRUCTION_AUDIT.json")
    p_acc_independence = read_json(PAPER / "D5_P_ACC_INDEPENDENCE_AUDIT.json")
    p_acc_row_binding = read_json(PAPER / "D5_P_ACC_ROW_BINDING_AUDIT.json")
    proof_manifest = read_json(PAPER / "PROOF_CLOSURE_MANIFEST.json")
    main_tex = read_text(LATEX / "main_cmame.tex")
    flat_tex = read_text(LATEX / "cmame_submission_flat" / "main_cmame_submission.tex")

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
        rows.append(projection_row(module, jacobian, float(h), float(solve_diag["max_gauss_stage_residual_norm"])))

    manuscript_tokens = [
        "PA2 weighted-inverse diagnostic",
        r"bounded finite control of \(h\delta A\)",
        "does not prove a uniform unweighted acceleration lift",
        "PA2 remains open",
        "primitive-and-Taylor route to PC2 remains open",
    ]

    full_rank_all = all(row["full_column_rank"] for row in rows)
    max_unweighted_acc = max(row["unweighted_acceleration_projection_constant"] for row in rows)
    max_weighted_acc = max(row["weighted_h_acceleration_projection_constant"] for row in rows)
    max_h_times_unweighted = max(row["h_times_unweighted_acceleration_projection_constant"] for row in rows)
    min_h_times_unweighted = min(row["h_times_unweighted_acceleration_projection_constant"] for row in rows)

    result = {
        "schema": "d5-p-acc-pa2-weighted-inverse-audit-v1",
        "status": "pa2_weighted_inverse_diagnostic_recorded_unweighted_lift_open",
        "read_only": True,
        "run_v047_invoked": False,
        "one_step_stage_newton_invoked": True,
        "submission_ready": False,
        "pc2_closed": False,
        "proof_gap_closed": False,
        "primitive_id": "P_acceleration_lift",
        "primitive_closed": False,
        "pa2_closed": False,
        "pa2_weighted_inverse_probe_recorded": True,
        "weighted_h_acceleration_control_recorded": True,
        "unweighted_acceleration_uniform_control_proved": False,
        "acceleration_lift_rate_proved": False,
        "term_bounds_proved": 0,
        "case": CASE_NAME,
        "h_values": H_VALUES,
        "operator_definition": {
            "map": "(delta S, delta A) -> (D N_h^nd[delta S, delta A], h delta A)",
            "source": "same finite weighted operator used by D5_P_STATE_PS2_LINEARIZATION_PROBE",
            "state_block": "S=(r,eta,v,omega) over three Gauss stages and two bodies",
            "acceleration_block": "A=(a,alpha) over three Gauss stages and two bodies",
            "lambda_columns_excluded": True,
            "non_dynamic_rows": NON_DYNAMIC_ROW_FAMILIES,
        },
        "summary": {
            "probe_count": len(rows),
            "state_block_dimension": rows[0]["state_column_count"],
            "acceleration_block_dimension": rows[0]["acceleration_column_count"],
            "domain_dimension": rows[0]["domain_column_count"],
            "non_dynamic_row_dimension": rows[0]["non_dynamic_row_count"],
            "weighted_operator_shape": rows[0]["weighted_operator_shape"],
            "finite_probe_full_column_rank_all": full_rank_all,
            "min_weighted_operator_rank": min(int(row["weighted_operator_rank"]) for row in rows),
            "max_weighted_operator_rank": max(int(row["weighted_operator_rank"]) for row in rows),
            "min_singular_value_across_probes": min(float(row["min_singular_value"]) for row in rows),
            "max_condition_number_across_probes": max(float(row["condition_number"]) for row in rows),
            "max_state_projection_constant": max(float(row["state_projection_constant"]) for row in rows),
            "max_unweighted_acceleration_projection_constant": max_unweighted_acc,
            "max_weighted_h_acceleration_projection_constant": max_weighted_acc,
            "h_times_unweighted_acceleration_projection_constant_range": [
                min_h_times_unweighted,
                max_h_times_unweighted,
            ],
            "weighted_h_acceleration_control_recorded": True,
            "unweighted_acceleration_uniform_control_proved": False,
            "pa2_closed": False,
            "pc2_closed": False,
        },
        "probes": rows,
        "source_consistency": {
            "run_v047_path": str(RUN.relative_to(ROOT)),
            "runtime_row_dimension": getattr(module, "DIM", None),
            "ps2_probe_schema": ps2_probe.get("schema"),
            "ps2_probe_full_column_rank_all": ps2_probe.get("summary", {}).get(
                "finite_probe_full_column_rank_all"
            ),
            "ps2_probe_uniform_constant_proved": ps2_probe.get("uniform_constant_proved"),
            "p_acc_lift_obstruction_schema": p_acc_lift_obstruction.get("schema"),
            "p_acc_lift_obstruction_recorded": p_acc_lift_obstruction.get("pa2_obstruction_recorded"),
            "p_acc_lift_obstruction_pa2_closed": p_acc_lift_obstruction.get("pa2_closed"),
            "p_acc_independence_schema": p_acc_independence.get("schema"),
            "p_acc_independence_closed": p_acc_independence.get("pa3_independence_closed"),
            "p_acc_independence_primitive_closed": p_acc_independence.get("primitive_closed"),
            "p_acc_row_binding_schema": p_acc_row_binding.get("schema"),
            "p_acc_row_binding_closed": p_acc_row_binding.get("pa4_row_binding_closed"),
            "proof_manifest_pc2_closed": close_requirement_satisfied(proof_manifest, "PC2"),
            "proof_manifest_proof_gap_closed": proof_manifest.get("closure_state", {}).get(
                "proof_gap_closed"
            ),
            "proof_manifest_direct_route_gap_closed": proof_manifest.get("closure_state", {}).get(
                "direct_pc2_proof_gap_closed"
            ),
            "proof_manifest_proof_gap_closed_scope": proof_manifest.get("closure_state", {}).get(
                "proof_gap_closed_scope"
            ),
        },
        "manuscript_link": {
            "main_tex_present": all(contains_normalized(main_tex, token) for token in manuscript_tokens),
            "flat_tex_present": all(contains_normalized(flat_tex, token) for token in manuscript_tokens),
            "tokens": manuscript_tokens,
        },
        "claim_boundary": {
            "allowed_now": (
                "finite weighted-inverse diagnostics show bounded finite control of h*delta A "
                "through the same weighted PS2 operator used for the state lift target"
            ),
            "forbidden_now": [
                "PA2 closure",
                "P_acc primitive closure",
                "uniform unweighted acceleration lift proof",
                "Taylor term bounds certified from P_acc",
                "primitive/Taylor PC2 route closure",
                "unconditional sixth-order theorem",
            ],
            "close_condition": (
                "PA2 closes only after the weighted finite projection diagnostic is replaced "
                "by a uniform compact-tube estimate that controls the unweighted acceleration "
                "lift at O(h^7), or after the theorem explicitly carries P_acceleration_lift "
                "as an assumption."
            ),
        },
    }

    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# D5 P_acc PA2 Weighted-Inverse Audit",
        "",
        "Status: **PA2 weighted-inverse diagnostic recorded; unweighted lift remains open**.",
        "",
        "This read-only audit evaluates the same finite weighted PS2 operator",
        "used for the state-lift target and records projection constants for",
        "`delta S`, `delta A`, and `h delta A`. It is a diagnostic, not a",
        "uniform compact-tube inverse proof.",
        "",
        "## Summary",
        "",
        f"- Probe count: `{result['summary']['probe_count']}`.",
        f"- Weighted operator full column rank in all probes: `{full_rank_all}`.",
        f"- Max unweighted acceleration projection constant: `{max_unweighted_acc:.6e}`.",
        f"- Max weighted h-acceleration projection constant: `{max_weighted_acc:.6e}`.",
        f"- Weighted h-acceleration control recorded: `{result['weighted_h_acceleration_control_recorded']}`.",
        f"- Unweighted acceleration uniform control proved: `{result['unweighted_acceleration_uniform_control_proved']}`.",
        f"- PA2 closed: `{result['pa2_closed']}`.",
        f"- P_acc primitive closed: `{result['primitive_closed']}`.",
        f"- Primitive/Taylor PC2 route closed: `{result['pc2_closed']}`.",
        "",
        "## Acceptance Boundary",
        "",
        "- The finite weighted operator supports bounded finite control of `h delta A`.",
        "- The audit does not prove a uniform unweighted acceleration lift.",
        "- PA2 remains open.",
        "- `P_acc` remains open.",
        "- Primitive/Taylor PC2 lane remains open.",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("d5_p_acc_pa2_weighted_inverse_audit=written")
    print(f"probe_count={len(rows)}")
    print(f"max_unweighted_acceleration_projection_constant={max_unweighted_acc:.6e}")
    print(f"max_weighted_h_acceleration_projection_constant={max_weighted_acc:.6e}")
    print("pa2_closed=False")
    print("pc2_closed=False")


if __name__ == "__main__":
    main()
