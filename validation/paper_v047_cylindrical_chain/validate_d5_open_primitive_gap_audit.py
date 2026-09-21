#!/usr/bin/env python3
"""Validate the D5 open-primitive gap audit."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
AUDIT_JSON = PAPER / "D5_OPEN_PRIMITIVE_GAP_AUDIT.json"
AUDIT_MD = PAPER / "D5_OPEN_PRIMITIVE_GAP_AUDIT.md"


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
        plan = read_json(PAPER / "D5_PRIMITIVE_OBLIGATION_CLOSURE_PLAN.json")
        p_state_gap = read_json(PAPER / "D5_P_STATE_LIFT_GAP_AUDIT.json")
        p_state_ps2_kinematic = read_json(PAPER / "D5_P_STATE_PS2_KINEMATIC_BLOCK_CERTIFICATE.json")
        p_state_ps2_lie_chart = read_json(PAPER / "D5_P_STATE_PS2_LIE_CHART_BINDING_AUDIT.json")
        p_state_ps2_row_injection = read_json(PAPER / "D5_P_STATE_PS2_ROW_INJECTION_AUDIT.json")
        p_state_ps2_nonlinear = read_json(PAPER / "D5_P_STATE_PS2_NONLINEAR_BINDING_AUDIT.json")
        p_state_ps2_aggregate = read_json(PAPER / "D5_P_STATE_PS2_AGGREGATE_PROMOTION_AUDIT.json")
        p_state_ps2_probe = read_json(PAPER / "D5_P_STATE_PS2_LINEARIZATION_PROBE.json")
        p_state_ps3_actual_gap = read_json(PAPER / "D5_P_STATE_PS3_ACTUAL_INSTANTIATION_GAP_AUDIT.json")
        p_state_ps3_full_route = read_json(PAPER / "D5_P_STATE_PS3_FULL_RESIDUAL_ROUTE_CERTIFICATE.json")
        p_acc_map_definition = read_json(PAPER / "D5_P_ACC_MAP_DEFINITION_AUDIT.json")
        p_acc_row_binding = read_json(PAPER / "D5_P_ACC_ROW_BINDING_AUDIT.json")
        p_acc_independence = read_json(PAPER / "D5_P_ACC_INDEPENDENCE_AUDIT.json")
        p_acc_pa2_weighted_inverse = read_json(PAPER / "D5_P_ACC_PA2_WEIGHTED_INVERSE_AUDIT.json")
        p_lambda_interface = read_json(PAPER / "D5_P_LAMBDA_INTERFACE_AUDIT.json")
        p_lambda_inf_sup_probe = read_json(PAPER / "D5_P_LAMBDA_INF_SUP_PROBE.json")
        p_lambda_d3_noncircularity = read_json(PAPER / "D5_P_LAMBDA_D3_NONCIRCULARITY_AUDIT.json")
        p_lambda_pl2_geometric_margin = read_json(PAPER / "D5_P_LAMBDA_PL2_GEOMETRIC_MARGIN_AUDIT.json")
        p_lambda_pl4_rate_propagation = read_json(PAPER / "D5_P_LAMBDA_PL4_RATE_PROPAGATION_AUDIT.json")
        p_geom_reduction = read_json(PAPER / "D5_P_GEOM_CHART_REDUCTION_AUDIT.json")
        p_gyro_reduction = read_json(PAPER / "D5_P_GYRO_BILINEAR_REDUCTION_AUDIT.json")
        proof_manifest = read_json(PAPER / "PROOF_CLOSURE_MANIFEST.json")
    except Exception as exc:  # noqa: BLE001
        print(f"D5 open primitive gap audit validation: FAIL\n- {exc}")
        return 1

    summary = audit.get("summary", {})
    source = audit.get("source_consistency", {})
    rows = audit.get("open_primitive_interfaces", [])
    gate = audit.get("anti_circularity_gate", {})
    dependency_graph = audit.get("primitive_dependency_graph", {})
    blocker_ledger = audit.get("reader_facing_blocker_ledger", {})
    conditional_closure = audit.get("conditional_closure_proposition", {})

    checks.check(audit.get("schema") == "d5-open-primitive-gap-audit-v1", "schema changed")
    checks.check(
        audit.get("status") == "open_primitive_gaps_recorded_primitive_taylor_pc2_open",
        "status changed",
    )
    checks.check(audit.get("read_only") is True, "audit must be read-only")
    checks.check(audit.get("run_v047_invoked") is False, "run_v047 must not be invoked")
    checks.check(audit.get("submission_ready") is False, "submission readiness overclaimed")
    checks.check(audit.get("pc2_closed") is False, "PC2 unexpectedly closed")
    checks.check(audit.get("proof_gap_closed") is False, "proof gap unexpectedly closed")
    checks.check(audit.get("primitive_bounds_closed_count") == 1, "primitive closed count changed")
    checks.check(audit.get("open_primitive_count") == 5, "open primitive count changed")
    checks.check(
        audit.get("open_plan_ids") == ["P_state", "P_acc", "P_lambda", "P_geom", "P_gyro"],
        "open plan ids changed",
    )
    checks.check(summary.get("open_primitive_count") == 5, "summary open count changed")
    checks.check(summary.get("total_future_subproofs") == 19, "future subproof count changed")
    checks.check(summary.get("future_subproofs_closed") == 16, "future subproof closure count changed")
    checks.check(summary.get("induced_taylor_bounds_proved") == 0, "Taylor bounds unexpectedly proved")
    checks.check(summary.get("conditional_reductions_closed") == 2, "conditional reduction count changed")
    checks.check(
        summary.get("term_rows_with_open_primitives")
        == {"P_state": 126, "P_acc": 36, "P_lambda": 72, "P_geom": 36, "P_gyro": 18},
        "open primitive term-row map changed",
    )
    checks.check(summary.get("primitive_dependency_graph_recorded") is True, "dependency graph not recorded")
    checks.check(
        summary.get("root_lift_primitives") == ["P_state", "P_acc"],
        "root lift primitive list changed",
    )
    checks.check(
        summary.get("root_dependent_primitives") == ["P_lambda"],
        "root-dependent primitive list changed",
    )
    checks.check(
        summary.get("conditional_downstream_primitives") == ["P_geom", "P_gyro"],
        "conditional downstream primitive list changed",
    )
    checks.check(summary.get("dependency_edge_count") == 5, "dependency edge count changed")
    checks.check(summary.get("root_lift_term_row_total") == 162, "root lift term-row total changed")
    checks.check(
        summary.get("root_dependent_term_row_total") == 72,
        "root-dependent term-row total changed",
    )
    checks.check(
        summary.get("conditional_downstream_term_row_total") == 54,
        "conditional downstream term-row total changed",
    )
    checks.check(
        summary.get("p_state_direct_full_residual_route_recorded") is True,
        "P_state direct full-residual route not recorded",
    )
    checks.check(
        summary.get("p_state_direct_route_ps3_input_closed") is True,
        "P_state direct-route PS3 input not closed",
    )
    checks.check(
        summary.get("p_state_direct_route_state_lift_rate_closed") is True,
        "P_state direct-route state lift not closed",
    )
    checks.check(
        summary.get("p_state_direct_route_h_weighted_acceleration_input_closed") is True,
        "P_state direct-route h-acceleration input not closed",
    )
    checks.check(
        summary.get("p_state_direct_route_strict_proof_steps_closed") == 4
        and summary.get("p_state_direct_route_strict_proof_steps_total") == 4,
        "P_state direct-route strict proof step count changed",
    )
    checks.check(
        summary.get("p_state_primitive_route_closed_by_direct_corollary") is False,
        "P_state primitive route unexpectedly closed by direct corollary",
    )
    checks.check(
        summary.get("p_state_primitive_route_induced_bounds_by_direct_corollary") == 0,
        "P_state primitive Taylor bounds unexpectedly certified by direct corollary",
    )
    checks.check(dependency_graph.get("graph_recorded") is True, "dependency graph marker missing")
    checks.check(
        dependency_graph.get("root_lift_primitives") == ["P_state", "P_acc"],
        "dependency graph root list changed",
    )
    checks.check(
        dependency_graph.get("root_dependent_primitives") == ["P_lambda"],
        "dependency graph root-dependent list changed",
    )
    checks.check(
        dependency_graph.get("conditional_downstream_primitives") == ["P_geom", "P_gyro"],
        "dependency graph downstream list changed",
    )
    expected_edges = [
        ("P_state", "P_lambda"),
        ("P_acc", "P_lambda"),
        ("P_state", "P_geom"),
        ("P_lambda", "P_geom"),
        ("P_state", "P_gyro"),
    ]
    actual_edges = [
        (edge.get("source"), edge.get("target"))
        for edge in dependency_graph.get("dependency_edges", [])
        if isinstance(edge, dict)
    ]
    checks.check(actual_edges == expected_edges, "primitive dependency edges changed")
    checks.check(
        dependency_graph.get("closure_sequence") == ["P_state", "P_acc", "P_lambda", "P_geom", "P_gyro"],
        "primitive closure sequence changed",
    )
    checks.check(
        dependency_graph.get("root_lift_term_rows")
        == {"P_state": 126, "P_acc": 36},
        "root lift term-row map changed",
    )
    checks.check(
        dependency_graph.get("root_dependent_term_rows")
        == {"P_lambda": 72},
        "root-dependent term-row map changed",
    )
    checks.check(
        dependency_graph.get("conditional_downstream_term_rows")
        == {"P_geom": 36, "P_gyro": 18},
        "conditional downstream term-row map changed",
    )
    checks.check(
        dependency_graph.get("pc2_closes_only_after_all_open_primitives_close") is True,
        "dependency graph PC2 boundary missing",
    )
    checks.check(
        dependency_graph.get("does_not_certify_taylor_bounds") is True,
        "dependency graph overclaims Taylor certification",
    )
    minimal_next = dependency_graph.get("minimal_next_subproofs", [])
    checks.check(isinstance(minimal_next, list) and len(minimal_next) == 3, "minimal next subproof list changed")
    checks.check(
        [item.get("primitive") for item in minimal_next if isinstance(item, dict)]
        == ["P_state", "P_acc", "P_lambda"],
        "minimal next subproof primitive order changed",
    )
    checks.check(
        gate.get("stage_residual_perturbation_lemma_disallowed_as_input") is True,
        "stage-residual anti-circularity gate missing",
    )
    checks.check(
        gate.get("dynamic_residual_defect_disallowed_as_input") is True,
        "dynamic-residual anti-circularity gate missing",
    )
    checks.check(
        gate.get("residual_identity_alone_disallowed_as_variable_lift_proof") is True,
        "residual-identity anti-circularity gate missing",
    )
    checks.check(
        gate.get("finite_numerical_slopes_disallowed_as_symbolic_pc2_closure") is True,
        "finite-slope anti-circularity gate missing",
    )
    checks.check(audit.get("manuscript_link", {}).get("main_tex_present") is True, "main TeX link missing")
    checks.check(audit.get("manuscript_link", {}).get("flat_tex_present") is True, "flat TeX link missing")
    checks.check(
        blocker_ledger.get("main_tex_present") is True,
        "reader-facing primitive blocker ledger missing from main TeX",
    )
    checks.check(
        blocker_ledger.get("flat_tex_present") is True,
        "reader-facing primitive blocker ledger missing from flat TeX",
    )
    checks.check(
        blocker_ledger.get("preserves_zero_actual_bounds") is True,
        "primitive blocker ledger does not preserve zero actual-bound boundary",
    )
    checks.check(
        blocker_ledger.get("preserves_primitive_route_open_token") is True,
        "primitive blocker ledger does not preserve reader-facing separate primitive-route boundary",
    )
    checks.check(
        blocker_ledger.get("does_not_promote_direct_route") is True,
        "primitive blocker ledger promotes or omits direct-route nonpromotion boundary",
    )
    expected_blocker_tokens = [
        r"\label{tab:d5-primitive-blocker-ledger}",
        "D5 primitive/Taylor retained-interface map",
        "specification, not a premise of Theorem",
        "no actual D5 primitive Taylor bound from this route is invoked by the theorem",
        "This separate primitive-route lemma is a conditional finite implication",
        "The direct full-residual route corollary does not close the primitive route",
        r"Unweighted \(O(h^7)\) acceleration lift",
        r"\(h\|\delta A\|=O(h^7)\)",
        "Geometry reduction alone is not an actual term closure",
        "Bilinear reduction alone is not an actual term closure",
    ]
    checks.check(
        blocker_ledger.get("tokens") == expected_blocker_tokens,
        "reader-facing primitive blocker ledger token list changed",
    )
    checks.check(
        "- Reader-facing primitive obstruction map main/flat: `True/True`." in audit_md,
        "reader-facing primitive obstruction map markdown summary missing",
    )
    checks.check(
        conditional_closure.get("main_tex_present") is True,
        "conditional primitive/Taylor non-closure implication missing from main TeX",
    )
    checks.check(
        conditional_closure.get("flat_tex_present") is True,
        "conditional primitive/Taylor non-closure implication missing from flat TeX",
    )
    checks.check(
        conditional_closure.get("records_sufficiency_only") is True,
        "conditional non-closure implication does not preserve sufficiency-only boundary",
    )
    checks.check(
        conditional_closure.get("keeps_root_lifts_open") is True,
        "conditional non-closure implication does not keep root lifts open",
    )
    checks.check(
        conditional_closure.get("keeps_zero_actual_bounds") is True,
        "conditional non-closure implication changes or omits zero actual-bound boundary",
    )
    checks.check(
        conditional_closure.get("blocks_direct_route_promotion") is True,
        "conditional non-closure implication promotes or omits direct-route nonpromotion boundary",
    )
    expected_conditional_tokens = [
        r"\label{lem:d5-primitive-obligation-implication}",
        "Conditional primitive Taylor implication criterion (non-closure)",
        "same compact tube",
        "five primitive obligations",
        "zero actual primitive-route Taylor subterm bounds out of the 162",
        r"R_{\mathrm{dyn}}(Z_G)=O(h^7)",
        "not a closure certificate",
        "not an accepted primitive-route closure",
        "not invoked by Theorem",
        "No inverse projection from the aggregate",
        "Actual primitive-route Taylor subterm bounds are not established until",
    ]
    checks.check(
        conditional_closure.get("tokens") == expected_conditional_tokens,
        "conditional non-closure implication token list changed",
    )
    checks.check(
        "- Conditional primitive/Taylor non-closure implication main/flat: `True/True`." in audit_md,
        "conditional non-closure implication markdown summary missing",
    )
    checks.check(source.get("primitive_plan_schema") == "d5-primitive-obligation-closure-plan-v1", "plan schema link missing")
    checks.check(source.get("primitive_plan_pc2_closed") is False, "plan unexpectedly closes PC2")
    checks.check(source.get("primitive_plan_open_count") == 5, "plan open count link changed")
    checks.check(source.get("p_state_gap_schema") == "d5-p-state-lift-gap-audit-v1", "P_state gap link missing")
    checks.check(source.get("p_state_gap_closed") is False and p_state_gap.get("primitive_closed") is False, "P_state gap unexpectedly closed")
    checks.check(source.get("p_state_map_definition_closed") is True, "P_state map definition closure missing")
    checks.check(source.get("p_state_anticircularity_closed") is True, "P_state anti-circularity closure missing")
    checks.check(source.get("p_state_ps2_weighted_target_spec_closed") is True, "P_state PS2 weighted target spec closure missing")
    checks.check(source.get("p_state_ps2_inverse_or_infsup_closed") is True, "P_state PS2 inverse not closed")
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
        source.get("p_state_ps3_actual_gap_schema")
        == p_state_ps3_actual_gap.get("schema")
        == "d5-p-state-ps3-actual-instantiation-gap-audit-v1",
        "P_state PS3 actual-instantiation gap schema not linked",
    )
    checks.check(
        source.get("p_state_ps3_actual_gap_recorded") is True
        and p_state_ps3_actual_gap.get("status")
        == "ps3_actual_instantiation_gap_recorded_actual_ps3_open",
        "P_state PS3 actual-instantiation gap not recorded",
    )
    checks.check(
        source.get("p_state_ps3_actual_gap_inputs_closed") == 2
        and p_state_ps3_actual_gap.get("summary", {}).get("input_requirements_closed") == 2,
        "P_state PS3 actual-instantiation closed input count changed",
    )
    checks.check(
        source.get("p_state_ps3_actual_gap_inputs_total") == 4
        and p_state_ps3_actual_gap.get("summary", {}).get("input_requirements_total") == 4,
        "P_state PS3 actual-instantiation total input count changed",
    )
    checks.check(
        source.get("p_state_ps3_actual_gap_h_input_closed") is False
        and p_state_ps3_actual_gap.get("summary", {}).get(
            "independent_h_weighted_acceleration_input_closed"
        )
        is False,
        "P_state PS3 h-weighted acceleration input unexpectedly closed",
    )
    checks.check(
        source.get("p_state_ps3_actual_gap_pc2_closed") is False
        and p_state_ps3_actual_gap.get("pc2_closed") is False,
        "P_state PS3 actual-instantiation gap unexpectedly closes PC2",
    )
    checks.check(
        source.get("p_state_ps3_full_route_schema")
        == p_state_ps3_full_route.get("schema")
        == "d5-p-state-ps3-full-residual-route-certificate-v1",
        "P_state PS3 full-residual route schema missing",
    )
    checks.check(
        source.get("p_state_ps3_full_route_certificate_closed") is True
        and p_state_ps3_full_route.get("summary", {}).get("full_residual_route_certificate_closed") is True,
        "P_state PS3 full-residual route not linked closed",
    )
    checks.check(
        source.get("p_state_ps3_full_route_ps3_input_closed") is True
        and p_state_ps3_full_route.get("summary", {}).get("direct_route_ps3_input_closed") is True,
        "P_state PS3 full-residual route PS3 input not linked closed",
    )
    checks.check(
        source.get("p_state_ps3_full_route_state_lift_rate_closed") is True
        and p_state_ps3_full_route.get("summary", {}).get("direct_route_state_lift_rate_closed") is True,
        "P_state PS3 full-residual route state lift not linked closed",
    )
    checks.check(
        source.get("p_state_ps3_full_route_h_acc_input_closed") is True
        and p_state_ps3_full_route.get("summary", {}).get(
            "direct_route_h_weighted_acceleration_input_closed"
        )
        is True,
        "P_state PS3 full-residual route h-acceleration input not linked closed",
    )
    checks.check(
        source.get("p_state_ps3_full_route_strict_steps_closed") == 4
        and source.get("p_state_ps3_full_route_strict_steps_total") == 4,
        "P_state PS3 full-residual route strict step count changed",
    )
    checks.check(
        source.get("p_state_ps3_full_route_primitive_route_closed") is False
        and p_state_ps3_full_route.get("summary", {}).get("primitive_route_closed") is False,
        "P_state PS3 full-residual route unexpectedly closes primitive route",
    )
    checks.check(
        source.get("p_state_ps3_full_route_primitive_induced_bounds") == 0
        and p_state_ps3_full_route.get("summary", {}).get("primitive_route_induced_taylor_bounds_proved")
        == 0,
        "P_state PS3 full-residual route unexpectedly certifies primitive Taylor bounds",
    )
    checks.check(source.get("p_state_ps2_kinematic_block_recorded") is True, "P_state PS2 kinematic block not recorded")
    checks.check(
        source.get("p_state_ps2_kinematic_subblock_bound_certified") is True,
        "P_state PS2 kinematic subblock bound not certified",
    )
    checks.check(
        source.get("p_state_ps2_kinematic_full_nonlinear_ps2_certified") is False,
        "P_state PS2 kinematic block overclaims full nonlinear PS2",
    )
    checks.check(
        source.get("p_state_ps2_kinematic_block_schema")
        == "d5-p-state-ps2-kinematic-block-certificate-v1"
        and p_state_ps2_kinematic.get("ps2_kinematic_block_certificate_recorded") is True,
        "P_state PS2 kinematic block schema not linked",
    )
    checks.check(
        source.get("p_state_ps2_kinematic_block_pc2_closed") is False
        and p_state_ps2_kinematic.get("pc2_closed") is False,
        "P_state PS2 kinematic block unexpectedly closes PC2",
    )
    checks.check(
        source.get("p_state_ps2_lie_chart_binding_schema")
        == "d5-p-state-ps2-lie-chart-binding-audit-v1"
        and p_state_ps2_lie_chart.get("schema") == "d5-p-state-ps2-lie-chart-binding-audit-v1",
        "P_state PS2 Lie-chart binding schema not linked",
    )
    checks.check(
        source.get("p_state_ps2_lie_chart_binding_recorded") is True
        and p_state_ps2_lie_chart.get("p_state_ps2_lie_chart_binding_recorded") is True,
        "P_state PS2 Lie-chart binding not recorded",
    )
    checks.check(
        source.get("p_state_ps2_lie_chart_so3_norm_equivalence") is True
        and p_state_ps2_lie_chart.get("certifies_so3_chart_norm_equivalence") is True,
        "P_state PS2 SO(3) chart norm equivalence not linked",
    )
    checks.check(
        source.get("p_state_ps2_lie_chart_full_mean_value_binding") is False
        and p_state_ps2_lie_chart.get("certifies_full_nonlinear_mean_value_binding") is False,
        "P_state PS2 Lie-chart audit overclaims mean-value binding",
    )
    checks.check(
        source.get("p_state_ps2_lie_chart_pc2_closed") is False
        and p_state_ps2_lie_chart.get("pc2_closed") is False,
        "P_state PS2 Lie-chart unexpectedly closes PC2",
    )
    checks.check(
        source.get("p_state_ps2_row_injection_schema")
        == "d5-p-state-ps2-row-injection-audit-v1"
        and p_state_ps2_row_injection.get("schema") == "d5-p-state-ps2-row-injection-audit-v1",
        "P_state PS2 row-injection schema not linked",
    )
    checks.check(
        source.get("p_state_ps2_row_injection_recorded") is True
        and p_state_ps2_row_injection.get("p_state_ps2_row_injection_recorded") is True,
        "P_state PS2 row injection not recorded",
    )
    checks.check(
        source.get("p_state_ps2_row_injection_certified") is True
        and p_state_ps2_row_injection.get("certifies_72_to_96_row_injection") is True,
        "P_state PS2 row injection not certified",
    )
    checks.check(
        source.get("p_state_ps2_row_injection_unweighted_scaling") is True
        and p_state_ps2_row_injection.get("certifies_unweighted_residual_scaling") is True,
        "P_state PS2 row injection scaling not linked",
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
        == "d5-p-state-ps2-nonlinear-binding-audit-v1"
        and p_state_ps2_nonlinear.get("schema") == "d5-p-state-ps2-nonlinear-binding-audit-v1",
        "P_state PS2 nonlinear binding schema not linked",
    )
    checks.check(
        source.get("p_state_ps2_nonlinear_binding_recorded") is True
        and p_state_ps2_nonlinear.get("p_state_ps2_nonlinear_binding_recorded") is True,
        "P_state PS2 nonlinear binding not recorded",
    )
    checks.check(
        source.get("p_state_ps2_nonlinear_rotational_mean_value") is True
        and p_state_ps2_nonlinear.get("certifies_rotational_lie_row_mean_value_binding") is True,
        "P_state PS2 nonlinear rotational mean-value binding not linked",
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
        source.get("p_state_ps2_linearization_probe_recorded") is True
        and p_state_ps2_probe.get("ps2_weighted_linearization_probe_recorded") is True,
        "P_state PS2 linearization probe not recorded",
    )
    checks.check(
        source.get("p_state_ps2_linearization_probe_full_column_rank_all") is True
        and p_state_ps2_probe.get("summary", {}).get("finite_probe_full_column_rank_all") is True,
        "P_state PS2 linearization probe rank missing",
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
    checks.check(source.get("p_state_ps3_conditional_conversion_closed") is True, "P_state PS3 conditional conversion missing")
    checks.check(source.get("p_state_ps3_actual_conversion_closed") is False, "P_state PS3 actual conversion unexpectedly closed")
    checks.check(
        source.get("p_acc_map_definition_schema") == "d5-p-acc-map-definition-audit-v1",
        "P_acc map-definition audit link missing",
    )
    checks.check(
        source.get("p_acc_map_definition_closed") is True
        and p_acc_map_definition.get("pa1_map_definition_closed") is True,
        "P_acc map definition closure missing",
    )
    checks.check(
        source.get("p_acc_map_definition_primitive_closed") is False
        and p_acc_map_definition.get("primitive_closed") is False,
        "P_acc primitive unexpectedly closed",
    )
    checks.check(
        source.get("p_acc_map_definition_pc2_closed") is False
        and p_acc_map_definition.get("pc2_closed") is False,
        "P_acc map definition unexpectedly closes PC2",
    )
    checks.check(
        source.get("p_acc_row_binding_schema") == "d5-p-acc-row-binding-audit-v1",
        "P_acc row-binding audit link missing",
    )
    checks.check(
        source.get("p_acc_row_binding_closed") is True
        and p_acc_row_binding.get("pa4_row_binding_closed") is True,
        "P_acc row binding closure missing",
    )
    checks.check(
        source.get("p_acc_row_binding_primitive_closed") is False
        and p_acc_row_binding.get("primitive_closed") is False,
        "P_acc row binding unexpectedly closes primitive",
    )
    checks.check(
        source.get("p_acc_row_binding_pc2_closed") is False
        and p_acc_row_binding.get("pc2_closed") is False,
        "P_acc row binding unexpectedly closes PC2",
    )
    checks.check(
        source.get("p_acc_independence_schema") == "d5-p-acc-independence-audit-v1",
        "P_acc independence audit link missing",
    )
    checks.check(
        source.get("p_acc_independence_closed") is True
        and p_acc_independence.get("pa3_independence_closed") is True,
        "P_acc independence closure missing",
    )
    checks.check(
        source.get("p_acc_independence_primitive_closed") is False
        and p_acc_independence.get("primitive_closed") is False,
        "P_acc independence unexpectedly closes primitive",
    )
    checks.check(
        source.get("p_acc_independence_pc2_closed") is False
        and p_acc_independence.get("pc2_closed") is False,
        "P_acc independence unexpectedly closes PC2",
    )
    checks.check(
        source.get("p_acc_pa2_weighted_inverse_schema") == "d5-p-acc-pa2-weighted-inverse-audit-v1",
        "P_acc PA2 weighted-inverse audit link missing",
    )
    checks.check(
        source.get("p_acc_pa2_weighted_inverse_recorded") is True
        and p_acc_pa2_weighted_inverse.get("pa2_weighted_inverse_probe_recorded") is True,
        "P_acc PA2 weighted-inverse probe not recorded",
    )
    checks.check(
        source.get("p_acc_pa2_weighted_inverse_unweighted_closed") is False
        and p_acc_pa2_weighted_inverse.get("unweighted_acceleration_uniform_control_proved") is False,
        "P_acc PA2 weighted-inverse audit unexpectedly proves unweighted acceleration control",
    )
    checks.check(
        source.get("p_acc_pa2_weighted_inverse_pa2_closed") is False
        and p_acc_pa2_weighted_inverse.get("pa2_closed") is False,
        "P_acc PA2 weighted-inverse audit unexpectedly closes PA2",
    )
    checks.check(
        source.get("p_acc_pa2_weighted_inverse_pc2_closed") is False
        and p_acc_pa2_weighted_inverse.get("pc2_closed") is False,
        "P_acc PA2 weighted-inverse audit unexpectedly closes PC2",
    )
    checks.check(
        source.get("p_lambda_interface_schema") == "d5-p-lambda-interface-audit-v1",
        "P_lambda interface audit link missing",
    )
    checks.check(
        source.get("p_lambda_interface_closed") is True
        and p_lambda_interface.get("pl1_interface_closed") is True,
        "P_lambda interface closure missing",
    )
    checks.check(
        source.get("p_lambda_interface_primitive_closed") is False
        and p_lambda_interface.get("primitive_closed") is False,
        "P_lambda interface unexpectedly closes primitive",
    )
    checks.check(
        source.get("p_lambda_interface_pc2_closed") is False
        and p_lambda_interface.get("pc2_closed") is False,
        "P_lambda interface unexpectedly closes PC2",
    )
    checks.check(
        source.get("p_lambda_inf_sup_probe_schema") == "d5-p-lambda-inf-sup-probe-v1",
        "P_lambda inf-sup probe link missing",
    )
    checks.check(
        source.get("p_lambda_inf_sup_probe_recorded") is True
        and p_lambda_inf_sup_probe.get("p_lambda_inf_sup_probe_recorded") is True,
        "P_lambda inf-sup probe not recorded",
    )
    checks.check(
        source.get("p_lambda_inf_sup_probe_full_column_rank_all") is True
        and p_lambda_inf_sup_probe.get("summary", {}).get("finite_probe_full_column_rank_all") is True,
        "P_lambda finite rank evidence missing",
    )
    checks.check(
        source.get("p_lambda_inf_sup_probe_uniform_constant_proved") is False
        and p_lambda_inf_sup_probe.get("uniform_constant_proved") is False,
        "P_lambda finite probe unexpectedly proves uniform constant",
    )
    checks.check(
        source.get("p_lambda_inf_sup_probe_pc2_closed") is False
        and p_lambda_inf_sup_probe.get("pc2_closed") is False,
        "P_lambda finite probe unexpectedly closes PC2",
    )
    checks.check(
        source.get("p_lambda_d3_noncircularity_schema")
        == "d5-p-lambda-d3-noncircularity-audit-v1",
        "P_lambda D3 non-circularity audit link missing",
    )
    checks.check(
        source.get("p_lambda_d3_noncircularity_closed") is True
        and p_lambda_d3_noncircularity.get("pl3_d3_noncircularity_closed") is True,
        "P_lambda PL3 non-circularity closure missing",
    )
    checks.check(
        source.get("p_lambda_d3_noncircularity_primitive_closed") is False
        and p_lambda_d3_noncircularity.get("primitive_closed") is False,
        "P_lambda D3 audit unexpectedly closes primitive",
    )
    checks.check(
        source.get("p_lambda_d3_noncircularity_pc2_closed") is False
        and p_lambda_d3_noncircularity.get("pc2_closed") is False,
        "P_lambda D3 audit unexpectedly closes PC2",
    )
    checks.check(
        source.get("p_lambda_pl2_geometric_margin_schema")
        == "d5-p-lambda-pl2-geometric-margin-audit-v1",
        "P_lambda PL2 geometric-margin audit link missing",
    )
    checks.check(
        source.get("p_lambda_pl2_geometric_margin_recorded") is True
        and p_lambda_pl2_geometric_margin.get("pl2_geometric_margin_route_recorded") is True,
        "P_lambda PL2 geometric-margin route not recorded",
    )
    checks.check(
        source.get("p_lambda_pl2_geometric_margin_compact_tube_reduction_recorded") is True
        and p_lambda_pl2_geometric_margin.get("summary", {}).get("compact_tube_reduction_recorded") is True,
        "P_lambda PL2 compact-tube reduction not recorded",
    )
    checks.check(
        source.get("p_lambda_pl2_geometric_margin_symbolic_structure_certificate_recorded") is True
        and p_lambda_pl2_geometric_margin.get("summary", {}).get("symbolic_structure_certificate_recorded") is True,
        "P_lambda PL2 symbolic structure certificate not recorded",
    )
    checks.check(
        source.get("p_lambda_pl2_geometric_margin_normal_force_margin_proved") is True
        and p_lambda_pl2_geometric_margin.get("summary", {}).get("normal_force_margin_proved") is True,
        "P_lambda PL2 normal-force margin not proved",
    )
    checks.check(
        source.get("p_lambda_pl2_geometric_margin_smooth_friction_orthogonal_perturbation_proved") is True
        and p_lambda_pl2_geometric_margin.get("summary", {}).get(
            "smooth_friction_orthogonal_perturbation_proved"
        )
        is True,
        "P_lambda PL2 smooth-friction orthogonal perturbation proof missing",
    )
    checks.check(
        source.get("p_lambda_pl2_geometric_margin_axis_plane_margin_certificate_recorded") is True
        and p_lambda_pl2_geometric_margin.get("axis_plane_margin_certificate", {}).get("certificate_recorded")
        is True,
        "P_lambda PL2 axis-plane margin certificate not recorded",
    )
    checks.check(
        source.get("p_lambda_pl2_geometric_margin_axis_torque_compact_axis_margin_proved") is True
        and p_lambda_pl2_geometric_margin.get("summary", {}).get("axis_torque_compact_axis_margin_proved")
        is True,
        "P_lambda PL2 axis-plane margin not proved",
    )
    checks.check(
        source.get("p_lambda_pl2_geometric_margin_symbolic_margin_premise_proved") is True
        and p_lambda_pl2_geometric_margin.get("summary", {}).get("symbolic_margin_premise_proved") is True,
        "P_lambda PL2 symbolic margin premise not proved",
    )
    checks.check(
        source.get("p_lambda_pl2_geometric_margin_compact_tube_reduction_closes_pl2") is True
        and p_lambda_pl2_geometric_margin.get("compact_tube_reduction", {}).get("closes_pl2") is True,
        "P_lambda PL2 compact-tube reduction does not close PL2",
    )
    checks.check(
        source.get("p_lambda_pl2_geometric_margin_finite_probe_sufficient_for_symbolic_margin") is False
        and p_lambda_pl2_geometric_margin.get("compact_tube_reduction", {}).get(
            "finite_probe_sufficient_for_symbolic_margin"
        )
        is False,
        "P_lambda PL2 finite probe unexpectedly proves symbolic margin",
    )
    checks.check(
        source.get("p_lambda_pl2_geometric_margin_pl2_closed") is True
        and p_lambda_pl2_geometric_margin.get("pl2_uniform_inf_sup_bound_proved") is True,
        "P_lambda PL2 geometric-margin audit does not close PL2",
    )
    checks.check(
        source.get("p_lambda_pl2_geometric_margin_pc2_closed") is False
        and p_lambda_pl2_geometric_margin.get("pc2_closed") is False,
        "P_lambda PL2 geometric-margin audit unexpectedly closes PC2",
    )
    checks.check(
        source.get("p_lambda_pl4_rate_propagation_schema")
        == "d5-p-lambda-pl4-rate-propagation-audit-v1",
        "P_lambda PL4 rate-propagation audit link missing",
    )
    checks.check(
        source.get("p_lambda_pl4_rate_propagation_closed") is True
        and p_lambda_pl4_rate_propagation.get("pl4_lift_propagation_closed") is True,
        "P_lambda PL4 rate propagation not closed",
    )
    checks.check(
        source.get("p_lambda_pl4_conditional_multiplier_rate") is True
        and p_lambda_pl4_rate_propagation.get("conditional_multiplier_lift_rate_proved") is True,
        "P_lambda PL4 conditional multiplier rate missing",
    )
    checks.check(
        source.get("p_lambda_pl4_actual_multiplier_rate") is False
        and p_lambda_pl4_rate_propagation.get("multiplier_lift_rate_proved") is False,
        "P_lambda PL4 unexpectedly proves actual multiplier rate",
    )
    checks.check(
        source.get("p_lambda_pl4_state_input_closed") is False
        and p_lambda_pl4_rate_propagation.get("actual_state_lift_input_closed") is False,
        "P_lambda PL4 unexpectedly closes state input",
    )
    checks.check(
        source.get("p_lambda_pl4_acceleration_input_closed") is False
        and p_lambda_pl4_rate_propagation.get("actual_acceleration_lift_input_closed") is False,
        "P_lambda PL4 unexpectedly closes acceleration input",
    )
    checks.check(
        source.get("p_lambda_pl4_primitive_closed") is False
        and p_lambda_pl4_rate_propagation.get("primitive_closed") is False,
        "P_lambda PL4 unexpectedly closes primitive",
    )
    checks.check(
        source.get("p_lambda_pl4_pc2_closed") is False
        and p_lambda_pl4_rate_propagation.get("pc2_closed") is False,
        "P_lambda PL4 unexpectedly closes PC2",
    )
    checks.check(
        source.get("p_geom_reduction_schema") == "d5-p-geom-chart-reduction-audit-v1",
        "P_geom reduction link missing",
    )
    checks.check(
        source.get("p_geom_chart_reduction_closed") is True
        and p_geom_reduction.get("chart_reduction_closed") is True,
        "P_geom chart reduction not closed",
    )
    checks.check(
        source.get("p_geom_primitive_closed") is False
        and p_geom_reduction.get("primitive_closed") is False,
        "P_geom primitive unexpectedly closed",
    )
    checks.check(
        source.get("p_geom_open_dependencies") == ["P_state pose lift O(h^7)", "P_lambda multiplier lift O(h^7)"],
        "P_geom open dependencies changed",
    )
    checks.check(
        source.get("p_gyro_reduction_schema") == "d5-p-gyro-bilinear-reduction-audit-v1",
        "P_gyro reduction link missing",
    )
    checks.check(
        source.get("p_gyro_algebraic_reduction_closed") is True
        and p_gyro_reduction.get("algebraic_reduction_closed") is True,
        "P_gyro algebraic reduction not closed",
    )
    checks.check(
        source.get("p_gyro_primitive_closed") is False
        and p_gyro_reduction.get("primitive_closed") is False,
        "P_gyro primitive unexpectedly closed",
    )
    checks.check(
        source.get("p_gyro_open_dependencies") == ["P_state angular-velocity lift O(h^7)"],
        "P_gyro open dependency changed",
    )
    checks.check(
        source.get("proof_manifest_proof_gap_closed") is True
        and source.get("proof_manifest_direct_route_gap_closed") is True
        and proof_manifest.get("closure_state", {}).get("pc2_closed_by_direct_substitution") is True,
        "proof manifest direct-substitution closure not reflected",
    )
    checks.check(
        source.get("proof_manifest_proof_gap_closed_scope")
        == proof_manifest.get("closure_state", {}).get("proof_gap_closed_scope"),
        "proof manifest proof-gap scope not reflected",
    )
    checks.check(source.get("proof_manifest_pc2_closed") is True, "proof manifest direct PC2 closure not reflected")
    checks.check(
        proof_manifest.get("closure_state", {}).get("primitive_lift_route_closed") is False,
        "proof manifest unexpectedly closes primitive lift route",
    )
    checks.check(plan.get("pc2_closed") is False, "closure plan unexpectedly closes PC2")
    checks.check(isinstance(rows, list) and len(rows) == 5, "open primitive row count changed")
    for row in rows:
        if not isinstance(row, dict):
            checks.check(False, "open primitive row is not an object")
            continue
        plan_id = row.get("plan_id")
        checks.check(plan_id in {"P_state", "P_acc", "P_lambda", "P_geom", "P_gyro"}, f"unexpected open primitive {plan_id}")
        checks.check(row.get("primitive_closed") is False, f"{plan_id} unexpectedly closed")
        expected_closed = 4 if plan_id == "P_lambda" else 3
        checks.check(
            row.get("future_subproofs_closed") == expected_closed,
            f"{plan_id} future subproof closure count changed",
        )
        checks.check(
            row.get("conditional_reduction_closed") is (plan_id in {"P_geom", "P_gyro"}),
            f"{plan_id} conditional reduction flag changed",
        )
        if plan_id == "P_geom":
            checks.check(
                row.get("open_dependencies") == ["P_state pose lift O(h^7)", "P_lambda multiplier lift O(h^7)"],
                "P_geom open dependencies missing",
            )
        if plan_id == "P_gyro":
            checks.check(
                row.get("open_dependencies") == ["P_state angular-velocity lift O(h^7)"],
                "P_gyro open dependency missing",
            )
        if plan_id == "P_state":
            checks.check(
                row.get("open_dependencies")
                == [
                    "PS3 actual state lift conversion after conditional implication",
                ],
                "P_state open dependencies missing",
            )
            ps2_lie_chart = row.get("ps2_lie_chart_diagnostic", {})
            checks.check(
                isinstance(ps2_lie_chart, dict)
                and ps2_lie_chart.get("lie_chart_binding_recorded") is True,
                "P_state PS2 Lie-chart diagnostic missing",
            )
            checks.check(
                ps2_lie_chart.get("so3_chart_norm_equivalence_certified") is True,
                "P_state PS2 SO(3) chart diagnostic missing",
            )
            checks.check(
                ps2_lie_chart.get("full_nonlinear_mean_value_binding_certified") is False,
                "P_state PS2 Lie-chart diagnostic overclaims mean-value binding",
            )
            checks.check(
                ps2_lie_chart.get("remaining_binding_gap_count") == 2,
                "P_state PS2 Lie-chart diagnostic gap count changed",
            )
            checks.check(
                ps2_lie_chart.get("ps2_closed") is False and ps2_lie_chart.get("pc2_closed") is False,
                "P_state PS2 Lie-chart diagnostic unexpectedly closes proof",
            )
            ps2_row_injection = row.get("ps2_row_injection_diagnostic", {})
            checks.check(
                isinstance(ps2_row_injection, dict)
                and ps2_row_injection.get("row_injection_recorded") is True,
                "P_state PS2 row-injection diagnostic missing",
            )
            checks.check(
                ps2_row_injection.get("row_injection_certified") is True,
                "P_state PS2 row-injection diagnostic not certified",
            )
            checks.check(
                ps2_row_injection.get("unweighted_scaling_certified") is True,
                "P_state PS2 row-injection scaling diagnostic missing",
            )
            checks.check(
                ps2_row_injection.get("full_nonlinear_mean_value_binding_certified") is False,
                "P_state PS2 row-injection diagnostic overclaims mean-value binding",
            )
            checks.check(
                ps2_row_injection.get("remaining_binding_gap_count") == 1,
                "P_state PS2 row-injection diagnostic gap count changed",
            )
            checks.check(
                ps2_row_injection.get("ps2_closed") is False and ps2_row_injection.get("pc2_closed") is False,
                "P_state PS2 row-injection diagnostic unexpectedly closes proof",
            )
            ps2_nonlinear = row.get("ps2_nonlinear_binding_diagnostic", {})
            checks.check(
                isinstance(ps2_nonlinear, dict)
                and ps2_nonlinear.get("nonlinear_binding_recorded") is True,
                "P_state PS2 nonlinear binding diagnostic missing",
            )
            checks.check(
                ps2_nonlinear.get("rotational_mean_value_binding_certified") is True,
                "P_state PS2 nonlinear binding diagnostic not certified",
            )
            checks.check(
                ps2_nonlinear.get("full_mean_value_binding_certified") is True,
                "P_state PS2 nonlinear full mean-value diagnostic missing",
            )
            checks.check(
                ps2_nonlinear.get("full_ps2_certified") is False,
                "P_state PS2 nonlinear binding diagnostic overclaims full PS2",
            )
            checks.check(
                ps2_nonlinear.get("remaining_promotion_gap_count") == 1,
                "P_state PS2 nonlinear binding diagnostic promotion gap count changed",
            )
            checks.check(
                ps2_nonlinear.get("ps2_closed") is False and ps2_nonlinear.get("pc2_closed") is False,
                "P_state PS2 nonlinear binding diagnostic unexpectedly closes proof",
            )
            ps2_aggregate = row.get("ps2_aggregate_promotion_diagnostic", {})
            checks.check(
                isinstance(ps2_aggregate, dict)
                and ps2_aggregate.get("aggregate_promotion_recorded") is True,
                "P_state PS2 aggregate diagnostic missing",
            )
            checks.check(
                ps2_aggregate.get("aggregate_weighted_ps2_inverse_certified") is True,
                "P_state PS2 aggregate diagnostic does not certify inverse",
            )
            checks.check(
                ps2_aggregate.get("uniform_ps2_constant_certified") is True,
                "P_state PS2 aggregate diagnostic does not certify uniform constant",
            )
            checks.check(ps2_aggregate.get("ps2_closed") is True, "P_state PS2 aggregate diagnostic does not close PS2")
            checks.check(
                ps2_aggregate.get("ps3_actual_conversion_closed") is False,
                "P_state PS2 aggregate diagnostic unexpectedly closes PS3",
            )
            checks.check(
                ps2_aggregate.get("p_state_closed") is False and ps2_aggregate.get("pc2_closed") is False,
                "P_state PS2 aggregate diagnostic unexpectedly closes primitive or PC2",
            )
        if plan_id == "P_acc":
            checks.check(
                row.get("open_dependencies")
                == ["PA2 velocity-collocation-to-acceleration lift proof"],
                "P_acc open dependencies missing",
            )
            pa2_diagnostic = row.get("pa2_weighted_inverse_diagnostic", {})
            checks.check(
                isinstance(pa2_diagnostic, dict)
                and pa2_diagnostic.get("pa2_weighted_inverse_probe_recorded") is True,
                "P_acc PA2 weighted-inverse diagnostic missing",
            )
            checks.check(
                pa2_diagnostic.get("weighted_h_acceleration_control_recorded") is True,
                "P_acc PA2 weighted h-acceleration diagnostic missing",
            )
            checks.check(
                pa2_diagnostic.get("finite_probe_full_column_rank_all") is True,
                "P_acc PA2 finite full-rank diagnostic missing",
            )
            checks.check(
                float(pa2_diagnostic.get("max_unweighted_acceleration_projection_constant", 0.0)) > 0.0,
                "P_acc PA2 unweighted acceleration projection constant missing",
            )
            checks.check(
                float(pa2_diagnostic.get("max_weighted_h_acceleration_projection_constant", 0.0)) > 0.0,
                "P_acc PA2 weighted h-acceleration projection constant missing",
            )
            checks.check(
                pa2_diagnostic.get("unweighted_acceleration_uniform_control_proved") is False,
                "P_acc PA2 diagnostic unexpectedly proves unweighted acceleration control",
            )
            checks.check(pa2_diagnostic.get("pa2_closed") is False, "P_acc PA2 diagnostic closes PA2")
            checks.check(pa2_diagnostic.get("pc2_closed") is False, "P_acc PA2 diagnostic closes PC2")
        if plan_id == "P_lambda":
            checks.check(
                row.get("open_dependencies")
                == [
                    "P_state actual state lift O(h^7)",
                    "P_acc unweighted acceleration lift O(h^7)",
                ],
                "P_lambda open dependencies missing",
            )
            finite_diagnostic = row.get("finite_diagnostic", {})
            checks.check(
                isinstance(finite_diagnostic, dict)
                and finite_diagnostic.get("p_lambda_inf_sup_probe_recorded") is True,
                "P_lambda finite diagnostic missing",
            )
            checks.check(
                finite_diagnostic.get("finite_probe_full_column_rank_all") is True,
                "P_lambda finite full-rank diagnostic missing",
            )
            checks.check(
                finite_diagnostic.get("uniform_constant_proved") is False,
                "P_lambda finite diagnostic unexpectedly proves uniform constant",
            )
            checks.check(
                finite_diagnostic.get("pc2_closed") is False,
                "P_lambda finite diagnostic unexpectedly closes PC2",
            )
            noncircularity_diagnostic = row.get("noncircularity_diagnostic", {})
            checks.check(
                isinstance(noncircularity_diagnostic, dict)
                and noncircularity_diagnostic.get("pl3_d3_noncircularity_closed") is True,
                "P_lambda non-circularity diagnostic missing",
            )
            checks.check(
                noncircularity_diagnostic.get("d3_identity_is_algebraic_mapping") is True,
                "P_lambda D3 algebraic-mapping boundary missing",
            )
            checks.check(
                noncircularity_diagnostic.get("d3_identity_does_not_assume_dynamic_defect_rate") is True,
                "P_lambda D3 dynamic-defect anti-circularity missing",
            )
            checks.check(
                noncircularity_diagnostic.get("d3_identity_not_used_as_multiplier_rate") is True,
                "P_lambda D3 multiplier-rate boundary missing",
            )
            checks.check(
                noncircularity_diagnostic.get("pc2_closed") is False,
                "P_lambda D3 diagnostic unexpectedly closes PC2",
            )
            pl2_diagnostic = row.get("pl2_geometric_margin_diagnostic", {})
            checks.check(
                isinstance(pl2_diagnostic, dict)
                and pl2_diagnostic.get("pl2_geometric_margin_route_recorded") is True,
                "P_lambda PL2 geometric-margin diagnostic missing",
            )
            checks.check(
                pl2_diagnostic.get("finite_full_stage_rank_all") is True,
                "P_lambda PL2 full-stage rank diagnostic missing",
            )
            checks.check(
                pl2_diagnostic.get("finite_translational_normal_rank_all") is True,
                "P_lambda PL2 translational normal rank diagnostic missing",
            )
            checks.check(
                pl2_diagnostic.get("finite_rotational_axis_torque_rank_all") is True,
                "P_lambda PL2 rotational torque rank diagnostic missing",
            )
            checks.check(
                pl2_diagnostic.get("compact_tube_reduction_recorded") is True,
                "P_lambda PL2 compact-tube reduction diagnostic missing",
            )
            checks.check(
                pl2_diagnostic.get("symbolic_structure_certificate_recorded") is True,
                "P_lambda PL2 symbolic structure diagnostic missing",
            )
            checks.check(
                pl2_diagnostic.get("normal_force_margin_proved") is True,
                "P_lambda PL2 normal-force margin diagnostic missing",
            )
            checks.check(
                pl2_diagnostic.get("smooth_friction_orthogonal_perturbation_proved") is True,
                "P_lambda PL2 smooth-friction diagnostic missing",
            )
            checks.check(
                pl2_diagnostic.get("translational_normal_subblock_lower_bound_proved") is True,
                "P_lambda PL2 translational lower-bound diagnostic missing",
            )
            checks.check(
                pl2_diagnostic.get("axis_plane_margin_certificate_recorded") is True,
                "P_lambda PL2 axis-plane margin certificate diagnostic missing",
            )
            checks.check(
                pl2_diagnostic.get("axis_torque_compact_axis_margin_proved") is True,
                "P_lambda PL2 axis-plane margin not proved",
            )
            checks.check(
                pl2_diagnostic.get("symbolic_margin_premise_proved") is True,
                "P_lambda PL2 diagnostic does not prove symbolic margin premise",
            )
            checks.check(
                pl2_diagnostic.get("compact_tube_reduction_closes_pl2") is True,
                "P_lambda PL2 compact-tube reduction diagnostic does not close PL2",
            )
            checks.check(
                pl2_diagnostic.get("finite_probe_sufficient_for_symbolic_margin") is False,
                "P_lambda PL2 diagnostic unexpectedly treats finite probes as symbolic proof",
            )
            checks.check(
                pl2_diagnostic.get("uniform_compact_tube_margin_proved") is True,
                "P_lambda PL2 diagnostic does not prove uniform compact-tube margin",
            )
            checks.check(
                pl2_diagnostic.get("pl2_uniform_inf_sup_bound_proved") is True,
                "P_lambda PL2 diagnostic does not close PL2",
            )
            checks.check(
                pl2_diagnostic.get("pc2_closed") is False,
                "P_lambda PL2 diagnostic unexpectedly closes PC2",
            )
            pl4_diagnostic = row.get("pl4_rate_propagation_diagnostic", {})
            checks.check(
                isinstance(pl4_diagnostic, dict)
                and pl4_diagnostic.get("pl4_lift_propagation_closed") is True,
                "P_lambda PL4 diagnostic missing",
            )
            checks.check(
                pl4_diagnostic.get("conditional_multiplier_lift_rate_proved") is True,
                "P_lambda PL4 conditional multiplier rate missing",
            )
            checks.check(
                pl4_diagnostic.get("multiplier_lift_rate_proved") is False,
                "P_lambda PL4 diagnostic unexpectedly proves actual multiplier rate",
            )
            checks.check(
                pl4_diagnostic.get("actual_state_lift_input_closed") is False,
                "P_lambda PL4 diagnostic unexpectedly closes state input",
            )
            checks.check(
                pl4_diagnostic.get("actual_acceleration_lift_input_closed") is False,
                "P_lambda PL4 diagnostic unexpectedly closes acceleration input",
            )
            checks.check(
                pl4_diagnostic.get("uses_first_order_taylor_with_quadratic_remainder") is True,
                "P_lambda PL4 Taylor marker missing",
            )
            checks.check(
                pl4_diagnostic.get("uses_stage_residual_defect") is False,
                "P_lambda PL4 diagnostic uses stage residual",
            )
            checks.check(
                pl4_diagnostic.get("uses_d5_dynamic_residual_defect") is False,
                "P_lambda PL4 diagnostic uses D5 dynamic defect",
            )
            checks.check(
                pl4_diagnostic.get("uses_direct_substitution_as_proof") is False,
                "P_lambda PL4 diagnostic uses direct substitution",
            )
            checks.check(
                pl4_diagnostic.get("uses_finite_probe_as_proof") is False,
                "P_lambda PL4 diagnostic uses finite probe",
            )
            checks.check(
                pl4_diagnostic.get("uses_d3_as_rate_proof") is False,
                "P_lambda PL4 diagnostic uses D3 as rate proof",
            )
            checks.check(
                pl4_diagnostic.get("term_bounds_proved") == 0,
                "P_lambda PL4 diagnostic unexpectedly proves Taylor bounds",
            )
            checks.check(
                pl4_diagnostic.get("pc2_closed") is False,
                "P_lambda PL4 diagnostic unexpectedly closes PC2",
            )
        if plan_id != "P_lambda":
            checks.check(row.get("finite_diagnostic") is None, f"{plan_id} finite diagnostic unexpectedly present")
            checks.check(
                row.get("noncircularity_diagnostic") is None,
                f"{plan_id} non-circularity diagnostic unexpectedly present",
            )
            checks.check(
                row.get("pl2_geometric_margin_diagnostic") is None,
                f"{plan_id} PL2 geometric-margin diagnostic unexpectedly present",
            )
            checks.check(
                row.get("pl4_rate_propagation_diagnostic") is None,
                f"{plan_id} PL4 rate-propagation diagnostic unexpectedly present",
            )
        if plan_id != "P_acc":
            checks.check(
                row.get("pa2_weighted_inverse_diagnostic") is None,
                f"{plan_id} PA2 weighted-inverse diagnostic unexpectedly present",
            )
        if plan_id != "P_state":
            checks.check(
                row.get("ps2_aggregate_promotion_diagnostic") is None,
                f"{plan_id} PS2 aggregate diagnostic unexpectedly present",
            )
        checks.check(row.get("induced_taylor_bounds_proved") == 0, f"{plan_id} induced bounds unexpectedly proved")
        checks.check(int(row.get("term_rows_using_obligation", 0)) > 0, f"{plan_id} has no term rows")
        checks.check(isinstance(row.get("missing_proof"), str) and row.get("missing_proof"), f"{plan_id} missing proof text absent")
        checks.check(isinstance(row.get("future_subproofs"), list) and row.get("future_subproofs"), f"{plan_id} future subproofs absent")
        checks.check(len(row.get("forbidden_shortcuts", [])) == 3, f"{plan_id} forbidden shortcuts changed")

    for token in [
        "Status: **open primitive gaps recorded; primitive-and-Taylor PC2 route remains open**.",
        "Open primitive obligations: `5/5`.",
        "Required future subproofs: `19`.",
        "Required future subproofs closed: `16/19`.",
        "Conditional reductions closed: `2`.",
        "Primitive dependency graph recorded: `True`.",
        "Root lift primitives: `['P_state', 'P_acc']`.",
        "Root-dependent conditional primitives: `['P_lambda']`.",
        "Conditional downstream primitives: `['P_geom', 'P_gyro']`.",
        "Dependency edges: `5`.",
        "Root, root-dependent, and downstream term-row totals: `162/72/54`.",
        "P_state direct full-residual route recorded: `True`.",
        "P_state direct-route PS3/state/h-acceleration rates closed: `True/True/True`.",
        "P_state direct-route strict proof steps closed: `4/4`.",
        "P_state primitive route closed by direct corollary: `False`.",
        "P_state primitive-route induced bounds by direct corollary: `0/162`.",
        "Induced Taylor bounds proved: `0/162`.",
        "Primitive/Taylor PC2 route closed: `False`.",
        "## Primitive Dependency Graph",
        "Closure sequence: `['P_state', 'P_acc', 'P_lambda', 'P_geom', 'P_gyro']`.",
        "Primitive/Taylor PC2 route closes only after all five open primitive obligations close.",
        "`P_state`: PS3 actual state-lift instantiation",
        "`P_acc`: PA2 unweighted acceleration lift",
        "`P_lambda`: instantiate PL4 with P_state/P_acc lift inputs",
        "## Direct-Route Corollary",
        "The P_state full-residual route certificate closes a direct-route PS3",
        "The direct-route PS3 input is closed.",
        "The primitive-and-Taylor PC2 route remains open.",
        "Zero primitive-route induced Taylor bounds are certified by this corollary.",
        "Lemma `stage-residual-defect` is disallowed as an input to every open primitive.",
        "The D5 dynamic residual defect is disallowed as an input to every open primitive.",
        "Residual identities alone do not prove variable-lift rates.",
        "Finite numerical slopes do not close the primitive-and-Taylor route to PC2.",
        "The PS2 kinematic-block certificate records a uniform Euclidean Gauss subblock bound.",
        "The PS2 Lie-chart binding audit records pure SO(3) norm-equivalence.",
        "The PS2 row-injection audit records 72-to-96 unweighted residual dominance.",
        "The PS2 nonlinear binding audit records rotational-row compact-tube mean-value control.",
        "The PS2 aggregate promotion audit closes the uniform weighted inverse while leaving PS3, P_state, and the primitive-and-Taylor route to PC2 open.",
        "The PS3 actual-instantiation gap audit records `2/4` PS3 inputs closed while the independent h-weighted acceleration input remains open.",
        "The finite PS2 linearization probe is full-rank on recorded solved-stage probes but does not prove a uniform compact-tube inf-sup constant.",
        "The closed P_state map definition, PS2 weighted target, PS2 aggregate promotion, PS3 conditional conversion, and anti-circularity route still depend on actual PS3 state-lift instantiation before they can imply primitive lift rates.",
        "The closed P_acc map definition, row binding, non-dynamic input boundary, and PA2 weighted-inverse diagnostic still depend on the unweighted acceleration lift-rate proof.",
        "The closed P_lambda interface, finite multiplier-column rank probe, PL2 geometric-margin route, PL2 symbolic normal/friction structure, PL2 axis-plane margin, PL2 compact-tube reduction, non-circular D3 algebraic mapping, and conditional PL4 propagation still depend on the actual P_state and P_acc lift inputs before P_lambda can close.",
        "The closed P_geom chart reduction still depends on the open P_state and P_lambda lifts.",
        "The closed P_gyro bilinear reduction still depends on the open P_state angular-velocity lift.",
        "Five primitive obligations remain open.",
        "The P_state non-dynamic map definition, PS2 weighted target, PS2 aggregate promotion, finite PS2 linearization probe, PS3 conditional conversion, and anti-circularity subproof are recorded, but P_state is not closed.",
        "The P_acc acceleration map definition, row binding, and independence subproof are closed, but P_acc is not closed.",
        "The P_lambda multiplier interface, finite inf-sup probe, PL2 symbolic normal/friction structure, PL2 axis-plane margin, PL2 compact-tube reduction, non-circular D3 algebraic mapping, and conditional PL4 propagation are recorded, but P_lambda is not closed.",
        "The P_geom chart reduction is recorded only as a conditional reduction; P_geom is not closed.",
        "The P_gyro algebraic reduction is recorded only as a conditional reduction; P_gyro is not closed.",
    ]:
        checks.check(token in audit_md, f"markdown missing token: {token}")

    if checks.errors:
        print("D5 open primitive gap audit validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("D5 open primitive gap audit validation: PASS")
    print("open_primitives=5/5")
    print("future_subproofs_closed=16/19")
    print("pc2_closed=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
