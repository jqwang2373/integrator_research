#!/usr/bin/env python3
"""Validate the open Newton-Euler symbolic-defect certificate scaffold."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
CERT_JSON = PAPER / "NEWTON_EULER_SYMBOLIC_DEFECT_CERTIFICATE.json"
CERT_MD = PAPER / "NEWTON_EULER_SYMBOLIC_DEFECT_CERTIFICATE.md"
MAIN_TEX = PAPER / "main_cmame.tex"
FLAT_TEX = PAPER / "cmame_submission_flat" / "main_cmame_submission.tex"


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


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def normalized_contains(text: str, token: str) -> bool:
    return " ".join(token.split()) in " ".join(text.split())


def expected_global_rows() -> list[int]:
    rows: list[int] = []
    for stage in range(3):
        base = stage * 44 + 24
        rows.extend(range(base, base + 12))
    return rows


def main() -> int:
    checks = Checks()
    try:
        cert = read_json(CERT_JSON)
        cert_md = read_text(CERT_MD)
        target_audit = read_json(PAPER / "NEWTON_EULER_SYMBOLIC_TARGET_AUDIT.json")
        ad_expanded_oracle = read_json(PAPER / "NEWTON_EULER_AD_EXPANDED_ROW_ORACLE_AUDIT.json")
        virtual_work_wrench = read_json(PAPER / "NEWTON_EULER_VIRTUAL_WORK_WRENCH_AUDIT.json")
        proof_remaining = read_json(PAPER / "PROOF_REMAINING_WORK_MANIFEST.json")
        proof_closure = read_json(PAPER / "PROOF_CLOSURE_MANIFEST.json")
        main_tex = read_text(MAIN_TEX)
        flat_tex = read_text(FLAT_TEX)
    except Exception as exc:  # noqa: BLE001
        print(f"newton_euler_symbolic_defect_certificate=FAIL\n- {exc}")
        return 1

    summary = cert.get("summary", {})
    row_certs = cert.get("row_certificates", [])
    requirements = cert.get("symbolic_certificate_requirements", [])
    open_obligations = cert.get("open_obligations", [])
    closed_obligations = cert.get("closed_obligations", [])
    runtime_expression = cert.get("runtime_expression_audit", {})
    runtime_template = cert.get("runtime_template_instantiation_audit", {})
    body_specific_wrench = cert.get("body_specific_wrench_expansion_audit", {})
    virtual_work_wrench_audit = cert.get("virtual_work_wrench_audit", {})
    template_equivalence = cert.get("template_algebraic_equivalence_audit", {})
    runtime_oracle_link = cert.get("runtime_dynamic_row_oracle_link_audit", {})
    ad_expanded_oracle_audit = cert.get("ad_expanded_row_oracle_audit", {})
    row_ordering_scaling_ad = cert.get("row_ordering_scaling_ad_audit", {})
    smooth_force_lift = cert.get("smooth_force_lift_certificate_audit", {})
    manuscript_link = cert.get("manuscript_link_audit", {})
    target_rows = target_audit.get("row_targets", [])
    target_by_global_row = {
        item.get("global_row"): item
        for item in target_rows
        if isinstance(item, dict)
    }

    checks.check(cert.get("schema") == "newton-euler-symbolic-defect-certificate-v1", "schema changed")
    checks.check(
        cert.get("status") == "balance_identities_closed_defect_not_proved",
        "status changed",
    )
    checks.check(cert.get("submission_ready") is False, "certificate overclaims submission readiness")
    checks.check(cert.get("certificate_complete") is False, "certificate unexpectedly complete")
    checks.check(cert.get("proof_gap_closed") is False, "certificate unexpectedly closes proof gap")
    checks.check(
        "false only for the primitive/symbolic Newton-Euler lane" in cert.get("proof_gap_closed_scope", ""),
        "symbolic certificate proof-gap scope missing",
    )
    checks.check(
        cert.get("dynamic_symbolic_oracle_complete") is False,
        "certificate unexpectedly closes symbolic oracle",
    )
    checks.check(
        "not an input to the accepted direct residual-bridge theorem route"
        in cert.get("dynamic_symbolic_oracle_complete_scope", ""),
        "symbolic-oracle scope missing",
    )
    checks.check(
        cert.get("stage_residual_O_h7_implementation_defect_proved") is False,
        "certificate unexpectedly proves O(h^7) dynamic defect",
    )
    checks.check(
        "not proved by this primitive/symbolic certificate"
        in cert.get("stage_residual_O_h7_implementation_defect_proved_scope", ""),
        "symbolic certificate stage-residual scope missing",
    )
    checks.check(
        cert.get("active_direct_pc2_route_source") == "D5_DYNAMIC_DIRECT_SUBSTITUTION_CERTIFICATE.json",
        "symbolic certificate direct PC2 route source missing",
    )
    checks.check(summary.get("row_count") == 36, "row count changed")
    checks.check(summary.get("translational_row_count") == 18, "translational row count changed")
    checks.check(summary.get("rotational_row_count") == 18, "rotational row count changed")
    checks.check(summary.get("symbolic_expanded_row_count") == 36, "symbolic expansion row count changed")
    checks.check(summary.get("runtime_mapped_row_count") == 36, "runtime mapped row count changed")
    checks.check(summary.get("certified_row_count") == 0, "certified row count changed")
    checks.check(summary.get("open_row_count") == 36, "open row count changed")
    checks.check(summary.get("obligation_count") == 6, "obligation count changed")
    checks.check(summary.get("open_obligation_count") == 1, "open obligation count changed")
    checks.check(summary.get("closed_obligation_count") == 5, "closed obligation count changed")
    checks.check(
        summary.get("closed_obligation_ids")
        == [
            "translational_balance_identity",
            "rotational_balance_identity",
            "multiplier_wrench_consistency",
            "smooth_force_lift_consistency",
            "symbolic_runtime_row_equivalence",
        ],
        "closed obligation ids changed",
    )
    checks.check(summary.get("row_obligation_link_count") == 180, "row-obligation link count changed")
    checks.check(summary.get("rows_with_complete_obligation_sets") == 36, "complete obligation rows changed")
    checks.check(summary.get("unsatisfied_close_requirement_ids") == [], "unsatisfied PC ids changed")
    checks.check(summary.get("pc1_symbolic_row_oracle_closed") is True, "PC1 not closed")
    checks.check(summary.get("pc2_dynamic_O_h7_defect_certificate_closed") is False, "PC2 unexpectedly closed")
    checks.check(summary.get("c1_row_expansion_closed") is True, "C1 row expansion should be closed")
    checks.check(summary.get("balance_identity_closed") is True, "D1/D2 balance identity not closed")
    checks.check(summary.get("balance_identity_closed_rows") == 36, "balance identity closed rows changed")
    checks.check(
        summary.get("translational_balance_identity_closed") is True,
        "translational balance identity not closed",
    )
    checks.check(
        summary.get("translational_balance_identity_closed_rows") == 18,
        "translational balance identity rows changed",
    )
    checks.check(
        summary.get("rotational_balance_identity_closed") is True,
        "rotational balance identity not closed",
    )
    checks.check(
        summary.get("rotational_balance_identity_closed_rows") == 18,
        "rotational balance identity rows changed",
    )
    checks.check(summary.get("runtime_row_layout_mapping_checked") is True, "runtime row layout mapping not checked")
    checks.check(
        summary.get("runtime_expression_structure_checked") is True,
        "runtime expression structure audit not checked",
    )
    checks.check(
        summary.get("runtime_expression_structure_checked_rows") == 36,
        "runtime expression checked row count changed",
    )
    checks.check(
        summary.get("runtime_expression_structure_translational_rows") == 18,
        "runtime expression translational row count changed",
    )
    checks.check(
        summary.get("runtime_expression_structure_rotational_rows") == 18,
        "runtime expression rotational row count changed",
    )
    checks.check(summary.get("c2_runtime_equivalence_closed") is True, "C2 runtime equivalence not closed")
    checks.check(
        summary.get("runtime_template_instantiation_checked") is True,
        "runtime template instantiation not checked",
    )
    checks.check(
        summary.get("runtime_template_instantiation_checked_rows") == 36,
        "runtime template instantiation row count changed",
    )
    checks.check(
        summary.get("runtime_template_instantiation_translational_rows") == 18,
        "runtime template translational row count changed",
    )
    checks.check(
        summary.get("runtime_template_instantiation_rotational_rows") == 18,
        "runtime template rotational row count changed",
    )
    checks.check(
        summary.get("body_specific_wrench_expansion_checked") is True,
        "body-specific wrench expansion not checked",
    )
    checks.check(
        summary.get("body_specific_wrench_expansion_checked_rows") == 36,
        "body-specific wrench checked row count changed",
    )
    checks.check(summary.get("body0_wrench_expansion_rows") == 18, "body0 wrench row count changed")
    checks.check(summary.get("body1_wrench_expansion_rows") == 18, "body1 wrench row count changed")
    checks.check(
        summary.get("virtual_work_wrench_sign_skeleton_checked") is True,
        "virtual-work wrench sign skeleton not checked",
    )
    checks.check(
        summary.get("virtual_work_wrench_sign_skeleton_checked_rows") == 36,
        "virtual-work wrench sign-skeleton row count changed",
    )
    checks.check(
        summary.get("virtual_work_template_identity_proved") is True,
        "virtual-work template identity not proved",
    )
    checks.check(
        summary.get("virtual_work_template_identity_rows") == 36,
        "virtual-work template identity row count changed",
    )
    checks.check(summary.get("virtual_work_template_identity_count") == 2, "virtual-work template identity count changed")
    checks.check(
        summary.get("virtual_work_template_identity_count_proved") == 2,
        "proved virtual-work template identity count changed",
    )
    checks.check(
        summary.get("row_expanded_virtual_work_identity_proved") is True,
        "row-expanded virtual-work identity not proved",
    )
    checks.check(
        summary.get("row_expanded_virtual_work_identity_rows") == 36,
        "row-expanded virtual-work identity row count changed",
    )
    checks.check(
        summary.get("row_expanded_virtual_work_identity_count") == 6,
        "row-expanded virtual-work identity count changed",
    )
    checks.check(
        summary.get("row_expanded_virtual_work_identity_count_proved") == 6,
        "proved row-expanded virtual-work identity count changed",
    )
    checks.check(
        summary.get("multiplier_wrench_consistency_closed") is True,
        "multiplier wrench consistency not closed",
    )
    checks.check(
        summary.get("full_row_expanded_virtual_work_identity_proved") is True,
        "row-expanded virtual-work identity not proved",
    )
    checks.check(
        summary.get("template_algebraic_equivalence_checked") is True,
        "template algebraic equivalence not checked",
    )
    checks.check(
        summary.get("template_algebraic_equivalence_checked_rows") == 36,
        "template algebraic equivalence row count changed",
    )
    checks.check(
        summary.get("template_algebraic_equivalence_translational_rows") == 18,
        "template algebraic equivalence translational count changed",
    )
    checks.check(
        summary.get("template_algebraic_equivalence_rotational_rows") == 18,
        "template algebraic equivalence rotational count changed",
    )
    checks.check(
        summary.get("c2_template_algebraic_equivalence_closed") is True,
        "template-level C2 subcheck not closed",
    )
    checks.check(
        summary.get("runtime_dynamic_row_formula_oracle_link_checked") is True,
        "runtime dynamic-row formula-oracle link not checked",
    )
    checks.check(
        summary.get("runtime_dynamic_row_formula_oracle_rows") == 36,
        "runtime dynamic-row formula-oracle row count changed",
    )
    checks.check(
        summary.get("runtime_full_formula_row_oracle_checked") is True,
        "runtime full formula-row oracle link not checked",
    )
    checks.check(
        summary.get("runtime_formula_row_ad_jacobian_checked") is True,
        "runtime formula-row AD Jacobian link not checked",
    )
    checks.check(
        summary.get("runtime_formula_row_ad_jacobian_probes") == 3,
        "runtime formula-row AD Jacobian probe count changed",
    )
    checks.check(
        summary.get("ad_expanded_row_oracle_checked") is True,
        "AD-expanded row oracle not checked",
    )
    checks.check(
        summary.get("ad_expanded_row_oracle_rows") == 36,
        "AD-expanded row oracle row count changed",
    )
    checks.check(
        summary.get("ad_expanded_row_oracle_columns_per_row") == 132,
        "AD-expanded row oracle column count changed",
    )
    checks.check(
        summary.get("ad_expanded_row_oracle_probe_count") == 3,
        "AD-expanded row oracle probe count changed",
    )
    checks.check(
        float(summary.get("ad_expanded_row_oracle_max_mismatch", 1.0)) <= 1.0e-12,
        "AD-expanded row oracle mismatch too large",
    )
    checks.check(
        summary.get("ad_expanded_symbolic_oracle_closure") is False,
        "AD-expanded audit overclaims symbolic closure",
    )
    checks.check(
        summary.get("row_ordering_scaling_ad_equivalence_closed") is True,
        "row-ordering/scaling/AD equivalence not closed",
    )
    checks.check(
        summary.get("smooth_force_lift_source_structure_checked") is True,
        "smooth force-lift source structure not checked",
    )
    checks.check(
        summary.get("smooth_force_lift_consistency_closed") is True,
        "smooth force-lift consistency not closed",
    )
    checks.check(
        summary.get("smooth_force_lift_global_C7_bound_proved") is True,
        "smooth force-lift global C7 bound not proved",
    )
    checks.check(summary.get("c4_manuscript_link_closed") is True, "C4 manuscript link not closed")

    checks.check(
        runtime_expression.get("source_file") == "v047_cylindrical_chain_pipeline/run_v047.py",
        "runtime expression source path changed",
    )
    checks.check(runtime_expression.get("residual_function_found") is True, "residual function not found")
    checks.check(runtime_expression.get("structure_checked") is True, "runtime expression structure not checked")
    checks.check(runtime_expression.get("checked_rows") == 36, "runtime expression checked rows changed")
    checks.check(runtime_expression.get("translational_rows_checked") == 18, "runtime expression translational rows changed")
    checks.check(runtime_expression.get("rotational_rows_checked") == 18, "runtime expression rotational rows changed")
    runtime_checks = runtime_expression.get("checks", {})
    for key in [
        "normal_force_lambda_basis_terms",
        "friction_brown_mcphee_terms",
        "joint_force_normal_plus_friction_axis",
        "body0_distal_force_subtraction_terms",
        "translational_balance_terms",
        "proximal_moment_arm_terms",
        "distal_moment_arm_terms",
        "proximal_axis_torque_terms",
        "distal_axis_torque_terms",
        "rotational_balance_terms",
        "dynamic_append_order_trans_then_rot",
    ]:
        checks.check(runtime_checks.get(key) is True, f"runtime expression check not satisfied: {key}")
    checks.check(
        "not an independent symbolic proof" in runtime_expression.get("scope", ""),
        "runtime expression scope boundary missing",
    )
    checks.check(runtime_template.get("checked") is True, "runtime template audit not checked")
    checks.check(runtime_template.get("checked_rows") == 36, "runtime template audit row count changed")
    checks.check(
        runtime_template.get("translational_rows_checked") == 18,
        "runtime template audit translational row count changed",
    )
    checks.check(
        runtime_template.get("rotational_rows_checked") == 18,
        "runtime template audit rotational row count changed",
    )
    checks.check(
        "D5 remains open"
        in runtime_template.get("scope", ""),
        "runtime template audit scope boundary missing",
    )
    checks.check(body_specific_wrench.get("checked") is True, "body-specific wrench audit not checked")
    checks.check(body_specific_wrench.get("checked_rows") == 36, "body-specific wrench audit row count changed")
    checks.check(body_specific_wrench.get("body0_rows_checked") == 18, "body-specific body0 rows changed")
    checks.check(body_specific_wrench.get("body1_rows_checked") == 18, "body-specific body1 rows changed")
    checks.check(
        "does not prove the O(h^7) dynamic defect bound"
        in body_specific_wrench.get("scope", ""),
        "body-specific wrench audit scope boundary missing",
    )
    checks.check(
        virtual_work_wrench.get("schema") == "newton-euler-virtual-work-wrench-audit-v1",
        "virtual-work audit schema changed",
    )
    checks.check(
        virtual_work_wrench.get("summary", {}).get("checked_rows") == 36,
        "source virtual-work audit row count changed",
    )
    checks.check(virtual_work_wrench_audit.get("checked") is True, "virtual-work audit not checked")
    checks.check(virtual_work_wrench_audit.get("checked_rows") == 36, "virtual-work audit checked rows changed")
    checks.check(
        virtual_work_wrench_audit.get("template_virtual_work_identity_proved") is True,
        "virtual-work template identity not proved",
    )
    checks.check(
        virtual_work_wrench_audit.get("template_virtual_work_identity_rows") == 36,
        "virtual-work template identity rows changed",
    )
    checks.check(virtual_work_wrench_audit.get("template_identity_count") == 2, "template identity count changed")
    checks.check(
        virtual_work_wrench_audit.get("template_identity_count_proved") == 2,
        "proved template identity count changed",
    )
    checks.check(virtual_work_wrench_audit.get("site_count_checked") == 9, "virtual-work audit site count changed")
    checks.check(virtual_work_wrench_audit.get("site_count") == 9, "virtual-work audit total site count changed")
    checks.check(
        virtual_work_wrench_audit.get("row_expanded_virtual_work_identity_proved") is True,
        "virtual-work audit row-expanded identity not proved",
    )
    checks.check(
        virtual_work_wrench_audit.get("row_expanded_virtual_work_identity_rows") == 36,
        "virtual-work audit row-expanded identity rows changed",
    )
    checks.check(
        virtual_work_wrench_audit.get("row_expanded_identity_count") == 6,
        "virtual-work audit row-expanded identity count changed",
    )
    checks.check(
        virtual_work_wrench_audit.get("row_expanded_identity_count_proved") == 6,
        "virtual-work audit proved row-expanded identity count changed",
    )
    checks.check(
        virtual_work_wrench_audit.get("multiplier_wrench_consistency_closed") is True,
        "virtual-work audit did not close multiplier consistency",
    )
    checks.check(
        virtual_work_wrench_audit.get("full_row_expanded_virtual_work_identity_proved") is True,
        "virtual-work audit row-expanded identity not proved",
    )
    checks.check(
        "row-expanded lower-pair multiplier-wrench identity" in virtual_work_wrench_audit.get("scope", ""),
        "virtual-work audit scope boundary missing",
    )
    checks.check(template_equivalence.get("checked") is True, "template algebraic audit not checked")
    checks.check(template_equivalence.get("checked_rows") == 36, "template algebraic audit row count changed")
    checks.check(
        template_equivalence.get("translational_rows_checked") == 18,
        "template algebraic audit translational row count changed",
    )
    checks.check(
        template_equivalence.get("rotational_rows_checked") == 18,
        "template algebraic audit rotational row count changed",
    )
    checks.check(
        "not an O(h^7) defect proof"
        in template_equivalence.get("scope", ""),
        "template algebraic audit scope boundary missing",
    )
    checks.check(runtime_oracle_link.get("checked") is True, "runtime oracle link not checked")
    checks.check(runtime_oracle_link.get("source") == "DYNAMIC_ROW_ORACLE_GATE.json", "runtime oracle source changed")
    family = runtime_oracle_link.get("dynamic_row_family", {})
    checks.check(family.get("name") == "newton_euler_weak_balance", "runtime oracle dynamic family changed")
    checks.check(family.get("offset") == 24, "runtime oracle dynamic family offset changed")
    checks.check(family.get("width") == 12, "runtime oracle dynamic family width changed")
    checks.check(family.get("total_rows") == 36, "runtime oracle dynamic row count changed")
    checks.check(
        runtime_oracle_link.get("full_formula_row_oracle_checked") is True,
        "runtime oracle full formula marker missing",
    )
    checks.check(
        runtime_oracle_link.get("full_formula_row_oracle_row_count") == 132,
        "runtime oracle full formula row count changed",
    )
    checks.check(
        runtime_oracle_link.get("dynamic_row_family_added") == "newton_euler_weak_balance",
        "runtime oracle did not add Newton-Euler family",
    )
    checks.check(
        runtime_oracle_link.get("runtime_formula_row_oracle_complete") is True,
        "runtime formula-row oracle marker missing",
    )
    checks.check(
        runtime_oracle_link.get("formula_row_ad_jacobian_checked") is True,
        "runtime formula-row AD Jacobian marker missing",
    )
    checks.check(
        runtime_oracle_link.get("formula_row_ad_jacobian_probe_count") == 3,
        "runtime formula-row AD Jacobian probes changed",
    )
    checks.check(runtime_oracle_link.get("runtime_ad_oracle_complete") is True, "runtime AD oracle marker missing")
    checks.check(runtime_oracle_link.get("symbolic_oracle_complete") is False, "runtime oracle overclaims symbolic oracle")
    checks.check(
        runtime_oracle_link.get("stage_residual_O_h7_implementation_defect_proved") is False,
        "runtime oracle overclaims O(h^7) proof",
    )
    checks.check(
        "finite-probe runtime evidence, not a symbolic identity proof"
        in runtime_oracle_link.get("scope", ""),
        "runtime oracle link scope boundary missing",
    )
    checks.check(
        ad_expanded_oracle.get("schema") == "newton-euler-ad-expanded-row-oracle-audit-v1",
        "source AD-expanded audit schema changed",
    )
    checks.check(
        ad_expanded_oracle.get("ad_expanded_row_oracle_closed") is True,
        "source AD-expanded row oracle not closed",
    )
    checks.check(
        ad_expanded_oracle.get("ad_expanded_symbolic_oracle_closure") is False,
        "source AD-expanded audit overclaims symbolic closure",
    )
    checks.check(
        ad_expanded_oracle_audit.get("source") == "NEWTON_EULER_AD_EXPANDED_ROW_ORACLE_AUDIT.json",
        "AD-expanded audit source changed",
    )
    checks.check(ad_expanded_oracle_audit.get("checked") is True, "AD-expanded audit not checked")
    checks.check(ad_expanded_oracle_audit.get("checked_rows") == 36, "AD-expanded audit row count changed")
    checks.check(ad_expanded_oracle_audit.get("columns_per_row") == 132, "AD-expanded audit column count changed")
    checks.check(ad_expanded_oracle_audit.get("probe_count") == 3, "AD-expanded audit probe count changed")
    checks.check(
        float(ad_expanded_oracle_audit.get("max_mismatch", 1.0)) <= 1.0e-12,
        "AD-expanded audit mismatch too large",
    )
    checks.check(
        ad_expanded_oracle_audit.get("ad_expanded_symbolic_oracle_closure") is False,
        "AD-expanded audit overclaims symbolic oracle",
    )
    checks.check(
        ad_expanded_oracle_audit.get("independent_symbolic_row_by_row_oracle_closed") is False,
        "AD-expanded audit overclaims independent symbolic rows",
    )
    checks.check(
        ad_expanded_oracle_audit.get("dynamic_symbolic_oracle_complete") is False,
        "AD-expanded audit overclaims dynamic symbolic oracle",
    )
    checks.check(
        ad_expanded_oracle_audit.get("stage_residual_O_h7_implementation_defect_proved") is False,
        "AD-expanded audit overclaims O(h^7)",
    )
    checks.check(
        "not a symbolic identity proof" in ad_expanded_oracle_audit.get("scope", ""),
        "AD-expanded audit scope boundary missing",
    )
    checks.check(
        row_ordering_scaling_ad.get("source") == "NEWTON_EULER_ROW_ORDERING_SCALING_AD_AUDIT.json",
        "D6 audit source changed",
    )
    checks.check(row_ordering_scaling_ad.get("checked") is True, "D6 audit not checked")
    checks.check(
        row_ordering_scaling_ad.get("symbolic_runtime_row_equivalence_closed") is True,
        "D6 symbolic runtime row-equivalence not closed",
    )
    checks.check(
        row_ordering_scaling_ad.get("row_ordering_scaling_ad_closed") is True,
        "D6 row-ordering/scaling/AD not closed",
    )
    checks.check(
        row_ordering_scaling_ad.get("dynamic_symbolic_oracle_complete") is False,
        "D6 audit overclaims dynamic symbolic oracle",
    )
    checks.check(
        row_ordering_scaling_ad.get("stage_residual_O_h7_implementation_defect_proved") is False,
        "D6 audit overclaims O(h^7)",
    )
    checks.check(
        "symbolic-certificate O(h^7) defect lane remains open" in row_ordering_scaling_ad.get("scope", ""),
        "D6 audit scope boundary missing",
    )
    checks.check(smooth_force_lift.get("source") == "SMOOTH_FORCE_LIFT_CERTIFICATE.json", "smooth force source changed")
    checks.check(smooth_force_lift.get("checked") is True, "smooth force source structure not checked")
    checks.check(
        smooth_force_lift.get("smooth_force_lift_consistency_closed") is True,
        "smooth force-lift certificate did not close D4",
    )
    checks.check(
        smooth_force_lift.get("global_C7_tube_derivative_bound_proved") is True,
        "smooth force-lift global C7 bound not proved",
    )
    checks.check(
        smooth_force_lift.get("smooth_branch", {}).get("stribeck_velocity") == 0.5,
        "smooth branch stribeck velocity changed",
    )
    checks.check(
        smooth_force_lift.get("sharp_branch", {}).get("stribeck_velocity") == 0.05,
        "sharp branch stribeck velocity changed",
    )
    checks.check(
        "compact proof-tube C7 derivative"
        in smooth_force_lift.get("scope", ""),
        "smooth force-lift scope boundary missing",
    )

    checks.check(isinstance(requirements, list) and len(requirements) == 4, "certificate requirement count changed")
    requirement_state = {item.get("id"): item.get("satisfied") for item in requirements}
    checks.check(requirement_state.get("C1_row_expansion") is True, "C1 row expansion not closed")
    checks.check(requirement_state.get("C2_runtime_equivalence") is True, "C2 runtime equivalence not closed")
    checks.check(requirement_state.get("C3_defect_bound") is False, "C3 defect bound unexpectedly closed")
    checks.check(requirement_state.get("C4_manuscript_link") is True, "C4 manuscript link should be closed")
    checks.check([item.get("id") for item in requirements] == ["C1_row_expansion", "C2_runtime_equivalence", "C3_defect_bound", "C4_manuscript_link"], "certificate requirement ids changed")

    checks.check(manuscript_link.get("checked") is True, "manuscript link audit not checked")
    checks.check(
        manuscript_link.get("requirement_id") == "C4_manuscript_link",
        "manuscript link requirement id changed",
    )
    checks.check(
        manuscript_link.get("source_files")
        == ["main_cmame.tex", "cmame_submission_flat/main_cmame_submission.tex"],
        "manuscript link source files changed",
    )
    for source_label in ["main_cmame.tex", "cmame_submission_flat/main_cmame_submission.tex"]:
        source_state = manuscript_link.get("checked_sources", {}).get(source_label, {})
        checks.check(source_state.get("present") is True, f"manuscript link missing in {source_label}")
        checks.check(source_state.get("missing_tokens") == [], f"manuscript link token missing in {source_label}")
    for tex_label, tex_text in [("main_cmame.tex", main_tex), ("main_cmame_submission.tex", flat_tex)]:
        for token in [
            "manuscript statement is deliberately narrower than the full primitive/Taylor route",
            "Newton--Euler symbolic-defect certificate is used here as a provenance record",
            "row-expansion and runtime-equivalence checks",
            "It is not the active dynamic-row closure route",
            "For the direct residual-bridge route used by PC2, the dynamic-row residual input is supplied by the D5 direct-substitution certificate",
            "symbolic-certificate C3 primitive/Taylor defect-bound lane remains open",
            "zero residual after substituting the smooth Gauss lift \\(Z_G\\)",
            "\\label{lem:stage-residual-defect}",
        ]:
            checks.check(normalized_contains(tex_text, token), f"{tex_label} missing C4 manuscript-link token: {token}")
    checks.check(
        "does not close the certificate's internal C3 route" in manuscript_link.get("scope", ""),
        "manuscript link scope overclaims C3 closure",
    )

    checks.check(isinstance(open_obligations, list) and len(open_obligations) == 1, "open obligation list changed")
    checks.check(all(item.get("proof_status") == "open" for item in open_obligations), "an obligation overclosed")
    checks.check(
        [item.get("id") for item in open_obligations] == ["gauss_stage_dynamic_defect_rate"],
        "open obligation ids changed",
    )
    checks.check(
        sum(int(item.get("target_row_count", 0)) for item in open_obligations) == 36,
        "open obligation rows changed",
    )
    checks.check(
        isinstance(closed_obligations, list) and len(closed_obligations) == 5,
        "closed obligation list changed",
    )
    closed_by_id = {item.get("id"): item for item in closed_obligations}
    expected_closed_rows = {
        "translational_balance_identity": 18,
        "rotational_balance_identity": 18,
        "multiplier_wrench_consistency": 36,
        "smooth_force_lift_consistency": 36,
        "symbolic_runtime_row_equivalence": 36,
    }
    for obligation_id, expected_rows in expected_closed_rows.items():
        checks.check(obligation_id in closed_by_id, f"closed obligation missing: {obligation_id}")
        checks.check(
            closed_by_id.get(obligation_id, {}).get("proof_status") == "closed",
            f"closed obligation status changed: {obligation_id}",
        )
        checks.check(
            closed_by_id.get(obligation_id, {}).get("target_row_count") == expected_rows,
            f"closed obligation row count changed: {obligation_id}",
        )

    checks.check(isinstance(row_certs, list) and len(row_certs) == 36, "row certificate list changed")
    checks.check([row.get("global_row") for row in row_certs] == expected_global_rows(), "global row ordering changed")
    checks.check(len(target_by_global_row) == 36, "target audit row map incomplete")
    checks.check(
        sum(1 for row in row_certs if row.get("balance_block") == "translational_newton_balance") == 18,
        "translational row certificates changed",
    )
    checks.check(
        sum(1 for row in row_certs if row.get("balance_block") == "rotational_euler_balance") == 18,
        "rotational row certificates changed",
    )
    for row in row_certs:
        target = target_by_global_row.get(row.get("global_row"), {})
        for key in [
            "stage",
            "body",
            "component",
            "balance_block",
            "local_block_row",
            "runtime_source_component",
            "runtime_source_component_offset",
            "runtime_source_component_width",
            "runtime_source_component_index",
        ]:
            checks.check(row.get(key) == target.get(key), f"row {row.get('global_row')} {key} mismatch with target audit")
        checks.check(row.get("runtime_row_mapping_present") is True, "row runtime mapping marker missing")
        checks.check(
            row.get("runtime_row_mapping_source") == "NEWTON_EULER_SYMBOLIC_TARGET_AUDIT.row_targets",
            "row runtime mapping source changed",
        )
        checks.check(
            "algebraic row equivalence remains open" in row.get("runtime_row_mapping_scope", ""),
            "row runtime mapping scope boundary missing",
        )
        checks.check(row.get("obligation_count") == 5, "row obligation count changed")
        checks.check(row.get("symbolic_expansion_present") is True, "row symbolic expansion missing")
        checks.check(
            row.get("runtime_expression_structure_checked") is True,
            "row runtime expression structure marker missing",
        )
        checks.check(
            "not an independent symbolic proof" in row.get("runtime_expression_structure_scope", ""),
            "row runtime expression structure scope missing",
        )
        checks.check(
            row.get("runtime_template_instantiation_checked") is True,
            "row runtime template instantiation marker missing",
        )
        expected_expression_key = (
            "trans" if row.get("balance_block") == "translational_newton_balance" else "rot"
        )
        checks.check(
            row.get("runtime_template_expression_key") == expected_expression_key,
            f"row {row.get('global_row')} runtime template expression key changed",
        )
        checks.check(
            row.get("runtime_template_mapping_present") is True,
            "row runtime template mapping marker missing",
        )
        term_presence = row.get("runtime_template_required_terms_present", {})
        checks.check(
            isinstance(term_presence, dict) and term_presence and all(value is True for value in term_presence.values()),
            f"row {row.get('global_row')} runtime template term presence incomplete",
        )
        checks.check(
            "not algebraic equivalence or an O(h^7) proof"
            in row.get("runtime_template_instantiation_scope", ""),
            "row runtime template scope boundary missing",
        )
        checks.check(
            row.get("body_specific_wrench_expansion_checked") is True,
            "row body-specific wrench expansion marker missing",
        )
        wrench = row.get("body_specific_wrench_expansion", {})
        checks.check(isinstance(wrench, dict), "row body-specific wrench expansion missing")
        checks.check(wrench.get("checked") is True, "row body-specific wrench expansion not checked")
        checks.check(bool(wrench.get("body_specific_expansion")), "row body-specific expansion text missing")
        checks.check(
            len(wrench.get("joint_force_definitions", [])) == 2,
            "row joint-force definition count changed",
        )
        if row.get("balance_block") == "translational_newton_balance":
            checks.check(
                wrench.get("equation_kind") == "body_specific_translational_force_balance",
                "translational wrench equation kind changed",
            )
            expected_net_force = "F_0 - F_1" if row.get("body") == 0 else "F_1"
            checks.check(wrench.get("net_force_expression") == expected_net_force, "net force expression changed")
        else:
            checks.check(
                wrench.get("equation_kind") == "body_specific_rotational_wrench_balance",
                "rotational wrench equation kind changed",
            )
            torque_text = str(wrench.get("joint_torque_expression", ""))
            checks.check("s_prev" in torque_text and "eta" in torque_text, "rotational torque expansion incomplete")
            if row.get("body") == 0:
                checks.check("s_next,0" in torque_text and "- eta_1" in torque_text, "body0 distal torque expansion missing")
            else:
                checks.check("s_next" not in torque_text, "body1 should not include distal torque expansion")
        checks.check(
            "still does not prove independent symbolic runtime equivalence"
            in wrench.get("scope", ""),
            "row body-specific wrench scope boundary missing",
        )
        checks.check(
            row.get("virtual_work_wrench_sign_skeleton_checked") is True,
            f"row {row.get('global_row')} missing virtual-work sign skeleton",
        )
        checks.check(
            row.get("virtual_work_wrench_audit_source") == "NEWTON_EULER_VIRTUAL_WORK_WRENCH_AUDIT.json",
            f"row {row.get('global_row')} virtual-work audit source changed",
        )
        checks.check(
            isinstance(row.get("virtual_work_wrench_expected_sites"), list)
            and bool(row.get("virtual_work_wrench_expected_sites")),
            f"row {row.get('global_row')} virtual-work site list missing",
        )
        checks.check(
            row.get("virtual_work_template_identity_proved") is True,
            f"row {row.get('global_row')} missing virtual-work template identity",
        )
        checks.check(
            row.get("row_expanded_virtual_work_identity_proved") is True,
            f"row {row.get('global_row')} missing row-expanded virtual-work identity",
        )
        checks.check(
            row.get("multiplier_wrench_consistency_closed") is True,
            f"row {row.get('global_row')} did not close multiplier consistency",
        )
        checks.check(
            row.get("full_row_expanded_virtual_work_identity_proved") is True,
            f"row {row.get('global_row')} missing row-expanded virtual-work proof",
        )
        template_eq = row.get("template_algebraic_equivalence", {})
        checks.check(
            row.get("template_algebraic_equivalence_checked") is True,
            "row template algebraic equivalence marker missing",
        )
        checks.check(isinstance(template_eq, dict), "row template algebraic equivalence missing")
        checks.check(template_eq.get("checked") is True, "row template algebraic equivalence not checked")
        checks.check(
            template_eq.get("simplified_difference") == "0",
            f"row {row.get('global_row')} template algebraic difference is not zero",
        )
        checks.check(bool(template_eq.get("runtime_scalar_template")), "runtime scalar template missing")
        checks.check(bool(template_eq.get("target_scalar_template")), "target scalar template missing")
        checks.check(isinstance(template_eq.get("role_map"), dict), "template role map missing")
        checks.check(
            "not a full AD-expanded row oracle"
            in template_eq.get("scope", ""),
            "row template algebraic equivalence scope boundary missing",
        )
        checks.check(
            row.get("runtime_formula_row_oracle_link_checked") is True,
            "row runtime formula-oracle link marker missing",
        )
        checks.check(
            row.get("runtime_formula_row_oracle_global_row") == row.get("global_row"),
            "row runtime formula-oracle global row mismatch",
        )
        checks.check(
            row.get("runtime_formula_row_oracle_family") == "newton_euler_weak_balance",
            "row runtime formula-oracle family changed",
        )
        checks.check(
            row.get("runtime_formula_row_oracle_source")
            == "DYNAMIC_ROW_ORACLE_GATE.full_independent_formula_row_oracle",
            "row runtime formula-oracle source changed",
        )
        checks.check(
            "not a symbolic identity proof" in row.get("runtime_formula_row_oracle_scope", ""),
            "row runtime formula-oracle scope boundary missing",
        )
        checks.check(
            row.get("ad_expanded_row_oracle_checked") is True,
            "row AD-expanded oracle marker missing",
        )
        checks.check(
            isinstance(row.get("ad_expanded_formula_family_major_row"), int),
            "row AD-expanded formula-major index missing",
        )
        checks.check(
            row.get("ad_expanded_jacobian_columns_covered") == 132,
            "row AD-expanded column count changed",
        )
        checks.check(
            row.get("ad_expanded_jacobian_probe_count") == 3,
            "row AD-expanded probe count changed",
        )
        checks.check(
            row.get("ad_expanded_row_oracle_source")
            == "NEWTON_EULER_AD_EXPANDED_ROW_ORACLE_AUDIT.json",
            "row AD-expanded source changed",
        )
        checks.check(
            "not a symbolic identity proof" in row.get("ad_expanded_row_oracle_scope", ""),
            "row AD-expanded scope boundary missing",
        )
        checks.check(
            row.get("row_ordering_scaling_ad_equivalence_closed") is True,
            "row D6 ordering/scaling/AD equivalence not closed",
        )
        checks.check(
            row.get("row_ordering_scaling_ad_audit_source")
            == "NEWTON_EULER_ROW_ORDERING_SCALING_AD_AUDIT.json",
            "row D6 audit source changed",
        )
        checks.check(
            "symbolic-certificate O(h^7) defect lane remains open" in row.get("row_ordering_scaling_ad_scope", ""),
            "row D6 scope boundary missing",
        )
        checks.check(row.get("balance_identity_closed") is True, "row balance identity not closed")
        checks.check(
            row.get("balance_identity_audit_source") == "NEWTON_EULER_BALANCE_IDENTITY_AUDIT.json",
            "row balance identity audit source changed",
        )
        checks.check(
            row.get("smooth_force_lift_source_structure_checked") is True,
            "row smooth force-lift source check missing",
        )
        checks.check(row.get("smooth_force_lift_consistency_closed") is True, "row smooth force-lift not closed")
        checks.check(
            row.get("smooth_force_lift_certificate_source") == "SMOOTH_FORCE_LIFT_CERTIFICATE.json",
            "row smooth force-lift source changed",
        )
        checks.check(
            "compact proof-tube C7 derivative bounds" in row.get("smooth_force_lift_scope", ""),
            "row smooth force-lift scope boundary missing",
        )
        checks.check(bool(row.get("symbolic_expansion")), "row symbolic expansion text missing")
        checks.check(
            "runtime row equivalence and O(h^7) defect bound remain open" in row.get("symbolic_expansion_scope", ""),
            "row expansion scope boundary missing",
        )
        checks.check(row.get("runtime_row_equivalence_proved") is True, "row runtime equivalence not closed")
        checks.check(row.get("defect_bound_O_h7_proved") is False, "row O(h^7) bound overclaimed")
        checks.check(
            row.get("certificate_status") == "balance_identity_closed_runtime_equivalence_closed_O_h7_bound_open",
            "row certificate status changed",
        )

    checks.check(target_audit.get("row_count") == summary.get("row_count"), "target audit row count mismatch")
    checks.check(
        target_audit.get("obligation_coverage_matrix", {}).get("row_obligation_link_count")
        == summary.get("row_obligation_link_count"),
        "target audit link count mismatch",
    )
    checks.check(
        proof_remaining.get("summary", {}).get("unsatisfied_close_requirement_ids")
        == summary.get("unsatisfied_close_requirement_ids"),
        "proof remaining-work PC ids mismatch",
    )
    checks.check(
        proof_closure.get("closure_state", {}).get("pc2_closed_by_direct_substitution") is True,
        "proof closure direct-substitution source missing",
    )
    checks.check(
        proof_closure.get("closure_state", {}).get("primitive_lift_route_closed") is False,
        "proof closure unexpectedly closes primitive lift route",
    )

    execution = cert.get("execution_policy", {})
    checks.check(execution.get("read_only_existing_artifacts") is True, "certificate is not read-only")
    checks.check(execution.get("default_1e_4_required") is False, "certificate requires default 1e-4")
    checks.check(execution.get("heavy_numerical_run_invoked") is False, "certificate invoked a heavy run")
    checks.check(execution.get("run_v047_invoked") is False, "certificate invoked run_v047")
    checks.check(execution.get("v048_runner_invoked") is False, "certificate invoked v048 runner")

    for token in [
        "Newton-Euler Symbolic Defect Certificate",
        "OPEN - primitive/symbolic lane not closed; direct D5 route separate",
        "Certificate complete: `False`.",
        "Primitive/symbolic-lane certified/open rows: `0/36`.",
        "Active direct-route D5 closure is carried by `D5_DYNAMIC_DIRECT_SUBSTITUTION_CERTIFICATE.md`, not by this primitive/symbolic certificate.",
        "Rows with symbolic expansion templates: `36`.",
        "Runtime-mapped rows: `36`.",
        "Runtime row layout mapping checked: `True`.",
        "Runtime expression structure checked rows: `36`.",
        "Runtime expression structure checked: `True`.",
        "Runtime template instantiation checked rows: `36`.",
        "Runtime template instantiation checked: `True`.",
        "Body-specific wrench expansion checked rows: `36`.",
        "Body-specific wrench expansion checked: `True`.",
        "Virtual-work wrench sign skeleton checked rows: `36`.",
        "Virtual-work wrench sign skeleton checked: `True`.",
        "Virtual-work template identity rows: `36`.",
        "Virtual-work template identity proved: `True`.",
        "Virtual-work template identities proved: `2/2`.",
        "Row-expanded virtual-work identity rows: `36`.",
        "Row-expanded virtual-work identity proved: `True`.",
        "Row-expanded virtual-work identities proved: `6/6`.",
        "Multiplier wrench consistency closed: `True`.",
        "Full row-expanded virtual-work identity proved: `True`.",
        "Template algebraic equivalence checked rows: `36`.",
        "Template algebraic equivalence checked: `True`.",
        "Template-level C2 subcheck closed: `True`.",
        "Balance identity closed rows: `36`.",
        "Translational balance identity closed rows: `18`.",
        "Rotational balance identity closed rows: `18`.",
        "Runtime dynamic-row formula-oracle link checked: `True`.",
        "Runtime dynamic-row formula-oracle rows: `36`.",
        "Runtime formula-row AD Jacobian probes: `3`.",
        "AD-expanded row oracle checked rows: `36`.",
        "AD-expanded row oracle checked: `True`.",
        "AD-expanded row oracle columns per row: `132`.",
        "AD-expanded symbolic oracle closure: `False`.",
        "Row-ordering/scaling/AD equivalence closed: `True`.",
        "Smooth force-lift source structure checked: `True`.",
        "Smooth force-lift consistency closed: `True`.",
        "Smooth force-lift global C7 bound proved: `True`.",
        "Runtime algebraic equivalence proved: `True`.",
        "C4 manuscript link closed: `True`.",
        "Newton-Euler row-obligation links: `180`.",
        "Open/closed Newton-Euler obligations: `1/5`.",
        "Closed Newton-Euler obligation ids: `['translational_balance_identity', 'rotational_balance_identity', 'multiplier_wrench_consistency', 'smooth_force_lift_consistency', 'symbolic_runtime_row_equivalence']`.",
        "Unsatisfied close requirements: `[]`.",
        "`C1_row_expansion`",
        "`C2_runtime_equivalence`",
        "`C3_defect_bound`",
        "`C4_manuscript_link`",
        "| `C4_manuscript_link` | `True` | connect the open certificate scaffold to Lemma stage-residual-defect without closing C3 |",
        "Manuscript Link Audit",
        "Checked: `True`.",
        "the symbolic-certificate C3 O(h^7) lane remains open while direct-route PC2 is closed separately.",
        "Closed Sub-Obligations",
        "Runtime Expression Structure Audit",
        "Checked translational/rotational rows: `18/18`.",
        "Row-level runtime-template instantiation checked: `True`.",
        "Runtime-template translational/rotational rows: `18/18`.",
        "Template-instantiation scope: confirms target-to-template mapping and required runtime terms; algebraic equivalence and O(h^7) proof remain open.",
        "Body-specific wrench expansion checked: `True`.",
        "Body-specific body0/body1 rows: `18/18`.",
        "Body-specific scope: expands proximal/distal force and torque signs for traceability; algebraic equivalence and O(h^7) proof remain open.",
        "Virtual-work wrench sign skeleton checked: `True`.",
        "Virtual-work wrench sign-skeleton rows: `36`.",
        "Virtual-work template identity proved: `True`.",
        "Virtual-work template identity rows: `36`.",
        "Virtual-work template identities proved: `2/2`.",
        "Row-expanded virtual-work identity proved: `True`.",
        "Row-expanded virtual-work identity rows: `36`.",
        "Row-expanded virtual-work identities proved: `6/6`.",
        "Virtual-work site coverage: `9/9`.",
        "Virtual-work scope: checks the D3 force/torque sign skeleton, template identity, and row-expanded lower-pair multiplier-wrench identity; remaining dynamic symbolic equivalence and O(h^7) proof remain open.",
        "Template algebraic equivalence checked: `True`.",
        "Template algebraic translational/rotational rows: `18/18`.",
        "Template algebraic scope: verifies runtime-template/body-specific expansion equality; D1/D2 balance identity is closed, while the symbolic-certificate O(h^7) lane remains open.",
        "D1/D2 balance identity audit checked: `True`.",
        "D1/D2 balance identity closed rows: `36`.",
        "Runtime dynamic-row formula-oracle link checked: `True`.",
        "Runtime dynamic-row formula-oracle rows: `36`.",
        "Runtime formula-row AD Jacobian probe count: `3`.",
        "Runtime formula-oracle scope: links all 36 dynamic rows to formula-row and AD-Jacobian evidence; the symbolic-certificate O(h^7) lane remains open.",
        "AD-expanded row oracle checked: `True`.",
        "AD-expanded row oracle rows: `36`.",
        "AD-expanded row oracle columns per row: `132`.",
        "AD-expanded row oracle scope: row-level runtime/formula AD binding is closed for all 36 Newton-Euler rows; symbolic identity and symbolic-certificate O(h^7) lane remain open.",
        "Primitive/symbolic false scope:",
        "Direct PC2 route source:",
        "Smooth force-lift source structure checked: `True`.",
        "Smooth branch stribeck velocity: `0.5`.",
        "Smooth force-lift scope: source-level Brown-McPhee smooth formula, stage-local lift structure, and compact proof-tube C7 bounds are checked for D4; the symbolic-certificate O(h^7) lane remains open.",
        "source-expression structure only",
        "Forbidden now: proof closure",
        "validate_newton_euler_symbolic_defect_certificate.py",
    ]:
        checks.check(token in cert_md, f"certificate markdown missing token: {token}")

    forbidden = cert.get("claim_policy", {}).get("forbidden_now", [])
    for token in [
        "newton_euler_symbolic_defect_certificate_complete",
        "dynamic_symbolic_oracle_complete",
        "stage_residual_O_h7_implementation_defect_proved",
        "proof_gap_closed",
        "submission_ready",
    ]:
        checks.check(token in forbidden, f"forbidden claim missing: {token}")

    if checks.errors:
        print("newton_euler_symbolic_defect_certificate=FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("newton_euler_symbolic_defect_certificate=PASS")
    print("certificate_complete=False")
    print("row_slots=36")
    print("symbolic_expanded_rows=36")
    print("runtime_mapped_rows=36")
    print("certified_rows=0")
    print("proof_gap_closed=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
