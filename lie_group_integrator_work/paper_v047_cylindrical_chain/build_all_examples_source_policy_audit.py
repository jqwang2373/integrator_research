#!/usr/bin/env python3
"""Build an all-example source-policy audit for flagged external rows."""

from __future__ import annotations

import csv
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
ROOT = PAPER.parent
V048 = ROOT / "v048_cross_paper_same_test_benchmarks"
RESULTS = V048 / "results"
OUT_JSON = PAPER / "ALL_EXAMPLES_SOURCE_POLICY_AUDIT.json"
OUT_MD = PAPER / "ALL_EXAMPLES_SOURCE_POLICY_AUDIT.md"

EXAMPLES = {"single_pendulum", "double_pendulum", "four_link", "slider_crank"}
STEP_SIZES = [0.1, 0.05, 0.025]


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def as_float(value: object) -> float:
    try:
        out = float(value)
    except (TypeError, ValueError):
        return float("nan")
    return out if math.isfinite(out) else float("nan")


def fmt(value: object) -> str:
    number = as_float(value)
    if not math.isfinite(number):
        return "nan"
    if abs(number) >= 1000.0 or (0.0 < abs(number) < 1.0e-3):
        return f"{number:.3e}"
    return f"{number:.6g}"


def source_suite_policy(suite: str, common_ref_src: str, coarse_src: str) -> dict[str, Any]:
    public_fixed_grid_tokens = all(
        token in common_ref_src
        for token in [
            "run_public_fixed_grid_model",
            "np.linspace(0.0, params.t_end, steps + 1, endpoint=True)",
            "body.r",
            "body.dr",
            "body.ddr",
        ]
    )
    installed_step_tokens = all(
        token in coarse_src
        for token in [
            "run_ra2021_rA_model_with_installed_step",
            "install_ra_newmark_family_step",
            "install_ra_tfe_m1_step",
            "install_ra_tfe_multinode_step",
            "install_ra_vp2024_coordinate_partitioning_step",
        ]
    )
    helper_grid_risk = "linspace(0,T,int(T/h))" in common_ref_src

    if suite == "ra2021_absolute_coordinate":
        return {
            "suite": suite,
            "row_source": "public SimEngineMBD setup and public rA/rp/reps stepper",
            "candidate_replay_policy": "fixed_grid_common_reference_replay",
            "time_grid_closed_for_common_reference": public_fixed_grid_tokens,
            "time_grid_source": "np.linspace(0.0, params.t_end, steps + 1, endpoint=True)",
            "position_source": "body.r",
            "velocity_source": "body.dr",
            "acceleration_source": "body.ddr",
            "source_helper_grid_risk": helper_grid_risk,
            "source_policy_closed": False,
            "closure_required": "rerun_or_independently_verify_public_rows_with_declared_velocity_mapping_time_grid_norm_runtime",
        }
    if suite == "hi2022_half_implicit":
        return {
            "suite": suite,
            "row_source": "public HI2022 setup and public half-implicit stepper",
            "candidate_replay_policy": "bounded_fixed_grid_common_reference_replay",
            "time_grid_closed_for_common_reference": public_fixed_grid_tokens,
            "time_grid_source": "np.linspace(0.0, params.t_end, steps + 1, endpoint=True)",
            "position_source": "body.r",
            "velocity_source": "body.dr",
            "acceleration_source": "body.ddr",
            "source_helper_grid_risk": helper_grid_risk,
            "full_T8_public_policy_complete": False,
            "source_policy_closed": False,
            "closure_required": "run_full_T8_public_policy_or_demote_hi2022_rows",
        }
    if suite == "tfe2026_original_pendulum":
        return {
            "suite": suite,
            "row_source": "paper-spec candidate reconstruction; no distinct public TFE code artifact found",
            "candidate_replay_policy": "attempted_paper_spec_reconstruction_diagnostic_only",
            "time_grid_closed_for_common_reference": installed_step_tokens,
            "time_grid_source": "run_ra2021_rA_model_with_installed_step fixed endpoint grid",
            "position_source": "body.r",
            "velocity_source": "body.dr",
            "acceleration_source": "body.ddr",
            "original_pendulum_source_policy_encoded": False,
            "public_code_recheck_status": "public_code_rechecked_no_distinct_tfe_code_artifact_attempted_not_reproducible",
            "self_reproduction_disposition": "attempted_not_reproducible_not_promoted",
            "source_policy_closed": False,
            "closure_required": "attempted_not_reproducible_not_promoted_from_available_public_material; keep_as_formal_order_or_diagnostic_comparator_only_unless_new_source_code_equivalent_artifact_appears",
        }
    if suite == "vp2024_velocity_partitioning":
        return {
            "suite": suite,
            "row_source": "public repository tree rechecked; no distinct VP2024 code path found",
            "candidate_replay_policy": "coordinate_partitioning_proxy_diagnostic_only",
            "time_grid_closed_for_common_reference": installed_step_tokens,
            "time_grid_source": "run_ra2021_rA_model_with_installed_step fixed endpoint grid",
            "position_source": "body.r",
            "velocity_source": "body.dr",
            "acceleration_source": "body.ddr",
            "independent_velocity_partitioning_code_path_resolved": False,
            "public_code_recheck_status": "public_code_rechecked_no_distinct_vp2024_path_attempted_not_reproducible",
            "self_reproduction_disposition": "attempted_not_reproducible_not_promoted",
            "source_policy_closed": False,
            "closure_required": "attempted_not_reproducible_not_promoted_until_distinct_public_vp2024_code_path_or_author_artifact_appears",
        }
    return {
        "suite": suite,
        "row_source": "unknown",
        "candidate_replay_policy": "manual_review",
        "source_policy_closed": False,
        "closure_required": "manual_review",
    }


def main() -> None:
    diagnosis = read_json(PAPER / "EXTERNAL_BASELINE_SOURCE_POLICY_DIAGNOSIS.json")
    triage = read_json(PAPER / "SOURCE_POLICY_CLOSURE_TRIAGE.json")
    recomputation = read_json(PAPER / "COMMON_REFERENCE_ORDER_RECOMPUTATION_AUDIT.json")
    comparison = read_json(PAPER / "COMPARISON_OBJECTIVE_CLOSURE_RECONCILIATION_AUDIT.json")
    raw_rows = read_csv(RESULTS / "common_reference_error_raw_rows.csv")
    common_ref_src = read_text(V048 / "build_common_reference_error_audit.py")
    coarse_src = read_text(V048 / "run_coarse_four_example_order.py")

    raw_by_key: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in raw_rows:
        raw_by_key[(row["method"], row["example"])].append(row)

    diagnosis_rows = diagnosis.get("diagnosis_rows", [])
    if not isinstance(diagnosis_rows, list):
        raise ValueError("diagnosis_rows is not a list")

    row_audits: list[dict[str, Any]] = []
    suite_counts: Counter[str] = Counter()
    example_counts: Counter[str] = Counter()
    category_counts: Counter[str] = Counter()
    risk_counts: Counter[str] = Counter()
    raw_flagged_row_count = 0

    for row in diagnosis_rows:
        if not isinstance(row, dict):
            continue
        suite = str(row.get("suite"))
        method = str(row.get("method"))
        example = str(row.get("example"))
        suite_policy = source_suite_policy(suite, common_ref_src, coarse_src)
        raw_for_cell = sorted(raw_by_key.get((method, example), []), key=lambda item: as_float(item.get("h")), reverse=True)
        raw_flagged_row_count += len(raw_for_cell)
        h_values = [as_float(item.get("h")) for item in raw_for_cell]
        raw_statuses = [item.get("status") for item in raw_for_cell]
        categories = [str(item) for item in row.get("diagnostic_categories", [])]
        risks = [str(item) for item in row.get("source_policy_risks", [])]
        row_audits.append(
            {
                "suite": suite,
                "example": example,
                "method": method,
                "h_values": h_values,
                "all_three_step_sizes_present": sorted(round(item, 12) for item in h_values) == sorted(STEP_SIZES),
                "raw_statuses": raw_statuses,
                "common_reference_comparison_arithmetic_verified": recomputation.get("verification", {}).get("mismatch_count") == 0,
                "candidate_compared_on_shared_reference_norm": True,
                "source_policy_closed": False,
                "claim_disposition": row.get("claim_disposition"),
                "diagnostic_categories": categories,
                "source_policy_risks": risks,
                "velocity_order": row.get("velocity_order"),
                "finest_position_error": row.get("finest_position_error"),
                "finest_velocity_error": row.get("finest_velocity_error"),
                "required_closure_action": row.get("required_closure_action"),
                "suite_policy_summary": suite_policy["closure_required"],
            }
        )
        suite_counts[suite] += 1
        example_counts[example] += 1
        for category in categories:
            category_counts[category] += 1
        for risk in risks:
            risk_counts[risk] += 1

    suite_policy_rows = {
        suite: source_suite_policy(suite, common_ref_src, coarse_src)
        for suite in sorted(suite_counts)
    }
    all_source_policy_open = all(row.get("source_policy_closed") is False for row in row_audits)
    all_three_h = all(row.get("all_three_step_sizes_present") is True for row in row_audits)

    result = {
        "schema": "all-examples-source-policy-audit-v1",
        "status": "all_flagged_examples_checked_source_policy_reproduction_open",
        "submission_ready": False,
        "external_superiority_claim": False,
        "source_policy_superiority_claim_allowed": comparison.get("source_policy_superiority_claim_allowed"),
        "common_reference_claim_allowed": comparison.get("common_reference_claim_allowed"),
        "comparison_matrix_closed": comparison.get("comparison_matrix_closed"),
        "execution_policy": {
            "default_1e_4_required": False,
            "heavy_numerical_run_invoked": False,
            "run_v047_invoked": False,
            "audit_mode": "read_only_static_and_existing_csv",
        },
        "coverage": {
            "flagged_row_count": len(row_audits),
            "flagged_raw_row_count": raw_flagged_row_count,
            "flagged_examples": sorted(example_counts),
            "flagged_by_example": dict(sorted(example_counts.items())),
            "flagged_by_suite": dict(sorted(suite_counts.items())),
            "diagnostic_category_counts": dict(sorted(category_counts.items())),
            "source_policy_risk_counts": dict(sorted(risk_counts.items())),
            "all_four_examples_covered": set(example_counts) == EXAMPLES,
            "all_flagged_rows_have_three_step_sizes": all_three_h,
        },
        "common_reference_mechanics": {
            "step_sizes": STEP_SIZES,
            "t_end": 0.1,
            "reference_h": 0.0125,
            "summary_order_mismatches": recomputation.get("verification", {}).get("mismatch_count"),
            "summary_cells_recomputed": recomputation.get("coverage", {}).get("method_example_cell_count"),
            "raw_ok_rows_recomputed": recomputation.get("coverage", {}).get("raw_ok_row_count"),
            "fixed_grid_public_replay_token_found": source_suite_policy("ra2021_absolute_coordinate", common_ref_src, coarse_src)[
                "time_grid_closed_for_common_reference"
            ],
            "body_velocity_source_token_found": "body.dr" in common_ref_src,
            "body_acceleration_source_token_found": "body.ddr" in common_ref_src,
        },
        "suite_policy_rows": suite_policy_rows,
        "row_audits": row_audits,
        "closure_boundary": {
            "all_source_policy_rows_closed": all_source_policy_open is False,
            "b2_can_close_now": False,
            "b4_can_close_now": False,
            "source_policy_reproduction_open": True,
            "source_policy_audit_is_not_method_correctness_judgment": True,
            "source_policy_audit_is_not_external_superiority_evidence": True,
            "required_next_step": (
                "RA2021/HI2022 remain not promoted until their source-policy rows are promoted "
                "or explicitly kept out of B4/B7. TFE/VP2024 rows have been rechecked, "
                "self-reproduction was attempted where possible, and the rows are marked "
                "attempted_not_reproducible_not_promoted rather than left as undecided rerun items."
            ),
        },
        "triage_crosscheck": {
            "triage_schema": triage.get("schema"),
            "triage_flagged_row_count": triage.get("triage_scope", {}).get("flagged_row_count"),
            "triage_action_counts": triage.get("triage_scope", {}).get("action_counts"),
            "triage_b2_can_close_now": triage.get("closure_boundary", {}).get("b2_can_close_now"),
            "triage_b4_can_close_now": triage.get("closure_boundary", {}).get("b4_can_close_now"),
        },
        "source_files": {
            "diagnosis": "EXTERNAL_BASELINE_SOURCE_POLICY_DIAGNOSIS.json",
            "triage": "SOURCE_POLICY_CLOSURE_TRIAGE.json",
            "recomputation": "COMMON_REFERENCE_ORDER_RECOMPUTATION_AUDIT.json",
            "comparison_reconciliation": "COMPARISON_OBJECTIVE_CLOSURE_RECONCILIATION_AUDIT.json",
            "raw_rows": "../v048_cross_paper_same_test_benchmarks/results/common_reference_error_raw_rows.csv",
            "common_reference_runner": "../v048_cross_paper_same_test_benchmarks/build_common_reference_error_audit.py",
            "coarse_runner": "../v048_cross_paper_same_test_benchmarks/run_coarse_four_example_order.py",
            "source_policy_self_reproduction_attempt_audit": "SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_AUDIT.json",
            "tfe_public_code_recheck": "TFE_PUBLIC_CODE_RECHECK_20260613.json",
            "vp2024_public_code_recheck": "VP2024_PUBLIC_CODE_RECHECK_20260613.json",
        },
    }

    with OUT_JSON.open("w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, sort_keys=True)
        handle.write("\n")

    lines = [
        "# All-Examples Source-Policy Audit",
        "",
        "Status: **ALL FLAGGED EXAMPLES CHECKED - SOURCE-POLICY REPRODUCTION OPEN**",
        "",
        f"- Flagged rows checked: `{len(row_audits)}`.",
        f"- Flagged raw rows checked: `{raw_flagged_row_count}`.",
        f"- Examples covered: `{', '.join(result['coverage']['flagged_examples'])}`.",
        f"- All four examples covered: `{result['coverage']['all_four_examples_covered']}`.",
        f"- Suites covered: `{', '.join(sorted(suite_counts))}`.",
        f"- All rows have `h=[0.1,0.05,0.025]`: `{all_three_h}`.",
        f"- Common-reference arithmetic mismatches: `{result['common_reference_mechanics']['summary_order_mismatches']}`.",
        f"- Source-policy superiority allowed: `{result['source_policy_superiority_claim_allowed']}`.",
        f"- B2/B4 can close now: `{result['closure_boundary']['b2_can_close_now']}/{result['closure_boundary']['b4_can_close_now']}`.",
        f"- Default `1e-4` required: `{result['execution_policy']['default_1e_4_required']}`.",
        f"- Heavy numerical run invoked: `{result['execution_policy']['heavy_numerical_run_invoked']}`.",
        "",
        "## Suite Policy Checks",
        "",
        "| suite | rows | row source | source-policy closed | closure required |",
        "| --- | ---: | --- | --- | --- |",
    ]
    for suite, policy in suite_policy_rows.items():
        lines.append(
            f"| `{suite}` | {suite_counts[suite]} | {policy['row_source']} | "
            f"`{policy['source_policy_closed']}` | {policy['closure_required']} |"
        )
    lines.extend(
        [
            "",
            "## Flagged Rows",
            "",
            "| example | suite | method | order | finest velocity error | categories |",
            "| --- | --- | --- | ---: | ---: | --- |",
        ]
    )
    for row in row_audits:
        lines.append(
            f"| `{row['example']}` | `{row['suite']}` | `{row['method']}` | "
            f"{fmt(row['velocity_order'])} | {fmt(row['finest_velocity_error'])} | "
            f"{', '.join(row['diagnostic_categories'])} |"
        )
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "This audit verifies coverage and source-policy risk classification for every flagged row. "
            "It does not close the source-policy reproduction, does not judge method correctness by itself, "
            "and does not authorize an external-superiority claim.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("all_examples_source_policy_audit=written")
    print(f"flagged_rows={len(row_audits)}")
    print(f"flagged_raw_rows={raw_flagged_row_count}")
    print(f"flagged_examples={','.join(result['coverage']['flagged_examples'])}")
    print("b2_b4_can_close_now=False/False")
    print("heavy_numerical_run_invoked=False")


if __name__ == "__main__":
    main()
