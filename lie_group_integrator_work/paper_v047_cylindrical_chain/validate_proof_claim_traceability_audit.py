#!/usr/bin/env python3
"""Validate proof-claim traceability against the manuscript and proof tables."""

from __future__ import annotations

import json
import math
import re
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
AUDIT_JSON = PAPER / "PROOF_CLAIM_TRACEABILITY_AUDIT.json"
AUDIT_MD = PAPER / "PROOF_CLAIM_TRACEABILITY_AUDIT.md"
MAIN_TEX = PAPER / "main_cmame.tex"
FLAT_TEX = PAPER / "cmame_submission_flat" / "main_cmame_submission.tex"
MAIN_PDF_TEXT = PAPER / "main_cmame.txt"
FLAT_PDF_TEXT = PAPER / "cmame_submission_flat" / "main_cmame_submission.txt"
PROOF_CLOSURE = PAPER / "PROOF_CLOSURE_MANIFEST.json"
PROOF_CONTRACT = PAPER / "CMAME_PROOF_CONTRACT_GATE.json"
PROOF_EVIDENCE = PAPER / "PROOF_EVIDENCE_MATRIX.md"
CLAIM_BOUNDARY = PAPER / "CLAIM_BOUNDARY.json"
BLOCKER_GATE = PAPER / "CMAME_BLOCKER_CLOSURE_GATE.json"
NEWTON_EULER_SYMBOLIC_TARGET = PAPER / "NEWTON_EULER_SYMBOLIC_TARGET_AUDIT.json"
NEWTON_EULER_SYMBOLIC_DEFECT_CERTIFICATE = PAPER / "NEWTON_EULER_SYMBOLIC_DEFECT_CERTIFICATE.json"

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
    "The theorem retains this as a uniform solver-scale hypothesis",
    "runs and backend stopping records provide finite diagnostics only",
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
    "No residual-to-error transfer theorem is assumed here",
    "the seven transfer obligations remain outside this theorem",
    "certificates prove the direct PC2 residual bridge under the retained P6",
    "they do not prove P6 or P7 themselves",
    "Kernel and observability obstruction",
    "observability statement",
    r"\(h\)-uniform",
    "near-null direction",
    "trajectory-visible perturbation",
    "trajectory-visible kernel directions",
    "Separate primitive-route target only; not invoked by the theorem",
    r"The theorem consumes \(\mathsf{D}_{\rm dir}\) as the proved direct certificate",
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
    "Parameter-dependent Taylor-family rule",
    r"\(h\mapsto F_{A,h}\)",
    "parameterized family of finite-dimensional stage maps",
    "applied only in the stage variable",
    "not a derivative with respect to \\(h\\)",
    "same frozen residual map",
    "Reference-style insertion checkpoint",
    "local truncation errors by substituting the exact constrained solution into",
    "BLieDF hidden-constraint difference estimate, multiplier recursion",
    "BDF zero-stability norm, or primitive D5 decomposition",
    "Stage-time binding for nonautonomous rows",
    r"time-indexed residual \(F_{A,h,t_n}\)",
    r"stage times \(t_{n,i}=t_n+c_i h\)",
    "synchronized time-indexed one-step statement",
    "fixed-time-slice",
    r"abbreviation for \(F_{A,h,t_n}\)",
    r"is only in the stage variables at fixed \(t_n\)",
    "same time-indexed residual slice",
    "different transition times and then assembled into one",
    r"R_{h,n}=F_{A,h,t_n}(Z_G(y,t_n,h);y)",
    "no non-dynamic row, Newton--Euler row, Jacobian, or endpoint map is imported",
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
    "Endpoint-time binding",
    "fixed-transition",
    r"\(\mathcal C_{h,t_n}\)",
    r"endpoint time \(t_n+h\)",
    "Endpoint-time nonfeedback rule",
    "not a dense-output interpolant",
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
    r"\label{tab:proof-causality-ledger}",
    "Proof causality",
    "Proof-causality rule",
    "each mathematical input is consumed",
    "D5 direct-substitution certificate is evaluated on the lifted Gauss stage",
    "before the local perturbation argument",
    "local defect bound is established before the discrete Gronwall transfer",
    "position--velocity reporting map is used only after the reduced-chart grid estimate",
    "do not feed PC2",
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
    "P5 inverse-boundary",
    "dynamic block of the residual vector",
    "stage-Jacobian inverse",
    "contraction radius",
    "branch-selection theorem",
    "endpoint right inverse",
    "stability factor",
    "solver policy",
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


class Checks:
    def __init__(self) -> None:
        self.errors: list[str] = []

    def check(self, condition: bool, message: str) -> None:
        if not condition:
            self.errors.append(message)


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


def count_map(tex: str) -> dict[str, int]:
    return {name: count_environment(tex, name) for name in EXPECTED_PROOF_OBJECT_COUNTS}


def reader_facing_boundary_checks(text: str) -> dict[str, Any]:
    tokens = {token: contains_normalized(text, token) for token in READER_FACING_BOUNDARY_TOKENS}
    return {
        "tokens": tokens,
        "all_tokens_present": all(tokens.values()),
    }


def main() -> int:
    checks = Checks()
    try:
        audit = read_json(AUDIT_JSON)
        audit_md = read_text(AUDIT_MD)
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
    except Exception as exc:  # noqa: BLE001
        print(f"proof claim traceability audit validation: FAIL\n- {exc}")
        return 1

    checks.check(audit.get("schema") == "proof-claim-traceability-audit-v1", "audit schema changed")
    checks.check(
        audit.get("status") == "conditional_proof_claims_traceable_submission_not_ready",
        "audit status changed",
    )
    checks.check(audit.get("read_only_audit") is True, "audit is not read-only")
    checks.check(audit.get("submission_ready") is False, "audit must not claim submission ready")
    checks.check(
        audit.get("submission_ready_scope")
        == "traceability_global_proof_boundary_not_narrowed_claim_package_decision",
        "traceability submission-ready scope changed",
    )
    strict_direct_standard = proof_closure.get(
        "strict_direct_residual_bridge_submission_standard", {}
    )
    checks.check(audit.get("proof_mode") == "conditional_consistency_transfer", "proof mode changed")
    checks.check(
        audit.get("proof_contract_mode") == proof_contract.get("proof_mode") == "conditional_consistency_transfer",
        "proof contract mode changed",
    )
    theorem_traceability = audit.get("manuscript_theorem_traceability", {})
    contract_traceability = proof_contract.get("manuscript_theorem_traceability", {})
    theorem_statement_boundary = proof_closure.get("theorem_statement_boundary", {})
    manuscript_traceability = proof_closure.get("manuscript_traceability", {})
    checks.check(
        theorem_traceability.get("source_manifest")
        == contract_traceability.get("source_manifest")
        == "PROOF_CLOSURE_MANIFEST.json",
        "proof-claim theorem traceability source manifest changed",
    )
    checks.check(
        theorem_traceability.get("source_contract_gate") == "CMAME_PROOF_CONTRACT_GATE.json",
        "proof-claim theorem traceability source contract gate changed",
    )
    checks.check(
        theorem_traceability.get("proof_closure_status")
        == contract_traceability.get("proof_closure_status")
        == proof_closure.get("status"),
        "proof-claim theorem traceability proof-closure status mismatch",
    )
    checks.check(
        theorem_traceability.get("accepted_theorem_label")
        == contract_traceability.get("accepted_theorem_label")
        == theorem_statement_boundary.get("accepted_theorem_label")
        == "thm:g6fullva-order",
        "proof-claim theorem traceability accepted theorem label mismatch",
    )
    checks.check(
        theorem_traceability.get("accepted_method_order")
        == contract_traceability.get("accepted_method_order")
        == theorem_statement_boundary.get("accepted_method_order")
        == 6,
        "proof-claim theorem traceability accepted method order mismatch",
    )
    checks.check(
        theorem_traceability.get("accepted_local_defect_order")
        == contract_traceability.get("accepted_local_defect_order")
        == theorem_statement_boundary.get("accepted_local_defect_order")
        == 7,
        "proof-claim theorem traceability accepted local defect order mismatch",
    )
    checks.check(
        theorem_traceability.get("theorem_statement_labels_present")
        == contract_traceability.get("theorem_statement_labels_present")
        == theorem_statement_boundary.get("all_required_labels_present_main_and_flat")
        is True,
        "proof-claim theorem traceability theorem label marker mismatch",
    )
    checks.check(
        theorem_traceability.get("conditional_theorem_boundary_present")
        == contract_traceability.get("conditional_theorem_boundary_present")
        == theorem_statement_boundary.get("conditional_theorem_boundary_present_main_and_flat")
        is True,
        "proof-claim theorem traceability conditional theorem boundary mismatch",
    )
    checks.check(
        theorem_traceability.get("theorem_reading_guide_present")
        == theorem_statement_boundary.get("theorem_reading_guide_present_main_and_flat")
        is True,
        "proof-claim theorem traceability theorem reading guide marker mismatch",
    )
    checks.check(
        theorem_traceability.get("conditional_proof_claims_mapped_to_manuscript")
        == contract_traceability.get("conditional_proof_claims_mapped_to_manuscript")
        == manuscript_traceability.get("conditional_proof_claims_mapped_to_manuscript")
        is True,
        "proof-claim theorem traceability manuscript mapping mismatch",
    )
    checks.check(
        theorem_traceability.get("proof_dependency_graph_present")
        == contract_traceability.get("proof_dependency_graph_present")
        == manuscript_traceability.get("proof_dependency_graph_present_main_and_flat")
        is True,
        "proof-claim theorem traceability proof dependencies mismatch",
    )
    checks.check(
        theorem_traceability.get("proof_traceability_table_present")
        == contract_traceability.get("proof_traceability_table_present")
        == manuscript_traceability.get("proof_traceability_table_present_main_and_flat")
        is True,
        "proof-claim theorem traceability proof traceability table mismatch",
    )
    checks.check(
        theorem_traceability.get("dynamic_proof_closure_matrix_present")
        == contract_traceability.get("dynamic_proof_closure_matrix_present")
        == manuscript_traceability.get("dynamic_proof_closure_matrix_present_main_and_flat")
        is True,
        "proof-claim theorem traceability dynamic proof closure matrix mismatch",
    )
    checks.check(
        theorem_traceability.get("primitive_lane_boundary_present")
        == contract_traceability.get("primitive_lane_boundary_present")
        == manuscript_traceability.get("primitive_lane_boundary_present_main_and_flat")
        is True,
        "proof-claim theorem traceability primitive-route boundary mismatch",
    )
    checks.check(
        theorem_traceability.get("theorem_scope_references_d5_primitive_blocker_ledger") is True,
        "proof-claim theorem scope does not reference D5 primitive blocker ledger",
    )
    checks.check(
        theorem_traceability.get("theorem_scope_preserves_primitive_pc2_closed_false") is True,
        "proof-claim theorem scope does not preserve primitive PC2-lane-open boundary",
    )
    checks.check(
        theorem_traceability.get("theorem_scope_primitive_boundary_present") is True,
        "proof-claim theorem scope primitive boundary token group missing",
    )
    checks.check(
        theorem_traceability.get("taylor_finite_implication_present") is True,
        "proof-claim Taylor finite-implication/nonclosure token group missing",
    )
    checks.check(
        theorem_traceability.get("taylor_finite_implication_main_flat") == [True, True],
        "proof-claim Taylor finite-implication main/flat status changed",
    )
    checks.check(
        theorem_traceability.get("route_exclusivity_boundary_present") is True,
        "proof-claim route-exclusivity boundary not propagated to theorem traceability",
    )
    checks.check(
        theorem_traceability.get("theorem_residual_certificate_exclusivity_present") is True,
        "proof-claim theorem residual-certificate exclusivity not propagated to theorem traceability",
    )
    for token in [
        r"\label{lem:d5-conditional-taylor-finite-sum}",
        r"\label{prop:d5-primitive-taylor-conditional-implication}",
        r"\label{lem:d5-primitive-obligation-implication}",
        "Conditional finite-sum Taylor implication for the D5 route",
        "This separate primitive-route lemma is a conditional finite implication",
        "Assume the five remaining primitive obligations",
        "every D5 Taylor subterm in the 36 Newton--Euler rows",
        "not an accepted primitive-route closure, not a PC2 input",
        "non-active replacement-certificate route rather than current theorem evidence",
    ]:
        checks.check(
            contains_normalized(main_tex, token) and contains_normalized(flat_tex, token),
            f"main/flat missing Taylor finite-implication token: {token}",
        )
    checks.check(
        contains_normalized(main_tex, r"Tables~\ref{tab:d5-primitive-blocker-ledger}")
        and contains_normalized(flat_tex, r"Tables~\ref{tab:d5-primitive-blocker-ledger}"),
        "main/flat theorem scope missing D5 primitive blocker ledger reference",
    )
    checks.check(
        contains_normalized(
            main_tex,
            "It is not theorem evidence unless the named primitives are independently proved on the same compact branch",
        )
        and contains_normalized(
            flat_tex,
            "It is not theorem evidence unless the named primitives are independently proved on the same compact branch",
        ),
        "main/flat theorem scope missing primitive PC2-lane-open prose",
    )
    checks.check(
        "- Theorem-scope primitive blocker ledger/pc2-open boundary: `True/True`." in audit_md,
        "proof-claim markdown missing theorem-scope primitive blocker ledger summary",
    )
    checks.check(
        "- Taylor finite-implication/nonclosure statements main/flat: `True/True`." in audit_md,
        "proof-claim markdown missing Taylor finite-implication/nonclosure summary",
    )
    checks.check(
        theorem_traceability.get("residual_nonpromotion_present")
        == contract_traceability.get("residual_nonpromotion_present")
        == manuscript_traceability.get("residual_to_error_nonpromotion_present_main_and_flat")
        is True,
        "proof-claim theorem traceability residual nonpromotion mismatch",
    )
    checks.check(
        theorem_traceability.get("eta_h_theorem_condition_retained")
        == contract_traceability.get("eta_h_theorem_condition_retained")
        == theorem_statement_boundary.get("eta_h_theorem_condition_retained")
        is True,
        "proof-claim theorem traceability eta_h theorem condition mismatch",
    )
    checks.check(
        theorem_traceability.get("eta_h_solver_policy_evidence_closed")
        == contract_traceability.get("eta_h_solver_policy_evidence_closed")
        == theorem_statement_boundary.get("eta_h_solver_policy_evidence_closed")
        is False,
        "proof-claim theorem traceability overclaims eta_h solver-policy theorem",
    )
    checks.check(
        theorem_traceability.get("fixed_tolerance_runs_are_asymptotic_proof")
        == contract_traceability.get("fixed_tolerance_runs_are_asymptotic_proof")
        == theorem_statement_boundary.get("fixed_tolerance_runs_are_asymptotic_proof")
        is False,
        "proof-claim theorem traceability overclaims fixed-tolerance proof",
    )
    checks.check(
        theorem_traceability.get("residual_to_error_not_promoted")
        == contract_traceability.get("residual_to_error_not_promoted")
        == theorem_statement_boundary.get("does_not_promote_residual_to_error")
        is True,
        "proof-claim theorem traceability residual-to-error boundary mismatch",
    )
    checks.check(
        theorem_traceability.get("source_policy_or_full_tfe_not_promoted")
        == contract_traceability.get("source_policy_or_full_tfe_not_promoted")
        == theorem_statement_boundary.get("does_not_promote_source_policy_or_full_tfe")
        is True,
        "proof-claim theorem traceability source-policy/full-TFE nonpromotion mismatch",
    )
    checks.check(
        theorem_traceability.get("does_not_change_proof_closure_state")
        == contract_traceability.get("does_not_change_proof_closure_state")
        == manuscript_traceability.get("does_not_change_proof_closure_state")
        is True,
        "proof-claim theorem traceability state-change marker mismatch",
    )
    checks.check(
        "without closing eta_h solver-policy theorem, residual-to-error, or source-policy/full-TFE gates"
        in theorem_traceability.get("traceability_audit_role", ""),
        "proof-claim theorem traceability role boundary missing",
    )
    summary = audit.get("summary", {})
    checks.check(
        summary.get("proof_status") == "conditional_direct_route_traceable_submission_not_ready",
        "traceability summary proof status changed",
    )
    checks.check(summary.get("submission_ready") is False, "traceability summary must not claim submission ready")
    checks.check(summary.get("theorem_assumptions_total") == 7, "traceability summary theorem count changed")
    checks.check(
        summary.get("theorem_assumptions_submission_satisfied") == 1,
        "traceability summary satisfied-theorem-assumption count changed",
    )
    checks.check(
        summary.get("theorem_assumptions_retained_or_open") == 6,
        "traceability summary retained-interface/open-nonpromotion count changed",
    )
    checks.check(
        summary.get("theorem_assumptions_retained_theorem_interfaces") == 5,
        "traceability summary retained theorem-interface count changed",
    )
    checks.check(
        summary.get("theorem_assumptions_open_nonpromotion_boundaries") == 1,
        "traceability summary open output-boundary count changed",
    )
    checks.check(
        summary.get("theorem_assumption_submission_satisfied_ids") == ["P5"],
        "traceability summary satisfied assumption IDs changed",
    )
    checks.check(
        summary.get("theorem_assumption_retained_or_open_ids") == ["P1", "P2", "P3", "P4", "P6", "P7"],
        "traceability summary retained-interface/open-nonpromotion IDs changed",
    )
    checks.check(
        summary.get("theorem_assumption_retained_theorem_interface_ids")
        == ["P1", "P2", "P3", "P4", "P6"],
        "traceability summary retained theorem-interface IDs changed",
    )
    checks.check(
        summary.get("theorem_assumption_open_nonpromotion_boundary_ids") == ["P7"],
        "traceability summary open output-boundary IDs changed",
    )
    checks.check(summary.get("close_requirements_total") == 4, "traceability summary close requirement count changed")
    checks.check(
        summary.get("close_requirements_unsatisfied") == 0,
        "traceability summary unsatisfied close requirement count changed",
    )
    checks.check(
        summary.get("close_requirement_satisfied_ids") == ["PC1", "PC2", "PC3", "PC4"],
        "traceability summary satisfied close requirement IDs changed",
    )
    checks.check(
        summary.get("close_requirement_unsatisfied_ids") == [],
        "traceability summary unsatisfied close requirement IDs changed",
    )
    checks.check(
        summary.get("remaining_claim_boundary_status") == "theorem_conditions_retained_not_submission_ready",
        "traceability summary remaining claim boundary status changed",
    )
    expected_anchor_map = manuscript_anchor_map(main_tex, flat_tex)
    checks.check(
        summary.get("manuscript_anchor_label_count")
        == expected_anchor_map["label_anchor_count"]
        == 24,
        "traceability summary manuscript anchor label count changed",
    )
    checks.check(
        summary.get("manuscript_anchor_map_present")
        == expected_anchor_map["all_label_anchors_present"]
        is True,
        "traceability summary manuscript anchor map missing",
    )
    checks.check(
        summary.get("theorem_assumption_anchor_count")
        == expected_anchor_map["theorem_assumption_anchor_count"]
        == 7,
        "traceability summary theorem-assumption anchor count changed",
    )
    checks.check(
        summary.get("theorem_assumption_anchor_map_present")
        == expected_anchor_map["all_theorem_assumption_anchors_present"]
        is True,
        "traceability summary theorem-assumption anchor map missing",
    )
    checks.check(
        summary.get("direct_pc2_proof_gap_closed") is True,
        "traceability summary direct PC2 proof gap not closed",
    )
    checks.check(
        summary.get("stage_residual_O_h7_implementation_defect_proved") is True,
        "traceability summary implementation defect proof changed",
    )
    checks.check(
        summary.get("dynamic_symbolic_oracle_complete") is False,
        "traceability summary must keep dynamic symbolic oracle open",
    )
    checks.check(
        summary.get("active_direct_newton_euler_open_obligations") == 0,
        "traceability summary active direct Newton-Euler open obligations changed",
    )
    checks.check(
        summary.get("symbolic_primitive_route_open_obligations") == 1,
        "traceability summary primitive-route open obligations changed",
    )
    checks.check(
        summary.get("eta_h_O_h7_solver_policy_evidence") is False,
        "traceability summary eta_h evidence must remain open",
    )
    checks.check(
        summary.get("eta_h_theorem_condition_retained_for_pc3") is True,
        "traceability summary PC3 retained-condition marker changed",
    )
    checks.check(
        summary.get("residual_to_error_blocking_obligations") == 7,
        "traceability summary residual-to-error obligation count changed",
    )
    checks.check(
        summary.get("residual_to_error_route_promoted") is False,
        "traceability summary must not promote residual-to-error route",
    )
    checks.check(
        summary.get("global_submission_boundaries_retained")
        == [
            "full_source_policy_package_ready",
            "theorem_level_eta_h_solver_policy_evidence",
            "closed_residual_to_error_theorem_for_mechanism_rows",
        ],
        "traceability summary global boundaries changed",
    )
    proof_writing_card = audit.get("proof_writing_boundary_card", {})
    checks.check(
        summary.get("proof_writing_boundary_card_status")
        == proof_writing_card.get("status")
        == "conditional_theorem_traceable_direct_pc2_closed_global_boundaries_retained",
        "proof-writing boundary card status changed",
    )
    checks.check(
        summary.get("proof_writing_boundary_card_safe_reader_claim")
        == proof_writing_card.get("safe_reader_claim")
        == (
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
        "proof-writing boundary card safe claim changed",
    )
    checks.check(
        proof_writing_card.get("schema") == "proof-writing-boundary-card-v1"
        and proof_writing_card.get("accepted_theorem_label") == "thm:g6fullva-order"
        and proof_writing_card.get("accepted_method_order") == 6
        and proof_writing_card.get("accepted_local_defect_order") == 7,
        "proof-writing boundary card theorem metadata changed",
    )
    checks.check(
        proof_writing_card.get("manuscript_anchor_map_present") is True
        and proof_writing_card.get("theorem_assumption_anchor_ids")
        == ["P1", "P2", "P3", "P4", "P5", "P6", "P7"],
        "proof-writing boundary card manuscript anchor map changed",
    )
    checks.check(
        proof_writing_card.get("submission_satisfied_assumption_ids") == ["P5"]
        and proof_writing_card.get("retained_or_open_assumption_ids")
        == ["P1", "P2", "P3", "P4", "P6", "P7"]
        and proof_writing_card.get("satisfied_close_requirement_ids")
        == ["PC1", "PC2", "PC3", "PC4"]
        and proof_writing_card.get("unsatisfied_close_requirement_ids") == [],
        "proof-writing boundary card assumption/close-requirement split changed",
    )
    checks.check(
        proof_writing_card.get("direct_pc2_proof_gap_closed") is True
        and proof_writing_card.get("stage_residual_O_h7_implementation_defect_proved") is True
        and proof_writing_card.get("active_direct_newton_euler_closed_rows") == 36
        and proof_writing_card.get("active_direct_newton_euler_open_obligations") == 0
        and proof_writing_card.get("symbolic_primitive_route_open_obligations") == 1,
        "proof-writing boundary card direct-route row split changed",
    )
    checks.check(
        proof_writing_card.get("proof_gap_closed_scope")
        == "direct_residual_bridge_kantorovich_route_closed_primitive_taylor_conditional_schema_open"
        and proof_writing_card.get("not_primitive_162_term_taylor_closure") is True
        and proof_writing_card.get("primitive_taylor_route_closed") is False
        and proof_writing_card.get("actual_taylor_bounds_proved") == 0
        and proof_writing_card.get("open_taylor_bound_terms") == 162
        and proof_writing_card.get("terms_with_open_primitive_blockers") == 162
        and proof_writing_card.get("open_primitive_assumption_count") == 5
        and proof_writing_card.get("open_primitive_count") == 5
        and proof_writing_card.get("route_exclusivity_boundary_present") is True
        and proof_writing_card.get("theorem_residual_certificate_exclusivity_present") is True
        and proof_writing_card.get("not_primitive_162_term_taylor_closure")
        == strict_direct_standard.get("not_primitive_162_term_taylor_closure")
        and proof_writing_card.get("primitive_taylor_route_closed")
        == strict_direct_standard.get("primitive_taylor_route_closed")
        and proof_writing_card.get("actual_taylor_bounds_proved")
        == strict_direct_standard.get("primitive_taylor_actual_bounds_proved")
        and proof_writing_card.get("open_taylor_bound_terms")
        == strict_direct_standard.get("primitive_taylor_open_bound_terms"),
        "proof-writing boundary card Taylor/primitive open-route guard changed",
    )
    checks.check(
        proof_writing_card.get("theorem_reading_guide_present")
        == theorem_traceability.get("theorem_reading_guide_present")
        is True,
        "proof-writing boundary card theorem reading guide marker missing",
    )
    checks.check(
        proof_writing_card.get("dynamic_symbolic_oracle_complete") is False
        and proof_writing_card.get("eta_h_theorem_condition_retained_for_pc3") is True
        and proof_writing_card.get("eta_h_solver_policy_evidence_closed") is False
        and proof_writing_card.get("fixed_tolerance_runs_are_asymptotic_proof") is False
        and proof_writing_card.get("residual_to_error_blocking_obligations") == 7
        and proof_writing_card.get("residual_to_error_route_promoted") is False
        and proof_writing_card.get("source_policy_or_full_tfe_not_promoted") is True,
        "proof-writing boundary card no-promotion flags changed",
    )
    checks.check(
        proof_writing_card.get("global_submission_boundaries_retained")
        == [
            "full_source_policy_package_ready",
            "theorem_level_eta_h_solver_policy_evidence",
            "closed_residual_to_error_theorem_for_mechanism_rows",
        ]
        and proof_writing_card.get("forbidden_reader_claims")
        == [
            "unconditional theorem without theorem-domain interfaces",
            "eta_h solver-policy condition closed",
            "fixed-tolerance runs as asymptotic proof",
            "accepted residual-to-error transfer theorem for mechanism rows",
            "source-policy/full-TFE package readiness",
            "mixing direct and primitive-route residual certificates to lower constants, remove P6, or prove a P7 residual-to-error transfer theorem",
        ],
        "proof-writing boundary card retained/forbidden boundary changed",
    )
    expected_reader_facing_boundary = {
        "main_tex": reader_facing_boundary_checks(main_tex),
        "flat_tex": reader_facing_boundary_checks(flat_tex),
        "main_pdf_text": reader_facing_boundary_checks(main_pdf_text),
        "flat_pdf_text": reader_facing_boundary_checks(flat_pdf_text),
    }
    checks.check(
        audit.get("reader_facing_proof_claim_boundary") == expected_reader_facing_boundary,
        "proof claim boundary token map stale",
    )
    checks.check(
        proof_writing_card.get("reader_facing_manuscript_boundary_present")
        == audit.get("remaining_claim_boundary", {}).get("reader_facing_manuscript_boundary_present")
        == summary.get("reader_facing_proof_claim_boundary_present")
        is True,
        "proof claim boundary not marked present",
    )
    for location, token_map in expected_reader_facing_boundary.items():
        checks.check(
            token_map["all_tokens_present"] is True,
            f"proof claim boundary missing in {location}",
        )
    checks.check(
        "Scope of theorem in main/flat TeX and PDF text: `True`."
        in audit_md,
        "audit markdown missing proof claim boundary line",
    )
    p7_boundary_tokens = [
        "residual-only mechanism rows require a separate",
        "P7 remains a separate output nonclaim/residual-to-error boundary",
        "not a theorem premise",
    ]
    expected_p7_boundary = {
        "tokens": p7_boundary_tokens,
        "checks": {
            "main_tex": {
                token: contains_normalized(main_tex, token) for token in p7_boundary_tokens
            },
            "flat_tex": {
                token: contains_normalized(flat_tex, token) for token in p7_boundary_tokens
            },
        },
        "all_tokens_present": True,
    }
    checks.check(
        audit.get("p7_retained_nonpromotion_boundary") == expected_p7_boundary,
        "P7 output nonclaim/residual-to-error boundary token map stale",
    )
    checks.check(
        theorem_traceability.get("p7_retained_nonpromotion_boundary_present")
        == audit.get("remaining_claim_boundary", {}).get("p7_retained_nonpromotion_boundary_present")
        == proof_writing_card.get("p7_retained_nonpromotion_boundary_present")
        == summary.get("p7_retained_nonpromotion_boundary_present")
        == expected_p7_boundary["all_tokens_present"]
        is True,
        "P7 output nonclaim/residual-to-error boundary not propagated in traceability audit",
    )
    checks.check(
        "P7 output nonclaim/residual-to-error boundary in manuscript: `True`." in audit_md,
        "audit markdown missing P7 output nonclaim/residual-to-error boundary line",
    )
    b1_scope_tokens = [
        "implementation-path boundary",
        "closed certificate supplies",
        "AD-expanded implementation-path",
        "active direct residual route only",
        "does not close the primitive dynamic symbolic oracle",
        "primitive symbolic defect certificate",
        "source-paper residual replacement",
        "source-policy package readiness",
    ]
    expected_b1_scope = {
        "tokens": b1_scope_tokens,
        "checks": {
            "main_tex": {
                token: contains_normalized(main_tex, token) for token in b1_scope_tokens
            },
            "flat_tex": {
                token: contains_normalized(flat_tex, token) for token in b1_scope_tokens
            },
            "main_pdf_text": {
                token: contains_normalized(main_pdf_text, token) for token in b1_scope_tokens
            },
            "flat_pdf_text": {
                token: contains_normalized(flat_pdf_text, token) for token in b1_scope_tokens
            },
        },
        "all_tokens_present": True,
    }
    checks.check(
        audit.get("b1_closure_scope_boundary") == expected_b1_scope,
        "B1 closure-scope boundary token map stale",
    )
    checks.check(
        theorem_traceability.get("b1_closure_scope_boundary_present")
        == audit.get("remaining_claim_boundary", {}).get("b1_closure_scope_boundary_present")
        == proof_writing_card.get("b1_closure_scope_boundary_present")
        == summary.get("b1_closure_scope_boundary_present")
        == expected_b1_scope["all_tokens_present"]
        is True,
        "B1 closure-scope boundary not propagated in traceability audit",
    )
    checks.check(
        "B1 closure-scope boundary in main/flat TeX and PDF text: `True`." in audit_md,
        "audit markdown missing B1 closure-scope boundary line",
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
    expected_p6_solver_scope = {
        "tokens": p6_solver_scope_tokens,
        "pdf_reader_tokens": p6_solver_scope_pdf_reader_tokens,
        "checks": {
            "main_tex": {
                token: contains_normalized(main_tex, token) for token in p6_solver_scope_tokens
            },
            "flat_tex": {
                token: contains_normalized(flat_tex, token) for token in p6_solver_scope_tokens
            },
            "main_pdf_text": {
                token: contains_normalized(main_pdf_text, token) for token in p6_solver_scope_pdf_reader_tokens
            },
            "flat_pdf_text": {
                token: contains_normalized(flat_pdf_text, token) for token in p6_solver_scope_pdf_reader_tokens
            },
        },
        "all_tokens_present": True,
        "tex_all_tokens_present": True,
        "pdf_reader_tokens_present": True,
    }
    checks.check(
        audit.get("p6_solver_scope_boundary") == expected_p6_solver_scope,
        "P6 solver-scope boundary token map stale",
    )
    checks.check(
        theorem_traceability.get("p6_solver_scope_boundary_present")
        == audit.get("remaining_claim_boundary", {}).get("p6_solver_scope_boundary_present")
        == proof_writing_card.get("p6_solver_scope_boundary_present")
        == summary.get("p6_solver_scope_boundary_present")
        == expected_p6_solver_scope["all_tokens_present"]
        is True,
        "P6 solver-scope boundary not propagated in traceability audit",
    )
    checks.check(
        "P6 solver-scope boundary in source TeX plus PDF reader text: `True`." in audit_md,
        "audit markdown missing P6 solver-scope boundary line",
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
    expected_p1p2_compact_tube = {
        "tokens": p1p2_compact_tube_tokens,
        "pdf_reader_tokens": p1p2_compact_tube_pdf_reader_tokens,
        "checks": {
            "main_tex": {
                token: contains_normalized(main_tex, token) for token in p1p2_compact_tube_tokens
            },
            "flat_tex": {
                token: contains_normalized(flat_tex, token) for token in p1p2_compact_tube_tokens
            },
            "main_pdf_text": {
                token: contains_normalized(main_pdf_text, token) for token in p1p2_compact_tube_pdf_reader_tokens
            },
            "flat_pdf_text": {
                token: contains_normalized(flat_pdf_text, token) for token in p1p2_compact_tube_pdf_reader_tokens
            },
        },
        "all_tokens_present": True,
        "tex_all_tokens_present": True,
        "pdf_reader_tokens_present": True,
    }
    checks.check(
        audit.get("p1p2_compact_tube_boundary") == expected_p1p2_compact_tube,
        "P1/P2 compact-tube boundary token map stale",
    )
    checks.check(
        theorem_traceability.get("p1p2_compact_tube_boundary_present")
        == audit.get("remaining_claim_boundary", {}).get("p1p2_compact_tube_boundary_present")
        == proof_writing_card.get("p1p2_compact_tube_boundary_present")
        == summary.get("p1p2_compact_tube_boundary_present")
        == expected_p1p2_compact_tube["all_tokens_present"]
        is True,
        "P1/P2 compact-tube boundary not propagated in traceability audit",
    )
    checks.check(
        "P1/P2 compact-tube boundary in source TeX plus PDF reader text: `True`." in audit_md,
        "audit markdown missing P1/P2 compact-tube boundary line",
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
    expected_p3p4_implementation_boundary = {
        "tokens": p3p4_implementation_boundary_tokens,
        "checks": {
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
        },
        "all_tokens_present": True,
    }
    checks.check(
        audit.get("p3p4_implementation_boundary") == expected_p3p4_implementation_boundary,
        "P3/P4 implementation-defect boundary token map stale",
    )
    checks.check(
        theorem_traceability.get("p3p4_implementation_boundary_present")
        == audit.get("remaining_claim_boundary", {}).get("p3p4_implementation_boundary_present")
        == proof_writing_card.get("p3p4_implementation_boundary_present")
        == summary.get("p3p4_implementation_boundary_present")
        == expected_p3p4_implementation_boundary["all_tokens_present"]
        is True,
        "P3/P4 implementation-defect boundary not propagated in traceability audit",
    )
    checks.check(
        "P3/P4 implementation-defect boundary in main/flat TeX and PDF text: `True`."
        in audit_md,
        "audit markdown missing P3/P4 implementation-defect boundary line",
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
    expected_p5_direct_route_boundary = {
        "tokens": p5_direct_route_tokens,
        "checks": {
            "main_tex": {
                token: contains_normalized(main_tex, token) for token in p5_direct_route_tokens
            },
            "flat_tex": {
                token: contains_normalized(flat_tex, token) for token in p5_direct_route_tokens
            },
            "main_pdf_text": {
                token: contains_normalized(main_pdf_text, token) for token in p5_direct_route_tokens
            },
            "flat_pdf_text": {
                token: contains_normalized(flat_pdf_text, token) for token in p5_direct_route_tokens
            },
        },
        "all_tokens_present": True,
    }
    checks.check(
        audit.get("p5_direct_route_boundary") == expected_p5_direct_route_boundary,
        "P5 direct-route boundary token map stale",
    )
    checks.check(
        theorem_traceability.get("p5_direct_route_boundary_present")
        == audit.get("remaining_claim_boundary", {}).get("p5_direct_route_boundary_present")
        == proof_writing_card.get("p5_direct_route_boundary_present")
        == summary.get("p5_direct_route_boundary_present")
        == expected_p5_direct_route_boundary["all_tokens_present"]
        is True,
        "P5 direct-route boundary not propagated in traceability audit",
    )
    checks.check(
        "P5 direct-route boundary in main/flat TeX and PDF text: `True`." in audit_md,
        "audit markdown missing P5 direct-route boundary line",
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
    expected_proof_causality_table = {
        "tokens": proof_causality_table_tokens,
        "checks": {
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
        },
        "all_tokens_present": True,
    }
    checks.check(
        audit.get("proof_causality_table") == expected_proof_causality_table,
        "proof-causality rule token map stale",
    )
    checks.check(
        theorem_traceability.get("proof_causality_table_present")
        == audit.get("remaining_claim_boundary", {}).get("proof_causality_table_present")
        == proof_writing_card.get("proof_causality_table_present")
        == summary.get("proof_causality_table_present")
        == expected_proof_causality_table["all_tokens_present"]
        is True,
        "proof-causality table not propagated in traceability audit",
    )
    checks.check(
        "Proof causality in main/flat TeX and PDF text: `True`." in audit_md,
        "audit markdown missing proof-causality table line",
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
    expected_direct_route_anticircularity_table = {
        "tokens": direct_route_anticircularity_table_tokens,
        "checks": {
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
        },
        "all_tokens_present": True,
    }
    checks.check(
        audit.get("direct_route_anticircularity_table")
        == expected_direct_route_anticircularity_table,
        "direct-route anti-circularity table token map stale",
    )
    checks.check(
        theorem_traceability.get("direct_route_anticircularity_table_present")
        == audit.get("remaining_claim_boundary", {}).get(
            "direct_route_anticircularity_table_present"
        )
        == proof_writing_card.get("direct_route_anticircularity_table_present")
        == summary.get("direct_route_anticircularity_table_present")
        == expected_direct_route_anticircularity_table["all_tokens_present"]
        is True,
        "direct-route anti-circularity table not propagated in traceability audit",
    )
    checks.check(
        "Direct-route anti-circularity table in main/flat TeX and PDF text: `True`."
        in audit_md,
        "audit markdown missing direct-route anti-circularity table line",
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
    expected_p_interface_satisfaction_table = {
        "tokens": p_interface_satisfaction_tokens,
        "checks": {
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
        },
        "all_tokens_present": True,
    }
    checks.check(
        audit.get("p_interface_satisfaction_table")
        == expected_p_interface_satisfaction_table,
        "Assumptions and theorem scope token map stale",
    )
    checks.check(
        theorem_traceability.get("p_interface_satisfaction_table_present")
        == audit.get("remaining_claim_boundary", {}).get(
            "p_interface_satisfaction_table_present"
        )
        == proof_writing_card.get("p_interface_satisfaction_table_present")
        == summary.get("p_interface_satisfaction_table_present")
        == expected_p_interface_satisfaction_table["all_tokens_present"]
        is True,
        "Assumptions and theorem scope not propagated in traceability audit",
    )
    checks.check(
        "Assumptions and theorem scope in main/flat TeX and PDF text: `True`."
        in audit_md,
        "audit markdown missing theorem-interface satisfaction table line",
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
    expected_p7_residual_to_error_table = {
        "tokens": p7_residual_to_error_table_tokens,
        "checks": {
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
        },
        "all_tokens_present": True,
    }
    checks.check(
        audit.get("p7_residual_to_error_table")
        == expected_p7_residual_to_error_table,
        "Residual-to-error boundary token map stale",
    )
    checks.check(
        theorem_traceability.get("p7_residual_to_error_table_present")
        == audit.get("remaining_claim_boundary", {}).get(
            "p7_residual_to_error_table_present"
        )
        == proof_writing_card.get("p7_residual_to_error_table_present")
        == summary.get("p7_residual_to_error_table_present")
        == expected_p7_residual_to_error_table["all_tokens_present"]
        is True,
        "Residual-to-error boundary not propagated in traceability audit",
    )
    checks.check(
        "Residual-to-error boundary in main/flat TeX and PDF text: `True`."
        in audit_md,
        "audit markdown missing Residual-to-error boundary line",
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
    expected_theorem_use_rule = {
        "tokens": theorem_use_rule_tokens,
        "checks": {
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
        },
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
        "all_tokens_present": True,
    }
    checks.check(
        audit.get("theorem_use_rule") == expected_theorem_use_rule,
        "theorem-use rule token map stale",
    )
    checks.check(
        "Theorem-use rule `true` values are token-presence checks only" in audit_md,
        "proof-claim traceability audit missing theorem-use token semantics note",
    )
    checks.check(
        theorem_traceability.get("theorem_use_rule_present")
        == audit.get("remaining_claim_boundary", {}).get("theorem_use_rule_present")
        == proof_writing_card.get("theorem_use_rule_present")
        == summary.get("theorem_use_rule_present")
        == expected_theorem_use_rule["all_tokens_present"]
        is True,
        "theorem-use rule not propagated in traceability audit",
    )
    checks.check(
        "Auxiliary-evidence scope in main/flat TeX and PDF text: `True`." in audit_md,
        "audit markdown missing auxiliary-evidence scope line",
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
    expected_quantifier_domain_table = {
        "tokens": quantifier_domain_table_tokens,
        "checks": {
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
        },
        "all_tokens_present": True,
    }
    checks.check(
        audit.get("quantifier_domain_table") == expected_quantifier_domain_table,
        "quantifier/domain table token map stale",
    )
    checks.check(
        theorem_traceability.get("quantifier_domain_table_present")
        == audit.get("remaining_claim_boundary", {}).get("quantifier_domain_table_present")
        == proof_writing_card.get("quantifier_domain_table_present")
        == summary.get("quantifier_domain_table_present")
        == expected_quantifier_domain_table["all_tokens_present"]
        is True,
        "quantifier/domain table not propagated in traceability audit",
    )
    checks.check(
        "Quantifier/domain table in main/flat TeX and PDF text: `True`."
        in audit_md,
        "audit markdown missing quantifier/domain table line",
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
    expected_local_global_transfer_table = {
        "tokens": local_global_transfer_table_tokens,
        "checks": {
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
        },
        "all_tokens_present": True,
    }
    checks.check(
        audit.get("local_global_transfer_table")
        == expected_local_global_transfer_table,
        "local-to-global transfer table token map stale",
    )
    checks.check(
        theorem_traceability.get("local_global_transfer_table_present")
        == audit.get("remaining_claim_boundary", {}).get(
            "local_global_transfer_table_present"
        )
        == proof_writing_card.get("local_global_transfer_table_present")
        == summary.get("local_global_transfer_table_present")
        == expected_local_global_transfer_table["all_tokens_present"]
        is True,
        "local-to-global transfer table not propagated in traceability audit",
    )
    checks.check(
        "Local-to-global transfer table in main/flat TeX and PDF text: `True`."
        in audit_md,
        "audit markdown missing local-to-global transfer table line",
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
    expected_objective_completion_boundary = {
        "tokens": objective_completion_boundary_tokens,
        "checks": {
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
        },
        "all_tokens_present": True,
    }
    checks.check(
        audit.get("objective_completion_boundary") == expected_objective_completion_boundary,
        "objective-completion boundary token map stale",
    )
    checks.check(
        theorem_traceability.get("objective_completion_boundary_present")
        == audit.get("remaining_claim_boundary", {}).get(
            "objective_completion_boundary_present"
        )
        == proof_writing_card.get("objective_completion_boundary_present")
        == summary.get("objective_completion_boundary_present")
        == expected_objective_completion_boundary["all_tokens_present"]
        is True,
        "objective-completion boundary not propagated in traceability audit",
    )
    checks.check(
        "Objective-completion boundary in main/flat TeX and PDF text: `True`."
        in audit_md,
        "audit markdown missing objective-completion boundary line",
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
    expected_constant_dependency_table = {
        "tokens": constant_dependency_table_tokens,
        "checks": {
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
        },
        "all_tokens_present": True,
    }
    checks.check(
        audit.get("constant_dependency_table") == expected_constant_dependency_table,
        "constant-dependency table token map stale",
    )
    checks.check(
        theorem_traceability.get("constant_dependency_table_present")
        == audit.get("remaining_claim_boundary", {}).get(
            "constant_dependency_table_present"
        )
        == proof_writing_card.get("constant_dependency_table_present")
        == summary.get("constant_dependency_table_present")
        == expected_constant_dependency_table["all_tokens_present"]
        is True,
        "constant-dependency table not propagated in traceability audit",
    )
    checks.check(
        "Constant-dependency table in main/flat TeX and PDF text: `True`."
        in audit_md,
        "audit markdown missing constant-dependency table line",
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
    expected_theorem_dependency_consumption_table = {
        "tokens": theorem_dependency_consumption_table_tokens,
        "checks": {
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
        },
        "all_tokens_present": True,
    }
    checks.check(
        audit.get("theorem_dependency_consumption_table")
        == expected_theorem_dependency_consumption_table,
        "theorem dependency consumption table token map stale",
    )
    checks.check(
        theorem_traceability.get("theorem_dependency_consumption_table_present")
        == audit.get("remaining_claim_boundary", {}).get(
            "theorem_dependency_consumption_table_present"
        )
        == proof_writing_card.get("theorem_dependency_consumption_table_present")
        == summary.get("theorem_dependency_consumption_table_present")
        == expected_theorem_dependency_consumption_table["all_tokens_present"]
        is True,
        "theorem dependency consumption table not propagated in traceability audit",
    )
    checks.check(
        "Theorem input-output flow in main/flat TeX and PDF text: `True`."
        in audit_md,
        "audit markdown missing theorem dependency consumption table line",
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
    expected_branch_consistency_table = {
        "tokens": branch_consistency_table_tokens,
        "checks": {
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
        },
        "all_tokens_present": True,
    }
    checks.check(
        audit.get("branch_consistency_table") == expected_branch_consistency_table,
        "accepted-branch consistency table token map stale",
    )
    checks.check(
        theorem_traceability.get("branch_consistency_table_present")
        == audit.get("remaining_claim_boundary", {}).get("branch_consistency_table_present")
        == proof_writing_card.get("branch_consistency_table_present")
        == summary.get("branch_consistency_table_present")
        == expected_branch_consistency_table["all_tokens_present"]
        is True,
        "accepted-branch consistency table not propagated in traceability audit",
    )
    checks.check(
        "Accepted-branch consistency ledger in main/flat TeX and PDF text: `True`."
        in audit_md,
        "audit markdown missing accepted-branch consistency table line",
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
    expected_implementation_route_oracle_table = {
        "tokens": implementation_route_oracle_table_tokens,
        "checks": {
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
        },
        "all_tokens_present": True,
    }
    checks.check(
        audit.get("implementation_route_oracle_table")
        == expected_implementation_route_oracle_table,
        "implementation-route/oracle separation table token map stale",
    )
    checks.check(
        theorem_traceability.get("implementation_route_oracle_table_present")
        == audit.get("remaining_claim_boundary", {}).get(
            "implementation_route_oracle_table_present"
        )
        == proof_writing_card.get("implementation_route_oracle_table_present")
        == summary.get("implementation_route_oracle_table_present")
        == expected_implementation_route_oracle_table["all_tokens_present"]
        is True,
        "implementation-route/oracle separation table not propagated in traceability audit",
    )
    checks.check(
        "Implementation-route/certificate separation table in main/flat TeX and PDF text: `True`."
        in audit_md,
        "audit markdown missing implementation-route/oracle separation table line",
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
    expected_nonlinear_solver_scale_table = {
        "tokens": nonlinear_solver_scale_table_tokens,
        "checks": {
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
        },
        "all_tokens_present": True,
    }
    checks.check(
        audit.get("nonlinear_solver_scale_table")
        == expected_nonlinear_solver_scale_table,
        "nonlinear-solver scale table token map stale",
    )
    checks.check(
        theorem_traceability.get("nonlinear_solver_scale_table_present")
        == audit.get("remaining_claim_boundary", {}).get(
            "nonlinear_solver_scale_table_present"
        )
        == proof_writing_card.get("nonlinear_solver_scale_table_present")
        == summary.get("nonlinear_solver_scale_table_present")
        == expected_nonlinear_solver_scale_table["all_tokens_present"]
        is True,
        "nonlinear-solver scale table not propagated in traceability audit",
    )
    checks.check(
        "Nonlinear-solver scale conditions in main/flat TeX and PDF text: `True`."
        in audit_md,
        "audit markdown missing nonlinear-solver scale table line",
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
    expected_local_defect_decomposition_table = {
        "tokens": local_defect_decomposition_table_tokens,
        "checks": {
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
        },
        "all_tokens_present": True,
    }
    checks.check(
        audit.get("local_defect_decomposition_table")
        == expected_local_defect_decomposition_table,
        "local-defect decomposition rule token map stale",
    )
    checks.check(
        theorem_traceability.get("local_defect_decomposition_table_present")
        == audit.get("remaining_claim_boundary", {}).get(
            "local_defect_decomposition_table_present"
        )
        == proof_writing_card.get("local_defect_decomposition_table_present")
        == summary.get("local_defect_decomposition_table_present")
        == expected_local_defect_decomposition_table["all_tokens_present"]
        is True,
        "local-defect decomposition table not propagated in traceability audit",
    )
    checks.check(
        "Local-defect decomposition ledger in main/flat TeX and PDF text: `True`."
        in audit_md,
        "audit markdown missing local-defect decomposition table line",
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
    expected_theorem_output_scope_table = {
        "tokens": theorem_output_scope_table_tokens,
        "checks": {
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
        },
        "all_tokens_present": True,
    }
    checks.check(
        audit.get("theorem_output_scope_table")
        == expected_theorem_output_scope_table,
        "theorem output scope table token map stale",
    )
    checks.check(
        theorem_traceability.get("theorem_output_scope_table_present")
        == audit.get("remaining_claim_boundary", {}).get(
            "theorem_output_scope_table_present"
        )
        == proof_writing_card.get("theorem_output_scope_table_present")
        == summary.get("theorem_output_scope_table_present")
        == expected_theorem_output_scope_table["all_tokens_present"]
        is True,
        "theorem output scope table not propagated in traceability audit",
    )
    checks.check(
        "Theorem output scope table in main/flat TeX and PDF text: `True`."
        in audit_md,
        "audit markdown missing theorem output scope table line",
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
    expected_reporting_map_table = {
        "tokens": reporting_map_table_tokens,
        "checks": {
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
        },
        "all_tokens_present": True,
    }
    checks.check(
        audit.get("reporting_map_table") == expected_reporting_map_table,
        "reporting-map/norm-equivalence table token map stale",
    )
    checks.check(
        theorem_traceability.get("reporting_map_table_present")
        == audit.get("remaining_claim_boundary", {}).get("reporting_map_table_present")
        == proof_writing_card.get("reporting_map_table_present")
        == summary.get("reporting_map_table_present")
        == expected_reporting_map_table["all_tokens_present"]
        is True,
        "reporting-map/norm-equivalence table not propagated in traceability audit",
    )
    checks.check(
        "Reporting-map/norm-equivalence table in main/flat TeX and PDF text: `True`."
        in audit_md,
        "audit markdown missing reporting-map/norm-equivalence table line",
    )
    expected_theorem_conclusion_scope_guard = {
        "tokens": THEOREM_CONCLUSION_SCOPE_GUARD_TOKENS,
        "checks": {
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
        },
        "all_tokens_present": True,
    }
    checks.check(
        audit.get("theorem_conclusion_scope_guard") == expected_theorem_conclusion_scope_guard,
        "scope-of-conclusion statement token map stale",
    )
    checks.check(
        theorem_traceability.get("theorem_conclusion_scope_guard_present")
        == audit.get("remaining_claim_boundary", {}).get("theorem_conclusion_scope_guard_present")
        == proof_writing_card.get("theorem_conclusion_scope_guard_present")
        == summary.get("theorem_conclusion_scope_guard_present")
        == expected_theorem_conclusion_scope_guard["all_tokens_present"]
        is True,
        "scope-of-conclusion statement not propagated in traceability audit",
    )
    checks.check(
        "Scope-of-conclusion statement in main/flat TeX and PDF text: `True`."
        in audit_md,
        "audit markdown missing scope-of-conclusion statement line",
    )
    expected_proof_strength_certificate = {
        "tokens": PROOF_STRENGTH_CERTIFICATE_TOKENS,
        "checks": {
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
        },
        "all_tokens_present": True,
    }
    checks.check(
        audit.get("proof_strength_certificate") == expected_proof_strength_certificate,
        "proof-structure statement token map stale",
    )
    checks.check(
        theorem_traceability.get("proof_strength_certificate_present")
        == audit.get("remaining_claim_boundary", {}).get("proof_strength_certificate_present")
        == proof_writing_card.get("proof_strength_certificate_present")
        == summary.get("proof_strength_certificate_present")
        == expected_proof_strength_certificate["all_tokens_present"]
        is True,
        "proof-structure statement not propagated in traceability audit",
    )
    checks.check(
        "Proof-structure statement in main/flat TeX and PDF text: `True`."
        in audit_md,
        "audit markdown missing proof-structure statement line",
    )
    expected_full_residual_bridge = {
        "tokens": FULL_RESIDUAL_BRIDGE_TOKENS,
        "checks": {
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
        },
        "all_tokens_present": True,
    }
    checks.check(
        audit.get("full_residual_bridge") == expected_full_residual_bridge,
        "full 132-row residual-defect bridge token map stale",
    )
    checks.check(
        theorem_traceability.get("full_residual_bridge_present")
        == audit.get("remaining_claim_boundary", {}).get("full_residual_bridge_present")
        == proof_writing_card.get("full_residual_bridge_present")
        == summary.get("full_residual_bridge_present")
        == expected_full_residual_bridge["all_tokens_present"]
        is True,
        "full 132-row residual-defect bridge not propagated in traceability audit",
    )
    checks.check(
        "Full 132-row residual-defect bridge in main/flat TeX and PDF text: `True`."
        in audit_md,
        "audit markdown missing full 132-row residual-defect bridge line",
    )
    expected_route_exclusivity = {
        "tex_tokens": ROUTE_EXCLUSIVITY_TEX_TOKENS,
        "pdf_text_tokens": ROUTE_EXCLUSIVITY_PDF_TEXT_TOKENS,
        "checks": {
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
        },
        "all_tokens_present": True,
        "nonmixing_semantics": (
            "The accepted direct residual-value certificate and any separate "
            "primitive/Taylor certificate must be used as separate same-branch "
            "proof routes. The audit records presence only; it does not lower "
            "constants, remove P6, prove a P7 residual-to-error transfer theorem, or prove the primitive route."
        ),
    }
    checks.check(
        audit.get("route_exclusivity_boundary") == expected_route_exclusivity,
        "route-exclusivity nonmixing token map stale",
    )
    checks.check(
        theorem_traceability.get("route_exclusivity_boundary_present")
        == audit.get("remaining_claim_boundary", {}).get("route_exclusivity_boundary_present")
        == proof_writing_card.get("route_exclusivity_boundary_present")
        == summary.get("route_exclusivity_boundary_present")
        == audit.get("remaining_gate_scope", {}).get("route_exclusivity_boundary_present")
        == expected_route_exclusivity["all_tokens_present"]
        is True,
        "route-exclusivity nonmixing boundary not propagated in traceability audit",
    )
    checks.check(
        "Route-exclusivity nonmixing boundary in main/flat TeX and PDF text: `True`."
        in audit_md,
        "audit markdown missing route-exclusivity nonmixing boundary line",
    )
    expected_theorem_residual_certificate_exclusivity = {
        "tex_tokens": THEOREM_RESIDUAL_CERTIFICATE_EXCLUSIVITY_TEX_TOKENS,
        "pdf_text_tokens": THEOREM_RESIDUAL_CERTIFICATE_EXCLUSIVITY_PDF_TEXT_TOKENS,
        "checks": {
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
        },
        "all_tokens_present": True,
        "nonmixing_semantics": (
            "The theorem statement itself consumes only one residual-value "
            "certificate. A future primitive/Taylor certificate may replace "
            "the accepted direct certificate only by proving a new same-tuple "
            "132-row residual-value bound; it may not be appended to lower "
            "constants, remove P6, prove a P7 residual-to-error transfer theorem, or prove the primitive route."
        ),
    }
    checks.check(
        audit.get("theorem_residual_certificate_exclusivity")
        == expected_theorem_residual_certificate_exclusivity,
        "theorem residual-certificate exclusivity token map stale",
    )
    checks.check(
        theorem_traceability.get("theorem_residual_certificate_exclusivity_present")
        == audit.get("remaining_claim_boundary", {}).get(
            "theorem_residual_certificate_exclusivity_present"
        )
        == proof_writing_card.get("theorem_residual_certificate_exclusivity_present")
        == summary.get("theorem_residual_certificate_exclusivity_present")
        == audit.get("remaining_gate_scope", {}).get(
            "theorem_residual_certificate_exclusivity_present"
        )
        == expected_theorem_residual_certificate_exclusivity["all_tokens_present"]
        is True,
        "theorem residual-certificate exclusivity not propagated in traceability audit",
    )
    checks.check(
        "Theorem residual-certificate exclusivity in statement: `True`."
        in audit_md,
        "audit markdown missing theorem residual-certificate exclusivity line",
    )
    expected_intro_proof_hierarchy = {
        "tokens": INTRO_PROOF_HIERARCHY_TOKENS,
        "checks": {
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
        },
        "all_tokens_present": True,
    }
    checks.check(
        audit.get("intro_proof_hierarchy") == expected_intro_proof_hierarchy,
        "introduction proof hierarchy token map stale",
    )
    checks.check(
        theorem_traceability.get("intro_proof_hierarchy_present")
        == audit.get("remaining_claim_boundary", {}).get("intro_proof_hierarchy_present")
        == proof_writing_card.get("intro_proof_hierarchy_present")
        == summary.get("intro_proof_hierarchy_present")
        == expected_intro_proof_hierarchy["all_tokens_present"]
        is True,
        "introduction proof hierarchy not propagated in traceability audit",
    )
    checks.check(
        "Introduction proof route in main/flat TeX and PDF text: `True`."
        in audit_md,
        "audit markdown missing introduction proof route line",
    )

    for tex, label in [(main_tex, "main"), (flat_tex, "flat")]:
        for token in EXPECTED_LABELS:
            checks.check(token in tex, f"{label} manuscript missing proof label: {token}")
        for token in REQUIRED_BOUNDARY_TOKENS:
            checks.check(contains_normalized(tex, token), f"{label} manuscript missing proof boundary token: {token}")
        for index in range(1, 7):
            checks.check(f"D{index} &" in tex, f"{label} manuscript missing Newton-Euler obligation D{index}")
        for token in [
            "Row-level target map for the Newton--Euler weak-balance rows",
            r"\label{tab:newton-euler-row-target-map}",
            "Rows 24--26 and 30--32",
            "Rows 27--29 and 33--35",
            "Rows 68--70 and 74--76",
            "Rows 71--73 and 77--79",
            "Rows 112--114 and 118--120",
            "Rows 115--117 and 121--123",
            r"i_{\mathrm{row}}(s,\rho)=44s+24+\rho",
            "D1/D2 balance identities give zero dynamic residual on \\(Z_G\\)",
        ]:
            checks.check(contains_normalized(tex, token), f"{label} manuscript missing row target map token: {token}")
        for token in [
            "Dynamic-row residual-identity table",
            "Verified input",
            "Proof role and remaining non-use",
            "D5 direct-substitution residual certificate",
            "The direct stage-residual input is supplied by zero row-local dynamic",
            "D6 certificate independently proves the dynamic row ordering",
        ]:
            checks.check(contains_normalized(tex, token), f"{label} manuscript missing dynamic proof matrix token: {token}")
        checks.check(count_map(tex) == EXPECTED_PROOF_OBJECT_COUNTS, f"{label} proof object counts changed")

    main_source = audit.get("main_source", {})
    flat_source = audit.get("flat_source", {})
    checks.check(main_source.get("all_labels_present") is True, "main labels not recorded as present")
    checks.check(flat_source.get("all_labels_present") is True, "flat labels not recorded as present")
    checks.check(main_source.get("all_boundary_tokens_present") is True, "main boundary tokens not recorded as present")
    checks.check(flat_source.get("all_boundary_tokens_present") is True, "flat boundary tokens not recorded as present")
    checks.check(
        main_source.get("proof_object_counts") == EXPECTED_PROOF_OBJECT_COUNTS,
        "main proof object counts stale",
    )
    checks.check(
        flat_source.get("proof_object_counts") == EXPECTED_PROOF_OBJECT_COUNTS,
        "flat proof object counts stale",
    )
    checks.check(main_source.get("all_newton_euler_ids_present") is True, "main D1-D6 IDs not recorded")
    checks.check(flat_source.get("all_newton_euler_ids_present") is True, "flat D1-D6 IDs not recorded")
    checks.check(
        main_source.get("newton_euler_row_target_map_present") is True,
        "main Newton-Euler row-level target map not recorded",
    )
    checks.check(
        flat_source.get("newton_euler_row_target_map_present") is True,
        "flat Newton-Euler row-level target map not recorded",
    )
    checks.check(
        audit.get("newton_euler_row_target_map_present") is True,
        "top-level Newton-Euler row-level target map marker missing",
    )
    checks.check(
        audit.get("newton_euler_symbolic_target_schema")
        == newton_euler_symbolic_target.get("schema")
        == "newton-euler-symbolic-target-audit-v1",
        "Newton-Euler symbolic target audit schema not carried into traceability audit",
    )
    checks.check(
        audit.get("newton_euler_symbolic_target_status")
        == "row_level_symbolic_targets_extracted_dynamic_defect_proof_open",
        "Newton-Euler symbolic target audit status changed",
    )
    checks.check(
        audit.get("newton_euler_symbolic_target_rows")
        == newton_euler_symbolic_target.get("row_count")
        == 36,
        "Newton-Euler symbolic target row count changed",
    )
    checks.check(
        audit.get("newton_euler_symbolic_target_translational_rows")
        == newton_euler_symbolic_target.get("translational_row_count")
        == 18,
        "Newton-Euler translational target row count changed",
    )
    checks.check(
        audit.get("newton_euler_symbolic_target_rotational_rows")
        == newton_euler_symbolic_target.get("rotational_row_count")
        == 18,
        "Newton-Euler rotational target row count changed",
    )
    checks.check(
        audit.get("newton_euler_symbolic_target_inventory_complete") is True,
        "Newton-Euler symbolic target inventory marker changed",
    )
    checks.check(
        audit.get("newton_euler_obligation_coverage_matrix_complete")
        == newton_euler_symbolic_target.get("obligation_coverage_matrix", {}).get("coverage_matrix_complete")
        is True,
        "Newton-Euler obligation coverage matrix not carried into traceability audit",
    )
    checks.check(
        audit.get("newton_euler_row_obligation_links")
        == newton_euler_symbolic_target.get("obligation_coverage_matrix", {}).get("row_obligation_link_count")
        == 180,
        "Newton-Euler row-obligation link count changed",
    )
    checks.check(
        audit.get("newton_euler_rows_with_complete_obligation_sets")
        == newton_euler_symbolic_target.get("obligation_coverage_matrix", {}).get(
            "rows_with_complete_obligation_sets"
        )
        == 36,
        "Newton-Euler row obligation set coverage changed",
    )
    checks.check(
        audit.get("newton_euler_obligations_with_target_rows")
        == newton_euler_symbolic_target.get("obligation_coverage_matrix", {}).get("obligations_with_target_rows")
        == 6,
        "Newton-Euler obligations-with-target-rows count changed",
    )
    checks.check(
        audit.get("newton_euler_obligation_coverage_proof_closure_advanced") is False,
        "Newton-Euler obligation coverage must not close proof",
    )
    checks.check(
        audit.get("newton_euler_symbolic_defect_certificate_complete")
        == newton_euler_symbolic_defect_certificate.get("certificate_complete")
        is False,
        "Newton-Euler symbolic defect certificate must remain open",
    )
    newton_euler_defect_summary = newton_euler_symbolic_defect_certificate.get("summary", {})
    checks.check(
        audit.get("newton_euler_runtime_expression_structure_checked")
        == newton_euler_defect_summary.get("runtime_expression_structure_checked")
        is True,
        "Newton-Euler runtime expression structure audit not carried into traceability audit",
    )
    checks.check(
        audit.get("newton_euler_runtime_expression_structure_checked_rows")
        == newton_euler_defect_summary.get("runtime_expression_structure_checked_rows")
        == 36,
        "Newton-Euler runtime expression checked row count changed",
    )
    checks.check(
        audit.get("newton_euler_runtime_expression_structure_translational_rows")
        == newton_euler_defect_summary.get("runtime_expression_structure_translational_rows")
        == 18,
        "Newton-Euler runtime expression translational row count changed",
    )
    checks.check(
        audit.get("newton_euler_runtime_expression_structure_rotational_rows")
        == newton_euler_defect_summary.get("runtime_expression_structure_rotational_rows")
        == 18,
        "Newton-Euler runtime expression rotational row count changed",
    )
    checks.check(
        audit.get("newton_euler_runtime_template_instantiation_checked")
        == newton_euler_defect_summary.get("runtime_template_instantiation_checked")
        is True,
        "Newton-Euler runtime template instantiation marker changed",
    )
    checks.check(
        audit.get("newton_euler_runtime_template_instantiation_checked_rows")
        == newton_euler_defect_summary.get("runtime_template_instantiation_checked_rows")
        == 36,
        "Newton-Euler runtime template instantiation row count changed",
    )
    checks.check(main_source.get("dynamic_proof_closure_matrix_present") is True, "main dynamic proof closure matrix not recorded")
    checks.check(flat_source.get("dynamic_proof_closure_matrix_present") is True, "flat dynamic proof closure matrix not recorded")
    checks.check(
        audit.get("dynamic_proof_closure_matrix_present") is True,
        "dynamic proof closure matrix top-level marker missing",
    )
    checks.check(
        audit.get("dynamic_proof_closure_matrix_status") == "present_direct_substitution_closure_inputs",
        "dynamic proof closure matrix status changed",
    )

    closure_state = proof_closure.get("closure_state", {})
    solver_state = proof_closure.get("solver_state", {})
    checks.check(audit.get("proof_closure_state") == closure_state, "proof closure state stale")
    checks.check(audit.get("solver_state") == solver_state, "solver state stale")
    checks.check(closure_state.get("proof_gap_closed") is True, "proof gap should be closed by direct substitution")
    checks.check(
        closure_state.get("proof_gap_closed_scope")
        == "direct_residual_bridge_kantorovich_route_closed_primitive_taylor_conditional_schema_open",
        "proof gap closure scope changed",
    )
    checks.check(closure_state.get("dynamic_symbolic_oracle_complete") is False, "dynamic oracle unexpectedly closed")
    checks.check(
        closure_state.get("stage_residual_O_h7_implementation_defect_proved") is True,
        "stage residual defect proof should be closed by direct substitution",
    )
    checks.check(
        closure_state.get("pc2_closed_by_direct_substitution") is True,
        "direct-substitution PC2 closure missing",
    )
    checks.check(
        closure_state.get("primitive_lift_route_closed") is False,
        "primitive lift route should remain open",
    )
    checks.check(
        closure_state.get("eta_h_O_h7_solver_policy_evidence") is False,
        "eta_h solver-policy theorem unexpectedly closed",
    )
    checks.check(
        solver_state.get("finite_scaled_tolerance_probe_ok_rows") == 4,
        "finite scaled-tolerance probe ok rows changed",
    )
    checks.check(
        solver_state.get("finite_scaled_tolerance_probe_total_rows") == 4,
        "finite scaled-tolerance probe total rows changed",
    )
    checks.check(
        float(solver_state.get("finite_scaled_tolerance_probe_max_residual_over_h7", math.inf)) < 1.0e4,
        "finite scaled-tolerance probe max eta-h ratio exceeds c_eta",
    )
    checks.check(
        solver_state.get("finite_scaled_tolerance_trajectory_probe_ok_rows") == 4,
        "finite scaled-tolerance trajectory probe ok rows changed",
    )
    checks.check(
        solver_state.get("finite_scaled_tolerance_trajectory_probe_total_rows") == 4,
        "finite scaled-tolerance trajectory probe total rows changed",
    )
    checks.check(
        solver_state.get("finite_scaled_tolerance_trajectory_probe_total_steps_checked") == 30,
        "finite scaled-tolerance trajectory probe step count changed",
    )
    checks.check(
        float(solver_state.get("finite_scaled_tolerance_trajectory_probe_max_residual_over_h7", math.inf)) < 1.0e4,
        "finite scaled-tolerance trajectory probe max eta-h ratio exceeds c_eta",
    )
    checks.check(
        solver_state.get("finite_tolerance_regime_sweep_policy_count") == 3,
        "finite tolerance-regime policy count changed",
    )
    checks.check(
        solver_state.get("finite_tolerance_regime_sweep_total_rows") == 12,
        "finite tolerance-regime row count changed",
    )
    checks.check(
        solver_state.get("finite_tolerance_regime_sweep_total_steps") == 90,
        "finite tolerance-regime step count changed",
    )
    checks.check(
        solver_state.get("finite_h_scaled_tolerance_sweep_recorded") is True,
        "finite h-scaled tolerance-regime sweep marker missing",
    )
    checks.check(
        solver_state.get("finite_h_scaled_tolerance_sweep_policy_names") == ["scaled_h7_c1e4", "scaled_h8_c1e6"],
        "finite h-scaled tolerance-regime policy names changed",
    )
    checks.check(solver_state.get("finite_h_scaled_tolerance_sweep_rows") == 8, "finite h-scaled row count changed")
    checks.check(solver_state.get("finite_h_scaled_tolerance_sweep_steps") == 60, "finite h-scaled step count changed")
    checks.check(
        float(solver_state.get("finite_h_scaled_tolerance_sweep_velocity_order_floor", math.nan)) > 6.0,
        "finite h-scaled velocity order floor too small",
    )
    checks.check(
        solver_state.get("local_defect_bound_has_explicit_uniform_constant_sum") is True,
        "explicit local-defect constant-sum marker missing",
    )
    checks.check(
        solver_state.get("eta_h_constant_absorbed_into_local_defect_constant") is True,
        "eta_h absorption into local-defect constant marker missing",
    )
    checks.check(
        solver_state.get("local_global_transfer_has_explicit_reduced_grid_constant") is True,
        "local-to-global explicit reduced-grid constant marker missing",
    )
    checks.check(
        solver_state.get("local_global_gronwall_factor_formula")
        == "Gamma_s(T) = (exp(C_s T)-1)/C_s with limit T at C_s=0",
        "local-to-global Gronwall factor formula changed",
    )
    checks.check(
        solver_state.get("local_global_reduced_grid_constant_formula") == "C_red = C_loc Gamma_s(T)",
        "local-to-global reduced-grid constant formula changed",
    )
    checks.check(
        solver_state.get("qv_reporting_map_constant_distinct_from_residual_defect_constant") is True,
        "q/v reporting map constant is not distinguished from residual defect constant",
    )
    checks.check(
        solver_state.get("qv_reporting_constant_formula") == "C_qv = C_{\\mathcal R} C_red",
        "q/v reporting constant formula changed",
    )
    checks.check(
        solver_state.get("gauss_truncation_bound_has_explicit_uniform_constant") is True,
        "explicit Gauss truncation constant marker missing",
    )
    checks.check(
        solver_state.get("gauss_truncation_constant_uniform_on_compact_trajectory_tube") is True,
        "compact-trajectory-tube Gauss constant marker missing",
    )
    checks.check(
        solver_state.get("stage_residual_to_root_bound_has_explicit_constant") is True,
        "explicit stage residual-to-root constant marker missing",
    )
    checks.check(
        solver_state.get("stage_residual_to_root_constant_formula") == "C_Z = 2 M C_R",
        "stage residual-to-root formula changed",
    )
    checks.check(
        solver_state.get("stage_root_endpoint_perturbation_constant_formula") == "C_A = M_E C_Z",
        "stage-root endpoint perturbation formula changed",
    )
    checks.check(
        solver_state.get("accepted_root_existence_proved_by_stage_residual_lemma") is True,
        "accepted root existence is not marked as proved by stage-residual lemma",
    )
    checks.check(
        solver_state.get("accepted_root_existence_not_assumed_as_isolated_root_premise") is True,
        "accepted root existence is still treated as an isolated-root premise",
    )
    checks.check(
        solver_state.get("endpoint_closure_raw_defect_bound_has_explicit_constant") is True,
        "endpoint-closure raw-defect explicit constant marker missing",
    )
    checks.check(
        solver_state.get("endpoint_closure_raw_defect_constant_symbol") == "C_{E,raw}",
        "endpoint-closure raw-defect constant symbol changed",
    )
    checks.check(
        solver_state.get("endpoint_closure_perturbation_bound_has_explicit_constant") is True,
        "endpoint-closure perturbation explicit constant marker missing",
    )
    checks.check(
        solver_state.get("endpoint_closure_perturbation_constant_formula") == "C_E = 4 M_E^ri C_{E,raw}",
        "endpoint-closure perturbation constant formula changed",
    )
    checks.check(
        solver_state.get("newton_residual_to_stage_bound_has_explicit_constant") is True,
        "explicit Newton residual-to-stage constant marker missing",
    )
    checks.check(
        solver_state.get("newton_endpoint_output_map") == "P_h = C_h o E_h",
        "Newton endpoint-output map binding changed",
    )
    checks.check(
        solver_state.get("newton_endpoint_output_map_bound")
        == "||P_h(Ztilde_A)-P_h(Z_A)|| <= C_N eta_h",
        "Newton endpoint-output perturbation bound changed",
    )
    checks.check(
        solver_state.get("newton_endpoint_output_map_derivative_bound_includes_closure") is True,
        "Newton endpoint-output derivative bound does not include closure",
    )
    checks.check(
        solver_state.get("newton_endpoint_output_map_lipschitz_constant_symbol") == "M_N",
        "Newton endpoint-output Lipschitz constant symbol changed",
    )
    checks.check(
        solver_state.get("newton_residual_to_endpoint_perturbation_constant_formula") == "C_N = 2 M_A M_N",
        "Newton residual-to-endpoint constant formula changed",
    )
    checks.check(
        solver_state.get("newton_eta_h_scaled_endpoint_bound_has_explicit_constant") is True,
        "eta_h-scaled Newton endpoint explicit constant marker missing",
    )
    checks.check(
        solver_state.get("newton_eta_h_scaled_endpoint_bound_formula") == "C_N c_eta h^7",
        "eta_h-scaled Newton endpoint bound formula changed",
    )
    checks.check(
        solver_state.get("local_global_transfer_grid_point_error_required") is True,
        "same-initial-state reported-grid local-to-global transfer marker missing",
    )
    checks.check(
        solver_state.get("reported_time_grid_defined_by_tn_equals_nh") is True,
        "reported time-grid definition marker missing",
    )
    checks.check(
        solver_state.get("exact_final_time_divisibility_required") is False,
        "exact final-time divisibility should not be required",
    )
    checks.check(
        solver_state.get("reported_qv_error_bound_uses_same_reported_time_grid") is True,
        "same reported time-grid q/v transfer marker missing",
    )
    checks.check(
        solver_state.get("reported_qv_error_bound_is_grid_maximum") is True,
        "reported q/v grid-maximum marker missing",
    )
    theorem_assumptions = proof_closure.get("theorem_assumption_coverage", [])
    close_requirements = proof_closure.get("close_requirements", [])
    close_requirements_by_id = {item.get("id"): item for item in close_requirements}
    satisfied_assumption_ids = [
        item.get("id") for item in theorem_assumptions if item.get("satisfied_for_submission")
    ]
    retained_or_open_assumptions = [
        item for item in theorem_assumptions if not item.get("satisfied_for_submission")
    ]
    retained_or_open_assumption_ids = [item.get("id") for item in retained_or_open_assumptions]
    satisfied_close_requirement_ids = [
        item.get("id") for item in close_requirements if item.get("satisfied")
    ]
    unsatisfied_close_requirement_ids = [
        item.get("id") for item in close_requirements if not item.get("satisfied")
    ]
    checks.check(audit.get("theorem_assumption_count") == len(theorem_assumptions) == 7, "assumption count changed")
    checks.check(
        audit.get("satisfied_theorem_assumption_count")
        == sum(1 for item in theorem_assumptions if item.get("satisfied_for_submission"))
        == 1,
        "satisfied assumption count changed",
    )
    checks.check(
        audit.get("unsatisfied_theorem_assumption_count")
        == sum(1 for item in theorem_assumptions if not item.get("satisfied_for_submission"))
        == 6,
        "unsatisfied assumption count changed",
    )
    checks.check(
        audit.get("theorem_assumption_submission_satisfied_ids") == satisfied_assumption_ids == ["P5"],
        "satisfied theorem assumption IDs stale",
    )
    checks.check(
        audit.get("theorem_assumption_retained_or_open_ids")
        == retained_or_open_assumption_ids
        == ["P1", "P2", "P3", "P4", "P6", "P7"],
        "retained-interface/open-nonpromotion theorem-boundary IDs stale",
    )
    checks.check(audit.get("close_requirement_count") == len(close_requirements) == 4, "close requirement count changed")
    checks.check(audit.get("satisfied_close_requirement_count") == 4, "satisfied close requirement count changed")
    checks.check(
        audit.get("unsatisfied_close_requirement_count")
        == sum(1 for item in close_requirements if not item.get("satisfied"))
        == 0,
        "unsatisfied close requirement count changed",
    )
    checks.check(
        audit.get("satisfied_close_requirement_ids") == satisfied_close_requirement_ids == ["PC1", "PC2", "PC3", "PC4"],
        "satisfied close requirement IDs stale",
    )
    checks.check(
        audit.get("unsatisfied_close_requirement_ids") == unsatisfied_close_requirement_ids == [],
        "unsatisfied close requirement IDs stale",
    )
    remaining_boundary = audit.get("remaining_claim_boundary", {})
    checks.check(
        remaining_boundary.get("status") == "theorem_conditions_retained_not_submission_ready",
        "remaining claim boundary status changed",
    )
    checks.check(
        remaining_boundary.get("theorem_assumptions_total") == len(theorem_assumptions) == 7,
        "remaining claim boundary assumption count stale",
    )
    checks.check(
        remaining_boundary.get("submission_satisfied_count") == 1
        and remaining_boundary.get("submission_satisfied_ids") == satisfied_assumption_ids == ["P5"],
        "remaining claim boundary satisfied assumption IDs stale",
    )
    checks.check(
        remaining_boundary.get("retained_or_open_count") == 6
        and remaining_boundary.get("retained_or_open_ids")
        == retained_or_open_assumption_ids
        == ["P1", "P2", "P3", "P4", "P6", "P7"],
        "remaining claim boundary retained-interface/open-nonpromotion IDs stale",
    )
    checks.check(
        remaining_boundary.get("retained_or_open_assumptions") == retained_or_open_assumptions,
        "remaining claim boundary retained-interface/open-nonpromotion entries stale",
    )
    checks.check(
        remaining_boundary.get("retained_theorem_interface_count") == 5
        and remaining_boundary.get("retained_theorem_interface_ids")
        == ["P1", "P2", "P3", "P4", "P6"],
        "remaining claim boundary retained theorem-interface IDs stale",
    )
    checks.check(
        remaining_boundary.get("open_nonpromotion_boundary_count") == 1
        and remaining_boundary.get("open_nonpromotion_boundary_ids") == ["P7"],
        "remaining claim boundary open output-boundary IDs stale",
    )
    checks.check(
        [
            item.get("id")
            for item in remaining_boundary.get("retained_theorem_interface_assumptions", [])
        ]
        == ["P1", "P2", "P3", "P4", "P6"],
        "remaining claim boundary retained theorem-interface assumptions stale",
    )
    checks.check(
        [
            item.get("id")
            for item in remaining_boundary.get("open_nonpromotion_boundary_assumptions", [])
        ]
        == ["P7"],
        "remaining claim boundary open output-boundary assumptions stale",
    )
    checks.check(
        remaining_boundary.get("close_requirement_count") == len(close_requirements) == 4
        and remaining_boundary.get("satisfied_close_requirement_ids")
        == satisfied_close_requirement_ids
        == ["PC1", "PC2", "PC3", "PC4"]
        and remaining_boundary.get("unsatisfied_close_requirement_ids") == [],
        "remaining claim boundary close requirement IDs stale",
    )
    checks.check(
        remaining_boundary.get("eta_h_solver_policy_evidence_closed")
        == closure_state.get("eta_h_O_h7_solver_policy_evidence")
        is False,
        "remaining claim boundary eta_h evidence overclaimed",
    )
    checks.check(
        remaining_boundary.get("eta_h_theorem_condition_retained_for_pc3") is True,
        "remaining claim boundary PC3 theorem condition missing",
    )
    checks.check(
        remaining_boundary.get("residual_to_error_route_promoted") is False,
        "remaining claim boundary promoted residual-to-error route",
    )
    checks.check(
        remaining_boundary.get("source_policy_or_full_tfe_not_promoted") is True,
        "remaining claim boundary source-policy/full-TFE nonpromotion missing",
    )
    checks.check(
        remaining_boundary.get("does_not_change_proof_closure_state") is True,
        "remaining claim boundary state-change marker missing",
    )
    checks.check(
        remaining_boundary.get("manuscript_anchor_map_present")
        == expected_anchor_map["all_label_anchors_present"]
        is True,
        "remaining claim boundary manuscript anchors missing",
    )
    checks.check(
        remaining_boundary.get("theorem_assumption_anchor_map_present")
        == expected_anchor_map["all_theorem_assumption_anchors_present"]
        is True,
        "remaining claim boundary theorem-interface/output-boundary anchors missing",
    )
    checks.check(
        remaining_boundary.get("theorem_assumption_anchor_ids")
        == expected_anchor_map["theorem_assumption_anchor_ids"]
        == ["P1", "P2", "P3", "P4", "P5", "P6", "P7"],
        "remaining claim boundary theorem-assumption anchor IDs changed",
    )
    checks.check(
        remaining_boundary.get("global_submission_boundaries_retained")
        == [
            "full_source_policy_package_ready",
            "theorem_level_eta_h_solver_policy_evidence",
            "closed_residual_to_error_theorem_for_mechanism_rows",
        ],
        "remaining claim boundary global boundaries changed",
    )
    checks.check(
        "does not promote eta_h evidence, residual-to-error rows, source-policy rows, or full-TFE replacement"
        in remaining_boundary.get("reading_rule", ""),
        "remaining claim boundary reading rule missing no-promotion scope",
    )
    checks.check(
        "The theorem invocation consumes exactly one residual-value certificate"
        in remaining_boundary.get("reading_rule", "")
        and "same-tuple 132-row residual-value bound rather than being appended"
        in remaining_boundary.get("reading_rule", ""),
        "remaining claim boundary reading rule missing theorem certificate exclusivity",
    )
    checks.check(
        "Remaining claim boundary: `theorem_conditions_retained_not_submission_ready`; satisfied IDs `P5`; retained theorem-interface IDs `P1,P2,P3,P4,P6`; open output-boundary IDs `P7`."
        in audit_md,
        "traceability markdown missing remaining claim boundary summary",
    )
    checks.check(
        "Remaining claim boundary no-promotion flags: eta closure `False`; residual route promoted `False`; source-policy/full-TFE not promoted `True`."
        in audit_md,
        "traceability markdown missing remaining claim boundary no-promotion flags",
    )
    actual_anchor_map = audit.get("manuscript_anchor_map", {})
    expected_anchor_table_coverage = theorem_anchor_table_reference_coverage(main_tex, flat_tex)
    actual_anchor_table_coverage = audit.get("theorem_anchor_table_reference_coverage", {})
    checks.check(
        actual_anchor_map == expected_anchor_map,
        "manuscript anchor map stale",
    )
    checks.check(
        proof_closure.get("manuscript_anchor_map") == expected_anchor_map,
        "proof closure manuscript anchor map stale",
    )
    checks.check(
        actual_anchor_map == proof_closure.get("manuscript_anchor_map"),
        "traceability/proof closure anchor map mismatch",
    )
    checks.check(
        "Manuscript anchor map: `True`; label anchors `24`; theorem-interface/P7-output-boundary anchors `7`."
        in audit_md,
        "traceability markdown missing manuscript anchor map summary",
    )
    checks.check(
        "Theorem-interface/P7-output-boundary anchor map present: `True`; IDs `P1,P2,P3,P4,P5,P6,P7`."
        in audit_md,
        "traceability markdown missing theorem-assumption anchor map summary",
    )
    checks.check(
        "Reader-facing theorem-interface split: theorem interfaces `P1--P6`; P7 is an output nonclaim/residual-to-error boundary anchor, not a theorem premise."
        in audit_md,
        "traceability markdown missing reader-facing P1-P6/P7 split",
    )
    checks.check(
        "Legacy P7-output-boundary anchor count includes P7 only for traceability across residual tables; it does not promote P7 into the theorem-interface list."
        in audit_md,
        "traceability markdown missing legacy P7 anchor-count explanation",
    )
    checks.check(
        actual_anchor_table_coverage == expected_anchor_table_coverage,
        "theorem-assumption anchor table reference coverage stale",
    )
    checks.check(
        actual_anchor_table_coverage.get("all_references_present_main_and_flat") is True,
        "theorem-assumption anchor table does not reference all theorem-interface tables",
    )
    checks.check(
        audit.get("summary", {}).get("theorem_anchor_table_reference_coverage_present") is True
        and audit.get("remaining_claim_boundary", {}).get(
            "theorem_anchor_table_reference_coverage_present"
        )
        is True,
        "theorem-assumption anchor table coverage not propagated",
    )
    checks.check(
        "Theorem-interface and output-boundary anchors table reference coverage: `True`." in audit_md,
        "traceability markdown missing theorem-assumption anchor table coverage line",
    )
    checks.check("## Manuscript Anchors" in audit_md, "traceability markdown missing manuscript anchors table")
    checks.check("## Theorem Interface Boundary" in audit_md, "traceability markdown missing theorem interface boundary table")
    for assumption_id in ["P1", "P2", "P3", "P4", "P5", "P6", "P7"]:
        checks.check(f"| `{assumption_id}` |" in audit_md, f"traceability markdown missing assumption row {assumption_id}")
        checks.check(
            f"| `{assumption_id}` |" in audit_md
            and assumption_id in actual_anchor_map.get("theorem_assumption_anchor_map", {}),
            f"traceability markdown or JSON missing manuscript anchor row {assumption_id}",
        )
    checks.check(
        close_requirements_by_id.get("PC1", {}).get("satisfied") is True,
        "PC1 should be satisfied by D1/D2 balance identity closure",
    )
    checks.check(
        close_requirements_by_id.get("PC2", {}).get("satisfied") is True,
        "PC2 residual-value bridge should be satisfied",
    )
    checks.check(
        close_requirements_by_id.get("PC2", {}).get("satisfaction_mode")
        == "D5 same-branch residual-value certificate: 96-row O(h^7) non-dynamic certificate plus 36 dynamic zero rows at Z_G",
        "PC2 satisfaction mode changed",
    )
    checks.check(
        close_requirements_by_id.get("PC3", {}).get("satisfied") is True,
        "PC3 should be satisfied by explicit theorem condition retention",
    )
    checks.check(
        close_requirements_by_id.get("PC3", {}).get("satisfaction_mode")
        == "explicit_theorem_condition_retained_not_empirical_solver_evidence",
        "PC3 satisfaction mode changed",
    )
    checks.check(
        close_requirements_by_id.get("PC3", {}).get("display_status")
        == "traceable only by retained P6 theorem condition; solver-policy theorem not proved",
        "PC3 display status must keep solver-policy theorem open",
    )
    checks.check(
        close_requirements_by_id.get("PC4", {}).get("satisfied") is True,
        "PC4 should retain the transfer-scope exclusion",
    )
    checks.check(
        close_requirements_by_id.get("PC4", {}).get("satisfaction_mode")
        == "nonpromotion_boundary_retained_residual_to_error_theorem_open",
        "PC4 nonpromotion mode changed",
    )
    checks.check(
        close_requirements_by_id.get("PC4", {}).get("display_status")
        == "transfer-scope exclusion retained; residual-to-error theorem not closed",
        "PC4 display status must keep residual-to-error closure open",
    )
    checks.check(
        close_requirements_by_id.get("PC4", {}).get("nonpromotion_boundary_retained") is True,
        "PC4 residual-to-error exclusion marker missing",
    )
    checks.check(
        close_requirements_by_id.get("PC4", {}).get("residual_to_error_closed") is False,
        "PC4 residual-to-error theorem closure overclaimed",
    )
    checks.check(
        close_requirements_by_id.get("PC4", {}).get("residual_to_error_route_promoted") is False,
        "PC4 residual-to-error route promotion overclaimed",
    )
    checks.check(audit.get("newton_euler_open_obligation_count") == 1, "Newton-Euler open obligation count changed")
    checks.check(audit.get("newton_euler_closed_obligation_count") == 5, "Newton-Euler closed obligation count changed")
    checks.check(
        audit.get("newton_euler_closed_obligation_ids")
        == [
            "translational_balance_identity",
            "rotational_balance_identity",
            "multiplier_wrench_consistency",
            "smooth_force_lift_consistency",
            "symbolic_runtime_row_equivalence",
        ],
        "Newton-Euler closed obligation ids changed",
    )
    checks.check(audit.get("residual_to_error_blocking_obligations") == 7, "residual-to-error count changed")
    checks.check(audit.get("certified_non_dynamic_rows") == 96, "certified non-dynamic rows changed")
    checks.check(audit.get("active_direct_newton_euler_closed_rows") == 36, "active direct Newton-Euler closed rows changed")
    checks.check(audit.get("active_direct_newton_euler_open_rows") == 0, "active direct Newton-Euler open rows changed")
    checks.check(
        audit.get("active_direct_newton_euler_open_obligations") == 0,
        "active direct Newton-Euler open obligations changed",
    )
    checks.check(audit.get("open_dynamic_rows") == 36, "open dynamic rows changed")
    checks.check(
        audit.get("open_dynamic_rows_scope") == "symbolic_primitive_certificate_route_not_active_direct_pc2",
        "open dynamic row scope changed",
    )
    checks.check(audit.get("formula_row_ad_jacobian_probe_count") == 3, "AD Jacobian probe count changed")
    checks.check(
        audit.get("proof_evidence_matrix_mentions_open_symbolic_oracle") is True
        and "D5 dynamic symbolic defect proof remains open" in proof_evidence,
        "proof evidence matrix no longer records open symbolic oracle",
    )
    claim = audit.get("claim_boundary", {})
    primary_claim = claim_boundary.get("primary_claim", {})
    checks.check(
        claim.get("accepted_method") == primary_claim.get("accepted_method") == "Gauss6/FullVA",
        "accepted method changed",
    )
    checks.check(
        claim.get("accepted_method_order") == primary_claim.get("method_order_claim") == 6,
        "accepted method order changed",
    )
    checks.check(claim.get("full_tfe_stage_replacement") is False, "claim boundary overclaims full TFE replacement")
    blocker_statuses = {row.get("id"): row.get("status") for row in blocker_gate.get("blockers", [])}
    readiness_boundary = audit.get("readiness_boundary", {})
    remaining_gate_scope = audit.get("remaining_gate_scope", {})
    checks.check(
        readiness_boundary.get("narrowed_claim_b4_b6_b7_statuses")
        == {key: blocker_statuses.get(key) for key in ["B4", "B6", "B7"]}
        == {"B4": "closed", "B6": "closed", "B7": "closed"},
        "traceability narrowed-claim B4/B6/B7 boundary changed",
    )
    checks.check(
        readiness_boundary.get("global_submission_boundaries_retained")
        == [
            "full_source_policy_package_ready",
            "theorem_level_eta_h_solver_policy_evidence",
            "closed_residual_to_error_theorem_for_mechanism_rows",
        ],
        "traceability global submission boundary list changed",
    )
    proof_closure_remaining = proof_closure.get("remaining_gate_scope", {})
    checks.check(
        remaining_gate_scope.get("narrowed_claim_b4_b6_b7_statuses")
        == {key: blocker_statuses.get(key) for key in ["B4", "B6", "B7"]}
        == {"B4": "closed", "B6": "closed", "B7": "closed"},
        "traceability remaining-gate B4/B6/B7 boundary changed",
    )
    checks.check(
        remaining_gate_scope.get("b4_b6_b7_closed_elsewhere_under_narrowed_claim") is True,
        "traceability remaining-gate narrowed-claim closure marker changed",
    )
    checks.check(
        remaining_gate_scope.get("proof_claims_traceable_under_conditional_scope") is True,
        "traceability remaining-gate conditional traceability marker changed",
    )
    checks.check(
        remaining_gate_scope.get("direct_pc2_proof_gap_closed") is True
        and remaining_gate_scope.get("direct_residual_bridge_route_satisfied") is True
        and remaining_gate_scope.get("direct_pc2_proof_gap_closed")
        == proof_closure_remaining.get("direct_pc2_proof_gap_closed"),
        "traceability remaining-gate direct PC2 closure markers changed",
    )
    checks.check(
        remaining_gate_scope.get("proof_gap_closed_scope")
        == "direct_residual_bridge_kantorovich_route_closed_primitive_taylor_conditional_schema_open"
        and remaining_gate_scope.get("not_primitive_162_term_taylor_closure") is True
        and remaining_gate_scope.get("primitive_taylor_route_closed") is False
        and remaining_gate_scope.get("actual_taylor_bounds_proved") == 0
        and remaining_gate_scope.get("open_taylor_bound_terms") == 162
        and remaining_gate_scope.get("terms_with_open_primitive_blockers") == 162
        and remaining_gate_scope.get("open_primitive_assumption_count") == 5
        and remaining_gate_scope.get("open_primitive_count") == 5
        and remaining_gate_scope.get("route_exclusivity_boundary_present") is True
        and remaining_gate_scope.get("theorem_residual_certificate_exclusivity_present")
        is True
        and remaining_gate_scope.get("not_primitive_162_term_taylor_closure")
        == strict_direct_standard.get("not_primitive_162_term_taylor_closure")
        and remaining_gate_scope.get("primitive_taylor_route_closed")
        == strict_direct_standard.get("primitive_taylor_route_closed")
        and remaining_gate_scope.get("actual_taylor_bounds_proved")
        == strict_direct_standard.get("primitive_taylor_actual_bounds_proved")
        and remaining_gate_scope.get("open_taylor_bound_terms")
        == strict_direct_standard.get("primitive_taylor_open_bound_terms"),
        "traceability remaining-gate Taylor/primitive open-route guard changed",
    )
    checks.check(
        remaining_gate_scope.get("dynamic_symbolic_oracle_complete") is False,
        "traceability remaining-gate dynamic symbolic oracle unexpectedly closed",
    )
    checks.check(
        remaining_gate_scope.get("eta_h_O_h7_solver_policy_evidence") is False
        and remaining_gate_scope.get("eta_h_theorem_condition_retained_for_pc3") is True,
        "traceability remaining-gate eta_h boundary changed",
    )
    checks.check(
        remaining_gate_scope.get("accepted_residual_to_error_theorem") is False
        and remaining_gate_scope.get("residual_to_error_blocking_obligations") == 7
        and remaining_gate_scope.get("residual_to_error_route_promoted") is False,
        "traceability remaining-gate residual-to-error boundary changed",
    )
    checks.check(
        remaining_gate_scope.get("active_direct_newton_euler_open_obligations") == 0
        and remaining_gate_scope.get("symbolic_primitive_route_open_obligations") == 1,
        "traceability remaining-gate Newton-Euler obligation boundary changed",
    )
    checks.check(
        remaining_gate_scope.get("global_submission_boundaries_retained")
        == [
            "full_source_policy_package_ready",
            "theorem_level_eta_h_solver_policy_evidence",
            "closed_residual_to_error_theorem_for_mechanism_rows",
        ],
        "traceability remaining-gate global boundary list changed",
    )

    for token in [
        "Status: **conditional proof claims traceable; global proof-package submission not ready**.",
        "`submission_ready=false` is scoped to traceability/global proof-package readiness",
        "Theorem labels/boundary/mapped: `True/True/True`.",
        "Theorem reading guide present: `True`.",
        "Proof dependency/traceability/dynamic matrix: `True/True/True`.",
        "Primitive-route and residual scope boundaries: `True/True`.",
        "Eta condition/closure and fixed-tolerance proof: `True/False/False`.",
        "Residual/source-policy-full-TFE not promoted: `True/True`; no-state-change `True`.",
        "P-interface partition: P1, P2, and P3 are retained theorem interfaces; P6 is the retained solver-scale interface; P4's binding convention is retained while its 96-row non-dynamic row-local certificate is proved; P5 direct-route discharged; P7 output nonclaim/residual-to-error boundary.",
        "Reader-facing theorem-interface split: theorem interfaces `P1--P6`; P7 is an output nonclaim/residual-to-error boundary anchor, not a theorem premise.",
        "| id | status | retained theorem interface | proved row certificate | direct-route discharged | evidence boundary |",
        "| `P4` | `binding_interface_retained_96_row_certificate_proved` | `True` | `True` | `False` | 96 kinematic/lower-pair rows certified; 36 Newton-Euler rows excluded |",
        "P4 split reading rule: P4 remains a retained binding interface and also carries a proved 96-row non-dynamic row certificate.",
        "The `direct-route discharged` column is reserved for assumptions fully discharged as theorem inputs by themselves; P4 is consumed only after its proved 96-row certificate is assembled with P5's 36-row direct Newton--Euler certificate on the same accepted branch.",
        "Proof-writing boundary card: `conditional_theorem_traceable_direct_pc2_closed_global_boundaries_retained`; safe claim `conditional order-six theorem under retained P1, P2, and P3 theorem interfaces, the separate P6 solver-scale interface, and the P4 binding convention, with P4's proved 96-row non-dynamic row-local certificate and P5's direct Newton-Euler rows supplying one same-branch 132-row residual bridge; route-exclusivity forbids mixing direct and primitive/Taylor residual certificates to lower constants, remove P6, or prove a P7 residual-to-error transfer theorem; the theorem statement itself consumes only one residual-value certificate, so a future primitive/Taylor certificate may only replace the accepted direct certificate by proving a new same-tuple 132-row residual-value bound; P7 remains a separate output nonclaim/residual-to-error boundary`.",
        "Direct residual-bridge scope: `direct_residual_bridge_kantorovich_route_closed_primitive_taylor_conditional_schema_open`.",
        "Primitive/Taylor closure boundary: not 162-term closure `True`; route closed `False`; actual/open terms `0` / `162`; open primitive inputs `5`.",
        "Route-exclusivity nonmixing boundary in main/flat TeX and PDF text: `True`.",
        "Theorem residual-certificate exclusivity in statement: `True`.",
        "The theorem invocation consumes exactly one residual-value certificate; any future primitive/Taylor certificate must replace the accepted direct certificate by proving a new same-tuple 132-row residual-value bound rather than being appended to it.",
        "Proof-writing forbidden reader claims: `unconditional theorem without theorem-domain interfaces,eta_h solver-policy condition closed,fixed-tolerance runs as asymptotic proof,accepted residual-to-error transfer theorem for mechanism rows,source-policy/full-TFE package readiness,mixing direct and primitive-route residual certificates to lower constants, remove P6, or prove a P7 residual-to-error transfer theorem`.",
        "Theorem-interface and output-boundary anchors table reference coverage: `True`.",
        "Legacy P7-output-boundary anchor count includes P7 only for traceability across residual tables; it does not promote P7 into the theorem-interface list.",
        "Active direct row split: `132` closed / `0` active-open.",
        "Symbolic/primitive-route row split: `96` non-dynamic certified / `36` dynamic not certified by that route.",
        "Symbolic/primitive-route Newton-Euler open obligations: `1`.",
        "Active direct Newton-Euler open obligations: `0`.",
        "Symbolic/primitive open-row scope: `symbolic_primitive_certificate_route_not_active_direct_pc2`.",
        "Newton-Euler row-level target map present: `True`.",
        "Newton-Euler symbolic target rows: `36` total, `18/18` translational/rotational.",
        "Newton-Euler symbolic defect certificate complete: `False`.",
        "Newton-Euler obligation coverage matrix complete: `True`.",
        "Newton-Euler row-obligation links: `180`.",
        "Newton-Euler rows with complete obligation sets: `36`.",
        "Newton-Euler obligation coverage does not close the primitive symbolic-defect route: `True`; active direct PC2 residual-bridge slot is closed separately: `True`.",
        "Newton-Euler runtime expression structure checked/rows: `True` / `36`.",
        "Newton-Euler runtime expression structure translational/rotational rows: `18` / `18`.",
        "Newton-Euler runtime template instantiation checked/rows: `True` / `36`.",
        "Proof-route checks: `4` traceable, `0` blocked under conditional scope.",
        "Newton-Euler closed obligations: `5`.",
        "Dynamic-row residual-identity table present: `True`.",
        "Dynamic-row residual-identity table status: `present_direct_substitution_closure_inputs`.",
        "Residual-to-error blocking obligations: `7`.",
        "Dynamic symbolic oracle complete: `False`.",
        "Stage residual O(h^7) implementation defect proved: `True`.",
        "Finite scaled-tolerance probe rows/max eta-h ratio: `4/4` / `127.583723`.",
        "Finite scaled-tolerance trajectory probe rows/steps/max eta-h ratio: `4/4` / `30` / `210.890786`.",
        "Per-step branch-selected eta_h policy: `eta_h^tube <= c_eta h^7 on the compact proof tube; reported-grid eta_h^reported = max_{0<=n<N} eta_{h,n} is only its accepted branch-selected trajectory specialization`.",
        "Same reduced-chart initial state required: `True`.",
        "Gauss-predictor branch-selected Newton solves required: `True` / `True`.",
        "Arbitrary Newton initializations or remote roots select branch: `False` / `False`.",
        "Explicit Gauss truncation constant uniform on compact trajectory tube: `True` / `True`.",
        "Explicit stage residual-to-root and endpoint constants: `True` / `C_Z = 2 M C_R` / `C_A = M_E C_Z`.",
        "Accepted root existence proved by stage-residual lemma / not isolated-root premise: `True` / `True`.",
        "Explicit endpoint-closure raw-defect and perturbation constants: `True` / `C_{E,raw}` / `True` / `C_E = 4 M_E^ri C_{E,raw}`.",
        "Four-term local-defect constants uniform on compact tube / accepted steps: `True` / `True`.",
        "Newton error controlled by compact-tube eta_h envelope; reported-grid maximum is specialization: `True`.",
        "Explicit Newton residual-to-stage and endpoint-output constant: `True` / `P_h = C_h o E_h` / `||P_h(Ztilde_A)-P_h(Z_A)|| <= C_N eta_h` / `C_N = 2 M_A M_N`.",
        "Explicit eta_h-scaled Newton endpoint bound: `True` / `C_N c_eta h^7`.",
        "Explicit local-defect constant sum and eta_h absorption: `True` / `True`.",
        "Explicit local-to-global and q/v reporting constants: `True` / `Gamma_s(T) = (exp(C_s T)-1)/C_s with limit T at C_s=0` / `C_red = C_loc Gamma_s(T)` / `True` / `C_qv = C_{\\mathcal R} C_red`.",
        "Same-initial-state reported-grid local-to-global transfer and same-grid reported q/v maximum: `True` / `True` / `True`.",
        "Reported time grid t_n=n h and no exact final-time divisibility requirement: `True` / `False`.",
        "eta_h^tube <= c_eta h^7 solver-policy theorem: `False`.",
        "PC3 retained by eta_h theorem condition, not by solver-policy theorem proof: `True`.",
        "PC4 boundary retained by residual-to-error boundary, not by transfer-theorem closure: `True`.",
        "Submission-ready scope: `traceability_global_proof_boundary_not_narrowed_claim_package_decision`.",
        "Narrowed-claim B4/B6/B7 subcheck statuses (narrowed-only; not source-policy row closure): `closed/closed/closed`.",
        "Remaining global submission boundaries: `full_source_policy_package_ready,theorem_level_eta_h_solver_policy_evidence,closed_residual_to_error_theorem_for_mechanism_rows`.",
        "Narrowed-claim B4/B6/B7 subcheck closed elsewhere while source-policy rows remain open: `True`.",
        "Proof claims traceable under conditional scope: `True`.",
        "Direct PC2 residual-value bridge closed under retained theorem interfaces: `True`.",
        "Remaining-gate eta_h theorem condition retained for PC3: `True`.",
        "Remaining-gate residual-to-error blocking obligations: `7`.",
        "Remaining-gate residual-to-error route promoted: `False`.",
        "Remaining-gate active direct Newton-Euler open obligations: `0`.",
        "Remaining-gate symbolic/primitive-route open obligations: `1`.",
        "Submission ready: `False`.",
    ]:
        checks.check(token in audit_md, f"audit markdown missing token: {token}")

    if checks.errors:
        print("proof claim traceability audit validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("proof claim traceability audit validation: PASS")
    print("proof_labels_present=True")
    print("theorem_traceability=True")
    print("unsatisfied_close_requirements=0")
    print("active_direct_newton_euler_open_obligations=0")
    print("symbolic_primitive_newton_euler_open_obligations=1")
    print("direct_pc2_proof_gap_closed=True")
    print("legacy_proof_gap_closed=True")
    print("remaining_gate_traceability_claims_mapped=True")
    print("remaining_gate_eta_h_theorem_condition_retained=True")
    print("submission_ready=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
