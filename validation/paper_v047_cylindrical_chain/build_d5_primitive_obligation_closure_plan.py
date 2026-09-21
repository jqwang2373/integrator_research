#!/usr/bin/env python3
"""Build the D5 primitive-obligation closure plan.

The plan records the proof interfaces needed after the primitive-bound
reduction. It does not prove the primitive bounds or close the primitive/Taylor PC2 route.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
from paper_paths import LATEX, package_path as manuscript_path
OUT_JSON = PAPER / "D5_PRIMITIVE_OBLIGATION_CLOSURE_PLAN.json"
OUT_MD = PAPER / "D5_PRIMITIVE_OBLIGATION_CLOSURE_PLAN.md"


OBLIGATION_PLAN = [
    {
        "plan_id": "P_tube",
        "primitive_id": "P_uniform_tube_constants",
        "close_order": 1,
        "lemma_interface": "compact smooth proof-tube constants are uniform for all D5 row maps",
        "existing_inputs": [
            "regular smooth FullVA lift contract",
            "D4 smooth force/friction branch statement",
            "D6 row ordering and unweighted scaling audit",
        ],
        "missing_proof": (
            "derive one compact tube containing the lifted Gauss stages and bound all "
            "Taylor constants for force, friction, geometry, and gyroscopic maps"
        ),
    },
    {
        "plan_id": "P_state",
        "primitive_id": "P_state_lift",
        "close_order": 2,
        "lemma_interface": "stage pose, translational velocity, and angular velocity lifts are O(h^7)",
        "existing_inputs": [
            "closed P_state map definition audit",
            "closed P_state anti-circularity audit",
            "closed P_state PS2 weighted target audit",
            "recorded P_state PS2 kinematic-block certificate",
            "recorded P_state PS2 Lie-chart binding audit",
            "recorded P_state PS2 row-injection audit",
            "recorded P_state PS2 nonlinear binding audit",
            "closed P_state PS2 aggregate promotion audit",
            "finite PS2 weighted linearization probe audit",
            "closed P_state PS3 conditional conversion audit",
            "recorded P_state PS3 actual-instantiation gap audit",
            "three-stage Gauss smooth reduced path",
            "96-row non-dynamic FullVA lift certificate",
            "endpoint closure perturbation condition",
        ],
        "missing_proof": (
            "connect the smooth reduced Gauss stage variables to the accepted Lie-chart "
            "pose and velocity variables with uniform O(h^7) lift bounds"
        ),
    },
    {
        "plan_id": "P_acc",
        "primitive_id": "P_acceleration_lift",
        "close_order": 3,
        "lemma_interface": "stage translational and angular acceleration lifts are O(h^7)",
        "existing_inputs": [
            "closed P_acc map definition audit",
            "closed P_acc row binding audit",
            "closed P_acc independence audit",
            "velocity collocation rows",
            "smooth reduced acceleration path",
            "regular FullVA acceleration-level constraints",
        ],
        "missing_proof": (
            "differentiate the smooth lift in the accepted variables and show the stage "
            "acceleration variables inherit the O(h^7) lift error"
        ),
    },
    {
        "plan_id": "P_lambda",
        "primitive_id": "P_multiplier_lift",
        "close_order": 4,
        "lemma_interface": "lower-pair multiplier lifts are O(h^7)",
        "existing_inputs": [
            "closed P_lambda interface audit",
            "D3 multiplier wrench consistency",
            "regular lower-pair constraint Jacobian",
            "stage Jacobian invertibility condition",
        ],
        "missing_proof": (
            "use the regular KKT or constrained Newton-Euler linearization to bound "
            "multiplier lift error uniformly across all stages and joints"
        ),
    },
    {
        "plan_id": "P_geom",
        "primitive_id": "P_geometry_lift",
        "close_order": 5,
        "lemma_interface": "dynamic-row force and torque Jacobian geometry lifts are O(h^7)",
        "existing_inputs": [
            "closed P_geom chart reduction audit",
            "D1/D2 balance identities",
            "D3 virtual-work wrench identity",
            "D6 row binding and accepted AD path",
        ],
        "missing_proof": (
            "combine the closed chart reduction with the still-open P_state pose lift "
            "and P_lambda multiplier lift and certify the induced geometry row terms"
        ),
    },
    {
        "plan_id": "P_gyro",
        "primitive_id": "P_gyroscopic_lift",
        "close_order": 6,
        "lemma_interface": "body-frame gyroscopic bilinear lift is O(h^7)",
        "existing_inputs": [
            "closed P_gyro bilinear reduction audit",
            "state angular-velocity lift",
            "constant body inertia",
            "uniform compact-tube velocity bound",
        ],
        "missing_proof": (
            "combine the closed bilinear reduction with the still-open P_state "
            "angular-velocity lift and certify the induced gyroscopic row terms"
        ),
    },
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


def main() -> None:
    primitive_reduction = read_json(PAPER / "D5_PRIMITIVE_BOUND_REDUCTION_AUDIT.json")
    term_budget = read_json(PAPER / "D5_TAYLOR_TERM_BUDGET_AUDIT.json")
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
    proof_manifest = read_json(PAPER / "PROOF_CLOSURE_MANIFEST.json")
    main_tex = read_text(LATEX / "main_cmame.tex")
    flat_tex = read_text(LATEX / "cmame_submission_flat" / "main_cmame_submission.tex")

    primitive_rows = {
        row.get("id"): row
        for row in primitive_reduction.get("primitive_obligations", [])
        if isinstance(row, dict)
    }
    plan_rows: list[dict[str, Any]] = []
    for row in OBLIGATION_PLAN:
        primitive = primitive_rows.get(row["primitive_id"], {})
        is_p_tube = row["plan_id"] == "P_tube"
        is_p_state = row["plan_id"] == "P_state"
        is_p_lambda = row["plan_id"] == "P_lambda"
        is_p_geom = row["plan_id"] == "P_geom"
        is_p_gyro = row["plan_id"] == "P_gyro"
        plan_rows.append(
            {
                **row,
                "term_rows_using_obligation": primitive.get("term_rows_using_obligation"),
                "proved": is_p_tube,
                "proof_artifact_present": is_p_tube,
                "conditional_reduction_artifact_present": (
                    (is_p_geom and p_geom_reduction.get("chart_reduction_closed") is True)
                    or (is_p_gyro and p_gyro_reduction.get("algebraic_reduction_closed") is True)
                ),
                "closure_mode": (
                    p_tube_audit.get("closure_mode") if is_p_tube else "open_lift_or_bilinear_bound"
                ),
                "gap_audit_present": is_p_state and p_state_gap.get("status") == "p_state_lift_gap_recorded_pc2_open",
                "interface_audit_present": is_p_lambda
                and p_lambda_interface.get("status") == "p_lambda_interface_closed_lift_open",
                "certifies_pc2_now": False,
            }
        )

    manuscript_tokens = [
        "Conditional primitive Taylor implication criterion (non-closure)",
        "Conditional primitive-obligation implication for D5 (non-closure)",
        "This separate primitive-route lemma is a conditional finite implication",
        "five primitive obligations are proved separately",
        "not an accepted primitive-route closure",
        "not a PC2 input",
        "does not close the primitive-and-Taylor route to PC2",
    ]
    primitive_proved = sum(1 for row in plan_rows if row.get("proved") is True)
    result = {
        "schema": "d5-primitive-obligation-closure-plan-v1",
        "status": "primitive_obligation_closure_plan_recorded_primitive_taylor_pc2_open",
        "read_only": True,
        "run_v047_invoked": False,
        "submission_ready": False,
        "pc2_closed": False,
        "pc2_closed_scope": "false only for the separate primitive/Taylor PC2 route; active direct PC2 residual-bridge slot is closed separately",
        "primitive_route_pc2_closed": False,
        "proof_gap_closed": False,
        "proof_gap_closed_scope": "false only for the separate primitive/Taylor proof gap; active direct PC2 residual-bridge proof-gap slot is closed separately",
        "primitive_route_proof_gap_closed": False,
        "primitive_bounds_proved": False,
        "primitive_bounds_closed_count": primitive_proved,
        "induced_taylor_bounds_proved": False,
        "summary": {
            "primitive_obligation_count": len(plan_rows),
            "primitive_obligations_with_closure_steps": len(plan_rows),
            "primitive_obligations_proved": primitive_proved,
            "open_primitive_obligations": len(plan_rows) - primitive_proved,
            "closure_step_count": sum(len(row["existing_inputs"]) for row in plan_rows),
            "term_rows": primitive_reduction.get("summary", {}).get("term_rows"),
            "term_rows_with_reduction_rule": primitive_reduction.get("summary", {}).get(
                "term_rows_with_reduction_rule"
            ),
            "induced_taylor_bounds_proved": 0,
            "p_tube_closed": p_tube_audit.get("primitive_closed"),
        },
        "conditional_implication": {
            "lemma_label": "lem:d5-primitive-obligation-implication",
            "implication_recorded_in_manuscript": all(
                contains_normalized(main_tex, token) for token in manuscript_tokens
            ),
            "main_tex_present": all(contains_normalized(main_tex, token) for token in manuscript_tokens),
            "flat_tex_present": all(contains_normalized(flat_tex, token) for token in manuscript_tokens),
            "tokens": manuscript_tokens,
            "claim": (
                "If P_tube and the five remaining primitive obligations are proved uniformly, the recorded "
                "finite reduction map implies all 162 D5 Taylor subterms are O(h^7)."
            ),
            "does_not_prove_remaining_primitives": True,
            "does_not_close_pc2": True,
        },
        "source_consistency": {
            "primitive_reduction_schema": primitive_reduction.get("schema"),
            "primitive_reduction_pc2_closed": primitive_reduction.get("pc2_closed"),
            "primitive_reduction_terms": primitive_reduction.get("summary", {}).get("term_rows"),
            "p_tube_audit_schema": p_tube_audit.get("schema"),
            "p_tube_closed": p_tube_audit.get("primitive_closed"),
            "p_tube_pc2_closed": p_tube_audit.get("pc2_closed"),
            "p_state_gap_audit_schema": p_state_gap.get("schema"),
            "p_state_gap_recorded": p_state_gap.get("status") == "p_state_lift_gap_recorded_pc2_open",
            "p_state_closed": p_state_gap.get("primitive_closed"),
            "p_state_pc2_closed": p_state_gap.get("pc2_closed"),
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
            "p_state_ps2_kinematic_subblock_bound_certified": p_state_ps2_kinematic.get(
                "certifies_uniform_euclidean_kinematic_subblock_bound"
            ),
            "p_state_ps2_kinematic_full_nonlinear_ps2_certified": p_state_ps2_kinematic.get(
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
            "p_acc_map_definition_schema": p_acc_map_definition.get("schema"),
            "p_acc_map_definition_closed": p_acc_map_definition.get("pa1_map_definition_closed"),
            "p_acc_map_definition_primitive_closed": p_acc_map_definition.get("primitive_closed"),
            "p_acc_map_definition_pc2_closed": p_acc_map_definition.get("pc2_closed"),
            "p_acc_row_binding_schema": p_acc_row_binding.get("schema"),
            "p_acc_row_binding_closed": p_acc_row_binding.get("pa4_row_binding_closed"),
            "p_acc_row_binding_primitive_closed": p_acc_row_binding.get("primitive_closed"),
            "p_acc_row_binding_pc2_closed": p_acc_row_binding.get("pc2_closed"),
            "p_acc_independence_schema": p_acc_independence.get("schema"),
            "p_acc_independence_closed": p_acc_independence.get("pa3_independence_closed"),
            "p_acc_independence_primitive_closed": p_acc_independence.get("primitive_closed"),
            "p_acc_independence_pc2_closed": p_acc_independence.get("pc2_closed"),
            "p_lambda_interface_schema": p_lambda_interface.get("schema"),
            "p_lambda_interface_closed": p_lambda_interface.get("pl1_interface_closed"),
            "p_lambda_interface_primitive_closed": p_lambda_interface.get("primitive_closed"),
            "p_lambda_interface_pc2_closed": p_lambda_interface.get("pc2_closed"),
            "p_geom_reduction_audit_schema": p_geom_reduction.get("schema"),
            "p_geom_chart_reduction_closed": p_geom_reduction.get("chart_reduction_closed"),
            "p_geom_primitive_closed": p_geom_reduction.get("primitive_closed"),
            "p_gyro_reduction_audit_schema": p_gyro_reduction.get("schema"),
            "p_gyro_algebraic_reduction_closed": p_gyro_reduction.get("algebraic_reduction_closed"),
            "p_gyro_primitive_closed": p_gyro_reduction.get("primitive_closed"),
            "term_budget_schema": term_budget.get("schema"),
            "term_budget_pc2_closed": term_budget.get("pc2_closed"),
            "proof_manifest_proof_gap_closed": proof_manifest.get("closure_state", {}).get("proof_gap_closed"),
            "proof_manifest_direct_route_gap_closed": proof_manifest.get("closure_state", {}).get(
                "direct_pc2_proof_gap_closed"
            ),
            "proof_manifest_proof_gap_closed_scope": proof_manifest.get("closure_state", {}).get(
                "proof_gap_closed_scope"
            ),
        },
        "primitive_obligation_plan": plan_rows,
        "claim_boundary": {
            "allowed_now": "conditional implication plan from six primitive obligations to 162 D5 term bounds",
            "forbidden_now": [
                "all primitive bounds proved",
                "Taylor term bounds certified",
                "primitive/Taylor PC2 route closure",
                "O(h^7) Newton-Euler dynamic-row proof closure",
                "submission-ready proof",
            ],
            "close_condition": (
                "Primitive/Taylor PC2 lane closes only after the six primitive obligations have independent "
                "uniform proofs and the induced 162 Taylor bounds are certified."
            ),
        },
    }

    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# D5 Primitive-Obligation Closure Plan",
        "",
        "Status: **closure plan recorded; primitive-and-Taylor PC2 route remains open**.",
        "",
        "This read-only plan records the six proof interfaces that remain after",
        "the D5 primitive-bound reduction. It records template coverage only:",
        "the conditional implication from primitive obligations to D5 Taylor bounds",
        "has no current primitive-route Taylor-bound instance. The compact-tube",
        "primitive is closed, but the five lift and bilinear primitives and",
        "all induced Taylor term bounds remain open (`0/162` actual primitive",
        "Taylor bounds certified).",
        "",
        "## Summary",
        "",
        f"- Primitive obligations: `{result['summary']['primitive_obligation_count']}`.",
        f"- Primitive obligations with closure steps: `{result['summary']['primitive_obligations_with_closure_steps']}/6`.",
        f"- Primitive obligations proved: `{result['summary']['primitive_obligations_proved']}/6`.",
        f"- Open primitive obligations: `{result['summary']['open_primitive_obligations']}/6`.",
        f"- P_tube compact constants closed: `{result['summary']['p_tube_closed']}`.",
        f"- P_state map definition closed: `{p_state_map_definition.get('ps1_map_definition_closed')}`.",
        f"- P_state anti-circularity closed: `{p_state_anticircularity.get('ps4_anticircularity_closed')}`.",
        f"- P_state PS2 weighted target specified: `{p_state_ps2_target.get('ps2_target_spec_closed')}`.",
        f"- P_state PS2 kinematic-block certificate recorded/subblock/full-PS2: `{p_state_ps2_kinematic.get('ps2_kinematic_block_certificate_recorded')}` / `{p_state_ps2_kinematic.get('certifies_uniform_euclidean_kinematic_subblock_bound')}` / `{p_state_ps2_kinematic.get('certifies_full_nonlinear_ps2')}`.",
        f"- P_state PS2 Lie-chart binding recorded/SO3/full-mean: `{p_state_ps2_lie_chart.get('p_state_ps2_lie_chart_binding_recorded')}` / `{p_state_ps2_lie_chart.get('certifies_so3_chart_norm_equivalence')}` / `{p_state_ps2_lie_chart.get('certifies_full_nonlinear_mean_value_binding')}`.",
        f"- P_state PS2 row injection recorded/72-to-96/scaling/full-mean: `{p_state_ps2_row_injection.get('p_state_ps2_row_injection_recorded')}` / `{p_state_ps2_row_injection.get('certifies_72_to_96_row_injection')}` / `{p_state_ps2_row_injection.get('certifies_unweighted_residual_scaling')}` / `{p_state_ps2_row_injection.get('certifies_full_nonlinear_mean_value_binding')}`.",
        f"- P_state PS2 nonlinear binding recorded/rot-mean/full-mean/full-PS2: `{p_state_ps2_nonlinear.get('p_state_ps2_nonlinear_binding_recorded')}` / `{p_state_ps2_nonlinear.get('certifies_rotational_lie_row_mean_value_binding')}` / `{p_state_ps2_nonlinear.get('certifies_full_nonlinear_mean_value_binding')}` / `{p_state_ps2_nonlinear.get('certifies_full_nonlinear_ps2')}`.",
        f"- P_state PS2 aggregate promotion recorded/inverse/uniform/P_state/PC2: `{p_state_ps2_aggregate.get('p_state_ps2_aggregate_promotion_recorded')}` / `{p_state_ps2_aggregate.get('certifies_aggregate_weighted_ps2_inverse')}` / `{p_state_ps2_aggregate.get('certifies_uniform_ps2_constant')}` / `{p_state_ps2_aggregate.get('primitive_closed')}` / `{p_state_ps2_aggregate.get('pc2_closed')}`.",
        f"- P_state finite PS2 linearization probe recorded/full-rank: `{p_state_ps2_probe.get('ps2_weighted_linearization_probe_recorded')}` / `{p_state_ps2_probe.get('summary', {}).get('finite_probe_full_column_rank_all')}`.",
        f"- P_state finite PS2 probe uniform constant proved: `{p_state_ps2_probe.get('uniform_constant_proved')}`.",
        f"- P_state PS3 conditional conversion recorded: `{p_state_ps3_conversion.get('ps3_conditional_conversion_closed')}`.",
        f"- P_state PS3 actual-instantiation gap inputs/h-input/PC2: `{p_state_ps3_actual_gap.get('summary', {}).get('input_requirements_closed')}`-`{p_state_ps3_actual_gap.get('summary', {}).get('input_requirements_total')}` / `{p_state_ps3_actual_gap.get('summary', {}).get('independent_h_weighted_acceleration_input_closed')}` / `{p_state_ps3_actual_gap.get('pc2_closed')}`.",
        f"- P_acc map definition closed: `{p_acc_map_definition.get('pa1_map_definition_closed')}`.",
        f"- P_acc row binding closed: `{p_acc_row_binding.get('pa4_row_binding_closed')}`.",
        f"- P_acc independence closed: `{p_acc_independence.get('pa3_independence_closed')}`.",
        f"- P_lambda interface closed: `{p_lambda_interface.get('pl1_interface_closed')}`.",
        f"- P_geom conditional chart reduction recorded; primitive remains open: `{p_geom_reduction.get('chart_reduction_closed')}`.",
        f"- P_gyro conditional bilinear reduction recorded; primitive remains open: `{p_gyro_reduction.get('algebraic_reduction_closed')}`.",
        f"- Taylor subterms with reduction rules: `{result['summary']['term_rows_with_reduction_rule']}/162`.",
        f"- Induced Taylor bounds proved: `{result['summary']['induced_taylor_bounds_proved']}/162`.",
        f"- Primitive/Taylor PC2 route closed: `{result['pc2_closed']}`.",
        "",
        "## Closure Plan",
        "",
        "| order | plan id | primitive id | term rows | proved | lemma interface |",
        "|---:|---|---|---:|---:|---|",
    ]
    for row in plan_rows:
        lines.append(
            f"| `{row['close_order']}` | `{row['plan_id']}` | `{row['primitive_id']}` | "
            f"`{row['term_rows_using_obligation']}` | `{row['proved']}` | {row['lemma_interface']} |"
        )
    lines.extend(
        [
            "",
            "## Acceptance Boundary",
            "",
            "- The manuscript records the conditional primitive-obligation implication.",
            "- The compact-tube primitive obligation is proved.",
            "- The P_state map definition, PS2 weighted target, PS2 aggregate promotion, finite PS2 linearization probe, PS3 conditional conversion, PS3 actual-instantiation gap, and anti-circularity subproof are recorded, but actual PS3 state-lift instantiation remains open.",
            "- The P_acc map definition, row binding, and independence subproof are closed, but the acceleration lift proof remains open.",
            "- The P_lambda interface, PL2 inf-sup, PL3 non-circularity, and conditional PL4 propagation are recorded, but the actual multiplier lift remains open until P_state and P_acc close.",
            "- The P_geom chart reduction is recorded only as a conditional reduction under P_state and P_lambda; P_geom itself remains open.",
            "- The P_gyro bilinear reduction is recorded only as a conditional reduction under P_state; P_gyro itself remains open.",
            "- Five lift and bilinear primitive obligations remain open.",
            "- Zero induced Taylor bounds are certified.",
            "- Primitive/Taylor PC2 route remains open.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("d5_primitive_obligation_closure_plan=written")
    print("primitive_obligations_proved=1/6")
    print("induced_taylor_bounds_proved=0/162")
    print("pc2_closed=False")


if __name__ == "__main__":
    main()
