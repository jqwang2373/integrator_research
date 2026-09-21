#!/usr/bin/env python3
"""Build a read-only OC6 source-equivalent reopen-readiness audit.

OC6 is blocked by TFE/VP source-policy rows that are terminal
unable-to-reproduce unless a new public or source-code-equivalent artifact
appears.  This audit consolidates the existing local 2026-06-20 refresh,
reopen monitor, self-reproduction, and TFE runner-contract evidence without
performing a new public-code search or running any numerical command.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
OUT_JSON = PAPER / "OC6_SOURCE_EQUIVALENT_REOPEN_READINESS_AUDIT_20260620.json"
OUT_MD = PAPER / "OC6_SOURCE_EQUIVALENT_REOPEN_READINESS_AUDIT_20260620.md"
SCHEMA = "oc6-source-equivalent-reopen-readiness-audit-20260620-v1"
STATUS = "oc6_reopen_conditions_monitored_no_positive_source_equivalent_artifact"
SOURCE_FILES = [
    "SOURCE_POLICY_PUBLIC_CODE_REFRESH_20260620.json",
    "SOURCE_POLICY_REOPEN_CONDITION_MONITOR_20260620.json",
    "SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_AUDIT.json",
    "TFE_SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_CERTIFICATE.json",
    "TFE_PUBLIC_CODE_RECHECK_20260613.json",
    "VP2024_PUBLIC_CODE_RECHECK_20260613.json",
    "TFE_DAE_RUNNER_CONTRACT_GAP_AUDIT.json",
    "TFE_RUNNER_CONTRACT_PREFLIGHT_CERTIFICATE.json",
    "TFE_BROWN_MCPHEE_SOURCE_CODE_EQUIVALENCE_CERTIFICATE.json",
    "TFE_FULL_T10_ENDPOINT_POLICY_CLOSURE_CERTIFICATE.json",
]
SUITE_REOPEN_CONDITIONS = {
    "tfe2026_original_pendulum": "new_public_or_source_code_equivalent_tfe_implementation_artifact",
    "vp2024_velocity_partitioning": "new_distinct_public_vp2024_velocity_partitioning_code_path",
}
SAFE_ACTIONS_WITHOUT_B4_OPT_IN = [
    {
        "action_id": "rebuild_read_only_audit_chain",
        "description": "Regenerate read-only audit/manifest/review artifacts from existing evidence.",
    },
    {
        "action_id": "rerun_read_only_validators",
        "description": "Run validators that inspect artifacts without launching numerical campaigns.",
    },
    {
        "action_id": "keep_narrowed_archive_provenance_only",
        "description": "Use the current archive only for narrowed-claim replay and provenance evidence.",
    },
    {
        "action_id": "monitor_reopen_conditions",
        "description": "Refresh read-only reopen-condition monitors for new local/public-code evidence.",
    },
]
SAFE_ACTION_IDS = [item["action_id"] for item in SAFE_ACTIONS_WITHOUT_B4_OPT_IN]
OPT_IN_ACTION_IDS = ["authorized_b4_ra_hi_source_policy_execution"]
REQUIRED_USER_APPROVAL_STATEMENT = (
    "I explicitly approve running the B4 source-policy execution commands listed in "
    "B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json."
)
BLOCKER_IDS = ["OC4", "OC6", "OC12"]
BLOCKER_OPEN_BY_ID = {"OC4": True, "OC6": True, "OC12": True}
BLOCKER_CLOSURE_DECISION_BY_ID = {
    "OC4": "remain_open_ready_for_authorized_execution_not_executed_not_promoted",
    "OC6": "remain_open_no_positive_source_equivalent_artifact",
    "OC12": "remain_partial_narrowed_replay_ready_full_source_policy_archive_not_ready",
}
BLOCKER_CLOSURE_ALLOWED_BY_ID = {"OC4": False, "OC6": False, "OC12": False}


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def canonical_digest(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return sha256_text(payload)


def count_by(rows: list[dict[str, Any]], key: str) -> dict[str, int]:
    return dict(sorted(Counter(str(row.get(key)) for row in rows).items()))


def blocker_token(values: dict[str, Any]) -> str:
    return ",".join(f"{blocker_id}:{values[blocker_id]}" for blocker_id in BLOCKER_IDS)


def int0(value: Any) -> int:
    return int(value or 0)


def suite_summary(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    summaries: list[dict[str, Any]] = []
    for suite_id in sorted(SUITE_REOPEN_CONDITIONS):
        suite_rows = [row for row in rows if row.get("suite_id") == suite_id]
        summaries.append(
            {
                "suite_id": suite_id,
                "row_count": len(suite_rows),
                "unable_to_reproduce_rows": sum(1 for row in suite_rows if row.get("unable_to_reproduce") is True),
                "public_code_available_rows": sum(1 for row in suite_rows if row.get("public_code_available") is True),
                "candidate_runner_available_rows": sum(
                    1 for row in suite_rows if row.get("candidate_runner_available") is True
                ),
                "candidate_runner_source_policy_equivalent_rows": sum(
                    1
                    for row in suite_rows
                    if row.get("candidate_runner_source_policy_equivalent") is True
                ),
                "source_policy_closed_rows": sum(1 for row in suite_rows if row.get("source_policy_closed") is True),
                "external_superiority_ready_rows": sum(
                    1 for row in suite_rows if row.get("external_superiority_ready") is True
                ),
                "post_execution_decision_counts": count_by(suite_rows, "post_execution_decision"),
                "primary_nonreproducibility_reason_counts": count_by(
                    suite_rows, "primary_nonreproducibility_reason"
                ),
                "reopen_condition": SUITE_REOPEN_CONDITIONS[suite_id],
            }
        )
    return summaries


def row_record(row: dict[str, Any]) -> dict[str, Any]:
    suite_id = str(row.get("suite_id"))
    return {
        "row_id": row.get("row_id"),
        "suite_id": suite_id,
        "method": row.get("method"),
        "example": row.get("example"),
        "public_code_available": row.get("public_code_available"),
        "candidate_runner_available": row.get("candidate_runner_available"),
        "candidate_runner_source_policy_equivalent": row.get(
            "candidate_runner_source_policy_equivalent"
        ),
        "source_policy_dae_runner_equivalent": row.get("source_policy_dae_runner_equivalent"),
        "source_policy_method_runner_equivalent": row.get(
            "source_policy_method_runner_equivalent"
        ),
        "unable_to_reproduce": row.get("unable_to_reproduce"),
        "source_policy_closed": row.get("source_policy_closed"),
        "external_superiority_ready": row.get("external_superiority_ready"),
        "post_execution_decision": row.get("post_execution_decision"),
        "source_policy_disposition": row.get("source_policy_disposition"),
        "accepted_use": row.get("accepted_use"),
        "primary_nonreproducibility_reason": row.get("primary_nonreproducibility_reason"),
        "counts_as_open_execution_queue": row.get("counts_as_open_execution_queue"),
        "reopen_condition": SUITE_REOPEN_CONDITIONS.get(suite_id),
    }


def build_payload() -> dict[str, Any]:
    public_refresh = read_json(PAPER / "SOURCE_POLICY_PUBLIC_CODE_REFRESH_20260620.json")
    reopen_monitor = read_json(PAPER / "SOURCE_POLICY_REOPEN_CONDITION_MONITOR_20260620.json")
    self_attempt = read_json(PAPER / "SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_AUDIT.json")
    tfe_self = read_json(PAPER / "TFE_SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_CERTIFICATE.json")
    tfe_public = read_json(PAPER / "TFE_PUBLIC_CODE_RECHECK_20260613.json")
    vp_public = read_json(PAPER / "VP2024_PUBLIC_CODE_RECHECK_20260613.json")
    tfe_gap = read_json(PAPER / "TFE_DAE_RUNNER_CONTRACT_GAP_AUDIT.json")
    tfe_runner = read_json(PAPER / "TFE_RUNNER_CONTRACT_PREFLIGHT_CERTIFICATE.json")
    brown_mcphee = read_json(PAPER / "TFE_BROWN_MCPHEE_SOURCE_CODE_EQUIVALENCE_CERTIFICATE.json")
    endpoint = read_json(PAPER / "TFE_FULL_T10_ENDPOINT_POLICY_CLOSURE_CERTIFICATE.json")

    rows = [
        row_record(row)
        for row in self_attempt.get("rows", [])
        if isinstance(row, dict) and row.get("suite_id") in SUITE_REOPEN_CONDITIONS
    ]
    rows.sort(key=lambda row: (str(row["suite_id"]), str(row["method"]), str(row["example"])))
    summaries = suite_summary(rows)
    latest_external_probe_rows = [
        row for row in public_refresh.get("latest_external_probe_rows", []) if isinstance(row, dict)
    ]
    latest_external_probe_rows_by_suite = count_by(latest_external_probe_rows, "suite_id")
    tfe_preflight = tfe_gap.get("source_policy_execution_preflight", {})
    tfe_missing_scope = tfe_gap.get("source_policy_execution_missing_scope", {})
    runner_matrix_summary = tfe_runner.get("source_policy_execution_block_matrix_summary", {})
    reopen_summary = {
        "public_refresh_status": public_refresh.get("status"),
        "public_refresh_date_checked": public_refresh.get("date_checked"),
        "public_refresh_rows": public_refresh.get("row_count"),
        "public_refresh_current_queries": public_refresh.get("current_query_count"),
        "public_refresh_positive_public_code_artifact_rows": public_refresh.get(
            "positive_public_code_artifact_rows"
        ),
        "public_refresh_local_positive_reopen_artifact_rows": public_refresh.get(
            "local_positive_reopen_artifact_rows"
        ),
        "public_refresh_source_policy_reopen_triggered": public_refresh.get(
            "source_policy_reopen_triggered"
        ),
        "public_refresh_source_policy_rows_closed": public_refresh.get(
            "source_policy_rows_closed"
        ),
        "public_refresh_latest_external_probe_marker": public_refresh.get(
            "latest_external_probe_marker"
        ),
        "latest_external_probe_date_checked": public_refresh.get(
            "latest_external_probe_date_checked"
        ),
        "latest_external_probe_count": public_refresh.get("latest_external_probe_count"),
        "latest_external_probe_positive_public_code_artifact_rows": public_refresh.get(
            "latest_external_probe_positive_public_code_artifact_rows"
        ),
        "latest_external_probe_source_policy_rows_closed": public_refresh.get(
            "latest_external_probe_source_policy_rows_closed"
        ),
        "latest_external_probe_access_limited_count": public_refresh.get(
            "latest_external_probe_access_limited_count"
        ),
        "latest_external_probe_global_absence_proved": public_refresh.get(
            "latest_external_probe_global_absence_proved"
        ),
        "latest_external_probe_source_policy_reopen_triggered": public_refresh.get(
            "latest_external_probe_source_policy_reopen_triggered"
        ),
        "latest_external_probe_marker": public_refresh.get("latest_external_probe_marker"),
        "reopen_monitor_status": reopen_monitor.get("status"),
        "reopen_monitor_date_checked": reopen_monitor.get("date_checked"),
        "reopen_monitor_unable_to_reproduce_rows": reopen_monitor.get(
            "unable_to_reproduce_rows"
        ),
        "reopen_monitor_positive_public_code_artifact_rows": reopen_monitor.get(
            "positive_public_code_artifact_rows"
        ),
        "reopen_monitor_local_positive_reopen_artifact_rows": reopen_monitor.get(
            "local_positive_reopen_artifact_rows"
        ),
        "reopen_monitor_source_policy_reopen_triggered": reopen_monitor.get(
            "source_policy_reopen_triggered"
        ),
    }
    tfe_reopen_summary = {
        "self_reproduction_status": tfe_self.get("status"),
        "self_reproduction_source_policy_closed_ratio": tfe_self.get(
            "source_policy_closed_ratio"
        ),
        "self_reproduction_unable_to_reproduce_rows": tfe_self.get(
            "unable_to_reproduce_rows"
        ),
        "public_code_recheck_status": tfe_public.get("status"),
        "public_code_recheck_repository_hits": tfe_public.get("coverage", {}).get(
            "github_repository_search_total_count"
        ),
        "public_code_recheck_user_hits": tfe_public.get("coverage", {}).get(
            "github_user_search_total_count"
        ),
        "public_code_recheck_direct_code_hits": tfe_public.get("coverage", {}).get(
            "direct_public_code_hit_count"
        ),
        "brown_mcphee_source_code_equivalent_law": brown_mcphee.get(
            "brown_mcphee_source_code_equivalent_law"
        ),
        "full_T10_endpoint_policy_resolved": endpoint.get(
            "source_grid_policy_resolved_for_full_T10"
        ),
        "source_policy_execution_preflight_status": tfe_preflight.get("status"),
        "ready_to_execute_source_policy_now": tfe_preflight.get(
            "ready_to_execute_source_policy_now"
        ),
        "can_promote_any_tfe_source_policy_row_now": tfe_preflight.get(
            "can_promote_any_tfe_source_policy_row_now"
        ),
        "execution_block_count": tfe_preflight.get("execution_block_count"),
        "effective_missing_contract_block_count": tfe_gap.get(
            "effective_missing_contract_block_count"
        ),
        "terminal_nonpromoted_contract_block_count": tfe_gap.get(
            "terminal_nonpromoted_contract_block_count"
        ),
        "requires_new_public_or_source_code_equivalent_artifact_to_reopen": (
            tfe_missing_scope.get(
                "requires_new_public_or_source_code_equivalent_artifact_to_reopen"
            )
        ),
        "source_policy_rows_completed": tfe_preflight.get("source_policy_rows_completed"),
        "runner_contract_preflight_status": tfe_runner.get("status"),
        "runner_contract_entrypoints": tfe_runner.get("entrypoint_count"),
        "runner_contract_callable": tfe_runner.get("callable_contract_count"),
        "runner_contract_candidate_backed": tfe_runner.get(
            "candidate_backed_contract_count"
        ),
        "runner_contract_source_policy_equivalent_blocks": runner_matrix_summary.get(
            "source_policy_equivalent_blocks"
        ),
        "runner_contract_requires_new_artifact_or_execution_blocks": runner_matrix_summary.get(
            "requires_new_artifact_or_execution_blocks"
        ),
        "runner_contract_safe_current_use": tfe_runner.get("safe_current_use"),
    }
    vp_reopen_summary = {
        "public_code_recheck_status": vp_public.get("status"),
        "source_policy_rows_attempted_not_reproducible": vp_public.get("coverage", {}).get(
            "source_policy_rows_attempted_not_reproducible"
        ),
        "source_policy_rows_closed": vp_public.get("coverage", {}).get(
            "source_policy_rows_closed"
        ),
        "tree_total_paths": vp_public.get("coverage", {}).get("tree_total_paths"),
        "year2024_path_count": vp_public.get("coverage", {}).get("year2024_path_count"),
        "keyword_path_hit_count": vp_public.get("coverage", {}).get("keyword_path_hit_count"),
        "can_close_vp2024_source_policy_rows_now": vp_public.get("decision", {}).get(
            "can_close_vp2024_source_policy_rows_now"
        ),
        "row_disposition": vp_public.get("decision", {}).get("row_disposition"),
        "reopen_condition": SUITE_REOPEN_CONDITIONS["vp2024_velocity_partitioning"],
    }
    digest_inputs = {
        "reopen_summary": reopen_summary,
        "tfe_reopen_summary": tfe_reopen_summary,
        "vp_reopen_summary": vp_reopen_summary,
        "latest_external_probe_rows_by_suite": latest_external_probe_rows_by_suite,
        "latest_external_probe_rows": latest_external_probe_rows,
        "suite_summary": summaries,
        "rows": rows,
    }
    source_policy_rows_closed = sum(1 for row in rows if row["source_policy_closed"] is True)
    candidate_source_equivalent_rows = sum(
        1 for row in rows if row["candidate_runner_source_policy_equivalent"] is True
    )
    source_policy_closed_ratio = f"{source_policy_rows_closed}/{len(rows)}"
    runner_contract_summary = {
        "status": tfe_runner.get("status"),
        "entrypoint_count": tfe_runner.get("entrypoint_count"),
        "callable_contract_count": tfe_runner.get("callable_contract_count"),
        "candidate_backed_contract_count": tfe_runner.get("candidate_backed_contract_count"),
        "source_policy_equivalent_blocks": runner_matrix_summary.get(
            "source_policy_equivalent_blocks"
        ),
        "requires_new_artifact_or_execution_blocks": runner_matrix_summary.get(
            "requires_new_artifact_or_execution_blocks"
        ),
        "safe_current_use": tfe_runner.get("safe_current_use"),
    }
    return {
        "schema": SCHEMA,
        "status": STATUS,
        "blocker_id": "OC6",
        "oc6_blocker_id": "OC6",
        "blocker_status": "partial",
        "oc6_blocker_status": "partial",
        "oc6_blocker_open": True,
        "objective_blocker_matrix_status": "global_objective_blockers_remain_open",
        "blocker_open_by_id": BLOCKER_OPEN_BY_ID,
        "blocker_closure_decision_by_id": BLOCKER_CLOSURE_DECISION_BY_ID,
        "blocker_closure_allowed_by_id": BLOCKER_CLOSURE_ALLOWED_BY_ID,
        "closure_decision": "remain_open_no_positive_source_equivalent_artifact",
        "oc6_closure_decision": "remain_open_no_positive_source_equivalent_artifact",
        "oc6_closure_allowed_now": False,
        "source_equivalent_artifact_found": False,
        "source_equivalent_artifact_rows": candidate_source_equivalent_rows,
        "source_equivalent_artifact_required_to_close": True,
        "reopen_condition": "suite_specific_source_equivalent_reopen_conditions",
        "reopen_condition_count": len(SUITE_REOPEN_CONDITIONS),
        "reopen_condition_by_suite": SUITE_REOPEN_CONDITIONS,
        "tfe_reopen_condition": SUITE_REOPEN_CONDITIONS["tfe2026_original_pendulum"],
        "tfe_source_equivalent_reopen_condition": SUITE_REOPEN_CONDITIONS[
            "tfe2026_original_pendulum"
        ],
        "vp_reopen_condition": SUITE_REOPEN_CONDITIONS["vp2024_velocity_partitioning"],
        "vp_source_equivalent_reopen_condition": SUITE_REOPEN_CONDITIONS[
            "vp2024_velocity_partitioning"
        ],
        "source_equivalent_reopen_conditions": SUITE_REOPEN_CONDITIONS,
        "date_checked": "2026-06-20",
        "read_only": True,
        "performs_new_public_code_search": False,
        "commands_executed_by_audit": False,
        "source_policy_execution_invoked": False,
        "source_policy_execution_allowed_now": False,
        "exact_b4_opt_in_required_for_execution": True,
        "safe_actions_without_b4_opt_in": SAFE_ACTIONS_WITHOUT_B4_OPT_IN,
        "safe_action_ids": SAFE_ACTION_IDS,
        "opt_in_action_ids": OPT_IN_ACTION_IDS,
        "next_safe_actions": SAFE_ACTIONS_WITHOUT_B4_OPT_IN,
        "next_safe_action_ids": SAFE_ACTION_IDS,
        "required_user_approval_statement": REQUIRED_USER_APPROVAL_STATEMENT,
        "guarded_execution_driver": "run_b4_source_policy_after_opt_in.sh",
        "heavy_numerical_run_invoked": False,
        "run_v047_invoked": False,
        "v048_runner_invoked": False,
        "submission_ready": False,
        "oc6_can_close_now": False,
        "external_superiority_claim_allowed": False,
        "rows_total": len(rows),
        "row_count": len(rows),
        "tfe_rows": sum(1 for row in rows if row["suite_id"] == "tfe2026_original_pendulum"),
        "vp_rows": sum(1 for row in rows if row["suite_id"] == "vp2024_velocity_partitioning"),
        "unable_to_reproduce_rows": sum(1 for row in rows if row["unable_to_reproduce"] is True),
        "public_code_available_rows": sum(1 for row in rows if row["public_code_available"] is True),
        "candidate_runner_available_rows": sum(
            1 for row in rows if row["candidate_runner_available"] is True
        ),
        "candidate_runner_source_policy_equivalent_rows": candidate_source_equivalent_rows,
        "source_policy_rows_closed": source_policy_rows_closed,
        "source_policy_closed_ratio": source_policy_closed_ratio,
        "source_policy_rows_promoted": 0,
        "external_superiority_ready_rows": sum(
            1 for row in rows if row["external_superiority_ready"] is True
        ),
        "positive_public_code_artifact_rows": int0(
            reopen_monitor.get("positive_public_code_artifact_rows")
        ),
        "local_positive_reopen_artifact_rows": int0(
            reopen_monitor.get("local_positive_reopen_artifact_rows")
        ),
        "source_policy_reopen_triggered": reopen_monitor.get("source_policy_reopen_triggered"),
        "latest_external_probe_date_checked": public_refresh.get(
            "latest_external_probe_date_checked"
        ),
        "latest_external_probe_count": public_refresh.get("latest_external_probe_count"),
        "latest_external_probe_positive_public_code_artifact_rows": public_refresh.get(
            "latest_external_probe_positive_public_code_artifact_rows"
        ),
        "latest_external_probe_source_policy_rows_closed": public_refresh.get(
            "latest_external_probe_source_policy_rows_closed"
        ),
        "latest_external_probe_access_limited_count": public_refresh.get(
            "latest_external_probe_access_limited_count"
        ),
        "latest_external_probe_global_absence_proved": public_refresh.get(
            "latest_external_probe_global_absence_proved"
        ),
        "latest_external_probe_source_policy_reopen_triggered": public_refresh.get(
            "latest_external_probe_source_policy_reopen_triggered"
        ),
        "latest_external_probe_marker": public_refresh.get("latest_external_probe_marker"),
        "latest_external_probe_boundary": {
            "marker": public_refresh.get("latest_external_probe_marker"),
            "access_limited_count": public_refresh.get(
                "latest_external_probe_access_limited_count"
            ),
            "global_absence_proved": public_refresh.get(
                "latest_external_probe_global_absence_proved"
            ),
            "positive_public_code_artifact_rows": public_refresh.get(
                "latest_external_probe_positive_public_code_artifact_rows"
            ),
            "source_policy_rows_closed": public_refresh.get(
                "latest_external_probe_source_policy_rows_closed"
            ),
            "source_policy_reopen_triggered": public_refresh.get(
                "latest_external_probe_source_policy_reopen_triggered"
            ),
            "access_limited_rows_are_not_positive_evidence": True,
            "access_limited_rows_do_not_prove_global_absence": True,
        },
        "latest_external_probe_rows_by_suite": latest_external_probe_rows_by_suite,
        "latest_external_probe_rows": latest_external_probe_rows,
        "suite_summary": summaries,
        "reopen_summary": reopen_summary,
        "tfe_reopen_summary": tfe_reopen_summary,
        "vp_reopen_summary": vp_reopen_summary,
        "runner_contract_summary": runner_contract_summary,
        "rows": rows,
        "reopen_readiness_digest": canonical_digest(digest_inputs),
        "source_files": SOURCE_FILES,
    }


def write_markdown(payload: dict[str, Any]) -> None:
    lines = [
        "# OC6 Source-Equivalent Reopen-Readiness Audit 20260620",
        "",
        f"Status: `{payload['status']}`.",
        "",
        "This is a read-only audit of existing local refresh and source-policy monitor artifacts. It does not perform a new public-code search, run v047/v048, or execute B4 source-policy commands.",
        "",
        f"- Rows TFE/VP/total: `{payload['tfe_rows']}/{payload['vp_rows']}/{payload['row_count']}`.",
        f"- Unable-to-reproduce rows: `{payload['unable_to_reproduce_rows']}`.",
        f"- Public-code available rows: `{payload['public_code_available_rows']}`.",
        f"- Candidate runner available/source-policy-equivalent rows: `{payload['candidate_runner_available_rows']}/{payload['candidate_runner_source_policy_equivalent_rows']}`.",
        f"- Positive public/local reopen artifact rows: `{payload['positive_public_code_artifact_rows']}/{payload['local_positive_reopen_artifact_rows']}`.",
        f"- Source-policy rows closed/promoted: `{payload['source_policy_rows_closed']}/{payload['source_policy_rows_promoted']}`.",
        f"- Source-policy closed ratio: `{payload['source_policy_closed_ratio']}`.",
        f"- Blocker/status/closure decision: `{payload['blocker_id']}/{payload['blocker_status']}/{payload['closure_decision']}`.",
        f"- OC6 aliases blocker/status/closure/allowed-now: `{payload['oc6_blocker_id']}/{payload['oc6_blocker_status']}/{payload['oc6_closure_decision']}/{payload['oc6_closure_allowed_now']}`.",
        f"- Source-equivalent artifact found/rows/required-to-close: `{payload['source_equivalent_artifact_found']}/{payload['source_equivalent_artifact_rows']}/{payload['source_equivalent_artifact_required_to_close']}`.",
        f"- Reopen condition alias/count: `{payload['reopen_condition']}/{payload['reopen_condition_count']}`.",
        f"- TFE/VP reopen conditions: `{payload['tfe_reopen_condition']}` / `{payload['vp_reopen_condition']}`.",
        f"- OC6 can close now / external-superiority allowed / submission ready: `{payload['oc6_can_close_now']}/{payload['external_superiority_claim_allowed']}/{payload['submission_ready']}`.",
        f"- New public-code search performed: `{payload['performs_new_public_code_search']}`.",
        f"- Commands/source-policy execution/heavy/run_v047/v048 invoked: `{payload['commands_executed_by_audit']}/{payload['source_policy_execution_invoked']}/{payload['heavy_numerical_run_invoked']}/{payload['run_v047_invoked']}/{payload['v048_runner_invoked']}`.",
        f"- Source-policy execution allowed now/invoked/exact opt-in required: `{payload['source_policy_execution_allowed_now']}/{payload['source_policy_execution_invoked']}/{payload['exact_b4_opt_in_required_for_execution']}`.",
        f"- Safe action ids: `{','.join(payload['safe_action_ids'])}`.",
        f"- Opt-in action ids: `{','.join(payload['opt_in_action_ids'])}`.",
        "",
        "## Objective Blocker Matrix",
        "",
        "This audit records OC6 source-equivalent reopen readiness. It does not close the global objective blockers.",
        "",
        f"- `blocker_open_by_id={blocker_token(payload['blocker_open_by_id'])}`",
        f"- `blocker_closure_decision_by_id={blocker_token(payload['blocker_closure_decision_by_id'])}`",
        f"- `blocker_closure_allowed_by_id={blocker_token(payload['blocker_closure_allowed_by_id'])}`",
        "",
        "## Reopen Monitor",
        "",
        f"- Public refresh: `{payload['reopen_summary']['public_refresh_status']}` on `{payload['reopen_summary']['public_refresh_date_checked']}`; rows/queries/positive/closed `{payload['reopen_summary']['public_refresh_rows']}/{payload['reopen_summary']['public_refresh_current_queries']}/{payload['reopen_summary']['public_refresh_positive_public_code_artifact_rows']}/{payload['reopen_summary']['public_refresh_source_policy_rows_closed']}`.",
        f"- Latest external probe: `{payload['latest_external_probe_date_checked']}/{payload['latest_external_probe_count']}/{payload['latest_external_probe_positive_public_code_artifact_rows']}/{payload['latest_external_probe_source_policy_rows_closed']}/{payload['latest_external_probe_access_limited_count']}/{payload['latest_external_probe_global_absence_proved']}/{payload['latest_external_probe_source_policy_reopen_triggered']}`.",
        f"- Latest external probe marker: `{payload['latest_external_probe_marker']}`.",
        f"- Latest external probe boundary positive/closed/access-limited/global-absence/reopen: `{payload['latest_external_probe_boundary']['positive_public_code_artifact_rows']}/{payload['latest_external_probe_boundary']['source_policy_rows_closed']}/{payload['latest_external_probe_boundary']['access_limited_count']}/{payload['latest_external_probe_boundary']['global_absence_proved']}/{payload['latest_external_probe_boundary']['source_policy_reopen_triggered']}`.",
        f"- Public refresh local-positive/reopen-triggered aliases: `{payload['reopen_summary']['public_refresh_local_positive_reopen_artifact_rows']}/{payload['reopen_summary']['public_refresh_source_policy_reopen_triggered']}`.",
        f"- Latest probe rows by suite: `{payload['latest_external_probe_rows_by_suite']}`.",
        "- Latest probe reading rule: access-limited searches are not positive artifact evidence and do not prove global absence.",
        f"- Reopen monitor: `{payload['reopen_summary']['reopen_monitor_status']}` on `{payload['reopen_summary']['reopen_monitor_date_checked']}`; unable/public-positive/local-positive/reopened `{payload['reopen_summary']['reopen_monitor_unable_to_reproduce_rows']}/{payload['reopen_summary']['reopen_monitor_positive_public_code_artifact_rows']}/{payload['reopen_summary']['reopen_monitor_local_positive_reopen_artifact_rows']}/{payload['reopen_summary']['reopen_monitor_source_policy_reopen_triggered']}`.",
        "",
        "## TFE Boundary",
        "",
        f"- TFE self-reproduction: `{payload['tfe_reopen_summary']['self_reproduction_status']}`; closed/unable `{payload['tfe_reopen_summary']['self_reproduction_source_policy_closed_ratio']}/{payload['tfe_reopen_summary']['self_reproduction_unable_to_reproduce_rows']}`.",
        f"- TFE public recheck hits repository/user/direct-code: `{payload['tfe_reopen_summary']['public_code_recheck_repository_hits']}/{payload['tfe_reopen_summary']['public_code_recheck_user_hits']}/{payload['tfe_reopen_summary']['public_code_recheck_direct_code_hits']}`.",
        f"- TFE source-equivalence blockers Brown-McPhee/full-T10-endpoint: `{payload['tfe_reopen_summary']['brown_mcphee_source_code_equivalent_law']}/{payload['tfe_reopen_summary']['full_T10_endpoint_policy_resolved']}`.",
        f"- TFE execution preflight ready/promote/blocks/source-rows: `{payload['tfe_reopen_summary']['ready_to_execute_source_policy_now']}/{payload['tfe_reopen_summary']['can_promote_any_tfe_source_policy_row_now']}/{payload['tfe_reopen_summary']['execution_block_count']}/{payload['tfe_reopen_summary']['source_policy_rows_completed']}`.",
        f"- TFE runner contract entrypoints/callable/candidate-backed/source-equivalent-blocks/requires-new: `{payload['tfe_reopen_summary']['runner_contract_entrypoints']}/{payload['tfe_reopen_summary']['runner_contract_callable']}/{payload['tfe_reopen_summary']['runner_contract_candidate_backed']}/{payload['tfe_reopen_summary']['runner_contract_source_policy_equivalent_blocks']}/{payload['tfe_reopen_summary']['runner_contract_requires_new_artifact_or_execution_blocks']}`.",
        "",
        "## VP Boundary",
        "",
        f"- VP public recheck: `{payload['vp_reopen_summary']['public_code_recheck_status']}`; attempted/closed/tree/year2024/keyword-hits `{payload['vp_reopen_summary']['source_policy_rows_attempted_not_reproducible']}/{payload['vp_reopen_summary']['source_policy_rows_closed']}/{payload['vp_reopen_summary']['tree_total_paths']}/{payload['vp_reopen_summary']['year2024_path_count']}/{payload['vp_reopen_summary']['keyword_path_hit_count']}`.",
        f"- VP close now / disposition: `{payload['vp_reopen_summary']['can_close_vp2024_source_policy_rows_now']}/{payload['vp_reopen_summary']['row_disposition']}`.",
        "",
        "## Suite Summary",
        "",
        "| suite | rows | unable | public code | candidate | source-equivalent | closed | reopen condition |",
        "|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for item in payload["suite_summary"]:
        lines.append(
            f"| `{item['suite_id']}` | `{item['row_count']}` | `{item['unable_to_reproduce_rows']}` | "
            f"`{item['public_code_available_rows']}` | `{item['candidate_runner_available_rows']}` | "
            f"`{item['candidate_runner_source_policy_equivalent_rows']}` | "
            f"`{item['source_policy_closed_rows']}` | `{item['reopen_condition']}` |"
        )
    lines.extend(
        [
            "",
            "Reading rule: OC6 remains open. Existing candidate/proxy runners are diagnostic only unless a new public or source-code-equivalent artifact satisfies the suite reopen condition and closes source-policy rows.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    payload = build_payload()
    with OUT_JSON.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")
    write_markdown(payload)
    print(
        "wrote "
        f"{OUT_JSON.name} and {OUT_MD.name}: "
        f"rows={payload['row_count']} "
        f"unable={payload['unable_to_reproduce_rows']} "
        f"source_equivalent={payload['candidate_runner_source_policy_equivalent_rows']} "
        f"source_policy_closed={payload['source_policy_rows_closed']}"
    )


if __name__ == "__main__":
    main()
