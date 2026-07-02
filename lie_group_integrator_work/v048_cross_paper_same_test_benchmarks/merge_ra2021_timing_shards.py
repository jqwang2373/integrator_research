#!/usr/bin/env python3
"""Merge 2021 public timing/iteration shards."""

from __future__ import annotations

import csv
from pathlib import Path

import run_v048 as rv


KEYS = ("form", "model", "mode", "h", "t_end", "tolerance")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def row_key(row: dict[str, str]) -> tuple[str, ...]:
    return tuple(str(row.get(key, "")) for key in KEYS)


def sort_key(row: dict[str, str]) -> tuple[int, int]:
    form_order = {form: idx for idx, form in enumerate(rv.RA2021_FORMS)}
    model_order = {model.name: idx for idx, model in enumerate(rv.RA2021_TIMING_MODELS)}
    return (
        form_order.get(row.get("form", ""), 99),
        model_order.get(row.get("model", ""), 99),
    )


def main() -> None:
    main_path = rv.RESULTS / "ra2021_public_timing_rows.csv"
    shard_dir = rv.RESULTS / "ra2021_timing_shards"
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
    timing_summary = rv.summarize_ra2021_timing_rows_from_csv(merged)
    summary["ra2021_public_timing"] = timing_summary
    summary["same_test_campaign_status"] = "not_run"
    summary["external_superiority_claim"] = False
    summary["ra2021_timing_shards_merged"] = shard_count
    rv.write_json_atomic(rv.RESULTS / "summary_v048.json", summary)
    rv.write_report(summary)
    print(f"ra2021_timing_shards_merged={shard_count}")
    print(f"ra2021_timing_rows={timing_summary['ok_row_count']}/{timing_summary['row_count']}")
    print(
        "ra2021_public_timing_policy_rows="
        f"{timing_summary['public_timing_rows_completed']}/{timing_summary['public_timing_required_count']}"
    )
    print("external_superiority_claim=False")


if __name__ == "__main__":
    main()
