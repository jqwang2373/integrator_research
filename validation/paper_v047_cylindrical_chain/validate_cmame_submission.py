#!/usr/bin/env python3
"""Read-only CMAME/Elsevier submission preflight for the v047 paper package."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


PAPER = Path(__file__).resolve().parent
from paper_paths import LATEX, package_path as manuscript_path
ROOT = PAPER.parent
PIPELINE = ROOT.parent / "numerics" / "v047_cylindrical_chain_pipeline"
RESULTS = PIPELINE / "results"

EXPECTED_EXAMPLES = {"single_pendulum", "double_pendulum", "four_link", "slider_crank"}
EXPECTED_DYNAMIC_ORDER_EXAMPLES = {"single_pendulum", "double_pendulum"}
EXPECTED_COVERAGE_ONLY_EXAMPLES = {"four_link", "slider_crank"}
EXPECTED_CAVEATS = {
    "sparse_speed_quantified",
    "full_tfe_stage_replacement_missing",
    "sharp_friction_coarse_order_reduction_ultra_recovered",
}
FLAT = LATEX / "cmame_submission_flat"
FLAT_FIGURES = [
    "Figure_1_convergence.png",
    "Figure_2_asme_lower_pair_graph_bridge.png",
    "Figure_3_asme_closed_loop_kinematic_fullva.png",
    "Figure_4_order_closure_blend.png",
    "Figure_5_velocity_compression.png",
    "Figure_6_sparse_speed_gap.png",
    "Figure_7_strict_common_reference_work_precision.png",
    "Figure_8_claim_boundary_limitations.png",
    "Figure_9_coarse_baseline_work_precision.png",
    "Figure_10_closed_loop_true_dynamic_order.png",
    "Figure_11_method_stage_architecture.png",
    "Figure_12_all_method_result_matrix.png",
    "Figure_13_work_precision_compendium.png",
]
EXPECTED_OC6_REOPEN_LATEST_EXTERNAL_PROBE = "2026-06-21/9/0/0/4/False/False"


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


def read_json(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(path)
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def contains_normalized(text: str, token: str) -> bool:
    return token in text or " ".join(token.split()) in " ".join(text.split())


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


def abstract_word_count(tex: str) -> int:
    match = re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", tex, flags=re.S)
    if not match:
        return 10**9
    stripped = re.sub(r"\\[a-zA-Z]+(?:\{[^{}]*\})?", " ", match.group(1))
    stripped = re.sub(r"[$^_{}\\]", " ", stripped)
    return len(re.findall(r"[A-Za-z0-9]+(?:[-/][A-Za-z0-9]+)?", stripped))


def keyword_count(tex: str) -> int:
    match = re.search(r"\\begin\{keyword\}(.*?)\\end\{keyword\}", tex, flags=re.S)
    if not match:
        return 0
    return len([item for item in match.group(1).split(r"\sep") if item.strip()])


def highlight_lines(text: str) -> list[str]:
    return [line[2:].strip() for line in text.splitlines() if line.startswith("- ")]


def check_one_log_clean(checks: Checks, log_path: Path, label: str) -> None:
    checks.check(log_path.exists() and log_path.stat().st_size > 0, f"{label} missing or empty")
    if not log_path.exists():
        return
    patterns = [
        r"Overfull",
        r"LaTeX Warning",
        r"Package .*Warning",
        r"pdfTeX warning",
        r"Undefined control sequence",
        r"Emergency stop",
    ]
    matches = [
        line
        for line in log_path.read_text(encoding="utf-8", errors="replace").splitlines()
        if any(re.search(pattern, line) for pattern in patterns)
    ]
    checks.check(not matches, f"{label} has warnings/errors: {matches[:4]}")


def check_log_clean(checks: Checks) -> None:
    check_one_log_clean(checks, LATEX / "main_cmame.log", "main_cmame.log")
    check_one_log_clean(checks, FLAT / "main_cmame_submission.log", "flat main_cmame_submission.log")


def check_files(checks: Checks) -> None:
    for label in [
        "main_cmame.tex",
        "main_cmame.pdf",
        "main_cmame.log",
        "highlights_cmame.txt",
        "declarations_cmame.md",
        "CMAME_SUBMISSION_CHECKLIST.md",
        "CMAME_SUBMISSION_READINESS_AUDIT.md",
        "CMAME_SUBMISSION_READINESS_REVIEW.md",
        "CMAME_BLOCKER_CLOSURE_GATE.md",
        "CMAME_BLOCKER_CLOSURE_GATE.json",
        "CMAME_EXTERNAL_BASELINE_GATE.md",
        "CMAME_EXTERNAL_BASELINE_GATE.json",
        "EXTERNAL_SAME_TEST_RUN_QUEUE.md",
        "EXTERNAL_SAME_TEST_RUN_QUEUE.json",
        "CMAME_PROOF_CONTRACT_GATE.md",
        "CMAME_PROOF_CONTRACT_GATE.json",
        "CMAME_VISUAL_LEGIBILITY_AUDIT.md",
        "CMAME_VISUAL_LEGIBILITY_AUDIT.json",
        "CMAME_RELATED_WORK_AUDIT.md",
        "CMAME_RELATED_WORK_AUDIT.json",
        "CMAME_PROSE_RESIDUE_AUDIT.md",
        "CMAME_PROSE_RESIDUE_AUDIT.json",
        "REFERENCE_METADATA_AUDIT.md",
        "REFERENCE_METADATA_AUDIT.json",
        "DYNAMIC_ROW_ORACLE_GATE.md",
        "DYNAMIC_ROW_ORACLE_GATE.json",
        "README_CMAME_FLAT_SUBMISSION.md",
        "cmame_submission_flat.zip",
        "CLAIM_BOUNDARY.json",
        "SOURCE_PAPER_COMPARISON.md",
        "KISSEL_NEGRUT_CODE_INVENTORY.md",
        "PROOF_EVIDENCE_MATRIX.md",
        "PROOF_NUMERICAL_SCALE_AUDIT.md",
        "PROOF_NUMERICAL_SCALE_AUDIT.json",
        "PROOF_SOLVER_SCALE_AUDIT.md",
        "PROOF_SOLVER_SCALE_AUDIT.json",
        "ORDER_ACCEPTANCE_GATE.md",
        "ORDER_ACCEPTANCE_GATE.json",
        "validate_cmame_blocker_closure_gate.py",
        "validate_cmame_external_baseline_gate.py",
        "validate_external_same_test_run_queue.py",
        "validate_cmame_proof_contract_gate.py",
        "validate_cmame_visual_legibility_audit.py",
        "validate_cmame_related_work_audit.py",
        "validate_cmame_prose_residue_audit.py",
        "validate_dynamic_row_oracle_gate.py",
        "validate_proof_numerical_scale_audit.py",
        "validate_proof_solver_scale_audit.py",
        "SUBMISSION_ARTIFACT_MANIFEST.json",
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
    ]:
        path = manuscript_path(label)
        checks.check(path.exists() and path.stat().st_size > 0, f"missing or empty file: {label}")
    pdf_path = LATEX / "main_cmame.pdf"
    if pdf_path.exists():
        checks.check(pdf_path.stat().st_size > 100_000, "main_cmame.pdf is unexpectedly small")
    for label in [
        "main_cmame_submission.tex",
        "main_cmame_submission.pdf",
        "main_cmame_submission.log",
        "highlights_cmame.txt",
        "declarations_cmame.md",
        *FLAT_FIGURES,
    ]:
        path = FLAT / label
        checks.check(path.exists() and path.stat().st_size > 0, f"missing or empty flat submission file: {label}")
    flat_pdf = FLAT / "main_cmame_submission.pdf"
    if flat_pdf.exists():
        checks.check(flat_pdf.stat().st_size > 100_000, "flat CMAME PDF is unexpectedly small")


def check_tex(checks: Checks, tex: str, boundary: dict, summary: dict) -> None:
    primary = boundary.get("primary_claim", {})
    comparator = boundary.get("comparator", {})
    asme = boundary.get("asme_acceptance", {})
    caveats = set(boundary.get("open_caveats", []))

    checks.check(r"\documentclass[preprint,12pt]{elsarticle}" in tex, "CMAME manuscript does not use elsarticle preprint class")
    checks.check(
        r"\journal{Computer Methods in Applied Mechanics and Engineering}" in tex,
        "CMAME journal marker missing",
    )
    checks.check(r"\begin{frontmatter}" in tex and r"\end{frontmatter}" in tex, "frontmatter missing")
    checks.check(r"\title{A Conditional Sixth-Order Lie-Group FullVA Integrator for Lower-Pair Mechanisms}" in tex, "title changed")
    checks.check(r"\author[inst1]{Jingquan Wang\corref{cor1}}" in tex, "author/corresponding author marker missing")
    checks.check(r"\affiliation[inst1]" in tex, "affiliation missing")
    for token in ["University of Wisconsin--Madison", "1513 University Avenue", "Madison", "53706"]:
        checks.check(token in tex, f"affiliation missing postal token: {token}")
    checks.check(abstract_word_count(tex) <= 250, "abstract exceeds 250 words")
    checks.check(1 <= keyword_count(tex) <= 7, "keyword count is outside 1 to 7")

    required_tokens = [
        "Computer Methods in Applied Mechanics and Engineering",
        "A Conditional Sixth-Order Lie-Group FullVA Integrator for Lower-Pair Mechanisms",
        "Related work",
        "The relevant literature separates into six clusters",
        "variational and symplectic integrators",
        "nonsmooth contact and friction solvers",
        "does not claim a new nonsmooth contact integrator",
        "Mathematical setting and definitions",
        "Nomenclature",
        "Main symbols used in the manuscript",
        "\\newtheorem{definition}{Definition}",
        "FullVA lower-pair residual",
        "Accepted method path",
        "Full-\\tfe{} stage replacement",
        "Validation protocol",
        "Algorithmic form of one \\method{} step",
        "Proof-dependency map for Proposition",
        "Cross-paper evidence accumulated",
        "Bounded common-reference diagnostic work/precision",
        "fixed-reference diagnostic gap count is zero",
        "strict_common_reference_work_precision.png",
        "claim_boundary_limitations.png",
        "Claim-boundary and limitation map",
        "coarse_baseline_work_precision.png",
        "Coarse-first baseline and work/precision diagnostics",
        "closed_loop_true_dynamic_order.png",
        "Closed-loop coarse-window trajectory diagnostics",
        "method_stage_architecture.png",
        "Accepted \\method{} one-step architecture",
        "does not require a default $10^{-4}$ step-size sweep",
        "without making $10^{-4}$ a default policy",
        "solver-scale check of the existing summary residuals",
        "not a scaled",
        "tolerance proof",
        "not an external-superiority claim",
        "Accepted dynamic order rows",
        "Coverage-only for dynamic order",
        "Order-estimate acceptance policy used in the numerical section",
        "Mechanism-coverage and work/precision evidence",
        "External-baseline evidence in progress",
        "Order-scope check",
        "not a default execution policy",
        "32 complete, 0 partial",
        "external same-test campaign remains incomplete",
        "paper makes no external-superiority claim",
        "Benchmark-policy dictionary",
        "bounded common-reference policy",
        "fixes $T=0.1$, $h\\in\\{0.1,0.05,0.025\\}$",
        "$h_{\\rm ref}=0.0125$ for every runnable method",
        "single-pendulum row uses",
        "analytic exact final state",
        "double-pendulum row uses the local \\method{}",
        "final $L^\\infty$ error",
        "four-link and slider-crank rows use closed-loop",
        "true-dynamic common-reference trajectories",
        "Source-policy rows, by contrast",
        "horizon, time grid, reference solution, error norm, tolerance, and output",
        "Required same-test comparisons and current external-suite claim boundary",
        "Claim allowed now",
        "Formula-order comparator only",
        "Coarse-first and common-reference evidence only",
        "Diagnostic boundaries and limitations",
        "Supplementary source package",
        "cmame_submission_flat",
        "Sparse backend speed-gap diagnostic",
        "order_closure_blend.png",
        "velocity_compression.png",
        "sparse_speed_gap.png",
        "Conditional order comparison",
        r"\label{prop:order-comparison}",
        "higher formal order",
        "conditional formal-order comparison",
        "conditional sixth-order Lie-group FullVA theorem",
        r"\label{thm:g6fullva-order}",
        "position and velocity orders 7.161 and 7.066",
        "single pendulum",
        "double pendulum",
        "four-link",
        "slider-crank",
        "p_{\\mathrm{TFE}}(m)=2m-1",
        "expected order $2m-1=5$",
        "Full-\\tfe{} stage replacement",
        "Reproducibility package",
        "journal source archive",
        "accepted claim scope and the non-claims",
        "full-\\tfe{} stage replacement is not accepted",
        "accepted theorem is tied to the Gauss/FullVA residual",
        "Source-format check",
        "Archive-completeness check",
        "Package check",
        "Repository-provenance check",
        "Declaration of competing interest",
        "Data availability",
        "Declaration of generative AI and AI-assisted technologies",
        "validate_paper_package.py",
        "validate_pipeline_outputs.py",
    ]
    for token in required_tokens:
        checks.check(contains_normalized(tex, token), f"main_cmame.tex missing token: {token}")

    forbidden_tokens = [
        "full_tfe_stage_replacement=true",
        "complete source-paper residual reproduction is accepted",
        "full-\\tfe{} replacement is accepted",
        "complete source-paper temporal finite-element residual replacement is accepted",
        "better-integrator result",
        "comparative integrator theorem",
    ]
    for token in forbidden_tokens:
        checks.check(token not in tex, f"main_cmame.tex has forbidden claim: {token}")

    checks.check(primary.get("accepted_method") == "Gauss6/FullVA", "boundary accepted method changed")
    checks.check(primary.get("method_order_claim") == 6, "boundary method order changed")
    checks.check(primary.get("smooth_projected_orders", {}).get("position") == 7.161, "boundary position order changed")
    checks.check(primary.get("smooth_projected_orders", {}).get("velocity") == 7.066, "boundary velocity order changed")
    checks.check(comparator.get("expected_order") == 5, "boundary comparator order changed")
    checks.check(boundary.get("full_tfe_stage_replacement") is False, "boundary full-TFE marker changed")
    checks.check(asme.get("full_tfe_required_for_gate") is False, "ASME gate now requires full-TFE")
    checks.check(set(primary.get("accepted_examples", [])) == EXPECTED_EXAMPLES, "boundary examples changed")
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
    checks.check(set(summary.get("asme_gate", {}).get("models", {})) == EXPECTED_EXAMPLES, "summary examples changed")
    checks.check(caveats == EXPECTED_CAVEATS, "open caveat set changed")


def check_external_boundary(checks: Checks, blocker_gate: dict, external_gate: dict) -> None:
    blocker_same_test = blocker_gate.get("same_test_boundary", {})
    external_same_test = external_gate.get("same_test_boundary", {})
    checks.check(
        blocker_same_test.get("same_test_campaign_status") == "not_run",
        "blocker gate lost same-test not-run marker",
    )
    checks.check(
        blocker_same_test.get("external_superiority_claim") is False,
        "blocker gate incorrectly claims external superiority",
    )
    checks.check(
        external_same_test.get("same_test_campaign_status") == "not_run",
        "external baseline gate lost same-test not-run marker",
    )
    checks.check(
        external_same_test.get("external_superiority_claim") is False,
        "external baseline gate incorrectly claims external superiority",
    )


def check_flat_source(checks: Checks, flat_tex: str) -> None:
    checks.check(r"\documentclass[preprint,12pt]{elsarticle}" in flat_tex, "flat source is not elsarticle")
    checks.check("figures/convergence.png" not in flat_tex, "flat source still references figures/convergence.png")
    checks.check(r"\figpath/convergence.png" not in flat_tex, "flat source still references figpath subfolder figures")
    checks.check("main_cmame_submission.tex" not in flat_tex or "main_cmame_submission" in str(FLAT), "flat source parse sanity")
    for figure in FLAT_FIGURES:
        checks.check(figure in flat_tex, f"flat source missing figure reference: {figure}")
    for token in [
        "full-\\tfe{} stage replacement is not accepted",
        "accepted theorem is tied to the Gauss/FullVA residual",
        "Nomenclature",
        "Supplementary source package",
        "Reproducibility package",
        "Order-scope check",
        "Figure_7_strict_common_reference_work_precision.png",
        "Figure_8_claim_boundary_limitations.png",
        "Figure_9_coarse_baseline_work_precision.png",
        "Figure_10_closed_loop_true_dynamic_order.png",
        "Figure_11_method_stage_architecture.png",
        "conditional formal-order comparison",
        "A Conditional Sixth-Order Lie-Group FullVA Integrator for Lower-Pair Mechanisms",
    ]:
        checks.check(contains_normalized(flat_tex, token), f"flat source missing token: {token}")


def check_readiness_audit(checks: Checks, text: str) -> None:
    for token in [
        "CMAME Submission Readiness Audit",
        "Status: **GLOBAL SUBMISSION OPEN; BOUNDED NARROWED SUBCHECK SATISFIED; FULL SOURCE-POLICY PACKAGE NOT READY**",
        "top-level verdict is global and remains",
        "`do_not_submit_global`",
        "bounded subsidiary subcheck",
        "CMAME Guide for Authors",
        "Elsevier LaTeX instructions",
        "University of Wisconsin-Madison contact page",
        "main_cmame.pdf",
        "main_cmame.tex",
        "definitions, nomenclature, method",
        "cmame_submission_flat/main_cmame_submission.tex",
        "Figure_1_convergence.png",
        "CMAME_SUBMISSION_READINESS_REVIEW.md",
        "CMAME_BLOCKER_CLOSURE_GATE.md",
        "CMAME_VISUAL_LEGIBILITY_AUDIT.md",
        "CMAME_RELATED_WORK_AUDIT.md",
        "full_tfe_stage_replacement=false",
        "bounded_narrowed_subcheck_satisfied=true",
        "legacy compatibility alias only, not global readiness:",
        "submission_ready_under_narrowed_claim=true",
        "mechanical_preflight_passed=true",
        "quality_review_passed_under_narrowed_claim=true",
        "full_source_policy_submission_ready=false",
        "open_narrowed_claim_blockers=0",
        "closed_narrowed_claim_blockers=B1,B2,B3,B4,B5,B6,B7,B8",
        "must not invoke",
    ]:
        checks.check(contains_normalized(text, token), f"CMAME readiness audit missing token: {token}")


def check_readiness_review(checks: Checks, text: str) -> None:
    for token in [
        "CMAME Submission-Readiness Review",
        "Status: **GLOBAL SUBMISSION OPEN; BOUNDED NARROWED SUBCHECK SATISFIED**",
        "do not submit globally yet",
        "bounded subsidiary subcheck",
        "academic-paper-reviewer",
        "Reference/style PDF read",
        "Current manuscript PDF read",
        "Historical decision before narrowed-claim closure",
        "Blocking Findings",
        "### B1. Closed",
        "### B8.",
        "bounded_narrowed_subcheck_satisfied=true",
        "Legacy compatibility alias, not a global readiness marker:",
        "submission_ready_under_narrowed_claim=true",
        "mechanical_preflight_passed=true",
        "quality_review_passed_under_narrowed_claim=true",
        "full_source_policy_submission_ready=false",
        "CMAME_VISUAL_LEGIBILITY_AUDIT.md/json",
        "CMAME_RELATED_WORK_AUDIT.md/json",
        "CMAME_PROSE_RESIDUE_AUDIT.md/json",
        "open_narrowed_claim_blockers=0",
        "closed_narrowed_claim_blockers=B1,B2,B3,B4,B5,B6,B7,B8",
    ]:
        checks.check(contains_normalized(text, token), f"CMAME readiness review missing token: {token}")


def check_highlights(checks: Checks, text: str) -> None:
    lines = highlight_lines(text)
    checks.check(3 <= len(lines) <= 5, "highlights must have 3 to 5 bullets")
    for line in lines:
        checks.check(len(line) <= 85, f"highlight exceeds 85 characters: {line}")
    for token in [
        "sixth-order",
        "7.161/7.066",
        "Four ASME-style",
        "m=3 TFE",
        "non-claim",
    ]:
        checks.check(token in text, f"highlights_cmame.txt missing token: {token}")


def check_declarations(checks: Checks, text: str) -> None:
    for token in [
        "Declaration of Competing Interest",
        "affiliated with the University of Wisconsin-Madison",
        "Funding",
        "No external funding",
        "Data Availability",
        "journal source archive",
        "narrowed archive boundary matches the reproducibility manifest: `True`",
        "`narrowed_archive_ready_not_full_source_policy_runner_archive/0/40/False/False/True`",
        "blocking ids/status `OC4,OC6,OC12` / `OC4=open,OC6=partial,OC12=partial`",
        "current archive use is `narrowed_claim_only`, not a full source-policy runner archive",
        "Declaration of Generative AI and AI-Assisted Technologies",
        "AI coding assistant",
        "takes full responsibility",
    ]:
        checks.check(contains_normalized(text, token), f"declarations_cmame.md missing token: {token}")


def check_manifest(
    checks: Checks,
    manifest: dict,
    objective_completion: dict,
    full_source_runner_gap: dict,
    reproducibility_manifest: dict,
    submission_integrity: dict,
) -> None:
    checks.check(manifest.get("recommended_pdf") == "main_cmame.pdf", "manifest recommended PDF is not CMAME PDF")
    checks.check(manifest.get("cmame_tex") == "main_cmame.tex", "manifest CMAME TeX path missing")
    checks.check(manifest.get("cmame_highlights") == "highlights_cmame.txt", "manifest CMAME highlights path missing")
    checks.check(manifest.get("cmame_declarations") == "declarations_cmame.md", "manifest CMAME declarations path missing")
    checks.check(
        manifest.get("cmame_readiness_audit") == "CMAME_SUBMISSION_READINESS_AUDIT.md",
        "manifest CMAME readiness audit path missing",
    )
    checks.check(
        manifest.get("cmame_readiness_review") == "CMAME_SUBMISSION_READINESS_REVIEW.md",
        "manifest CMAME readiness review path missing",
    )
    checks.check(
        manifest.get("cmame_blocker_closure_gate") == "CMAME_BLOCKER_CLOSURE_GATE.md",
        "manifest CMAME blocker-closure gate path missing",
    )
    checks.check(
        manifest.get("cmame_blocker_closure_gate_json") == "CMAME_BLOCKER_CLOSURE_GATE.json",
        "manifest CMAME blocker-closure gate JSON path missing",
    )
    checks.check(
        manifest.get("cmame_external_baseline_gate") == "CMAME_EXTERNAL_BASELINE_GATE.md",
        "manifest CMAME external-baseline gate path missing",
    )
    checks.check(
        manifest.get("cmame_external_baseline_gate_json") == "CMAME_EXTERNAL_BASELINE_GATE.json",
        "manifest CMAME external-baseline gate JSON path missing",
    )
    checks.check(
        manifest.get("cmame_proof_contract_gate") == "CMAME_PROOF_CONTRACT_GATE.md",
        "manifest CMAME proof-contract gate path missing",
    )
    checks.check(
        manifest.get("cmame_proof_contract_gate_json") == "CMAME_PROOF_CONTRACT_GATE.json",
        "manifest CMAME proof-contract gate JSON path missing",
    )
    checks.check(
        manifest.get("cmame_strict_proof_audit") == "CMAME_STRICT_PROOF_AUDIT.md",
        "manifest CMAME strict-proof audit path missing",
    )
    checks.check(
        manifest.get("cmame_strict_proof_audit_json") == "CMAME_STRICT_PROOF_AUDIT.json",
        "manifest CMAME strict-proof audit JSON path missing",
    )
    checks.check(
        manifest.get("cmame_visual_legibility_audit") == "CMAME_VISUAL_LEGIBILITY_AUDIT.md",
        "manifest CMAME visual-legibility audit path missing",
    )
    checks.check(
        manifest.get("cmame_visual_legibility_audit_json") == "CMAME_VISUAL_LEGIBILITY_AUDIT.json",
        "manifest CMAME visual-legibility audit JSON path missing",
    )
    checks.check(
        manifest.get("cmame_related_work_audit") == "CMAME_RELATED_WORK_AUDIT.md",
        "manifest CMAME related-work audit path missing",
    )
    checks.check(
        manifest.get("cmame_related_work_audit_json") == "CMAME_RELATED_WORK_AUDIT.json",
        "manifest CMAME related-work audit JSON path missing",
    )
    checks.check(
        manifest.get("proof_solver_scale_audit") == "PROOF_SOLVER_SCALE_AUDIT.md",
        "manifest proof solver-scale audit path missing",
    )
    checks.check(
        manifest.get("proof_solver_scale_audit_json") == "PROOF_SOLVER_SCALE_AUDIT.json",
        "manifest proof solver-scale audit JSON path missing",
    )
    checks.check(
        manifest.get("cmame_prose_residue_audit") == "CMAME_PROSE_RESIDUE_AUDIT.md",
        "manifest CMAME prose-residue audit path missing",
    )
    checks.check(
        manifest.get("cmame_prose_residue_audit_json") == "CMAME_PROSE_RESIDUE_AUDIT.json",
        "manifest CMAME prose-residue audit JSON path missing",
    )
    checks.check(
        manifest.get("dynamic_row_oracle_gate") == "DYNAMIC_ROW_ORACLE_GATE.md",
        "manifest dynamic row oracle gate path missing",
    )
    checks.check(
        manifest.get("dynamic_row_oracle_gate_json") == "DYNAMIC_ROW_ORACLE_GATE.json",
        "manifest dynamic row oracle gate JSON path missing",
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
    checks.check(manifest.get("cmame_flat_submission_dir") == "cmame_submission_flat", "manifest flat source dir missing")
    checks.check(
        manifest.get("cmame_flat_tex") == "cmame_submission_flat/main_cmame_submission.tex",
        "manifest flat TeX path missing",
    )
    checks.check(
        manifest.get("cmame_flat_pdf") == "cmame_submission_flat/main_cmame_submission.pdf",
        "manifest flat PDF path missing",
    )
    checks.check(manifest.get("cmame_flat_source_archive") == "cmame_submission_flat.zip", "manifest flat archive path missing")
    checks.check(
        manifest.get("external_same_test_run_queue") == "EXTERNAL_SAME_TEST_RUN_QUEUE.md",
        "manifest external same-test run queue path missing",
    )
    checks.check(
        manifest.get("external_same_test_run_queue_json") == "EXTERNAL_SAME_TEST_RUN_QUEUE.json",
        "manifest external same-test run queue JSON path missing",
    )
    checks.check("main_cmame.pdf" in manifest.get("required_submission_files", []), "manifest required files missing CMAME PDF")
    checks.check("main_cmame.tex" in manifest.get("required_submission_files", []), "manifest required files missing CMAME TeX")
    checks.check("highlights_cmame.txt" in manifest.get("required_submission_files", []), "manifest required files missing highlights")
    checks.check("declarations_cmame.md" in manifest.get("required_submission_files", []), "manifest required files missing declarations")
    checks.check(
        "CMAME_SUBMISSION_READINESS_AUDIT.md" in manifest.get("required_submission_files", []),
        "manifest required files missing readiness audit",
    )
    checks.check(
        "CMAME_SUBMISSION_READINESS_REVIEW.md" in manifest.get("required_submission_files", []),
        "manifest required files missing readiness review",
    )
    checks.check(
        "CMAME_BLOCKER_CLOSURE_GATE.md" in manifest.get("required_submission_files", []),
        "manifest required files missing blocker-closure gate",
    )
    checks.check(
        "CMAME_BLOCKER_CLOSURE_GATE.json" in manifest.get("required_submission_files", []),
        "manifest required files missing blocker-closure gate JSON",
    )
    checks.check(
        "CMAME_EXTERNAL_BASELINE_GATE.md" in manifest.get("required_submission_files", []),
        "manifest required files missing external-baseline gate",
    )
    checks.check(
        "CMAME_EXTERNAL_BASELINE_GATE.json" in manifest.get("required_submission_files", []),
        "manifest required files missing external-baseline gate JSON",
    )
    checks.check(
        "CMAME_PROOF_CONTRACT_GATE.md" in manifest.get("required_submission_files", []),
        "manifest required files missing proof-contract gate",
    )
    checks.check(
        "CMAME_PROOF_CONTRACT_GATE.json" in manifest.get("required_submission_files", []),
        "manifest required files missing proof-contract gate JSON",
    )
    checks.check(
        "CMAME_VISUAL_LEGIBILITY_AUDIT.md" in manifest.get("required_submission_files", []),
        "manifest required files missing visual-legibility audit",
    )
    checks.check(
        "CMAME_VISUAL_LEGIBILITY_AUDIT.json" in manifest.get("required_submission_files", []),
        "manifest required files missing visual-legibility audit JSON",
    )
    checks.check(
        "CMAME_RELATED_WORK_AUDIT.md" in manifest.get("required_submission_files", []),
        "manifest required files missing related-work audit",
    )
    checks.check(
        "CMAME_RELATED_WORK_AUDIT.json" in manifest.get("required_submission_files", []),
        "manifest required files missing related-work audit JSON",
    )
    checks.check(
        "CMAME_PROSE_RESIDUE_AUDIT.md" in manifest.get("required_submission_files", []),
        "manifest required files missing prose-residue audit",
    )
    checks.check(
        "CMAME_PROSE_RESIDUE_AUDIT.json" in manifest.get("required_submission_files", []),
        "manifest required files missing prose-residue audit JSON",
    )
    checks.check(
        "DYNAMIC_ROW_ORACLE_GATE.md" in manifest.get("required_submission_files", []),
        "manifest required files missing dynamic row oracle gate",
    )
    checks.check(
        "DYNAMIC_ROW_ORACLE_GATE.json" in manifest.get("required_submission_files", []),
        "manifest required files missing dynamic row oracle gate JSON",
    )
    checks.check(
        "cmame_submission_flat/main_cmame_submission.tex" in manifest.get("required_submission_files", []),
        "manifest required files missing flat TeX",
    )
    checks.check(
        "cmame_submission_flat/main_cmame_submission.pdf" in manifest.get("required_submission_files", []),
        "manifest required files missing flat PDF",
    )
    checks.check(
        "cmame_submission_flat.zip" in manifest.get("required_submission_files", []),
        "manifest required files missing flat source archive",
    )
    for figure in FLAT_FIGURES:
        label = f"cmame_submission_flat/{figure}"
        checks.check(label in manifest.get("required_submission_files", []), f"manifest required files missing flat figure: {figure}")
    for figure in [
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
    ]:
        checks.check(figure in manifest.get("required_submission_files", []), f"manifest required files missing figure: {figure}")
    checks.check("validate_cmame_submission.py" in manifest.get("validators", []), "manifest missing CMAME validator")
    checks.check(
        "validate_cmame_blocker_closure_gate.py" in manifest.get("validators", []),
        "manifest missing blocker-closure validator",
    )
    checks.check(
        "validate_reference_metadata_audit.py" in manifest.get("validators", []),
        "manifest missing reference metadata audit validator",
    )
    checks.check(
        "validate_cmame_external_baseline_gate.py" in manifest.get("validators", []),
        "manifest missing external-baseline validator",
    )
    checks.check(
        "validate_external_same_test_run_queue.py" in manifest.get("validators", []),
        "manifest missing external same-test run queue validator",
    )
    checks.check(
        "validate_cmame_proof_contract_gate.py" in manifest.get("validators", []),
        "manifest missing proof-contract validator",
    )
    checks.check(
        "validate_cmame_strict_proof_audit.py" in manifest.get("validators", []),
        "manifest missing strict-proof audit validator",
    )
    checks.check(
        "validate_cmame_visual_legibility_audit.py" in manifest.get("validators", []),
        "manifest missing visual-legibility audit validator",
    )
    checks.check(
        "validate_cmame_related_work_audit.py" in manifest.get("validators", []),
        "manifest missing related-work audit validator",
    )
    checks.check(
        "validate_cmame_prose_residue_audit.py" in manifest.get("validators", []),
        "manifest missing prose-residue audit validator",
    )
    checks.check(
        "validate_dynamic_row_oracle_gate.py" in manifest.get("validators", []),
        "manifest missing dynamic row oracle validator",
    )
    checks.check(
        "validate_proof_numerical_scale_audit.py" in manifest.get("validators", []),
        "manifest missing proof numerical scale audit validator",
    )
    checks.check(
        "validate_proof_solver_scale_audit.py" in manifest.get("validators", []),
        "manifest missing proof solver scale audit validator",
    )
    checks.check(
        "PROOF_SOLVER_SCALE_AUDIT.md" in manifest.get("evidence_anchors", []),
        "manifest missing proof solver scale audit anchor",
    )
    checks.check(
        "PROOF_SOLVER_SCALE_AUDIT.json" in manifest.get("evidence_anchors", []),
        "manifest missing proof solver scale audit JSON anchor",
    )
    checks.check(
        "CMAME_STRICT_PROOF_AUDIT.md" in manifest.get("evidence_anchors", []),
        "manifest missing strict-proof audit anchor",
    )
    checks.check(
        "CMAME_STRICT_PROOF_AUDIT.json" in manifest.get("evidence_anchors", []),
        "manifest missing strict-proof audit JSON anchor",
    )
    checks.check(
        "EXTERNAL_SAME_TEST_RUN_QUEUE.md" in manifest.get("evidence_anchors", []),
        "manifest missing external same-test run queue anchor",
    )
    checks.check(
        "EXTERNAL_SAME_TEST_RUN_QUEUE.json" in manifest.get("evidence_anchors", []),
        "manifest missing external same-test run queue JSON anchor",
    )
    checks.check(
        "CMAME_PROSE_RESIDUE_AUDIT.md" in manifest.get("evidence_anchors", []),
        "manifest missing prose-residue audit anchor",
    )
    checks.check(
        "CMAME_PROSE_RESIDUE_AUDIT.json" in manifest.get("evidence_anchors", []),
        "manifest missing prose-residue audit JSON anchor",
    )
    checks.check(manifest.get("full_tfe_stage_replacement") is False, "manifest full-TFE marker changed")
    checks.check(
        manifest.get("full_generator_invoked_by_submission_checks") is False,
        "manifest says submission checks invoke full generator",
    )
    objective_summary = objective_completion.get("summary", {})
    archive_action_boundary = full_source_runner_gap.get("action_boundary") or {}
    checks.check(
        manifest.get("full_source_policy_runner_archive_gap_action_boundary")
        == objective_summary.get("full_source_policy_runner_archive_gap_action_boundary")
        == archive_action_boundary,
        "manifest full source-policy archive action boundary changed",
    )
    checks.check(
        manifest.get("full_source_policy_runner_archive_gap_source_policy_execution_invoked")
        == objective_summary.get("full_source_policy_runner_archive_gap_source_policy_execution_invoked")
        == full_source_runner_gap.get("source_policy_execution_invoked")
        is False,
        "manifest full source-policy archive execution-invoked boundary changed",
    )
    checks.check(
        manifest.get("full_source_policy_runner_archive_gap_safe_action_ids")
        == objective_summary.get("full_source_policy_runner_archive_gap_safe_action_ids")
        == full_source_runner_gap.get("safe_action_ids"),
        "manifest full source-policy archive safe action IDs changed",
    )
    checks.check(
        manifest.get("full_source_policy_runner_archive_gap_opt_in_action_ids")
        == objective_summary.get("full_source_policy_runner_archive_gap_opt_in_action_ids")
        == full_source_runner_gap.get("opt_in_action_ids"),
        "manifest full source-policy archive opt-in action IDs changed",
    )
    checks.check(
        archive_action_boundary.get("source_policy_execution_allowed_now") is False
        and archive_action_boundary.get("exact_b4_opt_in_required_for_execution") is True
        and archive_action_boundary.get("safe_without_b4_opt_in_count") == 4
        and archive_action_boundary.get("opt_in_required_action_count") == 1
        and archive_action_boundary.get("opt_in_required_command_count") == 13
        and archive_action_boundary.get("opt_in_required_mapped_external_rows") == 20,
        "manifest full source-policy archive action boundary has unexpected counts",
    )
    narrowed_archive_boundary = manifest.get("narrowed_archive_boundary", {})
    expected_narrowed_archive_boundary = reproducibility_manifest.get("narrowed_archive_boundary", {})
    checks.check(
        narrowed_archive_boundary == expected_narrowed_archive_boundary,
        "manifest narrowed archive boundary does not match reproducibility package manifest",
    )
    checks.check(
        narrowed_archive_boundary.get("status")
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
        "submission artifact manifest does not carry OC6 latest external probe marker",
    )
    checks.check(
        manifest.get("oc6_reopen_latest_external_probe_date") == "2026-06-21"
        and manifest.get("oc6_reopen_latest_external_probe_count") == 9
        and manifest.get("oc6_reopen_latest_external_probe_positive_artifact_rows") == 0
        and manifest.get("oc6_reopen_latest_external_probe_source_policy_rows_closed") == 0
        and manifest.get("oc6_reopen_latest_external_probe_access_limited_count") == 4
        and manifest.get("oc6_reopen_latest_external_probe_global_absence_proved") is False
        and manifest.get("oc6_reopen_latest_external_probe_reopen_triggered") is False,
        "submission artifact manifest OC6 latest external probe fields changed",
    )
    submission_manifest_boundary = submission_integrity.get("submission_manifest_boundary", {})
    checks.check(
        oc6_latest_probe_marker(full_source_runner_gap) == EXPECTED_OC6_REOPEN_LATEST_EXTERNAL_PROBE,
        "full source-policy archive gap OC6 latest external probe marker changed",
    )
    checks.check(
        submission_manifest_boundary.get("oc6_reopen_latest_external_probe")
        == EXPECTED_OC6_REOPEN_LATEST_EXTERNAL_PROBE,
        "submission integrity audit does not carry OC6 latest external probe marker",
    )
    checks.check(
        submission_manifest_boundary.get("oc6_reopen_latest_external_probe_date") == "2026-06-21"
        and submission_manifest_boundary.get("oc6_reopen_latest_external_probe_count") == 9
        and submission_manifest_boundary.get("oc6_reopen_latest_external_probe_positive_artifact_rows") == 0
        and submission_manifest_boundary.get("oc6_reopen_latest_external_probe_source_policy_rows_closed") == 0
        and submission_manifest_boundary.get("oc6_reopen_latest_external_probe_access_limited_count") == 4
        and submission_manifest_boundary.get("oc6_reopen_latest_external_probe_global_absence_proved") is False
        and submission_manifest_boundary.get("oc6_reopen_latest_external_probe_reopen_triggered") is False
        and submission_manifest_boundary.get("oc6_reopen_latest_external_probe_matches_archive_gap") is True,
        "submission integrity audit OC6 latest external probe fields changed",
    )


def main() -> int:
    checks = Checks()
    try:
        tex = read_text(LATEX / "main_cmame.tex")
        highlights = read_text(LATEX / "highlights_cmame.txt")
        declarations = read_text(LATEX / "declarations_cmame.md")
        readiness = read_text(PAPER / "CMAME_SUBMISSION_READINESS_AUDIT.md")
        readiness_review = read_text(PAPER / "CMAME_SUBMISSION_READINESS_REVIEW.md")
        flat_tex = read_text(FLAT / "main_cmame_submission.tex")
        boundary = read_json(PAPER / "CLAIM_BOUNDARY.json")
        summary = read_json(RESULTS / "summary_v047.json")
        manifest = read_json(PAPER / "SUBMISSION_ARTIFACT_MANIFEST.json")
        submission_integrity = read_json(PAPER / "CMAME_SUBMISSION_INTEGRITY_AUDIT.json")
        objective_completion = read_json(PAPER / "OBJECTIVE_COMPLETION_AUDIT.json")
        full_source_runner_gap = read_json(PAPER / "FULL_SOURCE_POLICY_RUNNER_ARCHIVE_GAP_AUDIT.json")
        reproducibility_manifest = read_json(PAPER / "CMAME_REPRODUCIBILITY_PACKAGE_MANIFEST.json")
        blocker_gate = read_json(PAPER / "CMAME_BLOCKER_CLOSURE_GATE.json")
        external_gate = read_json(PAPER / "CMAME_EXTERNAL_BASELINE_GATE.json")
    except Exception as exc:  # noqa: BLE001 - concise CLI failure.
        print(f"v047 CMAME submission validation: FAIL\n- {exc}")
        return 1

    check_files(checks)
    check_tex(checks, tex, boundary, summary)
    check_flat_source(checks, flat_tex)
    check_highlights(checks, highlights)
    check_declarations(checks, declarations)
    check_readiness_audit(checks, readiness)
    check_readiness_review(checks, readiness_review)
    check_manifest(
        checks,
        manifest,
        objective_completion,
        full_source_runner_gap,
        reproducibility_manifest,
        submission_integrity,
    )
    check_external_boundary(checks, blocker_gate, external_gate)
    check_log_clean(checks)

    if checks.errors:
        print("v047 CMAME submission validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("v047 CMAME submission validation: PASS")
    print("journal=Computer Methods in Applied Mechanics and Engineering")
    print("document_class=elsarticle")
    print("recommended_pdf=main_cmame.pdf")
    print("accepted_method=Gauss6/FullVA")
    print("accepted_method_order=6")
    print("source_paper_m3_expected_order=5")
    print("asme_models=double_pendulum,four_link,single_pendulum,slider_crank")
    print("full_tfe_stage_replacement=False")
    print("submission_ready_under_narrowed_claim=True")
    print("full_source_policy_submission_ready=False")
    print("manifest_boundary_matches_archive_gap=True")
    print("manifest_action_boundary=4/1/False/True/13/20")
    print(f"oc6_reopen_latest_external_probe={EXPECTED_OC6_REOPEN_LATEST_EXTERNAL_PROBE}")
    print("mechanical_preflight_passed=True")
    print("quality_review_passed_under_narrowed_claim=True")
    print("run_v047_invoked=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
