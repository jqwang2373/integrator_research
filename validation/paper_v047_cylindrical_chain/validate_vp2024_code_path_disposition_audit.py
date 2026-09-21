#!/usr/bin/env python3
"""Validate the all-example VP2024 code-path disposition audit."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
EXPECTED_EXAMPLES = ["single_pendulum", "double_pendulum", "four_link", "slider_crank"]


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


def main() -> int:
    checks = Checks()
    try:
        audit = read_json(PAPER / "VP2024_CODE_PATH_DISPOSITION_AUDIT.json")
        audit_md = read_text(PAPER / "VP2024_CODE_PATH_DISPOSITION_AUDIT.md")
        closure = read_json(PAPER / "EXTERNAL_SOURCE_POLICY_CLOSURE_MANIFEST.json")
        case_recon = read_json(PAPER / "EXTERNAL_CASE_EVIDENCE_RECONCILIATION.json")
        comparison = read_json(PAPER / "COMPARISON_OBJECTIVE_CLOSURE_RECONCILIATION_AUDIT.json")
    except Exception as exc:  # noqa: BLE001
        print(f"VP2024 code-path disposition audit validation: FAIL\n- {exc}")
        return 1

    coverage = audit.get("coverage", {})
    source_files = audit.get("source_files", {})
    v048_summary = audit.get("v048_public_code_path_summary", {})
    disposition = audit.get("source_code_path_disposition", {})
    source_rows = audit.get("source_policy_rows", {})
    common = audit.get("common_reference_proxy_disposition", {})
    large = audit.get("large_step_diagnostic_boundary", {})
    search = audit.get("public_code_search", {})
    api = audit.get("public_repository_api_spot_check", {})
    local_scan = audit.get("local_repository_tree_scan", {})
    case = audit.get("case_reconciliation_crosscheck", {})
    method_identity = audit.get("method_identity", {})
    execution = audit.get("execution_policy", {})
    example_rows = audit.get("example_rows", [])
    closure_vp = next(row for row in closure.get("suites", []) if row.get("suite_id") == "vp2024_velocity_partitioning")
    recon_vp = next(row for row in case_recon.get("suites", []) if row.get("suite_id") == "vp2024_velocity_partitioning")

    checks.check(audit.get("schema") == "vp2024-code-path-disposition-audit-v1", "schema changed")
    checks.check(
        audit.get("status") == "all_four_examples_checked_no_distinct_public_code_unable_to_reproduce_not_promoted",
        "status changed",
    )
    checks.check(audit.get("submission_ready") is False, "audit must not mark submission ready")
    checks.check(audit.get("examples") == EXPECTED_EXAMPLES, "example order/set changed")
    checks.check(
        source_files.get("v048_summary") == "../../numerics/v048_cross_paper_same_test_benchmarks/results/summary_v048.json",
        "missing v048 summary source-file anchor",
    )
    checks.check(
        source_files.get("velocity_partitioning_code_search_csv")
        == "../../numerics/v048_cross_paper_same_test_benchmarks/results/velocity_partitioning_code_search.csv",
        "missing VP code-search CSV source-file anchor",
    )
    checks.check(
        source_files.get("external_source_policy_closure_manifest")
        == "EXTERNAL_SOURCE_POLICY_CLOSURE_MANIFEST.json",
        "missing source-policy closure source-file anchor",
    )
    checks.check(
        v048_summary.get("status") == "not_resolved_in_local_sbel_or_public_metadata_tree",
        "v048 VP code-path status changed",
    )
    checks.check(
        v048_summary.get("public_web_search_status") == "no_distinct_repo_found",
        "v048 public web-search status changed",
    )
    checks.check(v048_summary.get("relevant_code_path_resolved") is False, "v048 code path unexpectedly resolved")
    checks.check(v048_summary.get("row_count") == 18, "v048 VP code-search row count changed")
    checks.check(
        v048_summary.get("easychair_visible_repository_reference")
        == "https://github.com/uwsbel/public-metadata/tree/master/2021/ASME/rA-formulation",
        "v048 EasyChair public-code reference changed",
    )
    checks.check(coverage.get("examples_checked") == EXPECTED_EXAMPLES, "coverage examples changed")
    checks.check(coverage.get("all_four_examples_checked") is True, "all-four-example marker missing")
    checks.check(coverage.get("source_policy_rows") == 4, "source-policy row count changed")
    checks.check(coverage.get("source_policy_code_path_unresolved_rows") == 4, "VP source-policy unresolved count changed")
    checks.check(
        coverage.get("source_policy_rows_attempted_not_reproducible") == 4
        and coverage.get("unable_to_reproduce_rows") == 4,
        "VP attempted/unable counts changed",
    )
    checks.check(coverage.get("common_reference_proxy_rows") == 4, "common-reference VP proxy rows changed")
    checks.check(coverage.get("common_reference_local_velocity_order_wins") == 4, "VP proxy order wins changed")
    checks.check(coverage.get("common_reference_local_finest_velocity_error_wins") == 4, "VP proxy error wins changed")
    checks.check(coverage.get("large_step_diagnostic_local_velocity_order_wins") == 4, "large-step order wins changed")
    checks.check(coverage.get("large_step_diagnostic_local_finest_velocity_error_wins") == 1, "large-step error boundary changed")

    checks.check(method_identity.get("alias_resolved") is True, "VP alias resolution changed")
    checks.check(method_identity.get("implemented_method") == "vp2024_coordinate_partitioning_rA", "implemented VP method changed")
    checks.check(method_identity.get("distinct_unresolved_vp_method_remaining") is False, "distinct VP method unexpectedly unresolved")
    checks.check(disposition.get("distinct_public_vp_code_path_found") is False, "distinct public VP path unexpectedly found")
    checks.check(disposition.get("coordinate_partitioning_proxy_available") is True, "VP proxy availability changed")
    checks.check(disposition.get("coordinate_partitioning_proxy_is_source_policy_reproduction") is False, "VP proxy incorrectly promoted to source policy")
    checks.check(disposition.get("self_reproduction_attempted") is True, "VP self-reproduction marker missing")
    checks.check(disposition.get("unable_to_reproduce") is True, "VP unable-to-reproduce marker missing")
    checks.check(
        disposition.get("final_nonpublic_code_disposition") == "unable_to_reproduce_not_promoted",
        "VP final nonpublic-code disposition changed",
    )
    checks.check(disposition.get("current_disposition") == "demote_until_code_path_resolved", "VP disposition changed")
    checks.check(disposition.get("current_status") == "public_code_path_unresolved_or_proxy_only", "VP status changed")
    checks.check(disposition.get("claim_allowed_now") == "code-path-unresolved_related_work_only", "VP claim boundary changed")
    checks.check(disposition.get("accepted_for_external_superiority") is False, "VP accepted for external superiority")
    checks.check(disposition.get("queue_status") == "not_ready_code_path_unresolved", "VP queue status changed")
    checks.check(disposition.get("parallel_shard_count") == 0, "VP shard count changed")

    checks.check(source_rows.get("performance_matrix_row_count") == closure_vp.get("performance_rows", {}).get("row_count") == 4, "VP performance row count changed")
    checks.check(source_rows.get("completed_row_count") == 0, "VP source-policy rows unexpectedly completed")
    checks.check(source_rows.get("not_complete_row_count") == 4, "VP incomplete row count changed")
    checks.check(source_rows.get("status_counts") == {"code_path_unresolved": 4}, "VP status counts changed")
    checks.check(source_rows.get("source_policy_flagged_rows") == 3, "VP flagged-row count changed")
    checks.check(source_rows.get("attempted_not_reproducible_row_count") == 4, "VP attempted row count changed")
    checks.check(source_rows.get("unable_to_reproduce_row_count") == 4, "VP unable row count changed")
    checks.check(
        source_rows.get("final_nonpublic_code_disposition") == "unable_to_reproduce_not_promoted",
        "VP source-row final disposition changed",
    )
    checks.check(source_rows.get("source_policy_rows_closed") == 0, "VP source-policy rows unexpectedly closed")
    checks.check(source_rows.get("external_superiority_ready_rows") == 0, "VP rows unexpectedly claim-ready")

    checks.check(common.get("controlling_for_apples_to_apples_diagnostic") is True, "common-reference diagnostic boundary changed")
    checks.check(common.get("controlling_for_source_policy_external_superiority") is False, "common-reference proxy incorrectly controls source policy")
    checks.check(common.get("direct_nonlocal_velocity_order_wins") == comparison.get("direct_nonlocal_velocity_order_wins") == 40, "global order wins changed")
    checks.check(common.get("direct_nonlocal_finest_velocity_error_wins") == comparison.get("direct_nonlocal_finest_velocity_error_wins") == 40, "global error wins changed")
    checks.check(common.get("vp_proxy_local_velocity_order_wins") == 4, "VP proxy local order wins changed")
    checks.check(common.get("vp_proxy_local_finest_velocity_error_wins") == 4, "VP proxy local error wins changed")

    checks.check(large.get("noncontrolling_mixed_reference_policy") is True, "large-step boundary missing")
    checks.check(large.get("local_velocity_order_wins") == 4, "large-step local order wins changed")
    checks.check(large.get("local_finest_velocity_error_wins") == 1, "large-step local error wins changed")
    checks.check(large.get("vp_finest_velocity_error_wins") == 3, "legacy VP error boundary changed")

    checks.check(search.get("row_count", 0) >= 15, "VP code-search evidence row count too small")
    checks.check(
        search.get("source_csv") == "../../numerics/v048_cross_paper_same_test_benchmarks/results/velocity_partitioning_code_search.csv",
        "VP code-search source CSV anchor missing",
    )
    checks.check(search.get("public_web_search_row_count") == 1, "VP public web-search row count changed")
    checks.check(search.get("public_web_search_status") == "no_distinct_repo_found", "VP public search status changed")
    checks.check(
        "web_search_2026_05_31" in search.get("public_web_search_scopes", []),
        "VP public web-search dated scope missing",
    )
    checks.check(search.get("github_code_search_auth_boundary") is True, "GitHub code-search auth boundary missing")
    checks.check(search.get("points_to_2021_rA_repo") is True, "2021 rA repo reference marker missing")
    checks.check(search.get("distinct_vp_repo_found") is False, "distinct VP repo unexpectedly found")
    checks.check(search.get("distinct_vp_code_path_found") is False, "distinct VP code path unexpectedly found")
    checks.check(api.get("checked_on") == "2026-06-01", "API spot-check date changed")
    checks.check("CPD" in api.get("year_2024_directories", []), "2024 CPD directory snapshot missing")
    checks.check(api.get("year_2024_contains_velocity_partitioning_named_dir") is False, "VP-named 2024 dir unexpectedly present")
    checks.check(api.get("year_2024_cpd_tree_is_mbd_velocity_partitioning") is False, "CPD tree incorrectly treated as VP MBD")
    checks.check(local_scan.get("local_sbel_reproducibility_exists") is True, "local sbel-reproducibility scan missing")
    checks.check(
        local_scan.get("local_sbel_top_level_directories") == ["2021", "2022"],
        "local sbel-reproducibility top-level directory snapshot changed",
    )
    checks.check(
        local_scan.get("local_sbel_year_2024_directory_present") is False,
        "local sbel-reproducibility unexpectedly has a visible 2024 directory",
    )
    local_mbd_roots = set(local_scan.get("local_sbel_visible_mbd_code_roots", []))
    checks.check(
        "2021/ASME/rA-formulation" in local_mbd_roots
        and "2022/HalfImplicit_JCND" in local_mbd_roots,
        "local visible MBD code roots lost 2021/2022 anchors",
    )
    checks.check(
        local_scan.get("local_sbel_velocity_partition_term_hit_count") == 0,
        "local velocity-partition text search unexpectedly found hits",
    )
    checks.check(
        local_scan.get("local_sbel_distinct_vp2024_code_path_found") is False,
        "local scan unexpectedly found distinct VP2024 code path",
    )
    checks.check(local_scan.get("local_public_metadata_exists") is True, "local public-metadata scan missing")
    checks.check(
        local_scan.get("local_public_metadata_visible_non_git_file_count") == 0,
        "local public-metadata checkout unexpectedly exposes non-git files",
    )

    checks.check(case.get("bounded_evidence_present") == recon_vp.get("bounded_evidence_present") is False, "VP bounded evidence changed")
    checks.check(case.get("case_inventory_status_counts") == {"code_path_unresolved": 1}, "VP case inventory changed")
    checks.check(case.get("performance_status_counts") == {"code_path_unresolved": 4}, "VP performance case status changed")
    checks.check(case.get("external_superiority_ready") is False, "VP case unexpectedly ready")
    checks.check(case.get("source_policy_closed") is False, "VP case unexpectedly closed")

    checks.check(len(example_rows) == 4, "example-row count changed")
    checks.check([row.get("example") for row in example_rows] == EXPECTED_EXAMPLES, "example-row order changed")
    checks.check(all(row.get("source_policy_status") == "code_path_unresolved" for row in example_rows), "some VP source-policy row resolved unexpectedly")
    checks.check(all(row.get("source_policy_code_path_resolved") is False for row in example_rows), "some VP code path marked resolved")
    checks.check(all(row.get("self_reproduction_attempted") is True for row in example_rows), "some VP row missing self-reproduction attempt")
    checks.check(all(row.get("unable_to_reproduce") is True for row in example_rows), "some VP row missing unable marker")
    checks.check(
        all(row.get("final_nonpublic_code_disposition") == "unable_to_reproduce_not_promoted" for row in example_rows),
        "some VP row has stale final disposition",
    )
    checks.check(all(row.get("common_reference_proxy_status") == "ok" for row in example_rows), "some VP proxy row not ok")
    checks.check(all(row.get("common_reference_local_wins_velocity_order") is True for row in example_rows), "some VP proxy order win lost")
    checks.check(all(row.get("common_reference_local_wins_finest_velocity_error") is True for row in example_rows), "some VP proxy error win lost")
    checks.check(all(row.get("proxy_is_source_policy_reproduction") is False for row in example_rows), "some VP proxy row promoted to source policy")

    checks.check(execution.get("read_only_existing_artifacts") is True, "audit is not read-only")
    checks.check(execution.get("default_1e_4_required") is False, "audit requires default 1e-4")
    checks.check(execution.get("heavy_numerical_run_invoked") is False, "audit invoked heavy run")
    checks.check(execution.get("run_v047_invoked") is False, "audit invoked run_v047")
    checks.check(execution.get("v048_runner_invoked") is False, "audit invoked v048 runner")

    for token in [
        "ALL FOUR EXAMPLES CHECKED; NO DISTINCT PUBLIC CODE; UNABLE TO REPRODUCE; NOT PROMOTED",
        "Source-policy VP rows unresolved: `4/4`",
        "Source-policy VP rows attempted-not-reproducible/unable: `4/4`",
        "Final nonpublic-code disposition: `unable_to_reproduce_not_promoted`",
        "Common-reference proxy local velocity-order wins: `4/4`",
        "Common-reference proxy local finest-velocity-error wins: `4/4`",
        "Larger-step diagnostic local finest-velocity-error wins: `1/4`",
        "Distinct public VP code path found: `False`",
        "Proxy is source-policy reproduction: `False`",
        "Claim allowed now: `code-path-unresolved_related_work_only`",
        "Search evidence source: `../../numerics/v048_cross_paper_same_test_benchmarks/results/velocity_partitioning_code_search.csv`",
        "Public web search status: `no_distinct_repo_found`",
        "Public web search evidence rows: `1`",
        "GitHub code-search auth boundary: `True`",
        "V048 code-path summary status: `not_resolved_in_local_sbel_or_public_metadata_tree`",
        "2024 public repo directory names from the API spot check",
        "Local sbel-reproducibility top-level directories: `2021, 2022`",
        "Local velocity-partition search hits: `0`",
        "Local distinct VP2024 code path found: `False`",
    ]:
        checks.check(token in audit_md, f"markdown missing token: {token}")

    if checks.errors:
        print("VP2024 code-path disposition audit validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("VP2024 code-path disposition audit validation: PASS")
    print("examples=single_pendulum,double_pendulum,four_link,slider_crank")
    print("source_policy_code_path_unresolved_rows=4/4")
    print("unable_to_reproduce_rows=4/4")
    print("common_reference_vp_proxy_local_order_wins=4/4")
    print("common_reference_vp_proxy_local_error_wins=4/4")
    print("large_step_local_error_wins=1/4_noncontrolling")
    print("distinct_public_vp_code_path_found=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
