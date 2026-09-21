# Implementation Path Audit

Status: **READ-ONLY STATIC CODE PATH CHECKED - NOT SYMBOLIC PROOF**

This audit closes the narrow `implementation_path_check_for_132_row_residual`
piece of B1. It does not run `run_v047.py`, does not invoke any v048 runner,
and does not launch a default `1e-4` campaign.

## Execution Policy

- audit type: `read_only_static_audit`
- default policy: `coarse_first_no_default_1e-4`
- strict public-policy `1e-4`: `opt_in_only`
- `default_1e-4_required=false`
- `heavy_numerical_run_invoked=false`
- `run_v047_invoked=false`
- `v048_runner_invoked=false`
- `submission_ready=false`

## Accepted Code Path

The accepted cylindrical-chain method path is:

1. `residual_cylindrical_chain`
2. `R_VALUE = jax.jit(residual_cylindrical_chain)`
3. `R_JAC = jax.jit(jax.jacfwd(residual_cylindrical_chain, argnums=0))`
4. `gauss_step(..., solver="dense_jacfwd_csr", ...)` evaluates `R_VALUE`
   and assembles the dense Newton Jacobian with `R_JAC`
5. `integrate` calls `gauss_step` at each trajectory step
6. `run_case` calls `integrate` for the accepted dense and sparse runtime
   comparison paths
7. `main` writes `results/summary_v047.json` with `model.dimension = DIM`

This is the implementation path for the accepted `Gauss6/FullVA` 132-row
residual boundary. It is separate from the many diagnostic endpoint-TFE
candidate residuals in `run_v047.py`.

## Shape And Row Contract

- `N_BODIES=2`
- `N_JOINTS=2`
- `N_STAGES=3`
- `BODY_SIZE=18`
- `LAMBDA_SIZE=4`
- `STAGE_SIZE=44`
- `DIM=132`

The 44 rows per stage are:

| Row family | Offset | Width | Total rows |
| --- | ---: | ---: | ---: |
| `translational_position_weak_defect` | 0 | 6 | 18 |
| `rotational_lie_position_weak_defect` | 6 | 6 | 18 |
| `translational_velocity_weak_defect` | 12 | 6 | 18 |
| `angular_velocity_weak_defect` | 18 | 6 | 18 |
| `newton_euler_weak_balance` | 24 | 12 | 36 |
| `lower_pair_index3_weak_constraints` | 36 | 8 | 24 |

## Claim Boundary

This audit is stronger than a prose statement because it checks that the
accepted residual/Jacobian symbols are on the code path used by the trajectory
integrator and summary writer. It is still weaker than a symbolic proof.

What this audit supports:

- `implementation_path_check_for_132_row_residual=true`
- `runtime_formula_row_oracle_complete=true`
- `runtime_ad_oracle_complete=true`

What remains open:

- `independent_symbolic_row_oracle_complete=false`
- `stage_residual_O_h7_implementation_defect_proved_by_this_static_path_audit=false`
- `eta_h_O_h7_solver_policy_evidence=false`
- `full_tfe_stage_replacement=false`
- `external_superiority_claim=false`

This static path audit identifies the submitted residual/Jacobian route; it is
not the direct 132-row substitution certificate. The active direct
implementation-defect proof is recorded separately in
`PROOF_CLOSURE_MANIFEST.md/json`.

## Validator

Run:

```bash
../../.venv_sbel/bin/python validate_implementation_path_audit.py
```

Expected markers:

- `implementation_path_audit=PASS`
- `accepted_residual=residual_cylindrical_chain`
- `accepted_jacobian=R_JAC_jacfwd_argnums0`
- `implementation_path_check_for_132_row_residual=True`
- `stage_rows=132`
- `default_1e-4=False`
- `run_v047_invoked=False`
- `v048_runner_invoked=False`
- `submission_ready=False`
