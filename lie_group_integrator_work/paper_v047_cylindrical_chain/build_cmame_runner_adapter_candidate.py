#!/usr/bin/env python3
"""Build a compact runner-adapter candidate for the CMAME package.

The adapter is not a self-contained simulation package. It is a small executable
front-end that checks the shipped 44-row matrix and, when pointed at the local
v048 benchmark tree, can call the existing four-example report-only runner.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path


PAPER = Path(__file__).resolve().parent
ROOT = PAPER.parent
V048 = ROOT / "v048_cross_paper_same_test_benchmarks"
CANDIDATE = PAPER / "cmame_runner_adapter_candidate"
OUT_JSON = PAPER / "CMAME_RUNNER_ADAPTER_CANDIDATE_MANIFEST.json"
OUT_MD = PAPER / "CMAME_RUNNER_ADAPTER_CANDIDATE_MANIFEST.md"

DATA_SOURCES = [
    (PAPER / "PAPER_NUMERICAL_RESULT_MATRIX.csv", "paper_matrix/PAPER_NUMERICAL_RESULT_MATRIX.csv"),
    (PAPER / "PAPER_NUMERICAL_RESULT_MATRIX.json", "paper_matrix/PAPER_NUMERICAL_RESULT_MATRIX.json"),
    (V048 / "results" / "coarse_four_example_order_summary.csv", "v048_report/coarse_four_example_order_summary.csv"),
    (V048 / "results" / "coarse_four_example_order_summary.json", "v048_report/coarse_four_example_order_summary.json"),
    (V048 / "results" / "common_reference_error_summary.csv", "v048_report/common_reference_error_summary.csv"),
    (V048 / "results" / "common_reference_error_summary.json", "v048_report/common_reference_error_summary.json"),
    (
        V048 / "results" / "closed_loop_true_dynamic_strict_common_reference_rows.csv",
        "v048_report/closed_loop_true_dynamic_strict_common_reference_rows.csv",
    ),
    (
        V048 / "results" / "closed_loop_true_dynamic_strict_common_reference.json",
        "v048_report/closed_loop_true_dynamic_strict_common_reference.json",
    ),
    (PAPER / "CMAME_RUNNER_CENTERED_REPRODUCIBILITY_AUDIT.json", "audit/CMAME_RUNNER_CENTERED_REPRODUCIBILITY_AUDIT.json"),
]

ADAPTER_SCRIPT = r'''#!/usr/bin/env python3
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
'''

CLOSED_LOOP_LOCAL_SCRIPT = r'''#!/usr/bin/env python3
"""Replay-check the embedded four-link/slider-crank local closed-loop rows."""

from __future__ import annotations

import csv
import json
import math
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "v048_report"
RESULTS = ROOT / "results"
SUMMARY_JSON = RESULTS / "closed_loop_local_rows_summary.json"
ROWS_CSV = RESULTS / "closed_loop_local_rows.csv"
MODELS = ("four_link", "slider_crank")
STEP_SIZES = (0.1, 0.05, 0.025)


def read_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def as_float(value: object) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return float("nan")
    return number if math.isfinite(number) else float("nan")


def estimate_order(rows: list[dict[str, str]], key: str) -> float:
    pairs = sorted(
        [(as_float(row["h"]), as_float(row[key])) for row in rows],
        reverse=True,
    )
    pairs = [(h, e) for h, e in pairs if h > 0.0 and e > 0.0]
    if len(pairs) != 3:
        return float("nan")
    x = [math.log(h) for h, _ in pairs]
    y = [math.log(e) for _, e in pairs]
    x_mean = sum(x) / len(x)
    y_mean = sum(y) / len(y)
    denom = sum((item - x_mean) ** 2 for item in x)
    if denom == 0.0:
        return float("nan")
    return sum((xi - x_mean) * (yi - y_mean) for xi, yi in zip(x, y, strict=True)) / denom


def write_outputs(rows: list[dict[str, str]], orders: dict[str, tuple[float, float]]) -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    summary = {
        "schema": "cmame-closed-loop-local-rows-replay-v1",
        "status": "closed_loop_local_rows_replay_checked_not_self_contained_runner",
        "models": list(MODELS),
        "h_values": list(STEP_SIZES),
        "local_rows": len(rows),
        "model_orders": {
            model: {
                "position_order": orders[model][0],
                "velocity_order": orders[model][1],
            }
            for model in MODELS
        },
        "self_contained_simulation_runner": False,
        "source_policy_external_superiority_allowed": False,
        "proof_gap_closed_by_adapter": False,
        "submission_ready": False,
    }
    SUMMARY_JSON.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    fieldnames = [
        "model",
        "h",
        "pos_final_linf",
        "vel_final_linf",
        "status",
        "stage_oracle_used",
        "accepted_dynamic_order",
        "external_superiority_claim_allowed",
        "default_1e-4_required",
    ]
    with ROWS_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def main() -> int:
    summary = read_json(DATA / "closed_loop_true_dynamic_strict_common_reference.json")
    rows = read_csv(DATA / "closed_loop_true_dynamic_strict_common_reference_rows.csv")
    local_rows = [
        row
        for row in rows
        if row.get("source_suite") == "local_true_dynamic_newton"
        and row.get("method") == "Gauss6/FullVA-local-true-dynamic-newton"
    ]
    errors: list[str] = []
    if summary.get("schema") != "closed-loop-true-dynamic-strict-common-reference-v1":
        errors.append("closed-loop strict-common-reference schema changed")
    if summary.get("status") != "strict_common_reference_error_columns_available_not_external_superiority":
        errors.append("closed-loop strict-common-reference status changed")
    if summary.get("local_raw_row_count") != 6 or len(local_rows) != 6:
        errors.append("local closed-loop row count is not 6")
    if set(summary.get("strict_common_reference_available_examples", [])) != set(MODELS):
        errors.append("strict common-reference example set changed")
    if summary.get("external_superiority_claim") is not False:
        errors.append("closed-loop summary overclaims external superiority")
    if summary.get("heavy_numerical_run_invoked") is not False:
        errors.append("closed-loop summary unexpectedly marks a heavy numerical run")

    orders: dict[str, tuple[float, float]] = {}
    for model in MODELS:
        model_rows = sorted(
            [row for row in local_rows if row.get("model") == model],
            key=lambda row: as_float(row["h"]),
            reverse=True,
        )
        if [round(as_float(row["h"]), 12) for row in model_rows] != [round(h, 12) for h in STEP_SIZES]:
            errors.append(f"{model} h-grid changed")
            continue
        for row in model_rows:
            if row.get("status") != "ok":
                errors.append(f"{model} local row status changed")
            if row.get("stage_oracle_used") != "false":
                errors.append(f"{model} unexpectedly uses a stage oracle")
            if row.get("accepted_dynamic_order") != "true":
                errors.append(f"{model} local row lost accepted dynamic-order marker")
            if row.get("external_superiority_claim_allowed") != "false":
                errors.append(f"{model} overclaims external superiority")
            if row.get("default_1e-4_required") != "false":
                errors.append(f"{model} unexpectedly requires default 1e-4 policy")
        pos_order = estimate_order(model_rows, "pos_final_linf")
        vel_order = estimate_order(model_rows, "vel_final_linf")
        orders[model] = (pos_order, vel_order)
        if pos_order <= 5.0 or vel_order <= 5.0:
            errors.append(f"{model} local position/velocity order below threshold")

    if errors:
        print("cmame_closed_loop_local_rows_replay=FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    write_outputs(local_rows, orders)
    print("cmame_closed_loop_local_rows_replay=PASS")
    print("models=four_link,slider_crank")
    print("local_rows=6/6")
    print("summary_json=results/closed_loop_local_rows_summary.json")
    print("rows_csv=results/closed_loop_local_rows.csv")
    print(f"four_link_orders={orders['four_link'][0]:.6f}/{orders['four_link'][1]:.6f}")
    print(f"slider_crank_orders={orders['slider_crank'][0]:.6f}/{orders['slider_crank'][1]:.6f}")
    print("self_contained_simulation_runner=False")
    print("source_policy_external_superiority_allowed=False")
    print("proof_gap_closed_by_adapter=False")
    print("submission_ready=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
'''


def read_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def python_line_count(path: Path) -> int:
    return len(path.read_text(encoding="utf-8", errors="replace").splitlines())


def main() -> None:
    CANDIDATE.mkdir(parents=True, exist_ok=True)
    data_items: list[dict[str, object]] = []
    for source, rel_target in DATA_SOURCES:
        target = CANDIDATE / "data" / rel_target
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        data_items.append(
            {
                "path": f"data/{rel_target}",
                "source": str(source.relative_to(PAPER) if source.is_relative_to(PAPER) else source),
                "bytes": target.stat().st_size,
                "sha256": sha256(target),
            }
        )

    script_path = CANDIDATE / "scripts" / "run_four_example_matrix_adapter.py"
    write_text(script_path, ADAPTER_SCRIPT)
    closed_loop_script_path = CANDIDATE / "scripts" / "replay_closed_loop_local_rows.py"
    write_text(closed_loop_script_path, CLOSED_LOOP_LOCAL_SCRIPT)
    closed_loop_proc = subprocess.run(
        [sys.executable, str(closed_loop_script_path)],
        cwd=CANDIDATE,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    if closed_loop_proc.returncode != 0:
        raise RuntimeError(closed_loop_proc.stdout)
    readme = [
        "# CMAME Runner Adapter Candidate",
        "",
        "Status: runner-adapter candidate, not submission ready.",
        "",
        "This package is a compact executable adapter. It checks the embedded 44-row",
        "paper matrix and common-reference result audit. If a local v048 benchmark tree",
        "is provided, it can call `run_coarse_four_example_order.py --report-only`.",
        "",
        "It is not a self-contained simulation runner and does not close source-policy",
        "external rows or the proof gap.",
        "",
        "Human-runnable quickstart:",
        "",
        "```bash",
        "python scripts/run_four_example_matrix_adapter.py",
        "```",
        "",
        "Expected terminal markers:",
        "",
        "- `cmame_runner_adapter_candidate=PASS`.",
        "- `embedded_paper_matrix=44/44`.",
        "- `common_reference_order_error_wins=40/40,40/40`.",
        "- `source_policy_closed=0/40`.",
        "- `runner_adapter_present=True`.",
        "- `self_contained_simulation_runner=False`.",
        "- `submission_ready=False`.",
        "",
        "Closed-loop local four-link/slider-crank row replay:",
        "",
        "```bash",
        "python scripts/replay_closed_loop_local_rows.py",
        "```",
        "",
        "Expected terminal markers:",
        "",
        "- `cmame_closed_loop_local_rows_replay=PASS`.",
        "- `models=four_link,slider_crank`.",
        "- `local_rows=6/6`.",
        "- `summary_json=results/closed_loop_local_rows_summary.json`.",
        "- `rows_csv=results/closed_loop_local_rows.csv`.",
        "- `self_contained_simulation_runner=False`.",
        "- `source_policy_external_superiority_allowed=False`.",
        "- `proof_gap_closed_by_adapter=False`.",
        "",
        "Run embedded checks:",
        "",
        "```bash",
        "python scripts/run_four_example_matrix_adapter.py",
        "```",
        "",
        "Optional local v048 report-only call:",
        "",
        "```bash",
        "python scripts/run_four_example_matrix_adapter.py --external-v048-root ../../v048_cross_paper_same_test_benchmarks",
        "```",
    ]
    write_text(CANDIDATE / "README.md", "\n".join(readme) + "\n")

    matrix = read_json(PAPER / "PAPER_NUMERICAL_RESULT_MATRIX.json")
    audit = read_json(PAPER / "CMAME_RUNNER_CENTERED_REPRODUCIBILITY_AUDIT.json")
    closed_loop_summary_path = CANDIDATE / "results" / "closed_loop_local_rows_summary.json"
    closed_loop_rows_path = CANDIDATE / "results" / "closed_loop_local_rows.csv"
    manifest = {
        "schema": "cmame-runner-adapter-candidate-v1",
        "status": "runner_adapter_candidate_external_v048_required_not_submission_ready",
        "submission_ready": False,
        "package_dir": "cmame_runner_adapter_candidate",
        "runner_adapter_present": True,
        "self_contained_simulation_runner": False,
        "external_v048_required_for_report_generation": True,
        "source_policy_external_superiority_allowed": False,
        "source_policy_closed_rows": audit.get("source_policy_scope", {}).get("source_policy_closed_rows"),
        "source_policy_total_rows": audit.get("source_policy_scope", {}).get("source_policy_total_rows"),
        "proof_gap_closed_by_adapter": False,
        "paper_matrix_rows": matrix.get("row_count"),
        "paper_matrix_raw_rows": matrix.get("raw_row_count"),
        "paper_matrix_methods": matrix.get("method_count"),
        "common_reference_order_wins": matrix.get("direct_nonlocal_velocity_order_wins"),
        "common_reference_order_comparisons": matrix.get("direct_nonlocal_velocity_order_comparisons"),
        "common_reference_error_wins": matrix.get("direct_nonlocal_velocity_error_wins"),
        "common_reference_error_comparisons": matrix.get("direct_nonlocal_velocity_error_comparisons"),
        "closed_loop_local_rows_replay_present": True,
        "closed_loop_local_rows_summary_present": True,
        "closed_loop_local_rows": 6,
        "closed_loop_local_models": ["four_link", "slider_crank"],
        "candidate_file_count": len(data_items) + 5,
        "candidate_python_file_count": 2,
        "candidate_python_line_count": python_line_count(script_path) + python_line_count(closed_loop_script_path),
        "files": [
            {
                "path": "scripts/run_four_example_matrix_adapter.py",
                "source": "generated",
                "bytes": script_path.stat().st_size,
                "sha256": sha256(script_path),
                "python_lines": python_line_count(script_path),
            },
            {
                "path": "scripts/replay_closed_loop_local_rows.py",
                "source": "generated",
                "bytes": closed_loop_script_path.stat().st_size,
                "sha256": sha256(closed_loop_script_path),
                "python_lines": python_line_count(closed_loop_script_path),
            },
            {
                "path": "results/closed_loop_local_rows_summary.json",
                "source": "generated_by_replay_closed_loop_local_rows.py",
                "bytes": closed_loop_summary_path.stat().st_size,
                "sha256": sha256(closed_loop_summary_path),
            },
            {
                "path": "results/closed_loop_local_rows.csv",
                "source": "generated_by_replay_closed_loop_local_rows.py",
                "bytes": closed_loop_rows_path.stat().st_size,
                "sha256": sha256(closed_loop_rows_path),
            },
            *data_items,
            {"path": "README.md", "source": "generated", "bytes": (CANDIDATE / "README.md").stat().st_size, "sha256": sha256(CANDIDATE / "README.md")},
        ],
    }
    write_text(CANDIDATE / "MANIFEST.json", json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    write_text(OUT_JSON, json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    write_text(
        OUT_MD,
        "\n".join(
            [
                "# CMAME Runner Adapter Candidate Manifest",
                "",
                f"Status: **{manifest['status']}**.",
                f"Runner adapter present: `{manifest['runner_adapter_present']}`.",
                f"Self-contained simulation runner: `{manifest['self_contained_simulation_runner']}`.",
                f"Submission ready: `{manifest['submission_ready']}`.",
                f"Candidate Python size: `{manifest['candidate_python_file_count']}` files / `{manifest['candidate_python_line_count']}` lines.",
                f"Paper matrix rows: `{manifest['paper_matrix_rows']}/{manifest['paper_matrix_raw_rows']}`.",
                f"Common-reference order/error wins: `{manifest['common_reference_order_wins']}/{manifest['common_reference_order_comparisons']}` and `{manifest['common_reference_error_wins']}/{manifest['common_reference_error_comparisons']}`.",
                f"Closed-loop local rows replay: `{manifest['closed_loop_local_rows_replay_present']}`; rows/models `{manifest['closed_loop_local_rows']}` / `{','.join(manifest['closed_loop_local_models'])}`.",
                f"Closed-loop replay outputs: summary `{manifest['closed_loop_local_rows_summary_present']}`.",
                f"Source-policy rows closed: `{manifest['source_policy_closed_rows']}/{manifest['source_policy_total_rows']}`.",
            ]
        )
        + "\n",
    )
    print("cmame_runner_adapter_candidate=written")
    print(f"candidate_python_lines={manifest['candidate_python_line_count']}")
    print("runner_adapter_present=True")
    print("self_contained_simulation_runner=False")
    print("submission_ready=False")


if __name__ == "__main__":
    main()
