#!/usr/bin/env python3
"""Read-only validator for the CMAME external-baseline gate."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
ROOT = PAPER.parent
V048 = ROOT / "v048_cross_paper_same_test_benchmarks" / "results"
GATE_JSON = PAPER / "CMAME_EXTERNAL_BASELINE_GATE.json"
GATE_MD = PAPER / "CMAME_EXTERNAL_BASELINE_GATE.md"
MANIFEST = PAPER / "SUBMISSION_ARTIFACT_MANIFEST.json"
BLOCKER_GATE = PAPER / "CMAME_BLOCKER_CLOSURE_GATE.json"
CROSS_SPEC = PAPER / "CROSS_PAPER_BENCHMARK_SPEC.md"
CROSS_CASES = PAPER / "CROSS_PAPER_BENCHMARK_CASES.json"
RUN_QUEUE_JSON = PAPER / "EXTERNAL_SAME_TEST_RUN_QUEUE.json"
RUN_QUEUE_MD = PAPER / "EXTERNAL_SAME_TEST_RUN_QUEUE.md"
ACCEPTANCE_SHEET_JSON = PAPER / "EXTERNAL_SAME_TEST_ACCEPTANCE_SHEET.json"
ACCEPTANCE_SHEET_MD = PAPER / "EXTERNAL_SAME_TEST_ACCEPTANCE_SHEET.md"
HI2022_AUDIT_JSON = PAPER / "HI2022_POLICY_DECISION_AUDIT.json"
HI2022_AUDIT_MD = PAPER / "HI2022_POLICY_DECISION_AUDIT.md"
COMPARISON_RECONCILIATION_JSON = PAPER / "COMPARISON_OBJECTIVE_CLOSURE_RECONCILIATION_AUDIT.json"
COMPARISON_RECONCILIATION_MD = PAPER / "COMPARISON_OBJECTIVE_CLOSURE_RECONCILIATION_AUDIT.md"
ALL_SOURCE_POLICY_JSON = PAPER / "ALL_EXAMPLES_SOURCE_POLICY_AUDIT.json"
ALL_SOURCE_POLICY_MD = PAPER / "ALL_EXAMPLES_SOURCE_POLICY_AUDIT.md"
READINESS_REVIEW = PAPER / "CMAME_SUBMISSION_READINESS_REVIEW.md"
COARSE_FIRST = V048 / "coarse_first_external_readiness_gate.json"
PERFORMANCE = V048 / "four_example_performance_summary.json"
R2E = V048 / "closed_loop_residual_to_error_theorem_obligations.json"
PLAN_CSV = V048 / "closed_loop_true_dynamic_local_row_plan.csv"
PLAN_JSON = V048 / "closed_loop_true_dynamic_local_row_plan.json"
PLAN_MD = V048 / "closed_loop_true_dynamic_local_row_plan.md"
INTERFACE_CSV = V048 / "closed_loop_true_dynamic_interface_audit.csv"
INTERFACE_JSON = V048 / "closed_loop_true_dynamic_interface_audit.json"
INTERFACE_MD = V048 / "closed_loop_true_dynamic_interface_audit.md"
SCAFFOLD_CSV = V048 / "closed_loop_true_dynamic_residual_scaffold.csv"
SCAFFOLD_JSON = V048 / "closed_loop_true_dynamic_residual_scaffold.json"
SCAFFOLD_MD = V048 / "closed_loop_true_dynamic_residual_scaffold.md"
STAGE_AUDIT_CSV = V048 / "closed_loop_true_dynamic_stage_residual_audit.csv"
STAGE_AUDIT_JSON = V048 / "closed_loop_true_dynamic_stage_residual_audit.json"
STAGE_AUDIT_MD = V048 / "closed_loop_true_dynamic_stage_residual_audit.md"
ONE_STEP_CSV = V048 / "closed_loop_true_dynamic_one_step_smoke.csv"
ONE_STEP_JSON = V048 / "closed_loop_true_dynamic_one_step_smoke.json"
ONE_STEP_MD = V048 / "closed_loop_true_dynamic_one_step_smoke.md"
NEWTON_STAGE_CSV = V048 / "closed_loop_true_dynamic_newton_stage_smoke.csv"
NEWTON_STAGE_JSON = V048 / "closed_loop_true_dynamic_newton_stage_smoke.json"
NEWTON_STAGE_MD = V048 / "closed_loop_true_dynamic_newton_stage_smoke.md"
NEWTON_COARSE_CSV = V048 / "closed_loop_true_dynamic_newton_coarse_order_rows.csv"
NEWTON_COARSE_JSON = V048 / "closed_loop_true_dynamic_newton_coarse_order.json"
NEWTON_COARSE_MD = V048 / "closed_loop_true_dynamic_newton_coarse_order.md"
PUBLIC_WORK_ROWS_CSV = V048 / "closed_loop_true_dynamic_public_work_precision_rows.csv"
PUBLIC_WORK_SUMMARY_CSV = V048 / "closed_loop_true_dynamic_public_work_precision_summary.csv"
PUBLIC_WORK_JSON = V048 / "closed_loop_true_dynamic_public_work_precision.json"
PUBLIC_WORK_MD = V048 / "closed_loop_true_dynamic_public_work_precision.md"
STRICT_COMMON_ROWS_CSV = V048 / "closed_loop_true_dynamic_strict_common_reference_rows.csv"
STRICT_COMMON_SUMMARY_CSV = V048 / "closed_loop_true_dynamic_strict_common_reference_summary.csv"
STRICT_COMMON_JSON = V048 / "closed_loop_true_dynamic_strict_common_reference.json"
STRICT_COMMON_MD = V048 / "closed_loop_true_dynamic_strict_common_reference.md"
STRICT_COMMON_FIGURE = V048 / "closed_loop_true_dynamic_strict_common_reference_work_precision.png"

EXAMPLES = ["single_pendulum", "double_pendulum", "four_link", "slider_crank"]
COARSE_READY = ["single_pendulum", "double_pendulum"]
CLOSED_LOOP_MODELS = ["four_link", "slider_crank"]
SURROGATE_ONLY: list[str] = []


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


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(path)
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


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
        gate = read_json(GATE_JSON)
        gate_md = read_text(GATE_MD)
        manifest = read_json(MANIFEST)
        blocker_gate = read_json(BLOCKER_GATE)
        cross_spec = read_text(CROSS_SPEC)
        cross_cases = read_json(CROSS_CASES)
        run_queue = read_json(RUN_QUEUE_JSON)
        run_queue_md = read_text(RUN_QUEUE_MD)
        acceptance_sheet = read_json(ACCEPTANCE_SHEET_JSON)
        acceptance_sheet_md = read_text(ACCEPTANCE_SHEET_MD)
        hi2022_audit = read_json(HI2022_AUDIT_JSON)
        hi2022_audit_md = read_text(HI2022_AUDIT_MD)
        comparison_reconciliation_audit = read_json(COMPARISON_RECONCILIATION_JSON)
        comparison_reconciliation_md = read_text(COMPARISON_RECONCILIATION_MD)
        all_source_policy = read_json(ALL_SOURCE_POLICY_JSON)
        all_source_policy_md = read_text(ALL_SOURCE_POLICY_MD)
        readiness_review = read_text(READINESS_REVIEW)
        coarse_first = read_json(COARSE_FIRST)
        performance = read_json(PERFORMANCE)
        r2e = read_json(R2E)
        plan = read_json(PLAN_JSON)
        plan_rows = read_csv_rows(PLAN_CSV)
        plan_md = read_text(PLAN_MD)
        interface = read_json(INTERFACE_JSON)
        interface_rows = read_csv_rows(INTERFACE_CSV)
        interface_md = read_text(INTERFACE_MD)
        scaffold = read_json(SCAFFOLD_JSON)
        scaffold_rows = read_csv_rows(SCAFFOLD_CSV)
        scaffold_md = read_text(SCAFFOLD_MD)
        stage_audit = read_json(STAGE_AUDIT_JSON)
        stage_audit_rows = read_csv_rows(STAGE_AUDIT_CSV)
        stage_audit_md = read_text(STAGE_AUDIT_MD)
        one_step = read_json(ONE_STEP_JSON)
        one_step_rows = read_csv_rows(ONE_STEP_CSV)
        one_step_md = read_text(ONE_STEP_MD)
        newton_stage = read_json(NEWTON_STAGE_JSON)
        newton_stage_rows = read_csv_rows(NEWTON_STAGE_CSV)
        newton_stage_md = read_text(NEWTON_STAGE_MD)
        newton_coarse = read_json(NEWTON_COARSE_JSON)
        newton_coarse_rows = read_csv_rows(NEWTON_COARSE_CSV)
        newton_coarse_md = read_text(NEWTON_COARSE_MD)
        public_work = read_json(PUBLIC_WORK_JSON)
        public_work_rows = read_csv_rows(PUBLIC_WORK_ROWS_CSV)
        public_work_summary_rows = read_csv_rows(PUBLIC_WORK_SUMMARY_CSV)
        public_work_md = read_text(PUBLIC_WORK_MD)
        strict_common = read_json(STRICT_COMMON_JSON)
        strict_common_rows = read_csv_rows(STRICT_COMMON_ROWS_CSV)
        strict_common_summary_rows = read_csv_rows(STRICT_COMMON_SUMMARY_CSV)
        strict_common_md = read_text(STRICT_COMMON_MD)
    except Exception as exc:  # noqa: BLE001 - concise CLI failure.
        print(f"cmame_external_baseline_gate=FAIL\n- {exc}")
        return 1

    execution = gate.get("execution_policy", {})
    same_test = gate.get("same_test_boundary", {})
    cross_case_inventory = gate.get("cross_case_inventory_boundary", {})
    comparison_reconciliation = gate.get("comparison_reconciliation", {})
    source_policy_audit = gate.get("source_policy_audit", {})
    hi2022_policy_decision = gate.get("hi2022_policy_decision_audit", {})
    suite_status = gate.get("suite_status", {})
    next_batch = gate.get("next_parallel_batch", {})
    source_files = gate.get("source_files", {})
    acceptance_counts = gate.get("acceptance_counts", {})
    row_plan_artifacts = next_batch.get("row_plan_artifacts", {})
    row_plan_summary = next_batch.get("row_plan_summary", {})
    interface_artifacts = next_batch.get("dynamic_interface_audit_artifacts", {})
    interface_summary = next_batch.get("dynamic_interface_audit_summary", {})
    scaffold_artifacts = next_batch.get("true_dynamic_residual_scaffold_artifacts", {})
    scaffold_summary = next_batch.get("true_dynamic_residual_scaffold_summary", {})
    stage_audit_artifacts = next_batch.get("true_dynamic_stage_residual_audit_artifacts", {})
    stage_audit_summary = next_batch.get("true_dynamic_stage_residual_audit_summary", {})
    one_step_artifacts = next_batch.get("true_dynamic_one_step_smoke_artifacts", {})
    one_step_summary = next_batch.get("true_dynamic_one_step_smoke_summary", {})
    newton_stage_artifacts = next_batch.get("true_dynamic_newton_stage_smoke_artifacts", {})
    newton_stage_summary = next_batch.get("true_dynamic_newton_stage_smoke_summary", {})
    newton_coarse_artifacts = next_batch.get("true_dynamic_newton_coarse_order_artifacts", {})
    newton_coarse_summary = next_batch.get("true_dynamic_newton_coarse_order_summary", {})
    public_work_artifacts = next_batch.get("true_dynamic_public_work_precision_artifacts", {})
    public_work_summary = next_batch.get("true_dynamic_public_work_precision_summary", {})
    strict_common_artifacts = next_batch.get("true_dynamic_strict_common_reference_artifacts", {})
    strict_common_summary = next_batch.get("true_dynamic_strict_common_reference_summary", {})
    b2 = blocker_by_id(blocker_gate, "B2")

    checks.check(gate.get("schema") == "cmame-external-baseline-gate-v1", "schema changed")
    checks.check(gate.get("status") == "open_not_submission_ready", "status changed")
    checks.check(gate.get("submission_ready") is False, "gate must not claim submission ready")
    checks.check(gate.get("accepted_method") == "Gauss6/FullVA", "accepted method changed")
    checks.check(gate.get("accepted_method_order") == 6, "accepted method order changed")
    checks.check(gate.get("comparator_expected_order") == 5, "comparator order changed")

    checks.check(execution.get("default_step_policy") == "coarse_first_no_default_1e-4", "default policy changed")
    checks.check(execution.get("coarse_step_sizes") == [0.1, 0.05, 0.025], "coarse step sizes changed")
    checks.check(execution.get("coarse_reference_h") == 0.0125, "coarse reference changed")
    checks.check(execution.get("strict_public_policy_1e-4") == "opt_in_only", "strict public policy changed")
    checks.check(execution.get("default_1e-4_required") is False, "gate incorrectly requires default 1e-4")
    checks.check(execution.get("heavy_numerical_run_invoked_by_gate") is False, "gate must remain read-only")

    checks.check(same_test.get("same_test_campaign_status") == "not_run", "same-test status changed")
    checks.check(same_test.get("external_superiority_claim") is False, "external superiority overclaim")
    checks.check(same_test.get("full_external_same_test_campaign_passed") is False, "same-test pass overclaim")
    checks.check(same_test.get("comparison_matrix_closed") is True, "same-test comparison matrix closure changed")
    checks.check(same_test.get("common_reference_claim_allowed") is True, "same-test common-reference claim boundary changed")
    checks.check(
        same_test.get("source_policy_superiority_claim_allowed") is False,
        "same-test source-policy superiority boundary changed",
    )
    checks.check(same_test.get("common_reference_examples") == EXAMPLES, "same-test common-reference examples changed")
    checks.check(same_test.get("common_reference_cells") == 44, "same-test common-reference cells changed")
    checks.check(same_test.get("raw_rows_recomputed") == 132, "same-test raw row count changed")
    checks.check(same_test.get("summary_mismatches") == 0, "same-test summary mismatch count changed")
    checks.check(same_test.get("direct_nonlocal_velocity_order_wins") == 40, "same-test order wins changed")
    checks.check(same_test.get("direct_nonlocal_velocity_order_comparisons") == 40, "same-test order comparisons changed")
    checks.check(same_test.get("direct_nonlocal_finest_velocity_error_wins") == 40, "same-test error wins changed")
    checks.check(same_test.get("direct_nonlocal_finest_velocity_error_comparisons") == 40, "same-test error comparisons changed")
    checks.check(same_test.get("source_policy_flagged_rows") == 15, "same-test source-policy flagged count changed")
    checks.check(same_test.get("source_policy_velocity_mismatch_rows") == 10, "same-test source-policy velocity mismatch count changed")
    checks.check(
        same_test.get("all_examples_source_policy_audit_status") == all_source_policy.get("status"),
        "same-test all-example source-policy status changed",
    )
    checks.check(
        same_test.get("all_examples_source_policy_flagged_rows")
        == all_source_policy.get("coverage", {}).get("flagged_row_count")
        == 15,
        "same-test all-example source-policy flagged count changed",
    )
    checks.check(
        same_test.get("all_examples_source_policy_flagged_raw_rows")
        == all_source_policy.get("coverage", {}).get("flagged_raw_row_count")
        == 45,
        "same-test all-example source-policy raw-row count changed",
    )
    checks.check(
        same_test.get("all_examples_source_policy_all_four_examples") is True,
        "same-test all-example source-policy coverage marker changed",
    )
    checks.check(
        same_test.get("all_examples_source_policy_all_three_step_sizes") is True,
        "same-test all-example source-policy h marker changed",
    )
    checks.check(same_test.get("source_policy_reproduction_open") is True, "same-test source-policy reproduction boundary changed")
    checks.check(same_test.get("paper_submission_b2_b4_can_close_now") is False, "same-test incorrectly closes B2/B4")
    checks.check(same_test.get("coarse_same_window_ready_count") == 2, "coarse-ready count changed")
    checks.check(same_test.get("local_true_dynamic_order_available_count") == 2, "closed-loop coarse-dynamics diagnostic count changed")
    checks.check(same_test.get("dynamic_order_missing_count") == 0, "dynamic-order missing count changed")
    checks.check(same_test.get("public_work_precision_available_count") == 2, "public work/precision availability count changed")
    checks.check(same_test.get("public_work_precision_missing_count") == 0, "public work/precision missing count changed")
    checks.check(same_test.get("strict_common_reference_available_count") == 2, "strict common-reference availability count changed")
    checks.check(same_test.get("strict_common_reference_gap_count") == 0, "strict common-reference gap count changed")
    checks.check(same_test.get("strict_common_reference_figure_available") is True, "strict common-reference figure marker changed")
    checks.check(
        same_test.get("strict_common_reference_figure_integrated_in_manuscript") is True,
        "strict common-reference manuscript integration marker changed",
    )
    checks.check(same_test.get("coarse_first_order_time_examples") == COARSE_READY, "coarse-ready examples changed")
    checks.check(same_test.get("surrogate_only_examples") == SURROGATE_ONLY, "surrogate-only examples changed")
    checks.check(
        same_test.get("local_true_dynamic_order_examples") == CLOSED_LOOP_MODELS,
        "closed-loop coarse-dynamics diagnostic examples changed",
    )
    checks.check(
        same_test.get("public_work_precision_available_examples") == CLOSED_LOOP_MODELS,
        "public work/precision available examples changed",
    )
    checks.check(
        same_test.get("public_work_precision_missing_examples") == [],
        "public work/precision missing examples changed",
    )
    checks.check(
        same_test.get("strict_common_reference_available_examples") == CLOSED_LOOP_MODELS,
        "strict common-reference available examples changed",
    )
    checks.check(
        same_test.get("strict_common_reference_gap_examples") == [],
        "strict common-reference gap examples changed",
    )
    checks.check(same_test.get("accepted_external_dynamic_order_examples") == [], "external dynamic order overclaim")
    checks.check(same_test.get("closed_loop_residual_to_error_accepted") is False, "residual-to-error overclaim")
    checks.check(
        comparison_reconciliation_audit.get("schema") == "comparison-objective-closure-reconciliation-v1",
        "comparison reconciliation audit schema changed",
    )
    checks.check(
        comparison_reconciliation_audit.get("status")
        == "common_reference_objective_closed_source_policy_reproduction_open",
        "comparison reconciliation audit status changed",
    )
    checks.check(
        comparison_reconciliation.get("artifact") == "COMPARISON_OBJECTIVE_CLOSURE_RECONCILIATION_AUDIT.md",
        "comparison reconciliation artifact path changed",
    )
    checks.check(
        comparison_reconciliation.get("artifact_json") == "COMPARISON_OBJECTIVE_CLOSURE_RECONCILIATION_AUDIT.json",
        "comparison reconciliation JSON path changed",
    )
    checks.check(
        comparison_reconciliation.get("validator") == "validate_comparison_objective_closure_reconciliation_audit.py",
        "comparison reconciliation validator path changed",
    )
    checks.check(
        comparison_reconciliation.get("status") == comparison_reconciliation_audit.get("status"),
        "comparison reconciliation status mismatch",
    )
    checks.check(
        comparison_reconciliation.get("comparison_matrix_closed")
        == comparison_reconciliation_audit.get("comparison_matrix_closed")
        is True,
        "comparison matrix closure mismatch",
    )
    checks.check(
        comparison_reconciliation.get("common_reference_claim_allowed")
        == comparison_reconciliation_audit.get("common_reference_claim_allowed")
        is True,
        "common-reference claim boundary mismatch",
    )
    checks.check(
        comparison_reconciliation.get("source_policy_superiority_claim_allowed")
        == comparison_reconciliation_audit.get("source_policy_superiority_claim_allowed")
        is False,
        "source-policy superiority boundary mismatch",
    )
    checks.check(comparison_reconciliation.get("common_reference_examples") == EXAMPLES, "comparison examples changed")
    checks.check(comparison_reconciliation.get("common_reference_cells") == 44, "comparison cell count changed")
    checks.check(comparison_reconciliation.get("raw_rows_recomputed") == 132, "comparison raw row count changed")
    checks.check(comparison_reconciliation.get("summary_mismatches") == 0, "comparison mismatch count changed")
    checks.check(
        comparison_reconciliation.get("direct_nonlocal_velocity_order_wins")
        == comparison_reconciliation.get("direct_nonlocal_velocity_order_comparisons")
        == comparison_reconciliation_audit.get("direct_nonlocal_velocity_order_wins")
        == 40,
        "direct nonlocal order win count changed",
    )
    checks.check(
        comparison_reconciliation.get("direct_nonlocal_finest_velocity_error_wins")
        == comparison_reconciliation.get("direct_nonlocal_finest_velocity_error_comparisons")
        == comparison_reconciliation_audit.get("direct_nonlocal_finest_velocity_error_wins")
        == 40,
        "direct nonlocal finest-error win count changed",
    )
    checks.check(
        comparison_reconciliation.get("original_paper_velocity_error_wins")
        == comparison_reconciliation.get("original_paper_velocity_error_comparisons")
        == 16,
        "original-paper error win count changed",
    )
    checks.check(
        comparison_reconciliation.get("kissel_negrut_velocity_error_wins")
        == comparison_reconciliation.get("kissel_negrut_velocity_error_comparisons")
        == 24,
        "Kissel/Negrut error win count changed",
    )
    checks.check(
        comparison_reconciliation.get("source_policy_flagged_rows")
        == comparison_reconciliation_audit.get("source_policy_flagged_rows")
        == 15,
        "source-policy flagged count changed",
    )
    checks.check(
        comparison_reconciliation.get("source_policy_velocity_mismatch_rows")
        == comparison_reconciliation_audit.get("source_policy_velocity_mismatch_rows")
        == 10,
        "source-policy velocity mismatch count changed",
    )
    checks.check(
        comparison_reconciliation.get("paper_submission_b2_b4_can_close_now") is False,
        "comparison reconciliation incorrectly closes B2/B4",
    )
    require_tokens(
        checks,
        comparison_reconciliation_md,
        [
            "Comparison matrix closed: `True`",
            "Direct nonlocal velocity-order wins: `40/40`",
            "Direct nonlocal finest-velocity-error wins: `40/40`",
            "B2/B4 can close now: `False`",
        ],
        "COMPARISON_OBJECTIVE_CLOSURE_RECONCILIATION_AUDIT.md",
    )
    checks.check(
        source_policy_audit.get("artifact") == "ALL_EXAMPLES_SOURCE_POLICY_AUDIT.md",
        "all-example source-policy artifact path changed",
    )
    checks.check(
        source_policy_audit.get("artifact_json") == "ALL_EXAMPLES_SOURCE_POLICY_AUDIT.json",
        "all-example source-policy JSON path changed",
    )
    checks.check(
        source_policy_audit.get("validator") == "validate_all_examples_source_policy_audit.py",
        "all-example source-policy validator changed",
    )
    checks.check(source_policy_audit.get("status") == all_source_policy.get("status"), "all-example source-policy status mismatch")
    checks.check(
        source_policy_audit.get("flagged_rows")
        == all_source_policy.get("coverage", {}).get("flagged_row_count")
        == 15,
        "all-example source-policy flagged rows mismatch",
    )
    checks.check(
        source_policy_audit.get("flagged_raw_rows")
        == all_source_policy.get("coverage", {}).get("flagged_raw_row_count")
        == 45,
        "all-example source-policy raw rows mismatch",
    )
    checks.check(source_policy_audit.get("all_four_examples_covered") is True, "all-example source-policy examples changed")
    checks.check(
        source_policy_audit.get("all_flagged_rows_have_three_step_sizes") is True,
        "all-example source-policy step sizes changed",
    )
    checks.check(source_policy_audit.get("source_policy_reproduction_open") is True, "all-example source-policy boundary changed")
    checks.check(source_policy_audit.get("b2_can_close_now") is False, "all-example source-policy incorrectly closes B2")
    checks.check(source_policy_audit.get("b4_can_close_now") is False, "all-example source-policy incorrectly closes B4")
    checks.check(source_policy_audit.get("default_1e_4_required") is False, "all-example source-policy default 1e-4 changed")
    checks.check(source_policy_audit.get("heavy_numerical_run_invoked") is False, "all-example source-policy invoked heavy run")
    require_tokens(
        checks,
        all_source_policy_md,
        [
            "Flagged rows checked: `15`",
            "Flagged raw rows checked: `45`",
            "All four examples covered: `True`",
            "B2/B4 can close now: `False/False`",
        ],
        "ALL_EXAMPLES_SOURCE_POLICY_AUDIT.md",
    )
    checks.check(
        hi2022_audit.get("schema") == "hi2022-policy-decision-audit-v1",
        "HI2022 policy decision audit schema changed",
    )
    checks.check(
        hi2022_audit.get("status") == "bounded_T0p1_rows_complete_full_T8_source_policy_open",
        "HI2022 policy decision audit status changed",
    )
    hi_existing = hi2022_audit.get("existing_bounded_evidence", {})
    hi_source_policy = hi2022_audit.get("source_policy_required_before_external_superiority", {})
    hi_queue = hi2022_audit.get("queue_policy_decision", {})
    hi_execution = hi2022_audit.get("execution_policy", {})
    checks.check(hi_existing.get("row_count") == 24, "HI2022 audit bounded row count changed")
    checks.check(hi_existing.get("ok_row_count") == 24, "HI2022 audit bounded ok row count changed")
    checks.check(hi_existing.get("groups_with_three_step_sizes") == 8, "HI2022 audit bounded group count changed")
    checks.check(hi_existing.get("t_end_values") == [0.1], "HI2022 audit bounded horizon changed")
    checks.check(hi_existing.get("step_sizes") == [0.005, 0.01, 0.02], "HI2022 audit h-grid changed")
    checks.check(hi_source_policy.get("full_T8_policy_required") is True, "HI2022 audit lost full-T8 requirement")
    checks.check(hi_source_policy.get("full_T8_policy_completed") is False, "HI2022 audit overclaims full T8 policy")
    checks.check(
        hi_source_policy.get("accepted_for_bounded_evidence") is True,
        "HI2022 audit bounded evidence acceptance changed",
    )
    checks.check(
        hi_source_policy.get("accepted_for_external_superiority") is False,
        "HI2022 audit overclaims external superiority",
    )
    checks.check(
        hi_source_policy.get("accepted_source_policy_dynamic_order_examples_count") == 0,
        "HI2022 audit source-policy dynamic-order count changed",
    )
    checks.check(hi_queue.get("parallel_shard_count") == 8, "HI2022 audit parallel shard count changed")
    checks.check(hi_execution.get("default_1e_4_required") is False, "HI2022 audit default 1e-4 changed")
    checks.check(hi_execution.get("heavy_numerical_run_invoked") is False, "HI2022 audit invoked heavy run")
    checks.check(hi_execution.get("run_v047_invoked") is False, "HI2022 audit invoked run_v047")
    checks.check(
        hi2022_policy_decision.get("artifact") == "HI2022_POLICY_DECISION_AUDIT.md",
        "gate missing HI2022 audit artifact",
    )
    checks.check(
        hi2022_policy_decision.get("artifact_json") == "HI2022_POLICY_DECISION_AUDIT.json",
        "gate missing HI2022 audit JSON artifact",
    )
    checks.check(
        hi2022_policy_decision.get("validator") == "validate_hi2022_policy_decision_audit.py",
        "gate missing HI2022 audit validator",
    )
    checks.check(
        hi2022_policy_decision.get("status") == hi2022_audit.get("status"),
        "gate HI2022 audit status mismatch",
    )
    checks.check(
        hi2022_policy_decision.get("bounded_row_count") == hi_existing.get("row_count") == 24,
        "gate HI2022 bounded row count mismatch",
    )
    checks.check(
        hi2022_policy_decision.get("bounded_ok_row_count") == hi_existing.get("ok_row_count") == 24,
        "gate HI2022 bounded ok row count mismatch",
    )
    checks.check(
        hi2022_policy_decision.get("bounded_groups_with_three_step_sizes")
        == hi_existing.get("groups_with_three_step_sizes")
        == 8,
        "gate HI2022 bounded group count mismatch",
    )
    checks.check(
        hi2022_policy_decision.get("full_T8_policy_completed")
        == hi_source_policy.get("full_T8_policy_completed")
        is False,
        "gate HI2022 full-T8 policy boundary mismatch",
    )
    checks.check(
        hi2022_policy_decision.get("accepted_for_external_superiority")
        == hi_source_policy.get("accepted_for_external_superiority")
        is False,
        "gate HI2022 external superiority boundary mismatch",
    )
    checks.check(
        hi2022_policy_decision.get("accepted_source_policy_dynamic_order_examples_count")
        == hi_source_policy.get("accepted_source_policy_dynamic_order_examples_count")
        == 0,
        "gate HI2022 source-policy dynamic-order mismatch",
    )
    checks.check(
        hi2022_policy_decision.get("local_evidence_coverage_examples_count") == 4,
        "gate HI2022 local evidence coverage count mismatch",
    )
    checks.check(
        hi2022_policy_decision.get("accepted_method_dynamic_order_examples_count") == 2,
        "gate HI2022 accepted method dynamic-order count mismatch",
    )
    checks.check(
        hi2022_policy_decision.get("mechanism_coverage_examples_count") == 2,
        "gate HI2022 mechanism coverage count mismatch",
    )
    checks.check(
        hi2022_policy_decision.get("parallel_shard_count_after_policy_selection")
        == hi_queue.get("parallel_shard_count")
        == 8,
        "gate HI2022 shard count mismatch",
    )
    checks.check(
        hi2022_policy_decision.get("default_1e_4_required") is False
        and hi2022_policy_decision.get("heavy_numerical_run_invoked") is False
        and hi2022_policy_decision.get("run_v047_invoked") is False,
        "gate HI2022 execution-policy boundary changed",
    )
    require_tokens(
        checks,
        hi2022_audit_md,
        [
            "rows ok: `24/24`",
            "model/form groups with three h values: `8/8`",
            "local evidence coverage examples carried from dashboard: `4/4`",
            "accepted method dynamic-order examples carried from dashboard: `2/4`",
            "mechanism-coverage examples carried from dashboard: `2/4`",
            "source-policy dynamic-order examples: `0/4`",
            "external-superiority claim allowed: `False`",
        ],
        "HI2022_POLICY_DECISION_AUDIT.md",
    )
    require_tokens(
        checks,
        gate_md,
        [
            "HI2022_POLICY_DECISION_AUDIT.md/json",
            "bounded rows and `8/8` model/form groups",
            "source-policy dynamic-order examples remain",
            "`choose_full_T8_reproduction_or_explicit_demotion`",
        ],
        "CMAME_EXTERNAL_BASELINE_GATE.md",
    )
    checks.check(
        cross_case_inventory.get("status") == "spec_extracted_partial_evidence_not_full_campaign",
        "cross-case inventory boundary status changed",
    )
    checks.check(cross_case_inventory.get("same_test_campaign_status") == "not_run", "cross-case boundary overclaim")
    checks.check(
        cross_case_inventory.get("external_superiority_claim") is False,
        "cross-case boundary superiority overclaim",
    )
    checks.check(
        cross_case_inventory.get("full_external_same_test_campaign_passed") is False,
        "cross-case boundary full campaign overclaim",
    )
    checks.check(
        cross_case_inventory.get("default_1e-4_required") is False,
        "cross-case boundary default 1e-4 overclaim",
    )
    checks.check(
        cross_case_inventory.get("partial_evidence_overlay_required") is True,
        "cross-case boundary lost overlay requirement",
    )
    checks.check(next_batch.get("status") == "design_required_before_execution", "next batch status changed")
    checks.check(next_batch.get("default_1e-4_required") is False, "next batch incorrectly requires default 1e-4")
    checks.check(
        next_batch.get("external_same_test_run_queue") == "EXTERNAL_SAME_TEST_RUN_QUEUE.json",
        "next batch lost external run queue path",
    )
    checks.check(
        next_batch.get("parallel_shard_count_without_default_1e-4") == 20,
        "next batch parallel shard count changed",
    )
    checks.check(
        next_batch.get("target") == "close_remaining_external_suites_or_demote_external_superiority_claim",
        "next batch target changed",
    )
    checks.check(next_batch.get("new_code_required") is True, "next batch must record new code requirement")
    checks.check(row_plan_artifacts.get("status") == "plan_only_not_run", "row plan artifact status changed")
    checks.check(
        row_plan_artifacts.get("json")
        == "../v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_local_row_plan.json",
        "row plan JSON path changed",
    )
    checks.check(
        row_plan_artifacts.get("csv")
        == "../v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_local_row_plan.csv",
        "row plan CSV path changed",
    )
    checks.check(
        row_plan_artifacts.get("markdown")
        == "../v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_local_row_plan.md",
        "row plan markdown path changed",
    )
    checks.check(
        row_plan_artifacts.get("validator")
        == "../v048_cross_paper_same_test_benchmarks/validate_closed_loop_true_dynamic_local_row_plan.py",
        "row plan validator path changed",
    )
    checks.check(row_plan_summary.get("plan_only") is True, "row plan must remain plan-only")
    checks.check(row_plan_summary.get("row_count") == 24, "row plan summary row count changed")
    checks.check(row_plan_summary.get("local_target_row_count") == 6, "row plan local target count changed")
    checks.check(row_plan_summary.get("public_comparator_row_count") == 18, "row plan public comparator count changed")
    checks.check(row_plan_summary.get("true_dynamic_local_rows_available") == 0, "row plan true rows overclaimed")
    checks.check(row_plan_summary.get("accepted_dynamic_order_count") == 0, "row plan accepted order overclaimed")
    checks.check(row_plan_summary.get("strict_public_policy_1e-4_required") is False, "row plan strict 1e-4 overclaimed")
    checks.check(row_plan_summary.get("heavy_numerical_run_invoked") is False, "row plan invoked heavy numerical run")
    checks.check(
        interface_artifacts.get("status") == "setup_level_interface_verified_no_trajectory_run",
        "interface audit artifact status changed",
    )
    checks.check(
        interface_artifacts.get("json")
        == "../v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_interface_audit.json",
        "interface audit JSON path changed",
    )
    checks.check(
        interface_artifacts.get("csv")
        == "../v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_interface_audit.csv",
        "interface audit CSV path changed",
    )
    checks.check(
        interface_artifacts.get("markdown")
        == "../v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_interface_audit.md",
        "interface audit markdown path changed",
    )
    checks.check(
        interface_artifacts.get("validator")
        == "../v048_cross_paper_same_test_benchmarks/validate_closed_loop_true_dynamic_interface_audit.py",
        "interface audit validator path changed",
    )
    checks.check(interface_summary.get("dynamic_setup_ok_count") == 2, "interface audit dynamic setup count changed")
    checks.check(interface_summary.get("dynamic_setup_required_count") == 2, "interface audit required count changed")
    checks.check(interface_summary.get("local_gauss6_dynamic_runner_exists") is False, "interface audit local runner overclaimed")
    checks.check(interface_summary.get("public_dynamic_setup_available") is True, "interface audit public setup unavailable")
    checks.check(interface_summary.get("do_step_called") is False, "interface audit called do_step")
    checks.check(interface_summary.get("strict_public_policy_1e-4_required") is False, "interface audit strict 1e-4 overclaimed")
    checks.check(interface_summary.get("heavy_numerical_run_invoked") is False, "interface audit invoked heavy numerical run")
    checks.check(interface_summary.get("accepted_dynamic_order_count") == 0, "interface audit accepted order overclaimed")
    checks.check(
        scaffold_artifacts.get("status") == "residual_layout_specified_runner_not_implemented",
        "residual scaffold artifact status changed",
    )
    checks.check(
        scaffold_artifacts.get("json")
        == "../v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_residual_scaffold.json",
        "residual scaffold JSON path changed",
    )
    checks.check(
        scaffold_artifacts.get("csv")
        == "../v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_residual_scaffold.csv",
        "residual scaffold CSV path changed",
    )
    checks.check(
        scaffold_artifacts.get("markdown")
        == "../v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_residual_scaffold.md",
        "residual scaffold markdown path changed",
    )
    checks.check(
        scaffold_artifacts.get("validator")
        == "../v048_cross_paper_same_test_benchmarks/validate_closed_loop_true_dynamic_residual_scaffold.py",
        "residual scaffold validator path changed",
    )
    checks.check(scaffold_summary.get("stage_unknown_dim") == 72, "residual scaffold stage dim changed")
    checks.check(scaffold_summary.get("total_unknown_dim") == 216, "residual scaffold total dim changed")
    checks.check(scaffold_summary.get("square_total_system") is True, "residual scaffold must remain square")
    checks.check(scaffold_summary.get("local_runner_implemented") is False, "residual scaffold runner overclaimed")
    checks.check(scaffold_summary.get("strict_public_policy_1e-4_required") is False, "residual scaffold strict 1e-4 overclaimed")
    checks.check(scaffold_summary.get("default_1e-4_required") is False, "residual scaffold default 1e-4 overclaimed")
    checks.check(scaffold_summary.get("heavy_numerical_run_invoked") is False, "residual scaffold invoked heavy run")
    checks.check(scaffold_summary.get("accepted_dynamic_order_count") == 0, "residual scaffold accepted order overclaimed")
    checks.check(
        stage_audit_artifacts.get("status") == "stage_residual_evaluator_verified_stepper_not_implemented",
        "stage residual audit artifact status changed",
    )
    checks.check(
        stage_audit_artifacts.get("json")
        == "../v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_stage_residual_audit.json",
        "stage residual audit JSON path changed",
    )
    checks.check(
        stage_audit_artifacts.get("csv")
        == "../v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_stage_residual_audit.csv",
        "stage residual audit CSV path changed",
    )
    checks.check(
        stage_audit_artifacts.get("markdown")
        == "../v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_stage_residual_audit.md",
        "stage residual audit markdown path changed",
    )
    checks.check(
        stage_audit_artifacts.get("validator")
        == "../v048_cross_paper_same_test_benchmarks/validate_closed_loop_true_dynamic_stage_residual_audit.py",
        "stage residual audit validator path changed",
    )
    checks.check(stage_audit_summary.get("row_count") == 6, "stage residual audit row count changed")
    checks.check(stage_audit_summary.get("ok_row_count") == 6, "stage residual audit ok count changed")
    checks.check(stage_audit_summary.get("stage_unknown_dim") == 72, "stage residual audit stage unknown dim changed")
    checks.check(stage_audit_summary.get("stage_residual_dim") == 72, "stage residual audit stage residual dim changed")
    checks.check(stage_audit_summary.get("max_stage_residual_inf", 1.0) < 1.0e-10, "stage residual audit residual too large")
    checks.check(stage_audit_summary.get("stage_residual_evaluator_implemented") is True, "stage residual evaluator not recorded")
    checks.check(stage_audit_summary.get("trajectory_stepper_implemented") is False, "stage residual audit stepper overclaimed")
    checks.check(stage_audit_summary.get("default_1e-4_required") is False, "stage residual audit default 1e-4 overclaimed")
    checks.check(stage_audit_summary.get("heavy_numerical_run_invoked") is False, "stage residual audit invoked heavy run")
    checks.check(stage_audit_summary.get("accepted_dynamic_order_count") == 0, "stage residual audit accepted order overclaimed")
    checks.check(
        one_step_artifacts.get("status") == "one_step_smoke_passed_order_rows_not_run",
        "one-step smoke artifact status changed",
    )
    checks.check(
        one_step_artifacts.get("json")
        == "../v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_one_step_smoke.json",
        "one-step smoke JSON path changed",
    )
    checks.check(
        one_step_artifacts.get("csv")
        == "../v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_one_step_smoke.csv",
        "one-step smoke CSV path changed",
    )
    checks.check(
        one_step_artifacts.get("markdown")
        == "../v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_one_step_smoke.md",
        "one-step smoke markdown path changed",
    )
    checks.check(
        one_step_artifacts.get("validator")
        == "../v048_cross_paper_same_test_benchmarks/validate_closed_loop_true_dynamic_one_step_smoke.py",
        "one-step smoke validator path changed",
    )
    checks.check(one_step_summary.get("row_count") == 2, "one-step smoke row count changed")
    checks.check(one_step_summary.get("ok_row_count") == 2, "one-step smoke ok count changed")
    checks.check(one_step_summary.get("h") == 0.1, "one-step smoke h changed")
    checks.check(one_step_summary.get("max_stage_residual_inf", 1.0) < 1.0e-10, "one-step smoke residual too large")
    checks.check(one_step_summary.get("max_endpoint_pos_error_inf", 1.0) < 1.0e-4, "one-step smoke endpoint error too large")
    checks.check(one_step_summary.get("trajectory_stepper_executed") is True, "one-step smoke did not execute stepper")
    checks.check(one_step_summary.get("convergence_sweep_run") is False, "one-step smoke ran convergence sweep")
    checks.check(one_step_summary.get("simulate_runner_implemented") is False, "one-step smoke simulate runner overclaimed")
    checks.check(one_step_summary.get("default_1e-4_required") is False, "one-step smoke default 1e-4 overclaimed")
    checks.check(one_step_summary.get("heavy_numerical_run_invoked") is False, "one-step smoke invoked heavy run")
    checks.check(one_step_summary.get("accepted_dynamic_order_count") == 0, "one-step smoke accepted order overclaimed")
    checks.check(
        newton_stage_artifacts.get("status") == "non_oracle_stage_newton_smoke_passed_order_rows_not_run",
        "Newton stage smoke artifact status changed",
    )
    checks.check(
        newton_stage_artifacts.get("json")
        == "../v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_newton_stage_smoke.json",
        "Newton stage smoke JSON path changed",
    )
    checks.check(
        newton_stage_artifacts.get("csv")
        == "../v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_newton_stage_smoke.csv",
        "Newton stage smoke CSV path changed",
    )
    checks.check(
        newton_stage_artifacts.get("markdown")
        == "../v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_newton_stage_smoke.md",
        "Newton stage smoke markdown path changed",
    )
    checks.check(
        newton_stage_artifacts.get("validator")
        == "../v048_cross_paper_same_test_benchmarks/validate_closed_loop_true_dynamic_newton_stage_smoke.py",
        "Newton stage smoke validator path changed",
    )
    checks.check(newton_stage_summary.get("row_count") == 2, "Newton stage smoke row count changed")
    checks.check(newton_stage_summary.get("ok_row_count") == 2, "Newton stage smoke ok count changed")
    checks.check(newton_stage_summary.get("h") == 0.1, "Newton stage smoke h changed")
    checks.check(
        newton_stage_summary.get("stage_predictor_policy") == "start_extrapolated_no_stage_oracle",
        "Newton stage smoke predictor changed",
    )
    checks.check(newton_stage_summary.get("stage_oracle_used") is False, "Newton stage smoke used stage oracle")
    checks.check(
        newton_stage_summary.get("max_initial_stage_residual_inf", 0.0) > 1.0e-8,
        "Newton stage smoke initial residual not diagnostic",
    )
    checks.check(
        newton_stage_summary.get("max_stage_residual_inf", 1.0) < 1.0e-8,
        "Newton stage smoke residual too large",
    )
    checks.check(newton_stage_summary.get("trajectory_stepper_executed") is True, "Newton stage smoke did not execute stepper")
    checks.check(newton_stage_summary.get("convergence_sweep_run") is False, "Newton stage smoke ran convergence sweep")
    checks.check(newton_stage_summary.get("simulate_runner_implemented") is False, "Newton stage smoke simulate runner overclaimed")
    checks.check(newton_stage_summary.get("default_1e-4_required") is False, "Newton stage smoke default 1e-4 overclaimed")
    checks.check(newton_stage_summary.get("heavy_numerical_run_invoked") is False, "Newton stage smoke invoked heavy run")
    checks.check(newton_stage_summary.get("accepted_dynamic_order_count") == 0, "Newton stage smoke accepted order overclaimed")
    checks.check(next_batch.get("row_policy", {}).get("models") == CLOSED_LOOP_MODELS, "next batch model set changed")
    checks.check(next_batch.get("row_policy", {}).get("step_sizes") == [0.1, 0.05, 0.025], "next batch step sizes changed")
    checks.check(next_batch.get("row_policy", {}).get("reference_h") == 0.0125, "next batch reference changed")
    checks.check(
        "v047_cylindrical_chain_pipeline/run_v047.py" in next_batch.get("do_not_run", []),
        "next batch lost no-run_v047 guard",
    )

    checks.check(cross_cases.get("same_test_campaign_status") == "not_run", "cross cases same-test status changed")
    checks.check(
        cross_cases.get("status") == "spec_extracted_partial_evidence_not_full_campaign",
        "cross cases status changed",
    )
    checks.check(cross_cases.get("full_external_same_test_campaign_passed") is False, "cross cases full campaign overclaim")
    checks.check(cross_cases.get("external_superiority_claim") is False, "cross cases superiority overclaim")
    checks.check(cross_cases.get("default_1e-4_required") is False, "cross cases default 1e-4 overclaim")
    overlay = cross_cases.get("partial_evidence_overlay", {})
    checks.check(isinstance(overlay, dict), "cross cases partial evidence overlay missing")
    if isinstance(overlay, dict):
        claim_boundary = overlay.get("claim_boundary", {})
        ra_overlay = overlay.get("ra2021_absolute_coordinate", {})
        hi_overlay = overlay.get("hi2022_half_implicit", {})
        vp_overlay = overlay.get("vp2024_velocity_partitioning", {})
        checks.check(isinstance(claim_boundary, dict), "overlay claim boundary missing")
        if isinstance(claim_boundary, dict):
            checks.check(claim_boundary.get("same_test_campaign_status") == "not_run", "overlay same-test overclaim")
            checks.check(claim_boundary.get("external_superiority_claim") is False, "overlay superiority overclaim")
            checks.check(
                claim_boundary.get("strict_public_policy_1e-4_required") is False,
                "overlay strict 1e-4 overclaim",
            )
            checks.check(claim_boundary.get("default_1e-4_required") is False, "overlay default 1e-4 overclaim")
        checks.check(isinstance(ra_overlay, dict), "RA2021 overlay missing")
        if isinstance(ra_overlay, dict):
            checks.check(ra_overlay.get("public_baseline_order_rows") == 27, "RA2021 overlay public rows changed")
            checks.check(ra_overlay.get("public_order_summary_rows") == 9, "RA2021 overlay summary rows changed")
            checks.check(
                ra_overlay.get("coarse_same_window_ready_examples") == COARSE_READY,
                "RA2021 overlay coarse examples changed",
            )
            checks.check(
                ra_overlay.get("local_true_dynamic_order_examples") == CLOSED_LOOP_MODELS,
                "RA2021 overlay closed-loop coarse-dynamics examples changed",
            )
            checks.check(
                ra_overlay.get("public_work_precision_available_examples") == CLOSED_LOOP_MODELS,
                "RA2021 overlay public work examples changed",
            )
            checks.check(
                ra_overlay.get("strict_common_reference_available_examples") == CLOSED_LOOP_MODELS,
                "RA2021 overlay strict common-reference examples changed",
            )
            for artifact in ra_overlay.get("artifacts", []):
                checks.check((PAPER / artifact).resolve().exists(), f"RA2021 overlay artifact missing: {artifact}")
        checks.check(isinstance(hi_overlay, dict), "HI2022 overlay missing")
        if isinstance(hi_overlay, dict):
            checks.check(hi_overlay.get("bounded_rows") == 24, "HI2022 overlay bounded rows changed")
            checks.check(hi_overlay.get("full_T8_policy_complete") is False, "HI2022 overlay overclaimed T8 policy")
            for artifact in hi_overlay.get("artifacts", []):
                checks.check((PAPER / artifact).resolve().exists(), f"HI2022 overlay artifact missing: {artifact}")
        checks.check(isinstance(vp_overlay, dict), "VP2024 overlay missing")
        if isinstance(vp_overlay, dict):
            checks.check(vp_overlay.get("evidence_status") == "code_path_unresolved", "VP2024 overlay status changed")
            for artifact in vp_overlay.get("artifacts", []):
                checks.check((PAPER / artifact).resolve().exists(), f"VP2024 overlay artifact missing: {artifact}")
    required_groups = {group.get("group_id"): group.get("required_status") for group in cross_cases.get("case_groups", [])}
    checks.check(required_groups.get("tfe2026_original_pendulum") == "not_run", "TFE pendulum group overclaim")
    checks.check(required_groups.get("ra2021_absolute_coordinate") == "not_run", "RA2021 group overclaim")
    checks.check(required_groups.get("hi2022_half_implicit") == "not_run", "HI2022 group overclaim")
    checks.check(required_groups.get("vp2024_velocity_partitioning") == "code_path_unresolved", "VP2024 group overclaim")

    run_queue_counts = run_queue.get("coverage_counts", {})
    run_queue_execution = run_queue.get("execution_policy", {})
    checks.check(run_queue.get("schema") == "external-same-test-run-queue-v1", "external run queue schema changed")
    checks.check(
        run_queue.get("status") == "coarse_first_parallel_queue_ready_not_run",
        "external run queue status changed",
    )
    checks.check(run_queue.get("same_test_campaign_status") == "not_run", "external run queue overclaims same-test status")
    checks.check(run_queue.get("external_superiority_claim") is False, "external run queue overclaims superiority")
    checks.check(run_queue_execution.get("default_step_policy") == execution.get("default_step_policy"), "run queue policy mismatch")
    checks.check(run_queue_execution.get("coarse_step_sizes") == [0.1, 0.05, 0.025], "run queue coarse steps changed")
    checks.check(run_queue_execution.get("coarse_reference_h") == 0.0125, "run queue coarse reference changed")
    checks.check(run_queue_execution.get("default_1e-4_required") is False, "run queue overclaims default 1e-4")
    checks.check(run_queue_execution.get("heavy_numerical_run_invoked") is False, "run queue invoked heavy numerical run")
    checks.check(run_queue_execution.get("run_v047_invoked") is False, "run queue invoked run_v047")
    checks.check(run_queue_execution.get("v048_runner_invoked") is False, "run queue invoked v048 runner")
    checks.check(run_queue_counts.get("required_case_count") == 17, "run queue required case count changed")
    checks.check(
        run_queue_counts.get("parallel_shard_count_without_default_1e-4") == 20,
        "run queue parallel shard count changed",
    )
    checks.check(run_queue_counts.get("parallel_ready_batch_count") == 2, "run queue parallel-ready batch count changed")
    checks.check(run_queue_counts.get("not_ready_batch_count") == 2, "run queue not-ready batch count changed")
    require_tokens(
        checks,
        run_queue_md,
        [
            "External Same-Test Run Queue",
            "COARSE-FIRST PARALLEL QUEUE READY - NOT RUN",
            "required case count from `CROSS_PAPER_BENCHMARK_CASES.json`: `17`",
            "parallel shards without default `1e-4`: `20`",
            "`ra2021_coarse_same_window_order_time`",
            "`hi2022_halfimplicit_full_policy_decision`",
            "`tfe2026_original_pendulum_encoding`",
            "`vp2024_velocity_partitioning_code_resolution`",
            "validate_external_same_test_run_queue.py",
        ],
        "EXTERNAL_SAME_TEST_RUN_QUEUE.md",
    )

    checks.check(coarse_first.get("default_policy") == execution.get("default_step_policy"), "coarse-first policy mismatch")
    checks.check(coarse_first.get("same_test_campaign_status") == "not_run", "coarse-first same-test status changed")
    checks.check(coarse_first.get("external_superiority_claim") is False, "coarse-first superiority overclaim")
    checks.check(coarse_first.get("coarse_same_window_ready_count") == same_test.get("coarse_same_window_ready_count"), "coarse count mismatch")
    checks.check(coarse_first.get("dynamic_order_missing_count") == same_test.get("dynamic_order_missing_count"), "missing count mismatch")
    checks.check(coarse_first.get("submission_ready") is False, "coarse-first submission overclaim")

    checks.check(performance.get("examples") == EXAMPLES, "performance example list changed")
    checks.check(performance.get("row_count") == 48, "performance row count changed")
    checks.check(performance.get("completed_row_count") == 32, "performance completed count changed")
    checks.check(performance.get("partial_row_count") == 0, "performance partial count changed")
    checks.check(performance.get("same_test_campaign_status") == "not_run", "performance same-test status changed")
    checks.check(performance.get("external_superiority_claim") is False, "performance superiority overclaim")

    checks.check(r2e.get("accepted_residual_to_error_theorem") is False, "residual-to-error theorem overclaim")
    checks.check(r2e.get("accepted_dynamic_order_count") == 0, "residual-to-error dynamic order overclaim")
    checks.check(r2e.get("blocking_obligation_count") == 7, "residual-to-error obligation count changed")

    checks.check(plan.get("schema") == "closed-loop-true-dynamic-local-row-plan-v1", "true-dynamic row plan schema changed")
    checks.check(plan.get("status") == "plan_only_not_run", "true-dynamic row plan status changed")
    checks.check(plan.get("execution_status") == "not_run", "true-dynamic row plan execution changed")
    checks.check(plan.get("plan_only") is True, "true-dynamic row plan must remain plan-only")
    checks.check(plan.get("default_policy") == execution.get("default_step_policy"), "true-dynamic row plan policy mismatch")
    checks.check(plan.get("models") == CLOSED_LOOP_MODELS, "true-dynamic row plan model set changed")
    checks.check(plan.get("local_method") == "Gauss6/FullVA", "true-dynamic row plan local method changed")
    checks.check(plan.get("public_baselines") == ["rA", "rp", "reps"], "true-dynamic row plan public baselines changed")
    checks.check(plan.get("step_sizes") == [0.1, 0.05, 0.025], "true-dynamic row plan step sizes changed")
    checks.check(plan.get("reference_h") == 0.0125, "true-dynamic row plan reference h changed")
    checks.check(plan.get("row_count") == 24, "true-dynamic row plan row count changed")
    checks.check(plan.get("local_target_row_count") == 6, "true-dynamic row plan local target count changed")
    checks.check(plan.get("public_comparator_row_count") == 18, "true-dynamic row plan public comparator count changed")
    checks.check(plan.get("true_dynamic_local_rows_available") == 0, "true-dynamic row plan true rows overclaimed")
    checks.check(plan.get("accepted_dynamic_order_count") == 0, "true-dynamic row plan dynamic order overclaimed")
    checks.check(plan.get("strict_public_policy_1e-4_required") is False, "true-dynamic row plan strict 1e-4 overclaimed")
    checks.check(plan.get("default_1e-4_required") is False, "true-dynamic row plan default 1e-4 overclaimed")
    checks.check(plan.get("heavy_numerical_run_invoked") is False, "true-dynamic row plan invoked heavy run")
    checks.check(plan.get("external_superiority_claim") is False, "true-dynamic row plan external superiority overclaim")
    checks.check(len(plan_rows) == 24, "true-dynamic row plan CSV row count changed")
    checks.check(
        {row.get("execution_status") for row in plan_rows} == {"not_run"},
        "true-dynamic row plan CSV execution status changed",
    )
    checks.check({row.get("plan_only") for row in plan_rows} == {"true"}, "true-dynamic row plan CSV lost plan-only markers")
    checks.check(
        {row.get("strict_public_policy_1e-4_required") for row in plan_rows} == {"false"},
        "true-dynamic row plan CSV lost no-strict-1e-4 markers",
    )
    checks.check(
        "plan only; no numerical rows have been run" in plan_md,
        "true-dynamic row plan markdown lost plan-only boundary",
    )

    checks.check(
        interface.get("schema") == "closed-loop-true-dynamic-interface-audit-v1",
        "true-dynamic interface audit schema changed",
    )
    checks.check(
        interface.get("status") == "setup_level_interface_verified_no_trajectory_run",
        "true-dynamic interface audit status changed",
    )
    checks.check(interface.get("models") == CLOSED_LOOP_MODELS, "true-dynamic interface audit model set changed")
    checks.check(interface.get("row_count") == 4, "true-dynamic interface audit row count changed")
    checks.check(interface.get("dynamic_setup_ok_count") == 2, "true-dynamic interface audit dynamic setup count changed")
    checks.check(interface.get("dynamic_setup_required_count") == 2, "true-dynamic interface audit required count changed")
    checks.check(interface.get("kinematic_setup_ok_count") == 2, "true-dynamic interface audit kinematic setup count changed")
    checks.check(interface.get("local_gauss6_dynamic_runner_exists") is False, "true-dynamic interface audit local runner overclaimed")
    checks.check(interface.get("public_dynamic_setup_available") is True, "true-dynamic interface audit public setup unavailable")
    checks.check(interface.get("public_do_dynamics_step_available") is True, "true-dynamic interface audit public stepper unavailable")
    checks.check(interface.get("do_step_called") is False, "true-dynamic interface audit called do_step")
    checks.check(interface.get("heavy_numerical_run_invoked") is False, "true-dynamic interface audit invoked heavy run")
    checks.check(interface.get("default_policy") == execution.get("default_step_policy"), "true-dynamic interface audit policy mismatch")
    checks.check(interface.get("strict_public_policy_1e-4_required") is False, "true-dynamic interface audit strict 1e-4 overclaimed")
    checks.check(interface.get("default_1e-4_required") is False, "true-dynamic interface audit default 1e-4 overclaimed")
    checks.check(interface.get("accepted_dynamic_order_count") == 0, "true-dynamic interface audit dynamic order overclaimed")
    checks.check(interface.get("external_superiority_claim") is False, "true-dynamic interface audit external superiority overclaimed")
    checks.check(interface.get("required_next_runner") == plan.get("required_new_runner"), "true-dynamic interface audit runner mismatch")
    checks.check(interface.get("row_plan_count") == plan.get("row_count") == 24, "true-dynamic interface audit row-plan mismatch")
    checks.check(len(interface_rows) == 4, "true-dynamic interface audit CSV row count changed")
    checks.check({row.get("setup_status") for row in interface_rows} == {"ok"}, "true-dynamic interface audit setup status changed")
    checks.check({row.get("do_step_called") for row in interface_rows} == {"false"}, "true-dynamic interface audit CSV called do_step")
    checks.check(
        {row.get("strict_public_policy_1e-4_required") for row in interface_rows} == {"false"},
        "true-dynamic interface audit CSV lost no-strict-1e-4 markers",
    )
    checks.check(
        "setup-level interface verified; no trajectory rows run" in interface_md,
        "true-dynamic interface audit markdown lost no-trajectory boundary",
    )

    checks.check(
        scaffold.get("schema") == "closed-loop-true-dynamic-residual-scaffold-v1",
        "true-dynamic residual scaffold schema changed",
    )
    checks.check(
        scaffold.get("status") == "residual_layout_specified_runner_not_implemented",
        "true-dynamic residual scaffold status changed",
    )
    checks.check(scaffold.get("method") == "Gauss6/FullVA", "true-dynamic residual scaffold method changed")
    checks.check(scaffold.get("models") == CLOSED_LOOP_MODELS, "true-dynamic residual scaffold model set changed")
    checks.check(scaffold.get("n_stages") == 3, "true-dynamic residual scaffold stage count changed")
    checks.check(scaffold.get("row_count") == 2, "true-dynamic residual scaffold row count changed")
    checks.check(scaffold.get("stage_unknown_dim") == 72, "true-dynamic residual scaffold stage dim changed")
    checks.check(scaffold.get("total_unknown_dim") == 216, "true-dynamic residual scaffold total dim changed")
    checks.check(scaffold.get("square_total_system") is True, "true-dynamic residual scaffold not square")
    checks.check(scaffold.get("local_runner_implemented") is False, "true-dynamic residual scaffold runner overclaimed")
    checks.check(scaffold.get("default_policy") == execution.get("default_step_policy"), "true-dynamic residual scaffold policy mismatch")
    checks.check(scaffold.get("strict_public_policy_1e-4_required") is False, "true-dynamic residual scaffold strict 1e-4 overclaimed")
    checks.check(scaffold.get("default_1e-4_required") is False, "true-dynamic residual scaffold default 1e-4 overclaimed")
    checks.check(scaffold.get("heavy_numerical_run_invoked") is False, "true-dynamic residual scaffold invoked heavy run")
    checks.check(scaffold.get("accepted_dynamic_order_count") == 0, "true-dynamic residual scaffold accepted order overclaimed")
    checks.check(scaffold.get("external_superiority_claim") is False, "true-dynamic residual scaffold external superiority overclaimed")
    checks.check(scaffold.get("source_inputs", {}).get("interface_dynamic_setup_ok_count") == 2, "true-dynamic residual scaffold interface source mismatch")
    checks.check(scaffold.get("source_inputs", {}).get("row_plan_count") == 24, "true-dynamic residual scaffold row-plan source mismatch")
    checks.check(len(scaffold_rows) == 2, "true-dynamic residual scaffold CSV row count changed")
    checks.check({row.get("model") for row in scaffold_rows} == set(CLOSED_LOOP_MODELS), "true-dynamic residual scaffold CSV model set changed")
    for row in scaffold_rows:
        model = row.get("model", "<missing>")
        checks.check(row.get("stage_unknown_dim") == "72", f"{model} residual scaffold stage unknown dim changed")
        checks.check(row.get("stage_residual_dim") == "72", f"{model} residual scaffold stage residual dim changed")
        checks.check(row.get("total_unknown_dim") == "216", f"{model} residual scaffold total unknown dim changed")
        checks.check(row.get("total_residual_dim") == "216", f"{model} residual scaffold total residual dim changed")
        checks.check(row.get("square_total_system") == "true", f"{model} residual scaffold not square")
        checks.check(row.get("accepted_dynamic_order") == "false", f"{model} residual scaffold dynamic order overclaimed")
        checks.check(row.get("default_policy") == "coarse_first_no_default_1e-4", f"{model} residual scaffold policy changed")
        checks.check(row.get("strict_public_policy_1e-4_required") == "false", f"{model} residual scaffold strict 1e-4 changed")
    checks.check(
        "residual layout specified; runner not implemented" in scaffold_md,
        "true-dynamic residual scaffold markdown lost status boundary",
    )
    checks.check(
        "position/acceleration consistency rows" in scaffold_md,
        "true-dynamic residual scaffold markdown lost FullVA replacement text",
    )

    checks.check(
        stage_audit.get("schema") == "closed-loop-true-dynamic-stage-residual-audit-v1",
        "true-dynamic stage residual audit schema changed",
    )
    checks.check(
        stage_audit.get("status") == "stage_residual_evaluator_verified_stepper_not_implemented",
        "true-dynamic stage residual audit status changed",
    )
    checks.check(stage_audit.get("method") == "Gauss6/FullVA", "true-dynamic stage residual audit method changed")
    checks.check(stage_audit.get("models") == CLOSED_LOOP_MODELS, "true-dynamic stage residual audit model set changed")
    checks.check(stage_audit.get("row_count") == 6, "true-dynamic stage residual audit row count changed")
    checks.check(stage_audit.get("ok_row_count") == 6, "true-dynamic stage residual audit ok count changed")
    checks.check(stage_audit.get("stage_unknown_dim") == 72, "true-dynamic stage residual audit stage unknown dim changed")
    checks.check(stage_audit.get("stage_residual_dim") == 72, "true-dynamic stage residual audit stage residual dim changed")
    checks.check(stage_audit.get("max_stage_residual_inf", 1.0) < 1.0e-10, "true-dynamic stage residual audit residual too large")
    checks.check(stage_audit.get("stage_residual_evaluator_implemented") is True, "true-dynamic stage evaluator missing")
    checks.check(stage_audit.get("trajectory_stepper_implemented") is False, "true-dynamic stage audit stepper overclaimed")
    checks.check(stage_audit.get("simulate_runner_implemented") is False, "true-dynamic stage audit runner overclaimed")
    checks.check(stage_audit.get("accepted_dynamic_order_count") == 0, "true-dynamic stage audit accepted order overclaimed")
    checks.check(stage_audit.get("trajectory_stepper_executed") is False, "true-dynamic stage audit executed stepper")
    checks.check(stage_audit.get("default_policy") == execution.get("default_step_policy"), "true-dynamic stage audit policy mismatch")
    checks.check(stage_audit.get("strict_public_policy_1e-4_required") is False, "true-dynamic stage audit strict 1e-4 overclaimed")
    checks.check(stage_audit.get("default_1e-4_required") is False, "true-dynamic stage audit default 1e-4 overclaimed")
    checks.check(stage_audit.get("heavy_numerical_run_invoked") is False, "true-dynamic stage audit invoked heavy run")
    checks.check(stage_audit.get("external_superiority_claim") is False, "true-dynamic stage audit external superiority overclaimed")
    checks.check(len(stage_audit_rows) == 6, "true-dynamic stage residual audit CSV row count changed")
    checks.check({row.get("model") for row in stage_audit_rows} == set(CLOSED_LOOP_MODELS), "true-dynamic stage audit CSV model set changed")
    checks.check({row.get("status") for row in stage_audit_rows} == {"ok"}, "true-dynamic stage audit CSV status changed")
    checks.check({row.get("trajectory_stepper_executed") for row in stage_audit_rows} == {"false"}, "true-dynamic stage audit executed stepper")
    checks.check({row.get("accepted_dynamic_order") for row in stage_audit_rows} == {"false"}, "true-dynamic stage audit accepted dynamic order")
    checks.check(
        "stage residual evaluator verified; stepper not implemented" in stage_audit_md,
        "true-dynamic stage residual audit markdown lost status boundary",
    )
    checks.check(
        "must not be counted as a trajectory order row" in stage_audit_md,
        "true-dynamic stage residual audit markdown lost no-order boundary",
    )

    checks.check(
        one_step.get("schema") == "closed-loop-true-dynamic-one-step-smoke-v1",
        "true-dynamic one-step smoke schema changed",
    )
    checks.check(
        one_step.get("status") == "one_step_smoke_passed_order_rows_not_run",
        "true-dynamic one-step smoke status changed",
    )
    checks.check(one_step.get("method") == "Gauss6/FullVA", "true-dynamic one-step smoke method changed")
    checks.check(one_step.get("models") == CLOSED_LOOP_MODELS, "true-dynamic one-step smoke model set changed")
    checks.check(one_step.get("row_count") == 2, "true-dynamic one-step smoke row count changed")
    checks.check(one_step.get("ok_row_count") == 2, "true-dynamic one-step smoke ok count changed")
    checks.check(one_step.get("h") == 0.1, "true-dynamic one-step smoke h changed")
    checks.check(one_step.get("stage_count") == 3, "true-dynamic one-step smoke stage count changed")
    checks.check(one_step.get("stage_unknown_dim") == 72, "true-dynamic one-step smoke stage unknown dim changed")
    checks.check(one_step.get("stage_residual_dim") == 72, "true-dynamic one-step smoke stage residual dim changed")
    checks.check(one_step.get("max_stage_residual_inf", 1.0) < 1.0e-10, "true-dynamic one-step smoke residual too large")
    checks.check(one_step.get("max_endpoint_pos_error_inf", 1.0) < 1.0e-4, "true-dynamic one-step smoke endpoint error too large")
    checks.check(one_step.get("step_policy") == "oracle_initialized_one_step_smoke_not_order", "true-dynamic one-step smoke policy changed")
    checks.check(one_step.get("trajectory_stepper_implemented") is True, "true-dynamic one-step smoke stepper missing")
    checks.check(one_step.get("trajectory_stepper_executed") is True, "true-dynamic one-step smoke did not execute")
    checks.check(one_step.get("simulate_runner_implemented") is False, "true-dynamic one-step smoke runner overclaimed")
    checks.check(one_step.get("accepted_dynamic_order_count") == 0, "true-dynamic one-step smoke accepted order overclaimed")
    checks.check(one_step.get("convergence_sweep_run") is False, "true-dynamic one-step smoke ran convergence sweep")
    checks.check(one_step.get("default_policy") == execution.get("default_step_policy"), "true-dynamic one-step smoke policy mismatch")
    checks.check(one_step.get("strict_public_policy_1e-4_required") is False, "true-dynamic one-step smoke strict 1e-4 overclaimed")
    checks.check(one_step.get("default_1e-4_required") is False, "true-dynamic one-step smoke default 1e-4 overclaimed")
    checks.check(one_step.get("heavy_numerical_run_invoked") is False, "true-dynamic one-step smoke invoked heavy run")
    checks.check(one_step.get("external_superiority_claim") is False, "true-dynamic one-step smoke external superiority overclaimed")
    checks.check(len(one_step_rows) == 2, "true-dynamic one-step smoke CSV row count changed")
    checks.check({row.get("model") for row in one_step_rows} == set(CLOSED_LOOP_MODELS), "true-dynamic one-step smoke CSV model set changed")
    checks.check({row.get("status") for row in one_step_rows} == {"ok"}, "true-dynamic one-step smoke CSV status changed")
    checks.check({row.get("trajectory_stepper_executed") for row in one_step_rows} == {"true"}, "true-dynamic one-step smoke did not execute")
    checks.check({row.get("accepted_dynamic_order") for row in one_step_rows} == {"false"}, "true-dynamic one-step smoke accepted order")
    checks.check(
        "one-step smoke passed; order rows not run" in one_step_md,
        "true-dynamic one-step smoke markdown lost status boundary",
    )
    checks.check(
        "must not be counted as order" in one_step_md,
        "true-dynamic one-step smoke markdown lost no-order boundary",
    )
    checks.check(
        newton_stage.get("schema") == "closed-loop-true-dynamic-newton-stage-smoke-v1",
        "true-dynamic Newton stage smoke schema changed",
    )
    checks.check(
        newton_stage.get("status") == "non_oracle_stage_newton_smoke_passed_order_rows_not_run",
        "true-dynamic Newton stage smoke status changed",
    )
    checks.check(newton_stage.get("method") == "Gauss6/FullVA", "true-dynamic Newton stage smoke method changed")
    checks.check(newton_stage.get("models") == CLOSED_LOOP_MODELS, "true-dynamic Newton stage smoke model set changed")
    checks.check(newton_stage.get("row_count") == 2, "true-dynamic Newton stage smoke row count changed")
    checks.check(newton_stage.get("ok_row_count") == 2, "true-dynamic Newton stage smoke ok count changed")
    checks.check(newton_stage.get("h") == 0.1, "true-dynamic Newton stage smoke h changed")
    checks.check(newton_stage.get("stage_count") == 3, "true-dynamic Newton stage smoke stage count changed")
    checks.check(newton_stage.get("stage_unknown_dim") == 72, "true-dynamic Newton stage smoke stage unknown dim changed")
    checks.check(newton_stage.get("stage_residual_dim") == 72, "true-dynamic Newton stage smoke stage residual dim changed")
    checks.check(newton_stage.get("max_initial_stage_residual_inf", 0.0) > 1.0e-8, "true-dynamic Newton stage smoke initial residual not diagnostic")
    checks.check(newton_stage.get("max_stage_residual_inf", 1.0) < 1.0e-8, "true-dynamic Newton stage smoke residual too large")
    checks.check(newton_stage.get("max_endpoint_pos_error_inf", 1.0) < 1.0e-4, "true-dynamic Newton stage smoke endpoint error too large")
    checks.check(newton_stage.get("step_policy") == "non_oracle_newton_one_step_smoke_not_order", "true-dynamic Newton stage smoke policy changed")
    checks.check(
        newton_stage.get("stage_predictor_policy") == "start_extrapolated_no_stage_oracle",
        "true-dynamic Newton stage smoke predictor changed",
    )
    checks.check(newton_stage.get("stage_oracle_used") is False, "true-dynamic Newton stage smoke used stage oracle")
    checks.check(newton_stage.get("trajectory_stepper_implemented") is True, "true-dynamic Newton stage smoke stepper missing")
    checks.check(newton_stage.get("trajectory_stepper_executed") is True, "true-dynamic Newton stage smoke did not execute")
    checks.check(newton_stage.get("simulate_runner_implemented") is False, "true-dynamic Newton stage smoke runner overclaimed")
    checks.check(newton_stage.get("accepted_dynamic_order_count") == 0, "true-dynamic Newton stage smoke accepted order overclaimed")
    checks.check(newton_stage.get("convergence_sweep_run") is False, "true-dynamic Newton stage smoke ran convergence sweep")
    checks.check(newton_stage.get("default_policy") == execution.get("default_step_policy"), "true-dynamic Newton stage smoke policy mismatch")
    checks.check(newton_stage.get("strict_public_policy_1e-4_required") is False, "true-dynamic Newton stage smoke strict 1e-4 overclaimed")
    checks.check(newton_stage.get("default_1e-4_required") is False, "true-dynamic Newton stage smoke default 1e-4 overclaimed")
    checks.check(newton_stage.get("heavy_numerical_run_invoked") is False, "true-dynamic Newton stage smoke invoked heavy run")
    checks.check(newton_stage.get("external_superiority_claim") is False, "true-dynamic Newton stage smoke external superiority overclaimed")
    checks.check(len(newton_stage_rows) == 2, "true-dynamic Newton stage smoke CSV row count changed")
    checks.check({row.get("model") for row in newton_stage_rows} == set(CLOSED_LOOP_MODELS), "true-dynamic Newton stage smoke CSV model set changed")
    checks.check({row.get("status") for row in newton_stage_rows} == {"ok"}, "true-dynamic Newton stage smoke CSV status changed")
    checks.check({row.get("stage_oracle_used") for row in newton_stage_rows} == {"false"}, "true-dynamic Newton stage smoke CSV used stage oracle")
    checks.check({row.get("accepted_dynamic_order") for row in newton_stage_rows} == {"false"}, "true-dynamic Newton stage smoke accepted order")
    checks.check(
        "No stage-time kinematic oracle is used" in newton_stage_md,
        "true-dynamic Newton stage smoke markdown lost no-stage-oracle boundary",
    )
    checks.check(
        "must not be counted as order" in newton_stage_md,
        "true-dynamic Newton stage smoke markdown lost no-order boundary",
    )

    checks.check(
        newton_coarse_artifacts.get("status") == "coarse_true_dynamic_order_candidates_available_not_external_superiority",
        "Newton coarse-order artifact status changed",
    )
    checks.check(
        newton_coarse_artifacts.get("json")
        == "../v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_newton_coarse_order.json",
        "Newton coarse-order JSON path changed",
    )
    checks.check(
        newton_coarse_artifacts.get("csv")
        == "../v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_newton_coarse_order_rows.csv",
        "Newton coarse-order CSV path changed",
    )
    checks.check(
        newton_coarse_artifacts.get("markdown")
        == "../v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_newton_coarse_order.md",
        "Newton coarse-order markdown path changed",
    )
    checks.check(
        newton_coarse_artifacts.get("validator")
        == "../v048_cross_paper_same_test_benchmarks/validate_closed_loop_true_dynamic_newton_coarse_order.py",
        "Newton coarse-order validator path changed",
    )
    checks.check(newton_coarse_summary.get("row_count") == 6, "Newton coarse-order summary row count changed")
    checks.check(newton_coarse_summary.get("ok_row_count") == 6, "Newton coarse-order summary ok count changed")
    checks.check(newton_coarse_summary.get("models") == CLOSED_LOOP_MODELS, "Newton coarse-order summary models changed")
    checks.check(newton_coarse_summary.get("step_sizes") == [0.1, 0.05, 0.025], "Newton coarse-order summary step sizes changed")
    checks.check(newton_coarse_summary.get("reference_h") == 0.0125, "Newton coarse-order summary reference changed")
    checks.check(newton_coarse_summary.get("stage_oracle_used") is False, "Newton coarse-order summary used stage oracle")
    checks.check(newton_coarse_summary.get("convergence_sweep_run") is True, "Newton coarse-order summary lost sweep marker")
    checks.check(newton_coarse_summary.get("simulate_runner_implemented") is True, "Newton coarse-order summary lost runner marker")
    checks.check(newton_coarse_summary.get("accepted_dynamic_order_count") == 2, "Newton coarse-order summary accepted count changed")
    checks.check(
        newton_coarse_summary.get("public_work_precision_available_count") == 2,
        "Newton coarse-order summary lost public work/precision availability",
    )
    checks.check(
        newton_coarse_summary.get("public_work_precision_missing_count") == 0,
        "Newton coarse-order summary lost closed public work/precision gap",
    )
    checks.check(
        newton_coarse_summary.get("strict_common_reference_available_count") == 2,
        "Newton coarse-order summary lost strict common-reference availability",
    )
    checks.check(
        newton_coarse_summary.get("strict_common_reference_gap_count") == 0,
        "Newton coarse-order summary lost strict common-reference closure",
    )
    checks.check(newton_coarse_summary.get("default_1e-4_required") is False, "Newton coarse-order default 1e-4 overclaimed")
    checks.check(newton_coarse_summary.get("heavy_numerical_run_invoked") is False, "Newton coarse-order invoked heavy run")
    checks.check(newton_coarse_summary.get("external_superiority_claim") is False, "Newton coarse-order superiority overclaimed")
    checks.check(
        newton_coarse.get("schema") == "closed-loop-true-dynamic-newton-coarse-order-v1",
        "true-dynamic Newton coarse-order schema changed",
    )
    checks.check(
        newton_coarse.get("status") == "coarse_true_dynamic_order_candidates_available_not_external_superiority",
        "true-dynamic Newton coarse-order status changed",
    )
    checks.check(newton_coarse.get("models") == CLOSED_LOOP_MODELS, "true-dynamic Newton coarse-order model set changed")
    checks.check(newton_coarse.get("row_count") == 6, "true-dynamic Newton coarse-order row count changed")
    checks.check(newton_coarse.get("ok_row_count") == 6, "true-dynamic Newton coarse-order ok count changed")
    checks.check(newton_coarse.get("stage_oracle_used") is False, "true-dynamic Newton coarse-order used stage oracle")
    checks.check(newton_coarse.get("convergence_sweep_run") is True, "true-dynamic Newton coarse-order lost sweep marker")
    checks.check(newton_coarse.get("simulate_runner_implemented") is True, "true-dynamic Newton coarse-order runner missing")
    checks.check(newton_coarse.get("accepted_dynamic_order_count") == 2, "true-dynamic Newton coarse-order count changed")
    checks.check(newton_coarse.get("default_policy") == execution.get("default_step_policy"), "true-dynamic Newton coarse-order policy mismatch")
    checks.check(newton_coarse.get("strict_public_policy_1e-4_required") is False, "true-dynamic Newton coarse-order strict 1e-4 overclaimed")
    checks.check(newton_coarse.get("default_1e-4_required") is False, "true-dynamic Newton coarse-order default 1e-4 overclaimed")
    checks.check(newton_coarse.get("heavy_numerical_run_invoked") is False, "true-dynamic Newton coarse-order invoked heavy run")
    checks.check(newton_coarse.get("external_superiority_claim") is False, "true-dynamic Newton coarse-order superiority overclaimed")
    checks.check(len(newton_coarse_rows) == 6, "true-dynamic Newton coarse-order CSV row count changed")
    checks.check({row.get("model") for row in newton_coarse_rows} == set(CLOSED_LOOP_MODELS), "true-dynamic Newton coarse-order CSV model set changed")
    checks.check({row.get("status") for row in newton_coarse_rows} == {"ok"}, "true-dynamic Newton coarse-order CSV status changed")
    checks.check({row.get("stage_oracle_used") for row in newton_coarse_rows} == {"false"}, "true-dynamic Newton coarse-order CSV used stage oracle")
    checks.check({row.get("accepted_dynamic_order") for row in newton_coarse_rows} == {"true"}, "true-dynamic Newton coarse-order CSV lost accepted local order")
    checks.check(
        "Accepted dynamic-order candidates: `2`" in newton_coarse_md,
        "true-dynamic Newton coarse-order markdown lost accepted count",
    )
    checks.check(
        "public-baseline work/precision comparison" in newton_coarse_md,
        "true-dynamic Newton coarse-order markdown lost public gap boundary",
    )
    checks.check(
        public_work_artifacts.get("status")
        == "same_window_public_work_precision_available_reference_caveat_not_external_superiority",
        "public work/precision artifact status changed",
    )
    checks.check(
        public_work_artifacts.get("json")
        == "../v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_public_work_precision.json",
        "public work/precision JSON path changed",
    )
    checks.check(
        public_work_artifacts.get("csv")
        == "../v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_public_work_precision_rows.csv",
        "public work/precision CSV path changed",
    )
    checks.check(
        public_work_artifacts.get("summary_csv")
        == "../v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_public_work_precision_summary.csv",
        "public work/precision summary CSV path changed",
    )
    checks.check(
        public_work_artifacts.get("markdown")
        == "../v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_public_work_precision.md",
        "public work/precision markdown path changed",
    )
    checks.check(
        public_work_artifacts.get("validator")
        == "../v048_cross_paper_same_test_benchmarks/validate_closed_loop_true_dynamic_public_work_precision.py",
        "public work/precision validator path changed",
    )
    checks.check(public_work_summary.get("row_count") == 24, "public work/precision summary row count changed")
    checks.check(public_work_summary.get("ok_row_count") == 24, "public work/precision summary ok count changed")
    checks.check(public_work_summary.get("public_raw_row_count") == 18, "public work/precision public raw count changed")
    checks.check(public_work_summary.get("local_raw_row_count") == 6, "public work/precision local raw count changed")
    checks.check(public_work_summary.get("summary_row_count") == 8, "public work/precision summary table count changed")
    checks.check(public_work_summary.get("models") == CLOSED_LOOP_MODELS, "public work/precision model set changed")
    checks.check(public_work_summary.get("step_sizes") == [0.1, 0.05, 0.025], "public work/precision step sizes changed")
    checks.check(public_work_summary.get("public_work_precision_available_count") == 2, "public work/precision availability changed")
    checks.check(public_work_summary.get("public_work_precision_missing_count") == 0, "public work/precision missing count changed")
    checks.check(public_work_summary.get("strict_common_reference_error_columns") is False, "public work/precision strict reference flag changed")
    checks.check(public_work_summary.get("default_1e-4_required") is False, "public work/precision default 1e-4 overclaimed")
    checks.check(public_work_summary.get("external_superiority_claim") is False, "public work/precision superiority overclaimed")
    checks.check(public_work.get("schema") == "closed-loop-true-dynamic-public-work-precision-v1", "public work/precision schema changed")
    checks.check(public_work.get("row_count") == 24, "public work/precision artifact raw row count changed")
    checks.check(public_work.get("ok_row_count") == 24, "public work/precision artifact ok count changed")
    checks.check(public_work.get("public_work_precision_available_count") == 2, "public work/precision artifact availability changed")
    checks.check(public_work.get("public_work_precision_missing_count") == 0, "public work/precision artifact missing count changed")
    checks.check(public_work.get("strict_common_reference_error_columns") is False, "public work/precision artifact reference caveat changed")
    checks.check(public_work.get("external_superiority_claim") is False, "public work/precision artifact overclaimed superiority")
    checks.check(len(public_work_rows) == 24, "public work/precision raw CSV row count changed")
    checks.check(len(public_work_summary_rows) == 8, "public work/precision summary CSV row count changed")
    checks.check(
        "Strict common-reference error columns: `False`" in public_work_md,
        "public work/precision markdown lost reference caveat",
    )

    checks.check(
        strict_common_artifacts.get("status") == "strict_common_reference_error_columns_available_not_external_superiority",
        "strict common-reference artifact status changed",
    )
    checks.check(
        strict_common_artifacts.get("json")
        == "../v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_strict_common_reference.json",
        "strict common-reference JSON path changed",
    )
    checks.check(
        strict_common_artifacts.get("csv")
        == "../v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_strict_common_reference_rows.csv",
        "strict common-reference CSV path changed",
    )
    checks.check(
        strict_common_artifacts.get("summary_csv")
        == "../v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_strict_common_reference_summary.csv",
        "strict common-reference summary CSV path changed",
    )
    checks.check(
        strict_common_artifacts.get("markdown")
        == "../v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_strict_common_reference.md",
        "strict common-reference markdown path changed",
    )
    checks.check(
        strict_common_artifacts.get("figure")
        == "../v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_strict_common_reference_work_precision.png",
        "strict common-reference figure path changed",
    )
    checks.check(
        strict_common_artifacts.get("validator")
        == "../v048_cross_paper_same_test_benchmarks/validate_closed_loop_true_dynamic_strict_common_reference.py",
        "strict common-reference validator path changed",
    )
    checks.check(strict_common_summary.get("row_count") == 24, "strict common-reference summary row count changed")
    checks.check(strict_common_summary.get("ok_row_count") == 24, "strict common-reference summary ok count changed")
    checks.check(strict_common_summary.get("public_raw_row_count") == 18, "strict common-reference public raw count changed")
    checks.check(strict_common_summary.get("local_raw_row_count") == 6, "strict common-reference local raw count changed")
    checks.check(strict_common_summary.get("summary_row_count") == 8, "strict common-reference summary table count changed")
    checks.check(strict_common_summary.get("models") == CLOSED_LOOP_MODELS, "strict common-reference model set changed")
    checks.check(strict_common_summary.get("step_sizes") == [0.1, 0.05, 0.025], "strict common-reference step sizes changed")
    checks.check(strict_common_summary.get("common_reference_h") == 0.0125, "strict common-reference h changed")
    checks.check(
        strict_common_summary.get("common_reference_method") == "v047_exact_kinematic_endpoint",
        "strict common-reference method changed",
    )
    checks.check(strict_common_summary.get("strict_common_reference_available_count") == 2, "strict availability changed")
    checks.check(strict_common_summary.get("strict_common_reference_gap_count") == 0, "strict gap changed")
    checks.check(strict_common_summary.get("strict_common_reference_error_columns") is True, "strict reference flag changed")
    checks.check(strict_common_summary.get("publication_quality_figure_available") is True, "strict figure marker changed")
    checks.check(strict_common_summary.get("figure_integrated_in_manuscript") is True, "strict figure integration marker changed")
    checks.check(strict_common_summary.get("default_1e-4_required") is False, "strict common-reference default 1e-4 overclaimed")
    checks.check(strict_common_summary.get("external_superiority_claim") is False, "strict common-reference superiority overclaimed")
    checks.check(strict_common.get("schema") == "closed-loop-true-dynamic-strict-common-reference-v1", "strict artifact schema changed")
    checks.check(strict_common.get("row_count") == 24, "strict artifact raw row count changed")
    checks.check(strict_common.get("ok_row_count") == 24, "strict artifact ok count changed")
    checks.check(strict_common.get("strict_common_reference_available_count") == 2, "strict artifact availability changed")
    checks.check(strict_common.get("strict_common_reference_gap_count") == 0, "strict artifact gap changed")
    checks.check(strict_common.get("strict_common_reference_error_columns") is True, "strict artifact reference flag changed")
    checks.check(strict_common.get("publication_quality_figure_available") is True, "strict artifact figure marker changed")
    checks.check(strict_common.get("external_superiority_claim") is False, "strict artifact overclaimed superiority")
    checks.check(len(strict_common_rows) == 24, "strict common-reference raw CSV row count changed")
    checks.check(len(strict_common_summary_rows) == 8, "strict common-reference summary CSV row count changed")
    checks.check(STRICT_COMMON_FIGURE.exists() and STRICT_COMMON_FIGURE.stat().st_size > 10_000, "strict common-reference figure missing or small")
    checks.check(
        "Error columns: `pos_final_linf, vel_final_linf, acc_final_linf`" in strict_common_md,
        "strict common-reference markdown lost reference marker",
    )

    checks.check(b2.get("status") == "closed", "B2 should be closed by Route B claim demotion")
    checks.check(
        b2.get("route_b_claim_demotion_policy_applied") is True,
        "B2 Route B claim-demotion marker missing",
    )
    checks.check(
        b2.get("route_b_closes_external_superiority_claim_only") is True,
        "B2 Route B closure scope changed",
    )
    checks.check(b2.get("area") == "same_test_external_baseline", "B2 blocking area changed")
    checks.check(b2.get("external_baseline_gate") == "CMAME_EXTERNAL_BASELINE_GATE.md", "B2 external gate path missing")
    checks.check(
        b2.get("external_baseline_status") == "same_test_campaign_not_run_no_external_superiority_claim",
        "B2 external gate status changed",
    )
    checks.check(
        "original_tfe_pendulum_error_order_work_rows" in b2.get("closed_subrequirements", [])
        and "original_tfe_pendulum_error_order_work_rows" not in b2.get("required_to_close", []),
        "B2 lost original TFE Route B demotion closure",
    )
    checks.check("external_same_test_run_queue_added" in b2.get("partial_progress", []), "B2 lost external run queue marker")
    checks.check("EXTERNAL_SAME_TEST_RUN_QUEUE.md" in b2.get("partial_progress_evidence", []), "B2 run queue MD missing")
    checks.check("EXTERNAL_SAME_TEST_RUN_QUEUE.json" in b2.get("partial_progress_evidence", []), "B2 run queue JSON missing")
    checks.check(
        "validate_external_same_test_run_queue.py" in b2.get("partial_progress_evidence", []),
        "B2 run queue validator missing",
    )
    checks.check(
        "external_same_test_acceptance_sheet_added" in b2.get("partial_progress", []),
        "B2 lost acceptance sheet marker",
    )
    checks.check(
        "EXTERNAL_SAME_TEST_ACCEPTANCE_SHEET.md" in b2.get("partial_progress_evidence", []),
        "B2 acceptance sheet MD missing",
    )
    checks.check(
        "EXTERNAL_SAME_TEST_ACCEPTANCE_SHEET.json" in b2.get("partial_progress_evidence", []),
        "B2 acceptance sheet JSON missing",
    )
    checks.check(
        "validate_external_same_test_acceptance_sheet.py" in b2.get("partial_progress_evidence", []),
        "B2 acceptance sheet validator missing",
    )

    sheet_counts = acceptance_sheet.get("acceptance_counts", {})
    sheet_execution = acceptance_sheet.get("execution_policy", {})
    checks.check(
        gate.get("acceptance_sheet") == "EXTERNAL_SAME_TEST_ACCEPTANCE_SHEET.md",
        "gate missing acceptance sheet path",
    )
    checks.check(
        gate.get("acceptance_sheet_json") == "EXTERNAL_SAME_TEST_ACCEPTANCE_SHEET.json",
        "gate missing acceptance sheet JSON path",
    )
    checks.check(
        acceptance_sheet.get("status") == "acceptance_requirements_defined_campaign_not_run",
        "acceptance sheet status changed",
    )
    checks.check(acceptance_sheet.get("same_test_campaign_status") == "not_run", "acceptance sheet overclaims campaign")
    checks.check(acceptance_sheet.get("external_superiority_claim") is False, "acceptance sheet overclaims superiority")
    checks.check(sheet_execution.get("default_step_policy") == "coarse_first_no_default_1e-4", "acceptance sheet policy changed")
    checks.check(sheet_execution.get("coarse_step_sizes") == [0.1, 0.05, 0.025], "acceptance sheet coarse steps changed")
    checks.check(sheet_execution.get("coarse_reference_h") == 0.0125, "acceptance sheet reference changed")
    checks.check(sheet_execution.get("strict_public_policy_1e-4") == "opt_in_only", "acceptance sheet strict policy changed")
    checks.check(sheet_execution.get("default_1e-4_required") is False, "acceptance sheet requires default 1e-4")
    checks.check(sheet_execution.get("heavy_numerical_run_invoked") is False, "acceptance sheet invoked heavy run")
    checks.check(sheet_execution.get("run_v047_invoked") is False, "acceptance sheet invoked run_v047")
    checks.check(sheet_execution.get("v048_runner_invoked") is False, "acceptance sheet invoked v048 runner")
    checks.check(sheet_counts.get("external_required_case_count") == 17, "acceptance sheet case count changed")
    checks.check(sheet_counts.get("performance_matrix_row_count") == 48, "acceptance sheet performance row count changed")
    checks.check(sheet_counts.get("performance_matrix_completed_row_count") == 32, "acceptance sheet completed row count changed")
    checks.check(sheet_counts.get("performance_matrix_not_complete_row_count") == 16, "acceptance sheet incomplete row count changed")
    checks.check(sheet_counts.get("performance_matrix_partial_row_count") == 0, "acceptance sheet partial row count changed")
    checks.check(sheet_counts.get("local_evidence_coverage_examples_count") == 4, "acceptance sheet local evidence coverage count changed")
    checks.check(sheet_counts.get("accepted_method_dynamic_order_examples_count") == 2, "acceptance sheet accepted method dynamic-order count changed")
    checks.check(sheet_counts.get("mechanism_coverage_examples_count") == 2, "acceptance sheet mechanism coverage count changed")
    checks.check(sheet_counts.get("local_dynamic_order_examples_count") == 2, "acceptance sheet local dynamic-order count changed")
    checks.check(
        sheet_counts.get("accepted_source_policy_dynamic_order_examples_count") == 0,
        "acceptance sheet source-policy dynamic-order count changed",
    )
    checks.check(
        sheet_counts.get("accepted_external_dynamic_order_examples_count") == 0,
        "acceptance sheet accepted external order count changed",
    )
    checks.check(
        sheet_counts.get("parallel_shard_count_without_default_1e-4") == 20,
        "acceptance sheet shard count changed",
    )
    checks.check(acceptance_counts == sheet_counts, "gate acceptance counts do not match acceptance sheet")

    checks.check(suite_status.get("original_tfe2026_pendulum", {}).get("status") == "open_not_encoded", "TFE suite status changed")
    checks.check(
        suite_status.get("ra2021_kissel_taves_negrut", {}).get("status")
        == "partial_coarse_first_and_public_baseline_evidence",
        "RA2021 suite status changed",
    )
    checks.check(
        suite_status.get("hi2022_fang_kissel_zhang_negrut", {}).get("status") == "bounded_pilot_not_full_T8_policy",
        "HI2022 suite status changed",
    )
    checks.check(
        suite_status.get("vp2024_kissel_bakke_negrut", {}).get("status") == "code_path_unresolved",
        "VP2024 suite status changed",
    )
    vp_status = suite_status.get("vp2024_kissel_bakke_negrut", {})
    checks.check(vp_status.get("method_identity_resolved") is True, "VP2024 method identity resolution changed")
    checks.check(
        vp_status.get("implemented_method_label") == "vp2024_coordinate_partitioning_rA",
        "VP2024 implemented method label changed",
    )
    checks.check(
        vp_status.get("distinct_unresolved_method_remaining") is False,
        "VP2024 distinct unresolved method boundary changed",
    )
    checks.check(
        vp_status.get("source_code_path_separately_reproduced") is False,
        "VP2024 source-code reproduction boundary changed",
    )
    checks.check(vp_status.get("common_reference_alias_only") is True, "VP2024 common-reference alias marker changed")

    checks.check(manifest.get("cmame_external_baseline_gate") == "CMAME_EXTERNAL_BASELINE_GATE.md", "manifest missing external gate")
    checks.check(
        manifest.get("cmame_external_baseline_gate_json") == "CMAME_EXTERNAL_BASELINE_GATE.json",
        "manifest missing external gate JSON",
    )
    checks.check("CMAME_EXTERNAL_BASELINE_GATE.md" in manifest.get("evidence_anchors", []), "manifest missing external gate anchor")
    checks.check("CMAME_EXTERNAL_BASELINE_GATE.json" in manifest.get("evidence_anchors", []), "manifest missing external gate JSON anchor")
    checks.check("validate_cmame_external_baseline_gate.py" in manifest.get("validators", []), "manifest missing external gate validator")
    checks.check(
        manifest.get("comparison_objective_closure_reconciliation_audit")
        == "COMPARISON_OBJECTIVE_CLOSURE_RECONCILIATION_AUDIT.md",
        "manifest missing comparison reconciliation path",
    )
    checks.check(
        manifest.get("comparison_objective_closure_reconciliation_audit_json")
        == "COMPARISON_OBJECTIVE_CLOSURE_RECONCILIATION_AUDIT.json",
        "manifest missing comparison reconciliation JSON path",
    )
    checks.check(
        "COMPARISON_OBJECTIVE_CLOSURE_RECONCILIATION_AUDIT.md" in manifest.get("evidence_anchors", []),
        "manifest missing comparison reconciliation anchor",
    )
    checks.check(
        "COMPARISON_OBJECTIVE_CLOSURE_RECONCILIATION_AUDIT.json" in manifest.get("evidence_anchors", []),
        "manifest missing comparison reconciliation JSON anchor",
    )
    checks.check(
        "validate_comparison_objective_closure_reconciliation_audit.py" in manifest.get("validators", []),
        "manifest missing comparison reconciliation validator",
    )
    checks.check(
        manifest.get("source_policy_closure_triage") == "SOURCE_POLICY_CLOSURE_TRIAGE.md",
        "manifest missing source-policy closure triage path",
    )
    checks.check(
        manifest.get("source_policy_closure_triage_json") == "SOURCE_POLICY_CLOSURE_TRIAGE.json",
        "manifest missing source-policy closure triage JSON path",
    )
    checks.check(
        "SOURCE_POLICY_CLOSURE_TRIAGE.md" in manifest.get("evidence_anchors", []),
        "manifest missing source-policy closure triage anchor",
    )
    checks.check(
        "SOURCE_POLICY_CLOSURE_TRIAGE.json" in manifest.get("evidence_anchors", []),
        "manifest missing source-policy closure triage JSON anchor",
    )
    checks.check(
        "validate_source_policy_closure_triage.py" in manifest.get("validators", []),
        "manifest missing source-policy closure triage validator",
    )
    checks.check(
        manifest.get("all_examples_source_policy_audit") == "ALL_EXAMPLES_SOURCE_POLICY_AUDIT.md",
        "manifest missing all-example source-policy audit path",
    )
    checks.check(
        manifest.get("all_examples_source_policy_audit_json") == "ALL_EXAMPLES_SOURCE_POLICY_AUDIT.json",
        "manifest missing all-example source-policy audit JSON path",
    )
    checks.check(
        "ALL_EXAMPLES_SOURCE_POLICY_AUDIT.md" in manifest.get("evidence_anchors", []),
        "manifest missing all-example source-policy audit anchor",
    )
    checks.check(
        "ALL_EXAMPLES_SOURCE_POLICY_AUDIT.json" in manifest.get("evidence_anchors", []),
        "manifest missing all-example source-policy audit JSON anchor",
    )
    checks.check(
        "validate_all_examples_source_policy_audit.py" in manifest.get("validators", []),
        "manifest missing all-example source-policy audit validator",
    )
    checks.check(manifest.get("external_same_test_run_queue") == "EXTERNAL_SAME_TEST_RUN_QUEUE.md", "manifest missing run queue path")
    checks.check(
        manifest.get("external_same_test_run_queue_json") == "EXTERNAL_SAME_TEST_RUN_QUEUE.json",
        "manifest missing run queue JSON path",
    )
    checks.check("EXTERNAL_SAME_TEST_RUN_QUEUE.md" in manifest.get("evidence_anchors", []), "manifest missing run queue anchor")
    checks.check("EXTERNAL_SAME_TEST_RUN_QUEUE.json" in manifest.get("evidence_anchors", []), "manifest missing run queue JSON anchor")
    checks.check("validate_external_same_test_run_queue.py" in manifest.get("validators", []), "manifest missing run queue validator")
    checks.check(
        manifest.get("external_same_test_acceptance_sheet") == "EXTERNAL_SAME_TEST_ACCEPTANCE_SHEET.md",
        "manifest missing acceptance sheet path",
    )
    checks.check(
        manifest.get("external_same_test_acceptance_sheet_json") == "EXTERNAL_SAME_TEST_ACCEPTANCE_SHEET.json",
        "manifest missing acceptance sheet JSON path",
    )
    checks.check(
        "EXTERNAL_SAME_TEST_ACCEPTANCE_SHEET.md" in manifest.get("evidence_anchors", []),
        "manifest missing acceptance sheet anchor",
    )
    checks.check(
        "EXTERNAL_SAME_TEST_ACCEPTANCE_SHEET.json" in manifest.get("evidence_anchors", []),
        "manifest missing acceptance sheet JSON anchor",
    )
    checks.check(
        "validate_external_same_test_acceptance_sheet.py" in manifest.get("validators", []),
        "manifest missing acceptance sheet validator",
    )
    checks.check(
        manifest.get("hi2022_policy_decision_audit") == "HI2022_POLICY_DECISION_AUDIT.md",
        "manifest missing HI2022 policy-decision audit path",
    )
    checks.check(
        manifest.get("hi2022_policy_decision_audit_json") == "HI2022_POLICY_DECISION_AUDIT.json",
        "manifest missing HI2022 policy-decision audit JSON path",
    )
    checks.check(
        "HI2022_POLICY_DECISION_AUDIT.md" in manifest.get("evidence_anchors", []),
        "manifest missing HI2022 policy-decision audit anchor",
    )
    checks.check(
        "HI2022_POLICY_DECISION_AUDIT.json" in manifest.get("evidence_anchors", []),
        "manifest missing HI2022 policy-decision audit JSON anchor",
    )
    checks.check(
        "validate_hi2022_policy_decision_audit.py" in manifest.get("validators", []),
        "manifest missing HI2022 policy-decision audit validator",
    )
    checks.check(
        source_files.get("external_same_test_run_queue") == "EXTERNAL_SAME_TEST_RUN_QUEUE.json",
        "source files missing external run queue",
    )
    checks.check(
        source_files.get("external_same_test_acceptance_sheet") == "EXTERNAL_SAME_TEST_ACCEPTANCE_SHEET.json",
        "source files missing external acceptance sheet",
    )
    checks.check(
        source_files.get("external_same_test_acceptance_sheet_validator") == "validate_external_same_test_acceptance_sheet.py",
        "source files missing external acceptance sheet validator",
    )
    checks.check(
        source_files.get("hi2022_policy_decision_audit") == "HI2022_POLICY_DECISION_AUDIT.md",
        "source files missing HI2022 policy-decision audit",
    )
    checks.check(
        source_files.get("hi2022_policy_decision_audit_json") == "HI2022_POLICY_DECISION_AUDIT.json",
        "source files missing HI2022 policy-decision audit JSON",
    )
    checks.check(
        source_files.get("hi2022_policy_decision_audit_validator") == "validate_hi2022_policy_decision_audit.py",
        "source files missing HI2022 policy-decision audit validator",
    )
    checks.check(
        source_files.get("comparison_objective_closure_reconciliation_audit")
        == "COMPARISON_OBJECTIVE_CLOSURE_RECONCILIATION_AUDIT.md",
        "source files missing comparison reconciliation audit",
    )
    checks.check(
        source_files.get("comparison_objective_closure_reconciliation_audit_json")
        == "COMPARISON_OBJECTIVE_CLOSURE_RECONCILIATION_AUDIT.json",
        "source files missing comparison reconciliation JSON",
    )
    checks.check(
        source_files.get("comparison_objective_closure_reconciliation_validator")
        == "validate_comparison_objective_closure_reconciliation_audit.py",
        "source files missing comparison reconciliation validator",
    )
    checks.check(
        source_files.get("source_policy_closure_triage") == "SOURCE_POLICY_CLOSURE_TRIAGE.md",
        "source files missing source-policy closure triage",
    )
    checks.check(
        source_files.get("source_policy_closure_triage_json") == "SOURCE_POLICY_CLOSURE_TRIAGE.json",
        "source files missing source-policy closure triage JSON",
    )
    checks.check(
        source_files.get("source_policy_closure_triage_validator") == "validate_source_policy_closure_triage.py",
        "source files missing source-policy closure triage validator",
    )
    checks.check(
        source_files.get("all_examples_source_policy_audit") == "ALL_EXAMPLES_SOURCE_POLICY_AUDIT.md",
        "source files missing all-example source-policy audit",
    )
    checks.check(
        source_files.get("all_examples_source_policy_audit_json") == "ALL_EXAMPLES_SOURCE_POLICY_AUDIT.json",
        "source files missing all-example source-policy audit JSON",
    )
    checks.check(
        source_files.get("all_examples_source_policy_audit_validator") == "validate_all_examples_source_policy_audit.py",
        "source files missing all-example source-policy audit validator",
    )
    checks.check(
        source_files.get("true_dynamic_local_row_plan")
        == "../v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_local_row_plan.json",
        "source files missing true-dynamic row plan",
    )
    checks.check(
        source_files.get("true_dynamic_local_row_plan_validator")
        == "../v048_cross_paper_same_test_benchmarks/validate_closed_loop_true_dynamic_local_row_plan.py",
        "source files missing true-dynamic row plan validator",
    )
    checks.check(
        source_files.get("true_dynamic_interface_audit")
        == "../v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_interface_audit.json",
        "source files missing true-dynamic interface audit",
    )
    checks.check(
        source_files.get("true_dynamic_interface_audit_validator")
        == "../v048_cross_paper_same_test_benchmarks/validate_closed_loop_true_dynamic_interface_audit.py",
        "source files missing true-dynamic interface audit validator",
    )
    checks.check(
        source_files.get("true_dynamic_residual_scaffold")
        == "../v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_residual_scaffold.json",
        "source files missing true-dynamic residual scaffold",
    )
    checks.check(
        source_files.get("true_dynamic_residual_scaffold_validator")
        == "../v048_cross_paper_same_test_benchmarks/validate_closed_loop_true_dynamic_residual_scaffold.py",
        "source files missing true-dynamic residual scaffold validator",
    )
    checks.check(
        source_files.get("true_dynamic_stage_residual_audit")
        == "../v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_stage_residual_audit.json",
        "source files missing true-dynamic stage residual audit",
    )
    checks.check(
        source_files.get("true_dynamic_stage_residual_audit_validator")
        == "../v048_cross_paper_same_test_benchmarks/validate_closed_loop_true_dynamic_stage_residual_audit.py",
        "source files missing true-dynamic stage residual audit validator",
    )
    checks.check(
        source_files.get("true_dynamic_one_step_smoke")
        == "../v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_one_step_smoke.json",
        "source files missing true-dynamic one-step smoke",
    )
    checks.check(
        source_files.get("true_dynamic_one_step_smoke_validator")
        == "../v048_cross_paper_same_test_benchmarks/validate_closed_loop_true_dynamic_one_step_smoke.py",
        "source files missing true-dynamic one-step smoke validator",
    )
    checks.check(
        source_files.get("true_dynamic_newton_stage_smoke")
        == "../v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_newton_stage_smoke.json",
        "source files missing true-dynamic Newton stage smoke",
    )
    checks.check(
        source_files.get("true_dynamic_newton_stage_smoke_validator")
        == "../v048_cross_paper_same_test_benchmarks/validate_closed_loop_true_dynamic_newton_stage_smoke.py",
        "source files missing true-dynamic Newton stage smoke validator",
    )
    checks.check(
        source_files.get("true_dynamic_newton_coarse_order")
        == "../v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_newton_coarse_order.json",
        "source files missing true-dynamic Newton coarse order",
    )
    checks.check(
        source_files.get("true_dynamic_newton_coarse_order_validator")
        == "../v048_cross_paper_same_test_benchmarks/validate_closed_loop_true_dynamic_newton_coarse_order.py",
        "source files missing true-dynamic Newton coarse-order validator",
    )
    checks.check(
        source_files.get("true_dynamic_public_work_precision")
        == "../v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_public_work_precision.json",
        "source files missing true-dynamic public work/precision artifact",
    )
    checks.check(
        source_files.get("true_dynamic_public_work_precision_rows")
        == "../v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_public_work_precision_rows.csv",
        "source files missing true-dynamic public work/precision rows",
    )
    checks.check(
        source_files.get("true_dynamic_public_work_precision_summary")
        == "../v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_public_work_precision_summary.csv",
        "source files missing true-dynamic public work/precision summary",
    )
    checks.check(
        source_files.get("true_dynamic_public_work_precision_validator")
        == "../v048_cross_paper_same_test_benchmarks/validate_closed_loop_true_dynamic_public_work_precision.py",
        "source files missing true-dynamic public work/precision validator",
    )
    checks.check(
        source_files.get("true_dynamic_strict_common_reference")
        == "../v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_strict_common_reference.json",
        "source files missing strict common-reference artifact",
    )
    checks.check(
        source_files.get("true_dynamic_strict_common_reference_rows")
        == "../v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_strict_common_reference_rows.csv",
        "source files missing strict common-reference rows",
    )
    checks.check(
        source_files.get("true_dynamic_strict_common_reference_summary")
        == "../v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_strict_common_reference_summary.csv",
        "source files missing strict common-reference summary",
    )
    checks.check(
        source_files.get("true_dynamic_strict_common_reference_figure")
        == "../v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_strict_common_reference_work_precision.png",
        "source files missing strict common-reference figure",
    )
    checks.check(
        source_files.get("true_dynamic_strict_common_reference_validator")
        == "../v048_cross_paper_same_test_benchmarks/validate_closed_loop_true_dynamic_strict_common_reference.py",
        "source files missing strict common-reference validator",
    )
    checks.check(
        "../v048_cross_paper_same_test_benchmarks/validate_closed_loop_true_dynamic_local_row_plan.py"
        in manifest.get("validators", []),
        "manifest missing true-dynamic row plan validator",
    )
    checks.check(
        "../v048_cross_paper_same_test_benchmarks/validate_closed_loop_true_dynamic_interface_audit.py"
        in manifest.get("validators", []),
        "manifest missing true-dynamic interface audit validator",
    )
    checks.check(
        "../v048_cross_paper_same_test_benchmarks/validate_closed_loop_true_dynamic_residual_scaffold.py"
        in manifest.get("validators", []),
        "manifest missing true-dynamic residual scaffold validator",
    )
    checks.check(
        "../v048_cross_paper_same_test_benchmarks/validate_closed_loop_true_dynamic_stage_residual_audit.py"
        in manifest.get("validators", []),
        "manifest missing true-dynamic stage residual audit validator",
    )
    checks.check(
        "../v048_cross_paper_same_test_benchmarks/validate_closed_loop_true_dynamic_one_step_smoke.py"
        in manifest.get("validators", []),
        "manifest missing true-dynamic one-step smoke validator",
    )
    checks.check(
        "../v048_cross_paper_same_test_benchmarks/validate_closed_loop_true_dynamic_newton_stage_smoke.py"
        in manifest.get("validators", []),
        "manifest missing true-dynamic Newton stage smoke validator",
    )
    checks.check(
        "../v048_cross_paper_same_test_benchmarks/validate_closed_loop_true_dynamic_newton_coarse_order.py"
        in manifest.get("validators", []),
        "manifest missing true-dynamic Newton coarse-order validator",
    )
    checks.check(
        "../v048_cross_paper_same_test_benchmarks/validate_closed_loop_true_dynamic_public_work_precision.py"
        in manifest.get("validators", []),
        "manifest missing true-dynamic public work/precision validator",
    )
    checks.check(
        "../v048_cross_paper_same_test_benchmarks/validate_closed_loop_true_dynamic_strict_common_reference.py"
        in manifest.get("validators", []),
        "manifest missing strict common-reference validator",
    )
    for anchor in [
        "v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_residual_scaffold.json",
        "v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_residual_scaffold.csv",
        "v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_residual_scaffold.md",
        "v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_stage_residual_audit.json",
        "v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_stage_residual_audit.csv",
        "v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_stage_residual_audit.md",
        "v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_one_step_smoke.json",
        "v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_one_step_smoke.csv",
        "v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_one_step_smoke.md",
        "v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_newton_stage_smoke.json",
        "v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_newton_stage_smoke.csv",
        "v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_newton_stage_smoke.md",
        "v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_newton_coarse_order.json",
        "v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_newton_coarse_order_rows.csv",
        "v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_newton_coarse_order.md",
        "v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_public_work_precision.json",
        "v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_public_work_precision_rows.csv",
        "v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_public_work_precision_summary.csv",
        "v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_public_work_precision.md",
        "v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_strict_common_reference.json",
        "v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_strict_common_reference_rows.csv",
        "v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_strict_common_reference_summary.csv",
        "v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_strict_common_reference.md",
        "v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_strict_common_reference_work_precision.png",
    ]:
        checks.check(anchor in manifest.get("evidence_anchors", []), f"manifest missing closed-loop dynamic anchor: {anchor}")

    require_tokens(
        checks,
        gate_md,
        [
            "CMAME External Baseline Gate",
            "OPEN - NOT SUBMISSION READY",
            "coarse_first_no_default_1e-4",
            "default_1e-4_required=false",
            "same_test_campaign_status=not_run",
            "external_superiority_claim=false",
            "full_external_same_test_campaign_passed=false",
            "all-example common-reference comparison matrix closed: `true`",
            "common-reference examples checked",
            "common-reference cells checked: `44`",
            "raw rows recomputed for common-reference audit: `132`",
            "common-reference summary mismatches: `0`",
            "direct nonlocal velocity-order wins: `40/40`",
            "direct nonlocal finest-velocity-error wins: `40/40`",
            "original-paper velocity-error wins: `16/16`",
            "Kissel/Negrut-family velocity-error wins: `24/24`",
            "source-policy flagged raw rows checked by all-example audit: `45`",
            "source-policy flagged examples checked",
            "source-policy superiority claim allowed: `false`",
            "B2/B4 can close from common-reference evidence alone: `false`",
            "COMPARISON_OBJECTIVE_CLOSURE_RECONCILIATION_AUDIT.md/json",
            "ALL_EXAMPLES_SOURCE_POLICY_AUDIT.md/json",
            "15` flagged summary rows and `45` raw",
            "SOURCE_POLICY_CLOSURE_TRIAGE.md/json",
            "triage covers all four examples",
            "5 RA2021 public velocity-mapping/time-grid/norm rows",
            "4 original-TFE source-pendulum",
            "3 HI2022 full-`T=8` policy rows",
            "3 VP code-path-demotion rows",
            "finite-grid common-reference",
            "The audit recomputes all 44 summary cells from",
            "bounded diagnostic records 40/40 positive direct nonlocal velocity-order comparisons",
            "40/40 positive direct nonlocal finest-velocity-error comparisons",
            "source-paper default-policy reproduction",
            "coordinate-partitioning proxy is identified through the implemented",
            "distinct public VP code path remains unresolved and demoted",
            "partial_evidence_overlay",
            "no row inventory field requires a default `1e-4` campaign",
            "coarse-window trajectory diagnostics",
            "public work/precision available examples",
            "public work/precision missing examples: none",
            "strict common-reference available examples",
            "strict common-reference gap examples",
            "strict common-reference figure available: `true`",
            "strict common-reference figure integrated in manuscript: `true`",
            "single_pendulum",
            "double_pendulum",
            "four_link",
            "slider_crank",
            "surrogate-only closed-loop examples: none",
            "accepted external dynamic-order examples: none",
            "no residual-only row is promoted to a dynamic-order claim",
            "Next Parallel Batch",
            "close_remaining_external_suites_or_demote_external_superiority_claim",
            "closed-loop coarse-window trajectory diagnostic shard and public comparator",
            "Split independent review or figure tasks by model, public form, and step",
            "plan_only_not_run",
            "closed_loop_true_dynamic_local_row_plan.json",
            "EXTERNAL_SAME_TEST_RUN_QUEUE.md/json",
            "parallel shards without default `1e-4`: `20`",
            "ra2021_coarse_same_window_order_time",
            "hi2022_halfimplicit_full_policy_decision",
            "tfe2026_original_pendulum_encoding",
            "vp2024_velocity_partitioning_code_resolution",
            "setup_level_interface_verified_no_trajectory_run",
            "closed_loop_true_dynamic_interface_audit.json",
            "residual_layout_specified_runner_not_implemented",
            "closed_loop_true_dynamic_residual_scaffold.json",
            "stage unknown dimension: `72`",
            "total Newton dimension: `216`",
            "stage_residual_evaluator_verified_stepper_not_implemented",
            "closed_loop_true_dynamic_stage_residual_audit.json",
            "max stage residual infinity norm",
            "trajectory stepper implemented: `false`",
            "one_step_smoke_passed_order_rows_not_run",
            "closed_loop_true_dynamic_one_step_smoke.json",
            "trajectory stepper executed: `true`",
            "convergence sweep run: `false`",
            "non_oracle_stage_newton_smoke_passed_order_rows_not_run",
            "closed_loop_true_dynamic_newton_stage_smoke.json",
            "stage predictor policy: `start_extrapolated_no_stage_oracle`",
            "stage oracle used: `false`",
            "coarse_true_dynamic_order_candidates_available_not_external_superiority",
            "closed_loop_true_dynamic_newton_coarse_order.json",
            "closed-loop coarse-window trajectory diagnostic examples: `2`",
            "same_window_public_work_precision_available_reference_caveat_not_external_superiority",
            "closed_loop_true_dynamic_public_work_precision.json",
            "strict common-reference error columns: `false`",
            "strict_common_reference_error_columns_available_not_external_superiority",
            "closed_loop_true_dynamic_strict_common_reference.json",
            "strict common-reference error columns: `true`",
            "closed_loop_true_dynamic_strict_common_reference_work_precision.png",
            "figures/strict_common_reference_work_precision.png",
            "strict_public_policy_1e-4_required=false",
            "heavy_numerical_run_invoked=false",
            "validate_cmame_external_baseline_gate.py",
            "validate_external_same_test_run_queue.py",
            "validate_closed_loop_true_dynamic_local_row_plan.py",
            "validate_closed_loop_true_dynamic_interface_audit.py",
            "validate_closed_loop_true_dynamic_residual_scaffold.py",
            "validate_closed_loop_true_dynamic_stage_residual_audit.py",
            "validate_closed_loop_true_dynamic_one_step_smoke.py",
            "validate_closed_loop_true_dynamic_newton_stage_smoke.py",
            "validate_closed_loop_true_dynamic_newton_coarse_order.py",
            "validate_closed_loop_true_dynamic_public_work_precision.py",
            "validate_closed_loop_true_dynamic_strict_common_reference.py",
        ],
        "CMAME_EXTERNAL_BASELINE_GATE.md",
    )
    require_tokens(
        checks,
        cross_spec,
        [
            "same-test benchmark specification has been extracted",
            "partial_evidence_overlay",
            "coarse_first_no_default_1e-4",
            "external same-test benchmark campaign has passed",
            "It still cannot state",
            "external-method superiority",
            "The next executable gate is to run the cases listed",
        ],
        "CROSS_PAPER_BENCHMARK_SPEC.md",
    )
    require_tokens(
        checks,
        readiness_review,
        [
            "same-test external baseline",
            "same_test_campaign_status=not_run",
            "partial_evidence_overlay",
            "no-default-`1e-4` policy",
            "external superiority",
            "The benchmark specification and case inventory have now been extracted",
            "EXTERNAL_SAME_TEST_RUN_QUEUE.md/json",
            "EXTERNAL_SAME_TEST_ACCEPTANCE_SHEET.md/json",
            "20 non-default-`1e-4`",
            "`accepted_external_dynamic_order_examples=0`",
            "numerical campaign itself remains open",
        ],
        "CMAME_SUBMISSION_READINESS_REVIEW.md",
    )
    require_tokens(
        checks,
        acceptance_sheet_md,
        [
            "External Same-Test Acceptance Sheet",
            "ACCEPTANCE REQUIREMENTS DEFINED - CAMPAIGN NOT RUN",
            "coarse_first_no_default_1e-4",
            "`default_1e-4_required=false`",
            "`heavy_numerical_run_invoked=false`",
            "`run_v047_invoked=false`",
            "`v048_runner_invoked=false`",
            "parallel shards without default `1e-4`: `20`",
            "local evidence coverage examples: `4/4`",
            "accepted method dynamic-order examples: `2/4`",
            "mechanism-coverage examples: `2/4`",
            "accepted source-policy dynamic-order examples: `0/4`",
            "Neither B2 nor B4 requires a default `1e-4` campaign",
            "validate_external_same_test_acceptance_sheet.py",
        ],
        "EXTERNAL_SAME_TEST_ACCEPTANCE_SHEET.md",
    )

    forbidden = set(gate.get("forbidden_claims", []))
    for token in [
        "external_superiority_claim_true",
        "same_test_campaign_passed_true",
        "default_1e-4_required_true",
        "four_link_slider_crank_dynamic_order_accepted_by_surrogate",
        "original_tfe_pendulum_rows_completed_true",
        "hi2022_full_T8_policy_completed_true",
        "vp2024_code_path_resolved_true",
        "submission_ready_true",
    ]:
        checks.check(token in forbidden, f"forbidden claim missing: {token}")

    if checks.errors:
        print("cmame_external_baseline_gate=FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("cmame_external_baseline_gate=PASS")
    print("same_test_campaign_status=not_run")
    print("external_superiority_claim=False")
    print("comparison_matrix_closed=True")
    print("common_reference_examples=single_pendulum,double_pendulum,four_link,slider_crank")
    print("common_reference_cells=44")
    print("raw_rows_recomputed=132")
    print("summary_mismatches=0")
    print("direct_nonlocal_order_wins=40/40")
    print("direct_nonlocal_error_wins=40/40")
    print("original_paper_velocity_error_wins=16/16")
    print("kissel_negrut_velocity_error_wins=24/24")
    print("source_policy_flagged_rows=15")
    print("source_policy_velocity_mismatch_rows=10")
    print("source_policy_superiority_claim_allowed=False")
    print("b2_b4_can_close_now=False")
    print("default_1e-4=False")
    print("true_dynamic_row_plan=plan_only_not_run")
    print("true_dynamic_row_plan_rows=24")
    print("external_same_test_run_queue=PASS")
    print("external_same_test_acceptance_sheet=PASS")
    print("parallel_shard_count_without_default_1e-4=20")
    print("local_evidence_coverage_examples=4/4")
    print("accepted_method_dynamic_order_examples=2/4")
    print("mechanism_coverage_examples=2/4")
    print("source_policy_dynamic_order_examples=0/4")
    print("accepted_external_dynamic_order_examples=0")
    print("true_dynamic_interface_audit=setup_level_interface_verified_no_trajectory_run")
    print("true_dynamic_interface_dynamic_setup_ok=2/2")
    print("true_dynamic_residual_scaffold=residual_layout_specified_runner_not_implemented")
    print("true_dynamic_residual_scaffold_dims=72/216")
    print("true_dynamic_stage_residual_audit=stage_residual_evaluator_verified_stepper_not_implemented")
    print("true_dynamic_stage_residual_audit_rows=6/6")
    print("true_dynamic_one_step_smoke=one_step_smoke_passed_order_rows_not_run")
    print("true_dynamic_one_step_smoke_rows=2/2")
    print("true_dynamic_newton_stage_smoke=non_oracle_stage_newton_smoke_passed_order_rows_not_run")
    print("true_dynamic_newton_stage_smoke_rows=2/2")
    print("true_dynamic_newton_coarse_order=coarse_true_dynamic_order_candidates_available_not_external_superiority")
    print("true_dynamic_newton_coarse_order_rows=6/6")
    print("true_dynamic_public_work_precision=same_window_public_work_precision_available_reference_caveat_not_external_superiority")
    print("true_dynamic_public_work_precision_rows=24/24")
    print("true_dynamic_strict_common_reference=strict_common_reference_error_columns_available_not_external_superiority")
    print("true_dynamic_strict_common_reference_rows=24/24")
    print("closed_loop_mechanism_coverage_examples=four_link,slider_crank")
    print("public_work_precision_available_examples=four_link,slider_crank")
    print("public_work_precision_missing_examples=none")
    print("strict_common_reference_available_examples=four_link,slider_crank")
    print("strict_common_reference_gap_examples=none")
    print("strict_common_reference_figure_available=True")
    print("strict_common_reference_figure_integrated_in_manuscript=True")
    print("coarse_first_order_time_examples=single_pendulum,double_pendulum")
    print("surrogate_only_examples=none")
    print("accepted_external_dynamic_order_examples=none")
    print("closed_loop_residual_to_error_accepted=False")
    print("submission_ready=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
