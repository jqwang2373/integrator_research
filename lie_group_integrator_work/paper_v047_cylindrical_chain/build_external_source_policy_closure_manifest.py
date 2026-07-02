#!/usr/bin/env python3
"""Build the B2/B4 external source-policy closure manifest.

The manifest is deliberately stricter than the bounded common-reference table:
it records what is still needed before any source-paper reproduction or
external-superiority claim can enter a CMAME submission.
"""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


PAPER = Path(__file__).resolve().parent
ROOT = PAPER.parent
V048 = ROOT / "v048_cross_paper_same_test_benchmarks" / "results"
OUT_JSON = PAPER / "EXTERNAL_SOURCE_POLICY_CLOSURE_MANIFEST.json"
OUT_MD = PAPER / "EXTERNAL_SOURCE_POLICY_CLOSURE_MANIFEST.md"

EXAMPLES = ["single_pendulum", "double_pendulum", "four_link", "slider_crank"]

SUITE_ROWS = {
    "ra2021_absolute_coordinate": {
        "label": "Kissel--Taves--Negrut absolute-coordinate suite",
        "performance_sources": {"ra2021_public_code", "v048_public_horizon"},
        "current_status": "partial_public_policy_evidence_not_same-policy_superiority",
        "required_to_close": [
            "local Gauss6/FullVA dynamic order/work rows under the same public policy for all four examples",
            "declared state/velocity output map and norm identical to the source scripts",
            "runtime and Newton/work metrics reported under the same timing policy",
            "explicit bounded/no-superiority decision if only coarse same-window rows are retained",
        ],
        "claim_allowed_now": "baseline_order_time_summary_only",
    },
    "hi2022_half_implicit": {
        "label": "Fang--Kissel--Zhang--Negrut half-implicit suite",
        "performance_sources": {"hi2022_halfimplicit"},
        "current_status": "bounded_T0p1_pilot_not_full_T8_public_policy",
        "required_to_close": [
            "choose full T=8 public-policy reproduction or explicit demotion",
            "match the source paper's step sizes, reference policy, energy/constraint metrics, and work metrics",
            "record rA and rA_half on the selected policy before any superiority statement",
        ],
        "claim_allowed_now": "bounded_pilot_only",
    },
    "tfe2026_original_pendulum": {
        "label": "Chaturvedi--Sandu--Sandu TFE pendulum",
        "performance_sources": {"tfe2026_pdf"},
        "current_status": "source_policy_runner_friction_endpoint_and_work_rows_open",
        "required_to_close": [
            "prove or replace the candidate planar runner with a source-policy absolute-coordinate DAE runner",
            "replace the local Brown--McPhee published-formula surrogate with a source-code-equivalent friction law",
            "resolve the full T=10 endpoint/output policy for endpoint-incompatible published h rows",
            "run or explicitly demote Newmark, trapezoidal, TFE m=1/m=2/m=3, and Gauss6/FullVA work rows",
            "keep TFE m=3 as expected order five unless a separate source-policy reproduction proves otherwise",
        ],
        "claim_allowed_now": "formal_order_literature_comparator_only",
    },
    "vp2024_velocity_partitioning": {
        "label": "Kissel--Bakke--Negrut velocity-partitioning suite",
        "performance_sources": {"vp2024_unresolved"},
        "current_status": "public_code_path_unresolved_or_proxy_only",
        "required_to_close": [
            "resolve the distinct public velocity-partitioning code path or explicitly demote the suite",
            "extract its source time windows, step sizes, reference policy, and runtime metrics",
            "do not use the local coordinate-partitioning proxy as a source-policy reproduction",
        ],
        "claim_allowed_now": "code-path-unresolved_related_work_only",
    },
}


def read_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def batch_by_source(queue: dict) -> dict[str, dict]:
    mapping = {}
    for batch in queue.get("batch_queue", []):
        source = batch.get("source_id")
        if source:
            mapping[str(source)] = batch
    return mapping


def suite_queue_batch(suite_id: str, queue: dict) -> dict:
    batches = queue.get("batch_queue", [])
    batch_id = {
        "ra2021_absolute_coordinate": "ra2021_coarse_same_window_order_time",
        "hi2022_half_implicit": "hi2022_halfimplicit_full_policy_decision",
        "tfe2026_original_pendulum": "tfe2026_original_pendulum_encoding",
        "vp2024_velocity_partitioning": "vp2024_velocity_partitioning_code_resolution",
    }[suite_id]
    for batch in batches:
        if batch.get("batch_id") == batch_id:
            return batch
    raise KeyError(batch_id)


def count_performance_rows(rows: list[dict[str, str]], source_ids: set[str]) -> dict:
    selected = [row for row in rows if row.get("source_suite") in source_ids]
    status_counts = Counter(row.get("status") for row in selected)
    completed = sum(1 for row in selected if str(row.get("status", "")).startswith("completed"))
    not_complete = sum(1 for row in selected if not str(row.get("status", "")).startswith("completed"))
    examples = sorted({row.get("example") for row in selected if row.get("example")})
    methods = sorted({row.get("method") for row in selected if row.get("method")})
    return {
        "row_count": len(selected),
        "completed_row_count": completed,
        "not_complete_row_count": not_complete,
        "status_counts": dict(sorted(status_counts.items())),
        "examples": examples,
        "methods": methods,
        "all_four_examples_present": examples == sorted(EXAMPLES),
    }


def main() -> None:
    acceptance = read_json(PAPER / "EXTERNAL_SAME_TEST_ACCEPTANCE_SHEET.json")
    queue = read_json(PAPER / "EXTERNAL_SAME_TEST_RUN_QUEUE.json")
    source_policy = read_json(PAPER / "ALL_EXAMPLES_SOURCE_POLICY_AUDIT.json")
    suite_disposition = read_json(PAPER / "EXTERNAL_SUITE_DISPOSITION_AUDIT.json")
    forensic = read_json(V048 / "all_examples_apples_to_apples_forensic_audit.json")
    performance_summary = read_json(V048 / "four_example_performance_summary.json")
    performance_rows = read_csv(V048 / "four_example_performance_matrix.csv")

    flagged_by_suite = source_policy.get("coverage", {}).get("flagged_by_suite", {})
    disposition_by_suite = {
        row.get("suite_id"): row for row in suite_disposition.get("suite_dispositions", [])
    }
    suites = []
    runnable_now = []
    demote_or_encode = []
    for suite_id, spec in SUITE_ROWS.items():
        batch = suite_queue_batch(suite_id, queue)
        counts = count_performance_rows(performance_rows, set(spec["performance_sources"]))
        disposition = disposition_by_suite.get(suite_id, {})
        can_parallelize = bool(batch.get("can_parallelize"))
        if can_parallelize and int(batch.get("parallel_shard_count") or 0) > 0:
            runnable_now.append(suite_id)
        else:
            demote_or_encode.append(suite_id)
        suites.append(
            {
                "suite_id": suite_id,
                "label": spec["label"],
                "current_status": spec["current_status"],
                "queue_status": batch.get("queue_status"),
                "current_disposition": disposition.get("current_disposition"),
                "parallel_shard_count": batch.get("parallel_shard_count", 0),
                "can_parallelize": can_parallelize,
                "source_policy_flagged_rows": flagged_by_suite.get(suite_id, 0),
                "performance_rows": counts,
                "claim_allowed_now": spec["claim_allowed_now"],
                "accepted_for_external_superiority": False,
                "required_to_close": spec["required_to_close"],
                "next_action": batch.get("next_action"),
            }
        )

    acceptance_counts = acceptance.get("acceptance_counts", {})
    closure_requirements = [
        {
            "id": "SP1",
            "requirement": "all included suites have source time horizon, h-grid, reference, norm, output map, and runtime policy closed",
            "satisfied": False,
            "blocking_suites": [
                row["suite_id"]
                for row in suites
                if row["accepted_for_external_superiority"] is False
            ],
        },
        {
            "id": "SP2",
            "requirement": "all four examples have accepted external dynamic-order rows under source policy",
            "satisfied": acceptance_counts.get("accepted_external_dynamic_order_examples_count") == 4,
            "accepted_external_dynamic_order_examples_count": acceptance_counts.get(
                "accepted_external_dynamic_order_examples_count"
            ),
        },
        {
            "id": "SP3",
            "requirement": "paper-level direct external error superiority is allowed only after source-policy reproduction",
            "satisfied": forensic.get("strict_external_error_claim_allowed_rows") > 0
            and forensic.get("source_policy_reproduction") is True,
            "strict_external_error_claim_allowed_rows": forensic.get("strict_external_error_claim_allowed_rows"),
            "source_policy_reproduction": forensic.get("source_policy_reproduction"),
        },
        {
            "id": "SP4",
            "requirement": "B2/B4 close only after fair implemented baselines and work/precision evidence are complete",
            "satisfied": False,
            "b2_can_close_now": False,
            "b4_can_close_now": False,
        },
    ]

    result = {
        "schema": "external-source-policy-closure-manifest-v1",
        "status": "not_closed_source_policy_reproduction_required",
        "submission_ready": False,
        "examples": EXAMPLES,
        "same_test_campaign_status": acceptance.get("same_test_campaign_status"),
        "source_policy_reproduction": False,
        "external_superiority_claim_allowed": False,
        "paper_direct_error_superiority_claim_allowed": False,
        "b2_can_close_now": False,
        "b4_can_close_now": False,
        "performance_matrix": {
            "row_count": performance_summary.get("row_count"),
            "completed_row_count": performance_summary.get("completed_row_count"),
            "partial_row_count": performance_summary.get("partial_row_count"),
            "not_complete_row_count": performance_summary.get("not_complete_row_count"),
            "external_superiority_claim": performance_summary.get("external_superiority_claim"),
        },
        "common_reference_boundary": {
            "bounded_common_reference_diagnostic_rows": forensic.get("bounded_common_reference_diagnostic_rows"),
            "strict_external_error_claim_allowed_rows": forensic.get("strict_external_error_claim_allowed_rows"),
            "all_method_example_cells_checked": forensic.get("row_count"),
        },
        "source_policy_flagged_rows": source_policy.get("coverage", {}).get("flagged_row_count"),
        "source_policy_flagged_raw_rows": source_policy.get("coverage", {}).get("flagged_raw_row_count"),
        "source_policy_flagged_by_suite": flagged_by_suite,
        "runnable_parallel_suites": runnable_now,
        "not_ready_or_demote_suites": demote_or_encode,
        "parallel_ready_shards_without_default_1e_4": queue.get("coverage_counts", {}).get(
            "parallel_shard_count_without_default_1e-4"
        ),
        "default_1e_4_required": False,
        "heavy_numerical_run_invoked": False,
        "suites": suites,
        "closure_requirements": closure_requirements,
        "claim_policy": {
            "allowed_now": [
                "conditional formal order comparison against the m=3 TFE formula target",
                "bounded common-reference diagnostic order/error table",
                "public baseline order/time summaries as non-superiority evidence",
            ],
            "forbidden_now": [
                "paper-level external direct-error superiority",
                "complete source-paper reproduction",
                "VP2024 source-code reproduction",
                "full T=8 HI2022 source-policy superiority",
                "original TFE pendulum superiority before encoding the source setup",
            ],
        },
    }

    with OUT_JSON.open("w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, sort_keys=True)
        handle.write("\n")

    lines = [
        "# External Source-Policy Closure Manifest",
        "",
        "Status: **not closed - source-policy reproduction required**.",
        "",
        f"- Examples: `{', '.join(EXAMPLES)}`.",
        f"- Performance rows: `{result['performance_matrix']['completed_row_count']}/{result['performance_matrix']['row_count']}` completed.",
        f"- Not-complete performance rows: `{result['performance_matrix']['not_complete_row_count']}`.",
        f"- Bounded common-reference diagnostic rows: `{result['common_reference_boundary']['bounded_common_reference_diagnostic_rows']}`.",
        f"- Strict external error-claim rows allowed: `{result['common_reference_boundary']['strict_external_error_claim_allowed_rows']}`.",
        f"- Source-policy flagged rows/raw rows: `{result['source_policy_flagged_rows']}/{result['source_policy_flagged_raw_rows']}`.",
        f"- Parallel-ready shards without default `1e-4`: `{result['parallel_ready_shards_without_default_1e_4']}`.",
        f"- B2/B4 can close now: `{result['b2_can_close_now']}/{result['b4_can_close_now']}`.",
        f"- External superiority claim allowed: `{result['external_superiority_claim_allowed']}`.",
        "",
        "## Suite Closure State",
        "",
        "| suite | status | rows completed/total | flagged rows | shards | claim allowed now | next action |",
        "|---|---|---:|---:|---:|---|---|",
    ]
    for row in suites:
        counts = row["performance_rows"]
        lines.append(
            "| "
            f"`{row['label']}` | `{row['current_status']}` | "
            f"`{counts['completed_row_count']}/{counts['row_count']}` | "
            f"`{row['source_policy_flagged_rows']}` | `{row['parallel_shard_count']}` | "
            f"`{row['claim_allowed_now']}` | {row['next_action']} |"
        )
    lines.extend(
        [
            "",
            "## Closure Requirements",
            "",
            "| id | requirement | satisfied |",
            "|---|---|---:|",
        ]
    )
    for req in closure_requirements:
        lines.append(f"| `{req['id']}` | {req['requirement']} | `{req['satisfied']}` |")
    lines.extend(
        [
            "",
            "## Claim Policy",
            "",
            "- Allowed now: conditional formal order comparison, bounded common-reference diagnostics, and public baseline summaries as non-superiority evidence.",
            "- Forbidden now: paper-level external direct-error superiority, complete source-paper reproduction, VP2024 reproduction, full T=8 HI2022 superiority, and original TFE pendulum superiority.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("external_source_policy_closure_manifest=written")
    print(f"performance_rows={result['performance_matrix']['completed_row_count']}/{result['performance_matrix']['row_count']}")
    print("external_superiority_claim_allowed=False")
    print("b2_b4_can_close_now=False/False")


if __name__ == "__main__":
    main()
