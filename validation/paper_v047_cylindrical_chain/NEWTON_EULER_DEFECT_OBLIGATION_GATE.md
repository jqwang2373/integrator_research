# Newton-Euler Defect Obligation Gate

Status: **D5 SYMBOLIC/PRIMITIVE ROUTE OPEN; ACTIVE DIRECT PC2 CLOSED - NOT SUBMISSION READY**

This gate decomposes the Newton-Euler symbolic/primitive certificate route for
the accepted `Gauss6/FullVA` residual. The active direct-substitution PC2
route is closed by `D5_DYNAMIC_DIRECT_SUBSTITUTION_CERTIFICATE.md/json`; this
gate intentionally keeps the global symbolic/primitive route open and does not
complete the dynamic symbolic oracle, invoke `run_v047.py`, or require a
default `1e-4` campaign.

## Scope

| Row family | Rows | Decomposition |
| --- | ---: | --- |
| `newton_euler_weak_balance` | 36 | Three stages, two bodies, six balance rows per body-stage. |

The 36 rows are decomposed into:

- `translational_newton_balance`: 18 rows;
- `rotational_euler_balance`: 18 rows.

`NEWTON_EULER_BALANCE_IDENTITY_AUDIT.md/json` now closes the D1/D2
source-level balance identities for these rows.  The remaining theorem
symbolic/primitive route gap is D5: proving the lifted-stage dynamic residual
by the global primitive/Taylor certificate rather than the active direct
substitution route.
`NEWTON_EULER_SYMBOLIC_TARGET_AUDIT.md/json` remains the row-target
inventory for all 36 Newton-Euler weak-balance rows.

## Open Obligations

| Obligation | Required proof |
| --- | --- |
| `gauss_stage_dynamic_defect_rate` | primitive/Taylor or global symbolic-certificate route for the dynamic-row residual; the active direct D5 substitution route is recorded separately and is closed. |

## Closed Sub-Obligations

| Obligation | Closure evidence |
| --- | --- |
| `translational_balance_identity` | NEWTON_EULER_BALANCE_IDENTITY_AUDIT.md/json closes: source-level equality between each implemented translational dynamic row and the accepted weak linear-momentum balance; the active direct D5 route is closed, while the symbolic/primitive certificate route remains open. |
| `rotational_balance_identity` | NEWTON_EULER_BALANCE_IDENTITY_AUDIT.md/json closes: source-level equality between each implemented rotational dynamic row and the accepted body-frame angular-momentum balance; the active direct D5 route is closed, while the symbolic/primitive certificate route remains open. |
| `multiplier_wrench_consistency` | NEWTON_EULER_VIRTUAL_WORK_WRENCH_AUDIT.md/json closes: row-expanded lower-pair multiplier virtual-work identity for the implemented cylindrical-chain force and axis-torque sites. |
| `smooth_force_lift_consistency` | SMOOTH_FORCE_LIFT_CERTIFICATE.md/json closes: smooth Brown-McPhee force/friction and regularized normal-load lift are C7 with bounded derivatives on the accepted compact smooth proof tube. |
| `symbolic_runtime_row_equivalence` | NEWTON_EULER_ROW_ORDERING_SCALING_AD_AUDIT.md/json closes: independent row-ordering, residual-scaling, and accepted AD-binding equivalence for the 36 implemented Newton-Euler dynamic rows. |

Symbolic/primitive-route open obligation count: `1`.
Active direct PC2 closed: `True`.
Active direct dynamic zero residual rows: `36`.
Closed obligation count: `5`.
Closed obligation ids: `translational_balance_identity, rotational_balance_identity, multiplier_wrench_consistency, smooth_force_lift_consistency, symbolic_runtime_row_equivalence`.
Symbolic target inventory complete: `true`.

## Boundary

This gate only narrows the remaining symbolic/primitive proof work. It does not prove:

- `newton_euler_symbolic_defect_certificate_complete`;
- `symbolic_primitive_stage_residual_O_h7_certificate_complete`;
- `dynamic_symbolic_oracle_complete`;
- `eta_h_O_h7_solver_policy_evidence`;
- `full_tfe_stage_replacement`;
- external same-test superiority;
- submission readiness.

The theorem therefore uses the direct D5 substitution certificate for active
PC2 and remains conditional under retained P1, P2, and P3 theorem
interfaces, the separate P6 solver-scale interface, and the P4
binding convention, with P7 residual-to-error nonpromotion recorded
elsewhere.

## Execution Policy

- `default_1e-4_required=false`
- `run_v047_invoked=false`
- `v048_runner_invoked=false`
- `heavy_numerical_run_invoked=false`

## Validator

Run:

```bash
../../.venv_sbel/bin/python validate_newton_euler_defect_obligation_gate.py
```

Expected markers:

- `newton_euler_defect_obligation_gate=PASS`
- `row_family=newton_euler_weak_balance`
- `dynamic_row_count=36`
- `symbolic_primitive_open_obligation_count=1`
- `active_direct_pc2_closed=True`
- `closed_obligation_count=5`
- `symbolic_primitive_stage_residual_O_h7_certificate_complete=False`
- `dynamic_symbolic_oracle_complete=False`
- `submission_ready=False`
