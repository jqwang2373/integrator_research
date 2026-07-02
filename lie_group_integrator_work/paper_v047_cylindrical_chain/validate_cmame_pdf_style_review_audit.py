#!/usr/bin/env python3
"""Validate the PDF-read CMAME style review audit."""

from __future__ import annotations

import json
import sys
from pathlib import Path


PAPER = Path(__file__).resolve().parent
AUDIT_JSON = PAPER / "CMAME_PDF_STYLE_REVIEW_AUDIT.json"
AUDIT_MD = PAPER / "CMAME_PDF_STYLE_REVIEW_AUDIT.md"


class Checks:
    def __init__(self) -> None:
        self.errors: list[str] = []

    def check(self, condition: bool, message: str) -> None:
        if not condition:
            self.errors.append(message)


def read_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def main() -> int:
    checks = Checks()
    try:
        audit = read_json(AUDIT_JSON)
        md = read_text(AUDIT_MD)
    except Exception as exc:  # noqa: BLE001
        print(f"CMAME PDF style review audit validation: FAIL\n- {exc}")
        return 1

    reference = audit.get("reference_inventory", {})
    manuscript = audit.get("manuscript_inventory", {})
    flat = audit.get("flat_manuscript_inventory", {})
    ref_style = audit.get("reference_style_features", {})
    ms_style = audit.get("manuscript_style_features", {})

    checks.check(audit.get("schema") == "cmame-pdf-style-review-audit-v1", "schema changed")
    checks.check(
        audit.get("status") == "pdf_read_review_passed_narrowed_claim_subcheck_global_boundary_retained",
        "status changed",
    )
    checks.check(audit.get("ars_route") == "academic-paper-reviewer/full", "ARS route changed")
    checks.check(audit.get("submission_ready") is False, "PDF-style audit overclaims global submission readiness")
    checks.check(
        audit.get("submission_ready_scope")
        == "pdf_style_review_narrowed_claim_subcheck_passed_global_submission_boundary_retained",
        "PDF-style submission-ready scope changed",
    )
    checks.check(audit.get("submission_standard_scope") == "narrowed_claim_only", "submission standard scope changed")
    checks.check(
        audit.get("submission_standard_role") == "narrowed_claim_subcheck_not_global_review_verdict",
        "submission standard role changed",
    )
    checks.check(audit.get("global_submission_standard_met") is False, "global submission standard overclaimed")
    checks.check(audit.get("reference_text_read") is True, "reference PDF text was not read")
    checks.check(audit.get("manuscript_text_read") is True, "manuscript PDF text was not read")
    checks.check(audit.get("flat_manuscript_text_read") is True, "flat manuscript PDF text was not read")
    checks.check(reference.get("line_count", 0) > 1000, "reference text inventory is too small")
    checks.check(manuscript.get("line_count", 0) > 1500, "manuscript text inventory is too small")
    checks.check(flat.get("line_count", 0) > 2000, "flat manuscript text inventory is too small")
    checks.check(reference.get("algorithm_count", 0) >= 2, "reference algorithm boxes not detected")
    checks.check(reference.get("figure_count", 0) >= 18, "reference figure count unexpectedly low")
    checks.check(reference.get("table_count", 0) >= 3, "reference table count unexpectedly low")
    checks.check(ref_style.get("algorithm_boxes_present") is True, "reference algorithm style not recorded")
    checks.check(ref_style.get("numerical_experiments_section") is True, "reference numerical section missing")
    checks.check(ref_style.get("work_precision_figures") is True, "reference work/precision evidence missing")
    checks.check(
        ref_style.get("data_availability_and_declarations") is True,
        "reference declaration/data availability markers missing",
    )
    checks.check(ms_style.get("all_method_matrix_visible") is True, "manuscript all-method matrix not visible")
    checks.check(ms_style.get("theorem_present") is True, "manuscript theorem not detected")
    checks.check(ms_style.get("proofs_present") is True, "manuscript proof tokens not detected")
    checks.check(ms_style.get("figure_set_present") is True, "manuscript figure set not detected")
    checks.check(
        ms_style.get("reproducibility_appendix_present") is True
        or ms_style.get("artifact_appendix_present") is True,
        "reproducibility appendix not detected",
    )
    checks.check(
        ms_style.get("reproducibility_appendix_compacted") is True,
        "reproducibility appendix compaction marker missing",
    )
    checks.check(
        manuscript.get("audit_residue_mentions", 0) > reference.get("audit_residue_mentions", 0),
        "audit-residue comparison did not detect manuscript-specific repository language",
    )
    checks.check(audit.get("direct_nonlocal_velocity_order_wins") == 40, "order wins changed")
    checks.check(audit.get("direct_nonlocal_velocity_order_comparisons") == 40, "order comparisons changed")
    checks.check(audit.get("direct_nonlocal_velocity_error_wins") == 40, "error wins changed")
    checks.check(audit.get("direct_nonlocal_velocity_error_comparisons") == 40, "error comparisons changed")
    checks.check(audit.get("source_policy_rows_closed") == 0, "source-policy rows unexpectedly closed")
    checks.check(audit.get("source_policy_total_rows") == 40, "source-policy total changed")
    checks.check(audit.get("external_superiority_claim_allowed") is False, "external superiority allowed changed")
    checks.check(audit.get("narrowed_claim_evidence_supported") is True, "narrowed claim evidence support missing")
    checks.check(audit.get("b4_b7_closed_by_narrowed_claim_policy") is True, "B4/B7 narrowed closure missing")
    checks.check(audit.get("proof_gap_closed") is True, "proof gap closure not carried into PDF-style audit")
    checks.check(audit.get("direct_pc2_proof_gap_closed") is True, "scoped direct-PC2 proof closure missing")
    checks.check(
        audit.get("proof_gap_closed_scope") == "direct_residual_bridge_kantorovich_route_closed_primitive_taylor_conditional_schema_open",
        "proof gap scope missing from PDF-style audit",
    )
    checks.check(
        audit.get("direct_residual_bridge_submission_standard_satisfied") is True,
        "direct residual-bridge proof contract not carried into PDF-style audit",
    )
    checks.check(
        audit.get("direct_residual_bridge_active_standard_name")
        == "strict_direct_residual_bridge_submission_standard",
        "PDF-style audit did not preserve the active direct-route standard name",
    )
    checks.check(
        audit.get("direct_residual_bridge_submission_standard_scope")
        == "closed_by_direct_residual_bridge_kantorovich_route_primitive_taylor_conditional_schema_open",
        "direct residual-bridge scope missing from PDF-style audit",
    )
    checks.check(audit.get("primitive_taylor_route_closed") is False, "primitive Taylor route overclosed")
    checks.check(
        audit.get("primitive_taylor_schema_role")
        == (
            "conditional Newton-Euler primitive Taylor certificate schema; "
            "non-load-bearing under the active direct PC2 residual-bridge route"
        ),
        "primitive Taylor conditional-schema role changed",
    )
    checks.check(
        audit.get("primitive_taylor_schema_current_instance_available") is False,
        "primitive Taylor conditional schema unexpectedly has a current instance",
    )
    checks.check(
        audit.get("primitive_taylor_schema_blocker_summary")
        == "0/162 Taylor bounds certified; five primitive lift/bilinear antecedents remain open",
        "primitive Taylor conditional-schema blocker summary changed",
    )
    checks.check(audit.get("actual_taylor_bounds_proved") == 0, "actual Taylor bound count changed")
    checks.check(audit.get("open_taylor_bound_terms") == 162, "open Taylor term count changed")
    checks.check(
        audit.get("direct_substitution_supplies_active_pc2_residual_bridge") is True,
        "direct residual evidence not accepted as strict Taylor route input",
    )
    checks.check(
        audit.get("stage_residual_O_h7_implementation_defect_proved") is True,
        "stage residual defect proof not carried into PDF-style audit",
    )
    checks.check(audit.get("eta_h_O_h7_solver_policy_evidence") is False, "eta_h proof evidence unexpectedly closed")
    checks.check(audit.get("figure_set_b7_closed") is True, "B7 not closed")
    checks.check(audit.get("prose_b6_closed") is True, "B6 not closed")
    checks.check(audit.get("minimal_reproducibility_submission_ready") is False, "minimal package unexpectedly ready")
    checks.check(audit.get("submission_standard_met") is True, "audit did not mark submission standard met")
    checks.check(
        audit.get("narrowed_claim_submission_standard_met") is True,
        "audit did not mark narrowed-claim submission standard met",
    )
    checks.check(audit.get("full_source_policy_package_ready") is False, "audit overclaims full source-policy package")
    checks.check(audit.get("quality_review_passed") is True, "quality review did not pass")
    checks.check(audit.get("decision") == "submit_under_narrowed_claim", "decision changed")
    readiness_boundary = audit.get("readiness_boundary", {})
    remaining_gate_scope = audit.get("remaining_gate_scope", {})
    expected_global_boundaries = [
        "full_source_policy_package_ready",
        "theorem_level_eta_h_solver_policy_evidence",
        "closed_residual_to_error_theorem_for_mechanism_rows",
    ]
    checks.check(
        readiness_boundary.get("pdf_style_review_scope") == "pdf_read_quality_review_under_narrowed_claim",
        "PDF-style readiness scope changed",
    )
    checks.check(
        readiness_boundary.get("submission_standard_scope") == "narrowed_claim_only",
        "PDF-style readiness submission scope changed",
    )
    checks.check(
        readiness_boundary.get("narrowed_claim_b4_b6_b7_statuses")
        == {"B4": "closed", "B6": "closed", "B7": "closed"},
        "PDF-style readiness B4/B6/B7 statuses changed",
    )
    checks.check(
        readiness_boundary.get("global_submission_boundaries_retained") == expected_global_boundaries,
        "PDF-style readiness global boundaries changed",
    )
    checks.check(
        remaining_gate_scope.get("narrowed_claim_submission_standard_met") is True,
        "PDF-style remaining gate lost narrowed-claim pass marker",
    )
    checks.check(
        remaining_gate_scope.get("quality_review_passed_under_narrowed_claim") is True,
        "PDF-style remaining gate lost narrowed quality-review marker",
    )
    checks.check(
        remaining_gate_scope.get("global_submission_standard_met") is False,
        "PDF-style remaining gate overclaims global submission standard",
    )
    checks.check(
        remaining_gate_scope.get("source_policy_rows_closed") == audit.get("source_policy_rows_closed") == 0
        and remaining_gate_scope.get("source_policy_rows_total") == audit.get("source_policy_total_rows") == 40,
        "PDF-style remaining gate source-policy row counts changed",
    )
    checks.check(
        remaining_gate_scope.get("full_source_policy_package_ready") is False,
        "PDF-style remaining gate overclaims full source-policy package",
    )
    checks.check(
        remaining_gate_scope.get("minimal_reproducibility_submission_ready")
        is audit.get("minimal_reproducibility_submission_ready")
        is False,
        "PDF-style remaining gate minimal package boundary changed",
    )
    checks.check(
        remaining_gate_scope.get("direct_pc2_proof_gap_closed") is audit.get("direct_pc2_proof_gap_closed") is True,
        "PDF-style remaining gate lost direct-PC2 closure marker",
    )
    checks.check(
        remaining_gate_scope.get("direct_residual_bridge_route_satisfied")
        is audit.get("direct_residual_bridge_submission_standard_satisfied")
        is True,
        "PDF-style remaining gate lost direct residual-bridge route marker",
    )
    checks.check(
        remaining_gate_scope.get("eta_h_O_h7_solver_policy_evidence")
        is audit.get("eta_h_O_h7_solver_policy_evidence")
        is False,
        "PDF-style remaining gate eta_h boundary changed",
    )
    checks.check(
        remaining_gate_scope.get("eta_h_theorem_condition_retained") is True,
        "PDF-style remaining gate lost eta_h theorem-condition marker",
    )
    checks.check(
        remaining_gate_scope.get("accepted_residual_to_error_theorem") is False
        and remaining_gate_scope.get("residual_to_error_blocking_obligations") == 7
        and remaining_gate_scope.get("residual_to_error_route_promoted") is False,
        "PDF-style remaining gate residual-to-error boundary changed",
    )
    checks.check(
        remaining_gate_scope.get("b6_b7_closed_under_narrowed_claim") is True,
        "PDF-style remaining gate lost B6/B7 narrowed closure marker",
    )
    checks.check(
        remaining_gate_scope.get("submission_ready_not_claimed_by_pdf_style_audit") is True,
        "PDF-style remaining gate lost no-global-submission-ready marker",
    )
    checks.check(
        remaining_gate_scope.get("global_submission_boundaries_retained") == expected_global_boundaries,
        "PDF-style remaining gate global boundaries changed",
    )
    finding_ids = [item.get("id") for item in audit.get("blocking_findings", [])]
    checks.check(finding_ids == [], "blocking findings should be empty")
    scope_ids = [item.get("id") for item in audit.get("nonblocking_scope_findings", [])]
    for required in ["B4", "B6", "B7"]:
        checks.check(required in scope_ids, f"missing nonblocking scope finding {required}")
    checks.check("B2" not in finding_ids, "B2 should be closed by Route B claim demotion, not PDF-style blocking")

    for token in [
        "CMAME PDF Style Review Audit",
        "Reference text read: `True`",
        "Manuscript text read: `True`",
        "Flat manuscript text read: `True`",
        "Algorithm boxes present: `True`",
        "Direct residual-bridge proof contract satisfied: `True`.",
        "Direct residual-bridge active standard/scope: `strict_direct_residual_bridge_submission_standard` / `closed_by_direct_residual_bridge_kantorovich_route_primitive_taylor_conditional_schema_open`.",
        "Primitive/Taylor conditional-schema route closed and actual/open terms: `False` / `0/162`.",
        "Primitive/Taylor schema instance available and blocker summary: `False` / `0/162 Taylor bounds certified; five primitive lift/bilinear antecedents remain open`.",
        "Same-branch dynamic zero-block supplies active PC2 residual-bridge proof input: `True`.",
        "Numerical experiments section present: `True`",
        "Work/precision evidence present: `True`",
        "All-method matrix visible in PDF: `True`",
        "Reproducibility appendix present/compacted: `True/True`",
        "Source-policy rows closed: `0/40`",
        "External superiority claim allowed: `False`",
        "Direct PC2 proof gap/stage defect/eta_h closure state: `True/True/False`",
        "Direct PC2 proof-gap scope: `direct_residual_bridge_kantorovich_route_closed_primitive_taylor_conditional_schema_open`",
        "Subsidiary narrowed-claim subcheck standard met: `True`.",
        "Subsidiary narrowed-subcheck quality review passed: `True`; this is not global `quality_review_passed`.",
        "Full source-policy package ready: `False`.",
        "Submission standard scope: `narrowed_claim_only`.",
        "Submission standard role: `narrowed_claim_subcheck_not_global_review_verdict`.",
        "Global submission standard met: `False`.",
        "Submission ready: `False`.",
        "Submission ready scope: `pdf_style_review_narrowed_claim_subcheck_passed_global_submission_boundary_retained`.",
        "Narrowed-claim B4/B6/B7 statuses: `closed/closed/closed`.",
        "Remaining global submission boundaries: `full_source_policy_package_ready,theorem_level_eta_h_solver_policy_evidence,closed_residual_to_error_theorem_for_mechanism_rows`.",
        "Remaining-gate eta_h theorem condition retained: `True`.",
        "Remaining-gate residual-to-error blocking obligations: `7`.",
        "Remaining-gate submission ready not claimed: `True`.",
        "B6/B7 closed: `True/True`",
        "Minimal reproducibility package submission ready: `False`",
        "Bounded subcheck disposition: `bounded_subcheck_satisfied_not_global_submit`.",
        "PDF-style bounded-subcheck compatibility alias: `submit_under_narrowed_claim`; not a global submission instruction and not a global submission decision.",
    ]:
        checks.check(token in md, f"markdown missing token: {token}")

    if checks.errors:
        print("CMAME PDF style review audit validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("CMAME PDF style review audit validation: PASS")
    print(f"reference_figures={reference.get('figure_count')}")
    print(f"manuscript_figures={manuscript.get('figure_count')}")
    print(f"source_policy_rows_closed={audit.get('source_policy_rows_closed')}/{audit.get('source_policy_total_rows')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
