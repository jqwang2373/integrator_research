#!/usr/bin/env python3
"""Build a row-level B2 remaining-work manifest from existing source-policy artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent

SUITE_BY_PREFIX = {
    "ra2021_": "ra2021_absolute_coordinate",
    "hi2022_": "hi2022_half_implicit",
    "tfe2026_": "tfe2026_original_pendulum",
    "vp2024_": "vp2024_velocity_partitioning",
}

SUITE_ACTION = {
    "ra2021_absolute_coordinate": "route_b_demoted_keep_public_baseline_and_common_reference_diagnostics",
    "hi2022_half_implicit": "demoted_after_incomplete_full_T8_source_policy_evidence",
    "tfe2026_original_pendulum": "attempted_not_reproducible_not_promoted_keep_formula_comparator_and_candidate_diagnostics",
    "vp2024_velocity_partitioning": "attempted_not_reproducible_not_promoted_keep_proxy_diagnostic",
}

SUITE_REQUIREMENT = {
    "ra2021_absolute_coordinate": "ra2021_public_code_same_test_rows",
    "hi2022_half_implicit": "hi2022_public_code_same_test_rows",
    "tfe2026_original_pendulum": "original_tfe_pendulum_error_order_work_rows",
    "vp2024_velocity_partitioning": "vp2024_code_resolution_or_demotion",
}

SUITE_STATUS = {
    "ra2021_absolute_coordinate": "closed_by_route_b_external_superiority_demotion",
    "hi2022_half_implicit": "closed_by_explicit_source_policy_demotion",
    "tfe2026_original_pendulum": "closed_by_attempted_not_reproducible_route_b_external_superiority_demotion",
    "vp2024_velocity_partitioning": "closed_by_attempted_not_reproducible_route_b_external_superiority_demotion",
}


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def infer_suite(method: str) -> str:
    for prefix, suite_id in SUITE_BY_PREFIX.items():
        if method.startswith(prefix):
            return suite_id
    raise ValueError(f"cannot infer suite from method {method!r}")


def batch_by_id(queue: dict[str, Any]) -> dict[str, dict[str, Any]]:
    batches = queue.get("batch_queue", [])
    if not isinstance(batches, list):
        return {}
    result: dict[str, dict[str, Any]] = {}
    for batch in batches:
        if isinstance(batch, dict) and isinstance(batch.get("batch_id"), str):
            result[batch["batch_id"]] = batch
    return result


def build_closure_execution_plan(
    run_queue: dict[str, Any],
    ra2021_source_identity: dict[str, Any],
    tfe_model_audit: dict[str, Any],
) -> dict[str, Any]:
    """Record the launchable and non-launchable B2 work without running it."""
    return {
        "schema": "b2-source-policy-closure-execution-plan-v1",
        "read_only_plan": True,
        "default_1e_4_required": False,
        "source_policy_1e_4_requires_explicit_flag": True,
        "heavy_numerical_run_invoked": False,
        "run_v047_invoked": False,
        "v048_runner_invoked": False,
        "all_active_suites_ready_to_launch": True,
        "external_superiority_claim_allowed_after_plan_only": False,
        "same_test_acceptance_contract_version": "same-test-source-policy-contract-v1",
        "same_test_contract_closes_rows": False,
        "parallel_ready_shards_without_default_1e_4": run_queue.get("coverage_counts", {}).get(
            "parallel_shard_count_without_default_1e-4"
        ),
        "active_suite_lane_count": 0,
        "suite_lanes": [],
        "route_a_inactive_reference_lanes": [
            {
                "suite_id": "ra2021_absolute_coordinate",
                "status": "public_baseline_rows_complete_promotion_blocked",
                "ready_to_launch": True,
                "source_policy_1e_4_opt_in_required": True,
                "completed_public_order_groups": 12,
                "completed_public_timing_rows": 12,
                "source_identity_audit": "RA2021_SOURCE_IDENTITY_AUDIT.json",
                "source_output_mapping_verified": ra2021_source_identity.get("claim_boundary", {}).get(
                    "output_mapping_verified_from_source"
                ),
                "source_time_grid_policy_extracted": ra2021_source_identity.get("claim_boundary", {}).get(
                    "time_grid_policy_extracted_from_source"
                ),
                "source_policy_reproduction_rows_closed": ra2021_source_identity.get("claim_boundary", {}).get(
                    "source_policy_reproduction_rows_closed"
                ),
                "remaining_blockers": [
                    "promote_or_rerun_local_Gauss6_FullVA_same_policy_dynamic_order_rows",
                    "bind_error_norm_output_policy_to_source_policy_order_rows",
                    "tie_runtime_Newton_policy_to_accepted_source_policy_order_rows",
                    "produce_rerun_or_independent_verification_artifact",
                ],
                "same_test_acceptance_contract": {
                    "contract_id": "ra2021-source-policy-dynamic-order-work-contract",
                    "cases": ["single_pendulum", "double_pendulum", "four_link", "slider_crank"],
                    "horizon_policy": "use the RA2021 public-code horizon and output grid for each model; active dynamic-order promotion target is T=3",
                    "local_method_under_test": "Gauss6/FullVA",
                    "baseline_methods": ["ra2021_rA", "ra2021_rp", "ra2021_reps"],
                    "required_step_policy": {
                        "single_pendulum": [1.0e-2, 1.0e-3, 1.0e-4],
                        "double_pendulum": [1.0e-2, 2.0e-3, 1.0e-3],
                        "four_link": "T=3 true-dynamic source-policy row or explicit suite demotion",
                        "slider_crank": "T=3 true-dynamic source-policy row or explicit suite demotion",
                    },
                    "required_reference_policy": {
                        "single_pendulum": "source-public final output policy; current local candidate uses h_ref=1e-3 and is floor limited",
                        "double_pendulum": "h_ref=1e-4 source-policy self-reference",
                        "closed_loop": "source-public T=3 output policy; not the bounded T=0.1 local true-dynamic row",
                    },
                    "required_error_policy": "bind errors to the source output variables body.r/body.dr/body.ddr and the same norm/output grid used by the accepted source-policy row",
                    "required_solver_policy": "record the nonlinear tolerance, failure policy, and Newton cap for every accepted row",
                    "required_work_metrics": [
                        "wall_time_sec",
                        "total_newton_iterations",
                        "jacobian_or_colored_derivative_time_sec",
                        "linear_solve_time_sec_if_available",
                    ],
                    "acceptance_tests": [
                        "all four examples have promoted local Gauss6/FullVA rows or an explicit suite demotion",
                        "the promoted rows use the required horizon, h grid, reference, output norm, and solver policy",
                        "runtime/Newton metrics are tied to the same rows used for the order/error table",
                        "floor-limited or residual-only rows are not promoted to external superiority",
                    ],
                    "accepted_rows_closed_now": 0,
                    "plan_only_closes_b2": False,
                },
                "representative_commands": [
                    "../.venv_sbel/bin/python run_v048.py --full-ra2021-order --allow-source-policy-1e-4",
                    "../.venv_sbel/bin/python run_v048.py --reuse-existing-results --gauss6-public-single --gauss6-public-step-sizes 1e-2,1e-3,1e-4 --allow-source-policy-1e-4",
                    "../.venv_sbel/bin/python run_ra2021_double_order_shard.py --form rA --allow-source-policy-1e-4",
                    "../.venv_sbel/bin/python run_public_closed_loop_shard.py --model four_link --step-sizes 1e-2,1e-3,1e-4 --allow-source-policy-1e-4",
                ],
                "plan_only_closes_b2": False,
            },
            {
                "suite_id": "tfe2026_original_pendulum",
                "status": "nonpublic_code_attempted_not_reproducible_not_launch_ready",
                "ready_to_launch": False,
                "source_policy_1e_4_opt_in_required": None,
                "source_policy_t_end": 10.0,
                "source_reference_h": 1e-4,
                "candidate_scaffold_present": True,
                "public_code_available": False,
                "self_reproduction_attempted": True,
                "self_reproduction_attempt_status": "attempted_not_reproducible_not_promoted",
                "self_reproduction_attempt_audit": "SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_AUDIT.json",
                "candidate_full_T10_probe_implemented": tfe_model_audit.get(
                    "active_tfe_b2_full_T10_coarse_candidate_probe_implemented"
                ),
                "candidate_full_T10_probe_finite_rows": tfe_model_audit.get(
                    "active_tfe_b2_full_T10_coarse_candidate_probe_finite_rows"
                ),
                "candidate_full_T10_probe_residual_ok_rows": tfe_model_audit.get(
                    "active_tfe_b2_full_T10_coarse_candidate_probe_residual_ok_rows"
                ),
                "candidate_source_policy_rows_closed": tfe_model_audit.get(
                    "active_tfe_b2_full_T10_coarse_candidate_probe_source_policy_rows_completed"
                ),
                "remaining_blockers": [
                    "no_distinct_public_tfe_code_artifact_found",
                    "paper_spec_proxy_self_reproduction_not_source_policy_equivalent",
                    "keep_tfe_attempted_not_reproducible_until_new_source_code_equivalent_artifact_appears",
                ],
                "same_test_acceptance_contract": {
                    "contract_id": "tfe-source-pendulum-order-work-contract",
                    "cases": ["frictionless_pendulum", "frictional_revolute_joint_pendulum"],
                    "horizon_policy": "T=10 source pendulum horizon with the source endpoint/output convention",
                    "local_method_under_test": "Gauss6/FullVA on the source pendulum DAE",
                    "baseline_methods": [
                        "TFE_m1",
                        "TFE_m2",
                        "TFE_m3",
                        "Newmark_beta",
                        "trapezoidal",
                    ],
                    "required_step_policy": "source-paper h grids for the no-friction and friction rows, with h_ref=1e-4 reference for exact reproduction",
                    "required_reference_policy": "h_ref=1e-4 full-horizon source reference, not the current h_ref=0.0125 coarse candidate probe",
                    "required_friction_policy": "Brown-McPhee friction must be source-code-equivalent; the current published-formula surrogate is a candidate only",
                    "required_error_policy": "source coordinate and velocity error norms on the resolved source output grid",
                    "required_solver_policy": "match or explicitly justify source nonlinear tolerance and iteration policy before row promotion",
                    "required_work_metrics": [
                        "wall_time_sec",
                        "newton_iterations",
                        "jacobian_time_sec",
                        "source_reference_time_sec",
                    ],
                    "acceptance_tests": [
                        "no source-policy row is promoted from the paper-spec/proxy reconstruction",
                        "a future promotion would require a new source-code-equivalent public or author artifact",
                        "any future source-equivalent artifact would need the friction law, endpoint/output policy, reference, error norm, and work metrics bound to the same rows",
                        "candidate coarse or formula-only rows remain diagnostic and are not external-superiority evidence",
                    ],
                    "accepted_rows_closed_now": 0,
                    "plan_only_closes_b2": False,
                },
                "representative_commands": [],
                "plan_only_closes_b2": False,
            },
        ],
        "demoted_suite_lanes": [
            {
                "suite_id": "ra2021_absolute_coordinate",
                "status": "route_b_demoted_keep_public_baseline_and_common_reference_diagnostics",
                "demoted_by": "EXTERNAL_SUITE_DEMOTION_LEDGER.json",
                "source_policy_1e_4_opt_in_required": False,
                "completed_public_order_groups": 12,
                "completed_public_timing_rows": 12,
                "demotion_evidence": "EXTERNAL_SUITE_DEMOTION_LEDGER.json",
                "plan_only_closes_b2_subrequirement": True,
            },
            {
                "suite_id": "hi2022_half_implicit",
                "status": "demoted_after_incomplete_full_T8_source_policy_evidence",
                "demoted_by": "EXTERNAL_SUITE_DEMOTION_LEDGER.json",
                "source_policy_1e_4_opt_in_required": False,
                "completed_bounded_rows": 24,
                "source_policy_t_end": 8.0,
                "demotion_evidence": "HI2022_T8_TOLERANCE_REPAIR_AUDIT.json",
                "plan_only_closes_b2_subrequirement": True,
            },
            {
                "suite_id": "tfe2026_original_pendulum",
                "status": "attempted_not_reproducible_not_promoted_keep_formula_comparator_and_candidate_diagnostics",
                "demoted_by": "EXTERNAL_SUITE_DEMOTION_LEDGER.json",
                "source_policy_1e_4_opt_in_required": False,
                "source_policy_t_end": 10.0,
                "source_reference_h": 1e-4,
                "demotion_evidence": "SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_AUDIT.json",
                "self_reproduction_attempted": True,
                "self_reproduction_attempt_status": "attempted_not_reproducible_not_promoted",
                "plan_only_closes_b2_subrequirement": True,
            },
            {
                "suite_id": "vp2024_velocity_partitioning",
                "status": "attempted_not_reproducible_not_promoted_keep_proxy_diagnostic",
                "demoted_by": "EXTERNAL_SUITE_DEMOTION_LEDGER.json",
                "source_policy_1e_4_opt_in_required": False,
                "demotion_evidence": "VP2024_CODE_PATH_DISPOSITION_AUDIT.json",
                "self_reproduction_attempted": True,
                "self_reproduction_attempt_status": "unable_to_reproduce_not_promoted",
                "plan_only_closes_b2_subrequirement": True,
            },
        ],
    }


def main() -> None:
    row_ledger = read_json(PAPER / "SOURCE_POLICY_ROW_CLOSURE_LEDGER.json")
    run_queue = read_json(PAPER / "EXTERNAL_SAME_TEST_RUN_QUEUE.json")
    demotion = read_json(PAPER / "EXTERNAL_SUITE_DEMOTION_LEDGER.json")
    blocker = read_json(PAPER / "CMAME_BLOCKER_CLOSURE_GATE.json")
    tfe_spec = read_json(PAPER / "TFE_SOURCE_POLICY_SPEC.json")
    tfe_model_audit = read_json(PAPER / "TFE_SOURCE_PENDULUM_MODEL_AUDIT.json")
    hi2022 = read_json(PAPER / "HI2022_POLICY_DECISION_AUDIT.json")
    external_case = read_json(PAPER / "EXTERNAL_CASE_EVIDENCE_RECONCILIATION.json")
    ra2021_source_identity = read_json(PAPER / "RA2021_SOURCE_IDENTITY_AUDIT.json")
    vp2024_disposition = read_json(PAPER / "VP2024_CODE_PATH_DISPOSITION_AUDIT.json")

    batches = batch_by_id(run_queue)
    demoted_suite_ids = {
        item.get("suite_id")
        for item in demotion.get("demoted_suites", [])
        if isinstance(item, dict) and isinstance(item.get("suite_id"), str)
    }
    rows: list[dict[str, Any]] = []
    active_counts: dict[str, int] = {}
    demoted_counts: dict[str, int] = {}
    suite_counts: dict[str, int] = {}
    for index, row in enumerate(row_ledger.get("rows", []), start=1):
        method = row.get("method")
        if not isinstance(method, str):
            raise ValueError(f"row {index} has no method")
        suite_id = infer_suite(method)
        demoted = suite_id in demoted_suite_ids
        required_evidence = row.get("required_evidence", [])
        resolved_evidence: list[str] = []
        if suite_id == "ra2021_absolute_coordinate":
            resolved_evidence = [
                "source public code path and setup identity verified by RA2021_SOURCE_IDENTITY_AUDIT.json",
                "body.r/body.dr/body.ddr output mapping verified from source",
                "public endpoint time-grid convention extracted from source",
            ]
            required_evidence = [
                "local Gauss6 FullVA row under the same RA2021 source time-grid and dynamic policy",
                "error norm and output policy bound to source-policy order rows",
                "runtime/Newton-iteration policy tied to accepted source-policy order rows",
                "rerun or independent verification artifact",
            ]
        enriched = {
            "row_index": index,
            "suite_id": suite_id,
            "example": row.get("example"),
            "method": method,
            "status": SUITE_STATUS[suite_id],
            "action": SUITE_ACTION[suite_id],
            "b2_requirement": SUITE_REQUIREMENT[suite_id],
            "active_b2_requirement": not demoted,
            "demoted_from_external_superiority_scope": demoted,
            "source_policy_closed": False,
            "external_superiority_ready": False,
            "required_evidence": required_evidence,
        }
        if resolved_evidence:
            enriched["resolved_evidence"] = resolved_evidence
        rows.append(enriched)
        suite_counts[suite_id] = suite_counts.get(suite_id, 0) + 1
        if demoted:
            demoted_counts[suite_id] = demoted_counts.get(suite_id, 0) + 1
        else:
            active_counts[suite_id] = active_counts.get(suite_id, 0) + 1

    b2_blocker = next(item for item in blocker.get("blockers", []) if item.get("id") == "B2")
    suite_closure = row_ledger.get("suite_closure_status", {})
    suite_summaries = [
        {
            "suite_id": "ra2021_absolute_coordinate",
            "b2_requirement": "ra2021_public_code_same_test_rows",
            "flagged_rows": suite_counts.get("ra2021_absolute_coordinate", 0),
            "active_flagged_rows": active_counts.get("ra2021_absolute_coordinate", 0),
            "demoted_flagged_rows": demoted_counts.get("ra2021_absolute_coordinate", 0),
            "status": SUITE_STATUS["ra2021_absolute_coordinate"],
            "queue_batch": "ra2021_coarse_same_window_order_time",
            "can_parallelize": True,
            "parallel_shard_count": batches.get("ra2021_coarse_same_window_order_time", {}).get(
                "parallel_shard_count"
            ),
            "public_baseline_order_groups_completed": external_case.get("source_policy_progress", {})
            .get("ra2021_public_baselines", {})
            .get("order_groups_completed"),
            "public_baseline_order_groups_required": external_case.get("source_policy_progress", {})
            .get("ra2021_public_baselines", {})
            .get("order_groups_required"),
            "public_timing_rows_completed": external_case.get("source_policy_progress", {})
            .get("ra2021_public_baselines", {})
            .get("timing_rows_completed"),
            "public_timing_rows_required": external_case.get("source_policy_progress", {})
            .get("ra2021_public_baselines", {})
            .get("timing_rows_required"),
            "source_identity_audit": "RA2021_SOURCE_IDENTITY_AUDIT.json",
            "source_identity_audit_status": ra2021_source_identity.get("status"),
            "source_output_mapping_verified": ra2021_source_identity.get("claim_boundary", {}).get(
                "output_mapping_verified_from_source"
            ),
            "source_time_grid_policy_extracted": ra2021_source_identity.get("claim_boundary", {}).get(
                "time_grid_policy_extracted_from_source"
            ),
            "source_policy_reproduction_rows_closed_by_identity_audit": ra2021_source_identity.get(
                "claim_boundary", {}
            ).get("source_policy_reproduction_rows_closed"),
            "demoted_by": "EXTERNAL_SUITE_DEMOTION_LEDGER.json",
            "next_action": "keep as bounded public-code/common-reference diagnostic outside external-superiority scope",
        },
        {
            "suite_id": "hi2022_half_implicit",
            "b2_requirement": "hi2022_public_code_same_test_rows",
            "flagged_rows": suite_counts.get("hi2022_half_implicit", 0),
            "active_flagged_rows": active_counts.get("hi2022_half_implicit", 0),
            "demoted_flagged_rows": demoted_counts.get("hi2022_half_implicit", 0),
            "status": SUITE_STATUS["hi2022_half_implicit"],
            "queue_batch": "hi2022_halfimplicit_full_policy_decision",
            "can_parallelize": False,
            "parallel_shard_count": batches.get("hi2022_halfimplicit_full_policy_decision", {}).get(
                "parallel_shard_count"
            ),
            "bounded_T0p1_rows": hi2022.get("existing_bounded_evidence", {}).get("row_count"),
            "bounded_T0p1_rows_ok": hi2022.get("existing_bounded_evidence", {}).get("ok_row_count"),
            "full_T8_policy_completed": hi2022.get("source_policy_required_before_external_superiority", {}).get(
                "full_T8_policy_completed"
            ),
            "accepted_for_external_superiority": hi2022.get(
                "source_policy_required_before_external_superiority", {}
            ).get("accepted_for_external_superiority"),
            "demoted_by": "EXTERNAL_SUITE_DEMOTION_LEDGER.json",
            "next_action": "keep as bounded diagnostic only after incomplete T=8 source-policy evidence",
        },
        {
            "suite_id": "tfe2026_original_pendulum",
            "b2_requirement": "original_tfe_pendulum_error_order_work_rows",
            "flagged_rows": suite_counts.get("tfe2026_original_pendulum", 0),
            "active_flagged_rows": active_counts.get("tfe2026_original_pendulum", 0),
            "demoted_flagged_rows": demoted_counts.get("tfe2026_original_pendulum", 0),
            "status": SUITE_STATUS["tfe2026_original_pendulum"],
            "queue_batch": "tfe2026_original_pendulum_encoding",
            "can_parallelize": False,
            "parallel_shard_count": 0,
            "source_policy_spec_extracted": suite_closure.get("tfe2026_original_pendulum", {})
            .get("runner_gap", {})
            .get("source_policy_spec_extracted"),
            "source_reference_h": tfe_spec.get("source_policy", {})
            .get("solver_policy", {})
            .get("source_reference_h_for_exact_reproduction"),
            "source_policy_rows_completed": tfe_spec.get("runner_gap", {}).get("source_policy_rows_completed"),
            "runner_implemented": tfe_spec.get("runner_gap", {}).get("pendulum_dae_runner_implemented"),
            "candidate_scaffold_present": True,
            "candidate_full_T10_probe_implemented": tfe_model_audit.get(
                "active_tfe_b2_full_T10_coarse_candidate_probe_implemented"
            ),
            "candidate_full_T10_probe_finite_rows": tfe_model_audit.get(
                "active_tfe_b2_full_T10_coarse_candidate_probe_finite_rows"
            ),
            "candidate_full_T10_probe_residual_ok_rows": tfe_model_audit.get(
                "active_tfe_b2_full_T10_coarse_candidate_probe_residual_ok_rows"
            ),
            "candidate_full_T10_probe_source_policy_rows": tfe_model_audit.get(
                "active_tfe_b2_full_T10_coarse_candidate_probe_source_policy_rows_completed"
            ),
            "demoted_by": "EXTERNAL_SUITE_DEMOTION_LEDGER.json",
            "next_action": "keep as formal-order comparator and candidate diagnostic outside external-superiority scope",
        },
        {
            "suite_id": "vp2024_velocity_partitioning",
            "b2_requirement": "vp2024_code_resolution_or_demotion",
            "flagged_rows": suite_counts.get("vp2024_velocity_partitioning", 0),
            "active_flagged_rows": 0,
            "demoted_flagged_rows": demoted_counts.get("vp2024_velocity_partitioning", 0),
            "status": SUITE_STATUS["vp2024_velocity_partitioning"],
            "queue_batch": "vp2024_velocity_partitioning_code_resolution",
            "can_parallelize": False,
            "parallel_shard_count": 0,
            "code_path_resolved": False,
            "demoted_by": "EXTERNAL_SUITE_DEMOTION_LEDGER.json",
            "demoted_source_policy_rows": demotion.get("vp2024_demoted_source_policy_rows"),
            "full_source_policy_rows": vp2024_disposition.get("coverage", {}).get("source_policy_rows"),
            "source_policy_code_path_unresolved_rows": vp2024_disposition.get("coverage", {}).get(
                "source_policy_code_path_unresolved_rows"
            ),
            "self_reproduction_attempted_rows": vp2024_disposition.get("coverage", {}).get(
                "source_policy_rows_attempted_not_reproducible"
            ),
            "unable_to_reproduce_rows": vp2024_disposition.get("coverage", {}).get("unable_to_reproduce_rows"),
            "final_nonpublic_code_disposition": vp2024_disposition.get(
                "source_code_path_disposition", {}
            ).get("final_nonpublic_code_disposition"),
            "next_action": "keep proxy evidence diagnostic; full VP source-policy rows are unable-to-reproduce/not-promoted until a new source-code-equivalent artifact appears",
        },
    ]

    output = {
        "schema": "b2-source-policy-remaining-work-manifest-v1",
        "status": "route_b_all_external_suites_demoted_no_active_external_superiority_rows",
        "submission_ready": False,
        "source_policy_external_superiority_allowed": False,
        "external_superiority_claim_allowed": False,
        "row_count": len(rows),
        "active_flagged_row_count": sum(active_counts.values()),
        "demoted_flagged_row_count": sum(demoted_counts.values()),
        "source_policy_closed_rows": 0,
        "external_superiority_ready_rows": 0,
        "suite_counts": suite_counts,
        "active_suite_counts": active_counts,
        "demoted_suite_counts": demoted_counts,
        "b2_closed_by_demotion": demotion.get("b2_subrequirements_closed_by_demotion"),
        "b2_remaining_requirements": demotion.get("b2_required_to_close_after_demotions"),
        "b2_can_close_now": True,
        "b4_can_close_now": False,
        "route_b_b2_claim_boundary_synchronized": True,
        "route_b_b4_claim_boundary_synchronized": True,
        "route_b_b2_closure_ready_pending_gate_sync": False,
        "route_b_b4_closure_ready_pending_gate_sync": False,
        "remaining_active_suites": [],
        "demoted_suites": sorted(demoted_suite_ids),
        "suite_summaries": suite_summaries,
        "rows": rows,
        "execution_policy": {
            "read_only_existing_artifacts": True,
            "default_1e_4_required": False,
            "heavy_numerical_run_invoked": False,
            "run_v047_invoked": False,
            "v048_runner_invoked": False,
            "parallel_ready_shards_without_default_1e_4": run_queue.get("coverage_counts", {}).get(
                "parallel_shard_count_without_default_1e-4"
            ),
        },
        "closure_execution_plan": build_closure_execution_plan(run_queue, ra2021_source_identity, tfe_model_audit),
        "claim_policy": {
            "common_reference_claim_allowed": True,
            "source_policy_rows_must_be_closed_or_demoted_before_external_superiority": True,
            "demoted_rows_do_not_count_as_numerical_wins": True,
            "paper_must_report_remaining_active_suites": True,
        },
        "source_files": {
            "source_policy_row_closure_ledger": "SOURCE_POLICY_ROW_CLOSURE_LEDGER.json",
            "external_same_test_run_queue": "EXTERNAL_SAME_TEST_RUN_QUEUE.json",
            "external_case_evidence_reconciliation": "EXTERNAL_CASE_EVIDENCE_RECONCILIATION.json",
            "hi2022_policy_decision_audit": "HI2022_POLICY_DECISION_AUDIT.json",
            "tfe_source_policy_spec": "TFE_SOURCE_POLICY_SPEC.json",
            "tfe_source_pendulum_model_audit": "TFE_SOURCE_PENDULUM_MODEL_AUDIT.json",
            "source_policy_self_reproduction_attempt_audit": "SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_AUDIT.json",
            "vp2024_code_path_disposition_audit": "VP2024_CODE_PATH_DISPOSITION_AUDIT.json",
            "ra2021_source_identity_audit": "RA2021_SOURCE_IDENTITY_AUDIT.json",
            "external_suite_demotion_ledger": "EXTERNAL_SUITE_DEMOTION_LEDGER.json",
            "cmame_blocker_closure_gate": "CMAME_BLOCKER_CLOSURE_GATE.json",
        },
    }

    out_json = PAPER / "B2_SOURCE_POLICY_REMAINING_WORK_MANIFEST.json"
    out_md = PAPER / "B2_SOURCE_POLICY_REMAINING_WORK_MANIFEST.md"
    with out_json.open("w", encoding="utf-8") as handle:
        json.dump(output, handle, indent=2, sort_keys=True)
        handle.write("\n")

    lines = [
        "# B2 Source-Policy Remaining Work Manifest",
        "",
        "Status: `route_b_all_external_suites_demoted_no_active_external_superiority_rows`.",
        "",
        "This is a read-only manifest over existing artifacts. It does not run new numerical experiments.",
        "",
        f"- Total flagged source-policy rows: `{output['row_count']}`.",
        f"- Active flagged rows after Route B demotion: `{output['active_flagged_row_count']}`.",
        f"- Demoted flagged rows after Route B demotion: `{output['demoted_flagged_row_count']}`.",
        f"- Source-policy closed rows: `{output['source_policy_closed_rows']}`.",
        f"- External-superiority-ready rows: `{output['external_superiority_ready_rows']}`.",
        f"- B2 closed by demotion: `{output['b2_closed_by_demotion']}`.",
        f"- B2 remaining requirements: `{output['b2_remaining_requirements']}`.",
        f"- Route B B2/B4 claim-boundary synchronized: `{output['route_b_b2_claim_boundary_synchronized']}/{output['route_b_b4_claim_boundary_synchronized']}`.",
        f"- Route B B2/B4 closure ready pending gate sync: `{output['route_b_b2_closure_ready_pending_gate_sync']}/{output['route_b_b4_closure_ready_pending_gate_sync']}`.",
        f"- External superiority claim allowed: `{output['external_superiority_claim_allowed']}`.",
        f"- Default 1e-4/heavy/run_v047: `{output['execution_policy']['default_1e_4_required']}/{output['execution_policy']['heavy_numerical_run_invoked']}/{output['execution_policy']['run_v047_invoked']}`.",
        f"- Closure execution plan: `{output['closure_execution_plan']['schema']}`.",
        f"- Closure plan all active suites ready: `{output['closure_execution_plan']['all_active_suites_ready_to_launch']}`.",
        f"- Closure plan explicit 1e-4 opt-in required: `{output['closure_execution_plan']['source_policy_1e_4_requires_explicit_flag']}`.",
        f"- Same-test acceptance contract: `{output['closure_execution_plan']['same_test_acceptance_contract_version']}`.",
        f"- Same-test contract closes rows now: `{output['closure_execution_plan']['same_test_contract_closes_rows']}`.",
        f"- TFE candidate full T=10 probe finite/residual/source-policy rows: `{suite_summaries[2]['candidate_full_T10_probe_finite_rows']}/{suite_summaries[2]['candidate_full_T10_probe_residual_ok_rows']}/{suite_summaries[2]['candidate_full_T10_probe_source_policy_rows']}`.",
        "- TFE current disposition: `attempted_not_reproducible_not_promoted`; no public source-code-equivalent artifact was found.",
        f"- VP full source-policy rows unresolved/attempted/unable/closed: `{suite_summaries[3]['source_policy_code_path_unresolved_rows']}/{suite_summaries[3]['self_reproduction_attempted_rows']}/{suite_summaries[3]['unable_to_reproduce_rows']}/{output['source_policy_closed_rows']}`; final disposition `{suite_summaries[3]['final_nonpublic_code_disposition']}`.",
        "",
        "## Suite Summary",
        "",
        "| suite | active rows | demoted rows | status | next action |",
        "|---|---:|---:|---|---|",
    ]
    for suite in suite_summaries:
        lines.append(
            f"| `{suite['suite_id']}` | `{suite['active_flagged_rows']}` | "
            f"`{suite['demoted_flagged_rows']}` | `{suite['status']}` | {suite['next_action']} |"
        )
    lines.extend(
        [
            "",
            "## Row-Level Work Items",
            "",
            "| # | suite | example | method | status | action |",
            "|---:|---|---|---|---|---|",
        ]
    )
    for row in rows:
        lines.append(
            f"| {row['row_index']} | `{row['suite_id']}` | `{row['example']}` | "
            f"`{row['method']}` | `{row['status']}` | `{row['action']}` |"
        )
    lines.extend(
        [
            "",
            "## Closure Execution Plan",
            "",
            "| suite | ready to launch | explicit 1e-4 opt-in | plan-only closes B2 | key blocker |",
            "|---|---:|---:|---:|---|",
        ]
    )
    for lane in output["closure_execution_plan"].get("route_a_inactive_reference_lanes", []):
        blockers = lane.get("remaining_blockers", [])
        key_blocker = blockers[0] if blockers else "none"
        lines.append(
            f"| `{lane['suite_id']}` | `{lane['ready_to_launch']}` | "
            f"`{lane['source_policy_1e_4_opt_in_required']}` | `{lane['plan_only_closes_b2']}` | "
            f"`{key_blocker}` |"
        )
    lines.extend(
        [
            "",
            "## Same-Test Acceptance Contract",
            "",
            "| suite | cases | horizon/reference contract | required work metrics | acceptance rule |",
            "|---|---|---|---|---|",
        ]
    )
    for lane in output["closure_execution_plan"].get("route_a_inactive_reference_lanes", []):
        contract = lane["same_test_acceptance_contract"]
        cases = ", ".join(f"`{case}`" for case in contract["cases"])
        metrics = ", ".join(f"`{metric}`" for metric in contract["required_work_metrics"])
        acceptance_rules = "; ".join(contract["acceptance_tests"])
        if lane["suite_id"] == "ra2021_absolute_coordinate":
            horizon_reference = "T=3 source-policy target; public output variables and source-bound norm/reference policy"
        else:
            horizon_reference = "historical T=10 source pendulum contract retained only as a future condition if a source-code-equivalent artifact appears"
        lines.append(
            f"| `{lane['suite_id']}` | {cases} | {horizon_reference} | {metrics} | {acceptance_rules}; "
            f"accepted rows now `{contract['accepted_rows_closed_now']}` |"
        )
    lines.extend(
        [
            "",
            "Representative opt-in commands are stored in `B2_SOURCE_POLICY_REMAINING_WORK_MANIFEST.json`.",
            "They are not executed by this manifest, and rows involving `1e-4` require an explicit `--allow-source-policy-1e-4` flag.",
        ]
    )
    lines.extend(
        [
            "",
            "The Route B demotions are claim-boundary decisions, not numerical wins.",
            "TFE/VP rows with no usable public source-code-equivalent artifact are attempted-not-reproducible and not promoted.",
            "RA2021 and HI2022 public-root diagnostics remain not-promoted until a source-policy promotion/execution closeout succeeds.",
        ]
    )
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("b2_source_policy_remaining_work_manifest=written")
    print(f"active_flagged_rows={output['active_flagged_row_count']}")
    print(f"demoted_flagged_rows={output['demoted_flagged_row_count']}")
    print("source_policy_closed_rows=0")
    print(f"route_b_b2_claim_boundary_synchronized={output['route_b_b2_claim_boundary_synchronized']}")
    print(f"route_b_b2_closure_ready_pending_gate_sync={output['route_b_b2_closure_ready_pending_gate_sync']}")
    print("external_superiority_claim_allowed=False")


if __name__ == "__main__":
    main()
