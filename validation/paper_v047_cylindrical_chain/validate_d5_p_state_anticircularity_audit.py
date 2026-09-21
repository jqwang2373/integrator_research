#!/usr/bin/env python3
"""Validate the D5 P_state anti-circularity audit."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
AUDIT_JSON = PAPER / "D5_P_STATE_ANTICIRCULARITY_AUDIT.json"
AUDIT_MD = PAPER / "D5_P_STATE_ANTICIRCULARITY_AUDIT.md"


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
        primitive_reduction = read_json(PAPER / "D5_PRIMITIVE_BOUND_REDUCTION_AUDIT.json")
        kinematic_certificate = read_json(PAPER / "KINEMATIC_ROW_DEFECT_CERTIFICATE.json")
        p_state_map_definition = read_json(PAPER / "D5_P_STATE_MAP_DEFINITION_AUDIT.json")
        dynamic_readiness = read_json(PAPER / "D5_DYNAMIC_DEFECT_READINESS_AUDIT.json")
        proof_manifest = read_json(PAPER / "PROOF_CLOSURE_MANIFEST.json")
    except Exception as exc:  # noqa: BLE001
        print(f"D5 P_state anti-circularity audit validation: FAIL\n- {exc}")
        return 1

    summary = audit.get("summary", {})
    gate = audit.get("dependency_gate", {})
    source = audit.get("source_consistency", {})
    forbidden = audit.get("forbidden_inputs", [])
    allowed = audit.get("allowed_inputs", [])
    route = audit.get("future_route", [])

    checks.check(audit.get("schema") == "d5-p-state-anticircularity-audit-v1", "schema changed")
    checks.check(audit.get("status") == "p_state_ps4_anticircularity_closed_lift_open", "status changed")
    checks.check(audit.get("read_only") is True, "audit must be read-only")
    checks.check(audit.get("run_v047_invoked") is False, "run_v047 must not be invoked")
    checks.check(audit.get("submission_ready") is False, "submission readiness overclaimed")
    checks.check(audit.get("pc2_closed") is False, "PC2 unexpectedly closed")
    checks.check(audit.get("proof_gap_closed") is False, "proof gap unexpectedly closed")
    checks.check(audit.get("primitive_id") == "P_state_lift", "primitive id changed")
    checks.check(audit.get("plan_id") == "P_state", "plan id changed")
    checks.check(audit.get("primitive_closed") is False, "P_state unexpectedly closed")
    checks.check(audit.get("ps4_anticircularity_closed") is True, "PS4 not closed")
    checks.check(audit.get("state_lift_rate_proved") is False, "state lift rate overclaimed")
    checks.check(audit.get("certifies_dynamic_row_defect") is False, "dynamic defect overclaimed")
    checks.check(audit.get("certifies_induced_taylor_bounds") is False, "Taylor bounds overclaimed")
    checks.check(summary.get("closed_p_state_subproofs_after_ps4") == 2, "closed P_state subproof count changed")
    checks.check(summary.get("open_p_state_subproofs_after_ps4") == 2, "open P_state subproof count changed")
    checks.check(summary.get("ps1_map_definition_closed") is True, "PS1 map definition not linked")
    checks.check(summary.get("ps2_inverse_or_infsup_closed") is False, "PS2 unexpectedly closed")
    checks.check(summary.get("ps3_state_lift_conversion_closed") is False, "PS3 unexpectedly closed")
    checks.check(summary.get("ps4_anticircularity_closed") is True, "PS4 summary not closed")
    checks.check(summary.get("term_rows_using_p_state") == 126, "P_state term-row count changed")
    checks.check(summary.get("induced_taylor_bounds_proved") == 0, "Taylor bounds unexpectedly proved")
    checks.check(gate.get("all_forbidden_inputs_disallowed") is True, "forbidden-input gate not satisfied")
    checks.check(gate.get("all_allowed_inputs_available") is True, "allowed-input gate not satisfied")
    checks.check(gate.get("uses_stage_residual_defect") is False, "stage residual defect used")
    checks.check(gate.get("uses_d5_dynamic_residual_defect") is False, "D5 dynamic defect used")
    checks.check(gate.get("uses_unproved_newton_solution_closeness") is False, "unproved Newton closeness used")
    checks.check(gate.get("closes_only_ps4") is True, "audit must close only PS4")
    checks.check(isinstance(forbidden, list) and len(forbidden) == 3, "forbidden input count changed")
    checks.check(
        all(isinstance(item, dict) and item.get("disallowed_for_ps2_ps3") is True for item in forbidden),
        "a forbidden input is not disallowed",
    )
    checks.check(isinstance(allowed, list) and len(allowed) == 3, "allowed input count changed")
    checks.check(
        all(isinstance(item, dict) and item.get("available") is True for item in allowed),
        "an allowed input is unavailable",
    )
    checks.check(isinstance(route, list) and len(route) == 2, "future route count changed")
    route_status = {item.get("id"): item.get("closed_now") for item in route if isinstance(item, dict)}
    checks.check(route_status == {"PS2": False, "PS3": False}, "future route closure status changed")
    for item in route:
        if isinstance(item, dict):
            checks.check(item.get("forbidden_inputs") == ["F1", "F2", "F3"], f"{item.get('id')} forbidden inputs changed")
    checks.check(audit.get("manuscript_link", {}).get("main_tex_present") is True, "main TeX P_state text missing")
    checks.check(audit.get("manuscript_link", {}).get("flat_tex_present") is True, "flat TeX P_state text missing")
    checks.check(source.get("primitive_reduction_schema") == "d5-primitive-bound-reduction-audit-v1", "primitive reduction link missing")
    checks.check(source.get("primitive_reduction_pc2_closed") is False and primitive_reduction.get("pc2_closed") is False, "primitive reduction unexpectedly closes PC2")
    checks.check(source.get("kinematic_certificate_schema") == "kinematic-row-defect-certificate-v1", "kinematic certificate link missing")
    checks.check(source.get("kinematic_certificate_certified_rows") == 96, "non-dynamic certified row count changed")
    checks.check(source.get("kinematic_certificate_excluded_dynamic_rows") == 36, "excluded dynamic row count changed")
    checks.check(kinematic_certificate.get("proof_scope", {}).get("certified_row_count") == 96, "kinematic certificate certified rows changed")
    checks.check(source.get("p_state_map_definition_schema") == "d5-p-state-map-definition-audit-v1", "P_state map-definition link missing")
    checks.check(
        source.get("p_state_map_definition_closed") is True
        and p_state_map_definition.get("ps1_map_definition_closed") is True,
        "P_state map definition not closed",
    )
    checks.check(source.get("p_state_map_definition_primitive_closed") is False, "map definition unexpectedly closes P_state")
    checks.check(
        source.get("dynamic_readiness_pc2_closed") is True
        and dynamic_readiness.get("pc2_closed") is True,
        "dynamic readiness direct-route PC2 closure missing",
    )
    checks.check(
        dynamic_readiness.get("summary", {}).get("primitive_taylor_closed_rows") == 0,
        "dynamic readiness unexpectedly closes primitive/Taylor rows",
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

    for token in [
        "Status: **P_state PS4 anti-circularity closed; lift remains open**.",
        "Closed P_state subproofs after PS4: `2/4`.",
        "Open P_state subproofs after PS4: `2`.",
        "PS1 map definition closed: `True`.",
        "PS2 inverse or inf-sup closed: `False`.",
        "PS3 state lift conversion closed: `False`.",
        "PS4 anti-circularity closed: `True`.",
        "P_state primitive closed: `False`.",
        "Primitive/Taylor PC2 route closed: `False`.",
        "PS2 and PS3 cannot use Lemma `stage-residual-defect`.",
        "PS2 and PS3 cannot use the D5 dynamic Newton-Euler residual defect.",
        "PS4 is closed.",
        "PS2 and PS3 remain open.",
        "`P_state` remains open.",
    ]:
        checks.check(token in audit_md, f"markdown missing token: {token}")

    if checks.errors:
        print("D5 P_state anti-circularity audit validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("D5 P_state anti-circularity audit validation: PASS")
    print("ps4_anticircularity_closed=True")
    print("closed_p_state_subproofs_after_ps4=2/4")
    print("pc2_closed=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
