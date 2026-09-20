#!/usr/bin/env python3
"""Build a suite-level disposition audit for external baseline closure."""

from __future__ import annotations

import json
from pathlib import Path


PAPER = Path(__file__).resolve().parent
from paper_paths import LATEX, package_path as manuscript_path
OUT_JSON = PAPER / "EXTERNAL_SUITE_DISPOSITION_AUDIT.json"
OUT_MD = PAPER / "EXTERNAL_SUITE_DISPOSITION_AUDIT.md"

SUITE_LABELS = {
    "tfe2026_original_pendulum": "Chaturvedi--Sandu--Sandu TFE pendulum",
    "ra2021_absolute_coordinate": "Kissel--Taves--Negrut absolute-coordinate suite",
    "hi2022_half_implicit": "Fang--Kissel--Zhang--Negrut half-implicit suite",
    "vp2024_velocity_partitioning": "Kissel--Bakke--Negrut velocity-partitioning suite",
}


def read_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def queue_by_source(queue: dict) -> dict[str, dict]:
    mapping = {}
    for batch in queue.get("batch_queue", []):
        source = batch.get("source_id")
        if source:
            mapping[str(source)] = batch
    return mapping


def batch_for_suite(suite_id: str, queue: dict) -> dict:
    batches = queue.get("batch_queue", [])
    if suite_id == "tfe2026_original_pendulum":
        return next(batch for batch in batches if batch["batch_id"] == "tfe2026_original_pendulum_encoding")
    if suite_id == "ra2021_absolute_coordinate":
        return next(batch for batch in batches if batch["batch_id"] == "ra2021_coarse_same_window_order_time")
    if suite_id == "hi2022_half_implicit":
        return next(batch for batch in batches if batch["batch_id"] == "hi2022_halfimplicit_full_policy_decision")
    if suite_id == "vp2024_velocity_partitioning":
        return next(batch for batch in batches if batch["batch_id"] == "vp2024_velocity_partitioning_code_resolution")
    raise KeyError(suite_id)


def disposition_for_suite(suite: dict, batch: dict) -> dict[str, object]:
    suite_id = str(suite["suite_id"])
    status = str(suite["closure_status"])
    queue_status = str(batch.get("queue_status"))
    if suite_id == "vp2024_velocity_partitioning":
        disposition = "demote_until_code_path_resolved"
        required_next = "resolve public velocity-partitioning code path or state suite demotion"
    elif suite_id == "tfe2026_original_pendulum":
        disposition = "encode_then_run_or_demote"
        required_next = "encode source pendulum setup, output policy, friction law, and norm; then run or demote"
    elif suite_id == "hi2022_half_implicit":
        disposition = "choose_full_T8_run_or_demote"
        required_next = "choose full T=8 public-policy reproduction or explicit demotion"
    elif suite_id == "ra2021_absolute_coordinate":
        disposition = "run_remaining_same_test_or_bound_claim"
        required_next = "finish or rerun coarse same-window shards and record setup identity, reference policy, order, and time"
    else:
        disposition = "unclassified"
        required_next = "classify suite"
    return {
        "suite_id": suite_id,
        "label": SUITE_LABELS.get(suite_id, suite_id),
        "closure_status": status,
        "queue_status": queue_status,
        "parallel_shard_count": batch.get("parallel_shard_count", 0),
        "current_disposition": disposition,
        "claim_allowed_now": "diagnostic_or_literature_only",
        "accepted_external_superiority": False,
        "required_next_action": required_next,
        "closure_action_from_acceptance_sheet": suite.get("closure_action"),
    }


def main() -> None:
    acceptance = read_json(PAPER / "EXTERNAL_SAME_TEST_ACCEPTANCE_SHEET.json")
    queue = read_json(PAPER / "EXTERNAL_SAME_TEST_RUN_QUEUE.json")
    diagnosis = read_json(PAPER / "EXTERNAL_BASELINE_SOURCE_POLICY_DIAGNOSIS.json")
    blocker = read_json(PAPER / "CMAME_BLOCKER_CLOSURE_GATE.json")
    main_tex = read_text(LATEX / "main_cmame.tex")
    flat_tex = read_text(LATEX / "cmame_submission_flat" / "main_cmame_submission.tex")

    suite_rows = []
    for suite in acceptance.get("source_suite_acceptance", []):
        suite_rows.append(disposition_for_suite(suite, batch_for_suite(str(suite["suite_id"]), queue)))

    ready_shards = sum(int(row.get("parallel_shard_count") or 0) for row in suite_rows if "run" in row["current_disposition"])
    demote_or_run = [
        row
        for row in suite_rows
        if row["current_disposition"]
        in {"encode_then_run_or_demote", "choose_full_T8_run_or_demote", "demote_until_code_path_resolved"}
    ]
    run_or_bound = [
        row
        for row in suite_rows
        if row["current_disposition"] == "run_remaining_same_test_or_bound_claim"
    ]
    required_b2 = next(
        item.get("required_to_close", [])
        for item in blocker.get("blockers", [])
        if item.get("id") == "B2"
    )
    required_b4 = next(
        item.get("required_to_close", [])
        for item in blocker.get("blockers", [])
        if item.get("id") == "B4"
    )
    manuscript_disposition_markers = {
        "main_cross_paper_gate_table": "Required same-test comparisons and current external-suite claim boundary" in main_tex,
        "flat_cross_paper_gate_table": "Required same-test comparisons and current external-suite claim boundary" in flat_tex,
        "main_source_policy_diagnosis_table": "Source-policy diagnosis for flagged common-reference baseline rows" in main_tex,
        "flat_source_policy_diagnosis_table": "Source-policy diagnosis for flagged common-reference baseline rows" in flat_tex,
        "main_no_external_superiority": "no external-superiority claim" in main_tex,
        "flat_no_external_superiority": "no external-superiority claim" in flat_tex,
    }

    result = {
        "schema": "external-suite-disposition-audit-v1",
        "status": "suite_dispositions_defined_not_closed",
        "submission_ready": False,
        "suite_count": len(suite_rows),
        "accepted_external_superiority_suite_count": sum(
            1 for row in suite_rows if row["accepted_external_superiority"] is True
        ),
        "same_test_campaign_status": acceptance.get("same_test_campaign_status"),
        "external_superiority_claim": acceptance.get("external_superiority_claim"),
        "suite_dispositions": suite_rows,
        "closure_counts": {
            "parallel_ready_shards_without_default_1e_4": queue.get("coverage_counts", {}).get(
                "parallel_shard_count_without_default_1e-4"
            ),
            "ready_shards_from_disposition_rows": ready_shards,
            "suites_requiring_run_or_demote_decision": len(demote_or_run),
            "suites_requiring_run_or_bounded_claim": len(run_or_bound),
            "accepted_external_dynamic_order_examples_count": acceptance.get("acceptance_counts", {}).get(
                "accepted_external_dynamic_order_examples_count"
            ),
            "flagged_source_policy_rows": diagnosis.get("coverage", {}).get("flagged_row_count"),
            "position_aligned_velocity_mismatch_rows": diagnosis.get("coverage", {}).get(
                "position_aligned_velocity_mismatch_count"
            ),
        },
        "manuscript_disposition_markers": manuscript_disposition_markers,
        "b2_b4_closure": {
            "b2_required_to_close": required_b2,
            "b4_required_to_close": required_b4,
            "b2_can_close_now": False,
            "b4_can_close_now": False,
            "reason": "no accepted external dynamic-order suite and no completed fair implemented baseline/work-precision set",
        },
        "claim_boundary": {
            "external_superiority_allowed": False,
            "suite_dispositions_are_execution_guidance_not_acceptance": True,
            "default_1e_4_required": False,
        },
    }
    with OUT_JSON.open("w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, sort_keys=True)
        handle.write("\n")

    lines = [
        "# External Suite Disposition Audit",
        "",
        "Status: **suite dispositions defined; B2/B4 not closed**.",
        "",
        f"- Suites classified: `{len(suite_rows)}`.",
        f"- Accepted external-superiority suites: `{result['accepted_external_superiority_suite_count']}`.",
        f"- Same-test campaign status: `{result['same_test_campaign_status']}`.",
        f"- Parallel-ready shards without default `1e-4`: `{result['closure_counts']['parallel_ready_shards_without_default_1e_4']}`.",
        f"- Source-policy flagged rows: `{result['closure_counts']['flagged_source_policy_rows']}`.",
        f"- B2 can close now: `{result['b2_b4_closure']['b2_can_close_now']}`.",
        f"- B4 can close now: `{result['b2_b4_closure']['b4_can_close_now']}`.",
        "",
        "## Suite Dispositions",
        "",
        "| suite | current disposition | shards | required next action | claim allowed now |",
        "|---|---|---:|---|---|",
    ]
    for row in suite_rows:
        lines.append(
            "| "
            f"`{row['label']}` | `{row['current_disposition']}` | `{row['parallel_shard_count']}` | "
            f"{row['required_next_action']} | `{row['claim_allowed_now']}` |"
        )
    lines.extend(
        [
            "",
            "## Closure Boundary",
            "",
            "- B2 remains open until included suites are completed under fair same-test policy or explicitly demoted.",
            "- B4 remains open until fair implemented baselines and work/precision curves are available.",
            "- The current manuscript states the no-external-superiority boundary; this audit makes the per-suite execution state explicit.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("external_suite_disposition_audit=written")
    print(f"suites={len(suite_rows)}")
    print("accepted_external_superiority_suite_count=0")
    print("b2_can_close_now=False")
    print("b4_can_close_now=False")


if __name__ == "__main__":
    main()
