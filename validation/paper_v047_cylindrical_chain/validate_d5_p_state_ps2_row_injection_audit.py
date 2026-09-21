#!/usr/bin/env python3
"""Validate the D5 P_state PS2 row-injection audit."""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
AUDIT_JSON = PAPER / "D5_P_STATE_PS2_ROW_INJECTION_AUDIT.json"
AUDIT_MD = PAPER / "D5_P_STATE_PS2_ROW_INJECTION_AUDIT.md"


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


def main() -> int:
    checks = Checks()
    try:
        audit = read_json(AUDIT_JSON)
        audit_md = AUDIT_MD.read_text(encoding="utf-8", errors="replace")
        p_state_map = read_json(PAPER / "D5_P_STATE_MAP_DEFINITION_AUDIT.json")
        ps2_target = read_json(PAPER / "D5_P_STATE_PS2_WEIGHTED_TARGET_AUDIT.json")
        kinematic_block = read_json(PAPER / "D5_P_STATE_PS2_KINEMATIC_BLOCK_CERTIFICATE.json")
        lie_chart = read_json(PAPER / "D5_P_STATE_PS2_LIE_CHART_BINDING_AUDIT.json")
        p_state_gap = read_json(PAPER / "D5_P_STATE_LIFT_GAP_AUDIT.json")
    except Exception as exc:  # noqa: BLE001
        print(f"D5 P_state PS2 row-injection audit validation: FAIL\n- {exc}")
        return 1

    dims = audit.get("dimensions", {})
    source = audit.get("source_consistency", {})
    manuscript = audit.get("manuscript_link", {})

    checks.check(audit.get("schema") == "d5-p-state-ps2-row-injection-audit-v1", "schema changed")
    checks.check(audit.get("status") == "ps2_row_injection_recorded_full_ps2_open", "status changed")
    checks.check(audit.get("read_only") is True, "audit must be read-only")
    checks.check(audit.get("run_v047_invoked") is False, "run_v047 must not be invoked")
    checks.check(audit.get("submission_ready") is False, "submission readiness overclaimed")
    checks.check(audit.get("pc2_closed") is False, "PC2 unexpectedly closed")
    checks.check(audit.get("proof_gap_closed") is False, "proof gap unexpectedly closed")
    checks.check(audit.get("primitive_id") == "P_state_lift", "primitive id changed")
    checks.check(audit.get("primitive_closed") is False, "P_state unexpectedly closed")
    checks.check(audit.get("p_state_ps2_row_injection_recorded") is True, "row injection marker missing")
    checks.check(audit.get("certifies_72_to_96_row_injection") is True, "72-to-96 row injection not certified")
    checks.check(audit.get("certifies_unweighted_residual_scaling") is True, "unweighted scaling not certified")
    checks.check(close_to(audit.get("row_selection_operator_2_norm"), 1.0), "row selector norm changed")
    checks.check(audit.get("certifies_full_nonlinear_mean_value_binding") is False, "mean-value binding overclaimed")
    checks.check(audit.get("certifies_full_nonlinear_ps2") is False, "full nonlinear PS2 overclaimed")
    checks.check(audit.get("ps2_inverse_or_infsup_closed") is False, "PS2 unexpectedly closed")
    checks.check(audit.get("certifies_induced_taylor_bounds") is False, "Taylor bounds overclaimed")
    checks.check(audit.get("certifies_dynamic_row_defect") is False, "dynamic defect overclaimed")
    checks.check(dims.get("kinematic_row_dimension") == 72, "kinematic row count changed")
    checks.check(dims.get("lower_pair_surplus_rows") == 24, "lower-pair row count changed")
    checks.check(dims.get("non_dynamic_row_dimension") == 96, "non-dynamic row count changed")
    checks.check(len(dims.get("row_order", [])) == 5, "row order inventory changed")
    checks.check(len(audit.get("remaining_binding_gaps", [])) == 1, "remaining binding gap count changed")
    checks.check(
        "nonlinear compact-tube mean-value estimate" in audit.get("remaining_binding_gaps", [""])[0],
        "nonlinear mean-value gap missing",
    )
    checks.check(source.get("p_state_map_schema") == p_state_map.get("schema"), "P_state map source link missing")
    checks.check(source.get("p_state_map_definition_closed") is True, "P_state map definition not linked")
    checks.check(source.get("ps2_target_schema") == ps2_target.get("schema"), "PS2 target source link missing")
    checks.check(source.get("ps2_target_spec_closed") is True, "PS2 target spec not linked")
    checks.check(source.get("ps2_target_infsup_closed") is False, "PS2 target unexpectedly closed")
    checks.check(source.get("kinematic_block_schema") == kinematic_block.get("schema"), "kinematic block source link missing")
    checks.check(source.get("kinematic_block_bound_certified") is True, "kinematic block bound not linked")
    checks.check(source.get("kinematic_block_full_ps2") is False, "kinematic block unexpectedly closes PS2")
    checks.check(source.get("lie_chart_schema") == lie_chart.get("schema"), "Lie-chart source link missing")
    checks.check(source.get("lie_chart_so3_norm_equivalence") is True, "Lie-chart equivalence not linked")
    checks.check(source.get("lie_chart_full_mean_value_binding") is False, "Lie-chart unexpectedly closes mean-value")
    checks.check(source.get("p_state_gap_schema") == p_state_gap.get("schema"), "P_state gap source link missing")
    checks.check(source.get("p_state_gap_closed") is False, "P_state gap unexpectedly closed")
    checks.check(manuscript.get("main_tex_present") is True, "main TeX lemma missing")
    checks.check(manuscript.get("flat_tex_present") is True, "flat TeX lemma missing")

    for token in [
        "Status: **PS2 row injection recorded; full PS2 remains open**.",
        "Row injection recorded: `True`.",
        "72-to-96 row injection certified: `True`.",
        "Unweighted residual scaling certified: `True`.",
        "Row-selection operator 2-norm: `1.000000000000e+00`.",
        "Kinematic/lower-pair/non-dynamic rows: `72` / `24` / `96`.",
        "Full nonlinear mean-value binding certified: `False`.",
        "Full nonlinear PS2 certified: `False`.",
        "PS2 closed: `False`.",
        "Primitive/Taylor PC2 route closed: `False`.",
        "||Pi_kin delta N_h^nd||_2 <= ||delta N_h^nd||_2",
        "The 72-to-96 unweighted row injection is recorded.",
        "Nonlinear rotational-row mean-value binding remains open.",
        "PS2, PS3, P_state, PC2, and induced Taylor bounds remain open.",
    ]:
        checks.check(token in audit_md, f"markdown missing token: {token}")

    if checks.errors:
        print("D5 P_state PS2 row-injection audit validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("D5 P_state PS2 row-injection audit validation: PASS")
    print("row_selection_operator_2_norm=1.000000000000e+00")
    print("ps2_closed=False")
    print("pc2_closed=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
