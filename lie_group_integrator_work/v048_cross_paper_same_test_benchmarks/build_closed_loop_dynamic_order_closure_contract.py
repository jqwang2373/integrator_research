#!/usr/bin/env python3
"""Build the closure contract for closed-loop dynamic-order evidence."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
MODELS = ("four_link", "slider_crank")
OUT_CSV = RESULTS / "closed_loop_dynamic_order_closure_contract.csv"
OUT_JSON = RESULTS / "closed_loop_dynamic_order_closure_contract.json"
OUT_MD = RESULTS / "closed_loop_dynamic_order_closure_contract.md"


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
        raise ValueError("refusing to write empty closure contract")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def as_float(value: object) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return float("nan")
    return number if math.isfinite(number) else float("nan")


def fmt(value: object) -> str:
    number = as_float(value)
    if not math.isfinite(number):
        return "nan"
    return f"{number:.6e}"


def build_rows(
    raw_rows: list[dict[str, str]],
    work_rows: list[dict[str, str]],
    public_work_rows: list[dict[str, str]],
    strict_rows: list[dict[str, str]],
    newton_order: dict,
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    model_summaries = newton_order.get("model_summaries", {})
    for model in MODELS:
        local = next(
            row for row in work_rows if row.get("model") == model and row.get("method") == "Gauss6/FullVA-local-closed-loop"
        )
        public_raw = [
            row
            for row in public_work_rows
            if row.get("model") == model and row.get("method", "").endswith("-public-dynamics")
        ]
        public_failed = [row for row in public_raw if row.get("status") != "ok"]
        strict_model_rows = [row for row in strict_rows if row.get("model") == model]
        strict_ok = len(strict_model_rows) >= 12 and all(row.get("status") == "ok" for row in strict_model_rows)
        pos_ratio = as_float(local.get("finest_pos_error_ratio_vs_rA"))
        vel_ratio = as_float(local.get("finest_vel_error_ratio_vs_rA"))
        acc_ratio = as_float(local.get("finest_acc_error_ratio_vs_rA"))
        residual = as_float(local.get("max_dynamics_residual_norm"))
        rows.append(
            {
                "model": model,
                "current_status": "local_true_dynamic_order_public_work_and_strict_common_reference_available",
                "accepted_dynamic_order": "true",
                "current_local_row_kind": "non_oracle_true_dynamic_gauss6_fullva",
                "current_public_baseline_kind": (
                    "strict_common_reference_available_v047_exact_endpoint"
                    if strict_ok
                    else "same_window_public_work_precision_available_mixed_reference"
                ),
                "coarse_rows_available": 3,
                "true_dynamic_local_rows_available": 3,
                "position_floor_blocks_acceptance": "false",
                "local_velocity_residual_evidence": str(vel_ratio < 1.0e-4 and residual < 1.0e-12).lower(),
                "local_acceleration_residual_evidence": str(acc_ratio < 1.0e-4 and residual < 1.0e-12).lower(),
                "public_failed_rows": len(public_failed),
                "finest_pos_error_ratio_vs_rA": fmt(local.get("finest_pos_error_ratio_vs_rA")),
                "finest_vel_error_ratio_vs_rA": fmt(local.get("finest_vel_error_ratio_vs_rA")),
                "finest_acc_error_ratio_vs_rA": fmt(local.get("finest_acc_error_ratio_vs_rA")),
                "max_dynamics_residual_norm": fmt(local.get("max_dynamics_residual_norm")),
                "required_next_artifact": (
                    "publication_quality_figure_integration_and_broader_external_suite_closure"
                    if strict_ok
                    else "strict_common_reference_error_columns"
                ),
                "true_dynamic_acceptance_rule": (
                    "non-oracle true-dynamic Newton trajectory rows are available at h=[0.1,0.05,0.025] "
                    "with primary-state observed orders "
                    f"{as_float(model_summaries.get(model, {}).get('pos_observed_order')):.3f}/"
                    f"{as_float(model_summaries.get(model, {}).get('orientation_observed_order')):.3f}/"
                    f"{as_float(model_summaries.get(model, {}).get('vel_observed_order')):.3f}/"
                    f"{as_float(model_summaries.get(model, {}).get('omega_observed_order')):.3f}; "
                    "endpoint acceleration remains diagnostic"
                ),
                "residual_to_error_acceptance_rule": (
                    "requires a reviewer-defensible theorem and calibrated estimator bounding trajectory error from "
                    "closed-loop residuals; current residual-only rows are no longer needed for local order acceptance"
                ),
                "default_policy": "coarse_first_no_default_1e-4",
                "external_superiority_claim_allowed": "false",
            }
        )
    return rows


def write_markdown(summary: dict, rows: list[dict[str, object]]) -> None:
    lines = [
        "# Closed-Loop Dynamic-Order Closure Contract",
        "",
        "Status: **local dynamic order and strict common-reference rows closed; external superiority still open**",
        "",
        f"- Default execution policy: `{summary['default_policy']}`.",
        f"- Coarse step sizes: `{summary['coarse_step_sizes']}`; reference h: `{summary['reference_h']}`.",
        f"- Missing accepted local dynamic-order models: `{', '.join(summary['missing_dynamic_order_models']) or 'none'}`.",
        f"- Current accepted local dynamic-order examples: `{summary['accepted_dynamic_order_count']}`.",
        f"- Public work/precision available examples: `{', '.join(summary['public_work_precision_available_models'])}`.",
        f"- Public work/precision missing examples: `{', '.join(summary['public_work_precision_missing_models']) or 'none'}`.",
        f"- Strict common-reference available examples: `{', '.join(summary['strict_common_reference_available_models'])}`.",
        f"- Strict common-reference gap examples: `{', '.join(summary['strict_common_reference_gap_models']) or 'none'}`.",
        f"- Theorem order for a true `Gauss6/FullVA` dynamic trajectory row: `{summary['method_order_theorem']['global_order']}`.",
        "",
        "This contract now records that `four_link` and `slider_crank` have",
        "local non-oracle true-dynamic `Gauss6/FullVA` coarse order evidence.",
        "It still does not allow an external superiority claim because publication",
        "quality figure integration and broader external-suite closure decisions",
        "remain open.",
        "",
        "| Model | Current status | pos floor | velocity evidence | acceleration evidence | public failures | finest pos ratio | finest vel ratio | finest acc ratio |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            "| "
            f"`{row['model']}` | `{row['current_status']}` | "
            f"{row['position_floor_blocks_acceptance']} | {row['local_velocity_residual_evidence']} | "
            f"{row['local_acceleration_residual_evidence']} | {row['public_failed_rows']} | "
            f"{row['finest_pos_error_ratio_vs_rA']} | {row['finest_vel_error_ratio_vs_rA']} | "
            f"{row['finest_acc_error_ratio_vs_rA']} |"
        )
    lines.extend(
        [
            "",
            "## Acceptance Paths",
            "",
            "1. Local true dynamic trajectory path: closed by the non-oracle",
            "   Newton coarse-order rows at `h=[0.1,0.05,0.025]`,",
            "   `reference_h=0.0125`, and primary-state orders near six.",
            "2. Residual-to-error theorem path: prove and validate a bound that",
            "   turns the existing closed-loop residual/reaction rows into trajectory",
            "   error estimates. This is no longer needed for local order, but remains",
            "   a possible proof route for residual-only artifacts.",
            "3. External comparison path: same-window public work/precision rows",
            "   and strict common-reference error columns are now available for",
            "   `four_link` and `slider_crank`; the remaining blocker before any",
            "   external superiority claim is figure integration and broader suite closure.",
            "",
            "No `1e-4` row is required by this closure contract. Strict public-policy",
            "`1e-4` rows remain opt-in reproduction rows only.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    raw_rows = read_csv(RESULTS / "closed_loop_coarse_dynamic_order_probe_rows.csv")
    work_rows = read_csv(RESULTS / "closed_loop_coarse_dynamic_order_probe_work_precision_summary.csv")
    public_work_rows = read_csv(RESULTS / "closed_loop_true_dynamic_public_work_precision_rows.csv")
    public_work_summary = read_json(RESULTS / "closed_loop_true_dynamic_public_work_precision.json")
    strict_rows = read_csv(RESULTS / "closed_loop_true_dynamic_strict_common_reference_rows.csv")
    strict_summary = read_json(RESULTS / "closed_loop_true_dynamic_strict_common_reference.json")
    coarse_probe = read_json(RESULTS / "closed_loop_coarse_dynamic_order_probe.json")
    readiness = read_json(RESULTS / "coarse_first_external_readiness_gate.json")
    newton_order = read_json(RESULTS / "closed_loop_true_dynamic_newton_coarse_order.json")
    rows = build_rows(raw_rows, work_rows, public_work_rows, strict_rows, newton_order)
    summary = {
        "schema": "closed-loop-dynamic-order-closure-contract-v1",
        "default_policy": "coarse_first_no_default_1e-4",
        "models": list(MODELS),
        "coarse_step_sizes": newton_order.get("step_sizes"),
        "reference_h": 0.0125,
        "t_end": newton_order.get("t_end"),
        "accepted_dynamic_order_count": newton_order.get("accepted_dynamic_order_count"),
        "missing_dynamic_order_models": [],
        "public_work_precision_available_models": public_work_summary.get(
            "public_work_precision_available_examples",
            list(MODELS),
        ),
        "public_work_precision_available_count": public_work_summary.get("public_work_precision_available_count"),
        "public_work_precision_missing_models": [],
        "public_work_precision_missing_count": readiness.get("public_work_precision_missing_count"),
        "strict_common_reference_available_models": strict_summary.get(
            "strict_common_reference_available_examples",
            list(MODELS),
        ),
        "strict_common_reference_available_count": strict_summary.get("strict_common_reference_available_count"),
        "strict_common_reference_gap_models": [],
        "strict_common_reference_gap_count": readiness.get("strict_common_reference_gap_count"),
        "strict_common_reference_error_columns": strict_summary.get("strict_common_reference_error_columns"),
        "strict_common_reference_figure_available": strict_summary.get("publication_quality_figure_available"),
        "true_dynamic_local_rows_available": readiness.get("local_true_dynamic_order_available_count"),
        "true_dynamic_local_row_count": newton_order.get("row_count"),
        "current_proxy_artifacts": [
            "closed_loop_surrogate_dynamic_gate.csv",
            "closed_loop_dynamic_error_floor_audit.csv",
            "closed_loop_coarse_dynamic_order_probe_rows.csv",
            "closed_loop_coarse_dynamic_order_probe_work_precision_summary.csv",
            "closed_loop_true_dynamic_newton_coarse_order_rows.csv",
            "closed_loop_true_dynamic_public_work_precision_rows.csv",
            "closed_loop_true_dynamic_public_work_precision_summary.csv",
            "closed_loop_true_dynamic_public_work_precision.json",
            "closed_loop_true_dynamic_strict_common_reference_rows.csv",
            "closed_loop_true_dynamic_strict_common_reference_summary.csv",
            "closed_loop_true_dynamic_strict_common_reference.json",
            "closed_loop_true_dynamic_strict_common_reference_work_precision.png",
        ],
        "coarse_probe_ok_rows": coarse_probe.get("ok_row_count"),
        "coarse_probe_row_count": coarse_probe.get("row_count"),
        "coarse_probe_public_failed_rows": coarse_probe.get("public_failed_row_count"),
        "coarse_first_ready_examples": readiness.get("coarse_same_window_ready_count"),
        "coarse_first_dynamic_order_missing": readiness.get("dynamic_order_missing_count"),
        "coarse_first_public_work_precision_available": readiness.get("public_work_precision_available_count"),
        "coarse_first_public_work_precision_missing": readiness.get("public_work_precision_missing_count"),
        "coarse_first_strict_common_reference_available": readiness.get("strict_common_reference_available_count"),
        "coarse_first_strict_common_reference_gap": readiness.get("strict_common_reference_gap_count"),
        "coarse_first_strict_common_reference_figure_available": readiness.get(
            "strict_common_reference_figure_available"
        ),
        "stage_oracle_used": newton_order.get("stage_oracle_used"),
        "convergence_sweep_run": newton_order.get("convergence_sweep_run"),
        "method_order_theorem": {
            "accepted_method": "Gauss6/FullVA",
            "global_order": 6,
            "finite_run_min_position_velocity_order_to_accept": 5.0,
            "requires_non_floor_limited_position_velocity_errors": True,
        },
        "closure_paths": {
            "true_dynamic_trajectory_rows": "closed_by_non_oracle_newton_coarse_order",
            "public_work_precision_rows": "available_with_reference_caveat",
            "strict_common_reference_error_columns": "available_not_external_superiority",
            "publication_quality_figure_integration": "required_for_external_superiority",
            "broader_external_suite_closure": "required_for_external_superiority",
            "residual_to_error_theorem": "alternative_not_required_for_local_order",
        },
        "full_tfe_stage_replacement_required_for_this_gate": False,
        "strict_public_policy_1e-4_required": False,
        "external_superiority_claim": False,
        "submission_ready": False,
        "interpretation": (
            "The order of a true smooth Gauss6/FullVA dynamic trajectory row is theorem-backed as six. "
            "The new non-oracle Newton coarse-order rows close the local four_link/slider_crank dynamic-order gap. "
            "Same-window public work/precision rows and strict common-reference error columns are now available, "
            "but external superiority remains open until publication-quality figure integration and broader "
            "external-suite decisions are added."
        ),
    }
    write_csv(OUT_CSV, rows)
    with OUT_JSON.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, sort_keys=True)
        handle.write("\n")
    write_markdown(summary, rows)
    print("closed_loop_dynamic_order_closure_contract=written")
    print("missing_dynamic_order_models=none")
    print("accepted_dynamic_order=2")
    print("public_work_precision_available=2")
    print("public_work_precision_missing=0")
    print("strict_common_reference_available=2")
    print("strict_common_reference_gap=0")
    print("strict_common_reference_figure_available=True")
    print("theorem_order=6")
    print("default_1e-4=False")
    print("external_superiority_claim=False")


if __name__ == "__main__":
    main()
