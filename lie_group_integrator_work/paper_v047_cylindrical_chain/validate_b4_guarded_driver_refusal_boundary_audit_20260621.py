#!/usr/bin/env python3
"""Validate the static B4 guarded-driver refusal-boundary audit."""

from __future__ import annotations

import json
import shlex
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
DRIVER = PAPER / "run_b4_source_policy_after_opt_in.sh"
PACKET = PAPER / "B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json"
AUDIT = PAPER / "B4_GUARDED_DRIVER_REFUSAL_BOUNDARY_AUDIT_20260621.json"
AUDIT_MD = PAPER / "B4_GUARDED_DRIVER_REFUSAL_BOUNDARY_AUDIT_20260621.md"
APPROVAL = (
    "I explicitly approve running the B4 source-policy execution commands listed in "
    "B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json."
)
MARKER = "b4_guarded_driver_refusal_boundary_audit_20260621=True/True/2/0/13/False/False"


class Checks:
    def __init__(self) -> None:
        self.errors: list[str] = []

    def check(self, condition: bool, message: str) -> None:
        if not condition:
            self.errors.append(message)


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


def normalized_driver_commands(commands: list[str]) -> list[str]:
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


def main() -> int:
    checks = Checks()
    try:
        audit = read_json(AUDIT)
        packet = read_json(PACKET)
        driver_text = DRIVER.read_text(encoding="utf-8", errors="replace")
        markdown = AUDIT_MD.read_text(encoding="utf-8", errors="replace")
    except Exception as exc:  # noqa: BLE001
        print(f"B4 guarded driver refusal boundary audit validation: FAIL\n- {exc}")
        return 1

    commands = command_lines(driver_text)
    ra_commands = [line for line in commands if "--allow-source-policy-1e-4" in line]
    hi_commands = [line for line in commands if line.endswith("--execute")]

    checks.check(
        audit.get("schema") == "b4-guarded-driver-refusal-boundary-audit-20260621-v1",
        "schema changed",
    )
    checks.check(
        audit.get("status") == "guarded_driver_refusal_boundary_static_proved_not_executed",
        "status changed",
    )
    checks.check(audit.get("date_checked") == "2026-06-21", "date changed")
    checks.check(audit.get("read_only") is True, "audit must be read-only")
    checks.check(audit.get("static_only") is True, "audit must stay static-only")
    checks.check(audit.get("driver_invoked_by_audit") is False, "audit invoked driver")
    checks.check(audit.get("required_user_approval_statement") == APPROVAL, "approval phrase changed")
    checks.check(audit.get("no_opt_in_refusal_proved_static") is True, "no-opt-in refusal not proved")
    checks.check(audit.get("wrong_approval_refusal_proved_static") is True, "wrong-approval refusal not proved")
    checks.check(audit.get("refusal_exit_code") == 2, "refusal exit code changed")
    checks.check(audit.get("refusal_tokens_present") is True, "refusal tokens missing")
    checks.check(audit.get("pre_guard_command_count") == 0, "pre-guard command count changed")
    checks.check(
        audit.get("refusal_branch_source_policy_command_count") == 0,
        "refusal branch can execute source-policy commands",
    )
    checks.check(audit.get("forbidden_tokens_before_guard_close") == [], "forbidden tokens appear before guard closes")
    checks.check(audit.get("post_guard_source_policy_command_count") == 13, "post-guard command count changed")
    checks.check(audit.get("ra_allow_source_policy_1e_4_command_count") == 5, "RA command count changed")
    checks.check(audit.get("hi_execute_command_count") == 8, "HI command count changed")
    checks.check(audit.get("driver_commands_match_packet") is True, "driver/packet command mismatch")
    checks.check(audit.get("packet_ready_command_count") == packet.get("ready_command_count") == 13, "packet command count changed")
    checks.check(
        audit.get("packet_ready_command_mapped_external_rows")
        == packet.get("ready_command_mapped_external_rows")
        == 20,
        "packet mapped rows changed",
    )
    checks.check(audit.get("packet_execution_invoked") is False, "packet unexpectedly invoked execution")
    checks.check(
        audit.get("packet_explicit_user_opt_in_required") is True,
        "packet opt-in requirement changed",
    )
    checks.check(audit.get("source_policy_execution_invoked") is False, "source-policy execution was invoked")
    checks.check(audit.get("source_policy_execution_allowed_now") is False, "execution should not be allowed now")
    checks.check(audit.get("source_policy_rows_closed_by_audit") == 0, "audit overclosed source-policy rows")
    checks.check(audit.get("b4_can_close_now") is False, "audit must not close B4")
    checks.check(audit.get("b7_can_close_now") is False, "audit must not close B7")
    checks.check(audit.get("submission_ready") is False, "audit must not mark submission ready")
    checks.check(audit.get("marker") == MARKER, "marker changed")
    checks.check(normalized_driver_commands(commands) == packet_commands(packet), "driver commands no longer match packet")
    checks.check(len(commands) == 13 and len(ra_commands) == 5 and len(hi_commands) == 8, "driver command mix changed")
    checks.check(f"APPROVAL_REQUIRED='{APPROVAL}'" in driver_text, "driver approval constant changed")
    checks.check('if [[ "${1:-}" != "${APPROVAL_REQUIRED}" ]]; then' in driver_text, "driver guard changed")
    checks.check("exit 2" in driver_text, "driver refusal exit missing")

    forbidden = audit.get("forbidden_execution_flags", {})
    checks.check(
        forbidden == {
            "driver_invoked_by_audit": False,
            "source_policy_execution_invoked": False,
            "run_v047_invoked": False,
            "heavy_numerical_run_invoked": False,
            "v048_runner_invoked_by_audit": False,
        },
        "forbidden execution flags changed",
    )

    for token in [
        "Status: `guarded_driver_refusal_boundary_static_proved_not_executed`.",
        "Static only: `True`; driver invoked by audit: `False`.",
        f"Exact approval phrase: `{APPROVAL}`.",
        "Refusal boundary no-opt-in/wrong-approval/exit/pre/post/invoked/submission: `True/True/2/0/13/False/False`.",
        "Post-guard source-policy commands RA/HI/total: `5/8/13`.",
        "Driver commands match opt-in packet: `True`.",
        "Source-policy rows closed by this audit: `0`.",
        "B4/B7/submission ready: `False/False/False`.",
        f"`{MARKER}`",
    ]:
        checks.check(token in markdown, f"markdown missing token: {token}")

    if checks.errors:
        print("B4 guarded driver refusal boundary audit validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("B4 guarded driver refusal boundary audit validation: PASS")
    print(MARKER)
    print("no_opt_in_refusal_proved_static=True")
    print("wrong_approval_refusal_proved_static=True")
    print("refusal_exit_code=2")
    print("pre_guard_command_count=0")
    print("post_guard_source_policy_command_count=13")
    print("driver_invoked_by_audit=False")
    print("source_policy_execution_invoked=False")
    print("submission_ready=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
