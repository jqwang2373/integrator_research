#!/usr/bin/env python3
"""Build a paper-facing result pack from v047 and v048 evidence artifacts."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path


PAPER = Path(__file__).resolve().parent
ROOT = PAPER.parent
V047 = ROOT.parent / "numerics" / "v047_cylindrical_chain_pipeline" / "results"
V048 = ROOT.parent / "numerics" / "v048_cross_paper_same_test_benchmarks" / "results"
OUT_JSON = PAPER / "PAPER_RESULT_PACK.json"
OUT_MD = PAPER / "PAPER_RESULT_PACK.md"
BLOCKER_IDS = ["OC4", "OC6", "OC12"]

EXAMPLES = ("single_pendulum", "double_pendulum", "four_link", "slider_crank")
LOCAL = "local_Gauss6_FullVA"
METHOD_ORDER = (
    LOCAL,
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
)


def read_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def as_float(value: object) -> float:
    try:
        out = float(value)
    except (TypeError, ValueError):
        return float("nan")
    return out if math.isfinite(out) else float("nan")


def fmt(value: object) -> str:
    number = as_float(value)
    if not math.isfinite(number):
        return "nan"
    if abs(number) >= 1000.0 or (0.0 < abs(number) < 1.0e-2):
        return f"{number:.3e}"
    return f"{number:.3f}"


def fmt_order(value: object) -> str:
    number = as_float(value)
    if not math.isfinite(number):
        return "nan"
    if abs(number) >= 1000.0:
        return f"{number:.3e}"
    return f"{number:.3f}"


def blocker_token(values: dict[str, object]) -> str:
    return ",".join(f"{blocker_id}:{values[blocker_id]}" for blocker_id in BLOCKER_IDS)


def common_reference_table(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    by_example: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        by_example.setdefault(row["example"], []).append(row)
    table = []
    for example in EXAMPLES:
        group = by_example[example]
        local = next(row for row in group if row["method"] == LOCAL)
        nonlocal_rows = [row for row in group if row["method"] != LOCAL and row["status"] == "ok"]
        nearest_error = min(nonlocal_rows, key=lambda row: as_float(row["finest_vel_error"]))
        strongest_order = max(nonlocal_rows, key=lambda row: as_float(row["vel_order"]))
        weakest_order = min(nonlocal_rows, key=lambda row: as_float(row["vel_order"]))
        table.append(
            {
                "example": example,
                "local_velocity_order": as_float(local["vel_order"]),
                "local_finest_velocity_error": as_float(local["finest_vel_error"]),
                "nearest_nonlocal_method": nearest_error["method"],
                "nearest_nonlocal_finest_velocity_error": as_float(nearest_error["finest_vel_error"]),
                "strongest_nonlocal_method": strongest_order["method"],
                "strongest_nonlocal_velocity_order": as_float(strongest_order["vel_order"]),
                "weakest_nonlocal_method": weakest_order["method"],
                "weakest_nonlocal_velocity_order": as_float(weakest_order["vel_order"]),
            }
        )
    return table


def all_method_matrix(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    by_key = {(row["method"], row["example"]): row for row in rows if row.get("status") == "ok"}
    matrix = []
    for method in METHOD_ORDER:
        entry = {"method": method, "examples": {}}
        for example in EXAMPLES:
            row = by_key.get((method, example))
            if row is None:
                entry["examples"][example] = None
                continue
            entry["examples"][example] = {
                "velocity_order": as_float(row["vel_order"]),
                "finest_velocity_error": as_float(row["finest_vel_error"]),
            }
        matrix.append(entry)
    return matrix


def compact_cell(cell: object) -> str:
    if not isinstance(cell, dict):
        return "missing"
    return f"{fmt_order(cell.get('velocity_order'))} / {fmt(cell.get('finest_velocity_error'))}"


def main() -> None:
    v047_summary = read_json(V047 / "summary_v047.json")
    blocker = read_json(PAPER / "CMAME_BLOCKER_CLOSURE_GATE.json")
    common_summary = read_json(V048 / "common_reference_error_summary.json")
    common_rows = read_csv(V048 / "common_reference_error_summary.csv")
    apples = read_json(V048 / "apples_to_apples_policy_audit.json")
    global_policy = read_json(V048 / "global_comparison_policy_audit.json")
    forensic = read_json(V048 / "all_examples_apples_to_apples_forensic_audit.json")
    objective = read_json(V048 / "objective_closure_audit.json")
    objective_completion = read_json(PAPER / "OBJECTIVE_COMPLETION_AUDIT.json")
    performance = read_json(V048 / "four_example_performance_summary.json")
    proof_scale = read_json(PAPER / "PROOF_NUMERICAL_SCALE_AUDIT.json")
    solver_scale = read_json(PAPER / "PROOF_SOLVER_SCALE_AUDIT.json")
    proof_closure = read_json(PAPER / "PROOF_CLOSURE_MANIFEST.json")
    dynamic_oracle = read_json(PAPER / "DYNAMIC_ROW_ORACLE_GATE.json")
    proof_scale_boundary = proof_scale.get("proof_boundary", {})
    solver_scale_boundary = solver_scale.get("proof_boundary", {})
    proof_closure_state = proof_closure.get("closure_state", {})
    formula_jacobian_oracle = dynamic_oracle.get("formula_row_ad_jacobian_oracle", {})
    dynamic_acceptance_boundary = dynamic_oracle.get("acceptance_boundary", {})

    common_table = common_reference_table(common_rows)
    all_methods = all_method_matrix(common_rows)
    open_blockers = [item["id"] for item in blocker.get("blockers", []) if item.get("status") == "open"]
    closed_blockers = [item["id"] for item in blocker.get("blockers", []) if item.get("status") == "closed"]

    global_claim_boundary = global_policy.get("claim_boundary")
    if isinstance(global_claim_boundary, str):
        global_claim_boundary = global_claim_boundary.replace(
            "source-policy reproduction, velocity/output mapping, original TFE setup, and VP code-path issues",
            "source-policy reproduction, output/norm mapping, TFE runner/friction/endpoint policy, and VP code-path issues",
        )

    result = {
        "schema": "paper-result-pack-v1",
        "paper_safe": True,
        "submission_ready": False,
        "global_objective_complete": objective_completion.get("objective_complete"),
        "global_submission_ready": objective_completion.get("submission_ready"),
        "global_open_blockers": objective_completion.get("blocking_ids"),
        "objective_blocker_matrix_status": "global_objective_blockers_remain_open",
        "objective_source_policy_closed_ratio": objective_completion.get(
            "source_policy_closed_ratio"
        ),
        "blocker_open_by_id": objective_completion.get("blocker_open_by_id"),
        "blocker_closure_decision_by_id": objective_completion.get(
            "blocker_closure_decision_by_id"
        ),
        "blocker_closure_allowed_by_id": objective_completion.get(
            "blocker_closure_allowed_by_id"
        ),
        "objective_blocker_open_by_id": objective_completion.get("blocker_open_by_id"),
        "objective_blocker_closure_decision_by_id": objective_completion.get(
            "blocker_closure_decision_by_id"
        ),
        "objective_blocker_closure_allowed_by_id": objective_completion.get(
            "blocker_closure_allowed_by_id"
        ),
        "quality_review_passed": False,
        "quality_review_passed_under_narrowed_claim": bool(
            blocker.get("quality_review_passed") is True
            and blocker.get("submission_ready_under_narrowed_claim") is True
        ),
        "narrowed_claim_submission_standard_met": bool(
            blocker.get("quality_review_passed") is True
            and blocker.get("submission_ready_under_narrowed_claim") is True
        ),
        "narrowed_claim_decision": (
            "submit_under_narrowed_claim"
            if blocker.get("quality_review_passed") is True
            and blocker.get("submission_ready_under_narrowed_claim") is True
            else "do_not_submit_narrowed_claim"
        ),
        "quality_review_scope": "global_false_narrowed_claim_subcheck_true",
        "result_scope": "paper-facing result consolidation, not a new numerical run",
        "accepted_method": "Gauss6/FullVA",
        "accepted_method_order": 6,
        "smooth_projected_orders": {
            "position": 7.161,
            "velocity": 7.066,
        },
        "asme_examples": list(EXAMPLES),
        "asme_gate_status": v047_summary.get("asme_gate", {}).get("status"),
        "common_reference": {
            "step_sizes": common_summary.get("step_sizes"),
            "reference_h": common_summary.get("reference_h"),
            "t_end": common_summary.get("t_end"),
            "summary_rows": common_summary.get("summary_row_count"),
            "direct_error_comparable_rows": common_summary.get("direct_error_comparable_rows"),
            "local_velocity_order_wins": common_summary.get("local_velocity_order_wins"),
            "local_velocity_order_comparisons": common_summary.get("local_velocity_order_comparisons"),
            "local_finest_velocity_error_wins": common_summary.get("local_finest_velocity_error_wins"),
            "local_finest_velocity_error_comparisons": common_summary.get("local_finest_velocity_error_comparisons"),
            "original_paper_velocity_error_wins": common_summary.get("original_paper_velocity_error_wins"),
            "original_paper_velocity_error_comparisons": common_summary.get("original_paper_velocity_error_comparisons"),
            "kissel_negrut_velocity_error_wins": common_summary.get("kissel_negrut_velocity_error_wins"),
            "kissel_negrut_velocity_error_comparisons": common_summary.get("kissel_negrut_velocity_error_comparisons"),
            "public_code_fixed_grid_replay": common_summary.get("public_code_fixed_grid_replay"),
            "source_policy_reproduction": common_summary.get("source_policy_reproduction"),
            "apples_to_apples_rows": apples.get("paper_safe_row_count"),
            "apples_to_apples_total_rows": apples.get("row_count"),
            "global_policy_passed": global_policy.get("reasonable_apples_to_apples_claims"),
            "global_policy_passed_count": global_policy.get("passed_count"),
            "global_policy_row_count": global_policy.get("row_count"),
            "mixed_policy_direct_error_rows": global_policy.get("mixed_policy_direct_error_vs_local_comparable_rows"),
            "direct_error_rows_allowed": global_policy.get("direct_error_vs_local_comparable_rows"),
            "direct_error_rows_allowed_for_paper": global_policy.get("direct_error_rows_allowed_for_paper"),
            "paper_direct_error_superiority_claim_allowed": global_policy.get(
                "paper_direct_error_superiority_claim_allowed"
            ),
            "all_method_example_cells_checked": forensic.get("row_count"),
            "strict_external_error_claim_allowed_rows": forensic.get("strict_external_error_claim_allowed_rows"),
            "claim_boundary": global_claim_boundary,
            "table": common_table,
            "all_method_matrix": all_methods,
        },
        "v048_objective": {
            "objective_complete": objective.get("objective_complete"),
            "objective_scope": "v048_cross_paper_fixed_grid_comparison_scaffold_only",
            "global_submission_effect": "does_not_close_global_submission_ready",
            "passed_count": objective.get("passed_count"),
            "row_count": objective.get("row_count"),
            "source_policy_reproduction": objective.get("source_policy_reproduction"),
            "public_code_fixed_grid_replay": objective.get("public_code_fixed_grid_replay"),
        },
        "performance_matrix": {
            "row_count": performance.get("row_count"),
            "completed_row_count": performance.get("completed_row_count"),
            "same_test_campaign_status": performance.get("same_test_campaign_status"),
            "external_superiority_claim": performance.get("external_superiority_claim"),
        },
        "proof_status": {
            "proof_gap_closed": proof_closure_state.get("proof_gap_closed"),
            "direct_pc2_proof_gap_closed": proof_closure_state.get(
                "direct_pc2_proof_gap_closed", proof_closure_state.get("proof_gap_closed")
            ),
            "proof_gap_closed_scope": proof_closure_state.get("proof_gap_closed_scope"),
            "proof_gap_closed_reading_rule": (
                "The schema-only compatibility boolean proof_gap_closed is a "
                "schema-compatible shorthand for direct_pc2_proof_gap_closed and is "
                "scoped to the active direct PC2 residual-bridge/Kantorovich proof closure. "
                "Reader-facing proof status should use direct_pc2_proof_gap_closed. "
                "The compatibility boolean does not close the primitive/Taylor route, "
                "P6 solver-policy evidence, P7 residual-to-error promotion, "
                "source-policy readiness, full-TFE replacement, or global submission "
                "readiness."
            ),
            "stage_residual_O_h7_implementation_defect_proved": proof_closure_state.get(
                "stage_residual_O_h7_implementation_defect_proved"
            ),
            "dynamic_symbolic_oracle_complete": proof_closure_state.get("dynamic_symbolic_oracle_complete"),
            "symbolic_oracle_complete": formula_jacobian_oracle.get("symbolic_oracle_complete"),
            "dynamic_oracle_stage_residual_O_h7_symbolic_certificate_proved": (
                dynamic_acceptance_boundary.get("stage_residual_O_h7_implementation_defect_proved")
            ),
            "finite_run_error_scale_supports_order_six": proof_scale_boundary.get(
                "finite_run_error_scale_supports_order_six"
            ),
            "eta_h_O_h7_solver_policy_evidence": solver_scale_boundary.get("eta_h_O_h7_solver_policy_evidence"),
            "finite_scaled_tolerance_probe_recorded": solver_scale_boundary.get(
                "finite_scaled_tolerance_probe_recorded"
            ),
            "finite_scaled_tolerance_probe_ok_rows": solver_scale.get("finite_scaled_tolerance_probe", {}).get(
                "ok_row_count"
            ),
            "finite_scaled_tolerance_probe_total_rows": solver_scale.get("finite_scaled_tolerance_probe", {}).get(
                "row_count"
            ),
            "finite_scaled_tolerance_probe_max_residual_over_h7": solver_scale.get(
                "finite_scaled_tolerance_probe", {}
            ).get("max_final_residual_over_h7"),
            "scaled_tolerance_sweep_recorded": solver_scale_boundary.get("scaled_tolerance_sweep_recorded"),
            "runtime_ad_oracle_complete": formula_jacobian_oracle.get("runtime_ad_oracle_complete"),
        },
        "blocker_status": {
            "b_gate_open_blockers": open_blockers,
            "b_gate_closed_blockers": closed_blockers,
            "b_gate_open_blocker_count": len(open_blockers),
            "b_gate_closed_blocker_count": len(closed_blockers),
            "global_submission_open_blockers": ["OC4", "OC6", "OC12"],
            "global_submission_ready": False,
        },
        "paper_claim_boundary": (
            "The accepted paper claim is an order-six Gauss6/FullVA method claim with four-example "
            "validation and a bounded fixed-grid common-reference diagnostic. It is not source-policy "
            "reproduction, not paper-level direct error superiority, not a full TFE replacement, and not "
            "a full external superiority claim."
        ),
    }

    with OUT_JSON.open("w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, sort_keys=True)
        handle.write("\n")

    lines = [
        "# Paper Result Pack",
        "",
        "Status: **claim-boundary result consolidation, not submission-ready acceptance**.",
        "",
        f"- Accepted method: `{result['accepted_method']}`.",
        f"- Accepted method order: `{result['accepted_method_order']}`.",
        "- Smooth projected orders: `7.161/7.066` position/velocity.",
        f"- ASME examples: `{', '.join(result['asme_examples'])}`.",
        f"- Common-reference apples-to-apples rows: `{apples.get('paper_safe_row_count')}/{apples.get('row_count')}`.",
        f"- Global comparison-policy audit: `{global_policy.get('passed_count')}/{global_policy.get('row_count')}`.",
        f"- Mixed-policy direct error rows allowed: `{global_policy.get('mixed_policy_direct_error_vs_local_comparable_rows')}`.",
        f"- Paper direct error rows allowed: `{global_policy.get('direct_error_rows_allowed_for_paper')}`.",
        f"- All method/example cells checked: `{forensic.get('row_count')}`.",
        f"- Source-policy reproduction: `{common_summary.get('source_policy_reproduction')}`.",
        f"- Public-code fixed-grid replay: `{common_summary.get('public_code_fixed_grid_replay')}`.",
        f"- External superiority claim: `{performance.get('external_superiority_claim')}`.",
        f"- Submission ready: `{result['submission_ready']}`.",
        f"- Global objective complete: `{result['global_objective_complete']}`.",
        f"- Global submission ready: `{result['global_submission_ready']}`.",
        f"- Global open blockers: `{', '.join(result['global_open_blockers'])}`.",
        f"- Source-policy rows closed: `{result['objective_source_policy_closed_ratio']}`.",
        f"- v048 objective scope: `{result['v048_objective']['objective_scope']}`.",
        f"- v048 objective global effect: `{result['v048_objective']['global_submission_effect']}`.",
        f"- Global quality review passed: `{result['quality_review_passed']}`.",
        f"- Narrowed-claim quality review passed: `{result['quality_review_passed_under_narrowed_claim']}`.",
        f"- Narrowed-claim decision alias: `{result['narrowed_claim_decision']}` "
        "(legacy compatibility field for the bounded subcheck only; not a global submit instruction).",
        "",
        "## Objective Blocker Matrix",
        "",
        "This result pack consolidates paper evidence. It does not close the global objective blockers.",
        "",
        f"- `blocker_open_by_id={blocker_token(result['blocker_open_by_id'])}`",
        f"- `blocker_closure_decision_by_id={blocker_token(result['blocker_closure_decision_by_id'])}`",
        f"- `blocker_closure_allowed_by_id={blocker_token(result['blocker_closure_allowed_by_id'])}`",
        "",
        "## Common-Reference Velocity Evidence",
        "",
        "| Example | local order | local finest error | nearest nonlocal method | nearest nonlocal error | strongest nonlocal order | weakest nonlocal order |",
        "|---|---:|---:|---|---:|---:|---:|",
    ]
    for item in common_table:
        lines.append(
            "| "
            f"`{item['example']}` | `{fmt_order(item['local_velocity_order'])}` | "
            f"`{fmt(item['local_finest_velocity_error'])}` | "
            f"`{item['nearest_nonlocal_method']}` | `{fmt(item['nearest_nonlocal_finest_velocity_error'])}` | "
            f"`{item['strongest_nonlocal_method']} {fmt_order(item['strongest_nonlocal_velocity_order'])}` | "
            f"`{item['weakest_nonlocal_method']} {fmt_order(item['weakest_nonlocal_velocity_order'])}` |"
        )
    lines.extend(
        [
            "",
            "## All Runnable Method Rows",
            "",
            "Each cell is `observed velocity order / finest-step velocity error` on the shared fixed-grid "
            "`h={0.1,0.05,0.025}` sweep with reference `h=0.0125`.",
            "",
            "| Method | single_pendulum | double_pendulum | four_link | slider_crank |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for item in all_methods:
        examples = item["examples"]
        lines.append(
            "| "
            f"`{item['method']}` | "
            f"`{compact_cell(examples['single_pendulum'])}` | "
            f"`{compact_cell(examples['double_pendulum'])}` | "
            f"`{compact_cell(examples['four_link'])}` | "
            f"`{compact_cell(examples['slider_crank'])}` |"
        )
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            result["paper_claim_boundary"],
            "",
            "The fixed-grid common-reference matrix is a bounded diagnostic. The all-example forensic "
            "audit allows zero paper-level direct error rows. The main mixed-policy coarse table supports "
            "observed-order comparisons and diagnostics, not blanket cross-method error superiority.",
            "",
            "## Proof And Review Status",
            "",
            f"- Direct PC2 proof gap closed: `{result['proof_status']['direct_pc2_proof_gap_closed']}`.",
            f"- Direct proof gap scope: `{result['proof_status']['proof_gap_closed_scope']}`.",
            f"- Direct proof gap reading rule: {result['proof_status']['proof_gap_closed_reading_rule']}",
            f"- Finite-run order-six scale evidence: `{result['proof_status']['finite_run_error_scale_supports_order_six']}`.",
            f"- Finite scaled-tolerance probe rows/max eta-h ratio: `{result['proof_status']['finite_scaled_tolerance_probe_ok_rows']}/{result['proof_status']['finite_scaled_tolerance_probe_total_rows']}` / `{result['proof_status']['finite_scaled_tolerance_probe_max_residual_over_h7']:.6f}`.",
            f"- Scaled solver tolerance evidence: `{result['proof_status']['eta_h_O_h7_solver_policy_evidence']}`.",
            f"- Runtime AD formula-row oracle complete: `{result['proof_status']['runtime_ad_oracle_complete']}`.",
            f"- Dynamic symbolic oracle complete: `{result['proof_status']['dynamic_symbolic_oracle_complete']}`.",
            f"- Symbolic row oracle complete: `{result['proof_status']['symbolic_oracle_complete']}`.",
            f"- Symbolic-certificate stage residual `O(h^7)` route proved: `{result['proof_status']['dynamic_oracle_stage_residual_O_h7_symbolic_certificate_proved']}`.",
            f"- Direct-route stage residual `O(h^7)` implementation defect proved: `{result['proof_status']['stage_residual_O_h7_implementation_defect_proved']}`.",
            f"- Narrowed-claim B-gate open blockers: `{', '.join(open_blockers)}`.",
            f"- Narrowed-claim B-gate closed blockers: `{', '.join(closed_blockers)}`.",
            "- Global submission open blockers: `OC4, OC6, OC12`.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("paper_result_pack=written")
    print(f"common_reference_apples_to_apples={apples.get('paper_safe_row_count')}/{apples.get('row_count')}")
    print(f"global_comparison_policy={global_policy.get('passed_count')}/{global_policy.get('row_count')}")
    print(f"submission_ready={result['submission_ready']}")
    print(f"blocker_open_by_id={blocker_token(result['blocker_open_by_id'])}")
    print(
        "blocker_closure_decision_by_id="
        f"{blocker_token(result['blocker_closure_decision_by_id'])}"
    )
    print(f"blocker_closure_allowed_by_id={blocker_token(result['blocker_closure_allowed_by_id'])}")


if __name__ == "__main__":
    main()
