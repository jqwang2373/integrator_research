# Exact Stage Identity Gate

Status: **exact_stage_identity_route_pinned_lean_checked**.

This gate pins the compacted proof route of the CMAME manuscript: the implemented
Gauss6/FullVA stage system is exactly reduced joint-coordinate Gauss collocation, the stage
residual at the lifted Gauss stage is identically zero (`C_R = C_A = 0`), and the local defect is
`C_loc = C_G + C_E + C_N c_eta`. Retained interfaces: P1, P2, P6; output boundary: P7; removed:
P3, P4, P5. It changes no claim state and keeps `submission_ready=false`.

## Manuscript checks

- main: labels `38/38`, tokens `24/24`, retired tokens present `0`, lines `4043`, lemmas `9`, theorems `1`.
- flat: labels `38/38`, tokens `24/24`, retired tokens present `0`.
- display hygiene (main): unlabelled `0`, bare `0`, unreferenced labels `0` of `48`.

## Lean binding

- project: `/home/jingquanw/lean/integrator_order_proof` present=`True`, files `10/10`.
- lean check run here: `True`; status `all_required_theorems_checked_standard_axioms_no_sorry`; sorry count `0`.
- package copy `lean/`: files present `True`, in sync with the built development `True`.

| role | Lean theorem |
| --- | --- |
| `exact_stage_identity_nondynamic` | `IntegratorOrderProof.FullVA.Transition.nondynamic_rows_iff` |
| `exact_stage_identity_dynamic` | `IntegratorOrderProof.NewtonEuler.dynamic_rows_vanish` |
| `branch_selection` | `IntegratorOrderProof.root_unique_of_linearization` |
| `endpoint_closure` | `IntegratorOrderProof.endpoint_correction_bound_h7` |
| `inexact_newton` | `IntegratorOrderProof.inexact_newton_output_bound` |
| `local_to_global` | `IntegratorOrderProof.local_to_global` |
| `grid_bound` | `IntegratorOrderProof.conditional_sixth_order_grid_bound` |
| `gauss_tableau_order_conditions` | `IntegratorOrderProof.Gauss6.butcher_order_six_hypotheses` |
| `gauss_tableau_not_order_seven` | `IntegratorOrderProof.Gauss6.not_B_seven` |
| `quadrature_defect` | `IntegratorOrderProof.gauss6_step_defect` |
| `uniform_inverse_perturbation` | `IntegratorOrderProof.uniform_inverse_of_perturbation` |
| `newton_residual_decay` | `IntegratorOrderProof.simplified_newton_residual_decay` |

## Superseded artifacts

- `PROOF_CLOSURE_MANIFEST`
- `PROOF_CLAIM_TRACEABILITY_AUDIT`
- `CMAME_STRICT_PROOF_AUDIT`
- `CMAME_STRICT_PROOF_POLICY_RECONCILIATION_AUDIT`
- `CMAME_PROOF_STYLE_AUDIT`
- `NEWTON_EULER_SYMBOLIC_DEFECT_CERTIFICATE`
- `CMAME_PROOF_CONTRACT_GATE`

Validator: `validate_exact_stage_identity_gate.py`.
