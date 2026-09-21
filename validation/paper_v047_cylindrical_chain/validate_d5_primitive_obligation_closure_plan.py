#!/usr/bin/env python3
"""Validate the D5 primitive-obligation closure plan."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
PLAN_JSON = PAPER / "D5_PRIMITIVE_OBLIGATION_CLOSURE_PLAN.json"
PLAN_MD = PAPER / "D5_PRIMITIVE_OBLIGATION_CLOSURE_PLAN.md"


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
        plan = read_json(PLAN_JSON)
        plan_md = PLAN_MD.read_text(encoding="utf-8", errors="replace")
        primitive_reduction = read_json(PAPER / "D5_PRIMITIVE_BOUND_REDUCTION_AUDIT.json")
        p_tube_audit = read_json(PAPER / "D5_P_TUBE_CONSTANTS_AUDIT.json")
        p_state_gap = read_json(PAPER / "D5_P_STATE_LIFT_GAP_AUDIT.json")
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
        p_acc_map_definition = read_json(PAPER / "D5_P_ACC_MAP_DEFINITION_AUDIT.json")
        p_acc_row_binding = read_json(PAPER / "D5_P_ACC_ROW_BINDING_AUDIT.json")
        p_acc_independence = read_json(PAPER / "D5_P_ACC_INDEPENDENCE_AUDIT.json")
        p_lambda_interface = read_json(PAPER / "D5_P_LAMBDA_INTERFACE_AUDIT.json")
        p_geom_reduction = read_json(PAPER / "D5_P_GEOM_CHART_REDUCTION_AUDIT.json")
        p_gyro_reduction = read_json(PAPER / "D5_P_GYRO_BILINEAR_REDUCTION_AUDIT.json")
        term_budget = read_json(PAPER / "D5_TAYLOR_TERM_BUDGET_AUDIT.json")
        proof_manifest = read_json(PAPER / "PROOF_CLOSURE_MANIFEST.json")
    except Exception as exc:  # noqa: BLE001
        print(f"D5 primitive-obligation closure plan validation: FAIL\n- {exc}")
        return 1

    summary = plan.get("summary", {})
    implication = plan.get("conditional_implication", {})
    source = plan.get("source_consistency", {})
    rows = plan.get("primitive_obligation_plan", [])

    checks.check(plan.get("schema") == "d5-primitive-obligation-closure-plan-v1", "schema changed")
    checks.check(
        plan.get("status") == "primitive_obligation_closure_plan_recorded_primitive_taylor_pc2_open",
        "status changed",
    )
    checks.check(plan.get("read_only") is True, "plan must be read-only")
    checks.check(plan.get("run_v047_invoked") is False, "run_v047 must not be invoked")
    checks.check(plan.get("submission_ready") is False, "submission readiness overclaimed")
    checks.check(plan.get("pc2_closed") is False, "PC2 unexpectedly closed")
    checks.check(plan.get("proof_gap_closed") is False, "proof gap unexpectedly closed")
    checks.check(plan.get("primitive_bounds_proved") is False, "primitive bounds unexpectedly proved")
    checks.check(plan.get("primitive_bounds_closed_count") == 1, "primitive closed count changed")
    checks.check(plan.get("induced_taylor_bounds_proved") is False, "Taylor bounds unexpectedly proved")
    checks.check(summary.get("primitive_obligation_count") == 6, "primitive obligation count changed")
    checks.check(summary.get("primitive_obligations_with_closure_steps") == 6, "closure-step coverage changed")
    checks.check(summary.get("primitive_obligations_proved") == 1, "primitive closed count changed")
    checks.check(summary.get("open_primitive_obligations") == 5, "open primitive obligation count changed")
    checks.check(summary.get("closure_step_count") == 35, "closure-step count changed")
    checks.check(summary.get("term_rows") == 162, "term-row count changed")
    checks.check(summary.get("term_rows_with_reduction_rule") == 162, "reduction-rule coverage changed")
    checks.check(summary.get("induced_taylor_bounds_proved") == 0, "induced Taylor bounds unexpectedly proved")
    checks.check(summary.get("p_tube_closed") is True, "P_tube closure not carried into plan")
    checks.check(implication.get("lemma_label") == "lem:d5-primitive-obligation-implication", "lemma label changed")
    checks.check(implication.get("implication_recorded_in_manuscript") is True, "manuscript implication missing")
    checks.check(implication.get("main_tex_present") is True, "main TeX implication missing")
    checks.check(implication.get("flat_tex_present") is True, "flat TeX implication missing")
    checks.check(
        implication.get("does_not_prove_remaining_primitives") is True,
        "remaining primitive non-proof marker missing",
    )
    checks.check(implication.get("does_not_close_pc2") is True, "PC2 non-closure marker missing")
    checks.check(source.get("primitive_reduction_pc2_closed") is False, "source primitive reduction closes PC2")
    checks.check(source.get("primitive_reduction_terms") == 162, "source primitive reduction term count changed")
    checks.check(
        source.get("p_tube_audit_schema") == "d5-p-tube-constants-audit-v1"
        and source.get("p_tube_closed") is True
        and source.get("p_tube_pc2_closed") is False
        and p_tube_audit.get("primitive_closed") is True,
        "P_tube audit not linked into closure plan",
    )
    checks.check(
        source.get("p_state_gap_audit_schema") == "d5-p-state-lift-gap-audit-v1"
        and source.get("p_state_gap_recorded") is True
        and source.get("p_state_closed") is False
        and source.get("p_state_pc2_closed") is False
        and p_state_gap.get("primitive_closed") is False,
        "P_state lift-gap audit not linked into closure plan",
    )
    checks.check(
        source.get("p_state_map_definition_schema") == "d5-p-state-map-definition-audit-v1"
        and source.get("p_state_map_definition_closed") is True
        and source.get("p_state_map_definition_primitive_closed") is False
        and source.get("p_state_map_definition_pc2_closed") is False
        and p_state_map_definition.get("ps1_map_definition_closed") is True,
        "P_state map-definition audit not linked into closure plan",
    )
    checks.check(
        source.get("p_state_anticircularity_schema") == "d5-p-state-anticircularity-audit-v1"
        and source.get("p_state_anticircularity_closed") is True
        and source.get("p_state_anticircularity_primitive_closed") is False
        and source.get("p_state_anticircularity_pc2_closed") is False
        and p_state_anticircularity.get("ps4_anticircularity_closed") is True,
        "P_state anti-circularity audit not linked into closure plan",
    )
    checks.check(
        source.get("p_state_ps2_weighted_target_schema") == "d5-p-state-ps2-weighted-target-audit-v1"
        and source.get("p_state_ps2_weighted_target_spec_closed") is True
        and source.get("p_state_ps2_weighted_target_infsup_closed") is False
        and source.get("p_state_ps2_weighted_target_pc2_closed") is False
        and p_state_ps2_target.get("ps2_target_spec_closed") is True,
        "P_state PS2 weighted target audit not linked into closure plan",
    )
    checks.check(
        source.get("p_state_ps2_kinematic_block_schema")
        == "d5-p-state-ps2-kinematic-block-certificate-v1"
        and source.get("p_state_ps2_kinematic_block_recorded") is True
        and source.get("p_state_ps2_kinematic_subblock_bound_certified") is True
        and source.get("p_state_ps2_kinematic_full_nonlinear_ps2_certified") is False
        and source.get("p_state_ps2_kinematic_block_pc2_closed") is False
        and p_state_ps2_kinematic.get("ps2_kinematic_block_certificate_recorded") is True,
        "P_state PS2 kinematic-block certificate not linked into closure plan",
    )
    checks.check(
        source.get("p_state_ps2_lie_chart_binding_schema")
        == "d5-p-state-ps2-lie-chart-binding-audit-v1"
        and source.get("p_state_ps2_lie_chart_binding_recorded") is True
        and source.get("p_state_ps2_lie_chart_so3_norm_equivalence") is True
        and source.get("p_state_ps2_lie_chart_full_mean_value_binding") is False
        and source.get("p_state_ps2_lie_chart_pc2_closed") is False
        and p_state_ps2_lie_chart.get("p_state_ps2_lie_chart_binding_recorded") is True,
        "P_state PS2 Lie-chart binding audit not linked into closure plan",
    )
    checks.check(
        source.get("p_state_ps2_row_injection_schema")
        == "d5-p-state-ps2-row-injection-audit-v1"
        and source.get("p_state_ps2_row_injection_recorded") is True
        and source.get("p_state_ps2_row_injection_certified") is True
        and source.get("p_state_ps2_row_injection_unweighted_scaling") is True
        and source.get("p_state_ps2_row_injection_full_mean_value_binding") is False
        and source.get("p_state_ps2_row_injection_pc2_closed") is False
        and p_state_ps2_row_injection.get("p_state_ps2_row_injection_recorded") is True,
        "P_state PS2 row-injection audit not linked into closure plan",
    )
    checks.check(
        source.get("p_state_ps2_nonlinear_binding_schema")
        == "d5-p-state-ps2-nonlinear-binding-audit-v1"
        and source.get("p_state_ps2_nonlinear_binding_recorded") is True
        and source.get("p_state_ps2_nonlinear_rotational_mean_value") is True
        and source.get("p_state_ps2_nonlinear_full_mean_value_binding") is True
        and source.get("p_state_ps2_nonlinear_full_ps2") is False
        and source.get("p_state_ps2_nonlinear_pc2_closed") is False
        and p_state_ps2_nonlinear.get("p_state_ps2_nonlinear_binding_recorded") is True,
        "P_state PS2 nonlinear binding audit not linked into closure plan",
    )
    checks.check(
        source.get("p_state_ps2_aggregate_schema")
        == "d5-p-state-ps2-aggregate-promotion-audit-v1"
        and p_state_ps2_aggregate.get("schema") == "d5-p-state-ps2-aggregate-promotion-audit-v1",
        "P_state PS2 aggregate audit not linked into closure plan",
    )
    checks.check(
        source.get("p_state_ps2_aggregate_promotion_recorded") is True
        and p_state_ps2_aggregate.get("p_state_ps2_aggregate_promotion_recorded") is True,
        "P_state PS2 aggregate promotion not linked into closure plan",
    )
    checks.check(
        source.get("p_state_ps2_aggregate_weighted_inverse_certified") is True
        and p_state_ps2_aggregate.get("certifies_aggregate_weighted_ps2_inverse") is True,
        "P_state PS2 aggregate inverse not linked into closure plan",
    )
    checks.check(
        source.get("p_state_ps2_aggregate_uniform_constant_certified") is True
        and p_state_ps2_aggregate.get("certifies_uniform_ps2_constant") is True,
        "P_state PS2 aggregate constant not linked into closure plan",
    )
    checks.check(
        source.get("p_state_ps2_aggregate_inverse_or_infsup_closed") is True
        and p_state_ps2_aggregate.get("ps2_inverse_or_infsup_closed") is True,
        "P_state PS2 aggregate inf-sup not linked into closure plan",
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
        source.get("p_state_ps2_linearization_probe_schema") == "d5-p-state-ps2-linearization-probe-v1"
        and source.get("p_state_ps2_linearization_probe_recorded") is True
        and source.get("p_state_ps2_linearization_probe_full_column_rank_all") is True
        and source.get("p_state_ps2_linearization_probe_uniform_constant_proved") is False
        and source.get("p_state_ps2_linearization_probe_pc2_closed") is False
        and p_state_ps2_probe.get("ps2_weighted_linearization_probe_recorded") is True,
        "P_state PS2 linearization probe not linked into closure plan",
    )
    checks.check(
        source.get("p_state_ps3_conditional_conversion_schema")
        == "d5-p-state-ps3-conditional-conversion-audit-v1"
        and source.get("p_state_ps3_conditional_conversion_closed") is True
        and source.get("p_state_ps3_actual_conversion_closed") is False
        and source.get("p_state_ps3_conditional_conversion_pc2_closed") is False
        and p_state_ps3_conversion.get("ps3_conditional_conversion_closed") is True,
        "P_state PS3 conditional conversion audit not linked into closure plan",
    )
    checks.check(
        source.get("p_state_ps3_actual_gap_schema")
        == "d5-p-state-ps3-actual-instantiation-gap-audit-v1"
        and source.get("p_state_ps3_actual_gap_recorded") is True
        and source.get("p_state_ps3_actual_gap_inputs_closed") == 2
        and source.get("p_state_ps3_actual_gap_inputs_total") == 4
        and source.get("p_state_ps3_actual_gap_h_input_closed") is False
        and source.get("p_state_ps3_actual_gap_pc2_closed") is False
        and p_state_ps3_actual_gap.get("ps3_actual_state_lift_conversion_closed") is False,
        "P_state PS3 actual-instantiation gap audit not linked into closure plan",
    )
    checks.check(
        source.get("p_acc_map_definition_schema") == "d5-p-acc-map-definition-audit-v1"
        and source.get("p_acc_map_definition_closed") is True
        and source.get("p_acc_map_definition_primitive_closed") is False
        and source.get("p_acc_map_definition_pc2_closed") is False
        and p_acc_map_definition.get("pa1_map_definition_closed") is True,
        "P_acc map-definition audit not linked into closure plan",
    )
    checks.check(
        source.get("p_acc_row_binding_schema") == "d5-p-acc-row-binding-audit-v1"
        and source.get("p_acc_row_binding_closed") is True
        and source.get("p_acc_row_binding_primitive_closed") is False
        and source.get("p_acc_row_binding_pc2_closed") is False
        and p_acc_row_binding.get("pa4_row_binding_closed") is True,
        "P_acc row-binding audit not linked into closure plan",
    )
    checks.check(
        source.get("p_acc_independence_schema") == "d5-p-acc-independence-audit-v1"
        and source.get("p_acc_independence_closed") is True
        and source.get("p_acc_independence_primitive_closed") is False
        and source.get("p_acc_independence_pc2_closed") is False
        and p_acc_independence.get("pa3_independence_closed") is True,
        "P_acc independence audit not linked into closure plan",
    )
    checks.check(
        source.get("p_lambda_interface_schema") == "d5-p-lambda-interface-audit-v1"
        and source.get("p_lambda_interface_closed") is True
        and source.get("p_lambda_interface_primitive_closed") is False
        and source.get("p_lambda_interface_pc2_closed") is False
        and p_lambda_interface.get("pl1_interface_closed") is True,
        "P_lambda interface audit not linked into closure plan",
    )
    checks.check(
        source.get("p_geom_reduction_audit_schema") == "d5-p-geom-chart-reduction-audit-v1"
        and source.get("p_geom_chart_reduction_closed") is True
        and source.get("p_geom_primitive_closed") is False
        and p_geom_reduction.get("chart_reduction_closed") is True
        and p_geom_reduction.get("primitive_closed") is False,
        "P_geom chart reduction audit not linked into closure plan",
    )
    checks.check(
        source.get("p_gyro_reduction_audit_schema") == "d5-p-gyro-bilinear-reduction-audit-v1"
        and source.get("p_gyro_algebraic_reduction_closed") is True
        and source.get("p_gyro_primitive_closed") is False
        and p_gyro_reduction.get("algebraic_reduction_closed") is True
        and p_gyro_reduction.get("primitive_closed") is False,
        "P_gyro bilinear reduction audit not linked into closure plan",
    )
    checks.check(source.get("term_budget_pc2_closed") is False, "term budget closes PC2")
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
    checks.check(
        proof_manifest.get("closure_state", {}).get("primitive_lift_route_closed") is False,
        "proof manifest unexpectedly closes primitive lift route",
    )
    checks.check(primitive_reduction.get("pc2_closed") is False, "primitive reduction unexpectedly closes PC2")
    checks.check(term_budget.get("pc2_closed") is False, "term budget unexpectedly closes PC2")
    checks.check(isinstance(rows, list) and len(rows) == 6, "primitive closure plan row count changed")
    expected_order = ["P_tube", "P_state", "P_acc", "P_lambda", "P_geom", "P_gyro"]
    checks.check([row.get("plan_id") for row in rows] == expected_order, "primitive closure order changed")
    for row in rows:
        if not isinstance(row, dict):
            checks.check(False, "plan row is not an object")
            continue
        if row.get("plan_id") == "P_tube":
            checks.check(row.get("proved") is True, "P_tube not recorded as proved")
            checks.check(row.get("proof_artifact_present") is True, "P_tube proof artifact missing")
            checks.check(
                row.get("closure_mode") == "closed_by_regular_compact_tube_lemma",
                "P_tube closure mode changed",
            )
        else:
            checks.check(row.get("proved") is False, f"non-tube primitive unexpectedly proved: {row.get('plan_id')}")
            checks.check(row.get("proof_artifact_present") is False, "open primitive proof artifact unexpectedly present")
            checks.check(row.get("closure_mode") == "open_lift_or_bilinear_bound", "open primitive mode changed")
            checks.check(
                row.get("conditional_reduction_artifact_present") is (row.get("plan_id") in {"P_geom", "P_gyro"}),
                f"conditional reduction artifact flag changed for {row.get('plan_id')}",
            )
            if row.get("plan_id") == "P_state":
                checks.check(row.get("gap_audit_present") is True, "P_state gap audit missing from plan")
                checks.check(
                    "closed P_state map definition audit" in row.get("existing_inputs", []),
                    "P_state map-definition input missing",
                )
                checks.check(
                    "closed P_state anti-circularity audit" in row.get("existing_inputs", []),
                    "P_state anti-circularity input missing",
                )
                checks.check(
                    "closed P_state PS2 weighted target audit" in row.get("existing_inputs", []),
                    "P_state PS2 weighted target input missing",
                )
                checks.check(
                    "recorded P_state PS2 kinematic-block certificate" in row.get("existing_inputs", []),
                    "P_state PS2 kinematic-block input missing",
                )
                checks.check(
                    "recorded P_state PS2 Lie-chart binding audit" in row.get("existing_inputs", []),
                    "P_state PS2 Lie-chart binding input missing",
                )
                checks.check(
                    "recorded P_state PS2 row-injection audit" in row.get("existing_inputs", []),
                    "P_state PS2 row-injection input missing",
                )
                checks.check(
                    "recorded P_state PS2 nonlinear binding audit" in row.get("existing_inputs", []),
                    "P_state PS2 nonlinear binding input missing",
                )
                checks.check(
                    "closed P_state PS2 aggregate promotion audit" in row.get("existing_inputs", []),
                    "P_state PS2 aggregate input missing",
                )
                checks.check(
                    "finite PS2 weighted linearization probe audit" in row.get("existing_inputs", []),
                    "P_state finite PS2 linearization probe input missing",
                )
                checks.check(
                    "closed P_state PS3 conditional conversion audit" in row.get("existing_inputs", []),
                    "P_state PS3 conditional conversion input missing",
                )
                checks.check(
                    "recorded P_state PS3 actual-instantiation gap audit" in row.get("existing_inputs", []),
                    "P_state PS3 actual-instantiation gap input missing",
                )
            elif row.get("plan_id") == "P_acc":
                checks.check(row.get("gap_audit_present") is False, "unexpected gap audit marker on P_acc row")
                checks.check(row.get("interface_audit_present") is False, "unexpected interface marker on P_acc row")
                checks.check(
                    "closed P_acc map definition audit" in row.get("existing_inputs", []),
                    "P_acc map-definition input missing",
                )
                checks.check(
                    "closed P_acc row binding audit" in row.get("existing_inputs", []),
                    "P_acc row-binding input missing",
                )
                checks.check(
                    "closed P_acc independence audit" in row.get("existing_inputs", []),
                    "P_acc independence input missing",
                )
            elif row.get("plan_id") == "P_lambda":
                checks.check(row.get("gap_audit_present") is False, "unexpected gap audit marker on P_lambda row")
                checks.check(row.get("interface_audit_present") is True, "P_lambda interface audit missing from plan")
                checks.check(
                    "closed P_lambda interface audit" in row.get("existing_inputs", []),
                    "P_lambda interface input missing",
                )
            else:
                checks.check(row.get("gap_audit_present") is False, "unexpected gap audit marker on non-P_state row")
                checks.check(row.get("interface_audit_present") is False, "unexpected interface marker on non-P_lambda row")
            if row.get("plan_id") == "P_geom":
                checks.check(
                    "closed P_geom chart reduction audit" in row.get("existing_inputs", []),
                    "P_geom closed reduction input missing",
                )
                checks.check("still-open P_state" in row.get("missing_proof", ""), "P_geom P_state dependency missing")
                checks.check("P_lambda multiplier lift" in row.get("missing_proof", ""), "P_geom P_lambda dependency missing")
            if row.get("plan_id") == "P_gyro":
                checks.check(
                    "closed P_gyro bilinear reduction audit" in row.get("existing_inputs", []),
                    "P_gyro closed reduction input missing",
                )
                checks.check("still-open P_state" in row.get("missing_proof", ""), "P_gyro P_state dependency missing")
        checks.check(row.get("certifies_pc2_now") is False, "row unexpectedly certifies PC2")
        checks.check(int(row.get("term_rows_using_obligation", 0)) > 0, "plan row has no term rows")
        expected_inputs = (
            6
            if row.get("plan_id") == "P_acc"
            else 4
            if row.get("plan_id") in {"P_lambda", "P_geom", "P_gyro"}
            else 14
            if row.get("plan_id") == "P_state"
            else 3
        )
        checks.check(len(row.get("existing_inputs", [])) == expected_inputs, "plan row existing-input count changed")
        checks.check(isinstance(row.get("missing_proof"), str) and row.get("missing_proof"), "missing proof absent")

    for token in [
        "Status: **closure plan recorded; primitive-and-Taylor PC2 route remains open**.",
        "Primitive obligations: `6`.",
        "Primitive obligations with closure steps: `6/6`.",
        "Primitive obligations proved: `1/6`.",
        "Open primitive obligations: `5/6`.",
        "P_tube compact constants closed: `True`.",
        "P_state map definition closed: `True`.",
        "P_state anti-circularity closed: `True`.",
        "P_state PS2 weighted target specified: `True`.",
        "P_state PS2 kinematic-block certificate recorded/subblock/full-PS2: `True` / `True` / `False`.",
        "P_state PS2 Lie-chart binding recorded/SO3/full-mean: `True` / `True` / `False`.",
        "P_state PS2 row injection recorded/72-to-96/scaling/full-mean: `True` / `True` / `True` / `False`.",
        "P_state PS2 nonlinear binding recorded/rot-mean/full-mean/full-PS2: `True` / `True` / `True` / `False`.",
        "P_state PS2 aggregate promotion recorded/inverse/uniform/P_state/PC2: `True` / `True` / `True` / `False` / `False`.",
        "P_state finite PS2 linearization probe recorded/full-rank: `True` / `True`.",
        "P_state finite PS2 probe uniform constant proved: `False`.",
        "P_state PS3 conditional conversion recorded: `True`.",
        "P_state PS3 actual-instantiation gap inputs/h-input/PC2: `2`-`4` / `False` / `False`.",
        "P_acc map definition closed: `True`.",
        "P_acc row binding closed: `True`.",
        "P_acc independence closed: `True`.",
        "P_lambda interface closed: `True`.",
        "P_geom conditional chart reduction recorded; primitive remains open: `True`.",
        "P_gyro conditional bilinear reduction recorded; primitive remains open: `True`.",
        "Taylor subterms with reduction rules: `162/162`.",
        "Induced Taylor bounds proved: `0/162`.",
        "Primitive/Taylor PC2 route closed: `False`.",
        "The compact-tube primitive obligation is proved.",
        "The P_state map definition, PS2 weighted target, PS2 aggregate promotion, finite PS2 linearization probe, PS3 conditional conversion, PS3 actual-instantiation gap, and anti-circularity subproof are recorded, but actual PS3 state-lift instantiation remains open.",
        "The P_acc map definition, row binding, and independence subproof are closed, but the acceleration lift proof remains open.",
        "The P_lambda interface, PL2 inf-sup, PL3 non-circularity, and conditional PL4 propagation are recorded, but the actual multiplier lift remains open until P_state and P_acc close.",
        "The P_geom chart reduction is recorded only as a conditional reduction under P_state and P_lambda; P_geom itself remains open.",
        "The P_gyro bilinear reduction is recorded only as a conditional reduction under P_state; P_gyro itself remains open.",
        "Five lift and bilinear primitive obligations remain open.",
        "Zero induced Taylor bounds are certified.",
        "Primitive/Taylor PC2 route remains open.",
    ]:
        checks.check(token in plan_md, f"markdown missing token: {token}")

    if checks.errors:
        print("D5 primitive-obligation closure plan validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("D5 primitive-obligation closure plan validation: PASS")
    print("primitive_obligations_proved=1/6")
    print("induced_taylor_bounds_proved=0/162")
    print("pc2_closed=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
