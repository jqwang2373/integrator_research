#!/usr/bin/env python3
"""Build the D5 P_state PS3 h-acceleration input obstruction audit."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
OUT_JSON = PAPER / "D5_P_STATE_PS3_H_ACC_INPUT_OBSTRUCTION_AUDIT.json"
OUT_MD = PAPER / "D5_P_STATE_PS3_H_ACC_INPUT_OBSTRUCTION_AUDIT.md"


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def rank_range(values: list[int]) -> list[int | None]:
    if not values:
        return [None, None]
    return [min(values), max(values)]


def main() -> None:
    aggregate = read_json(PAPER / "D5_P_STATE_PS2_AGGREGATE_PROMOTION_AUDIT.json")
    conditional = read_json(PAPER / "D5_P_STATE_PS3_CONDITIONAL_CONVERSION_AUDIT.json")
    ps2_probe = read_json(PAPER / "D5_P_STATE_PS2_LINEARIZATION_PROBE.json")
    kinematic = read_json(PAPER / "KINEMATIC_ROW_DEFECT_CERTIFICATE.json")
    p_acc_obstruction = read_json(PAPER / "D5_P_ACC_LIFT_OBSTRUCTION_AUDIT.json")
    p_acc_weighted = read_json(PAPER / "D5_P_ACC_PA2_WEIGHTED_INVERSE_AUDIT.json")

    probe_summary = ps2_probe.get("summary", {})
    probe_rows = [row for row in ps2_probe.get("probes", []) if isinstance(row, dict)]
    domain_dim = int(probe_summary.get("domain_dimension", 0))
    state_dim = int(probe_summary.get("state_block_dimension", 0))
    acceleration_dim = int(probe_summary.get("auxiliary_acceleration_dimension", 0))
    non_dynamic_row_dim = int(probe_summary.get("non_dynamic_row_dimension", 0))
    weighted_operator_shape = probe_summary.get("weighted_operator_shape")
    non_dynamic_ranks = [
        int(row.get("non_dynamic_jacobian_rank", 0))
        for row in probe_rows
        if row.get("non_dynamic_jacobian_rank") is not None
    ]
    weighted_ranks = [
        int(row.get("weighted_operator_rank", 0))
        for row in probe_rows
        if row.get("weighted_operator_rank") is not None
    ]
    residual_nullities = [domain_dim - rank for rank in non_dynamic_ranks]
    residual_only_row_deficit = domain_dim - non_dynamic_row_dim
    h_values = [row.get("h") for row in probe_rows]

    result = {
        "schema": "d5-p-state-ps3-h-acc-input-obstruction-audit-v1",
        "status": "h_acc_input_obstruction_recorded_actual_ps3_open",
        "read_only": True,
        "run_v047_invoked": False,
        "submission_ready": False,
        "proof_gap_closed": False,
        "pc2_closed": False,
        "primitive_id": "P_state_lift",
        "primitive_closed": False,
        "ps3_actual_state_lift_conversion_closed": False,
        "independent_h_weighted_acceleration_input_closed": False,
        "non_circular_ps3_instantiation_closed": False,
        "certifies_induced_taylor_bounds": False,
        "certifies_taylor_bounds": False,
        "certifies_p_state": False,
        "certifies_actual_ps3": False,
        "finite_probe_is_proof": False,
        "dimensions": {
            "state_block_dimension": state_dim,
            "auxiliary_acceleration_dimension": acceleration_dim,
            "domain_dimension": domain_dim,
            "non_dynamic_row_dimension": non_dynamic_row_dim,
            "weighted_operator_shape": weighted_operator_shape,
            "residual_only_row_deficit": residual_only_row_deficit,
        },
        "finite_probe_diagnostic": {
            "probe_count": len(probe_rows),
            "h_values": h_values,
            "non_dynamic_jacobian_rank_range": rank_range(non_dynamic_ranks),
            "weighted_operator_rank_range": rank_range(weighted_ranks),
            "residual_only_nullity_range": rank_range(residual_nullities),
            "non_dynamic_jacobian_ranks": non_dynamic_ranks,
            "weighted_operator_ranks": weighted_ranks,
            "residual_only_nullities": residual_nullities,
            "weighted_operator_full_column_rank_all": probe_summary.get(
                "finite_probe_full_column_rank_all"
            ),
            "h_acceleration_rows_required_by_weighted_operator": True,
            "residual_only_input_sufficient_for_h_acceleration": False,
            "theorem_level_independent_h_acceleration_input_proved": False,
        },
        "strict_obstruction": {
            "ps2_estimate": "||delta S|| <= C_PS2 (||delta N_h^nd|| + h ||delta A||)",
            "residual_only_gap": (
                "The current 96 non-dynamic rows act on the 108-dimensional "
                "(S,A) domain and therefore do not by themselves provide the "
                "h-weighted acceleration input required by the PS2 estimate."
            ),
            "finite_rank_diagnostic": (
                "At the recorded solved stages, DN_h^nd has rank 96 over the "
                "108-dimensional domain, while adjoining hI_A raises the "
                "weighted operator rank to 108."
            ),
            "velocity_collocation_formula": p_acc_obstruction.get("rate_algebra", {}).get(
                "velocity_collocation_difference"
            ),
            "acceleration_formula": p_acc_obstruction.get("rate_algebra", {}).get(
                "acceleration_difference"
            ),
            "velocity_collocation_circular_for_p_state": True,
            "why_velocity_collocation_is_circular": (
                "The velocity-collocation rearrangement gives delta_A from "
                "delta_V and rho_V. Since delta_V is a P_state component, using "
                "that rearrangement as the independent PS3 input would assume "
                "part of the state lift being proved."
            ),
        },
        "non_circular_close_routes": {
            "recommended_route": "full_132_row_dynamic_residual_route",
            "route_R1_full_132_row_dynamic_residual": {
                "closed": False,
                "non_circular_if_completed": True,
                "requires": [
                    "PC2 D5 dynamic-row defect proof for the 36 Newton-Euler rows",
                    "stage-residual perturbation criterion applied to the full 132-row residual",
                    "no use of P_state actual PS3 as an input to the dynamic-row defect proof",
                ],
                "why_it_addresses_the_obstruction": (
                    "The missing 12 non-dynamic directions are the dynamic/free "
                    "stage directions. A full residual perturbation proof controls "
                    "the whole stage vector directly rather than asking the "
                    "96-row non-dynamic residual to supply h delta A."
                ),
            },
            "route_R2_stronger_velocity_before_inversion": {
                "closed": False,
                "non_circular_if_completed": True,
                "requires": [
                    "delta_V=O(h^8) before velocity-collocation inversion",
                    "rho_V=O(h^8) before velocity-collocation inversion",
                    "a proof of those O(h^8) bounds that does not use P_state actual PS3",
                ],
                "why_not_closed": (
                    "Current recorded inputs only give the O(h^7) scale before "
                    "the A_G^{-1}/h velocity-collocation inversion."
                ),
            },
            "route_R3_explicit_theorem_assumption": {
                "closed": False,
                "non_circular_if_stated": True,
                "requires": [
                    "state the independent h-weighted acceleration input as an explicit theorem assumption",
                    "weaken the manuscript claim boundary accordingly",
                    "prevent the assumption from being reported as a proved PS3 input",
                ],
                "why_not_closure": (
                    "This would make the theorem conditional rather than proving "
                    "actual PS3 from the current residual artifacts."
                ),
            },
        },
        "next_strict_proof_target": {
            "target": "PC2 full dynamic-row defect proof or explicit theorem weakening",
            "recommended_first_step": (
                "Close the D5 lifted-stage dynamic defect for the 36 Newton-Euler "
                "rows by a row-local Taylor proof, then use the full stage-residual "
                "perturbation criterion to obtain the missing state and acceleration "
                "input non-circularly."
            ),
            "must_not_do": [
                "derive h delta A from delta_V after P_state is the unknown being solved for",
                "promote the finite rank probe to a compact-tube theorem",
                "claim actual PS3 while PC2/D5 remains open",
            ],
        },
        "source_consistency": {
            "aggregate_schema": aggregate.get("schema"),
            "aggregate_ps2_closed": aggregate.get("ps2_inverse_or_infsup_closed"),
            "aggregate_primitive_closed": aggregate.get("primitive_closed"),
            "aggregate_pc2_closed": aggregate.get("pc2_closed"),
            "conditional_schema": conditional.get("schema"),
            "conditional_closed": conditional.get("ps3_conditional_conversion_closed"),
            "conditional_actual_inputs_closed": conditional.get(
                "actual_ps3_input_instantiation_closed"
            ),
            "conditional_actual_ps3_closed": conditional.get(
                "ps3_actual_state_lift_conversion_closed"
            ),
            "ps2_probe_schema": ps2_probe.get("schema"),
            "ps2_probe_recorded": ps2_probe.get("ps2_weighted_linearization_probe_recorded"),
            "ps2_probe_uniform_constant_proved": ps2_probe.get("uniform_constant_proved"),
            "ps2_probe_pc2_closed": ps2_probe.get("pc2_closed"),
            "kinematic_schema": kinematic.get("schema"),
            "kinematic_certified_rows": kinematic.get("proof_scope", {}).get(
                "certified_row_count"
            ),
            "kinematic_excluded_rows": kinematic.get("proof_scope", {}).get(
                "excluded_row_count"
            ),
            "p_acc_obstruction_schema": p_acc_obstruction.get("schema"),
            "p_acc_pa2_closed": p_acc_obstruction.get("pa2_closed"),
            "p_acc_current_unweighted_acceleration_rate": p_acc_obstruction.get(
                "current_recorded_inputs_imply_only_unweighted_acceleration_rate"
            ),
            "p_acc_velocity_collocation_alone_sufficient": p_acc_obstruction.get(
                "velocity_collocation_alone_sufficient_for_O_h7_acceleration"
            ),
            "p_acc_pc2_closed": p_acc_obstruction.get("pc2_closed"),
            "p_acc_weighted_schema": p_acc_weighted.get("schema"),
            "p_acc_weighted_h_control_recorded": p_acc_weighted.get(
                "weighted_h_acceleration_control_recorded"
            ),
            "p_acc_weighted_unweighted_uniform_control_proved": p_acc_weighted.get(
                "unweighted_acceleration_uniform_control_proved"
            ),
        },
        "summary": {
            "h_acceleration_input_obstruction_recorded": True,
            "state_block_dimension": state_dim,
            "auxiliary_acceleration_dimension": acceleration_dim,
            "domain_dimension": domain_dim,
            "non_dynamic_row_dimension": non_dynamic_row_dim,
            "residual_only_row_deficit": residual_only_row_deficit,
            "finite_probe_nullity_min": min(residual_nullities) if residual_nullities else None,
            "finite_probe_nullity_max": max(residual_nullities) if residual_nullities else None,
            "finite_probe_non_dynamic_rank_min": min(non_dynamic_ranks) if non_dynamic_ranks else None,
            "finite_probe_non_dynamic_rank_max": max(non_dynamic_ranks) if non_dynamic_ranks else None,
            "finite_probe_weighted_operator_rank_min": min(weighted_ranks) if weighted_ranks else None,
            "finite_probe_weighted_operator_rank_max": max(weighted_ranks) if weighted_ranks else None,
            "finite_probe_weighted_operator_full_rank_all": probe_summary.get(
                "finite_probe_full_column_rank_all"
            ),
            "residual_only_input_sufficient_for_h_acceleration": False,
            "recommended_non_circular_close_route": "full_132_row_dynamic_residual_route",
            "full_dynamic_residual_route_closed": False,
            "pc2_required_for_recommended_route": True,
            "stronger_velocity_route_closed": False,
            "explicit_assumption_route_available": True,
            "independent_h_weighted_acceleration_input_closed": False,
            "non_circular_ps3_instantiation_closed": False,
            "ps3_actual_state_lift_conversion_closed": False,
            "primitive_closed": False,
            "pc2_closed": False,
            "induced_taylor_bounds_proved": 0,
        },
        "claim_boundary": {
            "allowed_now": (
                "The current evidence records a strict obstruction: residual-only "
                "non-dynamic rows do not supply the independent h-weighted "
                "acceleration input required by actual PS3."
            ),
            "forbidden_now": [
                "finite probe promoted to theorem-level PS3 input",
                "velocity collocation used circularly as P_state input",
                "actual PS3 state lift proved",
                "P_state primitive closure",
                "Taylor term bounds certified from P_state",
                "primitive/Taylor PC2 route closure",
                "submission-ready proof",
            ],
            "close_condition": (
                "Actual PS3 requires a theorem-level, non-circular source of "
                "h ||delta A||=O(h^7), or an explicitly stated theorem assumption, "
                "before the conditional PS3 estimate can be instantiated."
            ),
        },
    }

    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# D5 P_state PS3 H-Acceleration Input Obstruction Audit",
        "",
        "Status: **h-weighted acceleration input obstruction recorded; actual PS3 remains open**.",
        "",
        "This read-only audit records why the current P_state PS3 evidence cannot",
        "non-circularly supply the `h delta A` input required by the aggregate",
        "weighted PS2 estimate.",
        "",
        "## Summary",
        "",
        f"- State/acceleration/domain dimensions: `{state_dim}` / `{acceleration_dim}` / `{domain_dim}`.",
        f"- Non-dynamic residual rows: `{non_dynamic_row_dim}`.",
        f"- Residual-only row deficit: `{residual_only_row_deficit}`.",
        f"- Residual-only finite nullity range: `{result['summary']['finite_probe_nullity_min']}`-`{result['summary']['finite_probe_nullity_max']}`.",
        f"- Non-dynamic finite rank range: `{result['summary']['finite_probe_non_dynamic_rank_min']}`-`{result['summary']['finite_probe_non_dynamic_rank_max']}`.",
        f"- Weighted operator finite rank range: `{result['summary']['finite_probe_weighted_operator_rank_min']}`-`{result['summary']['finite_probe_weighted_operator_rank_max']}`.",
        f"- Weighted operator full column rank in probes: `{result['summary']['finite_probe_weighted_operator_full_rank_all']}`.",
        f"- Residual-only input sufficient for h-acceleration: `{result['summary']['residual_only_input_sufficient_for_h_acceleration']}`.",
        f"- Independent h-weighted acceleration input closed: `{result['summary']['independent_h_weighted_acceleration_input_closed']}`.",
        f"- Actual PS3 state lift conversion closed: `{result['summary']['ps3_actual_state_lift_conversion_closed']}`.",
        f"- P_state primitive closed: `{result['summary']['primitive_closed']}`.",
        f"- Induced Taylor bounds proved: `{result['summary']['induced_taylor_bounds_proved']}/162`.",
        f"- Primitive/Taylor PC2 route closed: `{result['summary']['pc2_closed']}`.",
        "",
        "## Strict Obstruction",
        "",
        "`||delta S|| <= C_PS2 (||delta N_h^nd|| + h ||delta A||)`.",
        "",
        "The current 96 non-dynamic residual rows act on the 108-dimensional",
        "`(S,A)` domain. At the recorded solved stages, `DN_h^nd` has rank",
        "`96`, while `[DN_h^nd; hI_A]` has rank `108`. Thus the weighted",
        "operator becomes full column rank only after the `h delta A` rows are",
        "adjoined.",
        "",
        "Velocity collocation gives",
        "",
        "`delta_A = h^{-1} (A_G^{-1} \\otimes I) (delta_V - rho_V)`.",
        "",
        "That identity uses `delta_V`, which is a component of the `P_state`",
        "unknown. It is therefore circular as an independent PS3 input for",
        "proving the `P_state` lift.",
        "",
        "## Acceptance Boundary",
        "",
        "- This audit does not prove a theorem-level independent h-acceleration input.",
        "- The finite rank probe is diagnostic evidence, not a proof.",
        "- Actual PS3 remains open.",
        "- `P_state` remains open.",
        "- Primitive/Taylor PC2 lane remains open.",
        "",
        "## Strict Close Route",
        "",
        "The recommended non-circular close route is the full 132-row dynamic",
        "residual route: prove the D5 lifted-stage dynamic defect for the 36",
        "Newton-Euler rows by row-local Taylor expansion, then apply the full",
        "stage-residual perturbation criterion. This route would control the",
        "missing dynamic/free directions directly instead of asking the",
        "96-row residual-only map to supply `h delta A`.",
        "",
        "Two other routes remain possible but are not closed: prove",
        "`delta_V=O(h^8)` and `rho_V=O(h^8)` before the `A_G^{-1}/h` inversion,",
        "or weaken the theorem by stating the independent h-weighted",
        "acceleration input as an explicit assumption.",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("d5_p_state_ps3_h_acc_input_obstruction_audit=written")
    print("residual_only_row_deficit=12")
    print("finite_probe_nullity_range=12-12")
    print("independent_h_weighted_acceleration_input_closed=False")
    print("ps3_actual_state_lift_conversion_closed=False")
    print("pc2_closed=False")


if __name__ == "__main__":
    main()
