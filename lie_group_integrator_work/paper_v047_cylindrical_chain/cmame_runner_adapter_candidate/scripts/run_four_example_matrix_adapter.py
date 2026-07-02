#!/usr/bin/env python3
"""Check the CMAME four-example matrix and optionally call the v048 report runner."""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


def read_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def check_embedded_data() -> list[str]:
    errors: list[str] = []
    matrix = read_json(DATA / "paper_matrix" / "PAPER_NUMERICAL_RESULT_MATRIX.json")
    paper_rows = read_csv(DATA / "paper_matrix" / "PAPER_NUMERICAL_RESULT_MATRIX.csv")
    v048_summary = read_json(DATA / "v048_report" / "coarse_four_example_order_summary.json")
    common = read_json(DATA / "v048_report" / "common_reference_error_summary.json")
    common_rows = read_csv(DATA / "v048_report" / "common_reference_error_summary.csv")
    closed_loop = read_json(DATA / "v048_report" / "closed_loop_true_dynamic_strict_common_reference.json")
    closed_loop_rows = read_csv(DATA / "v048_report" / "closed_loop_true_dynamic_strict_common_reference_rows.csv")
    audit = read_json(DATA / "audit" / "CMAME_RUNNER_CENTERED_REPRODUCIBILITY_AUDIT.json")

    if matrix.get("row_count") != 44 or len(paper_rows) != 44:
        errors.append("paper matrix is not 44 rows")
    if matrix.get("raw_row_count") != 132:
        errors.append("paper matrix raw-row count changed")
    if matrix.get("method_count") != 11:
        errors.append("paper matrix method count changed")
    if set(matrix.get("examples", [])) != {"single_pendulum", "double_pendulum", "four_link", "slider_crank"}:
        errors.append("paper matrix example set changed")
    if matrix.get("direct_nonlocal_velocity_order_wins") != 40:
        errors.append("paper matrix order wins changed")
    if matrix.get("direct_nonlocal_velocity_error_wins") != 40:
        errors.append("paper matrix error wins changed")
    if matrix.get("source_policy_external_superiority_allowed") is not False:
        errors.append("source-policy external superiority was overclaimed")
    if matrix.get("paper_direct_error_superiority_allowed") is not False:
        errors.append("paper direct-error superiority was overclaimed")

    if v048_summary.get("status") != "required_complete":
        errors.append("v048 coarse summary is not required_complete")
    if v048_summary.get("required_methods_resolved") is not True:
        errors.append("v048 required methods are not resolved")
    if v048_summary.get("raw_row_count") != 148 or v048_summary.get("summary_row_count") != 52:
        errors.append("v048 coarse raw/summary counts changed")

    if common.get("schema") != "common-reference-error-audit-v1":
        errors.append("common-reference summary schema changed")
    if common.get("summary_row_count") != 44 or len(common_rows) != 44:
        errors.append("common-reference summary is not 44 rows")
    if common.get("raw_row_count") != 132:
        errors.append("common-reference raw-row count changed")
    if common.get("local_velocity_order_wins") != 40:
        errors.append("common-reference order wins changed")
    if common.get("local_finest_velocity_error_wins") != 40:
        errors.append("common-reference error wins changed")
    if common.get("source_policy_reproduction") is not False:
        errors.append("common-reference summary overclaims source-policy reproduction")

    local_closed_loop_rows = [
        row for row in closed_loop_rows if row.get("source_suite") == "local_true_dynamic_newton"
    ]
    if closed_loop.get("schema") != "closed-loop-true-dynamic-strict-common-reference-v1":
        errors.append("closed-loop strict-common-reference schema changed")
    if closed_loop.get("local_raw_row_count") != 6 or len(local_closed_loop_rows) != 6:
        errors.append("closed-loop local row count changed")
    if set(closed_loop.get("strict_common_reference_available_examples", [])) != {"four_link", "slider_crank"}:
        errors.append("closed-loop strict-common-reference example set changed")
    if closed_loop.get("external_superiority_claim") is not False:
        errors.append("closed-loop summary overclaims external superiority")

    if audit.get("runner_centered_package_ready") is not False:
        errors.append("runner-centered audit unexpectedly ready")
    if audit.get("current_candidate", {}).get("replay_only") is not True:
        errors.append("runner-centered audit no longer marks the compact candidate replay-only")
    return errors


def run_external_report_only(v048_root: Path) -> tuple[int, str]:
    script = v048_root / "run_coarse_four_example_order.py"
    if not script.exists():
        return 2, f"missing v048 runner: {script}"
    proc = subprocess.run(
        [sys.executable, str(script), "--report-only"],
        cwd=v048_root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    return proc.returncode, proc.stdout


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--external-v048-root", type=Path, default=None)
    args = parser.parse_args()

    errors = check_embedded_data()
    if args.external_v048_root is not None:
        code, output = run_external_report_only(args.external_v048_root)
        print(output.strip())
        if code != 0:
            errors.append(f"external v048 report-only runner failed with code {code}")

    if errors:
        print("cmame_runner_adapter_candidate=FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print("cmame_runner_adapter_candidate=PASS")
    print("embedded_paper_matrix=44/44")
    print("common_reference_order_error_wins=40/40,40/40")
    print("source_policy_closed=0/40")
    print("runner_adapter_present=True")
    print("self_contained_simulation_runner=False")
    print("submission_ready=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
