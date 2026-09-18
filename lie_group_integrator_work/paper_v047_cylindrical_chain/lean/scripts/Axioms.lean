-- Run with:  lake env lean scripts/Axioms.lean
-- Every theorem must report only [propext, Classical.choice, Quot.sound]; `sorryAx` must not appear.
import IntegratorOrderProof
#print axioms IntegratorOrderProof.exists_root_of_linearization
#print axioms IntegratorOrderProof.root_unique_of_linearization
#print axioms IntegratorOrderProof.stage_root_exists_unique
#print axioms IntegratorOrderProof.linearization_of_fderiv_bound
#print axioms IntegratorOrderProof.inexact_newton_output_bound
#print axioms IntegratorOrderProof.endpoint_closure_exists
#print axioms IntegratorOrderProof.endpoint_correction_bound_h7
#print axioms IntegratorOrderProof.geom_sum_le_gronwallFactor
#print axioms IntegratorOrderProof.local_to_global
#print axioms IntegratorOrderProof.reported_grid_bound
#print axioms IntegratorOrderProof.local_defect_bound
#print axioms IntegratorOrderProof.local_defect_bound_paper
#print axioms IntegratorOrderProof.conditional_sixth_order_grid_bound
#print axioms IntegratorOrderProof.NewtonEuler.StageData.transRow_eq
#print axioms IntegratorOrderProof.NewtonEuler.StageData.rotRow_eq
#print axioms IntegratorOrderProof.NewtonEuler.dynamic_rows_vanish
#print axioms IntegratorOrderProof.NewtonEuler.card_dynamic_rows
#print axioms IntegratorOrderProof.Gauss6.B_six
#print axioms IntegratorOrderProof.Gauss6.not_B_seven
#print axioms IntegratorOrderProof.Gauss6.C_three
#print axioms IntegratorOrderProof.Gauss6.D_three
#print axioms IntegratorOrderProof.Gauss6.butcher_order_six_hypotheses
#print axioms IntegratorOrderProof.quadrature_error_bound
#print axioms IntegratorOrderProof.gauss6_quadrature_error
#print axioms IntegratorOrderProof.gauss6_step_defect
#print axioms IntegratorOrderProof.FullVA.Transition.nondynamic_rows_vanish
#print axioms IntegratorOrderProof.FullVA.Transition.reducedCollocation_of_rows
#print axioms IntegratorOrderProof.FullVA.Transition.nondynamic_rows_iff
#print axioms IntegratorOrderProof.norm_le_of_perturbed
#print axioms IntegratorOrderProof.uniform_inverse_of_perturbation
#print axioms IntegratorOrderProof.simplified_newton_residual_decay
