#!/usr/bin/env python3
"""Build an OC6 source-equivalent artifact request packet.

The packet is a read-only handoff artifact. It records the exact
source-equivalent materials that would be needed from the authors or another
public artifact before the OC6 TFE source-policy rows can be reconsidered. It
does not send email, does not prove global absence, and closes no rows.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
ROOT = PAPER.parent
ARTICLE_STEM = "s11044-026-10153-w"
ARTICLE_TXT = ROOT.parent / "external" / "literature" / f"{ARTICLE_STEM}.txt"
ARTICLE_PDF = ROOT.parent / "external" / "literature" / f"{ARTICLE_STEM}.pdf"
OUT_JSON = PAPER / "OC6_TFE_SOURCE_EQUIVALENT_ARTIFACT_REQUEST_PACKET_20260621.json"
OUT_MD = PAPER / "OC6_TFE_SOURCE_EQUIVALENT_ARTIFACT_REQUEST_PACKET_20260621.md"

SCHEMA = "oc6-tfe-source-equivalent-artifact-request-packet-20260621-v1"
STATUS = "request_packet_ready_not_sent_no_source_policy_closure"
TITLE = "Higher-order integration of index-3 DAE with friction using time finite elements on Lie groups"
DOI = "10.1007/s11044-026-10153-w"
OFFICIAL_URL = "https://link.springer.com/article/10.1007/s11044-026-10153-w"
EXPECTED_CONTACT_EMAILS = ["ekanshchat96@vt.edu", "csandu@vt.edu", "sandu@cs.vt.edu"]
CORRESPONDING_AUTHOR_EMAIL = "ekanshchat96@vt.edu"


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def normalize_text(text: str) -> str:
    return (
        text.replace("\ufb00", "ff")
        .replace("\ufb01", "fi")
        .replace("\ufb02", "fl")
        .replace("\ufb03", "ffi")
        .replace("\ufb04", "ffl")
    )


def compact(text: str) -> str:
    return " ".join(normalize_text(text).split())


def marker_for_external_recheck(audit: dict[str, Any]) -> str:
    return (
        f"{audit.get('date_checked')}/"
        f"{audit.get('query_count')}/"
        f"{audit.get('positive_public_code_artifact_rows')}/"
        f"{audit.get('source_code_equivalent_artifact_rows')}/"
        f"{audit.get('source_policy_rows_closed_by_recheck')}/"
        f"{audit.get('source_policy_reopen_triggered')}/"
        f"{audit.get('global_absence_proved')}"
    )


def marker_for_publisher(audit: dict[str, Any]) -> str:
    article = audit.get("source_article", {})
    return (
        f"{audit.get('date_checked')}/"
        f"{audit.get('official_article_checked')}/"
        f"{article.get('source_artifact_signal_count')}/"
        f"{audit.get('positive_public_code_artifact_rows')}/"
        f"{audit.get('source_code_equivalent_artifact_rows')}/"
        f"{audit.get('source_policy_rows_closed_by_publisher_audit')}/"
        f"{audit.get('source_policy_reopen_triggered')}/"
        f"{audit.get('global_absence_proved')}"
    )


def main() -> None:
    if not ARTICLE_TXT.exists():
        raise FileNotFoundError(f"missing article text: {ARTICLE_TXT}")
    if not ARTICLE_PDF.exists():
        raise FileNotFoundError(f"missing article PDF: {ARTICLE_PDF}")

    article_text = normalize_text(ARTICLE_TXT.read_text(encoding="utf-8", errors="replace"))
    article_compact = compact(article_text)
    article_emails = sorted(set(re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+", article_text)))

    oc6_external_recheck = read_json(PAPER / "OC6_EXTERNAL_SOURCE_ARTIFACT_RECHECK_20260621.json")
    oc6_publisher_availability = read_json(
        PAPER / "OC6_TFE_PUBLISHER_ARTIFACT_AVAILABILITY_AUDIT_20260621.json"
    )
    oc6_reopen_readiness = read_json(PAPER / "OC6_SOURCE_EQUIVALENT_REOPEN_READINESS_AUDIT_20260620.json")
    tfe_runner_preflight = read_json(PAPER / "TFE_RUNNER_CONTRACT_PREFLIGHT_CERTIFICATE.json")
    tfe_gap = read_json(PAPER / "TFE_DAE_RUNNER_CONTRACT_GAP_AUDIT.json")
    tfe_source_policy_row_audit = read_json(PAPER / "TFE_SOURCE_POLICY_ROW_AUDIT.json")

    requested_artifacts = [
        {
            "id": "absolute_coordinate_T10_pendulum_dae_runner",
            "request": (
                "Source-code-equivalent absolute-coordinate T=10 pendulum DAE runner "
                "used for the article's index-3 frictional pendulum experiments."
            ),
            "closure_link": "pendulum_absolute_coordinate_source_policy_dae_runner_missing",
        },
        {
            "id": "tfe_newmark_trapezoidal_method_runners",
            "request": (
                "TFE m=1/m=2/m=3, Newmark-beta, and trapezoidal source-policy "
                "method runners with the same state, constraint, and output conventions."
            ),
            "closure_link": "tfe_newmark_trapezoidal_source_policy_method_runners_missing",
        },
        {
            "id": "brown_mcphee_friction_law_details",
            "request": (
                "Brown-McPhee friction law implementation details, including transition "
                "or Stribeck velocity, normal-load coupling, viscous/default policies, "
                "and any branch/tolerance conventions."
            ),
            "closure_link": "brown_mcphee_source_code_equivalent_law_open",
        },
        {
            "id": "full_T10_endpoint_and_sampling_policy",
            "request": (
                "Full T=10 endpoint/output sampling policy for rows whose nominal step "
                "size does not land exactly on the endpoint."
            ),
            "closure_link": "full_T10_source_grid_endpoint_policy_open",
        },
        {
            "id": "source_reference_policy_and_h_1e_minus_4_binding",
            "request": (
                "Reference-solution policy and h=1e-4 binding used for reported error "
                "normalization, including solver tolerances and any accepted reference files."
            ),
            "closure_link": "accepted_source_policy_reference_binding_missing",
        },
        {
            "id": "work_precision_row_table_binding",
            "request": (
                "Work-precision row table binding errors, orders, runtime, Newton "
                "diagnostics, and Jacobian timing to the same source-policy rows."
            ),
            "closure_link": "accepted_source_policy_work_precision_rows_not_executed_or_bound",
        },
        {
            "id": "license_permission_or_public_archive_identity",
            "request": (
                "License/permission statement or a public URL, repository commit, or "
                "archive hash that makes the supplied artifact reviewer-verifiable."
            ),
            "closure_link": "source_equivalent_artifact_identity_and_permission",
        },
    ]
    acceptance_criteria = [
        {
            "id": "source_code_equivalent_required",
            "criterion": (
                "Artifacts must be executable source code or source-code-equivalent "
                "implementation material sufficient to bind the OC6 source-policy rows."
            ),
        },
        {
            "id": "formula_only_not_sufficient",
            "criterion": "Formula-only explanations do not close OC6 source-policy rows.",
        },
        {
            "id": "pseudocode_only_not_sufficient",
            "criterion": "Pseudocode-only descriptions do not close OC6 source-policy rows.",
        },
        {
            "id": "candidate_only_not_sufficient",
            "criterion": (
                "Local candidate runners remain non-equivalent unless the supplied artifact "
                "matches the source-policy contracts and validator promotion rules."
            ),
        },
        {
            "id": "local_proxy_not_sufficient",
            "criterion": "A local proxy implementation is not accepted as publisher/source-equivalent code.",
        },
        {
            "id": "validator_promotion_required",
            "criterion": (
                "Rows close only after the relevant validators promote the evidence; this "
                "request packet itself closes zero rows."
            ),
        },
    ]
    request_packet_message = "\n".join(
        [
            f"Subject: Source-code-equivalent artifacts for {TITLE}",
            "",
            "Dear authors,",
            "",
            (
                "I am preparing a reproducibility audit for the paper "
                f"\"{TITLE}\" (DOI: {DOI}). The publisher article available to me "
                "does not expose a code-availability or supplementary-source artifact."
            ),
            "",
            (
                "Could you share source code, a source-code-equivalent implementation "
                "artifact, or a reviewer-verifiable archive/commit covering the requested "
                "items below? The goal is to bind the reported TFE pendulum rows to the "
                "same DAE runner, method runners, friction law, endpoint policy, reference "
                "solution policy, and work-precision table used in the study."
            ),
            "",
            "Requested items:",
            *[f"- {item['request']}" for item in requested_artifacts],
            "",
            "This message has not been sent by the audit script.",
            "",
            "Best regards,",
        ]
    )

    official_article_checked = (
        TITLE in article_compact
        and DOI in article_compact
        and all(email in article_emails for email in EXPECTED_CONTACT_EMAILS)
        and oc6_publisher_availability.get("official_article_checked") is True
    )
    tfe_preflight_marker = (
        f"{tfe_runner_preflight.get('status')}/"
        f"{tfe_runner_preflight.get('callable_contract_count')}/"
        f"{tfe_runner_preflight.get('entrypoint_count')}/"
        f"{tfe_runner_preflight.get('candidate_backed_contract_count')}/"
        f"{tfe_runner_preflight.get('source_policy_rows_completed')}/"
        f"{tfe_runner_preflight.get('source_policy_execution_block_count')}"
    )
    output: dict[str, Any] = {
        "schema": SCHEMA,
        "status": STATUS,
        "date_prepared": "2026-06-21",
        "read_only": True,
        "request_ready": True,
        "request_sent": False,
        "request_delivery_attempted": False,
        "official_article_checked": official_article_checked,
        "source_article": {
            "title": TITLE,
            "title_present_in_local_text": TITLE in article_compact,
            "doi": DOI,
            "doi_present_in_local_text": DOI in article_compact,
            "official_url": OFFICIAL_URL,
            "local_text_path": str(ARTICLE_TXT.relative_to(ROOT.parent)),
            "local_pdf_path": str(ARTICLE_PDF.relative_to(ROOT.parent)),
            "author_contact_emails": article_emails,
            "expected_contact_emails_present": {
                email: email in article_emails for email in EXPECTED_CONTACT_EMAILS
            },
            "corresponding_author_email": CORRESPONDING_AUTHOR_EMAIL,
        },
        "requested_artifact_count": len(requested_artifacts),
        "requested_artifacts": requested_artifacts,
        "acceptance_criteria": acceptance_criteria,
        "request_packet_message": request_packet_message,
        "source_policy_context": {
            "tfe_source_policy_row_audit_status": tfe_source_policy_row_audit.get("status"),
            "tfe_runner_contract_preflight_status": tfe_runner_preflight.get("status"),
            "tfe_runner_contract_preflight_marker": tfe_preflight_marker,
            "source_policy_execution_blocks": tfe_runner_preflight.get(
                "source_policy_execution_blocks"
            ),
            "candidate_backed_non_equivalent_runner_blocks": tfe_gap.get(
                "candidate_backed_non_equivalent_runner_block_ids"
            ),
            "effective_execution_blocks": tfe_gap.get("source_policy_execution_missing_contract_blocks"),
            "reopen_condition": oc6_reopen_readiness.get("reopen_condition"),
        },
        "not_closing": {
            "source_policy_rows_closed_by_packet": 0,
            "source_policy_rows_closed": 0,
            "source_policy_closed": False,
            "tfe_runner_closed": False,
            "source_policy_reopen_triggered": False,
            "global_absence_proved": False,
            "submission_ready": False,
            "request_packet_is_evidence_only": True,
        },
        "oc6_external_recheck_marker": marker_for_external_recheck(oc6_external_recheck),
        "oc6_publisher_artifact_availability_marker": marker_for_publisher(
            oc6_publisher_availability
        ),
        "tfe_runner_contract_preflight_marker": tfe_preflight_marker,
        "forbidden_execution_flags": {
            "source_policy_execution_invoked": False,
            "heavy_numerical_run_invoked": False,
            "run_v047_invoked": False,
            "v048_runner_invoked": False,
        },
    }

    OUT_JSON.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# OC6 TFE Source-Equivalent Artifact Request Packet 2026-06-21",
        "",
        f"Status: `{STATUS}`.",
        "",
        "This read-only packet prepares a source-equivalent artifact request. It has not been sent and it closes zero source-policy rows.",
        "",
        f"- Request ready: `{output['request_ready']}`.",
        f"- Request sent: `{output['request_sent']}`.",
        f"- Corresponding author email: `{CORRESPONDING_AUTHOR_EMAIL}`.",
        f"- Author contact emails: `{', '.join(article_emails)}`.",
        f"- Requested artifact count: `{len(requested_artifacts)}`.",
        f"- OC6 external recheck marker: `{output['oc6_external_recheck_marker']}`.",
        f"- OC6 publisher availability marker: `{output['oc6_publisher_artifact_availability_marker']}`.",
        f"- TFE runner preflight marker: `{output['tfe_runner_contract_preflight_marker']}`.",
        f"- Source-policy rows closed by packet: `{output['not_closing']['source_policy_rows_closed_by_packet']}`.",
        f"- Source-policy reopen triggered: `{output['not_closing']['source_policy_reopen_triggered']}`.",
        f"- Global absence proved: `{output['not_closing']['global_absence_proved']}`.",
        f"- Submission ready: `{output['not_closing']['submission_ready']}`.",
        "",
        "## Requested Artifacts",
        "",
    ]
    for item in requested_artifacts:
        lines.append(f"- `{item['id']}`: {item['request']}")
    lines.extend(
        [
            "",
            "## Acceptance Boundary",
            "",
            "- Formula-only, pseudocode-only, local candidate-only, or proxy implementations do not close OC6.",
            "- Rows close only after validator promotion of source-equivalent evidence.",
            "- This packet is a request handoff, not source-policy execution evidence.",
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print("oc6_tfe_source_equivalent_artifact_request_packet_20260621=written")
    print(f"status={STATUS}")
    print("request_ready=True")
    print("request_sent=False")
    print(f"corresponding_author_email={CORRESPONDING_AUTHOR_EMAIL}")
    print(f"author_contact_email_count={len(article_emails)}")
    print(f"requested_artifact_count={len(requested_artifacts)}")
    print("source_policy_rows_closed_by_packet=0")
    print("source_policy_reopen_triggered=False")
    print("global_absence_proved=False")
    print("submission_ready=False")


if __name__ == "__main__":
    main()
