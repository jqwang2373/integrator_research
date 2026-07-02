#!/usr/bin/env python3
"""Build a static refusal-boundary audit for the guarded B4 driver.

This script intentionally does not invoke the guarded driver. It only parses the
shell script and the opt-in packet to prove that missing or non-exact approval
stays on the refusal branch before any source-policy command can run.
"""

from __future__ import annotations

import json
import shlex
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
DRIVER = PAPER / "run_b4_source_policy_after_opt_in.sh"
PACKET = PAPER / "B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json"
HANDOFF = PAPER / "B4_SOURCE_POLICY_EXECUTION_HANDOFF_PACKAGE.json"
FREEZE = PAPER / "B4_SOURCE_POLICY_COMMAND_PREFLIGHT_FREEZE_20260620.json"
SCHEMA_AUDIT = PAPER / "B4_SOURCE_POLICY_EXPECTED_OUTPUT_SCHEMA_AUDIT_20260620.json"
PROMOTION_BLOCKER = PAPER / "B4_EXPECTED_OUTPUT_PROMOTION_READINESS_BLOCKER_AUDIT_20260620.json"
OUT_JSON = PAPER / "B4_GUARDED_DRIVER_REFUSAL_BOUNDARY_AUDIT_20260621.json"
OUT_MD = PAPER / "B4_GUARDED_DRIVER_REFUSAL_BOUNDARY_AUDIT_20260621.md"
APPROVAL = (
    "I explicitly approve running the B4 source-policy execution commands listed in "
    "B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json."
)
GUARD_LINE = 'if [[ "${1:-}" != "${APPROVAL_REQUIRED}" ]]; then'
FORBIDDEN_BEFORE_GUARD_CLOSE = [
    '"${PY}"',
    "run_v048.py",
    "run_public_closed_loop_shard.py",
    "run_hi2022_full_t8_source_policy_candidate.py",
    'cd "${V048_DIR}"',
    "build_b4_source_policy_post_execution_audit.py",
    "--record-approved-driver-execution",
]


def read_json(path: Path) -> dict[str, Any]:
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


def normalize_driver_commands(commands: list[str]) -> list[str]:
    return [
        " ".join(["../.venv_sbel/bin/python", *shlex.split(command)[1:]])
        for command in commands
    ]


def packet_commands(packet: dict[str, Any]) -> list[str]:
    return [
        command.get("command")
        for batch in packet.get("execution_batches", [])
        if isinstance(batch, dict)
        for command in batch.get("commands", [])
        if isinstance(command, dict)
    ]


def line_index(lines: list[str], token: str) -> int:
    for index, line in enumerate(lines, start=1):
        if token in line:
            return index
    raise ValueError(f"missing required driver token: {token}")


def build() -> dict[str, Any]:
    driver_text = DRIVER.read_text(encoding="utf-8", errors="replace")
    driver_lines = driver_text.splitlines()
    packet = read_json(PACKET)
    handoff = read_json(HANDOFF)
    freeze = read_json(FREEZE)
    schema_audit = read_json(SCHEMA_AUDIT)
    promotion_blocker = read_json(PROMOTION_BLOCKER)

    guard_index = line_index(driver_lines, GUARD_LINE)
    try:
        fi_index = next(
            index
            for index, line in enumerate(driver_lines[guard_index:], start=guard_index + 1)
            if line.strip() == "fi"
        )
    except StopIteration as exc:
        raise ValueError("missing fi closing the exact-approval guard") from exc

    pre_guard_lines = driver_lines[: guard_index - 1]
    refusal_branch_lines = driver_lines[guard_index: fi_index - 1]
    pre_guard_text = "\n".join(pre_guard_lines)
    refusal_branch_text = "\n".join(refusal_branch_lines)
    before_guard_close_text = "\n".join(driver_lines[: fi_index])
    post_guard_text = "\n".join(driver_lines[fi_index:])
    commands = command_lines(driver_text)
    ra_commands = [line for line in commands if "--allow-source-policy-1e-4" in line]
    hi_commands = [line for line in commands if line.endswith("--execute")]
    normalized_driver_commands = normalize_driver_commands(commands)
    listed_packet_commands = packet_commands(packet)

    pre_guard_command_count = pre_guard_text.count('"${PY}"')
    refusal_branch_command_count = refusal_branch_text.count('"${PY}"')
    forbidden_before_guard_close = [
        token for token in FORBIDDEN_BEFORE_GUARD_CLOSE if token in before_guard_close_text
    ]
    refusal_tokens_present = all(
        token in refusal_branch_text
        for token in [
            "Refusing to run B4 source-policy execution commands.",
            "Pass the exact approval statement as the first argument:",
            '"${APPROVAL_REQUIRED}"',
            "exit 2",
        ]
    )
    exact_guard_present = (
        f"APPROVAL_REQUIRED='{APPROVAL}'" in driver_text
        and GUARD_LINE in driver_text
        and refusal_tokens_present
    )
    no_opt_in_refusal_proved = (
        exact_guard_present
        and not forbidden_before_guard_close
        and pre_guard_command_count == 0
        and refusal_branch_command_count == 0
    )
    driver_commands_match_packet = normalized_driver_commands == listed_packet_commands
    source_policy_execution_invoked = any(
        [
            packet.get("execution_invoked_by_packet") is True,
            handoff.get("commands_not_run_by_handoff") is False,
            freeze.get("commands_executed_by_freeze") is True,
            schema_audit.get("commands_executed_by_audit") is True,
        ]
    )
    marker = (
        "b4_guarded_driver_refusal_boundary_audit_20260621="
        f"{no_opt_in_refusal_proved}/{no_opt_in_refusal_proved}/2/"
        f"{pre_guard_command_count}/{len(commands)}/False/False"
    )

    return {
        "schema": "b4-guarded-driver-refusal-boundary-audit-20260621-v1",
        "status": "guarded_driver_refusal_boundary_static_proved_not_executed",
        "date_checked": "2026-06-21",
        "read_only": True,
        "static_only": True,
        "driver_path": DRIVER.name,
        "driver_invoked_by_audit": False,
        "driver_execution_model": "static_text_parse_only_no_subprocess_no_shell_eval",
        "required_user_approval_statement": packet.get("required_user_approval_statement"),
        "guard_condition": GUARD_LINE,
        "guard_line_index": guard_index,
        "fi_line_index": fi_index,
        "no_opt_in_refusal_proved_static": no_opt_in_refusal_proved,
        "wrong_approval_refusal_proved_static": no_opt_in_refusal_proved,
        "refusal_exit_code": 2,
        "refusal_tokens_present": refusal_tokens_present,
        "pre_guard_command_count": pre_guard_command_count,
        "refusal_branch_source_policy_command_count": refusal_branch_command_count,
        "forbidden_tokens_before_guard_close": forbidden_before_guard_close,
        "post_guard_source_policy_command_count": len(commands),
        "ra_allow_source_policy_1e_4_command_count": len(ra_commands),
        "hi_execute_command_count": len(hi_commands),
        "driver_commands_match_packet": driver_commands_match_packet,
        "packet_ready_command_count": packet.get("ready_command_count"),
        "packet_ready_command_mapped_external_rows": packet.get(
            "ready_command_mapped_external_rows"
        ),
        "packet_execution_invoked": packet.get("execution_invoked_by_packet"),
        "packet_explicit_user_opt_in_required": packet.get(
            "explicit_user_opt_in_required_before_any_command"
        ),
        "handoff_status": handoff.get("status"),
        "handoff_commands_not_run": handoff.get("commands_not_run_by_handoff"),
        "freeze_status": freeze.get("status"),
        "freeze_commands_executed": freeze.get("commands_executed_by_freeze"),
        "expected_output_schema_status": schema_audit.get("status"),
        "expected_output_schema_commands_executed": schema_audit.get(
            "commands_executed_by_audit"
        ),
        "expected_output_promotion_blocker_status": promotion_blocker.get("status"),
        "source_policy_execution_invoked": source_policy_execution_invoked,
        "source_policy_execution_allowed_now": False,
        "source_policy_rows_closed_by_audit": 0,
        "b4_can_close_now": False,
        "b7_can_close_now": False,
        "submission_ready": False,
        "not_closing": {
            "source_policy_rows_closed_by_audit": 0,
            "source_policy_execution_invoked": source_policy_execution_invoked,
            "source_policy_execution_allowed_now": False,
            "b4_can_close_now": False,
            "b7_can_close_now": False,
            "submission_ready": False,
        },
        "forbidden_execution_flags": {
            "driver_invoked_by_audit": False,
            "source_policy_execution_invoked": source_policy_execution_invoked,
            "run_v047_invoked": False,
            "heavy_numerical_run_invoked": False,
            "v048_runner_invoked_by_audit": False,
        },
        "marker": marker,
    }


def write_markdown(audit: dict[str, Any]) -> None:
    lines = [
        "# B4 Guarded Driver Refusal Boundary Audit 20260621",
        "",
        f"- Status: `{audit['status']}`.",
        f"- Static only: `{audit['static_only']}`; driver invoked by audit: `{audit['driver_invoked_by_audit']}`.",
        f"- Exact approval phrase: `{audit['required_user_approval_statement']}`.",
        (
            "- Refusal boundary no-opt-in/wrong-approval/exit/pre/post/invoked/submission: "
            f"`{audit['no_opt_in_refusal_proved_static']}/"
            f"{audit['wrong_approval_refusal_proved_static']}/"
            f"{audit['refusal_exit_code']}/"
            f"{audit['pre_guard_command_count']}/"
            f"{audit['post_guard_source_policy_command_count']}/"
            f"{audit['source_policy_execution_invoked']}/"
            f"{audit['submission_ready']}`."
        ),
        f"- Refusal branch source-policy commands: `{audit['refusal_branch_source_policy_command_count']}`.",
        (
            "- Post-guard source-policy commands RA/HI/total: "
            f"`{audit['ra_allow_source_policy_1e_4_command_count']}/"
            f"{audit['hi_execute_command_count']}/"
            f"{audit['post_guard_source_policy_command_count']}`."
        ),
        f"- Driver commands match opt-in packet: `{audit['driver_commands_match_packet']}`.",
        f"- Source-policy rows closed by this audit: `{audit['source_policy_rows_closed_by_audit']}`.",
        f"- B4/B7/submission ready: `{audit['b4_can_close_now']}/{audit['b7_can_close_now']}/{audit['submission_ready']}`.",
        f"- `{audit['marker']}`",
        "",
        "This audit is a static parser over `run_b4_source_policy_after_opt_in.sh`; it does not execute the guarded driver.",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    audit = build()
    OUT_JSON.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(audit)
    print("b4_guarded_driver_refusal_boundary_audit_20260621=written")
    print(f"no_opt_in_refusal_proved_static={audit['no_opt_in_refusal_proved_static']}")
    print(f"wrong_approval_refusal_proved_static={audit['wrong_approval_refusal_proved_static']}")
    print(f"refusal_exit_code={audit['refusal_exit_code']}")
    print(f"pre_guard_command_count={audit['pre_guard_command_count']}")
    print(f"post_guard_source_policy_command_count={audit['post_guard_source_policy_command_count']}")
    print(f"driver_invoked_by_audit={audit['driver_invoked_by_audit']}")
    print(f"source_policy_execution_invoked={audit['source_policy_execution_invoked']}")
    print(f"submission_ready={audit['submission_ready']}")


if __name__ == "__main__":
    main()
