#!/usr/bin/env python3
"""Build a source-policy closure triage from the flagged baseline rows."""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
OUT_JSON = PAPER / "SOURCE_POLICY_CLOSURE_TRIAGE.json"
OUT_MD = PAPER / "SOURCE_POLICY_CLOSURE_TRIAGE.md"


ACTION_BY_SUITE = {
    "ra2021_absolute_coordinate": {
        "action_class": "fix_or_rerun_public_velocity_mapping_time_grid_norm_runtime",
        "display_action": "fix_or_rerun_public_velocity_mapping_time_grid_norm_runtime",
        "priority": 1,
        "decision": "fix_or_rerun",
        "next_step": (
            "Rerun or independently verify the public rA/rp/reps rows under the "
            "declared state-velocity mapping, time-grid convention, error norm, "
            "and runtime policy."
        ),
    },
    "tfe2026_original_pendulum": {
        "action_class": "resolve_tfe_runner_friction_endpoint_then_rerun_or_demote",
        "display_action": "attempted_not_reproducible_not_promoted",
        "priority": 2,
        "decision": "attempted_not_reproducible_not_promoted",
        "next_step": (
            "No distinct public TFE code artifact was found; paper-spec reconstruction was "
            "attempted but is not source-policy equivalent, so keep these rows not promoted "
            "unless a new source-code-equivalent artifact appears."
        ),
    },
    "hi2022_half_implicit": {
        "action_class": "choose_full_T8_public_policy_or_demote",
        "display_action": "choose_full_T8_public_policy_or_demote",
        "priority": 3,
        "decision": "run_full_policy_or_demote",
        "next_step": (
            "Choose the full T=8 public-policy reproduction or explicitly keep "
            "the bounded pilot as a non-claim."
        ),
    },
    "vp2024_velocity_partitioning": {
        "action_class": "demote_until_velocity_partitioning_code_path_resolved",
        "display_action": "attempted_not_reproducible_not_promoted",
        "priority": 4,
        "decision": "attempted_not_reproducible_not_promoted",
        "next_step": (
            "The public repository tree was rechecked and no distinct VP2024 code path was "
            "found; keep the coordinate-partitioning proxy diagnostic-only unless a new "
            "public path or author artifact appears."
        ),
    },
}


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def main() -> None:
    diagnosis = read_json(PAPER / "EXTERNAL_BASELINE_SOURCE_POLICY_DIAGNOSIS.json")
    suite_disposition = read_json(PAPER / "EXTERNAL_SUITE_DISPOSITION_AUDIT.json")
    comparison = read_json(PAPER / "COMPARISON_OBJECTIVE_CLOSURE_RECONCILIATION_AUDIT.json")

    rows = diagnosis.get("diagnosis_rows", [])
    if not isinstance(rows, list):
        raise ValueError("diagnosis_rows is not a list")

    triage_rows: list[dict[str, Any]] = []
    action_counts: Counter[str] = Counter()
    suite_counts: Counter[str] = Counter()
    example_counts: Counter[str] = Counter()
    category_counts: Counter[str] = Counter()
    risk_counts: Counter[str] = Counter()
    action_to_rows: defaultdict[str, list[dict[str, str]]] = defaultdict(list)

    for row in rows:
        if not isinstance(row, dict):
            continue
        suite = str(row.get("suite", "unknown"))
        action = ACTION_BY_SUITE.get(
            suite,
            {
                "action_class": "manual_review_required",
                "display_action": "manual_review_required",
                "priority": 99,
                "decision": "manual_review",
                "next_step": "Review this source-policy row manually.",
            },
        )
        item = {
            "suite": suite,
            "example": row.get("example"),
            "method": row.get("method"),
            "action_class": action["action_class"],
            "display_action": action["display_action"],
            "post_public_code_disposition": (
                "attempted_not_reproducible_not_promoted"
                if suite in {"tfe2026_original_pendulum", "vp2024_velocity_partitioning"}
                else None
            ),
            "priority": action["priority"],
            "decision": action["decision"],
            "required_closure_action": row.get("required_closure_action"),
            "diagnostic_categories": row.get("diagnostic_categories", []),
            "source_policy_risks": row.get("source_policy_risks", []),
            "velocity_order": row.get("velocity_order"),
            "finest_velocity_error": row.get("finest_velocity_error"),
            "finest_position_error": row.get("finest_position_error"),
            "claim_disposition": row.get("claim_disposition"),
        }
        triage_rows.append(item)
        action_counts[str(action["action_class"])] += 1
        suite_counts[suite] += 1
        example_counts[str(row.get("example"))] += 1
        for category in row.get("diagnostic_categories", []):
            category_counts[str(category)] += 1
        for risk in row.get("source_policy_risks", []):
            risk_counts[str(risk)] += 1
        action_to_rows[str(action["action_class"])].append(
            {
                "suite": suite,
                "example": str(row.get("example")),
                "method": str(row.get("method")),
                "required_closure_action": str(row.get("required_closure_action")),
            }
        )

    action_plan = []
    for suite, action in sorted(ACTION_BY_SUITE.items(), key=lambda item: item[1]["priority"]):
        action_class = str(action["action_class"])
        action_plan.append(
            {
                "priority": action["priority"],
                "suite": suite,
                "action_class": action_class,
                "display_action": action["display_action"],
                "decision": action["decision"],
                "flagged_row_count": action_counts[action_class],
                "rows": action_to_rows[action_class],
                "next_step": action["next_step"],
            }
        )

    result = {
        "schema": "source-policy-closure-triage-v1",
        "status": "triage_only_source_policy_closure_not_run",
        "submission_ready": False,
        "external_superiority_claim": False,
        "common_reference_claim_allowed": comparison.get("common_reference_claim_allowed"),
        "source_policy_superiority_claim_allowed": comparison.get("source_policy_superiority_claim_allowed"),
        "comparison_matrix_closed": comparison.get("comparison_matrix_closed"),
        "triage_scope": {
            "flagged_row_count": len(triage_rows),
            "flagged_examples": sorted(example_counts),
            "flagged_by_example": dict(sorted(example_counts.items())),
            "flagged_by_suite": dict(sorted(suite_counts.items())),
            "action_counts": dict(sorted(action_counts.items())),
            "diagnostic_category_counts": dict(sorted(category_counts.items())),
            "source_policy_risk_counts": dict(sorted(risk_counts.items())),
            "all_four_examples_covered_by_flagged_rows": set(example_counts) == {
                "single_pendulum",
                "double_pendulum",
                "four_link",
                "slider_crank",
            },
        },
        "action_plan": action_plan,
        "triage_rows": triage_rows,
        "closure_boundary": {
            "b2_can_close_now": False,
            "b4_can_close_now": False,
            "reason": (
                "This artifact only triages the 15 flagged source-policy rows; "
                "it does not rerun public baselines, encode the original TFE "
                "pendulum policy, complete the HI2022 T=8 policy, or resolve "
                "the VP source-code path."
            ),
            "default_1e_4_required": False,
            "heavy_numerical_run_invoked": False,
            "accepted_external_superiority_suite_count": suite_disposition.get(
                "accepted_external_superiority_suite_count"
            ),
        },
        "source_files": {
            "diagnosis": "EXTERNAL_BASELINE_SOURCE_POLICY_DIAGNOSIS.json",
            "suite_disposition": "EXTERNAL_SUITE_DISPOSITION_AUDIT.json",
            "comparison_reconciliation": "COMPARISON_OBJECTIVE_CLOSURE_RECONCILIATION_AUDIT.json",
        },
    }

    with OUT_JSON.open("w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, sort_keys=True)
        handle.write("\n")

    lines = [
        "# Source-Policy Closure Triage",
        "",
        "Status: **TRIAGE ONLY - SOURCE-POLICY CLOSURE NOT RUN**",
        "",
        f"- Comparison matrix closed: `{result['comparison_matrix_closed']}`.",
        f"- Common-reference claim allowed: `{result['common_reference_claim_allowed']}`.",
        f"- Source-policy superiority allowed: `{result['source_policy_superiority_claim_allowed']}`.",
        f"- Flagged source-policy rows: `{len(triage_rows)}`.",
        f"- Flagged examples: `{', '.join(result['triage_scope']['flagged_examples'])}`.",
        f"- All four examples covered by flagged rows: `{result['triage_scope']['all_four_examples_covered_by_flagged_rows']}`.",
        f"- B2/B4 can close now: `{result['closure_boundary']['b2_can_close_now']}/{result['closure_boundary']['b4_can_close_now']}`.",
        f"- Default `1e-4` required: `{result['closure_boundary']['default_1e_4_required']}`.",
        f"- Heavy numerical run invoked: `{result['closure_boundary']['heavy_numerical_run_invoked']}`.",
        "",
        "## Action Plan",
        "",
        "| priority | suite | disposition/action | rows | next step |",
        "| ---: | --- | --- | ---: | --- |",
    ]
    for action in action_plan:
        lines.append(
            f"| {action['priority']} | `{action['suite']}` | `{action['display_action']}` | "
            f"{action['flagged_row_count']} | {action['next_step']} |"
        )
    lines.extend(
        [
            "",
            "## Flagged Rows",
            "",
            "| suite | example | method | disposition/action |",
            "| --- | --- | --- | --- |",
        ]
    )
    for row in triage_rows:
        lines.append(
            f"| `{row['suite']}` | `{row['example']}` | `{row['method']}` | "
            f"`{row['display_action']}` |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("source_policy_closure_triage=written")
    print(f"flagged_rows={len(triage_rows)}")
    print("b2_b4_can_close_now=False/False")
    print("heavy_numerical_run_invoked=False")


if __name__ == "__main__":
    main()
