#!/usr/bin/env python3
"""Validate the compact CMAME runner-adapter candidate."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
from pathlib import Path


PAPER = Path(__file__).resolve().parent
CANDIDATE = PAPER / "cmame_runner_adapter_candidate"
MANIFEST_JSON = PAPER / "CMAME_RUNNER_ADAPTER_CANDIDATE_MANIFEST.json"
MANIFEST_MD = PAPER / "CMAME_RUNNER_ADAPTER_CANDIDATE_MANIFEST.md"


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


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    checks = Checks()
    try:
        manifest = read_json(MANIFEST_JSON)
        package_manifest = read_json(CANDIDATE / "MANIFEST.json")
        manifest_md = read_text(MANIFEST_MD)
        readme = read_text(CANDIDATE / "README.md")
        matrix = read_json(CANDIDATE / "data" / "paper_matrix" / "PAPER_NUMERICAL_RESULT_MATRIX.json")
        common = read_json(CANDIDATE / "data" / "v048_report" / "common_reference_error_summary.json")
        closed_loop = read_json(CANDIDATE / "data" / "v048_report" / "closed_loop_true_dynamic_strict_common_reference.json")
        closed_loop_replay_summary = read_json(CANDIDATE / "results" / "closed_loop_local_rows_summary.json")
        closed_loop_replay_rows = read_csv(CANDIDATE / "results" / "closed_loop_local_rows.csv")
        audit = read_json(CANDIDATE / "data" / "audit" / "CMAME_RUNNER_CENTERED_REPRODUCIBILITY_AUDIT.json")
    except Exception as exc:  # noqa: BLE001
        print(f"cmame runner-adapter candidate validation: FAIL\n- {exc}")
        return 1

    checks.check(manifest == package_manifest, "top-level and package manifests differ")
    checks.check(manifest.get("schema") == "cmame-runner-adapter-candidate-v1", "schema changed")
    checks.check(
        manifest.get("status") == "runner_adapter_candidate_external_v048_required_not_submission_ready",
        "status changed",
    )
    checks.check(manifest.get("submission_ready") is False, "candidate must not mark submission ready")
    checks.check(manifest.get("runner_adapter_present") is True, "runner adapter marker missing")
    checks.check(manifest.get("self_contained_simulation_runner") is False, "candidate overclaims self-contained simulation runner")
    checks.check(
        manifest.get("external_v048_required_for_report_generation") is True,
        "external v048 requirement marker missing",
    )
    checks.check(manifest.get("source_policy_external_superiority_allowed") is False, "source-policy superiority overclaimed")
    checks.check(manifest.get("source_policy_closed_rows") == 0, "source-policy closed rows changed")
    checks.check(manifest.get("source_policy_total_rows") == 40, "source-policy total rows changed")
    checks.check(manifest.get("proof_gap_closed_by_adapter") is False, "adapter proof closure overclaimed")
    checks.check(manifest.get("paper_matrix_rows") == matrix.get("row_count") == 44, "paper matrix row count changed")
    checks.check(manifest.get("paper_matrix_raw_rows") == matrix.get("raw_row_count") == 132, "paper matrix raw count changed")
    checks.check(manifest.get("paper_matrix_methods") == matrix.get("method_count") == 11, "paper matrix method count changed")
    checks.check(
        manifest.get("common_reference_order_wins") == manifest.get("common_reference_order_comparisons") == 40,
        "common-reference order wins changed",
    )
    checks.check(
        manifest.get("common_reference_error_wins") == manifest.get("common_reference_error_comparisons") == 40,
        "common-reference error wins changed",
    )
    checks.check(common.get("summary_row_count") == 44 and common.get("raw_row_count") == 132, "common-reference counts changed")
    checks.check(common.get("source_policy_reproduction") is False, "common-reference source-policy boundary changed")
    checks.check(audit.get("runner_centered_package_ready") is False, "runner-centered audit unexpectedly ready")
    checks.check(manifest.get("closed_loop_local_rows_replay_present") is True, "closed-loop replay marker missing")
    checks.check(
        manifest.get("closed_loop_local_rows_summary_present") is True,
        "closed-loop replay summary marker missing",
    )
    checks.check(manifest.get("closed_loop_local_rows") == 6, "closed-loop local row count changed")
    checks.check(
        set(manifest.get("closed_loop_local_models", [])) == {"four_link", "slider_crank"},
        "closed-loop local model set changed",
    )
    checks.check(
        closed_loop.get("schema") == "closed-loop-true-dynamic-strict-common-reference-v1",
        "closed-loop strict-common-reference schema changed",
    )
    checks.check(closed_loop.get("local_raw_row_count") == 6, "closed-loop strict local row count changed")
    checks.check(closed_loop.get("external_superiority_claim") is False, "closed-loop summary overclaims superiority")
    checks.check(
        closed_loop_replay_summary.get("schema") == "cmame-closed-loop-local-rows-replay-v1",
        "closed-loop replay summary schema changed",
    )
    checks.check(
        closed_loop_replay_summary.get("status")
        == "closed_loop_local_rows_replay_checked_not_self_contained_runner",
        "closed-loop replay summary status changed",
    )
    checks.check(closed_loop_replay_summary.get("local_rows") == 6, "closed-loop replay summary row count changed")
    checks.check(len(closed_loop_replay_rows) == 6, "closed-loop replay CSV row count changed")
    checks.check(
        set(closed_loop_replay_summary.get("models", [])) == {"four_link", "slider_crank"},
        "closed-loop replay summary model set changed",
    )
    checks.check(
        closed_loop_replay_summary.get("self_contained_simulation_runner") is False,
        "closed-loop replay overclaims self-contained simulation runner",
    )
    checks.check(
        closed_loop_replay_summary.get("source_policy_external_superiority_allowed") is False,
        "closed-loop replay overclaims source-policy superiority",
    )
    checks.check(
        closed_loop_replay_summary.get("proof_gap_closed_by_adapter") is False,
        "closed-loop replay overclaims adapter proof closure",
    )
    checks.check(closed_loop_replay_summary.get("submission_ready") is False, "closed-loop replay overclaims submission readiness")
    checks.check(manifest.get("candidate_file_count") == len(manifest.get("files", [])), "candidate file count stale")
    checks.check(manifest.get("candidate_python_file_count") == 2, "candidate Python file count changed")
    checks.check(2 <= int(manifest.get("candidate_python_line_count", 0)) <= 420, "adapter scripts too large")

    for item in manifest.get("files", []):
        rel = item.get("path")
        path = CANDIDATE / str(rel)
        checks.check(path.exists() and path.stat().st_size > 0, f"candidate file missing: {rel}")
        if path.exists():
            checks.check(path.stat().st_size == item.get("bytes"), f"candidate file size stale: {rel}")
            checks.check(sha256(path) == item.get("sha256"), f"candidate file hash stale: {rel}")

    replay = subprocess.run(
        [sys.executable, "scripts/run_four_example_matrix_adapter.py"],
        cwd=CANDIDATE,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    checks.check(replay.returncode == 0, f"adapter embedded check failed:\n{replay.stdout}")
    checks.check("cmame_runner_adapter_candidate=PASS" in replay.stdout, "adapter PASS marker missing")
    checks.check("self_contained_simulation_runner=False" in replay.stdout, "adapter boundary marker missing")
    closed_loop_replay = subprocess.run(
        [sys.executable, "scripts/replay_closed_loop_local_rows.py"],
        cwd=CANDIDATE,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    checks.check(
        closed_loop_replay.returncode == 0,
        f"closed-loop local row replay failed:\n{closed_loop_replay.stdout}",
    )
    for token in [
        "cmame_closed_loop_local_rows_replay=PASS",
        "models=four_link,slider_crank",
        "local_rows=6/6",
        "summary_json=results/closed_loop_local_rows_summary.json",
        "rows_csv=results/closed_loop_local_rows.csv",
        "self_contained_simulation_runner=False",
        "source_policy_external_superiority_allowed=False",
        "proof_gap_closed_by_adapter=False",
    ]:
        checks.check(token in closed_loop_replay.stdout, f"closed-loop replay missing token: {token}")

    for token in [
        "Status: **runner_adapter_candidate_external_v048_required_not_submission_ready**.",
        "Runner adapter present: `True`.",
        "Self-contained simulation runner: `False`.",
        "Submission ready: `False`.",
        "Candidate Python size: `2` files /",
        "Paper matrix rows: `44/132`.",
        "Common-reference order/error wins: `40/40` and `40/40`.",
        "Closed-loop local rows replay: `True`; rows/models `6` / `four_link,slider_crank`.",
        "Closed-loop replay outputs: summary `True`.",
        "Source-policy rows closed: `0/40`.",
    ]:
        checks.check(token in manifest_md, f"manifest markdown missing token: {token}")
    for token in [
        "runner-adapter candidate, not submission ready",
        "not a self-contained simulation runner",
        "does not close source-policy",
        "Closed-loop local four-link/slider-crank row replay",
        "summary_json=results/closed_loop_local_rows_summary.json",
    ]:
        checks.check(token in readme, f"README missing token: {token}")

    if checks.errors:
        print("cmame runner-adapter candidate validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("cmame runner-adapter candidate validation: PASS")
    print(f"candidate_python_lines={manifest.get('candidate_python_line_count')}")
    print("runner_adapter_present=True")
    print("self_contained_simulation_runner=False")
    print(f"source_policy_closed={manifest.get('source_policy_closed_rows')}/{manifest.get('source_policy_total_rows')}")
    print("submission_ready=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
