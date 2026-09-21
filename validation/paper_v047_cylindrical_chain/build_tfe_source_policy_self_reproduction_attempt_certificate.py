#!/usr/bin/env python3
"""Build a TFE source-policy self-reproduction attempt certificate.

The source paper specification is partially reconstructable from the PDF/text:
parameters, output norms, candidate formulas, and several bounded/full-horizon
diagnostics are present.  This certificate records that attempted reconstruction
and keeps the source-policy decision negative when the remaining obligations
are not source-equivalent.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
V048_RESULTS = PAPER.parent.parent / "numerics" / "v048_cross_paper_same_test_benchmarks" / "results"
OUT_JSON = PAPER / "TFE_SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_CERTIFICATE.json"
OUT_MD = PAPER / "TFE_SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_CERTIFICATE.md"

EXAMPLES = ["single_pendulum", "double_pendulum", "four_link", "slider_crank"]
TFE_B4_METHODS = [
    "tfe2026_Newmark_beta",
    "tfe2026_TFE_m1",
    "tfe2026_TFE_m2",
    "tfe2026_trapezoidal",
]


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def parse_bool(value: str | None) -> bool:
    return str(value).lower() == "true"


def parse_float(value: str | None) -> float:
    return float(value) if value not in (None, "") else float("nan")


def main() -> None:
    spec = read_json(PAPER / "TFE_SOURCE_POLICY_SPEC.json")
    public_code_recheck = read_json(PAPER / "TFE_PUBLIC_CODE_RECHECK_20260613.json")
    public_code_refresh_latest = read_json(PAPER / "SOURCE_POLICY_PUBLIC_CODE_REFRESH_20260620.json")
    model = read_json(PAPER / "TFE_SOURCE_PENDULUM_MODEL_AUDIT.json")
    method_contract = model.get("source_method_candidate_runner_contract_smoke", {})
    gauss6_dae_candidate_contract = model.get(
        "gauss6_fullva_dae_candidate_contract_smoke",
        {},
    )
    gap = read_json(PAPER / "TFE_DAE_RUNNER_CONTRACT_GAP_AUDIT.json")
    brown = read_json(PAPER / "TFE_BROWN_MCPHEE_SOURCE_LAW_BOUNDARY_AUDIT.json")
    brown_certificate = read_json(PAPER / "TFE_BROWN_MCPHEE_SOURCE_CODE_EQUIVALENCE_CERTIFICATE.json")
    grid = read_json(PAPER / "TFE_SOURCE_GRID_COMPATIBILITY_AUDIT.json")
    endpoint_certificate = read_json(PAPER / "TFE_FULL_T10_ENDPOINT_POLICY_CLOSURE_CERTIFICATE.json")
    full_t10 = read_json(PAPER / "TFE_FULL_T10_ABSOLUTE_DAE_LIFT_SUMMARY.json")
    same_test = read_json(V048_RESULTS / "tfe_source_pendulum_same_test_work_precision.json")
    same_test_summary_rows = read_csv_rows(
        V048_RESULTS / "tfe_source_pendulum_same_test_work_precision_summary.csv"
    )
    same_test_raw_rows = read_csv_rows(
        V048_RESULTS / "tfe_source_pendulum_same_test_work_precision_rows.csv"
    )

    summary_by_paper_method = {
        row["paper_method"]: {
            "source_method": row["source_method"],
            "expected_order": int(row["expected_order"]),
            "candidate_summary_rows": int(row["row_count"]),
            "ok_row_count": int(row["ok_row_count"]),
            "coordinate_pairwise_order_floor": parse_float(row["coordinate_pairwise_order_floor"]),
            "velocity_pairwise_order_floor": parse_float(row["velocity_pairwise_order_floor"]),
            "finest_coordinate_error_q": parse_float(row["finest_coordinate_error_q"]),
            "finest_velocity_error_v": parse_float(row["finest_velocity_error_v"]),
            "source_policy_method_runner_equivalent": parse_bool(
                row["source_policy_method_runner_equivalent"]
            ),
            "source_policy_row_completed": parse_bool(row["source_policy_row_completed"]),
            "accepted_use": row["accepted_use"],
        }
        for row in same_test_summary_rows
    }
    full_t10_by_paper_method = {
        str(row["paper_method"]): row
        for row in full_t10.get("rows", [])
        if isinstance(row, dict)
    }
    method_contract_rows = [
        row for row in method_contract.get("rows", [])
        if isinstance(row, dict)
    ]
    method_contract_paper_methods = sorted(
        {str(row.get("paper_method")) for row in method_contract_rows if row.get("paper_method")}
    )

    execution_blocks = list(gap.get("source_policy_execution_missing_contract_blocks", []))
    nonheavy_blocks = list(gap.get("nonheavy_missing_contract_blocks", []))
    all_blockers = nonheavy_blocks + execution_blocks
    execution_preflight = gap.get("source_policy_execution_preflight", {})
    row_dispositions: list[dict[str, Any]] = []
    for method in TFE_B4_METHODS:
        summary = summary_by_paper_method[method]
        full_t10_row = full_t10_by_paper_method.get(method, {})
        for example in EXAMPLES:
            source_scope_supported = example == "single_pendulum"
            method_covered_by_contract = method in method_contract_paper_methods
            if source_scope_supported:
                reason = "paper_spec_candidate_runner_not_source_policy_equivalent"
                blocking_contract_blocks = all_blockers
            else:
                reason = "tfe_source_paper_pendulum_suite_does_not_define_this_mechanism_runner"
                blocking_contract_blocks = [
                    "tfe_source_paper_pendulum_suite_does_not_define_this_mechanism_runner",
                    *all_blockers,
                ]
            row_dispositions.append(
                {
                    "row_id": f"{method}:{example}",
                    "method": method,
                    "example": example,
                    "self_reproduction_attempted": True,
                    "source_suite_scope_supported": source_scope_supported,
                    "candidate_method_summary_available": True,
                    "candidate_summary_rows": summary["candidate_summary_rows"],
                    "candidate_velocity_order_floor": summary["velocity_pairwise_order_floor"],
                    "candidate_finest_velocity_error": summary["finest_velocity_error_v"],
                    "method_covered_by_source_method_candidate_contract": method_covered_by_contract,
                    "source_method_candidate_contract_available_for_row": (
                        source_scope_supported and method_covered_by_contract
                    ),
                    "source_method_candidate_contract_accepted_use": (
                        method_contract.get("accepted_use")
                        if source_scope_supported and method_covered_by_contract
                        else None
                    ),
                    "source_method_candidate_contract_source_policy_rows_completed": 0,
                    "source_method_candidate_contract_method_equivalent": False,
                    "source_method_candidate_contract_dae_equivalent": False,
                    "full_T10_absolute_dae_lift_available": bool(full_t10_row),
                    "full_T10_absolute_dae_lift_step_rows": full_t10_row.get("step_residual_rows"),
                    "source_policy_method_runner_equivalent": False,
                    "source_policy_dae_runner_equivalent": False,
                    "monolithic_absolute_coordinate_dae_time_integrator": False,
                    "source_policy_closed": False,
                    "external_superiority_ready": False,
                    "unable_to_reproduce": True,
                    "source_policy_disposition": "attempted_not_reproducible",
                    "final_nonpublic_code_disposition": "unable_to_reproduce_not_promoted",
                    "primary_nonreproducibility_reason": reason,
                    "blocking_contract_blocks": blocking_contract_blocks,
                    "accepted_use": "diagnostic_candidate_or_related_work_only_not_source_policy",
                }
            )

    reconstructed_layers = {
        "source_policy_spec_extracted": spec.get("runner_gap", {}).get("source_policy_spec_extracted"),
        "source_pendulum_parameter_model_implemented": model.get(
            "source_pendulum_parameter_model_implemented"
        ),
        "source_output_error_policy_encoded": model.get("source_output_time_integration_smoke_implemented"),
        "tfe_appendix_b_coefficient_certificate_checked": model.get(
            "tfe_appendix_b_coefficient_certificate_checked"
        ),
        "same_test_candidate_work_precision_available": same_test.get(
            "same_test_work_precision_available"
        ),
        "same_test_candidate_raw_rows": len(same_test_raw_rows),
        "same_test_candidate_summary_rows": len(same_test_summary_rows),
        "absolute_coordinate_planar_lift_probe_rows": model.get(
            "absolute_coordinate_planar_lift_trajectory_probe_rows"
        ),
        "bounded_absolute_coordinate_dae_runner_rows": model.get(
            "bounded_absolute_coordinate_dae_trajectory_runner_rows"
        ),
        "dae_trajectory_bridge_contract_rows": model.get("dae_trajectory_bridge_contract_rows"),
        "full_T10_absolute_dae_lift_completed": full_t10.get(
            "full_T10_absolute_coordinate_lift_completed"
        ),
        "full_T10_absolute_dae_lift_step_residual_rows": full_t10.get(
            "step_residual_row_count"
        ),
        "candidate_frictional_dae_trajectory_contract_rows": model.get(
            "candidate_frictional_dae_trajectory_contract_rows"
        ),
        "source_method_candidate_runner_contract_implemented": model.get(
            "source_method_candidate_runner_contract_implemented"
        ),
        "source_method_candidate_runner_contract_rows": model.get(
            "source_method_candidate_runner_contract_rows"
        ),
        "source_method_candidate_runner_contract_source_policy_rows_completed": model.get(
            "source_method_candidate_runner_contract_source_policy_rows_completed"
        ),
        "source_method_candidate_runner_contract_method_equivalent": model.get(
            "source_method_candidate_runner_contract_method_equivalent"
        ),
        "source_method_candidate_runner_contract_dae_equivalent": model.get(
            "source_method_candidate_runner_contract_dae_equivalent"
        ),
        "gauss6_fullva_dae_candidate_contract_implemented": model.get(
            "gauss6_fullva_dae_candidate_contract_implemented"
        ),
        "gauss6_fullva_dae_candidate_contract_rows": model.get(
            "gauss6_fullva_dae_candidate_contract_rows"
        ),
        "gauss6_fullva_dae_candidate_contract_source_policy_rows_completed": model.get(
            "gauss6_fullva_dae_candidate_contract_source_policy_rows_completed"
        ),
        "gauss6_fullva_dae_candidate_contract_dae_equivalent": model.get(
            "gauss6_fullva_dae_candidate_contract_dae_equivalent"
        ),
        "gauss6_fullva_dae_candidate_contract_fullva_dae_equivalent": model.get(
            "gauss6_fullva_dae_candidate_contract_fullva_dae_equivalent"
        ),
    }
    unresolved_obligations = {
        "source_policy_runner_obligations": spec.get(
            "candidate_vs_source_policy_boundary", {}
        ).get("source_policy_runner_obligations", []),
        "nonheavy_missing_contract_blocks": nonheavy_blocks,
        "source_policy_execution_missing_contract_blocks": execution_blocks,
        "brown_mcphee_source_code_equivalent_law": brown.get(
            "brown_mcphee_source_code_equivalent_law"
        ),
        "brown_mcphee_transition_velocity_policy_resolved_from_source": brown.get(
            "brown_mcphee_transition_velocity_policy_resolved_from_source"
        ),
        "source_grid_policy_resolved_for_full_T10": grid.get(
            "source_grid_policy_resolved_for_full_T10"
        ),
        "monolithic_absolute_coordinate_dae_time_integrator": gap.get(
            "monolithic_absolute_coordinate_dae_time_integrator"
        ),
        "source_policy_method_runner_equivalent": gap.get("source_policy_method_runner_equivalent"),
        "source_policy_dae_runner_equivalent": gap.get("source_policy_dae_runner_equivalent"),
    }
    nonheavy_negative_certificates = {
        "brown_mcphee": {
            "certificate": "TFE_BROWN_MCPHEE_SOURCE_CODE_EQUIVALENCE_CERTIFICATE.json",
            "status": brown_certificate.get("status"),
            "certificate_available": brown_certificate.get("certificate_available"),
            "positive_source_code_equivalence_certified": brown_certificate.get(
                "positive_source_code_equivalence_certified"
            ),
            "nonheavy_contract_block_closed": brown_certificate.get(
                "nonheavy_contract_block_closed"
            ),
            "source_policy_rows_completed": brown_certificate.get(
                "source_policy_rows_completed"
            ),
        },
        "full_T10_endpoint_policy": {
            "certificate": "TFE_FULL_T10_ENDPOINT_POLICY_CLOSURE_CERTIFICATE.json",
            "status": endpoint_certificate.get("status"),
            "certificate_available": endpoint_certificate.get("certificate_available"),
            "positive_full_T10_endpoint_policy_certified": endpoint_certificate.get(
                "positive_full_T10_endpoint_policy_certified"
            ),
            "nonheavy_contract_block_closed": endpoint_certificate.get(
                "nonheavy_contract_block_closed"
            ),
            "source_policy_rows_completed": endpoint_certificate.get(
                "source_policy_rows_completed"
            ),
            "source_grid_policy_resolved_for_full_T10": endpoint_certificate.get(
                "source_grid_policy_resolved_for_full_T10"
            ),
        },
        "source_policy_rows_completed_by_negative_certificates": 0,
        "nonheavy_blocks_closed_by_negative_certificates": False,
    }
    required_next_actions = [
        (
            "Keep TFE source-policy rows attempted-not-reproducible/not-promoted under the current "
            f"{execution_preflight.get('current_route')} route."
        ),
        (
            "Reopen the TFE source-policy lane only if a new public or source-code-equivalent "
            "TFE implementation artifact appears."
        ),
        (
            "Do not execute or promote TFE source-policy work/precision rows until the required "
            "runner contracts exist: "
            + ", ".join(str(item) for item in execution_preflight.get("runner_contracts_required_before_execution", []))
            + "."
        ),
    ]

    output: dict[str, Any] = {
        "schema": "tfe-source-policy-self-reproduction-attempt-certificate-v1",
        "status": "attempted_not_reproducible_not_promoted",
        "read_only": True,
        "heavy_numerical_run_invoked": False,
        "run_v047_invoked": False,
        "v048_runner_invoked": False,
        "source_policy_closed": False,
        "source_policy_closed_ratio": f"0/{len(row_dispositions)}",
        "source_policy_rows_completed": 0,
        "source_policy_rows_closed": 0,
        "source_policy_rows_total": len(row_dispositions),
        "external_superiority_claim_allowed": False,
        "submission_ready": False,
        "public_code_recheck_status": public_code_recheck.get("status"),
        "public_code_recheck_date": public_code_recheck.get("date_checked"),
        "public_code_recheck_source_policy_rows_closed": public_code_recheck.get(
            "coverage", {}
        ).get("source_policy_rows_closed"),
        "public_code_recheck_attempted_not_reproducible_rows": public_code_recheck.get(
            "coverage", {}
        ).get("source_policy_rows_attempted_not_reproducible"),
        "public_code_refresh_latest_status": public_code_refresh_latest.get("status"),
        "public_code_refresh_latest_date": public_code_refresh_latest.get("date_checked"),
        "public_code_refresh_latest_rows": public_code_refresh_latest.get("row_count"),
        "public_code_refresh_latest_current_queries": public_code_refresh_latest.get(
            "current_query_count"
        ),
        "public_code_refresh_latest_positive_artifact_rows": public_code_refresh_latest.get(
            "positive_public_code_artifact_rows"
        ),
        "public_code_refresh_latest_source_policy_closed": public_code_refresh_latest.get(
            "source_policy_closed"
        ),
        "public_code_refresh_latest_source_policy_closed_ratio": public_code_refresh_latest.get(
            "source_policy_closed_ratio"
        ),
        "public_code_refresh_latest_source_policy_rows_closed": public_code_refresh_latest.get(
            "source_policy_rows_closed"
        ),
        "source_policy_execution_preflight_status": execution_preflight.get("status"),
        "source_policy_execution_preflight_current_route": execution_preflight.get(
            "current_route"
        ),
        "source_policy_execution_preflight_ready_now": execution_preflight.get(
            "ready_to_execute_source_policy_now"
        ),
        "source_policy_execution_preflight_can_promote_rows_now": execution_preflight.get(
            "can_promote_any_tfe_source_policy_row_now"
        ),
        "source_policy_execution_preflight_source_policy_rows_completed": execution_preflight.get(
            "source_policy_rows_completed"
        ),
        "reopen_condition": execution_preflight.get("reopen_condition"),
        "public_code_status": {
            "distinct_public_tfe_code_artifact_registered": False,
            "available_basis": "source_paper_text_plus_local_candidate_reconstruction",
            "paper_spec_self_reproduction_attempted": True,
            "public_code_recheck_certificate": "TFE_PUBLIC_CODE_RECHECK_20260613.json",
            "public_code_recheck_certificate_status": public_code_recheck.get("status"),
            "public_code_recheck_date": public_code_recheck.get("date_checked"),
            "public_code_recheck_github_repository_search_total_count": public_code_recheck.get(
                "coverage", {}
            ).get("github_repository_search_total_count"),
            "public_code_recheck_github_user_search_total_count": public_code_recheck.get(
                "coverage", {}
            ).get("github_user_search_total_count"),
            "public_code_recheck_github_code_search_api_status": public_code_recheck.get(
                "coverage", {}
            ).get("github_code_search_api_status"),
            "public_code_recheck_source_policy_rows_closed": public_code_recheck.get(
                "coverage", {}
            ).get("source_policy_rows_closed"),
            "public_code_recheck_attempted_not_reproducible_rows": public_code_recheck.get(
                "coverage", {}
            ).get("source_policy_rows_attempted_not_reproducible"),
        },
        "candidate_vs_source_policy_boundary": spec.get("candidate_vs_source_policy_boundary", {}),
        "row_count": len(row_dispositions),
        "self_reproduction_attempted_rows": len(row_dispositions),
        "attempted_not_reproducible_rows": len(row_dispositions),
        "unable_to_reproduce_rows": len(row_dispositions),
        "source_policy_rows_unable_to_reproduce": len(row_dispositions),
        "final_nonpublic_code_disposition": "unable_to_reproduce_not_promoted",
        "single_pendulum_attempted_rows": sum(
            1 for row in row_dispositions if row["source_suite_scope_supported"]
        ),
        "source_scope_unsupported_mechanism_rows": sum(
            1 for row in row_dispositions if not row["source_suite_scope_supported"]
        ),
        "source_policy_closed_rows": 0,
        "external_superiority_ready_rows": 0,
        "candidate_same_test_work_precision_rows": same_test.get("row_count"),
        "candidate_same_test_summary_rows": same_test.get("summary_row_count"),
        "candidate_same_test_ok_rows": same_test.get("ok_row_count"),
        "source_method_candidate_runner_contract": {
            "schema": method_contract.get("schema"),
            "runner_api": method_contract.get("runner_api"),
            "accepted_use": method_contract.get("accepted_use"),
            "row_count": method_contract.get("row_count"),
            "method_count": method_contract.get("method_count"),
            "paper_methods": method_contract_paper_methods,
            "b4_method_coverage_count": sum(
                1 for method in TFE_B4_METHODS if method in method_contract_paper_methods
            ),
            "b4_method_coverage_complete": all(
                method in method_contract_paper_methods for method in TFE_B4_METHODS
            ),
            "all_step_states_finite": method_contract.get("all_step_states_finite"),
            "all_candidate_residuals_below_1e_8": method_contract.get(
                "all_candidate_residuals_below_1e_8"
            ),
            "max_candidate_step_residual_norm": method_contract.get(
                "max_candidate_step_residual_norm"
            ),
            "source_policy_rows_completed": method_contract.get("source_policy_rows_completed"),
            "source_policy_method_runner_equivalent": method_contract.get(
                "source_policy_method_runner_equivalent"
            ),
            "source_policy_dae_runner_equivalent": method_contract.get(
                "source_policy_dae_runner_equivalent"
            ),
        },
        "gauss6_fullva_dae_candidate_contract": {
            "schema": gauss6_dae_candidate_contract.get("schema"),
            "runner_api": gauss6_dae_candidate_contract.get("runner_api"),
            "accepted_use": gauss6_dae_candidate_contract.get("accepted_use"),
            "row_count": gauss6_dae_candidate_contract.get("row_count"),
            "all_step_states_finite": gauss6_dae_candidate_contract.get(
                "all_step_states_finite"
            ),
            "all_candidate_residuals_below_1e_8": gauss6_dae_candidate_contract.get(
                "all_candidate_residuals_below_1e_8"
            ),
            "max_candidate_step_residual_norm": gauss6_dae_candidate_contract.get(
                "max_candidate_step_residual_norm"
            ),
            "source_policy_rows_completed": gauss6_dae_candidate_contract.get(
                "source_policy_rows_completed"
            ),
            "source_policy_dae_runner_equivalent": gauss6_dae_candidate_contract.get(
                "source_policy_dae_runner_equivalent"
            ),
            "fullva_dae_source_policy_equivalent": gauss6_dae_candidate_contract.get(
                "fullva_dae_source_policy_equivalent"
            ),
        },
        "reconstructed_layers": reconstructed_layers,
        "unresolved_obligations": unresolved_obligations,
        "source_policy_execution_preflight": execution_preflight,
        "required_next_actions": required_next_actions,
        "nonheavy_negative_certificates": nonheavy_negative_certificates,
        "closure_decision": {
            "can_close_tfe_source_policy_rows_now": False,
            "can_claim_external_superiority_from_tfe_now": False,
            "reason": (
                "The self-reproduction reaches a paper-spec candidate layer with same-test work/precision, "
                "a five-method candidate dispatch contract, absolute-coordinate residual checks, and a "
                "full-T10 DAE-lift diagnostic. The current package also carries negative Brown--McPhee "
                "source-code-equivalence and full-T10 endpoint-policy certificates; those certificates "
                "document non-promotion boundaries but close zero source-policy rows. The package still "
                "lacks source-code-equivalent method runners, a monolithic absolute-coordinate "
                "source-policy DAE integrator, a Gauss6/FullVA source-policy runner, and accepted "
                "source-policy work/precision row bindings."
            ),
        },
        "same_test_candidate_method_summary": [
            {"paper_method": method, **summary_by_paper_method[method]}
            for method in TFE_B4_METHODS
        ],
        "row_dispositions": row_dispositions,
        "source_files": [
            "TFE_PUBLIC_CODE_RECHECK_20260613.json",
            "SOURCE_POLICY_PUBLIC_CODE_REFRESH_20260620.json",
            "TFE_SOURCE_POLICY_SPEC.json",
            "TFE_SOURCE_PENDULUM_MODEL_AUDIT.json",
            "TFE_DAE_RUNNER_CONTRACT_GAP_AUDIT.json",
            "TFE_BROWN_MCPHEE_SOURCE_LAW_BOUNDARY_AUDIT.json",
            "TFE_BROWN_MCPHEE_SOURCE_CODE_EQUIVALENCE_CERTIFICATE.json",
            "TFE_SOURCE_GRID_COMPATIBILITY_AUDIT.json",
            "TFE_FULL_T10_ENDPOINT_POLICY_CLOSURE_CERTIFICATE.json",
            "TFE_FULL_T10_ABSOLUTE_DAE_LIFT_SUMMARY.json",
            "../../numerics/v048_cross_paper_same_test_benchmarks/results/tfe_source_pendulum_same_test_work_precision.json",
            "../../numerics/v048_cross_paper_same_test_benchmarks/results/tfe_source_pendulum_same_test_work_precision_rows.csv",
            "../../numerics/v048_cross_paper_same_test_benchmarks/results/tfe_source_pendulum_same_test_work_precision_summary.csv",
        ],
    }

    OUT_JSON.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# TFE Source-Policy Self-Reproduction Attempt Certificate",
        "",
        "Status: **attempted not reproducible; not promoted**.",
        "",
        f"- Rows audited: `{output['row_count']}`.",
        f"- Self-reproduction attempted rows: `{output['self_reproduction_attempted_rows']}`.",
        f"- Attempted-not-reproducible rows: `{output['attempted_not_reproducible_rows']}`.",
        f"- Unable-to-reproduce rows: `{output['unable_to_reproduce_rows']}`.",
        f"- Final nonpublic-code disposition: `{output['final_nonpublic_code_disposition']}`.",
        f"- Source-policy closed rows: `{output['source_policy_closed_rows']}`.",
        f"- External-superiority ready rows: `{output['external_superiority_ready_rows']}`.",
        (
            "- Public-code recheck status/repo hits/user hits/code-search/attempted/closed: "
            f"`{output['public_code_status']['public_code_recheck_certificate_status']}/"
            f"{output['public_code_status']['public_code_recheck_github_repository_search_total_count']}/"
            f"{output['public_code_status']['public_code_recheck_github_user_search_total_count']}/"
            f"{output['public_code_status']['public_code_recheck_github_code_search_api_status']}/"
            f"{output['public_code_status']['public_code_recheck_attempted_not_reproducible_rows']}/"
            f"{output['public_code_status']['public_code_recheck_source_policy_rows_closed']}`."
        ),
        (
            "- Latest public-code refresh status/date/rows/queries/positive/closed: "
            f"`{output['public_code_refresh_latest_status']}/"
            f"{output['public_code_refresh_latest_date']}/"
            f"{output['public_code_refresh_latest_rows']}/"
            f"{output['public_code_refresh_latest_current_queries']}/"
            f"{output['public_code_refresh_latest_positive_artifact_rows']}/"
            f"{output['public_code_refresh_latest_source_policy_closed_ratio']}`."
        ),
        (
            "- Single-pendulum attempted / source-scope-unsupported mechanism rows: "
            f"`{output['single_pendulum_attempted_rows']}/"
            f"{output['source_scope_unsupported_mechanism_rows']}`."
        ),
        (
            "- Candidate same-test raw/summary/ok rows: "
            f"`{output['candidate_same_test_work_precision_rows']}/"
            f"{output['candidate_same_test_summary_rows']}/"
            f"{output['candidate_same_test_ok_rows']}`."
        ),
        (
            "- Source-method candidate contract rows/B4 coverage/source rows/equivalent method/DAE: "
            f"`{output['source_method_candidate_runner_contract']['row_count']}/"
            f"{output['source_method_candidate_runner_contract']['b4_method_coverage_count']}/"
            f"{output['source_method_candidate_runner_contract']['source_policy_rows_completed']}/"
            f"{output['source_method_candidate_runner_contract']['source_policy_method_runner_equivalent']}/"
            f"{output['source_method_candidate_runner_contract']['source_policy_dae_runner_equivalent']}`."
        ),
        (
            "- Source-method candidate contract finite/residual-below-1e-8/max residual: "
            f"`{output['source_method_candidate_runner_contract']['all_step_states_finite']}/"
            f"{output['source_method_candidate_runner_contract']['all_candidate_residuals_below_1e_8']}/"
            f"{output['source_method_candidate_runner_contract']['max_candidate_step_residual_norm']:.3e}`."
        ),
        (
            "- Gauss6/FullVA DAE candidate contract rows/source rows/equivalent DAE/FullVA: "
            f"`{output['gauss6_fullva_dae_candidate_contract']['row_count']}/"
            f"{output['gauss6_fullva_dae_candidate_contract']['source_policy_rows_completed']}/"
            f"{output['gauss6_fullva_dae_candidate_contract']['source_policy_dae_runner_equivalent']}/"
            f"{output['gauss6_fullva_dae_candidate_contract']['fullva_dae_source_policy_equivalent']}`."
        ),
        (
            "- Full-T10 DAE-lift completed / step residual rows: "
            f"`{reconstructed_layers['full_T10_absolute_dae_lift_completed']}/"
            f"{reconstructed_layers['full_T10_absolute_dae_lift_step_residual_rows']}`."
        ),
        (
            "- Source-policy DAE/method/monolithic equivalence: "
            f"`{unresolved_obligations['source_policy_dae_runner_equivalent']}/"
            f"{unresolved_obligations['source_policy_method_runner_equivalent']}/"
            f"{unresolved_obligations['monolithic_absolute_coordinate_dae_time_integrator']}`."
        ),
        (
            "- Brown--McPhee source law / transition policy / full-T10 grid policy: "
            f"`{unresolved_obligations['brown_mcphee_source_code_equivalent_law']}/"
            f"{unresolved_obligations['brown_mcphee_transition_velocity_policy_resolved_from_source']}/"
            f"{unresolved_obligations['source_grid_policy_resolved_for_full_T10']}`."
        ),
        (
            "- Non-heavy negative certificates Brown/endpoint status: "
            f"`{nonheavy_negative_certificates['brown_mcphee']['status']}/"
            f"{nonheavy_negative_certificates['full_T10_endpoint_policy']['status']}`."
        ),
        (
            "- Non-heavy certificates closed source-policy rows/blocks: "
            f"`{nonheavy_negative_certificates['source_policy_rows_completed_by_negative_certificates']}/"
            f"{nonheavy_negative_certificates['nonheavy_blocks_closed_by_negative_certificates']}`."
        ),
        (
            "- Source-policy execution preflight status/blocks/ready/promote: "
            f"`{execution_preflight.get('status')}/"
            f"{execution_preflight.get('execution_block_count')}/"
            f"{execution_preflight.get('ready_to_execute_source_policy_now')}/"
            f"{execution_preflight.get('can_promote_any_tfe_source_policy_row_now')}`."
        ),
        (
            "- Source-policy execution preflight route/reopen/source rows: "
            f"`{execution_preflight.get('current_route')}/"
            f"{execution_preflight.get('reopen_condition')}/"
            f"{execution_preflight.get('source_policy_rows_completed')}`."
        ),
        "",
        "## Required Next Actions",
        "",
        *[f"- {item}" for item in required_next_actions],
        "",
        "## B4 Method Summary",
        "",
        "| method | candidate rows | velocity floor | finest velocity error | source-policy row |",
        "|---|---:|---:|---:|---:|",
    ]
    for item in output["same_test_candidate_method_summary"]:
        lines.append(
            f"| `{item['paper_method']}` | `{item['candidate_summary_rows']}` | "
            f"`{item['velocity_pairwise_order_floor']:.3f}` | "
            f"`{item['finest_velocity_error_v']:.3e}` | "
            f"`{item['source_policy_row_completed']}` |"
        )
    lines.extend(
        [
            "",
            "## Row Disposition",
            "",
            "| method | example | disposition | reason |",
            "|---|---|---|---|",
        ]
    )
    for row in row_dispositions:
        lines.append(
            f"| `{row['method']}` | `{row['example']}` | "
            f"`{row['source_policy_disposition']}` | "
            f"`{row['primary_nonreproducibility_reason']}` |"
        )
    lines.extend(["", output["closure_decision"]["reason"], ""])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print("tfe_source_policy_self_reproduction_attempt_certificate=written")
    print(f"attempted_not_reproducible_rows={output['attempted_not_reproducible_rows']}/{output['row_count']}")
    print(f"unable_to_reproduce_rows={output['unable_to_reproduce_rows']}/{output['row_count']}")
    print(f"public_code_recheck_status={output['public_code_recheck_status']}")
    print(f"reopen_condition={output['reopen_condition']}")
    print(f"source_policy_execution_preflight_status={output['source_policy_execution_preflight_status']}")
    print(
        "public_code_refresh_latest_positive_artifact_rows="
        f"{output['public_code_refresh_latest_positive_artifact_rows']}"
    )
    print("source_policy_closed_rows=0")
    print("external_superiority_ready_rows=0")


if __name__ == "__main__":
    main()
