#!/usr/bin/env python3
"""Validate the paper-core result consolidation."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent


class Checks:
    def __init__(self) -> None:
        self.errors: list[str] = []

    def check(self, condition: bool, message: str) -> None:
        if not condition:
            self.errors.append(message)


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def main() -> int:
    checks = Checks()
    try:
        audit = read_json(PAPER / "PAPER_CORE_RESULT_CONSOLIDATION.json")
        md = (PAPER / "PAPER_CORE_RESULT_CONSOLIDATION.md").read_text(encoding="utf-8")
        matrix = read_json(PAPER / "PAPER_NUMERICAL_RESULT_MATRIX.json")
        proof = read_json(PAPER / "PROOF_CLOSURE_MANIFEST.json")
    except Exception as exc:  # noqa: BLE001
        print(f"paper core result consolidation validation: FAIL\n- {exc}")
        return 1

    checks.check(audit.get("schema") == "paper-core-result-consolidation-v1", "schema changed")
    checks.check(
        audit.get("status") == "paper_core_results_consolidated_replay_only",
        "status changed",
    )
    checks.check(audit.get("submission_ready") is False, "submission-ready overclaimed")
    execution = audit.get("execution_policy", {})
    checks.check(execution.get("read_only_existing_artifacts") is True, "read-only marker missing")
    checks.check(execution.get("experiments_launched") is False, "experiment launch overclaimed")
    checks.check(execution.get("run_v047_invoked") is False, "run_v047 marker changed")
    checks.check(execution.get("run_v048_invoked") is False, "run_v048 marker changed")

    local = audit.get("four_example_local_order", {})
    checks.check(local.get("examples_closed") == local.get("examples_total") == 4, "four-example closure changed")
    rows = {row.get("example"): row for row in local.get("rows", [])}
    checks.check(set(rows) == {"single_pendulum", "double_pendulum", "four_link", "slider_crank"}, "example set changed")
    for example, source_row in matrix.get("per_example", {}).items():
        row = rows.get(example, {})
        checks.check(
            row.get("velocity_order") == source_row.get("local_velocity_order"),
            f"{example} velocity order not traced to matrix",
        )
        checks.check(
            row.get("finest_velocity_error") == source_row.get("local_finest_velocity_error"),
            f"{example} finest error not traced to matrix",
        )

    common = audit.get("common_reference_comparison", {})
    checks.check(common.get("velocity_order_wins") == common.get("velocity_order_comparisons") == 40, "order wins changed")
    checks.check(common.get("velocity_error_wins") == common.get("velocity_error_comparisons") == 40, "error wins changed")
    checks.check(common.get("source_policy_reproduction") is False, "source-policy reproduction overclaimed")
    checks.check(common.get("external_superiority_claim_allowed") is False, "external superiority overclaimed")

    closed = audit.get("closed_loop_true_dynamic_order", {})
    checks.check(closed.get("accepted_dynamic_order_count") == 2, "closed-loop candidate count changed")
    checks.check(closed.get("ok_row_count") == closed.get("row_count") == 6, "closed-loop row count changed")
    checks.check(closed.get("stage_oracle_used") is False, "stage oracle boundary changed")
    closed_rows = {row.get("example"): row for row in closed.get("rows", [])}
    for example in ["four_link", "slider_crank"]:
        row = closed_rows.get(example, {})
        checks.check(row.get("accepted_coarse_true_dynamic_order_candidate") is True, f"{example} not accepted")
        checks.check(float(row.get("min_primary_order", 0.0)) > 5.9, f"{example} primary order too low")

    figures = audit.get("paper_figures", {})
    checks.check(figures.get("core_figure_count") == 5, "core figure count changed")
    checks.check(figures.get("all_core_figures_exist") is True, "core figures missing")

    proof_boundary = audit.get("proof_boundary", {})
    checks.check(proof_boundary.get("proof_gap_closed") is True, "proof gap direct closure missing")
    checks.check(
        proof_boundary.get("proof_gap_closed_scope")
        == "direct_residual_bridge_kantorovich_route_closed_primitive_taylor_conditional_schema_open",
        "proof gap closure scope missing or changed",
    )
    checks.check(
        "schema-compatible shorthand for direct_pc2_proof_gap_closed"
        in proof_boundary.get("proof_gap_closed_reading_rule", ""),
        "proof-gap reading rule missing direct-PC2 scope",
    )
    schema_compat = proof_boundary.get("schema_compatibility", {})
    checks.check(
        schema_compat.get("legacy_key") == "proof_gap_closed"
        and schema_compat.get("legacy_key_retained_for_schema_compatibility") is True
        and schema_compat.get("preferred_key") == "direct_pc2_proof_gap_closed",
        "proof-gap schema compatibility missing or changed",
    )
    checks.check(
        proof_boundary.get("direct_pc2_proof_gap_closed") is True,
        "direct PC2 proof gap closure marker missing",
    )
    checks.check(
        proof_boundary.get("direct_residual_bridge_submission_standard_scope")
        == (
            "satisfied only for the active direct residual-bridge/Kantorovich "
            "PC2 route; not a primitive 162-term Taylor closure and not a "
            "global submission-ready proof package"
        ),
        "direct residual-bridge standard scope missing or changed",
    )
    checks.check(
        proof_boundary.get("primitive_162_term_taylor_route_closed") is False,
        "primitive 162-term Taylor route overclaimed",
    )
    checks.check(
        proof_boundary.get("stage_residual_O_h7_implementation_defect_proved") is True,
        "dynamic defect direct proof missing",
    )
    checks.check(
        proof_boundary.get("stage_residual_O_h7_implementation_defect_scope")
        == "implementation-path direct residual bridge at the lifted Gauss stage",
        "stage residual defect proof scope missing or changed",
    )
    checks.check(
        proof_boundary.get("primitive_lane_open_dynamic_rows")
        == proof_boundary.get("open_dynamic_rows")
        == proof.get("evidence_summary", {}).get("open_dynamic_rows")
        == 36,
        "open dynamic row count changed",
    )
    checks.check(
        proof_boundary.get("primitive_lane_open_dynamic_rows_scope")
        == proof.get("evidence_summary", {}).get("open_dynamic_rows_scope")
        == "symbolic_primitive_certificate_route_not_active_direct_pc2",
        "primitive-route dynamic row scope changed",
    )
    checks.check(
        proof_boundary.get("open_dynamic_rows_scope")
        == "legacy alias for primitive_lane_open_dynamic_rows; not an active direct-PC2 gap",
        "legacy open dynamic row scope missing",
    )
    checks.check(
        proof_boundary.get("newton_euler_row_obligation_links")
        == proof.get("evidence_summary", {}).get("newton_euler_row_obligation_links")
        == 180,
        "Newton-Euler obligation links changed",
    )

    review = audit.get("review_and_reproducibility", {})
    checks.check(review.get("result_to_manuscript_traceability_closed") is True, "traceability should be closed")
    checks.check(review.get("review_agent_submission_standard_met") is False, "review agent overclaimed")
    checks.check(review.get("minimal_package_ready") is False, "minimal package readiness overclaimed")

    for token in [
        "Status: **paper core results consolidated; replay-only, no experiment campaign**.",
        "Four-example local order: `4/4`.",
        "Common-reference order/error wins: `40/40` and `40/40`.",
        "Closed-loop coarse dynamics candidates: `2/2`.",
        "Direct PC2 proof gap closed: `True`.",
        "Direct PC2 proof-gap scope: `direct_residual_bridge_kantorovich_route_closed_primitive_taylor_conditional_schema_open`.",
        "Schema-only compatibility key `proof_gap_closed` retained: `True`; reader-facing proof status should use `direct_pc2_proof_gap_closed`.",
        "Primitive 162-term Taylor route closed: `False`.",
        "Experiments launched: `False`.",
        "Forbidden: strict source-paper policy external superiority",
    ]:
        checks.check(token in md, f"markdown missing token: {token}")

    if checks.errors:
        print("paper core result consolidation validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("paper core result consolidation validation: PASS")
    print("four_example_local_order=4/4")
    print("common_reference_order_error_wins=40/40,40/40")
    print("closed_loop_coarse_dynamics_candidates=2/2")
    print("experiments_launched=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
