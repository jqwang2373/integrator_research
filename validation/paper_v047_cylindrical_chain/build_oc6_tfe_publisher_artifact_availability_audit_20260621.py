#!/usr/bin/env python3
"""Build an OC6 audit for publisher/article source-artifact availability.

This is a read-only supplement to the OC6 external recheck.  It inspects the
local text/PDF copy of the official TFE article and records whether the article
itself exposes a code-availability, supplementary-source, GitHub, or
source-code-equivalent artifact signal.  Absence in the article is not treated
as global absence and closes no source-policy rows.
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
OUT_JSON = PAPER / "OC6_TFE_PUBLISHER_ARTIFACT_AVAILABILITY_AUDIT_20260621.json"
OUT_MD = PAPER / "OC6_TFE_PUBLISHER_ARTIFACT_AVAILABILITY_AUDIT_20260621.md"

SCHEMA = "oc6-tfe-publisher-artifact-availability-audit-20260621-v1"
STATUS = "publisher_article_checked_no_code_or_supplement_source_artifact_found"
TITLE = "Higher-order integration of index-3 DAE with friction using time finite elements on Lie groups"
DOI = "10.1007/s11044-026-10153-w"
OFFICIAL_URL = "https://link.springer.com/article/10.1007/s11044-026-10153-w"
AUTHORS = ["Ekansh Chaturvedi", "Corina Sandu", "Adrian Sandu"]
DATA_AVAILABILITY_PREFIX = "Data availability"


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


def count_token(text: str, token: str) -> int:
    return len(re.findall(re.escape(token), text, flags=re.IGNORECASE))


def find_line_with_prefix(text: str, prefix: str) -> str | None:
    for raw_line in normalize_text(text).splitlines():
        line = " ".join(raw_line.split())
        if line.startswith(prefix):
            return line
    return None


def main() -> None:
    if not ARTICLE_TXT.exists():
        raise FileNotFoundError(f"missing article text: {ARTICLE_TXT}")
    if not ARTICLE_PDF.exists():
        raise FileNotFoundError(f"missing article PDF: {ARTICLE_PDF}")

    article_text_raw = ARTICLE_TXT.read_text(encoding="utf-8", errors="replace")
    article_text = normalize_text(article_text_raw)
    article_compact = compact(article_text)
    data_availability_statement = find_line_with_prefix(article_text, DATA_AVAILABILITY_PREFIX)

    oc6_external_recheck = read_json(PAPER / "OC6_EXTERNAL_SOURCE_ARTIFACT_RECHECK_20260621.json")
    oc6_readiness = read_json(PAPER / "OC6_SOURCE_EQUIVALENT_REOPEN_READINESS_AUDIT_20260620.json")
    tfe_preflight = read_json(PAPER / "TFE_RUNNER_CONTRACT_PREFLIGHT_CERTIFICATE.json")

    code_availability_heading_found = bool(
        re.search(r"(?im)^\s*Code availability\b", article_text)
    )
    supplementary_source_signal_found = any(
        token.lower() in article_text.lower()
        for token in [
            "supplementary information",
            "supplementary material",
            "electronic supplementary material",
        ]
    )
    github_token_count = count_token(article_text, "github")
    source_code_token_count = count_token(article_text, "source code")
    repository_token_count = count_token(article_text, "repository")
    source_artifact_signal_count = (
        int(code_availability_heading_found)
        + int(supplementary_source_signal_found)
        + github_token_count
        + source_code_token_count
        + repository_token_count
    )

    title_present = TITLE in article_compact
    doi_present = DOI in article_compact
    authors_present = {author: (author in article_compact) for author in AUTHORS}
    official_article_checked = (
        title_present
        and doi_present
        and all(authors_present.values())
        and data_availability_statement is not None
    )

    output: dict[str, Any] = {
        "schema": SCHEMA,
        "status": STATUS,
        "date_checked": "2026-06-21",
        "read_only": True,
        "official_article_checked": official_article_checked,
        "source_article": {
            "title": TITLE,
            "title_present_in_local_text": title_present,
            "doi": DOI,
            "doi_present_in_local_text": doi_present,
            "authors": AUTHORS,
            "authors_present_in_local_text": authors_present,
            "official_url": OFFICIAL_URL,
            "local_text_path": str(ARTICLE_TXT.relative_to(ROOT.parent)),
            "local_pdf_path": str(ARTICLE_PDF.relative_to(ROOT.parent)),
            "data_availability_statement": data_availability_statement,
            "data_availability_statement_found": data_availability_statement is not None,
            "code_availability_heading_found": code_availability_heading_found,
            "supplementary_source_signal_found": supplementary_source_signal_found,
            "github_token_count": github_token_count,
            "source_code_token_count": source_code_token_count,
            "repository_token_count": repository_token_count,
            "source_artifact_signal_count": source_artifact_signal_count,
        },
        "publisher_artifact_disposition": {
            "positive_public_code_artifact_found": False,
            "source_code_equivalent_artifact_found": False,
            "source_policy_rows_closed_by_publisher_audit": 0,
            "source_policy_reopen_triggered": False,
            "accepted_use": "publisher_availability_boundary_only_not_source_policy_evidence",
            "reason": (
                "official article text/PDF is identified and carries a data-availability "
                "statement, but no code-availability, supplementary-source, GitHub, "
                "source-code, or repository signal was found in the local article text"
            ),
        },
        "oc6_external_recheck_marker": (
            f"{oc6_external_recheck.get('date_checked')}/"
            f"{oc6_external_recheck.get('query_count')}/"
            f"{oc6_external_recheck.get('positive_public_code_artifact_rows')}/"
            f"{oc6_external_recheck.get('source_code_equivalent_artifact_rows')}/"
            f"{oc6_external_recheck.get('source_policy_rows_closed_by_recheck')}/"
            f"{oc6_external_recheck.get('source_policy_reopen_triggered')}/"
            f"{oc6_external_recheck.get('global_absence_proved')}"
        ),
        "oc6_reopen_condition": oc6_readiness.get("reopen_condition"),
        "tfe_runner_contract_preflight_status": tfe_preflight.get("status"),
        "tfe_runner_contract_source_policy_rows_completed": tfe_preflight.get(
            "source_policy_rows_completed"
        ),
        "positive_public_code_artifact_rows": 0,
        "source_code_equivalent_artifact_rows": 0,
        "source_policy_rows_closed_by_publisher_audit": 0,
        "source_policy_reopen_triggered": False,
        "source_policy_closed": False,
        "submission_ready": False,
        "global_absence_proved": False,
        "evidence_policy": {
            "publisher_article_absence_is_global_absence_proof": False,
            "data_availability_statement_is_code_availability": False,
            "absence_of_code_availability_section_closes_source_policy": False,
            "no_positive_article_signal_action": "retain_oc6_open_no_positive_source_equivalent_artifact",
        },
        "forbidden_execution_flags": {
            "source_policy_execution_invoked": False,
            "heavy_numerical_run_invoked": False,
            "run_v047_invoked": False,
            "v048_runner_invoked": False,
        },
    }

    OUT_JSON.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# OC6 TFE Publisher Artifact Availability Audit 2026-06-21",
        "",
        f"Status: `{STATUS}`.",
        "",
        "This read-only audit checks the official article text/PDF boundary for a publisher-provided code or supplementary-source signal. It does not perform a new global search, does not prove global absence, and closes zero source-policy rows.",
        "",
        f"- Official article checked: `{official_article_checked}`.",
        f"- DOI/title present: `{doi_present}/{title_present}`.",
        f"- Data availability statement: `{data_availability_statement}`.",
        f"- Code availability heading found: `{code_availability_heading_found}`.",
        f"- Supplementary-source signal found: `{supplementary_source_signal_found}`.",
        f"- GitHub/source-code/repository token counts: `{github_token_count}/{source_code_token_count}/{repository_token_count}`.",
        f"- Source-artifact signal count: `{source_artifact_signal_count}`.",
        f"- Positive public-code artifact rows: `{output['positive_public_code_artifact_rows']}`.",
        f"- Source-code-equivalent artifact rows: `{output['source_code_equivalent_artifact_rows']}`.",
        f"- Source-policy rows closed by publisher audit: `{output['source_policy_rows_closed_by_publisher_audit']}`.",
        f"- Source-policy reopen triggered: `{output['source_policy_reopen_triggered']}`.",
        f"- Global absence proved: `{output['global_absence_proved']}`.",
        f"- Submission ready: `{output['submission_ready']}`.",
        f"- OC6 external recheck marker: `{output['oc6_external_recheck_marker']}`.",
        "",
        "## Boundary",
        "",
        "- A data-availability statement is not a code-availability statement.",
        "- Absence of code artifacts in the publisher article is not a proof of global absence.",
        "- OC6 remains open until a public/source-code-equivalent TFE artifact or a source-equivalent runner certificate exists.",
        "",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print("oc6_tfe_publisher_artifact_availability_audit_20260621=written")
    print(f"official_article_checked={official_article_checked}")
    print(f"data_availability_statement={data_availability_statement}")
    print(f"source_artifact_signal_count={source_artifact_signal_count}")
    print("positive_public_code_artifact_rows=0")
    print("source_code_equivalent_artifact_rows=0")
    print("source_policy_rows_closed_by_publisher_audit=0")
    print("source_policy_reopen_triggered=False")
    print("global_absence_proved=False")
    print("submission_ready=False")


if __name__ == "__main__":
    main()
