#!/usr/bin/env python3
"""Build a proof-claim traceability audit for the CMAME manuscript."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
from paper_paths import LATEX, package_path as manuscript_path
ROOT = PAPER.parent
MAIN_TEX = LATEX / "main_cmame.tex"
FLAT_TEX = LATEX / "cmame_submission_flat" / "main_cmame_submission.tex"
MAIN_PDF_TEXT = LATEX / "main_cmame.txt"
FLAT_PDF_TEXT = LATEX / "cmame_submission_flat" / "main_cmame_submission.txt"
PROOF_CLOSURE = PAPER / "PROOF_CLOSURE_MANIFEST.json"
PROOF_CONTRACT = PAPER / "CMAME_PROOF_CONTRACT_GATE.json"
PROOF_EVIDENCE = PAPER / "PROOF_EVIDENCE_MATRIX.md"
CLAIM_BOUNDARY = PAPER / "CLAIM_BOUNDARY.json"
BLOCKER_GATE = PAPER / "CMAME_BLOCKER_CLOSURE_GATE.json"
NEWTON_EULER_SYMBOLIC_TARGET = PAPER / "NEWTON_EULER_SYMBOLIC_TARGET_AUDIT.json"
NEWTON_EULER_SYMBOLIC_DEFECT_CERTIFICATE = PAPER / "NEWTON_EULER_SYMBOLIC_DEFECT_CERTIFICATE.json"

OUT_JSON = PAPER / "PROOF_CLAIM_TRACEABILITY_AUDIT.json"
OUT_MD = PAPER / "PROOF_CLAIM_TRACEABILITY_AUDIT.md"


EXPECTED_LABELS = [
    r"\label{ass:regularity}",
    r"\label{lem:endpoint-closure}",
    r"\label{lem:fullva-stage-lift}",
    r"\label{tab:newton-euler-obligations}",
    r"\label{tab:newton-euler-row-target-map}",
    r"\label{tab:dynamic-proof-closure-matrix}",
    r"\label{lem:d5-same-object-lift-instantiation}",
    r"\label{lem:stage-residual-defect}",
    r"\label{lem:reference-order-contract}",
    r"\label{lem:p6-p7-nonclosing}",
    r"\label{lem:same-object-composition}",
    r"\label{lem:taylor-route-separation}",
    r"\label{lem:t3-replacement-certificate-use-rule}",
    r"\label{lem:d5-conditional-taylor-finite-sum}",
    r"\label{lem:same-object-taylor-transport-gate}",
    r"\label{lem:full-132-row-residual-bridge}",
    r"\label{cor:route-separation-invariant}",
    r"\label{lem:d5-compact-tube-constants}",
    r"\label{lem:d5-p-state-map-definition}",
    r"\label{lem:d5-p-state-anticircularity}",
    r"\label{lem:d5-p-state-ps2-weighted-target}",
    r"\label{lem:d5-p-state-ps2-aggregate-promotion}",
    r"\label{lem:d5-p-state-ps2-linearization-probe}",
    r"\label{lem:d5-p-state-ps3-conditional-conversion}",
    r"\label{lem:d5-p-state-ps3-full-residual-route}",
    r"\label{lem:d5-p-state-direct-feedback-nonclosure}",
    r"\label{lem:d5-p-acc-map-definition}",
    r"\label{lem:d5-p-acc-row-binding}",
    r"\label{cor:d5-p-acc-row-bound-under-pacc}",
    r"\label{lem:d5-p-acc-independence}",
    r"\label{lem:d5-p-acc-pa2-obstruction}",
    r"\label{lem:d5-p-acc-lower-pair-nonclosure}",
    r"\label{lem:d5-p-lambda-interface}",
    r"\label{lem:d5-p-lambda-pl2-symbolic-structure}",
    r"\label{lem:d5-p-lambda-pl2-axis-plane-margin}",
    r"\label{lem:d5-p-lambda-pl2-compact-reduction}",
    r"\label{lem:d5-p-lambda-d3-noncircularity}",
    r"\label{lem:d5-p-lambda-pl4-rate-propagation}",
    r"\label{lem:d5-p-lambda-conditional-nonclosure}",
    r"\label{cor:d5-smooth-force-row-bound-under-lifts}",
    r"\label{lem:d5-geom-chart-reduction}",
    r"\label{cor:d5-geom-row-bound-under-lifts}",
    r"\label{lem:d5-gyro-bilinear-reduction}",
    r"\label{cor:d5-gyro-row-bound-under-pstate}",
    r"\label{lem:d5-primitive-obligation-implication}",
    r"\label{prop:d5-primitive-taylor-conditional-implication}",
    r"\label{lem:inexact-newton}",
    r"\label{lem:p6-reported-log-nonclosure}",
    r"\label{thm:g6fullva-order}",
    r"\label{eq:residual-certificate-slot}",
    r"\label{tab:theorem-assumption-anchor-ledger}",
    r"\label{tab:p6-solver-policy-obligation-ledger}",
    r"\label{tab:p1p2-compact-tube-obligation-ledger}",
    r"\label{tab:p3p4-implementation-defect-obligation-ledger}",
    r"\label{tab:p5-direct-route-satisfaction-ledger}",
    r"\label{tab:pcp-close-requirement-separation-ledger}",
    r"\label{tab:direct-route-anticircularity-ledger}",
    r"\label{tab:implementation-route-oracle-separation-ledger}",
    r"\label{tab:nonlinear-solver-scale-ledger}",
    r"\label{lem:no-reverse-taylor-inference}",
    r"\label{lem:tfe-target-order}",
    r"\label{prop:order-comparison}",
    r"\label{tab:proof-traceability}",
    r"\label{tab:p7-residual-to-error-obligation-ledger}",
]

MANUSCRIPT_ANCHOR_LABELS = {
    "regularity_assumption": r"\label{ass:regularity}",
    "endpoint_closure_lemma": r"\label{lem:endpoint-closure}",
    "fullva_stage_lift_lemma": r"\label{lem:fullva-stage-lift}",
    "newton_euler_obligation_table": r"\label{tab:newton-euler-obligations}",
    "newton_euler_row_target_map": r"\label{tab:newton-euler-row-target-map}",
    "dynamic_proof_closure_matrix": r"\label{tab:dynamic-proof-closure-matrix}",
    "d5_same_object_lift_instantiation_lemma": r"\label{lem:d5-same-object-lift-instantiation}",
    "stage_residual_defect_lemma": r"\label{lem:stage-residual-defect}",
    "reference_order_contract_lemma": r"\label{lem:reference-order-contract}",
    "p6_p7_nonclosing_lemma": r"\label{lem:p6-p7-nonclosing}",
    "same_object_composition_lemma": r"\label{lem:same-object-composition}",
    "same_object_taylor_transport_gate_lemma": r"\label{lem:same-object-taylor-transport-gate}",
    "full_132_row_residual_bridge_lemma": r"\label{lem:full-132-row-residual-bridge}",
    "inexact_newton_lemma": r"\label{lem:inexact-newton}",
    "p6_reported_log_nonclosure_lemma": r"\label{lem:p6-reported-log-nonclosure}",
    "conditional_order_theorem": r"\label{thm:g6fullva-order}",
    "order_comparison_proposition": r"\label{prop:order-comparison}",
    "proof_traceability_table": r"\label{tab:proof-traceability}",
    "no_reverse_taylor_inference_lemma": r"\label{lem:no-reverse-taylor-inference}",
    "p6_solver_policy_obligation_table": r"\label{tab:p6-solver-policy-obligation-ledger}",
    "p1p2_compact_tube_obligation_table": r"\label{tab:p1p2-compact-tube-obligation-ledger}",
    "p3p4_implementation_defect_obligation_table": r"\label{tab:p3p4-implementation-defect-obligation-ledger}",
    "p5_direct_route_satisfaction_table": r"\label{tab:p5-direct-route-satisfaction-ledger}",
    "p7_residual_to_error_obligation_table": r"\label{tab:p7-residual-to-error-obligation-ledger}",
}

THEOREM_ASSUMPTION_ANCHOR_KEYS = {
    "P1": ["regularity_assumption", "p1p2_compact_tube_obligation_table"],
    "P2": [
        "regularity_assumption",
        "endpoint_closure_lemma",
        "inexact_newton_lemma",
        "conditional_order_theorem",
        "p1p2_compact_tube_obligation_table",
    ],
    "P3": ["dynamic_proof_closure_matrix", "p3p4_implementation_defect_obligation_table"],
    "P4": [
        "fullva_stage_lift_lemma",
        "stage_residual_defect_lemma",
        "full_132_row_residual_bridge_lemma",
        "p3p4_implementation_defect_obligation_table",
    ],
    "P5": [
        "newton_euler_obligation_table",
        "newton_euler_row_target_map",
        "stage_residual_defect_lemma",
        "d5_same_object_lift_instantiation_lemma",
        "full_132_row_residual_bridge_lemma",
        "p5_direct_route_satisfaction_table",
    ],
    "P6": [
        "inexact_newton_lemma",
        "p6_reported_log_nonclosure_lemma",
        "conditional_order_theorem",
        "p6_solver_policy_obligation_table",
    ],
    "P7": ["proof_traceability_table", "p7_residual_to_error_obligation_table"],
}

THEOREM_ANCHOR_LEDGER_REFERENCES = {
    "P1": [r"\ref{tab:p1p2-compact-tube-obligation-ledger}"],
    "P2": [r"\ref{tab:p1p2-compact-tube-obligation-ledger}"],
    "P3": [r"\ref{tab:p3p4-implementation-defect-obligation-ledger}"],
    "P4": [r"\ref{tab:p3p4-implementation-defect-obligation-ledger}"],
    "P5": [r"\ref{tab:p5-direct-route-satisfaction-ledger}"],
    "P6": [r"\ref{tab:p6-solver-policy-obligation-ledger}"],
    "P7": [r"\ref{tab:p7-residual-to-error-obligation-ledger}"],
}

REQUIRED_BOUNDARY_TOKENS = [
    "not as an asymptotic solver-error proof",
    "companion direct-substitution certificate verifies the accepted stage residual",
    "full 132-row stage residual required for the order argument",
    "one-step accepted residual defect statement only",
    "Ideal lift is not implementation discharge",
    "target-equation identity for the smooth lift",
    "code-facing implemented \\(O(h^7)\\) bridge statement",
    "local accepted root",
    "compact-tube inverse condition",
    "Gauss-predictor branch",
    "finite rank probes are not a compact-tube inverse proof",
    "Gauss-predictor inverse and derivative bounds consumed by",
    "not an isolated-root premise in this compact-tube argument",
    "supplies the local accepted stage root",
    "not a global uniqueness claim for remote nonlinear roots",
    "not a certificate of global nonlinear solver convergence",
    "four-term local defect decomposition",
    "uniform in \\(y\\) on the compact proof tube and uniform in the reported accepted step index",
    "reported-grid maximum",
    "explicit local-defect",
    "explicit uniform constant sum",
    "explicit reduced-chart grid constant",
    r"\(C_{\rm loc},C_{\rm red},C_{qv}\)",
    "independent of \\(h\\) and the reported grid length \\(N_h\\)",
    "constants may depend on the compact proof tube",
    "not on \\(h\\), \\(N_h\\), the dense/sparse backend",
    "fixed production tolerances used in finite diagnostic runs",
    "allowed dependencies are exactly the compact-tube regularity",
    r"\|\Psi_h^{\mathrm{G6FVA}}(y)-\varphi_h(y)\|\le C_{\rm loc}h^7",
    r"\max_{0\le n\le N_h}\|y_n-y(t_n)\|\le C_{\rm red}h^6",
    r"\max_{0\le n\le N_h}\|\mathcal R(y_n)-\mathcal R(y(t_n))\|",
    r"C_{\rm red}=C_{\rm loc}\Gamma_s(T)",
    r"C_{qv}=C_{\mathcal R}C_{\rm red}",
    "triangle inequality over Gauss truncation, stage-root perturbation, endpoint closure, and inexact Newton",
    "uniform Gauss truncation constant",
    "compact trajectory tube",
    "explicit stage-residual-to-root estimate",
    "uniform stage-root threshold",
    "same contraction radius applies",
    "not selected separately for each reported step",
    "small-step restriction just used is uniform",
    "not chosen from a solved trajectory",
    "one-step stability scale",
    "nonnegative stability constant",
    r"C_s\ge0",
    "enlarge it to a nonnegative upper bound",
    "same-initial-state reduced-chart reported-grid estimate",
    "same-initial-state reported-grid",
    "reported fixed time grid",
    "any reported fixed time grid",
    "reported run may instantiate the theorem",
    "branch, tube, endpoint, proof-norm",
    "post-hoc filtered solver logs",
    r"\(0\le n\le N_h\), with \(N_hh\le T\)",
    "reported time grid",
    "grid length denoted by \\(N_h\\)",
    "maximum taken over \\(0\\le n\\le N_h\\)",
    "Scope of the theorem conclusion",
    "the displayed local-defect and same-initial-state reported-grid bounds",
    "residual-only mechanism rows",
    "source-policy rows",
    "fixed-tolerance logs, and comparison or",
    "do not promote mechanism-coverage residual rows to trajectory-error/order evidence",
    "The notation is a compact proof-domain partition",
    "P5 is the proved stage-local Newton--Euler identity",
    "compact proof-domain partition",
    "P5 is the proved stage-local Newton--Euler identity",
    "P1/P2/P3, the retained P4 binding side, and P6 describe the branch",
    "residual-only mechanism rows require a separate residual-to-error theorem",
    "The direct bridge supplies the local residual route under the retained",
    "P5 is the proved stage-local Newton--Euler identity",
    "P1/P2/P3, the retained P4 binding side, and P6 describe the branch",
    "AD-expanded implementation-path certificate is closed for that active route",
    "primitive dynamic symbolic oracle and primitive/Taylor symbolic-defect route remain outside",
    "not used by PC2",
    "P4 also contains the proved 96-row non-dynamic certificate",
    "solver-scale interfaces under which the theorem is invoked",
    "solver-scale interfaces under which the theorem is invoked",
    "Assumption admissibility note",
    "does not assume the theorem conclusion",
    "logically prior to, the discrete Gronwall step",
    "not an assumed local defect estimate",
    "The implication direction is fixed throughout",
    "stage-row defect on \\(Z_G\\)",
    "inferred backward",
    "observed sixth-order slopes",
    "successful Newton logs",
    "Forward-only Taylor invariant",
    "pre-global estimate on the fixed",
    "reverse reading from reported errors or finite",
    "Domain-exit is not a lower-order conclusion",
    "covered lower-order transition",
    "post-run row deletion rule",
    "discard failed steps after inspecting a trajectory",
    "direct-route residual decomposition",
    "not a certification of the primitive 162-subterm Taylor route",
    "not additive proof evidence",
    "conditional templates cannot be spliced",
    "primitive-route theorem would have to prove the five open primitive obligations",
    "redo the residual-to-root, endpoint, solver, and global-transfer chain",
    "all 162 subterms have a recorded reduction",
    "primitive-obligation implication for D5",
    "only as a conditional implication under those five still-open primitive",
    "not an accepted primitive-route closure",
    "PC2 input",
    "h\\)-weighted acceleration primitive terms",
    r"\label{tab:p-interface-satisfaction-ledger}",
    "Proof-domain partition",
    "P5 is the only stage-local dynamic identity proved",
    "P1/P2/P3, the retained P4 binding side, and P6 describe the branch",
    "P7 remains a separate output nonclaim/residual-to-error boundary",
    "local residual route under the retained P6",
    "do not turn domain conditions or the P7 boundary",
    "reproducibility package readiness claims",
    r"\label{tab:pcp-close-requirement-separation-ledger}",
    "Route and interface separation table",
    "Route and interface separation",
    "local residual route together with the retained P6 solver-scale condition",
    "PC3 is interpreted only through",
    "PC3 is therefore a retained-condition",
    "not an empirical proof and not an extra certificate",
    "PC4 is recorded only as a retained transfer-scope exclusion",
    "PC4 is not a local-defect ingredient",
    "solver-policy theorem",
    "do not prove a separate residual-to-error transfer theorem",
    r"\label{tab:theorem-dependency-consumption-ledger}",
    "Theorem input-output flow",
    "Theorem input-output flow",
    "displayed inputs record",
    "First consumed by",
    "Later theorem output",
    "P5 supplies",
    "P6 enters only through",
    "retained branch-solver scale",
    "P7 is recorded only in the exclusion column",
    "implemented residual path",
    "transfer-scope exclusion",
    r"\label{tab:accepted-branch-consistency-ledger}",
    "Accepted-branch consistency for",
    "Accepted-branch consistency rule",
    "Proof object",
    "Branch identity used",
    "Consistency source",
    "Explicit exclusion",
    "Gauss predictor",
    "Accepted stage root",
    "Endpoint correction",
    "Inexact Newton iterate",
    "Reported output grid",
    "same compact proof tube",
    "Gauss-predictor ball",
    "retained branch",
    "accepted-branch transitions",
    "remote-chart equivalence",
    "arbitrary Newton-root selection",
    "global nonlinear solver uniqueness",
    "terminal-time error",
    r"\label{tab:implementation-route-oracle-separation-ledger}",
    "Implementation-route/certificate separation table",
    "Implementation-route/certificate separation",
    "Route or certificate",
    "Theorem role",
    "Closed evidence",
    "Active direct residual-bridge route",
    "Runtime formula/AD binding",
    "AD-expanded certificate",
    "Primitive symbolic route",
    "Source-paper residual replacement",
    "implemented 132-row route",
    "stage-residual argument discharged by the direct route",
    "open primitive symbolic route",
    "non-active primitive symbolic-oracle completion record",
    "inputs to the theorem",
    "not contradictions of the direct D5 substitution closure",
    "not source-paper residual replacement",
    "not source-policy/full-\\tfe{} readiness",
    "not reproducibility package readiness evidence",
    r"\label{tab:nonlinear-solver-scale-ledger}",
    "Nonlinear-solver scale conditions",
    "Nonlinear-solver scale rule",
    "Solver-scale object",
    "Theorem role",
    "evidence boundary",
    "Compact-tube policy",
    "Reported-grid specialization",
    "Finite solver diagnostics",
    "Local-defect absorption",
    "Retained solver-policy condition",
    "retained P6 theorem condition",
    "reported-grid maximum",
    "finite scaled-tolerance probes",
    "Diagnose branch-scale",
    "trajectory specializations",
    "one-step estimate is local",
    "reported-trajectory specialization",
    "not an additional local hypothesis",
    "load-bearing solver object",
    "compact-tube envelope",
    "hidden \\(h\\)-dependent row weights",
    "\\(h\\)-independent compact-tube norm equivalence",
    "finite-dimensional norm-equivalence constant after the explicit residual",
    "small residual in a different norm, branch, row scaling, or terminal solve is not an input",
    "not a fitted residual sequence",
    "Accepted-branch consistency rule",
    "tube-envelope hypothesis",
    "independent solver-policy proof",
    "theorem-level solver-policy theorem",
    "fixed-tolerance asymptotic proof",
    "global Newton convergence",
    "arbitrary Newton-root selection",
    "reproducibility package readiness evidence",
    r"\label{tab:reporting-map-norm-equivalence-ledger}",
    "Reporting-map/norm-equivalence table",
    "Reporting-map/norm-equivalence rule",
    "Reporting step",
    "Input estimate",
    "Uniform map property",
    "Explicit non-use",
    "Reduced-chart grid",
    "Reporting map definition",
    "Derivative bound",
    "Reported grid scope",
    "reporting-map consequence",
    "reaction diagnostic",
    "global chart equivalence",
    "remote branch statement",
    "fitted-constant claim",
    r"\label{tab:local-defect-decomposition-ledger}",
    "Local-defect decomposition for",
    "Local-defect decomposition rule",
    "Triangle term",
    "Bound used",
    "Gauss truncation",
    "Stage-root perturbation",
    "Endpoint closure",
    "Inexact Newton termination",
    "Local-defect sum",
    "four displayed accepted-branch terms",
    "primitive dynamic symbolic oracle closure",
    "global Newton convergence",
    r"\label{tab:theorem-output-scope-ledger}",
    "Theorem output scope",
    "Theorem output scope rule",
    "Output layer",
    "Proven statement",
    "Explicit non-output",
    "One-step accepted map",
    "Reported position",
    "Method-order sentence",
    "the theorem outputs are exactly",
    "fixed-tolerance asymptotic proof",
    "P7 remains a separate output nonclaim/residual-to-error boundary",
    "residual-only mechanism rows require a separate",
    "P7 remains a separate output nonclaim/residual-to-error boundary",
    "not a theorem premise",
    r"\label{tab:theorem-assumption-anchor-ledger}",
    "Theorem-interface and output-boundary anchors",
    "Assumption-anchor map",
    "Interface & Manuscript anchor",
    "Consumption rule",
    "proof records where the compact-tube interfaces",
    "the direct Newton--Euler identity",
    "and the residual-to-error boundary enter the manuscript",
    r"Table~\ref{tab:p1p2-compact-tube-obligation-ledger}",
    r"Table~\ref{tab:p3p4-implementation-defect-obligation-ledger}",
    r"Table~\ref{tab:p5-direct-route-satisfaction-ledger}",
    r"Table~\ref{tab:p6-solver-policy-obligation-ledger}",
    "direct Newton--Euler identity",
    "row-local non-dynamic certificate",
    "the residual-to-error boundary",
    "Anchor presence is not a proof discharge",
    "Anchor presence is not a proof discharge",
    "does not prove compact-tube regularity",
    "primitive symbolic-oracle work",
    "PC1--PC2 route checks plus retained P6 and PC4 boundary",
    "PC1--PC2 close the local residual route under the stated theorem",
    "PC4 records residual-to-error exclusion only",
    "P5 is the only stage-local dynamic identity proved by direct substitution",
    "Route-to-local-defect sufficiency",
    "supplies exactly the local-defect input used by",
    "PC4 is a negative route rule",
    "sufficiency implication, this statement is not an equivalence",
    "does not choose constants from finite slopes, Newton logs",
    "source-policy rows, or reproducibility package records",
    "The main theorem proves a conditional",
    "A Conditional Sixth-Order Lie-Group FullVA Integrator for Lower-Pair Mechanisms",
    "retained interfaces are compact-tube regularity",
    "branch-selected solver scale",
    "residual-to-error promotion, full external same-test reproduction, and complete source-paper \\tfe{} residual replacement are not claimed",
    "exact final-time divisibility is not required",
    "same reported time grid",
    "local one-step hypotheses are used only for transitions",
    "terminal index \\(N\\) is an output index, not an extra solve",
    "terminal index \\(N_h\\) is only the last output value",
    "indexed by the transition steps \\(0\\le n<N_h\\)",
    "leftover interval \\(T-Nh\\) is outside this reported-grid estimate",
    "unreported leftover interval \\(T-N_hh\\) is outside the stated grid maximum",
    "no terminal-time error at \\(T\\) is inferred",
    "dynamic residual identity",
    "residual consistency",
    "closed-loop DAE stability or inf-sup control",
    "calibrated estimator",
    "coarse-first campaign",
    "residual magnitudes remain diagnostics and cannot replace the accepted smooth-branch order proof",
    r"\label{tab:p7-residual-to-error-obligation-ledger}",
    "Residual-to-error boundary",
    "all seven P7 dependency obligations remain open",
    "Residual tables and residual-to-error ratios are diagnostics only",
    "mechanism-coverage residual row",
    "closed-loop reaction table",
    "common-reference row",
    "source-policy row is promoted",
    "trajectory-error/order evidence",
    "P7 residual-to-error operator boundary",
    "P7 fixed-operator requirement",
    "same reported closed-loop branch",
    "mechanism residual operator",
    "trajectory norm",
    "uniform stability or inf-sup inverse",
    "fixed linearized inverse",
    "fixed before observed residual data",
    "not obtained by dividing",
    "measured trajectory errors",
    "same branch residual operator with a uniform inverse",
    "same-branch residual transfer operator",
    "\\(h\\)-independent constant \\(C_{\\rm P7}\\)",
    "small reaction or constraint residuals",
    "manuscript transfer theorem close together",
    r"\label{tab:theorem-use-rule}",
    "Auxiliary-evidence scope",
    "theorem inputs are restricted to",
    "Finite solver probes, residual/reaction tables, source-policy rows, and local reproducibility record evidence",
    "diagnostic or reproducibility-boundary evidence only",
    "not promoted to theorem-input status",
    "source-policy/full-\\tfe{} readiness",
    r"\label{tab:quantifier-domain-ledger}",
    "Quantifier/domain table",
    "Quantifier/domain rule",
    "the theorem quantifiers are",
    "Fixed proof data",
    "all retained-tube states",
    "any reported grid",
    "table records",
    "accepted compact proof tube",
    "accepted branch-selected",
    "arbitrary Newton roots",
    "unreported leftover interval",
    "terminal-time correction",
    "P6 is the retained theorem-level solver-policy condition",
    "P7 output nonclaim/residual-to-error boundary",
    r"\label{tab:local-global-transfer-ledger}",
    "Local-to-global transfer table",
    "Local-to-global transfer rule",
    "uniform branch-selected local defect",
    "stability scale",
    "tube-retention margin",
    "Accumulation-factor boundary",
    "accumulating at most \\(O(1/h)\\) reported transition defects",
    "uses \\(N_hh\\le T\\) before the constant is chosen",
    "independent of the reported step count \\(N_h\\)",
    "not fitted from the number of reported steps",
    "discrete Gronwall on reported transition steps",
    "accepted recurrence",
    "same initial reduced-chart state",
    "resampled or postprocessed sequence",
    "same-initial-state reported-grid estimate",
    "reported output indices",
    "reporting-map consequence",
    "residual/reaction tables",
    "sweep fits",
    "fixed production tolerances",
    "source-policy rows",
    "unreported leftover interval",
    "extra terminal solve",
    "P6 is the retained theorem-level solver-policy condition",
    "P7 output nonclaim/residual-to-error boundary",
    r"\label{tab:objective-completion-blockers}",
    "External reproduction and package boundaries retained by the paper package",
    "External reproduction/package boundary",
    "the three rows in",
    "are scope boundaries",
    "do not change the conditional theorem proof",
    "source-policy reproduction",
    "runner evidence",
    "That archive is outside the current paper package",
    r"\label{tab:constant-dependency-ledger}",
    "Constant-dependency table",
    "Constant-dependency rule",
    "the theorem constants are compact-tube constants only",
    "not fitted from the finite h-sweep",
    "source-policy comparison",
    "source-policy comparison",
    "residual/reaction table",
    "local reproducibility record",
    "P6 is the retained theorem-level solver-policy condition",
    "P7 output nonclaim/residual-to-error boundary",
    "ordinary compact-tube Lipschitz continuity alone is not enough",
    "tube-retention bootstrap",
    "not an invariant-region proof",
    "compact chart norm-equivalence",
    "chart-to-\\((q,v)\\) reporting map",
    "not claim a global equivalence across remote charts",
    "closed endpoint anchor",
    "Endpoint closure perturbation",
    "endpoint-ball margin",
    "endpoint-closure local right inverse",
    "local right-inverse perturbation",
    "unprojected endpoint closure defect has the explicit local",
    "endpoint-anchor family, uniform ball radius, right inverse",
    "projection diagnostic",
    "per-step projection log",
    "endpoint norm are used",
    r"\|\Delta z_E\|\le C_E h^7",
    r"C_E=4M_{E,\mathrm{ri}}C_{E,\mathrm{raw}}",
    "Endpoint-refinement boundary",
    "local closure solve inside the same endpoint ball",
    "not an extra terminal solve",
    "not a global projection proof",
    "not a fitted KKT correction norm",
    "endpoint-norm fixed",
    "dependent projection constant",
    "not a substitute for the stage-row defect certificate",
    "D5 certificate is a stage-local identity on \\(Z_G\\)",
    "not evidence about residuals evaluated at the inexact Newton iterate",
    "finite-run diagnostic trajectories, or closed-loop",
    "mechanism residual tables",
    "still-open residual-to-error boundary",
    "Pointwise right-invertibility",
    "strong local residual inverse",
    "strong local residual inverse used by Lemma",
    "local branch contract",
    "per-step branch-selected residual bound",
    r"\eta_h^{\rm tube}\le c_\eta h^7",
    "branch-selected solver hypothesis",
    "compact-tube branch-solver hypothesis",
    "compact-tube scaled branch-solver hypothesis",
    "scaled branch-solver hypothesis",
    "trajectory specialization",
    "solver-scale clause is a retained hypothesis",
    "selected Gauss-predictor branch",
    "trajectory specialization of the retained compact-tube envelope",
    "compact-tube \\(\\eta_h^{\\rm tube}\\) bound",
    "lemma-level residual budget",
        "compact-tube upper envelope",
        "not a replacement for the uniform compact-tube solver hypothesis",
        "residual norm, accepted branch",
        "Newton log",
        "tolerance sweep",
        "reported residual ratio",
        "post-hoc residual filtering",
        "cannot create an accepted transition",
        "Reported residual ratios",
        "cannot calibrate",
        "turn failed branch-scale rows into theorem inputs",
        "reported branch-selected Newton steps",
    "Gauss predictor on the same accepted branch",
    "arbitrary Newton initializations",
    "same reduced-chart initial state",
    "maximum over the accepted branch-selected Newton solves",
    r"\eta_h^{\rm reported}=\max_{0\le n<N_h}\eta_{h,n}",
    "accepted branch-selected \\method{} one-step map",
    "branch-selected accepted map",
    "accepted branch-selected map is order six",
    "not a statement about arbitrary nonlinear roots",
    r"C_Nc_\eta h^7",
    "averaged Jacobian",
    "pointwise Jacobian invertibility alone",
    "residual-to-error transfer theorem remain separate non-active/open proof routes",
    "AD-expanded certificate is not the primitive symbolic defect certificate",
    "primitive dynamic symbolic oracle remains open outside the active direct route",
    "not a primitive symbolic defect certificate and not a source-paper residual replacement",
    "AD-expanded implementation-path boundary",
    "closed certificate supplies",
    "AD-expanded implementation-path/derivative-cell closure",
    "active direct residual route only",
    "it does not close the primitive dynamic symbolic oracle",
    "source-paper residual replacement, or source-policy package readiness",
    "symbolic defect certificate remains a provenance record, not the route that",
    "proof dependencies used by the theorem",
    "finite solver probes attach only to P6",
    "P6 solver boundary",
    "branch-scale consistency only",
    "P6 remains the explicit theorem condition",
    "do not prove a theorem-level solver-policy theorem",
    "not turn fixed tolerances into an asymptotic proof",
    "do not assert global Newton convergence or remote-root selection",
    "compact-tube boundary",
    "P1 and P2 remain retained",
    "diagnose the selected branch only",
    "do not prove or remove smooth-lift regularity",
    "uniform compact-tube invertibility",
    "right-inverse hypotheses",
    "tube-retention stability",
    "P3/P4 implementation-defect boundary",
    "P3 and P4 remain retained",
    "implemented direct-route residual",
    "consumed by the same-branch direct residual bridge",
    "AD-expanded implementation-path certificate is closed",
    "primitive dynamic symbolic oracle",
    "primitive/Taylor symbolic-defect route",
    "source-paper residual reproduction",
    "lower-pair rows; it does not by itself prove the full 132-row",
    "does not by itself prove the full 132-row stage residual",
    "separate 36-row D5 direct-substitution certificate",
    "P5 direct-route boundary",
    "P5 direct-route boundary: P5",
    "residual identity on the smooth Gauss lift",
    "supplies the 36 dynamic rows required by PC2",
    "does not assert residual control",
    "inexact Newton iterate",
    "finite-run trajectories",
    "closed-loop mechanism residual tables",
    "source-policy rows",
    "residual-to-error promotion",
    r"\label{tab:proof-causality-ledger}",
    "Proof causality",
    "Proof-causality rule",
    "each mathematical input is consumed",
    "D5 direct-substitution certificate is evaluated on the lifted Gauss stage",
    "before the local perturbation argument",
    "local defect bound is established before the discrete Gronwall transfer",
    "position--velocity reporting map is used only after the reduced-chart grid estimate",
    "do not feed PC2",
    "residual tables are recorded only as diagnostics for the open P7 residual-to-error boundary",
    "primitive symbolic route is a separate primitive-route record",
    "is not an input to the PC2 stage-residual condition",
    r"\label{tab:direct-route-anticircularity-ledger}",
    "Direct-route anti-circularity table",
    "Direct-route anti-circularity rule",
    "Proof object",
    "Fixed before",
    "May depend on",
    "Explicit non-dependence",
    "Lifted Gauss stage",
    "Implemented residual rows",
    "D5 direct-substitution certificate",
    "Local perturbation/local defect",
    "Theorem conclusion",
    "the direct route is admissible",
    "D5 direct-substitution identities",
    "fixed before",
    "The theorem conclusion does not justify row identities",
    "not sources for D5",
    "does not prove P1/P2/P6/P7",
    "primitive/Taylor route",
    "reproducibility package readiness evidence",
    "implication would have to prove a bound",
    "uniform stability or inf-sup constant on the reported branch",
    "small residual norms alone are not a trajectory-error theorem",
    "residual rows remain diagnostics even when their measured norms are small",
    "The residual inequality and the branch-membership hypothesis are separate",
    "stage error without the averaged-Jacobian inverse",
    "The averaged-Jacobian inverse is the transfer operator",
    "active D5 direct-substitution certificate closes the dynamic defect",
    "target map indexes the direct D5 certificate",
    "The direct stage-residual input is supplied by zero row-local dynamic",
    "all 36 dynamic rows have zero residual",
    "It closes only the direct-route PS3 corollary",
    "The proposition does not compare error constants",
    "not a complete source-paper temporal finite-element residual replacement",
    "no residual-to-trajectory-error transfer theorem is accepted in this manuscript",
    "Residual-to-error transfer boundary",
    "This exclusion is not a residual-transfer theorem",
    "not accepted dynamic order rows",
    "joint criterion remains open",
    "Scope of theorem",
    "mathematical claim of",
    "conditional order-six theorem under",
    "P5",
    "direct Newton",
    "Euler route supply",
    "unconditional theorem without theorem-domain interfaces",
    "closure of",
    "fixed-tolerance asymptotic proof",
    "accepted residual-to-error transfer theorem for mechanism rows",
    "source-policy/full-TFE package readiness",
]

READER_FACING_BOUNDARY_TOKENS = [
    "Scope of theorem",
    "conditional order-six theorem",
    "P5",
    "direct Newton",
    "Newton",
    "Euler route",
    "unconditional theorem without theorem-domain",
    "solver-policy condition",
    "fixed-tolerance asymptotic proof",
    "accepted residual-to-error transfer theorem for mechanism rows",
    "source-policy/full",
    "TFE package readiness",
]

THEOREM_CONCLUSION_SCOPE_GUARD_TOKENS = [
    "theorem conclusion",
        "the displayed local-defect and same-initial-state reported-grid bounds",
    "reduced-chart branch-selected map",
    "residual-only mechanism rows",
    "source-policy rows",
    "fixed-tolerance logs, and comparison or",
    "do not promote mechanism-coverage residual rows to trajectory-error/order evidence",
]

PROOF_STRENGTH_CERTIFICATE_TOKENS = [
    "Proof structure",
    "load-bearing proof is the four-term uniform local-defect sum",
    "Same-object direct-substitution calculation",
    "fixed block vector",
    "P4 certificate gives",
    "P5 direct substitution identity gives",
    "exact theorem-level residual value inserted into the Taylor/Kantorovich perturbation",
    "stage-root equation",
    "endpoint reconstruction Lipschitz bound",
    "are one same-object",
    "No constant in this calculation is imported from",
    "stated local-to-global transfer",
    "reporting-map consequence",
    "proof-interface tables specify",
    "domain and nonuse boundaries",
    "do not replace the local-defect estimate",
    "choose constants",
    "from finite",
    "promote residual tables into trajectory-error",
    "Single-instance requirement",
    "same fixed residual map and norm",
    "Direct residual-bridge scope convention",
    "residual-bridge/Kantorovich input",
]

FULL_RESIDUAL_BRIDGE_TOKENS = [
    "Full 132-row residual-defect certificate bridge",
    "accepted row ordering, finite row-scaling map, and fixed finite-dimensional proof norm",
    "dependent row weights",
    "factors written in the residual formulas",
    "finite-dimensional norm-equivalence constant",
    "row scaling is not reweighted",
    "between residual rows and constants",
    "96-row non-dynamic certificate gives",
    "D5 direct-substitution certificate gives",
    "full implemented residual satisfies",
    "residual hypothesis of Lemma",
    "direct-route formula residual",
    "bridge discharges only this",
    "uniform stage inverse",
    "theorem interfaces consumed by the surrounding perturbation argument",
    "finite block-norm consequence",
    "not an empirical residual fit",
    "Direct-route sufficiency boundary",
    "not a primitive symbolic expansion",
    "missing primitive dynamic symbolic oracle is not a missing input",
    "remains a separate primitive-route record",
    "pre-perturbation statement on",
    "bridge is not",
    "a compact-tube inverse proof",
    "does not choose the Newton branch",
    "solver-scale hypotheses",
    "residual-defect handoff",
]

INTRO_PROOF_HIERARCHY_TOKENS = [
    "one-way conditional implication",
    "backfilled interpretation of numerical evidence",
    "compact-tube hypotheses choose the branch and constants before",
    "stage-row defect on",
    "endpoint closure and inexact Newton add controlled",
    "local-to-global transfer then gives",
    "grid estimate",
    "Finite step sweeps may identify the reported branch",
    "do not discharge the theorem-level solver hypothesis",
    "do not promote residual-only mechanism or external comparison rows",
    "retained interfaces delimit where the theorem may be invoked",
]

EXPECTED_PROOF_OBJECT_COUNTS = {
    "assumption": 1,
    "lemma": 50,
    "theorem": 1,
    "proposition": 2,
    "corollary": 7,
}

THEOREM_SCOPE_PRIMITIVE_BOUNDARY_TOKENS = [
    r"Tables~\ref{tab:d5-primitive-blocker-ledger}",
    r"and~\ref{tab:d5-open-primitive-proof-interfaces}",
    "accompanying conditional primitive/Taylor implication",
    "It is not theorem evidence unless the named primitives are independently proved on the same compact branch",
]

TAYLOR_FINITE_IMPLICATION_TOKENS = [
    r"\label{lem:d5-conditional-taylor-finite-sum}",
    r"\label{prop:d5-primitive-taylor-conditional-implication}",
    r"\label{lem:d5-primitive-obligation-implication}",
    "Conditional finite-sum Taylor implication for the D5 route",
    "This separate primitive-route lemma is a conditional finite implication",
    "Assume the five remaining primitive obligations",
    "every D5 Taylor subterm in the 36 Newton--Euler rows",
    "not an accepted primitive-route closure, not a PC2 input",
    "non-active replacement-certificate route rather than current theorem evidence",
]

ROUTE_EXCLUSIVITY_TEX_TOKENS = [
    "Route-exclusivity refinement",
    "one same-branch proof tuple",
    r"\(C_R^{\mathrm{T3}}h^7\)",
    r"cannot be combined with the accepted direct \(C_Rh^7\) term to",
    "lower constants, remove the retained P6 solver-scale condition, use P7",
    "consumes one residual-value certificate",
    "never mixes partial",
    "certificates from the direct and primitive routes",
]

ROUTE_EXCLUSIVITY_PDF_TEXT_TOKENS = [
    "Route-exclusivity refinement",
    "one same-branch proof tuple",
    "CRT3 h7",
    "accepted direct CR h7",
    "lower constants, remove the retained P6 solver-scale condition, use P7",
    "consumes one residual-value certificate",
    "never mixes partial",
    "certificates from the direct and primitive routes",
]

THEOREM_RESIDUAL_CERTIFICATE_EXCLUSIVITY_TEX_TOKENS = [
    r"\label{eq:residual-certificate-slot}",
    "Residual-certificate slot",
    r"\mathsf R_{\rm active}(h,y)\equiv \mathsf R_{\rm dir}(h,y)",
    r"\mathsf R_{\rm dir}(h,y)\Longrightarrow",
    r"\|F_{A,h}(Z_G;y)\|\le C_Rh^7",
    r"\(\mathsf R_{\rm prim}\) is not an additional premise",
    "all five primitive lift/reduction inputs and all \\(162\\) primitive",
    "may replace \\(\\mathsf R_{\\rm active}\\) only after proving",
    "it may not combine",
    "with the accepted direct certificate to lower constants, discharge P6",
    r"\(\mathsf R_{\rm dir}\) is instantiated, not",
    "supplemented, by the two discharged residual inputs",
    "P4's 96-row non-dynamic certificate",
    "P5's direct Newton--Euler substitution identity",
    "Only one residual-value certificate is consumed in this theorem invocation",
    r"new same-tuple \(132\)-row residual-value bound",
    "it cannot be appended to the direct certificate to lower constants, remove",
]

THEOREM_RESIDUAL_CERTIFICATE_EXCLUSIVITY_PDF_TEXT_TOKENS = [
    "Residual-certificate slot",
    "Ractive",
    "Rdir",
    "Rprim",
    "is not an additional premise",
    "all five primitive lift/reduction inputs and all 162 primitive",
    "primitive/Taylor certificate may replace Ractive only after",
    "proving a new same-tuple 132-row residual-value bound",
    "it may not combine",
    "with the accepted direct certificate to lower constants, discharge P6",
    "is instantiated, not supplemented",
    "by the two discharged residual inputs",
    "96-row non-dynamic certificate",
    "direct Newton",
    "substitution identity",
    "Only one residual-value certificate is consumed in this theorem invocation",
    "new same-tuple 132-row residual-value bound",
    "it cannot be appended to the direct certificate to lower constants",
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def count_environment(tex: str, name: str) -> int:
    return len(re.findall(rf"\\begin\{{{re.escape(name)}\}}", tex))


def _token_variants(value: str) -> set[str]:
    collapsed = " ".join(value.split())
    dehyphenated = re.sub(r"-\s+", "", collapsed)
    preserved_hyphen = re.sub(r"-\s+", "-", collapsed)
    hyphenless = collapsed.replace("-", "")
    return {collapsed, dehyphenated, preserved_hyphen, hyphenless}


def contains_normalized(text: str, token: str) -> bool:
    if token in text:
        return True
    text_variants = _token_variants(text)
    token_variants = _token_variants(token)
    return any(token_variant in text_variant for token_variant in token_variants for text_variant in text_variants)


def find_line_number(text: str, token: str) -> int | None:
    for index, line in enumerate(text.splitlines(), start=1):
        if token in line:
            return index
    return None


def manuscript_anchor_map(main_tex: str, flat_tex: str) -> dict[str, Any]:
    label_anchors: dict[str, dict[str, Any]] = {}
    for key, label_token in MANUSCRIPT_ANCHOR_LABELS.items():
        main_line = find_line_number(main_tex, label_token)
        flat_line = find_line_number(flat_tex, label_token)
        label_anchors[key] = {
            "label_token": label_token,
            "main_line": main_line,
            "flat_line": flat_line,
            "present_main": main_line is not None,
            "present_flat": flat_line is not None,
            "present_main_and_flat": main_line is not None and flat_line is not None,
        }

    theorem_assumption_anchors: dict[str, dict[str, Any]] = {}
    for assumption_id, label_keys in THEOREM_ASSUMPTION_ANCHOR_KEYS.items():
        theorem_assumption_anchors[assumption_id] = {
            "label_keys": label_keys,
            "main_lines": {key: label_anchors[key]["main_line"] for key in label_keys},
            "flat_lines": {key: label_anchors[key]["flat_line"] for key in label_keys},
            "all_present_main_and_flat": all(
                label_anchors[key]["present_main_and_flat"] for key in label_keys
            ),
        }

    return {
        "label_anchor_count": len(label_anchors),
        "all_label_anchors_present": all(
            item["present_main_and_flat"] for item in label_anchors.values()
        ),
        "labels": label_anchors,
        "theorem_assumption_anchor_count": len(theorem_assumption_anchors),
        "theorem_assumption_anchor_ids": sorted(theorem_assumption_anchors),
        "theorem_assumption_anchor_map": theorem_assumption_anchors,
        "all_theorem_assumption_anchors_present": all(
            item["all_present_main_and_flat"] for item in theorem_assumption_anchors.values()
        ),
    }


def extract_labeled_table_block(tex: str, label_token: str) -> str:
    label_index = tex.find(label_token)
    if label_index < 0:
        return ""
    begin_index = tex.rfind(r"\begin{table", 0, label_index)
    end_index = tex.find(r"\end{table}", label_index)
    if begin_index < 0 or end_index < 0:
        return ""
    return tex[begin_index : end_index + len(r"\end{table}")]


def extract_table_row(table_block: str, row_key: str) -> str:
    match = re.search(rf"(?:^|\n){re.escape(row_key)}\s*&.*?\\\\", table_block, re.S)
    return match.group(0) if match else ""


def theorem_anchor_table_reference_coverage(main_tex: str, flat_tex: str) -> dict[str, Any]:
    label_token = r"\label{tab:theorem-assumption-anchor-ledger}"

    def source_coverage(tex: str) -> dict[str, Any]:
        table_block = extract_labeled_table_block(tex, label_token)
        rows = {}
        for assumption_id, references in THEOREM_ANCHOR_LEDGER_REFERENCES.items():
            row_text = extract_table_row(table_block, assumption_id)
            reference_checks = {
                reference: contains_normalized(row_text, reference) for reference in references
            }
            rows[assumption_id] = {
                "row_present": bool(row_text),
                "references": reference_checks,
                "all_references_present": bool(row_text) and all(reference_checks.values()),
            }
        return {
            "table_present": bool(table_block),
            "rows": rows,
            "all_references_present": bool(table_block)
            and all(row["all_references_present"] for row in rows.values()),
        }

    sources = {
        "main_tex": source_coverage(main_tex),
        "flat_tex": source_coverage(flat_tex),
    }
    return {
        "label_token": label_token,
        "required_references": THEOREM_ANCHOR_LEDGER_REFERENCES,
        "sources": sources,
        "all_references_present_main_and_flat": all(
            source["all_references_present"] for source in sources.values()
        ),
    }


def blocker_statuses(gate: dict[str, Any], blocker_ids: list[str]) -> dict[str, str | None]:
    rows = {item.get("id"): item for item in gate.get("blockers", [])}
    return {blocker_id: rows.get(blocker_id, {}).get("status") for blocker_id in blocker_ids}


def source_checks(tex: str) -> dict[str, Any]:
    labels = {label: label in tex for label in EXPECTED_LABELS}
    boundary_tokens = {token: contains_normalized(tex, token) for token in REQUIRED_BOUNDARY_TOKENS}
    proof_object_counts = {
        name: count_environment(tex, name) for name in EXPECTED_PROOF_OBJECT_COUNTS
    }
    newton_euler_ids = {f"D{i}": f"D{i} &" in tex for i in range(1, 7)}
    dynamic_matrix_tokens = [
        "Dynamic-row residual-identity table",
        "Verified input",
        "Proof role and remaining non-use",
        "D5 direct-substitution residual certificate",
        "The direct stage-residual input is supplied by zero row-local dynamic",
        "D6 certificate independently proves the dynamic row ordering",
    ]
    dynamic_matrix = {
        token: contains_normalized(tex, token) for token in dynamic_matrix_tokens
    }
    row_target_tokens = [
        "Row-level target map for the Newton--Euler weak-balance rows",
        r"\label{tab:newton-euler-row-target-map}",
        "Rows 24--26 and 30--32",
        "Rows 27--29 and 33--35",
        "Rows 68--70 and 74--76",
        "Rows 71--73 and 77--79",
        "Rows 112--114 and 118--120",
        "Rows 115--117 and 121--123",
        "i_{\\mathrm{row}}(s,\\rho)=44s+24+\\rho",
        "D1/D2 balance identities give zero dynamic residual on \\(Z_G\\)",
    ]
    row_target_map = {
        token: contains_normalized(tex, token) for token in row_target_tokens
    }
    theorem_scope_primitive_boundary = {
        token: contains_normalized(tex, token) for token in THEOREM_SCOPE_PRIMITIVE_BOUNDARY_TOKENS
    }
    taylor_finite_implication = {
        token: contains_normalized(tex, token) for token in TAYLOR_FINITE_IMPLICATION_TOKENS
    }
    return {
        "labels": labels,
        "all_labels_present": all(labels.values()),
        "boundary_tokens": boundary_tokens,
        "all_boundary_tokens_present": all(boundary_tokens.values()),
        "proof_object_counts": proof_object_counts,
        "proof_object_counts_match_expected": proof_object_counts == EXPECTED_PROOF_OBJECT_COUNTS,
        "newton_euler_ids": newton_euler_ids,
        "all_newton_euler_ids_present": all(newton_euler_ids.values()),
        "dynamic_proof_closure_matrix": dynamic_matrix,
        "dynamic_proof_closure_matrix_present": all(dynamic_matrix.values()),
        "newton_euler_row_target_map": row_target_map,
        "newton_euler_row_target_map_present": all(row_target_map.values()),
        "theorem_scope_primitive_boundary": theorem_scope_primitive_boundary,
        "taylor_finite_implication": taylor_finite_implication,
        "theorem_scope_references_d5_primitive_blocker_ledger": contains_normalized(
            tex, r"Tables~\ref{tab:d5-primitive-blocker-ledger}"
        ),
        "theorem_scope_preserves_primitive_pc2_closed_false": contains_normalized(
            tex,
            "It is not theorem evidence unless the named primitives are independently proved on the same compact branch",
        ),
        "theorem_scope_primitive_boundary_present": all(theorem_scope_primitive_boundary.values()),
        "taylor_finite_implication_present": all(taylor_finite_implication.values()),
    }


def reader_facing_boundary_checks(text: str) -> dict[str, Any]:
    tokens = {token: contains_normalized(text, token) for token in READER_FACING_BOUNDARY_TOKENS}
    return {
        "tokens": tokens,
        "all_tokens_present": all(tokens.values()),
    }


def main() -> None:
    main_tex = read_text(MAIN_TEX)
    flat_tex = read_text(FLAT_TEX)
    main_pdf_text = read_text(MAIN_PDF_TEXT)
    flat_pdf_text = read_text(FLAT_PDF_TEXT)
    proof_closure = read_json(PROOF_CLOSURE)
    proof_contract = read_json(PROOF_CONTRACT)
    proof_evidence = read_text(PROOF_EVIDENCE)
    claim_boundary = read_json(CLAIM_BOUNDARY)
    blocker_gate = read_json(BLOCKER_GATE)
    newton_euler_symbolic_target = read_json(NEWTON_EULER_SYMBOLIC_TARGET)
    newton_euler_symbolic_defect_certificate = read_json(NEWTON_EULER_SYMBOLIC_DEFECT_CERTIFICATE)
    newton_euler_coverage = newton_euler_symbolic_target.get("obligation_coverage_matrix", {})
    newton_euler_defect_summary = newton_euler_symbolic_defect_certificate.get("summary", {})

    close_requirements = proof_closure.get("close_requirements", [])
    theorem_assumptions = proof_closure.get("theorem_assumption_coverage", [])
    open_newton = proof_closure.get("newton_euler_open_obligations", [])
    closed_newton = proof_closure.get("newton_euler_closed_obligations", [])
    closure_state = proof_closure.get("closure_state", {})
    proof_closure_remaining = proof_closure.get("remaining_gate_scope", {})
    strict_direct_standard = proof_closure.get(
        "strict_direct_residual_bridge_submission_standard", {}
    )
    solver_state = proof_closure.get("solver_state", {})
    evidence_summary = proof_closure.get("evidence_summary", {})
    theorem_statement_boundary = proof_closure.get("theorem_statement_boundary", {})
    manuscript_traceability = proof_closure.get("manuscript_traceability", {})
    theorem_reading_guide_present = (
        theorem_statement_boundary.get("theorem_reading_guide_present_main_and_flat")
        is True
    )
    primary_claim = claim_boundary.get("primary_claim", {})
    close_requirements_by_id = {item.get("id"): item for item in close_requirements}
    main_source_checks = source_checks(main_tex)
    flat_source_checks = source_checks(flat_tex)
    reader_facing_boundary = {
        "main_tex": reader_facing_boundary_checks(main_tex),
        "flat_tex": reader_facing_boundary_checks(flat_tex),
        "main_pdf_text": reader_facing_boundary_checks(main_pdf_text),
        "flat_pdf_text": reader_facing_boundary_checks(flat_pdf_text),
    }
    reader_facing_boundary_present = all(
        item["all_tokens_present"] for item in reader_facing_boundary.values()
    )
    p7_nonpromotion_boundary_tokens = [
        "residual-only mechanism rows require a separate",
        "P7 remains a separate output nonclaim/residual-to-error boundary",
        "not a theorem premise",
    ]
    p7_nonpromotion_boundary = {
        "main_tex": {
            token: contains_normalized(main_tex, token)
            for token in p7_nonpromotion_boundary_tokens
        },
        "flat_tex": {
            token: contains_normalized(flat_tex, token)
            for token in p7_nonpromotion_boundary_tokens
        },
    }
    p7_nonpromotion_boundary_present = all(
        all(token_map.values()) for token_map in p7_nonpromotion_boundary.values()
    )
    b1_closure_scope_tokens = [
        "implementation-path boundary",
        "closed certificate supplies",
        "AD-expanded implementation-path",
        "active direct residual route only",
        "does not close the primitive dynamic symbolic oracle",
        "primitive symbolic defect certificate",
        "source-paper residual replacement",
        "source-policy package readiness",
    ]
    b1_closure_scope_boundary = {
        "main_tex": {
            token: contains_normalized(main_tex, token)
            for token in b1_closure_scope_tokens
        },
        "flat_tex": {
            token: contains_normalized(flat_tex, token)
            for token in b1_closure_scope_tokens
        },
        "main_pdf_text": {
            token: contains_normalized(main_pdf_text, token)
            for token in b1_closure_scope_tokens
        },
        "flat_pdf_text": {
            token: contains_normalized(flat_pdf_text, token)
            for token in b1_closure_scope_tokens
        },
    }
    b1_closure_scope_boundary_present = all(
        all(token_map.values()) for token_map in b1_closure_scope_boundary.values()
    )
    p6_solver_scope_tokens = [
        "P6 remains the explicit theorem condition",
        "P6/P7 non-closing arrow contract",
        "The reverse arrow is not used",
        "after the compact-tube branch",
        "does not prove the compact-tube P6 condition",
        "branch-scale consistency only",
        "Solver-envelope admissibility criterion",
        "solver-admissible transition set",
        "not a postprocessing filter",
        "failed branch-ball membership",
        "P6 remains the explicit theorem",
        "branch-selected solver hypothesis",
        "do not prove a theorem-level solver-policy theorem",
        "not turn fixed tolerances into an asymptotic proof",
        "do not assert global Newton",
        "remote-root selection",
        "P6 solver-policy interface table",
        "P6 solver-scale interpretation",
        "solver-policy assumption discharge",
        "finite one-step",
        "finite short-trajectory probes",
        "tolerance-regime sweeps",
        "AD Jacobian probes",
        "branch-selected Newton diagnostics",
        "P6 admissibility boundary",
        "residual-tolerance",
        "not a restatement of the theorem conclusion",
        "computable 132-row residual norm",
        "stopping rule can be applied",
        "before endpoint error or observed order",
        "Solver-envelope quantifier discipline",
        "P6 conditional-instantiation checkpoint",
        "operational sufficient instantiation",
        "proof norm, row scaling, branch rule",
        "Backend-norm compatibility rule",
        "predeclared \\(h\\)-uniform conversion",
        "same row-scaled map \\(F_{A,h}\\)",
        "backend norms, relative residuals, correction norms",
        "cannot supply",
        "same Gauss-predictor branch",
        "proof-norm stopping target",
        "reported-grid specialization",
        "Reported solver logs are not a P6 proof",
        "not a compact-tube solver envelope",
        "It cannot calibrate",
        "prove branch membership",
        "sufficient instantiation rule",
    "does not prove a theorem-level solver-policy theorem",
    "residual ratios",
    "remote-root exclusion",
    "Direct residual-bridge scope convention",
    "residual-bridge/Kantorovich input",
    "does not prove a solver-policy theorem",
    "separate primitive/Taylor T3 route",
    "multiplier/reaction output-order claims",
    "does not enlarge the theorem conclusion",
    "before the step-size window",
    "before any residual logs are read",
    "changes the theorem hypothesis and the local-defect constant",
        "not a proof of P6",
        "finite diagnostics into theorem-level solver-policy proof",
        "not inferred from observed slopes",
        "exact trajectory",
        "compact-tube branch-membership and strong-local-inverse hypothesis",
        "retained theorem-level solver-policy condition",
        "P6 is the retained theorem-level solver-policy condition",
        "fixed tolerances",
        "asymptotic proof",
        "Uniform all-transition solver-policy theorem",
        "Additional theorem evidence needed only to prove P6 as a separate uniform",
        "all-transition solver-policy result",
        "conditional on P6",
        "The uniform all-transition scaled trajectory solver theorem is",
        "not proved here and is not needed to state the conditional theorem",
        "diagnostic-grade solver information",
    ]
    p6_solver_scope_pdf_reader_tokens = [
        "P6 solver-scale interpretation",
        "Reported solver logs are not a P6 proof",
        "Backend-norm compatibility rule",
        "predeclared h-uniform conversion",
        "not a compact-tube solver envelope",
        "conditional on P6",
        "compact-tube branch-membership and strong-local-inverse hypothesis",
        "does not prove a solver-policy theorem",
    ]
    p6_solver_scope_boundary = {
        "main_tex": {
            token: contains_normalized(main_tex, token)
            for token in p6_solver_scope_tokens
        },
        "flat_tex": {
            token: contains_normalized(flat_tex, token)
            for token in p6_solver_scope_tokens
        },
        "main_pdf_text": {
            token: contains_normalized(main_pdf_text, token)
            for token in p6_solver_scope_pdf_reader_tokens
        },
        "flat_pdf_text": {
            token: contains_normalized(flat_pdf_text, token)
            for token in p6_solver_scope_pdf_reader_tokens
        },
    }
    p6_solver_scope_tex_present = all(
        all(p6_solver_scope_boundary[source].values())
        for source in ["main_tex", "flat_tex"]
    )
    p6_solver_scope_pdf_reader_present = all(
        all(p6_solver_scope_boundary[source].values())
        for source in ["main_pdf_text", "flat_pdf_text"]
    )
    p6_solver_scope_boundary_present = (
        p6_solver_scope_tex_present and p6_solver_scope_pdf_reader_present
    )
    p1p2_compact_tube_tokens = [
        "compact-tube boundary",
        "P1 and P2 remain retained",
        "compact-tube theorem interfaces",
        "diagnose the selected branch only",
        "do not prove or remove smooth-lift",
        "uniform compact-tube invertibility",
        "right-inverse hypotheses",
        "tube-retention stability",
        "P1/P2 compact-tube interfaces",
        "P1/P2 compact-tube interpretation",
        "Retained object",
        "Current diagnostic",
        "Non-discharge",
        "assumption discharge",
        "lift regularity",
        "compact-tube inverse",
        "endpoint-ball/right-inverse",
        "strong local residual inverse",
        "reproducibility package evidence",
        "does not prove P1/P2",
        "load-bearing P1/P2",
        "Compact-inverse quantifier discipline",
        "proof residual norm",
        "inverse constants",
        "endpoint norm",
        "per-step projection log",
        "rank probe, solver log",
        "retained P2 interface",
        "refitting the tube or inverse constant",
        "single compact tube",
        "independent radius and constants",
        "selection map fixed before the asymptotic limit",
        "same row/column chart",
        "uniform right inverses on the tube",
        "do not establish tube retention",
        "uniform lower margin",
        "cannot be fitted from observed convergence",
    ]
    p1p2_compact_tube_pdf_reader_tokens = [
        "P1/P2 compact-tube boundary",
        "P1 and P2 remain retained",
        "uniform compact-tube invertibility",
        "P1/P2 compact-tube interpretation",
        "does not prove P1/P2",
    ]
    p1p2_compact_tube_boundary = {
        "main_tex": {
            token: contains_normalized(main_tex, token)
            for token in p1p2_compact_tube_tokens
        },
        "flat_tex": {
            token: contains_normalized(flat_tex, token)
            for token in p1p2_compact_tube_tokens
        },
        "main_pdf_text": {
            token: contains_normalized(main_pdf_text, token)
            for token in p1p2_compact_tube_pdf_reader_tokens
        },
        "flat_pdf_text": {
            token: contains_normalized(flat_pdf_text, token)
            for token in p1p2_compact_tube_pdf_reader_tokens
        },
    }
    p1p2_compact_tube_tex_present = all(
        all(p1p2_compact_tube_boundary[source].values())
        for source in ["main_tex", "flat_tex"]
    )
    p1p2_compact_tube_pdf_reader_present = all(
        all(p1p2_compact_tube_boundary[source].values())
        for source in ["main_pdf_text", "flat_pdf_text"]
    )
    p1p2_compact_tube_boundary_present = (
        p1p2_compact_tube_tex_present and p1p2_compact_tube_pdf_reader_present
    )
    p3p4_implementation_boundary_tokens = [
        "P3/P4 implementation-defect boundary",
        "P3/P4 implementation-defect boundary",
        "implemented direct-route residual",
        "consumed by the same-branch direct residual bridge",
        "AD-expanded implementation-path certificate is closed",
        "primitive dynamic symbolic oracle",
        "primitive/Taylor symbolic-defect route",
        "residual reproduction",
        "lower-pair rows; it does not by itself prove the full 132-row",
        "does not by itself prove the full 132-row stage",
        "separate 36-row D5 direct-substitution",
        "P3/P4 implementation-defect interface table",
        "P3/P4 implementation-defect boundary",
        "implementation-defect proof",
        "P3 runtime",
        "full-TFE readiness",
        "P4 96-row",
        "P4 handoff",
        "theorem-domain interfaces",
        "separate P5",
        "primitive dynamic symbolic oracle closure",
        "primitive/Taylor symbolic-defect route closure",
        "full 132-row stage",
        "does not close P3/P4",
        "promote P3/P4",
    ]
    p3p4_implementation_boundary = {
        "main_tex": {
            token: contains_normalized(main_tex, token)
            for token in p3p4_implementation_boundary_tokens
        },
        "flat_tex": {
            token: contains_normalized(flat_tex, token)
            for token in p3p4_implementation_boundary_tokens
        },
        "main_pdf_text": {
            token: contains_normalized(main_pdf_text, token)
            for token in p3p4_implementation_boundary_tokens
        },
        "flat_pdf_text": {
            token: contains_normalized(flat_pdf_text, token)
            for token in p3p4_implementation_boundary_tokens
        },
    }
    p3p4_implementation_boundary_present = all(
        all(token_map.values()) for token_map in p3p4_implementation_boundary.values()
    )
    p5_direct_route_tokens = [
        "P5 direct-route boundary",
        "P5 direct-route boundary: P5",
        "residual identity on the smooth Gauss lift",
        "The 36 Newton",
        "D5 direct-substitution certificate",
        "residual control",
        "inexact Newton iterate",
        "finite-run trajectories",
        "closed-loop mechanism residual tables",
        "source-policy rows",
        "residual-to-error promotion",
        "P5 direct-route satisfaction for",
        "P5 direct-route satisfaction rule",
        "not a global residual or trajectory certificate",
        "P5 stage-local",
        "P5 smooth-lift",
        "P5 handoff",
        "promotion rule",
        "row identity",
        "P5 is the only",
        "primitive dynamic symbolic oracle closure",
        "does not promote P5 beyond the direct stage-local",
        "P5 inverse-boundary",
        "dynamic block of the residual vector",
        "stage-Jacobian inverse",
        "contraction radius",
        "branch-selection theorem",
        "endpoint right inverse",
        "stability factor",
        "solver policy",
    ]
    p5_direct_route_boundary = {
        "main_tex": {
            token: contains_normalized(main_tex, token)
            for token in p5_direct_route_tokens
        },
        "flat_tex": {
            token: contains_normalized(flat_tex, token)
            for token in p5_direct_route_tokens
        },
        "main_pdf_text": {
            token: contains_normalized(main_pdf_text, token)
            for token in p5_direct_route_tokens
        },
        "flat_pdf_text": {
            token: contains_normalized(flat_pdf_text, token)
            for token in p5_direct_route_tokens
        },
    }
    p5_direct_route_boundary_present = all(
        all(token_map.values()) for token_map in p5_direct_route_boundary.values()
    )
    proof_causality_table_tokens = [
        "Proof skeleton",
        "perturbation chain",
        "Proof causality",
        "Proof-causality rule",
        "Mathematical input",
        "Consumed before",
        "Allowed source",
        "non-source",
        "D5 direct-substitution certificate",
        "local perturbation",
        "local defect bound is established before",
        "reporting map is used",
        "reduced-chart grid estimate",
        "downstream diagnostics",
        "do not feed PC2",
        "theorem-level solver-policy result",
        "residual-to-error transfer theorem",
        "source-policy readiness",
        "full-TFE readiness",
    ]
    proof_causality_table = {
        "main_tex": {
            token: contains_normalized(main_tex, token)
            for token in proof_causality_table_tokens
        },
        "flat_tex": {
            token: contains_normalized(flat_tex, token)
            for token in proof_causality_table_tokens
        },
        "main_pdf_text": {
            token: contains_normalized(main_pdf_text, token)
            for token in proof_causality_table_tokens
        },
        "flat_pdf_text": {
            token: contains_normalized(flat_pdf_text, token)
            for token in proof_causality_table_tokens
        },
    }
    proof_causality_table_present = all(
        all(token_map.values()) for token_map in proof_causality_table.values()
    )
    direct_route_anticircularity_table_tokens = [
        "Direct-route anti-circularity table",
        "Direct-route anti-circularity rule",
        "Proof object",
        "Fixed before",
        "May depend on",
        "Explicit non-dependence",
        "Lifted Gauss stage",
        "implemented residual rows",
        "D5 direct-substitution certificate",
        "local perturbation",
        "theorem conclusion",
        "direct route is admissible",
        "D5 direct-substitution identities",
        "fixed before",
        "does not justify row identities",
        "residual/reaction tables",
        "not sources for D5",
        "does not prove P1/P2/P6/P7",
        "dynamic symbolic oracle",
        "primitive/Taylor route",
        "reproducibility package readiness evidence",
    ]
    direct_route_anticircularity_table = {
        "main_tex": {
            token: contains_normalized(main_tex, token)
            for token in direct_route_anticircularity_table_tokens
        },
        "flat_tex": {
            token: contains_normalized(flat_tex, token)
            for token in direct_route_anticircularity_table_tokens
        },
        "main_pdf_text": {
            token: contains_normalized(main_pdf_text, token)
            for token in direct_route_anticircularity_table_tokens
        },
        "flat_pdf_text": {
            token: contains_normalized(flat_pdf_text, token)
            for token in direct_route_anticircularity_table_tokens
        },
    }
    direct_route_anticircularity_table_present = all(
        all(token_map.values())
        for token_map in direct_route_anticircularity_table.values()
    )
    p_interface_satisfaction_tokens = [
        "Assumptions and theorem scope",
        "Proof-domain partition",
        "P5 is the only stage-local dynamic identity proved",
        "P1/P2/P3, the retained P4 binding side, and P6 describe the branch",
        "P7 remains a separate output nonclaim/residual-to-error boundary",
        "local residual route under the retained P6",
        "domain conditions or the P7 boundary",
        "solver-policy theorem",
        "residual-to-error promotion",
        "source-policy rows",
        "reproducibility package readiness claims",
        "Route and interface separation table",
        "Route and interface separation",
        "local residual route together with the retained P6 solver-scale condition",
        "PC1 balance",
        "PC2 stage",
        "P6 is retained as the",
        "promotion is not used",
        "PC3 is interpreted only through",
        "PC3 is therefore a retained-condition",
        "not an empirical proof and not an extra certificate",
        "PC4 residual-to-error exclusion",
        "residual-to-error boundary",
        "is not a local-defect ingredient",
        "solver-policy theorem",
        "do not prove a separate residual-to-error transfer theorem",
        "Retained/discharged input rule",
        "retained domain hypotheses",
        "stage-residual inputs from theorem-domain interfaces",
        "implemented 132-row direct route",
        "does not merely assume",
        "consumes the implemented",
        "direct-route certificate",
        "after the local chart, row ordering",
        "discharged formula-residual",
        "residual input",
        "not an empirical residual fit",
    ]
    p_interface_satisfaction_table = {
        "main_tex": {
            token: contains_normalized(main_tex, token)
            for token in p_interface_satisfaction_tokens
        },
        "flat_tex": {
            token: contains_normalized(flat_tex, token)
            for token in p_interface_satisfaction_tokens
        },
        "main_pdf_text": {
            token: contains_normalized(main_pdf_text, token)
            for token in p_interface_satisfaction_tokens
        },
        "flat_pdf_text": {
            token: contains_normalized(flat_pdf_text, token)
            for token in p_interface_satisfaction_tokens
        },
    }
    p_interface_satisfaction_table_present = all(
        all(token_map.values()) for token_map in p_interface_satisfaction_table.values()
    )
    p7_residual_to_error_table_tokens = [
        "Residual-to-error boundary",
        "Residual-to-error boundary",
        "P6/P7 non-closing arrow contract",
        "The P7 clause is an output-exclusion clause",
        "Residual and reaction rows therefore remain mechanism-coverage diagnostics",
        "separate branch-compatible residual-to-error theorem",
        "fixed transfer operator",
        "independent constant required",
        "These two non-closing arrows are part of the theorem boundary",
        "P7 dependency obligations remain open",
        "Residual tables and residual-to-error ratios are diagnostics only",
        "mechanism-coverage residual row",
        "closed-loop reaction table",
        "common-reference row",
        "source-policy row is promoted",
        "trajectory-error/order evidence",
        "P7 residual-to-error operator boundary",
        "P7 fixed-operator requirement",
        "same reported closed-loop branch",
        "mechanism residual operator",
        "trajectory norm",
        "uniform stability or inf-sup inverse",
        "fixed linearized inverse",
        "fixed before observed residual data",
        "not obtained by dividing",
        "measured trajectory errors",
        "same branch residual operator with a uniform inverse",
        "small reaction or constraint residuals",
        "dynamic residual identity",
        "residual consistency",
        "stability or inf-sup control",
        "calibrated estimator",
        "reference-floor exclusion",
        "coarse-first campaign",
        "manuscript transfer theorem",
    ]
    p7_residual_to_error_table = {
        "main_tex": {
            token: contains_normalized(main_tex, token)
            for token in p7_residual_to_error_table_tokens
        },
        "flat_tex": {
            token: contains_normalized(flat_tex, token)
            for token in p7_residual_to_error_table_tokens
        },
        "main_pdf_text": {
            token: contains_normalized(main_pdf_text, token)
            for token in p7_residual_to_error_table_tokens
        },
        "flat_pdf_text": {
            token: contains_normalized(flat_pdf_text, token)
            for token in p7_residual_to_error_table_tokens
        },
    }
    p7_residual_to_error_table_present = all(
        all(token_map.values()) for token_map in p7_residual_to_error_table.values()
    )
    theorem_use_rule_tokens = [
        "Scope of auxiliary evidence",
        "Auxiliary-evidence scope",
        "theorem inputs are restricted to",
        "P1/P2/P3 conditions, the retained P4 binding interface, the P6 solver-scale condition",
        "P5 direct",
        "local reproducibility record evidence",
        "diagnostic or reproducibility-boundary evidence only",
        "not promoted to theorem-input status",
        "residual-to-error transfer theorem",
        "solver-policy theorem",
        "source-policy/full-TFE readiness",
        "not an assumed local defect estimate",
        "observed sixth-order slopes",
        "successful Newton logs",
        "Theorem input-output reading rule",
        "No arrow in this chain is used backwards",
        "instance discipline governs numerical reporting",
        "Same-object theorem-composition criterion",
        "jointly admissible tuple",
        "Reference-order contract and no-estimate transfer",
        "one-way proof-order contract",
        "typed ordering rule",
        "No BLieDF local-truncation constant",
        "reference proof is used only to order obligations",
        "missing FullVA hypotheses",
        "structural ordering discipline only; no Taylor estimate, primitive lift bound, or multiplier estimate is imported",
        "T2 full-map Taylor/Kantorovich estimate is established only for the fixed",
        "neither a premise nor a consequence of the theorem",
        "no BLieDF local-error, multiplier, or recursion estimate",
        "The theorem closure below refers only to the direct residual-bridge/Kantorovich",
        "argument under the stated branch, endpoint, implementation, and solver-scale",
        "it does not prove a separate theorem for fixed production tolerances",
        "not a separate primitive/Taylor subterm closure",
        "remains a stricter separate sufficient-route specification and is not used to",
    ]
    theorem_use_rule = {
        "main_tex": {
            token: contains_normalized(main_tex, token)
            for token in theorem_use_rule_tokens
        },
        "flat_tex": {
            token: contains_normalized(flat_tex, token)
            for token in theorem_use_rule_tokens
        },
        "main_pdf_text": {
            token: contains_normalized(main_pdf_text, token)
            for token in theorem_use_rule_tokens
        },
        "flat_pdf_text": {
            token: contains_normalized(flat_pdf_text, token)
            for token in theorem_use_rule_tokens
        },
    }
    theorem_use_rule_present = all(
        all(token_map.values()) for token_map in theorem_use_rule.values()
    )
    quantifier_domain_table_tokens = [
        "Quantifier/domain table",
        "Quantifier/domain rule",
        "Quantifier layer",
        "What is fixed or quantified",
        "Valid domain",
        "Explicit exclusions",
        "Fixed proof data",
        "all retained-tube states",
        "any reported grid",
        "accepted theorem domain",
        "reported run may instantiate the theorem",
        "branch, tube, endpoint, proof-norm",
        "post-hoc filtered solver logs",
        "table records",
        "accepted compact proof tube",
        "accepted branch-selected",
        "arbitrary Newton roots",
        "remote nonlinear roots",
        "unreported leftover interval",
        "terminal-time correction",
        "local reproducibility record states",
        "P6 is the retained theorem-level solver-policy condition",
        "P7 output nonclaim/residual-to-error boundary",
        "source-policy readiness",
        "full-TFE readiness",
        "Constant-selection hierarchy",
        "first fix the mechanism data",
        "reported branch",
        "Gauss-predictor branch rule",
        "P4 binding contract",
        "P5 direct-route certificate",
        "small enough for the Gauss truncation bound",
        "theorem constants as suprema",
        "No constant is re-fit",
        "observed slopes",
        "residual logs",
        "work-precision tables",
        "Same-object proof invariant",
        "same transition index",
        "same fixed proof norm",
        "not assembled from different runs",
    ]
    quantifier_domain_table = {
        "main_tex": {
            token: contains_normalized(main_tex, token)
            for token in quantifier_domain_table_tokens
        },
        "flat_tex": {
            token: contains_normalized(flat_tex, token)
            for token in quantifier_domain_table_tokens
        },
        "main_pdf_text": {
            token: contains_normalized(main_pdf_text, token)
            for token in quantifier_domain_table_tokens
        },
        "flat_pdf_text": {
            token: contains_normalized(flat_pdf_text, token)
            for token in quantifier_domain_table_tokens
        },
    }
    quantifier_domain_table_present = all(
        all(token_map.values()) for token_map in quantifier_domain_table.values()
    )
    local_global_transfer_table_tokens = [
        "Local-to-global initial-state boundary",
        "zero initial error",
        "unreported initial projection",
        "warm-start",
        "branch-selection",
        "chart-registration error",
        "separate initial-error",
        "not absorbed into",
        "Local-to-global transfer table",
        "Local-to-global transfer rule",
        "Transfer layer",
        "Input consumed",
        "Output produced",
        "Explicit non-use",
        "uniform branch-selected local defect",
        "stability scale",
        "tube-retention margin",
        "error recurrence",
        "tube-retention induction",
        "First-exit bootstrap",
        "first possible exit index",
        "after the Gronwall constant",
        "does not assume global tube retention",
        "first-exit index is a proof device",
        "trajectory failure log",
        "reported grid errors",
        "work-precision slopes",
        "exit diagnostics",
        "cannot calibrate",
        "finite run",
        "first-exit bootstrap",
        "hypothetical exit from the retained tube",
        "inside the tube margin",
        "Gronwall factor",
        "trajectory plots",
        "discrete Gronwall on reported transition steps",
        "Reference-style recursion analogue",
        "The analogy is structural, not an estimate transfer",
        "algebraic variables and stage multipliers have already been consumed inside",
        "There is no hidden multiplier recursion",
        "separate coupled output recursion",
        "accepted recurrence",
        "same initial reduced-chart state",
        "branch-registration defect",
        "resampled or postprocessed",
        "same-initial-state reported-grid estimate",
        "reported output indices",
        "reporting-map consequence",
        "residual/reaction tables",
        "sweep fits",
        "fixed production tolerances",
        "cannot fit a stability constant",
        "failed tube-retention row",
        "source-policy rows",
        "unreported leftover interval",
        "extra terminal solve",
        "P6 is the retained theorem-level solver-policy condition",
        "P7 output nonclaim/residual-to-error boundary",
        "source-policy readiness",
        "full-TFE readiness",
    ]
    local_global_transfer_table = {
        "main_tex": {
            token: contains_normalized(main_tex, token)
            for token in local_global_transfer_table_tokens
        },
        "flat_tex": {
            token: contains_normalized(flat_tex, token)
            for token in local_global_transfer_table_tokens
        },
        "main_pdf_text": {
            token: contains_normalized(main_pdf_text, token)
            for token in local_global_transfer_table_tokens
        },
        "flat_pdf_text": {
            token: contains_normalized(flat_pdf_text, token)
            for token in local_global_transfer_table_tokens
        },
    }
    local_global_transfer_table_present = all(
        all(token_map.values()) for token_map in local_global_transfer_table.values()
    )
    objective_completion_boundary_tokens = [
        "External reproduction and package boundaries retained by the paper package",
        "External reproduction/package boundary",
        "same-test",
        "source-policy reproduction",
        "no external rows",
        "Original",
        "runner package",
        "A complete source-policy",
        "Runner archive",
        "boundary",
        "bounded replay/provenance role",
        "full source-policy runner archive is outside this package",
        "outside the accepted theorem and comparison claims",
        "the three rows",
        "are scope boundaries",
        "do not change the conditional theorem proof",
        "source-policy reproduction",
        "runner evidence",
        "That archive is outside the current paper package",
    ]
    objective_completion_boundary = {
        "main_tex": {
            token: contains_normalized(main_tex, token)
            for token in objective_completion_boundary_tokens
        },
        "flat_tex": {
            token: contains_normalized(flat_tex, token)
            for token in objective_completion_boundary_tokens
        },
        "main_pdf_text": {
            token: contains_normalized(main_pdf_text, token)
            for token in objective_completion_boundary_tokens
        },
        "flat_pdf_text": {
            token: contains_normalized(flat_pdf_text, token)
            for token in objective_completion_boundary_tokens
        },
    }
    objective_completion_boundary_present = all(
        all(token_map.values()) for token_map in objective_completion_boundary.values()
    )
    constant_dependency_table_tokens = [
        "Constant-dependency table",
        "Constant-dependency rule",
        "Explicit non-dependencies",
        "compact-tube constants only",
        "h-sweep",
        "source-policy comparison",
        "source-policy comparison",
        "residual/reaction table",
        "local reproducibility record",
        "P6 is the retained theorem-level solver-policy condition",
        "P7 output nonclaim/residual-to-error boundary",
        "source-policy readiness",
        "full-TFE readiness",
    ]
    constant_dependency_table = {
        "main_tex": {
            token: contains_normalized(main_tex, token)
            for token in constant_dependency_table_tokens
        },
        "flat_tex": {
            token: contains_normalized(flat_tex, token)
            for token in constant_dependency_table_tokens
        },
        "main_pdf_text": {
            token: contains_normalized(main_pdf_text, token)
            for token in constant_dependency_table_tokens
        },
        "flat_pdf_text": {
            token: contains_normalized(flat_pdf_text, token)
            for token in constant_dependency_table_tokens
        },
    }
    constant_dependency_table_present = all(
        all(token_map.values()) for token_map in constant_dependency_table.values()
    )
    theorem_dependency_consumption_table_tokens = [
        "Theorem input-output flow",
        "Theorem input-output flow",
        "First consumed by",
        "Later theorem output",
        "P1/P2",
        "P3/P4",
        "P5 supplies",
        "retained branch-solver scale",
        "P7 is recorded",
        "residual-to-error boundary",
        "implemented residual path",
        "transfer-scope exclusion",
        "displayed inputs record",
        "explicit exclusions",
        "theorem-level solver-policy result",
        "residual-to-error promotion",
        "source-policy readiness",
        "reproducibility package readiness claims",
    ]
    theorem_dependency_consumption_table = {
        "main_tex": {
            token: contains_normalized(main_tex, token)
            for token in theorem_dependency_consumption_table_tokens
        },
        "flat_tex": {
            token: contains_normalized(flat_tex, token)
            for token in theorem_dependency_consumption_table_tokens
        },
        "main_pdf_text": {
            token: contains_normalized(main_pdf_text, token)
            for token in theorem_dependency_consumption_table_tokens
        },
        "flat_pdf_text": {
            token: contains_normalized(flat_pdf_text, token)
            for token in theorem_dependency_consumption_table_tokens
        },
    }
    theorem_dependency_consumption_table_present = all(
        all(token_map.values()) for token_map in theorem_dependency_consumption_table.values()
    )
    branch_consistency_table_tokens = [
        "Accepted branch-selected one-step map",
        "defined on the accepted subset",
        "Its theorem domain is the subset",
        "map is obtained by",
        "local root of the implemented 132-row residual",
        "fixed row ordering, finite row scaling, and proof norm",
        "map is undefined for theorem purposes",
        "not an extra terminal solve",
        "remote nonlinear root",
        "First-exit/P6 separation",
        "scaled residual part is not supplied by",
        "remains the retained P6 hypothesis",
        "Accepted-map definition boundary",
        "branch-selected accepted-domain map tied to the Gauss predictor",
        "not a global nonlinear-solver selection rule",
        "Accepted-branch consistency for",
        "Accepted-branch consistency rule",
        "Proof object",
        "Branch identity used",
        "Consistency source",
        "Explicit exclusion",
        "Gauss predictor",
        "local accepted stage root",
        "endpoint closure",
        "endpoint closure, and retained inexact-Newton",
        "same compact-tube branch",
        "Gauss-predictor ball",
        "retained branch",
        "accepted-branch transitions",
        "remote-chart equivalence",
        "arbitrary Newton-root selection",
        "global nonlinear solver uniqueness",
        "terminal-time error",
        "source-policy reproduction",
    ]
    branch_consistency_table = {
        "main_tex": {
            token: contains_normalized(main_tex, token)
            for token in branch_consistency_table_tokens
        },
        "flat_tex": {
            token: contains_normalized(flat_tex, token)
            for token in branch_consistency_table_tokens
        },
        "main_pdf_text": {
            token: contains_normalized(main_pdf_text, token)
            for token in branch_consistency_table_tokens
        },
        "flat_pdf_text": {
            token: contains_normalized(flat_pdf_text, token)
            for token in branch_consistency_table_tokens
        },
    }
    branch_consistency_table_present = all(
        all(token_map.values()) for token_map in branch_consistency_table.values()
    )
    implementation_route_oracle_table_tokens = [
        "Implementation-route/certificate separation table",
        "Implementation-route/certificate separation",
        "Theorem role",
        "Closed evidence",
        "Explicit non-use",
        "implemented 132-row direct route",
        "Runtime formula/AD binding",
        "AD-expanded certificate",
        "remain diagnostic",
        "source-policy readiness",
        "stage-residual argument discharged by the direct route",
        "open primitive symbolic route",
        "non-active primitive symbolic-oracle",
        "inputs to the theorem",
        "not contradictions",
        "direct D5 substitution closure",
        "not source-paper residual replacement",
        "reproducibility package readiness evidence",
    ]
    implementation_route_oracle_table = {
        "main_tex": {
            token: contains_normalized(main_tex, token)
            for token in implementation_route_oracle_table_tokens
        },
        "flat_tex": {
            token: contains_normalized(flat_tex, token)
            for token in implementation_route_oracle_table_tokens
        },
        "main_pdf_text": {
            token: contains_normalized(main_pdf_text, token)
            for token in implementation_route_oracle_table_tokens
        },
        "flat_pdf_text": {
            token: contains_normalized(flat_pdf_text, token)
            for token in implementation_route_oracle_table_tokens
        },
    }
    implementation_route_oracle_table_present = all(
        all(token_map.values()) for token_map in implementation_route_oracle_table.values()
    )
    nonlinear_solver_scale_table_tokens = [
        "Nonlinear-solver scale conditions",
        "Nonlinear-solver scale rule",
        "Solver-scale object",
        "Theorem role",
        "evidence boundary",
        "Explicit non-use",
        "retained P6",
        "reported-grid maximum",
        "finite scaled-tolerance probes",
        "Diagnose branch-scale",
        "trajectory specializations",
        "one-step estimate is local",
        "reported-trajectory specialization",
        "additional local hypothesis",
        "load-bearing solver object",
        "compact-tube envelope",
        "not a fitted residual sequence",
        "Accepted-branch consistency rule",
        "tube-envelope hypothesis",
        "independent solver-policy",
        "Solver-envelope quantifier discipline",
        "Backend-norm compatibility rule",
        "uniform conversion",
        "same row-scaled map",
        "backend norms, relative residuals, correction norms",
        "cannot supply",
        "finite logs",
        "changes the theorem hypothesis and local-defect constant",
        "not a proof of P6",
        "theorem-level solver-policy theorem",
        "fixed-tolerance asymptotic proof",
        "global Newton convergence",
        "arbitrary Newton-root selection",
        "source-policy reproduction",
        "residual-to-error promotion",
        "reproducibility package readiness evidence",
    ]
    nonlinear_solver_scale_table = {
        "main_tex": {
            token: contains_normalized(main_tex, token)
            for token in nonlinear_solver_scale_table_tokens
        },
        "flat_tex": {
            token: contains_normalized(flat_tex, token)
            for token in nonlinear_solver_scale_table_tokens
        },
        "main_pdf_text": {
            token: contains_normalized(main_pdf_text, token)
            for token in nonlinear_solver_scale_table_tokens
        },
        "flat_pdf_text": {
            token: contains_normalized(flat_pdf_text, token)
            for token in nonlinear_solver_scale_table_tokens
        },
    }
    nonlinear_solver_scale_table_present = all(
        all(token_map.values()) for token_map in nonlinear_solver_scale_table.values()
    )
    local_defect_decomposition_table_tokens = [
        "Local-defect map-chain definition",
        "proof compares exactly one chain of maps",
        "same compact branch",
        "exact local root of the implemented",
        "endpoint-closed exact-stage reference for the inexact Newton perturbation",
        "endpoint-closed inexact Newton map",
        "endpoint-output map",
        "same reduced-chart endpoint norm",
        "defined the residual-to-stage",
        "perturbation input",
        "branch, chart, norm, or transition index",
        "Algorithm-order consistency",
        "computes the inexact stage iterate",
        "same implemented output order",
        "exact-root reference",
        "not a reordered algorithm",
        "two already endpoint-closed outputs",
        "never mixes an unclosed inexact endpoint with a closed exact endpoint",
        "Local-defect decomposition for",
        "Local-defect decomposition rule",
        "Triangle term",
        "Bound used",
        "Proof source",
        "Explicit non-use",
        "Gauss truncation",
        "Gauss truncation constant boundary",
        "analytic collocation constant",
        "reduced-vector-field bounds",
        "implementation residual diagnostics",
        "endpoint-closure logs",
        "observed smooth",
        "cannot choose",
        "shrink the tube",
        "select the Gauss-predictor branch",
        "Stage-root",
        "Endpoint closure",
        "Inexact Newton",
        "Local-defect sum",
        "Norm/row-scaling bridge",
        "outputs live in this same theorem object",
        "C1 local-error slot",
        "same reduced-chart norm used by the stability recurrence",
        "different typed object",
        "explicit equivalence or transport lemma",
        "proof residual norm",
        "root norm",
        "fixed 132-row residual norm",
        "residual norm to the local stage-root norm",
        "endpoint norm",
        "endpoint-output map",
        "local endpoint-closure Lipschitz factor",
        "reduced-chart one-step",
        "separate compact-tube factor",
        "row scalings",
        "residual-log norm",
        "mechanism table norm",
        "four displayed accepted-branch",
        "finite-run h-sweeps",
        "remote nonlinear roots",
        "primitive symbolic oracle",
        "global Newton convergence",
        "residual-to-error promotion",
        "source-policy rows",
        "full-TFE readiness",
    ]
    local_defect_decomposition_table = {
        "main_tex": {
            token: contains_normalized(main_tex, token)
            for token in local_defect_decomposition_table_tokens
        },
        "flat_tex": {
            token: contains_normalized(flat_tex, token)
            for token in local_defect_decomposition_table_tokens
        },
        "main_pdf_text": {
            token: contains_normalized(main_pdf_text, token)
            for token in local_defect_decomposition_table_tokens
        },
        "flat_pdf_text": {
            token: contains_normalized(flat_pdf_text, token)
            for token in local_defect_decomposition_table_tokens
        },
    }
    local_defect_decomposition_table_present = (
        manuscript_traceability.get("local_defect_decomposition_table_present_main_and_flat")
        is True
    )
    theorem_output_scope_table_tokens = [
        "Theorem output scope",
        "Theorem output scope rule",
        "Output layer",
        "Proven statement",
        "Proof source",
        "Explicit non-output",
        "One-step accepted",
        "reduced grid",
        "reported grid",
        "Method-order",
        "sentence",
        "branch-selected one-step",
    "reported-grid",
    "Order six in the",
    "reported-grid sense",
    "constraint-output error estimates",
    "does not prove a P7 residual-to-error boundary",
    "does not turn fixed-tolerance finite runs",
    "residual/reaction table",
    "unreported terminal-time error",
    "not an interpolation statement",
        "off-grid sampling times",
        "dense output",
        "resampled work-precision curves",
        "postprocessed terminal value",
        "same branch/tube hypotheses",
        "reported trajectory is read",
        "output formatting",
        "interpolation policy",
        "remote-chart equivalence",
        "external superiority",
        "source-policy reproduction",
        "fixed-tolerance asymptotic proof",
    ]
    theorem_output_scope_table = {
        "main_tex": {
            token: contains_normalized(main_tex, token)
            for token in theorem_output_scope_table_tokens
        },
        "flat_tex": {
            token: contains_normalized(flat_tex, token)
            for token in theorem_output_scope_table_tokens
        },
        "main_pdf_text": {
            token: contains_normalized(main_pdf_text, token)
            for token in theorem_output_scope_table_tokens
        },
        "flat_pdf_text": {
            token: contains_normalized(flat_pdf_text, token)
            for token in theorem_output_scope_table_tokens
        },
    }
    theorem_output_scope_table_present = all(
        all(token_map.values()) for token_map in theorem_output_scope_table.values()
    )
    reporting_map_table_tokens = [
        "Reporting-map/norm-equivalence table",
        "Reporting-map/norm-equivalence rule",
        "Reporting step",
        "Input estimate",
        "Uniform map property",
        "Explicit non-use",
        "Derivative bound",
        "same output indices",
        "reduced-chart grid error",
        "accepted tube",
        "same reported grid",
        "reporting-map consequence",
        "residual-to-error transfer theorem",
        "reaction diagnostic",
        "global chart equivalence",
        "remote branch statement",
        "source-policy reproduction",
        "fitted-constant claim",
        "terminal-time claim",
        "not an interpolation statement",
        "off-grid sampling times",
        "dense output",
        "resampled work-precision curves",
        "postprocessed terminal value",
        "same branch/tube hypotheses",
        "reported trajectory is read",
        "output formatting",
        "interpolation policy",
    ]
    reporting_map_table = {
        "main_tex": {
            token: contains_normalized(main_tex, token)
            for token in reporting_map_table_tokens
        },
        "flat_tex": {
            token: contains_normalized(flat_tex, token)
            for token in reporting_map_table_tokens
        },
        "main_pdf_text": {
            token: contains_normalized(main_pdf_text, token)
            for token in reporting_map_table_tokens
        },
        "flat_pdf_text": {
            token: contains_normalized(flat_pdf_text, token)
            for token in reporting_map_table_tokens
        },
    }
    reporting_map_table_present = all(
        all(token_map.values()) for token_map in reporting_map_table.values()
    )
    theorem_conclusion_scope_guard = {
        "main_tex": {
            token: contains_normalized(main_tex, token)
            for token in THEOREM_CONCLUSION_SCOPE_GUARD_TOKENS
        },
        "flat_tex": {
            token: contains_normalized(flat_tex, token)
            for token in THEOREM_CONCLUSION_SCOPE_GUARD_TOKENS
        },
        "main_pdf_text": {
            token: contains_normalized(main_pdf_text, token)
            for token in THEOREM_CONCLUSION_SCOPE_GUARD_TOKENS
        },
        "flat_pdf_text": {
            token: contains_normalized(flat_pdf_text, token)
            for token in THEOREM_CONCLUSION_SCOPE_GUARD_TOKENS
        },
    }
    theorem_conclusion_scope_guard_present = all(
        all(token_map.values()) for token_map in theorem_conclusion_scope_guard.values()
    )
    proof_strength_certificate = {
        "main_tex": {
            token: contains_normalized(main_tex, token)
            for token in PROOF_STRENGTH_CERTIFICATE_TOKENS
        },
        "flat_tex": {
            token: contains_normalized(flat_tex, token)
            for token in PROOF_STRENGTH_CERTIFICATE_TOKENS
        },
        "main_pdf_text": {
            token: contains_normalized(main_pdf_text, token)
            for token in PROOF_STRENGTH_CERTIFICATE_TOKENS
        },
        "flat_pdf_text": {
            token: contains_normalized(flat_pdf_text, token)
            for token in PROOF_STRENGTH_CERTIFICATE_TOKENS
        },
    }
    proof_strength_certificate_present = all(
        all(token_map.values()) for token_map in proof_strength_certificate.values()
    )
    full_residual_bridge = {
        "main_tex": {
            token: contains_normalized(main_tex, token)
            for token in FULL_RESIDUAL_BRIDGE_TOKENS
        },
        "flat_tex": {
            token: contains_normalized(flat_tex, token)
            for token in FULL_RESIDUAL_BRIDGE_TOKENS
        },
        "main_pdf_text": {
            token: contains_normalized(main_pdf_text, token)
            for token in FULL_RESIDUAL_BRIDGE_TOKENS
        },
        "flat_pdf_text": {
            token: contains_normalized(flat_pdf_text, token)
            for token in FULL_RESIDUAL_BRIDGE_TOKENS
        },
    }
    full_residual_bridge_present = all(
        all(token_map.values()) for token_map in full_residual_bridge.values()
    )
    route_exclusivity_boundary = {
        "main_tex": {
            token: contains_normalized(main_tex, token)
            for token in ROUTE_EXCLUSIVITY_TEX_TOKENS
        },
        "flat_tex": {
            token: contains_normalized(flat_tex, token)
            for token in ROUTE_EXCLUSIVITY_TEX_TOKENS
        },
        "main_pdf_text": {
            token: contains_normalized(main_pdf_text, token)
            for token in ROUTE_EXCLUSIVITY_PDF_TEXT_TOKENS
        },
        "flat_pdf_text": {
            token: contains_normalized(flat_pdf_text, token)
            for token in ROUTE_EXCLUSIVITY_PDF_TEXT_TOKENS
        },
    }
    route_exclusivity_boundary_present = all(
        all(token_map.values()) for token_map in route_exclusivity_boundary.values()
    )
    theorem_residual_certificate_exclusivity = {
        "main_tex": {
            token: contains_normalized(main_tex, token)
            for token in THEOREM_RESIDUAL_CERTIFICATE_EXCLUSIVITY_TEX_TOKENS
        },
        "flat_tex": {
            token: contains_normalized(flat_tex, token)
            for token in THEOREM_RESIDUAL_CERTIFICATE_EXCLUSIVITY_TEX_TOKENS
        },
        "main_pdf_text": {
            token: contains_normalized(main_pdf_text, token)
            for token in THEOREM_RESIDUAL_CERTIFICATE_EXCLUSIVITY_PDF_TEXT_TOKENS
        },
        "flat_pdf_text": {
            token: contains_normalized(flat_pdf_text, token)
            for token in THEOREM_RESIDUAL_CERTIFICATE_EXCLUSIVITY_PDF_TEXT_TOKENS
        },
    }
    theorem_residual_certificate_exclusivity_present = all(
        all(token_map.values())
        for token_map in theorem_residual_certificate_exclusivity.values()
    )
    intro_proof_hierarchy = {
        "main_tex": {
            token: contains_normalized(main_tex, token)
            for token in INTRO_PROOF_HIERARCHY_TOKENS
        },
        "flat_tex": {
            token: contains_normalized(flat_tex, token)
            for token in INTRO_PROOF_HIERARCHY_TOKENS
        },
        "main_pdf_text": {
            token: contains_normalized(main_pdf_text, token)
            for token in INTRO_PROOF_HIERARCHY_TOKENS
        },
        "flat_pdf_text": {
            token: contains_normalized(flat_pdf_text, token)
            for token in INTRO_PROOF_HIERARCHY_TOKENS
        },
    }
    intro_proof_hierarchy_present = all(
        all(token_map.values()) for token_map in intro_proof_hierarchy.values()
    )
    manuscript_anchors = manuscript_anchor_map(main_tex, flat_tex)
    theorem_anchor_table_coverage = theorem_anchor_table_reference_coverage(main_tex, flat_tex)
    traceability_claims_mapped = (
        main_source_checks["all_labels_present"]
        and flat_source_checks["all_labels_present"]
        and main_source_checks["all_boundary_tokens_present"]
        and flat_source_checks["all_boundary_tokens_present"]
        and main_source_checks["proof_object_counts_match_expected"]
        and flat_source_checks["proof_object_counts_match_expected"]
        and main_source_checks["dynamic_proof_closure_matrix_present"]
        and flat_source_checks["dynamic_proof_closure_matrix_present"]
        and main_source_checks["newton_euler_row_target_map_present"]
        and flat_source_checks["newton_euler_row_target_map_present"]
        and main_source_checks["theorem_scope_primitive_boundary_present"]
        and flat_source_checks["theorem_scope_primitive_boundary_present"]
        and main_source_checks["taylor_finite_implication_present"]
        and flat_source_checks["taylor_finite_implication_present"]
        and reader_facing_boundary_present
        and p7_nonpromotion_boundary_present
        and b1_closure_scope_boundary_present
        and p6_solver_scope_boundary_present
        and p1p2_compact_tube_boundary_present
        and p3p4_implementation_boundary_present
        and p5_direct_route_boundary_present
        and proof_causality_table_present
        and direct_route_anticircularity_table_present
        and p_interface_satisfaction_table_present
        and p7_residual_to_error_table_present
        and theorem_use_rule_present
        and quantifier_domain_table_present
        and local_global_transfer_table_present
        and objective_completion_boundary_present
        and constant_dependency_table_present
        and theorem_dependency_consumption_table_present
        and branch_consistency_table_present
        and implementation_route_oracle_table_present
        and nonlinear_solver_scale_table_present
        and local_defect_decomposition_table_present
        and theorem_output_scope_table_present
        and reporting_map_table_present
        and theorem_conclusion_scope_guard_present
        and proof_strength_certificate_present
        and full_residual_bridge_present
        and route_exclusivity_boundary_present
        and theorem_residual_certificate_exclusivity_present
        and intro_proof_hierarchy_present
        and theorem_reading_guide_present
        and theorem_anchor_table_coverage["all_references_present_main_and_flat"]
    )
    satisfied_assumptions = sum(
        1 for item in theorem_assumptions if item.get("satisfied_for_submission")
    )
    unsatisfied_assumptions = sum(
        1 for item in theorem_assumptions if not item.get("satisfied_for_submission")
    )
    satisfied_assumption_ids = [
        item.get("id") for item in theorem_assumptions if item.get("satisfied_for_submission")
    ]
    retained_or_open_assumptions = [
        item for item in theorem_assumptions if not item.get("satisfied_for_submission")
    ]
    retained_or_open_assumption_ids = [item.get("id") for item in retained_or_open_assumptions]
    retained_theorem_interface_assumptions = [
        item for item in retained_or_open_assumptions if item.get("id") != "P7"
    ]
    retained_theorem_interface_ids = [
        item.get("id") for item in retained_theorem_interface_assumptions
    ]
    open_nonpromotion_boundary_assumptions = [
        item for item in retained_or_open_assumptions if item.get("id") == "P7"
    ]
    open_nonpromotion_boundary_ids = [
        item.get("id") for item in open_nonpromotion_boundary_assumptions
    ]
    satisfied_close_requirements = sum(1 for item in close_requirements if item.get("satisfied"))
    unsatisfied_close_requirements = sum(1 for item in close_requirements if not item.get("satisfied"))
    satisfied_close_requirement_ids = [
        item.get("id") for item in close_requirements if item.get("satisfied")
    ]
    unsatisfied_close_requirement_ids = [
        item.get("id") for item in close_requirements if not item.get("satisfied")
    ]
    global_submission_boundaries = [
        "full_source_policy_package_ready",
        "theorem_level_eta_h_solver_policy_evidence",
        "closed_residual_to_error_theorem_for_mechanism_rows",
    ]
    eta_h_condition_retained_for_pc3 = (
        close_requirements_by_id.get("PC3", {}).get("satisfied") is True
        and closure_state.get("eta_h_O_h7_solver_policy_evidence") is False
    )
    residual_to_error_route_promoted = not (
        close_requirements_by_id.get("PC4", {}).get("satisfied") is True
    )
    table_to_ledger_aliases = {
        "proof_causality_ledger_present": proof_causality_table_present,
        "direct_route_anticircularity_ledger_present": (
            direct_route_anticircularity_table_present
        ),
        "p_interface_satisfaction_ledger_present": p_interface_satisfaction_table_present,
        "p7_residual_to_error_ledger_present": p7_residual_to_error_table_present,
        "quantifier_domain_ledger_present": quantifier_domain_table_present,
        "local_global_transfer_ledger_present": local_global_transfer_table_present,
        "constant_dependency_ledger_present": constant_dependency_table_present,
        "theorem_dependency_consumption_ledger_present": (
            theorem_dependency_consumption_table_present
        ),
        "branch_consistency_ledger_present": branch_consistency_table_present,
        "implementation_route_oracle_ledger_present": (
            implementation_route_oracle_table_present
        ),
        "nonlinear_solver_scale_ledger_present": nonlinear_solver_scale_table_present,
        "local_defect_decomposition_ledger_present": (
            local_defect_decomposition_table_present
        ),
        "theorem_output_scope_ledger_present": theorem_output_scope_table_present,
        "reporting_map_ledger_present": reporting_map_table_present,
    }
    remaining_claim_boundary = {
        "status": "theorem_conditions_retained_not_submission_ready",
        "theorem_assumptions_total": len(theorem_assumptions),
        "submission_satisfied_count": satisfied_assumptions,
        "submission_satisfied_ids": satisfied_assumption_ids,
        "retained_or_open_count": unsatisfied_assumptions,
        "retained_or_open_ids": retained_or_open_assumption_ids,
        "retained_or_open_assumptions": retained_or_open_assumptions,
        "retained_theorem_interface_count": len(retained_theorem_interface_assumptions),
        "retained_theorem_interface_ids": retained_theorem_interface_ids,
        "retained_theorem_interface_assumptions": retained_theorem_interface_assumptions,
        "open_nonpromotion_boundary_count": len(open_nonpromotion_boundary_assumptions),
        "open_nonpromotion_boundary_ids": open_nonpromotion_boundary_ids,
        "open_nonpromotion_boundary_assumptions": open_nonpromotion_boundary_assumptions,
        "close_requirement_count": len(close_requirements),
        "satisfied_close_requirement_ids": satisfied_close_requirement_ids,
        "unsatisfied_close_requirement_ids": unsatisfied_close_requirement_ids,
        "eta_h_solver_policy_evidence_closed": closure_state.get("eta_h_O_h7_solver_policy_evidence"),
        "eta_h_theorem_condition_retained_for_pc3": eta_h_condition_retained_for_pc3,
        "residual_to_error_route_promoted": residual_to_error_route_promoted,
        "source_policy_or_full_tfe_not_promoted": theorem_statement_boundary.get(
            "does_not_promote_source_policy_or_full_tfe"
        ),
        "theorem_reading_guide_present": theorem_reading_guide_present,
        "does_not_change_proof_closure_state": manuscript_traceability.get(
            "does_not_change_proof_closure_state"
        ),
        "manuscript_anchor_map_present": manuscript_anchors["all_label_anchors_present"],
        "reader_facing_manuscript_boundary_present": reader_facing_boundary_present,
        "p7_retained_nonpromotion_boundary_present": p7_nonpromotion_boundary_present,
        "b1_closure_scope_boundary_present": b1_closure_scope_boundary_present,
        "p6_solver_scope_boundary_present": p6_solver_scope_boundary_present,
        "p1p2_compact_tube_boundary_present": p1p2_compact_tube_boundary_present,
        "p3p4_implementation_boundary_present": p3p4_implementation_boundary_present,
        "p5_direct_route_boundary_present": p5_direct_route_boundary_present,
        "proof_causality_table_present": proof_causality_table_present,
        "direct_route_anticircularity_table_present": (
            direct_route_anticircularity_table_present
        ),
        "p_interface_satisfaction_table_present": p_interface_satisfaction_table_present,
        "p7_residual_to_error_table_present": p7_residual_to_error_table_present,
        "theorem_use_rule_present": theorem_use_rule_present,
        "quantifier_domain_table_present": quantifier_domain_table_present,
        "local_global_transfer_table_present": local_global_transfer_table_present,
        "objective_completion_boundary_present": objective_completion_boundary_present,
        "constant_dependency_table_present": constant_dependency_table_present,
        "theorem_dependency_consumption_table_present": (
            theorem_dependency_consumption_table_present
        ),
        "branch_consistency_table_present": branch_consistency_table_present,
        "implementation_route_oracle_table_present": (
            implementation_route_oracle_table_present
        ),
        "nonlinear_solver_scale_table_present": nonlinear_solver_scale_table_present,
        "local_defect_decomposition_table_present": (
            local_defect_decomposition_table_present
        ),
        "theorem_output_scope_table_present": theorem_output_scope_table_present,
        "reporting_map_table_present": reporting_map_table_present,
        "theorem_conclusion_scope_guard_present": theorem_conclusion_scope_guard_present,
        "proof_strength_certificate_present": proof_strength_certificate_present,
        "full_residual_bridge_present": full_residual_bridge_present,
        "route_exclusivity_boundary_present": route_exclusivity_boundary_present,
        "theorem_residual_certificate_exclusivity_present": (
            theorem_residual_certificate_exclusivity_present
        ),
        "intro_proof_hierarchy_present": intro_proof_hierarchy_present,
        "theorem_anchor_table_reference_coverage_present": theorem_anchor_table_coverage[
            "all_references_present_main_and_flat"
        ],
        "theorem_assumption_anchor_map_present": manuscript_anchors[
            "all_theorem_assumption_anchors_present"
        ],
        "theorem_assumption_anchor_ids": manuscript_anchors["theorem_assumption_anchor_ids"],
        "global_submission_boundaries_retained": global_submission_boundaries,
        "reading_rule": (
            "The accepted theorem is traceable only under retained P1, P2, and P3 "
            "theorem interfaces, the separate P6 solver-scale interface, and the "
            "P4 binding convention; P4's proved 96-row non-dynamic row-local "
            "certificate and the satisfied P5 direct dynamic-row route supply "
            "the accepted 132-row residual bridge; P7 is recorded only as the "
            "separate residual-to-error boundary. The direct route and "
            "any future primitive/Taylor route are mutually exclusive same-branch "
            "certificate routes; they are not mixed to lower constants, discharge "
            "P6, or prove a P7 residual-to-error transfer theorem. The theorem invocation consumes exactly one "
            "residual-value certificate; any future primitive/Taylor certificate "
            "must replace the accepted direct certificate by proving a new same-tuple "
            "132-row residual-value bound rather than being appended to it. "
            "This boundary does not promote eta_h evidence, "
            "residual-to-error rows, source-policy rows, or full-TFE replacement."
        ),
    }
    proof_writing_boundary_card = {
        "schema": "proof-writing-boundary-card-v1",
        "status": "conditional_theorem_traceable_direct_pc2_closed_global_boundaries_retained",
        "accepted_theorem_label": theorem_statement_boundary.get("accepted_theorem_label"),
        "accepted_method_order": theorem_statement_boundary.get("accepted_method_order"),
        "accepted_local_defect_order": theorem_statement_boundary.get("accepted_local_defect_order"),
        "manuscript_anchor_map_present": manuscript_anchors["all_label_anchors_present"],
        "theorem_assumption_anchor_ids": manuscript_anchors["theorem_assumption_anchor_ids"],
        "submission_satisfied_assumption_ids": satisfied_assumption_ids,
        "retained_or_open_assumption_ids": retained_or_open_assumption_ids,
        "retained_theorem_interface_ids": retained_theorem_interface_ids,
        "open_nonpromotion_boundary_ids": open_nonpromotion_boundary_ids,
        "satisfied_close_requirement_ids": satisfied_close_requirement_ids,
        "unsatisfied_close_requirement_ids": unsatisfied_close_requirement_ids,
        "direct_pc2_proof_gap_closed": closure_state.get("direct_pc2_proof_gap_closed"),
        "proof_gap_closed_scope": closure_state.get("proof_gap_closed_scope"),
        "not_primitive_162_term_taylor_closure": strict_direct_standard.get(
            "not_primitive_162_term_taylor_closure"
        ),
        "primitive_taylor_route_closed": strict_direct_standard.get(
            "primitive_taylor_route_closed"
        ),
        "actual_taylor_bounds_proved": strict_direct_standard.get(
            "primitive_taylor_actual_bounds_proved"
        ),
        "open_taylor_bound_terms": strict_direct_standard.get(
            "primitive_taylor_open_bound_terms"
        ),
        "terms_with_open_primitive_blockers": strict_direct_standard.get(
            "primitive_taylor_terms_with_open_primitive_blockers"
        ),
        "open_primitive_assumption_count": strict_direct_standard.get(
            "primitive_taylor_open_primitive_count"
        ),
        "open_primitive_count": strict_direct_standard.get(
            "primitive_taylor_open_primitive_count"
        ),
        "stage_residual_O_h7_implementation_defect_proved": closure_state.get(
            "stage_residual_O_h7_implementation_defect_proved"
        ),
        "active_direct_newton_euler_closed_rows": evidence_summary.get(
            "active_direct_newton_euler_closed_rows"
        ),
        "active_direct_newton_euler_open_obligations": evidence_summary.get(
            "active_direct_newton_euler_open_obligations"
        ),
        "symbolic_primitive_route_open_obligations": len(open_newton),
        "dynamic_symbolic_oracle_complete": closure_state.get("dynamic_symbolic_oracle_complete"),
        "eta_h_theorem_condition_retained_for_pc3": eta_h_condition_retained_for_pc3,
        "eta_h_solver_policy_evidence_closed": closure_state.get("eta_h_O_h7_solver_policy_evidence"),
        "fixed_tolerance_runs_are_asymptotic_proof": theorem_statement_boundary.get(
            "fixed_tolerance_runs_are_asymptotic_proof"
        ),
        "residual_to_error_blocking_obligations": evidence_summary.get(
            "residual_to_error_blocking_obligations"
        ),
        "residual_to_error_route_promoted": residual_to_error_route_promoted,
        "source_policy_or_full_tfe_not_promoted": theorem_statement_boundary.get(
            "does_not_promote_source_policy_or_full_tfe"
        ),
        "global_submission_boundaries_retained": global_submission_boundaries,
        "reader_facing_manuscript_boundary_present": reader_facing_boundary_present,
        "p7_retained_nonpromotion_boundary_present": p7_nonpromotion_boundary_present,
        "b1_closure_scope_boundary_present": b1_closure_scope_boundary_present,
        "p6_solver_scope_boundary_present": p6_solver_scope_boundary_present,
        "p1p2_compact_tube_boundary_present": p1p2_compact_tube_boundary_present,
        "p3p4_implementation_boundary_present": p3p4_implementation_boundary_present,
        "p5_direct_route_boundary_present": p5_direct_route_boundary_present,
        "proof_causality_table_present": proof_causality_table_present,
        "direct_route_anticircularity_table_present": (
            direct_route_anticircularity_table_present
        ),
        "p_interface_satisfaction_table_present": p_interface_satisfaction_table_present,
        "p7_residual_to_error_table_present": p7_residual_to_error_table_present,
        "theorem_use_rule_present": theorem_use_rule_present,
        "quantifier_domain_table_present": quantifier_domain_table_present,
        "local_global_transfer_table_present": local_global_transfer_table_present,
        "objective_completion_boundary_present": objective_completion_boundary_present,
        "constant_dependency_table_present": constant_dependency_table_present,
        "theorem_dependency_consumption_table_present": (
            theorem_dependency_consumption_table_present
        ),
        "branch_consistency_table_present": branch_consistency_table_present,
        "implementation_route_oracle_table_present": (
            implementation_route_oracle_table_present
        ),
        "nonlinear_solver_scale_table_present": nonlinear_solver_scale_table_present,
        "local_defect_decomposition_table_present": (
            local_defect_decomposition_table_present
        ),
        "theorem_output_scope_table_present": theorem_output_scope_table_present,
        "reporting_map_table_present": reporting_map_table_present,
        "theorem_conclusion_scope_guard_present": theorem_conclusion_scope_guard_present,
        "proof_strength_certificate_present": proof_strength_certificate_present,
        "full_residual_bridge_present": full_residual_bridge_present,
        "route_exclusivity_boundary_present": route_exclusivity_boundary_present,
        "theorem_residual_certificate_exclusivity_present": (
            theorem_residual_certificate_exclusivity_present
        ),
        "intro_proof_hierarchy_present": intro_proof_hierarchy_present,
        "theorem_reading_guide_present": theorem_reading_guide_present,
        "safe_reader_claim": (
            "conditional order-six theorem under retained P1, P2, and P3 theorem "
            "interfaces, the separate P6 solver-scale interface, and the P4 "
            "binding convention, with P4's proved 96-row non-dynamic row-local "
            "certificate and P5's direct Newton-Euler rows supplying one same-branch "
            "132-row residual bridge; route-exclusivity forbids mixing direct and "
            "primitive/Taylor residual certificates to lower constants, remove P6, "
            "or prove a P7 residual-to-error transfer theorem; the theorem statement itself consumes only one "
            "residual-value certificate, so a future primitive/Taylor certificate "
            "may only replace the accepted direct certificate by proving a new "
            "same-tuple 132-row residual-value bound; P7 remains a separate "
            "output nonclaim/residual-to-error boundary"
        ),
        "forbidden_reader_claims": [
            "unconditional theorem without theorem-domain interfaces",
            "eta_h solver-policy condition closed",
            "fixed-tolerance runs as asymptotic proof",
            "accepted residual-to-error transfer theorem for mechanism rows",
            "source-policy/full-TFE package readiness",
            "mixing direct and primitive-route residual certificates to lower constants, remove P6, or prove a P7 residual-to-error transfer theorem",
        ],
    }
    remaining_claim_boundary.update(table_to_ledger_aliases)
    proof_writing_boundary_card.update(table_to_ledger_aliases)

    result = {
        "schema": "proof-claim-traceability-audit-v1",
        "status": "conditional_proof_claims_traceable_submission_not_ready",
        "read_only_audit": True,
        "submission_ready": False,
        "submission_ready_scope": "traceability_global_proof_boundary_not_narrowed_claim_package_decision",
        "summary": {
            "proof_status": "conditional_direct_route_traceable_submission_not_ready",
            "submission_ready": False,
            "theorem_assumptions_total": len(theorem_assumptions),
            "theorem_assumptions_submission_satisfied": satisfied_assumptions,
            "theorem_assumptions_retained_or_open": unsatisfied_assumptions,
            "theorem_assumptions_retained_theorem_interfaces": len(
                retained_theorem_interface_assumptions
            ),
            "theorem_assumptions_open_nonpromotion_boundaries": len(
                open_nonpromotion_boundary_assumptions
            ),
            "theorem_assumption_submission_satisfied_ids": satisfied_assumption_ids,
            "theorem_assumption_retained_or_open_ids": retained_or_open_assumption_ids,
            "theorem_assumption_retained_theorem_interface_ids": retained_theorem_interface_ids,
            "theorem_assumption_open_nonpromotion_boundary_ids": open_nonpromotion_boundary_ids,
            "close_requirements_total": len(close_requirements),
            "close_requirements_unsatisfied": unsatisfied_close_requirements,
            "close_requirement_satisfied_ids": satisfied_close_requirement_ids,
            "close_requirement_unsatisfied_ids": unsatisfied_close_requirement_ids,
            "remaining_claim_boundary_status": remaining_claim_boundary["status"],
            "theorem_conclusion_scope_guard_present": theorem_conclusion_scope_guard_present,
            "proof_strength_certificate_present": proof_strength_certificate_present,
            "full_residual_bridge_present": full_residual_bridge_present,
            "route_exclusivity_boundary_present": route_exclusivity_boundary_present,
            "theorem_residual_certificate_exclusivity_present": (
                theorem_residual_certificate_exclusivity_present
            ),
            "intro_proof_hierarchy_present": intro_proof_hierarchy_present,
            "manuscript_anchor_label_count": manuscript_anchors["label_anchor_count"],
            "manuscript_anchor_map_present": manuscript_anchors["all_label_anchors_present"],
            "theorem_assumption_anchor_count": manuscript_anchors[
                "theorem_assumption_anchor_count"
            ],
            "theorem_assumption_anchor_map_present": manuscript_anchors[
                "all_theorem_assumption_anchors_present"
            ],
            "direct_pc2_proof_gap_closed": closure_state.get("direct_pc2_proof_gap_closed"),
            "proof_gap_closed_scope": closure_state.get("proof_gap_closed_scope"),
            "stage_residual_O_h7_implementation_defect_proved": closure_state.get(
                "stage_residual_O_h7_implementation_defect_proved"
            ),
            "not_primitive_162_term_taylor_closure": strict_direct_standard.get(
                "not_primitive_162_term_taylor_closure"
            ),
            "primitive_taylor_route_closed": strict_direct_standard.get(
                "primitive_taylor_route_closed"
            ),
            "actual_taylor_bounds_proved": strict_direct_standard.get(
                "primitive_taylor_actual_bounds_proved"
            ),
            "open_taylor_bound_terms": strict_direct_standard.get(
                "primitive_taylor_open_bound_terms"
            ),
            "terms_with_open_primitive_blockers": strict_direct_standard.get(
                "primitive_taylor_terms_with_open_primitive_blockers"
            ),
            "open_primitive_assumption_count": strict_direct_standard.get(
                "primitive_taylor_open_primitive_count"
            ),
            "open_primitive_count": strict_direct_standard.get(
                "primitive_taylor_open_primitive_count"
            ),
            "dynamic_symbolic_oracle_complete": closure_state.get("dynamic_symbolic_oracle_complete"),
            "active_direct_newton_euler_open_obligations": evidence_summary.get(
                "active_direct_newton_euler_open_obligations"
            ),
            "symbolic_primitive_route_open_obligations": len(open_newton),
            "eta_h_O_h7_solver_policy_evidence": closure_state.get("eta_h_O_h7_solver_policy_evidence"),
            "eta_h_theorem_condition_retained_for_pc3": eta_h_condition_retained_for_pc3,
            "residual_to_error_blocking_obligations": evidence_summary.get(
                "residual_to_error_blocking_obligations"
            ),
            "residual_to_error_route_promoted": residual_to_error_route_promoted,
            "global_submission_boundaries_retained": global_submission_boundaries,
            "proof_writing_boundary_card_status": proof_writing_boundary_card["status"],
            "proof_writing_boundary_card_safe_reader_claim": (
                proof_writing_boundary_card["safe_reader_claim"]
            ),
            "reader_facing_proof_claim_boundary_present": reader_facing_boundary_present,
            "p7_retained_nonpromotion_boundary_present": p7_nonpromotion_boundary_present,
            "b1_closure_scope_boundary_present": b1_closure_scope_boundary_present,
            "p6_solver_scope_boundary_present": p6_solver_scope_boundary_present,
            "p1p2_compact_tube_boundary_present": p1p2_compact_tube_boundary_present,
            "p3p4_implementation_boundary_present": p3p4_implementation_boundary_present,
            "p5_direct_route_boundary_present": p5_direct_route_boundary_present,
            "proof_causality_table_present": proof_causality_table_present,
            "direct_route_anticircularity_table_present": (
                direct_route_anticircularity_table_present
            ),
            "p_interface_satisfaction_table_present": p_interface_satisfaction_table_present,
            "p7_residual_to_error_table_present": p7_residual_to_error_table_present,
            "theorem_use_rule_present": theorem_use_rule_present,
            "quantifier_domain_table_present": quantifier_domain_table_present,
            "local_global_transfer_table_present": local_global_transfer_table_present,
            "objective_completion_boundary_present": objective_completion_boundary_present,
            "constant_dependency_table_present": constant_dependency_table_present,
            "theorem_dependency_consumption_table_present": (
                theorem_dependency_consumption_table_present
            ),
            "branch_consistency_table_present": branch_consistency_table_present,
            "implementation_route_oracle_table_present": (
                implementation_route_oracle_table_present
            ),
            "nonlinear_solver_scale_table_present": nonlinear_solver_scale_table_present,
            "local_defect_decomposition_table_present": (
                local_defect_decomposition_table_present
            ),
            "theorem_output_scope_table_present": theorem_output_scope_table_present,
            "reporting_map_table_present": reporting_map_table_present,
            "theorem_conclusion_scope_guard_present": theorem_conclusion_scope_guard_present,
            "proof_strength_certificate_present": proof_strength_certificate_present,
            "full_residual_bridge_present": full_residual_bridge_present,
            "route_exclusivity_boundary_present": route_exclusivity_boundary_present,
            "theorem_residual_certificate_exclusivity_present": (
                theorem_residual_certificate_exclusivity_present
            ),
            "intro_proof_hierarchy_present": intro_proof_hierarchy_present,
            "theorem_anchor_table_reference_coverage_present": theorem_anchor_table_coverage[
                "all_references_present_main_and_flat"
            ],
        },
        "source_files": {
            "main_tex": "main_cmame.tex",
            "flat_tex": "cmame_submission_flat/main_cmame_submission.tex",
            "proof_closure_manifest": "PROOF_CLOSURE_MANIFEST.json",
            "proof_contract_gate": "CMAME_PROOF_CONTRACT_GATE.json",
            "proof_evidence_matrix": "PROOF_EVIDENCE_MATRIX.md",
            "claim_boundary": "CLAIM_BOUNDARY.json",
            "blocker_gate": "CMAME_BLOCKER_CLOSURE_GATE.json",
            "newton_euler_symbolic_target_audit": "NEWTON_EULER_SYMBOLIC_TARGET_AUDIT.json",
            "newton_euler_symbolic_defect_certificate": "NEWTON_EULER_SYMBOLIC_DEFECT_CERTIFICATE.json",
        },
        "main_source": main_source_checks,
        "flat_source": flat_source_checks,
        "reader_facing_proof_claim_boundary": reader_facing_boundary,
        "theorem_conclusion_scope_guard": {
            "tokens": THEOREM_CONCLUSION_SCOPE_GUARD_TOKENS,
            "checks": theorem_conclusion_scope_guard,
            "all_tokens_present": theorem_conclusion_scope_guard_present,
        },
        "proof_strength_certificate": {
            "tokens": PROOF_STRENGTH_CERTIFICATE_TOKENS,
            "checks": proof_strength_certificate,
            "all_tokens_present": proof_strength_certificate_present,
        },
        "full_residual_bridge": {
            "tokens": FULL_RESIDUAL_BRIDGE_TOKENS,
            "checks": full_residual_bridge,
            "all_tokens_present": full_residual_bridge_present,
        },
        "route_exclusivity_boundary": {
            "tex_tokens": ROUTE_EXCLUSIVITY_TEX_TOKENS,
            "pdf_text_tokens": ROUTE_EXCLUSIVITY_PDF_TEXT_TOKENS,
            "checks": route_exclusivity_boundary,
            "all_tokens_present": route_exclusivity_boundary_present,
            "nonmixing_semantics": (
                "The accepted direct residual-value certificate and any separate "
                "primitive/Taylor certificate must be used as separate same-branch "
                "proof routes. The audit records presence only; it does not lower "
                "constants, remove P6, prove a P7 residual-to-error transfer theorem, or prove the primitive route."
            ),
        },
        "theorem_residual_certificate_exclusivity": {
            "tex_tokens": THEOREM_RESIDUAL_CERTIFICATE_EXCLUSIVITY_TEX_TOKENS,
            "pdf_text_tokens": THEOREM_RESIDUAL_CERTIFICATE_EXCLUSIVITY_PDF_TEXT_TOKENS,
            "checks": theorem_residual_certificate_exclusivity,
            "all_tokens_present": theorem_residual_certificate_exclusivity_present,
            "nonmixing_semantics": (
                "The theorem statement itself consumes only one residual-value "
                "certificate. A future primitive/Taylor certificate may replace "
                "the accepted direct certificate only by proving a new same-tuple "
                "132-row residual-value bound; it may not be appended to lower "
                "constants, remove P6, prove a P7 residual-to-error transfer theorem, or prove the primitive route."
            ),
        },
        "intro_proof_hierarchy": {
            "tokens": INTRO_PROOF_HIERARCHY_TOKENS,
            "checks": intro_proof_hierarchy,
            "all_tokens_present": intro_proof_hierarchy_present,
        },
        "p7_retained_nonpromotion_boundary": {
            "tokens": p7_nonpromotion_boundary_tokens,
            "checks": p7_nonpromotion_boundary,
            "all_tokens_present": p7_nonpromotion_boundary_present,
        },
        "b1_closure_scope_boundary": {
            "tokens": b1_closure_scope_tokens,
            "checks": b1_closure_scope_boundary,
            "all_tokens_present": b1_closure_scope_boundary_present,
        },
        "p6_solver_scope_boundary": {
            "tokens": p6_solver_scope_tokens,
            "pdf_reader_tokens": p6_solver_scope_pdf_reader_tokens,
            "checks": p6_solver_scope_boundary,
            "all_tokens_present": p6_solver_scope_boundary_present,
            "tex_all_tokens_present": p6_solver_scope_tex_present,
            "pdf_reader_tokens_present": p6_solver_scope_pdf_reader_present,
        },
        "p1p2_compact_tube_boundary": {
            "tokens": p1p2_compact_tube_tokens,
            "pdf_reader_tokens": p1p2_compact_tube_pdf_reader_tokens,
            "checks": p1p2_compact_tube_boundary,
            "all_tokens_present": p1p2_compact_tube_boundary_present,
            "tex_all_tokens_present": p1p2_compact_tube_tex_present,
            "pdf_reader_tokens_present": p1p2_compact_tube_pdf_reader_present,
        },
        "p3p4_implementation_boundary": {
            "tokens": p3p4_implementation_boundary_tokens,
            "checks": p3p4_implementation_boundary,
            "all_tokens_present": p3p4_implementation_boundary_present,
        },
        "p5_direct_route_boundary": {
            "tokens": p5_direct_route_tokens,
            "checks": p5_direct_route_boundary,
            "all_tokens_present": p5_direct_route_boundary_present,
        },
        "proof_causality_table": {
            "tokens": proof_causality_table_tokens,
            "checks": proof_causality_table,
            "all_tokens_present": proof_causality_table_present,
        },
        "direct_route_anticircularity_table": {
            "tokens": direct_route_anticircularity_table_tokens,
            "checks": direct_route_anticircularity_table,
            "all_tokens_present": direct_route_anticircularity_table_present,
        },
        "p_interface_satisfaction_table": {
            "tokens": p_interface_satisfaction_tokens,
            "checks": p_interface_satisfaction_table,
            "all_tokens_present": p_interface_satisfaction_table_present,
        },
        "p7_residual_to_error_table": {
            "tokens": p7_residual_to_error_table_tokens,
            "checks": p7_residual_to_error_table,
            "all_tokens_present": p7_residual_to_error_table_present,
        },
        "theorem_use_rule": {
            "tokens": theorem_use_rule_tokens,
            "checks": theorem_use_rule,
            "check_semantics": (
                "The booleans under checks are normalized token-presence checks in "
                "main/flat TeX and extracted PDF text. A true value means the boundary "
                "phrase is present in that artifact; it does not promote residual-to-error "
                "transfer, solver-policy theorem, successful Newton logs, source-policy "
                "readiness, or full-TFE readiness to accepted theorem inputs."
            ),
            "nonpromotion_phrase_tokens": [
                "residual-to-error transfer theorem",
                "solver-policy theorem",
                "successful Newton logs",
                "source-policy/full-TFE readiness",
            ],
            "all_tokens_present": theorem_use_rule_present,
        },
        "quantifier_domain_table": {
            "tokens": quantifier_domain_table_tokens,
            "checks": quantifier_domain_table,
            "all_tokens_present": quantifier_domain_table_present,
        },
        "local_global_transfer_table": {
            "tokens": local_global_transfer_table_tokens,
            "checks": local_global_transfer_table,
            "all_tokens_present": local_global_transfer_table_present,
        },
        "objective_completion_boundary": {
            "tokens": objective_completion_boundary_tokens,
            "checks": objective_completion_boundary,
            "all_tokens_present": objective_completion_boundary_present,
        },
        "constant_dependency_table": {
            "tokens": constant_dependency_table_tokens,
            "checks": constant_dependency_table,
            "all_tokens_present": constant_dependency_table_present,
        },
        "theorem_dependency_consumption_table": {
            "tokens": theorem_dependency_consumption_table_tokens,
            "checks": theorem_dependency_consumption_table,
            "all_tokens_present": theorem_dependency_consumption_table_present,
        },
        "branch_consistency_table": {
            "tokens": branch_consistency_table_tokens,
            "checks": branch_consistency_table,
            "all_tokens_present": branch_consistency_table_present,
        },
        "implementation_route_oracle_table": {
            "tokens": implementation_route_oracle_table_tokens,
            "checks": implementation_route_oracle_table,
            "all_tokens_present": implementation_route_oracle_table_present,
        },
        "nonlinear_solver_scale_table": {
            "tokens": nonlinear_solver_scale_table_tokens,
            "checks": nonlinear_solver_scale_table,
            "all_tokens_present": nonlinear_solver_scale_table_present,
        },
        "local_defect_decomposition_table": {
            "tokens": local_defect_decomposition_table_tokens,
            "checks": local_defect_decomposition_table,
            "all_tokens_present": local_defect_decomposition_table_present,
        },
        "theorem_output_scope_table": {
            "tokens": theorem_output_scope_table_tokens,
            "checks": theorem_output_scope_table,
            "all_tokens_present": theorem_output_scope_table_present,
        },
        "reporting_map_table": {
            "tokens": reporting_map_table_tokens,
            "checks": reporting_map_table,
            "all_tokens_present": reporting_map_table_present,
        },
        "theorem_anchor_table_reference_coverage": theorem_anchor_table_coverage,
        "manuscript_anchor_map": manuscript_anchors,
        "accepted_theorem": proof_closure.get("accepted_theorem"),
        "manuscript_theorem_traceability": {
            "source_manifest": "PROOF_CLOSURE_MANIFEST.json",
            "source_contract_gate": "CMAME_PROOF_CONTRACT_GATE.json",
            "proof_closure_status": proof_closure.get("status"),
            "accepted_theorem_label": theorem_statement_boundary.get("accepted_theorem_label"),
            "accepted_method_order": theorem_statement_boundary.get("accepted_method_order"),
            "accepted_local_defect_order": theorem_statement_boundary.get("accepted_local_defect_order"),
            "theorem_statement_labels_present": theorem_statement_boundary.get(
                "all_required_labels_present_main_and_flat"
            ),
            "conditional_theorem_boundary_present": theorem_statement_boundary.get(
                "conditional_theorem_boundary_present_main_and_flat"
            ),
            "theorem_reading_guide_present": theorem_reading_guide_present,
            "conditional_proof_claims_mapped_to_manuscript": traceability_claims_mapped,
            "proof_dependency_graph_present": manuscript_traceability.get(
                "proof_dependency_graph_present_main_and_flat"
            ),
            "proof_traceability_table_present": manuscript_traceability.get(
                "proof_traceability_table_present_main_and_flat"
            ),
            "dynamic_proof_closure_matrix_present": manuscript_traceability.get(
                "dynamic_proof_closure_matrix_present_main_and_flat"
            ),
            "primitive_lane_boundary_present": manuscript_traceability.get(
                "primitive_lane_boundary_present_main_and_flat"
            ),
            "theorem_scope_references_d5_primitive_blocker_ledger": (
                main_source_checks["theorem_scope_references_d5_primitive_blocker_ledger"]
                and flat_source_checks["theorem_scope_references_d5_primitive_blocker_ledger"]
            ),
            "theorem_scope_preserves_primitive_pc2_closed_false": (
                main_source_checks["theorem_scope_preserves_primitive_pc2_closed_false"]
                and flat_source_checks["theorem_scope_preserves_primitive_pc2_closed_false"]
            ),
            "theorem_scope_primitive_boundary_present": (
                main_source_checks["theorem_scope_primitive_boundary_present"]
                and flat_source_checks["theorem_scope_primitive_boundary_present"]
            ),
            "taylor_finite_implication_present": (
                main_source_checks["taylor_finite_implication_present"]
                and flat_source_checks["taylor_finite_implication_present"]
            ),
            "taylor_finite_implication_main_flat": (
                main_source_checks["taylor_finite_implication_present"],
                flat_source_checks["taylor_finite_implication_present"],
            ),
            "route_exclusivity_boundary_present": route_exclusivity_boundary_present,
            "theorem_residual_certificate_exclusivity_present": (
                theorem_residual_certificate_exclusivity_present
            ),
            "residual_nonpromotion_present": manuscript_traceability.get(
                "residual_to_error_nonpromotion_present_main_and_flat"
            ),
            "reader_facing_manuscript_boundary_present": reader_facing_boundary_present,
            "eta_h_theorem_condition_retained": theorem_statement_boundary.get(
                "eta_h_theorem_condition_retained"
            ),
            "eta_h_solver_policy_evidence_closed": theorem_statement_boundary.get(
                "eta_h_solver_policy_evidence_closed"
            ),
            "fixed_tolerance_runs_are_asymptotic_proof": theorem_statement_boundary.get(
                "fixed_tolerance_runs_are_asymptotic_proof"
            ),
            "residual_to_error_not_promoted": theorem_statement_boundary.get(
                "does_not_promote_residual_to_error"
            ),
            "p7_retained_nonpromotion_boundary_present": p7_nonpromotion_boundary_present,
            "b1_closure_scope_boundary_present": b1_closure_scope_boundary_present,
            "p6_solver_scope_boundary_present": p6_solver_scope_boundary_present,
            "p1p2_compact_tube_boundary_present": p1p2_compact_tube_boundary_present,
            "p3p4_implementation_boundary_present": p3p4_implementation_boundary_present,
            "p5_direct_route_boundary_present": p5_direct_route_boundary_present,
            "proof_causality_table_present": proof_causality_table_present,
            "direct_route_anticircularity_table_present": (
                direct_route_anticircularity_table_present
            ),
            "p_interface_satisfaction_table_present": p_interface_satisfaction_table_present,
            "p7_residual_to_error_table_present": p7_residual_to_error_table_present,
            "theorem_use_rule_present": theorem_use_rule_present,
            "quantifier_domain_table_present": quantifier_domain_table_present,
            "local_global_transfer_table_present": local_global_transfer_table_present,
            "objective_completion_boundary_present": objective_completion_boundary_present,
            "constant_dependency_table_present": constant_dependency_table_present,
            "theorem_dependency_consumption_table_present": (
                theorem_dependency_consumption_table_present
            ),
            "branch_consistency_table_present": branch_consistency_table_present,
            "implementation_route_oracle_table_present": (
                implementation_route_oracle_table_present
            ),
            "nonlinear_solver_scale_table_present": nonlinear_solver_scale_table_present,
            "local_defect_decomposition_table_present": (
                local_defect_decomposition_table_present
            ),
            "theorem_output_scope_table_present": theorem_output_scope_table_present,
            "reporting_map_table_present": reporting_map_table_present,
            "theorem_conclusion_scope_guard_present": theorem_conclusion_scope_guard_present,
            "proof_strength_certificate_present": proof_strength_certificate_present,
            "full_residual_bridge_present": full_residual_bridge_present,
            "route_exclusivity_boundary_present": route_exclusivity_boundary_present,
            "intro_proof_hierarchy_present": intro_proof_hierarchy_present,
            "source_policy_or_full_tfe_not_promoted": theorem_statement_boundary.get(
                "does_not_promote_source_policy_or_full_tfe"
            ),
            "does_not_change_proof_closure_state": manuscript_traceability.get(
                "does_not_change_proof_closure_state"
            ),
            "traceability_audit_role": (
                "proof-claim traceability audit maps the accepted theorem label, proof dependencies, "
                "and proof tables to manuscript text without closing eta_h solver-policy "
                "theorem, residual-to-error, or source-policy/full-TFE gates"
            ),
        },
        "claim_boundary": {
            "accepted_method": primary_claim.get("accepted_method"),
            "accepted_method_order": primary_claim.get("method_order_claim"),
            "full_tfe_stage_replacement": claim_boundary.get("full_tfe_stage_replacement"),
            "submission_ready": False,
        },
        "proof_closure_state": closure_state,
        "solver_state": solver_state,
        "proof_mode": proof_closure.get("proof_mode"),
        "proof_contract_mode": proof_contract.get("proof_mode"),
        "theorem_assumption_count": len(theorem_assumptions),
        "satisfied_theorem_assumption_count": satisfied_assumptions,
        "unsatisfied_theorem_assumption_count": unsatisfied_assumptions,
        "theorem_assumption_submission_satisfied_ids": satisfied_assumption_ids,
        "theorem_assumption_retained_or_open_ids": retained_or_open_assumption_ids,
        "theorem_assumptions": theorem_assumptions,
        "remaining_claim_boundary": remaining_claim_boundary,
        "proof_writing_boundary_card": proof_writing_boundary_card,
        "close_requirement_count": len(close_requirements),
        "satisfied_close_requirement_count": satisfied_close_requirements,
        "unsatisfied_close_requirement_count": unsatisfied_close_requirements,
        "satisfied_close_requirement_ids": satisfied_close_requirement_ids,
        "unsatisfied_close_requirement_ids": unsatisfied_close_requirement_ids,
        "close_requirements": close_requirements,
        "newton_euler_open_obligation_count": len(open_newton),
        "newton_euler_closed_obligation_count": len(closed_newton),
        "newton_euler_closed_obligation_ids": [item.get("id") for item in closed_newton],
        "residual_to_error_blocking_obligations": evidence_summary.get("residual_to_error_blocking_obligations"),
        "certified_non_dynamic_rows": evidence_summary.get("certified_non_dynamic_rows"),
        "active_direct_newton_euler_closed_rows": evidence_summary.get("active_direct_newton_euler_closed_rows"),
        "active_direct_newton_euler_open_rows": evidence_summary.get("active_direct_newton_euler_open_rows"),
        "active_direct_newton_euler_open_obligations": evidence_summary.get(
            "active_direct_newton_euler_open_obligations"
        ),
        "open_dynamic_rows": evidence_summary.get("open_dynamic_rows"),
        "open_dynamic_rows_scope": evidence_summary.get("open_dynamic_rows_scope"),
        "formula_row_ad_jacobian_probe_count": evidence_summary.get("formula_row_ad_jacobian_probe_count"),
        "formula_row_ad_jacobian_max_mismatch": evidence_summary.get("formula_row_ad_jacobian_max_mismatch"),
        "proof_evidence_matrix_mentions_open_symbolic_oracle": (
            "D5 dynamic symbolic defect proof remains open" in proof_evidence
        ),
        "dynamic_proof_closure_matrix_status": "present_direct_substitution_closure_inputs",
        "dynamic_proof_closure_matrix_present": (
            main_source_checks["dynamic_proof_closure_matrix_present"]
            and flat_source_checks["dynamic_proof_closure_matrix_present"]
        ),
        "newton_euler_row_target_map_present": (
            main_source_checks["newton_euler_row_target_map_present"]
            and flat_source_checks["newton_euler_row_target_map_present"]
        ),
        "newton_euler_symbolic_target_schema": newton_euler_symbolic_target.get("schema"),
        "newton_euler_symbolic_target_status": newton_euler_symbolic_target.get("status"),
        "newton_euler_symbolic_target_rows": newton_euler_symbolic_target.get("row_count"),
        "newton_euler_symbolic_target_translational_rows": newton_euler_symbolic_target.get(
            "translational_row_count"
        ),
        "newton_euler_symbolic_target_rotational_rows": newton_euler_symbolic_target.get("rotational_row_count"),
        "newton_euler_symbolic_target_inventory_complete": newton_euler_symbolic_target.get(
            "closure_boundary", {}
        ).get("symbolic_target_inventory_complete"),
        "newton_euler_obligation_coverage_matrix_complete": newton_euler_coverage.get(
            "coverage_matrix_complete"
        ),
        "newton_euler_row_obligation_links": newton_euler_coverage.get("row_obligation_link_count"),
        "newton_euler_rows_with_complete_obligation_sets": newton_euler_coverage.get(
            "rows_with_complete_obligation_sets"
        ),
        "newton_euler_obligations_with_target_rows": newton_euler_coverage.get("obligations_with_target_rows"),
        "newton_euler_obligation_coverage_proof_closure_advanced": newton_euler_coverage.get(
            "proof_closure_advanced"
        ),
        "newton_euler_symbolic_defect_certificate_complete": newton_euler_symbolic_defect_certificate.get(
            "certificate_complete"
        ),
        "newton_euler_runtime_expression_structure_checked": newton_euler_defect_summary.get(
            "runtime_expression_structure_checked"
        ),
        "newton_euler_runtime_expression_structure_checked_rows": newton_euler_defect_summary.get(
            "runtime_expression_structure_checked_rows"
        ),
        "newton_euler_runtime_expression_structure_translational_rows": newton_euler_defect_summary.get(
            "runtime_expression_structure_translational_rows"
        ),
        "newton_euler_runtime_expression_structure_rotational_rows": newton_euler_defect_summary.get(
            "runtime_expression_structure_rotational_rows"
        ),
        "newton_euler_runtime_template_instantiation_checked": newton_euler_defect_summary.get(
            "runtime_template_instantiation_checked"
        ),
        "newton_euler_runtime_template_instantiation_checked_rows": newton_euler_defect_summary.get(
            "runtime_template_instantiation_checked_rows"
        ),
        "readiness_boundary": {
            "narrowed_claim_b4_b6_b7_statuses": blocker_statuses(blocker_gate, ["B4", "B6", "B7"]),
            "traceability_audit_scope": "proof_claim_traceability_and_B1_B3_boundary",
            "global_submission_boundaries_retained": global_submission_boundaries,
        },
        "remaining_gate_scope": {
            "narrowed_claim_b4_b6_b7_statuses": blocker_statuses(blocker_gate, ["B4", "B6", "B7"]),
            "b4_b6_b7_closed_elsewhere_under_narrowed_claim": (
                blocker_statuses(blocker_gate, ["B4", "B6", "B7"])
                == {"B4": "closed", "B6": "closed", "B7": "closed"}
            ),
            "proof_claims_traceable_under_conditional_scope": traceability_claims_mapped,
            "direct_pc2_proof_gap_closed": closure_state.get("direct_pc2_proof_gap_closed"),
            "proof_gap_closed_scope": closure_state.get("proof_gap_closed_scope"),
            "direct_residual_bridge_route_satisfied": proof_closure_remaining.get(
                "direct_residual_bridge_route_satisfied"
            ),
            "not_primitive_162_term_taylor_closure": strict_direct_standard.get(
                "not_primitive_162_term_taylor_closure"
            ),
            "primitive_taylor_route_closed": strict_direct_standard.get(
                "primitive_taylor_route_closed"
            ),
            "actual_taylor_bounds_proved": strict_direct_standard.get(
                "primitive_taylor_actual_bounds_proved"
            ),
            "open_taylor_bound_terms": strict_direct_standard.get(
                "primitive_taylor_open_bound_terms"
            ),
            "terms_with_open_primitive_blockers": strict_direct_standard.get(
                "primitive_taylor_terms_with_open_primitive_blockers"
            ),
            "open_primitive_assumption_count": strict_direct_standard.get(
                "primitive_taylor_open_primitive_count"
            ),
            "open_primitive_count": strict_direct_standard.get(
                "primitive_taylor_open_primitive_count"
            ),
            "dynamic_symbolic_oracle_complete": closure_state.get("dynamic_symbolic_oracle_complete"),
            "eta_h_O_h7_solver_policy_evidence": closure_state.get("eta_h_O_h7_solver_policy_evidence"),
            "eta_h_theorem_condition_retained_for_pc3": eta_h_condition_retained_for_pc3,
            "accepted_residual_to_error_theorem": closure_state.get("accepted_residual_to_error_theorem"),
            "residual_to_error_blocking_obligations": evidence_summary.get(
                "residual_to_error_blocking_obligations"
            ),
            "residual_to_error_route_promoted": residual_to_error_route_promoted,
            "active_direct_newton_euler_open_obligations": evidence_summary.get(
                "active_direct_newton_euler_open_obligations"
            ),
            "symbolic_primitive_route_open_obligations": len(open_newton),
            "global_submission_boundaries_retained": global_submission_boundaries,
            "route_exclusivity_boundary_present": route_exclusivity_boundary_present,
            "theorem_residual_certificate_exclusivity_present": (
                theorem_residual_certificate_exclusivity_present
            ),
        },
        "forbidden_now": proof_closure.get("claim_policy", {}).get("forbidden_now", []),
        "allowed_now": proof_closure.get("claim_policy", {}).get("allowed_now", []),
    }
    result["summary"].update(table_to_ledger_aliases)
    result["manuscript_theorem_traceability"].update(table_to_ledger_aliases)

    with OUT_JSON.open("w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, sort_keys=True)
        handle.write("\n")

    lines = [
        "# Proof Claim Traceability Audit",
        "",
        "Status: **conditional proof claims traceable; global proof-package submission not ready**.",
        "Here `submission_ready=false` is scoped to traceability/global proof-package readiness,",
        "not to the separate narrowed-claim package decision.",
        "",
        f"- Main proof labels present: `{result['main_source']['all_labels_present']}`.",
        f"- Flat proof labels present: `{result['flat_source']['all_labels_present']}`.",
        f"- Proof object counts match expected: `{result['main_source']['proof_object_counts_match_expected']}`.",
        f"- Theorem labels/boundary/mapped: `{result['manuscript_theorem_traceability']['theorem_statement_labels_present']}/{result['manuscript_theorem_traceability']['conditional_theorem_boundary_present']}/{result['manuscript_theorem_traceability']['conditional_proof_claims_mapped_to_manuscript']}`.",
        f"- Theorem reading guide present: `{result['manuscript_theorem_traceability']['theorem_reading_guide_present']}`.",
        f"- Proof dependency/traceability/dynamic matrix: `{result['manuscript_theorem_traceability']['proof_dependency_graph_present']}/{result['manuscript_theorem_traceability']['proof_traceability_table_present']}/{result['manuscript_theorem_traceability']['dynamic_proof_closure_matrix_present']}`.",
        f"- Primitive-route and residual scope boundaries: `{result['manuscript_theorem_traceability']['primitive_lane_boundary_present']}/{result['manuscript_theorem_traceability']['residual_nonpromotion_present']}`.",
        f"- Theorem-scope primitive blocker ledger/pc2-open boundary: `{result['manuscript_theorem_traceability']['theorem_scope_references_d5_primitive_blocker_ledger']}/{result['manuscript_theorem_traceability']['theorem_scope_preserves_primitive_pc2_closed_false']}`.",
        f"- Taylor finite-implication/nonclosure statements main/flat: `{result['manuscript_theorem_traceability']['taylor_finite_implication_main_flat'][0]}/{result['manuscript_theorem_traceability']['taylor_finite_implication_main_flat'][1]}`.",
        f"- Eta condition/closure and fixed-tolerance proof: `{result['manuscript_theorem_traceability']['eta_h_theorem_condition_retained']}/{result['manuscript_theorem_traceability']['eta_h_solver_policy_evidence_closed']}/{result['manuscript_theorem_traceability']['fixed_tolerance_runs_are_asymptotic_proof']}`.",
        f"- Residual/source-policy-full-TFE not promoted: `{result['manuscript_theorem_traceability']['residual_to_error_not_promoted']}/{result['manuscript_theorem_traceability']['source_policy_or_full_tfe_not_promoted']}`; no-state-change `{result['manuscript_theorem_traceability']['does_not_change_proof_closure_state']}`.",
        f"- Newton-Euler obligation IDs present: `{result['main_source']['all_newton_euler_ids_present']}`.",
        f"- Newton-Euler row-level target map present: `{result['newton_euler_row_target_map_present']}`.",
        f"- Newton-Euler symbolic target rows: `{result['newton_euler_symbolic_target_rows']}` total, `{result['newton_euler_symbolic_target_translational_rows']}/{result['newton_euler_symbolic_target_rotational_rows']}` translational/rotational.",
        f"- Newton-Euler symbolic target inventory complete: `{result['newton_euler_symbolic_target_inventory_complete']}`.",
        f"- Newton-Euler obligation coverage matrix complete: `{result['newton_euler_obligation_coverage_matrix_complete']}`.",
        f"- Newton-Euler row-obligation links: `{result['newton_euler_row_obligation_links']}`.",
        f"- Newton-Euler rows with complete obligation sets: `{result['newton_euler_rows_with_complete_obligation_sets']}`.",
        f"- Newton-Euler obligation coverage does not close the primitive symbolic-defect route: `{not result['newton_euler_obligation_coverage_proof_closure_advanced']}`; active direct PC2 residual-bridge slot is closed separately: `{result['proof_closure_state']['direct_pc2_proof_gap_closed']}`.",
        f"- Newton-Euler symbolic defect certificate complete: `{result['newton_euler_symbolic_defect_certificate_complete']}`.",
        f"- Newton-Euler runtime expression structure checked/rows: `{result['newton_euler_runtime_expression_structure_checked']}` / `{result['newton_euler_runtime_expression_structure_checked_rows']}`.",
        f"- Newton-Euler runtime expression structure translational/rotational rows: `{result['newton_euler_runtime_expression_structure_translational_rows']}` / `{result['newton_euler_runtime_expression_structure_rotational_rows']}`.",
        f"- Newton-Euler runtime template instantiation checked/rows: `{result['newton_euler_runtime_template_instantiation_checked']}` / `{result['newton_euler_runtime_template_instantiation_checked_rows']}`.",
        f"- Dynamic-row residual-identity table present: `{result['dynamic_proof_closure_matrix_present']}`.",
        f"- Dynamic-row residual-identity table status: `{result['dynamic_proof_closure_matrix_status']}`.",
        "- P-interface partition: P1, P2, and P3 are retained theorem interfaces; P6 is the retained solver-scale interface; P4's binding convention is retained while its 96-row non-dynamic row-local certificate is proved; P5 direct-route discharged; P7 output nonclaim/residual-to-error boundary.",
        "- Reader-facing theorem-interface split: theorem interfaces `P1--P6`; P7 is an output nonclaim/residual-to-error boundary anchor, not a theorem premise.",
        f"- Remaining claim boundary: `{result['remaining_claim_boundary']['status']}`; satisfied IDs `{','.join(result['remaining_claim_boundary']['submission_satisfied_ids'])}`; retained theorem-interface IDs `{','.join(result['remaining_claim_boundary']['retained_theorem_interface_ids'])}`; open output-boundary IDs `{','.join(result['remaining_claim_boundary']['open_nonpromotion_boundary_ids'])}`.",
        f"- Remaining claim boundary no-promotion flags: eta closure `{result['remaining_claim_boundary']['eta_h_solver_policy_evidence_closed']}`; residual route promoted `{result['remaining_claim_boundary']['residual_to_error_route_promoted']}`; source-policy/full-TFE not promoted `{result['remaining_claim_boundary']['source_policy_or_full_tfe_not_promoted']}`.",
        f"- P7 output nonclaim/residual-to-error boundary in manuscript: `{result['remaining_claim_boundary']['p7_retained_nonpromotion_boundary_present']}`.",
        f"- B1 closure-scope boundary in main/flat TeX and PDF text: `{result['remaining_claim_boundary']['b1_closure_scope_boundary_present']}`.",
        f"- P6 solver-scope boundary in source TeX plus PDF reader text: `{result['remaining_claim_boundary']['p6_solver_scope_boundary_present']}`.",
        f"- P1/P2 compact-tube boundary in source TeX plus PDF reader text: `{result['remaining_claim_boundary']['p1p2_compact_tube_boundary_present']}`.",
        f"- P3/P4 implementation-defect boundary in main/flat TeX and PDF text: `{result['remaining_claim_boundary']['p3p4_implementation_boundary_present']}`.",
        f"- P5 direct-route boundary in main/flat TeX and PDF text: `{result['remaining_claim_boundary']['p5_direct_route_boundary_present']}`.",
        f"- Proof causality in main/flat TeX and PDF text: `{result['remaining_claim_boundary']['proof_causality_table_present']}`.",
        f"- Direct-route anti-circularity table in main/flat TeX and PDF text: `{result['remaining_claim_boundary']['direct_route_anticircularity_table_present']}`.",
        f"- Assumptions and theorem scope in main/flat TeX and PDF text: `{result['remaining_claim_boundary']['p_interface_satisfaction_table_present']}`.",
        f"- Residual-to-error boundary in main/flat TeX and PDF text: `{result['remaining_claim_boundary']['p7_residual_to_error_table_present']}`.",
        f"- Auxiliary-evidence scope in main/flat TeX and PDF text: `{result['remaining_claim_boundary']['theorem_use_rule_present']}`.",
        "- Theorem-use rule `true` values are token-presence checks only; they do not promote residual-to-error transfer, solver-policy theorem, Newton logs, source-policy readiness, or full-TFE readiness to accepted theorem inputs.",
        f"- Quantifier/domain table in main/flat TeX and PDF text: `{result['remaining_claim_boundary']['quantifier_domain_table_present']}`.",
        f"- Local-to-global transfer table in main/flat TeX and PDF text: `{result['remaining_claim_boundary']['local_global_transfer_table_present']}`.",
        f"- Objective-completion boundary in main/flat TeX and PDF text: `{result['remaining_claim_boundary']['objective_completion_boundary_present']}`.",
        f"- Constant-dependency table in main/flat TeX and PDF text: `{result['remaining_claim_boundary']['constant_dependency_table_present']}`.",
        f"- Theorem input-output flow in main/flat TeX and PDF text: `{result['remaining_claim_boundary']['theorem_dependency_consumption_table_present']}`.",
        f"- Accepted-branch consistency ledger in main/flat TeX and PDF text: `{result['remaining_claim_boundary']['branch_consistency_table_present']}`.",
        f"- Implementation-route/certificate separation table in main/flat TeX and PDF text: `{result['remaining_claim_boundary']['implementation_route_oracle_table_present']}`.",
        f"- Nonlinear-solver scale conditions in main/flat TeX and PDF text: `{result['remaining_claim_boundary']['nonlinear_solver_scale_table_present']}`.",
        f"- Local-defect decomposition ledger in main/flat TeX and PDF text: `{result['remaining_claim_boundary']['local_defect_decomposition_table_present']}`.",
        f"- Theorem output scope table in main/flat TeX and PDF text: `{result['remaining_claim_boundary']['theorem_output_scope_table_present']}`.",
        f"- Reporting-map/norm-equivalence table in main/flat TeX and PDF text: `{result['remaining_claim_boundary']['reporting_map_table_present']}`.",
        f"- Scope-of-conclusion statement in main/flat TeX and PDF text: `{result['remaining_claim_boundary']['theorem_conclusion_scope_guard_present']}`.",
        f"- Proof-structure statement in main/flat TeX and PDF text: `{result['remaining_claim_boundary']['proof_strength_certificate_present']}`.",
        f"- Full 132-row residual-defect bridge in main/flat TeX and PDF text: `{result['remaining_claim_boundary']['full_residual_bridge_present']}`.",
        f"- Route-exclusivity nonmixing boundary in main/flat TeX and PDF text: `{result['remaining_claim_boundary']['route_exclusivity_boundary_present']}`.",
        f"- Theorem residual-certificate exclusivity in statement: `{result['remaining_claim_boundary']['theorem_residual_certificate_exclusivity_present']}`.",
        f"- Introduction proof route in main/flat TeX and PDF text: `{result['remaining_claim_boundary']['intro_proof_hierarchy_present']}`.",
        f"- Theorem-interface and output-boundary anchors table reference coverage: `{result['theorem_anchor_table_reference_coverage']['all_references_present_main_and_flat']}`.",
        f"- Proof-writing boundary card: `{result['proof_writing_boundary_card']['status']}`; safe claim `{result['proof_writing_boundary_card']['safe_reader_claim']}`.",
        f"- Direct residual-bridge scope: `{result['proof_writing_boundary_card']['proof_gap_closed_scope']}`.",
        f"- Primitive/Taylor closure boundary: not 162-term closure `{result['proof_writing_boundary_card']['not_primitive_162_term_taylor_closure']}`; route closed `{result['proof_writing_boundary_card']['primitive_taylor_route_closed']}`; actual/open terms `{result['proof_writing_boundary_card']['actual_taylor_bounds_proved']}` / `{result['proof_writing_boundary_card']['open_taylor_bound_terms']}`; open primitive inputs `{result['proof_writing_boundary_card']['open_primitive_count']}`.",
        f"- Proof-writing forbidden reader claims: `{','.join(result['proof_writing_boundary_card']['forbidden_reader_claims'])}`.",
        f"- Scope of theorem in main/flat TeX and PDF text: `{result['proof_writing_boundary_card']['reader_facing_manuscript_boundary_present']}`.",
        f"- Manuscript anchor map: `{result['manuscript_anchor_map']['all_label_anchors_present']}`; label anchors `{result['manuscript_anchor_map']['label_anchor_count']}`; theorem-interface/P7-output-boundary anchors `{result['manuscript_anchor_map']['theorem_assumption_anchor_count']}`.",
        f"- Theorem-interface/P7-output-boundary anchor map present: `{result['manuscript_anchor_map']['all_theorem_assumption_anchors_present']}`; IDs `{','.join(result['manuscript_anchor_map']['theorem_assumption_anchor_ids'])}`.",
        "- Legacy P7-output-boundary anchor count includes P7 only for traceability across residual tables; it does not promote P7 into the theorem-interface list.",
        f"- Proof-route checks: `{result['satisfied_close_requirement_count']}` traceable, `{result['unsatisfied_close_requirement_count']}` blocked under conditional scope.",
        f"- Active direct row split: `{result['certified_non_dynamic_rows'] + result['active_direct_newton_euler_closed_rows']}` closed / `{result['active_direct_newton_euler_open_rows']}` active-open.",
        f"- Symbolic/primitive-route row split: `{result['certified_non_dynamic_rows']}` non-dynamic certified / `{result['open_dynamic_rows']}` dynamic not certified by that route.",
        f"- Symbolic/primitive-route Newton-Euler open obligations: `{result['newton_euler_open_obligation_count']}`.",
        f"- Active direct Newton-Euler open obligations: `{result['active_direct_newton_euler_open_obligations']}`.",
        f"- Symbolic/primitive open-row scope: `{result['open_dynamic_rows_scope']}`.",
        f"- Newton-Euler closed obligations: `{result['newton_euler_closed_obligation_count']}`.",
        f"- Newton-Euler closed obligation ids: `{result['newton_euler_closed_obligation_ids']}`.",
        f"- Residual-to-error blocking obligations: `{result['residual_to_error_blocking_obligations']}`.",
        f"- Dynamic symbolic oracle complete: `{closure_state.get('dynamic_symbolic_oracle_complete')}`.",
        f"- Stage residual O(h^7) implementation defect proved: `{closure_state.get('stage_residual_O_h7_implementation_defect_proved')}`.",
        f"- Finite scaled-tolerance probe rows/max eta-h ratio: `{solver_state.get('finite_scaled_tolerance_probe_ok_rows')}/{solver_state.get('finite_scaled_tolerance_probe_total_rows')}` / `{solver_state.get('finite_scaled_tolerance_probe_max_residual_over_h7'):.6f}`.",
        f"- Finite scaled-tolerance trajectory probe rows/steps/max eta-h ratio: `{solver_state.get('finite_scaled_tolerance_trajectory_probe_ok_rows')}/{solver_state.get('finite_scaled_tolerance_trajectory_probe_total_rows')}` / `{solver_state.get('finite_scaled_tolerance_trajectory_probe_total_steps_checked')}` / `{solver_state.get('finite_scaled_tolerance_trajectory_probe_max_residual_over_h7'):.6f}`.",
        f"- Finite tolerance-regime sweep policies/rows/steps: `{solver_state.get('finite_tolerance_regime_sweep_policy_count')}` / `{solver_state.get('finite_tolerance_regime_sweep_total_rows')}` / `{solver_state.get('finite_tolerance_regime_sweep_total_steps')}`.",
        f"- Finite h-scaled tolerance-regime sweep rows/steps/velocity-order floor: `{solver_state.get('finite_h_scaled_tolerance_sweep_rows')}` / `{solver_state.get('finite_h_scaled_tolerance_sweep_steps')}` / `{solver_state.get('finite_h_scaled_tolerance_sweep_velocity_order_floor')}`.",
        f"- Per-step branch-selected eta_h policy: `{solver_state.get('per_step_newton_tolerance_policy')}`.",
        f"- Same reduced-chart initial state required: `{solver_state.get('same_reduced_chart_initial_state_required')}`.",
        f"- Gauss-predictor branch-selected Newton solves required: `{solver_state.get('branch_selected_newton_solves_required')}` / `{solver_state.get('newton_iterates_initialized_from_gauss_predictor_required')}`.",
        f"- Arbitrary Newton initializations or remote roots select branch: `{solver_state.get('arbitrary_newton_initializations_select_branch')}` / `{solver_state.get('remote_nonlinear_roots_select_branch')}`.",
        f"- Explicit Gauss truncation constant uniform on compact trajectory tube: `{solver_state.get('gauss_truncation_bound_has_explicit_uniform_constant')}` / `{solver_state.get('gauss_truncation_constant_uniform_on_compact_trajectory_tube')}`.",
        f"- Explicit stage residual-to-root and endpoint constants: `{solver_state.get('stage_residual_to_root_bound_has_explicit_constant')}` / `{solver_state.get('stage_residual_to_root_constant_formula')}` / `{solver_state.get('stage_root_endpoint_perturbation_constant_formula')}`.",
        f"- Accepted root existence proved by stage-residual lemma / not isolated-root premise: `{solver_state.get('accepted_root_existence_proved_by_stage_residual_lemma')}` / `{solver_state.get('accepted_root_existence_not_assumed_as_isolated_root_premise')}`.",
        f"- Explicit endpoint-closure raw-defect and perturbation constants: `{solver_state.get('endpoint_closure_raw_defect_bound_has_explicit_constant')}` / `{solver_state.get('endpoint_closure_raw_defect_constant_symbol')}` / `{solver_state.get('endpoint_closure_perturbation_bound_has_explicit_constant')}` / `{solver_state.get('endpoint_closure_perturbation_constant_formula')}`.",
        f"- Four-term local-defect constants uniform on compact tube / accepted steps: `{solver_state.get('local_defect_constants_uniform_on_compact_proof_tube')}` / `{solver_state.get('local_defect_constants_uniform_over_accepted_steps')}`.",
        f"- Newton error controlled by compact-tube eta_h envelope; reported-grid maximum is specialization: `{solver_state.get('newton_error_controlled_by_compact_tube_eta_h_envelope')}`.",
        f"- Explicit Newton residual-to-stage and endpoint-output constant: `{solver_state.get('newton_residual_to_stage_bound_has_explicit_constant')}` / `{solver_state.get('newton_endpoint_output_map')}` / `{solver_state.get('newton_endpoint_output_map_bound')}` / `{solver_state.get('newton_residual_to_endpoint_perturbation_constant_formula')}`.",
        f"- Explicit eta_h-scaled Newton endpoint bound: `{solver_state.get('newton_eta_h_scaled_endpoint_bound_has_explicit_constant')}` / `{solver_state.get('newton_eta_h_scaled_endpoint_bound_formula')}`.",
        f"- Explicit local-defect constant sum and eta_h absorption: `{solver_state.get('local_defect_bound_has_explicit_uniform_constant_sum')}` / `{solver_state.get('eta_h_constant_absorbed_into_local_defect_constant')}`.",
        f"- Explicit local-to-global and q/v reporting constants: `{solver_state.get('local_global_transfer_has_explicit_reduced_grid_constant')}` / `{solver_state.get('local_global_gronwall_factor_formula')}` / `{solver_state.get('local_global_reduced_grid_constant_formula')}` / `{solver_state.get('qv_reporting_map_constant_distinct_from_residual_defect_constant')}` / `{solver_state.get('qv_reporting_constant_formula')}`.",
        f"- Same-initial-state reported-grid local-to-global transfer and same-grid reported q/v maximum: `{solver_state.get('local_global_transfer_grid_point_error_required')}` / `{solver_state.get('reported_qv_error_bound_uses_same_reported_time_grid')}` / `{solver_state.get('reported_qv_error_bound_is_grid_maximum')}`.",
        f"- Reported time grid t_n=n h and no exact final-time divisibility requirement: `{solver_state.get('reported_time_grid_defined_by_tn_equals_nh')}` / `{solver_state.get('exact_final_time_divisibility_required')}`.",
        f"- eta_h^tube <= c_eta h^7 solver-policy theorem: `{closure_state.get('eta_h_O_h7_solver_policy_evidence')}`.",
        f"- PC3 retained by eta_h theorem condition, not by solver-policy theorem proof: `{any(item.get('id') == 'PC3' and item.get('traceable_under_conditional_scope') for item in close_requirements)}`.",
        f"- PC4 boundary retained by residual-to-error boundary, not by transfer-theorem closure: `{any(item.get('id') == 'PC4' and item.get('traceable_under_conditional_scope') and item.get('residual_to_error_closed') is False for item in close_requirements)}`.",
        f"- Submission-ready scope: `{result['submission_ready_scope']}`.",
        f"- Narrowed-claim B4/B6/B7 subcheck statuses (narrowed-only; not source-policy row closure): `{result['readiness_boundary']['narrowed_claim_b4_b6_b7_statuses']['B4']}/{result['readiness_boundary']['narrowed_claim_b4_b6_b7_statuses']['B6']}/{result['readiness_boundary']['narrowed_claim_b4_b6_b7_statuses']['B7']}`.",
        f"- Remaining global submission boundaries: `{','.join(result['readiness_boundary']['global_submission_boundaries_retained'])}`.",
        f"- Narrowed-claim B4/B6/B7 subcheck closed elsewhere while source-policy rows remain open: `{result['remaining_gate_scope']['b4_b6_b7_closed_elsewhere_under_narrowed_claim']}`.",
        f"- Proof claims traceable under conditional scope: `{result['remaining_gate_scope']['proof_claims_traceable_under_conditional_scope']}`.",
        f"- Direct PC2 residual-value bridge closed under retained theorem interfaces: `{result['remaining_gate_scope']['direct_pc2_proof_gap_closed']}`.",
        f"- Remaining-gate eta_h theorem condition retained for PC3: `{result['remaining_gate_scope']['eta_h_theorem_condition_retained_for_pc3']}`.",
        f"- Remaining-gate residual-to-error blocking obligations: `{result['remaining_gate_scope']['residual_to_error_blocking_obligations']}`.",
        f"- Remaining-gate residual-to-error route promoted: `{result['remaining_gate_scope']['residual_to_error_route_promoted']}`.",
        f"- Remaining-gate active direct Newton-Euler open obligations: `{result['remaining_gate_scope']['active_direct_newton_euler_open_obligations']}`.",
        f"- Remaining-gate symbolic/primitive-route open obligations: `{result['remaining_gate_scope']['symbolic_primitive_route_open_obligations']}`.",
        f"- Submission ready: `{result['submission_ready']}`.",
        "",
        "## Proof Objects",
        "",
        "| object | expected count | main count | flat count |",
        "|---|---:|---:|---:|",
    ]
    for name, expected in EXPECTED_PROOF_OBJECT_COUNTS.items():
        lines.append(
            f"| `{name}` | `{expected}` | `{result['main_source']['proof_object_counts'][name]}` | "
            f"`{result['flat_source']['proof_object_counts'][name]}` |"
        )
    lines.extend(
        [
            "",
            "## Theorem Interface Boundary",
            "",
            "| id | status | retained theorem interface | proved row certificate | direct-route discharged | evidence boundary |",
            "|---|---|---:|---:|---:|---|",
        ]
    )
    for item in theorem_assumptions:
        retained_interface = item.get("id") in retained_theorem_interface_ids
        proved_certificate = bool(
            item.get("proved_certificate") or item.get("satisfied_for_submission")
        )
        lines.append(
            f"| `{item['id']}` | `{item['status']}` | `{retained_interface}` | "
            f"`{proved_certificate}` | `{item['satisfied_for_submission']}` | "
            f"{item['evidence']} |"
        )
    lines.extend(
        [
            "",
            "P4 split reading rule: P4 remains a retained binding interface and also carries a proved 96-row non-dynamic row certificate.",
            "The `direct-route discharged` column is reserved for assumptions fully discharged as theorem inputs by themselves; P4 is consumed only after its proved 96-row certificate is assembled with P5's 36-row direct Newton--Euler certificate on the same accepted branch.",
            "",
            "## Manuscript Anchors",
            "",
            "| id | label keys | main lines | flat lines |",
            "|---|---|---|---|",
        ]
    )
    for assumption_id in result["manuscript_anchor_map"]["theorem_assumption_anchor_ids"]:
        anchor = result["manuscript_anchor_map"]["theorem_assumption_anchor_map"][assumption_id]
        label_keys = ",".join(anchor["label_keys"])
        main_lines = ",".join(
            f"{key}:{anchor['main_lines'][key]}" for key in anchor["label_keys"]
        )
        flat_lines = ",".join(
            f"{key}:{anchor['flat_lines'][key]}" for key in anchor["label_keys"]
        )
        lines.append(f"| `{assumption_id}` | `{label_keys}` | `{main_lines}` | `{flat_lines}` |")
    lines.extend(
        [
            "",
            "## Proof Route Checks",
            "",
            "| id | requirement | traceability status | mode |",
            "|---|---|---|---|",
        ]
    )
    for item in close_requirements:
        lines.append(
            f"| `{item['id']}` | {item['requirement']} | `{item.get('display_status', item.get('satisfied'))}` | "
            f"`{item.get('satisfaction_mode')}` |"
        )
    lines.extend(
        [
            "",
            "## Reading Rule",
            "",
            "The manuscript proof is traceable as a conditional local-defect-to-global-error proof.",
            "This audit records discharge of the PC2 stage-residual condition by the direct same-branch D5 residual-value bridge.",
            "It does not close the primitive dynamic symbolic oracle, the primitive/Taylor PC2 route,",
            "the empirical eta_h solver-scale diagnostics, or the residual-to-error route.",
            "PC3 enters the route only because the eta_h^tube <= c_eta h^7 policy remains an explicit theorem condition; the reported-grid eta_h is only the accepted trajectory specialization.",
            "The theorem invocation consumes exactly one residual-value certificate; any future primitive/Taylor certificate must replace the accepted direct certificate by proving a new same-tuple 132-row residual-value bound rather than being appended to it.",
            "PC4 is recorded only as a retained transfer-scope exclusion; four-link/slider-crank residual rows are not promoted to accepted dynamic-order proof.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("proof_claim_traceability_audit=written")
    print(f"labels_present={result['main_source']['all_labels_present']}/{result['flat_source']['all_labels_present']}")
    print(f"unsatisfied_close_requirements={result['unsatisfied_close_requirement_count']}")
    print("submission_ready=False")


if __name__ == "__main__":
    main()
