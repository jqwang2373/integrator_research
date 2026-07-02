#!/usr/bin/env python3
"""Validate the VP2024 public-code recheck certificate."""

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
        cert = read_json(PAPER / "VP2024_PUBLIC_CODE_RECHECK_20260613.json")
        text = (PAPER / "VP2024_PUBLIC_CODE_RECHECK_20260613.md").read_text(
            encoding="utf-8",
            errors="replace",
        )
        vp = read_json(PAPER / "VP2024_CODE_PATH_DISPOSITION_AUDIT.json")
    except Exception as exc:  # noqa: BLE001
        print(f"VP2024 public-code recheck validation: FAIL\n- {exc}")
        return 1

    coverage = cert.get("coverage", {})
    boundary = cert.get("claim_boundary", {})
    repo = cert.get("public_repository_recheck", {})
    decision = cert.get("decision", {})

    checks.check(
        cert.get("schema") == "vp2024-public-code-recheck-20260613-v1",
        "schema changed",
    )
    checks.check(
        cert.get("status")
        == "public_code_rechecked_no_distinct_vp2024_path_attempted_not_reproducible",
        "status changed",
    )
    checks.check(cert.get("date_checked") == "2026-06-13", "date changed")
    checks.check(cert.get("read_only") is True, "certificate must remain read-only")
    checks.check(cert.get("run_v047_invoked") is False, "certificate invoked run_v047")
    checks.check(cert.get("v048_runner_invoked") is False, "certificate invoked v048")
    checks.check(cert.get("suite_id") == "vp2024_velocity_partitioning", "suite changed")
    checks.check(cert.get("accepted_for_external_superiority") is False, "overclaims superiority")

    checks.check(coverage.get("tree_truncated") is False, "tree should be complete")
    checks.check(coverage.get("tree_total_paths") == 4487, "tree path count changed")
    checks.check(coverage.get("year2024_path_count") == 1540, "2024 path count changed")
    checks.check(coverage.get("keyword_path_hit_count") == 0, "keyword hit count changed")
    checks.check(coverage.get("keyword_path_hits") == [], "keyword hits should be empty")
    checks.check(
        coverage.get("github_code_search_api_status") == "requires_authentication",
        "GitHub code-search status changed",
    )
    checks.check(coverage.get("local_proxy_available") is True, "local proxy marker changed")
    checks.check(coverage.get("rechecked_external_rows") == 4, "rechecked row count changed")
    checks.check(
        coverage.get("source_policy_rows_attempted_not_reproducible") == 4,
        "attempted-not-reproducible row count changed",
    )
    checks.check(coverage.get("source_policy_rows_closed") == 0, "certificate overcloses rows")

    checks.check(
        boundary.get("distinct_public_vp2024_code_path_found") is False
        and vp.get("source_code_path_disposition", {}).get("distinct_public_vp_code_path_found") is False,
        "distinct VP path unexpectedly found",
    )
    checks.check(boundary.get("vp_proxy_is_source_policy_reproduction") is False, "proxy overpromoted")
    checks.check(boundary.get("external_superiority_claim_allowed") is False, "superiority overclaimed")
    checks.check(boundary.get("source_policy_rows_closed") == 0, "boundary overcloses rows")
    checks.check(boundary.get("source_policy_rows_total") == 4, "boundary row total changed")

    checks.check(
        repo.get("tree_api_url")
        == "https://api.github.com/repos/uwsbel/sbel-reproducibility/git/trees/master?recursive=1",
        "tree API URL changed",
    )
    checks.check(
        repo.get("contents_2024_api_url")
        == "https://api.github.com/repos/uwsbel/sbel-reproducibility/contents/2024?ref=master",
        "contents API URL changed",
    )
    checks.check(
        repo.get("tree_sha") == "cf9884a24a22a5281bacc3d87e67ff06c0911dfc",
        "tree sha changed",
    )
    checks.check(
        repo.get("contents_2024_paths")
        == [
            "2024/CPD",
            "2024/IROSImuGps",
            "2024/MNODE-code",
            "2024/PathFollowingSim2real",
            "2024/RSSworkshop",
        ],
        "2024 contents changed",
    )
    checks.check(
        repo.get("keyword_regex")
        == "velocity|Velocity|partition|Partition|DETC2023|116950|4065254|Kissel|Bakke|Negrut",
        "keyword regex changed",
    )

    checks.check(decision.get("can_close_vp2024_source_policy_rows_now") is False, "decision overcloses")
    checks.check(
        decision.get("row_disposition") == "attempted_not_reproducible_not_promoted",
        "row disposition changed",
    )
    checks.check(
        "VP2024_CODE_PATH_DISPOSITION_AUDIT.json" in cert.get("source_files", []),
        "source audit missing",
    )

    for token in [
        "Status: **public code rechecked; no distinct VP2024 path; attempted not reproducible; not promoted**.",
        "Tree truncated: `False`.",
        "Total paths: `4487`.",
        "2024 paths: `1540`.",
        "Keyword path hits for `velocity|Velocity|partition|Partition|DETC2023|116950|4065254|Kissel|Bakke|Negrut`: `0`.",
        "GitHub code-search API: `requires_authentication`.",
        "Source-policy rows closed: `0/4`.",
        "External-superiority claim allowed: `False`.",
    ]:
        checks.check(token in text, f"markdown missing token: {token}")

    if checks.errors:
        print("VP2024 public-code recheck validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("VP2024 public-code recheck validation: PASS")
    print("tree_total_paths=4487")
    print("keyword_path_hit_count=0")
    print("source_policy_rows_closed=0/4")
    return 0


if __name__ == "__main__":
    sys.exit(main())
