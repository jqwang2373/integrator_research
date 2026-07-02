#!/usr/bin/env python3
"""Validate the finite PS2 weighted linearization probe."""

from __future__ import annotations

import csv
import json
import math
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
AUDIT_JSON = PAPER / "D5_P_STATE_PS2_LINEARIZATION_PROBE.json"
AUDIT_MD = PAPER / "D5_P_STATE_PS2_LINEARIZATION_PROBE.md"
AUDIT_CSV = PAPER / "D5_P_STATE_PS2_LINEARIZATION_PROBE.csv"


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
        ps2_target = read_json(PAPER / "D5_P_STATE_PS2_WEIGHTED_TARGET_AUDIT.json")
        dynamic_oracle = read_json(PAPER / "DYNAMIC_ROW_ORACLE_GATE.json")
    except Exception as exc:  # noqa: BLE001
        print(f"D5 P_state PS2 linearization probe validation: FAIL\n- {exc}")
        return 1

    summary = audit.get("summary", {})
    source = audit.get("source_consistency", {})
    probes = audit.get("probes", [])
    boundary = audit.get("claim_boundary", {})

    checks.check(audit.get("schema") == "d5-p-state-ps2-linearization-probe-v1", "schema changed")
    checks.check(
        audit.get("status") == "finite_ps2_weighted_linearization_probe_recorded_ps2_open",
        "status changed",
    )
    checks.check(audit.get("read_only") is True, "probe must be read-only")
    checks.check(audit.get("run_v047_invoked") is False, "full v047 runner must not be invoked")
    checks.check(audit.get("one_step_stage_newton_invoked") is True, "one-step stage Newton marker missing")
    checks.check(audit.get("submission_ready") is False, "submission readiness overclaimed")
    checks.check(audit.get("proof_gap_closed") is False, "proof gap unexpectedly closed")
    checks.check(audit.get("pc2_closed") is False, "PC2 unexpectedly closed")
    checks.check(audit.get("primitive_closed") is False, "P_state unexpectedly closed")
    checks.check(audit.get("ps2_weighted_linearization_probe_recorded") is True, "probe marker missing")
    checks.check(audit.get("ps2_inverse_or_infsup_closed") is False, "PS2 inf-sup unexpectedly closed")
    checks.check(audit.get("uniform_constant_proved") is False, "uniform constant unexpectedly proved")
    checks.check(audit.get("p_state_lift_rate_proved") is False, "P_state lift rate unexpectedly proved")
    checks.check(audit.get("h_values") == [0.04, 0.02, 0.01], "probe h-values changed")
    checks.check(summary.get("probe_count") == 3, "probe count changed")
    checks.check(summary.get("state_block_dimension") == 72, "state dimension changed")
    checks.check(summary.get("auxiliary_acceleration_dimension") == 36, "acceleration dimension changed")
    checks.check(summary.get("domain_dimension") == 108, "domain dimension changed")
    checks.check(summary.get("non_dynamic_row_dimension") == 96, "non-dynamic row dimension changed")
    checks.check(summary.get("weighted_operator_shape") == [132, 108], "weighted operator shape changed")
    checks.check(summary.get("finite_probe_full_column_rank_all") is True, "finite full-rank probe failed")
    checks.check(summary.get("min_weighted_operator_rank") == 108, "minimum weighted rank changed")
    checks.check(summary.get("max_weighted_operator_rank") == 108, "maximum weighted rank changed")
    checks.check(finite_positive(summary.get("min_singular_value_across_probes")), "minimum singular value invalid")
    checks.check(
        finite_positive(summary.get("max_finite_state_projection_constant")),
        "state projection constant invalid",
    )
    checks.check(finite_positive(summary.get("max_gauss_stage_residual_norm")), "stage residual invalid")
    checks.check(summary.get("ps2_weighted_target_spec_closed") is True, "PS2 target spec not linked")
    checks.check(summary.get("ps2_inverse_or_infsup_closed") is False, "PS2 inverse unexpectedly linked closed")
    checks.check(source.get("ps2_target_schema") == "d5-p-state-ps2-weighted-target-audit-v1", "PS2 target schema not linked")
    checks.check(source.get("ps2_target_spec_closed") is True, "PS2 target spec source not closed")
    checks.check(source.get("ps2_target_infsup_closed") is False, "PS2 target source unexpectedly closes inf-sup")
    checks.check(source.get("ps2_target_state_dim") == ps2_target.get("summary", {}).get("state_block_dimension") == 72, "PS2 target state dimension mismatch")
    checks.check(source.get("ps2_target_acc_dim") == ps2_target.get("summary", {}).get("auxiliary_acceleration_dimension") == 36, "PS2 target acceleration dimension mismatch")
    checks.check(source.get("ps2_target_row_dim") == ps2_target.get("summary", {}).get("non_dynamic_row_dimension") == 96, "PS2 target row dimension mismatch")
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
        checks.check(row.get("weighted_operator_rank") == row.get("domain_column_count") == 108, "probe rank/domain mismatch")
        checks.check(row.get("non_dynamic_row_count") == 96, "probe row count mismatch")
        checks.check(row.get("state_column_count") == 72, "probe state columns mismatch")
        checks.check(row.get("acceleration_column_count") == 36, "probe acceleration columns mismatch")
        checks.check(row.get("weighted_operator_shape") == [132, 108], "probe operator shape mismatch")
        checks.check(finite_positive(row.get("min_singular_value")), "probe singular value invalid")
        checks.check(finite_positive(row.get("condition_number")), "probe condition invalid")
        checks.check(finite_positive(row.get("finite_state_projection_constant")), "probe projection constant invalid")
        checks.check(row.get("gauss_stage_residual_norm", 1.0) < 1.0e-9, "probe stage residual too large")

    checks.check(len(audit_csv) == 3, "CSV probe rows changed")
    csv_h_values = sorted(float(row["h"]) for row in audit_csv)
    checks.check(csv_h_values == [0.01, 0.02, 0.04], "CSV h-values changed")
    for row in audit_csv:
        checks.check(int(row["weighted_operator_rank"]) == int(row["domain_column_count"]) == 108, "CSV rank mismatch")
        checks.check(row["full_column_rank"] == "True", "CSV full-rank marker changed")

    checks.check(
        "uniform PS2 inverse or inf-sup theorem" in boundary.get("forbidden_now", []),
        "claim boundary no longer forbids uniform PS2 theorem",
    )
    for token in [
        "Status: **finite weighted linearization probe recorded; PS2 remains open**.",
        "Full column rank in all finite probes: `True`.",
        "PS2 inverse or inf-sup closed: `False`.",
        "Primitive/Taylor PC2 route closed: `False`.",
        "This is not a uniform compact-tube inverse or inf-sup proof.",
        "P_state, PS2, PC2, and the unconditional D5 theorem remain open.",
    ]:
        checks.check(token in audit_md, f"markdown missing token: {token}")

    if checks.errors:
        print("D5 P_state PS2 linearization probe validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("D5 P_state PS2 linearization probe validation: PASS")
    print("finite_probe_full_column_rank_all=True")
    print("ps2_inverse_or_infsup_closed=False")
    print("pc2_closed=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
