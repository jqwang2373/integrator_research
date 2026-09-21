#!/usr/bin/env python3
"""Build coarse-first same-window single-pendulum order/work rows."""

from __future__ import annotations

import math
from pathlib import Path

import run_v048 as rv


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
STEP_SIZES = (0.1, 0.05, 0.025)
REFERENCE_H = 0.0125
T_END = rv.RA2021_PUBLIC_T_END


def row_float(row: dict, key: str) -> float:
    try:
        return float(row.get(key, "nan"))
    except (TypeError, ValueError):
        return float("nan")


def fmt(value: float | None) -> str:
    if value is None or not math.isfinite(value):
        return "nan"
    return f"{value:.16e}"


def public_error(row: dict, key: str) -> float:
    return row_float(row, key)


def local_error(row: dict, key: str) -> float:
    mapping = {
        "pos_final_linf": "position_l2_error",
        "vel_final_linf": "velocity_l2_error",
        "acc_final_linf": "omega_l2_error",
    }
    return row_float(row, mapping[key])


def estimate_public_order(rows: list[dict], key: str) -> float | None:
    ok_rows = sorted([row for row in rows if row.get("status") == "ok"], key=lambda row: row_float(row, "h"), reverse=True)
    return rv.finite_or_none(
        rv.estimate_order([row_float(row, "h") for row in ok_rows], [public_error(row, key) for row in ok_rows])
    )


def estimate_local_order(rows: list[dict], key: str) -> float | None:
    ok_rows = sorted([row for row in rows if row.get("status") == "ok"], key=lambda row: row_float(row, "h"), reverse=True)
    return rv.finite_or_none(
        rv.estimate_order([row_float(row, "h") for row in ok_rows], [local_error(row, key) for row in ok_rows])
    )


def build_public_rows() -> tuple[list[dict], dict]:
    rv.switch_simengine_root(rv.SBEL_C2)
    rv.patch_modern_numpy_scalar_assignments()
    model = rv.RA2021_MODEL_BY_NAME["single_pendulum"]
    groups = tuple((form, model) for form in rv.RA2021_FORMS)
    config = rv.RA2021OrderConfig(
        policy="ra2021_single_pendulum_coarse_same_window_policy_not_full_campaign",
        run_mode="ra2021_single_pendulum_coarse_same_window",
        forms=tuple(rv.RA2021_FORMS),
        models=(model,),
        groups=groups,
        step_sizes=STEP_SIZES,
        reference_h=REFERENCE_H,
        t_end=T_END,
        run_public_code=True,
        full_ra2021_order_completed=False,
    )
    rows, summary = rv.run_ra2021_order_rows(config)
    for row in rows:
        row["coarse_same_window_policy"] = "True"
        row["public_policy_h"] = "False"
        row["notes"] = (
            "Coarse same-window single-pendulum public baseline row at T=3, "
            "h=0.1|0.05|0.025, reference h=0.0125. This is intentionally not "
            "the public h=1e-4 source policy."
        )
    summary.update(
        {
            "coarse_same_window_policy": True,
            "full_external_campaign_completed": False,
            "selected_step_trio_group_count": sum(
                1
                for form in rv.RA2021_FORMS
                if sum(1 for row in rows if row.get("form") == form and row.get("status") == "ok") == len(STEP_SIZES)
            ),
            "selected_step_trio_required_group_count": len(rv.RA2021_FORMS),
            "notes": "Coarse same-window single-pendulum public rows; no default h=1e-4 execution.",
        }
    )
    return rows, summary


def build_local_rows() -> tuple[list[dict], dict]:
    config = rv.Gauss6PublicSingleConfig(
        policy="gauss6_fullva_public_horizon_single_coarse_not_full_campaign",
        run_mode="gauss6_fullva_public_horizon_single_coarse",
        step_sizes=STEP_SIZES,
        reference_h=REFERENCE_H,
        t_end=T_END,
        run_model=True,
    )
    rows, summary = rv.run_gauss6_fullva_public_horizon_single_rows(config)
    for row in rows:
        row["row_type"] = "public_horizon_single_pendulum_coarse_order_work"
        row["coarse_same_window_policy"] = "True"
        row["public_policy_h"] = "False"
        row["notes"] = (
            "Coarse same-window Gauss6/FullVA single-pendulum row at T=3, "
            "h=0.1|0.05|0.025, reference h=0.0125. This is intentionally not "
            "the public h=1e-4 source policy."
        )
    summary.update(
        {
            "coarse_same_window_policy": True,
            "public_policy_h_rows_completed": 0,
            "public_single_step_trio_completed": False,
            "full_external_campaign_completed": False,
            "notes": "Coarse same-window Gauss6/FullVA single-pendulum rows; no default h=1e-4 execution.",
        }
    )
    return rows, summary


def build_work_summary(public_rows: list[dict], local_rows: list[dict]) -> tuple[list[dict], dict]:
    grouped: dict[str, list[dict]] = {}
    for form in rv.RA2021_FORMS:
        form_rows = [row for row in public_rows if row.get("form") == form and row.get("status") == "ok"]
        if form_rows:
            grouped[f"{form}-public-dynamics-coarse"] = form_rows
    ok_local_rows = [row for row in local_rows if row.get("status") == "ok"]
    if ok_local_rows:
        grouped["Gauss6/FullVA-public-horizon-single-coarse"] = ok_local_rows

    rA_rows = grouped.get("rA-public-dynamics-coarse", [])
    rA_finest = sorted(rA_rows, key=lambda row: row_float(row, "h"))[0] if rA_rows else {}

    summary_rows: list[dict] = []
    for method, rows in sorted(grouped.items()):
        sorted_rows = sorted(rows, key=lambda row: row_float(row, "h"))
        finest = sorted_rows[0] if sorted_rows else {}
        is_local = method.startswith("Gauss6/FullVA")
        error_fn = local_error if is_local else public_error
        order_fn = estimate_local_order if is_local else estimate_public_order
        runtime_num = row_float(finest, "runtime_sec")
        runtime_den = row_float(rA_finest, "runtime_sec")

        def ratio(key: str) -> str:
            numerator = error_fn(finest, key)
            denominator = public_error(rA_finest, key)
            if not math.isfinite(numerator) or not math.isfinite(denominator) or denominator == 0.0:
                return "nan"
            return f"{numerator / denominator:.16e}"

        summary_rows.append(
            {
                "policy": "ra2021_single_pendulum_coarse_same_window_work_precision_summary",
                "source_suite": "ra2021_taves_kissel_negrut",
                "case_id": "ra2021_single_pendulum_coarse_same_window_work_precision",
                "model": "single_pendulum",
                "method": method,
                "row_count": len(rows),
                "ok_row_count": len([row for row in rows if row.get("status") == "ok"]),
                "t_end": finest.get("t_end", "nan"),
                "reference_policy": finest.get("reference_policy", "public_kinematics_or_analytic_exact"),
                "reference_h": finest.get("reference_h", "nan"),
                "finest_h": fmt(row_float(finest, "h")),
                "pos_observed_order": fmt(order_fn(rows, "pos_final_linf")),
                "vel_observed_order": fmt(order_fn(rows, "vel_final_linf")),
                "acc_or_omega_observed_order": fmt(order_fn(rows, "acc_final_linf")),
                "finest_pos_error": fmt(error_fn(finest, "pos_final_linf")),
                "finest_vel_error": fmt(error_fn(finest, "vel_final_linf")),
                "finest_acc_or_omega_error": fmt(error_fn(finest, "acc_final_linf")),
                "finest_runtime_sec": fmt(runtime_num),
                "runtime_sec_sum": fmt(rv.finite_sum([row_float(row, "runtime_sec") for row in rows])),
                "finest_pos_error_ratio_vs_rA": ratio("pos_final_linf"),
                "finest_vel_error_ratio_vs_rA": ratio("vel_final_linf"),
                "finest_acc_or_omega_error_ratio_vs_rA": ratio("acc_final_linf"),
                "finest_runtime_ratio_vs_rA": fmt(
                    runtime_num / runtime_den
                    if math.isfinite(runtime_num) and math.isfinite(runtime_den) and runtime_den != 0.0
                    else float("nan")
                ),
                "iteration_or_newton_sum": fmt(
                    rv.finite_sum(
                        [
                            row_float(row, "avg_iterations")
                            if math.isfinite(row_float(row, "avg_iterations"))
                            else row_float(row, "total_newton_iterations")
                            for row in rows
                        ]
                    )
                ),
                "notes": (
                    "Coarse same-window single-pendulum order/work summary. "
                    "All rows use T=3, h=0.1|0.05|0.025, reference h=0.0125. "
                    "This is not the source h=1e-4 policy and not an external superiority claim."
                ),
            }
        )

    summary = {
        "policy": "ra2021_single_pendulum_coarse_same_window_work_precision_summary",
        "row_count": len(summary_rows),
        "ok_row_count": sum(1 for row in summary_rows if int(row["ok_row_count"]) >= 1),
        "methods": sorted({row["method"] for row in summary_rows}),
        "selected_step_sizes": list(STEP_SIZES),
        "selected_reference_h": REFERENCE_H,
        "selected_t_end": T_END,
        "full_external_campaign_completed": False,
        "external_superiority_claim": False,
        "default_policy": "coarse_first_no_default_1e-4",
        "notes": "Coarse same-window single-pendulum order/time summary; no external superiority claim.",
    }
    return summary_rows, summary


def write_markdown(summary_rows: list[dict], summary: dict) -> None:
    lines = [
        "# Single-Pendulum Coarse Same-Window Work/Precision",
        "",
        "Status: **coarse-first evidence only; not external superiority**",
        "",
        f"- Selected window: `T={summary['selected_t_end']}`, `h=0.1|0.05|0.025`.",
        f"- Reference h: `{summary['selected_reference_h']}`.",
        f"- Rows: `{summary['ok_row_count']}/{summary['row_count']}`.",
        f"- Default policy: `{summary['default_policy']}`.",
        "",
        "Reading rule: this artifact intentionally avoids default `1e-4` rows.",
        "",
        "| Method | Pos. order | Vel. order | Acc./omega order | Finest pos error | Finest vel error | Runtime ratio vs rA |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in summary_rows:
        lines.append(
            "| "
            f"`{row['method']}` | "
            f"{row['pos_observed_order']} | "
            f"{row['vel_observed_order']} | "
            f"{row['acc_or_omega_observed_order']} | "
            f"{row['finest_pos_error']} | "
            f"{row['finest_vel_error']} | "
            f"{row['finest_runtime_ratio_vs_rA']} |"
        )
    lines.append("")
    (RESULTS / "single_pendulum_coarse_same_window_work_precision_summary.md").write_text(
        "\n".join(lines),
        encoding="utf-8",
    )


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    public_rows, public_summary = build_public_rows()
    local_rows, local_summary = build_local_rows()
    work_rows, work_summary = build_work_summary(public_rows, local_rows)

    rv.write_csv(RESULTS / "ra2021_single_pendulum_coarse_order_rows.csv", public_rows)
    rv.write_csv(RESULTS / "gauss6_fullva_public_horizon_single_coarse_rows.csv", local_rows)
    rv.write_csv(RESULTS / "single_pendulum_coarse_same_window_work_precision_summary.csv", work_rows)
    rv.write_json_atomic(RESULTS / "single_pendulum_coarse_same_window_work_precision_summary.json", work_summary)
    write_markdown(work_rows, work_summary)

    summary = rv.read_or_rebuild_summary()
    summary["ra2021_single_pendulum_coarse_order"] = public_summary
    summary["gauss6_fullva_public_horizon_single_coarse"] = local_summary
    summary["single_pendulum_coarse_same_window_work_precision_summary"] = work_summary
    rv.write_json_atomic(RESULTS / "summary_v048.json", summary)
    rv.write_report(summary)

    print("single_pendulum_coarse_same_window=written")
    print(f"public_rows={public_summary['ok_row_count']}/{public_summary['row_count']}")
    print(f"local_rows={local_summary['ok_row_count']}/{local_summary['row_count']}")
    print(f"work_precision_rows={work_summary['ok_row_count']}/{work_summary['row_count']}")
    print("default_policy=coarse_first_no_default_1e-4")


if __name__ == "__main__":
    main()
