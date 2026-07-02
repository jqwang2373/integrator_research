#!/usr/bin/env python3
"""Build the B4 source-policy execution opt-in packet.

This packet is read-only. It packages the runnable B4 source-policy commands,
their row coverage, and the explicit user-opt-in boundary. It does not grant
permission to run the commands and it does not execute numerical runners.
"""

from __future__ import annotations

import json
import shlex
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
V048_WORKDIR = PAPER.parent / "v048_cross_paper_same_test_benchmarks"
OUT_JSON = PAPER / "B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json"
OUT_MD = PAPER / "B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.md"
DRIVER = PAPER / "run_b4_source_policy_after_opt_in.sh"


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def resolve_path(label: str | None) -> Path | None:
    if not label:
        return None
    path = Path(label)
    if path.is_absolute():
        return path
    return (PAPER / path).resolve()


def command_rows(row_ledger: dict[str, Any]) -> dict[str, list[dict[str, str]]]:
    out: dict[str, list[dict[str, str]]] = {}
    for row in row_ledger.get("rows", []):
        if not isinstance(row, dict):
            continue
        payload = {
            "suite_id": str(row.get("suite_id")),
            "method": str(row.get("method")),
            "example": str(row.get("example")),
            "readiness_status": str(row.get("readiness_status")),
        }
        for command_id in row.get("command_refs", []):
            out.setdefault(str(command_id), []).append(payload)
    return out


def resolve_from_workdir(label: str | None) -> Path | None:
    if not label:
        return None
    path = Path(label)
    if path.is_absolute():
        return path
    return (V048_WORKDIR / path).resolve()


def command_preflight(command_text: str | None) -> dict[str, Any]:
    text = str(command_text or "")
    shell_control_tokens = [";", "|", "&&", "||", ">", "<", "$(", "`"]
    try:
        argv = shlex.split(text)
        parse_ok = bool(argv)
        parse_error = None
    except ValueError as exc:
        argv = []
        parse_ok = False
        parse_error = str(exc)

    python_label = argv[0] if argv else None
    script_label = next((arg for arg in argv[1:] if arg.endswith(".py")), None)
    python_path = resolve_from_workdir(python_label)
    script_path = resolve_from_workdir(script_label)
    control_tokens_present = [token for token in shell_control_tokens if token in text]

    return {
        "schema": "b4-source-policy-command-preflight-v1",
        "execution_working_directory": "../v048_cross_paper_same_test_benchmarks",
        "execution_working_directory_exists": V048_WORKDIR.exists(),
        "argv": argv,
        "argc": len(argv),
        "parse_ok": parse_ok,
        "parse_error": parse_error,
        "python_executable": python_label,
        "python_executable_exists": bool(python_path and python_path.exists()),
        "runner_script": script_label,
        "runner_script_exists": bool(script_path and script_path.exists()),
        "shell_control_tokens_present": control_tokens_present,
        "shell_safe_single_command": parse_ok
        and not control_tokens_present
        and bool(python_path and python_path.exists())
        and bool(script_path and script_path.exists())
        and V048_WORKDIR.exists(),
        "dry_run_only": True,
        "executed_by_packet": False,
    }


def command_entry(command: dict[str, Any], rows_by_command: dict[str, list[dict[str, str]]]) -> dict[str, Any]:
    command_id = str(command.get("id"))
    command_text = command.get("command")
    expected_output = command.get("expected_output_after_run")
    expected_summary = command.get("expected_summary_after_run")
    output_path = resolve_path(expected_output)
    summary_path = resolve_path(expected_summary)
    mapped_rows = rows_by_command.get(command_id, [])
    return {
        "id": command_id,
        "command": command_text,
        "purpose": command.get("purpose"),
        "execution_preflight": command_preflight(str(command_text or "")),
        "expected_output_after_run": expected_output,
        "expected_summary_after_run": expected_summary,
        "expected_output_exists_now": bool(output_path and output_path.exists() and output_path.stat().st_size > 0),
        "expected_summary_exists_now": bool(summary_path and summary_path.exists() and summary_path.stat().st_size > 0)
        if expected_summary
        else None,
        "artifact_status": command.get("artifact_status", "not_run_by_this_packet"),
        "mapped_row_count": len(mapped_rows),
        "mapped_rows": mapped_rows,
    }


def acceptance_contract(batch_id: str) -> list[str]:
    common = [
        "execution was explicitly authorized by the user after this packet was produced",
        "expected output files exist and are nonempty",
        "row table uses the advertised source-policy step/reference/output policy",
        "error/order rows and runtime/Newton metrics are bound to the same accepted rows",
        "promotion validator records source-policy rows as closed before any B4/B7 closure claim",
        "work/precision figure uses only promoted rows and states the source policy",
    ]
    if batch_id == "ra2021_ready_after_explicit_1e_4_opt_in":
        return common + [
            "every RA2021 command includes --allow-source-policy-1e-4",
            "the public timing command and model-specific Gauss6/FullVA source-policy rows are both available",
        ]
    if batch_id == "hi2022_ready_no_1e_4_selected_candidate":
        return common + [
            "HI2022 selected-candidate commands do not use --allow-source-policy-1e-4",
            "isolated selected-candidate shards are not promoted unless full-policy figure scope is documented",
        ]
    return common


def unique_mapped_row_count(commands: list[dict[str, Any]]) -> int:
    keys = {
        (
            row.get("suite_id"),
            row.get("method"),
            row.get("example"),
        )
        for command in commands
        for row in command.get("mapped_rows", [])
        if isinstance(row, dict)
    }
    return len(keys)


def remaining_gap_program(
    unaddressed_rows: list[dict[str, Any]],
    b4: dict[str, Any],
    vp_audit: dict[str, Any],
    tfe_demotion_audit: dict[str, Any],
) -> dict[str, Any]:
    def count_rows(suite_id: str, *, example: str | None = None) -> int:
        return sum(
            1
            for row in unaddressed_rows
            if row.get("suite_id") == suite_id and (example is None or row.get("example") == example)
        )

    tfe_lane = next(
        (
            item
            for item in b4.get("execution_lanes", [])
            if isinstance(item, dict) and item.get("lane_id") == "tfe_source_policy_work_precision"
        ),
        {},
    )
    vp_lane = next(
        (
            item
            for item in b4.get("execution_lanes", [])
            if isinstance(item, dict) and item.get("lane_id") == "vp2024_source_code_path_work_precision"
        ),
        {},
    )
    hi_lane = next(
        (
            item
            for item in b4.get("execution_lanes", [])
            if isinstance(item, dict) and item.get("lane_id") == "hi2022_full_T8_work_precision"
        ),
        {},
    )
    vp_disposition = vp_audit.get("source_code_path_disposition", {})
    vp_source_rows = vp_audit.get("source_policy_rows", {})
    vp_coverage = vp_audit.get("coverage", {})
    candidate_entries = [
        {
            "id": "hi2022_single_pendulum_policy_gap",
            "suite_id": "hi2022_half_implicit",
            "row_count": count_rows("hi2022_half_implicit", example="single_pendulum"),
            "examples": ["single_pendulum"],
            "current_status": "not_mapped_to_current_hi2022_selected_candidate_preflight",
            "first_required_artifact": "extend HI2022 selected-candidate preflight to single_pendulum or keep HI2022 demoted from B4/B7 figures",
            "post_artifact_requirement": "bind full T=8 error/order rows and runtime/Newton work metrics to the same accepted rows",
            "ready_to_execute_now": False,
            "reason_not_ready_now": "the current HI2022 selected-candidate command set intentionally excludes single_pendulum",
            "requires_new_runner_or_code_path": False,
            "requires_source_policy_definition": True,
            "requires_explicit_heavy_run_opt_in_after_ready": True,
            "source_policy_1e_4_opt_in_required": hi_lane.get("source_policy_1e_4_opt_in_required"),
            "can_close_b4_b7_before_artifact": False,
        },
        {
            "id": "tfe_original_pendulum_runner_equivalence_gap",
            "suite_id": "tfe2026_original_pendulum",
            "row_count": count_rows("tfe2026_original_pendulum"),
            "examples": ["single_pendulum", "double_pendulum", "four_link", "slider_crank"],
            "current_status": "demoted_related_work_proxy_source_policy_runner_equivalence_open",
            "first_required_artifact": "TFE source-policy rows are demoted to related-work/formal-order comparator for the current claim; source-equivalent DAE runner certificate is required only before reintroducing TFE source-policy rows",
            "post_artifact_requirement": "run TFE m=1/m=2/Newmark/trapezoidal rows and local Gauss6 rows under one T=10 source reference policy",
            "ready_to_execute_now": False,
            "reason_not_ready_now": "pendulum DAE runner equivalence and full T=10 endpoint/output policy remain open",
            "requires_new_runner_or_code_path": True,
            "requires_source_policy_definition": True,
            "requires_explicit_heavy_run_opt_in_after_ready": True,
            "source_policy_1e_4_opt_in_required": tfe_lane.get("source_policy_1e_4_opt_in_required"),
            "demotion_audit_consumed": True,
            "demotion_audit": "TFE_B4_B7_SOURCE_POLICY_DEMOTION_AUDIT.json",
            "current_claim_requires_tfe_execution": tfe_demotion_audit.get(
                "current_claim_requires_tfe_source_policy_execution"
            ),
            "current_claim_requires_source_policy_execution": tfe_demotion_audit.get(
                "current_claim_requires_tfe_source_policy_execution"
            ),
            "demoted_related_work_proxy_rows_for_current_claim": tfe_demotion_audit.get(
                "demoted_related_work_proxy_rows_for_current_claim"
            ),
            "future_reintroduction_requires_runner_or_code_path_rows": tfe_demotion_audit.get(
                "future_reintroduction_requires_runner_or_code_path_rows"
            ),
            "claim_allowed_now": "source-policy-unresolved_related_work_formula_order_only",
            "preflight_closed_preconditions": tfe_lane.get("runner_equivalence_preflight_closed_preconditions"),
            "preflight_open_blockers": tfe_lane.get("runner_equivalence_preflight_open_blockers"),
            "candidate_work_precision_rows": tfe_lane.get("same_test_candidate_work_precision_rows"),
            "candidate_work_precision_methods": tfe_lane.get("same_test_candidate_work_precision_methods"),
            "can_close_b4_b7_before_artifact": False,
        },
        {
            "id": "vp2024_distinct_code_path_gap",
            "suite_id": "vp2024_velocity_partitioning",
            "row_count": count_rows("vp2024_velocity_partitioning"),
            "examples": ["single_pendulum", "double_pendulum", "four_link", "slider_crank"],
            "current_status": "attempted_not_reproducible_not_promoted_keep_proxy_diagnostic",
            "first_required_artifact": "VP2024 already demoted to related-work/proxy evidence for the current claim; resolve a distinct public velocity-partitioning code path only before reintroducing source-policy VP rows",
            "post_artifact_requirement": "extract source step/reference/output policy and run accepted order/work rows only if code path is resolved",
            "ready_to_execute_now": False,
            "reason_not_ready_now": "VP2024 audit records no distinct public code path; the coordinate-partitioning proxy is not a source-policy reproduction",
            "requires_new_runner_or_code_path": True,
            "requires_source_policy_definition": True,
            "requires_explicit_heavy_run_opt_in_after_ready": False,
            "source_policy_1e_4_opt_in_required": vp_lane.get("source_policy_1e_4_opt_in_required"),
            "demotion_audit_consumed": True,
            "demotion_audit": "VP2024_CODE_PATH_DISPOSITION_AUDIT.json",
            "current_claim_requires_vp_execution": False,
            "current_claim_requires_source_policy_execution": False,
            "claim_allowed_now": vp_disposition.get("claim_allowed_now"),
            "distinct_public_vp_code_path_found": vp_disposition.get("distinct_public_vp_code_path_found"),
            "proxy_is_source_policy_reproduction": vp_disposition.get(
                "coordinate_partitioning_proxy_is_source_policy_reproduction"
            ),
            "self_reproduction_attempted": vp_disposition.get("self_reproduction_attempted"),
            "unable_to_reproduce": vp_disposition.get("unable_to_reproduce"),
            "final_nonpublic_code_disposition": vp_disposition.get("final_nonpublic_code_disposition"),
            "source_policy_rows_closed": vp_source_rows.get("source_policy_rows_closed"),
            "source_policy_unresolved_rows": vp_coverage.get("source_policy_code_path_unresolved_rows"),
            "source_policy_rows_attempted_not_reproducible": vp_coverage.get(
                "source_policy_rows_attempted_not_reproducible"
            ),
            "source_policy_rows_unable_to_reproduce": vp_coverage.get("unable_to_reproduce_rows"),
            "common_reference_proxy_rows": vp_coverage.get("common_reference_proxy_rows"),
            "can_close_b4_b7_before_artifact": False,
        },
    ]
    entries = [entry for entry in candidate_entries if int(entry["row_count"]) > 0]
    return {
        "schema": "b4-source-policy-remaining-gap-program-v1",
        "status": f"remaining_{len(unaddressed_rows)}_rows_programmed_no_execution_invoked",
        "row_count": len(unaddressed_rows),
        "program_entry_count": len(entries),
        "all_entries_not_ready_to_execute_now": all(item["ready_to_execute_now"] is False for item in entries),
        "rows_requiring_new_runner_or_code_path": sum(
            int(item["row_count"]) for item in entries if item["requires_new_runner_or_code_path"] is True
        ),
        "rows_requiring_policy_definition": sum(
            int(item["row_count"]) for item in entries if item["requires_source_policy_definition"] is True
        ),
        "rows_demoted_related_work_proxy_for_current_claim": sum(
            int(item["row_count"])
            for item in entries
            if item.get("current_claim_requires_source_policy_execution") is False
            or item.get("current_claim_requires_tfe_execution") is False
            or item.get("current_claim_requires_vp_execution") is False
        ),
        "heavy_numerical_run_invoked": False,
        "run_v047_invoked": False,
        "v048_runner_invoked": False,
        "entries": entries,
    }


def post_execution_promotion_contract(
    *,
    b4: dict[str, Any],
    row_ledger: dict[str, Any],
    existing_promotion: dict[str, Any],
    ready_mapped_rows: int,
    unaddressed_rows: list[dict[str, Any]],
    gap_program: dict[str, Any],
) -> dict[str, Any]:
    publication_contract = b4.get("publication_grade_acceptance_contract", {})
    lane_summary = b4.get("execution_lane_summary", {})
    lanes = [item for item in b4.get("execution_lanes", []) if isinstance(item, dict)]
    ready_lanes = [
        item.get("lane_id")
        for item in lanes
        if item.get("ready_to_launch_after_explicit_opt_in") is True
    ]
    not_ready_lanes = [
        item.get("lane_id")
        for item in lanes
        if item.get("ready_to_launch_after_explicit_opt_in") is False
    ]
    checklist = [
        {
            "id": "source_policy_row_provenance",
            "required": True,
            "currently_satisfied": False,
            "current_evidence": f"{row_ledger.get('source_policy_rows_closed')}/{row_ledger.get('row_count')}",
            "acceptance_condition": (
                "each promoted row has a source-policy suite, method, example, horizon, step grid, "
                "reference policy, output variable set, and norm bound to the executed artifact"
            ),
        },
        {
            "id": "same_run_error_and_work_metrics",
            "required": True,
            "currently_satisfied": False,
            "current_evidence": "no promoted source-policy run records",
            "acceptance_condition": (
                "error/order rows and runtime/Newton/Jacobian/linear-solve work metrics come from the same "
                "accepted run records"
            ),
        },
        {
            "id": "diagnostic_rows_not_promoted",
            "required": True,
            "currently_satisfied": True,
            "current_evidence": (
                f"{existing_promotion.get('promotion_ready_without_new_execution_count')} existing artifacts "
                "are promotable without new execution"
            ),
            "acceptance_condition": (
                "common-reference, proxy, candidate, bounded-window, and same-window diagnostics remain labeled "
                "diagnostic unless their source-policy binding is separately verified"
            ),
        },
        {
            "id": "ready_command_rows_are_insufficient_by_themselves",
            "required": True,
            "currently_satisfied": True,
            "current_evidence": f"{ready_mapped_rows}/{row_ledger.get('row_count')} rows mapped by ready commands",
            "acceptance_condition": (
                "ready RA2021/HI2022 command output may be promoted only after row audits close; ready-command "
                "coverage alone cannot close B4/B7"
            ),
        },
        {
            "id": "remaining_gap_rows_stay_open_or_demoted",
            "required": True,
            "currently_satisfied": gap_program.get("rows_demoted_related_work_proxy_for_current_claim")
            == len(unaddressed_rows),
            "current_evidence": (
                f"{len(unaddressed_rows)} rows remain without executable source-policy commands and "
                f"{gap_program.get('rows_demoted_related_work_proxy_for_current_claim')}/{len(unaddressed_rows)} "
                "are explicitly demoted from current B4/B7 figures"
            ),
            "acceptance_condition": (
                "TFE runner-equivalence rows and VP2024 distinct-code-path rows are either closed by new "
                "source-policy evidence or remain explicitly demoted from B4/B7 figures"
            ),
        },
        {
            "id": "nonpublic_code_self_reproduction_disposition_recorded",
            "required": True,
            "currently_satisfied": row_ledger.get("source_policy_rows_attempted_not_reproducible") == 20,
            "current_evidence": (
                f"{row_ledger.get('source_policy_rows_attempted_not_reproducible')} attempted-not-reproducible "
                "rows recorded in SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_AUDIT.json"
            ),
            "acceptance_condition": (
                "rows without usable public code are explicitly attempted from the paper/source specification "
                "and marked not reproducible rather than left as unresolved execution work"
            ),
        },
        {
            "id": "publication_figures_rebuilt_from_promoted_rows",
            "required": True,
            "currently_satisfied": False,
            "current_evidence": "B7 is open and current figure set supports common-reference diagnostics only",
            "acceptance_condition": (
                "B4 work/precision figures and B7 baseline/work-precision figures are regenerated from promoted "
                "source-policy rows, with limitation labels for demoted suites"
            ),
        },
        {
            "id": "closure_validators_rerun_after_promotion",
            "required": True,
            "currently_satisfied": False,
            "current_evidence": "current packet is pre-execution and read-only",
            "acceptance_condition": (
                "after any promotion, rerun B4 row/readiness/promotion audits, blocker gate, review agent, "
                "reproducibility manifest, submission bundle, and full paper package validators"
            ),
        },
    ]
    return {
        "schema": "b4-source-policy-post-execution-promotion-contract-v1",
        "status": "promotion_contract_defined_no_rows_promoted",
        "source_publication_contract_id": publication_contract.get("contract_id"),
        "read_only": True,
        "post_execution_promotion_required": True,
        "source_policy_rows_closed_now": row_ledger.get("source_policy_rows_closed"),
        "source_policy_rows_total": row_ledger.get("row_count"),
        "source_policy_rows_attempted_not_reproducible": row_ledger.get(
            "source_policy_rows_attempted_not_reproducible"
        ),
        "source_policy_rows_still_requiring_execution_or_promotion": row_ledger.get(
            "source_policy_rows_still_requiring_execution_or_promotion"
        ),
        "ready_command_mapped_external_rows": ready_mapped_rows,
        "unaddressed_external_rows_after_ready_commands": len(unaddressed_rows),
        "existing_artifact_promotion_ready_count": existing_promotion.get(
            "promotion_ready_without_new_execution_count"
        ),
        "ready_lanes_after_explicit_opt_in": ready_lanes,
        "not_ready_lanes": not_ready_lanes,
        "lane_summary": {
            "ready_to_launch_after_explicit_opt_in_count": lane_summary.get(
                "ready_to_launch_after_explicit_opt_in_count"
            ),
            "not_ready_lane_count": lane_summary.get("not_ready_lane_count"),
            "source_policy_rows_closed_after_plan": lane_summary.get("source_policy_rows_closed_after_plan"),
            "source_policy_rows_total": lane_summary.get("source_policy_rows_total"),
        },
        "remaining_gap_program_status": gap_program.get("status"),
        "remaining_gap_rows_requiring_new_runner_or_code_path": gap_program.get(
            "rows_requiring_new_runner_or_code_path"
        ),
        "remaining_gap_rows_demoted_related_work_proxy_for_current_claim": gap_program.get(
            "rows_demoted_related_work_proxy_for_current_claim"
        ),
        "after_ready_commands_only": {
            "mapped_external_rows": ready_mapped_rows,
            "unaddressed_external_rows": len(unaddressed_rows),
            "b4_can_close": False,
            "b7_can_close": False,
            "reason": "ready commands cover only RA2021/selected HI2022 rows and still require post-run row promotion",
        },
        "promotion_checklist": checklist,
        "all_required_checks_satisfied_now": all(item["currently_satisfied"] for item in checklist),
        "b4_can_close_after_promotion_contract_now": False,
        "b7_can_close_after_promotion_contract_now": False,
        "closure_validator_sequence": [
            "validate_b4_source_policy_work_precision_execution_plan.py",
            "validate_b4_existing_artifact_promotion_audit.py",
            "validate_ra2021_double_source_policy_low_order_diagnosis.py",
            "validate_hi2022_ra_half_double_source_policy_failure_diagnosis.py",
            "validate_b4_source_policy_post_execution_audit.py",
            "validate_b4_source_policy_row_closure_readiness_ledger.py",
            "validate_b4_source_policy_execution_opt_in_packet.py",
            "validate_cmame_figure_set_audit.py",
            "validate_cmame_prose_residue_audit.py",
            "validate_cmame_review_agent.py",
            "validate_cmame_reproducibility_package_manifest.py",
            "validate_submission_bundle.py",
            "validate_paper_package.py",
        ],
    }


def main() -> None:
    b4 = read_json(PAPER / "B4_SOURCE_POLICY_WORK_PRECISION_EXECUTION_PLAN.json")
    row_ledger = read_json(PAPER / "B4_SOURCE_POLICY_ROW_CLOSURE_READINESS_LEDGER.json")
    existing_promotion = read_json(PAPER / "B4_EXISTING_ARTIFACT_PROMOTION_AUDIT.json")
    vp_audit = read_json(PAPER / "VP2024_CODE_PATH_DISPOSITION_AUDIT.json")
    tfe_demotion_audit = read_json(PAPER / "TFE_B4_B7_SOURCE_POLICY_DEMOTION_AUDIT.json")

    rows_by_command = command_rows(row_ledger)
    ra_commands = [
        command_entry(item, rows_by_command)
        for item in b4.get("ra2021_launch_preflight", {}).get("launch_commands", [])
        if isinstance(item, dict)
    ]
    hi_commands = [
        command_entry(item, rows_by_command)
        for item in b4.get("hi2022_launch_preflight", {}).get("launch_commands", [])
        if isinstance(item, dict)
    ]

    batches = [
        {
            "id": "ra2021_ready_after_explicit_1e_4_opt_in",
            "suite_id": "ra2021_absolute_coordinate",
            "status": "ready_not_run_requires_user_opt_in",
            "command_count": len(ra_commands),
            "mapped_external_rows": unique_mapped_row_count(ra_commands),
            "source_policy_1e_4_opt_in_required": True,
            "all_commands_require_allow_source_policy_1e_4": all(
                "--allow-source-policy-1e-4" in str(item.get("command")) for item in ra_commands
            ),
            "commands": ra_commands,
            "acceptance_contract": acceptance_contract("ra2021_ready_after_explicit_1e_4_opt_in"),
        },
        {
            "id": "hi2022_ready_no_1e_4_selected_candidate",
            "suite_id": "hi2022_half_implicit",
            "status": "preflight_ready_existing_selected_candidate_matrix_incomplete",
            "command_count": len(hi_commands),
            "mapped_external_rows": unique_mapped_row_count(hi_commands),
            "source_policy_1e_4_opt_in_required": False,
            "all_commands_avoid_allow_source_policy_1e_4": all(
                "--allow-source-policy-1e-4" not in str(item.get("command")) for item in hi_commands
            ),
            "commands": hi_commands,
            "acceptance_contract": acceptance_contract("hi2022_ready_no_1e_4_selected_candidate"),
        },
    ]

    terminal_attempted_rows = [
        row
        for row in row_ledger.get("rows", [])
        if isinstance(row, dict) and row.get("source_policy_disposition") == "attempted_not_reproducible"
    ]
    unaddressed_rows = [
        row
        for row in row_ledger.get("rows", [])
        if isinstance(row, dict)
        and not row.get("command_refs")
        and row.get("counts_as_open_execution_queue") is True
    ]
    all_commands = ra_commands + hi_commands
    command_preflights = [item.get("execution_preflight", {}) for item in all_commands]
    guarded_execution_protocol = {
        "schema": "b4-source-policy-guarded-execution-protocol-v1",
        "status": "dry_run_preflight_complete_execution_requires_exact_user_approval",
        "execution_working_directory": "../v048_cross_paper_same_test_benchmarks",
        "execution_working_directory_exists": V048_WORKDIR.exists(),
        "explicit_user_opt_in_required_before_any_command": True,
        "exact_approval_statement_required": (
            "I explicitly approve running the B4 source-policy execution commands listed in "
            "B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json."
        ),
        "packet_does_not_authorize_execution": True,
        "dry_run_only_until_approved": True,
        "execute_commands_now": False,
        "command_preflight_count": len(command_preflights),
        "all_commands_parse_ok": all(item.get("parse_ok") is True for item in command_preflights),
        "all_runner_scripts_exist": all(item.get("runner_script_exists") is True for item in command_preflights),
        "all_python_executables_exist": all(
            item.get("python_executable_exists") is True for item in command_preflights
        ),
        "all_commands_shell_safe_single_command": all(
            item.get("shell_safe_single_command") is True for item in command_preflights
        ),
        "heavy_numerical_run_invoked": False,
        "run_v047_invoked": False,
        "v048_runner_invoked": False,
    }
    gap_program = remaining_gap_program(unaddressed_rows, b4, vp_audit, tfe_demotion_audit)
    ready_mapped_rows = sum(int(batch["mapped_external_rows"]) for batch in batches)
    promotion_contract = post_execution_promotion_contract(
        b4=b4,
        row_ledger=row_ledger,
        existing_promotion=existing_promotion,
        ready_mapped_rows=ready_mapped_rows,
        unaddressed_rows=unaddressed_rows,
        gap_program=gap_program,
    )
    output: dict[str, Any] = {
        "schema": "b4-source-policy-execution-opt-in-packet-v1",
        "status": "ready_for_user_opt_in_packet_not_authorized_not_run",
        "read_only": True,
        "packet_does_not_authorize_execution": True,
        "explicit_user_opt_in_required_before_any_command": True,
        "source_policy_execution_allowed_now": False,
        "source_policy_execution_invoked": False,
        "exact_b4_opt_in_required_for_execution": True,
        "safe_action_ids": [
            "rebuild_read_only_audit_chain",
            "rerun_read_only_validators",
            "keep_narrowed_archive_provenance_only",
            "monitor_reopen_conditions",
        ],
        "opt_in_action_ids": ["authorized_b4_ra_hi_source_policy_execution"],
        "required_user_approval_statement": (
            "I explicitly approve running the B4 source-policy execution commands listed in "
            "B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json."
        ),
        "opt_in_required_phrase": (
            "I explicitly approve running the B4 source-policy execution commands listed in "
            "B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json."
        ),
        "exact_approval_statement": guarded_execution_protocol["exact_approval_statement_required"],
        "exact_required_user_approval_statement": guarded_execution_protocol[
            "exact_approval_statement_required"
        ],
        "commands_not_run_by_packet": True,
        "guarded_execution_driver_path": "run_b4_source_policy_after_opt_in.sh",
        "driver_requires_exact_approval": True,
        "driver_does_not_authorize_execution": True,
        "source_files": [
            "B4_SOURCE_POLICY_WORK_PRECISION_EXECUTION_PLAN.json",
            "B4_SOURCE_POLICY_ROW_CLOSURE_READINESS_LEDGER.json",
            "B4_EXISTING_ARTIFACT_PROMOTION_AUDIT.json",
            "RA2021_DOUBLE_SOURCE_POLICY_LOW_ORDER_DIAGNOSIS.json",
            "HI2022_RA_HALF_DOUBLE_SOURCE_POLICY_FAILURE_DIAGNOSIS.json",
            "TFE_B4_B7_SOURCE_POLICY_DEMOTION_AUDIT.json",
            "TFE_PUBLIC_CODE_RECHECK_20260613.json",
            "VP2024_CODE_PATH_DISPOSITION_AUDIT.json",
            "VP2024_PUBLIC_CODE_RECHECK_20260613.json",
            "SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_AUDIT.json",
            "SOURCE_POLICY_PUBLIC_CODE_REFRESH_20260614.json",
        ],
        "execution_invoked_by_packet": False,
        "heavy_numerical_run_invoked": False,
        "run_v047_invoked": False,
        "v048_runner_invoked": False,
        "source_policy_closed": False,
        "source_policy_closed_ratio": f"{row_ledger.get('source_policy_rows_closed')}/{row_ledger.get('row_count')}",
        "source_policy_rows_closed_now": row_ledger.get("source_policy_rows_closed"),
        "source_policy_rows_total": row_ledger.get("row_count"),
        "source_policy_rows_attempted_not_reproducible": row_ledger.get(
            "source_policy_rows_attempted_not_reproducible"
        ),
        "attempted_not_reproducible_rows": row_ledger.get(
            "source_policy_rows_attempted_not_reproducible"
        ),
        "source_policy_rows_still_requiring_execution_or_promotion": row_ledger.get(
            "source_policy_rows_still_requiring_execution_or_promotion"
        ),
        "ready_command_batch_count": len(batches),
        "ready_command_count": sum(int(batch["command_count"]) for batch in batches),
        "ready_command_mapped_external_rows": ready_mapped_rows,
        "unaddressed_external_rows_after_ready_commands": len(unaddressed_rows),
        "b4_can_close_now": False,
        "b7_can_close_now": False,
        "b4_can_close_after_ready_commands_only": False,
        "b7_can_close_after_ready_commands_only": False,
        "existing_artifact_promotion_ready_count": existing_promotion.get(
            "promotion_ready_without_new_execution_count"
        ),
        "guarded_execution_protocol": guarded_execution_protocol,
        "guarded_execution_driver": {
            "path": "run_b4_source_policy_after_opt_in.sh",
            "exists": DRIVER.exists(),
            "requires_exact_approval_argument": True,
            "approval_argument": guarded_execution_protocol["exact_approval_statement_required"],
            "executes_packet_command_count": sum(int(batch["command_count"]) for batch in batches),
            "post_execution_validator_sequence_included": True,
            "driver_does_not_authorize_execution": True,
        },
        "remaining_gap_program": gap_program,
        "execution_batches": batches,
        "unaddressed_row_summary": {
            "tfe2026_original_pendulum": sum(
                1 for row in unaddressed_rows if row.get("suite_id") == "tfe2026_original_pendulum"
            ),
            "vp2024_velocity_partitioning": sum(
                1 for row in unaddressed_rows if row.get("suite_id") == "vp2024_velocity_partitioning"
            ),
            "hi2022_half_implicit_single_pendulum": sum(
                1
                for row in unaddressed_rows
                if row.get("suite_id") == "hi2022_half_implicit" and row.get("example") == "single_pendulum"
            ),
        },
        "terminal_attempted_not_reproducible_row_summary": {
            "tfe2026_original_pendulum": sum(
                1 for row in terminal_attempted_rows if row.get("suite_id") == "tfe2026_original_pendulum"
            ),
            "vp2024_velocity_partitioning": sum(
                1 for row in terminal_attempted_rows if row.get("suite_id") == "vp2024_velocity_partitioning"
            ),
            "total": len(terminal_attempted_rows),
        },
        "unaddressed_rows": [
            {
                "suite_id": row.get("suite_id"),
                "method": row.get("method"),
                "example": row.get("example"),
                "readiness_status": row.get("readiness_status"),
                "first_blocker": (row.get("blocking_reasons") or [""])[0],
            }
            for row in unaddressed_rows
        ],
        "terminal_attempted_not_reproducible_rows": [
            {
                "suite_id": row.get("suite_id"),
                "method": row.get("method"),
                "example": row.get("example"),
                "readiness_status": row.get("readiness_status"),
                "first_blocker": row.get("primary_promotion_blocker"),
                "evidence": row.get("self_reproduction_evidence_ref"),
            }
            for row in terminal_attempted_rows
        ],
        "post_execution_promotion_required": True,
        "post_execution_promotion_contract": promotion_contract,
        "post_execution_promotion_requirements": [
            "regenerate source-policy row audits from executed artifacts",
            "promote rows only after source-policy step/reference/output/runtime binding is verified",
            "rebuild B4 work/precision figures from promoted rows",
            "rerun blocker gate, review agent, reproducibility manifest, submission bundle, and full paper package validators",
        ],
    }

    with OUT_JSON.open("w", encoding="utf-8") as handle:
        json.dump(output, handle, indent=2, sort_keys=True)
        handle.write("\n")

    lines = [
        "# B4 Source-Policy Execution Opt-In Packet",
        "",
        f"Status: `{output['status']}`.",
        "",
        "This packet is read-only. It does not authorize or run numerical execution.",
        "",
        f"- Explicit user opt-in required: `{output['explicit_user_opt_in_required_before_any_command']}`.",
        f"- Ready command batches/count: `{output['ready_command_batch_count']}/{output['ready_command_count']}`.",
        f"- Ready command mapped external rows: `{output['ready_command_mapped_external_rows']}/{output['source_policy_rows_total']}`.",
        f"- Unaddressed external rows after ready commands: `{output['unaddressed_external_rows_after_ready_commands']}`.",
        f"- Attempted-not-reproducible external rows: `{output['source_policy_rows_attempted_not_reproducible']}`.",
        f"- External rows still requiring execution/promotion: `{output['source_policy_rows_still_requiring_execution_or_promotion']}`.",
        f"- Source-policy rows closed now: `{output['source_policy_rows_closed_now']}/{output['source_policy_rows_total']}`.",
        f"- Source-policy execution allowed now/invoked/exact opt-in required: `{output['source_policy_execution_allowed_now']}/{output['source_policy_execution_invoked']}/{output['exact_b4_opt_in_required_for_execution']}`.",
        f"- Safe action ids: `{','.join(output['safe_action_ids'])}`.",
        f"- Opt-in action ids: `{','.join(output['opt_in_action_ids'])}`.",
        f"- B4/B7 can close now: `{output['b4_can_close_now']}/{output['b7_can_close_now']}`.",
        f"- B4/B7 can close after ready commands only: `{output['b4_can_close_after_ready_commands_only']}/{output['b7_can_close_after_ready_commands_only']}`.",
        f"- Heavy/run_v047/v048 invoked: `{output['heavy_numerical_run_invoked']}/{output['run_v047_invoked']}/{output['v048_runner_invoked']}`.",
            f"- Command preflight parse/runner/python/shell-safe: "
            f"`{guarded_execution_protocol['all_commands_parse_ok']}/"
            f"{guarded_execution_protocol['all_runner_scripts_exist']}/"
            f"{guarded_execution_protocol['all_python_executables_exist']}/"
            f"{guarded_execution_protocol['all_commands_shell_safe_single_command']}`.",
            f"- Remaining gap program rows/entries: `{gap_program['row_count']}/{gap_program['program_entry_count']}`.",
            f"- TFE rows attempted-not-reproducible: `{output['terminal_attempted_not_reproducible_row_summary']['tfe2026_original_pendulum']}`.",
            f"- VP2024 rows attempted-not-reproducible: `{output['terminal_attempted_not_reproducible_row_summary']['vp2024_velocity_partitioning']}`.",
            f"- Rows demoted related-work/proxy for current claim: `{gap_program['rows_demoted_related_work_proxy_for_current_claim']}`.",
            f"- Post-execution promotion contract: `{promotion_contract['schema']}` / `{promotion_contract['status']}`.",
            f"- Promotion checklist satisfied now: `{promotion_contract['all_required_checks_satisfied_now']}`.",
        "",
        "## Objective Blocker Matrix",
        "",
        "This packet is an OC4 execution handoff artifact. It does not close the global objective blockers.",
        "",
        "- `blocker_open_by_id=OC4:True,OC6:True,OC12:True`",
        "- `blocker_closure_decision_by_id=OC4:remain_open_ready_for_authorized_execution_not_executed_not_promoted,OC6:remain_open_no_positive_source_equivalent_artifact,OC12:remain_partial_narrowed_replay_ready_full_source_policy_archive_not_ready`",
        "- `blocker_closure_allowed_by_id=OC4:False,OC6:False,OC12:False`",
        "",
        "Required approval statement:",
        "",
        f"`{output['required_user_approval_statement']}`",
        "",
        "Guarded execution driver:",
        "",
        "- `run_b4_source_policy_after_opt_in.sh` is a prepared local driver for the packet commands.",
        "- It refuses to execute unless the exact approval statement above is passed as its first argument.",
        "- It is not an authorization artifact and does not change the current read-only packet status.",
        "",
        "## Ready Batches",
        "",
        "| batch | commands | mapped rows | 1e-4 opt-in |",
        "|---|---:|---:|---:|",
    ]
    for batch in batches:
        lines.append(
            f"| `{batch['id']}` | `{batch['command_count']}` | `{batch['mapped_external_rows']}` | "
            f"`{batch['source_policy_1e_4_opt_in_required']}` |"
        )
    lines.extend(
        [
            "",
            "## Guarded Execution Protocol",
            "",
            f"- Status: `{guarded_execution_protocol['status']}`.",
            f"- Execution working directory: `{guarded_execution_protocol['execution_working_directory']}`.",
            f"- Command preflights: `{guarded_execution_protocol['command_preflight_count']}`.",
            f"- All commands parse: `{guarded_execution_protocol['all_commands_parse_ok']}`.",
            f"- All runner scripts exist: `{guarded_execution_protocol['all_runner_scripts_exist']}`.",
            f"- All Python executables exist: `{guarded_execution_protocol['all_python_executables_exist']}`.",
            f"- All commands shell-safe single command: `{guarded_execution_protocol['all_commands_shell_safe_single_command']}`.",
            f"- Execute commands now: `{guarded_execution_protocol['execute_commands_now']}`.",
            f"- Dry-run only until approved: `{guarded_execution_protocol['dry_run_only_until_approved']}`.",
            "",
        ]
    )
    lines.extend(
        [
            "",
            "## Unaddressed Rows",
            "",
            f"- TFE rows without launch commands: `{output['unaddressed_row_summary']['tfe2026_original_pendulum']}`.",
            f"- VP2024 rows without launch commands: `{output['unaddressed_row_summary']['vp2024_velocity_partitioning']}`.",
            "- TFE current-claim disposition: `attempted_not_reproducible; related-work/formal-order comparator only; source-policy rows remain 0/16`.",
            "- VP2024 current-claim disposition: `attempted_not_reproducible; related-work/proxy only; source-policy rows remain 0/4`.",
            f"- HI2022 single-pendulum rows outside selected-candidate preflight: `{output['unaddressed_row_summary']['hi2022_half_implicit_single_pendulum']}`.",
            f"- Terminal attempted-not-reproducible rows: `{output['terminal_attempted_not_reproducible_row_summary']['total']}`.",
            f"- Terminal attempted-not-reproducible evidence: `SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_AUDIT.json`.",
            "",
            "## Remaining Gap Program",
            "",
            f"Status: `{gap_program['status']}`.",
            "",
            "| gap | rows | first required artifact | ready now |",
            "|---|---:|---|---:|",
        ]
    )
    for entry in gap_program["entries"]:
        lines.append(
            f"| `{entry['id']}` | `{entry['row_count']}` | {entry['first_required_artifact']} | "
            f"`{entry['ready_to_execute_now']}` |"
        )
    lines.extend(
        [
            "",
            "Post-execution promotion is still required before any B4/B7 closure claim.",
            "",
            "## Post-Execution Promotion Contract",
            "",
            f"- Contract: `{promotion_contract['schema']}`.",
            f"- Status: `{promotion_contract['status']}`.",
            f"- Source publication contract: `{promotion_contract['source_publication_contract_id']}`.",
            f"- Rows closed now: `{promotion_contract['source_policy_rows_closed_now']}/{promotion_contract['source_policy_rows_total']}`.",
            f"- Attempted-not-reproducible rows: `{promotion_contract['source_policy_rows_attempted_not_reproducible']}`.",
            f"- Rows still requiring execution/promotion: `{promotion_contract['source_policy_rows_still_requiring_execution_or_promotion']}`.",
            f"- Ready mapped/unaddressed rows: `{promotion_contract['ready_command_mapped_external_rows']}/{promotion_contract['unaddressed_external_rows_after_ready_commands']}`.",
            f"- Existing-artifact promotion-ready count: `{promotion_contract['existing_artifact_promotion_ready_count']}`.",
            f"- Ready/not-ready lanes: `{len(promotion_contract['ready_lanes_after_explicit_opt_in'])}/{len(promotion_contract['not_ready_lanes'])}`.",
            f"- Remaining gap rows requiring runner/code path: `{promotion_contract['remaining_gap_rows_requiring_new_runner_or_code_path']}`.",
            f"- Remaining gap rows demoted related-work/proxy for current claim: `{promotion_contract['remaining_gap_rows_demoted_related_work_proxy_for_current_claim']}`.",
            f"- After ready commands only can close B4/B7: `{promotion_contract['after_ready_commands_only']['b4_can_close']}/{promotion_contract['after_ready_commands_only']['b7_can_close']}`.",
            f"- All required promotion checks satisfied now: `{promotion_contract['all_required_checks_satisfied_now']}`.",
            "",
            "| check | satisfied now | acceptance condition |",
            "|---|---:|---|",
        ]
    )
    for item in promotion_contract["promotion_checklist"]:
        lines.append(
            f"| `{item['id']}` | `{item['currently_satisfied']}` | {item['acceptance_condition']} |"
        )
    lines.extend(
        [
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print("b4_source_policy_execution_opt_in_packet=written")
    print(f"ready_command_count={output['ready_command_count']}")
    print(f"ready_command_mapped_external_rows={output['ready_command_mapped_external_rows']}/40")
    print(f"unaddressed_external_rows={output['unaddressed_external_rows_after_ready_commands']}")
    print(f"attempted_not_reproducible_rows={output['source_policy_rows_attempted_not_reproducible']}")
    print("execution_invoked_by_packet=False")
    print("b4_can_close_after_ready_commands_only=False")


if __name__ == "__main__":
    main()
