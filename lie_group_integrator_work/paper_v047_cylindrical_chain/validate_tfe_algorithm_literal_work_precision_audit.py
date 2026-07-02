#!/usr/bin/env python3
"""Validate the TFE algorithm-literal work/precision audit."""

from __future__ import annotations

import csv
import json
import math
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
AUDIT_JSON = PAPER / "TFE_ALGORITHM_LITERAL_WORK_PRECISION_AUDIT.json"
AUDIT_MD = PAPER / "TFE_ALGORITHM_LITERAL_WORK_PRECISION_AUDIT.md"
AUDIT_CSV = PAPER / "TFE_ALGORITHM_LITERAL_WORK_PRECISION_AUDIT.csv"
AUDIT_FIGURE = PAPER / "figures" / "tfe_algorithm_literal_work_precision.png"
SOURCE_JSON = PAPER / "TFE_ALGORITHM_LITERAL_ENDPOINT_PROBE.json"
SOURCE_CSV = PAPER / "TFE_ALGORITHM_LITERAL_ENDPOINT_PROBE.csv"
EXPECTED_METHODS = {
    "tfe2026_Newmark_beta",
    "tfe2026_TFE_m1",
    "tfe2026_TFE_m2",
    "tfe2026_trapezoidal",
}


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


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def as_float(value: object) -> float:
    try:
        out = float(value)
    except (TypeError, ValueError):
        return float("nan")
    return out if math.isfinite(out) else float("nan")


def main() -> int:
    checks = Checks()
    try:
        audit = read_json(AUDIT_JSON)
        source = read_json(SOURCE_JSON)
        rows = read_csv(AUDIT_CSV)
        source_rows = read_csv(SOURCE_CSV)
        report = AUDIT_MD.read_text(encoding="utf-8")
    except Exception as exc:  # noqa: BLE001
        print(f"TFE algorithm-literal work/precision audit validation: FAIL\n- {exc}")
        return 1

    checks.check(audit.get("schema") == "tfe-algorithm-literal-work-precision-audit-v1", "schema changed")
    checks.check(
        audit.get("status") == "algorithm_literal_T10_newton_work_precision_available_source_policy_open",
        "status changed",
    )
    checks.check(audit.get("source_probe") == "TFE_ALGORITHM_LITERAL_ENDPOINT_PROBE.json", "source probe pointer changed")
    checks.check(audit.get("source_probe_csv") == "TFE_ALGORITHM_LITERAL_ENDPOINT_PROBE.csv", "source CSV pointer changed")
    checks.check(audit.get("t_final") == source.get("t_final") == 10.0, "T=10 horizon changed")
    checks.check(audit.get("reference_h") == source.get("reference_h") == 1.0e-4, "reference h changed")
    checks.check(audit.get("comparison_h") == source.get("comparison_h") == [0.012, 0.006, 0.003], "comparison h changed")
    checks.check(
        audit.get("algorithm_literal_endpoint_policy") == source.get("algorithm_literal_endpoint_policy"),
        "endpoint policy not inherited from source probe",
    )
    checks.check(audit.get("work_proxy") == "total_newton_iterations", "work proxy changed")
    checks.check(audit.get("runtime_proxy_available") is False, "runtime proxy unexpectedly claimed")
    checks.check(audit.get("method_count") == source.get("method_count") == 4, "method count changed")
    checks.check(audit.get("raw_row_count") == source.get("metric_row_count") == 12, "raw row count changed")
    checks.check(audit.get("summary_row_count") == 4, "summary row count changed")
    checks.check(audit.get("terminal_overrun_rows") == source.get("terminal_overrun_rows") == 12, "overrun count changed")
    checks.check(audit.get("source_policy_rows_completed") == 0, "source-policy rows overclosed")
    checks.check(audit.get("source_policy_method_runner_equivalent") is False, "method equivalence overclaimed")
    checks.check(
        audit.get("source_policy_exact_T_error_sampling_equivalent") is False,
        "exact-T sampling equivalence overclaimed",
    )
    checks.check(audit.get("external_superiority_claim_allowed") is False, "external superiority overclaimed")
    checks.check(audit.get("work_precision_figure_available") is True, "figure availability marker changed")
    checks.check(AUDIT_FIGURE.exists() and AUDIT_FIGURE.stat().st_size > 10_000, "figure missing or too small")

    checks.check(len(rows) == 12, "CSV raw row count changed")
    checks.check(len(source_rows) == 12, "source CSV row count changed")
    checks.check({row.get("paper_method") for row in rows} == EXPECTED_METHODS, "CSV method set changed")
    checks.check({row.get("source_policy_row_completed") for row in rows} == {"false"}, "CSV source-policy row overclosed")
    checks.check(
        {row.get("source_policy_method_runner_equivalent") for row in rows} == {"false"},
        "CSV method equivalence overclaimed",
    )
    checks.check(
        {row.get("source_policy_exact_T_error_sampling_equivalent") for row in rows} == {"false"},
        "CSV exact-T equivalence overclaimed",
    )
    checks.check(
        {row.get("external_superiority_claim_allowed") for row in rows} == {"false"},
        "CSV external superiority overclaimed",
    )
    checks.check(
        {row.get("accepted_use") for row in rows}
        == {"algorithm_literal_T10_newton_work_precision_not_source_policy"},
        "CSV accepted-use marker changed",
    )
    for method in EXPECTED_METHODS:
        group = [row for row in rows if row.get("paper_method") == method]
        checks.check(len(group) == 3, f"{method} row count changed")
        checks.check(all(as_float(row.get("h")) in {0.012, 0.006, 0.003} for row in group), f"{method} h-grid changed")
        checks.check(all(as_float(row.get("work_units_newton_iterations")) > 0.0 for row in group), f"{method} work missing")
        checks.check(all(as_float(row.get("velocity_error_v")) > 0.0 for row in group), f"{method} velocity error missing")
        checks.check(all(as_float(row.get("coordinate_error_q")) > 0.0 for row in group), f"{method} coordinate error missing")
        checks.check(all(as_float(row.get("terminal_overshoot")) > 0.0 for row in group), f"{method} overrun marker missing")
        checks.check(all(as_float(row.get("max_residual_norm")) < 1.0e-8 for row in group), f"{method} residual too large")

    summary_rows = audit.get("summary_rows", [])
    checks.check(isinstance(summary_rows, list) and len(summary_rows) == 4, "summary rows changed")
    for row in summary_rows if isinstance(summary_rows, list) else []:
        method = row.get("paper_method")
        checks.check(method in EXPECTED_METHODS, f"unexpected summary method {method}")
        checks.check(row.get("row_count") == 3, f"{method} summary row count changed")
        checks.check(row.get("terminal_overrun_rows") == 3, f"{method} terminal overrun count changed")
        checks.check(row.get("source_policy_row_completed") is False, f"{method} summary overclosed source policy")
        checks.check(row.get("source_policy_method_runner_equivalent") is False, f"{method} summary overclaimed method equivalence")
        checks.check(as_float(row.get("work_units_newton_iterations_sum")) > 0.0, f"{method} summary work missing")
        checks.check(as_float(row.get("finest_velocity_error_v")) > 0.0, f"{method} summary velocity error missing")

    for token in [
        "TFE Algorithm-Literal Work/Precision Audit",
        "Work proxy: `total_newton_iterations`",
        "Runtime proxy available: `False`",
        "Methods/raw rows/summary rows: `4/12/4`",
        "Terminal-overrun rows: `12`",
        "Source-policy rows completed: `0`",
        "External superiority claim allowed: `False`",
        "not a source-policy reproduction",
    ]:
        checks.check(token in report, f"markdown missing token: {token}")

    if checks.errors:
        print("TFE algorithm-literal work/precision audit validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("TFE algorithm-literal work/precision audit validation: PASS")
    print("methods=4")
    print("raw_rows=12")
    print("summary_rows=4")
    print("terminal_overrun_rows=12")
    print("source_policy_rows_completed=0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
