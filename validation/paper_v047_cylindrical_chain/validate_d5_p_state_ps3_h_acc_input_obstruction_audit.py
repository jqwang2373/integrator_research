#!/usr/bin/env python3
"""Validate the D5 P_state PS3 h-acceleration input obstruction audit."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
AUDIT_JSON = PAPER / "D5_P_STATE_PS3_H_ACC_INPUT_OBSTRUCTION_AUDIT.json"
AUDIT_MD = PAPER / "D5_P_STATE_PS3_H_ACC_INPUT_OBSTRUCTION_AUDIT.md"


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
        aggregate = read_json(PAPER / "D5_P_STATE_PS2_AGGREGATE_PROMOTION_AUDIT.json")
        conditional = read_json(PAPER / "D5_P_STATE_PS3_CONDITIONAL_CONVERSION_AUDIT.json")
        ps2_probe = read_json(PAPER / "D5_P_STATE_PS2_LINEARIZATION_PROBE.json")
        kinematic = read_json(PAPER / "KINEMATIC_ROW_DEFECT_CERTIFICATE.json")
        p_acc_obstruction = read_json(PAPER / "D5_P_ACC_LIFT_OBSTRUCTION_AUDIT.json")
        p_acc_weighted = read_json(PAPER / "D5_P_ACC_PA2_WEIGHTED_INVERSE_AUDIT.json")
    except Exception as exc:  # noqa: BLE001
        print(f"D5 P_state PS3 h-acceleration input obstruction audit validation: FAIL\n- {exc}")
        return 1

    summary = audit.get("summary", {})
    dims = audit.get("dimensions", {})
    finite = audit.get("finite_probe_diagnostic", {})
    strict = audit.get("strict_obstruction", {})
    routes = audit.get("non_circular_close_routes", {})
    next_target = audit.get("next_strict_proof_target", {})
    source = audit.get("source_consistency", {})

    checks.check(
        audit.get("schema") == "d5-p-state-ps3-h-acc-input-obstruction-audit-v1",
        "schema changed",
    )
    checks.check(
        audit.get("status") == "h_acc_input_obstruction_recorded_actual_ps3_open",
        "status changed",
    )
    checks.check(audit.get("read_only") is True, "audit must be read-only")
    checks.check(audit.get("run_v047_invoked") is False, "run_v047 must not be invoked")
    checks.check(audit.get("submission_ready") is False, "submission readiness overclaimed")
    checks.check(audit.get("proof_gap_closed") is False, "proof gap unexpectedly closed")
    checks.check(audit.get("pc2_closed") is False, "PC2 unexpectedly closed")
    checks.check(audit.get("primitive_id") == "P_state_lift", "primitive id changed")
    checks.check(audit.get("primitive_closed") is False, "P_state unexpectedly closed")
    checks.check(audit.get("ps3_actual_state_lift_conversion_closed") is False, "actual PS3 unexpectedly closed")
    checks.check(
        audit.get("independent_h_weighted_acceleration_input_closed") is False,
        "h-acceleration input unexpectedly closed",
    )
    checks.check(
        audit.get("non_circular_ps3_instantiation_closed") is False,
        "non-circular PS3 instantiation unexpectedly closed",
    )
    checks.check(audit.get("certifies_induced_taylor_bounds") is False, "Taylor bounds overclaimed")
    checks.check(audit.get("certifies_taylor_bounds") is False, "Taylor certification overclaimed")
    checks.check(audit.get("certifies_p_state") is False, "P_state certification overclaimed")
    checks.check(audit.get("certifies_actual_ps3") is False, "actual PS3 certification overclaimed")
    checks.check(audit.get("finite_probe_is_proof") is False, "finite probe overclaimed as proof")

    checks.check(dims.get("state_block_dimension") == 72, "state dimension changed")
    checks.check(dims.get("auxiliary_acceleration_dimension") == 36, "acceleration dimension changed")
    checks.check(dims.get("domain_dimension") == 108, "domain dimension changed")
    checks.check(dims.get("non_dynamic_row_dimension") == 96, "non-dynamic row dimension changed")
    checks.check(dims.get("weighted_operator_shape") == [132, 108], "weighted operator shape changed")
    checks.check(dims.get("residual_only_row_deficit") == 12, "residual-only row deficit changed")

    checks.check(finite.get("probe_count") == 3, "probe count changed")
    checks.check(finite.get("non_dynamic_jacobian_rank_range") == [96, 96], "non-dynamic rank range changed")
    checks.check(finite.get("weighted_operator_rank_range") == [108, 108], "weighted rank range changed")
    checks.check(finite.get("residual_only_nullity_range") == [12, 12], "residual nullity range changed")
    checks.check(finite.get("non_dynamic_jacobian_ranks") == [96, 96, 96], "non-dynamic ranks changed")
    checks.check(finite.get("weighted_operator_ranks") == [108, 108, 108], "weighted ranks changed")
    checks.check(finite.get("residual_only_nullities") == [12, 12, 12], "residual nullities changed")
    checks.check(finite.get("weighted_operator_full_column_rank_all") is True, "weighted full-rank probe missing")
    checks.check(
        finite.get("h_acceleration_rows_required_by_weighted_operator") is True,
        "h-acceleration row requirement missing",
    )
    checks.check(
        finite.get("residual_only_input_sufficient_for_h_acceleration") is False,
        "residual-only input unexpectedly sufficient",
    )
    checks.check(
        finite.get("theorem_level_independent_h_acceleration_input_proved") is False,
        "theorem-level h-acceleration input unexpectedly proved",
    )

    checks.check(summary.get("h_acceleration_input_obstruction_recorded") is True, "summary obstruction missing")
    checks.check(summary.get("state_block_dimension") == 72, "summary state dimension changed")
    checks.check(summary.get("auxiliary_acceleration_dimension") == 36, "summary acceleration dimension changed")
    checks.check(summary.get("domain_dimension") == 108, "summary domain dimension changed")
    checks.check(summary.get("non_dynamic_row_dimension") == 96, "summary row dimension changed")
    checks.check(summary.get("residual_only_row_deficit") == 12, "summary row deficit changed")
    checks.check(summary.get("finite_probe_nullity_min") == 12, "summary min nullity changed")
    checks.check(summary.get("finite_probe_nullity_max") == 12, "summary max nullity changed")
    checks.check(summary.get("finite_probe_non_dynamic_rank_min") == 96, "summary non-dynamic rank min changed")
    checks.check(summary.get("finite_probe_non_dynamic_rank_max") == 96, "summary non-dynamic rank max changed")
    checks.check(summary.get("finite_probe_weighted_operator_rank_min") == 108, "summary weighted rank min changed")
    checks.check(summary.get("finite_probe_weighted_operator_rank_max") == 108, "summary weighted rank max changed")
    checks.check(summary.get("finite_probe_weighted_operator_full_rank_all") is True, "summary weighted full-rank missing")
    checks.check(summary.get("residual_only_input_sufficient_for_h_acceleration") is False, "summary residual-only overclaimed")
    checks.check(
        summary.get("recommended_non_circular_close_route") == "full_132_row_dynamic_residual_route",
        "summary recommended route changed",
    )
    checks.check(summary.get("full_dynamic_residual_route_closed") is False, "summary dynamic route unexpectedly closed")
    checks.check(summary.get("pc2_required_for_recommended_route") is True, "summary PC2 requirement missing")
    checks.check(summary.get("stronger_velocity_route_closed") is False, "summary stronger-velocity route unexpectedly closed")
    checks.check(summary.get("explicit_assumption_route_available") is True, "summary explicit-assumption route missing")
    checks.check(summary.get("independent_h_weighted_acceleration_input_closed") is False, "summary h-input overclosed")
    checks.check(summary.get("non_circular_ps3_instantiation_closed") is False, "summary PS3 instantiation overclosed")
    checks.check(summary.get("ps3_actual_state_lift_conversion_closed") is False, "summary actual PS3 overclosed")
    checks.check(summary.get("primitive_closed") is False, "summary P_state overclosed")
    checks.check(summary.get("pc2_closed") is False, "summary PC2 overclosed")
    checks.check(summary.get("induced_taylor_bounds_proved") == 0, "summary Taylor bounds overclaimed")

    checks.check("h ||delta A||" in audit.get("claim_boundary", {}).get("close_condition", ""), "close condition missing h input")
    checks.check("delta_V" in strict.get("why_velocity_collocation_is_circular", ""), "circularity reason missing delta_V")
    checks.check(strict.get("velocity_collocation_circular_for_p_state") is True, "velocity collocation circularity missing")
    checks.check("h ||delta A||" in strict.get("ps2_estimate", ""), "PS2 estimate missing h acceleration")
    checks.check(
        routes.get("recommended_route") == "full_132_row_dynamic_residual_route",
        "recommended non-circular close route changed",
    )
    checks.check(
        routes.get("route_R1_full_132_row_dynamic_residual", {}).get("closed") is False,
        "full dynamic residual route unexpectedly closed",
    )
    checks.check(
        routes.get("route_R1_full_132_row_dynamic_residual", {}).get("non_circular_if_completed") is True,
        "full dynamic route non-circular condition missing",
    )
    checks.check(
        "PC2 D5 dynamic-row defect proof for the 36 Newton-Euler rows"
        in routes.get("route_R1_full_132_row_dynamic_residual", {}).get("requires", []),
        "full dynamic route PC2 requirement missing",
    )
    checks.check(
        routes.get("route_R2_stronger_velocity_before_inversion", {}).get("closed") is False,
        "stronger velocity route unexpectedly closed",
    )
    checks.check(
        "delta_V=O(h^8) before velocity-collocation inversion"
        in routes.get("route_R2_stronger_velocity_before_inversion", {}).get("requires", []),
        "stronger velocity route requirement missing",
    )
    checks.check(
        routes.get("route_R3_explicit_theorem_assumption", {}).get("closed") is False,
        "explicit assumption route unexpectedly closed",
    )
    checks.check(
        next_target.get("target") == "PC2 full dynamic-row defect proof or explicit theorem weakening",
        "next strict proof target changed",
    )
    checks.check(
        "promote the finite rank probe to a compact-tube theorem"
        in next_target.get("must_not_do", []),
        "finite probe anti-promotion target missing",
    )

    checks.check(source.get("aggregate_schema") == aggregate.get("schema"), "aggregate source schema missing")
    checks.check(source.get("aggregate_ps2_closed") is True and aggregate.get("ps2_inverse_or_infsup_closed") is True, "aggregate PS2 not linked closed")
    checks.check(source.get("aggregate_primitive_closed") is False and aggregate.get("primitive_closed") is False, "aggregate closes primitive")
    checks.check(source.get("aggregate_pc2_closed") is False and aggregate.get("pc2_closed") is False, "aggregate closes PC2")
    checks.check(source.get("conditional_schema") == conditional.get("schema"), "conditional source schema missing")
    checks.check(source.get("conditional_closed") is True and conditional.get("ps3_conditional_conversion_closed") is True, "conditional PS3 not linked")
    checks.check(source.get("conditional_actual_inputs_closed") is False, "conditional inputs unexpectedly closed")
    checks.check(source.get("conditional_actual_ps3_closed") is False, "conditional actual PS3 unexpectedly closed")
    checks.check(source.get("ps2_probe_schema") == ps2_probe.get("schema"), "probe source schema missing")
    checks.check(source.get("ps2_probe_recorded") is True, "probe not linked recorded")
    checks.check(source.get("ps2_probe_uniform_constant_proved") is False, "probe overclaimed uniform proof")
    checks.check(source.get("ps2_probe_pc2_closed") is False, "probe unexpectedly closes PC2")
    checks.check(source.get("kinematic_schema") == kinematic.get("schema"), "kinematic source schema missing")
    checks.check(source.get("kinematic_certified_rows") == 96, "kinematic row count changed")
    checks.check(source.get("kinematic_excluded_rows") == 36, "kinematic excluded row count changed")
    checks.check(source.get("p_acc_obstruction_schema") == p_acc_obstruction.get("schema"), "P_acc obstruction schema missing")
    checks.check(source.get("p_acc_pa2_closed") is False and p_acc_obstruction.get("pa2_closed") is False, "PA2 unexpectedly closed")
    checks.check(source.get("p_acc_velocity_collocation_alone_sufficient") is False, "velocity collocation unexpectedly sufficient")
    checks.check(source.get("p_acc_pc2_closed") is False and p_acc_obstruction.get("pc2_closed") is False, "P_acc unexpectedly closes PC2")
    checks.check(source.get("p_acc_weighted_schema") == p_acc_weighted.get("schema"), "P_acc weighted source schema missing")
    checks.check(source.get("p_acc_weighted_h_control_recorded") is True, "weighted h diagnostic missing")
    checks.check(source.get("p_acc_weighted_unweighted_uniform_control_proved") is False, "unweighted uniform control overclaimed")

    for token in [
        "Status: **h-weighted acceleration input obstruction recorded; actual PS3 remains open**.",
        "Residual-only row deficit: `12`.",
        "Residual-only finite nullity range: `12`-`12`.",
        "Non-dynamic finite rank range: `96`-`96`.",
        "Weighted operator finite rank range: `108`-`108`.",
        "Residual-only input sufficient for h-acceleration: `False`.",
        "Independent h-weighted acceleration input closed: `False`.",
        "Actual PS3 state lift conversion closed: `False`.",
        "P_state primitive closed: `False`.",
        "Induced Taylor bounds proved: `0/162`.",
        "Primitive/Taylor PC2 route closed: `False`.",
        "`||delta S|| <= C_PS2 (||delta N_h^nd|| + h ||delta A||)`.",
        "`delta_A = h^{-1} (A_G^{-1} \\otimes I) (delta_V - rho_V)`.",
        "The finite rank probe is diagnostic evidence, not a proof.",
        "The recommended non-circular close route is the full 132-row dynamic",
        "prove the D5 lifted-stage dynamic defect for the 36",
        "`delta_V=O(h^8)` and `rho_V=O(h^8)` before the `A_G^{-1}/h` inversion",
        "explicit assumption",
        "Actual PS3 remains open.",
    ]:
        checks.check(token in audit_md, f"markdown missing token: {token}")

    if checks.errors:
        print("D5 P_state PS3 h-acceleration input obstruction audit validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("D5 P_state PS3 h-acceleration input obstruction audit validation: PASS")
    print("residual_only_row_deficit=12")
    print("finite_probe_nullity_range=12-12")
    print("independent_h_weighted_acceleration_input_closed=False")
    print("ps3_actual_state_lift_conversion_closed=False")
    print("pc2_closed=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
