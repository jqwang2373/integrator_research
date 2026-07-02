#!/usr/bin/env python3
"""Validate the TFE full-T10 endpoint-policy closure certificate."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
EXPECTED_SAFE_ACTION_IDS = [
    "rebuild_read_only_audit_chain",
    "rerun_read_only_validators",
    "keep_narrowed_archive_provenance_only",
    "monitor_reopen_conditions",
]
EXPECTED_OPT_IN_ACTION_IDS = ["authorized_b4_ra_hi_source_policy_execution"]
EXPECTED_APPROVAL_STATEMENT = (
    "I explicitly approve running the B4 source-policy execution commands listed in "
    "B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json."
)


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


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def main() -> int:
    checks = Checks()
    try:
        cert = read_json(PAPER / "TFE_FULL_T10_ENDPOINT_POLICY_CLOSURE_CERTIFICATE.json")
        cert_md = read_text(PAPER / "TFE_FULL_T10_ENDPOINT_POLICY_CLOSURE_CERTIFICATE.md")
        grid = read_json(PAPER / "TFE_SOURCE_GRID_COMPATIBILITY_AUDIT.json")
        endpoint_boundary = read_json(PAPER / "TFE_ENDPOINT_POLICY_BOUNDARY_CERTIFICATE.json")
        endpoint_sensitivity = read_json(PAPER / "TFE_ENDPOINT_POLICY_SENSITIVITY_AUDIT.json")
        row_audit = read_json(PAPER / "TFE_SOURCE_POLICY_ROW_AUDIT.json")
    except Exception as exc:  # noqa: BLE001
        print(f"TFE full-T10 endpoint-policy closure certificate validation: FAIL\n- {exc}")
        return 1

    grid_boundary = cert.get("grid_boundary", {})
    source_text = cert.get("source_text_evidence", {})
    boundary = cert.get("endpoint_boundary_certificate", {})
    sensitivity = cert.get("diagnostic_endpoint_sensitivity", {})
    row_gap = cert.get("row_audit_gap_status", {})
    closure = cert.get("closure_decision", {})
    source_files = cert.get("source_files", {})
    grid_source_text = grid.get("source_text_endpoint_convention_audit", {})
    row_gap_ids = {
        row.get("id")
        for row in row_audit.get("source_policy_runner_equivalence_gap_matrix", {}).get(
            "open_blockers",
            [],
        )
    }

    checks.check(
        cert.get("schema") == "tfe-full-t10-endpoint-policy-closure-certificate-v1",
        "schema changed",
    )
    checks.check(
        cert.get("status") == "negative_full_T10_endpoint_policy_certificate_not_source_policy",
        "status changed",
    )
    checks.check(cert.get("read_only") is True, "certificate must remain read-only")
    checks.check(cert.get("heavy_numerical_run_invoked") is False, "certificate invoked heavy run")
    checks.check(cert.get("run_v047_invoked") is False, "certificate invoked run_v047")
    checks.check(cert.get("v048_runner_invoked") is False, "certificate invoked v048 runner")
    checks.check(
        cert.get("b4_source_policy_execution_invoked") is False,
        "certificate invoked B4 source-policy execution",
    )
    checks.check(
        cert.get("source_policy_execution_invoked") is False,
        "certificate invoked source-policy execution",
    )
    checks.check(cert.get("source_policy_execution_allowed_now") is False, "certificate allowed source-policy execution")
    checks.check(
        cert.get("exact_b4_opt_in_required_for_execution") is True,
        "certificate lost exact opt-in requirement",
    )
    checks.check(cert.get("safe_action_ids") == EXPECTED_SAFE_ACTION_IDS, "safe action ids changed")
    checks.check(cert.get("next_safe_action_ids") == EXPECTED_SAFE_ACTION_IDS, "next safe action ids changed")
    checks.check(cert.get("opt_in_action_ids") == EXPECTED_OPT_IN_ACTION_IDS, "opt-in action ids changed")
    checks.check(
        cert.get("required_user_approval_statement") == EXPECTED_APPROVAL_STATEMENT,
        "approval statement changed",
    )
    checks.check(
        cert.get("guarded_execution_driver") == "run_b4_source_policy_after_opt_in.sh",
        "guarded driver changed",
    )
    checks.check(cert.get("submission_ready") is False, "certificate overclaims submission readiness")
    checks.check(
        cert.get("external_superiority_claim_allowed") is False,
        "certificate overclaims external superiority",
    )
    checks.check(cert.get("can_close_now") is False, "certificate overclaims closure readiness")
    checks.check(cert.get("certificate_available") is True, "certificate availability marker missing")
    checks.check(
        cert.get("certificate_kind")
        == "current_package_negative_full_T10_endpoint_policy_certificate",
        "certificate kind changed",
    )
    checks.check(
        cert.get("positive_full_T10_endpoint_policy_certified") is False,
        "certificate overclaims positive full-T10 endpoint policy",
    )
    checks.check(
        cert.get("source_grid_policy_resolved_for_full_T10")
        == grid.get("source_grid_policy_resolved_for_full_T10")
        == endpoint_boundary.get("source_grid_policy_resolved_for_full_T10")
        is False,
        "full-T10 source-grid policy was overclosed",
    )
    checks.check(
        cert.get("source_policy_exact_T_error_sampling_equivalent")
        == endpoint_boundary.get("source_policy_exact_T_error_sampling_equivalent")
        is False,
        "exact-T error sampling source equivalence was overclaimed",
    )
    checks.check(
        cert.get("source_endpoint_convention_resolved_for_error_sampling")
        == grid_source_text.get("source_endpoint_convention_resolved_for_error_sampling")
        is False,
        "source endpoint convention was overclaimed",
    )
    checks.check(cert.get("source_policy_rows_completed") == 0, "certificate completed source-policy rows")
    checks.check(cert.get("nonheavy_contract_block_closed") is False, "certificate closed non-heavy block")
    checks.check(
        cert.get("algorithm_literal_endpoint_policy") == "fixed_h_until_tn_ge_tfinal",
        "algorithm-literal endpoint policy changed",
    )
    checks.check(
        cert.get("algorithm_literal_overrun_bound_proved") is True,
        "algorithm-literal overrun theorem marker missing",
    )

    checks.check(grid_boundary.get("row_count") == grid.get("row_count") == 6, "grid row count changed")
    checks.check(
        grid_boundary.get("integer_step_compatible_rows")
        == grid.get("integer_step_compatible_rows")
        == 2,
        "integer-compatible row count changed",
    )
    checks.check(
        grid_boundary.get("integer_step_incompatible_rows")
        == grid.get("integer_step_incompatible_rows")
        == 4,
        "integer-incompatible row count changed",
    )
    checks.check(
        grid_boundary.get("source_grid_policy_resolved_for_exact_T_compatible_rows")
        == grid.get("source_grid_policy_resolved_for_exact_T_compatible_rows")
        is True,
        "exact-T-compatible subset no longer resolved",
    )
    checks.check(
        grid_boundary.get("endpoint_incompatible_rows_require_source_endpoint_policy")
        == grid.get("endpoint_incompatible_rows_require_source_endpoint_policy")
        == 4,
        "endpoint-incompatible policy requirement count changed",
    )
    checks.check(
        grid_boundary.get("endpoint_incompatible_rows_demoted_from_source_policy")
        == grid.get("endpoint_incompatible_rows_demoted_from_source_policy")
        == 4,
        "endpoint-incompatible demotion count changed",
    )
    checks.check(
        len(grid_boundary.get("source_endpoint_compatible_row_ids", [])) == 2
        and len(grid_boundary.get("source_endpoint_incompatible_row_ids", [])) == 4,
        "endpoint compatible/incompatible row id sets changed",
    )

    checks.check(source_text.get("source_text_available") is True, "source text marker missing")
    checks.check(source_text.get("anchor_count") == 9, "source text anchor count changed")
    checks.check(
        source_text.get("algorithm_literal_constant_h_until_tn_ge_tfinal") is True,
        "fixed-h loop source-text marker missing",
    )
    checks.check(
        source_text.get("source_text_confirms_adjusted_h_for_exact_T") is False
        and source_text.get("source_text_confirms_interpolation_to_exact_T") is False
        and source_text.get("source_text_confirms_partial_final_step") is False
        and source_text.get("source_text_confirms_floor_or_nearest_endpoint_sampling") is False,
        "source text unexpectedly confirms an endpoint sampling convention",
    )

    checks.check(
        boundary.get("status") == endpoint_boundary.get("status"),
        "endpoint boundary status drifted",
    )
    checks.check(
        boundary.get("algorithm_literal_exact_T_row_count")
        == endpoint_boundary.get("algorithm_literal_exact_T_row_count")
        == 2,
        "endpoint boundary exact-T row count changed",
    )
    checks.check(
        boundary.get("algorithm_literal_overrun_row_count")
        == endpoint_boundary.get("algorithm_literal_overrun_row_count")
        == 4,
        "endpoint boundary overrun row count changed",
    )
    checks.check(
        boundary.get("source_policy_rows_completed")
        == endpoint_boundary.get("source_policy_rows_completed")
        == 0,
        "endpoint boundary overclosed source-policy rows",
    )
    checks.check(
        boundary.get("source_policy_method_runner_equivalent")
        == endpoint_boundary.get("source_policy_method_runner_equivalent")
        is False,
        "endpoint boundary overclaims method-runner equivalence",
    )
    checks.check(
        boundary.get("accepted_use") == "endpoint_policy_boundary_proof_not_source_policy",
        "endpoint boundary accepted-use changed",
    )
    checks.check(
        any("source-code-equivalent endpoint/output sampling" in item for item in boundary.get("not_proved", [])),
        "endpoint boundary no longer records missing source-code-equivalent sampling",
    )

    checks.check(
        sensitivity.get("status") == endpoint_sensitivity.get("status"),
        "endpoint sensitivity status drifted",
    )
    checks.check(
        sensitivity.get("summary_row_count") == len(endpoint_sensitivity.get("summary_rows", [])) == 16,
        "endpoint sensitivity summary row count changed",
    )
    checks.check(
        sensitivity.get("raw_row_count") == len(endpoint_sensitivity.get("raw_rows", [])) == 48,
        "endpoint sensitivity raw row count changed",
    )
    checks.check(
        sensitivity.get("source_policy_rows_completed")
        == endpoint_sensitivity.get("source_policy_rows_completed")
        == 0,
        "endpoint sensitivity overclosed source-policy rows",
    )
    checks.check(sensitivity.get("policy_count") == 4, "endpoint sensitivity policy count changed")
    checks.check(sensitivity.get("paper_method_count") == 4, "endpoint sensitivity method count changed")
    checks.check(
        float(sensitivity.get("max_terminal_time_offset_abs", 0.0)) > 0.007,
        "endpoint sensitivity lost noninteger T/h offset evidence",
    )

    checks.check(
        row_gap.get("gap_id") == "full_T10_source_grid_endpoint_policy_open",
        "row gap id changed",
    )
    checks.check(row_gap.get("gap_status") == "open", "row gap unexpectedly closed")
    checks.check(row_gap.get("can_resolve_without_heavy_run") is True, "non-heavy flag changed")
    checks.check(
        "full_T10_source_grid_endpoint_policy_open" in row_gap_ids,
        "row audit no longer carries full-T10 endpoint open blocker",
    )
    checks.check(
        closure.get("can_certify_full_T10_endpoint_policy_now") is False
        and closure.get("can_close_full_T10_source_grid_endpoint_policy_now") is False
        and closure.get("can_promote_tfe_source_policy_rows_now") is False,
        "closure decision overclaims endpoint source policy",
    )
    checks.check(
        len(cert.get("required_to_promote_full_T10_rows", [])) >= 6,
        "promotion requirement list unexpectedly short",
    )
    checks.check(
        source_files.get("source_grid_compatibility_audit") == "TFE_SOURCE_GRID_COMPATIBILITY_AUDIT.json"
        and source_files.get("endpoint_policy_boundary_certificate")
        == "TFE_ENDPOINT_POLICY_BOUNDARY_CERTIFICATE.json"
        and source_files.get("endpoint_policy_sensitivity_audit")
        == "TFE_ENDPOINT_POLICY_SENSITIVITY_AUDIT.json"
        and source_files.get("source_policy_row_audit") == "TFE_SOURCE_POLICY_ROW_AUDIT.json",
        "source file pointers changed",
    )

    for token in [
        "Status: **negative full-T10 endpoint-policy certificate; not source policy**.",
        "Certificate available: `True`.",
        "Positive full-T10 endpoint policy certified: `False`.",
        "Source grid policy resolved for full T=10: `False`.",
        "Exact-T error sampling source-equivalent: `False`.",
        "Source endpoint convention resolved for error sampling: `False`.",
        "Source-policy rows completed: `0`.",
        "Source-policy execution invoked / can close now: `False/False`.",
        "Source-policy execution allowed now/invoked/exact opt-in required: `False/False/True`.",
        "Safe action ids: `rebuild_read_only_audit_chain,rerun_read_only_validators,keep_narrowed_archive_provenance_only,monitor_reopen_conditions`.",
        "Opt-in action ids: `authorized_b4_ra_hi_source_policy_execution`.",
        "Non-heavy contract block closed: `False`.",
        "Grid rows/exact-compatible/incompatible/full-policy: `6/2/4/False`.",
        "Endpoint boundary exact/overrun/source rows/full-policy/exact-T-equivalent: `2/4/0/False/False`.",
        "Source text anchors/fixed-h-loop/error-sampling-resolved: `9/True/False`.",
        "Endpoint sensitivity summary/raw/source rows/policies/methods/max-offset: `16/48/0/4/4/8.000e-03`.",
        "Row-audit gap status/can-resolve-without-heavy-run: `open/True`.",
    ]:
        checks.check(token in cert_md, f"markdown missing token: {token}")

    if checks.errors:
        print("TFE full-T10 endpoint-policy closure certificate validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("TFE full-T10 endpoint-policy closure certificate validation: PASS")
    print("status=negative_full_T10_endpoint_policy_certificate_not_source_policy")
    print("source_grid_policy_resolved_for_full_T10=False")
    print("source_policy_rows_completed=0")
    print("source_policy_execution_invoked=False")
    print("source_policy_execution_allowed_now=False")
    print("can_close_now=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
