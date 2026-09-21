#!/usr/bin/env python3
"""Build the B6 closed-loop self-contained extraction audit."""

from __future__ import annotations

import ast
import json
from pathlib import Path


PAPER = Path(__file__).resolve().parent
from paper_paths import LATEX, package_path as manuscript_path
ROOT = PAPER.parent
V048 = ROOT.parent / "numerics" / "v048_cross_paper_same_test_benchmarks"
OUT_JSON = PAPER / "B6_CLOSED_LOOP_SELF_CONTAINED_EXTRACTION_AUDIT.json"
OUT_MD = PAPER / "B6_CLOSED_LOOP_SELF_CONTAINED_EXTRACTION_AUDIT.md"

CLOSED_LOOP_MODELS = ["four_link", "slider_crank"]
STEP_SIZES = [0.1, 0.05, 0.025]
REVIEWER_LINE_LIMIT = 2000

TARGET_SOURCES = {
    "../../numerics/v048_cross_paper_same_test_benchmarks/build_closed_loop_true_dynamic_newton_coarse_order.py": [
        ("import_v047_module", "external v047 loader to remove"),
        ("write_csv", "row output helper"),
        ("setup_exact_system", "exact/reference system setup to replace with local model setup"),
        ("finite", "order-fit finite-value guard"),
        ("observed_order", "three-step-size observed order fit"),
        ("simulate_model_h", "closed-loop model/h trajectory row generator"),
        ("build_model_summary", "per-model order and acceptance summary"),
        ("annotate_rows_with_orders", "row annotation with model-level orders"),
        ("write_markdown", "human-readable local row report"),
        ("main", "current non-self-contained orchestration"),
    ],
    "../../numerics/v048_cross_paper_same_test_benchmarks/closed_loop_fullva_dynamic_residual.py": [
        ("ClosedLoopStageContext", "stage chart/context state"),
        ("exp_so3", "SO(3) exponential map"),
        ("log_so3", "SO(3) logarithm map"),
        ("right_jacobian_inverse_so3", "SO(3) right-Jacobian inverse"),
        ("skew3", "skew matrix helper"),
        ("capture_stage_context", "start-of-step chart capture"),
        ("_snapshot_system_state", "residual side-effect guard"),
        ("_restore_system_state", "residual side-effect restoration"),
        ("generalized_qva_from_system", "pack q/v/a from multibody state"),
        ("pack_closed_loop_fullva_stage_vector", "stage vector packer"),
        ("unpack_closed_loop_fullva_stage_vector", "stage vector unpacker"),
        ("set_system_stage_state", "apply stage q/v/a to multibody state"),
        ("closed_loop_fullva_stage_residual_blocks", "constraint and Newton-Euler residual blocks"),
        ("closed_loop_fullva_stage_residual", "flat stage residual"),
        ("_body_vectors", "endpoint vector extraction helper"),
        ("_set_body_vectors", "endpoint vector assignment helper"),
        ("endpoint_state_from_system", "endpoint state extraction"),
        ("endpoint_state_error_inf", "endpoint infinity-norm errors"),
        ("finite_difference_jacobian", "dense finite-difference Newton Jacobian"),
        ("newton_solve_closed_loop_fullva_stage", "damped Newton stage solve"),
        ("start_extrapolated_closed_loop_stage_vector", "non-oracle stage predictor"),
        ("_apply_gauss6_endpoint_update", "Gauss6 endpoint update"),
        ("gauss6_closed_loop_fullva_dynamic_step_newton_smoke", "non-oracle closed-loop dynamic step"),
    ],
}

REQUIRED_EXTERNAL_SYMBOLS_TO_REPLACE = {
    "run_v047.py": [
        "load_v046",
        "project_v046_system_to_so3",
        "solve_v046_local_kinematic_fullva_time",
        "reconstruct_v046_reaction_dynamics",
        "v046_constraint_level_residuals",
    ],
    "v046 module returned by load_v046": [
        "MODELS",
        "setup_system",
        "patch_modern_numpy_scalar_assignments",
        "orthogonality_error",
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
    return (manuscript_path(path_label)).resolve() if path_label.startswith("../") else manuscript_path(path_label)


def line_count(path: Path) -> int:
    return len(read_text(path).splitlines())


def top_level_inventory(path: Path) -> tuple[dict[str, tuple[int, int]], list[str]]:
    tree = ast.parse(read_text(path))
    spans: dict[str, tuple[int, int]] = {}
    imports: list[str] = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            spans[node.name] = (node.lineno, int(getattr(node, "end_lineno", node.lineno)))
        elif isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            module = "." * node.level + (node.module or "")
            imports.append(module)
    return spans, sorted(set(imports))


def source_item(path_label: str, symbols: list[tuple[str, str]]) -> tuple[dict[str, object], list[dict[str, object]]]:
    path = resolve(path_label)
    spans, imports = top_level_inventory(path)
    source = {
        "path": path_label,
        "exists": path.exists(),
        "python_lines": line_count(path),
        "imports": imports,
        "top_level_symbol_count": len(spans),
    }
    rows: list[dict[str, object]] = []
    for symbol, role in symbols:
        start, end = spans.get(symbol, (0, 0))
        rows.append(
            {
                "path": path_label,
                "symbol": symbol,
                "role": role,
                "exists": symbol in spans,
                "start_line": start,
                "end_line": end,
                "symbol_line_count": end - start + 1 if start and end else 0,
                "port_action": "copy_or_reimplement_without_v047_v048_imports",
            }
        )
    return source, rows


def v048_python_inventory() -> dict[str, int]:
    files = sorted(V048.glob("*.py"))
    return {
        "python_file_count": len(files),
        "python_line_count": sum(line_count(path) for path in files),
    }


def main() -> None:
    runner_adapter = read_json(PAPER / "CMAME_RUNNER_ADAPTER_CANDIDATE_MANIFEST.json")
    b6_local_evidence = read_json(PAPER / "B6_FOUR_EXAMPLE_LOCAL_EVIDENCE_SUMMARY.json")
    review = read_json(PAPER / "CMAME_REVIEW_AGENT_REPORT.json")
    closed_loop_candidate_path = PAPER / "CMAME_CLOSED_LOOP_LOCAL_RUNNER_CANDIDATE_MANIFEST.json"
    closed_loop_candidate = read_json(closed_loop_candidate_path) if closed_loop_candidate_path.exists() else {}
    coarse = read_json(V048 / "results" / "closed_loop_true_dynamic_newton_coarse_order.json")
    strict_common = read_json(V048 / "results" / "closed_loop_true_dynamic_strict_common_reference.json")

    source_files: list[dict[str, object]] = []
    target_symbols: list[dict[str, object]] = []
    for path_label, symbols in TARGET_SOURCES.items():
        source, rows = source_item(path_label, symbols)
        source_files.append(source)
        target_symbols.extend(rows)

    target_symbol_lines = sum(int(item["symbol_line_count"]) for item in target_symbols)
    source_file_lines = sum(int(item["python_lines"]) for item in source_files)
    result_checks = review.get("result_checks", {})
    replay_only = list(b6_local_evidence.get("replay_only_examples", []))
    self_contained = list(b6_local_evidence.get("self_contained_examples", []))
    candidate_ready = (
        closed_loop_candidate.get("runner_passed") is True
        and closed_loop_candidate.get("self_contained_simulation_runner") is True
        and closed_loop_candidate.get("candidate_python_line_limit_ok") is True
        and closed_loop_candidate.get("imports_v046_v047_v048_or_v029") is False
        and closed_loop_candidate.get("closed_loop_local_rows") == 6
        and closed_loop_candidate.get("source_policy_external_superiority_allowed") is False
        and closed_loop_candidate.get("submission_ready") is False
    )

    audit = {
        "schema": "b6-closed-loop-self-contained-extraction-audit-v1",
        "status": (
            "closed_loop_self_contained_runner_candidate_ready_source_policy_open"
            if candidate_ready
            else "closed_loop_self_contained_extraction_target_mapped_runner_open"
        ),
        "generated_from": [
            "CMAME_RUNNER_ADAPTER_CANDIDATE_MANIFEST.json",
            "B6_FOUR_EXAMPLE_LOCAL_EVIDENCE_SUMMARY.json",
            "CMAME_REVIEW_AGENT_REPORT.json",
            "CMAME_CLOSED_LOOP_LOCAL_RUNNER_CANDIDATE_MANIFEST.json",
            "../../numerics/v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_newton_coarse_order.json",
            "../../numerics/v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_strict_common_reference.json",
        ],
        "submission_ready": False,
        "self_contained_runner_ready": candidate_ready,
        "b4_opt_in_required_for_this_audit": False,
        "source_policy_external_superiority_allowed": False,
        "source_policy_external_rows_closed": result_checks.get("source_policy_apples_to_apples_external_rows"),
        "source_policy_external_rows_total": result_checks.get("source_policy_apples_to_apples_external_total_rows"),
        "run_v047_invoked": False,
        "run_v048_invoked": False,
        "heavy_numerical_run_invoked": False,
        "closed_loop_models": CLOSED_LOOP_MODELS,
        "step_sizes": STEP_SIZES,
        "replay_only_closed_loop_examples": replay_only,
        "self_contained_examples_after_closed_loop_candidate": self_contained,
        "closed_loop_local_replay_rows": runner_adapter.get("closed_loop_local_rows"),
        "closed_loop_local_replay_present": runner_adapter.get("closed_loop_local_rows_replay_present"),
        "closed_loop_local_rows_summary_present": runner_adapter.get("closed_loop_local_rows_summary_present"),
        "coarse_order_status": coarse.get("status"),
        "coarse_order_accepted_dynamic_order_count": coarse.get("accepted_dynamic_order_count"),
        "coarse_order_simulate_runner_implemented": coarse.get("simulate_runner_implemented"),
        "strict_common_reference_status": strict_common.get("status"),
        "strict_common_reference_available_examples": strict_common.get("strict_common_reference_available_examples"),
        "closed_loop_local_runner_candidate": {
            "schema": closed_loop_candidate.get("schema"),
            "status": closed_loop_candidate.get("status", "missing"),
            "runner_passed": closed_loop_candidate.get("runner_passed", False),
            "self_contained_simulation_runner": closed_loop_candidate.get("self_contained_simulation_runner", False),
            "candidate_python_file_count": closed_loop_candidate.get("candidate_python_file_count"),
            "candidate_python_line_count": closed_loop_candidate.get("candidate_python_line_count"),
            "candidate_python_line_limit": closed_loop_candidate.get("candidate_python_line_limit", REVIEWER_LINE_LIMIT),
            "candidate_python_line_limit_ok": closed_loop_candidate.get("candidate_python_line_limit_ok", False),
            "imports_v046_v047_v048_or_v029": closed_loop_candidate.get("imports_v046_v047_v048_or_v029", True),
            "closed_loop_local_rows": closed_loop_candidate.get("closed_loop_local_rows", 0),
            "closed_loop_models": closed_loop_candidate.get("closed_loop_models", []),
            "step_sizes": closed_loop_candidate.get("step_sizes", []),
            "run_v047_invoked": closed_loop_candidate.get("run_v047_invoked", False),
            "run_v048_invoked": closed_loop_candidate.get("run_v048_invoked", False),
            "source_policy_external_superiority_allowed": closed_loop_candidate.get(
                "source_policy_external_superiority_allowed", False
            ),
            "source_policy_external_rows_closed": closed_loop_candidate.get("source_policy_external_rows_closed", 0),
            "source_policy_external_rows_total": closed_loop_candidate.get("source_policy_external_rows_total", 40),
        },
        "target_source_files": source_files,
        "target_source_file_count": len(source_files),
        "target_source_file_lines": source_file_lines,
        "target_symbol_count": len(target_symbols),
        "target_symbol_lines": target_symbol_lines,
        "target_symbols": target_symbols,
        "v048_total_python_inventory": v048_python_inventory(),
        "external_symbols_to_replace": REQUIRED_EXTERNAL_SYMBOLS_TO_REPLACE,
        "extraction_blockers": [
            {
                "id": "CL1_v047_loader_dependency",
                "status": "bypassed_by_compact_candidate" if candidate_ready else "open",
                "evidence": (
                    "compact candidate uses local rA-only public SBEL subset and does not import run_v047/v046"
                    if candidate_ready
                    else "current coarse-order builder imports run_v047.py and then loads v046"
                ),
            },
            {
                "id": "CL2_closed_loop_model_definitions",
                "status": "satisfied_by_compact_candidate" if candidate_ready else "open",
                "evidence": (
                    "compact candidate includes local four_link/slider_crank setup modules and public model JSON"
                    if candidate_ready
                    else "four_link and slider_crank setup_system/model definitions still live behind the v046 loader"
                ),
            },
            {
                "id": "CL3_primary_submission_runner",
                "status": (
                    "satisfied_compact_candidate_passed"
                    if candidate_ready
                    else "partial_non_compact_candidate_passed"
                    if closed_loop_candidate.get("runner_passed") is True
                    else "open"
                ),
                "evidence": (
                    "candidate regenerates six closed-loop rows without v046/v047/v048 imports "
                    "and satisfies the compact package line limit"
                    if candidate_ready
                    else "candidate regenerates six closed-loop rows without v046/v047/v048 imports, "
                    f"but package line-limit ok={closed_loop_candidate.get('candidate_python_line_limit_ok')}"
                    if closed_loop_candidate.get("runner_passed") is True
                    else "current reviewer-facing adapter replays six closed-loop rows instead of regenerating them"
                ),
            },
            {
                "id": "CL4_candidate_size_limit",
                "status": (
                    "satisfied" if closed_loop_candidate.get("candidate_python_line_limit_ok") is True else "open"
                ),
                "evidence": (
                    f"{closed_loop_candidate.get('candidate_python_file_count')}/"
                    f"{closed_loop_candidate.get('candidate_python_line_count')} Python files/lines; "
                    f"limit={REVIEWER_LINE_LIMIT}"
                ),
            },
        ],
        "acceptance_criteria": {
            "candidate_package": "cmame_closed_loop_local_runner_candidate",
            "max_python_lines": REVIEWER_LINE_LIMIT,
            "must_not_import": ["run_v047.py", "run_v048.py", "v029", "v046"],
            "regenerates_closed_loop_local_rows": 6,
            "models": CLOSED_LOOP_MODELS,
            "step_sizes": STEP_SIZES,
            "min_primary_order_threshold": 4.5,
            "source_policy_external_superiority_allowed": False,
        },
        "next_concrete_step": (
            "keep compact closed-loop candidate evidence synchronized while B4/B7 source-policy gates remain open; "
            "run the final B6 prose pass only after B4/B7 wording stabilizes"
            if candidate_ready
            else "reduce cmame_closed_loop_local_runner_candidate below the reviewer-facing line limit or split it into "
            "a compact runner API plus provenance archive"
            if closed_loop_candidate.get("runner_passed") is True
            else "port only the listed closed-loop symbols plus local four_link/slider_crank model setup into "
            "cmame_closed_loop_local_runner_candidate, replacing the six replay-only rows with self-contained execution"
        ),
    }

    OUT_JSON.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# B6 Closed-Loop Self-Contained Extraction Audit",
        "",
        f"Status: **{audit['status']}**.",
        f"Self-contained closed-loop runner ready: `{audit['self_contained_runner_ready']}`.",
        f"B4 opt-in required for this audit: `{audit['b4_opt_in_required_for_this_audit']}`.",
        f"Run v047/v048 invoked: `{audit['run_v047_invoked']}/{audit['run_v048_invoked']}`.",
        f"Closed-loop replay-only examples: `{audit['replay_only_closed_loop_examples']}`.",
        f"Closed-loop local replay rows: `{audit['closed_loop_local_replay_rows']}`.",
        f"Target closed-loop source files/lines: `{audit['target_source_file_count']}/{audit['target_source_file_lines']}`.",
        f"Target symbols/lines: `{audit['target_symbol_count']}/{audit['target_symbol_lines']}`.",
        f"Source-policy rows closed: `{audit['source_policy_external_rows_closed']}/{audit['source_policy_external_rows_total']}`.",
        f"Closed-loop candidate status: `{audit['closed_loop_local_runner_candidate']['status']}`.",
        f"Closed-loop candidate rows: `{audit['closed_loop_local_runner_candidate']['closed_loop_local_rows']}`.",
        f"Closed-loop candidate Python files/lines: `{audit['closed_loop_local_runner_candidate']['candidate_python_file_count']}/{audit['closed_loop_local_runner_candidate']['candidate_python_line_count']}`.",
        f"Closed-loop candidate line limit ok: `{audit['closed_loop_local_runner_candidate']['candidate_python_line_limit_ok']}`.",
        f"Closed-loop candidate package: `{audit['acceptance_criteria']['candidate_package']}`.",
        "",
        "## Target Sources",
        "",
        "| source | lines | imports |",
        "|---|---:|---|",
    ]
    for item in source_files:
        lines.append(f"| `{item['path']}` | `{item['python_lines']}` | `{', '.join(item['imports'])}` |")
    lines.extend(["", "## Target Symbols", "", "| source | symbol | role | lines |", "|---|---|---|---:|"])
    for item in target_symbols:
        lines.append(
            f"| `{item['path']}` | `{item['symbol']}` | {item['role']} | `{item['symbol_line_count']}` |"
        )
    lines.extend(["", "## Blockers", "", "| id | status | evidence |", "|---|---|---|"])
    for item in audit["extraction_blockers"]:
        lines.append(f"| `{item['id']}` | `{item['status']}` | {item['evidence']} |")
    lines.extend(
        [
            "",
            "## Next Step",
            "",
            audit["next_concrete_step"],
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("b6_closed_loop_self_contained_extraction_audit=written")
    print(f"self_contained_runner_ready={audit['self_contained_runner_ready']}")
    print(f"target_symbol_count={audit['target_symbol_count']}")
    print(f"target_symbol_lines={audit['target_symbol_lines']}")
    print(f"source_policy_closed={audit['source_policy_external_rows_closed']}/{audit['source_policy_external_rows_total']}")


if __name__ == "__main__":
    main()
