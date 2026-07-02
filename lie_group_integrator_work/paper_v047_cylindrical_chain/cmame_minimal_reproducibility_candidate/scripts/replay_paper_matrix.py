#!/usr/bin/env python3
"""Replay consistency checks for the CMAME minimal reproducibility candidate."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


def read_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def main() -> int:
    errors: list[str] = []
    matrix = read_json(DATA / "PAPER_NUMERICAL_RESULT_MATRIX.json")
    review = read_json(DATA / "CMAME_REVIEW_AGENT_REPORT.json")
    proof = read_json(DATA / "PROOF_CLOSURE_MANIFEST.json")
    traceability = read_json(DATA / "RESULT_TO_MANUSCRIPT_TRACEABILITY_AUDIT.json")
    dashboard = read_json(DATA / "FOUR_EXAMPLE_SOURCE_POLICY_DASHBOARD.json")
    newton = read_json(DATA / "NEWTON_EULER_SYMBOLIC_TARGET_AUDIT.json")

    with (DATA / "PAPER_NUMERICAL_RESULT_MATRIX.csv").open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    expected_examples = {"single_pendulum", "double_pendulum", "four_link", "slider_crank"}
    expected_methods = {
        "local_Gauss6_FullVA",
        "hi2022_rA",
        "hi2022_rA_half",
        "ra2021_rA",
        "ra2021_reps",
        "ra2021_rp",
        "tfe2026_Newmark_beta",
        "tfe2026_TFE_m1",
        "tfe2026_TFE_m2",
        "tfe2026_trapezoidal",
        "vp2024_coordinate_partitioning_rA",
    }
    expected_blocker_open = {"OC4": True, "OC6": True, "OC12": True}
    expected_blocker_decisions = {
        "OC4": "remain_open_ready_for_authorized_execution_not_executed_not_promoted",
        "OC6": "remain_open_no_positive_source_equivalent_artifact",
        "OC12": "remain_partial_narrowed_replay_ready_full_source_policy_archive_not_ready",
    }
    expected_blocker_allowed = {"OC4": False, "OC6": False, "OC12": False}
    expected_open_blockers = ["OC4", "OC6", "OC12"]

    if len(rows) != 44:
        errors.append(f"CSV row count is {len(rows)}, expected 44")
    if matrix.get("row_count") != 44 or matrix.get("raw_row_count") != 132:
        errors.append("matrix row/raw-row counts changed")
    if set(matrix.get("examples", [])) != expected_examples:
        errors.append("matrix example set changed")
    if set(matrix.get("methods", [])) != expected_methods:
        errors.append("matrix method set changed")
    if matrix.get("direct_nonlocal_velocity_order_wins") != 40:
        errors.append("common-reference order wins changed")
    if matrix.get("direct_nonlocal_velocity_error_wins") != 40:
        errors.append("common-reference error wins changed")
    if matrix.get("source_policy_external_superiority_allowed") is not False:
        errors.append("source-policy superiority was overclaimed")
    if any(row.get("strict_external_error_claim_allowed") == "True" for row in rows):
        errors.append("CSV contains a strict external error claim")

    result_checks = review.get("result_checks", {})
    code_checks = review.get("code_hygiene_checks", {})
    proof_checks = review.get("proof_checks", {})
    if (
        review.get("narrowed_submission_standard_met") is not True
        or review.get("narrowed_claim_decision") != "submit_under_narrowed_claim"
    ):
        errors.append("review-agent narrowed-claim boundary changed")
    if review.get("blocker_open_by_id") != expected_blocker_open:
        errors.append("review-agent objective blocker open map is stale")
    if review.get("objective_blocker_open_by_id") != expected_blocker_open:
        errors.append("review-agent nested objective blocker open map is stale")
    if review.get("blocker_closure_decision_by_id") != expected_blocker_decisions:
        errors.append("review-agent blocker closure decisions changed")
    if review.get("blocker_closure_allowed_by_id") != expected_blocker_allowed:
        errors.append("review-agent blocker closure permissions changed")
    if review.get("open_blockers") != expected_open_blockers:
        errors.append("review-agent open blocker list changed")
    if review.get("decision") != "do_not_submit_global" or review.get("submission_standard_met") is not False:
        errors.append("review-agent global submission boundary changed")
    if code_checks.get("minimal_reproducible_submission_code_ready") is not False:
        errors.append("minimal reproducible submission code was overclaimed")
    if result_checks.get("source_policy_apples_to_apples_external_rows") != 0:
        errors.append("source-policy rows unexpectedly closed")
    if result_checks.get("source_policy_apples_to_apples_external_total_rows") != 40:
        errors.append("source-policy row total changed")
    if proof_checks.get("proof_closure_proof_gap_closed") is not True:
        errors.append("proof gap closure missing in review")
    if proof_checks.get("proof_closure_stage_residual_O_h7_implementation_defect_proved") is not True:
        errors.append("stage-residual direct proof closure missing in review")

    if traceability.get("claim_boundary", {}).get("result_to_manuscript_traceability_closed") is not True:
        errors.append("result-to-manuscript traceability is not closed")
    if dashboard.get("source_policy_dynamic_order_examples") not in (0, None):
        errors.append("dashboard overclosed source-policy dynamic-order examples")

    proof_state = proof.get("closure_state", {})
    if proof_state.get("proof_gap_closed") is not True:
        errors.append("proof manifest direct closure missing")
    if proof_state.get("stage_residual_O_h7_implementation_defect_proved") is not True:
        errors.append("proof manifest stage-residual direct closure missing")
    if proof.get("evidence_summary", {}).get("open_dynamic_rows") != 36:
        errors.append("open dynamic-row count changed")
    coverage = newton.get("obligation_coverage_matrix", {})
    if coverage.get("coverage_matrix_complete") is not True:
        errors.append("Newton-Euler obligation coverage matrix missing")
    if coverage.get("row_obligation_link_count") != 180:
        errors.append("Newton-Euler row-obligation link count changed")
    if coverage.get("proof_closure_advanced") is not False:
        errors.append("coverage matrix overclaims proof closure")
    runtime = newton.get("supporting_runtime_evidence", {})
    if runtime.get("runtime_source_component_layout_matches_targets") is not True:
        errors.append("Newton-Euler runtime source layout marker missing")
    expected_layout = [
        ("body0_translational_balance_source", 0, 0, "translational_newton_balance"),
        ("body0_rotational_balance_source", 3, 0, "rotational_euler_balance"),
        ("body1_translational_balance_source", 6, 1, "translational_newton_balance"),
        ("body1_rotational_balance_source", 9, 1, "rotational_euler_balance"),
    ]
    expected_rows = []
    for stage in range(3):
        base = stage * 44 + 24
        for source, offset, body, block in expected_layout:
            for component_index, component in enumerate(["x", "y", "z"]):
                local = offset + component_index
                expected_rows.append((base + local, local, body, component, block, source))
    actual_rows = [
        (
            row.get("global_row"),
            row.get("local_block_row"),
            row.get("body"),
            row.get("component"),
            row.get("balance_block"),
            row.get("runtime_source_component"),
        )
        for row in newton.get("row_targets", [])
    ]
    if actual_rows != expected_rows:
        errors.append("Newton-Euler runtime row layout is stale or inconsistent")

    if errors:
        print("cmame_minimal_candidate_replay=FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print("cmame_minimal_candidate_replay=PASS")
    print("rows=44")
    print("methods=11")
    print("examples=4")
    print("common_reference_order_error_wins=40/40,40/40")
    print("source_policy_apples_to_apples_external=0/40")
    print("direct_pc2_proof_gap_closed=True")
    print("schema_compat_legacy_key_retained=True")
    print("proof_gap_scope=direct_residual_bridge_kantorovich_route_closed_primitive_taylor_conditional_schema_open")
    print("stage_residual_O_h7_direct_proof=True")
    print("newton_euler_symbolic_defect_certificate_complete=False")
    print("objective_blockers_open=OC4,OC6,OC12")
    print("global_submission_decision=do_not_submit_global")
    print("submission_ready=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
