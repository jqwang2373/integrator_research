#!/usr/bin/env python3
"""Validate the D5 P_state lift-gap audit."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
AUDIT_JSON = PAPER / "D5_P_STATE_LIFT_GAP_AUDIT.json"
AUDIT_MD = PAPER / "D5_P_STATE_LIFT_GAP_AUDIT.md"


class Checks:
    def __init__(self) -> None:
        self.errors: list[str] = []

    def check(self, condition: bool, message: str) -> None:
        if not condition:
            self.errors.append(message)


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def main() -> int:
    checks = Checks()
    try:
        audit = read_json(AUDIT_JSON)
        audit_md = AUDIT_MD.read_text(encoding="utf-8", errors="replace")
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
    except Exception as exc:  # noqa: BLE001
        print(f"D5 P_state lift-gap audit validation: FAIL\n- {exc}")
        return 1

    summary = audit.get("summary", {})
    source = audit.get("source_consistency", {})
    anti = audit.get("anti_circularity_gate", {})
    manuscript = audit.get("manuscript_link", {})

    checks.check(audit.get("schema") == "d5-p-state-lift-gap-audit-v1", "schema changed")
    checks.check(audit.get("status") == "p_state_lift_gap_recorded_pc2_open", "status changed")
    checks.check(audit.get("read_only") is True, "audit must be read-only")
    checks.check(audit.get("run_v047_invoked") is False, "run_v047 must not be invoked")
    checks.check(audit.get("submission_ready") is False, "submission readiness overclaimed")
    checks.check(audit.get("pc2_closed") is False, "PC2 unexpectedly closed")
    checks.check(audit.get("proof_gap_closed") is False, "proof gap unexpectedly closed")
    checks.check(audit.get("primitive_id") == "P_state_lift", "primitive id changed")
    checks.check(audit.get("plan_id") == "P_state", "plan id changed")
    checks.check(audit.get("primitive_closed") is False, "P_state unexpectedly closed")
    checks.check(audit.get("certifies_dynamic_row_defect") is False, "dynamic defect overclaimed")
    checks.check(audit.get("certifies_induced_taylor_bounds") is False, "Taylor bounds overclaimed")
    checks.check(summary.get("primitive_closed") is False, "summary overclaims P_state closure")
    checks.check(summary.get("term_rows_using_p_state") == 126, "P_state term-row count changed")
    checks.check(summary.get("non_dynamic_rows_certified") == 96, "non-dynamic row count changed")
    checks.check(summary.get("required_future_subproofs") == 4, "future subproof count changed")
    checks.check(summary.get("required_future_subproofs_closed") == 3, "P_state PS1/PS2/PS4 closure count missing")
    checks.check(summary.get("map_definition_closed") is True, "P_state map definition not linked as closed")
    checks.check(summary.get("anti_circularity_closed") is True, "P_state anti-circularity not linked as closed")
    checks.check(summary.get("ps2_weighted_target_spec_closed") is True, "P_state PS2 weighted target spec not linked as closed")
    checks.check(summary.get("ps2_inverse_or_infsup_closed") is True, "P_state PS2 inverse not closed by aggregate proof")
    checks.check(summary.get("ps2_kinematic_block_certificate_recorded") is True, "P_state PS2 kinematic block not recorded")
    checks.check(
        summary.get("ps2_kinematic_subblock_bound_certified") is True,
        "P_state PS2 kinematic subblock bound not certified",
    )
    checks.check(
        summary.get("ps2_kinematic_block_full_nonlinear_ps2_certified") is False,
        "P_state PS2 kinematic block overclaims full nonlinear PS2",
    )
    checks.check(
        summary.get("ps2_kinematic_block_remaining_binding_gaps") == 3,
        "P_state PS2 kinematic block binding gap count changed",
    )
    checks.check(summary.get("ps2_lie_chart_binding_recorded") is True, "P_state PS2 Lie-chart binding not recorded")
    checks.check(
        summary.get("ps2_so3_chart_norm_equivalence_certified") is True,
        "P_state PS2 SO(3) chart norm equivalence not certified",
    )
    checks.check(
        summary.get("ps2_lie_chart_full_nonlinear_mean_value_binding_certified") is False,
        "P_state PS2 Lie-chart audit overclaims nonlinear mean-value binding",
    )
    checks.check(
        summary.get("ps2_lie_chart_remaining_binding_gaps") == 2,
        "P_state PS2 Lie-chart remaining binding gap count changed",
    )
    checks.check(summary.get("ps2_row_injection_recorded") is True, "P_state PS2 row injection not recorded")
    checks.check(
        summary.get("ps2_72_to_96_row_injection_certified") is True,
        "P_state PS2 72-to-96 row injection not certified",
    )
    checks.check(
        summary.get("ps2_row_injection_unweighted_scaling_certified") is True,
        "P_state PS2 unweighted row scaling not certified",
    )
    checks.check(
        summary.get("ps2_row_injection_full_nonlinear_mean_value_binding_certified") is False,
        "P_state PS2 row injection overclaims mean-value binding",
    )
    checks.check(
        summary.get("ps2_row_injection_remaining_binding_gaps") == 1,
        "P_state PS2 row injection remaining binding gap count changed",
    )
    checks.check(summary.get("ps2_nonlinear_binding_recorded") is True, "P_state PS2 nonlinear binding not recorded")
    checks.check(
        summary.get("ps2_rotational_mean_value_binding_certified") is True,
        "P_state PS2 rotational mean-value binding not certified",
    )
    checks.check(
        summary.get("ps2_nonlinear_full_mean_value_binding_certified") is True,
        "P_state PS2 nonlinear mean-value binding not certified",
    )
    checks.check(
        summary.get("ps2_nonlinear_full_ps2_certified") is False,
        "P_state PS2 nonlinear binding overclaims full PS2",
    )
    checks.check(
        summary.get("ps2_nonlinear_promotion_gaps") == 1,
        "P_state PS2 nonlinear binding promotion gap count changed",
    )
    checks.check(summary.get("ps2_aggregate_promotion_recorded") is True, "P_state PS2 aggregate promotion not recorded")
    checks.check(
        summary.get("ps2_aggregate_weighted_inverse_certified") is True,
        "P_state PS2 aggregate inverse not certified",
    )
    checks.check(summary.get("ps2_uniform_constant_certified") is True, "P_state PS2 aggregate uniform constant missing")
    checks.check(summary.get("ps2_aggregate_p_state_closed") is False, "P_state aggregate audit closes primitive")
    checks.check(summary.get("ps2_aggregate_pc2_closed") is False, "P_state aggregate audit closes PC2")
    checks.check(summary.get("ps2_finite_linearization_probe_recorded") is True, "P_state PS2 finite probe not recorded")
    checks.check(summary.get("ps2_finite_probe_full_column_rank_all") is True, "P_state PS2 finite probe not full rank")
    checks.check(
        summary.get("ps2_finite_probe_uniform_constant_proved") is False,
        "P_state PS2 finite probe unexpectedly proves uniform constant",
    )
    checks.check(summary.get("ps2_uniform_constant_proved") is True, "P_state PS2 uniform constant not proved by aggregate")
    checks.check(summary.get("ps3_conditional_conversion_closed") is True, "P_state PS3 conditional conversion not linked as closed")
    checks.check(summary.get("ps3_actual_state_lift_conversion_closed") is False, "P_state PS3 actual conversion unexpectedly closed")
    checks.check(summary.get("induced_taylor_bounds_proved") == 0, "P_state unexpectedly proves Taylor bounds")
    checks.check(anti.get("residual_row_identity_is_not_variable_lift_estimate") is True, "row/state gap missing")
    checks.check(anti.get("stage_residual_perturbation_lemma_disallowed_as_input") is True, "stage lemma not barred")
    checks.check(anti.get("dynamic_residual_defect_disallowed_as_input") is True, "dynamic residual not barred")
    checks.check(
        anti.get("accepted_newton_solution_closeness_disallowed_without_independent_inverse") is True,
        "Newton closeness anti-circularity gate missing",
    )
    checks.check(manuscript.get("main_tex_present") is True, "main TeX P_state gap text missing")
    checks.check(manuscript.get("flat_tex_present") is True, "flat TeX P_state gap text missing")
    checks.check(source.get("primitive_reduction_pc2_closed") is False, "primitive reduction closes PC2")
    checks.check(
        source.get("kinematic_certificate_schema") == "kinematic-row-defect-certificate-v1",
        "kinematic certificate schema not linked",
    )
    checks.check(
        source.get("p_state_map_definition_schema") == "d5-p-state-map-definition-audit-v1",
        "P_state map-definition schema not linked",
    )
    checks.check(
        source.get("p_state_map_definition_closed") is True
        and p_state_map_definition.get("ps1_map_definition_closed") is True,
        "P_state map definition not closed",
    )
    checks.check(
        source.get("p_state_map_definition_primitive_closed") is False
        and p_state_map_definition.get("primitive_closed") is False,
        "P_state map definition unexpectedly closes primitive",
    )
    checks.check(
        source.get("p_state_map_definition_pc2_closed") is False
        and p_state_map_definition.get("pc2_closed") is False,
        "P_state map definition unexpectedly closes PC2",
    )
    checks.check(
        source.get("p_state_anticircularity_schema") == "d5-p-state-anticircularity-audit-v1",
        "P_state anti-circularity schema not linked",
    )
    checks.check(
        source.get("p_state_anticircularity_closed") is True
        and p_state_anticircularity.get("ps4_anticircularity_closed") is True,
        "P_state anti-circularity not closed",
    )
    checks.check(
        source.get("p_state_anticircularity_primitive_closed") is False
        and p_state_anticircularity.get("primitive_closed") is False,
        "P_state anti-circularity unexpectedly closes primitive",
    )
    checks.check(
        source.get("p_state_anticircularity_pc2_closed") is False
        and p_state_anticircularity.get("pc2_closed") is False,
        "P_state anti-circularity unexpectedly closes PC2",
    )
    checks.check(
        source.get("p_state_ps2_weighted_target_schema") == "d5-p-state-ps2-weighted-target-audit-v1",
        "P_state PS2 weighted target schema not linked",
    )
    checks.check(
        source.get("p_state_ps2_weighted_target_spec_closed") is True
        and p_state_ps2_target.get("ps2_target_spec_closed") is True,
        "P_state PS2 weighted target spec not closed",
    )
    checks.check(
        source.get("p_state_ps2_weighted_target_infsup_closed") is False
        and p_state_ps2_target.get("ps2_inverse_or_infsup_closed") is False,
        "P_state PS2 weighted target unexpectedly closes inf-sup",
    )
    checks.check(
        source.get("p_state_ps2_weighted_target_pc2_closed") is False
        and p_state_ps2_target.get("pc2_closed") is False,
        "P_state PS2 weighted target unexpectedly closes PC2",
    )
    checks.check(
        source.get("p_state_ps2_kinematic_block_schema")
        == "d5-p-state-ps2-kinematic-block-certificate-v1",
        "P_state PS2 kinematic-block schema not linked",
    )
    checks.check(
        source.get("p_state_ps2_kinematic_block_recorded") is True
        and p_state_ps2_kinematic.get("ps2_kinematic_block_certificate_recorded") is True,
        "P_state PS2 kinematic-block certificate not linked",
    )
    checks.check(
        source.get("p_state_ps2_kinematic_block_uniform_euclidean_bound") is True
        and p_state_ps2_kinematic.get("certifies_uniform_euclidean_kinematic_subblock_bound") is True,
        "P_state PS2 kinematic-block Euclidean bound not linked",
    )
    checks.check(
        source.get("p_state_ps2_kinematic_block_full_nonlinear_ps2") is False
        and p_state_ps2_kinematic.get("certifies_full_nonlinear_ps2") is False,
        "P_state PS2 kinematic-block overclaims nonlinear PS2",
    )
    checks.check(
        source.get("p_state_ps2_kinematic_block_pc2_closed") is False
        and p_state_ps2_kinematic.get("pc2_closed") is False,
        "P_state PS2 kinematic-block unexpectedly closes PC2",
    )
    checks.check(
        source.get("p_state_ps2_lie_chart_binding_schema")
        == "d5-p-state-ps2-lie-chart-binding-audit-v1",
        "P_state PS2 Lie-chart binding schema not linked",
    )
    checks.check(
        source.get("p_state_ps2_lie_chart_binding_recorded") is True
        and p_state_ps2_lie_chart.get("p_state_ps2_lie_chart_binding_recorded") is True,
        "P_state PS2 Lie-chart binding not linked",
    )
    checks.check(
        source.get("p_state_ps2_lie_chart_so3_norm_equivalence") is True
        and p_state_ps2_lie_chart.get("certifies_so3_chart_norm_equivalence") is True,
        "P_state PS2 SO(3) chart norm equivalence not linked",
    )
    checks.check(
        source.get("p_state_ps2_lie_chart_full_mean_value_binding") is False
        and p_state_ps2_lie_chart.get("certifies_full_nonlinear_mean_value_binding") is False,
        "P_state PS2 Lie-chart overclaims mean-value binding",
    )
    checks.check(
        source.get("p_state_ps2_lie_chart_full_nonlinear_ps2") is False
        and p_state_ps2_lie_chart.get("certifies_full_nonlinear_ps2") is False,
        "P_state PS2 Lie-chart unexpectedly closes nonlinear PS2",
    )
    checks.check(
        source.get("p_state_ps2_lie_chart_pc2_closed") is False
        and p_state_ps2_lie_chart.get("pc2_closed") is False,
        "P_state PS2 Lie-chart unexpectedly closes PC2",
    )
    checks.check(
        source.get("p_state_ps2_row_injection_schema")
        == "d5-p-state-ps2-row-injection-audit-v1",
        "P_state PS2 row-injection schema not linked",
    )
    checks.check(
        source.get("p_state_ps2_row_injection_recorded") is True
        and p_state_ps2_row_injection.get("p_state_ps2_row_injection_recorded") is True,
        "P_state PS2 row injection not linked",
    )
    checks.check(
        source.get("p_state_ps2_row_injection_certified") is True
        and p_state_ps2_row_injection.get("certifies_72_to_96_row_injection") is True,
        "P_state PS2 row injection certificate not linked",
    )
    checks.check(
        source.get("p_state_ps2_row_injection_unweighted_scaling") is True
        and p_state_ps2_row_injection.get("certifies_unweighted_residual_scaling") is True,
        "P_state PS2 unweighted scaling not linked",
    )
    checks.check(
        source.get("p_state_ps2_row_injection_full_mean_value_binding") is False
        and p_state_ps2_row_injection.get("certifies_full_nonlinear_mean_value_binding") is False,
        "P_state PS2 row injection overclaims mean-value binding",
    )
    checks.check(
        source.get("p_state_ps2_row_injection_pc2_closed") is False
        and p_state_ps2_row_injection.get("pc2_closed") is False,
        "P_state PS2 row injection unexpectedly closes PC2",
    )
    checks.check(
        source.get("p_state_ps2_nonlinear_binding_schema")
        == "d5-p-state-ps2-nonlinear-binding-audit-v1",
        "P_state PS2 nonlinear binding schema not linked",
    )
    checks.check(
        source.get("p_state_ps2_nonlinear_binding_recorded") is True
        and p_state_ps2_nonlinear.get("p_state_ps2_nonlinear_binding_recorded") is True,
        "P_state PS2 nonlinear binding not linked",
    )
    checks.check(
        source.get("p_state_ps2_nonlinear_rotational_mean_value") is True
        and p_state_ps2_nonlinear.get("certifies_rotational_lie_row_mean_value_binding") is True,
        "P_state PS2 rotational mean-value binding not linked",
    )
    checks.check(
        source.get("p_state_ps2_nonlinear_full_mean_value_binding") is True
        and p_state_ps2_nonlinear.get("certifies_full_nonlinear_mean_value_binding") is True,
        "P_state PS2 nonlinear mean-value binding not linked",
    )
    checks.check(
        source.get("p_state_ps2_nonlinear_full_ps2") is False
        and p_state_ps2_nonlinear.get("certifies_full_nonlinear_ps2") is False,
        "P_state PS2 nonlinear binding overclaims full PS2",
    )
    checks.check(
        source.get("p_state_ps2_nonlinear_pc2_closed") is False
        and p_state_ps2_nonlinear.get("pc2_closed") is False,
        "P_state PS2 nonlinear binding unexpectedly closes PC2",
    )
    checks.check(
        source.get("p_state_ps2_aggregate_schema")
        == "d5-p-state-ps2-aggregate-promotion-audit-v1"
        and p_state_ps2_aggregate.get("schema") == "d5-p-state-ps2-aggregate-promotion-audit-v1",
        "P_state PS2 aggregate schema not linked",
    )
    checks.check(
        source.get("p_state_ps2_aggregate_promotion_recorded") is True
        and p_state_ps2_aggregate.get("p_state_ps2_aggregate_promotion_recorded") is True,
        "P_state PS2 aggregate promotion not linked",
    )
    checks.check(
        source.get("p_state_ps2_aggregate_weighted_inverse_certified") is True
        and p_state_ps2_aggregate.get("certifies_aggregate_weighted_ps2_inverse") is True,
        "P_state PS2 aggregate inverse not linked",
    )
    checks.check(
        source.get("p_state_ps2_aggregate_uniform_constant_certified") is True
        and p_state_ps2_aggregate.get("certifies_uniform_ps2_constant") is True,
        "P_state PS2 aggregate uniform constant not linked",
    )
    checks.check(
        source.get("p_state_ps2_aggregate_inverse_or_infsup_closed") is True
        and p_state_ps2_aggregate.get("ps2_inverse_or_infsup_closed") is True,
        "P_state PS2 aggregate inf-sup closure not linked",
    )
    checks.check(
        source.get("p_state_ps2_aggregate_ps3_actual_conversion_closed") is False
        and p_state_ps2_aggregate.get("ps3_actual_state_lift_conversion_closed") is False,
        "P_state PS2 aggregate unexpectedly closes PS3",
    )
    checks.check(
        source.get("p_state_ps2_aggregate_primitive_closed") is False
        and p_state_ps2_aggregate.get("primitive_closed") is False,
        "P_state PS2 aggregate unexpectedly closes primitive",
    )
    checks.check(
        source.get("p_state_ps2_aggregate_pc2_closed") is False
        and p_state_ps2_aggregate.get("pc2_closed") is False,
        "P_state PS2 aggregate unexpectedly closes PC2",
    )
    checks.check(
        source.get("p_state_ps2_linearization_probe_schema")
        == "d5-p-state-ps2-linearization-probe-v1",
        "P_state PS2 linearization probe schema not linked",
    )
    checks.check(
        source.get("p_state_ps2_linearization_probe_recorded") is True
        and p_state_ps2_probe.get("ps2_weighted_linearization_probe_recorded") is True,
        "P_state PS2 finite probe not linked",
    )
    checks.check(
        source.get("p_state_ps2_linearization_probe_full_column_rank_all") is True
        and p_state_ps2_probe.get("summary", {}).get("finite_probe_full_column_rank_all") is True,
        "P_state PS2 finite probe rank not linked",
    )
    checks.check(
        source.get("p_state_ps2_linearization_probe_uniform_constant_proved") is False
        and p_state_ps2_probe.get("uniform_constant_proved") is False,
        "P_state PS2 finite probe unexpectedly proves uniform constant",
    )
    checks.check(
        source.get("p_state_ps2_linearization_probe_pc2_closed") is False
        and p_state_ps2_probe.get("pc2_closed") is False,
        "P_state PS2 finite probe unexpectedly closes PC2",
    )
    checks.check(
        source.get("p_state_ps3_conditional_conversion_schema")
        == "d5-p-state-ps3-conditional-conversion-audit-v1",
        "P_state PS3 conditional conversion schema not linked",
    )
    checks.check(
        source.get("p_state_ps3_conditional_conversion_closed") is True
        and p_state_ps3_conversion.get("ps3_conditional_conversion_closed") is True,
        "P_state PS3 conditional conversion not linked",
    )
    checks.check(
        source.get("p_state_ps3_actual_conversion_closed") is False
        and p_state_ps3_conversion.get("ps3_actual_state_lift_conversion_closed") is False,
        "P_state PS3 actual conversion unexpectedly closed",
    )
    checks.check(
        source.get("p_state_ps3_conditional_conversion_pc2_closed") is False
        and p_state_ps3_conversion.get("pc2_closed") is False,
        "P_state PS3 conditional conversion unexpectedly closes PC2",
    )
    checks.check(
        kinematic_certificate.get("proof_scope", {}).get("certified_row_count") == 96,
        "kinematic certificate row count changed",
    )
    checks.check(
        source.get("proof_manifest_proof_gap_closed") is True
        and proof_manifest.get("closure_state", {}).get("pc2_closed_by_direct_substitution") is True,
        "proof manifest direct-substitution closure not reflected",
    )
    checks.check(
        proof_manifest.get("closure_state", {}).get("primitive_lift_route_closed") is False,
        "proof manifest unexpectedly closes primitive lift route",
    )
    checks.check(primitive_reduction.get("pc2_closed") is False, "primitive reduction unexpectedly closes PC2")
    checks.check(len(audit.get("required_future_proof", [])) == 4, "future proof list changed")
    closed_map = {item.get("id"): item.get("closed") for item in audit.get("required_future_proof", [])}
    checks.check(closed_map == {"PS1": True, "PS2": True, "PS3": False, "PS4": True}, "P_state subproof status map changed")
    ps2_row = next((item for item in audit.get("required_future_proof", []) if item.get("id") == "PS2"), {})
    checks.check(ps2_row.get("target_spec_closed") is True, "PS2 target spec not linked")
    checks.check(
        ps2_row.get("target_spec_evidence") == "D5_P_STATE_PS2_WEIGHTED_TARGET_AUDIT",
        "PS2 target spec evidence changed",
    )
    checks.check(ps2_row.get("finite_linearization_probe_recorded") is True, "PS2 finite probe not linked")
    checks.check(ps2_row.get("kinematic_block_certificate_recorded") is True, "PS2 kinematic block not linked")
    checks.check(
        ps2_row.get("uniform_euclidean_kinematic_subblock_bound_certified") is True,
        "PS2 kinematic subblock bound not linked",
    )
    checks.check(ps2_row.get("full_nonlinear_ps2_certified") is False, "PS2 kinematic block overclaims full PS2")
    checks.check(
        ps2_row.get("kinematic_block_evidence") == "D5_P_STATE_PS2_KINEMATIC_BLOCK_CERTIFICATE",
        "PS2 kinematic block evidence changed",
    )
    checks.check(ps2_row.get("lie_chart_binding_recorded") is True, "PS2 Lie-chart binding not linked")
    checks.check(
        ps2_row.get("so3_chart_norm_equivalence_certified") is True,
        "PS2 SO(3) chart norm equivalence not linked",
    )
    checks.check(
        ps2_row.get("full_nonlinear_mean_value_binding_certified") is False,
        "PS2 Lie-chart audit unexpectedly closes mean-value binding",
    )
    checks.check(
        ps2_row.get("lie_chart_binding_evidence") == "D5_P_STATE_PS2_LIE_CHART_BINDING_AUDIT",
        "PS2 Lie-chart binding evidence changed",
    )
    checks.check(ps2_row.get("row_injection_recorded") is True, "PS2 row injection not linked")
    checks.check(
        ps2_row.get("row_injection_scaling_certified") is True,
        "PS2 row injection scaling not linked",
    )
    checks.check(
        ps2_row.get("row_injection_full_mean_value_binding_certified") is False,
        "PS2 row injection unexpectedly closes mean-value binding",
    )
    checks.check(
        ps2_row.get("row_injection_evidence") == "D5_P_STATE_PS2_ROW_INJECTION_AUDIT",
        "PS2 row injection evidence changed",
    )
    checks.check(ps2_row.get("nonlinear_binding_recorded") is True, "PS2 nonlinear binding not linked")
    checks.check(
        ps2_row.get("rotational_mean_value_binding_certified") is True,
        "PS2 rotational mean-value binding not certified",
    )
    checks.check(
        ps2_row.get("nonlinear_binding_full_mean_value_certified") is True,
        "PS2 nonlinear mean-value binding not certified",
    )
    checks.check(
        ps2_row.get("nonlinear_binding_full_ps2_certified") is False,
        "PS2 nonlinear binding overclaims full PS2",
    )
    checks.check(
        ps2_row.get("nonlinear_binding_evidence") == "D5_P_STATE_PS2_NONLINEAR_BINDING_AUDIT",
        "PS2 nonlinear binding evidence changed",
    )
    checks.check(ps2_row.get("aggregate_promotion_recorded") is True, "PS2 aggregate promotion not linked")
    checks.check(
        ps2_row.get("aggregate_weighted_ps2_inverse_certified") is True,
        "PS2 aggregate inverse not linked",
    )
    checks.check(ps2_row.get("uniform_ps2_constant_certified") is True, "PS2 aggregate constant not linked")
    checks.check(ps2_row.get("ps2_inverse_or_infsup_closed") is True, "PS2 aggregate inf-sup not linked")
    checks.check(
        ps2_row.get("aggregate_evidence") == "D5_P_STATE_PS2_AGGREGATE_PROMOTION_AUDIT",
        "PS2 aggregate evidence changed",
    )
    checks.check(ps2_row.get("finite_probe_full_column_rank_all") is True, "PS2 finite probe rank not linked")
    checks.check(
        ps2_row.get("finite_probe_uniform_constant_proved") is False,
        "PS2 finite probe unexpectedly proves uniform constant",
    )
    checks.check(
        ps2_row.get("finite_probe_evidence") == "D5_P_STATE_PS2_LINEARIZATION_PROBE",
        "PS2 finite probe evidence changed",
    )
    ps3_row = next((item for item in audit.get("required_future_proof", []) if item.get("id") == "PS3"), {})
    checks.check(ps3_row.get("conditional_conversion_closed") is True, "PS3 conditional conversion not linked")
    checks.check(ps3_row.get("actual_conversion_closed") is False, "PS3 actual conversion unexpectedly linked as closed")
    checks.check(
        ps3_row.get("conditional_conversion_evidence") == "D5_P_STATE_PS3_CONDITIONAL_CONVERSION_AUDIT",
        "PS3 conditional conversion evidence changed",
    )
    checks.check(ps3_row.get("actual_instantiation_gap_recorded") is True, "PS3 actual-instantiation gap not linked")
    checks.check(ps3_row.get("actual_instantiation_inputs_closed") == 2, "PS3 actual-instantiation closed input count changed")
    checks.check(ps3_row.get("actual_instantiation_inputs_total") == 4, "PS3 actual-instantiation total input count changed")
    checks.check(
        ps3_row.get("independent_h_weighted_acceleration_input_closed") is False,
        "PS3 independent h-weighted acceleration input unexpectedly closed",
    )
    checks.check(
        ps3_row.get("actual_instantiation_gap_evidence")
        == "D5_P_STATE_PS3_ACTUAL_INSTANTIATION_GAP_AUDIT",
        "PS3 actual-instantiation gap evidence changed",
    )
    checks.check(
        p_state_ps3_actual_gap.get("summary", {}).get("input_requirements_closed") == 2,
        "PS3 actual-instantiation source closed input count changed",
    )

    for token in [
        "Status: **P_state lift gap recorded; separate primitive-route certificate remains open**.",
        "P_state primitive closed: `False`.",
        "Term rows using P_state: `126/162`.",
        "Non-dynamic rows certified: `96/96`.",
        "Required future subproofs closed: `3/4`.",
        "PS1 map definition closed: `True`.",
        "PS4 anti-circularity closed: `True`.",
        "PS2 weighted target specification closed: `True`.",
        "PS2 kinematic-block certificate recorded/subblock/full-PS2/gaps: `True` / `True` / `False` / `3`.",
        "PS2 Lie-chart binding recorded/SO3/full-mean/gaps: `True` / `True` / `False` / `2`.",
        "PS2 row injection recorded/72-to-96/scaling/full-mean/gaps: `True` / `True` / `True` / `False` / `1`.",
        "PS2 nonlinear binding recorded/rot-mean/full-mean/full-PS2/gaps: `True` / `True` / `True` / `False` / `1`.",
        "PS2 aggregate promotion recorded/inverse/uniform/P_state/PC2: `True` / `True` / `True` / `False` / `False`.",
        "PS2 finite linearization probe recorded/full-rank: `True` / `True`.",
        "PS2 finite probe uniform constant proved: `False`.",
        "PS2 uniform constant proved: `True`.",
        "PS2 inverse or inf-sup closed: `True`.",
        "PS3 conditional conversion closed: `True`.",
        "PS3 actual-instantiation gap recorded/inputs/h-input: `True` / `2`-`4` / `False`.",
        "PS3 actual state lift conversion closed: `False`.",
        "Induced Taylor bounds proved: `0/162`.",
        "Primitive/Taylor PC2 route closed: `False`.",
        "A residual-row identity is not by itself a variable-lift estimate.",
        "Lemma `stage-residual-defect` is disallowed as an input to P_state.",
        "PS4 anti-circularity is closed.",
        "The PS2 weighted target specification is closed.",
        "The PS2 kinematic-block certificate records a uniform Euclidean Gauss subblock bound.",
        "The PS2 Lie-chart binding certificate records the pure SO(3) norm-equivalence constants.",
        "The PS2 row-injection audit records the 72-to-96 unweighted residual selection constant.",
        "The PS2 nonlinear binding audit records the rotational-row compact-tube mean-value estimate.",
        "Aggregate promotion of the component certificates to a full PS2 inverse is closed.",
        "The finite PS2 weighted linearization probe is recorded and full-rank on the finite solved-stage probes.",
        "The finite probe does not prove a uniform compact-tube inverse or inf-sup constant.",
        "The PS3 conditional conversion implication is recorded.",
        "PS2 local inverse or inf-sup proof is closed by the aggregate Taylor/mean-value proof.",
        "PS3 conversion to `O(h^7)` state lift rates remains open.",
        "P_state remains open.",
    ]:
        checks.check(token in audit_md, f"markdown missing token: {token}")

    if checks.errors:
        print("D5 P_state lift-gap audit validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("D5 P_state lift-gap audit validation: PASS")
    print("p_state_closed=False")
    print("required_future_subproofs_closed=3/4")
    print("pc2_closed=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
