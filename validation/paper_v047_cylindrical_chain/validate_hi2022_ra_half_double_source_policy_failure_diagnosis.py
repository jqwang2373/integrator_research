#!/usr/bin/env python3
"""Validate the HI2022 rA_half double-pendulum failure diagnosis."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
V048_RESULTS = PAPER.parent.parent / "numerics" / "v048_cross_paper_same_test_benchmarks" / "results"
STEM = "hi2022_full_t8_source_policy_candidate_rA_half_double_pendulum"


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
        audit = read_json(PAPER / "HI2022_RA_HALF_DOUBLE_SOURCE_POLICY_FAILURE_DIAGNOSIS.json")
        audit_md = read_text(PAPER / "HI2022_RA_HALF_DOUBLE_SOURCE_POLICY_FAILURE_DIAGNOSIS.md")
        summary = read_json(V048_RESULTS / f"{STEM}_summary.json")
    except Exception as exc:  # noqa: BLE001
        print(f"HI2022 rA_half double source-policy failure diagnosis validation: FAIL\n- {exc}")
        return 1

    contract = audit.get("candidate_contract", {})
    evidence = audit.get("execution_evidence", {})
    diagnosis = audit.get("diagnosis", {})
    tolerance_context = audit.get("tolerance_repair_context", {})
    promotion = audit.get("promotion_decision", {})
    rows = audit.get("rows", [])

    checks.check(
        audit.get("schema") == "hi2022-ra-half-double-source-policy-failure-diagnosis-v1",
        "schema changed",
    )
    checks.check(
        audit.get("status") == "diagnosis_only_partial_newton_failure_not_promoted",
        "status changed",
    )
    checks.check(audit.get("read_only") is True, "audit should be read-only")
    checks.check(audit.get("heavy_numerical_run_invoked_by_this_builder") is False, "builder invoked heavy run")
    checks.check(audit.get("run_v047_invoked_by_this_builder") is False, "builder invoked run_v047")
    checks.check(audit.get("v048_runner_invoked_by_this_builder") is False, "builder invoked v048 runner")

    checks.check(contract.get("summary_status") == summary.get("status"), "summary status stale")
    checks.check(
        contract.get("summary_status") == "partial_or_failed_full_T8_source_policy_candidate_not_promoted",
        "candidate is not the expected partial shard",
    )
    checks.check(contract.get("execution_phase") == "candidate", "execution phase changed")
    checks.check(contract.get("execute_requested") is True, "source candidate was not executed")
    checks.check(
        contract.get("heavy_numerical_run_invoked_by_source_candidate") is True,
        "source candidate execution marker missing",
    )
    checks.check(contract.get("form") == "rA_half", "form changed")
    checks.check(contract.get("model") == "double_pendulum", "model changed")
    checks.check(contract.get("selected_t_end") == 8.0, "selected T changed")
    checks.check(contract.get("selected_reference_h") == 0.001, "reference h changed")
    checks.check(contract.get("selected_step_sizes") == [0.02, 0.01, 0.005], "step sizes changed")
    checks.check(contract.get("source_policy_time_window_selected") is True, "T=8 marker missing")
    checks.check(contract.get("source_policy_reference_h_selected") is True, "reference marker missing")
    checks.check(contract.get("selected_coarse_trio") is True, "coarse-trio marker missing")
    checks.check(contract.get("full_public_grid_selected") is False, "full public grid overclaimed")
    checks.check(contract.get("source_policy_1e_4_included") is False, "1e-4 unexpectedly included")
    checks.check(contract.get("reference_status") == "ok", "reference status changed")
    checks.check(contract.get("estimated_reference_steps") == 8000, "reference step estimate changed")
    checks.check(contract.get("estimated_candidate_steps") == [400, 800, 1600], "candidate step estimates changed")
    checks.check(
        contract.get("canonical_hi2022_output_untouched_by_writer") is True,
        "canonical-output protection marker missing",
    )

    checks.check(evidence.get("row_count") == len(rows) == 3, "row count changed")
    checks.check(evidence.get("ok_row_count") == 1, "ok-row count changed")
    checks.check(evidence.get("failed_row_count") == 2, "failed-row count changed")
    checks.check(evidence.get("rows_complete") is False, "rows unexpectedly complete")
    checks.check(evidence.get("candidate_partial") is True, "partial marker missing")
    checks.check(evidence.get("selected_step_trio_completed") is False, "selected trio overclaimed")
    checks.check(evidence.get("source_policy_candidate_rows_completed") == 1, "candidate completion count changed")
    checks.check(evidence.get("position_pair_orders") == [], "position pair orders unexpectedly available")
    checks.check(evidence.get("velocity_pair_orders") == [], "velocity pair orders unexpectedly available")
    checks.check(evidence.get("acceleration_pair_orders") == [], "acceleration pair orders unexpectedly available")
    checks.check(evidence.get("selected_tolerance_values") == [1e-10], "selected tolerance values changed")
    checks.check(evidence.get("reference_tolerance_values") == [0.0001], "reference tolerance values changed")

    checks.check(diagnosis.get("partial_or_failed_shard") is True, "partial/failure diagnosis marker missing")
    checks.check(diagnosis.get("newton_failure_count") == 2, "Newton failure count changed")
    checks.check(diagnosis.get("failed_h_values") == [0.02, 0.01], "failed h values changed")
    checks.check(diagnosis.get("ok_h_values") == [0.005], "ok h values changed")
    checks.check(
        diagnosis.get("failure_loci")
        == [
            {
                "h": 0.02,
                "tolerance": 1e-10,
                "failure_time": 2.24,
                "failure_iteration_k": 100,
                "message_parsed": True,
            },
            {
                "h": 0.01,
                "tolerance": 1e-10,
                "failure_time": 5.8,
                "failure_iteration_k": 100,
                "message_parsed": True,
            },
        ],
        "Newton failure loci changed",
    )
    checks.check(diagnosis.get("pair_orders_available") is False, "pair orders overclaimed")
    checks.check(
        all("Newton-Raphson not converging" in message for message in diagnosis.get("failure_messages", [])),
        "failure messages no longer record Newton nonconvergence",
    )
    for label in [
        "selected_step_trio_incomplete",
        "coarse_and_mid_rows_newton_failure",
        "newton_failures_at_k_100_under_rA_half_tolerance_1e_10",
        "single_ok_row_insufficient_for_order",
        "full_public_grid_not_selected",
        "tolerance_repair_attempt_recorded_but_source_policy_still_open",
        "work_precision_publication_binding_missing",
    ]:
        checks.check(label in diagnosis.get("root_cause_labels", []), f"root-cause label missing: {label}")

    checks.check(
        tolerance_context.get("audit_status")
        == "tolerance_repair_attempt_recorded_not_source_policy_closure",
        "tolerance repair audit status changed",
    )
    checks.check(tolerance_context.get("original_tolerance_base") == 1e-10, "original tolerance base changed")
    checks.check(tolerance_context.get("repair_tolerance_base") == 1e-7, "repair tolerance base changed")
    checks.check(
        tolerance_context.get("additional_repair_tolerance_bases") == [1e-6],
        "additional repair tolerance bases changed",
    )
    checks.check(tolerance_context.get("combined_best_rows_ok_total") == [19, 24], "repair combined row count changed")
    checks.check(tolerance_context.get("combined_best_complete_groups") == [4, 8], "repair complete group count changed")
    checks.check(tolerance_context.get("recovered_row_count") == 1, "repair recovered-row count changed")
    checks.check(
        tolerance_context.get("source_policy_reproduction_closed") is False,
        "tolerance repair unexpectedly closes source policy",
    )
    checks.check(tolerance_context.get("full_T8_policy_completed") is False, "tolerance repair unexpectedly closes T8")
    checks.check(
        tolerance_context.get("external_superiority_claim_allowed") is False,
        "tolerance repair overclaims external superiority",
    )
    checks.check(
        "useful negative evidence only" in tolerance_context.get("interpretation", ""),
        "tolerance repair interpretation changed",
    )

    checks.check(promotion.get("promotion_ready") is False, "promotion readiness overclaimed")
    checks.check(promotion.get("source_policy_rows_promoted_by_this_diagnosis") == 0, "diagnosis promoted rows")
    checks.check(promotion.get("source_policy_rows_closed_by_this_diagnosis") == 0, "diagnosis closed rows")
    checks.check(promotion.get("b4_b7_can_close_from_this_diagnosis") is False, "diagnosis overcloses B4/B7")
    checks.check(promotion.get("external_superiority_claim_allowed") is False, "diagnosis overclaims superiority")
    checks.check("completed only the h=0.005 row" in promotion.get("reason", ""), "promotion reason changed")

    for row in rows:
        checks.check(row.get("source_policy_time_window_selected") is True, f"row {row.get('h')} T marker missing")
        checks.check(row.get("source_policy_reference_h_selected") is True, f"row {row.get('h')} ref marker missing")
        checks.check(row.get("source_policy_selected_coarse_h") is True, f"row {row.get('h')} h marker missing")
        checks.check(row.get("full_public_grid_selected") is False, f"row {row.get('h')} overclaims full grid")
        checks.check(row.get("source_policy_row_promoted") is False, f"row {row.get('h')} promoted")
        checks.check(row.get("canonical_hi2022_output_untouched") is True, f"row {row.get('h')} canonical marker missing")
    by_h = {row.get("h"): row for row in rows}
    checks.check(by_h.get(0.02, {}).get("failed") is True, "h=0.02 failure marker changed")
    checks.check(by_h.get(0.01, {}).get("failed") is True, "h=0.01 failure marker changed")
    checks.check(by_h.get(0.005, {}).get("status") == "ok", "h=0.005 ok marker changed")
    checks.check(by_h.get(0.02, {}).get("newton_failure_message_parsed") is True, "h=0.02 failure parse changed")
    checks.check(by_h.get(0.01, {}).get("newton_failure_message_parsed") is True, "h=0.01 failure parse changed")
    checks.check(by_h.get(0.02, {}).get("newton_failure_time") == 2.24, "h=0.02 failure time changed")
    checks.check(by_h.get(0.01, {}).get("newton_failure_time") == 5.8, "h=0.01 failure time changed")
    checks.check(by_h.get(0.02, {}).get("newton_failure_iteration_k") == 100, "h=0.02 failure k changed")
    checks.check(by_h.get(0.01, {}).get("newton_failure_iteration_k") == 100, "h=0.01 failure k changed")
    checks.check(by_h.get(0.005, {}).get("newton_failure_message_parsed") is False, "ok row should not parse failure")

    for token in [
        "Status: **diagnosis only; partial Newton-failure shard is not promoted**.",
        "Rows ok/failed/total: `1/2/3`.",
        "Selected step trio completed: `False`.",
        "Newton failure count: `2`.",
        "Failed h values: `[0.02, 0.01]`.",
        "failure_time': 2.24",
        "failure_time': 5.8",
        "Selected tolerance values: `[1e-10]`.",
        "Tolerance repair combined best rows/groups: `19/24` rows, `4/8` groups.",
        "Tolerance repair source-policy closed: `False`.",
        "Pair orders available: `False`.",
        "Promotion ready: `False`.",
        "Source-policy rows promoted by this diagnosis: `0`.",
        "B4/B7 can close from this diagnosis: `False`.",
        "These rows remain a root-cause diagnostic for B4/B7, not row-closure or external-superiority evidence.",
    ]:
        checks.check(token in audit_md, f"markdown missing token: {token}")

    if checks.errors:
        print("HI2022 rA_half double source-policy failure diagnosis validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("HI2022 rA_half double source-policy failure diagnosis validation: PASS")
    print("rows_ok_failed_total=1/2/3")
    print("newton_failure_count=2")
    print("source_policy_rows_promoted=0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
