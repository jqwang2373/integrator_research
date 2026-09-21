#!/usr/bin/env python3
"""Validate the TFE full-T10 coarse candidate summary."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path


PAPER = Path(__file__).resolve().parent
SUMMARY_JSON = PAPER / "TFE_FULL_T10_COARSE_CANDIDATE_SUMMARY.json"
SUMMARY_MD = PAPER / "TFE_FULL_T10_COARSE_CANDIDATE_SUMMARY.md"
SUMMARY_CSV = PAPER / "TFE_FULL_T10_COARSE_CANDIDATE_SUMMARY.csv"


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


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def finite(value: object) -> bool:
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def main() -> int:
    checks = Checks()
    try:
        summary = read_json(SUMMARY_JSON)
        csv_rows = read_csv(SUMMARY_CSV)
        md = SUMMARY_MD.read_text(encoding="utf-8")
    except Exception as exc:  # noqa: BLE001
        print(f"TFE full-T10 coarse candidate summary validation: FAIL\n- {exc}")
        return 1

    rows = summary.get("rows", [])
    checks.check(summary.get("schema") == "tfe-full-t10-coarse-candidate-summary-v1", "schema changed")
    checks.check(
        summary.get("status") == "full_T10_coarse_candidate_probe_summarized_not_source_policy",
        "status changed",
    )
    checks.check(summary.get("submission_ready") is False, "summary overclaims submission readiness")
    checks.check(summary.get("external_superiority_claim_allowed") is False, "summary overclaims superiority")
    checks.check(summary.get("source_policy_rows_completed") == 0, "source-policy rows unexpectedly closed")
    checks.check(summary.get("source_policy_reference_h") == 0.0001, "source-policy reference h changed")
    checks.check(summary.get("source_policy_reference_invoked") is False, "source-policy reference was invoked")
    checks.check(summary.get("default_1e_4_campaign_invoked") is False, "default 1e-4 campaign invoked")
    checks.check(summary.get("full_T10_candidate_probe_completed") is True, "full T=10 coarse probe missing")
    checks.check(summary.get("full_T10_source_policy_reproduction") is False, "source-policy overclaimed")
    checks.check(summary.get("t_final") == 10.0, "T=10 horizon changed")
    checks.check(summary.get("reference_h") == 0.0125, "coarse reference h changed")
    checks.check(summary.get("comparison_h") == [0.1, 0.05, 0.025], "comparison h-grid changed")
    checks.check(summary.get("row_count") == len(rows) == len(csv_rows) == 4, "row count changed")
    checks.check(summary.get("finite_row_count") == 4, "finite row count changed")
    checks.check(summary.get("residual_ok_row_count") == 4, "residual-ok row count changed")
    checks.check(summary.get("coordinate_error_decrease_row_count") == 4, "coordinate decrease row count changed")
    checks.check(summary.get("velocity_error_decrease_row_count") == 4, "velocity decrease row count changed")
    checks.check(summary.get("claim_boundary", {}).get("not_source_policy_reproduction") is True, "claim boundary missing")
    checks.check(summary.get("claim_boundary", {}).get("not_external_superiority_evidence") is True, "external boundary missing")

    expected_methods = {
        "tfe2026_Newmark_beta": 2,
        "tfe2026_TFE_m1": 1,
        "tfe2026_TFE_m2": 3,
        "tfe2026_trapezoidal": 2,
    }
    seen = {}
    for row in rows:
        method = row.get("paper_method")
        seen[method] = row.get("expected_order")
        checks.check(row.get("expected_order") == expected_methods.get(method), f"{method} target order changed")
        checks.check(len(row.get("coordinate_pairwise_orders", [])) == 2, f"{method} coordinate order pairs missing")
        checks.check(len(row.get("velocity_pairwise_orders", [])) == 2, f"{method} velocity order pairs missing")
        checks.check(row.get("finest_h") == 0.025, f"{method} finest h changed")
        checks.check(finite(row.get("finest_coordinate_error")), f"{method} coordinate error not finite")
        checks.check(finite(row.get("finest_velocity_error")), f"{method} velocity error not finite")
        checks.check(finite(row.get("max_newton_residual_norm")), f"{method} residual not finite")
        checks.check(row.get("source_policy_method_runner_equivalent") is False, f"{method} overclaims method equivalence")
        checks.check(row.get("source_policy_row_completed") is False, f"{method} overcloses row")
        checks.check(row.get("accepted_use") == "full_T10_coarse_candidate_probe_not_source_policy", f"{method} accepted-use changed")
    checks.check(seen == expected_methods, "method set changed")

    required_md_tokens = [
        "full T=10 coarse candidate probe summarized",
        "Source-policy rows completed: `0`",
        "tfe2026_TFE_m2",
        "not close original TFE source-policy reproduction",
    ]
    for token in required_md_tokens:
        checks.check(token in md, f"markdown missing token: {token}")

    if checks.errors:
        print("TFE full-T10 coarse candidate summary validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("TFE full-T10 coarse candidate summary validation: PASS")
    print("rows=4")
    print("finite_residual_ok=4/4")
    print("source_policy_rows_completed=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
