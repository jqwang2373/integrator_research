#!/usr/bin/env python3
"""Build the self-contained four-example runner extraction plan."""

from __future__ import annotations

import ast
import json
from pathlib import Path


PAPER = Path(__file__).resolve().parent
ROOT = PAPER.parent
V048 = ROOT / "v048_cross_paper_same_test_benchmarks"
OUT_JSON = PAPER / "CMAME_SELF_CONTAINED_RUNNER_EXTRACTION_PLAN.json"
OUT_MD = PAPER / "CMAME_SELF_CONTAINED_RUNNER_EXTRACTION_PLAN.md"

REVIEWER_FILE_LIMIT = 12
REVIEWER_LINE_LIMIT = 2000

REQUIRED_SYMBOLS = {
    "../v048_cross_paper_same_test_benchmarks/run_coarse_four_example_order.py": [
        ("run_ra2021_rows", "external_ra2021_public_baselines"),
        ("run_hi2022_rows", "external_hi2022_public_baselines"),
        ("run_local_single_double_rows", "local_single_double_gauss6_fullva"),
        ("local_closed_loop_rows", "local_four_link_slider_crank_closed_loop"),
        ("run_tfe2026_second_order_rows", "tfe_second_order_baselines"),
        ("run_tfe2026_tfe_m1_rows", "tfe_m1_baselines"),
        ("run_tfe2026_tfe_m2_rows", "tfe_m2_baselines"),
        ("run_tfe2026_tfe_m3_rows", "tfe_m3_scope_boundary"),
        ("run_vp2024_coordinate_partitioning_rows", "vp2024_proxy_baseline"),
        ("summarize", "paper_matrix_aggregation"),
    ],
    "../v048_cross_paper_same_test_benchmarks/run_v048.py": [
        ("run_public_model_state_history", "ra2021_public_state_history"),
        ("run_hi2022_model_state_history", "hi2022_public_state_history"),
        ("run_ra2021_order_rows", "ra2021_public_order_rows"),
        ("run_ra2021_double_pendulum_order_rows", "ra2021_double_public_rows"),
        ("run_hi2022_halfimplicit_rows", "hi2022_halfimplicit_rows"),
        ("run_gauss6_fullva_public_horizon_single_rows", "local_single_gauss6_rows"),
        ("run_gauss6_fullva_public_horizon_double_coarse_rows", "local_double_gauss6_rows"),
        ("switch_simengine_root", "external_public_code_path_switch"),
        ("patch_modern_numpy_scalar_assignments", "external_public_code_compatibility"),
        ("estimate_order", "order_estimation"),
    ],
    "../v048_cross_paper_same_test_benchmarks/build_closed_loop_true_dynamic_strict_common_reference.py": [
        ("import_v047_module", "v047_exact_endpoint_dependency"),
        ("setup_exact_system", "v047_exact_endpoint_reference"),
        ("local_rows", "local_true_dynamic_rows"),
        ("public_rows", "public_true_dynamic_rows"),
        ("summarize_rows", "strict_common_reference_summary"),
        ("main", "strict_common_reference_builder"),
    ],
    "../v048_cross_paper_same_test_benchmarks/closed_loop_fullva_dynamic_residual.py": [
        ("closed_loop_fullva_stage_residual", "dynamic_stage_residual_core"),
        ("endpoint_state_from_system", "endpoint_state_extraction"),
        ("endpoint_state_error_inf", "endpoint_error_norm"),
        ("gauss6_closed_loop_fullva_dynamic_step_newton_smoke", "non_oracle_newton_smoke"),
    ],
    "../v048_cross_paper_same_test_benchmarks/tfe_source_pendulum_model.py": [
        ("source_output_policy", "tfe_source_output_policy"),
        ("source_error_metrics", "tfe_source_error_metrics"),
        ("newmark_beta_candidate_step", "tfe_newmark_baseline"),
        ("trapezoidal_candidate_step", "tfe_trapezoidal_baseline"),
        ("tfe_m1_candidate_step", "tfe_m1_baseline"),
        ("tfe_multinode_candidate_step", "tfe_m2_m3_baseline"),
        ("bounded_source_policy_runner_smoke", "tfe_bounded_runner_smoke"),
        ("active_tfe_b2_full_t10_coarse_candidate_probe", "tfe_full_t10_probe"),
    ],
}


def read_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def resolve(path_label: str) -> Path:
    return (PAPER / path_label).resolve() if path_label.startswith("../") else PAPER / path_label


def symbol_spans(path: Path) -> dict[str, tuple[int, int]]:
    tree = ast.parse(read_text(path))
    spans: dict[str, tuple[int, int]] = {}
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            end = getattr(node, "end_lineno", node.lineno)
            spans[node.name] = (node.lineno, int(end))
    return spans


def build_symbol_inventory() -> tuple[list[dict[str, object]], int]:
    rows: list[dict[str, object]] = []
    total_lines = 0
    for path_label, symbols in REQUIRED_SYMBOLS.items():
        path = resolve(path_label)
        spans = symbol_spans(path)
        for symbol, role in symbols:
            start, end = spans.get(symbol, (0, 0))
            line_count = end - start + 1 if start and end else 0
            total_lines += line_count
            rows.append(
                {
                    "path": path_label,
                    "symbol": symbol,
                    "role": role,
                    "exists": symbol in spans,
                    "start_line": start,
                    "end_line": end,
                    "symbol_line_count": line_count,
                    "extractability": "requires_dependency_rewrite",
                }
            )
    return rows, total_lines


def main() -> None:
    runner_adapter = read_json(PAPER / "CMAME_RUNNER_ADAPTER_CANDIDATE_MANIFEST.json")
    runner_centered = read_json(PAPER / "CMAME_RUNNER_CENTERED_REPRODUCIBILITY_AUDIT.json")
    b6_local_evidence = read_json(PAPER / "B6_FOUR_EXAMPLE_LOCAL_EVIDENCE_SUMMARY.json")
    review = read_json(PAPER / "CMAME_REVIEW_AGENT_REPORT.json")
    proof = read_json(PAPER / "PROOF_CLOSURE_MANIFEST.json")
    matrix = read_json(PAPER / "PAPER_NUMERICAL_RESULT_MATRIX.json")
    p1_audit = read_json(PAPER / "CMAME_P1_LOCAL_RUNNER_EXTRACTION_AUDIT.json")
    closed_loop_audit = read_json(PAPER / "B6_CLOSED_LOOP_SELF_CONTAINED_EXTRACTION_AUDIT.json")
    closed_loop_candidate = read_json(PAPER / "CMAME_CLOSED_LOOP_LOCAL_RUNNER_CANDIDATE_MANIFEST.json")
    prose = read_json(PAPER / "CMAME_PROSE_RESIDUE_AUDIT.json")

    inventory, target_symbol_lines = build_symbol_inventory()
    source_policy_closed = review.get("result_checks", {}).get("source_policy_apples_to_apples_external_rows")
    source_policy_total = review.get("result_checks", {}).get("source_policy_apples_to_apples_external_total_rows")
    proof_closed = proof.get("closure_state", {}).get("proof_gap_closed") is True
    p1_local_ready = p1_audit.get("p1_local_single_double_ready") is True
    p1_single_candidate_ready = p1_audit.get("p1_single_runner_candidate_ready") is True
    p1_double_candidate_ready = p1_audit.get("p1_double_runner_candidate_ready") is True
    p1_regenerated_candidate_rows = p1_audit.get("p1_regenerated_candidate_rows", 0)
    p1_required_rows = p1_audit.get("p1_required_rows", 6)
    closed_loop_candidate_passed = closed_loop_candidate.get("runner_passed") is True
    closed_loop_candidate_compact = closed_loop_candidate.get("candidate_python_line_limit_ok") is True
    local_accepted_rows_self_contained_runner_ready = (
        p1_local_ready
        and p1_single_candidate_ready
        and p1_double_candidate_ready
        and b6_local_evidence.get("b6_local_evidence_runner_passed") is True
        and b6_local_evidence.get("human_runnable_four_example_self_contained_simulation_ready") is True
        and closed_loop_audit.get("self_contained_runner_ready") is True
        and closed_loop_candidate_passed
        and closed_loop_candidate_compact
    )
    full_source_policy_self_contained_runner_ready = (
        local_accepted_rows_self_contained_runner_ready
        and runner_centered.get("full_source_policy_runner_package_ready") is True
        and source_policy_closed == source_policy_total
        and source_policy_total == 40
    )
    prose_dependency = prose.get("post_baseline_final_prose_dependency", {})
    prose_preflight = prose.get("b6_closure_readiness_preflight", {})
    b6_final_prose_pass_ready = (
        prose_dependency.get("final_prose_pass_ready") is True
        and prose_dependency.get("b6_closure_allowed_now") is True
        and prose_preflight.get("status") == "b6_final_prose_pass_closed_under_narrowed_b4_b7_scope"
    )
    full_source_policy_b6_prose_ready = full_source_policy_self_contained_runner_ready

    phases = [
        {
            "id": "P0_report_adapter",
            "status": "partial_complete",
            "evidence": "runner-adapter candidate validates embedded 44-row matrix and can call v048 --report-only",
        },
        {
            "id": "P1_local_gauss6_rows",
            "status": "closed" if p1_local_ready else "open",
            "evidence": (
                "P1 dependency audit: "
                f"{p1_audit.get('status')}; "
                f"local single/double ready={p1_local_ready}; "
                f"single candidate ready={p1_single_candidate_ready}; "
                f"double candidate ready={p1_double_candidate_ready}; "
                f"candidate rows={p1_regenerated_candidate_rows}/{p1_required_rows}; "
                f"v047 primary closure lines={p1_audit.get('v047_primary_recursive_internal_dependency_lines')}"
            ),
        },
        {
            "id": "P1b_four_example_local_evidence_runner",
            "status": "closed" if b6_local_evidence.get("b6_local_evidence_runner_passed") is True else "open",
            "evidence": (
                f"four-example local evidence rows={b6_local_evidence.get('local_rows')}; "
                f"self-contained={b6_local_evidence.get('self_contained_examples')}; "
                f"replay-only={b6_local_evidence.get('replay_only_examples')}; "
                f"four-example self-contained simulation ready="
                f"{b6_local_evidence.get('human_runnable_four_example_self_contained_simulation_ready')}; "
                f"closed-loop extraction audit={closed_loop_audit.get('status')}"
            ),
        },
        {
            "id": "P1c_closed_loop_self_contained_runner",
            "status": (
                "closed_compact_candidate_passed"
                if closed_loop_candidate_passed and closed_loop_candidate_compact
                else "partial_non_compact_candidate_passed"
                if closed_loop_candidate_passed
                else "open"
            ),
            "evidence": (
                f"target symbols={closed_loop_audit.get('target_symbol_count')}/"
                f"{closed_loop_audit.get('target_symbol_lines')} lines; "
                f"replay-only closed-loop examples={closed_loop_audit.get('replay_only_closed_loop_examples')}; "
                f"candidate rows={closed_loop_candidate.get('closed_loop_local_rows')}; "
                f"candidate compact={closed_loop_candidate_compact}; "
                f"self-contained ready={closed_loop_audit.get('self_contained_runner_ready')}"
            ),
        },
        {
            "id": "P2_external_public_baselines",
            "status": "open",
            "evidence": "RA2021/HI2022/VP wrappers still depend on external public-code paths",
        },
        {
            "id": "P3_tfe_source_policy_rows",
            "status": "open",
            "evidence": "original TFE source-policy runner and full T=10 endpoint policy remain open",
        },
        {
            "id": "P4_proof_boundary",
            "status": "open" if not proof_closed else "closed",
            "scope": "direct_pc2_proof_boundary_subcheck_not_global_submission_readiness",
            "evidence": (
                f"direct_pc2_proof_gap_closed={proof_closed}; "
                "this package phase does not close primitive/Taylor, solver-policy, residual-to-error, or source-policy boundaries"
            ),
        },
    ]

    acceptance = {
        "max_python_files": REVIEWER_FILE_LIMIT,
        "max_python_lines": REVIEWER_LINE_LIMIT,
        "regenerates_paper_matrix_rows": 44,
        "regenerates_raw_rows": 132,
        "forbids_primary_import_run_v048": True,
        "forbids_primary_import_run_v047": True,
        "source_policy_rows_required_for_external_superiority": source_policy_total,
        "proof_gap_must_be_closed_for_submission_ready": True,
    }

    plan = {
        "schema": "cmame-self-contained-runner-extraction-plan-v1",
        "status": "local_accepted_rows_self_contained_runner_ready_source_policy_package_open",
        "generated_from": [
            "CMAME_RUNNER_ADAPTER_CANDIDATE_MANIFEST.json",
            "CMAME_RUNNER_CENTERED_REPRODUCIBILITY_AUDIT.json",
            "CMAME_P1_LOCAL_RUNNER_EXTRACTION_AUDIT.json",
            "B6_CLOSED_LOOP_SELF_CONTAINED_EXTRACTION_AUDIT.json",
            "CMAME_CLOSED_LOOP_LOCAL_RUNNER_CANDIDATE_MANIFEST.json",
            "B6_FOUR_EXAMPLE_LOCAL_EVIDENCE_SUMMARY.json",
            "CMAME_REVIEW_AGENT_REPORT.json",
            "PROOF_CLOSURE_MANIFEST.json",
            "PAPER_NUMERICAL_RESULT_MATRIX.json",
            "CMAME_PROSE_RESIDUE_AUDIT.json",
        ],
        "submission_ready": False,
        "self_contained_runner_ready": full_source_policy_self_contained_runner_ready,
        "local_accepted_rows_self_contained_runner_ready": local_accepted_rows_self_contained_runner_ready,
        "full_source_policy_self_contained_runner_ready": full_source_policy_self_contained_runner_ready,
        "b6_final_prose_pass_ready": b6_final_prose_pass_ready,
        "b6_final_prose_pass_scope": "narrowed_claim_current_submission",
        "full_source_policy_b6_prose_ready": full_source_policy_b6_prose_ready,
        "b6_closure_preflight_status": prose_preflight.get("status"),
        "b6_closure_allowed_now": prose_preflight.get("b6_closure_allowed_now"),
        "runner_package_boundary": {
            "local_accepted_rows_self_contained": local_accepted_rows_self_contained_runner_ready,
            "full_source_policy_self_contained": full_source_policy_self_contained_runner_ready,
            "b6_final_prose_pass_ready": b6_final_prose_pass_ready,
            "b6_final_prose_pass_scope": "narrowed_claim_current_submission",
            "full_source_policy_b6_prose_ready": full_source_policy_b6_prose_ready,
            "b6_closure_allowed_now": prose_preflight.get("b6_closure_allowed_now"),
            "source_policy_rows_closed": source_policy_closed,
            "source_policy_rows_total": source_policy_total,
            "reason_full_source_policy_deferred": (
                "The compact local accepted-row runner covers the accepted local examples, but the full "
                "source-policy runner package remains open until source-policy rows close. The B6 final prose "
                "pass is closed only under the narrowed current-claim policy that excludes source-policy "
                "work/precision superiority."
            ),
        },
        "runner_adapter_present": runner_adapter.get("runner_adapter_present"),
        "runner_adapter_self_contained": runner_adapter.get("self_contained_simulation_runner"),
        "b6_four_example_local_evidence": {
            "schema": b6_local_evidence.get("schema"),
            "status": b6_local_evidence.get("status"),
            "runner_passed": b6_local_evidence.get("b6_local_evidence_runner_passed"),
            "local_rows": b6_local_evidence.get("local_rows"),
            "self_contained_examples": b6_local_evidence.get("self_contained_examples"),
            "replay_only_examples": b6_local_evidence.get("replay_only_examples"),
            "four_example_local_evidence_available": b6_local_evidence.get(
                "human_runnable_four_example_local_evidence_available"
            ),
            "four_example_self_contained_simulation_ready": b6_local_evidence.get(
                "human_runnable_four_example_self_contained_simulation_ready"
            ),
        },
        "p1_local_runner_extraction_audit": {
            "schema": p1_audit.get("schema"),
            "status": p1_audit.get("status"),
            "p1_local_single_double_ready": p1_audit.get("p1_local_single_double_ready"),
            "p1_single_runner_candidate_ready": p1_audit.get("p1_single_runner_candidate_ready"),
            "p1_double_runner_candidate_ready": p1_audit.get("p1_double_runner_candidate_ready"),
            "p1_regenerated_candidate_rows": p1_audit.get("p1_regenerated_candidate_rows"),
            "p1_required_rows": p1_audit.get("p1_required_rows"),
            "p1_missing_candidate_rows": p1_audit.get("p1_missing_candidate_rows"),
            "p1_single_runner_candidate": p1_audit.get("p1_single_runner_candidate"),
            "p1_double_runner_candidate": p1_audit.get("p1_double_runner_candidate"),
            "v047_source_python_lines": p1_audit.get("v047_source_python_lines"),
            "v047_primary_recursive_internal_dependency_count": p1_audit.get(
                "v047_primary_recursive_internal_dependency_count"
            ),
            "v047_primary_recursive_internal_dependency_lines": p1_audit.get(
                "v047_primary_recursive_internal_dependency_lines"
            ),
            "open_blocker_count": sum(1 for item in p1_audit.get("open_blockers", []) if item.get("status") == "open"),
        },
        "b6_closed_loop_self_contained_extraction_audit": {
            "schema": closed_loop_audit.get("schema"),
            "status": closed_loop_audit.get("status"),
            "self_contained_runner_ready": closed_loop_audit.get("self_contained_runner_ready"),
            "target_source_file_count": closed_loop_audit.get("target_source_file_count"),
            "target_source_file_lines": closed_loop_audit.get("target_source_file_lines"),
            "target_symbol_count": closed_loop_audit.get("target_symbol_count"),
            "target_symbol_lines": closed_loop_audit.get("target_symbol_lines"),
            "replay_only_closed_loop_examples": closed_loop_audit.get("replay_only_closed_loop_examples"),
            "closed_loop_local_replay_rows": closed_loop_audit.get("closed_loop_local_replay_rows"),
            "run_v047_invoked": closed_loop_audit.get("run_v047_invoked"),
            "run_v048_invoked": closed_loop_audit.get("run_v048_invoked"),
            "b4_opt_in_required_for_this_audit": closed_loop_audit.get("b4_opt_in_required_for_this_audit"),
            "next_concrete_step": closed_loop_audit.get("next_concrete_step"),
        },
        "closed_loop_local_runner_candidate": {
            "schema": closed_loop_candidate.get("schema"),
            "status": closed_loop_candidate.get("status"),
            "runner_passed": closed_loop_candidate.get("runner_passed"),
            "self_contained_simulation_runner": closed_loop_candidate.get("self_contained_simulation_runner"),
            "candidate_python_file_count": closed_loop_candidate.get("candidate_python_file_count"),
            "candidate_python_line_count": closed_loop_candidate.get("candidate_python_line_count"),
            "candidate_python_line_limit_ok": closed_loop_candidate.get("candidate_python_line_limit_ok"),
            "imports_v046_v047_v048_or_v029": closed_loop_candidate.get("imports_v046_v047_v048_or_v029"),
            "closed_loop_local_rows": closed_loop_candidate.get("closed_loop_local_rows"),
            "closed_loop_models": closed_loop_candidate.get("closed_loop_models"),
            "source_policy_external_rows_closed": closed_loop_candidate.get("source_policy_external_rows_closed"),
            "source_policy_external_rows_total": closed_loop_candidate.get("source_policy_external_rows_total"),
            "source_policy_external_superiority_allowed": closed_loop_candidate.get(
                "source_policy_external_superiority_allowed"
            ),
            "submission_ready": closed_loop_candidate.get("submission_ready"),
            "next_concrete_step": closed_loop_candidate.get("next_concrete_step"),
        },
        "paper_matrix_rows": matrix.get("row_count"),
        "paper_matrix_raw_rows": matrix.get("raw_row_count"),
        "paper_matrix_methods": matrix.get("method_count"),
        "common_reference_order_wins": matrix.get("direct_nonlocal_velocity_order_wins"),
        "common_reference_error_wins": matrix.get("direct_nonlocal_velocity_error_wins"),
        "source_policy_closed_rows": source_policy_closed,
        "source_policy_total_rows": source_policy_total,
        "proof_gap_closed": proof_closed,
        "existing_runner_source_lines": runner_centered.get("existing_runner_source_total_python_lines"),
        "target_symbol_count": len(inventory),
        "target_symbol_lines": target_symbol_lines,
        "target_symbols": inventory,
        "phases": phases,
        "acceptance_criteria": acceptance,
        "next_concrete_step": closed_loop_candidate.get("next_concrete_step")
        if closed_loop_candidate_passed
        else closed_loop_audit.get("next_concrete_step"),
    }

    OUT_JSON.write_text(json.dumps(plan, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# CMAME Self-Contained Runner Extraction Plan",
        "",
        f"Status: **{plan['status']}**.",
        f"Full-package self-contained runner ready: `{plan['self_contained_runner_ready']}`.",
        f"Local accepted-row self-contained runner ready: `{plan['local_accepted_rows_self_contained_runner_ready']}`.",
        f"Full source-policy self-contained runner ready: `{plan['full_source_policy_self_contained_runner_ready']}`.",
        f"B6 final prose pass ready under narrowed claim: `{plan['b6_final_prose_pass_ready']}`.",
        f"Full source-policy B6 prose ready: `{plan['full_source_policy_b6_prose_ready']}`.",
        f"B6 closure preflight/status: `{plan['b6_closure_preflight_status']}`; allowed `{plan['b6_closure_allowed_now']}`.",
        f"Runner adapter present/self-contained: `{plan['runner_adapter_present']}/{plan['runner_adapter_self_contained']}`.",
        f"P1 local single/double ready: `{p1_audit.get('p1_local_single_double_ready')}`.",
        f"P1 single-runner candidate ready: `{p1_single_candidate_ready}`.",
        f"P1 double-runner candidate ready: `{p1_double_candidate_ready}`.",
        f"P1 regenerated candidate rows: `{p1_regenerated_candidate_rows}/{p1_required_rows}`.",
        f"B6 four-example local evidence runner: `{b6_local_evidence.get('b6_local_evidence_runner_passed')}`; rows `{b6_local_evidence.get('local_rows')}`; self-contained/replay-only `{b6_local_evidence.get('self_contained_examples')}/{b6_local_evidence.get('replay_only_examples')}`.",
        f"P1 audit status: `{p1_audit.get('status')}`.",
        f"P1 v047 primary closure lines: `{p1_audit.get('v047_primary_recursive_internal_dependency_lines')}`.",
        f"Closed-loop local runner candidate: `{closed_loop_candidate.get('status')}`; rows `{closed_loop_candidate.get('closed_loop_local_rows')}`; compact `{closed_loop_candidate.get('candidate_python_line_limit_ok')}`.",
        f"B6 closed-loop extraction audit: `{closed_loop_audit.get('status')}`; target symbols `{closed_loop_audit.get('target_symbol_count')}/{closed_loop_audit.get('target_symbol_lines')}`; ready `{closed_loop_audit.get('self_contained_runner_ready')}`.",
        f"Target source symbols: `{plan['target_symbol_count']}` functions/classes, `{plan['target_symbol_lines']}` symbol lines.",
        f"Source-policy rows closed: `{source_policy_closed}/{source_policy_total}`.",
        f"Direct PC2 proof gap closed: `{proof_closed}`.",
        "",
        "## Phases",
        "",
        "| phase | status | evidence |",
        "|---|---|---|",
    ]
    for phase in phases:
        lines.append(f"| `{phase['id']}` | `{phase['status']}` | {phase['evidence']} |")
    lines.extend(["", "## Target Symbols", "", "| source | symbol | role | lines |", "|---|---|---|---:|"])
    for item in inventory:
        lines.append(
            f"| `{item['path']}` | `{item['symbol']}` | {item['role']} | `{item['symbol_line_count']}` |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("cmame_self_contained_runner_extraction_plan=written")
    print(f"self_contained_runner_ready={plan['self_contained_runner_ready']}")
    print(
        "local_accepted_rows_self_contained_runner_ready="
        f"{plan['local_accepted_rows_self_contained_runner_ready']}"
    )
    print(
        "full_source_policy_self_contained_runner_ready="
        f"{plan['full_source_policy_self_contained_runner_ready']}"
    )
    print(f"target_symbol_count={plan['target_symbol_count']}")
    print(f"target_symbol_lines={plan['target_symbol_lines']}")
    print(f"source_policy_closed={source_policy_closed}/{source_policy_total}")


if __name__ == "__main__":
    main()
