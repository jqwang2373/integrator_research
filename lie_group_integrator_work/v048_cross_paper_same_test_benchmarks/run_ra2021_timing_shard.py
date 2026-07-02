#!/usr/bin/env python3
"""Run one 2021 public timing/iteration shard."""

from __future__ import annotations

import argparse

import run_v048 as rv


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--form", required=True, choices=rv.RA2021_FORMS)
    parser.add_argument(
        "--model",
        required=True,
        choices=sorted(rv.RA2021_TIMING_MODEL_BY_NAME),
    )
    parser.add_argument("--mode", default="dynamics")
    parser.add_argument("--h", type=float, default=rv.RA2021_PUBLIC_REFERENCE_H)
    parser.add_argument("--t-end", type=float, default=rv.RA2021_PUBLIC_T_END)
    parser.add_argument("--tol", type=float, default=None)
    parser.add_argument(
        "--allow-source-policy-1e-4",
        action="store_true",
        help="permit explicit h<=1e-4 timing rows; default shard runs stay coarse-first",
    )
    args = parser.parse_args()

    rv.require_source_policy_1e4_allow(
        parser,
        args.allow_source_policy_1e_4,
        "2021 timing shard",
        (float(args.h),),
    )
    model = rv.RA2021_TIMING_MODEL_BY_NAME[args.model]
    config = rv.RA2021TimingConfig(
        policy="ra2021_public_timing_iteration_policy_not_order_rows",
        run_mode="ra2021_public_timing_iteration_shard",
        forms=(args.form,),
        models=(model,),
        groups=((args.form, model),),
        h=float(args.h),
        t_end=float(args.t_end),
        tolerance=None if args.tol is None else float(args.tol),
        mode=str(args.mode),
        run_public_code=True,
        full_ra2021_timing_completed=False,
    )
    rows, summary = rv.run_ra2021_timing_rows(config)
    shard_dir = rv.RESULTS / "ra2021_timing_shards"
    shard_dir.mkdir(parents=True, exist_ok=True)
    tag = f"{args.form}_{args.model}_{args.mode}_{args.h:g}".replace(".", "p").replace("-", "m")
    rv.write_csv(shard_dir / f"{tag}.csv", rows)
    print(
        "ra2021_timing_shard=ok "
        f"group={args.form}:{args.model} rows={summary['ok_row_count']}/{summary['row_count']}"
    )


if __name__ == "__main__":
    main()
