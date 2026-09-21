#!/usr/bin/env python3
"""Validate the executable closed-loop local runner candidate manifest."""

from __future__ import annotations

import ast
import csv
import hashlib
import json
import math
import sys
from pathlib import Path


PAPER = Path(__file__).resolve().parent
CANDIDATE = PAPER / "cmame_closed_loop_local_runner_candidate"
MANIFEST = PAPER / "CMAME_CLOSED_LOOP_LOCAL_RUNNER_CANDIDATE_MANIFEST.json"
MANIFEST_MD = PAPER / "CMAME_CLOSED_LOOP_LOCAL_RUNNER_CANDIDATE_MANIFEST.md"
SUMMARY = CANDIDATE / "results" / "closed_loop_local_summary.json"
ROWS = CANDIDATE / "results" / "closed_loop_local_rows.csv"


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


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def python_lines(path: Path) -> int:
    return len(read_text(path).splitlines()) if path.suffix == ".py" else 0


def imported_modules(path: Path) -> list[str]:
    try:
        tree = ast.parse(read_text(path))
    except SyntaxError:
        return []
    modules: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            modules.append(node.module or "")
    return modules


def main() -> int:
    checks = Checks()
    try:
        manifest = read_json(MANIFEST)
        manifest_md = read_text(MANIFEST_MD)
        package_manifest = read_json(CANDIDATE / "MANIFEST.json")
        summary = read_json(SUMMARY)
        rows = read_rows(ROWS)
    except Exception as exc:  # noqa: BLE001
        print(f"CMAME closed-loop local runner candidate validation: FAIL\n- {exc}")
        return 1

    checks.check(manifest.get("schema") == "cmame-closed-loop-local-runner-candidate-v1", "schema changed")
    checks.check(
        manifest.get("status") == "closed_loop_local_runner_candidate_passed_compact",
        "candidate status should be passed-compact",
    )
    checks.check(manifest.get("submission_ready") is False, "candidate must not mark submission ready")
    checks.check(manifest.get("runner_passed") is True, "candidate runner did not pass")
    checks.check(
        manifest.get("self_contained_simulation_runner") is True,
        "candidate did not mark self-contained simulation runner",
    )
    checks.check(manifest.get("candidate_python_file_count") == 10, "candidate Python file count changed")
    checks.check(
        0 < manifest.get("candidate_python_line_count", 0) <= 2000,
        "candidate line count should be within limit",
    )
    checks.check(manifest.get("candidate_python_line_limit") == 2000, "candidate line limit changed")
    checks.check(manifest.get("candidate_python_line_limit_ok") is True, "candidate line limit not satisfied")
    checks.check(manifest.get("imports_v046_v047_v048_or_v029") is False, "forbidden import marker set")
    checks.check(manifest.get("forbidden_imports") == [], "forbidden imports present")
    checks.check(manifest.get("source_policy_external_superiority_allowed") is False, "source-policy overclaimed")
    checks.check(manifest.get("source_policy_external_rows_closed") == 0, "source-policy rows unexpectedly closed")
    checks.check(manifest.get("source_policy_external_rows_total") == 40, "source-policy row total changed")
    checks.check(manifest.get("run_v047_invoked") is False, "candidate invoked run_v047")
    checks.check(manifest.get("run_v048_invoked") is False, "candidate invoked run_v048")
    checks.check(manifest.get("heavy_numerical_run_invoked") is False, "candidate invoked heavy numerical run")
    checks.check(manifest.get("closed_loop_local_rows") == 6, "closed-loop row count changed")
    checks.check(set(manifest.get("closed_loop_models", [])) == {"four_link", "slider_crank"}, "model set changed")
    checks.check(manifest.get("step_sizes") == [0.1, 0.05, 0.025], "step-size grid changed")

    checks.check(
        package_manifest.get("schema") == manifest.get("schema")
        and package_manifest.get("status") == manifest.get("status"),
        "package MANIFEST does not match top-level manifest",
    )
    checks.check(package_manifest.get("runner_passed") is True, "package MANIFEST runner marker stale")

    checks.check(
        summary.get("schema") == "cmame-closed-loop-local-runner-candidate-summary-v1",
        "runner summary schema changed",
    )
    checks.check(
        summary.get("status") == "closed_loop_self_contained_candidate_rows_passed_not_source_policy",
        "runner summary status changed",
    )
    checks.check(summary.get("self_contained_simulation_runner") is True, "runner summary self-contained marker missing")
    checks.check(summary.get("imports_v046_v047_v048") is False, "runner summary import boundary changed")
    checks.check(summary.get("submission_ready") is False, "runner summary overclaimed submission readiness")
    checks.check(summary.get("source_policy_external_superiority_allowed") is False, "runner summary overclaimed policy")
    checks.check(summary.get("row_count") == 6 and summary.get("ok_row_count") == 6, "summary row counts changed")
    checks.check(summary.get("accepted_dynamic_order_count") == 2, "accepted closed-loop model count changed")

    checks.check(len(rows) == 6, "CSV row count changed")
    by_model: dict[str, list[dict[str, str]]] = {"four_link": [], "slider_crank": []}
    for row in rows:
        model = row.get("model", "")
        if model in by_model:
            by_model[model].append(row)
        checks.check(row.get("status") == "ok", f"row status not ok: {model} h={row.get('h')}")
        checks.check(row.get("row_type") == "self_contained_closed_loop_candidate", "row type changed")
        checks.check(row.get("trajectory_stepper_executed") == "true", "trajectory stepper did not execute")
        checks.check(row.get("simulate_runner_implemented") == "true", "simulate runner marker missing")
        checks.check(row.get("source_policy_external_superiority_allowed") == "false", "row policy overclaimed")
        checks.check(row.get("submission_ready") == "false", "row submission readiness overclaimed")
        checks.check(float(row.get("max_stage_residual_inf", "nan")) < 1.0e-8, "stage residual too large")
        checks.check(float(row.get("endpoint_so3_fro", "nan")) < 1.0e-12, "SO(3) projection error too large")
    checks.check(all(len(items) == 3 for items in by_model.values()), "expected three step sizes per closed-loop model")

    for model, item in summary.get("model_summaries", {}).items():
        checks.check(item.get("accepted_dynamic_order_candidate") is True, f"{model} order candidate not accepted")
        min_order = float(item.get("min_primary_order", "nan"))
        checks.check(math.isfinite(min_order) and min_order >= 4.5, f"{model} primary order too small")

    python_files = sorted(CANDIDATE.rglob("*.py"))
    checks.check(len(python_files) == manifest.get("candidate_python_file_count"), "Python file inventory stale")
    checks.check(
        sum(python_lines(path) for path in python_files) == manifest.get("candidate_python_line_count"),
        "Python line inventory stale",
    )
    forbidden = ("run_v047", "run_v048", "v046", "v047", "v048", "v029")
    bad_imports = []
    for path in python_files:
        imports = imported_modules(path)
        bad = [module for module in imports if any(token in module for token in forbidden)]
        if bad:
            bad_imports.append((path.relative_to(CANDIDATE).as_posix(), bad))
    checks.check(not bad_imports, f"forbidden imports found: {bad_imports}")

    for item in manifest.get("files", []):
        rel = item.get("path")
        if not isinstance(rel, str):
            checks.check(False, "manifest file item missing path")
            continue
        path = CANDIDATE / rel
        checks.check(path.exists(), f"candidate file missing: {rel}")
        if path.exists() and item.get("source") != "generated_by_runner":
            checks.check(path.stat().st_size == item.get("bytes"), f"candidate file byte count stale: {rel}")
            checks.check(sha256(path) == item.get("sha256"), f"candidate file hash stale: {rel}")

    for token in [
        "Status: **closed_loop_local_runner_candidate_passed_compact**.",
        "Runner passed: `True`.",
        "Self-contained simulation runner: `True`.",
        "Candidate Python files/lines: `10/",
        "Line limit ok: `True`.",
        "Forbidden imports present: `False`.",
        "Closed-loop local rows: `6`.",
        "Source-policy rows closed: `0/40`.",
        "cmame_closed_loop_local_runner_candidate=PASS",
        "rows_ok=6/6",
    ]:
        checks.check(token in manifest_md, f"markdown missing token: {token}")

    if checks.errors:
        print("CMAME closed-loop local runner candidate validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("CMAME closed-loop local runner candidate validation: PASS")
    print(f"status={manifest.get('status')}")
    print(f"runner_passed={manifest.get('runner_passed')}")
    print(
        "candidate_python="
        f"{manifest.get('candidate_python_file_count')}/{manifest.get('candidate_python_line_count')}"
    )
    print(f"closed_loop_local_rows={manifest.get('closed_loop_local_rows')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
