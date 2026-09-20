#!/usr/bin/env python3
"""Read-only validator for the CMAME blocker-closure gate."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
from paper_paths import LATEX, package_path as manuscript_path
ROOT = PAPER.parent
GATE_MD = PAPER / "CMAME_BLOCKER_CLOSURE_GATE.md"
GATE_JSON = PAPER / "CMAME_BLOCKER_CLOSURE_GATE.json"
REVIEW = PAPER / "CMAME_SUBMISSION_READINESS_REVIEW.md"
AUDIT = PAPER / "CMAME_SUBMISSION_READINESS_AUDIT.md"
MAIN_TEX = LATEX / "main_cmame.tex"
FLAT_TEX = LATEX / "cmame_submission_flat" / "main_cmame_submission.tex"
LIMITATION_FIGURE = LATEX / "figures" / "claim_boundary_limitations.png"
FLAT_LIMITATION_FIGURE = LATEX / "cmame_submission_flat" / "Figure_8_claim_boundary_limitations.png"
BASELINE_WORK_FIGURE = LATEX / "figures" / "coarse_baseline_work_precision.png"
FLAT_BASELINE_WORK_FIGURE = LATEX / "cmame_submission_flat" / "Figure_9_coarse_baseline_work_precision.png"
TRUE_DYNAMIC_ORDER_FIGURE = LATEX / "figures" / "closed_loop_true_dynamic_order.png"
FLAT_TRUE_DYNAMIC_ORDER_FIGURE = LATEX / "cmame_submission_flat" / "Figure_10_closed_loop_true_dynamic_order.png"
METHOD_ARCH_FIGURE = LATEX / "figures" / "method_stage_architecture.png"
FLAT_METHOD_ARCH_FIGURE = LATEX / "cmame_submission_flat" / "Figure_11_method_stage_architecture.png"
ALL_METHOD_MATRIX_FIGURE = LATEX / "figures" / "all_method_result_matrix.png"
FLAT_ALL_METHOD_MATRIX_FIGURE = LATEX / "cmame_submission_flat" / "Figure_12_all_method_result_matrix.png"
WORK_PRECISION_COMPENDIUM_FIGURE = LATEX / "figures" / "work_precision_compendium.png"
FLAT_WORK_PRECISION_COMPENDIUM_FIGURE = LATEX / "cmame_submission_flat" / "Figure_13_work_precision_compendium.png"
FIGURE_SET_AUDIT = PAPER / "CMAME_FIGURE_SET_AUDIT.md"
FIGURE_SET_AUDIT_JSON = PAPER / "CMAME_FIGURE_SET_AUDIT.json"
VISUAL_AUDIT = PAPER / "CMAME_VISUAL_LEGIBILITY_AUDIT.md"
VISUAL_AUDIT_JSON = PAPER / "CMAME_VISUAL_LEGIBILITY_AUDIT.json"
RELATED_WORK_AUDIT = PAPER / "CMAME_RELATED_WORK_AUDIT.md"
RELATED_WORK_AUDIT_JSON = PAPER / "CMAME_RELATED_WORK_AUDIT.json"
PROSE_RESIDUE_AUDIT = PAPER / "CMAME_PROSE_RESIDUE_AUDIT.md"
PROSE_RESIDUE_AUDIT_JSON = PAPER / "CMAME_PROSE_RESIDUE_AUDIT.json"
MANIFEST = PAPER / "SUBMISSION_ARTIFACT_MANIFEST.json"
ORDER_GATE = PAPER / "ORDER_ACCEPTANCE_GATE.json"
DYNAMIC_ORACLE = PAPER / "DYNAMIC_ROW_ORACLE_GATE.json"
EXTERNAL_BASELINE = PAPER / "CMAME_EXTERNAL_BASELINE_GATE.json"
EXTERNAL_ACCEPTANCE_SHEET = PAPER / "EXTERNAL_SAME_TEST_ACCEPTANCE_SHEET.json"
HI2022_POLICY_DECISION_AUDIT = PAPER / "HI2022_POLICY_DECISION_AUDIT.json"
HI2022_POLICY_DECISION_AUDIT_MD = PAPER / "HI2022_POLICY_DECISION_AUDIT.md"
HI2022_SOURCE_POLICY_AUDIT = PAPER / "HI2022_SOURCE_POLICY_ROW_AUDIT.json"
HI2022_SOURCE_POLICY_AUDIT_MD = PAPER / "HI2022_SOURCE_POLICY_ROW_AUDIT.md"
EXTERNAL_SUITE_DEMOTION_LEDGER = PAPER / "EXTERNAL_SUITE_DEMOTION_LEDGER.json"
EXTERNAL_SUITE_DEMOTION_LEDGER_MD = PAPER / "EXTERNAL_SUITE_DEMOTION_LEDGER.md"
B2_REMAINING_WORK = PAPER / "B2_SOURCE_POLICY_REMAINING_WORK_MANIFEST.json"
B2_REMAINING_WORK_MD = PAPER / "B2_SOURCE_POLICY_REMAINING_WORK_MANIFEST.md"
RA2021_SOURCE_POLICY_AUDIT = PAPER / "RA2021_SOURCE_POLICY_ROW_AUDIT.json"
RA2021_SOURCE_POLICY_AUDIT_MD = PAPER / "RA2021_SOURCE_POLICY_ROW_AUDIT.md"
TFE_SOURCE_POLICY_AUDIT = PAPER / "TFE_SOURCE_POLICY_ROW_AUDIT.json"
TFE_SOURCE_POLICY_AUDIT_MD = PAPER / "TFE_SOURCE_POLICY_ROW_AUDIT.md"
TFE_ALGORITHM_LITERAL_ENDPOINT_PROBE = PAPER / "TFE_ALGORITHM_LITERAL_ENDPOINT_PROBE.json"
TFE_ALGORITHM_LITERAL_ENDPOINT_PROBE_MD = PAPER / "TFE_ALGORITHM_LITERAL_ENDPOINT_PROBE.md"
TFE_ALGORITHM_LITERAL_ENDPOINT_PROBE_CSV = PAPER / "TFE_ALGORITHM_LITERAL_ENDPOINT_PROBE.csv"
TFE_ALGORITHM_LITERAL_ENDPOINT_PROBE_VALIDATOR = PAPER / "validate_tfe_algorithm_literal_endpoint_probe.py"
TFE_SOURCE_GRID_COMPATIBILITY_AUDIT = PAPER / "TFE_SOURCE_GRID_COMPATIBILITY_AUDIT.json"
TFE_SOURCE_GRID_COMPATIBILITY_AUDIT_MD = PAPER / "TFE_SOURCE_GRID_COMPATIBILITY_AUDIT.md"
TFE_SOURCE_GRID_COMPATIBILITY_VALIDATOR = PAPER / "validate_tfe_source_grid_compatibility_audit.py"
TFE_ALGORITHM_LITERAL_WORK_PRECISION = PAPER / "TFE_ALGORITHM_LITERAL_WORK_PRECISION_AUDIT.json"
TFE_ALGORITHM_LITERAL_WORK_PRECISION_MD = PAPER / "TFE_ALGORITHM_LITERAL_WORK_PRECISION_AUDIT.md"
TFE_ALGORITHM_LITERAL_WORK_PRECISION_CSV = PAPER / "TFE_ALGORITHM_LITERAL_WORK_PRECISION_AUDIT.csv"
TFE_ALGORITHM_LITERAL_WORK_PRECISION_FIGURE = LATEX / "figures" / "tfe_algorithm_literal_work_precision.png"
TFE_ALGORITHM_LITERAL_WORK_PRECISION_VALIDATOR = PAPER / "validate_tfe_algorithm_literal_work_precision_audit.py"
B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET = PAPER / "B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json"
B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET_MD = PAPER / "B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.md"
B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET_VALIDATOR = PAPER / "validate_b4_source_policy_execution_opt_in_packet.py"
B4_SOURCE_POLICY_POST_EXECUTION_AUDIT = PAPER / "B4_SOURCE_POLICY_POST_EXECUTION_AUDIT.json"
B4_SOURCE_POLICY_POST_EXECUTION_AUDIT_MD = PAPER / "B4_SOURCE_POLICY_POST_EXECUTION_AUDIT.md"
B4_SOURCE_POLICY_POST_EXECUTION_AUDIT_VALIDATOR = PAPER / "validate_b4_source_policy_post_execution_audit.py"
COMPARISON_RECONCILIATION = PAPER / "COMPARISON_OBJECTIVE_CLOSURE_RECONCILIATION_AUDIT.json"
COMPARISON_RECONCILIATION_MD = PAPER / "COMPARISON_OBJECTIVE_CLOSURE_RECONCILIATION_AUDIT.md"
ALL_SOURCE_POLICY = PAPER / "ALL_EXAMPLES_SOURCE_POLICY_AUDIT.json"
ALL_SOURCE_POLICY_MD = PAPER / "ALL_EXAMPLES_SOURCE_POLICY_AUDIT.md"
ALL_METHOD_DISPOSITION = PAPER / "ALL_METHOD_EXAMPLE_CLAIM_DISPOSITION_AUDIT.json"
ALL_METHOD_DISPOSITION_MD = PAPER / "ALL_METHOD_EXAMPLE_CLAIM_DISPOSITION_AUDIT.md"
FOUR_EXAMPLE_DASHBOARD = PAPER / "FOUR_EXAMPLE_SOURCE_POLICY_DASHBOARD.json"
PROOF_CONTRACT = PAPER / "CMAME_PROOF_CONTRACT_GATE.json"
PROOF_CLOSURE_MANIFEST = PAPER / "PROOF_CLOSURE_MANIFEST.json"
STRICT_PROOF_AUDIT = PAPER / "CMAME_STRICT_PROOF_AUDIT.json"
STRICT_PROOF_AUDIT_MD = PAPER / "CMAME_STRICT_PROOF_AUDIT.md"
KINEMATIC_DEFECT = PAPER / "KINEMATIC_ROW_DEFECT_CERTIFICATE.json"
NEWTON_EULER_OBLIGATION = PAPER / "NEWTON_EULER_DEFECT_OBLIGATION_GATE.json"
NEWTON_EULER_OBLIGATION_MD = PAPER / "NEWTON_EULER_DEFECT_OBLIGATION_GATE.md"
NEWTON_EULER_SYMBOLIC_TARGET = PAPER / "NEWTON_EULER_SYMBOLIC_TARGET_AUDIT.json"
NEWTON_EULER_SYMBOLIC_TARGET_MD = PAPER / "NEWTON_EULER_SYMBOLIC_TARGET_AUDIT.md"
NEWTON_EULER_AD_EXPANDED_ROW_ORACLE = PAPER / "NEWTON_EULER_AD_EXPANDED_ROW_ORACLE_AUDIT.json"
B1_SYMBOLIC_ROW_ORACLE_CLOSURE = PAPER / "B1_SYMBOLIC_ROW_ORACLE_CLOSURE_CERTIFICATE.json"
B1_AD_EXPANDED_SYMBOLIC_ORACLE_CLOSURE = PAPER / "B1_AD_EXPANDED_SYMBOLIC_ORACLE_CLOSURE_CERTIFICATE.json"
NEWTON_EULER_DYNAMIC_ROW_CLOSURE_CONTRACT = PAPER / "NEWTON_EULER_DYNAMIC_ROW_CLOSURE_CONTRACT.json"
D5_DYNAMIC_DEFECT_READINESS_AUDIT = PAPER / "D5_DYNAMIC_DEFECT_READINESS_AUDIT.json"
PROOF_SOLVER_SCALE_AUDIT = PAPER / "PROOF_SOLVER_SCALE_AUDIT.md"
PROOF_SOLVER_SCALE_AUDIT_JSON = PAPER / "PROOF_SOLVER_SCALE_AUDIT.json"
CROSS_CASES = PAPER / "CROSS_PAPER_BENCHMARK_CASES.json"
V048 = ROOT / "v048_cross_paper_same_test_benchmarks" / "results"
COARSE_FIRST = V048 / "coarse_first_external_readiness_gate.json"
COARSE_PROBE = V048 / "closed_loop_coarse_dynamic_order_probe.json"
TRUE_DYNAMIC_NEWTON = V048 / "closed_loop_true_dynamic_newton_coarse_order.json"
PUBLIC_WORK = V048 / "closed_loop_true_dynamic_public_work_precision.json"
STRICT_COMMON = V048 / "closed_loop_true_dynamic_strict_common_reference.json"
PERFORMANCE = V048 / "four_example_performance_summary.json"
TFE_SAME_TEST_WORK_PRECISION = V048 / "tfe_source_pendulum_same_test_work_precision.json"
TFE_SAME_TEST_WORK_PRECISION_MD = V048 / "tfe_source_pendulum_same_test_work_precision.md"
TFE_SAME_TEST_WORK_PRECISION_RAW_CSV = V048 / "tfe_source_pendulum_same_test_work_precision_rows.csv"
TFE_SAME_TEST_WORK_PRECISION_SUMMARY_CSV = V048 / "tfe_source_pendulum_same_test_work_precision_summary.csv"
TFE_SAME_TEST_WORK_PRECISION_FIGURE = V048 / "tfe_source_pendulum_same_test_work_precision.png"
TFE_SAME_TEST_WORK_PRECISION_VALIDATOR = ROOT / "v048_cross_paper_same_test_benchmarks" / "validate_tfe_source_pendulum_same_test_work_precision.py"


EXPECTED_BLOCKERS = {f"B{index}" for index in range(1, 9)}
EXPECTED_OPEN_BLOCKERS: set[str] = set()
EXPECTED_CLOSED_BLOCKERS = ["B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8"]
EXPECTED_EXAMPLES = ["single_pendulum", "double_pendulum", "four_link", "slider_crank"]
EXPECTED_DYNAMIC_ORDER_EXAMPLES = ["single_pendulum", "double_pendulum"]
EXPECTED_COVERAGE_ONLY_EXAMPLES = ["four_link", "slider_crank"]


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


def require_tokens(checks: Checks, text: str, tokens: list[str], label: str) -> None:
    for token in tokens:
        checks.check(contains_normalized(text, token), f"{label} missing token: {token}")


def argumentative_body(tex: str) -> str:
    """Return the paper body before availability/reproducibility appendices."""
    start = tex.find(r"\begin{abstract}")
    end = tex.find(r"\section*{Data availability}")
    if start < 0 or end < 0 or end <= start:
        return tex
    return tex[start:end]


def main() -> int:
    checks = Checks()
    try:
        gate_md = read_text(GATE_MD)
        gate = read_json(GATE_JSON)
        review = read_text(REVIEW)
        audit = read_text(AUDIT)
        main_tex = read_text(MAIN_TEX)
        flat_tex = read_text(FLAT_TEX)
        visual_audit = read_text(VISUAL_AUDIT)
        visual_audit_json = read_json(VISUAL_AUDIT_JSON)
        related_work_audit = read_text(RELATED_WORK_AUDIT)
        related_work_audit_json = read_json(RELATED_WORK_AUDIT_JSON)
        prose_residue_audit = read_text(PROSE_RESIDUE_AUDIT)
        prose_residue_audit_json = read_json(PROSE_RESIDUE_AUDIT_JSON)
        manifest = read_json(MANIFEST)
        order_gate = read_json(ORDER_GATE)
        dynamic_oracle = read_json(DYNAMIC_ORACLE)
        external_baseline = read_json(EXTERNAL_BASELINE)
        external_acceptance_sheet = read_json(EXTERNAL_ACCEPTANCE_SHEET)
        hi2022_policy_decision = read_json(HI2022_POLICY_DECISION_AUDIT)
        hi2022_policy_decision_md = read_text(HI2022_POLICY_DECISION_AUDIT_MD)
        hi2022_source_policy_audit = read_json(HI2022_SOURCE_POLICY_AUDIT)
        hi2022_source_policy_audit_md = read_text(HI2022_SOURCE_POLICY_AUDIT_MD)
        external_suite_demotion = read_json(EXTERNAL_SUITE_DEMOTION_LEDGER)
        external_suite_demotion_md = read_text(EXTERNAL_SUITE_DEMOTION_LEDGER_MD)
        b2_remaining_work = read_json(B2_REMAINING_WORK)
        b2_remaining_work_md = read_text(B2_REMAINING_WORK_MD)
        ra2021_source_policy_audit = read_json(RA2021_SOURCE_POLICY_AUDIT)
        ra2021_source_policy_audit_md = read_text(RA2021_SOURCE_POLICY_AUDIT_MD)
        tfe_source_policy_audit = read_json(TFE_SOURCE_POLICY_AUDIT)
        tfe_source_policy_audit_md = read_text(TFE_SOURCE_POLICY_AUDIT_MD)
        tfe_algorithm_literal_endpoint_probe = read_json(TFE_ALGORITHM_LITERAL_ENDPOINT_PROBE)
        tfe_algorithm_literal_endpoint_probe_md = read_text(TFE_ALGORITHM_LITERAL_ENDPOINT_PROBE_MD)
        tfe_source_grid_compatibility = read_json(TFE_SOURCE_GRID_COMPATIBILITY_AUDIT)
        tfe_source_grid_compatibility_md = read_text(TFE_SOURCE_GRID_COMPATIBILITY_AUDIT_MD)
        tfe_algorithm_literal_work_precision = read_json(TFE_ALGORITHM_LITERAL_WORK_PRECISION)
        tfe_algorithm_literal_work_precision_md = read_text(TFE_ALGORITHM_LITERAL_WORK_PRECISION_MD)
        b4_execution_opt_in_packet = read_json(B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET)
        b4_execution_opt_in_packet_md = read_text(B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET_MD)
        b4_source_policy_post_execution_audit = read_json(B4_SOURCE_POLICY_POST_EXECUTION_AUDIT)
        b4_source_policy_post_execution_audit_md = read_text(B4_SOURCE_POLICY_POST_EXECUTION_AUDIT_MD)
        comparison_reconciliation = read_json(COMPARISON_RECONCILIATION)
        comparison_reconciliation_md = read_text(COMPARISON_RECONCILIATION_MD)
        all_source_policy = read_json(ALL_SOURCE_POLICY)
        all_source_policy_md = read_text(ALL_SOURCE_POLICY_MD)
        all_method_disposition = read_json(ALL_METHOD_DISPOSITION)
        all_method_disposition_md = read_text(ALL_METHOD_DISPOSITION_MD)
        four_example_dashboard = read_json(FOUR_EXAMPLE_DASHBOARD)
        figure_set_audit = read_text(FIGURE_SET_AUDIT)
        figure_set_audit_json = read_json(FIGURE_SET_AUDIT_JSON)
        proof_contract = read_json(PROOF_CONTRACT)
        proof_closure_manifest = read_json(PROOF_CLOSURE_MANIFEST)
        strict_proof_audit = read_json(STRICT_PROOF_AUDIT)
        strict_proof_audit_md = read_text(STRICT_PROOF_AUDIT_MD)
        kinematic_defect = read_json(KINEMATIC_DEFECT)
        newton_euler_obligation = read_json(NEWTON_EULER_OBLIGATION)
        newton_euler_obligation_md = read_text(NEWTON_EULER_OBLIGATION_MD)
        newton_euler_symbolic_target = read_json(NEWTON_EULER_SYMBOLIC_TARGET)
        newton_euler_symbolic_target_md = read_text(NEWTON_EULER_SYMBOLIC_TARGET_MD)
        newton_euler_ad_expanded_row_oracle = read_json(NEWTON_EULER_AD_EXPANDED_ROW_ORACLE)
        b1_symbolic_row_oracle_closure = read_json(B1_SYMBOLIC_ROW_ORACLE_CLOSURE)
        b1_ad_expanded_symbolic_oracle_closure = read_json(B1_AD_EXPANDED_SYMBOLIC_ORACLE_CLOSURE)
        newton_euler_dynamic_contract = read_json(NEWTON_EULER_DYNAMIC_ROW_CLOSURE_CONTRACT)
        d5_dynamic_readiness = read_json(D5_DYNAMIC_DEFECT_READINESS_AUDIT)
        proof_solver_scale_audit = read_text(PROOF_SOLVER_SCALE_AUDIT)
        proof_solver_scale_audit_json = read_json(PROOF_SOLVER_SCALE_AUDIT_JSON)
        cases = read_json(CROSS_CASES)
        tfe_same_test_work_precision = read_json(TFE_SAME_TEST_WORK_PRECISION)
        tfe_same_test_work_precision_md = read_text(TFE_SAME_TEST_WORK_PRECISION_MD)
        coarse_first = read_json(COARSE_FIRST)
        coarse_probe = read_json(COARSE_PROBE)
        true_dynamic_newton = read_json(TRUE_DYNAMIC_NEWTON)
        public_work = read_json(PUBLIC_WORK)
        strict_common = read_json(STRICT_COMMON)
        performance = read_json(PERFORMANCE)
    except Exception as exc:  # noqa: BLE001 - concise CLI failure.
        print(f"cmame_blocker_closure_gate=FAIL\n- {exc}")
        return 1

    checks.check(gate.get("schema") == "cmame-blocker-closure-gate-v1", "gate schema changed")
    checks.check(
        gate.get("status") == "closed_narrowed_claim_subcheck_global_submission_open",
        "gate status changed",
    )
    checks.check(gate.get("global_submission_standard_met") is False, "gate overclaims global standard")
    checks.check(gate.get("global_open_blockers") == ["OC4", "OC6", "OC12"], "gate global blockers changed")
    checks.check(gate.get("narrowed_claim_open_blockers") == [], "gate narrowed blockers changed")
    checks.check(gate.get("narrowed_claim_open_blocker_count") == 0, "gate narrowed blocker count changed")
    checks.check(
        gate.get("submission_ready") is False,
        "gate must keep global submission_ready false outside the narrowed claim",
    )
    checks.check(
        gate.get("legacy_submission_ready_under_narrowed_claim") is True,
        "legacy narrowed-claim readiness marker changed",
    )
    checks.check(
        gate.get("submission_ready_scope") == "global_submission_ready_false_narrowed_claim_only",
        "gate submission_ready scope must separate global and narrowed readiness",
    )
    alias_warning = gate.get("narrowed_claim_alias_warning", "")
    checks.check(
        "validator-only compatibility aliases" in alias_warning
        and "do not read" in alias_warning
        and "global submission readiness" in alias_warning
        and "legacy_submission_ready_under_narrowed_claim" in alias_warning
        and "submission_ready_under_narrowed_claim" in alias_warning,
        "narrowed-claim alias warning missing or too weak",
    )
    checks.check(
        gate.get("submission_ready_under_narrowed_claim") is True,
        "narrowed-claim submission-ready marker changed",
    )
    checks.check(gate.get("proof_submission_ready") is False, "proof submission-ready boundary changed")
    checks.check(
        gate.get("full_source_policy_submission_ready") is False,
        "full source-policy submission-ready boundary changed",
    )
    checks.check(gate.get("mechanical_preflight_passed") is True, "mechanical preflight marker changed")
    checks.check(gate.get("quality_review_passed") is True, "gate did not mark quality review passed")
    checks.check(
        gate.get("closure_rule", {}).get("open_blocker_count") == 0,
        "gate open blocker count changed",
    )
    checks.check(
        gate.get("closure_rule", {}).get("closed_blockers") == EXPECTED_CLOSED_BLOCKERS,
        "gate closed blocker list changed",
    )
    checks.check(visual_audit_json.get("status") == "b5_closed_mechanism_visual_reproducibility_checked", "visual audit status changed")
    checks.check(visual_audit_json.get("closed_blocker", {}).get("id") == "B5", "visual audit does not close B5")
    checks.check(visual_audit_json.get("open_blocker_count_after_closure") == 7, "visual audit open blocker count changed")
    checks.check(visual_audit_json.get("execution_policy", {}).get("default_1e-4_required") is False, "visual audit incorrectly requires default 1e-4")
    checks.check(related_work_audit_json.get("status") == "b8_closed_related_work_depth_checked", "related-work audit status changed")
    checks.check(related_work_audit_json.get("closed_blocker", {}).get("id") == "B8", "related-work audit does not close B8")
    checks.check(related_work_audit_json.get("open_blocker_count_after_closure") == 6, "related-work audit open blocker count changed")
    checks.check(related_work_audit_json.get("closed_blockers") == ["B5", "B8"], "related-work audit closed blockers changed")
    checks.check(related_work_audit_json.get("execution_policy", {}).get("default_1e-4_required") is False, "related-work audit incorrectly requires default 1e-4")
    strict_boundary = strict_proof_audit.get("two_layer_proof_boundary", {})
    strict_primitive = strict_proof_audit.get("primitive_taylor_route", {})
    strict_direct_corollary = strict_proof_audit.get("direct_route_ps3_corollary", {})
    checks.check(strict_proof_audit.get("schema") == "cmame-strict-proof-audit-v1", "strict proof audit schema changed")
    checks.check(
        strict_proof_audit.get("status")
        == "strict_conditional_residual_bridge_proof_audited_b3_closed_submission_not_ready",
        "strict proof audit status changed",
    )
    checks.check(strict_proof_audit.get("submission_ready") is False, "strict proof audit must not claim submission ready")
    checks.check(
        strict_proof_audit.get("manuscript_strict_proof_features", {}).get("strict_conditional_math_proof_present")
        is True,
        "strict conditional residual-bridge proof marker missing",
    )
    checks.check(strict_boundary.get("b1_status") == "closed", "strict proof audit must record B1 closure")
    checks.check(
        strict_boundary.get("b1_closed_by_ad_expanded_symbolic_certificate") is True,
        "strict proof audit lost B1 AD-expanded closure marker",
    )
    checks.check(strict_boundary.get("b3_status") == "closed", "strict proof audit must close B3 direct route")
    checks.check(
        strict_boundary.get("b3_direct_proof_review_passed") is True,
        "strict proof audit lost B3 direct-review progress marker",
    )
    checks.check(
        "strict_implementation_proof_complete" not in strict_boundary,
        "strict proof audit must route-scope implementation proof readiness",
    )
    checks.check(
        strict_boundary.get("direct_route_strict_residual_bridge_kantorovich_proof_complete") is True,
        "strict proof audit lost direct-route proof completion marker",
    )
    checks.check(
        strict_boundary.get("symbolic_primitive_route_strict_implementation_proof_complete") is False,
        "strict proof audit overclaims symbolic/primitive implementation proof",
    )
    checks.check(strict_boundary.get("two_layer_boundary_consistent") is True, "strict proof audit boundary consistency changed")
    checks.check(strict_primitive.get("dependency_graph_recorded") is True, "strict proof primitive dependency graph missing")
    checks.check(
        strict_primitive.get("root_lift_primitives") == ["P_state", "P_acc"],
        "strict proof primitive root list changed",
    )
    checks.check(
        strict_primitive.get("root_dependent_primitives") == ["P_lambda"],
        "strict proof primitive root-dependent list changed",
    )
    checks.check(
        strict_primitive.get("conditional_downstream_primitives") == ["P_geom", "P_gyro"],
        "strict proof primitive downstream list changed",
    )
    checks.check(strict_primitive.get("dependency_edge_count") == 5, "strict proof primitive edge count changed")
    checks.check(
        strict_direct_corollary.get("certificate_closed") is True,
        "strict proof direct-route PS3 certificate not closed",
    )
    checks.check(
        strict_direct_corollary.get("direct_route_ps3_input_closed") is True,
        "strict proof direct-route PS3 input not closed",
    )
    checks.check(
        strict_direct_corollary.get("direct_route_state_lift_rate_closed") is True,
        "strict proof direct-route state lift not closed",
    )
    checks.check(
        strict_direct_corollary.get("direct_route_h_weighted_acceleration_input_closed") is True,
        "strict proof direct-route h-acceleration not closed",
    )
    checks.check(
        strict_direct_corollary.get("strict_proof_steps_closed") == 4
        and strict_direct_corollary.get("strict_proof_steps_total") == 4,
        "strict proof direct-route proof step count changed",
    )
    checks.check(
        strict_direct_corollary.get("primitive_route_closed") is False,
        "strict proof direct-route corollary unexpectedly closes primitive route",
    )
    checks.check(
        strict_direct_corollary.get("primitive_route_induced_taylor_bounds_proved") == 0,
        "strict proof direct-route corollary unexpectedly proves primitive Taylor bounds",
    )
    checks.check(
        "B1 is closed by `B1_AD_EXPANDED_SYMBOLIC_ORACLE_CLOSURE_CERTIFICATE.md`; this audit scopes only the B1/B3 proof boundary."
        in strict_proof_audit_md,
        "strict proof audit markdown boundary missing",
    )
    checks.check(
        "Narrowed-claim B4/B6/B7 subcheck statuses are recorded elsewhere (narrowed-only; not source-policy row closure): `closed/closed/closed`."
        in strict_proof_audit_md,
        "strict proof audit narrowed-claim boundary missing",
    )
    hi2022_source_policy = hi2022_policy_decision.get("source_policy_required_before_external_superiority", {})
    hi2022_bounded = hi2022_policy_decision.get("existing_bounded_evidence", {})
    hi2022_execution = hi2022_policy_decision.get("execution_policy", {})
    checks.check(
        hi2022_policy_decision.get("schema") == "hi2022-policy-decision-audit-v1",
        "HI2022 policy-decision audit schema changed",
    )
    checks.check(
        hi2022_policy_decision.get("status") == "bounded_T0p1_rows_complete_full_T8_source_policy_open",
        "HI2022 policy-decision status changed",
    )
    checks.check(
        hi2022_policy_decision.get("evidence_class") == "bounded_pilot_only_not_source_policy_reproduction",
        "HI2022 evidence class changed",
    )
    checks.check(hi2022_bounded.get("row_count") == 24, "HI2022 bounded row count changed")
    checks.check(hi2022_bounded.get("ok_row_count") == 24, "HI2022 bounded ok row count changed")
    checks.check(hi2022_bounded.get("group_count") == 8, "HI2022 bounded group count changed")
    checks.check(hi2022_bounded.get("groups_with_three_step_sizes") == 8, "HI2022 bounded three-step group count changed")
    checks.check(hi2022_bounded.get("t_end_values") == [0.1], "HI2022 bounded horizon changed")
    checks.check(hi2022_bounded.get("step_sizes") == [0.005, 0.01, 0.02], "HI2022 bounded step sizes changed")
    checks.check(
        hi2022_source_policy.get("full_T8_policy_completed") is False,
        "HI2022 full T=8 source policy unexpectedly closed",
    )
    checks.check(
        hi2022_source_policy.get("accepted_for_external_superiority") is False,
        "HI2022 external superiority unexpectedly accepted",
    )
    checks.check(
        hi2022_source_policy.get("accepted_source_policy_dynamic_order_examples_count") == 0,
        "HI2022 source-policy dynamic-order count changed",
    )
    checks.check(
        hi2022_source_policy_audit.get("schema") == "hi2022-source-policy-row-audit-v1",
        "HI2022 source-policy row audit schema changed",
    )
    checks.check(
        hi2022_source_policy_audit.get("status")
        == "bounded_T0p1_rows_complete_full_T8_source_policy_rows_not_closed",
        "HI2022 source-policy row audit status changed",
    )
    checks.check(
        hi2022_source_policy_audit.get("active_b2_flagged_rows") == 3,
        "HI2022 source-policy active B2 rows changed",
    )
    checks.check(
        hi2022_source_policy_audit.get("bounded_ok_row_count")
        == hi2022_source_policy_audit.get("bounded_row_count")
        == 24,
        "HI2022 source-policy bounded row count changed",
    )
    checks.check(
        hi2022_source_policy_audit.get("bounded_groups_with_three_step_sizes")
        == hi2022_source_policy_audit.get("bounded_group_count")
        == 8,
        "HI2022 source-policy bounded group count changed",
    )
    checks.check(
        hi2022_source_policy_audit.get("source_policy_closed_rows") == 0,
        "HI2022 source-policy rows unexpectedly closed",
    )
    checks.check(
        hi2022_source_policy_audit.get("decision", {}).get("can_close_hi2022_b2_requirement_now") is False,
        "HI2022 source-policy audit unexpectedly closes B2",
    )
    checks.check(
        hi2022_source_policy_audit.get("external_superiority_claim_allowed") is False,
        "HI2022 source-policy audit overclaims external superiority",
    )
    checks.check(
        hi2022_execution.get("default_1e_4_required") is False,
        "HI2022 audit incorrectly requires default 1e-4",
    )
    checks.check(hi2022_execution.get("run_v047_invoked") is False, "HI2022 audit invoked run_v047")
    checks.check(hi2022_execution.get("heavy_numerical_run_invoked") is False, "HI2022 audit invoked a heavy numerical run")
    demotion_execution = external_suite_demotion.get("execution_policy", {})
    demoted_suites = external_suite_demotion.get("demoted_suites", [])
    demoted_by_suite = {item.get("suite_id"): item for item in demoted_suites if isinstance(item, dict)}
    demoted_vp = demoted_by_suite.get("vp2024_velocity_partitioning", {})
    demoted_hi = demoted_by_suite.get("hi2022_half_implicit", {})
    demoted_ra = demoted_by_suite.get("ra2021_absolute_coordinate", {})
    demoted_tfe = demoted_by_suite.get("tfe2026_original_pendulum", {})
    checks.check(
        external_suite_demotion.get("schema") == "external-suite-demotion-ledger-v1",
        "external suite demotion ledger schema changed",
    )
    checks.check(
        external_suite_demotion.get("status") == "all_external_suites_demoted_from_external_superiority_scope",
        "external suite demotion ledger status changed",
    )
    checks.check(external_suite_demotion.get("submission_ready") is False, "demotion ledger overclaims submission readiness")
    checks.check(external_suite_demotion.get("demoted_suite_count") == 4, "demoted suite count changed")
    checks.check(
        external_suite_demotion.get("b2_subrequirements_closed_by_demotion")
        == [
            "vp2024_code_resolution_or_demotion",
            "hi2022_public_code_same_test_rows",
            "ra2021_public_code_same_test_rows",
            "original_tfe_pendulum_error_order_work_rows",
        ],
        "B2 demotion subrequirements changed",
    )
    checks.check(external_suite_demotion.get("demoted_source_policy_rows") == 16, "demoted source-policy rows changed")
    checks.check(external_suite_demotion.get("demoted_source_policy_flagged_rows") == 15, "demoted flagged rows changed")
    checks.check(
        external_suite_demotion.get("active_source_policy_flagged_rows_after_demotions") == 0,
        "active flagged rows after demotion changed",
    )
    checks.check(demoted_vp.get("suite_id") == "vp2024_velocity_partitioning", "demoted suite id changed")
    checks.check(demoted_vp.get("distinct_public_code_path_found") is False, "VP code path unexpectedly found")
    checks.check(demoted_vp.get("proxy_is_source_policy_reproduction") is False, "VP proxy promoted to source policy")
    checks.check(demoted_hi.get("suite_id") == "hi2022_half_implicit", "HI2022 demoted suite id missing")
    checks.check(demoted_hi.get("t8_coarse_complete_groups") == 4, "HI2022 T=8 demotion evidence changed")
    checks.check(demoted_hi.get("t8_coarse_group_count") == 8, "HI2022 T=8 demotion group count changed")
    checks.check(demoted_ra.get("suite_id") == "ra2021_absolute_coordinate", "RA2021 demoted suite id missing")
    checks.check(demoted_ra.get("source_policy_rows") == 5, "RA2021 demoted row count changed")
    checks.check(demoted_ra.get("source_policy_flagged_rows") == 5, "RA2021 demoted flagged-row count changed")
    checks.check(demoted_tfe.get("suite_id") == "tfe2026_original_pendulum", "TFE demoted suite id missing")
    checks.check(demoted_tfe.get("source_policy_rows") == 4, "TFE demoted row count changed")
    checks.check(demoted_tfe.get("source_policy_flagged_rows") == 4, "TFE demoted flagged-row count changed")
    checks.check(
        b2_remaining_work.get("schema") == "b2-source-policy-remaining-work-manifest-v1",
        "B2 remaining-work manifest schema changed",
    )
    checks.check(
        b2_remaining_work.get("status") == "route_b_all_external_suites_demoted_no_active_external_superiority_rows",
        "B2 remaining-work manifest status changed",
    )
    checks.check(b2_remaining_work.get("row_count") == 15, "B2 remaining-work row count changed")
    checks.check(b2_remaining_work.get("active_flagged_row_count") == 0, "B2 active flagged rows changed")
    checks.check(b2_remaining_work.get("demoted_flagged_row_count") == 15, "B2 demoted flagged rows changed")
    checks.check(b2_remaining_work.get("source_policy_closed_rows") == 0, "B2 source-policy closed rows changed")
    checks.check(
        b2_remaining_work.get("external_superiority_ready_rows") == 0,
        "B2 external-superiority-ready rows changed",
    )
    checks.check(
        b2_remaining_work.get("b2_closed_by_demotion")
        == [
            "vp2024_code_resolution_or_demotion",
            "hi2022_public_code_same_test_rows",
            "ra2021_public_code_same_test_rows",
            "original_tfe_pendulum_error_order_work_rows",
        ],
        "B2 remaining-work demotion closure changed",
    )
    checks.check(
        b2_remaining_work.get("b2_remaining_requirements") == [],
        "B2 remaining-work requirements changed",
    )
    checks.check(b2_remaining_work.get("b2_can_close_now") is True, "B2 remaining-work should close B2 by Route B claim demotion")
    checks.check(b2_remaining_work.get("b4_can_close_now") is False, "B2 remaining-work incorrectly closes B4")
    checks.check(
        b2_remaining_work.get("execution_policy", {}).get("default_1e_4_required") is False,
        "B2 remaining-work requires default 1e-4",
    )
    checks.check(
        b2_remaining_work.get("execution_policy", {}).get("run_v047_invoked") is False,
        "B2 remaining-work invoked run_v047",
    )
    checks.check(
        ra2021_source_policy_audit.get("schema") == "ra2021-source-policy-row-audit-v1",
        "RA2021 source-policy audit schema changed",
    )
    checks.check(
        ra2021_source_policy_audit.get("status") == "public_rows_complete_source_policy_rows_not_closed",
        "RA2021 source-policy audit status changed",
    )
    checks.check(ra2021_source_policy_audit.get("active_b2_flagged_rows") == 0, "RA2021 active rows changed")
    checks.check(
        ra2021_source_policy_audit.get("public_order_groups_completed")
        == ra2021_source_policy_audit.get("public_order_groups_required")
        == 12,
        "RA2021 public order groups changed",
    )
    checks.check(
        ra2021_source_policy_audit.get("public_timing_rows_completed")
        == ra2021_source_policy_audit.get("public_timing_rows_required")
        == 12,
        "RA2021 public timing rows changed",
    )
    checks.check(
        ra2021_source_policy_audit.get("source_policy_reproduction_rows") == 0,
        "RA2021 source-policy reproduction rows changed",
    )
    checks.check(
        ra2021_source_policy_audit.get("decision", {}).get("can_close_ra2021_b2_requirement_now") is False,
        "RA2021 B2 requirement unexpectedly closed",
    )
    checks.check(
        ra2021_source_policy_audit.get("external_superiority_claim_allowed") is False,
        "RA2021 audit overclaims external superiority",
    )
    checks.check(
        tfe_source_policy_audit.get("schema") == "tfe-source-policy-row-audit-v1",
        "TFE source-policy audit schema changed",
    )
    checks.check(
        tfe_source_policy_audit.get("status") == "source_policy_spec_extracted_runner_rows_not_closed",
        "TFE source-policy audit status changed",
    )
    checks.check(tfe_source_policy_audit.get("active_b2_flagged_rows") == 0, "TFE active rows changed")
    checks.check(tfe_source_policy_audit.get("source_policy_spec_extracted") is True, "TFE spec extraction marker changed")
    checks.check(
        tfe_source_policy_audit.get("pendulum_dae_runner_implemented") is False,
        "TFE pendulum runner unexpectedly implemented",
    )
    checks.check(
        tfe_source_policy_audit.get("source_policy_closed_rows") == 0,
        "TFE source-policy rows unexpectedly closed",
    )
    checks.check(
        tfe_source_policy_audit.get("decision", {}).get("can_close_tfe_b2_requirement_now") is False,
        "TFE B2 requirement unexpectedly closed",
    )
    checks.check(
        tfe_source_policy_audit.get("external_superiority_claim_allowed") is False,
        "TFE audit overclaims external superiority",
    )
    checks.check(
        tfe_algorithm_literal_endpoint_probe.get("schema") == "tfe-algorithm-literal-endpoint-probe-v1",
        "TFE algorithm-literal endpoint probe schema changed",
    )
    checks.check(
        tfe_algorithm_literal_endpoint_probe.get("status")
        == "algorithm_literal_full_T10_probe_available_source_policy_open",
        "TFE algorithm-literal endpoint probe status changed",
    )
    checks.check(
        tfe_algorithm_literal_endpoint_probe.get("method_count") == 4
        and tfe_algorithm_literal_endpoint_probe.get("metric_row_count") == 12,
        "TFE algorithm-literal endpoint probe row counts changed",
    )
    checks.check(
        tfe_algorithm_literal_endpoint_probe.get("terminal_overrun_rows") == 12,
        "TFE algorithm-literal endpoint overrun count changed",
    )
    checks.check(
        tfe_algorithm_literal_endpoint_probe.get("source_policy_rows_completed") == 0,
        "TFE algorithm-literal endpoint probe overcloses source-policy rows",
    )
    checks.check(
        tfe_algorithm_literal_endpoint_probe.get("source_policy_exact_T_error_sampling_equivalent") is False,
        "TFE algorithm-literal endpoint probe overclaims exact-T sampling equivalence",
    )
    for path in [
        TFE_ALGORITHM_LITERAL_ENDPOINT_PROBE_MD,
        TFE_ALGORITHM_LITERAL_ENDPOINT_PROBE,
        TFE_ALGORITHM_LITERAL_ENDPOINT_PROBE_CSV,
        TFE_ALGORITHM_LITERAL_ENDPOINT_PROBE_VALIDATOR,
    ]:
        checks.check(path.exists() and path.stat().st_size > 0, f"TFE algorithm-literal endpoint evidence missing: {path.name}")
    checks.check(
        tfe_algorithm_literal_work_precision.get("schema") == "tfe-algorithm-literal-work-precision-audit-v1",
        "TFE algorithm-literal work/precision schema changed",
    )
    checks.check(
        tfe_algorithm_literal_work_precision.get("status")
        == "algorithm_literal_T10_newton_work_precision_available_source_policy_open",
        "TFE algorithm-literal work/precision status changed",
    )
    checks.check(
        tfe_algorithm_literal_work_precision.get("source_probe") == "TFE_ALGORITHM_LITERAL_ENDPOINT_PROBE.json",
        "TFE algorithm-literal work/precision source probe changed",
    )
    checks.check(
        tfe_algorithm_literal_work_precision.get("work_proxy") == "total_newton_iterations",
        "TFE algorithm-literal work/precision work proxy changed",
    )
    checks.check(
        tfe_algorithm_literal_work_precision.get("runtime_proxy_available") is False,
        "TFE algorithm-literal work/precision overclaims runtime proxy",
    )
    checks.check(
        tfe_algorithm_literal_work_precision.get("method_count") == 4
        and tfe_algorithm_literal_work_precision.get("raw_row_count") == 12
        and tfe_algorithm_literal_work_precision.get("summary_row_count") == 4,
        "TFE algorithm-literal work/precision row counts changed",
    )
    checks.check(
        tfe_algorithm_literal_work_precision.get("terminal_overrun_rows") == 12,
        "TFE algorithm-literal work/precision terminal overrun count changed",
    )
    checks.check(
        tfe_algorithm_literal_work_precision.get("source_policy_rows_completed") == 0,
        "TFE algorithm-literal work/precision overcloses source-policy rows",
    )
    checks.check(
        tfe_algorithm_literal_work_precision.get("source_policy_method_runner_equivalent") is False,
        "TFE algorithm-literal work/precision overclaims method equivalence",
    )
    checks.check(
        tfe_algorithm_literal_work_precision.get("source_policy_exact_T_error_sampling_equivalent") is False,
        "TFE algorithm-literal work/precision overclaims exact-T sampling equivalence",
    )
    checks.check(
        tfe_algorithm_literal_work_precision.get("external_superiority_claim_allowed") is False,
        "TFE algorithm-literal work/precision overclaims external superiority",
    )
    checks.check(
        tfe_algorithm_literal_work_precision.get("work_precision_figure_available") is True,
        "TFE algorithm-literal work/precision figure availability changed",
    )
    checks.check(
        "Methods/raw rows/summary rows: `4/12/4`" in tfe_algorithm_literal_work_precision_md,
        "TFE algorithm-literal work/precision markdown stale",
    )
    for path in [
        TFE_ALGORITHM_LITERAL_WORK_PRECISION,
        TFE_ALGORITHM_LITERAL_WORK_PRECISION_MD,
        TFE_ALGORITHM_LITERAL_WORK_PRECISION_CSV,
        TFE_ALGORITHM_LITERAL_WORK_PRECISION_FIGURE,
        TFE_ALGORITHM_LITERAL_WORK_PRECISION_VALIDATOR,
    ]:
        checks.check(path.exists() and path.stat().st_size > 0, f"TFE algorithm-literal work/precision evidence missing: {path.name}")
    checks.check(
        tfe_same_test_work_precision.get("schema") == "tfe-source-pendulum-same-test-work-precision-v1",
        "TFE same-test work/precision schema changed",
    )
    checks.check(
        tfe_same_test_work_precision.get("status")
        == "same_test_candidate_work_precision_available_not_source_policy",
        "TFE same-test work/precision status changed",
    )
    checks.check(
        tfe_same_test_work_precision.get("same_test_work_precision_available") is True,
        "TFE same-test work/precision availability marker missing",
    )
    checks.check(
        tfe_same_test_work_precision.get("method_count") == 6
        and tfe_same_test_work_precision.get("row_count") == 18
        and tfe_same_test_work_precision.get("ok_row_count") == 18
        and tfe_same_test_work_precision.get("summary_row_count") == 6,
        "TFE same-test work/precision row counts changed",
    )
    checks.check(
        tfe_same_test_work_precision.get("figure_available") is True,
        "TFE same-test work/precision figure availability changed",
    )
    checks.check(
        tfe_same_test_work_precision.get("source_policy_rows_completed") == 0,
        "TFE same-test work/precision overcloses source-policy rows",
    )
    checks.check(
        tfe_same_test_work_precision.get("source_policy_method_runner_equivalent") is False,
        "TFE same-test work/precision overclaims method equivalence",
    )
    checks.check(
        tfe_same_test_work_precision.get("fullva_dae_source_policy_equivalent") is False,
        "TFE same-test work/precision overclaims FullVA DAE source-policy equivalence",
    )
    checks.check(
        tfe_same_test_work_precision.get("external_superiority_claim_allowed") is False,
        "TFE same-test work/precision overclaims external superiority",
    )
    checks.check(
        tfe_same_test_work_precision.get("default_1e-4_required") is False
        and tfe_same_test_work_precision.get("heavy_numerical_run_invoked") is False,
        "TFE same-test work/precision changed execution boundary",
    )
    checks.check("Rows: `18/18` ok" in tfe_same_test_work_precision_md, "TFE same-test work/precision report stale")
    for path in [
        TFE_SAME_TEST_WORK_PRECISION,
        TFE_SAME_TEST_WORK_PRECISION_MD,
        TFE_SAME_TEST_WORK_PRECISION_RAW_CSV,
        TFE_SAME_TEST_WORK_PRECISION_SUMMARY_CSV,
        TFE_SAME_TEST_WORK_PRECISION_FIGURE,
        TFE_SAME_TEST_WORK_PRECISION_VALIDATOR,
    ]:
        checks.check(path.exists() and path.stat().st_size > 0, f"TFE same-test work/precision evidence missing: {path.name}")
    checks.check(
        demoted_vp.get("claim_allowed_now") == "code-path-unresolved_related_work_only",
        "VP demotion claim boundary changed",
    )
    checks.check(demotion_execution.get("default_1e_4_required") is False, "demotion ledger requires default 1e-4")
    checks.check(demotion_execution.get("heavy_numerical_run_invoked") is False, "demotion ledger invoked heavy run")
    checks.check(demotion_execution.get("run_v047_invoked") is False, "demotion ledger invoked run_v047")
    checks.check(
        prose_residue_audit_json.get("status") == "main_body_machine_tokens_removed_reproducibility_appendix_compacted_b6_closed_under_narrowed_policy",
        "prose-residue audit status changed",
    )
    checks.check(prose_residue_audit_json.get("blocker") == "B6", "prose-residue audit blocker changed")
    checks.check(prose_residue_audit_json.get("submission_ready") is False, "prose-residue audit incorrectly claims submission ready")
    checks.check(
        prose_residue_audit_json.get("main_body_machine_token_count") == 0,
        "prose-residue audit main-body count changed",
    )
    checks.check(
        prose_residue_audit_json.get("flat_main_body_machine_token_count") == 0,
        "prose-residue audit flat main-body count changed",
    )
    checks.check(
        prose_residue_audit_json.get("appendix_evidence", {}).get("artifact_macro_count") == 0,
        "prose-residue audit appendix artifact count changed",
    )
    checks.check(
        prose_residue_audit_json.get("appendix_evidence", {}).get("flat_artifact_macro_count") == 0,
        "prose-residue audit flat appendix artifact count changed",
    )
    checks.check(
        prose_residue_audit_json.get("appendix_evidence", {}).get("reproducibility_appendix_compacted") is True,
        "prose-residue audit appendix compaction marker missing",
    )
    checks.check(
        prose_residue_audit_json.get("execution_policy", {}).get("default_1e-4_required") is False,
        "prose-residue audit incorrectly requires default 1e-4",
    )
    checks.check(
        prose_residue_audit_json.get("execution_policy", {}).get("run_v047_invoked") is False,
        "prose-residue audit invoked run_v047",
    )
    checks.check(LIMITATION_FIGURE.exists() and LIMITATION_FIGURE.stat().st_size > 100_000, "B7 limitation figure missing or too small")
    checks.check(
        FLAT_LIMITATION_FIGURE.exists() and FLAT_LIMITATION_FIGURE.stat().st_size > 100_000,
        "B7 flat limitation figure missing or too small",
    )
    checks.check(
        BASELINE_WORK_FIGURE.exists() and BASELINE_WORK_FIGURE.stat().st_size > 100_000,
        "B7 coarse baseline/work-precision figure missing or too small",
    )
    checks.check(
        FLAT_BASELINE_WORK_FIGURE.exists() and FLAT_BASELINE_WORK_FIGURE.stat().st_size > 100_000,
        "B7 flat coarse baseline/work-precision figure missing or too small",
    )
    checks.check(
        TRUE_DYNAMIC_ORDER_FIGURE.exists() and TRUE_DYNAMIC_ORDER_FIGURE.stat().st_size > 100_000,
        "B7 closed-loop coarse-dynamics diagnostic figure missing or too small",
    )
    checks.check(
        FLAT_TRUE_DYNAMIC_ORDER_FIGURE.exists() and FLAT_TRUE_DYNAMIC_ORDER_FIGURE.stat().st_size > 100_000,
        "B7 flat closed-loop coarse-dynamics diagnostic figure missing or too small",
    )
    checks.check(
        METHOD_ARCH_FIGURE.exists() and METHOD_ARCH_FIGURE.stat().st_size > 100_000,
        "B7 method-stage architecture figure missing or too small",
    )
    checks.check(
        FLAT_METHOD_ARCH_FIGURE.exists() and FLAT_METHOD_ARCH_FIGURE.stat().st_size > 100_000,
        "B7 flat method-stage architecture figure missing or too small",
    )
    checks.check(
        ALL_METHOD_MATRIX_FIGURE.exists() and ALL_METHOD_MATRIX_FIGURE.stat().st_size > 100_000,
        "B7 all-method result matrix figure missing or too small",
    )
    checks.check(
        FLAT_ALL_METHOD_MATRIX_FIGURE.exists() and FLAT_ALL_METHOD_MATRIX_FIGURE.stat().st_size > 100_000,
        "B7 flat all-method result matrix figure missing or too small",
    )
    checks.check(
        WORK_PRECISION_COMPENDIUM_FIGURE.exists() and WORK_PRECISION_COMPENDIUM_FIGURE.stat().st_size > 100_000,
        "B7 work/precision compendium figure missing or too small",
    )
    checks.check(
        FLAT_WORK_PRECISION_COMPENDIUM_FIGURE.exists()
        and FLAT_WORK_PRECISION_COMPENDIUM_FIGURE.stat().st_size > 100_000,
        "B7 flat work/precision compendium figure missing or too small",
    )
    checks.check(
        figure_set_audit_json.get("schema") == "cmame-figure-set-audit-v1",
        "figure-set audit schema changed",
    )
    checks.check(
        figure_set_audit_json.get("status") == "b7_figure_set_closed_narrowed_common_reference_diagnostic_scope",
        "figure-set audit status changed",
    )
    checks.check(
        figure_set_audit_json.get("figure_count") == figure_set_audit_json.get("expected_figure_count") == 13,
        "figure-set audit count changed",
    )
    checks.check(figure_set_audit_json.get("all_figures_available") is True, "figure-set audit lost available marker")
    checks.check(
        figure_set_audit_json.get("all_figures_integrated_main_flat") is True,
        "figure-set audit lost main/flat integration marker",
    )
    checks.check(figure_set_audit_json.get("all_pdf_captions_present") is True, "figure-set audit lost PDF caption marker")
    checks.check(figure_set_audit_json.get("all_legible_dimensions") is True, "figure-set audit lost dimension marker")
    checks.check(
        figure_set_audit_json.get("figure12_all_method_matrix_integrated") is True,
        "figure-set audit lost Figure 12 integration marker",
    )
    checks.check(
        figure_set_audit_json.get("figure13_work_precision_compendium_integrated") is True,
        "figure-set audit lost Figure 13 integration marker",
    )
    checks.check(figure_set_audit_json.get("b7_closed") is True, "figure-set audit did not close B7")
    checks.check(
        figure_set_audit_json.get("claim_boundary", {}).get("external_superiority_claim_allowed") is False,
        "figure-set audit overclaims external superiority",
    )
    checks.check(
        figure_set_audit_json.get("claim_boundary", {}).get("default_1e-4_required") is False,
        "figure-set audit incorrectly requires default 1e-4",
    )
    checks.check(
        figure_set_audit_json.get("claim_boundary", {}).get("heavy_numerical_run_invoked") is False,
        "figure-set audit invoked heavy numerical run",
    )
    require_tokens(
        checks,
        figure_set_audit,
        [
            "Figures audited: `13/13`",
            "Figure 12 all-method matrix integrated: `True`",
            "Figure 13 work/precision compendium integrated: `True`",
            "B7 closed: `True`",
            "Source-policy work/precision claim excluded: `True`",
            "External superiority claim allowed: `False`",
        ],
        "CMAME_FIGURE_SET_AUDIT.md",
    )

    execution = gate.get("execution_policy", {})
    checks.check(execution.get("default_step_policy") == "coarse_first_no_default_1e-4", "default step policy changed")
    checks.check(execution.get("strict_public_policy_1e-4") == "opt_in_only", "strict 1e-4 policy changed")
    checks.check(execution.get("default_1e-4_required") is False, "gate incorrectly requires default 1e-4")
    checks.check(execution.get("heavy_numerical_run_invoked_by_gate") is False, "gate must remain read-only")

    order_boundary = gate.get("order_boundary", {})
    checks.check(order_boundary.get("accepted_method") == "Gauss6/FullVA", "accepted method changed")
    checks.check(order_boundary.get("accepted_method_order") == 6, "accepted order changed")
    checks.check(order_boundary.get("comparator_expected_order") == 5, "comparator order changed")
    checks.check(
        order_boundary.get("local_dynamic_order_status")
        == four_example_dashboard.get("local_dynamic_order_status")
        == "accepted_method_dynamic_order_2_of_4_source_policy_external_open",
        "local dynamic-order status changed",
    )
    checks.check(
        order_boundary.get("local_evidence_coverage_status")
        == four_example_dashboard.get("local_evidence_coverage_status")
        == "all_four_examples_local_evidence_present_source_policy_dynamic_order_open",
        "local evidence-coverage status changed",
    )
    checks.check(
        order_boundary.get("local_evidence_coverage_examples")
        == four_example_dashboard.get("local_evidence_coverage_example_names")
        == EXPECTED_EXAMPLES,
        "local evidence-coverage examples changed",
    )
    checks.check(
        order_boundary.get("local_evidence_coverage_count")
        == four_example_dashboard.get("local_evidence_coverage_examples")
        == 4,
        "local evidence-coverage count changed",
    )
    checks.check(
        order_boundary.get("local_dynamic_order_closed_examples")
        == four_example_dashboard.get("local_dynamic_order_closed_example_names")
        == ["single_pendulum", "double_pendulum"],
        "local dynamic-order examples changed",
    )
    checks.check(
        order_boundary.get("local_dynamic_order_closed_count")
        == four_example_dashboard.get("local_dynamic_order_closed_examples")
        == 2,
        "local dynamic-order count changed",
    )
    checks.check(
        order_boundary.get("method_side_order_gate_examples")
        == four_example_dashboard.get("method_side_order_gate_examples")
        == EXPECTED_DYNAMIC_ORDER_EXAMPLES,
        "method-side order-gate examples changed",
    )
    checks.check(
        order_boundary.get("accepted_method_dynamic_order_examples")
        == four_example_dashboard.get("accepted_method_dynamic_order_examples")
        == EXPECTED_DYNAMIC_ORDER_EXAMPLES,
        "accepted method dynamic-order examples changed",
    )
    checks.check(
        order_boundary.get("accepted_method_dynamic_order_example_count")
        == four_example_dashboard.get("accepted_method_dynamic_order_example_count")
        == 2,
        "accepted method dynamic-order count changed",
    )
    checks.check(
        order_boundary.get("mechanism_coverage_examples")
        == four_example_dashboard.get("mechanism_coverage_examples")
        == EXPECTED_COVERAGE_ONLY_EXAMPLES,
        "mechanism-coverage examples changed",
    )
    checks.check(
        order_boundary.get("mechanism_coverage_example_count")
        == four_example_dashboard.get("mechanism_coverage_example_count")
        == 2,
        "mechanism-coverage count changed",
    )
    checks.check(
        order_boundary.get("closed_loop_true_dynamic_order_examples")
        == four_example_dashboard.get("closed_loop_true_dynamic_order_closed_example_names")
        == EXPECTED_COVERAGE_ONLY_EXAMPLES,
        "closed-loop coarse-dynamics examples changed",
    )
    checks.check(
        order_boundary.get("closed_loop_true_dynamic_order_count")
        == four_example_dashboard.get("closed_loop_true_dynamic_order_closed_examples")
        == 2,
        "closed-loop coarse-dynamics count changed",
    )
    checks.check(
        order_boundary.get("accepted_source_policy_dynamic_order_examples_count")
        == four_example_dashboard.get("accepted_source_policy_dynamic_order_examples")
        == 0,
        "source-policy dynamic-order count changed",
    )
    checks.check(
        order_boundary.get("accepted_dynamic_order_examples") == EXPECTED_DYNAMIC_ORDER_EXAMPLES,
        "accepted dynamic-order examples changed",
    )
    checks.check(
        order_boundary.get("coverage_only_dynamic_order_examples") == EXPECTED_COVERAGE_ONLY_EXAMPLES,
        "coverage-only dynamic-order examples changed",
    )
    checks.check(order_gate.get("accepted_dynamic_order_examples") == EXPECTED_DYNAMIC_ORDER_EXAMPLES, "order gate dynamic examples changed")
    checks.check(order_gate.get("coverage_only_examples") == EXPECTED_COVERAGE_ONLY_EXAMPLES, "order gate coverage examples changed")
    checks.check(order_gate.get("execution_policy", {}).get("default_step_policy") == "coarse_first_no_default_1e-4", "order gate default policy changed")
    checks.check(dynamic_oracle.get("schema") == "dynamic-row-oracle-gate-v2", "dynamic row oracle schema changed")
    checks.check(
        dynamic_oracle.get("status") == "runtime_row_and_block_oracle_passable_symbolic_oracle_open",
        "dynamic row oracle status changed",
    )
    checks.check(
        dynamic_oracle.get("runtime_block_functional_crosscheck", {}).get("checked") is True,
        "dynamic row oracle lost block-functional cross-check",
    )
    partial_formula_oracle = dynamic_oracle.get("partial_independent_formula_row_oracle", {})
    checks.check(partial_formula_oracle.get("checked") is True, "dynamic row oracle lost partial formula-row oracle")
    checks.check(partial_formula_oracle.get("row_count") == 96, "partial formula-row oracle count changed")
    checks.check(
        partial_formula_oracle.get("excluded_row_family") == "newton_euler_weak_balance",
        "partial formula-row oracle exclusion changed",
    )
    full_formula_oracle = dynamic_oracle.get("full_independent_formula_row_oracle", {})
    checks.check(full_formula_oracle.get("checked") is True, "dynamic row oracle lost full formula-row oracle")
    checks.check(full_formula_oracle.get("row_count") == 132, "full formula-row oracle count changed")
    checks.check(
        full_formula_oracle.get("added_row_family") == "newton_euler_weak_balance",
        "full formula-row oracle added-family marker changed",
    )
    checks.check(
        full_formula_oracle.get("runtime_formula_row_oracle_complete") is True,
        "full runtime formula-row oracle marker changed",
    )
    formula_jacobian_oracle = dynamic_oracle.get("formula_row_ad_jacobian_oracle", {})
    checks.check(formula_jacobian_oracle.get("checked") is True, "dynamic row oracle lost formula-row AD Jacobian oracle")
    checks.check(formula_jacobian_oracle.get("multi_probe_checked") is True, "dynamic row oracle lost formula-row AD Jacobian multi-probe marker")
    checks.check(formula_jacobian_oracle.get("probe_count") == 3, "formula-row AD Jacobian probe count changed")
    checks.check(formula_jacobian_oracle.get("row_count") == 132, "formula-row AD Jacobian row count changed")
    checks.check(formula_jacobian_oracle.get("column_count") == 132, "formula-row AD Jacobian column count changed")
    checks.check(
        formula_jacobian_oracle.get("symbolic_oracle_complete") is False,
        "formula-row AD Jacobian oracle incorrectly closes symbolic oracle",
    )
    checks.check(
        dynamic_oracle.get("acceptance_boundary", {}).get("independent_symbolic_row_oracle_complete") is False,
        "dynamic row oracle incorrectly closes symbolic oracle",
    )
    checks.check(
        dynamic_oracle.get("acceptance_boundary", {}).get("partial_independent_formula_rows_checked") is True,
        "dynamic row oracle lost partial formula-row acceptance marker",
    )
    checks.check(
        dynamic_oracle.get("acceptance_boundary", {}).get("full_independent_formula_rows_checked") is True,
        "dynamic row oracle lost full formula-row acceptance marker",
    )
    checks.check(
        dynamic_oracle.get("acceptance_boundary", {}).get("formula_row_ad_jacobian_checked") is True,
        "dynamic row oracle lost formula-row AD Jacobian marker",
    )
    checks.check(
        dynamic_oracle.get("acceptance_boundary", {}).get("formula_row_ad_jacobian_multi_probe_checked") is True,
        "dynamic row oracle lost formula-row AD Jacobian multi-probe marker",
    )
    checks.check(
        dynamic_oracle.get("acceptance_boundary", {}).get("partial_kinematic_stage_defect_certificate_checked") is True,
        "dynamic row oracle lost partial kinematic defect certificate marker",
    )
    checks.check(proof_contract.get("schema") == "cmame-proof-contract-gate-v1", "proof contract schema changed")
    checks.check(
        proof_contract.get("status") == "open_explicitly_conditional_not_submission_ready",
        "proof contract status changed",
    )
    checks.check(proof_contract.get("submission_ready") is False, "proof contract incorrectly claims submission ready")
    checks.check(
        proof_contract.get("theorem_contract", {}).get("dynamic_symbolic_oracle_complete") is False,
        "proof contract incorrectly closes dynamic symbolic oracle",
    )
    checks.check(
        proof_contract.get("theorem_contract", {}).get("stage_residual_O_h7_implementation_defect_proved") is True,
        "proof contract lost direct-substitution O(h^7) implementation-defect proof",
    )
    checks.check(
        proof_contract.get("theorem_contract", {}).get("newton_euler_stage_defect_certificate_open") is False,
        "proof contract still marks Newton-Euler direct-substitution certificate open",
    )
    checks.check(
        proof_contract.get("theorem_contract", {}).get("newton_euler_stage_defect_certificate_closed_by_direct_substitution")
        is True,
        "proof contract lost Newton-Euler direct-substitution closure marker",
    )
    checks.check(
        proof_contract.get("theorem_contract", {}).get("newton_euler_stage_defect_certificate_satisfaction_mode")
        == "D5 same-branch residual-value certificate: 96-row O(h^7) non-dynamic certificate plus 36 dynamic zero rows at Z_G",
        "proof contract Newton-Euler satisfaction mode changed",
    )
    checks.check(
        proof_contract.get("residual_to_error_contract", {}).get("accepted_residual_to_error_theorem") is False,
        "proof contract incorrectly accepts residual-to-error theorem",
    )
    checks.check(
        proof_contract.get("theorem_contract", {}).get("solver_scale_audit_checked") is True,
        "proof contract lost solver-scale audit marker",
    )
    checks.check(
        proof_contract.get("theorem_contract", {}).get("partial_kinematic_stage_defect_certificate_checked") is True,
        "proof contract lost partial kinematic defect certificate marker",
    )
    checks.check(
        proof_contract.get("theorem_contract", {}).get("partial_kinematic_stage_defect_rows_checked") == 96,
        "proof contract partial kinematic defect row count changed",
    )
    checks.check(
        proof_contract.get("theorem_contract", {}).get("newton_euler_defect_obligation_gate_checked") is True,
        "proof contract lost Newton-Euler obligation gate marker",
    )
    checks.check(
        proof_contract.get("theorem_contract", {}).get("newton_euler_defect_obligation_rows") == 36,
        "proof contract Newton-Euler obligation row count changed",
    )
    checks.check(
        proof_contract.get("theorem_contract", {}).get("newton_euler_defect_open_obligation_count") == 1,
        "proof contract Newton-Euler open obligation count changed",
    )
    checks.check(
        proof_contract.get("theorem_contract", {}).get("newton_euler_defect_open_obligation_scope")
        == "symbolic_primitive_certificate_route_not_active_direct_pc2",
        "proof contract Newton-Euler open obligation scope changed",
    )
    checks.check(
        proof_contract.get("theorem_contract", {}).get("newton_euler_symbolic_primitive_open_obligation_count")
        == 1,
        "proof contract symbolic/primitive Newton-Euler open obligation count changed",
    )
    checks.check(
        proof_contract.get("theorem_contract", {}).get("newton_euler_symbolic_primitive_open_obligation_scope")
        == "symbolic_primitive_certificate_route_not_active_direct_pc2",
        "proof contract symbolic/primitive Newton-Euler open obligation scope changed",
    )
    checks.check(
        proof_contract.get("theorem_contract", {}).get("active_direct_newton_euler_open_obligation_count") == 0,
        "proof contract active direct Newton-Euler open obligation count changed",
    )
    checks.check(
        proof_contract.get("theorem_contract", {}).get("active_direct_newton_euler_stage_defect_closed") is True,
        "proof contract active direct Newton-Euler stage defect closure marker changed",
    )
    checks.check(
        proof_contract.get("theorem_contract", {}).get("active_direct_newton_euler_zero_residual_rows") == 36,
        "proof contract active direct Newton-Euler zero-row count changed",
    )
    checks.check(
        proof_contract.get("theorem_contract", {}).get("newton_euler_defect_closed_obligation_count") == 5,
        "proof contract Newton-Euler closed obligation count changed",
    )
    checks.check(
        proof_contract.get("theorem_contract", {}).get("newton_euler_symbolic_defect_certificate_complete") is False,
        "proof contract overclaims Newton-Euler symbolic defect certificate",
    )
    checks.check(
        proof_contract.get("theorem_contract", {}).get("newton_euler_symbolic_target_audit_checked") is True,
        "proof contract lost Newton-Euler symbolic target audit marker",
    )
    checks.check(
        proof_contract.get("theorem_contract", {}).get("newton_euler_symbolic_target_rows") == 36,
        "proof contract Newton-Euler symbolic target row count changed",
    )
    checks.check(
        proof_contract.get("theorem_contract", {}).get("newton_euler_symbolic_target_inventory_complete") is True,
        "proof contract lost Newton-Euler symbolic target inventory marker",
    )
    checks.check(
        proof_contract.get("theorem_contract", {}).get("summary_level_solver_residuals_recorded") is True,
        "proof contract lost summary residual marker",
    )
    checks.check(
        proof_contract.get("theorem_contract", {}).get("scaled_tolerance_sweep_recorded") is False,
        "proof contract overclaims scaled tolerance sweep",
    )
    checks.check(
        proof_closure_manifest.get("schema") == "proof-closure-manifest-v1",
        "proof-closure manifest schema changed",
    )
    checks.check(
        proof_closure_manifest.get("status") == "pc2_closed_by_direct_residual_bridge_global_boundary_retained",
        "proof-closure manifest status changed",
    )
    checks.check(
        proof_closure_manifest.get("evidence_summary", {}).get("certified_non_dynamic_rows") == 96,
        "proof-closure certified row count changed",
    )
    checks.check(
        proof_closure_manifest.get("evidence_summary", {}).get("open_dynamic_rows") == 36,
        "proof-closure open dynamic row count changed",
    )
    checks.check(
        proof_closure_manifest.get("evidence_summary", {}).get("newton_euler_open_obligations") == 1,
        "proof-closure Newton-Euler obligation count changed",
    )
    checks.check(
        proof_closure_manifest.get("evidence_summary", {}).get("newton_euler_closed_obligations") == 5,
        "proof-closure Newton-Euler closed obligation count changed",
    )
    checks.check(
        proof_closure_manifest.get("evidence_summary", {}).get("newton_euler_symbolic_target_rows") == 36,
        "proof-closure Newton-Euler symbolic target row count changed",
    )
    checks.check(
        proof_closure_manifest.get("evidence_summary", {}).get("newton_euler_symbolic_target_translational_rows") == 18,
        "proof-closure Newton-Euler translational target row count changed",
    )
    checks.check(
        proof_closure_manifest.get("evidence_summary", {}).get("newton_euler_symbolic_target_rotational_rows") == 18,
        "proof-closure Newton-Euler rotational target row count changed",
    )
    checks.check(
        proof_closure_manifest.get("oracle_state", {}).get("newton_euler_symbolic_target_inventory_complete") is True,
        "proof-closure lost Newton-Euler symbolic target inventory marker",
    )
    checks.check(
        proof_closure_manifest.get("evidence_summary", {}).get("residual_to_error_blocking_obligations") == 7,
        "proof-closure residual-to-error blocker count changed",
    )
    checks.check(
        proof_closure_manifest.get("closure_state", {}).get("proof_gap_closed") is True,
        "proof-closure direct proof gap closure missing",
    )
    checks.check(
        proof_closure_manifest.get("closure_state", {}).get("stage_residual_O_h7_implementation_defect_proved")
        is True,
        "proof-closure direct O(h^7) implementation defect proof missing",
    )
    checks.check(
        proof_closure_manifest.get("closure_state", {}).get("pc2_closed_by_direct_substitution") is True,
        "proof-closure direct PC2 route missing",
    )
    checks.check(
        proof_closure_manifest.get("closure_state", {}).get("primitive_lift_route_closed") is False,
        "proof-closure unexpectedly closes primitive lift route",
    )
    checks.check(
        proof_closure_manifest.get("closure_state", {}).get("eta_h_O_h7_solver_policy_evidence") is False,
        "proof-closure incorrectly closes eta_h proof",
    )
    proof_close_requirements = {
        row.get("id"): row for row in proof_closure_manifest.get("close_requirements", [])
    }
    checks.check(
        proof_close_requirements.get("PC1", {}).get("satisfied") is True,
        "proof-closure PC1 balance identity item not satisfied",
    )
    checks.check(
        proof_close_requirements.get("PC2", {}).get("satisfied") is True,
        "proof-closure PC2 direct-substitution item not satisfied",
    )
    checks.check(
        proof_close_requirements.get("PC2", {}).get("satisfaction_mode")
        == "D5 same-branch residual-value certificate: 96-row O(h^7) non-dynamic certificate plus 36 dynamic zero rows at Z_G",
        "proof-closure PC2 satisfaction mode changed",
    )
    checks.check(
        proof_close_requirements.get("PC3", {}).get("satisfied") is True,
        "proof-closure PC3 condition-retention item not satisfied",
    )
    checks.check(
        proof_close_requirements.get("PC3", {}).get("satisfaction_mode")
        == "explicit_theorem_condition_retained_not_empirical_solver_evidence",
        "proof-closure PC3 satisfaction mode changed",
    )
    checks.check(
        proof_close_requirements.get("PC4", {}).get("satisfied") is True,
        "proof-closure PC4 nonpromotion boundary not retained",
    )
    checks.check(
        proof_close_requirements.get("PC4", {}).get("satisfaction_mode")
        == "nonpromotion_boundary_retained_residual_to_error_theorem_open",
        "proof-closure PC4 nonpromotion mode changed",
    )
    checks.check(
        proof_close_requirements.get("PC4", {}).get("residual_to_error_closed") is False,
        "proof-closure PC4 residual-to-error closure overclaimed",
    )
    checks.check(
        proof_close_requirements.get("PC4", {}).get("residual_to_error_route_promoted") is False,
        "proof-closure PC4 residual-to-error route promotion overclaimed",
    )
    checks.check(
        sum(1 for row in proof_close_requirements.values() if row.get("satisfied")) == 4,
        "proof-closure satisfied close requirement count changed",
    )
    checks.check(
        sum(1 for row in proof_close_requirements.values() if not row.get("satisfied")) == 0,
        "proof-closure unsatisfied close requirement count changed",
    )
    checks.check(
        proof_solver_scale_audit_json.get("status") == "summary_level_solver_residuals_recorded_not_scaled_eta_h_proof",
        "proof solver-scale audit status changed",
    )
    checks.check(
        proof_solver_scale_audit_json.get("proof_boundary", {}).get("summary_level_solver_residuals_recorded") is True,
        "proof solver-scale audit lost residual-record marker",
    )
    checks.check(
        proof_solver_scale_audit_json.get("proof_boundary", {}).get("finite_scaled_tolerance_probe_recorded") is True,
        "proof solver-scale audit lost finite scaled-tolerance probe marker",
    )
    checks.check(
        proof_solver_scale_audit_json.get("proof_boundary", {}).get("scaled_tolerance_sweep_recorded") is False,
        "proof solver-scale audit overclaims scaled tolerance sweep",
    )
    checks.check(
        proof_solver_scale_audit_json.get("proof_boundary", {}).get("eta_h_O_h7_solver_policy_evidence") is False,
        "proof solver-scale audit overclaims eta_h proof",
    )
    checks.check(external_baseline.get("schema") == "cmame-external-baseline-gate-v1", "external baseline schema changed")
    checks.check(external_baseline.get("status") == "open_not_submission_ready", "external baseline status changed")
    checks.check(external_baseline.get("submission_ready") is False, "external baseline incorrectly claims submission ready")
    checks.check(
        external_baseline.get("execution_policy", {}).get("default_1e-4_required") is False,
        "external baseline incorrectly requires default 1e-4",
    )
    checks.check(
        external_baseline.get("same_test_boundary", {}).get("same_test_campaign_status") == "not_run",
        "external baseline same-test status changed",
    )
    checks.check(
        external_baseline.get("same_test_boundary", {}).get("external_superiority_claim") is False,
        "external baseline incorrectly claims superiority",
    )
    checks.check(
        external_baseline.get("same_test_boundary", {}).get("comparison_matrix_closed") is True,
        "external baseline lost comparison matrix closure",
    )
    checks.check(
        external_baseline.get("same_test_boundary", {}).get("common_reference_examples") == EXPECTED_EXAMPLES,
        "external baseline all-example comparison coverage changed",
    )
    checks.check(
        external_baseline.get("same_test_boundary", {}).get("direct_nonlocal_velocity_order_wins") == 40,
        "external baseline order win count changed",
    )
    checks.check(
        external_baseline.get("same_test_boundary", {}).get("direct_nonlocal_finest_velocity_error_wins") == 40,
        "external baseline error win count changed",
    )
    checks.check(
        external_baseline.get("same_test_boundary", {}).get("source_policy_superiority_claim_allowed") is False,
        "external baseline source-policy boundary changed",
    )
    checks.check(
        external_baseline.get("same_test_boundary", {}).get("all_examples_source_policy_audit_status")
        == all_source_policy.get("status"),
        "external baseline all-example source-policy status changed",
    )
    checks.check(
        external_baseline.get("same_test_boundary", {}).get("all_examples_source_policy_flagged_rows")
        == all_source_policy.get("coverage", {}).get("flagged_row_count")
        == 15,
        "external baseline all-example source-policy flagged rows changed",
    )
    checks.check(
        external_baseline.get("same_test_boundary", {}).get("all_examples_source_policy_flagged_raw_rows")
        == all_source_policy.get("coverage", {}).get("flagged_raw_row_count")
        == 45,
        "external baseline all-example source-policy raw rows changed",
    )
    checks.check(
        external_baseline.get("source_policy_audit", {}).get("artifact") == "ALL_EXAMPLES_SOURCE_POLICY_AUDIT.md",
        "external baseline missing all-example source-policy audit artifact",
    )
    checks.check(
        external_baseline.get("source_policy_audit", {}).get("validator") == "validate_all_examples_source_policy_audit.py",
        "external baseline missing all-example source-policy validator",
    )
    checks.check(
        external_baseline.get("source_policy_audit", {}).get("b2_can_close_now") is False,
        "external baseline all-example source-policy incorrectly closes B2",
    )
    checks.check(
        external_baseline.get("cross_case_inventory_boundary", {}).get("status")
        == "spec_extracted_partial_evidence_not_full_campaign",
        "external baseline cross-case inventory boundary changed",
    )
    checks.check(
        external_baseline.get("cross_case_inventory_boundary", {}).get("default_1e-4_required") is False,
        "external baseline cross-case boundary incorrectly requires default 1e-4",
    )
    checks.check(
        external_baseline.get("same_test_boundary", {}).get("coarse_first_order_time_examples")
        == EXPECTED_DYNAMIC_ORDER_EXAMPLES,
        "external baseline coarse-first example split changed",
    )
    checks.check(
        external_baseline.get("same_test_boundary", {}).get("surrogate_only_examples")
        == [],
        "external baseline surrogate-only example split changed",
    )
    checks.check(
        external_baseline.get("same_test_boundary", {}).get("local_true_dynamic_order_examples")
        == EXPECTED_COVERAGE_ONLY_EXAMPLES,
        "external baseline closed-loop coarse-dynamics example split changed",
    )
    checks.check(
        external_baseline.get("same_test_boundary", {}).get("public_work_precision_available_examples")
        == EXPECTED_COVERAGE_ONLY_EXAMPLES,
        "external baseline public work/precision availability split changed",
    )
    checks.check(
        external_baseline.get("same_test_boundary", {}).get("public_work_precision_missing_examples")
        == [],
        "external baseline public work/precision missing split changed",
    )
    checks.check(
        external_baseline.get("same_test_boundary", {}).get("strict_common_reference_available_examples")
        == EXPECTED_COVERAGE_ONLY_EXAMPLES,
        "external baseline strict common-reference availability split changed",
    )
    checks.check(
        external_baseline.get("same_test_boundary", {}).get("strict_common_reference_gap_examples")
        == [],
        "external baseline strict common-reference gap split changed",
    )
    checks.check(
        external_baseline.get("acceptance_sheet") == "EXTERNAL_SAME_TEST_ACCEPTANCE_SHEET.md",
        "external baseline lost acceptance sheet path",
    )
    checks.check(
        external_baseline.get("acceptance_sheet_json") == "EXTERNAL_SAME_TEST_ACCEPTANCE_SHEET.json",
        "external baseline lost acceptance sheet JSON path",
    )
    checks.check(
        external_baseline.get("acceptance_counts", {}).get("parallel_shard_count_without_default_1e-4") == 20,
        "external baseline acceptance shard count changed",
    )
    checks.check(
        external_baseline.get("acceptance_counts", {}).get("accepted_external_dynamic_order_examples_count") == 0,
        "external baseline accepted external order count changed",
    )
    checks.check(
        external_acceptance_sheet.get("schema") == "external-same-test-acceptance-sheet-v1",
        "external acceptance sheet schema changed",
    )
    checks.check(
        external_acceptance_sheet.get("status") == "acceptance_requirements_defined_campaign_not_run",
        "external acceptance sheet status changed",
    )
    checks.check(
        external_acceptance_sheet.get("same_test_campaign_status") == "not_run",
        "external acceptance sheet overclaims same-test status",
    )
    checks.check(
        external_acceptance_sheet.get("external_superiority_claim") is False,
        "external acceptance sheet overclaims superiority",
    )
    checks.check(
        external_acceptance_sheet.get("execution_policy", {}).get("default_1e-4_required") is False,
        "external acceptance sheet incorrectly requires default 1e-4",
    )
    checks.check(
        external_acceptance_sheet.get("execution_policy", {}).get("heavy_numerical_run_invoked") is False,
        "external acceptance sheet invoked heavy numerical run",
    )
    checks.check(
        external_acceptance_sheet.get("acceptance_counts", {}).get("parallel_shard_count_without_default_1e-4") == 20,
        "external acceptance sheet shard count changed",
    )
    checks.check(
        external_acceptance_sheet.get("acceptance_counts", {}).get("accepted_external_dynamic_order_examples_count") == 0,
        "external acceptance sheet accepted external order count changed",
    )

    checks.check(
        comparison_reconciliation.get("schema") == "comparison-objective-closure-reconciliation-v1",
        "comparison reconciliation schema changed",
    )
    checks.check(
        comparison_reconciliation.get("status") == "common_reference_objective_closed_source_policy_reproduction_open",
        "comparison reconciliation status changed",
    )
    checks.check(
        comparison_reconciliation.get("examples") == EXPECTED_EXAMPLES,
        "comparison reconciliation example coverage changed",
    )
    checks.check(
        comparison_reconciliation.get("comparison_matrix_closed") is True,
        "comparison reconciliation lost closed common-reference matrix",
    )
    checks.check(
        comparison_reconciliation.get("common_reference_claim_allowed") is True,
        "comparison reconciliation common-reference claim boundary changed",
    )
    checks.check(
        comparison_reconciliation.get("paper_direct_error_superiority_claim_allowed") is False,
        "comparison reconciliation overclaims paper-level direct error superiority",
    )
    checks.check(
        comparison_reconciliation.get("strict_external_error_claim_allowed_rows") == 0,
        "comparison reconciliation strict external error-claim rows changed",
    )
    checks.check(
        comparison_reconciliation.get("source_policy_superiority_claim_allowed") is False,
        "comparison reconciliation overclaims source-policy superiority",
    )
    checks.check(comparison_reconciliation.get("common_reference_cells") == 44, "comparison cell count changed")
    checks.check(comparison_reconciliation.get("raw_rows_recomputed") == 132, "comparison raw row count changed")
    checks.check(comparison_reconciliation.get("summary_mismatches") == 0, "comparison mismatch count changed")
    checks.check(
        comparison_reconciliation.get("direct_nonlocal_velocity_order_wins")
        == comparison_reconciliation.get("direct_nonlocal_velocity_order_comparisons")
        == 40,
        "direct nonlocal order win count changed",
    )
    checks.check(
        comparison_reconciliation.get("direct_nonlocal_finest_velocity_error_wins")
        == comparison_reconciliation.get("direct_nonlocal_finest_velocity_error_comparisons")
        == 40,
        "direct nonlocal finest-error win count changed",
    )
    checks.check(
        comparison_reconciliation.get("source_policy_flagged_rows") == 15,
        "source-policy flagged row count changed",
    )
    checks.check(
        comparison_reconciliation.get("source_policy_velocity_mismatch_rows") == 10,
        "source-policy velocity mismatch count changed",
    )
    checks.check(
        comparison_reconciliation.get("b2_b4_reconciliation", {}).get("paper_submission_b2_b4_can_close_now") is False,
        "comparison reconciliation incorrectly closes B2/B4",
    )
    require_tokens(
        checks,
        comparison_reconciliation_md,
        [
            "bounded common-reference diagnostic assembled",
            "Comparison matrix closed: `True`",
            "Paper direct error superiority allowed: `False`",
            "Strict external error-claim rows allowed: `0`",
            "Direct nonlocal velocity-order wins: `40/40`",
            "Direct nonlocal finest-velocity-error wins: `40/40`",
            "B2/B4 can close now: `False`",
        ],
        "COMPARISON_OBJECTIVE_CLOSURE_RECONCILIATION_AUDIT.md",
    )
    checks.check(all_source_policy.get("schema") == "all-examples-source-policy-audit-v1", "all-example source-policy schema changed")
    checks.check(
        all_source_policy.get("coverage", {}).get("flagged_row_count") == 15,
        "all-example source-policy flagged rows changed",
    )
    checks.check(
        all_source_policy.get("coverage", {}).get("flagged_raw_row_count") == 45,
        "all-example source-policy raw rows changed",
    )
    checks.check(
        all_source_policy.get("closure_boundary", {}).get("b2_can_close_now") is False,
        "all-example source-policy incorrectly closes B2",
    )
    checks.check(
        all_source_policy.get("execution_policy", {}).get("heavy_numerical_run_invoked") is False,
        "all-example source-policy invoked heavy run",
    )
    require_tokens(
        checks,
        all_source_policy_md,
        [
            "Flagged rows checked: `15`",
            "Flagged raw rows checked: `45`",
            "All four examples covered: `True`",
            "B2/B4 can close now: `False/False`",
        ],
        "ALL_EXAMPLES_SOURCE_POLICY_AUDIT.md",
    )
    checks.check(
        all_method_disposition.get("schema") == "all-method-example-claim-disposition-audit-v1",
        "all-method claim-disposition schema changed",
    )
    checks.check(
        all_method_disposition.get("status")
        == "all_nonlocal_method_example_rows_checked_common_reference_closed_source_policy_open",
        "all-method claim-disposition status changed",
    )
    checks.check(
        all_method_disposition.get("coverage", {}).get("all_four_examples_checked") is True,
        "all-method claim-disposition no longer covers all four examples",
    )
    checks.check(
        all_method_disposition.get("coverage", {}).get("examples") == EXPECTED_EXAMPLES,
        "all-method claim-disposition example list changed",
    )
    checks.check(all_method_disposition.get("coverage", {}).get("total_cells") == 44, "all-method total cell count changed")
    checks.check(
        all_method_disposition.get("coverage", {}).get("nonlocal_cells")
        == all_method_disposition.get("coverage", {}).get("expected_nonlocal_cells")
        == 40,
        "all-method nonlocal cell count changed",
    )
    checks.check(
        all_method_disposition.get("coverage", {}).get("raw_rows_recomputed") == 132,
        "all-method raw row count changed",
    )
    checks.check(
        all_method_disposition.get("coverage", {}).get("summary_mismatches") == 0,
        "all-method summary mismatch count changed",
    )
    checks.check(
        all_method_disposition.get("claim_boundary", {}).get("nonlocal_source_policy_closed_rows") == 0,
        "all-method source-policy closed rows changed",
    )
    checks.check(
        all_method_disposition.get("claim_boundary", {}).get("nonlocal_source_policy_open_rows") == 40,
        "all-method source-policy open rows changed",
    )
    checks.check(
        all_method_disposition.get("claim_boundary", {}).get("flagged_nonlocal_rows") == 15,
        "all-method flagged nonlocal rows changed",
    )
    checks.check(
        all_method_disposition.get("claim_boundary", {}).get("strict_external_error_claim_allowed_rows") == 0,
        "all-method strict external error claim rows changed",
    )
    checks.check(
        all_method_disposition.get("claim_boundary", {}).get("source_policy_superiority_claim_allowed") is False,
        "all-method overclaims source-policy superiority",
    )
    checks.check(
        all_method_disposition.get("execution_policy", {}).get("heavy_numerical_run_invoked") is False,
        "all-method claim-disposition audit invoked heavy run",
    )
    checks.check(
        all_method_disposition.get("execution_policy", {}).get("run_v047_invoked") is False,
        "all-method claim-disposition audit invoked run_v047",
    )
    checks.check(
        all_method_disposition.get("execution_policy", {}).get("v048_runner_invoked") is False,
        "all-method claim-disposition audit invoked v048 runner",
    )
    require_tokens(
        checks,
        all_method_disposition_md,
        [
            "Examples checked: `single_pendulum, double_pendulum, four_link, slider_crank`",
            "Method/example cells: `44/44`",
            "Nonlocal comparison cells: `40/40`",
            "Nonlocal source-policy closed rows: `0/40`",
            "Nonlocal source-policy open rows: `40/40`",
            "Strict external error-claim rows: `0`",
        ],
        "ALL_METHOD_EXAMPLE_CLAIM_DISPOSITION_AUDIT.md",
    )

    same_test = gate.get("same_test_boundary", {})
    checks.check(same_test.get("same_test_campaign_status") == cases.get("same_test_campaign_status") == "not_run", "same-test status changed")
    checks.check(
        cases.get("status") == "spec_extracted_partial_evidence_not_full_campaign",
        "case inventory status changed",
    )
    checks.check(cases.get("default_1e-4_required") is False, "case inventory incorrectly requires default 1e-4")
    checks.check("partial_evidence_overlay" in cases, "case inventory lost partial evidence overlay")
    checks.check(same_test.get("external_superiority_claim") is False, "same-test boundary claims superiority")
    checks.check(same_test.get("comparison_matrix_closed") is True, "same-test boundary lost comparison matrix closure")
    checks.check(same_test.get("comparison_matrix_closed") == comparison_reconciliation.get("comparison_matrix_closed"), "same-test matrix closure mismatch")
    checks.check(same_test.get("common_reference_claim_allowed") is True, "same-test common-reference claim boundary changed")
    checks.check(
        same_test.get("source_policy_superiority_claim_allowed") is False,
        "same-test source-policy superiority boundary changed",
    )
    checks.check(same_test.get("common_reference_examples") == EXPECTED_EXAMPLES, "same-test all-example coverage changed")
    checks.check(same_test.get("common_reference_cells") == 44, "same-test common-reference cell count changed")
    checks.check(same_test.get("raw_rows_recomputed") == 132, "same-test raw row count changed")
    checks.check(same_test.get("summary_mismatches") == 0, "same-test summary mismatch count changed")
    checks.check(same_test.get("direct_nonlocal_velocity_order_wins") == 40, "same-test order win count changed")
    checks.check(same_test.get("direct_nonlocal_velocity_order_comparisons") == 40, "same-test order comparison count changed")
    checks.check(same_test.get("direct_nonlocal_finest_velocity_error_wins") == 40, "same-test error win count changed")
    checks.check(same_test.get("direct_nonlocal_finest_velocity_error_comparisons") == 40, "same-test error comparison count changed")
    checks.check(
        same_test.get("local_evidence_coverage_examples")
        == four_example_dashboard.get("local_evidence_coverage_example_names")
        == EXPECTED_EXAMPLES,
        "same-test local evidence-coverage examples changed",
    )
    checks.check(
        same_test.get("local_evidence_coverage_count")
        == four_example_dashboard.get("local_evidence_coverage_examples")
        == 4,
        "same-test local evidence-coverage count changed",
    )
    checks.check(
        same_test.get("accepted_method_dynamic_order_examples")
        == four_example_dashboard.get("accepted_method_dynamic_order_examples")
        == EXPECTED_DYNAMIC_ORDER_EXAMPLES,
        "same-test accepted method dynamic-order examples changed",
    )
    checks.check(
        same_test.get("accepted_method_dynamic_order_example_count")
        == four_example_dashboard.get("accepted_method_dynamic_order_example_count")
        == 2,
        "same-test accepted method dynamic-order count changed",
    )
    checks.check(
        same_test.get("mechanism_coverage_examples")
        == four_example_dashboard.get("mechanism_coverage_examples")
        == EXPECTED_COVERAGE_ONLY_EXAMPLES,
        "same-test mechanism-coverage examples changed",
    )
    checks.check(
        same_test.get("mechanism_coverage_example_count")
        == four_example_dashboard.get("mechanism_coverage_example_count")
        == 2,
        "same-test mechanism-coverage count changed",
    )
    checks.check(
        same_test.get("local_dynamic_order_closed_examples")
        == four_example_dashboard.get("local_dynamic_order_closed_example_names")
        == ["single_pendulum", "double_pendulum"],
        "same-test local dynamic-order examples changed",
    )
    checks.check(
        same_test.get("local_dynamic_order_closed_count")
        == four_example_dashboard.get("local_dynamic_order_closed_examples")
        == 2,
        "same-test local dynamic-order count changed",
    )
    checks.check(
        same_test.get("accepted_source_policy_dynamic_order_examples_count")
        == four_example_dashboard.get("accepted_source_policy_dynamic_order_examples")
        == 0,
        "same-test source-policy dynamic-order count changed",
    )
    checks.check(same_test.get("source_policy_flagged_rows") == 15, "same-test source-policy flagged count changed")
    checks.check(
        same_test.get("source_policy_velocity_mismatch_rows") == 10,
        "same-test source-policy velocity mismatch count changed",
    )
    checks.check(
        same_test.get("all_method_claim_disposition_audit_status") == all_method_disposition.get("status"),
        "same-test all-method claim-disposition status changed",
    )
    checks.check(
        same_test.get("all_method_claim_disposition_all_four_examples") is True,
        "same-test all-method four-example coverage changed",
    )
    checks.check(
        same_test.get("all_method_claim_disposition_total_cells")
        == all_method_disposition.get("coverage", {}).get("total_cells")
        == 44,
        "same-test all-method total cells changed",
    )
    checks.check(
        same_test.get("all_method_claim_disposition_nonlocal_cells")
        == all_method_disposition.get("coverage", {}).get("nonlocal_cells")
        == 40,
        "same-test all-method nonlocal cells changed",
    )
    checks.check(
        same_test.get("all_method_claim_disposition_source_policy_closed_rows")
        == all_method_disposition.get("claim_boundary", {}).get("nonlocal_source_policy_closed_rows")
        == 0,
        "same-test all-method source-policy closed rows changed",
    )
    checks.check(
        same_test.get("all_method_claim_disposition_source_policy_open_rows")
        == all_method_disposition.get("claim_boundary", {}).get("nonlocal_source_policy_open_rows")
        == 40,
        "same-test all-method source-policy open rows changed",
    )
    checks.check(
        same_test.get("all_method_claim_disposition_flagged_nonlocal_rows")
        == all_method_disposition.get("claim_boundary", {}).get("flagged_nonlocal_rows")
        == 15,
        "same-test all-method flagged nonlocal rows changed",
    )
    checks.check(
        same_test.get("all_method_claim_disposition_strict_external_error_claim_allowed_rows")
        == all_method_disposition.get("claim_boundary", {}).get("strict_external_error_claim_allowed_rows")
        == 0,
        "same-test all-method strict external rows changed",
    )
    checks.check(
        same_test.get("all_examples_source_policy_audit_status") == all_source_policy.get("status"),
        "same-test all-example source-policy status changed",
    )
    checks.check(
        same_test.get("all_examples_source_policy_flagged_rows")
        == all_source_policy.get("coverage", {}).get("flagged_row_count")
        == 15,
        "same-test all-example source-policy flagged rows changed",
    )
    checks.check(
        same_test.get("all_examples_source_policy_flagged_raw_rows")
        == all_source_policy.get("coverage", {}).get("flagged_raw_row_count")
        == 45,
        "same-test all-example source-policy raw rows changed",
    )
    checks.check(
        same_test.get("all_examples_source_policy_all_four_examples") is True,
        "same-test all-example source-policy coverage marker changed",
    )
    checks.check(
        same_test.get("all_examples_source_policy_all_three_step_sizes") is True,
        "same-test all-example source-policy step-size marker changed",
    )
    checks.check(same_test.get("source_policy_reproduction_open") is True, "same-test source-policy boundary changed")
    checks.check(
        same_test.get("hi2022_source_policy_row_audit_status") == hi2022_source_policy_audit.get("status"),
        "same-test HI2022 source-policy row audit status changed",
    )
    checks.check(
        same_test.get("hi2022_active_b2_flagged_rows")
        == hi2022_source_policy_audit.get("active_b2_flagged_rows")
        == 3,
        "same-test HI2022 active flagged rows changed",
    )
    checks.check(
        same_test.get("hi2022_source_policy_reproduction_rows")
        == hi2022_source_policy_audit.get("source_policy_closed_rows")
        == 0,
        "same-test HI2022 source-policy rows changed",
    )
    checks.check(
        same_test.get("hi2022_can_close_b2_requirement_now")
        == hi2022_source_policy_audit.get("decision", {}).get("can_close_hi2022_b2_requirement_now")
        is False,
        "same-test HI2022 B2 requirement unexpectedly closed",
    )
    checks.check(
        same_test.get("tfe_source_policy_row_audit_status") == tfe_source_policy_audit.get("status"),
        "same-test TFE source-policy row audit status changed",
    )
    checks.check(
        same_test.get("tfe_active_b2_flagged_rows")
        == tfe_source_policy_audit.get("active_b2_flagged_rows")
        == 0,
        "same-test TFE active flagged rows changed",
    )
    checks.check(
        same_test.get("tfe_source_policy_spec_extracted") is True,
        "same-test TFE spec extraction marker changed",
    )
    checks.check(
        same_test.get("tfe_pendulum_dae_runner_implemented") is False,
        "same-test TFE pendulum runner unexpectedly implemented",
    )
    checks.check(
        same_test.get("tfe_source_policy_reproduction_rows")
        == tfe_source_policy_audit.get("source_policy_closed_rows")
        == 0,
        "same-test TFE source-policy rows changed",
    )
    checks.check(
        same_test.get("tfe_can_close_b2_requirement_now")
        == tfe_source_policy_audit.get("decision", {}).get("can_close_tfe_b2_requirement_now")
        is False,
        "same-test TFE B2 requirement unexpectedly closed",
    )
    checks.check(
        same_test.get("b2_remaining_work_manifest_status") == b2_remaining_work.get("status"),
        "same-test B2 remaining-work manifest status changed",
    )
    checks.check(
        same_test.get("b2_remaining_active_flagged_rows")
        == b2_remaining_work.get("active_flagged_row_count")
        == 0,
        "same-test B2 active flagged rows changed",
    )
    checks.check(
        same_test.get("b2_remaining_demoted_flagged_rows")
        == b2_remaining_work.get("demoted_flagged_row_count")
        == 15,
        "same-test B2 demoted flagged rows changed",
    )
    checks.check(
        same_test.get("b2_remaining_source_policy_closed_rows")
        == b2_remaining_work.get("source_policy_closed_rows")
        == 0,
        "same-test B2 source-policy closed rows changed",
    )
    checks.check(
        same_test.get("b2_remaining_external_superiority_ready_rows")
        == b2_remaining_work.get("external_superiority_ready_rows")
        == 0,
        "same-test B2 external-superiority-ready rows changed",
    )
    closure_plan = b2_remaining_work.get("closure_execution_plan", {})
    checks.check(
        same_test.get("b2_closure_execution_plan_schema")
        == closure_plan.get("schema")
        == "b2-source-policy-closure-execution-plan-v1",
        "same-test B2 closure execution plan schema changed",
    )
    checks.check(
        same_test.get("b2_closure_execution_plan_all_active_suites_ready")
        == closure_plan.get("all_active_suites_ready_to_launch")
        is True,
        "same-test B2 closure plan launch readiness changed",
    )
    checks.check(
        same_test.get("b2_closure_execution_plan_explicit_1e-4_opt_in")
        == closure_plan.get("source_policy_1e_4_requires_explicit_flag")
        is True,
        "same-test B2 closure plan explicit 1e-4 guard changed",
    )
    checks.check(
        same_test.get("b2_closure_execution_plan_external_superiority_after_plan_only")
        == closure_plan.get("external_superiority_claim_allowed_after_plan_only")
        is False,
        "same-test B2 closure plan overclaims plan-only superiority",
    )
    checks.check(same_test.get("paper_submission_b2_b4_can_close_now") is False, "same-test incorrectly closes B2/B4")
    checks.check(same_test.get("dynamic_order_missing_examples") == [], "same-test dynamic-order missing examples changed")
    checks.check(
        same_test.get("local_true_dynamic_order_examples") == EXPECTED_COVERAGE_ONLY_EXAMPLES,
        "same-test closed-loop coarse-dynamics examples changed",
    )
    checks.check(same_test.get("local_true_dynamic_order_candidate_count") == 2, "same-test closed-loop coarse-dynamics diagnostic count changed")
    checks.check(
        same_test.get("four_link_true_dynamic_primary_orders") == [5.955, 5.955, 6.085, 5.971],
        "same-test four-link coarse-dynamics primary diagnostic slopes changed",
    )
    checks.check(
        same_test.get("slider_crank_true_dynamic_primary_orders") == [6.164, 6.159, 7.341, 6.426],
        "same-test slider-crank coarse-dynamics primary diagnostic slopes changed",
    )
    checks.check(
        same_test.get("public_work_precision_available_examples") == EXPECTED_COVERAGE_ONLY_EXAMPLES,
        "same-test public work/precision available examples changed",
    )
    checks.check(
        same_test.get("public_work_precision_missing_examples") == [],
        "same-test public work/precision missing examples changed",
    )
    checks.check(
        same_test.get("strict_common_reference_available_examples") == EXPECTED_COVERAGE_ONLY_EXAMPLES,
        "same-test strict common-reference available examples changed",
    )
    checks.check(
        same_test.get("strict_common_reference_gap_examples") == [],
        "same-test strict common-reference gap examples changed",
    )
    checks.check(same_test.get("strict_common_reference_figure_available") is True, "same-test strict figure marker changed")
    checks.check(
        same_test.get("strict_common_reference_figure_integrated_in_manuscript") is True,
        "same-test strict figure integration marker changed",
    )
    checks.check(same_test.get("coarse_baseline_work_precision_figure_available") is True, "same-test coarse baseline/work-precision figure marker changed")
    checks.check(
        same_test.get("coarse_baseline_work_precision_figure_integrated_in_manuscript") is True,
        "same-test coarse baseline/work-precision figure integration marker changed",
    )
    checks.check(same_test.get("closed_loop_true_dynamic_order_figure_available") is True, "same-test true-dynamic order figure marker changed")
    checks.check(
        same_test.get("closed_loop_true_dynamic_order_figure_integrated_in_manuscript") is True,
        "same-test true-dynamic order figure integration marker changed",
    )
    prose_boundary = gate.get("prose_residue_boundary", {})
    checks.check(prose_boundary.get("audit") == "CMAME_PROSE_RESIDUE_AUDIT.md", "prose boundary audit path missing")
    checks.check(prose_boundary.get("audit_json") == "CMAME_PROSE_RESIDUE_AUDIT.json", "prose boundary audit JSON path missing")
    checks.check(prose_boundary.get("validator") == "validate_cmame_prose_residue_audit.py", "prose boundary validator missing")
    checks.check(prose_boundary.get("main_body_machine_token_count") == 0, "prose boundary main-body count changed")
    checks.check(prose_boundary.get("flat_main_body_machine_token_count") == 0, "prose boundary flat main-body count changed")
    checks.check(prose_boundary.get("artifact_macro_confined_to_appendix") is True, "prose boundary appendix marker changed")
    checks.check(prose_boundary.get("appendix_artifact_macro_count") == 0, "prose boundary appendix count changed")
    checks.check(prose_boundary.get("flat_appendix_artifact_macro_count") == 0, "prose boundary flat appendix count changed")
    checks.check(prose_boundary.get("reproducibility_appendix_compacted") is True, "prose boundary compaction marker missing")
    checks.check(prose_boundary.get("b6_closed") is True, "prose boundary did not close B6")
    checks.check(prose_boundary.get("default_1e-4_required") is False, "prose boundary incorrectly requires default 1e-4")
    checks.check(prose_boundary.get("run_v047_invoked") is False, "prose boundary invoked run_v047")
    checks.check(coarse_first.get("same_test_campaign_status") == "not_run", "coarse-first gate same-test status changed")
    checks.check(coarse_first.get("external_superiority_claim") is False, "coarse-first gate claims superiority")
    checks.check(coarse_first.get("coarse_same_window_ready_count") == 2, "coarse-first ready count changed")
    checks.check(coarse_first.get("local_true_dynamic_order_available_count") == 2, "coarse-first local dynamic-order count changed")
    checks.check(coarse_first.get("public_work_precision_available_count") == 2, "coarse-first public work/precision availability count changed")
    checks.check(coarse_first.get("public_work_precision_missing_count") == 0, "coarse-first public work/precision missing count changed")
    checks.check(coarse_first.get("strict_common_reference_available_count") == 2, "coarse-first strict common-reference availability count changed")
    checks.check(coarse_first.get("strict_common_reference_gap_count") == 0, "coarse-first strict common-reference gap count changed")
    checks.check(coarse_first.get("strict_common_reference_figure_available") is True, "coarse-first strict common-reference figure marker changed")
    checks.check(coarse_first.get("dynamic_order_missing_count") == 0, "coarse-first missing count changed")
    checks.check(coarse_first.get("default_policy") == "coarse_first_no_default_1e-4", "coarse-first default policy changed")
    checks.check(coarse_probe.get("accepted_dynamic_order_count") == 0, "coarse probe dynamic-order count changed")
    checks.check(coarse_probe.get("step_sizes") == [0.1, 0.05, 0.025], "coarse probe step sizes changed")
    checks.check(coarse_probe.get("reference_h") == 0.0125, "coarse probe reference changed")
    checks.check(coarse_probe.get("same_test_campaign_status") == "not_run", "coarse probe same-test status changed")
    checks.check(true_dynamic_newton.get("schema") == "closed-loop-true-dynamic-newton-coarse-order-v1", "true-dynamic Newton schema changed")
    checks.check(true_dynamic_newton.get("status") == "coarse_true_dynamic_order_candidates_available_not_external_superiority", "true-dynamic Newton status changed")
    checks.check(true_dynamic_newton.get("accepted_dynamic_order_count") == 2, "true-dynamic Newton candidate count changed")
    checks.check(true_dynamic_newton.get("row_count") == 6, "true-dynamic Newton row count changed")
    checks.check(true_dynamic_newton.get("ok_row_count") == 6, "true-dynamic Newton ok row count changed")
    checks.check(true_dynamic_newton.get("step_sizes") == [0.1, 0.05, 0.025], "true-dynamic Newton step sizes changed")
    checks.check(true_dynamic_newton.get("stage_oracle_used") is False, "true-dynamic Newton unexpectedly used stage oracle")
    checks.check(true_dynamic_newton.get("default_1e-4_required") is False, "true-dynamic Newton incorrectly requires default 1e-4")
    checks.check(true_dynamic_newton.get("heavy_numerical_run_invoked") is False, "true-dynamic Newton invoked heavy numerical run")
    checks.check(true_dynamic_newton.get("external_superiority_claim") is False, "true-dynamic Newton overclaims external superiority")
    checks.check(public_work.get("public_work_precision_available_count") == 2, "public work/precision availability count changed")
    checks.check(public_work.get("public_work_precision_missing_count") == 0, "public work/precision missing count changed")
    checks.check(public_work.get("strict_common_reference_error_columns") is False, "public work/precision strict reference flag changed")
    checks.check(public_work.get("external_superiority_claim") is False, "public work/precision overclaimed superiority")
    checks.check(strict_common.get("strict_common_reference_available_count") == 2, "strict common-reference availability changed")
    checks.check(strict_common.get("strict_common_reference_gap_count") == 0, "strict common-reference gap changed")
    checks.check(strict_common.get("strict_common_reference_error_columns") is True, "strict common-reference flag changed")
    checks.check(strict_common.get("publication_quality_figure_available") is True, "strict common-reference figure changed")
    checks.check(strict_common.get("external_superiority_claim") is False, "strict common-reference overclaimed superiority")
    checks.check(performance.get("examples") == EXPECTED_EXAMPLES, "performance summary examples changed")
    checks.check(performance.get("completed_row_count") == 32, "performance completed-row count changed")
    checks.check(performance.get("partial_row_count") == 0, "performance partial-row count changed")
    checks.check(performance.get("external_superiority_claim") is False, "performance matrix claims superiority")
    checks.check(
        kinematic_defect.get("schema") == "kinematic-row-defect-certificate-v1",
        "kinematic defect certificate schema changed",
    )
    checks.check(
        kinematic_defect.get("proof_scope", {}).get("certified_row_count") == 96,
        "kinematic defect certificate row count changed",
    )
    checks.check(
        kinematic_defect.get("proof_scope", {}).get("excluded_row_family") == "newton_euler_weak_balance",
        "kinematic defect certificate excluded family changed",
    )
    checks.check(
        kinematic_defect.get("certificate", {}).get("stage_residual_O_h7_implementation_defect_proved") is False,
        "kinematic defect certificate overclaims full O(h^7) proof",
    )
    checks.check(
        newton_euler_obligation.get("schema") == "newton-euler-defect-obligation-gate-v1",
        "Newton-Euler obligation gate schema changed",
    )
    checks.check(
        newton_euler_obligation.get("status")
        == "d5_symbolic_primitive_route_open_active_direct_pc2_closed_not_submission_ready",
        "Newton-Euler obligation gate status changed",
    )
    checks.check(
        newton_euler_obligation.get("proof_scope", {}).get("row_family") == "newton_euler_weak_balance",
        "Newton-Euler obligation row family changed",
    )
    checks.check(
        newton_euler_obligation.get("proof_scope", {}).get("dynamic_row_count") == 36,
        "Newton-Euler obligation row count changed",
    )
    checks.check(
        newton_euler_obligation.get("closure_state", {}).get("open_obligation_count") == 1,
        "Newton-Euler obligation open count changed",
    )
    checks.check(
        newton_euler_obligation.get("closure_state", {}).get("closed_obligation_count") == 5,
        "Newton-Euler obligation closed count changed",
    )
    checks.check(
        newton_euler_obligation.get("closure_state", {}).get("stage_residual_O_h7_implementation_defect_proved") is False,
        "Newton-Euler symbolic/primitive route overclaims full O(h^7) proof",
    )
    checks.check(
        newton_euler_obligation.get("closure_state", {}).get("active_direct_pc2_closed") is True,
        "Newton-Euler obligation gate lost active direct PC2 closure marker",
    )
    checks.check(
        newton_euler_obligation.get("execution_policy", {}).get("default_1e-4_required") is False,
        "Newton-Euler obligation gate incorrectly requires default 1e-4",
    )
    checks.check(
        newton_euler_symbolic_target.get("schema") == "newton-euler-symbolic-target-audit-v1",
        "Newton-Euler symbolic target audit schema changed",
    )
    checks.check(
        newton_euler_symbolic_target.get("status") == "row_level_symbolic_targets_extracted_dynamic_defect_proof_open",
        "Newton-Euler symbolic target audit status changed",
    )
    checks.check(newton_euler_symbolic_target.get("row_count") == 36, "Newton-Euler symbolic target row count changed")
    checks.check(
        newton_euler_symbolic_target.get("translational_row_count") == 18,
        "Newton-Euler translational target row count changed",
    )
    checks.check(
        newton_euler_symbolic_target.get("rotational_row_count") == 18,
        "Newton-Euler rotational target row count changed",
    )
    checks.check(
        newton_euler_symbolic_target.get("closure_boundary", {}).get("symbolic_target_inventory_complete") is True,
        "Newton-Euler symbolic target inventory marker changed",
    )
    checks.check(
        newton_euler_symbolic_target.get("closure_boundary", {}).get("newton_euler_symbolic_defect_certificate_complete")
        is False,
        "Newton-Euler symbolic target audit overclaims symbolic defect certificate",
    )
    checks.check(
        newton_euler_symbolic_target.get("closure_boundary", {}).get("stage_residual_O_h7_implementation_defect_proved")
        is False,
        "Newton-Euler symbolic target audit overclaims O(h^7) stage residual proof",
    )

    blockers = gate.get("blockers", [])
    blocker_ids = {blocker.get("id") for blocker in blockers if isinstance(blocker, dict)}
    checks.check(len(blockers) == 8, "gate must track exactly B1-B8")
    checks.check(blocker_ids == EXPECTED_BLOCKERS, f"blocker IDs changed: {sorted(blocker_ids)}")
    for blocker in blockers:
        if not isinstance(blocker, dict):
            checks.check(False, "blocker entry is not an object")
            continue
        blocker_id = blocker.get("id", "<missing>")
        checks.check(blocker.get("default_1e-4_required") is False, f"{blocker_id} incorrectly requires default 1e-4")
        if blocker_id == "B5":
            checks.check(blocker.get("severity") == "closed", "B5 severity should be closed")
            checks.check(blocker.get("status") == "closed", "B5 should be closed")
            checks.check(blocker.get("closure_evidence") == "CMAME_VISUAL_LEGIBILITY_AUDIT.md", "B5 closure evidence missing")
            checks.check(blocker.get("closure_evidence_json") == "CMAME_VISUAL_LEGIBILITY_AUDIT.json", "B5 closure evidence JSON missing")
            checks.check(blocker.get("closure_basis") == "final_pdf_legibility_check", "B5 closure basis changed")
            checks.check(blocker.get("split_mechanism_diagrams_required") is False, "B5 split requirement changed")
            continue
        if blocker_id == "B8":
            checks.check(blocker.get("severity") == "closed", "B8 severity should be closed")
            checks.check(blocker.get("status") == "closed", "B8 should be closed")
            checks.check(blocker.get("closure_evidence") == "CMAME_RELATED_WORK_AUDIT.md", "B8 closure evidence missing")
            checks.check(blocker.get("closure_evidence_json") == "CMAME_RELATED_WORK_AUDIT.json", "B8 closure evidence JSON missing")
            checks.check(blocker.get("closure_basis") == "expanded_six_cluster_related_work_and_reference_set", "B8 closure basis changed")
            continue
        if blocker_id == "B1":
            checks.check(blocker.get("severity") == "closed", "B1 severity should be closed")
            checks.check(
                blocker.get("status") == "closed",
                "B1 should be closed by AD-expanded symbolic oracle certificate",
            )
            checks.check(
                blocker.get("closure_evidence") == "B1_AD_EXPANDED_SYMBOLIC_ORACLE_CLOSURE_CERTIFICATE.md",
                "B1 closure evidence missing",
            )
            checks.check(
                blocker.get("closure_evidence_json") == "B1_AD_EXPANDED_SYMBOLIC_ORACLE_CLOSURE_CERTIFICATE.json",
                "B1 closure evidence JSON missing",
            )
            checks.check(
                blocker.get("closure_basis")
                == "residual_identity_chain_rule_ad_expanded_symbolic_oracle",
                "B1 closure basis changed",
            )
            checks.check(blocker.get("required_to_close") == [], "B1 should have no remaining requirements")
        elif blocker_id == "B2":
            checks.check(blocker.get("severity") == "blocking", "B2 severity should stay blocking for future external-superiority claims")
            checks.check(blocker.get("status") == "closed", "B2 should be closed by Route B claim demotion")
            checks.check(
                "route_b_claim_demotion_policy_applied" in blocker.get("partial_progress", []),
                "B2 lost Route B claim-demotion progress marker",
            )
            checks.check(
                blocker.get("route_b_claim_demotion_policy_applied") is True,
                "B2 Route B claim-demotion marker changed",
            )
            checks.check(
                blocker.get("route_b_closes_external_superiority_claim_only") is True,
                "B2 Route B closure scope changed",
            )
            checks.check(
                blocker.get("source_policy_superiority_claim_allowed") is False,
                "B2 Route B closure overclaims external superiority",
            )
            checks.check(
                blocker.get("all_method_claim_disposition_source_policy_closed_rows") == 0,
                "B2 Route B closure should not close source-policy rows",
            )
            checks.check(
                blocker.get("b2_remaining_work_manifest_status")
                == "route_b_all_external_suites_demoted_no_active_external_superiority_rows",
                "B2 Route B remaining-work status changed",
            )
        elif blocker_id == "B3":
            checks.check(blocker.get("severity") == "closed", "B3 severity should be closed")
            checks.check(blocker.get("status") == "closed", "B3 should be closed by direct residual-bridge/Kantorovich route")
            checks.check(blocker.get("closure_evidence") == "B3_DIRECT_PROOF_REVIEW_AUDIT.md", "B3 closure evidence missing")
            checks.check(
                blocker.get("closure_evidence_json") == "B3_DIRECT_PROOF_REVIEW_AUDIT.json",
                "B3 closure evidence JSON missing",
            )
            checks.check(
                blocker.get("closure_basis") == "direct_residual_bridge_kantorovich_route",
                "B3 closure basis changed",
            )
            checks.check(
                blocker.get("required_to_close") == [],
                "B3 should have no remaining closure requirements",
            )
            checks.check(
                blocker.get("diagnostic_primitive_taylor_route_open_items")
                == [
                    "prove_five_open_primitive_taylor_lift_obligations",
                    "certify_all_162_D5_Taylor_subterms",
                    "close_primitive_taylor_PC2_route",
                ],
                "B3 diagnostic primitive route open items changed",
            )
        else:
            if blocker_id in {"B4", "B6", "B7"}:
                checks.check(blocker.get("severity") == "closed", f"{blocker_id} severity changed")
                checks.check(blocker.get("status") == "closed", f"{blocker_id} should be closed under narrowed policy")
                checks.check(blocker.get("required_to_close") == [], f"{blocker_id} should have no current-scope closure requirements")
            else:
                checks.check(blocker_id in EXPECTED_OPEN_BLOCKERS, f"{blocker_id} unexpected open blocker ID")
                checks.check(blocker.get("severity") == "blocking", f"{blocker_id} severity changed")
                checks.check(blocker.get("status") == "open", f"{blocker_id} should remain open until evidence closes it")
                checks.check(blocker.get("required_to_close"), f"{blocker_id} has no closure requirements")
        if blocker_id == "B1":
            checks.check(
                blocker.get("runtime_row_layout_oracle") == "DYNAMIC_ROW_ORACLE_GATE.md",
                "B1 runtime row oracle path missing",
            )
            checks.check(
                blocker.get("runtime_row_layout_oracle_status") == "row_and_block_passable_not_symbolic",
                "B1 runtime row oracle status changed",
            )
            checks.check(
                blocker.get("runtime_block_functional_oracle_status") == "gauss6_equivalent_crosscheck_passable_not_symbolic",
                "B1 runtime block-functional oracle status changed",
            )
            checks.check(
                blocker.get("partial_formula_row_oracle") == "DYNAMIC_ROW_ORACLE_GATE.md",
                "B1 partial formula-row oracle path missing",
            )
            checks.check(
                blocker.get("partial_formula_row_oracle_status")
                == "96_kinematic_and_lower_pair_rows_passable_newton_euler_excluded",
                "B1 partial formula-row oracle status changed",
            )
            checks.check(blocker.get("partial_formula_row_count") == 96, "B1 partial formula-row count changed")
            checks.check(
                blocker.get("partial_formula_excluded_row_family") == "newton_euler_weak_balance",
                "B1 partial formula-row exclusion changed",
            )
            checks.check(
                "partial_independent_formula_row_oracle_96_rows" in blocker.get("partial_progress", []),
                "B1 lost partial formula-row progress marker",
            )
            checks.check(
                blocker.get("partial_kinematic_stage_defect_certificate") == "KINEMATIC_ROW_DEFECT_CERTIFICATE.md",
                "B1 partial kinematic defect certificate path missing",
            )
            checks.check(
                blocker.get("partial_kinematic_stage_defect_rows") == 96,
                "B1 partial kinematic defect row count changed",
            )
            checks.check(
                "partial_kinematic_stage_defect_certificate_96_rows" in blocker.get("partial_progress", []),
                "B1 lost partial kinematic defect progress marker",
            )
            checks.check(
                "KINEMATIC_ROW_DEFECT_CERTIFICATE.md" in blocker.get("partial_progress_evidence", []),
                "B1 partial kinematic defect evidence missing",
            )
            checks.check(
                blocker.get("newton_euler_defect_obligation_gate") == "NEWTON_EULER_DEFECT_OBLIGATION_GATE.md",
                "B1 Newton-Euler obligation gate path missing",
            )
            checks.check(
                blocker.get("newton_euler_defect_obligation_rows") == 36,
                "B1 Newton-Euler obligation row count changed",
            )
            checks.check(
                blocker.get("newton_euler_defect_open_obligation_count") == 1,
                "B1 Newton-Euler open obligation count changed",
            )
            checks.check(
                blocker.get("newton_euler_defect_open_obligation_scope")
                == "symbolic_primitive_certificate_route_not_active_direct_pc2",
                "B1 Newton-Euler open obligation scope changed",
            )
            checks.check(
                blocker.get("newton_euler_symbolic_primitive_open_obligation_count") == 1,
                "B1 symbolic/primitive Newton-Euler open obligation count changed",
            )
            checks.check(
                blocker.get("newton_euler_symbolic_primitive_open_obligation_scope")
                == "symbolic_primitive_certificate_route_not_active_direct_pc2",
                "B1 symbolic/primitive Newton-Euler open obligation scope changed",
            )
            checks.check(
                blocker.get("active_direct_newton_euler_open_obligation_count") == 0,
                "B1 active direct Newton-Euler open obligation count changed",
            )
            checks.check(
                blocker.get("active_direct_newton_euler_stage_defect_closed") is True,
                "B1 active direct Newton-Euler stage defect closure marker changed",
            )
            checks.check(
                blocker.get("active_direct_newton_euler_zero_residual_rows") == 36,
                "B1 active direct Newton-Euler zero-row count changed",
            )
            checks.check(
                blocker.get("newton_euler_defect_closed_obligation_count") == 5,
                "B1 Newton-Euler closed obligation count changed",
            )
            checks.check(
                "newton_euler_dynamic_defect_obligation_gate_added" in blocker.get("partial_progress", []),
                "B1 missing Newton-Euler obligation progress marker",
            )
            checks.check(
                "NEWTON_EULER_DEFECT_OBLIGATION_GATE.md" in blocker.get("partial_progress_evidence", []),
                "B1 Newton-Euler obligation evidence missing",
            )
            checks.check(
                "NEWTON_EULER_DEFECT_OBLIGATION_GATE.json" in blocker.get("partial_progress_evidence", []),
                "B1 Newton-Euler obligation JSON evidence missing",
            )
            checks.check(
                "validate_newton_euler_defect_obligation_gate.py" in blocker.get("partial_progress_evidence", []),
                "B1 Newton-Euler obligation validator evidence missing",
            )
            checks.check(
                blocker.get("newton_euler_symbolic_target_audit") == "NEWTON_EULER_SYMBOLIC_TARGET_AUDIT.md",
                "B1 Newton-Euler symbolic target audit path missing",
            )
            checks.check(
                blocker.get("newton_euler_symbolic_target_audit_json") == "NEWTON_EULER_SYMBOLIC_TARGET_AUDIT.json",
                "B1 Newton-Euler symbolic target audit JSON path missing",
            )
            checks.check(
                blocker.get("newton_euler_symbolic_target_status")
                == "row_level_symbolic_targets_extracted_dynamic_defect_proof_open",
                "B1 Newton-Euler symbolic target audit status changed",
            )
            checks.check(
                blocker.get("newton_euler_symbolic_target_rows") == 36,
                "B1 Newton-Euler symbolic target row count changed",
            )
            checks.check(
                blocker.get("newton_euler_symbolic_target_translational_rows") == 18,
                "B1 Newton-Euler translational target row count changed",
            )
            checks.check(
                blocker.get("newton_euler_symbolic_target_rotational_rows") == 18,
                "B1 Newton-Euler rotational target row count changed",
            )
            checks.check(
                blocker.get("newton_euler_symbolic_target_inventory_complete") is True,
                "B1 Newton-Euler symbolic target inventory marker changed",
            )
            checks.check(
                blocker.get("newton_euler_symbolic_defect_certificate_complete") is False,
                "B1 overclaims Newton-Euler symbolic defect certificate",
            )
            checks.check(
                blocker.get("b1_symbolic_row_oracle_closure_certificate")
                == "B1_SYMBOLIC_ROW_ORACLE_CLOSURE_CERTIFICATE.md",
                "B1 symbolic row-oracle closure certificate path missing",
            )
            checks.check(
                blocker.get("b1_symbolic_row_oracle_closure_certificate_json")
                == "B1_SYMBOLIC_ROW_ORACLE_CLOSURE_CERTIFICATE.json",
                "B1 symbolic row-oracle closure certificate JSON path missing",
            )
            checks.check(
                b1_symbolic_row_oracle_closure.get("schema")
                == "b1-symbolic-row-oracle-closure-certificate-v1",
                "B1 symbolic row-oracle closure certificate schema changed",
            )
            checks.check(
                b1_symbolic_row_oracle_closure.get("status")
                == "independent_symbolic_row_oracle_closed_ad_expanded_symbolic_oracle_open",
                "B1 symbolic row-oracle closure certificate status changed",
            )
            checks.check(
                blocker.get("b1_independent_symbolic_row_by_row_oracle_for_expanded_fullva_rows_closed")
                == b1_symbolic_row_oracle_closure.get(
                    "independent_symbolic_row_by_row_oracle_for_expanded_fullva_rows_closed"
                )
                is True,
                "B1 independent symbolic row-oracle item should be closed",
            )
            checks.check(
                blocker.get("b1_independent_symbolic_row_by_row_oracle_closed_rows")
                == b1_symbolic_row_oracle_closure.get("independent_symbolic_row_by_row_oracle_closed_rows")
                == 36,
                "B1 independent symbolic row-oracle row count changed",
            )
            checks.check(
                blocker.get("b1_symbolic_row_oracle_closure_scope")
                == "residual_row_identity_scope_chain_rule_ad_expanded_symbolic_oracle_closed",
                "B1 symbolic row-oracle closure scope changed",
            )
            checks.check(
                b1_symbolic_row_oracle_closure.get("ad_expanded_symbolic_oracle_closure") is False,
                "B1 row-oracle certificate overclaims AD-expanded symbolic closure",
            )
            checks.check(
                b1_symbolic_row_oracle_closure.get("dynamic_symbolic_oracle_complete") is False,
                "B1 row-oracle certificate overclaims dynamic symbolic oracle",
            )
            checks.check(
                b1_symbolic_row_oracle_closure.get("stage_residual_O_h7_symbolic_certificate_proved") is False,
                "B1 row-oracle certificate overclaims symbolic-certificate O(h^7) proof",
            )
            checks.check(
                b1_symbolic_row_oracle_closure.get(
                    "stage_residual_O_h7_implementation_defect_proved_from_this_certificate"
                )
                is False,
                "B1 row-oracle certificate overclaims implementation-defect proof",
            )
            checks.check(
                blocker.get("b1_ad_expanded_symbolic_oracle_closure_certificate")
                == "B1_AD_EXPANDED_SYMBOLIC_ORACLE_CLOSURE_CERTIFICATE.md",
                "B1 AD-expanded symbolic closure certificate path missing",
            )
            checks.check(
                blocker.get("b1_ad_expanded_symbolic_oracle_closure_certificate_json")
                == "B1_AD_EXPANDED_SYMBOLIC_ORACLE_CLOSURE_CERTIFICATE.json",
                "B1 AD-expanded symbolic closure certificate JSON path missing",
            )
            checks.check(
                b1_ad_expanded_symbolic_oracle_closure.get("schema")
                == "b1-ad-expanded-symbolic-oracle-closure-certificate-v1",
                "B1 AD-expanded symbolic closure certificate schema changed",
            )
            checks.check(
                b1_ad_expanded_symbolic_oracle_closure.get("status")
                == "ad_expanded_symbolic_oracle_closed_without_o_h7_overclaim",
                "B1 AD-expanded symbolic closure certificate status changed",
            )
            checks.check(
                blocker.get("b1_ad_expanded_symbolic_oracle_closure")
                == b1_ad_expanded_symbolic_oracle_closure.get("ad_expanded_symbolic_oracle_closure")
                is True,
                "B1 AD-expanded symbolic oracle should be closed",
            )
            checks.check(
                blocker.get("b1_ad_expanded_symbolic_oracle_closed_rows")
                == b1_ad_expanded_symbolic_oracle_closure.get("ad_expanded_symbolic_oracle_closed_rows")
                == 36,
                "B1 AD-expanded symbolic closed rows changed",
            )
            checks.check(
                blocker.get("b1_ad_expanded_symbolic_oracle_columns_per_row")
                == b1_ad_expanded_symbolic_oracle_closure.get("columns_per_row")
                == 132,
                "B1 AD-expanded symbolic column count changed",
            )
            checks.check(
                blocker.get("b1_ad_expanded_symbolic_oracle_closed_cells")
                == b1_ad_expanded_symbolic_oracle_closure.get("ad_expanded_symbolic_oracle_closed_cells")
                == 4752,
                "B1 AD-expanded symbolic derivative-cell count changed",
            )
            checks.check(
                b1_ad_expanded_symbolic_oracle_closure.get("dynamic_symbolic_oracle_complete") is False,
                "B1 AD-expanded certificate must not overclaim global dynamic symbolic oracle",
            )
            checks.check(
                b1_ad_expanded_symbolic_oracle_closure.get(
                    "stage_residual_O_h7_symbolic_certificate_proved"
                )
                is False,
                "B1 AD-expanded certificate must not overclaim symbolic-certificate O(h^7) proof",
            )
            contract_summary = newton_euler_dynamic_contract.get("summary", {})
            readiness_summary = d5_dynamic_readiness.get("summary", {})
            checks.check(
                blocker.get("newton_euler_dynamic_row_closure_contract")
                == "NEWTON_EULER_DYNAMIC_ROW_CLOSURE_CONTRACT.md",
                "B1 dynamic-row closure contract path missing",
            )
            checks.check(
                blocker.get("newton_euler_dynamic_row_closure_contract_json")
                == "NEWTON_EULER_DYNAMIC_ROW_CLOSURE_CONTRACT.json",
                "B1 dynamic-row closure contract JSON path missing",
            )
            checks.check(
                blocker.get("newton_euler_dynamic_row_closure_contract_status")
                == newton_euler_dynamic_contract.get("status")
                == "direct_substitution_contract_closed_primitive_taylor_route_open",
                "B1 dynamic-row closure contract status changed",
            )
            checks.check(
                blocker.get("newton_euler_dynamic_row_closure_contract_traceability_rows")
                == contract_summary.get("rows_with_full_runtime_traceability")
                == 36,
                "B1 dynamic-row closure contract traceability rows changed",
            )
            checks.check(
                blocker.get("newton_euler_dynamic_row_closure_contract_theorem_closed_rows")
                == contract_summary.get("rows_with_direct_pc2_input_closure")
                == 36,
                "B1 dynamic-row closure contract theorem rows changed",
            )
            checks.check(
                blocker.get("newton_euler_dynamic_row_closure_contract_open_rows")
                == contract_summary.get("open_row_count")
                == 0,
                "B1 dynamic-row closure contract open rows changed",
            )
            checks.check(
                blocker.get("newton_euler_dynamic_row_closure_contract_pc_open")
                == contract_summary.get("unsatisfied_close_requirements")
                == [],
                "B1 dynamic-row closure contract open PCs changed",
            )
            checks.check(
                blocker.get("newton_euler_d5_readiness") == "D5_DYNAMIC_DEFECT_READINESS_AUDIT.md",
                "B1 D5 readiness path missing",
            )
            checks.check(
                blocker.get("newton_euler_d5_readiness_json") == "D5_DYNAMIC_DEFECT_READINESS_AUDIT.json",
                "B1 D5 readiness JSON path missing",
            )
            checks.check(
                blocker.get("newton_euler_d5_readiness_pc2_closed")
                == d5_dynamic_readiness.get("pc2_closed")
                is True,
                "B1 D5 readiness direct PC2 closure marker changed",
            )
            checks.check(
                blocker.get("newton_euler_d5_readiness_open_lifted_stage_terms")
                == readiness_summary.get("open_lifted_stage_terms")
                == 0,
                "B1 D5 readiness open lifted-stage terms changed",
            )
            checks.check(
                blocker.get("newton_euler_d5_readiness_theorem_certified_rows")
                == readiness_summary.get("theorem_certified_rows")
                == 36,
                "B1 D5 readiness direct-route certified rows changed",
            )
            checks.check(
                blocker.get("newton_euler_d5_direct_substitution_dynamic_zero_rows")
                == readiness_summary.get("direct_substitution_dynamic_zero_rows")
                == 36,
                "B1 D5 direct-substitution zero rows changed",
            )
            checks.check(
                blocker.get("newton_euler_d5_direct_substitution_primitive_taylor_route_closed") is False
                and readiness_summary.get("primitive_taylor_closed_rows") == 0,
                "B1 D5 primitive/Taylor route unexpectedly closed",
            )
            checks.check(
                "newton_euler_symbolic_target_audit_added" in blocker.get("partial_progress", []),
                "B1 missing Newton-Euler symbolic target audit progress marker",
            )
            checks.check(
                "newton_euler_symbolic_target_inventory_36_rows" in blocker.get("partial_progress", []),
                "B1 missing Newton-Euler symbolic target inventory progress marker",
            )
            checks.check(
                "newton_euler_dynamic_row_direct_substitution_contract_closed"
                in blocker.get("partial_progress", []),
                "B1 missing dynamic-row direct contract progress marker",
            )
            checks.check(
                "newton_euler_d5_readiness_direct_route_pc2_closed" in blocker.get("partial_progress", []),
                "B1 missing D5 readiness direct route progress marker",
            )
            checks.check(
                "NEWTON_EULER_SYMBOLIC_TARGET_AUDIT.md" in blocker.get("partial_progress_evidence", []),
                "B1 Newton-Euler symbolic target audit evidence missing",
            )
            checks.check(
                "NEWTON_EULER_SYMBOLIC_TARGET_AUDIT.json" in blocker.get("partial_progress_evidence", []),
                "B1 Newton-Euler symbolic target audit JSON evidence missing",
            )
            checks.check(
                "validate_newton_euler_symbolic_target_audit.py" in blocker.get("partial_progress_evidence", []),
                "B1 Newton-Euler symbolic target validator evidence missing",
            )
            for evidence, message in [
                ("NEWTON_EULER_DYNAMIC_ROW_CLOSURE_CONTRACT.md", "B1 dynamic-row closure contract evidence missing"),
                ("NEWTON_EULER_DYNAMIC_ROW_CLOSURE_CONTRACT.json", "B1 dynamic-row closure contract JSON evidence missing"),
                ("validate_newton_euler_dynamic_row_closure_contract.py", "B1 dynamic-row closure contract validator evidence missing"),
                ("D5_DYNAMIC_DEFECT_READINESS_AUDIT.md", "B1 D5 readiness evidence missing"),
                ("D5_DYNAMIC_DEFECT_READINESS_AUDIT.json", "B1 D5 readiness JSON evidence missing"),
                ("validate_d5_dynamic_defect_readiness_audit.py", "B1 D5 readiness validator evidence missing"),
            ]:
                checks.check(evidence in blocker.get("partial_progress_evidence", []), message)
            checks.check(
                blocker.get("full_formula_row_oracle") == "DYNAMIC_ROW_ORACLE_GATE.md",
                "B1 full formula-row oracle path missing",
            )
            checks.check(
                blocker.get("full_formula_row_oracle_status")
                == "132_runtime_formula_rows_passable_not_symbolic_defect_proof",
                "B1 full formula-row oracle status changed",
            )
            checks.check(blocker.get("full_formula_row_count") == 132, "B1 full formula-row count changed")
            checks.check(
                blocker.get("full_formula_added_row_family") == "newton_euler_weak_balance",
                "B1 full formula-row added family changed",
            )
            checks.check(
                "full_independent_formula_row_oracle_132_rows" in blocker.get("partial_progress", []),
                "B1 lost full formula-row progress marker",
            )
            checks.check(
                blocker.get("formula_row_ad_jacobian_oracle") == "DYNAMIC_ROW_ORACLE_GATE.md",
                "B1 formula-row AD Jacobian oracle path missing",
            )
            checks.check(
                blocker.get("formula_row_ad_jacobian_oracle_status")
                == "132x132_formula_jacfwd_matches_R_JAC_on_deterministic_probe_not_symbolic_defect_proof",
                "B1 formula-row AD Jacobian oracle status changed",
            )
            checks.check(
                blocker.get("formula_row_ad_jacobian_shape") == [132, 132],
                "B1 formula-row AD Jacobian shape changed",
            )
            checks.check(
                blocker.get("formula_row_ad_jacobian_probe_count") == 3,
                "B1 formula-row AD Jacobian probe count changed",
            )
            checks.check(
                float(blocker.get("formula_row_ad_jacobian_max_mismatch", 1.0)) <= 1.0e-12,
                "B1 formula-row AD Jacobian mismatch too large",
            )
            checks.check(
                "formula_row_ad_jacobian_oracle_132x132" in blocker.get("partial_progress", []),
                "B1 lost formula-row AD Jacobian progress marker",
            )
            checks.check(
                "multi_probe_formula_row_ad_jacobian_oracle_3_probes" in blocker.get("partial_progress", []),
                "B1 lost multi-probe formula-row AD Jacobian progress marker",
            )
            checks.check(
                blocker.get("newton_euler_ad_expanded_row_oracle_audit")
                == "NEWTON_EULER_AD_EXPANDED_ROW_ORACLE_AUDIT.md",
                "B1 AD-expanded row oracle audit path missing",
            )
            checks.check(
                blocker.get("newton_euler_ad_expanded_row_oracle_audit_json")
                == "NEWTON_EULER_AD_EXPANDED_ROW_ORACLE_AUDIT.json",
                "B1 AD-expanded row oracle audit JSON path missing",
            )
            checks.check(
                blocker.get("newton_euler_ad_expanded_row_oracle_status")
                == newton_euler_ad_expanded_row_oracle.get("status")
                == "ad_expanded_runtime_formula_binding_complete_symbolic_oracle_open",
                "B1 AD-expanded row oracle status changed",
            )
            checks.check(
                blocker.get("newton_euler_ad_expanded_row_oracle_closed")
                == newton_euler_ad_expanded_row_oracle.get("ad_expanded_row_oracle_closed")
                is True,
                "B1 AD-expanded row oracle closure marker changed",
            )
            checks.check(
                blocker.get("newton_euler_ad_expanded_row_oracle_rows")
                == newton_euler_ad_expanded_row_oracle.get("ad_expanded_row_oracle_rows")
                == 36,
                "B1 AD-expanded row oracle row count changed",
            )
            checks.check(
                blocker.get("newton_euler_ad_expanded_row_oracle_columns_per_row")
                == newton_euler_ad_expanded_row_oracle.get("ad_expanded_row_oracle_columns_per_row")
                == 132,
                "B1 AD-expanded row oracle column count changed",
            )
            checks.check(
                blocker.get("newton_euler_ad_expanded_row_oracle_probe_count")
                == newton_euler_ad_expanded_row_oracle.get("formula_row_ad_jacobian_probe_count")
                == 3,
                "B1 AD-expanded row oracle probe count changed",
            )
            checks.check(
                float(blocker.get("newton_euler_ad_expanded_row_oracle_max_mismatch", 1.0)) <= 1.0e-12
                and float(newton_euler_ad_expanded_row_oracle.get("formula_row_ad_jacobian_max_mismatch", 1.0))
                <= 1.0e-12,
                "B1 AD-expanded row oracle mismatch too large",
            )
            checks.check(
                blocker.get("newton_euler_ad_expanded_symbolic_oracle_closure")
                == b1_ad_expanded_symbolic_oracle_closure.get("ad_expanded_symbolic_oracle_closure")
                is True,
                "B1 AD-expanded symbolic oracle closure should be sourced from B1 closure certificate",
            )
            checks.check(
                blocker.get("newton_euler_ad_expanded_independent_symbolic_row_oracle_closed")
                == b1_symbolic_row_oracle_closure.get(
                    "independent_symbolic_row_by_row_oracle_for_expanded_fullva_rows_closed"
                )
                is True,
                "B1 AD-expanded independent symbolic row oracle should be closed",
            )
            checks.check(
                newton_euler_ad_expanded_row_oracle.get("ad_expanded_symbolic_oracle_closure") is False,
                "runtime AD audit alone should remain finite binding evidence",
            )
            checks.check(
                blocker.get("newton_euler_ad_expanded_dynamic_symbolic_oracle_complete")
                == newton_euler_ad_expanded_row_oracle.get("dynamic_symbolic_oracle_complete")
                is False,
                "B1 AD-expanded dynamic symbolic oracle must remain open",
            )
            checks.check(
                blocker.get("newton_euler_ad_expanded_stage_residual_O_h7_implementation_defect_proved")
                == newton_euler_ad_expanded_row_oracle.get("stage_residual_O_h7_implementation_defect_proved")
                is False,
                "B1 AD-expanded O(h^7) implementation-defect proof must remain open",
            )
            checks.check(
                "newton_euler_ad_expanded_row_oracle_36_rows" in blocker.get("partial_progress", []),
                "B1 missing AD-expanded row oracle progress marker",
            )
            for evidence, message in [
                ("NEWTON_EULER_AD_EXPANDED_ROW_ORACLE_AUDIT.md", "B1 AD-expanded row oracle evidence missing"),
                ("NEWTON_EULER_AD_EXPANDED_ROW_ORACLE_AUDIT.json", "B1 AD-expanded row oracle JSON evidence missing"),
                (
                    "validate_newton_euler_ad_expanded_row_oracle_audit.py",
                    "B1 AD-expanded row oracle validator evidence missing",
                ),
            ]:
                checks.check(evidence in blocker.get("partial_progress_evidence", []), message)
            checks.check(
                "b1_independent_symbolic_row_oracle_36_rows_closed" in blocker.get("partial_progress", []),
                "B1 missing independent symbolic row-oracle closure progress marker",
            )
            checks.check(
                "b1_ad_expanded_symbolic_oracle_4752_cells_closed" in blocker.get("partial_progress", []),
                "B1 missing AD-expanded symbolic oracle closure progress marker",
            )
            for evidence, message in [
                ("B1_SYMBOLIC_ROW_ORACLE_CLOSURE_CERTIFICATE.md", "B1 symbolic row-oracle closure evidence missing"),
                (
                    "B1_SYMBOLIC_ROW_ORACLE_CLOSURE_CERTIFICATE.json",
                    "B1 symbolic row-oracle closure JSON evidence missing",
                ),
                (
                    "validate_b1_symbolic_row_oracle_closure_certificate.py",
                    "B1 symbolic row-oracle closure validator evidence missing",
                ),
                (
                    "B1_AD_EXPANDED_SYMBOLIC_ORACLE_CLOSURE_CERTIFICATE.md",
                    "B1 AD-expanded symbolic closure evidence missing",
                ),
                (
                    "B1_AD_EXPANDED_SYMBOLIC_ORACLE_CLOSURE_CERTIFICATE.json",
                    "B1 AD-expanded symbolic closure JSON evidence missing",
                ),
                (
                    "validate_b1_ad_expanded_symbolic_oracle_closure_certificate.py",
                    "B1 AD-expanded symbolic closure validator evidence missing",
                ),
            ]:
                checks.check(evidence in blocker.get("partial_progress_evidence", []), message)
            checks.check(
                blocker.get("required_to_close") == [],
                "B1 required-to-close list should be empty after AD-expanded symbolic closure",
            )
            checks.check(
                blocker.get("strict_conditional_residual_bridge_proof_audit") == "CMAME_STRICT_PROOF_AUDIT.md",
                "B1 strict proof audit path missing",
            )
            checks.check(
                blocker.get("strict_conditional_residual_bridge_proof_audit_json") == "CMAME_STRICT_PROOF_AUDIT.json",
                "B1 strict proof audit JSON path missing",
            )
            checks.check(
                blocker.get("strict_conditional_residual_bridge_proof_audited") is True,
                "B1 strict proof audit marker missing",
            )
            checks.check(
                "strict_implementation_proof_complete" not in blocker,
                "B1 strict proof marker must be route-scoped",
            )
            checks.check(
                blocker.get("direct_route_strict_residual_bridge_kantorovich_proof_complete") is True,
                "B1 direct-route strict proof completion marker missing",
            )
            checks.check(
                blocker.get("direct_route_strict_proof_scope")
                == "active_direct_residual_bridge_kantorovich_route_for_B1_B3",
                "B1 direct-route strict proof scope changed",
            )
            checks.check(
                blocker.get("symbolic_primitive_route_strict_implementation_proof_complete") is False,
                "B1 symbolic/primitive implementation lane must remain open",
            )
            checks.check(
                blocker.get("symbolic_primitive_route_scope")
                == "conditional_schema_symbolic_primitive_route_not_active_pc2",
                "B1 symbolic/primitive proof scope changed",
            )
            checks.check(
                blocker.get("two_layer_proof_boundary_consistent") is True,
                "B1 strict proof two-layer boundary marker changed",
            )
            checks.check(
                blocker.get(
                    "b1_ad_expanded_implementation_oracle_still_open_after_strict_proof_audit"
                )
                is False,
                "B1 AD-expanded implementation oracle open marker after strict proof audit should be false",
            )
            checks.check(
                blocker.get(
                    "primitive_global_dynamic_symbolic_oracle_complete_after_strict_proof_audit"
                )
                is False,
                "primitive/global dynamic symbolic oracle should remain explicitly incomplete",
            )
            checks.check(
                blocker.get("strict_primitive_dependency_graph_recorded")
                == strict_primitive.get("dependency_graph_recorded")
                is True,
                "B1 strict primitive dependency graph marker changed",
            )
            checks.check(
                blocker.get("strict_primitive_root_lift_primitives")
                == strict_primitive.get("root_lift_primitives")
                == ["P_state", "P_acc"],
                "B1 strict primitive root list changed",
            )
            checks.check(
                blocker.get("strict_primitive_root_dependent_primitives")
                == strict_primitive.get("root_dependent_primitives")
                == ["P_lambda"],
                "B1 strict primitive root-dependent list changed",
            )
            checks.check(
                blocker.get("strict_primitive_conditional_downstream_primitives")
                == strict_primitive.get("conditional_downstream_primitives")
                == ["P_geom", "P_gyro"],
                "B1 strict primitive downstream list changed",
            )
            checks.check(
                blocker.get("strict_primitive_dependency_edge_count")
                == strict_primitive.get("dependency_edge_count")
                == 5,
                "B1 strict primitive dependency edge count changed",
            )
            checks.check(
                blocker.get("strict_primitive_closure_sequence")
                == strict_primitive.get("closure_sequence")
                == ["P_state", "P_acc", "P_lambda", "P_geom", "P_gyro"],
                "B1 strict primitive closure sequence changed",
            )
            checks.check(
                blocker.get("strict_primitive_root_lift_term_row_total")
                == strict_primitive.get("root_lift_term_row_total")
                == 162,
                "B1 strict primitive root-lift term-row total changed",
            )
            checks.check(
                blocker.get("strict_primitive_root_dependent_term_row_total")
                == strict_primitive.get("root_dependent_term_row_total")
                == 72,
                "B1 strict primitive root-dependent term-row total changed",
            )
            checks.check(
                blocker.get("strict_primitive_conditional_downstream_term_row_total")
                == strict_primitive.get("conditional_downstream_term_row_total")
                == 54,
                "B1 strict primitive downstream term-row total changed",
            )
            checks.check(
                blocker.get("strict_p_state_direct_full_residual_route_certificate")
                == "D5_P_STATE_PS3_FULL_RESIDUAL_ROUTE_CERTIFICATE.md",
                "B1 P_state direct-route certificate path missing",
            )
            checks.check(
                blocker.get("strict_p_state_direct_full_residual_route_certificate_json")
                == "D5_P_STATE_PS3_FULL_RESIDUAL_ROUTE_CERTIFICATE.json",
                "B1 P_state direct-route certificate JSON path missing",
            )
            checks.check(
                blocker.get("strict_p_state_direct_full_residual_route_recorded")
                == strict_direct_corollary.get("certificate_closed")
                is True,
                "B1 P_state direct-route certificate marker changed",
            )
            checks.check(
                blocker.get("strict_p_state_direct_route_ps3_input_closed")
                == strict_direct_corollary.get("direct_route_ps3_input_closed")
                is True,
                "B1 P_state direct-route PS3 input marker changed",
            )
            checks.check(
                blocker.get("strict_p_state_direct_route_state_lift_rate_closed")
                == strict_direct_corollary.get("direct_route_state_lift_rate_closed")
                is True,
                "B1 P_state direct-route state-lift marker changed",
            )
            checks.check(
                blocker.get("strict_p_state_direct_route_h_weighted_acceleration_input_closed")
                == strict_direct_corollary.get("direct_route_h_weighted_acceleration_input_closed")
                is True,
                "B1 P_state direct-route h-acceleration marker changed",
            )
            checks.check(
                blocker.get("strict_p_state_direct_route_proof_steps_closed")
                == strict_direct_corollary.get("strict_proof_steps_closed")
                == 4,
                "B1 P_state direct-route closed proof-step count changed",
            )
            checks.check(
                blocker.get("strict_p_state_direct_route_proof_steps_total")
                == strict_direct_corollary.get("strict_proof_steps_total")
                == 4,
                "B1 P_state direct-route total proof-step count changed",
            )
            checks.check(
                blocker.get("strict_p_state_primitive_route_closed_by_direct_corollary")
                == strict_direct_corollary.get("primitive_route_closed")
                is False,
                "B1 P_state direct-route corollary unexpectedly closes primitive route",
            )
            checks.check(
                blocker.get("strict_p_state_primitive_route_induced_bounds_by_direct_corollary")
                == strict_direct_corollary.get("primitive_route_induced_taylor_bounds_proved")
                == 0,
                "B1 P_state direct-route corollary unexpectedly proves primitive bounds",
            )
            checks.check(
                "strict_conditional_residual_bridge_proof_boundary_audited"
                in blocker.get("partial_progress", []),
                "B1 missing strict proof boundary progress marker",
            )
            checks.check(
                "strict_primitive_dependency_graph_recorded" in blocker.get("partial_progress", []),
                "B1 missing strict primitive dependency graph progress marker",
            )
            checks.check(
                "strict_p_state_direct_full_residual_route_certificate_closed"
                in blocker.get("partial_progress", []),
                "B1 missing P_state direct-route progress marker",
            )
            for evidence, message in [
                ("D5_OPEN_PRIMITIVE_GAP_AUDIT.md", "B1 D5 open primitive gap audit evidence missing"),
                ("D5_OPEN_PRIMITIVE_GAP_AUDIT.json", "B1 D5 open primitive gap JSON evidence missing"),
                ("validate_d5_open_primitive_gap_audit.py", "B1 D5 open primitive gap validator evidence missing"),
                ("D5_P_STATE_PS3_FULL_RESIDUAL_ROUTE_CERTIFICATE.md", "B1 P_state full-route certificate evidence missing"),
                ("D5_P_STATE_PS3_FULL_RESIDUAL_ROUTE_CERTIFICATE.json", "B1 P_state full-route certificate JSON evidence missing"),
                ("validate_d5_p_state_ps3_full_residual_route_certificate.py", "B1 P_state full-route validator evidence missing"),
                ("CMAME_STRICT_PROOF_AUDIT.md", "B1 strict proof audit evidence missing"),
                ("CMAME_STRICT_PROOF_AUDIT.json", "B1 strict proof audit JSON evidence missing"),
                ("validate_cmame_strict_proof_audit.py", "B1 strict proof audit validator evidence missing"),
            ]:
                checks.check(evidence in blocker.get("partial_progress_evidence", []), message)
        if blocker_id == "B3":
            checks.check(
                blocker.get("proof_contract_gate") == "CMAME_PROOF_CONTRACT_GATE.md",
                "B3 proof contract gate path missing",
            )
            checks.check(
                blocker.get("proof_contract_status") == "explicit_conditional_theorem_boundary_recorded",
                "B3 proof contract status changed",
            )
            checks.check(
                "noncircular_proof_contract_decomposition" in blocker.get("partial_progress", []),
                "B3 lost noncircular proof-condition decomposition progress marker",
            )
            checks.check(
                "proof_numerical_scale_audit_added" in blocker.get("partial_progress", []),
                "B3 lost proof numerical scale audit progress marker",
            )
            checks.check(
                "proof_solver_scale_audit_added" in blocker.get("partial_progress", []),
                "B3 lost proof solver-scale audit progress marker",
            )
            checks.check(
                "eta_h_theorem_condition_retained_pc3_satisfied" in blocker.get("partial_progress", []),
                "B3 lost PC3 condition-retention progress marker",
            )
            checks.check(
                "residual_to_error_promotion_avoided_pc4_satisfied" in blocker.get("partial_progress", []),
                "B3 lost PC4 residual-promotion progress marker",
            )
            checks.check(
                "partial_kinematic_stage_defect_certificate_added" in blocker.get("partial_progress", []),
                "B3 lost partial kinematic defect progress marker",
            )
            checks.check(
                "KINEMATIC_ROW_DEFECT_CERTIFICATE.md" in blocker.get("partial_progress_evidence", []),
                "B3 partial kinematic defect evidence missing",
            )
            checks.check(
                "newton_euler_dynamic_defect_obligations_decomposed" in blocker.get("partial_progress", []),
                "B3 lost Newton-Euler dynamic obligation progress marker",
            )
            checks.check(
                "NEWTON_EULER_DEFECT_OBLIGATION_GATE.md" in blocker.get("partial_progress_evidence", []),
                "B3 Newton-Euler obligation evidence missing",
            )
            checks.check(
                "NEWTON_EULER_DEFECT_OBLIGATION_GATE.json" in blocker.get("partial_progress_evidence", []),
                "B3 Newton-Euler obligation JSON evidence missing",
            )
            checks.check(
                "validate_newton_euler_defect_obligation_gate.py" in blocker.get("partial_progress_evidence", []),
                "B3 Newton-Euler obligation validator evidence missing",
            )
            checks.check(
                "newton_euler_symbolic_target_audit_added" in blocker.get("partial_progress", []),
                "B3 lost Newton-Euler symbolic target audit progress marker",
            )
            checks.check(
                "newton_euler_symbolic_target_inventory_36_rows" in blocker.get("partial_progress", []),
                "B3 lost Newton-Euler symbolic target inventory progress marker",
            )
            checks.check(
                "NEWTON_EULER_SYMBOLIC_TARGET_AUDIT.md" in blocker.get("partial_progress_evidence", []),
                "B3 Newton-Euler symbolic target audit evidence missing",
            )
            checks.check(
                "NEWTON_EULER_SYMBOLIC_TARGET_AUDIT.json" in blocker.get("partial_progress_evidence", []),
                "B3 Newton-Euler symbolic target audit JSON evidence missing",
            )
            checks.check(
                "validate_newton_euler_symbolic_target_audit.py" in blocker.get("partial_progress_evidence", []),
                "B3 Newton-Euler symbolic target validator evidence missing",
            )
            checks.check(
                blocker.get("newton_euler_defect_obligation_rows") == 36,
                "B3 Newton-Euler obligation row count changed",
            )
            checks.check(
                blocker.get("newton_euler_defect_open_obligation_count") == 1,
                "B3 Newton-Euler obligation open count changed",
            )
            checks.check(
                blocker.get("newton_euler_defect_open_obligation_scope")
                == "symbolic_primitive_certificate_route_not_active_direct_pc2",
                "B3 Newton-Euler obligation open scope changed",
            )
            checks.check(
                blocker.get("newton_euler_symbolic_primitive_open_obligation_count") == 1,
                "B3 symbolic/primitive Newton-Euler obligation open count changed",
            )
            checks.check(
                blocker.get("newton_euler_symbolic_primitive_open_obligation_scope")
                == "symbolic_primitive_certificate_route_not_active_direct_pc2",
                "B3 symbolic/primitive Newton-Euler obligation open scope changed",
            )
            checks.check(
                blocker.get("active_direct_newton_euler_open_obligation_count") == 0,
                "B3 active direct Newton-Euler obligation open count changed",
            )
            checks.check(
                blocker.get("active_direct_newton_euler_stage_defect_closed") is True,
                "B3 active direct Newton-Euler stage defect closure marker changed",
            )
            checks.check(
                blocker.get("active_direct_newton_euler_zero_residual_rows") == 36,
                "B3 active direct Newton-Euler zero-row count changed",
            )
            checks.check(
                blocker.get("newton_euler_defect_closed_obligation_count") == 5,
                "B3 Newton-Euler closed obligation count changed",
            )
            checks.check(
                blocker.get("newton_euler_symbolic_target_audit") == "NEWTON_EULER_SYMBOLIC_TARGET_AUDIT.md",
                "B3 Newton-Euler symbolic target audit path missing",
            )
            checks.check(
                blocker.get("newton_euler_symbolic_target_audit_json") == "NEWTON_EULER_SYMBOLIC_TARGET_AUDIT.json",
                "B3 Newton-Euler symbolic target audit JSON path missing",
            )
            checks.check(
                blocker.get("newton_euler_symbolic_target_status")
                == "row_level_symbolic_targets_extracted_dynamic_defect_proof_open",
                "B3 Newton-Euler symbolic target audit status changed",
            )
            checks.check(
                blocker.get("newton_euler_symbolic_target_rows") == 36,
                "B3 Newton-Euler symbolic target row count changed",
            )
            checks.check(
                blocker.get("newton_euler_symbolic_target_translational_rows") == 18,
                "B3 Newton-Euler translational target row count changed",
            )
            checks.check(
                blocker.get("newton_euler_symbolic_target_rotational_rows") == 18,
                "B3 Newton-Euler rotational target row count changed",
            )
            checks.check(
                blocker.get("newton_euler_symbolic_target_inventory_complete") is True,
                "B3 Newton-Euler symbolic target inventory marker changed",
            )
            checks.check(
                blocker.get("newton_euler_symbolic_defect_certificate_complete") is False,
                "B3 overclaims Newton-Euler symbolic defect certificate",
            )
            checks.check(
                "PROOF_SOLVER_SCALE_AUDIT.md" in blocker.get("partial_progress_evidence", []),
                "B3 proof solver-scale audit evidence missing",
            )
            checks.check(
                "PROOF_SOLVER_SCALE_AUDIT.json" in blocker.get("partial_progress_evidence", []),
                "B3 proof solver-scale audit JSON evidence missing",
            )
            checks.check(
                "validate_proof_solver_scale_audit.py" in blocker.get("partial_progress_evidence", []),
                "B3 proof solver-scale audit validator missing",
            )
            checks.check(
                "PROOF_CLOSURE_MANIFEST.md" in blocker.get("partial_progress_evidence", []),
                "B3 proof-closure manifest evidence missing",
            )
            checks.check(
                "PROOF_CLOSURE_MANIFEST.json" in blocker.get("partial_progress_evidence", []),
                "B3 proof-closure manifest JSON evidence missing",
            )
            checks.check(
                "validate_proof_closure_manifest.py" in blocker.get("partial_progress_evidence", []),
                "B3 proof-closure validator missing",
            )
            checks.check(
                blocker.get("finite_run_error_scale_supports_order_six") is True,
                "B3 lost finite-run order-six scale marker",
            )
            checks.check(
                blocker.get("summary_level_solver_residuals_recorded") is True,
                "B3 lost summary residual marker",
            )
            checks.check(
                "finite_scaled_tolerance_probe_added" in blocker.get("partial_progress", []),
                "B3 lost finite scaled-tolerance probe progress marker",
            )
            checks.check(
                "PROOF_SOLVER_SCALED_TOLERANCE_PROBE.md" in blocker.get("partial_progress_evidence", []),
                "B3 finite scaled-tolerance probe MD evidence missing",
            )
            checks.check(
                "PROOF_SOLVER_SCALED_TOLERANCE_PROBE.json" in blocker.get("partial_progress_evidence", []),
                "B3 finite scaled-tolerance probe JSON evidence missing",
            )
            checks.check(
                "validate_proof_solver_scaled_tolerance_probe.py" in blocker.get("partial_progress_evidence", []),
                "B3 finite scaled-tolerance probe validator missing",
            )
            checks.check(
                blocker.get("finite_scaled_tolerance_probe_recorded") is True,
                "B3 finite scaled-tolerance probe marker missing",
            )
            checks.check(blocker.get("finite_scaled_tolerance_probe_ok_rows") == 4, "B3 finite probe ok rows changed")
            checks.check(blocker.get("finite_scaled_tolerance_probe_total_rows") == 4, "B3 finite probe total rows changed")
            checks.check(
                float(blocker.get("finite_scaled_tolerance_probe_max_residual_over_h7", float("inf"))) < 1.0e4,
                "B3 finite probe eta-h ratio exceeds c_eta",
            )
            checks.check(
                blocker.get("scaled_tolerance_sweep_recorded") is False,
                "B3 overclaims scaled tolerance sweep",
            )
            checks.check(
                blocker.get("eta_h_O_h7_solver_policy_evidence") is False,
                "B3 overclaims eta_h solver-policy closure",
            )
            checks.check(
                blocker.get("eta_h_theorem_condition_retained") is True,
                "B3 lost eta_h theorem condition-retained marker",
            )
            checks.check(
                blocker.get("residual_to_error_promotion_avoided") is True,
                "B3 lost residual-to-error promotion avoidance marker",
            )
            checks.check(
                "d5_dynamic_direct_substitution_certificate_closed" in blocker.get("partial_progress", []),
                "B3 direct-substitution certificate progress missing",
            )
            checks.check(
                "D5_DYNAMIC_DIRECT_SUBSTITUTION_CERTIFICATE.md" in blocker.get("partial_progress_evidence", []),
                "B3 direct-substitution certificate evidence missing",
            )
            checks.check(
                blocker.get("proof_close_requirements_satisfied") == 4,
                "B3 satisfied close requirement count changed",
            )
            checks.check(
                blocker.get("proof_close_requirements_unsatisfied") == 0,
                "B3 unsatisfied close requirement count changed",
            )
            checks.check(
                blocker.get("pc2_satisfaction_mode")
                == "D5 same-branch residual-value certificate: 96-row O(h^7) non-dynamic certificate plus 36 dynamic zero rows at Z_G",
                "B3 PC2 satisfaction mode changed",
            )
            checks.check(
                blocker.get("pc3_satisfaction_mode")
                == "explicit_theorem_condition_retained_not_empirical_solver_evidence",
                "B3 PC3 satisfaction mode changed",
            )
            checks.check(
                blocker.get("pc4_satisfaction_mode")
                == "nonpromotion_boundary_retained_residual_to_error_theorem_open",
                "B3 PC4 nonpromotion mode changed",
            )
            checks.check(blocker.get("status") == "closed", "B3 should be closed under direct residual-bridge/Kantorovich standard")
            checks.check(
                blocker.get("required_to_close") == [],
                "B3 should have no remaining close requirements",
            )
            checks.check(
                blocker.get("diagnostic_primitive_taylor_route_open_items")
                == [
                    "prove_five_open_primitive_taylor_lift_obligations",
                    "certify_all_162_D5_Taylor_subterms",
                    "close_primitive_taylor_PC2_route",
                ],
                "B3 diagnostic primitive route open items changed",
            )
            checks.check(
                blocker.get("b3_can_close_from_proof_review") is True,
                "B3 direct-proof review should close direct residual-bridge route",
            )
            checks.check(
                blocker.get("b3_direct_proof_review_counts_as_residual_bridge_closure") is True,
                "B3 direct-proof review closure marker missing",
            )
            checks.check(
                blocker.get("direct_residual_bridge_submission_standard_status")
                == "closed_by_direct_residual_bridge_kantorovich_route_primitive_taylor_conditional_schema_open",
                "B3 active residual-bridge proof status changed",
            )
            checks.check(
                blocker.get("direct_residual_bridge_submission_standard_satisfied") is True,
                "B3 active direct residual-bridge proof contract not satisfied",
            )
            checks.check(
                blocker.get("direct_residual_bridge_required_pc2_route") == "direct_residual_bridge_kantorovich_route"
                and blocker.get("direct_residual_bridge_kantorovich_route_closed") is True,
                "B3 active residual-bridge PC2 route changed",
            )
            checks.check(
                blocker.get("primitive_taylor_route_required_for_b3_closure") is False,
                "B3 primitive route should not be required for closure",
            )
            checks.check(blocker.get("primitive_taylor_actual_bounds_proved") == 0, "B3 Taylor actual bounds changed")
            checks.check(blocker.get("primitive_taylor_open_bound_terms") == 162, "B3 Taylor open terms changed")
            checks.check(blocker.get("primitive_taylor_open_primitive_count") == 5, "B3 open primitive count changed")
        if blocker_id == "B2":
            checks.check(
                blocker.get("external_baseline_gate") == "CMAME_EXTERNAL_BASELINE_GATE.md",
                "B2 external baseline gate path missing",
            )
            checks.check(
                blocker.get("external_baseline_status") == "same_test_campaign_not_run_no_external_superiority_claim",
                "B2 external baseline status changed",
            )
            checks.check(
                "external_baseline_gate_added" in blocker.get("partial_progress", []),
                "B2 lost external baseline gate progress marker",
            )
            checks.check(
                "external_suite_claim_boundary_table_reader_facing" in blocker.get("partial_progress", []),
                "B2 lost reader-facing external-suite claim-boundary progress marker",
            )
            checks.check(
                "cross_paper_case_inventory_partial_evidence_overlay_added" in blocker.get("partial_progress", []),
                "B2 lost partial-evidence overlay progress marker",
            )
            checks.check(
                "external_same_test_run_queue_added" in blocker.get("partial_progress", []),
                "B2 lost external same-test run queue progress marker",
            )
            checks.check(
                "external_same_test_acceptance_sheet_added" in blocker.get("partial_progress", []),
                "B2 lost external same-test acceptance sheet progress marker",
            )
            checks.check(
                "comparison_objective_closure_reconciliation_added" in blocker.get("partial_progress", []),
                "B2 lost all-example comparison reconciliation progress marker",
            )
            checks.check(
                "source_policy_closure_triage_added" in blocker.get("partial_progress", []),
                "B2 lost source-policy closure triage progress marker",
            )
            checks.check(
                "all_examples_source_policy_audit_added" in blocker.get("partial_progress", []),
                "B2 lost all-example source-policy audit progress marker",
            )
            checks.check(
                "all_method_example_claim_disposition_audit_added" in blocker.get("partial_progress", []),
                "B2 lost all-method claim-disposition audit progress marker",
            )
            checks.check(
                "external_case_evidence_reconciliation_added" in blocker.get("partial_progress", []),
                "B2 lost external case/evidence reconciliation progress marker",
            )
            checks.check(
                "hi2022_policy_decision_audit_added" in blocker.get("partial_progress", []),
                "B2 lost HI2022 policy-decision audit progress marker",
            )
            checks.check(
                "hi2022_source_policy_row_audit_added" in blocker.get("partial_progress", []),
                "B2 lost HI2022 source-policy row audit progress marker",
            )
            checks.check(
                "vp2024_explicit_source_policy_demotion_recorded" in blocker.get("partial_progress", []),
                "B2 lost VP2024 demotion progress marker",
            )
            checks.check(
                "tfe_source_policy_spec_extracted" in blocker.get("partial_progress", []),
                "B2 lost TFE source-policy spec progress marker",
            )
            checks.check(
                "tfe_source_policy_row_audit_added" in blocker.get("partial_progress", []),
                "B2 lost TFE source-policy row audit progress marker",
            )
            checks.check(
                blocker.get("comparison_matrix_component_status") == "common_reference_order_error_closed",
                "B2 comparison-matrix component status changed",
            )
            checks.check(blocker.get("comparison_matrix_closed") is True, "B2 lost comparison matrix closure")
            checks.check(blocker.get("common_reference_claim_allowed") is True, "B2 common-reference claim boundary changed")
            checks.check(
                blocker.get("source_policy_superiority_claim_allowed") is False,
                "B2 overclaims source-policy superiority",
            )
            checks.check(blocker.get("direct_nonlocal_velocity_order_wins") == 40, "B2 order wins changed")
            checks.check(blocker.get("direct_nonlocal_velocity_order_comparisons") == 40, "B2 order comparisons changed")
            checks.check(blocker.get("direct_nonlocal_finest_velocity_error_wins") == 40, "B2 error wins changed")
            checks.check(blocker.get("direct_nonlocal_finest_velocity_error_comparisons") == 40, "B2 error comparisons changed")
            checks.check(blocker.get("source_policy_reproduction_open") is True, "B2 source-policy boundary changed")
            checks.check(blocker.get("source_policy_flagged_rows") == 15, "B2 source-policy flagged rows changed")
            checks.check(blocker.get("source_policy_velocity_mismatch_rows") == 10, "B2 velocity mismatch rows changed")
            checks.check(
                blocker.get("all_examples_source_policy_audit_status") == all_source_policy.get("status"),
                "B2 all-example source-policy status changed",
            )
            checks.check(
                blocker.get("all_examples_source_policy_flagged_rows")
                == all_source_policy.get("coverage", {}).get("flagged_row_count")
                == 15,
                "B2 all-example source-policy flagged rows changed",
            )
            checks.check(
                blocker.get("all_examples_source_policy_flagged_raw_rows")
                == all_source_policy.get("coverage", {}).get("flagged_raw_row_count")
                == 45,
                "B2 all-example source-policy raw rows changed",
            )
            checks.check(blocker.get("all_examples_source_policy_all_four_examples") is True, "B2 all-example source-policy examples changed")
            checks.check(blocker.get("all_examples_source_policy_all_three_step_sizes") is True, "B2 all-example source-policy step sizes changed")
            checks.check(
                blocker.get("hi2022_policy_decision_audit") == "HI2022_POLICY_DECISION_AUDIT.md",
                "B2 missing HI2022 policy-decision audit path",
            )
            checks.check(
                blocker.get("hi2022_policy_decision_audit_json") == "HI2022_POLICY_DECISION_AUDIT.json",
                "B2 missing HI2022 policy-decision audit JSON path",
            )
            checks.check(
                blocker.get("hi2022_policy_decision_status")
                == hi2022_policy_decision.get("status")
                == "bounded_T0p1_rows_complete_full_T8_source_policy_open",
                "B2 HI2022 policy-decision status changed",
            )
            checks.check(
                blocker.get("hi2022_bounded_rows") == hi2022_bounded.get("row_count") == 24,
                "B2 HI2022 bounded row count changed",
            )
            checks.check(
                blocker.get("hi2022_bounded_ok_rows") == hi2022_bounded.get("ok_row_count") == 24,
                "B2 HI2022 bounded ok row count changed",
            )
            checks.check(
                blocker.get("hi2022_bounded_groups") == hi2022_bounded.get("group_count") == 8,
                "B2 HI2022 bounded group count changed",
            )
            checks.check(
                blocker.get("hi2022_bounded_groups_with_three_step_sizes")
                == hi2022_bounded.get("groups_with_three_step_sizes")
                == 8,
                "B2 HI2022 bounded three-step group count changed",
            )
            checks.check(
                blocker.get("hi2022_full_T8_policy_completed")
                == hi2022_source_policy.get("full_T8_policy_completed")
                is False,
                "B2 HI2022 full T=8 policy boundary changed",
            )
            checks.check(
                blocker.get("hi2022_accepted_for_external_superiority")
                == hi2022_source_policy.get("accepted_for_external_superiority")
                is False,
                "B2 HI2022 external-superiority boundary changed",
            )
            checks.check(
                blocker.get("hi2022_accepted_source_policy_dynamic_order_examples")
                == hi2022_source_policy.get("accepted_source_policy_dynamic_order_examples_count")
                == 0,
                "B2 HI2022 source-policy dynamic-order count changed",
            )
            checks.check(
                blocker.get("hi2022_source_policy_row_audit") == "HI2022_SOURCE_POLICY_ROW_AUDIT.md",
                "B2 missing HI2022 source-policy row audit path",
            )
            checks.check(
                blocker.get("hi2022_source_policy_row_audit_json") == "HI2022_SOURCE_POLICY_ROW_AUDIT.json",
                "B2 missing HI2022 source-policy row audit JSON path",
            )
            checks.check(
                blocker.get("hi2022_source_policy_row_audit_status") == hi2022_source_policy_audit.get("status"),
                "B2 HI2022 source-policy row audit status changed",
            )
            checks.check(
                blocker.get("hi2022_active_b2_flagged_rows")
                == hi2022_source_policy_audit.get("active_b2_flagged_rows")
                == 3,
                "B2 HI2022 active flagged rows changed",
            )
            checks.check(
                blocker.get("hi2022_source_policy_reproduction_rows")
                == hi2022_source_policy_audit.get("source_policy_closed_rows")
                == 0,
                "B2 HI2022 source-policy reproduction rows changed",
            )
            checks.check(
                blocker.get("hi2022_can_close_b2_requirement_now")
                == hi2022_source_policy_audit.get("decision", {}).get("can_close_hi2022_b2_requirement_now")
                is False,
                "B2 HI2022 requirement unexpectedly closed",
            )
            checks.check(
                blocker.get("tfe_source_policy_row_audit") == "TFE_SOURCE_POLICY_ROW_AUDIT.md",
                "B2 missing TFE source-policy row audit path",
            )
            checks.check(
                blocker.get("tfe_source_policy_row_audit_json") == "TFE_SOURCE_POLICY_ROW_AUDIT.json",
                "B2 missing TFE source-policy row audit JSON path",
            )
            checks.check(
                blocker.get("tfe_source_policy_row_audit_status") == tfe_source_policy_audit.get("status"),
                "B2 TFE source-policy row audit status changed",
            )
            checks.check(
                blocker.get("tfe_active_b2_flagged_rows")
                == tfe_source_policy_audit.get("active_b2_flagged_rows")
                == 0,
                "B2 TFE active flagged rows changed",
            )
            checks.check(
                blocker.get("tfe_source_policy_spec_extracted") is True,
                "B2 TFE spec extraction marker changed",
            )
            checks.check(
                blocker.get("tfe_pendulum_dae_runner_implemented") is False,
                "B2 TFE pendulum runner unexpectedly implemented",
            )
            checks.check(
                blocker.get("tfe_source_policy_reproduction_rows")
                == tfe_source_policy_audit.get("source_policy_closed_rows")
                == 0,
                "B2 TFE source-policy reproduction rows changed",
            )
            checks.check(
                blocker.get("tfe_can_close_b2_requirement_now")
                == tfe_source_policy_audit.get("decision", {}).get("can_close_tfe_b2_requirement_now")
                is False,
                "B2 TFE requirement unexpectedly closed",
            )
            checks.check(
                blocker.get("hi2022_default_1e-4_required") is False,
                "B2 HI2022 incorrectly requires default 1e-4",
            )
            checks.check(blocker.get("hi2022_run_v047_invoked") is False, "B2 HI2022 audit invoked run_v047")
            checks.check(blocker.get("vp2024_source_policy_demoted") is True, "B2 VP2024 demotion marker missing")
            checks.check(
                blocker.get("vp2024_source_policy_demotion_ledger") == "EXTERNAL_SUITE_DEMOTION_LEDGER.md",
                "B2 missing VP2024 demotion ledger path",
            )
            checks.check(
                blocker.get("vp2024_source_policy_demotion_ledger_json") == "EXTERNAL_SUITE_DEMOTION_LEDGER.json",
                "B2 missing VP2024 demotion ledger JSON path",
            )
            checks.check(
                blocker.get("vp2024_demoted_source_policy_rows")
                == external_suite_demotion.get("vp2024_demoted_source_policy_rows")
                == 4,
                "B2 VP2024 demoted row count changed",
            )
            checks.check(
                blocker.get("vp2024_demoted_source_policy_flagged_rows")
                == external_suite_demotion.get("vp2024_demoted_source_policy_flagged_rows")
                == 3,
                "B2 VP2024 demoted flagged-row count changed",
            )
            checks.check(blocker.get("hi2022_source_policy_demoted") is True, "B2 HI2022 demotion marker missing")
            checks.check(
                blocker.get("hi2022_demoted_source_policy_rows")
                == external_suite_demotion.get("hi2022_demoted_source_policy_rows")
                == 3,
                "B2 HI2022 demoted row count changed",
            )
            checks.check(
                blocker.get("hi2022_demoted_source_policy_flagged_rows")
                == external_suite_demotion.get("hi2022_demoted_source_policy_flagged_rows")
                == 3,
                "B2 HI2022 demoted flagged-row count changed",
            )
            checks.check(blocker.get("ra2021_source_policy_demoted") is True, "B2 RA2021 demotion marker missing")
            checks.check(blocker.get("tfe_source_policy_demoted") is True, "B2 TFE demotion marker missing")
            checks.check(
                blocker.get("ra2021_demoted_source_policy_rows") == 5
                and blocker.get("ra2021_demoted_source_policy_flagged_rows") == 5,
                "B2 RA2021 demotion counts changed",
            )
            checks.check(
                blocker.get("tfe_demoted_source_policy_rows") == 4
                and blocker.get("tfe_demoted_source_policy_flagged_rows") == 4,
                "B2 TFE demotion counts changed",
            )
            checks.check(
                blocker.get("active_source_policy_flagged_rows_after_demotions")
                == external_suite_demotion.get("active_source_policy_flagged_rows_after_demotions")
                == 0,
                "B2 active source-policy flagged rows after demotion changed",
            )
            checks.check(
                "b2_source_policy_remaining_work_manifest_added" in blocker.get("partial_progress", []),
                "B2 lost remaining-work manifest progress marker",
            )
            checks.check(
                blocker.get("b2_source_policy_remaining_work_manifest")
                == "B2_SOURCE_POLICY_REMAINING_WORK_MANIFEST.md",
                "B2 missing remaining-work manifest path",
            )
            checks.check(
                blocker.get("b2_source_policy_remaining_work_manifest_json")
                == "B2_SOURCE_POLICY_REMAINING_WORK_MANIFEST.json",
                "B2 missing remaining-work manifest JSON path",
            )
            checks.check(
                blocker.get("b2_remaining_work_manifest_status") == b2_remaining_work.get("status"),
                "B2 remaining-work manifest status not carried into blocker",
            )
            checks.check(
                blocker.get("b2_remaining_active_flagged_rows")
                == b2_remaining_work.get("active_flagged_row_count")
                == 0,
                "B2 remaining active flagged rows changed",
            )
            checks.check(
                blocker.get("b2_remaining_demoted_flagged_rows")
                == b2_remaining_work.get("demoted_flagged_row_count")
                == 15,
                "B2 remaining demoted flagged rows changed",
            )
            checks.check(
                blocker.get("b2_remaining_source_policy_closed_rows")
                == b2_remaining_work.get("source_policy_closed_rows")
                == 0,
                "B2 remaining source-policy closed rows changed",
            )
            checks.check(
                blocker.get("b2_remaining_external_superiority_ready_rows")
                == b2_remaining_work.get("external_superiority_ready_rows")
                == 0,
                "B2 remaining external-superiority-ready rows changed",
            )
            checks.check(
                "b2_source_policy_closure_execution_plan_added" in blocker.get("partial_progress", []),
                "B2 lost closure execution plan progress marker",
            )
            checks.check(
                blocker.get("b2_closure_execution_plan_schema")
                == closure_plan.get("schema")
                == "b2-source-policy-closure-execution-plan-v1",
                "B2 closure execution plan schema changed",
            )
            checks.check(
                blocker.get("b2_closure_execution_plan_all_active_suites_ready")
                == closure_plan.get("all_active_suites_ready_to_launch")
                is True,
                "B2 closure plan launch readiness changed",
            )
            checks.check(
                blocker.get("b2_closure_execution_plan_explicit_1e-4_opt_in")
                == closure_plan.get("source_policy_1e_4_requires_explicit_flag")
                is True,
                "B2 closure plan explicit 1e-4 guard changed",
            )
            checks.check(
                blocker.get("b2_closure_execution_plan_external_superiority_after_plan_only")
                == closure_plan.get("external_superiority_claim_allowed_after_plan_only")
                is False,
                "B2 closure plan overclaims plan-only superiority",
            )
            checks.check(
                "ra2021_source_policy_row_audit_added" in blocker.get("partial_progress", []),
                "B2 lost RA2021 source-policy audit progress marker",
            )
            checks.check(
                blocker.get("ra2021_source_policy_row_audit") == "RA2021_SOURCE_POLICY_ROW_AUDIT.md",
                "B2 missing RA2021 source-policy audit path",
            )
            checks.check(
                blocker.get("ra2021_source_policy_row_audit_json") == "RA2021_SOURCE_POLICY_ROW_AUDIT.json",
                "B2 missing RA2021 source-policy audit JSON path",
            )
            checks.check(
                blocker.get("ra2021_source_policy_row_audit_status") == ra2021_source_policy_audit.get("status"),
                "B2 RA2021 source-policy audit status changed",
            )
            checks.check(
                blocker.get("ra2021_active_b2_flagged_rows")
                == ra2021_source_policy_audit.get("active_b2_flagged_rows")
                == 0,
                "B2 RA2021 active flagged rows changed",
            )
            checks.check(
                blocker.get("ra2021_public_order_groups_completed")
                == blocker.get("ra2021_public_order_groups_required")
                == ra2021_source_policy_audit.get("public_order_groups_completed")
                == ra2021_source_policy_audit.get("public_order_groups_required")
                == 12,
                "B2 RA2021 public order groups changed",
            )
            checks.check(
                blocker.get("ra2021_public_timing_rows_completed")
                == blocker.get("ra2021_public_timing_rows_required")
                == ra2021_source_policy_audit.get("public_timing_rows_completed")
                == ra2021_source_policy_audit.get("public_timing_rows_required")
                == 12,
                "B2 RA2021 public timing rows changed",
            )
            checks.check(
                blocker.get("ra2021_source_policy_reproduction_rows")
                == ra2021_source_policy_audit.get("source_policy_reproduction_rows")
                == 0,
                "B2 RA2021 source-policy reproduction rows changed",
            )
            checks.check(
                blocker.get("ra2021_can_close_b2_requirement_now")
                == ra2021_source_policy_audit.get("decision", {}).get("can_close_ra2021_b2_requirement_now")
                is False,
                "B2 RA2021 closure decision changed",
            )
            checks.check(
                blocker.get("closed_subrequirements")
                == [
                    "vp2024_code_resolution_or_demotion",
                    "hi2022_public_code_same_test_rows",
                    "ra2021_public_code_same_test_rows",
                    "original_tfe_pendulum_error_order_work_rows",
                ],
                "B2 closed subrequirements changed",
            )
            checks.check(
                blocker.get("required_to_close") == [],
                "B2 required-to-close list not updated after VP2024 demotion",
            )
            checks.check(
                blocker.get("all_method_claim_disposition_total_cells")
                == all_method_disposition.get("coverage", {}).get("total_cells")
                == 44,
                "B2 all-method total cells changed",
            )
            checks.check(
                blocker.get("all_method_claim_disposition_nonlocal_cells")
                == all_method_disposition.get("coverage", {}).get("nonlocal_cells")
                == 40,
                "B2 all-method nonlocal cells changed",
            )
            checks.check(
                blocker.get("all_method_claim_disposition_source_policy_closed_rows")
                == all_method_disposition.get("claim_boundary", {}).get("nonlocal_source_policy_closed_rows")
                == 0,
                "B2 all-method source-policy closed rows changed",
            )
            checks.check(
                blocker.get("all_method_claim_disposition_source_policy_open_rows")
                == all_method_disposition.get("claim_boundary", {}).get("nonlocal_source_policy_open_rows")
                == 40,
                "B2 all-method source-policy open rows changed",
            )
            checks.check(
                blocker.get("all_method_claim_disposition_strict_external_error_claim_allowed_rows")
                == all_method_disposition.get("claim_boundary", {}).get("strict_external_error_claim_allowed_rows")
                == 0,
                "B2 all-method strict external rows changed",
            )
            checks.check(blocker.get("paper_submission_b2_b4_can_close_now") is False, "B2 incorrectly closes B2/B4")
            checks.check(
                "EXTERNAL_SAME_TEST_RUN_QUEUE.md" in blocker.get("partial_progress_evidence", []),
                "B2 missing run queue MD evidence",
            )
            checks.check(
                "EXTERNAL_SAME_TEST_RUN_QUEUE.json" in blocker.get("partial_progress_evidence", []),
                "B2 missing run queue JSON evidence",
            )
            checks.check(
                "validate_external_same_test_run_queue.py" in blocker.get("partial_progress_evidence", []),
                "B2 missing run queue validator evidence",
            )
            checks.check(
                "EXTERNAL_SAME_TEST_ACCEPTANCE_SHEET.md" in blocker.get("partial_progress_evidence", []),
                "B2 missing acceptance sheet MD evidence",
            )
            checks.check(
                "EXTERNAL_SAME_TEST_ACCEPTANCE_SHEET.json" in blocker.get("partial_progress_evidence", []),
                "B2 missing acceptance sheet JSON evidence",
            )
            checks.check(
                "validate_external_same_test_acceptance_sheet.py" in blocker.get("partial_progress_evidence", []),
                "B2 missing acceptance sheet validator evidence",
            )
            checks.check(
                "COMPARISON_OBJECTIVE_CLOSURE_RECONCILIATION_AUDIT.md" in blocker.get("partial_progress_evidence", []),
                "B2 missing comparison reconciliation evidence",
            )
            checks.check(
                "COMPARISON_OBJECTIVE_CLOSURE_RECONCILIATION_AUDIT.json" in blocker.get("partial_progress_evidence", []),
                "B2 missing comparison reconciliation JSON evidence",
            )
            checks.check(
                "validate_comparison_objective_closure_reconciliation_audit.py" in blocker.get("partial_progress_evidence", []),
                "B2 missing comparison reconciliation validator evidence",
            )
            checks.check(
                "SOURCE_POLICY_CLOSURE_TRIAGE.md" in blocker.get("partial_progress_evidence", []),
                "B2 missing source-policy closure triage evidence",
            )
            checks.check(
                "SOURCE_POLICY_CLOSURE_TRIAGE.json" in blocker.get("partial_progress_evidence", []),
                "B2 missing source-policy closure triage JSON evidence",
            )
            checks.check(
                "validate_source_policy_closure_triage.py" in blocker.get("partial_progress_evidence", []),
                "B2 missing source-policy closure triage validator evidence",
            )
            checks.check(
                "ALL_EXAMPLES_SOURCE_POLICY_AUDIT.md" in blocker.get("partial_progress_evidence", []),
                "B2 missing all-example source-policy audit MD evidence",
            )
            checks.check(
                "ALL_EXAMPLES_SOURCE_POLICY_AUDIT.json" in blocker.get("partial_progress_evidence", []),
                "B2 missing all-example source-policy audit JSON evidence",
            )
            checks.check(
                "validate_all_examples_source_policy_audit.py" in blocker.get("partial_progress_evidence", []),
                "B2 missing all-example source-policy validator evidence",
            )
            checks.check(
                "ALL_METHOD_EXAMPLE_CLAIM_DISPOSITION_AUDIT.md" in blocker.get("partial_progress_evidence", []),
                "B2 missing all-method claim-disposition MD evidence",
            )
            checks.check(
                "ALL_METHOD_EXAMPLE_CLAIM_DISPOSITION_AUDIT.json" in blocker.get("partial_progress_evidence", []),
                "B2 missing all-method claim-disposition JSON evidence",
            )
            checks.check(
                "validate_all_method_example_claim_disposition_audit.py" in blocker.get("partial_progress_evidence", []),
                "B2 missing all-method claim-disposition validator evidence",
            )
            checks.check(
                "EXTERNAL_CASE_EVIDENCE_RECONCILIATION.md" in blocker.get("partial_progress_evidence", []),
                "B2 missing external case reconciliation evidence",
            )
            checks.check(
                "EXTERNAL_CASE_EVIDENCE_RECONCILIATION.json" in blocker.get("partial_progress_evidence", []),
                "B2 missing external case reconciliation JSON evidence",
            )
            checks.check(
                "validate_external_case_evidence_reconciliation.py" in blocker.get("partial_progress_evidence", []),
                "B2 missing external case reconciliation validator evidence",
            )
            checks.check(
                "HI2022_POLICY_DECISION_AUDIT.md" in blocker.get("partial_progress_evidence", []),
                "B2 missing HI2022 policy-decision audit evidence",
            )
            checks.check(
                "HI2022_POLICY_DECISION_AUDIT.json" in blocker.get("partial_progress_evidence", []),
                "B2 missing HI2022 policy-decision audit JSON evidence",
            )
            checks.check(
                "validate_hi2022_policy_decision_audit.py" in blocker.get("partial_progress_evidence", []),
                "B2 missing HI2022 policy-decision validator evidence",
            )
            checks.check(
                "HI2022_SOURCE_POLICY_ROW_AUDIT.md" in blocker.get("partial_progress_evidence", []),
                "B2 missing HI2022 source-policy row audit evidence",
            )
            checks.check(
                "HI2022_SOURCE_POLICY_ROW_AUDIT.json" in blocker.get("partial_progress_evidence", []),
                "B2 missing HI2022 source-policy row audit JSON evidence",
            )
            checks.check(
                "validate_hi2022_source_policy_row_audit.py" in blocker.get("partial_progress_evidence", []),
                "B2 missing HI2022 source-policy row audit validator evidence",
            )
            checks.check(
                "EXTERNAL_SUITE_DEMOTION_LEDGER.md" in blocker.get("partial_progress_evidence", []),
                "B2 missing external suite demotion ledger evidence",
            )
            checks.check(
                "EXTERNAL_SUITE_DEMOTION_LEDGER.json" in blocker.get("partial_progress_evidence", []),
                "B2 missing external suite demotion ledger JSON evidence",
            )
            checks.check(
                "validate_external_suite_demotion_ledger.py" in blocker.get("partial_progress_evidence", []),
                "B2 missing external suite demotion validator evidence",
            )
            checks.check(
                "B2_SOURCE_POLICY_REMAINING_WORK_MANIFEST.md" in blocker.get("partial_progress_evidence", []),
                "B2 missing remaining-work manifest evidence",
            )
            checks.check(
                "B2_SOURCE_POLICY_REMAINING_WORK_MANIFEST.json" in blocker.get("partial_progress_evidence", []),
                "B2 missing remaining-work manifest JSON evidence",
            )
            checks.check(
                "validate_b2_source_policy_remaining_work_manifest.py" in blocker.get("partial_progress_evidence", []),
                "B2 missing remaining-work manifest validator evidence",
            )
            checks.check(
                "RA2021_SOURCE_POLICY_ROW_AUDIT.md" in blocker.get("partial_progress_evidence", []),
                "B2 missing RA2021 source-policy audit evidence",
            )
            checks.check(
                "RA2021_SOURCE_POLICY_ROW_AUDIT.json" in blocker.get("partial_progress_evidence", []),
                "B2 missing RA2021 source-policy audit JSON evidence",
            )
            checks.check(
                "validate_ra2021_source_policy_row_audit.py" in blocker.get("partial_progress_evidence", []),
                "B2 missing RA2021 source-policy audit validator evidence",
            )
            checks.check(
                "TFE_SOURCE_POLICY_SPEC.md" in blocker.get("partial_progress_evidence", []),
                "B2 missing TFE source-policy spec evidence",
            )
            checks.check(
                "TFE_SOURCE_POLICY_SPEC.json" in blocker.get("partial_progress_evidence", []),
                "B2 missing TFE source-policy spec JSON evidence",
            )
            checks.check(
                "validate_tfe_source_policy_spec.py" in blocker.get("partial_progress_evidence", []),
                "B2 missing TFE source-policy spec validator evidence",
            )
            checks.check(
                "TFE_SOURCE_POLICY_ROW_AUDIT.md" in blocker.get("partial_progress_evidence", []),
                "B2 missing TFE source-policy row audit evidence",
            )
            checks.check(
                "TFE_SOURCE_POLICY_ROW_AUDIT.json" in blocker.get("partial_progress_evidence", []),
                "B2 missing TFE source-policy row audit JSON evidence",
            )
            checks.check(
                "validate_tfe_source_policy_row_audit.py" in blocker.get("partial_progress_evidence", []),
                "B2 missing TFE source-policy row audit validator evidence",
            )
            checks.check(
                blocker.get("cross_case_inventory_status") == "spec_extracted_partial_evidence_not_full_campaign",
                "B2 cross-case inventory status changed",
            )
            checks.check(blocker.get("default_1e-4_required") is False, "B2 incorrectly requires default 1e-4")
        if blocker_id == "B4":
            checks.check(
                "superconvergent_order_explanation" in blocker.get("partial_progress", []),
                "B4 lost observed-order interpretation progress marker",
            )
            checks.check(
                "order_acceptance_matrix_added" in blocker.get("partial_progress", []),
                "B4 lost order-acceptance matrix progress marker",
            )
            checks.check(
                "local_closed_loop_dynamic_order_candidate_matrix_added" in blocker.get("partial_progress", []),
                "B4 lost closed-loop coarse-dynamics diagnostic progress marker",
            )
            checks.check(
                "fair_baseline_acceptance_sheet_added" in blocker.get("partial_progress", []),
                "B4 lost fair baseline acceptance sheet progress marker",
            )
            checks.check(
                "common_reference_order_error_matrix_closed" in blocker.get("partial_progress", []),
                "B4 lost all-example common-reference matrix progress marker",
            )
            checks.check(
                "all_method_example_claim_disposition_audit_added" in blocker.get("partial_progress", []),
                "B4 lost all-method claim-disposition audit progress marker",
            )
            checks.check(
                "tfe_algorithm_literal_endpoint_probe_added" in blocker.get("partial_progress", []),
                "B4 lost TFE algorithm-literal endpoint probe progress marker",
            )
            checks.check(
                "tfe_source_grid_exact_T_endpoint_subclosure_added" in blocker.get("partial_progress", []),
                "B4 lost TFE exact-T source-grid endpoint subclosure marker",
            )
            checks.check(
                "tfe_source_pendulum_same_test_work_precision_added" in blocker.get("partial_progress", []),
                "B4 lost TFE source-pendulum same-test work/precision progress marker",
            )
            checks.check(
                "tfe_algorithm_literal_work_precision_audit_added" in blocker.get("partial_progress", []),
                "B4 lost TFE algorithm-literal work/precision progress marker",
            )
            checks.check(
                "b4_post_execution_promotion_contract_added" in blocker.get("partial_progress", []),
                "B4 lost post-execution promotion contract progress marker",
            )
            checks.check(
                "b4_post_execution_audit_recorded" in blocker.get("partial_progress", []),
                "B4 lost post-execution audit progress marker",
            )
            checks.check(
                "narrowed_claim_policy_reclassification_added" in blocker.get("partial_progress", []),
                "B4 lost narrowed-claim reclassification marker",
            )
            b4_promotion_contract = b4_execution_opt_in_packet.get("post_execution_promotion_contract", {})
            b4_post_summary = b4_source_policy_post_execution_audit.get("post_execution_summary", {})
            b4_post_presence = b4_source_policy_post_execution_audit.get("command_artifact_presence", {})
            b4_post_evidence = b4_source_policy_post_execution_audit.get("post_execution_artifact_evidence", {})
            b4_authorized = (
                b4_source_policy_post_execution_audit.get("verified_authorized_execution_recorded") is True
            )
            b4_expected_scope = (
                "verified_authorized_guarded_driver_execution"
                if b4_authorized
                else "no_verified_current_authorized_execution_record_existing_artifacts_only"
            )
            b4_expected_verified_commands = 13 if b4_authorized else 0
            checks.check(
                blocker.get("common_reference_order_error_matrix_closed") is True,
                "B4 common-reference order/error closure marker changed",
            )
            checks.check(blocker.get("comparison_matrix_closed") is True, "B4 lost comparison matrix closure")
            checks.check(blocker.get("common_reference_claim_allowed") is True, "B4 common-reference claim boundary changed")
            checks.check(
                blocker.get("source_policy_superiority_claim_allowed") is False,
                "B4 overclaims source-policy superiority",
            )
            checks.check(blocker.get("direct_nonlocal_velocity_order_wins") == 40, "B4 order wins changed")
            checks.check(blocker.get("direct_nonlocal_velocity_order_comparisons") == 40, "B4 order comparisons changed")
            checks.check(blocker.get("direct_nonlocal_finest_velocity_error_wins") == 40, "B4 error wins changed")
            checks.check(blocker.get("direct_nonlocal_finest_velocity_error_comparisons") == 40, "B4 error comparisons changed")
            checks.check(
                blocker.get("all_method_claim_disposition_total_cells")
                == all_method_disposition.get("coverage", {}).get("total_cells")
                == 44,
                "B4 all-method total cells changed",
            )
            checks.check(
                blocker.get("all_method_claim_disposition_nonlocal_cells")
                == all_method_disposition.get("coverage", {}).get("nonlocal_cells")
                == 40,
                "B4 all-method nonlocal cells changed",
            )
            checks.check(
                blocker.get("all_method_claim_disposition_source_policy_closed_rows")
                == all_method_disposition.get("claim_boundary", {}).get("nonlocal_source_policy_closed_rows")
                == 0,
                "B4 all-method source-policy closed rows changed",
            )
            checks.check(
                blocker.get("all_method_claim_disposition_source_policy_open_rows")
                == all_method_disposition.get("claim_boundary", {}).get("nonlocal_source_policy_open_rows")
                == 40,
                "B4 all-method source-policy open rows changed",
            )
            checks.check(
                blocker.get("tfe_algorithm_literal_endpoint_probe_metric_rows")
                == tfe_algorithm_literal_endpoint_probe.get("metric_row_count")
                == 12,
                "B4 TFE algorithm-literal endpoint metric-row count changed",
            )
            checks.check(
                blocker.get("tfe_algorithm_literal_endpoint_probe_terminal_overrun_rows")
                == tfe_algorithm_literal_endpoint_probe.get("terminal_overrun_rows")
                == 12,
                "B4 TFE algorithm-literal endpoint overrun count changed",
            )
            checks.check(
                blocker.get("tfe_algorithm_literal_endpoint_probe_source_policy_rows_completed")
                == tfe_algorithm_literal_endpoint_probe.get("source_policy_rows_completed")
                == 0,
                "B4 TFE algorithm-literal endpoint overcloses source-policy rows",
            )
            checks.check(
                blocker.get("tfe_algorithm_literal_endpoint_probe_exact_T_error_sampling_equivalent")
                == tfe_algorithm_literal_endpoint_probe.get("source_policy_exact_T_error_sampling_equivalent")
                is False,
                "B4 TFE algorithm-literal endpoint overclaims exact-T sampling equivalence",
            )
            checks.check(
                blocker.get("tfe_source_grid_compatibility_audit")
                == "TFE_SOURCE_GRID_COMPATIBILITY_AUDIT.md",
                "B4 TFE source-grid compatibility audit report path missing",
            )
            checks.check(
                blocker.get("tfe_source_grid_compatibility_audit_json")
                == "TFE_SOURCE_GRID_COMPATIBILITY_AUDIT.json",
                "B4 TFE source-grid compatibility audit JSON path missing",
            )
            checks.check(
                blocker.get("tfe_source_grid_exact_T_compatible_rows_endpoint_convention_resolved")
                == tfe_source_grid_compatibility.get(
                    "endpoint_compatible_rows_source_endpoint_convention_resolved"
                )
                == 2,
                "B4 TFE exact-T source-grid resolved row count changed",
            )
            checks.check(
                blocker.get("tfe_source_grid_endpoint_incompatible_rows_requiring_policy")
                == tfe_source_grid_compatibility.get("endpoint_incompatible_rows_require_source_endpoint_policy")
                == 4,
                "B4 TFE source-grid endpoint-policy-required row count changed",
            )
            checks.check(
                blocker.get("tfe_source_grid_policy_resolved_for_exact_T_compatible_rows")
                == tfe_source_grid_compatibility.get(
                    "source_grid_policy_resolved_for_exact_T_compatible_rows"
                )
                is True,
                "B4 TFE exact-T source-grid subclosure changed",
            )
            checks.check(
                blocker.get("tfe_source_grid_policy_resolved_for_full_T10")
                == tfe_source_grid_compatibility.get("source_grid_policy_resolved_for_full_T10")
                is False,
                "B4 TFE source-grid full T10 policy overclosed",
            )
            checks.check(
                blocker.get("tfe_source_grid_source_policy_rows_completed")
                == tfe_source_grid_compatibility.get("source_policy_rows_completed")
                == 0,
                "B4 TFE source-grid overcloses source-policy rows",
            )
            checks.check(
                blocker.get("tfe_source_grid_endpoint_compatible_row_ids")
                == tfe_source_grid_compatibility.get("source_endpoint_compatible_row_ids")
                == ["frictional_pendulum:h=0.008", "frictional_pendulum:h=0.2"],
                "B4 TFE exact-T source-grid row IDs changed",
            )
            checks.check(
                blocker.get("tfe_source_grid_endpoint_incompatible_row_ids")
                == tfe_source_grid_compatibility.get("source_endpoint_incompatible_row_ids")
                == [
                    "frictionless_pendulum:h=0.003",
                    "frictionless_pendulum:h=0.006",
                    "frictionless_pendulum:h=0.012",
                    "frictional_pendulum:h=0.003",
                ],
                "B4 TFE endpoint-incompatible source-grid row IDs changed",
            )
            checks.check(
                "Exact-T compatible rows with endpoint-grid convention resolved: `2`."
                in tfe_source_grid_compatibility_md,
                "B4 TFE source-grid audit markdown lacks exact-T subclosure marker",
            )
            checks.check(
                contains_normalized(
                    gate_md,
                    "TFE source-grid exact-T endpoint subclosure added with `2` rows resolved",
                ),
                "B4 gate markdown missing TFE exact-T source-grid subclosure summary",
            )
            checks.check(
                blocker.get("tfe_source_pendulum_same_test_work_precision")
                == "../v048_cross_paper_same_test_benchmarks/results/tfe_source_pendulum_same_test_work_precision.md",
                "B4 TFE same-test work/precision report path missing",
            )
            checks.check(
                blocker.get("tfe_source_pendulum_same_test_work_precision_json")
                == "../v048_cross_paper_same_test_benchmarks/results/tfe_source_pendulum_same_test_work_precision.json",
                "B4 TFE same-test work/precision JSON path missing",
            )
            checks.check(
                blocker.get("tfe_source_pendulum_same_test_work_precision_methods")
                == tfe_same_test_work_precision.get("method_count")
                == 6,
                "B4 TFE same-test work/precision method count changed",
            )
            checks.check(
                blocker.get("tfe_source_pendulum_same_test_work_precision_rows")
                == tfe_same_test_work_precision.get("row_count")
                == 18,
                "B4 TFE same-test work/precision row count changed",
            )
            checks.check(
                blocker.get("tfe_source_pendulum_same_test_work_precision_ok_rows")
                == tfe_same_test_work_precision.get("ok_row_count")
                == 18,
                "B4 TFE same-test work/precision ok row count changed",
            )
            checks.check(
                blocker.get("tfe_source_pendulum_same_test_work_precision_summary_rows")
                == tfe_same_test_work_precision.get("summary_row_count")
                == 6,
                "B4 TFE same-test work/precision summary row count changed",
            )
            checks.check(
                blocker.get("tfe_source_pendulum_same_test_work_precision_figure_available")
                == tfe_same_test_work_precision.get("figure_available")
                is True,
                "B4 TFE same-test work/precision figure availability changed",
            )
            checks.check(
                blocker.get("tfe_source_pendulum_same_test_work_precision_source_policy_rows_completed")
                == tfe_same_test_work_precision.get("source_policy_rows_completed")
                == 0,
                "B4 TFE same-test work/precision overcloses source-policy rows",
            )
            checks.check(
                blocker.get("tfe_source_pendulum_same_test_work_precision_external_superiority_allowed")
                == tfe_same_test_work_precision.get("external_superiority_claim_allowed")
                is False,
                "B4 TFE same-test work/precision overclaims external superiority",
            )
            checks.check(
                blocker.get("tfe_algorithm_literal_work_precision_audit")
                == "TFE_ALGORITHM_LITERAL_WORK_PRECISION_AUDIT.md",
                "B4 TFE algorithm-literal work/precision report path missing",
            )
            checks.check(
                blocker.get("tfe_algorithm_literal_work_precision_audit_json")
                == "TFE_ALGORITHM_LITERAL_WORK_PRECISION_AUDIT.json",
                "B4 TFE algorithm-literal work/precision JSON path missing",
            )
            checks.check(
                blocker.get("tfe_algorithm_literal_work_precision_audit_csv")
                == "TFE_ALGORITHM_LITERAL_WORK_PRECISION_AUDIT.csv",
                "B4 TFE algorithm-literal work/precision CSV path missing",
            )
            checks.check(
                blocker.get("tfe_algorithm_literal_work_precision_figure")
                == "figures/tfe_algorithm_literal_work_precision.png",
                "B4 TFE algorithm-literal work/precision figure path missing",
            )
            checks.check(
                blocker.get("tfe_algorithm_literal_work_precision_work_proxy")
                == tfe_algorithm_literal_work_precision.get("work_proxy")
                == "total_newton_iterations",
                "B4 TFE algorithm-literal work/precision work proxy changed",
            )
            checks.check(
                blocker.get("tfe_algorithm_literal_work_precision_runtime_proxy_available")
                == tfe_algorithm_literal_work_precision.get("runtime_proxy_available")
                is False,
                "B4 TFE algorithm-literal work/precision overclaims runtime proxy",
            )
            checks.check(
                blocker.get("tfe_algorithm_literal_work_precision_methods")
                == tfe_algorithm_literal_work_precision.get("method_count")
                == 4,
                "B4 TFE algorithm-literal work/precision method count changed",
            )
            checks.check(
                blocker.get("tfe_algorithm_literal_work_precision_raw_rows")
                == tfe_algorithm_literal_work_precision.get("raw_row_count")
                == 12,
                "B4 TFE algorithm-literal work/precision raw row count changed",
            )
            checks.check(
                blocker.get("tfe_algorithm_literal_work_precision_summary_rows")
                == tfe_algorithm_literal_work_precision.get("summary_row_count")
                == 4,
                "B4 TFE algorithm-literal work/precision summary row count changed",
            )
            checks.check(
                blocker.get("tfe_algorithm_literal_work_precision_terminal_overrun_rows")
                == tfe_algorithm_literal_work_precision.get("terminal_overrun_rows")
                == 12,
                "B4 TFE algorithm-literal work/precision terminal overrun count changed",
            )
            checks.check(
                blocker.get("tfe_algorithm_literal_work_precision_source_policy_rows_completed")
                == tfe_algorithm_literal_work_precision.get("source_policy_rows_completed")
                == 0,
                "B4 TFE algorithm-literal work/precision overcloses source-policy rows",
            )
            checks.check(
                blocker.get("tfe_algorithm_literal_work_precision_external_superiority_allowed")
                == tfe_algorithm_literal_work_precision.get("external_superiority_claim_allowed")
                is False,
                "B4 TFE algorithm-literal work/precision overclaims external superiority",
            )
            checks.check(
                blocker.get("source_policy_publication_grade_work_precision_open") is True,
                "B4 source-policy work/precision boundary changed",
            )
            checks.check(
                blocker.get("source_policy_work_precision_claim_excluded") is True,
                "B4 did not exclude source-policy work/precision from current claim",
            )
            checks.check(
                blocker.get("b4_post_execution_promotion_contract") == "B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json",
                "B4 promotion contract path missing",
            )
            checks.check(
                blocker.get("b4_post_execution_promotion_contract_schema")
                == b4_promotion_contract.get("schema")
                == "b4-source-policy-post-execution-promotion-contract-v1",
                "B4 promotion contract schema changed",
            )
            checks.check(
                blocker.get("b4_post_execution_promotion_contract_status")
                == b4_promotion_contract.get("status")
                == "promotion_contract_defined_no_rows_promoted",
                "B4 promotion contract status changed",
            )
            checks.check(
                blocker.get("b4_post_execution_promotion_contract_rows_closed")
                == b4_promotion_contract.get("source_policy_rows_closed_now")
                == 0,
                "B4 promotion contract overcloses source-policy rows",
            )
            checks.check(
                blocker.get("b4_post_execution_promotion_contract_rows_total")
                == b4_promotion_contract.get("source_policy_rows_total")
                == 40,
                "B4 promotion contract source-policy row total changed",
            )
            checks.check(
                blocker.get("b4_post_execution_promotion_contract_ready_mapped_rows")
                == b4_promotion_contract.get("ready_command_mapped_external_rows")
                == b4_promotion_contract.get("after_ready_commands_only", {}).get("mapped_external_rows")
                == 20,
                "B4 promotion contract ready mapped rows changed",
            )
            checks.check(
                blocker.get("b4_post_execution_promotion_contract_unaddressed_rows")
                == b4_promotion_contract.get("unaddressed_external_rows_after_ready_commands")
                == b4_promotion_contract.get("after_ready_commands_only", {}).get("unaddressed_external_rows")
                == 0,
                "B4 promotion contract unaddressed row count changed",
            )
            checks.check(
                blocker.get("b4_post_execution_promotion_contract_checks_satisfied_now")
                == b4_promotion_contract.get("all_required_checks_satisfied_now")
                is False,
                "B4 promotion contract prematurely satisfies all checks",
            )
            checks.check(
                blocker.get("b4_post_execution_promotion_contract_b4_can_close_now")
                == b4_promotion_contract.get("b4_can_close_after_promotion_contract_now")
                == b4_promotion_contract.get("after_ready_commands_only", {}).get("b4_can_close")
                is False,
                "B4 promotion contract prematurely closes B4",
            )
            checks.check(
                blocker.get("b4_post_execution_promotion_contract_b7_can_close_now")
                == b4_promotion_contract.get("b7_can_close_after_promotion_contract_now")
                == b4_promotion_contract.get("after_ready_commands_only", {}).get("b7_can_close")
                is False,
                "B4 promotion contract prematurely closes B7",
            )
            checks.check(
                blocker.get("b4_post_execution_promotion_contract_ready_lane_count")
                == b4_promotion_contract.get("lane_summary", {}).get("ready_to_launch_after_explicit_opt_in_count")
                == 2,
                "B4 promotion contract ready lane count changed",
            )
            checks.check(
                blocker.get("b4_post_execution_promotion_contract_not_ready_lane_count")
                == b4_promotion_contract.get("lane_summary", {}).get("not_ready_lane_count")
                == 2,
                "B4 promotion contract not-ready lane count changed",
            )
            checks.check(
                blocker.get("b4_post_execution_promotion_contract_runner_code_path_gap_rows")
                == b4_promotion_contract.get("remaining_gap_rows_requiring_new_runner_or_code_path")
                == 0,
                "B4 promotion contract runner/code-path gap rows changed",
            )
            checks.check(
                b4_promotion_contract.get("post_execution_promotion_required") is True,
                "B4 promotion contract lost post-execution requirement",
            )
            checks.check(
                [item.get("id") for item in b4_promotion_contract.get("promotion_checklist", [])]
                == [
                    "source_policy_row_provenance",
                    "same_run_error_and_work_metrics",
                    "diagnostic_rows_not_promoted",
                    "ready_command_rows_are_insufficient_by_themselves",
                    "remaining_gap_rows_stay_open_or_demoted",
                    "nonpublic_code_self_reproduction_disposition_recorded",
                    "publication_figures_rebuilt_from_promoted_rows",
                    "closure_validators_rerun_after_promotion",
                ],
                "B4 promotion contract checklist IDs changed",
            )
            checks.check(
                contains_normalized(
                    gate_md,
                    "B4 post-execution promotion contract added with schema",
                ),
                "B4 gate markdown missing promotion contract summary",
            )
            checks.check(
                contains_normalized(
                    gate_md,
                    "rows `0/40`, ready/unaddressed `20/0`, checks satisfied `False`, closes B4/B7 `False/False`",
                ),
                "B4 gate markdown missing promotion contract closure boundary",
            )
            checks.check(
                contains_normalized(
                    b4_execution_opt_in_packet_md,
                    "Post-execution promotion contract",
                ),
                "B4 opt-in packet markdown missing promotion contract section",
            )
            checks.check(
                blocker.get("b4_source_policy_post_execution_audit") == "B4_SOURCE_POLICY_POST_EXECUTION_AUDIT.md",
                "B4 post-execution audit report path missing",
            )
            checks.check(
                blocker.get("b4_source_policy_post_execution_audit_json") == "B4_SOURCE_POLICY_POST_EXECUTION_AUDIT.json",
                "B4 post-execution audit JSON path missing",
            )
            checks.check(
                blocker.get("b4_source_policy_post_execution_audit_schema")
                == b4_source_policy_post_execution_audit.get("schema")
                == "b4-source-policy-post-execution-audit-v1",
                "B4 post-execution audit schema changed",
            )
            checks.check(
                blocker.get("b4_source_policy_post_execution_audit_status")
                == b4_source_policy_post_execution_audit.get("status"),
                "B4 post-execution audit status changed",
            )
            checks.check(
                blocker.get("b4_source_policy_post_execution_approved_driver_execution_recorded")
                == b4_source_policy_post_execution_audit.get("approved_driver_execution_recorded")
                == b4_post_summary.get("approved_driver_execution_recorded")
                is b4_authorized,
                "B4 post-execution audit approved driver marker inconsistent",
            )
            checks.check(
                blocker.get("b4_source_policy_post_execution_verified_authorized_execution_recorded")
                == b4_source_policy_post_execution_audit.get("verified_authorized_execution_recorded")
                == b4_post_summary.get("verified_authorized_execution_recorded")
                is b4_authorized,
                "B4 post-execution audit verified authorized marker inconsistent",
            )
            checks.check(
                blocker.get("b4_source_policy_post_execution_existing_ready_command_artifacts_present")
                == b4_source_policy_post_execution_audit.get("existing_ready_command_artifacts_present")
                == b4_post_summary.get("existing_ready_command_artifacts_present")
                is True,
                "B4 post-execution audit existing-artifact marker changed",
            )
            checks.check(
                blocker.get("b4_source_policy_post_execution_execution_record_scope")
                == b4_source_policy_post_execution_audit.get("execution_record_scope")
                == b4_expected_scope,
                "B4 post-execution audit execution scope changed",
            )
            checks.check(
                blocker.get("b4_source_policy_post_execution_outputs_present")
                == b4_post_presence.get("all_expected_outputs_exist_now")
                is True,
                "B4 post-execution audit output-presence marker changed",
            )
            checks.check(
                blocker.get("b4_source_policy_post_execution_ready_commands_in_packet")
                == b4_post_summary.get("ready_commands_in_packet")
                == b4_post_presence.get("command_count")
                == 13,
                "B4 post-execution ready command packet count changed",
            )
            checks.check(
                blocker.get("b4_source_policy_post_execution_ready_commands_verified_executed_by_this_record")
                == b4_post_summary.get("ready_commands_verified_executed_by_this_record")
                == b4_expected_verified_commands,
                "B4 post-execution verified executed command count changed",
            )
            checks.check(
                blocker.get("b4_source_policy_post_execution_ready_mapped_rows")
                == b4_post_summary.get("ready_command_mapped_external_rows")
                == b4_source_policy_post_execution_audit.get("guarded_driver", {}).get(
                    "ready_command_mapped_external_rows"
                )
                == 20,
                "B4 post-execution ready mapped rows changed",
            )
            checks.check(
                blocker.get("b4_source_policy_post_execution_unaddressed_rows")
                == b4_post_summary.get("unaddressed_external_rows_after_ready_commands")
                == b4_source_policy_post_execution_audit.get("guarded_driver", {}).get(
                    "unaddressed_external_rows_after_ready_commands"
                )
                == 0,
                "B4 post-execution unaddressed row count changed",
            )
            checks.check(
                blocker.get("b4_source_policy_post_execution_rows_closed")
                == b4_source_policy_post_execution_audit.get("source_policy_rows_closed")
                == b4_source_policy_post_execution_audit.get("row_status_after_driver", {}).get(
                    "source_policy_rows_closed"
                )
                == b4_post_summary.get("source_policy_rows_promoted_after_driver")
                == 0,
                "B4 post-execution audit overcloses source-policy rows",
            )
            checks.check(
                blocker.get("b4_source_policy_post_execution_rows_total")
                == b4_source_policy_post_execution_audit.get("source_policy_total_rows")
                == b4_source_policy_post_execution_audit.get("row_status_after_driver", {}).get(
                    "source_policy_rows_total"
                )
                == b4_post_summary.get("source_policy_rows_total")
                == 40,
                "B4 post-execution source-policy row total changed",
            )
            checks.check(
                blocker.get("b4_source_policy_post_execution_rows_open")
                == b4_source_policy_post_execution_audit.get("source_policy_rows_open")
                == b4_source_policy_post_execution_audit.get("row_status_after_driver", {}).get(
                    "source_policy_rows_open"
                )
                == 20,
                "B4 post-execution open row count changed",
            )
            checks.check(
                blocker.get("b4_source_policy_post_execution_external_superiority_claim_allowed")
                == b4_source_policy_post_execution_audit.get("external_superiority_claim_allowed")
                is False,
                "B4 post-execution audit overclaims external superiority",
            )
            checks.check(
                blocker.get("b4_source_policy_post_execution_b4_can_close_now")
                == b4_source_policy_post_execution_audit.get("b4_can_close_now")
                == b4_post_summary.get("b4_can_close_now")
                is False,
                "B4 post-execution audit prematurely closes B4",
            )
            checks.check(
                blocker.get("b4_source_policy_post_execution_b7_can_close_now")
                == b4_source_policy_post_execution_audit.get("b7_can_close_now")
                == b4_post_summary.get("b7_can_close_now")
                is False,
                "B4 post-execution audit prematurely closes B7",
            )
            checks.check(
                blocker.get("b4_source_policy_post_execution_ra2021_double_low_order_status")
                == b4_post_evidence.get("ra2021_double_low_order_diagnosis_status")
                == "diagnosis_only_low_order_floor_limited_not_promoted",
                "B4 post-execution RA2021 low-order diagnosis status changed",
            )
            checks.check(
                blocker.get("b4_source_policy_post_execution_hi2022_selected_candidate_status")
                == b4_post_evidence.get("hi2022_selected_candidate_status")
                == "selected_candidate_matrix_partially_executed_not_promoted",
                "B4 post-execution HI2022 selected-candidate status changed",
            )
            checks.check(
                blocker.get("b4_source_policy_post_execution_hi2022_ra_half_double_failure_status")
                == b4_post_evidence.get("hi2022_ra_half_double_failure_diagnosis_status")
                == "diagnosis_only_partial_newton_failure_not_promoted",
                "B4 post-execution HI2022 failure diagnosis status changed",
            )
            checks.check(
                contains_normalized(
                    gate_md,
                    "B4 post-execution audit recorded with status",
                ),
                "B4 gate markdown missing post-execution audit summary",
            )
            checks.check(
                contains_normalized(
                    gate_md,
                    f"verified-authorized/existing-artifacts/output-present `{b4_authorized}/True/True`, promoted rows `0/40`, and B4/B7 close flags `False/False`",
                ),
                "B4 gate markdown missing post-execution audit closure boundary",
            )
            checks.check(
                "Top-level post-execution summary rows/B4/B7: `0/40` / `False/False`."
                in b4_source_policy_post_execution_audit_md,
                "B4 post-execution audit markdown summary missing",
            )
            checks.check(blocker.get("paper_submission_b4_can_close_now") is True, "B4 not marked closed under narrowed policy")
            checks.check(
                blocker.get("paper_submission_b4_can_close_now_under_narrowed_policy") is True,
                "B4 narrowed-policy closure marker missing",
            )
            checks.check(
                "../v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_newton_coarse_order.json"
                in blocker.get("partial_progress_evidence", []),
                "B4 closed-loop coarse-dynamics diagnostic evidence missing",
            )
            checks.check(
                "EXTERNAL_SAME_TEST_ACCEPTANCE_SHEET.md" in blocker.get("partial_progress_evidence", []),
                "B4 acceptance sheet MD evidence missing",
            )
            checks.check(
                "EXTERNAL_SAME_TEST_ACCEPTANCE_SHEET.json" in blocker.get("partial_progress_evidence", []),
                "B4 acceptance sheet JSON evidence missing",
            )
            checks.check(
                "COMPARISON_OBJECTIVE_CLOSURE_RECONCILIATION_AUDIT.md" in blocker.get("partial_progress_evidence", []),
                "B4 comparison reconciliation evidence missing",
            )
            checks.check(
                "COMPARISON_OBJECTIVE_CLOSURE_RECONCILIATION_AUDIT.json" in blocker.get("partial_progress_evidence", []),
                "B4 comparison reconciliation JSON evidence missing",
            )
            checks.check(
                "validate_comparison_objective_closure_reconciliation_audit.py" in blocker.get("partial_progress_evidence", []),
                "B4 comparison reconciliation validator evidence missing",
            )
            checks.check(
                "ALL_METHOD_EXAMPLE_CLAIM_DISPOSITION_AUDIT.md" in blocker.get("partial_progress_evidence", []),
                "B4 all-method claim-disposition MD evidence missing",
            )
            checks.check(
                "ALL_METHOD_EXAMPLE_CLAIM_DISPOSITION_AUDIT.json" in blocker.get("partial_progress_evidence", []),
                "B4 all-method claim-disposition JSON evidence missing",
            )
            checks.check(
                "validate_all_method_example_claim_disposition_audit.py" in blocker.get("partial_progress_evidence", []),
                "B4 all-method claim-disposition validator evidence missing",
            )
            checks.check(
                "TFE_ALGORITHM_LITERAL_ENDPOINT_PROBE.md" in blocker.get("partial_progress_evidence", []),
                "B4 TFE algorithm-literal endpoint probe MD evidence missing",
            )
            checks.check(
                "TFE_ALGORITHM_LITERAL_ENDPOINT_PROBE.json" in blocker.get("partial_progress_evidence", []),
                "B4 TFE algorithm-literal endpoint probe JSON evidence missing",
            )
            checks.check(
                "TFE_ALGORITHM_LITERAL_ENDPOINT_PROBE.csv" in blocker.get("partial_progress_evidence", []),
                "B4 TFE algorithm-literal endpoint probe CSV evidence missing",
            )
            checks.check(
                "validate_tfe_algorithm_literal_endpoint_probe.py" in blocker.get("partial_progress_evidence", []),
                "B4 TFE algorithm-literal endpoint probe validator evidence missing",
            )
            for evidence, message in [
                ("TFE_SOURCE_GRID_COMPATIBILITY_AUDIT.md", "B4 TFE source-grid audit MD evidence missing"),
                ("TFE_SOURCE_GRID_COMPATIBILITY_AUDIT.json", "B4 TFE source-grid audit JSON evidence missing"),
                (
                    "validate_tfe_source_grid_compatibility_audit.py",
                    "B4 TFE source-grid audit validator evidence missing",
                ),
            ]:
                checks.check(evidence in blocker.get("partial_progress_evidence", []), message)
            for evidence, message in [
                (
                    "../v048_cross_paper_same_test_benchmarks/results/tfe_source_pendulum_same_test_work_precision.md",
                    "B4 TFE same-test work/precision MD evidence missing",
                ),
                (
                    "../v048_cross_paper_same_test_benchmarks/results/tfe_source_pendulum_same_test_work_precision.json",
                    "B4 TFE same-test work/precision JSON evidence missing",
                ),
                (
                    "../v048_cross_paper_same_test_benchmarks/results/tfe_source_pendulum_same_test_work_precision_rows.csv",
                    "B4 TFE same-test work/precision raw CSV evidence missing",
                ),
                (
                    "../v048_cross_paper_same_test_benchmarks/results/tfe_source_pendulum_same_test_work_precision_summary.csv",
                    "B4 TFE same-test work/precision summary CSV evidence missing",
                ),
                (
                    "../v048_cross_paper_same_test_benchmarks/results/tfe_source_pendulum_same_test_work_precision.png",
                    "B4 TFE same-test work/precision figure evidence missing",
                ),
                (
                    "../v048_cross_paper_same_test_benchmarks/validate_tfe_source_pendulum_same_test_work_precision.py",
                    "B4 TFE same-test work/precision validator evidence missing",
                ),
                (
                    "TFE_ALGORITHM_LITERAL_WORK_PRECISION_AUDIT.md",
                    "B4 TFE algorithm-literal work/precision MD evidence missing",
                ),
                (
                    "TFE_ALGORITHM_LITERAL_WORK_PRECISION_AUDIT.json",
                    "B4 TFE algorithm-literal work/precision JSON evidence missing",
                ),
                (
                    "TFE_ALGORITHM_LITERAL_WORK_PRECISION_AUDIT.csv",
                    "B4 TFE algorithm-literal work/precision CSV evidence missing",
                ),
                (
                    "figures/tfe_algorithm_literal_work_precision.png",
                    "B4 TFE algorithm-literal work/precision figure evidence missing",
                ),
                (
                    "validate_tfe_algorithm_literal_work_precision_audit.py",
                    "B4 TFE algorithm-literal work/precision validator evidence missing",
                ),
                (
                    "B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.md",
                    "B4 source-policy execution opt-in packet MD evidence missing",
                ),
                (
                    "B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json",
                    "B4 source-policy execution opt-in packet JSON evidence missing",
                ),
                (
                    "validate_b4_source_policy_execution_opt_in_packet.py",
                    "B4 source-policy execution opt-in packet validator evidence missing",
                ),
                (
                    "B4_SOURCE_POLICY_POST_EXECUTION_AUDIT.md",
                    "B4 source-policy post-execution audit MD evidence missing",
                ),
                (
                    "B4_SOURCE_POLICY_POST_EXECUTION_AUDIT.json",
                    "B4 source-policy post-execution audit JSON evidence missing",
                ),
                (
                    "validate_b4_source_policy_post_execution_audit.py",
                    "B4 source-policy post-execution audit validator evidence missing",
                ),
            ]:
                checks.check(evidence in blocker.get("partial_progress_evidence", []), message)
            checks.check(
                blocker.get("required_to_close", []) == [],
                "B4 should not have current-scope remaining requirements",
            )
            checks.check(
                set(blocker.get("excluded_future_source_policy_requirements", []))
                == {"fair_implemented_baselines", "work_precision_curves"},
                "B4 future source-policy requirements changed",
            )
        if blocker_id == "B6":
            checks.check(
                "proof_traceability_table_reader_facing_rewrite" in blocker.get("partial_progress", []),
                "B6 lost proof-traceability prose progress marker",
            )
            checks.check(
                "main_body_machine_token_removal_pass" in blocker.get("partial_progress", []),
                "B6 lost main-body machine-token removal progress marker",
            )
            checks.check(
                "comparison_theorem_wording_removed" in blocker.get("partial_progress", []),
                "B6 lost comparison-theorem wording cleanup progress marker",
            )
            checks.check(
                "reproducibility_appendix_compaction_pass" in blocker.get("partial_progress", []),
                "B6 lost reproducibility appendix compaction progress marker",
            )
            checks.check(
                "prose_residue_audit_added" in blocker.get("partial_progress", []),
                "B6 lost prose-residue audit progress marker",
            )
            checks.check(
                "b6_post_execution_dependency_boundary_added" in blocker.get("partial_progress", []),
                "B6 lost post-execution dependency progress marker",
            )
            checks.check(
                "final_prose_pass_closed_under_narrowed_policy" in blocker.get("partial_progress", []),
                "B6 lost narrowed final-prose closure marker",
            )
            b6_post_dependency = prose_residue_audit_json.get("post_baseline_final_prose_dependency", {}).get(
                "post_execution_dependency_boundary",
                {},
            )
            b6_authorized = b6_post_dependency.get("verified_authorized_execution_recorded") is True
            b6_expected_status = (
                "verified_authorized_execution_zero_promoted_rows_source_policy_excluded_final_prose_enabled"
                if b6_authorized
                else "existing_artifacts_present_no_verified_authorized_execution_zero_promoted_rows_source_policy_excluded_final_prose_enabled"
            )
            b6_expected_scope = (
                "verified_authorized_guarded_driver_execution"
                if b6_authorized
                else "no_verified_current_authorized_execution_record_existing_artifacts_only"
            )
            checks.check(
                "CMAME_PROSE_RESIDUE_AUDIT.md" in blocker.get("partial_progress_evidence", []),
                "B6 prose-residue audit evidence missing",
            )
            checks.check(
                "CMAME_PROSE_RESIDUE_AUDIT.json" in blocker.get("partial_progress_evidence", []),
                "B6 prose-residue audit JSON evidence missing",
            )
            checks.check(
                "validate_cmame_prose_residue_audit.py" in blocker.get("partial_progress_evidence", []),
                "B6 prose-residue audit validator evidence missing",
            )
            checks.check(
                "B4_SOURCE_POLICY_POST_EXECUTION_AUDIT.json" in blocker.get("partial_progress_evidence", []),
                "B6 post-execution dependency audit evidence missing",
            )
            checks.check(blocker.get("main_body_machine_token_count") == 0, "B6 main-body token count changed")
            checks.check(blocker.get("flat_main_body_machine_token_count") == 0, "B6 flat main-body token count changed")
            checks.check(blocker.get("artifact_macro_confined_to_appendix") is True, "B6 appendix confinement marker changed")
            checks.check(blocker.get("appendix_artifact_macro_count") == 0, "B6 appendix artifact count changed")
            checks.check(blocker.get("flat_appendix_artifact_macro_count") == 0, "B6 flat appendix artifact count changed")
            checks.check(blocker.get("reproducibility_appendix_compacted") is True, "B6 appendix compaction marker missing")
            checks.check(blocker.get("run_v047_invoked") is False, "B6 prose audit should not invoke run_v047")
            checks.check(
                blocker.get("b6_post_execution_dependency_status")
                == b6_post_dependency.get("status")
                == b6_expected_status,
                "B6 post-execution dependency status changed",
            )
            checks.check(
                blocker.get("b6_post_execution_dependency_audit")
                == b6_post_dependency.get("post_execution_audit")
                == "B4_SOURCE_POLICY_POST_EXECUTION_AUDIT.json",
                "B6 post-execution dependency audit path changed",
            )
            checks.check(
                blocker.get("b6_post_execution_approved_driver_execution_recorded")
                == b6_post_dependency.get("approved_driver_execution_recorded")
                is b6_authorized,
                "B6 post-execution dependency approved driver marker inconsistent",
            )
            checks.check(
                blocker.get("b6_post_execution_verified_authorized_execution_recorded")
                == b6_post_dependency.get("verified_authorized_execution_recorded")
                is b6_authorized,
                "B6 post-execution dependency verified authorized marker inconsistent",
            )
            checks.check(
                blocker.get("b6_post_execution_existing_ready_command_artifacts_present")
                == b6_post_dependency.get("existing_ready_command_artifacts_present")
                is True,
                "B6 post-execution dependency existing-artifact marker changed",
            )
            checks.check(
                blocker.get("b6_post_execution_execution_record_scope")
                == b6_post_dependency.get("execution_record_scope")
                == b6_expected_scope,
                "B6 post-execution dependency execution scope changed",
            )
            checks.check(
                blocker.get("b6_post_execution_outputs_present")
                == b6_post_dependency.get("all_expected_outputs_exist_now")
                is True,
                "B6 post-execution output-presence marker changed",
            )
            checks.check(
                blocker.get("b6_post_execution_rows_promoted_after_driver")
                == b6_post_dependency.get("source_policy_rows_promoted_after_driver")
                == 0,
                "B6 post-execution dependency overpromotes source-policy rows",
            )
            checks.check(
                blocker.get("b6_post_execution_rows_total")
                == b6_post_dependency.get("source_policy_rows_total")
                == 40,
                "B6 post-execution dependency row total changed",
            )
            checks.check(
                blocker.get("b6_post_execution_b4_can_close_now")
                == b6_post_dependency.get("b4_can_close_now")
                is False,
                "B6 post-execution dependency prematurely closes B4",
            )
            checks.check(
                blocker.get("b6_post_execution_b7_can_close_now")
                == b6_post_dependency.get("b7_can_close_now")
                is False,
                "B6 post-execution dependency prematurely closes B7",
            )
            checks.check(
                blocker.get("b6_post_execution_same_guarded_driver_rerun_recommended")
                == b6_post_dependency.get("same_guarded_driver_rerun_recommended")
                is False,
                "B6 post-execution dependency should not recommend same driver rerun",
            )
            checks.check(
                blocker.get("b6_post_execution_final_prose_pass_enabled")
                == b6_post_dependency.get("final_prose_pass_enabled_by_post_execution")
                is False,
                "B6 post-execution dependency incorrectly enables final prose pass",
            )
            checks.check(
                blocker.get("b6_final_prose_pass_enabled_by_narrowed_policy")
                == b6_post_dependency.get("final_prose_pass_enabled_by_narrowed_policy")
                is True,
                "B6 narrowed-policy final prose marker missing",
            )
        if blocker_id == "B7":
            checks.check(
                "limitation_explanation_figure_integrated" in blocker.get("partial_progress", []),
                "B7 lost limitation-figure progress marker",
            )
            checks.check(
                "figures/claim_boundary_limitations.png" in blocker.get("partial_progress_evidence", []),
                "B7 limitation figure evidence missing",
            )
            checks.check(
                "cmame_submission_flat/Figure_8_claim_boundary_limitations.png" in blocker.get("partial_progress_evidence", []),
                "B7 flat limitation figure evidence missing",
            )
            checks.check(
                "coarse_baseline_work_precision_figure_integrated" in blocker.get("partial_progress", []),
                "B7 lost coarse baseline/work-precision figure progress marker",
            )
            checks.check(
                "figures/coarse_baseline_work_precision.png" in blocker.get("partial_progress_evidence", []),
                "B7 coarse baseline/work-precision figure evidence missing",
            )
            checks.check(
                "cmame_submission_flat/Figure_9_coarse_baseline_work_precision.png" in blocker.get("partial_progress_evidence", []),
                "B7 flat coarse baseline/work-precision figure evidence missing",
            )
            checks.check(
                "closed_loop_true_dynamic_order_figure_integrated" in blocker.get("partial_progress", []),
                "B7 lost closed-loop coarse-dynamics diagnostic figure progress marker",
            )
            checks.check(
                "figures/closed_loop_true_dynamic_order.png" in blocker.get("partial_progress_evidence", []),
                "B7 closed-loop coarse-dynamics diagnostic figure evidence missing",
            )
            checks.check(
                "cmame_submission_flat/Figure_10_closed_loop_true_dynamic_order.png" in blocker.get("partial_progress_evidence", []),
                "B7 flat closed-loop coarse-dynamics diagnostic figure evidence missing",
            )
            checks.check(
                "method_stage_architecture_figure_integrated" in blocker.get("partial_progress", []),
                "B7 lost method-stage architecture figure progress marker",
            )
            checks.check(
                "figures/method_stage_architecture.png" in blocker.get("partial_progress_evidence", []),
                "B7 method-stage architecture figure evidence missing",
            )
            checks.check(
                "cmame_submission_flat/Figure_11_method_stage_architecture.png" in blocker.get("partial_progress_evidence", []),
                "B7 flat method-stage architecture figure evidence missing",
            )
            checks.check(
                "all_method_result_matrix_figure_integrated" in blocker.get("partial_progress", []),
                "B7 lost all-method matrix figure progress marker",
            )
            checks.check(
                "figure_set_audit_added" in blocker.get("partial_progress", []),
                "B7 lost figure-set audit progress marker",
            )
            checks.check(
                "narrowed_diagnostic_figure_scope_closed" in blocker.get("partial_progress", []),
                "B7 lost narrowed figure-scope closure marker",
            )
            checks.check(
                "figures/all_method_result_matrix.png" in blocker.get("partial_progress_evidence", []),
                "B7 all-method matrix figure evidence missing",
            )
            checks.check(
                "cmame_submission_flat/Figure_12_all_method_result_matrix.png" in blocker.get("partial_progress_evidence", []),
                "B7 flat all-method matrix figure evidence missing",
            )
            checks.check(
                "work_precision_compendium_figure_integrated" in blocker.get("partial_progress", []),
                "B7 lost work/precision compendium figure progress marker",
            )
            checks.check(
                "tfe_algorithm_literal_work_precision_figure13_panel_integrated"
                in blocker.get("partial_progress", []),
                "B7 lost TFE Algorithm-literal Figure 13 panel progress marker",
            )
            checks.check(
                "figures/work_precision_compendium.png" in blocker.get("partial_progress_evidence", []),
                "B7 work/precision compendium figure evidence missing",
            )
            checks.check(
                "cmame_submission_flat/Figure_13_work_precision_compendium.png"
                in blocker.get("partial_progress_evidence", []),
                "B7 flat work/precision compendium figure evidence missing",
            )
            checks.check(
                "TFE_ALGORITHM_LITERAL_WORK_PRECISION_AUDIT.csv"
                in blocker.get("partial_progress_evidence", []),
                "B7 TFE Algorithm-literal work/precision CSV evidence missing",
            )
            checks.check(
                "CMAME_FIGURE_SET_AUDIT.md" in blocker.get("partial_progress_evidence", []),
                "B7 figure-set audit MD evidence missing",
            )
            checks.check(
                "CMAME_FIGURE_SET_AUDIT.json" in blocker.get("partial_progress_evidence", []),
                "B7 figure-set audit JSON evidence missing",
            )
            checks.check(
                "validate_cmame_figure_set_audit.py" in blocker.get("partial_progress_evidence", []),
                "B7 figure-set audit validator evidence missing",
            )
            checks.check(blocker.get("figure_set_audit") == "CMAME_FIGURE_SET_AUDIT.md", "B7 figure-set audit path missing")
            checks.check(blocker.get("figure_set_audit_json") == "CMAME_FIGURE_SET_AUDIT.json", "B7 figure-set audit JSON path missing")
            checks.check(blocker.get("figure_count_audited") == 13, "B7 figure count changed")
            checks.check(blocker.get("figure12_all_method_matrix_integrated") is True, "B7 Figure 12 integration marker changed")
            checks.check(
                blocker.get("figure13_work_precision_compendium_integrated") is True,
                "B7 Figure 13 integration marker changed",
            )
            checks.check(
                blocker.get("figure13_tfe_algorithm_literal_work_precision_panels_integrated") is True,
                "B7 Figure 13 TFE Algorithm-literal panel marker changed",
            )
            checks.check(
                blocker.get("figure13_tfe_algorithm_literal_work_precision_source_csv")
                == "TFE_ALGORITHM_LITERAL_WORK_PRECISION_AUDIT.csv",
                "B7 Figure 13 TFE Algorithm-literal source CSV changed",
            )
            checks.check(
                blocker.get("figure13_tfe_algorithm_literal_work_precision_source_policy_rows_completed")
                == tfe_algorithm_literal_work_precision.get("source_policy_rows_completed"),
                "B7 Figure 13 TFE Algorithm-literal source-policy count mismatch",
            )
            checks.check(blocker.get("all_figures_integrated_main_flat") is True, "B7 main/flat integration marker changed")
            checks.check(blocker.get("all_pdf_captions_present") is True, "B7 PDF caption marker changed")
            checks.check(blocker.get("b7_closed_by_figure_set_audit") is True, "B7 figure-set audit did not close blocker")

    forbidden_main_body_tokens = [
        r"\artifact{",
        "CLAIM_BOUNDARY",
        "ORDER_ACCEPTANCE_GATE",
        "CROSS_PAPER_BENCHMARK",
        "DYNAMIC_ROW_ORACLE",
        "IMPLEMENTATION_FIDELITY",
        "SOURCE_PAPER_COMPARISON",
        "CMAME_",
        "CURRENT_PIPELINE",
        "SUBMISSION_",
        "validate_",
        "run_v047",
        "summary_v047",
        "external_superiority_claim",
        "same_test_campaign_status",
        "full_tfe_stage_replacement=false",
        "source repository",
        "present artifact",
        "present artifacts",
    ]
    for tex_label, tex_text in [("main_cmame.tex", main_tex), ("main_cmame_submission.tex", flat_tex)]:
        body = argumentative_body(tex_text)
        for token in forbidden_main_body_tokens:
            checks.check(token not in body, f"{tex_label} main body still contains machine token: {token}")

    closure_rule = gate.get("closure_rule", {})
    checks.check(closure_rule.get("open_blocker_count") == 0, "open blocker count changed")
    checks.check(closure_rule.get("ready_when_open_blocker_count") == 0, "ready closure rule changed")
    checks.check(closure_rule.get("submission_ready_requires_quality_review_passed") is True, "quality-review closure rule changed")
    checks.check(closure_rule.get("validators_are_necessary_not_sufficient") is True, "validator sufficiency marker changed")

    for source_key, source_label in gate.get("source_files", {}).items():
        checks.check(isinstance(source_label, str) and source_label, f"source file label missing for {source_key}")
    source_files = gate.get("source_files", {})
    checks.check(
        source_files.get("all_method_example_claim_disposition_audit") == "ALL_METHOD_EXAMPLE_CLAIM_DISPOSITION_AUDIT.md",
        "gate source files missing all-method claim-disposition audit",
    )
    checks.check(
        source_files.get("all_method_example_claim_disposition_audit_json") == "ALL_METHOD_EXAMPLE_CLAIM_DISPOSITION_AUDIT.json",
        "gate source files missing all-method claim-disposition JSON",
    )
    checks.check(
        source_files.get("all_method_example_claim_disposition_audit_validator")
        == "validate_all_method_example_claim_disposition_audit.py",
        "gate source files missing all-method claim-disposition validator",
    )
    checks.check(
        source_files.get("b4_source_policy_post_execution_audit") == "B4_SOURCE_POLICY_POST_EXECUTION_AUDIT.md",
        "gate source files missing B4 post-execution audit",
    )
    checks.check(
        source_files.get("b4_source_policy_post_execution_audit_json") == "B4_SOURCE_POLICY_POST_EXECUTION_AUDIT.json",
        "gate source files missing B4 post-execution audit JSON",
    )
    checks.check(
        source_files.get("b4_source_policy_post_execution_audit_validator")
        == "validate_b4_source_policy_post_execution_audit.py",
        "gate source files missing B4 post-execution audit validator",
    )
    checks.check(
        source_files.get("hi2022_policy_decision_audit") == "HI2022_POLICY_DECISION_AUDIT.md",
        "gate source files missing HI2022 policy-decision audit",
    )
    checks.check(
        source_files.get("hi2022_policy_decision_audit_json") == "HI2022_POLICY_DECISION_AUDIT.json",
        "gate source files missing HI2022 policy-decision audit JSON",
    )
    checks.check(
        source_files.get("hi2022_policy_decision_audit_validator") == "validate_hi2022_policy_decision_audit.py",
        "gate source files missing HI2022 policy-decision validator",
    )
    checks.check(
        source_files.get("hi2022_source_policy_row_audit") == "HI2022_SOURCE_POLICY_ROW_AUDIT.md",
        "gate source files missing HI2022 source-policy row audit",
    )
    checks.check(
        source_files.get("hi2022_source_policy_row_audit_json") == "HI2022_SOURCE_POLICY_ROW_AUDIT.json",
        "gate source files missing HI2022 source-policy row audit JSON",
    )
    checks.check(
        source_files.get("hi2022_source_policy_row_audit_validator")
        == "validate_hi2022_source_policy_row_audit.py",
        "gate source files missing HI2022 source-policy row audit validator",
    )
    checks.check(
        source_files.get("external_suite_demotion_ledger") == "EXTERNAL_SUITE_DEMOTION_LEDGER.md",
        "gate source files missing external suite demotion ledger",
    )
    checks.check(
        source_files.get("external_suite_demotion_ledger_json") == "EXTERNAL_SUITE_DEMOTION_LEDGER.json",
        "gate source files missing external suite demotion ledger JSON",
    )
    checks.check(
        source_files.get("external_suite_demotion_ledger_validator") == "validate_external_suite_demotion_ledger.py",
        "gate source files missing external suite demotion ledger validator",
    )
    checks.check(
        source_files.get("b2_source_policy_remaining_work_manifest") == "B2_SOURCE_POLICY_REMAINING_WORK_MANIFEST.md",
        "gate source files missing B2 remaining-work manifest",
    )
    checks.check(
        source_files.get("b2_source_policy_remaining_work_manifest_json")
        == "B2_SOURCE_POLICY_REMAINING_WORK_MANIFEST.json",
        "gate source files missing B2 remaining-work manifest JSON",
    )
    checks.check(
        source_files.get("b2_source_policy_remaining_work_manifest_validator")
        == "validate_b2_source_policy_remaining_work_manifest.py",
        "gate source files missing B2 remaining-work manifest validator",
    )
    checks.check(
        source_files.get("ra2021_source_policy_row_audit") == "RA2021_SOURCE_POLICY_ROW_AUDIT.md",
        "gate source files missing RA2021 source-policy audit",
    )
    checks.check(
        source_files.get("ra2021_source_policy_row_audit_json") == "RA2021_SOURCE_POLICY_ROW_AUDIT.json",
        "gate source files missing RA2021 source-policy audit JSON",
    )
    checks.check(
        source_files.get("ra2021_source_policy_row_audit_validator") == "validate_ra2021_source_policy_row_audit.py",
        "gate source files missing RA2021 source-policy audit validator",
    )
    checks.check(
        source_files.get("tfe_source_policy_row_audit") == "TFE_SOURCE_POLICY_ROW_AUDIT.md",
        "gate source files missing TFE source-policy audit",
    )
    checks.check(
        source_files.get("tfe_source_policy_row_audit_json") == "TFE_SOURCE_POLICY_ROW_AUDIT.json",
        "gate source files missing TFE source-policy audit JSON",
    )
    checks.check(
        source_files.get("tfe_source_policy_row_audit_validator") == "validate_tfe_source_policy_row_audit.py",
        "gate source files missing TFE source-policy audit validator",
    )
    checks.check(
        source_files.get("four_example_source_policy_dashboard") == "FOUR_EXAMPLE_SOURCE_POLICY_DASHBOARD.md",
        "gate source files missing four-example dashboard",
    )
    checks.check(
        source_files.get("four_example_source_policy_dashboard_json") == "FOUR_EXAMPLE_SOURCE_POLICY_DASHBOARD.json",
        "gate source files missing four-example dashboard JSON",
    )
    checks.check(
        source_files.get("four_example_source_policy_dashboard_validator")
        == "validate_four_example_source_policy_dashboard.py",
        "gate source files missing four-example dashboard validator",
    )
    checks.check(source_files.get("cmame_figure_set_audit") == "CMAME_FIGURE_SET_AUDIT.md", "gate source files missing figure-set audit")
    checks.check(
        source_files.get("cmame_figure_set_audit_json") == "CMAME_FIGURE_SET_AUDIT.json",
        "gate source files missing figure-set audit JSON",
    )
    checks.check(
        source_files.get("cmame_figure_set_audit_validator") == "validate_cmame_figure_set_audit.py",
        "gate source files missing figure-set audit validator",
    )
    checks.check(
        source_files.get("newton_euler_symbolic_target_audit") == "NEWTON_EULER_SYMBOLIC_TARGET_AUDIT.md",
        "gate source files missing Newton-Euler symbolic target audit",
    )
    checks.check(
        source_files.get("newton_euler_symbolic_target_audit_json") == "NEWTON_EULER_SYMBOLIC_TARGET_AUDIT.json",
        "gate source files missing Newton-Euler symbolic target audit JSON",
    )
    checks.check(
        source_files.get("newton_euler_symbolic_target_audit_validator")
        == "validate_newton_euler_symbolic_target_audit.py",
        "gate source files missing Newton-Euler symbolic target validator",
    )

    require_tokens(
        checks,
        gate_md,
        [
            "CMAME Blocker Closure Gate",
            "Status: **NARROWED CLAIM SUBCHECK CLOSED; GLOBAL SUBMISSION OPEN**",
            "`submission_ready=false`",
            "`global_submission_standard_met=false`",
            "`global_open_blockers=OC4,OC6,OC12`",
            "OC6/P6 disambiguation: `OC6` is the global source-policy TFE DAE-runner",
            "theorem `P6` is the retained solver-scale interface",
            "not a closed source-policy runner row.",
            "`narrowed_claim_subcheck_closed=true`",
            "legacy narrowed-claim compatibility flag, retained for validators only and not a global readiness marker:",
            "`legacy_submission_ready_under_narrowed_claim=true`",
            "deprecated narrowed-claim compatibility alias, retained for validators only and not a global readiness marker:",
            "`submission_ready_under_narrowed_claim=true`",
            "`submission_ready_scope=global_submission_ready_false_narrowed_claim_only`",
            "narrowed-claim alias warning:",
            "`validator-only compatibility aliases; do not read legacy_submission_ready_under_narrowed_claim or submission_ready_under_narrowed_claim as global submission readiness`",
            "`global_proof_package_submission_ready=false`",
            "legacy proof-readiness compatibility alias: `proof_submission_ready=false`",
            "`full_source_policy_submission_ready=false`",
            "coarse_first_no_default_1e-4",
            "default_1e-4_required=false",
            "same_test_campaign_status=not_run",
            "external_superiority_claim=false",
            "partial_evidence_overlay",
            "`default_1e-4_required=false`",
            "local evidence coverage examples: `4/4`",
            "accepted method dynamic-order examples: `2/4` (`single_pendulum`, `double_pendulum`)",
            "closed-loop mechanism-coverage coarse-dynamics diagnostics: `four_link`, `slider_crank`",
            "accepted source-policy dynamic-order examples: `0/4`",
            "HI2022 policy-decision audit status",
            "`bounded_T0p1_rows_complete_full_T8_source_policy_open`",
            "HI2022 bounded rows: `24/24`",
            "HI2022 full `T=8` source-policy completed: `false`",
            "HI2022 accepted for external superiority: `false`",
            "HI2022 source-policy dynamic-order examples: `0/4`",
            "HI2022 source-policy row audit status",
            "HI2022 active/source-policy-closed rows: `3/0`",
            "HI2022 B2 requirement can close now: `false`",
            "VP2024 source-policy suite demoted: `true`",
            "VP2024 demoted source-policy rows: `4`, flagged rows: `3`",
            "HI2022 source-policy suite demoted: `true`",
            "HI2022 demoted source-policy rows: `3`, flagged rows: `3`",
            "RA2021 source-policy suite demoted: `true`",
            "RA2021 demoted source-policy rows: `5`, flagged rows: `5`",
            "TFE source-policy suite demoted: `true`",
            "TFE demoted source-policy rows: `4`, flagged rows: `4`",
            "active source-policy flagged rows after demotions: `0`",
            "B2 closure execution plan",
            "`b2-source-policy-closure-execution-plan-v1`",
            "all active suites ready remains `true`",
            "explicit `1e-4` rows remain opt-in only",
            "historical method-side accepted dynamic-order examples: `single_pendulum`",
            "historical coverage-only method-side examples: `four_link`, `slider_crank`",
            "v048 coarse-first ready examples: `2/4`",
            "closed-loop coarse-dynamics diagnostic examples: `four_link`, `slider_crank`",
            "closed-loop coarse-dynamics diagnostic count: `2`",
            "four-link coarse-dynamics primary diagnostic slopes: `5.955/5.955/6.085/5.971`",
            "slider-crank coarse-dynamics primary diagnostic slopes: `6.164/6.159/7.341/6.426`",
            "public work/precision available examples: `four_link`, `slider_crank`",
            "public work/precision missing examples: none",
            "strict common-reference available examples: `four_link`, `slider_crank`",
            "strict common-reference gap examples: none",
            "strict common-reference figure available: `true`",
            "strict common-reference figure integrated in manuscript: `true`",
            "limitation explanation figure integrated in manuscript: `true`",
            "coarse baseline/work-precision figure integrated in manuscript: `true`",
            "closed-loop coarse-dynamics diagnostic figure integrated in manuscript: `true`",
            "method-stage architecture figure integrated in manuscript: `true`",
            "all-method result matrix figure integrated in manuscript: `true`",
            "work/precision compendium figure integrated in manuscript: `true`",
            "figure-set audit added: `true`, `13/13` figures checked in main/flat/PDF",
            "B6 prose-residue audit added: `true`",
            "B6 post-execution dependency boundary: `existing_artifacts_present_no_verified_authorized_execution_zero_promoted_rows_source_policy_excluded_final_prose_enabled`",
            "B6 post-execution final prose enabled by narrowed policy: `true`",
            "main-body machine-token count: `0`",
            "artifact macros confined to reproducibility appendix: `true`",
            "appendix artifact macro count: `0`",
            "reproducibility appendix compaction pass completed",
            "accepted dynamic-order count: `0`",
            "partial independent formula-row oracle rows: `96`",
            "partial kinematic/lower-pair defect certificate rows: `96`",
            "Newton-Euler dynamic defect obligation rows: `36`",
            "Newton-Euler active direct dynamic-defect open obligations: `0`",
            "Newton-Euler symbolic/primitive-route open obligations: `1`",
            "Newton-Euler symbolic target audit rows: `36`",
            "Newton-Euler symbolic target translational/rotational rows: `18/18`",
            "Newton-Euler symbolic target inventory complete: `true`",
            "Newton-Euler symbolic defect certificate complete: `false`",
            "partial formula-row excluded family: `newton_euler_weak_balance`",
            "full independent formula-row oracle rows: `132`",
            "runtime formula-row oracle complete: `true`",
            "formula-row AD Jacobian oracle: `true`",
            "formula-row AD Jacobian probe count: `3`",
            "max formula-row Jacobian mismatch: `3.330669e-16`",
            "`open_narrowed_claim_blockers=0`",
            "`closed_blockers=B1,B2,B3,B4,B5,B6,B7,B8`",
            "all-example common-reference comparison matrix closed: `true`",
            "common-reference examples checked",
            "common-reference cells checked: `44`",
            "raw rows recomputed for common-reference audit: `132`",
            "common-reference summary mismatches: `0`",
            "direct nonlocal velocity-order wins: `40/40`",
            "direct nonlocal finest-velocity-error wins: `40/40`",
            "all-method claim-disposition audit: `44` total cells",
            "all-method source-policy rows closed/open: `0/40`",
            "all-method strict external error-claim rows allowed: `0`",
            "B4 post-execution audit status",
            f"`{b4_source_policy_post_execution_audit.get('status')}`",
            "B4 post-execution verified-authorized/existing-artifacts/output-present",
            f"`{str(b4_authorized).lower()}/true/true`",
            "B4 post-execution promoted rows: `0/40`",
            "B4/B7 post-execution close flags: `false/false`",
            "B4/B7 narrowed-claim policy closure: `true`",
            "B6 narrowed-claim final prose closure: `true`",
            "source-policy flagged raw rows checked by all-example audit: `45`",
            "source-policy flagged examples checked",
            "source-policy superiority claim allowed: `false`",
            "B2/B4 can close from common-reference evidence alone: `false`",
            "COMPARISON_OBJECTIVE_CLOSURE_RECONCILIATION_AUDIT.md/json",
            "ALL_EXAMPLES_SOURCE_POLICY_AUDIT.md/json",
            "HI2022_POLICY_DECISION_AUDIT.md/json",
            "24/24 bounded `T=0.1` rows",
            "accepted source-policy dynamic-order examples stay at `0/4`",
            "EXTERNAL_SUITE_DEMOTION_LEDGER.md/json",
            "explicitly demotes VP2024, HI2022, RA2021, and TFE from external-superiority scope",
            "4 VP, 3 HI2022, 5 RA2021, and 4 TFE source-policy rows",
            "B2 remaining-work manifest status",
            "B2 active/demoted flagged rows after Route B demotion: `0/15`",
            "B2 source-policy closed rows and external-superiority-ready rows: `0/0`",
            "B2_SOURCE_POLICY_REMAINING_WORK_MANIFEST.md/json",
            "no active source-policy flagged rows remain after demotion",
            "source-policy rows closed stay `0/40`",
            "RA2021 source-policy row audit status",
            "RA2021 public order groups and timing rows: `12/12`, `12/12`",
            "RA2021 source-policy reproduction rows: `0/12`",
            "RA2021 B2 requirement can close now: `false`",
            "RA2021_SOURCE_POLICY_ROW_AUDIT.md/json",
            "RA2021 public order groups and timing rows are complete (`12/12` and `12/12`)",
            "source-policy reproduction rows remain `0/12`",
            "TFE source-policy row audit status",
            "TFE active/source-policy-closed rows: `0/0`",
            "TFE pendulum runner implemented: `false`",
            "TFE_ALGORITHM_LITERAL_ENDPOINT_PROBE.md/json/csv",
            "`4` methods, `12` metric rows, and `12` terminal-overrun rows",
            "source-policy rows still `0`",
            "tfe_source_pendulum_same_test_work_precision.md/json/csv/png",
            "`6` methods, `18/18` ok rows, and `6` summary rows",
            "same-test candidate work/precision rows still close `0` source-policy rows",
            "TFE_ALGORITHM_LITERAL_WORK_PRECISION_AUDIT.md/json/csv",
            "`4` methods, `12` raw rows, `4` summary rows, and `12` terminal-overrun rows",
            "runtime_proxy_available=false",
            "DYNAMIC_ROW_ORACLE_GATE.md",
            "CMAME_VISUAL_LEGIBILITY_AUDIT.md",
            "CMAME_RELATED_WORK_AUDIT.md",
            "CMAME_EXTERNAL_BASELINE_GATE.md",
            "external baseline gate and suite claim-boundary table added",
            "same_test_campaign_status=not_run",
            "CMAME_PROOF_CONTRACT_GATE.md",
            "proof contract gate added",
            "noncircular proof-condition decomposition added",
            "NEWTON_EULER_SYMBOLIC_TARGET_AUDIT.md/json",
            "direct residual-bridge/Kantorovich perturbation route",
            "PROOF_CLOSURE_MANIFEST.md/json",
            "strict_direct_residual_bridge_submission_standard.satisfied=true",
            "required_pc2_route=direct_residual_bridge_kantorovich_route",
            "direct_residual_bridge_kantorovich_route_closed=true",
            "primitive_route_required_for_b3_closure=false",
            "actual_taylor_bounds_proved=0",
            "open_taylor_bound_terms=162",
            "open_primitive_count=5",
            "96-row non-dynamic defect certificate",
            "Newton-Euler dynamic obligation ledger",
            "Newton-Euler symbolic target audit",
            "18 translational and 18 rotational",
            "primitive/Taylor 162-subterm route retained as an open conditional certificate schema",
            "conditional in the solver/regularity sense",
            "order-acceptance matrix added",
            "closed-loop coarse-dynamics diagnostic matrix added",
            "fair-baseline acceptance sheet added",
            "common-reference order/error matrix closed",
            "all-method claim-disposition",
            "TFE algorithm-literal endpoint probe added",
            "external run queue, acceptance sheet, all-example comparison reconciliation, source-policy closure triage, all-example source-policy audit, all-method claim-disposition audit, external case/evidence reconciliation, HI2022 policy-decision audit, HI2022 source-policy row audit, VP2024 explicit demotion ledger, B2 remaining-work manifest, B2 closure execution plan, RA2021 source-policy row audit, and TFE source-policy row audit added",
            "B2 remaining-work manifest added",
            "SOURCE_POLICY_CLOSURE_TRIAGE.md/json",
            "ALL_METHOD_EXAMPLE_CLAIM_DISPOSITION_AUDIT.md/json",
            "CMAME_FIGURE_SET_AUDIT.md/json",
            "acceptance sheet added",
            "20 non-`1e-4` shards",
            "accepted_external_dynamic_order_examples=0",
            "closed by AD-expanded symbolic oracle certificate",
            "Newton-Euler AD-expanded row oracle rows: `36/36`",
            "Newton-Euler AD-expanded row oracle columns/probes: `132/3`",
            "Newton-Euler AD-expanded symbolic oracle closure: `true`",
            "B1 independent residual symbolic row oracle rows: `36/36`",
            "B1 AD-expanded symbolic derivative cells: `4752/4752`",
            "B1 remaining symbolic oracle requirements: `[]`",
            "NEWTON_EULER_AD_EXPANDED_ROW_ORACLE_AUDIT.md/json",
            "row-level AD-expanded runtime/formula binding coverage for all 36 Newton--Euler dynamic rows",
            "B1_SYMBOLIC_ROW_ORACLE_CLOSURE_CERTIFICATE.md/json",
            "closes the independent residual-row symbolic oracle item for all 36 Newton--Euler rows",
            "B1_AD_EXPANDED_SYMBOLIC_ORACLE_CLOSURE_CERTIFICATE.md/json",
            "closing `36 x 132 = 4752` AD-expanded symbolic derivative cells",
            "Newton-Euler dynamic-row direct-substitution contract direct-route row-defect closed rows: `36/36`",
            "Newton-Euler D5 readiness open lifted-stage terms: `0/36`",
            "Newton-Euler D5 direct route PC2 closed: `true`",
            "Newton-Euler D5 primitive/Taylor route closed: `false`",
            "Current B1 Direct-Route Update",
            "B1 is therefore closed",
            "P_state direct full-residual route certificate closed: `true`",
            "P_state direct-route PS3/state/h-acceleration rates closed: `true/true/true`",
            "P_state primitive route closed by direct corollary: `false`",
            "D5_P_STATE_PS3_FULL_RESIDUAL_ROUTE_CERTIFICATE.md/json",
            "closes a strict direct-route PS3/state/h-acceleration corollary",
            "without closing the primitive/Taylor route or certifying primitive-route Taylor bounds",
            "96 non-dynamic rows",
            "KINEMATIC_ROW_DEFECT_CERTIFICATE.md/json",
            "NEWTON_EULER_DEFECT_OBLIGATION_GATE.md/json",
            "NEWTON_EULER_SYMBOLIC_TARGET_AUDIT.md/json",
            "active direct D5 route closed; symbolic/primitive D5 route remains open",
            "active_direct_newton_euler_open_obligation_count=0",
            "newton_euler_symbolic_primitive_open_obligation_count=1",
            "newton_euler_symbolic_primitive_open_obligation_scope=symbolic_primitive_certificate_route_not_active_direct_pc2",
            "132 runtime formula rows",
            "formula-row AD Jacobian oracle",
            "partial_formula_row_count=96",
            "full_formula_row_count=132",
            "formula_row_ad_jacobian_oracle=PASS",
            "formula_row_ad_jacobian_probe_count=3",
            "strict conditional residual-bridge proof boundary audit added",
            "CMAME_STRICT_PROOF_AUDIT.md/json",
            "direct_route_strict_residual_bridge_kantorovich_proof_complete=true",
            "symbolic_primitive_route_strict_implementation_proof_complete=false",
            "b1_ad_expanded_implementation_oracle_still_open_after_strict_proof_audit=false",
            "primitive_global_dynamic_symbolic_oracle_complete_after_strict_proof_audit=false",
            "B1",
            "B2",
            "B3",
            "B4",
            "B5",
            "B6",
            "B7",
            "B8",
            "proof-traceability prose pass started",
            "main-body machine-token removal pass completed",
            "comparison-theorem wording removed",
            "prose residue audit added",
            "limitation explanation figure integrated",
            "coarse baseline/work-precision figure integrated",
            "closed-loop coarse-dynamics diagnostic figure integrated",
            "method-stage architecture",
            "all-method result matrix figure integrated",
            "figure-set audit added",
            "validate_cmame_blocker_closure_gate.py",
        ],
        "CMAME_BLOCKER_CLOSURE_GATE.md",
    )
    checks.check(
        "- `submission_ready=True`" not in gate_md,
        "gate md must not contain an unscoped submission_ready=True marker",
    )
    require_tokens(
        checks,
        review,
        [
            "Status: **GLOBAL SUBMISSION OPEN; BOUNDED NARROWED SUBCHECK SATISFIED**",
            "do not submit globally yet",
            "bounded subsidiary subcheck",
            "### B1. Closed",
            "### B2.",
            "### B3.",
            "### B4.",
            "### B5.",
            "### B6.",
            "### B7.",
            "### B8.",
            "theorem traceability table",
            "reader-facing evidence",
            "proof numerical scale audit",
            "solver-scale audit",
            "smooth reference `max_linear_residual_norm=2.800513564816292e-13`",
            "PROOF_SOLVER_SCALED_TOLERANCE_PROBE.md/json/csv",
            "127.58372278641149",
            "theorem_level_scaled_tolerance_sweep_recorded=false",
            "CMAME_PROSE_RESIDUE_AUDIT.md/json",
            "finite-run order-six scale",
            "main-body machine-token removal pass",
            "main-body machine-token count is `0`",
            "conditional formal-order comparison language",
            "circular one-step perturbation shortcut",
            "theorem now decomposes the `O(h^7)` local",
            "partial independent formula-row oracle",
            "96 non-dynamic kinematic/lower-pair rows",
            "full independent formula-row oracle",
            "132 runtime formula rows",
            "multi-probe formula-row AD Jacobian oracle",
            "three deterministic stage vectors",
            "3.330669e-16",
            "newton_euler_weak_balance",
            "Figure 8",
            "Figure 9",
            "Figure 10",
            "Figure 11",
            "Figure 12",
            "accepted-method architecture schematic",
            "all-method all-example common-reference result matrix",
            "ALL_METHOD_EXAMPLE_CLAIM_DISPOSITION_AUDIT.md/json",
            "CMAME_FIGURE_SET_AUDIT.md/json",
            "44 order/error cells",
            "0/40` source-policy rows",
            "13 figures",
            "no full-TFE replacement",
            "order-acceptance policy table",
            "closed-loop coarse-dynamics Newton diagnostic evidence",
            "closed-loop coarse-dynamics diagnostic figure",
            "without introducing a new numerical campaign or a default `1e-4` policy",
            "5.955/5.955/6.085/5.971",
            "6.164/6.159/7.341/6.426",
            "no default `1e-4`",
            "closed-loop coarse-dynamics diagnostic rows",
            "external-suite comparison table",
            "EXTERNAL_SAME_TEST_RUN_QUEUE.md/json",
            "EXTERNAL_SAME_TEST_ACCEPTANCE_SHEET.md/json",
            "20 non-default-`1e-4`",
            "accepted_external_dynamic_order_examples=0",
            "external_superiority_claim=false",
            "limitation-figure part of B7",
            "all-method all-example result matrix",
            "13-figure audit",
            "coarse-first baseline comparison",
            "work/precision figure",
            "bounded_narrowed_subcheck_satisfied=true",
            "Legacy compatibility alias, not a global readiness marker:",
            "submission_ready_under_narrowed_claim=true",
            "quality_review_passed_under_narrowed_claim=true",
            "full_source_policy_submission_ready=false",
            "open_narrowed_claim_blockers=0",
            "closed_narrowed_claim_blockers=B1,B2,B3,B4,B5,B6,B7,B8",
        ],
        "CMAME_SUBMISSION_READINESS_REVIEW.md",
    )
    require_tokens(
        checks,
        hi2022_policy_decision_md,
        [
            "Status: **BOUNDED T=0.1 ROWS COMPLETE; FULL T=8 SOURCE POLICY OPEN**",
            "rows ok: `24/24`",
            "model/form groups with three h values: `8/8`",
            "accepted for external superiority: `False`",
            "source-policy dynamic-order examples: `0/4`",
            "It does not run any numerical shard",
        ],
        "HI2022_POLICY_DECISION_AUDIT.md",
    )
    require_tokens(
        checks,
        hi2022_source_policy_audit_md,
        [
            "Status: **bounded T=0.1 rows complete; full T=8 source-policy rows not closed**.",
            "Active B2 flagged HI2022 rows: `3`.",
            "Bounded rows ok: `24/24`.",
            "Bounded form/model groups complete: `8/8`.",
            "Full T=8 source policy completed: `False`.",
            "Source-policy reproduction rows: `0/3`.",
            "Can close HI2022 B2 requirement now: `False`.",
        ],
        "HI2022_SOURCE_POLICY_ROW_AUDIT.md",
    )
    require_tokens(
        checks,
        tfe_source_policy_audit_md,
        [
            "Status: **source policy spec extracted; runner rows not closed**.",
            "Active B2 flagged TFE rows: `0`.",
            "Source-policy spec extracted: `True`.",
            "Pendulum DAE runner implemented: `False`.",
            "Source-policy rows completed: `0`.",
            "Source-policy reproduction rows: `0/4`.",
            "Can close TFE B2 requirement now: `False`.",
        ],
        "TFE_SOURCE_POLICY_ROW_AUDIT.md",
    )
    require_tokens(
        checks,
        external_suite_demotion_md,
        [
            "Status: **all external source-policy suites explicitly demoted from external-superiority scope**",
            "B2 subrequirements closed by demotion",
            "vp2024_code_resolution_or_demotion",
            "hi2022_public_code_same_test_rows",
            "ra2021_public_code_same_test_rows",
            "original_tfe_pendulum_error_order_work_rows",
            "Demoted VP2024 source-policy rows/flagged rows: `4/3`",
            "Demoted HI2022 source-policy rows/flagged rows: `3/3`",
            "Demoted RA2021 source-policy rows/flagged rows: `5/5`",
            "Demoted TFE source-policy rows/flagged rows: `4/4`",
            "Active source-policy flagged rows after demotions: `0`",
            "These demotions are claim-boundary decisions, not numerical wins.",
        ],
        "EXTERNAL_SUITE_DEMOTION_LEDGER.md",
    )
    require_tokens(
        checks,
        b2_remaining_work_md,
        [
            "Status: `route_b_all_external_suites_demoted_no_active_external_superiority_rows`.",
            "Total flagged source-policy rows: `15`.",
            "Active flagged rows after Route B demotion: `0`.",
            "Demoted flagged rows after Route B demotion: `15`.",
            "Source-policy closed rows: `0`.",
            "External-superiority-ready rows: `0`.",
            "B2 closed by demotion: `['vp2024_code_resolution_or_demotion', 'hi2022_public_code_same_test_rows', 'ra2021_public_code_same_test_rows', 'original_tfe_pendulum_error_order_work_rows']`.",
            "External superiority claim allowed: `False`.",
            "The Route B demotions are claim-boundary decisions, not numerical wins.",
            "Route B B2/B4 claim-boundary synchronized: `True/True`.",
            "Route B B2/B4 closure ready pending gate sync: `False/False`.",
        ],
        "B2_SOURCE_POLICY_REMAINING_WORK_MANIFEST.md",
    )
    require_tokens(
        checks,
        ra2021_source_policy_audit_md,
        [
            "Status: **public rows complete; source-policy rows not closed**.",
            "Active B2 flagged RA2021 rows: `0`.",
            "Public order groups completed: `12/12`.",
            "Public timing rows completed: `12/12`.",
            "Fixed-grid common-reference RA2021 rows: `12/12`.",
            "Paper-safe common-reference RA2021 rows: `12/12`.",
            "Source-policy reproduction rows: `0/12`.",
            "Source-policy closed rows: `0`.",
            "External-superiority-ready rows: `0`.",
            "Can close RA2021 B2 requirement now: `False`.",
            "The RA2021 rows remain bounded common-reference diagnostics, not external-superiority evidence.",
        ],
        "RA2021_SOURCE_POLICY_ROW_AUDIT.md",
    )
    require_tokens(
        checks,
        audit,
        [
            "legacy compatibility alias only, not global readiness:",
            "submission_ready_under_narrowed_claim=true",
            "mechanical_preflight_passed=true",
            "quality_review_passed_under_narrowed_claim=true",
            "full_source_policy_submission_ready=false",
            "CMAME_SUBMISSION_READINESS_REVIEW.md",
            "CMAME_VISUAL_LEGIBILITY_AUDIT.md",
            "CMAME_RELATED_WORK_AUDIT.md",
        ],
        "CMAME_SUBMISSION_READINESS_AUDIT.md",
    )
    require_tokens(
        checks,
        visual_audit,
        [
            "Status: **B5 CLOSED - MECHANISM VISUAL REPRODUCIBILITY CHECKED**",
            "`open_blockers=7`",
            "`closed_blockers=B5`",
            "`default_1e-4_required=false`",
        ],
        "CMAME_VISUAL_LEGIBILITY_AUDIT.md",
    )
    require_tokens(
        checks,
        related_work_audit,
        [
            "Status: **B8 CLOSED - RELATED-WORK DEPTH CHECKED**",
            "Legacy compatibility alias only, not global readiness:",
            "These markers describe the bounded narrowed-claim subcheck only; they do not",
            "override `submission_ready=false` or close OC4/OC6/OC12.",
            "`open_narrowed_claim_blockers=0`",
            "`closed_narrowed_claim_blockers=B1,B2,B3,B4,B5,B6,B7,B8`",
            "`default_1e-4_required=false`",
        ],
        "CMAME_RELATED_WORK_AUDIT.md",
    )
    require_tokens(
        checks,
        proof_solver_scale_audit,
        [
            "Proof Solver Scale Audit",
            "SUMMARY-LEVEL SOLVER RESIDUALS RECORDED - NOT A SCALED ETA_H PROOF",
            "2.800513564816292e-13",
            "3584.657362964853",
            "finite scaled-tolerance probe",
            "127.58372278641149",
            "theorem_level_scaled_tolerance_sweep_recorded=false",
            "eta_h_O_h7_solver_policy_evidence=false",
            "run_v047_invoked=false",
        ],
        "PROOF_SOLVER_SCALE_AUDIT.md",
    )
    require_tokens(
        checks,
        newton_euler_obligation_md,
        [
            "Newton-Euler Defect Obligation Gate",
            "D5 SYMBOLIC/PRIMITIVE ROUTE OPEN; ACTIVE DIRECT PC2 CLOSED - NOT SUBMISSION READY",
            "Symbolic/primitive-route open obligation count: `1`",
            "Active direct PC2 closed: `True`",
            "Closed obligation count: `5`",
            "translational_balance_identity",
            "rotational_balance_identity",
            "multiplier_wrench_consistency",
            "smooth_force_lift_consistency",
            "gauss_stage_dynamic_defect_rate",
            "symbolic_runtime_row_equivalence",
            "default_1e-4_required=false",
        ],
        "NEWTON_EULER_DEFECT_OBLIGATION_GATE.md",
    )
    require_tokens(
        checks,
        newton_euler_symbolic_target_md,
        [
            "Newton-Euler Symbolic Target Audit",
            "row-level symbolic targets extracted; dynamic defect proof open",
            "Dynamic rows: `36`",
            "Translational/rotational rows: `18/18`",
            "Symbolic target inventory complete: `True`",
            "Newton-Euler symbolic defect certificate complete: `False`",
            "Stage residual O(h^7) implementation defect proved: `False`",
            "Dynamic symbolic oracle complete: `False`",
        ],
        "NEWTON_EULER_SYMBOLIC_TARGET_AUDIT.md",
    )
    require_tokens(
        checks,
        prose_residue_audit,
        [
            "Status: **B6 CLOSED - MAIN-BODY MACHINE TOKENS REMOVED AND NARROWED CLAIM PROSE FINALIZED**",
            "main-body machine-token count: `0`",
            "appendix artifact macro count: `0`",
            "source-package summary",
            "`default_1e-4_required=false`",
            "`run_v047_invoked=false`",
            "`submission_ready=false`",
        ],
        "CMAME_PROSE_RESIDUE_AUDIT.md",
    )

    checks.check(manifest.get("cmame_blocker_closure_gate") == "CMAME_BLOCKER_CLOSURE_GATE.md", "manifest blocker gate path missing")
    checks.check(manifest.get("cmame_blocker_closure_gate_json") == "CMAME_BLOCKER_CLOSURE_GATE.json", "manifest blocker gate JSON path missing")
    checks.check(manifest.get("cmame_external_baseline_gate") == "CMAME_EXTERNAL_BASELINE_GATE.md", "manifest external baseline gate path missing")
    checks.check(manifest.get("cmame_external_baseline_gate_json") == "CMAME_EXTERNAL_BASELINE_GATE.json", "manifest external baseline gate JSON path missing")
    checks.check(
        manifest.get("comparison_objective_closure_reconciliation_audit")
        == "COMPARISON_OBJECTIVE_CLOSURE_RECONCILIATION_AUDIT.md",
        "manifest comparison reconciliation audit path missing",
    )
    checks.check(
        manifest.get("comparison_objective_closure_reconciliation_audit_json")
        == "COMPARISON_OBJECTIVE_CLOSURE_RECONCILIATION_AUDIT.json",
        "manifest comparison reconciliation audit JSON path missing",
    )
    checks.check(
        manifest.get("source_policy_closure_triage") == "SOURCE_POLICY_CLOSURE_TRIAGE.md",
        "manifest source-policy closure triage path missing",
    )
    checks.check(
        manifest.get("source_policy_closure_triage_json") == "SOURCE_POLICY_CLOSURE_TRIAGE.json",
        "manifest source-policy closure triage JSON path missing",
    )
    checks.check(
        manifest.get("all_examples_source_policy_audit") == "ALL_EXAMPLES_SOURCE_POLICY_AUDIT.md",
        "manifest all-example source-policy audit path missing",
    )
    checks.check(
        manifest.get("all_examples_source_policy_audit_json") == "ALL_EXAMPLES_SOURCE_POLICY_AUDIT.json",
        "manifest all-example source-policy audit JSON path missing",
    )
    checks.check(
        manifest.get("all_method_example_claim_disposition_audit") == "ALL_METHOD_EXAMPLE_CLAIM_DISPOSITION_AUDIT.md",
        "manifest all-method claim-disposition audit path missing",
    )
    checks.check(
        manifest.get("all_method_example_claim_disposition_audit_json") == "ALL_METHOD_EXAMPLE_CLAIM_DISPOSITION_AUDIT.json",
        "manifest all-method claim-disposition audit JSON path missing",
    )
    checks.check(manifest.get("cmame_figure_set_audit") == "CMAME_FIGURE_SET_AUDIT.md", "manifest figure-set audit path missing")
    checks.check(
        manifest.get("cmame_figure_set_audit_json") == "CMAME_FIGURE_SET_AUDIT.json",
        "manifest figure-set audit JSON path missing",
    )
    checks.check(
        manifest.get("external_same_test_acceptance_sheet") == "EXTERNAL_SAME_TEST_ACCEPTANCE_SHEET.md",
        "manifest external same-test acceptance sheet path missing",
    )
    checks.check(
        manifest.get("external_same_test_acceptance_sheet_json") == "EXTERNAL_SAME_TEST_ACCEPTANCE_SHEET.json",
        "manifest external same-test acceptance sheet JSON path missing",
    )
    checks.check(manifest.get("cmame_visual_legibility_audit") == "CMAME_VISUAL_LEGIBILITY_AUDIT.md", "manifest visual audit path missing")
    checks.check(manifest.get("cmame_visual_legibility_audit_json") == "CMAME_VISUAL_LEGIBILITY_AUDIT.json", "manifest visual audit JSON path missing")
    checks.check(manifest.get("cmame_related_work_audit") == "CMAME_RELATED_WORK_AUDIT.md", "manifest related-work audit path missing")
    checks.check(manifest.get("cmame_related_work_audit_json") == "CMAME_RELATED_WORK_AUDIT.json", "manifest related-work audit JSON path missing")
    checks.check(manifest.get("cmame_prose_residue_audit") == "CMAME_PROSE_RESIDUE_AUDIT.md", "manifest prose-residue audit path missing")
    checks.check(manifest.get("cmame_prose_residue_audit_json") == "CMAME_PROSE_RESIDUE_AUDIT.json", "manifest prose-residue audit JSON path missing")
    checks.check("CMAME_BLOCKER_CLOSURE_GATE.md" in manifest.get("evidence_anchors", []), "manifest blocker gate anchor missing")
    checks.check("CMAME_BLOCKER_CLOSURE_GATE.json" in manifest.get("evidence_anchors", []), "manifest blocker gate JSON anchor missing")
    checks.check("CMAME_EXTERNAL_BASELINE_GATE.md" in manifest.get("evidence_anchors", []), "manifest external baseline gate anchor missing")
    checks.check("CMAME_EXTERNAL_BASELINE_GATE.json" in manifest.get("evidence_anchors", []), "manifest external baseline gate JSON anchor missing")
    checks.check(
        "COMPARISON_OBJECTIVE_CLOSURE_RECONCILIATION_AUDIT.md" in manifest.get("evidence_anchors", []),
        "manifest comparison reconciliation anchor missing",
    )
    checks.check(
        "COMPARISON_OBJECTIVE_CLOSURE_RECONCILIATION_AUDIT.json" in manifest.get("evidence_anchors", []),
        "manifest comparison reconciliation JSON anchor missing",
    )
    checks.check(
        "SOURCE_POLICY_CLOSURE_TRIAGE.md" in manifest.get("evidence_anchors", []),
        "manifest source-policy closure triage anchor missing",
    )
    checks.check(
        "SOURCE_POLICY_CLOSURE_TRIAGE.json" in manifest.get("evidence_anchors", []),
        "manifest source-policy closure triage JSON anchor missing",
    )
    checks.check(
        "ALL_EXAMPLES_SOURCE_POLICY_AUDIT.md" in manifest.get("evidence_anchors", []),
        "manifest all-example source-policy audit anchor missing",
    )
    checks.check(
        "ALL_EXAMPLES_SOURCE_POLICY_AUDIT.json" in manifest.get("evidence_anchors", []),
        "manifest all-example source-policy audit JSON anchor missing",
    )
    checks.check(
        "ALL_METHOD_EXAMPLE_CLAIM_DISPOSITION_AUDIT.md" in manifest.get("evidence_anchors", []),
        "manifest all-method claim-disposition audit anchor missing",
    )
    checks.check(
        "ALL_METHOD_EXAMPLE_CLAIM_DISPOSITION_AUDIT.json" in manifest.get("evidence_anchors", []),
        "manifest all-method claim-disposition audit JSON anchor missing",
    )
    checks.check("CMAME_FIGURE_SET_AUDIT.md" in manifest.get("evidence_anchors", []), "manifest figure-set audit anchor missing")
    checks.check("CMAME_FIGURE_SET_AUDIT.json" in manifest.get("evidence_anchors", []), "manifest figure-set audit JSON anchor missing")
    checks.check(
        "EXTERNAL_SAME_TEST_ACCEPTANCE_SHEET.md" in manifest.get("evidence_anchors", []),
        "manifest external same-test acceptance sheet anchor missing",
    )
    checks.check(
        "EXTERNAL_SAME_TEST_ACCEPTANCE_SHEET.json" in manifest.get("evidence_anchors", []),
        "manifest external same-test acceptance sheet JSON anchor missing",
    )
    checks.check(
        "EXTERNAL_SOURCE_POLICY_CLOSURE_MANIFEST.md" in manifest.get("evidence_anchors", []),
        "manifest external source-policy closure manifest anchor missing",
    )
    checks.check(
        "EXTERNAL_SOURCE_POLICY_CLOSURE_MANIFEST.json" in manifest.get("evidence_anchors", []),
        "manifest external source-policy closure manifest JSON anchor missing",
    )
    checks.check(
        "EXTERNAL_CASE_EVIDENCE_RECONCILIATION.md" in manifest.get("evidence_anchors", []),
        "manifest external case reconciliation anchor missing",
    )
    checks.check(
        "EXTERNAL_CASE_EVIDENCE_RECONCILIATION.json" in manifest.get("evidence_anchors", []),
        "manifest external case reconciliation JSON anchor missing",
    )
    checks.check("HI2022_POLICY_DECISION_AUDIT.md" in manifest.get("evidence_anchors", []), "manifest HI2022 policy-decision audit anchor missing")
    checks.check(
        "HI2022_POLICY_DECISION_AUDIT.json" in manifest.get("evidence_anchors", []),
        "manifest HI2022 policy-decision audit JSON anchor missing",
    )
    checks.check(
        "HI2022_SOURCE_POLICY_ROW_AUDIT.md" in manifest.get("evidence_anchors", []),
        "manifest HI2022 source-policy row audit anchor missing",
    )
    checks.check(
        "HI2022_SOURCE_POLICY_ROW_AUDIT.json" in manifest.get("evidence_anchors", []),
        "manifest HI2022 source-policy row audit JSON anchor missing",
    )
    checks.check("EXTERNAL_SUITE_DEMOTION_LEDGER.md" in manifest.get("evidence_anchors", []), "manifest external suite demotion ledger anchor missing")
    checks.check(
        "EXTERNAL_SUITE_DEMOTION_LEDGER.json" in manifest.get("evidence_anchors", []),
        "manifest external suite demotion ledger JSON anchor missing",
    )
    checks.check("TFE_SOURCE_POLICY_SPEC.md" in manifest.get("evidence_anchors", []), "manifest TFE source-policy spec anchor missing")
    checks.check("TFE_SOURCE_POLICY_SPEC.json" in manifest.get("evidence_anchors", []), "manifest TFE source-policy spec JSON anchor missing")
    checks.check(
        "TFE_SOURCE_POLICY_ROW_AUDIT.md" in manifest.get("evidence_anchors", []),
        "manifest TFE source-policy row audit anchor missing",
    )
    checks.check(
        "TFE_SOURCE_POLICY_ROW_AUDIT.json" in manifest.get("evidence_anchors", []),
        "manifest TFE source-policy row audit JSON anchor missing",
    )
    checks.check(
        "TFE_B4_B7_SOURCE_POLICY_DEMOTION_AUDIT.md" in manifest.get("evidence_anchors", []),
        "manifest TFE B4/B7 source-policy demotion audit anchor missing",
    )
    checks.check(
        "TFE_B4_B7_SOURCE_POLICY_DEMOTION_AUDIT.json" in manifest.get("evidence_anchors", []),
        "manifest TFE B4/B7 source-policy demotion audit JSON anchor missing",
    )
    checks.check("CMAME_PROOF_CONTRACT_GATE.md" in manifest.get("evidence_anchors", []), "manifest proof contract gate anchor missing")
    checks.check("CMAME_PROOF_CONTRACT_GATE.json" in manifest.get("evidence_anchors", []), "manifest proof contract gate JSON anchor missing")
    checks.check("PROOF_CLOSURE_MANIFEST.md" in manifest.get("evidence_anchors", []), "manifest proof closure anchor missing")
    checks.check("PROOF_CLOSURE_MANIFEST.json" in manifest.get("evidence_anchors", []), "manifest proof closure JSON anchor missing")
    checks.check("CMAME_VISUAL_LEGIBILITY_AUDIT.md" in manifest.get("evidence_anchors", []), "manifest visual audit anchor missing")
    checks.check("CMAME_VISUAL_LEGIBILITY_AUDIT.json" in manifest.get("evidence_anchors", []), "manifest visual audit JSON anchor missing")
    checks.check("CMAME_RELATED_WORK_AUDIT.md" in manifest.get("evidence_anchors", []), "manifest related-work audit anchor missing")
    checks.check("CMAME_RELATED_WORK_AUDIT.json" in manifest.get("evidence_anchors", []), "manifest related-work audit JSON anchor missing")
    checks.check("PROOF_SOLVER_SCALE_AUDIT.md" in manifest.get("evidence_anchors", []), "manifest proof solver-scale audit anchor missing")
    checks.check("PROOF_SOLVER_SCALE_AUDIT.json" in manifest.get("evidence_anchors", []), "manifest proof solver-scale audit JSON anchor missing")
    checks.check("PROOF_SOLVER_SCALED_TOLERANCE_PROBE.md" in manifest.get("evidence_anchors", []), "manifest proof solver scaled-tolerance probe anchor missing")
    checks.check("PROOF_SOLVER_SCALED_TOLERANCE_PROBE.json" in manifest.get("evidence_anchors", []), "manifest proof solver scaled-tolerance probe JSON anchor missing")
    checks.check("PROOF_SOLVER_SCALED_TOLERANCE_PROBE.csv" in manifest.get("evidence_anchors", []), "manifest proof solver scaled-tolerance probe CSV anchor missing")
    checks.check("CMAME_PROSE_RESIDUE_AUDIT.md" in manifest.get("evidence_anchors", []), "manifest prose-residue audit anchor missing")
    checks.check("CMAME_PROSE_RESIDUE_AUDIT.json" in manifest.get("evidence_anchors", []), "manifest prose-residue audit JSON anchor missing")
    checks.check("DYNAMIC_ROW_ORACLE_GATE.md" in manifest.get("evidence_anchors", []), "manifest dynamic row oracle anchor missing")
    checks.check("DYNAMIC_ROW_ORACLE_GATE.json" in manifest.get("evidence_anchors", []), "manifest dynamic row oracle JSON anchor missing")
    checks.check(
        "KINEMATIC_ROW_DEFECT_CERTIFICATE.md" in manifest.get("evidence_anchors", []),
        "manifest kinematic row defect certificate anchor missing",
    )
    checks.check(
        "KINEMATIC_ROW_DEFECT_CERTIFICATE.json" in manifest.get("evidence_anchors", []),
        "manifest kinematic row defect certificate JSON anchor missing",
    )
    checks.check(
        "NEWTON_EULER_DEFECT_OBLIGATION_GATE.md" in manifest.get("evidence_anchors", []),
        "manifest Newton-Euler obligation gate anchor missing",
    )
    checks.check(
        "NEWTON_EULER_DEFECT_OBLIGATION_GATE.json" in manifest.get("evidence_anchors", []),
        "manifest Newton-Euler obligation gate JSON anchor missing",
    )
    checks.check(
        "NEWTON_EULER_SYMBOLIC_TARGET_AUDIT.md" in manifest.get("evidence_anchors", []),
        "manifest Newton-Euler symbolic target audit anchor missing",
    )
    checks.check(
        "NEWTON_EULER_SYMBOLIC_TARGET_AUDIT.json" in manifest.get("evidence_anchors", []),
        "manifest Newton-Euler symbolic target audit JSON anchor missing",
    )
    checks.check(
        "v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_strict_common_reference.json"
        in manifest.get("evidence_anchors", []),
        "manifest strict common-reference anchor missing",
    )
    checks.check("validate_cmame_blocker_closure_gate.py" in manifest.get("validators", []), "manifest blocker gate validator missing")
    checks.check("validate_cmame_external_baseline_gate.py" in manifest.get("validators", []), "manifest external baseline validator missing")
    checks.check(
        "validate_comparison_objective_closure_reconciliation_audit.py" in manifest.get("validators", []),
        "manifest comparison reconciliation validator missing",
    )
    checks.check(
        "validate_source_policy_closure_triage.py" in manifest.get("validators", []),
        "manifest source-policy closure triage validator missing",
    )
    checks.check(
        "validate_all_examples_source_policy_audit.py" in manifest.get("validators", []),
        "manifest all-example source-policy audit validator missing",
    )
    checks.check(
        "validate_all_method_example_claim_disposition_audit.py" in manifest.get("validators", []),
        "manifest all-method claim-disposition audit validator missing",
    )
    checks.check(
        "validate_cmame_figure_set_audit.py" in manifest.get("validators", []),
        "manifest figure-set audit validator missing",
    )
    checks.check(
        "validate_external_same_test_acceptance_sheet.py" in manifest.get("validators", []),
        "manifest external same-test acceptance sheet validator missing",
    )
    checks.check(
        "validate_external_source_policy_closure_manifest.py" in manifest.get("validators", []),
        "manifest external source-policy closure manifest validator missing",
    )
    checks.check(
        "validate_external_case_evidence_reconciliation.py" in manifest.get("validators", []),
        "manifest external case reconciliation validator missing",
    )
    checks.check(
        manifest.get("hi2022_policy_decision_audit") == "HI2022_POLICY_DECISION_AUDIT.md",
        "manifest HI2022 policy-decision audit missing",
    )
    checks.check(
        manifest.get("hi2022_policy_decision_audit_json") == "HI2022_POLICY_DECISION_AUDIT.json",
        "manifest HI2022 policy-decision audit JSON missing",
    )
    checks.check(
        "validate_hi2022_policy_decision_audit.py" in manifest.get("validators", []),
        "manifest HI2022 policy-decision validator missing",
    )
    checks.check(
        manifest.get("hi2022_source_policy_row_audit") == "HI2022_SOURCE_POLICY_ROW_AUDIT.md",
        "manifest HI2022 source-policy row audit missing",
    )
    checks.check(
        manifest.get("hi2022_source_policy_row_audit_json") == "HI2022_SOURCE_POLICY_ROW_AUDIT.json",
        "manifest HI2022 source-policy row audit JSON missing",
    )
    checks.check(
        "validate_hi2022_source_policy_row_audit.py" in manifest.get("validators", []),
        "manifest HI2022 source-policy row audit validator missing",
    )
    checks.check(
        manifest.get("external_suite_demotion_ledger") == "EXTERNAL_SUITE_DEMOTION_LEDGER.md",
        "manifest external suite demotion ledger missing",
    )
    checks.check(
        manifest.get("external_suite_demotion_ledger_json") == "EXTERNAL_SUITE_DEMOTION_LEDGER.json",
        "manifest external suite demotion ledger JSON missing",
    )
    checks.check(
        "validate_external_suite_demotion_ledger.py" in manifest.get("validators", []),
        "manifest external suite demotion validator missing",
    )
    checks.check(
        manifest.get("tfe_source_policy_row_audit") == "TFE_SOURCE_POLICY_ROW_AUDIT.md",
        "manifest TFE source-policy row audit missing",
    )
    checks.check(
        manifest.get("tfe_source_policy_row_audit_json") == "TFE_SOURCE_POLICY_ROW_AUDIT.json",
        "manifest TFE source-policy row audit JSON missing",
    )
    checks.check(
        manifest.get("tfe_b4_b7_source_policy_demotion_audit") == "TFE_B4_B7_SOURCE_POLICY_DEMOTION_AUDIT.md",
        "manifest TFE B4/B7 source-policy demotion audit missing",
    )
    checks.check(
        manifest.get("tfe_b4_b7_source_policy_demotion_audit_json")
        == "TFE_B4_B7_SOURCE_POLICY_DEMOTION_AUDIT.json",
        "manifest TFE B4/B7 source-policy demotion audit JSON missing",
    )
    checks.check(
        manifest.get("newton_euler_symbolic_target_audit") == "NEWTON_EULER_SYMBOLIC_TARGET_AUDIT.md",
        "manifest Newton-Euler symbolic target audit missing",
    )
    checks.check(
        manifest.get("newton_euler_symbolic_target_audit_json") == "NEWTON_EULER_SYMBOLIC_TARGET_AUDIT.json",
        "manifest Newton-Euler symbolic target audit JSON missing",
    )
    checks.check("validate_tfe_source_policy_spec.py" in manifest.get("validators", []), "manifest TFE source-policy validator missing")
    checks.check(
        "validate_tfe_source_policy_row_audit.py" in manifest.get("validators", []),
        "manifest TFE source-policy row audit validator missing",
    )
    checks.check(
        "validate_tfe_b4_b7_source_policy_demotion_audit.py" in manifest.get("validators", []),
        "manifest TFE B4/B7 source-policy demotion audit validator missing",
    )
    checks.check("validate_cmame_proof_contract_gate.py" in manifest.get("validators", []), "manifest proof contract validator missing")
    checks.check("validate_proof_closure_manifest.py" in manifest.get("validators", []), "manifest proof closure validator missing")
    checks.check("validate_cmame_visual_legibility_audit.py" in manifest.get("validators", []), "manifest visual audit validator missing")
    checks.check("validate_cmame_related_work_audit.py" in manifest.get("validators", []), "manifest related-work audit validator missing")
    checks.check("validate_proof_solver_scale_audit.py" in manifest.get("validators", []), "manifest proof solver-scale audit validator missing")
    checks.check("validate_proof_solver_scaled_tolerance_probe.py" in manifest.get("validators", []), "manifest proof solver scaled-tolerance probe validator missing")
    checks.check("validate_cmame_prose_residue_audit.py" in manifest.get("validators", []), "manifest prose-residue audit validator missing")
    checks.check("validate_dynamic_row_oracle_gate.py" in manifest.get("validators", []), "manifest dynamic row oracle validator missing")
    checks.check(
        "validate_kinematic_row_defect_certificate.py" in manifest.get("validators", []),
        "manifest kinematic row defect certificate validator missing",
    )
    checks.check(
        "validate_newton_euler_defect_obligation_gate.py" in manifest.get("validators", []),
        "manifest Newton-Euler obligation gate validator missing",
    )
    checks.check(
        "validate_newton_euler_symbolic_target_audit.py" in manifest.get("validators", []),
        "manifest Newton-Euler symbolic target audit validator missing",
    )

    checks.check(
        set(gate.get("forbidden_claims", []))
        == {
            "same_test_campaign_passed",
            "external_superiority_claim_true",
            "source_policy_rows_promoted_true",
            "source_policy_work_precision_claim_true",
            "default_1e-4_required",
        },
        "forbidden-claim guard changed",
    )

    if checks.errors:
        print("cmame_blocker_closure_gate=FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("cmame_blocker_closure_gate=PASS")
    print("open_narrowed_claim_blockers=0")
    print("closed_blockers=B1,B2,B3,B4,B5,B6,B7,B8")
    print("submission_ready_under_narrowed_claim=True")
    print("narrowed_claim_alias_warning=validator_only_not_global_submission_ready")
    print("full_source_policy_submission_ready=False")
    print("mechanical_preflight_passed=True")
    print("quality_review_passed_under_narrowed_claim=True")
    print("same_test_campaign_status=not_run")
    print("external_superiority_claim=False")
    print("comparison_matrix_closed=True")
    print("common_reference_examples=single_pendulum,double_pendulum,four_link,slider_crank")
    print("common_reference_cells=44")
    print("raw_rows_recomputed=132")
    print("summary_mismatches=0")
    print("direct_nonlocal_order_wins=40/40")
    print("direct_nonlocal_error_wins=40/40")
    print("all_method_claim_disposition_cells=44")
    print("all_method_claim_disposition_nonlocal_cells=40")
    print("all_method_source_policy_closed_open=0/40")
    print("all_method_strict_external_error_claim_rows=0")
    print("figure_set_audit=13/13")
    print("figure12_all_method_matrix_integrated=True")
    print("figure13_work_precision_compendium_integrated=True")
    print("source_policy_flagged_rows=15")
    print("source_policy_velocity_mismatch_rows=10")
    print("source_policy_superiority_claim_allowed=False")
    print("b2_b4_can_close_now=False")
    print("default_1e-4=False")
    print("accepted_external_dynamic_order_examples=0")
    print("parallel_shard_count_without_default_1e-4=20")
    print("partial_formula_row_count=96")
    print("partial_kinematic_stage_defect_certificate_checked=True")
    print("partial_kinematic_stage_defect_rows=96")
    print("newton_euler_defect_obligation_gate_checked=True")
    print("active_direct_newton_euler_open_obligation_count=0")
    print("newton_euler_symbolic_primitive_open_obligation_count=1")
    print("newton_euler_symbolic_primitive_open_obligation_scope=symbolic_primitive_certificate_route_not_active_direct_pc2")
    print("newton_euler_defect_closed_obligation_count=5")
    print("newton_euler_symbolic_target_audit_checked=True")
    print("newton_euler_symbolic_target_rows=36")
    print("newton_euler_symbolic_target_translational_rotational_rows=18/18")
    print("newton_euler_symbolic_defect_certificate_complete=False")
    print("full_formula_row_count=132")
    print("formula_row_ad_jacobian_oracle=PASS")
    print("formula_row_ad_jacobian_probe_count=3")
    print("summary_level_solver_residuals_recorded=True")
    print("scaled_tolerance_sweep_recorded=False")
    print("main_body_machine_token_count=0")
    print("artifact_macro_confined_to_appendix=True")
    print("appendix_artifact_macro_count=0")
    print("coarse_first_ready_examples=2/4")
    print("local_evidence_coverage_examples=4/4")
    print("accepted_method_dynamic_order_examples=single_pendulum,double_pendulum")
    print("source_policy_dynamic_order_examples=0/4")
    print("accepted_dynamic_order_examples=single_pendulum,double_pendulum")
    print("coverage_only_examples=four_link,slider_crank")
    print("local_closed_loop_dynamic_order_candidates=2")
    print("four_link_true_dynamic_primary_orders=5.955/5.955/6.085/5.971")
    print("slider_crank_true_dynamic_primary_orders=6.164/6.159/7.341/6.426")
    print("strict_common_reference_available_examples=four_link,slider_crank")
    print("strict_common_reference_gap_examples=none")
    print("strict_common_reference_figure_integrated_in_manuscript=True")
    return 0


if __name__ == "__main__":
    sys.exit(main())
