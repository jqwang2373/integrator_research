#!/usr/bin/env python3
"""Reconcile external case inventory markers with existing bounded evidence."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
ROOT = PAPER.parent
V048 = ROOT / "v048_cross_paper_same_test_benchmarks" / "results"
OUT_JSON = PAPER / "EXTERNAL_CASE_EVIDENCE_RECONCILIATION.json"
OUT_MD = PAPER / "EXTERNAL_CASE_EVIDENCE_RECONCILIATION.md"

EXAMPLES = ["single_pendulum", "double_pendulum", "four_link", "slider_crank"]


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def group_counts(rows: list[dict[str, str]], source_suite: str) -> dict[str, Any]:
    selected = [row for row in rows if row.get("source_suite") == source_suite]
    examples = sorted({row.get("example") for row in selected if row.get("example")})
    methods = sorted({row.get("method") for row in selected if row.get("method")})
    completed = [row for row in selected if str(row.get("status", "")).startswith("completed")]
    return {
        "row_count": len(selected),
        "completed_row_count": len(completed),
        "not_complete_row_count": len(selected) - len(completed),
        "examples": examples,
        "methods": methods,
        "all_four_examples_present": examples == sorted(EXAMPLES),
        "status_counts": dict(sorted(Counter(row.get("status") for row in selected).items())),
    }


def selected_groups(summary: dict[str, Any], key: str) -> dict[str, Any]:
    block = summary.get(key, {})
    groups = block.get("groups", {}) if isinstance(block, dict) else {}
    complete = [
        name
        for name, row in groups.items()
        if isinstance(row, dict) and row.get("selected_step_trio_completed") is True
    ]
    incomplete = [
        name
        for name, row in groups.items()
        if isinstance(row, dict) and row.get("selected_step_trio_completed") is not True
    ]
    failed_groups = [
        name
        for name, row in groups.items()
        if isinstance(row, dict) and row.get("ok_row_count", 0) < row.get("row_count", 0)
    ]
    return {
        "group_count": len(groups),
        "completed_group_count": len(complete),
        "incomplete_group_count": len(incomplete),
        "complete_groups": complete,
        "incomplete_groups": incomplete,
        "failed_or_partial_groups": failed_groups,
        "selected_step_trio_group_count": block.get("selected_step_trio_group_count"),
        "selected_step_trio_required_group_count": block.get("selected_step_trio_required_group_count"),
        "ok_row_count": block.get("ok_row_count"),
        "row_count": block.get("row_count"),
    }


def source_policy_progress(summary: dict[str, Any]) -> dict[str, Any]:
    ra_order = summary.get("ra2021_order", {})
    ra_double = summary.get("ra2021_double_pendulum_order", {})
    ra_timing = summary.get("ra2021_public_timing", {})
    gauss_single = summary.get("gauss6_fullva_public_horizon_single", {})
    gauss_double = summary.get("gauss6_fullva_public_horizon_double_coarse", {})
    gauss_closed = summary.get("gauss6_fullva_public_horizon_closed_loop", {})
    hi2022 = summary.get("hi2022_halfimplicit", {})

    return {
        "ra2021_public_baselines": {
            "order_groups_completed": (
                int(ra_order.get("public_step_trio_group_count") or 0)
                + int(ra_double.get("selected_step_trio_group_count") or 0)
            ),
            "order_groups_required": (
                int(ra_order.get("public_step_trio_required_group_count") or 0)
                + int(ra_double.get("selected_step_trio_required_group_count") or 0)
            ),
            "order_rows_ok": int(ra_order.get("ok_row_count") or 0)
            + int(ra_double.get("ok_row_count") or 0),
            "order_rows_total": int(ra_order.get("row_count") or 0)
            + int(ra_double.get("row_count") or 0),
            "timing_rows_completed": int(ra_timing.get("public_timing_rows_completed") or 0),
            "timing_rows_required": int(ra_timing.get("public_timing_required_count") or 0),
        },
        "ra2021_local_gauss6_rows": {
            "single_public_policy_rows_completed": gauss_single.get("public_single_step_trio_completed") is True,
            "single_public_policy_order_floor_limited": True,
            "double_public_policy_rows_completed": gauss_double.get("public_double_step_trio_completed") is True,
            "double_current_policy": gauss_double.get("policy"),
            "double_current_step_sizes": gauss_double.get("selected_step_sizes"),
            "closed_loop_public_horizon_rows_completed": (
                gauss_closed.get("public_closed_loop_step_trios_completed") is True
            ),
            "closed_loop_row_kind": "kinematic_reaction_residual_not_true_dynamic_order",
            "accepted_external_dynamic_order_examples": [],
            "accepted_external_dynamic_order_count": 0,
        },
        "hi2022_public_baselines": {
            "bounded_pilot_groups_completed": hi2022.get("selected_step_trio_group_count"),
            "bounded_pilot_groups_required": hi2022.get("selected_step_trio_required_group_count"),
            "bounded_pilot_rows_ok": hi2022.get("ok_row_count"),
            "full_T8_policy_completed": hi2022.get("full_hi2022_campaign_completed") is True,
        },
        "remaining_source_policy_blockers": [
            "local Gauss6/FullVA double-pendulum rows are coarse-first, not the 2021 public h policy",
            "four-link and slider-crank local public-horizon rows are kinematic/reaction residual rows, not true dynamic order rows",
            "single-pendulum local public-policy rows are reference-floor limited",
            "HI2022 is only a bounded T=0.1 pilot, not the full T=8 public policy",
            "TFE source pendulum runner is not implemented",
            "VP2024 distinct public code path is unresolved",
        ],
    }


def cases_by_group(cases: dict[str, Any]) -> dict[str, dict[str, Any]]:
    output: dict[str, dict[str, Any]] = {}
    for item in cases.get("cases", []):
        if not isinstance(item, dict):
            continue
        group = str(item.get("group_id"))
        entry = output.setdefault(
            group,
            {
                "case_count": 0,
                "case_status_counts": Counter(),
                "case_ids": [],
                "blockers": [],
            },
        )
        entry["case_count"] += 1
        entry["case_ids"].append(item.get("case_id"))
        entry["case_status_counts"][item.get("current_status")] += 1
        if item.get("blocker"):
            entry["blockers"].append(item.get("blocker"))
    for entry in output.values():
        entry["case_status_counts"] = dict(sorted(entry["case_status_counts"].items()))
    return output


def main() -> None:
    cases = read_json(PAPER / "CROSS_PAPER_BENCHMARK_CASES.json")
    queue = read_json(PAPER / "EXTERNAL_SAME_TEST_RUN_QUEUE.json")
    closure = read_json(PAPER / "EXTERNAL_SOURCE_POLICY_CLOSURE_MANIFEST.json")
    row_ledger = read_json(PAPER / "SOURCE_POLICY_ROW_CLOSURE_LEDGER.json")
    acceptance = read_json(PAPER / "EXTERNAL_SAME_TEST_ACCEPTANCE_SHEET.json")
    summary = read_json(V048 / "summary_v048.json")
    performance_rows = read_csv(V048 / "four_example_performance_matrix.csv")

    case_groups = cases_by_group(cases)
    closure_by_suite = {row.get("suite_id"): row for row in closure.get("suites", [])}
    queue_by_id = {row.get("batch_id"): row for row in queue.get("batch_queue", [])}

    suites = [
        {
            "suite_id": "ra2021_absolute_coordinate",
            "case_group_id": "ra2021_absolute_coordinate",
            "queue_batch_id": "ra2021_coarse_same_window_order_time",
            "bounded_evidence_present": True,
            "full_source_policy_campaign_completed": False,
            "source_policy_closed": False,
            "external_superiority_ready": False,
            "case_inventory_interpretation": "not_run markers mean the full source-policy same-test campaign remains open; bounded/coarse evidence exists separately",
            "performance_rows": group_counts(performance_rows, "ra2021_public_code"),
            "extra_performance_rows": group_counts(performance_rows, "v048_public_horizon"),
            "order_group_status": {
                "single_four_slider_public_order": selected_groups(summary, "ra2021_order"),
                "double_pendulum_public_dynamic_self_reference": selected_groups(
                    summary,
                    "ra2021_double_pendulum_coarse_order",
                ),
            },
        },
        {
            "suite_id": "hi2022_half_implicit",
            "case_group_id": "hi2022_half_implicit",
            "queue_batch_id": "hi2022_halfimplicit_full_policy_decision",
            "bounded_evidence_present": True,
            "full_source_policy_campaign_completed": False,
            "source_policy_closed": False,
            "external_superiority_ready": False,
            "case_inventory_interpretation": "bounded T=0.1 pilot exists; full T=8 source policy is still a run-or-demote decision",
            "performance_rows": group_counts(performance_rows, "hi2022_halfimplicit"),
            "order_group_status": {
                "bounded_T0p1_groups": selected_groups(summary, "hi2022_halfimplicit"),
            },
        },
        {
            "suite_id": "tfe2026_original_pendulum",
            "case_group_id": "tfe2026_original_pendulum",
            "queue_batch_id": "tfe2026_original_pendulum_encoding",
            "bounded_evidence_present": False,
            "full_source_policy_campaign_completed": False,
            "source_policy_closed": False,
            "external_superiority_ready": False,
            "case_inventory_interpretation": "source pendulum setup, friction law, error norm, and output policy are not encoded",
            "performance_rows": group_counts(performance_rows, "tfe2026_pdf"),
            "order_group_status": {},
        },
        {
            "suite_id": "vp2024_velocity_partitioning",
            "case_group_id": "vp2024_velocity_partitioning",
            "queue_batch_id": "vp2024_velocity_partitioning_code_resolution",
            "bounded_evidence_present": False,
            "full_source_policy_campaign_completed": False,
            "source_policy_closed": False,
            "external_superiority_ready": False,
            "case_inventory_interpretation": "distinct velocity-partitioning public code path is unresolved; coordinate-partitioning proxy is not source-policy evidence",
            "performance_rows": group_counts(performance_rows, "vp2024_unresolved"),
            "order_group_status": {},
        },
    ]

    for suite in suites:
        suite_id = suite["suite_id"]
        case_group_id = suite["case_group_id"]
        queue_batch_id = suite["queue_batch_id"]
        closure_row = closure_by_suite.get(suite_id, {})
        queue_row = queue_by_id.get(queue_batch_id, {})
        case_group = case_groups.get(case_group_id, {})
        suite["case_inventory"] = case_group
        suite["queue_status"] = queue_row.get("queue_status")
        suite["queue_next_action"] = queue_row.get("next_action")
        suite["parallel_shard_count"] = queue_row.get("parallel_shard_count")
        suite["closure_manifest_status"] = closure_row.get("current_status")
        suite["claim_allowed_now"] = closure_row.get("claim_allowed_now")
        suite["required_to_close"] = closure_row.get("required_to_close", [])

    result = {
        "schema": "external-case-evidence-reconciliation-v1",
        "status": "bounded_evidence_present_full_source_policy_campaign_open",
        "submission_ready": False,
        "examples": EXAMPLES,
        "source_policy_progress": source_policy_progress(summary),
        "same_test_campaign_status": closure.get("same_test_campaign_status"),
        "case_inventory_case_count": sum(row.get("case_count", 0) for row in case_groups.values()),
        "case_inventory_status_counts": dict(
            sorted(
                Counter(
                    case.get("current_status")
                    for case in cases.get("cases", [])
                    if isinstance(case, dict)
                ).items()
            )
        ),
        "bounded_or_public_evidence_suites": [
            suite["suite_id"] for suite in suites if suite["bounded_evidence_present"]
        ],
        "not_ready_or_demote_suites": [
            suite["suite_id"] for suite in suites if not suite["bounded_evidence_present"]
        ],
        "source_policy_row_ledger": {
            "flagged_rows": row_ledger.get("coverage", {}).get("flagged_row_count"),
            "flagged_by_example": row_ledger.get("coverage", {}).get("flagged_by_example"),
            "rows_source_policy_closed": row_ledger.get("coverage", {}).get("rows_source_policy_closed"),
            "rows_external_superiority_ready": row_ledger.get("coverage", {}).get(
                "rows_external_superiority_ready"
            ),
        },
        "acceptance_boundary": {
            "accepted_external_dynamic_order_examples_count": acceptance.get("acceptance_counts", {}).get(
                "accepted_external_dynamic_order_examples_count"
            ),
            "external_superiority_claim": acceptance.get("external_superiority_claim"),
            "b2_can_close_now": closure.get("b2_can_close_now"),
            "b4_can_close_now": closure.get("b4_can_close_now"),
        },
        "execution_policy": {
            "read_only_existing_artifacts": True,
            "default_1e_4_required": False,
            "heavy_numerical_run_invoked": False,
            "run_v047_invoked": False,
            "v048_runner_invoked": False,
        },
        "suites": suites,
        "interpretation": {
            "case_inventory_not_run_is_not_zero_evidence": True,
            "reason": (
                "The case inventory tracks the full source-policy same-test campaign. "
                "The reconciliation records bounded/coarse evidence already present in "
                "v048 while keeping source-policy closure and external-superiority claims open."
            ),
            "current_source_policy_reading": (
                "The 2021 public baselines and timing rows are substantially complete, "
                "but local Gauss6/FullVA rows are not yet complete source-policy dynamic "
                "order/work rows for all four examples."
            ),
        },
    }

    with OUT_JSON.open("w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, sort_keys=True)
        handle.write("\n")

    lines = [
        "# External Case Evidence Reconciliation",
        "",
        "Status: **BOUNDED EVIDENCE PRESENT; FULL SOURCE-POLICY CAMPAIGN OPEN**.",
        "",
        f"- Same-test campaign status: `{result['same_test_campaign_status']}`.",
        f"- Case inventory status counts: `{result['case_inventory_status_counts']}`.",
        f"- Bounded/public evidence suites: `{', '.join(result['bounded_or_public_evidence_suites'])}`.",
        f"- Not-ready or demote suites: `{', '.join(result['not_ready_or_demote_suites'])}`.",
        (
            "- 2021 public baseline order groups: "
            f"`{result['source_policy_progress']['ra2021_public_baselines']['order_groups_completed']}/"
            f"{result['source_policy_progress']['ra2021_public_baselines']['order_groups_required']}`."
        ),
        (
            "- 2021 public timing rows: "
            f"`{result['source_policy_progress']['ra2021_public_baselines']['timing_rows_completed']}/"
            f"{result['source_policy_progress']['ra2021_public_baselines']['timing_rows_required']}`."
        ),
        (
            "- Local Gauss6/FullVA source-policy dynamic-order examples accepted: "
            f"`{result['source_policy_progress']['ra2021_local_gauss6_rows']['accepted_external_dynamic_order_count']}/4`."
        ),
        f"- Source-policy rows closed: `{result['source_policy_row_ledger']['rows_source_policy_closed']}/15`.",
        f"- External-superiority-ready rows: `{result['source_policy_row_ledger']['rows_external_superiority_ready']}/15`.",
        f"- Accepted external dynamic-order examples: `{result['acceptance_boundary']['accepted_external_dynamic_order_examples_count']}`.",
        f"- B2/B4 can close now: `{result['acceptance_boundary']['b2_can_close_now']}/{result['acceptance_boundary']['b4_can_close_now']}`.",
        f"- Default `1e-4` required: `{result['execution_policy']['default_1e_4_required']}`.",
        f"- Heavy numerical run invoked: `{result['execution_policy']['heavy_numerical_run_invoked']}`.",
        "",
        "## Suite Reconciliation",
        "",
        "| suite | case inventory | bounded evidence | performance rows | source-policy closed | allowed use |",
        "| --- | --- | --- | ---: | --- | --- |",
    ]
    for suite in suites:
        case_status = suite.get("case_inventory", {}).get("case_status_counts", {})
        perf = suite.get("performance_rows", {})
        extra = suite.get("extra_performance_rows", {})
        completed = int(perf.get("completed_row_count") or 0) + int(extra.get("completed_row_count") or 0)
        total = int(perf.get("row_count") or 0) + int(extra.get("row_count") or 0)
        lines.append(
            f"| `{suite['suite_id']}` | `{case_status}` | `{suite['bounded_evidence_present']}` | "
            f"{completed}/{total} | `{suite['source_policy_closed']}` | `{suite['claim_allowed_now']}` |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "The case inventory's `not_run` markers refer to the full source-policy",
            "same-test campaign. They do not erase bounded/coarse evidence already",
            "present in v048. They also do not close source-policy reproduction,",
            "B2/B4, or any external-superiority claim.",
            "",
            "The current 2021 public-code reading is more specific: the public",
            "baseline order and timing rows are complete, but the local",
            "Gauss6/FullVA rows are not yet complete source-policy dynamic",
            "order/work rows for all four examples.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("external_case_evidence_reconciliation=written")
    print("bounded_evidence_suites=ra2021_absolute_coordinate,hi2022_half_implicit")
    print("not_ready_or_demote_suites=tfe2026_original_pendulum,vp2024_velocity_partitioning")
    print("source_policy_rows_closed=0/15")
    print("external_superiority_ready_rows=0/15")


if __name__ == "__main__":
    main()
