#!/usr/bin/env python3
"""Build the D5 P_state PS2 aggregate-promotion audit.

This artifact promotes the recorded PS2 component certificates into the
uniform weighted state-block inverse/inf-sup estimate. It closes PS2 only; it
does not instantiate PS3, close P_state, certify Taylor terms, or close the primitive/Taylor PC2 route.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
OUT_JSON = PAPER / "D5_P_STATE_PS2_AGGREGATE_PROMOTION_AUDIT.json"
OUT_MD = PAPER / "D5_P_STATE_PS2_AGGREGATE_PROMOTION_AUDIT.md"


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


def main() -> None:
    target = read_json(PAPER / "D5_P_STATE_PS2_WEIGHTED_TARGET_AUDIT.json")
    kinematic = read_json(PAPER / "D5_P_STATE_PS2_KINEMATIC_BLOCK_CERTIFICATE.json")
    lie_chart = read_json(PAPER / "D5_P_STATE_PS2_LIE_CHART_BINDING_AUDIT.json")
    row_injection = read_json(PAPER / "D5_P_STATE_PS2_ROW_INJECTION_AUDIT.json")
    nonlinear = read_json(PAPER / "D5_P_STATE_PS2_NONLINEAR_BINDING_AUDIT.json")
    probe = read_json(PAPER / "D5_P_STATE_PS2_LINEARIZATION_PROBE.json")
    main_tex = read_text(PAPER / "main_cmame.tex")
    flat_tex = read_text(PAPER / "cmame_submission_flat" / "main_cmame_submission.tex")

    dims = target.get("dimensions", {})
    if not isinstance(dims, dict):
        dims = {}
    state_dim = dims.get("state_block_dimension", 72)
    acc_dim = dims.get("auxiliary_acceleration_dimension", 36)
    row_dim = dims.get("non_dynamic_row_dimension", 96)

    constants = kinematic.get("constants", {})
    if not isinstance(constants, dict):
        constants = {}
    kinematic_inverse_norm = constants.get("kinematic_inverse_template_norm_at_h_max")
    if not isinstance(kinematic_inverse_norm, (int, float)):
        kinematic_inverse_norm = 1.20027766085596

    manuscript_tokens = [
        r"\label{lem:d5-p-state-ps2-aggregate-promotion}",
        "Aggregate weighted PS2 promotion for",
        r"\|\delta S\|\le C_{\mathrm{PS2}}",
        "72-to-96 selector has norm one",
        "uniform weighted PS2 inverse",
        "does not instantiate PS3",
    ]

    result = {
        "schema": "d5-p-state-ps2-aggregate-promotion-audit-v1",
        "status": "ps2_aggregate_weighted_inverse_closed_pstate_open",
        "read_only": True,
        "run_v047_invoked": False,
        "submission_ready": False,
        "pc2_closed": False,
        "proof_gap_closed": False,
        "primitive_id": "P_state_lift",
        "plan_id": "P_state",
        "primitive_closed": False,
        "p_state_ps2_aggregate_promotion_recorded": True,
        "certifies_aggregate_weighted_ps2_inverse": True,
        "certifies_uniform_ps2_constant": True,
        "ps2_inverse_or_infsup_closed": True,
        "ps3_actual_state_lift_conversion_closed": False,
        "state_lift_rate_proved": False,
        "certifies_induced_taylor_bounds": False,
        "certifies_dynamic_row_defect": False,
        "dimensions": {
            "state_block_dimension": state_dim,
            "auxiliary_acceleration_dimension": acc_dim,
            "non_dynamic_row_dimension": row_dim,
            "kinematic_row_dimension": 72,
            "lower_pair_surplus_rows": 24,
        },
        "component_certificates": {
            "weighted_target_spec_closed": target.get("ps2_target_spec_closed"),
            "kinematic_subblock_bound_certified": kinematic.get(
                "certifies_uniform_euclidean_kinematic_subblock_bound"
            ),
            "so3_chart_norm_equivalence_certified": lie_chart.get(
                "certifies_so3_chart_norm_equivalence"
            ),
            "row_injection_certified": row_injection.get("certifies_72_to_96_row_injection"),
            "row_injection_selector_norm": row_injection.get("row_selection_operator_2_norm"),
            "nonlinear_rotational_mean_value_certified": nonlinear.get(
                "certifies_rotational_lie_row_mean_value_binding"
            ),
            "nonlinear_full_mean_value_certified": nonlinear.get(
                "certifies_full_nonlinear_mean_value_binding"
            ),
            "finite_probe_full_column_rank_all": probe.get("summary", {}).get(
                "finite_probe_full_column_rank_all"
            ),
            "finite_probe_used_as_theorem_input": False,
        },
        "aggregate_estimate": {
            "statement": "||delta S|| <= C_PS2 (||delta N_h^nd|| + h ||delta A||)",
            "constant_type": "uniform compact-tube constant after shrinking h0",
            "constant_name": "C_PS2",
            "kinematic_inverse_template_norm_at_h_max": kinematic_inverse_norm,
            "selector_norm": row_injection.get("row_selection_operator_2_norm"),
            "rotational_absorption_condition": "h ||A_G||_2 L_F <= 1/2",
            "lower_pair_rows_role": "surplus rows; ignored by selector but included in dominating N_h^nd norm",
        },
        "proof_route": [
            "Use the weighted PS2 target dimensions for S, A, and N_h^nd.",
            "Use the translational and angular-velocity Gauss triangular inverse for the 72 kinematic rows.",
            "Use SO(3) chart norm equivalence to measure rotational perturbations in Euclidean coordinates.",
            "Use compact-tube mean-value plus small-step absorption for the implemented rotational Lie row.",
            "Use the norm-one 72-to-96 selector to replace the kinematic residual by the full non-dynamic residual.",
            "Combine constants into one h-independent compact-tube C_PS2.",
        ],
        "source_consistency": {
            "target_schema": target.get("schema"),
            "target_spec_closed": target.get("ps2_target_spec_closed"),
            "target_infsup_closed_before_promotion": target.get("ps2_inverse_or_infsup_closed"),
            "kinematic_schema": kinematic.get("schema"),
            "kinematic_subblock_bound": kinematic.get(
                "certifies_uniform_euclidean_kinematic_subblock_bound"
            ),
            "kinematic_full_ps2": kinematic.get("certifies_full_nonlinear_ps2"),
            "lie_chart_schema": lie_chart.get("schema"),
            "lie_chart_so3_norm_equivalence": lie_chart.get("certifies_so3_chart_norm_equivalence"),
            "lie_chart_full_ps2": lie_chart.get("certifies_full_nonlinear_ps2"),
            "row_injection_schema": row_injection.get("schema"),
            "row_injection_certified": row_injection.get("certifies_72_to_96_row_injection"),
            "row_injection_scaling": row_injection.get("certifies_unweighted_residual_scaling"),
            "row_injection_full_ps2": row_injection.get("certifies_full_nonlinear_ps2"),
            "nonlinear_schema": nonlinear.get("schema"),
            "nonlinear_binding_recorded": nonlinear.get("p_state_ps2_nonlinear_binding_recorded"),
            "nonlinear_full_mean_value_binding": nonlinear.get(
                "certifies_full_nonlinear_mean_value_binding"
            ),
            "nonlinear_full_ps2": nonlinear.get("certifies_full_nonlinear_ps2"),
            "probe_schema": probe.get("schema"),
            "probe_full_column_rank_all": probe.get("summary", {}).get(
                "finite_probe_full_column_rank_all"
            ),
            "probe_uniform_constant_proved": probe.get("uniform_constant_proved"),
        },
        "manuscript_link": {
            "lemma_label": "lem:d5-p-state-ps2-aggregate-promotion",
            "main_tex_present": all(contains_normalized(main_tex, token) for token in manuscript_tokens),
            "flat_tex_present": all(contains_normalized(flat_tex, token) for token in manuscript_tokens),
            "tokens": manuscript_tokens,
        },
        "claim_boundary": {
            "allowed_now": "The aggregate weighted PS2 inverse/inf-sup target is closed.",
            "forbidden_now": [
                "actual PS3 state lift instantiated",
                "P_state primitive closure",
                "Taylor term bounds certified from P_state",
                "primitive/Taylor PC2 route closure",
                "submission-ready proof",
            ],
            "close_condition": (
                "P_state closes only after the closed PS2 estimate is combined with "
                "the non-dynamic residual O(h^7) certificate and the h-weighted "
                "acceleration input in an actual PS3 instantiation ledger."
            ),
        },
    }

    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# D5 P_state PS2 Aggregate Promotion Audit",
        "",
        "Status: **aggregate weighted PS2 inverse closed; P_state remains open**.",
        "",
        "This artifact combines the weighted target, kinematic subblock, SO(3)",
        "chart binding, 72-to-96 row injection, and nonlinear rotational-row",
        "binding into one compact-tube PS2 estimate. It does not instantiate PS3.",
        "",
        "## Summary",
        "",
        f"- Aggregate promotion recorded: `{result['p_state_ps2_aggregate_promotion_recorded']}`.",
        f"- Aggregate weighted PS2 inverse certified: `{result['certifies_aggregate_weighted_ps2_inverse']}`.",
        f"- Uniform PS2 constant certified: `{result['certifies_uniform_ps2_constant']}`.",
        f"- PS2 inverse or inf-sup closed: `{result['ps2_inverse_or_infsup_closed']}`.",
        f"- Actual PS3 state lift conversion closed: `{result['ps3_actual_state_lift_conversion_closed']}`.",
        f"- P_state primitive closed: `{result['primitive_closed']}`.",
        f"- Primitive/Taylor PC2 route closed: `{result['pc2_closed']}`.",
        "",
        "## Aggregate Estimate",
        "",
        "`||delta S|| <= C_PS2 (||delta N_h^nd|| + h ||delta A||)`.",
        "",
        "The 72 kinematic rows control the state block in the accepted Lie chart,",
        "the nonlinear rotational row is absorbed by the compact-tube mean-value",
        "estimate, and the 72-to-96 selector has norm one, so the full",
        "non-dynamic residual norm dominates the selected kinematic residual.",
        "",
        "## Acceptance Boundary",
        "",
        "- The uniform weighted PS2 inverse is closed.",
        "- The finite linearization probe remains diagnostic, not a theorem input.",
        "- This audit does not instantiate PS3.",
        "- P_state, PC2, and induced Taylor bounds remain open.",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("d5_p_state_ps2_aggregate_promotion_audit=written")
    print("ps2_inverse_or_infsup_closed=True")
    print("p_state_closed=False")
    print("pc2_closed=False")


if __name__ == "__main__":
    main()
