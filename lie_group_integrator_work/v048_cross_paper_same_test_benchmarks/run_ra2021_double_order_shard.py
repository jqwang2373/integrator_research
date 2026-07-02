#!/usr/bin/env python3
"""Run one 2021 public double-pendulum dynamic self-reference order shard."""

from __future__ import annotations

import argparse

import run_v048 as rv


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--form", required=True, choices=rv.RA2021_FORMS)
    parser.add_argument(
        "--step-sizes",
        default=",".join(str(h) for h in rv.RA2021_DOUBLE_ORDER_STEP_SIZES),
    )
    parser.add_argument("--reference-h", type=float, default=rv.RA2021_DOUBLE_ORDER_REFERENCE_H)
    parser.add_argument("--t-end", type=float, default=rv.RA2021_PUBLIC_T_END)
    parser.add_argument("--tol", type=float, default=None)
    parser.add_argument(
        "--allow-source-policy-1e-4",
        action="store_true",
        help="permit explicit h<=1e-4 source-policy rows; default shard runs stay coarse-first",
    )
    args = parser.parse_args()

    step_sizes = tuple(rv.parse_float_csv(args.step_sizes))
    rv.require_source_policy_1e4_allow(
        parser,
        args.allow_source_policy_1e_4,
        "2021 double-pendulum order shard",
        step_sizes + (float(args.reference_h),),
    )
    config = rv.RA2021DoubleOrderConfig(
        policy="ra2021_double_pendulum_dynamic_self_reference_order_policy",
        run_mode="ra2021_double_pendulum_dynamic_self_reference_order_shard",
        forms=(args.form,),
        step_sizes=step_sizes,
        reference_h=float(args.reference_h),
        t_end=float(args.t_end),
        tolerance=None if args.tol is None else float(args.tol),
        run_public_code=True,
        full_ra2021_double_order_completed=False,
    )
    rows, summary = rv.run_ra2021_double_pendulum_order_rows(config)
    shard_dir = rv.RESULTS / "ra2021_double_order_shards"
    shard_dir.mkdir(parents=True, exist_ok=True)
    tag = f"{args.form}_double_pendulum_{args.reference_h:g}".replace(".", "p").replace("-", "m")
    rv.write_csv(shard_dir / f"{tag}.csv", rows)
    print(
        "ra2021_double_order_shard=ok "
        f"group={args.form}:double_pendulum rows={summary['ok_row_count']}/{summary['row_count']}"
    )


if __name__ == "__main__":
    main()
