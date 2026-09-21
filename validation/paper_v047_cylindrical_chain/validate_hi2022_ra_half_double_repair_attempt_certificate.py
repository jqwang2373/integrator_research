#!/usr/bin/env python3
"""Validate the HI2022 rA_half double-pendulum repair-attempt certificate."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
TARGET_GROUP = "rA_half:double_pendulum"


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


def main() -> int:
    checks = Checks()
    try:
        cert = read_json(PAPER / "HI2022_RA_HALF_DOUBLE_REPAIR_ATTEMPT_CERTIFICATE.json")
        text = (PAPER / "HI2022_RA_HALF_DOUBLE_REPAIR_ATTEMPT_CERTIFICATE.md").read_text(
            encoding="utf-8",
            errors="replace",
        )
        diagnosis = read_json(PAPER / "HI2022_RA_HALF_DOUBLE_SOURCE_POLICY_FAILURE_DIAGNOSIS.json")
        repair = read_json(PAPER / "HI2022_T8_TOLERANCE_REPAIR_AUDIT.json")
        ledger = read_json(PAPER / "B4_SOURCE_POLICY_ROW_CLOSURE_READINESS_LEDGER.json")
    except Exception as exc:  # noqa: BLE001
        print(f"HI2022 rA_half double repair-attempt certificate validation: FAIL\n- {exc}")
        return 1

    target_row = next(
        (
            row
            for row in ledger.get("rows", [])
            if isinstance(row, dict)
            and row.get("suite_id") == "hi2022_half_implicit"
            and row.get("method") == "hi2022_rA_half"
            and row.get("example") == "double_pendulum"
        ),
        {},
    )
    initial = cert.get("initial_selected_trio_diagnosis", {})
    evidence = cert.get("tolerance_repair_evidence", {})
    combined_target = evidence.get("combined_target_group", {})
    public_contract = cert.get("full_public_grid_contract", {})
    claim = cert.get("claim_boundary", {})
    ledger_status = cert.get("row_ledger_status", {})
    repair_attempts = evidence.get("repair_attempts", [])
    failed_target_rows = evidence.get("combined_failed_target_rows", [])

    checks.check(
        cert.get("schema") == "hi2022-ra-half-double-repair-attempt-certificate-v1",
        "schema changed",
    )
    checks.check(
        cert.get("status") == "targeted_repair_attempted_not_reproducible_not_promoted",
        "status changed",
    )
    checks.check(cert.get("read_only") is True, "certificate must remain read-only")
    checks.check(
        cert.get("heavy_numerical_run_invoked_by_this_builder") is False,
        "certificate invoked heavy run",
    )
    checks.check(cert.get("run_v047_invoked_by_this_builder") is False, "certificate invoked run_v047")
    checks.check(cert.get("v048_runner_invoked_by_this_builder") is False, "certificate invoked v048")
    checks.check(cert.get("suite_id") == "hi2022_half_implicit", "suite changed")
    checks.check(cert.get("method") == "hi2022_rA_half", "method changed")
    checks.check(cert.get("example") == "double_pendulum", "example changed")
    checks.check(cert.get("target_group") == TARGET_GROUP, "target group changed")
    checks.check(cert.get("source_policy_closed") is False, "certificate overclosed source policy")
    checks.check(cert.get("source_policy_rows_promoted") == 0, "certificate promoted rows")
    checks.check(cert.get("external_superiority_ready") is False, "certificate overclaims superiority")
    checks.check(cert.get("b4_can_close_from_certificate") is False, "certificate closes B4")
    checks.check(cert.get("b7_can_close_from_certificate") is False, "certificate closes B7")

    checks.check(
        ledger_status.get("readiness_status") == target_row.get("readiness_status")
        == "selected_candidate_partial_or_failed_not_promoted",
        "ledger readiness status not carried",
    )
    checks.check(
        ledger_status.get("post_execution_decision") == target_row.get("post_execution_decision") == "not_promoted",
        "ledger post-execution decision changed",
    )
    checks.check(
        ledger_status.get("source_policy_disposition") == target_row.get("source_policy_disposition")
        == "promotion_open",
        "ledger disposition changed",
    )
    checks.check(
        ledger_status.get("counts_as_open_execution_queue") == target_row.get("counts_as_open_execution_queue") is True,
        "target row should remain in open execution/promotion queue",
    )
    checks.check(
        ledger_status.get("primary_promotion_blocker")
        == target_row.get("primary_promotion_blocker")
        == "hi2022_ra_half_double_partial_newton_failure_not_promoted",
        "target blocker changed",
    )

    checks.check(initial.get("status") == diagnosis.get("status"), "diagnosis status stale")
    checks.check(initial.get("row_count") == 3, "initial selected-trio row count changed")
    checks.check(initial.get("ok_row_count") == 1, "initial selected-trio ok rows changed")
    checks.check(initial.get("failed_row_count") == 2, "initial selected-trio failed rows changed")
    checks.check(initial.get("failed_h_values") == [0.02, 0.01], "initial failed h values changed")
    checks.check(initial.get("ok_h_values") == [0.005], "initial ok h values changed")
    checks.check(initial.get("pair_orders_available") is False, "pair orders unexpectedly available")
    checks.check(initial.get("source_policy_rows_promoted") == 0, "diagnosis promoted rows")

    checks.check(evidence.get("repair_audit_status") == repair.get("status"), "repair audit status stale")
    checks.check(evidence.get("original_tolerance_base") == 1e-10, "original tolerance changed")
    checks.check(evidence.get("repair_tolerance_base") == 1e-7, "repair tolerance changed")
    checks.check(evidence.get("additional_repair_tolerance_bases") == [1e-6], "additional repair tolerance changed")
    checks.check(evidence.get("repair_step_sizes") == [0.1, 0.05, 0.025], "repair step sizes changed")
    checks.check(evidence.get("repair_reference_h") == 0.0125, "repair reference h changed")
    checks.check(evidence.get("contains_source_policy_1e_4_rows") is False, "repair unexpectedly contains 1e-4 rows")
    checks.check(evidence.get("repair_v048_runner_invoked_in_original_artifact") is True, "repair provenance changed")
    checks.check(evidence.get("builder_v048_runner_invoked") is False, "validator/build pass invoked v048")

    checks.check(len(repair_attempts) == 2, "repair attempt count changed")
    checks.check([item.get("tolerance_base") for item in repair_attempts] == [1e-7, 1e-6], "repair tolerances changed")
    checks.check(
        all(item.get("target_group_complete") is False for item in repair_attempts),
        "a tolerance repair unexpectedly completed the target group",
    )
    checks.check(
        all(item.get("target_group_ok_rows") == 1 for item in repair_attempts),
        "target repair ok-row count changed",
    )
    checks.check(
        all(item.get("target_group_failed_rows") == 2 for item in repair_attempts),
        "target repair failed-row count changed",
    )
    checks.check(combined_target.get("complete_three_step_group") is False, "combined target unexpectedly complete")
    checks.check(combined_target.get("ok_row_count") == 1, "combined target ok rows changed")
    checks.check(combined_target.get("failed_row_count") == 2, "combined target failed rows changed")
    checks.check(
        combined_target.get("failure_families") == {"newton_not_converging": 2, "ok": 1},
        "combined target failure families changed",
    )
    checks.check(len(failed_target_rows) == 2, "combined failed target-row count changed")
    checks.check({row.get("h") for row in failed_target_rows} == {0.05, 0.1}, "failed target h set changed")
    checks.check(
        all(row.get("failure_family") == "newton_not_converging" for row in failed_target_rows),
        "failed target family changed",
    )

    checks.check(evidence.get("combined_best_ok_rows") == 19, "combined best ok row count changed")
    checks.check(evidence.get("combined_best_row_count") == 24, "combined best total row count changed")
    checks.check(evidence.get("combined_best_complete_groups") == 4, "combined best complete group count changed")
    checks.check(evidence.get("combined_best_group_count") == 8, "combined best group count changed")
    checks.check(len(evidence.get("recovered_rows", [])) == 1, "recovered row count changed")
    checks.check(evidence.get("remaining_incomplete_group_count") == 4, "remaining incomplete group count changed")

    checks.check(public_contract.get("required_rows") == 72, "public-grid row requirement changed")
    checks.check(public_contract.get("required_form_model_groups") == 8, "public-grid group requirement changed")
    checks.check(public_contract.get("reference_h") == 0.001, "public-grid reference h changed")
    checks.check(public_contract.get("tolerance_base") == 1e-10, "public-grid tolerance changed")
    checks.check(len(public_contract.get("step_sizes", [])) == 9, "public step-grid size changed")

    checks.check(claim.get("targeted_repair_completed") is False, "targeted repair overclosed")
    checks.check(claim.get("coarse_trio_diagnostic_repair_completed") is False, "coarse repair overclosed")
    checks.check(claim.get("full_public_grid_matches_repair_policy") is False, "repair/public grid overmatched")
    checks.check(claim.get("full_T8_policy_completed") is False, "full T8 policy overclosed")
    checks.check(claim.get("source_policy_reproduction_closed") is False, "source-policy reproduction overclosed")
    checks.check(claim.get("external_superiority_claim_allowed") is False, "external superiority overclaimed")
    checks.check(claim.get("accepted_source_policy_dynamic_order_examples") == 0, "accepted examples changed")

    decision = cert.get("closure_decision", {})
    checks.check(decision.get("can_close_hi2022_ra_half_double_now") is False, "decision overcloses target row")
    checks.check(
        decision.get("can_promote_to_b4_b7_source_policy_figure") is False,
        "decision overpromotes figure row",
    )
    source_files = cert.get("source_files", [])
    checks.check(
        "HI2022_RA_HALF_DOUBLE_SOURCE_POLICY_FAILURE_DIAGNOSIS.json" in source_files
        and "HI2022_T8_TOLERANCE_REPAIR_AUDIT.json" in source_files
        and "B4_SOURCE_POLICY_ROW_CLOSURE_READINESS_LEDGER.json" in source_files,
        "source files missing",
    )

    for token in [
        "Status: **targeted repair attempted; not reproducible; not promoted**.",
        "Source-policy rows promoted: `0`.",
        "External-superiority ready: `False`.",
        "B4/B7 can close from certificate: `False/False`.",
        "Initial selected-trio ok/failed rows: `1/2`.",
        "Combined repair target ok/failed rows: `1/2`.",
        "Full public-grid rows required: `72`.",
        "Full T=8 policy completed: `False`.",
        "Source-policy reproduction closed: `False`.",
        "`0.05`",
        "`0.1`",
    ]:
        checks.check(token in text, f"markdown missing token: {token}")

    if checks.errors:
        print("HI2022 rA_half double repair-attempt certificate validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("HI2022 rA_half double repair-attempt certificate validation: PASS")
    print("target_group=rA_half:double_pendulum")
    print("combined_target_ok_failed=1/2")
    print("source_policy_rows_promoted=0")
    print("external_superiority_ready=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
