#!/usr/bin/env python3
"""Validate the local CMAME submission-integrity audit."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
from paper_paths import LATEX, package_path as manuscript_path
AUDIT_JSON = PAPER / "CMAME_SUBMISSION_INTEGRITY_AUDIT.json"
AUDIT_MD = PAPER / "CMAME_SUBMISSION_INTEGRITY_AUDIT.md"
EXPECTED_OC6_REOPEN_LATEST_EXTERNAL_PROBE = "2026-06-21/9/0/0/4/False/False"


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


def citation_keys(tex: str) -> list[str]:
    keys: list[str] = []
    for group in re.findall(r"\\cite\{([^}]*)\}", tex):
        keys.extend(key.strip() for key in group.split(",") if key.strip())
    return sorted(set(keys))


def bibitem_keys(tex: str) -> list[str]:
    return sorted(set(re.findall(r"\\bibitem\{([^}]*)\}", tex)))


def oc6_latest_probe(full_source_runner_gap: dict[str, Any]) -> dict[str, Any]:
    nested = full_source_runner_gap.get("oc6_source_equivalent_reopen_readiness_audit", {})
    if not isinstance(nested, dict):
        nested = {}
    top_level = {
        "date": full_source_runner_gap.get(
            "oc6_source_equivalent_reopen_readiness_latest_external_probe_date"
        ),
        "count": full_source_runner_gap.get(
            "oc6_source_equivalent_reopen_readiness_latest_external_probe_count"
        ),
        "positive_artifact_rows": full_source_runner_gap.get(
            "oc6_source_equivalent_reopen_readiness_latest_external_probe_positive_artifact_rows"
        ),
        "source_policy_rows_closed": full_source_runner_gap.get(
            "oc6_source_equivalent_reopen_readiness_latest_external_probe_source_policy_rows_closed"
        ),
        "access_limited_count": full_source_runner_gap.get(
            "oc6_source_equivalent_reopen_readiness_latest_external_probe_access_limited_count"
        ),
        "global_absence_proved": full_source_runner_gap.get(
            "oc6_source_equivalent_reopen_readiness_latest_external_probe_global_absence_proved"
        ),
        "reopen_triggered": full_source_runner_gap.get(
            "oc6_source_equivalent_reopen_readiness_latest_external_probe_reopen_triggered"
        ),
    }
    nested_fields = {
        "date": nested.get("latest_external_probe_date_checked"),
        "count": nested.get("latest_external_probe_count"),
        "positive_artifact_rows": nested.get("latest_external_probe_positive_public_code_artifact_rows"),
        "source_policy_rows_closed": nested.get("latest_external_probe_source_policy_rows_closed"),
        "access_limited_count": nested.get("latest_external_probe_access_limited_count"),
        "global_absence_proved": nested.get("latest_external_probe_global_absence_proved"),
        "reopen_triggered": nested.get("latest_external_probe_source_policy_reopen_triggered"),
    }
    marker = (
        f"{top_level['date']}/{top_level['count']}/{top_level['positive_artifact_rows']}/"
        f"{top_level['source_policy_rows_closed']}/{top_level['access_limited_count']}/"
        f"{top_level['global_absence_proved']}/{top_level['reopen_triggered']}"
    )
    return {
        **top_level,
        "marker": marker,
        "top_level_matches_nested": top_level == nested_fields,
    }


def main() -> int:
    checks = Checks()
    try:
        audit = read_json(AUDIT_JSON)
        audit_md = read_text(AUDIT_MD)
        reference_audit = read_json(PAPER / "REFERENCE_METADATA_AUDIT.json")
        main_tex = read_text(LATEX / "main_cmame.tex")
        flat_tex = read_text(LATEX / "cmame_submission_flat" / "main_cmame_submission.tex")
        manifest = read_json(PAPER / "SUBMISSION_ARTIFACT_MANIFEST.json")
        full_source_runner_gap = read_json(PAPER / "FULL_SOURCE_POLICY_RUNNER_ARCHIVE_GAP_AUDIT.json")
        objective_completion = read_json(PAPER / "OBJECTIVE_COMPLETION_AUDIT.json")
        reproducibility_manifest = read_json(PAPER / "CMAME_REPRODUCIBILITY_PACKAGE_MANIFEST.json")
    except Exception as exc:  # noqa: BLE001
        print(f"cmame_submission_integrity_audit=FAIL\n- {exc}")
        return 1

    main_cites = citation_keys(main_tex)
    main_bibs = bibitem_keys(main_tex)
    flat_cites = citation_keys(flat_tex)
    flat_bibs = bibitem_keys(flat_tex)
    citation_integrity = audit.get("citation_key_integrity", {})
    sidecars = audit.get("submission_sidecars", {})
    reference_summary = audit.get("reference_metadata_audit", {})
    boundary = audit.get("claim_boundary", {})
    manifest_boundary = audit.get("submission_manifest_boundary", {})
    objective_boundary = audit.get("objective_completion_boundary", {})
    manifest_action_boundary = manifest.get("full_source_policy_runner_archive_gap_action_boundary", {})
    manifest_narrowed_archive_boundary = manifest.get("narrowed_archive_boundary", {})
    reproducibility_narrowed_archive_boundary = reproducibility_manifest.get(
        "narrowed_archive_boundary", {}
    )
    oc6_probe = oc6_latest_probe(full_source_runner_gap)

    checks.check(audit.get("schema") == "cmame-submission-integrity-audit-v1", "schema changed")
    checks.check(
        audit.get("status") == "submission_integrity_passed_reference_web_verified",
        "audit status changed",
    )
    checks.check(audit.get("submission_ready") is False, "audit must not mark submission ready")
    checks.check(audit.get("local_integrity_passed") is True, "local citation/sidecar integrity must pass")
    checks.check(
        audit.get("external_reference_web_verification_complete") is True,
        "external web verification should be closed",
    )
    checks.check(
        audit.get("external_reference_web_verification_required_for_final_submission") is False,
        "external web verification requirement should be closed",
    )
    checks.check(
        reference_summary.get("schema") == reference_audit.get("schema") == "reference-metadata-audit-v1",
        "reference metadata audit not carried into submission-integrity audit",
    )
    checks.check(
        reference_summary.get("status") == "all_reference_metadata_web_verified",
        "reference metadata audit status changed",
    )
    checks.check(reference_summary.get("reference_count") == 28, "reference metadata reference count changed")
    checks.check(reference_summary.get("doi_reference_count") == 16, "reference metadata DOI count changed")
    checks.check(reference_summary.get("doi_metadata_verified_count") == 16, "verified DOI metadata count changed")
    checks.check(reference_summary.get("doi_metadata_unresolved_count") == 0, "unresolved DOI metadata count changed")
    checks.check(reference_summary.get("local_non_doi_reference_count") == 12, "local non-DOI count changed")
    checks.check(reference_summary.get("non_doi_metadata_verified_count") == 12, "verified non-DOI metadata count changed")
    checks.check(reference_summary.get("non_doi_reference_count") == 0, "open non-DOI reference count changed")
    checks.check(
        reference_summary.get("external_reference_web_verification_complete") is True,
        "reference metadata audit did not close external verification",
    )
    checks.check(
        reference_summary.get("bibliographic_metadata_web_verified") is True,
        "reference metadata audit did not close bibliographic verification",
    )
    checks.check(audit.get("read_only") is True, "audit must be read-only")
    checks.check(audit.get("run_v047_invoked") is False, "audit must not invoke run_v047")
    checks.check(audit.get("heavy_numerical_run_invoked") is False, "audit must not invoke heavy runs")
    checks.check(
        objective_boundary.get("schema")
        == objective_completion.get("schema")
        == "objective-completion-audit-v1",
        "objective completion schema not carried into submission-integrity audit",
    )
    checks.check(
        objective_boundary.get("status")
        == objective_completion.get("status")
        == "not_complete_submission_standard_open",
        "objective completion status not carried into submission-integrity audit",
    )
    checks.check(
        objective_boundary.get("objective_complete")
        == objective_completion.get("objective_complete")
        is False
        and objective_boundary.get("submission_ready")
        == objective_completion.get("submission_ready")
        is False,
        "objective completion readiness boundary changed in submission-integrity audit",
    )
    checks.check(
        objective_boundary.get("blocking_ids")
        == objective_completion.get("blocking_ids")
        == ["OC4", "OC6", "OC12"],
        "objective blocker IDs not carried into submission-integrity audit",
    )
    checks.check(
        objective_boundary.get("blockers_by_id") == objective_completion.get("blockers_by_id"),
        "objective blocker map stale in submission-integrity audit",
    )
    checks.check(
        objective_boundary.get("blocker_status_by_id")
        == objective_completion.get("blocker_status_by_id"),
        "objective blocker status map stale in submission-integrity audit",
    )
    checks.check(
        objective_boundary.get("blocker_next_actions_by_id")
        == objective_completion.get("blocker_next_actions_by_id"),
        "objective blocker next-action map stale in submission-integrity audit",
    )
    checks.check(
        objective_boundary.get("blocker_required_to_close_by_id")
        == objective_completion.get("blocker_required_to_close_by_id"),
        "objective blocker required-to-close map stale in submission-integrity audit",
    )
    checks.check(
        objective_boundary.get("blocker_safe_next_actions_by_id")
        == objective_completion.get("blocker_safe_next_actions_by_id"),
        "objective blocker safe-next-action map stale in submission-integrity audit",
    )
    checks.check(
        objective_boundary.get("blocker_opt_in_required_actions_by_id")
        == objective_completion.get("blocker_opt_in_required_actions_by_id"),
        "objective blocker opt-in-required-action map stale in submission-integrity audit",
    )
    checks.check(
        objective_boundary.get("source_policy_closed_ratio")
        == objective_completion.get("source_policy_closed_ratio")
        == "0/40",
        "objective source-policy ratio not carried into submission-integrity audit",
    )

    checks.check(citation_integrity.get("main_cited_key_count") == len(main_cites) == 28, "main cited key count changed")
    checks.check(citation_integrity.get("flat_cited_key_count") == len(flat_cites) == 28, "flat cited key count changed")
    checks.check(citation_integrity.get("main_bibitem_count") == len(main_bibs) == 28, "main bibitem count changed")
    checks.check(citation_integrity.get("flat_bibitem_count") == len(flat_bibs) == 28, "flat bibitem count changed")
    checks.check(citation_integrity.get("main_and_flat_citation_keys_match") is True, "main/flat citation keys differ")
    checks.check(citation_integrity.get("main_and_flat_bibitem_keys_match") is True, "main/flat bibitem keys differ")
    checks.check(citation_integrity.get("main_dangling_citation_keys") == [], "main has dangling citation keys")
    checks.check(citation_integrity.get("flat_dangling_citation_keys") == [], "flat has dangling citation keys")
    checks.check(citation_integrity.get("main_orphan_bibitem_keys") == [], "main has orphan bibitems")
    checks.check(citation_integrity.get("flat_orphan_bibitem_keys") == [], "flat has orphan bibitems")
    checks.check(citation_integrity.get("main_unresolved_log_lines") == [], "main log has unresolved citation lines")
    checks.check(citation_integrity.get("flat_unresolved_log_lines") == [], "flat log has unresolved citation lines")
    checks.check(citation_integrity.get("pdf_references_heading_present") is True, "main PDF references heading missing")
    checks.check(
        citation_integrity.get("flat_pdf_references_heading_present") is True,
        "flat PDF references heading missing",
    )

    checks.check(sidecars.get("declaration_tokens_present") is True, "main declarations incomplete")
    checks.check(sidecars.get("flat_declaration_tokens_present") is True, "flat declarations incomplete")
    checks.check(sidecars.get("highlight_count") == 5, "main highlight count changed")
    checks.check(sidecars.get("flat_highlight_count") == 5, "flat highlight count changed")
    checks.check(sidecars.get("highlight_count_in_elsevier_range") is True, "main highlight count outside range")
    checks.check(
        sidecars.get("flat_highlight_count_in_elsevier_range") is True,
        "flat highlight count outside range",
    )
    checks.check(sidecars.get("cover_letter_mentions_journal") is True, "cover letter missing journal")
    checks.check(sidecars.get("cover_letter_mentions_recommended_pdf") is True, "cover letter missing recommended PDF")

    checks.check(boundary.get("local_citation_key_integrity_closed") is True, "local citation integrity not closed")
    checks.check(boundary.get("bibliographic_metadata_web_verified") is True, "web metadata verification not closed")
    checks.check(boundary.get("submission_integrity_gate_closed") is True, "submission integrity gate not closed")
    checks.check(
        boundary.get("manifest_full_source_policy_boundary_checked") is True,
        "manifest full source-policy boundary not checked",
    )
    checks.check(
        manifest_boundary.get("schema") == manifest.get("schema") == "v047-submission-artifact-manifest-v1",
        "manifest schema not carried into submission-integrity audit",
    )
    checks.check(
        manifest_boundary.get("full_source_policy_runner_archive_gap_action_boundary")
        == manifest_action_boundary
        == full_source_runner_gap.get("action_boundary"),
        "manifest action boundary does not match archive gap audit",
    )
    checks.check(
        manifest_boundary.get("full_source_policy_runner_archive_gap_safe_action_ids")
        == manifest.get("full_source_policy_runner_archive_gap_safe_action_ids")
        == full_source_runner_gap.get("safe_action_ids"),
        "manifest safe action IDs do not match archive gap audit",
    )
    checks.check(
        manifest_boundary.get("full_source_policy_runner_archive_gap_opt_in_action_ids")
        == manifest.get("full_source_policy_runner_archive_gap_opt_in_action_ids")
        == full_source_runner_gap.get("opt_in_action_ids"),
        "manifest opt-in action IDs do not match archive gap audit",
    )
    checks.check(
        manifest_boundary.get("full_source_policy_runner_archive_gap_source_policy_execution_invoked")
        == manifest_boundary.get("source_policy_execution_invoked")
        == manifest.get("full_source_policy_runner_archive_gap_source_policy_execution_invoked")
        == full_source_runner_gap.get("source_policy_execution_invoked")
        is False,
        "manifest source-policy execution-invoked boundary does not match archive gap audit",
    )
    checks.check(
        manifest_boundary.get("manifest_boundary_matches_archive_gap") is True,
        "manifest boundary does not report archive-gap consistency",
    )
    checks.check(
        audit.get("manifest_boundary_matches_archive_gap")
        == manifest_boundary.get("manifest_boundary_matches_archive_gap")
        is True,
        "top-level manifest boundary match alias stale",
    )
    checks.check(
        manifest_boundary.get("generic_blocker_aliases_match_objective") is True,
        "manifest generic blocker aliases do not report objective consistency",
    )
    checks.check(
        manifest_boundary.get("blocker_required_to_close_by_id")
        == manifest.get("blocker_required_to_close_by_id")
        == manifest_boundary.get("objective_blocker_required_to_close_by_id")
        == manifest.get("objective_blocker_required_to_close_by_id")
        == objective_completion.get("blocker_required_to_close_by_id"),
        "manifest generic required-to-close blocker alias stale in submission-integrity audit",
    )
    checks.check(
        manifest_boundary.get("blocker_safe_next_actions_by_id")
        == manifest.get("blocker_safe_next_actions_by_id")
        == manifest_boundary.get("objective_blocker_safe_next_actions_by_id")
        == manifest.get("objective_blocker_safe_next_actions_by_id")
        == objective_completion.get("blocker_safe_next_actions_by_id"),
        "manifest generic safe-next-actions blocker alias stale in submission-integrity audit",
    )
    checks.check(
        manifest_boundary.get("blocker_opt_in_required_actions_by_id")
        == manifest.get("blocker_opt_in_required_actions_by_id")
        == manifest_boundary.get("objective_blocker_opt_in_required_actions_by_id")
        == manifest.get("objective_blocker_opt_in_required_actions_by_id")
        == objective_completion.get("blocker_opt_in_required_actions_by_id"),
        "manifest generic opt-in-required blocker alias stale in submission-integrity audit",
    )
    checks.check(
        manifest_boundary.get("narrowed_archive_boundary")
        == manifest_narrowed_archive_boundary
        == reproducibility_narrowed_archive_boundary,
        "manifest narrowed archive boundary not carried into submission-integrity audit",
    )
    checks.check(
        manifest_boundary.get("narrowed_archive_boundary_matches_reproducibility_manifest") is True,
        "manifest narrowed archive boundary does not report reproducibility-manifest consistency",
    )
    checks.check(
        manifest_narrowed_archive_boundary.get("status")
        == "narrowed_archive_ready_not_full_source_policy_runner_archive"
        and manifest_narrowed_archive_boundary.get("scope") == "narrowed_claim_only"
        and manifest_narrowed_archive_boundary.get("blocking_ids")
        == objective_completion.get("blocking_ids")
        and manifest_narrowed_archive_boundary.get("blocker_status_by_id")
        == objective_completion.get("blocker_status_by_id")
        and manifest_narrowed_archive_boundary.get("source_policy_closed_ratio")
        == objective_completion.get("source_policy_closed_ratio")
        == "0/40",
        "manifest narrowed archive blocker/source-policy boundary changed",
    )
    checks.check(
        manifest_boundary.get("narrowed_archive_boundary_status")
        == manifest.get("narrowed_archive_boundary_status")
        == manifest_narrowed_archive_boundary.get("status")
        and manifest_boundary.get("narrowed_archive_boundary_source_policy_closed_ratio")
        == manifest.get("narrowed_archive_boundary_source_policy_closed_ratio")
        == manifest_narrowed_archive_boundary.get("source_policy_closed_ratio")
        and manifest_boundary.get(
            "narrowed_archive_boundary_current_archive_usable_as_full_source_policy_runner_archive"
        )
        == manifest.get(
            "narrowed_archive_boundary_current_archive_usable_as_full_source_policy_runner_archive"
        )
        == manifest_narrowed_archive_boundary.get(
            "current_archive_usable_as_full_source_policy_runner_archive"
        )
        and manifest_boundary.get("narrowed_archive_boundary_source_policy_execution_allowed_now")
        == manifest.get("narrowed_archive_boundary_source_policy_execution_allowed_now")
        == manifest_narrowed_archive_boundary.get("source_policy_execution_allowed_now")
        and manifest_boundary.get("narrowed_archive_boundary_exact_b4_opt_in_required_for_execution")
        == manifest.get("narrowed_archive_boundary_exact_b4_opt_in_required_for_execution")
        == manifest_narrowed_archive_boundary.get("exact_b4_opt_in_required_for_execution")
        and manifest_boundary.get("narrowed_archive_boundary_safe_action_ids")
        == manifest.get("narrowed_archive_boundary_safe_action_ids")
        == manifest_narrowed_archive_boundary.get("safe_action_ids")
        and manifest_boundary.get("narrowed_archive_boundary_opt_in_action_ids")
        == manifest.get("narrowed_archive_boundary_opt_in_action_ids")
        == manifest_narrowed_archive_boundary.get("opt_in_action_ids"),
        "manifest narrowed archive aliases not carried into submission-integrity audit",
    )
    checks.check(
        manifest_boundary.get("source_policy_execution_allowed_now") is False
        and manifest_boundary.get("exact_b4_opt_in_required_for_execution") is True
        and manifest_boundary.get("safe_without_b4_opt_in_count") == 4
        and manifest_boundary.get("opt_in_required_action_count") == 1
        and manifest_boundary.get("opt_in_required_command_count") == 13
        and manifest_boundary.get("opt_in_required_mapped_external_rows") == 20,
        "manifest boundary counts changed",
    )
    checks.check(
        audit.get("manifest_source_policy_execution_invoked")
        == audit.get("source_policy_execution_invoked")
        == manifest_boundary.get("source_policy_execution_invoked")
        == full_source_runner_gap.get("source_policy_execution_invoked")
        is False,
        "top-level manifest/source-policy execution alias stale",
    )
    checks.check(
        audit.get("source_policy_closed_ratio")
        == manifest_boundary.get("narrowed_archive_boundary_source_policy_closed_ratio")
        == manifest_narrowed_archive_boundary.get("source_policy_closed_ratio")
        == "0/40",
        "top-level source-policy closed-ratio alias stale",
    )
    checks.check(
        audit.get("oc12_archive_action_boundary")
        == manifest_boundary.get("full_source_policy_runner_archive_gap_action_boundary")
        == full_source_runner_gap.get("action_boundary"),
        "top-level OC12 action boundary alias stale",
    )
    checks.check(
        audit.get("oc12_archive_safe_action_ids")
        == manifest_boundary.get("full_source_policy_runner_archive_gap_safe_action_ids")
        == full_source_runner_gap.get("safe_action_ids")
        and audit.get("oc12_archive_opt_in_action_ids")
        == manifest_boundary.get("full_source_policy_runner_archive_gap_opt_in_action_ids")
        == full_source_runner_gap.get("opt_in_action_ids"),
        "top-level OC12 action-id aliases stale",
    )
    checks.check(
        audit.get("oc12_archive_source_policy_execution_allowed_now")
        == manifest_boundary.get("source_policy_execution_allowed_now")
        is False
        and audit.get("oc12_archive_source_policy_execution_invoked")
        == manifest_boundary.get("source_policy_execution_invoked")
        is False
        and audit.get("oc12_archive_exact_b4_opt_in_required_for_execution")
        == manifest_boundary.get("exact_b4_opt_in_required_for_execution")
        is True
        and audit.get("oc12_archive_opt_in_required_command_count")
        == manifest_boundary.get("opt_in_required_command_count")
        == 13
        and audit.get("oc12_archive_opt_in_required_mapped_external_rows")
        == manifest_boundary.get("opt_in_required_mapped_external_rows")
        == 20,
        "top-level OC12 execution/count aliases stale",
    )
    checks.check(
        manifest_boundary.get("oc6_reopen_latest_external_probe")
        == manifest.get("oc6_reopen_latest_external_probe")
        == oc6_probe["marker"]
        == EXPECTED_OC6_REOPEN_LATEST_EXTERNAL_PROBE,
        "OC6 latest external probe marker not carried from manifest into submission-integrity audit",
    )
    checks.check(
        manifest_boundary.get("oc6_reopen_latest_external_probe_date")
        == manifest.get("oc6_reopen_latest_external_probe_date")
        == oc6_probe["date"]
        == "2026-06-21",
        "OC6 latest external probe date changed",
    )
    checks.check(
        manifest_boundary.get("oc6_reopen_latest_external_probe_count")
        == manifest.get("oc6_reopen_latest_external_probe_count")
        == oc6_probe["count"]
        == 9,
        "OC6 latest external probe count changed",
    )
    checks.check(
        manifest_boundary.get("oc6_reopen_latest_external_probe_positive_artifact_rows")
        == manifest.get("oc6_reopen_latest_external_probe_positive_artifact_rows")
        == oc6_probe["positive_artifact_rows"]
        == 0,
        "OC6 latest external probe positive artifact rows changed",
    )
    checks.check(
        manifest_boundary.get("oc6_reopen_latest_external_probe_source_policy_rows_closed")
        == manifest.get("oc6_reopen_latest_external_probe_source_policy_rows_closed")
        == oc6_probe["source_policy_rows_closed"]
        == 0,
        "OC6 latest external probe source-policy closed rows changed",
    )
    checks.check(
        manifest_boundary.get("oc6_reopen_latest_external_probe_access_limited_count")
        == manifest.get("oc6_reopen_latest_external_probe_access_limited_count")
        == oc6_probe["access_limited_count"]
        == 4,
        "OC6 latest external probe access-limited count changed",
    )
    checks.check(
        manifest_boundary.get("oc6_reopen_latest_external_probe_global_absence_proved")
        == manifest.get("oc6_reopen_latest_external_probe_global_absence_proved")
        == oc6_probe["global_absence_proved"]
        is False,
        "OC6 latest external probe global-absence flag changed",
    )
    checks.check(
        manifest_boundary.get("oc6_reopen_latest_external_probe_reopen_triggered")
        == manifest.get("oc6_reopen_latest_external_probe_reopen_triggered")
        == oc6_probe["reopen_triggered"]
        is False,
        "OC6 latest external probe reopen flag changed",
    )
    checks.check(
        manifest_boundary.get("oc6_reopen_latest_external_probe_matches_archive_gap")
        == oc6_probe["top_level_matches_nested"]
        is True,
        "OC6 latest external probe nested/top-level archive-gap consistency changed",
    )
    checks.check(
        boundary.get("oc6_latest_external_probe_checked") is True,
        "claim boundary does not record OC6 latest external probe check",
    )
    checks.check(
        "external reference web verification complete: `true`" in audit_md.lower(),
        "MD missing closed web-verification boundary",
    )
    checks.check(
        "DOI metadata verified: `16/16`" in audit_md,
        "MD missing DOI metadata verification count",
    )
    checks.check(
        "Non-DOI metadata verified: `12/12`" in audit_md,
        "MD missing non-DOI verified count",
    )
    checks.check(
        "Non-DOI references still open: `0`" in audit_md,
        "MD missing non-DOI open count",
    )
    checks.check(
        "Full source-policy archive boundary matches archive gap audit: `True`" in audit_md,
        "MD missing manifest/archive boundary match",
    )
    checks.check(
        "Manifest safe/opt-in action counts: `4/1`" in audit_md,
        "MD missing manifest action counts",
    )
    checks.check(
        "Manifest source-policy execution allowed now / invoked / exact opt-in required: `False/False/True`" in audit_md,
        "MD missing manifest execution boundary",
    )
    checks.check(
        "Manifest opt-in commands/mapped rows: `13/20`" in audit_md,
        "MD missing manifest opt-in command boundary",
    )
    checks.check(
        "Manifest safe action ids: `rebuild_read_only_audit_chain,rerun_read_only_validators,keep_narrowed_archive_provenance_only,monitor_reopen_conditions`"
        in audit_md,
        "MD missing manifest safe action IDs",
    )
    checks.check(
        "Manifest opt-in action ids: `authorized_b4_ra_hi_source_policy_execution`" in audit_md,
        "MD missing manifest opt-in action IDs",
    )
    checks.check(
        "Manifest narrowed archive boundary/status/source-policy/use/execution/exact: `narrowed_archive_ready_not_full_source_policy_runner_archive/0/40/False/False/True`"
        in audit_md,
        "MD missing narrowed archive execution boundary",
    )
    checks.check(
        "Manifest narrowed archive boundary matches reproducibility manifest: `True`" in audit_md,
        "MD missing narrowed archive reproducibility-manifest match",
    )
    checks.check(
        "Manifest narrowed archive safe/opt-in action ids: `rebuild_read_only_audit_chain,rerun_read_only_validators,keep_narrowed_archive_provenance_only,monitor_reopen_conditions` / `authorized_b4_ra_hi_source_policy_execution`"
        in audit_md,
        "MD missing narrowed archive safe/opt-in action IDs",
    )
    checks.check(
        "Top-level OC12 archive action boundary safe/opt-in/allowed/invoked/exact/commands/rows: `4/1/False/False/True/13/20`"
        in audit_md,
        "MD missing top-level OC12 archive action boundary",
    )
    checks.check(
        "Top-level OC12 archive safe/opt-in action ids: `rebuild_read_only_audit_chain,rerun_read_only_validators,keep_narrowed_archive_provenance_only,monitor_reopen_conditions` / `authorized_b4_ra_hi_source_policy_execution`"
        in audit_md,
        "MD missing top-level OC12 safe/opt-in action IDs",
    )
    checks.check(
        "Objective blocker status by id: `{'OC4': 'open', 'OC6': 'partial', 'OC12': 'partial'}`."
        in audit_md,
        "MD missing objective blocker status map",
    )
    checks.check(
        "Objective blocker next actions by id: `{'OC4': 'RA/HI can only close through exact B4 opt-in authorized closeout or a new source-policy promotion artifact; TFE/VP remain unable-to-reproduce/not-promoted'"
        in audit_md,
        "MD missing objective blocker next-action map",
    )
    checks.check(
        "Objective blocker required-to-close by id:" in audit_md,
        "MD missing objective blocker required-to-close map",
    )
    checks.check(
        "Objective blocker safe next actions by id:" in audit_md,
        "MD missing objective blocker safe-next-action map",
    )
    checks.check(
        "Objective blocker opt-in required actions by id:" in audit_md,
        "MD missing objective blocker opt-in-required-action map",
    )
    checks.check(
        "Submission manifest generic blocker aliases match objective: `True`." in audit_md,
        "MD missing submission manifest generic blocker alias marker",
    )
    checks.check(
        f"OC6 reopen latest external probe carried by full-archive gap: `{EXPECTED_OC6_REOPEN_LATEST_EXTERNAL_PROBE}`"
        in audit_md,
        "MD missing OC6 latest external probe marker",
    )
    checks.check(
        "OC6 reopen latest external probe nested/top-level match: `True`" in audit_md,
        "MD missing OC6 archive-gap consistency marker",
    )

    checks.check(
        manifest.get("cmame_submission_integrity_audit") == "CMAME_SUBMISSION_INTEGRITY_AUDIT.md",
        "manifest missing submission integrity audit",
    )
    checks.check(
        manifest.get("cmame_submission_integrity_audit_json") == "CMAME_SUBMISSION_INTEGRITY_AUDIT.json",
        "manifest missing submission integrity audit JSON",
    )
    checks.check(
        "CMAME_SUBMISSION_INTEGRITY_AUDIT.md" in manifest.get("evidence_anchors", []),
        "manifest missing integrity audit anchor",
    )
    checks.check(
        "CMAME_SUBMISSION_INTEGRITY_AUDIT.json" in manifest.get("evidence_anchors", []),
        "manifest missing integrity audit JSON anchor",
    )
    checks.check(
        manifest.get("reference_metadata_audit") == "REFERENCE_METADATA_AUDIT.md",
        "manifest missing reference metadata audit",
    )
    checks.check(
        manifest.get("reference_metadata_audit_json") == "REFERENCE_METADATA_AUDIT.json",
        "manifest missing reference metadata audit JSON",
    )
    checks.check(
        "REFERENCE_METADATA_AUDIT.md" in manifest.get("evidence_anchors", []),
        "manifest missing reference metadata audit anchor",
    )
    checks.check(
        "REFERENCE_METADATA_AUDIT.json" in manifest.get("evidence_anchors", []),
        "manifest missing reference metadata audit JSON anchor",
    )
    checks.check(
        "validate_cmame_submission_integrity_audit.py" in manifest.get("validators", []),
        "manifest missing integrity audit validator",
    )
    checks.check(
        "validate_reference_metadata_audit.py" in manifest.get("validators", []),
        "manifest missing reference metadata audit validator",
    )

    forbidden = set(audit.get("forbidden_claims", []))
    for token in ["submission_ready_true"]:
        checks.check(token in forbidden, f"forbidden claim missing: {token}")
    for token in [
        "external_reference_web_verification_complete_true",
        "bibliographic_metadata_verified_true",
        "submission_integrity_gate_closed_true",
    ]:
        checks.check(token not in forbidden, f"closed integrity claim incorrectly forbidden: {token}")

    if checks.errors:
        print("cmame_submission_integrity_audit=FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("cmame_submission_integrity_audit=PASS")
    print("local_integrity_passed=True")
    print("citation_keys=28/28")
    print("dangling_citation_keys=0")
    print("orphan_bibitems=0")
    print("doi_metadata_verified=16/16")
    print("non_doi_metadata_verified=12/12")
    print("non_doi_reference_count=0")
    print("external_reference_web_verification_complete=True")
    print("manifest_boundary_matches_archive_gap=True")
    print("manifest_source_policy_execution_invoked=False")
    print(f"oc6_reopen_latest_external_probe={EXPECTED_OC6_REOPEN_LATEST_EXTERNAL_PROBE}")
    print("submission_ready=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
