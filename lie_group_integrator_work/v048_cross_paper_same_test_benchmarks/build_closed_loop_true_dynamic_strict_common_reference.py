#!/usr/bin/env python3
"""Build strict common-reference rows for closed-loop true-dynamic comparisons."""

from __future__ import annotations

import csv
import importlib.util
import json
import math
import sys
import time
from pathlib import Path

import numpy as np

import closed_loop_fullva_dynamic_residual as dynres
import run_v048 as rv


HERE = Path(__file__).resolve().parent
WORK_ROOT = HERE.parent
RESULTS = HERE / "results"
V047_RUN = WORK_ROOT / "v047_cylindrical_chain_pipeline" / "run_v047.py"
MODELS = ("four_link", "slider_crank")
PUBLIC_FORMS = ("rA", "rp", "reps")
STEP_SIZES = (0.1, 0.05, 0.025)
T_END = 0.1
REFERENCE_H = 0.0125
POLICY = "closed_loop_true_dynamic_strict_common_reference"
RAW_CSV = RESULTS / "closed_loop_true_dynamic_strict_common_reference_rows.csv"
SUMMARY_CSV = RESULTS / "closed_loop_true_dynamic_strict_common_reference_summary.csv"
SUMMARY_JSON = RESULTS / "closed_loop_true_dynamic_strict_common_reference.json"
SUMMARY_MD = RESULTS / "closed_loop_true_dynamic_strict_common_reference.md"
FIGURE = RESULTS / "closed_loop_true_dynamic_strict_common_reference_work_precision.png"


def import_v047_module():
    module_name = "v047_cylindrical_chain_pipeline_run_v047_for_strict_common_reference"
    if module_name in sys.modules:
        return sys.modules[module_name]
    spec = importlib.util.spec_from_file_location(module_name, V047_RUN)
    if spec is None or spec.loader is None:
        raise ImportError(f"could not load {V047_RUN}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


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


def estimate_order(rows: list[dict[str, object]], key: str) -> float:
    clean = sorted(
        [(as_float(row.get("h")), as_float(row.get(key))) for row in rows if row.get("status") == "ok"],
        reverse=True,
    )
    clean = [(h, e) for h, e in clean if h > 0.0 and e > 0.0 and math.isfinite(e)]
    if len(clean) < 2:
        return float("nan")
    slope, _ = np.polyfit(np.log([h for h, _ in clean]), np.log([e for _, e in clean]), 1)
    return float(slope)


def setup_exact_system(v047_module, v046, model, h: float, t: float):
    system, _params = v046.setup_system(model, "dynamics", h, T_END, 1.0e-12)
    system.initialize()
    v047_module.project_v046_system_to_so3(system)
    v047_module.solve_v046_local_kinematic_fullva_time(system, t, 1.0e-12)
    return system


def public_like_endpoint(reference: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    nb = int(reference["r"].size // 3)
    return {
        "pos": np.asarray(reference["r"], dtype=float).reshape(nb, 3),
        "vel": np.asarray(reference["dr"], dtype=float).reshape(nb, 3),
        "acc": np.asarray(reference["ddr"], dtype=float).reshape(nb, 3),
    }


def final_error_to_reference(candidate: dict[str, np.ndarray], reference: dict[str, np.ndarray], key: str) -> float:
    cand = np.asarray(candidate[key], dtype=float)[:, :, -1]
    ref = np.asarray(reference[key], dtype=float)
    if cand.shape != ref.shape:
        raise ValueError(f"{key} shape mismatch {cand.shape} vs {ref.shape}")
    return float(np.max(np.abs(cand - ref)))


def reference_floors(model_name: str, reference: dict[str, np.ndarray]) -> dict[str, float]:
    public_ref = rv.run_public_model(
        rv.RA2021_MODEL_BY_NAME[model_name],
        "rA",
        "kinematics",
        REFERENCE_H,
        T_END,
        tol=1.0e-12,
    )
    return {
        "pos": final_error_to_reference(public_ref, reference, "pos"),
        "vel": final_error_to_reference(public_ref, reference, "vel"),
        "acc": final_error_to_reference(public_ref, reference, "acc"),
        "runtime_sec": float(public_ref["runtime_sec"]),
    }


def local_rows(reference_by_model: dict[str, dict[str, np.ndarray]], floors_by_model: dict[str, dict[str, float]]) -> list[dict[str, object]]:
    source = read_csv(RESULTS / "closed_loop_true_dynamic_newton_coarse_order_rows.csv")
    rows: list[dict[str, object]] = []
    for row in source:
        model = row.get("model", "")
        if model not in MODELS:
            continue
        floor = floors_by_model[model]
        rows.append(
            {
                "policy": POLICY,
                "source_suite": "local_true_dynamic_newton",
                "case_id": f"{model}_Gauss6_FullVA_true_dynamic_strict_common_reference",
                "model": model,
                "method": "Gauss6/FullVA-local-true-dynamic-newton",
                "form": "local",
                "row_type": "strict_common_reference_local_row",
                "t_end": fmt(row.get("t_end")),
                "common_reference_method": "v047_exact_kinematic_endpoint",
                "common_reference_h": fmt(REFERENCE_H),
                "h": fmt(row.get("h")),
                "status": row.get("status", "missing"),
                "steps": row.get("steps", "nan"),
                "pos_final_linf": fmt(row.get("endpoint_pos_error_inf")),
                "vel_final_linf": fmt(row.get("endpoint_vel_error_inf")),
                "acc_final_linf": fmt(row.get("endpoint_acc_error_inf")),
                "pos_observed_order": fmt(row.get("model_pos_observed_order")),
                "vel_observed_order": fmt(row.get("model_vel_observed_order")),
                "acc_observed_order": fmt(row.get("model_acc_observed_order")),
                "runtime_sec": fmt(row.get("runtime_sec")),
                "avg_iterations_or_newton_per_step": fmt(
                    as_float(row.get("total_stage_newton_iterations")) / max(1.0, as_float(row.get("steps")))
                ),
                "max_iterations_or_newton": row.get("total_stage_newton_iterations", "nan"),
                "total_iterations_or_newton": row.get("total_stage_newton_iterations", "nan"),
                "reference_floor_pos_linf": fmt(floor["pos"]),
                "reference_floor_vel_linf": fmt(floor["vel"]),
                "reference_floor_acc_linf": fmt(floor["acc"]),
                "stage_oracle_used": row.get("stage_oracle_used", "false"),
                "accepted_dynamic_order": row.get("accepted_dynamic_order", "false"),
                "strict_common_reference_error_columns": "true",
                "acceleration_column_diagnostic": "true",
                "default_policy": "coarse_first_no_default_1e-4",
                "strict_public_policy_1e-4_required": "false",
                "default_1e-4_required": "false",
                "heavy_numerical_run_invoked": "false",
                "external_superiority_claim_allowed": "false",
                "notes": (
                    "Local true-dynamic Newton row copied from the accepted coarse-order artifact. "
                    "Its endpoint errors already use the same v047 exact endpoint reference used here."
                ),
            }
        )
    return rows


def public_rows(reference_by_model: dict[str, dict[str, np.ndarray]], floors_by_model: dict[str, dict[str, float]]) -> list[dict[str, object]]:
    rv.switch_simengine_root(rv.SBEL_C2)
    rv.patch_modern_numpy_scalar_assignments()
    rows: list[dict[str, object]] = []
    for model_name in MODELS:
        public_model = rv.RA2021_MODEL_BY_NAME[model_name]
        reference = reference_by_model[model_name]
        floor = floors_by_model[model_name]
        for form in PUBLIC_FORMS:
            form_rows: list[dict[str, object]] = []
            for h in STEP_SIZES:
                started = time.perf_counter()
                row: dict[str, object] = {
                    "policy": POLICY,
                    "source_suite": "ra2021_taves_kissel_negrut",
                    "case_id": f"ra2021_{model_name}_{form}_strict_common_reference",
                    "model": model_name,
                    "method": f"{form}-public-dynamics",
                    "form": form,
                    "row_type": "strict_common_reference_public_row",
                    "t_end": fmt(T_END),
                    "common_reference_method": "v047_exact_kinematic_endpoint",
                    "common_reference_h": fmt(REFERENCE_H),
                    "h": fmt(h),
                    "status": "ok",
                    "steps": int(round(T_END / h)),
                    "pos_final_linf": "nan",
                    "vel_final_linf": "nan",
                    "acc_final_linf": "nan",
                    "pos_observed_order": "nan",
                    "vel_observed_order": "nan",
                    "acc_observed_order": "nan",
                    "runtime_sec": "nan",
                    "avg_iterations_or_newton_per_step": "nan",
                    "max_iterations_or_newton": "nan",
                    "total_iterations_or_newton": "nan",
                    "reference_floor_pos_linf": fmt(floor["pos"]),
                    "reference_floor_vel_linf": fmt(floor["vel"]),
                    "reference_floor_acc_linf": fmt(floor["acc"]),
                    "stage_oracle_used": "not_applicable",
                    "accepted_dynamic_order": "false",
                    "strict_common_reference_error_columns": "true",
                    "acceleration_column_diagnostic": "true",
                    "default_policy": "coarse_first_no_default_1e-4",
                    "strict_public_policy_1e-4_required": "false",
                    "default_1e-4_required": "false",
                    "heavy_numerical_run_invoked": "false",
                    "external_superiority_claim_allowed": "false",
                    "notes": (
                        "Public 2021 dynamics row recomputed against the shared v047 exact endpoint reference. "
                        "No source-policy 1e-4 row is run."
                    ),
                }
                try:
                    candidate = rv.run_public_model(public_model, form, "dynamics", h, T_END, tol=None)
                    row.update(
                        {
                            "pos_final_linf": fmt(final_error_to_reference(candidate, reference, "pos")),
                            "vel_final_linf": fmt(final_error_to_reference(candidate, reference, "vel")),
                            "acc_final_linf": fmt(final_error_to_reference(candidate, reference, "acc")),
                            "runtime_sec": fmt(candidate["runtime_sec"]),
                            "avg_iterations_or_newton_per_step": fmt(candidate["avg_iterations"]),
                            "max_iterations_or_newton": fmt(candidate["max_iterations"]),
                            "total_iterations_or_newton": fmt(float(np.sum(candidate["iters"]))),
                        }
                    )
                except Exception as exc:  # noqa: BLE001 - public failures must remain visible.
                    row["status"] = f"failed:{type(exc).__name__}:{str(exc).replace(chr(10), ' ')}"
                    row["runtime_sec"] = fmt(time.perf_counter() - started)
                form_rows.append(row)
                rows.append(row)
            for key, order in {
                "pos_observed_order": estimate_order(form_rows, "pos_final_linf"),
                "vel_observed_order": estimate_order(form_rows, "vel_final_linf"),
                "acc_observed_order": estimate_order(form_rows, "acc_final_linf"),
            }.items():
                for item in form_rows:
                    item[key] = fmt(order)
    return rows


def summarize_rows(rows: list[dict[str, object]]) -> tuple[list[dict[str, object]], dict[str, object]]:
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

        summary_rows.append(
            {
                "policy": f"{POLICY}_summary",
                "source_suite": finest.get("source_suite", "missing"),
                "case_id": f"{model}_{method}_strict_common_reference_summary",
                "model": model,
                "method": method,
                "row_count": len(group),
                "ok_row_count": len(ok),
                "t_end": fmt(finest.get("t_end")),
                "common_reference_method": finest.get("common_reference_method", "missing"),
                "common_reference_h": fmt(finest.get("common_reference_h")),
                "finest_h": fmt(finest.get("h")),
                "pos_observed_order": fmt(finest.get("pos_observed_order")),
                "vel_observed_order": fmt(finest.get("vel_observed_order")),
                "acc_observed_order": fmt(finest.get("acc_observed_order")),
                "finest_pos_final_linf": fmt(finest.get("pos_final_linf")),
                "finest_vel_final_linf": fmt(finest.get("vel_final_linf")),
                "finest_acc_final_linf": fmt(finest.get("acc_final_linf")),
                "runtime_sec_sum": fmt(finite_sum([as_float(row.get("runtime_sec")) for row in ok])),
                "total_iterations_or_newton_sum": fmt(
                    finite_sum([as_float(row.get("total_iterations_or_newton")) for row in ok])
                ),
                "finest_pos_error_ratio_vs_public_rA": ratio("pos_final_linf"),
                "finest_vel_error_ratio_vs_public_rA": ratio("vel_final_linf"),
                "finest_acc_error_ratio_vs_public_rA": ratio("acc_final_linf"),
                "finest_runtime_ratio_vs_public_rA": ratio("runtime_sec"),
                "reference_floor_pos_linf": fmt(finest.get("reference_floor_pos_linf")),
                "reference_floor_vel_linf": fmt(finest.get("reference_floor_vel_linf")),
                "reference_floor_acc_linf": fmt(finest.get("reference_floor_acc_linf")),
                "strict_common_reference_error_columns": finest.get("strict_common_reference_error_columns", "false"),
                "acceleration_column_diagnostic": finest.get("acceleration_column_diagnostic", "true"),
                "accepted_dynamic_order": finest.get("accepted_dynamic_order", "false"),
                "external_superiority_claim_allowed": "false",
                "notes": (
                    "All methods in this row group use the v047 exact endpoint as the common "
                    "position/velocity/acceleration reference. Acceleration remains a diagnostic column."
                ),
            }
        )

    available_models = []
    for model in MODELS:
        model_rows = [row for row in rows if row.get("model") == model]
        public_ok = [
            row
            for row in model_rows
            if str(row.get("method", "")).endswith("-public-dynamics") and row.get("status") == "ok"
        ]
        local_ok = [
            row
            for row in model_rows
            if row.get("method") == "Gauss6/FullVA-local-true-dynamic-newton" and row.get("status") == "ok"
        ]
        if len(public_ok) == len(PUBLIC_FORMS) * len(STEP_SIZES) and len(local_ok) == len(STEP_SIZES):
            available_models.append(model)

    figure_written = FIGURE.exists() and FIGURE.stat().st_size > 0
    summary = {
        "schema": "closed-loop-true-dynamic-strict-common-reference-v1",
        "status": "strict_common_reference_error_columns_available_not_external_superiority",
        "policy": POLICY,
        "default_policy": "coarse_first_no_default_1e-4",
        "models": list(MODELS),
        "public_forms": list(PUBLIC_FORMS),
        "step_sizes": list(STEP_SIZES),
        "t_end": T_END,
        "common_reference_method": "v047_exact_kinematic_endpoint",
        "common_reference_h": REFERENCE_H,
        "row_count": len(rows),
        "ok_row_count": sum(1 for row in rows if row.get("status") == "ok"),
        "public_raw_row_count": sum(1 for row in rows if str(row.get("method", "")).endswith("-public-dynamics")),
        "local_raw_row_count": sum(1 for row in rows if row.get("method") == "Gauss6/FullVA-local-true-dynamic-newton"),
        "summary_row_count": len(summary_rows),
        "strict_common_reference_available_count": len(available_models),
        "strict_common_reference_available_examples": available_models,
        "strict_common_reference_gap_count": len(MODELS) - len(available_models),
        "strict_common_reference_error_columns": True,
        "strict_common_reference_columns": ["pos_final_linf", "vel_final_linf", "acc_final_linf"],
        "acceleration_column_diagnostic": True,
        "accepted_external_dynamic_order_examples": [],
        "publication_quality_figure_available": figure_written,
        "figure": str(FIGURE.relative_to(HERE)),
        "external_superiority_claim": False,
        "default_1e-4_required": False,
        "strict_public_policy_1e-4_required": False,
        "heavy_numerical_run_invoked": False,
        "interpretation": (
            "This artifact recomputes the public closed-loop dynamics rows against the same v047 exact "
            "endpoint reference already used by the local true-dynamic Newton rows. It closes the strict "
            "common-reference error-column gap for position/velocity/acceleration columns at the coarse "
            "window, but it is not an external superiority claim."
        ),
    }
    return summary_rows, summary


def write_markdown(summary: dict[str, object], summary_rows: list[dict[str, object]]) -> None:
    lines = [
        "# Closed-Loop True-Dynamic Strict Common Reference",
        "",
        f"Status: **{str(summary['status']).replace('_', ' ')}**",
        "",
        f"- Rows: `{summary['ok_row_count']}/{summary['row_count']}` ok.",
        f"- Strict common-reference examples available: `{summary['strict_common_reference_available_count']}`.",
        f"- Strict common-reference examples missing: `{summary['strict_common_reference_gap_count']}`.",
        f"- Common reference: `{summary['common_reference_method']}`, `h={summary['common_reference_h']}`.",
        f"- Error columns: `{', '.join(summary['strict_common_reference_columns'])}`.",
        f"- Acceleration column diagnostic: `{summary['acceleration_column_diagnostic']}`.",
        f"- Publication figure available: `{summary['publication_quality_figure_available']}`.",
        f"- Default `1e-4` required: `{summary['default_1e-4_required']}`.",
        f"- External superiority claim: `{summary['external_superiority_claim']}`.",
        "",
        "The public `rA/rp/reps` rows are recomputed against the same v047 exact",
        "endpoint reference used by the local true-dynamic Newton rows. This removes",
        "the previous mixed-reference caveat for the tabulated translational error",
        "columns. It still does not claim external superiority; broader baseline",
        "coverage, figure integration, and paper review remain open.",
        "",
        "| Model | Method | ok | pos order | vel order | acc order | finest pos | finest vel | runtime sum | pos ratio vs rA | vel ratio vs rA |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in summary_rows:
        lines.append(
            "| "
            f"`{row['model']}` | `{row['method']}` | `{row['ok_row_count']}/{row['row_count']}` | "
            f"`{row['pos_observed_order']}` | `{row['vel_observed_order']}` | `{row['acc_observed_order']}` | "
            f"`{row['finest_pos_final_linf']}` | `{row['finest_vel_final_linf']}` | "
            f"`{row['runtime_sec_sum']}` | `{row['finest_pos_error_ratio_vs_public_rA']}` | "
            f"`{row['finest_vel_error_ratio_vs_public_rA']}` |"
        )
    SUMMARY_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_figure(rows: list[dict[str, object]]) -> None:
    import matplotlib.pyplot as plt

    method_labels = {
        "Gauss6/FullVA-local-true-dynamic-newton": "Gauss6/FullVA",
        "rA-public-dynamics": "rA",
        "rp-public-dynamics": "rp",
        "reps-public-dynamics": "reps",
    }
    markers = {
        "Gauss6/FullVA-local-true-dynamic-newton": "o",
        "rA-public-dynamics": "s",
        "rp-public-dynamics": "^",
        "reps-public-dynamics": "D",
    }
    colors = {
        "Gauss6/FullVA-local-true-dynamic-newton": "#0b3d91",
        "rA-public-dynamics": "#b23a48",
        "rp-public-dynamics": "#2f7d32",
        "reps-public-dynamics": "#6a4c93",
    }
    rc = {
        "font.size": 8,
        "axes.titlesize": 9,
        "axes.labelsize": 8,
        "xtick.labelsize": 7,
        "ytick.labelsize": 7,
        "legend.fontsize": 7,
        "figure.titlesize": 10,
    }
    with plt.rc_context(rc):
        fig, axes = plt.subplots(1, 2, figsize=(6.9, 2.85), constrained_layout=True)
        for ax, model in zip(axes, MODELS, strict=True):
            model_rows = [row for row in rows if row.get("model") == model and row.get("status") == "ok"]
            for method in method_labels:
                group = sorted(
                    [row for row in model_rows if row.get("method") == method],
                    key=lambda row: as_float(row.get("h")),
                )
                xs = [as_float(row.get("runtime_sec")) for row in group]
                ys = [as_float(row.get("pos_final_linf")) for row in group]
                clean = [
                    (x, y)
                    for x, y in zip(xs, ys)
                    if x > 0.0 and y > 0.0 and math.isfinite(x) and math.isfinite(y)
                ]
                if not clean:
                    continue
                ax.plot(
                    [item[0] for item in clean],
                    [item[1] for item in clean],
                    marker=markers.get(method, "o"),
                    color=colors.get(method, "#333333"),
                    linewidth=1.2,
                    markersize=4.0,
                    label=method_labels[method],
                )
            ax.set_xscale("log")
            ax.set_yscale("log")
            ax.set_title(model.replace("_", " "))
            ax.set_xlabel("runtime per row (s)")
            ax.set_ylabel("position error")
            ax.grid(True, which="both", alpha=0.25, linewidth=0.45)
        handles, labels = axes[0].get_legend_handles_labels()
        fig.legend(
            handles,
            labels,
            loc="lower center",
            bbox_to_anchor=(0.5, -0.04),
            ncols=4,
            frameon=False,
            handlelength=1.7,
            columnspacing=1.5,
        )
        fig.savefig(FIGURE, dpi=260, bbox_inches="tight", pad_inches=0.04)
    plt.close("all")


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    v047_module = import_v047_module()
    v046 = v047_module.load_v046()
    v046.patch_modern_numpy_scalar_assignments()
    models = {model.name: model for model in v046.MODELS}
    rv.switch_simengine_root(rv.SBEL_C2)
    rv.patch_modern_numpy_scalar_assignments()

    reference_by_model: dict[str, dict[str, np.ndarray]] = {}
    floors_by_model: dict[str, dict[str, float]] = {}
    for model_name in MODELS:
        reference_system = setup_exact_system(v047_module, v046, models[model_name], REFERENCE_H, T_END)
        reference_by_model[model_name] = public_like_endpoint(dynres.endpoint_state_from_system(reference_system))
        floors_by_model[model_name] = reference_floors(model_name, reference_by_model[model_name])

    rows = local_rows(reference_by_model, floors_by_model) + public_rows(reference_by_model, floors_by_model)
    write_figure(rows)
    summary_rows, summary = summarize_rows(rows)
    summary["publication_quality_figure_available"] = FIGURE.exists() and FIGURE.stat().st_size > 0
    write_csv(RAW_CSV, rows)
    write_csv(SUMMARY_CSV, summary_rows)
    with SUMMARY_JSON.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, sort_keys=True)
        handle.write("\n")
    write_markdown(summary, summary_rows)
    print("closed_loop_true_dynamic_strict_common_reference=written")
    print(f"rows_ok={summary['ok_row_count']}/{summary['row_count']}")
    print(f"strict_common_reference_available={summary['strict_common_reference_available_count']}/2")
    print(f"strict_common_reference_gap={summary['strict_common_reference_gap_count']}")
    print(f"figure={FIGURE.name}")
    print("default_1e-4=False")
    print("external_superiority_claim=False")


if __name__ == "__main__":
    main()
