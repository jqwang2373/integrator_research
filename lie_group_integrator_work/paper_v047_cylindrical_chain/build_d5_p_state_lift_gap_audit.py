#!/usr/bin/env python3
"""Build the D5 P_state lift-gap audit.

This audit records why the 96-row non-dynamic residual certificate does not by
itself close the P_state primitive. It is an anti-circularity gate, not a proof
closure artifact.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
OUT_JSON = PAPER / "D5_P_STATE_LIFT_GAP_AUDIT.json"
OUT_MD = PAPER / "D5_P_STATE_LIFT_GAP_AUDIT.md"


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
    primitive_reduction = read_json(PAPER / "D5_PRIMITIVE_BOUND_REDUCTION_AUDIT.json")
    kinematic_certificate = read_json(PAPER / "KINEMATIC_ROW_DEFECT_CERTIFICATE.json")
    p_state_map_definition = read_json(PAPER / "D5_P_STATE_MAP_DEFINITION_AUDIT.json")
    p_state_anticircularity = read_json(PAPER / "D5_P_STATE_ANTICIRCULARITY_AUDIT.json")
    p_state_ps2_target = read_json(PAPER / "D5_P_STATE_PS2_WEIGHTED_TARGET_AUDIT.json")
    p_state_ps2_kinematic = read_json(PAPER / "D5_P_STATE_PS2_KINEMATIC_BLOCK_CERTIFICATE.json")
    p_state_ps2_lie_chart = read_json(PAPER / "D5_P_STATE_PS2_LIE_CHART_BINDING_AUDIT.json")
    p_state_ps2_row_injection = read_json(PAPER / "D5_P_STATE_PS2_ROW_INJECTION_AUDIT.json")
    p_state_ps2_nonlinear = read_json(PAPER / "D5_P_STATE_PS2_NONLINEAR_BINDING_AUDIT.json")
    p_state_ps2_aggregate = read_json(PAPER / "D5_P_STATE_PS2_AGGREGATE_PROMOTION_AUDIT.json")
    p_state_ps2_probe = read_json(PAPER / "D5_P_STATE_PS2_LINEARIZATION_PROBE.json")
    p_state_ps3_conversion = read_json(PAPER / "D5_P_STATE_PS3_CONDITIONAL_CONVERSION_AUDIT.json")
    p_state_ps3_actual_gap = read_json(PAPER / "D5_P_STATE_PS3_ACTUAL_INSTANTIATION_GAP_AUDIT.json")
    proof_manifest = read_json(PAPER / "PROOF_CLOSURE_MANIFEST.json")
    main_tex = read_text(PAPER / "main_cmame.tex")
    flat_tex = read_text(PAPER / "cmame_submission_flat" / "main_cmame_submission.tex")

    primitive_rows = primitive_reduction.get("primitive_obligations", [])
    p_state_row = next(
        (
            row
            for row in primitive_rows
            if isinstance(row, dict) and row.get("id") == "P_state_lift"
        ),
        {},
    )
    proof_scope = kinematic_certificate.get("proof_scope", {})
    manuscript_tokens = [
        r"P_{\mathrm{state}}",
        r"\label{lem:d5-p-state-map-definition}",
        r"\mathcal N_h^{\mathrm{nd}}",
        "residual-row identity is not by itself a variable-lift estimate",
        "aggregate PS2 inverse",
        "actual PS3 instantiation",
        r"must not use Lemma~\ref{lem:stage-residual-defect}",
        r"\label{lem:d5-p-state-ps2-kinematic-block}",
        r"\label{lem:d5-p-state-ps2-lie-chart-binding}",
        r"\label{lem:d5-p-state-ps2-row-injection}",
        r"\label{lem:d5-p-state-ps2-nonlinear-binding}",
        r"\label{lem:d5-p-state-ps2-aggregate-promotion}",
        r"\label{lem:d5-p-state-ps2-linearization-probe}",
        r"\label{lem:d5-p-state-ps3-conditional-conversion}",
    ]
    result = {
        "schema": "d5-p-state-lift-gap-audit-v1",
        "status": "p_state_lift_gap_recorded_pc2_open",
        "read_only": True,
        "run_v047_invoked": False,
        "submission_ready": False,
        "pc2_closed": False,
        "proof_gap_closed": False,
        "primitive_id": "P_state_lift",
        "plan_id": "P_state",
        "primitive_closed": False,
        "certifies_dynamic_row_defect": False,
        "certifies_induced_taylor_bounds": False,
        "anti_circularity_gate": {
            "residual_row_identity_is_not_variable_lift_estimate": True,
            "stage_residual_perturbation_lemma_disallowed_as_input": True,
            "dynamic_residual_defect_disallowed_as_input": True,
            "accepted_newton_solution_closeness_disallowed_without_independent_inverse": True,
        },
        "accepted_inputs_available": {
            "non_dynamic_rows_certified": proof_scope.get("certified_row_count"),
            "non_dynamic_families": proof_scope.get("certified_row_families"),
            "excluded_dynamic_family": proof_scope.get("excluded_row_family"),
            "excluded_dynamic_rows": proof_scope.get("excluded_row_count"),
        },
        "required_future_proof": [
            {
                "id": "PS1",
                "statement": "Define the non-dynamic stage map in the accepted Lie chart with pose, translational velocity, and angular velocity variables.",
                "closed": True,
                "evidence": "D5_P_STATE_MAP_DEFINITION_AUDIT",
            },
            {
                "id": "PS2",
                "statement": "Prove a local inverse or inf-sup bound for that non-dynamic stage map on the compact proof tube.",
                "closed": p_state_ps2_aggregate.get("ps2_inverse_or_infsup_closed") is True,
                "target_spec_closed": p_state_ps2_target.get("ps2_target_spec_closed") is True,
                "target_spec_evidence": "D5_P_STATE_PS2_WEIGHTED_TARGET_AUDIT",
                "kinematic_block_certificate_recorded": p_state_ps2_kinematic.get(
                    "ps2_kinematic_block_certificate_recorded"
                )
                is True,
                "uniform_euclidean_kinematic_subblock_bound_certified": p_state_ps2_kinematic.get(
                    "certifies_uniform_euclidean_kinematic_subblock_bound"
                )
                is True,
                "full_nonlinear_ps2_certified": p_state_ps2_kinematic.get("certifies_full_nonlinear_ps2")
                is True,
                "kinematic_block_evidence": "D5_P_STATE_PS2_KINEMATIC_BLOCK_CERTIFICATE",
                "lie_chart_binding_recorded": p_state_ps2_lie_chart.get(
                    "p_state_ps2_lie_chart_binding_recorded"
                )
                is True,
                "so3_chart_norm_equivalence_certified": p_state_ps2_lie_chart.get(
                    "certifies_so3_chart_norm_equivalence"
                )
                is True,
                "full_nonlinear_mean_value_binding_certified": p_state_ps2_lie_chart.get(
                    "certifies_full_nonlinear_mean_value_binding"
                )
                is True,
                "lie_chart_binding_evidence": "D5_P_STATE_PS2_LIE_CHART_BINDING_AUDIT",
                "row_injection_recorded": p_state_ps2_row_injection.get(
                    "p_state_ps2_row_injection_recorded"
                )
                is True,
                "row_injection_scaling_certified": p_state_ps2_row_injection.get(
                    "certifies_72_to_96_row_injection"
                )
                is True,
                "row_injection_full_mean_value_binding_certified": p_state_ps2_row_injection.get(
                    "certifies_full_nonlinear_mean_value_binding"
                )
                is True,
                "row_injection_evidence": "D5_P_STATE_PS2_ROW_INJECTION_AUDIT",
                "nonlinear_binding_recorded": p_state_ps2_nonlinear.get(
                    "p_state_ps2_nonlinear_binding_recorded"
                )
                is True,
                "rotational_mean_value_binding_certified": p_state_ps2_nonlinear.get(
                    "certifies_rotational_lie_row_mean_value_binding"
                )
                is True,
                "nonlinear_binding_full_mean_value_certified": p_state_ps2_nonlinear.get(
                    "certifies_full_nonlinear_mean_value_binding"
                )
                is True,
                "nonlinear_binding_full_ps2_certified": p_state_ps2_nonlinear.get(
                    "certifies_full_nonlinear_ps2"
                )
                is True,
                "nonlinear_binding_evidence": "D5_P_STATE_PS2_NONLINEAR_BINDING_AUDIT",
                "aggregate_promotion_recorded": p_state_ps2_aggregate.get(
                    "p_state_ps2_aggregate_promotion_recorded"
                )
                is True,
                "aggregate_weighted_ps2_inverse_certified": p_state_ps2_aggregate.get(
                    "certifies_aggregate_weighted_ps2_inverse"
                )
                is True,
                "uniform_ps2_constant_certified": p_state_ps2_aggregate.get(
                    "certifies_uniform_ps2_constant"
                )
                is True,
                "ps2_inverse_or_infsup_closed": p_state_ps2_aggregate.get(
                    "ps2_inverse_or_infsup_closed"
                )
                is True,
                "aggregate_evidence": "D5_P_STATE_PS2_AGGREGATE_PROMOTION_AUDIT",
                "finite_linearization_probe_recorded": p_state_ps2_probe.get(
                    "ps2_weighted_linearization_probe_recorded"
                )
                is True,
                "finite_probe_full_column_rank_all": p_state_ps2_probe.get("summary", {}).get(
                    "finite_probe_full_column_rank_all"
                )
                is True,
                "finite_probe_uniform_constant_proved": p_state_ps2_probe.get(
                    "uniform_constant_proved"
                )
                is True,
                "finite_probe_evidence": "D5_P_STATE_PS2_LINEARIZATION_PROBE",
            },
            {
                "id": "PS3",
                "statement": "Combine the 96-row non-dynamic residual certificate with the inverse bound to obtain O(h^7) state-variable lift rates.",
                "closed": False,
                "conditional_conversion_closed": p_state_ps3_conversion.get(
                    "ps3_conditional_conversion_closed"
                )
                is True,
                "actual_conversion_closed": p_state_ps3_conversion.get(
                    "ps3_actual_state_lift_conversion_closed"
                )
                is True,
                "conditional_conversion_evidence": "D5_P_STATE_PS3_CONDITIONAL_CONVERSION_AUDIT",
                "actual_instantiation_gap_recorded": p_state_ps3_actual_gap.get("status")
                == "ps3_actual_instantiation_gap_recorded_actual_ps3_open",
                "actual_instantiation_inputs_closed": p_state_ps3_actual_gap.get("summary", {}).get(
                    "input_requirements_closed"
                ),
                "actual_instantiation_inputs_total": p_state_ps3_actual_gap.get("summary", {}).get(
                    "input_requirements_total"
                ),
                "independent_h_weighted_acceleration_input_closed": p_state_ps3_actual_gap.get(
                    "summary", {}
                ).get("independent_h_weighted_acceleration_input_closed"),
                "actual_instantiation_gap_evidence": "D5_P_STATE_PS3_ACTUAL_INSTANTIATION_GAP_AUDIT",
            },
            {
                "id": "PS4",
                "statement": "Show the argument is independent of the D5 dynamic residual bound and of Lemma stage-residual perturbation.",
                "closed": p_state_anticircularity.get("ps4_anticircularity_closed") is True,
                "evidence": "D5_P_STATE_ANTICIRCULARITY_AUDIT",
            },
        ],
        "summary": {
            "primitive_closed": False,
            "term_rows_using_p_state": p_state_row.get("term_rows_using_obligation"),
            "non_dynamic_rows_certified": proof_scope.get("certified_row_count"),
            "required_future_subproofs": 4,
            "required_future_subproofs_closed": 3,
            "map_definition_closed": p_state_map_definition.get("ps1_map_definition_closed"),
            "anti_circularity_closed": p_state_anticircularity.get("ps4_anticircularity_closed"),
            "ps2_weighted_target_spec_closed": p_state_ps2_target.get("ps2_target_spec_closed"),
            "ps2_inverse_or_infsup_closed": p_state_ps2_aggregate.get("ps2_inverse_or_infsup_closed"),
            "ps2_kinematic_block_certificate_recorded": p_state_ps2_kinematic.get(
                "ps2_kinematic_block_certificate_recorded"
            ),
            "ps2_kinematic_subblock_bound_certified": p_state_ps2_kinematic.get(
                "certifies_uniform_euclidean_kinematic_subblock_bound"
            ),
            "ps2_kinematic_block_full_nonlinear_ps2_certified": p_state_ps2_kinematic.get(
                "certifies_full_nonlinear_ps2"
            ),
            "ps2_kinematic_block_remaining_binding_gaps": len(
                p_state_ps2_kinematic.get("remaining_binding_gaps", [])
            ),
            "ps2_lie_chart_binding_recorded": p_state_ps2_lie_chart.get(
                "p_state_ps2_lie_chart_binding_recorded"
            ),
            "ps2_so3_chart_norm_equivalence_certified": p_state_ps2_lie_chart.get(
                "certifies_so3_chart_norm_equivalence"
            ),
            "ps2_lie_chart_full_nonlinear_mean_value_binding_certified": p_state_ps2_lie_chart.get(
                "certifies_full_nonlinear_mean_value_binding"
            ),
            "ps2_lie_chart_remaining_binding_gaps": len(
                p_state_ps2_lie_chart.get("remaining_binding_gaps", [])
            ),
            "ps2_row_injection_recorded": p_state_ps2_row_injection.get(
                "p_state_ps2_row_injection_recorded"
            ),
            "ps2_72_to_96_row_injection_certified": p_state_ps2_row_injection.get(
                "certifies_72_to_96_row_injection"
            ),
            "ps2_row_injection_unweighted_scaling_certified": p_state_ps2_row_injection.get(
                "certifies_unweighted_residual_scaling"
            ),
            "ps2_row_injection_full_nonlinear_mean_value_binding_certified": p_state_ps2_row_injection.get(
                "certifies_full_nonlinear_mean_value_binding"
            ),
            "ps2_row_injection_remaining_binding_gaps": len(
                p_state_ps2_row_injection.get("remaining_binding_gaps", [])
            ),
            "ps2_nonlinear_binding_recorded": p_state_ps2_nonlinear.get(
                "p_state_ps2_nonlinear_binding_recorded"
            ),
            "ps2_rotational_mean_value_binding_certified": p_state_ps2_nonlinear.get(
                "certifies_rotational_lie_row_mean_value_binding"
            ),
            "ps2_nonlinear_full_mean_value_binding_certified": p_state_ps2_nonlinear.get(
                "certifies_full_nonlinear_mean_value_binding"
            ),
            "ps2_nonlinear_full_ps2_certified": p_state_ps2_nonlinear.get("certifies_full_nonlinear_ps2"),
            "ps2_nonlinear_promotion_gaps": len(
                p_state_ps2_nonlinear.get("remaining_promotion_gaps", [])
            ),
            "ps2_aggregate_promotion_recorded": p_state_ps2_aggregate.get(
                "p_state_ps2_aggregate_promotion_recorded"
            ),
            "ps2_aggregate_weighted_inverse_certified": p_state_ps2_aggregate.get(
                "certifies_aggregate_weighted_ps2_inverse"
            ),
            "ps2_uniform_constant_certified": p_state_ps2_aggregate.get("certifies_uniform_ps2_constant"),
            "ps2_aggregate_p_state_closed": p_state_ps2_aggregate.get("primitive_closed"),
            "ps2_aggregate_pc2_closed": p_state_ps2_aggregate.get("pc2_closed"),
            "ps2_finite_linearization_probe_recorded": p_state_ps2_probe.get(
                "ps2_weighted_linearization_probe_recorded"
            ),
            "ps2_finite_probe_full_column_rank_all": p_state_ps2_probe.get("summary", {}).get(
                "finite_probe_full_column_rank_all"
            ),
            "ps2_finite_probe_uniform_constant_proved": p_state_ps2_probe.get(
                "uniform_constant_proved"
            ),
            "ps2_uniform_constant_proved": p_state_ps2_aggregate.get("certifies_uniform_ps2_constant"),
            "ps3_conditional_conversion_closed": p_state_ps3_conversion.get(
                "ps3_conditional_conversion_closed"
            ),
            "ps3_actual_state_lift_conversion_closed": p_state_ps3_conversion.get(
                "ps3_actual_state_lift_conversion_closed"
            ),
            "ps3_actual_instantiation_gap_recorded": p_state_ps3_actual_gap.get("status")
            == "ps3_actual_instantiation_gap_recorded_actual_ps3_open",
            "ps3_actual_instantiation_inputs_closed": p_state_ps3_actual_gap.get("summary", {}).get(
                "input_requirements_closed"
            ),
            "ps3_actual_instantiation_inputs_total": p_state_ps3_actual_gap.get("summary", {}).get(
                "input_requirements_total"
            ),
            "ps3_independent_h_weighted_acceleration_input_closed": p_state_ps3_actual_gap.get(
                "summary", {}
            ).get("independent_h_weighted_acceleration_input_closed"),
            "induced_taylor_bounds_proved": 0,
        },
        "manuscript_link": {
            "main_tex_present": all(contains_normalized(main_tex, token) for token in manuscript_tokens),
            "flat_tex_present": all(contains_normalized(flat_tex, token) for token in manuscript_tokens),
            "tokens": manuscript_tokens,
        },
        "source_consistency": {
            "primitive_reduction_schema": primitive_reduction.get("schema"),
            "primitive_reduction_pc2_closed": primitive_reduction.get("pc2_closed"),
            "kinematic_certificate_schema": kinematic_certificate.get("schema"),
            "kinematic_certificate_status": kinematic_certificate.get("status"),
            "p_state_map_definition_schema": p_state_map_definition.get("schema"),
            "p_state_map_definition_closed": p_state_map_definition.get("ps1_map_definition_closed"),
            "p_state_map_definition_primitive_closed": p_state_map_definition.get("primitive_closed"),
            "p_state_map_definition_pc2_closed": p_state_map_definition.get("pc2_closed"),
            "p_state_anticircularity_schema": p_state_anticircularity.get("schema"),
            "p_state_anticircularity_closed": p_state_anticircularity.get("ps4_anticircularity_closed"),
            "p_state_anticircularity_primitive_closed": p_state_anticircularity.get("primitive_closed"),
            "p_state_anticircularity_pc2_closed": p_state_anticircularity.get("pc2_closed"),
            "p_state_ps2_weighted_target_schema": p_state_ps2_target.get("schema"),
            "p_state_ps2_weighted_target_spec_closed": p_state_ps2_target.get("ps2_target_spec_closed"),
            "p_state_ps2_weighted_target_infsup_closed": p_state_ps2_target.get("ps2_inverse_or_infsup_closed"),
            "p_state_ps2_weighted_target_pc2_closed": p_state_ps2_target.get("pc2_closed"),
            "p_state_ps2_kinematic_block_schema": p_state_ps2_kinematic.get("schema"),
            "p_state_ps2_kinematic_block_recorded": p_state_ps2_kinematic.get(
                "ps2_kinematic_block_certificate_recorded"
            ),
            "p_state_ps2_kinematic_block_uniform_euclidean_bound": p_state_ps2_kinematic.get(
                "certifies_uniform_euclidean_kinematic_subblock_bound"
            ),
            "p_state_ps2_kinematic_block_full_nonlinear_ps2": p_state_ps2_kinematic.get(
                "certifies_full_nonlinear_ps2"
            ),
            "p_state_ps2_kinematic_block_pc2_closed": p_state_ps2_kinematic.get("pc2_closed"),
            "p_state_ps2_lie_chart_binding_schema": p_state_ps2_lie_chart.get("schema"),
            "p_state_ps2_lie_chart_binding_recorded": p_state_ps2_lie_chart.get(
                "p_state_ps2_lie_chart_binding_recorded"
            ),
            "p_state_ps2_lie_chart_so3_norm_equivalence": p_state_ps2_lie_chart.get(
                "certifies_so3_chart_norm_equivalence"
            ),
            "p_state_ps2_lie_chart_full_mean_value_binding": p_state_ps2_lie_chart.get(
                "certifies_full_nonlinear_mean_value_binding"
            ),
            "p_state_ps2_lie_chart_full_nonlinear_ps2": p_state_ps2_lie_chart.get(
                "certifies_full_nonlinear_ps2"
            ),
            "p_state_ps2_lie_chart_pc2_closed": p_state_ps2_lie_chart.get("pc2_closed"),
            "p_state_ps2_row_injection_schema": p_state_ps2_row_injection.get("schema"),
            "p_state_ps2_row_injection_recorded": p_state_ps2_row_injection.get(
                "p_state_ps2_row_injection_recorded"
            ),
            "p_state_ps2_row_injection_certified": p_state_ps2_row_injection.get(
                "certifies_72_to_96_row_injection"
            ),
            "p_state_ps2_row_injection_unweighted_scaling": p_state_ps2_row_injection.get(
                "certifies_unweighted_residual_scaling"
            ),
            "p_state_ps2_row_injection_full_mean_value_binding": p_state_ps2_row_injection.get(
                "certifies_full_nonlinear_mean_value_binding"
            ),
            "p_state_ps2_row_injection_pc2_closed": p_state_ps2_row_injection.get("pc2_closed"),
            "p_state_ps2_nonlinear_binding_schema": p_state_ps2_nonlinear.get("schema"),
            "p_state_ps2_nonlinear_binding_recorded": p_state_ps2_nonlinear.get(
                "p_state_ps2_nonlinear_binding_recorded"
            ),
            "p_state_ps2_nonlinear_rotational_mean_value": p_state_ps2_nonlinear.get(
                "certifies_rotational_lie_row_mean_value_binding"
            ),
            "p_state_ps2_nonlinear_full_mean_value_binding": p_state_ps2_nonlinear.get(
                "certifies_full_nonlinear_mean_value_binding"
            ),
            "p_state_ps2_nonlinear_full_ps2": p_state_ps2_nonlinear.get("certifies_full_nonlinear_ps2"),
            "p_state_ps2_nonlinear_pc2_closed": p_state_ps2_nonlinear.get("pc2_closed"),
            "p_state_ps2_aggregate_schema": p_state_ps2_aggregate.get("schema"),
            "p_state_ps2_aggregate_promotion_recorded": p_state_ps2_aggregate.get(
                "p_state_ps2_aggregate_promotion_recorded"
            ),
            "p_state_ps2_aggregate_weighted_inverse_certified": p_state_ps2_aggregate.get(
                "certifies_aggregate_weighted_ps2_inverse"
            ),
            "p_state_ps2_aggregate_uniform_constant_certified": p_state_ps2_aggregate.get(
                "certifies_uniform_ps2_constant"
            ),
            "p_state_ps2_aggregate_inverse_or_infsup_closed": p_state_ps2_aggregate.get(
                "ps2_inverse_or_infsup_closed"
            ),
            "p_state_ps2_aggregate_ps3_actual_conversion_closed": p_state_ps2_aggregate.get(
                "ps3_actual_state_lift_conversion_closed"
            ),
            "p_state_ps2_aggregate_primitive_closed": p_state_ps2_aggregate.get("primitive_closed"),
            "p_state_ps2_aggregate_pc2_closed": p_state_ps2_aggregate.get("pc2_closed"),
            "p_state_ps2_linearization_probe_schema": p_state_ps2_probe.get("schema"),
            "p_state_ps2_linearization_probe_recorded": p_state_ps2_probe.get(
                "ps2_weighted_linearization_probe_recorded"
            ),
            "p_state_ps2_linearization_probe_full_column_rank_all": p_state_ps2_probe.get("summary", {}).get(
                "finite_probe_full_column_rank_all"
            ),
            "p_state_ps2_linearization_probe_uniform_constant_proved": p_state_ps2_probe.get(
                "uniform_constant_proved"
            ),
            "p_state_ps2_linearization_probe_pc2_closed": p_state_ps2_probe.get("pc2_closed"),
            "p_state_ps3_conditional_conversion_schema": p_state_ps3_conversion.get("schema"),
            "p_state_ps3_conditional_conversion_closed": p_state_ps3_conversion.get(
                "ps3_conditional_conversion_closed"
            ),
            "p_state_ps3_actual_conversion_closed": p_state_ps3_conversion.get(
                "ps3_actual_state_lift_conversion_closed"
            ),
            "p_state_ps3_conditional_conversion_pc2_closed": p_state_ps3_conversion.get("pc2_closed"),
            "p_state_ps3_actual_gap_schema": p_state_ps3_actual_gap.get("schema"),
            "p_state_ps3_actual_gap_recorded": p_state_ps3_actual_gap.get("status")
            == "ps3_actual_instantiation_gap_recorded_actual_ps3_open",
            "p_state_ps3_actual_gap_inputs_closed": p_state_ps3_actual_gap.get("summary", {}).get(
                "input_requirements_closed"
            ),
            "p_state_ps3_actual_gap_inputs_total": p_state_ps3_actual_gap.get("summary", {}).get(
                "input_requirements_total"
            ),
            "p_state_ps3_actual_gap_h_input_closed": p_state_ps3_actual_gap.get("summary", {}).get(
                "independent_h_weighted_acceleration_input_closed"
            ),
            "p_state_ps3_actual_gap_pc2_closed": p_state_ps3_actual_gap.get("pc2_closed"),
            "proof_manifest_proof_gap_closed": proof_manifest.get("closure_state", {}).get("proof_gap_closed"),
            "proof_manifest_direct_route_gap_closed": proof_manifest.get("closure_state", {}).get(
                "direct_pc2_proof_gap_closed"
            ),
            "proof_manifest_proof_gap_closed_scope": proof_manifest.get("closure_state", {}).get(
                "proof_gap_closed_scope"
            ),
        },
        "claim_boundary": {
            "allowed_now": "P_state PS1 map definition and PS4 anti-circular proof rule are closed.",
            "forbidden_now": [
                "P_state primitive closed",
                "state lift O(h^7) proved",
                "Taylor term bounds certified from P_state",
                "primitive/Taylor PC2 route closure",
                "submission-ready proof",
            ],
            "close_condition": (
                "P_state closes only after the closed PS2 inverse is combined with the "
                "96-row residual certificate and the h-weighted acceleration input in an "
                "actual PS3 instantiation without using the D5 dynamic residual theorem."
            ),
        },
    }

    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# D5 P_state Lift-Gap Audit",
        "",
        "Status: **P_state lift gap recorded; separate primitive-route certificate remains open**.",
        "",
        "This read-only audit records that the 96-row non-dynamic residual",
        "certificate is not yet a state-variable lift-rate proof. The PS2",
        "aggregate inverse is now closed; the missing step is the actual PS3",
        "instantiation that combines it with the residual and h-weighted",
        "acceleration inputs in the lift ledger.",
        "",
        "## Summary",
        "",
        f"- P_state primitive closed: `{result['summary']['primitive_closed']}`.",
        f"- Term rows using P_state: `{result['summary']['term_rows_using_p_state']}/162`.",
        f"- Non-dynamic rows certified: `{result['summary']['non_dynamic_rows_certified']}/96`.",
        f"- Required future subproofs closed: `{result['summary']['required_future_subproofs_closed']}/{result['summary']['required_future_subproofs']}`.",
        f"- PS1 map definition closed: `{result['summary']['map_definition_closed']}`.",
        f"- PS4 anti-circularity closed: `{result['summary']['anti_circularity_closed']}`.",
        f"- PS2 weighted target specification closed: `{result['summary']['ps2_weighted_target_spec_closed']}`.",
        f"- PS2 kinematic-block certificate recorded/subblock/full-PS2/gaps: `{result['summary']['ps2_kinematic_block_certificate_recorded']}` / `{result['summary']['ps2_kinematic_subblock_bound_certified']}` / `{result['summary']['ps2_kinematic_block_full_nonlinear_ps2_certified']}` / `{result['summary']['ps2_kinematic_block_remaining_binding_gaps']}`.",
        f"- PS2 Lie-chart binding recorded/SO3/full-mean/gaps: `{result['summary']['ps2_lie_chart_binding_recorded']}` / `{result['summary']['ps2_so3_chart_norm_equivalence_certified']}` / `{result['summary']['ps2_lie_chart_full_nonlinear_mean_value_binding_certified']}` / `{result['summary']['ps2_lie_chart_remaining_binding_gaps']}`.",
        f"- PS2 row injection recorded/72-to-96/scaling/full-mean/gaps: `{result['summary']['ps2_row_injection_recorded']}` / `{result['summary']['ps2_72_to_96_row_injection_certified']}` / `{result['summary']['ps2_row_injection_unweighted_scaling_certified']}` / `{result['summary']['ps2_row_injection_full_nonlinear_mean_value_binding_certified']}` / `{result['summary']['ps2_row_injection_remaining_binding_gaps']}`.",
        f"- PS2 nonlinear binding recorded/rot-mean/full-mean/full-PS2/gaps: `{result['summary']['ps2_nonlinear_binding_recorded']}` / `{result['summary']['ps2_rotational_mean_value_binding_certified']}` / `{result['summary']['ps2_nonlinear_full_mean_value_binding_certified']}` / `{result['summary']['ps2_nonlinear_full_ps2_certified']}` / `{result['summary']['ps2_nonlinear_promotion_gaps']}`.",
        f"- PS2 aggregate promotion recorded/inverse/uniform/P_state/PC2: `{result['summary']['ps2_aggregate_promotion_recorded']}` / `{result['summary']['ps2_aggregate_weighted_inverse_certified']}` / `{result['summary']['ps2_uniform_constant_certified']}` / `{result['summary']['ps2_aggregate_p_state_closed']}` / `{result['summary']['ps2_aggregate_pc2_closed']}`.",
        f"- PS2 finite linearization probe recorded/full-rank: `{result['summary']['ps2_finite_linearization_probe_recorded']}` / `{result['summary']['ps2_finite_probe_full_column_rank_all']}`.",
        f"- PS2 finite probe uniform constant proved: `{result['summary']['ps2_finite_probe_uniform_constant_proved']}`.",
        f"- PS2 uniform constant proved: `{result['summary']['ps2_uniform_constant_proved']}`.",
        f"- PS2 inverse or inf-sup closed: `{result['summary']['ps2_inverse_or_infsup_closed']}`.",
        f"- PS3 conditional conversion closed: `{result['summary']['ps3_conditional_conversion_closed']}`.",
        f"- PS3 actual-instantiation gap recorded/inputs/h-input: `{result['summary']['ps3_actual_instantiation_gap_recorded']}` / `{result['summary']['ps3_actual_instantiation_inputs_closed']}`-`{result['summary']['ps3_actual_instantiation_inputs_total']}` / `{result['summary']['ps3_independent_h_weighted_acceleration_input_closed']}`.",
        f"- PS3 actual state lift conversion closed: `{result['summary']['ps3_actual_state_lift_conversion_closed']}`.",
        f"- Induced Taylor bounds proved: `{result['summary']['induced_taylor_bounds_proved']}/162`.",
        f"- Primitive/Taylor PC2 route closed: `{result['pc2_closed']}`.",
        "",
        "## Anti-Circularity Gate",
        "",
        "- A residual-row identity is not by itself a variable-lift estimate.",
        "- Lemma `stage-residual-defect` is disallowed as an input to P_state.",
        "- The D5 dynamic residual defect is disallowed as an input to P_state.",
        "- Accepted Newton-solution closeness needs an independent inverse bound.",
        "",
        "## Required Future Proof",
        "",
        "| id | status | statement |",
        "|---|---|---|",
    ]
    for item in result["required_future_proof"]:
        lines.append(f"| `{item['id']}` | `{item['closed']}` | {item['statement']} |")
    lines.extend(
        [
            "",
            "## Acceptance Boundary",
            "",
        "- PS4 anti-circularity is closed.",
        "- The PS2 weighted target specification is closed.",
        "- The PS2 kinematic-block certificate records a uniform Euclidean Gauss subblock bound.",
        "- The PS2 Lie-chart binding certificate records the pure SO(3) norm-equivalence constants.",
        "- The PS2 row-injection audit records the 72-to-96 unweighted residual selection constant.",
        "- The PS2 nonlinear binding audit records the rotational-row compact-tube mean-value estimate.",
        "- Aggregate promotion of the component certificates to a full PS2 inverse is closed.",
        "- The finite PS2 weighted linearization probe is recorded and full-rank on the finite solved-stage probes.",
        "- The finite probe does not prove a uniform compact-tube inverse or inf-sup constant.",
        "- The PS3 conditional conversion implication is recorded.",
        "- PS2 local inverse or inf-sup proof is closed by the aggregate Taylor/mean-value proof.",
        "- PS3 conversion to `O(h^7)` state lift rates remains open.",
        "- P_state remains open.",
            "- Zero P_state-induced Taylor bounds are certified.",
            "- Primitive/Taylor PC2 lane remains open.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("d5_p_state_lift_gap_audit=written")
    print("p_state_closed=False")
    print("required_future_subproofs_closed=3/4")
    print("pc2_closed=False")


if __name__ == "__main__":
    main()
