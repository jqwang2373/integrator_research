#!/usr/bin/env python3
"""Validate the HI2022 policy-decision audit against current evidence."""

from __future__ import annotations

import csv
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
ROOT = PAPER.parent
V048 = ROOT / "v048_cross_paper_same_test_benchmarks" / "results"
AUDIT_JSON = PAPER / "HI2022_POLICY_DECISION_AUDIT.json"
AUDIT_MD = PAPER / "HI2022_POLICY_DECISION_AUDIT.md"
ROWS_CSV = V048 / "hi2022_halfimplicit_rows.csv"
SUMMARY_JSON = V048 / "summary_v048.json"
QUEUE_JSON = PAPER / "EXTERNAL_SAME_TEST_RUN_QUEUE.json"
ACCEPTANCE_JSON = PAPER / "EXTERNAL_SAME_TEST_ACCEPTANCE_SHEET.json"
DASHBOARD_JSON = PAPER / "FOUR_EXAMPLE_SOURCE_POLICY_DASHBOARD.json"

EXAMPLES = ["single_pendulum", "double_pendulum", "four_link", "slider_crank"]
FORMS = ["rA", "rA_half"]
STEP_SIZES = [0.005, 0.01, 0.02]


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


def queue_batch(queue: dict[str, Any], batch_id: str) -> dict[str, Any]:
    for batch in queue.get("batch_queue", []):
        if isinstance(batch, dict) and batch.get("batch_id") == batch_id:
            return batch
    return {}


def main() -> int:
    checks = Checks()
    try:
        audit = read_json(AUDIT_JSON)
        audit_md = read_text(AUDIT_MD)
        rows = read_csv_rows(ROWS_CSV)
        summary = read_json(SUMMARY_JSON)
        queue = read_json(QUEUE_JSON)
        acceptance = read_json(ACCEPTANCE_JSON)
        dashboard = read_json(DASHBOARD_JSON)
    except Exception as exc:  # noqa: BLE001 - concise CLI failure.
        print(f"hi2022_policy_decision_audit=FAIL\n- {exc}")
        return 1

    existing = audit.get("existing_bounded_evidence", {})
    source_policy = audit.get("source_policy_required_before_external_superiority", {})
    queue_policy = audit.get("queue_policy_decision", {})
    local_boundary = audit.get("local_order_boundary", {})
    execution = audit.get("execution_policy", {})
    hi_summary = summary.get("hi2022_halfimplicit", {})
    hi_batch = queue_batch(queue, "hi2022_halfimplicit_full_policy_decision")

    grouped: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[(row.get("model", ""), row.get("form", ""))].append(row)

    checks.check(audit.get("schema") == "hi2022-policy-decision-audit-v1", "schema changed")
    checks.check(
        audit.get("status") == "bounded_T0p1_rows_complete_full_T8_source_policy_open",
        "status changed",
    )
    checks.check(audit.get("submission_ready") is False, "audit must not mark submission ready")
    checks.check(audit.get("suite_id") == "hi2022_half_implicit", "suite id changed")
    checks.check(audit.get("source_suite") == "hi2022_fang_kissel_zhang_negrut", "source suite changed")
    checks.check(
        audit.get("evidence_class") == "bounded_pilot_only_not_source_policy_reproduction",
        "evidence class changed",
    )

    checks.check(len(rows) == existing.get("row_count") == hi_summary.get("row_count") == 24, "HI2022 row count changed")
    checks.check(
        sum(1 for row in rows if row.get("status") == "ok")
        == existing.get("ok_row_count")
        == hi_summary.get("ok_row_count")
        == 24,
        "HI2022 ok row count changed",
    )
    checks.check(existing.get("policy") == "hi2022_bounded_four_example_pilot_not_full_campaign", "policy changed")
    checks.check(existing.get("source_suite") == "hi2022_fang_kissel_zhang_negrut", "source suite row label changed")
    checks.check(existing.get("t_end_values") == [0.1], "bounded T=0.1 horizon changed")
    checks.check(existing.get("step_sizes") == STEP_SIZES, "bounded step sizes changed")
    checks.check(existing.get("reference_h_values") == [0.001], "bounded reference h changed")
    checks.check(existing.get("models") == EXAMPLES, "model coverage changed")
    checks.check(existing.get("forms") == FORMS, "form coverage changed")
    checks.check(existing.get("group_count") == 8, "group count changed")
    checks.check(existing.get("groups_with_three_step_sizes") == 8, "three-step group count changed")
    for model in EXAMPLES:
        for form in FORMS:
            rows_for_group = grouped[(model, form)]
            group = existing.get("row_groups", {}).get(f"{form}:{model}", {})
            checks.check(len(rows_for_group) == group.get("row_count") == 3, f"group row count changed for {form}:{model}")
            checks.check(
                sum(1 for row in rows_for_group if row.get("status") == "ok") == group.get("ok_row_count") == 3,
                f"group ok count changed for {form}:{model}",
            )
            checks.check(group.get("step_sizes") == STEP_SIZES, f"group h-grid changed for {form}:{model}")

    checks.check(summary.get("hi2022_halfimplicit_rows_completed") is True, "summary row completion changed")
    checks.check(hi_summary.get("full_hi2022_campaign_completed") is False, "summary overclaims full HI2022 campaign")
    checks.check(source_policy.get("full_T8_policy_required") is True, "full T8 requirement changed")
    checks.check(source_policy.get("full_T8_policy_completed") is False, "audit overclaims full T8 completion")
    checks.check(source_policy.get("source_policy_reproduction_closed") is False, "audit overclaims source-policy closure")
    checks.check(source_policy.get("accepted_for_bounded_evidence") is True, "bounded evidence acceptance changed")
    checks.check(source_policy.get("accepted_for_external_superiority") is False, "audit overclaims external superiority")
    checks.check(
        source_policy.get("accepted_source_policy_dynamic_order_examples_count")
        == acceptance.get("acceptance_counts", {}).get("accepted_source_policy_dynamic_order_examples_count")
        == 0,
        "source-policy dynamic-order acceptance count changed",
    )
    checks.check(
        source_policy.get("accepted_external_dynamic_order_examples_count")
        == acceptance.get("acceptance_counts", {}).get("accepted_external_dynamic_order_examples_count")
        == 0,
        "external dynamic-order acceptance count changed",
    )
    checks.check(source_policy.get("external_superiority_claim_allowed") is False, "audit overclaims superiority")
    checks.check(source_policy.get("paper_direct_error_superiority_allowed") is False, "audit overclaims direct-error superiority")

    checks.check(queue_policy.get("batch_id") == "hi2022_halfimplicit_full_policy_decision", "queue batch id changed")
    checks.check(queue_policy.get("queue_status") == hi_batch.get("queue_status") == "parallel_ready_after_policy_selection", "queue status changed")
    checks.check(queue_policy.get("models") == hi_batch.get("models") == EXAMPLES, "queue model set changed")
    checks.check(queue_policy.get("public_forms") == hi_batch.get("public_forms") == ["rA_half", "rA"], "queue forms changed")
    checks.check(queue_policy.get("time_horizon") == hi_batch.get("time_horizon") == 8.0, "queue T=8 policy changed")
    checks.check(queue_policy.get("parallel_shard_count") == hi_batch.get("parallel_shard_count") == 8, "queue shard count changed")
    checks.check(queue_policy.get("can_parallelize") is True, "queue parallel marker changed")
    checks.check(queue_policy.get("source_policy_1e-4_required") is False, "queue source-policy 1e-4 marker changed")

    checks.check(
        local_boundary.get("local_evidence_coverage_examples_count")
        == dashboard.get("local_evidence_coverage_examples")
        == 4,
        "local evidence coverage count changed",
    )
    checks.check(
        local_boundary.get("local_evidence_coverage_examples")
        == dashboard.get("local_evidence_coverage_example_names")
        == EXAMPLES,
        "local evidence coverage example list changed",
    )
    checks.check(
        local_boundary.get("accepted_method_dynamic_order_examples_count")
        == dashboard.get("accepted_method_dynamic_order_example_count")
        == 2,
        "accepted method dynamic-order count changed",
    )
    checks.check(
        local_boundary.get("accepted_method_dynamic_order_examples")
        == dashboard.get("accepted_method_dynamic_order_examples")
        == ["single_pendulum", "double_pendulum"],
        "accepted method dynamic-order examples changed",
    )
    checks.check(
        local_boundary.get("mechanism_coverage_examples_count")
        == dashboard.get("mechanism_coverage_example_count")
        == 2,
        "mechanism coverage count changed",
    )
    checks.check(
        local_boundary.get("mechanism_coverage_examples")
        == dashboard.get("mechanism_coverage_examples")
        == ["four_link", "slider_crank"],
        "mechanism coverage examples changed",
    )
    checks.check(local_boundary.get("local_dynamic_order_examples_count") == dashboard.get("local_dynamic_order_closed_examples") == 2, "local order boundary changed")
    checks.check(local_boundary.get("local_dynamic_order_examples") == dashboard.get("local_dynamic_order_closed_example_names") == ["single_pendulum", "double_pendulum"], "local order example list changed")
    checks.check(local_boundary.get("accepted_source_policy_dynamic_order_examples") == dashboard.get("accepted_source_policy_dynamic_order_examples") == 0, "dashboard source-policy count changed")
    checks.check(local_boundary.get("source_policy_external_superiority_allowed") is False, "dashboard superiority boundary changed")

    checks.check(execution.get("read_only_audit") is True, "audit lost read-only marker")
    checks.check(execution.get("default_1e_4_required") is False, "audit incorrectly requires default 1e-4")
    checks.check(execution.get("heavy_numerical_run_invoked") is False, "audit invoked heavy run")
    checks.check(execution.get("run_v047_invoked") is False, "audit invoked run_v047")
    checks.check(execution.get("v048_runner_invoked") is False, "audit invoked v048 runner")
    checks.check(audit.get("decision") == "choose_full_T8_reproduction_or_explicit_demotion", "decision changed")

    for token in [
        "BOUNDED T=0.1 ROWS COMPLETE",
        "FULL T=8 SOURCE POLICY OPEN",
        "rows ok: `24/24`",
        "model/form groups with three h values: `8/8`",
        "local evidence coverage examples carried from dashboard: `4/4`",
        "accepted method dynamic-order examples carried from dashboard: `2/4`",
        "mechanism-coverage examples carried from dashboard: `2/4`",
        "source-policy dynamic-order examples: `0/4`",
        "external-superiority claim allowed: `False`",
        "choose_full_T8_reproduction_or_explicit_demotion",
    ]:
        checks.check(token in audit_md, f"markdown missing token: {token}")

    if checks.errors:
        print("hi2022_policy_decision_audit=FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("hi2022_policy_decision_audit=PASS")
    print("bounded_rows=24/24")
    print("bounded_groups=8/8")
    print("full_T8_policy_completed=False")
    print("accepted_for_external_superiority=False")
    print("local_evidence_coverage_examples=4/4")
    print("accepted_method_dynamic_order_examples=2/4")
    print("mechanism_coverage_examples=2/4")
    print("source_policy_dynamic_order_examples=0/4")
    print("default_1e-4_required=False")
    print("run_v047_invoked=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
