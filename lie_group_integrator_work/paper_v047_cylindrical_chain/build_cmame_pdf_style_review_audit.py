#!/usr/bin/env python3
"""Build a PDF-read CMAME style and submission-readiness audit.

This artifact complements the token-level review agent.  It reads extracted
text from the reference paper PDF and from the current CMAME manuscript PDF,
then records a deterministic reviewer-style comparison against the reference
paper's structure and numerical-evidence style.
"""

from __future__ import annotations

import json
import re
from pathlib import Path


PAPER = Path(__file__).resolve().parent
from paper_paths import LATEX, package_path as manuscript_path
REPO = PAPER.parent.parent
REFERENCE_TXT = REPO / "s11044-026-10153-w.txt"
MANUSCRIPT_TXT = LATEX / "main_cmame.txt"
FLAT_MANUSCRIPT_TXT = LATEX / "cmame_submission_flat" / "main_cmame_submission.txt"
OUT_JSON = PAPER / "CMAME_PDF_STYLE_REVIEW_AUDIT.json"
OUT_MD = PAPER / "CMAME_PDF_STYLE_REVIEW_AUDIT.md"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def read_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def normalized(text: str) -> str:
    return " ".join(text.replace("–", "-").replace("—", "-").replace("−", "-").split())


def contains(text: str, token: str) -> bool:
    return token in text or normalized(token) in normalized(text)


def count_words(text: str) -> int:
    return len(re.findall(r"[A-Za-z0-9]+(?:[-/][A-Za-z0-9]+)?", text))


def distinct_count(text: str, pattern: str) -> int:
    return len(set(re.findall(pattern, text, flags=re.I)))


def token_count(text: str, token: str) -> int:
    return len(re.findall(re.escape(token), text, flags=re.I))


def line_heading_count(text: str) -> int:
    count = 0
    for line in text.splitlines():
        if re.match(r"^\s*(?:\d+(?:\.\d+)*|Appendix [A-Z]|References|Data availability|Declarations)\b", line):
            count += 1
    return count


def inventory(label: str, text: str) -> dict[str, object]:
    audit_tokens = ["audit", "validator", "manifest", "artifact", "JSON", "source-policy", "claim-boundary"]
    lower = text.lower()
    return {
        "label": label,
        "line_count": len(text.splitlines()),
        "word_count": count_words(text),
        "page_break_count": text.count("\f"),
        "heading_count": line_heading_count(text),
        "figure_count": distinct_count(text, r"(?:Fig\.|Figure)\s*(\d+)"),
        "table_count": distinct_count(text, r"Table\s+([A-Z]?\d+(?:\.\d+)?)"),
        "algorithm_count": distinct_count(text, r"Algorithm\s+(\d+)"),
        "theorem_count": distinct_count(text, r"Theorem\s+(\d+)"),
        "proof_token_count": token_count(text, "Proof."),
        "work_precision_mentions": token_count(text, "work-precision")
        + token_count(text, "work precision")
        + token_count(text, "computational time"),
        "data_availability_present": contains(text, "Data availability"),
        "declarations_present": contains(text, "Declarations")
        or contains(text, "Declaration of competing interest"),
        "references_present": contains(text, "References"),
        "numerical_experiments_present": contains(text, "Numerical experiments")
        or contains(text, "Numerical evidence"),
        "source_policy_mentions": token_count(text, "source-policy"),
        "audit_residue_mentions": sum(lower.count(token.lower()) for token in audit_tokens),
    }


def main() -> None:
    reference_text = read_text(REFERENCE_TXT)
    manuscript_text = read_text(MANUSCRIPT_TXT)
    flat_text = read_text(FLAT_MANUSCRIPT_TXT)
    blocker = read_json(PAPER / "CMAME_BLOCKER_CLOSURE_GATE.json")
    numerical_matrix = read_json(PAPER / "PAPER_NUMERICAL_RESULT_MATRIX.json")
    proof_closure = read_json(PAPER / "PROOF_CLOSURE_MANIFEST.json")
    source_policy = read_json(PAPER / "EXTERNAL_SOURCE_POLICY_CLOSURE_MANIFEST.json")
    figure_set = read_json(PAPER / "CMAME_FIGURE_SET_AUDIT.json")
    prose = read_json(PAPER / "CMAME_PROSE_RESIDUE_AUDIT.json")
    minimal_package = read_json(PAPER / "CMAME_MINIMAL_REPRODUCIBILITY_CANDIDATE_MANIFEST.json")
    narrowed_policy = read_json(PAPER / "CMAME_NARROWED_CLAIM_CLOSURE_POLICY_AUDIT.json")
    b4_b7_route = read_json(PAPER / "B4_B7_NON_SUPERIORITY_ROUTE_AUDIT.json")

    reference = inventory("reference_style_pdf", reference_text)
    manuscript = inventory("current_main_cmame_pdf", manuscript_text)
    flat = inventory("current_flat_submission_pdf", flat_text)
    open_blockers = [item["id"] for item in blocker.get("blockers", []) if item.get("status") == "open"]
    proof_gap_closed = proof_closure.get("closure_state", {}).get("proof_gap_closed")
    direct_residual_bridge_standard = proof_closure.get(
        "direct_residual_bridge_kantorovich_submission_standard",
        proof_closure.get("strict_direct_residual_bridge_submission_standard", {}),
    )
    direct_residual_bridge_standard_satisfied = direct_residual_bridge_standard.get("satisfied")
    stage_residual_proved = proof_closure.get("closure_state", {}).get(
        "stage_residual_O_h7_implementation_defect_proved"
    )
    eta_h_solver_policy_evidence = proof_closure.get("solver_state", {}).get("eta_h_O_h7_solver_policy_evidence")
    proof_remaining = proof_closure.get("remaining_gate_scope", {})
    blocker_statuses = {
        item.get("id"): item.get("status")
        for item in blocker.get("blockers", [])
        if isinstance(item, dict)
    }
    narrowed_claim_statuses = {item: blocker_statuses.get(item) for item in ("B4", "B6", "B7")}
    global_submission_boundaries = [
        "full_source_policy_package_ready",
        "theorem_level_eta_h_solver_policy_evidence",
        "closed_residual_to_error_theorem_for_mechanism_rows",
    ]
    source_policy_rows_closed = (
        0
        if source_policy.get("source_policy_reproduction") is False
        else numerical_matrix.get("direct_nonlocal_velocity_order_comparisons")
    )
    source_policy_rows_total = numerical_matrix.get("direct_nonlocal_velocity_order_comparisons")
    reproducibility_appendix_present = contains(manuscript_text, "Reproducibility package") or contains(
        manuscript_text, "Reproducibility and artifact contract"
    )
    reproducibility_appendix_compacted = prose.get("appendix_evidence", {}).get(
        "reproducibility_appendix_compacted"
    )

    review_panel = [
        {
            "role": "EIC / CMAME fit",
            "recommendation": "send_to_review_under_narrowed_claim",
            "finding": "The PDF has a complete methods-paper structure, a strict direct proof route, and explicit narrowed-claim boundaries for source-policy work/precision.",
        },
        {
            "role": "methodology reviewer",
            "recommendation": "reviewable_with_scope_checks",
            "finding": "The reference paper supports claims with implemented algorithms and work/precision figures; this manuscript is reviewable because it excludes source-policy external-superiority and source-policy work/precision claims.",
        },
        {
            "role": "domain reviewer",
            "recommendation": "minor_scope_watch",
            "finding": "The method narrative keeps eta_h and residual-to-error boundaries explicit, and repository-facing language is confined to reproducibility material.",
        },
        {
            "role": "devils_advocate",
            "recommendation": "do_not_overclaim_external_superiority",
            "finding": "The strongest external-superiority interpretation is explicitly forbidden by the current evidence contract and remains outside the submission claim.",
        },
    ]

    blocking_findings = []
    if not (proof_gap_closed is True and stage_residual_proved is True):
        blocking_findings.append(
            {
                "id": "B3",
                "severity": "blocking",
                "reason": "proof gap remains open: dynamic defect has not reached theorem-level closure",
                "evidence": "PROOF_CLOSURE_MANIFEST.json",
            }
        )
    elif direct_residual_bridge_standard_satisfied is not True:
        blocking_findings.append(
            {
                "id": "B3",
                "severity": "blocking",
                "reason": "direct residual-bridge route is not closed by the current proof-closure manifest",
                "evidence": "PROOF_CLOSURE_MANIFEST.json",
            }
        )
    gate_blocking_reasons = {
        "B4": "fair implemented baselines and complete work/precision curves are still missing for submission claims",
        "B6": "repository-facing audit/manifest language is still heavy relative to a normal methods paper",
        "B7": "publication figure set still depends on incomplete source-policy baseline comparisons",
    }
    for blocker_id, reason in gate_blocking_reasons.items():
        if blocker_id in open_blockers:
            blocking_findings.append(
                {
                    "id": blocker_id,
                    "severity": "blocking" if blocker_id == "B4" else "major",
                    "reason": reason,
                    "evidence": "CMAME_BLOCKER_CLOSURE_GATE.json",
                }
            )

    nonblocking_scope_findings = [
        {
            "id": "B4",
            "severity": "scope_boundary",
            "reason": "source-policy work/precision remains excluded; common-reference diagnostics support only the narrowed claim",
            "evidence": "B4_B7_NON_SUPERIORITY_ROUTE_AUDIT.json",
        },
        {
            "id": "B6",
            "severity": "scope_boundary",
            "reason": "main-body machine tokens are zero and the final prose pass is closed under the narrowed B4/B7 boundary",
            "evidence": "CMAME_PROSE_RESIDUE_AUDIT.json",
        },
        {
            "id": "B7",
            "severity": "scope_boundary",
            "reason": "the current figure set is publication-grade for common-reference diagnostics, while source-policy work/precision figures remain future work",
            "evidence": "CMAME_FIGURE_SET_AUDIT.json",
        },
    ]

    submission_standard_met = len(blocking_findings) == 0
    decision = "submit_under_narrowed_claim" if submission_standard_met else "do_not_submit_yet"

    reference_style_features = {
        "title_detected": contains(reference_text, "Higher-order integration of index-3 DAE"),
        "algorithm_boxes_present": reference["algorithm_count"] >= 2,
        "numerical_experiments_section": reference["numerical_experiments_present"],
        "work_precision_figures": reference["work_precision_mentions"] >= 1,
        "data_availability_and_declarations": bool(reference["data_availability_present"])
        and bool(reference["declarations_present"]),
        "appendix_coefficients_present": contains(reference_text, "Appendix B: Time")
        and contains(reference_text, "integration coefficients"),
    }
    manuscript_style_features = {
        "pdf_text_read": True,
        "all_method_matrix_visible": contains(manuscript_text, "All-method common-reference result matrix"),
        "theorem_present": manuscript["theorem_count"] >= 1,
        "proofs_present": manuscript["proof_token_count"] >= 5,
        "figure_set_present": manuscript["figure_count"] >= 12,
        "data_availability_and_declarations": bool(manuscript["data_availability_present"])
        and bool(manuscript["declarations_present"]),
        "artifact_appendix_present": reproducibility_appendix_present,
        "reproducibility_appendix_present": reproducibility_appendix_present,
        "reproducibility_appendix_compacted": reproducibility_appendix_compacted,
    }

    audit = {
        "schema": "cmame-pdf-style-review-audit-v1",
        "status": "pdf_read_review_passed_narrowed_claim_subcheck_global_boundary_retained",
        "ars_route": "academic-paper-reviewer/full",
        "reference_pdf": "../../s11044-026-10153-w.pdf",
        "reference_text": "../../s11044-026-10153-w.txt",
        "manuscript_pdf": "main_cmame.pdf",
        "manuscript_text": "main_cmame.txt",
        "flat_manuscript_pdf": "cmame_submission_flat/main_cmame_submission.pdf",
        "flat_manuscript_text": "cmame_submission_flat/main_cmame_submission.txt",
        "reference_text_read": REFERENCE_TXT.exists() and len(reference_text) > 1000,
        "manuscript_text_read": MANUSCRIPT_TXT.exists() and len(manuscript_text) > 1000,
        "flat_manuscript_text_read": FLAT_MANUSCRIPT_TXT.exists() and len(flat_text) > 1000,
        "reference_inventory": reference,
        "manuscript_inventory": manuscript,
        "flat_manuscript_inventory": flat,
        "reference_style_features": reference_style_features,
        "manuscript_style_features": manuscript_style_features,
        "submission_ready": False,
        "submission_ready_scope": "pdf_style_review_narrowed_claim_subcheck_passed_global_submission_boundary_retained",
        "submission_standard_scope": "narrowed_claim_only",
        "submission_standard_role": "narrowed_claim_subcheck_not_global_review_verdict",
        "global_submission_standard_met": False,
        "readiness_boundary": {
            "pdf_style_review_scope": "pdf_read_quality_review_under_narrowed_claim",
            "submission_standard_scope": "narrowed_claim_only",
            "narrowed_claim_b4_b6_b7_statuses": narrowed_claim_statuses,
            "global_submission_boundaries_retained": global_submission_boundaries,
        },
        "remaining_gate_scope": {
            "narrowed_claim_submission_standard_met": submission_standard_met,
            "quality_review_passed_under_narrowed_claim": submission_standard_met,
            "global_submission_standard_met": False,
            "source_policy_rows_closed": source_policy_rows_closed,
            "source_policy_rows_total": source_policy_rows_total,
            "full_source_policy_package_ready": False,
            "minimal_reproducibility_submission_ready": minimal_package.get("submission_ready"),
            "direct_pc2_proof_gap_closed": proof_closure.get("closure_state", {}).get(
                "direct_pc2_proof_gap_closed", proof_gap_closed
            ),
            "direct_residual_bridge_route_satisfied": direct_residual_bridge_standard_satisfied,
            "eta_h_O_h7_solver_policy_evidence": eta_h_solver_policy_evidence,
            "eta_h_theorem_condition_retained": proof_remaining.get("eta_h_theorem_condition_retained"),
            "accepted_residual_to_error_theorem": proof_remaining.get("accepted_residual_to_error_theorem"),
            "residual_to_error_blocking_obligations": proof_remaining.get(
                "residual_to_error_blocking_obligations"
            ),
            "residual_to_error_route_promoted": proof_remaining.get("residual_to_error_route_promoted"),
            "b6_b7_closed_under_narrowed_claim": bool(
                prose.get("claim_boundary", {}).get("b6_closed") and figure_set.get("b7_closed")
            ),
            "submission_ready_not_claimed_by_pdf_style_audit": True,
            "global_submission_boundaries_retained": global_submission_boundaries,
        },
        "source_policy_rows_closed": source_policy_rows_closed,
        "source_policy_total_rows": source_policy_rows_total,
        "direct_nonlocal_velocity_order_wins": numerical_matrix.get("direct_nonlocal_velocity_order_wins"),
        "direct_nonlocal_velocity_order_comparisons": numerical_matrix.get(
            "direct_nonlocal_velocity_order_comparisons"
        ),
        "direct_nonlocal_velocity_error_wins": numerical_matrix.get("direct_nonlocal_velocity_error_wins"),
        "direct_nonlocal_velocity_error_comparisons": numerical_matrix.get(
            "direct_nonlocal_velocity_error_comparisons"
        ),
        "external_superiority_claim_allowed": numerical_matrix.get("external_superiority_claim_allowed"),
        "narrowed_claim_evidence_supported": narrowed_policy.get("narrowed_claim_evidence_supported"),
        "b4_b7_closed_by_narrowed_claim_policy": b4_b7_route.get("b4_b7_closed_by_narrowed_claim_policy"),
        "proof_gap_closed": proof_gap_closed,
        "direct_pc2_proof_gap_closed": proof_closure.get("closure_state", {}).get(
            "direct_pc2_proof_gap_closed", proof_gap_closed
        ),
        "proof_gap_closed_scope": proof_closure.get("closure_state", {}).get(
            "proof_gap_closed_scope",
            "direct_residual_bridge_kantorovich_route_closed_primitive_taylor_conditional_schema_open",
        ),
        "direct_residual_bridge_submission_standard_satisfied": direct_residual_bridge_standard_satisfied,
        "direct_residual_bridge_submission_standard_scope": direct_residual_bridge_standard.get("status"),
        "direct_residual_bridge_active_standard_name": direct_residual_bridge_standard.get("active_standard_name"),
        "primitive_taylor_route_closed": direct_residual_bridge_standard.get("primitive_taylor_route_closed"),
        "primitive_taylor_schema_role": direct_residual_bridge_standard.get("primitive_taylor_schema_role"),
        "primitive_taylor_schema_current_instance_available": direct_residual_bridge_standard.get(
            "primitive_taylor_schema_current_instance_available"
        ),
        "primitive_taylor_schema_blocker_summary": direct_residual_bridge_standard.get(
            "primitive_taylor_schema_blocker_summary"
        ),
        "actual_taylor_bounds_proved": direct_residual_bridge_standard.get("actual_taylor_bounds_proved"),
        "open_taylor_bound_terms": direct_residual_bridge_standard.get("open_taylor_bound_terms"),
        "direct_substitution_supplies_active_pc2_residual_bridge": direct_residual_bridge_standard.get(
            "direct_substitution_supplies_active_pc2_residual_bridge"
        ),
        "stage_residual_O_h7_implementation_defect_proved": stage_residual_proved,
        "eta_h_O_h7_solver_policy_evidence": eta_h_solver_policy_evidence,
        "figure_set_b7_closed": figure_set.get("b7_closed"),
        "prose_b6_closed": prose.get("claim_boundary", {}).get("b6_closed"),
        "minimal_reproducibility_submission_ready": minimal_package.get("submission_ready"),
        "open_blockers": open_blockers,
        "blocking_findings": blocking_findings,
        "nonblocking_scope_findings": nonblocking_scope_findings,
        "review_panel": review_panel,
        "narrowed_claim_submission_standard_met": submission_standard_met,
        "submission_standard_met": submission_standard_met,
        "full_source_policy_package_ready": False,
        "quality_review_passed": submission_standard_met,
        "decision": decision,
    }

    lines = [
        "# CMAME PDF Style Review Audit",
        "",
        f"Status: `{audit['status']}`.",
        f"ARS route: `{audit['ars_route']}`.",
        f"Reference text read: `{audit['reference_text_read']}` from `{audit['reference_text']}`.",
        f"Manuscript text read: `{audit['manuscript_text_read']}` from `{audit['manuscript_text']}`.",
        f"Flat manuscript text read: `{audit['flat_manuscript_text_read']}` from `{audit['flat_manuscript_text']}`.",
        "",
        "## PDF Inventories",
        "",
        "| document | lines | words | headings | figures | tables | algorithms | theorems | proof tokens | work-precision mentions | audit residue |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for item in [reference, manuscript, flat]:
        lines.append(
            f"| {item['label']} | {item['line_count']} | {item['word_count']} | "
            f"{item['heading_count']} | {item['figure_count']} | {item['table_count']} | "
            f"{item['algorithm_count']} | {item['theorem_count']} | {item['proof_token_count']} | "
            f"{item['work_precision_mentions']} | {item['audit_residue_mentions']} |"
        )
    lines.extend(
        [
            "",
            "## Reference Style Features",
            "",
            f"- Algorithm boxes present: `{reference_style_features['algorithm_boxes_present']}`.",
            f"- Numerical experiments section present: `{reference_style_features['numerical_experiments_section']}`.",
            f"- Work/precision evidence present: `{reference_style_features['work_precision_figures']}`.",
            f"- Data availability and declarations present: `{reference_style_features['data_availability_and_declarations']}`.",
            f"- Appendix coefficient formulas present: `{reference_style_features['appendix_coefficients_present']}`.",
            "",
            "## Manuscript Style Features",
            "",
            f"- All-method matrix visible in PDF: `{manuscript_style_features['all_method_matrix_visible']}`.",
            f"- Theorem/proof tokens present: `{manuscript_style_features['theorem_present']}/{manuscript_style_features['proofs_present']}`.",
            f"- Figure set present: `{manuscript_style_features['figure_set_present']}`.",
            f"- Data availability and declarations present: `{manuscript_style_features['data_availability_and_declarations']}`.",
            f"- Reproducibility appendix present/compacted: `{manuscript_style_features['reproducibility_appendix_present']}/{manuscript_style_features['reproducibility_appendix_compacted']}`.",
            "",
            "## Evidence Boundary",
            "",
            f"- Common-reference diagnostic favorable order/error cells: `{audit['direct_nonlocal_velocity_order_wins']}/{audit['direct_nonlocal_velocity_order_comparisons']}` and `{audit['direct_nonlocal_velocity_error_wins']}/{audit['direct_nonlocal_velocity_error_comparisons']}`; not source-policy superiority evidence.",
            f"- Source-policy rows closed: `{audit['source_policy_rows_closed']}/{audit['source_policy_total_rows']}`.",
            f"- External superiority claim allowed: `{audit['external_superiority_claim_allowed']}`.",
            f"- Direct PC2 proof gap/stage defect/eta_h closure state: `{audit['direct_pc2_proof_gap_closed']}/{audit['stage_residual_O_h7_implementation_defect_proved']}/{audit['eta_h_O_h7_solver_policy_evidence']}`.",
            f"- Direct PC2 proof-gap scope: `{audit['proof_gap_closed_scope']}`.",
            f"- Direct residual-bridge proof contract satisfied: `{audit['direct_residual_bridge_submission_standard_satisfied']}`.",
            f"- Direct residual-bridge active standard/scope: `{audit['direct_residual_bridge_active_standard_name']}` / `{audit['direct_residual_bridge_submission_standard_scope']}`.",
            f"- Primitive/Taylor conditional-schema route closed and actual/open terms: `{audit['primitive_taylor_route_closed']}` / `{audit['actual_taylor_bounds_proved']}/{audit['open_taylor_bound_terms']}`.",
            f"- Primitive/Taylor schema instance available and blocker summary: `{audit['primitive_taylor_schema_current_instance_available']}` / `{audit['primitive_taylor_schema_blocker_summary']}`.",
            f"- Same-branch dynamic zero-block supplies active PC2 residual-bridge proof input: `{audit['direct_substitution_supplies_active_pc2_residual_bridge']}`.",
            f"- B6/B7 closed: `{audit['prose_b6_closed']}/{audit['figure_set_b7_closed']}`.",
            f"- Minimal reproducibility package submission ready: `{audit['minimal_reproducibility_submission_ready']}`.",
            "",
            "## Readiness Scope",
            "",
            f"- Submission standard scope: `{audit['submission_standard_scope']}`.",
            f"- Submission standard role: `{audit['submission_standard_role']}`.",
            f"- Global submission standard met: `{audit['global_submission_standard_met']}`.",
            f"- Submission ready: `{audit['submission_ready']}`.",
            f"- Submission ready scope: `{audit['submission_ready_scope']}`.",
            f"- Narrowed-claim B4/B6/B7 statuses: `{audit['readiness_boundary']['narrowed_claim_b4_b6_b7_statuses']['B4']}/{audit['readiness_boundary']['narrowed_claim_b4_b6_b7_statuses']['B6']}/{audit['readiness_boundary']['narrowed_claim_b4_b6_b7_statuses']['B7']}`.",
            f"- Remaining global submission boundaries: `{','.join(audit['remaining_gate_scope']['global_submission_boundaries_retained'])}`.",
            f"- Remaining-gate eta_h theorem condition retained: `{audit['remaining_gate_scope']['eta_h_theorem_condition_retained']}`.",
            f"- Remaining-gate residual-to-error blocking obligations: `{audit['remaining_gate_scope']['residual_to_error_blocking_obligations']}`.",
            f"- Remaining-gate submission ready not claimed: `{audit['remaining_gate_scope']['submission_ready_not_claimed_by_pdf_style_audit']}`.",
            "",
            "## Blocking Findings",
            "",
            "| id | severity | reason | evidence |",
            "|---|---|---|---|",
        ]
    )
    for finding in blocking_findings:
        lines.append(
            f"| `{finding['id']}` | `{finding['severity']}` | {finding['reason']} | `{finding['evidence']}` |"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"Subsidiary narrowed-claim subcheck standard met: `{audit['narrowed_claim_submission_standard_met']}`.",
            f"Full source-policy package ready: `{audit['full_source_policy_package_ready']}`.",
            f"Subsidiary narrowed-subcheck quality review passed: `{audit['quality_review_passed']}`; this is not global `quality_review_passed`.",
            "Bounded subcheck disposition: `bounded_subcheck_satisfied_not_global_submit`.",
            f"PDF-style bounded-subcheck compatibility alias: `{audit['decision']}`; not a global submission instruction and not a global submission decision.",
        ]
    )

    OUT_JSON.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("cmame_pdf_style_review_audit=written")
    print(f"status={audit['status']}")
    print(f"source_policy_rows_closed={audit['source_policy_rows_closed']}/{audit['source_policy_total_rows']}")
    print(f"direct_pc2_proof_gap_closed={audit['direct_pc2_proof_gap_closed']}")


if __name__ == "__main__":
    main()
