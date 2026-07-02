#!/usr/bin/env python3
"""Validate the guarded B4 source-policy execution driver without running it."""

from __future__ import annotations

import json
import shlex
import sys
from pathlib import Path


PAPER = Path(__file__).resolve().parent
DRIVER = PAPER / "run_b4_source_policy_after_opt_in.sh"
PACKET = PAPER / "B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json"
APPROVAL = (
    "I explicitly approve running the B4 source-policy execution commands listed in "
    "B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json."
)


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


def command_lines(text: str) -> list[str]:
    return [
        line.strip()
        for line in text.splitlines()
        if line.strip().startswith('"${PY}" ')
        and (
            line.strip().endswith("--allow-source-policy-1e-4")
            or line.strip().endswith("--execute")
        )
    ]


def main() -> int:
    checks = Checks()
    try:
        packet = read_json(PACKET)
        text = DRIVER.read_text(encoding="utf-8", errors="replace")
    except Exception as exc:  # noqa: BLE001
        print(f"B4 guarded execution driver validation: FAIL\n- {exc}")
        return 1

    lines = text.splitlines()
    commands = command_lines(text)
    ra_commands = [line for line in commands if "--allow-source-policy-1e-4" in line]
    hi_commands = [line for line in commands if line.endswith("--execute")]
    packet_commands = [
        command.get("command")
        for batch in packet.get("execution_batches", [])
        if isinstance(batch, dict)
        for command in batch.get("commands", [])
        if isinstance(command, dict)
    ]

    checks.check(lines[:2] == ["#!/usr/bin/env bash", "set -euo pipefail"], "driver shell guard changed")
    checks.check(f"APPROVAL_REQUIRED='{APPROVAL}'" in text, "exact approval statement missing")
    checks.check(
        'if [[ "${1:-}" != "${APPROVAL_REQUIRED}" ]]; then' in text,
        "first-argument exact-approval guard missing",
    )
    checks.check("Refusing to run B4 source-policy execution commands." in text, "refusal message missing")
    checks.check("exit 2" in text, "nonzero refusal exit missing")
    checks.check('V048_DIR="${SCRIPT_DIR}/../v048_cross_paper_same_test_benchmarks"' in text, "v048 cwd binding changed")
    checks.check('PY="${SCRIPT_DIR}/../.venv_sbel/bin/python"' in text, "python executable binding changed")
    checks.check('cd "${V048_DIR}"' in text, "driver does not enter v048 directory before execution commands")
    checks.check('cd "${SCRIPT_DIR}"' in text, "driver does not return to paper directory for post-processing")
    checks.check("run_v047.py" not in text, "driver must not call run_v047.py")

    checks.check(len(commands) == 13, "guarded driver command count changed")
    checks.check(len(ra_commands) == 5, "RA2021 guarded command count changed")
    checks.check(len(hi_commands) == 8, "HI2022 guarded command count changed")
    checks.check(all("--allow-source-policy-1e-4" in line for line in ra_commands), "RA commands lost explicit 1e-4 opt-in flag")
    checks.check(all("--allow-source-policy-1e-4" not in line for line in hi_commands), "HI commands unexpectedly use 1e-4 opt-in flag")
    checks.check(all(line.endswith("--execute") for line in hi_commands), "HI commands must stay explicit execute shards")

    normalized_driver_commands = [
        " ".join(["../.venv_sbel/bin/python", *shlex.split(line)[1:]])
        for line in commands
    ]
    checks.check(
        normalized_driver_commands == packet_commands,
        "guarded driver commands diverge from B4 opt-in packet command list",
    )

    for token in [
        'build_b4_source_policy_post_execution_audit.py --record-approved-driver-execution "${APPROVAL_REQUIRED}"',
        "build_b4_source_policy_row_closure_readiness_ledger.py",
        "build_b4_source_policy_execution_opt_in_packet.py",
        "build_cmame_reproducibility_package_manifest.py",
        "cmame_submission_review_agent.py",
        "validate_b4_source_policy_work_precision_execution_plan.py",
        "validate_b4_existing_artifact_promotion_audit.py",
        "validate_b4_source_policy_post_execution_audit.py",
        "validate_b4_source_policy_row_closure_readiness_ledger.py",
        "validate_b4_source_policy_execution_opt_in_packet.py",
        "validate_cmame_reproducibility_package_manifest.py",
        "validate_cmame_review_agent.py",
        "validate_submission_bundle.py",
        "validate_paper_package.py",
    ]:
        checks.check(token in text, f"driver missing post-execution token: {token}")

    if checks.errors:
        print("B4 guarded execution driver validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("B4 guarded execution driver validation: PASS")
    print("exact_approval_guard=True")
    print("driver_command_count=13")
    print("ra_allow_source_policy_1e_4_commands=5")
    print("hi_execute_commands=8")
    print("commands_match_opt_in_packet=True")
    print("run_v047_invoked=False")
    print("execution_invoked_by_validator=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
