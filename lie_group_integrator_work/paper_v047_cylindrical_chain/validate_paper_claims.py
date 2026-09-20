#!/usr/bin/env python3
"""Read-only consistency checks for the v047 paper draft.

The goal is not to rerun simulations. This script verifies that the paper's
headline claims remain synchronized with the generated v047 artifacts.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


PAPER = Path(__file__).resolve().parent
ROOT = PAPER.parent
PIPELINE = ROOT / "v047_cylindrical_chain_pipeline"
RESULTS = PIPELINE / "results"

EXPECTED_ASME_STATUS = "four_asme_method_rows_accepted_projection_sharp_sparse_caveats"
EXPECTED_MODELS = {
    "single_pendulum",
    "double_pendulum",
    "four_link",
    "slider_crank",
}
EXPECTED_DYNAMIC_ORDER_MODELS = {"single_pendulum", "double_pendulum"}
EXPECTED_COVERAGE_ONLY_MODELS = {"four_link", "slider_crank"}
EXPECTED_MAPPING_STATUS = {
    "single_pendulum": "exact_driven_absolute_fullva_residual",
    "double_pendulum": "accepted_method_side_double_revolute_fullva_reference_policy",
    "four_link": "accepted_closed_loop_kinematic_fullva_reaction_dynamics",
    "slider_crank": "accepted_closed_loop_kinematic_fullva_reaction_dynamics",
}
EXPECTED_REMAINING_CAVEATS = {
    "sparse_speed_quantified",
    "full_tfe_stage_replacement_missing",
    "sharp_friction_coarse_order_reduction_ultra_recovered",
}


class Checks:
    def __init__(self) -> None:
        self.errors: list[str] = []

    def check(self, condition: bool, message: str) -> None:
        if not condition:
            self.errors.append(message)


def read_text(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(path)
    return path.read_text()


def read_json(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(path)
    with path.open() as handle:
        return json.load(handle)


def contains_normalized(text: str, token: str) -> bool:
    return token in text or " ".join(token.split()) in " ".join(text.split())


def read_summary() -> dict:
    return read_json(RESULTS / "summary_v047.json")


def rounded(value: float, digits: int = 3) -> str:
    return f"{value:.{digits}f}"


def sci(value: float, digits: int = 3) -> str:
    return f"{value:.{digits}e}"


def latex_sci(value: float, digits: int = 3) -> str:
    mantissa, exponent = sci(value, digits).split("e")
    return f"{mantissa}\\times10^{{{int(exponent)}}}"


def check_asme_claim(checks: Checks, summary: dict, tex: str) -> None:
    asme = summary.get("asme_gate", {})
    checks.check(asme.get("status") == EXPECTED_ASME_STATUS, "summary ASME gate status changed")
    checks.check(EXPECTED_ASME_STATUS in tex, "paper does not include the current ASME gate status")
    models = asme.get("models", {})
    checks.check(set(models) == EXPECTED_MODELS, f"paper ASME model set mismatch: {sorted(models)}")
    for model, expected in EXPECTED_MAPPING_STATUS.items():
        actual = models.get(model, {}).get("v047_mapping_status")
        checks.check(actual == expected, f"{model} mapping status is {actual!r}, expected {expected!r}")
        checks.check(model.replace("_", " ") in tex or model in tex, f"paper does not mention {model}")


def check_asme_quantitative_claim(checks: Checks, summary: dict, tex: str, readme: str) -> None:
    runs = summary["asme_gate"]["method_runs"]
    single = runs["single_pendulum_driven_absolute_fullva"]
    single_min_order = rounded(
        min(
            float(single["position_observed_order"]),
            float(single["velocity_observed_order"]),
            float(single["orientation_observed_order"]),
            float(single["omega_observed_order"]),
        )
    )
    double = runs["double_pendulum"]
    double_min_order = rounded(
        min(
            float(double["orientation_observed_order"]),
            float(double["omega_observed_order"]),
        )
    )
    closed = runs["closed_loop_kinematic_fullva"]["models"]
    four = closed["four_link"]
    slider = closed["slider_crank"]
    four_max_constraint_value = max(
        float(four["max_position_constraint_norm"]),
        float(four["max_velocity_constraint_norm"]),
        float(four["max_acceleration_constraint_norm"]),
    )
    four_max_constraint = sci(four_max_constraint_value)
    four_max_constraint_tex = latex_sci(four_max_constraint_value)
    slider_max_constraint_value = max(
        float(slider["max_position_constraint_norm"]),
        float(slider["max_velocity_constraint_norm"]),
        float(slider["max_acceleration_constraint_norm"]),
    )
    slider_max_constraint = sci(slider_max_constraint_value)
    slider_max_constraint_tex = latex_sci(slider_max_constraint_value)
    reactions = runs["closed_loop_reaction_dynamics"]["models"]
    four_reaction = sci(float(reactions["four_link"]["max_dynamics_residual_norm"]))
    four_reaction_tex = latex_sci(float(reactions["four_link"]["max_dynamics_residual_norm"]))
    slider_reaction = sci(float(reactions["slider_crank"]["max_dynamics_residual_norm"]))
    slider_reaction_tex = latex_sci(float(reactions["slider_crank"]["max_dynamics_residual_norm"]))
    single_stage_residual = sci(float(single["max_stage_residual_norm"]))
    single_stage_residual_tex = latex_sci(float(single["max_stage_residual_norm"]))
    double_pos_constraint = sci(float(double["max_endpoint_constraint_norm"]))
    double_pos_constraint_tex = latex_sci(float(double["max_endpoint_constraint_norm"]))
    double_vel_constraint = sci(float(double["max_endpoint_velocity_constraint_norm"]))
    double_vel_constraint_tex = latex_sci(float(double["max_endpoint_velocity_constraint_norm"]))

    required_tex = [
        "Quantitative evidence behind the accepted four-example gate",
        single_min_order,
        single_stage_residual_tex,
        double_min_order,
        double_pos_constraint_tex,
        double_vel_constraint_tex,
        four_max_constraint_tex,
        four_reaction_tex,
        slider_max_constraint_tex,
        slider_reaction_tex,
    ]
    for text in required_tex:
        checks.check(text in tex, f"paper is missing ASME quantitative evidence: {text}")

    for text in [
        single_min_order,
        double_min_order,
        four_max_constraint,
        four_reaction,
    ]:
        checks.check(text in readme, f"paper README is missing ASME quantitative evidence: {text}")

    # Keep these variables explicitly used in the readme/text checks above so
    # future edits cannot silently drop the numeric evidence.
    _ = (
        slider_max_constraint,
        slider_reaction,
        single_stage_residual,
        double_pos_constraint,
        double_vel_constraint,
    )

def check_convergence_claim(checks: Checks, summary: dict, tex: str) -> tuple[str, str]:
    smooth = summary["convergence"]["cases"]["cylindrical_smooth"]["projected_velocity"]
    sharp = summary["convergence"]["cases"]["cylindrical_sharp"]["projected_velocity"]
    smooth_pos = rounded(float(smooth["position_order"]))
    smooth_vel = rounded(float(smooth["velocity_order"]))
    sharp_pos = rounded(float(sharp["position_order"]))
    sharp_vel = rounded(float(sharp["velocity_order"]))
    for value, label in [
        (smooth_pos, "smooth position order"),
        (smooth_vel, "smooth velocity order"),
        (sharp_pos, "sharp position order"),
        (sharp_vel, "sharp velocity order"),
    ]:
        checks.check(value in tex, f"paper is missing {label} value {value}")
    checks.check(smooth["h_values"] == [0.04, 0.02, 0.01], "smooth h-sweep changed")
    checks.check(sharp["h_values"] == [0.04, 0.02, 0.01], "sharp h-sweep changed")
    return smooth_pos, smooth_vel


def check_tfe_boundary(checks: Checks, summary: dict, tex: str) -> None:
    tfe = summary.get("endpoint_tfe_paper_lower_pair_velocity_compression_audit", {})
    checks.check(tfe.get("accepted_h_sweep_present") is False, "TFE accepted h-sweep unexpectedly true")
    checks.check(tfe.get("full_tfe_stage_replacement") is False, "full TFE stage replacement unexpectedly true")
    checks.check(tfe.get("row_space_compression_probe_row_count") == 36, "row-space row count changed")
    checks.check(tfe.get("row_space_compression_probe_spanning_row_count") == 0, "row-space span count changed")
    checks.check(
        0.7 < float(tfe.get("row_space_compression_probe_best_projection_relative_residual", 0.0)) < 0.8,
        "row-space best residual changed",
    )
    checks.check(
        0.9 < float(tfe.get("row_space_compression_probe_best_nonfinal_projection_relative_residual", 0.0)) < 1.1,
        "row-space best non-final residual changed",
    )
    for text in [
        "independent full-\\tfe{} stage replacement",
        "row-space compression audit",
        "36 target-free",
        "full_tfe_stage_replacement",
        "matrix-mixing follow-up",
        "diagonal\\_plus\\_row\\_broadcast\\_feature",
        "active-velocity extension",
        "stage2_velocity_column_broadcast_feature",
        "stage2_velocity_shifted_column_broadcast_feature",
        "missing-direction decomposition",
        "angular_velocity_w",
        "0.963",
        "angular-only mask",
        "0.752997",
        "translation/angular cross-coupling",
        "0.898812",
        "positive-Lagrange velocity predictor",
        "0.117782",
        "near-terminal convex",
        "0.049317",
        "0.051890",
        "0.052472",
        "stage02_convex_pose_velocity_0p01_z",
        "0.009512",
        "0.009978",
        "0.010085",
        "0.019205",
        "0.049390",
        "0.103464",
        "terminal-limit extrapolation",
        "4.699",
        "2.335",
        "1.168",
        "1.175",
        "mean-acceleration",
        "0.076159",
        "lie_position_u",
        "generalized-velocity shift",
        "0.012376",
        "0.077874",
        "pose-slope",
        "0.878519",
        "source-to-velocity lift",
        "34-row audit",
        "current-pose endpoint velocity matrix",
        "0.609803",
        "matrix-difference",
        "0.042593",
        "0.009527",
        "0.009590",
        "near-terminal slope",
        "stage02_convex_pose_velocity_slope_0p01_0p05_z",
        "0.677034",
        "near-terminal curvature",
        "stage02_convex_pose_velocity_curvature_0p01_0p05_0p10_z",
        "0.871228",
        "source/history coefficient-feature",
        "source_curvature_shifted_column_broadcast_feature",
        "0.898873",
        "nonlinear recurrent curvature/history",
        "source_curvature_minus_history_delta_diagonal_plus_row_broadcast_feature",
        "0.898865",
        "0.556051",
        "0.999996",
        "terminal-limit source-lift",
        "curvature\\_m0p1",
        "curvature\\_p0p01",
        "5.298",
        "1.076",
        "mean-acceleration bridge scale",
        "accel\\_p0p01",
        "0.000867721",
        "0.706665",
        "generalized-acceleration Taylor-shift",
        "genaccel\\_p0p01",
        "0.000866899",
        "0.701135",
        "pose-acceleration Taylor-shift",
        "poseaccel\\_p0p01",
        "4.1835e-05",
        "0.711570",
        "0.771337",
        "tiny pose-acceleration scale",
        "poseaccel\\_p0p0005",
        "5.5898e-06",
        "translation_acceleration_a",
        "0.350240",
        "pose+velocity acceleration Taylor",
        "posevelaccel\\_p0p0005\\_m0p0001",
        "1.0173e-05",
        "0.544660",
        "component-split pose-acceleration",
        "transposeaccel\\_m0p01",
        "9.6511e-06",
        "component-split velocity-acceleration",
        "transvelaccel\\_m0p01",
        "2.138\\times10^{-4}",
        "transvelaccel\\_m0p0005",
        "9.8175\\times10^{-6}",
        "0.000864560",
        "component-mixed pose/velocity Taylor",
        "p0.0005/m0.0005",
        "9.987\\times10^{-6}",
        "0.774582",
        "stage-2-fixed/delta acceleration velocity-shift",
        "transvelaccelstage2\\_m0p0005",
        "1.0119\\times10^{-5}",
        "nonfinal terminal velocity/source predictor",
        "euler1",
        "0.923466",
        "translation_velocity_v",
        "0.959959",
        "stage-2 source-to-velocity transport",
        "0.0001251",
        "historydelta\\_m0p01",
        "historydelta\\_m0p0001",
        "1.251\\times10^{-6}",
        "1.296\\times10^{-6}",
        "Gauss endpoint-pose",
        "gauss_endpoint_pose_positive_lagrange_z",
        "0.208599",
        "lie_position_u",
        "0.651",
        "gauss_endpoint_pose_stage02_convex_0p00_z",
        "0.172659",
        "rank six",
        "0.952340",
        "stage02_convex_pose_velocity_0p01_sourcelift_historydelta_p1_z",
    ]:
        checks.check(text in tex, f"paper is missing TFE boundary text: {text}")


def check_reproducibility_claim(checks: Checks, summary: dict, tex: str, readme: str) -> None:
    runtime = f"{float(summary['runtime_sec']):.2f}"
    checks.check(runtime in tex, f"paper is missing full-regeneration runtime {runtime}")
    checks.check(runtime in readme, f"paper README is missing full-regeneration runtime {runtime}")
    for text in [
        "validate_paper_package.py",
        "validate_paper_claims.py",
        "validate_cmame_submission.py",
        "validate_proof_evidence_matrix.py",
        "validate_source_paper_comparison.py",
        "validate_submission_bundle.py",
        "validate_four_asme_minimal.py",
        "validate_v047_outputs.py",
        "run_v047.py",
        "CLAIM\\_BOUNDARY.json",
        "machine-readable claim boundary",
        "evidence_files",
        "summary\\_v047.json",
        "convergence CSV",
        "ASME CSV rows",
        "paper-\\tfe{} formula-mapping CSV",
        "full-\\tfe{} gap ledger",
        "repair specification",
        "paper PDF",
        "Chinese status note",
    ]:
        checks.check(text in tex or text in readme, f"paper reproducibility docs missing {text}")


def check_better_integrator_boundary(
    checks: Checks,
    tex: str,
    readme: str,
    checklist: str,
    ledger: str,
    status_cn: str,
) -> None:
    required = [
        (tex, "A Conditional Sixth-Order Formal-Order Comparison", "paper text"),
        (tex, "conditional formal-order comparison", "paper text"),
        (tex, "Formal-order comparison relative to the local paper-style \\tfe{} target", "paper text"),
        (tex, "sixth-order \\method{} path", "paper text"),
        (tex, "\\newtheorem{theorem}{Theorem}", "paper text"),
        (tex, "\\newtheorem{lemma}{Lemma}", "paper text"),
        (tex, "\\newtheorem{assumption}{Assumption}", "paper text"),
        (tex, "\\newtheorem{corollary}{Corollary}", "paper text"),
        (tex, "not needed for the formal-order comparison claim", "paper text"),
        (tex, "Role of the Full-TFE Replacement", "paper text"),
        (tex, "The v047 evidence supports the intended conditional formal-order comparison", "paper text"),
        (tex, "Main Comparative Proposition", "paper text"),
        (tex, "\\newtheorem{proposition}{Proposition}", "paper text"),
        (tex, "\\begin{proposition}[Formal-order comparison]", "paper text"),
        (tex, "\\label{prop:formal-order-comparison}", "paper text"),
        (tex, "\\begin{proof}[Evidence and proof sketch]", "paper text"),
        (tex, "\\end{proof}", "paper text"),
        (tex, "Within the current v047 artifact scope", "paper text"),
        (tex, "full residual reproduction theorem", "paper text"),
        (tex, "Comparator Definition", "paper text"),
        (tex, "Comparator definition for the paper-facing formal-order comparison", "paper text"),
        (tex, "Local paper-style $m=3$ Lobatto-\\tfe{} target", "paper text"),
        (tex, "Complete source-paper \\tfe{} residual", "paper text"),
        (tex, "not the main paper-facing", "paper text"),
        (tex, "comparator for Proposition~\\ref{prop:formal-order-comparison}", "paper text"),
        (tex, "Original-paper boundary versus accepted v047 claim", "paper text"),
        (tex, "\\label{tab:source-paper-v047-boundary}", "paper text"),
        (tex, "Source-paper/local target", "paper text"),
        (tex, "Accepted v047 claim", "paper text"),
        (tex, "What is implemented as the method?", "paper text"),
        (tex, "What remains outside the claim?", "paper text"),
        (tex, "not a completed", "paper text"),
        (tex, "source-paper residual reproduction", "paper text"),
        (tex, "Acceptance criteria for the paper-facing formal-order comparison", "paper text"),
        (tex, "\\label{tab:formal-order-acceptance}", "paper text"),
        (tex, "Accepted method path", "paper text"),
        (tex, "Order exceedance", "paper text"),
        (tex, "Four-example gate", "paper text"),
        (tex, "Comparator boundary", "paper text"),
        (tex, "Caveat separation", "paper text"),
        (tex, "Read-only reproducibility", "paper text"),
        (tex, "without invoking the full v047", "paper text"),
        (tex, "generator", "paper text"),
        (tex, "Accepted One-Step Integrator", "paper text"),
        (tex, "\\label{sec:accepted-one-step-integrator}", "paper text"),
        (tex, "one-step map", "paper text"),
        (tex, "\\Psi_h^{\\mathrm{G6FVA}}", "paper text"),
        (tex, "solve the 132-row nonlinear stage system", "paper text"),
        (tex, "The theorem endpoint object is the velocity-level/KKT closure functional", "paper text"),
        (tex, "Proposition Evidence Traceability", "paper text"),
        (tex, "\\label{tab:proposition-traceability}", "paper text"),
        (tex, "Traceability for the formal-order comparison proposition", "paper text"),
        (tex, "Accepted \\method{} one-step map", "paper text"),
        (tex, "Smooth high-order behavior", "paper text"),
        (tex, "Four-example acceptance", "paper text"),
        (tex, "Comparator boundary", "paper text"),
        (tex, "Open full-\\tfe{} caveat", "paper text"),
        (tex, "Corollary acceptance", "paper text"),
        (tex, "Assumption--lemma--theorem--corollary chain", "paper text"),
        (tex, "current read-only v047 artifact scope", "paper text"),
        (tex, "Repository synchronization", "paper text"),
        (tex, "\\begin{assumption}[Smooth accepted-path order assumptions]", "paper text"),
        (tex, "\\label{ass:g6fva-order}", "paper text"),
        (tex, "regular smooth", "paper text"),
        (tex, "constrained flow in a local Lie-group chart", "paper text"),
        (tex, "Newton", "paper text"),
        (tex, "tolerance below the sixth-order truncation scale", "paper text"),
        (tex, "smooth diffeomorphisms on the tested trajectory tube", "paper text"),
        (tex, "\\begin{theorem}[Order of the accepted \\method{} map]", "paper text"),
        (tex, "\\label{thm:g6fullva-order}", "paper text"),
        (tex, "Under Assumption~\\ref{ass:g6fva-order}", "paper text"),
        (tex, "direct 132-row residual bridge", "paper text"),
        (tex, "row-local \\(O(h^7)\\) residual input", "paper text"),
        (tex, "Newton--Euler rows vanish by direct substitution", "paper text"),
        (tex, "local defect $O(h^7)$", "paper text"),
        (tex, "global error $O(h^6)$", "paper text"),
        (tex, "Endpoint closure and the inexact", "paper text"),
        (tex, "local-to-global transfer then gives the", "paper text"),
        (tex, "Residual-only mechanism rows, source-policy", "paper text"),
        (tex, "separate primitive/Taylor T3 route", "paper text"),
        (tex, "\\begin{lemma}[Order of the local paper-style \\tfe{} target]", "paper text"),
        (tex, "\\label{lem:tfe-target-order}", "paper text"),
        (tex, "formula-order convention", "paper text"),
        (tex, "$p_{\\mathrm{TFE}}(3)=5$", "paper text"),
        (tex, "compact-tube hypotheses", "paper text"),
        (tex, "\\begin{theorem}[Accepted formal-order comparison theorem]", "paper text"),
        (tex, "\\label{thm:accepted-formal-order-comparison}", "paper text"),
        (tex, "current v047 artifact contract", "paper text"),
        (tex, "the following and only the following paper-facing statement", "paper text"),
        (tex, "The theorem does not assert complete source-paper", "paper text"),
        (tex, "\\emph{Order.}", "paper text"),
        (tex, "\\emph{Four-example evidence.}", "paper text"),
        (tex, "\\emph{Comparison.}", "paper text"),
        (tex, "\\emph{Boundary.}", "paper text"),
        (tex, "Theorem~\\ref{thm:accepted-formal-order-comparison}", "paper text"),
        (tex, "\\begin{corollary}[Artifact-backed formal-order comparison acceptance]", "paper text"),
        (tex, "\\label{cor:artifact-backed-acceptance}", "paper text"),
        (tex, "current read-only v047 artifact", "paper text"),
        (tex, "Proposition~\\ref{prop:formal-order-comparison} is accepted", "paper text"),
        (tex, "Theorem~\\ref{thm:g6fullva-order}", "paper text"),
        (tex, "accepts only the formal-order comparison", "paper text"),
        (tex, "not the stronger reproduction", "paper text"),
        (tex, "claim.", "paper text"),
        (readme, "Primary paper claim", "paper README"),
        (readme, "conditional formal-order comparison", "paper README"),
        (readme, "not an implemented source-paper superiority claim", "paper README"),
        (readme, "CLAIM_BOUNDARY.json", "paper README"),
        (checklist, "Primary claim: the paper states a conditional formal-order comparison", "reviewer checklist"),
        (ledger, "Conditional formal-order comparison with the local paper-style TFE target", "claim ledger"),
        (ledger, "bounded order-comparison statement", "claim ledger"),
        (ledger, "Original Paper Versus Accepted v047 Claim", "claim ledger"),
        (ledger, "Table `tab:source-paper-v047-boundary`", "claim ledger"),
        (ledger, "Boundary question", "claim ledger"),
        (ledger, "Complete source-paper TFE residual is not the accepted comparator", "claim ledger"),
        (ledger, "Conditional formal-order comparison inside the current v047 artifact scope", "claim ledger"),
        (ledger, "Order-Comparison Acceptance Criteria", "claim ledger"),
        (ledger, "paper-facing order-comparison acceptance table", "claim ledger"),
        (ledger, "Accepted method path", "claim ledger"),
        (ledger, "Order exceedance", "claim ledger"),
        (ledger, "Four-example gate", "claim ledger"),
        (ledger, "Comparator boundary", "claim ledger"),
        (ledger, "Caveat separation", "claim ledger"),
        (ledger, "Read-only reproducibility", "claim ledger"),
        (ledger, "without invoking the full v047 generator", "claim ledger"),
        (ledger, "accepted method-order theorem plus a separate", "claim ledger"),
        (ledger, "is deliberately scoped", "claim ledger"),
        (ledger, "claim boundary keeps source-policy reproduction", "claim ledger"),
        (status_cn, "主目标不是复现原 paper", "Chinese status note"),
        (status_cn, "formal-order comparison", "Chinese status note"),
        (status_cn, "这影响主 claim 吗？ | 不影响", "Chinese status note"),
        (status_cn, "原 paper / local target vs accepted v047 claim", "Chinese status note"),
        (status_cn, "Source-paper/local target", "Chinese status note"),
        (status_cn, "Accepted v047 claim", "Chinese status note"),
        (status_cn, "Not claimed", "Chinese status note"),
        (status_cn, "complete source-paper residual reproduction", "Chinese status note"),
        (status_cn, "every source-paper", "Chinese status note"),
    ]
    for haystack, needle, label in required:
        checks.check(needle in haystack, f"{label} missing formal-order boundary: {needle}")


def check_tfe_terminology_boundary(
    checks: Checks,
    tex: str,
    readme: str,
    status_cn: str,
    quickstart: str,
) -> None:
    required = [
        (quickstart, "Terminology: TFE Versus FTE", "validation quickstart"),
        (quickstart, "`TFE` means temporal finite element", "validation quickstart"),
        (quickstart, "`FTE` is not a separate method", "validation quickstart"),
        (
            quickstart,
            "`full TFE replacement` means replacing the accepted `Gauss6/FullVA` 132-row stage residual",
            "validation quickstart",
        ),
        (quickstart, "stricter than the accepted formal-order comparison", "validation quickstart"),
        (readme, "Terminology: `TFE` means temporal finite element", "paper README"),
        (readme, "`FTE` is not a separate method", "paper README"),
        (readme, "replacing the accepted `Gauss6/FullVA` 132-row stage residual", "paper README"),
        (readme, "paper-derived temporal finite-element weak rows", "paper README"),
        (status_cn, "`TFE` 是 temporal finite element，不是 `FTE`", "Chinese status note"),
        (status_cn, "full TFE replacement", "Chinese status note"),
        (status_cn, "paper-derived temporal finite-element weak rows", "Chinese status note"),
        (tex, "occasional spelling ``FTE''", "paper text"),
        (tex, "should be read as \\tfe{}, temporal finite element", "paper text"),
        (tex, "full-\\tfe{} replacement", "paper text"),
    ]
    for haystack, needle, label in required:
        checks.check(contains_normalized(haystack, needle), f"{label} missing TFE terminology boundary: {needle}")


def check_current_pipeline_contract(checks: Checks, contract: str, boundary: dict) -> None:
    evidence_files = boundary.get("evidence_files", {})
    checks.check(
        evidence_files.get("current_pipeline_contract") == "CURRENT_PIPELINE_CONTRACT.md",
        "claim boundary JSON current pipeline contract evidence path changed",
    )
    for text in [
        "Current Pipeline Contract",
        "`research-pipeline`",
        "process guard",
        "current files in this repository are authoritative",
        "paper_v047_cylindrical_chain/CLAIM_BOUNDARY.json",
        "pipeline_validation_results/pipeline_validation_summary.json",
        "v047_cylindrical_chain_pipeline/results/summary_v047.json",
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
        "../.venv_sbel/bin/python validate_submission_bundle.py",
        "../.venv_sbel/bin/python validate_cmame_submission.py",
        "../.venv_sbel/bin/python validate_paper_package.py",
        "../.venv_sbel/bin/python validate_four_asme_minimal.py",
        "../.venv_sbel/bin/python validate_full_tfe_gap.py",
        "../.venv_sbel/bin/python validate_full_tfe_repair_spec.py",
        "../.venv_sbel/bin/python validate_v047_outputs.py",
        "Do not run `v047_cylindrical_chain_pipeline/run_v047.py`",
        "Next Real Research Gate",
        "source-free",
        "projection-free",
        "non-terminal-row-replacement",
        "132-row Newton system full rank",
    ]:
        checks.check(contains_normalized(contract, text), f"current pipeline contract missing {text}")


def check_claim_boundary_json(checks: Checks, summary: dict, boundary: dict) -> None:
    smooth = summary["convergence"]["cases"]["cylindrical_smooth"]["projected_velocity"]
    asme = summary.get("asme_gate", {})
    runs = asme.get("method_runs", {})
    primary = boundary.get("primary_claim", {})
    asme_acceptance = boundary.get("asme_acceptance", {})
    comparator = boundary.get("comparator", {})
    full_generator = boundary.get("full_generator", {})
    terminology = boundary.get("terminology", {})
    full_tfe_term = terminology.get("full_tfe_replacement", {})
    order_conventions = boundary.get("order_conventions", {})
    observed_orders = order_conventions.get("observed_smooth_projected_orders", {})
    paper_order_target = order_conventions.get("local_paper_style_tfe_formula_target", {})
    diagnostic_candidates = order_conventions.get("diagnostic_candidates_not_accepted", [])
    full_tfe_gap_contract = boundary.get("full_tfe_gap_contract", {})
    caveat_contracts = boundary.get("remaining_caveat_contracts", {})
    smooth_orders = primary.get("smooth_projected_orders", {})
    evidence_files = boundary.get("evidence_files", {})

    checks.check(boundary.get("schema") == "v047-paper-claim-boundary-v1", "claim boundary JSON schema changed")
    checks.check(
        primary.get("name") == "sixth_order_fullva_formal_order_alternative",
        "claim boundary JSON primary claim changed",
    )
    checks.check(
        primary.get("status") == "accepted_as_formal_order_alternative_not_external_superiority",
        "claim boundary JSON primary status changed",
    )
    checks.check(primary.get("accepted_method") == "Gauss6/FullVA", "claim boundary JSON accepted method changed")
    checks.check(primary.get("method_order_claim") == 6, "claim boundary JSON method order is not six")
    checks.check(
        rounded(float(smooth_orders.get("position", 0.0))) == rounded(float(smooth["position_order"])),
        "claim boundary JSON position order does not match summary",
    )
    checks.check(
        rounded(float(smooth_orders.get("velocity", 0.0))) == rounded(float(smooth["velocity_order"])),
        "claim boundary JSON velocity order does not match summary",
    )
    checks.check(
        primary.get("asme_gate_status") == summary.get("asme_gate", {}).get("status"),
        "claim boundary JSON ASME status does not match summary",
    )
    checks.check(set(primary.get("accepted_examples", [])) == EXPECTED_MODELS, "claim boundary JSON ASME examples changed")
    checks.check(
        primary.get("accepted_examples_role") == "mechanism_coverage_examples_not_all_dynamic_order",
        "claim boundary JSON accepted-example role changed",
    )
    checks.check(
        set(primary.get("accepted_dynamic_order_examples", [])) == EXPECTED_DYNAMIC_ORDER_MODELS,
        "claim boundary JSON dynamic-order examples changed",
    )
    checks.check(
        set(primary.get("accepted_mechanism_coverage_examples", [])) == EXPECTED_MODELS,
        "claim boundary JSON mechanism-coverage examples changed",
    )
    checks.check(
        set(primary.get("coverage_only_dynamic_order_examples", [])) == EXPECTED_COVERAGE_ONLY_MODELS,
        "claim boundary JSON coverage-only dynamic-order examples changed",
    )
    checks.check(asme_acceptance.get("status") == asme.get("status"), "claim boundary JSON ASME acceptance status changed")
    checks.check(
        asme_acceptance.get("source") == "v047_cylindrical_chain_pipeline/results/summary_v047.json:asme_gate.method_runs",
        "claim boundary JSON ASME acceptance source changed",
    )
    checks.check(
        asme_acceptance.get("full_tfe_required_for_gate") is False,
        "claim boundary JSON incorrectly requires full TFE for ASME gate",
    )
    checks.check(
        set(asme_acceptance.get("accepted_examples", [])) == EXPECTED_MODELS,
        "claim boundary JSON ASME accepted examples changed",
    )
    checks.check(
        asme_acceptance.get("accepted_examples_role") == "mechanism_coverage_examples_not_all_dynamic_order",
        "claim boundary JSON ASME accepted-example role changed",
    )
    checks.check(
        set(asme_acceptance.get("accepted_dynamic_order_examples", [])) == EXPECTED_DYNAMIC_ORDER_MODELS,
        "claim boundary JSON ASME dynamic-order examples changed",
    )
    checks.check(
        set(asme_acceptance.get("accepted_mechanism_coverage_examples", [])) == EXPECTED_MODELS,
        "claim boundary JSON ASME mechanism-coverage examples changed",
    )
    checks.check(
        set(asme_acceptance.get("coverage_only_dynamic_order_examples", [])) == EXPECTED_COVERAGE_ONLY_MODELS,
        "claim boundary JSON ASME coverage-only dynamic-order examples changed",
    )
    for model, expected_status in EXPECTED_MAPPING_STATUS.items():
        checks.check(
            asme_acceptance.get(model, {}).get("mapping_status") == expected_status,
            f"claim boundary JSON ASME mapping status changed for {model}",
        )
    single = runs["single_pendulum_driven_absolute_fullva"]
    single_min_order = min(
        float(single["position_observed_order"]),
        float(single["velocity_observed_order"]),
        float(single["orientation_observed_order"]),
        float(single["omega_observed_order"]),
    )
    double = runs["double_pendulum"]
    double_min_order = min(
        float(double["orientation_observed_order"]),
        float(double["omega_observed_order"]),
    )
    closed_loop = runs["closed_loop_kinematic_fullva"]["models"]
    reactions = runs["closed_loop_reaction_dynamics"]["models"]
    for model in ["four_link", "slider_crank"]:
        closed_model = closed_loop[model]
        reaction_model = reactions[model]
        max_constraint = max(
            float(closed_model["max_position_constraint_norm"]),
            float(closed_model["max_velocity_constraint_norm"]),
            float(closed_model["max_acceleration_constraint_norm"]),
        )
        boundary_model = asme_acceptance.get(model, {})
        checks.check(
            boundary_model.get("closed_loop_status") == closed_model.get("status"),
            f"claim boundary JSON closed-loop status changed for {model}",
        )
        checks.check(
            boundary_model.get("reaction_status") == reaction_model.get("status"),
            f"claim boundary JSON reaction status changed for {model}",
        )
        checks.check(
            [float(h) for h in boundary_model.get("h_values", [])] == [0.02, 0.01, 0.005],
            f"claim boundary JSON ASME h-values changed for {model}",
        )
        checks.check(
            sci(float(boundary_model.get("max_closed_loop_constraint_norm", 0.0))) == sci(max_constraint),
            f"claim boundary JSON max closed-loop constraint changed for {model}",
        )
        checks.check(
            sci(float(boundary_model.get("max_dynamics_residual_norm", 0.0)))
            == sci(float(reaction_model["max_dynamics_residual_norm"])),
            f"claim boundary JSON max dynamics residual changed for {model}",
        )
    checks.check(
        rounded(float(asme_acceptance.get("single_pendulum", {}).get("absolute_fullva_min_order", 0.0)))
        == rounded(single_min_order),
        "claim boundary JSON single-pendulum minimum order changed",
    )
    checks.check(
        sci(float(asme_acceptance.get("single_pendulum", {}).get("max_stage_residual_norm", 0.0)))
        == sci(float(single["max_stage_residual_norm"])),
        "claim boundary JSON single-pendulum stage residual changed",
    )
    checks.check(
        rounded(float(asme_acceptance.get("double_pendulum", {}).get("method_min_order", 0.0)))
        == rounded(double_min_order),
        "claim boundary JSON double-pendulum minimum order changed",
    )
    checks.check(
        asme_acceptance.get("double_pendulum", {}).get("accepted_reference") == "v029_fullva_nested_h0.005",
        "claim boundary JSON double-pendulum reference policy changed",
    )
    checks.check(
        sci(float(asme_acceptance.get("double_pendulum", {}).get("max_endpoint_constraint_norm", 0.0)))
        == sci(float(double["max_endpoint_constraint_norm"])),
        "claim boundary JSON double-pendulum endpoint constraint changed",
    )
    checks.check(
        sci(float(asme_acceptance.get("double_pendulum", {}).get("max_endpoint_velocity_constraint_norm", 0.0)))
        == sci(float(double["max_endpoint_velocity_constraint_norm"])),
        "claim boundary JSON double-pendulum velocity constraint changed",
    )
    checks.check(
        comparator.get("name") == "local_paper_style_m3_gauss_lobatto_tfe_formula_target",
        "claim boundary JSON comparator changed",
    )
    checks.check(comparator.get("expected_order") == 5, "claim boundary JSON comparator order is not five")
    checks.check(
        comparator.get("complete_source_paper_residual_accepted") is False,
        "claim boundary JSON unexpectedly accepts complete source-paper residual",
    )
    checks.check(boundary.get("full_tfe_stage_replacement") is False, "claim boundary JSON unexpectedly accepts full TFE")
    checks.check(terminology.get("tfe") == "temporal finite element", "claim boundary JSON TFE terminology changed")
    checks.check(
        terminology.get("fte") == "typo_for_tfe_not_a_separate_method",
        "claim boundary JSON FTE terminology changed",
    )
    checks.check(
        full_tfe_term.get("meaning")
        == "replace the accepted Gauss6/FullVA 132-row stage residual with paper-derived temporal finite-element weak rows",
        "claim boundary JSON full-TFE replacement meaning changed",
    )
    checks.check(
        full_tfe_term.get("role")
        == "stronger_source_paper_reproduction_gate_not_prerequisite_for_formal_order_comparison",
        "claim boundary JSON full-TFE replacement role changed",
    )
    checks.check(full_tfe_term.get("accepted") is False, "claim boundary JSON full-TFE terminology unexpectedly accepted")
    checks.check(order_conventions.get("accepted_method") == "Gauss6/FullVA", "claim boundary JSON order method changed")
    checks.check(order_conventions.get("accepted_method_order") == 6, "claim boundary JSON accepted method order changed")
    checks.check(
        rounded(float(observed_orders.get("position", 0.0))) == rounded(float(smooth["position_order"])),
        "claim boundary JSON observed position order does not match summary",
    )
    checks.check(
        rounded(float(observed_orders.get("velocity", 0.0))) == rounded(float(smooth["velocity_order"])),
        "claim boundary JSON observed velocity order does not match summary",
    )
    checks.check(
        observed_orders.get("source") == "v047_cylindrical_chain_pipeline/results/cylindrical_chain_convergence.csv",
        "claim boundary JSON observed-order source changed",
    )
    checks.check(paper_order_target.get("nodes") == "m=3 Gauss-Lobatto", "claim boundary JSON paper-order nodes changed")
    checks.check(paper_order_target.get("expected_order") == 5, "claim boundary JSON paper-order target changed")
    checks.check(
        paper_order_target.get("role") == "comparator_not_accepted_method",
        "claim boundary JSON paper-order role changed",
    )
    diagnostic_by_name = {candidate.get("name"): candidate for candidate in diagnostic_candidates}
    expected_diagnostics = {
        "source_free_final_stage_velocity_closure": (3.523, 4.828, "order_limited_not_full_tfe_replacement"),
        "endpoint_pose_velocity_predictor_smoke": (4.142, 2.305, "terminal_closure_but_order_limited"),
    }
    for name, (pos_order, vel_order, reason) in expected_diagnostics.items():
        candidate = diagnostic_by_name.get(name, {})
        candidate_orders = candidate.get("smooth_orders", {})
        checks.check(name in diagnostic_by_name, f"claim boundary JSON missing diagnostic order candidate {name}")
        checks.check(
            rounded(float(candidate_orders.get("position", 0.0))) == rounded(pos_order),
            f"claim boundary JSON diagnostic position order changed for {name}",
        )
        checks.check(
            rounded(float(candidate_orders.get("velocity", 0.0))) == rounded(vel_order),
            f"claim boundary JSON diagnostic velocity order changed for {name}",
        )
        checks.check(candidate.get("reason") == reason, f"claim boundary JSON diagnostic reason changed for {name}")
    full_stage_gap = summary.get("endpoint_tfe_full_stage_acceptance_gap_audit", {})
    readiness = summary.get("endpoint_tfe_readiness_audit", {})
    acceptance_matrix = summary.get("endpoint_tfe_paper_lower_pair_closure_acceptance_matrix_audit", {})
    compression = summary.get("endpoint_tfe_paper_lower_pair_velocity_compression_audit", {})
    final_stage = summary.get("endpoint_tfe_paper_lower_pair_source_free_final_stage_velocity_closure_audit", {})
    final_smooth = final_stage.get("cases", {}).get("cylindrical_smooth", {})
    blend = summary.get("endpoint_tfe_paper_lower_pair_source_free_order_closure_blend_trajectory_audit", {})
    gap_acceptance = full_tfe_gap_contract.get("closure_acceptance_matrix", {})
    gap_compression = full_tfe_gap_contract.get("velocity_compression_blocker", {})
    gap_final_stage = full_tfe_gap_contract.get("source_free_final_stage_split", {})
    gap_blend = full_tfe_gap_contract.get("order_closure_blend_split", {})
    checks.check(
        full_tfe_gap_contract.get("status") == full_stage_gap.get("status"),
        "claim boundary JSON full-TFE gap status changed",
    )
    checks.check(
        full_tfe_gap_contract.get("full_tfe_stage_replacement") is False,
        "claim boundary JSON full-TFE gap unexpectedly accepted",
    )
    checks.check(
        full_tfe_gap_contract.get("stage_row_budget") == full_stage_gap.get("stage_row_budget") == 132,
        "claim boundary JSON full-TFE stage row budget changed",
    )
    checks.check(
        [float(h) for h in full_tfe_gap_contract.get("h_values", [])] == [0.04, 0.02, 0.01],
        "claim boundary JSON full-TFE h-values changed",
    )
    checks.check(float(full_tfe_gap_contract.get("reference_h", 0.0)) == 0.005, "claim boundary JSON full-TFE reference h changed")
    checks.check(full_tfe_gap_contract.get("proxy_residual_solved") is True, "claim boundary JSON full-TFE proxy solve flag changed")
    checks.check(
        full_tfe_gap_contract.get("derived_full_tfe_stage_functional_present") is False,
        "claim boundary JSON unexpectedly has derived full-TFE stage functional",
    )
    checks.check(
        full_tfe_gap_contract.get("endpoint_boundary_source_removed") is False,
        "claim boundary JSON unexpectedly removes endpoint-boundary source",
    )
    checks.check(
        sci(float(full_tfe_gap_contract.get("max_proxy_residual_norm", 0.0)))
        == sci(float(full_stage_gap.get("max_proxy_residual_norm", 0.0))),
        "claim boundary JSON full-TFE proxy residual changed",
    )
    checks.check(
        full_tfe_gap_contract.get("min_acceptance_satisfied_count") == full_stage_gap.get("min_acceptance_satisfied_count"),
        "claim boundary JSON full-TFE satisfied count changed",
    )
    checks.check(
        full_tfe_gap_contract.get("max_acceptance_missing_count") == full_stage_gap.get("max_acceptance_missing_count"),
        "claim boundary JSON full-TFE missing count changed",
    )
    checks.check(
        full_tfe_gap_contract.get("readiness_counts") == readiness.get("counts"),
        "claim boundary JSON full-TFE readiness counts changed",
    )
    checks.check(gap_acceptance.get("accepted_candidate_count") == acceptance_matrix.get("accepted_candidate_count") == 0, "claim boundary JSON full-TFE accepted candidate count changed")
    checks.check(
        gap_acceptance.get("best_order_preserving_source_free_candidate")
        == acceptance_matrix.get("best_order_preserving_source_free_candidate"),
        "claim boundary JSON full-TFE best order-preserving candidate changed",
    )
    checks.check(
        gap_acceptance.get("best_terminal_velocity_candidate") == acceptance_matrix.get("best_terminal_velocity_candidate"),
        "claim boundary JSON full-TFE best terminal-velocity candidate changed",
    )
    checks.check(gap_compression.get("accepted_h_sweep_present") is False, "claim boundary JSON full-TFE compression unexpectedly accepted h-sweep")
    checks.check(
        gap_compression.get("row_space_compression_rows") == compression.get("row_space_compression_probe_row_count") == 36,
        "claim boundary JSON full-TFE row-space row count changed",
    )
    checks.check(
        gap_compression.get("row_space_spans") == compression.get("row_space_compression_probe_spanning_row_count") == 0,
        "claim boundary JSON full-TFE row-space span count changed",
    )
    checks.check(
        gap_compression.get("weak_row_structure_rows") == compression.get("weak_row_structure_capacity_probe_row_count") == 216,
        "claim boundary JSON full-TFE weak-row row count changed",
    )
    checks.check(
        gap_compression.get("weak_row_structure_spans") == compression.get("weak_row_structure_capacity_probe_spanning_row_count") == 0,
        "claim boundary JSON full-TFE weak-row span count changed",
    )
    checks.check(
        rounded(float(gap_compression.get("best_row_space_residual", 0.0)), 6)
        == rounded(float(compression.get("row_space_compression_probe_best_projection_relative_residual", 0.0)), 6),
        "claim boundary JSON full-TFE row-space residual changed",
    )
    checks.check(
        rounded(float(gap_compression.get("best_nonfinal_residual", 0.0)), 6)
        == rounded(float(compression.get("row_space_compression_probe_best_nonfinal_projection_relative_residual", 0.0)), 6),
        "claim boundary JSON full-TFE nonfinal residual changed",
    )
    checks.check(
        gap_final_stage.get("terminal_velocity_closed") is True,
        "claim boundary JSON final-stage terminal closure flag changed",
    )
    checks.check(
        sci(float(gap_final_stage.get("max_raw_terminal_endpoint_velocity_constraint_norm", 0.0)))
        == sci(float(final_stage.get("max_raw_terminal_endpoint_velocity_constraint_norm", 0.0))),
        "claim boundary JSON final-stage terminal velocity changed",
    )
    checks.check(
        rounded(float(gap_final_stage.get("smooth_position_order", 0.0)))
        == rounded(float(final_smooth.get("position_order", 0.0))),
        "claim boundary JSON final-stage position order changed",
    )
    checks.check(
        rounded(float(gap_final_stage.get("smooth_velocity_order", 0.0)))
        == rounded(float(final_smooth.get("velocity_order", 0.0))),
        "claim boundary JSON final-stage velocity order changed",
    )
    checks.check(
        gap_final_stage.get("reason_not_accepted")
        == "terminal_closed_but_smooth_position_order_below_accepted_full_tfe_floor",
        "claim boundary JSON final-stage rejection reason changed",
    )
    checks.check(
        gap_blend.get("order_and_terminal_intersection_present") is False,
        "claim boundary JSON order/closure intersection unexpectedly present",
    )
    checks.check(
        sci(float(gap_blend.get("terminal_closing_beta_max_velocity", 0.0)))
        == sci(float(blend.get("global_best_beta_max_terminal_velocity", 0.0))),
        "claim boundary JSON order/closure terminal velocity changed",
    )
    checks.check(
        rounded(float(gap_blend.get("terminal_closing_beta_min_order", 0.0)))
        == rounded(float(blend.get("global_best_beta_min_order", 0.0))),
        "claim boundary JSON order/closure min order changed",
    )
    checks.check(
        full_tfe_gap_contract.get("next_repair_target")
        == "derive a nonterminal endpoint-pose predictor that closes terminal velocity on trajectory",
        "claim boundary JSON full-TFE next repair target changed",
    )
    checks.check(
        full_tfe_gap_contract.get("compression_next_repair_target")
        == compression.get("next_repair_target"),
        "claim boundary JSON full-TFE compression repair target changed",
    )
    sparse_contract = caveat_contracts.get("sparse_speed_quantified", {})
    sparse_speed = summary.get("sparse_speed_gap_audit", {})
    sparse_cost = summary.get("sparse_cost_model_audit", {})
    sparse_smooth = sparse_speed.get("cases", {}).get("cylindrical_smooth", {})
    sparse_sharp = sparse_speed.get("cases", {}).get("cylindrical_sharp", {})
    checks.check(sparse_contract.get("status") == sparse_speed.get("status"), "claim boundary JSON sparse speed status changed")
    checks.check(
        sparse_contract.get("cost_model_status") == sparse_cost.get("status"),
        "claim boundary JSON sparse speed cost-model status changed",
    )
    checks.check(sparse_contract.get("pattern_nnz") == sparse_smooth.get("pattern_nnz") == sparse_sharp.get("pattern_nnz") == 2637, "claim boundary JSON sparse pattern nnz changed")
    checks.check(sparse_contract.get("row_colors") == sparse_smooth.get("row_colors") == sparse_sharp.get("row_colors") == 60, "claim boundary JSON sparse row colors changed")
    checks.check(sparse_contract.get("column_colors") == sparse_smooth.get("column_colors") == sparse_sharp.get("column_colors") == 90, "claim boundary JSON sparse column colors changed")
    checks.check(sparse_contract.get("repeats") == sparse_speed.get("repeats") == 5, "claim boundary JSON sparse repeat count changed")
    checks.check(sparse_contract.get("dense_beats_row") is True, "claim boundary JSON sparse dense-beats-row flag changed")
    checks.check(
        rounded(float(sparse_contract.get("smooth_row_runtime_over_dense", 0.0)))
        == rounded(float(sparse_smooth.get("row_slowdown_vs_dense", 0.0))),
        "claim boundary JSON sparse smooth runtime ratio changed",
    )
    checks.check(
        rounded(float(sparse_contract.get("sharp_row_runtime_over_dense", 0.0)))
        == rounded(float(sparse_sharp.get("row_slowdown_vs_dense", 0.0))),
        "claim boundary JSON sparse sharp runtime ratio changed",
    )
    checks.check(
        rounded(float(sparse_contract.get("max_row_runtime_reduction_needed_to_match_dense", 0.0)), 6)
        == rounded(float(sparse_cost.get("max_row_runtime_reduction_needed_to_match_dense", 0.0)), 6),
        "claim boundary JSON sparse match-dense reduction changed",
    )
    checks.check(
        rounded(float(sparse_contract.get("max_row_runtime_reduction_needed_for_10pct_dense_win", 0.0)), 6)
        == rounded(float(sparse_cost.get("max_row_runtime_reduction_needed_for_10pct_dense_win", 0.0)), 6),
        "claim boundary JSON sparse 10pct-win reduction changed",
    )
    checks.check(
        rounded(float(sparse_contract.get("min_effective_row_colors_at_dense_cost", 0.0)), 3)
        == rounded(float(sparse_cost.get("min_effective_row_colors_at_dense_cost", 0.0)), 3),
        "claim boundary JSON sparse effective row colors changed",
    )
    checks.check(
        sparse_contract.get("role") == "quantified_caveat_not_sparse_wall_clock_speed_win",
        "claim boundary JSON sparse caveat role changed",
    )
    sharp_contract = caveat_contracts.get("sharp_friction_coarse_order_reduction_ultra_recovered", {})
    smoothness = summary.get("friction_smoothness_sweep", {})
    coarse_case = smoothness.get("cases", {}).get("stribeck_0p05", {})
    smooth_case = smoothness.get("cases", {}).get("stribeck_0p5", {})
    sharp_ultra = summary.get("sharp_ultra_refinement_audit", {})
    sharp_cost = summary.get("sharp_refinement_cost_envelope_audit", {})
    checks.check(sharp_contract.get("smoothness_status") == smoothness.get("status"), "claim boundary JSON sharp smoothness status changed")
    checks.check(float(sharp_contract.get("coarse_stribeck_velocity", 0.0)) == 0.05, "claim boundary JSON sharp coarse stribeck velocity changed")
    checks.check(float(sharp_contract.get("smooth_stribeck_velocity", 0.0)) == 0.5, "claim boundary JSON sharp smooth stribeck velocity changed")
    checks.check(
        rounded(float(sharp_contract.get("coarse_position_order", 0.0)))
        == rounded(float(coarse_case.get("position_order", 0.0))),
        "claim boundary JSON sharp coarse position order changed",
    )
    checks.check(
        rounded(float(sharp_contract.get("coarse_velocity_order", 0.0)))
        == rounded(float(coarse_case.get("velocity_order", 0.0))),
        "claim boundary JSON sharp coarse velocity order changed",
    )
    checks.check(
        rounded(float(sharp_contract.get("smooth_position_order", 0.0)))
        == rounded(float(smooth_case.get("position_order", 0.0))),
        "claim boundary JSON sharp smooth position order changed",
    )
    checks.check(
        rounded(float(sharp_contract.get("smooth_velocity_order", 0.0)))
        == rounded(float(smooth_case.get("velocity_order", 0.0))),
        "claim boundary JSON sharp smooth velocity order changed",
    )
    checks.check(sharp_contract.get("ultra_status") == sharp_ultra.get("status"), "claim boundary JSON sharp ultra status changed")
    checks.check([float(h) for h in sharp_contract.get("ultra_h_values", [])] == [0.005, 0.0025, 0.00125], "claim boundary JSON sharp ultra h-values changed")
    checks.check(
        rounded(float(sharp_contract.get("ultra_position_order_all", 0.0)))
        == rounded(float(sharp_ultra.get("position_observed_order_all", 0.0))),
        "claim boundary JSON sharp ultra position order changed",
    )
    checks.check(
        rounded(float(sharp_contract.get("ultra_velocity_order_all", 0.0)))
        == rounded(float(sharp_ultra.get("velocity_observed_order_all", 0.0))),
        "claim boundary JSON sharp ultra velocity order changed",
    )
    checks.check(
        rounded(float(sharp_contract.get("ultra_position_tail_order", 0.0)))
        == rounded(float(sharp_ultra.get("position_tail_order", 0.0))),
        "claim boundary JSON sharp ultra position tail order changed",
    )
    checks.check(
        rounded(float(sharp_contract.get("ultra_velocity_tail_order", 0.0)))
        == rounded(float(sharp_ultra.get("velocity_tail_order", 0.0))),
        "claim boundary JSON sharp ultra velocity tail order changed",
    )
    checks.check(sharp_contract.get("cost_status") == sharp_cost.get("status"), "claim boundary JSON sharp cost status changed")
    checks.check(sharp_contract.get("practical_cost_caveat") is True, "claim boundary JSON sharp practical-cost flag changed")
    checks.check(
        rounded(float(sharp_contract.get("max_runtime_factor_vs_h001", 0.0)))
        == rounded(float(sharp_cost.get("max_runtime_factor_vs_h001", 0.0))),
        "claim boundary JSON sharp runtime factor changed",
    )
    checks.check(
        rounded(float(sharp_contract.get("max_accepted_steps_factor_vs_h001", 0.0)))
        == rounded(float(sharp_cost.get("max_accepted_steps_factor_vs_h001", 0.0))),
        "claim boundary JSON sharp steps factor changed",
    )
    checks.check(
        rounded(float(sharp_contract.get("max_newton_iteration_factor_vs_h001", 0.0)))
        == rounded(float(sharp_cost.get("max_newton_iteration_factor_vs_h001", 0.0))),
        "claim boundary JSON sharp Newton factor changed",
    )
    checks.check(
        rounded(float(sharp_contract.get("max_velocity_error_reduction_vs_h001", 0.0)))
        == rounded(float(sharp_cost.get("max_velocity_error_reduction_vs_h001", 0.0))),
        "claim boundary JSON sharp velocity-error reduction changed",
    )
    checks.check(
        sharp_contract.get("role") == "practical_coarse_regime_cost_caveat_not_asymptotic_failure",
        "claim boundary JSON sharp caveat role changed",
    )
    checks.check(set(boundary.get("open_caveats", [])) == EXPECTED_REMAINING_CAVEATS, "claim boundary JSON caveats changed")
    for not_claimed in [
        "complete_source_paper_residual_reproduction",
        "independent_full_tfe_stage_replacement",
        "sparse_ad_wall_clock_speed_win",
        "sharp_friction_coarse_regime_solved",
    ]:
        checks.check(not_claimed in boundary.get("not_claimed", []), f"claim boundary JSON missing not-claimed item {not_claimed}")
    for validator in [
        "validate_cmame_submission.py",
        "validate_paper_claims.py",
        "validate_paper_package.py",
        "validate_proof_evidence_matrix.py",
        "validate_order_acceptance_gate.py",
        "validate_source_paper_comparison.py",
        "validate_submission_bundle.py",
        "validate_four_asme_minimal.py",
        "validate_full_tfe_gap.py",
        "validate_full_tfe_repair_spec.py",
        "validate_pipeline_outputs.py",
    ]:
        checks.check(validator in boundary.get("read_only_validators", []), f"claim boundary JSON missing validator {validator}")
    checks.check(full_generator.get("script") == "run_v047.py", "claim boundary JSON full-generator script changed")
    checks.check(
        full_generator.get("required_for_paper_claim_check") is False,
        "claim boundary JSON says run_v047.py is required for paper claim check",
    )
    required_evidence_files = {
        "summary_json": "v047_cylindrical_chain_pipeline/results/summary_v047.json",
        "convergence_csv": "v047_cylindrical_chain_pipeline/results/cylindrical_chain_convergence.csv",
        "asme_gate_csv": "v047_cylindrical_chain_pipeline/results/cylindrical_chain_asme_gate.csv",
        "asme_method_runs_csv": "v047_cylindrical_chain_pipeline/results/cylindrical_chain_asme_method_runs.csv",
        "asme_single_absolute_csv": "v047_cylindrical_chain_pipeline/results/cylindrical_chain_asme_single_absolute_fullva_runs.csv",
        "asme_double_method_csv": "v047_cylindrical_chain_pipeline/results/cylindrical_chain_asme_double_method_runs.csv",
        "asme_closed_loop_kinematic_csv": "v047_cylindrical_chain_pipeline/results/cylindrical_chain_asme_closed_loop_kinematic_fullva.csv",
        "asme_closed_loop_reaction_csv": "v047_cylindrical_chain_pipeline/results/cylindrical_chain_asme_closed_loop_reaction_dynamics.csv",
        "paper_formula_mapping_csv": "v047_cylindrical_chain_pipeline/results/cylindrical_chain_endpoint_tfe_paper_formula_mapping_audit.csv",
        "full_tfe_gap_ledger": "v047_cylindrical_chain_pipeline/FULL_TFE_REPLACEMENT_GAP_LEDGER.md",
        "full_tfe_repair_spec": "v047_cylindrical_chain_pipeline/FULL_TFE_REPAIR_SPEC.md",
        "paper_tex": "paper_v047_cylindrical_chain/main.tex",
        "paper_pdf": "paper_v047_cylindrical_chain/main.pdf",
        "cmame_tex": "paper_v047_cylindrical_chain/main_cmame.tex",
        "cmame_pdf": "paper_v047_cylindrical_chain/main_cmame.pdf",
        "cmame_highlights": "paper_v047_cylindrical_chain/highlights_cmame.txt",
        "cmame_declarations": "paper_v047_cylindrical_chain/declarations_cmame.md",
        "cmame_checklist": "paper_v047_cylindrical_chain/CMAME_SUBMISSION_CHECKLIST.md",
        "proof_evidence_matrix": "paper_v047_cylindrical_chain/PROOF_EVIDENCE_MATRIX.md",
        "order_acceptance_gate": "paper_v047_cylindrical_chain/ORDER_ACCEPTANCE_GATE.md",
        "order_acceptance_gate_json": "paper_v047_cylindrical_chain/ORDER_ACCEPTANCE_GATE.json",
        "paper_claim_ledger": "paper_v047_cylindrical_chain/PAPER_CLAIM_LEDGER.md",
        "paper_reviewer_checklist": "paper_v047_cylindrical_chain/REVIEWER_CHECKLIST.md",
        "paper_current_status_cn": "paper_v047_cylindrical_chain/CURRENT_STATUS_CN.md",
        "source_paper_comparison": "paper_v047_cylindrical_chain/SOURCE_PAPER_COMPARISON.md",
        "current_pipeline_contract": "CURRENT_PIPELINE_CONTRACT.md",
    }
    for key, rel_path in required_evidence_files.items():
        checks.check(evidence_files.get(key) == rel_path, f"claim boundary JSON evidence path changed for {key}")
        path = ROOT / rel_path
        checks.check(path.exists() and path.stat().st_size > 0, f"claim boundary JSON evidence file missing or empty: {rel_path}")


def check_reviewer_checklist(checks: Checks, summary: dict, checklist: str, tex: str, readme: str) -> None:
    runtime = f"{float(summary['runtime_sec']):.2f}"
    for text in [
        "v047 Reviewer Checklist",
        EXPECTED_ASME_STATUS,
        "single_pendulum",
        "double_pendulum",
        "four_link",
        "slider_crank",
        "Gauss6/FullVA",
        "7.161/7.066",
        "single_absolute_min_order=6.024",
        "double_method_min_order=6.089",
        "closed_loop_max_constraint_norm=1.052e-14",
        "closed_loop_reaction_max_dynamics_residual=1.338e-13",
        "Original Paper Versus Accepted v047 Claim",
        "Source-paper/local target",
        "Accepted v047 claim",
        "Not claimed",
        "conditional formal-order comparison",
        "every source-paper TFE residual row",
        "Order-Comparison Acceptance Criteria",
        "Accepted method path",
        "Order exceedance",
        "Four-example gate",
        "Comparator boundary",
        "Caveat separation",
        "Read-only reproducibility",
        "diagnostic paper-TFE substitution",
        "expected order five target",
        "without invoking the full",
        "v047 generator",
        "validate_four_asme_minimal.py",
        "v047 minimal four-ASME validation: PASS",
        "full_tfe_stage_replacement=False",
        "m=3",
        "Gauss-Lobatto TFE",
        "4.011e-16",
        "3.523",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_posevelaccel_p0p0005_m0p0001_z",
        "1.0173e-05",
        "component-split pose-acceleration",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_transposeaccel_m0p01_z",
        "9.6511e-06",
        "component-split velocity-acceleration",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_transvelaccel_m0p01_z",
        "2.138e-04",
        "transvelaccel_m0p0005",
        "9.8175e-06",
        "component-mixed pose/velocity Taylor",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_angpose_transvelaccel_p0p0005_m0p0005_z",
        "9.987e-06",
        "stage-2-fixed/delta acceleration velocity-shift",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_transvelaccelstage2_m0p0005_z",
        "1.0119e-05",
        "nonfinal terminal velocity/source predictor",
        "nonfinal_velocity_terminal_euler1_z",
        "0.923466",
        "stage-2 source-to-velocity transport",
        "stage02_convex_pose_velocity_0p00_sourceliftmatrixdiff_historydelta_m0p01_z",
        "0.0001251",
        "stage02_convex_pose_velocity_0p00_sourceliftmatrixdiff_historydelta_m0p0001_z",
        "1.251e-06",
        "stage02_convex_pose_velocity_0p00_sourceliftmatrixdiff_historydelta_m0p0001_angposeaccel_p0p0001_z",
        "1.296e-06",
        "stage02_convex_pose_velocity_0p00_z",
        "1.327e-15",
        "31.7",
        "span_row_count=1",
        "local-span-not-full-TFE",
        "lower_pair_endpoint_pose_velocity_predictor_h_sweep_smoke",
        "8.124e-17",
        "4.142/2.305",
        "6.255e-06",
        "2.345/1.878",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_z",
        "projection_used=false",
        "1.254e-07",
        "6.412/3.775",
        "1.244e-08",
        "4.054/2.364",
        "stage02_convex_pose_velocity_extrapolate_0p00001_0p00002_z",
        "1.254e-13",
        "1.254e-14",
        "4.142/2.305",
        "smooth_order_ok=false",
        "stage02_convex_pose_velocity_quadextrapolate_0p002_0p005_0p01_z",
        "2.029e-13",
        "8.254e-15",
        "nonfinal_velocity_terminal_linear012_z",
        "nonfinal_velocity_terminal_euler2_z",
        "1.770e-07",
        "3.584e-07",
        "2.559e-11",
        "1.328e-07",
        "1.134e-07",
        "stage02_convex_pose_velocity_0p00_sourceliftmatrixdiff_historydelta_m0p00001_z",
        "8.021e-13",
        "5.910e-14",
        "terminal_velocity_closed=true",
        "stage02_convex_pose_velocity_0p01_terminalproj_z",
        "6.739e+08",
        "terminalproj_p0p1",
        "7.028e-06",
        "2.301/1.788",
        "terminalproj_p0p5",
        "1.321e-05",
        "2.158/1.433",
        "projection_used=true",
        "validate_full_tfe_gap.py",
        "validate_full_tfe_repair_spec.py",
        "accepted_candidate_count=0",
        "next_repair_target=derive a nonterminal endpoint-pose predictor that closes terminal velocity on trajectory",
        "validate_paper_package.py",
        "note=run_v047.py was not invoked",
        "Do not run the full generator",
        "run_v047.py",
        runtime,
    ]:
        checks.check(text in checklist, f"reviewer checklist missing {text}")
    checks.check("REVIEWER\\_CHECKLIST.md" in tex, "paper does not list reviewer checklist artifact")
    checks.check("REVIEWER_CHECKLIST.md" in readme, "paper README does not mention reviewer checklist")


def check_order_proof_status(checks: Checks, proof_ledger: str, tex: str, readme: str) -> None:
    for text in [
        "### v047_cylindrical_chain_pipeline",
        "Expected order: conditional sixth order",
        "conditional sixth order for the accepted smooth",
        "P5 direct Newton--Euler residual bridge",
        "retained P6 branch-selected solver scale",
        "velocity-level/KKT closure subsystem",
        "raw endpoint position defect is a separate",
        "does not discharge the P2 endpoint raw-defect/right-",
        "endpoint object is the KKT closure functional",
        "Primary claim boundary",
        "conditional formal-order comparison",
        "not required for this bounded",
        "formal-order comparison",
        "Proof status: direct-route conditional Gauss6/FullVA proof closed",
        "full TFE stage replacement remain false",
        "No residual error theorem is accepted",
        "Seven residual-to-error obligations remain blocking",
        "not accepted dynamic order rows",
    ]:
        checks.check(text in proof_ledger, f"order proof ledger missing {text}")
    for text in [
        "\\section{Proof Status}",
        "Conditional order-six argument",
        "Order-preserving backend change",
        "theorem endpoint object is the velocity-level/KKT closure functional",
        "full_tfe_stage_replacement=false",
        "ORDER\\_PROOF\\_LEDGER.md",
    ]:
        checks.check(text in tex, f"paper is missing proof-status text: {text}")
    for text in [
        "proof status is conditional",
        "ORDER_PROOF_LEDGER.md",
        "open proof obligation",
    ]:
        checks.check(text in readme, f"paper README is missing proof-status text: {text}")


def check_claim_ledger(checks: Checks, summary: dict, ledger: str, smooth_pos: str, smooth_vel: str) -> None:
    runtime = f"{float(summary['runtime_sec']):.2f}"
    required_text = [
        EXPECTED_ASME_STATUS,
        "full_tfe_stage_replacement=false",
        "ASME Quantitative Evidence",
        "single_absolute_min_order=6.024",
        "single_absolute_max_stage_residual=3.664e-12",
        "double_method_min_order=6.089",
        "double_endpoint_position_constraint=7.034e-13",
        "double_endpoint_velocity_constraint=8.323e-12",
        "four_link_closed_loop_max_constraint_norm=1.052e-14",
        "four_link_reaction_max_dynamics_residual=1.338e-13",
        "slider_crank_closed_loop_max_constraint_norm=1.204e-15",
        "slider_crank_reaction_max_dynamics_residual=6.492e-15",
        "Proof/Status Evidence",
        "ORDER_PROOF_LEDGER.md",
        "conditional Gauss6/FullVA order-six argument",
        "order-preserving backend",
        "open proof obligation",
        "No residual error theorem is accepted",
        "Seven residual-to-error obligations remain blocking",
        "not accepted dynamic order rows",
        "lower_pair_recurrent_weak_closure_smoke",
        "lower_pair_recurrent_weak_closure_trajectory_smoke",
        "lower_pair_recurrent_weak_closure_h_sweep_smoke",
        "lower_pair_recurrent_terminal_blend_one_step_smoke",
        "lower_pair_recurrent_terminal_blend_h_sweep_smoke",
        "lower_pair_recurrent_terminal_component_one_step_smoke",
        "lower_pair_recurrent_terminal_component_h_sweep_smoke",
        "lower_pair_recurrent_history_gamma_h_sweep_smoke",
        "lower_pair_recurrent_weak_differential_audit",
        "lower_pair_recurrent_stage2_gradient_differential_audit",
        "lower_pair_recurrent_stage2_matrix_gradient_differential_audit",
        "6.737e-13",
        "6.484e-13",
        "2.483e-12",
        "4.463e-12",
        "9.998e-12",
        "2.337e-10",
        "2.319e-10",
        "7.994e-06",
        "8.234e-06",
        "-0.428",
        "5.317/6.782",
        "2.555/1.918",
        "7.845e-17",
        "9.479e-17",
        "6.071e-13",
        "3.533e-13",
        "3.260e-12",
        "4.766e-12",
        "3.049e-16",
        "2.941e-16",
        "4.413",
        "4.397",
        "0,0.25,0.5,0.75,1",
        "4.414",
        "8.234e-06",
        "0.9,0.99,0.999,1",
        "4.415",
        "4.678e-07",
        "component_2_release_0p999",
        "component_7_release_0p999",
        "1.766e-12",
        "3.456e-17",
        "1.234e-11",
        "98.4",
        "2.696e-16",
        "4.401",
        "history_gamma_h_sweep_smoke_present=true",
        "38.9",
        "2.586e-12",
        "9.365e-07",
        "1.451e-07",
        "4.402",
        "36.9",
        "3.869e-12",
        "1.452e-07",
        "recurrent_weak_differential_audit_present=true",
        "26.0",
        "0.899",
        "0.974",
        "1.456e-15",
        "6.872",
        "any_recurrent_weak_spans_terminal_bridge=false",
        "coefficient_gradient_gap_present=true",
        "stage2",
        "translation_velocity_v",
        "recurrent_stage2_gradient_differential_audit_present=true",
        "35.3",
        "curvature_plus_history_delta",
        "1e12",
        "1.246e-09",
        "recurrent_stage2_matrix_gradient_differential_audit_present=true",
        "68.1",
        "diagonal_plus_row_broadcast_feature",
        "0.898873",
        "4.005e-09",
        "46.6",
        "stage2_velocity_column_broadcast_feature",
        "0.585746",
        "1.460e-06",
        "51.2",
        "stage2_velocity_shifted_column_broadcast_feature",
        "0.576548",
        "27.8",
        "angular_velocity_w",
        "0.502991",
        "0.963038",
        "0.487135",
        "35.3",
        "stage2_angular_velocity_shifted_column_broadcast_feature",
        "0.752997",
        "0.660361",
        "0.978093",
        "stage2_velocity_angular_to_translation_cross_feature",
        "0.898812",
        "0.556004",
        "0.999994",
        "paper_endpoint_pose_positive_lagrange_z",
        "0.117782",
        "0.514237",
        "0.961546",
        "paper_endpoint_pose_stage02_convex_0p00_z",
        "paper_endpoint_pose_stage02_convex_0p05_z",
        "0.049317",
        "0.051890",
        "0.052472",
        "h-scaling",
        "stage02_convex_pose_velocity_0p01_z",
        "0.009512",
        "0.009978",
        "0.010085",
        "0.019205",
        "0.049390",
        "0.103464",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_z",
        "4.699e-06",
        "2.335e-06",
        "1.168e-06",
        "1.175e-05",
        "terminal-equivalent",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_accel_m1_z",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_accel_p1_z",
        "0.076159",
        "lie_position_u",
        "nonterminal span count `0`",
        "57.3",
        "stage2_velocity_feature_outer_stage2_velocity",
        "0.898720",
        "56.7",
        "stage2_velocity_diagonal_plus_hadamard_row_feature_stage2_velocity",
        "0.898530",
        "nonterminal mean-acceleration correction rows `18`",
        "generalized-velocity acceleration predictor rows `18`",
        "0.012376",
        "0.077874",
        "kinematic pose-slope predictor rows `26`",
        "stage02_convex_pose_velocity_0p02_poseslope_m0p1_z",
        "0.878519",
        "source-to-velocity lift predictor rows `34`",
        "source-to-velocity lift predictor elapsed `76.4`",
        "stage02_convex_pose_velocity_0p01_sourcelift_historydelta_p1_z",
        "stage02_convex_pose_velocity_0p01_sourcelift_source0_p1_z",
        "source-to-velocity lift predictor best corrected residual `0.609803`",
        "matrix-difference source-to-velocity lift predictor rows `14`",
        "matrix-difference source-to-velocity lift predictor elapsed `58.7`",
        "matrix-difference source-to-velocity lift predictor coarse residual `0.042593`",
        "matrix-difference source-to-velocity lift scale-sweep rows `26`",
        "matrix-difference source-to-velocity lift scale-sweep elapsed `92.5`",
        "stage02_convex_pose_velocity_0p01_sourceliftmatrixdiff_historydelta_p0p1_z",
        "matrix-difference source-to-velocity lift scale-sweep best corrected residual `0.009527`",
        "normalized-history source-law rows `10`",
        "normalized-history source-law elapsed `49.4`",
        "stage02_convex_pose_velocity_0p01_sourceliftmatrixdiff_historyunitdelta_p0p1_z",
        "normalized-history source-law best corrected residual `0.009590`",
        "near-terminal slope follow-up rows `4`",
        "near-terminal slope follow-up elapsed `25.8`",
        "near-terminal slope follow-up best law `stage02_convex_pose_velocity_slope_0p01_0p05_z`",
        "near-terminal slope follow-up best residual `0.677034`",
        "near-terminal curvature follow-up rows `4`",
        "near-terminal curvature follow-up elapsed `26.7`",
        "near-terminal curvature follow-up best law `stage02_convex_pose_velocity_curvature_0p01_0p05_0p10_z`",
        "near-terminal curvature follow-up best residual `0.871228`",
        "source/history coefficient-feature matrix follow-up rows `16`",
        "source/history coefficient-feature matrix follow-up elapsed `44.8`",
        "source/history coefficient-feature matrix follow-up best law `source_curvature_shifted_column_broadcast_feature`",
        "source/history coefficient-feature matrix follow-up best residual `0.898873`",
        "nonlinear curvature/history matrix-feature follow-up rows `16`",
        "nonlinear curvature/history matrix-feature follow-up elapsed `45.5`",
        "nonlinear curvature/history matrix-feature follow-up best law `source_curvature_minus_history_delta_diagonal_plus_row_broadcast_feature`",
        "nonlinear curvature/history matrix-feature follow-up best residual `0.898865`",
        "nonlinear curvature/history matrix-feature follow-up dominant family `translation_velocity_v`",
        "nonlinear curvature/history matrix-feature follow-up dominant fraction `0.556051`",
        "nonlinear curvature/history matrix-feature follow-up stage2 fraction `0.999996`",
        "nonlinear curvature/history matrix-feature follow-up span count `0`",
        "terminal-limit source-lift matrix-difference follow-up rows `8`",
        "terminal-limit source-lift matrix-difference follow-up elapsed `47.5`",
        "terminal-limit source-lift matrix-difference follow-up best law `stage02_convex_pose_velocity_extrapolate_0p01_0p02_sourceliftmatrixdiff_curvature_m0p1_z`",
        "terminal-limit source-lift matrix-difference follow-up best residual `5.298e-06`",
        "curvature source-lift scale refinement rows `11`",
        "curvature source-lift scale refinement elapsed `52.9`",
        "curvature source-lift scale refinement best law `stage02_convex_pose_velocity_extrapolate_0p01_0p02_sourceliftmatrixdiff_curvature_p0p01_z`",
        "curvature source-lift scale refinement best residual `5.298e-06`",
        "curvature source-lift scale refinement source curvature norm `1.076e-14`",
        "mean-acceleration bridge scale refinement rows `11`",
        "mean-acceleration bridge scale refinement elapsed `31.4`",
        "mean-acceleration bridge scale refinement best nonterminal law `stage02_convex_pose_velocity_extrapolate_0p01_0p02_accel_p0p01_z`",
        "mean-acceleration bridge scale refinement best nonterminal residual `0.000867721`",
        "mean-acceleration bridge scale refinement dominant family `lie_position_u`",
        "gauss endpoint-pose velocity-predictor rows `7`",
        "gauss endpoint-pose velocity-predictor elapsed `28.7`",
        "gauss endpoint-pose velocity-predictor best law `gauss_endpoint_pose_positive_lagrange_z`",
        "gauss endpoint-pose velocity-predictor residual `0.208599`",
        "gauss endpoint-pose velocity-predictor remaining dominant variable `lie_position_u`",
        "gauss endpoint-pose velocity-predictor remaining dominant fraction `0.650605`",
        "gauss endpoint-pose velocity-predictor stage fractions `0.524567/0.209731/0.265702`",
        "remaining gauss endpoint-pose rows `11`",
        "remaining gauss endpoint-pose elapsed `31.5`",
        "remaining gauss endpoint-pose best law `gauss_endpoint_pose_stage02_convex_0p00_z`",
        "remaining gauss endpoint-pose residual `0.172659`",
        "remaining gauss endpoint-pose independent target rank `6`",
        "remaining gauss endpoint-pose dominant variable `lie_position_u`",
        "remaining gauss endpoint-pose dominant fraction `0.952340`",
        "remaining gauss endpoint-pose stage fractions `0.320394/0.305625/0.373981`",
        "any_candidate_spans_terminal_bridge=false",
        "order_terminal_intersection_present=false",
        "terminal_velocity_closed=false",
        "accepted_h_sweep_present=false",
        f"{smooth_pos}/{smooth_vel}",
        runtime,
        "PAPER_CLAIM_LEDGER.md",
        "summary_v047.json",
        "cylindrical_chain_asme_gate.csv",
        "cylindrical_chain_asme_closed_loop_kinematic_fullva.csv",
        "cylindrical_chain_asme_closed_loop_reaction_dynamics.csv",
        "validate_paper_package.py",
        "validate_paper_claims.py",
        "validate_four_asme_minimal.py",
        "validate_full_tfe_gap.py",
        "FULL_TFE_REPLACEMENT_GAP_LEDGER.md",
        "validate_v047_outputs.py",
        "run_v047.py",
    ]
    for model in EXPECTED_MODELS:
        required_text.append(model)
    for text in required_text:
        checks.check(text in ledger, f"paper claim ledger missing {text}")


def check_full_tfe_gap_ledger(checks: Checks, gap_ledger: str) -> None:
    for text in [
        EXPECTED_ASME_STATUS,
        "full_tfe_stage_replacement=false",
        "accepted_h_sweep_present=false",
        "order_and_terminal_intersection_present=false",
        "accepted_candidate_count=0",
        "4.011e-16",
        "3.523",
        "7.378e-01",
        "9.815e-01",
        "0.899",
        "0.974",
        "1.456e-15",
        "any_recurrent_weak_spans_terminal_bridge=false",
        "stage-2 translational velocity",
        "stage-2 angular velocity",
        "27.8",
        "angular_velocity_w",
        "0.502991",
        "0.963038",
        "stage2_angular_velocity_shifted_column_broadcast_feature",
        "0.752997",
        "0.660361",
        "0.978093",
        "simple angular-only masking",
        "coupled translation/angular stage-2",
        "stage2_velocity_angular_to_translation_cross_feature",
        "0.898812",
        "0.556004",
        "0.999994",
        "translation/angular outer-cross",
        "paper_endpoint_pose_positive_lagrange_z",
        "0.117782",
        "0.514237",
        "0.961546",
        "endpoint-pose positive-Lagrange",
        "paper_endpoint_pose_stage02_convex_0p00_z",
        "terminal-bridge equivalent",
        "paper_endpoint_pose_stage02_convex_0p05_z",
        "0.049317",
        "0.051890",
        "0.052472",
        "stage02_convex_pose_velocity_0p01_z",
        "0.009512",
        "0.009978",
        "0.010085",
        "0.019205",
        "0.049390",
        "0.103464",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_z",
        "4.699e-06",
        "2.335e-06",
        "1.168e-06",
        "1.175e-05",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_accel_m1_z",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_accel_p1_z",
        "0.076159",
        "lie_position_u",
        "nonterminal_span_row_count=0",
        "stage02_convex_pose_velocity_slope_0p01_0p05_z",
        "0.677034",
        "25.8",
        "0.490108",
        "stage02_convex_pose_velocity_curvature_0p01_0p05_0p10_z",
        "0.871228",
        "26.7",
        "0.591909",
        "0.886084",
        "source_curvature_shifted_column_broadcast_feature",
        "0.898873",
        "44.8",
        "0.556060",
        "1.000000",
        "source_curvature_minus_history_delta_diagonal_plus_row_broadcast_feature",
        "0.898865",
        "45.5",
        "0.556051",
        "0.999996",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_sourceliftmatrixdiff_curvature_m0p1_z",
        "5.298e-06",
        "47.5",
        "translation_acceleration_a",
        "0.407672",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_sourceliftmatrixdiff_curvature_p0p01_z",
        "52.9",
        "1.076e-14",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_accel_p0p01_z",
        "0.000867721",
        "31.4",
        "0.706665",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_genaccel_p0p01_z",
        "0.000866899",
        "30.2",
        "0.701135",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_poseaccel_p0p01_z",
        "4.1835e-05",
        "29.9",
        "0.711570",
        "0.771337",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_poseaccel_p0p0005_z",
        "5.5898e-06",
        "30.0",
        "translation_acceleration_a",
        "0.350240",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_posevelaccel_p0p0005_m0p0001_z",
        "1.0173e-05",
        "30.7",
        "0.544660",
        "component-split pose-acceleration",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_transposeaccel_m0p01_z",
        "32.3+32.3",
        "9.6511e-06",
        "translation-only",
        "angular/Lie",
        "component-split velocity-acceleration",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_transvelaccel_m0p01_z",
        "2.138e-04",
        "31.8",
        "0.886603",
        "angvelaccel_p0p01",
        "0.000864560",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_transvelaccel_m0p0005_z",
        "9.8175e-06",
        "0.802349",
        "component-mixed pose/velocity Taylor",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_angpose_transvelaccel_p0p0005_m0p0005_z",
        "9.987e-06",
        "32.0",
        "0.774582",
        "0.625975",
        "stage-2-fixed/delta acceleration velocity-shift",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_transvelaccelstage2_m0p0005_z",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_transvelacceldelta20_m0p0005_z",
        "1.0119e-05",
        "nonfinal terminal velocity/source predictor",
        "nonfinal_velocity_terminal_euler1_z",
        "0.923466",
        "translation_velocity_v",
        "0.959959",
        "stage-2 source-to-velocity transport",
        "stage02_convex_pose_velocity_0p00_sourceliftmatrixdiff_historydelta_m0p1_z",
        "0.001251",
        "stage02_convex_pose_velocity_0p00_sourceliftmatrixdiff_historydelta_m0p01_z",
        "0.0001251",
        "stage02_convex_pose_velocity_0p00_sourceliftmatrixdiff_historydelta_m0p0001_z",
        "1.251e-06",
        "stage02_convex_pose_velocity_0p00_sourceliftmatrixdiff_historydelta_m0p0001_angposeaccel_p0p0001_z",
        "1.296e-06",
        "stage02_convex_pose_velocity_0p00_z",
        "1.327e-15",
        "31.7",
        "span_row_count=1",
        "local-span-not-full-TFE",
        "lower_pair_endpoint_pose_velocity_predictor_h_sweep_smoke",
        "8.124e-17",
        "4.142/2.305",
        "6.255e-06",
        "2.345/1.878",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_z",
        "projection_used=false",
        "1.254e-07",
        "6.412/3.775",
        "1.244e-08",
        "4.054/2.364",
        "stage02_convex_pose_velocity_0p01_terminalproj_z",
        "6.739e+08",
        "stage02_convex_pose_velocity_0p01_terminalproj_p0p1_z",
        "7.028e-06",
        "2.301/1.788",
        "stage02_convex_pose_velocity_0p01_terminalproj_p0p5_z",
        "1.321e-05",
        "2.158/1.433",
        "projection_used=true",
        "gauss_endpoint_pose_positive_lagrange_z",
        "0.208599",
        "28.7",
        "lie_position_u",
        "0.650605",
        "gauss_endpoint_pose_stage02_convex_0p00_z",
        "0.172659",
        "31.5",
        "0.952340",
        "stage02_convex_pose_velocity_0p01_accel_m0p1_z",
        "stage02_convex_pose_velocity_0p01_genaccel_m0p1_z",
        "0.012376",
        "0.077874",
        "simple nonterminal acceleration corrections",
        "stage02_convex_pose_velocity_0p02_poseslope_m0p1_z",
        "0.878519",
        "kinematic stage-pose-slope velocity predictors",
        "source-to-velocity lift",
        "current-pose",
        "stage02_convex_pose_velocity_0p01_sourcelift_historydelta_p1_z",
        "stage02_convex_pose_velocity_0p01_sourcelift_source0_p1_z",
        "0.609803",
        "matrix-difference source-to-velocity lift",
        "0.042593",
        "58.7",
        "stage02_convex_pose_velocity_0p01_sourceliftmatrixdiff_historydelta_p0p1_z",
        "0.009527",
        "92.5",
        "normalized-history",
        "stage02_convex_pose_velocity_0p01_sourceliftmatrixdiff_historyunitdelta_p0p1_z",
        "0.009590",
        "49.4",
        "any_candidate_spans_terminal_bridge=false",
        "simple source/history scalar coefficient-gradient",
        "target-free row/column matrix coefficient-gradient",
        "target-free active-velocity coefficient-gradient",
        "revised analytical weak-row formula",
        "nonlinear recurrent history source law",
        "validate_full_tfe_gap.py",
    ]:
        checks.check(text in gap_ledger, f"full TFE gap ledger missing {text}")


def check_full_tfe_repair_spec(checks: Checks, repair_spec: str) -> None:
    for text in [
        "paper_tfe_lower_pair_source_free_recurrent_weak_closure_rows_jax",
        "residual_cylindrical_chain_endpoint_tfe_paper_lower_pair_source_free_recurrent_weak_closure_candidate",
        "coefficient-gradient closure",
        "V047_TARGET_AUDIT=lower_pair_recurrent_weak_closure_smoke",
        "V047_TARGET_AUDIT=lower_pair_recurrent_weak_closure_trajectory_smoke",
        "V047_TARGET_AUDIT=lower_pair_recurrent_weak_closure_h_sweep_smoke",
        "V047_TARGET_AUDIT=lower_pair_recurrent_terminal_blend_one_step_smoke",
        "V047_TARGET_AUDIT=lower_pair_recurrent_terminal_blend_h_sweep_smoke",
        "V047_TARGET_AUDIT=lower_pair_recurrent_terminal_component_one_step_smoke",
        "V047_TARGET_AUDIT=lower_pair_recurrent_terminal_component_h_sweep_smoke",
        "V047_TARGET_AUDIT=lower_pair_recurrent_history_gamma_h_sweep_smoke",
        "V047_TARGET_AUDIT=lower_pair_recurrent_weak_differential_audit",
        "V047_TARGET_AUDIT=lower_pair_recurrent_stage2_gradient_differential_audit",
        "V047_TARGET_AUDIT=lower_pair_recurrent_stage2_matrix_gradient_differential_audit",
        "V047_RECURRENT_HISTORY_GAMMA_POLICIES",
        "V047_RECURRENT_HISTORY_GAMMA_RELEASES",
        "V047_RECURRENT_WEAK_DIFFERENTIAL_CASES",
        "V047_RECURRENT_WEAK_DIFFERENTIAL_HISTORY_MODES",
        "V047_RECURRENT_STAGE2_GRADIENT_FEATURES",
        "V047_RECURRENT_STAGE2_GRADIENT_GAINS",
        "V047_RECURRENT_STAGE2_MATRIX_LAWS",
        "V047_RECURRENT_STAGE2_MATRIX_GAINS",
        "diagnostic_smoke_only=true",
        "6.737e-13",
        "6.484e-13",
        "2.483e-12",
        "4.463e-12",
        "9.998e-12",
        "2.337e-10",
        "2.319e-10",
        "7.994e-06",
        "8.234e-06",
        "-0.428",
        "5.317/6.782",
        "2.555/1.918",
        "7.845e-17",
        "9.479e-17",
        "6.071e-13",
        "3.533e-13",
        "4.766e-12",
        "8.105e-06",
        "3.049e-16",
        "2.941e-16",
        "4.413",
        "4.397",
        "3.204/-0.428",
        "0,0.25,0.5,0.75,1",
        "60",
        "4.414",
        "8.234e-06",
        "0.9,0.99,0.999,1",
        "48",
        "4.415",
        "4.678e-07",
        "one_step_component_gamma_sweep_present=true",
        "1.766e-12",
        "component_2_release_0p999",
        "3.456e-17",
        "component_7_release_0p999",
        "1.234e-11",
        "component_trajectory_h_sweep_smoke_present=true",
        "98.4",
        "2.696e-16",
        "4.401",
        "history_gamma_h_sweep_smoke_present=true",
        "38.9",
        "2.586e-12",
        "9.365e-07",
        "1.451e-07",
        "4.402",
        "36.9",
        "3.869e-12",
        "1.452e-07",
        "recurrent_weak_differential_audit_present=true",
        "26.0",
        "0.899",
        "0.974",
        "1.456e-15",
        "6.872",
        "any_recurrent_weak_spans_terminal_bridge=false",
        "coefficient_gradient_gap_present=true",
        "stage2",
        "translation_velocity_v",
        "recurrent_stage2_gradient_differential_audit_present=true",
        "35.3",
        "curvature_plus_history_delta",
        "1e12",
        "1.246e-09",
        "2.861e+04",
        "recurrent_stage2_matrix_gradient_differential_audit_present=true",
        "68.1",
        "diagonal_plus_row_broadcast_feature",
        "0.898873",
        "4.005e-09",
        "9.197e+04",
        "46.6",
        "stage2_velocity_column_broadcast_feature",
        "0.585746",
        "1.460e-06",
        "3.353e+07",
        "51.2",
        "stage2_velocity_shifted_column_broadcast_feature",
        "0.576548",
        "27.8",
        "full_run_invoked=false",
        "artifact_written=false",
        "summary_updated=false",
        "0.909693",
        "angular_velocity_w",
        "0.502991",
        "0.963038",
        "0.487135",
        "0.964696",
        "stage2_angular_velocity_shifted_column_broadcast_feature",
        "0.752997",
        "0.660361",
        "0.978093",
        "coupled translation/angular stage-2 weak-row",
        "stage2_velocity_angular_to_translation_cross_feature",
        "0.898812",
        "0.556004",
        "0.999994",
        "translation/angular outer-cross",
        "paper_endpoint_pose_positive_lagrange_z",
        "0.117782",
        "0.514237",
        "0.961546",
        "endpoint-pose generalized-velocity predictor",
        "paper_endpoint_pose_stage02_convex_0p00_z",
        "terminal_bridge_equivalent_predictor=true",
        "paper_endpoint_pose_stage02_convex_0p05_z",
        "0.049317",
        "0.051890",
        "0.052472",
        "h-scaling",
        "stage02_convex_pose_velocity_0p01_z",
        "0.009512",
        "0.009978",
        "0.010085",
        "0.019205",
        "0.049390",
        "0.103464",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_z",
        "4.699e-06",
        "2.335e-06",
        "1.168e-06",
        "1.175e-05",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_accel_m1_z",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_accel_p1_z",
        "0.076159",
        "lie_position_u",
        "any_nonterminal_candidate_spans_terminal_bridge=false",
        "stage02_convex_pose_velocity_slope_0p01_0p05_z",
        "0.677034",
        "25.8",
        "0.490108",
        "stage02_convex_pose_velocity_curvature_0p01_0p05_0p10_z",
        "0.871228",
        "26.7",
        "0.591909",
        "0.886084",
        "source_curvature_shifted_column_broadcast_feature",
        "0.898873",
        "44.8",
        "0.556060",
        "1.000000",
        "source_curvature_minus_history_delta_diagonal_plus_row_broadcast_feature",
        "0.898865",
        "45.5",
        "0.556051",
        "0.999996",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_sourceliftmatrixdiff_curvature_m0p1_z",
        "5.298e-06",
        "47.5",
        "translation_acceleration_a",
        "0.407672",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_sourceliftmatrixdiff_curvature_p0p01_z",
        "52.9",
        "1.076e-14",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_accel_p0p01_z",
        "0.000867721",
        "31.4",
        "0.706665",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_genaccel_p0p01_z",
        "0.000866899",
        "30.2",
        "0.701135",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_poseaccel_p0p01_z",
        "4.1835e-05",
        "29.9",
        "0.711570",
        "0.771337",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_poseaccel_p0p0005_z",
        "5.5898e-06",
        "30.0",
        "translation_acceleration_a",
        "0.350240",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_posevelaccel_p0p0005_m0p0001_z",
        "1.0173e-05",
        "30.7",
        "0.544660",
        "component-split pose-acceleration",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_transposeaccel_m0p01_z",
        "32.3+32.3",
        "9.6511e-06",
        "angular/Lie",
        "component-split velocity-acceleration",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_transvelaccel_m0p01_z",
        "2.138e-04",
        "31.8",
        "0.886603",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_transvelaccel_m0p0005_z",
        "9.8175e-06",
        "31.4",
        "0.802349",
        "0.000864560",
        "component-mixed pose/velocity Taylor",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_angpose_transvelaccel_p0p0005_m0p0005_z",
        "9.987e-06",
        "32.0",
        "0.774582",
        "0.625975",
        "stage-2-fixed/delta acceleration velocity-shift",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_transvelaccelstage2_m0p0005_z",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_transvelacceldelta20_m0p0005_z",
        "1.0119e-05",
        "nonfinal terminal velocity/source predictor",
        "nonfinal_velocity_terminal_euler1_z",
        "0.923466",
        "translation_velocity_v",
        "0.959959",
        "stage-2 source-to-velocity transport",
        "stage02_convex_pose_velocity_0p00_sourceliftmatrixdiff_historydelta_m0p1_z",
        "0.001251",
        "stage02_convex_pose_velocity_0p00_sourceliftmatrixdiff_historydelta_m0p01_z",
        "0.0001251",
        "stage02_convex_pose_velocity_0p00_sourceliftmatrixdiff_historydelta_m0p0001_z",
        "1.251e-06",
        "stage02_convex_pose_velocity_0p00_sourceliftmatrixdiff_historydelta_m0p0001_angposeaccel_p0p0001_z",
        "1.296e-06",
        "stage02_convex_pose_velocity_0p00_z",
        "1.327e-15",
        "31.7",
        "span_row_count=1",
        "local-span-not-full-TFE",
        "lower_pair_endpoint_pose_velocity_predictor_h_sweep_smoke",
        "8.124e-17",
        "4.142/2.305",
        "6.255e-06",
        "2.345/1.878",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_z",
        "projection_used=false",
        "1.254e-07",
        "6.412/3.775",
        "1.244e-08",
        "4.054/2.364",
        "stage02_convex_pose_velocity_0p01_terminalproj_z",
        "6.739e+08",
        "stage02_convex_pose_velocity_0p01_terminalproj_p0p1_z",
        "7.028e-06",
        "2.301/1.788",
        "stage02_convex_pose_velocity_0p01_terminalproj_p0p5_z",
        "1.321e-05",
        "2.158/1.433",
        "projection_used=true",
        "gauss_endpoint_pose_positive_lagrange_z",
        "0.208599",
        "28.7",
        "lie_position_u",
        "0.650605",
        "gauss_endpoint_pose_stage02_convex_0p00_z",
        "0.172659",
        "31.5",
        "0.952340",
        "57.3",
        "stage2_velocity_feature_outer_stage2_velocity",
        "0.898720",
        "56.7",
        "stage2_velocity_diagonal_plus_hadamard_row_feature_stage2_velocity",
        "0.898530",
        "stage02_convex_pose_velocity_0p01_accel_m0p1_z",
        "stage02_convex_pose_velocity_0p01_genaccel_m0p1_z",
        "0.012376",
        "0.077874",
        "generalized-velocity Taylor",
        "stage02_convex_pose_velocity_0p02_poseslope_m0p1_z",
        "0.878519",
        "kinematic pose-slope",
        "source-to-velocity lift",
        "stage02_convex_pose_velocity_0p01_sourcelift_historydelta_p1_z",
        "stage02_convex_pose_velocity_0p01_sourcelift_source0_p1_z",
        "0.609803",
        "76.4",
        "matrix-difference source-to-velocity lift",
        "0.042593",
        "58.7",
        "stage02_convex_pose_velocity_0p01_sourceliftmatrixdiff_historydelta_p0p1_z",
        "0.009527",
        "92.5",
        "normalized-history",
        "stage02_convex_pose_velocity_0p01_sourceliftmatrixdiff_historyunitdelta_p0p1_z",
        "0.009590",
        "49.4",
        "any_candidate_spans_terminal_bridge=false",
        "order_terminal_intersection_present=false",
        "any_gamma_terminal_velocity_closed=true",
        "terminal_velocity_closed=false",
        "h=[0.04,0.02,0.01]",
        "h=0.005",
        "full_tfe_stage_replacement=false",
        "validate_full_tfe_repair_spec.py",
    ]:
        checks.check(text in repair_spec, f"full TFE repair spec missing {text}")


def check_current_status_cn(checks: Checks, summary: dict, status_cn: str) -> None:
    smooth = summary["convergence"]["cases"]["cylindrical_smooth"]["projected_velocity"]
    final_stage = summary.get("endpoint_tfe_paper_lower_pair_source_free_final_stage_velocity_closure_audit", {})
    final_smooth = final_stage.get("cases", {}).get("cylindrical_smooth", {})
    runtime = f"{float(summary['runtime_sec']):.2f}"
    smooth_orders = f"{rounded(float(smooth['position_order']))}/{rounded(float(smooth['velocity_order']))}"
    final_stage_position_order = rounded(float(final_smooth.get("position_order", 0.0)))

    checks.check(summary.get("asme_gate", {}).get("status") == EXPECTED_ASME_STATUS, "summary ASME gate status changed")
    checks.check(final_stage.get("full_tfe_stage_replacement") is False, "final-stage closure unexpectedly claims full TFE")
    for text in [
        "v047 当前状态说明",
        "原 paper / local target vs accepted v047 claim",
        "Source-paper/local target",
        "Accepted v047 claim",
        "Not claimed",
        "conditional order-comparison",
        "complete source-paper residual reproduction",
        "every source-paper",
        "single_pendulum",
        "double_pendulum",
        "four_link",
        "slider_crank",
        "Gauss6/FullVA",
        smooth_orders,
        "TFE",
        "temporal finite element",
        "m=3",
        "expected order 是 `5`",
        "full_tfe_stage_replacement=false",
        "132-row stage residual",
        "source-free",
        "endpoint-boundary source",
        "terminal-row replacement",
        "output projection",
        "target-direction oracle",
        final_stage_position_order,
        runtime,
        "validate_paper_package.py",
        "validate_paper_claims.py",
        "validate_four_asme_minimal.py",
        "validate_full_tfe_gap.py",
        "validate_full_tfe_repair_spec.py",
        "validate_v047_outputs.py",
        "run_v047.py",
        "full_tfe_stage_replacement_missing",
        "revised analytical weak-row formula",
        "nonlinear recurrent history source law",
        "stage02_convex_pose_velocity_curvature_0p01_0p05_0p10_z",
        "0.871228",
        "26.7",
        "source_curvature_shifted_column_broadcast_feature",
        "0.898873",
        "44.8",
        "source_curvature_minus_history_delta_diagonal_plus_row_broadcast_feature",
        "0.898865",
        "45.5",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_sourceliftmatrixdiff_curvature_m0p1_z",
        "5.298e-06",
        "47.5",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_sourceliftmatrixdiff_curvature_p0p01_z",
        "52.9",
        "1.076e-14",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_accel_p0p01_z",
        "0.000867721",
        "31.4",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_genaccel_p0p01_z",
        "0.000866899",
        "30.2",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_poseaccel_p0p01_z",
        "4.1835e-05",
        "29.9",
        "0.711570",
        "0.771337",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_poseaccel_p0p0005_z",
        "5.5898e-06",
        "30.0",
        "translation_acceleration_a",
        "0.350240",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_posevelaccel_p0p0005_m0p0001_z",
        "1.0173e-05",
        "30.7",
        "0.544660",
        "component-split velocity-acceleration",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_transvelaccel_m0p01_z",
        "2.138e-04",
        "31.8",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_transvelaccel_m0p0005_z",
        "9.8175e-06",
        "31.4",
        "0.802349",
        "component-mixed pose/velocity Taylor",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_angpose_transvelaccel_p0p0005_m0p0005_z",
        "9.987e-06",
        "32.0",
        "0.774582",
        "stage-2-fixed/delta acceleration velocity-shift",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_transvelaccelstage2_m0p0005_z",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_transvelacceldelta20_m0p0005_z",
        "1.0119e-05",
        "nonfinal terminal velocity/source predictor",
        "nonfinal_velocity_terminal_euler1_z",
        "0.923466",
        "translation_velocity_v",
        "0.959959",
        "stage-2 source-to-velocity transport",
        "stage02_convex_pose_velocity_0p00_sourceliftmatrixdiff_historydelta_m0p1_z",
        "0.001251",
        "stage02_convex_pose_velocity_0p00_sourceliftmatrixdiff_historydelta_m0p01_z",
        "0.0001251",
        "stage02_convex_pose_velocity_0p00_sourceliftmatrixdiff_historydelta_m0p0001_z",
        "1.251e-06",
        "stage02_convex_pose_velocity_0p00_sourceliftmatrixdiff_historydelta_m0p0001_angposeaccel_p0p0001_z",
        "1.296e-06",
        "stage02_convex_pose_velocity_0p00_z",
        "1.327e-15",
        "31.7",
        "span_row_count=1",
        "local-span-not-full-TFE",
        "lower_pair_endpoint_pose_velocity_predictor_h_sweep_smoke",
        "8.124e-17",
        "4.142/2.305",
        "6.255e-06",
        "2.345/1.878",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_z",
        "projection_used=false",
        "1.254e-07",
        "6.412/3.775",
        "1.244e-08",
        "4.054/2.364",
        "stage02_convex_pose_velocity_0p01_terminalproj_z",
        "6.739e+08",
        "stage02_convex_pose_velocity_0p01_terminalproj_p0p1_z",
        "7.028e-06",
        "2.301/1.788",
        "stage02_convex_pose_velocity_0p01_terminalproj_p0p5_z",
        "1.321e-05",
        "2.158/1.433",
        "projection_used=true",
        "gauss_endpoint_pose_positive_lagrange_z",
        "0.208599",
        "28.7",
        "lie_position_u",
        "0.650605",
        "gauss_endpoint_pose_stage02_convex_0p00_z",
        "0.172659",
        "31.5",
        "0.952340",
        "stage-2 active translation/angular cross",
        "stage2_velocity_symmetric_translation_angular_cross_feature",
        "0.898843",
        "50.9",
        "0.556036",
        "0.999999",
        "non-stage-2 mean/source/history feature matrix",
        "stage01_mean_velocity_diagonal_plus_row_broadcast_feature",
        "0.827381",
        "36.5",
        "0.571311",
        "0.991949",
        "h=[0.04,0.02,0.01]",
        "reference_h=0.005",
    ]:
        checks.check(text in status_cn, f"Chinese status note missing {text}")


def check_figures_and_pdf(checks: Checks, tex: str) -> int:
    figures = sorted(set(re.findall(r"\\plotfigure\{\\figpath/([^}]+)\}", tex)))
    checks.check(bool(figures), "paper has no plotfigure references")
    for figure in figures:
        path = PAPER / "figures" / figure
        checks.check(path.exists(), f"missing figure snapshot: {figure}")
        if path.exists():
            checks.check(path.stat().st_size > 1000, f"figure snapshot is too small: {figure}")
    pdf = PAPER / "main.pdf"
    checks.check(pdf.exists(), "paper PDF is missing")
    if pdf.exists():
        checks.check(pdf.stat().st_size > 1_000_000, "paper PDF is unexpectedly small")
    return len(figures)


def main() -> int:
    checks = Checks()
    try:
        tex = read_text(PAPER / "main.tex")
        readme = read_text(PAPER / "README.md")
        ledger = read_text(PAPER / "PAPER_CLAIM_LEDGER.md")
        reviewer_checklist = read_text(PAPER / "REVIEWER_CHECKLIST.md")
        gap_ledger = read_text(PIPELINE / "FULL_TFE_REPLACEMENT_GAP_LEDGER.md")
        repair_spec = read_text(PIPELINE / "FULL_TFE_REPAIR_SPEC.md")
        proof_ledger = read_text(ROOT / "docs" / "ORDER_PROOF_LEDGER.md")
        status_cn = read_text(PAPER / "CURRENT_STATUS_CN.md")
        quickstart = read_text(ROOT / "docs" / "VALIDATION_QUICKSTART.md")
        current_pipeline_contract = read_text(ROOT / "CURRENT_PIPELINE_CONTRACT.md")
        claim_boundary = read_json(PAPER / "CLAIM_BOUNDARY.json")
        summary = read_summary()
        check_asme_claim(checks, summary, tex)
        check_asme_quantitative_claim(checks, summary, tex, readme)
        smooth_pos, smooth_vel = check_convergence_claim(checks, summary, tex)
        check_tfe_boundary(checks, summary, tex)
        check_reproducibility_claim(checks, summary, tex, readme)
        check_better_integrator_boundary(checks, tex, readme, reviewer_checklist, ledger, status_cn)
        check_tfe_terminology_boundary(checks, tex, readme, status_cn, quickstart)
        check_current_pipeline_contract(checks, current_pipeline_contract, claim_boundary)
        check_claim_boundary_json(checks, summary, claim_boundary)
        check_reviewer_checklist(checks, summary, reviewer_checklist, tex, readme)
        check_order_proof_status(checks, proof_ledger, tex, readme)
        check_claim_ledger(checks, summary, ledger, smooth_pos, smooth_vel)
        check_full_tfe_gap_ledger(checks, gap_ledger)
        check_full_tfe_repair_spec(checks, repair_spec)
        check_current_status_cn(checks, summary, status_cn)
        figure_count = check_figures_and_pdf(checks, tex)
    except Exception as exc:  # noqa: BLE001 - command-line validator reports fatal read/parse issues.
        print("v047 paper claim validation: FAIL")
        print(f"fatal={exc}")
        return 1

    if checks.errors:
        print("v047 paper claim validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("v047 paper claim validation: PASS")
    print(f"asme_gate_status={summary['asme_gate']['status']}")
    print(f"smooth_projected_orders={smooth_pos}/{smooth_vel}")
    print("full_tfe_stage_replacement=False")
    print("claim_ledger_checked=True")
    print("claim_boundary_json_checked=True")
    print("claim_boundary_asme_acceptance_checked=True")
    print("claim_boundary_full_tfe_gap_checked=True")
    print("claim_boundary_terminology_checked=True")
    print("claim_boundary_order_conventions_checked=True")
    print("claim_boundary_remaining_caveats_checked=True")
    print("current_pipeline_contract_checked=True")
    print("tfe_terminology_checked=True")
    print(f"figures_checked={figure_count}")
    print(f"pdf_size_bytes={(PAPER / 'main.pdf').stat().st_size}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
