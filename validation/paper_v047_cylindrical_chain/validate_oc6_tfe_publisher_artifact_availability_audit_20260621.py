#!/usr/bin/env python3
"""Validate the OC6 TFE publisher artifact availability audit."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
ROOT = PAPER.parent
ARTICLE_STEM = "s11044-026-10153-w"
AUDIT_JSON = PAPER / "OC6_TFE_PUBLISHER_ARTIFACT_AVAILABILITY_AUDIT_20260621.json"
AUDIT_MD = PAPER / "OC6_TFE_PUBLISHER_ARTIFACT_AVAILABILITY_AUDIT_20260621.md"
ARTICLE_TXT = ROOT.parent / "external" / "literature" / f"{ARTICLE_STEM}.txt"
ARTICLE_PDF = ROOT.parent / "external" / "literature" / f"{ARTICLE_STEM}.pdf"
EXPECTED_DATA_AVAILABILITY = "Data availability No datasets were generated or analysed during the current study."


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


def main() -> int:
    checks = Checks()
    try:
        audit = read_json(AUDIT_JSON)
        text = AUDIT_MD.read_text(encoding="utf-8", errors="replace")
        oc6_external_recheck = read_json(PAPER / "OC6_EXTERNAL_SOURCE_ARTIFACT_RECHECK_20260621.json")
        oc6_readiness = read_json(PAPER / "OC6_SOURCE_EQUIVALENT_REOPEN_READINESS_AUDIT_20260620.json")
        tfe_preflight = read_json(PAPER / "TFE_RUNNER_CONTRACT_PREFLIGHT_CERTIFICATE.json")
    except Exception as exc:  # noqa: BLE001
        print(f"OC6 TFE publisher artifact availability audit validation: FAIL\n- {exc}")
        return 1

    article = audit.get("source_article", {})
    disposition = audit.get("publisher_artifact_disposition", {})
    policy = audit.get("evidence_policy", {})
    flags = audit.get("forbidden_execution_flags", {})
    expected_external_marker = (
        f"{oc6_external_recheck.get('date_checked')}/"
        f"{oc6_external_recheck.get('query_count')}/"
        f"{oc6_external_recheck.get('positive_public_code_artifact_rows')}/"
        f"{oc6_external_recheck.get('source_code_equivalent_artifact_rows')}/"
        f"{oc6_external_recheck.get('source_policy_rows_closed_by_recheck')}/"
        f"{oc6_external_recheck.get('source_policy_reopen_triggered')}/"
        f"{oc6_external_recheck.get('global_absence_proved')}"
    )

    checks.check(
        audit.get("schema") == "oc6-tfe-publisher-artifact-availability-audit-20260621-v1",
        "schema changed",
    )
    checks.check(
        audit.get("status") == "publisher_article_checked_no_code_or_supplement_source_artifact_found",
        "status changed",
    )
    checks.check(audit.get("date_checked") == "2026-06-21", "date changed")
    checks.check(audit.get("read_only") is True, "audit must remain read-only")
    checks.check(ARTICLE_TXT.exists(), "article text missing")
    checks.check(ARTICLE_PDF.exists(), "article PDF missing")
    checks.check(audit.get("official_article_checked") is True, "official article not checked")
    checks.check(
        article.get("title") == "Higher-order integration of index-3 DAE with friction using time finite elements on Lie groups",
        "article title changed",
    )
    checks.check(article.get("doi") == "10.1007/s11044-026-10153-w", "DOI changed")
    checks.check(article.get("official_url") == "https://link.springer.com/article/10.1007/s11044-026-10153-w", "official URL changed")
    checks.check(article.get("title_present_in_local_text") is True, "title missing from local text")
    checks.check(article.get("doi_present_in_local_text") is True, "DOI missing from local text")
    checks.check(
        all(article.get("authors_present_in_local_text", {}).get(author) is True for author in [
            "Ekansh Chaturvedi",
            "Corina Sandu",
            "Adrian Sandu",
        ]),
        "authors missing from local text",
    )
    checks.check(
        article.get("data_availability_statement") == EXPECTED_DATA_AVAILABILITY,
        "data availability statement changed",
    )
    checks.check(article.get("data_availability_statement_found") is True, "data availability statement missing")
    checks.check(article.get("code_availability_heading_found") is False, "code availability heading unexpectedly found")
    checks.check(article.get("supplementary_source_signal_found") is False, "supplementary source signal unexpectedly found")
    checks.check(article.get("github_token_count") == 0, "GitHub token count changed")
    checks.check(article.get("source_code_token_count") == 0, "source-code token count changed")
    checks.check(article.get("repository_token_count") == 0, "repository token count changed")
    checks.check(article.get("source_artifact_signal_count") == 0, "source-artifact signal count changed")
    checks.check(disposition.get("positive_public_code_artifact_found") is False, "disposition overclaims public code")
    checks.check(disposition.get("source_code_equivalent_artifact_found") is False, "disposition overclaims source equivalence")
    checks.check(disposition.get("source_policy_rows_closed_by_publisher_audit") == 0, "publisher audit overclosed rows")
    checks.check(disposition.get("source_policy_reopen_triggered") is False, "publisher audit reopened unexpectedly")
    checks.check(
        disposition.get("accepted_use") == "publisher_availability_boundary_only_not_source_policy_evidence",
        "accepted-use boundary changed",
    )
    checks.check(audit.get("positive_public_code_artifact_rows") == 0, "positive artifact rows changed")
    checks.check(audit.get("source_code_equivalent_artifact_rows") == 0, "source-equivalent artifact rows changed")
    checks.check(audit.get("source_policy_rows_closed_by_publisher_audit") == 0, "publisher audit overclosed source-policy rows")
    checks.check(audit.get("source_policy_reopen_triggered") is False, "publisher audit unexpectedly triggered reopen")
    checks.check(audit.get("source_policy_closed") is False, "publisher audit overclosed source policy")
    checks.check(audit.get("submission_ready") is False, "publisher audit overclaimed submission readiness")
    checks.check(audit.get("global_absence_proved") is False, "publisher audit overproved global absence")
    checks.check(audit.get("oc6_external_recheck_marker") == expected_external_marker, "external recheck marker mismatch")
    checks.check(audit.get("oc6_reopen_condition") == oc6_readiness.get("reopen_condition"), "OC6 reopen condition mismatch")
    checks.check(
        audit.get("tfe_runner_contract_preflight_status") == tfe_preflight.get("status"),
        "TFE preflight status mismatch",
    )
    checks.check(
        audit.get("tfe_runner_contract_source_policy_rows_completed") == 0,
        "TFE preflight source-policy row count changed",
    )
    checks.check(policy.get("publisher_article_absence_is_global_absence_proof") is False, "publisher absence overclaimed")
    checks.check(policy.get("data_availability_statement_is_code_availability") is False, "data availability overclaimed as code")
    checks.check(policy.get("absence_of_code_availability_section_closes_source_policy") is False, "code-availability absence overclosed source policy")
    for key in [
        "source_policy_execution_invoked",
        "heavy_numerical_run_invoked",
        "run_v047_invoked",
        "v048_runner_invoked",
    ]:
        checks.check(flags.get(key) is False, f"{key} changed")

    for token in [
        "Status: `publisher_article_checked_no_code_or_supplement_source_artifact_found`.",
        "Official article checked: `True`.",
        f"Data availability statement: `{EXPECTED_DATA_AVAILABILITY}`.",
        "Code availability heading found: `False`.",
        "Supplementary-source signal found: `False`.",
        "GitHub/source-code/repository token counts: `0/0/0`.",
        "Source-artifact signal count: `0`.",
        "Source-code-equivalent artifact rows: `0`.",
        "Source-policy rows closed by publisher audit: `0`.",
        "Global absence proved: `False`.",
    ]:
        checks.check(token in text, f"markdown missing token: {token}")

    if checks.errors:
        print("OC6 TFE publisher artifact availability audit validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("OC6 TFE publisher artifact availability audit validation: PASS")
    print("official_article_checked=True")
    print(f"data_availability_statement={EXPECTED_DATA_AVAILABILITY}")
    print("source_artifact_signal_count=0")
    print("positive_public_code_artifact_rows=0")
    print("source_code_equivalent_artifact_rows=0")
    print("source_policy_rows_closed_by_publisher_audit=0")
    print("source_policy_reopen_triggered=False")
    print("global_absence_proved=False")
    print("submission_ready=False")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
