#!/usr/bin/env python3
"""Merge public-horizon closed-loop shards into v048 artifacts."""

from __future__ import annotations

import csv
from pathlib import Path

import run_v048 as rv


KEYS = ("model", "h", "t_end", "reference_h", "method", "row_type")


def row_key(row: dict[str, str]) -> tuple[str, ...]:
    return tuple(str(row.get(key, "")) for key in KEYS)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def sort_key(row: dict[str, str]) -> tuple[str, float]:
    return (row.get("model", ""), -rv.as_float(row, "h"))


def main() -> None:
    main_path = rv.RESULTS / "gauss6_fullva_public_horizon_closed_loop_rows.csv"
    shard_dir = rv.RESULTS / "public_closed_loop_shards"
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
    public_summary = rv.summarize_closed_loop_rows_from_csv(merged, public_horizon=True)
    summary["gauss6_fullva_public_horizon_closed_loop"] = public_summary
    summary["same_test_campaign_status"] = "not_run"
    summary["external_superiority_claim"] = False
    summary["public_closed_loop_shards_merged"] = shard_count
    rv.write_json_atomic(rv.RESULTS / "summary_v048.json", summary)
    rv.write_report(summary)
    print(f"public_closed_loop_shards_merged={shard_count}")
    print(f"public_closed_loop_rows={public_summary['ok_row_count']}/{public_summary['row_count']}")
    print(f"public_h_rows={public_summary['public_step_size_rows_completed']}/{public_summary['public_step_size_required_count']}")
    print("external_superiority_claim=False")


if __name__ == "__main__":
    main()
