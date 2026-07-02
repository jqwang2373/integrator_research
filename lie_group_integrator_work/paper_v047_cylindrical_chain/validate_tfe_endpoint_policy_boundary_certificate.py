#!/usr/bin/env python3
"""Validate the TFE endpoint policy boundary certificate."""

from __future__ import annotations

import csv
import json
import math
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
JSON_PATH = PAPER / "TFE_ENDPOINT_POLICY_BOUNDARY_CERTIFICATE.json"
MD_PATH = PAPER / "TFE_ENDPOINT_POLICY_BOUNDARY_CERTIFICATE.md"
CSV_PATH = PAPER / "TFE_ENDPOINT_POLICY_BOUNDARY_CERTIFICATE.csv"


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


def as_float(value: Any) -> float:
    try:
        out = float(value)
    except (TypeError, ValueError):
        return float("nan")
    return out if math.isfinite(out) else float("nan")


def main() -> int:
    checks = Checks()
    try:
        cert = read_json(JSON_PATH)
        grid = read_json(PAPER / "TFE_SOURCE_GRID_COMPATIBILITY_AUDIT.json")
        endpoint_probe = read_json(PAPER / "TFE_ALGORITHM_LITERAL_ENDPOINT_PROBE.json")
        endpoint_work = read_json(PAPER / "TFE_ALGORITHM_LITERAL_WORK_PRECISION_AUDIT.json")
        sensitivity = read_json(PAPER / "TFE_ENDPOINT_POLICY_SENSITIVITY_AUDIT.json")
        rows = read_csv(CSV_PATH)
        md = MD_PATH.read_text(encoding="utf-8", errors="replace")
    except Exception as exc:  # noqa: BLE001
        print(f"TFE endpoint policy boundary certificate validation: FAIL\n- {exc}")
        return 1

    checks.check(
        cert.get("schema") == "tfe-endpoint-policy-boundary-certificate-v1",
        "schema changed",
    )
    checks.check(
        cert.get("status") == "endpoint_policy_literal_overrun_bound_proved_source_policy_open",
        "status changed",
    )
    checks.check(cert.get("read_only") is True, "certificate must be read-only")
    checks.check(cert.get("submission_ready") is False, "certificate overclaims submission readiness")
    checks.check(cert.get("source_policy_rows_completed") == 0, "certificate overcloses source-policy rows")
    checks.check(cert.get("external_superiority_claim_allowed") is False, "certificate overclaims superiority")
    checks.check(
        cert.get("source_policy_exact_T_error_sampling_equivalent") is False,
        "certificate overclaims exact-T error sampling",
    )
    checks.check(
        cert.get("source_policy_method_runner_equivalent") is False,
        "certificate overclaims method-runner equivalence",
    )
    checks.check(
        cert.get("source_grid_policy_resolved_for_full_T10") is False,
        "certificate overcloses full T=10 grid policy",
    )
    checks.check(
        cert.get("source_grid_policy_resolved_for_exact_T_compatible_rows")
        == grid.get("source_grid_policy_resolved_for_exact_T_compatible_rows")
        is True,
        "exact-T compatible subset boundary changed",
    )
    checks.check(
        cert.get("algorithm_literal_endpoint_policy")
        == endpoint_probe.get("algorithm_literal_endpoint_policy")
        == "fixed_h_until_tn_ge_tfinal",
        "algorithm-literal endpoint policy changed",
    )
    checks.check(cert.get("t_final") == 10.0, "T horizon changed")
    checks.check(cert.get("row_count") == 6, "source h row count changed")
    checks.check(cert.get("algorithm_literal_exact_T_row_count") == 2, "exact-T row count changed")
    checks.check(cert.get("algorithm_literal_overrun_row_count") == 4, "overrun row count changed")

    expected_compatible = [
        "frictional_pendulum:h=0.008",
        "frictional_pendulum:h=0.2",
    ]
    expected_incompatible = [
        "frictionless_pendulum:h=0.003",
        "frictionless_pendulum:h=0.006",
        "frictionless_pendulum:h=0.012",
        "frictional_pendulum:h=0.003",
    ]
    checks.check(cert.get("source_endpoint_compatible_row_ids") == expected_compatible, "compatible IDs changed")
    checks.check(cert.get("source_endpoint_incompatible_row_ids") == expected_incompatible, "incompatible IDs changed")
    checks.check(
        cert.get("source_endpoint_incompatible_row_ids_demoted_from_source_policy")
        == expected_incompatible,
        "demoted incompatible IDs changed",
    )
    checks.check(
        cert.get("endpoint_incompatible_rows_demoted_from_source_policy") == 4,
        "endpoint demotion count changed",
    )
    checks.check(
        "diagnostic-only" in cert.get("endpoint_incompatible_demotion_contract", ""),
        "endpoint demotion contract missing diagnostic boundary",
    )

    theorem = cert.get("theorem", {})
    checks.check(theorem.get("name") == "fixed_h_until_final_time_endpoint_bound", "theorem name changed")
    checks.check(len(theorem.get("proof_steps", [])) == 5, "proof step count changed")
    checks.check("0 < t_N - T < h" in theorem.get("statement", ""), "theorem statement lost overrun bound")
    checks.check("N=ceil(T/h)" in theorem.get("statement", ""), "theorem statement lost ceiling definition")

    support = cert.get("source_text_support", {})
    checks.check(support.get("source_text_available") is True, "source text support missing")
    checks.check(support.get("anchor_count", 0) >= 8, "source text anchor support changed")
    checks.check(support.get("algorithm_literal_constant_h_until_tn_ge_tfinal") is True, "fixed-h loop support missing")
    checks.check(
        support.get("source_endpoint_convention_resolved_for_error_sampling") is False,
        "source endpoint convention unexpectedly resolved",
    )

    boundary = cert.get("diagnostic_work_precision_boundary", {})
    checks.check(boundary.get("endpoint_probe_metric_rows") == endpoint_probe.get("metric_row_count") == 12, "endpoint metric rows stale")
    checks.check(
        boundary.get("endpoint_probe_terminal_overrun_rows")
        == endpoint_probe.get("terminal_overrun_rows")
        == 12,
        "endpoint overrun rows stale",
    )
    checks.check(boundary.get("work_precision_rows") == endpoint_work.get("raw_row_count") == 12, "work rows stale")
    checks.check(boundary.get("work_precision_summary_rows") == endpoint_work.get("summary_row_count") == 4, "work summary rows stale")
    checks.check(boundary.get("work_precision_figure_available") is True, "work figure marker changed")
    checks.check(boundary.get("work_precision_b4_progress") is True, "B4 progress marker changed")
    checks.check(boundary.get("work_precision_b4_closure") is False, "B4 closure overclaimed")
    checks.check(boundary.get("endpoint_sensitivity_raw_rows") == sensitivity.get("raw_row_count") == 48, "endpoint sensitivity row count stale")
    checks.check(
        boundary.get("endpoint_sensitivity_source_policy_rows_completed")
        == sensitivity.get("source_policy_rows_completed")
        == 0,
        "endpoint sensitivity source-policy rows overclosed",
    )

    cert_rows = cert.get("rows", [])
    checks.check(len(cert_rows) == len(rows) == 6, "certificate row table changed")
    csv_by_id = {row["row_id"]: row for row in rows}
    for row in cert_rows:
        row_id = row.get("row_id")
        h = as_float(row.get("h"))
        overshoot = as_float(row.get("algorithm_literal_overshoot"))
        terminal_time = as_float(row.get("algorithm_literal_terminal_time"))
        hits_exact = row.get("hits_exact_T") is True
        checks.check(row_id in csv_by_id, f"CSV missing row {row_id}")
        checks.check(as_float(row.get("t_final")) == 10.0, f"{row_id} T changed")
        checks.check(row.get("source_policy_row_completed") is False, f"{row_id} overcloses source-policy row")
        checks.check(math.isfinite(h) and h > 0.0, f"{row_id} invalid h")
        checks.check(math.isfinite(terminal_time), f"{row_id} invalid terminal time")
        if hits_exact:
            checks.check(abs(overshoot) <= 1.0e-12, f"{row_id} exact row has overrun")
            checks.check(row.get("requires_source_error_sampling_policy") is False, f"{row_id} exact row should not require endpoint policy")
            checks.check(
                row.get("source_policy_demoted_until_source_endpoint_sampling_policy") is False,
                f"{row_id} exact row demoted unexpectedly",
            )
        else:
            checks.check(0.0 < overshoot < h, f"{row_id} overrun bound failed")
            checks.check(row.get("algorithm_literal_overrun_strictly_less_than_h") is True, f"{row_id} overrun marker failed")
            checks.check(row.get("requires_source_error_sampling_policy") is True, f"{row_id} should require source endpoint policy")
            checks.check(
                row.get("source_policy_demoted_until_source_endpoint_sampling_policy") is True,
                f"{row_id} missing endpoint demotion marker",
            )
            checks.check(
                0.0 < as_float(row.get("final_partial_step_fraction_of_h")) < 1.0,
                f"{row_id} partial final step fraction invalid",
            )

    dispositions = cert.get("policy_disposition", [])
    checks.check(len(dispositions) == 4, "policy disposition count changed")
    checks.check(
        all(item.get("source_equivalent_for_exact_T_error_sampling") is False for item in dispositions),
        "a policy disposition overclaims exact-T source equivalence",
    )
    checks.check(
        all(item.get("source_policy_rows_completed") == 0 for item in dispositions),
        "a policy disposition overcloses source-policy rows",
    )

    claim_boundary = cert.get("claim_boundary", {})
    checks.check(
        claim_boundary.get("accepted_use") == "endpoint_policy_boundary_proof_not_source_policy",
        "accepted-use boundary changed",
    )
    checks.check("exact-T source-policy error sampling equivalence" in claim_boundary.get("not_proved", []), "not-proved boundary missing exact-T sampling")
    checks.check(
        any("endpoint-incompatible" in item for item in claim_boundary.get("demoted", [])),
        "claim boundary missing endpoint demotion",
    )

    source_files = cert.get("source_files", {})
    checks.check(source_files.get("grid_audit") == "TFE_SOURCE_GRID_COMPATIBILITY_AUDIT.json", "grid source file missing")
    checks.check(source_files.get("algorithm_literal_endpoint_probe") == "TFE_ALGORITHM_LITERAL_ENDPOINT_PROBE.json", "endpoint source file missing")
    checks.check(source_files.get("algorithm_literal_work_precision") == "TFE_ALGORITHM_LITERAL_WORK_PRECISION_AUDIT.json", "work source file missing")
    checks.check(source_files.get("endpoint_sensitivity") == "TFE_ENDPOINT_POLICY_SENSITIVITY_AUDIT.json", "sensitivity source file missing")

    for token in [
        "TFE Endpoint Policy Boundary Certificate",
        "Source-policy rows completed: `0`.",
        "Full T=10 source-grid policy resolved: `False`.",
        "Exact-T error-sampling equivalent: `False`.",
        "Algorithm-literal endpoint policy: `fixed_h_until_tn_ge_tfinal`.",
        "Exact-T / overrun source h rows: `2/4`.",
        "Endpoint-incompatible demoted rows: `4`.",
        "For T>0 and h>0",
        "N=ceil(T/h)",
        "Source endpoint convention resolved for error sampling: `False`.",
        "Demotion contract:",
        "Endpoint probe metric/overrun rows: `12/12`.",
        "Work-precision rows/summary/figure/B4-progress/B4-closure: `12/4/True/True/False`.",
        "No source-policy rows are closed by this certificate.",
        "Endpoint-incompatible rows remain demoted from source-policy promotion",
    ]:
        checks.check(token in md, f"markdown missing token: {token}")

    if checks.errors:
        print("TFE endpoint policy boundary certificate validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("TFE endpoint policy boundary certificate validation: PASS")
    print("rows=6")
    print("exact_overrun_rows=2/4")
    print("source_policy_rows_completed=0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
