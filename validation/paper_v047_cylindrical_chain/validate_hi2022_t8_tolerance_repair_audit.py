#!/usr/bin/env python3
"""Validate the HI2022 T=8 tolerance-repair audit."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
AUDIT_JSON = PAPER / "HI2022_T8_TOLERANCE_REPAIR_AUDIT.json"
AUDIT_MD = PAPER / "HI2022_T8_TOLERANCE_REPAIR_AUDIT.md"


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


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def main() -> int:
    checks = Checks()
    try:
        audit = read_json(AUDIT_JSON)
        audit_md = read_text(AUDIT_MD)
    except Exception as exc:  # noqa: BLE001
        print(f"HI2022 T8 tolerance-repair audit validation: FAIL\n- {exc}")
        return 1

    original = audit.get("original_t8_coarse", {})
    repair = audit.get("repair_attempt", {})
    repair_attempts = audit.get("repair_attempts", [])
    latest_repair = audit.get("latest_repair_attempt", {})
    best = audit.get("combined_best", {})
    policy = audit.get("repair_policy", {})
    boundary = audit.get("claim_boundary", {})
    public_contract = audit.get("full_public_grid_contract", {})
    repair_contract = audit.get("current_repair_vs_public_contract", {})
    post_b4 = audit.get("post_b4_decision", {})
    target_contract = audit.get("targeted_repair_acceptance_contract", {})

    checks.check(audit.get("schema") == "hi2022-t8-tolerance-repair-audit-v1", "schema changed")
    checks.check(
        audit.get("status") == "tolerance_repair_attempt_recorded_not_source_policy_closure",
        "status changed",
    )
    checks.check(audit.get("submission_ready") is False, "audit overclaims submission")
    checks.check(audit.get("suite_id") == "hi2022_half_implicit", "suite id changed")
    checks.check(original.get("row_count") == 24, "original row count changed")
    checks.check(original.get("ok_row_count") == 18, "original ok count changed")
    checks.check(original.get("complete_form_model_groups") == 4, "original complete group count changed")
    checks.check(repair.get("row_count") == 12, "repair row count changed")
    checks.check(repair.get("ok_row_count") == 7, "repair ok count changed")
    checks.check(repair.get("complete_form_model_groups") == 0, "repair complete group count changed")
    checks.check(len(repair_attempts) == 2, "repair attempt count changed")
    if len(repair_attempts) == 2:
        checks.check(repair_attempts[0].get("tolerance_base") == 1.0e-7, "first repair tolerance changed")
        checks.check(repair_attempts[1].get("tolerance_base") == 1.0e-6, "second repair tolerance changed")
    checks.check(latest_repair.get("row_count") == 18, "second repair row count changed")
    checks.check(latest_repair.get("ok_row_count") == 13, "second repair ok count changed")
    checks.check(latest_repair.get("complete_form_model_groups") == 2, "second repair complete groups changed")
    checks.check(best.get("row_count") == 24, "combined row count changed")
    checks.check(best.get("ok_row_count") == 19, "combined ok count changed")
    checks.check(best.get("complete_form_model_groups") == 4, "combined complete group count changed")
    checks.check(best.get("recovered_row_count") == 1, "recovered row count changed")
    checks.check(len(best.get("row_details", [])) == 24, "combined row details missing")
    remaining_groups = best.get("remaining_incomplete_groups", [])
    checks.check(len(remaining_groups) == 4, "remaining incomplete group count changed")
    expected_remaining = {
        "rA:slider_crank": 1,
        "rA_half:double_pendulum": 2,
        "rA_half:four_link": 1,
        "rA_half:slider_crank": 1,
    }
    remaining_by_group = {group.get("group"): group for group in remaining_groups}
    checks.check(set(remaining_by_group) == set(expected_remaining), "remaining incomplete group names changed")
    for group_name, failed_count in expected_remaining.items():
        group = remaining_by_group.get(group_name, {})
        checks.check(group.get("failed_row_count") == failed_count, f"{group_name} failed count changed")
        checks.check(len(group.get("failed_rows", [])) == failed_count, f"{group_name} failed row details changed")
    recovered = best.get("recovered_rows", [])
    checks.check(len(recovered) == 1, "recovered rows length changed")
    if recovered:
        row = recovered[0]
        checks.check(row.get("form") == "rA_half", "recovered form changed")
        checks.check(row.get("model") == "double_pendulum", "recovered model changed")
        checks.check(abs(float(row.get("h")) - 0.025) < 1e-15, "recovered h changed")
    checks.check(policy.get("repair_tolerance_base") == 1.0e-7, "repair tolerance changed")
    checks.check(policy.get("additional_repair_tolerance_bases") == [1.0e-6], "additional tolerance changed")
    checks.check(policy.get("original_tolerance_base") == 1.0e-10, "original tolerance marker changed")
    checks.check(policy.get("contains_source_policy_1e_4_rows") is False, "repair unexpectedly contains 1e-4 rows")
    checks.check(policy.get("default_1e_4_required") is False, "repair requires default 1e-4")
    checks.check(policy.get("run_v047_invoked") is False, "repair invoked run_v047")
    checks.check(policy.get("v048_runner_invoked_for_repair") is True, "repair runner provenance missing")
    checks.check(boundary.get("source_policy_reproduction_closed") is False, "source policy unexpectedly closed")
    checks.check(boundary.get("full_T8_policy_completed") is False, "full T8 policy unexpectedly closed")
    checks.check(boundary.get("external_superiority_claim_allowed") is False, "external superiority overclaimed")
    checks.check(boundary.get("accepted_source_policy_dynamic_order_examples") == 0, "dynamic-order count changed")
    checks.check(public_contract.get("required_rows") == 72, "public-grid required row count changed")
    checks.check(public_contract.get("required_form_model_groups") == 8, "public-grid group count changed")
    checks.check(public_contract.get("step_sizes") == [1e-4, 2e-4, 4e-4, 1e-3, 2e-3, 4e-3, 1e-2, 2e-2, 4e-2], "public step sizes changed")
    checks.check(public_contract.get("reference_h") == 1.0e-3, "public reference h changed")
    checks.check(public_contract.get("tolerance_base") == 1.0e-10, "public tolerance base changed")
    checks.check(repair_contract.get("current_repair_required_rows") == 24, "repair contract row count changed")
    checks.check(repair_contract.get("matches_public_step_grid") is False, "repair unexpectedly matches public grid")
    checks.check(repair_contract.get("matches_public_reference_h") is False, "repair unexpectedly matches public reference")
    checks.check(repair_contract.get("diagnostic_only") is True, "repair diagnostic boundary missing")
    checks.check(post_b4.get("decision") == "demote_from_b4_b7_source_policy_figures", "post-B4 decision changed")
    checks.check(post_b4.get("demote_from_b4_b7_source_policy_figures") is True, "post-B4 demotion missing")
    checks.check(post_b4.get("rows_promoted") == 0, "post-B4 promoted rows changed")
    checks.check(post_b4.get("targeted_repair_required_before_promotion") is True, "targeted repair marker missing")
    checks.check(post_b4.get("do_not_rerun_guarded_driver_blindly") is True, "blind-rerun guard missing")
    checks.check(len(target_contract.get("coarse_trio_diagnostic_repair_requires", [])) == 3, "coarse repair contract changed")
    checks.check(len(target_contract.get("full_public_grid_promotion_requires", [])) == 3, "full promotion contract changed")

    for token in [
        "Status: **tolerance repair recorded; source-policy closure still open**.",
        "Original T=8 coarse rows ok: `18/24`.",
        "Repair rows ok: `7/12`.",
        "Second repair rows ok: `13/18`.",
        "Additional repair tolerance base: `1e-06`.",
        "Combined best rows ok: `19/24`.",
        "Combined best complete form/model groups: `4/8`.",
        "Recovered rows: `1`.",
        "Remaining incomplete groups: `4`.",
        "`rA_half:double_pendulum`",
        "`rA_half:four_link`",
        "`rA:slider_crank`",
        "`rA_half:slider_crank`",
        "Full public-grid required rows: `72`.",
        "Public step sizes: `0.0001, 0.0002, 0.0004, 0.001, 0.002, 0.004, 0.01, 0.02, 0.04`.",
        "Current repair step sizes: `0.1, 0.05, 0.025`.",
        "Post-B4 decision: `demote_from_b4_b7_source_policy_figures`.",
        "Targeted repair required before promotion: `True`.",
        "Do not rerun guarded driver blindly: `True`.",
        "Full promotion requires all `72` public-grid rows",
        "Source-policy reproduction closed: `False`.",
        "External superiority claim allowed: `False`.",
        "validate_hi2022_t8_tolerance_repair_audit.py",
    ]:
        checks.check(token in audit_md, f"markdown missing token: {token}")

    if checks.errors:
        print("HI2022 T8 tolerance-repair audit validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("HI2022 T8 tolerance-repair audit validation: PASS")
    print("combined_best_rows=19/24")
    print("combined_best_complete_groups=4/8")
    print("source_policy_reproduction_closed=False")
    print("external_superiority_claim_allowed=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
