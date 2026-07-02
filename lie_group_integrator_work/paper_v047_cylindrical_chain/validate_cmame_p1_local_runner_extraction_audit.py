#!/usr/bin/env python3
"""Validate the P1 local-runner extraction dependency audit."""

from __future__ import annotations

import ast
import json
import sys
from pathlib import Path


PAPER = Path(__file__).resolve().parent
ROOT = PAPER.parent


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


def resolve_label(path_label: str) -> Path:
    path = Path(path_label)
    if path_label.startswith("lie_group_integrator_work/"):
        return ROOT.parent / path_label
    if path_label.startswith("../"):
        return (PAPER / path_label).resolve()
    return PAPER / path_label


def line_count(path: Path) -> int:
    return len(read_text(path).splitlines())


def top_level_spans(path: Path) -> dict[str, tuple[int, int]]:
    tree = ast.parse(read_text(path), filename=str(path))
    spans: dict[str, tuple[int, int]] = {}
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            spans[node.name] = (node.lineno, int(getattr(node, "end_lineno", node.lineno)))
    return spans


def record_map(records: list[dict]) -> dict[str, dict]:
    return {str(item.get("symbol")): item for item in records}


def main() -> int:
    checks = Checks()
    try:
        audit = read_json(PAPER / "CMAME_P1_LOCAL_RUNNER_EXTRACTION_AUDIT.json")
        audit_md = read_text(PAPER / "CMAME_P1_LOCAL_RUNNER_EXTRACTION_AUDIT.md")
        matrix = read_json(PAPER / "PAPER_NUMERICAL_RESULT_MATRIX.json")
        review = read_json(PAPER / "CMAME_REVIEW_AGENT_REPORT.json")
        single_summary = read_json(
            PAPER / "cmame_p1_single_runner_candidate" / "results" / "single_pendulum_summary.json"
        )
        double_summary = read_json(
            PAPER / "cmame_p1_double_runner_candidate" / "results" / "double_pendulum_summary.json"
        )
    except Exception as exc:  # noqa: BLE001
        print(f"cmame P1 local-runner extraction audit validation: FAIL\n- {exc}")
        return 1

    checks.check(audit.get("schema") == "cmame-p1-local-runner-extraction-audit-v1", "schema changed")
    checks.check(
        audit.get("status") == "closed_single_double_runner_candidates_ready",
        "status changed",
    )
    checks.check(audit.get("read_only") is True, "audit must be read-only")
    checks.check(audit.get("submission_ready") is False, "audit must not mark submission ready")
    checks.check(audit.get("self_contained_runner_ready") is False, "self-contained runner overclaimed")
    checks.check(audit.get("p1_local_single_double_ready") is True, "P1 local rows not recorded as ready")
    checks.check(audit.get("p1_single_runner_candidate_ready") is True, "single-runner candidate not recorded")
    checks.check(audit.get("p1_double_runner_candidate_ready") is True, "double-runner candidate not recorded")
    checks.check(audit.get("p1_regenerated_candidate_rows") == 6, "P1 regenerated candidate row count changed")
    checks.check(audit.get("p1_required_rows") == 6, "P1 required row count changed")
    checks.check(audit.get("p1_missing_candidate_rows") == 0, "P1 missing candidate row count changed")
    checks.check(audit.get("reviewer_facing_python_file_limit") == 12, "file limit changed")
    checks.check(audit.get("reviewer_facing_python_line_limit") == 2000, "line limit changed")

    v047_path = resolve_label(str(audit.get("v047_source")))
    v048_path = resolve_label(str(audit.get("v048_run_source")))
    coarse_path = resolve_label(str(audit.get("v048_coarse_source")))
    checks.check(v047_path.exists(), "v047 source path missing")
    checks.check(v048_path.exists(), "v048 run source path missing")
    checks.check(coarse_path.exists(), "v048 coarse source path missing")
    if v047_path.exists():
        checks.check(audit.get("v047_source_python_lines") == line_count(v047_path) == 69264, "v047 line count changed")
    if v048_path.exists():
        checks.check(audit.get("v048_run_python_lines") == line_count(v048_path) == 5106, "v048 run line count changed")
    if coarse_path.exists():
        checks.check(
            audit.get("v048_coarse_python_lines") == line_count(coarse_path) == 2159,
            "v048 coarse line count changed",
        )

    checks.check(audit.get("paper_matrix_rows") == matrix.get("row_count") == 44, "paper matrix row count changed")
    checks.check(
        audit.get("paper_matrix_raw_rows") == matrix.get("raw_row_count") == 132,
        "paper matrix raw row count changed",
    )
    checks.check(audit.get("common_reference_order_wins") == 40, "common-reference order wins changed")
    checks.check(audit.get("common_reference_error_wins") == 40, "common-reference error wins changed")
    checks.check(
        audit.get("source_policy_closed_rows")
        == review.get("result_checks", {}).get("source_policy_apples_to_apples_external_rows")
        == 0,
        "source-policy closed row count changed",
    )
    checks.check(
        audit.get("source_policy_total_rows")
        == review.get("result_checks", {}).get("source_policy_apples_to_apples_external_total_rows")
        == 40,
        "source-policy total row count changed",
    )
    checks.check(audit.get("p1_target_examples") == ["single_pendulum", "double_pendulum"], "P1 examples changed")
    checks.check(audit.get("p1_required_step_sizes") == [0.1, 0.05, 0.025], "P1 step sizes changed")
    checks.check(audit.get("p1_required_reference_h") == 0.0125, "P1 reference h changed")
    checks.check(audit.get("p1_required_t_end") == 0.1, "P1 time horizon changed")
    candidate = audit.get("p1_single_runner_candidate", {})
    checks.check(
        candidate.get("schema")
        == single_summary.get("schema")
        == "cmame-p1-single-runner-candidate-v1",
        "single candidate schema not carried into P1 audit",
    )
    checks.check(
        candidate.get("status")
        == single_summary.get("status")
        == "single_runner_candidate_not_p1_complete",
        "single candidate status not carried into P1 audit",
    )
    checks.check(candidate.get("example") == single_summary.get("example") == "single_pendulum", "single example changed")
    checks.check(candidate.get("rows") == single_summary.get("rows") == 3, "single candidate rows changed")
    checks.check(candidate.get("h_values") == single_summary.get("h_values") == [0.1, 0.05, 0.025], "single h values changed")
    checks.check(candidate.get("t_final") == single_summary.get("t_final") == 0.1, "single time horizon changed")
    checks.check(candidate.get("p1_single_only_ready") is True, "single-only readiness missing")
    checks.check(candidate.get("p1_complete") is False, "single candidate overclaims P1 completion")
    checks.check(candidate.get("imports_v047_or_v048") is False, "single candidate import boundary changed")
    checks.check(
        candidate.get("source_policy_external_superiority_allowed") is False,
        "single candidate overclaims source-policy superiority",
    )
    checks.check(candidate.get("proof_gap_closed") is False, "single candidate overclaims proof closure")
    checks.check(float(candidate.get("position_order", 0.0)) > 5.0, "single candidate position order too low")
    checks.check(float(candidate.get("velocity_order", 0.0)) > 5.0, "single candidate velocity order too low")
    for label in ["script", "summary", "csv", "validator"]:
        checks.check(resolve_label(str(candidate.get(label))).exists(), f"single candidate path missing: {label}")
    if resolve_label(str(candidate.get("script"))).exists():
        checks.check(
            candidate.get("script_python_lines") == line_count(resolve_label(str(candidate.get("script")))),
            "single candidate script line count stale",
        )
    if resolve_label(str(candidate.get("validator"))).exists():
        checks.check(
            candidate.get("validator_python_lines") == line_count(resolve_label(str(candidate.get("validator")))),
            "single candidate validator line count stale",
        )
    double_candidate = audit.get("p1_double_runner_candidate", {})
    checks.check(
        double_candidate.get("schema")
        == double_summary.get("schema")
        == "cmame-p1-double-runner-candidate-v1",
        "double candidate schema not carried into P1 audit",
    )
    checks.check(
        double_candidate.get("status")
        == double_summary.get("status")
        == "double_runner_candidate_not_source_policy_or_proof_complete",
        "double candidate status not carried into P1 audit",
    )
    checks.check(
        double_candidate.get("example") == double_summary.get("example") == "double_pendulum",
        "double example changed",
    )
    checks.check(double_candidate.get("rows") == double_summary.get("rows") == 3, "double candidate rows changed")
    checks.check(
        double_candidate.get("h_values") == double_summary.get("h_values") == [0.1, 0.05, 0.025],
        "double h values changed",
    )
    checks.check(double_candidate.get("reference_h") == double_summary.get("reference_h") == 0.0125, "double reference h changed")
    checks.check(double_candidate.get("t_final") == double_summary.get("t_final") == 0.1, "double time horizon changed")
    checks.check(double_candidate.get("p1_double_only_ready") is True, "double-only readiness missing")
    checks.check(double_candidate.get("p1_complete") is False, "double candidate overclaims P1 completion")
    checks.check(double_candidate.get("imports_v047_v048_or_v029") is False, "double candidate import boundary changed")
    checks.check(
        double_candidate.get("source_policy_external_superiority_allowed") is False,
        "double candidate overclaims source-policy superiority",
    )
    checks.check(double_candidate.get("proof_gap_closed") is False, "double candidate overclaims proof closure")
    checks.check(float(double_candidate.get("position_order", 0.0)) > 5.0, "double candidate position order too low")
    checks.check(float(double_candidate.get("velocity_order", 0.0)) > 5.0, "double candidate velocity order too low")
    checks.check(float(double_candidate.get("finest_position_error", 1.0)) < 1.0e-10, "double finest position error too large")
    checks.check(float(double_candidate.get("finest_velocity_error", 1.0)) < 1.0e-10, "double finest velocity error too large")
    for label in ["script", "summary", "csv", "validator"]:
        checks.check(resolve_label(str(double_candidate.get(label))).exists(), f"double candidate path missing: {label}")
    if resolve_label(str(double_candidate.get("script"))).exists():
        checks.check(
            double_candidate.get("script_python_lines") == line_count(resolve_label(str(double_candidate.get("script")))),
            "double candidate script line count stale",
        )
    if resolve_label(str(double_candidate.get("validator"))).exists():
        checks.check(
            double_candidate.get("validator_python_lines") == line_count(resolve_label(str(double_candidate.get("validator")))),
            "double candidate validator line count stale",
        )

    wrapper_records = record_map(audit.get("v048_wrapper_symbols", []))
    seed_records = record_map(audit.get("v047_primary_seed_symbols", []))
    optional_records = record_map(audit.get("v047_optional_closed_loop_symbols", []))

    for symbol in [
        "import_v047_single_fullva_module",
        "public_single_reference_alignment",
        "run_gauss6_fullva_public_horizon_single_rows",
        "run_gauss6_fullva_public_horizon_double_coarse_rows",
        "run_local_single_double_rows",
    ]:
        checks.check(symbol in wrapper_records, f"wrapper symbol missing: {symbol}")
        checks.check(wrapper_records.get(symbol, {}).get("exists") is True, f"wrapper symbol not found: {symbol}")

    for symbol in [
        "integrate_asme_single_driven_absolute_fullva",
        "load_v029",
        "make_asme_double_pendulum_params",
        "integrate_v029_asme_double_trajectory",
        "compare_nested_trajectory",
    ]:
        checks.check(symbol in seed_records, f"v047 seed missing: {symbol}")
        checks.check(seed_records.get(symbol, {}).get("exists") is True, f"v047 seed not found: {symbol}")

    for symbol in [
        "load_v046",
        "project_v046_system_to_so3",
        "solve_v046_local_kinematic_fullva_time",
        "reconstruct_v046_reaction_dynamics",
    ]:
        checks.check(symbol in optional_records, f"optional closed-loop seed missing: {symbol}")
        checks.check(optional_records.get(symbol, {}).get("exists") is True, f"optional seed not found: {symbol}")

    single = seed_records.get("integrate_asme_single_driven_absolute_fullva", {})
    checks.check(
        {
            "asme_single_absolute_initial_state",
            "solve_asme_single_absolute_fullva_step",
            "asme_single_absolute_endpoint_diagnostics",
        }.issubset(set(single.get("direct_internal_calls", []))),
        "single-pendulum direct dependencies changed",
    )
    double = seed_records.get("integrate_v029_asme_double_trajectory", {})
    checks.check(
        {"asme_double_world_rotation", "asme_double_pendulum_initial_state"}.issubset(
            set(double.get("direct_internal_calls", []))
        ),
        "double-pendulum direct dependencies changed",
    )
    checks.check(
        {"v029.base_method", "v029.residual_mode", "v029.gauss_step"}.issubset(
            set(double.get("direct_external_attribute_calls", []))
        ),
        "double-pendulum v029 dynamic boundary changed",
    )
    checks.check(
        "asme_bar_mass_inertia"
        in set(seed_records.get("make_asme_double_pendulum_params", {}).get("direct_internal_calls", [])),
        "double parameter bridge dependency changed",
    )

    single_wrapper = wrapper_records.get("run_gauss6_fullva_public_horizon_single_rows", {})
    double_wrapper = wrapper_records.get("run_gauss6_fullva_public_horizon_double_coarse_rows", {})
    checks.check(
        "v047_module.integrate_asme_single_driven_absolute_fullva"
        in set(single_wrapper.get("direct_external_attribute_calls", [])),
        "single wrapper no longer records v047 integration call",
    )
    checks.check(
        {
            "v047_module.load_v029",
            "v047_module.make_asme_double_pendulum_params",
            "v047_module.integrate_v029_asme_double_trajectory",
            "v047_module.compare_nested_trajectory",
        }.issubset(set(double_wrapper.get("direct_external_attribute_calls", []))),
        "double wrapper no longer records v047/v029 bridge calls",
    )

    called = set(audit.get("v048_wrapper_run_v047_symbols_called", []))
    checks.check(
        {
            "integrate_asme_single_driven_absolute_fullva",
            "load_v029",
            "make_asme_double_pendulum_params",
            "integrate_v029_asme_double_trajectory",
            "compare_nested_trajectory",
        }.issubset(called),
        "wrapper-to-v047 call list incomplete",
    )
    checks.check(
        audit.get("v047_primary_direct_internal_dependency_count", 0) >= 5,
        "primary direct dependency count unexpectedly small",
    )
    checks.check(
        audit.get("v047_primary_recursive_internal_dependency_count", 0) >= 10,
        "primary recursive dependency count unexpectedly small",
    )
    checks.check(
        audit.get("v047_primary_recursive_internal_dependency_lines", 0) >= 400,
        "primary recursive dependency line count unexpectedly small",
    )

    dynamic_boundaries = {item.get("id"): item for item in audit.get("dynamic_import_boundaries", [])}
    checks.check(dynamic_boundaries.get("v048_import_v047", {}).get("status") == "open", "v048 import boundary changed")
    checks.check(dynamic_boundaries.get("v047_load_v029", {}).get("status") == "open", "v029 boundary changed")
    criteria = audit.get("acceptance_criteria", {})
    checks.check(criteria.get("forbids_primary_import_run_v047") is True, "run_v047 import criterion changed")
    checks.check(criteria.get("forbids_dynamic_load_v029") is True, "load_v029 criterion changed")
    checks.check(criteria.get("required_rows") == 6, "required P1 row count changed")
    checks.check(criteria.get("required_step_sizes") == [0.1, 0.05, 0.025], "criteria step sizes changed")
    checks.check(criteria.get("required_reference_h") == 0.0125, "criteria reference h changed")
    checks.check(criteria.get("required_t_end") == 0.1, "criteria time horizon changed")

    blockers = {item.get("id"): item for item in audit.get("open_blockers", [])}
    for blocker_id in ["P1B1_primary_v047_import", "P1B2_dynamic_v029_bridge", "P1B3_no_standalone_mechanism_module", "P1B4_no_p1_row_regeneration_certificate"]:
        checks.check(blockers.get(blocker_id, {}).get("status") == "closed", f"{blocker_id} not closed")

    for path, records in [(v047_path, seed_records), (v047_path, optional_records), (v048_path, wrapper_records)]:
        if not path.exists():
            continue
        spans = top_level_spans(path)
        for symbol, record in records.items():
            if record.get("path") != str(path.relative_to(ROOT.parent)):
                continue
            if symbol in spans:
                start, end = spans[symbol]
                checks.check(record.get("start_line") == start, f"start line stale for {symbol}")
                checks.check(record.get("end_line") == end, f"end line stale for {symbol}")
                checks.check(record.get("symbol_line_count") == end - start + 1, f"line count stale for {symbol}")

    for token in [
        "Status: **closed_single_double_runner_candidates_ready**.",
        "P1 local single/double ready: `True`.",
        "P1 single-runner candidate ready: `True`.",
        "P1 double-runner candidate ready: `True`.",
        "P1 regenerated candidate rows: `6/6`.",
        "Self-contained runner ready: `False`.",
        "v047 source size: `69264` Python lines.",
        "Source-policy rows closed: `0/40`.",
        "`P1B1_primary_v047_import`",
        "`P1B2_dynamic_v029_bridge`",
        "`P1B3_no_standalone_mechanism_module`",
        "`P1B4_no_p1_row_regeneration_certificate`",
    ]:
        checks.check(token in audit_md, f"audit markdown missing token: {token}")

    if checks.errors:
        print("cmame P1 local-runner extraction audit validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("cmame P1 local-runner extraction audit validation: PASS")
    print(f"p1_local_single_double_ready={audit.get('p1_local_single_double_ready')}")
    print(f"p1_single_runner_candidate_ready={audit.get('p1_single_runner_candidate_ready')}")
    print(f"p1_double_runner_candidate_ready={audit.get('p1_double_runner_candidate_ready')}")
    print(f"p1_regenerated_candidate_rows={audit.get('p1_regenerated_candidate_rows')}/{audit.get('p1_required_rows')}")
    print(f"v047_source_python_lines={audit.get('v047_source_python_lines')}")
    print(
        "v047_primary_recursive_internal_dependency_count="
        f"{audit.get('v047_primary_recursive_internal_dependency_count')}"
    )
    print(
        "v047_primary_recursive_internal_dependency_lines="
        f"{audit.get('v047_primary_recursive_internal_dependency_lines')}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
