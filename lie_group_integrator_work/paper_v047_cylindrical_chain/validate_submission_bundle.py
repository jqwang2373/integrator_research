#!/usr/bin/env python3
"""Read-only submission-bundle preflight for the v047 paper package."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


PAPER = Path(__file__).resolve().parent
from paper_paths import LATEX, package_path as manuscript_path
ROOT = PAPER.parent
PIPELINE = ROOT / "v047_cylindrical_chain_pipeline"
RESULTS = PIPELINE / "results"

EXPECTED_EXAMPLES = {"single_pendulum", "double_pendulum", "four_link", "slider_crank"}
EXPECTED_DYNAMIC_ORDER_EXAMPLES = {"single_pendulum", "double_pendulum"}
EXPECTED_COVERAGE_ONLY_EXAMPLES = {"four_link", "slider_crank"}
EXPECTED_CAVEATS = {
    "sparse_speed_quantified",
    "full_tfe_stage_replacement_missing",
    "sharp_friction_coarse_order_reduction_ultra_recovered",
}
EXPECTED_OC6_REOPEN_LATEST_EXTERNAL_PROBE = "2026-06-21/9/0/0/4/False/False"


class Checks:
    def __init__(self) -> None:
        self.errors: list[str] = []

    def check(self, condition: bool, message: str) -> None:
        if not condition:
            self.errors.append(message)


def read_json(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(path)
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def read_text(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8", errors="replace")


def contains_normalized(text: str, token: str) -> bool:
    return token in text or " ".join(token.split()) in " ".join(text.split())


def package_path(path_label: str) -> Path:
    if path_label.startswith("../"):
        return (manuscript_path(path_label)).resolve()
    paper_path = manuscript_path(path_label)
    if paper_path.exists():
        return paper_path
    return ROOT / path_label


def oc6_latest_probe_marker(full_source_runner_gap: dict) -> str:
    return (
        f"{full_source_runner_gap.get('oc6_source_equivalent_reopen_readiness_latest_external_probe_date')}/"
        f"{full_source_runner_gap.get('oc6_source_equivalent_reopen_readiness_latest_external_probe_count')}/"
        f"{full_source_runner_gap.get('oc6_source_equivalent_reopen_readiness_latest_external_probe_positive_artifact_rows')}/"
        f"{full_source_runner_gap.get('oc6_source_equivalent_reopen_readiness_latest_external_probe_source_policy_rows_closed')}/"
        f"{full_source_runner_gap.get('oc6_source_equivalent_reopen_readiness_latest_external_probe_access_limited_count')}/"
        f"{full_source_runner_gap.get('oc6_source_equivalent_reopen_readiness_latest_external_probe_global_absence_proved')}/"
        f"{full_source_runner_gap.get('oc6_source_equivalent_reopen_readiness_latest_external_probe_reopen_triggered')}"
    )


def check_log_clean(checks: Checks, log_name: str) -> None:
    log_path = manuscript_path(log_name)
    checks.check(log_path.exists() and log_path.stat().st_size > 0, f"{log_name} missing or empty")
    if not log_path.exists():
        return
    patterns = [
        r"Overfull",
        r"LaTeX Warning",
        r"Package .*Warning",
        r"pdfTeX warning",
    ]
    warning_lines = [
        line
        for line in log_path.read_text(errors="replace").splitlines()
        if any(re.search(pattern, line) for pattern in patterns)
    ]
    checks.check(not warning_lines, f"{log_name} has LaTeX warnings: {warning_lines[:3]}")


def check_manifest(
    checks: Checks,
    manifest: dict,
    boundary: dict,
    summary: dict,
    objective_completion: dict,
    full_source_runner_gap: dict,
    reproducibility_manifest: dict,
) -> None:
    claim = manifest.get("accepted_claim", {})
    comparator = claim.get("comparator", {})
    primary = boundary.get("primary_claim", {})
    boundary_comparator = boundary.get("comparator", {})

    checks.check(manifest.get("schema") == "v047-submission-artifact-manifest-v1", "manifest schema changed")
    checks.check(manifest.get("recommended_pdf") == "main_cmame.pdf", "recommended PDF changed")
    checks.check(manifest.get("cmame_tex") == "main_cmame.tex", "CMAME TeX path changed")
    checks.check(manifest.get("cmame_highlights") == "highlights_cmame.txt", "CMAME highlights path changed")
    checks.check(manifest.get("cmame_declarations") == "declarations_cmame.md", "CMAME declarations path changed")
    checks.check(manifest.get("cmame_checklist") == "CMAME_SUBMISSION_CHECKLIST.md", "CMAME checklist path changed")
    checks.check(
        manifest.get("cmame_readiness_audit") == "CMAME_SUBMISSION_READINESS_AUDIT.md",
        "CMAME readiness audit path changed",
    )
    checks.check(
        manifest.get("cmame_readiness_review") == "CMAME_SUBMISSION_READINESS_REVIEW.md",
        "CMAME readiness review path changed",
    )
    checks.check(
        manifest.get("cmame_submission_integrity_audit") == "CMAME_SUBMISSION_INTEGRITY_AUDIT.md",
        "CMAME submission-integrity audit path changed",
    )
    checks.check(
        manifest.get("cmame_submission_integrity_audit_json") == "CMAME_SUBMISSION_INTEGRITY_AUDIT.json",
        "CMAME submission-integrity audit JSON path changed",
    )
    checks.check(
        manifest.get("cmame_blocker_closure_gate") == "CMAME_BLOCKER_CLOSURE_GATE.md",
        "CMAME blocker-closure gate path changed",
    )
    checks.check(
        manifest.get("cmame_blocker_closure_gate_json") == "CMAME_BLOCKER_CLOSURE_GATE.json",
        "CMAME blocker-closure gate JSON path changed",
    )
    checks.check(
        manifest.get("cmame_external_baseline_gate") == "CMAME_EXTERNAL_BASELINE_GATE.md",
        "CMAME external-baseline gate path changed",
    )
    checks.check(
        manifest.get("cmame_external_baseline_gate_json") == "CMAME_EXTERNAL_BASELINE_GATE.json",
        "CMAME external-baseline gate JSON path changed",
    )
    checks.check(
        manifest.get("cmame_proof_contract_gate") == "CMAME_PROOF_CONTRACT_GATE.md",
        "CMAME proof-contract gate path changed",
    )
    checks.check(
        manifest.get("cmame_proof_contract_gate_json") == "CMAME_PROOF_CONTRACT_GATE.json",
        "CMAME proof-contract gate JSON path changed",
    )
    checks.check(
        manifest.get("proof_closure_manifest") == "PROOF_CLOSURE_MANIFEST.md",
        "proof-closure manifest path changed",
    )
    checks.check(
        manifest.get("proof_closure_manifest_json") == "PROOF_CLOSURE_MANIFEST.json",
        "proof-closure manifest JSON path changed",
    )
    checks.check(
        manifest.get("proof_claim_traceability_audit") == "PROOF_CLAIM_TRACEABILITY_AUDIT.md",
        "proof-claim traceability audit path changed",
    )
    checks.check(
        manifest.get("proof_claim_traceability_audit_json") == "PROOF_CLAIM_TRACEABILITY_AUDIT.json",
        "proof-claim traceability audit JSON path changed",
    )
    checks.check(
        manifest.get("d5_primitive_bound_reduction_audit") == "D5_PRIMITIVE_BOUND_REDUCTION_AUDIT.md",
        "D5 primitive-bound reduction audit path changed",
    )
    checks.check(
        manifest.get("d5_primitive_bound_reduction_audit_json") == "D5_PRIMITIVE_BOUND_REDUCTION_AUDIT.json",
        "D5 primitive-bound reduction audit JSON path changed",
    )
    checks.check(
        manifest.get("d5_p_tube_constants_audit") == "D5_P_TUBE_CONSTANTS_AUDIT.md",
        "D5 P_tube constants audit path changed",
    )
    checks.check(
        manifest.get("d5_p_tube_constants_audit_json") == "D5_P_TUBE_CONSTANTS_AUDIT.json",
        "D5 P_tube constants audit JSON path changed",
    )
    checks.check(
        manifest.get("d5_p_state_lift_gap_audit") == "D5_P_STATE_LIFT_GAP_AUDIT.md",
        "D5 P_state lift-gap audit path changed",
    )
    checks.check(
        manifest.get("d5_p_state_lift_gap_audit_json") == "D5_P_STATE_LIFT_GAP_AUDIT.json",
        "D5 P_state lift-gap audit JSON path changed",
    )
    checks.check(
        manifest.get("d5_p_state_map_definition_audit") == "D5_P_STATE_MAP_DEFINITION_AUDIT.md",
        "D5 P_state map-definition audit path changed",
    )
    checks.check(
        manifest.get("d5_p_state_map_definition_audit_json") == "D5_P_STATE_MAP_DEFINITION_AUDIT.json",
        "D5 P_state map-definition audit JSON path changed",
    )
    checks.check(
        manifest.get("d5_p_state_anticircularity_audit") == "D5_P_STATE_ANTICIRCULARITY_AUDIT.md",
        "D5 P_state anti-circularity audit path changed",
    )
    checks.check(
        manifest.get("d5_p_state_anticircularity_audit_json") == "D5_P_STATE_ANTICIRCULARITY_AUDIT.json",
        "D5 P_state anti-circularity audit JSON path changed",
    )
    checks.check(
        manifest.get("d5_p_state_ps2_weighted_target_audit") == "D5_P_STATE_PS2_WEIGHTED_TARGET_AUDIT.md",
        "D5 P_state PS2 weighted target audit path changed",
    )
    checks.check(
        manifest.get("d5_p_state_ps2_weighted_target_audit_json") == "D5_P_STATE_PS2_WEIGHTED_TARGET_AUDIT.json",
        "D5 P_state PS2 weighted target audit JSON path changed",
    )
    checks.check(
        manifest.get("d5_p_state_ps2_kinematic_block_certificate")
        == "D5_P_STATE_PS2_KINEMATIC_BLOCK_CERTIFICATE.md",
        "D5 P_state PS2 kinematic-block certificate path changed",
    )
    checks.check(
        manifest.get("d5_p_state_ps2_kinematic_block_certificate_json")
        == "D5_P_STATE_PS2_KINEMATIC_BLOCK_CERTIFICATE.json",
        "D5 P_state PS2 kinematic-block certificate JSON path changed",
    )
    checks.check(
        manifest.get("d5_p_state_ps2_lie_chart_binding_audit")
        == "D5_P_STATE_PS2_LIE_CHART_BINDING_AUDIT.md",
        "D5 P_state PS2 Lie-chart binding audit path changed",
    )
    checks.check(
        manifest.get("d5_p_state_ps2_lie_chart_binding_audit_json")
        == "D5_P_STATE_PS2_LIE_CHART_BINDING_AUDIT.json",
        "D5 P_state PS2 Lie-chart binding audit JSON path changed",
    )
    checks.check(
        manifest.get("d5_p_state_ps2_row_injection_audit") == "D5_P_STATE_PS2_ROW_INJECTION_AUDIT.md",
        "D5 P_state PS2 row-injection audit path changed",
    )
    checks.check(
        manifest.get("d5_p_state_ps2_row_injection_audit_json") == "D5_P_STATE_PS2_ROW_INJECTION_AUDIT.json",
        "D5 P_state PS2 row-injection audit JSON path changed",
    )
    checks.check(
        manifest.get("d5_p_state_ps2_nonlinear_binding_audit")
        == "D5_P_STATE_PS2_NONLINEAR_BINDING_AUDIT.md",
        "D5 P_state PS2 nonlinear binding audit path changed",
    )
    checks.check(
        manifest.get("d5_p_state_ps2_nonlinear_binding_audit_json")
        == "D5_P_STATE_PS2_NONLINEAR_BINDING_AUDIT.json",
        "D5 P_state PS2 nonlinear binding audit JSON path changed",
    )
    checks.check(
        manifest.get("d5_p_state_ps2_aggregate_promotion_audit")
        == "D5_P_STATE_PS2_AGGREGATE_PROMOTION_AUDIT.md",
        "D5 P_state PS2 aggregate promotion audit path changed",
    )
    checks.check(
        manifest.get("d5_p_state_ps2_aggregate_promotion_audit_json")
        == "D5_P_STATE_PS2_AGGREGATE_PROMOTION_AUDIT.json",
        "D5 P_state PS2 aggregate promotion audit JSON path changed",
    )
    checks.check(
        manifest.get("d5_p_state_ps2_linearization_probe") == "D5_P_STATE_PS2_LINEARIZATION_PROBE.md",
        "D5 P_state PS2 linearization probe path changed",
    )
    checks.check(
        manifest.get("d5_p_state_ps2_linearization_probe_json") == "D5_P_STATE_PS2_LINEARIZATION_PROBE.json",
        "D5 P_state PS2 linearization probe JSON path changed",
    )
    checks.check(
        manifest.get("d5_p_state_ps2_linearization_probe_csv") == "D5_P_STATE_PS2_LINEARIZATION_PROBE.csv",
        "D5 P_state PS2 linearization probe CSV path changed",
    )
    checks.check(
        manifest.get("d5_p_state_ps3_conditional_conversion_audit")
        == "D5_P_STATE_PS3_CONDITIONAL_CONVERSION_AUDIT.md",
        "D5 P_state PS3 conditional conversion audit path changed",
    )
    checks.check(
        manifest.get("d5_p_state_ps3_conditional_conversion_audit_json")
        == "D5_P_STATE_PS3_CONDITIONAL_CONVERSION_AUDIT.json",
        "D5 P_state PS3 conditional conversion audit JSON path changed",
    )
    checks.check(
        manifest.get("d5_p_state_ps3_actual_instantiation_gap_audit")
        == "D5_P_STATE_PS3_ACTUAL_INSTANTIATION_GAP_AUDIT.md",
        "D5 P_state PS3 actual-instantiation gap audit path changed",
    )
    checks.check(
        manifest.get("d5_p_state_ps3_actual_instantiation_gap_audit_json")
        == "D5_P_STATE_PS3_ACTUAL_INSTANTIATION_GAP_AUDIT.json",
        "D5 P_state PS3 actual-instantiation gap audit JSON path changed",
    )
    checks.check(
        manifest.get("d5_p_state_ps3_h_acc_input_obstruction_audit")
        == "D5_P_STATE_PS3_H_ACC_INPUT_OBSTRUCTION_AUDIT.md",
        "D5 P_state PS3 h-acc input obstruction audit path changed",
    )
    checks.check(
        manifest.get("d5_p_state_ps3_h_acc_input_obstruction_audit_json")
        == "D5_P_STATE_PS3_H_ACC_INPUT_OBSTRUCTION_AUDIT.json",
        "D5 P_state PS3 h-acc input obstruction audit JSON path changed",
    )
    checks.check(
        manifest.get("d5_p_acc_map_definition_audit") == "D5_P_ACC_MAP_DEFINITION_AUDIT.md",
        "D5 P_acc map-definition audit path changed",
    )
    checks.check(
        manifest.get("d5_p_acc_map_definition_audit_json") == "D5_P_ACC_MAP_DEFINITION_AUDIT.json",
        "D5 P_acc map-definition audit JSON path changed",
    )
    checks.check(
        manifest.get("d5_p_acc_row_binding_audit") == "D5_P_ACC_ROW_BINDING_AUDIT.md",
        "D5 P_acc row-binding audit path changed",
    )
    checks.check(
        manifest.get("d5_p_acc_row_binding_audit_json") == "D5_P_ACC_ROW_BINDING_AUDIT.json",
        "D5 P_acc row-binding audit JSON path changed",
    )
    checks.check(
        manifest.get("d5_p_acc_independence_audit") == "D5_P_ACC_INDEPENDENCE_AUDIT.md",
        "D5 P_acc independence audit path changed",
    )
    checks.check(
        manifest.get("d5_p_acc_independence_audit_json") == "D5_P_ACC_INDEPENDENCE_AUDIT.json",
        "D5 P_acc independence audit JSON path changed",
    )
    checks.check(
        manifest.get("d5_p_lambda_interface_audit") == "D5_P_LAMBDA_INTERFACE_AUDIT.md",
        "D5 P_lambda interface audit path changed",
    )
    checks.check(
        manifest.get("d5_p_lambda_interface_audit_json") == "D5_P_LAMBDA_INTERFACE_AUDIT.json",
        "D5 P_lambda interface audit JSON path changed",
    )
    checks.check(
        manifest.get("d5_p_geom_chart_reduction_audit") == "D5_P_GEOM_CHART_REDUCTION_AUDIT.md",
        "D5 P_geom chart-reduction audit path changed",
    )
    checks.check(
        manifest.get("d5_p_geom_chart_reduction_audit_json") == "D5_P_GEOM_CHART_REDUCTION_AUDIT.json",
        "D5 P_geom chart-reduction audit JSON path changed",
    )
    checks.check(
        manifest.get("d5_p_gyro_bilinear_reduction_audit")
        == "D5_P_GYRO_BILINEAR_REDUCTION_AUDIT.md",
        "D5 P_gyro bilinear-reduction audit path changed",
    )
    checks.check(
        manifest.get("d5_p_gyro_bilinear_reduction_audit_json")
        == "D5_P_GYRO_BILINEAR_REDUCTION_AUDIT.json",
        "D5 P_gyro bilinear-reduction audit JSON path changed",
    )
    checks.check(
        manifest.get("d5_open_primitive_gap_audit") == "D5_OPEN_PRIMITIVE_GAP_AUDIT.md",
        "D5 open primitive gap audit path changed",
    )
    checks.check(
        manifest.get("d5_open_primitive_gap_audit_json") == "D5_OPEN_PRIMITIVE_GAP_AUDIT.json",
        "D5 open primitive gap audit JSON path changed",
    )
    checks.check(
        manifest.get("d5_primitive_obligation_closure_plan") == "D5_PRIMITIVE_OBLIGATION_CLOSURE_PLAN.md",
        "D5 primitive-obligation closure plan path changed",
    )
    checks.check(
        manifest.get("d5_primitive_obligation_closure_plan_json") == "D5_PRIMITIVE_OBLIGATION_CLOSURE_PLAN.json",
        "D5 primitive-obligation closure plan JSON path changed",
    )
    checks.check(
        manifest.get("d5_conditional_taylor_certificate") == "D5_CONDITIONAL_TAYLOR_CERTIFICATE.md",
        "D5 conditional Taylor certificate path changed",
    )
    checks.check(
        manifest.get("d5_conditional_taylor_certificate_json") == "D5_CONDITIONAL_TAYLOR_CERTIFICATE.json",
        "D5 conditional Taylor certificate JSON path changed",
    )
    checks.check(
        manifest.get("dynamic_row_oracle_gate") == "DYNAMIC_ROW_ORACLE_GATE.md",
        "dynamic row oracle gate path changed",
    )
    checks.check(
        manifest.get("dynamic_row_oracle_gate_json") == "DYNAMIC_ROW_ORACLE_GATE.json",
        "dynamic row oracle gate JSON path changed",
    )
    checks.check(
        manifest.get("newton_euler_defect_obligation_gate") == "NEWTON_EULER_DEFECT_OBLIGATION_GATE.md",
        "Newton-Euler obligation gate path changed",
    )
    checks.check(
        manifest.get("newton_euler_defect_obligation_gate_json") == "NEWTON_EULER_DEFECT_OBLIGATION_GATE.json",
        "Newton-Euler obligation gate JSON path changed",
    )
    checks.check(
        manifest.get("newton_euler_virtual_work_wrench_audit")
        == "NEWTON_EULER_VIRTUAL_WORK_WRENCH_AUDIT.md",
        "Newton-Euler virtual-work wrench audit path changed",
    )
    checks.check(
        manifest.get("newton_euler_virtual_work_wrench_audit_json")
        == "NEWTON_EULER_VIRTUAL_WORK_WRENCH_AUDIT.json",
        "Newton-Euler virtual-work wrench audit JSON path changed",
    )
    checks.check(
        manifest.get("newton_euler_ad_expanded_row_oracle_audit")
        == "NEWTON_EULER_AD_EXPANDED_ROW_ORACLE_AUDIT.md",
        "Newton-Euler AD-expanded row oracle audit path changed",
    )
    checks.check(
        manifest.get("newton_euler_ad_expanded_row_oracle_audit_json")
        == "NEWTON_EULER_AD_EXPANDED_ROW_ORACLE_AUDIT.json",
        "Newton-Euler AD-expanded row oracle audit JSON path changed",
    )
    checks.check(
        manifest.get("b1_symbolic_row_oracle_closure_certificate")
        == "B1_SYMBOLIC_ROW_ORACLE_CLOSURE_CERTIFICATE.md",
        "B1 symbolic row-oracle closure certificate path changed",
    )
    checks.check(
        manifest.get("b1_symbolic_row_oracle_closure_certificate_json")
        == "B1_SYMBOLIC_ROW_ORACLE_CLOSURE_CERTIFICATE.json",
        "B1 symbolic row-oracle closure certificate JSON path changed",
    )
    checks.check(
        manifest.get("b1_ad_expanded_symbolic_oracle_closure_certificate")
        == "B1_AD_EXPANDED_SYMBOLIC_ORACLE_CLOSURE_CERTIFICATE.md",
        "B1 AD-expanded symbolic oracle closure certificate path changed",
    )
    checks.check(
        manifest.get("b1_ad_expanded_symbolic_oracle_closure_certificate_json")
        == "B1_AD_EXPANDED_SYMBOLIC_ORACLE_CLOSURE_CERTIFICATE.json",
        "B1 AD-expanded symbolic oracle closure certificate JSON path changed",
    )
    checks.check(
        manifest.get("newton_euler_dynamic_row_closure_contract")
        == "NEWTON_EULER_DYNAMIC_ROW_CLOSURE_CONTRACT.md",
        "Newton-Euler dynamic-row closure contract path changed",
    )
    checks.check(
        manifest.get("newton_euler_dynamic_row_closure_contract_json")
        == "NEWTON_EULER_DYNAMIC_ROW_CLOSURE_CONTRACT.json",
        "Newton-Euler dynamic-row closure contract JSON path changed",
    )
    checks.check(manifest.get("submission_ready") is False, "manifest submission-ready gate changed")
    checks.check(manifest.get("mechanical_preflight_passed") is True, "manifest mechanical preflight gate changed")
    checks.check(manifest.get("quality_review_passed") is False, "manifest quality review gate changed")
    checks.check(
        manifest.get("quality_review_passed_under_narrowed_claim") is True,
        "manifest narrowed-claim quality review marker changed",
    )
    checks.check(
        manifest.get("narrowed_claim_submission_standard_met") is True,
        "manifest narrowed-claim standard marker changed",
    )
    checks.check(
        manifest.get("narrowed_claim_decision") == "submit_under_narrowed_claim",
        "manifest narrowed-claim decision marker changed",
    )
    checks.check(
        manifest.get("quality_review_scope") == "global_false_narrowed_claim_subcheck_true",
        "manifest quality review scope changed",
    )
    checks.check(manifest.get("cmame_flat_submission_dir") == "cmame_submission_flat", "CMAME flat source dir changed")
    checks.check(
        manifest.get("cmame_flat_tex") == "cmame_submission_flat/main_cmame_submission.tex",
        "CMAME flat TeX path changed",
    )
    checks.check(
        manifest.get("cmame_flat_pdf") == "cmame_submission_flat/main_cmame_submission.pdf",
        "CMAME flat PDF path changed",
    )
    checks.check(manifest.get("cmame_flat_source_archive") == "cmame_submission_flat.zip", "CMAME flat archive path changed")
    checks.check(manifest.get("concise_pdf") == "main_concise.pdf", "concise PDF path changed")
    checks.check(manifest.get("supporting_pdf") == "main.pdf", "supporting PDF changed")
    checks.check(manifest.get("submission_index") == "SUBMISSION_PACKET.md", "submission index changed")
    checks.check(manifest.get("cover_letter") == "COVER_LETTER.md", "cover letter changed")
    checks.check(manifest.get("file_inventory") == "SUBMISSION_FILE_INVENTORY.md", "file inventory changed")
    checks.check(
        manifest.get("review_response_template") == "REVIEW_RESPONSE_TEMPLATE.md",
        "review response template changed",
    )
    checks.check(
        manifest.get("source_paper_comparison") == "SOURCE_PAPER_COMPARISON.md",
        "source-paper comparison path changed",
    )

    checks.check(
        manifest.get("cross_paper_benchmark_matrix") == "CROSS_PAPER_BENCHMARK_MATRIX.md",
        "cross-paper benchmark matrix path changed",
    )
    checks.check(
        manifest.get("cross_paper_benchmark_spec") == "CROSS_PAPER_BENCHMARK_SPEC.md",
        "cross-paper benchmark spec path changed",
    )
    checks.check(
        manifest.get("cross_paper_benchmark_cases") == "CROSS_PAPER_BENCHMARK_CASES.json",
        "cross-paper benchmark cases path changed",
    )
    checks.check(
        manifest.get("external_same_test_run_queue") == "EXTERNAL_SAME_TEST_RUN_QUEUE.md",
        "external same-test run queue path changed",
    )
    checks.check(
        manifest.get("external_same_test_run_queue_json") == "EXTERNAL_SAME_TEST_RUN_QUEUE.json",
        "external same-test run queue JSON path changed",
    )
    checks.check(
        manifest.get("kissel_negrut_code_inventory") == "KISSEL_NEGRUT_CODE_INVENTORY.md",
        "Kissel/Negrut code inventory path changed",
    )
    checks.check(
        manifest.get("external_source_policy_closure_manifest") == "EXTERNAL_SOURCE_POLICY_CLOSURE_MANIFEST.md",
        "external source-policy closure manifest path changed",
    )
    checks.check(
        manifest.get("external_source_policy_closure_manifest_json")
        == "EXTERNAL_SOURCE_POLICY_CLOSURE_MANIFEST.json",
        "external source-policy closure manifest JSON path changed",
    )
    checks.check(
        manifest.get("tfe_source_policy_spec") == "TFE_SOURCE_POLICY_SPEC.md",
        "TFE source-policy spec path changed",
    )
    checks.check(
        manifest.get("tfe_source_policy_spec_json") == "TFE_SOURCE_POLICY_SPEC.json",
        "TFE source-policy spec JSON path changed",
    )
    checks.check(
        manifest.get("tfe_source_policy_row_audit") == "TFE_SOURCE_POLICY_ROW_AUDIT.md",
        "TFE source-policy row audit path changed",
    )
    checks.check(
        manifest.get("tfe_source_policy_row_audit_json") == "TFE_SOURCE_POLICY_ROW_AUDIT.json",
        "TFE source-policy row audit JSON path changed",
    )
    checks.check(
        manifest.get("tfe_b4_b7_source_policy_demotion_audit") == "TFE_B4_B7_SOURCE_POLICY_DEMOTION_AUDIT.md",
        "TFE B4/B7 source-policy demotion audit path changed",
    )
    checks.check(
        manifest.get("tfe_b4_b7_source_policy_demotion_audit_json")
        == "TFE_B4_B7_SOURCE_POLICY_DEMOTION_AUDIT.json",
        "TFE B4/B7 source-policy demotion audit JSON path changed",
    )
    checks.check(
        manifest.get("tfe_source_pendulum_model_audit") == "TFE_SOURCE_PENDULUM_MODEL_AUDIT.md",
        "TFE source pendulum model audit path changed",
    )
    checks.check(
        manifest.get("tfe_source_pendulum_model_audit_json") == "TFE_SOURCE_PENDULUM_MODEL_AUDIT.json",
        "TFE source pendulum model audit JSON path changed",
    )
    checks.check(
        manifest.get("tfe_brown_mcphee_source_law_boundary_audit")
        == "TFE_BROWN_MCPHEE_SOURCE_LAW_BOUNDARY_AUDIT.md",
        "TFE Brown-McPhee source-law boundary audit path changed",
    )
    checks.check(
        manifest.get("tfe_brown_mcphee_source_law_boundary_audit_json")
        == "TFE_BROWN_MCPHEE_SOURCE_LAW_BOUNDARY_AUDIT.json",
        "TFE Brown-McPhee source-law boundary audit JSON path changed",
    )
    checks.check(
        manifest.get("tfe_source_grid_compatibility_audit") == "TFE_SOURCE_GRID_COMPATIBILITY_AUDIT.md",
        "TFE source grid compatibility audit path changed",
    )
    checks.check(
        manifest.get("tfe_source_grid_compatibility_audit_json") == "TFE_SOURCE_GRID_COMPATIBILITY_AUDIT.json",
        "TFE source grid compatibility audit JSON path changed",
    )
    checks.check(
        manifest.get("tfe_endpoint_policy_boundary_certificate") == "TFE_ENDPOINT_POLICY_BOUNDARY_CERTIFICATE.md",
        "TFE endpoint policy boundary certificate path changed",
    )
    checks.check(
        manifest.get("tfe_endpoint_policy_boundary_certificate_json")
        == "TFE_ENDPOINT_POLICY_BOUNDARY_CERTIFICATE.json",
        "TFE endpoint policy boundary certificate JSON path changed",
    )
    checks.check(
        manifest.get("tfe_endpoint_policy_boundary_certificate_csv")
        == "TFE_ENDPOINT_POLICY_BOUNDARY_CERTIFICATE.csv",
        "TFE endpoint policy boundary certificate CSV path changed",
    )
    checks.check(
        manifest.get("cmame_reproducibility_package_manifest") == "CMAME_REPRODUCIBILITY_PACKAGE_MANIFEST.md",
        "CMAME reproducibility package manifest path changed",
    )
    checks.check(
        manifest.get("cmame_reproducibility_package_manifest_json") == "CMAME_REPRODUCIBILITY_PACKAGE_MANIFEST.json",
        "CMAME reproducibility package manifest JSON path changed",
    )
    checks.check(
        manifest.get("cmame_minimal_reproducibility_candidate_manifest")
        == "CMAME_MINIMAL_REPRODUCIBILITY_CANDIDATE_MANIFEST.md",
        "CMAME minimal reproducibility candidate manifest path changed",
    )
    checks.check(
        manifest.get("cmame_minimal_reproducibility_candidate_manifest_json")
        == "CMAME_MINIMAL_REPRODUCIBILITY_CANDIDATE_MANIFEST.json",
        "CMAME minimal reproducibility candidate manifest JSON path changed",
    )
    checks.check(
        manifest.get("objective_completion_audit") == "OBJECTIVE_COMPLETION_AUDIT.md",
        "objective completion audit path changed",
    )
    checks.check(
        manifest.get("objective_completion_audit_json") == "OBJECTIVE_COMPLETION_AUDIT.json",
        "objective completion audit JSON path changed",
    )
    checks.check(
        manifest.get("cmame_visual_legibility_audit") == "CMAME_VISUAL_LEGIBILITY_AUDIT.md",
        "CMAME visual-legibility audit path changed",
    )
    checks.check(
        manifest.get("cmame_visual_legibility_audit_json") == "CMAME_VISUAL_LEGIBILITY_AUDIT.json",
        "CMAME visual-legibility audit JSON path changed",
    )
    checks.check(
        manifest.get("cmame_figure_set_audit") == "CMAME_FIGURE_SET_AUDIT.md",
        "CMAME figure-set audit path changed",
    )
    checks.check(
        manifest.get("cmame_figure_set_audit_json") == "CMAME_FIGURE_SET_AUDIT.json",
        "CMAME figure-set audit JSON path changed",
    )
    checks.check(
        manifest.get("cmame_related_work_audit") == "CMAME_RELATED_WORK_AUDIT.md",
        "CMAME related-work audit path changed",
    )
    checks.check(
        manifest.get("cmame_related_work_audit_json") == "CMAME_RELATED_WORK_AUDIT.json",
        "CMAME related-work audit JSON path changed",
    )
    checks.check(
        manifest.get("cmame_prose_residue_audit") == "CMAME_PROSE_RESIDUE_AUDIT.md",
        "CMAME prose-residue audit path changed",
    )
    checks.check(
        manifest.get("cmame_prose_residue_audit_json") == "CMAME_PROSE_RESIDUE_AUDIT.json",
        "CMAME prose-residue audit JSON path changed",
    )
    checks.check(
        manifest.get("cmame_claim_hygiene_audit") == "CMAME_CLAIM_HYGIENE_AUDIT.md",
        "CMAME claim-hygiene audit path changed",
    )
    checks.check(
        manifest.get("cmame_claim_hygiene_audit_json") == "CMAME_CLAIM_HYGIENE_AUDIT.json",
        "CMAME claim-hygiene audit JSON path changed",
    )
    checks.check(
        manifest.get("proof_solver_scale_audit") == "PROOF_SOLVER_SCALE_AUDIT.md",
        "proof solver-scale audit path changed",
    )
    checks.check(
        manifest.get("proof_solver_scale_audit_json") == "PROOF_SOLVER_SCALE_AUDIT.json",
        "proof solver-scale audit JSON path changed",
    )
    checks.check(
        manifest.get("proof_solver_scaled_tolerance_trajectory_probe")
        == "PROOF_SOLVER_SCALED_TOLERANCE_TRAJECTORY_PROBE.md",
        "proof solver scaled-tolerance trajectory probe path changed",
    )
    checks.check(
        manifest.get("proof_solver_scaled_tolerance_trajectory_probe_json")
        == "PROOF_SOLVER_SCALED_TOLERANCE_TRAJECTORY_PROBE.json",
        "proof solver scaled-tolerance trajectory probe JSON path changed",
    )
    checks.check(
        manifest.get("proof_solver_scaled_tolerance_trajectory_probe_csv")
        == "PROOF_SOLVER_SCALED_TOLERANCE_TRAJECTORY_PROBE.csv",
        "proof solver scaled-tolerance trajectory probe CSV path changed",
    )
    checks.check(
        manifest.get("proof_solver_tolerance_regime_sweep") == "PROOF_SOLVER_TOLERANCE_REGIME_SWEEP.md",
        "proof solver tolerance-regime sweep path changed",
    )
    checks.check(
        manifest.get("proof_solver_tolerance_regime_sweep_json") == "PROOF_SOLVER_TOLERANCE_REGIME_SWEEP.json",
        "proof solver tolerance-regime sweep JSON path changed",
    )
    checks.check(
        manifest.get("proof_solver_tolerance_regime_sweep_csv") == "PROOF_SOLVER_TOLERANCE_REGIME_SWEEP.csv",
        "proof solver tolerance-regime sweep CSV path changed",
    )
    checks.check(
        manifest.get("cmame_proof_style_audit") == "CMAME_PROOF_STYLE_AUDIT.md",
        "CMAME proof-style audit path changed",
    )
    checks.check(
        manifest.get("cmame_proof_style_audit_json") == "CMAME_PROOF_STYLE_AUDIT.json",
        "CMAME proof-style audit JSON path changed",
    )
    checks.check(
        manifest.get("cmame_strict_proof_audit") == "CMAME_STRICT_PROOF_AUDIT.md",
        "CMAME strict-proof audit path changed",
    )
    checks.check(
        manifest.get("cmame_strict_proof_audit_json") == "CMAME_STRICT_PROOF_AUDIT.json",
        "CMAME strict-proof audit JSON path changed",
    )
    checks.check(
        manifest.get("cmame_strict_proof_policy_reconciliation_audit")
        == "CMAME_STRICT_PROOF_POLICY_RECONCILIATION_AUDIT.md",
        "CMAME strict-proof policy reconciliation audit path changed",
    )
    checks.check(
        manifest.get("cmame_strict_proof_policy_reconciliation_audit_json")
        == "CMAME_STRICT_PROOF_POLICY_RECONCILIATION_AUDIT.json",
        "CMAME strict-proof policy reconciliation audit JSON path changed",
    )
    checks.check(
        manifest.get("external_suite_disposition_audit") == "EXTERNAL_SUITE_DISPOSITION_AUDIT.md",
        "external suite disposition audit path changed",
    )
    checks.check(
        manifest.get("external_suite_disposition_audit_json") == "EXTERNAL_SUITE_DISPOSITION_AUDIT.json",
        "external suite disposition audit JSON path changed",
    )
    checks.check(
        manifest.get("comparison_objective_closure_reconciliation_audit")
        == "COMPARISON_OBJECTIVE_CLOSURE_RECONCILIATION_AUDIT.md",
        "comparison reconciliation audit path changed",
    )
    checks.check(
        manifest.get("comparison_objective_closure_reconciliation_audit_json")
        == "COMPARISON_OBJECTIVE_CLOSURE_RECONCILIATION_AUDIT.json",
        "comparison reconciliation audit JSON path changed",
    )
    checks.check(
        manifest.get("vp2024_code_path_disposition_audit") == "VP2024_CODE_PATH_DISPOSITION_AUDIT.md",
        "VP2024 code-path disposition audit path changed",
    )
    checks.check(
        manifest.get("vp2024_code_path_disposition_audit_json") == "VP2024_CODE_PATH_DISPOSITION_AUDIT.json",
        "VP2024 code-path disposition audit JSON path changed",
    )
    checks.check(
        manifest.get("external_suite_demotion_ledger") == "EXTERNAL_SUITE_DEMOTION_LEDGER.md",
        "external suite demotion ledger path changed",
    )
    checks.check(
        manifest.get("external_suite_demotion_ledger_json") == "EXTERNAL_SUITE_DEMOTION_LEDGER.json",
        "external suite demotion ledger JSON path changed",
    )
    checks.check(
        manifest.get("b2_source_policy_remaining_work_manifest") == "B2_SOURCE_POLICY_REMAINING_WORK_MANIFEST.md",
        "B2 source-policy remaining-work manifest path changed",
    )
    checks.check(
        manifest.get("b2_source_policy_remaining_work_manifest_json")
        == "B2_SOURCE_POLICY_REMAINING_WORK_MANIFEST.json",
        "B2 source-policy remaining-work manifest JSON path changed",
    )
    checks.check(
        manifest.get("b4_source_policy_work_precision_execution_plan")
        == "B4_SOURCE_POLICY_WORK_PRECISION_EXECUTION_PLAN.md",
        "B4 source-policy work/precision execution plan path changed",
    )
    checks.check(
        manifest.get("b4_source_policy_work_precision_execution_plan_json")
        == "B4_SOURCE_POLICY_WORK_PRECISION_EXECUTION_PLAN.json",
        "B4 source-policy work/precision execution plan JSON path changed",
    )
    checks.check(
        manifest.get("b4_existing_artifact_promotion_audit") == "B4_EXISTING_ARTIFACT_PROMOTION_AUDIT.md",
        "B4 existing-artifact promotion audit path changed",
    )
    checks.check(
        manifest.get("b4_existing_artifact_promotion_audit_json") == "B4_EXISTING_ARTIFACT_PROMOTION_AUDIT.json",
        "B4 existing-artifact promotion audit JSON path changed",
    )
    checks.check(
        manifest.get("b4_source_policy_post_execution_audit") == "B4_SOURCE_POLICY_POST_EXECUTION_AUDIT.md",
        "B4 source-policy post-execution audit path changed",
    )
    checks.check(
        manifest.get("b4_source_policy_post_execution_audit_json") == "B4_SOURCE_POLICY_POST_EXECUTION_AUDIT.json",
        "B4 source-policy post-execution audit JSON path changed",
    )
    checks.check(
        manifest.get("ra2021_double_source_policy_low_order_diagnosis")
        == "RA2021_DOUBLE_SOURCE_POLICY_LOW_ORDER_DIAGNOSIS.md",
        "RA2021 double low-order diagnosis path changed",
    )
    checks.check(
        manifest.get("ra2021_double_source_policy_low_order_diagnosis_json")
        == "RA2021_DOUBLE_SOURCE_POLICY_LOW_ORDER_DIAGNOSIS.json",
        "RA2021 double low-order diagnosis JSON path changed",
    )
    checks.check(
        manifest.get("hi2022_ra_half_double_source_policy_failure_diagnosis")
        == "HI2022_RA_HALF_DOUBLE_SOURCE_POLICY_FAILURE_DIAGNOSIS.md",
        "HI2022 rA_half double failure diagnosis path changed",
    )
    checks.check(
        manifest.get("hi2022_ra_half_double_source_policy_failure_diagnosis_json")
        == "HI2022_RA_HALF_DOUBLE_SOURCE_POLICY_FAILURE_DIAGNOSIS.json",
        "HI2022 rA_half double failure diagnosis JSON path changed",
    )
    checks.check(
        manifest.get("b4_source_policy_row_closure_readiness_ledger")
        == "B4_SOURCE_POLICY_ROW_CLOSURE_READINESS_LEDGER.md",
        "B4 source-policy row closure-readiness ledger path changed",
    )
    checks.check(
        manifest.get("b4_source_policy_row_closure_readiness_ledger_json")
        == "B4_SOURCE_POLICY_ROW_CLOSURE_READINESS_LEDGER.json",
        "B4 source-policy row closure-readiness ledger JSON path changed",
    )
    checks.check(
        manifest.get("b4_source_policy_row_closure_readiness_ledger_csv")
        == "B4_SOURCE_POLICY_ROW_CLOSURE_READINESS_LEDGER.csv",
        "B4 source-policy row closure-readiness ledger CSV path changed",
    )
    checks.check(
        manifest.get("b4_source_policy_execution_opt_in_packet")
        == "B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.md",
        "B4 source-policy execution opt-in packet path changed",
    )
    checks.check(
        manifest.get("b4_source_policy_execution_opt_in_packet_json")
        == "B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json",
        "B4 source-policy execution opt-in packet JSON path changed",
    )
    checks.check(
        manifest.get("b4_source_policy_execution_handoff_package")
        == "B4_SOURCE_POLICY_EXECUTION_HANDOFF_PACKAGE.md",
        "B4 source-policy execution handoff package path changed",
    )
    checks.check(
        manifest.get("b4_source_policy_execution_handoff_package_json")
        == "B4_SOURCE_POLICY_EXECUTION_HANDOFF_PACKAGE.json",
        "B4 source-policy execution handoff package JSON path changed",
    )
    checks.check(
        manifest.get("b4_source_policy_command_preflight_freeze")
        == "B4_SOURCE_POLICY_COMMAND_PREFLIGHT_FREEZE_20260620.md",
        "B4 source-policy command preflight freeze path changed",
    )
    checks.check(
        manifest.get("b4_source_policy_command_preflight_freeze_json")
        == "B4_SOURCE_POLICY_COMMAND_PREFLIGHT_FREEZE_20260620.json",
        "B4 source-policy command preflight freeze JSON path changed",
    )
    checks.check(
        manifest.get("b4_source_policy_expected_output_schema_audit")
        == "B4_SOURCE_POLICY_EXPECTED_OUTPUT_SCHEMA_AUDIT_20260620.md",
        "B4 expected-output schema audit path changed",
    )
    checks.check(
        manifest.get("b4_source_policy_expected_output_schema_audit_json")
        == "B4_SOURCE_POLICY_EXPECTED_OUTPUT_SCHEMA_AUDIT_20260620.json",
        "B4 expected-output schema audit JSON path changed",
    )
    checks.check(
        manifest.get("b4_expected_output_promotion_readiness_blocker_audit")
        == "B4_EXPECTED_OUTPUT_PROMOTION_READINESS_BLOCKER_AUDIT_20260620.md",
        "B4 expected-output promotion-readiness blocker audit path changed",
    )
    checks.check(
        manifest.get("b4_expected_output_promotion_readiness_blocker_audit_json")
        == "B4_EXPECTED_OUTPUT_PROMOTION_READINESS_BLOCKER_AUDIT_20260620.json",
        "B4 expected-output promotion-readiness blocker audit JSON path changed",
    )
    checks.check(
        manifest.get("oc6_source_equivalent_reopen_readiness_audit")
        == "OC6_SOURCE_EQUIVALENT_REOPEN_READINESS_AUDIT_20260620.md",
        "OC6 source-equivalent reopen-readiness audit path changed",
    )
    checks.check(
        manifest.get("oc6_source_equivalent_reopen_readiness_audit_json")
        == "OC6_SOURCE_EQUIVALENT_REOPEN_READINESS_AUDIT_20260620.json",
        "OC6 source-equivalent reopen-readiness audit JSON path changed",
    )
    checks.check(
        manifest.get("full_source_policy_runner_archive_gap_audit")
        == "FULL_SOURCE_POLICY_RUNNER_ARCHIVE_GAP_AUDIT.md",
        "full source-policy runner archive gap audit path changed",
    )
    checks.check(
        manifest.get("full_source_policy_runner_archive_gap_audit_json")
        == "FULL_SOURCE_POLICY_RUNNER_ARCHIVE_GAP_AUDIT.json",
        "full source-policy runner archive gap audit JSON path changed",
    )
    checks.check(
        manifest.get("source_policy_reopen_condition_monitor")
        == "SOURCE_POLICY_REOPEN_CONDITION_MONITOR_20260620.md",
        "source-policy reopen-condition monitor path changed",
    )
    checks.check(
        manifest.get("source_policy_reopen_condition_monitor_json")
        == "SOURCE_POLICY_REOPEN_CONDITION_MONITOR_20260620.json",
        "source-policy reopen-condition monitor JSON path changed",
    )
    objective_summary = objective_completion.get("summary", {})
    archive_action_boundary = full_source_runner_gap.get("action_boundary") or {}
    checks.check(
        manifest.get("full_source_policy_runner_archive_gap_action_boundary")
        == objective_summary.get("full_source_policy_runner_archive_gap_action_boundary")
        == archive_action_boundary,
        "manifest full source-policy runner archive action boundary changed",
    )
    checks.check(
        manifest.get("full_source_policy_runner_archive_gap_source_policy_execution_invoked")
        == objective_summary.get("full_source_policy_runner_archive_gap_source_policy_execution_invoked")
        == full_source_runner_gap.get("source_policy_execution_invoked")
        is False,
        "manifest full source-policy runner archive execution-invoked boundary changed",
    )
    checks.check(
        manifest.get("full_source_policy_runner_archive_gap_safe_action_ids")
        == objective_summary.get("full_source_policy_runner_archive_gap_safe_action_ids")
        == full_source_runner_gap.get("safe_action_ids"),
        "manifest full source-policy runner archive safe action IDs changed",
    )
    checks.check(
        manifest.get("full_source_policy_runner_archive_gap_opt_in_action_ids")
        == objective_summary.get("full_source_policy_runner_archive_gap_opt_in_action_ids")
        == full_source_runner_gap.get("opt_in_action_ids"),
        "manifest full source-policy runner archive opt-in action IDs changed",
    )
    checks.check(
        archive_action_boundary.get("source_policy_execution_allowed_now") is False
        and archive_action_boundary.get("exact_b4_opt_in_required_for_execution") is True
        and archive_action_boundary.get("safe_without_b4_opt_in_count") == 4
        and archive_action_boundary.get("opt_in_required_action_count") == 1
        and archive_action_boundary.get("opt_in_required_command_count") == 13
        and archive_action_boundary.get("opt_in_required_mapped_external_rows") == 20,
        "manifest full source-policy runner archive action boundary has unexpected counts",
    )
    narrowed_archive_boundary = manifest.get("narrowed_archive_boundary", {})
    expected_narrowed_archive_boundary = reproducibility_manifest.get("narrowed_archive_boundary", {})
    checks.check(
        narrowed_archive_boundary == expected_narrowed_archive_boundary,
        "manifest narrowed archive boundary does not match reproducibility package manifest",
    )
    checks.check(
        narrowed_archive_boundary.get("schema") == "narrowed-repro-code-archive-boundary-v1"
        and narrowed_archive_boundary.get("status")
        == "narrowed_archive_ready_not_full_source_policy_runner_archive"
        and narrowed_archive_boundary.get("scope") == "narrowed_claim_only"
        and narrowed_archive_boundary.get("blocking_ids") == objective_completion.get("blocking_ids")
        and narrowed_archive_boundary.get("blocker_status_by_id")
        == objective_completion.get("blocker_status_by_id")
        and narrowed_archive_boundary.get("blocker_required_to_close_by_id")
        == objective_completion.get("blocker_required_to_close_by_id")
        and narrowed_archive_boundary.get("blocker_safe_next_actions_by_id")
        == objective_completion.get("blocker_safe_next_actions_by_id")
        and narrowed_archive_boundary.get("blocker_opt_in_required_actions_by_id")
        == objective_completion.get("blocker_opt_in_required_actions_by_id")
        and narrowed_archive_boundary.get("source_policy_closed_ratio")
        == objective_completion.get("source_policy_closed_ratio")
        == "0/40",
        "manifest narrowed archive blocker/source-policy boundary changed",
    )
    checks.check(
        manifest.get("objective_blocker_required_to_close_by_id")
        == objective_completion.get("blocker_required_to_close_by_id")
        and manifest.get("objective_blocker_safe_next_actions_by_id")
        == objective_completion.get("blocker_safe_next_actions_by_id")
        and manifest.get("objective_blocker_opt_in_required_actions_by_id")
        == objective_completion.get("blocker_opt_in_required_actions_by_id"),
        "manifest objective blocker closure/action aliases are stale",
    )
    checks.check(
        manifest.get("blocker_required_to_close_by_id")
        == manifest.get("objective_blocker_required_to_close_by_id")
        == objective_completion.get("blocker_required_to_close_by_id")
        and manifest.get("blocker_safe_next_actions_by_id")
        == manifest.get("objective_blocker_safe_next_actions_by_id")
        == objective_completion.get("blocker_safe_next_actions_by_id")
        and manifest.get("blocker_opt_in_required_actions_by_id")
        == manifest.get("objective_blocker_opt_in_required_actions_by_id")
        == objective_completion.get("blocker_opt_in_required_actions_by_id"),
        "manifest generic blocker closure/action aliases are stale",
    )
    checks.check(
        narrowed_archive_boundary.get("current_archive_usable_as_full_source_policy_runner_archive")
        is False
        and narrowed_archive_boundary.get("source_policy_execution_allowed_now") is False
        and narrowed_archive_boundary.get("exact_b4_opt_in_required_for_execution") is True
        and narrowed_archive_boundary.get("safe_action_ids") == full_source_runner_gap.get("safe_action_ids")
        and narrowed_archive_boundary.get("opt_in_action_ids") == full_source_runner_gap.get("opt_in_action_ids"),
        "manifest narrowed archive use/action boundary changed",
    )
    checks.check(
        manifest.get("narrowed_archive_boundary_status") == narrowed_archive_boundary.get("status")
        and manifest.get("narrowed_archive_boundary_source_policy_closed_ratio")
        == narrowed_archive_boundary.get("source_policy_closed_ratio")
        and manifest.get(
            "narrowed_archive_boundary_current_archive_usable_as_full_source_policy_runner_archive"
        )
        == narrowed_archive_boundary.get(
            "current_archive_usable_as_full_source_policy_runner_archive"
        )
        and manifest.get("narrowed_archive_boundary_source_policy_execution_allowed_now")
        == narrowed_archive_boundary.get("source_policy_execution_allowed_now")
        and manifest.get("narrowed_archive_boundary_exact_b4_opt_in_required_for_execution")
        == narrowed_archive_boundary.get("exact_b4_opt_in_required_for_execution")
        and manifest.get("narrowed_archive_boundary_safe_action_ids")
        == narrowed_archive_boundary.get("safe_action_ids")
        and manifest.get("narrowed_archive_boundary_opt_in_action_ids")
        == narrowed_archive_boundary.get("opt_in_action_ids"),
        "manifest narrowed archive top-level aliases are stale",
    )
    checks.check(
        manifest.get("oc6_reopen_latest_external_probe")
        == oc6_latest_probe_marker(full_source_runner_gap)
        == EXPECTED_OC6_REOPEN_LATEST_EXTERNAL_PROBE,
        "manifest OC6 latest external probe marker changed",
    )
    checks.check(
        manifest.get("oc6_reopen_latest_external_probe_date") == "2026-06-21"
        and manifest.get("oc6_reopen_latest_external_probe_count") == 9
        and manifest.get("oc6_reopen_latest_external_probe_positive_artifact_rows") == 0
        and manifest.get("oc6_reopen_latest_external_probe_source_policy_rows_closed") == 0
        and manifest.get("oc6_reopen_latest_external_probe_access_limited_count") == 4
        and manifest.get("oc6_reopen_latest_external_probe_global_absence_proved") is False
        and manifest.get("oc6_reopen_latest_external_probe_reopen_triggered") is False,
        "manifest OC6 latest external probe field tuple changed",
    )
    checks.check(
        manifest.get("ra2021_source_policy_row_audit") == "RA2021_SOURCE_POLICY_ROW_AUDIT.md",
        "RA2021 source-policy row audit path changed",
    )
    checks.check(
        manifest.get("ra2021_source_policy_row_audit_json") == "RA2021_SOURCE_POLICY_ROW_AUDIT.json",
        "RA2021 source-policy row audit JSON path changed",
    )
    checks.check(
        manifest.get("ra2021_source_identity_audit") == "RA2021_SOURCE_IDENTITY_AUDIT.md",
        "RA2021 source-identity audit path changed",
    )
    checks.check(
        manifest.get("ra2021_source_identity_audit_json") == "RA2021_SOURCE_IDENTITY_AUDIT.json",
        "RA2021 source-identity audit JSON path changed",
    )
    checks.check(
        manifest.get("hi2022_policy_decision_audit") == "HI2022_POLICY_DECISION_AUDIT.md",
        "HI2022 policy-decision audit path changed",
    )
    checks.check(
        manifest.get("hi2022_policy_decision_audit_json") == "HI2022_POLICY_DECISION_AUDIT.json",
        "HI2022 policy-decision audit JSON path changed",
    )
    checks.check(
        manifest.get("hi2022_source_policy_row_audit") == "HI2022_SOURCE_POLICY_ROW_AUDIT.md",
        "HI2022 source-policy row audit path changed",
    )
    checks.check(
        manifest.get("hi2022_source_policy_row_audit_json") == "HI2022_SOURCE_POLICY_ROW_AUDIT.json",
        "HI2022 source-policy row audit JSON path changed",
    )
    checks.check(
        manifest.get("hi2022_t8_tolerance_repair_audit") == "HI2022_T8_TOLERANCE_REPAIR_AUDIT.md",
        "HI2022 T=8 tolerance-repair audit path changed",
    )
    checks.check(
        manifest.get("hi2022_t8_tolerance_repair_audit_json") == "HI2022_T8_TOLERANCE_REPAIR_AUDIT.json",
        "HI2022 T=8 tolerance-repair audit JSON path changed",
    )
    checks.check(manifest.get("claim_boundary") == "CLAIM_BOUNDARY.json", "claim boundary path changed")
    checks.check(manifest.get("full_tfe_stage_replacement") is False, "manifest full-TFE marker changed")
    checks.check(
        manifest.get("full_generator_invoked_by_submission_checks") is False,
        "manifest says submission checks invoke full generator",
    )

    checks.check(claim.get("type") == "conditional_formal_order_comparison", "manifest claim type changed")
    checks.check(claim.get("accepted_method") == primary.get("accepted_method") == "Gauss6/FullVA", "method mismatch")
    checks.check(claim.get("method_order_claim") == primary.get("method_order_claim") == 6, "method order mismatch")
    checks.check(
        claim.get("smooth_projected_orders", {}).get("position")
        == primary.get("smooth_projected_orders", {}).get("position")
        == 7.161,
        "smooth position order mismatch",
    )
    checks.check(
        claim.get("smooth_projected_orders", {}).get("velocity")
        == primary.get("smooth_projected_orders", {}).get("velocity")
        == 7.066,
        "smooth velocity order mismatch",
    )
    checks.check(comparator.get("expected_order") == boundary_comparator.get("expected_order") == 5, "comparator order mismatch")
    checks.check(set(claim.get("accepted_examples", [])) == EXPECTED_EXAMPLES, "manifest example set mismatch")
    checks.check(set(primary.get("accepted_examples", [])) == EXPECTED_EXAMPLES, "boundary example set mismatch")
    checks.check(
        primary.get("accepted_examples_role") == "mechanism_coverage_examples_not_all_dynamic_order",
        "boundary example role changed",
    )
    checks.check(
        set(primary.get("accepted_dynamic_order_examples", [])) == EXPECTED_DYNAMIC_ORDER_EXAMPLES,
        "boundary dynamic-order examples changed",
    )
    checks.check(
        set(primary.get("accepted_mechanism_coverage_examples", [])) == EXPECTED_EXAMPLES,
        "boundary mechanism-coverage examples changed",
    )
    checks.check(
        set(primary.get("coverage_only_dynamic_order_examples", [])) == EXPECTED_COVERAGE_ONLY_EXAMPLES,
        "boundary coverage-only dynamic-order examples changed",
    )
    checks.check(set(boundary.get("open_caveats", [])) == EXPECTED_CAVEATS, "boundary caveat set mismatch")
    checks.check(set(manifest.get("open_caveats", [])) == EXPECTED_CAVEATS, "manifest caveat set mismatch")
    checks.check(summary.get("asme_gate", {}).get("status") == primary.get("asme_gate_status"), "summary ASME status mismatch")
    checks.check(set(summary.get("asme_gate", {}).get("models", {})) == EXPECTED_EXAMPLES, "summary example set mismatch")

    required_submission_files = set(manifest.get("required_submission_files", []))
    checks.check(
        required_submission_files
        == {
            "main_cmame.pdf",
            "main_cmame.tex",
            "highlights_cmame.txt",
            "declarations_cmame.md",
            "CMAME_SUBMISSION_CHECKLIST.md",
            "CMAME_SUBMISSION_READINESS_AUDIT.md",
            "CMAME_SUBMISSION_READINESS_REVIEW.md",
            "CMAME_SUBMISSION_INTEGRITY_AUDIT.md",
            "CMAME_SUBMISSION_INTEGRITY_AUDIT.json",
            "REFERENCE_METADATA_AUDIT.md",
            "REFERENCE_METADATA_AUDIT.json",
            "CMAME_BLOCKER_CLOSURE_GATE.md",
            "CMAME_BLOCKER_CLOSURE_GATE.json",
            "CMAME_EXTERNAL_BASELINE_GATE.md",
            "CMAME_EXTERNAL_BASELINE_GATE.json",
            "CMAME_PROOF_CONTRACT_GATE.md",
            "CMAME_PROOF_CONTRACT_GATE.json",
            "CMAME_VISUAL_LEGIBILITY_AUDIT.md",
            "CMAME_VISUAL_LEGIBILITY_AUDIT.json",
            "CMAME_FIGURE_SET_AUDIT.md",
            "CMAME_FIGURE_SET_AUDIT.json",
            "CMAME_RELATED_WORK_AUDIT.md",
            "CMAME_RELATED_WORK_AUDIT.json",
            "CMAME_PROSE_RESIDUE_AUDIT.md",
            "CMAME_PROSE_RESIDUE_AUDIT.json",
            "CMAME_CLAIM_HYGIENE_AUDIT.md",
            "CMAME_CLAIM_HYGIENE_AUDIT.json",
            "DYNAMIC_ROW_ORACLE_GATE.md",
            "DYNAMIC_ROW_ORACLE_GATE.json",
            "README_CMAME_FLAT_SUBMISSION.md",
            "cmame_submission_flat/main_cmame_submission.tex",
            "cmame_submission_flat/main_cmame_submission.pdf",
            "cmame_submission_flat.zip",
            "cmame_submission_flat/highlights_cmame.txt",
            "cmame_submission_flat/declarations_cmame.md",
            "cmame_submission_flat/Figure_1_convergence.png",
            "cmame_submission_flat/Figure_2_asme_lower_pair_graph_bridge.png",
            "cmame_submission_flat/Figure_3_asme_closed_loop_kinematic_fullva.png",
            "cmame_submission_flat/Figure_4_order_closure_blend.png",
            "cmame_submission_flat/Figure_5_velocity_compression.png",
            "cmame_submission_flat/Figure_6_sparse_speed_gap.png",
            "cmame_submission_flat/Figure_7_strict_common_reference_work_precision.png",
            "cmame_submission_flat/Figure_8_claim_boundary_limitations.png",
            "cmame_submission_flat/Figure_9_coarse_baseline_work_precision.png",
            "cmame_submission_flat/Figure_10_closed_loop_true_dynamic_order.png",
            "cmame_submission_flat/Figure_11_method_stage_architecture.png",
            "cmame_submission_flat/Figure_12_all_method_result_matrix.png",
            "cmame_submission_flat/Figure_13_work_precision_compendium.png",
            "COVER_LETTER.md",
            "SUBMISSION_PACKET.md",
            "SUBMISSION_ARTIFACT_MANIFEST.json",
            "SUBMISSION_FILE_INVENTORY.md",
            "REVIEW_RESPONSE_TEMPLATE.md",
            "CLAIM_BOUNDARY.json",
            "figures/convergence.png",
            "figures/asme_lower_pair_graph_bridge.png",
            "figures/asme_closed_loop_kinematic_fullva.png",
            "figures/order_closure_blend.png",
            "figures/velocity_compression.png",
            "figures/sparse_speed_gap.png",
            "figures/strict_common_reference_work_precision.png",
            "figures/claim_boundary_limitations.png",
            "figures/coarse_baseline_work_precision.png",
            "figures/closed_loop_true_dynamic_order.png",
            "figures/method_stage_architecture.png",
            "figures/all_method_result_matrix.png",
            "figures/work_precision_compendium.png",
        },
        "required submission file set changed",
    )

    for file_label in sorted(required_submission_files):
        path = package_path(file_label)
        checks.check(path.exists() and path.stat().st_size > 0, f"required submission file missing or empty: {file_label}")

    for file_label in manifest.get("evidence_anchors", []):
        path = package_path(file_label)
        checks.check(path.exists() and path.stat().st_size > 0, f"evidence anchor missing or empty: {file_label}")

    checks.check("complete_source_paper_residual_reproduction" in manifest.get("non_claims", []), "source-paper non-claim missing")
    checks.check("accepted_independent_full_tfe_stage_replacement" in manifest.get("non_claims", []), "full-TFE non-claim missing")
    checks.check("sparse_ad_already_faster_than_dense_jacfwd" in manifest.get("non_claims", []), "sparse speed non-claim missing")
    checks.check("PROOF_EVIDENCE_MATRIX.md" in manifest.get("evidence_anchors", []), "proof evidence matrix anchor missing")
    checks.check(
        "PROOF_NUMERICAL_SCALE_AUDIT.md" in manifest.get("evidence_anchors", []),
        "proof numerical scale audit anchor missing",
    )
    checks.check(
        "PROOF_NUMERICAL_SCALE_AUDIT.json" in manifest.get("evidence_anchors", []),
        "proof numerical scale audit JSON anchor missing",
    )
    checks.check(
        "PROOF_SOLVER_SCALE_AUDIT.md" in manifest.get("evidence_anchors", []),
        "proof solver-scale audit anchor missing",
    )
    checks.check(
        "PROOF_SOLVER_SCALE_AUDIT.json" in manifest.get("evidence_anchors", []),
        "proof solver-scale audit JSON anchor missing",
    )
    checks.check(
        "PROOF_SOLVER_SCALED_TOLERANCE_PROBE.md" in manifest.get("evidence_anchors", []),
        "proof solver scaled-tolerance probe anchor missing",
    )
    checks.check(
        "PROOF_SOLVER_SCALED_TOLERANCE_PROBE.json" in manifest.get("evidence_anchors", []),
        "proof solver scaled-tolerance probe JSON anchor missing",
    )
    checks.check(
        "PROOF_SOLVER_SCALED_TOLERANCE_PROBE.csv" in manifest.get("evidence_anchors", []),
        "proof solver scaled-tolerance probe CSV anchor missing",
    )
    checks.check(
        "PROOF_SOLVER_SCALED_TOLERANCE_TRAJECTORY_PROBE.md" in manifest.get("evidence_anchors", []),
        "proof solver scaled-tolerance trajectory probe anchor missing",
    )
    checks.check(
        "PROOF_SOLVER_SCALED_TOLERANCE_TRAJECTORY_PROBE.json" in manifest.get("evidence_anchors", []),
        "proof solver scaled-tolerance trajectory probe JSON anchor missing",
    )
    checks.check(
        "PROOF_SOLVER_SCALED_TOLERANCE_TRAJECTORY_PROBE.csv" in manifest.get("evidence_anchors", []),
        "proof solver scaled-tolerance trajectory probe CSV anchor missing",
    )
    checks.check(
        "PROOF_SOLVER_TOLERANCE_REGIME_SWEEP.md" in manifest.get("evidence_anchors", []),
        "proof solver tolerance-regime sweep anchor missing",
    )
    checks.check(
        "PROOF_SOLVER_TOLERANCE_REGIME_SWEEP.json" in manifest.get("evidence_anchors", []),
        "proof solver tolerance-regime sweep JSON anchor missing",
    )
    checks.check(
        "PROOF_SOLVER_TOLERANCE_REGIME_SWEEP.csv" in manifest.get("evidence_anchors", []),
        "proof solver tolerance-regime sweep CSV anchor missing",
    )
    checks.check(
        "CMAME_PROOF_STYLE_AUDIT.md" in manifest.get("evidence_anchors", []),
        "CMAME proof-style audit anchor missing",
    )
    checks.check(
        "CMAME_PROOF_STYLE_AUDIT.json" in manifest.get("evidence_anchors", []),
        "CMAME proof-style audit JSON anchor missing",
    )
    checks.check(
        "CMAME_STRICT_PROOF_AUDIT.md" in manifest.get("evidence_anchors", []),
        "CMAME strict-proof audit anchor missing",
    )
    checks.check(
        "CMAME_STRICT_PROOF_AUDIT.json" in manifest.get("evidence_anchors", []),
        "CMAME strict-proof audit JSON anchor missing",
    )
    checks.check(
        "CMAME_STRICT_PROOF_POLICY_RECONCILIATION_AUDIT.md" in manifest.get("evidence_anchors", []),
        "CMAME strict-proof policy reconciliation audit anchor missing",
    )
    checks.check(
        "CMAME_STRICT_PROOF_POLICY_RECONCILIATION_AUDIT.json" in manifest.get("evidence_anchors", []),
        "CMAME strict-proof policy reconciliation audit JSON anchor missing",
    )
    checks.check(
        "CMAME_PROSE_RESIDUE_AUDIT.md" in manifest.get("evidence_anchors", []),
        "CMAME prose-residue audit anchor missing",
    )
    checks.check(
        "CMAME_PROSE_RESIDUE_AUDIT.json" in manifest.get("evidence_anchors", []),
        "CMAME prose-residue audit JSON anchor missing",
    )
    checks.check(
        "CMAME_REPRODUCIBILITY_PACKAGE_MANIFEST.md" in manifest.get("evidence_anchors", []),
        "CMAME reproducibility package manifest anchor missing",
    )
    checks.check(
        "CMAME_REPRODUCIBILITY_PACKAGE_MANIFEST.json" in manifest.get("evidence_anchors", []),
        "CMAME reproducibility package manifest JSON anchor missing",
    )
    checks.check(
        "CMAME_MINIMAL_REPRODUCIBILITY_CANDIDATE_MANIFEST.md" in manifest.get("evidence_anchors", []),
        "CMAME minimal reproducibility candidate manifest anchor missing",
    )
    checks.check(
        "CMAME_MINIMAL_REPRODUCIBILITY_CANDIDATE_MANIFEST.json" in manifest.get("evidence_anchors", []),
        "CMAME minimal reproducibility candidate manifest JSON anchor missing",
    )
    checks.check(
        "OBJECTIVE_COMPLETION_AUDIT.md" in manifest.get("evidence_anchors", []),
        "objective completion audit anchor missing",
    )
    checks.check(
        "OBJECTIVE_COMPLETION_AUDIT.json" in manifest.get("evidence_anchors", []),
        "objective completion audit JSON anchor missing",
    )
    checks.check(
        "validate_cmame_reproducibility_package_manifest.py" in manifest.get("validators", []),
        "CMAME reproducibility package manifest validator missing",
    )
    checks.check(
        "validate_cmame_minimal_reproducibility_candidate.py" in manifest.get("validators", []),
        "CMAME minimal reproducibility candidate validator missing",
    )
    checks.check(
        "CMAME_CLAIM_HYGIENE_AUDIT.md" in manifest.get("evidence_anchors", []),
        "CMAME claim-hygiene audit anchor missing",
    )
    checks.check(
        "CMAME_CLAIM_HYGIENE_AUDIT.json" in manifest.get("evidence_anchors", []),
        "CMAME claim-hygiene audit JSON anchor missing",
    )
    checks.check("SOURCE_PAPER_COMPARISON.md" in manifest.get("evidence_anchors", []), "source-paper comparison anchor missing")
    checks.check(
        "CROSS_PAPER_BENCHMARK_MATRIX.md" in manifest.get("evidence_anchors", []),
        "cross-paper benchmark matrix anchor missing",
    )
    checks.check(
        "CROSS_PAPER_BENCHMARK_SPEC.md" in manifest.get("evidence_anchors", []),
        "cross-paper benchmark spec anchor missing",
    )
    checks.check(
        "CROSS_PAPER_BENCHMARK_CASES.json" in manifest.get("evidence_anchors", []),
        "cross-paper benchmark cases anchor missing",
    )
    checks.check(
        "EXTERNAL_SAME_TEST_RUN_QUEUE.md" in manifest.get("evidence_anchors", []),
        "external same-test run queue anchor missing",
    )
    checks.check(
        "EXTERNAL_SAME_TEST_RUN_QUEUE.json" in manifest.get("evidence_anchors", []),
        "external same-test run queue JSON anchor missing",
    )
    checks.check(
        "KISSEL_NEGRUT_CODE_INVENTORY.md" in manifest.get("evidence_anchors", []),
        "Kissel/Negrut code inventory anchor missing",
    )
    checks.check(
        "EXTERNAL_SUITE_DISPOSITION_AUDIT.md" in manifest.get("evidence_anchors", []),
        "external suite disposition audit anchor missing",
    )
    checks.check(
        "EXTERNAL_SUITE_DISPOSITION_AUDIT.json" in manifest.get("evidence_anchors", []),
        "external suite disposition audit JSON anchor missing",
    )
    checks.check(
        "EXTERNAL_SOURCE_POLICY_CLOSURE_MANIFEST.md" in manifest.get("evidence_anchors", []),
        "external source-policy closure manifest anchor missing",
    )
    checks.check(
        "EXTERNAL_SOURCE_POLICY_CLOSURE_MANIFEST.json" in manifest.get("evidence_anchors", []),
        "external source-policy closure manifest JSON anchor missing",
    )
    checks.check(
        "TFE_SOURCE_POLICY_SPEC.md" in manifest.get("evidence_anchors", []),
        "TFE source-policy spec anchor missing",
    )
    checks.check(
        "TFE_SOURCE_POLICY_SPEC.json" in manifest.get("evidence_anchors", []),
        "TFE source-policy spec JSON anchor missing",
    )
    checks.check(
        "TFE_SOURCE_POLICY_ROW_AUDIT.md" in manifest.get("evidence_anchors", []),
        "TFE source-policy row audit anchor missing",
    )
    checks.check(
        "TFE_SOURCE_POLICY_ROW_AUDIT.json" in manifest.get("evidence_anchors", []),
        "TFE source-policy row audit JSON anchor missing",
    )
    checks.check(
        "TFE_B4_B7_SOURCE_POLICY_DEMOTION_AUDIT.md" in manifest.get("evidence_anchors", []),
        "TFE B4/B7 source-policy demotion audit anchor missing",
    )
    checks.check(
        "TFE_B4_B7_SOURCE_POLICY_DEMOTION_AUDIT.json" in manifest.get("evidence_anchors", []),
        "TFE B4/B7 source-policy demotion audit JSON anchor missing",
    )
    checks.check(
        "TFE_SOURCE_PENDULUM_MODEL_AUDIT.md" in manifest.get("evidence_anchors", []),
        "TFE source pendulum model audit anchor missing",
    )
    checks.check(
        "TFE_SOURCE_PENDULUM_MODEL_AUDIT.json" in manifest.get("evidence_anchors", []),
        "TFE source pendulum model audit JSON anchor missing",
    )
    checks.check(
        "TFE_BROWN_MCPHEE_SOURCE_LAW_BOUNDARY_AUDIT.md" in manifest.get("evidence_anchors", []),
        "TFE Brown-McPhee source-law boundary audit anchor missing",
    )
    checks.check(
        "TFE_BROWN_MCPHEE_SOURCE_LAW_BOUNDARY_AUDIT.json" in manifest.get("evidence_anchors", []),
        "TFE Brown-McPhee source-law boundary audit JSON anchor missing",
    )
    checks.check(
        "TFE_SOURCE_GRID_COMPATIBILITY_AUDIT.md" in manifest.get("evidence_anchors", []),
        "TFE source grid compatibility audit anchor missing",
    )
    checks.check(
        "TFE_SOURCE_GRID_COMPATIBILITY_AUDIT.json" in manifest.get("evidence_anchors", []),
        "TFE source grid compatibility audit JSON anchor missing",
    )
    checks.check(
        "TFE_ENDPOINT_POLICY_BOUNDARY_CERTIFICATE.md" in manifest.get("evidence_anchors", []),
        "TFE endpoint policy boundary certificate anchor missing",
    )
    checks.check(
        "TFE_ENDPOINT_POLICY_BOUNDARY_CERTIFICATE.json" in manifest.get("evidence_anchors", []),
        "TFE endpoint policy boundary certificate JSON anchor missing",
    )
    checks.check(
        "TFE_ENDPOINT_POLICY_BOUNDARY_CERTIFICATE.csv" in manifest.get("evidence_anchors", []),
        "TFE endpoint policy boundary certificate CSV anchor missing",
    )
    checks.check(
        "COMPARISON_OBJECTIVE_CLOSURE_RECONCILIATION_AUDIT.md" in manifest.get("evidence_anchors", []),
        "comparison reconciliation audit anchor missing",
    )
    checks.check(
        "COMPARISON_OBJECTIVE_CLOSURE_RECONCILIATION_AUDIT.json" in manifest.get("evidence_anchors", []),
        "comparison reconciliation audit JSON anchor missing",
    )
    checks.check(
        "VP2024_CODE_PATH_DISPOSITION_AUDIT.md" in manifest.get("evidence_anchors", []),
        "VP2024 code-path disposition audit anchor missing",
    )
    checks.check(
        "VP2024_CODE_PATH_DISPOSITION_AUDIT.json" in manifest.get("evidence_anchors", []),
        "VP2024 code-path disposition audit JSON anchor missing",
    )
    checks.check(
        "EXTERNAL_SUITE_DEMOTION_LEDGER.md" in manifest.get("evidence_anchors", []),
        "external suite demotion ledger anchor missing",
    )
    checks.check(
        "EXTERNAL_SUITE_DEMOTION_LEDGER.json" in manifest.get("evidence_anchors", []),
        "external suite demotion ledger JSON anchor missing",
    )
    checks.check(
        "B2_SOURCE_POLICY_REMAINING_WORK_MANIFEST.md" in manifest.get("evidence_anchors", []),
        "B2 source-policy remaining-work manifest anchor missing",
    )
    checks.check(
        "B2_SOURCE_POLICY_REMAINING_WORK_MANIFEST.json" in manifest.get("evidence_anchors", []),
        "B2 source-policy remaining-work manifest JSON anchor missing",
    )
    checks.check(
        "B4_SOURCE_POLICY_WORK_PRECISION_EXECUTION_PLAN.md" in manifest.get("evidence_anchors", []),
        "B4 source-policy work/precision execution plan anchor missing",
    )
    checks.check(
        "B4_SOURCE_POLICY_WORK_PRECISION_EXECUTION_PLAN.json" in manifest.get("evidence_anchors", []),
        "B4 source-policy work/precision execution plan JSON anchor missing",
    )
    checks.check(
        "B4_EXISTING_ARTIFACT_PROMOTION_AUDIT.md" in manifest.get("evidence_anchors", []),
        "B4 existing-artifact promotion audit anchor missing",
    )
    checks.check(
        "B4_EXISTING_ARTIFACT_PROMOTION_AUDIT.json" in manifest.get("evidence_anchors", []),
        "B4 existing-artifact promotion audit JSON anchor missing",
    )
    checks.check(
        "B4_SOURCE_POLICY_POST_EXECUTION_AUDIT.md" in manifest.get("evidence_anchors", []),
        "B4 source-policy post-execution audit anchor missing",
    )
    checks.check(
        "B4_SOURCE_POLICY_POST_EXECUTION_AUDIT.json" in manifest.get("evidence_anchors", []),
        "B4 source-policy post-execution audit JSON anchor missing",
    )
    checks.check(
        "RA2021_DOUBLE_SOURCE_POLICY_LOW_ORDER_DIAGNOSIS.md" in manifest.get("evidence_anchors", []),
        "RA2021 double low-order diagnosis anchor missing",
    )
    checks.check(
        "RA2021_DOUBLE_SOURCE_POLICY_LOW_ORDER_DIAGNOSIS.json" in manifest.get("evidence_anchors", []),
        "RA2021 double low-order diagnosis JSON anchor missing",
    )
    checks.check(
        "HI2022_RA_HALF_DOUBLE_SOURCE_POLICY_FAILURE_DIAGNOSIS.md" in manifest.get("evidence_anchors", []),
        "HI2022 rA_half double failure diagnosis anchor missing",
    )
    checks.check(
        "HI2022_RA_HALF_DOUBLE_SOURCE_POLICY_FAILURE_DIAGNOSIS.json" in manifest.get("evidence_anchors", []),
        "HI2022 rA_half double failure diagnosis JSON anchor missing",
    )
    checks.check(
        "B4_SOURCE_POLICY_ROW_CLOSURE_READINESS_LEDGER.md" in manifest.get("evidence_anchors", []),
        "B4 source-policy row closure-readiness ledger anchor missing",
    )
    checks.check(
        "B4_SOURCE_POLICY_ROW_CLOSURE_READINESS_LEDGER.json" in manifest.get("evidence_anchors", []),
        "B4 source-policy row closure-readiness ledger JSON anchor missing",
    )
    checks.check(
        "B4_SOURCE_POLICY_ROW_CLOSURE_READINESS_LEDGER.csv" in manifest.get("evidence_anchors", []),
        "B4 source-policy row closure-readiness ledger CSV anchor missing",
    )
    checks.check(
        "B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.md" in manifest.get("evidence_anchors", []),
        "B4 source-policy execution opt-in packet anchor missing",
    )
    checks.check(
        "B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json" in manifest.get("evidence_anchors", []),
        "B4 source-policy execution opt-in packet JSON anchor missing",
    )
    checks.check(
        "B4_SOURCE_POLICY_EXECUTION_HANDOFF_PACKAGE.md" in manifest.get("evidence_anchors", []),
        "B4 source-policy execution handoff package anchor missing",
    )
    checks.check(
        "B4_SOURCE_POLICY_EXECUTION_HANDOFF_PACKAGE.json" in manifest.get("evidence_anchors", []),
        "B4 source-policy execution handoff package JSON anchor missing",
    )
    checks.check(
        "B4_SOURCE_POLICY_COMMAND_PREFLIGHT_FREEZE_20260620.md" in manifest.get("evidence_anchors", []),
        "B4 source-policy command preflight freeze anchor missing",
    )
    checks.check(
        "B4_SOURCE_POLICY_COMMAND_PREFLIGHT_FREEZE_20260620.json" in manifest.get("evidence_anchors", []),
        "B4 source-policy command preflight freeze JSON anchor missing",
    )
    checks.check(
        "B4_SOURCE_POLICY_EXPECTED_OUTPUT_SCHEMA_AUDIT_20260620.md"
        in manifest.get("evidence_anchors", []),
        "B4 expected-output schema audit anchor missing",
    )
    checks.check(
        "B4_SOURCE_POLICY_EXPECTED_OUTPUT_SCHEMA_AUDIT_20260620.json"
        in manifest.get("evidence_anchors", []),
        "B4 expected-output schema audit JSON anchor missing",
    )
    checks.check(
        "B4_EXPECTED_OUTPUT_PROMOTION_READINESS_BLOCKER_AUDIT_20260620.md"
        in manifest.get("evidence_anchors", []),
        "B4 expected-output promotion-readiness blocker audit anchor missing",
    )
    checks.check(
        "B4_EXPECTED_OUTPUT_PROMOTION_READINESS_BLOCKER_AUDIT_20260620.json"
        in manifest.get("evidence_anchors", []),
        "B4 expected-output promotion-readiness blocker audit JSON anchor missing",
    )
    checks.check(
        "OC6_SOURCE_EQUIVALENT_REOPEN_READINESS_AUDIT_20260620.md"
        in manifest.get("evidence_anchors", []),
        "OC6 source-equivalent reopen-readiness audit anchor missing",
    )
    checks.check(
        "OC6_SOURCE_EQUIVALENT_REOPEN_READINESS_AUDIT_20260620.json"
        in manifest.get("evidence_anchors", []),
        "OC6 source-equivalent reopen-readiness audit JSON anchor missing",
    )
    checks.check(
        "FULL_SOURCE_POLICY_RUNNER_ARCHIVE_GAP_AUDIT.md" in manifest.get("evidence_anchors", []),
        "full source-policy runner archive gap audit anchor missing",
    )
    checks.check(
        "FULL_SOURCE_POLICY_RUNNER_ARCHIVE_GAP_AUDIT.json" in manifest.get("evidence_anchors", []),
        "full source-policy runner archive gap audit JSON anchor missing",
    )
    checks.check(
        "SOURCE_POLICY_REOPEN_CONDITION_MONITOR_20260620.md" in manifest.get("evidence_anchors", []),
        "source-policy reopen-condition monitor anchor missing",
    )
    checks.check(
        "SOURCE_POLICY_REOPEN_CONDITION_MONITOR_20260620.json" in manifest.get("evidence_anchors", []),
        "source-policy reopen-condition monitor JSON anchor missing",
    )
    checks.check(
        "RA2021_SOURCE_POLICY_ROW_AUDIT.md" in manifest.get("evidence_anchors", []),
        "RA2021 source-policy row audit anchor missing",
    )
    checks.check(
        "RA2021_SOURCE_POLICY_ROW_AUDIT.json" in manifest.get("evidence_anchors", []),
        "RA2021 source-policy row audit JSON anchor missing",
    )
    checks.check(
        "RA2021_SOURCE_IDENTITY_AUDIT.md" in manifest.get("evidence_anchors", []),
        "RA2021 source-identity audit anchor missing",
    )
    checks.check(
        "RA2021_SOURCE_IDENTITY_AUDIT.json" in manifest.get("evidence_anchors", []),
        "RA2021 source-identity audit JSON anchor missing",
    )
    checks.check(
        "HI2022_POLICY_DECISION_AUDIT.md" in manifest.get("evidence_anchors", []),
        "HI2022 policy-decision audit anchor missing",
    )
    checks.check(
        "HI2022_POLICY_DECISION_AUDIT.json" in manifest.get("evidence_anchors", []),
        "HI2022 policy-decision audit JSON anchor missing",
    )
    checks.check(
        "HI2022_SOURCE_POLICY_ROW_AUDIT.md" in manifest.get("evidence_anchors", []),
        "HI2022 source-policy row audit anchor missing",
    )
    checks.check(
        "HI2022_SOURCE_POLICY_ROW_AUDIT.json" in manifest.get("evidence_anchors", []),
        "HI2022 source-policy row audit JSON anchor missing",
    )
    checks.check(
        "HI2022_T8_TOLERANCE_REPAIR_AUDIT.md" in manifest.get("evidence_anchors", []),
        "HI2022 T=8 tolerance-repair audit anchor missing",
    )
    checks.check(
        "HI2022_T8_TOLERANCE_REPAIR_AUDIT.json" in manifest.get("evidence_anchors", []),
        "HI2022 T=8 tolerance-repair audit JSON anchor missing",
    )
    checks.check("CMAME_SUBMISSION_CHECKLIST.md" in manifest.get("evidence_anchors", []), "CMAME checklist anchor missing")
    checks.check("CMAME_SUBMISSION_READINESS_AUDIT.md" in manifest.get("evidence_anchors", []), "CMAME readiness audit anchor missing")
    checks.check(
        "CMAME_SUBMISSION_READINESS_REVIEW.md" in manifest.get("evidence_anchors", []),
        "CMAME readiness review anchor missing",
    )
    checks.check(
        "CMAME_SUBMISSION_INTEGRITY_AUDIT.md" in manifest.get("evidence_anchors", []),
        "CMAME submission-integrity audit anchor missing",
    )
    checks.check(
        "CMAME_SUBMISSION_INTEGRITY_AUDIT.json" in manifest.get("evidence_anchors", []),
        "CMAME submission-integrity audit JSON anchor missing",
    )
    checks.check(
        "CMAME_BLOCKER_CLOSURE_GATE.md" in manifest.get("evidence_anchors", []),
        "CMAME blocker-closure gate anchor missing",
    )
    checks.check(
        "CMAME_BLOCKER_CLOSURE_GATE.json" in manifest.get("evidence_anchors", []),
        "CMAME blocker-closure gate JSON anchor missing",
    )
    checks.check(
        "CMAME_EXTERNAL_BASELINE_GATE.md" in manifest.get("evidence_anchors", []),
        "CMAME external-baseline gate anchor missing",
    )
    checks.check(
        "CMAME_EXTERNAL_BASELINE_GATE.json" in manifest.get("evidence_anchors", []),
        "CMAME external-baseline gate JSON anchor missing",
    )
    checks.check(
        "CMAME_PROOF_CONTRACT_GATE.md" in manifest.get("evidence_anchors", []),
        "CMAME proof-contract gate anchor missing",
    )
    checks.check(
        "CMAME_PROOF_CONTRACT_GATE.json" in manifest.get("evidence_anchors", []),
        "CMAME proof-contract gate JSON anchor missing",
    )
    checks.check(
        "PROOF_CLOSURE_MANIFEST.md" in manifest.get("evidence_anchors", []),
        "proof-closure manifest anchor missing",
    )
    checks.check(
        "PROOF_CLOSURE_MANIFEST.json" in manifest.get("evidence_anchors", []),
        "proof-closure manifest JSON anchor missing",
    )
    checks.check(
        "PROOF_CLAIM_TRACEABILITY_AUDIT.md" in manifest.get("evidence_anchors", []),
        "proof-claim traceability audit anchor missing",
    )
    checks.check(
        "PROOF_CLAIM_TRACEABILITY_AUDIT.json" in manifest.get("evidence_anchors", []),
        "proof-claim traceability audit JSON anchor missing",
    )
    checks.check(
        "D5_TAYLOR_TERM_BUDGET_AUDIT.md" in manifest.get("evidence_anchors", []),
        "D5 Taylor term-budget audit anchor missing",
    )
    checks.check(
        "D5_TAYLOR_TERM_BUDGET_AUDIT.json" in manifest.get("evidence_anchors", []),
        "D5 Taylor term-budget audit JSON anchor missing",
    )
    checks.check(
        "D5_PRIMITIVE_BOUND_REDUCTION_AUDIT.md" in manifest.get("evidence_anchors", []),
        "D5 primitive-bound reduction audit anchor missing",
    )
    checks.check(
        "D5_PRIMITIVE_BOUND_REDUCTION_AUDIT.json" in manifest.get("evidence_anchors", []),
        "D5 primitive-bound reduction audit JSON anchor missing",
    )
    checks.check(
        "D5_P_TUBE_CONSTANTS_AUDIT.md" in manifest.get("evidence_anchors", []),
        "D5 P_tube constants audit anchor missing",
    )
    checks.check(
        "D5_P_TUBE_CONSTANTS_AUDIT.json" in manifest.get("evidence_anchors", []),
        "D5 P_tube constants audit JSON anchor missing",
    )
    checks.check(
        "D5_P_STATE_LIFT_GAP_AUDIT.md" in manifest.get("evidence_anchors", []),
        "D5 P_state lift-gap audit anchor missing",
    )
    checks.check(
        "D5_P_STATE_LIFT_GAP_AUDIT.json" in manifest.get("evidence_anchors", []),
        "D5 P_state lift-gap audit JSON anchor missing",
    )
    checks.check(
        "D5_P_STATE_MAP_DEFINITION_AUDIT.md" in manifest.get("evidence_anchors", []),
        "D5 P_state map-definition audit anchor missing",
    )
    checks.check(
        "D5_P_STATE_MAP_DEFINITION_AUDIT.json" in manifest.get("evidence_anchors", []),
        "D5 P_state map-definition audit JSON anchor missing",
    )
    checks.check(
        "D5_P_STATE_ANTICIRCULARITY_AUDIT.md" in manifest.get("evidence_anchors", []),
        "D5 P_state anti-circularity audit anchor missing",
    )
    checks.check(
        "D5_P_STATE_ANTICIRCULARITY_AUDIT.json" in manifest.get("evidence_anchors", []),
        "D5 P_state anti-circularity audit JSON anchor missing",
    )
    checks.check(
        "D5_P_STATE_PS2_WEIGHTED_TARGET_AUDIT.md" in manifest.get("evidence_anchors", []),
        "D5 P_state PS2 weighted target audit anchor missing",
    )
    checks.check(
        "D5_P_STATE_PS2_WEIGHTED_TARGET_AUDIT.json" in manifest.get("evidence_anchors", []),
        "D5 P_state PS2 weighted target audit JSON anchor missing",
    )
    checks.check(
        "D5_P_STATE_PS2_KINEMATIC_BLOCK_CERTIFICATE.md" in manifest.get("evidence_anchors", []),
        "D5 P_state PS2 kinematic-block certificate anchor missing",
    )
    checks.check(
        "D5_P_STATE_PS2_KINEMATIC_BLOCK_CERTIFICATE.json" in manifest.get("evidence_anchors", []),
        "D5 P_state PS2 kinematic-block certificate JSON anchor missing",
    )
    checks.check(
        "D5_P_STATE_PS2_LIE_CHART_BINDING_AUDIT.md" in manifest.get("evidence_anchors", []),
        "D5 P_state PS2 Lie-chart binding audit anchor missing",
    )
    checks.check(
        "D5_P_STATE_PS2_LIE_CHART_BINDING_AUDIT.json" in manifest.get("evidence_anchors", []),
        "D5 P_state PS2 Lie-chart binding audit JSON anchor missing",
    )
    checks.check(
        "D5_P_STATE_PS2_ROW_INJECTION_AUDIT.md" in manifest.get("evidence_anchors", []),
        "D5 P_state PS2 row-injection audit anchor missing",
    )
    checks.check(
        "D5_P_STATE_PS2_ROW_INJECTION_AUDIT.json" in manifest.get("evidence_anchors", []),
        "D5 P_state PS2 row-injection audit JSON anchor missing",
    )
    checks.check(
        "D5_P_STATE_PS2_NONLINEAR_BINDING_AUDIT.md" in manifest.get("evidence_anchors", []),
        "D5 P_state PS2 nonlinear binding audit anchor missing",
    )
    checks.check(
        "D5_P_STATE_PS2_NONLINEAR_BINDING_AUDIT.json" in manifest.get("evidence_anchors", []),
        "D5 P_state PS2 nonlinear binding audit JSON anchor missing",
    )
    checks.check(
        "D5_P_STATE_PS2_AGGREGATE_PROMOTION_AUDIT.md" in manifest.get("evidence_anchors", []),
        "D5 P_state PS2 aggregate promotion audit anchor missing",
    )
    checks.check(
        "D5_P_STATE_PS2_AGGREGATE_PROMOTION_AUDIT.json" in manifest.get("evidence_anchors", []),
        "D5 P_state PS2 aggregate promotion audit JSON anchor missing",
    )
    checks.check(
        "D5_P_STATE_PS2_LINEARIZATION_PROBE.md" in manifest.get("evidence_anchors", []),
        "D5 P_state PS2 linearization probe anchor missing",
    )
    checks.check(
        "D5_P_STATE_PS2_LINEARIZATION_PROBE.json" in manifest.get("evidence_anchors", []),
        "D5 P_state PS2 linearization probe JSON anchor missing",
    )
    checks.check(
        "D5_P_STATE_PS2_LINEARIZATION_PROBE.csv" in manifest.get("evidence_anchors", []),
        "D5 P_state PS2 linearization probe CSV anchor missing",
    )
    checks.check(
        "D5_P_STATE_PS3_CONDITIONAL_CONVERSION_AUDIT.md" in manifest.get("evidence_anchors", []),
        "D5 P_state PS3 conditional conversion audit anchor missing",
    )
    checks.check(
        "D5_P_STATE_PS3_CONDITIONAL_CONVERSION_AUDIT.json" in manifest.get("evidence_anchors", []),
        "D5 P_state PS3 conditional conversion audit JSON anchor missing",
    )
    checks.check(
        "D5_P_STATE_PS3_ACTUAL_INSTANTIATION_GAP_AUDIT.md" in manifest.get("evidence_anchors", []),
        "D5 P_state PS3 actual-instantiation gap audit anchor missing",
    )
    checks.check(
        "D5_P_STATE_PS3_ACTUAL_INSTANTIATION_GAP_AUDIT.json" in manifest.get("evidence_anchors", []),
        "D5 P_state PS3 actual-instantiation gap audit JSON anchor missing",
    )
    checks.check(
        "D5_P_STATE_PS3_H_ACC_INPUT_OBSTRUCTION_AUDIT.md" in manifest.get("evidence_anchors", []),
        "D5 P_state PS3 h-acc input obstruction audit anchor missing",
    )
    checks.check(
        "D5_P_STATE_PS3_H_ACC_INPUT_OBSTRUCTION_AUDIT.json" in manifest.get("evidence_anchors", []),
        "D5 P_state PS3 h-acc input obstruction audit JSON anchor missing",
    )
    checks.check(
        "D5_P_ACC_MAP_DEFINITION_AUDIT.md" in manifest.get("evidence_anchors", []),
        "D5 P_acc map-definition audit anchor missing",
    )
    checks.check(
        "D5_P_ACC_MAP_DEFINITION_AUDIT.json" in manifest.get("evidence_anchors", []),
        "D5 P_acc map-definition audit JSON anchor missing",
    )
    checks.check(
        "D5_P_ACC_ROW_BINDING_AUDIT.md" in manifest.get("evidence_anchors", []),
        "D5 P_acc row-binding audit anchor missing",
    )
    checks.check(
        "D5_P_ACC_ROW_BINDING_AUDIT.json" in manifest.get("evidence_anchors", []),
        "D5 P_acc row-binding audit JSON anchor missing",
    )
    checks.check(
        "D5_P_ACC_INDEPENDENCE_AUDIT.md" in manifest.get("evidence_anchors", []),
        "D5 P_acc independence audit anchor missing",
    )
    checks.check(
        "D5_P_ACC_INDEPENDENCE_AUDIT.json" in manifest.get("evidence_anchors", []),
        "D5 P_acc independence audit JSON anchor missing",
    )
    checks.check(
        "D5_P_LAMBDA_INTERFACE_AUDIT.md" in manifest.get("evidence_anchors", []),
        "D5 P_lambda interface audit anchor missing",
    )
    checks.check(
        "D5_P_LAMBDA_INTERFACE_AUDIT.json" in manifest.get("evidence_anchors", []),
        "D5 P_lambda interface audit JSON anchor missing",
    )
    checks.check(
        "D5_P_GEOM_CHART_REDUCTION_AUDIT.md" in manifest.get("evidence_anchors", []),
        "D5 P_geom chart-reduction audit anchor missing",
    )
    checks.check(
        "D5_P_GEOM_CHART_REDUCTION_AUDIT.json" in manifest.get("evidence_anchors", []),
        "D5 P_geom chart-reduction audit JSON anchor missing",
    )
    checks.check(
        "D5_P_GYRO_BILINEAR_REDUCTION_AUDIT.md" in manifest.get("evidence_anchors", []),
        "D5 P_gyro bilinear-reduction audit anchor missing",
    )
    checks.check(
        "D5_P_GYRO_BILINEAR_REDUCTION_AUDIT.json" in manifest.get("evidence_anchors", []),
        "D5 P_gyro bilinear-reduction audit JSON anchor missing",
    )
    checks.check(
        "D5_OPEN_PRIMITIVE_GAP_AUDIT.md" in manifest.get("evidence_anchors", []),
        "D5 open primitive gap audit anchor missing",
    )
    checks.check(
        "D5_OPEN_PRIMITIVE_GAP_AUDIT.json" in manifest.get("evidence_anchors", []),
        "D5 open primitive gap audit JSON anchor missing",
    )
    checks.check(
        "D5_PRIMITIVE_OBLIGATION_CLOSURE_PLAN.md" in manifest.get("evidence_anchors", []),
        "D5 primitive-obligation closure plan anchor missing",
    )
    checks.check(
        "D5_PRIMITIVE_OBLIGATION_CLOSURE_PLAN.json" in manifest.get("evidence_anchors", []),
        "D5 primitive-obligation closure plan JSON anchor missing",
    )
    checks.check(
        "D5_CONDITIONAL_TAYLOR_CERTIFICATE.md" in manifest.get("evidence_anchors", []),
        "D5 conditional Taylor certificate anchor missing",
    )
    checks.check(
        "D5_CONDITIONAL_TAYLOR_CERTIFICATE.json" in manifest.get("evidence_anchors", []),
        "D5 conditional Taylor certificate JSON anchor missing",
    )
    checks.check(
        "CMAME_VISUAL_LEGIBILITY_AUDIT.md" in manifest.get("evidence_anchors", []),
        "CMAME visual-legibility audit anchor missing",
    )
    checks.check(
        "CMAME_VISUAL_LEGIBILITY_AUDIT.json" in manifest.get("evidence_anchors", []),
        "CMAME visual-legibility audit JSON anchor missing",
    )
    checks.check(
        "CMAME_FIGURE_SET_AUDIT.md" in manifest.get("evidence_anchors", []),
        "CMAME figure-set audit anchor missing",
    )
    checks.check(
        "CMAME_FIGURE_SET_AUDIT.json" in manifest.get("evidence_anchors", []),
        "CMAME figure-set audit JSON anchor missing",
    )
    checks.check(
        "CMAME_RELATED_WORK_AUDIT.md" in manifest.get("evidence_anchors", []),
        "CMAME related-work audit anchor missing",
    )
    checks.check(
        "CMAME_RELATED_WORK_AUDIT.json" in manifest.get("evidence_anchors", []),
        "CMAME related-work audit JSON anchor missing",
    )
    checks.check(
        "DYNAMIC_ROW_ORACLE_GATE.md" in manifest.get("evidence_anchors", []),
        "dynamic row oracle gate anchor missing",
    )
    checks.check(
        "DYNAMIC_ROW_ORACLE_GATE.json" in manifest.get("evidence_anchors", []),
        "dynamic row oracle gate JSON anchor missing",
    )
    checks.check(
        "NEWTON_EULER_DEFECT_OBLIGATION_GATE.md" in manifest.get("evidence_anchors", []),
        "Newton-Euler obligation gate anchor missing",
    )
    checks.check(
        "NEWTON_EULER_DEFECT_OBLIGATION_GATE.json" in manifest.get("evidence_anchors", []),
        "Newton-Euler obligation gate JSON anchor missing",
    )
    checks.check(
        "NEWTON_EULER_VIRTUAL_WORK_WRENCH_AUDIT.md" in manifest.get("evidence_anchors", []),
        "Newton-Euler virtual-work wrench audit anchor missing",
    )
    checks.check(
        "NEWTON_EULER_VIRTUAL_WORK_WRENCH_AUDIT.json" in manifest.get("evidence_anchors", []),
        "Newton-Euler virtual-work wrench audit JSON anchor missing",
    )
    checks.check(
        "NEWTON_EULER_AD_EXPANDED_ROW_ORACLE_AUDIT.md" in manifest.get("evidence_anchors", []),
        "Newton-Euler AD-expanded row oracle audit anchor missing",
    )
    checks.check(
        "NEWTON_EULER_AD_EXPANDED_ROW_ORACLE_AUDIT.json" in manifest.get("evidence_anchors", []),
        "Newton-Euler AD-expanded row oracle audit JSON anchor missing",
    )
    checks.check(
        "B1_SYMBOLIC_ROW_ORACLE_CLOSURE_CERTIFICATE.md" in manifest.get("evidence_anchors", []),
        "B1 symbolic row-oracle closure certificate anchor missing",
    )
    checks.check(
        "B1_SYMBOLIC_ROW_ORACLE_CLOSURE_CERTIFICATE.json" in manifest.get("evidence_anchors", []),
        "B1 symbolic row-oracle closure certificate JSON anchor missing",
    )
    checks.check(
        "B1_AD_EXPANDED_SYMBOLIC_ORACLE_CLOSURE_CERTIFICATE.md" in manifest.get("evidence_anchors", []),
        "B1 AD-expanded symbolic oracle closure certificate anchor missing",
    )
    checks.check(
        "B1_AD_EXPANDED_SYMBOLIC_ORACLE_CLOSURE_CERTIFICATE.json" in manifest.get("evidence_anchors", []),
        "B1 AD-expanded symbolic oracle closure certificate JSON anchor missing",
    )
    for anchor in [
        "v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_residual_scaffold.json",
        "v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_residual_scaffold.csv",
        "v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_residual_scaffold.md",
        "v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_stage_residual_audit.json",
        "v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_stage_residual_audit.csv",
        "v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_stage_residual_audit.md",
        "v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_one_step_smoke.json",
        "v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_one_step_smoke.csv",
        "v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_one_step_smoke.md",
        "v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_newton_stage_smoke.json",
        "v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_newton_stage_smoke.csv",
        "v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_newton_stage_smoke.md",
        "v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_newton_coarse_order.json",
        "v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_newton_coarse_order_rows.csv",
        "v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_newton_coarse_order.md",
        "v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_public_work_precision.json",
        "v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_public_work_precision_rows.csv",
        "v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_public_work_precision_summary.csv",
        "v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_public_work_precision.md",
        "v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_strict_common_reference.json",
        "v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_strict_common_reference_rows.csv",
        "v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_strict_common_reference_summary.csv",
        "v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_strict_common_reference.md",
        "v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_strict_common_reference_work_precision.png",
    ]:
        checks.check(anchor in manifest.get("evidence_anchors", []), f"closed-loop dynamic anchor missing: {anchor}")
    checks.check("README_CMAME_FLAT_SUBMISSION.md" in manifest.get("evidence_anchors", []), "CMAME flat README anchor missing")
    checks.check("cmame_submission_flat.zip" in manifest.get("evidence_anchors", []), "CMAME flat archive anchor missing")
    checks.check(
        "cmame_submission_flat/main_cmame_submission.tex" in manifest.get("evidence_anchors", []),
        "CMAME flat TeX anchor missing",
    )
    checks.check(
        "cmame_submission_flat/main_cmame_submission.pdf" in manifest.get("evidence_anchors", []),
        "CMAME flat PDF anchor missing",
    )
    checks.check("main_cmame.pdf" in manifest.get("evidence_anchors", []), "CMAME PDF anchor missing")
    checks.check("main_cmame.tex" in manifest.get("evidence_anchors", []), "CMAME TeX anchor missing")
    checks.check("highlights_cmame.txt" in manifest.get("evidence_anchors", []), "CMAME highlights anchor missing")
    checks.check("declarations_cmame.md" in manifest.get("evidence_anchors", []), "CMAME declarations anchor missing")
    checks.check("REFERENCE_METADATA_AUDIT.md" in manifest.get("evidence_anchors", []), "reference metadata audit anchor missing")
    checks.check(
        "REFERENCE_METADATA_AUDIT.json" in manifest.get("evidence_anchors", []),
        "reference metadata audit JSON anchor missing",
    )
    checks.check(
        manifest.get("reference_metadata_audit") == "REFERENCE_METADATA_AUDIT.md",
        "reference metadata audit manifest path missing",
    )
    checks.check(
        manifest.get("reference_metadata_audit_json") == "REFERENCE_METADATA_AUDIT.json",
        "reference metadata audit JSON manifest path missing",
    )
    checks.check(
        manifest.get("paper_numerical_result_matrix") == "PAPER_NUMERICAL_RESULT_MATRIX.md",
        "paper numerical result matrix manifest path missing",
    )
    checks.check(
        manifest.get("paper_numerical_result_matrix_json") == "PAPER_NUMERICAL_RESULT_MATRIX.json",
        "paper numerical result matrix JSON manifest path missing",
    )
    checks.check(
        manifest.get("paper_numerical_result_matrix_csv") == "PAPER_NUMERICAL_RESULT_MATRIX.csv",
        "paper numerical result matrix CSV manifest path missing",
    )
    checks.check(
        manifest.get("result_to_manuscript_traceability_audit") == "RESULT_TO_MANUSCRIPT_TRACEABILITY_AUDIT.md",
        "result-to-manuscript traceability audit manifest path missing",
    )
    checks.check(
        manifest.get("result_to_manuscript_traceability_audit_json") == "RESULT_TO_MANUSCRIPT_TRACEABILITY_AUDIT.json",
        "result-to-manuscript traceability audit JSON manifest path missing",
    )
    checks.check(
        manifest.get("all_method_example_claim_disposition_audit")
        == "ALL_METHOD_EXAMPLE_CLAIM_DISPOSITION_AUDIT.md",
        "all-method claim-disposition audit manifest path missing",
    )
    checks.check(
        manifest.get("all_method_example_claim_disposition_audit_json")
        == "ALL_METHOD_EXAMPLE_CLAIM_DISPOSITION_AUDIT.json",
        "all-method claim-disposition audit JSON manifest path missing",
    )
    checks.check(
        "PAPER_NUMERICAL_RESULT_MATRIX.md" in manifest.get("evidence_anchors", []),
        "paper numerical result matrix anchor missing",
    )
    checks.check(
        "PAPER_NUMERICAL_RESULT_MATRIX.json" in manifest.get("evidence_anchors", []),
        "paper numerical result matrix JSON anchor missing",
    )
    checks.check(
        "PAPER_NUMERICAL_RESULT_MATRIX.csv" in manifest.get("evidence_anchors", []),
        "paper numerical result matrix CSV anchor missing",
    )
    checks.check(
        "RESULT_TO_MANUSCRIPT_TRACEABILITY_AUDIT.md" in manifest.get("evidence_anchors", []),
        "result-to-manuscript traceability audit anchor missing",
    )
    checks.check(
        "RESULT_TO_MANUSCRIPT_TRACEABILITY_AUDIT.json" in manifest.get("evidence_anchors", []),
        "result-to-manuscript traceability audit JSON anchor missing",
    )
    checks.check(
        "ALL_METHOD_EXAMPLE_CLAIM_DISPOSITION_AUDIT.md" in manifest.get("evidence_anchors", []),
        "all-method claim-disposition audit anchor missing",
    )
    checks.check(
        "ALL_METHOD_EXAMPLE_CLAIM_DISPOSITION_AUDIT.json" in manifest.get("evidence_anchors", []),
        "all-method claim-disposition audit JSON anchor missing",
    )
    checks.check(
        manifest.get("all_examples_result_sanity_audit") == "ALL_EXAMPLES_RESULT_SANITY_AUDIT.md",
        "all-example result sanity audit manifest path missing",
    )
    checks.check(
        manifest.get("all_examples_result_sanity_audit_json") == "ALL_EXAMPLES_RESULT_SANITY_AUDIT.json",
        "all-example result sanity audit JSON manifest path missing",
    )
    checks.check(
        manifest.get("all_examples_source_policy_audit") == "ALL_EXAMPLES_SOURCE_POLICY_AUDIT.md",
        "all-example source-policy audit manifest path missing",
    )
    checks.check(
        manifest.get("all_examples_source_policy_audit_json") == "ALL_EXAMPLES_SOURCE_POLICY_AUDIT.json",
        "all-example source-policy audit JSON manifest path missing",
    )
    checks.check(
        manifest.get("source_policy_closure_triage") == "SOURCE_POLICY_CLOSURE_TRIAGE.md",
        "source-policy closure triage manifest path missing",
    )
    checks.check(
        manifest.get("source_policy_closure_triage_json") == "SOURCE_POLICY_CLOSURE_TRIAGE.json",
        "source-policy closure triage JSON manifest path missing",
    )
    checks.check(
        manifest.get("source_policy_row_closure_ledger") == "SOURCE_POLICY_ROW_CLOSURE_LEDGER.md",
        "source-policy row closure ledger manifest path missing",
    )
    checks.check(
        manifest.get("source_policy_row_closure_ledger_json") == "SOURCE_POLICY_ROW_CLOSURE_LEDGER.json",
        "source-policy row closure ledger JSON manifest path missing",
    )
    checks.check(
        manifest.get("external_case_evidence_reconciliation") == "EXTERNAL_CASE_EVIDENCE_RECONCILIATION.md",
        "external case evidence reconciliation manifest path missing",
    )
    checks.check(
        manifest.get("external_case_evidence_reconciliation_json") == "EXTERNAL_CASE_EVIDENCE_RECONCILIATION.json",
        "external case evidence reconciliation JSON manifest path missing",
    )
    for anchor in [
        "ALL_EXAMPLES_RESULT_SANITY_AUDIT.md",
        "ALL_EXAMPLES_RESULT_SANITY_AUDIT.json",
        "ALL_EXAMPLES_SOURCE_POLICY_AUDIT.md",
        "ALL_EXAMPLES_SOURCE_POLICY_AUDIT.json",
        "SOURCE_POLICY_CLOSURE_TRIAGE.md",
        "SOURCE_POLICY_CLOSURE_TRIAGE.json",
        "SOURCE_POLICY_ROW_CLOSURE_LEDGER.md",
        "SOURCE_POLICY_ROW_CLOSURE_LEDGER.json",
        "EXTERNAL_CASE_EVIDENCE_RECONCILIATION.md",
        "EXTERNAL_CASE_EVIDENCE_RECONCILIATION.json",
        "HI2022_T8_TOLERANCE_REPAIR_AUDIT.md",
        "HI2022_T8_TOLERANCE_REPAIR_AUDIT.json",
        "VP2024_CODE_PATH_DISPOSITION_AUDIT.md",
        "VP2024_CODE_PATH_DISPOSITION_AUDIT.json",
    ]:
        checks.check(anchor in manifest.get("evidence_anchors", []), f"all-example/source-policy anchor missing: {anchor}")
    checks.check("validate_cmame_submission.py" in manifest.get("validators", []), "CMAME submission validator missing")
    checks.check(
        "validate_cmame_submission_integrity_audit.py" in manifest.get("validators", []),
        "CMAME submission-integrity audit validator missing",
    )
    checks.check(
        "validate_reference_metadata_audit.py" in manifest.get("validators", []),
        "reference metadata audit validator missing",
    )
    checks.check(
        "validate_cmame_blocker_closure_gate.py" in manifest.get("validators", []),
        "CMAME blocker-closure validator missing",
    )
    checks.check(
        "validate_cmame_external_baseline_gate.py" in manifest.get("validators", []),
        "CMAME external-baseline validator missing",
    )
    checks.check(
        "validate_cmame_proof_contract_gate.py" in manifest.get("validators", []),
        "CMAME proof-contract validator missing",
    )
    checks.check(
        "validate_proof_closure_manifest.py" in manifest.get("validators", []),
        "proof-closure manifest validator missing",
    )
    checks.check(
        "validate_proof_claim_traceability_audit.py" in manifest.get("validators", []),
        "proof-claim traceability validator missing",
    )
    checks.check(
        "validate_d5_taylor_term_budget_audit.py" in manifest.get("validators", []),
        "D5 Taylor term-budget validator missing",
    )
    checks.check(
        "validate_d5_primitive_bound_reduction_audit.py" in manifest.get("validators", []),
        "D5 primitive-bound reduction validator missing",
    )
    checks.check(
        "validate_d5_p_tube_constants_audit.py" in manifest.get("validators", []),
        "D5 P_tube constants validator missing",
    )
    checks.check(
        "validate_d5_p_state_lift_gap_audit.py" in manifest.get("validators", []),
        "D5 P_state lift-gap validator missing",
    )
    checks.check(
        "validate_d5_p_state_map_definition_audit.py" in manifest.get("validators", []),
        "D5 P_state map-definition validator missing",
    )
    checks.check(
        "validate_d5_p_state_anticircularity_audit.py" in manifest.get("validators", []),
        "D5 P_state anti-circularity validator missing",
    )
    checks.check(
        "validate_d5_p_state_ps2_weighted_target_audit.py" in manifest.get("validators", []),
        "D5 P_state PS2 weighted target validator missing",
    )
    checks.check(
        "validate_d5_p_state_ps2_kinematic_block_certificate.py" in manifest.get("validators", []),
        "D5 P_state PS2 kinematic-block validator missing",
    )
    checks.check(
        "validate_d5_p_state_ps2_lie_chart_binding_audit.py" in manifest.get("validators", []),
        "D5 P_state PS2 Lie-chart binding validator missing",
    )
    checks.check(
        "validate_d5_p_state_ps2_row_injection_audit.py" in manifest.get("validators", []),
        "D5 P_state PS2 row-injection validator missing",
    )
    checks.check(
        "validate_d5_p_state_ps2_nonlinear_binding_audit.py" in manifest.get("validators", []),
        "D5 P_state PS2 nonlinear binding validator missing",
    )
    checks.check(
        "validate_d5_p_state_ps2_aggregate_promotion_audit.py" in manifest.get("validators", []),
        "D5 P_state PS2 aggregate promotion validator missing",
    )
    checks.check(
        "validate_d5_p_state_ps2_linearization_probe.py" in manifest.get("validators", []),
        "D5 P_state PS2 linearization probe validator missing",
    )
    checks.check(
        "validate_d5_p_state_ps3_conditional_conversion_audit.py" in manifest.get("validators", []),
        "D5 P_state PS3 conditional conversion validator missing",
    )
    checks.check(
        "validate_d5_p_state_ps3_actual_instantiation_gap_audit.py" in manifest.get("validators", []),
        "D5 P_state PS3 actual-instantiation gap validator missing",
    )
    checks.check(
        "validate_d5_p_state_ps3_h_acc_input_obstruction_audit.py" in manifest.get("validators", []),
        "D5 P_state PS3 h-acc input obstruction validator missing",
    )
    checks.check(
        "validate_d5_p_acc_map_definition_audit.py" in manifest.get("validators", []),
        "D5 P_acc map-definition validator missing",
    )
    checks.check(
        "validate_d5_p_acc_row_binding_audit.py" in manifest.get("validators", []),
        "D5 P_acc row-binding validator missing",
    )
    checks.check(
        "validate_d5_p_acc_independence_audit.py" in manifest.get("validators", []),
        "D5 P_acc independence validator missing",
    )
    checks.check(
        "validate_d5_p_lambda_interface_audit.py" in manifest.get("validators", []),
        "D5 P_lambda interface validator missing",
    )
    checks.check(
        "validate_d5_p_geom_chart_reduction_audit.py" in manifest.get("validators", []),
        "D5 P_geom chart-reduction validator missing",
    )
    checks.check(
        "validate_d5_p_gyro_bilinear_reduction_audit.py" in manifest.get("validators", []),
        "D5 P_gyro bilinear-reduction validator missing",
    )
    checks.check(
        "validate_d5_open_primitive_gap_audit.py" in manifest.get("validators", []),
        "D5 open primitive gap validator missing",
    )
    checks.check(
        "validate_d5_primitive_obligation_closure_plan.py" in manifest.get("validators", []),
        "D5 primitive-obligation closure plan validator missing",
    )
    checks.check(
        "validate_d5_conditional_taylor_certificate.py" in manifest.get("validators", []),
        "D5 conditional Taylor certificate validator missing",
    )
    checks.check(
        "validate_paper_numerical_result_matrix.py" in manifest.get("validators", []),
        "paper numerical result matrix validator missing",
    )
    checks.check(
        "validate_result_to_manuscript_traceability_audit.py" in manifest.get("validators", []),
        "result-to-manuscript traceability audit validator missing",
    )
    checks.check(
        "validate_all_method_example_claim_disposition_audit.py" in manifest.get("validators", []),
        "all-method claim-disposition validator missing",
    )
    checks.check(
        "validate_all_examples_result_sanity_audit.py" in manifest.get("validators", []),
        "all-example result sanity audit validator missing",
    )
    checks.check(
        "validate_all_examples_source_policy_audit.py" in manifest.get("validators", []),
        "all-example source-policy audit validator missing",
    )
    checks.check(
        "validate_source_policy_closure_triage.py" in manifest.get("validators", []),
        "source-policy closure triage validator missing",
    )
    checks.check(
        "validate_source_policy_row_closure_ledger.py" in manifest.get("validators", []),
        "source-policy row closure ledger validator missing",
    )
    checks.check(
        "validate_external_case_evidence_reconciliation.py" in manifest.get("validators", []),
        "external case evidence reconciliation validator missing",
    )
    checks.check(
        "validate_vp2024_code_path_disposition_audit.py" in manifest.get("validators", []),
        "VP2024 code-path disposition validator missing",
    )
    checks.check(
        "validate_external_suite_demotion_ledger.py" in manifest.get("validators", []),
        "external suite demotion ledger validator missing",
    )
    checks.check(
        "validate_b2_source_policy_remaining_work_manifest.py" in manifest.get("validators", []),
        "B2 source-policy remaining-work manifest validator missing",
    )
    checks.check(
        "validate_b4_source_policy_work_precision_execution_plan.py" in manifest.get("validators", []),
        "B4 source-policy work/precision execution plan validator missing",
    )
    checks.check(
        "validate_b4_existing_artifact_promotion_audit.py" in manifest.get("validators", []),
        "B4 existing-artifact promotion audit validator missing",
    )
    checks.check(
        "validate_b4_source_policy_post_execution_audit.py" in manifest.get("validators", []),
        "B4 source-policy post-execution audit validator missing",
    )
    checks.check(
        "validate_ra2021_double_source_policy_low_order_diagnosis.py" in manifest.get("validators", []),
        "RA2021 double low-order diagnosis validator missing",
    )
    checks.check(
        "validate_hi2022_ra_half_double_source_policy_failure_diagnosis.py"
        in manifest.get("validators", []),
        "HI2022 rA_half double failure diagnosis validator missing",
    )
    checks.check(
        "validate_b4_source_policy_row_closure_readiness_ledger.py" in manifest.get("validators", []),
        "B4 source-policy row closure-readiness ledger validator missing",
    )
    checks.check(
        "validate_b4_source_policy_execution_opt_in_packet.py" in manifest.get("validators", []),
        "B4 source-policy execution opt-in packet validator missing",
    )
    checks.check(
        "validate_b4_source_policy_execution_handoff_package.py" in manifest.get("validators", []),
        "B4 source-policy execution handoff package validator missing",
    )
    checks.check(
        "validate_b4_source_policy_command_preflight_freeze_20260620.py" in manifest.get("validators", []),
        "B4 source-policy command preflight freeze validator missing",
    )
    checks.check(
        "validate_b4_source_policy_expected_output_schema_audit_20260620.py"
        in manifest.get("validators", []),
        "B4 expected-output schema audit validator missing",
    )
    checks.check(
        "validate_b4_expected_output_promotion_readiness_blocker_audit_20260620.py"
        in manifest.get("validators", []),
        "B4 expected-output promotion-readiness blocker audit validator missing",
    )
    checks.check(
        "validate_oc6_source_equivalent_reopen_readiness_audit_20260620.py"
        in manifest.get("validators", []),
        "OC6 source-equivalent reopen-readiness audit validator missing",
    )
    checks.check(
        "validate_ra2021_source_policy_row_audit.py" in manifest.get("validators", []),
        "RA2021 source-policy row audit validator missing",
    )
    checks.check(
        "validate_ra2021_source_identity_audit.py" in manifest.get("validators", []),
        "RA2021 source-identity audit validator missing",
    )
    checks.check(
        "validate_hi2022_policy_decision_audit.py" in manifest.get("validators", []),
        "HI2022 policy-decision audit validator missing",
    )
    checks.check(
        "validate_hi2022_source_policy_row_audit.py" in manifest.get("validators", []),
        "HI2022 source-policy row audit validator missing",
    )
    checks.check(
        "validate_hi2022_t8_tolerance_repair_audit.py" in manifest.get("validators", []),
        "HI2022 T=8 tolerance-repair audit validator missing",
    )
    checks.check(
        "validate_cmame_visual_legibility_audit.py" in manifest.get("validators", []),
        "CMAME visual-legibility audit validator missing",
    )
    checks.check(
        "validate_cmame_figure_set_audit.py" in manifest.get("validators", []),
        "CMAME figure-set audit validator missing",
    )
    checks.check(
        "validate_cmame_related_work_audit.py" in manifest.get("validators", []),
        "CMAME related-work audit validator missing",
    )
    checks.check(
        "validate_cmame_prose_residue_audit.py" in manifest.get("validators", []),
        "CMAME prose-residue audit validator missing",
    )
    checks.check(
        "validate_cmame_claim_hygiene_audit.py" in manifest.get("validators", []),
        "CMAME claim-hygiene audit validator missing",
    )
    checks.check(
        "validate_dynamic_row_oracle_gate.py" in manifest.get("validators", []),
        "dynamic row oracle validator missing",
    )
    checks.check(
        "validate_newton_euler_defect_obligation_gate.py" in manifest.get("validators", []),
        "Newton-Euler obligation gate validator missing",
    )
    checks.check(
        "validate_newton_euler_virtual_work_wrench_audit.py" in manifest.get("validators", []),
        "Newton-Euler virtual-work wrench audit validator missing",
    )
    checks.check(
        "validate_b1_symbolic_row_oracle_closure_certificate.py" in manifest.get("validators", []),
        "B1 symbolic row-oracle closure validator missing",
    )
    checks.check(
        "validate_b1_ad_expanded_symbolic_oracle_closure_certificate.py" in manifest.get("validators", []),
        "B1 AD-expanded symbolic oracle closure validator missing",
    )
    checks.check(
        "validate_newton_euler_dynamic_row_closure_contract.py" in manifest.get("validators", []),
        "Newton-Euler dynamic-row closure contract validator missing",
    )
    checks.check(
        "../v048_cross_paper_same_test_benchmarks/validate_closed_loop_true_dynamic_residual_scaffold.py"
        in manifest.get("validators", []),
        "residual scaffold validator missing",
    )
    checks.check(
        "../v048_cross_paper_same_test_benchmarks/validate_closed_loop_true_dynamic_stage_residual_audit.py"
        in manifest.get("validators", []),
        "stage residual audit validator missing",
    )
    checks.check(
        "../v048_cross_paper_same_test_benchmarks/validate_closed_loop_true_dynamic_one_step_smoke.py"
        in manifest.get("validators", []),
        "one-step smoke validator missing",
    )
    checks.check(
        "../v048_cross_paper_same_test_benchmarks/validate_closed_loop_true_dynamic_newton_stage_smoke.py"
        in manifest.get("validators", []),
        "Newton stage smoke validator missing",
    )
    checks.check(
        "../v048_cross_paper_same_test_benchmarks/validate_closed_loop_true_dynamic_newton_coarse_order.py"
        in manifest.get("validators", []),
        "Newton coarse-order validator missing",
    )
    checks.check(
        "../v048_cross_paper_same_test_benchmarks/validate_closed_loop_true_dynamic_public_work_precision.py"
        in manifest.get("validators", []),
        "public work/precision validator missing",
    )
    checks.check(
        "../v048_cross_paper_same_test_benchmarks/validate_closed_loop_true_dynamic_strict_common_reference.py"
        in manifest.get("validators", []),
        "strict common-reference validator missing",
    )
    checks.check("validate_proof_evidence_matrix.py" in manifest.get("validators", []), "proof evidence matrix validator missing")
    checks.check(
        "validate_proof_numerical_scale_audit.py" in manifest.get("validators", []),
        "proof numerical scale audit validator missing",
    )
    checks.check(
        "validate_proof_solver_scale_audit.py" in manifest.get("validators", []),
        "proof solver-scale audit validator missing",
    )
    checks.check(
        "validate_proof_solver_scaled_tolerance_probe.py" in manifest.get("validators", []),
        "proof solver scaled-tolerance probe validator missing",
    )
    checks.check(
        "validate_proof_solver_scaled_tolerance_trajectory_probe.py" in manifest.get("validators", []),
        "proof solver scaled-tolerance trajectory probe validator missing",
    )
    checks.check(
        "validate_proof_solver_tolerance_regime_sweep.py" in manifest.get("validators", []),
        "proof solver tolerance-regime sweep validator missing",
    )
    checks.check(
        "validate_cmame_proof_style_audit.py" in manifest.get("validators", []),
        "CMAME proof-style audit validator missing",
    )
    checks.check(
        "validate_cmame_strict_proof_audit.py" in manifest.get("validators", []),
        "CMAME strict-proof audit validator missing",
    )
    checks.check(
        "validate_cmame_strict_proof_policy_reconciliation_audit.py" in manifest.get("validators", []),
        "CMAME strict-proof policy reconciliation audit validator missing",
    )
    checks.check("validate_source_paper_comparison.py" in manifest.get("validators", []), "source-paper comparison validator missing")
    checks.check(
        "validate_cross_paper_benchmark_spec.py" in manifest.get("validators", []),
        "cross-paper benchmark spec validator missing",
    )
    checks.check(
        "validate_cross_paper_benchmark_cases.py" in manifest.get("validators", []),
        "cross-paper benchmark cases validator missing",
    )
    checks.check(
        "validate_external_same_test_run_queue.py" in manifest.get("validators", []),
        "external same-test run queue validator missing",
    )
    checks.check(
        "validate_external_suite_disposition_audit.py" in manifest.get("validators", []),
        "external suite disposition audit validator missing",
    )
    checks.check(
        "validate_external_source_policy_closure_manifest.py" in manifest.get("validators", []),
        "external source-policy closure manifest validator missing",
    )
    checks.check(
        "validate_tfe_source_policy_spec.py" in manifest.get("validators", []),
        "TFE source-policy spec validator missing",
    )
    checks.check(
        "validate_tfe_source_policy_row_audit.py" in manifest.get("validators", []),
        "TFE source-policy row audit validator missing",
    )
    checks.check(
        "validate_tfe_b4_b7_source_policy_demotion_audit.py" in manifest.get("validators", []),
        "TFE B4/B7 source-policy demotion audit validator missing",
    )
    checks.check(
        "validate_tfe_source_pendulum_model_audit.py" in manifest.get("validators", []),
        "TFE source pendulum model audit validator missing",
    )
    checks.check(
        "validate_tfe_brown_mcphee_source_law_boundary_audit.py" in manifest.get("validators", []),
        "TFE Brown-McPhee source-law boundary audit validator missing",
    )
    checks.check(
        "validate_tfe_source_grid_compatibility_audit.py" in manifest.get("validators", []),
        "TFE source grid compatibility audit validator missing",
    )
    checks.check(
        "validate_tfe_endpoint_policy_boundary_certificate.py" in manifest.get("validators", []),
        "TFE endpoint policy boundary certificate validator missing",
    )
    checks.check(
        "validate_comparison_objective_closure_reconciliation_audit.py" in manifest.get("validators", []),
        "comparison reconciliation audit validator missing",
    )
    checks.check(
        "validate_objective_completion_audit.py" in manifest.get("validators", []),
        "objective completion audit validator missing",
    )
    checks.check("validate_submission_bundle.py" in manifest.get("validators", []), "submission bundle validator missing")


def check_paper_result_pack(checks: Checks, result_pack: dict, objective_completion: dict) -> None:
    v048_objective = result_pack.get("v048_objective", {})
    result_pack_md = read_text(PAPER / "PAPER_RESULT_PACK.md")
    checks.check(result_pack.get("schema") == "paper-result-pack-v1", "paper result-pack schema changed")
    checks.check(result_pack.get("submission_ready") is False, "paper result-pack overclaims submission readiness")
    checks.check(
        result_pack.get("global_objective_complete")
        == objective_completion.get("objective_complete")
        is False,
        "paper result-pack global objective mirror stale",
    )
    checks.check(
        result_pack.get("global_submission_ready")
        == objective_completion.get("submission_ready")
        is False,
        "paper result-pack global submission-ready mirror stale",
    )
    checks.check(
        result_pack.get("global_open_blockers")
        == objective_completion.get("blocking_ids")
        == ["OC4", "OC6", "OC12"],
        "paper result-pack global blocker mirror stale",
    )
    checks.check(
        result_pack.get("objective_blocker_matrix_status")
        == "global_objective_blockers_remain_open",
        "paper result-pack objective blocker matrix status changed",
    )
    checks.check(
        result_pack.get("objective_source_policy_closed_ratio")
        == objective_completion.get("source_policy_closed_ratio")
        == "0/40",
        "paper result-pack source-policy ratio mirror stale",
    )
    checks.check(
        result_pack.get("blocker_open_by_id")
        == result_pack.get("objective_blocker_open_by_id")
        == objective_completion.get("blocker_open_by_id")
        == {"OC4": True, "OC6": True, "OC12": True},
        "paper result-pack blocker-open matrix stale",
    )
    checks.check(
        result_pack.get("blocker_closure_decision_by_id")
        == result_pack.get("objective_blocker_closure_decision_by_id")
        == objective_completion.get("blocker_closure_decision_by_id")
        == {
            "OC4": "remain_open_ready_for_authorized_execution_not_executed_not_promoted",
            "OC6": "remain_open_no_positive_source_equivalent_artifact",
            "OC12": "remain_partial_narrowed_replay_ready_full_source_policy_archive_not_ready",
        },
        "paper result-pack blocker closure-decision matrix stale",
    )
    checks.check(
        result_pack.get("blocker_closure_allowed_by_id")
        == result_pack.get("objective_blocker_closure_allowed_by_id")
        == objective_completion.get("blocker_closure_allowed_by_id")
        == {"OC4": False, "OC6": False, "OC12": False},
        "paper result-pack blocker closure-allowed matrix stale",
    )
    for token in [
        "## Objective Blocker Matrix",
        "This result pack consolidates paper evidence. It does not close the global objective blockers.",
        "Source-policy rows closed: `0/40`.",
        "`blocker_open_by_id=OC4:True,OC6:True,OC12:True`",
        "`blocker_closure_decision_by_id=OC4:remain_open_ready_for_authorized_execution_not_executed_not_promoted,OC6:remain_open_no_positive_source_equivalent_artifact,OC12:remain_partial_narrowed_replay_ready_full_source_policy_archive_not_ready`",
        "`blocker_closure_allowed_by_id=OC4:False,OC6:False,OC12:False`",
    ]:
        checks.check(token in result_pack_md, f"paper result-pack markdown missing token: {token}")
    checks.check(
        v048_objective.get("objective_complete") is True
        and v048_objective.get("objective_scope")
        == "v048_cross_paper_fixed_grid_comparison_scaffold_only"
        and v048_objective.get("global_submission_effect")
        == "does_not_close_global_submission_ready"
        and v048_objective.get("source_policy_reproduction") is False,
        "paper result-pack v048 local objective boundary stale",
    )
    checks.check(
        result_pack.get("quality_review_scope") == "global_false_narrowed_claim_subcheck_true"
        and result_pack.get("quality_review_passed") is False
        and result_pack.get("quality_review_passed_under_narrowed_claim") is True,
        "paper result-pack quality-review scope stale",
    )


def check_submission_texts(checks: Checks) -> None:
    required_tokens: dict[str, list[str]] = {
        "SUBMISSION_PACKET.md": [
            "do not submit globally yet",
            "bounded subsidiary subcheck",
            "narrowed_claim_role=subsidiary_bounded_subcheck_not_top_level_review_verdict",
            "Full source-policy package remains not ready",
            "Full source-policy runner archive boundary: safe actions without B4 opt-in",
            "source-policy execution allowed now `False`",
            "exact B4 opt-in required for execution `True`",
            "opt-in commands/mapped external",
            "rows `13/20`",
            "Command-row traceability covers unique RA/HI rows `20/20`",
            "row refs `32/32`",
            "mismatch/terminal/closed/promotion-ready counts `0/0/0/0`",
            "Safe action ids are `rebuild_read_only_audit_chain,rerun_read_only_validators,keep_narrowed_archive_provenance_only,monitor_reopen_conditions`",
            "opt-in action ids are `authorized_b4_ra_hi_source_policy_execution`",
            "`run_b4_source_policy_after_opt_in.sh`",
            "I explicitly approve running the B4 source-policy execution commands listed in B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json.",
            "Narrowed archive boundary matches the reproducibility manifest: `True`",
            "Narrowed archive boundary status/source-policy/use/execution/exact",
            "`narrowed_archive_ready_not_full_source_policy_runner_archive/0/40/False/False/True`",
            "Narrowed archive boundary blocking ids/status",
            "`OC4,OC6,OC12` / `OC4=open,OC6=partial,OC12=partial`",
            "current archive use is therefore `narrowed_claim_only`, not a full",
            "direct-PC2 theorem-input route",
            "supply the direct-PC2 theorem input",
            "This row-level contract does not close the primitive/Taylor route, P6 solver-policy evidence,",
            "P7 residual-to-error promotion, source-policy readiness, or full-TFE replacement",
            "`bounded_narrowed_subcheck_satisfied=True`",
            "legacy compatibility alias `submission_ready_under_narrowed_claim=True` is not a",
            "`full_source_policy_submission_ready=False`",
            "`main_cmame.pdf`",
            "`main_cmame.tex`",
            "`highlights_cmame.txt`",
            "`declarations_cmame.md`",
            "`CMAME_SUBMISSION_CHECKLIST.md`",
            "`CMAME_SUBMISSION_READINESS_AUDIT.md`",
            "`CMAME_SUBMISSION_READINESS_REVIEW.md`",
            "`CMAME_SUBMISSION_INTEGRITY_AUDIT.md`",
            "`CMAME_SUBMISSION_INTEGRITY_AUDIT.json`",
            "`CMAME_BLOCKER_CLOSURE_GATE.md`",
            "`CMAME_BLOCKER_CLOSURE_GATE.json`",
            "`CMAME_EXTERNAL_BASELINE_GATE.md`",
            "`CMAME_EXTERNAL_BASELINE_GATE.json`",
            "`CMAME_VISUAL_LEGIBILITY_AUDIT.md`",
            "`CMAME_VISUAL_LEGIBILITY_AUDIT.json`",
            "`CMAME_RELATED_WORK_AUDIT.md`",
            "`CMAME_RELATED_WORK_AUDIT.json`",
            "`CMAME_CLAIM_HYGIENE_AUDIT.md`",
            "`CMAME_CLAIM_HYGIENE_AUDIT.json`",
            "`DYNAMIC_ROW_ORACLE_GATE.md`",
            "`DYNAMIC_ROW_ORACLE_GATE.json`",
            "`NEWTON_EULER_DEFECT_OBLIGATION_GATE.md`",
            "`NEWTON_EULER_DEFECT_OBLIGATION_GATE.json`",
            "`README_CMAME_FLAT_SUBMISSION.md`",
            "`cmame_submission_flat/main_cmame_submission.tex`",
            "`cmame_submission_flat/main_cmame_submission.pdf`",
            "`cmame_submission_flat.zip`",
            "Accepted Claim",
            "Do Not Claim",
            "PROOF_EVIDENCE_MATRIX.md",
            "PROOF_NUMERICAL_SCALE_AUDIT.md",
            "PROOF_SOLVER_SCALE_AUDIT.md",
            "PROOF_SOLVER_SCALE_AUDIT.json",
            "PROOF_SOLVER_SCALED_TOLERANCE_PROBE.md",
            "PROOF_SOLVER_SCALED_TOLERANCE_PROBE.json",
            "PROOF_SOLVER_SCALED_TOLERANCE_TRAJECTORY_PROBE.md",
            "PROOF_SOLVER_SCALED_TOLERANCE_TRAJECTORY_PROBE.json",
            "PROOF_SOLVER_SCALED_TOLERANCE_TRAJECTORY_PROBE.csv",
            "PROOF_SOLVER_TOLERANCE_REGIME_SWEEP.md",
            "PROOF_SOLVER_TOLERANCE_REGIME_SWEEP.json",
            "PROOF_SOLVER_TOLERANCE_REGIME_SWEEP.csv",
            "PROOF_CLAIM_TRACEABILITY_AUDIT.md",
            "PROOF_CLAIM_TRACEABILITY_AUDIT.json",
            "theorem_level_scaled_tolerance_sweep_recorded=false",
            "finite_tolerance_regime_sweep_recorded=true",
            "eta_h_O_h7_solver_policy_evidence=false",
            "PAPER_NUMERICAL_RESULT_MATRIX.md",
            "PAPER_NUMERICAL_RESULT_MATRIX.json",
            "PAPER_NUMERICAL_RESULT_MATRIX.csv",
            "RESULT_TO_MANUSCRIPT_TRACEABILITY_AUDIT.md",
            "RESULT_TO_MANUSCRIPT_TRACEABILITY_AUDIT.json",
            "ALL_METHOD_EXAMPLE_CLAIM_DISPOSITION_AUDIT.md",
            "ALL_METHOD_EXAMPLE_CLAIM_DISPOSITION_AUDIT.json",
            "`40/40` nonlocal method/example rows",
            "`0/40` source-policy-closed nonlocal rows",
            "44/44",
            "132",
            "15` flagged nonlocal rows",
            "Review Agent Gate",
            "submission_standard_met=false",
            "submission_standard_scope=global_submission_standard",
            "decision=do_not_submit_global",
            "open_blockers=OC4,OC6,OC12",
            "bounded_subcheck_satisfied_not_global_submit=true",
            "legacy compatibility alias: `narrowed_claim_submission_standard_met=true`",
            "legacy compatibility alias: `narrowed_claim_decision=submit_under_narrowed_claim`",
            "full_source_policy_package_ready=false",
            "proof traceability row split: `96` certified non-dynamic rows",
            "`36/0` active direct Newton--Euler closed/open rows",
            "`36` symbolic/primitive-route Newton--Euler rows not certified by that route",
            "CMAME_BLOCKER_CLOSURE_GATE.md",
            "CMAME_EXTERNAL_BASELINE_GATE.md",
            "CMAME_VISUAL_LEGIBILITY_AUDIT.md",
            "CMAME_RELATED_WORK_AUDIT.md",
            "CMAME_PROSE_RESIDUE_AUDIT.md",
            "CMAME_CLAIM_HYGIENE_AUDIT.md",
            "DYNAMIC_ROW_ORACLE_GATE.md",
            "NEWTON_EULER_DEFECT_OBLIGATION_GATE.md",
            "validate_proof_evidence_matrix.py",
            "validate_proof_numerical_scale_audit.py",
            "validate_proof_solver_scale_audit.py",
            "validate_proof_claim_traceability_audit.py",
            "validate_paper_numerical_result_matrix.py",
            "validate_result_to_manuscript_traceability_audit.py",
            "validate_all_method_example_claim_disposition_audit.py",
            "validate_all_examples_result_sanity_audit.py",
            "validate_source_policy_row_closure_ledger.py",
            "cmame_submission_review_agent.py",
            "validate_cmame_review_agent.py",
            "validate_cmame_blocker_closure_gate.py",
            "validate_cmame_submission_integrity_audit.py",
            "validate_cmame_external_baseline_gate.py",
            "validate_cmame_visual_legibility_audit.py",
            "validate_cmame_figure_set_audit.py",
            "validate_cmame_related_work_audit.py",
            "validate_cmame_prose_residue_audit.py",
            "validate_cmame_claim_hygiene_audit.py",
            "validate_dynamic_row_oracle_gate.py",
            "SOURCE_PAPER_COMPARISON.md",
            "validate_source_paper_comparison.py",
            "CROSS_PAPER_BENCHMARK_SPEC.md",
            "CROSS_PAPER_BENCHMARK_CASES.json",
            "EXTERNAL_SAME_TEST_RUN_QUEUE.md",
            "EXTERNAL_SAME_TEST_RUN_QUEUE.json",
            "20 non-default-`1e-4` shards",
            "KISSEL_NEGRUT_CODE_INVENTORY.md",
            "EXTERNAL_SUITE_DISPOSITION_AUDIT.md",
            "EXTERNAL_SUITE_DISPOSITION_AUDIT.json",
            "ALL_EXAMPLES_SOURCE_POLICY_AUDIT.md",
            "ALL_EXAMPLES_SOURCE_POLICY_AUDIT.json",
            "SOURCE_POLICY_CLOSURE_TRIAGE.md",
            "SOURCE_POLICY_CLOSURE_TRIAGE.json",
            "SOURCE_POLICY_ROW_CLOSURE_LEDGER.md",
            "SOURCE_POLICY_ROW_CLOSURE_LEDGER.json",
            "EXTERNAL_CASE_EVIDENCE_RECONCILIATION.md",
            "EXTERNAL_CASE_EVIDENCE_RECONCILIATION.json",
            "RA2021_SOURCE_IDENTITY_AUDIT.md",
            "RA2021_SOURCE_IDENTITY_AUDIT.json",
            "RA2021 source-code identity audit",
            "output mapping and time-grid convention",
            "HI2022_T8_TOLERANCE_REPAIR_AUDIT.md",
            "HI2022_T8_TOLERANCE_REPAIR_AUDIT.json",
            "19/24 rows",
            "4/8",
            "B4_SOURCE_POLICY_POST_EXECUTION_AUDIT.md",
            "B4_SOURCE_POLICY_POST_EXECUTION_AUDIT.json",
            "all 13 ready-command outputs are present",
            "0/40 source-policy rows",
            "B4_SOURCE_POLICY_ROW_CLOSURE_READINESS_LEDGER.md",
            "B4_SOURCE_POLICY_ROW_CLOSURE_READINESS_LEDGER.json",
            "B4_SOURCE_POLICY_ROW_CLOSURE_READINESS_LEDGER.csv",
            "20 rows have launch-command references",
            "20 remain without launch commands",
            "RA2021_DOUBLE_SOURCE_POLICY_LOW_ORDER_DIAGNOSIS.md",
            "RA2021_DOUBLE_SOURCE_POLICY_LOW_ORDER_DIAGNOSIS.json",
            "low-order/floor-limited",
            "HI2022_RA_HALF_DOUBLE_SOURCE_POLICY_FAILURE_DIAGNOSIS.md",
            "HI2022_RA_HALF_DOUBLE_SOURCE_POLICY_FAILURE_DIAGNOSIS.json",
            "completes only 1/3 rows",
            "validate_external_case_evidence_reconciliation.py",
            "validate_ra2021_source_identity_audit.py",
            "validate_hi2022_t8_tolerance_repair_audit.py",
            "VP2024_CODE_PATH_DISPOSITION_AUDIT.md",
            "VP2024_CODE_PATH_DISPOSITION_AUDIT.json",
            "validate_vp2024_code_path_disposition_audit.py",
            "`4/4` VP2024 source-policy rows unresolved",
            "`4/4` VP2024 common-reference proxy order/error wins",
            "`1/4` VP2024 larger-step diagnostic local error wins",
            "RA2021 and HI2022 have bounded/coarse evidence",
            "`0/15` source-policy-closed rows",
            "`0/15` external-superiority-ready rows",
            "COMPARISON_OBJECTIVE_CLOSURE_RECONCILIATION_AUDIT.md",
            "COMPARISON_OBJECTIVE_CLOSURE_RECONCILIATION_AUDIT.json",
            "validate_cross_paper_benchmark_spec.py",
            "validate_cross_paper_benchmark_cases.py",
            "validate_external_same_test_run_queue.py",
            "validate_external_suite_disposition_audit.py",
            "validate_comparison_objective_closure_reconciliation_audit.py",
            "validate_submission_bundle.py",
            "`full_tfe_stage_replacement=false`",
        ],
        "COVER_LETTER.md": [
            "Cover Letter Draft",
            "`main_cmame.pdf`",
            "`Gauss6/FullVA`",
            "`7.161/7.066`",
            "`m=3` Gauss-Lobatto TFE formula target",
            "validate_proof_evidence_matrix.py",
            "validate_source_paper_comparison.py",
            "`full_tfe_stage_replacement=false`",
            "full source-policy runner archive is not ready",
            "Safe actions without B4 opt-in are `4`",
            "opt-in-required actions are `1`",
            "source-policy execution allowed now is `False`",
            "exact B4 opt-in required for",
            "opt-in commands/mapped external rows are `13/20`",
            "Command-row traceability covers unique RA/HI rows `20/20`",
            "row refs `32/32`",
            "mismatch/terminal/closed/promotion-ready counts `0/0/0/0`",
            "Safe action ids are `rebuild_read_only_audit_chain,rerun_read_only_validators,keep_narrowed_archive_provenance_only,monitor_reopen_conditions`",
            "opt-in action ids are `authorized_b4_ra_hi_source_policy_execution`",
            "`run_b4_source_policy_after_opt_in.sh`",
            "I explicitly approve running the B4 source-policy execution commands listed in B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json.",
            "narrowed archive boundary matches the reproducibility manifest: `True`",
            "`narrowed_archive_ready_not_full_source_policy_runner_archive/0/40/False/False/True`",
            "blocking ids/status `OC4,OC6,OC12`",
            "`OC4=open,OC6=partial,OC12=partial`",
            "`narrowed_claim_only`, not a full source-policy runner archive",
        ],
        "SUBMISSION_FILE_INVENTORY.md": [
            "Primary Submission Files",
            "Supporting Evidence Files",
            "Validators",
            "`main_cmame.pdf`",
            "`main_cmame.tex`",
            "`highlights_cmame.txt`",
            "`declarations_cmame.md`",
            "`CMAME_SUBMISSION_CHECKLIST.md`",
            "`CMAME_SUBMISSION_READINESS_AUDIT.md`",
            "`CMAME_SUBMISSION_READINESS_REVIEW.md`",
            "`CMAME_SUBMISSION_INTEGRITY_AUDIT.md`",
            "`CMAME_SUBMISSION_INTEGRITY_AUDIT.json`",
            "`CMAME_BLOCKER_CLOSURE_GATE.md`",
            "`CMAME_BLOCKER_CLOSURE_GATE.json`",
            "`CMAME_EXTERNAL_BASELINE_GATE.md`",
            "`CMAME_EXTERNAL_BASELINE_GATE.json`",
            "`CMAME_VISUAL_LEGIBILITY_AUDIT.md`",
            "`CMAME_VISUAL_LEGIBILITY_AUDIT.json`",
            "`CMAME_FIGURE_SET_AUDIT.md`",
            "`CMAME_FIGURE_SET_AUDIT.json`",
            "`CMAME_RELATED_WORK_AUDIT.md`",
            "`CMAME_RELATED_WORK_AUDIT.json`",
            "`CMAME_PROSE_RESIDUE_AUDIT.md`",
            "`CMAME_PROSE_RESIDUE_AUDIT.json`",
            "`CMAME_CLAIM_HYGIENE_AUDIT.md`",
            "`CMAME_CLAIM_HYGIENE_AUDIT.json`",
            "`B4_SOURCE_POLICY_POST_EXECUTION_AUDIT.md`",
            "`B4_SOURCE_POLICY_POST_EXECUTION_AUDIT.json`",
            "`RA2021_DOUBLE_SOURCE_POLICY_LOW_ORDER_DIAGNOSIS.md`",
            "`RA2021_DOUBLE_SOURCE_POLICY_LOW_ORDER_DIAGNOSIS.json`",
            "`HI2022_RA_HALF_DOUBLE_SOURCE_POLICY_FAILURE_DIAGNOSIS.md`",
            "`HI2022_RA_HALF_DOUBLE_SOURCE_POLICY_FAILURE_DIAGNOSIS.json`",
            "`B4_SOURCE_POLICY_ROW_CLOSURE_READINESS_LEDGER.md`",
            "`B4_SOURCE_POLICY_ROW_CLOSURE_READINESS_LEDGER.json`",
            "`B4_SOURCE_POLICY_ROW_CLOSURE_READINESS_LEDGER.csv`",
            "`B4_SOURCE_POLICY_EXECUTION_HANDOFF_PACKAGE.md`",
            "`B4_SOURCE_POLICY_EXECUTION_HANDOFF_PACKAGE.json`",
            "`B4_SOURCE_POLICY_COMMAND_PREFLIGHT_FREEZE_20260620.md`",
            "`B4_SOURCE_POLICY_COMMAND_PREFLIGHT_FREEZE_20260620.json`",
            "`B4_SOURCE_POLICY_EXPECTED_OUTPUT_SCHEMA_AUDIT_20260620.md`",
            "`B4_SOURCE_POLICY_EXPECTED_OUTPUT_SCHEMA_AUDIT_20260620.json`",
            "`B4_EXPECTED_OUTPUT_PROMOTION_READINESS_BLOCKER_AUDIT_20260620.md`",
            "`B4_EXPECTED_OUTPUT_PROMOTION_READINESS_BLOCKER_AUDIT_20260620.json`",
            "`OC6_SOURCE_EQUIVALENT_REOPEN_READINESS_AUDIT_20260620.md`",
            "`OC6_SOURCE_EQUIVALENT_REOPEN_READINESS_AUDIT_20260620.json`",
            "`FULL_SOURCE_POLICY_RUNNER_ARCHIVE_GAP_AUDIT.md`",
            "`FULL_SOURCE_POLICY_RUNNER_ARCHIVE_GAP_AUDIT.json`",
            "narrowed archive boundary tuple `narrowed_archive_ready_not_full_source_policy_runner_archive/0/40/False/False/True`",
            "matching `CMAME_REPRODUCIBILITY_PACKAGE_MANIFEST.json`",
            "blocking ids/status `OC4,OC6,OC12` / `OC4=open,OC6=partial,OC12=partial`",
            "current archive use is `narrowed_claim_only`, not a full source-policy runner archive",
            "submission-manifest narrowed archive boundary mirror proving manifest/reproducibility-manifest match `True`",
            "`SOURCE_POLICY_REOPEN_CONDITION_MONITOR_20260620.md`",
            "`SOURCE_POLICY_REOPEN_CONDITION_MONITOR_20260620.json`",
            "`DYNAMIC_ROW_ORACLE_GATE.md`",
            "`DYNAMIC_ROW_ORACLE_GATE.json`",
            "`NEWTON_EULER_DEFECT_OBLIGATION_GATE.md`",
            "`NEWTON_EULER_DEFECT_OBLIGATION_GATE.json`",
            "`README_CMAME_FLAT_SUBMISSION.md`",
            "`cmame_submission_flat/main_cmame_submission.tex`",
            "`cmame_submission_flat/main_cmame_submission.pdf`",
            "`cmame_submission_flat.zip`",
            "`cmame_submission_flat/Figure_7_strict_common_reference_work_precision.png`",
            "`cmame_submission_flat/Figure_8_claim_boundary_limitations.png`",
            "`cmame_submission_flat/Figure_9_coarse_baseline_work_precision.png`",
            "`cmame_submission_flat/Figure_10_closed_loop_true_dynamic_order.png`",
            "`cmame_submission_flat/Figure_11_method_stage_architecture.png`",
            "`cmame_submission_flat/Figure_12_all_method_result_matrix.png`",
            "`cmame_submission_flat/Figure_13_work_precision_compendium.png`",
            "`PROOF_EVIDENCE_MATRIX.md`",
            "`PROOF_NUMERICAL_SCALE_AUDIT.md`",
            "`PROOF_NUMERICAL_SCALE_AUDIT.json`",
            "`PROOF_SOLVER_SCALE_AUDIT.md`",
            "`PROOF_SOLVER_SCALE_AUDIT.json`",
            "`PROOF_SOLVER_SCALED_TOLERANCE_PROBE.md`",
            "`PROOF_SOLVER_SCALED_TOLERANCE_PROBE.json`",
            "theorem-level solver proof closure still false",
            "`PROOF_SOLVER_SCALED_TOLERANCE_TRAJECTORY_PROBE.md`",
            "`PROOF_SOLVER_SCALED_TOLERANCE_TRAJECTORY_PROBE.json`",
            "`PROOF_SOLVER_SCALED_TOLERANCE_TRAJECTORY_PROBE.csv`",
            "`PROOF_SOLVER_TOLERANCE_REGIME_SWEEP.md`",
            "`PROOF_SOLVER_TOLERANCE_REGIME_SWEEP.json`",
            "`PROOF_SOLVER_TOLERANCE_REGIME_SWEEP.csv`",
            "`PROOF_CLAIM_TRACEABILITY_AUDIT.md`",
            "`PROOF_CLAIM_TRACEABILITY_AUDIT.json`",
            "`PAPER_NUMERICAL_RESULT_MATRIX.md`",
            "`PAPER_NUMERICAL_RESULT_MATRIX.json`",
            "`PAPER_NUMERICAL_RESULT_MATRIX.csv`",
            "`RESULT_TO_MANUSCRIPT_TRACEABILITY_AUDIT.md`",
            "`RESULT_TO_MANUSCRIPT_TRACEABILITY_AUDIT.json`",
            "`ALL_METHOD_EXAMPLE_CLAIM_DISPOSITION_AUDIT.md`",
            "`ALL_METHOD_EXAMPLE_CLAIM_DISPOSITION_AUDIT.json`",
            "`ALL_EXAMPLES_RESULT_SANITY_AUDIT.md`",
            "`ALL_EXAMPLES_RESULT_SANITY_AUDIT.json`",
            "`ALL_EXAMPLES_SOURCE_POLICY_AUDIT.md`",
            "`ALL_EXAMPLES_SOURCE_POLICY_AUDIT.json`",
            "`SOURCE_POLICY_CLOSURE_TRIAGE.md`",
            "`SOURCE_POLICY_CLOSURE_TRIAGE.json`",
            "`SOURCE_POLICY_ROW_CLOSURE_LEDGER.md`",
            "`SOURCE_POLICY_ROW_CLOSURE_LEDGER.json`",
            "`EXTERNAL_CASE_EVIDENCE_RECONCILIATION.md`",
            "`EXTERNAL_CASE_EVIDENCE_RECONCILIATION.json`",
            "`RA2021_SOURCE_IDENTITY_AUDIT.md`",
            "`RA2021_SOURCE_IDENTITY_AUDIT.json`",
            "`HI2022_T8_TOLERANCE_REPAIR_AUDIT.md`",
            "`HI2022_T8_TOLERANCE_REPAIR_AUDIT.json`",
            "`VP2024_CODE_PATH_DISPOSITION_AUDIT.md`",
            "`VP2024_CODE_PATH_DISPOSITION_AUDIT.json`",
            "`44/44` method/example cells",
            "`15` flagged nonlocal rows",
            "`validate_cmame_submission.py`",
            "`validate_cmame_submission_integrity_audit.py`",
            "`validate_cmame_blocker_closure_gate.py`",
            "`validate_cmame_external_baseline_gate.py`",
            "`validate_cmame_visual_legibility_audit.py`",
            "`validate_cmame_figure_set_audit.py`",
            "`validate_cmame_related_work_audit.py`",
            "`validate_cmame_prose_residue_audit.py`",
            "`validate_cmame_claim_hygiene_audit.py`",
            "`validate_dynamic_row_oracle_gate.py`",
            "`validate_newton_euler_defect_obligation_gate.py`",
            "`validate_newton_euler_virtual_work_wrench_audit.py`",
            "`validate_newton_euler_dynamic_row_closure_contract.py`",
            "`../v048_cross_paper_same_test_benchmarks/validate_closed_loop_true_dynamic_strict_common_reference.py`",
            "`validate_proof_evidence_matrix.py`",
            "`validate_proof_numerical_scale_audit.py`",
            "`validate_proof_solver_scale_audit.py`",
            "`validate_proof_solver_scaled_tolerance_probe.py`",
            "`validate_proof_solver_scaled_tolerance_trajectory_probe.py`",
            "`validate_proof_solver_tolerance_regime_sweep.py`",
            "`validate_proof_claim_traceability_audit.py`",
            "`validate_paper_numerical_result_matrix.py`",
            "`validate_result_to_manuscript_traceability_audit.py`",
            "`validate_all_method_example_claim_disposition_audit.py`",
            "`validate_all_examples_result_sanity_audit.py`",
            "`validate_source_policy_row_closure_ledger.py`",
            "`validate_external_case_evidence_reconciliation.py`",
            "`validate_ra2021_source_identity_audit.py`",
            "`validate_hi2022_t8_tolerance_repair_audit.py`",
            "`validate_vp2024_code_path_disposition_audit.py`",
            "`SOURCE_PAPER_COMPARISON.md`",
            "`validate_source_paper_comparison.py`",
            "`CROSS_PAPER_BENCHMARK_SPEC.md`",
            "`CROSS_PAPER_BENCHMARK_CASES.json`",
            "`EXTERNAL_SAME_TEST_RUN_QUEUE.md`",
            "`EXTERNAL_SAME_TEST_RUN_QUEUE.json`",
            "`KISSEL_NEGRUT_CODE_INVENTORY.md`",
            "`EXTERNAL_SUITE_DISPOSITION_AUDIT.md`",
            "`EXTERNAL_SUITE_DISPOSITION_AUDIT.json`",
            "`VP2024_CODE_PATH_DISPOSITION_AUDIT.md`",
            "`VP2024_CODE_PATH_DISPOSITION_AUDIT.json`",
            "`COMPARISON_OBJECTIVE_CLOSURE_RECONCILIATION_AUDIT.md`",
            "`COMPARISON_OBJECTIVE_CLOSURE_RECONCILIATION_AUDIT.json`",
            "`validate_cross_paper_benchmark_spec.py`",
            "`validate_cross_paper_benchmark_cases.py`",
            "`validate_external_same_test_run_queue.py`",
            "`validate_external_suite_disposition_audit.py`",
            "`validate_comparison_objective_closure_reconciliation_audit.py`",
            "`validate_submission_bundle.py`",
            "`validate_paper_package.py`",
            "must not invoke `run_v047.py`",
        ],
        "CMAME_SUBMISSION_CHECKLIST.md": [
            "Review Agent Gate",
            "`PAPER_NUMERICAL_RESULT_MATRIX.md/json/csv`",
            "`ALL_METHOD_EXAMPLE_CLAIM_DISPOSITION_AUDIT.md/json`",
            "`RESULT_TO_MANUSCRIPT_TRACEABILITY_AUDIT.md/json`",
            "`ALL_EXAMPLES_RESULT_SANITY_AUDIT.md/json`",
            "`40/40` nonlocal method/example rows",
            "`0/40` source-policy-closed nonlocal rows",
            "`SOURCE_POLICY_ROW_CLOSURE_LEDGER.md/json`",
            "`EXTERNAL_CASE_EVIDENCE_RECONCILIATION.md/json`",
            "`VP2024_CODE_PATH_DISPOSITION_AUDIT.md/json`",
            "zero rows are source-policy closed",
            "`4/4` VP2024 source-policy rows unresolved",
            "`4/4` VP2024 common-reference proxy order/error wins",
            "`PROOF_CLAIM_TRACEABILITY_AUDIT.md/json`",
            "`CMAME_SUBMISSION_INTEGRITY_AUDIT.md/json`",
            "`CMAME_REVIEW_AGENT_REPORT.md/json`",
            "`validate_paper_numerical_result_matrix.py` with `44/44` cells from `132`",
            "`validate_result_to_manuscript_traceability_audit.py` with `44/44` manuscript/PDF velocity cells",
            "`validate_all_examples_result_sanity_audit.py` with four examples covered",
            "`validate_source_policy_row_closure_ledger.py`",
            "`validate_external_case_evidence_reconciliation.py`",
            "`15` flagged nonlocal rows quarantined",
            "`validate_proof_claim_traceability_audit.py` with proof labels present",
            "`validate_cmame_submission_integrity_audit.py` with local citation integrity passed",
            "`1/7` theorem interfaces submission-satisfied, `5/7` retained theorem interfaces, `1/7` open P7 nonpromotion boundary",
            "`4/0` close requirements/unsatisfied close requirements",
            "`96` certified non-dynamic rows, `36/0` active direct Newton--Euler",
            "`36` symbolic/primitive-route Newton--Euler rows not",
            "`submission_standard_scope=global_submission_standard`",
            "`decision=do_not_submit_global`",
            "`open_blockers=OC4,OC6,OC12`",
            "`submission_standard_met=False`",
            "`bounded_subcheck_satisfied_not_global_submit`",
            "legacy compatibility aliases",
            "`narrowed_claim_decision=submit_under_narrowed_claim`",
            "`narrowed_claim_submission_standard_met=True`",
            "full source-policy package readiness remains false",
            "narrowed archive boundary matches the reproducibility manifest: `True`",
            "`narrowed_archive_ready_not_full_source_policy_runner_archive/0/40/False/False/True`",
            "Blocking ids/status: `OC4,OC6,OC12` / `OC4=open,OC6=partial,OC12=partial`",
            "Current archive use is `narrowed_claim_only`, not a full source-policy runner archive",
        ],
        "REVIEWER_CHECKLIST.md": [
            "Review Agent Gate",
            "`PAPER_NUMERICAL_RESULT_MATRIX.md/json/csv` covers `44/44` method/example",
            "`RESULT_TO_MANUSCRIPT_TRACEABILITY_AUDIT.md/json` covers `44/44` manuscript/PDF velocity cells",
            "`ALL_EXAMPLES_RESULT_SANITY_AUDIT.md/json` locks the exact `15` flagged",
            "`SOURCE_POLICY_ROW_CLOSURE_LEDGER.md/json` checks each flagged row",
            "`EXTERNAL_CASE_EVIDENCE_RECONCILIATION.md/json` separates full-campaign",
            "`VP2024_CODE_PATH_DISPOSITION_AUDIT.md/json` checks all four VP examples",
            "`0/15` source-policy-closed rows",
            "`4/4` VP2024 source-policy rows unresolved",
            "`4/4` VP2024 common-reference proxy order/error wins",
            "`PROOF_CLAIM_TRACEABILITY_AUDIT.md/json` confirms proof labels",
            "`CMAME_SUBMISSION_INTEGRITY_AUDIT.md/json` confirms local citation integrity",
            "`submission_standard_scope=global_submission_standard`",
            "`decision=do_not_submit_global`",
            "`open_blockers=OC4,OC6,OC12`",
            "`bounded_subcheck_satisfied_not_global_submit`",
            "`narrowed_claim_decision=submit_under_narrowed_claim`",
            "legacy compatibility aliases",
            "full source-policy package readiness false",
            "../.venv_sbel/bin/python cmame_submission_review_agent.py",
            "../.venv_sbel/bin/python validate_cmame_review_agent.py",
            "../.venv_sbel/bin/python validate_paper_numerical_result_matrix.py",
            "../.venv_sbel/bin/python validate_result_to_manuscript_traceability_audit.py",
            "../.venv_sbel/bin/python validate_all_method_example_claim_disposition_audit.py",
            "../.venv_sbel/bin/python validate_all_examples_result_sanity_audit.py",
            "../.venv_sbel/bin/python validate_source_policy_row_closure_ledger.py",
            "../.venv_sbel/bin/python validate_external_case_evidence_reconciliation.py",
            "../.venv_sbel/bin/python validate_vp2024_code_path_disposition_audit.py",
            "../.venv_sbel/bin/python validate_proof_claim_traceability_audit.py",
            "../.venv_sbel/bin/python validate_cmame_submission_integrity_audit.py",
            "flagged_nonlocal_rows=15",
            "direct_pc2_proof_gap_closed=True",
            "submission_standard_met=False",
            "bounded_subcheck_satisfied_not_global_submit=True",
            "legacy_narrowed_claim_submission_standard_met=True",
            "legacy_narrowed_claim_decision=submit_under_narrowed_claim",
            "full_source_policy_submission_ready=False",
            "narrowed archive boundary matches the reproducibility manifest: `True`",
            "`narrowed_archive_ready_not_full_source_policy_runner_archive/0/40/False/False/True`",
            "Blocking ids/status: `OC4,OC6,OC12` / `OC4=open,OC6=partial,OC12=partial`",
            "Current archive use is `narrowed_claim_only`, not a full source-policy runner archive",
        ],
        "REVIEW_RESPONSE_TEMPLATE.md": [
            "What Is The Main Claim?",
            "Why Is Full-TFE Replacement Not Required For The Main Claim?",
            "What Are The Four Validated Examples?",
            "PROOF_EVIDENCE_MATRIX.md",
            "validate_proof_evidence_matrix.py",
            "SOURCE_PAPER_COMPARISON.md",
            "validate_source_paper_comparison.py",
            "main_cmame.pdf",
            "CMAME_SUBMISSION_CHECKLIST.md",
            "What Is The Source-Policy Runner Archive Boundary?",
            "safe actions without B4 opt-in `4`",
            "opt-in-required actions `1`",
            "source-policy execution allowed now `False`",
            "exact B4 opt-in required for",
            "opt-in commands/mapped external rows `13/20`",
            "Command-row traceability covers unique RA/HI rows `20/20`",
            "row refs `32/32`",
            "mismatch/terminal/closed/promotion-ready counts `0/0/0/0`",
            "Safe action ids are `rebuild_read_only_audit_chain,rerun_read_only_validators,keep_narrowed_archive_provenance_only,monitor_reopen_conditions`",
            "opt-in action ids are `authorized_b4_ra_hi_source_policy_execution`",
            "narrowed archive boundary matches the reproducibility manifest: `True`",
            "`narrowed_archive_ready_not_full_source_policy_runner_archive/0/40/False/False/True`",
            "blocking ids/status `OC4,OC6,OC12`",
            "`OC4=open,OC6=partial,OC12=partial`",
            "`narrowed_claim_only`, not a full source-policy runner archive",
            "`run_b4_source_policy_after_opt_in.sh`",
            "I explicitly approve running the B4 source-policy execution commands listed in B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json.",
            "What Should Not Be Claimed?",
            "`full_tfe_stage_replacement=false`",
        ],
    }
    forbidden_tokens = [
        "full_tfe_stage_replacement=true",
        "complete source-paper residual reproduction is accepted",
        "accepted independent full-TFE stage replacement.",
    ]
    stale_tokens_by_file = {
        "SUBMISSION_PACKET.md": [
            "B1-B4 and B6-B7 open",
            "appendix_artifact_macro_count=47",
            "external_reference_web_verification_complete=False",
            "Do not submit yet",
            "not the active theorem closure route",
            "runtime traceability and theorem closure under the direct PC2 proof route",
        ],
        "SUBMISSION_FILE_INVENTORY.md": [
            "direct-substitution theorem closure covers `36/36` rows",
            "theorem closure still false",
        ],
        "CMAME_SUBMISSION_CHECKLIST.md": [
            "external_reference_web_verification_complete=False",
        ],
        "REVIEWER_CHECKLIST.md": [
            "external_reference_web_verification_complete=False",
        ],
    }
    for file_label, tokens in required_tokens.items():
        text = read_text(manuscript_path(file_label))
        for token in tokens:
            checks.check(contains_normalized(text, token), f"{file_label} missing token: {token}")
        for forbidden in forbidden_tokens:
            checks.check(forbidden not in text, f"{file_label} has forbidden claim: {forbidden}")
        for stale in stale_tokens_by_file.get(file_label, []):
            checks.check(not contains_normalized(text, stale), f"{file_label} has stale token: {stale}")


def main() -> int:
    checks = Checks()
    try:
        manifest = read_json(PAPER / "SUBMISSION_ARTIFACT_MANIFEST.json")
        boundary = read_json(PAPER / "CLAIM_BOUNDARY.json")
        summary = read_json(RESULTS / "summary_v047.json")
        result_pack = read_json(PAPER / "PAPER_RESULT_PACK.json")
        objective_completion = read_json(PAPER / "OBJECTIVE_COMPLETION_AUDIT.json")
        full_source_runner_gap = read_json(PAPER / "FULL_SOURCE_POLICY_RUNNER_ARCHIVE_GAP_AUDIT.json")
        reproducibility_manifest = read_json(PAPER / "CMAME_REPRODUCIBILITY_PACKAGE_MANIFEST.json")
    except Exception as exc:  # noqa: BLE001 - concise CLI failure.
        print(f"v047 submission bundle validation: FAIL\n- {exc}")
        return 1

    check_manifest(
        checks,
        manifest,
        boundary,
        summary,
        objective_completion,
        full_source_runner_gap,
        reproducibility_manifest,
    )
    check_paper_result_pack(checks, result_pack, objective_completion)
    check_submission_texts(checks)
    check_log_clean(checks, "main.log")
    check_log_clean(checks, "main_concise.log")
    check_log_clean(checks, "main_cmame.log")
    check_log_clean(checks, "cmame_submission_flat/main_cmame_submission.log")

    for pdf_label in ["main_cmame.pdf", "cmame_submission_flat/main_cmame_submission.pdf", "main_concise.pdf", "main.pdf"]:
        path = manuscript_path(pdf_label)
        checks.check(path.exists() and path.stat().st_size > 100_000, f"{pdf_label} missing or unexpectedly small")

    if checks.errors:
        print("v047 submission bundle validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("v047 submission bundle validation: PASS")
    print("recommended_pdf=main_cmame.pdf")
    print("cmame_document_class=elsarticle")
    print("accepted_method=Gauss6/FullVA")
    print("smooth_projected_orders=7.161/7.066")
    print("comparator_expected_order=5")
    print("asme_models=double_pendulum,four_link,single_pendulum,slider_crank")
    print("full_tfe_stage_replacement=False")
    print("submission_ready=False")
    print("mechanical_preflight_passed=True")
    print("quality_review_passed=False")
    print("proof_solver_scale_audit_validator=checked")
    print("default_1e-4=False")
    print("run_v047_invoked=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
