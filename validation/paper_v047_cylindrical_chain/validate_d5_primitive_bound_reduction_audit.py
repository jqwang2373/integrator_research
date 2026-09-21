#!/usr/bin/env python3
"""Validate the D5 primitive-bound reduction audit."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
AUDIT_JSON = PAPER / "D5_PRIMITIVE_BOUND_REDUCTION_AUDIT.json"
AUDIT_MD = PAPER / "D5_PRIMITIVE_BOUND_REDUCTION_AUDIT.md"


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
        term_budget = read_json(PAPER / "D5_TAYLOR_TERM_BUDGET_AUDIT.json")
        proof_manifest = read_json(PAPER / "PROOF_CLOSURE_MANIFEST.json")
    except Exception as exc:  # noqa: BLE001
        print(f"D5 primitive-bound reduction audit validation: FAIL\n- {exc}")
        return 1

    summary = audit.get("summary", {})
    source = audit.get("source_consistency", {})
    manuscript = audit.get("manuscript_link", {})
    primitive_rows = audit.get("primitive_obligations", [])
    reduction_rows = audit.get("reduction_rows", [])
    corollaries = audit.get("conditional_row_level_corollaries", {})
    smooth_corollary = corollaries.get("smooth_force_torque_lift", {})

    checks.check(audit.get("schema") == "d5-primitive-bound-reduction-audit-v1", "schema changed")
    checks.check(audit.get("status") == "primitive_reduction_recorded_pc2_open", "status changed")
    checks.check(audit.get("read_only") is True, "audit must be read-only")
    checks.check(audit.get("run_v047_invoked") is False, "run_v047 must not be invoked")
    checks.check(audit.get("submission_ready") is False, "submission readiness overclaimed")
    checks.check(audit.get("pc2_closed") is False, "PC2 unexpectedly closed")
    checks.check(audit.get("proof_gap_closed") is False, "proof gap unexpectedly closed")
    checks.check(audit.get("term_bound_closure_claimed") is False, "term-bound closure unexpectedly claimed")
    checks.check(summary.get("term_rows") == 162, "term-row count changed")
    checks.check(summary.get("term_rows_with_reduction_rule") == 162, "reduction-rule coverage changed")
    checks.check(summary.get("primitive_obligation_count") == 6, "primitive obligation count changed")
    checks.check(summary.get("primitive_obligations_proved") == 1, "primitive closed count changed")
    checks.check(summary.get("open_primitive_obligations") == 5, "open primitive obligation count changed")
    checks.check(summary.get("p_tube_closed") is True, "P_tube compact constants not recorded as closed")
    checks.check(summary.get("term_bounds_proved") == 0, "Taylor term bounds unexpectedly proved")
    checks.check(summary.get("acceleration_lift_terms") == 36, "acceleration group count changed")
    checks.check(summary.get("smooth_force_torque_lift_terms") == 72, "smooth force/torque group count changed")
    checks.check(summary.get("multiplier_geometry_lift_terms") == 36, "multiplier geometry group count changed")
    checks.check(summary.get("gyroscopic_bilinear_lift_terms") == 18, "gyroscopic group count changed")
    checks.check(term_budget.get("pc2_closed") is False, "term budget unexpectedly closes PC2")
    checks.check(source.get("term_budget_pc2_closed") is False, "source term budget PC2 boundary changed")
    checks.check(
        source.get("readiness_direct_route_pc2_closed") is True,
        "source readiness direct-route PC2 boundary changed",
    )
    checks.check(
        source.get("readiness_primitive_taylor_closed_rows") == 0,
        "source readiness primitive/Taylor row boundary changed",
    )
    checks.check(
        source.get("readiness_primitive_route_closed") is False,
        "source readiness unexpectedly closes primitive route",
    )
    checks.check(
        source.get("proof_manifest_proof_gap_closed") is True
        and source.get("proof_manifest_direct_route_gap_closed") is True
        and proof_manifest.get("closure_state", {}).get("pc2_closed_by_direct_substitution") is True,
        "proof manifest direct-substitution closure not reflected",
    )
    checks.check(
        source.get("proof_manifest_proof_gap_closed_scope")
        == proof_manifest.get("closure_state", {}).get("proof_gap_closed_scope"),
        "proof manifest proof-gap scope not reflected",
    )
    checks.check(
        proof_manifest.get("closure_state", {}).get("primitive_lift_route_closed") is False,
        "proof manifest unexpectedly closes primitive lift route",
    )
    checks.check(manuscript.get("main_tex_present") is True, "main TeX primitive-bound link missing")
    checks.check(manuscript.get("flat_tex_present") is True, "flat TeX primitive-bound link missing")
    checks.check(
        r"\label{cor:d5-smooth-force-row-bound-under-lifts}" in manuscript.get("tokens", []),
        "smooth force row-level corollary token missing",
    )
    checks.check(
        smooth_corollary.get("label") == "cor:d5-smooth-force-row-bound-under-lifts",
        "smooth force corollary label missing",
    )
    checks.check(
        smooth_corollary.get("main_tex_present") is True
        and smooth_corollary.get("flat_tex_present") is True,
        "smooth force corollary missing in main/flat TeX",
    )
    checks.check(
        smooth_corollary.get("term_rows_conditionally_bound_under_lifts") == 72,
        "smooth force corollary row count changed",
    )
    checks.check(
        smooth_corollary.get("primitive_inputs_assumed")
        == ["P_state_lift", "P_multiplier_lift"],
        "smooth force corollary primitive inputs changed",
    )
    checks.check(
        smooth_corollary.get("actual_taylor_bounds_proved") == 0,
        "smooth force corollary overclaims Taylor bounds",
    )
    checks.check(
        smooth_corollary.get("primitive_closed") is False
        and smooth_corollary.get("pc2_closed") is False,
        "smooth force corollary overclaims primitive or PC2 closure",
    )
    checks.check(
        smooth_corollary.get("uses_d4_direct_route_smoothness_as_rate_proof") is False,
        "smooth force corollary must not use D4 direct route as primitive-rate proof",
    )
    checks.check(isinstance(primitive_rows, list) and len(primitive_rows) == 6, "primitive row list changed")
    checks.check(isinstance(reduction_rows, list) and len(reduction_rows) == 162, "reduction row list changed")
    primitive_ids = {row.get("id") for row in primitive_rows if isinstance(row, dict)}
    checks.check(
        primitive_ids
        == {
            "P_state_lift",
            "P_acceleration_lift",
            "P_multiplier_lift",
            "P_geometry_lift",
            "P_gyroscopic_lift",
            "P_uniform_tube_constants",
        },
        "primitive ids changed",
    )
    for row in primitive_rows:
        if isinstance(row, dict):
            if row.get("id") == "P_uniform_tube_constants":
                checks.check(row.get("proved") is True, "P_tube compact constants not proved")
                checks.check(
                    row.get("proof_source") == "Lemma~\\ref{lem:d5-compact-tube-constants}",
                    "P_tube proof source changed",
                )
            else:
                checks.check(row.get("proved") is False, f"non-tube primitive unexpectedly proved: {row.get('id')}")
            checks.check(
                int(row.get("term_rows_using_obligation", 0)) > 0,
                f"primitive obligation has no term rows: {row.get('id')}",
            )
    for row in reduction_rows:
        if not isinstance(row, dict):
            checks.check(False, "reduction row is not an object")
            continue
        checks.check(row.get("reduction_rule_recorded") is True, "reduction rule missing")
        checks.check(row.get("primitive_bounds_proved") is False, "primitive bounds unexpectedly proved")
        checks.check(row.get("term_bound_proved") is False, "term bound unexpectedly proved")
        checks.check(row.get("certifies_theorem_now") is False, "reduction row unexpectedly certifies theorem")
        checks.check(
            set(row.get("primitive_obligations", [])).issubset(primitive_ids),
            "reduction row references unknown primitive",
        )

    for token in [
        "Status: **primitive reduction recorded; primitive/Taylor PC2 route remains open**.",
        "Taylor subterms with reduction rules: `162/162`.",
        "Primitive obligations: `6`.",
        "Primitive obligations proved: `1/6`.",
        "P_tube compact constants closed: `True`.",
        "Taylor term bounds proved: `0/162`.",
        "Separate primitive/Taylor PC2 route closed: `False`.",
        "Smooth force/torque/friction corollary present main/flat: `True/True`.",
        "Smooth force/torque/friction rows conditionally bounded: `72/72`.",
        "Smooth force/torque/friction actual Taylor bounds proved: `0/72`.",
        "D4 direct-route smoothness used as primitive-rate proof: `False`.",
        "The compact-tube primitive obligation is proved.",
        "Five lift and bilinear primitive obligations remain open.",
        "Zero Taylor term bounds are certified.",
    ]:
        checks.check(token in audit_md, f"markdown missing token: {token}")

    if checks.errors:
        print("D5 primitive-bound reduction audit validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("D5 primitive-bound reduction audit validation: PASS")
    print("term_rows_with_reduction_rule=162/162")
    print("primitive_obligations_proved=1/6")
    print("pc2_closed=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
