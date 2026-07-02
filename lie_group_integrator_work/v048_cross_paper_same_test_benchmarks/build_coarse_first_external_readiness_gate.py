#!/usr/bin/env python3
"""Build the coarse-first external-comparison readiness gate from existing rows."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
EXAMPLES = ("single_pendulum", "double_pendulum", "four_link", "slider_crank")
COARSE_H = "0.1|0.05|0.025"
COARSE_REFERENCE_H = "0.0125"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def read_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def first_row(rows: list[dict[str, str]], *, method: str, example: str) -> dict[str, str] | None:
    for row in rows:
        if row.get("method") == method and row.get("example") == example:
            return row
    return None


def public_rows(rows: list[dict[str, str]], example: str) -> list[dict[str, str]]:
    return [
        row
        for row in rows
        if row.get("example") == example
        and row.get("method") in {"rA", "rp", "reps"}
        and row.get("source_suite") == "ra2021_public_code"
    ]


def completed_count(rows: list[dict[str, str]]) -> int:
    return sum(1 for row in rows if row.get("status", "").startswith("completed"))


def row_by_method(rows: list[dict[str, str]], method: str) -> dict[str, str]:
    for row in rows:
        if row.get("method") == method:
            return row
    return {}


def fmt_order(row: dict[str, str], key: str) -> str:
    try:
        return f"{float(row.get(key, 'nan')):.3f}"
    except ValueError:
        return "nan"


def make_row(
    *,
    example: str,
    readiness_status: str,
    local_status: str,
    public_status: str,
    current_order_evidence: str,
    current_time_evidence: str,
    next_lightweight_action: str,
    remaining_blocker: str,
    evidence_paths: str,
) -> dict[str, str]:
    return {
        "example": example,
        "default_policy": "coarse_first_no_default_1e-4",
        "coarse_step_sizes": COARSE_H,
        "coarse_reference_h": COARSE_REFERENCE_H,
        "readiness_status": readiness_status,
        "local_status": local_status,
        "public_baseline_status": public_status,
        "current_order_evidence": current_order_evidence,
        "current_time_evidence": current_time_evidence,
        "superiority_claim_allowed": "false",
        "next_lightweight_action": next_lightweight_action,
        "remaining_blocker": remaining_blocker,
        "evidence_paths": evidence_paths,
    }


def build_gate() -> tuple[list[dict[str, str]], dict]:
    matrix = read_csv(RESULTS / "four_example_performance_matrix.csv")
    summary = read_json(RESULTS / "summary_v048.json")
    surrogate_path = RESULTS / "closed_loop_surrogate_dynamic_gate.csv"
    surrogate_rows = read_csv(surrogate_path) if surrogate_path.exists() else []
    surrogate_by_model = {row.get("model"): row for row in surrogate_rows}
    floor_audit_path = RESULTS / "closed_loop_dynamic_error_floor_audit.csv"
    floor_audit_rows = read_csv(floor_audit_path) if floor_audit_path.exists() else []
    floor_audit_by_model = {row.get("model"): row for row in floor_audit_rows}
    newton_order_path = RESULTS / "closed_loop_true_dynamic_newton_coarse_order.json"
    newton_order_rows_path = RESULTS / "closed_loop_true_dynamic_newton_coarse_order_rows.csv"
    newton_order_summary = read_json(newton_order_path) if newton_order_path.exists() else {}
    newton_order_by_model = newton_order_summary.get("model_summaries", {})
    public_work_path = RESULTS / "closed_loop_true_dynamic_public_work_precision_summary.csv"
    public_work_json_path = RESULTS / "closed_loop_true_dynamic_public_work_precision.json"
    public_work_rows = read_csv(public_work_path) if public_work_path.exists() else []
    public_work_summary = read_json(public_work_json_path) if public_work_json_path.exists() else {}
    public_work_by_model = {
        model: [row for row in public_work_rows if row.get("model") == model]
        for model in ("four_link", "slider_crank")
    }
    strict_reference_path = RESULTS / "closed_loop_true_dynamic_strict_common_reference_summary.csv"
    strict_reference_json_path = RESULTS / "closed_loop_true_dynamic_strict_common_reference.json"
    strict_reference_rows = read_csv(strict_reference_path) if strict_reference_path.exists() else []
    strict_reference_summary = read_json(strict_reference_json_path) if strict_reference_json_path.exists() else {}
    strict_reference_by_model = {
        model: [row for row in strict_reference_rows if row.get("model") == model]
        for model in ("four_link", "slider_crank")
    }
    single_work_path = RESULTS / "single_pendulum_coarse_same_window_work_precision_summary.csv"
    single_work_json_path = RESULTS / "single_pendulum_coarse_same_window_work_precision_summary.json"
    single_work_rows = read_csv(single_work_path) if single_work_path.exists() else []
    single_work_summary = read_json(single_work_json_path) if single_work_json_path.exists() else {}
    single_coarse_available = (
        single_work_summary.get("default_policy") == "coarse_first_no_default_1e-4"
        and single_work_summary.get("external_superiority_claim") is False
        and single_work_summary.get("row_count", 0) >= 4
        and single_work_summary.get("ok_row_count", 0) >= 4
    )

    rows: list[dict[str, str]] = []
    for example in EXAMPLES:
        local_public = first_row(matrix, method="Gauss6/FullVA-public-horizon", example=example)
        public = public_rows(matrix, example)
        public_completed = completed_count(public)

        if example == "double_pendulum":
            coarse = summary.get("ra2021_double_pendulum_coarse_order", {})
            work = summary.get("double_pendulum_coarse_same_window_work_precision_summary", {})
            rows.append(
                make_row(
                    example=example,
                    readiness_status="coarse_same_window_order_time_available",
                    local_status=local_public.get("status", "missing") if local_public else "missing",
                    public_status=f"{coarse.get('ok_row_count', 0)}/{coarse.get('row_count', 0)} coarse public rows ok",
                    current_order_evidence=(
                        "Gauss6/FullVA pos/vel order 7.951/7.042; "
                        "public rA/reps pos/vel order 0.703/0.754; rp nonconverged"
                    ),
                    current_time_evidence=(
                        "work/precision summary has "
                        f"{work.get('ok_row_count', 0)}/{work.get('row_count', 0)} rows"
                    ),
                    next_lightweight_action=(
                        "Use this as the coarse-first template; do not rerun source h=1e-4 unless strict "
                        "source-policy reproduction is explicitly requested."
                    ),
                    remaining_blocker=(
                        "Closed-loop local true-dynamic order is now available, but same-window "
                        "public work/precision comparison is still missing for four_link and slider_crank."
                    ),
                    evidence_paths=(
                        "results/gauss6_fullva_public_horizon_double_coarse_rows.csv;"
                        "results/ra2021_double_pendulum_coarse_order_rows.csv;"
                        "results/double_pendulum_coarse_same_window_work_precision_summary.csv"
                    ),
                )
            )
        elif example == "single_pendulum":
            if single_coarse_available:
                gauss = row_by_method(single_work_rows, "Gauss6/FullVA-public-horizon-single-coarse")
                rA = row_by_method(single_work_rows, "rA-public-dynamics-coarse")
                reps = row_by_method(single_work_rows, "reps-public-dynamics-coarse")
                rows.append(
                    make_row(
                        example=example,
                        readiness_status="coarse_same_window_order_time_available",
                        local_status="3/3 coarse local rows ok",
                        public_status="9/9 coarse public rows ok",
                        current_order_evidence=(
                            "Gauss6/FullVA pos/vel order "
                            f"{fmt_order(gauss, 'pos_observed_order')}/{fmt_order(gauss, 'vel_observed_order')}; "
                            "public rA/reps vel order "
                            f"{fmt_order(rA, 'vel_observed_order')}/{fmt_order(reps, 'vel_observed_order')}; "
                            "position columns near the public/reference floor are diagnostics."
                        ),
                        current_time_evidence=(
                            "work/precision summary has "
                            f"{single_work_summary.get('ok_row_count', 0)}/{single_work_summary.get('row_count', 0)} rows; "
                            "Gauss6 finest-h runtime ratio vs rA is "
                            f"{fmt_order(gauss, 'finest_runtime_ratio_vs_rA')}."
                        ),
                        next_lightweight_action=(
                            "Use this as the single-pendulum coarse-first row; do not rerun source h=1e-4 "
                            "unless strict source-policy reproduction is explicitly requested."
                        ),
                        remaining_blocker=(
                            "Single-pendulum coarse evidence is available; full external superiority "
                            "still requires public work/precision comparison for the closed-loop true-dynamic rows."
                        ),
                        evidence_paths=(
                            "results/ra2021_single_pendulum_coarse_order_rows.csv;"
                            "results/gauss6_fullva_public_horizon_single_coarse_rows.csv;"
                            "results/single_pendulum_coarse_same_window_work_precision_summary.csv;"
                            "results/single_pendulum_coarse_same_window_work_precision_summary.json"
                        ),
                    )
                )
            else:
                rows.append(
                    make_row(
                        example=example,
                        readiness_status="public_policy_rows_exist_but_not_coarse_default",
                        local_status=local_public.get("status", "missing") if local_public else "missing",
                        public_status=f"{public_completed}/3 public forms completed in matrix",
                        current_order_evidence=(
                            "Public-horizon local and public rows exist, but local final errors are "
                            "roundoff/reference-floor limited and use the historical public h policy."
                        ),
                        current_time_evidence=(
                            "Runtime rows exist in the four-example matrix, but no dedicated coarse "
                            "same-window order/time summary is present."
                        ),
                        next_lightweight_action=(
                            "Add a coarse same-window single-pendulum tranche at T=3, h=0.1|0.05|0.025, "
                            "reference h=0.0125 or an explicitly justified smaller reference."
                        ),
                        remaining_blocker=(
                            "Current evidence is useful but does not follow the no-default-1e-4 coarse-first "
                            "comparison policy."
                        ),
                        evidence_paths=(
                            "results/ra2021_order_rows.csv;"
                            "results/gauss6_fullva_public_horizon_single_rows.csv;"
                            "results/four_example_performance_matrix.csv"
                        ),
                    )
                )
        else:
            surrogate = surrogate_by_model.get(example)
            floor_audit = floor_audit_by_model.get(example)
            newton_order = newton_order_by_model.get(example, {})
            public_work = public_work_by_model.get(example, [])
            public_work_available = (
                public_work_summary.get("public_work_precision_missing_count") == 0
                and public_work_summary.get("external_superiority_claim") is False
                and len(public_work) >= 4
                and all(row.get("ok_row_count") == "3" for row in public_work)
            )
            strict_reference = strict_reference_by_model.get(example, [])
            strict_reference_available = (
                strict_reference_summary.get("strict_common_reference_gap_count") == 0
                and strict_reference_summary.get("external_superiority_claim") is False
                and len(strict_reference) >= 4
                and all(row.get("ok_row_count") == "3" for row in strict_reference)
            )
            if newton_order.get("accepted_dynamic_order_candidate") is True:
                if strict_reference_available:
                    readiness_status = "local_true_dynamic_order_public_work_and_strict_common_reference_available"
                elif public_work_available:
                    readiness_status = "local_true_dynamic_order_and_public_work_available_reference_caveat"
                else:
                    readiness_status = "local_true_dynamic_order_available_public_work_missing"
                current_order_evidence = (
                    "Local true-dynamic Newton coarse row available: pos/orient/vel/omega order "
                    f"{float(newton_order.get('pos_observed_order', float('nan'))):.3f}/"
                    f"{float(newton_order.get('orientation_observed_order', float('nan'))):.3f}/"
                    f"{float(newton_order.get('vel_observed_order', float('nan'))):.3f}/"
                    f"{float(newton_order.get('omega_observed_order', float('nan'))):.3f}; "
                    "stage oracle used=false; endpoint acceleration remains diagnostic."
                )
                if strict_reference_available:
                    current_time_evidence = (
                        "Same-window public rA/rp/reps work/precision rows and strict common-reference "
                        "v047 exact-endpoint error columns are available."
                    )
                    next_lightweight_action = (
                        "Integrate the strict common-reference work/precision figure into the manuscript "
                        "and keep source h=1e-4 opt-in."
                    )
                    remaining_blocker = (
                        "Strict common-reference rows are available, but external superiority still needs "
                        "publication-quality figure integration and the broader external-suite closure decisions."
                    )
                elif public_work_available:
                    current_time_evidence = (
                        "Same-window public rA/rp/reps work/precision rows are available; "
                        "strict common-reference error columns are still false."
                    )
                    next_lightweight_action = (
                        "Add a strict common-reference error table or manuscript caveat before any "
                        "external superiority claim; keep source h=1e-4 opt-in."
                    )
                    remaining_blocker = (
                        "Public work/precision rows are available, but external superiority still needs "
                        "strict common-reference error columns and publication-quality figures."
                    )
                else:
                    current_time_evidence = (
                        "Local true-dynamic runtimes are recorded in the coarse Newton rows; "
                        "same-window public work/precision comparison against these rows is still missing."
                    )
                    next_lightweight_action = (
                        "Add same-window public rA/rp/reps work/precision comparison against the true-dynamic "
                        "Newton rows; keep source h=1e-4 opt-in."
                    )
                    remaining_blocker = (
                        "Accepted local true-dynamic order is available, but external superiority still needs "
                        "public-baseline work/precision rows on the same window."
                    )
                evidence_paths = (
                    "results/closed_loop_true_dynamic_newton_coarse_order_rows.csv;"
                    "results/closed_loop_true_dynamic_newton_coarse_order.json;"
                    "results/closed_loop_true_dynamic_public_work_precision_rows.csv;"
                    "results/closed_loop_true_dynamic_public_work_precision_summary.csv;"
                    "results/closed_loop_true_dynamic_public_work_precision.json;"
                    "results/closed_loop_true_dynamic_strict_common_reference_rows.csv;"
                    "results/closed_loop_true_dynamic_strict_common_reference_summary.csv;"
                    "results/closed_loop_true_dynamic_strict_common_reference.json;"
                    "results/closed_loop_true_dynamic_strict_common_reference_work_precision.png;"
                    "results/closed_loop_surrogate_dynamic_gate.csv;"
                    "results/closed_loop_dynamic_error_floor_audit.csv;"
                    "results/four_example_performance_matrix.csv"
                )
            elif surrogate:
                readiness_status = "surrogate_available_dynamic_order_still_missing"
                floor_text = ""
                if floor_audit:
                    floor_text = (
                        " Floor audit: local velocity/acceleration error ratios "
                        f"{floor_audit.get('local_vel_error_ratio_vs_public', 'nan')}/"
                        f"{floor_audit.get('local_acc_error_ratio_vs_public', 'nan')}; "
                        "position/reference floor blocks accepted dynamic order."
                    )
                current_order_evidence = (
                    "Selected-window residual-to-error surrogate available: public rA "
                    f"velocity order {surrogate.get('public_vel_order', 'nan')}; local "
                    f"velocity-error ratio {surrogate.get('local_vel_error_ratio_vs_public', 'nan')} "
                    "against the public rA finest row; local row remains residual-floor/kinematic."
                    f"{floor_text}"
                )
                current_time_evidence = (
                    "Surrogate work row available: local runtime ratio "
                    f"{surrogate.get('local_runtime_ratio_vs_public', 'nan')} and max dynamics "
                    f"residual {surrogate.get('local_max_dynamics_residual_norm', 'nan')}."
                )
                next_lightweight_action = (
                    "Promote this surrogate only after adding a true local dynamic order/work row "
                    "or a reviewer-defensible residual-to-error acceptance proof; keep source h=1e-4 opt-in."
                )
                remaining_blocker = (
                    "Surrogate exists, but accepted local dynamic order/work evidence is still missing."
                )
                evidence_paths = (
                    "results/closed_loop_surrogate_dynamic_gate.csv;"
                    "results/closed_loop_dynamic_error_floor_audit.csv;"
                    "results/ra2021_order_rows.csv;"
                    "results/gauss6_fullva_public_horizon_closed_loop_rows.csv;"
                    "results/gauss6_fullva_closed_loop_same_window_comparison_rows.csv;"
                    "results/four_example_performance_matrix.csv"
                )
            else:
                readiness_status = "residual_or_selected_window_only_dynamic_order_missing"
                current_order_evidence = (
                    "Public baseline order rows exist; local Gauss6/FullVA rows currently verify "
                    "closed-loop constraint/reaction residuals rather than dynamic order/work."
                )
                current_time_evidence = (
                    "Selected-window table-shape and public-horizon residual runtimes exist, "
                    "but they are not dynamic order/work-superiority rows."
                )
                next_lightweight_action = (
                    "Add a coarse same-window dynamic-order surrogate or a defensible residual-to-error "
                    "metric at T=0.2 or T=3 using h=0.02|0.01|0.005 first; keep source h=1e-4 opt-in."
                )
                remaining_blocker = (
                    "Need comparable local dynamic order/work metric on the same mechanism; residual "
                    "rows alone are not enough for CMAME superiority."
                )
                evidence_paths = (
                    "results/ra2021_order_rows.csv;"
                    "results/gauss6_fullva_public_horizon_closed_loop_rows.csv;"
                    "results/gauss6_fullva_closed_loop_same_window_comparison_rows.csv;"
                    "results/four_example_performance_matrix.csv"
                )
            rows.append(
                make_row(
                    example=example,
                    readiness_status=readiness_status,
                    local_status=local_public.get("status", "missing") if local_public else "missing",
                    public_status=f"{public_completed}/3 public forms completed in matrix",
                    current_order_evidence=current_order_evidence,
                    current_time_evidence=current_time_evidence,
                    next_lightweight_action=next_lightweight_action,
                    remaining_blocker=remaining_blocker,
                    evidence_paths=evidence_paths,
                )
            )

    ready = [row for row in rows if row["readiness_status"] == "coarse_same_window_order_time_available"]
    missing_dynamic = [
        row
        for row in rows
        if row["readiness_status"]
        in {
            "residual_or_selected_window_only_dynamic_order_missing",
            "surrogate_available_dynamic_order_still_missing",
        }
    ]
    local_true_dynamic = [
        row
        for row in rows
        if row["readiness_status"]
        in {
            "local_true_dynamic_order_available_public_work_missing",
            "local_true_dynamic_order_and_public_work_available_reference_caveat",
            "local_true_dynamic_order_public_work_and_strict_common_reference_available",
        }
    ]
    public_work_missing = [
        row for row in rows if row["readiness_status"] == "local_true_dynamic_order_available_public_work_missing"
    ]
    public_work_available = [
        row
        for row in rows
        if row["readiness_status"] == "local_true_dynamic_order_and_public_work_available_reference_caveat"
        or row["readiness_status"] == "local_true_dynamic_order_public_work_and_strict_common_reference_available"
    ]
    common_reference_available = [
        row
        for row in rows
        if row["readiness_status"] == "local_true_dynamic_order_public_work_and_strict_common_reference_available"
    ]
    common_reference_gap = [
        row for row in public_work_available if row["readiness_status"] != "local_true_dynamic_order_public_work_and_strict_common_reference_available"
    ]
    surrogate_available = [
        row for row in rows if row["readiness_status"] == "surrogate_available_dynamic_order_still_missing"
    ]
    summary_out = {
        "schema": "coarse-first-external-readiness-gate-v1",
        "examples": list(EXAMPLES),
        "row_count": len(rows),
        "coarse_same_window_ready_count": len(ready),
        "single_coarse_same_window_available_count": 1 if single_coarse_available else 0,
        "local_true_dynamic_order_available_count": len(local_true_dynamic),
        "public_work_precision_available_count": len(public_work_available),
        "public_work_precision_missing_count": len(public_work_missing),
        "strict_common_reference_available_count": len(common_reference_available),
        "strict_common_reference_gap_count": len(common_reference_gap),
        "strict_common_reference_figure_available": bool(
            strict_reference_summary.get("publication_quality_figure_available") is True
        ),
        "closed_loop_surrogate_available_count": len(surrogate_available),
        "closed_loop_floor_audit_available_count": len(
            [
                row
                for row in rows
                if row["example"] in {"four_link", "slider_crank"}
                and "closed_loop_dynamic_error_floor_audit.csv" in row["evidence_paths"]
            ]
        ),
        "dynamic_order_missing_count": len(missing_dynamic),
        "default_policy": "coarse_first_no_default_1e-4",
        "coarse_step_sizes": [0.1, 0.05, 0.025],
        "coarse_reference_h": 0.0125,
        "same_test_campaign_status": summary.get("same_test_campaign_status", "unknown"),
        "external_superiority_claim": False,
        "submission_ready": False,
        "interpretation": (
            "This is a read-only readiness gate for the user's coarse-first comparison policy. "
            "It does not run numerical simulations. Local true-dynamic order rows can close the "
            "closed-loop dynamic-order gap. Same-window public work/precision rows can close the "
            "work/precision availability gap. Strict common-reference rows can close the reference "
            "family gap, but external superiority still requires publication-quality figure integration "
            "and broader external-suite closure decisions."
        ),
    }
    return rows, summary_out


def write_markdown(rows: list[dict[str, str]], summary: dict) -> None:
    lines = [
        "# Coarse-First External Readiness Gate",
        "",
        "Status: **not submission ready; no external superiority claim**",
        "",
        f"- Default policy: `{summary['default_policy']}`.",
        f"- Coarse step sizes: `{COARSE_H}`.",
        f"- Coarse reference h: `{COARSE_REFERENCE_H}`.",
        f"- Coarse same-window ready examples: `{summary['coarse_same_window_ready_count']}/4`.",
        f"- Local true-dynamic order available examples: `{summary['local_true_dynamic_order_available_count']}`.",
        f"- Public work/precision available examples: `{summary['public_work_precision_available_count']}`.",
        f"- Public work/precision missing examples: `{summary['public_work_precision_missing_count']}`.",
        f"- Strict common-reference available examples: `{summary['strict_common_reference_available_count']}`.",
        f"- Strict common-reference gap examples: `{summary['strict_common_reference_gap_count']}`.",
        f"- Strict common-reference figure available: `{summary['strict_common_reference_figure_available']}`.",
        f"- Closed-loop surrogate available examples: `{summary['closed_loop_surrogate_available_count']}`.",
        f"- Closed-loop floor-audit available examples: `{summary['closed_loop_floor_audit_available_count']}`.",
        f"- Dynamic-order missing examples: `{summary['dynamic_order_missing_count']}`.",
        f"- Same-test campaign status: `{summary['same_test_campaign_status']}`.",
        "",
        "Reading rule: `1e-4` is not a default execution target. Use it only for strict source-paper/public-code policy reproduction.",
        "",
        "| Example | Readiness | Local status | Public baseline | Current order evidence | Next lightweight action | Blocker |",
        "|---|---|---|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            "| "
            f"`{row['example']}` | "
            f"`{row['readiness_status']}` | "
            f"`{row['local_status']}` | "
            f"{row['public_baseline_status']} | "
            f"{row['current_order_evidence']} | "
            f"{row['next_lightweight_action']} | "
            f"{row['remaining_blocker']} |"
        )
    lines.append("")
    (RESULTS / "coarse_first_external_readiness_gate.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    rows, summary = build_gate()
    write_csv(RESULTS / "coarse_first_external_readiness_gate.csv", rows)
    with (RESULTS / "coarse_first_external_readiness_gate.json").open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, sort_keys=True)
        handle.write("\n")
    write_markdown(rows, summary)
    print("coarse_first_external_readiness_gate=written")
    print(f"rows={summary['row_count']}")
    print(f"coarse_same_window_ready={summary['coarse_same_window_ready_count']}/4")
    print(f"public_work_precision_available={summary['public_work_precision_available_count']}")
    print(f"strict_common_reference_available={summary['strict_common_reference_available_count']}")
    print(f"strict_common_reference_gap={summary['strict_common_reference_gap_count']}")
    print(f"strict_common_reference_figure_available={summary['strict_common_reference_figure_available']}")
    print(f"dynamic_order_missing={summary['dynamic_order_missing_count']}")
    print("external_superiority_claim=False")


if __name__ == "__main__":
    main()
