#!/usr/bin/env python3
"""Build a small companion launcher for local accepted-row runners.

The companion does not copy the runner sources into the minimal replay package.
It gives reviewers one compact index/launcher for the existing self-contained
local runner candidates while preserving the full source-policy boundary.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path


PAPER = Path(__file__).resolve().parent
from paper_paths import LATEX, package_path as manuscript_path
COMPANION = PAPER / "cmame_local_accepted_runner_companion"
OUT_JSON = PAPER / "CMAME_LOCAL_ACCEPTED_RUNNER_COMPANION_MANIFEST.json"
OUT_MD = PAPER / "CMAME_LOCAL_ACCEPTED_RUNNER_COMPANION_MANIFEST.md"


LAUNCHER_SCRIPT = r'''#!/usr/bin/env python3
"""Run the local accepted-row companion checks for the CMAME package."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT.parent

RUNS = [
    {
        "id": "minimal_replay_boundary",
        "example": "paper_matrix",
        "cwd": "cmame_minimal_reproducibility_candidate",
        "script": "cmame_minimal_reproducibility_candidate/scripts/replay_paper_matrix.py",
        "pass_token": "cmame_minimal_candidate_replay=PASS",
    },
    {
        "id": "single_pendulum_self_contained",
        "example": "single_pendulum",
        "cwd": "cmame_p1_single_runner_candidate",
        "script": "cmame_p1_single_runner_candidate/scripts/run_single_pendulum_fullva.py",
        "pass_token": "p1_single_runner_candidate=PASS",
    },
    {
        "id": "double_pendulum_self_contained",
        "example": "double_pendulum",
        "cwd": "cmame_p1_double_runner_candidate",
        "script": "cmame_p1_double_runner_candidate/scripts/run_double_pendulum_fullva.py",
        "pass_token": "p1_double_runner_candidate=PASS",
    },
    {
        "id": "four_link_slider_crank_self_contained",
        "example": "four_link,slider_crank",
        "cwd": "cmame_closed_loop_local_runner_candidate",
        "script": "cmame_closed_loop_local_runner_candidate/scripts/run_closed_loop_fullva_candidate.py",
        "pass_token": "cmame_closed_loop_local_runner_candidate=PASS",
    },
]


def read_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def run_item(item: dict[str, str]) -> dict[str, object]:
    script = manuscript_path(item["script"])
    cwd = manuscript_path(item["cwd"])
    proc = subprocess.run(
        [sys.executable, str(script)],
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    output = proc.stdout.strip()
    passed = proc.returncode == 0 and item["pass_token"] in output
    return {
        "id": item["id"],
        "example": item["example"],
        "script": item["script"],
        "returncode": proc.returncode,
        "passed": passed,
        "output_tail": output.splitlines()[-10:],
    }


def main() -> int:
    runs = [run_item(item) for item in RUNS]
    errors = [f"{item['id']} failed" for item in runs if item["passed"] is not True]

    minimal = read_json(PAPER / "CMAME_MINIMAL_REPRODUCIBILITY_CANDIDATE_MANIFEST.json")
    single = read_json(PAPER / "cmame_p1_single_runner_candidate/results/single_pendulum_summary.json")
    double = read_json(PAPER / "cmame_p1_double_runner_candidate/results/double_pendulum_summary.json")
    closed = read_json(PAPER / "cmame_closed_loop_local_runner_candidate/results/closed_loop_local_summary.json")
    b6 = read_json(PAPER / "B6_FOUR_EXAMPLE_LOCAL_EVIDENCE_SUMMARY.json")
    review = read_json(PAPER / "CMAME_REVIEW_AGENT_REPORT.json")
    b4_handoff = read_json(PAPER / "B4_SOURCE_POLICY_EXECUTION_HANDOFF_PACKAGE.json")

    result_checks = review.get("result_checks", {})
    b4_driver = b4_handoff.get("approval_boundary", {}).get("guarded_execution_driver", {})
    handoff = {
        "status": b4_handoff.get("status"),
        "execution_authorized": b4_handoff.get("execution_authorized"),
        "commands_not_run_by_handoff": b4_handoff.get("commands_not_run_by_handoff"),
        "exact_required_user_approval_statement": b4_handoff.get("approval_boundary", {}).get(
            "exact_required_user_approval_statement"
        ),
        "guarded_execution_driver": b4_driver.get("path"),
        "driver_requires_exact_approval": b4_driver.get("requires_exact_approval_argument"),
        "driver_does_not_authorize_execution": b4_driver.get("driver_does_not_authorize_execution"),
        "opt_in_required_command_count": b4_handoff.get("opt_in_required_actions", {}).get(
            "command_count"
        ),
        "opt_in_required_mapped_external_rows": b4_handoff.get("opt_in_required_actions", {}).get(
            "mapped_external_rows"
        ),
        "terminal_unable_to_reproduce_rows": b4_handoff.get("source_policy_row_state", {}).get(
            "unable_to_reproduce"
        ),
    }
    source_closed = result_checks.get("source_policy_apples_to_apples_external_rows")
    source_total = result_checks.get("source_policy_apples_to_apples_external_total_rows")
    examples = ["single_pendulum", "double_pendulum", "four_link", "slider_crank"]
    local_rows = int(single.get("rows", 0)) + int(double.get("rows", 0)) + int(closed.get("row_count", 0))

    if minimal.get("read_only_replay_package") is not True:
        errors.append("minimal replay-only boundary changed")
    if local_rows != 12:
        errors.append(f"local row count changed: {local_rows}")
    if b6.get("human_runnable_four_example_self_contained_simulation_ready") is not True:
        errors.append("B6 four-example self-contained marker missing")
    if source_closed != 0 or source_total != 40:
        errors.append(f"source-policy row boundary changed: {source_closed}/{source_total}")

    if errors:
        print("cmame_local_accepted_runner_companion=FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print("cmame_local_accepted_runner_companion=PASS")
    print("minimal_replay_boundary=preserved")
    print("self_contained_examples=single_pendulum,double_pendulum,four_link,slider_crank")
    print(f"local_rows={local_rows}")
    print(f"source_policy_external_rows={source_closed}/{source_total}")
    print(f"source_policy_handoff_status={handoff.get('status')}")
    print(f"source_policy_handoff_authorized={handoff.get('execution_authorized')}")
    print(f"source_policy_handoff_driver={handoff.get('guarded_execution_driver')}")
    print(
        "source_policy_handoff_opt_in="
        f"{handoff.get('opt_in_required_command_count')}/"
        f"{handoff.get('opt_in_required_mapped_external_rows')}"
    )
    print("full_source_policy_runner_package_ready=False")
    print("submission_ready=False")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
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


def file_item(path: Path, rel: str, role: str) -> dict[str, object]:
    item: dict[str, object] = {
        "path": rel,
        "role": role,
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }
    if path.suffix == ".py":
        item["python_lines"] = python_line_count(path)
    return item


def main() -> None:
    COMPANION.mkdir(parents=True, exist_ok=True)
    script_path = COMPANION / "scripts" / "run_local_accepted_runner_companion.py"
    write_text(script_path, LAUNCHER_SCRIPT)

    proc = subprocess.run(
        [sys.executable, str(script_path)],
        cwd=COMPANION,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stdout)

    minimal = read_json(PAPER / "CMAME_MINIMAL_REPRODUCIBILITY_CANDIDATE_MANIFEST.json")
    b6 = read_json(PAPER / "B6_FOUR_EXAMPLE_LOCAL_EVIDENCE_SUMMARY.json")
    review = read_json(PAPER / "CMAME_REVIEW_AGENT_REPORT.json")
    single = read_json(PAPER / "cmame_p1_single_runner_candidate/results/single_pendulum_summary.json")
    double = read_json(PAPER / "cmame_p1_double_runner_candidate/results/double_pendulum_summary.json")
    closed = read_json(PAPER / "cmame_closed_loop_local_runner_candidate/results/closed_loop_local_summary.json")
    b4_handoff = read_json(PAPER / "B4_SOURCE_POLICY_EXECUTION_HANDOFF_PACKAGE.json")
    result_checks = review.get("result_checks", {})
    b4_driver = b4_handoff.get("approval_boundary", {}).get("guarded_execution_driver", {})
    source_policy_execution_handoff = {
        "status": b4_handoff.get("status"),
        "execution_authorized": b4_handoff.get("execution_authorized"),
        "commands_not_run_by_handoff": b4_handoff.get("commands_not_run_by_handoff"),
        "exact_required_user_approval_statement": b4_handoff.get("approval_boundary", {}).get(
            "exact_required_user_approval_statement"
        ),
        "guarded_execution_driver": b4_driver.get("path"),
        "driver_requires_exact_approval": b4_driver.get("requires_exact_approval_argument"),
        "driver_does_not_authorize_execution": b4_driver.get("driver_does_not_authorize_execution"),
        "opt_in_required_command_count": b4_handoff.get("opt_in_required_actions", {}).get(
            "command_count"
        ),
        "opt_in_required_mapped_external_rows": b4_handoff.get("opt_in_required_actions", {}).get(
            "mapped_external_rows"
        ),
        "terminal_unable_to_reproduce_rows": b4_handoff.get("source_policy_row_state", {}).get(
            "unable_to_reproduce"
        ),
    }

    readme = [
        "# CMAME Local Accepted-Row Runner Companion",
        "",
        "Status: local accepted-row companion ready, source-policy package open.",
        "",
        "This companion is a small reviewer-facing index and launcher for the existing",
        "local self-contained runner candidates. It intentionally does not copy those",
        "runner sources into the minimal replay package, and it does not claim full",
        "source-policy or submission readiness.",
        "",
        "Run:",
        "",
        "```bash",
        "python scripts/run_local_accepted_runner_companion.py",
        "```",
        "",
        "Expected terminal markers:",
        "",
        "- `cmame_local_accepted_runner_companion=PASS`.",
        "- `minimal_replay_boundary=preserved`.",
        "- `self_contained_examples=single_pendulum,double_pendulum,four_link,slider_crank`.",
        "- `local_rows=12`.",
        "- `source_policy_external_rows=0/40`.",
        "- `source_policy_handoff_status=source_policy_execution_handoff_ready_not_authorized_not_run`.",
        "- `source_policy_handoff_authorized=False`.",
        "- `source_policy_handoff_driver=run_b4_source_policy_after_opt_in.sh`.",
        "- `source_policy_handoff_opt_in=13/20`.",
        "- `full_source_policy_runner_package_ready=False`.",
        "- `submission_ready=False`.",
        "",
        "B4 handoff boundary:",
        "",
        "- exact approval statement: `I explicitly approve running the B4 source-policy execution commands listed in B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json.`;",
        "- guarded driver: `run_b4_source_policy_after_opt_in.sh`, requires exact approval, and does not authorize execution by itself.",
    ]
    readme_path = COMPANION / "README.md"
    write_text(readme_path, "\n".join(readme) + "\n")

    files = [
        file_item(readme_path, "README.md", "companion_readme"),
        file_item(script_path, "scripts/run_local_accepted_runner_companion.py", "local_accepted_runner_launcher"),
    ]
    manifest = {
        "schema": "cmame-local-accepted-runner-companion-v1",
        "status": "local_accepted_runner_companion_ready_source_policy_package_open",
        "submission_ready": False,
        "package_dir": "cmame_local_accepted_runner_companion",
        "launcher_passed": True,
        "minimal_replay_boundary_preserved": minimal.get("read_only_replay_package") is True,
        "copies_runner_source": False,
        "uses_existing_self_contained_runner_candidates": True,
        "local_accepted_rows_runner_available": True,
        "full_source_policy_runner_package_ready": False,
        "source_policy_external_superiority_allowed": False,
        "source_policy_execution_handoff": source_policy_execution_handoff,
        "source_policy_execution_allowed_now": b4_handoff.get("source_policy_execution_allowed_now"),
        "source_policy_execution_invoked": b4_handoff.get("source_policy_execution_invoked"),
        "exact_b4_opt_in_required_for_execution": b4_handoff.get(
            "exact_b4_opt_in_required_for_execution"
        ),
        "safe_action_ids": b4_handoff.get("safe_action_ids"),
        "opt_in_action_ids": b4_handoff.get("opt_in_action_ids"),
        "required_user_approval_statement": (
            b4_handoff.get("required_user_approval_statement")
            or b4_handoff.get("exact_approval_statement")
            or b4_handoff.get("opt_in_required_phrase")
        ),
        "guarded_execution_driver": b4_handoff.get("guarded_execution_driver"),
        "source_policy_closed_rows": result_checks.get("source_policy_apples_to_apples_external_rows"),
        "source_policy_total_rows": result_checks.get("source_policy_apples_to_apples_external_total_rows"),
        "local_rows": b6.get("local_rows"),
        "self_contained_examples": b6.get("self_contained_examples"),
        "replay_only_examples": b6.get("replay_only_examples"),
        "runner_commands": [
            "cmame_minimal_reproducibility_candidate/scripts/replay_paper_matrix.py",
            "cmame_p1_single_runner_candidate/scripts/run_single_pendulum_fullva.py",
            "cmame_p1_double_runner_candidate/scripts/run_double_pendulum_fullva.py",
            "cmame_closed_loop_local_runner_candidate/scripts/run_closed_loop_fullva_candidate.py",
        ],
        "runner_summaries": {
            "single_pendulum_rows": single.get("rows"),
            "double_pendulum_rows": double.get("rows"),
            "closed_loop_rows": closed.get("row_count"),
            "single_position_order": single.get("position_order"),
            "double_position_order": double.get("position_order"),
            "closed_loop_models": list(closed.get("model_summaries", {}).keys()),
        },
        "candidate_file_count": len(files),
        "candidate_python_file_count": 1,
        "candidate_python_line_count": python_line_count(script_path),
        "reviewer_facing_python_file_limit": 12,
        "reviewer_facing_python_line_limit": 2000,
        "files": files,
    }
    write_text(COMPANION / "MANIFEST.json", json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    write_text(OUT_JSON, json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    write_text(
        OUT_MD,
        "\n".join(
            [
                "# CMAME Local Accepted-Row Runner Companion Manifest",
                "",
                f"Status: **{manifest['status']}**.",
                f"Launcher passed: `{manifest['launcher_passed']}`.",
                f"Minimal replay boundary preserved: `{manifest['minimal_replay_boundary_preserved']}`.",
                f"Local rows: `{manifest['local_rows']}`.",
                f"Self-contained examples: `{manifest['self_contained_examples']}`.",
                f"Replay-only examples: `{manifest['replay_only_examples']}`.",
                f"Source-policy rows closed: `{manifest['source_policy_closed_rows']}/{manifest['source_policy_total_rows']}`.",
                f"Source-policy execution allowed now/invoked/exact opt-in required: `{manifest['source_policy_execution_allowed_now']}/{manifest['source_policy_execution_invoked']}/{manifest['exact_b4_opt_in_required_for_execution']}`.",
                f"Safe action ids: `{manifest['safe_action_ids']}`; opt-in action ids: `{manifest['opt_in_action_ids']}`.",
                f"Source-policy execution handoff exact approval/driver: `{source_policy_execution_handoff['exact_required_user_approval_statement']}/{source_policy_execution_handoff['guarded_execution_driver']}/{source_policy_execution_handoff['driver_requires_exact_approval']}/{source_policy_execution_handoff['driver_does_not_authorize_execution']}/{source_policy_execution_handoff['opt_in_required_command_count']}/{source_policy_execution_handoff['opt_in_required_mapped_external_rows']}`.",
                f"Full source-policy runner package ready: `{manifest['full_source_policy_runner_package_ready']}`.",
                f"Candidate Python size: `{manifest['candidate_python_file_count']}` file / `{manifest['candidate_python_line_count']}` lines.",
                "",
                "Reading rule: this is a launcher/index for local accepted-row runner candidates, not a source-policy runner archive.",
            ]
        )
        + "\n",
    )

    print("cmame_local_accepted_runner_companion=written")
    print(f"candidate_python_lines={manifest['candidate_python_line_count']}")
    print(f"local_rows={manifest['local_rows']}")
    print(f"source_policy_closed={manifest['source_policy_closed_rows']}/{manifest['source_policy_total_rows']}")
    print(f"source_policy_execution_allowed_now={manifest['source_policy_execution_allowed_now']}")
    print(f"source_policy_execution_invoked={manifest['source_policy_execution_invoked']}")
    print("submission_ready=False")


if __name__ == "__main__":
    main()
