# Proof Solver Scaled-Tolerance Trajectory Probe

Status: `finite_scaled_tolerance_trajectory_probe_recorded_not_theorem_closure`.

This finite short-trajectory probe imports the accepted v047 residual
functions and applies `eta_h = c_eta h^7` at every smooth trajectory
step. It does not invoke `run_v047.py`, does not run a default `1e-4`
campaign, and does not close the optional primitive/global dynamic
symbolic lane; active direct PC2 remains closed by the separate
D5 direct-substitution route.

- Probe schema: `proof-solver-scaled-tolerance-trajectory-probe-v1`.
- Case: `cylindrical_smooth`.
- h values: `[0.04, 0.02, 0.01, 0.005]`.
- t_final: `0.08`.
- c_eta: `10000.0`.
- Rows ok: `4/4`.
- Total trajectory steps checked: `30`.
- Max final residual / h^7: `2.1089078604575462e+02`.
- Scaled trajectory policy exercised: `True`.
- Theorem-level solver proof closed: `False`.
- eta_h_O_h7_solver_policy_evidence: `False`.
- default_1e-4_required: `False`.
- run_v047_invoked: `False`.

| h | steps | eta target | max residual | max residual / h^7 | Newton iters | status |
|---:|---:|---:|---:|---:|---:|---|
| 0.04 | 2 | 1.638400e-06 | 6.392846e-14 | 3.901884e-04 | 12 | ok |
| 0.02 | 4 | 1.280000e-08 | 1.286348e-14 | 1.004959e-02 | 24 | ok |
| 0.01 | 8 | 1.000000e-10 | 1.523472e-14 | 1.523472e+00 | 48 | ok |
| 0.005 | 16 | 7.812500e-13 | 1.647584e-14 | 2.108908e+02 | 96 | ok |

Interpretation: this is stronger than the one-step finite probe because
the scaled stopping rule is exercised over a short trajectory. It is
still a finite P6 diagnostic record, not solver-policy closure, not a
theorem-level scaled tolerance sweep over every reported trajectory and not a substitute
for the optional primitive/global dynamic symbolic lane.

Validator: `validate_proof_solver_scaled_tolerance_trajectory_probe.py`.
