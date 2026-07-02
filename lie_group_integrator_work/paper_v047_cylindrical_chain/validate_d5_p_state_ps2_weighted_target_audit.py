#!/usr/bin/env python3
"""Validate the D5 P_state PS2 weighted target audit."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
AUDIT_JSON = PAPER / "D5_P_STATE_PS2_WEIGHTED_TARGET_AUDIT.json"
AUDIT_MD = PAPER / "D5_P_STATE_PS2_WEIGHTED_TARGET_AUDIT.md"


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
        p_state_map = read_json(PAPER / "D5_P_STATE_MAP_DEFINITION_AUDIT.json")
        p_state_anti = read_json(PAPER / "D5_P_STATE_ANTICIRCULARITY_AUDIT.json")
        p_acc_obstruction = read_json(PAPER / "D5_P_ACC_LIFT_OBSTRUCTION_AUDIT.json")
        kinematic = read_json(PAPER / "KINEMATIC_ROW_DEFECT_CERTIFICATE.json")
        proof_manifest = read_json(PAPER / "PROOF_CLOSURE_MANIFEST.json")
    except Exception as exc:  # noqa: BLE001
        print(f"D5 P_state PS2 weighted target audit validation: FAIL\n- {exc}")
        return 1

    summary = audit.get("summary", {})
    dims = audit.get("dimensions", {})
    target = audit.get("weighted_infsup_target", {})
    noncirc = audit.get("non_circularity", {})
    source = audit.get("source_consistency", {})

    checks.check(audit.get("schema") == "d5-p-state-ps2-weighted-target-audit-v1", "schema changed")
    checks.check(
        audit.get("status") == "p_state_ps2_weighted_infsup_target_recorded_ps2_open",
        "status changed",
    )
    checks.check(audit.get("read_only") is True, "audit must be read-only")
    checks.check(audit.get("run_v047_invoked") is False, "run_v047 must not be invoked")
    checks.check(audit.get("submission_ready") is False, "submission readiness overclaimed")
    checks.check(audit.get("pc2_closed") is False, "PC2 unexpectedly closed")
    checks.check(audit.get("proof_gap_closed") is False, "proof gap unexpectedly closed")
    checks.check(audit.get("primitive_id") == "P_state_lift", "primitive id changed")
    checks.check(audit.get("plan_id") == "P_state", "plan id changed")
    checks.check(audit.get("primitive_closed") is False, "P_state unexpectedly closed")
    checks.check(audit.get("ps2_target_spec_closed") is True, "PS2 target spec not closed")
    checks.check(audit.get("ps2_inverse_or_infsup_closed") is False, "PS2 inf-sup unexpectedly closed")
    checks.check(audit.get("ps3_state_lift_conversion_closed") is False, "PS3 unexpectedly closed")
    checks.check(audit.get("state_lift_rate_proved") is False, "state lift rate overclaimed")
    checks.check(audit.get("certifies_induced_taylor_bounds") is False, "Taylor bounds overclaimed")
    checks.check(audit.get("certifies_dynamic_row_defect") is False, "dynamic defect overclaimed")
    checks.check(dims.get("stages") == 3, "stage count changed")
    checks.check(dims.get("bodies") == 2, "body count changed")
    checks.check(dims.get("state_block_dimension") == 72, "state block dimension changed")
    checks.check(dims.get("auxiliary_acceleration_dimension") == 36, "acceleration dimension changed")
    checks.check(dims.get("domain_dimension_with_acceleration") == 108, "full domain dimension changed")
    checks.check(dims.get("non_dynamic_row_dimension") == 96, "row dimension changed")
    checks.check(dims.get("row_deficit_vs_full_state_acceleration_domain") == 12, "full-domain deficit changed")
    checks.check(dims.get("row_surplus_vs_state_block") == 24, "state-block row surplus changed")
    checks.check(sum(dims.get("row_family_dimensions", {}).values()) == 96, "row-family dimension sum changed")
    checks.check(target.get("literal_full_domain_inverse_possible") is False, "literal inverse overclaimed")
    checks.check(target.get("state_block_infsup_with_acceleration_parameter") is True, "state-block target missing")
    checks.check(
        target.get("target_estimate") == "||delta S|| <= C_PS2 (||delta N_h^nd|| + h ||delta A||)",
        "weighted target estimate changed",
    )
    checks.check(target.get("weighted_domain_norm") == "||delta S|| + h ||delta A||", "weighted norm changed")
    checks.check("h A_G delta A" in target.get("why_h_weighted", ""), "h-weight rationale missing")
    checks.check("one h-power" in target.get("compatible_with_p_acc_obstruction", ""), "P_acc compatibility missing")
    checks.check(noncirc.get("uses_stage_residual_defect") is False, "stage residual defect used")
    checks.check(noncirc.get("uses_d5_dynamic_residual_defect") is False, "D5 dynamic residual used")
    checks.check(noncirc.get("uses_residual_identity_as_variable_lift") is False, "residual identity used as lift")
    checks.check(summary.get("ps2_target_spec_closed") is True, "summary target spec not closed")
    checks.check(summary.get("ps2_inverse_or_infsup_closed") is False, "summary PS2 overclosed")
    checks.check(summary.get("ps3_state_lift_conversion_closed") is False, "summary PS3 overclosed")
    checks.check(summary.get("closed_p_state_subproofs_after_target_spec") == 2, "P_state subproof count changed")
    checks.check(summary.get("induced_taylor_bounds_proved") == 0, "Taylor bounds unexpectedly proved")
    checks.check(source.get("p_state_map_schema") == "d5-p-state-map-definition-audit-v1", "P_state map link missing")
    checks.check(
        source.get("p_state_map_definition_closed") is True
        and p_state_map.get("ps1_map_definition_closed") is True,
        "P_state map definition not closed",
    )
    checks.check(source.get("p_state_map_primitive_closed") is False, "P_state map overclosed primitive")
    checks.check(source.get("p_state_anticircularity_schema") == "d5-p-state-anticircularity-audit-v1", "PS4 link missing")
    checks.check(
        source.get("p_state_anticircularity_closed") is True
        and p_state_anti.get("ps4_anticircularity_closed") is True,
        "PS4 anti-circularity not linked",
    )
    checks.check(source.get("p_state_anticircularity_pc2_closed") is False, "PS4 unexpectedly closes PC2")
    checks.check(source.get("p_acc_obstruction_schema") == "d5-p-acc-lift-obstruction-audit-v1", "P_acc obstruction link missing")
    checks.check(
        source.get("p_acc_current_unweighted_acceleration_rate") == "O(h^6)"
        and p_acc_obstruction.get("current_recorded_inputs_imply_only_unweighted_acceleration_rate") == "O(h^6)",
        "P_acc obstruction rate link changed",
    )
    checks.check(source.get("kinematic_certificate_schema") == "kinematic-row-defect-certificate-v1", "kinematic link missing")
    checks.check(
        source.get("kinematic_certificate_certified_rows") == 96
        and kinematic.get("proof_scope", {}).get("certified_row_count") == 96,
        "kinematic row count changed",
    )
    checks.check(
        source.get("proof_manifest_proof_gap_closed") is True
        and proof_manifest.get("closure_state", {}).get("pc2_closed_by_direct_substitution") is True,
        "proof manifest direct-substitution closure not reflected",
    )
    checks.check(
        proof_manifest.get("closure_state", {}).get("primitive_lift_route_closed") is False,
        "proof manifest unexpectedly closes primitive lift route",
    )
    checks.check(audit.get("manuscript_link", {}).get("main_tex_present") is True, "main TeX PS2 target missing")
    checks.check(audit.get("manuscript_link", {}).get("flat_tex_present") is True, "flat TeX PS2 target missing")

    for token in [
        "Status: **PS2 target specified; P_state lift remains open**.",
        "PS2 target specification closed: `True`.",
        "PS2 inverse or inf-sup closed: `False`.",
        "PS3 state lift conversion closed: `False`.",
        "P_state primitive closed: `False`.",
        "State block dimension: `72`.",
        "Auxiliary acceleration dimension: `36`.",
        "Non-dynamic row dimension: `96`.",
        "Induced Taylor bounds proved: `0/162`.",
        "Primitive/Taylor PC2 route closed: `False`.",
        "||delta S|| <= C_PS2 (||delta N_h^nd|| + h ||delta A||)",
        "The PS2 target specification is closed.",
        "The uniform PS2 inf-sup constant remains open.",
        "`P_state` remains open.",
    ]:
        checks.check(token in audit_md, f"markdown missing token: {token}")

    if checks.errors:
        print("D5 P_state PS2 weighted target audit validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("D5 P_state PS2 weighted target audit validation: PASS")
    print("ps2_target_spec_closed=True")
    print("ps2_inverse_or_infsup_closed=False")
    print("pc2_closed=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
