#!/usr/bin/env python3
"""Build a full-T10 endpoint-policy closure certificate for TFE."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
OUT_JSON = PAPER / "TFE_FULL_T10_ENDPOINT_POLICY_CLOSURE_CERTIFICATE.json"
OUT_MD = PAPER / "TFE_FULL_T10_ENDPOINT_POLICY_CLOSURE_CERTIFICATE.md"

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


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def main() -> None:
    grid = read_json(PAPER / "TFE_SOURCE_GRID_COMPATIBILITY_AUDIT.json")
    endpoint_boundary = read_json(PAPER / "TFE_ENDPOINT_POLICY_BOUNDARY_CERTIFICATE.json")
    endpoint_sensitivity = read_json(PAPER / "TFE_ENDPOINT_POLICY_SENSITIVITY_AUDIT.json")
    row_audit = read_json(PAPER / "TFE_SOURCE_POLICY_ROW_AUDIT.json")

    sensitivity_summary = endpoint_sensitivity.get("summary_rows", [])
    sensitivity_raw = endpoint_sensitivity.get("raw_rows", [])
    policies = sorted({row.get("policy") for row in sensitivity_summary if row.get("policy")})
    methods = sorted({row.get("paper_method") for row in sensitivity_summary if row.get("paper_method")})
    terminal_offsets = [
        abs(float(row.get("max_terminal_time_offset_abs", 0.0)))
        for row in sensitivity_summary
        if row.get("max_terminal_time_offset_abs") is not None
    ]
    row_gap = next(
        (
            row
            for row in row_audit.get("source_policy_runner_equivalence_gap_matrix", {}).get(
                "open_blockers",
                [],
            )
            if row.get("id") == "full_T10_source_grid_endpoint_policy_open"
        ),
        {},
    )
    source_text = grid.get("source_text_endpoint_convention_audit", {})
    endpoint_subclosure = grid.get("endpoint_grid_subclosure", {})
    boundary_claim = endpoint_boundary.get("claim_boundary", {})

    output: dict[str, Any] = {
        "schema": "tfe-full-t10-endpoint-policy-closure-certificate-v1",
        "status": "negative_full_T10_endpoint_policy_certificate_not_source_policy",
        "read_only": True,
        "heavy_numerical_run_invoked": False,
        "run_v047_invoked": False,
        "v048_runner_invoked": False,
        "b4_source_policy_execution_invoked": False,
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
        "submission_ready": False,
        "external_superiority_claim_allowed": False,
        "can_close_now": False,
        "certificate_available": True,
        "certificate_kind": "current_package_negative_full_T10_endpoint_policy_certificate",
        "positive_full_T10_endpoint_policy_certified": False,
        "source_grid_policy_resolved_for_full_T10": False,
        "source_policy_exact_T_error_sampling_equivalent": False,
        "source_endpoint_convention_resolved_for_error_sampling": False,
        "source_policy_rows_completed": 0,
        "nonheavy_contract_block_closed": False,
        "algorithm_literal_endpoint_policy": endpoint_boundary.get(
            "algorithm_literal_endpoint_policy"
        ),
        "algorithm_literal_overrun_bound_proved": (
            endpoint_boundary.get("theorem", {}).get("name")
            == "fixed_h_until_final_time_endpoint_bound"
        ),
        "grid_boundary": {
            "row_count": grid.get("row_count"),
            "integer_step_compatible_rows": grid.get("integer_step_compatible_rows"),
            "integer_step_incompatible_rows": grid.get("integer_step_incompatible_rows"),
            "source_grid_policy_resolved_for_exact_T_compatible_rows": grid.get(
                "source_grid_policy_resolved_for_exact_T_compatible_rows"
            ),
            "source_grid_policy_resolved_for_full_T10": grid.get(
                "source_grid_policy_resolved_for_full_T10"
            ),
            "endpoint_compatible_rows_source_endpoint_convention_resolved": grid.get(
                "endpoint_compatible_rows_source_endpoint_convention_resolved"
            ),
            "endpoint_incompatible_rows_require_source_endpoint_policy": grid.get(
                "endpoint_incompatible_rows_require_source_endpoint_policy"
            ),
            "endpoint_incompatible_rows_demoted_from_source_policy": grid.get(
                "endpoint_incompatible_rows_demoted_from_source_policy"
            ),
            "source_endpoint_compatible_row_ids": grid.get(
                "source_endpoint_compatible_row_ids",
                [],
            ),
            "source_endpoint_incompatible_row_ids": grid.get(
                "source_endpoint_incompatible_row_ids",
                [],
            ),
        },
        "source_text_evidence": {
            "source_text_available": source_text.get("source_text_available"),
            "anchor_count": source_text.get("anchor_count"),
            "algorithm_literal_constant_h_until_tn_ge_tfinal": source_text.get(
                "algorithm_literal_constant_h_until_tn_ge_tfinal"
            ),
            "source_endpoint_convention_resolved_for_error_sampling": source_text.get(
                "source_endpoint_convention_resolved_for_error_sampling"
            ),
            "source_text_confirms_adjusted_h_for_exact_T": source_text.get(
                "source_text_confirms_adjusted_h_for_exact_T"
            ),
            "source_text_confirms_interpolation_to_exact_T": source_text.get(
                "source_text_confirms_interpolation_to_exact_T"
            ),
            "source_text_confirms_partial_final_step": source_text.get(
                "source_text_confirms_partial_final_step"
            ),
            "source_text_confirms_floor_or_nearest_endpoint_sampling": source_text.get(
                "source_text_confirms_floor_or_nearest_endpoint_sampling"
            ),
        },
        "endpoint_boundary_certificate": {
            "status": endpoint_boundary.get("status"),
            "algorithm_literal_exact_T_row_count": endpoint_boundary.get(
                "algorithm_literal_exact_T_row_count"
            ),
            "algorithm_literal_overrun_row_count": endpoint_boundary.get(
                "algorithm_literal_overrun_row_count"
            ),
            "endpoint_incompatible_rows_demoted_from_source_policy": endpoint_boundary.get(
                "endpoint_incompatible_rows_demoted_from_source_policy"
            ),
            "source_grid_policy_resolved_for_full_T10": endpoint_boundary.get(
                "source_grid_policy_resolved_for_full_T10"
            ),
            "source_policy_exact_T_error_sampling_equivalent": endpoint_boundary.get(
                "source_policy_exact_T_error_sampling_equivalent"
            ),
            "source_policy_method_runner_equivalent": endpoint_boundary.get(
                "source_policy_method_runner_equivalent"
            ),
            "source_policy_rows_completed": endpoint_boundary.get(
                "source_policy_rows_completed"
            ),
            "accepted_use": boundary_claim.get("accepted_use"),
            "not_proved": boundary_claim.get("not_proved", []),
        },
        "diagnostic_endpoint_sensitivity": {
            "status": endpoint_sensitivity.get("status"),
            "summary_row_count": len(sensitivity_summary),
            "raw_row_count": len(sensitivity_raw),
            "source_policy_rows_completed": endpoint_sensitivity.get(
                "source_policy_rows_completed"
            ),
            "policies": policies,
            "policy_count": len(policies),
            "paper_methods": methods,
            "paper_method_count": len(methods),
            "max_terminal_time_offset_abs": max(terminal_offsets) if terminal_offsets else None,
        },
        "row_audit_gap_status": {
            "gap_id": row_gap.get("id"),
            "gap_status": row_gap.get("status"),
            "first_required_artifact": row_gap.get("first_required_artifact"),
            "can_resolve_without_heavy_run": row_gap.get("can_resolve_without_heavy_run"),
        },
        "closure_decision": {
            "can_certify_full_T10_endpoint_policy_now": False,
            "can_close_full_T10_source_grid_endpoint_policy_now": False,
            "can_promote_tfe_source_policy_rows_now": False,
            "reason": (
                "The current package proves only the fixed-h algorithm-literal overrun bound and "
                "resolves the exact-T-compatible subset. Four published h rows do not divide T=10; "
                "the source text does not identify the error/output sampling convention for those "
                "noninteger T/h rows. This certificate therefore records a negative full-T10 "
                "endpoint-policy closure decision and leaves source-policy rows at zero."
            ),
        },
        "required_to_promote_full_T10_rows": grid.get(
            "required_to_accept_full_T10_rows",
            [],
        ),
        "endpoint_grid_subclosure": {
            "boundary": endpoint_subclosure.get("boundary"),
            "source_policy_rows_completed": endpoint_subclosure.get(
                "source_policy_rows_completed"
            ),
            "source_grid_policy_resolved_for_full_T10": endpoint_subclosure.get(
                "source_grid_policy_resolved_for_full_T10"
            ),
            "endpoint_incompatible_rows_require_source_endpoint_policy": endpoint_subclosure.get(
                "endpoint_incompatible_rows_require_source_endpoint_policy"
            ),
            "endpoint_incompatible_rows_demoted_from_source_policy": endpoint_subclosure.get(
                "endpoint_incompatible_rows_demoted_from_source_policy"
            ),
        },
        "source_files": {
            "source_grid_compatibility_audit": "TFE_SOURCE_GRID_COMPATIBILITY_AUDIT.json",
            "endpoint_policy_boundary_certificate": "TFE_ENDPOINT_POLICY_BOUNDARY_CERTIFICATE.json",
            "endpoint_policy_sensitivity_audit": "TFE_ENDPOINT_POLICY_SENSITIVITY_AUDIT.json",
            "source_policy_row_audit": "TFE_SOURCE_POLICY_ROW_AUDIT.json",
        },
    }

    with OUT_JSON.open("w", encoding="utf-8") as handle:
        json.dump(output, handle, indent=2, sort_keys=True)
        handle.write("\n")

    lines = [
        "# TFE Full-T10 Endpoint Policy Closure Certificate",
        "",
        "Status: **negative full-T10 endpoint-policy certificate; not source policy**.",
        "",
        f"- Certificate available: `{output['certificate_available']}`.",
        f"- Positive full-T10 endpoint policy certified: `{output['positive_full_T10_endpoint_policy_certified']}`.",
        f"- Source grid policy resolved for full T=10: `{output['source_grid_policy_resolved_for_full_T10']}`.",
        f"- Exact-T error sampling source-equivalent: `{output['source_policy_exact_T_error_sampling_equivalent']}`.",
        f"- Source endpoint convention resolved for error sampling: `{output['source_endpoint_convention_resolved_for_error_sampling']}`.",
        f"- Source-policy rows completed: `{output['source_policy_rows_completed']}`.",
        f"- Source-policy execution invoked / can close now: `{output['source_policy_execution_invoked']}/{output['can_close_now']}`.",
        f"- Source-policy execution allowed now/invoked/exact opt-in required: `{output['source_policy_execution_allowed_now']}/{output['source_policy_execution_invoked']}/{output['exact_b4_opt_in_required_for_execution']}`.",
        f"- Safe action ids: `{','.join(output['safe_action_ids'])}`.",
        f"- Opt-in action ids: `{','.join(output['opt_in_action_ids'])}`.",
        f"- Non-heavy contract block closed: `{output['nonheavy_contract_block_closed']}`.",
        (
            "- Grid rows/exact-compatible/incompatible/full-policy: "
            f"`{output['grid_boundary']['row_count']}/"
            f"{output['grid_boundary']['integer_step_compatible_rows']}/"
            f"{output['grid_boundary']['integer_step_incompatible_rows']}/"
            f"{output['grid_boundary']['source_grid_policy_resolved_for_full_T10']}`."
        ),
        (
            "- Endpoint boundary exact/overrun/source rows/full-policy/exact-T-equivalent: "
            f"`{output['endpoint_boundary_certificate']['algorithm_literal_exact_T_row_count']}/"
            f"{output['endpoint_boundary_certificate']['algorithm_literal_overrun_row_count']}/"
            f"{output['endpoint_boundary_certificate']['source_policy_rows_completed']}/"
            f"{output['endpoint_boundary_certificate']['source_grid_policy_resolved_for_full_T10']}/"
            f"{output['endpoint_boundary_certificate']['source_policy_exact_T_error_sampling_equivalent']}`."
        ),
        (
            "- Source text anchors/fixed-h-loop/error-sampling-resolved: "
            f"`{output['source_text_evidence']['anchor_count']}/"
            f"{output['source_text_evidence']['algorithm_literal_constant_h_until_tn_ge_tfinal']}/"
            f"{output['source_text_evidence']['source_endpoint_convention_resolved_for_error_sampling']}`."
        ),
        (
            "- Endpoint sensitivity summary/raw/source rows/policies/methods/max-offset: "
            f"`{output['diagnostic_endpoint_sensitivity']['summary_row_count']}/"
            f"{output['diagnostic_endpoint_sensitivity']['raw_row_count']}/"
            f"{output['diagnostic_endpoint_sensitivity']['source_policy_rows_completed']}/"
            f"{output['diagnostic_endpoint_sensitivity']['policy_count']}/"
            f"{output['diagnostic_endpoint_sensitivity']['paper_method_count']}/"
            f"{output['diagnostic_endpoint_sensitivity']['max_terminal_time_offset_abs']:.3e}`."
        ),
        (
            "- Row-audit gap status/can-resolve-without-heavy-run: "
            f"`{output['row_audit_gap_status']['gap_status']}/"
            f"{output['row_audit_gap_status']['can_resolve_without_heavy_run']}`."
        ),
        "",
        "## Decision",
        "",
        output["closure_decision"]["reason"],
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("tfe_full_t10_endpoint_policy_closure_certificate=written")
    print(f"status={output['status']}")
    print("source_grid_policy_resolved_for_full_T10=False")
    print("source_policy_rows_completed=0")
    print("source_policy_execution_invoked=False")
    print("source_policy_execution_allowed_now=False")
    print("can_close_now=False")


if __name__ == "__main__":
    main()
