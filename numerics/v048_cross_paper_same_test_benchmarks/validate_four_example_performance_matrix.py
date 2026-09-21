#!/usr/bin/env python3
"""Read-only validator for the v048 four-example performance matrix."""

from __future__ import annotations

import csv
import json
import math
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
EXAMPLES = {"single_pendulum", "double_pendulum", "four_link", "slider_crank"}
PUBLIC_H = (0.01, 0.001, 0.0001)


class Checks:
    def __init__(self) -> None:
        self.errors: list[str] = []

    def check(self, condition: bool, message: str) -> None:
        if not condition:
            self.errors.append(message)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def read_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def parse_float(value: str) -> float:
    try:
        return float(value)
    except ValueError:
        return float("nan")


def parse_h_values(value: str) -> list[float]:
    return [parse_float(part) for part in value.split("|") if part]


def has_public_h_trio(row: dict[str, str]) -> bool:
    values = parse_h_values(row.get("h_values", ""))
    return all(
        any(math.isclose(value, required, rel_tol=1.0e-12, abs_tol=1.0e-15) for value in values)
        for required in PUBLIC_H
    )


def main() -> int:
    checks = Checks()
    try:
        rows = read_csv(RESULTS / "four_example_performance_matrix.csv")
        summary = read_json(RESULTS / "four_example_performance_summary.json")
        markdown = (RESULTS / "four_example_performance_matrix.md").read_text(encoding="utf-8")
    except Exception as exc:  # noqa: BLE001 - concise CLI failure.
        print(f"four-example performance matrix validation: FAIL\n- {exc}")
        return 1

    completed = sum(1 for row in rows if row.get("status", "").startswith("completed"))
    partial = sum(1 for row in rows if row.get("status", "").startswith("partial"))

    checks.check(summary.get("schema") == "four-example-method-performance-matrix-v1", "summary schema changed")
    checks.check(set(summary.get("examples", [])) == EXAMPLES, "summary example set changed")
    checks.check(len(rows) == summary.get("row_count"), "summary row count does not match CSV")
    checks.check(completed == summary.get("completed_row_count"), "completed count does not match CSV")
    checks.check(partial == summary.get("partial_row_count"), "partial count does not match CSV")
    checks.check(summary.get("external_superiority_claim") is False, "matrix must not claim external superiority")
    checks.check(summary.get("same_test_campaign_status") == "not_run", "same-test campaign must remain not_run")
    checks.check(len(rows) >= 48, "matrix row count is unexpectedly small")
    checks.check(completed >= 32, "completed row count should include the double coarse Gauss6 public-horizon pilot")
    checks.check({row.get("example") for row in rows} >= EXAMPLES, "matrix is missing one of the four examples")

    public_timing = [
        row
        for row in rows
        if row.get("method") in {"rA", "rp", "reps"}
        and row.get("example") == "double_pendulum"
    ]
    checks.check(len(public_timing) == 3, "2021 public double-pendulum timing rows missing from matrix")
    for row in public_timing:
        method = row.get("method")
        checks.check(
            row.get("status") == "completed_public_dynamic_self_reference_order_policy",
            f"{method} double-pendulum status should be completed_public_dynamic_self_reference_order_policy",
        )
        checks.check(row.get("row_count") == "3", f"{method} double-pendulum row_count should be 3")
        checks.check(row.get("ok_count") == "3", f"{method} double-pendulum ok_count should be 3")
        checks.check(
            any(math.isclose(value, 0.001, rel_tol=1.0e-12, abs_tol=1.0e-15) for value in parse_h_values(row.get("h_values", ""))),
            f"{method} double-pendulum order row should record h=1e-3",
        )
        checks.check(not math.isnan(parse_float(row.get("pos_order", "nan"))), f"{method} double-pendulum should record pos order")
        checks.check(not math.isnan(parse_float(row.get("vel_order", "nan"))), f"{method} double-pendulum should record vel order")
        checks.check(
            "dynamic self-reference order" in row.get("caveat", ""),
            f"{method} double-pendulum caveat must say dynamic self-reference",
        )

    public_closed = [
        row
        for row in rows
        if row.get("method") == "Gauss6/FullVA-public-horizon"
        and row.get("example") in {"four_link", "slider_crank"}
    ]
    checks.check(len(public_closed) == 2, "public-horizon closed-loop matrix rows missing")
    for row in public_closed:
        example = row.get("example")
        checks.check(
            row.get("status") == "completed_public_horizon_residual_trio",
            f"{example} public-horizon closed-loop status is stale",
        )
        checks.check(row.get("row_count") == "3", f"{example} row_count should be 3")
        checks.check(row.get("ok_count") == "3", f"{example} ok_count should be 3")
        checks.check(has_public_h_trio(row), f"{example} h_values should include the public h trio")
        checks.check("only h=1e-2" not in row.get("caveat", ""), f"{example} caveat still says only h=1e-2")
        checks.check(
            "not public dynamic order/work" in row.get("caveat", ""),
            f"{example} caveat must preserve the no-superiority interpretation",
        )

    public_double_coarse = [
        row
        for row in rows
        if row.get("method") == "Gauss6/FullVA-public-horizon"
        and row.get("example") == "double_pendulum"
    ]
    checks.check(len(public_double_coarse) == 1, "public-horizon double coarse matrix row missing")
    if public_double_coarse:
        row = public_double_coarse[0]
        checks.check(
            row.get("status") == "completed_public_horizon_coarse_double_pilot",
            "double public-horizon row should be the coarse pilot status",
        )
        checks.check(row.get("row_count") == "3", "double public-horizon coarse row_count should be 3")
        checks.check(row.get("ok_count") == "3", "double public-horizon coarse ok_count should be 3")
        checks.check(
            all(
                any(math.isclose(value, required, rel_tol=1.0e-12, abs_tol=1.0e-15) for value in parse_h_values(row.get("h_values", "")))
                for required in (0.1, 0.05, 0.025)
            ),
            "double public-horizon coarse h_values should include 0.1, 0.05, and 0.025",
        )
        checks.check(not math.isnan(parse_float(row.get("pos_order", "nan"))), "double coarse row should record pos order")
        checks.check(not math.isnan(parse_float(row.get("vel_order", "nan"))), "double coarse row should record vel order")
        checks.check(
            "not the public h=1e-2|1e-3|1e-4 policy" in row.get("caveat", ""),
            "double coarse caveat must preserve public-policy boundary",
        )

    hi2022_rows = [
        row
        for row in rows
        if row.get("family") == "Fang/Kissel/Zhang/Negrut 2022"
        and row.get("method") in {"rA-hi2022", "rA_half-hi2022"}
    ]
    checks.check(len(hi2022_rows) == 8, "2022 half-implicit four-example bounded-pilot rows missing")
    for method in {"rA-hi2022", "rA_half-hi2022"}:
        method_rows = [row for row in hi2022_rows if row.get("method") == method]
        checks.check({row.get("example") for row in method_rows} == EXAMPLES, f"{method} should cover all four examples")
        for row in method_rows:
            example = row.get("example")
            checks.check(row.get("status") == "completed_bounded_pilot", f"{method} {example} should be completed bounded pilot")
            checks.check(row.get("row_count") == "3", f"{method} {example} row_count should be 3")
            checks.check(row.get("ok_count") == "3", f"{method} {example} ok_count should be 3")
            checks.check(not math.isnan(parse_float(row.get("vel_order", "nan"))), f"{method} {example} should record velocity order")
            checks.check("bounded T=0.1 pilot" in row.get("caveat", ""), f"{method} {example} caveat must preserve bounded-pilot status")

    checks.check("coverage ledger, not a completed external superiority claim" in markdown, "markdown missing status warning")
    checks.check("completed_public_horizon_residual_trio" in markdown, "markdown missing completed residual trio status")
    checks.check(
        "completed_public_horizon_coarse_double_pilot" in markdown,
        "markdown missing double coarse public-horizon status",
    )
    checks.check(
        "completed_public_dynamic_self_reference_order_policy" in markdown,
        "markdown missing public dynamic self-reference order status",
    )

    if checks.errors:
        print("four-example performance matrix validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("four-example performance matrix validation: PASS")
    print(f"rows={summary.get('row_count')}")
    print(f"completed={summary.get('completed_row_count')}")
    print(f"partial={summary.get('partial_row_count')}")
    print("external_superiority_claim=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
