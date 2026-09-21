#!/usr/bin/env python3
"""Build the four-example method-performance matrix from existing artifacts."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path


HERE = Path(__file__).resolve().parent
WORK_ROOT = HERE.parent
RESULTS = HERE / "results"
V046 = WORK_ROOT / "v046_asme_four_examples_validation" / "results"
V047 = WORK_ROOT / "v047_cylindrical_chain_pipeline" / "results"

EXAMPLES = ("single_pendulum", "double_pendulum", "four_link", "slider_crank")
PUBLIC_FORMS = ("rA", "rp", "reps")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def as_float(row: dict, key: str) -> float:
    try:
        return float(row.get(key, "nan"))
    except (TypeError, ValueError):
        return float("nan")


def fmt(value: float | None) -> str:
    if value is None or not math.isfinite(value):
        return "nan"
    return f"{value:.16e}"


def observed_order(rows: list[dict], h_key: str, error_key: str) -> float | None:
    clean = [(as_float(row, h_key), as_float(row, error_key)) for row in rows if row.get("status") == "ok"]
    clean = [(h, err) for h, err in clean if h > 0.0 and err > 0.0 and math.isfinite(h) and math.isfinite(err)]
    if len(clean) < 2:
        return None
    n = len(clean)
    sx = sum(math.log(h) for h, _ in clean)
    sy = sum(math.log(err) for _, err in clean)
    sxx = sum(math.log(h) ** 2 for h, _ in clean)
    sxy = sum(math.log(h) * math.log(err) for h, err in clean)
    denom = n * sxx - sx * sx
    if denom == 0.0:
        return None
    return (n * sxy - sx * sy) / denom


def unique_floats(rows: list[dict], key: str) -> str:
    values = sorted({as_float(row, key) for row in rows if math.isfinite(as_float(row, key))}, reverse=True)
    return "|".join(f"{value:.6g}" for value in values)


def has_required_h_values(rows: list[dict], required: tuple[float, ...]) -> bool:
    ok_h = [as_float(row, "h") for row in rows if row.get("status") == "ok"]
    return all(any(math.isclose(h, required_h, rel_tol=1.0e-12, abs_tol=1.0e-15) for h in ok_h) for required_h in required)


def sum_float(rows: list[dict], key: str) -> float:
    values = [as_float(row, key) for row in rows if math.isfinite(as_float(row, key))]
    return sum(values) if values else float("nan")


def max_float(rows: list[dict], key: str) -> float:
    values = [as_float(row, key) for row in rows if math.isfinite(as_float(row, key))]
    return max(values) if values else float("nan")


def min_h_row(rows: list[dict]) -> dict | None:
    ok_rows = [row for row in rows if row.get("status") == "ok" and math.isfinite(as_float(row, "h"))]
    if not ok_rows:
        return None
    return min(ok_rows, key=lambda row: as_float(row, "h"))


def add_row(
    rows: list[dict],
    *,
    family: str,
    method: str,
    example: str,
    source_suite: str,
    status: str,
    evidence: str,
    row_count: int = 0,
    ok_count: int = 0,
    h_values: str = "",
    t_end: str = "nan",
    pos_order: float | None = None,
    vel_order: float | None = None,
    acc_order: float | None = None,
    finest_pos_error: float | None = None,
    finest_vel_error: float | None = None,
    finest_acc_error: float | None = None,
    total_runtime_sec: float | None = None,
    finest_runtime_sec: float | None = None,
    total_newton_or_iterations: float | None = None,
    max_newton_or_iterations: float | None = None,
    caveat: str = "",
) -> None:
    rows.append(
        {
            "family": family,
            "method": method,
            "example": example,
            "source_suite": source_suite,
            "status": status,
            "row_count": row_count,
            "ok_count": ok_count,
            "h_values": h_values,
            "t_end": t_end,
            "pos_order": fmt(pos_order),
            "vel_order": fmt(vel_order),
            "acc_order": fmt(acc_order),
            "finest_pos_error": fmt(finest_pos_error),
            "finest_vel_error": fmt(finest_vel_error),
            "finest_acc_error": fmt(finest_acc_error),
            "total_runtime_sec": fmt(total_runtime_sec),
            "finest_runtime_sec": fmt(finest_runtime_sec),
            "total_newton_or_iterations": fmt(total_newton_or_iterations),
            "max_newton_or_iterations": fmt(max_newton_or_iterations),
            "evidence": evidence,
            "caveat": caveat,
        }
    )


def add_missing_rows(rows: list[dict], existing_keys: set[tuple[str, str]], method: str, family: str, source: str, status: str, caveat: str) -> None:
    for example in EXAMPLES:
        key = (method, example)
        if key not in existing_keys:
            add_row(
                rows,
                family=family,
                method=method,
                example=example,
                source_suite=source,
                status=status,
                evidence="not_yet_available",
                caveat=caveat,
            )


def build_matrix() -> tuple[list[dict], dict]:
    rows: list[dict] = []

    v046_rows = read_csv(V046 / "asme_four_examples_validation.csv")
    for example in EXAMPLES:
        erows = [row for row in v046_rows if row.get("model") == example and row.get("form") == "rA"]
        finest = min_h_row(erows)
        add_row(
            rows,
            family="Kissel/Taves/Negrut 2021",
            method="rA-v046-short-window",
            example=example,
            source_suite="v046_asme_four_examples_validation",
            status="completed_short_window" if erows else "not_run",
            row_count=len(erows),
            ok_count=sum(1 for row in erows if row.get("status") == "ok"),
            h_values=unique_floats(erows, "h"),
            t_end="0.2",
            pos_order=observed_order(erows, "h", "pos_traj_linf"),
            vel_order=observed_order(erows, "h", "vel_traj_linf"),
            acc_order=observed_order(erows, "h", "acc_traj_linf"),
            finest_pos_error=as_float(finest, "pos_traj_linf") if finest else None,
            finest_vel_error=as_float(finest, "vel_traj_linf") if finest else None,
            finest_acc_error=as_float(finest, "acc_traj_linf") if finest else None,
            total_runtime_sec=sum_float(erows, "runtime_sec"),
            finest_runtime_sec=as_float(finest, "runtime_sec") if finest else None,
            total_newton_or_iterations=sum_float(erows, "avg_iterations"),
            max_newton_or_iterations=max_float(erows, "max_iterations"),
            evidence="v046_asme_four_examples_validation/results/asme_four_examples_validation.csv",
            caveat="short T=0.2 v046 reproduction; public 2021 policy differs",
        )

    ra2021_rows = read_csv(RESULTS / "ra2021_order_rows.csv")
    double_order_path = RESULTS / "ra2021_double_pendulum_order_rows.csv"
    ra2021_double_order_rows = read_csv(double_order_path) if double_order_path.exists() else []
    timing_path = RESULTS / "ra2021_public_timing_rows.csv"
    ra2021_timing_rows = read_csv(timing_path) if timing_path.exists() else []
    for form in PUBLIC_FORMS:
        for example in EXAMPLES:
            erows = [row for row in ra2021_rows if row.get("form") == form and row.get("model") == example]
            double_erows = [
                row for row in ra2021_double_order_rows if row.get("form") == form and row.get("model") == example
            ]
            timing_erows = [
                row for row in ra2021_timing_rows if row.get("form") == form and row.get("model") == example
            ]
            finest = min_h_row(erows)
            if erows:
                status = "completed_public_order_policy"
                h_values = unique_floats(erows, "h")
                evidence = "v048_cross_paper_same_test_benchmarks/results/ra2021_order_rows.csv"
                caveat = "public 2021 order-analysis suite; double_pendulum is not an order-analysis model in this script"
            elif double_erows:
                double_ok = sum(1 for row in double_erows if row.get("status") == "ok")
                finest = min_h_row(double_erows)
                reference_runtime = as_float(double_erows[0], "reference_runtime_sec")
                add_row(
                    rows,
                    family="Kissel/Taves/Negrut 2021",
                    method=form,
                    example=example,
                    source_suite="ra2021_public_code",
                    status=(
                        "completed_public_dynamic_self_reference_order_policy"
                        if double_ok == len(double_erows) and len(double_erows) >= 3
                        else "partial_public_dynamic_self_reference_order_policy"
                    ),
                    row_count=len(double_erows),
                    ok_count=double_ok,
                    h_values=unique_floats(double_erows, "h"),
                    t_end="3.0",
                    pos_order=observed_order(double_erows, "h", "pos_final_linf"),
                    vel_order=observed_order(double_erows, "h", "vel_final_linf"),
                    acc_order=observed_order(double_erows, "h", "acc_final_linf"),
                    finest_pos_error=as_float(finest, "pos_final_linf") if finest else None,
                    finest_vel_error=as_float(finest, "vel_final_linf") if finest else None,
                    finest_acc_error=as_float(finest, "acc_final_linf") if finest else None,
                    total_runtime_sec=sum_float(double_erows, "runtime_sec")
                    + (reference_runtime if math.isfinite(reference_runtime) else 0.0),
                    finest_runtime_sec=as_float(finest, "runtime_sec") if finest else None,
                    total_newton_or_iterations=sum_float(double_erows, "avg_iterations"),
                    max_newton_or_iterations=max_float(double_erows, "max_iterations"),
                    evidence="v048_cross_paper_same_test_benchmarks/results/ra2021_double_pendulum_order_rows.csv",
                    caveat=(
                        "dynamic self-reference order; public order_analysis.py has no "
                        "double-pendulum kinematic-reference order row"
                    ),
                )
                continue
            elif timing_erows:
                timing_ok = sum(1 for row in timing_erows if row.get("status") == "ok")
                status = (
                    "completed_public_timing_policy"
                    if timing_ok == len(timing_erows)
                    else "partial_or_failed_public_timing_policy"
                )
                h_values = unique_floats(timing_erows, "h")
                evidence = "v048_cross_paper_same_test_benchmarks/results/ra2021_public_timing_rows.csv"
                caveat = (
                    "public timing/iteration row only; no kinematic-reference order/errors; "
                    "public order-analysis script has no double-pendulum order row"
                )
                add_row(
                    rows,
                    family="Kissel/Taves/Negrut 2021",
                    method=form,
                    example=example,
                    source_suite="ra2021_public_code",
                    status=status,
                    row_count=len(timing_erows),
                    ok_count=timing_ok,
                    h_values=h_values,
                    t_end="3.0",
                    total_runtime_sec=sum_float(timing_erows, "runtime_sec"),
                    finest_runtime_sec=as_float(min_h_row(timing_erows), "runtime_sec")
                    if min_h_row(timing_erows)
                    else None,
                    total_newton_or_iterations=sum_float(timing_erows, "avg_iterations"),
                    max_newton_or_iterations=max_float(timing_erows, "max_iterations"),
                    evidence=evidence,
                    caveat=caveat,
                )
                continue
            else:
                status = "not_in_2021_public_order_script" if example == "double_pendulum" else "not_run"
                h_values = ""
                evidence = "not_yet_available"
                caveat = "needs timing/iteration row or separate source-policy row for this example"
            add_row(
                rows,
                family="Kissel/Taves/Negrut 2021",
                method=form,
                example=example,
                source_suite="ra2021_public_code",
                status=status,
                row_count=len(erows),
                ok_count=sum(1 for row in erows if row.get("status") == "ok"),
                h_values=h_values,
                t_end="3.0" if erows else "nan",
                pos_order=observed_order(erows, "h", "pos_final_linf"),
                vel_order=observed_order(erows, "h", "vel_final_linf"),
                acc_order=observed_order(erows, "h", "acc_final_linf"),
                finest_pos_error=as_float(finest, "pos_final_linf") if finest else None,
                finest_vel_error=as_float(finest, "vel_final_linf") if finest else None,
                finest_acc_error=as_float(finest, "acc_final_linf") if finest else None,
                total_runtime_sec=sum_float(erows, "runtime_sec"),
                finest_runtime_sec=as_float(finest, "runtime_sec") if finest else None,
                total_newton_or_iterations=sum_float(erows, "avg_iterations"),
                max_newton_or_iterations=max_float(erows, "max_iterations"),
                evidence=evidence,
                caveat=caveat,
            )

    single_rows = read_csv(V047 / "cylindrical_chain_asme_single_absolute_fullva_runs.csv")
    finest = min_h_row(single_rows)
    add_row(
        rows,
        family="local proposed method",
        method="Gauss6/FullVA-v047",
        example="single_pendulum",
        source_suite="v047_asme_single_absolute",
        status="completed_internal_four_example_gate",
        row_count=len(single_rows),
        ok_count=sum(1 for row in single_rows if row.get("status") == "ok"),
        h_values=unique_floats(single_rows, "h"),
        t_end="0.2",
        pos_order=observed_order(single_rows, "h", "position_l2_error"),
        vel_order=observed_order(single_rows, "h", "velocity_l2_error"),
        acc_order=None,
        finest_pos_error=as_float(finest, "position_l2_error") if finest else None,
        finest_vel_error=as_float(finest, "velocity_l2_error") if finest else None,
        finest_acc_error=None,
        total_runtime_sec=sum_float(single_rows, "runtime_sec"),
        finest_runtime_sec=as_float(finest, "runtime_sec") if finest else None,
        total_newton_or_iterations=sum_float(single_rows, "total_newton_iterations"),
        max_newton_or_iterations=max_float(single_rows, "total_newton_iterations"),
        evidence="v047_cylindrical_chain_pipeline/results/cylindrical_chain_asme_single_absolute_fullva_runs.csv",
        caveat="single driven residual uses analytic reference; public-horizon tranche is recorded separately",
    )

    double_rows = read_csv(V047 / "cylindrical_chain_asme_double_method_runs.csv")
    finest = min_h_row(double_rows)
    add_row(
        rows,
        family="local proposed method",
        method="Gauss6/FullVA-v047",
        example="double_pendulum",
        source_suite="v047_asme_double_method",
        status="completed_internal_four_example_gate",
        row_count=len(double_rows),
        ok_count=sum(1 for row in double_rows if row.get("status") == "ok"),
        h_values=unique_floats(double_rows, "h"),
        t_end="0.2",
        pos_order=observed_order(double_rows, "h", "orientation_error_rad"),
        vel_order=observed_order(double_rows, "h", "omega_l2_error"),
        acc_order=None,
        finest_pos_error=as_float(finest, "orientation_error_rad") if finest else None,
        finest_vel_error=as_float(finest, "omega_l2_error") if finest else None,
        finest_acc_error=None,
        total_runtime_sec=sum_float(double_rows, "runtime_sec"),
        finest_runtime_sec=as_float(finest, "runtime_sec") if finest else None,
        total_newton_or_iterations=sum_float(double_rows, "total_newton_iterations"),
        max_newton_or_iterations=max_float(double_rows, "total_newton_iterations"),
        evidence="v047_cylindrical_chain_pipeline/results/cylindrical_chain_asme_double_method_runs.csv",
        caveat="method-side FullVA mapping with local nested reference",
    )

    closed_rows = read_csv(V047 / "cylindrical_chain_asme_closed_loop_kinematic_fullva.csv")
    reaction_rows = read_csv(V047 / "cylindrical_chain_asme_closed_loop_reaction_dynamics.csv")
    for example in ("four_link", "slider_crank"):
        erows = [row for row in closed_rows if row.get("model") == example]
        rrows = [row for row in reaction_rows if row.get("model") == example]
        finest = min_h_row(erows)
        add_row(
            rows,
            family="local proposed method",
            method="Gauss6/FullVA-v047",
            example=example,
            source_suite="v047_asme_closed_loop",
            status="completed_internal_four_example_gate",
            row_count=len(erows),
            ok_count=sum(1 for row in erows if row.get("status") == "ok"),
            h_values=unique_floats(erows, "h"),
            t_end="0.2",
            pos_order=None,
            vel_order=None,
            acc_order=None,
            finest_pos_error=as_float(finest, "pos_traj_linf") if finest else None,
            finest_vel_error=as_float(finest, "vel_traj_linf") if finest else None,
            finest_acc_error=as_float(finest, "acc_traj_linf") if finest else None,
            total_runtime_sec=sum_float(erows, "runtime_sec"),
            finest_runtime_sec=as_float(finest, "runtime_sec") if finest else None,
            total_newton_or_iterations=sum_float(erows, "total_newton_iterations"),
            max_newton_or_iterations=max_float(erows, "max_newton_iterations"),
            evidence="v047_cylindrical_chain_pipeline/results/cylindrical_chain_asme_closed_loop_kinematic_fullva.csv",
            caveat=(
                "driven closed-loop kinematic FullVA plus reaction reconstruction; "
                "trajectory differences sit at roundoff and are not interpreted as dynamic order; "
                f"max dynamics residual {max_float(rrows, 'max_dynamics_residual_norm'):.3e}"
            ),
        )

    public_single = read_csv(RESULTS / "gauss6_fullva_public_horizon_single_rows.csv")
    finest = min_h_row(public_single)
    add_row(
        rows,
        family="local proposed method",
        method="Gauss6/FullVA-public-horizon",
        example="single_pendulum",
        source_suite="v048_public_horizon",
        status="completed_public_horizon_trio",
        row_count=len(public_single),
        ok_count=sum(1 for row in public_single if row.get("status") == "ok"),
        h_values=unique_floats(public_single, "h"),
        t_end="3.0",
        pos_order=observed_order(public_single, "h", "position_l2_error"),
        vel_order=observed_order(public_single, "h", "velocity_l2_error"),
        acc_order=None,
        finest_pos_error=as_float(finest, "position_l2_error") if finest else None,
        finest_vel_error=as_float(finest, "velocity_l2_error") if finest else None,
        total_runtime_sec=sum_float(public_single, "runtime_sec"),
        finest_runtime_sec=as_float(finest, "runtime_sec") if finest else None,
        total_newton_or_iterations=sum_float(public_single, "total_newton_iterations"),
        max_newton_or_iterations=max_float(public_single, "total_newton_iterations"),
        evidence="v048_cross_paper_same_test_benchmarks/results/gauss6_fullva_public_horizon_single_rows.csv",
        caveat="roundoff/reference-floor limited final-error order",
    )

    public_closed = read_csv(RESULTS / "gauss6_fullva_public_horizon_closed_loop_rows.csv")
    for example in ("four_link", "slider_crank"):
        erows = [row for row in public_closed if row.get("model") == example]
        finest = min_h_row(erows)
        public_trio_completed = (
            len(erows) == 3
            and sum(1 for row in erows if row.get("status") == "ok") == 3
            and has_required_h_values(erows, (0.01, 0.001, 0.0001))
        )
        add_row(
            rows,
            family="local proposed method",
            method="Gauss6/FullVA-public-horizon",
            example=example,
            source_suite="v048_public_horizon",
            status=(
                "completed_public_horizon_residual_trio"
                if public_trio_completed
                else "partial_public_horizon_residual_rows"
            ),
            row_count=len(erows),
            ok_count=sum(1 for row in erows if row.get("status") == "ok"),
            h_values=unique_floats(erows, "h"),
            t_end="3.0",
            pos_order=observed_order(erows, "h", "pos_traj_linf"),
            vel_order=observed_order(erows, "h", "vel_traj_linf"),
            acc_order=observed_order(erows, "h", "acc_traj_linf"),
            finest_pos_error=as_float(finest, "pos_traj_linf") if finest else None,
            finest_vel_error=as_float(finest, "vel_traj_linf") if finest else None,
            finest_acc_error=as_float(finest, "acc_traj_linf") if finest else None,
            total_runtime_sec=sum_float(erows, "runtime_sec"),
            finest_runtime_sec=as_float(finest, "runtime_sec") if finest else None,
            total_newton_or_iterations=sum_float(erows, "total_newton_iterations"),
            max_newton_or_iterations=max_float(erows, "max_newton_iterations"),
            evidence="v048_cross_paper_same_test_benchmarks/results/gauss6_fullva_public_horizon_closed_loop_rows.csv",
            caveat=(
                "completed public h trio as closed-loop constraint/reaction residual rows; "
                "not public dynamic order/work-superiority rows"
                if public_trio_completed
                else "incomplete public h trio; residual rows, not public dynamic order/work rows"
            ),
        )
    public_double_coarse = read_csv(RESULTS / "gauss6_fullva_public_horizon_double_coarse_rows.csv")
    if public_double_coarse:
        finest = min_h_row(public_double_coarse)
        add_row(
            rows,
            family="local proposed method",
            method="Gauss6/FullVA-public-horizon",
            example="double_pendulum",
            source_suite="v048_public_horizon",
            status="completed_public_horizon_coarse_double_pilot",
            row_count=len(public_double_coarse),
            ok_count=sum(1 for row in public_double_coarse if row.get("status") == "ok"),
            h_values=unique_floats(public_double_coarse, "h"),
            t_end="3.0",
            pos_order=observed_order(public_double_coarse, "h", "pos_traj_linf"),
            vel_order=observed_order(public_double_coarse, "h", "vel_traj_linf"),
            acc_order=None,
            finest_pos_error=as_float(finest, "pos_traj_linf") if finest else None,
            finest_vel_error=as_float(finest, "vel_traj_linf") if finest else None,
            total_runtime_sec=sum_float(public_double_coarse, "runtime_sec"),
            finest_runtime_sec=as_float(finest, "runtime_sec") if finest else None,
            total_newton_or_iterations=sum_float(public_double_coarse, "total_newton_iterations"),
            max_newton_or_iterations=max_float(public_double_coarse, "total_newton_iterations"),
            evidence="v048_cross_paper_same_test_benchmarks/results/gauss6_fullva_public_horizon_double_coarse_rows.csv",
            caveat=(
                "coarse T=3 local v029 FullVA self-reference pilot with h=0.1|0.05|0.025; "
                "not the public h=1e-2|1e-3|1e-4 policy and not an external superiority row"
            ),
        )
    add_missing_rows(
        rows,
        {(row["method"], row["example"]) for row in rows},
        "Gauss6/FullVA-public-horizon",
        "local proposed method",
        "v048_public_horizon",
        "not_run",
        "double_pendulum public-horizon policy still needs an exact source-policy row",
    )

    hi_rows = read_csv(RESULTS / "hi2022_halfimplicit_rows.csv")
    for form in ("rA", "rA_half"):
        for example in EXAMPLES:
            erows = [row for row in hi_rows if row.get("form") == form and row.get("model") == example]
            if not erows:
                continue
            ok_count = sum(1 for row in erows if row.get("status") == "ok")
            finest = min_h_row(erows)
            add_row(
                rows,
                family="Fang/Kissel/Zhang/Negrut 2022",
                method=f"{form}-hi2022",
                example=example,
                source_suite="hi2022_halfimplicit",
                status="completed_bounded_pilot" if ok_count >= 3 else "partial_bounded_pilot",
                row_count=len(erows),
                ok_count=ok_count,
                h_values=unique_floats(erows, "h"),
                t_end="0.1",
                pos_order=observed_order(erows, "h", "pos_final_linf"),
                vel_order=observed_order(erows, "h", "vel_final_linf"),
                acc_order=observed_order(erows, "h", "acc_final_linf"),
                finest_pos_error=as_float(finest, "pos_final_linf") if finest else None,
                finest_vel_error=as_float(finest, "vel_final_linf") if finest else None,
                finest_acc_error=as_float(finest, "acc_final_linf") if finest else None,
                total_runtime_sec=sum_float(erows, "runtime_sec"),
                finest_runtime_sec=as_float(finest, "runtime_sec") if finest else None,
                total_newton_or_iterations=sum_float(erows, "avg_iterations"),
                max_newton_or_iterations=max_float(erows, "max_iterations"),
                evidence="v048_cross_paper_same_test_benchmarks/results/hi2022_halfimplicit_rows.csv",
                caveat=(
                    "bounded T=0.1 pilot; full T=8 2022 policy remains open; "
                    f"reference={erows[0].get('reference_policy', 'unknown')}"
                ),
            )
        add_missing_rows(
            rows,
            {(row["method"], row["example"]) for row in rows},
            f"{form}-hi2022",
            "Fang/Kissel/Zhang/Negrut 2022",
            "hi2022_halfimplicit",
            "not_run",
            "full 2022 source-policy row is open or not selected in the current bounded pilot",
        )

    for method in ("velocity_partitioning_2024", "TFE_m1", "TFE_m2", "TFE_m3"):
        add_missing_rows(
            rows,
            {(row["method"], row["example"]) for row in rows},
            method,
            "external source unresolved" if method == "velocity_partitioning_2024" else "original TFE paper",
            "vp2024_unresolved" if method == "velocity_partitioning_2024" else "tfe2026_pdf",
            "code_path_unresolved" if method == "velocity_partitioning_2024" else "not_encoded_for_four_asme_examples",
            "cannot claim four-example performance until source policy/code is encoded",
        )

    completed = sum(1 for row in rows if row["status"].startswith("completed"))
    partial = sum(1 for row in rows if row["status"].startswith("partial"))
    summary = {
        "schema": "four-example-method-performance-matrix-v1",
        "examples": list(EXAMPLES),
        "row_count": len(rows),
        "completed_row_count": completed,
        "partial_row_count": partial,
        "not_complete_row_count": len(rows) - completed - partial,
        "external_superiority_claim": False,
        "same_test_campaign_status": "not_run",
        "interpretation": (
            "This matrix is a coverage and performance ledger. It records completed and partial rows, "
            "but it does not claim external-method superiority until every required method/example cell "
            "uses the same source policy or a documented policy distinction."
        ),
    }
    return rows, summary


def write_markdown(rows: list[dict], summary: dict) -> None:
    lines = [
        "# Four-Example Method Performance Matrix",
        "",
        "Status: **coverage ledger, not a completed external superiority claim**",
        "",
        f"- Rows: `{summary['row_count']}`.",
        f"- Completed rows: `{summary['completed_row_count']}`.",
        f"- Partial rows: `{summary['partial_row_count']}`.",
        f"- Same-test campaign status: `{summary['same_test_campaign_status']}`.",
        f"- External superiority claim: `{summary['external_superiority_claim']}`.",
        "",
        "| Method | Example | Status | h values | Pos/order | Vel/order | Finest runtime | Evidence | Caveat |",
        "|---|---|---|---|---:|---:|---:|---|---|",
    ]
    for row in rows:
        lines.append(
            "| "
            f"`{row['method']}` | "
            f"`{row['example']}` | "
            f"`{row['status']}` | "
            f"`{row['h_values']}` | "
            f"{row['pos_order']} | "
            f"{row['vel_order']} | "
            f"{row['finest_runtime_sec']} | "
            f"`{row['evidence']}` | "
            f"{row['caveat']} |"
        )
    lines.extend(
        [
            "",
            "## Reading Rule",
            "",
            "A row is comparable only within its stated source suite and policy. The table",
            "does not merge the 2021 public `rA/rp/reps` policy, the 2022 half-implicit",
            "policy, the local v047 internal four-example gate, and unresolved 2024",
            "velocity-partitioning code into one claimed same-test result.",
            "",
        ]
    )
    (RESULTS / "four_example_performance_matrix.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    rows, summary = build_matrix()
    RESULTS.mkdir(parents=True, exist_ok=True)
    write_csv(RESULTS / "four_example_performance_matrix.csv", rows)
    with (RESULTS / "four_example_performance_summary.json").open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, sort_keys=True)
        handle.write("\n")
    write_markdown(rows, summary)
    print("four_example_performance_matrix=written")
    print(f"rows={summary['row_count']}")
    print(f"completed={summary['completed_row_count']}")
    print(f"partial={summary['partial_row_count']}")
    print("external_superiority_claim=False")


if __name__ == "__main__":
    main()
