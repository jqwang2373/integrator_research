#!/usr/bin/env python3
"""Build the P1 local-runner extraction dependency audit.

This is a read-only AST audit.  It does not import run_v047.py, run v048, or
execute numerical experiments.  Its purpose is to make the local single/double
runner gap explicit before we try to extract a reviewer-facing code package.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path


PAPER = Path(__file__).resolve().parent
ROOT = PAPER.parent
V047_RUN = ROOT.parent / "numerics" / "v047_cylindrical_chain_pipeline" / "run_v047.py"
V048_RUN = ROOT.parent / "numerics" / "v048_cross_paper_same_test_benchmarks" / "run_v048.py"
V048_COARSE = ROOT.parent / "numerics" / "v048_cross_paper_same_test_benchmarks" / "run_coarse_four_example_order.py"
P1_SINGLE_CANDIDATE = PAPER / "cmame_p1_single_runner_candidate"
P1_SINGLE_SCRIPT = P1_SINGLE_CANDIDATE / "scripts" / "run_single_pendulum_fullva.py"
P1_SINGLE_SUMMARY = P1_SINGLE_CANDIDATE / "results" / "single_pendulum_summary.json"
P1_SINGLE_CSV = P1_SINGLE_CANDIDATE / "results" / "single_pendulum_rows.csv"
P1_SINGLE_VALIDATOR = PAPER / "validate_cmame_p1_single_runner_candidate.py"
P1_DOUBLE_CANDIDATE = PAPER / "cmame_p1_double_runner_candidate"
P1_DOUBLE_SCRIPT = P1_DOUBLE_CANDIDATE / "scripts" / "run_double_pendulum_fullva.py"
P1_DOUBLE_SUMMARY = P1_DOUBLE_CANDIDATE / "results" / "double_pendulum_summary.json"
P1_DOUBLE_CSV = P1_DOUBLE_CANDIDATE / "results" / "double_pendulum_rows.csv"
P1_DOUBLE_VALIDATOR = PAPER / "validate_cmame_p1_double_runner_candidate.py"
OUT_JSON = PAPER / "CMAME_P1_LOCAL_RUNNER_EXTRACTION_AUDIT.json"
OUT_MD = PAPER / "CMAME_P1_LOCAL_RUNNER_EXTRACTION_AUDIT.md"

REVIEWER_FILE_LIMIT = 12
REVIEWER_LINE_LIMIT = 2000
P1_STEP_SIZES = [0.1, 0.05, 0.025]
P1_REFERENCE_H = 0.0125
P1_T_END = 0.1

V047_PRIMARY_SEEDS = [
    ("integrate_asme_single_driven_absolute_fullva", "single_pendulum_local_gauss6_fullva"),
    ("load_v029", "dynamic_double_pendulum_source_loader"),
    ("make_asme_double_pendulum_params", "double_pendulum_asme_parameter_bridge"),
    ("integrate_v029_asme_double_trajectory", "double_pendulum_local_gauss6_fullva_trajectory"),
    ("compare_nested_trajectory", "double_pendulum_reference_error_metric"),
]

V047_OPTIONAL_CLOSED_LOOP_SEEDS = [
    ("load_v046", "dynamic_four_link_slider_crank_source_loader"),
    ("project_v046_system_to_so3", "closed_loop_projection_helper"),
    ("solve_v046_local_kinematic_fullva_time", "closed_loop_kinematic_solver"),
    ("reconstruct_v046_reaction_dynamics", "closed_loop_reaction_reconstruction"),
]

V048_WRAPPERS = [
    (V048_RUN, "import_v047_single_fullva_module", "dynamic_v047_import_boundary"),
    (V048_RUN, "public_single_reference_alignment", "single_public_reference_alignment"),
    (V048_RUN, "run_gauss6_fullva_public_horizon_single_rows", "single_local_row_wrapper"),
    (V048_RUN, "run_gauss6_fullva_public_horizon_double_coarse_rows", "double_local_row_wrapper"),
    (V048_COARSE, "run_local_single_double_rows", "coarse_four_example_local_entry"),
]

EXTERNAL_OBJECT_NAMES = {"module", "rv", "v047_module", "v029", "spec", "loader", "np", "time", "sys"}


def read_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def read_optional_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return read_json(path)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def label_path(path: Path) -> str:
    try:
        return str(path.relative_to(PAPER))
    except ValueError:
        return str(path.relative_to(ROOT.parent))


def line_count(path: Path) -> int:
    return len(read_text(path).splitlines())


def optional_line_count(path: Path) -> int:
    return line_count(path) if path.exists() else 0


def parse(path: Path) -> ast.Module:
    return ast.parse(read_text(path), filename=str(path))


def top_level_nodes(path: Path) -> dict[str, ast.AST]:
    tree = parse(path)
    out: dict[str, ast.AST] = {}
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            out[node.name] = node
    return out


def node_span(node: ast.AST | None) -> tuple[int, int, int]:
    if node is None:
        return 0, 0, 0
    start = int(getattr(node, "lineno", 0))
    end = int(getattr(node, "end_lineno", start))
    return start, end, end - start + 1


class CallCollector(ast.NodeVisitor):
    def __init__(self) -> None:
        self.name_calls: set[str] = set()
        self.attribute_calls: set[str] = set()
        self.external_attribute_calls: set[str] = set()

    def visit_Call(self, node: ast.Call) -> None:  # noqa: N802
        func = node.func
        if isinstance(func, ast.Name):
            self.name_calls.add(func.id)
        elif isinstance(func, ast.Attribute):
            self.attribute_calls.add(func.attr)
            if isinstance(func.value, ast.Name) and func.value.id in EXTERNAL_OBJECT_NAMES:
                self.external_attribute_calls.add(f"{func.value.id}.{func.attr}")
        self.generic_visit(node)


def collect_calls(node: ast.AST | None) -> CallCollector:
    collector = CallCollector()
    if node is not None:
        collector.visit(node)
    return collector


def symbol_record(path: Path, symbol: str, role: str, top_symbols: dict[str, ast.AST]) -> dict[str, object]:
    node = top_symbols.get(symbol)
    start, end, lines = node_span(node)
    calls = collect_calls(node)
    direct_internal = sorted(name for name in calls.name_calls if name in top_symbols and name != symbol)
    return {
        "path": label_path(path),
        "symbol": symbol,
        "role": role,
        "exists": node is not None,
        "start_line": start,
        "end_line": end,
        "symbol_line_count": lines,
        "direct_internal_calls": direct_internal,
        "direct_internal_call_count": len(direct_internal),
        "direct_external_attribute_calls": sorted(calls.external_attribute_calls),
        "direct_external_attribute_call_count": len(calls.external_attribute_calls),
        "direct_call_names": sorted(calls.name_calls),
        "direct_attribute_call_names": sorted(calls.attribute_calls),
    }


def recursive_closure(seed_symbols: list[str], top_symbols: dict[str, ast.AST]) -> list[str]:
    seen: set[str] = set()
    pending = list(seed_symbols)
    while pending:
        symbol = pending.pop(0)
        if symbol in seen or symbol not in top_symbols:
            continue
        seen.add(symbol)
        calls = collect_calls(top_symbols[symbol])
        for name in sorted(calls.name_calls):
            if name in top_symbols and name not in seen:
                pending.append(name)
    return sorted(seen)


def closure_line_count(symbols: list[str], top_symbols: dict[str, ast.AST]) -> int:
    total = 0
    for symbol in symbols:
        _start, _end, lines = node_span(top_symbols.get(symbol))
        total += lines
    return total


def main() -> None:
    review = read_json(PAPER / "CMAME_REVIEW_AGENT_REPORT.json")
    matrix = read_json(PAPER / "PAPER_NUMERICAL_RESULT_MATRIX.json")
    single_summary = read_optional_json(P1_SINGLE_SUMMARY)
    double_summary = read_optional_json(P1_DOUBLE_SUMMARY)

    v047_symbols = top_level_nodes(V047_RUN)
    v048_symbols = top_level_nodes(V048_RUN)
    v048_coarse_symbols = top_level_nodes(V048_COARSE)

    v047_seed_records = [
        symbol_record(V047_RUN, symbol, role, v047_symbols) for symbol, role in V047_PRIMARY_SEEDS
    ]
    optional_records = [
        symbol_record(V047_RUN, symbol, role, v047_symbols) for symbol, role in V047_OPTIONAL_CLOSED_LOOP_SEEDS
    ]
    wrapper_records = []
    for path, symbol, role in V048_WRAPPERS:
        top = v048_symbols if path == V048_RUN else v048_coarse_symbols
        wrapper_records.append(symbol_record(path, symbol, role, top))

    primary_seed_names = [symbol for symbol, _role in V047_PRIMARY_SEEDS]
    primary_closure = recursive_closure(primary_seed_names, v047_symbols)
    primary_closure_lines = closure_line_count(primary_closure, v047_symbols)

    primary_direct_deps = sorted(
        {
            dep
            for record in v047_seed_records
            for dep in record["direct_internal_calls"]
            if isinstance(dep, str)
        }
    )
    wrapper_v047_attribute_calls = sorted(
        {
            call
            for record in wrapper_records
            for call in record["direct_external_attribute_calls"]
            if isinstance(call, str) and call.startswith("v047_module.")
        }
    )
    wrapper_run_v047_calls = sorted(call.replace("v047_module.", "") for call in wrapper_v047_attribute_calls)

    source_policy_closed = review.get("result_checks", {}).get("source_policy_apples_to_apples_external_rows")
    source_policy_total = review.get("result_checks", {}).get("source_policy_apples_to_apples_external_total_rows")
    single_candidate_ready = (
        single_summary.get("schema") == "cmame-p1-single-runner-candidate-v1"
        and single_summary.get("status") == "single_runner_candidate_not_p1_complete"
        and single_summary.get("example") == "single_pendulum"
        and single_summary.get("rows") == 3
        and single_summary.get("h_values") == P1_STEP_SIZES
        and single_summary.get("t_final") == P1_T_END
        and single_summary.get("p1_single_only_ready") is True
        and single_summary.get("p1_complete") is False
        and single_summary.get("imports_v047_or_v048") is False
        and single_summary.get("source_policy_external_superiority_allowed") is False
        and single_summary.get("proof_gap_closed") is False
        and float(single_summary.get("position_order", 0.0)) > 5.0
        and float(single_summary.get("velocity_order", 0.0)) > 5.0
        and P1_SINGLE_SCRIPT.exists()
        and P1_SINGLE_CSV.exists()
        and P1_SINGLE_VALIDATOR.exists()
    )
    double_candidate_ready = (
        double_summary.get("schema") == "cmame-p1-double-runner-candidate-v1"
        and double_summary.get("status") == "double_runner_candidate_not_source_policy_or_proof_complete"
        and double_summary.get("example") == "double_pendulum"
        and double_summary.get("rows") == 3
        and double_summary.get("h_values") == P1_STEP_SIZES
        and double_summary.get("reference_h") == P1_REFERENCE_H
        and double_summary.get("t_final") == P1_T_END
        and double_summary.get("p1_double_only_ready") is True
        and double_summary.get("p1_complete") is False
        and double_summary.get("imports_v047_v048_or_v029") is False
        and double_summary.get("source_policy_external_superiority_allowed") is False
        and double_summary.get("proof_gap_closed") is False
        and float(double_summary.get("position_order", 0.0)) > 5.0
        and float(double_summary.get("velocity_order", 0.0)) > 5.0
        and P1_DOUBLE_SCRIPT.exists()
        and P1_DOUBLE_CSV.exists()
        and P1_DOUBLE_VALIDATOR.exists()
    )
    regenerated_candidate_rows = (
        (int(single_summary.get("rows", 0)) if single_candidate_ready else 0)
        + (int(double_summary.get("rows", 0)) if double_candidate_ready else 0)
    )
    p1_local_ready = single_candidate_ready and double_candidate_ready and regenerated_candidate_rows == 6
    audit_status = (
        "closed_single_double_runner_candidates_ready"
        if p1_local_ready
        else ("open_single_runner_candidate_double_missing" if single_candidate_ready else "open_v047_local_runner_dependencies_not_extracted")
    )

    acceptance = {
        "forbids_primary_import_run_v047": True,
        "forbids_dynamic_load_v029": True,
        "requires_self_contained_single_mechanism": True,
        "requires_self_contained_double_mechanism": True,
        "requires_regenerated_examples": ["single_pendulum", "double_pendulum"],
        "required_step_sizes": P1_STEP_SIZES,
        "required_reference_h": P1_REFERENCE_H,
        "required_t_end": P1_T_END,
        "required_rows": 6,
        "max_python_files": REVIEWER_FILE_LIMIT,
        "max_python_lines": REVIEWER_LINE_LIMIT,
    }

    blockers = [
        {
            "id": "P1B1_primary_v047_import",
            "status": "closed" if p1_local_ready else "open",
            "evidence": (
                "standalone P1 single/double candidates regenerate local rows without importing run_v047.py"
                if p1_local_ready
                else "v048 local wrappers call import_v047_single_fullva_module before running local rows"
            ),
        },
        {
            "id": "P1B2_dynamic_v029_bridge",
            "status": "closed" if p1_local_ready else "open",
            "evidence": (
                "standalone double-pendulum candidate vendors the required FullVA residual and does not load run_v029.py"
                if p1_local_ready
                else "double-pendulum local rows call load_v029 and then v029.Params/v029.gauss_step dynamically"
            ),
        },
        {
            "id": "P1B3_no_standalone_mechanism_module",
            "status": "closed" if p1_local_ready else "open",
            "evidence": (
                "standalone single-pendulum and double-pendulum candidates are present"
                if p1_local_ready
                else "single-pendulum standalone runner candidate present, but the double-pendulum standalone runner is still missing"
                if single_candidate_ready
                else "current candidate is a report adapter/replay package, not a single/double simulation runner"
            ),
        },
        {
            "id": "P1B4_no_p1_row_regeneration_certificate",
            "status": "closed" if p1_local_ready else "open",
            "evidence": (
                "single-pendulum and double-pendulum candidates regenerated 6/6 local rows"
                if p1_local_ready
                else f"single-pendulum candidate regenerated {regenerated_candidate_rows}/6 local rows; double-pendulum rows remain missing"
                if single_candidate_ready
                else "no compact runner has regenerated the six local single/double rows under h=0.1,0.05,0.025"
            ),
        },
    ]

    audit = {
        "schema": "cmame-p1-local-runner-extraction-audit-v1",
        "status": audit_status,
        "read_only": True,
        "submission_ready": False,
        "self_contained_runner_ready": False,
        "p1_local_single_double_ready": p1_local_ready,
        "p1_single_runner_candidate_ready": single_candidate_ready,
        "p1_double_runner_candidate_ready": double_candidate_ready,
        "p1_regenerated_candidate_rows": regenerated_candidate_rows,
        "p1_required_rows": 6,
        "p1_missing_candidate_rows": max(0, 6 - regenerated_candidate_rows),
        "p1_single_runner_candidate": {
            "schema": single_summary.get("schema"),
            "status": single_summary.get("status"),
            "example": single_summary.get("example"),
            "path": "cmame_p1_single_runner_candidate",
            "script": "cmame_p1_single_runner_candidate/scripts/run_single_pendulum_fullva.py",
            "summary": "cmame_p1_single_runner_candidate/results/single_pendulum_summary.json",
            "csv": "cmame_p1_single_runner_candidate/results/single_pendulum_rows.csv",
            "validator": "validate_cmame_p1_single_runner_candidate.py",
            "script_exists": P1_SINGLE_SCRIPT.exists(),
            "summary_exists": P1_SINGLE_SUMMARY.exists(),
            "csv_exists": P1_SINGLE_CSV.exists(),
            "validator_exists": P1_SINGLE_VALIDATOR.exists(),
            "script_python_lines": optional_line_count(P1_SINGLE_SCRIPT),
            "validator_python_lines": optional_line_count(P1_SINGLE_VALIDATOR),
            "rows": single_summary.get("rows"),
            "h_values": single_summary.get("h_values"),
            "t_final": single_summary.get("t_final"),
            "position_order": single_summary.get("position_order"),
            "velocity_order": single_summary.get("velocity_order"),
            "orientation_order": single_summary.get("orientation_order"),
            "omega_order": single_summary.get("omega_order"),
            "p1_single_only_ready": single_summary.get("p1_single_only_ready"),
            "p1_complete": single_summary.get("p1_complete"),
            "imports_v047_or_v048": single_summary.get("imports_v047_or_v048"),
            "source_policy_external_superiority_allowed": single_summary.get(
                "source_policy_external_superiority_allowed"
            ),
            "proof_gap_closed": single_summary.get("proof_gap_closed"),
        },
        "p1_double_runner_candidate": {
            "schema": double_summary.get("schema"),
            "status": double_summary.get("status"),
            "example": double_summary.get("example"),
            "path": "cmame_p1_double_runner_candidate",
            "script": "cmame_p1_double_runner_candidate/scripts/run_double_pendulum_fullva.py",
            "summary": "cmame_p1_double_runner_candidate/results/double_pendulum_summary.json",
            "csv": "cmame_p1_double_runner_candidate/results/double_pendulum_rows.csv",
            "validator": "validate_cmame_p1_double_runner_candidate.py",
            "script_exists": P1_DOUBLE_SCRIPT.exists(),
            "summary_exists": P1_DOUBLE_SUMMARY.exists(),
            "csv_exists": P1_DOUBLE_CSV.exists(),
            "validator_exists": P1_DOUBLE_VALIDATOR.exists(),
            "script_python_lines": optional_line_count(P1_DOUBLE_SCRIPT),
            "validator_python_lines": optional_line_count(P1_DOUBLE_VALIDATOR),
            "rows": double_summary.get("rows"),
            "h_values": double_summary.get("h_values"),
            "reference_h": double_summary.get("reference_h"),
            "t_final": double_summary.get("t_final"),
            "position_order": double_summary.get("position_order"),
            "velocity_order": double_summary.get("velocity_order"),
            "finest_position_error": double_summary.get("finest_position_error"),
            "finest_velocity_error": double_summary.get("finest_velocity_error"),
            "p1_double_only_ready": double_summary.get("p1_double_only_ready"),
            "p1_complete": double_summary.get("p1_complete"),
            "imports_v047_v048_or_v029": double_summary.get("imports_v047_v048_or_v029"),
            "source_policy_external_superiority_allowed": double_summary.get(
                "source_policy_external_superiority_allowed"
            ),
            "proof_gap_closed": double_summary.get("proof_gap_closed"),
        },
        "reviewer_facing_python_file_limit": REVIEWER_FILE_LIMIT,
        "reviewer_facing_python_line_limit": REVIEWER_LINE_LIMIT,
        "v047_source": label_path(V047_RUN),
        "v047_source_python_lines": line_count(V047_RUN),
        "v048_run_source": label_path(V048_RUN),
        "v048_run_python_lines": line_count(V048_RUN),
        "v048_coarse_source": label_path(V048_COARSE),
        "v048_coarse_python_lines": line_count(V048_COARSE),
        "paper_matrix_rows": matrix.get("row_count"),
        "paper_matrix_raw_rows": matrix.get("raw_row_count"),
        "common_reference_order_wins": matrix.get("direct_nonlocal_velocity_order_wins"),
        "common_reference_error_wins": matrix.get("direct_nonlocal_velocity_error_wins"),
        "source_policy_closed_rows": source_policy_closed,
        "source_policy_total_rows": source_policy_total,
        "p1_target_examples": ["single_pendulum", "double_pendulum"],
        "p1_required_step_sizes": P1_STEP_SIZES,
        "p1_required_reference_h": P1_REFERENCE_H,
        "p1_required_t_end": P1_T_END,
        "v048_wrapper_symbols": wrapper_records,
        "v047_primary_seed_symbols": v047_seed_records,
        "v047_optional_closed_loop_symbols": optional_records,
        "v047_primary_direct_internal_dependencies": primary_direct_deps,
        "v047_primary_direct_internal_dependency_count": len(primary_direct_deps),
        "v047_primary_recursive_internal_dependency_symbols": primary_closure,
        "v047_primary_recursive_internal_dependency_count": len(primary_closure),
        "v047_primary_recursive_internal_dependency_lines": primary_closure_lines,
        "v048_wrapper_v047_attribute_calls": wrapper_v047_attribute_calls,
        "v048_wrapper_run_v047_symbols_called": wrapper_run_v047_calls,
        "dynamic_import_boundaries": [
            {
                "id": "v048_import_v047",
                "status": "open",
                "source": label_path(V048_RUN),
                "symbol": "import_v047_single_fullva_module",
                "target": "v047_cylindrical_chain_pipeline/run_v047.py",
            },
            {
                "id": "v047_load_v029",
                "status": "open",
                "source": label_path(V047_RUN),
                "symbol": "load_v029",
                "target": "V029_PATH dynamic module",
            },
        ],
        "open_blockers": blockers,
        "acceptance_criteria": acceptance,
        "next_extraction_actions": [
            "keep the self-contained single/double P1 runner candidates synchronized with PAPER_NUMERICAL_RESULT_MATRIX",
            "do not promote P1 local rows into source-policy external-superiority claims",
            "continue with P2 external public baselines or P4 proof-boundary closure before submission readiness",
        ],
    }

    OUT_JSON.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# CMAME P1 Local-Runner Extraction Audit",
        "",
        f"Status: **{audit['status']}**.",
        f"P1 local single/double ready: `{audit['p1_local_single_double_ready']}`.",
        f"P1 single-runner candidate ready: `{audit['p1_single_runner_candidate_ready']}`.",
        f"P1 double-runner candidate ready: `{audit['p1_double_runner_candidate_ready']}`.",
        f"P1 regenerated candidate rows: `{audit['p1_regenerated_candidate_rows']}/{audit['p1_required_rows']}`.",
        f"Self-contained runner ready: `{audit['self_contained_runner_ready']}`.",
        f"v047 source size: `{audit['v047_source_python_lines']}` Python lines.",
        f"v048 local runner wrappers: `{len(wrapper_records)}` symbols.",
        f"v047 primary seed closure: `{audit['v047_primary_recursive_internal_dependency_count']}` symbols, `{audit['v047_primary_recursive_internal_dependency_lines']}` symbol lines.",
        f"Source-policy rows closed: `{source_policy_closed}/{source_policy_total}`.",
        "",
        "## Acceptance Boundary",
        "",
        f"- Required examples: `{', '.join(acceptance['requires_regenerated_examples'])}`.",
        f"- Required h values: `{P1_STEP_SIZES}` with reference h `{P1_REFERENCE_H}` and T `{P1_T_END}`.",
        f"- Primary import of run_v047 forbidden: `{acceptance['forbids_primary_import_run_v047']}`.",
        f"- Dynamic load_v029 forbidden: `{acceptance['forbids_dynamic_load_v029']}`.",
        "",
        "## Single-Runner Candidate",
        "",
        "| field | value |",
        "|---|---:|",
        f"| ready | `{single_candidate_ready}` |",
        f"| rows | `{regenerated_candidate_rows}/6` |",
        f"| position order | `{single_summary.get('position_order')}` |",
        f"| velocity order | `{single_summary.get('velocity_order')}` |",
        f"| imports v047/v048 | `{single_summary.get('imports_v047_or_v048')}` |",
        "",
        "## Double-Runner Candidate",
        "",
        "| field | value |",
        "|---|---:|",
        f"| ready | `{double_candidate_ready}` |",
        f"| rows | `{double_summary.get('rows')}/3` |",
        f"| position order | `{double_summary.get('position_order')}` |",
        f"| velocity order | `{double_summary.get('velocity_order')}` |",
        f"| imports v047/v048/v029 | `{double_summary.get('imports_v047_v048_or_v029')}` |",
        "",
        "## v048 Wrapper Symbols",
        "",
        "| source | symbol | role | lines | v047 calls |",
        "|---|---|---|---:|---|",
    ]
    for item in wrapper_records:
        calls = ", ".join(item["direct_external_attribute_calls"]) or "-"
        lines.append(
            f"| `{item['path']}` | `{item['symbol']}` | {item['role']} | "
            f"`{item['symbol_line_count']}` | `{calls}` |"
        )
    lines.extend(["", "## v047 Primary Seeds", "", "| symbol | role | lines | direct internal calls |", "|---|---|---:|---|"])
    for item in v047_seed_records:
        deps = ", ".join(item["direct_internal_calls"]) or "-"
        lines.append(f"| `{item['symbol']}` | {item['role']} | `{item['symbol_line_count']}` | `{deps}` |")
    lines.extend(["", "## Open Blockers", "", "| id | status | evidence |", "|---|---|---|"])
    for item in blockers:
        lines.append(f"| `{item['id']}` | `{item['status']}` | {item['evidence']} |")
    lines.extend(["", "## Next Extraction Actions", ""])
    for action in audit["next_extraction_actions"]:
        lines.append(f"- {action}")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("cmame_p1_local_runner_extraction_audit=written")
    print(f"p1_local_single_double_ready={audit['p1_local_single_double_ready']}")
    print(f"p1_single_runner_candidate_ready={audit['p1_single_runner_candidate_ready']}")
    print(f"p1_double_runner_candidate_ready={audit['p1_double_runner_candidate_ready']}")
    print(f"p1_regenerated_candidate_rows={audit['p1_regenerated_candidate_rows']}/{audit['p1_required_rows']}")
    print(f"v047_source_python_lines={audit['v047_source_python_lines']}")
    print(f"v047_primary_recursive_internal_dependency_count={audit['v047_primary_recursive_internal_dependency_count']}")
    print(f"v047_primary_recursive_internal_dependency_lines={audit['v047_primary_recursive_internal_dependency_lines']}")


if __name__ == "__main__":
    main()
