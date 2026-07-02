#!/usr/bin/env python3
"""Merge 2022 Half-Implicit model shards into canonical v048 artifacts."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import run_v048


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--models", default="single_pendulum,double_pendulum,four_link,slider_crank")
    parser.add_argument("--in-dir", default=str(run_v048.RESULTS / "hi2022_model_shards"))
    args = parser.parse_args()

    rows: list[dict[str, str]] = []
    in_dir = Path(args.in_dir)
    for model in run_v048.select_hi2022_models(args.models):
        path = in_dir / f"hi2022_{model}_rows.csv"
        if not path.exists():
            raise FileNotFoundError(path)
        rows.extend(read_csv(path))

    rows.sort(key=lambda row: (row.get("model", ""), row.get("form", ""), run_v048.as_float(row, "h")))
    run_v048.write_csv(run_v048.RESULTS / "hi2022_halfimplicit_rows.csv", rows)

    config = run_v048.HI2022Config(
        policy="hi2022_bounded_four_example_pilot_not_full_campaign",
        run_mode="hi2022_bounded_four_example_pilot",
        forms=run_v048.select_hi2022_forms(",".join(run_v048.ordered_values(rows, "form", run_v048.HI2022_FORMS))),
        models=run_v048.select_hi2022_models(",".join(run_v048.ordered_values(rows, "model", run_v048.HI2022_MODELS))),
        step_sizes=tuple(run_v048.ordered_float_values(rows, "h")),
        reference_h=run_v048.rows_first_float(rows, "reference_h"),
        t_end=run_v048.rows_first_float(rows, "t_end"),
        tolerance_base=run_v048.HI2022_TOLERANCE_BASE,
        run_public_code=any(row.get("status") == "ok" for row in rows),
        full_hi2022_campaign_completed=False,
    )
    run_v048.write_csv(run_v048.RESULTS / "hi2022_workload_estimate.csv", run_v048.hi2022_workload_estimate(config))
    hi2022_summary = run_v048.summarize_hi2022_rows_from_csv(rows)
    summary = run_v048.read_or_rebuild_summary()
    summary["hi2022_halfimplicit"] = hi2022_summary
    summary["hi2022_halfimplicit_rows_completed"] = (
        hi2022_summary["selected_step_trio_group_count"]
        == hi2022_summary["selected_step_trio_required_group_count"]
    )
    run_v048.write_json_atomic(run_v048.RESULTS / "summary_v048.json", summary)
    run_v048.write_report(summary)
    print(
        f"hi2022_rows={hi2022_summary['ok_row_count']}/{hi2022_summary['row_count']} "
        f"groups={hi2022_summary['selected_step_trio_group_count']}/"
        f"{hi2022_summary['selected_step_trio_required_group_count']}"
    )


if __name__ == "__main__":
    main()
