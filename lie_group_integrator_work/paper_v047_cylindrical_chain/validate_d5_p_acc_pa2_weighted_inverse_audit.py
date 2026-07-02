#!/usr/bin/env python3
"""Validate the D5 P_acc PA2 weighted-inverse audit."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
AUDIT_JSON = PAPER / "D5_P_ACC_PA2_WEIGHTED_INVERSE_AUDIT.json"
AUDIT_MD = PAPER / "D5_P_ACC_PA2_WEIGHTED_INVERSE_AUDIT.md"


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
        audit = read_json(AUDIT_JSON)
        audit_md = AUDIT_MD.read_text(encoding="utf-8", errors="replace")
        ps2_probe = read_json(PAPER / "D5_P_STATE_PS2_LINEARIZATION_PROBE.json")
        p_acc_lift_obstruction = read_json(PAPER / "D5_P_ACC_LIFT_OBSTRUCTION_AUDIT.json")
        p_acc_independence = read_json(PAPER / "D5_P_ACC_INDEPENDENCE_AUDIT.json")
        p_acc_row_binding = read_json(PAPER / "D5_P_ACC_ROW_BINDING_AUDIT.json")
        proof_manifest = read_json(PAPER / "PROOF_CLOSURE_MANIFEST.json")
    except Exception as exc:  # noqa: BLE001
        print(f"D5 P_acc PA2 weighted-inverse audit validation: FAIL\n- {exc}")
        return 1

    summary = audit.get("summary", {})
    source = audit.get("source_consistency", {})
    claim = audit.get("claim_boundary", {})
    rows = audit.get("probes", [])

    checks.check(audit.get("schema") == "d5-p-acc-pa2-weighted-inverse-audit-v1", "schema changed")
    checks.check(
        audit.get("status") == "pa2_weighted_inverse_diagnostic_recorded_unweighted_lift_open",
        "status changed",
    )
    checks.check(audit.get("read_only") is True, "audit must be read-only")
    checks.check(audit.get("run_v047_invoked") is False, "run_v047 must not be invoked")
    checks.check(audit.get("one_step_stage_newton_invoked") is True, "finite stage probe not recorded")
    checks.check(audit.get("submission_ready") is False, "submission readiness overclaimed")
    checks.check(audit.get("pc2_closed") is False, "PC2 unexpectedly closed")
    checks.check(audit.get("proof_gap_closed") is False, "proof gap unexpectedly closed")
    checks.check(audit.get("primitive_closed") is False, "P_acc unexpectedly closed")
    checks.check(audit.get("pa2_closed") is False, "PA2 unexpectedly closed")
    checks.check(audit.get("pa2_weighted_inverse_probe_recorded") is True, "PA2 weighted probe not recorded")
    checks.check(
        audit.get("weighted_h_acceleration_control_recorded") is True,
        "weighted h-acceleration diagnostic missing",
    )
    checks.check(
        audit.get("unweighted_acceleration_uniform_control_proved") is False,
        "unweighted acceleration uniform proof overclaimed",
    )
    checks.check(audit.get("acceleration_lift_rate_proved") is False, "acceleration lift overclaimed")
    checks.check(audit.get("term_bounds_proved") == 0, "Taylor bounds unexpectedly proved")
    checks.check(audit.get("h_values") == [0.04, 0.02, 0.01], "h-values changed")

    checks.check(summary.get("probe_count") == 3, "probe count changed")
    checks.check(summary.get("state_block_dimension") == 72, "state dimension changed")
    checks.check(summary.get("acceleration_block_dimension") == 36, "acceleration dimension changed")
    checks.check(summary.get("domain_dimension") == 108, "domain dimension changed")
    checks.check(summary.get("non_dynamic_row_dimension") == 96, "non-dynamic row dimension changed")
    checks.check(summary.get("weighted_operator_shape") == [132, 108], "weighted operator shape changed")
    checks.check(summary.get("finite_probe_full_column_rank_all") is True, "finite full-rank diagnostic missing")
    checks.check(summary.get("min_weighted_operator_rank") == 108, "min weighted rank changed")
    checks.check(summary.get("max_weighted_operator_rank") == 108, "max weighted rank changed")
    for key in [
        "min_singular_value_across_probes",
        "max_state_projection_constant",
        "max_unweighted_acceleration_projection_constant",
        "max_weighted_h_acceleration_projection_constant",
    ]:
        checks.check(float(summary.get(key, 0.0)) > 0.0, f"{key} is not positive")
    checks.check(summary.get("weighted_h_acceleration_control_recorded") is True, "summary weighted control missing")
    checks.check(
        summary.get("unweighted_acceleration_uniform_control_proved") is False,
        "summary overclaims unweighted acceleration control",
    )
    checks.check(summary.get("pa2_closed") is False, "summary overclaims PA2")
    checks.check(summary.get("pc2_closed") is False, "summary overclaims PC2")

    checks.check(isinstance(rows, list) and len(rows) == 3, "probe rows missing")
    for row in rows:
        if not isinstance(row, dict):
            checks.check(False, "probe row is not an object")
            continue
        checks.check(row.get("case") == "cylindrical_smooth", "case changed")
        checks.check(row.get("h") in [0.04, 0.02, 0.01], "probe h changed")
        checks.check(row.get("full_column_rank") is True, "probe not full column rank")
        checks.check(row.get("weighted_operator_rank") == 108, "probe rank changed")
        for key in [
            "min_singular_value",
            "state_projection_constant",
            "unweighted_acceleration_projection_constant",
            "weighted_h_acceleration_projection_constant",
            "h_times_unweighted_acceleration_projection_constant",
        ]:
            checks.check(float(row.get(key, 0.0)) > 0.0, f"probe {key} is not positive")

    checks.check(source.get("ps2_probe_schema") == ps2_probe.get("schema"), "PS2 probe schema link missing")
    checks.check(
        source.get("ps2_probe_full_column_rank_all") is True
        and ps2_probe.get("summary", {}).get("finite_probe_full_column_rank_all") is True,
        "PS2 finite full-rank link missing",
    )
    checks.check(
        source.get("ps2_probe_uniform_constant_proved") is False
        and ps2_probe.get("uniform_constant_proved") is False,
        "PS2 probe unexpectedly proves uniform constant",
    )
    checks.check(
        source.get("p_acc_lift_obstruction_schema") == p_acc_lift_obstruction.get("schema"),
        "P_acc obstruction schema link missing",
    )
    checks.check(
        source.get("p_acc_lift_obstruction_recorded") is True
        and p_acc_lift_obstruction.get("pa2_obstruction_recorded") is True,
        "P_acc obstruction link missing",
    )
    checks.check(
        source.get("p_acc_lift_obstruction_pa2_closed") is False
        and p_acc_lift_obstruction.get("pa2_closed") is False,
        "P_acc obstruction unexpectedly closes PA2",
    )
    checks.check(
        source.get("p_acc_independence_closed") is True
        and p_acc_independence.get("pa3_independence_closed") is True,
        "P_acc independence link missing",
    )
    checks.check(
        source.get("p_acc_independence_primitive_closed") is False
        and p_acc_independence.get("primitive_closed") is False,
        "P_acc independence unexpectedly closes primitive",
    )
    checks.check(
        source.get("p_acc_row_binding_closed") is True
        and p_acc_row_binding.get("pa4_row_binding_closed") is True,
        "P_acc row binding link missing",
    )
    checks.check(source.get("proof_manifest_pc2_closed") is True, "proof manifest direct PC2 closure not reflected")
    checks.check(
        source.get("proof_manifest_proof_gap_closed") is True
        and proof_manifest.get("closure_state", {}).get("pc2_closed_by_direct_substitution") is True,
        "proof manifest direct-substitution closure not reflected",
    )
    checks.check(
        proof_manifest.get("closure_state", {}).get("primitive_lift_route_closed") is False,
        "proof manifest unexpectedly closes primitive lift route",
    )
    checks.check(audit.get("manuscript_link", {}).get("main_tex_present") is True, "main TeX link missing")
    checks.check(audit.get("manuscript_link", {}).get("flat_tex_present") is True, "flat TeX link missing")

    for forbidden in [
        "PA2 closure",
        "P_acc primitive closure",
        "uniform unweighted acceleration lift proof",
        "Taylor term bounds certified from P_acc",
        "primitive/Taylor PC2 route closure",
        "unconditional sixth-order theorem",
    ]:
        checks.check(forbidden in claim.get("forbidden_now", []), f"forbidden claim missing: {forbidden}")

    for token in [
        "Status: **PA2 weighted-inverse diagnostic recorded; unweighted lift remains open**.",
        "Probe count: `3`.",
        "Weighted operator full column rank in all probes: `True`.",
        "Weighted h-acceleration control recorded: `True`.",
        "Unweighted acceleration uniform control proved: `False`.",
        "PA2 closed: `False`.",
        "P_acc primitive closed: `False`.",
        "Primitive/Taylor PC2 route closed: `False`.",
        "The finite weighted operator supports bounded finite control of `h delta A`.",
        "The audit does not prove a uniform unweighted acceleration lift.",
        "PA2 remains open.",
        "`P_acc` remains open.",
    ]:
        checks.check(token in audit_md, f"markdown missing token: {token}")

    if checks.errors:
        print("D5 P_acc PA2 weighted-inverse audit validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("D5 P_acc PA2 weighted-inverse audit validation: PASS")
    print("probe_count=3")
    print("weighted_h_acceleration_control_recorded=True")
    print("unweighted_acceleration_uniform_control_proved=False")
    print("pa2_closed=False")
    print("pc2_closed=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
