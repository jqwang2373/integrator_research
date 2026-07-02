#!/usr/bin/env python3
"""Validate the isolated HI2022 full-T=8 source-policy candidate shard."""

from __future__ import annotations

import csv
import json
import math
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
STEM = "hi2022_full_t8_source_policy_candidate_rA_double_pendulum"


class Checks:
    def __init__(self) -> None:
        self.errors: list[str] = []

    def check(self, condition: bool, message: str) -> None:
        if not condition:
            self.errors.append(message)


def read_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def pair_orders(rows: list[dict[str, str]], metric: str) -> list[float]:
    pairs = sorted(
        [
            (float(row["h"]), float(row[metric]))
            for row in rows
            if row.get("status") == "ok" and math.isfinite(float(row.get(metric, "nan")))
        ],
        reverse=True,
    )
    return [
        math.log(e0 / e1) / math.log(h0 / h1)
        for (h0, e0), (h1, e1) in zip(pairs, pairs[1:])
        if e0 > 0.0 and e1 > 0.0
    ]


def main() -> int:
    checks = Checks()
    rows_path = RESULTS / f"{STEM}_rows.csv"
    summary_path = RESULTS / f"{STEM}_summary.json"
    md_path = RESULTS / f"{STEM}.md"
    try:
        rows = read_csv(rows_path)
        summary = read_json(summary_path)
        md = md_path.read_text(encoding="utf-8")
    except Exception as exc:  # noqa: BLE001
        print(f"HI2022 full T=8 source-policy candidate validation: FAIL\n- {exc}")
        return 1

    ok_rows = [row for row in rows if row.get("status") == "ok"]
    status = summary.get("status")
    allowed_statuses = {
        "planned_full_T8_source_policy_candidate",
        "partial_or_failed_full_T8_source_policy_candidate_not_promoted",
        "executed_full_T8_selected_coarse_trio_not_promoted",
    }
    checks.check(summary.get("schema") == "hi2022-full-t8-source-policy-candidate-v1", "schema changed")
    checks.check(status in allowed_statuses, "status changed")
    checks.check(summary.get("form") == "rA", "form changed")
    checks.check(summary.get("model") == "double_pendulum", "model changed")
    checks.check(summary.get("selected_t_end") == 8.0, "T=8 selection changed")
    checks.check(summary.get("selected_reference_h") == 0.001, "reference h changed")
    checks.check(summary.get("selected_step_sizes") == [0.02, 0.01, 0.005], "selected h trio changed")
    checks.check(summary.get("estimated_reference_steps") == 8000, "reference step estimate changed")
    checks.check(summary.get("estimated_candidate_steps") == [400, 800, 1600], "candidate step estimates changed")
    checks.check(summary.get("source_policy_time_window_selected") is True, "T=8 source-policy marker missing")
    checks.check(summary.get("source_policy_reference_h_selected") is True, "source reference marker missing")
    checks.check(summary.get("selected_coarse_trio") is True, "coarse trio marker missing")
    checks.check(summary.get("full_public_grid_selected") is False, "candidate unexpectedly selected full grid")
    checks.check(summary.get("full_T8_policy_completed") is False, "candidate overclaims full T8 completion")
    checks.check(summary.get("source_policy_1e_4_included") is False, "candidate unexpectedly includes h=1e-4")
    checks.check(summary.get("row_count") == len(rows) == 3, "row count changed")
    checks.check(summary.get("ok_row_count") == len(ok_rows), "ok-row count stale")
    checks.check(
        summary.get("source_policy_candidate_rows_completed") == len(ok_rows),
        "candidate completion count stale",
    )
    checks.check(summary.get("h_values") == [0.02, 0.01, 0.005], "row h values changed")
    checks.check(summary.get("source_policy_reproduction_rows_promoted") == 0, "rows unexpectedly promoted")
    checks.check(summary.get("source_policy_rows_closed_by_this_evidence") == 0, "source-policy rows overclosed")
    checks.check(summary.get("counts_as_full_public_grid_source_policy") is False, "full-grid marker overclaimed")
    checks.check(summary.get("counts_as_b4_accepted_source_policy_rows") is False, "B4 accepted rows overclaimed")
    checks.check(summary.get("counts_as_complete_work_precision_curve") is False, "work/precision overclaimed")
    checks.check(summary.get("promotion_ready") is False, "promotion readiness overclaimed")
    checks.check(summary.get("b4_can_close_from_this_evidence") is False, "B4 overclosed")
    checks.check(summary.get("b7_can_close_from_this_evidence") is False, "B7 overclosed")
    checks.check(
        summary.get("canonical_hi2022_output_untouched_by_writer") is True,
        "canonical output protection marker missing",
    )
    checks.check(summary.get("isolated_rows_output") == f"{STEM}_rows.csv", "isolated rows output changed")

    if status == "executed_full_T8_selected_coarse_trio_not_promoted":
        checks.check(summary.get("execute_requested") is True, "executed artifact did not request execution")
        checks.check(summary.get("heavy_numerical_run_invoked") is True, "executed artifact missing heavy-run marker")
        checks.check(summary.get("ok_row_count") == 3, "executed artifact not complete")
        checks.check(summary.get("selected_step_trio_completed") is True, "executed trio not complete")
        checks.check(summary.get("reference_status") == "ok", "reference status changed")
        checks.check(float(summary.get("reference_runtime_sec")) > 0.0, "reference runtime missing")
        checks.check(
            len(summary.get("runtime_sec_values", [])) == 3
            and all(float(value) > 0.0 for value in summary.get("runtime_sec_values", [])),
            "runtime values missing",
        )
        checks.check(summary.get("position_pair_orders") == pair_orders(rows, "pos_final_linf"), "position orders stale")
        checks.check(summary.get("velocity_pair_orders") == pair_orders(rows, "vel_final_linf"), "velocity orders stale")
        checks.check(
            summary.get("acceleration_pair_orders") == pair_orders(rows, "acc_final_linf"),
            "acceleration orders stale",
        )

    for row in rows:
        checks.check(row.get("form") == "rA", f"row {row.get('h')} form changed")
        checks.check(row.get("model") == "double_pendulum", f"row {row.get('h')} model changed")
        checks.check(row.get("t_end") == "8.0", f"row {row.get('h')} T changed")
        checks.check(row.get("reference_h") == "0.001", f"row {row.get('h')} reference h changed")
        checks.check(row.get("row_type") == "full_T8_selected_source_policy_candidate", f"row {row.get('h')} type changed")
        checks.check(row.get("source_policy_time_window_selected") == "True", f"row {row.get('h')} T marker missing")
        checks.check(row.get("source_policy_reference_h_selected") == "True", f"row {row.get('h')} ref marker missing")
        checks.check(row.get("source_policy_selected_coarse_h") == "True", f"row {row.get('h')} h marker missing")
        checks.check(row.get("full_public_grid_selected") == "False", f"row {row.get('h')} overclaims full grid")
        checks.check(row.get("source_policy_row_promoted") == "False", f"row {row.get('h')} promoted")
        checks.check(row.get("canonical_hi2022_output_untouched") == "True", f"row {row.get('h')} canonical marker missing")

    for token in [
        "Status: **",
        "T=8 time window selected: `True`.",
        "Reference h selected: `True`.",
        "Selected step sizes: `[0.02, 0.01, 0.005]`.",
        "Full public grid selected: `False`.",
        "Source-policy 1e-4 included: `False`.",
        "Full T=8 policy completed: `False`.",
        "Source-policy rows promoted: `0`.",
        "Source-policy rows closed by this evidence: `0`.",
        "Promotion ready: `False`.",
        "B4/B7 can close from this candidate: `False/False`.",
        "Canonical HI2022 output untouched by this writer: `True`.",
        "selected coarse trio is not the full encoded HI2022 public step family",
    ]:
        checks.check(token in md, f"markdown missing token: {token}")

    if checks.errors:
        print("HI2022 full T=8 source-policy candidate validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("HI2022 full T=8 source-policy candidate validation: PASS")
    print(f"status={status}")
    print("source_policy_time_window_selected=True")
    print(f"source_policy_candidate_rows_completed={len(ok_rows)}/3")
    print("source_policy_rows_closed_by_this_evidence=0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
