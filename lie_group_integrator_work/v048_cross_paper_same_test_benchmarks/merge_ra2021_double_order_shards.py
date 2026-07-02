#!/usr/bin/env python3
"""Merge 2021 double-pendulum dynamic self-reference order shards."""

from __future__ import annotations

import csv
from pathlib import Path

import run_v048 as rv


KEYS = ("form", "model", "mode", "h", "reference_h", "t_end", "tolerance")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def row_key(row: dict[str, str]) -> tuple[str, ...]:
    return tuple(str(row.get(key, "")) for key in KEYS)


def sort_key(row: dict[str, str]) -> tuple[int, float]:
    form_order = {form: idx for idx, form in enumerate(rv.RA2021_FORMS)}
    return (form_order.get(row.get("form", ""), 99), rv.as_float(row, "h"))


def main() -> None:
    main_path = rv.RESULTS / "ra2021_double_pendulum_order_rows.csv"
    shard_dir = rv.RESULTS / "ra2021_double_order_shards"
    rows: dict[tuple[str, ...], dict[str, str]] = {}
    if main_path.exists():
        for row in read_csv(main_path):
            rows[row_key(row)] = row
    shard_count = 0
    for shard_path in sorted(shard_dir.glob("*.csv")) if shard_dir.exists() else []:
        shard_count += 1
        for row in read_csv(shard_path):
            rows[row_key(row)] = row
    merged = sorted(rows.values(), key=sort_key)
    rv.write_csv(main_path, merged)

    summary = rv.read_or_rebuild_summary()
    double_summary = rv.summarize_ra2021_double_pendulum_order_rows_from_csv(merged)
    summary["ra2021_double_pendulum_order"] = double_summary
    summary["same_test_campaign_status"] = "not_run"
    summary["external_superiority_claim"] = False
    summary["ra2021_double_order_shards_merged"] = shard_count
    rv.write_json_atomic(rv.RESULTS / "summary_v048.json", summary)
    rv.write_report(summary)
    print(f"ra2021_double_order_shards_merged={shard_count}")
    print(f"ra2021_double_order_rows={double_summary['ok_row_count']}/{double_summary['row_count']}")
    print(
        "ra2021_double_order_groups="
        f"{double_summary['selected_step_trio_group_count']}/{double_summary['selected_step_trio_required_group_count']}"
    )
    print("external_superiority_claim=False")


if __name__ == "__main__":
    main()
