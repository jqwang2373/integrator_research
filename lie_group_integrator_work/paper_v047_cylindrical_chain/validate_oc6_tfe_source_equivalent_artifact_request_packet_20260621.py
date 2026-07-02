#!/usr/bin/env python3
"""Validate the OC6 source-equivalent artifact request packet."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
ROOT = PAPER.parent
ARTICLE_STEM = "s11044-026-10153-w"
PACKET_JSON = PAPER / "OC6_TFE_SOURCE_EQUIVALENT_ARTIFACT_REQUEST_PACKET_20260621.json"
PACKET_MD = PAPER / "OC6_TFE_SOURCE_EQUIVALENT_ARTIFACT_REQUEST_PACKET_20260621.md"
ARTICLE_TXT = ROOT.parent / f"{ARTICLE_STEM}.txt"
ARTICLE_PDF = ROOT.parent / f"{ARTICLE_STEM}.pdf"
EXPECTED_STATUS = "request_packet_ready_not_sent_no_source_policy_closure"
EXPECTED_EMAILS = ["ekanshchat96@vt.edu", "csandu@vt.edu", "sandu@cs.vt.edu"]


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


def main() -> int:
    checks = Checks()
    try:
        packet = read_json(PACKET_JSON)
        text = PACKET_MD.read_text(encoding="utf-8", errors="replace")
        oc6_external_recheck = read_json(PAPER / "OC6_EXTERNAL_SOURCE_ARTIFACT_RECHECK_20260621.json")
        oc6_publisher_availability = read_json(
            PAPER / "OC6_TFE_PUBLISHER_ARTIFACT_AVAILABILITY_AUDIT_20260621.json"
        )
        tfe_runner_preflight = read_json(PAPER / "TFE_RUNNER_CONTRACT_PREFLIGHT_CERTIFICATE.json")
    except Exception as exc:  # noqa: BLE001
        print(f"OC6 TFE source-equivalent artifact request packet validation: FAIL\n- {exc}")
        return 1

    source_article = packet.get("source_article", {})
    not_closing = packet.get("not_closing", {})
    flags = packet.get("forbidden_execution_flags", {})
    requested_artifacts = packet.get("requested_artifacts", [])
    acceptance_ids = {
        item.get("id") for item in packet.get("acceptance_criteria", []) if isinstance(item, dict)
    }
    expected_tfe_preflight_marker = (
        f"{tfe_runner_preflight.get('status')}/"
        f"{tfe_runner_preflight.get('callable_contract_count')}/"
        f"{tfe_runner_preflight.get('entrypoint_count')}/"
        f"{tfe_runner_preflight.get('candidate_backed_contract_count')}/"
        f"{tfe_runner_preflight.get('source_policy_rows_completed')}/"
        f"{tfe_runner_preflight.get('source_policy_execution_block_count')}"
    )

    checks.check(
        packet.get("schema") == "oc6-tfe-source-equivalent-artifact-request-packet-20260621-v1",
        "schema changed",
    )
    checks.check(packet.get("status") == EXPECTED_STATUS, "status changed")
    checks.check(packet.get("date_prepared") == "2026-06-21", "date changed")
    checks.check(packet.get("read_only") is True, "packet must remain read-only")
    checks.check(packet.get("request_ready") is True, "request should remain ready")
    checks.check(packet.get("request_sent") is False, "packet must not claim sent request")
    checks.check(packet.get("request_delivery_attempted") is False, "packet must not claim delivery")
    checks.check(ARTICLE_TXT.exists(), "article text missing")
    checks.check(ARTICLE_PDF.exists(), "article PDF missing")
    checks.check(packet.get("official_article_checked") is True, "official article not checked")
    checks.check(source_article.get("doi") == "10.1007/s11044-026-10153-w", "DOI changed")
    checks.check(
        source_article.get("title")
        == "Higher-order integration of index-3 DAE with friction using time finite elements on Lie groups",
        "title changed",
    )
    checks.check(
        source_article.get("official_url") == "https://link.springer.com/article/10.1007/s11044-026-10153-w",
        "official URL changed",
    )
    checks.check(
        source_article.get("corresponding_author_email") == "ekanshchat96@vt.edu",
        "corresponding author email changed",
    )
    for email in EXPECTED_EMAILS:
        checks.check(email in source_article.get("author_contact_emails", []), f"missing email {email}")
        checks.check(
            source_article.get("expected_contact_emails_present", {}).get(email) is True,
            f"email presence flag missing for {email}",
        )
    checks.check(packet.get("requested_artifact_count") == 7, "requested artifact count changed")
    checks.check(len(requested_artifacts) == 7, "requested artifacts list count changed")
    for artifact_id in [
        "absolute_coordinate_T10_pendulum_dae_runner",
        "tfe_newmark_trapezoidal_method_runners",
        "brown_mcphee_friction_law_details",
        "full_T10_endpoint_and_sampling_policy",
        "source_reference_policy_and_h_1e_minus_4_binding",
        "work_precision_row_table_binding",
        "license_permission_or_public_archive_identity",
    ]:
        checks.check(
            any(item.get("id") == artifact_id for item in requested_artifacts if isinstance(item, dict)),
            f"missing requested artifact {artifact_id}",
        )
    checks.check(
        {
            "source_code_equivalent_required",
            "formula_only_not_sufficient",
            "pseudocode_only_not_sufficient",
            "candidate_only_not_sufficient",
            "local_proxy_not_sufficient",
            "validator_promotion_required",
        }.issubset(acceptance_ids),
        "acceptance criteria lost non-equivalence rejection policy",
    )
    checks.check("This message has not been sent by the audit script." in packet.get("request_packet_message", ""), "message lost not-sent sentence")
    checks.check(
        not_closing.get("source_policy_rows_closed_by_packet") == 0
        and not_closing.get("source_policy_rows_closed") == 0
        and not_closing.get("source_policy_closed") is False
        and not_closing.get("tfe_runner_closed") is False
        and not_closing.get("source_policy_reopen_triggered") is False
        and not_closing.get("global_absence_proved") is False
        and not_closing.get("submission_ready") is False,
        "packet overclaimed closure, reopen, global absence, or submission readiness",
    )
    checks.check(
        packet.get("oc6_external_recheck_marker") == marker_for_external_recheck(oc6_external_recheck),
        "external recheck marker mismatch",
    )
    checks.check(
        packet.get("oc6_publisher_artifact_availability_marker")
        == marker_for_publisher(oc6_publisher_availability),
        "publisher availability marker mismatch",
    )
    checks.check(
        packet.get("tfe_runner_contract_preflight_marker") == expected_tfe_preflight_marker,
        "TFE runner preflight marker mismatch",
    )
    for key in [
        "source_policy_execution_invoked",
        "heavy_numerical_run_invoked",
        "run_v047_invoked",
        "v048_runner_invoked",
    ]:
        checks.check(flags.get(key) is False, f"{key} changed")

    for token in [
        f"Status: `{EXPECTED_STATUS}`.",
        "Request ready: `True`.",
        "Request sent: `False`.",
        "Corresponding author email: `ekanshchat96@vt.edu`.",
        "Requested artifact count: `7`.",
        "Source-policy rows closed by packet: `0`.",
        "Source-policy reopen triggered: `False`.",
        "Global absence proved: `False`.",
        "Submission ready: `False`.",
        "Formula-only, pseudocode-only, local candidate-only, or proxy implementations do not close OC6.",
    ]:
        checks.check(token in text, f"markdown missing token: {token}")

    if checks.errors:
        print("OC6 TFE source-equivalent artifact request packet validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("OC6 TFE source-equivalent artifact request packet validation: PASS")
    print(f"status={EXPECTED_STATUS}")
    print("request_ready=True")
    print("request_sent=False")
    print("corresponding_author_email=ekanshchat96@vt.edu")
    print("author_contact_email_count=3")
    print("requested_artifact_count=7")
    print("source_policy_rows_closed_by_packet=0")
    print("source_policy_reopen_triggered=False")
    print("global_absence_proved=False")
    print("submission_ready=False")
    print("oc6_tfe_source_equivalent_artifact_request_packet_20260621=ready_not_sent/7/0/False/False")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
