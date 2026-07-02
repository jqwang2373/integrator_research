#!/usr/bin/env python3
"""Read-only validator for the coarse-first external readiness gate."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
EXAMPLES = {"single_pendulum", "double_pendulum", "four_link", "slider_crank"}


class Checks:
    def __init__(self) -> None:
        self.errors: list[str] = []

    def check(self, condition: bool, message: str) -> None:
        if not condition:
            self.errors.append(message)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def read_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def main() -> int:
    checks = Checks()
    try:
        rows = read_csv(RESULTS / "coarse_first_external_readiness_gate.csv")
        summary = read_json(RESULTS / "coarse_first_external_readiness_gate.json")
        markdown = (RESULTS / "coarse_first_external_readiness_gate.md").read_text(encoding="utf-8")
    except Exception as exc:  # noqa: BLE001 - concise CLI failure.
        print(f"coarse-first external readiness gate validation: FAIL\n- {exc}")
        return 1

    by_example = {row.get("example"): row for row in rows}
    checks.check(summary.get("schema") == "coarse-first-external-readiness-gate-v1", "schema changed")
    checks.check(set(summary.get("examples", [])) == EXAMPLES, "summary examples changed")
    checks.check(len(rows) == 4, "readiness gate must have one row per example")
    checks.check(set(by_example) == EXAMPLES, "CSV examples changed")
    checks.check(summary.get("row_count") == 4, "summary row count changed")
    checks.check(summary.get("default_policy") == "coarse_first_no_default_1e-4", "default policy changed")
    checks.check(summary.get("coarse_step_sizes") == [0.1, 0.05, 0.025], "coarse step sizes changed")
    checks.check(summary.get("coarse_reference_h") == 0.0125, "coarse reference h changed")
    checks.check(summary.get("same_test_campaign_status") == "not_run", "same-test campaign must remain not_run")
    checks.check(summary.get("external_superiority_claim") is False, "must not claim external superiority")
    checks.check(summary.get("submission_ready") is False, "readiness gate must not mark submission ready")
    checks.check(summary.get("coarse_same_window_ready_count") == 2, "single and double should be coarse-ready now")
    checks.check(
        summary.get("single_coarse_same_window_available_count") == 1,
        "single coarse same-window availability count changed",
    )
    checks.check(
        summary.get("local_true_dynamic_order_available_count") == 2,
        "closed-loop local true-dynamic order count changed",
    )
    checks.check(
        summary.get("public_work_precision_available_count") == 2,
        "closed-loop public work/precision availability count changed",
    )
    checks.check(
        summary.get("public_work_precision_missing_count") == 0,
        "closed-loop public work/precision should now be available",
    )
    checks.check(
        summary.get("strict_common_reference_available_count") == 2,
        "closed-loop strict common-reference availability count changed",
    )
    checks.check(
        summary.get("strict_common_reference_gap_count") == 0,
        "closed-loop strict common-reference gap should now be closed",
    )
    checks.check(
        summary.get("strict_common_reference_figure_available") is True,
        "closed-loop strict common-reference figure availability changed",
    )
    checks.check(summary.get("closed_loop_surrogate_available_count") == 0, "closed-loop surrogate status count changed")
    checks.check(summary.get("closed_loop_floor_audit_available_count") == 2, "closed-loop floor-audit count changed")
    checks.check(summary.get("dynamic_order_missing_count") == 0, "closed-loop dynamic order should now be locally available")

    double_row = by_example.get("double_pendulum", {})
    checks.check(
        double_row.get("readiness_status") == "coarse_same_window_order_time_available",
        "double_pendulum should be the available coarse same-window row",
    )
    checks.check("7.951/7.042" in double_row.get("current_order_evidence", ""), "double Gauss6 order missing")
    checks.check("0.703/0.754" in double_row.get("current_order_evidence", ""), "double public order missing")
    checks.check(double_row.get("superiority_claim_allowed") == "false", "double row must not allow superiority claim")

    single_row = by_example.get("single_pendulum", {})
    checks.check(
        single_row.get("readiness_status") == "coarse_same_window_order_time_available",
        "single_pendulum should be a coarse same-window row",
    )
    checks.check(
        "6.054/2.951" in single_row.get("current_order_evidence", ""),
        "single row should report Gauss6 coarse order",
    )
    checks.check(
        "reference floor" in single_row.get("current_order_evidence", ""),
        "single row should preserve reference-floor caveat",
    )
    checks.check(
        "do not rerun source h=1e-4" in single_row.get("next_lightweight_action", ""),
        "single row should preserve no-default-1e-4 action",
    )

    for example in ("four_link", "slider_crank"):
        row = by_example.get(example, {})
        checks.check(
            row.get("readiness_status")
            == "local_true_dynamic_order_public_work_and_strict_common_reference_available",
            f"{example} should have local true-dynamic order, public work, and strict common-reference evidence",
        )
        checks.check(
            "Local true-dynamic Newton coarse row available" in row.get("current_order_evidence", ""),
            f"{example} should report local true-dynamic order",
        )
        checks.check(
            "pos/orient/vel/omega order" in row.get("current_order_evidence", ""),
            f"{example} should report primary state orders",
        )
        checks.check(
            "stage oracle used=false" in row.get("current_order_evidence", ""),
            f"{example} should record no stage oracle",
        )
        checks.check(
            "strict common-reference v047 exact-endpoint error columns are available"
            in row.get("current_time_evidence", ""),
            f"{example} should record strict common-reference evidence",
        )
        checks.check(
            "keep source h=1e-4 opt-in" in row.get("next_lightweight_action", ""),
            f"{example} should keep no-default-1e-4 action",
        )
        checks.check(
            "closed_loop_true_dynamic_newton_coarse_order_rows.csv" in row.get("evidence_paths", ""),
            f"{example} missing true-dynamic order evidence path",
        )
        checks.check(
            "closed_loop_true_dynamic_public_work_precision_summary.csv" in row.get("evidence_paths", ""),
            f"{example} missing public work/precision evidence path",
        )
        checks.check(
            "closed_loop_true_dynamic_strict_common_reference_summary.csv" in row.get("evidence_paths", ""),
            f"{example} missing strict common-reference evidence path",
        )

    checks.check("no external superiority claim" in markdown, "markdown must preserve no-superiority status")
    checks.check("`1e-4` is not a default execution target" in markdown, "markdown must state no default 1e-4")
    checks.check("coarse_same_window_order_time_available" in markdown, "markdown missing coarse-ready status")
    checks.check(
        "local_true_dynamic_order_public_work_and_strict_common_reference_available" in markdown,
        "markdown missing strict common-reference status",
    )

    if checks.errors:
        print("coarse-first external readiness gate validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("coarse-first external readiness gate validation: PASS")
    print(f"rows={summary.get('row_count')}")
    print(f"coarse_same_window_ready={summary.get('coarse_same_window_ready_count')}/4")
    print(f"local_true_dynamic_order={summary.get('local_true_dynamic_order_available_count')}")
    print(f"public_work_precision_available={summary.get('public_work_precision_available_count')}")
    print(f"public_work_precision_missing={summary.get('public_work_precision_missing_count')}")
    print(f"strict_common_reference_available={summary.get('strict_common_reference_available_count')}")
    print(f"strict_common_reference_gap={summary.get('strict_common_reference_gap_count')}")
    print(f"strict_common_reference_figure_available={summary.get('strict_common_reference_figure_available')}")
    print(f"closed_loop_floor_audit={summary.get('closed_loop_floor_audit_available_count')}")
    print(f"dynamic_order_missing={summary.get('dynamic_order_missing_count')}")
    print("external_superiority_claim=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
