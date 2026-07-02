#!/usr/bin/env python3
"""Validate the 2026-06-14 source-policy public-code refresh."""

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
        audit = read_json(PAPER / "SOURCE_POLICY_PUBLIC_CODE_REFRESH_20260614.json")
        text = (PAPER / "SOURCE_POLICY_PUBLIC_CODE_REFRESH_20260614.md").read_text(
            encoding="utf-8",
            errors="replace",
        )
        self_attempt = read_json(PAPER / "SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_AUDIT.json")
    except Exception as exc:  # noqa: BLE001
        print(f"Source-policy public-code refresh validation: FAIL\n- {exc}")
        return 1

    suite_refreshes = [row for row in audit.get("suite_refreshes", []) if isinstance(row, dict)]
    by_suite = {row.get("suite_id"): row for row in suite_refreshes}
    tfe = by_suite.get("tfe2026_original_pendulum", {})
    vp = by_suite.get("vp2024_velocity_partitioning", {})
    vp_tree = vp.get("public_repository_tree_refresh", {}) if isinstance(vp.get("public_repository_tree_refresh"), dict) else {}

    checks.check(audit.get("schema") == "source-policy-public-code-refresh-20260614-v1", "schema changed")
    checks.check(
        audit.get("status")
        == "public_code_refresh_no_new_source_artifact_nonpublic_rows_remain_unable_to_reproduce",
        "status changed",
    )
    checks.check(audit.get("date_checked") == "2026-06-14", "date changed")
    checks.check(audit.get("read_only") is True, "refresh must remain read-only")
    checks.check(audit.get("row_count") == 20, "row count changed")
    checks.check(audit.get("public_code_available_rows") == 0, "refresh found public-code rows unexpectedly")
    checks.check(audit.get("self_reproduction_attempted_rows") == 20, "attempted count changed")
    checks.check(audit.get("unable_to_reproduce_rows") == 20, "unable-to-reproduce count changed")
    checks.check(audit.get("source_policy_rows_closed") == 0, "refresh overcloses source-policy rows")
    checks.check(audit.get("source_policy_rows_promoted") == 0, "refresh overpromotes source-policy rows")
    checks.check(audit.get("external_superiority_ready_rows") == 0, "refresh overclaims external superiority")
    checks.check(audit.get("open_execution_queue_rows") == 0, "refresh should not reopen execution queue")
    checks.check(audit.get("heavy_numerical_run_invoked") is False, "refresh invoked heavy run")
    checks.check(audit.get("run_v047_invoked") is False, "refresh invoked run_v047")
    checks.check(audit.get("v048_runner_invoked") is False, "refresh invoked v048")
    checks.check(
        "SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_AUDIT.json" in audit.get("source_files", []),
        "missing self-reproduction source file",
    )

    policy = audit.get("policy", {})
    checks.check(
        policy.get("public_code_absent_action") == "use_self_reproduction_attempt_evidence",
        "public-code-absent policy changed",
    )
    checks.check(
        policy.get("failed_or_proxy_self_reproduction_action") == "mark_unable_to_reproduce_not_promoted",
        "failed self-reproduction policy changed",
    )
    checks.check(policy.get("not_reproducible_rows_are_source_policy_closed") is False, "policy overcloses")
    checks.check(
        policy.get("not_reproducible_rows_are_external_superiority_ready") is False,
        "policy overclaims",
    )
    checks.check(
        policy.get("rate_limited_query_policy") == "rate_limited_queries_are_not_positive_public_code_evidence",
        "rate-limit policy changed",
    )

    checks.check(tfe.get("row_count") == 16, "TFE row count changed")
    checks.check(tfe.get("prior_public_code_recheck") == "TFE_PUBLIC_CODE_RECHECK_20260613.json", "TFE prior pointer changed")
    checks.check(tfe.get("confirmed_zero_query_count") == 6, "TFE zero-query count changed")
    checks.check(tfe.get("rate_limited_query_count") == 1, "TFE rate-limit count changed")
    checks.check(tfe.get("public_code_available_now") is False, "TFE public code unexpectedly available")
    checks.check(tfe.get("self_reproduction_attempted_rows") == 16, "TFE attempted rows changed")
    checks.check(tfe.get("unable_to_reproduce_rows") == 16, "TFE unable rows changed")
    checks.check(tfe.get("source_policy_rows_closed") == 0, "TFE overclosed")
    checks.check(tfe.get("source_policy_rows_promoted") == 0, "TFE overpromoted")
    checks.check(tfe.get("final_disposition") == "unable_to_reproduce_not_promoted", "TFE disposition changed")

    checks.check(vp.get("row_count") == 4, "VP row count changed")
    checks.check(vp.get("prior_public_code_recheck") == "VP2024_PUBLIC_CODE_RECHECK_20260613.json", "VP prior pointer changed")
    checks.check(vp.get("confirmed_zero_query_count") == 4, "VP zero-query count changed")
    checks.check(vp.get("public_code_available_now") is False, "VP public code unexpectedly available")
    checks.check(vp.get("self_reproduction_attempted_rows") == 4, "VP attempted rows changed")
    checks.check(vp.get("unable_to_reproduce_rows") == 4, "VP unable rows changed")
    checks.check(vp.get("source_policy_rows_closed") == 0, "VP overclosed")
    checks.check(vp.get("source_policy_rows_promoted") == 0, "VP overpromoted")
    checks.check(vp.get("final_disposition") == "unable_to_reproduce_not_promoted", "VP disposition changed")
    checks.check(vp_tree.get("tree_sha") == "cf9884a24a22a5281bacc3d87e67ff06c0911dfc", "VP tree SHA changed")
    checks.check(vp_tree.get("tree_truncated") is False, "VP tree truncated")
    checks.check(vp_tree.get("tree_total_paths") == 4487, "VP path count changed")
    checks.check(vp_tree.get("keyword_path_hit_count") == 0, "VP keyword hits changed")
    checks.check(vp_tree.get("keyword_path_hits") == [], "VP keyword hits not empty")

    checks.check(self_attempt.get("row_count") == 20, "self-reproduction audit row count changed")
    checks.check(self_attempt.get("unable_to_reproduce_rows") == 20, "self-reproduction unable count changed")
    checks.check(self_attempt.get("source_policy_closed_rows") == 0, "self-reproduction overclosed rows")

    for token in [
        "Status: `public_code_refresh_no_new_source_artifact_nonpublic_rows_remain_unable_to_reproduce`.",
        "Rows refreshed: `20`.",
        "Public-code-available rows: `0`.",
        "Self-reproduction attempted rows: `20`.",
        "Unable-to-reproduce rows: `20`.",
        "Source-policy rows closed/promoted: `0/0`.",
        "External-superiority ready rows: `0`.",
        "Open execution-queue rows: `0`.",
        "`tfe2026_original_pendulum`",
        "`vp2024_velocity_partitioning`",
        "Tree SHA: `cf9884a24a22a5281bacc3d87e67ff06c0911dfc`.",
        "Keyword path hits: `0`.",
    ]:
        checks.check(token in text, f"markdown missing token: {token}")

    if checks.errors:
        print("Source-policy public-code refresh validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("Source-policy public-code refresh validation: PASS")
    print("rows=20")
    print("public_code_available_rows=0")
    print("unable_to_reproduce_rows=20")
    print("source_policy_closed=0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
