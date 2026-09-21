#!/usr/bin/env python3
"""Validate the TFE public-code recheck certificate."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent


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
        cert = read_json(PAPER / "TFE_PUBLIC_CODE_RECHECK_20260613.json")
        text = (PAPER / "TFE_PUBLIC_CODE_RECHECK_20260613.md").read_text(
            encoding="utf-8",
            errors="replace",
        )
        paper_text = (PAPER / "../../external/literature/s11044-026-10153-w.txt").resolve().read_text(
            encoding="utf-8",
            errors="replace",
        )
        tfe_attempt = read_json(PAPER / "TFE_SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_CERTIFICATE.json")
    except Exception as exc:  # noqa: BLE001
        print(f"TFE public-code recheck validation: FAIL\n- {exc}")
        return 1

    coverage = cert.get("coverage", {})
    boundary = cert.get("claim_boundary", {})
    source_paper = cert.get("source_paper", {})
    recheck = cert.get("public_code_recheck", {})
    decision = cert.get("decision", {})

    checks.check(cert.get("schema") == "tfe-public-code-recheck-20260613-v1", "schema changed")
    checks.check(
        cert.get("status")
        == "public_code_rechecked_no_distinct_tfe_code_artifact_attempted_not_reproducible",
        "status changed",
    )
    checks.check(cert.get("date_checked") == "2026-06-13", "date changed")
    checks.check(cert.get("read_only") is True, "certificate must remain read-only")
    checks.check(cert.get("run_v047_invoked") is False, "certificate invoked run_v047")
    checks.check(cert.get("v048_runner_invoked") is False, "certificate invoked v048")
    checks.check(cert.get("suite_id") == "tfe2026_original_pendulum", "suite changed")
    checks.check(cert.get("accepted_for_external_superiority") is False, "overclaims superiority")

    checks.check(
        source_paper.get("title")
        == "Higher-order integration of index-3 DAE with friction using time finite elements on Lie groups",
        "source-paper title changed",
    )
    checks.check(source_paper.get("doi") == "10.1007/s11044-026-10153-w", "source-paper DOI changed")
    checks.check("Higher-order integration of index-3 DAE with friction using" in paper_text, "paper title missing from text")
    checks.check("https://doi.org/10.1007/s11044-026-10153-w" in paper_text, "paper DOI missing from text")
    checks.check("Ekansh Chaturvedi" in paper_text, "paper author missing from text")

    checks.check(coverage.get("github_repository_search_total_count") == 0, "repository hit count changed")
    checks.check(coverage.get("github_repository_search_incomplete_results") is False, "repository search incomplete")
    checks.check(coverage.get("github_user_search_total_count") == 0, "GitHub user hit count changed")
    checks.check(
        coverage.get("github_code_search_api_status") == "requires_authentication",
        "GitHub code-search status changed",
    )
    checks.check(coverage.get("web_search_direct_public_code_hit_count") == 0, "web direct-hit count changed")
    checks.check(coverage.get("direct_public_code_hit_count") == 0, "direct public-code hits changed")
    checks.check(
        coverage.get("paper_spec_candidate_reconstruction_available") is True,
        "paper-spec reconstruction availability changed",
    )
    checks.check(coverage.get("rechecked_external_rows") == 16, "rechecked row count changed")
    checks.check(
        coverage.get("source_policy_rows_attempted_not_reproducible")
        == tfe_attempt.get("attempted_not_reproducible_rows")
        == 16,
        "attempted-not-reproducible row count changed",
    )
    checks.check(coverage.get("source_policy_rows_closed") == 0, "certificate overcloses rows")

    checks.check(boundary.get("distinct_public_tfe_code_artifact_found") is False, "distinct TFE code unexpectedly found")
    checks.check(
        boundary.get("paper_spec_reconstruction_is_source_policy_reproduction") is False,
        "paper-spec reconstruction overpromoted",
    )
    checks.check(boundary.get("external_superiority_claim_allowed") is False, "superiority overclaimed")
    checks.check(boundary.get("source_policy_rows_closed") == 0, "boundary overcloses rows")
    checks.check(boundary.get("source_policy_rows_total") == 16, "boundary row total changed")

    repository_results = recheck.get("github_repository_search_results", [])
    checks.check(len(repository_results) == 6, "repository search query count changed")
    checks.check(
        all(item.get("total_count") == 0 and item.get("incomplete_results") is False for item in repository_results),
        "repository search result changed",
    )
    user_results = recheck.get("github_user_search_results", [])
    checks.check(len(user_results) == 1, "user search query count changed")
    checks.check(user_results[0].get("total_count") == 0, "user search result changed")
    checks.check(len(recheck.get("web_search_queries", [])) == 8, "web-search query count changed")

    checks.check(decision.get("can_close_tfe_source_policy_rows_now") is False, "decision overcloses")
    checks.check(
        decision.get("row_disposition") == "attempted_not_reproducible_not_promoted",
        "row disposition changed",
    )
    checks.check(
        "TFE_SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_CERTIFICATE.json" in cert.get("source_files", []),
        "TFE self-reproduction certificate missing",
    )

    for token in [
        "Status: **public code rechecked; no distinct TFE source-code artifact; attempted not reproducible; not promoted**.",
        "DOI: `10.1007/s11044-026-10153-w`.",
        "GitHub repository search total count: `0`.",
        "GitHub user search total count: `0`.",
        "GitHub code-search API: `requires_authentication`.",
        "Web-search direct public-code hits: `0`.",
        "Paper-spec candidate reconstruction available: `True`.",
        "Source-policy rows attempted-not-reproducible: `16`.",
        "Source-policy rows closed: `0/16`.",
        "External-superiority claim allowed: `False`.",
    ]:
        checks.check(token in text, f"markdown missing token: {token}")

    if checks.errors:
        print("TFE public-code recheck validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("TFE public-code recheck validation: PASS")
    print("github_repository_search_total_count=0")
    print("source_policy_rows_closed=0/16")
    print("attempted_not_reproducible_rows=16")
    return 0


if __name__ == "__main__":
    sys.exit(main())
