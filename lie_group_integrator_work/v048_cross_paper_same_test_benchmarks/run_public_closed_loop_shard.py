#!/usr/bin/env python3
"""Run one public-horizon Gauss6/FullVA closed-loop shard.

The shard writes independent CSV/JSON artifacts so several models can run in
parallel without racing on the main v048 summary files.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import run_v048 as rv


def safe_float_token(value: float) -> str:
    return f"{value:.0e}".replace("+", "").replace("-", "m").replace(".", "p")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", required=True, choices=["four_link", "slider_crank"])
    parser.add_argument("--step-sizes", default="0.02,0.01,0.005")
    parser.add_argument(
        "--allow-source-policy-1e-4",
        action="store_true",
        help="permit explicit 1e-4 source-policy rows; default shard runs stay coarse",
    )
    parser.add_argument("--t-end", type=float, default=rv.RA2021_PUBLIC_T_END)
    parser.add_argument("--reference-h", type=float, default=rv.RA2021_PUBLIC_REFERENCE_H)
    args = parser.parse_args()

    step_sizes = rv.parse_float_csv(args.step_sizes)
    rv.require_source_policy_1e4_allow(
        parser,
        args.allow_source_policy_1e_4,
        "public closed-loop shard",
        step_sizes + (float(args.reference_h),),
    )
    config = rv.Gauss6ClosedLoopConfig(
        policy="gauss6_fullva_public_horizon_closed_loop_kinematic_reaction_not_full_campaign",
        run_mode="gauss6_fullva_public_horizon_closed_loop_2021_tranche_shard",
        models=(args.model,),
        step_sizes=step_sizes,
        reference_h=float(args.reference_h),
        t_end=float(args.t_end),
        run_model=True,
    )
    rows, summary = rv.run_gauss6_fullva_closed_loop_external_rows(config)
    shard_dir = rv.RESULTS / "public_closed_loop_shards"
    shard_dir.mkdir(parents=True, exist_ok=True)
    step_token = "_".join(safe_float_token(h) for h in step_sizes)
    csv_path = shard_dir / f"{args.model}_{step_token}.csv"
    json_path = shard_dir / f"{args.model}_{step_token}.json"
    rv.write_csv(csv_path, rows)
    with json_path.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print(f"public_closed_loop_shard=ok model={args.model} rows={summary['ok_row_count']}/{summary['row_count']}")
    print(f"csv={csv_path}")


if __name__ == "__main__":
    main()
