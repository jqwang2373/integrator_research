#!/usr/bin/env python3
"""Read-only validator for the external same-test acceptance sheet."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
ROOT = PAPER.parent
V048 = ROOT.parent / "numerics" / "v048_cross_paper_same_test_benchmarks" / "results"
SHEET_JSON = PAPER / "EXTERNAL_SAME_TEST_ACCEPTANCE_SHEET.json"
SHEET_MD = PAPER / "EXTERNAL_SAME_TEST_ACCEPTANCE_SHEET.md"
RUN_QUEUE = PAPER / "EXTERNAL_SAME_TEST_RUN_QUEUE.json"
EXTERNAL_GATE = PAPER / "CMAME_EXTERNAL_BASELINE_GATE.json"
BLOCKER_GATE = PAPER / "CMAME_BLOCKER_CLOSURE_GATE.json"
FOUR_EXAMPLE_DASHBOARD = PAPER / "FOUR_EXAMPLE_SOURCE_POLICY_DASHBOARD.json"
CROSS_CASES = PAPER / "CROSS_PAPER_BENCHMARK_CASES.json"
MANIFEST = PAPER / "SUBMISSION_ARTIFACT_MANIFEST.json"
PERFORMANCE = V048 / "four_example_performance_summary.json"
TRUE_DYNAMIC = V048 / "closed_loop_true_dynamic_newton_coarse_order.json"
STRICT_COMMON = V048 / "closed_loop_true_dynamic_strict_common_reference.json"

EXPECTED_EXAMPLES = ["single_pendulum", "double_pendulum", "four_link", "slider_crank"]
EXPECTED_METRICS = [
    "position_error",
    "velocity_error",
    "observed_order",
    "runtime",
    "work_precision",
    "average_newton_iterations",
    "constraint_drift",
    "reference_policy",
    "same_test_setup_identity",
]


class Checks:
    def __init__(self) -> None:
        self.errors: list[str] = []

    def check(self, condition: bool, message: str) -> None:
        if not condition:
            self.errors.append(message)


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(path)
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def read_text(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8", errors="replace")


def contains_normalized(text: str, token: str) -> bool:
    return token in text or " ".join(token.split()) in " ".join(text.split())


def require_tokens(checks: Checks, text: str, tokens: list[str], label: str) -> None:
    for token in tokens:
        checks.check(contains_normalized(text, token), f"{label} missing token: {token}")


def blocker_by_id(blocker_gate: dict[str, Any], blocker_id: str) -> dict[str, Any]:
    for blocker in blocker_gate.get("blockers", []):
        if isinstance(blocker, dict) and blocker.get("id") == blocker_id:
            return blocker
    return {}


def main() -> int:
    checks = Checks()
    try:
        sheet = read_json(SHEET_JSON)
        sheet_md = read_text(SHEET_MD)
        run_queue = read_json(RUN_QUEUE)
        external_gate = read_json(EXTERNAL_GATE)
        blocker_gate = read_json(BLOCKER_GATE)
        four_example_dashboard = read_json(FOUR_EXAMPLE_DASHBOARD)
        cross_cases = read_json(CROSS_CASES)
        manifest = read_json(MANIFEST)
        performance = read_json(PERFORMANCE)
        true_dynamic = read_json(TRUE_DYNAMIC)
        strict_common = read_json(STRICT_COMMON)
    except Exception as exc:  # noqa: BLE001 - concise CLI failure.
        print(f"external_same_test_acceptance_sheet=FAIL\n- {exc}")
        return 1

    execution = sheet.get("execution_policy", {})
    counts = sheet.get("acceptance_counts", {})
    closure = sheet.get("closure_rules", {})
    b2 = blocker_by_id(blocker_gate, "B2")
    b4 = blocker_by_id(blocker_gate, "B4")

    checks.check(sheet.get("schema") == "external-same-test-acceptance-sheet-v1", "schema changed")
    checks.check(
        sheet.get("status") == "acceptance_requirements_defined_campaign_not_run",
        "status changed",
    )
    checks.check(sheet.get("submission_ready") is False, "sheet must not claim submission ready")
    checks.check(sheet.get("same_test_campaign_status") == "not_run", "same-test status changed")
    checks.check(sheet.get("external_superiority_claim") is False, "external superiority overclaim")

    checks.check(execution.get("read_only_acceptance_sheet") is True, "sheet lost read-only marker")
    checks.check(execution.get("default_step_policy") == "coarse_first_no_default_1e-4", "default policy changed")
    checks.check(execution.get("coarse_step_sizes") == [0.1, 0.05, 0.025], "coarse step sizes changed")
    checks.check(execution.get("coarse_reference_h") == 0.0125, "coarse reference changed")
    checks.check(execution.get("strict_public_policy_1e-4") == "opt_in_only", "strict 1e-4 policy changed")
    checks.check(execution.get("default_1e-4_required") is False, "sheet incorrectly requires default 1e-4")
    checks.check(execution.get("heavy_numerical_run_invoked") is False, "sheet invoked heavy numerical run")
    checks.check(execution.get("run_v047_invoked") is False, "sheet invoked run_v047")
    checks.check(execution.get("v048_runner_invoked") is False, "sheet invoked v048 runner")

    checks.check(counts.get("examples_required") == 4, "example count changed")
    checks.check(counts.get("external_required_case_count") == 17, "external case count changed")
    checks.check(counts.get("performance_matrix_row_count") == 48, "performance row count changed")
    checks.check(counts.get("performance_matrix_completed_row_count") == 32, "performance completed count changed")
    checks.check(counts.get("performance_matrix_not_complete_row_count") == 16, "performance incomplete count changed")
    checks.check(counts.get("performance_matrix_partial_row_count") == 0, "performance partial count changed")
    checks.check(
        counts.get("local_evidence_coverage_examples_count")
        == four_example_dashboard.get("local_evidence_coverage_examples")
        == 4,
        "local evidence coverage count changed",
    )
    checks.check(
        counts.get("accepted_method_dynamic_order_examples_count")
        == four_example_dashboard.get("accepted_method_dynamic_order_example_count")
        == 2,
        "accepted method dynamic-order count changed",
    )
    checks.check(
        counts.get("mechanism_coverage_examples_count")
        == four_example_dashboard.get("mechanism_coverage_example_count")
        == 2,
        "mechanism coverage count changed",
    )
    checks.check(
        counts.get("local_dynamic_order_examples_count")
        == four_example_dashboard.get("local_dynamic_order_closed_examples")
        == 2,
        "local dynamic-order count changed",
    )
    checks.check(
        counts.get("accepted_source_policy_dynamic_order_examples_count")
        == four_example_dashboard.get("accepted_source_policy_dynamic_order_examples")
        == 0,
        "source-policy dynamic-order count changed",
    )
    checks.check(
        counts.get("accepted_external_dynamic_order_examples_count") == 0,
        "accepted external dynamic-order count changed",
    )
    checks.check(counts.get("parallel_ready_batch_count") == 2, "parallel-ready batch count changed")
    checks.check(
        counts.get("parallel_shard_count_without_default_1e-4") == 20,
        "parallel shard count changed",
    )
    checks.check(sheet.get("required_metric_columns") == EXPECTED_METRICS, "required metric list changed")

    rows = sheet.get("example_acceptance_rows", [])
    row_by_example = {row.get("example"): row for row in rows if isinstance(row, dict)}
    checks.check(list(row_by_example) == EXPECTED_EXAMPLES, "example acceptance rows changed")
    for example, row in row_by_example.items():
        checks.check(row.get("accepted_for_external_superiority") is False, f"{example} overclaims external superiority")
    checks.check(row_by_example["single_pendulum"].get("accepted_for_internal_method_order") is True, "single order marker changed")
    checks.check(row_by_example["double_pendulum"].get("accepted_for_internal_method_order") is True, "double order marker changed")
    checks.check(row_by_example["four_link"].get("accepted_for_internal_method_order") is False, "four-link dynamic-order marker changed")
    checks.check(row_by_example["slider_crank"].get("accepted_for_internal_method_order") is False, "slider-crank dynamic-order marker changed")
    checks.check(row_by_example["four_link"].get("accepted_for_mechanism_coverage") is True, "four-link mechanism coverage marker changed")
    checks.check(row_by_example["slider_crank"].get("accepted_for_mechanism_coverage") is True, "slider-crank mechanism coverage marker changed")

    suite_ids = [row.get("suite_id") for row in sheet.get("source_suite_acceptance", []) if isinstance(row, dict)]
    checks.check(
        suite_ids
        == [
            "tfe2026_original_pendulum",
            "ra2021_absolute_coordinate",
            "hi2022_half_implicit",
            "vp2024_velocity_partitioning",
        ],
        "suite acceptance list changed",
    )
    for suite in sheet.get("source_suite_acceptance", []):
        if isinstance(suite, dict):
            checks.check(
                suite.get("default_1e-4_required") is False,
                f"{suite.get('suite_id', '<unknown>')} incorrectly requires default 1e-4",
            )

    checks.check(closure.get("residual_only_rows_count_as_dynamic_order") is False, "residual-only rule changed")
    checks.check(closure.get("suite_demotions_must_be_in_manuscript") is True, "suite demotion rule changed")
    checks.check(closure.get("default_1e-4_required_for_b2_or_b4") is False, "B2/B4 default 1e-4 rule changed")

    queue_counts = run_queue.get("coverage_counts", {})
    queue_execution = run_queue.get("execution_policy", {})
    checks.check(run_queue.get("same_test_campaign_status") == "not_run", "run queue overclaims campaign")
    checks.check(run_queue.get("external_superiority_claim") is False, "run queue overclaims superiority")
    checks.check(queue_execution.get("default_step_policy") == execution.get("default_step_policy"), "run queue policy mismatch")
    checks.check(queue_execution.get("coarse_step_sizes") == execution.get("coarse_step_sizes"), "run queue coarse steps mismatch")
    checks.check(queue_execution.get("coarse_reference_h") == execution.get("coarse_reference_h"), "run queue reference mismatch")
    checks.check(queue_execution.get("default_1e-4_required") is False, "run queue requires default 1e-4")
    checks.check(queue_counts.get("required_case_count") == counts.get("external_required_case_count"), "case count mismatch")
    checks.check(
        run_queue.get("local_dynamic_order_boundary", {}).get("local_evidence_coverage_examples_count")
        == counts.get("local_evidence_coverage_examples_count"),
        "run queue local evidence coverage count mismatch",
    )
    checks.check(
        run_queue.get("local_dynamic_order_boundary", {}).get("accepted_method_dynamic_order_examples_count")
        == counts.get("accepted_method_dynamic_order_examples_count"),
        "run queue accepted method dynamic-order count mismatch",
    )
    checks.check(
        run_queue.get("local_dynamic_order_boundary", {}).get("mechanism_coverage_examples_count")
        == counts.get("mechanism_coverage_examples_count"),
        "run queue mechanism coverage count mismatch",
    )
    checks.check(
        run_queue.get("local_dynamic_order_boundary", {}).get("accepted_source_policy_dynamic_order_examples_count")
        == counts.get("accepted_source_policy_dynamic_order_examples_count"),
        "run queue source-policy dynamic-order count mismatch",
    )
    checks.check(
        queue_counts.get("parallel_shard_count_without_default_1e-4")
        == counts.get("parallel_shard_count_without_default_1e-4"),
        "parallel shard mismatch",
    )

    checks.check(performance.get("examples") == EXPECTED_EXAMPLES, "performance examples changed")
    checks.check(performance.get("row_count") == counts.get("performance_matrix_row_count"), "performance row mismatch")
    checks.check(performance.get("completed_row_count") == counts.get("performance_matrix_completed_row_count"), "completed mismatch")
    checks.check(performance.get("not_complete_row_count") == counts.get("performance_matrix_not_complete_row_count"), "incomplete mismatch")
    checks.check(performance.get("partial_row_count") == counts.get("performance_matrix_partial_row_count"), "partial mismatch")
    checks.check(performance.get("same_test_campaign_status") == "not_run", "performance campaign overclaim")
    checks.check(performance.get("external_superiority_claim") is False, "performance superiority overclaim")

    checks.check(true_dynamic.get("step_sizes") == [0.1, 0.05, 0.025], "true-dynamic coarse steps changed")
    checks.check(true_dynamic.get("external_superiority_claim") is False, "true-dynamic superiority overclaim")
    checks.check(strict_common.get("strict_common_reference_error_columns") is True, "strict common-reference columns missing")
    checks.check(strict_common.get("external_superiority_claim") is False, "strict common-reference superiority overclaim")

    checks.check(external_gate.get("acceptance_sheet") == "EXTERNAL_SAME_TEST_ACCEPTANCE_SHEET.md", "external gate missing sheet path")
    checks.check(
        external_gate.get("acceptance_sheet_json") == "EXTERNAL_SAME_TEST_ACCEPTANCE_SHEET.json",
        "external gate missing sheet JSON path",
    )
    checks.check(
        external_gate.get("acceptance_counts", {}).get("parallel_shard_count_without_default_1e-4") == 20,
        "external gate acceptance shard count changed",
    )
    checks.check(
        external_gate.get("acceptance_counts", {}).get("accepted_external_dynamic_order_examples_count") == 0,
        "external gate accepted external order count changed",
    )
    checks.check(
        external_gate.get("execution_policy", {}).get("default_1e-4_required") is False,
        "external gate default 1e-4 marker changed",
    )
    checks.check(cross_cases.get("same_test_campaign_status") == "not_run", "cross cases campaign overclaim")
    checks.check(cross_cases.get("external_superiority_claim") is False, "cross cases superiority overclaim")
    checks.check(cross_cases.get("default_1e-4_required") is False, "cross cases default 1e-4 overclaim")

    checks.check("external_same_test_acceptance_sheet_added" in b2.get("partial_progress", []), "B2 lost acceptance progress marker")
    checks.check("EXTERNAL_SAME_TEST_ACCEPTANCE_SHEET.md" in b2.get("partial_progress_evidence", []), "B2 sheet evidence missing")
    checks.check("EXTERNAL_SAME_TEST_ACCEPTANCE_SHEET.json" in b2.get("partial_progress_evidence", []), "B2 sheet JSON evidence missing")
    checks.check(
        "validate_external_same_test_acceptance_sheet.py" in b2.get("partial_progress_evidence", []),
        "B2 sheet validator evidence missing",
    )
    checks.check("fair_baseline_acceptance_sheet_added" in b4.get("partial_progress", []), "B4 lost acceptance progress marker")
    checks.check("EXTERNAL_SAME_TEST_ACCEPTANCE_SHEET.md" in b4.get("partial_progress_evidence", []), "B4 sheet evidence missing")
    checks.check("EXTERNAL_SAME_TEST_ACCEPTANCE_SHEET.json" in b4.get("partial_progress_evidence", []), "B4 sheet JSON evidence missing")

    checks.check(
        manifest.get("external_same_test_acceptance_sheet") == "EXTERNAL_SAME_TEST_ACCEPTANCE_SHEET.md",
        "manifest sheet path missing",
    )
    checks.check(
        manifest.get("external_same_test_acceptance_sheet_json") == "EXTERNAL_SAME_TEST_ACCEPTANCE_SHEET.json",
        "manifest sheet JSON path missing",
    )
    checks.check("EXTERNAL_SAME_TEST_ACCEPTANCE_SHEET.md" in manifest.get("evidence_anchors", []), "manifest sheet anchor missing")
    checks.check("EXTERNAL_SAME_TEST_ACCEPTANCE_SHEET.json" in manifest.get("evidence_anchors", []), "manifest sheet JSON anchor missing")
    checks.check(
        "validate_external_same_test_acceptance_sheet.py" in manifest.get("validators", []),
        "manifest sheet validator missing",
    )

    require_tokens(
        checks,
        sheet_md,
        [
            "External Same-Test Acceptance Sheet",
            "ACCEPTANCE REQUIREMENTS DEFINED - CAMPAIGN NOT RUN",
            "coarse_first_no_default_1e-4",
            "strict public-policy `1e-4`: `opt_in_only`",
            "`default_1e-4_required=false`",
            "`heavy_numerical_run_invoked=false`",
            "`run_v047_invoked=false`",
            "`v048_runner_invoked=false`",
            "`same_test_campaign_status=not_run`",
            "`external_superiority_claim=false`",
            "local evidence coverage examples: `4/4`",
            "accepted method dynamic-order examples: `2/4`",
            "mechanism-coverage examples: `2/4`",
            "accepted source-policy dynamic-order examples: `0/4`",
            "parallel shards without default `1e-4`: `20`",
            "Residual-only rows do not count as dynamic order",
            "Neither B2 nor B4 requires a default `1e-4` campaign",
            "h=[0.1,0.05,0.025]",
            "reference `h=0.0125`",
            "validate_external_same_test_acceptance_sheet.py",
        ],
        "EXTERNAL_SAME_TEST_ACCEPTANCE_SHEET.md",
    )

    if checks.errors:
        print("external_same_test_acceptance_sheet=FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("external_same_test_acceptance_sheet=PASS")
    print(f"same_test_campaign_status={sheet.get('same_test_campaign_status')}")
    print(
        "accepted_external_dynamic_order_examples="
        f"{counts.get('accepted_external_dynamic_order_examples_count')}"
    )
    print(f"local_evidence_coverage_examples={counts.get('local_evidence_coverage_examples_count')}/4")
    print(
        "accepted_method_dynamic_order_examples="
        f"{counts.get('accepted_method_dynamic_order_examples_count')}/4"
    )
    print(f"mechanism_coverage_examples={counts.get('mechanism_coverage_examples_count')}/4")
    print(
        "source_policy_dynamic_order_examples="
        f"{counts.get('accepted_source_policy_dynamic_order_examples_count')}/4"
    )
    print(
        "parallel_shard_count_without_default_1e-4="
        f"{counts.get('parallel_shard_count_without_default_1e-4')}"
    )
    print(f"default_1e-4={execution.get('default_1e-4_required')}")
    print(f"heavy_numerical_run_invoked={execution.get('heavy_numerical_run_invoked')}")
    print(f"external_superiority_claim={sheet.get('external_superiority_claim')}")
    print(f"submission_ready={sheet.get('submission_ready')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
