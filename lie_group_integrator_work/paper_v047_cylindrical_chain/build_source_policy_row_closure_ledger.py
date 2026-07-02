#!/usr/bin/env python3
"""Build a row-level closure ledger for flagged source-policy rows."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
OUT_JSON = PAPER / "SOURCE_POLICY_ROW_CLOSURE_LEDGER.json"
OUT_MD = PAPER / "SOURCE_POLICY_ROW_CLOSURE_LEDGER.md"

EXPECTED_EXAMPLES = ["single_pendulum", "double_pendulum", "four_link", "slider_crank"]

BATCH_BY_SUITE = {
    "ra2021_absolute_coordinate": "ra2021_coarse_same_window_order_time",
    "hi2022_half_implicit": "hi2022_halfimplicit_full_policy_decision",
    "tfe2026_original_pendulum": "tfe2026_original_pendulum_encoding",
    "vp2024_velocity_partitioning": "vp2024_velocity_partitioning_code_resolution",
}

REQUIRED_EVIDENCE_BY_ACTION = {
    "fix_or_rerun_public_velocity_mapping_time_grid_norm_runtime": [
        "local Gauss6 FullVA row under the same RA2021 source time-grid and dynamic policy",
        "error norm and output policy bound to source-policy order rows",
        "runtime/Newton-iteration policy tied to accepted source-policy order rows",
        "rerun or independent verification artifact",
    ],
    "resolve_tfe_runner_friction_endpoint_then_rerun_or_demote": [
        "source-policy DAE runner equivalence for the absolute-coordinate pendulum",
        "Brown--McPhee source-code-equivalent friction law",
        "full T=10 endpoint/output policy for endpoint-incompatible h rows",
        "TFE/Newmark/trapezoidal and Gauss6/FullVA source-policy method runners",
        "accepted work-precision row table or explicit demotion",
    ],
    "choose_full_T8_public_policy_or_demote": [
        "full T=8 public-policy step-size/reference decision",
        "public half-implicit code path identity",
        "velocity mapping and error norm check",
        "runtime/iteration and energy-or-constraint metric policy",
        "full-policy rerun artifact or explicit demotion",
    ],
    "demote_until_velocity_partitioning_code_path_resolved": [
        "public velocity-partitioning code path",
        "method identity separate from coordinate-partitioning proxy",
        "source step-size/reference policy",
        "order/runtime output policy",
        "resolved rerun artifact or explicit suite demotion",
    ],
}

RA2021_RESOLVED_EVIDENCE = [
    "source public code path and setup identity verified by RA2021_SOURCE_IDENTITY_AUDIT.json",
    "body.r/body.dr/body.ddr output mapping verified from source",
    "public endpoint time-grid convention extracted from source",
]

RA2021_REPLACEMENT_RISKS = [
    "local_Gauss6_FullVA_source_policy_promotion_open",
    "error_norm_runtime_Newton_policy_binding_open",
    "rerun_or_independent_verification_artifact_missing",
]

RA2021_RESOLVED_RISKS = {
    "state_velocity_output_mapping_requires_recheck",
}

TFE_RESOLVED_EVIDENCE = [
    "source pendulum body/setup parameters encoded by TFE_SOURCE_POLICY_SPEC.json and TFE_SOURCE_PENDULUM_MODEL_AUDIT.json",
    "source coordinate/velocity output and error norm policy encoded",
    "full T=10 h_ref=1e-4 source-reference feasibility probe completed without promoting rows",
]

TFE_REMAINING_EVIDENCE = [
    "source-code-equivalent Brown--McPhee friction law, including transition velocity and coupling policy",
    "monolithic absolute-coordinate source-policy DAE runner for frictionless and frictional cases",
    "TFE/Newmark/trapezoidal and Gauss6/FullVA method runners under the same source reference/output policy",
    "full T=10 endpoint/output policy for endpoint-incompatible published h rows",
    "accepted work-precision row table binding error/order, runtime, and work metrics",
]

TFE_STALE_RISKS = {
    "source_pendulum_setup_not_encoded",
    "source_error_norm_and_output_policy_not_encoded",
}

TFE_REPLACEMENT_RISKS = [
    "source_policy_DAE_runner_equivalence_open",
    "brown_mcphee_source_code_equivalent_law_open",
    "full_T10_endpoint_policy_open",
    "accepted_source_policy_work_rows_not_bound",
]


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def batch_lookup(queue: dict[str, Any]) -> dict[str, dict[str, Any]]:
    batches = queue.get("batch_queue", [])
    if not isinstance(batches, list):
        return {}
    return {str(item.get("batch_id")): item for item in batches if isinstance(item, dict)}


def case_group_status(cases: dict[str, Any]) -> dict[str, dict[str, Any]]:
    output: dict[str, dict[str, Any]] = {}
    for item in cases.get("cases", []):
        if not isinstance(item, dict):
            continue
        group = str(item.get("group_id"))
        entry = output.setdefault(
            group,
            {
                "case_count": 0,
                "not_run_count": 0,
                "case_ids": [],
                "blockers": [],
            },
        )
        entry["case_count"] += 1
        entry["case_ids"].append(item.get("case_id"))
        if item.get("current_status") != "complete":
            entry["not_run_count"] += 1
        blocker = item.get("blocker")
        if blocker:
            entry["blockers"].append(blocker)
    return output


def main() -> None:
    triage = read_json(PAPER / "SOURCE_POLICY_CLOSURE_TRIAGE.json")
    all_source = read_json(PAPER / "ALL_EXAMPLES_SOURCE_POLICY_AUDIT.json")
    diagnosis = read_json(PAPER / "EXTERNAL_BASELINE_SOURCE_POLICY_DIAGNOSIS.json")
    queue = read_json(PAPER / "EXTERNAL_SAME_TEST_RUN_QUEUE.json")
    cases = read_json(PAPER / "CROSS_PAPER_BENCHMARK_CASES.json")
    tfe_spec = read_json(PAPER / "TFE_SOURCE_POLICY_SPEC.json")
    tfe_model = read_json(PAPER / "TFE_SOURCE_PENDULUM_MODEL_AUDIT.json")
    ra2021_identity = read_json(PAPER / "RA2021_SOURCE_IDENTITY_AUDIT.json")
    source_policy_self_reproduction = read_json(PAPER / "SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_AUDIT.json")
    tfe_public_code_recheck = read_json(PAPER / "TFE_PUBLIC_CODE_RECHECK_20260613.json")
    vp2024_public_code_recheck = read_json(PAPER / "VP2024_PUBLIC_CODE_RECHECK_20260613.json")

    batch_by_id = batch_lookup(queue)
    case_status = case_group_status(cases)
    audit_by_key = {
        (row.get("method"), row.get("example")): row
        for row in all_source.get("row_audits", [])
        if isinstance(row, dict)
    }
    diagnosis_by_key = {
        (row.get("method"), row.get("example")): row
        for row in diagnosis.get("diagnosis_rows", [])
        if isinstance(row, dict)
    }

    rows: list[dict[str, Any]] = []
    suite_counts: Counter[str] = Counter()
    action_counts: Counter[str] = Counter()
    example_counts: Counter[str] = Counter()

    for item in triage.get("triage_rows", []):
        if not isinstance(item, dict):
            continue
        suite = str(item.get("suite"))
        method = str(item.get("method"))
        example = str(item.get("example"))
        action = str(item.get("action_class"))
        batch_id = BATCH_BY_SUITE.get(suite)
        batch = batch_by_id.get(str(batch_id), {})
        audit = audit_by_key.get((method, example), {})
        diag = diagnosis_by_key.get((method, example), {})
        required = list(REQUIRED_EVIDENCE_BY_ACTION.get(action, ["manual closure evidence"]))
        resolved_evidence: list[str] = []
        source_policy_risks = [str(risk) for risk in item.get("source_policy_risks", [])]
        if suite == "ra2021_absolute_coordinate":
            resolved_evidence = RA2021_RESOLVED_EVIDENCE
            source_policy_risks = [
                risk for risk in source_policy_risks if risk not in RA2021_RESOLVED_RISKS
            ]
            for risk in RA2021_REPLACEMENT_RISKS:
                if risk not in source_policy_risks:
                    source_policy_risks.append(risk)
        if suite == "tfe2026_original_pendulum":
            if (
                tfe_spec.get("runner_gap", {}).get("source_policy_spec_extracted") is True
                and tfe_model.get("source_pendulum_parameter_model_implemented") is True
                and tfe_model.get("source_error_norm_and_output_policy_encoded") is True
                and tfe_model.get("source_reference_solution_policy_full_T10_probe_completed") is True
                and tfe_model.get("source_reference_solution_policy_full_T10_probe_rows_completed") == 0
            ):
                resolved_evidence = TFE_RESOLVED_EVIDENCE
                required = TFE_REMAINING_EVIDENCE
            source_policy_risks = [
                risk for risk in source_policy_risks if risk not in TFE_STALE_RISKS
            ]
            for risk in TFE_REPLACEMENT_RISKS:
                if risk not in source_policy_risks:
                    source_policy_risks.append(risk)
        post_public_code_disposition = None
        public_code_recheck_status = None
        display_action = action
        current_allowed_use = "diagnostic_common_reference_only"
        if suite == "tfe2026_original_pendulum":
            post_public_code_disposition = "attempted_not_reproducible_not_promoted"
            public_code_recheck_status = tfe_public_code_recheck.get("status")
            display_action = post_public_code_disposition
            current_allowed_use = "attempted_not_reproducible_not_promoted_diagnostic_only"
        if suite == "vp2024_velocity_partitioning":
            post_public_code_disposition = "attempted_not_reproducible_not_promoted"
            public_code_recheck_status = vp2024_public_code_recheck.get("status")
            display_action = post_public_code_disposition
            current_allowed_use = "attempted_not_reproducible_not_promoted_diagnostic_only"
            for risk in [
                "distinct_public_vp2024_code_path_not_found",
                "coordinate_partitioning_proxy_not_source_policy_reproduction",
            ]:
                if risk not in source_policy_risks:
                    source_policy_risks.append(risk)
        rows.append(
            {
                "suite": suite,
                "method": method,
                "example": example,
                "action_class": action,
                "display_action": display_action,
                "priority": item.get("priority"),
                "post_public_code_disposition": post_public_code_disposition,
                "public_code_recheck_status": public_code_recheck_status,
                "source_policy_closed": False,
                "can_support_external_superiority": False,
                "current_allowed_use": current_allowed_use,
                "required_closure_action": item.get("required_closure_action"),
                "required_evidence": required,
                "missing_evidence": required,
                "missing_evidence_count": len(required),
                "resolved_evidence": resolved_evidence,
                "resolved_evidence_count": len(resolved_evidence),
                "current_evidence": {
                    "three_coarse_step_sizes_present": audit.get("all_three_step_sizes_present"),
                    "common_reference_arithmetic_verified": audit.get(
                        "common_reference_comparison_arithmetic_verified"
                    ),
                    "candidate_compared_on_shared_reference_norm": audit.get(
                        "candidate_compared_on_shared_reference_norm"
                    ),
                    "source_policy_risks": source_policy_risks,
                    "diagnostic_categories": item.get("diagnostic_categories", []),
                    "claim_disposition": item.get("claim_disposition"),
                    "velocity_order": item.get("velocity_order"),
                    "finest_velocity_error": item.get("finest_velocity_error"),
                    "finest_position_error": item.get("finest_position_error"),
                    "diagnosis_row_present": bool(diag),
                },
                "queue": {
                    "batch_id": batch_id,
                    "queue_status": batch.get("queue_status"),
                    "can_parallelize": batch.get("can_parallelize"),
                    "parallel_shard_count": batch.get("parallel_shard_count"),
                    "next_action": batch.get("next_action"),
                    "source_policy_1e_4_required": batch.get("source_policy_1e-4_required"),
                },
                "source_case_status": case_status.get(suite, {}),
            }
        )
        suite_counts[suite] += 1
        action_counts[action] += 1
        example_counts[example] += 1

    tfe_policy = tfe_spec.get("source_policy", {})
    result = {
        "schema": "source-policy-row-closure-ledger-v1",
        "status": "row_level_source_policy_closure_open",
        "submission_ready": False,
        "external_superiority_claim": False,
        "source_policy_superiority_claim_allowed": False,
        "common_reference_claim_allowed": triage.get("common_reference_claim_allowed"),
        "comparison_matrix_closed": triage.get("comparison_matrix_closed"),
        "coverage": {
            "flagged_row_count": len(rows),
            "flagged_examples": sorted(example_counts),
            "flagged_by_example": dict(sorted(example_counts.items())),
            "flagged_by_suite": dict(sorted(suite_counts.items())),
            "action_counts": dict(sorted(action_counts.items())),
            "all_four_examples_covered": set(example_counts) == set(EXPECTED_EXAMPLES),
            "rows_source_policy_closed": sum(1 for row in rows if row["source_policy_closed"]),
            "rows_external_superiority_ready": sum(1 for row in rows if row["can_support_external_superiority"]),
        },
        "execution_policy": {
            "read_only_existing_artifacts": True,
            "default_1e_4_required": False,
            "heavy_numerical_run_invoked": False,
            "run_v047_invoked": False,
            "v048_runner_invoked": False,
            "parallel_ready_shards_without_default_1e_4": queue.get("coverage_counts", {}).get(
                "parallel_shard_count_without_default_1e-4"
            ),
        },
        "suite_closure_status": {
            "ra2021_absolute_coordinate": {
                "status": "open_verify_or_rerun_public_rows",
                "flagged_rows": suite_counts.get("ra2021_absolute_coordinate", 0),
                "queue_batch": BATCH_BY_SUITE["ra2021_absolute_coordinate"],
                "parallel_ready": True,
                "source_identity_status": ra2021_identity.get("status"),
                "source_identity_resolved_evidence_per_row": len(RA2021_RESOLVED_EVIDENCE),
                "source_policy_promotion_evidence_remaining_per_row": len(
                    REQUIRED_EVIDENCE_BY_ACTION["fix_or_rerun_public_velocity_mapping_time_grid_norm_runtime"]
                ),
                "output_mapping_verified_from_source": ra2021_identity.get("claim_boundary", {}).get(
                    "output_mapping_verified_from_source"
                ),
                "time_grid_policy_extracted_from_source": ra2021_identity.get("claim_boundary", {}).get(
                    "time_grid_policy_extracted_from_source"
                ),
            },
            "tfe2026_original_pendulum": {
                "status": "attempted_not_reproducible_not_promoted_source_policy_rows_not_closed",
                "flagged_rows": suite_counts.get("tfe2026_original_pendulum", 0),
                "source_policy_status": tfe_spec.get("status"),
                "runner_gap": tfe_spec.get("runner_gap", {}),
                "source_reference_h": tfe_policy.get("solver_policy", {}).get("source_reference_h_for_exact_reproduction"),
                "public_code_recheck_status": tfe_public_code_recheck.get("status"),
                "self_reproduction_attempt_status": source_policy_self_reproduction.get("status"),
                "attempted_not_reproducible_rows": tfe_public_code_recheck.get("coverage", {}).get(
                    "source_policy_rows_attempted_not_reproducible"
                ),
            },
            "hi2022_half_implicit": {
                "status": "open_choose_full_T8_policy_or_demote",
                "flagged_rows": suite_counts.get("hi2022_half_implicit", 0),
                "queue_batch": BATCH_BY_SUITE["hi2022_half_implicit"],
                "parallel_ready_after_policy_selection": True,
            },
            "vp2024_velocity_partitioning": {
                "status": "attempted_not_reproducible_not_promoted_no_distinct_public_code_path",
                "flagged_rows": suite_counts.get("vp2024_velocity_partitioning", 0),
                "queue_batch": BATCH_BY_SUITE["vp2024_velocity_partitioning"],
                "code_path_resolved": False,
                "public_code_recheck_status": vp2024_public_code_recheck.get("status"),
                "self_reproduction_attempt_status": source_policy_self_reproduction.get("status"),
                "attempted_not_reproducible_rows": vp2024_public_code_recheck.get("coverage", {}).get(
                    "source_policy_rows_attempted_not_reproducible"
                ),
            },
        },
        "closure_rule": {
            "b2_can_close_now": False,
            "b4_can_close_now": False,
            "all_rows_must_be_closed_or_demoted": True,
            "row_demotions_must_be_stated_in_manuscript": True,
            "reason": (
                "All 15 flagged source-policy rows are row-level open. The fixed-grid "
                "common-reference arithmetic is useful diagnostic evidence, but no row "
                "can support an external-superiority claim until its required evidence "
                "is supplied or its suite is explicitly demoted."
            ),
        },
        "rows": rows,
        "source_files": {
            "triage": "SOURCE_POLICY_CLOSURE_TRIAGE.json",
            "all_examples_source_policy_audit": "ALL_EXAMPLES_SOURCE_POLICY_AUDIT.json",
            "source_policy_diagnosis": "EXTERNAL_BASELINE_SOURCE_POLICY_DIAGNOSIS.json",
            "external_same_test_run_queue": "EXTERNAL_SAME_TEST_RUN_QUEUE.json",
            "cross_paper_cases": "CROSS_PAPER_BENCHMARK_CASES.json",
            "tfe_source_policy_spec": "TFE_SOURCE_POLICY_SPEC.json",
            "ra2021_source_identity_audit": "RA2021_SOURCE_IDENTITY_AUDIT.json",
            "source_policy_self_reproduction_attempt_audit": "SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_AUDIT.json",
            "tfe_public_code_recheck": "TFE_PUBLIC_CODE_RECHECK_20260613.json",
            "vp2024_public_code_recheck": "VP2024_PUBLIC_CODE_RECHECK_20260613.json",
        },
    }

    with OUT_JSON.open("w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, sort_keys=True)
        handle.write("\n")

    lines = [
        "# Source-Policy Row Closure Ledger",
        "",
        "Status: **ROW-LEVEL SOURCE-POLICY CLOSURE OPEN**",
        "",
        f"- Flagged source-policy rows: `{len(rows)}`.",
        f"- Examples covered: `{', '.join(result['coverage']['flagged_examples'])}`.",
        f"- Rows source-policy closed: `{result['coverage']['rows_source_policy_closed']}`.",
        f"- Rows external-superiority ready: `{result['coverage']['rows_external_superiority_ready']}`.",
        f"- B2/B4 can close now: `{result['closure_rule']['b2_can_close_now']}/{result['closure_rule']['b4_can_close_now']}`.",
        "- RA2021 resolved source-identity evidence per active row: `3`; remaining promotion evidence per active row: `4`.",
        f"- Parallel-ready shards without default `1e-4`: `{result['execution_policy']['parallel_ready_shards_without_default_1e_4']}`.",
        f"- Heavy numerical run invoked: `{result['execution_policy']['heavy_numerical_run_invoked']}`.",
        "",
        "## Flagged Rows By Example",
        "",
        "| example | flagged rows |",
        "| --- | ---: |",
    ]
    for example in EXPECTED_EXAMPLES:
        lines.append(f"| `{example}` | {example_counts.get(example, 0)} |")
    lines.extend(
        [
            "",
            "## Suite Status",
            "",
            "| suite | flagged rows | status |",
            "| --- | ---: | --- |",
        ]
    )
    for suite, status in result["suite_closure_status"].items():
        lines.append(f"| `{suite}` | {status['flagged_rows']} | `{status['status']}` |")
    lines.extend(
        [
            "",
            "## Row Ledger",
            "",
            "| suite | example | method | velocity order | finest velocity error | disposition/action | missing evidence count | allowed use |",
            "| --- | --- | --- | ---: | ---: | --- | ---: | --- |",
        ]
    )
    for row in rows:
        velocity_order = row.get("current_evidence", {}).get("velocity_order")
        finest_velocity_error = row.get("current_evidence", {}).get("finest_velocity_error")
        velocity_order_text = "n/a" if velocity_order is None else f"{float(velocity_order):.3g}"
        finest_velocity_error_text = "n/a" if finest_velocity_error is None else f"{float(finest_velocity_error):.3e}"
        lines.append(
            f"| `{row['suite']}` | `{row['example']}` | `{row['method']}` | "
            f"{velocity_order_text} | {finest_velocity_error_text} | "
            f"`{row['display_action']}` | {len(row['missing_evidence'])} | "
            f"`{row['current_allowed_use']}` |"
        )
    lines.extend(
        [
            "",
            "## Closure Rule",
            "",
            "Every flagged row must either receive the row-level source-policy evidence",
            "listed in the JSON ledger or be explicitly demoted from the external",
            "superiority claim. Fixed-grid common-reference arithmetic alone is not a",
            "source-policy closure certificate.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("source_policy_row_closure_ledger=written")
    print(f"flagged_rows={len(rows)}")
    print("rows_source_policy_closed=0")
    print("rows_external_superiority_ready=0")
    print("b2_b4_can_close_now=False/False")


if __name__ == "__main__":
    main()
