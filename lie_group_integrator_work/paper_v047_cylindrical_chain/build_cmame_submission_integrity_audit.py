#!/usr/bin/env python3
"""Build a local CMAME submission-integrity audit.

The audit is intentionally local and read-only with respect to numerical
artifacts. It verifies citation-key consistency, sidecar submission files, and
unresolved-reference markers. It does not perform the ARS-required web
verification of every bibliographic item, so it cannot close submission
readiness by itself.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
OUT_JSON = PAPER / "CMAME_SUBMISSION_INTEGRITY_AUDIT.json"
OUT_MD = PAPER / "CMAME_SUBMISSION_INTEGRITY_AUDIT.md"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def read_json_if_present(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def citation_keys(tex: str) -> list[str]:
    keys: list[str] = []
    for group in re.findall(r"\\cite\{([^}]*)\}", tex):
        keys.extend(key.strip() for key in group.split(",") if key.strip())
    return sorted(set(keys))


def bibitem_keys(tex: str) -> list[str]:
    return sorted(set(re.findall(r"\\bibitem\{([^}]*)\}", tex)))


def count_citation_groups(tex: str) -> int:
    return len(re.findall(r"\\cite\{[^}]*\}", tex))


def unresolved_markers(log_text: str) -> list[str]:
    patterns = [
        "Citation",
        "undefined",
        "There were undefined references",
        "Reference",
    ]
    return [
        line.strip()
        for line in log_text.splitlines()
        if "undefined" in line.lower() and any(pattern.lower() in line.lower() for pattern in patterns)
    ]


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


def sidecar_status() -> dict[str, Any]:
    declarations = read_text(PAPER / "declarations_cmame.md")
    flat_declarations = read_text(PAPER / "cmame_submission_flat" / "declarations_cmame.md")
    highlights = read_text(PAPER / "highlights_cmame.txt")
    flat_highlights = read_text(PAPER / "cmame_submission_flat" / "highlights_cmame.txt")
    cover = read_text(PAPER / "COVER_LETTER.md")
    declaration_tokens = [
        "Declaration of Competing Interest",
        "Funding",
        "Data Availability",
        "Declaration of Generative AI and AI-Assisted Technologies",
    ]
    highlight_items = [line for line in highlights.splitlines() if line.strip().startswith("- ")]
    flat_highlight_items = [line for line in flat_highlights.splitlines() if line.strip().startswith("- ")]
    return {
        "declarations_present": True,
        "flat_declarations_present": True,
        "declaration_tokens_present": all(token in declarations for token in declaration_tokens),
        "flat_declaration_tokens_present": all(token in flat_declarations for token in declaration_tokens),
        "highlights_present": True,
        "flat_highlights_present": True,
        "highlight_count": len(highlight_items),
        "flat_highlight_count": len(flat_highlight_items),
        "highlight_count_in_elsevier_range": 3 <= len(highlight_items) <= 5,
        "flat_highlight_count_in_elsevier_range": 3 <= len(flat_highlight_items) <= 5,
        "cover_letter_present": True,
        "cover_letter_mentions_journal": "Computer Methods in Applied Mechanics and Engineering" in cover,
        "cover_letter_mentions_recommended_pdf": "main_cmame.pdf" in cover,
    }


def main() -> None:
    main_tex = read_text(PAPER / "main_cmame.tex")
    flat_tex = read_text(PAPER / "cmame_submission_flat" / "main_cmame_submission.tex")
    main_log = read_text(PAPER / "main_cmame.log")
    flat_log = read_text(PAPER / "cmame_submission_flat" / "main_cmame_submission.log")
    main_pdf_text = read_text(PAPER / "main_cmame.txt")
    flat_pdf_text = read_text(PAPER / "cmame_submission_flat" / "main_cmame_submission.txt")
    reference_audit = read_json_if_present(PAPER / "REFERENCE_METADATA_AUDIT.json")
    manifest = read_json_if_present(PAPER / "SUBMISSION_ARTIFACT_MANIFEST.json")
    full_source_runner_gap = read_json_if_present(PAPER / "FULL_SOURCE_POLICY_RUNNER_ARCHIVE_GAP_AUDIT.json")
    objective_completion = read_json_if_present(PAPER / "OBJECTIVE_COMPLETION_AUDIT.json")
    reproducibility_manifest = read_json_if_present(
        PAPER / "CMAME_REPRODUCIBILITY_PACKAGE_MANIFEST.json"
    )
    objective_blocking_ids = list(objective_completion.get("blocking_ids", []))
    objective_blockers_by_id = {
        req_id: objective_completion.get("blockers_by_id", {}).get(req_id)
        for req_id in objective_blocking_ids
    }
    objective_blocker_status_by_id = {
        req_id: objective_completion.get("blocker_status_by_id", {}).get(req_id)
        for req_id in objective_blocking_ids
    }
    objective_blocker_next_actions_by_id = {
        req_id: objective_completion.get("blocker_next_actions_by_id", {}).get(req_id)
        for req_id in objective_blocking_ids
    }
    objective_blocker_required_to_close_by_id = {
        req_id: objective_completion.get("blocker_required_to_close_by_id", {}).get(req_id)
        for req_id in objective_blocking_ids
    }
    objective_blocker_safe_next_actions_by_id = {
        req_id: objective_completion.get("blocker_safe_next_actions_by_id", {}).get(req_id)
        for req_id in objective_blocking_ids
    }
    objective_blocker_opt_in_required_actions_by_id = {
        req_id: objective_completion.get("blocker_opt_in_required_actions_by_id", {}).get(req_id)
        for req_id in objective_blocking_ids
    }

    main_cites = citation_keys(main_tex)
    main_bibs = bibitem_keys(main_tex)
    flat_cites = citation_keys(flat_tex)
    flat_bibs = bibitem_keys(flat_tex)
    main_dangling = sorted(set(main_cites) - set(main_bibs))
    main_orphans = sorted(set(main_bibs) - set(main_cites))
    flat_dangling = sorted(set(flat_cites) - set(flat_bibs))
    flat_orphans = sorted(set(flat_bibs) - set(flat_cites))
    main_unresolved = unresolved_markers(main_log)
    flat_unresolved = unresolved_markers(flat_log)
    sidecars = sidecar_status()

    local_integrity_passed = not (
        main_dangling
        or main_orphans
        or flat_dangling
        or flat_orphans
        or main_unresolved
        or flat_unresolved
        or main_cites != flat_cites
        or main_bibs != flat_bibs
        or not sidecars["declaration_tokens_present"]
        or not sidecars["flat_declaration_tokens_present"]
        or not sidecars["highlight_count_in_elsevier_range"]
        or not sidecars["flat_highlight_count_in_elsevier_range"]
        or "References" not in main_pdf_text
        or "References" not in flat_pdf_text
    )
    reference_web_verified = (
        reference_audit.get("external_reference_web_verification_complete") is True
        and reference_audit.get("bibliographic_metadata_web_verified") is True
        and reference_audit.get("non_doi_reference_count") == 0
        and reference_audit.get("doi_metadata_unresolved_count") == 0
    )
    manifest_action_boundary = manifest.get("full_source_policy_runner_archive_gap_action_boundary", {})
    manifest_narrowed_archive_boundary = manifest.get("narrowed_archive_boundary", {})
    reproducibility_narrowed_archive_boundary = reproducibility_manifest.get(
        "narrowed_archive_boundary", {}
    )
    manifest_narrowed_boundary_matches_reproducibility = (
        manifest_narrowed_archive_boundary == reproducibility_narrowed_archive_boundary
    )
    oc6_probe = oc6_latest_probe(full_source_runner_gap)
    manifest_oc6_probe = {
        "marker": manifest.get("oc6_reopen_latest_external_probe"),
        "date": manifest.get("oc6_reopen_latest_external_probe_date"),
        "count": manifest.get("oc6_reopen_latest_external_probe_count"),
        "positive_artifact_rows": manifest.get(
            "oc6_reopen_latest_external_probe_positive_artifact_rows"
        ),
        "source_policy_rows_closed": manifest.get(
            "oc6_reopen_latest_external_probe_source_policy_rows_closed"
        ),
        "access_limited_count": manifest.get("oc6_reopen_latest_external_probe_access_limited_count"),
        "global_absence_proved": manifest.get("oc6_reopen_latest_external_probe_global_absence_proved"),
        "reopen_triggered": manifest.get("oc6_reopen_latest_external_probe_reopen_triggered"),
    }
    manifest_oc6_probe_matches_archive_gap = (
        manifest_oc6_probe["marker"] == oc6_probe["marker"]
        and manifest_oc6_probe["date"] == oc6_probe["date"]
        and manifest_oc6_probe["count"] == oc6_probe["count"]
        and manifest_oc6_probe["positive_artifact_rows"] == oc6_probe["positive_artifact_rows"]
        and manifest_oc6_probe["source_policy_rows_closed"] == oc6_probe["source_policy_rows_closed"]
        and manifest_oc6_probe["access_limited_count"] == oc6_probe["access_limited_count"]
        and manifest_oc6_probe["global_absence_proved"] == oc6_probe["global_absence_proved"]
        and manifest_oc6_probe["reopen_triggered"] == oc6_probe["reopen_triggered"]
        and oc6_probe["top_level_matches_nested"] is True
    )
    manifest_boundary_matches_archive_gap = (
        manifest_action_boundary == full_source_runner_gap.get("action_boundary")
        and manifest.get("full_source_policy_runner_archive_gap_safe_action_ids")
        == full_source_runner_gap.get("safe_action_ids")
        and manifest.get("full_source_policy_runner_archive_gap_opt_in_action_ids")
        == full_source_runner_gap.get("opt_in_action_ids")
        and manifest.get("full_source_policy_runner_archive_gap_source_policy_execution_invoked")
        == full_source_runner_gap.get("source_policy_execution_invoked")
        is False
        and manifest_oc6_probe_matches_archive_gap
    )
    integrity_gate_closed = local_integrity_passed and reference_web_verified
    status = "submission_integrity_passed_reference_web_verified" if integrity_gate_closed else (
        "local_submission_integrity_pass_external_reference_web_verification_open"
        if local_integrity_passed
        else "local_submission_integrity_failed"
    )

    result = {
        "schema": "cmame-submission-integrity-audit-v1",
        "status": status,
        "submission_ready": False,
        "source_policy_execution_allowed_now": manifest.get(
            "narrowed_archive_boundary_source_policy_execution_allowed_now"
        ),
        "source_policy_execution_invoked": manifest.get(
            "narrowed_archive_boundary_source_policy_execution_invoked",
            manifest.get("full_source_policy_runner_archive_gap_source_policy_execution_invoked"),
        ),
        "manifest_boundary_matches_archive_gap": manifest_boundary_matches_archive_gap,
        "manifest_source_policy_execution_invoked": manifest.get(
            "full_source_policy_runner_archive_gap_source_policy_execution_invoked"
        ),
        "source_policy_closed_ratio": manifest.get("narrowed_archive_boundary_source_policy_closed_ratio"),
        "exact_b4_opt_in_required_for_execution": manifest.get(
            "narrowed_archive_boundary_exact_b4_opt_in_required_for_execution"
        ),
        "safe_action_ids": manifest.get("narrowed_archive_boundary_safe_action_ids", []),
        "opt_in_action_ids": manifest.get("narrowed_archive_boundary_opt_in_action_ids", []),
        "required_user_approval_statement": manifest.get(
            "narrowed_archive_boundary_required_user_approval_statement",
            manifest_narrowed_archive_boundary.get("required_user_approval_statement"),
        ),
        "guarded_execution_driver": manifest.get(
            "narrowed_archive_boundary_guarded_execution_driver",
            manifest_narrowed_archive_boundary.get("guarded_execution_driver"),
        ),
        "oc12_archive_action_boundary": manifest_action_boundary,
        "oc12_archive_safe_action_ids": manifest.get(
            "full_source_policy_runner_archive_gap_safe_action_ids", []
        ),
        "oc12_archive_opt_in_action_ids": manifest.get(
            "full_source_policy_runner_archive_gap_opt_in_action_ids", []
        ),
        "oc12_archive_source_policy_execution_allowed_now": manifest_action_boundary.get(
            "source_policy_execution_allowed_now"
        ),
        "oc12_archive_source_policy_execution_invoked": manifest.get(
            "full_source_policy_runner_archive_gap_source_policy_execution_invoked"
        ),
        "oc12_archive_exact_b4_opt_in_required_for_execution": manifest_action_boundary.get(
            "exact_b4_opt_in_required_for_execution"
        ),
        "oc12_archive_opt_in_required_command_count": manifest_action_boundary.get(
            "opt_in_required_command_count"
        ),
        "oc12_archive_opt_in_required_mapped_external_rows": manifest_action_boundary.get(
            "opt_in_required_mapped_external_rows"
        ),
        "local_integrity_passed": local_integrity_passed,
        "external_reference_web_verification_complete": reference_web_verified,
        "external_reference_web_verification_required_for_final_submission": not reference_web_verified,
        "reference_metadata_audit": {
            "schema": reference_audit.get("schema"),
            "status": reference_audit.get("status"),
            "reference_count": reference_audit.get("reference_count"),
            "doi_reference_count": reference_audit.get("doi_reference_count"),
            "doi_metadata_verified_count": reference_audit.get("doi_metadata_verified_count"),
            "doi_metadata_unresolved_count": reference_audit.get("doi_metadata_unresolved_count"),
            "local_non_doi_reference_count": reference_audit.get("local_non_doi_reference_count"),
            "non_doi_metadata_verified_count": reference_audit.get("non_doi_metadata_verified_count"),
            "non_doi_reference_count": reference_audit.get("non_doi_reference_count"),
            "external_reference_web_verification_complete": reference_audit.get(
                "external_reference_web_verification_complete", False
            ),
            "bibliographic_metadata_web_verified": reference_audit.get("bibliographic_metadata_web_verified", False),
        },
        "read_only": True,
        "run_v047_invoked": False,
        "heavy_numerical_run_invoked": False,
        "objective_completion_boundary": {
            "schema": objective_completion.get("schema"),
            "status": objective_completion.get("status"),
            "objective_complete": objective_completion.get("objective_complete"),
            "submission_ready": objective_completion.get("submission_ready"),
            "blocking_ids": objective_blocking_ids,
            "blockers_by_id": objective_blockers_by_id,
            "blocker_status_by_id": objective_blocker_status_by_id,
            "blocker_next_actions_by_id": objective_blocker_next_actions_by_id,
            "blocker_required_to_close_by_id": objective_blocker_required_to_close_by_id,
            "blocker_safe_next_actions_by_id": objective_blocker_safe_next_actions_by_id,
            "blocker_opt_in_required_actions_by_id": objective_blocker_opt_in_required_actions_by_id,
            "source_policy_closed_ratio": objective_completion.get("source_policy_closed_ratio"),
        },
        "citation_key_integrity": {
            "main_citation_group_count": count_citation_groups(main_tex),
            "flat_citation_group_count": count_citation_groups(flat_tex),
            "main_cited_key_count": len(main_cites),
            "flat_cited_key_count": len(flat_cites),
            "main_bibitem_count": len(main_bibs),
            "flat_bibitem_count": len(flat_bibs),
            "main_and_flat_citation_keys_match": main_cites == flat_cites,
            "main_and_flat_bibitem_keys_match": main_bibs == flat_bibs,
            "main_dangling_citation_keys": main_dangling,
            "main_orphan_bibitem_keys": main_orphans,
            "flat_dangling_citation_keys": flat_dangling,
            "flat_orphan_bibitem_keys": flat_orphans,
            "main_unresolved_log_lines": main_unresolved,
            "flat_unresolved_log_lines": flat_unresolved,
            "pdf_references_heading_present": "References" in main_pdf_text,
            "flat_pdf_references_heading_present": "References" in flat_pdf_text,
        },
        "submission_sidecars": sidecars,
        "submission_manifest_boundary": {
            "schema": manifest.get("schema"),
            "full_source_policy_runner_archive_gap_action_boundary": manifest_action_boundary,
            "full_source_policy_runner_archive_gap_safe_action_ids": manifest.get(
                "full_source_policy_runner_archive_gap_safe_action_ids", []
            ),
            "full_source_policy_runner_archive_gap_opt_in_action_ids": manifest.get(
                "full_source_policy_runner_archive_gap_opt_in_action_ids", []
            ),
            "full_source_policy_runner_archive_gap_source_policy_execution_invoked": manifest.get(
                "full_source_policy_runner_archive_gap_source_policy_execution_invoked"
            ),
            "narrowed_archive_boundary": manifest_narrowed_archive_boundary,
            "narrowed_archive_boundary_matches_reproducibility_manifest": (
                manifest_narrowed_boundary_matches_reproducibility
            ),
            "narrowed_archive_boundary_status": manifest.get("narrowed_archive_boundary_status"),
            "narrowed_archive_boundary_source_policy_closed_ratio": manifest.get(
                "narrowed_archive_boundary_source_policy_closed_ratio"
            ),
            "narrowed_archive_boundary_current_archive_usable_as_full_source_policy_runner_archive": (
                manifest.get(
                    "narrowed_archive_boundary_current_archive_usable_as_full_source_policy_runner_archive"
                )
            ),
            "narrowed_archive_boundary_source_policy_execution_allowed_now": manifest.get(
                "narrowed_archive_boundary_source_policy_execution_allowed_now"
            ),
            "narrowed_archive_boundary_exact_b4_opt_in_required_for_execution": manifest.get(
                "narrowed_archive_boundary_exact_b4_opt_in_required_for_execution"
            ),
            "narrowed_archive_boundary_safe_action_ids": manifest.get(
                "narrowed_archive_boundary_safe_action_ids", []
            ),
            "narrowed_archive_boundary_opt_in_action_ids": manifest.get(
                "narrowed_archive_boundary_opt_in_action_ids", []
            ),
            "blocker_required_to_close_by_id": manifest.get("blocker_required_to_close_by_id"),
            "blocker_safe_next_actions_by_id": manifest.get("blocker_safe_next_actions_by_id"),
            "blocker_opt_in_required_actions_by_id": manifest.get(
                "blocker_opt_in_required_actions_by_id"
            ),
            "objective_blocker_required_to_close_by_id": manifest.get(
                "objective_blocker_required_to_close_by_id"
            ),
            "objective_blocker_safe_next_actions_by_id": manifest.get(
                "objective_blocker_safe_next_actions_by_id"
            ),
            "objective_blocker_opt_in_required_actions_by_id": manifest.get(
                "objective_blocker_opt_in_required_actions_by_id"
            ),
            "generic_blocker_aliases_match_objective": (
                manifest.get("blocker_required_to_close_by_id")
                == manifest.get("objective_blocker_required_to_close_by_id")
                == objective_completion.get("blocker_required_to_close_by_id")
                and manifest.get("blocker_safe_next_actions_by_id")
                == manifest.get("objective_blocker_safe_next_actions_by_id")
                == objective_completion.get("blocker_safe_next_actions_by_id")
                and manifest.get("blocker_opt_in_required_actions_by_id")
                == manifest.get("objective_blocker_opt_in_required_actions_by_id")
                == objective_completion.get("blocker_opt_in_required_actions_by_id")
            ),
            "manifest_boundary_matches_archive_gap": manifest_boundary_matches_archive_gap,
            "source_policy_execution_allowed_now": manifest_action_boundary.get(
                "source_policy_execution_allowed_now"
            ),
            "source_policy_execution_invoked": manifest.get(
                "full_source_policy_runner_archive_gap_source_policy_execution_invoked"
            ),
            "exact_b4_opt_in_required_for_execution": manifest_action_boundary.get(
                "exact_b4_opt_in_required_for_execution"
            ),
            "safe_without_b4_opt_in_count": manifest_action_boundary.get("safe_without_b4_opt_in_count"),
            "opt_in_required_action_count": manifest_action_boundary.get("opt_in_required_action_count"),
            "opt_in_required_command_count": manifest_action_boundary.get("opt_in_required_command_count"),
            "opt_in_required_mapped_external_rows": manifest_action_boundary.get(
                "opt_in_required_mapped_external_rows"
            ),
            "oc6_reopen_latest_external_probe": manifest_oc6_probe["marker"],
            "oc6_reopen_latest_external_probe_date": manifest_oc6_probe["date"],
            "oc6_reopen_latest_external_probe_count": manifest_oc6_probe["count"],
            "oc6_reopen_latest_external_probe_positive_artifact_rows": manifest_oc6_probe[
                "positive_artifact_rows"
            ],
            "oc6_reopen_latest_external_probe_source_policy_rows_closed": manifest_oc6_probe[
                "source_policy_rows_closed"
            ],
            "oc6_reopen_latest_external_probe_access_limited_count": manifest_oc6_probe[
                "access_limited_count"
            ],
            "oc6_reopen_latest_external_probe_global_absence_proved": manifest_oc6_probe[
                "global_absence_proved"
            ],
            "oc6_reopen_latest_external_probe_reopen_triggered": manifest_oc6_probe["reopen_triggered"],
            "oc6_reopen_latest_external_probe_matches_archive_gap": manifest_oc6_probe_matches_archive_gap,
            "archive_gap_oc6_reopen_latest_external_probe": oc6_probe["marker"],
        },
        "claim_boundary": {
            "local_citation_key_integrity_closed": local_integrity_passed,
            "bibliographic_metadata_web_verified": reference_web_verified,
            "submission_integrity_gate_closed": integrity_gate_closed,
            "manifest_full_source_policy_boundary_checked": manifest_boundary_matches_archive_gap,
            "oc6_latest_external_probe_checked": oc6_probe["top_level_matches_nested"],
            "reason_open": None
            if integrity_gate_closed
            else "ARS-style 100% external reference metadata verification has not been performed in this local audit.",
        },
        "forbidden_claims": [
            "submission_ready_true",
            *(
                []
                if integrity_gate_closed
                else [
                    "external_reference_web_verification_complete_true",
                    "bibliographic_metadata_verified_true",
                    "submission_integrity_gate_closed_true",
                ]
            ),
        ],
    }

    with OUT_JSON.open("w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, sort_keys=True)
        handle.write("\n")

    lines = [
        "# CMAME Submission Integrity Audit",
        "",
        "Status: **SUBMISSION INTEGRITY PASSED FOR LOCAL CITATIONS, SIDECARS, AND EXTERNAL REFERENCE METADATA**."
        if integrity_gate_closed
        else "Status: **LOCAL CITATION/SIDECAR INTEGRITY PASSED; EXTERNAL REFERENCE WEB VERIFICATION OPEN**."
        if local_integrity_passed
        else "Status: **LOCAL SUBMISSION INTEGRITY FAILED**.",
        "",
        "This read-only audit checks local citation integrity, journal sidecars,",
        "and the reference-metadata audit. It does not mark the whole paper",
        "submission ready because source-policy, proof, prose, and minimal-code",
        "gates are checked separately.",
        "",
        "## Citation-Key Integrity",
        "",
        f"- Main citation groups: `{result['citation_key_integrity']['main_citation_group_count']}`.",
        f"- Main cited keys / bibitems: `{len(main_cites)}/{len(main_bibs)}`.",
        f"- Flat cited keys / bibitems: `{len(flat_cites)}/{len(flat_bibs)}`.",
        f"- Main dangling citation keys: `{', '.join(main_dangling) if main_dangling else 'none'}`.",
        f"- Main orphan bibitems: `{', '.join(main_orphans) if main_orphans else 'none'}`.",
        f"- Flat dangling citation keys: `{', '.join(flat_dangling) if flat_dangling else 'none'}`.",
        f"- Flat orphan bibitems: `{', '.join(flat_orphans) if flat_orphans else 'none'}`.",
        f"- Main/flat citation keys match: `{main_cites == flat_cites}`.",
        f"- Main/flat bibitem keys match: `{main_bibs == flat_bibs}`.",
        f"- Unresolved citation/reference log lines: `{len(main_unresolved)}/{len(flat_unresolved)}`.",
        "",
        "## Submission Sidecars",
        "",
        f"- Declaration tokens present main/flat: `{sidecars['declaration_tokens_present']}/{sidecars['flat_declaration_tokens_present']}`.",
        f"- Highlight count main/flat: `{sidecars['highlight_count']}/{sidecars['flat_highlight_count']}`.",
        f"- Cover letter mentions journal/PDF: `{sidecars['cover_letter_mentions_journal']}/{sidecars['cover_letter_mentions_recommended_pdf']}`.",
        "",
        "## Submission Manifest Boundary",
        "",
        f"- Manifest schema: `{manifest.get('schema', 'missing')}`.",
        f"- Full source-policy archive boundary matches archive gap audit: `{manifest_boundary_matches_archive_gap}`.",
        f"- Manifest safe/opt-in action counts: `{manifest_action_boundary.get('safe_without_b4_opt_in_count')}/{manifest_action_boundary.get('opt_in_required_action_count')}`.",
        f"- Manifest source-policy execution allowed now / invoked / exact opt-in required: `{manifest_action_boundary.get('source_policy_execution_allowed_now')}/{manifest.get('full_source_policy_runner_archive_gap_source_policy_execution_invoked')}/{manifest_action_boundary.get('exact_b4_opt_in_required_for_execution')}`.",
        f"- Manifest opt-in commands/mapped rows: `{manifest_action_boundary.get('opt_in_required_command_count')}/{manifest_action_boundary.get('opt_in_required_mapped_external_rows')}`.",
        f"- Manifest safe action ids: `{','.join(manifest.get('full_source_policy_runner_archive_gap_safe_action_ids', []))}`.",
        f"- Manifest opt-in action ids: `{','.join(manifest.get('full_source_policy_runner_archive_gap_opt_in_action_ids', []))}`.",
        f"- Manifest narrowed archive boundary/status/source-policy/use/execution/exact: `{manifest.get('narrowed_archive_boundary_status')}/{manifest.get('narrowed_archive_boundary_source_policy_closed_ratio')}/{manifest.get('narrowed_archive_boundary_current_archive_usable_as_full_source_policy_runner_archive')}/{manifest.get('narrowed_archive_boundary_source_policy_execution_allowed_now')}/{manifest.get('narrowed_archive_boundary_exact_b4_opt_in_required_for_execution')}`.",
        f"- Manifest narrowed archive boundary matches reproducibility manifest: `{manifest_narrowed_boundary_matches_reproducibility}`.",
        f"- Manifest narrowed archive safe/opt-in action ids: `{','.join(manifest.get('narrowed_archive_boundary_safe_action_ids', []))}` / `{','.join(manifest.get('narrowed_archive_boundary_opt_in_action_ids', []))}`.",
        f"- Manifest narrowed archive required approval/driver: `{result['required_user_approval_statement']}/{result['guarded_execution_driver']}`.",
        f"- Top-level OC12 archive action boundary safe/opt-in/allowed/invoked/exact/commands/rows: `{manifest_action_boundary.get('safe_without_b4_opt_in_count')}/{manifest_action_boundary.get('opt_in_required_action_count')}/{manifest_action_boundary.get('source_policy_execution_allowed_now')}/{manifest.get('full_source_policy_runner_archive_gap_source_policy_execution_invoked')}/{manifest_action_boundary.get('exact_b4_opt_in_required_for_execution')}/{manifest_action_boundary.get('opt_in_required_command_count')}/{manifest_action_boundary.get('opt_in_required_mapped_external_rows')}`.",
        f"- Top-level OC12 archive safe/opt-in action ids: `{','.join(result['oc12_archive_safe_action_ids'])}` / `{','.join(result['oc12_archive_opt_in_action_ids'])}`.",
        f"- Submission manifest generic blocker aliases match objective: `{result['submission_manifest_boundary']['generic_blocker_aliases_match_objective']}`.",
        f"- Objective blocker status by id: `{objective_blocker_status_by_id}`.",
        f"- Objective blocker next actions by id: `{objective_blocker_next_actions_by_id}`.",
        f"- Objective blocker required-to-close by id: `{objective_blocker_required_to_close_by_id}`.",
        f"- Objective blocker safe next actions by id: `{objective_blocker_safe_next_actions_by_id}`.",
        f"- Objective blocker opt-in required actions by id: `{objective_blocker_opt_in_required_actions_by_id}`.",
        f"- OC6 reopen latest external probe carried by full-archive gap: `{oc6_probe['marker']}`.",
        f"- OC6 reopen latest external probe nested/top-level match: `{oc6_probe['top_level_matches_nested']}`.",
        "",
        "## Integrity Boundary",
        "",
        f"- Reference metadata audit: `{reference_audit.get('status', 'missing')}`.",
        f"- DOI metadata verified: `{reference_audit.get('doi_metadata_verified_count', 0)}/{reference_audit.get('doi_reference_count', 0)}`.",
        f"- Non-DOI metadata verified: `{reference_audit.get('non_doi_metadata_verified_count', 0)}/{reference_audit.get('local_non_doi_reference_count', 0)}`.",
        f"- Non-DOI references still open: `{reference_audit.get('non_doi_reference_count', 0)}`.",
        f"- External reference web verification complete: `{reference_web_verified}`.",
        f"- Submission integrity gate closed: `{integrity_gate_closed}`.",
        "- Whole-paper submission ready: `False`.",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("cmame_submission_integrity_audit=written")
    print(f"local_integrity_passed={local_integrity_passed}")
    print(f"main_cited_key_count={len(main_cites)}")
    print(f"main_bibitem_count={len(main_bibs)}")
    print(f"non_doi_metadata_verified={reference_audit.get('non_doi_metadata_verified_count', 0)}/{reference_audit.get('local_non_doi_reference_count', 0)}")
    print(f"non_doi_reference_count={reference_audit.get('non_doi_reference_count', 0)}")
    print(f"external_reference_web_verification_complete={reference_web_verified}")
    print(f"manifest_boundary_matches_archive_gap={manifest_boundary_matches_archive_gap}")
    print(f"oc6_reopen_latest_external_probe={oc6_probe['marker']}")


if __name__ == "__main__":
    main()
