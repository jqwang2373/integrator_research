#!/usr/bin/env python3
"""Validate the D5 P_tube compact-constants audit."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
AUDIT_JSON = PAPER / "D5_P_TUBE_CONSTANTS_AUDIT.json"
AUDIT_MD = PAPER / "D5_P_TUBE_CONSTANTS_AUDIT.md"


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
        term_budget = read_json(PAPER / "D5_TAYLOR_TERM_BUDGET_AUDIT.json")
        proof_manifest = read_json(PAPER / "PROOF_CLOSURE_MANIFEST.json")
    except Exception as exc:  # noqa: BLE001
        print(f"D5 P_tube constants audit validation: FAIL\n- {exc}")
        return 1

    summary = audit.get("summary", {})
    source = audit.get("source_consistency", {})
    manuscript = audit.get("manuscript_link", {})

    checks.check(audit.get("schema") == "d5-p-tube-constants-audit-v1", "schema changed")
    checks.check(
        audit.get("status") == "p_tube_compact_constants_closed_pc2_open",
        "status changed",
    )
    checks.check(audit.get("read_only") is True, "audit must be read-only")
    checks.check(audit.get("run_v047_invoked") is False, "run_v047 must not be invoked")
    checks.check(audit.get("submission_ready") is False, "submission readiness overclaimed")
    checks.check(audit.get("pc2_closed") is False, "PC2 unexpectedly closed")
    checks.check(audit.get("proof_gap_closed") is False, "proof gap unexpectedly closed")
    checks.check(audit.get("primitive_id") == "P_uniform_tube_constants", "primitive id changed")
    checks.check(audit.get("plan_id") == "P_tube", "plan id changed")
    checks.check(audit.get("primitive_closed") is True, "P_tube not recorded as closed")
    checks.check(
        audit.get("closure_mode") == "closed_by_regular_compact_tube_lemma",
        "closure mode changed",
    )
    checks.check(audit.get("certifies_dynamic_row_defect") is False, "dynamic defect overclaimed")
    checks.check(audit.get("certifies_induced_taylor_bounds") is False, "Taylor bounds overclaimed")
    checks.check(summary.get("primitive_obligation_count") == 6, "primitive count changed")
    checks.check(summary.get("primitive_obligations_closed") == 1, "closed primitive count changed")
    checks.check(summary.get("primitive_obligations_remaining") == 5, "remaining primitive count changed")
    checks.check(summary.get("term_rows_using_p_tube") == 162, "P_tube term-row count changed")
    checks.check(summary.get("term_rows") == 162, "term-row count changed")
    checks.check(summary.get("induced_taylor_bounds_proved") == 0, "Taylor bounds unexpectedly proved")
    checks.check(manuscript.get("lemma_label") == "lem:d5-compact-tube-constants", "lemma label changed")
    checks.check(manuscript.get("main_tex_present") is True, "main TeX compact-tube lemma missing")
    checks.check(manuscript.get("flat_tex_present") is True, "flat TeX compact-tube lemma missing")
    checks.check(source.get("primitive_reduction_pc2_closed") is False, "primitive reduction closes PC2")
    checks.check(source.get("term_budget_pc2_closed") is False, "term budget closes PC2")
    checks.check(
        source.get("proof_manifest_proof_gap_closed") is True
        and proof_manifest.get("closure_state", {}).get("pc2_closed_by_direct_substitution") is True,
        "proof manifest direct-substitution closure not reflected",
    )
    checks.check(
        proof_manifest.get("closure_state", {}).get("primitive_lift_route_closed") is False,
        "proof manifest unexpectedly closes primitive lift route",
    )
    checks.check(primitive_reduction.get("pc2_closed") is False, "primitive reduction unexpectedly closes PC2")
    checks.check(term_budget.get("pc2_closed") is False, "term budget unexpectedly closes PC2")
    checks.check(
        audit.get("remaining_primitive_obligations")
        == [
            "P_state_lift",
            "P_acceleration_lift",
            "P_multiplier_lift",
            "P_geometry_lift",
            "P_gyroscopic_lift",
        ],
        "remaining primitive list changed",
    )

    for token in [
        "Status: **P_tube compact constants closed; separate primitive-route certificate remains open**.",
        "Primitive closed: `P_uniform_tube_constants`.",
        "Primitive obligations closed: `1/6`.",
        "Primitive obligations remaining: `5/6`.",
        "Term rows using P_tube: `162/162`.",
        "Induced Taylor bounds proved: `0/162`.",
        "Primitive/Taylor PC2 route closed: `False`.",
        "Five lift and bilinear primitive obligations remain open.",
        "Zero induced Taylor bounds are certified.",
        "Primitive/Taylor PC2 lane remains open.",
    ]:
        checks.check(token in audit_md, f"markdown missing token: {token}")

    if checks.errors:
        print("D5 P_tube constants audit validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("D5 P_tube constants audit validation: PASS")
    print("primitive_obligations_closed=1/6")
    print("induced_taylor_bounds_proved=0/162")
    print("pc2_closed=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
