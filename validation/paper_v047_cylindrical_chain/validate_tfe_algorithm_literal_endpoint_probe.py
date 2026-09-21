#!/usr/bin/env python3
"""Validate the TFE algorithm-literal endpoint probe."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
JSON_PATH = PAPER / "TFE_ALGORITHM_LITERAL_ENDPOINT_PROBE.json"
MD_PATH = PAPER / "TFE_ALGORITHM_LITERAL_ENDPOINT_PROBE.md"
CSV_PATH = PAPER / "TFE_ALGORITHM_LITERAL_ENDPOINT_PROBE.csv"
EXPECTED_METHODS = {
    "tfe2026_Newmark_beta",
    "tfe2026_TFE_m1",
    "tfe2026_TFE_m2",
    "tfe2026_trapezoidal",
}
EXPECTED_H = {0.012, 0.006, 0.003}


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
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def finite(value: Any) -> bool:
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def main() -> int:
    checks = Checks()
    try:
        audit = read_json(JSON_PATH)
        rows = read_csv(CSV_PATH)
        md = MD_PATH.read_text(encoding="utf-8", errors="replace")
    except Exception as exc:  # noqa: BLE001
        print(f"TFE algorithm-literal endpoint probe validation: FAIL\n- {exc}")
        return 1

    checks.check(audit.get("schema") == "tfe-algorithm-literal-endpoint-probe-v1", "schema changed")
    checks.check(
        audit.get("status") == "algorithm_literal_full_T10_probe_available_source_policy_open",
        "status changed",
    )
    checks.check(audit.get("submission_ready") is False, "probe overclaims submission readiness")
    checks.check(audit.get("external_superiority_claim_allowed") is False, "probe overclaims superiority")
    checks.check(audit.get("source_policy_rows_completed") == 0, "probe overcloses source-policy rows")
    checks.check(
        audit.get("source_policy_method_runner_equivalent") is False,
        "probe overclaims method-runner equivalence",
    )
    checks.check(
        audit.get("source_policy_exact_T_error_sampling_equivalent") is False,
        "probe overclaims exact-T error-sampling equivalence",
    )
    checks.check(
        audit.get("source_text_fixed_h_loop_supported") is True,
        "source fixed-h loop support not carried into probe",
    )
    checks.check(audit.get("method_count") == 4, "method count changed")
    checks.check(audit.get("metric_row_count") == 12, "metric row count changed")
    checks.check(audit.get("terminal_overrun_rows") == 12, "terminal overrun count changed")
    checks.check(set(audit.get("comparison_h", [])) == EXPECTED_H, "comparison h values changed")
    checks.check(audit.get("reference_h") == 1.0e-4, "reference h changed")
    checks.check(audit.get("t_final") == 10.0, "t_final changed")

    method_rows = audit.get("method_rows", [])
    checks.check({row.get("paper_method") for row in method_rows} == EXPECTED_METHODS, "method labels changed")
    for row in method_rows:
        checks.check(row.get("source_policy_row_completed") is False, f"{row.get('paper_method')} overclosed")
        checks.check(row.get("source_policy_method_runner_equivalent") is False, f"{row.get('paper_method')} overclaims equivalence")
        checks.check(row.get("finite_metrics") is True, f"{row.get('paper_method')} has non-finite metrics")
        checks.check(finite(row.get("max_residual_norm")), f"{row.get('paper_method')} residual not finite")
        checks.check(len(row.get("metrics", [])) == 3, f"{row.get('paper_method')} metric count changed")

    checks.check(len(rows) == 12, "CSV row count changed")
    checks.check({row["paper_method"] for row in rows} == EXPECTED_METHODS, "CSV method labels changed")
    checks.check({float(row["h"]) for row in rows} == EXPECTED_H, "CSV h values changed")
    for row in rows:
        checks.check(row.get("source_policy_row_completed") == "false", "CSV row overcloses source policy")
        checks.check(float(row["terminal_overshoot"]) > 0.0, "CSV terminal overrun missing")
        for key in ["coordinate_error_q", "velocity_error_v", "frobenius_error_norm_eta", "max_residual_norm"]:
            checks.check(finite(row.get(key)), f"CSV non-finite {key}")

    for token in [
        "TFE Algorithm-Literal Endpoint Probe",
        "Source text fixed-h loop supported: `True`",
        "Endpoint policy: `fixed_h_until_tn_ge_tfinal`",
        "Methods / metric rows: `4/12`",
        "Terminal overrun rows: `12`",
        "Source-policy rows completed: `0`",
        "Exact-T error sampling equivalent: `False`",
    ]:
        checks.check(token in md, f"markdown missing token: {token}")

    if checks.errors:
        print("TFE algorithm-literal endpoint probe validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("TFE algorithm-literal endpoint probe validation: PASS")
    print(f"methods={audit.get('method_count')}")
    print(f"metric_rows={audit.get('metric_row_count')}")
    print(f"terminal_overrun_rows={audit.get('terminal_overrun_rows')}")
    print(f"source_policy_rows_completed={audit.get('source_policy_rows_completed')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
