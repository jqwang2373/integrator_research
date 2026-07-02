#!/usr/bin/env python3
"""Run one 2022 Half-Implicit model shard for the v048 benchmark ledger."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import run_v048


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", required=True, choices=run_v048.HI2022_MODELS)
    parser.add_argument("--forms", default="rA,rA_half")
    parser.add_argument("--step-sizes", default="0.02,0.01,0.005")
    parser.add_argument("--reference-h", type=float, default=run_v048.HI2022_REFERENCE_H)
    parser.add_argument("--t-end", type=float, default=0.1)
    parser.add_argument("--tolerance-base", type=float, default=run_v048.HI2022_TOLERANCE_BASE)
    parser.add_argument("--plan-only", action="store_true")
    parser.add_argument(
        "--allow-source-policy-1e-4",
        action="store_true",
        help="permit explicit h<=1e-4 source-policy rows; default shard runs stay coarse-first",
    )
    parser.add_argument("--out-dir", default=str(run_v048.RESULTS / "hi2022_model_shards"))
    args = parser.parse_args()

    step_sizes = run_v048.parse_float_csv(args.step_sizes)
    if not args.plan_only:
        run_v048.require_source_policy_1e4_allow(
            parser,
            args.allow_source_policy_1e_4,
            "2022 half-implicit model shard",
            step_sizes + (float(args.reference_h),),
        )
    config = run_v048.HI2022Config(
        policy="hi2022_bounded_four_example_pilot_not_full_campaign",
        run_mode="hi2022_bounded_four_example_pilot_model_shard",
        forms=run_v048.select_hi2022_forms(args.forms),
        models=(args.model,),
        step_sizes=step_sizes,
        reference_h=args.reference_h,
        t_end=args.t_end,
        tolerance_base=args.tolerance_base,
        run_public_code=not args.plan_only,
        full_hi2022_campaign_completed=False,
    )
    rows, summary = run_v048.run_hi2022_halfimplicit_rows(config)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    run_v048.write_csv(out_dir / f"hi2022_{args.model}_rows.csv", rows)
    with (out_dir / f"hi2022_{args.model}_summary.json").open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print(
        f"hi2022_model_shard={args.model} "
        f"ok={summary['ok_row_count']}/{summary['row_count']} "
        f"groups={summary['selected_step_trio_group_count']}/{summary['selected_step_trio_required_group_count']}"
    )


if __name__ == "__main__":
    main()
