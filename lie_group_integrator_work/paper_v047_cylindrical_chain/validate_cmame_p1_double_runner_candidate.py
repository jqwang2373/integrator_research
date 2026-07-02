#!/usr/bin/env python3
"""Validate the double-example P1 runner candidate."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


PAPER = Path(__file__).resolve().parent
CANDIDATE = PAPER / "cmame_p1_double_runner_candidate"
SCRIPT = CANDIDATE / "scripts" / "run_double_pendulum_fullva.py"
SUMMARY = CANDIDATE / "results" / "double_pendulum_summary.json"
CSV = CANDIDATE / "results" / "double_pendulum_rows.csv"
README = CANDIDATE / "README.md"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def read_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def main() -> int:
    errors: list[str] = []
    if not SCRIPT.exists():
        errors.append("runner script missing")
    else:
        source = read_text(SCRIPT)
        forbidden = ["import_v047", "run_v047.py", "run_v048.py", "run_v029.py", "../v047", "../v048", "../v029"]
        for token in forbidden:
            if token in source:
                errors.append(f"runner imports or references forbidden source token: {token}")

    proc = subprocess.run(
        [sys.executable, str(SCRIPT)],
        cwd=CANDIDATE,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    if proc.returncode != 0:
        errors.append(f"runner failed:\n{proc.stdout}")
    for token in [
        "p1_double_runner_candidate=PASS",
        "example=double_pendulum",
        "rows=3",
        "p1_double_only_ready=True",
        "p1_complete=False",
        "imports_v047_v048_or_v029=False",
        "source_policy_external_superiority_allowed=False",
        "local_runner_proof_gap_closed=False",
    ]:
        if token not in proc.stdout:
            errors.append(f"runner output missing token: {token}")

    if README.exists():
        readme = read_text(README)
        if "`local_runner_proof_gap_closed=False`" not in readme:
            errors.append("README missing scoped local-runner proof boundary token")
        if "`proof_gap_closed=False`" in readme:
            errors.append("README reintroduced naked local proof_gap_closed marker")
        if "global direct-PC2 Newton--Euler proof boundary" not in readme:
            errors.append("README missing global direct-PC2 proof-boundary separation")
    else:
        errors.append("README missing")

    if not SUMMARY.exists() or not CSV.exists():
        errors.append("runner outputs missing")
    else:
        summary = read_json(SUMMARY)
        if summary.get("schema") != "cmame-p1-double-runner-candidate-v1":
            errors.append("summary schema changed")
        if summary.get("status") != "double_runner_candidate_not_source_policy_or_proof_complete":
            errors.append("summary status changed")
        if summary.get("example") != "double_pendulum":
            errors.append("summary example changed")
        if summary.get("rows") != 3:
            errors.append("summary row count changed")
        if summary.get("h_values") != [0.1, 0.05, 0.025]:
            errors.append("summary h values changed")
        if float(summary.get("reference_h", 0.0)) != 0.0125:
            errors.append("reference h changed")
        if float(summary.get("t_final", 0.0)) != 0.1:
            errors.append("time horizon changed")
        if summary.get("p1_double_only_ready") is not True:
            errors.append("double-only readiness missing")
        if summary.get("p1_complete") is not False:
            errors.append("runner overclaims P1 completion")
        if summary.get("imports_v047_v048_or_v029") is not False:
            errors.append("runner overclaims no-import boundary")
        if summary.get("source_policy_external_superiority_allowed") is not False:
            errors.append("runner overclaims source-policy superiority")
        if summary.get("proof_gap_closed") is not False:
            errors.append("runner overclaims proof closure")
        if float(summary.get("position_order", 0.0)) <= 5.0:
            errors.append("position order below P1 double candidate threshold")
        if float(summary.get("velocity_order", 0.0)) <= 5.0:
            errors.append("velocity order below P1 double candidate threshold")
        if float(summary.get("finest_position_error", 1.0)) > 1.0e-10:
            errors.append("finest position error too large")
        if float(summary.get("finest_velocity_error", 1.0)) > 1.0e-10:
            errors.append("finest velocity error too large")

    if errors:
        print("cmame_p1_double_runner_candidate=FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    summary = read_json(SUMMARY)
    print("cmame_p1_double_runner_candidate=PASS")
    print(f"position_order={float(summary['position_order']):.6f}")
    print(f"velocity_order={float(summary['velocity_order']):.6f}")
    print("p1_double_only_ready=True")
    print("p1_complete=False")
    print("imports_v047_v048_or_v029=False")
    print("source_policy_external_superiority_allowed=False")
    print("local_runner_proof_gap_closed=False")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
