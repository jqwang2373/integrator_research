#!/usr/bin/env python3
"""Validate the CMAME strict-proof boundary audit."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
ROOT = PAPER.parent.parent
AUDIT_JSON = PAPER / "CMAME_STRICT_PROOF_AUDIT.json"
AUDIT_MD = PAPER / "CMAME_STRICT_PROOF_AUDIT.md"
REF_TXT = ROOT / "1-s2.0-S0377042719305229-main.txt"
MAIN_TEX = PAPER / "main_cmame.tex"
FLAT_TEX = PAPER / "cmame_submission_flat" / "main_cmame_submission.tex"
BLOCKER = PAPER / "CMAME_BLOCKER_CLOSURE_GATE.json"
PROOF_CONTRACT = PAPER / "CMAME_PROOF_CONTRACT_GATE.json"
PROOF_CLOSURE = PAPER / "PROOF_CLOSURE_MANIFEST.json"
PROOF_CLAIM_TRACEABILITY = PAPER / "PROOF_CLAIM_TRACEABILITY_AUDIT.json"
PROOF_STYLE = PAPER / "CMAME_PROOF_STYLE_AUDIT.json"
D5_TAYLOR = PAPER / "D5_CONDITIONAL_TAYLOR_CERTIFICATE.json"
D5_TERM_BUDGET = PAPER / "D5_TAYLOR_TERM_BUDGET_AUDIT.json"
D5_OPEN_PRIMITIVE = PAPER / "D5_OPEN_PRIMITIVE_GAP_AUDIT.json"
D5_P_STATE_PS3_FULL_ROUTE = PAPER / "D5_P_STATE_PS3_FULL_RESIDUAL_ROUTE_CERTIFICATE.json"
DYNAMIC_ORACLE = PAPER / "DYNAMIC_ROW_ORACLE_GATE.json"
B1_AD_EXPANDED_CLOSURE = PAPER / "B1_AD_EXPANDED_SYMBOLIC_ORACLE_CLOSURE_CERTIFICATE.json"
DIRECT_ROUTE_SCOPE = "direct_residual_bridge_kantorovich_route_closed_primitive_taylor_conditional_schema_open"


class Checks:
    def __init__(self) -> None:
        self.errors: list[str] = []

    def check(self, condition: bool, message: str) -> None:
        if not condition:
            self.errors.append(message)


def read_text(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8", errors="replace")


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(path)
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def contains_normalized(text: str, token: str) -> bool:
    return token in text or " ".join(token.split()) in " ".join(text.split())


def blocker_by_id(gate: dict[str, Any], blocker_id: str) -> dict[str, Any]:
    for item in gate.get("blockers", []):
        if item.get("id") == blocker_id:
            return item
    raise KeyError(blocker_id)


def sidecar_proof_gap_scope_entries() -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []

    def walk(file_name: str, node: Any, path: str) -> None:
        if isinstance(node, dict):
            if "proof_manifest_proof_gap_closed" in node:
                scope = node.get("proof_manifest_proof_gap_closed_scope")
                entries.append(
                    {
                        "file": file_name,
                        "json_path": path,
                        "legacy_value": node.get("proof_manifest_proof_gap_closed"),
                        "scope": scope,
                        "scope_ok": scope == DIRECT_ROUTE_SCOPE,
                    }
                )
            for key, value in node.items():
                child_path = f"{path}.{key}" if path else str(key)
                walk(file_name, value, child_path)
        elif isinstance(node, list):
            for index, value in enumerate(node):
                walk(file_name, value, f"{path}[{index}]")

    for path in sorted(PAPER.glob("D5_*.json")):
        walk(path.name, read_json(path), "$")
    return entries


def main() -> int:
    checks = Checks()
    try:
        audit = read_json(AUDIT_JSON)
        audit_md = read_text(AUDIT_MD)
        ref_text = read_text(REF_TXT)
        main_tex = read_text(MAIN_TEX)
        flat_tex = read_text(FLAT_TEX)
        blocker = read_json(BLOCKER)
        proof_contract = read_json(PROOF_CONTRACT)
        proof_closure = read_json(PROOF_CLOSURE)
        proof_claim_traceability = read_json(PROOF_CLAIM_TRACEABILITY)
        proof_style = read_json(PROOF_STYLE)
        d5_taylor = read_json(D5_TAYLOR)
        d5_term_budget = read_json(D5_TERM_BUDGET)
        d5_open_primitive = read_json(D5_OPEN_PRIMITIVE)
        d5_p_state_ps3_full_route = read_json(D5_P_STATE_PS3_FULL_ROUTE)
        dynamic_oracle = read_json(DYNAMIC_ORACLE)
        b1_ad_expanded_closure = read_json(B1_AD_EXPANDED_CLOSURE)
        sidecar_scope_entries = sidecar_proof_gap_scope_entries()
    except Exception as exc:  # noqa: BLE001
        print(f"cmame_strict_proof_audit=FAIL\n- {exc}")
        return 1

    b1 = blocker_by_id(blocker, "B1")
    b3 = blocker_by_id(blocker, "B3")
    b4 = blocker_by_id(blocker, "B4")
    b6 = blocker_by_id(blocker, "B6")
    b7 = blocker_by_id(blocker, "B7")
    theorem_contract = proof_contract.get("theorem_contract", {})
    closure_state = proof_closure.get("closure_state", {})
    manifest_direct_standard = proof_closure.get(
        "direct_residual_bridge_kantorovich_submission_standard", {}
    )
    manifest_strict_direct = proof_closure.get("strict_direct_residual_bridge_submission_standard", {})
    closure_evidence = proof_closure.get("evidence_summary", {})
    theorem_statement_boundary = proof_closure.get("theorem_statement_boundary", {})
    manuscript_traceability = proof_closure.get("manuscript_traceability", {})
    proof_closure_anchor_map = proof_closure.get("manuscript_anchor_map", {})
    proof_claim_anchor_map = proof_claim_traceability.get("manuscript_anchor_map", {})
    proof_writing_card = proof_claim_traceability.get("proof_writing_boundary_card", {})
    proof_claim_remaining_boundary = proof_claim_traceability.get("remaining_claim_boundary", {})
    expected_anchor_evidence_sources = [
        "PROOF_CLOSURE_MANIFEST.json",
        "PROOF_CLAIM_TRACEABILITY_AUDIT.json",
    ]
    d5_summary = d5_taylor.get("summary", {})
    term_budget_summary = d5_term_budget.get("summary", {})
    primitive_gap_summary = d5_open_primitive.get("summary", {})
    primitive_dependency_graph = d5_open_primitive.get("primitive_dependency_graph", {})
    dynamic_boundary = dynamic_oracle.get("acceptance_boundary", {})
    formula_ad_oracle = dynamic_oracle.get("formula_row_ad_jacobian_oracle", {})
    full_formula_oracle = dynamic_oracle.get("full_independent_formula_row_oracle", {})

    checks.check(audit.get("schema") == "cmame-strict-proof-audit-v1", "audit schema changed")
    checks.check(
        audit.get("status") == "strict_conditional_residual_bridge_proof_audited_b3_closed_submission_not_ready",
        "audit status changed",
    )
    checks.check(audit.get("read_only_audit") is True, "audit must be read-only")
    checks.check(audit.get("submission_ready") is False, "audit must not claim submission ready")
    readiness_boundary = audit.get("readiness_boundary", {})
    checks.check(
        audit.get("submission_ready_scope")
        == "strict_proof_global_boundary_not_narrowed_claim_package_decision",
        "submission-ready scope changed",
    )
    checks.check(
        readiness_boundary.get("strict_proof_audit_scope")
        == "B1_B3_strict_conditional_residual_bridge_proof_boundary",
        "strict proof audit scope changed",
    )
    checks.check(
        readiness_boundary.get("narrowed_claim_b4_b6_b7_statuses")
        == {"B4": b4.get("status"), "B6": b6.get("status"), "B7": b7.get("status")}
        == {"B4": "closed", "B6": "closed", "B7": "closed"},
        "narrowed-claim B4/B6/B7 statuses changed",
    )
    checks.check(
        readiness_boundary.get("global_submission_boundaries_retained")
        == [
            "full_source_policy_package_ready",
            "theorem_level_eta_h_solver_policy_evidence",
            "closed_residual_to_error_theorem_for_mechanism_rows",
        ],
        "global submission boundaries changed",
    )
    theorem_traceability = audit.get("manuscript_theorem_traceability", {})
    checks.check(
        theorem_traceability.get("proof_closure_status") == proof_closure.get("status"),
        "manuscript theorem traceability proof-closure status mismatch",
    )
    checks.check(
        theorem_traceability.get("theorem_statement_labels_present")
        == theorem_statement_boundary.get("all_required_labels_present_main_and_flat")
        is True,
        "theorem labels not carried into strict proof audit",
    )
    checks.check(
        theorem_traceability.get("conditional_theorem_boundary_present")
        == theorem_statement_boundary.get("conditional_theorem_boundary_present_main_and_flat")
        is True,
        "conditional theorem boundary not carried into strict proof audit",
    )
    checks.check(
        theorem_traceability.get("conditional_proof_claims_mapped_to_manuscript")
        == manuscript_traceability.get("conditional_proof_claims_mapped_to_manuscript")
        is True,
        "proof claims not mapped into strict proof audit",
    )
    checks.check(
        theorem_traceability.get("proof_dependency_graph_present")
        == manuscript_traceability.get("proof_dependency_graph_present_main_and_flat")
        is True,
        "proof dependencies not carried into strict proof audit",
    )
    checks.check(
        theorem_traceability.get("proof_traceability_table_present")
        == manuscript_traceability.get("proof_traceability_table_present_main_and_flat")
        is True,
        "proof traceability table not carried into strict proof audit",
    )
    checks.check(
        theorem_traceability.get("dynamic_proof_closure_matrix_present")
        == manuscript_traceability.get("dynamic_proof_closure_matrix_present_main_and_flat")
        is True,
        "dynamic proof matrix not carried into strict proof audit",
    )
    checks.check(
        theorem_traceability.get("primitive_lane_boundary_present")
        == manuscript_traceability.get("primitive_lane_boundary_present_main_and_flat")
        is True,
        "primitive-route boundary not carried into strict proof audit",
    )
    checks.check(
        theorem_traceability.get("residual_nonpromotion_present")
        == manuscript_traceability.get("residual_to_error_nonpromotion_present_main_and_flat")
        is True,
        "residual nonpromotion traceability not carried into strict proof audit",
    )
    checks.check(
        theorem_traceability.get("eta_h_theorem_condition_retained")
        == theorem_statement_boundary.get("eta_h_theorem_condition_retained")
        is True,
        "eta_h theorem condition not retained in strict proof audit",
    )
    checks.check(
        theorem_traceability.get("eta_h_solver_policy_evidence_closed")
        == theorem_statement_boundary.get("eta_h_solver_policy_evidence_closed")
        is False,
        "strict proof audit overclaims eta_h solver-policy theorem",
    )
    checks.check(
        theorem_traceability.get("fixed_tolerance_runs_are_asymptotic_proof")
        == theorem_statement_boundary.get("fixed_tolerance_runs_are_asymptotic_proof")
        is False,
        "strict proof audit promotes fixed-tolerance runs to asymptotic proof",
    )
    checks.check(
        theorem_traceability.get("residual_to_error_not_promoted")
        == theorem_statement_boundary.get("does_not_promote_residual_to_error")
        is True,
        "strict proof audit lost residual-to-error boundary",
    )
    checks.check(
        theorem_traceability.get("source_policy_or_full_tfe_not_promoted")
        == theorem_statement_boundary.get("does_not_promote_source_policy_or_full_tfe")
        is True,
        "strict proof audit lost source-policy/full-TFE nonpromotion",
    )
    checks.check(
        theorem_traceability.get("does_not_change_proof_closure_state")
        == manuscript_traceability.get("does_not_change_proof_closure_state")
        is True,
        "strict proof audit changed proof closure state through traceability",
    )
    checks.check(
        theorem_traceability.get("manuscript_anchor_map_present")
        == proof_closure_anchor_map.get("all_label_anchors_present")
        is True,
        "proof-closure manuscript anchor map not carried into strict proof audit",
    )
    checks.check(
        theorem_traceability.get("manuscript_anchor_label_count")
        == proof_closure_anchor_map.get("label_anchor_count")
        == 24,
        "proof-closure manuscript anchor label count not carried into strict proof audit",
    )
    checks.check(
        theorem_traceability.get("theorem_assumption_anchor_map_present")
        == proof_closure_anchor_map.get("all_theorem_assumption_anchors_present")
        is True,
        "proof-closure theorem-assumption anchor map not carried into strict proof audit",
    )
    checks.check(
        theorem_traceability.get("theorem_assumption_anchor_count")
        == proof_closure_anchor_map.get("theorem_assumption_anchor_count")
        == 7,
        "proof-closure theorem-assumption anchor count not carried into strict proof audit",
    )
    checks.check(
        theorem_traceability.get("theorem_assumption_anchor_ids")
        == proof_closure_anchor_map.get("theorem_assumption_anchor_ids")
        == ["P1", "P2", "P3", "P4", "P5", "P6", "P7"],
        "proof-closure theorem-assumption anchor IDs not carried into strict proof audit",
    )
    checks.check(
        theorem_traceability.get("proof_closure_proof_claim_anchor_maps_match") is True
        and proof_closure_anchor_map == proof_claim_anchor_map,
        "proof-closure/proof-claim manuscript anchor maps diverged in strict proof audit",
    )
    checks.check(
        theorem_traceability.get("reader_facing_manuscript_boundary_present")
        == proof_writing_card.get("reader_facing_manuscript_boundary_present")
        == proof_claim_traceability.get("remaining_claim_boundary", {}).get(
            "reader_facing_manuscript_boundary_present"
        )
        == proof_claim_traceability.get("summary", {}).get("reader_facing_proof_claim_boundary_present")
        is True,
        "reader-facing proof-claim boundary not carried into strict proof audit",
    )
    checks.check(
        "Reader-facing proof-claim boundary present in manuscript/PDF text: `True`." in audit_md,
        "strict proof audit markdown missing reader-facing proof-claim boundary",
    )
    checks.check(
        theorem_traceability.get("p7_retained_nonpromotion_boundary_present")
        == proof_writing_card.get("p7_retained_nonpromotion_boundary_present")
        == proof_claim_traceability.get("remaining_claim_boundary", {}).get(
            "p7_retained_nonpromotion_boundary_present"
        )
        == proof_claim_traceability.get("summary", {}).get("p7_retained_nonpromotion_boundary_present")
        is True,
        "P7 output nonclaim/residual-to-error boundary not carried into strict proof audit",
    )
    checks.check(
        "P7 output nonclaim/residual-to-error boundary present in manuscript: `True`." in audit_md,
        "strict proof audit markdown missing P7 output nonclaim/residual-to-error boundary",
    )
    checks.check(
        theorem_traceability.get("b1_closure_scope_boundary_present")
        == proof_writing_card.get("b1_closure_scope_boundary_present")
        == proof_claim_traceability.get("remaining_claim_boundary", {}).get(
            "b1_closure_scope_boundary_present"
        )
        == proof_claim_traceability.get("summary", {}).get("b1_closure_scope_boundary_present")
        is True,
        "B1 closure-scope boundary not carried into strict proof audit",
    )
    checks.check(
        "B1 closure-scope boundary present in manuscript/PDF text: `True`." in audit_md,
        "strict proof audit markdown missing B1 closure-scope boundary",
    )
    checks.check(
        theorem_traceability.get("p6_solver_scope_boundary_present")
        == proof_writing_card.get("p6_solver_scope_boundary_present")
        == proof_claim_traceability.get("remaining_claim_boundary", {}).get(
            "p6_solver_scope_boundary_present"
        )
        == proof_claim_traceability.get("summary", {}).get("p6_solver_scope_boundary_present")
        is True,
        "P6 solver-scope boundary not carried into strict proof audit",
    )
    checks.check(
        "P6 solver-scope boundary present in manuscript/PDF text: `True`." in audit_md,
        "strict proof audit markdown missing P6 solver-scope boundary",
    )
    checks.check(
        theorem_traceability.get("p1p2_compact_tube_boundary_present")
        == proof_claim_remaining_boundary.get("p1p2_compact_tube_boundary_present")
        == proof_claim_traceability.get("summary", {}).get("p1p2_compact_tube_boundary_present")
        is True,
        "P1/P2 compact-tube boundary not carried into strict proof audit",
    )
    checks.check(
        "P1/P2 compact-tube boundary present in manuscript/PDF text: `True`." in audit_md,
        "strict proof audit markdown missing P1/P2 compact-tube boundary",
    )
    checks.check(
        theorem_traceability.get("p3p4_implementation_boundary_present")
        == proof_writing_card.get("p3p4_implementation_boundary_present")
        == proof_claim_traceability.get("remaining_claim_boundary", {}).get(
            "p3p4_implementation_boundary_present"
        )
        == proof_claim_traceability.get("summary", {}).get("p3p4_implementation_boundary_present")
        is True,
        "P3/P4 implementation-defect boundary not carried into strict proof audit",
    )
    checks.check(
        "P3/P4 implementation-defect boundary present in manuscript/PDF text: `True`."
        in audit_md,
        "strict proof audit markdown missing P3/P4 implementation-defect boundary",
    )
    checks.check(
        theorem_traceability.get("p5_direct_route_boundary_present")
        == proof_writing_card.get("p5_direct_route_boundary_present")
        == proof_claim_traceability.get("remaining_claim_boundary", {}).get(
            "p5_direct_route_boundary_present"
        )
        == proof_claim_traceability.get("summary", {}).get("p5_direct_route_boundary_present")
        is True,
        "P5 direct-route boundary not carried into strict proof audit",
    )
    checks.check(
        "P5 direct-route boundary present in manuscript/PDF text: `True`." in audit_md,
        "strict proof audit markdown missing P5 direct-route boundary",
    )
    checks.check(
        theorem_traceability.get("proof_causality_ledger_present")
        == proof_writing_card.get("proof_causality_ledger_present")
        == proof_claim_traceability.get("remaining_claim_boundary", {}).get(
            "proof_causality_ledger_present"
        )
        == proof_claim_traceability.get("summary", {}).get(
            "proof_causality_ledger_present"
        )
        is True,
        "proof-causality table not carried into strict proof audit",
    )
    checks.check(
        "Proof-causality table present in manuscript/PDF text: `True`."
        in audit_md,
        "strict proof audit markdown missing proof-causality table",
    )
    checks.check(
        theorem_traceability.get("direct_route_anticircularity_ledger_present")
        == proof_writing_card.get("direct_route_anticircularity_ledger_present")
        == proof_claim_traceability.get("remaining_claim_boundary", {}).get(
            "direct_route_anticircularity_ledger_present"
        )
        == proof_claim_traceability.get("summary", {}).get(
            "direct_route_anticircularity_ledger_present"
        )
        is True,
        "direct-route anti-circularity table not carried into strict proof audit",
    )
    checks.check(
        "Direct-route anti-circularity table present in manuscript/PDF text: `True`."
        in audit_md,
        "strict proof audit markdown missing direct-route anti-circularity table",
    )
    checks.check(
        theorem_traceability.get("p_interface_satisfaction_ledger_present")
        == proof_writing_card.get("p_interface_satisfaction_ledger_present")
        == proof_claim_traceability.get("remaining_claim_boundary", {}).get(
            "p_interface_satisfaction_ledger_present"
        )
        == proof_claim_traceability.get("summary", {}).get(
            "p_interface_satisfaction_ledger_present"
        )
        is True,
        "Theorem-interface satisfaction table not carried into strict proof audit",
    )
    checks.check(
        "Theorem-interface satisfaction table present in manuscript/PDF text: `True`."
        in audit_md,
        "strict proof audit markdown missing theorem-interface satisfaction table",
    )
    checks.check(
        theorem_traceability.get("p7_residual_to_error_ledger_present")
        == proof_writing_card.get("p7_residual_to_error_ledger_present")
        == proof_claim_traceability.get("remaining_claim_boundary", {}).get(
            "p7_residual_to_error_ledger_present"
        )
        == proof_claim_traceability.get("summary", {}).get(
            "p7_residual_to_error_ledger_present"
        )
        is True,
        "Residual-to-error transfer-scope exclusion table not carried into strict proof audit",
    )
    checks.check(
        "Residual-to-error transfer-scope exclusion table present in manuscript/PDF text: `True`."
        in audit_md,
        "strict proof audit markdown missing Residual-to-error transfer-scope exclusion table",
    )
    checks.check(
        theorem_traceability.get("theorem_use_rule_present")
        == proof_writing_card.get("theorem_use_rule_present")
        == proof_claim_traceability.get("remaining_claim_boundary", {}).get(
            "theorem_use_rule_present"
        )
        == proof_claim_traceability.get("summary", {}).get(
            "theorem_use_rule_present"
        )
        is True,
        "theorem-use rule not carried into strict proof audit",
    )
    checks.check(
        "Auxiliary-evidence scope present in manuscript/PDF text: `True`." in audit_md,
        "strict proof audit markdown missing auxiliary-evidence scope",
    )
    checks.check(
        theorem_traceability.get("quantifier_domain_ledger_present")
        == proof_writing_card.get("quantifier_domain_ledger_present")
        == proof_claim_traceability.get("remaining_claim_boundary", {}).get(
            "quantifier_domain_ledger_present"
        )
        == proof_claim_traceability.get("summary", {}).get(
            "quantifier_domain_ledger_present"
        )
        is True,
        "quantifier/domain table not carried into strict proof audit",
    )
    checks.check(
        "Quantifier/domain table present in manuscript/PDF text: `True`."
        in audit_md,
        "strict proof audit markdown missing quantifier/domain table",
    )
    checks.check(
        theorem_traceability.get("local_global_transfer_ledger_present")
        == proof_writing_card.get("local_global_transfer_ledger_present")
        == proof_claim_traceability.get("remaining_claim_boundary", {}).get(
            "local_global_transfer_ledger_present"
        )
        == proof_claim_traceability.get("summary", {}).get(
            "local_global_transfer_ledger_present"
        )
        is True,
        "local-to-global transfer table not carried into strict proof audit",
    )
    checks.check(
        "Local-to-global transfer table present in manuscript/PDF text: `True`."
        in audit_md,
        "strict proof audit markdown missing local-to-global transfer table",
    )
    checks.check(
        theorem_traceability.get("objective_completion_boundary_present")
        == proof_writing_card.get("objective_completion_boundary_present")
        == proof_claim_traceability.get("remaining_claim_boundary", {}).get(
            "objective_completion_boundary_present"
        )
        == proof_claim_traceability.get("summary", {}).get(
            "objective_completion_boundary_present"
        )
        is True,
        "objective-completion boundary not carried into strict proof audit",
    )
    checks.check(
        "Objective-completion boundary present in manuscript/PDF text: `True`."
        in audit_md,
        "strict proof audit markdown missing objective-completion boundary",
    )
    checks.check(
        theorem_traceability.get("constant_dependency_ledger_present")
        == proof_writing_card.get("constant_dependency_ledger_present")
        == proof_claim_traceability.get("remaining_claim_boundary", {}).get(
            "constant_dependency_ledger_present"
        )
        == proof_claim_traceability.get("summary", {}).get(
            "constant_dependency_ledger_present"
        )
        is True,
        "constant-dependency table not carried into strict proof audit",
    )
    checks.check(
        "Constant-dependency table present in manuscript/PDF text: `True`."
        in audit_md,
        "strict proof audit markdown missing constant-dependency table",
    )
    checks.check(
        theorem_traceability.get("theorem_dependency_consumption_ledger_present")
        == proof_writing_card.get("theorem_dependency_consumption_ledger_present")
        == proof_claim_traceability.get("remaining_claim_boundary", {}).get(
            "theorem_dependency_consumption_ledger_present"
        )
        == proof_claim_traceability.get("summary", {}).get(
            "theorem_dependency_consumption_ledger_present"
        )
        is True,
        "theorem dependency consumption table not carried into strict proof audit",
    )
    checks.check(
        "Theorem dependency consumption table present in manuscript/PDF text: `True`."
        in audit_md,
        "strict proof audit markdown missing theorem dependency consumption table",
    )
    checks.check(
        theorem_traceability.get("branch_consistency_ledger_present")
        == proof_claim_remaining_boundary.get("branch_consistency_table_present")
        == proof_claim_traceability.get("summary", {}).get("branch_consistency_table_present")
        is True,
        "accepted-branch consistency table not carried into strict proof audit",
    )
    checks.check(
        "Accepted-branch consistency table present in manuscript/PDF text: `True`."
        in audit_md,
        "strict proof audit markdown missing accepted-branch consistency table",
    )
    checks.check(
        theorem_traceability.get("implementation_route_oracle_ledger_present")
        == proof_writing_card.get("implementation_route_oracle_ledger_present")
        == proof_claim_traceability.get("remaining_claim_boundary", {}).get(
            "implementation_route_oracle_ledger_present"
        )
        == proof_claim_traceability.get("summary", {}).get(
            "implementation_route_oracle_ledger_present"
        )
        is True,
        "implementation-route/oracle separation table not carried into strict proof audit",
    )
    checks.check(
        "Implementation-route/certificate separation table present in manuscript/PDF text: `True`."
        in audit_md,
        "strict proof audit markdown missing implementation-route/oracle separation table",
    )
    checks.check(
        theorem_traceability.get("nonlinear_solver_scale_ledger_present")
        == proof_writing_card.get("nonlinear_solver_scale_ledger_present")
        == proof_claim_traceability.get("remaining_claim_boundary", {}).get(
            "nonlinear_solver_scale_ledger_present"
        )
        == proof_claim_traceability.get("summary", {}).get(
            "nonlinear_solver_scale_ledger_present"
        )
        is True,
        "nonlinear-solver scale table not carried into strict proof audit",
    )
    checks.check(
        "Nonlinear-solver scale table present in manuscript/PDF text: `True`."
        in audit_md,
        "strict proof audit markdown missing nonlinear-solver scale table",
    )
    checks.check(
        theorem_traceability.get("local_defect_decomposition_ledger_present")
        == proof_writing_card.get("local_defect_decomposition_ledger_present")
        == proof_claim_traceability.get("remaining_claim_boundary", {}).get(
            "local_defect_decomposition_ledger_present"
        )
        == proof_claim_traceability.get("summary", {}).get(
            "local_defect_decomposition_ledger_present"
        )
        is True,
        "local-defect decomposition table not carried into strict proof audit",
    )
    checks.check(
        "Local-defect decomposition table present in manuscript/PDF text: `True`."
        in audit_md,
        "strict proof audit markdown missing local-defect decomposition table",
    )
    checks.check(
        theorem_traceability.get("theorem_output_scope_ledger_present")
        == proof_writing_card.get("theorem_output_scope_ledger_present")
        == proof_claim_traceability.get("remaining_claim_boundary", {}).get(
            "theorem_output_scope_ledger_present"
        )
        == proof_claim_traceability.get("summary", {}).get(
            "theorem_output_scope_ledger_present"
        )
        is True,
        "theorem output scope table not carried into strict proof audit",
    )
    checks.check(
        "Theorem output scope table present in manuscript/PDF text: `True`."
        in audit_md,
        "strict proof audit markdown missing theorem output scope table",
    )
    checks.check(
        theorem_traceability.get("reporting_map_ledger_present")
        == proof_writing_card.get("reporting_map_ledger_present")
        == proof_claim_traceability.get("remaining_claim_boundary", {}).get(
            "reporting_map_ledger_present"
        )
        == proof_claim_traceability.get("summary", {}).get(
            "reporting_map_ledger_present"
        )
        is True,
        "reporting-map/norm-equivalence table not carried into strict proof audit",
    )
    checks.check(
        "Reporting-map/norm-equivalence table present in manuscript/PDF text: `True`."
        in audit_md,
        "strict proof audit markdown missing reporting-map/norm-equivalence table",
    )
    checks.check(
        theorem_traceability.get("theorem_conclusion_scope_guard_present")
        == proof_writing_card.get("theorem_conclusion_scope_guard_present")
        == proof_claim_traceability.get("remaining_claim_boundary", {}).get(
            "theorem_conclusion_scope_guard_present"
        )
        == proof_claim_traceability.get("summary", {}).get(
            "theorem_conclusion_scope_guard_present"
        )
        is True,
        "scope-of-conclusion statement not carried into strict proof audit",
    )
    checks.check(
        "Scope-of-conclusion statement present in manuscript/PDF text: `True`."
        in audit_md,
        "strict proof audit markdown missing scope-of-conclusion statement",
    )
    checks.check(
        theorem_traceability.get("proof_strength_certificate_present")
        == proof_writing_card.get("proof_strength_certificate_present")
        == proof_claim_traceability.get("remaining_claim_boundary", {}).get(
            "proof_strength_certificate_present"
        )
        == proof_claim_traceability.get("summary", {}).get(
            "proof_strength_certificate_present"
        )
        is True,
        "proof-structure statement not carried into strict proof audit",
    )
    checks.check(
        "Proof-structure statement present in manuscript/PDF text: `True`."
        in audit_md,
        "strict proof audit markdown missing proof-structure statement",
    )
    checks.check(
        theorem_traceability.get("full_residual_bridge_present")
        == proof_writing_card.get("full_residual_bridge_present")
        == proof_claim_traceability.get("remaining_claim_boundary", {}).get(
            "full_residual_bridge_present"
        )
        == proof_claim_traceability.get("summary", {}).get("full_residual_bridge_present")
        is True,
        "full 132-row residual-defect bridge not carried into strict proof audit",
    )
    checks.check(
        "Full 132-row residual-defect bridge present in manuscript/PDF text: `True`."
        in audit_md,
        "strict proof audit markdown missing full residual bridge",
    )
    checks.check(
        theorem_traceability.get("anchor_evidence_sources") == expected_anchor_evidence_sources,
        "strict proof audit manuscript anchor evidence sources changed",
    )

    for token in [
        "3. BLieDF",
        "6. Convergence analysis",
        "Proof. Taylor expansion for Eq. (12)",
        "global error in the configuration variables",
        "Baker",
        "The local truncation errors of the k-step BLieDF method",
        "An error estimate for",
        "a coupled error recursion is obtained",
        "has the order of convergence p = k",
        "Appendix. Proof of Theorem 4",
    ]:
        checks.check(contains_normalized(ref_text, token), f"reference text missing token: {token}")

    reference_features = audit.get("reference_style_features", {})
    for key in [
        "bliedf_section_present",
        "convergence_section_present",
        "taylor_local_error_lemma_present",
        "lie_algebra_global_error_present",
        "bch_perturbation_present",
        "constrained_local_error_theorem_present",
        "constraint_multiplier_estimate_present",
        "coupled_error_recursion_present",
        "bdf_order_boundary_present",
        "appendix_proof_present",
    ]:
        checks.check(reference_features.get(key) is True, f"reference feature not recorded true: {key}")

    for tex, label in [(main_tex, "main manuscript"), (flat_tex, "flat manuscript")]:
        for token in [
            r"\label{ass:regularity}",
            r"\label{lem:endpoint-closure}",
            "velocity-level/KKT closure equations",
            "not the set of every raw endpoint",
            "raw position residual in that table is a separate monitor",
            "do not discharge the compact-tube endpoint raw-defect/right-inverse hypothesis",
            "Endpoint diagnostic-scope checkpoint",
            "order-fit row in Table~\\ref{tab:endpoint-closure-scaling} is not used",
            "fixed uniform compact-tube data before that table is read",
            "raw position monitor may have a different fitted slope without contradicting the lemma",
            "small raw position monitor would not discharge the velocity-level/KKT defect bound",
            "consistency diagnostic for the reported closure subsystem",
            r"\label{lem:stage-residual-defect}",
            r"F_{A,h}(Z_G+\Delta;y)",
            r"Q_h(\Delta)",
            r"\mathcal T_h(\Delta)",
            r"\rho_h=2M\|R_h\|",
            r"\le 2MC_Rh^7=C_Zh^7",
            "Ideal lift is not implementation discharge",
            "target-equation identity for the smooth lift",
            r"code-facing implemented \(O(h^7)\) bridge statement",
            r"C_E=4M_{E,\mathrm{ri}}C_{E,\mathrm{raw}}",
            r"\label{lem:inexact-newton}",
            r"C_N=2M_AM_N",
            r"C_Nc_\eta h^7",
            r"\label{lem:p6-reported-log-nonclosure}",
            "Reported solver logs are not a P6 proof",
            "not a compact-tube solver envelope",
            "It cannot calibrate",
            "prove branch membership",
            "diagnostic-grade solver information",
            "Branch-ball membership checkpoint",
            "two independent solver facts",
            r"\(B_{r_A}(Z_A)\)",
            r"\eta_h^{\rm tube}",
            "cannot replace the first",
            "not a theorem input unless",
            "same Gauss-predictor branch",
            "not counted as a larger local constant or as a lower-order inexact Newton step",
            "P6 conditional-instantiation checkpoint",
            "operational sufficient instantiation",
            "proof norm, row scaling, branch rule",
            "proof-norm stopping target",
            "reported-grid specialization",
            "hidden \\(h\\)-dependent row weights",
            "\\(h\\)-independent compact-tube norm equivalence",
            "finite-dimensional norm-equivalence constant after the explicit residual",
            "small residual in a different norm, branch, row scaling, or terminal solve is not an input",
            "sufficient instantiation rule, not a hidden empirical discharge",
            "does not prove a theorem-level solver-policy theorem",
            r"does not choose \(c_\eta\) from residual ratios",
            "does not prove global Newton convergence or remote-root exclusion",
            "P6 evidence-grade rule",
            "P6 has only one theorem-grade input",
            "predeclared same-branch residual envelope",
            "diagnostic-grade evidence only",
            "solver log can specialize a P6 hypothesis",
            "reported run may instantiate the theorem",
            "branch, tube, endpoint, proof-norm",
            "post-hoc filtered solver logs",
            "Theorem input-output reading rule",
            "No arrow in this chain is used backwards",
            "reported run may only specialize that theorem instance",
            "cannot retroactively change the theorem branch, norm, row scaling, or residual envelope",
            "Only one residual-value certificate is consumed in this theorem invocation",
            "future primitive/Taylor certificate may replace the accepted direct",
            "cannot be appended to the direct certificate to lower constants, remove",
            "Same-object theorem-composition criterion",
            "branch, row convention, norm, and endpoint map agree before the constants are chosen",
            "cannot be spliced into a single theorem instance",
            "jointly admissible tuple",
            "reference-style C1--C4 slots are admissible only when their outputs live in this same theorem object",
            "C1 local-error slot may feed the C3 perturbation slot only as the bridged residual value for the declared",
            "different typed object",
            "requires an explicit equivalence or transport lemma before it can enter the theorem composition",
            "Residual-bridge handoff",
            "P5 direct dynamic-row identity",
            "branch-solver scale are theorem-domain hypotheses",
            "The theorem closure below refers only to the direct residual-bridge/Kantorovich",
            "argument under the stated branch, endpoint, implementation, and solver-scale",
            "it does not prove a separate theorem for fixed production tolerances",
            "P7 residual-to-error route is deliberately not used",
            "the theorem is strong but conditional",
            "Reference-paper proof-method alignment",
            "Lie-group constrained-BDF convergence",
            "not the temporal finite-element comparator",
            "the comparator paper therefore have disjoint roles",
            "as a proof-obligation ordering template, not as a literal proof transfer",
            "no FullVA residual Taylor constant",
            "no one-step Gauss theorem",
            "formal Gauss order is used only for the reduced smooth Gauss branch",
            "FullVA enters the next proof slot through the fixed",
            "technical neighborhood and start-value assumptions",
            "retained compact-tube/branch domain, endpoint and solver-scale interfaces",
            "do not verify them retroactively",
            "technical-neighborhood and start-value clauses",
            "same-reduced-initial-state clauses, all fixed before any diagnostic table is read",
            "Reference-order Taylor discipline",
            "structural ordering discipline only; no Taylor estimate, primitive lift bound, or multiplier estimate is imported",
            "T2 full-map Taylor/Kantorovich estimate is established only for the fixed",
            "report numerical diagnostics after the theorem boundary is fixed",
            "Taylor-expansion local truncation estimate",
            "global configuration error in the Lie algebra",
            "Baker--Campbell--Hausdorff perturbation estimates",
            "holonomic-constraint differences, a multiplier estimate, and a coupled error",
            "not by importing the",
            "Reference no-estimate-transfer table",
            "No-estimate-transfer table for the Wieloch--Arnold constrained-BDF proof",
            "Forbidden estimate transfer",
            "Replacement in this proof",
            "No BLieDF Taylor constant, BDF \\(p=k\\) conclusion",
            "The BCH constants and global Lie-algebra recursion constants",
            "The reference multiplier-history estimate and hidden-constraint estimate",
            "The table is not a theorem input",
            "fixed object, smooth-branch insertion, local defect, and local-to-global",
            "proof-order transfer, not an estimate transfer",
            "the 132-row residual bridge used here",
            "does not import the reference paper's BLieDF hidden-constraint estimates",
            "Constraint-multiplier and reaction-output fence",
            "multiplier-error estimate; it is not a theorem",
            "stage multipliers",
            "They enter the accepted theorem only through the \\(132\\)-row residual bridge",
            "\\(h^6\\) trajectory estimate for multiplier histories",
            "separate multiplier/reaction reporting theorem",
            "not be read as a residual-to-error promotion or as a multiplier-order claim",
            "slot analogy is not symmetric",
            "BDF hidden-constraint estimate cannot replace the FullVA lower-pair",
            "FullVA direct residual bridge cannot be read as proving the reference",
            "Taylor-layer separation",
            "T1 is the standard smooth Gauss collocation local-truncation layer",
            "T2 is the theorem-level FullVA residual-map layer",
            "T3 is the separate primitive Newton--Euler Taylor route",
            "Only T1 and T2 are load-bearing",
            "Taylor accounting rule",
            "scheme, variables, comparison solution, and constants are fixed before",
            "all Taylor constants in the load-bearing lemmas are compact-tube constants",
            r"Taylor variable for T2 is \(\Delta=Z-Z_G\)",
            "zero Newton--Euler rows enter before the full-map Taylor expansion",
            "cannot use the T2 conclusion to prove those primitives",
            r"\label{lem:same-object-taylor-transport-gate}",
            "same mathematical object used here",
            "accepted FullVA stage variables",
            "not a T3 input, cannot certify any of the \\(162\\) primitive D5 Taylor",
            r"\label{lem:no-reverse-taylor-inference}",
            "global \\(O(h^6)\\) output estimate and finite diagnostics cannot be used backward",
            "do not prove the five open primitive lift or bilinear estimates",
            "Taylor-projection checkpoint",
            "aggregate estimate in the fixed block norm",
            "not a projection certificate for the 162 primitive scalar subterms",
            r"\Pi_{\rm prim}",
            "primitive projection/right-inverse",
            r"independent \(O(h^7)\) bounds for all primitive lift maps",
            "No such primitive projection/right-inverse is used",
            "aggregate residual bridge can close the T2 residual-defect input while the primitive-route status",
            "not additive proof evidence",
            "conditional templates cannot be spliced",
            "primitive-route theorem would have to prove the five open primitive obligations",
            "redo the residual-to-root, endpoint, solver, and global-transfer chain",
            "Route-exclusivity refinement",
            "one same-branch proof tuple",
            r"C_R^{\mathrm{T3}}h^7",
            "cannot be combined with the accepted direct \\(C_Rh^7\\) term to",
            "remove the retained P6 solver-scale condition",
            "use P7 residual-to-error rows",
            "consumes one residual-value certificate",
            "never mixes partial certificates from the direct and primitive routes",
            "Same-object direct-substitution calculation",
            r"R_h=F_{A,h}(Z_G;y)",
            r"F^{\rm dyn}_{A,h}(Z_G;y)=0",
            r"\Delta=-J_h^{-1}R_h-J_h^{-1}Q_h(\Delta)",
            r"\le M_EC_Zh^7=C_Ah^7",
            "No constant in this calculation is imported from",
            r"\label{prop:d5-primitive-taylor-conditional-implication}",
            r"\label{lem:d5-primitive-obligation-implication}",
            "This separate primitive-route lemma is a conditional finite implication",
            "Assume the five remaining primitive obligations",
            "every D5 Taylor subterm in the 36 Newton--Euler rows",
            "not an accepted primitive-route closure, not a PC2 input",
            "Common admissible-window checkpoint",
            "single same-branch admissibility rule",
            r"h_\star=",
            r"h_{\rm res}",
            r"h_{\rm rep}",
            r"2MC_Rh_0^7\le r",
            r"y(t_n)\in\mathcal D_h",
            "be admissible as exact-state inputs for that local-defect comparison",
            "compact-tube part of this domain is handled by the first-exit",
            "P6 solver-envelope membership remain retained transition hypotheses",
            "mean-value form of the residual",
            r"\label{lem:local-global-transfer}",
            r"C_{\rm red}=C_{\rm loc}\Gamma_s(T)",
            "Reference-style proof invariant",
            "fixed FullVA residual and branch",
            "same-branch residual defect at",
            "No BLieDF local-error constant",
            "not allowed to define an upstream arrow",
            "Reference-style recursion analogue",
            "The analogy is structural, not an estimate transfer",
            "lower-pair algebraic variables and stage multipliers have already been consumed inside the fixed",
            "There is no hidden multiplier recursion",
            "separate coupled output recursion",
            "Truncated first-exit recursion checkpoint",
            r"m_\ast=\min\{N,n_\ast\}",
            "evaluated only before the hypothetical first exit",
            "does not use the local estimates after a hypothetical exit",
            "contradicting the definition of the first exit",
            "only after this contradiction is the estimate extended to every reported index",
            "Time-augmentation convention for the transfer",
            r"\widehat y=(y,\tau)",
            r"\dot\tau=1",
            r"\tau\mapsto\tau+h",
            "time component contributes zero grid error",
            r"\varphi_{t+h,t}(y)",
            "no time-phase mismatch",
            "autonomous augmented semigroup identity",
            "Synchronized-time stability slice",
            "same reported input-time slice",
            r"\tau_n=t_n",
            r"\tau_{n+1}=t_{n+1}",
            "does not hide a time-registration error",
            "never compares states with different time phases",
            "time-shifted trajectory data",
            r"\Psi_{h,t_n}",
            "Convex chart-neighborhood checkpoint",
            "fixed convex coordinate neighborhood",
            r"\sup_{y\in U_K}\|D\mathcal R(y)\|\le C_{\mathcal R}",
            r"does not assume that \(K\) itself is convex",
            "segments between them stay inside \\(U_K\\)",
            "one fixed Euclidean chart",
            "not an atlas switch",
            "not a fitted norm-equivalence constant",
            "Stability-map binding checkpoint",
            "the endpoint-closed inexact accepted map",
            "same accepted compact branch and proof norm",
            "used only to decompose the one-step local defect",
            "their stability is not substituted into the global recursion",
            "same-branch stability scale for the accepted map",
            r"y_{n+1}=\Psi_h^{\mathrm{G6FVA}}(y_n)",
            "prevents a hidden map-switch",
            r"C_{qv}=C_{\mathcal R}C_{\rm red}",
            "Order-accounting checkpoint",
            r"local defect bounded by \(C_{\rm loc}h^7\)",
            r"N_h=O(h^{-1})",
            "theorem refers to the same-initial-state reported-grid \\(h^6\\) bound",
            "7.161/7.066 are downstream consistency evidence",
            "not a seventh-order theorem",
            "A stronger global-order statement would require a new theorem",
            r"\label{thm:g6fullva-order}",
            "discrete Gronwall argument",
        "retained as a separate primitive-route specification",
            "Taylor's formula with integral remainder",
            r"\label{lem:d5-p-state-ps3-full-residual-route}",
            "Direct-route state-block corollary; not primitive",
            "direct-route residual decomposition",
            "componentwise Newton--Euler equations on the same lifted stage",
            r"r^{\rm tr}_{sbc}(Z_G)=0",
            "D3 fixes the signs",
            "implemented unweighted scalar rows are exactly these component residuals",
            "not a certification of the primitive 162-subterm Taylor route",
            "no actual D5 primitive",
            r"36 \(h\)-weighted acceleration primitive terms",
            "not a complete source-paper temporal finite-element residual replacement",
        ]:
            checks.check(contains_normalized(tex, token), f"{label} missing strict proof token: {token}")
        checks.check(
            not contains_normalized(
                tex,
                r"\(y(t_n)\in K\) in the accepted compact sub-tube for each transition input",
            ),
            f"{label} still uses weak exact-state compact-tube theorem token",
        )

    proof_features = audit.get("manuscript_strict_proof_features", {})
    sidecar_scope = audit.get("sidecar_proof_gap_scope_audit", {})
    expected_sidecar_scope_count = len(sidecar_scope_entries)
    expected_sidecar_scope_ok_count = sum(
        1 for item in sidecar_scope_entries if item.get("scope_ok")
    )
    checks.check(
        sidecar_scope.get("legacy_key") == "proof_manifest_proof_gap_closed",
        "sidecar proof-gap legacy key changed",
    )
    checks.check(
        sidecar_scope.get("legacy_key_retained_for_schema_compatibility") is True,
        "sidecar proof-gap legacy compatibility marker missing",
    )
    checks.check(
        sidecar_scope.get("expected_scope") == DIRECT_ROUTE_SCOPE,
        "sidecar proof-gap expected scope changed",
    )
    checks.check(
        sidecar_scope.get("entry_count") == expected_sidecar_scope_count > 0,
        "sidecar proof-gap entry count changed",
    )
    checks.check(
        sidecar_scope.get("direct_route_scoped_count")
        == expected_sidecar_scope_ok_count
        == expected_sidecar_scope_count,
        "sidecar proof-gap legacy references are not all direct-route scoped",
    )
    checks.check(
        sidecar_scope.get("all_legacy_references_direct_route_scoped") is True,
        "sidecar proof-gap all-scoped marker missing",
    )
    for key in [
        "not_primitive_taylor_route_closure",
        "not_p6_solver_policy_closure",
        "not_p7_residual_to_error_closure",
        "not_source_policy_or_output_order_closure",
    ]:
        checks.check(sidecar_scope.get(key) is True, f"sidecar proof-gap nonclosure guard missing: {key}")
    recorded_entries = sidecar_scope.get("entries", [])
    checks.check(len(recorded_entries) == expected_sidecar_scope_count, "sidecar proof-gap entries not recorded")
    for recorded, expected in zip(recorded_entries, sidecar_scope_entries):
        checks.check(recorded.get("file") == expected.get("file"), "sidecar proof-gap entry file mismatch")
        checks.check(recorded.get("json_path") == expected.get("json_path"), "sidecar proof-gap entry path mismatch")
        checks.check(recorded.get("scope_ok") is True, "sidecar proof-gap recorded entry not scoped")
    checks.check(
        proof_features.get("strict_conditional_math_proof_present") is True,
        "strict conditional residual-bridge proof marker missing",
    )
    for label in ["main", "flat"]:
        feature_group = proof_features.get(label, {})
        for key in [
            "regularity_assumption",
            "endpoint_closure_lemma",
            "endpoint_functional_velocity_kkt",
            "endpoint_not_raw_diagnostics",
            "endpoint_raw_position_monitor_boundary",
            "endpoint_diagnostics_do_not_discharge_p2",
            "endpoint_diagnostic_scope_checkpoint",
            "endpoint_order_fit_not_hypothesis_source",
            "endpoint_fixed_compact_tube_data_before_table",
            "endpoint_raw_position_slope_no_contradiction",
            "endpoint_small_raw_position_no_discharge",
            "endpoint_table_consistency_diagnostic_only",
            "stage_residual_perturbation_lemma",
            "stage_taylor_expansion",
            "quadratic_remainder",
            "newton_kantorovich_absorption",
            "contraction_radius",
            "stage_error_bound",
            "stage_single_instance_requirement",
            "stage_same_fixed_residual_map_norm",
            "endpoint_closure_explicit_constant",
            "inexact_newton_lemma",
            "inexact_newton_endpoint_constant",
            "inexact_newton_scaled_endpoint_constant",
            "inexact_branch_ball_checkpoint",
            "inexact_two_independent_solver_facts",
            "inexact_iterate_certified_in_ball",
            "inexact_residual_envelope_fixed_norm",
            "inexact_residual_cannot_replace_membership",
            "inexact_log_not_theorem_input",
            "inexact_same_gauss_predictor_branch",
            "inexact_not_larger_constant_or_lower_order",
            "p6_conditional_instantiation_checkpoint",
            "p6_operational_sufficient_instantiation",
            "p6_fixed_norm_scaling_branch_rule",
            "p6_same_gauss_predictor_branch_certified",
            "p6_proof_norm_stopping_target",
            "p6_reported_grid_specialization",
            "p6_no_hidden_h_dependent_row_weights",
            "p6_h_independent_norm_equivalence",
            "p6_explicit_residual_h_factor_binding",
            "p6_small_residual_wrong_norm_not_input",
            "p6_sufficient_not_empirical_discharge",
            "p6_no_theorem_level_solver_evidence",
            "p6_no_residual_ratio_fitting",
            "p6_no_global_newton_remote_root",
            "p6_evidence_grade_rule",
            "p6_only_one_theorem_grade_input",
            "p6_predeclared_same_branch_residual_envelope",
            "p6_diagnostic_grade_evidence_only",
            "p6_log_specializes_not_creates",
            "proof_obligation_closure_narrative",
            "p5_direct_dynamic_row_identity",
            "p1p2p3_p4binding_p6_retained_conditions",
            "p7_residual_to_error_deliberately_not_used",
            "strong_but_conditional_theorem",
            "reference_proof_method_alignment",
            "reference_bdf_alignment",
            "reference_technical_startvalue_boundary",
            "reference_technical_assumptions_mapped_to_domain",
            "reference_no_retroactive_diagnostic_verification",
            "reference_technical_theorem_contract_boundary",
            "reference_technical_theorem_contract_replacement",
            "reference_taylor_local_error",
            "reference_lie_algebra_global_error",
            "reference_bch_perturbation",
            "reference_coupled_error_recursion",
            "reference_no_bdf_import",
            "reference_no_estimate_transfer_ledger",
            "reference_no_estimate_transfer_caption",
            "reference_forbidden_transfer_column",
            "reference_replacement_column",
            "reference_no_bdf_premise",
            "reference_no_bch_constants",
            "reference_no_multiplier_history_import",
            "reference_table_not_theorem_input",
            "reference_fixed_object_sequence",
            "reference_fullva_translation_checkpoint",
            "reference_partial_order_obligations",
            "reference_r1_fixed_discrete_object",
            "reference_r2_smooth_branch_same_object",
            "reference_r3_fixed_object_defect_conversion",
            "reference_r4_stability_after_local_defect",
            "reference_right_hand_independent",
            "reference_does_not_repair_failed_lemma",
            "reference_dependency_graph_not_premise",
            "reference_constrained_dae_slot_checkpoint",
            "reference_two_distinct_dae_slots",
            "reference_constraint_difference_multiplier_slot",
            "reference_local_defect_slot_full_bridge",
            "reference_constrained_dae_slot_fullva",
            "reference_multipliers_stage_unknowns_not_histories",
            "reference_no_bypass_constraint_layer",
            "reference_slot_analogy_not_symmetric",
            "reference_bdf_hidden_constraint_not_fullva_certificate",
            "reference_direct_bridge_not_multiplier_history_theorem",
            "method_endpoint_p2_controlled",
            "method_endpoint_diagnostics_separate",
            "theorem_named_clauses",
            "theorem_p1_smooth_lift_clause",
            "theorem_p2_endpoint_inverse_clause",
            "theorem_p3_implementation_clause",
            "theorem_p4_only_96_rows",
            "theorem_p5_only_direct_36_rows",
            "theorem_p6_only_solver_envelope",
            "theorem_clauses_not_inferred_from_diagnostics",
            "theorem_input_output_reading_rule",
            "theorem_no_backward_arrows",
            "theorem_reported_run_only_specializes",
            "theorem_no_retroactive_instance_change",
            "theorem_one_residual_certificate",
            "theorem_future_t3_same_tuple_replacement",
            "theorem_no_append_lower_remove_promote",
            "proof_gap_token_scope_checkpoint",
            "proof_gap_token_direct_pc2_only",
            "proof_gap_token_not_p6_p7_primitive",
            "proof_gap_token_not_extra_assumption",
            "constraint_multiplier_reaction_output_fence",
            "multiplier_step_not_theorem_output",
            "stage_multipliers_algebraic_unknowns",
            "multipliers_enter_only_through_residual_bridge",
            "no_multiplier_reaction_h6_estimate",
            "separate_multiplier_reaction_theorem_required",
            "reaction_residuals_not_multiplier_order_claim",
            "taylor_layer_separation_checkpoint",
            "taylor_t1_gauss_layer",
            "taylor_t2_full_residual_map_layer",
            "taylor_t3_optional_primitive_route",
            "taylor_t1_t2_load_bearing",
            "taylor_accounting_rule",
            "taylor_fixed_before_expansion",
            "taylor_constants_compact_tube_only",
            "taylor_t2_variable_delta",
            "taylor_zero_rows_before_full_map",
            "taylor_no_t2_to_prove_primitives",
            "taylor_same_object_transport_gate",
            "taylor_same_mathematical_object",
            "taylor_transport_fullva_stage_variables",
            "taylor_transport_not_t3_input",
            "taylor_no_reverse_inference_lemma",
            "taylor_no_reverse_global_estimate",
            "taylor_no_reverse_does_not_prove_primitives",
            "taylor_projection_checkpoint",
            "taylor_aggregate_fixed_block_norm",
            "taylor_not_projection_certificate_162",
            "taylor_primitive_projection_operator",
            "taylor_projection_right_inverse_needed",
            "taylor_independent_primitive_lift_bounds",
            "taylor_no_projection_right_inverse_used",
            "taylor_t2_closed_while_primitive_separate",
            "taylor_counts_not_additive_proof_evidence",
            "taylor_templates_not_spliced_with_pc2",
            "taylor_primitive_route_must_prove_five_obligations",
            "taylor_primitive_route_must_redo_chain",
            "taylor_route_exclusivity_refinement",
            "taylor_route_same_branch_tuple",
            "taylor_route_future_t3_own_cr",
            "taylor_route_cannot_lower_constants",
            "taylor_route_cannot_remove_p6",
            "taylor_route_cannot_promote_p7",
            "taylor_route_one_residual_certificate",
            "taylor_route_never_mixes_partial",
            "common_admissible_window_checkpoint",
            "single_same_branch_admissibility_rule",
            "common_h_star_window",
            "common_window_res_rep_disambiguated",
            "common_window_reporting_symbol",
            "kantorovich_common_window_restrictions",
            "exact_comparison_inputs_in_accepted_domain",
            "exact_state_defect_domain_invocation",
            "compact_tube_part_first_exit",
            "branch_solver_parts_retained",
            "stability_map_binding_checkpoint",
            "stability_map_is_g6fullva",
            "stability_same_branch_proof_norm",
            "local_global_truncated_first_exit_checkpoint",
            "local_global_truncated_index",
            "local_global_truncated_only_before_exit",
            "local_global_no_post_exit_estimates",
            "local_global_exit_contradiction",
            "local_global_extend_after_exit_excluded",
            "local_global_time_augmentation_checkpoint",
            "local_global_augmented_chart",
            "local_global_tau_dot_one",
            "local_global_exact_time_advance",
            "local_global_time_zero_error",
            "local_global_two_parameter_flow",
            "local_global_no_time_phase_mismatch",
            "local_global_augmented_semigroup_identity",
            "local_global_synchronized_time_slice",
            "local_global_same_input_time_slice",
            "local_global_tau_n_equals_t_n",
            "local_global_exact_next_time",
            "local_global_no_time_registration_error",
            "local_global_no_different_time_phases",
            "local_global_no_time_shifted_fit",
            "local_global_time_indexed_map",
            "reporting_convex_chart_checkpoint",
            "reporting_fixed_convex_neighborhood",
            "reporting_u_k_derivative_supremum",
            "reporting_no_convex_k_assumption",
            "reporting_segments_inside_uk",
            "reporting_one_euclidean_chart",
            "reporting_no_atlas_switch",
            "reporting_no_fitted_norm_equivalence",
            "exact_stage_maps_local_defect_only",
            "no_exact_stage_stability_substitution",
            "stability_constant_accepted_map",
            "single_g6fullva_recurrence",
            "no_hidden_map_switch",
            "order_accounting_checkpoint",
            "order_accounting_local_h7_global_h6",
            "order_accounting_nh_inverse",
            "order_accounting_sixth_order_grid_bound",
            "order_accounting_observed_slopes_downstream",
            "order_accounting_not_seventh_order",
            "order_accounting_stronger_claim_requires_new_theorem",
            "mean_value_residual",
            "local_global_transfer_lemma",
            "local_global_reduced_grid_constant",
            "qv_reporting_explicit_constant",
            "conditional_order_theorem",
            "discrete_gronwall_step",
            "primitive_taylor_route_retained",
            "integral_remainder_primitive",
            "p_state_ps3_full_residual_route",
            "direct_route_state_block_corollary",
            "direct_route_residual_decomposition",
            "dynamic_row_component_balance_expansion",
            "dynamic_row_residual_zero_substitution",
            "dynamic_row_virtual_work_sign_binding",
            "dynamic_row_implemented_scalar_binding",
            "primitive_162_subterm_boundary",
            "primitive_taylor_bounds_not_established",
            "h_weighted_acceleration_terms_insufficient",
            "proof_boundary_not_source_replacement",
        ]:
            checks.check(feature_group.get(key) is True, f"{label} strict proof feature not true: {key}")

    boundary = audit.get("two_layer_proof_boundary", {})
    checks.check(boundary.get("b1_status") == b1.get("status") == "closed", "B1 must be closed")
    checks.check(boundary.get("b3_status") == b3.get("status") == "closed", "B3 direct route must be closed")
    checks.check(
        boundary.get("b3_direct_proof_review_passed") is True,
        "B3 direct proof review progress marker missing",
    )
    checks.check(
        boundary.get("b3_closed_by_direct_proof_review") is True,
        "B3 direct proof review closure marker missing",
    )
    checks.check(
        boundary.get("b1_ad_expanded_implementation_oracle_still_open") is False,
        "B1 implementation-oracle open marker should be false",
    )
    checks.check(
        boundary.get("primitive_dynamic_symbolic_oracle_complete") is False,
        "primitive/global dynamic symbolic oracle boundary changed",
    )
    checks.check(
        boundary.get("b1_closed_by_ad_expanded_symbolic_certificate") is True,
        "B1 AD-expanded symbolic closure marker missing",
    )
    checks.check(
        boundary.get("b1_ad_expanded_symbolic_certificate_schema")
        == b1_ad_expanded_closure.get("schema")
        == "b1-ad-expanded-symbolic-oracle-closure-certificate-v1",
        "B1 AD-expanded symbolic certificate schema changed",
    )
    checks.check(
        boundary.get("b1_ad_expanded_symbolic_certificate_status")
        == "ad_expanded_symbolic_oracle_closed_without_o_h7_overclaim",
        "B1 AD-expanded symbolic certificate status changed",
    )
    checks.check(
        boundary.get("b1_ad_expanded_symbolic_oracle_closure")
        == b1_ad_expanded_closure.get("ad_expanded_symbolic_oracle_closure")
        is True,
        "B1 AD-expanded symbolic oracle not closed",
    )
    checks.check(
        boundary.get("b1_ad_expanded_symbolic_oracle_closed_cells")
        == b1_ad_expanded_closure.get("ad_expanded_symbolic_oracle_closed_cells")
        == 4752,
        "B1 AD-expanded symbolic derivative-cell count changed",
    )
    checks.check(boundary.get("proof_contract_status") == proof_contract.get("status"), "proof contract status mismatch")
    checks.check(boundary.get("proof_closure_status") == proof_closure.get("status"), "proof closure status mismatch")
    checks.check(boundary.get("proof_style_status") == proof_style.get("status"), "proof style status mismatch")
    checks.check(
        boundary.get("contract_stage_residual_O_h7_implementation_defect_proved")
        is theorem_contract.get("stage_residual_O_h7_implementation_defect_proved")
        is True,
        "contract-level implementation proof boundary changed",
    )
    checks.check(
        boundary.get("direct_route_stage_residual_O_h7")
        is closure_state.get("stage_residual_O_h7_implementation_defect_proved")
        is True,
        "direct-route stage residual closure marker changed",
    )
    checks.check(
        boundary.get("direct_route_dynamic_zero_rows")
        == closure_evidence.get("newton_euler_d5_direct_substitution_dynamic_zero_rows")
        == 36,
        "direct-route dynamic row count changed",
    )
    checks.check(
        boundary.get("direct_route_full_stage_rows")
        == closure_evidence.get("newton_euler_d5_direct_substitution_full_stage_rows")
        == 132,
        "direct-route full row count changed",
    )
    checks.check(
        boundary.get("dynamic_symbolic_oracle_complete")
        is theorem_contract.get("dynamic_symbolic_oracle_complete")
        is False,
        "dynamic symbolic oracle boundary changed",
    )
    checks.check(
        boundary.get("runtime_formula_row_oracle_complete")
        is full_formula_oracle.get("runtime_formula_row_oracle_complete")
        is True,
        "runtime formula row oracle marker changed",
    )
    checks.check(
        boundary.get("runtime_ad_oracle_complete")
        is formula_ad_oracle.get("runtime_ad_oracle_complete")
        is True,
        "runtime AD oracle marker changed",
    )
    checks.check(
        boundary.get("independent_symbolic_row_oracle_complete")
        is dynamic_boundary.get("independent_symbolic_row_oracle_complete")
        is False,
        "independent symbolic row oracle boundary changed",
    )
    checks.check(boundary.get("dynamic_row_oracle_status") == dynamic_oracle.get("status"), "dynamic oracle status mismatch")
    checks.check(
        "strict_implementation_proof_complete" not in boundary,
        "generic strict implementation proof token must be route-scoped",
    )
    checks.check(
        boundary.get("direct_route_strict_residual_bridge_kantorovich_proof_complete") is True,
        "active direct residual-bridge/Kantorovich proof should be complete",
    )
    checks.check(
        boundary.get("direct_route_strict_proof_scope")
        == "active_direct_residual_bridge_kantorovich_route_for_B1_B3",
        "direct-route strict proof scope changed",
    )
    checks.check(
        boundary.get("symbolic_primitive_route_strict_implementation_proof_complete") is False,
        "symbolic/primitive implementation lane must remain open",
    )
    checks.check(
        boundary.get("symbolic_primitive_route_scope")
        == "conditional_schema_symbolic_primitive_route_not_active_pc2",
        "symbolic/primitive proof scope changed",
    )
    checks.check(boundary.get("two_layer_boundary_consistent") is True, "two-layer boundary consistency failed")

    primitive = audit.get("primitive_taylor_route", {})
    checks.check(primitive.get("rows") == d5_summary.get("dynamic_rows") == 36, "primitive Taylor row count changed")
    checks.check(primitive.get("terms") == d5_summary.get("term_rows") == 162, "primitive Taylor term count changed")
    checks.check(
        primitive.get("conditional_rows")
        == d5_summary.get("conditional_dynamic_rows_under_open_primitive_assumptions")
        == 36,
        "conditional primitive row count changed",
    )
    checks.check(
        primitive.get("conditional_terms")
        == d5_summary.get("conditional_term_bounds_under_open_primitive_assumptions")
        == 162,
        "conditional primitive term count changed",
    )
    checks.check(primitive.get("actual_rows_proved") == d5_summary.get("actual_dynamic_rows_proved") == 0, "primitive rows overclaimed")
    checks.check(primitive.get("actual_terms_proved") == d5_summary.get("actual_taylor_bounds_proved") == 0, "primitive terms overclaimed")
    checks.check(
        primitive.get("open_primitive_assumptions")
        == d5_summary.get("open_primitive_assumption_count")
        == 5,
        "open primitive assumption count changed",
    )
    checks.check(
        primitive.get("proved_primitive_count") == d5_summary.get("proved_primitive_count") == 1,
        "proved primitive count changed",
    )
    checks.check(
        primitive.get("strict_taylor_reduction_terms")
        == term_budget_summary.get("strict_taylor_reduction_terms")
        == 162,
        "strict Taylor reduction term count changed",
    )
    checks.check(
        primitive.get("anti_circular_taylor_terms")
        == term_budget_summary.get("anti_circular_taylor_terms")
        == 162,
        "anti-circular Taylor term count changed",
    )
    checks.check(
        primitive.get("terms_with_open_primitive_blockers")
        == term_budget_summary.get("terms_with_open_primitive_blockers")
        == 162,
        "open primitive Taylor blocker count changed",
    )
    checks.check(
        primitive.get("unweighted_acceleration_blocked_terms")
        == term_budget_summary.get("unweighted_acceleration_blocked_terms")
        == 36,
        "unweighted acceleration blocker count changed",
    )
    checks.check(
        primitive.get("h_weighted_acceleration_sufficient_terms")
        == term_budget_summary.get("h_weighted_acceleration_sufficient_terms")
        == 0,
        "h-weighted acceleration incorrectly became sufficient",
    )
    checks.check(
        primitive.get("h_weighted_acceleration_insufficient_terms")
        == term_budget_summary.get("h_weighted_acceleration_insufficient_terms")
        == 36,
        "h-weighted acceleration insufficiency count changed",
    )
    checks.check(
        primitive.get("primitive_blocker_usage")
        == term_budget_summary.get("primitive_blocker_usage")
        == {
            "P_acceleration_lift": 36,
            "P_geometry_lift": 36,
            "P_gyroscopic_lift": 18,
            "P_multiplier_lift": 72,
            "P_state_lift": 126,
        },
        "primitive blocker usage changed",
    )
    checks.check(
        primitive.get("dependency_graph_recorded")
        == primitive_dependency_graph.get("graph_recorded")
        is True,
        "primitive dependency graph marker changed",
    )
    checks.check(
        primitive.get("root_lift_primitives")
        == primitive_dependency_graph.get("root_lift_primitives")
        == ["P_state", "P_acc"],
        "primitive root lift list changed",
    )
    checks.check(
        primitive.get("root_dependent_primitives")
        == primitive_dependency_graph.get("root_dependent_primitives")
        == ["P_lambda"],
        "primitive root-dependent list changed",
    )
    checks.check(
        primitive.get("conditional_downstream_primitives")
        == primitive_dependency_graph.get("conditional_downstream_primitives")
        == ["P_geom", "P_gyro"],
        "primitive downstream list changed",
    )
    checks.check(
        primitive.get("dependency_edge_count")
        == len(primitive_dependency_graph.get("dependency_edges", []))
        == 5,
        "primitive dependency edge count changed",
    )
    checks.check(
        primitive.get("closure_sequence")
        == primitive_dependency_graph.get("closure_sequence")
        == ["P_state", "P_acc", "P_lambda", "P_geom", "P_gyro"],
        "primitive closure sequence changed",
    )
    checks.check(
        primitive.get("root_lift_term_row_total")
        == primitive_gap_summary.get("root_lift_term_row_total")
        == 162,
        "primitive root lift term-row total changed",
    )
    checks.check(
        primitive.get("root_dependent_term_row_total")
        == primitive_gap_summary.get("root_dependent_term_row_total")
        == 72,
        "primitive root-dependent term-row total changed",
    )
    checks.check(
        primitive.get("conditional_downstream_term_row_total")
        == primitive_gap_summary.get("conditional_downstream_term_row_total")
        == 54,
        "primitive downstream term-row total changed",
    )
    checks.check(
        isinstance(primitive.get("minimal_next_subproofs"), list)
        and [item.get("primitive") for item in primitive.get("minimal_next_subproofs", [])]
        == ["P_state", "P_acc", "P_lambda"],
        "primitive minimal next subproofs changed",
    )
    checks.check("pc2_closed" not in primitive, "generic primitive PC2 token must be route-scoped")
    checks.check(primitive.get("primitive_route_pc2_closed") is d5_taylor.get("pc2_closed") is False, "primitive route must not close PC2")
    d5_route_separation = d5_taylor.get("route_separation", {})
    for key_name in [
        "conditional_templates_not_additive_proof_evidence",
        "conditional_templates_not_spliced_with_direct_pc2_bridge",
        "direct_pc2_bridge_does_not_close_primitive_route",
        "primitive_route_must_prove_five_uniform_lift_primitives",
        "primitive_route_must_redo_residual_to_root_endpoint_solver_global_chain",
    ]:
        checks.check(
            primitive.get(key_name) is d5_route_separation.get(key_name) is True,
            f"D5 route-separation marker missing from strict proof audit: {key_name}",
        )
    checks.check(
        primitive.get("route_separation_scope")
        == d5_route_separation.get("route_separation_scope")
        == (
            "conditional_taylor_templates_are_schema_only_until_their_own_"
            "primitive_lifts_and_full_perturbation_chain_close"
        ),
        "D5 route-separation scope changed",
    )

    strict_standard = audit.get("direct_residual_bridge_kantorovich_submission_standard", {})
    strict_direct = audit.get("strict_direct_residual_bridge_submission_standard", {})
    checks.check(
        strict_standard.get("manifest_status")
        == manifest_direct_standard.get("status")
        == "closed_by_direct_residual_bridge_kantorovich_route_primitive_taylor_conditional_schema_open",
        "direct residual-bridge submission-standard status changed",
    )
    checks.check(
        strict_standard.get("required_pc2_route")
        == manifest_direct_standard.get("required_pc2_route")
        == "direct_residual_bridge_kantorovich_route",
        "direct residual-bridge required PC2 route changed",
    )
    checks.check(
        strict_standard.get("satisfied") is manifest_direct_standard.get("satisfied") is True,
        "direct residual-bridge route not satisfied",
    )
    checks.check(
        strict_standard.get("proof_gap_closed_under_active_direct_residual_bridge_standard")
        is manifest_direct_standard.get("proof_gap_closed_under_active_direct_residual_bridge_standard")
        is True,
        "direct residual-bridge proof gap not closed by direct route",
    )
    checks.check(
        strict_standard.get("not_primitive_162_term_taylor_closure")
        is manifest_direct_standard.get("not_primitive_162_term_taylor_closure")
        is True,
        "direct residual-bridge primitive-route scope flag missing",
    )
    checks.check(
        strict_standard.get("direct_substitution_supplies_active_pc2_residual_bridge")
        is manifest_direct_standard.get("direct_substitution_supplies_active_pc2_residual_bridge")
        is True,
        "direct residual evidence not accepted as active PC2 residual-bridge input",
    )
    checks.check(
        strict_standard.get("current_gate_b3_status") == b3.get("status") == "closed",
        "current B3 status link changed",
    )
    checks.check(
        strict_standard.get("b3_should_close_under_active_direct_residual_bridge_standard") is True,
        "B3 direct residual-bridge closure flag missing",
    )
    checks.check(
        strict_standard.get("direct_residual_bridge_kantorovich_route_closed")
        is manifest_direct_standard.get("direct_residual_bridge_kantorovich_route_closed")
        is True,
        "direct residual-bridge/Kantorovich route closure marker missing",
    )
    checks.check(
        strict_standard.get("active_standard_name") == "strict_direct_residual_bridge_submission_standard"
        and "legacy_key_retained_for_validator_compatibility" not in strict_standard,
        "strict standard active name missing or stale legacy key still present",
    )
    checks.check(
        strict_direct.get("required_pc2_route")
        == manifest_strict_direct.get("required_pc2_route")
        == "direct_residual_bridge_kantorovich_route"
        and strict_direct.get("satisfied") is True,
        "strict direct residual-bridge alias changed",
    )
    checks.check(
        strict_standard.get("primitive_route_required_for_b3_closure")
        is manifest_direct_standard.get("primitive_route_required_for_b3_closure")
        is False,
        "primitive route should be diagnostic for B3 closure",
    )
    checks.check(
        strict_standard.get("actual_taylor_bounds_proved")
        == manifest_direct_standard.get("actual_taylor_bounds_proved")
        == 0,
        "strict Taylor actual proof count changed",
    )
    checks.check(
        strict_standard.get("open_taylor_bound_terms")
        == manifest_direct_standard.get("open_taylor_bound_terms")
        == 162,
        "strict Taylor open term count changed",
    )
    checks.check(
        strict_standard.get("terms_with_open_primitive_blockers")
        == manifest_direct_standard.get("terms_with_open_primitive_blockers")
        == 162,
        "strict Taylor open primitive blocker count changed",
    )
    checks.check(
        strict_standard.get("open_primitive_count")
        == manifest_direct_standard.get("open_primitive_count")
        == 5,
        "strict Taylor open primitive count changed",
    )
    checks.check(
        strict_standard.get("h_weighted_acceleration_sufficient_terms")
        == manifest_direct_standard.get("h_weighted_acceleration_sufficient_terms")
        == 0,
        "strict Taylor h-weighted acceleration unexpectedly sufficient",
    )
    checks.check(
        strict_standard.get("h_weighted_acceleration_insufficient_terms")
        == manifest_direct_standard.get("h_weighted_acceleration_insufficient_terms")
        == 36,
        "strict Taylor h-weighted acceleration insufficiency count changed",
    )
    for token in [
        "## Direct-Route Residual-Bridge Proof Contract",
        "Direct residual-bridge proof contract satisfied: `True`.",
        "Direct PC2 proof gap closed under active residual-bridge contract: `True`.",
        "Direct substitution supplies the active PC2 residual-bridge proof input: `True`.",
        "B3 should close under active residual-bridge standard: `True`.",
        "Direct-route residual decomposition boundary present: `True`.",
        "Taylor no-splicing boundary present: `True/True/True/True`.",
        "Taylor same-object/no-reverse boundary present: `True/True/True/True/True/True/True/True/True`.",
        "Taylor route-exclusivity refinement present: `True/True/True/True/True/True/True/True`.",
        "Taylor finite-implication formal statements present: `True/True/True/True/True/True`.",
        "Primitive 162-subterm Taylor route not certified: `True`.",
        "Primitive Taylor bounds not established on theorem route: `True`.",
        "36 h-weighted acceleration primitive terms remain insufficient: `True`.",
        "D5 route-separation locks: `True/True/True/True/True`.",
        "D5 route-separation scope: `conditional_taylor_templates_are_schema_only_until_their_own_primitive_lifts_and_full_perturbation_chain_close`.",
    ]:
        checks.check(token in audit_md, f"strict proof audit markdown missing token: {token}")
    checks.check("proof_gap_closed" not in primitive, "generic primitive proof-gap token must be route-scoped")
    checks.check(primitive.get("primitive_route_proof_gap_closed") is d5_taylor.get("proof_gap_closed") is False, "primitive route proof gap boundary changed")
    checks.check(
        "stage_residual_O_h7_implementation_defect_proved" not in primitive,
        "generic primitive stage-residual token must be route-scoped",
    )
    checks.check(
        primitive.get("primitive_route_stage_residual_O_h7_implementation_defect_proved")
        is d5_taylor.get("stage_residual_O_h7_implementation_defect_proved")
        is False,
        "primitive route implementation proof boundary changed",
    )

    direct_corollary = audit.get("direct_route_ps3_corollary", {})
    d5_full_summary = d5_p_state_ps3_full_route.get("summary", {})
    checks.check(
        direct_corollary.get("schema")
        == d5_p_state_ps3_full_route.get("schema")
        == "d5-p-state-ps3-full-residual-route-certificate-v1",
        "direct-route PS3 certificate schema missing",
    )
    checks.check(
        direct_corollary.get("certificate_closed")
        == d5_full_summary.get("full_residual_route_certificate_closed")
        is True,
        "direct-route certificate closure not linked",
    )
    checks.check(
        direct_corollary.get("direct_route_ps3_input_closed")
        == d5_full_summary.get("direct_route_ps3_input_closed")
        is True,
        "direct-route PS3 input closure not linked",
    )
    checks.check(
        direct_corollary.get("direct_route_state_lift_rate_closed")
        == d5_full_summary.get("direct_route_state_lift_rate_closed")
        is True,
        "direct-route state lift closure not linked",
    )
    checks.check(
        direct_corollary.get("direct_route_h_weighted_acceleration_input_closed")
        == d5_full_summary.get("direct_route_h_weighted_acceleration_input_closed")
        is True,
        "direct-route h-acceleration closure not linked",
    )
    checks.check(
        direct_corollary.get("strict_proof_steps_closed")
        == d5_full_summary.get("strict_proof_steps_closed")
        == 4,
        "direct-route strict proof closed count changed",
    )
    checks.check(
        direct_corollary.get("strict_proof_steps_total")
        == d5_full_summary.get("strict_proof_steps_total")
        == 4,
        "direct-route strict proof total count changed",
    )
    checks.check(
        direct_corollary.get("primitive_route_closed")
        == d5_full_summary.get("primitive_route_closed")
        is False,
        "direct-route corollary unexpectedly closes primitive route",
    )
    checks.check(
        direct_corollary.get("primitive_route_induced_taylor_bounds_proved")
        == d5_full_summary.get("primitive_route_induced_taylor_bounds_proved")
        == 0,
        "direct-route corollary overclaims primitive Taylor bounds",
    )
    checks.check(
        direct_corollary.get("certifies_primitive_taylor_route")
        == d5_p_state_ps3_full_route.get("certifies_primitive_taylor_route")
        is False,
        "direct-route corollary overclaims primitive Taylor route",
    )
    checks.check(
        direct_corollary.get("uses_velocity_collocation_h_inverse_route") is False,
        "direct-route corollary uses velocity-collocation shortcut",
    )
    checks.check(
        direct_corollary.get("uses_finite_probe_as_proof") is False,
        "direct-route corollary uses finite probe as proof",
    )

    for token in [
        "Status: **strict conditional residual-bridge proof audited; global proof-package submission not ready**.",
        "Here `submission_ready=false` is scoped to the strict-proof/global proof-package boundary,",
        "not to the separate narrowed-claim package decision.",
        "Strict conditional residual-bridge proof present: `True`.",
        "BLieDF/convergence sections present: `True/True`.",
        "Taylor local-error lemma and constrained local-error theorem present: `True/True`.",
        "Lie-algebra global-error and BCH perturbation structure present: `True/True`.",
        "Constraint multiplier estimate and coupled recursion present: `True/True`.",
        "BDF order boundary and appendix proof present: `True/True`.",
        "Reference role-separation locks present: `True/True/True/True/True/True`.",
        "Reference technical/start-value boundary present: `True/True/True/True/True`.",
        "Reference proof-order transfer locks present: `True/True/True`.",
        "Constraint-multiplier/reaction output fence present: `True/True/True/True/True/True/True`.",
        "Residual-bridge handoff present: `True/True/True/True/True`.",
        "Reference-to-FullVA translation map present: `True/True/True/True/True/True/True/True/True`.",
        "Reference constrained-DAE slot map present: `True/True/True/True/True/True/True/True/True/True`.",
        "Named theorem-domain clauses present: `True/True/True/True/True/True/True/True/True/True`.",
        "Theorem input-output direction locks present: `True/True/True/True`.",
        "Theorem residual-certificate exclusivity locks present: `True/True/True`.",
        "Proof-gap closure scope locks present: `True/True/True/True`.",
        f"D5 sidecar proof-gap legacy keys direct-route scoped: `{expected_sidecar_scope_ok_count}/{expected_sidecar_scope_count}`; primitive/P6/P7/source-policy nonclosure retained: `True/True/True/True`.",
        "Same-object closure locks present: `True/True/True/True`.",
        "Same-object typed-slot composition locks present: `True/True/True/True`.",
        "Taylor accounting rule present: `True/True/True/True/True/True`.",
        "Taylor same-object/no-reverse boundary present: `True/True/True/True/True/True/True/True/True`.",
        "Taylor projection checkpoint present: `True/True/True/True/True/True/True/True`.",
        "Taylor finite-implication formal statements present: `True/True/True/True/True/True`.",
        "Same-object direct-substitution calculation present: `True/True/True/True/True/True`.",
        "Endpoint diagnostic-scope checkpoint present: `True/True/True/True/True/True`.",
        "Stage single-instance locks present: `True/True`.",
        "Inexact Newton branch-ball checkpoint present: `True/True/True/True/True/True/True/True`.",
        "P6 conditional-instantiation checkpoint present: `True/True/True/True/True/True/True/True/True/True`.",
        "P6 evidence-grade rule present: `True/True/True/True/True`.",
        "P6 proof-norm/no-reweighting checkpoint present: `True/True/True/True`.",
        "Stability-map binding checkpoint present: `True/True/True/True/True/True/True/True`.",
        "Reference-style proof invariant present: `True/True/True/True/True`.",
        "Reference-style recursion analogue present: `True/True/True/True/True`.",
        "Truncated first-exit recursion checkpoint present: `True/True/True/True/True/True`.",
        "Time-augmentation local-to-global checkpoint present: `True/True/True/True/True/True/True/True`.",
        "Synchronized-time stability slice present: `True/True/True/True/True/True/True/True`.",
        "Reporting-map convex chart checkpoint present: `True/True/True/True/True/True/True/True`.",
        "Order-accounting checkpoint present: `True/True/True/True/True/True/True`.",
        "Direct-route state-block corollary present: `True`.",
        "Theorem labels/boundary/mapped: `True/True/True`.",
        "Proof dependency/traceability/dynamic matrix: `True/True/True`.",
        "Primitive-route and residual scope boundaries: `True/True`.",
        "Eta condition/closure and fixed-tolerance proof: `True/False/False`.",
        "Residual/source-policy-full-TFE not promoted: `True/True`; no-state-change `True`.",
        "Proof-closure manuscript anchor map: `True`; label anchors `24`; theorem-interface/P7-output-boundary anchors `7`; IDs `P1,P2,P3,P4,P5,P6,P7`; proof-claim map match `True`.",
        "Reader-facing theorem-interface split: theorem interfaces `P1--P6`; P7 is an output nonclaim/residual-to-error boundary anchor, not a theorem premise.",
        "Anchor evidence sources: `PROOF_CLOSURE_MANIFEST.json,PROOF_CLAIM_TRACEABILITY_AUDIT.json`.",
        "B3 closed by direct proof review: `True`.",
        "B3 direct proof review passed: `True`.",
        "B1 AD-expanded implementation oracle still open: `False`.",
        "Primitive/global dynamic symbolic oracle complete: `False`.",
        "B1 closed by AD-expanded symbolic certificate: `True`.",
        "B1 AD-expanded symbolic closure/cells: `True/4752`.",
        "Contract-level implementation defect proved: `True`.",
        "Direct-route stage residual O(h^7): `True`.",
        "Direct residual-bridge/Kantorovich proof complete: `True`.",
        "Symbolic/primitive implementation proof complete: `False`.",
        "Dynamic symbolic oracle complete: `False`.",
        "Two-layer boundary consistent: `True`.",
        "PC2 closed by primitive route: `False`.",
        "Primitive-route proof gap closed: `False`.",
        "Primitive-route stage residual O(h^7) proved: `False`.",
        "Primitive/Taylor reductions: `162/162`.",
        "Anti-circular Taylor terms: `162/162`.",
        "Terms blocked by open primitives: `162/162`.",
        "Unweighted acceleration blockers: `36/36`.",
        "h-weighted acceleration sufficient terms: `0`.",
        "Primitive dependency graph recorded: `True`.",
        "Root lift primitives: `['P_state', 'P_acc']`.",
        "Root-dependent conditional primitives: `['P_lambda']`.",
        "Conditional downstream primitives: `['P_geom', 'P_gyro']`.",
        "Dependency edges: `5`.",
        "Closure sequence: `['P_state', 'P_acc', 'P_lambda', 'P_geom', 'P_gyro']`.",
        "Root, root-dependent, and downstream term-row totals: `162/72/54`.",
        "Full residual route certificate closed for direct-route PS3 corollary only: `True`.",
        "Direct-route PS3 corollary closed, not primitive P_state closure: `True`.",
        "Direct-route state/h-acceleration corollary rates closed, not primitive lifts: `True/True`.",
        "Direct-route strict proof steps closed: `4/4`.",
        "Primitive route closed by corollary: `False`.",
        "Primitive-route induced Taylor bounds proved by corollary: `0/162`.",
        "Uses velocity-collocation h-inverse route: `False`.",
        "Uses finite probe as proof: `False`.",
        "Submission-ready scope: `strict_proof_global_boundary_not_narrowed_claim_package_decision`.",
        "Strict proof audit scope: `B1_B3_strict_conditional_residual_bridge_proof_boundary`.",
        "B1 is closed by `B1_AD_EXPANDED_SYMBOLIC_ORACLE_CLOSURE_CERTIFICATE.md`; this audit scopes only the B1/B3 proof boundary.",
        "Narrowed-claim B4/B6/B7 subcheck statuses are recorded elsewhere (narrowed-only; not source-policy row closure): `closed/closed/closed`.",
        "Remaining global submission boundaries: `full_source_policy_package_ready,theorem_level_eta_h_solver_policy_evidence,closed_residual_to_error_theorem_for_mechanism_rows`.",
        "`submission_ready=false`.",
    ]:
        checks.check(token in audit_md, f"audit markdown missing token: {token}")

    if checks.errors:
        print("cmame_strict_proof_audit=FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("cmame_strict_proof_audit=PASS")
    print("strict_conditional_residual_bridge_proof_present=True")
    print("b3_closed=True")
    print("b1_closed=True")
    print("submission_ready=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
