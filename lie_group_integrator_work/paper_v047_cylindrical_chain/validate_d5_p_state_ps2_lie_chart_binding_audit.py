#!/usr/bin/env python3
"""Validate the D5 P_state PS2 Lie-chart binding audit."""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
AUDIT_JSON = PAPER / "D5_P_STATE_PS2_LIE_CHART_BINDING_AUDIT.json"
AUDIT_MD = PAPER / "D5_P_STATE_PS2_LIE_CHART_BINDING_AUDIT.md"


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


def close_to(value: object, expected: float, tol: float = 1.0e-12) -> bool:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return False
    return math.isfinite(number) and abs(number - expected) <= tol


def expected_jr_inv_bound(theta: float) -> float:
    return theta / (2.0 * math.sin(0.5 * theta))


def main() -> int:
    checks = Checks()
    try:
        audit = read_json(AUDIT_JSON)
        audit_md = AUDIT_MD.read_text(encoding="utf-8", errors="replace")
        p_tube = read_json(PAPER / "D5_P_TUBE_CONSTANTS_AUDIT.json")
        ps2_target = read_json(PAPER / "D5_P_STATE_PS2_WEIGHTED_TARGET_AUDIT.json")
        p_state_map = read_json(PAPER / "D5_P_STATE_MAP_DEFINITION_AUDIT.json")
        p_state_gap = read_json(PAPER / "D5_P_STATE_LIFT_GAP_AUDIT.json")
    except Exception as exc:  # noqa: BLE001
        print(f"D5 P_state PS2 Lie-chart binding audit validation: FAIL\n- {exc}")
        return 1

    constants = audit.get("constants", {})
    dims = audit.get("dimensions", {})
    source = audit.get("source_consistency", {})
    manuscript = audit.get("manuscript_link", {})
    theta = 0.5
    jr_inv = expected_jr_inv_bound(theta)

    checks.check(audit.get("schema") == "d5-p-state-ps2-lie-chart-binding-audit-v1", "schema changed")
    checks.check(
        audit.get("status") == "ps2_lie_chart_binding_recorded_full_ps2_open",
        "status changed",
    )
    checks.check(audit.get("read_only") is True, "audit must be read-only")
    checks.check(audit.get("run_v047_invoked") is False, "run_v047 must not be invoked")
    checks.check(audit.get("submission_ready") is False, "submission readiness overclaimed")
    checks.check(audit.get("pc2_closed") is False, "PC2 unexpectedly closed")
    checks.check(audit.get("proof_gap_closed") is False, "proof gap unexpectedly closed")
    checks.check(audit.get("primitive_id") == "P_state_lift", "primitive id changed")
    checks.check(audit.get("primitive_closed") is False, "P_state unexpectedly closed")
    checks.check(
        audit.get("p_state_ps2_lie_chart_binding_recorded") is True,
        "Lie-chart binding marker missing",
    )
    checks.check(
        audit.get("certifies_so3_chart_norm_equivalence") is True,
        "SO(3) chart norm-equivalence not certified",
    )
    checks.check(
        audit.get("certifies_rotational_chart_binding_constant") is True,
        "rotational chart binding constant missing",
    )
    checks.check(
        audit.get("certifies_full_nonlinear_mean_value_binding") is False,
        "nonlinear mean-value binding overclaimed",
    )
    checks.check(
        audit.get("certifies_full_row_injection_scaling") is False,
        "full row injection/scaling overclaimed",
    )
    checks.check(audit.get("certifies_full_nonlinear_ps2") is False, "full nonlinear PS2 overclaimed")
    checks.check(audit.get("ps2_inverse_or_infsup_closed") is False, "PS2 unexpectedly closed")
    checks.check(audit.get("certifies_induced_taylor_bounds") is False, "Taylor bounds overclaimed")
    checks.check(audit.get("certifies_dynamic_row_defect") is False, "dynamic defect overclaimed")
    checks.check(close_to(constants.get("chart_radius_rad"), theta), "chart radius changed")
    checks.check(close_to(constants.get("right_jacobian_2_norm_bound"), 1.0), "J_r bound changed")
    checks.check(
        close_to(constants.get("right_jacobian_inverse_2_norm_bound"), jr_inv),
        "J_r inverse bound changed",
    )
    checks.check(close_to(constants.get("chart_equivalence_factor"), jr_inv), "chart factor changed")
    checks.check(dims.get("rotational_chart_rows") == 18, "rotational chart row count changed")
    checks.check(dims.get("angular_velocity_rows") == 18, "angular velocity row count changed")
    checks.check(dims.get("rotational_kinematic_rows") == 36, "rotational kinematic row count changed")
    checks.check(len(audit.get("remaining_binding_gaps", [])) == 2, "remaining binding gap count changed")
    checks.check(
        "nonlinear compact-tube mean-value estimate" in audit.get("remaining_binding_gaps", [""])[0],
        "nonlinear mean-value gap missing",
    )
    checks.check(
        "72 kinematic rows into the 96-row" in audit.get("remaining_binding_gaps", ["", ""])[1],
        "72-to-96 row injection gap missing",
    )
    checks.check(source.get("p_tube_schema") == p_tube.get("schema"), "P_tube source link missing")
    checks.check(source.get("p_tube_closed") is True and p_tube.get("primitive_closed") is True, "P_tube not closed")
    checks.check(source.get("p_tube_pc2_closed") is False and p_tube.get("pc2_closed") is False, "P_tube closes PC2")
    checks.check(source.get("ps2_target_schema") == ps2_target.get("schema"), "PS2 target source link missing")
    checks.check(source.get("ps2_target_spec_closed") is True, "PS2 target spec not linked")
    checks.check(source.get("ps2_target_infsup_closed") is False, "PS2 target unexpectedly closed")
    checks.check(source.get("p_state_map_schema") == p_state_map.get("schema"), "P_state map source link missing")
    checks.check(source.get("p_state_map_definition_closed") is True, "P_state map definition not linked")
    checks.check(source.get("p_state_gap_schema") == p_state_gap.get("schema"), "P_state gap source link missing")
    checks.check(source.get("p_state_gap_closed") is False, "P_state gap unexpectedly closed")
    checks.check(manuscript.get("main_tex_present") is True, "main TeX lemma missing")
    checks.check(manuscript.get("flat_tex_present") is True, "flat TeX lemma missing")

    for token in [
        "Status: **PS2 Lie-chart binding recorded; full PS2 remains open**.",
        "Lie-chart binding recorded: `True`.",
        "SO(3) chart norm-equivalence certified: `True`.",
        "Full nonlinear mean-value binding certified: `False`.",
        "Full row injection/scaling certified: `False`.",
        "Full nonlinear PS2 certified: `False`.",
        "Chart radius: `0.5` rad.",
        "Rotational kinematic rows: `36`.",
        "PS2 closed: `False`.",
        "Primitive/Taylor PC2 route closed: `False`.",
        "Pure SO(3) chart norm-equivalence is recorded.",
        "Nonlinear rotational-row mean-value binding remains open.",
        "72-to-96 residual row injection/scaling remains open.",
        "PS2, PS3, P_state, PC2, and induced Taylor bounds remain open.",
    ]:
        checks.check(token in audit_md, f"markdown missing token: {token}")

    if checks.errors:
        print("D5 P_state PS2 Lie-chart binding audit validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("D5 P_state PS2 Lie-chart binding audit validation: PASS")
    print(f"chart_equivalence_factor={constants.get('chart_equivalence_factor'):.12e}")
    print("ps2_closed=False")
    print("pc2_closed=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
