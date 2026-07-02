#!/usr/bin/env python3
"""Run the public-horizon Gauss6/FullVA double-pendulum coarse tranche."""

from __future__ import annotations

import argparse

import run_v048 as rv


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--step-sizes", default="0.1,0.05,0.025")
    parser.add_argument("--reference-h", type=float, default=0.0125)
    parser.add_argument("--t-end", type=float, default=rv.RA2021_PUBLIC_T_END)
    parser.add_argument(
        "--allow-source-policy-1e-4",
        action="store_true",
        help="permit explicit h<=1e-4 rows; default shard runs stay coarse-first",
    )
    args = parser.parse_args()

    step_sizes = tuple(rv.parse_float_csv(args.step_sizes))
    rv.require_source_policy_1e4_allow(
        parser,
        args.allow_source_policy_1e_4,
        "public double coarse shard",
        step_sizes + (float(args.reference_h),),
    )
    config = rv.Gauss6PublicDoubleCoarseConfig(
        policy="gauss6_fullva_public_horizon_double_coarse_not_full_campaign",
        run_mode="gauss6_fullva_public_horizon_double_coarse",
        step_sizes=step_sizes,
        reference_h=float(args.reference_h),
        t_end=float(args.t_end),
        run_model=True,
    )
    rows, summary = rv.run_gauss6_fullva_public_horizon_double_coarse_rows(config)
    rv.write_csv(rv.RESULTS / "gauss6_fullva_public_horizon_double_coarse_rows.csv", rows)

    rebuilt = rv.rebuild_summary_from_existing_results()
    rebuilt["gauss6_fullva_public_horizon_double_coarse"] = summary
    rebuilt["same_test_campaign_status"] = "not_run"
    rebuilt["external_superiority_claim"] = False
    rv.write_json_atomic(rv.RESULTS / "summary_v048.json", rebuilt)
    rv.write_report(rebuilt)

    print(
        "public_double_coarse=ok "
        f"rows={summary['ok_row_count']}/{summary['row_count']} "
        f"pos_order={summary.get('pos_observed_order')} "
        f"vel_order={summary.get('vel_observed_order')}"
    )


if __name__ == "__main__":
    main()
