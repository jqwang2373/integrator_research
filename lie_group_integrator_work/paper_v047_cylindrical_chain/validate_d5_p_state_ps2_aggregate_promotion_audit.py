#!/usr/bin/env python3
"""Validate the D5 P_state PS2 aggregate-promotion audit."""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
AUDIT_JSON = PAPER / "D5_P_STATE_PS2_AGGREGATE_PROMOTION_AUDIT.json"
AUDIT_MD = PAPER / "D5_P_STATE_PS2_AGGREGATE_PROMOTION_AUDIT.md"


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
        target = read_json(PAPER / "D5_P_STATE_PS2_WEIGHTED_TARGET_AUDIT.json")
        kinematic = read_json(PAPER / "D5_P_STATE_PS2_KINEMATIC_BLOCK_CERTIFICATE.json")
        lie_chart = read_json(PAPER / "D5_P_STATE_PS2_LIE_CHART_BINDING_AUDIT.json")
        row_injection = read_json(PAPER / "D5_P_STATE_PS2_ROW_INJECTION_AUDIT.json")
        nonlinear = read_json(PAPER / "D5_P_STATE_PS2_NONLINEAR_BINDING_AUDIT.json")
        probe = read_json(PAPER / "D5_P_STATE_PS2_LINEARIZATION_PROBE.json")
    except Exception as exc:  # noqa: BLE001
        print(f"D5 P_state PS2 aggregate-promotion audit validation: FAIL\n- {exc}")
        return 1

    dims = audit.get("dimensions", {})
    components = audit.get("component_certificates", {})
    estimate = audit.get("aggregate_estimate", {})
    source = audit.get("source_consistency", {})
    manuscript = audit.get("manuscript_link", {})

    checks.check(audit.get("schema") == "d5-p-state-ps2-aggregate-promotion-audit-v1", "schema changed")
    checks.check(
        audit.get("status") == "ps2_aggregate_weighted_inverse_closed_pstate_open",
        "status changed",
    )
    checks.check(audit.get("read_only") is True, "audit must be read-only")
    checks.check(audit.get("run_v047_invoked") is False, "run_v047 must not be invoked")
    checks.check(audit.get("submission_ready") is False, "submission readiness overclaimed")
    checks.check(audit.get("pc2_closed") is False, "PC2 unexpectedly closed")
    checks.check(audit.get("proof_gap_closed") is False, "proof gap unexpectedly closed")
    checks.check(audit.get("primitive_id") == "P_state_lift", "primitive id changed")
    checks.check(audit.get("primitive_closed") is False, "P_state unexpectedly closed")
    checks.check(audit.get("p_state_ps2_aggregate_promotion_recorded") is True, "aggregate marker missing")
    checks.check(
        audit.get("certifies_aggregate_weighted_ps2_inverse") is True,
        "aggregate weighted PS2 inverse not certified",
    )
    checks.check(audit.get("certifies_uniform_ps2_constant") is True, "uniform PS2 constant not certified")
    checks.check(audit.get("ps2_inverse_or_infsup_closed") is True, "PS2 not closed")
    checks.check(audit.get("ps3_actual_state_lift_conversion_closed") is False, "PS3 unexpectedly closed")
    checks.check(audit.get("state_lift_rate_proved") is False, "state lift unexpectedly proved")
    checks.check(audit.get("certifies_induced_taylor_bounds") is False, "Taylor bounds overclaimed")
    checks.check(audit.get("certifies_dynamic_row_defect") is False, "dynamic defect overclaimed")
    checks.check(dims.get("state_block_dimension") == 72, "state dimension changed")
    checks.check(dims.get("auxiliary_acceleration_dimension") == 36, "acceleration dimension changed")
    checks.check(dims.get("non_dynamic_row_dimension") == 96, "non-dynamic row dimension changed")
    checks.check(dims.get("kinematic_row_dimension") == 72, "kinematic row dimension changed")
    checks.check(dims.get("lower_pair_surplus_rows") == 24, "lower-pair surplus row count changed")
    checks.check(components.get("weighted_target_spec_closed") is True, "weighted target component missing")
    checks.check(components.get("kinematic_subblock_bound_certified") is True, "kinematic component missing")
    checks.check(components.get("so3_chart_norm_equivalence_certified") is True, "SO(3) component missing")
    checks.check(components.get("row_injection_certified") is True, "row injection component missing")
    checks.check(close_to(components.get("row_injection_selector_norm"), 1.0), "selector norm changed")
    checks.check(
        components.get("nonlinear_rotational_mean_value_certified") is True,
        "nonlinear rotational component missing",
    )
    checks.check(components.get("nonlinear_full_mean_value_certified") is True, "nonlinear component missing")
    checks.check(components.get("finite_probe_full_column_rank_all") is True, "finite probe rank not carried")
    checks.check(components.get("finite_probe_used_as_theorem_input") is False, "finite probe used as theorem input")
    checks.check(
        estimate.get("statement") == "||delta S|| <= C_PS2 (||delta N_h^nd|| + h ||delta A||)",
        "aggregate estimate statement changed",
    )
    checks.check(estimate.get("constant_type") == "uniform compact-tube constant after shrinking h0", "constant type changed")
    checks.check(estimate.get("constant_name") == "C_PS2", "constant name changed")
    checks.check(close_to(estimate.get("selector_norm"), 1.0), "estimate selector norm changed")
    checks.check("h ||A_G||_2 L_F <= 1/2" in estimate.get("rotational_absorption_condition", ""), "absorption condition missing")
    checks.check(len(audit.get("proof_route", [])) == 6, "proof route inventory changed")
    checks.check(source.get("target_schema") == target.get("schema"), "target source link missing")
    checks.check(source.get("target_spec_closed") is True, "target spec not linked")
    checks.check(source.get("target_infsup_closed_before_promotion") is False, "target audit unexpectedly closes PS2")
    checks.check(source.get("kinematic_schema") == kinematic.get("schema"), "kinematic source link missing")
    checks.check(source.get("kinematic_subblock_bound") is True, "kinematic bound not linked")
    checks.check(source.get("kinematic_full_ps2") is False, "kinematic component overclaims PS2")
    checks.check(source.get("lie_chart_schema") == lie_chart.get("schema"), "Lie-chart source link missing")
    checks.check(source.get("lie_chart_so3_norm_equivalence") is True, "Lie-chart equivalence not linked")
    checks.check(source.get("lie_chart_full_ps2") is False, "Lie-chart component overclaims PS2")
    checks.check(source.get("row_injection_schema") == row_injection.get("schema"), "row injection source link missing")
    checks.check(source.get("row_injection_certified") is True, "row injection not linked")
    checks.check(source.get("row_injection_scaling") is True, "row injection scaling not linked")
    checks.check(source.get("row_injection_full_ps2") is False, "row injection component overclaims PS2")
    checks.check(source.get("nonlinear_schema") == nonlinear.get("schema"), "nonlinear source link missing")
    checks.check(source.get("nonlinear_binding_recorded") is True, "nonlinear binding not linked")
    checks.check(source.get("nonlinear_full_mean_value_binding") is True, "nonlinear mean-value not linked")
    checks.check(source.get("nonlinear_full_ps2") is False, "nonlinear component overclaims full PS2")
    checks.check(source.get("probe_schema") == probe.get("schema"), "probe source link missing")
    checks.check(source.get("probe_full_column_rank_all") is True, "probe rank not linked")
    checks.check(source.get("probe_uniform_constant_proved") is False, "probe unexpectedly proves uniform constant")
    checks.check(manuscript.get("main_tex_present") is True, "main TeX lemma missing")
    checks.check(manuscript.get("flat_tex_present") is True, "flat TeX lemma missing")

    for token in [
        "Status: **aggregate weighted PS2 inverse closed; P_state remains open**.",
        "Aggregate promotion recorded: `True`.",
        "Aggregate weighted PS2 inverse certified: `True`.",
        "Uniform PS2 constant certified: `True`.",
        "PS2 inverse or inf-sup closed: `True`.",
        "Actual PS3 state lift conversion closed: `False`.",
        "P_state primitive closed: `False`.",
        "Primitive/Taylor PC2 route closed: `False`.",
        "||delta S|| <= C_PS2 (||delta N_h^nd|| + h ||delta A||)",
        "The uniform weighted PS2 inverse is closed.",
        "The finite linearization probe remains diagnostic, not a theorem input.",
        "This audit does not instantiate PS3.",
        "P_state, PC2, and induced Taylor bounds remain open.",
    ]:
        checks.check(token in audit_md, f"markdown missing token: {token}")

    if checks.errors:
        print("D5 P_state PS2 aggregate-promotion audit validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("D5 P_state PS2 aggregate-promotion audit validation: PASS")
    print("ps2_inverse_or_infsup_closed=True")
    print("p_state_closed=False")
    print("pc2_closed=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
