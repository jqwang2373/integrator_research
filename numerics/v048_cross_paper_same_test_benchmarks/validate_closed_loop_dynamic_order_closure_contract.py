#!/usr/bin/env python3
"""Validate the closed-loop dynamic-order closure contract."""

from __future__ import annotations

import csv
import json
import math
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
MODELS = {"four_link", "slider_crank"}


class Checks:
    def __init__(self) -> None:
        self.errors: list[str] = []

    def check(self, condition: bool, message: str) -> None:
        if not condition:
            self.errors.append(message)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def read_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def as_float(value: object) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return float("nan")
    return number if math.isfinite(number) else float("nan")


def main() -> int:
    checks = Checks()
    try:
        rows = read_csv(RESULTS / "closed_loop_dynamic_order_closure_contract.csv")
        summary = read_json(RESULTS / "closed_loop_dynamic_order_closure_contract.json")
        report = (RESULTS / "closed_loop_dynamic_order_closure_contract.md").read_text(encoding="utf-8")
        coarse_probe = read_json(RESULTS / "closed_loop_coarse_dynamic_order_probe.json")
        readiness = read_json(RESULTS / "coarse_first_external_readiness_gate.json")
        public_work = read_json(RESULTS / "closed_loop_true_dynamic_public_work_precision.json")
        strict_common = read_json(RESULTS / "closed_loop_true_dynamic_strict_common_reference.json")
    except Exception as exc:  # noqa: BLE001 - concise CLI failure.
        print(f"closed-loop dynamic-order closure contract validation: FAIL\n- {exc}")
        return 1

    checks.check(summary.get("schema") == "closed-loop-dynamic-order-closure-contract-v1", "schema changed")
    checks.check(summary.get("default_policy") == "coarse_first_no_default_1e-4", "default policy changed")
    checks.check(summary.get("coarse_step_sizes") == [0.1, 0.05, 0.025], "coarse step sizes changed")
    checks.check(math.isclose(float(summary.get("reference_h")), 0.0125), "reference h changed")
    checks.check(math.isclose(float(summary.get("t_end")), 0.1), "time horizon changed")
    checks.check(set(summary.get("models", [])) == MODELS, "model set changed")
    checks.check(summary.get("missing_dynamic_order_models", []) == [], "missing model set changed")
    checks.check(
        set(summary.get("public_work_precision_available_models", [])) == MODELS,
        "public work/precision available model set changed",
    )
    checks.check(summary.get("public_work_precision_available_count") == 2, "public work/precision count changed")
    checks.check(summary.get("public_work_precision_missing_models", []) == [], "public work/precision missing model set changed")
    checks.check(summary.get("public_work_precision_missing_count") == 0, "public work/precision missing count changed")
    checks.check(
        set(summary.get("strict_common_reference_available_models", [])) == MODELS,
        "strict common-reference available model set changed",
    )
    checks.check(summary.get("strict_common_reference_available_count") == 2, "strict common-reference available count changed")
    checks.check(summary.get("strict_common_reference_gap_models", []) == [], "strict common-reference gap model set changed")
    checks.check(summary.get("strict_common_reference_gap_count") == 0, "strict common-reference gap count changed")
    checks.check(summary.get("strict_common_reference_error_columns") is True, "strict common-reference flag changed")
    checks.check(summary.get("strict_common_reference_figure_available") is True, "strict common-reference figure marker changed")
    checks.check(summary.get("accepted_dynamic_order_count") == 2, "accepted local dynamic order count changed")
    checks.check(summary.get("true_dynamic_local_rows_available") == 2, "true dynamic local rows not available")
    checks.check(summary.get("true_dynamic_local_row_count") == 6, "true dynamic local row count changed")
    checks.check(summary.get("coarse_probe_ok_rows") == coarse_probe.get("ok_row_count") == 11, "coarse ok count changed")
    checks.check(summary.get("coarse_probe_row_count") == coarse_probe.get("row_count") == 12, "coarse row count changed")
    checks.check(
        summary.get("coarse_probe_public_failed_rows") == coarse_probe.get("public_failed_row_count") == 1,
        "coarse public failure count changed",
    )
    checks.check(
        summary.get("coarse_first_ready_examples") == readiness.get("coarse_same_window_ready_count") == 2,
        "coarse-first ready count changed",
    )
    checks.check(
        summary.get("coarse_first_dynamic_order_missing") == readiness.get("dynamic_order_missing_count") == 0,
        "coarse-first missing count changed",
    )
    checks.check(
        summary.get("coarse_first_public_work_precision_available")
        == readiness.get("public_work_precision_available_count")
        == public_work.get("public_work_precision_available_count")
        == 2,
        "coarse-first public work/precision availability changed",
    )
    checks.check(
        summary.get("coarse_first_public_work_precision_missing")
        == readiness.get("public_work_precision_missing_count")
        == public_work.get("public_work_precision_missing_count")
        == 0,
        "coarse-first public work/precision missing count changed",
    )
    checks.check(
        summary.get("coarse_first_strict_common_reference_gap")
        == readiness.get("strict_common_reference_gap_count")
        == 0,
        "coarse-first strict common-reference gap changed",
    )
    checks.check(
        summary.get("coarse_first_strict_common_reference_available")
        == readiness.get("strict_common_reference_available_count")
        == strict_common.get("strict_common_reference_available_count")
        == 2,
        "coarse-first strict common-reference availability changed",
    )
    checks.check(
        summary.get("coarse_first_strict_common_reference_figure_available")
        == readiness.get("strict_common_reference_figure_available")
        is True,
        "coarse-first strict common-reference figure marker changed",
    )
    checks.check(summary.get("stage_oracle_used") is False, "stage oracle overclaimed")
    checks.check(summary.get("convergence_sweep_run") is True, "convergence sweep marker changed")
    theorem = summary.get("method_order_theorem", {})
    checks.check(theorem.get("accepted_method") == "Gauss6/FullVA", "theorem method changed")
    checks.check(theorem.get("global_order") == 6, "theorem order changed")
    checks.check(theorem.get("finite_run_min_position_velocity_order_to_accept") == 5.0, "finite-run order threshold changed")
    checks.check(theorem.get("requires_non_floor_limited_position_velocity_errors") is True, "floor condition changed")
    checks.check(summary.get("full_tfe_stage_replacement_required_for_this_gate") is False, "full TFE incorrectly required")
    checks.check(summary.get("strict_public_policy_1e-4_required") is False, "strict 1e-4 incorrectly required")
    checks.check(summary.get("external_superiority_claim") is False, "external superiority incorrectly accepted")
    checks.check(summary.get("submission_ready") is False, "submission-ready incorrectly accepted")

    checks.check(len(rows) == 2, "expected one closure row per closed-loop model")
    checks.check({row.get("model") for row in rows} == MODELS, "CSV model set changed")
    for row in rows:
        model = row.get("model", "<missing>")
        checks.check(
            row.get("current_status") == "local_true_dynamic_order_public_work_and_strict_common_reference_available",
            f"{model} status changed",
        )
        checks.check(row.get("accepted_dynamic_order") == "true", f"{model} local dynamic order not accepted")
        checks.check(
            row.get("current_local_row_kind") == "non_oracle_true_dynamic_gauss6_fullva",
            f"{model} local row kind changed",
        )
        checks.check(
            row.get("current_public_baseline_kind") == "strict_common_reference_available_v047_exact_endpoint",
            f"{model} public baseline kind changed",
        )
        checks.check(row.get("true_dynamic_local_rows_available") == "3", f"{model} true dynamic row count changed")
        checks.check(row.get("position_floor_blocks_acceptance") == "false", f"{model} position-floor boundary changed")
        checks.check(row.get("local_velocity_residual_evidence") == "true", f"{model} velocity evidence changed")
        checks.check(row.get("local_acceleration_residual_evidence") == "true", f"{model} acceleration evidence changed")
        checks.check(as_float(row.get("finest_vel_error_ratio_vs_rA")) < 1.0e-4, f"{model} velocity ratio changed")
        checks.check(as_float(row.get("finest_acc_error_ratio_vs_rA")) < 1.0e-4, f"{model} acceleration ratio changed")
        checks.check(as_float(row.get("max_dynamics_residual_norm")) < 1.0e-12, f"{model} dynamics residual changed")
        checks.check(
            row.get("required_next_artifact") == "publication_quality_figure_integration_and_broader_external_suite_closure",
            f"{model} next artifact changed",
        )
        checks.check(row.get("default_policy") == "coarse_first_no_default_1e-4", f"{model} default policy changed")
        checks.check(row.get("external_superiority_claim_allowed") == "false", f"{model} superiority boundary changed")

    checks.check({row.get("public_failed_rows") for row in rows} == {"0"}, "public failure count changed")

    for token in [
        "Closed-Loop Dynamic-Order Closure Contract",
        "local dynamic order and strict common-reference rows closed",
        "Public work/precision available examples",
        "Strict common-reference gap examples",
        "Theorem order for a true `Gauss6/FullVA` dynamic trajectory row: `6`",
        "Local true dynamic trajectory path",
        "External comparison path",
        "Residual-to-error theorem path",
        "No `1e-4` row is required",
    ]:
        checks.check(token in report, f"report missing token: {token}")

    if checks.errors:
        print("closed-loop dynamic-order closure contract validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("closed-loop dynamic-order closure contract validation: PASS")
    print("missing_dynamic_order_models=none")
    print("accepted_dynamic_order=2")
    print("true_dynamic_local_rows=2")
    print("public_work_precision_available=2")
    print("public_work_precision_missing=0")
    print("strict_common_reference_available=2")
    print("strict_common_reference_gap=0")
    print("strict_common_reference_figure_available=True")
    print("theorem_order=6")
    print("default_1e-4=False")
    print("external_superiority_claim=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
