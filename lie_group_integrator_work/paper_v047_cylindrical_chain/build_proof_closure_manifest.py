#!/usr/bin/env python3
"""Build the proof-closure manifest for the CMAME package.

This manifest is a hard boundary between the current conditional order theorem
and unscoped/global proof-package submission-ready claims.  It aggregates the
existing proof gates without
running numerical experiments.
"""

from __future__ import annotations

import json
import re
from pathlib import Path


PAPER = Path(__file__).resolve().parent
from paper_paths import LATEX, package_path as manuscript_path
ROOT = PAPER.parent
V048 = ROOT / "v048_cross_paper_same_test_benchmarks" / "results"
MAIN_TEX = LATEX / "main_cmame.tex"
FLAT_TEX = LATEX / "cmame_submission_flat" / "main_cmame_submission.tex"
OUT_JSON = PAPER / "PROOF_CLOSURE_MANIFEST.json"
OUT_MD = PAPER / "PROOF_CLOSURE_MANIFEST.md"

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


def blocker_statuses(gate: dict, blocker_ids: list[str]) -> dict[str, str | None]:
    rows = {item.get("id"): item for item in gate.get("blockers", [])}
    return {blocker_id: rows.get(blocker_id, {}).get("status") for blocker_id in blocker_ids}


def main() -> None:
    proof_contract = read_json(PAPER / "CMAME_PROOF_CONTRACT_GATE.json")
    proof_style = read_json(PAPER / "CMAME_PROOF_STYLE_AUDIT.json")
    blocker_gate = read_json(PAPER / "CMAME_BLOCKER_CLOSURE_GATE.json")
    dynamic_oracle = read_json(PAPER / "DYNAMIC_ROW_ORACLE_GATE.json")
    kinematic = read_json(PAPER / "KINEMATIC_ROW_DEFECT_CERTIFICATE.json")
    newton_euler = read_json(PAPER / "NEWTON_EULER_DEFECT_OBLIGATION_GATE.json")
    newton_euler_targets = read_json(PAPER / "NEWTON_EULER_SYMBOLIC_TARGET_AUDIT.json")
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
    newton_euler_balance_identity = read_json(PAPER / "NEWTON_EULER_BALANCE_IDENTITY_AUDIT.json")
    numerical_scale = read_json(PAPER / "PROOF_NUMERICAL_SCALE_AUDIT.json")
    solver_scale = read_json(PAPER / "PROOF_SOLVER_SCALE_AUDIT.json")
    implementation = read_json(PAPER / "IMPLEMENTATION_PATH_AUDIT.json")
    order_gate = read_json(PAPER / "ORDER_ACCEPTANCE_GATE.json")
    residual_to_error = read_json(V048 / "closed_loop_residual_to_error_theorem_obligations.json")
    main_tex = read_text(MAIN_TEX)
    flat_tex = read_text(FLAT_TEX)

    theorem_contract = proof_contract.get("theorem_contract", {})
    proof_boundary = proof_style.get("proof_boundary", {})
    kinematic_scope = kinematic.get("proof_scope", {})
    newton_scope = newton_euler.get("proof_scope", {})
    newton_closure = newton_euler.get("closure_state", {})
    newton_target_coverage = newton_euler_targets.get("obligation_coverage_matrix", {})
    newton_certificate_summary = newton_euler_certificate.get("summary", {})
    newton_closure_contract_summary = newton_euler_closure_contract.get("summary", {})
    d5_readiness_summary = d5_readiness.get("summary", {})
    d5_direct_summary = d5_direct_substitution.get("summary", {})
    d5_term_budget_summary = d5_term_budget.get("summary", {})
    d5_primitive_reduction_summary = d5_primitive_reduction.get("summary", {})
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
    formula_jacobian = dynamic_oracle.get("formula_row_ad_jacobian_oracle", {})
    numerical_orders = numerical_scale.get("smooth_projected_velocity_global_orders", {})
    endpoint_orders = numerical_scale.get("endpoint_global_closure_orders", {})
    solver_boundary = solver_scale.get("proof_boundary", {})
    implementation_boundary = implementation.get("proof_boundary", {})
    finite_solver_probe = solver_scale.get("finite_scaled_tolerance_probe", {})
    finite_solver_trajectory_probe = solver_scale.get("finite_scaled_tolerance_trajectory_probe", {})
    finite_tolerance_regime_sweep = solver_scale.get("finite_tolerance_regime_sweep", {})
    solver_condition_retained = (
        theorem_contract.get("newton_tolerance_policy") == "eta_h^tube <= c_eta h^7 for asymptotic proof"
        and theorem_contract.get("per_step_newton_tolerance_policy")
        == (
            "eta_h^tube <= c_eta h^7 on the compact proof tube; reported-grid eta_h^reported = "
            "max_{0<=n<N} eta_{h,n} is only its accepted branch-selected trajectory specialization"
        )
        and theorem_contract.get("same_reduced_chart_initial_state_required") is True
        and theorem_contract.get("branch_selected_newton_solves_required") is True
        and theorem_contract.get("newton_iterates_initialized_from_gauss_predictor_required") is True
        and theorem_contract.get("arbitrary_newton_initializations_select_branch") is False
        and theorem_contract.get("remote_nonlinear_roots_select_branch") is False
        and theorem_contract.get("gauss_truncation_bound_has_explicit_uniform_constant") is True
        and theorem_contract.get("gauss_truncation_constant_uniform_on_compact_trajectory_tube") is True
        and theorem_contract.get("stage_residual_to_root_bound_has_explicit_constant") is True
        and theorem_contract.get("stage_residual_to_root_constant_formula") == "C_Z = 2 M C_R"
        and theorem_contract.get("stage_root_endpoint_perturbation_constant_formula") == "C_A = M_E C_Z"
        and theorem_contract.get("accepted_root_existence_proved_by_stage_residual_lemma") is True
        and theorem_contract.get("accepted_root_existence_not_assumed_as_isolated_root_premise") is True
        and theorem_contract.get("endpoint_closure_raw_defect_bound_has_explicit_constant") is True
        and theorem_contract.get("endpoint_closure_raw_defect_constant_symbol") == "C_{E,raw}"
        and theorem_contract.get("endpoint_closure_perturbation_bound_has_explicit_constant") is True
        and theorem_contract.get("endpoint_closure_perturbation_constant_formula")
        == "C_E = 4 M_E^ri C_{E,raw}"
        and theorem_contract.get("local_defect_constants_uniform_on_compact_proof_tube") is True
        and theorem_contract.get("local_defect_constants_uniform_over_accepted_steps") is True
        and theorem_contract.get("newton_error_controlled_by_compact_tube_eta_h_envelope") is True
        and theorem_contract.get("newton_error_controlled_by_single_accepted_branch_eta_h_max") is True
        and theorem_contract.get("newton_residual_to_stage_bound_has_explicit_constant") is True
        and theorem_contract.get("newton_endpoint_output_map") == "P_h = C_h o E_h"
        and theorem_contract.get("newton_endpoint_output_map_bound")
        == "||P_h(Ztilde_A)-P_h(Z_A)|| <= C_N eta_h"
        and theorem_contract.get("newton_endpoint_output_map_derivative_bound_includes_closure") is True
        and theorem_contract.get("newton_endpoint_output_map_lipschitz_constant_symbol") == "M_N"
        and theorem_contract.get("newton_residual_to_endpoint_perturbation_constant_formula")
        == "C_N = 2 M_A M_N"
        and theorem_contract.get("newton_eta_h_scaled_endpoint_bound_has_explicit_constant") is True
        and theorem_contract.get("newton_eta_h_scaled_endpoint_bound_formula") == "C_N c_eta h^7"
        and theorem_contract.get("local_defect_bound_has_explicit_uniform_constant_sum") is True
        and theorem_contract.get("eta_h_constant_absorbed_into_local_defect_constant") is True
        and theorem_contract.get("local_global_transfer_has_explicit_reduced_grid_constant") is True
        and theorem_contract.get("local_global_gronwall_factor_formula")
        == "Gamma_s(T) = (exp(C_s T)-1)/C_s with limit T at C_s=0"
        and theorem_contract.get("local_global_reduced_grid_constant_formula") == "C_red = C_loc Gamma_s(T)"
        and theorem_contract.get("qv_reporting_map_constant_distinct_from_residual_defect_constant") is True
        and theorem_contract.get("qv_reporting_constant_formula") == "C_qv = C_{\\mathcal R} C_red"
        and theorem_contract.get("local_global_transfer_grid_point_error_required") is True
        and theorem_contract.get("reported_time_grid_defined_by_tn_equals_nh") is True
        and theorem_contract.get("exact_final_time_divisibility_required") is False
        and theorem_contract.get("reported_qv_error_bound_uses_same_reported_time_grid") is True
        and theorem_contract.get("reported_qv_error_bound_is_grid_maximum") is True
        and solver_boundary.get("eta_h_O_h7_solver_policy_evidence") is False
    )
    residual_promotion_not_made = (
        residual_to_error.get("accepted_residual_to_error_theorem") is False
        and set(order_gate.get("coverage_only_examples", [])) == {"four_link", "slider_crank"}
        and not {"four_link", "slider_crank"}.intersection(order_gate.get("accepted_dynamic_order_examples", []))
    )
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
    source_manuscript_anchor_map = manuscript_anchor_map(main_tex, flat_tex)
    source_theorem_anchor_table_coverage = theorem_anchor_table_reference_coverage(
        main_tex, flat_tex
    )
    manuscript_labels_present = all(main_label_presence.values()) and all(flat_label_presence.values())
    theorem_boundary_present = all(main_theorem_boundary.values()) and all(flat_theorem_boundary.values())
    theorem_reading_guide_present = all(main_theorem_reading_guide.values()) and all(
        flat_theorem_reading_guide.values()
    )
    proof_traceability_present = all(main_proof_traceability.values()) and all(flat_proof_traceability.values())
    theorem_use_rule_present = all(main_theorem_use_rule.values()) and all(
        flat_theorem_use_rule.values()
    )
    constant_dependency_table_present = all(main_constant_dependency_table.values()) and all(
        flat_constant_dependency_table.values()
    )
    theorem_dependency_consumption_table_present = all(
        main_theorem_dependency_consumption_table.values()
    ) and all(flat_theorem_dependency_consumption_table.values())
    theorem_output_scope_table_present = all(main_theorem_output_scope_table.values()) and all(
        flat_theorem_output_scope_table.values()
    )
    quantifier_domain_table_present = all(main_quantifier_domain_table.values()) and all(
        flat_quantifier_domain_table.values()
    )
    local_global_transfer_table_present = all(main_local_global_transfer_table.values()) and all(
        flat_local_global_transfer_table.values()
    )
    reporting_map_table_present = all(main_reporting_map_table.values()) and all(
        flat_reporting_map_table.values()
    )
    proof_causality_table_present = all(main_proof_causality_table.values()) and all(
        flat_proof_causality_table.values()
    )
    branch_consistency_table_present = all(main_branch_consistency_table.values()) and all(
        flat_branch_consistency_table.values()
    )
    local_defect_decomposition_table_present = all(
        main_local_defect_decomposition_table.values()
    ) and all(flat_local_defect_decomposition_table.values())
    direct_route_anticircularity_table_present = all(
        main_direct_route_anticircularity_table.values()
    ) and all(flat_direct_route_anticircularity_table.values())
    implementation_route_oracle_table_present = all(
        main_implementation_route_oracle_table.values()
    ) and all(flat_implementation_route_oracle_table.values())
    b1_ad_expanded_closure_table_present = all(
        main_b1_ad_expanded_closure_table.values()
    ) and all(flat_b1_ad_expanded_closure_table.values())
    p1p2_compact_tube_boundary_present = all(
        main_p1p2_compact_tube_boundary.values()
    ) and all(flat_p1p2_compact_tube_boundary.values())
    p3p4_implementation_boundary_present = all(
        main_p3p4_implementation_boundary.values()
    ) and all(flat_p3p4_implementation_boundary.values())
    p5_direct_route_boundary_present = all(
        main_p5_direct_route_boundary.values()
    ) and all(flat_p5_direct_route_boundary.values())
    p6_solver_scope_boundary_present = all(
        main_p6_solver_scope_boundary.values()
    ) and all(flat_p6_solver_scope_boundary.values())
    nonlinear_solver_scale_table_present = all(
        main_nonlinear_solver_scale_table.values()
    ) and all(flat_nonlinear_solver_scale_table.values())
    p_interface_satisfaction_table_present = all(
        main_p_interface_satisfaction_table.values()
    ) and all(flat_p_interface_satisfaction_table.values())
    p7_residual_to_error_obligation_table_present = all(
        main_p7_residual_to_error_obligation_table.values()
    ) and all(flat_p7_residual_to_error_obligation_table.values())
    pc2_direct_route_satisfied = (
        d5_direct_substitution.get("direct_route_mathematical_certificate_closed") is True
        and d5_direct_substitution.get("direct_route_non_circular") is True
        and d5_direct_substitution.get("stage_residual_O_h7_by_direct_route") is True
        and d5_direct_summary.get("dynamic_zero_residual_rows") == 36
        and d5_direct_summary.get("certified_non_dynamic_rows") == 96
        and d5_direct_summary.get("full_stage_rows_if_promoted") == 132
        and d5_direct_summary.get("forbidden_shortcuts_used") == 0
    )

    theorem_assumptions = [
        {
            "id": "P1",
            "assumption": "regular smooth FullVA lift exists on the proof tube",
            "status": "theorem_condition_retained",
            "satisfied_for_submission": False,
            "evidence": "regular_smooth_fullva_lift_required=true",
        },
        {
            "id": "P2",
            "assumption": "stage Jacobian is uniformly invertible on the compact-tube Gauss-predictor branch, endpoint closure has a closed anchor, local ball margin, and local right inverse, the accepted one-step map has 1+C_s h stability with tube-retention bootstrap, the local-to-global transfer is a same-initial-state reported-grid estimate on the accepted reduced-chart branch with reported time grid t_n=n h and no exact final-time divisibility requirement, the reported q/v bound uses the same reported time grid as a grid maximum, and the inexact Newton residual estimate has a strong local residual inverse",
            "status": "theorem_condition_retained",
            "satisfied_for_submission": False,
            "evidence": "stage_jacobian_uniformly_invertible_required=true; stage_jacobian_uniform_inverse_required_on_gauss_predictor_branch=true; finite_rank_probes_sufficient_for_stage_inverse=false; accepted_endpoint_closure_closed_anchor_required=true; accepted_endpoint_closure_local_ball_margin_required=true; accepted_endpoint_closure_local_right_inverse_required=true; endpoint_closure_perturbation_constant_formula=C_E = 4 M_E^ri C_{E,raw}; accepted_one_step_stability_required=true; accepted_tube_retention_bootstrap_required=true; local_global_reduced_grid_constant_formula=C_red = C_loc Gamma_s(T); qv_reporting_constant_formula=C_qv = C_{\\mathcal R} C_red; local_global_transfer_grid_point_error_required=true; reported_time_grid_defined_by_tn_equals_nh=true; exact_final_time_divisibility_required=false; reported_qv_error_bound_uses_same_reported_time_grid=true; reported_qv_error_bound_is_grid_maximum=true; accepted_newton_residual_strong_local_inverse_required=true; newton_eta_h_scaled_endpoint_bound_formula=C_N c_eta h^7",
        },
        {
            "id": "P3",
            "assumption": "implemented 132-row residual matches the audited row formulas",
            "status": "runtime_formula_and_ad_oracle_checked_symbolic_oracle_open",
            "satisfied_for_submission": False,
            "evidence": "132 formula rows checked and 3 AD Jacobian probes matched R_JAC",
        },
        {
            "id": "P4",
            "assumption": "non-dynamic rows have O(h^7) stage defect on the smooth lift",
            "status": "binding_interface_retained_96_row_certificate_proved",
            "satisfied_for_submission": False,
            "retained_interface": True,
            "proved_certificate": True,
            "certificate_rows": 96,
            "excluded_rows": 36,
            "evidence": "96 kinematic/lower-pair rows certified; 36 Newton-Euler rows excluded",
        },
        {
            "id": "P5",
            "assumption": "Newton-Euler rows have O(h^7) implementation defect",
            "status": "d5_direct_substitution_certificate_closed",
            "satisfied_for_submission": pc2_direct_route_satisfied,
            "evidence": "D5_DYNAMIC_DIRECT_SUBSTITUTION_CERTIFICATE proves 36 dynamic rows have zero residual on Z_G using closed D1/D2/D3/D4/D6 inputs and no circular P_state/P_acc/P_lambda route",
        },
        {
            "id": "P6",
            "assumption": "inexact Newton residuals obey eta_h^tube <= c_eta h^7 on the compact proof tube under the strong local residual inverse bound; the reported-grid eta_h^reported=max_n eta_{h,n} over accepted branch-selected Newton solves is only the accepted trajectory specialization",
            "status": "finite_probe_recorded_theorem_condition_retained",
            "satisfied_for_submission": False,
            "evidence": "accepted_newton_residual_strong_local_inverse_required=true; same reduced-chart initial state and Gauss-predictor branch selection retained; arbitrary Newton initializations and remote nonlinear roots excluded; summary residuals recorded; finite one-step scaled-tolerance probe has 4/4 rows ok; finite short-trajectory scaled-tolerance probe has 4/4 rows and 30 steps ok; uniform all-transition scaled solver-policy theorem still open and not needed to state the conditional theorem; closure would be needed only to promote P6 from retained hypothesis to discharged solver theorem",
        },
        {
            "id": "P7",
            "assumption": "closed-loop residual rates imply trajectory error rates",
            "status": "open_residual_to_error_transfer",
            "satisfied_for_submission": False,
            "evidence": "7 residual-to-error obligations remain blocking",
        },
    ]

    close_requirements = [
        {
            "id": "PC1",
            "requirement": "independent symbolic row-by-row oracle for expanded FullVA rows",
            "satisfied": True,
            "traceable_under_conditional_scope": True,
            "display_status": "traceable: balance-identity route closed",
            "satisfaction_mode": "D1/D2 balance identities closed by NEWTON_EULER_BALANCE_IDENTITY_AUDIT",
        },
        {
            "id": "PC2",
            "requirement": "O(h^7) implementation residual-defect certificate",
            "satisfied": pc2_direct_route_satisfied,
            "traceable_under_conditional_scope": pc2_direct_route_satisfied,
            "display_status": "traceable: direct D5 residual-value bridge satisfied",
            "satisfaction_mode": "D5 same-branch residual-value certificate: 96-row O(h^7) non-dynamic certificate plus 36 dynamic zero rows at Z_G",
        },
        {
            "id": "PC3",
            "requirement": "explicit eta_h^tube <= c_eta h^7 solver-policy theorem or theorem condition retained",
            "satisfied": solver_condition_retained,
            "traceable_under_conditional_scope": solver_condition_retained,
            "display_status": "traceable only by retained P6 theorem condition; solver-policy theorem not proved",
            "satisfaction_mode": "explicit_theorem_condition_retained_not_empirical_solver_evidence",
        },
        {
            "id": "PC4",
            "requirement": "residual-to-error obligations closed before four-link/slider-crank residual promotion",
            "satisfied": residual_promotion_not_made,
            "traceable_under_conditional_scope": residual_promotion_not_made,
            "display_status": "transfer-scope exclusion retained; residual-to-error theorem not closed",
            "satisfaction_mode": "nonpromotion_boundary_retained_residual_to_error_theorem_open",
            "nonpromotion_boundary_retained": residual_promotion_not_made,
            "residual_to_error_closed": False,
            "residual_to_error_route_promoted": False,
        },
    ]

    result = {
        "schema": "proof-closure-manifest-v1",
        "status": "pc2_closed_by_direct_residual_bridge_global_boundary_retained",
        "submission_ready": False,
        "submission_ready_scope": "proof_closure_global_boundary_not_narrowed_claim_package_decision",
        "proof_mode": proof_contract.get("proof_mode"),
        "accepted_theorem": {
            "accepted_method": proof_contract.get("accepted_method"),
            "accepted_method_order": proof_contract.get("accepted_method_order"),
            "accepted_global_error_order": proof_contract.get("accepted_global_error_order"),
            "accepted_local_defect_order": proof_contract.get("accepted_local_defect_order"),
            "comparator": proof_contract.get("comparator"),
        },
        "evidence_summary": {
            "total_runtime_rows": newton_scope.get("total_runtime_rows"),
            "certified_non_dynamic_rows": kinematic_scope.get("certified_row_count"),
            "active_direct_newton_euler_closed_rows": d5_direct_summary.get("dynamic_zero_residual_rows"),
            "active_direct_newton_euler_open_rows": 0 if pc2_direct_route_satisfied else newton_scope.get("dynamic_row_count"),
            "active_direct_newton_euler_open_obligations": 0 if pc2_direct_route_satisfied else newton_closure.get("open_obligation_count"),
            "open_dynamic_rows": newton_scope.get("dynamic_row_count"),
            "open_dynamic_rows_scope": "symbolic_primitive_certificate_route_not_active_direct_pc2",
            "newton_euler_open_obligations": newton_closure.get("open_obligation_count"),
            "newton_euler_open_obligations_scope": "symbolic_primitive_certificate_route_not_active_direct_pc2",
            "newton_euler_closed_obligations": newton_closure.get("closed_obligation_count"),
            "newton_euler_closed_obligation_ids": newton_closure.get("closed_obligation_ids", []),
            "newton_euler_symbolic_target_rows": newton_euler_targets.get("row_count"),
            "newton_euler_symbolic_target_translational_rows": newton_euler_targets.get("translational_row_count"),
            "newton_euler_symbolic_target_rotational_rows": newton_euler_targets.get("rotational_row_count"),
            "newton_euler_obligation_coverage_matrix_complete": newton_target_coverage.get(
                "coverage_matrix_complete"
            ),
            "newton_euler_row_obligation_links": newton_target_coverage.get("row_obligation_link_count"),
            "newton_euler_rows_with_complete_obligation_sets": newton_target_coverage.get(
                "rows_with_complete_obligation_sets"
            ),
            "newton_euler_obligations_with_target_rows": newton_target_coverage.get(
                "obligations_with_target_rows"
            ),
            "newton_euler_runtime_expression_structure_checked": newton_certificate_summary.get(
                "runtime_expression_structure_checked"
            ),
            "newton_euler_runtime_expression_structure_checked_rows": newton_certificate_summary.get(
                "runtime_expression_structure_checked_rows"
            ),
            "newton_euler_runtime_expression_structure_translational_rows": newton_certificate_summary.get(
                "runtime_expression_structure_translational_rows"
            ),
            "newton_euler_runtime_expression_structure_rotational_rows": newton_certificate_summary.get(
                "runtime_expression_structure_rotational_rows"
            ),
            "newton_euler_runtime_template_instantiation_checked": newton_certificate_summary.get(
                "runtime_template_instantiation_checked"
            ),
            "newton_euler_runtime_template_instantiation_checked_rows": newton_certificate_summary.get(
                "runtime_template_instantiation_checked_rows"
            ),
            "newton_euler_template_algebraic_equivalence_checked": newton_certificate_summary.get(
                "template_algebraic_equivalence_checked"
            ),
            "newton_euler_template_algebraic_equivalence_checked_rows": newton_certificate_summary.get(
                "template_algebraic_equivalence_checked_rows"
            ),
            "newton_euler_template_algebraic_equivalence_translational_rows": newton_certificate_summary.get(
                "template_algebraic_equivalence_translational_rows"
            ),
            "newton_euler_template_algebraic_equivalence_rotational_rows": newton_certificate_summary.get(
                "template_algebraic_equivalence_rotational_rows"
            ),
            "newton_euler_c2_template_algebraic_equivalence_closed": newton_certificate_summary.get(
                "c2_template_algebraic_equivalence_closed"
            ),
            "newton_euler_balance_identity_closed": newton_certificate_summary.get("balance_identity_closed"),
            "newton_euler_balance_identity_closed_rows": newton_certificate_summary.get(
                "balance_identity_closed_rows"
            ),
            "newton_euler_translational_balance_identity_closed": newton_certificate_summary.get(
                "translational_balance_identity_closed"
            ),
            "newton_euler_translational_balance_identity_closed_rows": newton_certificate_summary.get(
                "translational_balance_identity_closed_rows"
            ),
            "newton_euler_rotational_balance_identity_closed": newton_certificate_summary.get(
                "rotational_balance_identity_closed"
            ),
            "newton_euler_rotational_balance_identity_closed_rows": newton_certificate_summary.get(
                "rotational_balance_identity_closed_rows"
            ),
            "newton_euler_virtual_work_wrench_sign_skeleton_checked": newton_certificate_summary.get(
                "virtual_work_wrench_sign_skeleton_checked"
            ),
            "newton_euler_virtual_work_wrench_sign_skeleton_checked_rows": newton_certificate_summary.get(
                "virtual_work_wrench_sign_skeleton_checked_rows"
            ),
            "newton_euler_virtual_work_template_identity_proved": newton_certificate_summary.get(
                "virtual_work_template_identity_proved"
            ),
            "newton_euler_virtual_work_template_identity_rows": newton_certificate_summary.get(
                "virtual_work_template_identity_rows"
            ),
            "newton_euler_multiplier_wrench_consistency_closed": newton_certificate_summary.get(
                "multiplier_wrench_consistency_closed"
            ),
            "newton_euler_row_expanded_virtual_work_identity_proved": newton_certificate_summary.get(
                "row_expanded_virtual_work_identity_proved"
            ),
            "newton_euler_balance_identity_audit_checked": newton_euler_balance_identity.get(
                "balance_identity_closed"
            )
            is True,
            "newton_euler_row_expanded_virtual_work_identity_rows": newton_certificate_summary.get(
                "row_expanded_virtual_work_identity_rows"
            ),
            "newton_euler_dynamic_row_closure_contract_rows": newton_closure_contract_summary.get("row_count"),
            "newton_euler_dynamic_row_closure_contract_traceability_rows": newton_closure_contract_summary.get(
                "rows_with_full_runtime_traceability"
            ),
            "newton_euler_dynamic_row_closure_contract_theorem_closed_rows": newton_closure_contract_summary.get(
                "rows_with_direct_pc2_input_closure"
            ),
            "newton_euler_dynamic_row_closure_contract_open_rows": newton_closure_contract_summary.get(
                "open_row_count"
            ),
            "newton_euler_dynamic_row_closure_contract_pc_open": newton_closure_contract_summary.get(
                "unsatisfied_close_requirements"
            ),
            "b1_ad_expanded_symbolic_oracle_closure": b1_ad_expanded_closure.get(
                "ad_expanded_symbolic_oracle_closure"
            ),
            "b1_ad_expanded_symbolic_oracle_closed_rows": b1_ad_expanded_closure.get(
                "ad_expanded_symbolic_oracle_closed_rows"
            ),
            "b1_ad_expanded_symbolic_oracle_closed_cells": b1_ad_expanded_closure.get(
                "ad_expanded_symbolic_oracle_closed_cells"
            ),
            "b1_ad_expanded_symbolic_oracle_columns_per_row": b1_ad_expanded_closure.get(
                "columns_per_row"
            ),
            "b1_dynamic_symbolic_oracle_complete": b1_ad_expanded_closure.get(
                "dynamic_symbolic_oracle_complete"
            ),
            "b1_stage_residual_O_h7_from_certificate": b1_ad_expanded_closure.get(
                "stage_residual_O_h7_implementation_defect_proved_from_this_certificate"
            ),
            "b1_submission_ready_from_certificate": b1_ad_expanded_closure.get("submission_ready"),
            "b1_ad_expanded_certificate_status": b1_ad_expanded_closure.get("status"),
            "newton_euler_d5_dynamic_defect_blueprint_rows": newton_closure_contract_summary.get(
                "d5_dynamic_defect_blueprint_rows"
            ),
            "newton_euler_d5_open_lifted_stage_terms": newton_closure_contract_summary.get(
                "d5_open_lifted_stage_terms"
            ),
            "newton_euler_d5_rows_requiring_power_at_least_seven": newton_closure_contract_summary.get(
                "d5_rows_requiring_power_at_least_seven"
            ),
            "newton_euler_d5_finite_probe_sufficient_rows": newton_closure_contract_summary.get(
                "d5_finite_probe_sufficient_rows"
            ),
            "newton_euler_d5_residual_to_error_promotion_allowed_rows": newton_closure_contract_summary.get(
                "d5_residual_to_error_promotion_allowed_rows"
            ),
            "newton_euler_d5_blueprint_is_not_closure": newton_closure_contract_summary.get(
                "d5_blueprint_is_not_closure"
            ),
            "newton_euler_d5_readiness_rows": d5_readiness_summary.get("row_count"),
            "newton_euler_d5_readiness_runtime_ready_rows": d5_readiness_summary.get(
                "runtime_traceability_ready_rows"
            ),
            "newton_euler_d5_readiness_open_lifted_stage_terms": d5_readiness_summary.get(
                "open_lifted_stage_terms"
            ),
            "newton_euler_d5_readiness_theorem_certified_rows": d5_readiness_summary.get(
                "theorem_certified_rows"
            ),
            "newton_euler_d5_readiness_pc2_closed": d5_readiness.get("pc2_closed"),
            "newton_euler_d5_readiness_manifest_linked": d5_readiness.get("status")
            == "d5_direct_substitution_closure_recorded_primitive_taylor_route_open",
            "newton_euler_d5_direct_substitution_status": d5_direct_substitution.get("status"),
            "newton_euler_d5_direct_substitution_closed": d5_direct_substitution.get(
                "direct_route_mathematical_certificate_closed"
            ),
            "newton_euler_d5_direct_substitution_non_circular": d5_direct_substitution.get(
                "direct_route_non_circular"
            ),
            "newton_euler_d5_direct_substitution_stage_residual_O_h7": d5_direct_substitution.get(
                "stage_residual_O_h7_by_direct_route"
            ),
            "newton_euler_d5_direct_substitution_dynamic_zero_rows": d5_direct_summary.get(
                "dynamic_zero_residual_rows"
            ),
            "newton_euler_d5_direct_substitution_full_stage_rows": d5_direct_summary.get(
                "full_stage_rows_if_promoted"
            ),
            "newton_euler_d5_direct_substitution_forbidden_shortcuts": d5_direct_summary.get(
                "forbidden_shortcuts_used"
            ),
            "newton_euler_d5_direct_substitution_direct_route_pc2_active": pc2_direct_route_satisfied,
            "newton_euler_d5_direct_substitution_residual_to_error_promotion": False,
            "newton_euler_d5_direct_substitution_source_policy_promotion": False,
            "newton_euler_d5_direct_substitution_manifest_linked": d5_direct_substitution.get("schema")
            == "d5-dynamic-direct-substitution-certificate-v1",
            "newton_euler_d5_taylor_term_budget_rows": d5_term_budget_summary.get("dynamic_rows"),
            "newton_euler_d5_taylor_term_budget_terms": d5_term_budget_summary.get("term_rows"),
            "newton_euler_d5_taylor_term_budget_open_terms": d5_term_budget_summary.get(
                "open_taylor_bound_terms"
            ),
            "newton_euler_d5_taylor_term_budget_certified_terms": d5_term_budget_summary.get(
                "certified_taylor_bound_terms"
            ),
            "newton_euler_d5_taylor_strict_reduction_terms": d5_term_budget_summary.get(
                "strict_taylor_reduction_terms"
            ),
            "newton_euler_d5_taylor_anti_circular_terms": d5_term_budget_summary.get(
                "anti_circular_taylor_terms"
            ),
            "newton_euler_d5_taylor_terms_with_open_primitive_blockers": d5_term_budget_summary.get(
                "terms_with_open_primitive_blockers"
            ),
            "newton_euler_d5_taylor_unweighted_acceleration_blocked_terms": d5_term_budget_summary.get(
                "unweighted_acceleration_blocked_terms"
            ),
            "newton_euler_d5_taylor_h_weighted_acceleration_sufficient_terms": d5_term_budget_summary.get(
                "h_weighted_acceleration_sufficient_terms"
            ),
            "newton_euler_d5_taylor_h_weighted_acceleration_insufficient_terms": d5_term_budget_summary.get(
                "h_weighted_acceleration_insufficient_terms"
            ),
            "newton_euler_d5_taylor_primitive_blocker_usage": d5_term_budget_summary.get(
                "primitive_blocker_usage"
            ),
            "newton_euler_d5_taylor_template_usage": d5_term_budget_summary.get(
                "taylor_template_usage"
            ),
            "newton_euler_d5_taylor_term_budget_pc2_closed": d5_term_budget.get("pc2_closed"),
            "newton_euler_d5_taylor_term_budget_manifest_linked": d5_term_budget.get("status")
            == "d5_taylor_subterm_budget_recorded_pc2_open",
            "newton_euler_d5_primitive_reduction_terms": d5_primitive_reduction_summary.get("term_rows"),
            "newton_euler_d5_primitive_reduction_rules": d5_primitive_reduction_summary.get(
                "term_rows_with_reduction_rule"
            ),
            "newton_euler_d5_primitive_obligations": d5_primitive_reduction_summary.get(
                "primitive_obligation_count"
            ),
            "newton_euler_d5_primitive_obligations_proved": d5_primitive_reduction_summary.get(
                "primitive_obligations_proved"
            ),
            "newton_euler_d5_primitive_term_bounds_proved": d5_primitive_reduction_summary.get(
                "term_bounds_proved"
            ),
            "newton_euler_d5_primitive_reduction_pc2_closed": d5_primitive_reduction.get("pc2_closed"),
            "newton_euler_d5_primitive_reduction_manifest_linked": d5_primitive_reduction.get("status")
            == "primitive_reduction_recorded_pc2_open",
            "newton_euler_d5_smooth_force_corollary_label": d5_smooth_force_corollary.get("label"),
            "newton_euler_d5_smooth_force_corollary_main_flat_present": (
                d5_smooth_force_corollary.get("main_tex_present") is True
                and d5_smooth_force_corollary.get("flat_tex_present") is True
            ),
            "newton_euler_d5_smooth_force_conditionally_bound_terms": d5_smooth_force_corollary.get(
                "term_rows_conditionally_bound_under_lifts"
            ),
            "newton_euler_d5_smooth_force_summary_terms": d5_primitive_reduction_summary.get(
                "smooth_force_torque_lift_terms"
            ),
            "newton_euler_d5_smooth_force_primitive_inputs_assumed": d5_smooth_force_corollary.get(
                "primitive_inputs_assumed"
            ),
            "newton_euler_d5_smooth_force_actual_taylor_bounds_proved": d5_smooth_force_corollary.get(
                "actual_taylor_bounds_proved"
            ),
            "newton_euler_d5_smooth_force_primitive_closed": d5_smooth_force_corollary.get(
                "primitive_closed"
            ),
            "newton_euler_d5_smooth_force_pc2_closed": d5_smooth_force_corollary.get("pc2_closed"),
            "newton_euler_d5_smooth_force_d4_direct_route_used_as_rate_proof": (
                d5_smooth_force_corollary.get("uses_d4_direct_route_smoothness_as_rate_proof")
            ),
            "newton_euler_d5_p_tube_constants_closed": d5_p_tube_constants.get("primitive_closed"),
            "newton_euler_d5_p_tube_constants_term_rows": d5_p_tube_summary.get("term_rows_using_p_tube"),
            "newton_euler_d5_p_tube_constants_remaining_primitives": d5_p_tube_summary.get(
                "primitive_obligations_remaining"
            ),
            "newton_euler_d5_p_tube_constants_induced_bounds_proved": d5_p_tube_summary.get(
                "induced_taylor_bounds_proved"
            ),
            "newton_euler_d5_p_tube_constants_pc2_closed": d5_p_tube_constants.get("pc2_closed"),
            "newton_euler_d5_p_tube_constants_manifest_linked": d5_p_tube_constants.get("status")
            == "p_tube_compact_constants_closed_pc2_open",
            "newton_euler_d5_p_state_gap_recorded": d5_p_state_gap.get("status")
            == "p_state_lift_gap_recorded_pc2_open",
            "newton_euler_d5_p_state_closed": d5_p_state_gap.get("primitive_closed"),
            "newton_euler_d5_p_state_map_definition_recorded": d5_p_state_map_definition.get("status")
            == "p_state_map_definition_closed_lift_open",
            "newton_euler_d5_p_state_map_definition_closed": d5_p_state_map_definition.get(
                "ps1_map_definition_closed"
            ),
            "newton_euler_d5_p_state_map_rows": d5_p_state_map_summary.get("non_dynamic_map_rows"),
            "newton_euler_d5_p_state_map_subproofs_closed": d5_p_state_map_summary.get(
                "closed_subproof_count"
            ),
            "newton_euler_d5_p_state_map_required_subproofs": d5_p_state_map_summary.get(
                "required_subproof_count"
            ),
            "newton_euler_d5_p_state_map_pc2_closed": d5_p_state_map_definition.get("pc2_closed"),
            "newton_euler_d5_p_state_anticircularity_recorded": d5_p_state_anticircularity.get("status")
            == "p_state_ps4_anticircularity_closed_lift_open",
            "newton_euler_d5_p_state_anticircularity_closed": d5_p_state_anticircularity.get(
                "ps4_anticircularity_closed"
            ),
            "newton_euler_d5_p_state_anticircularity_subproofs_after": d5_p_state_anticircularity_summary.get(
                "closed_p_state_subproofs_after_ps4"
            ),
            "newton_euler_d5_p_state_anticircularity_open_subproofs_after": d5_p_state_anticircularity_summary.get(
                "open_p_state_subproofs_after_ps4"
            ),
            "newton_euler_d5_p_state_anticircularity_pc2_closed": d5_p_state_anticircularity.get("pc2_closed"),
            "newton_euler_d5_p_state_ps2_weighted_target_recorded": d5_p_state_ps2_target.get("status")
            == "p_state_ps2_weighted_infsup_target_recorded_ps2_open",
            "newton_euler_d5_p_state_ps2_weighted_target_spec_closed": d5_p_state_ps2_target.get(
                "ps2_target_spec_closed"
            ),
            "newton_euler_d5_p_state_ps2_weighted_target_infsup_closed": d5_p_state_ps2_target.get(
                "ps2_inverse_or_infsup_closed"
            ),
            "newton_euler_d5_p_state_ps2_weighted_target_state_dim": d5_p_state_ps2_target_summary.get(
                "state_block_dimension"
            ),
            "newton_euler_d5_p_state_ps2_weighted_target_acc_dim": d5_p_state_ps2_target_summary.get(
                "auxiliary_acceleration_dimension"
            ),
            "newton_euler_d5_p_state_ps2_weighted_target_row_dim": d5_p_state_ps2_target_summary.get(
                "non_dynamic_row_dimension"
            ),
            "newton_euler_d5_p_state_ps2_weighted_target_pc2_closed": d5_p_state_ps2_target.get("pc2_closed"),
            "newton_euler_d5_p_state_ps2_kinematic_block_recorded": d5_p_state_ps2_kinematic.get(
                "ps2_kinematic_block_certificate_recorded"
            ),
            "newton_euler_d5_p_state_ps2_kinematic_subblock_bound_certified": d5_p_state_ps2_kinematic.get(
                "certifies_uniform_euclidean_kinematic_subblock_bound"
            ),
            "newton_euler_d5_p_state_ps2_kinematic_full_nonlinear_ps2_certified": d5_p_state_ps2_kinematic.get(
                "certifies_full_nonlinear_ps2"
            ),
            "newton_euler_d5_p_state_ps2_kinematic_rows": d5_p_state_ps2_kinematic_dims.get(
                "kinematic_row_dimension"
            ),
            "newton_euler_d5_p_state_ps2_kinematic_lower_pair_surplus_rows": (
                d5_p_state_ps2_kinematic_dims.get("lower_pair_surplus_rows_not_needed_for_subblock")
            ),
            "newton_euler_d5_p_state_ps2_kinematic_inverse_template_norm": (
                d5_p_state_ps2_kinematic_constants.get("kinematic_inverse_template_2_norm_at_h_max")
            ),
            "newton_euler_d5_p_state_ps2_kinematic_binding_gap_count": len(
                d5_p_state_ps2_kinematic.get("remaining_binding_gaps", [])
            ),
            "newton_euler_d5_p_state_ps2_kinematic_pc2_closed": d5_p_state_ps2_kinematic.get("pc2_closed"),
            "newton_euler_d5_p_state_ps2_lie_chart_binding_recorded": d5_p_state_ps2_lie_chart.get(
                "p_state_ps2_lie_chart_binding_recorded"
            ),
            "newton_euler_d5_p_state_ps2_lie_chart_so3_norm_equivalence": d5_p_state_ps2_lie_chart.get(
                "certifies_so3_chart_norm_equivalence"
            ),
            "newton_euler_d5_p_state_ps2_lie_chart_full_mean_value_binding": d5_p_state_ps2_lie_chart.get(
                "certifies_full_nonlinear_mean_value_binding"
            ),
            "newton_euler_d5_p_state_ps2_lie_chart_full_nonlinear_ps2": d5_p_state_ps2_lie_chart.get(
                "certifies_full_nonlinear_ps2"
            ),
            "newton_euler_d5_p_state_ps2_lie_chart_equivalence_factor": (
                d5_p_state_ps2_lie_chart_constants.get("chart_equivalence_factor")
            ),
            "newton_euler_d5_p_state_ps2_lie_chart_remaining_binding_gaps": len(
                d5_p_state_ps2_lie_chart.get("remaining_binding_gaps", [])
            ),
            "newton_euler_d5_p_state_ps2_lie_chart_pc2_closed": d5_p_state_ps2_lie_chart.get("pc2_closed"),
            "newton_euler_d5_p_state_ps2_row_injection_recorded": d5_p_state_ps2_row_injection.get(
                "p_state_ps2_row_injection_recorded"
            ),
            "newton_euler_d5_p_state_ps2_row_injection_72_to_96_certified": d5_p_state_ps2_row_injection.get(
                "certifies_72_to_96_row_injection"
            ),
            "newton_euler_d5_p_state_ps2_row_injection_unweighted_scaling": d5_p_state_ps2_row_injection.get(
                "certifies_unweighted_residual_scaling"
            ),
            "newton_euler_d5_p_state_ps2_row_injection_selector_norm": d5_p_state_ps2_row_injection.get(
                "row_selection_operator_2_norm"
            ),
            "newton_euler_d5_p_state_ps2_row_injection_full_mean_value_binding": d5_p_state_ps2_row_injection.get(
                "certifies_full_nonlinear_mean_value_binding"
            ),
            "newton_euler_d5_p_state_ps2_row_injection_full_nonlinear_ps2": d5_p_state_ps2_row_injection.get(
                "certifies_full_nonlinear_ps2"
            ),
            "newton_euler_d5_p_state_ps2_row_injection_remaining_binding_gaps": len(
                d5_p_state_ps2_row_injection.get("remaining_binding_gaps", [])
            ),
            "newton_euler_d5_p_state_ps2_row_injection_pc2_closed": d5_p_state_ps2_row_injection.get("pc2_closed"),
            "newton_euler_d5_p_state_ps2_nonlinear_binding_recorded": d5_p_state_ps2_nonlinear.get(
                "p_state_ps2_nonlinear_binding_recorded"
            ),
            "newton_euler_d5_p_state_ps2_nonlinear_rotational_mean_value": d5_p_state_ps2_nonlinear.get(
                "certifies_rotational_lie_row_mean_value_binding"
            ),
            "newton_euler_d5_p_state_ps2_nonlinear_full_mean_value": d5_p_state_ps2_nonlinear.get(
                "certifies_full_nonlinear_mean_value_binding"
            ),
            "newton_euler_d5_p_state_ps2_nonlinear_full_ps2": d5_p_state_ps2_nonlinear.get(
                "certifies_full_nonlinear_ps2"
            ),
            "newton_euler_d5_p_state_ps2_nonlinear_promotion_gaps": len(
                d5_p_state_ps2_nonlinear.get("remaining_promotion_gaps", [])
            ),
            "newton_euler_d5_p_state_ps2_nonlinear_pc2_closed": d5_p_state_ps2_nonlinear.get("pc2_closed"),
            "newton_euler_d5_p_state_ps2_aggregate_promotion_recorded": d5_p_state_ps2_aggregate.get(
                "p_state_ps2_aggregate_promotion_recorded"
            ),
            "newton_euler_d5_p_state_ps2_aggregate_weighted_inverse_certified": (
                d5_p_state_ps2_aggregate.get("certifies_aggregate_weighted_ps2_inverse")
            ),
            "newton_euler_d5_p_state_ps2_aggregate_uniform_constant_certified": d5_p_state_ps2_aggregate.get(
                "certifies_uniform_ps2_constant"
            ),
            "newton_euler_d5_p_state_ps2_aggregate_inverse_or_infsup_closed": d5_p_state_ps2_aggregate.get(
                "ps2_inverse_or_infsup_closed"
            ),
            "newton_euler_d5_p_state_ps2_aggregate_ps3_actual_conversion_closed": (
                d5_p_state_ps2_aggregate.get("ps3_actual_state_lift_conversion_closed")
            ),
            "newton_euler_d5_p_state_ps2_aggregate_p_state_closed": d5_p_state_ps2_aggregate.get(
                "primitive_closed"
            ),
            "newton_euler_d5_p_state_ps2_aggregate_pc2_closed": d5_p_state_ps2_aggregate.get("pc2_closed"),
            "newton_euler_d5_p_state_ps2_linearization_probe_recorded": d5_p_state_ps2_probe.get(
                "ps2_weighted_linearization_probe_recorded"
            ),
            "newton_euler_d5_p_state_ps2_linearization_probe_full_column_rank_all": d5_p_state_ps2_probe_summary.get(
                "finite_probe_full_column_rank_all"
            ),
            "newton_euler_d5_p_state_ps2_linearization_probe_rank_range": [
                d5_p_state_ps2_probe_summary.get("min_weighted_operator_rank"),
                d5_p_state_ps2_probe_summary.get("max_weighted_operator_rank"),
            ],
            "newton_euler_d5_p_state_ps2_linearization_probe_min_singular": d5_p_state_ps2_probe_summary.get(
                "min_singular_value_across_probes"
            ),
            "newton_euler_d5_p_state_ps2_linearization_probe_max_state_projection_constant": d5_p_state_ps2_probe_summary.get(
                "max_finite_state_projection_constant"
            ),
            "newton_euler_d5_p_state_ps2_linearization_probe_uniform_constant_proved": d5_p_state_ps2_probe.get(
                "uniform_constant_proved"
            ),
            "newton_euler_d5_p_state_ps2_linearization_probe_pc2_closed": d5_p_state_ps2_probe.get("pc2_closed"),
            "newton_euler_d5_p_state_ps3_conditional_conversion_recorded": d5_p_state_ps3_conversion.get(
                "status"
            )
            == "p_state_ps3_conditional_conversion_recorded_ps3_actual_open",
            "newton_euler_d5_p_state_ps3_conditional_conversion_closed": d5_p_state_ps3_conversion.get(
                "ps3_conditional_conversion_closed"
            ),
            "newton_euler_d5_p_state_ps3_actual_conversion_closed": d5_p_state_ps3_conversion.get(
                "ps3_actual_state_lift_conversion_closed"
            ),
            "newton_euler_d5_p_state_ps3_ps2_dependency_satisfied_by_aggregate": (
                d5_p_state_ps3_conversion.get("ps2_dependency_satisfied_by_aggregate")
            ),
            "newton_euler_d5_p_state_ps3_ps2_inverse_or_infsup_closed": (
                d5_p_state_ps3_conversion.get("ps2_inverse_or_infsup_closed")
            ),
            "newton_euler_d5_p_state_ps3_actual_input_instantiation_closed": (
                d5_p_state_ps3_conversion.get("actual_ps3_input_instantiation_closed")
            ),
            "newton_euler_d5_p_state_ps3_weighted_acceleration_rate": d5_p_state_ps3_conversion_summary.get(
                "weighted_acceleration_input_rate"
            ),
            "newton_euler_d5_p_state_ps3_conditional_state_lift_rate": d5_p_state_ps3_conversion_summary.get(
                "conditional_state_lift_rate"
            ),
            "newton_euler_d5_p_state_ps3_pc2_closed": d5_p_state_ps3_conversion.get("pc2_closed"),
            "newton_euler_d5_p_state_ps3_actual_gap_recorded": (
                d5_p_state_ps3_actual_gap.get("status")
                == "ps3_actual_instantiation_gap_recorded_actual_ps3_open"
            ),
            "newton_euler_d5_p_state_ps3_actual_gap_inputs_closed": d5_p_state_ps3_actual_gap.get(
                "summary", {}
            ).get("input_requirements_closed"),
            "newton_euler_d5_p_state_ps3_actual_gap_inputs_total": d5_p_state_ps3_actual_gap.get(
                "summary", {}
            ).get("input_requirements_total"),
            "newton_euler_d5_p_state_ps3_actual_gap_independent_h_acc_input_closed": (
                d5_p_state_ps3_actual_gap.get("summary", {}).get(
                    "independent_h_weighted_acceleration_input_closed"
                )
            ),
            "newton_euler_d5_p_state_ps3_actual_gap_non_circular_instantiation_closed": (
                d5_p_state_ps3_actual_gap.get("summary", {}).get("non_circular_ps3_instantiation_closed")
            ),
            "newton_euler_d5_p_state_ps3_actual_gap_p_state_closed": d5_p_state_ps3_actual_gap.get(
                "primitive_closed"
            ),
            "newton_euler_d5_p_state_ps3_actual_gap_pc2_closed": d5_p_state_ps3_actual_gap.get(
                "pc2_closed"
            ),
            "newton_euler_d5_p_state_ps3_h_acc_obstruction_recorded": (
                d5_p_state_ps3_h_acc_obstruction_summary.get(
                    "h_acceleration_input_obstruction_recorded"
                )
            ),
            "newton_euler_d5_p_state_ps3_h_acc_obstruction_finite_nullity_min": (
                d5_p_state_ps3_h_acc_obstruction_summary.get("finite_probe_nullity_min")
            ),
            "newton_euler_d5_p_state_ps3_h_acc_obstruction_finite_nullity_max": (
                d5_p_state_ps3_h_acc_obstruction_summary.get("finite_probe_nullity_max")
            ),
            "newton_euler_d5_p_state_ps3_h_acc_obstruction_residual_only_input_sufficient": (
                d5_p_state_ps3_h_acc_obstruction_summary.get(
                    "residual_only_input_sufficient_for_h_acceleration"
                )
            ),
            "newton_euler_d5_p_state_ps3_h_acc_obstruction_independent_h_acc_input_closed": (
                d5_p_state_ps3_h_acc_obstruction_summary.get(
                    "independent_h_weighted_acceleration_input_closed"
                )
            ),
            "newton_euler_d5_p_state_ps3_h_acc_obstruction_actual_ps3_closed": (
                d5_p_state_ps3_h_acc_obstruction_summary.get(
                    "ps3_actual_state_lift_conversion_closed"
                )
            ),
            "newton_euler_d5_p_state_ps3_h_acc_obstruction_pc2_closed": (
                d5_p_state_ps3_h_acc_obstruction.get("pc2_closed")
            ),
            "newton_euler_d5_p_state_ps3_h_acc_obstruction_finite_probe_is_proof": (
                d5_p_state_ps3_h_acc_obstruction.get("finite_probe_is_proof")
            ),
            "newton_euler_d5_p_state_term_rows": d5_p_state_summary.get("term_rows_using_p_state"),
            "newton_euler_d5_p_state_future_subproofs_closed": d5_p_state_summary.get(
                "required_future_subproofs_closed"
            ),
            "newton_euler_d5_p_state_future_subproofs": d5_p_state_summary.get("required_future_subproofs"),
            "newton_euler_d5_p_state_induced_bounds_proved": d5_p_state_summary.get(
                "induced_taylor_bounds_proved"
            ),
            "newton_euler_d5_p_state_pc2_closed": d5_p_state_gap.get("pc2_closed"),
            "newton_euler_d5_p_acc_map_definition_recorded": d5_p_acc_map_definition.get("status")
            == "p_acc_map_definition_closed_lift_open",
            "newton_euler_d5_p_acc_map_definition_closed": d5_p_acc_map_definition.get(
                "pa1_map_definition_closed"
            ),
            "newton_euler_d5_p_acc_map_rows": d5_p_acc_map_summary.get("term_rows_conditionally_mapped"),
            "newton_euler_d5_p_acc_map_subproofs_closed": d5_p_acc_map_summary.get(
                "closed_subproof_count"
            ),
            "newton_euler_d5_p_acc_map_required_subproofs": d5_p_acc_map_summary.get(
                "required_subproof_count"
            ),
            "newton_euler_d5_p_acc_map_pc2_closed": d5_p_acc_map_definition.get("pc2_closed"),
            "newton_euler_d5_p_acc_row_binding_recorded": d5_p_acc_row_binding.get("status")
            == "p_acc_row_binding_closed_lift_open",
            "newton_euler_d5_p_acc_row_binding_closed": d5_p_acc_row_binding.get(
                "pa4_row_binding_closed"
            ),
            "newton_euler_d5_p_acc_row_binding_rows": d5_p_acc_row_binding_summary.get(
                "term_rows_bound_to_ordering"
            ),
            "newton_euler_d5_p_acc_row_binding_subproofs_after": d5_p_acc_row_binding_summary.get(
                "p_acc_closed_subproof_count_after_binding"
            ),
            "newton_euler_d5_p_acc_row_binding_required_subproofs": d5_p_acc_row_binding_summary.get(
                "required_subproof_count"
            ),
            "newton_euler_d5_p_acc_row_binding_pc2_closed": d5_p_acc_row_binding.get("pc2_closed"),
            "newton_euler_d5_p_acc_independence_recorded": d5_p_acc_independence.get("status")
            == "p_acc_independence_closed_lift_open",
            "newton_euler_d5_p_acc_independence_closed": d5_p_acc_independence.get(
                "pa3_independence_closed"
            ),
            "newton_euler_d5_p_acc_independence_input_families": d5_p_acc_independence_summary.get(
                "non_dynamic_input_families_certified"
            ),
            "newton_euler_d5_p_acc_independence_required_input_families": d5_p_acc_independence_summary.get(
                "required_non_dynamic_input_families"
            ),
            "newton_euler_d5_p_acc_independence_subproofs_after": d5_p_acc_independence_summary.get(
                "p_acc_closed_subproof_count_after_independence"
            ),
            "newton_euler_d5_p_acc_independence_required_subproofs": d5_p_acc_independence_summary.get(
                "required_subproof_count"
            ),
            "newton_euler_d5_p_acc_independence_pc2_closed": d5_p_acc_independence.get("pc2_closed"),
            "newton_euler_d5_p_acc_pa2_obstruction_recorded": d5_p_acc_lift_obstruction.get("status")
            == "p_acc_pa2_obstruction_recorded_lift_open",
            "newton_euler_d5_p_acc_pa2_closed": d5_p_acc_lift_obstruction.get("pa2_closed"),
            "newton_euler_d5_p_acc_velocity_collocation_alone_sufficient": d5_p_acc_lift_obstruction.get(
                "velocity_collocation_alone_sufficient_for_O_h7_acceleration"
            ),
            "newton_euler_d5_p_acc_current_unweighted_acceleration_rate": d5_p_acc_lift_obstruction.get(
                "current_recorded_inputs_imply_only_unweighted_acceleration_rate"
            ),
            "newton_euler_d5_p_acc_lift_rate_proved": d5_p_acc_lift_obstruction.get(
                "acceleration_lift_rate_proved"
            ),
            "newton_euler_d5_p_acc_lift_obstruction_term_bounds_proved": d5_p_acc_lift_obstruction.get(
                "term_bounds_proved"
            ),
            "newton_euler_d5_p_acc_lift_obstruction_pc2_closed": d5_p_acc_lift_obstruction.get(
                "pc2_closed"
            ),
            "newton_euler_d5_p_acc_pa2_weighted_inverse_recorded": d5_p_acc_pa2_weighted_inverse.get(
                "pa2_weighted_inverse_probe_recorded"
            ),
            "newton_euler_d5_p_acc_pa2_weighted_h_control_recorded": d5_p_acc_pa2_weighted_inverse.get(
                "weighted_h_acceleration_control_recorded"
            ),
            "newton_euler_d5_p_acc_pa2_weighted_inverse_probe_count": d5_p_acc_pa2_weighted_inverse_summary.get(
                "probe_count"
            ),
            "newton_euler_d5_p_acc_pa2_weighted_inverse_full_rank_all": d5_p_acc_pa2_weighted_inverse_summary.get(
                "finite_probe_full_column_rank_all"
            ),
            "newton_euler_d5_p_acc_pa2_max_unweighted_acceleration_projection_constant": (
                d5_p_acc_pa2_weighted_inverse_summary.get(
                    "max_unweighted_acceleration_projection_constant"
                )
            ),
            "newton_euler_d5_p_acc_pa2_max_weighted_h_acceleration_projection_constant": (
                d5_p_acc_pa2_weighted_inverse_summary.get(
                    "max_weighted_h_acceleration_projection_constant"
                )
            ),
            "newton_euler_d5_p_acc_pa2_unweighted_uniform_control_proved": (
                d5_p_acc_pa2_weighted_inverse.get("unweighted_acceleration_uniform_control_proved")
            ),
            "newton_euler_d5_p_acc_pa2_weighted_inverse_pa2_closed": d5_p_acc_pa2_weighted_inverse.get(
                "pa2_closed"
            ),
            "newton_euler_d5_p_acc_pa2_weighted_inverse_pc2_closed": d5_p_acc_pa2_weighted_inverse.get(
                "pc2_closed"
            ),
            "newton_euler_d5_p_lambda_interface_recorded": d5_p_lambda_interface.get("status")
            == "p_lambda_interface_closed_lift_open",
            "newton_euler_d5_p_lambda_interface_closed": d5_p_lambda_interface.get(
                "pl1_interface_closed"
            ),
            "newton_euler_d5_p_lambda_pl2_geometric_margin_recorded": (
                d5_p_lambda_pl2_geometric_margin.get("status")
                == "pl2_uniform_inf_sup_bound_proved_p_lambda_rate_open"
            ),
            "newton_euler_d5_p_lambda_pl2_uniform_inf_sup_bound_proved": (
                d5_p_lambda_pl2_geometric_margin.get("pl2_uniform_inf_sup_bound_proved")
            ),
            "newton_euler_d5_p_lambda_pl2_symbolic_margin_premise_proved": (
                d5_p_lambda_pl2_summary.get("symbolic_margin_premise_proved")
            ),
            "newton_euler_d5_p_lambda_pl2_probe_stage_rows": d5_p_lambda_pl2_summary.get(
                "probe_stage_rows"
            ),
            "newton_euler_d5_p_lambda_pl2_finite_probe_sufficient_for_uniform_proof": (
                d5_p_lambda_pl2_implication.get("finite_probe_sufficient_for_uniform_proof")
            ),
            "newton_euler_d5_p_lambda_pl2_primitive_closed": (
                d5_p_lambda_pl2_geometric_margin.get("primitive_closed")
            ),
            "newton_euler_d5_p_lambda_pl2_pc2_closed": d5_p_lambda_pl2_geometric_margin.get(
                "pc2_closed"
            ),
            "newton_euler_d5_p_lambda_d3_noncircularity_recorded": (
                d5_p_lambda_d3_noncircularity.get("status")
                == "p_lambda_d3_noncircularity_closed_lift_open"
            ),
            "newton_euler_d5_p_lambda_d3_noncircularity_closed": d5_p_lambda_d3_noncircularity.get(
                "pl3_d3_noncircularity_closed"
            ),
            "newton_euler_d5_p_lambda_pl4_rate_propagation_recorded": (
                d5_p_lambda_pl4_rate_propagation.get("status")
                == "p_lambda_pl4_rate_propagation_closed_conditionally_lift_open"
            ),
            "newton_euler_d5_p_lambda_pl4_rate_propagation_closed": d5_p_lambda_pl4_rate_propagation.get(
                "pl4_lift_propagation_closed"
            ),
            "newton_euler_d5_p_lambda_pl4_conditional_multiplier_rate": (
                d5_p_lambda_pl4_rate_propagation.get("conditional_multiplier_lift_rate_proved")
            ),
            "newton_euler_d5_p_lambda_pl4_actual_multiplier_rate": d5_p_lambda_pl4_rate_propagation.get(
                "multiplier_lift_rate_proved"
            ),
            "newton_euler_d5_p_lambda_pl4_open_input_dependencies": d5_p_lambda_pl4_summary.get(
                "open_input_dependency_count"
            ),
            "newton_euler_d5_p_lambda_stage_variables": d5_p_lambda_summary.get("stage_lambda_variables"),
            "newton_euler_d5_p_lambda_direct_rows": d5_p_lambda_summary.get(
                "direct_multiplier_term_rows"
            ),
            "newton_euler_d5_p_lambda_term_rows": d5_p_lambda_summary.get(
                "term_rows_using_p_lambda"
            ),
            "newton_euler_d5_p_lambda_subproofs_after": d5_p_lambda_summary.get(
                "p_lambda_closed_subproof_count_after_interface"
            )
            if d5_p_lambda_pl4_summary.get("p_lambda_closed_subproof_count_after_pl4") is None
            else d5_p_lambda_pl4_summary.get("p_lambda_closed_subproof_count_after_pl4"),
            "newton_euler_d5_p_lambda_open_subproofs_after": d5_p_lambda_pl4_summary.get(
                "open_subproof_count_after_pl4"
            ),
            "newton_euler_d5_p_lambda_required_subproofs": d5_p_lambda_summary.get(
                "required_subproof_count"
            ),
            "newton_euler_d5_p_lambda_conditional_pl_subproofs_complete": (
                d5_p_lambda_pl4_summary.get("p_lambda_closed_subproof_count_after_pl4")
                == d5_p_lambda_summary.get("required_subproof_count")
                and d5_p_lambda_pl4_summary.get("open_subproof_count_after_pl4") == 0
                and d5_p_lambda_pl4_rate_propagation.get(
                    "conditional_multiplier_lift_rate_proved"
                )
                is True
            ),
            "newton_euler_d5_p_lambda_actual_multiplier_lift_open": (
                d5_p_lambda_pl4_rate_propagation.get("multiplier_lift_rate_proved")
                is False
                and d5_p_lambda_interface.get("primitive_closed") is False
                and d5_p_lambda_interface.get("pc2_closed") is False
            ),
            "newton_euler_d5_p_lambda_conditional_subproof_scope": (
                "PL1/PL2/PL3/PL4 subproof count is complete only for the conditional "
                "propagation mechanism; the actual multiplier lift still depends "
                "on open P_state and P_acc inputs and certifies no primitive "
                "Taylor subterm."
            ),
            "newton_euler_d5_p_lambda_primitive_closed": d5_p_lambda_interface.get("primitive_closed"),
            "newton_euler_d5_p_lambda_pc2_closed": d5_p_lambda_interface.get("pc2_closed"),
            "newton_euler_d5_p_geom_reduction_recorded": d5_p_geom_reduction.get("status")
            == "p_geom_chart_reduction_closed_primitive_open",
            "newton_euler_d5_p_geom_chart_reduction_closed": d5_p_geom_reduction.get("chart_reduction_closed"),
            "newton_euler_d5_p_geom_actual_primitive_open": (
                d5_p_geom_reduction.get("primitive_closed") is False
                and d5_p_geom_reduction.get("pc2_closed") is False
                and d5_p_geom_summary.get("open_dependency_count") == 2
            ),
            "newton_euler_d5_p_geom_conditional_reduction_scope": (
                "chart reduction closed means only the downstream conditional "
                "Lipschitz map under open P_state and P_lambda inputs; the "
                "actual P_geom primitive and PC2 remain open and certify no "
                "primitive Taylor subterm without those lifts."
            ),
            "newton_euler_d5_p_geom_closed_subproofs": d5_p_geom_summary.get("closed_subproof_count"),
            "newton_euler_d5_p_geom_required_subproofs": d5_p_geom_summary.get("required_subproof_count"),
            "newton_euler_d5_p_geom_open_dependencies": d5_p_geom_summary.get("open_dependency_count"),
            "newton_euler_d5_p_geom_conditionally_reduced_rows": d5_p_geom_summary.get(
                "term_rows_conditionally_reduced"
            ),
            "newton_euler_d5_p_geom_translational_rows": d5_p_geom_summary.get(
                "translational_rows_conditionally_reduced"
            ),
            "newton_euler_d5_p_geom_rotational_rows": d5_p_geom_summary.get(
                "rotational_rows_conditionally_reduced"
            ),
            "newton_euler_d5_p_geom_primitive_closed": d5_p_geom_reduction.get("primitive_closed"),
            "newton_euler_d5_p_geom_pc2_closed": d5_p_geom_reduction.get("pc2_closed"),
            "newton_euler_d5_p_gyro_reduction_recorded": d5_p_gyro_reduction.get("status")
            == "p_gyro_bilinear_reduction_closed_primitive_open",
            "newton_euler_d5_p_gyro_algebraic_reduction_closed": d5_p_gyro_reduction.get(
                "algebraic_reduction_closed"
            ),
            "newton_euler_d5_p_gyro_internal_reduction_complete_not_primitive": (
                d5_p_gyro_reduction.get("algebraic_reduction_closed") is True
                and d5_p_gyro_summary.get("closed_subproof_count")
                == d5_p_gyro_summary.get("required_subproof_count")
                and d5_p_gyro_reduction.get("primitive_closed") is False
            ),
            "newton_euler_d5_p_gyro_actual_primitive_open": (
                d5_p_gyro_reduction.get("primitive_closed") is False
                and d5_p_gyro_reduction.get("pc2_closed") is False
                and d5_p_gyro_summary.get("open_dependency_count") == 1
            ),
            "newton_euler_d5_p_gyro_conditional_reduction_scope": (
                "algebraic reduction closed means only the internal bilinear "
                "gyroscopic reduction under the open P_state angular-velocity "
                "input; the actual P_gyro primitive and PC2 remain open and "
                "certify no primitive Taylor subterm without that lift."
            ),
            "newton_euler_d5_p_gyro_closed_subproofs": d5_p_gyro_summary.get("closed_subproof_count"),
            "newton_euler_d5_p_gyro_required_subproofs": d5_p_gyro_summary.get("required_subproof_count"),
            "newton_euler_d5_p_gyro_open_dependencies": d5_p_gyro_summary.get("open_dependency_count"),
            "newton_euler_d5_p_gyro_conditionally_reduced_rows": d5_p_gyro_summary.get(
                "term_rows_conditionally_reduced"
            ),
            "newton_euler_d5_p_gyro_primitive_closed": d5_p_gyro_reduction.get("primitive_closed"),
            "newton_euler_d5_p_gyro_pc2_closed": d5_p_gyro_reduction.get("pc2_closed"),
            "newton_euler_d5_primitive_closure_plan_obligations": d5_primitive_closure_summary.get(
                "primitive_obligation_count"
            ),
            "newton_euler_d5_primitive_closure_plan_interfaces": d5_primitive_closure_summary.get(
                "primitive_obligations_with_closure_steps"
            ),
            "newton_euler_d5_primitive_closure_plan_proved": d5_primitive_closure_summary.get(
                "primitive_obligations_proved"
            ),
            "newton_euler_d5_primitive_closure_plan_open": d5_primitive_closure_summary.get(
                "open_primitive_obligations"
            ),
            "newton_euler_d5_primitive_closure_plan_induced_bounds_proved": d5_primitive_closure_summary.get(
                "induced_taylor_bounds_proved"
            ),
            "newton_euler_d5_primitive_closure_plan_pc2_closed": d5_primitive_closure_plan.get("pc2_closed"),
            "newton_euler_d5_primitive_closure_plan_manifest_linked": d5_primitive_closure_plan.get("status")
            == "primitive_obligation_closure_plan_recorded_primitive_taylor_pc2_open",
            "newton_euler_d5_conditional_taylor_certificate_terms": d5_conditional_taylor_summary.get(
                "term_rows"
            ),
            "newton_euler_d5_conditional_taylor_certificate_rows": d5_conditional_taylor_summary.get(
                "dynamic_rows"
            ),
            "newton_euler_d5_conditional_taylor_certificate_conditional_terms": d5_conditional_taylor_summary.get(
                "conditional_term_bounds_under_open_primitive_assumptions"
            ),
            "newton_euler_d5_conditional_taylor_certificate_conditional_rows": d5_conditional_taylor_summary.get(
                "conditional_dynamic_rows_under_open_primitive_assumptions"
            ),
            "newton_euler_d5_conditional_taylor_certificate_actual_terms_proved": d5_conditional_taylor_summary.get(
                "actual_taylor_bounds_proved"
            ),
            "newton_euler_d5_conditional_taylor_certificate_open_primitive_assumptions": d5_conditional_taylor_summary.get(
                "open_primitive_assumption_count"
            ),
            "newton_euler_d5_conditional_taylor_certificate_pc2_closed": d5_conditional_taylor_certificate.get(
                "pc2_closed"
            ),
            "newton_euler_d5_conditional_taylor_certificate_manifest_linked": (
                d5_conditional_taylor_certificate.get("status")
                == "conditional_taylor_certificate_recorded_primitive_taylor_pc2_open"
            ),
            "newton_euler_d5_open_primitive_gap_recorded": d5_open_primitive_gap.get("status")
            == "open_primitive_gaps_recorded_primitive_taylor_pc2_open",
            "newton_euler_d5_open_primitive_gap_count": d5_open_primitive_summary.get("open_primitive_count"),
            "newton_euler_d5_open_primitive_gap_future_subproofs": d5_open_primitive_summary.get(
                "total_future_subproofs"
            ),
            "newton_euler_d5_open_primitive_gap_future_subproofs_closed": d5_open_primitive_summary.get(
                "future_subproofs_closed"
            ),
            "newton_euler_d5_open_primitive_gap_induced_bounds_proved": d5_open_primitive_summary.get(
                "induced_taylor_bounds_proved"
            ),
            "newton_euler_d5_open_primitive_gap_pc2_closed": d5_open_primitive_gap.get("pc2_closed"),
            "residual_to_error_blocking_obligations": residual_to_error.get("blocking_obligation_count"),
            "formula_row_ad_jacobian_probe_count": formula_jacobian.get("probe_count"),
            "formula_row_ad_jacobian_max_mismatch": theorem_contract.get("formula_row_ad_jacobian_max_mismatch"),
            "smooth_projected_position_order": numerical_orders.get("position_error_fit"),
            "smooth_projected_velocity_order": numerical_orders.get("velocity_error_fit"),
            "endpoint_raw_position_constraint_fit": endpoint_orders.get("raw_endpoint_position_constraint_fit"),
            "endpoint_raw_velocity_constraint_fit": endpoint_orders.get("raw_endpoint_velocity_constraint_fit"),
            "smooth_reference_eta_over_h7": theorem_contract.get("smooth_reference_eta_over_reference_h7"),
        },
        "closure_state": {
            "proof_gap_closed": pc2_direct_route_satisfied,
            "direct_pc2_proof_gap_closed": pc2_direct_route_satisfied,
            "proof_gap_closed_scope": "direct_residual_bridge_kantorovich_route_closed_primitive_taylor_conditional_schema_open",
            "dynamic_symbolic_oracle_complete": theorem_contract.get("dynamic_symbolic_oracle_complete"),
            "stage_residual_O_h7_implementation_defect_proved": pc2_direct_route_satisfied,
            "pc2_closed_by_direct_substitution": pc2_direct_route_satisfied,
            "primitive_lift_route_closed": False,
            "eta_h_O_h7_solver_policy_evidence": theorem_contract.get("eta_h_O_h7_solver_policy_evidence"),
            "fixed_tolerance_runs_are_asymptotic_proof": theorem_contract.get(
                "fixed_tolerance_runs_are_asymptotic_proof"
            ),
            "accepted_residual_to_error_theorem": residual_to_error.get("accepted_residual_to_error_theorem"),
            "full_tfe_stage_replacement": theorem_contract.get("full_tfe_stage_replacement"),
            "submission_ready": False,
        },
        "readiness_boundary": {
            "narrowed_claim_b4_b6_b7_statuses": blocker_statuses(blocker_gate, ["B4", "B6", "B7"]),
            "proof_closure_manifest_scope": "direct_pc2_closure_and_theorem_condition_traceability",
            "global_submission_boundaries_retained": [
                "full_source_policy_package_ready",
                "theorem_level_eta_h_solver_policy_evidence",
                "closed_residual_to_error_theorem_for_mechanism_rows",
            ],
        },
        "remaining_gate_scope": {
            "narrowed_claim_b4_b6_b7_statuses": blocker_statuses(blocker_gate, ["B4", "B6", "B7"]),
            "b4_b6_b7_closed_elsewhere_under_narrowed_claim": (
                blocker_statuses(blocker_gate, ["B4", "B6", "B7"])
                == {"B4": "closed", "B6": "closed", "B7": "closed"}
            ),
            "direct_pc2_proof_gap_closed": pc2_direct_route_satisfied,
            "direct_residual_bridge_route_satisfied": pc2_direct_route_satisfied,
            "primitive_route_closed": False,
            "eta_h_O_h7_solver_policy_evidence": solver_boundary.get("eta_h_O_h7_solver_policy_evidence"),
            "eta_h_theorem_condition_retained": solver_condition_retained,
            "accepted_residual_to_error_theorem": residual_to_error.get("accepted_residual_to_error_theorem"),
            "residual_to_error_blocking_obligations": residual_to_error.get("blocking_obligation_count"),
            "residual_to_error_route_promoted": not residual_promotion_not_made,
            "active_direct_newton_euler_open_obligations": (
                0 if pc2_direct_route_satisfied else newton_closure.get("open_obligation_count")
            ),
            "symbolic_primitive_route_open_obligations": newton_closure.get("open_obligation_count"),
            "global_submission_boundaries_retained": [
                "full_source_policy_package_ready",
                "theorem_level_eta_h_solver_policy_evidence",
                "closed_residual_to_error_theorem_for_mechanism_rows",
            ],
        },
        "direct_residual_bridge_kantorovich_submission_standard": {
            "status": "closed_by_direct_residual_bridge_kantorovich_route_primitive_taylor_conditional_schema_open",
            "required_pc2_route": "direct_residual_bridge_kantorovich_route",
            "satisfied": pc2_direct_route_satisfied,
            "proof_gap_closed_under_active_direct_residual_bridge_standard": pc2_direct_route_satisfied,
            "not_primitive_162_term_taylor_closure": True,
            "direct_substitution_supplies_active_pc2_residual_bridge": pc2_direct_route_satisfied,
            "direct_substitution_role": (
                "row-local residual evidence used as the residual input to the direct "
                "residual-bridge/Kantorovich perturbation route; the primitive 162-subterm "
                "Taylor route is retained as a separate primitive-route specification "
                "and is not required for B3 closure"
            ),
            "direct_residual_bridge_kantorovich_route_closed": pc2_direct_route_satisfied,
            "theorem_invocation_consumes_one_residual_value_certificate": True,
            "future_primitive_taylor_certificate_replacement_only": True,
            "future_primitive_taylor_requires_same_tuple_132_row_bound": True,
            "future_primitive_taylor_may_not_append_lower_remove_or_promote": True,
            "primitive_route_required_for_b3_closure": False,
            "primitive_taylor_route_closed": False,
            "primitive_taylor_schema_role": (
                "conditional Newton-Euler primitive Taylor certificate schema; "
                "non-load-bearing under the active direct PC2 residual-bridge route"
            ),
            "primitive_taylor_schema_current_instance_available": False,
            "primitive_taylor_schema_blocker_summary": (
                "0/162 Taylor bounds certified; five primitive lift/bilinear "
                "antecedents remain open"
            ),
            "actual_taylor_bounds_proved": d5_conditional_taylor_summary.get("actual_taylor_bounds_proved"),
            "certified_taylor_bound_terms": d5_term_budget_summary.get("certified_taylor_bound_terms"),
            "open_taylor_bound_terms": d5_term_budget_summary.get("open_taylor_bound_terms"),
            "strict_taylor_reduction_terms": d5_term_budget_summary.get("strict_taylor_reduction_terms"),
            "terms_with_open_primitive_blockers": d5_term_budget_summary.get(
                "terms_with_open_primitive_blockers"
            ),
            "open_primitive_assumption_count": d5_conditional_taylor_summary.get(
                "open_primitive_assumption_count"
            ),
            "open_primitive_count": d5_open_primitive_summary.get("open_primitive_count"),
            "primitive_obligations_proved": d5_primitive_reduction_summary.get(
                "primitive_obligations_proved"
            ),
            "primitive_obligation_count": d5_primitive_reduction_summary.get("primitive_obligation_count"),
            "h_weighted_acceleration_sufficient_terms": d5_term_budget_summary.get(
                "h_weighted_acceleration_sufficient_terms"
            ),
            "h_weighted_acceleration_insufficient_terms": d5_term_budget_summary.get(
                "h_weighted_acceleration_insufficient_terms"
            ),
            "minimum_required_next_route": (
                "for the separate primitive conditional-schema route, prove the five open "
                "primitive lift/bilinear obligations, including an unweighted O(h^7) "
                "acceleration lift, before certifying the 162 D5 Taylor subterms"
            ),
        },
        "oracle_state": {
            "runtime_formula_row_oracle_complete": implementation_boundary.get("runtime_formula_row_oracle_complete"),
            "runtime_ad_oracle_complete": implementation_boundary.get("runtime_ad_oracle_complete"),
            "independent_symbolic_row_oracle_complete": implementation_boundary.get(
                "independent_symbolic_row_oracle_complete"
            ),
            "newton_euler_formula_oracle_complete": theorem_contract.get("newton_euler_formula_oracle_complete"),
            "newton_euler_symbolic_target_inventory_complete": newton_euler_targets.get(
                "closure_boundary", {}
            ).get("symbolic_target_inventory_complete"),
            "newton_euler_obligation_coverage_matrix_complete": newton_target_coverage.get(
                "coverage_matrix_complete"
            ),
            "newton_euler_runtime_expression_structure_checked": newton_certificate_summary.get(
                "runtime_expression_structure_checked"
            ),
            "newton_euler_runtime_template_instantiation_checked": newton_certificate_summary.get(
                "runtime_template_instantiation_checked"
            ),
            "newton_euler_template_algebraic_equivalence_checked": newton_certificate_summary.get(
                "template_algebraic_equivalence_checked"
            ),
            "newton_euler_c2_template_algebraic_equivalence_closed": newton_certificate_summary.get(
                "c2_template_algebraic_equivalence_closed"
            ),
            "newton_euler_virtual_work_wrench_sign_skeleton_checked": newton_certificate_summary.get(
                "virtual_work_wrench_sign_skeleton_checked"
            ),
            "newton_euler_virtual_work_template_identity_proved": newton_certificate_summary.get(
                "virtual_work_template_identity_proved"
            ),
            "newton_euler_multiplier_wrench_consistency_closed": newton_certificate_summary.get(
                "multiplier_wrench_consistency_closed"
            ),
            "newton_euler_row_expanded_virtual_work_identity_proved": newton_certificate_summary.get(
                "row_expanded_virtual_work_identity_proved"
            ),
            "newton_euler_balance_identity_closed": newton_certificate_summary.get("balance_identity_closed"),
        },
        "solver_state": {
            "per_step_newton_tolerance_policy": theorem_contract.get("per_step_newton_tolerance_policy"),
            "same_reduced_chart_initial_state_required": theorem_contract.get(
                "same_reduced_chart_initial_state_required"
            ),
            "branch_selected_newton_solves_required": theorem_contract.get(
                "branch_selected_newton_solves_required"
            ),
            "newton_iterates_initialized_from_gauss_predictor_required": theorem_contract.get(
                "newton_iterates_initialized_from_gauss_predictor_required"
            ),
            "arbitrary_newton_initializations_select_branch": theorem_contract.get(
                "arbitrary_newton_initializations_select_branch"
            ),
            "remote_nonlinear_roots_select_branch": theorem_contract.get(
                "remote_nonlinear_roots_select_branch"
            ),
            "local_defect_constants_uniform_on_compact_proof_tube": theorem_contract.get(
                "local_defect_constants_uniform_on_compact_proof_tube"
            ),
            "local_defect_constants_uniform_over_accepted_steps": theorem_contract.get(
                "local_defect_constants_uniform_over_accepted_steps"
            ),
            "newton_error_controlled_by_single_accepted_branch_eta_h_max": theorem_contract.get(
                "newton_error_controlled_by_single_accepted_branch_eta_h_max"
            ),
            "newton_error_controlled_by_compact_tube_eta_h_envelope": theorem_contract.get(
                "newton_error_controlled_by_compact_tube_eta_h_envelope"
            ),
            "newton_residual_to_stage_bound_has_explicit_constant": theorem_contract.get(
                "newton_residual_to_stage_bound_has_explicit_constant"
            ),
            "newton_endpoint_output_map": theorem_contract.get("newton_endpoint_output_map"),
            "newton_endpoint_output_map_bound": theorem_contract.get("newton_endpoint_output_map_bound"),
            "newton_endpoint_output_map_derivative_bound_includes_closure": theorem_contract.get(
                "newton_endpoint_output_map_derivative_bound_includes_closure"
            ),
            "newton_endpoint_output_map_lipschitz_constant_symbol": theorem_contract.get(
                "newton_endpoint_output_map_lipschitz_constant_symbol"
            ),
            "newton_residual_to_endpoint_perturbation_constant_formula": theorem_contract.get(
                "newton_residual_to_endpoint_perturbation_constant_formula"
            ),
            "newton_eta_h_scaled_endpoint_bound_has_explicit_constant": theorem_contract.get(
                "newton_eta_h_scaled_endpoint_bound_has_explicit_constant"
            ),
            "newton_eta_h_scaled_endpoint_bound_formula": theorem_contract.get(
                "newton_eta_h_scaled_endpoint_bound_formula"
            ),
            "local_defect_bound_has_explicit_uniform_constant_sum": theorem_contract.get(
                "local_defect_bound_has_explicit_uniform_constant_sum"
            ),
            "gauss_truncation_bound_has_explicit_uniform_constant": theorem_contract.get(
                "gauss_truncation_bound_has_explicit_uniform_constant"
            ),
            "gauss_truncation_constant_uniform_on_compact_trajectory_tube": theorem_contract.get(
                "gauss_truncation_constant_uniform_on_compact_trajectory_tube"
            ),
            "stage_residual_to_root_bound_has_explicit_constant": theorem_contract.get(
                "stage_residual_to_root_bound_has_explicit_constant"
            ),
            "stage_residual_to_root_constant_formula": theorem_contract.get(
                "stage_residual_to_root_constant_formula"
            ),
            "stage_root_endpoint_perturbation_constant_formula": theorem_contract.get(
                "stage_root_endpoint_perturbation_constant_formula"
            ),
            "accepted_root_existence_proved_by_stage_residual_lemma": theorem_contract.get(
                "accepted_root_existence_proved_by_stage_residual_lemma"
            ),
            "accepted_root_existence_not_assumed_as_isolated_root_premise": theorem_contract.get(
                "accepted_root_existence_not_assumed_as_isolated_root_premise"
            ),
            "endpoint_closure_raw_defect_bound_has_explicit_constant": theorem_contract.get(
                "endpoint_closure_raw_defect_bound_has_explicit_constant"
            ),
            "endpoint_closure_raw_defect_constant_symbol": theorem_contract.get(
                "endpoint_closure_raw_defect_constant_symbol"
            ),
            "endpoint_closure_perturbation_bound_has_explicit_constant": theorem_contract.get(
                "endpoint_closure_perturbation_bound_has_explicit_constant"
            ),
            "endpoint_closure_perturbation_constant_formula": theorem_contract.get(
                "endpoint_closure_perturbation_constant_formula"
            ),
            "eta_h_constant_absorbed_into_local_defect_constant": theorem_contract.get(
                "eta_h_constant_absorbed_into_local_defect_constant"
            ),
            "local_global_transfer_has_explicit_reduced_grid_constant": theorem_contract.get(
                "local_global_transfer_has_explicit_reduced_grid_constant"
            ),
            "local_global_gronwall_factor_formula": theorem_contract.get(
                "local_global_gronwall_factor_formula"
            ),
            "local_global_reduced_grid_constant_formula": theorem_contract.get(
                "local_global_reduced_grid_constant_formula"
            ),
            "qv_reporting_map_constant_distinct_from_residual_defect_constant": theorem_contract.get(
                "qv_reporting_map_constant_distinct_from_residual_defect_constant"
            ),
            "qv_reporting_constant_formula": theorem_contract.get(
                "qv_reporting_constant_formula"
            ),
            "local_global_transfer_grid_point_error_required": theorem_contract.get(
                "local_global_transfer_grid_point_error_required"
            ),
            "reported_time_grid_defined_by_tn_equals_nh": theorem_contract.get(
                "reported_time_grid_defined_by_tn_equals_nh"
            ),
            "exact_final_time_divisibility_required": theorem_contract.get(
                "exact_final_time_divisibility_required"
            ),
            "reported_qv_error_bound_uses_same_reported_time_grid": theorem_contract.get(
                "reported_qv_error_bound_uses_same_reported_time_grid"
            ),
            "reported_qv_error_bound_is_grid_maximum": theorem_contract.get(
                "reported_qv_error_bound_is_grid_maximum"
            ),
            "summary_level_solver_residuals_recorded": solver_boundary.get("summary_level_solver_residuals_recorded"),
            "finite_scaled_tolerance_probe_recorded": solver_boundary.get("finite_scaled_tolerance_probe_recorded"),
            "finite_scaled_tolerance_probe_ok_rows": finite_solver_probe.get("ok_row_count"),
            "finite_scaled_tolerance_probe_total_rows": finite_solver_probe.get("row_count"),
            "finite_scaled_tolerance_probe_max_residual_over_h7": finite_solver_probe.get(
                "max_final_residual_over_h7"
            ),
            "finite_scaled_tolerance_trajectory_probe_recorded": solver_boundary.get(
                "finite_scaled_tolerance_trajectory_probe_recorded"
            ),
            "finite_scaled_tolerance_trajectory_probe_ok_rows": finite_solver_trajectory_probe.get("ok_row_count"),
            "finite_scaled_tolerance_trajectory_probe_total_rows": finite_solver_trajectory_probe.get("row_count"),
            "finite_scaled_tolerance_trajectory_probe_total_steps_checked": finite_solver_trajectory_probe.get(
                "total_steps_checked"
            ),
            "finite_scaled_tolerance_trajectory_probe_max_residual_over_h7": finite_solver_trajectory_probe.get(
                "max_final_residual_over_h7"
            ),
            "finite_tolerance_regime_sweep_recorded": solver_boundary.get(
                "finite_tolerance_regime_sweep_recorded"
            ),
            "finite_h_scaled_tolerance_sweep_recorded": solver_boundary.get(
                "finite_h_scaled_tolerance_sweep_recorded"
            ),
            "finite_h_scaled_tolerance_sweep_policy_names": finite_tolerance_regime_sweep.get(
                "finite_h_scaled_policy_names"
            ),
            "finite_h_scaled_tolerance_sweep_rows": finite_tolerance_regime_sweep.get(
                "finite_h_scaled_policy_rows"
            ),
            "finite_h_scaled_tolerance_sweep_steps": finite_tolerance_regime_sweep.get(
                "finite_h_scaled_policy_steps"
            ),
            "finite_h_scaled_tolerance_sweep_velocity_order_floor": finite_tolerance_regime_sweep.get(
                "finite_h_scaled_velocity_order_floor"
            ),
            "finite_tolerance_regime_sweep_policy_count": finite_tolerance_regime_sweep.get("policy_count"),
            "finite_tolerance_regime_sweep_total_rows": finite_tolerance_regime_sweep.get("total_rows_checked"),
            "finite_tolerance_regime_sweep_total_steps": finite_tolerance_regime_sweep.get("total_steps_checked"),
            "finite_tolerance_regime_sweep_fixed_position_velocity_orders": finite_tolerance_regime_sweep.get(
                "fixed_1e_10_position_velocity_orders"
            ),
            "finite_tolerance_regime_sweep_h7_position_velocity_orders": finite_tolerance_regime_sweep.get(
                "scaled_h7_position_velocity_orders"
            ),
            "finite_tolerance_regime_sweep_h8_position_velocity_orders": finite_tolerance_regime_sweep.get(
                "scaled_h8_position_velocity_orders"
            ),
            "scaled_tolerance_sweep_recorded": solver_boundary.get("scaled_tolerance_sweep_recorded"),
            "eta_h_O_h7_solver_policy_evidence": solver_boundary.get("eta_h_O_h7_solver_policy_evidence"),
        },
        "theorem_statement_boundary": {
            "main_tex": "main_cmame.tex",
            "flat_tex": "cmame_submission_flat/main_cmame_submission.tex",
            "accepted_theorem_label": "thm:g6fullva-order",
            "labels_present_main": main_label_presence,
            "labels_present_flat": flat_label_presence,
            "all_required_labels_present_main_and_flat": manuscript_labels_present,
            "manuscript_anchor_label_count": source_manuscript_anchor_map["label_anchor_count"],
            "manuscript_anchor_map_present": source_manuscript_anchor_map["all_label_anchors_present"],
            "theorem_assumption_anchor_count": source_manuscript_anchor_map[
                "theorem_assumption_anchor_count"
            ],
            "theorem_assumption_anchor_map_present": source_manuscript_anchor_map[
                "all_theorem_assumption_anchors_present"
            ],
            "theorem_anchor_table_reference_coverage_present": (
                source_theorem_anchor_table_coverage["all_references_present_main_and_flat"]
            ),
            "theorem_boundary_tokens_main": main_theorem_boundary,
            "theorem_boundary_tokens_flat": flat_theorem_boundary,
            "conditional_theorem_boundary_present_main_and_flat": theorem_boundary_present,
            "theorem_reading_guide_tokens_main": main_theorem_reading_guide,
            "theorem_reading_guide_tokens_flat": flat_theorem_reading_guide,
            "theorem_reading_guide_present_main_and_flat": theorem_reading_guide_present,
            "accepted_method_order": 6,
            "accepted_local_defect_order": 7,
            "eta_h_theorem_condition_retained": solver_condition_retained,
            "eta_h_solver_policy_evidence_closed": solver_boundary.get("eta_h_O_h7_solver_policy_evidence"),
            "fixed_tolerance_runs_are_asymptotic_proof": theorem_contract.get(
                "fixed_tolerance_runs_are_asymptotic_proof"
            ),
            "does_not_promote_residual_to_error": residual_promotion_not_made,
            "does_not_promote_source_policy_or_full_tfe": True,
        },
        "manuscript_traceability": {
            "main_tex": "main_cmame.tex",
            "flat_tex": "cmame_submission_flat/main_cmame_submission.tex",
            "proof_traceability_tokens_main": main_proof_traceability,
            "proof_traceability_tokens_flat": flat_proof_traceability,
            "proof_dependency_graph_present_main_and_flat": (
                main_proof_traceability["reader_facing_dependency_graph"]
                and flat_proof_traceability["reader_facing_dependency_graph"]
            ),
            "proof_traceability_table_present_main_and_flat": (
                main_label_presence["proof_traceability_table"]
                and flat_label_presence["proof_traceability_table"]
            ),
            "dynamic_proof_closure_matrix_present_main_and_flat": (
                main_label_presence["dynamic_proof_closure_matrix"]
                and flat_label_presence["dynamic_proof_closure_matrix"]
            ),
            "residual_to_error_nonpromotion_present_main_and_flat": (
                main_proof_traceability["residual_to_error_nonpromotion"]
                and flat_proof_traceability["residual_to_error_nonpromotion"]
            ),
            "primitive_lane_boundary_present_main_and_flat": (
                main_proof_traceability["primitive_lane_not_pc2_input"]
                and flat_proof_traceability["primitive_lane_not_pc2_input"]
            ),
            "conditional_proof_claims_mapped_to_manuscript": (
                manuscript_labels_present
                and theorem_boundary_present
                and proof_traceability_present
                and theorem_use_rule_present
                and constant_dependency_table_present
                and theorem_dependency_consumption_table_present
                and theorem_output_scope_table_present
                and quantifier_domain_table_present
                and local_global_transfer_table_present
                and reporting_map_table_present
                and proof_causality_table_present
                and branch_consistency_table_present
                and local_defect_decomposition_table_present
                and direct_route_anticircularity_table_present
                and implementation_route_oracle_table_present
                and b1_ad_expanded_closure_table_present
                and p1p2_compact_tube_boundary_present
                and p3p4_implementation_boundary_present
                and p5_direct_route_boundary_present
                and p6_solver_scope_boundary_present
                and nonlinear_solver_scale_table_present
                and p_interface_satisfaction_table_present
                and p7_residual_to_error_obligation_table_present
                and source_theorem_anchor_table_coverage["all_references_present_main_and_flat"]
                and pc2_direct_route_satisfied
                and solver_condition_retained
                and residual_promotion_not_made
            ),
            "theorem_use_rule_present_main_and_flat": theorem_use_rule_present,
            "constant_dependency_table_present_main_and_flat": constant_dependency_table_present,
            "theorem_dependency_consumption_table_present_main_and_flat": (
                theorem_dependency_consumption_table_present
            ),
            "theorem_output_scope_table_present_main_and_flat": theorem_output_scope_table_present,
            "quantifier_domain_table_present_main_and_flat": quantifier_domain_table_present,
            "local_global_transfer_table_present_main_and_flat": (
                local_global_transfer_table_present
            ),
            "reporting_map_table_present_main_and_flat": reporting_map_table_present,
            "proof_causality_table_present_main_and_flat": proof_causality_table_present,
            "branch_consistency_table_present_main_and_flat": branch_consistency_table_present,
            "local_defect_decomposition_table_present_main_and_flat": (
                local_defect_decomposition_table_present
            ),
            "direct_route_anticircularity_table_present_main_and_flat": (
                direct_route_anticircularity_table_present
            ),
            "implementation_route_oracle_table_present_main_and_flat": (
                implementation_route_oracle_table_present
            ),
            "b1_ad_expanded_closure_table_present_main_and_flat": (
                b1_ad_expanded_closure_table_present
            ),
            "p1p2_compact_tube_boundary_present_main_and_flat": (
                p1p2_compact_tube_boundary_present
            ),
            "p3p4_implementation_boundary_present_main_and_flat": (
                p3p4_implementation_boundary_present
            ),
            "p5_direct_route_boundary_present_main_and_flat": (
                p5_direct_route_boundary_present
            ),
            "p6_solver_scope_boundary_present_main_and_flat": (
                p6_solver_scope_boundary_present
            ),
            "nonlinear_solver_scale_table_present_main_and_flat": (
                nonlinear_solver_scale_table_present
            ),
            "p_interface_satisfaction_table_present_main_and_flat": (
                p_interface_satisfaction_table_present
            ),
            "p7_residual_to_error_obligation_table_present_main_and_flat": (
                p7_residual_to_error_obligation_table_present
            ),
            "manuscript_anchor_map_present": source_manuscript_anchor_map["all_label_anchors_present"],
            "theorem_assumption_anchor_map_present": source_manuscript_anchor_map[
                "all_theorem_assumption_anchors_present"
            ],
            "theorem_assumption_anchor_ids": source_manuscript_anchor_map[
                "theorem_assumption_anchor_ids"
            ],
            "theorem_anchor_table_reference_coverage_present": (
                source_theorem_anchor_table_coverage["all_references_present_main_and_flat"]
            ),
            "does_not_change_proof_closure_state": True,
        },
        "manuscript_anchor_map": source_manuscript_anchor_map,
        "theorem_anchor_table_reference_coverage": source_theorem_anchor_table_coverage,
        "theorem_use_rule_boundary": {
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
            "all_tokens_present_main_and_flat": theorem_use_rule_present,
        },
        "constant_dependency_table_boundary": {
            "tokens": CONSTANT_DEPENDENCY_LEDGER_TOKENS,
            "checks": {
                "main_tex": main_constant_dependency_table,
                "flat_tex": flat_constant_dependency_table,
            },
            "all_tokens_present_main_and_flat": constant_dependency_table_present,
        },
        "theorem_dependency_consumption_table_boundary": {
            "tokens": THEOREM_DEPENDENCY_CONSUMPTION_LEDGER_TOKENS,
            "checks": {
                "main_tex": main_theorem_dependency_consumption_table,
                "flat_tex": flat_theorem_dependency_consumption_table,
            },
            "all_tokens_present_main_and_flat": theorem_dependency_consumption_table_present,
        },
        "theorem_output_scope_table_boundary": {
            "tokens": THEOREM_OUTPUT_SCOPE_LEDGER_TOKENS,
            "checks": {
                "main_tex": main_theorem_output_scope_table,
                "flat_tex": flat_theorem_output_scope_table,
            },
            "all_tokens_present_main_and_flat": theorem_output_scope_table_present,
        },
        "quantifier_domain_table_boundary": {
            "tokens": QUANTIFIER_DOMAIN_LEDGER_TOKENS,
            "checks": {
                "main_tex": main_quantifier_domain_table,
                "flat_tex": flat_quantifier_domain_table,
            },
            "all_tokens_present_main_and_flat": quantifier_domain_table_present,
        },
        "local_global_transfer_table_boundary": {
            "tokens": LOCAL_GLOBAL_TRANSFER_LEDGER_TOKENS,
            "checks": {
                "main_tex": main_local_global_transfer_table,
                "flat_tex": flat_local_global_transfer_table,
            },
            "all_tokens_present_main_and_flat": local_global_transfer_table_present,
        },
        "reporting_map_table_boundary": {
            "tokens": REPORTING_MAP_LEDGER_TOKENS,
            "checks": {
                "main_tex": main_reporting_map_table,
                "flat_tex": flat_reporting_map_table,
            },
            "all_tokens_present_main_and_flat": reporting_map_table_present,
        },
        "proof_causality_table_boundary": {
            "tokens": PROOF_CAUSALITY_LEDGER_TOKENS,
            "checks": {
                "main_tex": main_proof_causality_table,
                "flat_tex": flat_proof_causality_table,
            },
            "all_tokens_present_main_and_flat": proof_causality_table_present,
        },
        "branch_consistency_table_boundary": {
            "tokens": BRANCH_CONSISTENCY_LEDGER_TOKENS,
            "checks": {
                "main_tex": main_branch_consistency_table,
                "flat_tex": flat_branch_consistency_table,
            },
            "all_tokens_present_main_and_flat": branch_consistency_table_present,
        },
        "local_defect_decomposition_table_boundary": {
            "tokens": LOCAL_DEFECT_DECOMPOSITION_LEDGER_TOKENS,
            "checks": {
                "main_tex": main_local_defect_decomposition_table,
                "flat_tex": flat_local_defect_decomposition_table,
            },
            "all_tokens_present_main_and_flat": local_defect_decomposition_table_present,
        },
        "direct_route_anticircularity_table_boundary": {
            "tokens": DIRECT_ROUTE_ANTICIRCULARITY_LEDGER_TOKENS,
            "checks": {
                "main_tex": main_direct_route_anticircularity_table,
                "flat_tex": flat_direct_route_anticircularity_table,
            },
            "all_tokens_present_main_and_flat": direct_route_anticircularity_table_present,
        },
        "implementation_route_oracle_table_boundary": {
            "tokens": IMPLEMENTATION_ROUTE_ORACLE_LEDGER_TOKENS,
            "checks": {
                "main_tex": main_implementation_route_oracle_table,
                "flat_tex": flat_implementation_route_oracle_table,
            },
            "all_tokens_present_main_and_flat": implementation_route_oracle_table_present,
        },
        "b1_ad_expanded_closure_table_boundary": {
            "tokens": B1_AD_EXPANDED_CLOSURE_LEDGER_TOKENS,
            "checks": {
                "main_tex": main_b1_ad_expanded_closure_table,
                "flat_tex": flat_b1_ad_expanded_closure_table,
            },
            "all_tokens_present_main_and_flat": b1_ad_expanded_closure_table_present,
        },
        "p1p2_compact_tube_boundary": {
            "tokens": P1P2_COMPACT_TUBE_BOUNDARY_TOKENS,
            "checks": {
                "main_tex": main_p1p2_compact_tube_boundary,
                "flat_tex": flat_p1p2_compact_tube_boundary,
            },
            "all_tokens_present_main_and_flat": p1p2_compact_tube_boundary_present,
        },
        "p3p4_implementation_boundary": {
            "tokens": P3P4_IMPLEMENTATION_BOUNDARY_TOKENS,
            "checks": {
                "main_tex": main_p3p4_implementation_boundary,
                "flat_tex": flat_p3p4_implementation_boundary,
            },
            "all_tokens_present_main_and_flat": p3p4_implementation_boundary_present,
        },
        "p5_direct_route_boundary": {
            "tokens": P5_DIRECT_ROUTE_BOUNDARY_TOKENS,
            "checks": {
                "main_tex": main_p5_direct_route_boundary,
                "flat_tex": flat_p5_direct_route_boundary,
            },
            "all_tokens_present_main_and_flat": p5_direct_route_boundary_present,
        },
        "p6_solver_scope_boundary": {
            "tokens": P6_SOLVER_SCOPE_BOUNDARY_TOKENS,
            "checks": {
                "main_tex": main_p6_solver_scope_boundary,
                "flat_tex": flat_p6_solver_scope_boundary,
            },
            "all_tokens_present_main_and_flat": p6_solver_scope_boundary_present,
        },
        "nonlinear_solver_scale_table_boundary": {
            "tokens": NONLINEAR_SOLVER_SCALE_LEDGER_TOKENS,
            "checks": {
                "main_tex": main_nonlinear_solver_scale_table,
                "flat_tex": flat_nonlinear_solver_scale_table,
            },
            "all_tokens_present_main_and_flat": nonlinear_solver_scale_table_present,
        },
        "p_interface_satisfaction_table_boundary": {
            "tokens": P_INTERFACE_SATISFACTION_LEDGER_TOKENS,
            "checks": {
                "main_tex": main_p_interface_satisfaction_table,
                "flat_tex": flat_p_interface_satisfaction_table,
            },
            "all_tokens_present_main_and_flat": p_interface_satisfaction_table_present,
        },
        "p7_residual_to_error_obligation_table_boundary": {
            "tokens": P7_RESIDUAL_TO_ERROR_OBLIGATION_LEDGER_TOKENS,
            "checks": {
                "main_tex": main_p7_residual_to_error_obligation_table,
                "flat_tex": flat_p7_residual_to_error_obligation_table,
            },
            "all_tokens_present_main_and_flat": (
                p7_residual_to_error_obligation_table_present
            ),
        },
        "theorem_assumption_coverage": theorem_assumptions,
        "newton_euler_open_obligations": newton_euler.get("open_obligations", []),
        "newton_euler_symbolic_primitive_open_obligations": newton_euler.get("open_obligations", []),
        "newton_euler_closed_obligations": newton_euler.get("closed_obligations", []),
        "residual_to_error_required_next_artifacts": residual_to_error.get("required_next_artifacts", []),
        "residual_to_error_promotion_policy": {
            "accepted_residual_to_error_theorem": residual_to_error.get("accepted_residual_to_error_theorem"),
            "coverage_only_examples": order_gate.get("coverage_only_examples", []),
            "accepted_dynamic_order_examples": order_gate.get("accepted_dynamic_order_examples", []),
            "residual_promotion_not_made": residual_promotion_not_made,
        },
        "close_requirements": close_requirements,
        "claim_policy": {
            "allowed_now": [
                "conditional local-defect-to-global-error theorem for Gauss6/FullVA under stated assumptions",
                "finite-run numerical scale diagnostic as support, not proof closure",
                "formal order comparison against the expected fifth-order TFE target",
            ],
            "forbidden_now": [
                "unconditional proof closure",
                "separate primitive/global dynamic symbolic oracle complete",
                "primitive/Taylor-route PC2 closure",
                "separate primitive/global dynamic symbolic route complete",
                "fixed-tolerance runs prove eta_h^tube <= c_eta h^7",
                "accepted residual-to-error transfer theorem",
                "full TFE stage replacement",
                "unscoped/global proof-package submission-ready claim",
            ],
        },
        "source_files": {
            "proof_contract": "CMAME_PROOF_CONTRACT_GATE.json",
            "proof_style_audit": "CMAME_PROOF_STYLE_AUDIT.json",
            "dynamic_oracle": "DYNAMIC_ROW_ORACLE_GATE.json",
            "kinematic_row_defect_certificate": "KINEMATIC_ROW_DEFECT_CERTIFICATE.json",
            "newton_euler_defect_obligation_gate": "NEWTON_EULER_DEFECT_OBLIGATION_GATE.json",
            "newton_euler_symbolic_target_audit": "NEWTON_EULER_SYMBOLIC_TARGET_AUDIT.json",
            "newton_euler_virtual_work_wrench_audit": "NEWTON_EULER_VIRTUAL_WORK_WRENCH_AUDIT.json",
            "newton_euler_balance_identity_audit": "NEWTON_EULER_BALANCE_IDENTITY_AUDIT.json",
            "newton_euler_dynamic_row_closure_contract": "NEWTON_EULER_DYNAMIC_ROW_CLOSURE_CONTRACT.json",
            "b1_ad_expanded_symbolic_oracle_closure_certificate": "B1_AD_EXPANDED_SYMBOLIC_ORACLE_CLOSURE_CERTIFICATE.json",
            "d5_dynamic_defect_readiness_audit": "D5_DYNAMIC_DEFECT_READINESS_AUDIT.json",
            "d5_dynamic_direct_substitution_certificate": "D5_DYNAMIC_DIRECT_SUBSTITUTION_CERTIFICATE.json",
            "d5_taylor_term_budget_audit": "D5_TAYLOR_TERM_BUDGET_AUDIT.json",
            "d5_primitive_bound_reduction_audit": "D5_PRIMITIVE_BOUND_REDUCTION_AUDIT.json",
            "d5_p_tube_constants_audit": "D5_P_TUBE_CONSTANTS_AUDIT.json",
            "d5_p_state_lift_gap_audit": "D5_P_STATE_LIFT_GAP_AUDIT.json",
            "d5_p_state_map_definition_audit": "D5_P_STATE_MAP_DEFINITION_AUDIT.json",
            "d5_p_state_anticircularity_audit": "D5_P_STATE_ANTICIRCULARITY_AUDIT.json",
            "d5_p_state_ps2_weighted_target_audit": "D5_P_STATE_PS2_WEIGHTED_TARGET_AUDIT.json",
            "d5_p_state_ps2_kinematic_block_certificate": "D5_P_STATE_PS2_KINEMATIC_BLOCK_CERTIFICATE.json",
            "d5_p_state_ps2_lie_chart_binding_audit": "D5_P_STATE_PS2_LIE_CHART_BINDING_AUDIT.json",
            "d5_p_state_ps2_row_injection_audit": "D5_P_STATE_PS2_ROW_INJECTION_AUDIT.json",
            "d5_p_state_ps2_nonlinear_binding_audit": "D5_P_STATE_PS2_NONLINEAR_BINDING_AUDIT.json",
            "d5_p_state_ps2_aggregate_promotion_audit": "D5_P_STATE_PS2_AGGREGATE_PROMOTION_AUDIT.json",
            "d5_p_state_ps2_linearization_probe": "D5_P_STATE_PS2_LINEARIZATION_PROBE.json",
            "d5_p_state_ps3_conditional_conversion_audit": "D5_P_STATE_PS3_CONDITIONAL_CONVERSION_AUDIT.json",
            "d5_p_state_ps3_actual_instantiation_gap_audit": "D5_P_STATE_PS3_ACTUAL_INSTANTIATION_GAP_AUDIT.json",
            "d5_p_state_ps3_h_acc_input_obstruction_audit": "D5_P_STATE_PS3_H_ACC_INPUT_OBSTRUCTION_AUDIT.json",
            "d5_p_acc_map_definition_audit": "D5_P_ACC_MAP_DEFINITION_AUDIT.json",
            "d5_p_acc_row_binding_audit": "D5_P_ACC_ROW_BINDING_AUDIT.json",
            "d5_p_acc_independence_audit": "D5_P_ACC_INDEPENDENCE_AUDIT.json",
            "d5_p_acc_lift_obstruction_audit": "D5_P_ACC_LIFT_OBSTRUCTION_AUDIT.json",
            "d5_p_acc_pa2_weighted_inverse_audit": "D5_P_ACC_PA2_WEIGHTED_INVERSE_AUDIT.json",
            "d5_p_lambda_interface_audit": "D5_P_LAMBDA_INTERFACE_AUDIT.json",
            "d5_p_lambda_pl2_geometric_margin_audit": "D5_P_LAMBDA_PL2_GEOMETRIC_MARGIN_AUDIT.json",
            "d5_p_lambda_d3_noncircularity_audit": "D5_P_LAMBDA_D3_NONCIRCULARITY_AUDIT.json",
            "d5_p_lambda_pl4_rate_propagation_audit": "D5_P_LAMBDA_PL4_RATE_PROPAGATION_AUDIT.json",
            "d5_p_geom_chart_reduction_audit": "D5_P_GEOM_CHART_REDUCTION_AUDIT.json",
            "d5_p_gyro_bilinear_reduction_audit": "D5_P_GYRO_BILINEAR_REDUCTION_AUDIT.json",
            "d5_primitive_obligation_closure_plan": "D5_PRIMITIVE_OBLIGATION_CLOSURE_PLAN.json",
            "d5_conditional_taylor_certificate": "D5_CONDITIONAL_TAYLOR_CERTIFICATE.json",
            "d5_open_primitive_gap_audit": "D5_OPEN_PRIMITIVE_GAP_AUDIT.json",
            "proof_numerical_scale_audit": "PROOF_NUMERICAL_SCALE_AUDIT.json",
            "proof_solver_scale_audit": "PROOF_SOLVER_SCALE_AUDIT.json",
            "implementation_path_audit": "IMPLEMENTATION_PATH_AUDIT.json",
            "blocker_gate": "CMAME_BLOCKER_CLOSURE_GATE.json",
            "residual_to_error_obligations": "../v048_cross_paper_same_test_benchmarks/results/closed_loop_residual_to_error_theorem_obligations.json",
            "main_tex": "main_cmame.tex",
            "flat_tex": "cmame_submission_flat/main_cmame_submission.tex",
        },
    }
    result.update(
        {
            "constant_dependency_ledger_boundary": result[
                "constant_dependency_table_boundary"
            ],
            "theorem_dependency_consumption_ledger_boundary": result[
                "theorem_dependency_consumption_table_boundary"
            ],
            "theorem_output_scope_ledger_boundary": result[
                "theorem_output_scope_table_boundary"
            ],
            "quantifier_domain_ledger_boundary": result["quantifier_domain_table_boundary"],
            "local_global_transfer_ledger_boundary": result[
                "local_global_transfer_table_boundary"
            ],
            "reporting_map_ledger_boundary": result["reporting_map_table_boundary"],
            "proof_causality_ledger_boundary": result["proof_causality_table_boundary"],
            "branch_consistency_ledger_boundary": result["branch_consistency_table_boundary"],
            "local_defect_decomposition_ledger_boundary": result[
                "local_defect_decomposition_table_boundary"
            ],
            "direct_route_anticircularity_ledger_boundary": result[
                "direct_route_anticircularity_table_boundary"
            ],
            "implementation_route_oracle_ledger_boundary": result[
                "implementation_route_oracle_table_boundary"
            ],
            "b1_ad_expanded_closure_ledger_boundary": result[
                "b1_ad_expanded_closure_table_boundary"
            ],
            "nonlinear_solver_scale_ledger_boundary": result[
                "nonlinear_solver_scale_table_boundary"
            ],
            "p_interface_satisfaction_ledger_boundary": result[
                "p_interface_satisfaction_table_boundary"
            ],
            "p7_residual_to_error_obligation_ledger_boundary": result[
                "p7_residual_to_error_obligation_table_boundary"
            ],
        }
    )

    strict_standard = result["direct_residual_bridge_kantorovich_submission_standard"]
    strict_standard["active_standard_name"] = "strict_direct_residual_bridge_submission_standard"
    result["strict_direct_residual_bridge_submission_standard"] = {
        "status": strict_standard["status"],
        "required_pc2_route": strict_standard["required_pc2_route"],
        "satisfied": strict_standard["satisfied"],
        "proof_gap_closed_under_active_direct_residual_bridge_standard": strict_standard[
            "proof_gap_closed_under_active_direct_residual_bridge_standard"
        ],
        "not_primitive_162_term_taylor_closure": strict_standard[
            "not_primitive_162_term_taylor_closure"
        ],
        "direct_substitution_supplies_active_pc2_residual_bridge": strict_standard[
            "direct_substitution_supplies_active_pc2_residual_bridge"
        ],
        "direct_residual_bridge_kantorovich_route_closed": strict_standard[
            "direct_residual_bridge_kantorovich_route_closed"
        ],
        "theorem_invocation_consumes_one_residual_value_certificate": strict_standard[
            "theorem_invocation_consumes_one_residual_value_certificate"
        ],
        "future_primitive_taylor_certificate_replacement_only": strict_standard[
            "future_primitive_taylor_certificate_replacement_only"
        ],
        "future_primitive_taylor_requires_same_tuple_132_row_bound": strict_standard[
            "future_primitive_taylor_requires_same_tuple_132_row_bound"
        ],
        "future_primitive_taylor_may_not_append_lower_remove_or_promote": strict_standard[
            "future_primitive_taylor_may_not_append_lower_remove_or_promote"
        ],
        "primitive_taylor_route_closed": strict_standard["primitive_taylor_route_closed"],
        "primitive_route_required_for_b3_closure": strict_standard[
            "primitive_route_required_for_b3_closure"
        ],
        "primitive_taylor_actual_bounds_proved": strict_standard["actual_taylor_bounds_proved"],
        "primitive_taylor_open_bound_terms": strict_standard["open_taylor_bound_terms"],
        "primitive_taylor_terms_with_open_primitive_blockers": strict_standard[
            "terms_with_open_primitive_blockers"
        ],
        "primitive_taylor_open_primitive_count": strict_standard["open_primitive_count"],
    }

    with OUT_JSON.open("w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, sort_keys=True)
        handle.write("\n")

    lines = [
        "# Proof Closure Manifest",
        "",
        "Status: **Direct PC2 residual-value bridge closed under retained theorem interfaces; global claim-promotion/package gates still open**.",
        "Here `submission_ready=false` is scoped to proof-closure/global proof-package readiness,",
        "not to the separate narrowed-claim package decision.",
        "",
        f"- Submission-ready scope: `{result['submission_ready_scope']}`.",
        f"- Narrowed-claim B4/B6/B7 subcheck statuses (narrowed-only; not source-policy row closure): `{result['readiness_boundary']['narrowed_claim_b4_b6_b7_statuses']['B4']}/{result['readiness_boundary']['narrowed_claim_b4_b6_b7_statuses']['B6']}/{result['readiness_boundary']['narrowed_claim_b4_b6_b7_statuses']['B7']}`.",
        f"- Remaining global submission boundaries: `{','.join(result['readiness_boundary']['global_submission_boundaries_retained'])}`.",
        f"- Narrowed-claim B4/B6/B7 subcheck closed elsewhere while source-policy rows remain open: `{result['remaining_gate_scope']['b4_b6_b7_closed_elsewhere_under_narrowed_claim']}`.",
        f"- Direct PC2 residual-value bridge closed under retained theorem interfaces: `{result['remaining_gate_scope']['direct_pc2_proof_gap_closed']}`.",
        f"- Remaining-gate eta_h theorem condition retained: `{result['remaining_gate_scope']['eta_h_theorem_condition_retained']}`.",
        f"- Remaining-gate residual-to-error blocking obligations: `{result['remaining_gate_scope']['residual_to_error_blocking_obligations']}`.",
        f"- Remaining-gate residual-to-error route promoted: `{result['remaining_gate_scope']['residual_to_error_route_promoted']}`.",
        f"- Remaining-gate active direct Newton-Euler open obligations: `{result['remaining_gate_scope']['active_direct_newton_euler_open_obligations']}`.",
        f"- Remaining-gate symbolic/primitive-route open obligations: `{result['remaining_gate_scope']['symbolic_primitive_route_open_obligations']}`.",
        f"- Accepted method/order: `{result['accepted_theorem']['accepted_method']}` / `{result['accepted_theorem']['accepted_method_order']}`.",
        f"- Local defect/global order target: `{result['accepted_theorem']['accepted_local_defect_order']}` / `{result['accepted_theorem']['accepted_global_error_order']}`.",
        f"- Comparator expected order: `{result['accepted_theorem']['comparator']['expected_order']}`.",
        f"- Runtime rows: `{result['evidence_summary']['total_runtime_rows']}`.",
        f"- Certified non-dynamic rows: `{result['evidence_summary']['certified_non_dynamic_rows']}`.",
        f"- Active direct Newton-Euler closed/open rows: `{result['evidence_summary']['active_direct_newton_euler_closed_rows']}/{result['evidence_summary']['active_direct_newton_euler_open_rows']}`.",
        f"- Active direct Newton-Euler open obligations: `{result['evidence_summary']['active_direct_newton_euler_open_obligations']}`.",
        f"- Symbolic/primitive-route Newton-Euler rows not certified by that route: `{result['evidence_summary']['open_dynamic_rows']}`.",
        f"- Symbolic/primitive-route Newton-Euler open obligations: `{result['evidence_summary']['newton_euler_open_obligations']}`.",
        f"- Symbolic/primitive open-row scope: `{result['evidence_summary']['open_dynamic_rows_scope']}`.",
        f"- Newton-Euler closed obligations: `{result['evidence_summary']['newton_euler_closed_obligations']}`.",
        f"- Newton-Euler closed obligation ids: `{result['evidence_summary']['newton_euler_closed_obligation_ids']}`.",
        f"- Newton-Euler symbolic target rows translational/rotational: `{result['evidence_summary']['newton_euler_symbolic_target_rows']}` / `{result['evidence_summary']['newton_euler_symbolic_target_translational_rows']}/{result['evidence_summary']['newton_euler_symbolic_target_rotational_rows']}`.",
        f"- Newton-Euler obligation coverage matrix complete: `{result['evidence_summary']['newton_euler_obligation_coverage_matrix_complete']}`.",
        f"- Newton-Euler row-obligation links: `{result['evidence_summary']['newton_euler_row_obligation_links']}`.",
        f"- Newton-Euler rows with complete obligation sets: `{result['evidence_summary']['newton_euler_rows_with_complete_obligation_sets']}`.",
        f"- Newton-Euler runtime expression structure checked/rows: `{result['evidence_summary']['newton_euler_runtime_expression_structure_checked']}` / `{result['evidence_summary']['newton_euler_runtime_expression_structure_checked_rows']}`.",
        f"- Newton-Euler runtime template instantiation checked/rows: `{result['evidence_summary']['newton_euler_runtime_template_instantiation_checked']}` / `{result['evidence_summary']['newton_euler_runtime_template_instantiation_checked_rows']}`.",
        f"- Newton-Euler template algebraic equivalence checked/rows: `{result['evidence_summary']['newton_euler_template_algebraic_equivalence_checked']}` / `{result['evidence_summary']['newton_euler_template_algebraic_equivalence_checked_rows']}`.",
        f"- Newton-Euler template algebraic translational/rotational rows: `{result['evidence_summary']['newton_euler_template_algebraic_equivalence_translational_rows']}/{result['evidence_summary']['newton_euler_template_algebraic_equivalence_rotational_rows']}`.",
        f"- Newton-Euler template-level C2 subcheck closed: `{result['evidence_summary']['newton_euler_c2_template_algebraic_equivalence_closed']}`.",
        f"- Newton-Euler balance identity closed/rows: `{result['evidence_summary']['newton_euler_balance_identity_closed']}` / `{result['evidence_summary']['newton_euler_balance_identity_closed_rows']}`.",
        f"- Newton-Euler translational/rotational balance identity closed rows: `{result['evidence_summary']['newton_euler_translational_balance_identity_closed_rows']}/{result['evidence_summary']['newton_euler_rotational_balance_identity_closed_rows']}`.",
        f"- Newton-Euler virtual-work sign-skeleton checked/rows: `{result['evidence_summary']['newton_euler_virtual_work_wrench_sign_skeleton_checked']}` / `{result['evidence_summary']['newton_euler_virtual_work_wrench_sign_skeleton_checked_rows']}`.",
        f"- Newton-Euler virtual-work template identity proved/rows: `{result['evidence_summary']['newton_euler_virtual_work_template_identity_proved']}` / `{result['evidence_summary']['newton_euler_virtual_work_template_identity_rows']}`.",
        f"- Newton-Euler row-expanded virtual-work identity proved/rows: `{result['evidence_summary']['newton_euler_row_expanded_virtual_work_identity_proved']}` / `{result['evidence_summary']['newton_euler_row_expanded_virtual_work_identity_rows']}`.",
        f"- Newton-Euler multiplier-wrench consistency closed: `{result['evidence_summary']['newton_euler_multiplier_wrench_consistency_closed']}`.",
        f"- Newton-Euler closure-contract rows/traceability/direct-route row-defect closed: `{result['evidence_summary']['newton_euler_dynamic_row_closure_contract_rows']}` / `{result['evidence_summary']['newton_euler_dynamic_row_closure_contract_traceability_rows']}` / `{result['evidence_summary']['newton_euler_dynamic_row_closure_contract_theorem_closed_rows']}`.",
        f"- Newton-Euler closure-contract open rows: `{result['evidence_summary']['newton_euler_dynamic_row_closure_contract_open_rows']}`.",
        f"- Newton-Euler closure-contract open PCs: `{','.join(result['evidence_summary']['newton_euler_dynamic_row_closure_contract_pc_open'])}`.",
        f"- Newton-Euler D5 blueprint rows/open lifted-stage terms/power-seven rows: `{result['evidence_summary']['newton_euler_d5_dynamic_defect_blueprint_rows']}` / `{result['evidence_summary']['newton_euler_d5_open_lifted_stage_terms']}` / `{result['evidence_summary']['newton_euler_d5_rows_requiring_power_at_least_seven']}`.",
        f"- Newton-Euler D5 finite-probe/residual-promotion accepted rows: `{result['evidence_summary']['newton_euler_d5_finite_probe_sufficient_rows']}` / `{result['evidence_summary']['newton_euler_d5_residual_to_error_promotion_allowed_rows']}`.",
        f"- Newton-Euler D5 direct-substitution blueprint nonclosure flag: `{result['evidence_summary']['newton_euler_d5_blueprint_is_not_closure']}`.",
        f"- Newton-Euler D5 readiness rows/runtime-ready/open-lifted/direct-route certified: `{result['evidence_summary']['newton_euler_d5_readiness_rows']}` / `{result['evidence_summary']['newton_euler_d5_readiness_runtime_ready_rows']}` / `{result['evidence_summary']['newton_euler_d5_readiness_open_lifted_stage_terms']}` / `{result['evidence_summary']['newton_euler_d5_readiness_theorem_certified_rows']}`.",
        f"- Newton-Euler D5 readiness PC2 closed: `{result['evidence_summary']['newton_euler_d5_readiness_pc2_closed']}`.",
        f"- Newton-Euler D5 same-branch dynamic zero-block certificate satisfied/non-circular/O(h^7): `{result['evidence_summary']['newton_euler_d5_direct_substitution_closed']}` / `{result['evidence_summary']['newton_euler_d5_direct_substitution_non_circular']}` / `{result['evidence_summary']['newton_euler_d5_direct_substitution_stage_residual_O_h7']}`.",
        f"- Newton-Euler D5 same-branch dynamic-zero/full-stage rows: `{result['evidence_summary']['newton_euler_d5_direct_substitution_dynamic_zero_rows']}` / `{result['evidence_summary']['newton_euler_d5_direct_substitution_full_stage_rows']}`.",
        f"- Newton-Euler D5 same-branch dynamic zero-block forbidden shortcuts/direct-route PC2 active: `{result['evidence_summary']['newton_euler_d5_direct_substitution_forbidden_shortcuts']}` / `{result['evidence_summary']['newton_euler_d5_direct_substitution_direct_route_pc2_active']}`; residual-to-error/source-policy promotion: `{result['evidence_summary']['newton_euler_d5_direct_substitution_residual_to_error_promotion']}` / `{result['evidence_summary']['newton_euler_d5_direct_substitution_source_policy_promotion']}`.",
        f"- Separate primitive/Taylor route does not discharge the PC2 stage-residual condition: `True`; induced primitive-route Taylor bounds certified/open obligations: `{result['evidence_summary']['newton_euler_d5_primitive_term_bounds_proved']}/{result['evidence_summary']['newton_euler_d5_taylor_term_budget_terms']}` / `{result['evidence_summary']['newton_euler_d5_p_tube_constants_remaining_primitives']}`.",
        f"- Newton-Euler D5 Taylor term budget rows/terms/open/certified: `{result['evidence_summary']['newton_euler_d5_taylor_term_budget_rows']}` / `{result['evidence_summary']['newton_euler_d5_taylor_term_budget_terms']}` / `{result['evidence_summary']['newton_euler_d5_taylor_term_budget_open_terms']}` / `{result['evidence_summary']['newton_euler_d5_taylor_term_budget_certified_terms']}`.",
        f"- Newton-Euler D5 Taylor term budget PC2 closed: `{result['evidence_summary']['newton_euler_d5_taylor_term_budget_pc2_closed']}`.",
        f"- Newton-Euler D5 primitive reduction terms/rules/obligations/proved: `{result['evidence_summary']['newton_euler_d5_primitive_reduction_terms']}` / `{result['evidence_summary']['newton_euler_d5_primitive_reduction_rules']}` / `{result['evidence_summary']['newton_euler_d5_primitive_obligations']}` / `{result['evidence_summary']['newton_euler_d5_primitive_obligations_proved']}`.",
        f"- Newton-Euler D5 primitive reduction term bounds proved: `{result['evidence_summary']['newton_euler_d5_primitive_term_bounds_proved']}`.",
        f"- Newton-Euler D5 primitive reduction PC2 closed: `{result['evidence_summary']['newton_euler_d5_primitive_reduction_pc2_closed']}`.",
        f"- Newton-Euler D5 smooth force/torque/friction corollary label/conditional rows/main-flat: `{result['evidence_summary']['newton_euler_d5_smooth_force_corollary_label']}` / `{result['evidence_summary']['newton_euler_d5_smooth_force_conditionally_bound_terms']}` / `{result['evidence_summary']['newton_euler_d5_smooth_force_corollary_main_flat_present']}`.",
        f"- Newton-Euler D5 smooth force/torque/friction inputs/actual bounds/primitive/PC2/D4-as-rate: `{result['evidence_summary']['newton_euler_d5_smooth_force_primitive_inputs_assumed']}` / `{result['evidence_summary']['newton_euler_d5_smooth_force_actual_taylor_bounds_proved']}` / `{result['evidence_summary']['newton_euler_d5_smooth_force_primitive_closed']}` / `{result['evidence_summary']['newton_euler_d5_smooth_force_pc2_closed']}` / `{result['evidence_summary']['newton_euler_d5_smooth_force_d4_direct_route_used_as_rate_proof']}`.",
        f"- Newton-Euler D5 P_tube compact constants closed/term rows/remaining primitives: `{result['evidence_summary']['newton_euler_d5_p_tube_constants_closed']}` / `{result['evidence_summary']['newton_euler_d5_p_tube_constants_term_rows']}` / `{result['evidence_summary']['newton_euler_d5_p_tube_constants_remaining_primitives']}`.",
        f"- Newton-Euler D5 P_tube induced bounds/PC2 closed: `{result['evidence_summary']['newton_euler_d5_p_tube_constants_induced_bounds_proved']}` / `{result['evidence_summary']['newton_euler_d5_p_tube_constants_pc2_closed']}`.",
        f"- Newton-Euler D5 P_state gap recorded/closed/term rows: `{result['evidence_summary']['newton_euler_d5_p_state_gap_recorded']}` / `{result['evidence_summary']['newton_euler_d5_p_state_closed']}` / `{result['evidence_summary']['newton_euler_d5_p_state_term_rows']}`.",
        f"- Newton-Euler D5 P_state map definition recorded/closed/rows/subproofs: `{result['evidence_summary']['newton_euler_d5_p_state_map_definition_recorded']}` / `{result['evidence_summary']['newton_euler_d5_p_state_map_definition_closed']}` / `{result['evidence_summary']['newton_euler_d5_p_state_map_rows']}` / `{result['evidence_summary']['newton_euler_d5_p_state_map_subproofs_closed']}` / `{result['evidence_summary']['newton_euler_d5_p_state_map_required_subproofs']}`.",
        f"- Newton-Euler D5 P_state anti-circularity recorded/closed/subproofs-after/open-after/PC2: `{result['evidence_summary']['newton_euler_d5_p_state_anticircularity_recorded']}` / `{result['evidence_summary']['newton_euler_d5_p_state_anticircularity_closed']}` / `{result['evidence_summary']['newton_euler_d5_p_state_anticircularity_subproofs_after']}` / `{result['evidence_summary']['newton_euler_d5_p_state_anticircularity_open_subproofs_after']}` / `{result['evidence_summary']['newton_euler_d5_p_state_anticircularity_pc2_closed']}`.",
        f"- Newton-Euler D5 P_state PS2 weighted target recorded/spec/infsup/state-acc-row/PC2: `{result['evidence_summary']['newton_euler_d5_p_state_ps2_weighted_target_recorded']}` / `{result['evidence_summary']['newton_euler_d5_p_state_ps2_weighted_target_spec_closed']}` / `{result['evidence_summary']['newton_euler_d5_p_state_ps2_weighted_target_infsup_closed']}` / `{result['evidence_summary']['newton_euler_d5_p_state_ps2_weighted_target_state_dim']}`-`{result['evidence_summary']['newton_euler_d5_p_state_ps2_weighted_target_acc_dim']}`-`{result['evidence_summary']['newton_euler_d5_p_state_ps2_weighted_target_row_dim']}` / `{result['evidence_summary']['newton_euler_d5_p_state_ps2_weighted_target_pc2_closed']}`.",
        f"- Newton-Euler D5 P_state PS2 kinematic block recorded/subblock/full-PS2/rows-surplus/norm/gaps/PC2: `{result['evidence_summary']['newton_euler_d5_p_state_ps2_kinematic_block_recorded']}` / `{result['evidence_summary']['newton_euler_d5_p_state_ps2_kinematic_subblock_bound_certified']}` / `{result['evidence_summary']['newton_euler_d5_p_state_ps2_kinematic_full_nonlinear_ps2_certified']}` / `{result['evidence_summary']['newton_euler_d5_p_state_ps2_kinematic_rows']}`-`{result['evidence_summary']['newton_euler_d5_p_state_ps2_kinematic_lower_pair_surplus_rows']}` / `{result['evidence_summary']['newton_euler_d5_p_state_ps2_kinematic_inverse_template_norm']}` / `{result['evidence_summary']['newton_euler_d5_p_state_ps2_kinematic_binding_gap_count']}` / `{result['evidence_summary']['newton_euler_d5_p_state_ps2_kinematic_pc2_closed']}`.",
        f"- Newton-Euler D5 P_state PS2 Lie-chart binding recorded/SO3/full-mean/full-PS2/factor/gaps/PC2: `{result['evidence_summary']['newton_euler_d5_p_state_ps2_lie_chart_binding_recorded']}` / `{result['evidence_summary']['newton_euler_d5_p_state_ps2_lie_chart_so3_norm_equivalence']}` / `{result['evidence_summary']['newton_euler_d5_p_state_ps2_lie_chart_full_mean_value_binding']}` / `{result['evidence_summary']['newton_euler_d5_p_state_ps2_lie_chart_full_nonlinear_ps2']}` / `{result['evidence_summary']['newton_euler_d5_p_state_ps2_lie_chart_equivalence_factor']}` / `{result['evidence_summary']['newton_euler_d5_p_state_ps2_lie_chart_remaining_binding_gaps']}` / `{result['evidence_summary']['newton_euler_d5_p_state_ps2_lie_chart_pc2_closed']}`.",
        f"- Newton-Euler D5 P_state PS2 row injection recorded/72-to-96/scaling/norm/full-mean/full-PS2/gaps/PC2: `{result['evidence_summary']['newton_euler_d5_p_state_ps2_row_injection_recorded']}` / `{result['evidence_summary']['newton_euler_d5_p_state_ps2_row_injection_72_to_96_certified']}` / `{result['evidence_summary']['newton_euler_d5_p_state_ps2_row_injection_unweighted_scaling']}` / `{result['evidence_summary']['newton_euler_d5_p_state_ps2_row_injection_selector_norm']}` / `{result['evidence_summary']['newton_euler_d5_p_state_ps2_row_injection_full_mean_value_binding']}` / `{result['evidence_summary']['newton_euler_d5_p_state_ps2_row_injection_full_nonlinear_ps2']}` / `{result['evidence_summary']['newton_euler_d5_p_state_ps2_row_injection_remaining_binding_gaps']}` / `{result['evidence_summary']['newton_euler_d5_p_state_ps2_row_injection_pc2_closed']}`.",
        f"- Newton-Euler D5 P_state PS2 nonlinear binding recorded/rot-mean/full-mean/full-PS2/gaps/PC2: `{result['evidence_summary']['newton_euler_d5_p_state_ps2_nonlinear_binding_recorded']}` / `{result['evidence_summary']['newton_euler_d5_p_state_ps2_nonlinear_rotational_mean_value']}` / `{result['evidence_summary']['newton_euler_d5_p_state_ps2_nonlinear_full_mean_value']}` / `{result['evidence_summary']['newton_euler_d5_p_state_ps2_nonlinear_full_ps2']}` / `{result['evidence_summary']['newton_euler_d5_p_state_ps2_nonlinear_promotion_gaps']}` / `{result['evidence_summary']['newton_euler_d5_p_state_ps2_nonlinear_pc2_closed']}`.",
        f"- Newton-Euler D5 P_state PS2 aggregate promotion recorded/inverse/uniform/PS2/PS3/P_state/PC2: `{result['evidence_summary']['newton_euler_d5_p_state_ps2_aggregate_promotion_recorded']}` / `{result['evidence_summary']['newton_euler_d5_p_state_ps2_aggregate_weighted_inverse_certified']}` / `{result['evidence_summary']['newton_euler_d5_p_state_ps2_aggregate_uniform_constant_certified']}` / `{result['evidence_summary']['newton_euler_d5_p_state_ps2_aggregate_inverse_or_infsup_closed']}` / `{result['evidence_summary']['newton_euler_d5_p_state_ps2_aggregate_ps3_actual_conversion_closed']}` / `{result['evidence_summary']['newton_euler_d5_p_state_ps2_aggregate_p_state_closed']}` / `{result['evidence_summary']['newton_euler_d5_p_state_ps2_aggregate_pc2_closed']}`.",
        f"- Newton-Euler D5 P_state PS2 finite linearization probe recorded/full-rank/rank-range/min-singular/state-projection/uniform/PC2: `{result['evidence_summary']['newton_euler_d5_p_state_ps2_linearization_probe_recorded']}` / `{result['evidence_summary']['newton_euler_d5_p_state_ps2_linearization_probe_full_column_rank_all']}` / `{result['evidence_summary']['newton_euler_d5_p_state_ps2_linearization_probe_rank_range']}` / `{result['evidence_summary']['newton_euler_d5_p_state_ps2_linearization_probe_min_singular']}` / `{result['evidence_summary']['newton_euler_d5_p_state_ps2_linearization_probe_max_state_projection_constant']}` / `{result['evidence_summary']['newton_euler_d5_p_state_ps2_linearization_probe_uniform_constant_proved']}` / `{result['evidence_summary']['newton_euler_d5_p_state_ps2_linearization_probe_pc2_closed']}`.",
        f"- Newton-Euler D5 P_state PS3 conditional conversion recorded/conditional/actual/PS2/input/rates/PC2: `{result['evidence_summary']['newton_euler_d5_p_state_ps3_conditional_conversion_recorded']}` / `{result['evidence_summary']['newton_euler_d5_p_state_ps3_conditional_conversion_closed']}` / `{result['evidence_summary']['newton_euler_d5_p_state_ps3_actual_conversion_closed']}` / `{result['evidence_summary']['newton_euler_d5_p_state_ps3_ps2_dependency_satisfied_by_aggregate']}`-`{result['evidence_summary']['newton_euler_d5_p_state_ps3_ps2_inverse_or_infsup_closed']}` / `{result['evidence_summary']['newton_euler_d5_p_state_ps3_actual_input_instantiation_closed']}` / `{result['evidence_summary']['newton_euler_d5_p_state_ps3_weighted_acceleration_rate']}`-`{result['evidence_summary']['newton_euler_d5_p_state_ps3_conditional_state_lift_rate']}` / `{result['evidence_summary']['newton_euler_d5_p_state_ps3_pc2_closed']}`.",
        f"- Newton-Euler D5 P_state PS3 actual-instantiation gap recorded/inputs/h-input/table/P_state/PC2: `{result['evidence_summary']['newton_euler_d5_p_state_ps3_actual_gap_recorded']}` / `{result['evidence_summary']['newton_euler_d5_p_state_ps3_actual_gap_inputs_closed']}`-`{result['evidence_summary']['newton_euler_d5_p_state_ps3_actual_gap_inputs_total']}` / `{result['evidence_summary']['newton_euler_d5_p_state_ps3_actual_gap_independent_h_acc_input_closed']}` / `{result['evidence_summary']['newton_euler_d5_p_state_ps3_actual_gap_non_circular_instantiation_closed']}` / `{result['evidence_summary']['newton_euler_d5_p_state_ps3_actual_gap_p_state_closed']}` / `{result['evidence_summary']['newton_euler_d5_p_state_ps3_actual_gap_pc2_closed']}`.",
        f"- Newton-Euler D5 P_state PS3 h-acc input obstruction recorded/nullity/residual-only/input/PS3/PC2: `{result['evidence_summary']['newton_euler_d5_p_state_ps3_h_acc_obstruction_recorded']}` / `{result['evidence_summary']['newton_euler_d5_p_state_ps3_h_acc_obstruction_finite_nullity_min']}`-`{result['evidence_summary']['newton_euler_d5_p_state_ps3_h_acc_obstruction_finite_nullity_max']}` / `{result['evidence_summary']['newton_euler_d5_p_state_ps3_h_acc_obstruction_residual_only_input_sufficient']}` / `{result['evidence_summary']['newton_euler_d5_p_state_ps3_h_acc_obstruction_independent_h_acc_input_closed']}` / `{result['evidence_summary']['newton_euler_d5_p_state_ps3_h_acc_obstruction_actual_ps3_closed']}` / `{result['evidence_summary']['newton_euler_d5_p_state_ps3_h_acc_obstruction_pc2_closed']}`.",
        f"- Newton-Euler D5 P_state future subproofs closed/total and induced bounds/PC2: `{result['evidence_summary']['newton_euler_d5_p_state_future_subproofs_closed']}` / `{result['evidence_summary']['newton_euler_d5_p_state_future_subproofs']}` / `{result['evidence_summary']['newton_euler_d5_p_state_induced_bounds_proved']}` / `{result['evidence_summary']['newton_euler_d5_p_state_pc2_closed']}`.",
        f"- Newton-Euler D5 P_acc map definition recorded/closed/rows/subproofs: `{result['evidence_summary']['newton_euler_d5_p_acc_map_definition_recorded']}` / `{result['evidence_summary']['newton_euler_d5_p_acc_map_definition_closed']}` / `{result['evidence_summary']['newton_euler_d5_p_acc_map_rows']}` / `{result['evidence_summary']['newton_euler_d5_p_acc_map_subproofs_closed']}` / `{result['evidence_summary']['newton_euler_d5_p_acc_map_required_subproofs']}`.",
        f"- Newton-Euler D5 P_acc row binding recorded/closed/rows/subproofs-after: `{result['evidence_summary']['newton_euler_d5_p_acc_row_binding_recorded']}` / `{result['evidence_summary']['newton_euler_d5_p_acc_row_binding_closed']}` / `{result['evidence_summary']['newton_euler_d5_p_acc_row_binding_rows']}` / `{result['evidence_summary']['newton_euler_d5_p_acc_row_binding_subproofs_after']}` / `{result['evidence_summary']['newton_euler_d5_p_acc_row_binding_required_subproofs']}`.",
        f"- Newton-Euler D5 P_acc independence recorded/closed/input-families/subproofs-after: `{result['evidence_summary']['newton_euler_d5_p_acc_independence_recorded']}` / `{result['evidence_summary']['newton_euler_d5_p_acc_independence_closed']}` / `{result['evidence_summary']['newton_euler_d5_p_acc_independence_input_families']}` / `{result['evidence_summary']['newton_euler_d5_p_acc_independence_required_input_families']}` / `{result['evidence_summary']['newton_euler_d5_p_acc_independence_subproofs_after']}` / `{result['evidence_summary']['newton_euler_d5_p_acc_independence_required_subproofs']}`.",
        f"- Newton-Euler D5 P_acc PA2 obstruction recorded/closed/current-rate: `{result['evidence_summary']['newton_euler_d5_p_acc_pa2_obstruction_recorded']}` / `{result['evidence_summary']['newton_euler_d5_p_acc_pa2_closed']}` / `{result['evidence_summary']['newton_euler_d5_p_acc_current_unweighted_acceleration_rate']}`.",
        f"- Newton-Euler D5 P_acc velocity-collocation-alone sufficient/lift-rate-proved/term-bounds/PC2: `{result['evidence_summary']['newton_euler_d5_p_acc_velocity_collocation_alone_sufficient']}` / `{result['evidence_summary']['newton_euler_d5_p_acc_lift_rate_proved']}` / `{result['evidence_summary']['newton_euler_d5_p_acc_lift_obstruction_term_bounds_proved']}` / `{result['evidence_summary']['newton_euler_d5_p_acc_lift_obstruction_pc2_closed']}`.",
        f"- Newton-Euler D5 P_acc PA2 weighted-inverse recorded/h-control/probes/full-rank: `{result['evidence_summary']['newton_euler_d5_p_acc_pa2_weighted_inverse_recorded']}` / `{result['evidence_summary']['newton_euler_d5_p_acc_pa2_weighted_h_control_recorded']}` / `{result['evidence_summary']['newton_euler_d5_p_acc_pa2_weighted_inverse_probe_count']}` / `{result['evidence_summary']['newton_euler_d5_p_acc_pa2_weighted_inverse_full_rank_all']}`.",
        f"- Newton-Euler D5 P_acc PA2 projection constants unweighted/weighted-h and unweighted-control/PA2/PC2: `{result['evidence_summary']['newton_euler_d5_p_acc_pa2_max_unweighted_acceleration_projection_constant']}` / `{result['evidence_summary']['newton_euler_d5_p_acc_pa2_max_weighted_h_acceleration_projection_constant']}` / `{result['evidence_summary']['newton_euler_d5_p_acc_pa2_unweighted_uniform_control_proved']}` / `{result['evidence_summary']['newton_euler_d5_p_acc_pa2_weighted_inverse_pa2_closed']}` / `{result['evidence_summary']['newton_euler_d5_p_acc_pa2_weighted_inverse_pc2_closed']}`.",
        f"- Newton-Euler D5 P_lambda interface/PL2/D3/PL4 recorded/closed/lambda-vars/direct-rows/term-rows/conditional-subproofs-after/open-after: `{result['evidence_summary']['newton_euler_d5_p_lambda_interface_recorded']}`-`{result['evidence_summary']['newton_euler_d5_p_lambda_pl2_geometric_margin_recorded']}`-`{result['evidence_summary']['newton_euler_d5_p_lambda_d3_noncircularity_recorded']}`-`{result['evidence_summary']['newton_euler_d5_p_lambda_pl4_rate_propagation_recorded']}` / `{result['evidence_summary']['newton_euler_d5_p_lambda_interface_closed']}`-`{result['evidence_summary']['newton_euler_d5_p_lambda_pl2_uniform_inf_sup_bound_proved']}`-`{result['evidence_summary']['newton_euler_d5_p_lambda_d3_noncircularity_closed']}`-`{result['evidence_summary']['newton_euler_d5_p_lambda_pl4_rate_propagation_closed']}` / `{result['evidence_summary']['newton_euler_d5_p_lambda_stage_variables']}` / `{result['evidence_summary']['newton_euler_d5_p_lambda_direct_rows']}` / `{result['evidence_summary']['newton_euler_d5_p_lambda_term_rows']}` / `{result['evidence_summary']['newton_euler_d5_p_lambda_subproofs_after']}` / `{result['evidence_summary']['newton_euler_d5_p_lambda_required_subproofs']}` / `{result['evidence_summary']['newton_euler_d5_p_lambda_open_subproofs_after']}`.",
        f"- Newton-Euler D5 P_lambda PL2 symbolic margin/probe-stage-rows/finite-probe-as-proof/primitive/PC2: `{result['evidence_summary']['newton_euler_d5_p_lambda_pl2_symbolic_margin_premise_proved']}` / `{result['evidence_summary']['newton_euler_d5_p_lambda_pl2_probe_stage_rows']}` / `{result['evidence_summary']['newton_euler_d5_p_lambda_pl2_finite_probe_sufficient_for_uniform_proof']}` / `{result['evidence_summary']['newton_euler_d5_p_lambda_pl2_primitive_closed']}` / `{result['evidence_summary']['newton_euler_d5_p_lambda_pl2_pc2_closed']}`.",
        f"- Newton-Euler D5 P_lambda conditional PL subproofs complete/actual multiplier lift open/scope: `{result['evidence_summary']['newton_euler_d5_p_lambda_conditional_pl_subproofs_complete']}` / `{result['evidence_summary']['newton_euler_d5_p_lambda_actual_multiplier_lift_open']}` / {result['evidence_summary']['newton_euler_d5_p_lambda_conditional_subproof_scope']}",
        f"- Newton-Euler D5 P_lambda PL4 conditional/actual multiplier rate and open inputs: `{result['evidence_summary']['newton_euler_d5_p_lambda_pl4_conditional_multiplier_rate']}` / `{result['evidence_summary']['newton_euler_d5_p_lambda_pl4_actual_multiplier_rate']}` / `{result['evidence_summary']['newton_euler_d5_p_lambda_pl4_open_input_dependencies']}`.",
        f"- Newton-Euler D5 P_lambda primitive/PC2 closed: `{result['evidence_summary']['newton_euler_d5_p_lambda_primitive_closed']}` / `{result['evidence_summary']['newton_euler_d5_p_lambda_pc2_closed']}`.",
        f"- Newton-Euler D5 P_geom reduction recorded/chart-closed/actual primitive open/scope: `{result['evidence_summary']['newton_euler_d5_p_geom_reduction_recorded']}` / `{result['evidence_summary']['newton_euler_d5_p_geom_chart_reduction_closed']}` / `{result['evidence_summary']['newton_euler_d5_p_geom_actual_primitive_open']}` / {result['evidence_summary']['newton_euler_d5_p_geom_conditional_reduction_scope']}",
        f"- Newton-Euler D5 P_geom subproofs closed/total, open inputs, conditional rows, primitive, PC2: `{result['evidence_summary']['newton_euler_d5_p_geom_closed_subproofs']}` / `{result['evidence_summary']['newton_euler_d5_p_geom_required_subproofs']}` / `{result['evidence_summary']['newton_euler_d5_p_geom_open_dependencies']}` / `{result['evidence_summary']['newton_euler_d5_p_geom_conditionally_reduced_rows']}` / `{result['evidence_summary']['newton_euler_d5_p_geom_primitive_closed']}` / `{result['evidence_summary']['newton_euler_d5_p_geom_pc2_closed']}`.",
        f"- Newton-Euler D5 P_geom translational/rotational reduced rows: `{result['evidence_summary']['newton_euler_d5_p_geom_translational_rows']}` / `{result['evidence_summary']['newton_euler_d5_p_geom_rotational_rows']}`.",
        f"- Newton-Euler D5 P_gyro reduction recorded/algebraic-closed/internal complete not primitive/actual primitive open/scope: `{result['evidence_summary']['newton_euler_d5_p_gyro_reduction_recorded']}` / `{result['evidence_summary']['newton_euler_d5_p_gyro_algebraic_reduction_closed']}` / `{result['evidence_summary']['newton_euler_d5_p_gyro_internal_reduction_complete_not_primitive']}` / `{result['evidence_summary']['newton_euler_d5_p_gyro_actual_primitive_open']}` / {result['evidence_summary']['newton_euler_d5_p_gyro_conditional_reduction_scope']}",
        f"- Newton-Euler D5 P_gyro subproofs closed/total, open inputs, conditional rows, primitive, PC2: `{result['evidence_summary']['newton_euler_d5_p_gyro_closed_subproofs']}` / `{result['evidence_summary']['newton_euler_d5_p_gyro_required_subproofs']}` / `{result['evidence_summary']['newton_euler_d5_p_gyro_open_dependencies']}` / `{result['evidence_summary']['newton_euler_d5_p_gyro_conditionally_reduced_rows']}` / `{result['evidence_summary']['newton_euler_d5_p_gyro_primitive_closed']}` / `{result['evidence_summary']['newton_euler_d5_p_gyro_pc2_closed']}`.",
        f"- Newton-Euler D5 primitive closure-plan obligations/interfaces/proved/open: `{result['evidence_summary']['newton_euler_d5_primitive_closure_plan_obligations']}` / `{result['evidence_summary']['newton_euler_d5_primitive_closure_plan_interfaces']}` / `{result['evidence_summary']['newton_euler_d5_primitive_closure_plan_proved']}` / `{result['evidence_summary']['newton_euler_d5_primitive_closure_plan_open']}`.",
        f"- Newton-Euler D5 primitive closure-plan induced bounds proved: `{result['evidence_summary']['newton_euler_d5_primitive_closure_plan_induced_bounds_proved']}`.",
        f"- Newton-Euler D5 primitive closure-plan PC2 closed: `{result['evidence_summary']['newton_euler_d5_primitive_closure_plan_pc2_closed']}`.",
        f"- Newton-Euler D5 conditional Taylor certificate rows/terms: `{result['evidence_summary']['newton_euler_d5_conditional_taylor_certificate_rows']}` / `{result['evidence_summary']['newton_euler_d5_conditional_taylor_certificate_terms']}`.",
        f"- Newton-Euler D5 conditional Taylor certificate conditional rows/terms: `{result['evidence_summary']['newton_euler_d5_conditional_taylor_certificate_conditional_rows']}` / `{result['evidence_summary']['newton_euler_d5_conditional_taylor_certificate_conditional_terms']}`.",
        f"- Newton-Euler D5 conditional Taylor certificate actual terms proved/open primitive assumptions/PC2: `{result['evidence_summary']['newton_euler_d5_conditional_taylor_certificate_actual_terms_proved']}` / `{result['evidence_summary']['newton_euler_d5_conditional_taylor_certificate_open_primitive_assumptions']}` / `{result['evidence_summary']['newton_euler_d5_conditional_taylor_certificate_pc2_closed']}`.",
        f"- Newton-Euler D5 open primitive gap recorded/count: `{result['evidence_summary']['newton_euler_d5_open_primitive_gap_recorded']}` / `{result['evidence_summary']['newton_euler_d5_open_primitive_gap_count']}`.",
        f"- Newton-Euler D5 open primitive future subproofs closed/total and induced bounds/PC2: `{result['evidence_summary']['newton_euler_d5_open_primitive_gap_future_subproofs_closed']}` / `{result['evidence_summary']['newton_euler_d5_open_primitive_gap_future_subproofs']}` / `{result['evidence_summary']['newton_euler_d5_open_primitive_gap_induced_bounds_proved']}` / `{result['evidence_summary']['newton_euler_d5_open_primitive_gap_pc2_closed']}`.",
        f"- Residual-to-error blocking obligations: `{result['evidence_summary']['residual_to_error_blocking_obligations']}`.",
        f"- Formula-row AD Jacobian probes/max mismatch: `{result['evidence_summary']['formula_row_ad_jacobian_probe_count']}` / `{result['evidence_summary']['formula_row_ad_jacobian_max_mismatch']}`.",
        f"- Smooth projected position/velocity orders: `{result['evidence_summary']['smooth_projected_position_order']:.6f}` / `{result['evidence_summary']['smooth_projected_velocity_order']:.6f}`.",
        f"- Endpoint raw constraint fits: `{result['evidence_summary']['endpoint_raw_position_constraint_fit']:.6f}` / `{result['evidence_summary']['endpoint_raw_velocity_constraint_fit']:.6f}`.",
        f"- Smooth reference eta/h^7 diagnostic: `{result['evidence_summary']['smooth_reference_eta_over_h7']:.6f}`.",
        f"- Finite scaled-tolerance probe rows/max eta-h ratio: `{result['solver_state']['finite_scaled_tolerance_probe_ok_rows']}/{result['solver_state']['finite_scaled_tolerance_probe_total_rows']}` / `{result['solver_state']['finite_scaled_tolerance_probe_max_residual_over_h7']:.6f}`.",
        f"- Finite scaled-tolerance trajectory probe rows/steps/max eta-h ratio: `{result['solver_state']['finite_scaled_tolerance_trajectory_probe_ok_rows']}/{result['solver_state']['finite_scaled_tolerance_trajectory_probe_total_rows']}` / `{result['solver_state']['finite_scaled_tolerance_trajectory_probe_total_steps_checked']}` / `{result['solver_state']['finite_scaled_tolerance_trajectory_probe_max_residual_over_h7']:.6f}`.",
        f"- Finite tolerance-regime sweep policies/rows/steps: `{result['solver_state']['finite_tolerance_regime_sweep_policy_count']}` / `{result['solver_state']['finite_tolerance_regime_sweep_total_rows']}` / `{result['solver_state']['finite_tolerance_regime_sweep_total_steps']}`.",
        f"- Finite h-scaled tolerance-regime sweep rows/steps/velocity-order floor: `{result['solver_state']['finite_h_scaled_tolerance_sweep_rows']}` / `{result['solver_state']['finite_h_scaled_tolerance_sweep_steps']}` / `{result['solver_state']['finite_h_scaled_tolerance_sweep_velocity_order_floor']}`.",
        f"- Per-step branch-selected eta_h policy: `{result['solver_state']['per_step_newton_tolerance_policy']}`.",
        f"- Same reduced-chart initial state required: `{result['solver_state']['same_reduced_chart_initial_state_required']}`.",
        f"- Gauss-predictor branch-selected Newton solves required: `{result['solver_state']['branch_selected_newton_solves_required']}` / `{result['solver_state']['newton_iterates_initialized_from_gauss_predictor_required']}`.",
        f"- Arbitrary Newton initializations or remote roots select branch: `{result['solver_state']['arbitrary_newton_initializations_select_branch']}` / `{result['solver_state']['remote_nonlinear_roots_select_branch']}`.",
        f"- Explicit Gauss truncation constant uniform on compact trajectory tube: `{result['solver_state']['gauss_truncation_bound_has_explicit_uniform_constant']}` / `{result['solver_state']['gauss_truncation_constant_uniform_on_compact_trajectory_tube']}`.",
        f"- Explicit stage residual-to-root and endpoint constants: `{result['solver_state']['stage_residual_to_root_bound_has_explicit_constant']}` / `{result['solver_state']['stage_residual_to_root_constant_formula']}` / `{result['solver_state']['stage_root_endpoint_perturbation_constant_formula']}`.",
        f"- Accepted root existence proved by stage-residual lemma / not isolated-root premise: `{result['solver_state']['accepted_root_existence_proved_by_stage_residual_lemma']}` / `{result['solver_state']['accepted_root_existence_not_assumed_as_isolated_root_premise']}`.",
        f"- Explicit endpoint-closure raw-defect and perturbation constants: `{result['solver_state']['endpoint_closure_raw_defect_bound_has_explicit_constant']}` / `{result['solver_state']['endpoint_closure_raw_defect_constant_symbol']}` / `{result['solver_state']['endpoint_closure_perturbation_bound_has_explicit_constant']}` / `{result['solver_state']['endpoint_closure_perturbation_constant_formula']}`.",
        f"- Four-term local-defect constants uniform on compact tube / accepted steps: `{result['solver_state']['local_defect_constants_uniform_on_compact_proof_tube']}` / `{result['solver_state']['local_defect_constants_uniform_over_accepted_steps']}`.",
        f"- Newton error controlled by compact-tube eta_h envelope; reported-grid maximum is specialization: `{result['solver_state']['newton_error_controlled_by_compact_tube_eta_h_envelope']}`.",
        f"- Explicit Newton residual-to-stage and endpoint-output constant: `{result['solver_state']['newton_residual_to_stage_bound_has_explicit_constant']}` / `{result['solver_state']['newton_endpoint_output_map']}` / `{result['solver_state']['newton_endpoint_output_map_bound']}` / `{result['solver_state']['newton_residual_to_endpoint_perturbation_constant_formula']}`.",
        f"- Explicit eta_h-scaled Newton endpoint bound: `{result['solver_state']['newton_eta_h_scaled_endpoint_bound_has_explicit_constant']}` / `{result['solver_state']['newton_eta_h_scaled_endpoint_bound_formula']}`.",
        f"- Explicit local-defect constant sum and eta_h absorption: `{result['solver_state']['local_defect_bound_has_explicit_uniform_constant_sum']}` / `{result['solver_state']['eta_h_constant_absorbed_into_local_defect_constant']}`.",
        f"- Explicit local-to-global and q/v reporting constants: `{result['solver_state']['local_global_transfer_has_explicit_reduced_grid_constant']}` / `{result['solver_state']['local_global_gronwall_factor_formula']}` / `{result['solver_state']['local_global_reduced_grid_constant_formula']}` / `{result['solver_state']['qv_reporting_map_constant_distinct_from_residual_defect_constant']}` / `{result['solver_state']['qv_reporting_constant_formula']}`.",
        f"- Same-initial-state reported-grid local-to-global transfer and same-grid reported q/v maximum: `{result['solver_state']['local_global_transfer_grid_point_error_required']}` / `{result['solver_state']['reported_qv_error_bound_uses_same_reported_time_grid']}` / `{result['solver_state']['reported_qv_error_bound_is_grid_maximum']}`.",
        f"- Reported time grid t_n=n h and no exact final-time divisibility requirement: `{result['solver_state']['reported_time_grid_defined_by_tn_equals_nh']}` / `{result['solver_state']['exact_final_time_divisibility_required']}`.",
        f"- Direct PC2 residual-value bridge closed under retained theorem interfaces: `{result['closure_state']['direct_pc2_proof_gap_closed']}`.",
        f"- Direct PC2 residual-bridge scope: `{result['closure_state']['proof_gap_closed_scope']}`.",
        f"- Dynamic symbolic oracle complete: `{result['closure_state']['dynamic_symbolic_oracle_complete']}`.",
        f"- Stage residual O(h^7) defect proved: `{result['closure_state']['stage_residual_O_h7_implementation_defect_proved']}`.",
        f"- Active direct residual-bridge proof standard: `{result['strict_direct_residual_bridge_submission_standard']['required_pc2_route']}`.",
        f"- Direct residual-bridge proof contract satisfied: `{result['strict_direct_residual_bridge_submission_standard']['satisfied']}`.",
        f"- Not primitive 162-term Taylor closure: `{result['strict_direct_residual_bridge_submission_standard']['not_primitive_162_term_taylor_closure']}`.",
        f"- Theorem residual-certificate consumption rule: one certificate `{result['strict_direct_residual_bridge_submission_standard']['theorem_invocation_consumes_one_residual_value_certificate']}`; future primitive/Taylor replacement-only `{result['strict_direct_residual_bridge_submission_standard']['future_primitive_taylor_certificate_replacement_only']}`; same-tuple 132-row bound required `{result['strict_direct_residual_bridge_submission_standard']['future_primitive_taylor_requires_same_tuple_132_row_bound']}`; no append/lower/remove/promote `{result['strict_direct_residual_bridge_submission_standard']['future_primitive_taylor_may_not_append_lower_remove_or_promote']}`.",
        f"- Primitive/Taylor actual/open terms: `{result['strict_direct_residual_bridge_submission_standard']['primitive_taylor_actual_bounds_proved']}` / `{result['strict_direct_residual_bridge_submission_standard']['primitive_taylor_open_bound_terms']}`.",
        f"- Primitive/Taylor subterms blocked by open primitive assumptions: `{result['strict_direct_residual_bridge_submission_standard']['primitive_taylor_terms_with_open_primitive_blockers']}`.",
        f"- Primitive/Taylor open primitive count: `{result['strict_direct_residual_bridge_submission_standard']['primitive_taylor_open_primitive_count']}`.",
        f"- Same-branch dynamic zero-block supplies active PC2 residual-bridge proof input: `{result['strict_direct_residual_bridge_submission_standard']['direct_substitution_supplies_active_pc2_residual_bridge']}`.",
        f"- eta_h^tube <= c_eta h^7 solver-policy theorem: `{result['closure_state']['eta_h_O_h7_solver_policy_evidence']}`.",
        f"- eta_h theorem condition retained: `{solver_condition_retained}`.",
        f"- Theorem label present main/flat: `{main_label_presence['conditional_order_theorem']}/{flat_label_presence['conditional_order_theorem']}`.",
        f"- Manuscript proof labels all present main/flat: `{all(main_label_presence.values())}/{all(flat_label_presence.values())}`.",
        f"- Manuscript anchor map present: `{result['manuscript_anchor_map']['all_label_anchors_present']}`; label anchors `{result['manuscript_anchor_map']['label_anchor_count']}`; theorem-interface/P7-output-boundary anchors `{result['manuscript_anchor_map']['theorem_assumption_anchor_count']}`.",
        f"- Theorem-interface/P7-output-boundary manuscript anchor IDs: `{','.join(result['manuscript_anchor_map']['theorem_assumption_anchor_ids'])}`.",
        "- Reader-facing theorem-interface split: theorem interfaces `P1--P6`; P7 is an output nonclaim/residual-to-error boundary anchor, not a theorem premise.",
        "- Legacy P7-output-boundary anchor count includes P7 only for traceability across residual tables; it does not promote P7 into the theorem-interface list.",
        f"- Theorem-assumption anchor table table reference coverage: `{result['theorem_anchor_table_reference_coverage']['all_references_present_main_and_flat']}`.",
        f"- Auxiliary-evidence scope main/flat coverage: `{result['theorem_use_rule_boundary']['all_tokens_present_main_and_flat']}`.",
        f"- Constant-dependency rule main/flat coverage: `{result['constant_dependency_table_boundary']['all_tokens_present_main_and_flat']}`.",
        f"- Theorem input-output flow main/flat coverage: `{result['theorem_dependency_consumption_table_boundary']['all_tokens_present_main_and_flat']}`.",
        f"- Theorem output scope rule main/flat coverage: `{result['theorem_output_scope_table_boundary']['all_tokens_present_main_and_flat']}`.",
        f"- Quantifier/domain rule main/flat coverage: `{result['quantifier_domain_table_boundary']['all_tokens_present_main_and_flat']}`.",
        f"- Local-to-global transfer rule main/flat coverage: `{result['local_global_transfer_table_boundary']['all_tokens_present_main_and_flat']}`.",
        f"- Reporting-map/norm-equivalence rule main/flat coverage: `{result['reporting_map_table_boundary']['all_tokens_present_main_and_flat']}`.",
        f"- Proof-causality rule main/flat coverage: `{result['proof_causality_table_boundary']['all_tokens_present_main_and_flat']}`.",
        f"- Accepted-branch consistency rule main/flat coverage: `{result['branch_consistency_table_boundary']['all_tokens_present_main_and_flat']}`.",
        f"- Local-defect decomposition rule main/flat coverage: `{result['local_defect_decomposition_table_boundary']['all_tokens_present_main_and_flat']}`.",
        f"- Direct-route anti-circularity rule main/flat coverage: `{result['direct_route_anticircularity_table_boundary']['all_tokens_present_main_and_flat']}`.",
        f"- Implementation-route/certificate separation main/flat coverage: `{result['implementation_route_oracle_table_boundary']['all_tokens_present_main_and_flat']}`.",
        f"- B1 AD-expanded closure table interpretation main/flat coverage: `{result['b1_ad_expanded_closure_table_boundary']['all_tokens_present_main_and_flat']}`.",
        f"- P1/P2 compact-tube boundary main/flat coverage: `{result['p1p2_compact_tube_boundary']['all_tokens_present_main_and_flat']}`.",
        f"- P3/P4 implementation-defect boundary main/flat coverage: `{result['p3p4_implementation_boundary']['all_tokens_present_main_and_flat']}`.",
        f"- P5 direct-route boundary main/flat coverage: `{result['p5_direct_route_boundary']['all_tokens_present_main_and_flat']}`.",
        f"- P6 solver-scope boundary main/flat coverage: `{result['p6_solver_scope_boundary']['all_tokens_present_main_and_flat']}`.",
        f"- Nonlinear-solver scale rule main/flat coverage: `{result['nonlinear_solver_scale_table_boundary']['all_tokens_present_main_and_flat']}`.",
        f"- Assumptions and theorem scope interpretation main/flat coverage: `{result['p_interface_satisfaction_table_boundary']['all_tokens_present_main_and_flat']}`.",
        f"- Residual-to-error boundary main/flat coverage: `{result['p7_residual_to_error_obligation_table_boundary']['all_tokens_present_main_and_flat']}`.",
        f"- Conditional theorem branch/eta/grid/fixed-tolerance boundary: `{theorem_boundary_present}/{main_theorem_boundary['compact_tube_eta_h_condition']}/{main_theorem_boundary['grid_point_order_six_statement']}/{main_theorem_boundary['fixed_tolerance_exclusion']}`.",
        f"- Theorem reading guide main/flat coverage: `{result['theorem_statement_boundary']['theorem_reading_guide_present_main_and_flat']}`.",
        f"- Proof dependency graph/table/residual non-promotion: `{result['manuscript_traceability']['proof_dependency_graph_present_main_and_flat']}/{result['manuscript_traceability']['proof_traceability_table_present_main_and_flat']}/{result['manuscript_traceability']['residual_to_error_nonpromotion_present_main_and_flat']}`.",
        f"- Conditional proof claims mapped to manuscript: `{result['manuscript_traceability']['conditional_proof_claims_mapped_to_manuscript']}`.",
        f"- Four-link/slider residual-to-error promotion made: `{not residual_promotion_not_made}`.",
        f"- Proof-route checks traceable/blocked under conditional scope: `{sum(1 for row in close_requirements if row['traceable_under_conditional_scope'])}/{sum(1 for row in close_requirements if not row['traceable_under_conditional_scope'])}`.",
        f"- Submission ready: `{result['submission_ready']}`.",
        "",
        "## Manuscript Theorem Traceability",
        "",
        "| item | main | flat |",
        "|---|---:|---:|",
    ]
    for key in MANUSCRIPT_LABEL_TOKENS:
        lines.append(f"| `{key}` | `{main_label_presence[key]}` | `{flat_label_presence[key]}` |")
    lines.extend(
        [
            "",
            "## Theorem Assumption Manuscript Anchors",
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
            "The manifest reads the theorem/proof labels from the manuscript and the flat submission source.",
            "This traceability check documents the conditional proof writing boundary only; it does not close solver-policy theorem, residual-to-error promotion, source-policy rows, or full-TFE replacement.",
            "For theorem-use rule maps, `true` means that the boundary phrase is present in the checked artifact; it does not make the phrase an accepted theorem input.",
            "",
            "## Theorem Assumption Coverage",
            "",
            "P6/OC6 disambiguation: theorem `P6` is the retained compact-tube solver-scale interface; objective blocker `OC6` is the separate source-policy TFE DAE-runner/package gap and is not closed by this proof manifest.",
            "",
            "| id | assumption | status | retained theorem interface | proved row certificate | satisfied for submission | evidence |",
            "|---|---|---|---:|---:|---:|---|",
        ]
    )
    for row in theorem_assumptions:
        retained_interface = row["id"] in {"P1", "P2", "P3", "P4", "P6"}
        proved_certificate = bool(row.get("proved_certificate") or row["satisfied_for_submission"])
        lines.append(
            f"| `{row['id']}` | {row['assumption']} | `{row['status']}` | "
            f"`{retained_interface}` | `{proved_certificate}` | "
            f"`{row['satisfied_for_submission']}` | {row['evidence']} |"
        )

    lines.extend(
        [
            "",
            "P4 split reading rule: P4 remains a retained binding interface and also carries a proved 96-row non-dynamic row certificate.",
            "The `satisfied for submission` column is reserved for assumptions fully discharged as theorem inputs by themselves; P4 is consumed only after its proved 96-row certificate is assembled with P5's 36-row direct Newton--Euler certificate on the same accepted branch.",
            "",
            "## Newton-Euler Symbolic/Primitive-Lane Open Obligations",
            "",
            "| id | rows | status | required proof |",
            "|---|---:|---|---|",
        ]
    )
    for row in result["newton_euler_open_obligations"]:
        lines.append(
            f"| `{row['id']}` | `{row['row_count']}` | `{row['status']}` | {row['required_proof']} |"
        )
    lines.extend(
        [
            "",
            "## Newton-Euler Closed Sub-Obligations",
            "",
            "| id | rows | status | closure evidence |",
            "|---|---:|---|---|",
        ]
    )
    for row in result["newton_euler_closed_obligations"]:
        lines.append(
            f"| `{row['id']}` | `{row['row_count']}` | `{row['status']}` | {row['closure_evidence']} |"
        )

    lines.extend(
        [
            "",
            "## Proof Route Checks",
            "",
            "| id | requirement | traceability status | mode |",
            "|---|---|---|---|",
        ]
    )
    for row in close_requirements:
        lines.append(
            f"| `{row['id']}` | {row['requirement']} | `{row['display_status']}` | "
            f"`{row['satisfaction_mode']}` |"
        )

    lines.extend(
        [
            "",
            "## Claim Policy",
            "",
            "- Allowed now: conditional local-defect-to-global-error theorem, finite-run numerical scale diagnostic support, and formal order comparison.",
            "- Forbidden now: unconditional non-assumption theorem closure, dynamic symbolic oracle completion, residual-to-error promotion, full TFE stage replacement, and unscoped/global proof-package submission-ready claims.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
