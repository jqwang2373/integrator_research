#!/usr/bin/env python3
"""Validate the paper-facing numerical order/error matrix against source audits."""

from __future__ import annotations

import csv
import json
import math
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
ROOT = PAPER.parent
V048 = ROOT.parent / "numerics" / "v048_cross_paper_same_test_benchmarks" / "results"

MATRIX_JSON = PAPER / "PAPER_NUMERICAL_RESULT_MATRIX.json"
MATRIX_CSV = PAPER / "PAPER_NUMERICAL_RESULT_MATRIX.csv"
MATRIX_MD = PAPER / "PAPER_NUMERICAL_RESULT_MATRIX.md"
COMMON_JSON = V048 / "common_reference_error_summary.json"
COMMON_CSV = V048 / "common_reference_error_summary.csv"
FORENSIC_JSON = V048 / "all_examples_apples_to_apples_forensic_audit.json"
FORENSIC_CSV = V048 / "all_examples_apples_to_apples_forensic_audit.csv"

EXPECTED_EXAMPLES = ["single_pendulum", "double_pendulum", "four_link", "slider_crank"]
EXPECTED_METHODS = [
    "local_Gauss6_FullVA",
    "hi2022_rA",
    "hi2022_rA_half",
    "ra2021_rA",
    "ra2021_reps",
    "ra2021_rp",
    "tfe2026_Newmark_beta",
    "tfe2026_TFE_m1",
    "tfe2026_TFE_m2",
    "tfe2026_trapezoidal",
    "vp2024_coordinate_partitioning_rA",
]


class Checks:
    def __init__(self) -> None:
        self.errors: list[str] = []

    def check(self, condition: bool, message: str) -> None:
        if not condition:
            self.errors.append(message)


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


def as_float(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() == "true"


def floats_match(left: Any, right: Any, tol: float = 1.0e-12) -> bool:
    left_number = as_float(left)
    right_number = as_float(right)
    if left_number is None and right_number is None:
        return True
    if left_number is None or right_number is None:
        return False
    scale = max(1.0, abs(left_number), abs(right_number))
    return abs(left_number - right_number) <= tol * scale


def key(row: dict[str, Any]) -> tuple[str, str]:
    return str(row["method"]), str(row["example"])


def main() -> int:
    checks = Checks()
    try:
        matrix = read_json(MATRIX_JSON)
        matrix_csv = read_csv(MATRIX_CSV)
        matrix_md = read_text(MATRIX_MD)
        common = read_json(COMMON_JSON)
        common_rows = read_csv(COMMON_CSV)
        forensic = read_json(FORENSIC_JSON)
        forensic_rows = read_csv(FORENSIC_CSV)
    except Exception as exc:  # noqa: BLE001 - compact CLI failure.
        print(f"paper numerical result matrix validation: FAIL\n- {exc}")
        return 1

    rows = matrix.get("rows", [])
    if not isinstance(rows, list):
        rows = []
    checks.check(matrix.get("schema") == "paper-numerical-result-matrix-v1", "matrix schema changed")
    checks.check(
        matrix.get("status") == "paper_ready_table_source_policy_boundary_open",
        "matrix status changed",
    )
    checks.check(matrix.get("examples") == EXPECTED_EXAMPLES, "matrix example order changed")
    checks.check(matrix.get("methods") == EXPECTED_METHODS, "matrix method order changed")
    checks.check(matrix.get("method_count") == 11, "matrix method count changed")
    checks.check(matrix.get("row_count") == 44, "matrix row count changed")
    checks.check(matrix.get("expected_row_count") == 44, "matrix expected row count changed")
    checks.check(matrix.get("raw_row_count") == 132, "matrix raw row count changed")
    checks.check(matrix.get("step_sizes") == [0.1, 0.05, 0.025], "matrix step sizes changed")
    checks.check(floats_match(matrix.get("reference_h"), 0.0125), "matrix reference h changed")
    checks.check(matrix.get("source_policy_reproduction") is False, "matrix overclaims source-policy reproduction")
    checks.check(
        matrix.get("source_policy_external_superiority_allowed") is False,
        "matrix overclaims source-policy external superiority",
    )
    checks.check(
        matrix.get("paper_direct_error_superiority_allowed") is False,
        "matrix overclaims paper-level direct error superiority",
    )
    checks.check(matrix.get("strict_external_error_claim_allowed_rows") == 0, "strict external rows changed")
    checks.check(matrix.get("direct_nonlocal_velocity_order_wins") == 40, "direct order wins changed")
    checks.check(matrix.get("direct_nonlocal_velocity_order_comparisons") == 40, "direct order comparisons changed")
    checks.check(matrix.get("direct_nonlocal_velocity_error_wins") == 40, "direct error wins changed")
    checks.check(matrix.get("direct_nonlocal_velocity_error_comparisons") == 40, "direct error comparisons changed")
    checks.check(len(matrix_csv) == 44, "matrix CSV row count changed")
    checks.check("Method/example cells: `44/44`" in matrix_md, "matrix markdown missing 44/44 marker")
    checks.check(
        "Source-policy external superiority allowed: `False`" in matrix_md,
        "matrix markdown missing source-policy boundary",
    )

    matrix_by_key = {key(row): row for row in rows if isinstance(row, dict)}
    common_by_key = {key(row): row for row in common_rows}
    forensic_by_key = {key(row): row for row in forensic_rows}
    expected_keys = {(method, example) for example in EXPECTED_EXAMPLES for method in EXPECTED_METHODS}
    checks.check(set(matrix_by_key) == expected_keys, "matrix keys do not cover all method/example cells")
    checks.check(set(common_by_key) >= expected_keys, "source common-reference keys missing expected cells")
    checks.check(set(forensic_by_key) >= expected_keys, "source forensic keys missing expected cells")

    for cell_key in sorted(expected_keys):
        row = matrix_by_key.get(cell_key, {})
        common_row = common_by_key.get(cell_key, {})
        forensic_row = forensic_by_key.get(cell_key, {})
        checks.check(row.get("family") == common_row.get("family"), f"{cell_key} family mismatch")
        checks.check(row.get("status") == common_row.get("status"), f"{cell_key} status mismatch")
        checks.check(row.get("source_level") == forensic_row.get("source_level"), f"{cell_key} source level mismatch")
        checks.check(row.get("paper_claim_scope") == forensic_row.get("paper_claim_scope"), f"{cell_key} claim scope mismatch")
        checks.check(row.get("h_values") == common_row.get("h_values"), f"{cell_key} h grid mismatch")
        checks.check(row.get("reference_policy") == common_row.get("reference_policy"), f"{cell_key} reference policy mismatch")
        checks.check(row.get("error_norm") == common_row.get("error_norm"), f"{cell_key} error norm mismatch")
        checks.check(floats_match(row.get("position_order"), common_row.get("pos_order")), f"{cell_key} position order mismatch")
        checks.check(floats_match(row.get("velocity_order"), common_row.get("vel_order")), f"{cell_key} velocity order mismatch")
        checks.check(floats_match(row.get("acceleration_order"), common_row.get("acc_order")), f"{cell_key} acceleration order mismatch")
        checks.check(
            floats_match(row.get("finest_position_error"), common_row.get("finest_pos_error")),
            f"{cell_key} position error mismatch",
        )
        checks.check(
            floats_match(row.get("finest_velocity_error"), common_row.get("finest_vel_error")),
            f"{cell_key} velocity error mismatch",
        )
        checks.check(
            floats_match(row.get("finest_acceleration_error"), common_row.get("finest_acc_error")),
            f"{cell_key} acceleration error mismatch",
        )
        checks.check(
            row.get("source_policy_closed") == as_bool(forensic_row.get("source_policy_closed")),
            f"{cell_key} source-policy flag mismatch",
        )
        checks.check(
            row.get("strict_external_error_claim_allowed")
            == as_bool(forensic_row.get("strict_external_error_claim_allowed")),
            f"{cell_key} strict external flag mismatch",
        )
        issues = row.get("issues", [])
        if str(cell_key[0]).startswith("tfe2026_"):
            checks.check(
                "original_tfe_setup_not_encoded" not in issues,
                f"{cell_key} keeps stale TFE setup issue",
            )
            checks.check(
                "original_tfe_runner_and_friction_source_policy_open" in issues,
                f"{cell_key} missing updated TFE runner/friction issue",
            )

    per_example = matrix.get("per_example", {})
    for example in EXPECTED_EXAMPLES:
        example_summary = per_example.get(example, {})
        checks.check(example_summary.get("method_rows") == 11, f"{example} method row count changed")
        checks.check(
            example_summary.get("source_policy_open_nonlocal_rows") == 10,
            f"{example} source-policy open nonlocal count changed",
        )
        checks.check(
            example_summary.get("strict_external_error_claim_allowed_rows") == 0,
            f"{example} strict external row count changed",
        )

    checks.check(common.get("summary_row_count") == 44, "source common summary row count changed")
    checks.check(common.get("raw_row_count") == 132, "source common raw row count changed")
    checks.check(forensic.get("row_count") == 44, "source forensic row count changed")
    checks.check(forensic.get("raw_row_count") == 132, "source forensic raw row count changed")
    checks.check(
        forensic.get("direct_error_superiority_claim_allowed_for_paper") is False,
        "source forensic direct-error boundary changed",
    )

    if checks.errors:
        print("paper numerical result matrix validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1
    print("paper numerical result matrix validation: PASS")
    print("rows=44/44")
    print("examples=single_pendulum,double_pendulum,four_link,slider_crank")
    print("methods=11")
    print("source_policy_external_superiority_allowed=False")
    print("paper_direct_error_superiority_allowed=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
