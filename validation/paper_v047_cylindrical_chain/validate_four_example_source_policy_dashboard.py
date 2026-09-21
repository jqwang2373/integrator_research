#!/usr/bin/env python3
"""Validate the four-example source-policy dashboard."""

from __future__ import annotations

import json
from pathlib import Path


PAPER = Path(__file__).resolve().parent
ROOT = PAPER.parent
V048_RESULTS = ROOT.parent / "numerics" / "v048_cross_paper_same_test_benchmarks" / "results"
EXAMPLES = ["single_pendulum", "double_pendulum", "four_link", "slider_crank"]


class Checks:
    def __init__(self) -> None:
        self.errors: list[str] = []

    def check(self, condition: bool, message: str) -> None:
        if not condition:
            self.errors.append(message)


def read_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def main() -> int:
    checks = Checks()
    try:
        dashboard = read_json(PAPER / "FOUR_EXAMPLE_SOURCE_POLICY_DASHBOARD.json")
        matrix = read_json(PAPER / "PAPER_NUMERICAL_RESULT_MATRIX.json")
        closure = read_json(V048_RESULTS / "closed_loop_dynamic_order_closure_contract.json")
        newton_order = read_json(V048_RESULTS / "closed_loop_true_dynamic_newton_coarse_order.json")
        md = (PAPER / "FOUR_EXAMPLE_SOURCE_POLICY_DASHBOARD.md").read_text(encoding="utf-8")
    except Exception as exc:  # noqa: BLE001 - CLI validator reports parse/read failures.
        print(f"four-example source-policy dashboard validation: FAIL\n- {exc}")
        return 1

    rows = dashboard.get("rows", [])
    matrix_rows = matrix.get("rows", [])
    checks.check(dashboard.get("schema") == "four-example-source-policy-dashboard-v1", "dashboard schema changed")
    checks.check(
        dashboard.get("status") == "all_four_examples_checked_source_policy_dynamic_order_open",
        "dashboard status changed",
    )
    checks.check(
        dashboard.get("local_dynamic_order_status")
        == "accepted_method_dynamic_order_2_of_4_source_policy_external_open",
        "dashboard local dynamic-order status changed",
    )
    checks.check(
        dashboard.get("local_evidence_coverage_status")
        == "all_four_examples_local_evidence_present_source_policy_dynamic_order_open",
        "dashboard local evidence-coverage status changed",
    )
    checks.check(dashboard.get("examples") == EXAMPLES, "dashboard examples are not the four canonical examples")
    checks.check(dashboard.get("row_count") == 4, "dashboard must have one row per example")
    checks.check(dashboard.get("all_four_examples_checked") is True, "dashboard does not confirm all four examples")
    checks.check(dashboard.get("local_evidence_coverage_examples") == 4, "local evidence coverage is not 4/4")
    checks.check(dashboard.get("local_dynamic_order_closed_examples") == 2, "local dynamic-order count is not 2/4")
    checks.check(
        dashboard.get("local_evidence_coverage_example_names") == EXAMPLES,
        "local evidence coverage examples changed",
    )
    checks.check(
        dashboard.get("local_dynamic_order_closed_example_names") == ["single_pendulum", "double_pendulum"],
        "local dynamic-order examples changed",
    )
    checks.check(
        dashboard.get("method_side_order_gate_examples") == ["single_pendulum", "double_pendulum"],
        "method-side order-gate examples changed",
    )
    checks.check(
        dashboard.get("accepted_method_dynamic_order_examples") == ["single_pendulum", "double_pendulum"],
        "accepted method dynamic-order examples changed",
    )
    checks.check(
        dashboard.get("accepted_method_dynamic_order_example_count") == 2,
        "accepted method dynamic-order count changed",
    )
    checks.check(
        dashboard.get("mechanism_coverage_examples") == ["four_link", "slider_crank"],
        "mechanism-coverage examples changed",
    )
    checks.check(dashboard.get("mechanism_coverage_example_count") == 2, "mechanism-coverage count changed")
    checks.check(
        dashboard.get("closed_loop_coarse_dynamics_diagnostic_examples") == 2,
        "closed-loop coarse-dynamics diagnostic count changed",
    )
    checks.check(
        dashboard.get("closed_loop_coarse_dynamics_diagnostic_example_names") == ["four_link", "slider_crank"],
        "closed-loop coarse-dynamics diagnostic examples changed",
    )
    checks.check(
        dashboard.get("closed_loop_true_dynamic_order_closed_examples")
        == closure.get("accepted_dynamic_order_count")
        == 2,
        "closed-loop true-dynamic closure count changed",
    )
    checks.check(
        dashboard.get("closed_loop_true_dynamic_order_closed_example_names")
        == closure.get("models")
        == ["four_link", "slider_crank"],
        "closed-loop true-dynamic closure models changed",
    )
    checks.check(
        dashboard.get("closed_loop_true_dynamic_step_sizes")
        == closure.get("coarse_step_sizes")
        == [0.1, 0.05, 0.025],
        "closed-loop true-dynamic step sizes changed",
    )
    checks.check(dashboard.get("closed_loop_true_dynamic_reference_h") == 0.0125, "closed-loop reference h changed")
    checks.check(dashboard.get("closed_loop_true_dynamic_stage_oracle_used") is False, "stage oracle boundary changed")
    checks.check(dashboard.get("closed_loop_true_dynamic_rows") == 6, "closed-loop true-dynamic row count changed")
    checks.check(dashboard.get("common_reference_cells") == len(matrix_rows) == 44, "common-reference cell count changed")
    checks.check(dashboard.get("common_reference_nonlocal_cells") == 40, "nonlocal common-reference count changed")
    checks.check(dashboard.get("common_reference_local_order_wins") == 40, "local order wins changed")
    checks.check(dashboard.get("common_reference_local_error_wins") == 40, "local error wins changed")
    checks.check(dashboard.get("nonlocal_source_policy_closed_rows") == 0, "source-policy closed rows must remain 0")
    checks.check(
        dashboard.get("accepted_source_policy_dynamic_order_examples") == 0,
        "accepted source-policy dynamic-order examples must remain 0",
    )
    checks.check(
        dashboard.get("source_policy_external_superiority_allowed") is False,
        "dashboard must not allow external superiority",
    )
    checks.check(dashboard.get("paper_direct_error_superiority_allowed") is False, "direct error claim must be false")
    checks.check(dashboard.get("default_1e_4_required") is False, "default 1e-4 should remain disabled")
    checks.check(dashboard.get("heavy_numerical_run_invoked") is False, "heavy numerical run should not be invoked")

    seen = [row.get("example") for row in rows if isinstance(row, dict)]
    checks.check(seen == EXAMPLES, "row examples are not in canonical order")
    for row in rows:
        if not isinstance(row, dict):
            checks.check(False, "dashboard row is not a JSON object")
            continue
        example = row.get("example")
        checks.check(row.get("common_reference_nonlocal_rows") == 10, f"{example} nonlocal row count changed")
        checks.check(row.get("common_reference_local_order_wins") == 10, f"{example} order wins changed")
        checks.check(row.get("common_reference_local_error_wins") == 10, f"{example} error wins changed")
        checks.check(row.get("nonlocal_source_policy_closed_rows") == 0, f"{example} source-policy closure changed")
        checks.check(
            row.get("nonlocal_strict_external_error_claim_rows") == 0,
            f"{example} strict external error rows changed",
        )
        checks.check(
            row.get("accepted_source_policy_dynamic_order") is False,
            f"{example} must not be source-policy dynamic-order accepted",
        )
        checks.check(isinstance(row.get("local_dynamic_order_layer"), str), f"{example} missing local order layer")
        if example in {"single_pendulum", "double_pendulum"}:
            checks.check(row.get("local_dynamic_order_accepted") is True, f"{example} local dynamic order not accepted")
            checks.check(isinstance(row.get("local_dynamic_order_artifact"), str), f"{example} missing local order artifact")
            checks.check(row.get("local_dynamic_order_min_primary_order") is not None, f"{example} missing local min order")
        else:
            checks.check(row.get("local_dynamic_order_accepted") is False, f"{example} overclaims local dynamic order")
            checks.check(row.get("mechanism_coverage_candidate") is True, f"{example} missing mechanism coverage")
            checks.check(
                row.get("closed_loop_coarse_dynamics_diagnostic") is True,
                f"{example} missing coarse-dynamics diagnostic marker",
            )
        checks.check(isinstance(row.get("source_policy_status"), str) and row["source_policy_status"], f"{example} missing status")

    by_example = {row.get("example"): row for row in rows if isinstance(row, dict)}
    checks.check(
        by_example.get("single_pendulum", {}).get("local_dynamic_order_layer") == "method_side_order_gate",
        "single local order layer changed",
    )
    checks.check(
        by_example.get("double_pendulum", {}).get("local_dynamic_order_layer") == "method_side_order_gate",
        "double local order layer changed",
    )
    for model in ["four_link", "slider_crank"]:
        row = by_example.get(model, {})
        summary = newton_order.get("model_summaries", {}).get(model, {})
        checks.check(
            row.get("local_dynamic_order_layer") == "closed_loop_coarse_dynamics_diagnostic",
            f"{model} local order layer changed",
        )
        checks.check(
            row.get("local_dynamic_order_scope") == "mechanism_coverage_coarse_dynamics_diagnostic_not_dynamic_order",
            f"{model} local order scope changed",
        )
        checks.check(
            row.get("local_dynamic_order_primary_orders", {}).get("velocity")
            == summary.get("vel_observed_order"),
            f"{model} velocity order not carried from v048",
        )

    for token in [
        "Four-Example Source-Policy Dashboard",
        "single_pendulum",
        "double_pendulum",
        "four_link",
        "slider_crank",
        "Local evidence coverage examples: `4/4`",
        "Accepted method dynamic-order examples: `2/4` (`single_pendulum, double_pendulum`)",
        "Closed-loop coarse-dynamics diagnostics: `2/2`",
        "Source-policy dynamic-order examples: `0/4`",
        "External-superiority claim allowed: `False`",
        "Accepted method dynamic-order evidence is the single/double pendulum layer",
        "not a four-example dynamic-order claim",
    ]:
        checks.check(token in md, f"dashboard markdown missing token: {token}")

    if checks.errors:
        print("four-example source-policy dashboard validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("four-example source-policy dashboard validation: PASS")
    print("examples=single_pendulum,double_pendulum,four_link,slider_crank")
    print("local_evidence_coverage_examples=4/4")
    print("accepted_method_dynamic_order_examples=2/4")
    print("source_policy_dynamic_order_examples=0/4")
    print("common_reference_nonlocal_order_error_wins=40/40,40/40")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
