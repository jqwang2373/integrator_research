#!/usr/bin/env python3
"""Compute direct common-reference errors for the runnable coarse baselines.

The main coarse matrix intentionally preserves each source suite's native
reference policy.  This audit is stricter: for every accepted runnable method,
the candidate final state is compared against the same per-example reference and
norm as the local row.
"""

from __future__ import annotations

import csv
import importlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

import build_closed_loop_true_dynamic_newton_coarse_order as closed_loop_local
import closed_loop_fullva_dynamic_residual as dynres
import run_coarse_four_example_order as coarse
import run_v048 as rv


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
OUT_RAW = RESULTS / "common_reference_error_raw_rows.csv"
OUT_SUMMARY = RESULTS / "common_reference_error_summary.csv"
OUT_JSON = RESULTS / "common_reference_error_summary.json"
OUT_MD = RESULTS / "common_reference_error_summary.md"

STEP_SIZES = (0.1, 0.05, 0.025)
REFERENCE_H = 0.0125
T_END = 0.1
EXAMPLES = ("single_pendulum", "double_pendulum", "four_link", "slider_crank")
LOCAL = "local_Gauss6_FullVA"

METHODS = (
    ("local proposed method", LOCAL),
    ("Kissel/Taves/Negrut 2021", "ra2021_rA"),
    ("Kissel/Taves/Negrut 2021", "ra2021_rp"),
    ("Kissel/Taves/Negrut 2021", "ra2021_reps"),
    ("Fang/Kissel/Zhang/Negrut 2022", "hi2022_rA"),
    ("Fang/Kissel/Zhang/Negrut 2022", "hi2022_rA_half"),
    ("original TFE paper", "tfe2026_Newmark_beta"),
    ("original TFE paper", "tfe2026_trapezoidal"),
    ("original TFE paper", "tfe2026_TFE_m1"),
    ("original TFE paper", "tfe2026_TFE_m2"),
    ("Kissel/Bakke/Negrut 2024", "vp2024_coordinate_partitioning_rA"),
)

OMITTED_METHODS = {
    "tfe2026_TFE_m3_GL": "source_backed_scope_excluded_four_link",
}

ALIAS_METHODS = {
    "vp2024_lie_group_ode_partitioning": "vp2024_coordinate_partitioning_rA",
}


def as_float(value: object) -> float:
    try:
        out = float(value)
    except (TypeError, ValueError):
        return float("nan")
    return out if math.isfinite(out) else float("nan")


def fmt(value: object) -> str:
    number = as_float(value)
    return "nan" if not math.isfinite(number) else f"{number:.16e}"


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"refusing to write empty {path.name}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def estimate_order(rows: list[dict[str, object]], key: str) -> float:
    pairs = [
        (as_float(row["h"]), as_float(row[key]))
        for row in rows
        if row.get("status") == "ok" and as_float(row["h"]) > 0.0 and as_float(row[key]) > 0.0
    ]
    pairs.sort(reverse=True)
    if len(pairs) < 3:
        return float("nan")
    slope, _ = np.polyfit(np.log([h for h, _ in pairs]), np.log([err for _, err in pairs]), 1)
    return float(slope)


def final_norm(example: str, candidate: np.ndarray, reference: np.ndarray) -> float:
    diff = np.asarray(candidate, dtype=float) - np.asarray(reference, dtype=float)
    if example == "single_pendulum":
        return float(np.linalg.norm(diff.reshape(-1)))
    return float(np.max(np.abs(diff)))


def final_errors_from_arrays(example: str, candidate: dict[str, Any], reference: dict[str, Any]) -> dict[str, float]:
    pos = np.asarray(candidate["pos"], dtype=float)[:, :, -1]
    vel = np.asarray(candidate["vel"], dtype=float)[:, :, -1]
    errors = {
        "pos": final_norm(example, pos, np.asarray(reference["pos"], dtype=float)),
        "vel": final_norm(example, vel, np.asarray(reference["vel"], dtype=float)),
        "acc": float("nan"),
    }
    if "acc" in candidate and reference.get("acc") is not None:
        acc = np.asarray(candidate["acc"], dtype=float)[:, :, -1]
        errors["acc"] = final_norm(example, acc, np.asarray(reference["acc"], dtype=float))
    return errors


def run_public_fixed_grid_model(
    *,
    model_name: str,
    module_name: str,
    form: str,
    mode: str,
    h: float,
    t_end: float,
    tol: float | None,
    arg_time_flag: str,
) -> dict[str, Any]:
    """Replay a public model on the actual coarse grid t_i=i*h.

    The public example functions allocate ``t_steps=int(T/h)`` and then use
    ``linspace(0,T,t_steps)``.  That convention is almost invisible for the
    source paper's small h rows, but it is not an apples-to-apples coarse-grid
    final-state comparison.  This replay keeps the source setup and stepper but
    records states on ``0,h,...,T``.
    """

    module = importlib.import_module(module_name)
    setup = getattr(module, f"setup_{model_name}")
    args = [
        "--form",
        form,
        "--mode",
        mode,
        "--step_size",
        str(h),
        arg_time_flag,
        str(t_end),
        "--log",
        "warning",
        "--no-plot",
    ]
    if tol is not None:
        args.extend(["--tol", str(tol)])
    system, params = setup(args)
    system.initialize()
    steps = int(round(params.t_end / params.h))
    if abs(steps * params.h - params.t_end) > 1.0e-12:
        raise ValueError(f"h={params.h} does not divide t_end={params.t_end}")
    t_grid = np.linspace(0.0, params.t_end, steps + 1, endpoint=True)
    pos_data = np.zeros((system.nb, 3, steps + 1))
    vel_data = np.zeros((system.nb, 3, steps + 1))
    acc_data = np.zeros((system.nb, 3, steps + 1))
    num_iters = np.zeros(steps + 1)
    for i, t in enumerate(t_grid):
        system.do_step(i, t)
        num_iters[i] = system.k
        for j, body in enumerate(system.bodies):
            pos_data[j, :, i] = np.asarray(body.r).reshape(3)
            vel_data[j, :, i] = np.asarray(body.dr).reshape(3)
            acc_data[j, :, i] = np.asarray(body.ddr).reshape(3)
    return {"pos": pos_data, "vel": vel_data, "acc": acc_data, "iters": num_iters, "t_grid": t_grid}


class ReferenceBundle:
    def __init__(self) -> None:
        self.v047 = rv.import_v047_single_fullva_module()
        self.v029 = self.v047.load_v029()
        self.double_params = self.v047.make_asme_double_pendulum_params(self.v029)
        self.closed_v047 = closed_loop_local.import_v047_module()
        self.v046 = self.closed_v047.load_v046()
        self.v046.patch_modern_numpy_scalar_assignments()
        self.closed_models = {model.name: model for model in self.v046.MODELS}
        self.references = self._build_references()

    def _build_references(self) -> dict[str, dict[str, Any]]:
        single = self.v047.asme_single_state_from_time(T_END)
        double = self.v047.integrate_v029_asme_double_trajectory(
            self.v029,
            "double_revolute_gauss6_fullva",
            REFERENCE_H,
            T_END,
            self.double_params,
        )
        refs: dict[str, dict[str, Any]] = {
            "single_pendulum": {
                "pos": np.asarray(single["r"], dtype=float).reshape(1, 3),
                "vel": np.asarray(single["v"], dtype=float).reshape(1, 3),
                "acc": np.asarray(single["a"], dtype=float).reshape(1, 3),
                "reference_policy": "analytic_exact_single_pendulum",
                "norm": "final_l2",
            },
            "double_pendulum": {
                "pos": np.asarray(double["pos"], dtype=float)[:, :, -1],
                "vel": np.asarray(double["vel"], dtype=float)[:, :, -1],
                "acc": None,
                "reference_policy": "local_fullva_h_0.0125_final_state",
                "norm": "final_linf",
            },
        }
        for example in ("four_link", "slider_crank"):
            system = closed_loop_local.setup_exact_system(
                self.closed_v047,
                self.v046,
                self.closed_models[example],
                REFERENCE_H,
                T_END,
            )
            endpoint = dynres.endpoint_state_from_system(system)
            nb = len(endpoint["r"]) // 3
            refs[example] = {
                "pos": np.asarray(endpoint["r"], dtype=float).reshape(nb, 3),
                "vel": np.asarray(endpoint["dr"], dtype=float).reshape(nb, 3),
                "acc": np.asarray(endpoint["ddr"], dtype=float).reshape(nb, 3),
                "reference_policy": "v047_exact_closed_loop_endpoint_h_0.0125",
                "norm": "final_linf",
            }
        return refs


def raw_row(
    *,
    family: str,
    method: str,
    example: str,
    h: object,
    status: str,
    reference_policy: str,
    error_norm: str,
    pos_error: object = "nan",
    vel_error: object = "nan",
    acc_error: object = "nan",
    evidence: str,
    notes: str,
) -> dict[str, object]:
    return {
        "family": family,
        "method": method,
        "example": example,
        "h": fmt(h),
        "t_end": fmt(T_END),
        "reference_h": fmt(REFERENCE_H),
        "reference_policy": reference_policy,
        "error_norm": error_norm,
        "status": status,
        "pos_error": fmt(pos_error),
        "vel_error": fmt(vel_error),
        "acc_error": fmt(acc_error),
        "evidence": evidence,
        "notes": notes,
    }


def run_local_row(bundle: ReferenceBundle, family: str, example: str, h: float) -> dict[str, object]:
    reference = bundle.references[example]
    try:
        if example == "single_pendulum":
            out = bundle.v047.integrate_asme_single_driven_absolute_fullva(h, T_END, False)
            return raw_row(
                family=family,
                method=LOCAL,
                example=example,
                h=h,
                status="ok",
                reference_policy=reference["reference_policy"],
                error_norm=reference["norm"],
                pos_error=out["position_l2_error"],
                vel_error=out["velocity_l2_error"],
                evidence="v047.integrate_asme_single_driven_absolute_fullva",
                notes="local single-pendulum row against analytic exact final state",
            )
        if example == "double_pendulum":
            candidate = bundle.v047.integrate_v029_asme_double_trajectory(
                bundle.v029,
                "double_revolute_gauss6_fullva",
                h,
                T_END,
                bundle.double_params,
            )
            errors = final_errors_from_arrays(example, candidate, reference)
            return raw_row(
                family=family,
                method=LOCAL,
                example=example,
                h=h,
                status="ok",
                reference_policy=reference["reference_policy"],
                error_norm=reference["norm"],
                pos_error=errors["pos"],
                vel_error=errors["vel"],
                evidence="v047.integrate_v029_asme_double_trajectory",
                notes="local double-pendulum row against the shared local FullVA h=0.0125 final reference",
            )
        local_reference = {
            "r": reference["pos"].reshape(-1),
            "dr": reference["vel"].reshape(-1),
            "ddr": reference["acc"].reshape(-1),
            "omega": np.zeros(3 * reference["pos"].shape[0]),
            "domega": np.zeros(3 * reference["pos"].shape[0]),
            "A": np.zeros((reference["pos"].shape[0], 3, 3)),
        }
        system = closed_loop_local.setup_exact_system(
            bundle.closed_v047,
            bundle.v046,
            bundle.closed_models[example],
            REFERENCE_H,
            T_END,
        )
        endpoint = dynres.endpoint_state_from_system(system)
        local_reference.update(
            {
                "omega": endpoint["omega"],
                "domega": endpoint["domega"],
                "A": endpoint["A"],
            }
        )
        row = closed_loop_local.simulate_model_h(
            bundle.closed_v047,
            bundle.v046,
            bundle.closed_models[example],
            h,
            local_reference,
        )
        status = "ok" if row.get("status") == "ok" else str(row.get("status"))
        return raw_row(
            family=family,
            method=LOCAL,
            example=example,
            h=h,
            status=status,
            reference_policy=reference["reference_policy"],
            error_norm=reference["norm"],
            pos_error=row.get("endpoint_pos_error_inf"),
            vel_error=row.get("endpoint_vel_error_inf"),
            acc_error=row.get("endpoint_acc_error_inf"),
            evidence="build_closed_loop_true_dynamic_newton_coarse_order.simulate_model_h",
            notes="local closed-loop true-dynamic Newton row against the shared exact endpoint reference",
        )
    except Exception as exc:  # noqa: BLE001 - keep audit row visible.
        return raw_row(
            family=family,
            method=LOCAL,
            example=example,
            h=h,
            status=f"failed:{type(exc).__name__}:{str(exc).replace(chr(10), ' ')}",
            reference_policy=reference["reference_policy"],
            error_norm=reference["norm"],
            evidence="local common-reference runner",
            notes="local candidate failed in common-reference audit",
        )


def run_public_ra2021_candidate(method: str, example: str, h: float) -> dict[str, Any]:
    rv.switch_simengine_root(rv.SBEL_C2)
    rv.patch_modern_numpy_scalar_assignments()
    form = method.removeprefix("ra2021_")
    model = coarse.ra2021_public_model_for_example(example)
    return run_public_fixed_grid_model(
        model_name=model.name,
        module_name=model.module,
        form=form,
        mode="dynamics",
        h=h,
        t_end=T_END,
        tol=None,
        arg_time_flag="--end_time",
    )


def run_hi2022_candidate(method: str, example: str, h: float) -> dict[str, Any]:
    rv.switch_simengine_root(rv.HI2022_ROOT)
    rv.patch_hi2022_modern_numpy_scalar_assignments()
    form = method.removeprefix("hi2022_")
    tolerance = rv.hi2022_tolerance(form, h, rv.HI2022_TOLERANCE_BASE)
    return run_public_fixed_grid_model(
        model_name=example,
        module_name=f"SimEngineMBD.example_models.{example}",
        form=form,
        mode="dynamics",
        h=h,
        t_end=T_END,
        tol=tolerance,
        arg_time_flag="-t",
    )


def run_tfe_candidate(method: str, example: str, h: float) -> dict[str, Any]:
    if method == "tfe2026_Newmark_beta":
        return coarse.run_ra2021_newmark_family_model(
            example=example,
            h=h,
            t_end=T_END,
            gamma=coarse.TFE2026_NEWMARK_GAMMA,
            beta=coarse.TFE2026_NEWMARK_BETA,
        )
    if method == "tfe2026_trapezoidal":
        return coarse.run_ra2021_newmark_family_model(
            example=example,
            h=h,
            t_end=T_END,
            gamma=coarse.TFE2026_TRAPEZOIDAL_GAMMA,
            beta=coarse.TFE2026_TRAPEZOIDAL_BETA,
        )
    if method == "tfe2026_TFE_m1":
        return coarse.run_ra2021_tfe_m1_model(
            example=example,
            h=h,
            t_end=T_END,
            nu=coarse.TFE2026_TFE_M1_NU,
        )
    if method == "tfe2026_TFE_m2":
        return coarse.run_ra2021_tfe_multinode_model(
            example=example,
            h=h,
            t_end=T_END,
            m=2,
            nu=coarse.TFE2026_TFE_M2_NU,
        )
    raise ValueError(f"unsupported TFE method {method}")


def run_nonlocal_row(bundle: ReferenceBundle, family: str, method: str, example: str, h: float) -> dict[str, object]:
    reference = bundle.references[example]
    try:
        if method.startswith("ra2021_"):
            candidate = run_public_ra2021_candidate(method, example, h)
        elif method.startswith("hi2022_"):
            candidate = run_hi2022_candidate(method, example, h)
        elif method.startswith("tfe2026_"):
            candidate = run_tfe_candidate(method, example, h)
        elif method == "vp2024_coordinate_partitioning_rA":
            candidate = coarse.run_vp2024_coordinate_partitioning_model(example=example, h=h, t_end=T_END)
        else:
            raise ValueError(f"unsupported method {method}")
        errors = final_errors_from_arrays(example, candidate, reference)
        replay_note = (
            "candidate final state compared against the same reference/norm as the local method"
        )
        evidence = "common-reference final-state replay"
        if method.startswith(("ra2021_", "hi2022_")):
            replay_note = (
                "candidate final state compared against the same reference/norm as the local method; "
                "public-code source setup and stepper are retained, but the coarse replay uses fixed "
                "times t_i=i*h because the source run_* helpers use linspace(0,T,int(T/h))"
            )
            evidence = "common-reference fixed-grid final-state replay"
        return raw_row(
            family=family,
            method=method,
            example=example,
            h=h,
            status="ok",
            reference_policy=reference["reference_policy"],
            error_norm=reference["norm"],
            pos_error=errors["pos"],
            vel_error=errors["vel"],
            acc_error=errors["acc"],
            evidence=evidence,
            notes=replay_note,
        )
    except Exception as exc:  # noqa: BLE001 - keep audit row visible.
        return raw_row(
            family=family,
            method=method,
            example=example,
            h=h,
            status=f"failed:{type(exc).__name__}:{str(exc).replace(chr(10), ' ')}",
            reference_policy=reference["reference_policy"],
            error_norm=reference["norm"],
            evidence="common-reference final-state replay",
            notes="candidate failed in direct common-reference audit",
        )


def summarize(raw_rows: list[dict[str, object]]) -> tuple[list[dict[str, object]], dict[str, object]]:
    summary_rows: list[dict[str, object]] = []
    grouped: dict[tuple[str, str], list[dict[str, object]]] = {}
    for row in raw_rows:
        grouped.setdefault((str(row["method"]), str(row["example"])), []).append(row)

    for (method, example), rows in sorted(grouped.items()):
        ok_rows = [row for row in rows if row["status"] == "ok"]
        finest = min(ok_rows, key=lambda row: as_float(row["h"])) if ok_rows else rows[0]
        summary_rows.append(
            {
                "family": finest["family"],
                "method": method,
                "example": example,
                "status": "ok" if len(ok_rows) == len(STEP_SIZES) else str(finest["status"]),
                "ok_count": len(ok_rows),
                "row_count": len(rows),
                "h_values": "|".join(fmt(row["h"]) for row in sorted(ok_rows, key=lambda item: as_float(item["h"]), reverse=True)),
                "t_end": fmt(T_END),
                "reference_h": fmt(REFERENCE_H),
                "reference_policy": finest["reference_policy"],
                "error_norm": finest["error_norm"],
                "pos_order": fmt(estimate_order(ok_rows, "pos_error")),
                "vel_order": fmt(estimate_order(ok_rows, "vel_error")),
                "acc_order": fmt(estimate_order(ok_rows, "acc_error")),
                "finest_pos_error": fmt(finest.get("pos_error")),
                "finest_vel_error": fmt(finest.get("vel_error")),
                "finest_acc_error": fmt(finest.get("acc_error")),
                "vel_error_ratio_vs_local": "nan",
                "local_finest_vel_error_win": "nan",
                "local_vel_order_win": "nan",
                "notes": finest["notes"],
            }
        )

    by_key = {(row["method"], row["example"]): row for row in summary_rows}
    local_order_wins = 0
    local_error_wins = 0
    comparable_order_rows = 0
    comparable_error_rows = 0
    original_paper_error_wins = 0
    original_paper_comparable = 0
    kissel_negrut_error_wins = 0
    kissel_negrut_comparable = 0
    for row in summary_rows:
        if row["method"] == LOCAL or row["status"] != "ok":
            continue
        local = by_key.get((LOCAL, row["example"]))
        if not local or local["status"] != "ok":
            continue
        local_vel_order = as_float(local["vel_order"])
        method_vel_order = as_float(row["vel_order"])
        if math.isfinite(local_vel_order) and math.isfinite(method_vel_order):
            comparable_order_rows += 1
            order_win = local_vel_order > method_vel_order
            local_order_wins += int(order_win)
            row["local_vel_order_win"] = str(order_win).lower()
        local_vel_error = as_float(local["finest_vel_error"])
        method_vel_error = as_float(row["finest_vel_error"])
        if math.isfinite(local_vel_error) and math.isfinite(method_vel_error) and local_vel_error > 0.0:
            comparable_error_rows += 1
            error_win = local_vel_error < method_vel_error
            local_error_wins += int(error_win)
            row["vel_error_ratio_vs_local"] = fmt(method_vel_error / local_vel_error)
            row["local_finest_vel_error_win"] = str(error_win).lower()
            if row["family"] == "original TFE paper":
                original_paper_comparable += 1
                original_paper_error_wins += int(error_win)
            if "Kissel" in str(row["family"]) or "Negrut" in str(row["family"]):
                kissel_negrut_comparable += 1
                kissel_negrut_error_wins += int(error_win)

    summary = {
        "schema": "common-reference-error-audit-v1",
        "step_sizes": list(STEP_SIZES),
        "reference_h": REFERENCE_H,
        "t_end": T_END,
        "examples": list(EXAMPLES),
        "run_method_count": len(METHODS),
        "omitted_methods": OMITTED_METHODS,
        "alias_methods": ALIAS_METHODS,
        "raw_row_count": len(raw_rows),
        "summary_row_count": len(summary_rows),
        "direct_error_comparable_rows": comparable_error_rows,
        "local_velocity_order_wins": local_order_wins,
        "local_velocity_order_comparisons": comparable_order_rows,
        "local_finest_velocity_error_wins": local_error_wins,
        "local_finest_velocity_error_comparisons": comparable_error_rows,
        "original_paper_velocity_error_wins": original_paper_error_wins,
        "original_paper_velocity_error_comparisons": original_paper_comparable,
        "kissel_negrut_velocity_error_wins": kissel_negrut_error_wins,
        "kissel_negrut_velocity_error_comparisons": kissel_negrut_comparable,
        "direct_error_superiority_claim": (
            comparable_error_rows > 0 and local_error_wins == comparable_error_rows
        ),
        "apples_to_apples_coarse_claim": (
            comparable_error_rows > 0 and local_error_wins == comparable_error_rows
        ),
        "source_policy_reproduction": False,
        "public_code_fixed_grid_replay": True,
        "public_source_run_helpers_time_grid_caveat": (
            "The 2021/2022 public run_* helpers allocate int(T/h) samples with "
            "linspace(0,T,int(T/h)); the common-reference audit uses the same setup "
            "and steppers but replays coarse rows on t_i=i*h."
        ),
        "claim": (
            "These rows are direct final-state error comparisons under one shared reference "
            "and norm per example on the coarse h grid. Public-code baselines are replayed "
            "on fixed times t_i=i*h to avoid the source helper time-grid convention at coarse h. "
            "This is an apples-to-apples coarse comparison, not source-policy reproduction."
        ),
    }
    return summary_rows, summary


def write_markdown(summary_rows: list[dict[str, object]], summary: dict[str, object]) -> None:
    lines = [
        "# Common-Reference Error Audit",
        "",
        f"Step sizes: `{summary['step_sizes']}`; reference h: `{summary['reference_h']}`; t_end: `{summary['t_end']}`.",
        f"Runnable methods audited: `{summary['run_method_count']}`.",
        f"Omitted methods: `{json.dumps(summary['omitted_methods'], sort_keys=True)}`.",
        f"Alias methods: `{json.dumps(summary['alias_methods'], sort_keys=True)}`.",
        "",
        f"Local velocity-order wins: `{summary['local_velocity_order_wins']}/{summary['local_velocity_order_comparisons']}`.",
        f"Local finest-velocity-error wins: `{summary['local_finest_velocity_error_wins']}/{summary['local_finest_velocity_error_comparisons']}`.",
        f"Original-paper finest-velocity-error wins: `{summary['original_paper_velocity_error_wins']}/{summary['original_paper_velocity_error_comparisons']}`.",
        f"Kissel/Negrut-family finest-velocity-error wins: `{summary['kissel_negrut_velocity_error_wins']}/{summary['kissel_negrut_velocity_error_comparisons']}`.",
        f"Direct all-row error superiority claim: `{summary['direct_error_superiority_claim']}`.",
        f"Apples-to-apples coarse claim: `{summary['apples_to_apples_coarse_claim']}`.",
        f"Source-policy reproduction: `{summary['source_policy_reproduction']}`.",
        f"Public-code fixed-grid replay: `{summary['public_code_fixed_grid_replay']}`.",
        "",
        "| Example | Method | status | norm | vel order | finest vel error | ratio vs local | local error win | local order win |",
        "|---|---|---:|---|---:|---:|---:|---:|---:|",
    ]
    for row in summary_rows:
        lines.append(
            "| "
            f"`{row['example']}` | `{row['method']}` | `{row['status']}` | `{row['error_norm']}` | "
            f"`{row['vel_order']}` | `{row['finest_vel_error']}` | `{row['vel_error_ratio_vs_local']}` | "
            f"`{row['local_finest_vel_error_win']}` | `{row['local_vel_order_win']}` |"
        )
    lines.extend(["", str(summary["claim"])])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    bundle = ReferenceBundle()
    raw_rows: list[dict[str, object]] = []
    for family, method in METHODS:
        for example in EXAMPLES:
            for h in STEP_SIZES:
                if method == LOCAL:
                    raw_rows.append(run_local_row(bundle, family, example, h))
                else:
                    raw_rows.append(run_nonlocal_row(bundle, family, method, example, h))
    summary_rows, summary = summarize(raw_rows)
    write_csv(OUT_RAW, raw_rows)
    write_csv(OUT_SUMMARY, summary_rows)
    with OUT_JSON.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, sort_keys=True)
        handle.write("\n")
    write_markdown(summary_rows, summary)
    print("common_reference_error_audit=written")
    print(f"direct_error_comparable_rows={summary['direct_error_comparable_rows']}")
    print(
        "local_finest_velocity_error_wins="
        f"{summary['local_finest_velocity_error_wins']}/{summary['local_finest_velocity_error_comparisons']}"
    )
    print(
        "local_velocity_order_wins="
        f"{summary['local_velocity_order_wins']}/{summary['local_velocity_order_comparisons']}"
    )


if __name__ == "__main__":
    main()
