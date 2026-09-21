#!/usr/bin/env python3
"""Build same-window public work/precision rows for true-dynamic Newton local rows."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import numpy as np

import run_v048 as rv


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
MODELS = ("four_link", "slider_crank")
PUBLIC_FORMS = ("rA", "rp", "reps")
STEP_SIZES = (0.1, 0.05, 0.025)
T_END = 0.1
REFERENCE_H = 0.0125
POLICY = "closed_loop_true_dynamic_newton_same_window_public_work_precision"
RAW_CSV = RESULTS / "closed_loop_true_dynamic_public_work_precision_rows.csv"
SUMMARY_CSV = RESULTS / "closed_loop_true_dynamic_public_work_precision_summary.csv"
SUMMARY_JSON = RESULTS / "closed_loop_true_dynamic_public_work_precision.json"
SUMMARY_MD = RESULTS / "closed_loop_true_dynamic_public_work_precision.md"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def read_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"refusing to write empty {path.name}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def as_float(value: object) -> float:
    try:
        out = float(value)
    except (TypeError, ValueError):
        return float("nan")
    return out if math.isfinite(out) else float("nan")


def fmt(value: object) -> str:
    number = as_float(value)
    return "nan" if not math.isfinite(number) else f"{number:.16e}"


def finite_sum(values: list[float]) -> float:
    clean = [value for value in values if math.isfinite(value)]
    return float(sum(clean)) if clean else float("nan")


def estimate_order_from_rows(rows: list[dict[str, object]], key: str) -> float:
    clean = sorted(
        [(as_float(row.get("h")), as_float(row.get(key))) for row in rows if row.get("status") == "ok"],
        reverse=True,
    )
    clean = [(h, e) for h, e in clean if h > 0.0 and e > 0.0 and math.isfinite(e)]
    if len(clean) < 2:
        return float("nan")
    slope, _ = np.polyfit(np.log([h for h, _ in clean]), np.log([e for _, e in clean]), 1)
    return float(slope)


def local_rows() -> list[dict[str, object]]:
    rows = read_csv(RESULTS / "closed_loop_true_dynamic_newton_coarse_order_rows.csv")
    out: list[dict[str, object]] = []
    for row in rows:
        if row.get("model") not in MODELS:
            continue
        out.append(
            {
                "policy": POLICY,
                "source_suite": "local_true_dynamic_newton",
                "case_id": f"{row['model']}_true_dynamic_newton_same_window",
                "model": row["model"],
                "method": "Gauss6/FullVA-local-true-dynamic-newton",
                "form": "local",
                "row_type": "same_window_public_work_precision_local_row",
                "t_end": fmt(row.get("t_end")),
                "reference_method": "v047_exact_kinematic_endpoint",
                "reference_h": fmt(REFERENCE_H),
                "h": fmt(row.get("h")),
                "status": row.get("status", "missing"),
                "steps": row.get("steps", "nan"),
                "pos_final_linf": fmt(row.get("endpoint_pos_error_inf")),
                "vel_final_linf": fmt(row.get("endpoint_vel_error_inf")),
                "acc_final_linf": fmt(row.get("endpoint_acc_error_inf")),
                "orientation_final_linf": fmt(row.get("endpoint_orientation_error_inf")),
                "omega_final_linf": fmt(row.get("endpoint_omega_error_inf")),
                "pos_observed_order": fmt(row.get("model_pos_observed_order")),
                "vel_observed_order": fmt(row.get("model_vel_observed_order")),
                "acc_observed_order": fmt(row.get("model_acc_observed_order")),
                "orientation_observed_order": fmt(row.get("model_orientation_observed_order")),
                "omega_observed_order": fmt(row.get("model_omega_observed_order")),
                "runtime_sec": fmt(row.get("runtime_sec")),
                "reference_runtime_sec": "nan",
                "avg_iterations_or_newton_per_step": fmt(
                    as_float(row.get("total_stage_newton_iterations")) / max(1.0, as_float(row.get("steps")))
                ),
                "max_iterations_or_newton": row.get("total_stage_newton_iterations", "nan"),
                "total_iterations_or_newton": row.get("total_stage_newton_iterations", "nan"),
                "stage_oracle_used": row.get("stage_oracle_used", "false"),
                "all_stages_converged": row.get("all_stages_converged", "false"),
                "reference_alignment": "local_exact_endpoint_not_public_kinematic_array",
                "accepted_dynamic_order": row.get("accepted_dynamic_order", "false"),
                "default_policy": "coarse_first_no_default_1e-4",
                "strict_public_policy_1e-4_required": "false",
                "default_1e-4_required": "false",
                "heavy_numerical_run_invoked": "false",
                "external_superiority_claim_allowed": "false",
                "notes": (
                    "Local true-dynamic Newton row at the same T and h values as the public rows. "
                    "Errors use the local exact endpoint reference; compare as a work/precision diagnostic "
                    "until a strict common-reference table is added."
                ),
            }
        )
    return out


def public_rows() -> list[dict[str, object]]:
    rv.switch_simengine_root(rv.SBEL_C2)
    rv.patch_modern_numpy_scalar_assignments()
    out: list[dict[str, object]] = []
    for model_name in MODELS:
        public_model = rv.RA2021_MODEL_BY_NAME[model_name]
        reference = rv.run_public_model(public_model, "rA", "kinematics", REFERENCE_H, T_END, tol=1.0e-12)
        reference_runtime = float(reference["runtime_sec"])
        for form in PUBLIC_FORMS:
            form_rows: list[dict[str, object]] = []
            for h in STEP_SIZES:
                row: dict[str, object] = {
                    "policy": POLICY,
                    "source_suite": "ra2021_taves_kissel_negrut",
                    "case_id": f"ra2021_{model_name}_{form}_same_window_public_work_precision",
                    "model": model_name,
                    "method": f"{form}-public-dynamics",
                    "form": form,
                    "row_type": "same_window_public_work_precision_public_row",
                    "t_end": fmt(T_END),
                    "reference_method": "rA-public-kinematics",
                    "reference_h": fmt(REFERENCE_H),
                    "h": fmt(h),
                    "status": "ok",
                    "steps": int(round(T_END / h)),
                    "pos_final_linf": "nan",
                    "vel_final_linf": "nan",
                    "acc_final_linf": "nan",
                    "orientation_final_linf": "nan",
                    "omega_final_linf": "nan",
                    "pos_observed_order": "nan",
                    "vel_observed_order": "nan",
                    "acc_observed_order": "nan",
                    "orientation_observed_order": "nan",
                    "omega_observed_order": "nan",
                    "runtime_sec": "nan",
                    "avg_iterations_or_newton_per_step": "nan",
                    "max_iterations_or_newton": "nan",
                    "total_iterations_or_newton": "nan",
                    "stage_oracle_used": "not_applicable",
                    "all_stages_converged": "not_applicable",
                    "reference_alignment": "public_rA_kinematic_array",
                    "accepted_dynamic_order": "false",
                    "default_policy": "coarse_first_no_default_1e-4",
                    "strict_public_policy_1e-4_required": "false",
                    "default_1e-4_required": "false",
                    "heavy_numerical_run_invoked": "false",
                    "external_superiority_claim_allowed": "false",
                    "notes": (
                        "Public 2021 dynamics row on the same coarse T and h values as the local true-dynamic "
                        "Newton rows. No source-policy 1e-4 row is run."
                    ),
                }
                try:
                    candidate = rv.run_public_model(public_model, form, "dynamics", h, T_END, tol=None)
                    pos_error = rv.final_error(reference, candidate, "pos")
                    vel_error = rv.final_error(reference, candidate, "vel")
                    acc_error = rv.final_error(reference, candidate, "acc")
                    row.update(
                        {
                            "pos_final_linf": fmt(pos_error),
                            "vel_final_linf": fmt(vel_error),
                            "acc_final_linf": fmt(acc_error),
                            "runtime_sec": fmt(candidate["runtime_sec"]),
                            "avg_iterations_or_newton_per_step": fmt(candidate["avg_iterations"]),
                            "max_iterations_or_newton": fmt(candidate["max_iterations"]),
                            "total_iterations_or_newton": fmt(float(np.sum(candidate["iters"]))),
                        }
                    )
                except Exception as exc:  # noqa: BLE001 - preserve public failures.
                    row["status"] = f"failed:{type(exc).__name__}:{str(exc).replace(chr(10), ' ')}"
                form_rows.append(row)
                out.append(row)
            orders = {
                "pos_observed_order": estimate_order_from_rows(form_rows, "pos_final_linf"),
                "vel_observed_order": estimate_order_from_rows(form_rows, "vel_final_linf"),
                "acc_observed_order": estimate_order_from_rows(form_rows, "acc_final_linf"),
            }
            for row in form_rows:
                for key, value in orders.items():
                    row[key] = fmt(value)
                row["reference_runtime_sec"] = fmt(reference_runtime)
    return out


def summarize_rows(rows: list[dict[str, object]]) -> tuple[list[dict[str, object]], dict]:
    grouped: dict[tuple[str, str], list[dict[str, object]]] = {}
    for row in rows:
        grouped.setdefault((str(row["model"]), str(row["method"])), []).append(row)

    public_ra_finest: dict[str, dict[str, object]] = {}
    for (model, method), group in grouped.items():
        if method == "rA-public-dynamics":
            ok = [row for row in group if row.get("status") == "ok"]
            if ok:
                public_ra_finest[model] = sorted(ok, key=lambda row: as_float(row.get("h")))[0]

    summary_rows: list[dict[str, object]] = []
    for (model, method), group in sorted(grouped.items()):
        ok = [row for row in group if row.get("status") == "ok"]
        sorted_ok = sorted(ok, key=lambda row: as_float(row.get("h")))
        finest = sorted_ok[0] if sorted_ok else {}
        baseline = public_ra_finest.get(model, {})

        def ratio(key: str) -> str:
            numerator = as_float(finest.get(key))
            denominator = as_float(baseline.get(key))
            if not math.isfinite(numerator) or not math.isfinite(denominator) or denominator == 0.0:
                return "nan"
            return fmt(numerator / denominator)

        runtime_values = [as_float(row.get("runtime_sec")) for row in ok]
        iteration_values = [as_float(row.get("total_iterations_or_newton")) for row in ok]
        summary_rows.append(
            {
                "policy": f"{POLICY}_summary",
                "source_suite": finest.get("source_suite", "missing"),
                "case_id": f"{model}_{method}_same_window_public_work_precision_summary",
                "model": model,
                "method": method,
                "row_count": len(group),
                "ok_row_count": len(ok),
                "t_end": fmt(finest.get("t_end")),
                "reference_method": finest.get("reference_method", "missing"),
                "reference_h": fmt(finest.get("reference_h")),
                "finest_h": fmt(finest.get("h")),
                "pos_observed_order": fmt(finest.get("pos_observed_order")),
                "vel_observed_order": fmt(finest.get("vel_observed_order")),
                "acc_observed_order": fmt(finest.get("acc_observed_order")),
                "orientation_observed_order": fmt(finest.get("orientation_observed_order")),
                "omega_observed_order": fmt(finest.get("omega_observed_order")),
                "finest_pos_final_linf": fmt(finest.get("pos_final_linf")),
                "finest_vel_final_linf": fmt(finest.get("vel_final_linf")),
                "finest_acc_final_linf": fmt(finest.get("acc_final_linf")),
                "finest_runtime_sec": fmt(finest.get("runtime_sec")),
                "runtime_sec_sum": fmt(finite_sum(runtime_values)),
                "total_iterations_or_newton_sum": fmt(finite_sum(iteration_values)),
                "finest_pos_error_ratio_vs_public_rA": ratio("pos_final_linf"),
                "finest_vel_error_ratio_vs_public_rA": ratio("vel_final_linf"),
                "finest_acc_error_ratio_vs_public_rA": ratio("acc_final_linf"),
                "finest_runtime_ratio_vs_public_rA": ratio("runtime_sec"),
                "reference_alignment": finest.get("reference_alignment", "missing"),
                "accepted_dynamic_order": finest.get("accepted_dynamic_order", "false"),
                "external_superiority_claim_allowed": "false",
                "notes": (
                    "Same-window coarse work/precision summary. Public rows use the public rA kinematic "
                    "reference; local rows use the local exact endpoint reference, so this closes the public "
                    "work/precision availability gap but not a strict common-reference superiority claim."
                ),
            }
        )

    public_complete_models = []
    for model in MODELS:
        model_public = [
            row
            for row in summary_rows
            if row["model"] == model and str(row["method"]).endswith("-public-dynamics")
        ]
        if len(model_public) == len(PUBLIC_FORMS) and all(int(row["ok_row_count"]) == len(STEP_SIZES) for row in model_public):
            public_complete_models.append(model)

    local_complete_models = []
    for model in MODELS:
        local = [
            row
            for row in summary_rows
            if row["model"] == model and row["method"] == "Gauss6/FullVA-local-true-dynamic-newton"
        ]
        if local and int(local[0]["ok_row_count"]) == len(STEP_SIZES) and local[0]["accepted_dynamic_order"] == "true":
            local_complete_models.append(model)

    summary = {
        "schema": "closed-loop-true-dynamic-public-work-precision-v1",
        "status": "same_window_public_work_precision_available_reference_caveat_not_external_superiority",
        "policy": POLICY,
        "default_policy": "coarse_first_no_default_1e-4",
        "models": list(MODELS),
        "public_forms": list(PUBLIC_FORMS),
        "step_sizes": list(STEP_SIZES),
        "t_end": T_END,
        "reference_h": REFERENCE_H,
        "row_count": len(rows),
        "ok_row_count": sum(1 for row in rows if row.get("status") == "ok"),
        "public_raw_row_count": sum(1 for row in rows if str(row.get("method", "")).endswith("-public-dynamics")),
        "local_raw_row_count": sum(1 for row in rows if row.get("method") == "Gauss6/FullVA-local-true-dynamic-newton"),
        "summary_row_count": len(summary_rows),
        "public_work_precision_available_count": len(public_complete_models),
        "public_work_precision_available_examples": public_complete_models,
        "public_work_precision_missing_count": len(MODELS) - len(public_complete_models),
        "local_true_dynamic_order_available_count": len(local_complete_models),
        "strict_common_reference_error_columns": False,
        "reference_alignment_status": "mixed_reference_family_requires_manuscript_caveat",
        "accepted_external_dynamic_order_examples": [],
        "external_superiority_claim": False,
        "default_1e-4_required": False,
        "strict_public_policy_1e-4_required": False,
        "heavy_numerical_run_invoked": False,
        "interpretation": (
            "This artifact adds the missing same-window public work/precision rows for the two closed-loop "
            "models at T=0.1 and h=0.1|0.05|0.025. It is not an external superiority claim because the "
            "local and public error columns still use different reference families."
        ),
    }
    return summary_rows, summary


def write_markdown(summary: dict, summary_rows: list[dict[str, object]]) -> None:
    lines = [
        "# Closed-Loop True-Dynamic Public Work/Precision",
        "",
        f"Status: **{summary['status'].replace('_', ' ')}**",
        "",
        f"- Rows: `{summary['ok_row_count']}/{summary['row_count']}` ok.",
        f"- Public work/precision examples available: `{summary['public_work_precision_available_count']}`.",
        f"- Public work/precision examples missing: `{summary['public_work_precision_missing_count']}`.",
        f"- Strict common-reference error columns: `{summary['strict_common_reference_error_columns']}`.",
        f"- Default `1e-4` required: `{summary['default_1e-4_required']}`.",
        f"- External superiority claim: `{summary['external_superiority_claim']}`.",
        "",
        "This table aligns the public 2021 closed-loop dynamics rows with the local",
        "true-dynamic Newton rows in model, time window, and step sizes. It still",
        "keeps a reference-family caveat: public errors are measured against the",
        "public `rA` kinematic reference, while local errors are the already accepted",
        "local exact-endpoint errors.",
        "",
        "| Model | Method | ok | pos order | vel order | acc order | finest pos | finest vel | runtime sum | runtime ratio vs rA |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in summary_rows:
        lines.append(
            "| "
            f"`{row['model']}` | `{row['method']}` | `{row['ok_row_count']}/{row['row_count']}` | "
            f"`{row['pos_observed_order']}` | `{row['vel_observed_order']}` | `{row['acc_observed_order']}` | "
            f"`{row['finest_pos_final_linf']}` | `{row['finest_vel_final_linf']}` | "
            f"`{row['runtime_sec_sum']}` | `{row['finest_runtime_ratio_vs_public_rA']}` |"
        )
    SUMMARY_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    rows = local_rows() + public_rows()
    summary_rows, summary = summarize_rows(rows)
    write_csv(RAW_CSV, rows)
    write_csv(SUMMARY_CSV, summary_rows)
    with SUMMARY_JSON.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, sort_keys=True)
        handle.write("\n")
    write_markdown(summary, summary_rows)
    print("closed_loop_true_dynamic_public_work_precision=written")
    print(f"rows_ok={summary['ok_row_count']}/{summary['row_count']}")
    print(f"public_work_precision_available={summary['public_work_precision_available_count']}/2")
    print(f"public_work_precision_missing={summary['public_work_precision_missing_count']}")
    print("strict_common_reference_error_columns=False")
    print("default_1e-4=False")
    print("external_superiority_claim=False")


if __name__ == "__main__":
    main()
