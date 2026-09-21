# Proof Numerical Scale Audit

Status: **finite-run scale diagnostic, not an asymptotic solver proof**

This audit reads the existing
`v047_cylindrical_chain_pipeline/results/cylindrical_chain_convergence.csv`
smooth rows. It does not run `run_v047.py`, does not run any v048 numerical
runner, and does not require a default `1e-4` campaign.

## Read-Only Policy

- accepted method: `Gauss6/FullVA`
- case: `cylindrical_smooth`
- step sizes: `0.04`, `0.02`, `0.01`
- reference step: `0.005`
- default step policy: `coarse_first_no_default_1e-4`
- `default_1e-4_required=false`
- `heavy_numerical_run_invoked=false`
- `run_v047_invoked=false`

## What The Existing Rows Support

The projected smooth trajectory gives global position and velocity fits
`7.160828003417387` and `7.066182539651858` over the recorded three-step
window. Since the proof-level theorem only claims global order six, these
finite-window slopes support at least sixth-order smooth behavior; they are
not a seventh-order theorem.

For endpoint closure, the CSV records raw endpoint position and velocity
constraint monitors with global-fit orders `5.985100758394371` and
`6.072290794930567`. Their h^6-normalized ratios remain bounded on the three
recorded steps:

| quantity | h=0.04 | h=0.02 | h=0.01 |
| --- | ---: | ---: | ---: |
| projected position error / h^6 | 43.00081482394556 | 28.721642129670443 | 8.601785083254413 |
| projected velocity error / h^6 | 2459.1612968083577 | 461.5433184630342 | 560.894478179553 |
| raw endpoint position constraint / h^6 | 0.001436306128294646 | 0.001433077272191527 | 0.0014662811475967602 |
| raw endpoint velocity constraint / h^6 | 0.0330637492139094 | 0.03022601889413138 | 0.029910846414046365 |

This is consistent with a global sixth-order error budget and with the local
O(h^7) endpoint-closure budget used in Lemma 1 of the manuscript, because
global accumulation over a fixed interval reduces the visible power by one.
These monitor rows are not, by themselves, the theorem-level local endpoint
functional \(E\) in Lemma 1: the manuscript defines \(E\) as the same-branch
velocity-level/KKT closure subsystem corrected by \(\mathcal C_h\), while the
raw position defect is a separate diagnostic monitor. The finite endpoint rows
therefore support scale consistency for the endpoint part of the local O(h^7)
budget, but do not discharge the retained P2 endpoint raw-defect/right-inverse
hypothesis.

## What It Does Not Prove

The convergence CSV does not record per-step Newton residual norms or a
solver policy of the form `eta_h <= c_eta h^7`. Therefore this audit keeps:

- `eta_h_O_h7_solver_policy_evidence=false`
- `fixed_tolerance_runs_are_asymptotic_proof=false`
- `stage_residual_O_h7_implementation_defect_proved_by_this_audit=false`
- `dynamic_symbolic_oracle_complete=false`

This does not contradict the separate proof-closure manifest: the active
direct 132-row implementation residual-defect route is closed there. It says
only that the convergence CSV is not itself an implementation-defect proof,
and it does not discharge the theorem-level solver-scale or compact-tube
interfaces.

## Validator

Run:

```bash
../../.venv_sbel/bin/python validate_proof_numerical_scale_audit.py
```

Expected markers:

- `proof_numerical_scale_audit=PASS`
- `finite_run_error_scale_supports_order_six=True`
- `eta_h_O_h7_solver_policy_evidence=False`
- `stage_residual_O_h7_implementation_defect_proved_by_this_audit=False`
- `default_1e-4=False`
