#!/usr/bin/env python3
"""Validate the B6 closed-loop self-contained extraction audit."""

from __future__ import annotations

import ast
import json
import sys
from pathlib import Path


PAPER = Path(__file__).resolve().parent
from paper_paths import LATEX, package_path as manuscript_path


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
    return (manuscript_path(path_label)).resolve() if path_label.startswith("../") else manuscript_path(path_label)


def symbol_spans(path: Path) -> dict[str, tuple[int, int]]:
    tree = ast.parse(read_text(path))
    spans: dict[str, tuple[int, int]] = {}
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            spans[node.name] = (node.lineno, int(getattr(node, "end_lineno", node.lineno)))
    return spans


def line_count(path: Path) -> int:
    return len(read_text(path).splitlines())


def main() -> int:
    checks = Checks()
    try:
        audit = read_json(PAPER / "B6_CLOSED_LOOP_SELF_CONTAINED_EXTRACTION_AUDIT.json")
        audit_md = read_text(PAPER / "B6_CLOSED_LOOP_SELF_CONTAINED_EXTRACTION_AUDIT.md")
        runner_adapter = read_json(PAPER / "CMAME_RUNNER_ADAPTER_CANDIDATE_MANIFEST.json")
        b6_local_evidence = read_json(PAPER / "B6_FOUR_EXAMPLE_LOCAL_EVIDENCE_SUMMARY.json")
        review = read_json(PAPER / "CMAME_REVIEW_AGENT_REPORT.json")
        closed_loop_candidate_source = read_json(PAPER / "CMAME_CLOSED_LOOP_LOCAL_RUNNER_CANDIDATE_MANIFEST.json")
        coarse = read_json(
            PAPER / "../../numerics/v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_newton_coarse_order.json"
        )
        strict_common = read_json(
            PAPER / "../../numerics/v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_strict_common_reference.json"
        )
    except Exception as exc:  # noqa: BLE001
        print(f"B6 closed-loop self-contained extraction audit validation: FAIL\n- {exc}")
        return 1

    result_checks = review.get("result_checks", {})
    checks.check(
        audit.get("schema") == "b6-closed-loop-self-contained-extraction-audit-v1",
        "schema changed",
    )
    checks.check(
        "CMAME_CLOSED_LOOP_LOCAL_RUNNER_CANDIDATE_MANIFEST.json" in audit.get("generated_from", []),
        "closed-loop runner candidate missing from audit provenance",
    )
    checks.check(
        audit.get("status") == "closed_loop_self_contained_runner_candidate_ready_source_policy_open",
        "status changed",
    )
    checks.check(audit.get("submission_ready") is False, "audit must not mark submission ready")
    checks.check(audit.get("self_contained_runner_ready") is True, "closed-loop compact runner candidate not marked ready")
    checks.check(audit.get("b4_opt_in_required_for_this_audit") is False, "B4 opt-in should not be needed for audit")
    checks.check(audit.get("run_v047_invoked") is False, "audit must not invoke run_v047")
    checks.check(audit.get("run_v048_invoked") is False, "audit must not invoke run_v048")
    checks.check(audit.get("heavy_numerical_run_invoked") is False, "audit must not run heavy numerical campaigns")
    checks.check(audit.get("source_policy_external_superiority_allowed") is False, "external superiority boundary changed")
    checks.check(
        audit.get("source_policy_external_rows_closed")
        == result_checks.get("source_policy_apples_to_apples_external_rows")
        == 0,
        "source-policy closed rows changed",
    )
    checks.check(
        audit.get("source_policy_external_rows_total")
        == result_checks.get("source_policy_apples_to_apples_external_total_rows")
        == 40,
        "source-policy total rows changed",
    )
    checks.check(audit.get("closed_loop_models") == ["four_link", "slider_crank"], "closed-loop model set changed")
    checks.check(audit.get("step_sizes") == [0.1, 0.05, 0.025], "closed-loop step sizes changed")
    checks.check(
        audit.get("replay_only_closed_loop_examples", []) == [],
        "closed-loop replay-only examples changed",
    )
    checks.check(
        set(audit.get("self_contained_examples_after_closed_loop_candidate", []))
        == {"single_pendulum", "double_pendulum", "four_link", "slider_crank"},
        "post-candidate self-contained example set changed",
    )
    checks.check(
        audit.get("closed_loop_local_replay_rows") == runner_adapter.get("closed_loop_local_rows") == 6,
        "closed-loop replay row count changed",
    )
    checks.check(
        audit.get("closed_loop_local_replay_present")
        == runner_adapter.get("closed_loop_local_rows_replay_present")
        is True,
        "closed-loop replay marker missing",
    )
    checks.check(
        audit.get("closed_loop_local_rows_summary_present")
        == runner_adapter.get("closed_loop_local_rows_summary_present")
        is True,
        "closed-loop replay summary marker missing",
    )
    checks.check(
        b6_local_evidence.get("human_runnable_four_example_self_contained_simulation_ready") is True,
        "B6 local evidence did not mark four-example self-contained simulation ready",
    )
    checks.check(
        audit.get("coarse_order_status") == coarse.get("status"),
        "coarse-order status not carried into audit",
    )
    checks.check(
        audit.get("coarse_order_accepted_dynamic_order_count")
        == coarse.get("accepted_dynamic_order_count")
        == 2,
        "coarse-order accepted count changed",
    )
    checks.check(
        audit.get("coarse_order_simulate_runner_implemented") == coarse.get("simulate_runner_implemented") is True,
        "coarse-order runner marker not carried into audit",
    )
    checks.check(
        audit.get("strict_common_reference_status") == strict_common.get("status"),
        "strict common-reference status not carried into audit",
    )
    checks.check(
        set(audit.get("strict_common_reference_available_examples", [])) == {"four_link", "slider_crank"},
        "strict common-reference examples changed",
    )
    closed_loop_candidate = audit.get("closed_loop_local_runner_candidate", {})
    checks.check(
        closed_loop_candidate.get("schema") == closed_loop_candidate_source.get("schema"),
        "closed-loop candidate schema not carried into audit",
    )
    checks.check(
        closed_loop_candidate.get("status")
        == closed_loop_candidate_source.get("status")
        == "closed_loop_local_runner_candidate_passed_compact",
        "closed-loop candidate status not carried into audit",
    )
    checks.check(closed_loop_candidate.get("runner_passed") is True, "closed-loop candidate did not pass")
    checks.check(
        closed_loop_candidate.get("self_contained_simulation_runner") is True,
        "closed-loop candidate self-contained marker missing",
    )
    checks.check(
        closed_loop_candidate.get("candidate_python_file_count")
        == closed_loop_candidate_source.get("candidate_python_file_count")
        == 10,
        "closed-loop candidate Python file count stale",
    )
    checks.check(
        closed_loop_candidate.get("candidate_python_line_count")
        == closed_loop_candidate_source.get("candidate_python_line_count")
        and 0 < closed_loop_candidate.get("candidate_python_line_count", 0) <= 2000,
        "closed-loop candidate Python line count stale",
    )
    checks.check(
        closed_loop_candidate.get("candidate_python_line_limit_ok") is True,
        "closed-loop candidate compact marker missing",
    )
    checks.check(
        closed_loop_candidate.get("imports_v046_v047_v048_or_v029") is False,
        "closed-loop candidate forbidden import marker set",
    )
    checks.check(closed_loop_candidate.get("closed_loop_local_rows") == 6, "closed-loop candidate row count stale")
    checks.check(
        set(closed_loop_candidate.get("closed_loop_models", [])) == {"four_link", "slider_crank"},
        "closed-loop candidate model set stale",
    )
    checks.check(closed_loop_candidate.get("step_sizes") == [0.1, 0.05, 0.025], "candidate step sizes stale")
    checks.check(
        closed_loop_candidate.get("run_v047_invoked") is False
        and closed_loop_candidate.get("run_v048_invoked") is False,
        "closed-loop candidate invoked v047/v048",
    )
    checks.check(
        closed_loop_candidate.get("source_policy_external_superiority_allowed") is False
        and closed_loop_candidate.get("source_policy_external_rows_closed") == 0
        and closed_loop_candidate.get("source_policy_external_rows_total") == 40,
        "closed-loop candidate overclaimed source policy",
    )

    target_sources = audit.get("target_source_files", [])
    checks.check(audit.get("target_source_file_count") == len(target_sources) == 2, "target source file count changed")
    total_source_lines = 0
    expected_paths = {
        "../../numerics/v048_cross_paper_same_test_benchmarks/build_closed_loop_true_dynamic_newton_coarse_order.py",
        "../../numerics/v048_cross_paper_same_test_benchmarks/closed_loop_fullva_dynamic_residual.py",
    }
    checks.check({item.get("path") for item in target_sources} == expected_paths, "target source set changed")
    for item in target_sources:
        path = resolve(str(item.get("path")))
        checks.check(path.exists(), f"target source missing: {item.get('path')}")
        if path.exists():
            count = line_count(path)
            total_source_lines += count
            checks.check(item.get("python_lines") == count, f"target source line count stale: {item.get('path')}")
    checks.check(audit.get("target_source_file_lines") == total_source_lines, "target source total line count stale")

    target_symbols = audit.get("target_symbols", [])
    checks.check(audit.get("target_symbol_count") == len(target_symbols) >= 30, "target symbol count too small")
    total_symbol_lines = 0
    for item in target_symbols:
        path = resolve(str(item.get("path")))
        symbol = str(item.get("symbol"))
        if not path.exists():
            continue
        spans = symbol_spans(path)
        checks.check(symbol in spans, f"target symbol missing: {item.get('path')}::{symbol}")
        if symbol in spans:
            start, end = spans[symbol]
            line_total = end - start + 1
            total_symbol_lines += line_total
            checks.check(item.get("start_line") == start, f"target symbol start line stale: {symbol}")
            checks.check(item.get("end_line") == end, f"target symbol end line stale: {symbol}")
            checks.check(item.get("symbol_line_count") == line_total, f"target symbol line count stale: {symbol}")
    checks.check(audit.get("target_symbol_lines") == total_symbol_lines, "target symbol line total stale")
    checks.check(total_symbol_lines < 2000, "closed-loop symbol target unexpectedly exceeds reviewer line limit")

    inventory = audit.get("v048_total_python_inventory", {})
    checks.check(inventory.get("python_file_count", 0) > 50, "v048 source inventory unexpectedly small")
    checks.check(inventory.get("python_line_count", 0) > 20000, "v048 source line inventory unexpectedly small")
    blockers = {item.get("id"): item for item in audit.get("extraction_blockers", [])}
    checks.check(
        blockers.get("CL1_v047_loader_dependency", {}).get("status") == "bypassed_by_compact_candidate",
        "CL1 compact-candidate bypass not recorded",
    )
    checks.check(
        blockers.get("CL2_closed_loop_model_definitions", {}).get("status") == "satisfied_by_compact_candidate",
        "CL2 compact-candidate model definition closure not recorded",
    )
    checks.check(
        blockers.get("CL3_primary_submission_runner", {}).get("status") == "satisfied_compact_candidate_passed",
        "CL3 should record the passed compact candidate",
    )
    checks.check(
        blockers.get("CL4_candidate_size_limit", {}).get("status") == "satisfied",
        "CL4 candidate size blocker should be satisfied",
    )
    criteria = audit.get("acceptance_criteria", {})
    checks.check(criteria.get("candidate_package") == "cmame_closed_loop_local_runner_candidate", "candidate package changed")
    checks.check(criteria.get("max_python_lines") == 2000, "closed-loop package line limit changed")
    checks.check(set(criteria.get("must_not_import", [])) == {"run_v047.py", "run_v048.py", "v029", "v046"}, "import ban changed")
    checks.check(criteria.get("regenerates_closed_loop_local_rows") == 6, "closed-loop row target changed")
    checks.check(criteria.get("source_policy_external_superiority_allowed") is False, "criteria overclaims superiority")

    for token in [
        "Status: **closed_loop_self_contained_runner_candidate_ready_source_policy_open**.",
        "Self-contained closed-loop runner ready: `True`.",
        "B4 opt-in required for this audit: `False`.",
        "Run v047/v048 invoked: `False/False`.",
        "Closed-loop replay-only examples: `[]`.",
        "Closed-loop local replay rows: `6`.",
        "Closed-loop candidate status: `closed_loop_local_runner_candidate_passed_compact`.",
        "Closed-loop candidate rows: `6`.",
        "Closed-loop candidate Python files/lines: `10/",
        "Closed-loop candidate line limit ok: `True`.",
        "Source-policy rows closed: `0/40`.",
        "`CL1_v047_loader_dependency`",
        "`CL2_closed_loop_model_definitions`",
        "`CL3_primary_submission_runner`",
        "`CL4_candidate_size_limit`",
        "cmame_closed_loop_local_runner_candidate",
    ]:
        checks.check(token in audit_md, f"markdown missing token: {token}")

    if checks.errors:
        print("B6 closed-loop self-contained extraction audit validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("B6 closed-loop self-contained extraction audit validation: PASS")
    print(f"self_contained_runner_ready={audit.get('self_contained_runner_ready')}")
    print(f"target_symbol_count={audit.get('target_symbol_count')}")
    print(f"target_symbol_lines={audit.get('target_symbol_lines')}")
    print(
        "source_policy_closed="
        f"{audit.get('source_policy_external_rows_closed')}/{audit.get('source_policy_external_rows_total')}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
