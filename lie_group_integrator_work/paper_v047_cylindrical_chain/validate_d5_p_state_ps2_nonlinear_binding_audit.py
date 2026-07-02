#!/usr/bin/env python3
"""Validate the D5 P_state PS2 nonlinear binding audit."""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
AUDIT_JSON = PAPER / "D5_P_STATE_PS2_NONLINEAR_BINDING_AUDIT.json"
AUDIT_MD = PAPER / "D5_P_STATE_PS2_NONLINEAR_BINDING_AUDIT.md"


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


def finite_positive(value: object) -> bool:
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
        p_tube = read_json(PAPER / "D5_P_TUBE_CONSTANTS_AUDIT.json")
        p_state_map = read_json(PAPER / "D5_P_STATE_MAP_DEFINITION_AUDIT.json")
        ps2_target = read_json(PAPER / "D5_P_STATE_PS2_WEIGHTED_TARGET_AUDIT.json")
        kinematic_block = read_json(PAPER / "D5_P_STATE_PS2_KINEMATIC_BLOCK_CERTIFICATE.json")
        lie_chart = read_json(PAPER / "D5_P_STATE_PS2_LIE_CHART_BINDING_AUDIT.json")
        row_injection = read_json(PAPER / "D5_P_STATE_PS2_ROW_INJECTION_AUDIT.json")
    except Exception as exc:  # noqa: BLE001
        print(f"D5 P_state PS2 nonlinear binding audit validation: FAIL\n- {exc}")
        return 1

    dims = audit.get("dimensions", {})
    constants = audit.get("compact_tube_constants", {})
    statement = audit.get("mean_value_statement", {})
    source = audit.get("source_consistency", {})
    manuscript = audit.get("manuscript_link", {})

    checks.check(audit.get("schema") == "d5-p-state-ps2-nonlinear-binding-audit-v1", "schema changed")
    checks.check(
        audit.get("status") == "ps2_nonlinear_rotational_binding_closed_full_ps2_promotion_open",
        "status changed",
    )
    checks.check(audit.get("read_only") is True, "audit must be read-only")
    checks.check(audit.get("run_v047_invoked") is False, "run_v047 must not be invoked")
    checks.check(audit.get("submission_ready") is False, "submission readiness overclaimed")
    checks.check(audit.get("pc2_closed") is False, "PC2 unexpectedly closed")
    checks.check(audit.get("proof_gap_closed") is False, "proof gap unexpectedly closed")
    checks.check(audit.get("primitive_id") == "P_state_lift", "primitive id changed")
    checks.check(audit.get("primitive_closed") is False, "P_state unexpectedly closed")
    checks.check(audit.get("p_state_ps2_nonlinear_binding_recorded") is True, "binding marker missing")
    checks.check(
        audit.get("certifies_rotational_lie_row_mean_value_binding") is True,
        "rotational mean-value binding not certified",
    )
    checks.check(audit.get("certifies_compact_tube_lipschitz_bound") is True, "Lipschitz bound missing")
    checks.check(audit.get("certifies_small_step_absorption") is True, "small-step absorption missing")
    checks.check(
        audit.get("certifies_full_nonlinear_mean_value_binding") is True,
        "nonlinear mean-value binding not certified",
    )
    checks.check(audit.get("certifies_full_nonlinear_ps2") is False, "full PS2 overclaimed")
    checks.check(audit.get("ps2_inverse_or_infsup_closed") is False, "PS2 unexpectedly closed")
    checks.check(audit.get("certifies_induced_taylor_bounds") is False, "Taylor bounds overclaimed")
    checks.check(audit.get("certifies_dynamic_row_defect") is False, "dynamic defect overclaimed")
    checks.check(dims.get("rotational_lie_collocation_rows") == 18, "rotational row count changed")
    checks.check(dims.get("angular_velocity_collocation_rows") == 18, "angular velocity row count changed")
    checks.check(dims.get("state_rotational_coordinates") == 36, "rotational state dimension changed")
    checks.check(dims.get("angular_acceleration_coordinates") == 18, "angular acceleration dimension changed")
    checks.check(finite_positive(constants.get("chart_radius")), "chart radius missing")
    checks.check(finite_positive(constants.get("gauss_matrix_2_norm")), "Gauss norm missing")
    checks.check(constants.get("right_jacobian_inverse_smooth_on_tube") is True, "Jr inverse smoothness missing")
    checks.check(constants.get("finite_lipschitz_constant_name") == "L_F", "Lipschitz constant name changed")
    checks.check("h ||A_G||_2 L_F <= 1/2" in constants.get("absorption_condition", ""), "absorption condition missing")
    checks.check("J_r(eta_j)^(-1) omega_j" in statement.get("row", ""), "implemented row statement missing")
    checks.check("||Delta F|| <= L_F" in statement.get("difference_bound", ""), "difference bound missing")
    checks.check("||Delta eta|| + ||Delta omega||" in statement.get("absorbed_rotational_bound", ""), "absorbed bound missing")
    checks.check(statement.get("uses_dynamic_rows") is False, "binding must not use dynamic rows")
    checks.check(statement.get("uses_stage_residual_lemma") is False, "binding must not use stage residual lemma")
    checks.check(len(audit.get("remaining_promotion_gaps", [])) == 1, "promotion gap count changed")
    checks.check(
        "aggregate weighted PS2 inverse constant" in audit.get("remaining_promotion_gaps", [""])[0],
        "aggregate promotion gap missing",
    )
    checks.check(source.get("p_tube_schema") == p_tube.get("schema"), "P_tube source link missing")
    checks.check(source.get("p_tube_closed") is True, "P_tube not linked as closed")
    checks.check(source.get("p_tube_pc2_closed") is False, "P_tube unexpectedly closes PC2")
    checks.check(source.get("p_state_map_schema") == p_state_map.get("schema"), "P_state map link missing")
    checks.check(source.get("p_state_map_definition_closed") is True, "P_state map definition not linked")
    checks.check(source.get("ps2_target_schema") == ps2_target.get("schema"), "PS2 target link missing")
    checks.check(source.get("ps2_target_spec_closed") is True, "PS2 target spec not linked")
    checks.check(source.get("ps2_target_infsup_closed") is False, "PS2 target unexpectedly closed")
    checks.check(source.get("kinematic_block_schema") == kinematic_block.get("schema"), "kinematic source link missing")
    checks.check(source.get("kinematic_block_bound_certified") is True, "kinematic bound not linked")
    checks.check(source.get("kinematic_block_full_ps2") is False, "kinematic block unexpectedly closes PS2")
    checks.check(source.get("lie_chart_schema") == lie_chart.get("schema"), "Lie-chart source link missing")
    checks.check(source.get("lie_chart_so3_norm_equivalence") is True, "Lie-chart equivalence not linked")
    checks.check(source.get("lie_chart_full_mean_value_binding") is False, "Lie-chart overclaims mean-value binding")
    checks.check(source.get("row_injection_schema") == row_injection.get("schema"), "row injection source link missing")
    checks.check(source.get("row_injection_certified") is True, "row injection not linked")
    checks.check(source.get("row_injection_unweighted_scaling") is True, "row injection scaling not linked")
    checks.check(source.get("row_injection_full_ps2") is False, "row injection unexpectedly closes PS2")
    checks.check(manuscript.get("main_tex_present") is True, "main TeX lemma missing")
    checks.check(manuscript.get("flat_tex_present") is True, "flat TeX lemma missing")

    for token in [
        "Status: **PS2 nonlinear rotational-row binding closed; aggregate PS2 promotion remains open**.",
        "Nonlinear binding recorded: `True`.",
        "Rotational Lie-row mean-value binding certified: `True`.",
        "Compact-tube Lipschitz bound certified: `True`.",
        "Small-step absorption certified: `True`.",
        "Full nonlinear mean-value binding certified: `True`.",
        "Full nonlinear PS2 certified by this artifact: `False`.",
        "PS2 closed: `False`.",
        "Primitive/Taylor PC2 route closed: `False`.",
        "F(eta, omega) = J_r(eta)^(-1) omega",
        "h ||A_G||_2 L_F <= 1/2",
        "The rotational nonlinear compact-tube mean-value estimate is certified.",
        "It does not by itself promote the aggregate PS2 inverse.",
        "PS3, P_state, PC2, and induced Taylor bounds remain open.",
    ]:
        checks.check(token in audit_md, f"markdown missing token: {token}")

    if checks.errors:
        print("D5 P_state PS2 nonlinear binding audit validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("D5 P_state PS2 nonlinear binding audit validation: PASS")
    print("rotational_mean_value_binding=True")
    print("ps2_closed=False")
    print("pc2_closed=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
