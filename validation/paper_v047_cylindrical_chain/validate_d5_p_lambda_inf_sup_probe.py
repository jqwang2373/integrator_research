#!/usr/bin/env python3
"""Validate the finite P_lambda multiplier-column inf-sup probe."""

from __future__ import annotations

import csv
import json
import math
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
AUDIT_JSON = PAPER / "D5_P_LAMBDA_INF_SUP_PROBE.json"
AUDIT_MD = PAPER / "D5_P_LAMBDA_INF_SUP_PROBE.md"
AUDIT_CSV = PAPER / "D5_P_LAMBDA_INF_SUP_PROBE.csv"


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


def finite_positive(value: Any) -> bool:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return False
    return math.isfinite(number) and number > 0.0


def main() -> int:
    checks = Checks()
    try:
        audit = read_json(AUDIT_JSON)
        audit_md = AUDIT_MD.read_text(encoding="utf-8", errors="replace")
        audit_csv = read_csv(AUDIT_CSV)
        p_lambda_interface = read_json(PAPER / "D5_P_LAMBDA_INTERFACE_AUDIT.json")
        d3_wrench = read_json(PAPER / "NEWTON_EULER_VIRTUAL_WORK_WRENCH_AUDIT.json")
        dynamic_oracle = read_json(PAPER / "DYNAMIC_ROW_ORACLE_GATE.json")
    except Exception as exc:  # noqa: BLE001
        print(f"D5 P_lambda inf-sup probe validation: FAIL\n- {exc}")
        return 1

    summary = audit.get("summary", {})
    source = audit.get("source_consistency", {})
    probes = audit.get("probes", [])
    boundary = audit.get("claim_boundary", {})

    checks.check(audit.get("schema") == "d5-p-lambda-inf-sup-probe-v1", "schema changed")
    checks.check(
        audit.get("status") == "finite_p_lambda_inf_sup_probe_recorded_uniform_constant_not_proved",
        "status changed",
    )
    checks.check(audit.get("read_only") is True, "probe must be read-only")
    checks.check(audit.get("run_v047_invoked") is False, "full v047 runner must not be invoked")
    checks.check(audit.get("one_step_stage_newton_invoked") is True, "one-step stage Newton marker missing")
    checks.check(audit.get("submission_ready") is False, "submission readiness overclaimed")
    checks.check(audit.get("proof_gap_closed") is False, "proof gap unexpectedly closed")
    checks.check(audit.get("pc2_closed") is False, "PC2 unexpectedly closed")
    checks.check(audit.get("primitive_closed") is False, "P_lambda unexpectedly closed")
    checks.check(audit.get("p_lambda_inf_sup_probe_recorded") is True, "probe marker missing")
    checks.check(audit.get("pl2_uniform_inf_sup_bound_proved") is False, "PL2 uniform bound unexpectedly proved")
    checks.check(audit.get("uniform_constant_proved") is False, "uniform constant unexpectedly proved")
    checks.check(audit.get("multiplier_lift_rate_proved") is False, "multiplier lift unexpectedly proved")
    checks.check(audit.get("term_bounds_proved") == 0, "Taylor bounds unexpectedly proved")
    checks.check(audit.get("h_values") == [0.04, 0.02, 0.01], "probe h-values changed")

    checks.check(summary.get("probe_count") == 3, "probe count changed")
    checks.check(summary.get("dynamic_row_dimension") == 36, "dynamic row dimension changed")
    checks.check(summary.get("lambda_column_dimension") == 24, "lambda column dimension changed")
    checks.check(summary.get("operator_shape") == [36, 24], "operator shape changed")
    checks.check(summary.get("finite_probe_full_column_rank_all") is True, "finite full-rank probe failed")
    checks.check(summary.get("min_operator_rank") == 24, "minimum operator rank changed")
    checks.check(summary.get("max_operator_rank") == 24, "maximum operator rank changed")
    checks.check(finite_positive(summary.get("min_singular_value_across_probes")), "minimum singular value invalid")
    checks.check(finite_positive(summary.get("max_condition_number_across_probes")), "condition number invalid")
    checks.check(summary.get("max_condition_number_across_probes", 1.0e9) < 100.0, "condition number unexpectedly large")
    checks.check(
        finite_positive(summary.get("max_finite_multiplier_recovery_constant")),
        "finite recovery constant invalid",
    )
    checks.check(finite_positive(summary.get("max_gauss_stage_residual_norm")), "stage residual invalid")
    checks.check(summary.get("max_gauss_stage_residual_norm", 1.0) < 1.0e-9, "stage residual too large")
    checks.check(summary.get("p_lambda_interface_closed") is True, "P_lambda interface not linked")
    checks.check(summary.get("d3_multiplier_wrench_consistency_closed") is True, "D3 wrench consistency not linked")
    checks.check(summary.get("pl2_uniform_inf_sup_bound_proved") is False, "PL2 closure overclaimed")

    checks.check(
        source.get("p_lambda_interface_schema") == "d5-p-lambda-interface-audit-v1",
        "P_lambda interface schema not linked",
    )
    checks.check(
        source.get("p_lambda_interface_closed") is True
        and p_lambda_interface.get("pl1_interface_closed") is True,
        "P_lambda PL1 interface closure missing",
    )
    checks.check(
        source.get("p_lambda_interface_primitive_closed") is False
        and p_lambda_interface.get("primitive_closed") is False,
        "P_lambda primitive unexpectedly closed",
    )
    checks.check(source.get("p_lambda_interface_pc2_closed") is False, "P_lambda interface unexpectedly closes PC2")
    checks.check(source.get("p_lambda_term_rows_using_obligation") == 72, "P_lambda term-row link changed")
    checks.check(source.get("d3_wrench_schema") == d3_wrench.get("schema"), "D3 schema link mismatch")
    checks.check(source.get("d3_multiplier_wrench_consistency_closed") is True, "D3 consistency link missing")
    checks.check(source.get("d3_stage_residual_defect_proved") is False, "D3 unexpectedly proves D5")
    checks.check(source.get("d3_link_closed") is True, "D3 link should be closed")
    dynamic_oracle_formula = dynamic_oracle.get("formula_row_ad_jacobian_oracle", {})
    checks.check(source.get("dynamic_oracle_schema") == dynamic_oracle.get("schema"), "dynamic oracle schema link mismatch")
    checks.check(source.get("runtime_row_dimension") == 132, "runtime row dimension changed")
    checks.check(
        source.get("dynamic_oracle_runtime_rows") == dynamic_oracle_formula.get("row_count") == 132,
        "dynamic oracle runtime row count changed",
    )
    checks.check(
        source.get("dynamic_oracle_runtime_columns") == dynamic_oracle_formula.get("column_count") == 132,
        "dynamic oracle runtime column count changed",
    )

    checks.check(isinstance(probes, list) and len(probes) == 3, "probe table changed")
    for row in probes:
        checks.check(row.get("full_column_rank") is True, f"probe h={row.get('h')} not full column rank")
        checks.check(row.get("operator_rank") == row.get("lambda_column_count") == 24, "probe rank/domain mismatch")
        checks.check(row.get("dynamic_row_count") == 36, "probe row count mismatch")
        checks.check(row.get("operator_shape") == [36, 24], "probe operator shape mismatch")
        checks.check(finite_positive(row.get("min_singular_value")), "probe singular value invalid")
        checks.check(finite_positive(row.get("condition_number")), "probe condition invalid")
        checks.check(row.get("condition_number", 1.0e9) < 100.0, "probe condition unexpectedly large")
        checks.check(finite_positive(row.get("finite_multiplier_recovery_constant")), "probe recovery constant invalid")
        checks.check(row.get("gauss_stage_residual_norm", 1.0) < 1.0e-9, "probe stage residual too large")

    checks.check(len(audit_csv) == 3, "CSV probe rows changed")
    csv_h_values = sorted(float(row["h"]) for row in audit_csv)
    checks.check(csv_h_values == [0.01, 0.02, 0.04], "CSV h-values changed")
    for row in audit_csv:
        checks.check(int(row["operator_rank"]) == int(row["lambda_column_count"]) == 24, "CSV rank mismatch")
        checks.check(row["full_column_rank"] == "True", "CSV full-rank marker changed")

    checks.check(
        "uniform P_lambda inf-sup theorem" in boundary.get("forbidden_now", []),
        "claim boundary no longer forbids uniform P_lambda theorem",
    )
    for token in [
        "Status: **finite multiplier-column inf-sup probe recorded; finite probe itself does not close PL2**.",
        "Full column rank in all finite probes: `True`.",
        "PL2 uniform inf-sup bound proved: `False`.",
        "Multiplier lift rate proved: `False`.",
        "Primitive/Taylor PC2 route closed: `False`.",
        "This is a finite solved-stage rank diagnostic.",
        "It does not prove a uniform compact-tube inf-sup constant.",
        "The finite probe itself does not close PL2; P_lambda, PC2, and the unconditional D5 theorem remain open.",
    ]:
        checks.check(token in audit_md, f"markdown missing token: {token}")

    if checks.errors:
        print("D5 P_lambda inf-sup probe validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("D5 P_lambda inf-sup probe validation: PASS")
    print("finite_probe_full_column_rank_all=True")
    print("pl2_uniform_inf_sup_bound_proved=False")
    print("pc2_closed=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
