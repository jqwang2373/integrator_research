#!/usr/bin/env python3
"""Validate the source-policy self-reproduction attempt audit."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
EXPECTED_EXAMPLES = {"single_pendulum", "double_pendulum", "four_link", "slider_crank"}
EXPECTED_TFE_METHODS = {
    "tfe2026_Newmark_beta",
    "tfe2026_TFE_m1",
    "tfe2026_TFE_m2",
    "tfe2026_trapezoidal",
}
EXPECTED_VP_METHODS = {"vp2024_coordinate_partitioning_rA"}


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
        audit = read_json(PAPER / "SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_AUDIT.json")
        tfe_public_code_recheck = read_json(PAPER / "TFE_PUBLIC_CODE_RECHECK_20260613.json")
        vp_recheck = read_json(PAPER / "VP2024_PUBLIC_CODE_RECHECK_20260613.json")
        public_code_refresh = read_json(PAPER / "SOURCE_POLICY_PUBLIC_CODE_REFRESH_20260614.json")
        text = (PAPER / "SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_AUDIT.md").read_text(
            encoding="utf-8",
            errors="replace",
        )
    except Exception as exc:  # noqa: BLE001
        print(f"Source-policy self-reproduction attempt audit validation: FAIL\n- {exc}")
        return 1

    rows = [row for row in audit.get("rows", []) if isinstance(row, dict)]
    tfe_rows = [row for row in rows if row.get("suite_id") == "tfe2026_original_pendulum"]
    vp_rows = [row for row in rows if row.get("suite_id") == "vp2024_velocity_partitioning"]
    tfe_recheck_coverage = tfe_public_code_recheck.get("coverage", {})
    vp_recheck_coverage = vp_recheck.get("coverage", {})

    checks.check(audit.get("schema") == "source-policy-self-reproduction-attempt-audit-v1", "schema changed")
    checks.check(
        audit.get("status") == "nonpublic_code_rows_attempted_not_reproducible_not_promoted",
        "status changed",
    )
    checks.check(audit.get("read_only") is True, "audit must remain read-only")
    checks.check(audit.get("row_count") == len(rows) == 20, "row count changed")
    checks.check(audit.get("total_rows") == 20, "total_rows alias changed")
    checks.check(
        audit.get("suites") == ["tfe2026_original_pendulum", "vp2024_velocity_partitioning"],
        "suite alias changed",
    )
    checks.check(len(tfe_rows) == 16, "TFE attempted row count changed")
    checks.check(len(vp_rows) == 4, "VP attempted row count changed")
    checks.check(audit.get("self_reproduction_attempted_rows") == 20, "attempted count changed")
    checks.check(audit.get("attempted_not_reproducible_rows") == 20, "not-reproducible count changed")
    checks.check(
        audit.get("source_policy_rows_attempted_not_reproducible") == 20,
        "source-policy attempted-not-reproducible alias changed",
    )
    checks.check(audit.get("unable_to_reproduce_rows") == 20, "unable-to-reproduce count changed")
    checks.check(
        audit.get("source_policy_rows_unable_to_reproduce") == 20,
        "source-policy unable-to-reproduce alias changed",
    )
    checks.check(audit.get("source_policy_closed_rows") == 0, "audit overcloses source-policy rows")
    checks.check(audit.get("source_policy_rows_closed") == 0, "source-policy closed alias changed")
    checks.check(audit.get("external_superiority_ready_rows") == 0, "audit overclaims external-superiority rows")
    checks.check(audit.get("open_execution_queue_rows") == 0, "not-reproducible rows should not stay in execution queue")
    checks.check(audit.get("heavy_numerical_run_invoked") is False, "audit invoked heavy run")
    checks.check(audit.get("run_v047_invoked") is False, "audit invoked run_v047")
    checks.check(audit.get("v048_runner_invoked") is False, "audit invoked v048")

    policy = audit.get("policy", {})
    checks.check(
        policy.get("public_code_absent_action") == "attempt_paper_spec_self_reproduction",
        "public-code-absent policy changed",
    )
    checks.check(
        policy.get("under_specified_or_proxy_only_action") == "mark_attempted_not_reproducible",
        "under-specified policy changed",
    )
    checks.check(
        policy.get("failed_self_reproduction_action") == "mark_unable_to_reproduce_not_promoted",
        "failed self-reproduction policy changed",
    )
    checks.check(policy.get("not_reproducible_rows_are_source_policy_closed") is False, "policy overcloses")
    checks.check(policy.get("not_reproducible_rows_are_external_superiority_ready") is False, "policy overclaims")

    checks.check({row.get("example") for row in tfe_rows} == EXPECTED_EXAMPLES, "TFE examples changed")
    checks.check({row.get("method") for row in tfe_rows} == EXPECTED_TFE_METHODS, "TFE methods changed")
    checks.check({row.get("example") for row in vp_rows} == EXPECTED_EXAMPLES, "VP examples changed")
    checks.check({row.get("method") for row in vp_rows} == EXPECTED_VP_METHODS, "VP methods changed")

    for row in rows:
        label = f"{row.get('method')}:{row.get('example')}"
        checks.check(row.get("self_reproduction_attempted") is True, f"{label} not attempted")
        checks.check(
            row.get("source_policy_disposition") == "attempted_not_reproducible",
            f"{label} disposition changed",
        )
        checks.check(row.get("unable_to_reproduce") is True, f"{label} missing unable-to-reproduce marker")
        checks.check(
            row.get("final_nonpublic_code_disposition") == "unable_to_reproduce_not_promoted",
            f"{label} final nonpublic-code disposition changed",
        )
        checks.check(row.get("post_execution_decision") == "attempted_not_reproducible", f"{label} decision changed")
        checks.check(row.get("source_policy_closed") is False, f"{label} overclosed")
        checks.check(row.get("external_superiority_ready") is False, f"{label} overclaims")
        checks.check(row.get("counts_as_open_execution_queue") is False, f"{label} still queued")
        checks.check(row.get("primary_nonreproducibility_reason"), f"{label} missing reason")
        checks.check(row.get("self_reproduction_artifacts"), f"{label} missing artifact list")
    checks.check(
        sum(row.get("candidate_runner_available") is True for row in tfe_rows) == 16,
        "TFE candidate-runner availability changed",
    )
    checks.check(
        "TFE_SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_CERTIFICATE.json" in audit.get("source_files", []),
        "TFE self-reproduction certificate missing from source files",
    )
    checks.check(
        "TFE_PUBLIC_CODE_RECHECK_20260613.json" in audit.get("source_files", []),
        "TFE public-code recheck certificate missing from source files",
    )
    checks.check(
        "VP2024_PUBLIC_CODE_RECHECK_20260613.json" in audit.get("source_files", []),
        "VP public-code recheck certificate missing from source files",
    )
    checks.check(
        "SOURCE_POLICY_PUBLIC_CODE_REFRESH_20260614.json" in audit.get("source_files", []),
        "2026-06-14 public-code refresh missing from source files",
    )
    checks.check(
        public_code_refresh.get("status")
        == "public_code_refresh_no_new_source_artifact_nonpublic_rows_remain_unable_to_reproduce",
        "public-code refresh status changed",
    )
    checks.check(public_code_refresh.get("row_count") == 20, "public-code refresh row count changed")
    checks.check(public_code_refresh.get("unable_to_reproduce_rows") == 20, "public-code refresh unable count changed")
    checks.check(public_code_refresh.get("source_policy_rows_closed") == 0, "public-code refresh overclosed rows")
    for row in tfe_rows:
        label = f"{row.get('method')}:{row.get('example')}"
        checks.check(
            "TFE_SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_CERTIFICATE.json"
            in row.get("self_reproduction_artifacts", []),
            f"{label} missing TFE attempt certificate artifact",
        )
        checks.check(
            "TFE_PUBLIC_CODE_RECHECK_20260613.json" in row.get("self_reproduction_artifacts", []),
            f"{label} missing TFE public-code recheck artifact",
        )
        checks.check(
            "SOURCE_POLICY_PUBLIC_CODE_REFRESH_20260614.json" in row.get("self_reproduction_artifacts", []),
            f"{label} missing 2026-06-14 public-code refresh artifact",
        )
        checks.check(
            row.get("self_reproduction_attempt_certificate")
            == "TFE_SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_CERTIFICATE.json",
            f"{label} missing TFE attempt certificate pointer",
        )
        checks.check(
            row.get("self_reproduction_attempt_certificate_status")
            == "attempted_not_reproducible_not_promoted",
            f"{label} TFE attempt certificate status changed",
        )
        checks.check(
            row.get("self_reproduction_attempt_certificate_rows") == 16,
            f"{label} TFE attempt certificate row count changed",
        )
        checks.check(
            row.get("self_reproduction_attempt_certificate_closed_rows") == 0,
            f"{label} TFE attempt certificate overclosed rows",
        )
        checks.check(
            row.get("public_code_recheck_certificate") == "TFE_PUBLIC_CODE_RECHECK_20260613.json",
            f"{label} missing TFE public-code recheck pointer",
        )
        checks.check(
            row.get("public_code_refresh_certificate") == "SOURCE_POLICY_PUBLIC_CODE_REFRESH_20260614.json",
            f"{label} missing 2026-06-14 public-code refresh pointer",
        )
        checks.check(
            row.get("public_code_recheck_certificate_status")
            == "public_code_rechecked_no_distinct_tfe_code_artifact_attempted_not_reproducible",
            f"{label} TFE public-code recheck status changed",
        )
        checks.check(row.get("public_code_recheck_date") == "2026-06-13", f"{label} TFE recheck date changed")
        checks.check(
            row.get("public_code_recheck_github_repository_search_total_count") == 0,
            f"{label} TFE repository search count changed",
        )
        checks.check(
            row.get("public_code_recheck_github_user_search_total_count") == 0,
            f"{label} TFE user search count changed",
        )
        checks.check(
            row.get("public_code_recheck_github_code_search_api_status") == "requires_authentication",
            f"{label} TFE code-search status changed",
        )
        checks.check(
            row.get("public_code_recheck_source_policy_closed_rows") == 0,
            f"{label} TFE public-code recheck overclosed rows",
        )
        checks.check(
            row.get("public_code_recheck_attempted_not_reproducible_rows") == 16,
            f"{label} TFE public-code recheck attempted rows changed",
        )
    checks.check(
        all(row.get("candidate_runner_source_policy_equivalent") is False for row in rows),
        "candidate runner was incorrectly promoted",
    )
    for row in vp_rows:
        label = f"{row.get('method')}:{row.get('example')}"
        checks.check(
            "VP2024_PUBLIC_CODE_RECHECK_20260613.json" in row.get("self_reproduction_artifacts", []),
            f"{label} missing VP public-code recheck artifact",
        )
        checks.check(
            "SOURCE_POLICY_PUBLIC_CODE_REFRESH_20260614.json" in row.get("self_reproduction_artifacts", []),
            f"{label} missing 2026-06-14 public-code refresh artifact",
        )
        checks.check(
            row.get("public_code_recheck_certificate") == "VP2024_PUBLIC_CODE_RECHECK_20260613.json",
            f"{label} missing VP public-code recheck pointer",
        )
        checks.check(
            row.get("public_code_refresh_certificate") == "SOURCE_POLICY_PUBLIC_CODE_REFRESH_20260614.json",
            f"{label} missing 2026-06-14 public-code refresh pointer",
        )
        checks.check(
            row.get("public_code_recheck_certificate_status")
            == "public_code_rechecked_no_distinct_vp2024_path_attempted_not_reproducible",
            f"{label} VP recheck status changed",
        )
        checks.check(row.get("public_code_recheck_date") == "2026-06-13", f"{label} VP recheck date changed")
        checks.check(row.get("public_code_recheck_tree_truncated") is False, f"{label} VP tree truncated")
        checks.check(row.get("public_code_recheck_tree_total_paths") == 4487, f"{label} VP tree count changed")
        checks.check(
            row.get("public_code_recheck_year2024_path_count") == 1540,
            f"{label} VP 2024 path count changed",
        )
        checks.check(
            row.get("public_code_recheck_keyword_path_hit_count") == 0,
            f"{label} VP keyword hits changed",
        )
        checks.check(
            row.get("public_code_recheck_source_policy_closed_rows") == 0,
            f"{label} VP recheck overclosed rows",
        )
        checks.check(
            row.get("public_code_recheck_attempted_not_reproducible_rows") == 4,
            f"{label} VP attempted-not-reproducible rows changed",
        )
        checks.check(
            row.get("distinct_public_vp2024_code_path_found") is False,
            f"{label} distinct VP public path unexpectedly found",
        )
    checks.check(vp_recheck_coverage.get("tree_truncated") is False, "VP recheck tree should be complete")
    checks.check(vp_recheck_coverage.get("keyword_path_hit_count") == 0, "VP recheck keyword hits changed")
    checks.check(vp_recheck_coverage.get("source_policy_rows_closed") == 0, "VP recheck overcloses rows")
    checks.check(tfe_recheck_coverage.get("github_repository_search_total_count") == 0, "TFE recheck repo hits changed")
    checks.check(tfe_recheck_coverage.get("source_policy_rows_closed") == 0, "TFE recheck overcloses rows")

    for token in [
        "Status: `nonpublic_code_rows_attempted_not_reproducible_not_promoted`.",
        "Rows audited: `20`.",
        "Self-reproduction attempted rows: `20`.",
        "Attempted-not-reproducible rows: `20`.",
        "Unable-to-reproduce rows: `20`.",
        "Source-policy closed rows: `0`.",
        "External-superiority ready rows: `0`.",
        "`tfe2026_original_pendulum`",
        "`vp2024_velocity_partitioning`",
        "`attempted_not_reproducible`",
    ]:
        checks.check(token in text, f"markdown missing token: {token}")

    if checks.errors:
        print("Source-policy self-reproduction attempt audit validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("Source-policy self-reproduction attempt audit validation: PASS")
    print("attempted_not_reproducible_rows=20/20")
    print("source_policy_closed_rows=0")
    print("external_superiority_ready_rows=0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
