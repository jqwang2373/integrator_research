#!/usr/bin/env python3
"""Validate the CMAME proof-style audit against reference text and manuscript."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
from paper_paths import LATEX, package_path as manuscript_path
ROOT = PAPER.parent.parent
AUDIT_JSON = PAPER / "CMAME_PROOF_STYLE_AUDIT.json"
AUDIT_MD = PAPER / "CMAME_PROOF_STYLE_AUDIT.md"
REF_PDF = ROOT / "1-s2.0-S0377042719305229-main.pdf"
REF_TXT = ROOT / "1-s2.0-S0377042719305229-main.txt"
MAIN_TEX = LATEX / "main_cmame.tex"
FLAT_TEX = LATEX / "cmame_submission_flat" / "main_cmame_submission.tex"
PROOF_CONTRACT = PAPER / "CMAME_PROOF_CONTRACT_GATE.json"
BLOCKER_GATE = PAPER / "CMAME_BLOCKER_CLOSURE_GATE.json"
STRICT_PROOF_AUDIT = PAPER / "CMAME_STRICT_PROOF_AUDIT.json"
PROOF_CLOSURE = PAPER / "PROOF_CLOSURE_MANIFEST.json"
PROOF_CLAIM_TRACEABILITY = PAPER / "PROOF_CLAIM_TRACEABILITY_AUDIT.json"


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


def display_equation_hygiene(text: str) -> dict[str, Any]:
    checked_envs = ["equation", "align", "subequations"]
    missing_label_locations: list[dict[str, Any]] = []
    env_counts: dict[str, int] = {}
    for env in checked_envs:
        pattern = re.compile(rf"\\begin\{{{env}\}}(.*?)\\end\{{{env}\}}", re.S)
        matches = list(pattern.finditer(text))
        env_counts[env] = len(matches)
        for match in matches:
            if r"\label{" not in match.group(0):
                missing_label_locations.append(
                    {
                        "env": env,
                        "line": text[: match.start()].count("\n") + 1,
                    }
                )

    bare_display_patterns = [
        r"^\s*\\\[",
        r"^\s*\\\]",
        r"\\begin\{align\*\}",
        r"\\begin\{equation\*\}",
        r"\\begin\{displaymath\}",
        r"\$\$",
    ]
    bare_display_locations: list[dict[str, Any]] = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        for pattern in bare_display_patterns:
            if re.search(pattern, line):
                bare_display_locations.append({"line": lineno, "pattern": pattern})
                break

    return {
        "checked_envs": checked_envs,
        "env_counts": env_counts,
        "missing_label_count": len(missing_label_locations),
        "missing_label_locations": missing_label_locations,
        "bare_display_count": len(bare_display_locations),
        "bare_display_locations": bare_display_locations,
        "all_checked_displays_labelled": not missing_label_locations,
        "no_bare_display_math": not bare_display_locations,
    }


def display_equation_reference_hygiene(text: str) -> dict[str, Any]:
    theorem_start = text.find(r"\begin{theorem}[Conditional sixth-order")
    proof_start = text.find(r"\begin{proof}[Proof of Theorem~\ref{thm:g6fullva-order}]")
    proof_end = text.find(r"\end{proof}", proof_start)
    checked_envs = ["equation", "align", "subequations"]
    display_labels: list[dict[str, Any]] = []
    theorem_region_labels: list[dict[str, Any]] = []

    for env in checked_envs:
        pattern = re.compile(rf"\\begin\{{{env}\}}(.*?)\\end\{{{env}\}}", re.S)
        for match in pattern.finditer(text):
            line = text[: match.start()].count("\n") + 1
            for label in re.findall(r"\\label\{([^}]+)\}", match.group(0)):
                entry = {"env": env, "line": line, "label": label}
                display_labels.append(entry)
                if theorem_start <= match.start() <= proof_end:
                    theorem_region_labels.append(entry)

    unreferenced: list[dict[str, Any]] = []
    theorem_unreferenced: list[dict[str, Any]] = []
    for entry in display_labels:
        label = entry["label"]
        text_without_label_definition = re.sub(
            rf"\\label\{{{re.escape(label)}\}}",
            "",
            text,
        )
        referenced = bool(
            re.search(rf"\\(?:eqref|ref)\{{{re.escape(label)}\}}", text_without_label_definition)
        )
        if not referenced:
            unreferenced.append(entry)

    theorem_label_set = {entry["label"] for entry in theorem_region_labels}
    theorem_unreferenced = [
        entry for entry in unreferenced if entry["label"] in theorem_label_set
    ]

    return {
        "checked_envs": checked_envs,
        "display_label_count": len(display_labels),
        "unreferenced_label_count": len(unreferenced),
        "theorem_statement_and_proof_label_count": len(theorem_region_labels),
        "theorem_statement_and_proof_unreferenced_count": len(theorem_unreferenced),
        "theorem_statement_and_proof_unreferenced_labels": theorem_unreferenced,
        "all_display_labels_referenced": not unreferenced,
        "all_theorem_statement_and_proof_display_labels_referenced": not theorem_unreferenced,
        "remaining_unreferenced_scope": (
            "none" if not unreferenced else "outside_active_order_theorem_statement_and_proof"
        ),
    }


def main() -> int:
    checks = Checks()
    try:
        audit = read_json(AUDIT_JSON)
        audit_md = read_text(AUDIT_MD)
        ref_text = read_text(REF_TXT)
        main_tex = read_text(MAIN_TEX)
        flat_tex = read_text(FLAT_TEX)
        proof_contract = read_json(PROOF_CONTRACT)
        blocker_gate = read_json(BLOCKER_GATE)
        strict_proof_audit = read_json(STRICT_PROOF_AUDIT)
        proof_closure = read_json(PROOF_CLOSURE)
        proof_claim_traceability = read_json(PROOF_CLAIM_TRACEABILITY)
    except Exception as exc:  # noqa: BLE001
        print(f"cmame_proof_style_audit=FAIL\n- {exc}")
        return 1

    checks.check(audit.get("schema") == "cmame-proof-style-audit-v1", "audit schema changed")
    checks.check(
        audit.get("status") == "proof_style_audit_completed_conditional_proof_not_submission_ready",
        "audit status changed",
    )
    checks.check(audit.get("submission_ready") is False, "audit must not claim submission ready")
    checks.check(
        audit.get("submission_ready_scope")
        == "proof_style_global_boundary_not_narrowed_claim_package_decision",
        "proof-style submission-ready scope changed",
    )
    checks.check(audit.get("read_only_audit") is True, "audit must be read-only")
    checks.check(REF_PDF.exists() and REF_PDF.stat().st_size > 100_000, "reference PDF missing or too small")
    checks.check(REF_TXT.exists() and len(ref_text) > 10_000, "reference PDF text missing or too small")

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
        checks.check(contains_normalized(ref_text, token), f"reference text missing proof-style token: {token}")

    for tex, label in [(main_tex, "main manuscript"), (flat_tex, "flat manuscript")]:
        for token in [
            r"\label{tab:newton-euler-obligations}",
            r"\label{tab:newton-euler-row-target-map}",
            "D1 & Translational balance rows",
            "D2 & Rotational balance rows",
            "D3 & Multiplier wrench rows",
            "D4 & Force/friction smoothness",
            "D5 & Dynamic-row defect rate",
            "D6 & Implemented row ordering",
            "Row-level target map for the Newton--Euler weak-balance rows",
            "Rows 24--26 and 30--32",
            "Rows 115--117 and 121--123",
            "complete; the active D5 direct-substitution certificate closes the dynamic",
            r"\label{lem:stage-residual-defect}",
            r"\label{lem:inexact-newton}",
            r"\label{thm:g6fullva-order}",
            r"\label{tab:proof-traceability}",
            r"\label{tab:common-reference-all-methods}",
            r"\label{tab:reference-proof-order-correspondence}",
            "Reference proof-order correspondence",
            "Lie-group constrained-BDF proof architecture",
            "Present FullVA analogue",
            "What is not imported",
            "No primitive D5 Taylor subterm is",
            "certified by the reference correspondence",
            "No BDF \\(p=k\\) theorem",
            "Taylor-layer separation",
            "T1 is the standard smooth Gauss collocation local-truncation layer",
            "T2 is the theorem-level FullVA residual-map layer",
            "T3 is the separate primitive Newton--Euler Taylor route",
            "Only T1 and T2 are load-bearing",
            "D5 primitive/Taylor inventory describes a separate sufficient proof route",
            "primitive inventory is separate-route material",
        ]:
            checks.check(contains_normalized(tex, token), f"{label} missing token: {token}")

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
        checks.check(reference_features.get(key) is True, f"reference feature not recorded: {key}")

    manuscript_features = audit.get("manuscript_style_features", {})
    for key in [
        "conditional_order_theorem_present",
        "stage_residual_perturbation_lemma_present",
        "inexact_newton_tolerance_lemma_present",
        "newton_euler_obligation_table_present",
        "newton_euler_row_target_map_present",
        "all_method_common_reference_table_present",
        "proof_traceability_table_present",
        "reference_proof_order_correspondence_table_present",
        "taylor_layer_separation_checkpoint_present",
        "taylor_three_slots_present",
        "taylor_t1_t2_load_bearing_boundary_present",
    ]:
        checks.check(manuscript_features.get(key) is True, f"manuscript feature not recorded: {key}")

    display_hygiene = audit.get("display_equation_hygiene", {})
    expected_display_hygiene = {
        "main_tex": display_equation_hygiene(main_tex),
        "flat_tex": display_equation_hygiene(flat_tex),
    }
    checks.check(
        display_hygiene == expected_display_hygiene,
        "display-equation hygiene audit is missing or stale",
    )
    for tex_label, hygiene in expected_display_hygiene.items():
        checks.check(
            hygiene["missing_label_count"] == 0,
            f"{tex_label} has displayed equation/align/subequations blocks without labels",
        )
        checks.check(
            hygiene["bare_display_count"] == 0,
            f"{tex_label} has bare or unnumbered display math",
        )
        checks.check(
            hygiene["all_checked_displays_labelled"] is True,
            f"{tex_label} display-label boolean changed",
        )
        checks.check(
            hygiene["no_bare_display_math"] is True,
            f"{tex_label} bare-display boolean changed",
        )

    display_reference_hygiene = audit.get("display_equation_reference_hygiene", {})
    expected_display_reference_hygiene = {
        "main_tex": display_equation_reference_hygiene(main_tex),
        "flat_tex": display_equation_reference_hygiene(flat_tex),
    }
    checks.check(
        display_reference_hygiene == expected_display_reference_hygiene,
        "display-equation reference hygiene audit is missing or stale",
    )
    for tex_label, hygiene in expected_display_reference_hygiene.items():
        checks.check(
            hygiene["unreferenced_label_count"] == 0,
            f"{tex_label} has globally unreferenced display labels",
        )
        checks.check(
            hygiene["all_display_labels_referenced"] is True,
            f"{tex_label} global display-reference boolean changed",
        )
        checks.check(
            hygiene["theorem_statement_and_proof_unreferenced_count"] == 0,
            f"{tex_label} has unreferenced display labels in the active order theorem/proof",
        )
        checks.check(
            hygiene["all_theorem_statement_and_proof_display_labels_referenced"] is True,
            f"{tex_label} theorem/proof display-reference boolean changed",
        )

    style_traceability = audit.get("proof_contract_theorem_traceability", {})
    contract_traceability = proof_contract.get("manuscript_theorem_traceability", {})
    strict_traceability = strict_proof_audit.get("manuscript_theorem_traceability", {})
    proof_closure_anchor_map = proof_closure.get("manuscript_anchor_map", {})
    proof_claim_anchor_map = proof_claim_traceability.get("manuscript_anchor_map", {})
    expected_theorem_assumption_anchor_ids = ["P1", "P2", "P3", "P4", "P5", "P6", "P7"]
    checks.check(
        style_traceability.get("source_gate") == "CMAME_PROOF_CONTRACT_GATE.json",
        "proof-style theorem traceability source gate changed",
    )
    checks.check(
        style_traceability.get("source_manifest")
        == contract_traceability.get("source_manifest")
        == "PROOF_CLOSURE_MANIFEST.json",
        "proof-style theorem traceability source manifest changed",
    )
    for key in [
        "proof_closure_status",
        "accepted_theorem_label",
        "accepted_method_order",
        "accepted_local_defect_order",
    ]:
        checks.check(
            style_traceability.get(key) == contract_traceability.get(key),
            f"proof-style theorem traceability mismatch: {key}",
        )
    for key in [
        "theorem_statement_labels_present",
        "conditional_theorem_boundary_present",
        "conditional_proof_claims_mapped_to_manuscript",
        "proof_dependency_graph_present",
        "proof_traceability_table_present",
        "dynamic_proof_closure_matrix_present",
        "primitive_lane_boundary_present",
        "residual_nonpromotion_present",
        "eta_h_theorem_condition_retained",
        "residual_to_error_not_promoted",
        "source_policy_or_full_tfe_not_promoted",
        "does_not_change_proof_closure_state",
    ]:
        checks.check(
            style_traceability.get(key) is contract_traceability.get(key) is True,
            f"proof-style theorem traceability lost true marker: {key}",
        )
    checks.check(
        style_traceability.get("manuscript_anchor_map_present")
        == contract_traceability.get("manuscript_anchor_map_present")
        == strict_traceability.get("manuscript_anchor_map_present")
        == proof_closure_anchor_map.get("all_label_anchors_present")
        is True,
        "proof-style manuscript anchor map is not synchronized across proof audits",
    )
    checks.check(
        style_traceability.get("manuscript_anchor_label_count")
        == contract_traceability.get("manuscript_anchor_label_count")
        == strict_traceability.get("manuscript_anchor_label_count")
        == proof_closure_anchor_map.get("label_anchor_count")
        == 24,
        "proof-style manuscript anchor label count changed",
    )
    checks.check(
        style_traceability.get("theorem_assumption_anchor_map_present")
        == contract_traceability.get("theorem_assumption_anchor_map_present")
        == strict_traceability.get("theorem_assumption_anchor_map_present")
        == proof_closure_anchor_map.get("all_theorem_assumption_anchors_present")
        is True,
        "proof-style theorem-assumption anchor map is not synchronized across proof audits",
    )
    checks.check(
        style_traceability.get("theorem_assumption_anchor_count")
        == contract_traceability.get("theorem_assumption_anchor_count")
        == strict_traceability.get("theorem_assumption_anchor_count")
        == proof_closure_anchor_map.get("theorem_assumption_anchor_count")
        == 7,
        "proof-style theorem-assumption anchor count changed",
    )
    checks.check(
        style_traceability.get("theorem_assumption_anchor_ids")
        == contract_traceability.get("theorem_assumption_anchor_ids")
        == strict_traceability.get("theorem_assumption_anchor_ids")
        == proof_closure_anchor_map.get("theorem_assumption_anchor_ids")
        == expected_theorem_assumption_anchor_ids,
        "proof-style theorem-assumption anchor IDs changed",
    )
    checks.check(
        style_traceability.get("proof_closure_proof_claim_anchor_maps_match")
        == contract_traceability.get("proof_closure_proof_claim_anchor_maps_match")
        == strict_traceability.get("proof_closure_proof_claim_anchor_maps_match")
        is True
        and proof_closure_anchor_map == proof_claim_anchor_map,
        "proof-style proof-closure/proof-claim manuscript anchor maps diverged",
    )
    checks.check(
        style_traceability.get("anchor_evidence_sources")
        == contract_traceability.get("anchor_evidence_sources")
        == ["PROOF_CLOSURE_MANIFEST.json", "PROOF_CLAIM_TRACEABILITY_AUDIT.json"],
        "proof-style manuscript anchor evidence sources changed",
    )
    for key in [
        "eta_h_solver_policy_evidence_closed",
        "fixed_tolerance_runs_are_asymptotic_proof",
    ]:
        checks.check(
            style_traceability.get(key) is contract_traceability.get(key) is False,
            f"proof-style theorem traceability overclaims false-boundary marker: {key}",
        )
    checks.check(
        "without closing eta_h solver-policy closure, residual-to-error, or source-policy/full-TFE gates"
        in style_traceability.get("style_audit_role", ""),
        "proof-style theorem traceability role boundary missing",
    )

    obligations = audit.get("newton_euler_obligations", [])
    checks.check(len(obligations) == 6, "Newton-Euler obligation count changed")
    target_map = audit.get("newton_euler_row_target_map", {})
    checks.check(target_map.get("row_count") == 36, "Newton-Euler row target map row count changed")
    checks.check(target_map.get("translational_rows") == 18, "Newton-Euler row target map translational count changed")
    checks.check(target_map.get("rotational_rows") == 18, "Newton-Euler row target map rotational count changed")
    checks.check(target_map.get("symbolic_defect_certificate_complete") is False, "row target map overclaims symbolic defect closure")
    proof_boundary = audit.get("proof_boundary", {})
    blocker_status = {row.get("id"): row.get("status") for row in blocker_gate.get("blockers", [])}
    strict_boundary = strict_proof_audit.get("two_layer_proof_boundary", {})
    checks.check(proof_boundary.get("b1_status") == blocker_status.get("B1") == "closed", "B1 proof-style boundary changed")
    checks.check(proof_boundary.get("b3_status") == blocker_status.get("B3") == "closed", "B3 proof-style boundary changed")
    checks.check(
        proof_boundary.get("b3_direct_proof_review_passed")
        is strict_boundary.get("b3_direct_proof_review_passed")
        is True,
        "B3 direct-proof review progress marker changed",
    )
    checks.check(
        proof_boundary.get("b3_closed_by_direct_proof_review")
        is strict_boundary.get("b3_closed_by_direct_proof_review")
        is True,
        "B3 direct-proof review closure marker changed",
    )
    checks.check(
        proof_boundary.get("b1_ad_expanded_implementation_oracle_still_open")
        is strict_boundary.get("b1_ad_expanded_implementation_oracle_still_open")
        is False,
        "B1 implementation-oracle open marker changed",
    )
    checks.check(
        proof_boundary.get("primitive_dynamic_symbolic_oracle_complete")
        is strict_boundary.get("primitive_dynamic_symbolic_oracle_complete")
        is False,
        "primitive/global dynamic symbolic oracle marker changed",
    )
    checks.check(
        proof_boundary.get("b1_closed_by_ad_expanded_symbolic_certificate")
        is strict_boundary.get("b1_closed_by_ad_expanded_symbolic_certificate")
        is True,
        "B1 AD-expanded closure certificate marker changed",
    )
    checks.check(
        proof_boundary.get("b1_ad_expanded_symbolic_oracle_closure")
        is strict_boundary.get("b1_ad_expanded_symbolic_oracle_closure")
        is True,
        "B1 AD-expanded symbolic closure marker changed",
    )
    checks.check(
        proof_boundary.get("b1_ad_expanded_symbolic_oracle_closed_cells")
        == strict_boundary.get("b1_ad_expanded_symbolic_oracle_closed_cells")
        == 4752,
        "B1 AD-expanded symbolic closure cell count changed",
    )
    checks.check(proof_boundary.get("proof_style_gap_narrowed") is True, "proof style gap should be narrowed")
    checks.check(proof_boundary.get("proof_gap_closed") is True, "audit must carry B3 proof-gap closure")
    checks.check(
        proof_boundary.get("proof_gap_closed_scope")
        == "direct_residual_bridge_kantorovich_route_closed_primitive_taylor_conditional_schema_open",
        "proof gap scope marker changed",
    )
    checks.check(
        proof_boundary.get("primitive_taylor_schema_scope")
        == "conditional_schema_open_no_current_instance_5_primitives_0_of_162_terms",
        "proof-style primitive Taylor conditional-schema scope changed",
    )
    checks.check(
        proof_boundary.get("primitive_taylor_reader_scope")
        == "certificate_status_future_route_not_diagnostic_evidence",
        "proof-style primitive Taylor reader-facing scope changed",
    )
    checks.check(
        proof_boundary.get("primitive_taylor_schema_current_instance_available") is False,
        "proof-style primitive Taylor conditional schema unexpectedly has a current instance",
    )
    checks.check(
        proof_boundary.get("primitive_taylor_schema_load_bearing_for_current_theorem") is False,
        "proof-style primitive Taylor schema was promoted to theorem input",
    )
    checks.check(
        proof_boundary.get("taylor_layer_separation_checkpoint_present") is True,
        "proof style boundary lost Taylor-layer separation",
    )
    checks.check(
        proof_boundary.get("taylor_layer_checkpoint_scope")
        == "T1_Gauss_truncation_and_T2_full_residual_map_Taylor_are_load_bearing_T3_primitive_D5_Taylor_is_conditional_schema_uninstantiated",
        "Taylor-layer checkpoint scope changed",
    )
    checks.check(
        proof_boundary.get("taylor_layer_checkpoint_reader_scope")
        == "T1_T2_load_bearing_T3_conditional_certificate_status_not_diagnostic_evidence",
        "Taylor-layer reader-facing checkpoint scope changed",
    )
    checks.check(
        proof_boundary.get("dynamic_symbolic_oracle_complete")
        is proof_contract.get("theorem_contract", {}).get("dynamic_symbolic_oracle_complete")
        is False,
        "dynamic symbolic oracle boundary changed",
    )
    checks.check(
        proof_boundary.get("stage_residual_O_h7_implementation_defect_proved")
        is proof_contract.get("theorem_contract", {}).get("stage_residual_O_h7_implementation_defect_proved")
        is True,
        "stage residual proof boundary changed",
    )
    checks.check(
        proof_boundary.get("scaled_tolerance_sweep_recorded")
        is proof_contract.get("theorem_contract", {}).get("scaled_tolerance_sweep_recorded")
        is False,
        "scaled tolerance boundary changed",
    )
    readiness_boundary = audit.get("readiness_boundary", {})
    remaining_gate_scope = audit.get("remaining_gate_scope", {})
    expected_narrowed_statuses = {"B4": "closed", "B6": "closed", "B7": "closed"}
    expected_global_boundaries = [
        "full_source_policy_package_ready",
        "theorem_level_eta_h_solver_policy_evidence",
        "closed_residual_to_error_theorem_for_mechanism_rows",
    ]
    checks.check(
        readiness_boundary.get("narrowed_claim_b4_b6_b7_statuses") == expected_narrowed_statuses,
        "proof-style narrowed-claim B4/B6/B7 boundary changed",
    )
    checks.check(
        readiness_boundary.get("global_submission_boundaries_retained") == expected_global_boundaries,
        "proof-style global submission boundary list changed",
    )
    checks.check(
        remaining_gate_scope.get("narrowed_claim_b4_b6_b7_statuses") == expected_narrowed_statuses,
        "proof-style remaining-gate narrowed-claim statuses changed",
    )
    checks.check(
        remaining_gate_scope.get("b4_b6_b7_closed_elsewhere_under_narrowed_claim") is True,
        "proof-style remaining gate lost B4/B6/B7 narrowed-claim closure marker",
    )
    checks.check(
        remaining_gate_scope.get("proof_style_audit_scope") == "proof_style_and_B1_B3_traceability",
        "proof-style remaining-gate scope changed",
    )
    checks.check(
        remaining_gate_scope.get("b1_b3_proof_style_blockers_closed") is True,
        "proof-style remaining gate lost B1/B3 closed marker",
    )
    checks.check(
        remaining_gate_scope.get("b1_closed_by_ad_expanded_symbolic_certificate")
        is proof_boundary.get("b1_closed_by_ad_expanded_symbolic_certificate")
        is True,
        "proof-style remaining gate lost B1 closure marker",
    )
    checks.check(
        remaining_gate_scope.get("b3_closed_by_direct_proof_review")
        is proof_boundary.get("b3_closed_by_direct_proof_review")
        is True,
        "proof-style remaining gate lost B3 direct proof closure marker",
    )
    checks.check(
        remaining_gate_scope.get("direct_residual_bridge_kantorovich_route_closed") is True,
        "proof-style remaining gate incorrectly leaves direct B3 route open",
    )
    checks.check(
        remaining_gate_scope.get("primitive_taylor_route_conditional_schema_open") is True,
        "proof-style remaining gate lost primitive-route conditional-schema boundary",
    )
    checks.check(
        remaining_gate_scope.get("primitive_taylor_route_conditional_schema_current_instance_available") is False,
        "proof-style remaining gate unexpectedly instantiated primitive-route conditional schema",
    )
    checks.check(
        remaining_gate_scope.get("primitive_taylor_route_reader_scope")
        == "conditional_certificate_status_record_for_future_route",
        "proof-style remaining gate lost primitive-route reader-facing scope",
    )
    checks.check(
        remaining_gate_scope.get("primitive_taylor_conditional_schema_open") is True,
        "proof-style remaining gate lost primitive Taylor conditional-schema boundary",
    )
    checks.check(
        remaining_gate_scope.get("primitive_taylor_schema_current_instance_available") is False,
        "proof-style remaining gate overclaims a primitive Taylor current instance",
    )
    for key in [
        "dynamic_symbolic_oracle_complete",
        "stage_residual_O_h7_implementation_defect_proved",
        "scaled_tolerance_sweep_recorded",
        "eta_h_O_h7_solver_policy_evidence",
    ]:
        checks.check(
            remaining_gate_scope.get(key) == proof_boundary.get(key),
            f"proof-style remaining gate mismatch: {key}",
        )
    checks.check(
        remaining_gate_scope.get("eta_h_theorem_condition_retained") is True,
        "proof-style remaining gate lost eta_h theorem-condition marker",
    )
    residual_contract = proof_contract.get("residual_to_error_contract", {})
    checks.check(
        remaining_gate_scope.get("accepted_residual_to_error_theorem")
        is residual_contract.get("accepted_residual_to_error_theorem")
        is False,
        "proof-style remaining gate residual-to-error acceptance boundary changed",
    )
    checks.check(
        remaining_gate_scope.get("residual_to_error_blocking_obligations")
        == residual_contract.get("blocking_obligation_count")
        == 7,
        "proof-style remaining gate residual-to-error blocking count changed",
    )
    checks.check(
        remaining_gate_scope.get("residual_to_error_route_promoted") is False,
        "proof-style remaining gate overclaims residual-to-error route promotion",
    )
    checks.check(
        remaining_gate_scope.get("full_source_policy_package_ready") is False,
        "proof-style remaining gate overclaims full source-policy package readiness",
    )
    checks.check(
        remaining_gate_scope.get("submission_ready_not_claimed_by_proof_style_audit") is True,
        "proof-style remaining gate lost no-submission-ready marker",
    )
    checks.check(
        remaining_gate_scope.get("global_submission_boundaries_retained") == expected_global_boundaries,
        "proof-style remaining-gate global submission boundaries changed",
    )
    required_to_close = audit.get("required_to_close", [])
    checks.check(
        "strict_full_system_taylor_kantorovich_route_closure_for_B3" not in required_to_close,
        "proof-style audit still lists closed B3 direct route as required to close",
    )
    for token in [
        "keep_B1_AD_expanded_symbolic_oracle_closure_certificate_synchronized",
        "scaled_eta_h_O_h7_solver_policy_evidence_or_kept_as_theorem_condition",
        "closed_residual_to_error_theorem_for_mechanism_rows",
        "source_policy_external_baseline_rows_before_submission_ready_claim",
    ]:
        checks.check(token in required_to_close, f"proof-style required-to-close token missing: {token}")

    for token in [
        "Status: **conditional theorem proof aligned; global submission boundaries retained**.",
        "`submission_ready=false` is scoped to proof-style/global proof-package",
        "`D1`",
        "`D6`",
        "Newton-Euler row-level target map present: `true`",
        "row target count: `36`",
        "translational/rotational: `18/18`",
        "Taylor-layer separation present: `true`",
        "Taylor slots separated: `T1` Gauss truncation and `T2` full residual-map",
        "conditional certificate schema with no current instance (`0/162` term",
        "Proof Contract Theorem Traceability",
        "Theorem labels/boundary/mapped: `true/true/true`.",
        "Proof dependency/traceability/dynamic matrix: `true/true/true`.",
        "Primitive-route and residual nonpromotion boundaries: `true/true`.",
        "Eta condition/closure and fixed-tolerance proof: `true/false/false`.",
        "Residual/source-policy-full-TFE not promoted: `true/true`; no-state-change `true`.",
        "Manuscript anchor map: `true`; label anchors `24`; theorem-interface/P7-output-boundary anchors `7`; IDs `P1,P2,P3,P4,P5,P6,P7`; proof-claim map match `true`.",
        "Reader-facing theorem-interface split: theorem interfaces `P1--P6`; P7 is an output nonclaim/residual-to-error boundary anchor, not a theorem premise.",
        "`b3_direct_proof_review_passed=true`",
        "`b3_closed_by_direct_proof_review=true`",
        "`b1_implementation_oracle_still_open=false`",
        "`b1_closed_by_ad_expanded_symbolic_certificate=true`",
        "`b1_ad_expanded_symbolic_oracle_closure=true`",
        "`b1_ad_expanded_symbolic_oracle_closed_cells=4752`",
        "`dynamic_symbolic_oracle_complete=false`",
        "`stage_residual_O_h7_implementation_defect_proved=true`",
        "`proof_gap_closed_scope=direct_residual_bridge_kantorovich_route_closed_primitive_taylor_conditional_schema_open`",
        "`taylor_layer_separation_scope=T1_Gauss_truncation_and_T2_full_residual_map_Taylor_are_load_bearing_T3_primitive_D5_Taylor_is_conditional_schema_uninstantiated`",
        "`taylor_layer_reader_scope=T1_T2_load_bearing_T3_conditional_certificate_status_not_diagnostic_evidence`",
        "`primitive_taylor_schema_scope=conditional_schema_open_no_current_instance_5_primitives_0_of_162_terms`",
        "`primitive_taylor_reader_scope=certificate_status_future_route_not_diagnostic_evidence`",
        "`primitive_taylor_schema_current_instance_available=false`",
        "`submission_ready_scope=proof_style_global_boundary_not_narrowed_claim_package_decision`",
        "`narrowed_claim_b4_b6_b7_statuses=closed/closed/closed`",
        "`global_submission_boundaries=full_source_policy_package_ready,theorem_level_eta_h_solver_policy_evidence,closed_residual_to_error_theorem_for_mechanism_rows`",
        "`submission_ready=false`",
        "Remaining Gate Scope",
        "`b4_b6_b7_closed_elsewhere_under_narrowed_claim=true`",
        "`b1_b3_proof_style_blockers_closed=true`",
        "`direct_residual_bridge_kantorovich_route_closed=true`",
        "`primitive_taylor_route_conditional_schema_open=true`",
        "`primitive_taylor_route_conditional_schema_current_instance_available=false`",
        "`primitive_taylor_route_reader_scope=conditional_certificate_status_record_for_future_route`",
        "`primitive_taylor_conditional_schema_open=true`",
        "`eta_h_theorem_condition_retained=true`",
        "`accepted_residual_to_error_theorem=false`",
        "`residual_to_error_blocking_obligations=7`",
        "`residual_to_error_route_promoted=false`",
        "`full_source_policy_package_ready=false`",
        "`submission_ready_not_claimed_by_proof_style_audit=true`",
    ]:
        checks.check(token in audit_md, f"audit markdown missing token: {token}")

    if checks.errors:
        print("cmame_proof_style_audit=FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("cmame_proof_style_audit=PASS")
    print("reference_pdf_checked=True")
    print("newton_euler_obligation_table=True")
    print("newton_euler_obligations=6")
    print("direct_pc2_proof_gap_closed=True")
    print("legacy_proof_gap_closed=True")
    print("b3_closed=True")
    print("b1_closed=True")
    print("b1_open=False")
    print("submission_ready=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
