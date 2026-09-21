#!/usr/bin/env python3
"""Build a four-example source-policy dashboard for submission review.

The all-method matrix already carries every order/error value. This dashboard
reduces it to one row per example so the review agent cannot accidentally
reason from a single pendulum row or from aggregate counts alone.
"""

from __future__ import annotations

import json
from pathlib import Path


PAPER = Path(__file__).resolve().parent
ROOT = PAPER.parent
V048_RESULTS = ROOT.parent / "numerics" / "v048_cross_paper_same_test_benchmarks" / "results"
EXAMPLES = ["single_pendulum", "double_pendulum", "four_link", "slider_crank"]


def read_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def fmt(value: object) -> str:
    if value is None:
        return "nan"
    if isinstance(value, (int, float)):
        return f"{value:.3e}" if abs(value) < 1e-2 or abs(value) >= 1e3 else f"{value:.3f}"
    return str(value)


def status_for_example(example: str, source_policy_progress: dict) -> str:
    local = source_policy_progress.get("ra2021_local_gauss6_rows", {})
    if example == "single_pendulum":
        if local.get("single_public_policy_rows_completed") and local.get("single_public_policy_order_floor_limited"):
            return "single public-policy rows completed but reference-floor limited; not accepted external dynamic order"
        return "single public-policy rows not closed"
    if example == "double_pendulum":
        policy = local.get("double_current_policy", "unknown_double_policy")
        if local.get("double_public_policy_rows_completed") is False:
            return f"{policy}; not the public policy dynamic-order campaign"
        return "double public-policy rows completed"
    if example in {"four_link", "slider_crank"}:
        kind = local.get("closed_loop_row_kind", "unknown_closed_loop_row_kind")
        if local.get("closed_loop_public_horizon_rows_completed"):
            return (
                f"source-policy public-horizon rows completed as {kind}; separate closed-loop "
                "coarse-dynamics diagnostic rows are available, but not accepted as external "
                "source-policy dynamic order"
            )
        return "closed-loop public-horizon rows not closed"
    raise ValueError(f"unexpected example {example}")


def local_dynamic_order_evidence(example: str, order_gate: dict, newton_order: dict) -> dict:
    gate_examples = order_gate.get("examples", {})
    gate_example = gate_examples.get(example, {}) if isinstance(gate_examples, dict) else {}
    accepted_gate_examples = set(order_gate.get("accepted_dynamic_order_examples", []))
    if example in accepted_gate_examples:
        return {
            "local_dynamic_order_accepted": True,
            "local_dynamic_order_layer": "method_side_order_gate",
            "local_dynamic_order_scope": gate_example.get("method_scope", gate_example.get("role")),
            "local_dynamic_order_artifact": "ORDER_ACCEPTANCE_GATE.json",
            "local_dynamic_order_min_primary_order": gate_example.get("min_observed_order"),
            "local_dynamic_order_primary_orders": {},
            "mechanism_coverage_candidate": False,
            "closed_loop_coarse_dynamics_diagnostic": False,
        }

    model_summaries = newton_order.get("model_summaries", {})
    model = model_summaries.get(example, {}) if isinstance(model_summaries, dict) else {}
    if model.get("accepted_dynamic_order_candidate") is True:
        return {
            "local_dynamic_order_accepted": False,
            "local_dynamic_order_layer": "closed_loop_coarse_dynamics_diagnostic",
            "local_dynamic_order_scope": "mechanism_coverage_coarse_dynamics_diagnostic_not_dynamic_order",
            "local_dynamic_order_artifact": (
                "v048_cross_paper_same_test_benchmarks/results/"
                "closed_loop_true_dynamic_newton_coarse_order.json"
            ),
            "local_dynamic_order_min_primary_order": model.get("min_primary_order"),
            "local_dynamic_order_primary_orders": {
                "position": model.get("pos_observed_order"),
                "orientation": model.get("orientation_observed_order"),
                "velocity": model.get("vel_observed_order"),
                "omega": model.get("omega_observed_order"),
            },
            "mechanism_coverage_candidate": True,
            "closed_loop_coarse_dynamics_diagnostic": True,
        }

    return {
        "local_dynamic_order_accepted": False,
        "local_dynamic_order_layer": "not_closed",
        "local_dynamic_order_scope": gate_example.get("role", "unknown"),
        "local_dynamic_order_artifact": None,
        "local_dynamic_order_min_primary_order": None,
        "local_dynamic_order_primary_orders": {},
        "mechanism_coverage_candidate": False,
        "closed_loop_coarse_dynamics_diagnostic": False,
    }


def build_dashboard() -> dict:
    matrix = read_json(PAPER / "PAPER_NUMERICAL_RESULT_MATRIX.json")
    order_gate = read_json(PAPER / "ORDER_ACCEPTANCE_GATE.json")
    reconciliation = read_json(PAPER / "EXTERNAL_CASE_EVIDENCE_RECONCILIATION.json")
    newton_order = read_json(V048_RESULTS / "closed_loop_true_dynamic_newton_coarse_order.json")
    closure_contract = read_json(V048_RESULTS / "closed_loop_dynamic_order_closure_contract.json")

    rows = matrix.get("rows", [])
    if not isinstance(rows, list):
        raise ValueError("PAPER_NUMERICAL_RESULT_MATRIX rows is not a list")

    accepted_dynamic = set(order_gate.get("accepted_dynamic_order_examples", []))
    coverage_only = set(order_gate.get("coverage_only_examples", []))
    source_policy_progress = reconciliation.get("source_policy_progress", {})

    example_rows = []
    for example in EXAMPLES:
        local_rows = [row for row in rows if row.get("example") == example and row.get("method") == "local_Gauss6_FullVA"]
        if len(local_rows) != 1:
            raise ValueError(f"expected one local row for {example}, found {len(local_rows)}")
        local = local_rows[0]
        nonlocal_rows = [row for row in rows if row.get("example") == example and row.get("method") != "local_Gauss6_FullVA"]
        order_wins = sum(1 for row in nonlocal_rows if row.get("local_velocity_order_win") is True)
        error_wins = sum(1 for row in nonlocal_rows if row.get("local_finest_velocity_error_win") is True)
        source_policy_closed = sum(1 for row in nonlocal_rows if row.get("source_policy_closed") is True)
        strict_error_rows = sum(1 for row in nonlocal_rows if row.get("strict_external_error_claim_allowed") is True)
        flagged_rows = sum(1 for row in nonlocal_rows if "source_policy_not_closed" in row.get("issues", []))
        role = "accepted_dynamic_order_example" if example in accepted_dynamic else "coverage_only_example"
        if example not in accepted_dynamic and example not in coverage_only:
            role = "not_classified"
        local_order = local_dynamic_order_evidence(example, order_gate, newton_order)

        example_rows.append(
            {
                "example": example,
                "local_velocity_order": local.get("velocity_order"),
                "local_finest_velocity_error": local.get("finest_velocity_error"),
                "local_position_order": local.get("position_order"),
                "local_finest_position_error": local.get("finest_position_error"),
                "common_reference_nonlocal_rows": len(nonlocal_rows),
                "common_reference_local_order_wins": order_wins,
                "common_reference_local_error_wins": error_wins,
                "nonlocal_source_policy_closed_rows": source_policy_closed,
                "nonlocal_strict_external_error_claim_rows": strict_error_rows,
                "nonlocal_source_policy_flagged_rows": flagged_rows,
                "accepted_internal_role": role,
                **local_order,
                "accepted_source_policy_dynamic_order": False,
                "source_policy_status": status_for_example(example, source_policy_progress),
            }
        )

    total_nonlocal = sum(row["common_reference_nonlocal_rows"] for row in example_rows)
    local_dynamic_closed = [row["example"] for row in example_rows if row["local_dynamic_order_accepted"]]
    local_evidence_coverage = [
        row["example"]
        for row in example_rows
        if row["local_dynamic_order_accepted"] or row.get("mechanism_coverage_candidate") is True
    ]
    accepted_method_dynamic = list(order_gate.get("accepted_dynamic_order_examples", []))
    mechanism_coverage = list(order_gate.get("coverage_only_examples", []))
    dashboard = {
        "schema": "four-example-source-policy-dashboard-v1",
        "status": "all_four_examples_checked_source_policy_dynamic_order_open",
        "local_evidence_coverage_status": "all_four_examples_local_evidence_present_source_policy_dynamic_order_open",
        "local_evidence_coverage_examples": len(local_evidence_coverage),
        "local_evidence_coverage_example_names": local_evidence_coverage,
        "accepted_method_dynamic_order_examples": accepted_method_dynamic,
        "accepted_method_dynamic_order_example_count": len(accepted_method_dynamic),
        "mechanism_coverage_examples": mechanism_coverage,
        "mechanism_coverage_example_count": len(mechanism_coverage),
        "local_dynamic_order_status": "accepted_method_dynamic_order_2_of_4_source_policy_external_open",
        "examples": EXAMPLES,
        "row_count": len(example_rows),
        "all_four_examples_checked": set(item["example"] for item in example_rows) == set(EXAMPLES),
        "local_dynamic_order_closed_examples": len(local_dynamic_closed),
        "local_dynamic_order_closed_example_names": local_dynamic_closed,
        "method_side_order_gate_examples": list(order_gate.get("accepted_dynamic_order_examples", [])),
        "closed_loop_coarse_dynamics_diagnostic_examples": len(mechanism_coverage),
        "closed_loop_coarse_dynamics_diagnostic_example_names": mechanism_coverage,
        "closed_loop_true_dynamic_order_closed_examples": closure_contract.get("accepted_dynamic_order_count"),
        "closed_loop_true_dynamic_order_closed_example_names": closure_contract.get("models"),
        "closed_loop_true_dynamic_order_artifact": (
            "v048_cross_paper_same_test_benchmarks/results/"
            "closed_loop_dynamic_order_closure_contract.json"
        ),
        "closed_loop_true_dynamic_step_sizes": closure_contract.get("coarse_step_sizes"),
        "closed_loop_true_dynamic_reference_h": closure_contract.get("reference_h"),
        "closed_loop_true_dynamic_stage_oracle_used": closure_contract.get("stage_oracle_used"),
        "closed_loop_true_dynamic_rows": closure_contract.get("true_dynamic_local_row_count"),
        "common_reference_cells": len(rows),
        "common_reference_nonlocal_cells": total_nonlocal,
        "common_reference_local_order_wins": sum(row["common_reference_local_order_wins"] for row in example_rows),
        "common_reference_local_error_wins": sum(row["common_reference_local_error_wins"] for row in example_rows),
        "nonlocal_source_policy_closed_rows": sum(row["nonlocal_source_policy_closed_rows"] for row in example_rows),
        "accepted_source_policy_dynamic_order_examples": sum(
            1 for row in example_rows if row["accepted_source_policy_dynamic_order"]
        ),
        "source_policy_external_superiority_allowed": False,
        "paper_direct_error_superiority_allowed": False,
        "default_1e_4_required": reconciliation.get("execution_policy", {}).get("default_1e_4_required"),
        "heavy_numerical_run_invoked": reconciliation.get("execution_policy", {}).get("heavy_numerical_run_invoked"),
        "interpretation": (
            "The bounded common-reference matrix covers all four examples and all runnable methods. "
            "It supports the finite-grid common-reference order/error diagnostic. "
            "Separately, all four examples now have local evidence coverage: "
            "single/double from accepted method-side dynamic-order rows and four/slider from "
            "non-oracle closed-loop coarse-dynamics diagnostic rows. "
            "This still does not close source-policy external dynamic-order evidence for any of the four examples "
            "and does not allow an external-superiority claim."
        ),
        "rows": example_rows,
    }
    return dashboard


def write_markdown(dashboard: dict) -> str:
    lines = [
        "# Four-Example Source-Policy Dashboard",
        "",
        f"Status: **{dashboard['status']}**.",
        "",
        f"- Examples checked: `{', '.join(dashboard['examples'])}`.",
        f"- Common-reference cells: `{dashboard['common_reference_cells']}`.",
        f"- Common-reference nonlocal order/error wins: `{dashboard['common_reference_local_order_wins']}/{dashboard['common_reference_nonlocal_cells']}` and `{dashboard['common_reference_local_error_wins']}/{dashboard['common_reference_nonlocal_cells']}`.",
        f"- Local evidence coverage examples: `{dashboard['local_evidence_coverage_examples']}/4`.",
        f"- Accepted method dynamic-order examples: `{dashboard['accepted_method_dynamic_order_example_count']}/4` (`{', '.join(dashboard['accepted_method_dynamic_order_examples'])}`).",
        f"- Closed-loop coarse-dynamics diagnostics: `{dashboard['closed_loop_true_dynamic_order_closed_examples']}/2` at h=`{dashboard['closed_loop_true_dynamic_step_sizes']}`.",
        f"- Source-policy dynamic-order examples: `{dashboard['accepted_source_policy_dynamic_order_examples']}/4`.",
        f"- External-superiority claim allowed: `{dashboard['source_policy_external_superiority_allowed']}`.",
        "",
        "| Example | Local evidence layer | Local velocity order/error | Common-reference nonlocal wins | Accepted source-policy dynamic order | Source-policy status |",
        "|---|---|---:|---:|---:|---|",
    ]
    for row in dashboard["rows"]:
        lines.append(
            "| "
            + row["example"]
            + " | "
            + f"{row['local_dynamic_order_layer']} ({fmt(row['local_dynamic_order_min_primary_order'])})"
            + " | "
            + f"{fmt(row['local_velocity_order'])} / {fmt(row['local_finest_velocity_error'])}"
            + " | "
            + f"{row['common_reference_local_order_wins']}/{row['common_reference_nonlocal_rows']} order, {row['common_reference_local_error_wins']}/{row['common_reference_nonlocal_rows']} error"
            + " | "
            + str(row["accepted_source_policy_dynamic_order"])
            + " | "
            + row["source_policy_status"]
            + " |"
        )
    lines.extend(
        [
            "",
            "Reading rule: this dashboard has three layers. Accepted method dynamic-order evidence is the single/double pendulum layer; closed-loop mechanism evidence is the four-link/slider-crank layer; source-policy external dynamic-order closure is still `0/4`. The local evidence coverage count is `4/4`, but that is not a four-example dynamic-order claim and does not allow external superiority.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    dashboard = build_dashboard()
    (PAPER / "FOUR_EXAMPLE_SOURCE_POLICY_DASHBOARD.json").write_text(
        json.dumps(dashboard, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (PAPER / "FOUR_EXAMPLE_SOURCE_POLICY_DASHBOARD.md").write_text(write_markdown(dashboard), encoding="utf-8")
    print("four_example_source_policy_dashboard=written")
    print(f"local_evidence_coverage_examples={dashboard['local_evidence_coverage_examples']}/4")
    print(f"accepted_method_dynamic_order_examples={dashboard['accepted_method_dynamic_order_example_count']}/4")
    print(f"source_policy_dynamic_order_examples={dashboard['accepted_source_policy_dynamic_order_examples']}/4")
    print(f"common_reference_nonlocal_cells={dashboard['common_reference_nonlocal_cells']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
