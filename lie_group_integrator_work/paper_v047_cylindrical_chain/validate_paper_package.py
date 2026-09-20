#!/usr/bin/env python3
"""Run the lightweight validation chain for the v047 paper package.

This wrapper is intentionally read-only by default. It checks the existing PDF
and generated artifacts, and it never invokes run_v047.py. Pass --latex to also
attempt a PDF rebuild from this wrapper.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path


PAPER = Path(__file__).resolve().parent
ROOT = PAPER.parent
PIPELINE = ROOT / "v047_cylindrical_chain_pipeline"
PYTHON = ROOT / ".venv_sbel" / "bin" / "python"


def run_step(name: str, cmd: list[str], cwd: Path, show_tail: int = 8) -> tuple[bool, str]:
    proc = subprocess.run(cmd, cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output = proc.stdout.strip()
    status = "PASS" if proc.returncode == 0 else "FAIL"
    print(f"[{status}] {name}")
    if output:
        lines = output.splitlines()
        for line in lines[-show_tail:]:
            print(f"  {line}")
    return proc.returncode == 0, output


def latex_command(target: str = "main.tex") -> list[str]:
    if os.name == "nt":
        return ["latexmk", "-pdf", "-interaction=nonstopmode", target]
    return ["cmd.exe", "/c", "latexmk", "-pdf", "-interaction=nonstopmode", target]


def contains_normalized(text: str, token: str) -> bool:
    return token in text or " ".join(token.split()) in " ".join(text.split())


def check_latex_log() -> bool:
    patterns = [
        r"Overfull",
        r"LaTeX Warning",
        r"Package .*Warning",
        r"pdfTeX warning",
    ]
    failures: list[str] = []
    checked: list[str] = []
    for log_name in ["main.log", "main_concise.log", "main_cmame.log", "cmame_submission_flat/main_cmame_submission.log", "arxiv/main_arxiv.log"]:
        log_path = PAPER / log_name
        if not log_path.exists():
            failures.append(f"{log_name} is missing; run with --latex or rebuild PDFs first")
            continue
        checked.append(log_name)
        log_text = log_path.read_text(errors="replace")
        for line in log_text.splitlines():
            if any(re.search(pattern, line) for pattern in patterns):
                failures.append(f"{log_name}: {line}")

    print("[", end="")
    if failures:
        print("FAIL] latex log cleanliness")
        for line in failures[-8:]:
            print(f"  {line}")
        return False

    print("PASS] latex log cleanliness")
    print(f"  {', '.join(checked)} have no Overfull/LaTeX/Package/pdfTeX warnings")
    return True


def check_required_files() -> bool:
    required_files = [
        PAPER / "main.tex",
        PAPER / "main.pdf",
        PAPER / "main.log",
        PAPER / "main_concise.tex",
        PAPER / "main_concise.pdf",
        PAPER / "main_concise.log",
        PAPER / "main_cmame.tex",
        PAPER / "main_cmame.pdf",
        PAPER / "main_cmame.log",
        PAPER / "highlights_cmame.txt",
        PAPER / "declarations_cmame.md",
        PAPER / "CMAME_SUBMISSION_CHECKLIST.md",
        PAPER / "CMAME_SUBMISSION_READINESS_AUDIT.md",
        PAPER / "CMAME_SUBMISSION_READINESS_REVIEW.md",
        PAPER / "CMAME_PDF_STYLE_REVIEW_AUDIT.md",
        PAPER / "CMAME_PDF_STYLE_REVIEW_AUDIT.json",
        PAPER / "CMAME_SUBMISSION_INTEGRITY_AUDIT.md",
        PAPER / "CMAME_SUBMISSION_INTEGRITY_AUDIT.json",
        PAPER / "REFERENCE_METADATA_AUDIT.md",
        PAPER / "REFERENCE_METADATA_AUDIT.json",
        PAPER / "CMAME_BLOCKER_CLOSURE_GATE.md",
        PAPER / "CMAME_BLOCKER_CLOSURE_GATE.json",
        PAPER / "CMAME_EXTERNAL_BASELINE_GATE.md",
        PAPER / "CMAME_EXTERNAL_BASELINE_GATE.json",
        PAPER / "CMAME_PROOF_CONTRACT_GATE.md",
        PAPER / "CMAME_PROOF_CONTRACT_GATE.json",
        PAPER / "CMAME_VISUAL_LEGIBILITY_AUDIT.md",
        PAPER / "CMAME_VISUAL_LEGIBILITY_AUDIT.json",
        PAPER / "CMAME_FIGURE_SET_AUDIT.md",
        PAPER / "CMAME_FIGURE_SET_AUDIT.json",
        PAPER / "CMAME_SCALABILITY_BOUNDARY_AUDIT.md",
        PAPER / "CMAME_SCALABILITY_BOUNDARY_AUDIT.json",
        PAPER / "CMAME_RELATED_WORK_AUDIT.md",
        PAPER / "CMAME_RELATED_WORK_AUDIT.json",
        PAPER / "CMAME_PROSE_RESIDUE_AUDIT.md",
        PAPER / "CMAME_PROSE_RESIDUE_AUDIT.json",
        PAPER / "CMAME_NARROWED_CLAIM_CLOSURE_POLICY_AUDIT.md",
        PAPER / "CMAME_NARROWED_CLAIM_CLOSURE_POLICY_AUDIT.json",
        PAPER / "build_cmame_narrowed_claim_closure_policy_audit.py",
        PAPER / "validate_cmame_narrowed_claim_closure_policy_audit.py",
        PAPER / "CMAME_PROOF_STYLE_AUDIT.md",
        PAPER / "CMAME_PROOF_STYLE_AUDIT.json",
        PAPER / "CMAME_STRICT_PROOF_AUDIT.md",
        PAPER / "CMAME_STRICT_PROOF_AUDIT.json",
        PAPER / "CMAME_STRICT_PROOF_POLICY_RECONCILIATION_AUDIT.md",
        PAPER / "CMAME_STRICT_PROOF_POLICY_RECONCILIATION_AUDIT.json",
        PAPER / "build_cmame_strict_proof_policy_reconciliation_audit.py",
        PAPER / "validate_cmame_strict_proof_policy_reconciliation_audit.py",
        PAPER / "PROOF_CLOSURE_MANIFEST.md",
        PAPER / "PROOF_CLOSURE_MANIFEST.json",
        PAPER / "PROOF_CLAIM_TRACEABILITY_AUDIT.md",
        PAPER / "PROOF_CLAIM_TRACEABILITY_AUDIT.json",
        PAPER / "D5_DYNAMIC_DEFECT_READINESS_AUDIT.md",
        PAPER / "D5_DYNAMIC_DEFECT_READINESS_AUDIT.json",
        PAPER / "D5_DYNAMIC_DIRECT_SUBSTITUTION_CERTIFICATE.md",
        PAPER / "D5_DYNAMIC_DIRECT_SUBSTITUTION_CERTIFICATE.json",
        PAPER / "D5_TAYLOR_TERM_BUDGET_AUDIT.md",
        PAPER / "D5_TAYLOR_TERM_BUDGET_AUDIT.json",
        PAPER / "D5_PRIMITIVE_BOUND_REDUCTION_AUDIT.md",
        PAPER / "D5_PRIMITIVE_BOUND_REDUCTION_AUDIT.json",
        PAPER / "D5_P_TUBE_CONSTANTS_AUDIT.md",
        PAPER / "D5_P_TUBE_CONSTANTS_AUDIT.json",
        PAPER / "D5_P_STATE_LIFT_GAP_AUDIT.md",
        PAPER / "D5_P_STATE_LIFT_GAP_AUDIT.json",
        PAPER / "D5_P_STATE_MAP_DEFINITION_AUDIT.md",
        PAPER / "D5_P_STATE_MAP_DEFINITION_AUDIT.json",
        PAPER / "D5_P_STATE_ANTICIRCULARITY_AUDIT.md",
        PAPER / "D5_P_STATE_ANTICIRCULARITY_AUDIT.json",
        PAPER / "D5_P_STATE_PS2_WEIGHTED_TARGET_AUDIT.md",
        PAPER / "D5_P_STATE_PS2_WEIGHTED_TARGET_AUDIT.json",
        PAPER / "D5_P_STATE_PS2_KINEMATIC_BLOCK_CERTIFICATE.md",
        PAPER / "D5_P_STATE_PS2_KINEMATIC_BLOCK_CERTIFICATE.json",
        PAPER / "D5_P_STATE_PS2_LIE_CHART_BINDING_AUDIT.md",
        PAPER / "D5_P_STATE_PS2_LIE_CHART_BINDING_AUDIT.json",
        PAPER / "D5_P_STATE_PS2_ROW_INJECTION_AUDIT.md",
        PAPER / "D5_P_STATE_PS2_ROW_INJECTION_AUDIT.json",
        PAPER / "D5_P_STATE_PS2_NONLINEAR_BINDING_AUDIT.md",
        PAPER / "D5_P_STATE_PS2_NONLINEAR_BINDING_AUDIT.json",
        PAPER / "D5_P_STATE_PS2_AGGREGATE_PROMOTION_AUDIT.md",
        PAPER / "D5_P_STATE_PS2_AGGREGATE_PROMOTION_AUDIT.json",
        PAPER / "D5_P_STATE_PS2_LINEARIZATION_PROBE.md",
        PAPER / "D5_P_STATE_PS2_LINEARIZATION_PROBE.json",
        PAPER / "D5_P_STATE_PS2_LINEARIZATION_PROBE.csv",
        PAPER / "D5_P_STATE_PS3_CONDITIONAL_CONVERSION_AUDIT.md",
        PAPER / "D5_P_STATE_PS3_CONDITIONAL_CONVERSION_AUDIT.json",
        PAPER / "D5_P_STATE_PS3_ACTUAL_INSTANTIATION_GAP_AUDIT.md",
        PAPER / "D5_P_STATE_PS3_ACTUAL_INSTANTIATION_GAP_AUDIT.json",
        PAPER / "D5_P_STATE_PS3_H_ACC_INPUT_OBSTRUCTION_AUDIT.md",
        PAPER / "D5_P_STATE_PS3_H_ACC_INPUT_OBSTRUCTION_AUDIT.json",
        PAPER / "D5_P_STATE_PS3_FULL_RESIDUAL_ROUTE_CERTIFICATE.md",
        PAPER / "D5_P_STATE_PS3_FULL_RESIDUAL_ROUTE_CERTIFICATE.json",
        PAPER / "D5_P_ACC_MAP_DEFINITION_AUDIT.md",
        PAPER / "D5_P_ACC_MAP_DEFINITION_AUDIT.json",
        PAPER / "D5_P_ACC_ROW_BINDING_AUDIT.md",
        PAPER / "D5_P_ACC_ROW_BINDING_AUDIT.json",
        PAPER / "D5_P_ACC_INDEPENDENCE_AUDIT.md",
        PAPER / "D5_P_ACC_INDEPENDENCE_AUDIT.json",
        PAPER / "D5_P_ACC_LIFT_OBSTRUCTION_AUDIT.md",
        PAPER / "D5_P_ACC_LIFT_OBSTRUCTION_AUDIT.json",
        PAPER / "D5_P_ACC_PA2_WEIGHTED_INVERSE_AUDIT.md",
        PAPER / "D5_P_ACC_PA2_WEIGHTED_INVERSE_AUDIT.json",
        PAPER / "D5_P_LAMBDA_INTERFACE_AUDIT.md",
        PAPER / "D5_P_LAMBDA_INTERFACE_AUDIT.json",
        PAPER / "D5_P_LAMBDA_INF_SUP_PROBE.md",
        PAPER / "D5_P_LAMBDA_INF_SUP_PROBE.json",
        PAPER / "D5_P_LAMBDA_INF_SUP_PROBE.csv",
        PAPER / "D5_P_LAMBDA_PL2_GEOMETRIC_MARGIN_AUDIT.md",
        PAPER / "D5_P_LAMBDA_PL2_GEOMETRIC_MARGIN_AUDIT.json",
        PAPER / "D5_P_LAMBDA_D3_NONCIRCULARITY_AUDIT.md",
        PAPER / "D5_P_LAMBDA_D3_NONCIRCULARITY_AUDIT.json",
        PAPER / "D5_P_LAMBDA_PL4_RATE_PROPAGATION_AUDIT.md",
        PAPER / "D5_P_LAMBDA_PL4_RATE_PROPAGATION_AUDIT.json",
        PAPER / "D5_P_GEOM_CHART_REDUCTION_AUDIT.md",
        PAPER / "D5_P_GEOM_CHART_REDUCTION_AUDIT.json",
        PAPER / "D5_P_GYRO_BILINEAR_REDUCTION_AUDIT.md",
        PAPER / "D5_P_GYRO_BILINEAR_REDUCTION_AUDIT.json",
        PAPER / "D5_OPEN_PRIMITIVE_GAP_AUDIT.md",
        PAPER / "D5_OPEN_PRIMITIVE_GAP_AUDIT.json",
        PAPER / "D5_PRIMITIVE_OBLIGATION_CLOSURE_PLAN.md",
        PAPER / "D5_PRIMITIVE_OBLIGATION_CLOSURE_PLAN.json",
        PAPER / "D5_CONDITIONAL_TAYLOR_CERTIFICATE.md",
        PAPER / "D5_CONDITIONAL_TAYLOR_CERTIFICATE.json",
        PAPER / "ALL_EXAMPLES_RESULT_SANITY_AUDIT.md",
        PAPER / "ALL_EXAMPLES_RESULT_SANITY_AUDIT.json",
        PAPER / "COMMON_REFERENCE_ORDER_RECOMPUTATION_AUDIT.md",
        PAPER / "COMMON_REFERENCE_ORDER_RECOMPUTATION_AUDIT.json",
        PAPER / "EXTERNAL_BASELINE_SOURCE_POLICY_DIAGNOSIS.md",
        PAPER / "EXTERNAL_BASELINE_SOURCE_POLICY_DIAGNOSIS.json",
        PAPER / "SOURCE_POLICY_CLOSURE_TRIAGE.md",
        PAPER / "SOURCE_POLICY_CLOSURE_TRIAGE.json",
        PAPER / "SOURCE_POLICY_ROW_CLOSURE_LEDGER.md",
        PAPER / "SOURCE_POLICY_ROW_CLOSURE_LEDGER.json",
        PAPER / "SOURCE_POLICY_LOCAL_CANDIDATE_GAP_AUDIT.md",
        PAPER / "SOURCE_POLICY_LOCAL_CANDIDATE_GAP_AUDIT.json",
        PAPER / "ALL_EXAMPLES_SOURCE_POLICY_AUDIT.md",
        PAPER / "ALL_EXAMPLES_SOURCE_POLICY_AUDIT.json",
        PAPER / "EXTERNAL_SUITE_DISPOSITION_AUDIT.md",
        PAPER / "EXTERNAL_SUITE_DISPOSITION_AUDIT.json",
        PAPER / "EXTERNAL_SOURCE_POLICY_CLOSURE_MANIFEST.md",
        PAPER / "EXTERNAL_SOURCE_POLICY_CLOSURE_MANIFEST.json",
        PAPER / "EXTERNAL_CASE_EVIDENCE_RECONCILIATION.md",
        PAPER / "EXTERNAL_CASE_EVIDENCE_RECONCILIATION.json",
        PAPER / "VP2024_CODE_PATH_DISPOSITION_AUDIT.md",
        PAPER / "VP2024_CODE_PATH_DISPOSITION_AUDIT.json",
        PAPER / "TFE_SOURCE_POLICY_SPEC.md",
        PAPER / "TFE_SOURCE_POLICY_SPEC.json",
        PAPER / "TFE_SOURCE_POLICY_ROW_AUDIT.md",
        PAPER / "TFE_SOURCE_POLICY_ROW_AUDIT.json",
        PAPER / "TFE_B4_B7_SOURCE_POLICY_DEMOTION_AUDIT.md",
        PAPER / "TFE_B4_B7_SOURCE_POLICY_DEMOTION_AUDIT.json",
        PAPER / "TFE_SOURCE_PENDULUM_MODEL_AUDIT.md",
        PAPER / "TFE_SOURCE_PENDULUM_MODEL_AUDIT.json",
        PAPER / "TFE_BROWN_MCPHEE_SOURCE_LAW_BOUNDARY_AUDIT.md",
        PAPER / "TFE_BROWN_MCPHEE_SOURCE_LAW_BOUNDARY_AUDIT.json",
        PAPER / "build_tfe_brown_mcphee_source_law_boundary_audit.py",
        PAPER / "validate_tfe_brown_mcphee_source_law_boundary_audit.py",
        PAPER / "TFE_BROWN_MCPHEE_SOURCE_CODE_EQUIVALENCE_CERTIFICATE.md",
        PAPER / "TFE_BROWN_MCPHEE_SOURCE_CODE_EQUIVALENCE_CERTIFICATE.json",
        PAPER / "build_tfe_brown_mcphee_source_code_equivalence_certificate.py",
        PAPER / "validate_tfe_brown_mcphee_source_code_equivalence_certificate.py",
        PAPER / "TFE_DAE_RUNNER_CONTRACT_GAP_AUDIT.md",
        PAPER / "TFE_DAE_RUNNER_CONTRACT_GAP_AUDIT.json",
        PAPER / "build_tfe_dae_runner_contract_gap_audit.py",
        PAPER / "validate_tfe_dae_runner_contract_gap_audit.py",
        PAPER / "TFE_RUNNER_CONTRACT_PREFLIGHT_CERTIFICATE.md",
        PAPER / "TFE_RUNNER_CONTRACT_PREFLIGHT_CERTIFICATE.json",
        PAPER / "build_tfe_runner_contract_preflight_certificate.py",
        PAPER / "validate_tfe_runner_contract_preflight_certificate.py",
        PAPER / "TFE_FULL_T10_ABSOLUTE_DAE_LIFT_SUMMARY.md",
        PAPER / "TFE_FULL_T10_ABSOLUTE_DAE_LIFT_SUMMARY.json",
        PAPER / "TFE_FULL_T10_ABSOLUTE_DAE_LIFT_SUMMARY.csv",
        PAPER / "build_tfe_full_t10_absolute_dae_lift_summary.py",
        PAPER / "validate_tfe_full_t10_absolute_dae_lift_summary.py",
        PAPER / "TFE_SOURCE_GRID_COMPATIBILITY_AUDIT.md",
        PAPER / "TFE_SOURCE_GRID_COMPATIBILITY_AUDIT.json",
        PAPER / "TFE_ENDPOINT_POLICY_BOUNDARY_CERTIFICATE.md",
        PAPER / "TFE_ENDPOINT_POLICY_BOUNDARY_CERTIFICATE.json",
        PAPER / "TFE_ENDPOINT_POLICY_BOUNDARY_CERTIFICATE.csv",
        PAPER / "build_tfe_endpoint_policy_boundary_certificate.py",
        PAPER / "validate_tfe_endpoint_policy_boundary_certificate.py",
        PAPER / "TFE_ENDPOINT_POLICY_SENSITIVITY_AUDIT.md",
        PAPER / "TFE_ENDPOINT_POLICY_SENSITIVITY_AUDIT.json",
        PAPER / "TFE_ENDPOINT_POLICY_SENSITIVITY_AUDIT.csv",
        PAPER / "TFE_FULL_T10_ENDPOINT_POLICY_CLOSURE_CERTIFICATE.md",
        PAPER / "TFE_FULL_T10_ENDPOINT_POLICY_CLOSURE_CERTIFICATE.json",
        PAPER / "build_tfe_full_t10_endpoint_policy_closure_certificate.py",
        PAPER / "validate_tfe_full_t10_endpoint_policy_closure_certificate.py",
        PAPER / "TFE_SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_CERTIFICATE.md",
        PAPER / "TFE_SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_CERTIFICATE.json",
        PAPER / "build_tfe_source_policy_self_reproduction_attempt_certificate.py",
        PAPER / "validate_tfe_source_policy_self_reproduction_attempt_certificate.py",
        PAPER / "OBJECTIVE_COMPLETION_AUDIT.md",
        PAPER / "OBJECTIVE_COMPLETION_AUDIT.json",
        PAPER / "COMPARISON_OBJECTIVE_CLOSURE_RECONCILIATION_AUDIT.md",
        PAPER / "COMPARISON_OBJECTIVE_CLOSURE_RECONCILIATION_AUDIT.json",
        PAPER / "PAPER_RESULT_PACK.md",
        PAPER / "PAPER_RESULT_PACK.json",
        PAPER / "PAPER_NUMERICAL_RESULT_MATRIX.md",
        PAPER / "PAPER_NUMERICAL_RESULT_MATRIX.json",
        PAPER / "PAPER_NUMERICAL_RESULT_MATRIX.csv",
        PAPER / "FOUR_EXAMPLE_SOURCE_POLICY_DASHBOARD.md",
        PAPER / "FOUR_EXAMPLE_SOURCE_POLICY_DASHBOARD.json",
        PAPER / "RESULT_TO_MANUSCRIPT_TRACEABILITY_AUDIT.md",
        PAPER / "RESULT_TO_MANUSCRIPT_TRACEABILITY_AUDIT.json",
        PAPER / "ALL_METHOD_EXAMPLE_CLAIM_DISPOSITION_AUDIT.md",
        PAPER / "ALL_METHOD_EXAMPLE_CLAIM_DISPOSITION_AUDIT.json",
        PAPER / "CMAME_REVIEW_AGENT_REPORT.md",
        PAPER / "CMAME_REVIEW_AGENT_REPORT.json",
        PAPER / "FULL_SOURCE_POLICY_RUNNER_ARCHIVE_GAP_AUDIT.md",
        PAPER / "FULL_SOURCE_POLICY_RUNNER_ARCHIVE_GAP_AUDIT.json",
        PAPER / "build_full_source_policy_runner_archive_gap_audit.py",
        PAPER / "validate_full_source_policy_runner_archive_gap_audit.py",
        PAPER / "CMAME_REPRODUCIBILITY_PACKAGE_MANIFEST.md",
        PAPER / "CMAME_REPRODUCIBILITY_PACKAGE_MANIFEST.json",
        PAPER / "CMAME_RUNNER_CENTERED_REPRODUCIBILITY_AUDIT.md",
        PAPER / "CMAME_RUNNER_CENTERED_REPRODUCIBILITY_AUDIT.json",
        PAPER / "build_cmame_runner_centered_reproducibility_audit.py",
        PAPER / "validate_cmame_runner_centered_reproducibility_audit.py",
        PAPER / "CMAME_RUNNER_ADAPTER_CANDIDATE_MANIFEST.md",
        PAPER / "CMAME_RUNNER_ADAPTER_CANDIDATE_MANIFEST.json",
        PAPER / "build_cmame_runner_adapter_candidate.py",
        PAPER / "validate_cmame_runner_adapter_candidate.py",
        PAPER / "CMAME_SELF_CONTAINED_RUNNER_EXTRACTION_PLAN.md",
        PAPER / "CMAME_SELF_CONTAINED_RUNNER_EXTRACTION_PLAN.json",
        PAPER / "build_cmame_self_contained_runner_extraction_plan.py",
        PAPER / "validate_cmame_self_contained_runner_extraction_plan.py",
        PAPER / "run_b6_four_example_local_evidence.py",
        PAPER / "validate_b6_four_example_local_evidence.py",
        PAPER / "B6_FOUR_EXAMPLE_LOCAL_EVIDENCE_SUMMARY.md",
        PAPER / "B6_FOUR_EXAMPLE_LOCAL_EVIDENCE_SUMMARY.json",
        PAPER / "B6_CLOSED_LOOP_SELF_CONTAINED_EXTRACTION_AUDIT.md",
        PAPER / "B6_CLOSED_LOOP_SELF_CONTAINED_EXTRACTION_AUDIT.json",
        PAPER / "build_b6_closed_loop_self_contained_extraction_audit.py",
        PAPER / "validate_b6_closed_loop_self_contained_extraction_audit.py",
        PAPER / "CMAME_CLOSED_LOOP_LOCAL_RUNNER_CANDIDATE_MANIFEST.md",
        PAPER / "CMAME_CLOSED_LOOP_LOCAL_RUNNER_CANDIDATE_MANIFEST.json",
        PAPER / "build_cmame_closed_loop_local_runner_candidate.py",
        PAPER / "validate_cmame_closed_loop_local_runner_candidate.py",
        PAPER / "cmame_closed_loop_local_runner_candidate" / "README.md",
        PAPER / "cmame_closed_loop_local_runner_candidate" / "MANIFEST.json",
        PAPER / "cmame_closed_loop_local_runner_candidate" / "scripts" / "run_closed_loop_fullva_candidate.py",
        PAPER / "cmame_closed_loop_local_runner_candidate" / "results" / "closed_loop_local_summary.json",
        PAPER / "cmame_closed_loop_local_runner_candidate" / "results" / "closed_loop_local_rows.csv",
        PAPER / "CMAME_P1_LOCAL_RUNNER_EXTRACTION_AUDIT.md",
        PAPER / "CMAME_P1_LOCAL_RUNNER_EXTRACTION_AUDIT.json",
        PAPER / "build_cmame_p1_local_runner_extraction_audit.py",
        PAPER / "validate_cmame_p1_local_runner_extraction_audit.py",
        PAPER / "validate_cmame_p1_single_runner_candidate.py",
        PAPER / "cmame_p1_single_runner_candidate" / "README.md",
        PAPER / "cmame_p1_single_runner_candidate" / "scripts" / "run_single_pendulum_fullva.py",
        PAPER / "cmame_p1_single_runner_candidate" / "results" / "single_pendulum_summary.json",
        PAPER / "cmame_p1_single_runner_candidate" / "results" / "single_pendulum_rows.csv",
        PAPER / "validate_cmame_p1_double_runner_candidate.py",
        PAPER / "cmame_p1_double_runner_candidate" / "README.md",
        PAPER / "cmame_p1_double_runner_candidate" / "scripts" / "run_double_pendulum_fullva.py",
        PAPER / "cmame_p1_double_runner_candidate" / "results" / "double_pendulum_summary.json",
        PAPER / "cmame_p1_double_runner_candidate" / "results" / "double_pendulum_rows.csv",
        PAPER / "CMAME_LOCAL_ACCEPTED_RUNNER_COMPANION_MANIFEST.md",
        PAPER / "CMAME_LOCAL_ACCEPTED_RUNNER_COMPANION_MANIFEST.json",
        PAPER / "build_cmame_local_accepted_runner_companion.py",
        PAPER / "validate_cmame_local_accepted_runner_companion.py",
        PAPER / "cmame_local_accepted_runner_companion" / "README.md",
        PAPER / "cmame_local_accepted_runner_companion" / "MANIFEST.json",
        PAPER / "cmame_local_accepted_runner_companion" / "scripts" / "run_local_accepted_runner_companion.py",
        PAPER / "cmame_narrowed_repro_bundle" / "README.md",
        PAPER / "cmame_narrowed_repro_bundle" / "MANIFEST.json",
        PAPER / "cmame_narrowed_repro_bundle" / "scripts" / "run_narrowed_repro_bundle.py",
        PAPER / "cmame_narrowed_repro_bundle" / "results" / "narrowed_repro_bundle_report.md",
        PAPER / "cmame_narrowed_repro_bundle" / "results" / "narrowed_repro_bundle_summary.json",
        PAPER / "cmame_narrowed_repro_bundle" / "results" / "narrowed_repro_bundle_summary.md",
        PAPER / "validate_cmame_narrowed_repro_bundle.py",
        PAPER / "cmame_runner_adapter_candidate" / "README.md",
        PAPER / "cmame_runner_adapter_candidate" / "MANIFEST.json",
        PAPER / "cmame_runner_adapter_candidate" / "scripts" / "run_four_example_matrix_adapter.py",
        PAPER / "cmame_runner_adapter_candidate" / "scripts" / "replay_closed_loop_local_rows.py",
        PAPER / "cmame_runner_adapter_candidate" / "results" / "closed_loop_local_rows_summary.json",
        PAPER / "cmame_runner_adapter_candidate" / "results" / "closed_loop_local_rows.csv",
        PAPER / "CMAME_MINIMAL_REPRODUCIBILITY_CANDIDATE_MANIFEST.md",
        PAPER / "CMAME_MINIMAL_REPRODUCIBILITY_CANDIDATE_MANIFEST.json",
        PAPER / "build_cmame_minimal_reproducibility_candidate.py",
        PAPER / "validate_cmame_minimal_reproducibility_candidate.py",
        PAPER / "cmame_minimal_reproducibility_candidate" / "README.md",
        PAPER / "cmame_minimal_reproducibility_candidate" / "MANIFEST.json",
        PAPER / "cmame_minimal_reproducibility_candidate" / "scripts" / "replay_paper_matrix.py",
        PAPER / "DYNAMIC_ROW_ORACLE_GATE.md",
        PAPER / "DYNAMIC_ROW_ORACLE_GATE.json",
        PAPER / "KINEMATIC_ROW_DEFECT_CERTIFICATE.md",
        PAPER / "KINEMATIC_ROW_DEFECT_CERTIFICATE.json",
        PAPER / "NEWTON_EULER_DEFECT_OBLIGATION_GATE.md",
        PAPER / "NEWTON_EULER_DEFECT_OBLIGATION_GATE.json",
        PAPER / "NEWTON_EULER_VIRTUAL_WORK_WRENCH_AUDIT.md",
        PAPER / "NEWTON_EULER_VIRTUAL_WORK_WRENCH_AUDIT.json",
        PAPER / "build_newton_euler_virtual_work_wrench_audit.py",
        PAPER / "validate_newton_euler_virtual_work_wrench_audit.py",
        PAPER / "NEWTON_EULER_SYMBOLIC_DEFECT_CERTIFICATE.md",
        PAPER / "NEWTON_EULER_SYMBOLIC_DEFECT_CERTIFICATE.json",
        PAPER / "build_newton_euler_symbolic_defect_certificate.py",
        PAPER / "validate_newton_euler_symbolic_defect_certificate.py",
        PAPER / "NEWTON_EULER_AD_EXPANDED_ROW_ORACLE_AUDIT.md",
        PAPER / "NEWTON_EULER_AD_EXPANDED_ROW_ORACLE_AUDIT.json",
        PAPER / "build_newton_euler_ad_expanded_row_oracle_audit.py",
        PAPER / "validate_newton_euler_ad_expanded_row_oracle_audit.py",
        PAPER / "B1_SYMBOLIC_ROW_ORACLE_CLOSURE_CERTIFICATE.md",
        PAPER / "B1_SYMBOLIC_ROW_ORACLE_CLOSURE_CERTIFICATE.json",
        PAPER / "build_b1_symbolic_row_oracle_closure_certificate.py",
        PAPER / "validate_b1_symbolic_row_oracle_closure_certificate.py",
        PAPER / "B1_AD_EXPANDED_SYMBOLIC_ORACLE_CLOSURE_CERTIFICATE.md",
        PAPER / "B1_AD_EXPANDED_SYMBOLIC_ORACLE_CLOSURE_CERTIFICATE.json",
        PAPER / "build_b1_ad_expanded_symbolic_oracle_closure_certificate.py",
        PAPER / "validate_b1_ad_expanded_symbolic_oracle_closure_certificate.py",
        PAPER / "NEWTON_EULER_DYNAMIC_ROW_CLOSURE_CONTRACT.md",
        PAPER / "NEWTON_EULER_DYNAMIC_ROW_CLOSURE_CONTRACT.json",
        PAPER / "build_newton_euler_dynamic_row_closure_contract.py",
        PAPER / "validate_newton_euler_dynamic_row_closure_contract.py",
        PAPER / "README_CMAME_FLAT_SUBMISSION.md",
        PAPER / "cmame_submission_flat.zip",
        PAPER / "cmame_submission_flat" / "main_cmame_submission.tex",
        PAPER / "cmame_submission_flat" / "main_cmame_submission.pdf",
        PAPER / "cmame_submission_flat" / "main_cmame_submission.log",
        PAPER / "cmame_submission_flat" / "highlights_cmame.txt",
        PAPER / "cmame_submission_flat" / "declarations_cmame.md",
        PAPER / "cmame_submission_flat" / "Figure_1_convergence.png",
        PAPER / "cmame_submission_flat" / "Figure_2_asme_lower_pair_graph_bridge.png",
        PAPER / "cmame_submission_flat" / "Figure_3_asme_closed_loop_kinematic_fullva.png",
        PAPER / "cmame_submission_flat" / "Figure_4_order_closure_blend.png",
        PAPER / "cmame_submission_flat" / "Figure_5_velocity_compression.png",
        PAPER / "cmame_submission_flat" / "Figure_6_sparse_speed_gap.png",
        PAPER / "cmame_submission_flat" / "Figure_7_strict_common_reference_work_precision.png",
        PAPER / "cmame_submission_flat" / "Figure_8_claim_boundary_limitations.png",
        PAPER / "cmame_submission_flat" / "Figure_9_coarse_baseline_work_precision.png",
        PAPER / "cmame_submission_flat" / "Figure_10_closed_loop_true_dynamic_order.png",
        PAPER / "cmame_submission_flat" / "Figure_11_method_stage_architecture.png",
        PAPER / "cmame_submission_flat" / "Figure_12_all_method_result_matrix.png",
        PAPER / "cmame_submission_flat" / "Figure_13_work_precision_compendium.png",
        PAPER / "README.md",
        PAPER / "CLAIM_BOUNDARY.json",
        PAPER / "CURRENT_STATUS_CN.md",
        PAPER / "PAPER_CLAIM_LEDGER.md",
        PAPER / "REVIEWER_CHECKLIST.md",
        PAPER / "SUBMISSION_PACKET.md",
        PAPER / "COVER_LETTER.md",
        PAPER / "SUBMISSION_ARTIFACT_MANIFEST.json",
        PAPER / "SUBMISSION_FILE_INVENTORY.md",
        PAPER / "REVIEW_RESPONSE_TEMPLATE.md",
        PAPER / "SOURCE_PAPER_COMPARISON.md",
        PAPER / "CROSS_PAPER_BENCHMARK_MATRIX.md",
        PAPER / "CROSS_PAPER_BENCHMARK_SPEC.md",
        PAPER / "CROSS_PAPER_BENCHMARK_CASES.json",
        PAPER / "EXTERNAL_SAME_TEST_RUN_QUEUE.md",
        PAPER / "EXTERNAL_SAME_TEST_RUN_QUEUE.json",
        PAPER / "KISSEL_NEGRUT_CODE_INVENTORY.md",
        PAPER / "PROOF_EVIDENCE_MATRIX.md",
        PAPER / "PROOF_NUMERICAL_SCALE_AUDIT.md",
        PAPER / "PROOF_NUMERICAL_SCALE_AUDIT.json",
        PAPER / "PROOF_SOLVER_SCALE_AUDIT.md",
        PAPER / "PROOF_SOLVER_SCALE_AUDIT.json",
        PAPER / "PROOF_SOLVER_SCALED_TOLERANCE_PROBE.md",
        PAPER / "PROOF_SOLVER_SCALED_TOLERANCE_PROBE.json",
        PAPER / "PROOF_SOLVER_SCALED_TOLERANCE_PROBE.csv",
        PAPER / "PROOF_SOLVER_SCALED_TOLERANCE_TRAJECTORY_PROBE.md",
        PAPER / "PROOF_SOLVER_SCALED_TOLERANCE_TRAJECTORY_PROBE.json",
        PAPER / "PROOF_SOLVER_SCALED_TOLERANCE_TRAJECTORY_PROBE.csv",
        PAPER / "PROOF_SOLVER_TOLERANCE_REGIME_SWEEP.md",
        PAPER / "PROOF_SOLVER_TOLERANCE_REGIME_SWEEP.json",
        PAPER / "PROOF_SOLVER_TOLERANCE_REGIME_SWEEP.csv",
        PAPER / "ORDER_ACCEPTANCE_GATE.md",
        PAPER / "ORDER_ACCEPTANCE_GATE.json",
        PAPER / "IMPLEMENTATION_FIDELITY_CERTIFICATE.md",
        PAPER / "IMPLEMENTATION_PATH_AUDIT.md",
        PAPER / "IMPLEMENTATION_PATH_AUDIT.json",
        PAPER / "validate_kinematic_row_defect_certificate.py",
        PAPER / "validate_cmame_submission.py",
        PAPER / "validate_cmame_submission_integrity_audit.py",
        PAPER / "validate_reference_metadata_audit.py",
        PAPER / "validate_cmame_blocker_closure_gate.py",
        PAPER / "validate_cmame_external_baseline_gate.py",
        PAPER / "validate_cmame_proof_contract_gate.py",
        PAPER / "validate_cmame_visual_legibility_audit.py",
        PAPER / "validate_cmame_figure_set_audit.py",
        PAPER / "validate_cmame_scalability_boundary_audit.py",
        PAPER / "validate_cmame_related_work_audit.py",
        PAPER / "validate_cmame_prose_residue_audit.py",
        PAPER / "validate_cmame_proof_style_audit.py",
        PAPER / "validate_proof_closure_manifest.py",
        PAPER / "validate_proof_claim_traceability_audit.py",
        PAPER / "build_exact_stage_identity_gate.py",
        PAPER / "validate_exact_stage_identity_gate.py",
        PAPER / "EXACT_STAGE_IDENTITY_GATE.md",
        PAPER / "EXACT_STAGE_IDENTITY_GATE.json",
        PAPER / "run_exact_stage_identity_numerical_check.py",
        PAPER / "validate_exact_stage_identity_numerical_check.py",
        PAPER / "EXACT_STAGE_IDENTITY_NUMERICAL_CHECK.md",
        PAPER / "EXACT_STAGE_IDENTITY_NUMERICAL_CHECK.json",
        PAPER / "EXACT_STAGE_IDENTITY_NUMERICAL_CHECK.csv",
        PAPER / "run_p2_constants_numerical_check.py",
        PAPER / "validate_p2_constants_numerical_check.py",
        PAPER / "P2_CONSTANTS_NUMERICAL_CHECK.md",
        PAPER / "P2_CONSTANTS_NUMERICAL_CHECK.json",
        PAPER / "P2_CONSTANTS_NUMERICAL_CHECK.csv",
        PAPER / "build_arxiv_version.py",
        PAPER / "validate_arxiv_version.py",
        PAPER / "arxiv" / "main_arxiv.tex",
        PAPER / "arxiv" / "main_arxiv.pdf",
        PAPER / "arxiv" / "README.md",
        PAPER / "arxiv" / "arxiv_submission.zip",
        PAPER / "arxiv" / "ARXIV_VERSION.json",
        PAPER / "lean" / "lakefile.toml",
        PAPER / "lean" / "lean-toolchain",
        PAPER / "lean" / "scripts" / "Axioms.lean",
        PAPER / "validate_d5_dynamic_defect_readiness_audit.py",
        PAPER / "validate_d5_dynamic_direct_substitution_certificate.py",
        PAPER / "validate_d5_taylor_term_budget_audit.py",
        PAPER / "validate_d5_primitive_bound_reduction_audit.py",
        PAPER / "validate_d5_p_tube_constants_audit.py",
        PAPER / "validate_d5_p_state_lift_gap_audit.py",
        PAPER / "validate_d5_p_state_map_definition_audit.py",
        PAPER / "validate_d5_p_state_anticircularity_audit.py",
        PAPER / "validate_d5_p_state_ps2_weighted_target_audit.py",
        PAPER / "validate_d5_p_state_ps2_kinematic_block_certificate.py",
        PAPER / "validate_d5_p_state_ps2_lie_chart_binding_audit.py",
        PAPER / "validate_d5_p_state_ps2_row_injection_audit.py",
        PAPER / "validate_d5_p_state_ps2_nonlinear_binding_audit.py",
        PAPER / "validate_d5_p_state_ps2_aggregate_promotion_audit.py",
        PAPER / "validate_d5_p_state_ps2_linearization_probe.py",
        PAPER / "validate_d5_p_state_ps3_conditional_conversion_audit.py",
        PAPER / "validate_d5_p_state_ps3_actual_instantiation_gap_audit.py",
        PAPER / "validate_d5_p_state_ps3_h_acc_input_obstruction_audit.py",
        PAPER / "validate_d5_p_state_ps3_full_residual_route_certificate.py",
        PAPER / "validate_d5_p_acc_map_definition_audit.py",
        PAPER / "validate_d5_p_acc_row_binding_audit.py",
        PAPER / "validate_d5_p_acc_independence_audit.py",
        PAPER / "validate_d5_p_acc_lift_obstruction_audit.py",
        PAPER / "validate_d5_p_geom_chart_reduction_audit.py",
        PAPER / "validate_d5_p_gyro_bilinear_reduction_audit.py",
        PAPER / "validate_d5_open_primitive_gap_audit.py",
        PAPER / "validate_d5_primitive_obligation_closure_plan.py",
        PAPER / "validate_d5_conditional_taylor_certificate.py",
        PAPER / "validate_all_examples_result_sanity_audit.py",
        PAPER / "validate_common_reference_order_recomputation_audit.py",
        PAPER / "validate_external_baseline_source_policy_diagnosis.py",
        PAPER / "validate_source_policy_closure_triage.py",
        PAPER / "validate_source_policy_row_closure_ledger.py",
        PAPER / "validate_all_examples_source_policy_audit.py",
        PAPER / "validate_external_suite_disposition_audit.py",
        PAPER / "validate_external_source_policy_closure_manifest.py",
        PAPER / "validate_external_case_evidence_reconciliation.py",
        PAPER / "validate_vp2024_code_path_disposition_audit.py",
        PAPER / "B2_SOURCE_POLICY_REMAINING_WORK_MANIFEST.md",
        PAPER / "B2_SOURCE_POLICY_REMAINING_WORK_MANIFEST.json",
        PAPER / "validate_b2_source_policy_remaining_work_manifest.py",
        PAPER / "EXTERNAL_SUPERIORITY_CLAIM_DEMOTION_AUDIT.md",
        PAPER / "EXTERNAL_SUPERIORITY_CLAIM_DEMOTION_AUDIT.json",
        PAPER / "build_external_superiority_claim_demotion_audit.py",
        PAPER / "validate_external_superiority_claim_demotion_audit.py",
        PAPER / "B4_B7_NON_SUPERIORITY_ROUTE_AUDIT.md",
        PAPER / "B4_B7_NON_SUPERIORITY_ROUTE_AUDIT.json",
        PAPER / "build_b4_b7_non_superiority_route_audit.py",
        PAPER / "validate_b4_b7_non_superiority_route_audit.py",
        PAPER / "B4_EXISTING_ARTIFACT_PROMOTION_AUDIT.md",
        PAPER / "B4_EXISTING_ARTIFACT_PROMOTION_AUDIT.json",
        PAPER / "build_b4_existing_artifact_promotion_audit.py",
        PAPER / "validate_b4_existing_artifact_promotion_audit.py",
        PAPER / "B4_SOURCE_POLICY_POST_EXECUTION_AUDIT.md",
        PAPER / "B4_SOURCE_POLICY_POST_EXECUTION_AUDIT.json",
        PAPER / "build_b4_source_policy_post_execution_audit.py",
        PAPER / "validate_b4_source_policy_post_execution_audit.py",
        PAPER / "SOURCE_POLICY_PUBLIC_CODE_REFRESH_20260620.md",
        PAPER / "SOURCE_POLICY_PUBLIC_CODE_REFRESH_20260620.json",
        PAPER / "build_source_policy_public_code_refresh_20260620.py",
        PAPER / "validate_source_policy_public_code_refresh_20260620.py",
        PAPER / "SOURCE_POLICY_REOPEN_CONDITION_MONITOR_20260620.md",
        PAPER / "SOURCE_POLICY_REOPEN_CONDITION_MONITOR_20260620.json",
        PAPER / "build_source_policy_reopen_condition_monitor_20260620.py",
        PAPER / "validate_source_policy_reopen_condition_monitor_20260620.py",
        PAPER / "RA2021_DOUBLE_SOURCE_POLICY_LOW_ORDER_DIAGNOSIS.md",
        PAPER / "RA2021_DOUBLE_SOURCE_POLICY_LOW_ORDER_DIAGNOSIS.json",
        PAPER / "build_ra2021_double_source_policy_low_order_diagnosis.py",
        PAPER / "validate_ra2021_double_source_policy_low_order_diagnosis.py",
        PAPER / "HI2022_RA_HALF_DOUBLE_SOURCE_POLICY_FAILURE_DIAGNOSIS.md",
        PAPER / "HI2022_RA_HALF_DOUBLE_SOURCE_POLICY_FAILURE_DIAGNOSIS.json",
        PAPER / "build_hi2022_ra_half_double_source_policy_failure_diagnosis.py",
        PAPER / "validate_hi2022_ra_half_double_source_policy_failure_diagnosis.py",
        PAPER / "B4_SOURCE_POLICY_ROW_CLOSURE_READINESS_LEDGER.md",
        PAPER / "B4_SOURCE_POLICY_ROW_CLOSURE_READINESS_LEDGER.json",
        PAPER / "B4_SOURCE_POLICY_ROW_CLOSURE_READINESS_LEDGER.csv",
        PAPER / "build_b4_source_policy_row_closure_readiness_ledger.py",
        PAPER / "validate_b4_source_policy_row_closure_readiness_ledger.py",
        PAPER / "RA_HI_SOURCE_POLICY_OUTPUT_INVENTORY.md",
        PAPER / "RA_HI_SOURCE_POLICY_OUTPUT_INVENTORY.json",
        PAPER / "build_ra_hi_source_policy_output_inventory.py",
        PAPER / "validate_ra_hi_source_policy_output_inventory.py",
        PAPER / "RA_HI_SOURCE_POLICY_CLOSEOUT_CHECKLIST.md",
        PAPER / "RA_HI_SOURCE_POLICY_CLOSEOUT_CHECKLIST.json",
        PAPER / "build_ra_hi_source_policy_closeout_checklist.py",
        PAPER / "validate_ra_hi_source_policy_closeout_checklist.py",
        PAPER / "RA_HI_SOURCE_POLICY_PROMOTION_BLOCKER_MATRIX.md",
        PAPER / "RA_HI_SOURCE_POLICY_PROMOTION_BLOCKER_MATRIX.json",
        PAPER / "RA_HI_SOURCE_POLICY_PROMOTION_BLOCKER_MATRIX.csv",
        PAPER / "build_ra_hi_source_policy_promotion_blocker_matrix.py",
        PAPER / "validate_ra_hi_source_policy_promotion_blocker_matrix.py",
        PAPER / "RA_HI_SOURCE_POLICY_POST_EXECUTION_ATTEMPT_CERTIFICATE.md",
        PAPER / "RA_HI_SOURCE_POLICY_POST_EXECUTION_ATTEMPT_CERTIFICATE.json",
        PAPER / "build_ra_hi_source_policy_post_execution_attempt_certificate.py",
        PAPER / "validate_ra_hi_source_policy_post_execution_attempt_certificate.py",
        PAPER / "B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.md",
        PAPER / "B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json",
        PAPER / "build_b4_source_policy_execution_opt_in_packet.py",
        PAPER / "validate_b4_source_policy_execution_opt_in_packet.py",
        PAPER / "run_b4_source_policy_after_opt_in.sh",
        PAPER / "validate_b4_source_policy_guarded_driver.py",
        PAPER / "B4_GUARDED_DRIVER_REFUSAL_BOUNDARY_AUDIT_20260621.md",
        PAPER / "B4_GUARDED_DRIVER_REFUSAL_BOUNDARY_AUDIT_20260621.json",
        PAPER / "build_b4_guarded_driver_refusal_boundary_audit_20260621.py",
        PAPER / "validate_b4_guarded_driver_refusal_boundary_audit_20260621.py",
        PAPER / "B4_SOURCE_POLICY_EXECUTION_HANDOFF_PACKAGE.md",
        PAPER / "B4_SOURCE_POLICY_EXECUTION_HANDOFF_PACKAGE.json",
        PAPER / "build_b4_source_policy_execution_handoff_package.py",
        PAPER / "validate_b4_source_policy_execution_handoff_package.py",
        PAPER / "B4_SOURCE_POLICY_COMMAND_PREFLIGHT_FREEZE_20260620.md",
        PAPER / "B4_SOURCE_POLICY_COMMAND_PREFLIGHT_FREEZE_20260620.json",
        PAPER / "build_b4_source_policy_command_preflight_freeze_20260620.py",
        PAPER / "validate_b4_source_policy_command_preflight_freeze_20260620.py",
        PAPER / "B4_SOURCE_POLICY_EXPECTED_OUTPUT_SCHEMA_AUDIT_20260620.md",
        PAPER / "B4_SOURCE_POLICY_EXPECTED_OUTPUT_SCHEMA_AUDIT_20260620.json",
        PAPER / "build_b4_source_policy_expected_output_schema_audit_20260620.py",
        PAPER / "validate_b4_source_policy_expected_output_schema_audit_20260620.py",
        PAPER / "B4_EXPECTED_OUTPUT_PROMOTION_READINESS_BLOCKER_AUDIT_20260620.md",
        PAPER / "B4_EXPECTED_OUTPUT_PROMOTION_READINESS_BLOCKER_AUDIT_20260620.json",
        PAPER / "build_b4_expected_output_promotion_readiness_blocker_audit_20260620.py",
        PAPER / "validate_b4_expected_output_promotion_readiness_blocker_audit_20260620.py",
        PAPER / "OC6_SOURCE_EQUIVALENT_REOPEN_READINESS_AUDIT_20260620.md",
        PAPER / "OC6_SOURCE_EQUIVALENT_REOPEN_READINESS_AUDIT_20260620.json",
        PAPER / "build_oc6_source_equivalent_reopen_readiness_audit_20260620.py",
        PAPER / "validate_oc6_source_equivalent_reopen_readiness_audit_20260620.py",
        PAPER / "FULL_SOURCE_POLICY_ROW_PROVENANCE_AUDIT.md",
        PAPER / "FULL_SOURCE_POLICY_ROW_PROVENANCE_AUDIT.json",
        PAPER / "FULL_SOURCE_POLICY_ROW_PROVENANCE_AUDIT.csv",
        PAPER / "build_full_source_policy_row_provenance_audit.py",
        PAPER / "validate_full_source_policy_row_provenance_audit.py",
        PAPER / "RA2021_SOURCE_POLICY_ROW_AUDIT.md",
        PAPER / "RA2021_SOURCE_POLICY_ROW_AUDIT.json",
        PAPER / "validate_ra2021_source_policy_row_audit.py",
        PAPER / "RA2021_SOURCE_IDENTITY_AUDIT.md",
        PAPER / "RA2021_SOURCE_IDENTITY_AUDIT.json",
        PAPER / "build_ra2021_source_identity_audit.py",
        PAPER / "validate_ra2021_source_identity_audit.py",
        PAPER / "HI2022_POLICY_DECISION_AUDIT.md",
        PAPER / "HI2022_POLICY_DECISION_AUDIT.json",
        PAPER / "validate_hi2022_policy_decision_audit.py",
        PAPER / "HI2022_SOURCE_POLICY_ROW_AUDIT.md",
        PAPER / "HI2022_SOURCE_POLICY_ROW_AUDIT.json",
        PAPER / "validate_hi2022_source_policy_row_audit.py",
        PAPER / "HI2022_T8_TOLERANCE_REPAIR_AUDIT.md",
        PAPER / "HI2022_T8_TOLERANCE_REPAIR_AUDIT.json",
        PAPER / "build_hi2022_t8_tolerance_repair_audit.py",
        PAPER / "validate_hi2022_t8_tolerance_repair_audit.py",
        PAPER / "validate_tfe_source_policy_spec.py",
        PAPER / "validate_tfe_source_policy_row_audit.py",
        PAPER / "validate_tfe_b4_b7_source_policy_demotion_audit.py",
        PAPER / "validate_tfe_source_pendulum_model_audit.py",
        PAPER / "validate_tfe_brown_mcphee_source_law_boundary_audit.py",
        PAPER / "validate_tfe_brown_mcphee_source_code_equivalence_certificate.py",
        PAPER / "validate_tfe_dae_runner_contract_gap_audit.py",
        PAPER / "validate_tfe_full_t10_absolute_dae_lift_summary.py",
        PAPER / "validate_tfe_source_grid_compatibility_audit.py",
        PAPER / "validate_tfe_endpoint_policy_boundary_certificate.py",
        PAPER / "validate_tfe_endpoint_policy_sensitivity_audit.py",
        PAPER / "validate_tfe_full_t10_endpoint_policy_closure_certificate.py",
        PAPER / "validate_objective_completion_audit.py",
        PAPER / "validate_comparison_objective_closure_reconciliation_audit.py",
        PAPER / "validate_paper_numerical_result_matrix.py",
        PAPER / "validate_four_example_source_policy_dashboard.py",
        PAPER / "validate_result_to_manuscript_traceability_audit.py",
        PAPER / "validate_all_method_example_claim_disposition_audit.py",
        PAPER / "validate_cmame_review_agent.py",
        PAPER / "validate_cmame_reproducibility_package_manifest.py",
        PAPER / "build_cmame_reproducibility_package_manifest.py",
        PAPER / "sync_submission_artifact_manifest_boundary.py",
        PAPER / "validate_submission_artifact_manifest_boundary_sync.py",
        PAPER / "validate_dynamic_row_oracle_gate.py",
        PAPER / "validate_concise_paper.py",
        PAPER / "validate_paper_claims.py",
        PAPER / "validate_proof_evidence_matrix.py",
        PAPER / "validate_proof_numerical_scale_audit.py",
        PAPER / "validate_proof_solver_scale_audit.py",
        PAPER / "validate_proof_solver_scaled_tolerance_probe.py",
        PAPER / "validate_proof_solver_scaled_tolerance_trajectory_probe.py",
        PAPER / "validate_proof_solver_tolerance_regime_sweep.py",
        PAPER / "validate_order_acceptance_gate.py",
        PAPER / "validate_implementation_fidelity_certificate.py",
        PAPER / "validate_implementation_path_audit.py",
        PAPER / "validate_newton_euler_defect_obligation_gate.py",
        PAPER / "validate_source_paper_comparison.py",
        PAPER / "validate_cross_paper_benchmark_spec.py",
        PAPER / "validate_cross_paper_benchmark_cases.py",
        PAPER / "validate_external_same_test_run_queue.py",
        PAPER / "validate_submission_bundle.py",
        PAPER / "validate_paper_package.py",
        ROOT / "CURRENT_PIPELINE_CONTRACT.md",
    ]
    missing = [path.name for path in required_files if not path.exists() or path.stat().st_size <= 0]

    boundary_ok = False
    boundary_error = ""
    contract_ok = False
    contract_error = ""
    submission_manifest_ok = False
    submission_manifest_error = ""
    submission_packet_ok = False
    submission_packet_error = ""
    cover_letter_ok = False
    cover_letter_error = ""
    file_inventory_ok = False
    file_inventory_error = ""
    review_response_ok = False
    review_response_error = ""
    boundary_docs_ok = False
    boundary_docs_error = ""
    boundary_path = PAPER / "CLAIM_BOUNDARY.json"
    if boundary_path.exists():
        try:
            boundary = json.loads(boundary_path.read_text())
            asme_acceptance = boundary.get("asme_acceptance", {})
            full_tfe_gap = boundary.get("full_tfe_gap_contract", {})
            gap_compression = full_tfe_gap.get("velocity_compression_blocker", {})
            caveat_contracts = boundary.get("remaining_caveat_contracts", {})
            sparse_contract = caveat_contracts.get("sparse_speed_quantified", {})
            sharp_contract = caveat_contracts.get("sharp_friction_coarse_order_reduction_ultra_recovered", {})
            terminology = boundary.get("terminology", {})
            full_tfe_term = terminology.get("full_tfe_replacement", {})
            order_conventions = boundary.get("order_conventions", {})
            observed_orders = order_conventions.get("observed_smooth_projected_orders", {})
            paper_order_target = order_conventions.get("local_paper_style_tfe_formula_target", {})
            boundary_ok = (
                boundary.get("schema") == "v047-paper-claim-boundary-v1"
                and boundary.get("primary_claim", {}).get("accepted_method") == "Gauss6/FullVA"
                and boundary.get("primary_claim", {}).get("accepted_examples_role")
                == "mechanism_coverage_examples_not_all_dynamic_order"
                and set(boundary.get("primary_claim", {}).get("accepted_dynamic_order_examples", []))
                == {"single_pendulum", "double_pendulum"}
                and set(boundary.get("primary_claim", {}).get("accepted_mechanism_coverage_examples", []))
                == {"single_pendulum", "double_pendulum", "four_link", "slider_crank"}
                and set(boundary.get("primary_claim", {}).get("coverage_only_dynamic_order_examples", []))
                == {"four_link", "slider_crank"}
                and boundary.get("full_tfe_stage_replacement") is False
                and asme_acceptance.get("status") == "four_asme_method_rows_accepted_projection_sharp_sparse_caveats"
                and asme_acceptance.get("full_tfe_required_for_gate") is False
                and asme_acceptance.get("accepted_examples_role")
                == "mechanism_coverage_examples_not_all_dynamic_order"
                and set(asme_acceptance.get("accepted_dynamic_order_examples", []))
                == {"single_pendulum", "double_pendulum"}
                and set(asme_acceptance.get("accepted_mechanism_coverage_examples", []))
                == {"single_pendulum", "double_pendulum", "four_link", "slider_crank"}
                and set(asme_acceptance.get("coverage_only_dynamic_order_examples", []))
                == {"four_link", "slider_crank"}
                and asme_acceptance.get("single_pendulum", {}).get("absolute_fullva_min_order") == 6.024
                and asme_acceptance.get("double_pendulum", {}).get("method_min_order") == 6.089
                and asme_acceptance.get("four_link", {}).get("max_dynamics_residual_norm") == 1.338e-13
                and asme_acceptance.get("slider_crank", {}).get("max_dynamics_residual_norm") == 6.492e-15
                and full_tfe_gap.get("status") == "full_stage_acceptance_gap_quantified_not_full_tfe"
                and full_tfe_gap.get("full_tfe_stage_replacement") is False
                and full_tfe_gap.get("stage_row_budget") == 132
                and full_tfe_gap.get("derived_full_tfe_stage_functional_present") is False
                and full_tfe_gap.get("endpoint_boundary_source_removed") is False
                and full_tfe_gap.get("max_acceptance_missing_count") == 3
                and full_tfe_gap.get("closure_acceptance_matrix", {}).get("accepted_candidate_count") == 0
                and gap_compression.get("row_space_compression_rows") == 36
                and gap_compression.get("row_space_spans") == 0
                and sparse_contract.get("status") == "speed_gap_quantified_dense_still_faster"
                and sparse_contract.get("dense_beats_row") is True
                and sparse_contract.get("row_colors") == 60
                and sparse_contract.get("column_colors") == 90
                and sharp_contract.get("ultra_status") == "ultra_high_order_recovered"
                and sharp_contract.get("practical_cost_caveat") is True
                and sharp_contract.get("cost_status") == "sharp_refinement_cost_quantified_ultra_high_order_cost_caveat"
                and terminology.get("tfe") == "temporal finite element"
                and terminology.get("fte") == "typo_for_tfe_not_a_separate_method"
                and full_tfe_term.get("accepted") is False
                and order_conventions.get("accepted_method") == "Gauss6/FullVA"
                and order_conventions.get("accepted_method_order") == 6
                and observed_orders.get("position") == 7.161
                and observed_orders.get("velocity") == 7.066
                and paper_order_target.get("expected_order") == 5
                and paper_order_target.get("role") == "comparator_not_accepted_method"
                and boundary.get("evidence_files", {}).get("current_pipeline_contract") == "CURRENT_PIPELINE_CONTRACT.md"
                and boundary.get("evidence_files", {}).get("order_acceptance_gate")
                == "paper_v047_cylindrical_chain/ORDER_ACCEPTANCE_GATE.md"
                and boundary.get("evidence_files", {}).get("order_acceptance_gate_json")
                == "paper_v047_cylindrical_chain/ORDER_ACCEPTANCE_GATE.json"
                and "validate_order_acceptance_gate.py" in boundary.get("read_only_validators", [])
                and boundary.get("full_generator", {}).get("required_for_paper_claim_check") is False
            )
            if not boundary_ok:
                boundary_error = "CLAIM_BOUNDARY.json has unexpected claim-boundary values"
        except Exception as exc:  # noqa: BLE001 - command-line wrapper reports parse failures.
            boundary_error = f"CLAIM_BOUNDARY.json parse failed: {exc}"

    contract_path = ROOT / "CURRENT_PIPELINE_CONTRACT.md"
    if contract_path.exists():
        contract_text = contract_path.read_text(encoding="utf-8", errors="replace")
        contract_ok = all(
            contains_normalized(contract_text, token)
            for token in [
                "Current Pipeline Contract",
                "`research-pipeline`",
                "process guard",
                "current files in this repository are authoritative",
                "conditional formal-order comparison",
                "not an implemented source-paper superiority claim",
                "not a complete source-paper residual reproduction claim",
                "`Gauss6/FullVA`",
                "`7.161/7.066`",
                "`m=3` Gauss-Lobatto TFE target",
                "expected order `5`",
                "`single_pendulum`",
                "`double_pendulum`",
                "`four_link`",
                "`slider_crank`",
                "four_asme_method_rows_accepted_projection_sharp_sparse_caveats",
                "`sparse_speed_quantified`",
                "`full_tfe_stage_replacement_missing`",
                "`sharp_friction_coarse_order_reduction_ultra_recovered`",
                "`full_tfe_stage_replacement=false`",
                ".venv_sbel/bin/python validate_pipeline_outputs.py",
                "../.venv_sbel/bin/python validate_proof_evidence_matrix.py",
                "../.venv_sbel/bin/python validate_source_paper_comparison.py",
                "../.venv_sbel/bin/python validate_cross_paper_benchmark_spec.py",
                "../.venv_sbel/bin/python validate_cross_paper_benchmark_cases.py",
                "../.venv_sbel/bin/python validate_submission_bundle.py",
                "../.venv_sbel/bin/python validate_cmame_submission.py",
                "../.venv_sbel/bin/python validate_paper_package.py",
                "../.venv_sbel/bin/python validate_implementation_fidelity_certificate.py",
                "../.venv_sbel/bin/python validate_four_asme_minimal.py",
                "../.venv_sbel/bin/python validate_full_tfe_gap.py",
                "../.venv_sbel/bin/python validate_full_tfe_repair_spec.py",
                "../.venv_sbel/bin/python validate_v047_outputs.py",
                "Do not run `v047_cylindrical_chain_pipeline/run_v047.py`",
                "Paper Quality Status",
                "`submission_ready=false`",
                "`mechanical_preflight_passed=true`",
                "`quality_review_passed=false`",
                "CMAME_SUBMISSION_READINESS_REVIEW.md",
                "CMAME_BLOCKER_CLOSURE_GATE.md",
                "CMAME_BLOCKER_CLOSURE_GATE.json",
                "CMAME_EXTERNAL_BASELINE_GATE.md",
                "CMAME_EXTERNAL_BASELINE_GATE.json",
                "../.venv_sbel/bin/python validate_cmame_external_baseline_gate.py",
                "external_superiority_claim=false",
                "CMAME_PROOF_CONTRACT_GATE.md",
                "CMAME_PROOF_CONTRACT_GATE.json",
                "../.venv_sbel/bin/python validate_cmame_proof_contract_gate.py",
                "eta_h^tube <= c_eta h^7",
                "DYNAMIC_ROW_ORACLE_GATE.md",
                "DYNAMIC_ROW_ORACLE_GATE.json",
                "FULL_SOURCE_POLICY_RUNNER_ARCHIVE_GAP_AUDIT.md",
                "validate_full_source_policy_runner_archive_gap_audit.py",
                "../.venv_sbel/bin/python validate_full_source_policy_runner_archive_gap_audit.py",
                "full_archive_ready_now=False",
                "source-policy rows remain `0/40`",
                "current narrowed archive boundary matches the reproducibility manifest",
                "`narrowed_archive_ready_not_full_source_policy_runner_archive/0/40/False/False/True`",
                "`OC4=open,OC6=partial,OC12=partial`",
                "`narrowed_claim_only`, not a full source-policy runner archive",
                "paper_v047_cylindrical_chain/OBJECTIVE_COMPLETION_AUDIT.md",
                "paper_v047_cylindrical_chain/OBJECTIVE_COMPLETION_AUDIT.json",
                "blocker_open_by_id=OC4:True,OC6:True,OC12:True",
                "blocker_closure_decision_by_id=OC4:remain_open_ready_for_authorized_execution_not_executed_not_promoted,OC6:remain_open_no_positive_source_equivalent_artifact,OC12:remain_partial_narrowed_replay_ready_full_source_policy_archive_not_ready",
                "blocker_closure_allowed_by_id=OC4:False,OC6:False,OC12:False",
                "contract-level guard against treating validator PASS or the narrowed archive as global submission readiness",
                "TFE_SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_CERTIFICATE.md",
                "validate_tfe_source_policy_self_reproduction_attempt_certificate.py",
                "../.venv_sbel/bin/python validate_tfe_source_policy_self_reproduction_attempt_certificate.py",
                "attempted_not_reproducible_rows=16/16",
                "source_policy_closed_rows=0",
                "RA_HI_SOURCE_POLICY_CLOSEOUT_CHECKLIST.md",
                "RA_HI_SOURCE_POLICY_PROMOTION_BLOCKER_MATRIX.md",
                "RA_HI_SOURCE_POLICY_POST_EXECUTION_ATTEMPT_CERTIFICATE.md",
                "validate_ra_hi_source_policy_closeout_checklist.py",
                "../.venv_sbel/bin/python validate_ra_hi_source_policy_closeout_checklist.py",
                "source_policy_closed=0/20",
                "validate_ra_hi_source_policy_promotion_blocker_matrix.py",
                "../.venv_sbel/bin/python validate_ra_hi_source_policy_promotion_blocker_matrix.py",
                "not_promoted=20",
                "validate_ra_hi_source_policy_post_execution_attempt_certificate.py",
                "source_policy_rows_promoted=0",
                "default_1e-4_required=false",
                "CROSS_PAPER_BENCHMARK_CASES.json",
                "KISSEL_NEGRUT_CODE_INVENTORY.md",
                "IMPLEMENTATION_FIDELITY_CERTIFICATE.md",
                "position/velocity orders `7.951/7.042`",
                "32 completed and 0 partial rows",
                "Next Real Research Gate",
                "multi-paper Kissel/Negrut code inventory",
                "Kissel/Bakke/Negrut velocity-partitioning",
                "code-path-resolution gate",
                "source-free",
                "projection-free",
                "non-terminal-row-replacement",
                "132-row Newton system full rank",
            ]
        )
        if not contract_ok:
            contract_error = "CURRENT_PIPELINE_CONTRACT.md has unexpected current-pipeline boundary values"

    manifest_path = PAPER / "SUBMISSION_ARTIFACT_MANIFEST.json"
    if manifest_path.exists():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            objective_completion = json.loads((PAPER / "OBJECTIVE_COMPLETION_AUDIT.json").read_text(encoding="utf-8"))
            full_source_runner_gap = json.loads(
                (PAPER / "FULL_SOURCE_POLICY_RUNNER_ARCHIVE_GAP_AUDIT.json").read_text(encoding="utf-8")
            )
            reproducibility_manifest = json.loads(
                (PAPER / "CMAME_REPRODUCIBILITY_PACKAGE_MANIFEST.json").read_text(encoding="utf-8")
            )
            claim = manifest.get("accepted_claim", {})
            comparator = claim.get("comparator", {})
            objective_summary = objective_completion.get("summary", {})
            manifest_archive_action_boundary = manifest.get("full_source_policy_runner_archive_gap_action_boundary") or {}
            manifest_narrowed_archive_boundary = manifest.get("narrowed_archive_boundary") or {}
            reproducibility_narrowed_archive_boundary = (
                reproducibility_manifest.get("narrowed_archive_boundary") or {}
            )
            submission_manifest_ok = (
                manifest.get("schema") == "v047-submission-artifact-manifest-v1"
                and manifest.get("recommended_pdf") == "main_cmame.pdf"
                and manifest.get("cmame_tex") == "main_cmame.tex"
                and manifest.get("cmame_highlights") == "highlights_cmame.txt"
                and manifest.get("cmame_declarations") == "declarations_cmame.md"
                and manifest.get("cmame_checklist") == "CMAME_SUBMISSION_CHECKLIST.md"
                and manifest.get("cmame_readiness_audit") == "CMAME_SUBMISSION_READINESS_AUDIT.md"
                and manifest.get("cmame_readiness_review") == "CMAME_SUBMISSION_READINESS_REVIEW.md"
                and manifest.get("cmame_submission_integrity_audit") == "CMAME_SUBMISSION_INTEGRITY_AUDIT.md"
                and manifest.get("cmame_submission_integrity_audit_json") == "CMAME_SUBMISSION_INTEGRITY_AUDIT.json"
                and manifest.get("reference_metadata_audit") == "REFERENCE_METADATA_AUDIT.md"
                and manifest.get("reference_metadata_audit_json") == "REFERENCE_METADATA_AUDIT.json"
                and manifest.get("cmame_blocker_closure_gate") == "CMAME_BLOCKER_CLOSURE_GATE.md"
                and manifest.get("cmame_blocker_closure_gate_json") == "CMAME_BLOCKER_CLOSURE_GATE.json"
                and manifest.get("cmame_external_baseline_gate") == "CMAME_EXTERNAL_BASELINE_GATE.md"
                and manifest.get("cmame_external_baseline_gate_json") == "CMAME_EXTERNAL_BASELINE_GATE.json"
                and manifest.get("cmame_proof_contract_gate") == "CMAME_PROOF_CONTRACT_GATE.md"
                and manifest.get("cmame_proof_contract_gate_json") == "CMAME_PROOF_CONTRACT_GATE.json"
                and manifest.get("cmame_visual_legibility_audit") == "CMAME_VISUAL_LEGIBILITY_AUDIT.md"
                and manifest.get("cmame_visual_legibility_audit_json") == "CMAME_VISUAL_LEGIBILITY_AUDIT.json"
                and manifest.get("cmame_figure_set_audit") == "CMAME_FIGURE_SET_AUDIT.md"
                and manifest.get("cmame_figure_set_audit_json") == "CMAME_FIGURE_SET_AUDIT.json"
                and manifest.get("cmame_scalability_boundary_audit")
                == "CMAME_SCALABILITY_BOUNDARY_AUDIT.md"
                and manifest.get("cmame_scalability_boundary_audit_json")
                == "CMAME_SCALABILITY_BOUNDARY_AUDIT.json"
                and manifest.get("cmame_related_work_audit") == "CMAME_RELATED_WORK_AUDIT.md"
                and manifest.get("cmame_related_work_audit_json") == "CMAME_RELATED_WORK_AUDIT.json"
                and manifest.get("cmame_prose_residue_audit") == "CMAME_PROSE_RESIDUE_AUDIT.md"
                and manifest.get("cmame_prose_residue_audit_json") == "CMAME_PROSE_RESIDUE_AUDIT.json"
                and manifest.get("cmame_claim_hygiene_audit") == "CMAME_CLAIM_HYGIENE_AUDIT.md"
                and manifest.get("cmame_claim_hygiene_audit_json") == "CMAME_CLAIM_HYGIENE_AUDIT.json"
                and manifest.get("cmame_proof_style_audit") == "CMAME_PROOF_STYLE_AUDIT.md"
                and manifest.get("cmame_proof_style_audit_json") == "CMAME_PROOF_STYLE_AUDIT.json"
                and manifest.get("cmame_strict_proof_audit") == "CMAME_STRICT_PROOF_AUDIT.md"
                and manifest.get("cmame_strict_proof_audit_json") == "CMAME_STRICT_PROOF_AUDIT.json"
                and manifest.get("cmame_strict_proof_policy_reconciliation_audit")
                == "CMAME_STRICT_PROOF_POLICY_RECONCILIATION_AUDIT.md"
                and manifest.get("cmame_strict_proof_policy_reconciliation_audit_json")
                == "CMAME_STRICT_PROOF_POLICY_RECONCILIATION_AUDIT.json"
                and manifest.get("proof_closure_manifest") == "PROOF_CLOSURE_MANIFEST.md"
                and manifest.get("proof_closure_manifest_json") == "PROOF_CLOSURE_MANIFEST.json"
                and manifest.get("proof_claim_traceability_audit") == "PROOF_CLAIM_TRACEABILITY_AUDIT.md"
                and manifest.get("proof_claim_traceability_audit_json") == "PROOF_CLAIM_TRACEABILITY_AUDIT.json"
                and manifest.get("d5_dynamic_defect_readiness_audit") == "D5_DYNAMIC_DEFECT_READINESS_AUDIT.md"
                and manifest.get("d5_dynamic_defect_readiness_audit_json") == "D5_DYNAMIC_DEFECT_READINESS_AUDIT.json"
                and manifest.get("d5_dynamic_direct_substitution_certificate")
                == "D5_DYNAMIC_DIRECT_SUBSTITUTION_CERTIFICATE.md"
                and manifest.get("d5_dynamic_direct_substitution_certificate_json")
                == "D5_DYNAMIC_DIRECT_SUBSTITUTION_CERTIFICATE.json"
                and manifest.get("d5_taylor_term_budget_audit") == "D5_TAYLOR_TERM_BUDGET_AUDIT.md"
                and manifest.get("d5_taylor_term_budget_audit_json") == "D5_TAYLOR_TERM_BUDGET_AUDIT.json"
                and manifest.get("d5_primitive_bound_reduction_audit") == "D5_PRIMITIVE_BOUND_REDUCTION_AUDIT.md"
                and manifest.get("d5_primitive_bound_reduction_audit_json") == "D5_PRIMITIVE_BOUND_REDUCTION_AUDIT.json"
                and manifest.get("d5_p_tube_constants_audit") == "D5_P_TUBE_CONSTANTS_AUDIT.md"
                and manifest.get("d5_p_tube_constants_audit_json") == "D5_P_TUBE_CONSTANTS_AUDIT.json"
                and manifest.get("d5_p_state_lift_gap_audit") == "D5_P_STATE_LIFT_GAP_AUDIT.md"
                and manifest.get("d5_p_state_lift_gap_audit_json") == "D5_P_STATE_LIFT_GAP_AUDIT.json"
                and manifest.get("d5_p_state_map_definition_audit") == "D5_P_STATE_MAP_DEFINITION_AUDIT.md"
                and manifest.get("d5_p_state_map_definition_audit_json") == "D5_P_STATE_MAP_DEFINITION_AUDIT.json"
                and manifest.get("d5_p_state_anticircularity_audit") == "D5_P_STATE_ANTICIRCULARITY_AUDIT.md"
                and manifest.get("d5_p_state_anticircularity_audit_json") == "D5_P_STATE_ANTICIRCULARITY_AUDIT.json"
                and manifest.get("d5_p_state_ps2_weighted_target_audit") == "D5_P_STATE_PS2_WEIGHTED_TARGET_AUDIT.md"
                and manifest.get("d5_p_state_ps2_weighted_target_audit_json") == "D5_P_STATE_PS2_WEIGHTED_TARGET_AUDIT.json"
                and manifest.get("d5_p_state_ps2_kinematic_block_certificate")
                == "D5_P_STATE_PS2_KINEMATIC_BLOCK_CERTIFICATE.md"
                and manifest.get("d5_p_state_ps2_kinematic_block_certificate_json")
                == "D5_P_STATE_PS2_KINEMATIC_BLOCK_CERTIFICATE.json"
                and manifest.get("d5_p_state_ps2_lie_chart_binding_audit")
                == "D5_P_STATE_PS2_LIE_CHART_BINDING_AUDIT.md"
                and manifest.get("d5_p_state_ps2_lie_chart_binding_audit_json")
                == "D5_P_STATE_PS2_LIE_CHART_BINDING_AUDIT.json"
                and manifest.get("d5_p_state_ps2_row_injection_audit")
                == "D5_P_STATE_PS2_ROW_INJECTION_AUDIT.md"
                and manifest.get("d5_p_state_ps2_row_injection_audit_json")
                == "D5_P_STATE_PS2_ROW_INJECTION_AUDIT.json"
                and manifest.get("d5_p_state_ps2_nonlinear_binding_audit")
                == "D5_P_STATE_PS2_NONLINEAR_BINDING_AUDIT.md"
                and manifest.get("d5_p_state_ps2_nonlinear_binding_audit_json")
                == "D5_P_STATE_PS2_NONLINEAR_BINDING_AUDIT.json"
                and manifest.get("d5_p_state_ps2_aggregate_promotion_audit")
                == "D5_P_STATE_PS2_AGGREGATE_PROMOTION_AUDIT.md"
                and manifest.get("d5_p_state_ps2_aggregate_promotion_audit_json")
                == "D5_P_STATE_PS2_AGGREGATE_PROMOTION_AUDIT.json"
                and manifest.get("d5_p_state_ps2_linearization_probe") == "D5_P_STATE_PS2_LINEARIZATION_PROBE.md"
                and manifest.get("d5_p_state_ps2_linearization_probe_json") == "D5_P_STATE_PS2_LINEARIZATION_PROBE.json"
                and manifest.get("d5_p_state_ps2_linearization_probe_csv") == "D5_P_STATE_PS2_LINEARIZATION_PROBE.csv"
                and manifest.get("d5_p_state_ps3_conditional_conversion_audit") == "D5_P_STATE_PS3_CONDITIONAL_CONVERSION_AUDIT.md"
                and manifest.get("d5_p_state_ps3_conditional_conversion_audit_json") == "D5_P_STATE_PS3_CONDITIONAL_CONVERSION_AUDIT.json"
                and manifest.get("d5_p_state_ps3_actual_instantiation_gap_audit") == "D5_P_STATE_PS3_ACTUAL_INSTANTIATION_GAP_AUDIT.md"
                and manifest.get("d5_p_state_ps3_actual_instantiation_gap_audit_json") == "D5_P_STATE_PS3_ACTUAL_INSTANTIATION_GAP_AUDIT.json"
                and manifest.get("d5_p_state_ps3_h_acc_input_obstruction_audit") == "D5_P_STATE_PS3_H_ACC_INPUT_OBSTRUCTION_AUDIT.md"
                and manifest.get("d5_p_state_ps3_h_acc_input_obstruction_audit_json") == "D5_P_STATE_PS3_H_ACC_INPUT_OBSTRUCTION_AUDIT.json"
                and manifest.get("d5_p_acc_map_definition_audit") == "D5_P_ACC_MAP_DEFINITION_AUDIT.md"
                and manifest.get("d5_p_acc_map_definition_audit_json") == "D5_P_ACC_MAP_DEFINITION_AUDIT.json"
                and manifest.get("d5_p_acc_row_binding_audit") == "D5_P_ACC_ROW_BINDING_AUDIT.md"
                and manifest.get("d5_p_acc_row_binding_audit_json") == "D5_P_ACC_ROW_BINDING_AUDIT.json"
                and manifest.get("d5_p_acc_independence_audit") == "D5_P_ACC_INDEPENDENCE_AUDIT.md"
                and manifest.get("d5_p_acc_independence_audit_json") == "D5_P_ACC_INDEPENDENCE_AUDIT.json"
                and manifest.get("d5_p_acc_lift_obstruction_audit") == "D5_P_ACC_LIFT_OBSTRUCTION_AUDIT.md"
                and manifest.get("d5_p_acc_lift_obstruction_audit_json")
                == "D5_P_ACC_LIFT_OBSTRUCTION_AUDIT.json"
                and manifest.get("d5_p_acc_pa2_weighted_inverse_audit")
                == "D5_P_ACC_PA2_WEIGHTED_INVERSE_AUDIT.md"
                and manifest.get("d5_p_acc_pa2_weighted_inverse_audit_json")
                == "D5_P_ACC_PA2_WEIGHTED_INVERSE_AUDIT.json"
                and manifest.get("d5_p_lambda_interface_audit") == "D5_P_LAMBDA_INTERFACE_AUDIT.md"
                and manifest.get("d5_p_lambda_interface_audit_json") == "D5_P_LAMBDA_INTERFACE_AUDIT.json"
                and manifest.get("d5_p_lambda_inf_sup_probe") == "D5_P_LAMBDA_INF_SUP_PROBE.md"
                and manifest.get("d5_p_lambda_inf_sup_probe_json") == "D5_P_LAMBDA_INF_SUP_PROBE.json"
                and manifest.get("d5_p_lambda_inf_sup_probe_csv") == "D5_P_LAMBDA_INF_SUP_PROBE.csv"
                and manifest.get("d5_p_lambda_pl2_geometric_margin_audit")
                == "D5_P_LAMBDA_PL2_GEOMETRIC_MARGIN_AUDIT.md"
                and manifest.get("d5_p_lambda_pl2_geometric_margin_audit_json")
                == "D5_P_LAMBDA_PL2_GEOMETRIC_MARGIN_AUDIT.json"
                and manifest.get("d5_p_lambda_d3_noncircularity_audit")
                == "D5_P_LAMBDA_D3_NONCIRCULARITY_AUDIT.md"
                and manifest.get("d5_p_lambda_d3_noncircularity_audit_json")
                == "D5_P_LAMBDA_D3_NONCIRCULARITY_AUDIT.json"
                and manifest.get("d5_p_lambda_pl4_rate_propagation_audit")
                == "D5_P_LAMBDA_PL4_RATE_PROPAGATION_AUDIT.md"
                and manifest.get("d5_p_lambda_pl4_rate_propagation_audit_json")
                == "D5_P_LAMBDA_PL4_RATE_PROPAGATION_AUDIT.json"
                and manifest.get("d5_p_geom_chart_reduction_audit") == "D5_P_GEOM_CHART_REDUCTION_AUDIT.md"
                and manifest.get("d5_p_geom_chart_reduction_audit_json") == "D5_P_GEOM_CHART_REDUCTION_AUDIT.json"
                and manifest.get("d5_p_gyro_bilinear_reduction_audit") == "D5_P_GYRO_BILINEAR_REDUCTION_AUDIT.md"
                and manifest.get("d5_p_gyro_bilinear_reduction_audit_json") == "D5_P_GYRO_BILINEAR_REDUCTION_AUDIT.json"
                and manifest.get("d5_open_primitive_gap_audit") == "D5_OPEN_PRIMITIVE_GAP_AUDIT.md"
                and manifest.get("d5_open_primitive_gap_audit_json") == "D5_OPEN_PRIMITIVE_GAP_AUDIT.json"
                and manifest.get("d5_primitive_obligation_closure_plan") == "D5_PRIMITIVE_OBLIGATION_CLOSURE_PLAN.md"
                and manifest.get("d5_primitive_obligation_closure_plan_json") == "D5_PRIMITIVE_OBLIGATION_CLOSURE_PLAN.json"
                and manifest.get("d5_conditional_taylor_certificate") == "D5_CONDITIONAL_TAYLOR_CERTIFICATE.md"
                and manifest.get("d5_conditional_taylor_certificate_json") == "D5_CONDITIONAL_TAYLOR_CERTIFICATE.json"
                and manifest.get("external_suite_disposition_audit") == "EXTERNAL_SUITE_DISPOSITION_AUDIT.md"
                and manifest.get("external_suite_disposition_audit_json") == "EXTERNAL_SUITE_DISPOSITION_AUDIT.json"
                and manifest.get("external_source_policy_closure_manifest")
                == "EXTERNAL_SOURCE_POLICY_CLOSURE_MANIFEST.md"
                and manifest.get("external_source_policy_closure_manifest_json")
                == "EXTERNAL_SOURCE_POLICY_CLOSURE_MANIFEST.json"
                and manifest.get("tfe_source_policy_spec") == "TFE_SOURCE_POLICY_SPEC.md"
                and manifest.get("tfe_source_policy_spec_json") == "TFE_SOURCE_POLICY_SPEC.json"
                and manifest.get("tfe_source_policy_row_audit") == "TFE_SOURCE_POLICY_ROW_AUDIT.md"
                and manifest.get("tfe_source_policy_row_audit_json") == "TFE_SOURCE_POLICY_ROW_AUDIT.json"
                and manifest.get("tfe_b4_b7_source_policy_demotion_audit")
                == "TFE_B4_B7_SOURCE_POLICY_DEMOTION_AUDIT.md"
                and manifest.get("tfe_b4_b7_source_policy_demotion_audit_json")
                == "TFE_B4_B7_SOURCE_POLICY_DEMOTION_AUDIT.json"
                and manifest.get("tfe_source_pendulum_model_audit") == "TFE_SOURCE_PENDULUM_MODEL_AUDIT.md"
                and manifest.get("tfe_source_pendulum_model_audit_json")
                == "TFE_SOURCE_PENDULUM_MODEL_AUDIT.json"
                and manifest.get("tfe_brown_mcphee_source_law_boundary_audit")
                == "TFE_BROWN_MCPHEE_SOURCE_LAW_BOUNDARY_AUDIT.md"
                and manifest.get("tfe_brown_mcphee_source_law_boundary_audit_json")
                == "TFE_BROWN_MCPHEE_SOURCE_LAW_BOUNDARY_AUDIT.json"
                and manifest.get("tfe_source_grid_compatibility_audit")
                == "TFE_SOURCE_GRID_COMPATIBILITY_AUDIT.md"
                and manifest.get("tfe_source_grid_compatibility_audit_json")
                == "TFE_SOURCE_GRID_COMPATIBILITY_AUDIT.json"
                and manifest.get("tfe_endpoint_policy_boundary_certificate")
                == "TFE_ENDPOINT_POLICY_BOUNDARY_CERTIFICATE.md"
                and manifest.get("tfe_endpoint_policy_boundary_certificate_json")
                == "TFE_ENDPOINT_POLICY_BOUNDARY_CERTIFICATE.json"
                and manifest.get("tfe_endpoint_policy_boundary_certificate_csv")
                == "TFE_ENDPOINT_POLICY_BOUNDARY_CERTIFICATE.csv"
                and manifest.get("tfe_endpoint_policy_sensitivity_audit")
                == "TFE_ENDPOINT_POLICY_SENSITIVITY_AUDIT.md"
                and manifest.get("tfe_endpoint_policy_sensitivity_audit_json")
                == "TFE_ENDPOINT_POLICY_SENSITIVITY_AUDIT.json"
                and manifest.get("tfe_endpoint_policy_sensitivity_audit_csv")
                == "TFE_ENDPOINT_POLICY_SENSITIVITY_AUDIT.csv"
                and manifest.get("objective_completion_audit") == "OBJECTIVE_COMPLETION_AUDIT.md"
                and manifest.get("objective_completion_audit_json") == "OBJECTIVE_COMPLETION_AUDIT.json"
                and manifest.get("comparison_objective_closure_reconciliation_audit")
                == "COMPARISON_OBJECTIVE_CLOSURE_RECONCILIATION_AUDIT.md"
                and manifest.get("comparison_objective_closure_reconciliation_audit_json")
                == "COMPARISON_OBJECTIVE_CLOSURE_RECONCILIATION_AUDIT.json"
                and manifest.get("proof_solver_scale_audit") == "PROOF_SOLVER_SCALE_AUDIT.md"
                and manifest.get("proof_solver_scale_audit_json") == "PROOF_SOLVER_SCALE_AUDIT.json"
                and manifest.get("proof_solver_scaled_tolerance_trajectory_probe")
                == "PROOF_SOLVER_SCALED_TOLERANCE_TRAJECTORY_PROBE.md"
                and manifest.get("proof_solver_scaled_tolerance_trajectory_probe_json")
                == "PROOF_SOLVER_SCALED_TOLERANCE_TRAJECTORY_PROBE.json"
                and manifest.get("proof_solver_scaled_tolerance_trajectory_probe_csv")
                == "PROOF_SOLVER_SCALED_TOLERANCE_TRAJECTORY_PROBE.csv"
                and manifest.get("proof_solver_tolerance_regime_sweep")
                == "PROOF_SOLVER_TOLERANCE_REGIME_SWEEP.md"
                and manifest.get("proof_solver_tolerance_regime_sweep_json")
                == "PROOF_SOLVER_TOLERANCE_REGIME_SWEEP.json"
                and manifest.get("proof_solver_tolerance_regime_sweep_csv")
                == "PROOF_SOLVER_TOLERANCE_REGIME_SWEEP.csv"
                and manifest.get("dynamic_row_oracle_gate") == "DYNAMIC_ROW_ORACLE_GATE.md"
                and manifest.get("dynamic_row_oracle_gate_json") == "DYNAMIC_ROW_ORACLE_GATE.json"
                and manifest.get("kinematic_row_defect_certificate") == "KINEMATIC_ROW_DEFECT_CERTIFICATE.md"
                and manifest.get("kinematic_row_defect_certificate_json") == "KINEMATIC_ROW_DEFECT_CERTIFICATE.json"
                and manifest.get("newton_euler_defect_obligation_gate") == "NEWTON_EULER_DEFECT_OBLIGATION_GATE.md"
                and manifest.get("newton_euler_defect_obligation_gate_json") == "NEWTON_EULER_DEFECT_OBLIGATION_GATE.json"
                and manifest.get("newton_euler_ad_expanded_row_oracle_audit")
                == "NEWTON_EULER_AD_EXPANDED_ROW_ORACLE_AUDIT.md"
                and manifest.get("newton_euler_ad_expanded_row_oracle_audit_json")
                == "NEWTON_EULER_AD_EXPANDED_ROW_ORACLE_AUDIT.json"
                and manifest.get("b1_symbolic_row_oracle_closure_certificate")
                == "B1_SYMBOLIC_ROW_ORACLE_CLOSURE_CERTIFICATE.md"
                and manifest.get("b1_symbolic_row_oracle_closure_certificate_json")
                == "B1_SYMBOLIC_ROW_ORACLE_CLOSURE_CERTIFICATE.json"
                and manifest.get("b1_ad_expanded_symbolic_oracle_closure_certificate")
                == "B1_AD_EXPANDED_SYMBOLIC_ORACLE_CLOSURE_CERTIFICATE.md"
                and manifest.get("b1_ad_expanded_symbolic_oracle_closure_certificate_json")
                == "B1_AD_EXPANDED_SYMBOLIC_ORACLE_CLOSURE_CERTIFICATE.json"
                and manifest.get("newton_euler_dynamic_row_closure_contract")
                == "NEWTON_EULER_DYNAMIC_ROW_CLOSURE_CONTRACT.md"
                and manifest.get("newton_euler_dynamic_row_closure_contract_json")
                == "NEWTON_EULER_DYNAMIC_ROW_CLOSURE_CONTRACT.json"
                and manifest.get("submission_ready") is False
                and manifest.get("mechanical_preflight_passed") is True
                and manifest.get("quality_review_passed") is False
                and manifest.get("quality_review_passed_under_narrowed_claim") is True
                and manifest.get("narrowed_claim_submission_standard_met") is True
                and manifest.get("narrowed_claim_decision") == "submit_under_narrowed_claim"
                and manifest.get("quality_review_scope") == "global_false_narrowed_claim_subcheck_true"
                and manifest.get("cmame_flat_submission_dir") == "cmame_submission_flat"
                and manifest.get("cmame_flat_tex") == "cmame_submission_flat/main_cmame_submission.tex"
                and manifest.get("cmame_flat_pdf") == "cmame_submission_flat/main_cmame_submission.pdf"
                and manifest.get("cmame_flat_source_archive") == "cmame_submission_flat.zip"
                and manifest.get("concise_pdf") == "main_concise.pdf"
                and manifest.get("supporting_pdf") == "main.pdf"
                and manifest.get("submission_index") == "SUBMISSION_PACKET.md"
                and manifest.get("cover_letter") == "COVER_LETTER.md"
                and manifest.get("file_inventory") == "SUBMISSION_FILE_INVENTORY.md"
                and manifest.get("review_response_template") == "REVIEW_RESPONSE_TEMPLATE.md"
                and manifest.get("source_paper_comparison") == "SOURCE_PAPER_COMPARISON.md"
                and manifest.get("paper_numerical_result_matrix") == "PAPER_NUMERICAL_RESULT_MATRIX.md"
                and manifest.get("paper_numerical_result_matrix_json") == "PAPER_NUMERICAL_RESULT_MATRIX.json"
                and manifest.get("paper_numerical_result_matrix_csv") == "PAPER_NUMERICAL_RESULT_MATRIX.csv"
                and manifest.get("four_example_source_policy_dashboard") == "FOUR_EXAMPLE_SOURCE_POLICY_DASHBOARD.md"
                and manifest.get("four_example_source_policy_dashboard_json")
                == "FOUR_EXAMPLE_SOURCE_POLICY_DASHBOARD.json"
                and manifest.get("result_to_manuscript_traceability_audit")
                == "RESULT_TO_MANUSCRIPT_TRACEABILITY_AUDIT.md"
                and manifest.get("result_to_manuscript_traceability_audit_json")
                == "RESULT_TO_MANUSCRIPT_TRACEABILITY_AUDIT.json"
                and manifest.get("all_method_example_claim_disposition_audit")
                == "ALL_METHOD_EXAMPLE_CLAIM_DISPOSITION_AUDIT.md"
                and manifest.get("all_method_example_claim_disposition_audit_json")
                == "ALL_METHOD_EXAMPLE_CLAIM_DISPOSITION_AUDIT.json"
                and manifest.get("cross_paper_benchmark_matrix") == "CROSS_PAPER_BENCHMARK_MATRIX.md"
                and manifest.get("cross_paper_benchmark_spec") == "CROSS_PAPER_BENCHMARK_SPEC.md"
                and manifest.get("cross_paper_benchmark_cases") == "CROSS_PAPER_BENCHMARK_CASES.json"
                and manifest.get("external_same_test_run_queue") == "EXTERNAL_SAME_TEST_RUN_QUEUE.md"
                and manifest.get("external_same_test_run_queue_json") == "EXTERNAL_SAME_TEST_RUN_QUEUE.json"
                and manifest.get("kissel_negrut_code_inventory") == "KISSEL_NEGRUT_CODE_INVENTORY.md"
                and manifest.get("source_policy_closure_triage") == "SOURCE_POLICY_CLOSURE_TRIAGE.md"
                and manifest.get("source_policy_closure_triage_json") == "SOURCE_POLICY_CLOSURE_TRIAGE.json"
                and manifest.get("source_policy_row_closure_ledger") == "SOURCE_POLICY_ROW_CLOSURE_LEDGER.md"
                and manifest.get("source_policy_row_closure_ledger_json") == "SOURCE_POLICY_ROW_CLOSURE_LEDGER.json"
                and manifest.get("source_policy_local_candidate_gap_audit")
                == "SOURCE_POLICY_LOCAL_CANDIDATE_GAP_AUDIT.md"
                and manifest.get("source_policy_local_candidate_gap_audit_json")
                == "SOURCE_POLICY_LOCAL_CANDIDATE_GAP_AUDIT.json"
                and manifest.get("all_examples_source_policy_audit") == "ALL_EXAMPLES_SOURCE_POLICY_AUDIT.md"
                and manifest.get("all_examples_source_policy_audit_json") == "ALL_EXAMPLES_SOURCE_POLICY_AUDIT.json"
                and manifest.get("external_case_evidence_reconciliation") == "EXTERNAL_CASE_EVIDENCE_RECONCILIATION.md"
                and manifest.get("external_case_evidence_reconciliation_json") == "EXTERNAL_CASE_EVIDENCE_RECONCILIATION.json"
                and manifest.get("vp2024_code_path_disposition_audit") == "VP2024_CODE_PATH_DISPOSITION_AUDIT.md"
                and manifest.get("vp2024_code_path_disposition_audit_json") == "VP2024_CODE_PATH_DISPOSITION_AUDIT.json"
                and manifest.get("b4_existing_artifact_promotion_audit")
                == "B4_EXISTING_ARTIFACT_PROMOTION_AUDIT.md"
                and manifest.get("b4_existing_artifact_promotion_audit_json")
                == "B4_EXISTING_ARTIFACT_PROMOTION_AUDIT.json"
                and manifest.get("b4_source_policy_post_execution_audit")
                == "B4_SOURCE_POLICY_POST_EXECUTION_AUDIT.md"
                and manifest.get("b4_source_policy_post_execution_audit_json")
                == "B4_SOURCE_POLICY_POST_EXECUTION_AUDIT.json"
                and manifest.get("ra2021_double_source_policy_low_order_diagnosis")
                == "RA2021_DOUBLE_SOURCE_POLICY_LOW_ORDER_DIAGNOSIS.md"
                and manifest.get("ra2021_double_source_policy_low_order_diagnosis_json")
                == "RA2021_DOUBLE_SOURCE_POLICY_LOW_ORDER_DIAGNOSIS.json"
                and manifest.get("hi2022_ra_half_double_source_policy_failure_diagnosis")
                == "HI2022_RA_HALF_DOUBLE_SOURCE_POLICY_FAILURE_DIAGNOSIS.md"
                and manifest.get("hi2022_ra_half_double_source_policy_failure_diagnosis_json")
                == "HI2022_RA_HALF_DOUBLE_SOURCE_POLICY_FAILURE_DIAGNOSIS.json"
                and manifest.get("b4_source_policy_row_closure_readiness_ledger")
                == "B4_SOURCE_POLICY_ROW_CLOSURE_READINESS_LEDGER.md"
                and manifest.get("b4_source_policy_row_closure_readiness_ledger_json")
                == "B4_SOURCE_POLICY_ROW_CLOSURE_READINESS_LEDGER.json"
                and manifest.get("b4_source_policy_row_closure_readiness_ledger_csv")
                == "B4_SOURCE_POLICY_ROW_CLOSURE_READINESS_LEDGER.csv"
                and manifest.get("b4_source_policy_execution_opt_in_packet")
                == "B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.md"
                and manifest.get("b4_source_policy_execution_opt_in_packet_json")
                == "B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json"
                and manifest.get("b4_source_policy_execution_handoff_package")
                == "B4_SOURCE_POLICY_EXECUTION_HANDOFF_PACKAGE.md"
                and manifest.get("b4_source_policy_execution_handoff_package_json")
                == "B4_SOURCE_POLICY_EXECUTION_HANDOFF_PACKAGE.json"
                and manifest.get("b4_source_policy_command_preflight_freeze")
                == "B4_SOURCE_POLICY_COMMAND_PREFLIGHT_FREEZE_20260620.md"
                and manifest.get("b4_source_policy_command_preflight_freeze_json")
                == "B4_SOURCE_POLICY_COMMAND_PREFLIGHT_FREEZE_20260620.json"
                and manifest.get("b4_source_policy_expected_output_schema_audit")
                == "B4_SOURCE_POLICY_EXPECTED_OUTPUT_SCHEMA_AUDIT_20260620.md"
                and manifest.get("b4_source_policy_expected_output_schema_audit_json")
                == "B4_SOURCE_POLICY_EXPECTED_OUTPUT_SCHEMA_AUDIT_20260620.json"
                and manifest.get("b4_expected_output_promotion_readiness_blocker_audit")
                == "B4_EXPECTED_OUTPUT_PROMOTION_READINESS_BLOCKER_AUDIT_20260620.md"
                and manifest.get("b4_expected_output_promotion_readiness_blocker_audit_json")
                == "B4_EXPECTED_OUTPUT_PROMOTION_READINESS_BLOCKER_AUDIT_20260620.json"
                and manifest.get("oc6_source_equivalent_reopen_readiness_audit")
                == "OC6_SOURCE_EQUIVALENT_REOPEN_READINESS_AUDIT_20260620.md"
                and manifest.get("oc6_source_equivalent_reopen_readiness_audit_json")
                == "OC6_SOURCE_EQUIVALENT_REOPEN_READINESS_AUDIT_20260620.json"
                and manifest.get("full_source_policy_runner_archive_gap_audit")
                == "FULL_SOURCE_POLICY_RUNNER_ARCHIVE_GAP_AUDIT.md"
                and manifest.get("full_source_policy_runner_archive_gap_audit_json")
                == "FULL_SOURCE_POLICY_RUNNER_ARCHIVE_GAP_AUDIT.json"
                and manifest.get("source_policy_reopen_condition_monitor")
                == "SOURCE_POLICY_REOPEN_CONDITION_MONITOR_20260620.md"
                and manifest.get("source_policy_reopen_condition_monitor_json")
                == "SOURCE_POLICY_REOPEN_CONDITION_MONITOR_20260620.json"
                and manifest_archive_action_boundary
                == objective_summary.get("full_source_policy_runner_archive_gap_action_boundary")
                == full_source_runner_gap.get("action_boundary")
                and manifest.get("full_source_policy_runner_archive_gap_safe_action_ids")
                == objective_summary.get("full_source_policy_runner_archive_gap_safe_action_ids")
                == full_source_runner_gap.get("safe_action_ids")
                and manifest.get("full_source_policy_runner_archive_gap_opt_in_action_ids")
                == objective_summary.get("full_source_policy_runner_archive_gap_opt_in_action_ids")
                == full_source_runner_gap.get("opt_in_action_ids")
                and manifest.get("full_source_policy_runner_archive_gap_source_policy_execution_invoked")
                == objective_summary.get("full_source_policy_runner_archive_gap_source_policy_execution_invoked")
                == full_source_runner_gap.get("source_policy_execution_invoked")
                is False
                and manifest_archive_action_boundary.get("source_policy_execution_allowed_now") is False
                and manifest_archive_action_boundary.get("exact_b4_opt_in_required_for_execution") is True
                and manifest_archive_action_boundary.get("safe_without_b4_opt_in_count") == 4
                and manifest_archive_action_boundary.get("opt_in_required_action_count") == 1
                and manifest_archive_action_boundary.get("opt_in_required_command_count") == 13
                and manifest_archive_action_boundary.get("opt_in_required_mapped_external_rows") == 20
                and manifest_narrowed_archive_boundary == reproducibility_narrowed_archive_boundary
                and manifest_narrowed_archive_boundary.get("status")
                == "narrowed_archive_ready_not_full_source_policy_runner_archive"
                and manifest_narrowed_archive_boundary.get("scope") == "narrowed_claim_only"
                and manifest_narrowed_archive_boundary.get("blocking_ids")
                == objective_completion.get("blocking_ids")
                and manifest_narrowed_archive_boundary.get("blocker_status_by_id")
                == objective_completion.get("blocker_status_by_id")
                and manifest_narrowed_archive_boundary.get("blocker_required_to_close_by_id")
                == objective_completion.get("blocker_required_to_close_by_id")
                and manifest_narrowed_archive_boundary.get("blocker_safe_next_actions_by_id")
                == objective_completion.get("blocker_safe_next_actions_by_id")
                and manifest_narrowed_archive_boundary.get("blocker_opt_in_required_actions_by_id")
                == objective_completion.get("blocker_opt_in_required_actions_by_id")
                and manifest_narrowed_archive_boundary.get("source_policy_closed_ratio")
                == objective_completion.get("source_policy_closed_ratio")
                == "0/40"
                and manifest_narrowed_archive_boundary.get(
                    "current_archive_usable_as_full_source_policy_runner_archive"
                )
                is False
                and manifest_narrowed_archive_boundary.get("source_policy_execution_allowed_now") is False
                and manifest_narrowed_archive_boundary.get(
                    "exact_b4_opt_in_required_for_execution"
                )
                is True
                and manifest_narrowed_archive_boundary.get("safe_action_ids")
                == full_source_runner_gap.get("safe_action_ids")
                and manifest_narrowed_archive_boundary.get("opt_in_action_ids")
                == full_source_runner_gap.get("opt_in_action_ids")
                and manifest.get("narrowed_archive_boundary_status")
                == manifest_narrowed_archive_boundary.get("status")
                and manifest.get("narrowed_archive_boundary_source_policy_closed_ratio")
                == manifest_narrowed_archive_boundary.get("source_policy_closed_ratio")
                and manifest.get(
                    "narrowed_archive_boundary_current_archive_usable_as_full_source_policy_runner_archive"
                )
                == manifest_narrowed_archive_boundary.get(
                    "current_archive_usable_as_full_source_policy_runner_archive"
                )
                and manifest.get("narrowed_archive_boundary_source_policy_execution_allowed_now")
                == manifest_narrowed_archive_boundary.get("source_policy_execution_allowed_now")
                and manifest.get("narrowed_archive_boundary_exact_b4_opt_in_required_for_execution")
                == manifest_narrowed_archive_boundary.get("exact_b4_opt_in_required_for_execution")
                and manifest.get("narrowed_archive_boundary_safe_action_ids")
                == manifest_narrowed_archive_boundary.get("safe_action_ids")
                and manifest.get("narrowed_archive_boundary_opt_in_action_ids")
                == manifest_narrowed_archive_boundary.get("opt_in_action_ids")
                and manifest.get("objective_blocker_required_to_close_by_id")
                == objective_completion.get("blocker_required_to_close_by_id")
                and manifest.get("objective_blocker_safe_next_actions_by_id")
                == objective_completion.get("blocker_safe_next_actions_by_id")
                and manifest.get("objective_blocker_opt_in_required_actions_by_id")
                == objective_completion.get("blocker_opt_in_required_actions_by_id")
                and manifest.get("blocker_required_to_close_by_id")
                == manifest.get("objective_blocker_required_to_close_by_id")
                == objective_completion.get("blocker_required_to_close_by_id")
                and manifest.get("blocker_safe_next_actions_by_id")
                == manifest.get("objective_blocker_safe_next_actions_by_id")
                == objective_completion.get("blocker_safe_next_actions_by_id")
                and manifest.get("blocker_opt_in_required_actions_by_id")
                == manifest.get("objective_blocker_opt_in_required_actions_by_id")
                == objective_completion.get("blocker_opt_in_required_actions_by_id")
                and manifest.get("oc6_reopen_latest_external_probe")
                == (
                    f"{full_source_runner_gap.get('oc6_source_equivalent_reopen_readiness_latest_external_probe_date')}/"
                    f"{full_source_runner_gap.get('oc6_source_equivalent_reopen_readiness_latest_external_probe_count')}/"
                    f"{full_source_runner_gap.get('oc6_source_equivalent_reopen_readiness_latest_external_probe_positive_artifact_rows')}/"
                    f"{full_source_runner_gap.get('oc6_source_equivalent_reopen_readiness_latest_external_probe_source_policy_rows_closed')}/"
                    f"{full_source_runner_gap.get('oc6_source_equivalent_reopen_readiness_latest_external_probe_access_limited_count')}/"
                    f"{full_source_runner_gap.get('oc6_source_equivalent_reopen_readiness_latest_external_probe_global_absence_proved')}/"
                    f"{full_source_runner_gap.get('oc6_source_equivalent_reopen_readiness_latest_external_probe_reopen_triggered')}"
                )
                == "2026-06-21/9/0/0/4/False/False"
                and manifest.get("oc6_reopen_latest_external_probe_date") == "2026-06-21"
                and manifest.get("oc6_reopen_latest_external_probe_count") == 9
                and manifest.get("oc6_reopen_latest_external_probe_positive_artifact_rows") == 0
                and manifest.get("oc6_reopen_latest_external_probe_source_policy_rows_closed") == 0
                and manifest.get("oc6_reopen_latest_external_probe_access_limited_count") == 4
                and manifest.get("oc6_reopen_latest_external_probe_global_absence_proved") is False
                and manifest.get("oc6_reopen_latest_external_probe_reopen_triggered") is False
                and manifest.get("ra2021_source_identity_audit") == "RA2021_SOURCE_IDENTITY_AUDIT.md"
                and manifest.get("ra2021_source_identity_audit_json") == "RA2021_SOURCE_IDENTITY_AUDIT.json"
                and manifest.get("hi2022_policy_decision_audit") == "HI2022_POLICY_DECISION_AUDIT.md"
                and manifest.get("hi2022_policy_decision_audit_json") == "HI2022_POLICY_DECISION_AUDIT.json"
                and manifest.get("hi2022_source_policy_row_audit") == "HI2022_SOURCE_POLICY_ROW_AUDIT.md"
                and manifest.get("hi2022_source_policy_row_audit_json") == "HI2022_SOURCE_POLICY_ROW_AUDIT.json"
                and manifest.get("hi2022_t8_tolerance_repair_audit") == "HI2022_T8_TOLERANCE_REPAIR_AUDIT.md"
                and manifest.get("hi2022_t8_tolerance_repair_audit_json") == "HI2022_T8_TOLERANCE_REPAIR_AUDIT.json"
                and manifest.get("implementation_fidelity_certificate") == "IMPLEMENTATION_FIDELITY_CERTIFICATE.md"
                and manifest.get("implementation_path_audit") == "IMPLEMENTATION_PATH_AUDIT.md"
                and manifest.get("implementation_path_audit_json") == "IMPLEMENTATION_PATH_AUDIT.json"
                and manifest.get("order_acceptance_gate") == "ORDER_ACCEPTANCE_GATE.md"
                and manifest.get("order_acceptance_gate_json") == "ORDER_ACCEPTANCE_GATE.json"
                and manifest.get("claim_boundary") == "CLAIM_BOUNDARY.json"
                and claim.get("type") == "conditional_formal_order_comparison"
                and claim.get("accepted_method") == "Gauss6/FullVA"
                and claim.get("method_order_claim") == 6
                and claim.get("smooth_projected_orders", {}).get("position") == 7.161
                and claim.get("smooth_projected_orders", {}).get("velocity") == 7.066
                and comparator.get("expected_order") == 5
                and set(claim.get("accepted_examples", []))
                == {"single_pendulum", "double_pendulum", "four_link", "slider_crank"}
                and "complete_source_paper_residual_reproduction" in manifest.get("non_claims", [])
                and "accepted_independent_full_tfe_stage_replacement" in manifest.get("non_claims", [])
                and manifest.get("full_tfe_stage_replacement") is False
                and manifest.get("full_generator_invoked_by_submission_checks") is False
                and "validate_cmame_submission.py" in manifest.get("validators", [])
                and "validate_cmame_submission_integrity_audit.py" in manifest.get("validators", [])
                and "validate_reference_metadata_audit.py" in manifest.get("validators", [])
                and "validate_cmame_blocker_closure_gate.py" in manifest.get("validators", [])
                and "validate_cmame_external_baseline_gate.py" in manifest.get("validators", [])
                and "validate_cmame_proof_contract_gate.py" in manifest.get("validators", [])
                and "validate_cmame_visual_legibility_audit.py" in manifest.get("validators", [])
                and "validate_cmame_figure_set_audit.py" in manifest.get("validators", [])
                and "validate_cmame_scalability_boundary_audit.py" in manifest.get("validators", [])
                and "validate_cmame_related_work_audit.py" in manifest.get("validators", [])
                and "validate_cmame_prose_residue_audit.py" in manifest.get("validators", [])
                and "validate_cmame_claim_hygiene_audit.py" in manifest.get("validators", [])
                and "validate_cmame_proof_style_audit.py" in manifest.get("validators", [])
                and "validate_cmame_strict_proof_audit.py" in manifest.get("validators", [])
                and "validate_proof_closure_manifest.py" in manifest.get("validators", [])
                and "validate_proof_claim_traceability_audit.py" in manifest.get("validators", [])
                and "validate_d5_dynamic_defect_readiness_audit.py" in manifest.get("validators", [])
                and "validate_d5_dynamic_direct_substitution_certificate.py" in manifest.get("validators", [])
                and "validate_d5_taylor_term_budget_audit.py" in manifest.get("validators", [])
                and "validate_d5_primitive_bound_reduction_audit.py" in manifest.get("validators", [])
                and "validate_d5_p_tube_constants_audit.py" in manifest.get("validators", [])
                and "validate_d5_p_state_lift_gap_audit.py" in manifest.get("validators", [])
                and "validate_d5_p_state_map_definition_audit.py" in manifest.get("validators", [])
                and "validate_d5_p_state_anticircularity_audit.py" in manifest.get("validators", [])
                and "validate_d5_p_state_ps2_weighted_target_audit.py" in manifest.get("validators", [])
                and "validate_d5_p_state_ps2_kinematic_block_certificate.py" in manifest.get("validators", [])
                and "validate_d5_p_state_ps2_lie_chart_binding_audit.py" in manifest.get("validators", [])
                and "validate_d5_p_state_ps2_row_injection_audit.py" in manifest.get("validators", [])
                and "validate_d5_p_state_ps2_nonlinear_binding_audit.py" in manifest.get("validators", [])
                and "validate_d5_p_state_ps2_aggregate_promotion_audit.py" in manifest.get("validators", [])
                and "validate_d5_p_state_ps2_linearization_probe.py" in manifest.get("validators", [])
                and "validate_d5_p_state_ps3_conditional_conversion_audit.py" in manifest.get("validators", [])
                and "validate_d5_p_state_ps3_actual_instantiation_gap_audit.py" in manifest.get("validators", [])
                and "validate_d5_p_state_ps3_h_acc_input_obstruction_audit.py" in manifest.get("validators", [])
                and "validate_d5_p_acc_map_definition_audit.py" in manifest.get("validators", [])
                and "validate_d5_p_acc_row_binding_audit.py" in manifest.get("validators", [])
                and "validate_d5_p_acc_independence_audit.py" in manifest.get("validators", [])
                and "validate_d5_p_acc_lift_obstruction_audit.py" in manifest.get("validators", [])
                and "validate_d5_p_acc_pa2_weighted_inverse_audit.py" in manifest.get("validators", [])
                and "validate_d5_p_lambda_interface_audit.py" in manifest.get("validators", [])
                and "validate_d5_p_lambda_inf_sup_probe.py" in manifest.get("validators", [])
                and "validate_d5_p_lambda_pl2_geometric_margin_audit.py" in manifest.get("validators", [])
                and "validate_d5_p_lambda_d3_noncircularity_audit.py" in manifest.get("validators", [])
                and "validate_d5_p_geom_chart_reduction_audit.py" in manifest.get("validators", [])
                and "validate_d5_p_gyro_bilinear_reduction_audit.py" in manifest.get("validators", [])
                and "validate_d5_open_primitive_gap_audit.py" in manifest.get("validators", [])
                and "validate_d5_primitive_obligation_closure_plan.py" in manifest.get("validators", [])
                and "validate_paper_numerical_result_matrix.py" in manifest.get("validators", [])
                and "validate_four_example_source_policy_dashboard.py" in manifest.get("validators", [])
                and "validate_result_to_manuscript_traceability_audit.py" in manifest.get("validators", [])
                and "validate_all_method_example_claim_disposition_audit.py" in manifest.get("validators", [])
                and "validate_dynamic_row_oracle_gate.py" in manifest.get("validators", [])
                and "validate_kinematic_row_defect_certificate.py" in manifest.get("validators", [])
                and "validate_newton_euler_defect_obligation_gate.py" in manifest.get("validators", [])
                and "validate_newton_euler_virtual_work_wrench_audit.py" in manifest.get("validators", [])
                and "validate_b1_symbolic_row_oracle_closure_certificate.py" in manifest.get("validators", [])
                and "validate_b1_ad_expanded_symbolic_oracle_closure_certificate.py"
                in manifest.get("validators", [])
                and "validate_newton_euler_dynamic_row_closure_contract.py" in manifest.get("validators", [])
                and "validate_concise_paper.py" in manifest.get("validators", [])
                and "validate_proof_evidence_matrix.py" in manifest.get("validators", [])
                and "validate_proof_numerical_scale_audit.py" in manifest.get("validators", [])
                and "validate_proof_solver_scale_audit.py" in manifest.get("validators", [])
                and "validate_proof_solver_scaled_tolerance_probe.py" in manifest.get("validators", [])
                and "validate_proof_solver_scaled_tolerance_trajectory_probe.py" in manifest.get("validators", [])
                and "validate_proof_solver_tolerance_regime_sweep.py" in manifest.get("validators", [])
                and "validate_order_acceptance_gate.py" in manifest.get("validators", [])
                and "validate_implementation_fidelity_certificate.py" in manifest.get("validators", [])
                and "validate_implementation_path_audit.py" in manifest.get("validators", [])
                and "validate_source_paper_comparison.py" in manifest.get("validators", [])
                and "validate_cross_paper_benchmark_spec.py" in manifest.get("validators", [])
                and "validate_cross_paper_benchmark_cases.py" in manifest.get("validators", [])
                and "validate_external_same_test_run_queue.py" in manifest.get("validators", [])
                and "validate_source_policy_closure_triage.py" in manifest.get("validators", [])
                and "validate_source_policy_row_closure_ledger.py" in manifest.get("validators", [])
                and "validate_source_policy_local_candidate_gap_audit.py" in manifest.get("validators", [])
                and "validate_all_examples_source_policy_audit.py" in manifest.get("validators", [])
                and "validate_external_suite_disposition_audit.py" in manifest.get("validators", [])
                and "validate_external_source_policy_closure_manifest.py" in manifest.get("validators", [])
                and "validate_external_case_evidence_reconciliation.py" in manifest.get("validators", [])
                and "validate_vp2024_code_path_disposition_audit.py" in manifest.get("validators", [])
                and "validate_b2_source_policy_remaining_work_manifest.py" in manifest.get("validators", [])
                and "validate_b4_source_policy_work_precision_execution_plan.py" in manifest.get("validators", [])
                and "validate_b4_existing_artifact_promotion_audit.py" in manifest.get("validators", [])
                and "validate_b4_source_policy_post_execution_audit.py" in manifest.get("validators", [])
                and "validate_ra2021_double_source_policy_low_order_diagnosis.py" in manifest.get("validators", [])
                and "validate_hi2022_ra_half_double_source_policy_failure_diagnosis.py"
                in manifest.get("validators", [])
                and "validate_b4_source_policy_row_closure_readiness_ledger.py" in manifest.get("validators", [])
                and "validate_b4_source_policy_execution_opt_in_packet.py" in manifest.get("validators", [])
                and "validate_b4_source_policy_execution_handoff_package.py" in manifest.get("validators", [])
                and "validate_b4_source_policy_command_preflight_freeze_20260620.py" in manifest.get("validators", [])
                and "validate_b4_source_policy_expected_output_schema_audit_20260620.py" in manifest.get("validators", [])
                and "validate_b4_expected_output_promotion_readiness_blocker_audit_20260620.py" in manifest.get("validators", [])
                and "validate_oc6_source_equivalent_reopen_readiness_audit_20260620.py" in manifest.get("validators", [])
                and "validate_ra2021_source_policy_row_audit.py" in manifest.get("validators", [])
                and "validate_ra2021_source_identity_audit.py" in manifest.get("validators", [])
                and "validate_hi2022_policy_decision_audit.py" in manifest.get("validators", [])
                and "validate_hi2022_source_policy_row_audit.py" in manifest.get("validators", [])
                and "validate_hi2022_t8_tolerance_repair_audit.py" in manifest.get("validators", [])
                and "validate_tfe_source_policy_spec.py" in manifest.get("validators", [])
                and "validate_tfe_source_policy_row_audit.py" in manifest.get("validators", [])
                and "validate_tfe_b4_b7_source_policy_demotion_audit.py" in manifest.get("validators", [])
                and "validate_tfe_source_pendulum_model_audit.py" in manifest.get("validators", [])
                and "validate_tfe_brown_mcphee_source_law_boundary_audit.py" in manifest.get("validators", [])
                and "validate_tfe_source_grid_compatibility_audit.py" in manifest.get("validators", [])
                and "validate_tfe_endpoint_policy_boundary_certificate.py" in manifest.get("validators", [])
                and "validate_tfe_endpoint_policy_sensitivity_audit.py" in manifest.get("validators", [])
                and "validate_objective_completion_audit.py" in manifest.get("validators", [])
                and "validate_comparison_objective_closure_reconciliation_audit.py" in manifest.get("validators", [])
                and "validate_cmame_minimal_reproducibility_candidate.py" in manifest.get("validators", [])
                and "validate_b1_symbolic_row_oracle_closure_certificate.py" in manifest.get("validators", [])
                and "validate_b1_ad_expanded_symbolic_oracle_closure_certificate.py"
                in manifest.get("validators", [])
                and "validate_submission_bundle.py" in manifest.get("validators", [])
                and "validate_paper_package.py" in manifest.get("validators", [])
                and "../validate_pipeline_outputs.py" in manifest.get("validators", [])
                and set(manifest.get("required_submission_files", []))
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
                }
                and "main_cmame.pdf" in manifest.get("evidence_anchors", [])
                and "main_cmame.tex" in manifest.get("evidence_anchors", [])
                and "highlights_cmame.txt" in manifest.get("evidence_anchors", [])
                and "declarations_cmame.md" in manifest.get("evidence_anchors", [])
                and "CMAME_SUBMISSION_CHECKLIST.md" in manifest.get("evidence_anchors", [])
                and "CMAME_SUBMISSION_READINESS_AUDIT.md" in manifest.get("evidence_anchors", [])
                and "CMAME_SUBMISSION_READINESS_REVIEW.md" in manifest.get("evidence_anchors", [])
                and "CMAME_SUBMISSION_INTEGRITY_AUDIT.md" in manifest.get("evidence_anchors", [])
                and "CMAME_SUBMISSION_INTEGRITY_AUDIT.json" in manifest.get("evidence_anchors", [])
                and "REFERENCE_METADATA_AUDIT.md" in manifest.get("evidence_anchors", [])
                and "REFERENCE_METADATA_AUDIT.json" in manifest.get("evidence_anchors", [])
                and "CMAME_BLOCKER_CLOSURE_GATE.md" in manifest.get("evidence_anchors", [])
                and "CMAME_BLOCKER_CLOSURE_GATE.json" in manifest.get("evidence_anchors", [])
                and "CMAME_EXTERNAL_BASELINE_GATE.md" in manifest.get("evidence_anchors", [])
                and "CMAME_EXTERNAL_BASELINE_GATE.json" in manifest.get("evidence_anchors", [])
                and "CMAME_PROOF_CONTRACT_GATE.md" in manifest.get("evidence_anchors", [])
                and "CMAME_PROOF_CONTRACT_GATE.json" in manifest.get("evidence_anchors", [])
                and "CMAME_VISUAL_LEGIBILITY_AUDIT.md" in manifest.get("evidence_anchors", [])
                and "CMAME_VISUAL_LEGIBILITY_AUDIT.json" in manifest.get("evidence_anchors", [])
                and "CMAME_FIGURE_SET_AUDIT.md" in manifest.get("evidence_anchors", [])
                and "CMAME_FIGURE_SET_AUDIT.json" in manifest.get("evidence_anchors", [])
                and "CMAME_SCALABILITY_BOUNDARY_AUDIT.md" in manifest.get("evidence_anchors", [])
                and "CMAME_SCALABILITY_BOUNDARY_AUDIT.json" in manifest.get("evidence_anchors", [])
                and "CMAME_RELATED_WORK_AUDIT.md" in manifest.get("evidence_anchors", [])
                and "CMAME_RELATED_WORK_AUDIT.json" in manifest.get("evidence_anchors", [])
                and "CMAME_PROSE_RESIDUE_AUDIT.md" in manifest.get("evidence_anchors", [])
                and "CMAME_PROSE_RESIDUE_AUDIT.json" in manifest.get("evidence_anchors", [])
                and "CMAME_CLAIM_HYGIENE_AUDIT.md" in manifest.get("evidence_anchors", [])
                and "CMAME_CLAIM_HYGIENE_AUDIT.json" in manifest.get("evidence_anchors", [])
                and "CMAME_PROOF_STYLE_AUDIT.md" in manifest.get("evidence_anchors", [])
                and "CMAME_PROOF_STYLE_AUDIT.json" in manifest.get("evidence_anchors", [])
                and "CMAME_STRICT_PROOF_AUDIT.md" in manifest.get("evidence_anchors", [])
                and "CMAME_STRICT_PROOF_AUDIT.json" in manifest.get("evidence_anchors", [])
                and "CMAME_STRICT_PROOF_POLICY_RECONCILIATION_AUDIT.md"
                in manifest.get("evidence_anchors", [])
                and "CMAME_STRICT_PROOF_POLICY_RECONCILIATION_AUDIT.json"
                in manifest.get("evidence_anchors", [])
                and "PROOF_CLOSURE_MANIFEST.md" in manifest.get("evidence_anchors", [])
                and "PROOF_CLOSURE_MANIFEST.json" in manifest.get("evidence_anchors", [])
                and "PROOF_CLAIM_TRACEABILITY_AUDIT.md" in manifest.get("evidence_anchors", [])
                and "PROOF_CLAIM_TRACEABILITY_AUDIT.json" in manifest.get("evidence_anchors", [])
                and "D5_DYNAMIC_DEFECT_READINESS_AUDIT.md" in manifest.get("evidence_anchors", [])
                and "D5_DYNAMIC_DEFECT_READINESS_AUDIT.json" in manifest.get("evidence_anchors", [])
                and "D5_DYNAMIC_DIRECT_SUBSTITUTION_CERTIFICATE.md" in manifest.get("evidence_anchors", [])
                and "D5_DYNAMIC_DIRECT_SUBSTITUTION_CERTIFICATE.json" in manifest.get("evidence_anchors", [])
                and "D5_TAYLOR_TERM_BUDGET_AUDIT.md" in manifest.get("evidence_anchors", [])
                and "D5_TAYLOR_TERM_BUDGET_AUDIT.json" in manifest.get("evidence_anchors", [])
                and "D5_PRIMITIVE_BOUND_REDUCTION_AUDIT.md" in manifest.get("evidence_anchors", [])
                and "D5_PRIMITIVE_BOUND_REDUCTION_AUDIT.json" in manifest.get("evidence_anchors", [])
                and "D5_P_TUBE_CONSTANTS_AUDIT.md" in manifest.get("evidence_anchors", [])
                and "D5_P_TUBE_CONSTANTS_AUDIT.json" in manifest.get("evidence_anchors", [])
                and "D5_P_STATE_LIFT_GAP_AUDIT.md" in manifest.get("evidence_anchors", [])
                and "D5_P_STATE_LIFT_GAP_AUDIT.json" in manifest.get("evidence_anchors", [])
                and "D5_P_STATE_MAP_DEFINITION_AUDIT.md" in manifest.get("evidence_anchors", [])
                and "D5_P_STATE_MAP_DEFINITION_AUDIT.json" in manifest.get("evidence_anchors", [])
                and "D5_P_STATE_ANTICIRCULARITY_AUDIT.md" in manifest.get("evidence_anchors", [])
                and "D5_P_STATE_ANTICIRCULARITY_AUDIT.json" in manifest.get("evidence_anchors", [])
                and "D5_P_STATE_PS2_WEIGHTED_TARGET_AUDIT.md" in manifest.get("evidence_anchors", [])
                and "D5_P_STATE_PS2_WEIGHTED_TARGET_AUDIT.json" in manifest.get("evidence_anchors", [])
                and "D5_P_STATE_PS2_KINEMATIC_BLOCK_CERTIFICATE.md" in manifest.get("evidence_anchors", [])
                and "D5_P_STATE_PS2_KINEMATIC_BLOCK_CERTIFICATE.json" in manifest.get("evidence_anchors", [])
                and "D5_P_STATE_PS2_LIE_CHART_BINDING_AUDIT.md" in manifest.get("evidence_anchors", [])
                and "D5_P_STATE_PS2_LIE_CHART_BINDING_AUDIT.json" in manifest.get("evidence_anchors", [])
                and "D5_P_STATE_PS2_ROW_INJECTION_AUDIT.md" in manifest.get("evidence_anchors", [])
                and "D5_P_STATE_PS2_ROW_INJECTION_AUDIT.json" in manifest.get("evidence_anchors", [])
                and "D5_P_STATE_PS2_NONLINEAR_BINDING_AUDIT.md" in manifest.get("evidence_anchors", [])
                and "D5_P_STATE_PS2_NONLINEAR_BINDING_AUDIT.json" in manifest.get("evidence_anchors", [])
                and "D5_P_STATE_PS2_AGGREGATE_PROMOTION_AUDIT.md" in manifest.get("evidence_anchors", [])
                and "D5_P_STATE_PS2_AGGREGATE_PROMOTION_AUDIT.json" in manifest.get("evidence_anchors", [])
                and "D5_P_STATE_PS2_LINEARIZATION_PROBE.md" in manifest.get("evidence_anchors", [])
                and "D5_P_STATE_PS2_LINEARIZATION_PROBE.json" in manifest.get("evidence_anchors", [])
                and "D5_P_STATE_PS2_LINEARIZATION_PROBE.csv" in manifest.get("evidence_anchors", [])
                and "D5_P_STATE_PS3_CONDITIONAL_CONVERSION_AUDIT.md" in manifest.get("evidence_anchors", [])
                and "D5_P_STATE_PS3_CONDITIONAL_CONVERSION_AUDIT.json" in manifest.get("evidence_anchors", [])
                and "D5_P_STATE_PS3_ACTUAL_INSTANTIATION_GAP_AUDIT.md" in manifest.get("evidence_anchors", [])
                and "D5_P_STATE_PS3_ACTUAL_INSTANTIATION_GAP_AUDIT.json" in manifest.get("evidence_anchors", [])
                and "D5_P_STATE_PS3_H_ACC_INPUT_OBSTRUCTION_AUDIT.md" in manifest.get("evidence_anchors", [])
                and "D5_P_STATE_PS3_H_ACC_INPUT_OBSTRUCTION_AUDIT.json" in manifest.get("evidence_anchors", [])
                and "D5_P_ACC_MAP_DEFINITION_AUDIT.md" in manifest.get("evidence_anchors", [])
                and "D5_P_ACC_MAP_DEFINITION_AUDIT.json" in manifest.get("evidence_anchors", [])
                and "D5_P_ACC_ROW_BINDING_AUDIT.md" in manifest.get("evidence_anchors", [])
                and "D5_P_ACC_ROW_BINDING_AUDIT.json" in manifest.get("evidence_anchors", [])
                and "D5_P_ACC_INDEPENDENCE_AUDIT.md" in manifest.get("evidence_anchors", [])
                and "D5_P_ACC_INDEPENDENCE_AUDIT.json" in manifest.get("evidence_anchors", [])
                and "D5_P_ACC_LIFT_OBSTRUCTION_AUDIT.md" in manifest.get("evidence_anchors", [])
                and "D5_P_ACC_LIFT_OBSTRUCTION_AUDIT.json" in manifest.get("evidence_anchors", [])
                and "D5_P_ACC_PA2_WEIGHTED_INVERSE_AUDIT.md" in manifest.get("evidence_anchors", [])
                and "D5_P_ACC_PA2_WEIGHTED_INVERSE_AUDIT.json" in manifest.get("evidence_anchors", [])
                and "D5_P_LAMBDA_INTERFACE_AUDIT.md" in manifest.get("evidence_anchors", [])
                and "D5_P_LAMBDA_INTERFACE_AUDIT.json" in manifest.get("evidence_anchors", [])
                and "D5_P_LAMBDA_INF_SUP_PROBE.md" in manifest.get("evidence_anchors", [])
                and "D5_P_LAMBDA_INF_SUP_PROBE.json" in manifest.get("evidence_anchors", [])
                and "D5_P_LAMBDA_INF_SUP_PROBE.csv" in manifest.get("evidence_anchors", [])
                and "D5_P_LAMBDA_PL2_GEOMETRIC_MARGIN_AUDIT.md" in manifest.get("evidence_anchors", [])
                and "D5_P_LAMBDA_PL2_GEOMETRIC_MARGIN_AUDIT.json" in manifest.get("evidence_anchors", [])
                and "D5_P_LAMBDA_D3_NONCIRCULARITY_AUDIT.md" in manifest.get("evidence_anchors", [])
                and "D5_P_LAMBDA_D3_NONCIRCULARITY_AUDIT.json" in manifest.get("evidence_anchors", [])
                and "D5_P_LAMBDA_PL4_RATE_PROPAGATION_AUDIT.md" in manifest.get("evidence_anchors", [])
                and "D5_P_LAMBDA_PL4_RATE_PROPAGATION_AUDIT.json" in manifest.get("evidence_anchors", [])
                and "D5_P_GEOM_CHART_REDUCTION_AUDIT.md" in manifest.get("evidence_anchors", [])
                and "D5_P_GEOM_CHART_REDUCTION_AUDIT.json" in manifest.get("evidence_anchors", [])
                and "D5_P_GYRO_BILINEAR_REDUCTION_AUDIT.md" in manifest.get("evidence_anchors", [])
                and "D5_P_GYRO_BILINEAR_REDUCTION_AUDIT.json" in manifest.get("evidence_anchors", [])
                and "D5_OPEN_PRIMITIVE_GAP_AUDIT.md" in manifest.get("evidence_anchors", [])
                and "D5_OPEN_PRIMITIVE_GAP_AUDIT.json" in manifest.get("evidence_anchors", [])
                and "D5_PRIMITIVE_OBLIGATION_CLOSURE_PLAN.md" in manifest.get("evidence_anchors", [])
                and "D5_PRIMITIVE_OBLIGATION_CLOSURE_PLAN.json" in manifest.get("evidence_anchors", [])
                and "D5_CONDITIONAL_TAYLOR_CERTIFICATE.md" in manifest.get("evidence_anchors", [])
                and "D5_CONDITIONAL_TAYLOR_CERTIFICATE.json" in manifest.get("evidence_anchors", [])
                and "DYNAMIC_ROW_ORACLE_GATE.md" in manifest.get("evidence_anchors", [])
                and "DYNAMIC_ROW_ORACLE_GATE.json" in manifest.get("evidence_anchors", [])
                and "KINEMATIC_ROW_DEFECT_CERTIFICATE.md" in manifest.get("evidence_anchors", [])
                and "KINEMATIC_ROW_DEFECT_CERTIFICATE.json" in manifest.get("evidence_anchors", [])
                and "NEWTON_EULER_DEFECT_OBLIGATION_GATE.md" in manifest.get("evidence_anchors", [])
                and "NEWTON_EULER_DEFECT_OBLIGATION_GATE.json" in manifest.get("evidence_anchors", [])
                and "NEWTON_EULER_VIRTUAL_WORK_WRENCH_AUDIT.md" in manifest.get("evidence_anchors", [])
                and "NEWTON_EULER_VIRTUAL_WORK_WRENCH_AUDIT.json" in manifest.get("evidence_anchors", [])
                and "NEWTON_EULER_AD_EXPANDED_ROW_ORACLE_AUDIT.md" in manifest.get("evidence_anchors", [])
                and "NEWTON_EULER_AD_EXPANDED_ROW_ORACLE_AUDIT.json" in manifest.get("evidence_anchors", [])
                and "B1_SYMBOLIC_ROW_ORACLE_CLOSURE_CERTIFICATE.md" in manifest.get("evidence_anchors", [])
                and "B1_SYMBOLIC_ROW_ORACLE_CLOSURE_CERTIFICATE.json" in manifest.get("evidence_anchors", [])
                and "B1_AD_EXPANDED_SYMBOLIC_ORACLE_CLOSURE_CERTIFICATE.md"
                in manifest.get("evidence_anchors", [])
                and "B1_AD_EXPANDED_SYMBOLIC_ORACLE_CLOSURE_CERTIFICATE.json"
                in manifest.get("evidence_anchors", [])
                and "README_CMAME_FLAT_SUBMISSION.md" in manifest.get("evidence_anchors", [])
                and "cmame_submission_flat/main_cmame_submission.tex" in manifest.get("evidence_anchors", [])
                and "cmame_submission_flat/main_cmame_submission.pdf" in manifest.get("evidence_anchors", [])
                and "cmame_submission_flat.zip" in manifest.get("evidence_anchors", [])
                and "main_concise.pdf" in manifest.get("evidence_anchors", [])
                and "PAPER_CLAIM_LEDGER.md" in manifest.get("evidence_anchors", [])
                and "PROOF_EVIDENCE_MATRIX.md" in manifest.get("evidence_anchors", [])
                and "PROOF_NUMERICAL_SCALE_AUDIT.md" in manifest.get("evidence_anchors", [])
                and "PROOF_NUMERICAL_SCALE_AUDIT.json" in manifest.get("evidence_anchors", [])
                and "PROOF_SOLVER_SCALE_AUDIT.md" in manifest.get("evidence_anchors", [])
                and "PROOF_SOLVER_SCALE_AUDIT.json" in manifest.get("evidence_anchors", [])
                and "PROOF_SOLVER_SCALED_TOLERANCE_PROBE.md" in manifest.get("evidence_anchors", [])
                and "PROOF_SOLVER_SCALED_TOLERANCE_PROBE.json" in manifest.get("evidence_anchors", [])
                and "PROOF_SOLVER_SCALED_TOLERANCE_PROBE.csv" in manifest.get("evidence_anchors", [])
                and "PROOF_SOLVER_SCALED_TOLERANCE_TRAJECTORY_PROBE.md" in manifest.get("evidence_anchors", [])
                and "PROOF_SOLVER_SCALED_TOLERANCE_TRAJECTORY_PROBE.json" in manifest.get("evidence_anchors", [])
                and "PROOF_SOLVER_SCALED_TOLERANCE_TRAJECTORY_PROBE.csv" in manifest.get("evidence_anchors", [])
                and "PROOF_SOLVER_TOLERANCE_REGIME_SWEEP.md" in manifest.get("evidence_anchors", [])
                and "PROOF_SOLVER_TOLERANCE_REGIME_SWEEP.json" in manifest.get("evidence_anchors", [])
                and "PROOF_SOLVER_TOLERANCE_REGIME_SWEEP.csv" in manifest.get("evidence_anchors", [])
                and "ORDER_ACCEPTANCE_GATE.md" in manifest.get("evidence_anchors", [])
                and "ORDER_ACCEPTANCE_GATE.json" in manifest.get("evidence_anchors", [])
                and "IMPLEMENTATION_PATH_AUDIT.md" in manifest.get("evidence_anchors", [])
                and "IMPLEMENTATION_PATH_AUDIT.json" in manifest.get("evidence_anchors", [])
                and "SOURCE_PAPER_COMPARISON.md" in manifest.get("evidence_anchors", [])
                and "CROSS_PAPER_BENCHMARK_MATRIX.md" in manifest.get("evidence_anchors", [])
                and "CROSS_PAPER_BENCHMARK_SPEC.md" in manifest.get("evidence_anchors", [])
                and "CROSS_PAPER_BENCHMARK_CASES.json" in manifest.get("evidence_anchors", [])
                and "EXTERNAL_SAME_TEST_RUN_QUEUE.md" in manifest.get("evidence_anchors", [])
                and "EXTERNAL_SAME_TEST_RUN_QUEUE.json" in manifest.get("evidence_anchors", [])
                and "KISSEL_NEGRUT_CODE_INVENTORY.md" in manifest.get("evidence_anchors", [])
                and "SOURCE_POLICY_CLOSURE_TRIAGE.md" in manifest.get("evidence_anchors", [])
                and "SOURCE_POLICY_CLOSURE_TRIAGE.json" in manifest.get("evidence_anchors", [])
                and "SOURCE_POLICY_ROW_CLOSURE_LEDGER.md" in manifest.get("evidence_anchors", [])
                and "SOURCE_POLICY_ROW_CLOSURE_LEDGER.json" in manifest.get("evidence_anchors", [])
                and "SOURCE_POLICY_LOCAL_CANDIDATE_GAP_AUDIT.md" in manifest.get("evidence_anchors", [])
                and "SOURCE_POLICY_LOCAL_CANDIDATE_GAP_AUDIT.json" in manifest.get("evidence_anchors", [])
                and "ALL_EXAMPLES_SOURCE_POLICY_AUDIT.md" in manifest.get("evidence_anchors", [])
                and "ALL_EXAMPLES_SOURCE_POLICY_AUDIT.json" in manifest.get("evidence_anchors", [])
                and "EXTERNAL_SUITE_DISPOSITION_AUDIT.md" in manifest.get("evidence_anchors", [])
                and "EXTERNAL_SUITE_DISPOSITION_AUDIT.json" in manifest.get("evidence_anchors", [])
                and "EXTERNAL_SOURCE_POLICY_CLOSURE_MANIFEST.md" in manifest.get("evidence_anchors", [])
                and "EXTERNAL_SOURCE_POLICY_CLOSURE_MANIFEST.json" in manifest.get("evidence_anchors", [])
                and "EXTERNAL_CASE_EVIDENCE_RECONCILIATION.md" in manifest.get("evidence_anchors", [])
                and "EXTERNAL_CASE_EVIDENCE_RECONCILIATION.json" in manifest.get("evidence_anchors", [])
                and "VP2024_CODE_PATH_DISPOSITION_AUDIT.md" in manifest.get("evidence_anchors", [])
                and "VP2024_CODE_PATH_DISPOSITION_AUDIT.json" in manifest.get("evidence_anchors", [])
                and "RA2021_SOURCE_IDENTITY_AUDIT.md" in manifest.get("evidence_anchors", [])
                and "RA2021_SOURCE_IDENTITY_AUDIT.json" in manifest.get("evidence_anchors", [])
                and "HI2022_POLICY_DECISION_AUDIT.md" in manifest.get("evidence_anchors", [])
                and "HI2022_POLICY_DECISION_AUDIT.json" in manifest.get("evidence_anchors", [])
                and "HI2022_SOURCE_POLICY_ROW_AUDIT.md" in manifest.get("evidence_anchors", [])
                and "HI2022_SOURCE_POLICY_ROW_AUDIT.json" in manifest.get("evidence_anchors", [])
                and "HI2022_T8_TOLERANCE_REPAIR_AUDIT.md" in manifest.get("evidence_anchors", [])
                and "HI2022_T8_TOLERANCE_REPAIR_AUDIT.json" in manifest.get("evidence_anchors", [])
                and "B4_SOURCE_POLICY_EXECUTION_HANDOFF_PACKAGE.md" in manifest.get("evidence_anchors", [])
                and "B4_SOURCE_POLICY_EXECUTION_HANDOFF_PACKAGE.json" in manifest.get("evidence_anchors", [])
                and "B4_SOURCE_POLICY_COMMAND_PREFLIGHT_FREEZE_20260620.md" in manifest.get("evidence_anchors", [])
                and "B4_SOURCE_POLICY_COMMAND_PREFLIGHT_FREEZE_20260620.json" in manifest.get("evidence_anchors", [])
                and "B4_SOURCE_POLICY_EXPECTED_OUTPUT_SCHEMA_AUDIT_20260620.md" in manifest.get("evidence_anchors", [])
                and "B4_SOURCE_POLICY_EXPECTED_OUTPUT_SCHEMA_AUDIT_20260620.json" in manifest.get("evidence_anchors", [])
                and "B4_EXPECTED_OUTPUT_PROMOTION_READINESS_BLOCKER_AUDIT_20260620.md" in manifest.get("evidence_anchors", [])
                and "B4_EXPECTED_OUTPUT_PROMOTION_READINESS_BLOCKER_AUDIT_20260620.json" in manifest.get("evidence_anchors", [])
                and "OC6_SOURCE_EQUIVALENT_REOPEN_READINESS_AUDIT_20260620.md" in manifest.get("evidence_anchors", [])
                and "OC6_SOURCE_EQUIVALENT_REOPEN_READINESS_AUDIT_20260620.json" in manifest.get("evidence_anchors", [])
                and "FULL_SOURCE_POLICY_RUNNER_ARCHIVE_GAP_AUDIT.md" in manifest.get("evidence_anchors", [])
                and "FULL_SOURCE_POLICY_RUNNER_ARCHIVE_GAP_AUDIT.json" in manifest.get("evidence_anchors", [])
                and "SOURCE_POLICY_REOPEN_CONDITION_MONITOR_20260620.md" in manifest.get("evidence_anchors", [])
                and "SOURCE_POLICY_REOPEN_CONDITION_MONITOR_20260620.json" in manifest.get("evidence_anchors", [])
                and "TFE_SOURCE_POLICY_SPEC.md" in manifest.get("evidence_anchors", [])
                and "TFE_SOURCE_POLICY_SPEC.json" in manifest.get("evidence_anchors", [])
                and "TFE_SOURCE_POLICY_ROW_AUDIT.md" in manifest.get("evidence_anchors", [])
                and "TFE_SOURCE_POLICY_ROW_AUDIT.json" in manifest.get("evidence_anchors", [])
                and "TFE_B4_B7_SOURCE_POLICY_DEMOTION_AUDIT.md" in manifest.get("evidence_anchors", [])
                and "TFE_B4_B7_SOURCE_POLICY_DEMOTION_AUDIT.json" in manifest.get("evidence_anchors", [])
                and "TFE_SOURCE_PENDULUM_MODEL_AUDIT.md" in manifest.get("evidence_anchors", [])
                and "TFE_SOURCE_PENDULUM_MODEL_AUDIT.json" in manifest.get("evidence_anchors", [])
                and "TFE_BROWN_MCPHEE_SOURCE_LAW_BOUNDARY_AUDIT.md" in manifest.get("evidence_anchors", [])
                and "TFE_BROWN_MCPHEE_SOURCE_LAW_BOUNDARY_AUDIT.json" in manifest.get("evidence_anchors", [])
                and "TFE_SOURCE_GRID_COMPATIBILITY_AUDIT.md" in manifest.get("evidence_anchors", [])
                and "TFE_SOURCE_GRID_COMPATIBILITY_AUDIT.json" in manifest.get("evidence_anchors", [])
                and "TFE_ENDPOINT_POLICY_BOUNDARY_CERTIFICATE.md" in manifest.get("evidence_anchors", [])
                and "TFE_ENDPOINT_POLICY_BOUNDARY_CERTIFICATE.json" in manifest.get("evidence_anchors", [])
                and "TFE_ENDPOINT_POLICY_BOUNDARY_CERTIFICATE.csv" in manifest.get("evidence_anchors", [])
                and "TFE_ENDPOINT_POLICY_SENSITIVITY_AUDIT.md" in manifest.get("evidence_anchors", [])
                and "TFE_ENDPOINT_POLICY_SENSITIVITY_AUDIT.json" in manifest.get("evidence_anchors", [])
                and "TFE_ENDPOINT_POLICY_SENSITIVITY_AUDIT.csv" in manifest.get("evidence_anchors", [])
                and "OBJECTIVE_COMPLETION_AUDIT.md" in manifest.get("evidence_anchors", [])
                and "OBJECTIVE_COMPLETION_AUDIT.json" in manifest.get("evidence_anchors", [])
                and "COMPARISON_OBJECTIVE_CLOSURE_RECONCILIATION_AUDIT.md" in manifest.get("evidence_anchors", [])
                and "COMPARISON_OBJECTIVE_CLOSURE_RECONCILIATION_AUDIT.json" in manifest.get("evidence_anchors", [])
                and "PAPER_NUMERICAL_RESULT_MATRIX.md" in manifest.get("evidence_anchors", [])
                and "PAPER_NUMERICAL_RESULT_MATRIX.json" in manifest.get("evidence_anchors", [])
                and "PAPER_NUMERICAL_RESULT_MATRIX.csv" in manifest.get("evidence_anchors", [])
                and "RESULT_TO_MANUSCRIPT_TRACEABILITY_AUDIT.md" in manifest.get("evidence_anchors", [])
                and "RESULT_TO_MANUSCRIPT_TRACEABILITY_AUDIT.json" in manifest.get("evidence_anchors", [])
                and "ALL_METHOD_EXAMPLE_CLAIM_DISPOSITION_AUDIT.md" in manifest.get("evidence_anchors", [])
                and "ALL_METHOD_EXAMPLE_CLAIM_DISPOSITION_AUDIT.json" in manifest.get("evidence_anchors", [])
                and "REVIEWER_CHECKLIST.md" in manifest.get("evidence_anchors", [])
                and "CURRENT_PIPELINE_CONTRACT.md" in manifest.get("evidence_anchors", [])
            )
            if not submission_manifest_ok:
                submission_manifest_error = "SUBMISSION_ARTIFACT_MANIFEST.json has unexpected submission-boundary values"
        except Exception as exc:  # noqa: BLE001 - command-line wrapper reports parse failures.
            submission_manifest_error = f"SUBMISSION_ARTIFACT_MANIFEST.json parse failed: {exc}"

    submission_packet_path = PAPER / "SUBMISSION_PACKET.md"
    if submission_packet_path.exists():
        submission_packet_text = submission_packet_path.read_text(
            encoding="utf-8", errors="replace"
        )
        submission_packet_ok = all(
            contains_normalized(submission_packet_text, token)
            for token in [
                "top-level review status is **do not submit globally yet**",
                "Full source-policy package remains not ready",
                "Narrowed archive boundary blocking ids/status",
                "`OC4,OC6,OC12` / `OC4=open,OC6=partial,OC12=partial`",
                "Objective completion blocker matrix",
                "blocker_open_by_id=OC4:True,OC6:True,OC12:True",
                "blocker_closure_decision_by_id=OC4:remain_open_ready_for_authorized_execution_not_executed_not_promoted,OC6:remain_open_no_positive_source_equivalent_artifact,OC12:remain_partial_narrowed_replay_ready_full_source_policy_archive_not_ready",
                "blocker_closure_allowed_by_id=OC4:False,OC6:False,OC12:False",
                "recorded global blockers remain open",
                "not a submission-ready signal",
                "`narrowed_claim_only`, not a full source-policy runner archive",
            ]
        )
        if not submission_packet_ok:
            submission_packet_error = "SUBMISSION_PACKET.md has unexpected objective blocker boundary values"

    cover_path = PAPER / "COVER_LETTER.md"
    if cover_path.exists():
        cover_text = cover_path.read_text(encoding="utf-8", errors="replace")
        cover_letter_ok = all(
            contains_normalized(cover_text, token)
            for token in [
                "Cover Letter Draft",
                "main_cmame.pdf",
                "main_cmame.tex",
                "highlights_cmame.txt",
                "declarations_cmame.md",
                "A Conditional Sixth-Order Lie-Group FullVA Integrator for Lower-Pair Mechanisms",
                "`Gauss6/FullVA`",
                "`7.161/7.066`",
                "`single_pendulum`",
                "`double_pendulum`",
                "`four_link`",
                "`slider_crank`",
                "`m=3` Gauss-Lobatto TFE formula target",
                "expected order `5`",
                "bounded formal-order comparison",
                "PROOF_EVIDENCE_MATRIX.md",
                "ORDER_ACCEPTANCE_GATE.md",
                "SOURCE_PAPER_COMPARISON.md",
                "`full_tfe_stage_replacement=false`",
                "does not claim complete source-paper residual reproduction",
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
                "narrowed archive boundary matches the reproducibility manifest: `True`",
                "`narrowed_archive_ready_not_full_source_policy_runner_archive/0/40/False/False/True`",
                "blocking ids/status `OC4,OC6,OC12`",
                "`OC4=open,OC6=partial,OC12=partial`",
                "`narrowed_claim_only`, not a full source-policy runner archive",
                "objective completion blocker matrix remains",
                "blocker_open_by_id=OC4:True,OC6:True,OC12:True",
                "blocker_closure_decision_by_id=OC4:remain_open_ready_for_authorized_execution_not_executed_not_promoted,OC6:remain_open_no_positive_source_equivalent_artifact,OC12:remain_partial_narrowed_replay_ready_full_source_policy_archive_not_ready",
                "blocker_closure_allowed_by_id=OC4:False,OC6:False,OC12:False",
                "do not invoke `run_v047.py`",
            ]
        )
        if not cover_letter_ok:
            cover_letter_error = "COVER_LETTER.md has unexpected claim-boundary values"

    inventory_path = PAPER / "SUBMISSION_FILE_INVENTORY.md"
    if inventory_path.exists():
        inventory_text = inventory_path.read_text(encoding="utf-8", errors="replace")
        file_inventory_ok = all(
            contains_normalized(inventory_text, token)
            for token in [
                "Submission File Inventory",
                "Primary Submission Files",
                "Supporting Evidence Files",
                "Validators",
                "Accepted Claim Snapshot",
                "Non-Claims",
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
                "`CMAME_PROOF_CONTRACT_GATE.md`",
                "`CMAME_PROOF_CONTRACT_GATE.json`",
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
                "`CMAME_VISUAL_LEGIBILITY_AUDIT.md`",
                "`CMAME_VISUAL_LEGIBILITY_AUDIT.json`",
                "`CMAME_FIGURE_SET_AUDIT.md`",
                "`CMAME_FIGURE_SET_AUDIT.json`",
                "`CMAME_RELATED_WORK_AUDIT.md`",
                "`CMAME_RELATED_WORK_AUDIT.json`",
                "`CMAME_PROSE_RESIDUE_AUDIT.md`",
                "`CMAME_PROSE_RESIDUE_AUDIT.json`",
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
                "objective completion matrix remains `blocker_open_by_id=OC4:True,OC6:True,OC12:True`",
                "`blocker_closure_allowed_by_id=OC4:False,OC6:False,OC12:False`",
                "`OBJECTIVE_COMPLETION_AUDIT.md`",
                "`OBJECTIVE_COMPLETION_AUDIT.json`",
                "Objective-level completion audit showing `objective_complete=false`",
                "central blocker matrix `blocker_open_by_id=OC4:True,OC6:True,OC12:True`",
                "blocker_closure_decision_by_id=OC4:remain_open_ready_for_authorized_execution_not_executed_not_promoted,OC6:remain_open_no_positive_source_equivalent_artifact,OC12:remain_partial_narrowed_replay_ready_full_source_policy_archive_not_ready",
                "`blocker_closure_allowed_by_id=OC4:False,OC6:False,OC12:False`",
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
                "`COVER_LETTER.md`",
                "`SUBMISSION_PACKET.md`",
                "`SUBMISSION_ARTIFACT_MANIFEST.json`",
                "`SUBMISSION_FILE_INVENTORY.md`",
                "`REVIEW_RESPONSE_TEMPLATE.md`",
                "`CLAIM_BOUNDARY.json`",
                "`main.pdf`",
                "`PROOF_EVIDENCE_MATRIX.md`",
                "`CMAME_BLOCKER_CLOSURE_GATE.md`",
                "`CMAME_BLOCKER_CLOSURE_GATE.json`",
                "`CMAME_EXTERNAL_BASELINE_GATE.md`",
                "`CMAME_EXTERNAL_BASELINE_GATE.json`",
                "`CMAME_PROOF_CONTRACT_GATE.md`",
                "`CMAME_PROOF_CONTRACT_GATE.json`",
                "`PROOF_NUMERICAL_SCALE_AUDIT.md`",
                "`PROOF_NUMERICAL_SCALE_AUDIT.json`",
                "`PROOF_SOLVER_SCALE_AUDIT.md`",
                "`PROOF_SOLVER_SCALE_AUDIT.json`",
                "`PROOF_SOLVER_SCALED_TOLERANCE_PROBE.md`",
                "`PROOF_SOLVER_SCALED_TOLERANCE_PROBE.json`",
                "`PROOF_SOLVER_SCALED_TOLERANCE_TRAJECTORY_PROBE.md`",
                "`PROOF_SOLVER_SCALED_TOLERANCE_TRAJECTORY_PROBE.json`",
                "`PROOF_SOLVER_SCALED_TOLERANCE_TRAJECTORY_PROBE.csv`",
                "`PROOF_SOLVER_TOLERANCE_REGIME_SWEEP.md`",
                "`PROOF_SOLVER_TOLERANCE_REGIME_SWEEP.json`",
                "`PROOF_SOLVER_TOLERANCE_REGIME_SWEEP.csv`",
                "`CMAME_VISUAL_LEGIBILITY_AUDIT.md`",
                "`CMAME_VISUAL_LEGIBILITY_AUDIT.json`",
                "`CMAME_RELATED_WORK_AUDIT.md`",
                "`CMAME_RELATED_WORK_AUDIT.json`",
                "`DYNAMIC_ROW_ORACLE_GATE.md`",
                "`DYNAMIC_ROW_ORACLE_GATE.json`",
                "`NEWTON_EULER_DEFECT_OBLIGATION_GATE.md`",
                "`NEWTON_EULER_DEFECT_OBLIGATION_GATE.json`",
                "`D5_PRIMITIVE_BOUND_REDUCTION_AUDIT.md`",
                "`D5_PRIMITIVE_BOUND_REDUCTION_AUDIT.json`",
                "`D5_P_TUBE_CONSTANTS_AUDIT.md`",
                "`D5_P_TUBE_CONSTANTS_AUDIT.json`",
                "`D5_P_STATE_LIFT_GAP_AUDIT.md`",
                "`D5_P_STATE_LIFT_GAP_AUDIT.json`",
                "`D5_P_STATE_MAP_DEFINITION_AUDIT.md`",
                "`D5_P_STATE_MAP_DEFINITION_AUDIT.json`",
                "`D5_P_STATE_ANTICIRCULARITY_AUDIT.md`",
                "`D5_P_STATE_ANTICIRCULARITY_AUDIT.json`",
                "`D5_P_STATE_PS2_WEIGHTED_TARGET_AUDIT.md`",
                "`D5_P_STATE_PS2_WEIGHTED_TARGET_AUDIT.json`",
                "`D5_P_STATE_PS2_AGGREGATE_PROMOTION_AUDIT.md`",
                "`D5_P_STATE_PS2_AGGREGATE_PROMOTION_AUDIT.json`",
                "`D5_P_STATE_PS2_LINEARIZATION_PROBE.md`",
                "`D5_P_STATE_PS2_LINEARIZATION_PROBE.json`",
                "`D5_P_STATE_PS2_LINEARIZATION_PROBE.csv`",
                "`D5_P_STATE_PS3_CONDITIONAL_CONVERSION_AUDIT.md`",
                "`D5_P_STATE_PS3_CONDITIONAL_CONVERSION_AUDIT.json`",
                "`D5_P_STATE_PS3_ACTUAL_INSTANTIATION_GAP_AUDIT.md`",
                "`D5_P_STATE_PS3_ACTUAL_INSTANTIATION_GAP_AUDIT.json`",
                "`D5_P_STATE_PS3_H_ACC_INPUT_OBSTRUCTION_AUDIT.md`",
                "`D5_P_STATE_PS3_H_ACC_INPUT_OBSTRUCTION_AUDIT.json`",
                "`D5_P_ACC_MAP_DEFINITION_AUDIT.md`",
                "`D5_P_ACC_MAP_DEFINITION_AUDIT.json`",
                "`D5_P_ACC_ROW_BINDING_AUDIT.md`",
                "`D5_P_ACC_ROW_BINDING_AUDIT.json`",
                "`D5_P_ACC_INDEPENDENCE_AUDIT.md`",
                "`D5_P_ACC_INDEPENDENCE_AUDIT.json`",
                "`D5_P_ACC_LIFT_OBSTRUCTION_AUDIT.md`",
                "`D5_P_ACC_LIFT_OBSTRUCTION_AUDIT.json`",
                "`D5_P_ACC_PA2_WEIGHTED_INVERSE_AUDIT.md`",
                "`D5_P_ACC_PA2_WEIGHTED_INVERSE_AUDIT.json`",
                "`D5_P_LAMBDA_INTERFACE_AUDIT.md`",
                "`D5_P_LAMBDA_INTERFACE_AUDIT.json`",
                "`D5_P_LAMBDA_INF_SUP_PROBE.md`",
                "`D5_P_LAMBDA_INF_SUP_PROBE.json`",
                "`D5_P_LAMBDA_INF_SUP_PROBE.csv`",
                "`D5_P_LAMBDA_PL2_GEOMETRIC_MARGIN_AUDIT.md`",
                "`D5_P_LAMBDA_PL2_GEOMETRIC_MARGIN_AUDIT.json`",
                "`D5_P_LAMBDA_D3_NONCIRCULARITY_AUDIT.md`",
                "`D5_P_LAMBDA_D3_NONCIRCULARITY_AUDIT.json`",
                "`D5_P_LAMBDA_PL4_RATE_PROPAGATION_AUDIT.md`",
                "`D5_P_LAMBDA_PL4_RATE_PROPAGATION_AUDIT.json`",
                "`D5_P_GEOM_CHART_REDUCTION_AUDIT.md`",
                "`D5_P_GEOM_CHART_REDUCTION_AUDIT.json`",
                "`D5_P_GYRO_BILINEAR_REDUCTION_AUDIT.md`",
                "`D5_P_GYRO_BILINEAR_REDUCTION_AUDIT.json`",
                "`D5_OPEN_PRIMITIVE_GAP_AUDIT.md`",
                "`D5_OPEN_PRIMITIVE_GAP_AUDIT.json`",
                "`D5_PRIMITIVE_OBLIGATION_CLOSURE_PLAN.md`",
                "`D5_PRIMITIVE_OBLIGATION_CLOSURE_PLAN.json`",
                "`D5_CONDITIONAL_TAYLOR_CERTIFICATE.md`",
                "`D5_CONDITIONAL_TAYLOR_CERTIFICATE.json`",
                "`ORDER_ACCEPTANCE_GATE.md`",
                "`ORDER_ACCEPTANCE_GATE.json`",
                "`IMPLEMENTATION_PATH_AUDIT.md`",
                "`IMPLEMENTATION_PATH_AUDIT.json`",
                "`SOURCE_PAPER_COMPARISON.md`",
                "`CROSS_PAPER_BENCHMARK_MATRIX.md`",
                "`CROSS_PAPER_BENCHMARK_SPEC.md`",
                "`CROSS_PAPER_BENCHMARK_CASES.json`",
                "`EXTERNAL_SAME_TEST_RUN_QUEUE.md`",
                "`EXTERNAL_SAME_TEST_RUN_QUEUE.json`",
                "`KISSEL_NEGRUT_CODE_INVENTORY.md`",
                "`EXTERNAL_SUITE_DISPOSITION_AUDIT.md`",
                "`EXTERNAL_SUITE_DISPOSITION_AUDIT.json`",
                "`SOURCE_POLICY_LOCAL_CANDIDATE_GAP_AUDIT.md`",
                "`SOURCE_POLICY_LOCAL_CANDIDATE_GAP_AUDIT.json`",
                "`VP2024_CODE_PATH_DISPOSITION_AUDIT.md`",
                "`VP2024_CODE_PATH_DISPOSITION_AUDIT.json`",
                "`RESULT_TO_MANUSCRIPT_TRACEABILITY_AUDIT.md`",
                "`RESULT_TO_MANUSCRIPT_TRACEABILITY_AUDIT.json`",
                "`ALL_METHOD_EXAMPLE_CLAIM_DISPOSITION_AUDIT.md`",
                "`ALL_METHOD_EXAMPLE_CLAIM_DISPOSITION_AUDIT.json`",
                "`COMPARISON_OBJECTIVE_CLOSURE_RECONCILIATION_AUDIT.md`",
                "`COMPARISON_OBJECTIVE_CLOSURE_RECONCILIATION_AUDIT.json`",
                "`PAPER_CLAIM_LEDGER.md`",
                "`REVIEWER_CHECKLIST.md`",
                "`CURRENT_STATUS_CN.md`",
                "`../CURRENT_PIPELINE_CONTRACT.md`",
                "`../v047_cylindrical_chain_pipeline/results/summary_v047.json`",
                "`validate_cmame_submission.py`",
                "`validate_cmame_submission_integrity_audit.py`",
                "`validate_cmame_blocker_closure_gate.py`",
                "`validate_cmame_external_baseline_gate.py`",
                "`validate_cmame_proof_contract_gate.py`",
                "`validate_cmame_visual_legibility_audit.py`",
                "`validate_cmame_related_work_audit.py`",
                "`validate_cmame_prose_residue_audit.py`",
                "`validate_dynamic_row_oracle_gate.py`",
                "`validate_newton_euler_defect_obligation_gate.py`",
                "`validate_d5_primitive_bound_reduction_audit.py`",
                "`validate_d5_p_tube_constants_audit.py`",
                "`validate_d5_p_state_lift_gap_audit.py`",
                "`validate_d5_p_state_map_definition_audit.py`",
                "`validate_d5_p_state_anticircularity_audit.py`",
                "`validate_d5_p_state_ps2_weighted_target_audit.py`",
                "`validate_d5_p_state_ps2_aggregate_promotion_audit.py`",
                "`validate_d5_p_state_ps2_linearization_probe.py`",
                "`validate_d5_p_state_ps3_conditional_conversion_audit.py`",
                "`validate_d5_p_state_ps3_actual_instantiation_gap_audit.py`",
                "`validate_d5_p_state_ps3_h_acc_input_obstruction_audit.py`",
                "`validate_d5_p_acc_map_definition_audit.py`",
                "`validate_d5_p_acc_row_binding_audit.py`",
                "`validate_d5_p_acc_independence_audit.py`",
                "`validate_d5_p_acc_lift_obstruction_audit.py`",
                "`validate_d5_dynamic_direct_substitution_certificate.py`",
                "`validate_d5_p_lambda_interface_audit.py`",
                "`validate_d5_p_lambda_inf_sup_probe.py`",
                "`validate_d5_p_lambda_d3_noncircularity_audit.py`",
                "`validate_d5_open_primitive_gap_audit.py`",
                "`validate_d5_primitive_obligation_closure_plan.py`",
                "`validate_d5_conditional_taylor_certificate.py`",
                "`validate_concise_paper.py`",
                "`validate_paper_claims.py`",
                "`validate_proof_evidence_matrix.py`",
                "`validate_proof_numerical_scale_audit.py`",
                "`validate_proof_solver_scale_audit.py`",
                "`validate_proof_solver_scaled_tolerance_probe.py`",
                "`validate_proof_solver_scaled_tolerance_trajectory_probe.py`",
                "`validate_proof_solver_tolerance_regime_sweep.py`",
                "`validate_order_acceptance_gate.py`",
                "`validate_source_paper_comparison.py`",
                "`validate_implementation_path_audit.py`",
                "`validate_cross_paper_benchmark_spec.py`",
                "`validate_cross_paper_benchmark_cases.py`",
                "`validate_external_same_test_run_queue.py`",
                "`validate_external_suite_disposition_audit.py`",
                "`validate_source_policy_local_candidate_gap_audit.py`",
                "`validate_vp2024_code_path_disposition_audit.py`",
                "`validate_result_to_manuscript_traceability_audit.py`",
                "`validate_all_method_example_claim_disposition_audit.py`",
                "`validate_comparison_objective_closure_reconciliation_audit.py`",
                "`validate_submission_bundle.py`",
                "`validate_paper_package.py`",
                "`../validate_pipeline_outputs.py`",
                "`Gauss6/FullVA`",
                "`7.161/7.066`",
                "`m=3` Gauss-Lobatto TFE formula target",
                "`single_pendulum`",
                "`double_pendulum`",
                "`four_link`",
                "`slider_crank`",
                "`full_tfe_stage_replacement=false`",
                "must not invoke `run_v047.py`",
            ]
        )
        file_inventory_ok = file_inventory_ok and "theorem closure still false" not in inventory_text
        if not file_inventory_ok:
            file_inventory_error = "SUBMISSION_FILE_INVENTORY.md has unexpected submission inventory values"

    review_path = PAPER / "REVIEW_RESPONSE_TEMPLATE.md"
    if review_path.exists():
        review_text = review_path.read_text(encoding="utf-8", errors="replace")
        review_response_ok = all(
            contains_normalized(review_text, token)
            for token in [
                "Reviewer Response Template",
                "What Is The Main Claim?",
                "`Gauss6/FullVA`",
                "method-order claim `6`",
                "`7.161/7.066`",
                "`m=3` Gauss-Lobatto TFE formula target",
                "expected order `5`",
                "PROOF_EVIDENCE_MATRIX.md",
                "ORDER_ACCEPTANCE_GATE.md",
                "SOURCE_PAPER_COMPARISON.md",
                "`2m-1=5`",
                "`full_tfe_stage_replacement=false`",
                "Why Is Full-TFE Replacement Not Required For The Main Claim?",
                "132 Gauss/FullVA stage rows",
                "What Are The Four Validated Examples?",
                "`single_pendulum`",
                "`double_pendulum`",
                "`four_link`",
                "`slider_crank`",
                "`single_absolute_min_order=6.024`",
                "`double_method_min_order=6.089`",
                "`four_link_closed_loop_max_constraint_norm=1.052e-14`",
                "`slider_crank_reaction_max_dynamics_residual=6.492e-15`",
                "What Remains Open?",
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
                "`sparse_speed_quantified`",
                "`full_tfe_stage_replacement_missing`",
                "`sharp_friction_coarse_order_reduction_ultra_recovered`",
                "How Can The Claims Be Reproduced?",
                "do not invoke the full",
                "`run_v047.py`",
                "What Should Not Be Claimed?",
                "complete source-paper residual reproduction",
                "accepted independent full-TFE stage replacement",
                "blocker_open_by_id=OC4:True,OC6:True,OC12:True",
                "blocker_closure_decision_by_id=OC4:remain_open_ready_for_authorized_execution_not_executed_not_promoted,OC6:remain_open_no_positive_source_equivalent_artifact,OC12:remain_partial_narrowed_replay_ready_full_source_policy_archive_not_ready",
                "blocker_closure_allowed_by_id=OC4:False,OC6:False,OC12:False",
            ]
        )
        if not review_response_ok:
            review_response_error = "REVIEW_RESPONSE_TEMPLATE.md has unexpected claim-boundary values"

    boundary_doc_tokens = [
        "narrowed archive boundary matches the reproducibility manifest: `True`",
        "`narrowed_archive_ready_not_full_source_policy_runner_archive/0/40/False/False/True`",
        "`OC4=open,OC6=partial,OC12=partial`",
        "`narrowed_claim_only`, not a full source-policy runner archive",
        "blocker_open_by_id=OC4:True,OC6:True,OC12:True",
        "blocker_closure_decision_by_id=OC4:remain_open_ready_for_authorized_execution_not_executed_not_promoted,OC6:remain_open_no_positive_source_equivalent_artifact,OC12:remain_partial_narrowed_replay_ready_full_source_policy_archive_not_ready",
        "blocker_closure_allowed_by_id=OC4:False,OC6:False,OC12:False",
    ]
    boundary_doc_paths = [
        "declarations_cmame.md",
        "cmame_submission_flat/declarations_cmame.md",
        "README_CMAME_FLAT_SUBMISSION.md",
        "CMAME_SUBMISSION_CHECKLIST.md",
        "REVIEWER_CHECKLIST.md",
        "CURRENT_STATUS_CN.md",
        "COVER_LETTER.md",
    ]
    boundary_doc_missing: list[str] = []
    for rel_path in boundary_doc_paths:
        path = PAPER / rel_path
        text = path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""
        for token in boundary_doc_tokens:
            if not contains_normalized(text, token):
                boundary_doc_missing.append(f"{rel_path}: {token}")
    boundary_docs_ok = not boundary_doc_missing
    if not boundary_docs_ok:
        boundary_docs_error = "archive-boundary docs missing tokens: " + "; ".join(boundary_doc_missing)

    global_blocker_matrix_doc_tokens = [
        "blocker_open_by_id=OC4:True,OC6:True,OC12:True",
        "blocker_closure_decision_by_id=OC4:remain_open_ready_for_authorized_execution_not_executed_not_promoted,OC6:remain_open_no_positive_source_equivalent_artifact,OC12:remain_partial_narrowed_replay_ready_full_source_policy_archive_not_ready",
        "blocker_closure_allowed_by_id=OC4:False,OC6:False,OC12:False",
        "does not authorize B4/source-policy execution",
    ]
    global_blocker_matrix_doc_paths = [
        "CMAME_SUBMISSION_READINESS_AUDIT.md",
        "CMAME_SUBMISSION_READINESS_REVIEW.md",
        "CMAME_BLOCKER_CLOSURE_GATE.md",
        "CMAME_EXTERNAL_BASELINE_GATE.md",
        "CMAME_PROOF_CONTRACT_GATE.md",
        "CMAME_VISUAL_LEGIBILITY_AUDIT.md",
        "CMAME_RELATED_WORK_AUDIT.md",
        "CMAME_PROSE_RESIDUE_AUDIT.md",
    ]
    global_blocker_matrix_doc_missing: list[str] = []
    for rel_path in global_blocker_matrix_doc_paths:
        path = PAPER / rel_path
        text = path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""
        for token in global_blocker_matrix_doc_tokens:
            if not contains_normalized(text, token):
                global_blocker_matrix_doc_missing.append(f"{rel_path}: {token}")
    global_blocker_matrix_docs_ok = not global_blocker_matrix_doc_missing
    if not global_blocker_matrix_docs_ok:
        global_blocker_matrix_docs_error = (
            "global blocker matrix docs missing tokens: "
            + "; ".join(global_blocker_matrix_doc_missing)
        )

    print("[", end="")
    if (
        missing
        or not boundary_ok
        or not contract_ok
        or not submission_manifest_ok
        or not submission_packet_ok
        or not cover_letter_ok
        or not file_inventory_ok
        or not review_response_ok
        or not boundary_docs_ok
        or not global_blocker_matrix_docs_ok
    ):
        print("FAIL] package required files")
        for name in missing:
            print(f"  missing_or_empty={name}")
        if boundary_error:
            print(f"  {boundary_error}")
        if contract_error:
            print(f"  {contract_error}")
        if submission_manifest_error:
            print(f"  {submission_manifest_error}")
        if submission_packet_error:
            print(f"  {submission_packet_error}")
        if cover_letter_error:
            print(f"  {cover_letter_error}")
        if file_inventory_error:
            print(f"  {file_inventory_error}")
        if review_response_error:
            print(f"  {review_response_error}")
        if boundary_docs_error:
            print(f"  {boundary_docs_error}")
        if not global_blocker_matrix_docs_ok:
            print(f"  {global_blocker_matrix_docs_error}")
        return False

    print("PASS] package required files")
    print("  CLAIM_BOUNDARY.json schema=v047-paper-claim-boundary-v1")
    print("  CLAIM_BOUNDARY.json asme_acceptance=four_examples_quantitative")
    print("  CLAIM_BOUNDARY.json full_tfe_gap_contract=quantified_not_accepted")
    print("  CLAIM_BOUNDARY.json remaining_caveat_contracts=sparse_speed_and_sharp_friction")
    print("  CLAIM_BOUNDARY.json terminology=tfe/fte/full_tfe_replacement")
    print("  CLAIM_BOUNDARY.json order_conventions=accepted6_observed7p161_7p066_comparator5")
    print("  CURRENT_PIPELINE_CONTRACT.md current_pipeline_boundary=checked")
    print("  CMAME_SUBMISSION_READINESS_REVIEW.md quality_review=checked")
    print("  CMAME_PDF_STYLE_REVIEW_AUDIT.md pdf_style_review=checked")
    print("  CMAME_SUBMISSION_INTEGRITY_AUDIT.md submission_integrity_audit=checked")
    print("  CMAME_BLOCKER_CLOSURE_GATE.md blocker_closure_gate=checked")
    print("  CMAME_EXTERNAL_BASELINE_GATE.md external_baseline_gate=checked")
    print("  CMAME_PROOF_CONTRACT_GATE.md proof_contract_gate=checked")
    print("  CMAME_SCALABILITY_BOUNDARY_AUDIT.md scalability_boundary_audit=checked")
    print("  PROOF_CLOSURE_MANIFEST.md proof_closure_manifest=checked")
    print("  PROOF_CLAIM_TRACEABILITY_AUDIT.md proof_claim_traceability_audit=checked")
    print("  D5_DYNAMIC_DEFECT_READINESS_AUDIT.md d5_dynamic_defect_readiness_audit=checked")
    print("  D5_DYNAMIC_DIRECT_SUBSTITUTION_CERTIFICATE.md d5_dynamic_direct_substitution_certificate=checked")
    print("  D5_TAYLOR_TERM_BUDGET_AUDIT.md d5_taylor_term_budget_audit=checked")
    print("  D5_PRIMITIVE_BOUND_REDUCTION_AUDIT.md d5_primitive_bound_reduction_audit=checked")
    print("  D5_P_TUBE_CONSTANTS_AUDIT.md d5_p_tube_constants_audit=checked")
    print("  D5_P_STATE_LIFT_GAP_AUDIT.md d5_p_state_lift_gap_audit=checked")
    print("  D5_P_STATE_MAP_DEFINITION_AUDIT.md d5_p_state_map_definition_audit=checked")
    print("  D5_P_STATE_ANTICIRCULARITY_AUDIT.md d5_p_state_anticircularity_audit=checked")
    print("  D5_P_STATE_PS2_WEIGHTED_TARGET_AUDIT.md d5_p_state_ps2_weighted_target_audit=checked")
    print("  D5_P_STATE_PS2_KINEMATIC_BLOCK_CERTIFICATE.md d5_p_state_ps2_kinematic_block_certificate=checked")
    print("  D5_P_STATE_PS2_LIE_CHART_BINDING_AUDIT.md d5_p_state_ps2_lie_chart_binding_audit=checked")
    print("  D5_P_STATE_PS2_ROW_INJECTION_AUDIT.md d5_p_state_ps2_row_injection_audit=checked")
    print("  D5_P_STATE_PS2_NONLINEAR_BINDING_AUDIT.md d5_p_state_ps2_nonlinear_binding_audit=checked")
    print("  D5_P_STATE_PS2_AGGREGATE_PROMOTION_AUDIT.md d5_p_state_ps2_aggregate_promotion_audit=checked")
    print("  D5_P_STATE_PS2_LINEARIZATION_PROBE.md d5_p_state_ps2_linearization_probe=checked")
    print("  D5_P_STATE_PS3_CONDITIONAL_CONVERSION_AUDIT.md d5_p_state_ps3_conditional_conversion_audit=checked")
    print("  D5_P_STATE_PS3_ACTUAL_INSTANTIATION_GAP_AUDIT.md d5_p_state_ps3_actual_instantiation_gap_audit=checked")
    print("  D5_P_STATE_PS3_H_ACC_INPUT_OBSTRUCTION_AUDIT.md d5_p_state_ps3_h_acc_input_obstruction_audit=checked")
    print("  D5_P_STATE_PS3_FULL_RESIDUAL_ROUTE_CERTIFICATE.md d5_p_state_ps3_full_residual_route_certificate=checked")
    print("  D5_P_ACC_MAP_DEFINITION_AUDIT.md d5_p_acc_map_definition_audit=checked")
    print("  D5_P_ACC_ROW_BINDING_AUDIT.md d5_p_acc_row_binding_audit=checked")
    print("  D5_P_ACC_INDEPENDENCE_AUDIT.md d5_p_acc_independence_audit=checked")
    print("  D5_P_ACC_LIFT_OBSTRUCTION_AUDIT.md d5_p_acc_lift_obstruction_audit=checked")
    print("  D5_P_ACC_PA2_WEIGHTED_INVERSE_AUDIT.md d5_p_acc_pa2_weighted_inverse_audit=checked")
    print("  D5_P_LAMBDA_INTERFACE_AUDIT.md d5_p_lambda_interface_audit=checked")
    print("  D5_P_LAMBDA_INF_SUP_PROBE.md d5_p_lambda_inf_sup_probe=checked")
    print("  D5_P_LAMBDA_PL2_GEOMETRIC_MARGIN_AUDIT.md d5_p_lambda_pl2_geometric_margin_audit=checked")
    print("  D5_P_LAMBDA_D3_NONCIRCULARITY_AUDIT.md d5_p_lambda_d3_noncircularity_audit=checked")
    print("  D5_P_LAMBDA_PL4_RATE_PROPAGATION_AUDIT.md d5_p_lambda_pl4_rate_propagation_audit=checked")
    print("  D5_P_GEOM_CHART_REDUCTION_AUDIT.md d5_p_geom_chart_reduction_audit=checked")
    print("  D5_P_GYRO_BILINEAR_REDUCTION_AUDIT.md d5_p_gyro_bilinear_reduction_audit=checked")
    print("  D5_OPEN_PRIMITIVE_GAP_AUDIT.md d5_open_primitive_gap_audit=checked")
    print("  D5_PRIMITIVE_OBLIGATION_CLOSURE_PLAN.md d5_primitive_obligation_closure_plan=checked")
    print("  D5_CONDITIONAL_TAYLOR_CERTIFICATE.md d5_conditional_taylor_certificate=checked")
    print("  RESULT_TO_MANUSCRIPT_TRACEABILITY_AUDIT.md result_to_manuscript_traceability_audit=checked")
    print("  PROOF_NUMERICAL_SCALE_AUDIT.md proof_numerical_scale_audit=checked")
    print("  PROOF_SOLVER_SCALE_AUDIT.md proof_solver_scale_audit=checked")
    print("  PROOF_SOLVER_SCALED_TOLERANCE_PROBE.md proof_solver_scaled_tolerance_probe=checked")
    print("  PROOF_SOLVER_SCALED_TOLERANCE_TRAJECTORY_PROBE.md proof_solver_scaled_tolerance_trajectory_probe=checked")
    print("  PROOF_SOLVER_TOLERANCE_REGIME_SWEEP.md proof_solver_tolerance_regime_sweep=checked")
    print("  CMAME_STRICT_PROOF_AUDIT.md strict_proof_audit=checked")
    print("  CMAME_STRICT_PROOF_POLICY_RECONCILIATION_AUDIT.md strict_proof_policy_reconciliation=checked")
    print("  CMAME_VISUAL_LEGIBILITY_AUDIT.md visual_legibility_audit=checked")
    print("  CMAME_RELATED_WORK_AUDIT.md related_work_audit=checked")
    print("  CMAME_PROSE_RESIDUE_AUDIT.md prose_residue_audit=checked")
    print("  DYNAMIC_ROW_ORACLE_GATE.md dynamic_row_oracle_gate=checked")
    print("  KINEMATIC_ROW_DEFECT_CERTIFICATE.md kinematic_row_defect_certificate=checked")
    print("  NEWTON_EULER_DEFECT_OBLIGATION_GATE.md newton_euler_defect_obligation_gate=checked")
    print("  submission_ready=False")
    print("  mechanical_preflight_passed=True")
    print("  quality_review_passed=False")
    print("  SUBMISSION_PACKET.md submission_boundary=checked")
    print("  SUBMISSION_ARTIFACT_MANIFEST.json submission_manifest=checked")
    print("  COVER_LETTER.md cover_letter_boundary=checked")
    print("  SUBMISSION_FILE_INVENTORY.md file_inventory=checked")
    print("  REVIEW_RESPONSE_TEMPLATE.md review_response_boundary=checked")
    print("  reviewer-facing archive boundary docs=checked")
    print("  global blocker matrix docs=checked")
    print("  main_cmame.tex cmame_elsarticle_source=checked")
    print("  main_cmame.pdf cmame_recommended_pdf=checked")
    print("  cmame_submission_flat/main_cmame_submission.tex flat_source=checked")
    print("  cmame_submission_flat/main_cmame_submission.pdf flat_pdf=checked")
    print("  validate_cmame_submission.py cmame_submission_validator=checked")
    print("  validate_cmame_pdf_style_review_audit.py pdf_style_review_validator=checked")
    print("  validate_cmame_submission_integrity_audit.py submission_integrity_audit_validator=checked")
    print("  validate_reference_metadata_audit.py reference_metadata_audit_validator=checked")
    print("  B4_GUARDED_DRIVER_REFUSAL_BOUNDARY_AUDIT_20260621.md b4_guarded_driver_refusal_boundary_audit=checked")
    print("  validate_b4_guarded_driver_refusal_boundary_audit_20260621.py b4_guarded_driver_refusal_boundary_validator=checked")
    print("  validate_cmame_blocker_closure_gate.py blocker_closure_gate_validator=checked")
    print("  validate_cmame_external_baseline_gate.py external_baseline_gate_validator=checked")
    print("  validate_cmame_proof_contract_gate.py proof_contract_gate_validator=checked")
    print("  validate_cmame_visual_legibility_audit.py visual_legibility_audit_validator=checked")
    print("  validate_cmame_figure_set_audit.py figure_set_audit_validator=checked")
    print("  validate_cmame_scalability_boundary_audit.py scalability_boundary_audit_validator=checked")
    print("  validate_cmame_related_work_audit.py related_work_audit_validator=checked")
    print("  validate_cmame_prose_residue_audit.py prose_residue_audit_validator=checked")
    print("  validate_cmame_proof_style_audit.py proof_style_audit_validator=checked")
    print("  validate_proof_closure_manifest.py proof_closure_manifest_validator=checked")
    print("  validate_proof_claim_traceability_audit.py proof_claim_traceability_validator=checked")
    print("  validate_d5_dynamic_defect_readiness_audit.py d5_dynamic_defect_readiness_validator=checked")
    print("  validate_d5_dynamic_direct_substitution_certificate.py d5_dynamic_direct_substitution_validator=checked")
    print("  validate_d5_taylor_term_budget_audit.py d5_taylor_term_budget_validator=checked")
    print("  validate_d5_primitive_bound_reduction_audit.py d5_primitive_bound_reduction_validator=checked")
    print("  validate_d5_p_tube_constants_audit.py d5_p_tube_constants_validator=checked")
    print("  validate_d5_p_state_lift_gap_audit.py d5_p_state_lift_gap_validator=checked")
    print("  validate_d5_p_state_map_definition_audit.py d5_p_state_map_definition_validator=checked")
    print("  validate_d5_p_state_anticircularity_audit.py d5_p_state_anticircularity_validator=checked")
    print("  validate_d5_p_state_ps2_weighted_target_audit.py d5_p_state_ps2_weighted_target_validator=checked")
    print("  validate_d5_p_state_ps2_kinematic_block_certificate.py d5_p_state_ps2_kinematic_block_validator=checked")
    print("  validate_d5_p_state_ps2_lie_chart_binding_audit.py d5_p_state_ps2_lie_chart_binding_validator=checked")
    print("  validate_d5_p_state_ps2_row_injection_audit.py d5_p_state_ps2_row_injection_validator=checked")
    print("  validate_d5_p_state_ps2_nonlinear_binding_audit.py d5_p_state_ps2_nonlinear_binding_validator=checked")
    print("  validate_d5_p_state_ps2_aggregate_promotion_audit.py d5_p_state_ps2_aggregate_promotion_validator=checked")
    print("  validate_d5_p_state_ps2_linearization_probe.py d5_p_state_ps2_linearization_probe_validator=checked")
    print("  validate_d5_p_state_ps3_conditional_conversion_audit.py d5_p_state_ps3_conditional_conversion_validator=checked")
    print("  validate_d5_p_state_ps3_actual_instantiation_gap_audit.py d5_p_state_ps3_actual_instantiation_gap_validator=checked")
    print("  validate_d5_p_state_ps3_h_acc_input_obstruction_audit.py d5_p_state_ps3_h_acc_input_obstruction_validator=checked")
    print("  validate_d5_p_acc_map_definition_audit.py d5_p_acc_map_definition_validator=checked")
    print("  validate_d5_p_acc_row_binding_audit.py d5_p_acc_row_binding_validator=checked")
    print("  validate_d5_p_acc_independence_audit.py d5_p_acc_independence_validator=checked")
    print("  validate_d5_p_acc_lift_obstruction_audit.py d5_p_acc_lift_obstruction_validator=checked")
    print("  validate_d5_p_lambda_interface_audit.py d5_p_lambda_interface_validator=checked")
    print("  validate_d5_p_lambda_inf_sup_probe.py d5_p_lambda_inf_sup_probe_validator=checked")
    print("  validate_d5_p_lambda_d3_noncircularity_audit.py d5_p_lambda_d3_noncircularity_validator=checked")
    print("  validate_d5_open_primitive_gap_audit.py d5_open_primitive_gap_validator=checked")
    print("  validate_d5_primitive_obligation_closure_plan.py d5_primitive_obligation_closure_plan_validator=checked")
    print("  validate_result_to_manuscript_traceability_audit.py result_to_manuscript_traceability_validator=checked")
    print("  validate_four_example_source_policy_dashboard.py four_example_source_policy_dashboard_validator=checked")
    print("  validate_dynamic_row_oracle_gate.py dynamic_row_oracle_gate_validator=checked")
    print("  validate_kinematic_row_defect_certificate.py kinematic_row_defect_certificate_validator=checked")
    print("  NEWTON_EULER_VIRTUAL_WORK_WRENCH_AUDIT.md newton_euler_virtual_work_wrench_audit=checked")
    print("  validate_newton_euler_virtual_work_wrench_audit.py newton_euler_virtual_work_wrench_audit_validator=checked")
    print("  NEWTON_EULER_SYMBOLIC_DEFECT_CERTIFICATE.md newton_euler_symbolic_defect_certificate=checked")
    print("  NEWTON_EULER_DYNAMIC_ROW_CLOSURE_CONTRACT.md newton_euler_dynamic_row_closure_contract=checked")
    print("  validate_newton_euler_dynamic_row_closure_contract.py newton_euler_dynamic_row_closure_contract_validator=checked")
    print("  PROOF_EVIDENCE_MATRIX.md proof_evidence_matrix=checked")
    print("  validate_proof_evidence_matrix.py proof_evidence_matrix_validator=checked")
    print("  validate_proof_numerical_scale_audit.py proof_numerical_scale_audit_validator=checked")
    print("  validate_proof_solver_scale_audit.py proof_solver_scale_audit_validator=checked")
    print("  validate_proof_solver_scaled_tolerance_probe.py proof_solver_scaled_tolerance_probe_validator=checked")
    print("  validate_proof_solver_scaled_tolerance_trajectory_probe.py proof_solver_scaled_tolerance_trajectory_probe_validator=checked")
    print("  validate_proof_solver_tolerance_regime_sweep.py proof_solver_tolerance_regime_sweep_validator=checked")
    print("  ORDER_ACCEPTANCE_GATE.md order_acceptance_gate=checked")
    print("  validate_order_acceptance_gate.py order_acceptance_gate_validator=checked")
    print("  IMPLEMENTATION_FIDELITY_CERTIFICATE.md implementation_fidelity_certificate=checked")
    print("  validate_implementation_fidelity_certificate.py implementation_fidelity_certificate_validator=checked")
    print("  IMPLEMENTATION_PATH_AUDIT.md implementation_path_audit=checked")
    print("  validate_implementation_path_audit.py implementation_path_audit_validator=checked")
    print("  SOURCE_PAPER_COMPARISON.md source_paper_comparison=checked")
    print("  validate_source_paper_comparison.py source_paper_comparison_validator=checked")
    print("  EXTERNAL_SAME_TEST_RUN_QUEUE.md external_same_test_run_queue=checked")
    print("  validate_external_same_test_run_queue.py external_same_test_run_queue_validator=checked")
    print("  SOURCE_POLICY_CLOSURE_TRIAGE.md source_policy_closure_triage=checked")
    print("  validate_source_policy_closure_triage.py source_policy_closure_triage_validator=checked")
    print("  SOURCE_POLICY_ROW_CLOSURE_LEDGER.md source_policy_row_closure_ledger=checked")
    print("  validate_source_policy_row_closure_ledger.py source_policy_row_closure_ledger_validator=checked")
    print("  SOURCE_POLICY_LOCAL_CANDIDATE_GAP_AUDIT.md source_policy_local_candidate_gap_audit=checked")
    print("  validate_source_policy_local_candidate_gap_audit.py source_policy_local_candidate_gap_validator=checked")
    print("  ALL_METHOD_EXAMPLE_CLAIM_DISPOSITION_AUDIT.md all_method_claim_disposition_audit=checked")
    print("  validate_all_method_example_claim_disposition_audit.py all_method_claim_disposition_validator=checked")
    print("  ALL_EXAMPLES_SOURCE_POLICY_AUDIT.md all_examples_source_policy_audit=checked")
    print("  validate_all_examples_source_policy_audit.py all_examples_source_policy_audit_validator=checked")
    print("  EXTERNAL_SOURCE_POLICY_CLOSURE_MANIFEST.md external_source_policy_closure_manifest=checked")
    print("  validate_external_source_policy_closure_manifest.py external_source_policy_closure_manifest_validator=checked")
    print("  VP2024_CODE_PATH_DISPOSITION_AUDIT.md vp2024_code_path_disposition_audit=checked")
    print("  validate_vp2024_code_path_disposition_audit.py vp2024_code_path_disposition_validator=checked")
    print("  RA2021_SOURCE_IDENTITY_AUDIT.md ra2021_source_identity_audit=checked")
    print("  validate_ra2021_source_identity_audit.py ra2021_source_identity_validator=checked")
    print("  HI2022_POLICY_DECISION_AUDIT.md hi2022_policy_decision_audit=checked")
    print("  validate_hi2022_policy_decision_audit.py hi2022_policy_decision_validator=checked")
    print("  HI2022_SOURCE_POLICY_ROW_AUDIT.md hi2022_source_policy_row_audit=checked")
    print("  validate_hi2022_source_policy_row_audit.py hi2022_source_policy_row_audit_validator=checked")
    print("  HI2022_T8_TOLERANCE_REPAIR_AUDIT.md hi2022_t8_tolerance_repair_audit=checked")
    print("  validate_hi2022_t8_tolerance_repair_audit.py hi2022_t8_tolerance_repair_validator=checked")
    print("  TFE_SOURCE_POLICY_SPEC.md tfe_source_policy_spec=checked")
    print("  validate_tfe_source_policy_spec.py tfe_source_policy_spec_validator=checked")
    print("  TFE_SOURCE_POLICY_ROW_AUDIT.md tfe_source_policy_row_audit=checked")
    print("  validate_tfe_source_policy_row_audit.py tfe_source_policy_row_audit_validator=checked")
    print("  TFE_B4_B7_SOURCE_POLICY_DEMOTION_AUDIT.md tfe_b4_b7_source_policy_demotion_audit=checked")
    print("  validate_tfe_b4_b7_source_policy_demotion_audit.py tfe_b4_b7_source_policy_demotion_validator=checked")
    print("  TFE_SOURCE_PENDULUM_MODEL_AUDIT.md tfe_source_pendulum_model_audit=checked")
    print("  validate_tfe_source_pendulum_model_audit.py tfe_source_pendulum_model_validator=checked")
    print("  TFE_BROWN_MCPHEE_SOURCE_LAW_BOUNDARY_AUDIT.md tfe_brown_mcphee_source_law_boundary_audit=checked")
    print("  validate_tfe_brown_mcphee_source_law_boundary_audit.py tfe_brown_mcphee_source_law_boundary_validator=checked")
    print("  TFE_BROWN_MCPHEE_SOURCE_CODE_EQUIVALENCE_CERTIFICATE.md tfe_brown_mcphee_source_code_equivalence_certificate=checked")
    print("  validate_tfe_brown_mcphee_source_code_equivalence_certificate.py tfe_brown_mcphee_source_code_equivalence_certificate_validator=checked")
    print("  TFE_DAE_RUNNER_CONTRACT_GAP_AUDIT.md tfe_dae_runner_contract_gap_audit=checked")
    print("  validate_tfe_dae_runner_contract_gap_audit.py tfe_dae_runner_contract_gap_validator=checked")
    print("  TFE_RUNNER_CONTRACT_PREFLIGHT_CERTIFICATE.md tfe_runner_contract_preflight_certificate=checked")
    print("  validate_tfe_runner_contract_preflight_certificate.py tfe_runner_contract_preflight_certificate_validator=checked")
    print("  TFE_FULL_T10_ABSOLUTE_DAE_LIFT_SUMMARY.md tfe_full_t10_absolute_dae_lift_summary=checked")
    print("  validate_tfe_full_t10_absolute_dae_lift_summary.py tfe_full_t10_absolute_dae_lift_validator=checked")
    print("  TFE_SOURCE_GRID_COMPATIBILITY_AUDIT.md tfe_source_grid_compatibility_audit=checked")
    print("  validate_tfe_source_grid_compatibility_audit.py tfe_source_grid_compatibility_validator=checked")
    print("  TFE_ENDPOINT_POLICY_BOUNDARY_CERTIFICATE.md tfe_endpoint_policy_boundary_certificate=checked")
    print("  validate_tfe_endpoint_policy_boundary_certificate.py tfe_endpoint_policy_boundary_validator=checked")
    print("  TFE_ENDPOINT_POLICY_SENSITIVITY_AUDIT.md tfe_endpoint_policy_sensitivity_audit=checked")
    print("  validate_tfe_endpoint_policy_sensitivity_audit.py tfe_endpoint_policy_sensitivity_validator=checked")
    print("  TFE_FULL_T10_ENDPOINT_POLICY_CLOSURE_CERTIFICATE.md tfe_full_t10_endpoint_policy_closure_certificate=checked")
    print("  validate_tfe_full_t10_endpoint_policy_closure_certificate.py tfe_full_t10_endpoint_policy_closure_certificate_validator=checked")
    print("  OBJECTIVE_COMPLETION_AUDIT.md objective_completion_audit=checked")
    print("  validate_objective_completion_audit.py objective_completion_validator=checked")
    print("  validate_submission_bundle.py submission_bundle_validator=checked")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--latex", action="store_true", help="also rebuild main.pdf before running validators")
    args = parser.parse_args()

    if not PYTHON.exists():
        print(f"[FAIL] python environment missing: {PYTHON}")
        return 1

    failures = 0
    if args.latex:
        ok, _ = run_step("latex paper build", latex_command("main.tex"), PAPER)
        failures += 0 if ok else 1
        ok, _ = run_step("latex concise paper build", latex_command("main_concise.tex"), PAPER)
        failures += 0 if ok else 1
        ok, _ = run_step("latex CMAME paper build", latex_command("main_cmame.tex"), PAPER)
        failures += 0 if ok else 1
        ok, _ = run_step(
            "latex flat CMAME source build",
            latex_command("main_cmame_submission.tex"),
            PAPER / "cmame_submission_flat",
        )
        failures += 0 if ok else 1

    failures += 0 if check_required_files() else 1
    steps: list[tuple[str, list[str], Path]] = [
        ("paper claim validator", [str(PYTHON), "validate_paper_claims.py"], PAPER),
        ("concise paper validator", [str(PYTHON), "validate_concise_paper.py"], PAPER),
        ("CMAME submission validator", [str(PYTHON), "validate_cmame_submission.py"], PAPER),
        ("CMAME submission integrity audit validator", [str(PYTHON), "validate_cmame_submission_integrity_audit.py"], PAPER),
        ("reference metadata audit validator", [str(PYTHON), "validate_reference_metadata_audit.py"], PAPER),
        ("CMAME blocker closure gate validator", [str(PYTHON), "validate_cmame_blocker_closure_gate.py"], PAPER),
        ("CMAME external baseline gate validator", [str(PYTHON), "validate_cmame_external_baseline_gate.py"], PAPER),
        # 2026-09-17: the "CMAME proof contract gate validator" step (validate_cmame_proof_contract_gate.py)
        # pinned the retired 96-row/D5 route; superseded by the exact-stage-identity gate (its JSON is kept
        # as an archived record). Likewise superseded: "CMAME proof style audit validator",
        # "CMAME strict proof audit validator", "CMAME strict proof policy reconciliation audit validator",
        # "proof closure manifest validator", "proof-claim traceability audit validator",
        # "Newton-Euler symbolic defect certificate validator".
        ("CMAME visual legibility audit validator", [str(PYTHON), "validate_cmame_visual_legibility_audit.py"], PAPER),
        ("CMAME figure-set audit validator", [str(PYTHON), "validate_cmame_figure_set_audit.py"], PAPER),
        (
            "CMAME scalability boundary audit validator",
            [str(PYTHON), "validate_cmame_scalability_boundary_audit.py"],
            PAPER,
        ),
        ("CMAME related work audit validator", [str(PYTHON), "validate_cmame_related_work_audit.py"], PAPER),
        ("CMAME prose residue audit validator", [str(PYTHON), "validate_cmame_prose_residue_audit.py"], PAPER),
        (
            "CMAME narrowed-claim closure policy audit validator",
            [str(PYTHON), "validate_cmame_narrowed_claim_closure_policy_audit.py"],
            PAPER,
        ),
        # 2026-09-17: the proof-style, strict-proof, policy-reconciliation, proof-closure, and
        # proof-claim traceability gates pinned the retired 96-row/PS2/primitive-Taylor route and are
        # superseded by the exact-stage-identity gate.
        ("exact stage identity gate validator", [str(PYTHON), "validate_exact_stage_identity_gate.py"], PAPER),
        (
            "exact stage identity numerical check validator",
            [str(PYTHON), "validate_exact_stage_identity_numerical_check.py"],
            PAPER,
        ),
        (
            "P2 constants numerical check validator",
            [str(PYTHON), "validate_p2_constants_numerical_check.py"],
            PAPER,
        ),
        ("arXiv version validator", [str(PYTHON), "validate_arxiv_version.py"], PAPER),
        (
            "D5 dynamic-defect readiness audit validator",
            [str(PYTHON), "validate_d5_dynamic_defect_readiness_audit.py"],
            PAPER,
        ),
        (
            "D5 dynamic direct-substitution certificate validator",
            [str(PYTHON), "validate_d5_dynamic_direct_substitution_certificate.py"],
            PAPER,
        ),
        (
            "D5 Taylor term-budget audit validator",
            [str(PYTHON), "validate_d5_taylor_term_budget_audit.py"],
            PAPER,
        ),
        (
            "D5 primitive-bound reduction audit validator",
            [str(PYTHON), "validate_d5_primitive_bound_reduction_audit.py"],
            PAPER,
        ),
        (
            "D5 P_tube constants audit validator",
            [str(PYTHON), "validate_d5_p_tube_constants_audit.py"],
            PAPER,
        ),
        (
            "D5 P_state lift-gap audit validator",
            [str(PYTHON), "validate_d5_p_state_lift_gap_audit.py"],
            PAPER,
        ),
        (
            "D5 P_state map-definition audit validator",
            [str(PYTHON), "validate_d5_p_state_map_definition_audit.py"],
            PAPER,
        ),
        (
            "D5 P_state anti-circularity audit validator",
            [str(PYTHON), "validate_d5_p_state_anticircularity_audit.py"],
            PAPER,
        ),
        (
            "D5 P_state PS2 weighted-target audit validator",
            [str(PYTHON), "validate_d5_p_state_ps2_weighted_target_audit.py"],
            PAPER,
        ),
        (
            "D5 P_state PS2 kinematic-block certificate validator",
            [str(PYTHON), "validate_d5_p_state_ps2_kinematic_block_certificate.py"],
            PAPER,
        ),
        (
            "D5 P_state PS2 Lie-chart binding audit validator",
            [str(PYTHON), "validate_d5_p_state_ps2_lie_chart_binding_audit.py"],
            PAPER,
        ),
        (
            "D5 P_state PS2 row-injection audit validator",
            [str(PYTHON), "validate_d5_p_state_ps2_row_injection_audit.py"],
            PAPER,
        ),
        (
            "D5 P_state PS2 nonlinear binding audit validator",
            [str(PYTHON), "validate_d5_p_state_ps2_nonlinear_binding_audit.py"],
            PAPER,
        ),
        (
            "D5 P_state PS2 aggregate-promotion audit validator",
            [str(PYTHON), "validate_d5_p_state_ps2_aggregate_promotion_audit.py"],
            PAPER,
        ),
        (
            "D5 P_state PS2 linearization-probe validator",
            [str(PYTHON), "validate_d5_p_state_ps2_linearization_probe.py"],
            PAPER,
        ),
        (
            "D5 P_state PS3 conditional-conversion audit validator",
            [str(PYTHON), "validate_d5_p_state_ps3_conditional_conversion_audit.py"],
            PAPER,
        ),
        (
            "D5 P_state PS3 actual-instantiation gap audit validator",
            [str(PYTHON), "validate_d5_p_state_ps3_actual_instantiation_gap_audit.py"],
            PAPER,
        ),
        (
            "D5 P_state PS3 h-acceleration input obstruction audit validator",
            [str(PYTHON), "validate_d5_p_state_ps3_h_acc_input_obstruction_audit.py"],
            PAPER,
        ),
        (
            "D5 P_state PS3 full-residual route certificate validator",
            [str(PYTHON), "validate_d5_p_state_ps3_full_residual_route_certificate.py"],
            PAPER,
        ),
        (
            "D5 P_acc map-definition audit validator",
            [str(PYTHON), "validate_d5_p_acc_map_definition_audit.py"],
            PAPER,
        ),
        (
            "D5 P_acc row-binding audit validator",
            [str(PYTHON), "validate_d5_p_acc_row_binding_audit.py"],
            PAPER,
        ),
        (
            "D5 P_acc independence audit validator",
            [str(PYTHON), "validate_d5_p_acc_independence_audit.py"],
            PAPER,
        ),
        (
            "D5 P_acc lift-obstruction audit validator",
            [str(PYTHON), "validate_d5_p_acc_lift_obstruction_audit.py"],
            PAPER,
        ),
        (
            "D5 P_acc PA2 weighted-inverse audit validator",
            [str(PYTHON), "validate_d5_p_acc_pa2_weighted_inverse_audit.py"],
            PAPER,
        ),
        (
            "D5 P_lambda interface audit validator",
            [str(PYTHON), "validate_d5_p_lambda_interface_audit.py"],
            PAPER,
        ),
        (
            "D5 P_lambda inf-sup probe validator",
            [str(PYTHON), "validate_d5_p_lambda_inf_sup_probe.py"],
            PAPER,
        ),
        (
            "D5 P_lambda PL2 geometric-margin audit validator",
            [str(PYTHON), "validate_d5_p_lambda_pl2_geometric_margin_audit.py"],
            PAPER,
        ),
        (
            "D5 P_lambda D3 non-circularity audit validator",
            [str(PYTHON), "validate_d5_p_lambda_d3_noncircularity_audit.py"],
            PAPER,
        ),
        (
            "D5 P_lambda PL4 rate-propagation audit validator",
            [str(PYTHON), "validate_d5_p_lambda_pl4_rate_propagation_audit.py"],
            PAPER,
        ),
        (
            "D5 P_geom chart-reduction audit validator",
            [str(PYTHON), "validate_d5_p_geom_chart_reduction_audit.py"],
            PAPER,
        ),
        (
            "D5 P_gyro bilinear-reduction audit validator",
            [str(PYTHON), "validate_d5_p_gyro_bilinear_reduction_audit.py"],
            PAPER,
        ),
        (
            "D5 open primitive gap audit validator",
            [str(PYTHON), "validate_d5_open_primitive_gap_audit.py"],
            PAPER,
        ),
        (
            "D5 primitive-obligation closure plan validator",
            [str(PYTHON), "validate_d5_primitive_obligation_closure_plan.py"],
            PAPER,
        ),
        (
            "D5 conditional Taylor certificate validator",
            [str(PYTHON), "validate_d5_conditional_taylor_certificate.py"],
            PAPER,
        ),
        ("paper numerical result matrix validator", [str(PYTHON), "validate_paper_numerical_result_matrix.py"], PAPER),
        (
            "four-example source-policy dashboard validator",
            [str(PYTHON), "validate_four_example_source_policy_dashboard.py"],
            PAPER,
        ),
        (
            "result-to-manuscript traceability audit validator",
            [str(PYTHON), "validate_result_to_manuscript_traceability_audit.py"],
            PAPER,
        ),
        (
            "all-method claim-disposition audit validator",
            [str(PYTHON), "validate_all_method_example_claim_disposition_audit.py"],
            PAPER,
        ),
        ("all-examples result sanity audit validator", [str(PYTHON), "validate_all_examples_result_sanity_audit.py"], PAPER),
        (
            "common-reference order recomputation audit validator",
            [str(PYTHON), "validate_common_reference_order_recomputation_audit.py"],
            PAPER,
        ),
        (
            "external baseline source-policy diagnosis validator",
            [str(PYTHON), "validate_external_baseline_source_policy_diagnosis.py"],
            PAPER,
        ),
        (
            "source-policy closure triage validator",
            [str(PYTHON), "validate_source_policy_closure_triage.py"],
            PAPER,
        ),
        (
            "source-policy row closure ledger validator",
            [str(PYTHON), "validate_source_policy_row_closure_ledger.py"],
            PAPER,
        ),
        (
            "source-policy local candidate gap audit validator",
            [str(PYTHON), "validate_source_policy_local_candidate_gap_audit.py"],
            PAPER,
        ),
        (
            "all-examples source-policy audit validator",
            [str(PYTHON), "validate_all_examples_source_policy_audit.py"],
            PAPER,
        ),
        (
            "external suite disposition audit validator",
            [str(PYTHON), "validate_external_suite_disposition_audit.py"],
            PAPER,
        ),
        (
            "external source-policy closure manifest validator",
            [str(PYTHON), "validate_external_source_policy_closure_manifest.py"],
            PAPER,
        ),
        (
            "external case evidence reconciliation validator",
            [str(PYTHON), "validate_external_case_evidence_reconciliation.py"],
            PAPER,
        ),
        (
            "VP2024 code-path disposition audit validator",
            [str(PYTHON), "validate_vp2024_code_path_disposition_audit.py"],
            PAPER,
        ),
        (
            "B2 source-policy remaining-work manifest validator",
            [str(PYTHON), "validate_b2_source_policy_remaining_work_manifest.py"],
            PAPER,
        ),
        (
            "external-superiority claim-demotion audit validator",
            [str(PYTHON), "validate_external_superiority_claim_demotion_audit.py"],
            PAPER,
        ),
        (
            "B4/B7 non-superiority route audit validator",
            [str(PYTHON), "validate_b4_b7_non_superiority_route_audit.py"],
            PAPER,
        ),
        (
            "B4 source-policy work/precision execution plan validator",
            [str(PYTHON), "validate_b4_source_policy_work_precision_execution_plan.py"],
            PAPER,
        ),
        (
            "B4 existing-artifact promotion audit validator",
            [str(PYTHON), "validate_b4_existing_artifact_promotion_audit.py"],
            PAPER,
        ),
        (
            "B4 source-policy post-execution audit validator",
            [str(PYTHON), "validate_b4_source_policy_post_execution_audit.py"],
            PAPER,
        ),
        (
            "source-policy public-code refresh 20260620 validator",
            [str(PYTHON), "validate_source_policy_public_code_refresh_20260620.py"],
            PAPER,
        ),
        (
            "source-policy reopen-condition monitor 20260620 validator",
            [str(PYTHON), "validate_source_policy_reopen_condition_monitor_20260620.py"],
            PAPER,
        ),
        (
            "RA2021 double source-policy low-order diagnosis validator",
            [str(PYTHON), "validate_ra2021_double_source_policy_low_order_diagnosis.py"],
            PAPER,
        ),
        (
            "HI2022 rA_half double source-policy failure diagnosis validator",
            [str(PYTHON), "validate_hi2022_ra_half_double_source_policy_failure_diagnosis.py"],
            PAPER,
        ),
        (
            "B4 source-policy row closure-readiness ledger validator",
            [str(PYTHON), "validate_b4_source_policy_row_closure_readiness_ledger.py"],
            PAPER,
        ),
        (
            "RA/HI source-policy output inventory validator",
            [str(PYTHON), "validate_ra_hi_source_policy_output_inventory.py"],
            PAPER,
        ),
        (
            "RA/HI source-policy closeout checklist validator",
            [str(PYTHON), "validate_ra_hi_source_policy_closeout_checklist.py"],
            PAPER,
        ),
        (
            "RA/HI source-policy promotion blocker matrix validator",
            [str(PYTHON), "validate_ra_hi_source_policy_promotion_blocker_matrix.py"],
            PAPER,
        ),
        (
            "RA/HI post-execution attempt certificate validator",
            [str(PYTHON), "validate_ra_hi_source_policy_post_execution_attempt_certificate.py"],
            PAPER,
        ),
        (
            "B4 source-policy execution opt-in packet validator",
            [str(PYTHON), "validate_b4_source_policy_execution_opt_in_packet.py"],
            PAPER,
        ),
        (
            "B4 source-policy guarded driver validator",
            [str(PYTHON), "validate_b4_source_policy_guarded_driver.py"],
            PAPER,
        ),
        (
            "B4 source-policy execution handoff package validator",
            [str(PYTHON), "validate_b4_source_policy_execution_handoff_package.py"],
            PAPER,
        ),
        (
            "B4 source-policy command preflight freeze 20260620 validator",
            [str(PYTHON), "validate_b4_source_policy_command_preflight_freeze_20260620.py"],
            PAPER,
        ),
        (
            "B4 source-policy expected-output schema audit 20260620 validator",
            [str(PYTHON), "validate_b4_source_policy_expected_output_schema_audit_20260620.py"],
            PAPER,
        ),
        (
            "B4 expected-output promotion-readiness blocker audit 20260620 validator",
            [str(PYTHON), "validate_b4_expected_output_promotion_readiness_blocker_audit_20260620.py"],
            PAPER,
        ),
        (
            "OC6 source-equivalent reopen-readiness audit 20260620 validator",
            [str(PYTHON), "validate_oc6_source_equivalent_reopen_readiness_audit_20260620.py"],
            PAPER,
        ),
        (
            "full source-policy row provenance audit validator",
            [str(PYTHON), "validate_full_source_policy_row_provenance_audit.py"],
            PAPER,
        ),
        (
            "RA2021 source-policy row audit validator",
            [str(PYTHON), "validate_ra2021_source_policy_row_audit.py"],
            PAPER,
        ),
        (
            "RA2021 source-identity audit validator",
            [str(PYTHON), "validate_ra2021_source_identity_audit.py"],
            PAPER,
        ),
        (
            "HI2022 policy-decision audit validator",
            [str(PYTHON), "validate_hi2022_policy_decision_audit.py"],
            PAPER,
        ),
        (
            "HI2022 source-policy row audit validator",
            [str(PYTHON), "validate_hi2022_source_policy_row_audit.py"],
            PAPER,
        ),
        (
            "HI2022 T=8 tolerance-repair audit validator",
            [str(PYTHON), "validate_hi2022_t8_tolerance_repair_audit.py"],
            PAPER,
        ),
        ("TFE source-policy spec validator", [str(PYTHON), "validate_tfe_source_policy_spec.py"], PAPER),
        (
            "TFE source-policy row audit validator",
            [str(PYTHON), "validate_tfe_source_policy_row_audit.py"],
            PAPER,
        ),
        (
            "TFE source-pendulum model audit validator",
            [str(PYTHON), "validate_tfe_source_pendulum_model_audit.py"],
            PAPER,
        ),
        (
            "TFE Brown-McPhee source-law boundary audit validator",
            [str(PYTHON), "validate_tfe_brown_mcphee_source_law_boundary_audit.py"],
            PAPER,
        ),
        (
            "TFE Brown-McPhee source-code equivalence certificate validator",
            [str(PYTHON), "validate_tfe_brown_mcphee_source_code_equivalence_certificate.py"],
            PAPER,
        ),
        (
            "TFE DAE runner contract gap audit validator",
            [str(PYTHON), "validate_tfe_dae_runner_contract_gap_audit.py"],
            PAPER,
        ),
        (
            "TFE runner contract preflight certificate validator",
            [str(PYTHON), "validate_tfe_runner_contract_preflight_certificate.py"],
            PAPER,
        ),
        (
            "TFE full-T10 absolute DAE-lift summary validator",
            [str(PYTHON), "validate_tfe_full_t10_absolute_dae_lift_summary.py"],
            PAPER,
        ),
        (
            "TFE source grid compatibility audit validator",
            [str(PYTHON), "validate_tfe_source_grid_compatibility_audit.py"],
            PAPER,
        ),
        (
            "TFE endpoint policy boundary certificate validator",
            [str(PYTHON), "validate_tfe_endpoint_policy_boundary_certificate.py"],
            PAPER,
        ),
        (
            "TFE endpoint-policy sensitivity audit validator",
            [str(PYTHON), "validate_tfe_endpoint_policy_sensitivity_audit.py"],
            PAPER,
        ),
        (
            "TFE full-T10 endpoint policy closure certificate validator",
            [str(PYTHON), "validate_tfe_full_t10_endpoint_policy_closure_certificate.py"],
            PAPER,
        ),
        (
            "TFE B4/B7 source-policy demotion audit validator",
            [str(PYTHON), "validate_tfe_b4_b7_source_policy_demotion_audit.py"],
            PAPER,
        ),
        (
            "TFE source-policy self-reproduction attempt certificate validator",
            [str(PYTHON), "validate_tfe_source_policy_self_reproduction_attempt_certificate.py"],
            PAPER,
        ),
        (
            "objective completion audit validator",
            [str(PYTHON), "validate_objective_completion_audit.py"],
            PAPER,
        ),
        (
            "comparison objective closure reconciliation audit validator",
            [str(PYTHON), "validate_comparison_objective_closure_reconciliation_audit.py"],
            PAPER,
        ),
        (
            "CMAME PDF style review audit validator",
            [str(PYTHON), "validate_cmame_pdf_style_review_audit.py"],
            PAPER,
        ),
        ("CMAME review agent validator", [str(PYTHON), "validate_cmame_review_agent.py"], PAPER),
        (
            "full source-policy runner archive gap audit validator",
            [str(PYTHON), "validate_full_source_policy_runner_archive_gap_audit.py"],
            PAPER,
        ),
        (
            "CMAME reproducibility package manifest validator",
            [str(PYTHON), "validate_cmame_reproducibility_package_manifest.py"],
            PAPER,
        ),
        (
            "CMAME runner-centered reproducibility audit validator",
            [str(PYTHON), "validate_cmame_runner_centered_reproducibility_audit.py"],
            PAPER,
        ),
        (
            "CMAME runner-adapter candidate validator",
            [str(PYTHON), "validate_cmame_runner_adapter_candidate.py"],
            PAPER,
        ),
        (
            "CMAME self-contained runner extraction plan validator",
            [str(PYTHON), "validate_cmame_self_contained_runner_extraction_plan.py"],
            PAPER,
        ),
        (
            "B6 four-example local evidence validator",
            [str(PYTHON), "validate_b6_four_example_local_evidence.py"],
            PAPER,
        ),
        (
            "B6 closed-loop self-contained extraction audit validator",
            [str(PYTHON), "validate_b6_closed_loop_self_contained_extraction_audit.py"],
            PAPER,
        ),
        (
            "CMAME closed-loop local runner candidate validator",
            [str(PYTHON), "validate_cmame_closed_loop_local_runner_candidate.py"],
            PAPER,
        ),
        (
            "CMAME P1 local-runner extraction audit validator",
            [str(PYTHON), "validate_cmame_p1_local_runner_extraction_audit.py"],
            PAPER,
        ),
        (
            "CMAME P1 single-runner candidate validator",
            [str(PYTHON), "validate_cmame_p1_single_runner_candidate.py"],
            PAPER,
        ),
        (
            "CMAME P1 double-runner candidate validator",
            [str(PYTHON), "validate_cmame_p1_double_runner_candidate.py"],
            PAPER,
        ),
        (
            "CMAME local accepted-row runner companion validator",
            [str(PYTHON), "validate_cmame_local_accepted_runner_companion.py"],
            PAPER,
        ),
        (
            "CMAME narrowed reproducibility bundle validator",
            [str(PYTHON), "validate_cmame_narrowed_repro_bundle.py"],
            PAPER,
        ),
        (
            "CMAME minimal reproducibility candidate validator",
            [str(PYTHON), "validate_cmame_minimal_reproducibility_candidate.py"],
            PAPER,
        ),
        ("dynamic row oracle gate validator", [str(PYTHON), "validate_dynamic_row_oracle_gate.py"], PAPER),
        ("kinematic row defect certificate validator", [str(PYTHON), "validate_kinematic_row_defect_certificate.py"], PAPER),
        ("Newton-Euler defect obligation gate validator", [str(PYTHON), "validate_newton_euler_defect_obligation_gate.py"], PAPER),
        (
            "Newton-Euler virtual-work wrench audit validator",
            [str(PYTHON), "validate_newton_euler_virtual_work_wrench_audit.py"],
            PAPER,
        ),
        # 2026-09-17: NEWTON_EULER_SYMBOLIC_DEFECT_CERTIFICATE is superseded by the exact-stage-identity
        # gate (36 Newton-Euler rows are proved to vanish in the Lean development).
        (
            "B1 symbolic row-oracle closure certificate validator",
            [str(PYTHON), "validate_b1_symbolic_row_oracle_closure_certificate.py"],
            PAPER,
        ),
        (
            "B1 AD-expanded symbolic oracle closure certificate validator",
            [str(PYTHON), "validate_b1_ad_expanded_symbolic_oracle_closure_certificate.py"],
            PAPER,
        ),
        (
            "Newton-Euler dynamic-row closure contract validator",
            [str(PYTHON), "validate_newton_euler_dynamic_row_closure_contract.py"],
            PAPER,
        ),
        ("proof evidence matrix validator", [str(PYTHON), "validate_proof_evidence_matrix.py"], PAPER),
        ("proof numerical scale audit validator", [str(PYTHON), "validate_proof_numerical_scale_audit.py"], PAPER),
        ("proof solver-scale audit validator", [str(PYTHON), "validate_proof_solver_scale_audit.py"], PAPER),
        (
            "proof solver scaled-tolerance probe validator",
            [str(PYTHON), "validate_proof_solver_scaled_tolerance_probe.py"],
            PAPER,
        ),
        (
            "proof solver scaled-tolerance trajectory probe validator",
            [str(PYTHON), "validate_proof_solver_scaled_tolerance_trajectory_probe.py"],
            PAPER,
        ),
        (
            "proof solver tolerance-regime sweep validator",
            [str(PYTHON), "validate_proof_solver_tolerance_regime_sweep.py"],
            PAPER,
        ),
        ("order acceptance gate validator", [str(PYTHON), "validate_order_acceptance_gate.py"], PAPER),
        ("implementation fidelity certificate validator", [str(PYTHON), "validate_implementation_fidelity_certificate.py"], PAPER),
        ("implementation path audit validator", [str(PYTHON), "validate_implementation_path_audit.py"], PAPER),
        ("source-paper comparison validator", [str(PYTHON), "validate_source_paper_comparison.py"], PAPER),
        ("cross-paper benchmark spec validator", [str(PYTHON), "validate_cross_paper_benchmark_spec.py"], PAPER),
        ("cross-paper benchmark case validator", [str(PYTHON), "validate_cross_paper_benchmark_cases.py"], PAPER),
        ("external same-test run queue validator", [str(PYTHON), "validate_external_same_test_run_queue.py"], PAPER),
        ("submission bundle validator", [str(PYTHON), "validate_submission_bundle.py"], PAPER),
        ("minimal four-ASME validator", [str(PYTHON), "validate_four_asme_minimal.py"], PIPELINE),
        ("full-TFE gap validator", [str(PYTHON), "validate_full_tfe_gap.py"], PIPELINE),
        ("full-TFE repair spec validator", [str(PYTHON), "validate_full_tfe_repair_spec.py"], PIPELINE),
        ("full v047 artifact validator", [str(PYTHON), "validate_v047_outputs.py"], PIPELINE),
    ]
    required_output_markers = {
        "CMAME submission validator": [
            "manifest_boundary_matches_archive_gap=True",
            "manifest_action_boundary=4/1/False/True/13/20",
            "oc6_reopen_latest_external_probe=2026-06-21/9/0/0/4/False/False",
            "full_source_policy_submission_ready=False",
            "run_v047_invoked=False",
        ],
        "CMAME submission integrity audit validator": [
            "manifest_boundary_matches_archive_gap=True",
            "manifest_source_policy_execution_invoked=False",
            "oc6_reopen_latest_external_probe=2026-06-21/9/0/0/4/False/False",
            "submission_ready=False",
        ],
        "CMAME narrowed-claim closure policy audit validator": [
            "CMAME narrowed-claim closure policy audit validation: PASS",
            "narrowed_claim_evidence_supported=True",
            "current_gate_can_close_now=True",
            "source_policy_rows=0/40",
            "blocker_open_by_id=OC4:True,OC6:True,OC12:True",
            "blocker_closure_decision_by_id=OC4:remain_open_ready_for_authorized_execution_not_executed_not_promoted,OC6:remain_open_no_positive_source_equivalent_artifact,OC12:remain_partial_narrowed_replay_ready_full_source_policy_archive_not_ready",
            "blocker_closure_allowed_by_id=OC4:False,OC6:False,OC12:False",
        ],
        "full source-policy runner archive gap audit validator": [
            "source_policy_closed=0/40",
            "oc6_reopen_latest_external_probe=2026-06-21/9/0/0/4/False/False",
            "opt_in_required_command_count=13",
            "opt_in_required_mapped_external_rows=20",
            "safe_next_actions_without_b4_opt_in=4",
            "opt_in_required_actions=1",
            "safe_action_ids=rebuild_read_only_audit_chain,rerun_read_only_validators,keep_narrowed_archive_provenance_only,monitor_reopen_conditions",
            "opt_in_action_ids=authorized_b4_ra_hi_source_policy_execution",
            "source_policy_execution_allowed_now=False",
            "exact_b4_opt_in_required_for_execution=True",
            "source_policy_execution_invoked=False",
            "driver_does_not_authorize_execution=True",
            "tfe_runner_contract_preflight=contract_entrypoints_callable_candidate_backed_source_policy_open/3/3/3/0/4",
            "full_archive_ready_now=False",
            "oc12_closure_decision=remain_partial_narrowed_replay_ready_full_source_policy_archive_not_ready",
            "current_archive_usable_as_full_source_policy_runner_archive=False",
            "safe_current_use=narrowed_claim_replay_and_audit_provenance_only",
            "primary_submission_package_allowed=False",
            "blocker_open_by_id=OC4:True,OC6:True,OC12:True",
            "blocker_closure_decision_by_id=OC4:remain_open_ready_for_authorized_execution_not_executed_not_promoted,OC6:remain_open_no_positive_source_equivalent_artifact,OC12:remain_partial_narrowed_replay_ready_full_source_policy_archive_not_ready",
            "blocker_closure_allowed_by_id=OC4:False,OC6:False,OC12:False",
            "submission_ready=False",
        ],
        "TFE source-policy self-reproduction attempt certificate validator": [
            "attempted_not_reproducible_rows=16/16",
            "public_code_recheck_status=public_code_rechecked_no_distinct_tfe_code_artifact_attempted_not_reproducible",
            "reopen_condition=new_public_or_source_code_equivalent_tfe_implementation_artifact",
            "source_policy_execution_preflight_status=terminal_no_public_code_self_reproduction_attempted_not_promoted",
            "public_code_refresh_latest_positive_artifact_rows=0",
            "source_policy_closed=0/16",
            "source_policy_closed_rows=0",
            "submission_ready=False",
        ],
        "source-policy public-code refresh 20260620 validator": [
            "rows=20",
            "current_queries=11",
            "positive_public_code_artifact_rows=0",
            "latest_external_probe=2026-06-21/9/0/0/4/False/False",
            "source_policy_closed=0",
            "source_policy_closed_ratio=0/20",
            "submission_ready=False",
        ],
        "source-policy reopen-condition monitor 20260620 validator": [
            "source-policy reopen-condition monitor validation: PASS",
            "rows=20",
            "unable_to_reproduce_rows=20",
            "positive_public_code_artifact_rows=0",
            "local_positive_reopen_artifact_rows=0",
            "source_policy_reopen_triggered=False",
            "source_policy_closed=0/20",
            "submission_ready=False",
        ],
        "TFE runner contract preflight certificate validator": [
            "entrypoints=3/3",
            "candidate_backed=3/3",
            "source_policy_rows_completed=0",
            "execution_blocks=4",
            "source_policy_equivalent=False/False",
        ],
        "TFE Brown-McPhee source-code equivalence certificate validator": [
            "TFE Brown-McPhee source-code-equivalence certificate validation: PASS",
            "status=negative_source_code_equivalence_certificate_not_source_policy",
            "brown_mcphee_source_code_equivalent_law=False",
            "source_policy_rows_completed=0",
            "source_policy_execution_invoked=False",
            "can_close_now=False",
            "blocker_open_by_id=OC4:True,OC6:True,OC12:True",
            "blocker_closure_decision_by_id=OC4:remain_open_ready_for_authorized_execution_not_executed_not_promoted,OC6:remain_open_no_positive_source_equivalent_artifact,OC12:remain_partial_narrowed_replay_ready_full_source_policy_archive_not_ready",
            "blocker_closure_allowed_by_id=OC4:False,OC6:False,OC12:False",
        ],
        "TFE full-T10 endpoint policy closure certificate validator": [
            "TFE full-T10 endpoint-policy closure certificate validation: PASS",
            "status=negative_full_T10_endpoint_policy_certificate_not_source_policy",
            "source_grid_policy_resolved_for_full_T10=False",
            "source_policy_rows_completed=0",
            "source_policy_execution_invoked=False",
            "can_close_now=False",
        ],
        "objective completion audit validator": [
            "status=not_complete_submission_standard_open",
            "objective_complete=False",
            "source_policy_rows=0/40",
            "blocking_open=3",
            "blocking_ids=OC4,OC6,OC12",
            "blocker_open_by_id=OC4:True,OC6:True,OC12:True",
            "blocker_closure_decision_by_id=OC4:remain_open_ready_for_authorized_execution_not_executed_not_promoted,OC6:remain_open_no_positive_source_equivalent_artifact,OC12:remain_partial_narrowed_replay_ready_full_source_policy_archive_not_ready",
            "blocker_closure_allowed_by_id=OC4:False,OC6:False,OC12:False",
            "source_policy_execution_invoked=False",
            "run_v047_invoked=False",
            "heavy_numerical_run_invoked=False",
            "v048_runner_invoked=False",
            "oc4_aliases=OC4/open/True/remain_open_ready_for_authorized_execution_not_executed_not_promoted/False/13/20/20/32/32/0",
            "oc4_evidence_files=6",
            "oc4_row_provenance=40/40/0/40/0",
            "oc4_provenance_handoff=source_policy_execution_handoff_ready_not_authorized_not_run/False/True",
            "oc6_evidence_files=9",
            "oc6_aliases=OC6/partial/True/remain_open_no_positive_source_equivalent_artifact/False/suite_specific_source_equivalent_reopen_conditions/2026-06-21/9/0/0/4/False/False",
            "oc6_candidate_backed_non_equivalent_runner_blocks=3",
            "oc6_latest_external_probe=2026-06-21/9/0/0/4/False/False",
            "oc6_runner_contract_preflight=contract_entrypoints_callable_candidate_backed_source_policy_open/3/3/3/3/0/4",
            "oc6_tfe_self_reproduction=attempted_not_reproducible_not_promoted/0/16",
            "oc6_public_code_recheck_status=public_code_rechecked_no_distinct_tfe_code_artifact_attempted_not_reproducible",
            "oc6_public_code_refresh=20/11/0/0/20",
            "oc12_aliases=OC12/partial/True/remain_partial_narrowed_replay_ready_full_source_policy_archive_not_ready/False/False/narrowed_claim_replay_and_audit_provenance_only/False",
            "oc12_archive_tfe_preflight=contract_entrypoints_callable_candidate_backed_source_policy_open/3/3/3/3/0/4",
            "oc12_archive_action_boundary=4/1/False/False/True/13/20",
            "oc12_archive_safe_action_ids=rebuild_read_only_audit_chain,rerun_read_only_validators,keep_narrowed_archive_provenance_only,monitor_reopen_conditions",
            "oc12_archive_opt_in_action_ids=authorized_b4_ra_hi_source_policy_execution",
        ],
        "CMAME review agent validator": [
            "oc12_archive_tfe_preflight=contract_entrypoints_callable_candidate_backed_source_policy_open/3/3/3/3/0/4",
            "oc12_archive_action_boundary=4/1/False/False/True/13/20",
            "oc6_reopen_latest_external_probe=2026-06-21/9/0/0/4/False/False",
            "oc12_archive_safe_action_ids=rebuild_read_only_audit_chain,rerun_read_only_validators,keep_narrowed_archive_provenance_only,monitor_reopen_conditions",
            "oc12_archive_opt_in_action_ids=authorized_b4_ra_hi_source_policy_execution",
            "blocker_open_by_id=OC4:True,OC6:True,OC12:True",
            "blocker_closure_decision_by_id=OC4:remain_open_ready_for_authorized_execution_not_executed_not_promoted,OC6:remain_open_no_positive_source_equivalent_artifact,OC12:remain_partial_narrowed_replay_ready_full_source_policy_archive_not_ready",
            "blocker_closure_allowed_by_id=OC4:False,OC6:False,OC12:False",
        ],
        "CMAME reproducibility package manifest validator": [
            "source_policy_closed=0/40",
            "source_policy_execution_handoff_driver=run_b4_source_policy_after_opt_in.sh",
            "source_policy_execution_handoff_driver_requires_exact_approval=True",
            "source_policy_execution_handoff_driver_does_not_authorize_execution=True",
            "tfe_runner_contract_preflight=contract_entrypoints_callable_candidate_backed_source_policy_open/3/3/3/3/0/4",
            "oc12_archive_tfe_preflight=contract_entrypoints_callable_candidate_backed_source_policy_open/3/3/3/3/0/4",
            "oc12_archive_action_boundary=4/1/False/False/True/13/20",
            "oc6_reopen_latest_external_probe=2026-06-21/9/0/0/4/False/False",
            "oc12_archive_safe_action_ids=rebuild_read_only_audit_chain,rerun_read_only_validators,keep_narrowed_archive_provenance_only,monitor_reopen_conditions",
            "oc12_archive_opt_in_action_ids=authorized_b4_ra_hi_source_policy_execution",
            "minimal_package_ready=False",
        ],
        "RA/HI source-policy output inventory validator": [
            "commands=13",
            "outputs=13/13",
            "source_policy_closed=0",
        ],
        "RA/HI source-policy closeout checklist validator": [
            "source_policy_closed=0/20",
            "ready_commands=13",
        ],
        "RA/HI source-policy promotion blocker matrix validator": [
            "source_policy_closed=0/20",
            "not_promoted=20",
        ],
        "RA/HI post-execution attempt certificate validator": [
            "rows=20",
            "source_policy_rows_promoted=0",
            "external_superiority_ready_rows=0",
            "source_policy_closed=0/40",
            "run_v047_invoked=False",
            "submission_ready=False",
        ],
        "B4 source-policy post-execution audit validator": [
            "b4 source-policy post-execution audit validation: PASS",
            "source_policy_rows_closed=0/40",
            "b4_can_close_now=False",
            "b7_can_close_now=False",
            "blocker_open_by_id=OC4:True,OC6:True,OC12:True",
            "blocker_closure_allowed_by_id=OC4:False,OC6:False,OC12:False",
        ],
        "B4 source-policy execution opt-in packet validator": [
            "ready_command_mapped_external_rows=20/40",
            "source_policy_closed_now=0/40",
            "commands_not_run_by_packet=True",
            "exact_approval_statement=present",
            "guarded_execution_driver_path=run_b4_source_policy_after_opt_in.sh",
            "driver_requires_exact_approval=True",
            "driver_does_not_authorize_execution=True",
            "execution_invoked_by_packet=False",
            "blocker_open_by_id=OC4:True,OC6:True,OC12:True",
            "blocker_closure_allowed_by_id=OC4:False,OC6:False,OC12:False",
        ],
        "B4 source-policy guarded driver validator": [
            "exact_approval_guard=True",
            "driver_command_count=13",
            "ra_allow_source_policy_1e_4_commands=5",
            "hi_execute_commands=8",
            "commands_match_opt_in_packet=True",
            "run_v047_invoked=False",
            "execution_invoked_by_validator=False",
        ],
        "B4 source-policy execution handoff package validator": [
            "source_policy_closed=0/40",
            "terminal_unable_to_reproduce_rows=20",
            "ready_command_count=13",
            "opt_in_required_command_count=13",
            "opt_in_required_mapped_external_rows=20",
            "execution_authorized=False",
            "guarded_execution_driver=run_b4_source_policy_after_opt_in.sh",
            "driver_requires_exact_approval=True",
            "command_preflight_freeze=PASS",
            "expected_output_schema_audit=PASS",
            "submission_ready=False",
        ],
        "B4 expected-output promotion-readiness blocker audit 20260620 validator": [
            "b4 expected-output promotion-readiness blocker audit validation: PASS",
            "schema_ready=13/13",
            "promotion_ready=0",
            "unique_rows=20",
            "source_policy_rows_closed=0",
            "blocker_open_by_id=OC4:True,OC6:True,OC12:True",
            "blocker_closure_allowed_by_id=OC4:False,OC6:False,OC12:False",
        ],
        "OC6 source-equivalent reopen-readiness audit 20260620 validator": [
            "OC6 source-equivalent reopen-readiness audit validation: PASS",
            "rows=20",
            "unable=20",
            "source_equivalent=0",
            "source_policy_closed=0",
            "oc6_blocker_id=OC6",
            "oc6_blocker_status=partial",
            "oc6_closure_decision=remain_open_no_positive_source_equivalent_artifact",
            "oc6_closure_allowed_now=False",
            "reopen_condition=suite_specific_source_equivalent_reopen_conditions",
            "latest_external_probe=2026-06-21/9/0/0/4/False/False",
            "latest_external_probe_boundary=0/0/4/False/False",
            "blocker_open_by_id=OC4:True,OC6:True,OC12:True",
            "blocker_closure_decision_by_id=OC4:remain_open_ready_for_authorized_execution_not_executed_not_promoted,OC6:remain_open_no_positive_source_equivalent_artifact,OC12:remain_partial_narrowed_replay_ready_full_source_policy_archive_not_ready",
            "blocker_closure_allowed_by_id=OC4:False,OC6:False,OC12:False",
        ],
        "B4 source-policy command preflight freeze 20260620 validator": [
            "b4 source-policy command preflight freeze validation: PASS",
            "ready_command_count=13",
            "unique_mapped_ra_hi_rows=20",
            "expected_artifacts=21/21",
            "commands_executed_by_freeze=False",
            "source_policy_closed=0/40",
        ],
        "B4 source-policy expected-output schema audit 20260620 validator": [
            "b4 expected-output schema audit validation: PASS",
            "commands=13/13",
            "artifacts=21/21",
            "csv_json_parseable=13/8",
            "source_policy_rows_closed=0",
        ],
        "full source-policy row provenance audit validator": [
            "rows=40",
            "provenance_preflight=40/40",
            "source_policy_closed=0/40",
            "promotion_ready_rows=0",
            "oc4_blocker_id=OC4",
            "oc4_blocker_status=open",
            "oc4_closure_decision=remain_open_ready_for_authorized_execution_not_executed_not_promoted",
            "oc4_closure_allowed_now=False",
            "ready_commands_mapped_rows=13/20",
            "traceability_unique_traced_declared_mismatch=20/32/32/0",
        ],
    }
    for name, cmd, cwd in steps:
        ok, output = run_step(name, cmd, cwd)
        for marker in required_output_markers.get(name, []):
            if marker not in output:
                print(f"[FAIL] {name} output contract")
                print(f"  missing_marker={marker}")
                ok = False
        failures += 0 if ok else 1
    failures += 0 if check_latex_log() else 1

    if failures:
        print(f"v047 paper package validation: FAIL ({failures} failed step(s))")
        return 1

    print("v047 paper package validation: PASS")
    print("submission_ready=False")
    print("mechanical_preflight_passed=True")
    print("quality_review_passed=False")
    print("note=run_v047.py was not invoked")
    if not args.latex:
        print("note=existing PDFs were checked; pass --latex to rebuild them from this wrapper")
    return 0


if __name__ == "__main__":
    sys.exit(main())
