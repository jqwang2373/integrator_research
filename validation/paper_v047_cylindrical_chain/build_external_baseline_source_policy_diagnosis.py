#!/usr/bin/env python3
"""Diagnose source-policy risks behind flagged external baseline rows."""

from __future__ import annotations

import csv
import json
import math
from collections import Counter, defaultdict
from pathlib import Path


PAPER = Path(__file__).resolve().parent
ROOT = PAPER.parent
V048 = ROOT.parent / "numerics" / "v048_cross_paper_same_test_benchmarks" / "results"
RAW_CSV = V048 / "common_reference_error_raw_rows.csv"
OUT_JSON = PAPER / "EXTERNAL_BASELINE_SOURCE_POLICY_DIAGNOSIS.json"
OUT_MD = PAPER / "EXTERNAL_BASELINE_SOURCE_POLICY_DIAGNOSIS.md"

POSITION_ALIGNMENT_TOL = 1.0e-6
LARGE_VELOCITY_ERROR = 1.0e-1
VERY_SMALL_VELOCITY_ERROR = 1.0e-6
LOW_ORDER = 0.5
FLOOR_ORDER = 0.1


def read_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


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
    if abs(number) >= 1000.0 or (0.0 < abs(number) < 1.0e-2):
        return f"{number:.3e}"
    return f"{number:.3f}"


def method_family(method: str) -> str:
    if method.startswith("ra2021"):
        return "ra2021_absolute_coordinate"
    if method.startswith("hi2022"):
        return "hi2022_half_implicit"
    if method.startswith("tfe2026"):
        return "tfe2026_original_pendulum"
    if method.startswith("vp2024"):
        return "vp2024_velocity_partitioning"
    return "unknown"


def suite_policy_risks(method: str) -> list[str]:
    family = method_family(method)
    if family == "ra2021_absolute_coordinate":
        return [
            "public_code_setup_retained_but_common_reference_fixed_grid_replay",
            "source_helpers_use_linspace_0_T_int_T_over_h_convention",
            "state_velocity_output_mapping_requires_recheck",
        ]
    if family == "hi2022_half_implicit":
        return [
            "bounded_pilot_not_full_T8_public_policy",
            "public_code_setup_retained_but_common_reference_fixed_grid_replay",
            "state_velocity_output_mapping_requires_recheck",
        ]
    if family == "tfe2026_original_pendulum":
        return [
            "source_policy_DAE_runner_equivalence_open",
            "brown_mcphee_source_code_equivalent_law_open",
            "full_T10_endpoint_policy_open",
            "accepted_source_policy_work_rows_not_bound",
        ]
    if family == "vp2024_velocity_partitioning":
        return [
            "velocity_partitioning_code_path_unresolved",
            "coordinate_partitioning_proxy_only",
            "near_reference_floor_can_make_order_unidentifiable",
        ]
    return ["source_policy_unknown"]


def closure_action(method: str, example: str) -> str:
    family = method_family(method)
    if family == "ra2021_absolute_coordinate":
        return (
            f"rerun_or_verify_ra2021_{example}_under_declared_same_test_policy_with_state_velocity_mapping_time_grid_norm_and_runtime"
        )
    if family == "hi2022_half_implicit":
        return (
            f"choose_full_T8_public_policy_or_explicitly_demote_hi2022_{example}_before_external_superiority"
        )
    if family == "tfe2026_original_pendulum":
        return "encode_original_tfe_pendulum_setup_error_norm_friction_law_output_policy_then_rerun_or_demote"
    if family == "vp2024_velocity_partitioning":
        return "resolve_velocity_partitioning_code_path_or_demote_vp2024_suite"
    return "resolve_source_policy_before_claim"


def row_categories(example: str, method: str, order: float, pos_error: float, vel_error: float) -> list[str]:
    categories: list[str] = []
    if math.isfinite(pos_error) and math.isfinite(vel_error):
        if pos_error <= POSITION_ALIGNMENT_TOL and vel_error > LARGE_VELOCITY_ERROR:
            categories.append("position_aligned_velocity_mismatch")
    if math.isfinite(order) and abs(order) < FLOOR_ORDER and math.isfinite(vel_error) and vel_error <= VERY_SMALL_VELOCITY_ERROR:
        categories.append("near_reference_floor_order_not_identifiable")
    if math.isfinite(order) and order < 0.0 and math.isfinite(vel_error) and vel_error > 1.0:
        categories.append("negative_order_large_error_fixed_grid_or_form_mismatch")
    if math.isfinite(order) and order < LOW_ORDER and math.isfinite(vel_error) and vel_error < 1.0e-3:
        categories.append("low_order_but_small_error_needs_wider_step_window")
    if example == "single_pendulum" and method.startswith(("ra2021", "tfe2026")) and vel_error > 1.0:
        categories.append("single_pendulum_velocity_output_policy_suspect")
    if not categories:
        categories.append("source_policy_recheck_required")
    return categories


def main() -> None:
    sanity = read_json(PAPER / "ALL_EXAMPLES_RESULT_SANITY_AUDIT.json")
    recomputation = read_json(PAPER / "COMMON_REFERENCE_ORDER_RECOMPUTATION_AUDIT.json")
    run_queue = read_json(PAPER / "EXTERNAL_SAME_TEST_RUN_QUEUE.json")
    acceptance = read_json(PAPER / "EXTERNAL_SAME_TEST_ACCEPTANCE_SHEET.json")
    raw_rows = read_csv(RAW_CSV)
    raw_by_key: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in raw_rows:
        raw_by_key[(row["method"], row["example"])].append(row)

    diagnosis_rows: list[dict[str, object]] = []
    for flagged in sanity.get("baseline_sanity", {}).get("flagged_rows", []):
        method = str(flagged["method"])
        example = str(flagged["example"])
        rows = sorted(raw_by_key[(method, example)], key=lambda item: as_float(item["h"]))
        finest = rows[0] if rows else {}
        pos_error = as_float(finest.get("pos_error"))
        vel_error = as_float(finest.get("vel_error"))
        acc_error = as_float(finest.get("acc_error"))
        order = as_float(flagged.get("velocity_order"))
        ratio = vel_error / max(pos_error, 1.0e-300) if math.isfinite(pos_error) and math.isfinite(vel_error) else float("nan")
        categories = row_categories(example, method, order, pos_error, vel_error)
        diagnosis_rows.append(
            {
                "method": method,
                "example": example,
                "suite": method_family(method),
                "velocity_order": order,
                "finest_h": as_float(finest.get("h")),
                "finest_position_error": pos_error,
                "finest_velocity_error": vel_error,
                "finest_acceleration_error": acc_error,
                "velocity_to_position_error_ratio": ratio,
                "sanity_flags": flagged.get("flags", []),
                "diagnostic_categories": categories,
                "source_policy_risks": suite_policy_risks(method),
                "required_closure_action": closure_action(method, example),
                "claim_disposition": "diagnostic_only_not_external_superiority_evidence",
            }
        )

    category_counts = Counter(
        category for row in diagnosis_rows for category in row.get("diagnostic_categories", [])
    )
    suite_counts = Counter(str(row["suite"]) for row in diagnosis_rows)
    example_counts = Counter(str(row["example"]) for row in diagnosis_rows)
    position_aligned_velocity_mismatch_count = sum(
        1 for row in diagnosis_rows if "position_aligned_velocity_mismatch" in row["diagnostic_categories"]
    )

    result = {
        "schema": "external-baseline-source-policy-diagnosis-v1",
        "status": "diagnosis_only_source_policy_recheck_required",
        "submission_ready": False,
        "all_four_examples_covered_by_flagged_rows": set(example_counts) == {
            "single_pendulum",
            "double_pendulum",
            "four_link",
            "slider_crank",
        },
        "source_policy_recheck_required": True,
        "external_superiority_allowed": False,
        "coverage": {
            "flagged_row_count": len(diagnosis_rows),
            "flagged_examples": sorted(example_counts),
            "flagged_by_example": dict(sorted(example_counts.items())),
            "flagged_by_suite": dict(sorted(suite_counts.items())),
            "category_counts": dict(sorted(category_counts.items())),
            "position_aligned_velocity_mismatch_count": position_aligned_velocity_mismatch_count,
        },
        "source_policy_context": {
            "common_reference_arithmetic_mismatches": recomputation.get("verification", {}).get("mismatch_count"),
            "all_examples_sanity_flagged_rows": sanity.get("baseline_sanity", {}).get("flagged_nonlocal_count"),
            "same_test_campaign_status": run_queue.get("same_test_campaign_status"),
            "run_queue_status": run_queue.get("status"),
            "acceptance_sheet_status": acceptance.get("status"),
            "accepted_external_dynamic_order_examples_count": acceptance.get("acceptance_counts", {}).get(
                "accepted_external_dynamic_order_examples_count"
            ),
            "parallel_shard_count_without_default_1e_4": run_queue.get("coverage_counts", {}).get(
                "parallel_shard_count_without_default_1e-4"
            ),
        },
        "diagnosis_rows": diagnosis_rows,
        "claim_boundary": {
            "diagnosis_is_not_method_correctness_judgment": True,
            "diagnosis_is_not_external_superiority_evidence": True,
            "paper_safe_use": (
                "Use this audit to explain why flagged common-reference baseline rows require source-policy "
                "closure before any external-superiority claim."
            ),
            "b2_b4_status": "not_closed",
        },
    }
    with OUT_JSON.open("w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, sort_keys=True)
        handle.write("\n")

    lines = [
        "# External Baseline Source-Policy Diagnosis",
        "",
        "Status: **diagnosis only; source-policy recheck still required**.",
        "",
        f"- Flagged baseline rows diagnosed: `{len(diagnosis_rows)}`.",
        f"- Flagged examples: `{', '.join(sorted(example_counts))}`.",
        f"- Position-aligned but velocity-mismatched rows: `{position_aligned_velocity_mismatch_count}`.",
        f"- Common-reference arithmetic mismatches: `{recomputation.get('verification', {}).get('mismatch_count')}`.",
        f"- Same-test campaign status: `{run_queue.get('same_test_campaign_status')}`.",
        f"- Accepted external dynamic-order examples: `{acceptance.get('acceptance_counts', {}).get('accepted_external_dynamic_order_examples_count')}`.",
        f"- External superiority allowed: `{result['external_superiority_allowed']}`.",
        "",
        "## Diagnostic Category Counts",
        "",
        "| category | rows |",
        "|---|---:|",
    ]
    for category, count in sorted(category_counts.items()):
        lines.append(f"| `{category}` | `{count}` |")
    lines.extend(
        [
            "",
            "## Flagged Row Diagnosis",
            "",
            "| method | example | order | finest pos error | finest vel error | categories | closure action |",
            "|---|---|---:|---:|---:|---|---|",
        ]
    )
    for row in diagnosis_rows:
        lines.append(
            "| "
            f"`{row['method']}` | `{row['example']}` | `{fmt(row['velocity_order'])}` | "
            f"`{fmt(row['finest_position_error'])}` | `{fmt(row['finest_velocity_error'])}` | "
            f"`{', '.join(row['diagnostic_categories'])}` | `{row['required_closure_action']}` |"
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- This audit diagnoses comparison-policy risks; it does not decide that an external method is intrinsically bad.",
            "- The zero-mismatch recomputation audit means the current table arithmetic is consistent with the raw rows.",
            "- B2/B4 remain open until source-policy same-test runs are completed or suites are explicitly demoted in the manuscript.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("external_baseline_source_policy_diagnosis=written")
    print(f"flagged_rows={len(diagnosis_rows)}")
    print(f"position_aligned_velocity_mismatch={position_aligned_velocity_mismatch_count}")
    print("external_superiority_allowed=False")


if __name__ == "__main__":
    main()
