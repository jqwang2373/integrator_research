#!/usr/bin/env python3
"""Validate the all-example result sanity audit."""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path


PAPER = Path(__file__).resolve().parent
ROOT = PAPER.parent
V048 = ROOT.parent / "numerics" / "v048_cross_paper_same_test_benchmarks" / "results"
EXPECTED_EXAMPLES = {"single_pendulum", "double_pendulum", "four_link", "slider_crank"}
EXPECTED_FLAGGED_KEYS = {
    "hi2022_rA/four_link",
    "hi2022_rA_half/double_pendulum",
    "hi2022_rA_half/four_link",
    "ra2021_rA/single_pendulum",
    "ra2021_rA/four_link",
    "ra2021_reps/single_pendulum",
    "ra2021_rp/single_pendulum",
    "ra2021_rp/double_pendulum",
    "tfe2026_Newmark_beta/single_pendulum",
    "tfe2026_TFE_m1/single_pendulum",
    "tfe2026_TFE_m2/single_pendulum",
    "tfe2026_trapezoidal/single_pendulum",
    "vp2024_coordinate_partitioning_rA/single_pendulum",
    "vp2024_coordinate_partitioning_rA/four_link",
    "vp2024_coordinate_partitioning_rA/slider_crank",
}
EXPECTED_FLAGGED_BY_EXAMPLE = {
    "single_pendulum": 8,
    "double_pendulum": 2,
    "four_link": 4,
    "slider_crank": 1,
}
EXPECTED_FLAGGED_BY_METHOD = {
    "hi2022_rA": 1,
    "hi2022_rA_half": 2,
    "ra2021_rA": 2,
    "ra2021_reps": 1,
    "ra2021_rp": 2,
    "tfe2026_Newmark_beta": 1,
    "tfe2026_TFE_m1": 1,
    "tfe2026_TFE_m2": 1,
    "tfe2026_trapezoidal": 1,
    "vp2024_coordinate_partitioning_rA": 3,
}
EXPECTED_FORENSIC_ISSUE_COUNTS = {
    "near_floor_order_unidentifiable": 3,
    "negative_velocity_order": 3,
    "original_tfe_runner_and_friction_source_policy_open": 16,
    "position_aligned_velocity_mismatch": 20,
    "source_policy_not_closed": 40,
    "velocity_error_nonmonotone_or_floor_limited": 5,
    "vp2024_code_path_unresolved_or_proxy": 4,
}
FORENSIC_ISSUE_REMAP = {
    "original_tfe_setup_not_encoded": "original_tfe_runner_and_friction_source_policy_open",
}


class Checks:
    def __init__(self) -> None:
        self.errors: list[str] = []

    def check(self, condition: bool, message: str) -> None:
        if not condition:
            self.errors.append(message)


def read_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def finite_number(value: object) -> bool:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return False
    return math.isfinite(number)


def main() -> int:
    checks = Checks()
    try:
        audit = read_json(PAPER / "ALL_EXAMPLES_RESULT_SANITY_AUDIT.json")
        audit_md = read_text(PAPER / "ALL_EXAMPLES_RESULT_SANITY_AUDIT.md")
        result_pack = read_json(PAPER / "PAPER_RESULT_PACK.json")
        forensic = read_json(V048 / "all_examples_apples_to_apples_forensic_audit.json")
    except Exception as exc:  # noqa: BLE001
        print(f"all-examples result sanity audit validation: FAIL\n- {exc}")
        return 1

    coverage = audit.get("coverage", {})
    local_gate = audit.get("local_method_gate", {})
    baseline = audit.get("baseline_sanity", {})
    boundary = audit.get("paper_claim_boundary", {})
    source_boundary = audit.get("source_policy_boundary", {})

    checks.check(audit.get("schema") == "all-examples-result-sanity-audit-v1", "audit schema changed")
    checks.check(audit.get("all_four_examples_audited") is True, "not all four examples audited")
    checks.check(set(coverage.get("examples", [])) == EXPECTED_EXAMPLES, "coverage example set changed")
    checks.check(coverage.get("example_count") == 4, "example count changed")
    checks.check(coverage.get("method_count") == 11, "method count changed")
    checks.check(coverage.get("cell_count") == 44, "cell count changed")
    checks.check(coverage.get("expected_cell_count") == 44, "expected cell count changed")
    checks.check(coverage.get("nonlocal_cell_count") == 40, "nonlocal cell count changed")
    checks.check(local_gate.get("method") == "local_Gauss6_FullVA", "local method changed")
    checks.check(local_gate.get("passed") is True, "local empirical gate did not pass")
    checks.check(local_gate.get("passed_rows") == local_gate.get("expected_rows") == 4, "local pass count changed")
    checks.check(
        finite_number(local_gate.get("min_velocity_order")) and float(local_gate.get("min_velocity_order")) >= 5.5,
        "local min observed order below gate",
    )
    checks.check(
        finite_number(local_gate.get("max_finest_velocity_error"))
        and float(local_gate.get("max_finest_velocity_error")) <= 1.0e-8,
        "local max finest velocity error above gate",
    )
    checks.check(baseline.get("source_policy_recheck_required") is True, "source-policy recheck gate missing")
    checks.check(baseline.get("flagged_nonlocal_count") == 15, "flagged nonlocal row count changed")
    checks.check(set(baseline.get("flagged_examples", [])) == EXPECTED_EXAMPLES, "flags do not cover all examples")
    checks.check(baseline.get("flagged_by_example") == EXPECTED_FLAGGED_BY_EXAMPLE, "flagged-by-example counts changed")
    checks.check(baseline.get("flagged_by_method") == EXPECTED_FLAGGED_BY_METHOD, "flagged-by-method counts changed")
    checks.check(set(baseline.get("flagged_row_keys", [])) == EXPECTED_FLAGGED_KEYS, "exact flagged row set changed")
    checks.check(
        baseline.get("severity_counts") == {"critical_recheck": 11, "warning_recheck": 4},
        "flagged severity counts changed",
    )
    checks.check(baseline.get("all_flagged_rows_quarantined") is True, "flagged rows are not fully quarantined")
    checks.check(boundary.get("external_superiority_allowed") is False, "external superiority boundary changed")
    checks.check(
        boundary.get("baseline_rows_usable_for_external_superiority") is False,
        "baseline external superiority boundary changed",
    )
    checks.check(boundary.get("exact_flagged_set_required") is True, "exact flagged-set requirement missing")
    checks.check(boundary.get("flagged_rows_enter_paper_claims") is False, "flagged rows leaked into paper claims")
    checks.check(audit.get("submission_ready") is False, "audit must not mark submission ready")
    checks.check(source_boundary.get("source_policy_reproduction") is False, "source-policy reproduction boundary changed")
    checks.check(source_boundary.get("public_code_fixed_grid_replay") is True, "public-code fixed-grid boundary changed")
    checks.check(
        result_pack.get("common_reference", {}).get("apples_to_apples_rows") == 44,
        "result pack apples-to-apples count changed",
    )
    checks.check(forensic.get("schema") == "all-examples-apples-to-apples-forensic-audit-v1", "forensic schema changed")
    checks.check(forensic.get("row_count") == 44, "forensic row count changed")
    checks.check(forensic.get("raw_row_count") == 132, "forensic raw row count changed")
    checks.check(forensic.get("all_method_example_cells_checked") is True, "forensic did not check all cells")
    checks.check(forensic.get("examples") and set(forensic.get("examples", [])) == EXPECTED_EXAMPLES, "forensic examples changed")
    checks.check(forensic.get("source_policy_superiority_claim_allowed") is False, "forensic overclaims source-policy superiority")
    checks.check(
        forensic.get("direct_error_superiority_claim_allowed_for_paper") is False,
        "forensic overclaims direct error superiority",
    )
    mapped_forensic_issue_counts: dict[str, int] = {}
    for issue, count in forensic.get("issue_counts", {}).items():
        mapped_issue = FORENSIC_ISSUE_REMAP.get(issue, issue)
        mapped_forensic_issue_counts[mapped_issue] = mapped_forensic_issue_counts.get(mapped_issue, 0) + int(count)
    checks.check(mapped_forensic_issue_counts == EXPECTED_FORENSIC_ISSUE_COUNTS, "forensic issue counts changed")
    for example in EXPECTED_EXAMPLES:
        per_example = forensic.get("per_example", {}).get(example, {})
        checks.check(per_example.get("row_count") == 11, f"{example} forensic row count changed")
        checks.check(per_example.get("method_count") == 11, f"{example} forensic method count changed")
        checks.check(per_example.get("issue_count") == 10, f"{example} forensic issue count changed")
        checks.check(
            per_example.get("source_policy_open_count") == 10,
            f"{example} forensic source-policy open count changed",
        )
        checks.check(
            per_example.get("strict_external_error_claim_allowed_count") == 0,
            f"{example} forensic strict-claim count changed",
        )
    for row in baseline.get("flagged_rows", []):
        checks.check(
            row.get("disposition") == "needs_source_policy_recheck_before_external_claim",
            f"{row.get('method')}/{row.get('example')} is not quarantined",
        )
    for token in [
        "all four examples audited",
        "`single_pendulum`",
        "`double_pendulum`",
        "`four_link`",
        "`slider_crank`",
        "Flagged Nonlocal Rows",
        "Exact Recheck Set",
        "Every flagged row is quarantined",
        "does not close B4 or any source-policy execution rows",
    ]:
        checks.check(token in audit_md, f"audit markdown missing token: {token}")

    if checks.errors:
        print("all-examples result sanity audit validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("all-examples result sanity audit validation: PASS")
    print("cells=44/44")
    print("examples=single_pendulum,double_pendulum,four_link,slider_crank")
    print(f"flagged_nonlocal_rows={baseline.get('flagged_nonlocal_count')}")
    print("external_superiority_allowed=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
