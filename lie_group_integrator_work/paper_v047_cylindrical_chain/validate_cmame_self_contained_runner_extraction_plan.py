#!/usr/bin/env python3
"""Validate the self-contained runner extraction plan."""

from __future__ import annotations

import ast
import json
import sys
from pathlib import Path


PAPER = Path(__file__).resolve().parent


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


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def resolve(path_label: str) -> Path:
    return (PAPER / path_label).resolve() if path_label.startswith("../") else PAPER / path_label


def symbol_spans(path: Path) -> dict[str, tuple[int, int]]:
    tree = ast.parse(read_text(path))
    spans: dict[str, tuple[int, int]] = {}
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            spans[node.name] = (node.lineno, int(getattr(node, "end_lineno", node.lineno)))
    return spans


def main() -> int:
    checks = Checks()
    try:
        plan = read_json(PAPER / "CMAME_SELF_CONTAINED_RUNNER_EXTRACTION_PLAN.json")
        plan_md = read_text(PAPER / "CMAME_SELF_CONTAINED_RUNNER_EXTRACTION_PLAN.md")
        adapter = read_json(PAPER / "CMAME_RUNNER_ADAPTER_CANDIDATE_MANIFEST.json")
        runner_centered = read_json(PAPER / "CMAME_RUNNER_CENTERED_REPRODUCIBILITY_AUDIT.json")
        b6_local_evidence_source = read_json(PAPER / "B6_FOUR_EXAMPLE_LOCAL_EVIDENCE_SUMMARY.json")
        matrix = read_json(PAPER / "PAPER_NUMERICAL_RESULT_MATRIX.json")
        proof = read_json(PAPER / "PROOF_CLOSURE_MANIFEST.json")
        p1_audit_source = read_json(PAPER / "CMAME_P1_LOCAL_RUNNER_EXTRACTION_AUDIT.json")
        closed_loop_audit_source = read_json(PAPER / "B6_CLOSED_LOOP_SELF_CONTAINED_EXTRACTION_AUDIT.json")
        closed_loop_candidate_source = read_json(PAPER / "CMAME_CLOSED_LOOP_LOCAL_RUNNER_CANDIDATE_MANIFEST.json")
    except Exception as exc:  # noqa: BLE001
        print(f"cmame self-contained runner extraction plan validation: FAIL\n- {exc}")
        return 1

    checks.check(
        plan.get("schema") == "cmame-self-contained-runner-extraction-plan-v1",
        "schema changed",
    )
    checks.check(
        plan.get("status") == "local_accepted_rows_self_contained_runner_ready_source_policy_package_open",
        "status changed",
    )
    checks.check(
        "CMAME_P1_LOCAL_RUNNER_EXTRACTION_AUDIT.json" in plan.get("generated_from", []),
        "P1 audit missing from plan provenance",
    )
    checks.check(
        "B6_CLOSED_LOOP_SELF_CONTAINED_EXTRACTION_AUDIT.json" in plan.get("generated_from", []),
        "B6 closed-loop extraction audit missing from plan provenance",
    )
    checks.check(
        "CMAME_CLOSED_LOOP_LOCAL_RUNNER_CANDIDATE_MANIFEST.json" in plan.get("generated_from", []),
        "closed-loop local runner candidate missing from plan provenance",
    )
    checks.check(
        "B6_FOUR_EXAMPLE_LOCAL_EVIDENCE_SUMMARY.json" in plan.get("generated_from", []),
        "B6 local-evidence summary missing from plan provenance",
    )
    checks.check(
        "CMAME_PROSE_RESIDUE_AUDIT.json" in plan.get("generated_from", []),
        "B6 prose residue audit missing from plan provenance",
    )
    checks.check(plan.get("submission_ready") is False, "plan must not mark submission ready")
    checks.check(
        plan.get("self_contained_runner_ready") is False,
        "full-package self-contained runner unexpectedly ready",
    )
    checks.check(
        plan.get("local_accepted_rows_self_contained_runner_ready") is True,
        "local accepted-row self-contained runner readiness missing",
    )
    checks.check(
        plan.get("full_source_policy_self_contained_runner_ready") is False,
        "full source-policy self-contained runner readiness overclaimed",
    )
    checks.check(
        plan.get("b6_final_prose_pass_ready") is True
        and plan.get("b6_final_prose_pass_scope") == "narrowed_claim_current_submission"
        and plan.get("full_source_policy_b6_prose_ready") is False
        and plan.get("b6_closure_preflight_status") == "b6_final_prose_pass_closed_under_narrowed_b4_b7_scope"
        and plan.get("b6_closure_allowed_now") is True,
        "B6 narrowed/full source-policy prose boundary changed",
    )
    boundary = plan.get("runner_package_boundary", {})
    checks.check(
        boundary.get("local_accepted_rows_self_contained") is True
        and boundary.get("full_source_policy_self_contained") is False
        and boundary.get("b6_final_prose_pass_ready") is True
        and boundary.get("b6_final_prose_pass_scope") == "narrowed_claim_current_submission"
        and boundary.get("full_source_policy_b6_prose_ready") is False
        and boundary.get("b6_closure_allowed_now") is True
        and boundary.get("source_policy_rows_closed") == 0
        and boundary.get("source_policy_rows_total") == 40,
        "self-contained runner local/full source-policy boundary stale",
    )
    checks.check(plan.get("runner_adapter_present") == adapter.get("runner_adapter_present") is True, "adapter marker stale")
    checks.check(
        plan.get("runner_adapter_self_contained") == adapter.get("self_contained_simulation_runner") is False,
        "adapter self-contained boundary stale",
    )
    b6_local_evidence = plan.get("b6_four_example_local_evidence", {})
    checks.check(
        b6_local_evidence.get("schema")
        == b6_local_evidence_source.get("schema")
        == "b6-four-example-local-evidence-summary-v1",
        "B6 local-evidence schema not carried into extraction plan",
    )
    checks.check(
        b6_local_evidence.get("runner_passed") == b6_local_evidence_source.get("b6_local_evidence_runner_passed") is True,
        "B6 local-evidence runner pass marker missing",
    )
    checks.check(
        b6_local_evidence.get("local_rows") == b6_local_evidence_source.get("local_rows") == 12,
        "B6 local-evidence rows changed",
    )
    checks.check(
        set(b6_local_evidence.get("self_contained_examples", []))
        == {"single_pendulum", "double_pendulum", "four_link", "slider_crank"},
        "B6 self-contained example set changed",
    )
    checks.check(
        b6_local_evidence.get("replay_only_examples", []) == [],
        "B6 replay-only example set changed",
    )
    checks.check(
        b6_local_evidence.get("four_example_local_evidence_available") is True
        and b6_local_evidence.get("four_example_self_contained_simulation_ready") is True,
        "B6 local/self-contained boundary changed",
    )
    checks.check(plan.get("paper_matrix_rows") == matrix.get("row_count") == 44, "paper matrix rows changed")
    checks.check(plan.get("paper_matrix_raw_rows") == matrix.get("raw_row_count") == 132, "paper matrix raw rows changed")
    checks.check(plan.get("paper_matrix_methods") == matrix.get("method_count") == 11, "paper matrix methods changed")
    checks.check(plan.get("common_reference_order_wins") == 40, "common-reference order wins changed")
    checks.check(plan.get("common_reference_error_wins") == 40, "common-reference error wins changed")
    checks.check(plan.get("source_policy_closed_rows") == 0, "source-policy rows unexpectedly closed")
    checks.check(plan.get("source_policy_total_rows") == 40, "source-policy total rows changed")
    checks.check(plan.get("proof_gap_closed") is True, "proof gap direct closure missing in plan")
    checks.check(
        proof.get("closure_state", {}).get("proof_gap_closed") is True,
        "proof manifest direct closure missing",
    )
    p1_audit = plan.get("p1_local_runner_extraction_audit", {})
    checks.check(
        p1_audit.get("schema")
        == p1_audit_source.get("schema")
        == "cmame-p1-local-runner-extraction-audit-v1",
        "P1 audit schema not carried into extraction plan",
    )
    checks.check(
        p1_audit.get("status")
        == p1_audit_source.get("status")
        == "closed_single_double_runner_candidates_ready",
        "P1 audit status not carried into extraction plan",
    )
    checks.check(
        p1_audit.get("p1_local_single_double_ready")
        == p1_audit_source.get("p1_local_single_double_ready")
        is True,
        "P1 local runner readiness not carried into extraction plan",
    )
    checks.check(
        p1_audit.get("p1_single_runner_candidate_ready")
        == p1_audit_source.get("p1_single_runner_candidate_ready")
        is True,
        "P1 single-runner candidate progress not carried into extraction plan",
    )
    checks.check(
        p1_audit.get("p1_double_runner_candidate_ready")
        == p1_audit_source.get("p1_double_runner_candidate_ready")
        is True,
        "P1 double-runner candidate progress not carried into extraction plan",
    )
    checks.check(
        p1_audit.get("p1_regenerated_candidate_rows")
        == p1_audit_source.get("p1_regenerated_candidate_rows")
        == 6,
        "P1 regenerated candidate row count changed in extraction plan",
    )
    checks.check(
        p1_audit.get("p1_required_rows") == p1_audit_source.get("p1_required_rows") == 6,
        "P1 required row count changed in extraction plan",
    )
    checks.check(
        p1_audit.get("p1_missing_candidate_rows") == p1_audit_source.get("p1_missing_candidate_rows") == 0,
        "P1 missing row count changed in extraction plan",
    )
    checks.check(
        p1_audit.get("p1_single_runner_candidate", {}).get("p1_complete") is False,
        "P1 single candidate overclaims completion in extraction plan",
    )
    checks.check(
        p1_audit.get("p1_double_runner_candidate", {}).get("p1_complete") is False,
        "P1 double candidate overclaims completion in extraction plan",
    )
    checks.check(
        p1_audit.get("v047_source_python_lines") == p1_audit_source.get("v047_source_python_lines") == 69264,
        "P1 v047 source line count stale in extraction plan",
    )
    checks.check(
        p1_audit.get("v047_primary_recursive_internal_dependency_count")
        == p1_audit_source.get("v047_primary_recursive_internal_dependency_count"),
        "P1 recursive dependency count stale in extraction plan",
    )
    checks.check(
        p1_audit.get("v047_primary_recursive_internal_dependency_lines")
        == p1_audit_source.get("v047_primary_recursive_internal_dependency_lines"),
        "P1 recursive dependency line count stale in extraction plan",
    )
    checks.check(p1_audit.get("open_blocker_count") == 0, "P1 open blocker count changed")
    closed_loop_audit = plan.get("b6_closed_loop_self_contained_extraction_audit", {})
    checks.check(
        closed_loop_audit.get("schema")
        == closed_loop_audit_source.get("schema")
        == "b6-closed-loop-self-contained-extraction-audit-v1",
        "B6 closed-loop extraction audit schema not carried into extraction plan",
    )
    checks.check(
        closed_loop_audit.get("status")
        == closed_loop_audit_source.get("status")
        == "closed_loop_self_contained_runner_candidate_ready_source_policy_open",
        "B6 closed-loop extraction audit status not carried into extraction plan",
    )
    checks.check(
        closed_loop_audit.get("self_contained_runner_ready") is True,
        "B6 closed-loop audit did not mark compact runner ready in extraction plan",
    )
    checks.check(
        closed_loop_audit.get("target_source_file_count") == closed_loop_audit_source.get("target_source_file_count") == 2,
        "B6 closed-loop target source count stale in extraction plan",
    )
    checks.check(
        closed_loop_audit.get("target_symbol_count") == closed_loop_audit_source.get("target_symbol_count") >= 30,
        "B6 closed-loop target symbol count stale in extraction plan",
    )
    checks.check(
        closed_loop_audit.get("target_symbol_lines") == closed_loop_audit_source.get("target_symbol_lines"),
        "B6 closed-loop target symbol lines stale in extraction plan",
    )
    checks.check(
        closed_loop_audit.get("replay_only_closed_loop_examples", []) == [],
        "B6 closed-loop replay-only examples changed in extraction plan",
    )
    checks.check(
        closed_loop_audit.get("closed_loop_local_replay_rows") == 6,
        "B6 closed-loop replay row count changed in extraction plan",
    )
    checks.check(
        closed_loop_audit.get("run_v047_invoked") is False
        and closed_loop_audit.get("run_v048_invoked") is False
        and closed_loop_audit.get("b4_opt_in_required_for_this_audit") is False,
        "B6 closed-loop extraction audit execution boundary changed in extraction plan",
    )
    closed_loop_candidate = plan.get("closed_loop_local_runner_candidate", {})
    checks.check(
        closed_loop_candidate.get("schema") == closed_loop_candidate_source.get("schema"),
        "closed-loop candidate schema not carried into plan",
    )
    checks.check(
        closed_loop_candidate.get("status")
        == closed_loop_candidate_source.get("status")
        == "closed_loop_local_runner_candidate_passed_compact",
        "closed-loop candidate status not carried into plan",
    )
    checks.check(closed_loop_candidate.get("runner_passed") is True, "closed-loop candidate did not pass in plan")
    checks.check(
        closed_loop_candidate.get("self_contained_simulation_runner") is True,
        "closed-loop candidate self-contained marker missing in plan",
    )
    checks.check(
        closed_loop_candidate.get("candidate_python_file_count") == 10
        and 0 < closed_loop_candidate.get("candidate_python_line_count", 0) <= 2000
        and closed_loop_candidate.get("candidate_python_line_limit_ok") is True,
        "closed-loop candidate compact size not carried into plan",
    )
    checks.check(
        closed_loop_candidate.get("imports_v046_v047_v048_or_v029") is False,
        "closed-loop candidate forbidden import marker set in plan",
    )
    checks.check(
        closed_loop_candidate.get("closed_loop_local_rows") == 6
        and set(closed_loop_candidate.get("closed_loop_models", [])) == {"four_link", "slider_crank"},
        "closed-loop candidate rows/models not carried into plan",
    )
    checks.check(
        closed_loop_candidate.get("source_policy_external_rows_closed") == 0
        and closed_loop_candidate.get("source_policy_external_rows_total") == 40
        and closed_loop_candidate.get("source_policy_external_superiority_allowed") is False
        and closed_loop_candidate.get("submission_ready") is False,
        "closed-loop candidate overclaimed source policy or submission readiness in plan",
    )
    existing_runner_source_lines = runner_centered.get("existing_runner_source_total_python_lines")
    checks.check(
        isinstance(existing_runner_source_lines, int) and existing_runner_source_lines > 0,
        "runner-centered source line count missing",
    )
    checks.check(
        plan.get("existing_runner_source_lines") == existing_runner_source_lines,
        "existing runner source line count stale",
    )

    target_symbols = plan.get("target_symbols", [])
    checks.check(plan.get("target_symbol_count") == len(target_symbols) >= 30, "target symbol count changed")
    total_symbol_lines = 0
    for item in target_symbols:
        path = resolve(str(item.get("path")))
        checks.check(path.exists(), f"source path missing: {item.get('path')}")
        if not path.exists():
            continue
        spans = symbol_spans(path)
        symbol = str(item.get("symbol"))
        checks.check(symbol in spans, f"symbol missing: {item.get('path')}::{symbol}")
        if symbol in spans:
            start, end = spans[symbol]
            line_count = end - start + 1
            total_symbol_lines += line_count
            checks.check(item.get("start_line") == start, f"start line stale for {symbol}")
            checks.check(item.get("end_line") == end, f"end line stale for {symbol}")
            checks.check(item.get("symbol_line_count") == line_count, f"line count stale for {symbol}")
    checks.check(plan.get("target_symbol_lines") == total_symbol_lines, "target symbol total line count stale")
    checks.check(total_symbol_lines > 2000, "target symbols unexpectedly below reviewer line limit")

    phases = {item.get("id"): item for item in plan.get("phases", [])}
    checks.check(phases.get("P0_report_adapter", {}).get("status") == "partial_complete", "adapter phase should be partial")
    checks.check(phases.get("P1_local_gauss6_rows", {}).get("status") == "closed", "P1 local phase not closed")
    checks.check(
        phases.get("P1b_four_example_local_evidence_runner", {}).get("status") == "closed",
        "P1b four-example local-evidence phase not closed",
    )
    checks.check(
        phases.get("P1c_closed_loop_self_contained_runner", {}).get("status")
        == "closed_compact_candidate_passed",
        "P1c closed-loop self-contained runner phase should record passed compact candidate",
    )
    for phase_id in ["P2_external_public_baselines", "P3_tfe_source_policy_rows"]:
        checks.check(phases.get(phase_id, {}).get("status") == "open", f"{phase_id} unexpectedly closed")
    checks.check(
        phases.get("P4_proof_boundary", {}).get("status") == "closed",
        "P4 proof boundary should be closed after direct proof closure",
    )
    criteria = plan.get("acceptance_criteria", {})
    checks.check(criteria.get("max_python_files") == 12, "file limit changed")
    checks.check(criteria.get("max_python_lines") == 2000, "line limit changed")
    checks.check(criteria.get("regenerates_paper_matrix_rows") == 44, "matrix regeneration target changed")
    checks.check(criteria.get("regenerates_raw_rows") == 132, "raw-row regeneration target changed")
    checks.check(criteria.get("forbids_primary_import_run_v048") is True, "run_v048 import boundary changed")
    checks.check(criteria.get("forbids_primary_import_run_v047") is True, "run_v047 import boundary changed")

    for token in [
        "Status: **local_accepted_rows_self_contained_runner_ready_source_policy_package_open**.",
        "Full-package self-contained runner ready: `False`.",
        "Local accepted-row self-contained runner ready: `True`.",
        "Full source-policy self-contained runner ready: `False`.",
        "B6 final prose pass ready under narrowed claim: `True`.",
        "Full source-policy B6 prose ready: `False`.",
        "B6 closure preflight/status: `b6_final_prose_pass_closed_under_narrowed_b4_b7_scope`; allowed `True`.",
        "Runner adapter present/self-contained: `True/False`.",
        "P1 local single/double ready: `True`.",
        "P1 single-runner candidate ready: `True`.",
        "P1 double-runner candidate ready: `True`.",
        "P1 regenerated candidate rows: `6/6`.",
        "B6 four-example local evidence runner: `True`; rows `12`;",
        "P1 audit status: `closed_single_double_runner_candidates_ready`.",
        "Closed-loop local runner candidate: `closed_loop_local_runner_candidate_passed_compact`; rows `6`; compact `True`.",
        "B6 closed-loop extraction audit: `closed_loop_self_contained_runner_candidate_ready_source_policy_open`;",
        "Source-policy rows closed: `0/40`.",
        "Direct PC2 proof gap closed: `True`.",
        "`P0_report_adapter`",
        "`P1_local_gauss6_rows`",
        "`P1b_four_example_local_evidence_runner`",
        "`P1c_closed_loop_self_contained_runner`",
        "`P2_external_public_baselines`",
        "`P3_tfe_source_policy_rows`",
    ]:
        checks.check(token in plan_md, f"plan markdown missing token: {token}")

    if checks.errors:
        print("cmame self-contained runner extraction plan validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("cmame self-contained runner extraction plan validation: PASS")
    print(f"self_contained_runner_ready={plan.get('self_contained_runner_ready')}")
    print(
        "local_accepted_rows_self_contained_runner_ready="
        f"{plan.get('local_accepted_rows_self_contained_runner_ready')}"
    )
    print(
        "full_source_policy_self_contained_runner_ready="
        f"{plan.get('full_source_policy_self_contained_runner_ready')}"
    )
    print(f"target_symbol_count={plan.get('target_symbol_count')}")
    print(f"target_symbol_lines={plan.get('target_symbol_lines')}")
    print(f"b6_local_evidence_rows={b6_local_evidence.get('local_rows')}")
    print(f"source_policy_closed={plan.get('source_policy_closed_rows')}/{plan.get('source_policy_total_rows')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
