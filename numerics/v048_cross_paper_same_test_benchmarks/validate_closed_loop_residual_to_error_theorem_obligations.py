#!/usr/bin/env python3
"""Validate closed-loop residual-to-error theorem obligations."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
MODELS = {"four_link", "slider_crank"}
EXPECTED_IDS = {"R2E-1", "R2E-2", "R2E-3", "R2E-4", "R2E-5", "R2E-6", "R2E-7"}


class Checks:
    def __init__(self) -> None:
        self.errors: list[str] = []

    def check(self, condition: bool, message: str) -> None:
        if not condition:
            self.errors.append(message)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def read_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def main() -> int:
    checks = Checks()
    try:
        rows = read_csv(RESULTS / "closed_loop_residual_to_error_theorem_obligations.csv")
        summary = read_json(RESULTS / "closed_loop_residual_to_error_theorem_obligations.json")
        report = (RESULTS / "closed_loop_residual_to_error_theorem_obligations.md").read_text(
            encoding="utf-8"
        )
        feasibility = read_json(RESULTS / "closed_loop_true_dynamic_row_feasibility_audit.json")
        floor = read_json(RESULTS / "closed_loop_dynamic_error_floor_audit.json")
        coarse = read_json(RESULTS / "closed_loop_coarse_dynamic_order_probe.json")
    except Exception as exc:  # noqa: BLE001 - concise CLI failure.
        print(f"closed-loop residual-to-error theorem obligations validation: FAIL\n- {exc}")
        return 1

    checks.check(summary.get("schema") == "closed-loop-residual-to-error-theorem-obligations-v1", "schema changed")
    checks.check(summary.get("default_policy") == "coarse_first_no_default_1e-4", "default policy changed")
    checks.check(set(summary.get("models", [])) == MODELS, "model set changed")
    checks.check(summary.get("obligation_count") == 7, "obligation count changed")
    checks.check(summary.get("blocking_obligation_count") == 7, "blocking obligation count changed")
    checks.check(summary.get("accepted_residual_to_error_theorem") is False, "residual-to-error theorem incorrectly accepted")
    checks.check(summary.get("accepted_dynamic_order_count") == 0, "dynamic order incorrectly accepted")
    checks.check(summary.get("true_dynamic_local_rows_available") == 0, "true dynamic local rows unexpectedly available")
    checks.check(
        summary.get("current_local_row_kind") == "kinematic_fullva_plus_reaction_reconstruction",
        "local row kind changed",
    )
    checks.check(summary.get("position_floor_blocker_count") == 2, "position floor blocker count changed")
    checks.check(summary.get("local_velocity_evidence_rows") == 2, "velocity evidence count changed")
    checks.check(summary.get("local_acceleration_evidence_rows") == 2, "acceleration evidence count changed")
    checks.check(summary.get("strict_public_policy_1e-4_required") is False, "strict 1e-4 incorrectly required")
    checks.check(summary.get("external_superiority_claim") is False, "external superiority incorrectly accepted")
    checks.check(summary.get("submission_ready") is False, "submission-ready incorrectly accepted")
    checks.check(
        feasibility.get("true_dynamic_local_rows_available") == 0,
        "feasibility audit no longer agrees on true dynamic rows",
    )
    checks.check(floor.get("position_floor_blocker_count") == 2, "floor audit no longer agrees")
    checks.check(coarse.get("accepted_dynamic_order_count") == 0, "coarse probe no longer agrees")

    checks.check(len(rows) == 7, "expected seven theorem-obligation rows")
    checks.check({row.get("obligation_id") for row in rows} == EXPECTED_IDS, "obligation IDs changed")
    for row in rows:
        oid = row.get("obligation_id", "<missing>")
        checks.check(row.get("blocking") == "true", f"{oid} should remain blocking")
        checks.check(row.get("current_status") not in {"satisfied", "accepted"}, f"{oid} unexpectedly accepted")
        checks.check(row.get("next_artifact"), f"{oid} missing next artifact")
        checks.check(row.get("required_for_acceptance"), f"{oid} missing acceptance requirement")

    by_id = {row.get("obligation_id"): row for row in rows}
    checks.check(by_id["R2E-1"].get("current_status") == "not_satisfied", "R2E-1 status changed")
    checks.check("same local dynamic DAE trajectory map" in by_id["R2E-1"].get("required_for_acceptance", ""), "R2E-1 weakened")
    checks.check(by_id["R2E-2"].get("current_status") == "partial_evidence_not_rate_proof", "R2E-2 status changed")
    checks.check(by_id["R2E-3"].get("current_status") == "missing", "R2E-3 status changed")
    checks.check(by_id["R2E-4"].get("current_status") == "partial_but_position_floor_blocked", "R2E-4 status changed")
    checks.check(by_id["R2E-5"].get("current_status") == "not_satisfied", "R2E-5 status changed")
    checks.check(by_id["R2E-6"].get("current_status") == "campaign_exists_but_not_accepted", "R2E-6 status changed")
    checks.check(by_id["R2E-7"].get("current_status") == "missing", "R2E-7 status changed")

    for token in [
        "Closed-Loop Residual-to-Error Theorem Obligations",
        "residual-to-error promotion is not accepted",
        "Small reaction residuals are useful evidence",
        "dynamic residual identity",
        "stability or inf-sup bound",
        "reference-floor exclusion",
        "manuscript theorem and proof",
        "accepted dynamic-order rows",
    ]:
        checks.check(token in report, f"report missing token: {token}")

    if checks.errors:
        print("closed-loop residual-to-error theorem obligations validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("closed-loop residual-to-error theorem obligations validation: PASS")
    print("obligations=7")
    print("blocking_obligations=7")
    print("accepted_residual_to_error_theorem=False")
    print("accepted_dynamic_order=0")
    print("true_dynamic_local_rows=0")
    print("default_1e-4=False")
    print("external_superiority_claim=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
