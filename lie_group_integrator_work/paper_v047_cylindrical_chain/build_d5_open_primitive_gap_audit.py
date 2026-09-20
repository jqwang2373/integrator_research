#!/usr/bin/env python3
"""Build the D5 open-primitive gap audit.

This audit records the remaining primitive proof interfaces after P_tube has
closed. It also records the closed P_geom and P_gyro algebraic reductions,
while keeping both primitives open because their lift dependencies remain
unproved. It does not close any lift primitive or PC2.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
from paper_paths import LATEX, package_path as manuscript_path
OUT_JSON = PAPER / "D5_OPEN_PRIMITIVE_GAP_AUDIT.json"
OUT_MD = PAPER / "D5_OPEN_PRIMITIVE_GAP_AUDIT.md"


FUTURE_SUBPROOFS = {
    "P_state": [
        "Define the non-dynamic stage map in the accepted Lie chart.",
        "Prove a local inverse or inf-sup bound for the non-dynamic stage map.",
        "Convert the 96-row certificate into O(h^7) pose and velocity lift rates.",
        "Keep the argument independent of the D5 dynamic residual theorem.",
    ],
    "P_acc": [
        "Define accepted acceleration variable and D5 acceleration-lift row map.",
        "Prove that velocity-collocation perturbations imply O(h^7) acceleration lift rates.",
        "Show lower-pair acceleration rows do not rely on the dynamic-balance defect.",
        "Bind translational and angular acceleration variables to the manuscript residual ordering.",
    ],
    "P_lambda": [
        "Write the stage KKT/Newton-Euler linearization with multiplier columns exposed.",
        "Prove a uniform multiplier inf-sup bound on the compact proof tube.",
        "Use D3 wrench consistency without assuming the D5 dynamic residual rate.",
        "Propagate the state and acceleration lift bounds to O(h^7) multiplier rates.",
    ],
    "P_geom": [
        "Expand force, torque, moment-arm, and constraint-Jacobian geometry in the accepted chart.",
        "Apply compact-tube derivative constants plus state and multiplier lift rates.",
        "Check row ordering, scaling, and AD columns against the expanded geometry terms.",
        "Certify the induced O(h^7) geometry contribution for every dynamic component row.",
    ],
    "P_gyro": [
        "Use constant body inertia and compact angular-velocity bounds.",
        "Apply a bilinear difference estimate to omega x J omega.",
        "Bind the estimate to the 18 rotational Newton-Euler rows.",
    ],
}


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


def close_requirement_satisfied(manifest: dict[str, Any], requirement_id: str) -> bool | None:
    for row in manifest.get("close_requirements", []):
        if isinstance(row, dict) and row.get("id") == requirement_id:
            value = row.get("satisfied")
            return value if isinstance(value, bool) else None
    return None


def main() -> None:
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
    main_tex = read_text(LATEX / "main_cmame.tex")
    flat_tex = read_text(LATEX / "cmame_submission_flat" / "main_cmame_submission.tex")

    open_rows = [
        row
        for row in plan.get("primitive_obligation_plan", [])
        if isinstance(row, dict) and row.get("proved") is False
    ]
    open_plan_ids = [row.get("plan_id") for row in open_rows]
    open_interfaces = []
    for row in open_rows:
        plan_id = row["plan_id"]
        subproofs = FUTURE_SUBPROOFS[plan_id]
        geom_reduction_applies = (
            plan_id == "P_geom"
            and p_geom_reduction.get("chart_reduction_closed") is True
            and p_geom_reduction.get("primitive_closed") is False
        )
        gyro_reduction_applies = (
            plan_id == "P_gyro"
            and p_gyro_reduction.get("algebraic_reduction_closed") is True
            and p_gyro_reduction.get("primitive_closed") is False
        )
        conditional_reduction_applies = geom_reduction_applies or gyro_reduction_applies
        if geom_reduction_applies:
            subproofs_closed = 3
            open_dependencies = p_geom_reduction.get("open_dependencies", [])
        elif gyro_reduction_applies:
            subproofs_closed = len(subproofs)
            open_dependencies = p_gyro_reduction.get("open_dependencies", [])
        elif plan_id == "P_state":
            subproofs_closed = int(p_state_gap.get("summary", {}).get("required_future_subproofs_closed", 0))
            open_dependencies = [
                "PS3 actual state lift conversion after conditional implication",
            ]
            ps2_lie_chart_diagnostic = {
                "lie_chart_binding_recorded": p_state_ps2_lie_chart.get(
                    "p_state_ps2_lie_chart_binding_recorded"
                ),
                "so3_chart_norm_equivalence_certified": p_state_ps2_lie_chart.get(
                    "certifies_so3_chart_norm_equivalence"
                ),
                "full_nonlinear_mean_value_binding_certified": p_state_ps2_lie_chart.get(
                    "certifies_full_nonlinear_mean_value_binding"
                ),
                "remaining_binding_gap_count": len(p_state_ps2_lie_chart.get("remaining_binding_gaps", [])),
                "ps2_closed": p_state_ps2_lie_chart.get("ps2_inverse_or_infsup_closed"),
                "pc2_closed": p_state_ps2_lie_chart.get("pc2_closed"),
            }
            ps2_row_injection_diagnostic = {
                "row_injection_recorded": p_state_ps2_row_injection.get(
                    "p_state_ps2_row_injection_recorded"
                ),
                "row_injection_certified": p_state_ps2_row_injection.get(
                    "certifies_72_to_96_row_injection"
                ),
                "unweighted_scaling_certified": p_state_ps2_row_injection.get(
                    "certifies_unweighted_residual_scaling"
                ),
                "full_nonlinear_mean_value_binding_certified": p_state_ps2_row_injection.get(
                    "certifies_full_nonlinear_mean_value_binding"
                ),
                "remaining_binding_gap_count": len(p_state_ps2_row_injection.get("remaining_binding_gaps", [])),
                "ps2_closed": p_state_ps2_row_injection.get("ps2_inverse_or_infsup_closed"),
                "pc2_closed": p_state_ps2_row_injection.get("pc2_closed"),
            }
            ps2_nonlinear_binding_diagnostic = {
                "nonlinear_binding_recorded": p_state_ps2_nonlinear.get(
                    "p_state_ps2_nonlinear_binding_recorded"
                ),
                "rotational_mean_value_binding_certified": p_state_ps2_nonlinear.get(
                    "certifies_rotational_lie_row_mean_value_binding"
                ),
                "full_mean_value_binding_certified": p_state_ps2_nonlinear.get(
                    "certifies_full_nonlinear_mean_value_binding"
                ),
                "full_ps2_certified": p_state_ps2_nonlinear.get("certifies_full_nonlinear_ps2"),
                "remaining_promotion_gap_count": len(
                    p_state_ps2_nonlinear.get("remaining_promotion_gaps", [])
                ),
                "ps2_closed": p_state_ps2_nonlinear.get("ps2_inverse_or_infsup_closed"),
                "pc2_closed": p_state_ps2_nonlinear.get("pc2_closed"),
            }
            ps2_aggregate_promotion_diagnostic = {
                "aggregate_promotion_recorded": p_state_ps2_aggregate.get(
                    "p_state_ps2_aggregate_promotion_recorded"
                ),
                "aggregate_weighted_ps2_inverse_certified": p_state_ps2_aggregate.get(
                    "certifies_aggregate_weighted_ps2_inverse"
                ),
                "uniform_ps2_constant_certified": p_state_ps2_aggregate.get(
                    "certifies_uniform_ps2_constant"
                ),
                "ps2_closed": p_state_ps2_aggregate.get("ps2_inverse_or_infsup_closed"),
                "ps3_actual_conversion_closed": p_state_ps2_aggregate.get(
                    "ps3_actual_state_lift_conversion_closed"
                ),
                "p_state_closed": p_state_ps2_aggregate.get("primitive_closed"),
                "pc2_closed": p_state_ps2_aggregate.get("pc2_closed"),
            }
        elif plan_id == "P_acc":
            subproofs_closed = int(
                p_acc_independence.get("summary", {}).get(
                    "p_acc_closed_subproof_count_after_independence", 0
                )
            )
            open_dependencies = [
                "PA2 velocity-collocation-to-acceleration lift proof",
            ]
            pa2_weighted_inverse_diagnostic = {
                "pa2_weighted_inverse_probe_recorded": p_acc_pa2_weighted_inverse.get(
                    "pa2_weighted_inverse_probe_recorded"
                ),
                "weighted_h_acceleration_control_recorded": p_acc_pa2_weighted_inverse.get(
                    "weighted_h_acceleration_control_recorded"
                ),
                "finite_probe_full_column_rank_all": p_acc_pa2_weighted_inverse.get("summary", {}).get(
                    "finite_probe_full_column_rank_all"
                ),
                "max_unweighted_acceleration_projection_constant": p_acc_pa2_weighted_inverse.get(
                    "summary", {}
                ).get("max_unweighted_acceleration_projection_constant"),
                "max_weighted_h_acceleration_projection_constant": p_acc_pa2_weighted_inverse.get(
                    "summary", {}
                ).get("max_weighted_h_acceleration_projection_constant"),
                "unweighted_acceleration_uniform_control_proved": p_acc_pa2_weighted_inverse.get(
                    "unweighted_acceleration_uniform_control_proved"
                ),
                "pa2_closed": p_acc_pa2_weighted_inverse.get("pa2_closed"),
                "pc2_closed": p_acc_pa2_weighted_inverse.get("pc2_closed"),
            }
        elif plan_id == "P_lambda":
            pl2_closed = p_lambda_pl2_geometric_margin.get("pl2_uniform_inf_sup_bound_proved") is True
            pl4_closed = p_lambda_pl4_rate_propagation.get("pl4_lift_propagation_closed") is True
            subproofs_closed = int(
                p_lambda_d3_noncircularity.get("summary", {}).get(
                    "p_lambda_closed_subproof_count_after_d3", 0
                )
            ) + (1 if pl2_closed else 0) + (1 if pl4_closed else 0)
            if pl4_closed:
                open_dependencies = p_lambda_pl4_rate_propagation.get("open_dependencies", [])
            else:
                open_dependencies = ["PL4 state/acceleration lift propagation to multiplier rate"]
            if not pl2_closed:
                open_dependencies.insert(0, "PL2 uniform multiplier inf-sup bound")
            finite_diagnostic = {
                "p_lambda_inf_sup_probe_recorded": p_lambda_inf_sup_probe.get(
                    "p_lambda_inf_sup_probe_recorded"
                ),
                "finite_probe_full_column_rank_all": p_lambda_inf_sup_probe.get("summary", {}).get(
                    "finite_probe_full_column_rank_all"
                ),
                "min_singular_value_across_probes": p_lambda_inf_sup_probe.get("summary", {}).get(
                    "min_singular_value_across_probes"
                ),
                "max_condition_number_across_probes": p_lambda_inf_sup_probe.get("summary", {}).get(
                    "max_condition_number_across_probes"
                ),
                "uniform_constant_proved": p_lambda_inf_sup_probe.get("uniform_constant_proved"),
                "pc2_closed": p_lambda_inf_sup_probe.get("pc2_closed"),
            }
            noncircularity_diagnostic = {
                "pl3_d3_noncircularity_closed": p_lambda_d3_noncircularity.get(
                    "pl3_d3_noncircularity_closed"
                ),
                "d3_identity_is_algebraic_mapping": p_lambda_d3_noncircularity.get(
                    "d3_non_circularity_gate", {}
                ).get("d3_identity_is_algebraic_mapping"),
                "d3_identity_does_not_assume_dynamic_defect_rate": p_lambda_d3_noncircularity.get(
                    "d3_non_circularity_gate", {}
                ).get("d3_identity_does_not_assume_dynamic_defect_rate"),
                "d3_identity_not_used_as_multiplier_rate": p_lambda_d3_noncircularity.get(
                    "d3_non_circularity_gate", {}
                ).get("d3_identity_not_used_as_multiplier_rate"),
                "pc2_closed": p_lambda_d3_noncircularity.get("pc2_closed"),
            }
            pl2_geometric_margin_diagnostic = {
                "pl2_geometric_margin_route_recorded": p_lambda_pl2_geometric_margin.get(
                    "pl2_geometric_margin_route_recorded"
                ),
                "compact_tube_reduction_recorded": p_lambda_pl2_geometric_margin.get("summary", {}).get(
                    "compact_tube_reduction_recorded"
                ),
                "symbolic_structure_certificate_recorded": p_lambda_pl2_geometric_margin.get("summary", {}).get(
                    "symbolic_structure_certificate_recorded"
                ),
                "normal_force_margin_proved": p_lambda_pl2_geometric_margin.get("summary", {}).get(
                    "normal_force_margin_proved"
                ),
                "smooth_friction_orthogonal_perturbation_proved": p_lambda_pl2_geometric_margin.get(
                    "summary", {}
                ).get("smooth_friction_orthogonal_perturbation_proved"),
                "translational_normal_subblock_lower_bound_proved": p_lambda_pl2_geometric_margin.get(
                    "summary", {}
                ).get("translational_normal_subblock_lower_bound_proved"),
                "axis_plane_margin_certificate_recorded": p_lambda_pl2_geometric_margin.get(
                    "axis_plane_margin_certificate", {}
                ).get("certificate_recorded"),
                "axis_torque_compact_axis_margin_proved": p_lambda_pl2_geometric_margin.get("summary", {}).get(
                    "axis_torque_compact_axis_margin_proved"
                ),
                "symbolic_margin_premise_proved": p_lambda_pl2_geometric_margin.get("summary", {}).get(
                    "symbolic_margin_premise_proved"
                ),
                "compact_tube_reduction_closes_pl2": p_lambda_pl2_geometric_margin.get(
                    "compact_tube_reduction", {}
                ).get("closes_pl2"),
                "finite_probe_sufficient_for_symbolic_margin": p_lambda_pl2_geometric_margin.get(
                    "compact_tube_reduction", {}
                ).get("finite_probe_sufficient_for_symbolic_margin"),
                "finite_full_stage_rank_all": p_lambda_pl2_geometric_margin.get("summary", {}).get(
                    "finite_full_stage_rank_all"
                ),
                "finite_translational_normal_rank_all": p_lambda_pl2_geometric_margin.get("summary", {}).get(
                    "finite_translational_normal_rank_all"
                ),
                "finite_rotational_axis_torque_rank_all": p_lambda_pl2_geometric_margin.get("summary", {}).get(
                    "finite_rotational_axis_torque_rank_all"
                ),
                "uniform_compact_tube_margin_proved": p_lambda_pl2_geometric_margin.get(
                    "uniform_compact_tube_margin_proved"
                ),
                "pl2_uniform_inf_sup_bound_proved": p_lambda_pl2_geometric_margin.get(
                    "pl2_uniform_inf_sup_bound_proved"
                ),
                "pc2_closed": p_lambda_pl2_geometric_margin.get("pc2_closed"),
            }
            pl4_rate_propagation_diagnostic = {
                "pl4_lift_propagation_closed": p_lambda_pl4_rate_propagation.get(
                    "pl4_lift_propagation_closed"
                ),
                "conditional_multiplier_lift_rate_proved": p_lambda_pl4_rate_propagation.get(
                    "conditional_multiplier_lift_rate_proved"
                ),
                "multiplier_lift_rate_proved": p_lambda_pl4_rate_propagation.get(
                    "multiplier_lift_rate_proved"
                ),
                "actual_state_lift_input_closed": p_lambda_pl4_rate_propagation.get(
                    "actual_state_lift_input_closed"
                ),
                "actual_acceleration_lift_input_closed": p_lambda_pl4_rate_propagation.get(
                    "actual_acceleration_lift_input_closed"
                ),
                "uses_first_order_taylor_with_quadratic_remainder": p_lambda_pl4_rate_propagation.get(
                    "proof_certificate", {}
                ).get("uses_first_order_taylor_with_quadratic_remainder"),
                "uses_stage_residual_defect": p_lambda_pl4_rate_propagation.get(
                    "proof_certificate", {}
                ).get("uses_stage_residual_defect"),
                "uses_d5_dynamic_residual_defect": p_lambda_pl4_rate_propagation.get(
                    "proof_certificate", {}
                ).get("uses_d5_dynamic_residual_defect"),
                "uses_direct_substitution_as_proof": p_lambda_pl4_rate_propagation.get(
                    "proof_certificate", {}
                ).get("uses_direct_substitution_as_proof"),
                "uses_finite_probe_as_proof": p_lambda_pl4_rate_propagation.get(
                    "proof_certificate", {}
                ).get("uses_finite_probe_as_proof"),
                "uses_d3_as_rate_proof": p_lambda_pl4_rate_propagation.get("proof_certificate", {}).get(
                    "uses_d3_as_rate_proof"
                ),
                "term_bounds_proved": p_lambda_pl4_rate_propagation.get("term_bounds_proved"),
                "pc2_closed": p_lambda_pl4_rate_propagation.get("pc2_closed"),
            }
        else:
            subproofs_closed = 0
            open_dependencies = []
            finite_diagnostic = None
            noncircularity_diagnostic = None
            pl2_geometric_margin_diagnostic = None
            pa2_weighted_inverse_diagnostic = None
            ps2_lie_chart_diagnostic = None
            ps2_row_injection_diagnostic = None
            ps2_nonlinear_binding_diagnostic = None
            ps2_aggregate_promotion_diagnostic = None
        if plan_id != "P_lambda":
            finite_diagnostic = None
            noncircularity_diagnostic = None
            pl2_geometric_margin_diagnostic = None
            pl4_rate_propagation_diagnostic = None
        if plan_id != "P_acc":
            pa2_weighted_inverse_diagnostic = None
        if plan_id != "P_state":
            ps2_lie_chart_diagnostic = None
            ps2_row_injection_diagnostic = None
            ps2_nonlinear_binding_diagnostic = None
            ps2_aggregate_promotion_diagnostic = None
        open_interfaces.append(
            {
                "plan_id": plan_id,
                "primitive_id": row.get("primitive_id"),
                "term_rows_using_obligation": row.get("term_rows_using_obligation"),
                "lemma_interface": row.get("lemma_interface"),
                "missing_proof": row.get("missing_proof"),
                "future_subproofs": subproofs,
                "future_subproofs_closed": subproofs_closed,
                "primitive_closed": False,
                "conditional_reduction_closed": conditional_reduction_applies,
                "open_dependencies": open_dependencies,
                "finite_diagnostic": finite_diagnostic,
                "noncircularity_diagnostic": noncircularity_diagnostic,
                "pl2_geometric_margin_diagnostic": pl2_geometric_margin_diagnostic,
                "pl4_rate_propagation_diagnostic": pl4_rate_propagation_diagnostic,
                "pa2_weighted_inverse_diagnostic": pa2_weighted_inverse_diagnostic,
                "ps2_lie_chart_diagnostic": ps2_lie_chart_diagnostic,
                "ps2_row_injection_diagnostic": ps2_row_injection_diagnostic,
                "ps2_nonlinear_binding_diagnostic": ps2_nonlinear_binding_diagnostic,
                "ps2_aggregate_promotion_diagnostic": ps2_aggregate_promotion_diagnostic,
                "induced_taylor_bounds_proved": 0,
                "forbidden_shortcuts": [
                    "do not use Lemma stage-residual-defect as an input",
                    "do not assume the D5 dynamic residual defect rate",
                    "do not infer variable-lift rates from residual identity alone",
                ],
            }
        )

    manuscript_tokens = [
        r"\label{tab:d5-open-primitive-proof-interfaces}",
        "Retained primitive proof interfaces for D5",
        r"\(P_{\mathrm{acc}}\)",
        r"\(P_{\lambda}\)",
        r"\(P_{\mathrm{geom}}\)",
        r"\(P_{\mathrm{gyro}}\)",
        "None of the five retained primitive rows is allowed to use",
        r"\label{lem:d5-p-acc-independence}",
        r"\label{lem:d5-p-lambda-interface}",
        r"\label{lem:d5-p-lambda-pl2-axis-plane-margin}",
        r"\label{lem:d5-p-lambda-d3-noncircularity}",
        r"\label{lem:d5-p-lambda-pl4-rate-propagation}",
        r"\label{lem:d5-geom-chart-reduction}",
        r"\label{lem:d5-gyro-bilinear-reduction}",
    ]
    blocker_ledger_tokens = [
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
    conditional_closure_tokens = [
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
    total_future_subproofs = sum(len(row["future_subproofs"]) for row in open_interfaces)
    total_future_subproofs_closed = sum(int(row["future_subproofs_closed"]) for row in open_interfaces)
    term_rows_by_plan = {
        row["plan_id"]: row["term_rows_using_obligation"] for row in open_interfaces
    }
    primitive_dependency_graph = {
        "graph_recorded": True,
        "root_lift_primitives": ["P_state", "P_acc"],
        "root_dependent_primitives": ["P_lambda"],
        "conditional_downstream_primitives": ["P_geom", "P_gyro"],
        "dependency_edges": [
            {
                "source": "P_state",
                "target": "P_lambda",
                "reason": "multiplier-rate proof propagates state lift errors through the constrained Newton-Euler linearization",
            },
            {
                "source": "P_acc",
                "target": "P_lambda",
                "reason": "multiplier-rate proof propagates acceleration lift errors through the constrained Newton-Euler linearization",
            },
            {
                "source": "P_state",
                "target": "P_geom",
                "reason": "accepted-chart multiplier geometry reduction needs the pose lift",
            },
            {
                "source": "P_lambda",
                "target": "P_geom",
                "reason": "accepted-chart multiplier geometry reduction needs the multiplier lift",
            },
            {
                "source": "P_state",
                "target": "P_gyro",
                "reason": "gyroscopic bilinear reduction needs the angular-velocity lift",
            },
        ],
        "closure_sequence": ["P_state", "P_acc", "P_lambda", "P_geom", "P_gyro"],
        "root_lift_term_rows": {
            key: term_rows_by_plan[key] for key in ["P_state", "P_acc"]
        },
        "root_dependent_term_rows": {
            key: term_rows_by_plan[key] for key in ["P_lambda"]
        },
        "conditional_downstream_term_rows": {
            key: term_rows_by_plan[key] for key in ["P_geom", "P_gyro"]
        },
        "root_lift_term_row_total": sum(term_rows_by_plan[key] for key in ["P_state", "P_acc"]),
        "root_dependent_term_row_total": sum(term_rows_by_plan[key] for key in ["P_lambda"]),
        "conditional_downstream_term_row_total": sum(term_rows_by_plan[key] for key in ["P_geom", "P_gyro"]),
        "minimal_next_subproofs": [
            {
                "primitive": "P_state",
                "next_subproof": "PS3 actual state-lift instantiation",
                "blocking_detail": "independent h-weighted acceleration input remains open",
            },
            {
                "primitive": "P_acc",
                "next_subproof": "PA2 unweighted acceleration lift",
                "blocking_detail": "current evidence controls h times acceleration, not the unweighted acceleration error",
            },
            {
                "primitive": "P_lambda",
                "next_subproof": "instantiate PL4 with P_state/P_acc lift inputs",
                "blocking_detail": "PL4 conditional propagation is closed, but the actual state and unweighted acceleration lift inputs remain open",
            },
        ],
        "pc2_closes_only_after_all_open_primitives_close": True,
        "does_not_certify_taylor_bounds": True,
    }
    result = {
        "schema": "d5-open-primitive-gap-audit-v1",
        "status": "open_primitive_gaps_recorded_primitive_taylor_pc2_open",
        "read_only": True,
        "run_v047_invoked": False,
        "submission_ready": False,
        "pc2_closed": False,
        "pc2_closed_scope": "false only for the separate primitive/Taylor PC2 route; active direct PC2 residual-bridge slot is closed separately",
        "primitive_route_pc2_closed": False,
        "proof_gap_closed": False,
        "proof_gap_closed_scope": "false only for the separate primitive/Taylor proof gap; active direct PC2 residual-bridge proof-gap slot is closed separately",
        "primitive_route_proof_gap_closed": False,
        "primitive_bounds_closed_count": plan.get("primitive_bounds_closed_count"),
        "open_primitive_count": len(open_interfaces),
        "open_plan_ids": open_plan_ids,
        "summary": {
            "open_primitive_count": len(open_interfaces),
            "total_future_subproofs": total_future_subproofs,
            "future_subproofs_closed": total_future_subproofs_closed,
            "induced_taylor_bounds_proved": 0,
            "conditional_reductions_closed": sum(
                1
                for reduction_closed in [
                    p_geom_reduction.get("chart_reduction_closed"),
                    p_gyro_reduction.get("algebraic_reduction_closed"),
                ]
                if reduction_closed
            ),
            "term_rows_with_open_primitives": {
                row["plan_id"]: row["term_rows_using_obligation"] for row in open_interfaces
            },
            "primitive_dependency_graph_recorded": primitive_dependency_graph["graph_recorded"],
            "root_lift_primitives": primitive_dependency_graph["root_lift_primitives"],
            "root_dependent_primitives": primitive_dependency_graph["root_dependent_primitives"],
            "conditional_downstream_primitives": primitive_dependency_graph[
                "conditional_downstream_primitives"
            ],
            "dependency_edge_count": len(primitive_dependency_graph["dependency_edges"]),
            "root_lift_term_row_total": primitive_dependency_graph["root_lift_term_row_total"],
            "root_dependent_term_row_total": primitive_dependency_graph[
                "root_dependent_term_row_total"
            ],
            "conditional_downstream_term_row_total": primitive_dependency_graph[
                "conditional_downstream_term_row_total"
            ],
            "p_state_direct_full_residual_route_recorded": p_state_ps3_full_route.get("schema")
            == "d5-p-state-ps3-full-residual-route-certificate-v1",
            "p_state_direct_route_ps3_input_closed": p_state_ps3_full_route.get("summary", {}).get(
                "direct_route_ps3_input_closed"
            ),
            "p_state_direct_route_state_lift_rate_closed": p_state_ps3_full_route.get("summary", {}).get(
                "direct_route_state_lift_rate_closed"
            ),
            "p_state_direct_route_h_weighted_acceleration_input_closed": p_state_ps3_full_route.get(
                "summary", {}
            ).get("direct_route_h_weighted_acceleration_input_closed"),
            "p_state_direct_route_strict_proof_steps_closed": p_state_ps3_full_route.get(
                "summary", {}
            ).get("strict_proof_steps_closed"),
            "p_state_direct_route_strict_proof_steps_total": p_state_ps3_full_route.get(
                "summary", {}
            ).get("strict_proof_steps_total"),
            "p_state_primitive_route_closed_by_direct_corollary": p_state_ps3_full_route.get(
                "summary", {}
            ).get("primitive_route_closed"),
            "p_state_primitive_route_induced_bounds_by_direct_corollary": p_state_ps3_full_route.get(
                "summary", {}
            ).get("primitive_route_induced_taylor_bounds_proved"),
        },
        "primitive_dependency_graph": primitive_dependency_graph,
        "open_primitive_interfaces": open_interfaces,
        "anti_circularity_gate": {
            "stage_residual_perturbation_lemma_disallowed_as_input": True,
            "dynamic_residual_defect_disallowed_as_input": True,
            "residual_identity_alone_disallowed_as_variable_lift_proof": True,
            "finite_numerical_slopes_disallowed_as_symbolic_pc2_closure": True,
        },
        "manuscript_link": {
            "main_tex_present": all(contains_normalized(main_tex, token) for token in manuscript_tokens),
            "flat_tex_present": all(contains_normalized(flat_tex, token) for token in manuscript_tokens),
            "tokens": manuscript_tokens,
        },
        "reader_facing_blocker_ledger": {
            "main_tex_present": all(contains_normalized(main_tex, token) for token in blocker_ledger_tokens),
            "flat_tex_present": all(contains_normalized(flat_tex, token) for token in blocker_ledger_tokens),
            "tokens": blocker_ledger_tokens,
            "preserves_zero_actual_bounds": (
                contains_normalized(
                    main_tex,
                    "no actual D5 primitive Taylor bound from this route is invoked by the theorem",
                )
                and contains_normalized(
                    flat_tex,
                    "no actual D5 primitive Taylor bound from this route is invoked by the theorem",
                )
            ),
            "preserves_primitive_route_open_token": (
                contains_normalized(main_tex, "This separate primitive-route lemma is a conditional finite implication")
                and contains_normalized(flat_tex, "This separate primitive-route lemma is a conditional finite implication")
            ),
            "does_not_promote_direct_route": (
                contains_normalized(
                    main_tex,
                    "The direct full-residual route corollary does not close the primitive route",
                )
                and contains_normalized(
                    flat_tex,
                    "The direct full-residual route corollary does not close the primitive route",
                )
            ),
        },
        "conditional_closure_proposition": {
            "main_tex_present": all(contains_normalized(main_tex, token) for token in conditional_closure_tokens),
            "flat_tex_present": all(contains_normalized(flat_tex, token) for token in conditional_closure_tokens),
            "tokens": conditional_closure_tokens,
            "records_sufficiency_only": (
                contains_normalized(main_tex, "conditional finite implication")
                and contains_normalized(flat_tex, "conditional finite implication")
            ),
            "keeps_root_lifts_open": (
                contains_normalized(
                    main_tex,
                    "Actual primitive-route Taylor subterm bounds are not established until",
                )
                and contains_normalized(
                    flat_tex,
                    "Actual primitive-route Taylor subterm bounds are not established until",
                )
            ),
            "keeps_zero_actual_bounds": (
                contains_normalized(
                    main_tex,
                    "zero actual primitive-route Taylor subterm bounds out of the 162",
                )
                and contains_normalized(
                    flat_tex,
                    "zero actual primitive-route Taylor subterm bounds out of the 162",
                )
            ),
            "blocks_direct_route_promotion": (
                contains_normalized(
                    main_tex,
                    "No inverse projection from the aggregate",
                )
                and contains_normalized(
                    flat_tex,
                    "No inverse projection from the aggregate",
                )
            ),
        },
        "source_consistency": {
            "primitive_plan_schema": plan.get("schema"),
            "primitive_plan_pc2_closed": plan.get("pc2_closed"),
            "primitive_plan_open_count": plan.get("summary", {}).get("open_primitive_obligations"),
            "p_state_gap_schema": p_state_gap.get("schema"),
            "p_state_gap_closed": p_state_gap.get("primitive_closed"),
            "p_state_map_definition_closed": p_state_gap.get("summary", {}).get("map_definition_closed"),
            "p_state_anticircularity_closed": p_state_gap.get("summary", {}).get("anti_circularity_closed"),
            "p_state_ps2_weighted_target_spec_closed": p_state_gap.get("summary", {}).get(
                "ps2_weighted_target_spec_closed"
            ),
            "p_state_ps2_inverse_or_infsup_closed": p_state_gap.get("summary", {}).get(
                "ps2_inverse_or_infsup_closed"
            ),
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
            "p_state_ps3_full_route_schema": p_state_ps3_full_route.get("schema"),
            "p_state_ps3_full_route_certificate_closed": p_state_ps3_full_route.get("summary", {}).get(
                "full_residual_route_certificate_closed"
            ),
            "p_state_ps3_full_route_ps3_input_closed": p_state_ps3_full_route.get("summary", {}).get(
                "direct_route_ps3_input_closed"
            ),
            "p_state_ps3_full_route_state_lift_rate_closed": p_state_ps3_full_route.get("summary", {}).get(
                "direct_route_state_lift_rate_closed"
            ),
            "p_state_ps3_full_route_h_acc_input_closed": p_state_ps3_full_route.get("summary", {}).get(
                "direct_route_h_weighted_acceleration_input_closed"
            ),
            "p_state_ps3_full_route_strict_steps_closed": p_state_ps3_full_route.get("summary", {}).get(
                "strict_proof_steps_closed"
            ),
            "p_state_ps3_full_route_strict_steps_total": p_state_ps3_full_route.get("summary", {}).get(
                "strict_proof_steps_total"
            ),
            "p_state_ps3_full_route_primitive_route_closed": p_state_ps3_full_route.get("summary", {}).get(
                "primitive_route_closed"
            ),
            "p_state_ps3_full_route_primitive_induced_bounds": p_state_ps3_full_route.get("summary", {}).get(
                "primitive_route_induced_taylor_bounds_proved"
            ),
            "p_state_ps2_kinematic_block_recorded": p_state_gap.get("summary", {}).get(
                "ps2_kinematic_block_certificate_recorded"
            ),
            "p_state_ps2_kinematic_subblock_bound_certified": p_state_gap.get("summary", {}).get(
                "ps2_kinematic_subblock_bound_certified"
            ),
            "p_state_ps2_kinematic_full_nonlinear_ps2_certified": p_state_gap.get("summary", {}).get(
                "ps2_kinematic_block_full_nonlinear_ps2_certified"
            ),
            "p_state_ps2_kinematic_block_schema": p_state_ps2_kinematic.get("schema"),
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
            "p_state_ps3_conditional_conversion_closed": p_state_gap.get("summary", {}).get(
                "ps3_conditional_conversion_closed"
            ),
            "p_state_ps3_actual_conversion_closed": p_state_gap.get("summary", {}).get(
                "ps3_actual_state_lift_conversion_closed"
            ),
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
            "p_acc_pa2_weighted_inverse_schema": p_acc_pa2_weighted_inverse.get("schema"),
            "p_acc_pa2_weighted_inverse_recorded": p_acc_pa2_weighted_inverse.get(
                "pa2_weighted_inverse_probe_recorded"
            ),
            "p_acc_pa2_weighted_inverse_unweighted_closed": p_acc_pa2_weighted_inverse.get(
                "unweighted_acceleration_uniform_control_proved"
            ),
            "p_acc_pa2_weighted_inverse_pa2_closed": p_acc_pa2_weighted_inverse.get("pa2_closed"),
            "p_acc_pa2_weighted_inverse_pc2_closed": p_acc_pa2_weighted_inverse.get("pc2_closed"),
            "p_lambda_interface_schema": p_lambda_interface.get("schema"),
            "p_lambda_interface_closed": p_lambda_interface.get("pl1_interface_closed"),
            "p_lambda_interface_primitive_closed": p_lambda_interface.get("primitive_closed"),
            "p_lambda_interface_pc2_closed": p_lambda_interface.get("pc2_closed"),
            "p_lambda_inf_sup_probe_schema": p_lambda_inf_sup_probe.get("schema"),
            "p_lambda_inf_sup_probe_recorded": p_lambda_inf_sup_probe.get(
                "p_lambda_inf_sup_probe_recorded"
            ),
            "p_lambda_inf_sup_probe_full_column_rank_all": p_lambda_inf_sup_probe.get("summary", {}).get(
                "finite_probe_full_column_rank_all"
            ),
            "p_lambda_inf_sup_probe_uniform_constant_proved": p_lambda_inf_sup_probe.get(
                "uniform_constant_proved"
            ),
            "p_lambda_inf_sup_probe_pc2_closed": p_lambda_inf_sup_probe.get("pc2_closed"),
            "p_lambda_d3_noncircularity_schema": p_lambda_d3_noncircularity.get("schema"),
            "p_lambda_d3_noncircularity_closed": p_lambda_d3_noncircularity.get(
                "pl3_d3_noncircularity_closed"
            ),
            "p_lambda_d3_noncircularity_primitive_closed": p_lambda_d3_noncircularity.get(
                "primitive_closed"
            ),
            "p_lambda_d3_noncircularity_pc2_closed": p_lambda_d3_noncircularity.get("pc2_closed"),
            "p_lambda_pl2_geometric_margin_schema": p_lambda_pl2_geometric_margin.get("schema"),
            "p_lambda_pl2_geometric_margin_recorded": p_lambda_pl2_geometric_margin.get(
                "pl2_geometric_margin_route_recorded"
            ),
            "p_lambda_pl2_geometric_margin_compact_tube_reduction_recorded": (
                p_lambda_pl2_geometric_margin.get("summary", {}).get("compact_tube_reduction_recorded")
            ),
            "p_lambda_pl2_geometric_margin_symbolic_structure_certificate_recorded": (
                p_lambda_pl2_geometric_margin.get("summary", {}).get("symbolic_structure_certificate_recorded")
            ),
            "p_lambda_pl2_geometric_margin_normal_force_margin_proved": (
                p_lambda_pl2_geometric_margin.get("summary", {}).get("normal_force_margin_proved")
            ),
            "p_lambda_pl2_geometric_margin_smooth_friction_orthogonal_perturbation_proved": (
                p_lambda_pl2_geometric_margin.get("summary", {}).get(
                    "smooth_friction_orthogonal_perturbation_proved"
                )
            ),
            "p_lambda_pl2_geometric_margin_axis_plane_margin_certificate_recorded": (
                p_lambda_pl2_geometric_margin.get("axis_plane_margin_certificate", {}).get("certificate_recorded")
            ),
            "p_lambda_pl2_geometric_margin_axis_torque_compact_axis_margin_proved": (
                p_lambda_pl2_geometric_margin.get("summary", {}).get("axis_torque_compact_axis_margin_proved")
            ),
            "p_lambda_pl2_geometric_margin_symbolic_margin_premise_proved": (
                p_lambda_pl2_geometric_margin.get("summary", {}).get("symbolic_margin_premise_proved")
            ),
            "p_lambda_pl2_geometric_margin_compact_tube_reduction_closes_pl2": (
                p_lambda_pl2_geometric_margin.get("compact_tube_reduction", {}).get("closes_pl2")
            ),
            "p_lambda_pl2_geometric_margin_finite_probe_sufficient_for_symbolic_margin": (
                p_lambda_pl2_geometric_margin.get("compact_tube_reduction", {}).get(
                    "finite_probe_sufficient_for_symbolic_margin"
                )
            ),
            "p_lambda_pl2_geometric_margin_pl2_closed": p_lambda_pl2_geometric_margin.get(
                "pl2_uniform_inf_sup_bound_proved"
            ),
            "p_lambda_pl2_geometric_margin_pc2_closed": p_lambda_pl2_geometric_margin.get("pc2_closed"),
            "p_lambda_pl4_rate_propagation_schema": p_lambda_pl4_rate_propagation.get("schema"),
            "p_lambda_pl4_rate_propagation_closed": p_lambda_pl4_rate_propagation.get(
                "pl4_lift_propagation_closed"
            ),
            "p_lambda_pl4_conditional_multiplier_rate": p_lambda_pl4_rate_propagation.get(
                "conditional_multiplier_lift_rate_proved"
            ),
            "p_lambda_pl4_actual_multiplier_rate": p_lambda_pl4_rate_propagation.get(
                "multiplier_lift_rate_proved"
            ),
            "p_lambda_pl4_state_input_closed": p_lambda_pl4_rate_propagation.get(
                "actual_state_lift_input_closed"
            ),
            "p_lambda_pl4_acceleration_input_closed": p_lambda_pl4_rate_propagation.get(
                "actual_acceleration_lift_input_closed"
            ),
            "p_lambda_pl4_primitive_closed": p_lambda_pl4_rate_propagation.get("primitive_closed"),
            "p_lambda_pl4_pc2_closed": p_lambda_pl4_rate_propagation.get("pc2_closed"),
            "p_geom_reduction_schema": p_geom_reduction.get("schema"),
            "p_geom_chart_reduction_closed": p_geom_reduction.get("chart_reduction_closed"),
            "p_geom_primitive_closed": p_geom_reduction.get("primitive_closed"),
            "p_geom_open_dependencies": p_geom_reduction.get("open_dependencies", []),
            "p_gyro_reduction_schema": p_gyro_reduction.get("schema"),
            "p_gyro_algebraic_reduction_closed": p_gyro_reduction.get("algebraic_reduction_closed"),
            "p_gyro_primitive_closed": p_gyro_reduction.get("primitive_closed"),
            "p_gyro_open_dependencies": p_gyro_reduction.get("open_dependencies", []),
            "proof_manifest_proof_gap_closed": proof_manifest.get("closure_state", {}).get("proof_gap_closed"),
            "proof_manifest_direct_route_gap_closed": proof_manifest.get("closure_state", {}).get(
                "direct_pc2_proof_gap_closed"
            ),
            "proof_manifest_proof_gap_closed_scope": proof_manifest.get("closure_state", {}).get(
                "proof_gap_closed_scope"
            ),
            "proof_manifest_pc2_closed": close_requirement_satisfied(proof_manifest, "PC2"),
        },
        "claim_boundary": {
            "allowed_now": (
                "the five open primitive proof interfaces are explicitly recorded, and "
                "the P_lambda PL4, P_geom, and P_gyro conditional reductions are recorded "
                "with their open lift dependencies"
            ),
            "forbidden_now": [
                "P_acc closure",
                "P_lambda closure",
                "P_geom closure",
                "P_gyro closure",
                "primitive/Taylor PC2 route closure",
                "unconditional sixth-order theorem",
            ],
            "close_condition": (
                "Primitive/Taylor PC2 lane closes only after the open P_state and P_acc interfaces have independent "
                "uniform proofs, P_lambda is instantiated with those inputs, P_geom and P_gyro "
                "receive their required lift inputs, and the induced D5 Taylor subterm bounds "
                "are certified."
            ),
        },
    }

    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# D5 Open Primitive Gap Audit",
        "",
        "Status: **open primitive gaps recorded; primitive-and-Taylor PC2 route remains open**.",
        "",
        "This read-only audit records the five D5 primitive obligations that",
        "remain after the compact-tube constant primitive is closed. It is a",
        "proof-gap ledger, not a closure certificate.",
        "",
        "## Summary",
        "",
        f"- Open primitive obligations: `{result['summary']['open_primitive_count']}/5`.",
        f"- Required future subproofs: `{result['summary']['total_future_subproofs']}`.",
        f"- Required future subproofs closed: `{result['summary']['future_subproofs_closed']}/{result['summary']['total_future_subproofs']}`.",
        f"- Conditional reductions closed: `{result['summary']['conditional_reductions_closed']}`.",
        f"- Primitive dependency graph recorded: `{result['summary']['primitive_dependency_graph_recorded']}`.",
        f"- Root lift primitives: `{result['summary']['root_lift_primitives']}`.",
        f"- Root-dependent conditional primitives: `{result['summary']['root_dependent_primitives']}`.",
        f"- Conditional downstream primitives: `{result['summary']['conditional_downstream_primitives']}`.",
        f"- Dependency edges: `{result['summary']['dependency_edge_count']}`.",
        f"- Root, root-dependent, and downstream term-row totals: `{result['summary']['root_lift_term_row_total']}/{result['summary']['root_dependent_term_row_total']}/{result['summary']['conditional_downstream_term_row_total']}`.",
        f"- P_state direct full-residual route recorded: `{result['summary']['p_state_direct_full_residual_route_recorded']}`.",
        f"- P_state direct-route PS3/state/h-acceleration rates closed: `{result['summary']['p_state_direct_route_ps3_input_closed']}/{result['summary']['p_state_direct_route_state_lift_rate_closed']}/{result['summary']['p_state_direct_route_h_weighted_acceleration_input_closed']}`.",
        f"- P_state direct-route strict proof steps closed: `{result['summary']['p_state_direct_route_strict_proof_steps_closed']}/{result['summary']['p_state_direct_route_strict_proof_steps_total']}`.",
        f"- P_state primitive route closed by direct corollary: `{result['summary']['p_state_primitive_route_closed_by_direct_corollary']}`.",
        f"- P_state primitive-route induced bounds by direct corollary: `{result['summary']['p_state_primitive_route_induced_bounds_by_direct_corollary']}/162`.",
        f"- Induced Taylor bounds proved: `{result['summary']['induced_taylor_bounds_proved']}/162`.",
        f"- Primitive/Taylor PC2 route closed: `{result['pc2_closed']}`.",
        f"- Reader-facing primitive obstruction map main/flat: `{result['reader_facing_blocker_ledger']['main_tex_present']}/{result['reader_facing_blocker_ledger']['flat_tex_present']}`.",
        f"- Conditional primitive/Taylor non-closure implication main/flat: `{result['conditional_closure_proposition']['main_tex_present']}/{result['conditional_closure_proposition']['flat_tex_present']}`.",
        "",
        "## Open Interfaces",
        "",
        "| primitive | term rows | future subproofs | subproofs closed | primitive closed |",
        "|---|---:|---:|---:|---:|",
    ]
    for row in open_interfaces:
        lines.append(
            f"| `{row['plan_id']}` | `{row['term_rows_using_obligation']}` | "
            f"`{len(row['future_subproofs'])}` | `{row['future_subproofs_closed']}` | "
            f"`{row['primitive_closed']}` |"
        )
    lines.extend(
        [
            "",
            "## Primitive Dependency Graph",
            "",
            "| source | target | reason |",
            "|---|---|---|",
        ]
    )
    for edge in primitive_dependency_graph["dependency_edges"]:
        lines.append(f"| `{edge['source']}` | `{edge['target']}` | {edge['reason']} |")
    lines.extend(
        [
            "",
            f"- Closure sequence: `{primitive_dependency_graph['closure_sequence']}`.",
            f"- Root lift primitives: `{primitive_dependency_graph['root_lift_primitives']}`.",
            f"- Root-dependent conditional primitives: `{primitive_dependency_graph['root_dependent_primitives']}`.",
            f"- Conditional downstream primitives: `{primitive_dependency_graph['conditional_downstream_primitives']}`.",
            "- Primitive/Taylor PC2 route closes only after all five open primitive obligations close.",
            "",
            "### Minimal Next Subproofs",
            "",
        ]
    )
    for item in primitive_dependency_graph["minimal_next_subproofs"]:
        lines.append(
            f"- `{item['primitive']}`: {item['next_subproof']} ({item['blocking_detail']})."
        )
    lines.extend(
        [
            "",
            "## Direct-Route Corollary",
            "",
            "The P_state full-residual route certificate closes a direct-route PS3",
            "input corollary by combining the 96 non-dynamic rows, the 36-row D5",
            "direct-substitution certificate, and the stage-residual perturbation",
            "criterion. This bypasses the h-acceleration obstruction without using",
            "velocity collocation or finite probes.",
            "",
            "- The direct-route PS3 input is closed.",
            "- The direct-route state and h-weighted acceleration rates are closed.",
            "- The direct-route proof has `4/4` strict steps closed.",
            "- The primitive-and-Taylor PC2 route remains open.",
            "- Zero primitive-route induced Taylor bounds are certified by this corollary.",
            "",
            "## Anti-Circularity Gate",
            "",
            "- Lemma `stage-residual-defect` is disallowed as an input to every open primitive.",
            "- The D5 dynamic residual defect is disallowed as an input to every open primitive.",
            "- Residual identities alone do not prove variable-lift rates.",
            "- Finite numerical slopes do not close the primitive-and-Taylor route to PC2.",
            "- The PS2 kinematic-block certificate records a uniform Euclidean Gauss subblock bound.",
            "- The PS2 Lie-chart binding audit records pure SO(3) norm-equivalence.",
            "- The PS2 row-injection audit records 72-to-96 unweighted residual dominance.",
            "- The PS2 nonlinear binding audit records rotational-row compact-tube mean-value control.",
            "- The PS2 aggregate promotion audit closes the uniform weighted inverse while leaving PS3, P_state, and the primitive-and-Taylor route to PC2 open.",
            "- The PS3 actual-instantiation gap audit records `2/4` PS3 inputs closed while the independent h-weighted acceleration input remains open.",
            "- The finite PS2 linearization probe is full-rank on recorded solved-stage probes but does not prove a uniform compact-tube inf-sup constant.",
            "- The closed P_state map definition, PS2 weighted target, PS2 aggregate promotion, PS3 conditional conversion, and anti-circularity route still depend on actual PS3 state-lift instantiation before they can imply primitive lift rates.",
            "- The closed P_acc map definition, row binding, non-dynamic input boundary, and PA2 weighted-inverse diagnostic still depend on the unweighted acceleration lift-rate proof.",
            "- The closed P_lambda interface, finite multiplier-column rank probe, PL2 geometric-margin route, PL2 symbolic normal/friction structure, PL2 axis-plane margin, PL2 compact-tube reduction, non-circular D3 algebraic mapping, and conditional PL4 propagation still depend on the actual P_state and P_acc lift inputs before P_lambda can close.",
            "- The closed P_geom chart reduction still depends on the open P_state and P_lambda lifts.",
            "- The closed P_gyro bilinear reduction still depends on the open P_state angular-velocity lift.",
            "",
            "## Acceptance Boundary",
            "",
            "- Five primitive obligations remain open.",
            "- The P_state non-dynamic map definition, PS2 weighted target, PS2 aggregate promotion, finite PS2 linearization probe, PS3 conditional conversion, and anti-circularity subproof are recorded, but P_state is not closed.",
            "- The P_acc acceleration map definition, row binding, and independence subproof are closed, but P_acc is not closed.",
            "- The P_lambda multiplier interface, finite inf-sup probe, PL2 symbolic normal/friction structure, PL2 axis-plane margin, PL2 compact-tube reduction, non-circular D3 algebraic mapping, and conditional PL4 propagation are recorded, but P_lambda is not closed.",
            "- The P_geom chart reduction is recorded only as a conditional reduction; P_geom is not closed.",
            "- The P_gyro algebraic reduction is recorded only as a conditional reduction; P_gyro is not closed.",
            "- Zero induced Taylor bounds are certified by this audit.",
            "- Primitive/Taylor PC2 route remains open.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("d5_open_primitive_gap_audit=written")
    print("open_primitives=5/5")
    print(f"future_subproofs_closed={total_future_subproofs_closed}/{total_future_subproofs}")
    print("pc2_closed=False")


if __name__ == "__main__":
    main()
