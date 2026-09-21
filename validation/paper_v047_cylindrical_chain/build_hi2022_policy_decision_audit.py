#!/usr/bin/env python3
"""Build the HI2022 policy-decision audit from existing v048 evidence.

This is a read-only evidence classifier. It does not run HI2022 shards and it
does not promote the bounded T=0.1 pilot rows to source-policy reproduction.
"""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
ROOT = PAPER.parent
V048 = ROOT.parent / "numerics" / "v048_cross_paper_same_test_benchmarks" / "results"
ROWS_CSV = V048 / "hi2022_halfimplicit_rows.csv"
SUMMARY_JSON = V048 / "summary_v048.json"
OUT_JSON = PAPER / "HI2022_POLICY_DECISION_AUDIT.json"
OUT_MD = PAPER / "HI2022_POLICY_DECISION_AUDIT.md"

EXAMPLES = ["single_pendulum", "double_pendulum", "four_link", "slider_crank"]
FORMS = ["rA", "rA_half"]


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def unique_sorted(rows: list[dict[str, str]], key: str) -> list[str]:
    return sorted({row.get(key, "") for row in rows if row.get(key, "")})


def unique_floats(rows: list[dict[str, str]], key: str) -> list[float]:
    return sorted({float(row[key]) for row in rows if row.get(key)})


def queue_batch(queue: dict[str, Any], batch_id: str) -> dict[str, Any]:
    for batch in queue.get("batch_queue", []):
        if isinstance(batch, dict) and batch.get("batch_id") == batch_id:
            return batch
    raise KeyError(batch_id)


def row_count_by_group(rows: list[dict[str, str]]) -> dict[str, dict[str, Any]]:
    grouped: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[(row.get("model", ""), row.get("form", ""))].append(row)

    result = {}
    for model in EXAMPLES:
        for form in FORMS:
            group_rows = grouped.get((model, form), [])
            summary_key = f"{form}:{model}"
            result[summary_key] = {
                "model": model,
                "form": form,
                "row_count": len(group_rows),
                "ok_row_count": sum(1 for row in group_rows if row.get("status") == "ok"),
                "step_sizes": unique_floats(group_rows, "h"),
                "reference_modes": unique_sorted(group_rows, "reference_mode"),
                "reference_policies": unique_sorted(group_rows, "reference_policy"),
                "execution_paths": unique_sorted(group_rows, "execution_path"),
            }
    return result


def main() -> None:
    rows = read_csv(ROWS_CSV)
    summary = read_json(SUMMARY_JSON)
    queue = read_json(PAPER / "EXTERNAL_SAME_TEST_RUN_QUEUE.json")
    acceptance = read_json(PAPER / "EXTERNAL_SAME_TEST_ACCEPTANCE_SHEET.json")
    dashboard = read_json(PAPER / "FOUR_EXAMPLE_SOURCE_POLICY_DASHBOARD.json")

    hi_summary = summary.get("hi2022_halfimplicit", {})
    hi_batch = queue_batch(queue, "hi2022_halfimplicit_full_policy_decision")
    row_groups = row_count_by_group(rows)

    existing_policy = {
        "policy": rows[0].get("policy") if rows else None,
        "source_suite": rows[0].get("source_suite") if rows else None,
        "run_mode": hi_summary.get("run_mode"),
        "t_end_values": unique_floats(rows, "t_end"),
        "step_sizes": unique_floats(rows, "h"),
        "reference_h_values": unique_floats(rows, "reference_h"),
        "forms": [form for form in FORMS if any(row.get("form") == form for row in rows)],
        "models": [model for model in EXAMPLES if any(row.get("model") == model for row in rows)],
        "row_count": len(rows),
        "ok_row_count": sum(1 for row in rows if row.get("status") == "ok"),
        "group_count": len(row_groups),
        "groups_with_three_step_sizes": sum(1 for item in row_groups.values() if item["row_count"] == 3),
        "status_counts": dict(sorted(Counter(row.get("status") for row in rows).items())),
        "reference_modes": unique_sorted(rows, "reference_mode"),
        "reference_policies": unique_sorted(rows, "reference_policy"),
        "execution_paths": unique_sorted(rows, "execution_path"),
        "row_groups": row_groups,
    }

    queue_policy = {
        "batch_id": hi_batch.get("batch_id"),
        "queue_status": hi_batch.get("queue_status"),
        "models": hi_batch.get("models"),
        "public_forms": hi_batch.get("public_forms"),
        "time_horizon": hi_batch.get("time_horizon"),
        "step_sizes": hi_batch.get("step_sizes"),
        "reference_h": hi_batch.get("reference_h"),
        "parallel_shard_count": hi_batch.get("parallel_shard_count"),
        "can_parallelize": hi_batch.get("can_parallelize"),
        "source_policy_1e-4_required": hi_batch.get("source_policy_1e-4_required"),
        "next_action": hi_batch.get("next_action"),
    }

    result = {
        "schema": "hi2022-policy-decision-audit-v1",
        "status": "bounded_T0p1_rows_complete_full_T8_source_policy_open",
        "submission_ready": False,
        "suite_id": "hi2022_half_implicit",
        "source_suite": "hi2022_fang_kissel_zhang_negrut",
        "evidence_class": "bounded_pilot_only_not_source_policy_reproduction",
        "existing_bounded_evidence": existing_policy,
        "source_policy_required_before_external_superiority": {
            "full_T8_policy_required": True,
            "full_T8_policy_completed": bool(hi_summary.get("full_hi2022_campaign_completed")),
            "source_policy_reproduction_closed": False,
            "accepted_for_bounded_evidence": True,
            "accepted_for_external_superiority": False,
            "accepted_source_policy_dynamic_order_examples_count": acceptance.get("acceptance_counts", {}).get(
                "accepted_source_policy_dynamic_order_examples_count"
            ),
            "accepted_external_dynamic_order_examples_count": acceptance.get("acceptance_counts", {}).get(
                "accepted_external_dynamic_order_examples_count"
            ),
            "external_superiority_claim_allowed": False,
            "paper_direct_error_superiority_allowed": False,
        },
        "queue_policy_decision": queue_policy,
        "local_order_boundary": {
            "local_evidence_coverage_examples_count": dashboard.get("local_evidence_coverage_examples"),
            "local_evidence_coverage_examples": dashboard.get("local_evidence_coverage_example_names"),
            "accepted_method_dynamic_order_examples_count": dashboard.get(
                "accepted_method_dynamic_order_example_count"
            ),
            "accepted_method_dynamic_order_examples": dashboard.get("accepted_method_dynamic_order_examples"),
            "mechanism_coverage_examples_count": dashboard.get("mechanism_coverage_example_count"),
            "mechanism_coverage_examples": dashboard.get("mechanism_coverage_examples"),
            "local_dynamic_order_examples_count": dashboard.get("local_dynamic_order_closed_examples"),
            "local_dynamic_order_examples": dashboard.get("local_dynamic_order_closed_example_names"),
            "accepted_source_policy_dynamic_order_examples": dashboard.get(
                "accepted_source_policy_dynamic_order_examples"
            ),
            "source_policy_external_superiority_allowed": dashboard.get("source_policy_external_superiority_allowed"),
        },
        "execution_policy": {
            "read_only_audit": True,
            "default_1e_4_required": False,
            "heavy_numerical_run_invoked": False,
            "run_v047_invoked": False,
            "v048_runner_invoked": False,
        },
        "decision": "choose_full_T8_reproduction_or_explicit_demotion",
        "recommended_next_action": "choose_full_T8_reproduction_or_explicit_demotion",
        "claim_policy": {
            "allowed_now": [
                "HI2022 bounded T=0.1 pilot rows as diagnostic evidence",
                "HI2022 queue/workload planning without default 1e-4",
            ],
            "forbidden_now": [
                "HI2022 full T=8 source-policy reproduction",
                "HI2022 external-superiority claim",
                "paper-level direct-error superiority based on HI2022 bounded pilot rows",
            ],
        },
        "source_files": {
            "rows_csv": "../../numerics/v048_cross_paper_same_test_benchmarks/results/hi2022_halfimplicit_rows.csv",
            "summary_v048": "../../numerics/v048_cross_paper_same_test_benchmarks/results/summary_v048.json",
            "run_queue": "EXTERNAL_SAME_TEST_RUN_QUEUE.json",
            "acceptance_sheet": "EXTERNAL_SAME_TEST_ACCEPTANCE_SHEET.json",
            "four_example_source_policy_dashboard": "FOUR_EXAMPLE_SOURCE_POLICY_DASHBOARD.json",
        },
    }

    with OUT_JSON.open("w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, sort_keys=True)
        handle.write("\n")

    lines = [
        "# HI2022 Policy Decision Audit",
        "",
        "Status: **BOUNDED T=0.1 ROWS COMPLETE; FULL T=8 SOURCE POLICY OPEN**",
        "",
        "This audit classifies the existing Fang--Kissel--Zhang--Negrut half-implicit evidence.",
        "It does not run any numerical shard and does not promote the bounded pilot to an external-superiority claim.",
        "",
        "## Existing Evidence",
        "",
        f"- source suite: `{result['source_suite']}`",
        f"- evidence class: `{result['evidence_class']}`",
        f"- existing policy: `{existing_policy['policy']}`",
        f"- existing horizon: `{existing_policy['t_end_values']}`",
        f"- existing h-grid: `{existing_policy['step_sizes']}`",
        f"- reference h: `{existing_policy['reference_h_values']}`",
        f"- rows ok: `{existing_policy['ok_row_count']}/{existing_policy['row_count']}`",
        f"- model/form groups with three h values: `{existing_policy['groups_with_three_step_sizes']}/8`",
        "",
        "## Source-Policy Boundary",
        "",
        f"- full `T=8` source policy completed: `{result['source_policy_required_before_external_superiority']['full_T8_policy_completed']}`",
        f"- accepted for bounded evidence: `{result['source_policy_required_before_external_superiority']['accepted_for_bounded_evidence']}`",
        f"- accepted for external superiority: `{result['source_policy_required_before_external_superiority']['accepted_for_external_superiority']}`",
        f"- local evidence coverage examples carried from dashboard: `{result['local_order_boundary']['local_evidence_coverage_examples_count']}/4`",
        f"- accepted method dynamic-order examples carried from dashboard: `{result['local_order_boundary']['accepted_method_dynamic_order_examples_count']}/4`",
        f"- mechanism-coverage examples carried from dashboard: `{result['local_order_boundary']['mechanism_coverage_examples_count']}/4`",
        f"- source-policy dynamic-order examples: `{result['source_policy_required_before_external_superiority']['accepted_source_policy_dynamic_order_examples_count']}/4`",
        f"- external-superiority claim allowed: `{result['source_policy_required_before_external_superiority']['external_superiority_claim_allowed']}`",
        "",
        "## Existing Row Groups",
        "",
        "| Group | Rows ok | h values | Reference policy | Execution path |",
        "| --- | ---: | --- | --- | --- |",
    ]
    for group_id in sorted(row_groups):
        item = row_groups[group_id]
        lines.append(
            f"| `{group_id}` | `{item['ok_row_count']}/{item['row_count']}` | "
            f"`{item['step_sizes']}` | `{', '.join(item['reference_policies'])}` | "
            f"`{', '.join(item['execution_paths'])}` |"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"`{result['decision']}`.",
            "",
            "Before any CMAME external-superiority statement, either run the full `T=8` source-policy reproduction",
            "or explicitly demote this suite to bounded diagnostic evidence in the manuscript.",
            "",
            "## Validator",
            "",
            "Run:",
            "",
            "```bash",
            "../../.venv_sbel/bin/python validate_hi2022_policy_decision_audit.py",
            "```",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
