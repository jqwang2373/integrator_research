# Proof Solver Scale Audit

Status: **SUMMARY-LEVEL SOLVER RESIDUALS RECORDED - NOT A SCALED ETA_H PROOF**

This read-only audit re-checks existing residual-scale fields in
`../../numerics/v047_cylindrical_chain_pipeline/results/summary_v047.json`. It does not
invoke `run_v047.py`, v048 numerical runners, or any default `1e-4` campaign.
Here `submission_ready=false` is scoped to the solver-scale/global `eta_h`
proof boundary, not to the separate narrowed-claim package decision.

## Recorded Residuals

The existing summary records the following residual-scale quantities:

- smooth projected reference `max_linear_residual_norm`:
  `2.800513564816292e-13`
- smooth raw-endpoint reference `max_linear_residual_norm`:
  `2.800513564816292e-13`
- sharp projected reference `max_linear_residual_norm`:
  `3.7018688740777353e-13`
- sharp raw-endpoint reference `max_linear_residual_norm`:
  `3.7018688740777353e-13`
- endpoint-KKT smooth reference `max_linear_residual_norm`:
  `4.3384560428137684e-14`
- endpoint-KKT sharp reference `max_linear_residual_norm`:
  `4.932067561463195e-14`
- single-pendulum driven FullVA `max_stage_residual_norm`:
  `9.187733067060637e-13`
- single-pendulum absolute FullVA `max_stage_residual_norm`:
  `3.663986665284353e-12`

These are finite-run residual records. They show that the solved systems reach
small residuals, but they are not a proof-level scaled solver-tolerance sweep.

## Eta-H Scale Diagnostic

For a sixth-order asymptotic theorem, the inexact Newton contribution must be
controlled at local scale `eta_h <= c_eta h^7`. Using the smooth projected reference
linear residual as a fixed residual scale gives:

| `h` | residual / `h^7` |
| --- | ---: |
| `0.04` | `0.0017092978300880684` |
| `0.02` | `0.21879012225127276` |
| `0.01` | `28.005135648162913` |
| `0.005` | `3584.657362964853` |

Using the endpoint-KKT smooth reference linear residual gives:

| `h` | residual / `h^7` |
| --- | ---: |
| `0.04` | `0.000264798342456895` |
| `0.02` | `0.03389418783448256` |
| `0.01` | `4.3384560428137675` |
| `0.005` | `555.3223734801622` |

The increasing fine-step ratios are exactly why the manuscript keeps
`eta_h_O_h7_solver_policy_evidence=false`: the current records are fixed-scale
finite-run data, not an asymptotic `eta_h <= c_eta h^7` policy certificate.

## Finite Scaled-Tolerance Probe

The finite scaled-tolerance probe in `PROOF_SOLVER_SCALED_TOLERANCE_PROBE.md`,
`PROOF_SOLVER_SCALED_TOLERANCE_PROBE.json`, and
`PROOF_SOLVER_SCALED_TOLERANCE_PROBE.csv` adds a finite executable probe for
the solver-scale condition. It imports the accepted v047 residual functions
and solves one smooth initial step with the residual stopping target
`eta_h = c_eta h^7`, using `c_eta=10000.0` and `h=[0.04,0.02,0.01,0.005]`.

The probe records `4/4` ok rows and a maximum final residual divided by `h^7`
of `127.58372278641149`, below the imposed `c_eta` bound. This is useful
solver-policy diagnostic support, but it is still a finite probe, not a theorem-level
scaled tolerance sweep over every reported trajectory and not a substitute for
the retained compact-tube solver policy. The optional primitive dynamic
symbolic-defect certificate remains outside the active direct proof route.

## Finite Scaled-Tolerance Trajectory Probe

The finite scaled-tolerance trajectory probe in
`PROOF_SOLVER_SCALED_TOLERANCE_TRAJECTORY_PROBE.md`,
`PROOF_SOLVER_SCALED_TOLERANCE_TRAJECTORY_PROBE.json`, and
`PROOF_SOLVER_SCALED_TOLERANCE_TRAJECTORY_PROBE.csv` applies the same
`eta_h = c_eta h^7` stopping target over a short smooth trajectory. It checks
`h=[0.04,0.02,0.01,0.005]`, `t_final=0.08`, and `c_eta=10000.0`.

The trajectory probe records `4/4` ok rows, `30` short-trajectory steps, and a
maximum final residual divided by `h^7` of `210.89078604575462`, below the
imposed `c_eta` bound. This is a stronger finite solver-policy diagnostic
record than the one-step probe, but it is not a theorem-level scaled tolerance
sweep over every reported trajectory and not a substitute for the retained
compact-tube solver policy. It also does not promote the optional primitive
dynamic symbolic route.

## Finite Tolerance-Regime Sweep

The finite tolerance-regime sweep in
`PROOF_SOLVER_TOLERANCE_REGIME_SWEEP.md`,
`PROOF_SOLVER_TOLERANCE_REGIME_SWEEP.json`, and
`PROOF_SOLVER_TOLERANCE_REGIME_SWEEP.csv` compares fixed `1e-10`,
`c h^7`, and `c h^8` residual targets on the same smooth short trajectory.
It uses `h=[0.04,0.02,0.01,0.005]`, `t_final=0.08`, and a local reference
with `h=0.0025` and residual target `1e-13`.

All `12` policy/step-size rows converge over `90` checked trajectory steps.
The fixed `1e-10` row records position/velocity orders
`6.946347411176867/6.608089993735075`; the `c h^7` row records the same
orders, and the `c h^8` row records
`6.946365976765468/6.608137477881583`. This answers the finite-window
tolerance comparison requested by the proof review. The two shrinking-target
policies are recorded separately as
`finite_h_scaled_tolerance_sweep_recorded=true`, with `8` h-scaled rows, `60`
checked h-scaled trajectory steps, and a position/velocity order floor of
`6.946347411176867/6.608089993735075`. It does not change the asymptotic
proof boundary: `finite_tolerance_regime_sweep_recorded=true`, while
`theorem_level_scaled_tolerance_sweep_recorded=false` and
`eta_h_O_h7_solver_policy_evidence=false` remain in force.
Here `finite_h_scaled_tolerance_sweep_recorded=true` records finite
h-scaled diagnostics only; `theorem_level_scaled_tolerance_sweep_recorded=false` means
the uniform all-transition scaled solver-policy closure is still open.
This is a finite-window tolerance comparison only; it does not instantiate P6
or close a scaled-tolerance proof under a uniform all-transition policy for
the reported trajectory.

## Proof Boundary

- `submission_ready_scope=solver_scale_global_eta_h_boundary_not_narrowed_claim_package_decision`
- `solver_scale_audit_scope=finite_solver_scale_diagnostic_and_theorem_level_eta_h_boundary`
- `narrowed_claim_b4_b6_b7_statuses=closed/closed/closed`
- `global_submission_boundaries_retained=full_source_policy_package_ready,theorem_level_eta_h_solver_policy_evidence,closed_residual_to_error_theorem_for_mechanism_rows`
- `summary_level_solver_residuals_recorded=true`
- `convergence_csv_newton_residual_norm_recorded=false`
- `finite_scaled_tolerance_probe_recorded=true`
- `finite_scaled_tolerance_trajectory_probe_recorded=true`
- `finite_tolerance_regime_sweep_recorded=true`
- `finite_h_scaled_tolerance_sweep_recorded=true`
- `fixed_tolerance_window_comparison_only=true`
- `fixed_tolerance_does_not_instantiate_P6=true`
- `theorem_level_scaled_tolerance_sweep_recorded=false`
- `eta_h_O_h7_solver_policy_evidence=false`
- `fixed_tolerance_runs_are_asymptotic_proof=false`
- `stage_residual_O_h7_implementation_defect_proved_by_this_audit=false`
- `dynamic_symbolic_oracle_complete=false`
- `default_1e-4_required=false`
- `run_v047_invoked=false`
- `submission_ready=false`

## Remaining Gate Scope

This audit records finite solver-scale diagnostics for the `eta_h <= c_eta h^7`
condition without promoting those diagnostics to a theorem-level solver-policy
certificate. The narrowed-claim B4/B6/B7 package blockers are closed elsewhere,
so the remaining solver-scale gate is the global proof boundary, not a new
narrowed-claim package decision.

- `b4_b6_b7_closed_elsewhere_under_narrowed_claim=true`
- `finite_solver_scale_diagnostic_recorded=true`
- `eta_h_theorem_condition_retained=true`
- `eta_h_O_h7_solver_policy_evidence=false`
- `theorem_level_scaled_tolerance_sweep_recorded=false`
- `fixed_tolerance_runs_are_asymptotic_proof=false`
- `stage_residual_O_h7_implementation_defect_proved_by_this_audit=false`
- `dynamic_symbolic_oracle_complete=false`
- `remaining_gate_global_submission_boundaries_retained=full_source_policy_package_ready,theorem_level_eta_h_solver_policy_evidence,closed_residual_to_error_theorem_for_mechanism_rows`

## Validator

Run:

```bash
../../.venv_sbel/bin/python validate_proof_solver_scale_audit.py
../../.venv_sbel/bin/python validate_proof_solver_scaled_tolerance_probe.py
../../.venv_sbel/bin/python validate_proof_solver_scaled_tolerance_trajectory_probe.py
../../.venv_sbel/bin/python validate_proof_solver_tolerance_regime_sweep.py
```

Expected markers:

- `proof_solver_scale_audit=PASS`
- `summary_level_solver_residuals_recorded=True`
- `finite_tolerance_regime_sweep_recorded=True`
- `scaled_tolerance_sweep_recorded=False`
- `eta_h_O_h7_solver_policy_evidence=False`
- `default_1e-4=False`
- `run_v047_invoked=False`
- `submission_ready=False`
