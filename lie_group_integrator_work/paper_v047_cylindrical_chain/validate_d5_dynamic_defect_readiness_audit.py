#!/usr/bin/env python3
"""Validate the D5 dynamic-defect readiness audit."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
AUDIT_JSON = PAPER / "D5_DYNAMIC_DEFECT_READINESS_AUDIT.json"
AUDIT_MD = PAPER / "D5_DYNAMIC_DEFECT_READINESS_AUDIT.md"


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
        contract = read_json(PAPER / "NEWTON_EULER_DYNAMIC_ROW_CLOSURE_CONTRACT.json")
        proof_manifest = read_json(PAPER / "PROOF_CLOSURE_MANIFEST.json")
        direct_substitution = read_json(PAPER / "D5_DYNAMIC_DIRECT_SUBSTITUTION_CERTIFICATE.json")
    except Exception as exc:  # noqa: BLE001
        print(f"D5 dynamic-defect readiness validation: FAIL\n- {exc}")
        return 1

    summary = audit.get("summary", {})
    manuscript = audit.get("manuscript_link", {})
    source = audit.get("source_consistency", {})
    rows = audit.get("rows", [])

    checks.check(audit.get("schema") == "d5-dynamic-defect-readiness-audit-v1", "schema changed")
    checks.check(
        audit.get("status") == "d5_direct_substitution_closure_recorded_primitive_taylor_route_open",
        "status changed",
    )
    checks.check(audit.get("read_only") is True, "audit must be read-only")
    checks.check(audit.get("run_v047_invoked") is False, "run_v047 must not be invoked")
    checks.check(audit.get("submission_ready") is False, "submission readiness overclaimed")
    checks.check(audit.get("pc2_closed") is True, "PC2 direct-substitution closure missing")
    checks.check(audit.get("proof_gap_closed") is True, "proof gap direct-substitution closure missing")
    checks.check(
        audit.get("direct_residual_bridge_proof_gap_closed") is True,
        "scoped direct residual-bridge proof-gap closure missing",
    )
    checks.check(
        audit.get("proof_gap_closed_scope") == "direct_substitution_row_defect_pc2_only",
        "proof-gap closure scope missing or changed",
    )
    checks.check(audit.get("primitive_taylor_route_closed") is False, "primitive/Taylor route overclaimed")
    checks.check(audit.get("residual_to_error_route_closed") is False, "residual-to-error route overclaimed")
    checks.check(
        audit.get("multiplier_reaction_output_order_claimed") is False,
        "multiplier/reaction output order overclaimed",
    )
    checks.check(
        audit.get("stage_residual_O_h7_implementation_defect_proved") is True,
        "O(h^7) defect proof not closed by direct substitution",
    )
    checks.check(summary.get("row_count") == 36, "row count changed")
    checks.check(summary.get("expected_row_count") == contract.get("summary", {}).get("row_count") == 36, "expected row count changed")
    checks.check(summary.get("translational_rows") == 18, "translational row count changed")
    checks.check(summary.get("rotational_rows") == 18, "rotational row count changed")
    checks.check(summary.get("stage_counts") == {"0": 12, "1": 12, "2": 12}, "stage counts changed")
    checks.check(summary.get("body_counts") == {"0": 18, "1": 18}, "body counts changed")
    checks.check(summary.get("runtime_traceability_ready_rows") == 36, "not all rows are runtime-traceability ready")
    checks.check(summary.get("power_seven_required_rows") == 36, "not all rows require power seven")
    checks.check(summary.get("open_lifted_stage_terms") == 0, "open lifted-stage term count changed")
    checks.check(summary.get("direct_substitution_closed_rows") == 36, "direct-substitution row count changed")
    checks.check(
        summary.get("direct_substitution_dynamic_zero_rows")
        == direct_substitution.get("summary", {}).get("dynamic_zero_residual_rows")
        == 36,
        "direct-substitution zero row count changed",
    )
    checks.check(summary.get("primitive_taylor_closed_rows") == 0, "primitive/Taylor row count changed")
    checks.check(summary.get("theorem_certified_rows") == 36, "direct-route certified row count changed")
    checks.check(summary.get("finite_probe_sufficient_rows") == 0, "finite-probe sufficient row count changed")
    checks.check(summary.get("residual_to_error_promotion_allowed_rows") == 0, "residual-promotion row count changed")
    checks.check(summary.get("manuscript_d5_target_table_present_main_flat") is True, "manuscript D5 target table missing")
    checks.check(manuscript.get("main_tex_present") is True, "main TeX D5 target missing")
    checks.check(manuscript.get("flat_tex_present") is True, "flat TeX D5 target missing")
    checks.check(manuscript.get("main_tex_missing_tokens") == [], "main TeX D5 tokens missing")
    checks.check(manuscript.get("flat_tex_missing_tokens") == [], "flat TeX D5 tokens missing")
    checks.check(source.get("contract_d5_blueprint_is_not_closure") is False, "D5 direct closure boundary changed")
    checks.check(source.get("certificate_pc2_closed") is False, "symbolic certificate unexpectedly closed PC2")
    checks.check(source.get("direct_substitution_closed") is True, "direct-substitution certificate not linked")
    checks.check(
        proof_manifest.get("closure_state", {}).get("pc2_closed_by_direct_substitution") is True,
        "proof manifest direct-substitution PC2 closure missing",
    )
    checks.check(
        proof_manifest.get("closure_state", {}).get("primitive_lift_route_closed") is False,
        "proof manifest unexpectedly closes primitive lift route",
    )

    checks.check(isinstance(rows, list) and len(rows) == 36, "row list length changed")
    global_rows = [row.get("global_row") for row in rows if isinstance(row, dict)]
    checks.check(
        global_rows
        == [
            24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35,
            68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79,
            112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123,
        ],
        "global row map changed",
    )
    for row in rows if isinstance(rows, list) else []:
        if not isinstance(row, dict):
            checks.check(False, "row entry is not an object")
            continue
        checks.check(row.get("closed_input_count") == row.get("closed_input_expected") == 5, f"row {row.get('global_row')} closed inputs changed")
        checks.check(row.get("runtime_traceability_ready") is True, f"row {row.get('global_row')} runtime traceability missing")
        checks.check(row.get("required_certificate_kind") == "direct_substitution_row_oracle", f"row {row.get('global_row')} certificate kind changed")
        checks.check(row.get("required_defect_power") == 7, f"row {row.get('global_row')} required power changed")
        checks.check(row.get("open_terms") == [], f"row {row.get('global_row')} open term changed")
        checks.check(row.get("finite_probe_evidence_sufficient") is False, f"row {row.get('global_row')} finite-probe boundary changed")
        checks.check(row.get("residual_to_error_promotion_allowed") is False, f"row {row.get('global_row')} residual promotion boundary changed")
        checks.check(row.get("direct_substitution_closed") is True, f"row {row.get('global_row')} direct substitution not closed")
        checks.check(
            row.get("direct_substitution_residual_after_substitution") == "0",
            f"row {row.get('global_row')} direct residual changed",
        )
        checks.check(row.get("primitive_taylor_route_closed") is False, f"row {row.get('global_row')} primitive/Taylor route overclosed")
        checks.check(row.get("certified_for_theorem") is True, f"row {row.get('global_row')} theorem certification missing")
        checks.check(row.get("defect_bound_O_h7_proved") is True, f"row {row.get('global_row')} O(h^7) proof missing")

    for token in [
        "Status: **D5 direct-substitution closure recorded; primitive/Taylor route remains open**.",
        "Rows checked: `36/36`.",
        "Runtime-traceability-ready rows: `36/36`.",
        "Open lifted-stage dynamic terms: `0/36`.",
        "Direct-substitution closed rows: `36/36`.",
        "Direct-substitution dynamic zero rows: `36/36`.",
        "Primitive/Taylor closed rows: `0/36`.",
        "Direct-route certified rows: `36/36`.",
        "Direct PC2 row-defect route closed: `True`.",
        "Proof gap closed scope: `direct_substitution_row_defect_pc2_only`.",
        "Primitive/Taylor route closed: `False`.",
        "Residual-to-error route closed: `False`.",
        "Multiplier/reaction output order claimed: `False`.",
        "Forbidden now: primitive/Taylor-route closure",
    ]:
        checks.check(token in audit_md, f"markdown missing token: {token}")

    if checks.errors:
        print("D5 dynamic-defect readiness validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("D5 dynamic-defect readiness validation: PASS")
    print("rows=36/36")
    print("runtime_traceability_ready_rows=36/36")
    print("open_lifted_stage_terms=0/36")
    print("pc2_closed=True")
    print("submission_ready=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
