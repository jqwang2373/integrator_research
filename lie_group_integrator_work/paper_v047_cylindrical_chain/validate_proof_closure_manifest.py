#!/usr/bin/env python3
"""Validate the proof-closure manifest."""

from __future__ import annotations

import json
import math
import re
import sys
from pathlib import Path


PAPER = Path(__file__).resolve().parent
from paper_paths import LATEX, package_path as manuscript_path
ROOT = PAPER.parent
V048 = ROOT / "v048_cross_paper_same_test_benchmarks" / "results"
MAIN_TEX = LATEX / "main_cmame.tex"
FLAT_TEX = LATEX / "cmame_submission_flat" / "main_cmame_submission.tex"

MANUSCRIPT_LABEL_TOKENS = {
    "regularity_assumption": r"\label{ass:regularity}",
    "endpoint_closure_lemma": r"\label{lem:endpoint-closure}",
    "fullva_stage_lift_lemma": r"\label{lem:fullva-stage-lift}",
    "newton_euler_obligation_table": r"\label{tab:newton-euler-obligations}",
    "newton_euler_row_target_map": r"\label{tab:newton-euler-row-target-map}",
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
    "dynamic_proof_closure_matrix": r"\label{tab:dynamic-proof-closure-matrix}",
    "d5_same_object_lift_instantiation_lemma": r"\label{lem:d5-same-object-lift-instantiation}",
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

THEOREM_BOUNDARY_TOKENS = {
    "branch_selected_map_statement": "accepted branch-selected \\method{} map",
    "compact_tube_eta_h_condition": r"\eta_h^{\rm tube}\le c_\eta h^7",
    "grid_point_order_six_statement": "Under these compact-branch, endpoint/stability, implementation-binding, and",
    "fixed_tolerance_exclusion": "fixed production tolerances used in",
    "dense_sparse_backend_exclusion": "dense/sparse backend",
}

THEOREM_READING_GUIDE_TOKENS = {
    "heading": "Theorem reading guide",
    "four_layers": "The theorem below has four layers",
    "domain_layer": "P1, P2, P3, and P6 fix the domain",
    "residual_layer": "P4 and P5 supply the proved residual data",
    "row_split": "96 non-dynamic FullVA rows",
    "dynamic_rows": "36 Newton--Euler rows vanish",
    "conclusion_layer": "single \\(132\\)-row residual bridge",
    "output_scope_layer": "the reporting map converts that bound only",
    "output_nonclaims": "residual, reaction, multiplier, constraint-output, source-policy, and",
    "non_inputs": "are outside these four layers",
    "downstream_diagnostics": "are therefore conditional auxiliary implications",
    "no_backward_reading": "cannot be read backward",
}

PROOF_TRACEABILITY_TOKENS = {
    "reader_facing_dependency_graph": "The proof dependencies used by the theorem are:",
    "primitive_lane_not_pc2_input": "not an input to the PC2 stage-residual condition",
    "finite_solver_probes_attach_only_to_p6": "attach only to P6",
    "residual_tables_recorded_only_as_open_p7_interface_diagnostics": "recorded only as diagnostics for the open P7 residual-to-error boundary",
    "residual_to_error_nonpromotion": "No residual-to-error transfer theorem is accepted for residual-only mechanism",
    "conditional_theorem_reading": "is therefore a conditional",
}

THEOREM_USE_RULE_TOKENS = [
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
    "source-policy/full-\\tfe{} readiness",
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
    "primitive-obligation implication for D5",
    "only as a conditional implication under those five still-open primitive",
    "not an accepted primitive-route closure",
    "PC2 input",
    "Non-vacuity/admissibility note",
    "local same-branch domain of applicability",
    "not the error estimate itself",
    "They do not assume the \\(O(h^7)\\) local defect",
    "Same-object proof invariant",
    "same transition index",
    "same fixed proof norm",
    "not assembled from different runs",
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
    "The implication direction is fixed throughout",
    "stage-row defect on \\(Z_G\\)",
    "inferred backward",
    "proved 132-row direct residual bridge",
    "global grid bound by the stability/tube-retention transfer",
    "unconditional source-policy result",
]

CONSTANT_DEPENDENCY_LEDGER_TOKENS = [
    "Constant-dependency table",
    "Constant-dependency rule",
    "Explicit non-dependencies",
    "compact-tube constants only",
    "h-sweep",
    "solver tolerance table",
    "source-policy comparison",
    "residual/reaction table",
    "local reproducibility record",
    "P6 is the retained theorem-level solver-policy condition",
    "P7 output nonclaim/residual-to-error boundary",
    "source-policy readiness",
    "full-TFE readiness",
    "Same-object proof invariant",
    "same transition index",
    "same fixed proof norm",
    "not assembled from different runs",
]

THEOREM_DEPENDENCY_CONSUMPTION_LEDGER_TOKENS = [
    "Theorem input-output flow",
    "Theorem input-output flow",
    "First consumed by",
    "Later theorem output",
    "P1/P2",
    "P3/P4",
    "P5 supplies",
    "P6 enters only through",
    "P7 is recorded only in the exclusion column",
    "implemented residual path",
    "transfer-scope exclusion",
    "displayed inputs record",
    "theorem inputs and explicit exclusions only",
    "theorem-level solver-policy theorem",
    "residual-to-error promotion",
    "source-policy readiness",
    "reproducibility package readiness claims",
]

THEOREM_OUTPUT_SCOPE_LEDGER_TOKENS = [
    "Theorem output scope",
    "Theorem output scope rule",
    "Output layer",
    "Proven statement",
    "Proof source",
    "Explicit non-output",
    "One-step accepted",
    "Same-initial-state reduced grid",
    "reported grid",
    "Method-order",
    "sentence",
    "branch-selected one-step",
    "reported-grid",
    "same-initial-state reported-grid order-six sentence",
    "Order six in the same-initial-state reported-grid sense",
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
    "full source-policy reproduction",
    "fixed-tolerance asymptotic proof",
]

QUANTIFIER_DOMAIN_LEDGER_TOKENS = [
    "Quantifier/domain table",
    "Quantifier/domain rule",
    "Quantifier layer",
    "What is fixed or quantified",
    "Valid domain",
    "Explicit exclusions",
    "Fixed proof data",
    "all retained-tube states",
    "any reported grid",
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
]

LOCAL_GLOBAL_TRANSFER_LEDGER_TOKENS = [
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
    "First-exit bootstrap domain",
    "first possible exit index",
    "after the Gronwall constant",
    "not assume global tube retention as the conclusion",
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

REPORTING_MAP_LEDGER_TOKENS = [
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
    "local reporting-map consequence",
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

PROOF_CAUSALITY_LEDGER_TOKENS = [
    "Proof causality",
    "Proof-causality rule",
    "Mathematical input",
    "Consumed before",
    "Allowed source",
    "Explicit non-source",
    "substitution certificate is evaluated on the lifted Gauss stage",
    "before the local perturbation argument",
    "local defect bound is established before",
    "reporting map is used",
    "reduced-chart grid estimate",
    "downstream diagnostics or reproducibility-boundary evidence",
    "do not feed PC2",
    "theorem-level solver-policy theorem",
    "residual-to-error transfer theorem",
    "source-policy readiness",
    "full-TFE readiness",
]

BRANCH_CONSISTENCY_LEDGER_TOKENS = [
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
    "First-exit/P6 separation",
    "scaled residual part is not supplied by first exit",
    "remains the retained P6 hypothesis",
    "remote-chart equivalence",
    "arbitrary Newton-root selection",
    "global nonlinear solver uniqueness",
    "terminal-time error",
    "source-policy reproduction",
]

LOCAL_DEFECT_DECOMPOSITION_LEDGER_TOKENS = [
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
    "proof residual norm",
    "root norm",
    "fixed 132-row residual norm",
    "residual norm to the local stage-root norm",
    "endpoint norm",
    "endpoint-output map",
    "local endpoint-closure Lipschitz factor",
    "reduced-chart one-step norm",
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
    "Algorithm-order consistency",
    "computes the inexact stage iterate",
    "same implemented output order",
    "exact-root reference",
    "not a reordered algorithm",
    "two already endpoint-closed outputs",
    "never mixes an unclosed inexact endpoint with a closed exact endpoint",
]

DIRECT_ROUTE_ANTICIRCULARITY_LEDGER_TOKENS = [
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
    "theorem conclusion does not justify row identities",
    "residual/reaction tables",
    "not sources for D5",
    "does not prove P1/P2/P6/P7",
    "dynamic symbolic oracle",
    "primitive/Taylor route",
    "reproducibility package readiness evidence",
]

IMPLEMENTATION_ROUTE_ORACLE_LEDGER_TOKENS = [
    "Implementation-route/certificate separation table",
    "Implementation-route/certificate separation",
    "Route or certificate",
    "Theorem role",
    "Closed evidence",
    "Explicit non-use",
    "direct 132-row route",
    "Runtime formula/AD binding",
    "AD-expanded certificate",
    "remain diagnostic",
    "source-policy readiness",
    "implemented 132-row direct route",
    "stage-residual argument discharged by the direct route",
    "open primitive symbolic route",
    "non-active primitive symbolic-oracle completion record",
    "inputs to the theorem",
    "not contradictions",
    "direct D5 substitution closure",
    "not source-paper residual replacement",
    "reproducibility package readiness evidence",
]

B1_AD_EXPANDED_CLOSURE_LEDGER_TOKENS = [
    "AD-expanded implementation-path boundary",
    "closed certificate supplies",
    "AD-expanded implementation-path",
    "derivative-cell closure",
    "active direct residual route only",
    "does not close the primitive dynamic symbolic oracle",
    "primitive symbolic defect certificate",
    "source-paper residual replacement",
    "source-policy package readiness",
    "AD-expanded closure covers",
    "Newton--Euler derivative cells",
    "stage-residual proof route",
    "not a primitive symbolic defect certificate",
]

P_INTERFACE_SATISFACTION_LEDGER_TOKENS = [
    "Assumptions and theorem scope",
    "Proof-domain partition",
    "P5 is the only stage-local dynamic identity proved",
    "P1/P2/P3, the retained P4 binding side, and P6 describe the branch",
    "P7 remains a separate output nonclaim/residual-to-error boundary",
    "PC1--PC2 supply the local residual route under the retained P6",
    "do not turn domain conditions or the P7 boundary",
    "solver-policy theorem",
    "residual-to-error promotion",
    "source-policy rows",
    "reproducibility package readiness claims",
    "Route and interface separation table",
    "Route and interface separation",
    "PC1--PC2 local residual route together with the retained P6 solver-scale condition",
    "PC1 balance",
    "PC2 stage",
    "P6 is retained as the",
    "promotion is not used",
    "PC3 is interpreted only through the retained P6",
    "PC4 is recorded only as a retained transfer-scope exclusion",
    "PC4 is not a local-defect ingredient",
    "do not prove a solver-policy theorem",
    "do not prove a separate residual-to-error transfer theorem",
    "Retained/discharged input rule",
    "retained domain hypotheses",
    "stage-residual inputs from theorem-domain interfaces",
    "implemented 132-row direct route",
    "theorem does not merely assume",
    "consumes the implemented",
    "direct-route certificate",
    "formula residual at the lifted Gauss stage",
    "row ordering, and row scaling have been fixed",
    "discharged formula-residual input",
    "not an empirical residual fit",
]

P1P2_COMPACT_TUBE_BOUNDARY_TOKENS = [
    "P1/P2 compact-tube boundary",
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
    "not an assumption discharge",
    "lift regularity, compact-tube inverse",
    "compact-tube inverse",
    "endpoint-ball/right-inverse",
    "strong local residual inverse",
    "reproducibility package evidence",
    "does not prove P1/P2",
    "load-bearing P1/P2",
    "Compact-inverse quantifier discipline",
    "proof residual norm",
    "inverse constants",
    "rank probe, solver log",
    "retained P2 interface",
    "refitting the tube or inverse constant",
    "single compact tube",
    "independent radius and constants",
    "selection map fixed before the asymptotic limit",
    "same row/column chart",
    "uniform right inverses on the tube",
    "do not establish tube retention",
    "branch-jump exclusion",
    "cannot be fitted from observed convergence rows",
]

P3P4_IMPLEMENTATION_BOUNDARY_TOKENS = [
    "P3/P4 implementation-defect boundary",
    "P3/P4 implementation-defect boundary",
    "implemented direct-route residual/Jacobian path",
    "consumed by the same-branch direct residual bridge",
    "AD-expanded implementation-path certificate is closed",
    "primitive dynamic symbolic oracle",
    "primitive/Taylor symbolic-defect route",
    "residual reproduction",
    "kinematic and lower-pair rows; it does not by itself prove the full 132-row",
    "does not by itself prove the full 132-row stage residual",
    "separate 36-row D5 direct-substitution",
    "P3/P4 implementation-defect interface table",
    "P3/P4 implementation-defect boundary",
    "implementation-defect proof",
    "P3 runtime",
    "full-TFE readiness",
    "P4 96-row",
    "P4 handoff",
    "theorem-domain interfaces",
    "separate P5 direct Newton",
    "primitive dynamic symbolic oracle closure",
    "primitive/Taylor symbolic-defect route closure",
    "full 132-row stage",
    "does not close P3/P4",
    "promote P3/P4",
]

P5_DIRECT_ROUTE_BOUNDARY_TOKENS = [
    "P5 direct-route boundary",
    "P5 is proved only as a stage-local",
    "residual identity on the smooth Gauss lift",
    "supplies the 36 dynamic rows required by PC2",
    "D5 direct-substitution certificate",
    "does not assert residual control at the inexact Newton",
    "finite-run trajectories",
    "closed-loop mechanism residual tables",
    "source-policy rows",
    "residual-to-error promotion",
    "P5 direct-route satisfaction for",
    "P5 direct-route satisfaction rule",
    "displayed evidence is stage-local",
    "P5 stage-local",
    "P5 smooth-lift",
    "P5 handoff",
    "P5 scope/exclusion",
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

P6_SOLVER_SCOPE_BOUNDARY_TOKENS = [
    "P6 solver boundary",
    "P6/P7 non-closing arrow contract",
    "The P6 clause is an input-domain clause",
    "after the compact-tube branch",
    "The reverse arrow is not used",
    "does not prove the compact-tube P6 condition",
    "branch-scale consistency only",
    "P6 remains the explicit theorem",
    "branch-selected solver hypothesis",
    "do not prove a theorem-level solver-policy theorem",
    "do not turn fixed tolerances into an asymptotic proof",
    "do not assert global Newton",
    "remote-root selection",
    "P6 solver-policy interface table",
    "P6 solver-scale interpretation",
    "solver-policy assumption discharge",
    "finite one-step probes",
    "finite short-trajectory probes",
    "tolerance-regime sweeps",
    "AD Jacobian probes",
    "branch-selected Newton diagnostics",
    "P6 admissibility boundary",
    "residual-tolerance contract, not a restatement of the theorem conclusion",
    "computable 132-row residual norm",
    "dependent stopping rule",
    "before endpoint error or observed order slopes are measured",
    "Solver-envelope quantifier discipline",
    "P6 conditional-instantiation checkpoint",
    "operational sufficient instantiation",
    "proof norm, row scaling, branch rule",
    "same Gauss-predictor branch",
    "proof-norm stopping target",
    "reported-grid specialization",
    "sufficient instantiation rule",
    "not a hidden empirical discharge",
    "does not prove a theorem-level solver-policy theorem",
    "residual ratios",
    "remote-root exclusion",
    "before the step-size window",
    "before any residual logs are read",
    "changes the theorem hypothesis and the local-defect constant",
    "not a proof of P6",
    "residual norm, accepted branch",
    "Newton log",
    "tolerance sweep",
    "reported residual ratio",
    "post-hoc residual filtering",
    "cannot create an accepted transition",
    "Reported residual ratios",
    "cannot calibrate",
    "turn failed branch-scale rows into theorem inputs",
    "finite diagnostics into theorem-level solver-policy proof",
    "not inferred from observed slopes",
    "does not assume access to the exact trajectory",
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
]

NONLINEAR_SOLVER_SCALE_LEDGER_TOKENS = [
    "Nonlinear-solver scale conditions",
    "Nonlinear-solver scale rule",
    "Solver-scale object",
    "Theorem role",
    "evidence boundary",
    "Explicit non-use",
    "retained P6",
    "reported-grid maximum",
    "finite scaled-tolerance probes",
    "branch-scale diagnostics",
    "trajectory specializations",
    "one-step estimate is local",
    "reported-trajectory specialization",
    "not an additional local hypothesis",
    "load-bearing solver object",
    "compact-tube envelope",
    "not a fitted residual sequence",
    "Branch consistency and the retained P6 condition",
    "tube-envelope hypothesis",
    "independent solver-policy proof",
    "Solver-envelope quantifier discipline",
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

P7_RESIDUAL_TO_ERROR_OBLIGATION_LEDGER_TOKENS = [
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
    "dynamic residual identity",
    "residual consistency",
    "same-branch residual transfer operator",
    "\\(h\\)-independent constant \\(C_{\\rm P7}\\)",
    "P7 fixed-operator requirement",
    "fixed linearized inverse",
    "fixed before observed residual data",
    "not obtained by dividing",
    "measured trajectory errors",
    "stability or inf-sup control",
    "calibrated estimator",
    "reference-floor exclusion",
    "coarse-first campaign",
    "manuscript transfer theorem",
]


class Checks:
    def __init__(self) -> None:
        self.errors: list[str] = []

    def check(self, condition: bool, message: str) -> None:
        if not condition:
            self.errors.append(message)


def read_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def token_presence(source: str, tokens: dict[str, str]) -> dict[str, bool]:
    return {key: token in source for key, token in tokens.items()}


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
    return any(
        token_variant in text_variant
        for token_variant in token_variants
        for text_variant in text_variants
    )


def normalized_token_presence(source: str, tokens: list[str]) -> dict[str, bool]:
    return {token: contains_normalized(source, token) for token in tokens}


def normalized_named_token_presence(source: str, tokens: dict[str, str]) -> dict[str, bool]:
    return {key: contains_normalized(source, token) for key, token in tokens.items()}


def find_line_number(source: str, token: str) -> int | None:
    for index, line in enumerate(source.splitlines(), start=1):
        if token in line:
            return index
    return None


def manuscript_anchor_map(main_tex: str, flat_tex: str) -> dict:
    label_anchors = {}
    for key, label_token in MANUSCRIPT_LABEL_TOKENS.items():
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

    theorem_assumption_anchors = {}
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


def theorem_anchor_table_reference_coverage(main_tex: str, flat_tex: str) -> dict:
    label_token = r"\label{tab:theorem-assumption-anchor-ledger}"

    def source_coverage(tex: str) -> dict:
        table_block = extract_labeled_table_block(tex, label_token)
        rows = {}
        for assumption_id, references in THEOREM_ANCHOR_LEDGER_REFERENCES.items():
            row_text = extract_table_row(table_block, assumption_id)
            reference_checks = {reference: reference in row_text for reference in references}
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


def close_to(value: object, expected: float, tol: float = 1.0e-12) -> bool:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return False
    return math.isfinite(number) and abs(number - expected) <= tol


def main() -> int:
    checks = Checks()
    try:
        manifest = read_json(PAPER / "PROOF_CLOSURE_MANIFEST.json")
        manifest_md = read_text(PAPER / "PROOF_CLOSURE_MANIFEST.md")
        proof_contract = read_json(PAPER / "CMAME_PROOF_CONTRACT_GATE.json")
        proof_style = read_json(PAPER / "CMAME_PROOF_STYLE_AUDIT.json")
        blocker_gate = read_json(PAPER / "CMAME_BLOCKER_CLOSURE_GATE.json")
        dynamic_oracle = read_json(PAPER / "DYNAMIC_ROW_ORACLE_GATE.json")
        kinematic = read_json(PAPER / "KINEMATIC_ROW_DEFECT_CERTIFICATE.json")
        newton_euler = read_json(PAPER / "NEWTON_EULER_DEFECT_OBLIGATION_GATE.json")
        newton_euler_targets = read_json(PAPER / "NEWTON_EULER_SYMBOLIC_TARGET_AUDIT.json")
        newton_euler_virtual_work = read_json(PAPER / "NEWTON_EULER_VIRTUAL_WORK_WRENCH_AUDIT.json")
        newton_euler_certificate = read_json(PAPER / "NEWTON_EULER_SYMBOLIC_DEFECT_CERTIFICATE.json")
        newton_euler_closure_contract = read_json(PAPER / "NEWTON_EULER_DYNAMIC_ROW_CLOSURE_CONTRACT.json")
        b1_ad_expanded_closure = read_json(PAPER / "B1_AD_EXPANDED_SYMBOLIC_ORACLE_CLOSURE_CERTIFICATE.json")
        d5_readiness = read_json(PAPER / "D5_DYNAMIC_DEFECT_READINESS_AUDIT.json")
        d5_direct_substitution = read_json(PAPER / "D5_DYNAMIC_DIRECT_SUBSTITUTION_CERTIFICATE.json")
        d5_term_budget = read_json(PAPER / "D5_TAYLOR_TERM_BUDGET_AUDIT.json")
        d5_primitive_reduction = read_json(PAPER / "D5_PRIMITIVE_BOUND_REDUCTION_AUDIT.json")
        d5_p_tube_constants = read_json(PAPER / "D5_P_TUBE_CONSTANTS_AUDIT.json")
        d5_p_state_gap = read_json(PAPER / "D5_P_STATE_LIFT_GAP_AUDIT.json")
        d5_p_state_map_definition = read_json(PAPER / "D5_P_STATE_MAP_DEFINITION_AUDIT.json")
        d5_p_state_anticircularity = read_json(PAPER / "D5_P_STATE_ANTICIRCULARITY_AUDIT.json")
        d5_p_state_ps2_target = read_json(PAPER / "D5_P_STATE_PS2_WEIGHTED_TARGET_AUDIT.json")
        d5_p_state_ps2_kinematic = read_json(PAPER / "D5_P_STATE_PS2_KINEMATIC_BLOCK_CERTIFICATE.json")
        d5_p_state_ps2_lie_chart = read_json(PAPER / "D5_P_STATE_PS2_LIE_CHART_BINDING_AUDIT.json")
        d5_p_state_ps2_row_injection = read_json(PAPER / "D5_P_STATE_PS2_ROW_INJECTION_AUDIT.json")
        d5_p_state_ps2_nonlinear = read_json(PAPER / "D5_P_STATE_PS2_NONLINEAR_BINDING_AUDIT.json")
        d5_p_state_ps2_aggregate = read_json(PAPER / "D5_P_STATE_PS2_AGGREGATE_PROMOTION_AUDIT.json")
        d5_p_state_ps2_probe = read_json(PAPER / "D5_P_STATE_PS2_LINEARIZATION_PROBE.json")
        d5_p_state_ps3_conversion = read_json(PAPER / "D5_P_STATE_PS3_CONDITIONAL_CONVERSION_AUDIT.json")
        d5_p_state_ps3_actual_gap = read_json(PAPER / "D5_P_STATE_PS3_ACTUAL_INSTANTIATION_GAP_AUDIT.json")
        d5_p_state_ps3_h_acc_obstruction = read_json(PAPER / "D5_P_STATE_PS3_H_ACC_INPUT_OBSTRUCTION_AUDIT.json")
        d5_p_acc_map_definition = read_json(PAPER / "D5_P_ACC_MAP_DEFINITION_AUDIT.json")
        d5_p_acc_row_binding = read_json(PAPER / "D5_P_ACC_ROW_BINDING_AUDIT.json")
        d5_p_acc_independence = read_json(PAPER / "D5_P_ACC_INDEPENDENCE_AUDIT.json")
        d5_p_acc_lift_obstruction = read_json(PAPER / "D5_P_ACC_LIFT_OBSTRUCTION_AUDIT.json")
        d5_p_acc_pa2_weighted_inverse = read_json(PAPER / "D5_P_ACC_PA2_WEIGHTED_INVERSE_AUDIT.json")
        d5_p_lambda_interface = read_json(PAPER / "D5_P_LAMBDA_INTERFACE_AUDIT.json")
        d5_p_lambda_pl2_geometric_margin = read_json(PAPER / "D5_P_LAMBDA_PL2_GEOMETRIC_MARGIN_AUDIT.json")
        d5_p_lambda_d3_noncircularity = read_json(PAPER / "D5_P_LAMBDA_D3_NONCIRCULARITY_AUDIT.json")
        d5_p_lambda_pl4_rate_propagation = read_json(PAPER / "D5_P_LAMBDA_PL4_RATE_PROPAGATION_AUDIT.json")
        d5_p_geom_reduction = read_json(PAPER / "D5_P_GEOM_CHART_REDUCTION_AUDIT.json")
        d5_p_gyro_reduction = read_json(PAPER / "D5_P_GYRO_BILINEAR_REDUCTION_AUDIT.json")
        d5_primitive_closure_plan = read_json(PAPER / "D5_PRIMITIVE_OBLIGATION_CLOSURE_PLAN.json")
        d5_conditional_taylor_certificate = read_json(PAPER / "D5_CONDITIONAL_TAYLOR_CERTIFICATE.json")
        d5_open_primitive_gap = read_json(PAPER / "D5_OPEN_PRIMITIVE_GAP_AUDIT.json")
        numerical_scale = read_json(PAPER / "PROOF_NUMERICAL_SCALE_AUDIT.json")
        solver_scale = read_json(PAPER / "PROOF_SOLVER_SCALE_AUDIT.json")
        implementation = read_json(PAPER / "IMPLEMENTATION_PATH_AUDIT.json")
        residual_to_error = read_json(V048 / "closed_loop_residual_to_error_theorem_obligations.json")
        main_tex = read_text(MAIN_TEX)
        flat_tex = read_text(FLAT_TEX)
    except Exception as exc:  # noqa: BLE001
        print(f"proof closure manifest validation: FAIL\n- {exc}")
        return 1

    theorem = manifest.get("accepted_theorem", {})
    evidence = manifest.get("evidence_summary", {})
    closure = manifest.get("closure_state", {})
    strict_taylor = manifest.get("direct_residual_bridge_kantorovich_submission_standard", {})
    strict_direct = manifest.get("strict_direct_residual_bridge_submission_standard", {})
    oracle = manifest.get("oracle_state", {})
    solver = manifest.get("solver_state", {})
    theorem_boundary = manifest.get("theorem_statement_boundary", {})
    manuscript_traceability = manifest.get("manuscript_traceability", {})
    readiness_boundary = manifest.get("readiness_boundary", {})
    remaining_gate_scope = manifest.get("remaining_gate_scope", {})
    assumptions = {row.get("id"): row for row in manifest.get("theorem_assumption_coverage", [])}
    requirements = {row.get("id"): row for row in manifest.get("close_requirements", [])}
    obligation_ids = {row.get("id") for row in manifest.get("newton_euler_open_obligations", [])}
    blocker_statuses = {row.get("id"): row.get("status") for row in blocker_gate.get("blockers", [])}
    d5_summary = d5_readiness.get("summary", {})
    d5_direct_summary = d5_direct_substitution.get("summary", {})
    d5_term_summary = d5_term_budget.get("summary", {})
    d5_primitive_summary = d5_primitive_reduction.get("summary", {})
    d5_smooth_force_corollary = d5_primitive_reduction.get("conditional_row_level_corollaries", {}).get(
        "smooth_force_torque_lift", {}
    )
    d5_p_tube_summary = d5_p_tube_constants.get("summary", {})
    d5_p_state_summary = d5_p_state_gap.get("summary", {})
    d5_p_state_map_summary = d5_p_state_map_definition.get("summary", {})
    d5_p_state_anticircularity_summary = d5_p_state_anticircularity.get("summary", {})
    d5_p_state_ps2_target_summary = d5_p_state_ps2_target.get("summary", {})
    d5_p_state_ps2_kinematic_dims = d5_p_state_ps2_kinematic.get("dimensions", {})
    d5_p_state_ps2_kinematic_constants = d5_p_state_ps2_kinematic.get("constants", {})
    d5_p_state_ps2_lie_chart_constants = d5_p_state_ps2_lie_chart.get("constants", {})
    d5_p_state_ps2_probe_summary = d5_p_state_ps2_probe.get("summary", {})
    d5_p_state_ps3_conversion_summary = d5_p_state_ps3_conversion.get("summary", {})
    d5_p_state_ps3_h_acc_obstruction_summary = d5_p_state_ps3_h_acc_obstruction.get("summary", {})
    d5_p_acc_map_summary = d5_p_acc_map_definition.get("summary", {})
    d5_p_acc_row_binding_summary = d5_p_acc_row_binding.get("summary", {})
    d5_p_acc_independence_summary = d5_p_acc_independence.get("summary", {})
    d5_p_acc_pa2_weighted_inverse_summary = d5_p_acc_pa2_weighted_inverse.get("summary", {})
    d5_p_lambda_summary = d5_p_lambda_interface.get("summary", {})
    d5_p_lambda_pl2_summary = d5_p_lambda_pl2_geometric_margin.get("summary", {})
    d5_p_lambda_pl2_implication = d5_p_lambda_pl2_geometric_margin.get("conditional_pl2_implication", {})
    d5_p_lambda_d3_summary = d5_p_lambda_d3_noncircularity.get("summary", {})
    d5_p_lambda_pl4_summary = d5_p_lambda_pl4_rate_propagation.get("summary", {})
    d5_p_geom_summary = d5_p_geom_reduction.get("summary", {})
    d5_p_gyro_summary = d5_p_gyro_reduction.get("summary", {})
    d5_primitive_closure_summary = d5_primitive_closure_plan.get("summary", {})
    d5_conditional_taylor_summary = d5_conditional_taylor_certificate.get("summary", {})
    d5_open_primitive_summary = d5_open_primitive_gap.get("summary", {})
    main_label_presence = token_presence(main_tex, MANUSCRIPT_LABEL_TOKENS)
    flat_label_presence = token_presence(flat_tex, MANUSCRIPT_LABEL_TOKENS)
    main_theorem_boundary = token_presence(main_tex, THEOREM_BOUNDARY_TOKENS)
    flat_theorem_boundary = token_presence(flat_tex, THEOREM_BOUNDARY_TOKENS)
    main_theorem_reading_guide = normalized_named_token_presence(
        main_tex, THEOREM_READING_GUIDE_TOKENS
    )
    flat_theorem_reading_guide = normalized_named_token_presence(
        flat_tex, THEOREM_READING_GUIDE_TOKENS
    )
    main_proof_traceability = token_presence(main_tex, PROOF_TRACEABILITY_TOKENS)
    flat_proof_traceability = token_presence(flat_tex, PROOF_TRACEABILITY_TOKENS)
    main_theorem_use_rule = normalized_token_presence(main_tex, THEOREM_USE_RULE_TOKENS)
    flat_theorem_use_rule = normalized_token_presence(flat_tex, THEOREM_USE_RULE_TOKENS)
    main_constant_dependency_table = normalized_token_presence(
        main_tex, CONSTANT_DEPENDENCY_LEDGER_TOKENS
    )
    flat_constant_dependency_table = normalized_token_presence(
        flat_tex, CONSTANT_DEPENDENCY_LEDGER_TOKENS
    )
    main_theorem_dependency_consumption_table = normalized_token_presence(
        main_tex, THEOREM_DEPENDENCY_CONSUMPTION_LEDGER_TOKENS
    )
    flat_theorem_dependency_consumption_table = normalized_token_presence(
        flat_tex, THEOREM_DEPENDENCY_CONSUMPTION_LEDGER_TOKENS
    )
    main_theorem_output_scope_table = normalized_token_presence(
        main_tex, THEOREM_OUTPUT_SCOPE_LEDGER_TOKENS
    )
    flat_theorem_output_scope_table = normalized_token_presence(
        flat_tex, THEOREM_OUTPUT_SCOPE_LEDGER_TOKENS
    )
    main_quantifier_domain_table = normalized_token_presence(
        main_tex, QUANTIFIER_DOMAIN_LEDGER_TOKENS
    )
    flat_quantifier_domain_table = normalized_token_presence(
        flat_tex, QUANTIFIER_DOMAIN_LEDGER_TOKENS
    )
    main_local_global_transfer_table = normalized_token_presence(
        main_tex, LOCAL_GLOBAL_TRANSFER_LEDGER_TOKENS
    )
    flat_local_global_transfer_table = normalized_token_presence(
        flat_tex, LOCAL_GLOBAL_TRANSFER_LEDGER_TOKENS
    )
    main_reporting_map_table = normalized_token_presence(main_tex, REPORTING_MAP_LEDGER_TOKENS)
    flat_reporting_map_table = normalized_token_presence(flat_tex, REPORTING_MAP_LEDGER_TOKENS)
    main_proof_causality_table = normalized_token_presence(main_tex, PROOF_CAUSALITY_LEDGER_TOKENS)
    flat_proof_causality_table = normalized_token_presence(flat_tex, PROOF_CAUSALITY_LEDGER_TOKENS)
    main_branch_consistency_table = normalized_token_presence(
        main_tex, BRANCH_CONSISTENCY_LEDGER_TOKENS
    )
    flat_branch_consistency_table = normalized_token_presence(
        flat_tex, BRANCH_CONSISTENCY_LEDGER_TOKENS
    )
    main_local_defect_decomposition_table = normalized_token_presence(
        main_tex, LOCAL_DEFECT_DECOMPOSITION_LEDGER_TOKENS
    )
    flat_local_defect_decomposition_table = normalized_token_presence(
        flat_tex, LOCAL_DEFECT_DECOMPOSITION_LEDGER_TOKENS
    )
    main_direct_route_anticircularity_table = normalized_token_presence(
        main_tex, DIRECT_ROUTE_ANTICIRCULARITY_LEDGER_TOKENS
    )
    flat_direct_route_anticircularity_table = normalized_token_presence(
        flat_tex, DIRECT_ROUTE_ANTICIRCULARITY_LEDGER_TOKENS
    )
    main_implementation_route_oracle_table = normalized_token_presence(
        main_tex, IMPLEMENTATION_ROUTE_ORACLE_LEDGER_TOKENS
    )
    flat_implementation_route_oracle_table = normalized_token_presence(
        flat_tex, IMPLEMENTATION_ROUTE_ORACLE_LEDGER_TOKENS
    )
    main_b1_ad_expanded_closure_table = normalized_token_presence(
        main_tex, B1_AD_EXPANDED_CLOSURE_LEDGER_TOKENS
    )
    flat_b1_ad_expanded_closure_table = normalized_token_presence(
        flat_tex, B1_AD_EXPANDED_CLOSURE_LEDGER_TOKENS
    )
    main_p1p2_compact_tube_boundary = normalized_token_presence(
        main_tex, P1P2_COMPACT_TUBE_BOUNDARY_TOKENS
    )
    flat_p1p2_compact_tube_boundary = normalized_token_presence(
        flat_tex, P1P2_COMPACT_TUBE_BOUNDARY_TOKENS
    )
    main_p3p4_implementation_boundary = normalized_token_presence(
        main_tex, P3P4_IMPLEMENTATION_BOUNDARY_TOKENS
    )
    flat_p3p4_implementation_boundary = normalized_token_presence(
        flat_tex, P3P4_IMPLEMENTATION_BOUNDARY_TOKENS
    )
    main_p5_direct_route_boundary = normalized_token_presence(
        main_tex, P5_DIRECT_ROUTE_BOUNDARY_TOKENS
    )
    flat_p5_direct_route_boundary = normalized_token_presence(
        flat_tex, P5_DIRECT_ROUTE_BOUNDARY_TOKENS
    )
    main_p6_solver_scope_boundary = normalized_token_presence(
        main_tex, P6_SOLVER_SCOPE_BOUNDARY_TOKENS
    )
    flat_p6_solver_scope_boundary = normalized_token_presence(
        flat_tex, P6_SOLVER_SCOPE_BOUNDARY_TOKENS
    )
    main_nonlinear_solver_scale_table = normalized_token_presence(
        main_tex, NONLINEAR_SOLVER_SCALE_LEDGER_TOKENS
    )
    flat_nonlinear_solver_scale_table = normalized_token_presence(
        flat_tex, NONLINEAR_SOLVER_SCALE_LEDGER_TOKENS
    )
    main_p_interface_satisfaction_table = normalized_token_presence(
        main_tex, P_INTERFACE_SATISFACTION_LEDGER_TOKENS
    )
    flat_p_interface_satisfaction_table = normalized_token_presence(
        flat_tex, P_INTERFACE_SATISFACTION_LEDGER_TOKENS
    )
    main_p7_residual_to_error_obligation_table = normalized_token_presence(
        main_tex, P7_RESIDUAL_TO_ERROR_OBLIGATION_LEDGER_TOKENS
    )
    flat_p7_residual_to_error_obligation_table = normalized_token_presence(
        flat_tex, P7_RESIDUAL_TO_ERROR_OBLIGATION_LEDGER_TOKENS
    )
    expected_anchor_map = manuscript_anchor_map(main_tex, flat_tex)
    expected_anchor_table_coverage = theorem_anchor_table_reference_coverage(
        main_tex, flat_tex
    )
    expected_theorem_use_rule = {
        "tokens": THEOREM_USE_RULE_TOKENS,
        "checks": {
            "main_tex": main_theorem_use_rule,
            "flat_tex": flat_theorem_use_rule,
        },
        "check_semantics": (
            "The booleans under checks are normalized manuscript token-presence checks. "
            "A true value means the boundary phrase is present in that artifact; it does "
            "not promote residual-to-error transfer, solver-policy theorem, successful "
            "Newton logs, source-policy readiness, or full-TFE readiness to accepted "
            "theorem inputs."
        ),
        "nonpromotion_phrase_tokens": [
            "residual-to-error transfer theorem",
            "solver-policy theorem",
            "successful Newton logs",
            "source-policy/full-\\tfe{} readiness",
        ],
        "all_tokens_present_main_and_flat": all(main_theorem_use_rule.values())
        and all(flat_theorem_use_rule.values()),
    }
    expected_constant_dependency_table = {
        "tokens": CONSTANT_DEPENDENCY_LEDGER_TOKENS,
        "checks": {
            "main_tex": main_constant_dependency_table,
            "flat_tex": flat_constant_dependency_table,
        },
        "all_tokens_present_main_and_flat": all(main_constant_dependency_table.values())
        and all(flat_constant_dependency_table.values()),
    }
    expected_theorem_dependency_consumption_table = {
        "tokens": THEOREM_DEPENDENCY_CONSUMPTION_LEDGER_TOKENS,
        "checks": {
            "main_tex": main_theorem_dependency_consumption_table,
            "flat_tex": flat_theorem_dependency_consumption_table,
        },
        "all_tokens_present_main_and_flat": all(
            main_theorem_dependency_consumption_table.values()
        )
        and all(flat_theorem_dependency_consumption_table.values()),
    }
    expected_theorem_output_scope_table = {
        "tokens": THEOREM_OUTPUT_SCOPE_LEDGER_TOKENS,
        "checks": {
            "main_tex": main_theorem_output_scope_table,
            "flat_tex": flat_theorem_output_scope_table,
        },
        "all_tokens_present_main_and_flat": all(main_theorem_output_scope_table.values())
        and all(flat_theorem_output_scope_table.values()),
    }
    expected_quantifier_domain_table = {
        "tokens": QUANTIFIER_DOMAIN_LEDGER_TOKENS,
        "checks": {
            "main_tex": main_quantifier_domain_table,
            "flat_tex": flat_quantifier_domain_table,
        },
        "all_tokens_present_main_and_flat": all(main_quantifier_domain_table.values())
        and all(flat_quantifier_domain_table.values()),
    }
    expected_local_global_transfer_table = {
        "tokens": LOCAL_GLOBAL_TRANSFER_LEDGER_TOKENS,
        "checks": {
            "main_tex": main_local_global_transfer_table,
            "flat_tex": flat_local_global_transfer_table,
        },
        "all_tokens_present_main_and_flat": all(main_local_global_transfer_table.values())
        and all(flat_local_global_transfer_table.values()),
    }
    expected_reporting_map_table = {
        "tokens": REPORTING_MAP_LEDGER_TOKENS,
        "checks": {
            "main_tex": main_reporting_map_table,
            "flat_tex": flat_reporting_map_table,
        },
        "all_tokens_present_main_and_flat": all(main_reporting_map_table.values())
        and all(flat_reporting_map_table.values()),
    }
    expected_proof_causality_table = {
        "tokens": PROOF_CAUSALITY_LEDGER_TOKENS,
        "checks": {
            "main_tex": main_proof_causality_table,
            "flat_tex": flat_proof_causality_table,
        },
        "all_tokens_present_main_and_flat": all(main_proof_causality_table.values())
        and all(flat_proof_causality_table.values()),
    }
    expected_branch_consistency_table = {
        "tokens": BRANCH_CONSISTENCY_LEDGER_TOKENS,
        "checks": {
            "main_tex": main_branch_consistency_table,
            "flat_tex": flat_branch_consistency_table,
        },
        "all_tokens_present_main_and_flat": all(main_branch_consistency_table.values())
        and all(flat_branch_consistency_table.values()),
    }
    expected_local_defect_decomposition_table = {
        "tokens": LOCAL_DEFECT_DECOMPOSITION_LEDGER_TOKENS,
        "checks": {
            "main_tex": main_local_defect_decomposition_table,
            "flat_tex": flat_local_defect_decomposition_table,
        },
        "all_tokens_present_main_and_flat": all(
            main_local_defect_decomposition_table.values()
        )
        and all(flat_local_defect_decomposition_table.values()),
    }
    expected_direct_route_anticircularity_table = {
        "tokens": DIRECT_ROUTE_ANTICIRCULARITY_LEDGER_TOKENS,
        "checks": {
            "main_tex": main_direct_route_anticircularity_table,
            "flat_tex": flat_direct_route_anticircularity_table,
        },
        "all_tokens_present_main_and_flat": all(
            main_direct_route_anticircularity_table.values()
        )
        and all(flat_direct_route_anticircularity_table.values()),
    }
    expected_implementation_route_oracle_table = {
        "tokens": IMPLEMENTATION_ROUTE_ORACLE_LEDGER_TOKENS,
        "checks": {
            "main_tex": main_implementation_route_oracle_table,
            "flat_tex": flat_implementation_route_oracle_table,
        },
        "all_tokens_present_main_and_flat": all(
            main_implementation_route_oracle_table.values()
        )
        and all(flat_implementation_route_oracle_table.values()),
    }
    expected_b1_ad_expanded_closure_table = {
        "tokens": B1_AD_EXPANDED_CLOSURE_LEDGER_TOKENS,
        "checks": {
            "main_tex": main_b1_ad_expanded_closure_table,
            "flat_tex": flat_b1_ad_expanded_closure_table,
        },
        "all_tokens_present_main_and_flat": all(
            main_b1_ad_expanded_closure_table.values()
        )
        and all(flat_b1_ad_expanded_closure_table.values()),
    }
    expected_p_interface_satisfaction_table = {
        "tokens": P_INTERFACE_SATISFACTION_LEDGER_TOKENS,
        "checks": {
            "main_tex": main_p_interface_satisfaction_table,
            "flat_tex": flat_p_interface_satisfaction_table,
        },
        "all_tokens_present_main_and_flat": all(
            main_p_interface_satisfaction_table.values()
        )
        and all(flat_p_interface_satisfaction_table.values()),
    }
    expected_p1p2_compact_tube_boundary = {
        "tokens": P1P2_COMPACT_TUBE_BOUNDARY_TOKENS,
        "checks": {
            "main_tex": main_p1p2_compact_tube_boundary,
            "flat_tex": flat_p1p2_compact_tube_boundary,
        },
        "all_tokens_present_main_and_flat": all(
            main_p1p2_compact_tube_boundary.values()
        )
        and all(flat_p1p2_compact_tube_boundary.values()),
    }
    expected_p3p4_implementation_boundary = {
        "tokens": P3P4_IMPLEMENTATION_BOUNDARY_TOKENS,
        "checks": {
            "main_tex": main_p3p4_implementation_boundary,
            "flat_tex": flat_p3p4_implementation_boundary,
        },
        "all_tokens_present_main_and_flat": all(
            main_p3p4_implementation_boundary.values()
        )
        and all(flat_p3p4_implementation_boundary.values()),
    }
    expected_p5_direct_route_boundary = {
        "tokens": P5_DIRECT_ROUTE_BOUNDARY_TOKENS,
        "checks": {
            "main_tex": main_p5_direct_route_boundary,
            "flat_tex": flat_p5_direct_route_boundary,
        },
        "all_tokens_present_main_and_flat": all(
            main_p5_direct_route_boundary.values()
        )
        and all(flat_p5_direct_route_boundary.values()),
    }
    expected_p6_solver_scope_boundary = {
        "tokens": P6_SOLVER_SCOPE_BOUNDARY_TOKENS,
        "checks": {
            "main_tex": main_p6_solver_scope_boundary,
            "flat_tex": flat_p6_solver_scope_boundary,
        },
        "all_tokens_present_main_and_flat": all(
            main_p6_solver_scope_boundary.values()
        )
        and all(flat_p6_solver_scope_boundary.values()),
    }
    expected_nonlinear_solver_scale_table = {
        "tokens": NONLINEAR_SOLVER_SCALE_LEDGER_TOKENS,
        "checks": {
            "main_tex": main_nonlinear_solver_scale_table,
            "flat_tex": flat_nonlinear_solver_scale_table,
        },
        "all_tokens_present_main_and_flat": all(
            main_nonlinear_solver_scale_table.values()
        )
        and all(flat_nonlinear_solver_scale_table.values()),
    }
    expected_p7_residual_to_error_obligation_table = {
        "tokens": P7_RESIDUAL_TO_ERROR_OBLIGATION_LEDGER_TOKENS,
        "checks": {
            "main_tex": main_p7_residual_to_error_obligation_table,
            "flat_tex": flat_p7_residual_to_error_obligation_table,
        },
        "all_tokens_present_main_and_flat": all(
            main_p7_residual_to_error_obligation_table.values()
        )
        and all(flat_p7_residual_to_error_obligation_table.values()),
    }

    checks.check(manifest.get("schema") == "proof-closure-manifest-v1", "schema changed")
    checks.check(
        manifest.get("status") == "pc2_closed_by_direct_residual_bridge_global_boundary_retained",
        "status changed",
    )
    checks.check(manifest.get("submission_ready") is False, "manifest must not mark submission ready")
    checks.check(
        manifest.get("submission_ready_scope")
        == "proof_closure_global_boundary_not_narrowed_claim_package_decision",
        "submission-ready scope changed",
    )
    checks.check(manifest.get("proof_mode") == "conditional_consistency_transfer", "proof mode changed")
    checks.check(theorem_boundary.get("main_tex") == "main_cmame.tex", "theorem boundary main TeX path changed")
    checks.check(
        theorem_boundary.get("flat_tex") == "cmame_submission_flat/main_cmame_submission.tex",
        "theorem boundary flat TeX path changed",
    )
    checks.check(
        theorem_boundary.get("accepted_theorem_label") == "thm:g6fullva-order",
        "accepted theorem label changed",
    )
    checks.check(
        theorem_boundary.get("labels_present_main") == main_label_presence
        and theorem_boundary.get("labels_present_flat") == flat_label_presence
        and theorem_boundary.get("all_required_labels_present_main_and_flat") is True,
        "manuscript theorem/proof labels are not carried into proof closure",
    )
    checks.check(
        all(main_label_presence.values()) and all(flat_label_presence.values()),
        "main/flat manuscript proof labels missing",
    )
    checks.check(
        theorem_boundary.get("manuscript_anchor_label_count")
        == expected_anchor_map["label_anchor_count"]
        == 24,
        "theorem boundary manuscript anchor count changed",
    )
    checks.check(
        theorem_boundary.get("manuscript_anchor_map_present")
        == expected_anchor_map["all_label_anchors_present"]
        is True,
        "theorem boundary manuscript anchor map missing",
    )
    checks.check(
        theorem_boundary.get("theorem_assumption_anchor_count")
        == expected_anchor_map["theorem_assumption_anchor_count"]
        == 7,
        "theorem boundary assumption anchor count changed",
    )
    checks.check(
        theorem_boundary.get("theorem_assumption_anchor_map_present")
        == expected_anchor_map["all_theorem_assumption_anchors_present"]
        is True,
        "theorem boundary assumption anchor map missing",
    )
    checks.check(
        manifest.get("manuscript_anchor_map") == expected_anchor_map,
        "proof closure manuscript anchor map stale",
    )
    checks.check(
        manifest.get("theorem_anchor_table_reference_coverage")
        == expected_anchor_table_coverage,
        "proof closure theorem-anchor table reference coverage stale",
    )
    checks.check(
        manifest.get("theorem_anchor_table_reference_coverage", {}).get(
            "all_references_present_main_and_flat"
        )
        is True,
        "proof closure theorem-anchor table does not reference all theorem-interface tables",
    )
    checks.check(
        manifest.get("theorem_use_rule_boundary") == expected_theorem_use_rule,
        "proof closure theorem-use rule boundary stale",
    )
    checks.check(
        "For theorem-use rule maps, `true` means that the boundary phrase is present"
        in manifest_md,
        "proof-closure manifest missing theorem-use token semantics note",
    )
    checks.check(
        manifest.get("theorem_use_rule_boundary", {}).get("all_tokens_present_main_and_flat")
        is True,
        "proof closure theorem-use rule boundary missing main/flat tokens",
    )
    checks.check(
        manifest.get("constant_dependency_table_boundary")
        == expected_constant_dependency_table,
        "proof closure constant-dependency table interpretation stale",
    )
    checks.check(
        manifest.get("constant_dependency_table_boundary", {}).get(
            "all_tokens_present_main_and_flat"
        )
        is True,
        "proof closure constant-dependency table interpretation missing main/flat tokens",
    )
    checks.check(
        manifest.get("theorem_dependency_consumption_table_boundary")
        == expected_theorem_dependency_consumption_table,
        "proof closure theorem dependency-consumption table interpretation stale",
    )
    checks.check(
        manifest.get("theorem_dependency_consumption_table_boundary", {}).get(
            "all_tokens_present_main_and_flat"
        )
        is True,
        "proof closure theorem dependency-consumption table interpretation missing main/flat tokens",
    )
    checks.check(
        manifest.get("theorem_output_scope_table_boundary")
        == expected_theorem_output_scope_table,
        "proof closure theorem output-scope table interpretation stale",
    )
    checks.check(
        manifest.get("theorem_output_scope_table_boundary", {}).get(
            "all_tokens_present_main_and_flat"
        )
        is True,
        "proof closure theorem output-scope table interpretation missing main/flat tokens",
    )
    checks.check(
        manifest.get("quantifier_domain_table_boundary") == expected_quantifier_domain_table,
        "proof closure quantifier/domain table interpretation stale",
    )
    checks.check(
        manifest.get("quantifier_domain_table_boundary", {}).get(
            "all_tokens_present_main_and_flat"
        )
        is True,
        "proof closure quantifier/domain table interpretation missing main/flat tokens",
    )
    checks.check(
        manifest.get("local_global_transfer_table_boundary")
        == expected_local_global_transfer_table,
        "proof closure local-to-global transfer table interpretation stale",
    )
    checks.check(
        manifest.get("local_global_transfer_table_boundary", {}).get(
            "all_tokens_present_main_and_flat"
        )
        is True,
        "proof closure local-to-global transfer table interpretation missing main/flat tokens",
    )
    checks.check(
        manifest.get("reporting_map_table_boundary") == expected_reporting_map_table,
        "proof closure reporting-map table interpretation stale",
    )
    checks.check(
        manifest.get("reporting_map_table_boundary", {}).get(
            "all_tokens_present_main_and_flat"
        )
        is True,
        "proof closure reporting-map table interpretation missing main/flat tokens",
    )
    checks.check(
        manifest.get("proof_causality_table_boundary") == expected_proof_causality_table,
        "proof closure proof-causality table interpretation stale",
    )
    checks.check(
        manifest.get("proof_causality_table_boundary", {}).get(
            "all_tokens_present_main_and_flat"
        )
        is True,
        "proof closure proof-causality table interpretation missing main/flat tokens",
    )
    checks.check(
        manifest.get("branch_consistency_table_boundary") == expected_branch_consistency_table,
        "proof closure branch-consistency table interpretation stale",
    )
    checks.check(
        manifest.get("branch_consistency_table_boundary", {}).get(
            "all_tokens_present_main_and_flat"
        )
        is True,
        "proof closure branch-consistency table interpretation missing main/flat tokens",
    )
    checks.check(
        manifest.get("local_defect_decomposition_table_boundary")
        == expected_local_defect_decomposition_table,
        "proof closure local-defect decomposition table interpretation stale",
    )
    checks.check(
        manifest.get("local_defect_decomposition_table_boundary", {}).get(
            "all_tokens_present_main_and_flat"
        )
        is True,
        "proof closure local-defect decomposition table interpretation missing main/flat tokens",
    )
    checks.check(
        manifest.get("direct_route_anticircularity_table_boundary")
        == expected_direct_route_anticircularity_table,
        "proof closure direct-route anti-circularity table interpretation stale",
    )
    checks.check(
        manifest.get("direct_route_anticircularity_table_boundary", {}).get(
            "all_tokens_present_main_and_flat"
        )
        is True,
        "proof closure direct-route anti-circularity table interpretation missing main/flat tokens",
    )
    checks.check(
        manifest.get("implementation_route_oracle_table_boundary")
        == expected_implementation_route_oracle_table,
        "proof closure implementation-route/oracle table interpretation stale",
    )
    checks.check(
        manifest.get("implementation_route_oracle_table_boundary", {}).get(
            "all_tokens_present_main_and_flat"
        )
        is True,
        "proof closure implementation-route/oracle table interpretation missing main/flat tokens",
    )
    checks.check(
        manifest.get("b1_ad_expanded_closure_table_boundary")
        == expected_b1_ad_expanded_closure_table,
        "proof closure B1 AD-expanded closure table interpretation stale",
    )
    checks.check(
        manifest.get("b1_ad_expanded_closure_table_boundary", {}).get(
            "all_tokens_present_main_and_flat"
        )
        is True,
        "proof closure B1 AD-expanded closure table interpretation missing main/flat tokens",
    )
    checks.check(
        manifest.get("p1p2_compact_tube_boundary")
        == expected_p1p2_compact_tube_boundary,
        "proof closure P1/P2 compact-tube boundary stale",
    )
    checks.check(
        manifest.get("p1p2_compact_tube_boundary", {}).get(
            "all_tokens_present_main_and_flat"
        )
        is True,
        "proof closure P1/P2 compact-tube boundary missing main/flat tokens",
    )
    checks.check(
        manuscript_traceability.get("p1p2_compact_tube_boundary_present_main_and_flat")
        is True,
        "P1/P2 compact-tube boundary not propagated into manuscript traceability",
    )
    checks.check(
        manifest.get("p3p4_implementation_boundary")
        == expected_p3p4_implementation_boundary,
        "proof closure P3/P4 implementation-defect boundary stale",
    )
    checks.check(
        manifest.get("p3p4_implementation_boundary", {}).get(
            "all_tokens_present_main_and_flat"
        )
        is True,
        "proof closure P3/P4 implementation-defect boundary missing main/flat tokens",
    )
    checks.check(
        manuscript_traceability.get("p3p4_implementation_boundary_present_main_and_flat")
        is True,
        "P3/P4 implementation-defect boundary not propagated into manuscript traceability",
    )
    checks.check(
        manifest.get("p5_direct_route_boundary") == expected_p5_direct_route_boundary,
        "proof closure P5 direct-route boundary stale",
    )
    checks.check(
        manifest.get("p5_direct_route_boundary", {}).get(
            "all_tokens_present_main_and_flat"
        )
        is True,
        "proof closure P5 direct-route boundary missing main/flat tokens",
    )
    checks.check(
        manuscript_traceability.get("p5_direct_route_boundary_present_main_and_flat")
        is True,
        "P5 direct-route boundary not propagated into manuscript traceability",
    )
    checks.check(
        manifest.get("p6_solver_scope_boundary") == expected_p6_solver_scope_boundary,
        "proof closure P6 solver-scope boundary stale",
    )
    checks.check(
        manifest.get("p6_solver_scope_boundary", {}).get(
            "all_tokens_present_main_and_flat"
        )
        is True,
        "proof closure P6 solver-scope boundary missing main/flat tokens",
    )
    checks.check(
        manuscript_traceability.get("p6_solver_scope_boundary_present_main_and_flat")
        is True,
        "P6 solver-scope boundary not propagated into manuscript traceability",
    )
    checks.check(
        manifest.get("nonlinear_solver_scale_table_boundary")
        == expected_nonlinear_solver_scale_table,
        "proof closure nonlinear-solver scale table interpretation stale",
    )
    checks.check(
        manifest.get("nonlinear_solver_scale_table_boundary", {}).get(
            "all_tokens_present_main_and_flat"
        )
        is True,
        "proof closure nonlinear-solver scale table interpretation missing main/flat tokens",
    )
    checks.check(
        manuscript_traceability.get("nonlinear_solver_scale_table_present_main_and_flat")
        is True,
        "nonlinear-solver scale table not propagated into manuscript traceability",
    )
    checks.check(
        manifest.get("p_interface_satisfaction_table_boundary")
        == expected_p_interface_satisfaction_table,
        "proof closure theorem-interface satisfaction table interpretation stale",
    )
    checks.check(
        manifest.get("p_interface_satisfaction_table_boundary", {}).get(
            "all_tokens_present_main_and_flat"
        )
        is True,
        "proof closure theorem-interface satisfaction table interpretation missing main/flat tokens",
    )
    checks.check(
        manifest.get("p7_residual_to_error_obligation_table_boundary")
        == expected_p7_residual_to_error_obligation_table,
        "proof closure Residual-to-error boundary stale",
    )
    checks.check(
        manifest.get("p7_residual_to_error_obligation_table_boundary", {}).get(
            "all_tokens_present_main_and_flat"
        )
        is True,
        "proof closure Residual-to-error boundary missing main/flat tokens",
    )
    checks.check(
        manuscript_traceability.get(
            "p7_residual_to_error_obligation_table_present_main_and_flat"
        )
        is True,
        "Residual-to-error boundary not propagated into manuscript traceability",
    )
    checks.check(
        theorem_boundary.get("theorem_anchor_table_reference_coverage_present") is True,
        "theorem boundary theorem-anchor table coverage not propagated",
    )
    checks.check(
        theorem_boundary.get("theorem_boundary_tokens_main") == main_theorem_boundary
        and theorem_boundary.get("theorem_boundary_tokens_flat") == flat_theorem_boundary
        and theorem_boundary.get("conditional_theorem_boundary_present_main_and_flat") is True,
        "conditional theorem boundary tokens are not carried into proof closure",
    )
    checks.check(
        theorem_boundary.get("theorem_reading_guide_tokens_main") == main_theorem_reading_guide
        and theorem_boundary.get("theorem_reading_guide_tokens_flat") == flat_theorem_reading_guide
        and theorem_boundary.get("theorem_reading_guide_present_main_and_flat") is True,
        "theorem reading guide tokens are not carried into proof closure",
    )
    checks.check(
        all(main_theorem_boundary.values()) and all(flat_theorem_boundary.values()),
        "main/flat conditional theorem boundary tokens missing",
    )
    checks.check(
        all(main_theorem_reading_guide.values()) and all(flat_theorem_reading_guide.values()),
        "main/flat theorem reading guide tokens missing",
    )
    checks.check(
        theorem_boundary.get("accepted_method_order") == 6
        and theorem_boundary.get("accepted_local_defect_order") == 7
        and theorem_boundary.get("eta_h_theorem_condition_retained") is True
        and theorem_boundary.get("eta_h_solver_policy_evidence_closed") is False
        and theorem_boundary.get("fixed_tolerance_runs_are_asymptotic_proof") is False
        and theorem_boundary.get("does_not_promote_residual_to_error") is True
        and theorem_boundary.get("does_not_promote_source_policy_or_full_tfe") is True,
        "theorem statement boundary overclaims proof/source-policy closure",
    )
    checks.check(
        manuscript_traceability.get("main_tex") == "main_cmame.tex"
        and manuscript_traceability.get("flat_tex") == "cmame_submission_flat/main_cmame_submission.tex",
        "manuscript traceability paths changed",
    )
    checks.check(
        manuscript_traceability.get("proof_traceability_tokens_main") == main_proof_traceability
        and manuscript_traceability.get("proof_traceability_tokens_flat") == flat_proof_traceability
        and all(main_proof_traceability.values())
        and all(flat_proof_traceability.values()),
        "proof traceability tokens are not carried into proof closure",
    )
    checks.check(
        manuscript_traceability.get("proof_dependency_graph_present_main_and_flat") is True
        and manuscript_traceability.get("proof_traceability_table_present_main_and_flat") is True
        and manuscript_traceability.get("dynamic_proof_closure_matrix_present_main_and_flat") is True
        and manuscript_traceability.get("residual_to_error_nonpromotion_present_main_and_flat") is True
        and manuscript_traceability.get("primitive_lane_boundary_present_main_and_flat") is True
        and manuscript_traceability.get("conditional_proof_claims_mapped_to_manuscript") is True
        and manuscript_traceability.get("manuscript_anchor_map_present")
        == expected_anchor_map["all_label_anchors_present"]
        and manuscript_traceability.get("theorem_assumption_anchor_map_present")
        == expected_anchor_map["all_theorem_assumption_anchors_present"]
        and manuscript_traceability.get("theorem_assumption_anchor_ids")
        == expected_anchor_map["theorem_assumption_anchor_ids"]
        and manuscript_traceability.get("theorem_anchor_table_reference_coverage_present")
        is True
        and manuscript_traceability.get("theorem_use_rule_present_main_and_flat")
        is True
        and manuscript_traceability.get("constant_dependency_table_present_main_and_flat")
        is True
        and manuscript_traceability.get(
            "theorem_dependency_consumption_table_present_main_and_flat"
        )
        is True
        and manuscript_traceability.get("theorem_output_scope_table_present_main_and_flat")
        is True
        and manuscript_traceability.get("quantifier_domain_table_present_main_and_flat")
        is True
        and manuscript_traceability.get("local_global_transfer_table_present_main_and_flat")
        is True
        and manuscript_traceability.get("reporting_map_table_present_main_and_flat")
        is True
        and manuscript_traceability.get("proof_causality_table_present_main_and_flat")
        is True
        and manuscript_traceability.get("branch_consistency_table_present_main_and_flat")
        is True
        and manuscript_traceability.get(
            "local_defect_decomposition_table_present_main_and_flat"
        )
        is True
        and manuscript_traceability.get(
            "direct_route_anticircularity_table_present_main_and_flat"
        )
        is True
        and manuscript_traceability.get(
            "implementation_route_oracle_table_present_main_and_flat"
        )
        is True
        and manuscript_traceability.get("b1_ad_expanded_closure_table_present_main_and_flat")
        is True
        and manuscript_traceability.get("p1p2_compact_tube_boundary_present_main_and_flat")
        is True
        and manuscript_traceability.get("p3p4_implementation_boundary_present_main_and_flat")
        is True
        and manuscript_traceability.get("p5_direct_route_boundary_present_main_and_flat")
        is True
        and manuscript_traceability.get("nonlinear_solver_scale_table_present_main_and_flat")
        is True
        and manuscript_traceability.get("p_interface_satisfaction_table_present_main_and_flat")
        is True
        and manuscript_traceability.get("does_not_change_proof_closure_state") is True,
        "manuscript traceability summary changed",
    )
    checks.check(
        readiness_boundary.get("narrowed_claim_b4_b6_b7_statuses")
        == {key: blocker_statuses.get(key) for key in ["B4", "B6", "B7"]}
        == {"B4": "closed", "B6": "closed", "B7": "closed"},
        "proof-closure narrowed-claim B4/B6/B7 boundary changed",
    )
    checks.check(
        readiness_boundary.get("proof_closure_manifest_scope")
        == "direct_pc2_closure_and_theorem_condition_traceability",
        "proof-closure manifest scope changed",
    )
    checks.check(
        readiness_boundary.get("global_submission_boundaries_retained")
        == [
            "full_source_policy_package_ready",
            "theorem_level_eta_h_solver_policy_evidence",
            "closed_residual_to_error_theorem_for_mechanism_rows",
        ],
        "proof-closure global submission boundary list changed",
    )
    checks.check(
        remaining_gate_scope.get("narrowed_claim_b4_b6_b7_statuses")
        == {key: blocker_statuses.get(key) for key in ["B4", "B6", "B7"]}
        == {"B4": "closed", "B6": "closed", "B7": "closed"},
        "proof-closure remaining-gate B4/B6/B7 boundary changed",
    )
    checks.check(
        remaining_gate_scope.get("b4_b6_b7_closed_elsewhere_under_narrowed_claim") is True,
        "proof-closure remaining-gate narrowed-claim closure marker changed",
    )
    checks.check(
        remaining_gate_scope.get("direct_pc2_proof_gap_closed") is True
        and remaining_gate_scope.get("direct_residual_bridge_route_satisfied") is True,
        "proof-closure remaining-gate direct PC2 closure markers changed",
    )
    checks.check(
        remaining_gate_scope.get("primitive_route_closed") is False,
        "proof-closure remaining-gate primitive route unexpectedly closed",
    )
    checks.check(
        remaining_gate_scope.get("eta_h_O_h7_solver_policy_evidence") is False
        and remaining_gate_scope.get("eta_h_theorem_condition_retained") is True,
        "proof-closure remaining-gate eta_h boundary changed",
    )
    checks.check(
        remaining_gate_scope.get("accepted_residual_to_error_theorem") is False
        and remaining_gate_scope.get("residual_to_error_blocking_obligations") == 7
        and remaining_gate_scope.get("residual_to_error_route_promoted") is False,
        "proof-closure remaining-gate residual-to-error boundary changed",
    )
    checks.check(
        remaining_gate_scope.get("active_direct_newton_euler_open_obligations") == 0
        and remaining_gate_scope.get("symbolic_primitive_route_open_obligations") == 1,
        "proof-closure remaining-gate Newton-Euler obligation boundary changed",
    )
    checks.check(
        remaining_gate_scope.get("global_submission_boundaries_retained")
        == [
            "full_source_policy_package_ready",
            "theorem_level_eta_h_solver_policy_evidence",
            "closed_residual_to_error_theorem_for_mechanism_rows",
        ],
        "proof-closure remaining-gate global boundary list changed",
    )
    checks.check(theorem.get("accepted_method") == "Gauss6/FullVA", "accepted method changed")
    checks.check(theorem.get("accepted_method_order") == 6, "accepted method order changed")
    checks.check(theorem.get("accepted_global_error_order") == 6, "accepted global order changed")
    checks.check(theorem.get("accepted_local_defect_order") == 7, "accepted local defect order changed")
    checks.check(theorem.get("comparator", {}).get("expected_order") == 5, "comparator expected order changed")
    checks.check(evidence.get("total_runtime_rows") == 132, "runtime row count changed")
    checks.check(evidence.get("certified_non_dynamic_rows") == 96, "certified non-dynamic row count changed")
    checks.check(evidence.get("active_direct_newton_euler_closed_rows") == 36, "active direct Newton-Euler closed rows changed")
    checks.check(evidence.get("active_direct_newton_euler_open_rows") == 0, "active direct Newton-Euler open rows changed")
    checks.check(
        evidence.get("active_direct_newton_euler_open_obligations") == 0,
        "active direct Newton-Euler open obligations changed",
    )
    checks.check(evidence.get("open_dynamic_rows") == 36, "open dynamic row count changed")
    checks.check(
        evidence.get("open_dynamic_rows_scope") == "symbolic_primitive_certificate_route_not_active_direct_pc2",
        "open dynamic row scope changed",
    )
    checks.check(evidence.get("newton_euler_open_obligations") == 1, "Newton-Euler open obligation count changed")
    checks.check(
        evidence.get("newton_euler_open_obligations_scope")
        == "symbolic_primitive_certificate_route_not_active_direct_pc2",
        "Newton-Euler open obligation scope changed",
    )
    checks.check(evidence.get("newton_euler_closed_obligations") == 5, "Newton-Euler closed obligation count changed")
    checks.check(
        evidence.get("newton_euler_closed_obligation_ids")
        == [
            "translational_balance_identity",
            "rotational_balance_identity",
            "multiplier_wrench_consistency",
            "smooth_force_lift_consistency",
            "symbolic_runtime_row_equivalence",
        ],
        "Newton-Euler closed obligation ids changed",
    )
    checks.check(evidence.get("newton_euler_symbolic_target_rows") == 36, "Newton-Euler target row count changed")
    checks.check(
        evidence.get("newton_euler_symbolic_target_translational_rows") == 18,
        "Newton-Euler target translational count changed",
    )
    checks.check(
        evidence.get("newton_euler_symbolic_target_rotational_rows") == 18,
        "Newton-Euler target rotational count changed",
    )
    checks.check(
        evidence.get("newton_euler_obligation_coverage_matrix_complete") is True,
        "Newton-Euler obligation coverage matrix not complete",
    )
    checks.check(evidence.get("newton_euler_row_obligation_links") == 180, "row-obligation link count changed")
    checks.check(
        evidence.get("newton_euler_rows_with_complete_obligation_sets") == 36,
        "row obligation set coverage changed",
    )
    checks.check(evidence.get("newton_euler_obligations_with_target_rows") == 6, "obligation coverage count changed")
    checks.check(
        evidence.get("newton_euler_runtime_expression_structure_checked")
        == newton_euler_certificate.get("summary", {}).get("runtime_expression_structure_checked")
        is True,
        "Newton-Euler runtime expression structure marker changed",
    )
    checks.check(
        evidence.get("newton_euler_runtime_expression_structure_checked_rows")
        == newton_euler_certificate.get("summary", {}).get("runtime_expression_structure_checked_rows")
        == 36,
        "Newton-Euler runtime expression checked rows changed",
    )
    checks.check(
        evidence.get("newton_euler_runtime_expression_structure_translational_rows") == 18,
        "Newton-Euler runtime expression translational rows changed",
    )
    checks.check(
        evidence.get("newton_euler_runtime_expression_structure_rotational_rows") == 18,
        "Newton-Euler runtime expression rotational rows changed",
    )
    checks.check(
        evidence.get("newton_euler_runtime_template_instantiation_checked")
        == newton_euler_certificate.get("summary", {}).get("runtime_template_instantiation_checked")
        is True,
        "Newton-Euler runtime template instantiation marker changed",
    )
    checks.check(
        evidence.get("newton_euler_runtime_template_instantiation_checked_rows")
        == newton_euler_certificate.get("summary", {}).get("runtime_template_instantiation_checked_rows")
        == 36,
        "Newton-Euler runtime template instantiation rows changed",
    )
    checks.check(
        evidence.get("newton_euler_template_algebraic_equivalence_checked")
        == newton_euler_certificate.get("summary", {}).get("template_algebraic_equivalence_checked")
        is True,
        "Newton-Euler template algebraic equivalence marker changed",
    )
    checks.check(
        evidence.get("newton_euler_template_algebraic_equivalence_checked_rows")
        == newton_euler_certificate.get("summary", {}).get("template_algebraic_equivalence_checked_rows")
        == 36,
        "Newton-Euler template algebraic equivalence rows changed",
    )
    checks.check(
        evidence.get("newton_euler_template_algebraic_equivalence_translational_rows") == 18,
        "Newton-Euler template algebraic equivalence translational rows changed",
    )
    checks.check(
        evidence.get("newton_euler_template_algebraic_equivalence_rotational_rows") == 18,
        "Newton-Euler template algebraic equivalence rotational rows changed",
    )
    checks.check(
        evidence.get("newton_euler_c2_template_algebraic_equivalence_closed") is True,
        "Newton-Euler template-level C2 subcheck not closed",
    )
    checks.check(
        evidence.get("newton_euler_balance_identity_closed") is True,
        "Newton-Euler balance identity not closed",
    )
    checks.check(
        evidence.get("newton_euler_balance_identity_closed_rows") == 36,
        "Newton-Euler balance identity closed rows changed",
    )
    checks.check(
        evidence.get("newton_euler_translational_balance_identity_closed_rows") == 18,
        "Newton-Euler translational balance identity rows changed",
    )
    checks.check(
        evidence.get("newton_euler_rotational_balance_identity_closed_rows") == 18,
        "Newton-Euler rotational balance identity rows changed",
    )
    checks.check(
        evidence.get("newton_euler_virtual_work_wrench_sign_skeleton_checked")
        == newton_euler_certificate.get("summary", {}).get("virtual_work_wrench_sign_skeleton_checked")
        is True,
        "Newton-Euler virtual-work sign skeleton not checked",
    )
    checks.check(
        evidence.get("newton_euler_virtual_work_wrench_sign_skeleton_checked_rows")
        == newton_euler_certificate.get("summary", {}).get("virtual_work_wrench_sign_skeleton_checked_rows")
        == newton_euler_virtual_work.get("summary", {}).get("checked_rows")
        == 36,
        "Newton-Euler virtual-work sign-skeleton rows changed",
    )
    checks.check(
        evidence.get("newton_euler_virtual_work_template_identity_proved")
        == newton_euler_certificate.get("summary", {}).get("virtual_work_template_identity_proved")
        == newton_euler_virtual_work.get("template_virtual_work_identity_proved")
        is True,
        "Newton-Euler virtual-work template identity not proved",
    )
    checks.check(
        evidence.get("newton_euler_virtual_work_template_identity_rows")
        == newton_euler_certificate.get("summary", {}).get("virtual_work_template_identity_rows")
        == newton_euler_virtual_work.get("summary", {}).get("template_virtual_work_identity_rows")
        == 36,
        "Newton-Euler virtual-work template identity rows changed",
    )
    checks.check(
        evidence.get("newton_euler_multiplier_wrench_consistency_closed")
        == newton_euler_certificate.get("summary", {}).get("multiplier_wrench_consistency_closed")
        is True,
        "Newton-Euler multiplier-wrench consistency not closed",
    )
    checks.check(
        evidence.get("newton_euler_row_expanded_virtual_work_identity_proved")
        == newton_euler_certificate.get("summary", {}).get("row_expanded_virtual_work_identity_proved")
        is True,
        "Newton-Euler row-expanded virtual-work identity not proved",
    )
    checks.check(
        evidence.get("newton_euler_row_expanded_virtual_work_identity_rows")
        == newton_euler_certificate.get("summary", {}).get("row_expanded_virtual_work_identity_rows")
        == 36,
        "Newton-Euler row-expanded virtual-work identity rows changed",
    )
    checks.check(
        evidence.get("newton_euler_dynamic_row_closure_contract_rows")
        == newton_euler_closure_contract.get("summary", {}).get("row_count")
        == 36,
        "Newton-Euler dynamic-row closure contract row count changed",
    )
    checks.check(
        evidence.get("newton_euler_dynamic_row_closure_contract_traceability_rows")
        == newton_euler_closure_contract.get("summary", {}).get("rows_with_full_runtime_traceability")
        == 36,
        "Newton-Euler dynamic-row traceability count changed",
    )
    checks.check(
        evidence.get("newton_euler_dynamic_row_closure_contract_theorem_closed_rows")
        == newton_euler_closure_contract.get("summary", {}).get("rows_with_direct_pc2_input_closure")
        == 36,
        "Newton-Euler dynamic-row closure contract direct-route row-defect closed rows changed",
    )
    checks.check(
        evidence.get("newton_euler_dynamic_row_closure_contract_open_rows")
        == newton_euler_closure_contract.get("summary", {}).get("open_row_count")
        == 0,
        "Newton-Euler dynamic-row closure contract open row count changed",
    )
    checks.check(
        evidence.get("newton_euler_dynamic_row_closure_contract_pc_open") == [],
        "Newton-Euler dynamic-row closure contract open PCs changed",
    )
    checks.check(
        evidence.get("b1_ad_expanded_symbolic_oracle_closure")
        == b1_ad_expanded_closure.get("ad_expanded_symbolic_oracle_closure")
        is True,
        "B1 AD-expanded symbolic oracle closure not carried into proof closure",
    )
    checks.check(
        evidence.get("b1_ad_expanded_symbolic_oracle_closed_rows")
        == b1_ad_expanded_closure.get("ad_expanded_symbolic_oracle_closed_rows")
        == 36,
        "B1 AD-expanded closed row count changed",
    )
    checks.check(
        evidence.get("b1_ad_expanded_symbolic_oracle_closed_cells")
        == b1_ad_expanded_closure.get("ad_expanded_symbolic_oracle_closed_cells")
        == 4752,
        "B1 AD-expanded derivative-cell count changed",
    )
    checks.check(
        evidence.get("b1_ad_expanded_symbolic_oracle_columns_per_row")
        == b1_ad_expanded_closure.get("columns_per_row")
        == 132,
        "B1 AD-expanded columns-per-row count changed",
    )
    checks.check(
        evidence.get("b1_dynamic_symbolic_oracle_complete")
        == b1_ad_expanded_closure.get("dynamic_symbolic_oracle_complete")
        is False,
        "B1 certificate must not close the dynamic symbolic oracle",
    )
    checks.check(
        evidence.get("b1_stage_residual_O_h7_from_certificate")
        == b1_ad_expanded_closure.get(
            "stage_residual_O_h7_implementation_defect_proved_from_this_certificate"
        )
        is False,
        "B1 certificate must not independently prove the O(h^7) stage residual",
    )
    checks.check(
        evidence.get("b1_submission_ready_from_certificate")
        == b1_ad_expanded_closure.get("submission_ready")
        is False,
        "B1 certificate must not mark the package submission ready",
    )
    checks.check(
        evidence.get("b1_ad_expanded_certificate_status")
        == b1_ad_expanded_closure.get("status")
        == "ad_expanded_symbolic_oracle_closed_without_o_h7_overclaim",
        "B1 AD-expanded certificate status changed",
    )
    checks.check(
        evidence.get("newton_euler_d5_dynamic_defect_blueprint_rows")
        == newton_euler_closure_contract.get("summary", {}).get("d5_dynamic_defect_blueprint_rows")
        == 36,
        "Newton-Euler D5 blueprint row count changed",
    )
    checks.check(
        evidence.get("newton_euler_d5_open_lifted_stage_terms")
        == newton_euler_closure_contract.get("summary", {}).get("d5_open_lifted_stage_terms")
        == 0,
        "Newton-Euler D5 open lifted-stage term count changed",
    )
    checks.check(
        evidence.get("newton_euler_d5_rows_requiring_power_at_least_seven")
        == newton_euler_closure_contract.get("summary", {}).get("d5_rows_requiring_power_at_least_seven")
        == 36,
        "Newton-Euler D5 power-seven row count changed",
    )
    checks.check(
        evidence.get("newton_euler_d5_finite_probe_sufficient_rows")
        == newton_euler_closure_contract.get("summary", {}).get("d5_finite_probe_sufficient_rows")
        == 0,
        "Newton-Euler D5 incorrectly accepts finite-probe-only rows",
    )
    checks.check(
        evidence.get("newton_euler_d5_residual_to_error_promotion_allowed_rows")
        == newton_euler_closure_contract.get("summary", {}).get(
            "d5_residual_to_error_promotion_allowed_rows"
        )
        == 0,
        "Newton-Euler D5 incorrectly allows residual-to-error promotion rows",
    )
    checks.check(
        evidence.get("newton_euler_d5_blueprint_is_not_closure")
        == newton_euler_closure_contract.get("summary", {}).get("d5_blueprint_is_not_closure")
        is False,
        "Newton-Euler D5 blueprint non-closure marker changed",
    )
    checks.check(
        evidence.get("newton_euler_d5_readiness_rows") == d5_summary.get("row_count") == 36,
        "Newton-Euler D5 readiness row count changed",
    )
    checks.check(
        evidence.get("newton_euler_d5_readiness_runtime_ready_rows")
        == d5_summary.get("runtime_traceability_ready_rows")
        == 36,
        "Newton-Euler D5 readiness runtime-ready count changed",
    )
    checks.check(
        evidence.get("newton_euler_d5_readiness_open_lifted_stage_terms")
        == d5_summary.get("open_lifted_stage_terms")
        == 0,
        "Newton-Euler D5 readiness open lifted-stage count changed",
    )
    checks.check(
        evidence.get("newton_euler_d5_readiness_theorem_certified_rows")
        == d5_summary.get("theorem_certified_rows")
        == 36,
        "Newton-Euler D5 readiness direct-route certified rows changed",
    )
    checks.check(
        evidence.get("newton_euler_d5_readiness_pc2_closed") is True
        and d5_readiness.get("pc2_closed") is True,
        "Newton-Euler D5 readiness direct PC2 closure missing",
    )
    checks.check(
        evidence.get("newton_euler_d5_readiness_manifest_linked") is True,
        "Newton-Euler D5 readiness audit is not linked",
    )
    checks.check(
        evidence.get("newton_euler_d5_direct_substitution_status")
        == d5_direct_substitution.get("status")
        == "direct_substitution_certificate_closed",
        "Newton-Euler D5 direct-substitution certificate status changed",
    )
    checks.check(
        evidence.get("newton_euler_d5_direct_substitution_closed")
        == d5_direct_substitution.get("direct_route_mathematical_certificate_closed")
        is True,
        "Newton-Euler D5 direct-substitution certificate is not closed",
    )
    checks.check(
        evidence.get("newton_euler_d5_direct_substitution_non_circular")
        == d5_direct_substitution.get("direct_route_non_circular")
        is True,
        "Newton-Euler D5 direct-substitution route is not non-circular",
    )
    checks.check(
        evidence.get("newton_euler_d5_direct_substitution_stage_residual_O_h7")
        == d5_direct_substitution.get("stage_residual_O_h7_by_direct_route")
        is True,
        "Newton-Euler D5 direct-substitution route does not prove O(h^7)",
    )
    checks.check(
        evidence.get("newton_euler_d5_direct_substitution_dynamic_zero_rows")
        == d5_direct_summary.get("dynamic_zero_residual_rows")
        == 36,
        "Newton-Euler D5 direct-substitution dynamic zero-row count changed",
    )
    checks.check(
        evidence.get("newton_euler_d5_direct_substitution_full_stage_rows")
        == d5_direct_summary.get("full_stage_rows_if_promoted")
        == 132,
        "Newton-Euler D5 direct-substitution full-stage row count changed",
    )
    checks.check(
        evidence.get("newton_euler_d5_direct_substitution_forbidden_shortcuts")
        == d5_direct_summary.get("forbidden_shortcuts_used")
        == 0,
        "Newton-Euler D5 direct-substitution uses a forbidden shortcut",
    )
    checks.check(
        evidence.get("newton_euler_d5_direct_substitution_direct_route_pc2_active") is True,
        "Newton-Euler D5 direct-substitution direct-route PC2 activity missing",
    )
    checks.check(
        evidence.get("newton_euler_d5_direct_substitution_residual_to_error_promotion") is False,
        "Newton-Euler D5 direct-substitution must not promote residual-to-error closure",
    )
    checks.check(
        evidence.get("newton_euler_d5_direct_substitution_source_policy_promotion") is False,
        "Newton-Euler D5 direct-substitution must not promote source-policy closure",
    )
    checks.check(
        evidence.get("newton_euler_d5_direct_substitution_manifest_linked") is True,
        "Newton-Euler D5 direct-substitution manifest link missing",
    )
    checks.check(
        evidence.get("newton_euler_d5_taylor_term_budget_rows")
        == d5_term_summary.get("dynamic_rows")
        == 36,
        "Newton-Euler D5 Taylor term-budget row count changed",
    )
    checks.check(
        evidence.get("newton_euler_d5_taylor_term_budget_terms")
        == d5_term_summary.get("term_rows")
        == 162,
        "Newton-Euler D5 Taylor term-budget term count changed",
    )
    checks.check(
        evidence.get("newton_euler_d5_taylor_term_budget_open_terms")
        == d5_term_summary.get("open_taylor_bound_terms")
        == 162,
        "Newton-Euler D5 Taylor term-budget open term count changed",
    )
    checks.check(
        evidence.get("newton_euler_d5_taylor_term_budget_certified_terms")
        == d5_term_summary.get("certified_taylor_bound_terms")
        == 0,
        "Newton-Euler D5 Taylor term-budget unexpectedly certifies terms",
    )
    checks.check(
        evidence.get("newton_euler_d5_taylor_strict_reduction_terms")
        == d5_term_summary.get("strict_taylor_reduction_terms")
        == 162,
        "Newton-Euler D5 strict Taylor reduction count changed",
    )
    checks.check(
        evidence.get("newton_euler_d5_taylor_anti_circular_terms")
        == d5_term_summary.get("anti_circular_taylor_terms")
        == 162,
        "Newton-Euler D5 anti-circular Taylor count changed",
    )
    checks.check(
        evidence.get("newton_euler_d5_taylor_terms_with_open_primitive_blockers")
        == d5_term_summary.get("terms_with_open_primitive_blockers")
        == 162,
        "Newton-Euler D5 open primitive blocker term count changed",
    )
    checks.check(
        evidence.get("newton_euler_d5_taylor_unweighted_acceleration_blocked_terms")
        == d5_term_summary.get("unweighted_acceleration_blocked_terms")
        == 36,
        "Newton-Euler D5 unweighted acceleration blocker count changed",
    )
    checks.check(
        evidence.get("newton_euler_d5_taylor_h_weighted_acceleration_sufficient_terms")
        == d5_term_summary.get("h_weighted_acceleration_sufficient_terms")
        == 0,
        "Newton-Euler D5 h-weighted acceleration was incorrectly accepted",
    )
    checks.check(
        evidence.get("newton_euler_d5_taylor_h_weighted_acceleration_insufficient_terms")
        == d5_term_summary.get("h_weighted_acceleration_insufficient_terms")
        == 36,
        "Newton-Euler D5 h-weighted acceleration insufficiency count changed",
    )
    checks.check(
        evidence.get("newton_euler_d5_taylor_primitive_blocker_usage")
        == d5_term_summary.get("primitive_blocker_usage")
        == {
            "P_acceleration_lift": 36,
            "P_geometry_lift": 36,
            "P_gyroscopic_lift": 18,
            "P_multiplier_lift": 72,
            "P_state_lift": 126,
        },
        "Newton-Euler D5 primitive blocker usage changed",
    )
    checks.check(
        evidence.get("newton_euler_d5_taylor_template_usage")
        == d5_term_summary.get("taylor_template_usage")
        == {
            "bilinear_gyroscopic_mean_value_lift": 18,
            "linear_unweighted_acceleration_lift": 18,
            "linear_unweighted_angular_acceleration_lift": 18,
            "product_geometry_multiplier_lift": 36,
            "smooth_force_lipschitz_state_lift": 18,
            "smooth_friction_lipschitz_state_multiplier_lift": 18,
            "smooth_friction_torque_lipschitz_state_multiplier_lift": 18,
            "smooth_torque_lipschitz_state_lift": 18,
        },
        "Newton-Euler D5 Taylor template usage changed",
    )
    checks.check(
        evidence.get("newton_euler_d5_taylor_term_budget_pc2_closed") is False
        and d5_term_budget.get("pc2_closed") is False,
        "Newton-Euler D5 Taylor term-budget unexpectedly closes PC2",
    )
    checks.check(
        evidence.get("newton_euler_d5_taylor_term_budget_manifest_linked") is True,
        "Newton-Euler D5 Taylor term-budget audit is not linked",
    )
    checks.check(
        evidence.get("newton_euler_d5_primitive_reduction_terms")
        == d5_primitive_summary.get("term_rows")
        == 162,
        "Newton-Euler D5 primitive reduction term count changed",
    )
    checks.check(
        evidence.get("newton_euler_d5_primitive_reduction_rules")
        == d5_primitive_summary.get("term_rows_with_reduction_rule")
        == 162,
        "Newton-Euler D5 primitive reduction rule count changed",
    )
    checks.check(
        evidence.get("newton_euler_d5_primitive_obligations")
        == d5_primitive_summary.get("primitive_obligation_count")
        == 6,
        "Newton-Euler D5 primitive obligation count changed",
    )
    checks.check(
        evidence.get("newton_euler_d5_primitive_obligations_proved")
        == d5_primitive_summary.get("primitive_obligations_proved")
        == 1,
        "Newton-Euler D5 primitive closed count changed",
    )
    checks.check(
        evidence.get("newton_euler_d5_primitive_term_bounds_proved")
        == d5_primitive_summary.get("term_bounds_proved")
        == 0,
        "Newton-Euler D5 primitive reduction unexpectedly proves term bounds",
    )
    checks.check(
        evidence.get("newton_euler_d5_primitive_reduction_pc2_closed") is False
        and d5_primitive_reduction.get("pc2_closed") is False,
        "Newton-Euler D5 primitive reduction unexpectedly closes PC2",
    )
    checks.check(
        evidence.get("newton_euler_d5_primitive_reduction_manifest_linked") is True,
        "Newton-Euler D5 primitive reduction audit is not linked",
    )
    checks.check(
        evidence.get("newton_euler_d5_smooth_force_corollary_label")
        == d5_smooth_force_corollary.get("label")
        == "cor:d5-smooth-force-row-bound-under-lifts",
        "Newton-Euler D5 smooth force corollary label missing",
    )
    checks.check(
        evidence.get("newton_euler_d5_smooth_force_corollary_main_flat_present") is True
        and d5_smooth_force_corollary.get("main_tex_present") is True
        and d5_smooth_force_corollary.get("flat_tex_present") is True,
        "Newton-Euler D5 smooth force corollary not present in main/flat TeX",
    )
    checks.check(
        evidence.get("newton_euler_d5_smooth_force_conditionally_bound_terms")
        == d5_smooth_force_corollary.get("term_rows_conditionally_bound_under_lifts")
        == 72,
        "Newton-Euler D5 smooth force conditional row count changed",
    )
    checks.check(
        evidence.get("newton_euler_d5_smooth_force_summary_terms")
        == d5_primitive_summary.get("smooth_force_torque_lift_terms")
        == 72,
        "Newton-Euler D5 smooth force summary term count changed",
    )
    checks.check(
        evidence.get("newton_euler_d5_smooth_force_primitive_inputs_assumed")
        == d5_smooth_force_corollary.get("primitive_inputs_assumed")
        == ["P_state_lift", "P_multiplier_lift"],
        "Newton-Euler D5 smooth force primitive-input boundary changed",
    )
    checks.check(
        evidence.get("newton_euler_d5_smooth_force_actual_taylor_bounds_proved")
        == d5_smooth_force_corollary.get("actual_taylor_bounds_proved")
        == 0,
        "Newton-Euler D5 smooth force corollary unexpectedly proves Taylor bounds",
    )
    checks.check(
        evidence.get("newton_euler_d5_smooth_force_primitive_closed") is False
        and d5_smooth_force_corollary.get("primitive_closed") is False,
        "Newton-Euler D5 smooth force corollary unexpectedly closes primitive route",
    )
    checks.check(
        evidence.get("newton_euler_d5_smooth_force_pc2_closed") is False
        and d5_smooth_force_corollary.get("pc2_closed") is False,
        "Newton-Euler D5 smooth force corollary unexpectedly closes PC2",
    )
    checks.check(
        evidence.get("newton_euler_d5_smooth_force_d4_direct_route_used_as_rate_proof") is False
        and d5_smooth_force_corollary.get("uses_d4_direct_route_smoothness_as_rate_proof") is False,
        "Newton-Euler D5 smooth force corollary uses D4 direct route as a primitive rate proof",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_tube_constants_closed") is True
        and d5_p_tube_constants.get("primitive_closed") is True,
        "Newton-Euler D5 P_tube compact constants not closed",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_tube_constants_term_rows")
        == d5_p_tube_summary.get("term_rows_using_p_tube")
        == 162,
        "Newton-Euler D5 P_tube term-row count changed",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_tube_constants_remaining_primitives")
        == d5_p_tube_summary.get("primitive_obligations_remaining")
        == 5,
        "Newton-Euler D5 P_tube remaining primitive count changed",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_tube_constants_induced_bounds_proved")
        == d5_p_tube_summary.get("induced_taylor_bounds_proved")
        == 0,
        "Newton-Euler D5 P_tube unexpectedly proves induced Taylor bounds",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_tube_constants_pc2_closed") is False
        and d5_p_tube_constants.get("pc2_closed") is False,
        "Newton-Euler D5 P_tube unexpectedly closes PC2",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_tube_constants_manifest_linked") is True,
        "Newton-Euler D5 P_tube audit is not linked",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_state_gap_recorded") is True
        and d5_p_state_gap.get("status") == "p_state_lift_gap_recorded_pc2_open",
        "Newton-Euler D5 P_state gap audit not recorded",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_state_closed") is False
        and d5_p_state_gap.get("primitive_closed") is False,
        "Newton-Euler D5 P_state unexpectedly closed",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_state_map_definition_recorded") is True
        and d5_p_state_map_definition.get("status") == "p_state_map_definition_closed_lift_open",
        "Newton-Euler D5 P_state map-definition audit not recorded",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_state_map_definition_closed") is True
        and d5_p_state_map_definition.get("ps1_map_definition_closed") is True,
        "Newton-Euler D5 P_state map definition not closed",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_state_map_rows")
        == d5_p_state_map_summary.get("non_dynamic_map_rows")
        == 96,
        "Newton-Euler D5 P_state map row count changed",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_state_map_subproofs_closed")
        == d5_p_state_map_summary.get("closed_subproof_count")
        == 1,
        "Newton-Euler D5 P_state map subproof count changed",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_state_map_required_subproofs")
        == d5_p_state_map_summary.get("required_subproof_count")
        == 4,
        "Newton-Euler D5 P_state map required subproof count changed",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_state_map_pc2_closed") is False
        and d5_p_state_map_definition.get("pc2_closed") is False,
        "Newton-Euler D5 P_state map definition unexpectedly closes PC2",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_state_anticircularity_recorded")
        == (d5_p_state_anticircularity.get("status") == "p_state_ps4_anticircularity_closed_lift_open")
        is True,
        "Newton-Euler D5 P_state anti-circularity audit not recorded",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_state_anticircularity_closed")
        == d5_p_state_anticircularity.get("ps4_anticircularity_closed")
        is True,
        "Newton-Euler D5 P_state anti-circularity not closed",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_state_anticircularity_subproofs_after")
        == d5_p_state_anticircularity_summary.get("closed_p_state_subproofs_after_ps4")
        == 2,
        "Newton-Euler D5 P_state anti-circularity subproof count changed",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_state_anticircularity_open_subproofs_after")
        == d5_p_state_anticircularity_summary.get("open_p_state_subproofs_after_ps4")
        == 2,
        "Newton-Euler D5 P_state anti-circularity open subproof count changed",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_state_anticircularity_pc2_closed") is False
        and d5_p_state_anticircularity.get("pc2_closed") is False,
        "Newton-Euler D5 P_state anti-circularity unexpectedly closes PC2",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_state_ps2_weighted_target_recorded")
        == (d5_p_state_ps2_target.get("status") == "p_state_ps2_weighted_infsup_target_recorded_ps2_open")
        is True,
        "Newton-Euler D5 P_state PS2 weighted target audit not recorded",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_state_ps2_weighted_target_spec_closed")
        == d5_p_state_ps2_target.get("ps2_target_spec_closed")
        is True,
        "Newton-Euler D5 P_state PS2 weighted target spec not closed",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_state_ps2_weighted_target_infsup_closed")
        == d5_p_state_ps2_target.get("ps2_inverse_or_infsup_closed")
        is False,
        "Newton-Euler D5 P_state PS2 inf-sup unexpectedly closed",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_state_ps2_weighted_target_state_dim")
        == d5_p_state_ps2_target_summary.get("state_block_dimension")
        == 72,
        "Newton-Euler D5 P_state PS2 state dimension changed",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_state_ps2_weighted_target_acc_dim")
        == d5_p_state_ps2_target_summary.get("auxiliary_acceleration_dimension")
        == 36,
        "Newton-Euler D5 P_state PS2 acceleration dimension changed",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_state_ps2_weighted_target_row_dim")
        == d5_p_state_ps2_target_summary.get("non_dynamic_row_dimension")
        == 96,
        "Newton-Euler D5 P_state PS2 row dimension changed",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_state_ps2_weighted_target_pc2_closed") is False
        and d5_p_state_ps2_target.get("pc2_closed") is False,
        "Newton-Euler D5 P_state PS2 target unexpectedly closes PC2",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_state_ps2_kinematic_block_recorded") is True
        and d5_p_state_ps2_kinematic.get("ps2_kinematic_block_certificate_recorded") is True,
        "Newton-Euler D5 P_state PS2 kinematic block not recorded",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_state_ps2_kinematic_subblock_bound_certified") is True
        and d5_p_state_ps2_kinematic.get("certifies_uniform_euclidean_kinematic_subblock_bound") is True,
        "Newton-Euler D5 P_state PS2 kinematic subblock bound not certified",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_state_ps2_kinematic_full_nonlinear_ps2_certified") is False
        and d5_p_state_ps2_kinematic.get("certifies_full_nonlinear_ps2") is False,
        "Newton-Euler D5 P_state PS2 kinematic block overclaims full nonlinear PS2",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_state_ps2_kinematic_rows")
        == d5_p_state_ps2_kinematic_dims.get("kinematic_row_dimension")
        == 72,
        "Newton-Euler D5 P_state PS2 kinematic row count changed",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_state_ps2_kinematic_lower_pair_surplus_rows")
        == d5_p_state_ps2_kinematic_dims.get("lower_pair_surplus_rows_not_needed_for_subblock")
        == 24,
        "Newton-Euler D5 P_state PS2 kinematic surplus row count changed",
    )
    checks.check(
        close_to(
            evidence.get("newton_euler_d5_p_state_ps2_kinematic_inverse_template_norm"),
            d5_p_state_ps2_kinematic_constants.get("kinematic_inverse_template_2_norm_at_h_max"),
        ),
        "Newton-Euler D5 P_state PS2 kinematic inverse norm changed",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_state_ps2_kinematic_binding_gap_count") == 3,
        "Newton-Euler D5 P_state PS2 kinematic binding gap count changed",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_state_ps2_kinematic_pc2_closed") is False
        and d5_p_state_ps2_kinematic.get("pc2_closed") is False,
        "Newton-Euler D5 P_state PS2 kinematic block unexpectedly closes PC2",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_state_ps2_lie_chart_binding_recorded") is True
        and d5_p_state_ps2_lie_chart.get("p_state_ps2_lie_chart_binding_recorded") is True,
        "Newton-Euler D5 P_state PS2 Lie-chart binding not recorded",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_state_ps2_lie_chart_so3_norm_equivalence") is True
        and d5_p_state_ps2_lie_chart.get("certifies_so3_chart_norm_equivalence") is True,
        "Newton-Euler D5 P_state PS2 SO(3) chart norm equivalence not linked",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_state_ps2_lie_chart_full_mean_value_binding") is False
        and d5_p_state_ps2_lie_chart.get("certifies_full_nonlinear_mean_value_binding") is False,
        "Newton-Euler D5 P_state PS2 Lie-chart overclaims mean-value binding",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_state_ps2_lie_chart_full_nonlinear_ps2") is False
        and d5_p_state_ps2_lie_chart.get("certifies_full_nonlinear_ps2") is False,
        "Newton-Euler D5 P_state PS2 Lie-chart unexpectedly closes full nonlinear PS2",
    )
    checks.check(
        close_to(
            evidence.get("newton_euler_d5_p_state_ps2_lie_chart_equivalence_factor"),
            d5_p_state_ps2_lie_chart_constants.get("chart_equivalence_factor"),
        ),
        "Newton-Euler D5 P_state PS2 Lie-chart equivalence factor changed",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_state_ps2_lie_chart_remaining_binding_gaps") == 2,
        "Newton-Euler D5 P_state PS2 Lie-chart remaining binding gap count changed",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_state_ps2_lie_chart_pc2_closed") is False
        and d5_p_state_ps2_lie_chart.get("pc2_closed") is False,
        "Newton-Euler D5 P_state PS2 Lie-chart unexpectedly closes PC2",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_state_ps2_row_injection_recorded") is True
        and d5_p_state_ps2_row_injection.get("p_state_ps2_row_injection_recorded") is True,
        "Newton-Euler D5 P_state PS2 row injection not recorded",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_state_ps2_row_injection_72_to_96_certified") is True
        and d5_p_state_ps2_row_injection.get("certifies_72_to_96_row_injection") is True,
        "Newton-Euler D5 P_state PS2 row injection not certified",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_state_ps2_row_injection_unweighted_scaling") is True
        and d5_p_state_ps2_row_injection.get("certifies_unweighted_residual_scaling") is True,
        "Newton-Euler D5 P_state PS2 row injection scaling not linked",
    )
    checks.check(
        close_to(evidence.get("newton_euler_d5_p_state_ps2_row_injection_selector_norm"), 1.0),
        "Newton-Euler D5 P_state PS2 row selector norm changed",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_state_ps2_row_injection_full_mean_value_binding") is False
        and d5_p_state_ps2_row_injection.get("certifies_full_nonlinear_mean_value_binding") is False,
        "Newton-Euler D5 P_state PS2 row injection overclaims mean-value binding",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_state_ps2_row_injection_full_nonlinear_ps2") is False
        and d5_p_state_ps2_row_injection.get("certifies_full_nonlinear_ps2") is False,
        "Newton-Euler D5 P_state PS2 row injection unexpectedly closes full PS2",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_state_ps2_row_injection_remaining_binding_gaps") == 1,
        "Newton-Euler D5 P_state PS2 row injection gap count changed",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_state_ps2_row_injection_pc2_closed") is False
        and d5_p_state_ps2_row_injection.get("pc2_closed") is False,
        "Newton-Euler D5 P_state PS2 row injection unexpectedly closes PC2",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_state_ps2_nonlinear_binding_recorded") is True
        and d5_p_state_ps2_nonlinear.get("p_state_ps2_nonlinear_binding_recorded") is True,
        "Newton-Euler D5 P_state PS2 nonlinear binding not recorded",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_state_ps2_nonlinear_rotational_mean_value") is True
        and d5_p_state_ps2_nonlinear.get("certifies_rotational_lie_row_mean_value_binding") is True,
        "Newton-Euler D5 P_state PS2 nonlinear rotational mean-value binding not linked",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_state_ps2_nonlinear_full_mean_value") is True
        and d5_p_state_ps2_nonlinear.get("certifies_full_nonlinear_mean_value_binding") is True,
        "Newton-Euler D5 P_state PS2 nonlinear mean-value binding not linked",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_state_ps2_nonlinear_full_ps2") is False
        and d5_p_state_ps2_nonlinear.get("certifies_full_nonlinear_ps2") is False,
        "Newton-Euler D5 P_state PS2 nonlinear binding overclaims full PS2",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_state_ps2_nonlinear_promotion_gaps") == 1,
        "Newton-Euler D5 P_state PS2 nonlinear promotion gap count changed",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_state_ps2_nonlinear_pc2_closed") is False
        and d5_p_state_ps2_nonlinear.get("pc2_closed") is False,
        "Newton-Euler D5 P_state PS2 nonlinear binding unexpectedly closes PC2",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_state_ps2_aggregate_promotion_recorded") is True
        and d5_p_state_ps2_aggregate.get("p_state_ps2_aggregate_promotion_recorded") is True,
        "Newton-Euler D5 P_state PS2 aggregate promotion not recorded",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_state_ps2_aggregate_weighted_inverse_certified") is True
        and d5_p_state_ps2_aggregate.get("certifies_aggregate_weighted_ps2_inverse") is True,
        "Newton-Euler D5 P_state PS2 aggregate inverse not certified",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_state_ps2_aggregate_uniform_constant_certified") is True
        and d5_p_state_ps2_aggregate.get("certifies_uniform_ps2_constant") is True,
        "Newton-Euler D5 P_state PS2 aggregate uniform constant not certified",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_state_ps2_aggregate_inverse_or_infsup_closed") is True
        and d5_p_state_ps2_aggregate.get("ps2_inverse_or_infsup_closed") is True,
        "Newton-Euler D5 P_state PS2 aggregate inf-sup not closed",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_state_ps2_aggregate_ps3_actual_conversion_closed") is False
        and d5_p_state_ps2_aggregate.get("ps3_actual_state_lift_conversion_closed") is False,
        "Newton-Euler D5 P_state PS2 aggregate unexpectedly closes PS3",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_state_ps2_aggregate_p_state_closed") is False
        and d5_p_state_ps2_aggregate.get("primitive_closed") is False,
        "Newton-Euler D5 P_state PS2 aggregate unexpectedly closes P_state",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_state_ps2_aggregate_pc2_closed") is False
        and d5_p_state_ps2_aggregate.get("pc2_closed") is False,
        "Newton-Euler D5 P_state PS2 aggregate unexpectedly closes PC2",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_state_ps2_linearization_probe_recorded")
        == d5_p_state_ps2_probe.get("ps2_weighted_linearization_probe_recorded")
        is True,
        "Newton-Euler D5 P_state PS2 linearization probe not recorded",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_state_ps2_linearization_probe_full_column_rank_all")
        == d5_p_state_ps2_probe_summary.get("finite_probe_full_column_rank_all")
        is True,
        "Newton-Euler D5 P_state PS2 linearization probe full-rank marker missing",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_state_ps2_linearization_probe_rank_range")
        == [
            d5_p_state_ps2_probe_summary.get("min_weighted_operator_rank"),
            d5_p_state_ps2_probe_summary.get("max_weighted_operator_rank"),
        ]
        == [108, 108],
        "Newton-Euler D5 P_state PS2 linearization probe rank range changed",
    )
    checks.check(
        close_to(
            evidence.get("newton_euler_d5_p_state_ps2_linearization_probe_min_singular"),
            d5_p_state_ps2_probe_summary.get("min_singular_value_across_probes"),
        ),
        "Newton-Euler D5 P_state PS2 probe minimum singular value changed",
    )
    checks.check(
        close_to(
            evidence.get("newton_euler_d5_p_state_ps2_linearization_probe_max_state_projection_constant"),
            d5_p_state_ps2_probe_summary.get("max_finite_state_projection_constant"),
        ),
        "Newton-Euler D5 P_state PS2 probe projection constant changed",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_state_ps2_linearization_probe_uniform_constant_proved")
        == d5_p_state_ps2_probe.get("uniform_constant_proved")
        is False,
        "Newton-Euler D5 P_state PS2 probe unexpectedly proves uniform constant",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_state_ps2_linearization_probe_pc2_closed") is False
        and d5_p_state_ps2_probe.get("pc2_closed") is False,
        "Newton-Euler D5 P_state PS2 probe unexpectedly closes PC2",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_state_ps3_conditional_conversion_recorded")
        == (
            d5_p_state_ps3_conversion.get("status")
            == "p_state_ps3_conditional_conversion_recorded_ps3_actual_open"
        )
        is True,
        "Newton-Euler D5 P_state PS3 conditional conversion audit not recorded",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_state_ps3_conditional_conversion_closed")
        == d5_p_state_ps3_conversion.get("ps3_conditional_conversion_closed")
        is True,
        "Newton-Euler D5 P_state PS3 conditional conversion not closed",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_state_ps3_actual_conversion_closed")
        == d5_p_state_ps3_conversion.get("ps3_actual_state_lift_conversion_closed")
        is False,
        "Newton-Euler D5 P_state PS3 actual conversion unexpectedly closed",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_state_ps3_ps2_dependency_satisfied_by_aggregate")
        == d5_p_state_ps3_conversion.get("ps2_dependency_satisfied_by_aggregate")
        is True,
        "Newton-Euler D5 P_state PS3 aggregate PS2 dependency not satisfied",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_state_ps3_ps2_inverse_or_infsup_closed")
        == d5_p_state_ps3_conversion.get("ps2_inverse_or_infsup_closed")
        is True,
        "Newton-Euler D5 P_state PS3 PS2 inverse not linked as closed",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_state_ps3_actual_input_instantiation_closed")
        == d5_p_state_ps3_conversion.get("actual_ps3_input_instantiation_closed")
        is False,
        "Newton-Euler D5 P_state PS3 actual input instantiation unexpectedly closed",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_state_ps3_weighted_acceleration_rate")
        == d5_p_state_ps3_conversion_summary.get("weighted_acceleration_input_rate")
        == "O(h^7)",
        "Newton-Euler D5 P_state PS3 weighted acceleration rate changed",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_state_ps3_conditional_state_lift_rate")
        == d5_p_state_ps3_conversion_summary.get("conditional_state_lift_rate")
        == "O(h^7)",
        "Newton-Euler D5 P_state PS3 conditional state rate changed",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_state_ps3_pc2_closed") is False
        and d5_p_state_ps3_conversion.get("pc2_closed") is False,
        "Newton-Euler D5 P_state PS3 conversion unexpectedly closes PC2",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_state_ps3_actual_gap_recorded") is True
        and d5_p_state_ps3_actual_gap.get("status")
        == "ps3_actual_instantiation_gap_recorded_actual_ps3_open",
        "Newton-Euler D5 P_state PS3 actual-instantiation gap not recorded",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_state_ps3_actual_gap_inputs_closed")
        == d5_p_state_ps3_actual_gap.get("summary", {}).get("input_requirements_closed")
        == 2,
        "Newton-Euler D5 P_state PS3 actual-gap closed input count changed",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_state_ps3_actual_gap_inputs_total")
        == d5_p_state_ps3_actual_gap.get("summary", {}).get("input_requirements_total")
        == 4,
        "Newton-Euler D5 P_state PS3 actual-gap input total changed",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_state_ps3_actual_gap_independent_h_acc_input_closed")
        is False
        and d5_p_state_ps3_actual_gap.get("summary", {}).get(
            "independent_h_weighted_acceleration_input_closed"
        )
        is False,
        "Newton-Euler D5 P_state PS3 h-weighted acceleration input unexpectedly closed",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_state_ps3_actual_gap_non_circular_instantiation_closed")
        is False
        and d5_p_state_ps3_actual_gap.get("summary", {}).get("non_circular_ps3_instantiation_closed")
        is False,
        "Newton-Euler D5 P_state PS3 actual instantiation unexpectedly closed",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_state_ps3_actual_gap_p_state_closed") is False
        and d5_p_state_ps3_actual_gap.get("primitive_closed") is False,
        "Newton-Euler D5 P_state PS3 actual gap unexpectedly closes P_state",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_state_ps3_actual_gap_pc2_closed") is False
        and d5_p_state_ps3_actual_gap.get("pc2_closed") is False,
        "Newton-Euler D5 P_state PS3 actual gap unexpectedly closes PC2",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_state_ps3_h_acc_obstruction_recorded") is True
        and d5_p_state_ps3_h_acc_obstruction_summary.get(
            "h_acceleration_input_obstruction_recorded"
        )
        is True,
        "Newton-Euler D5 P_state PS3 h-acc obstruction not recorded",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_state_ps3_h_acc_obstruction_finite_nullity_min")
        == d5_p_state_ps3_h_acc_obstruction_summary.get("finite_probe_nullity_min")
        == 12,
        "Newton-Euler D5 P_state PS3 h-acc obstruction min nullity changed",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_state_ps3_h_acc_obstruction_finite_nullity_max")
        == d5_p_state_ps3_h_acc_obstruction_summary.get("finite_probe_nullity_max")
        == 12,
        "Newton-Euler D5 P_state PS3 h-acc obstruction max nullity changed",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_state_ps3_h_acc_obstruction_residual_only_input_sufficient")
        is False
        and d5_p_state_ps3_h_acc_obstruction_summary.get(
            "residual_only_input_sufficient_for_h_acceleration"
        )
        is False,
        "Newton-Euler D5 P_state PS3 residual-only h-acc input unexpectedly sufficient",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_state_ps3_h_acc_obstruction_independent_h_acc_input_closed")
        is False
        and d5_p_state_ps3_h_acc_obstruction_summary.get(
            "independent_h_weighted_acceleration_input_closed"
        )
        is False,
        "Newton-Euler D5 P_state PS3 h-acc input unexpectedly closed",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_state_ps3_h_acc_obstruction_actual_ps3_closed")
        is False
        and d5_p_state_ps3_h_acc_obstruction_summary.get(
            "ps3_actual_state_lift_conversion_closed"
        )
        is False,
        "Newton-Euler D5 P_state PS3 h-acc obstruction unexpectedly closes actual PS3",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_state_ps3_h_acc_obstruction_pc2_closed") is False
        and d5_p_state_ps3_h_acc_obstruction.get("pc2_closed") is False,
        "Newton-Euler D5 P_state PS3 h-acc obstruction unexpectedly closes PC2",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_state_ps3_h_acc_obstruction_finite_probe_is_proof")
        is False
        and d5_p_state_ps3_h_acc_obstruction.get("finite_probe_is_proof") is False,
        "Newton-Euler D5 P_state PS3 h-acc obstruction finite probe overclaimed as proof",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_state_term_rows")
        == d5_p_state_summary.get("term_rows_using_p_state")
        == 126,
        "Newton-Euler D5 P_state term-row count changed",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_state_future_subproofs_closed")
        == d5_p_state_summary.get("required_future_subproofs_closed")
        == 3,
        "Newton-Euler D5 P_state future subproof closure count changed",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_state_future_subproofs")
        == d5_p_state_summary.get("required_future_subproofs")
        == 4,
        "Newton-Euler D5 P_state future subproof count changed",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_state_induced_bounds_proved")
        == d5_p_state_summary.get("induced_taylor_bounds_proved")
        == 0,
        "Newton-Euler D5 P_state unexpectedly proves induced Taylor bounds",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_state_pc2_closed") is False
        and d5_p_state_gap.get("pc2_closed") is False,
        "Newton-Euler D5 P_state unexpectedly closes PC2",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_acc_map_definition_recorded") is True
        and d5_p_acc_map_definition.get("status") == "p_acc_map_definition_closed_lift_open",
        "Newton-Euler D5 P_acc map-definition audit not recorded",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_acc_map_definition_closed") is True
        and d5_p_acc_map_definition.get("pa1_map_definition_closed") is True,
        "Newton-Euler D5 P_acc map definition not closed",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_acc_map_rows")
        == d5_p_acc_map_summary.get("term_rows_conditionally_mapped")
        == 36,
        "Newton-Euler D5 P_acc map row count changed",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_acc_map_subproofs_closed")
        == d5_p_acc_map_summary.get("closed_subproof_count")
        == 1,
        "Newton-Euler D5 P_acc map subproof count changed",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_acc_map_required_subproofs")
        == d5_p_acc_map_summary.get("required_subproof_count")
        == 4,
        "Newton-Euler D5 P_acc map required subproof count changed",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_acc_map_pc2_closed") is False
        and d5_p_acc_map_definition.get("pc2_closed") is False,
        "Newton-Euler D5 P_acc map definition unexpectedly closes PC2",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_acc_row_binding_recorded") is True
        and d5_p_acc_row_binding.get("status") == "p_acc_row_binding_closed_lift_open",
        "Newton-Euler D5 P_acc row-binding audit not recorded",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_acc_row_binding_closed") is True
        and d5_p_acc_row_binding.get("pa4_row_binding_closed") is True,
        "Newton-Euler D5 P_acc row binding not closed",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_acc_row_binding_rows")
        == d5_p_acc_row_binding_summary.get("term_rows_bound_to_ordering")
        == 36,
        "Newton-Euler D5 P_acc row-binding row count changed",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_acc_row_binding_subproofs_after")
        == d5_p_acc_row_binding_summary.get("p_acc_closed_subproof_count_after_binding")
        == 2,
        "Newton-Euler D5 P_acc row-binding subproof count changed",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_acc_row_binding_required_subproofs")
        == d5_p_acc_row_binding_summary.get("required_subproof_count")
        == 4,
        "Newton-Euler D5 P_acc row-binding required subproof count changed",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_acc_row_binding_pc2_closed") is False
        and d5_p_acc_row_binding.get("pc2_closed") is False,
        "Newton-Euler D5 P_acc row binding unexpectedly closes PC2",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_acc_independence_recorded") is True
        and d5_p_acc_independence.get("status") == "p_acc_independence_closed_lift_open",
        "Newton-Euler D5 P_acc independence audit not recorded",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_acc_independence_closed") is True
        and d5_p_acc_independence.get("pa3_independence_closed") is True,
        "Newton-Euler D5 P_acc independence not closed",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_acc_independence_input_families")
        == d5_p_acc_independence_summary.get("non_dynamic_input_families_certified")
        == 3,
        "Newton-Euler D5 P_acc independence input-family count changed",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_acc_independence_required_input_families")
        == d5_p_acc_independence_summary.get("required_non_dynamic_input_families")
        == 3,
        "Newton-Euler D5 P_acc independence required input-family count changed",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_acc_independence_subproofs_after")
        == d5_p_acc_independence_summary.get("p_acc_closed_subproof_count_after_independence")
        == 3,
        "Newton-Euler D5 P_acc independence subproof count changed",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_acc_independence_required_subproofs")
        == d5_p_acc_independence_summary.get("required_subproof_count")
        == 4,
        "Newton-Euler D5 P_acc independence required subproof count changed",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_acc_independence_pc2_closed") is False
        and d5_p_acc_independence.get("pc2_closed") is False,
        "Newton-Euler D5 P_acc independence unexpectedly closes PC2",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_acc_pa2_obstruction_recorded") is True
        and d5_p_acc_lift_obstruction.get("status") == "p_acc_pa2_obstruction_recorded_lift_open",
        "Newton-Euler D5 P_acc PA2 obstruction audit not recorded",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_acc_pa2_closed") is False
        and d5_p_acc_lift_obstruction.get("pa2_closed") is False,
        "Newton-Euler D5 P_acc PA2 unexpectedly closed",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_acc_velocity_collocation_alone_sufficient") is False
        and d5_p_acc_lift_obstruction.get("velocity_collocation_alone_sufficient_for_O_h7_acceleration")
        is False,
        "Newton-Euler D5 P_acc velocity-collocation-alone sufficiency overclaimed",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_acc_current_unweighted_acceleration_rate")
        == d5_p_acc_lift_obstruction.get("current_recorded_inputs_imply_only_unweighted_acceleration_rate")
        == "O(h^6)",
        "Newton-Euler D5 P_acc current acceleration rate changed",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_acc_lift_rate_proved") is False
        and d5_p_acc_lift_obstruction.get("acceleration_lift_rate_proved") is False,
        "Newton-Euler D5 P_acc lift rate unexpectedly proved",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_acc_lift_obstruction_term_bounds_proved")
        == d5_p_acc_lift_obstruction.get("term_bounds_proved")
        == 0,
        "Newton-Euler D5 P_acc lift obstruction unexpectedly proves term bounds",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_acc_lift_obstruction_pc2_closed") is False
        and d5_p_acc_lift_obstruction.get("pc2_closed") is False,
        "Newton-Euler D5 P_acc lift obstruction unexpectedly closes PC2",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_acc_pa2_weighted_inverse_recorded") is True
        and d5_p_acc_pa2_weighted_inverse.get("pa2_weighted_inverse_probe_recorded") is True,
        "Newton-Euler D5 P_acc PA2 weighted-inverse audit not recorded",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_acc_pa2_weighted_h_control_recorded") is True
        and d5_p_acc_pa2_weighted_inverse.get("weighted_h_acceleration_control_recorded") is True,
        "Newton-Euler D5 P_acc PA2 weighted-h control diagnostic not recorded",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_acc_pa2_weighted_inverse_probe_count")
        == d5_p_acc_pa2_weighted_inverse_summary.get("probe_count")
        == 3,
        "Newton-Euler D5 P_acc PA2 weighted-inverse probe count changed",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_acc_pa2_weighted_inverse_full_rank_all") is True
        and d5_p_acc_pa2_weighted_inverse_summary.get("finite_probe_full_column_rank_all") is True,
        "Newton-Euler D5 P_acc PA2 weighted-inverse finite probes lost full-rank status",
    )
    checks.check(
        close_to(
            evidence.get("newton_euler_d5_p_acc_pa2_max_unweighted_acceleration_projection_constant"),
            d5_p_acc_pa2_weighted_inverse_summary.get(
                "max_unweighted_acceleration_projection_constant"
            ),
        )
        and float(
            evidence.get("newton_euler_d5_p_acc_pa2_max_unweighted_acceleration_projection_constant")
        )
        > 0.0,
        "Newton-Euler D5 P_acc PA2 unweighted acceleration projection constant changed",
    )
    checks.check(
        close_to(
            evidence.get("newton_euler_d5_p_acc_pa2_max_weighted_h_acceleration_projection_constant"),
            d5_p_acc_pa2_weighted_inverse_summary.get(
                "max_weighted_h_acceleration_projection_constant"
            ),
        )
        and float(
            evidence.get("newton_euler_d5_p_acc_pa2_max_weighted_h_acceleration_projection_constant")
        )
        > 0.0,
        "Newton-Euler D5 P_acc PA2 weighted-h acceleration projection constant changed",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_acc_pa2_unweighted_uniform_control_proved") is False
        and d5_p_acc_pa2_weighted_inverse.get("unweighted_acceleration_uniform_control_proved")
        is False,
        "Newton-Euler D5 P_acc PA2 unweighted uniform control unexpectedly proved",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_acc_pa2_weighted_inverse_pa2_closed") is False
        and d5_p_acc_pa2_weighted_inverse.get("pa2_closed") is False,
        "Newton-Euler D5 P_acc PA2 weighted-inverse audit unexpectedly closes PA2",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_acc_pa2_weighted_inverse_pc2_closed") is False
        and d5_p_acc_pa2_weighted_inverse.get("pc2_closed") is False,
        "Newton-Euler D5 P_acc PA2 weighted-inverse audit unexpectedly closes PC2",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_lambda_interface_recorded") is True
        and d5_p_lambda_interface.get("status") == "p_lambda_interface_closed_lift_open",
        "Newton-Euler D5 P_lambda interface audit not recorded",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_lambda_interface_closed") is True
        and d5_p_lambda_interface.get("pl1_interface_closed") is True,
        "Newton-Euler D5 P_lambda interface not closed",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_lambda_pl2_geometric_margin_recorded") is True
        and d5_p_lambda_pl2_geometric_margin.get("status")
        == "pl2_uniform_inf_sup_bound_proved_p_lambda_rate_open",
        "Newton-Euler D5 P_lambda PL2 geometric-margin audit not recorded",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_lambda_pl2_uniform_inf_sup_bound_proved") is True
        and d5_p_lambda_pl2_geometric_margin.get("pl2_uniform_inf_sup_bound_proved") is True,
        "Newton-Euler D5 P_lambda PL2 uniform inf-sup subproof not closed",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_lambda_pl2_symbolic_margin_premise_proved") is True
        and d5_p_lambda_pl2_summary.get("symbolic_margin_premise_proved") is True,
        "Newton-Euler D5 P_lambda PL2 symbolic margin premise not proved",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_lambda_pl2_probe_stage_rows")
        == d5_p_lambda_pl2_summary.get("probe_stage_rows")
        == 9,
        "Newton-Euler D5 P_lambda PL2 probe row count changed",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_lambda_pl2_finite_probe_sufficient_for_uniform_proof") is False
        and d5_p_lambda_pl2_implication.get("finite_probe_sufficient_for_uniform_proof") is False,
        "Newton-Euler D5 P_lambda PL2 finite probes incorrectly promoted to proof",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_lambda_pl2_primitive_closed") is False
        and d5_p_lambda_pl2_geometric_margin.get("primitive_closed") is False,
        "Newton-Euler D5 P_lambda PL2 unexpectedly closes P_lambda",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_lambda_pl2_pc2_closed") is False
        and d5_p_lambda_pl2_geometric_margin.get("pc2_closed") is False,
        "Newton-Euler D5 P_lambda PL2 unexpectedly closes PC2",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_lambda_d3_noncircularity_recorded") is True
        and d5_p_lambda_d3_noncircularity.get("status")
        == "p_lambda_d3_noncircularity_closed_lift_open",
        "Newton-Euler D5 P_lambda D3 non-circularity audit not recorded",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_lambda_d3_noncircularity_closed") is True
        and d5_p_lambda_d3_noncircularity.get("pl3_d3_noncircularity_closed") is True,
        "Newton-Euler D5 P_lambda PL3 non-circularity not closed",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_lambda_stage_variables")
        == d5_p_lambda_summary.get("stage_lambda_variables")
        == 24,
        "Newton-Euler D5 P_lambda stage variable count changed",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_lambda_direct_rows")
        == d5_p_lambda_summary.get("direct_multiplier_term_rows")
        == 36,
        "Newton-Euler D5 P_lambda direct row count changed",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_lambda_term_rows")
        == d5_p_lambda_summary.get("term_rows_using_p_lambda")
        == 72,
        "Newton-Euler D5 P_lambda primitive term row count changed",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_lambda_pl4_rate_propagation_recorded") is True
        and d5_p_lambda_pl4_rate_propagation.get("status")
        == "p_lambda_pl4_rate_propagation_closed_conditionally_lift_open",
        "Newton-Euler D5 P_lambda PL4 propagation not recorded",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_lambda_pl4_rate_propagation_closed") is True
        and d5_p_lambda_pl4_rate_propagation.get("pl4_lift_propagation_closed") is True,
        "Newton-Euler D5 P_lambda PL4 propagation not closed",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_lambda_pl4_conditional_multiplier_rate") is True
        and d5_p_lambda_pl4_rate_propagation.get("conditional_multiplier_lift_rate_proved") is True,
        "Newton-Euler D5 P_lambda PL4 conditional rate missing",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_lambda_pl4_actual_multiplier_rate") is False
        and d5_p_lambda_pl4_rate_propagation.get("multiplier_lift_rate_proved") is False,
        "Newton-Euler D5 P_lambda PL4 unexpectedly proves actual multiplier rate",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_lambda_pl4_open_input_dependencies")
        == d5_p_lambda_pl4_summary.get("open_input_dependency_count")
        == 2,
        "Newton-Euler D5 P_lambda PL4 open input dependency count changed",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_lambda_subproofs_after")
        == d5_p_lambda_pl4_summary.get("p_lambda_closed_subproof_count_after_pl4")
        == 4,
        "Newton-Euler D5 P_lambda subproof count changed",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_lambda_open_subproofs_after")
        == d5_p_lambda_pl4_summary.get("open_subproof_count_after_pl4")
        == 0,
        "Newton-Euler D5 P_lambda open subproof count changed",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_lambda_required_subproofs")
        == d5_p_lambda_summary.get("required_subproof_count")
        == 4,
        "Newton-Euler D5 P_lambda required subproof count changed",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_lambda_conditional_pl_subproofs_complete") is True,
        "Newton-Euler D5 P_lambda conditional PL subproof completion boundary missing",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_lambda_actual_multiplier_lift_open") is True,
        "Newton-Euler D5 P_lambda actual lift-open boundary missing",
    )
    checks.check(
        "PL1/PL2/PL3/PL4 subproof count is complete"
        in evidence.get("newton_euler_d5_p_lambda_conditional_subproof_scope", "")
        and "conditional propagation mechanism"
        in evidence.get("newton_euler_d5_p_lambda_conditional_subproof_scope", "")
        and "open P_state and P_acc inputs"
        in evidence.get("newton_euler_d5_p_lambda_conditional_subproof_scope", "")
        and "no primitive Taylor subterm"
        in evidence.get("newton_euler_d5_p_lambda_conditional_subproof_scope", ""),
        "Newton-Euler D5 P_lambda conditional subproof scope text missing",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_lambda_primitive_closed") is False
        and d5_p_lambda_interface.get("primitive_closed") is False,
        "Newton-Euler D5 P_lambda primitive unexpectedly closed",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_lambda_pc2_closed") is False
        and d5_p_lambda_interface.get("pc2_closed") is False,
        "Newton-Euler D5 P_lambda unexpectedly closes PC2",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_geom_reduction_recorded") is True
        and d5_p_geom_reduction.get("status") == "p_geom_chart_reduction_closed_primitive_open",
        "Newton-Euler D5 P_geom reduction not recorded",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_geom_chart_reduction_closed") is True
        and d5_p_geom_reduction.get("chart_reduction_closed") is True,
        "Newton-Euler D5 P_geom chart reduction not closed",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_geom_actual_primitive_open") is True,
        "Newton-Euler D5 P_geom actual primitive-open boundary missing",
    )
    checks.check(
        "downstream conditional Lipschitz map"
        in evidence.get("newton_euler_d5_p_geom_conditional_reduction_scope", "")
        and "open P_state and P_lambda inputs"
        in evidence.get("newton_euler_d5_p_geom_conditional_reduction_scope", "")
        and "no primitive Taylor subterm"
        in evidence.get("newton_euler_d5_p_geom_conditional_reduction_scope", ""),
        "Newton-Euler D5 P_geom conditional reduction scope text missing",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_geom_closed_subproofs")
        == d5_p_geom_summary.get("closed_subproof_count")
        == 3,
        "Newton-Euler D5 P_geom closed subproof count changed",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_geom_required_subproofs")
        == d5_p_geom_summary.get("required_subproof_count")
        == 4,
        "Newton-Euler D5 P_geom required subproof count changed",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_geom_open_dependencies")
        == d5_p_geom_summary.get("open_dependency_count")
        == 2,
        "Newton-Euler D5 P_geom dependency count changed",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_geom_conditionally_reduced_rows")
        == d5_p_geom_summary.get("term_rows_conditionally_reduced")
        == 36,
        "Newton-Euler D5 P_geom reduced row count changed",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_geom_translational_rows")
        == d5_p_geom_summary.get("translational_rows_conditionally_reduced")
        == 18,
        "Newton-Euler D5 P_geom translational row count changed",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_geom_rotational_rows")
        == d5_p_geom_summary.get("rotational_rows_conditionally_reduced")
        == 18,
        "Newton-Euler D5 P_geom rotational row count changed",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_geom_primitive_closed") is False
        and d5_p_geom_reduction.get("primitive_closed") is False,
        "Newton-Euler D5 P_geom primitive unexpectedly closed",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_geom_pc2_closed") is False
        and d5_p_geom_reduction.get("pc2_closed") is False,
        "Newton-Euler D5 P_geom unexpectedly closes PC2",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_gyro_reduction_recorded") is True
        and d5_p_gyro_reduction.get("status") == "p_gyro_bilinear_reduction_closed_primitive_open",
        "Newton-Euler D5 P_gyro reduction not recorded",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_gyro_algebraic_reduction_closed") is True
        and d5_p_gyro_reduction.get("algebraic_reduction_closed") is True,
        "Newton-Euler D5 P_gyro algebraic reduction not closed",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_gyro_internal_reduction_complete_not_primitive") is True,
        "Newton-Euler D5 P_gyro internal/primitive boundary missing",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_gyro_actual_primitive_open") is True,
        "Newton-Euler D5 P_gyro actual primitive-open boundary missing",
    )
    checks.check(
        "internal bilinear gyroscopic reduction"
        in evidence.get("newton_euler_d5_p_gyro_conditional_reduction_scope", "")
        and "open P_state angular-velocity input"
        in evidence.get("newton_euler_d5_p_gyro_conditional_reduction_scope", "")
        and "no primitive Taylor subterm"
        in evidence.get("newton_euler_d5_p_gyro_conditional_reduction_scope", ""),
        "Newton-Euler D5 P_gyro conditional reduction scope text missing",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_gyro_closed_subproofs")
        == d5_p_gyro_summary.get("closed_subproof_count")
        == 3,
        "Newton-Euler D5 P_gyro closed subproof count changed",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_gyro_required_subproofs")
        == d5_p_gyro_summary.get("required_subproof_count")
        == 3,
        "Newton-Euler D5 P_gyro required subproof count changed",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_gyro_open_dependencies")
        == d5_p_gyro_summary.get("open_dependency_count")
        == 1,
        "Newton-Euler D5 P_gyro dependency count changed",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_gyro_conditionally_reduced_rows")
        == d5_p_gyro_summary.get("term_rows_conditionally_reduced")
        == 18,
        "Newton-Euler D5 P_gyro reduced row count changed",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_gyro_primitive_closed") is False
        and d5_p_gyro_reduction.get("primitive_closed") is False,
        "Newton-Euler D5 P_gyro primitive unexpectedly closed",
    )
    checks.check(
        evidence.get("newton_euler_d5_p_gyro_pc2_closed") is False
        and d5_p_gyro_reduction.get("pc2_closed") is False,
        "Newton-Euler D5 P_gyro unexpectedly closes PC2",
    )
    checks.check(
        evidence.get("newton_euler_d5_primitive_closure_plan_obligations")
        == d5_primitive_closure_summary.get("primitive_obligation_count")
        == 6,
        "Newton-Euler D5 primitive closure-plan obligation count changed",
    )
    checks.check(
        evidence.get("newton_euler_d5_primitive_closure_plan_interfaces")
        == d5_primitive_closure_summary.get("primitive_obligations_with_closure_steps")
        == 6,
        "Newton-Euler D5 primitive closure-plan interface count changed",
    )
    checks.check(
        evidence.get("newton_euler_d5_primitive_closure_plan_proved")
        == d5_primitive_closure_summary.get("primitive_obligations_proved")
        == 1,
        "Newton-Euler D5 primitive closure plan proved count changed",
    )
    checks.check(
        evidence.get("newton_euler_d5_primitive_closure_plan_open")
        == d5_primitive_closure_summary.get("open_primitive_obligations")
        == 5,
        "Newton-Euler D5 primitive closure-plan open count changed",
    )
    checks.check(
        evidence.get("newton_euler_d5_primitive_closure_plan_induced_bounds_proved")
        == d5_primitive_closure_summary.get("induced_taylor_bounds_proved")
        == 0,
        "Newton-Euler D5 primitive closure plan unexpectedly proves induced Taylor bounds",
    )
    checks.check(
        evidence.get("newton_euler_d5_primitive_closure_plan_pc2_closed") is False
        and d5_primitive_closure_plan.get("pc2_closed") is False,
        "Newton-Euler D5 primitive closure plan unexpectedly closes PC2",
    )
    checks.check(
        evidence.get("newton_euler_d5_primitive_closure_plan_manifest_linked") is True,
        "Newton-Euler D5 primitive closure plan is not linked",
    )
    checks.check(
        evidence.get("newton_euler_d5_conditional_taylor_certificate_terms")
        == d5_conditional_taylor_summary.get("term_rows")
        == 162,
        "Newton-Euler D5 conditional Taylor certificate term count changed",
    )
    checks.check(
        evidence.get("newton_euler_d5_conditional_taylor_certificate_rows")
        == d5_conditional_taylor_summary.get("dynamic_rows")
        == 36,
        "Newton-Euler D5 conditional Taylor certificate row count changed",
    )
    checks.check(
        evidence.get("newton_euler_d5_conditional_taylor_certificate_conditional_terms")
        == d5_conditional_taylor_summary.get("conditional_term_bounds_under_open_primitive_assumptions")
        == 162,
        "Newton-Euler D5 conditional Taylor term coverage changed",
    )
    checks.check(
        evidence.get("newton_euler_d5_conditional_taylor_certificate_conditional_rows")
        == d5_conditional_taylor_summary.get("conditional_dynamic_rows_under_open_primitive_assumptions")
        == 36,
        "Newton-Euler D5 conditional Taylor row coverage changed",
    )
    checks.check(
        evidence.get("newton_euler_d5_conditional_taylor_certificate_actual_terms_proved")
        == d5_conditional_taylor_summary.get("actual_taylor_bounds_proved")
        == 0,
        "Newton-Euler D5 conditional certificate unexpectedly proves Taylor bounds",
    )
    checks.check(
        evidence.get("newton_euler_d5_conditional_taylor_certificate_open_primitive_assumptions")
        == d5_conditional_taylor_summary.get("open_primitive_assumption_count")
        == 5,
        "Newton-Euler D5 conditional certificate open-primitive count changed",
    )
    checks.check(
        evidence.get("newton_euler_d5_conditional_taylor_certificate_pc2_closed") is False
        and d5_conditional_taylor_certificate.get("pc2_closed") is False,
        "Newton-Euler D5 conditional Taylor certificate unexpectedly closes PC2",
    )
    checks.check(
        evidence.get("newton_euler_d5_conditional_taylor_certificate_manifest_linked") is True
        and d5_conditional_taylor_certificate.get("status")
        == "conditional_taylor_certificate_recorded_primitive_taylor_pc2_open",
        "Newton-Euler D5 conditional Taylor certificate is not linked",
    )
    checks.check(
        d5_conditional_taylor_certificate.get("conditional_certificate_only") is True,
        "Newton-Euler D5 conditional Taylor certificate lost conditional-only marker",
    )
    checks.check(
        d5_conditional_taylor_certificate.get("stage_residual_O_h7_implementation_defect_proved") is False,
        "Newton-Euler D5 conditional Taylor certificate overclaims implementation defect proof",
    )
    checks.check(
        evidence.get("newton_euler_d5_open_primitive_gap_recorded") is True
        and d5_open_primitive_gap.get("status")
        == "open_primitive_gaps_recorded_primitive_taylor_pc2_open",
        "Newton-Euler D5 open primitive gap audit not recorded",
    )
    checks.check(
        evidence.get("newton_euler_d5_open_primitive_gap_count")
        == d5_open_primitive_summary.get("open_primitive_count")
        == 5,
        "Newton-Euler D5 open primitive gap count changed",
    )
    checks.check(
        evidence.get("newton_euler_d5_open_primitive_gap_future_subproofs")
        == d5_open_primitive_summary.get("total_future_subproofs")
        == 19,
        "Newton-Euler D5 open primitive future-subproof count changed",
    )
    checks.check(
        evidence.get("newton_euler_d5_open_primitive_gap_future_subproofs_closed")
        == d5_open_primitive_summary.get("future_subproofs_closed")
        == 16,
        "Newton-Euler D5 open primitive future subproof closure count changed",
    )
    checks.check(
        evidence.get("newton_euler_d5_open_primitive_gap_induced_bounds_proved")
        == d5_open_primitive_summary.get("induced_taylor_bounds_proved")
        == 0,
        "Newton-Euler D5 open primitive audit unexpectedly proves induced bounds",
    )
    checks.check(
        evidence.get("newton_euler_d5_open_primitive_gap_pc2_closed") is False
        and d5_open_primitive_gap.get("pc2_closed") is False,
        "Newton-Euler D5 open primitive audit unexpectedly closes PC2",
    )
    checks.check(evidence.get("residual_to_error_blocking_obligations") == 7, "residual-to-error blocker count changed")
    checks.check(evidence.get("formula_row_ad_jacobian_probe_count") == 3, "AD Jacobian probe count changed")
    checks.check(
        close_to(evidence.get("formula_row_ad_jacobian_max_mismatch"), 3.330669e-16, 1.0e-21),
        "AD Jacobian max mismatch changed",
    )
    checks.check(
        close_to(evidence.get("smooth_projected_position_order"), 7.160828003417387),
        "smooth projected position order changed",
    )
    checks.check(
        close_to(evidence.get("smooth_projected_velocity_order"), 7.066182539651858),
        "smooth projected velocity order changed",
    )
    checks.check(
        close_to(evidence.get("endpoint_raw_position_constraint_fit"), 5.985100758394371),
        "endpoint position fit changed",
    )
    checks.check(
        close_to(evidence.get("endpoint_raw_velocity_constraint_fit"), 6.072290794930567),
        "endpoint velocity fit changed",
    )
    checks.check(
        close_to(evidence.get("smooth_reference_eta_over_h7"), 3584.657362964853),
        "eta/h^7 diagnostic changed",
    )
    checks.check(closure.get("proof_gap_closed") is True, "proof gap must be closed by direct substitution")
    checks.check(closure.get("direct_pc2_proof_gap_closed") is True, "scoped direct PC2 proof closure missing")
    checks.check(
        closure.get("proof_gap_closed_scope")
        == "direct_residual_bridge_kantorovich_route_closed_primitive_taylor_conditional_schema_open",
        "proof gap scope marker missing",
    )
    checks.check(closure.get("dynamic_symbolic_oracle_complete") is False, "dynamic symbolic oracle must remain open")
    checks.check(
        closure.get("stage_residual_O_h7_implementation_defect_proved") is True,
        "O(h^7) implementation-defect proof not closed by direct substitution",
    )
    checks.check(closure.get("pc2_closed_by_direct_substitution") is True, "PC2 direct-substitution closure missing")
    checks.check(closure.get("primitive_lift_route_closed") is False, "primitive lift route should remain open")
    checks.check(
        strict_taylor.get("status")
        == "closed_by_direct_residual_bridge_kantorovich_route_primitive_taylor_conditional_schema_open",
        "direct residual-bridge submission-standard status changed",
    )
    checks.check(
        strict_taylor.get("required_pc2_route") == "direct_residual_bridge_kantorovich_route",
        "direct residual-bridge PC2 route requirement changed",
    )
    checks.check(strict_taylor.get("satisfied") is True, "direct residual-bridge route not satisfied")
    checks.check(
        strict_taylor.get("proof_gap_closed_under_active_direct_residual_bridge_standard") is True,
        "direct residual-bridge proof gap not closed by direct route",
    )
    checks.check(
        strict_taylor.get("not_primitive_162_term_taylor_closure") is True,
        "direct residual-bridge primitive-route scope flag missing",
    )
    checks.check(
        strict_taylor.get("direct_substitution_supplies_active_pc2_residual_bridge") is True,
        "direct residual evidence not accepted as active PC2 residual-bridge input",
    )
    checks.check(
        strict_taylor.get("direct_residual_bridge_kantorovich_route_closed") is True,
        "direct residual-bridge/Kantorovich route not closed",
    )
    for key in [
        "theorem_invocation_consumes_one_residual_value_certificate",
        "future_primitive_taylor_certificate_replacement_only",
        "future_primitive_taylor_requires_same_tuple_132_row_bound",
        "future_primitive_taylor_may_not_append_lower_remove_or_promote",
    ]:
        checks.check(
            strict_taylor.get(key) is True and strict_direct.get(key) is True,
            f"strict direct residual-bridge certificate-consumption boundary missing: {key}",
        )
    checks.check(
        strict_taylor.get("active_standard_name") == "strict_direct_residual_bridge_submission_standard"
        and "legacy_key_retained_for_validator_compatibility" not in strict_taylor,
        "direct residual-bridge active standard missing or stale legacy key still present",
    )
    checks.check(
        strict_direct.get("required_pc2_route") == "direct_residual_bridge_kantorovich_route"
        and strict_direct.get("satisfied") is True
        and strict_direct.get("primitive_taylor_route_closed") is False,
        "strict direct residual-bridge alias changed",
    )
    checks.check(
        strict_direct.get("not_primitive_162_term_taylor_closure") is True,
        "strict direct residual-bridge primitive-route scope flag missing",
    )
    checks.check(
        strict_taylor.get("primitive_route_required_for_b3_closure") is False,
        "primitive route should be diagnostic, not required for B3 closure",
    )
    checks.check(
        strict_taylor.get("primitive_taylor_route_closed") is False,
        "diagnostic primitive route unexpectedly closed",
    )
    checks.check(
        strict_taylor.get("primitive_taylor_schema_role")
        == (
            "conditional Newton-Euler primitive Taylor certificate schema; "
            "non-load-bearing under the active direct PC2 residual-bridge route"
        ),
        "strict Taylor conditional-schema role changed",
    )
    checks.check(
        strict_taylor.get("primitive_taylor_schema_current_instance_available") is False,
        "strict Taylor conditional schema unexpectedly has a current instance",
    )
    checks.check(
        strict_taylor.get("primitive_taylor_schema_blocker_summary")
        == "0/162 Taylor bounds certified; five primitive lift/bilinear antecedents remain open",
        "strict Taylor conditional-schema blocker summary changed",
    )
    checks.check(
        strict_taylor.get("actual_taylor_bounds_proved")
        == d5_conditional_taylor_summary.get("actual_taylor_bounds_proved")
        == 0,
        "strict Taylor actual bound count changed",
    )
    checks.check(
        strict_taylor.get("certified_taylor_bound_terms")
        == d5_term_summary.get("certified_taylor_bound_terms")
        == 0,
        "strict Taylor certified term count changed",
    )
    checks.check(
        strict_taylor.get("open_taylor_bound_terms")
        == d5_term_summary.get("open_taylor_bound_terms")
        == 162,
        "strict Taylor open term count changed",
    )
    checks.check(
        strict_taylor.get("strict_taylor_reduction_terms")
        == d5_term_summary.get("strict_taylor_reduction_terms")
        == 162,
        "strict Taylor reduction count changed",
    )
    checks.check(
        strict_taylor.get("terms_with_open_primitive_blockers")
        == d5_term_summary.get("terms_with_open_primitive_blockers")
        == 162,
        "strict Taylor primitive blocker term count changed",
    )
    checks.check(
        strict_taylor.get("open_primitive_assumption_count")
        == d5_conditional_taylor_summary.get("open_primitive_assumption_count")
        == 5,
        "strict Taylor open primitive assumption count changed",
    )
    checks.check(
        strict_taylor.get("open_primitive_count") == d5_open_primitive_summary.get("open_primitive_count") == 5,
        "strict Taylor open primitive count changed",
    )
    checks.check(
        strict_taylor.get("primitive_obligations_proved")
        == d5_primitive_summary.get("primitive_obligations_proved")
        == 1,
        "strict Taylor proved primitive count changed",
    )
    checks.check(
        strict_taylor.get("primitive_obligation_count")
        == d5_primitive_summary.get("primitive_obligation_count")
        == 6,
        "strict Taylor primitive obligation count changed",
    )
    checks.check(
        strict_taylor.get("h_weighted_acceleration_sufficient_terms")
        == d5_term_summary.get("h_weighted_acceleration_sufficient_terms")
        == 0,
        "strict Taylor h-weighted acceleration unexpectedly sufficient",
    )
    checks.check(
        strict_taylor.get("h_weighted_acceleration_insufficient_terms")
        == d5_term_summary.get("h_weighted_acceleration_insufficient_terms")
        == 36,
        "strict Taylor h-weighted acceleration insufficiency count changed",
    )
    checks.check(closure.get("eta_h_O_h7_solver_policy_evidence") is False, "eta_h proof must remain open")
    checks.check(
        closure.get("fixed_tolerance_runs_are_asymptotic_proof") is False,
        "fixed-tolerance proof boundary changed",
    )
    checks.check(
        closure.get("accepted_residual_to_error_theorem") is False,
        "residual-to-error transfer theorem must remain open",
    )
    checks.check(closure.get("full_tfe_stage_replacement") is False, "full TFE marker changed")
    checks.check(closure.get("submission_ready") is False, "closure state must not mark submission ready")
    checks.check(oracle.get("runtime_formula_row_oracle_complete") is True, "runtime formula oracle missing")
    checks.check(oracle.get("runtime_ad_oracle_complete") is True, "runtime AD oracle missing")
    checks.check(
        oracle.get("independent_symbolic_row_oracle_complete") is False,
        "symbolic row oracle unexpectedly complete",
    )
    checks.check(oracle.get("newton_euler_formula_oracle_complete") is True, "Newton-Euler formula oracle missing")
    checks.check(
        oracle.get("newton_euler_symbolic_target_inventory_complete") is True,
        "Newton-Euler symbolic target inventory marker missing",
    )
    checks.check(
        oracle.get("newton_euler_obligation_coverage_matrix_complete") is True,
        "Newton-Euler obligation coverage marker missing",
    )
    checks.check(solver.get("summary_level_solver_residuals_recorded") is True, "solver residual marker missing")
    checks.check(
        solver.get("finite_scaled_tolerance_probe_recorded") is True,
        "finite scaled-tolerance probe marker missing",
    )
    checks.check(solver.get("finite_scaled_tolerance_probe_ok_rows") == 4, "finite probe ok row count changed")
    checks.check(solver.get("finite_scaled_tolerance_probe_total_rows") == 4, "finite probe total row count changed")
    checks.check(
        float(solver.get("finite_scaled_tolerance_probe_max_residual_over_h7", math.inf)) < 1.0e4,
        "finite probe residual/h7 exceeds c_eta",
    )
    checks.check(
        solver.get("finite_scaled_tolerance_trajectory_probe_recorded") is True,
        "finite scaled-tolerance trajectory probe marker missing",
    )
    checks.check(
        solver.get("finite_scaled_tolerance_trajectory_probe_ok_rows") == 4,
        "finite trajectory probe ok row count changed",
    )
    checks.check(
        solver.get("finite_scaled_tolerance_trajectory_probe_total_rows") == 4,
        "finite trajectory probe total row count changed",
    )
    checks.check(
        solver.get("finite_scaled_tolerance_trajectory_probe_total_steps_checked") == 30,
        "finite trajectory probe step count changed",
    )
    checks.check(
        float(solver.get("finite_scaled_tolerance_trajectory_probe_max_residual_over_h7", math.inf)) < 1.0e4,
        "finite trajectory probe residual/h7 exceeds c_eta",
    )
    checks.check(
        solver.get("finite_tolerance_regime_sweep_recorded") is True,
        "finite tolerance-regime sweep marker missing",
    )
    checks.check(
        solver.get("finite_h_scaled_tolerance_sweep_recorded") is True,
        "finite h-scaled tolerance-regime sweep marker missing",
    )
    checks.check(
        solver.get("finite_h_scaled_tolerance_sweep_policy_names") == ["scaled_h7_c1e4", "scaled_h8_c1e6"],
        "finite h-scaled tolerance-regime policy names changed",
    )
    checks.check(solver.get("finite_h_scaled_tolerance_sweep_rows") == 8, "finite h-scaled row count changed")
    checks.check(solver.get("finite_h_scaled_tolerance_sweep_steps") == 60, "finite h-scaled step count changed")
    checks.check(
        float(solver.get("finite_h_scaled_tolerance_sweep_velocity_order_floor", math.nan)) > 6.0,
        "finite h-scaled velocity order floor too small",
    )
    checks.check(solver.get("finite_tolerance_regime_sweep_policy_count") == 3, "finite tolerance-regime policy count changed")
    checks.check(solver.get("finite_tolerance_regime_sweep_total_rows") == 12, "finite tolerance-regime row count changed")
    checks.check(solver.get("finite_tolerance_regime_sweep_total_steps") == 90, "finite tolerance-regime step count changed")
    checks.check(solver.get("scaled_tolerance_sweep_recorded") is False, "scaled tolerance sweep unexpectedly closed")
    checks.check(solver.get("eta_h_O_h7_solver_policy_evidence") is False, "solver eta_h proof unexpectedly closed")
    checks.check(
        solver.get("per_step_newton_tolerance_policy")
        == (
            "eta_h^tube <= c_eta h^7 on the compact proof tube; reported-grid eta_h^reported = "
            "max_{0<=n<N} eta_{h,n} is only its accepted branch-selected trajectory specialization"
        ),
        "per-step Newton tolerance policy missing from manifest",
    )
    checks.check(
        solver.get("same_reduced_chart_initial_state_required") is True,
        "same reduced-chart initial state requirement missing from manifest",
    )
    checks.check(
        solver.get("branch_selected_newton_solves_required") is True
        and solver.get("newton_iterates_initialized_from_gauss_predictor_required") is True,
        "Gauss-predictor branch-selected Newton solve requirement missing from manifest",
    )
    checks.check(
        solver.get("arbitrary_newton_initializations_select_branch") is False
        and solver.get("remote_nonlinear_roots_select_branch") is False,
        "manifest overclaims branch selection for arbitrary Newton roots",
    )
    checks.check(
        solver.get("gauss_truncation_bound_has_explicit_uniform_constant") is True,
        "manifest missing explicit Gauss truncation constant marker",
    )
    checks.check(
        solver.get("gauss_truncation_constant_uniform_on_compact_trajectory_tube") is True,
        "manifest missing compact-trajectory-tube Gauss constant marker",
    )
    checks.check(
        solver.get("stage_residual_to_root_bound_has_explicit_constant") is True,
        "manifest missing explicit stage residual-to-root constant marker",
    )
    checks.check(
        solver.get("stage_residual_to_root_constant_formula") == "C_Z = 2 M C_R",
        "manifest stage residual-to-root formula changed",
    )
    checks.check(
        solver.get("stage_root_endpoint_perturbation_constant_formula") == "C_A = M_E C_Z",
        "manifest stage-root endpoint perturbation formula changed",
    )
    checks.check(
        solver.get("accepted_root_existence_proved_by_stage_residual_lemma") is True,
        "manifest accepted root existence is not marked as proved by stage-residual lemma",
    )
    checks.check(
        solver.get("accepted_root_existence_not_assumed_as_isolated_root_premise") is True,
        "manifest accepted root existence is still treated as an isolated-root premise",
    )
    checks.check(
        solver.get("endpoint_closure_raw_defect_bound_has_explicit_constant") is True,
        "manifest missing explicit endpoint-closure raw-defect constant marker",
    )
    checks.check(
        solver.get("endpoint_closure_raw_defect_constant_symbol") == "C_{E,raw}",
        "manifest endpoint-closure raw-defect constant symbol changed",
    )
    checks.check(
        solver.get("endpoint_closure_perturbation_bound_has_explicit_constant") is True,
        "manifest missing explicit endpoint-closure perturbation constant marker",
    )
    checks.check(
        solver.get("endpoint_closure_perturbation_constant_formula") == "C_E = 4 M_E^ri C_{E,raw}",
        "manifest endpoint-closure perturbation constant formula changed",
    )
    checks.check(
        solver.get("local_defect_constants_uniform_on_compact_proof_tube") is True,
        "manifest missing compact-tube uniform local-defect constant marker",
    )
    checks.check(
        solver.get("local_defect_constants_uniform_over_accepted_steps") is True,
        "manifest missing accepted-step uniform local-defect constant marker",
    )
    checks.check(
        solver.get("newton_error_controlled_by_compact_tube_eta_h_envelope") is True,
        "manifest missing compact-tube eta_h envelope marker",
    )
    checks.check(
        solver.get("newton_error_controlled_by_single_accepted_branch_eta_h_max") is True,
        "manifest missing legacy reported-grid eta_h maximum compatibility marker",
    )
    checks.check(
        solver.get("newton_residual_to_stage_bound_has_explicit_constant") is True,
        "manifest missing explicit Newton residual-to-stage constant marker",
    )
    checks.check(
        solver.get("newton_endpoint_output_map") == "P_h = C_h o E_h",
        "manifest Newton endpoint-output map binding changed",
    )
    checks.check(
        solver.get("newton_endpoint_output_map_bound")
        == "||P_h(Ztilde_A)-P_h(Z_A)|| <= C_N eta_h",
        "manifest Newton endpoint-output perturbation bound changed",
    )
    checks.check(
        solver.get("newton_endpoint_output_map_derivative_bound_includes_closure") is True,
        "manifest Newton endpoint-output derivative bound does not include closure",
    )
    checks.check(
        solver.get("newton_endpoint_output_map_lipschitz_constant_symbol") == "M_N",
        "manifest Newton endpoint-output Lipschitz constant symbol changed",
    )
    checks.check(
        solver.get("newton_residual_to_endpoint_perturbation_constant_formula") == "C_N = 2 M_A M_N",
        "manifest Newton residual-to-endpoint constant formula changed",
    )
    checks.check(
        solver.get("newton_eta_h_scaled_endpoint_bound_has_explicit_constant") is True,
        "manifest missing explicit eta_h-scaled Newton endpoint bound marker",
    )
    checks.check(
        solver.get("newton_eta_h_scaled_endpoint_bound_formula") == "C_N c_eta h^7",
        "manifest eta_h-scaled Newton endpoint bound formula changed",
    )
    checks.check(
        solver.get("local_defect_bound_has_explicit_uniform_constant_sum") is True,
        "manifest missing explicit local-defect constant-sum marker",
    )
    checks.check(
        solver.get("eta_h_constant_absorbed_into_local_defect_constant") is True,
        "manifest missing eta_h absorption into local-defect constant marker",
    )
    checks.check(
        solver.get("local_global_transfer_has_explicit_reduced_grid_constant") is True,
        "manifest missing explicit reduced-grid constant marker",
    )
    checks.check(
        solver.get("local_global_gronwall_factor_formula")
        == "Gamma_s(T) = (exp(C_s T)-1)/C_s with limit T at C_s=0",
        "manifest local-to-global Gronwall factor formula changed",
    )
    checks.check(
        solver.get("local_global_reduced_grid_constant_formula") == "C_red = C_loc Gamma_s(T)",
        "manifest reduced-grid constant formula changed",
    )
    checks.check(
        solver.get("qv_reporting_map_constant_distinct_from_residual_defect_constant") is True,
        "manifest q/v reporting map constant is not distinguished from residual defect constant",
    )
    checks.check(
        solver.get("qv_reporting_constant_formula") == "C_qv = C_{\\mathcal R} C_red",
        "manifest q/v reporting constant formula changed",
    )
    checks.check(
        solver.get("local_global_transfer_grid_point_error_required") is True,
        "manifest missing same-initial-state reported-grid local-to-global transfer marker",
    )
    checks.check(
        solver.get("reported_time_grid_defined_by_tn_equals_nh") is True,
        "manifest missing reported time-grid definition marker",
    )
    checks.check(
        solver.get("exact_final_time_divisibility_required") is False,
        "manifest still requires exact final-time divisibility",
    )
    checks.check(
        solver.get("reported_qv_error_bound_uses_same_reported_time_grid") is True,
        "manifest missing same reported time-grid q/v transfer marker",
    )
    checks.check(
        solver.get("reported_qv_error_bound_is_grid_maximum") is True,
        "manifest missing reported q/v grid-maximum marker",
    )
    checks.check(set(assumptions) == {"P1", "P2", "P3", "P4", "P5", "P6", "P7"}, "assumption ids changed")
    checks.check(
        "same-initial-state reported-grid estimate on the accepted reduced-chart branch" in assumptions.get("P2", {}).get("assumption", "")
        and "reported time grid t_n=n h" in assumptions.get("P2", {}).get("assumption", "")
        and "no exact final-time divisibility requirement" in assumptions.get("P2", {}).get("assumption", "")
        and "reported_time_grid_defined_by_tn_equals_nh=true" in assumptions.get("P2", {}).get("evidence", "")
        and "exact_final_time_divisibility_required=false" in assumptions.get("P2", {}).get("evidence", "")
        and "reported_qv_error_bound_is_grid_maximum=true" in assumptions.get("P2", {}).get("evidence", ""),
        "P2 same-initial-state reported-grid transfer boundary missing",
    )
    checks.check(
        "local_global_reduced_grid_constant_formula=C_red = C_loc Gamma_s(T)"
        in assumptions.get("P2", {}).get("evidence", "")
        and "qv_reporting_constant_formula=C_qv = C_{\\mathcal R} C_red"
        in assumptions.get("P2", {}).get("evidence", ""),
        "P2 explicit global/reporting constant evidence missing",
    )
    checks.check(
        "newton_eta_h_scaled_endpoint_bound_formula=C_N c_eta h^7"
        in assumptions.get("P2", {}).get("evidence", ""),
        "P2 explicit eta_h-scaled Newton endpoint bound evidence missing",
    )
    checks.check(
        assumptions.get("P5", {}).get("status") == "d5_direct_substitution_certificate_closed",
        "P5 direct-substitution assumption status missing",
    )
    checks.check(
        assumptions.get("P4", {}).get("status")
        == "binding_interface_retained_96_row_certificate_proved"
        and assumptions.get("P4", {}).get("retained_interface") is True
        and assumptions.get("P4", {}).get("proved_certificate") is True
        and assumptions.get("P4", {}).get("certificate_rows") == 96
        and assumptions.get("P4", {}).get("excluded_rows") == 36,
        "P4 retained/proved split changed",
    )
    checks.check(
        assumptions.get("P5", {}).get("satisfied_for_submission") is True,
        "P5 should be satisfied by the direct-substitution certificate",
    )
    checks.check(
        all(
            row.get("satisfied_for_submission") is False
            for key, row in assumptions.items()
            if key != "P5"
        ),
        "only P5 should be closed for submission",
    )
    checks.check(
        assumptions.get("P6", {}).get("status") == "finite_probe_recorded_theorem_condition_retained",
        "P6 solver assumption status changed",
    )
    checks.check(
        "branch-selected Newton solves" in assumptions.get("P6", {}).get("assumption", "")
        and "Gauss-predictor branch selection retained" in assumptions.get("P6", {}).get("evidence", ""),
        "P6 solver branch-selection boundary missing",
    )
    checks.check(set(requirements) == {"PC1", "PC2", "PC3", "PC4"}, "close requirement ids changed")
    checks.check(requirements.get("PC1", {}).get("satisfied") is True, "PC1 should be closed")
    checks.check(requirements.get("PC2", {}).get("satisfied") is True, "PC2 residual-value bridge should be satisfied")
    checks.check(
        requirements.get("PC2", {}).get("satisfaction_mode")
        == "D5 same-branch residual-value certificate: 96-row O(h^7) non-dynamic certificate plus 36 dynamic zero rows at Z_G",
        "PC2 satisfaction mode changed",
    )
    checks.check(
        requirements.get("PC3", {}).get("satisfied") is True,
        "PC3 should be satisfied by explicit theorem condition retention",
    )
    checks.check(
        requirements.get("PC3", {}).get("satisfaction_mode")
        == "explicit_theorem_condition_retained_not_empirical_solver_evidence",
        "PC3 satisfaction mode changed",
    )
    checks.check(
        requirements.get("PC3", {}).get("display_status")
        == "traceable only by retained P6 theorem condition; solver-policy theorem not proved",
        "PC3 display status must keep solver-policy theorem open",
    )
    checks.check(
        requirements.get("PC4", {}).get("satisfied") is True,
        "PC4 should retain the transfer-scope exclusion",
    )
    checks.check(
        requirements.get("PC4", {}).get("satisfaction_mode")
        == "nonpromotion_boundary_retained_residual_to_error_theorem_open",
        "PC4 nonpromotion mode changed",
    )
    checks.check(
        requirements.get("PC4", {}).get("display_status")
        == "transfer-scope exclusion retained; residual-to-error theorem not closed",
        "PC4 display status must keep residual-to-error closure open",
    )
    checks.check(
        requirements.get("PC4", {}).get("nonpromotion_boundary_retained") is True,
        "PC4 residual-to-error exclusion marker missing",
    )
    checks.check(
        requirements.get("PC4", {}).get("residual_to_error_closed") is False,
        "PC4 residual-to-error theorem closure overclaimed",
    )
    checks.check(
        requirements.get("PC4", {}).get("residual_to_error_route_promoted") is False,
        "PC4 residual-to-error route promotion overclaimed",
    )
    checks.check(
        sum(1 for row in requirements.values() if not row.get("satisfied")) == 0,
        "unsatisfied close requirement count changed",
    )
    promotion_policy = manifest.get("residual_to_error_promotion_policy", {})
    checks.check(
        promotion_policy.get("residual_promotion_not_made") is True,
        "residual-to-error promotion policy changed",
    )
    checks.check(
        set(promotion_policy.get("coverage_only_examples", [])) == {"four_link", "slider_crank"},
        "coverage-only examples changed in proof closure policy",
    )
    checks.check(
        obligation_ids
        == {"gauss_stage_dynamic_defect_rate"},
        "Newton-Euler obligation ids changed",
    )

    checks.check(proof_contract.get("status") == "open_explicitly_conditional_not_submission_ready", "proof contract status changed")
    checks.check(proof_style.get("proof_boundary", {}).get("proof_gap_closed") is True, "proof style closure marker missing")
    checks.check(dynamic_oracle.get("formula_row_ad_jacobian_oracle", {}).get("probe_count") == 3, "dynamic oracle probe count changed")
    checks.check(kinematic.get("proof_scope", {}).get("certified_row_count") == 96, "kinematic row count changed")
    checks.check(newton_euler.get("closure_state", {}).get("open_obligation_count") == 1, "Newton-Euler closure count changed")
    checks.check(newton_euler.get("closure_state", {}).get("closed_obligation_count") == 5, "Newton-Euler closed count changed")
    checks.check(newton_euler_targets.get("row_count") == 36, "Newton-Euler symbolic target row count changed")
    checks.check(newton_euler_targets.get("translational_row_count") == 18, "Newton-Euler target translational rows changed")
    checks.check(newton_euler_targets.get("rotational_row_count") == 18, "Newton-Euler target rotational rows changed")
    checks.check(
        newton_euler_targets.get("obligation_coverage_matrix", {}).get("coverage_matrix_complete") is True,
        "Newton-Euler symbolic target coverage matrix changed",
    )
    checks.check(
        newton_euler_targets.get("obligation_coverage_matrix", {}).get("row_obligation_link_count") == 180,
        "Newton-Euler symbolic target coverage links changed",
    )
    checks.check(
        oracle.get("newton_euler_runtime_expression_structure_checked") is True,
        "oracle state missing runtime expression structure marker",
    )
    checks.check(
        oracle.get("newton_euler_runtime_template_instantiation_checked") is True,
        "oracle state missing runtime template instantiation marker",
    )
    checks.check(
        oracle.get("newton_euler_template_algebraic_equivalence_checked") is True,
        "oracle state missing template algebraic equivalence marker",
    )
    checks.check(
        oracle.get("newton_euler_c2_template_algebraic_equivalence_closed") is True,
        "oracle state missing template-level C2 subcheck marker",
    )
    checks.check(numerical_scale.get("proof_boundary", {}).get("finite_run_error_scale_supports_order_six") is True, "finite-run scale diagnostic changed")
    checks.check(
        solver_scale.get("proof_boundary", {}).get("finite_scaled_tolerance_probe_recorded") is True,
        "solver-scale finite probe marker changed",
    )
    checks.check(
        solver_scale.get("proof_boundary", {}).get("finite_scaled_tolerance_trajectory_probe_recorded") is True,
        "solver-scale finite trajectory probe marker changed",
    )
    checks.check(
        solver_scale.get("proof_boundary", {}).get("finite_tolerance_regime_sweep_recorded") is True,
        "solver-scale finite tolerance-regime sweep marker changed",
    )
    checks.check(
        solver_scale.get("proof_boundary", {}).get("finite_h_scaled_tolerance_sweep_recorded") is True,
        "solver-scale finite h-scaled tolerance-regime sweep marker changed",
    )
    checks.check(solver_scale.get("proof_boundary", {}).get("eta_h_O_h7_solver_policy_evidence") is False, "solver-scale boundary changed")
    checks.check(
        implementation.get("proof_boundary", {}).get("stage_residual_O_h7_implementation_defect_proved_by_this_static_path_audit") is False,
        "implementation path overclaims O(h^7) proof from static path evidence",
    )
    checks.check(residual_to_error.get("blocking_obligation_count") == 7, "residual-to-error blocker count changed")
    source_files = manifest.get("source_files", {})
    checks.check(
        source_files.get("d5_dynamic_direct_substitution_certificate")
        == "D5_DYNAMIC_DIRECT_SUBSTITUTION_CERTIFICATE.json",
        "D5 dynamic direct-substitution source file link missing",
    )
    checks.check(
        source_files.get("b1_ad_expanded_symbolic_oracle_closure_certificate")
        == "B1_AD_EXPANDED_SYMBOLIC_ORACLE_CLOSURE_CERTIFICATE.json",
        "B1 AD-expanded symbolic oracle closure source file link missing",
    )
    checks.check(
        source_files.get("d5_taylor_term_budget_audit") == "D5_TAYLOR_TERM_BUDGET_AUDIT.json",
        "D5 Taylor term-budget source file link missing",
    )
    checks.check(
        source_files.get("d5_primitive_bound_reduction_audit") == "D5_PRIMITIVE_BOUND_REDUCTION_AUDIT.json",
        "D5 primitive-bound reduction source file link missing",
    )
    checks.check(
        source_files.get("d5_p_tube_constants_audit") == "D5_P_TUBE_CONSTANTS_AUDIT.json",
        "D5 P_tube constants source file link missing",
    )
    checks.check(
        source_files.get("d5_p_state_lift_gap_audit") == "D5_P_STATE_LIFT_GAP_AUDIT.json",
        "D5 P_state lift-gap source file link missing",
    )
    checks.check(
        source_files.get("d5_p_state_map_definition_audit") == "D5_P_STATE_MAP_DEFINITION_AUDIT.json",
        "D5 P_state map-definition source file link missing",
    )
    checks.check(
        source_files.get("d5_p_state_anticircularity_audit") == "D5_P_STATE_ANTICIRCULARITY_AUDIT.json",
        "D5 P_state anti-circularity source file link missing",
    )
    checks.check(
        source_files.get("d5_p_state_ps2_weighted_target_audit") == "D5_P_STATE_PS2_WEIGHTED_TARGET_AUDIT.json",
        "D5 P_state PS2 weighted target source file link missing",
    )
    checks.check(
        source_files.get("d5_p_state_ps2_kinematic_block_certificate")
        == "D5_P_STATE_PS2_KINEMATIC_BLOCK_CERTIFICATE.json",
        "D5 P_state PS2 kinematic-block source file link missing",
    )
    checks.check(
        source_files.get("d5_p_state_ps2_lie_chart_binding_audit")
        == "D5_P_STATE_PS2_LIE_CHART_BINDING_AUDIT.json",
        "D5 P_state PS2 Lie-chart binding source file link missing",
    )
    checks.check(
        source_files.get("d5_p_state_ps2_row_injection_audit")
        == "D5_P_STATE_PS2_ROW_INJECTION_AUDIT.json",
        "D5 P_state PS2 row-injection source file link missing",
    )
    checks.check(
        source_files.get("d5_p_state_ps2_nonlinear_binding_audit")
        == "D5_P_STATE_PS2_NONLINEAR_BINDING_AUDIT.json",
        "D5 P_state PS2 nonlinear binding source file link missing",
    )
    checks.check(
        source_files.get("d5_p_state_ps2_aggregate_promotion_audit")
        == "D5_P_STATE_PS2_AGGREGATE_PROMOTION_AUDIT.json",
        "D5 P_state PS2 aggregate promotion source file link missing",
    )
    checks.check(
        source_files.get("d5_p_state_ps2_linearization_probe")
        == "D5_P_STATE_PS2_LINEARIZATION_PROBE.json",
        "D5 P_state PS2 linearization probe source file link missing",
    )
    checks.check(
        source_files.get("d5_p_state_ps3_conditional_conversion_audit")
        == "D5_P_STATE_PS3_CONDITIONAL_CONVERSION_AUDIT.json",
        "D5 P_state PS3 conditional conversion source file link missing",
    )
    checks.check(
        source_files.get("d5_p_state_ps3_actual_instantiation_gap_audit")
        == "D5_P_STATE_PS3_ACTUAL_INSTANTIATION_GAP_AUDIT.json",
        "D5 P_state PS3 actual-instantiation gap source file link missing",
    )
    checks.check(
        source_files.get("d5_p_state_ps3_h_acc_input_obstruction_audit")
        == "D5_P_STATE_PS3_H_ACC_INPUT_OBSTRUCTION_AUDIT.json",
        "D5 P_state PS3 h-acc obstruction source file link missing",
    )
    checks.check(
        source_files.get("d5_p_acc_map_definition_audit") == "D5_P_ACC_MAP_DEFINITION_AUDIT.json",
        "D5 P_acc map-definition source file link missing",
    )
    checks.check(
        source_files.get("d5_p_acc_row_binding_audit") == "D5_P_ACC_ROW_BINDING_AUDIT.json",
        "D5 P_acc row-binding source file link missing",
    )
    checks.check(
        source_files.get("d5_p_acc_independence_audit") == "D5_P_ACC_INDEPENDENCE_AUDIT.json",
        "D5 P_acc independence source file link missing",
    )
    checks.check(
        source_files.get("d5_p_acc_lift_obstruction_audit") == "D5_P_ACC_LIFT_OBSTRUCTION_AUDIT.json",
        "D5 P_acc lift-obstruction source file link missing",
    )
    checks.check(
        source_files.get("d5_p_acc_pa2_weighted_inverse_audit")
        == "D5_P_ACC_PA2_WEIGHTED_INVERSE_AUDIT.json",
        "D5 P_acc PA2 weighted-inverse source file link missing",
    )
    checks.check(
        source_files.get("d5_p_lambda_interface_audit") == "D5_P_LAMBDA_INTERFACE_AUDIT.json",
        "D5 P_lambda interface source file link missing",
    )
    checks.check(
        source_files.get("d5_p_lambda_d3_noncircularity_audit")
        == "D5_P_LAMBDA_D3_NONCIRCULARITY_AUDIT.json",
        "D5 P_lambda D3 non-circularity source file link missing",
    )
    checks.check(
        source_files.get("d5_p_lambda_pl4_rate_propagation_audit")
        == "D5_P_LAMBDA_PL4_RATE_PROPAGATION_AUDIT.json",
        "D5 P_lambda PL4 rate-propagation source file link missing",
    )
    checks.check(
        source_files.get("d5_p_geom_chart_reduction_audit") == "D5_P_GEOM_CHART_REDUCTION_AUDIT.json",
        "D5 P_geom chart-reduction source file link missing",
    )
    checks.check(
        source_files.get("d5_p_gyro_bilinear_reduction_audit")
        == "D5_P_GYRO_BILINEAR_REDUCTION_AUDIT.json",
        "D5 P_gyro bilinear-reduction source file link missing",
    )
    checks.check(
        source_files.get("d5_primitive_obligation_closure_plan") == "D5_PRIMITIVE_OBLIGATION_CLOSURE_PLAN.json",
        "D5 primitive-obligation closure-plan source file link missing",
    )
    checks.check(
        source_files.get("d5_conditional_taylor_certificate") == "D5_CONDITIONAL_TAYLOR_CERTIFICATE.json",
        "D5 conditional Taylor certificate source file link missing",
    )
    checks.check(
        source_files.get("d5_open_primitive_gap_audit") == "D5_OPEN_PRIMITIVE_GAP_AUDIT.json",
        "D5 open primitive gap source file link missing",
    )

    for token in [
        "Status: **Direct PC2 residual-value bridge closed under retained theorem interfaces; global claim-promotion/package gates still open**.",
        "Accepted method/order: `Gauss6/FullVA` / `6`.",
        "Runtime rows: `132`.",
        "Certified non-dynamic rows: `96`.",
        "Active direct Newton-Euler closed/open rows: `36/0`.",
        "Active direct Newton-Euler open obligations: `0`.",
        "Symbolic/primitive-route Newton-Euler rows not certified by that route: `36`.",
        "Symbolic/primitive-route Newton-Euler open obligations: `1`.",
        "Symbolic/primitive open-row scope: `symbolic_primitive_certificate_route_not_active_direct_pc2`.",
        "Newton-Euler closed obligations: `5`.",
        "Newton-Euler closed obligation ids: `['translational_balance_identity', 'rotational_balance_identity', 'multiplier_wrench_consistency', 'smooth_force_lift_consistency', 'symbolic_runtime_row_equivalence']`.",
        "Newton-Euler symbolic target rows translational/rotational: `36` / `18/18`.",
        "Newton-Euler obligation coverage matrix complete: `True`.",
        "Newton-Euler row-obligation links: `180`.",
        "Newton-Euler rows with complete obligation sets: `36`.",
        "Newton-Euler runtime expression structure checked/rows: `True` / `36`.",
        "Newton-Euler runtime template instantiation checked/rows: `True` / `36`.",
        "Newton-Euler template algebraic equivalence checked/rows: `True` / `36`.",
        "Newton-Euler template algebraic translational/rotational rows: `18/18`.",
        "Newton-Euler template-level C2 subcheck closed: `True`.",
        "Newton-Euler balance identity closed/rows: `True` / `36`.",
        "Newton-Euler translational/rotational balance identity closed rows: `18/18`.",
        "Newton-Euler virtual-work sign-skeleton checked/rows: `True` / `36`.",
        "Newton-Euler virtual-work template identity proved/rows: `True` / `36`.",
        "Newton-Euler row-expanded virtual-work identity proved/rows: `True` / `36`.",
        "Newton-Euler multiplier-wrench consistency closed: `True`.",
        "Newton-Euler closure-contract rows/traceability/direct-route row-defect closed: `36` / `36` / `36`.",
        "Newton-Euler closure-contract open PCs: ``.",
        "Newton-Euler D5 blueprint rows/open lifted-stage terms/power-seven rows: `36` / `0` / `36`.",
        "Newton-Euler D5 finite-probe/residual-promotion accepted rows: `0` / `0`.",
        "Newton-Euler D5 direct-substitution blueprint nonclosure flag: `False`.",
        "Newton-Euler D5 readiness rows/runtime-ready/open-lifted/direct-route certified: `36` / `36` / `0` / `36`.",
        "Newton-Euler D5 readiness PC2 closed: `True`.",
        "Newton-Euler D5 same-branch dynamic zero-block certificate satisfied/non-circular/O(h^7): `True` / `True` / `True`.",
        "Newton-Euler D5 same-branch dynamic-zero/full-stage rows: `36` / `132`.",
        "Newton-Euler D5 same-branch dynamic zero-block forbidden shortcuts/direct-route PC2 active: `0` / `True`; residual-to-error/source-policy promotion: `False` / `False`.",
        "Separate primitive/Taylor route does not discharge the PC2 stage-residual condition: `True`; induced primitive-route Taylor bounds certified/open obligations: `0/162` / `5`.",
        "Newton-Euler D5 Taylor term budget rows/terms/open/certified: `36` / `162` / `162` / `0`.",
        "Newton-Euler D5 Taylor term budget PC2 closed: `False`.",
        "Newton-Euler D5 primitive reduction terms/rules/obligations/proved: `162` / `162` / `6` / `1`.",
        "Newton-Euler D5 primitive reduction term bounds proved: `0`.",
        "Newton-Euler D5 primitive reduction PC2 closed: `False`.",
        "Newton-Euler D5 smooth force/torque/friction corollary label/conditional rows/main-flat: `cor:d5-smooth-force-row-bound-under-lifts` / `72` / `True`.",
        "Newton-Euler D5 smooth force/torque/friction inputs/actual bounds/primitive/PC2/D4-as-rate: `['P_state_lift', 'P_multiplier_lift']` / `0` / `False` / `False` / `False`.",
        "Newton-Euler D5 P_tube compact constants closed/term rows/remaining primitives: `True` / `162` / `5`.",
        "Newton-Euler D5 P_tube induced bounds/PC2 closed: `0` / `False`.",
        "Newton-Euler D5 P_state gap recorded/closed/term rows: `True` / `False` / `126`.",
        "Newton-Euler D5 P_state map definition recorded/closed/rows/subproofs: `True` / `True` / `96` / `1` / `4`.",
        "Newton-Euler D5 P_state anti-circularity recorded/closed/subproofs-after/open-after/PC2: `True` / `True` / `2` / `2` / `False`.",
        "Newton-Euler D5 P_state PS2 weighted target recorded/spec/infsup/state-acc-row/PC2: `True` / `True` / `False` / `72`-`36`-`96` / `False`.",
        "Newton-Euler D5 P_state PS2 kinematic block recorded/subblock/full-PS2/rows-surplus/norm/gaps/PC2: `True` / `True` / `False` / `72`-`24` / `1.20027766085596` / `3` / `False`.",
        "Newton-Euler D5 P_state PS2 Lie-chart binding recorded/SO3/full-mean/full-PS2/factor/gaps/PC2: `True` / `True` / `False` / `False`",
        "Newton-Euler D5 P_state PS2 row injection recorded/72-to-96/scaling/norm/full-mean/full-PS2/gaps/PC2: `True` / `True` / `True` / `1.0` / `False` / `False` / `1` / `False`.",
        "Newton-Euler D5 P_state PS2 nonlinear binding recorded/rot-mean/full-mean/full-PS2/gaps/PC2: `True` / `True` / `True` / `False` / `1` / `False`.",
        "Newton-Euler D5 P_state PS2 aggregate promotion recorded/inverse/uniform/PS2/PS3/P_state/PC2: `True` / `True` / `True` / `True` / `False` / `False` / `False`.",
        "Newton-Euler D5 P_state PS2 finite linearization probe recorded/full-rank/rank-range/min-singular/state-projection/uniform/PC2: `True` / `True` / `[108, 108]`",
        "Newton-Euler D5 P_state PS3 conditional conversion recorded/conditional/actual/PS2/input/rates/PC2: `True` / `True` / `False` / `True`-`True` / `False` / `O(h^7)`-`O(h^7)` / `False`.",
        "Newton-Euler D5 P_state PS3 actual-instantiation gap recorded/inputs/h-input/table/P_state/PC2: `True` / `2`-`4` / `False` / `False` / `False` / `False`.",
        "Newton-Euler D5 P_state PS3 h-acc input obstruction recorded/nullity/residual-only/input/PS3/PC2: `True` / `12`-`12` / `False` / `False` / `False` / `False`.",
        "Newton-Euler D5 P_state future subproofs closed/total and induced bounds/PC2: `3` / `4` / `0` / `False`.",
        "Newton-Euler D5 P_acc map definition recorded/closed/rows/subproofs: `True` / `True` / `36` / `1` / `4`.",
        "Newton-Euler D5 P_acc row binding recorded/closed/rows/subproofs-after: `True` / `True` / `36` / `2` / `4`.",
        "Newton-Euler D5 P_acc independence recorded/closed/input-families/subproofs-after: `True` / `True` / `3` / `3` / `3` / `4`.",
        "Newton-Euler D5 P_acc PA2 obstruction recorded/closed/current-rate: `True` / `False` / `O(h^6)`.",
        "Newton-Euler D5 P_acc velocity-collocation-alone sufficient/lift-rate-proved/term-bounds/PC2: `False` / `False` / `0` / `False`.",
        "Newton-Euler D5 P_acc PA2 weighted-inverse recorded/h-control/probes/full-rank: `True` / `True` / `3` / `True`.",
        "Newton-Euler D5 P_acc PA2 projection constants unweighted/weighted-h and unweighted-control/PA2/PC2: `100.00000000000063` / `1.0000000000000056` / `False` / `False` / `False`.",
        "Newton-Euler D5 P_lambda interface/PL2/D3/PL4 recorded/closed/lambda-vars/direct-rows/term-rows/conditional-subproofs-after/open-after: `True`-`True`-`True`-`True` / `True`-`True`-`True`-`True` / `24` / `36` / `72` / `4` / `4` / `0`.",
        "Newton-Euler D5 P_lambda PL2 symbolic margin/probe-stage-rows/finite-probe-as-proof/primitive/PC2: `True` / `9` / `False` / `False` / `False`.",
        "Newton-Euler D5 P_lambda conditional PL subproofs complete/actual multiplier lift open/scope: `True` / `True` / PL1/PL2/PL3/PL4 subproof count is complete only for the conditional propagation mechanism; the actual multiplier lift still depends on open P_state and P_acc inputs and certifies no primitive Taylor subterm.",
        "Newton-Euler D5 P_lambda PL4 conditional/actual multiplier rate and open inputs: `True` / `False` / `2`.",
        "Newton-Euler D5 P_lambda primitive/PC2 closed: `False` / `False`.",
        "Newton-Euler D5 P_geom reduction recorded/chart-closed/actual primitive open/scope: `True` / `True` / `True` / chart reduction closed means only the downstream conditional Lipschitz map under open P_state and P_lambda inputs; the actual P_geom primitive and PC2 remain open and certify no primitive Taylor subterm without those lifts.",
        "Newton-Euler D5 P_geom subproofs closed/total, open inputs, conditional rows, primitive, PC2: `3` / `4` / `2` / `36` / `False` / `False`.",
        "Newton-Euler D5 P_geom translational/rotational reduced rows: `18` / `18`.",
        "Newton-Euler D5 P_gyro reduction recorded/algebraic-closed/internal complete not primitive/actual primitive open/scope: `True` / `True` / `True` / `True` / algebraic reduction closed means only the internal bilinear gyroscopic reduction under the open P_state angular-velocity input; the actual P_gyro primitive and PC2 remain open and certify no primitive Taylor subterm without that lift.",
        "Newton-Euler D5 P_gyro subproofs closed/total, open inputs, conditional rows, primitive, PC2: `3` / `3` / `1` / `18` / `False` / `False`.",
        "Newton-Euler D5 primitive closure-plan obligations/interfaces/proved/open: `6` / `6` / `1` / `5`.",
        "Newton-Euler D5 primitive closure-plan induced bounds proved: `0`.",
        "Newton-Euler D5 primitive closure-plan PC2 closed: `False`.",
        "Newton-Euler D5 conditional Taylor certificate rows/terms: `36` / `162`.",
        "Newton-Euler D5 conditional Taylor certificate conditional rows/terms: `36` / `162`.",
        "Newton-Euler D5 conditional Taylor certificate actual terms proved/open primitive assumptions/PC2: `0` / `5` / `False`.",
        "Newton-Euler D5 open primitive gap recorded/count: `True` / `5`.",
        "Newton-Euler D5 open primitive future subproofs closed/total and induced bounds/PC2: `16` / `19` / `0` / `False`.",
        "Residual-to-error blocking obligations: `7`.",
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
        "Direct PC2 residual-value bridge closed under retained theorem interfaces: `True`.",
        "Direct PC2 residual-bridge scope: `direct_residual_bridge_kantorovich_route_closed_primitive_taylor_conditional_schema_open`.",
        "Dynamic symbolic oracle complete: `False`.",
        "Stage residual O(h^7) defect proved: `True`.",
        "Active direct residual-bridge proof standard: `direct_residual_bridge_kantorovich_route`.",
        "Direct residual-bridge proof contract satisfied: `True`.",
        "Not primitive 162-term Taylor closure: `True`.",
        "Theorem residual-certificate consumption rule: one certificate `True`; future primitive/Taylor replacement-only `True`; same-tuple 132-row bound required `True`; no append/lower/remove/promote `True`.",
        "Primitive/Taylor actual/open terms: `0` / `162`.",
        "Primitive/Taylor subterms blocked by open primitive assumptions: `162`.",
        "Same-branch dynamic zero-block supplies active PC2 residual-bridge proof input: `True`.",
        "eta_h^tube <= c_eta h^7 solver-policy theorem: `False`.",
        "eta_h theorem condition retained: `True`.",
        "Theorem label present main/flat: `True/True`.",
        "Manuscript proof labels all present main/flat: `True/True`.",
        "Manuscript anchor map present: `True`; label anchors `24`; theorem-interface/P7-output-boundary anchors `7`.",
        "Theorem-interface/P7-output-boundary manuscript anchor IDs: `P1,P2,P3,P4,P5,P6,P7`.",
        "Reader-facing theorem-interface split: theorem interfaces `P1--P6`; P7 is an output nonclaim/residual-to-error boundary anchor, not a theorem premise.",
        "Legacy P7-output-boundary anchor count includes P7 only for traceability across residual tables; it does not promote P7 into the theorem-interface list.",
        "Theorem-assumption anchor table table reference coverage: `True`.",
        "Auxiliary-evidence scope main/flat coverage: `True`.",
        "Constant-dependency rule main/flat coverage: `True`.",
        "Theorem input-output flow main/flat coverage: `True`.",
        "Theorem output scope rule main/flat coverage: `True`.",
        "Quantifier/domain rule main/flat coverage: `True`.",
        "Local-to-global transfer rule main/flat coverage: `True`.",
        "Reporting-map/norm-equivalence rule main/flat coverage: `True`.",
        "Proof-causality rule main/flat coverage: `True`.",
        "Accepted-branch consistency rule main/flat coverage: `True`.",
        "Local-defect decomposition rule main/flat coverage: `True`.",
        "Direct-route anti-circularity rule main/flat coverage: `True`.",
        "Implementation-route/certificate separation main/flat coverage: `True`.",
        "B1 AD-expanded closure table interpretation main/flat coverage: `True`.",
        "P1/P2 compact-tube boundary main/flat coverage: `True`.",
        "P3/P4 implementation-defect boundary main/flat coverage: `True`.",
        "P5 direct-route boundary main/flat coverage: `True`.",
        "P6 solver-scope boundary main/flat coverage: `True`.",
        "Nonlinear-solver scale rule main/flat coverage: `True`.",
        "Assumptions and theorem scope interpretation main/flat coverage: `True`.",
        "Residual-to-error boundary main/flat coverage: `True`.",
        "Conditional theorem branch/eta/grid/fixed-tolerance boundary: `True/True/True/True`.",
        "Theorem reading guide main/flat coverage: `True`.",
        "Proof dependency graph/table/residual non-promotion: `True/True/True`.",
        "Conditional proof claims mapped to manuscript: `True`.",
        "## Manuscript Theorem Traceability",
        "## Theorem Assumption Manuscript Anchors",
        "P6/OC6 disambiguation: theorem `P6` is the retained compact-tube solver-scale interface; objective blocker `OC6` is the separate source-policy TFE DAE-runner/package gap and is not closed by this proof manifest.",
        "This traceability check documents the conditional proof writing boundary only; it does not close solver-policy theorem, residual-to-error promotion, source-policy rows, or full-TFE replacement.",
        "Four-link/slider residual-to-error promotion made: `False`.",
        "Proof-route checks traceable/blocked under conditional scope: `4/0`.",
        "Here `submission_ready=false` is scoped to proof-closure/global proof-package readiness,",
        "not to the separate narrowed-claim package decision.",
        "Submission-ready scope: `proof_closure_global_boundary_not_narrowed_claim_package_decision`.",
        "Narrowed-claim B4/B6/B7 subcheck statuses (narrowed-only; not source-policy row closure): `closed/closed/closed`.",
        "Remaining global submission boundaries: `full_source_policy_package_ready,theorem_level_eta_h_solver_policy_evidence,closed_residual_to_error_theorem_for_mechanism_rows`.",
        "Narrowed-claim B4/B6/B7 subcheck closed elsewhere while source-policy rows remain open: `True`.",
        "Direct PC2 residual-value bridge closed under retained theorem interfaces: `True`.",
        "Remaining-gate eta_h theorem condition retained: `True`.",
        "Remaining-gate residual-to-error blocking obligations: `7`.",
        "Remaining-gate residual-to-error route promoted: `False`.",
        "Remaining-gate active direct Newton-Euler open obligations: `0`.",
        "Remaining-gate symbolic/primitive-route open obligations: `1`.",
        "Submission ready: `False`.",
        "`P5`",
        "`PC1` | independent symbolic row-by-row oracle for expanded FullVA rows | `traceable: balance-identity route closed`",
        "`PC2` | O(h^7) implementation residual-defect certificate | `traceable: direct D5 residual-value bridge satisfied`",
        "`PC3` | explicit eta_h^tube <= c_eta h^7 solver-policy theorem or theorem condition retained | `traceable only by retained P6 theorem condition; solver-policy theorem not proved`",
        "`PC4` | residual-to-error obligations closed before four-link/slider-crank residual promotion | `transfer-scope exclusion retained; residual-to-error theorem not closed`",
        "Forbidden now: unconditional non-assumption theorem closure, dynamic symbolic oracle completion, residual-to-error promotion, full TFE stage replacement, and unscoped/global proof-package submission-ready claims.",
    ]:
        checks.check(token in manifest_md, f"markdown missing token: {token}")
    for assumption_id in ["P1", "P2", "P3", "P4", "P5", "P6", "P7"]:
        checks.check(
            f"| `{assumption_id}` |" in manifest_md,
            f"markdown missing theorem-assumption anchor row {assumption_id}",
        )

    if checks.errors:
        print("proof closure manifest validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("proof closure manifest validation: PASS")
    print("direct_pc2_proof_gap_closed=True")
    print("certified_non_dynamic_rows=96")
    print("direct_dynamic_zero_rows=36")
    print("close_requirements_satisfied=4/4")
    print("unsatisfied_close_requirements=0")
    print("residual_to_error_blocking_obligations=7")
    print("remaining_gate_direct_pc2_proof_gap_closed=True")
    print("remaining_gate_eta_h_theorem_condition_retained=True")
    return 0


if __name__ == "__main__":
    sys.exit(main())
