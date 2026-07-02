# Kinematic Row Defect Certificate

Status: **PARTIAL PROOF CERTIFICATE - 96 ROWS - NOT SUBMISSION READY**

This certificate records a narrow proof-progress item for the accepted
`Gauss6/FullVA` residual. It does not run `run_v047.py`, does not invoke any
v048 numerical runner, and does not require a default `1e-4` campaign.

## Scope

The certificate applies only to the non-dynamic row families that already have
independent formula-row coverage in `DYNAMIC_ROW_ORACLE_GATE.md`:

| Row family | Rows | Proof role |
| --- | ---: | --- |
| `translational_position_weak_defect` | 18 | Collocation lift row. |
| `rotational_lie_position_weak_defect` | 18 | Lie-algebra collocation lift row. |
| `translational_velocity_weak_defect` | 18 | Velocity collocation lift row. |
| `angular_velocity_weak_defect` | 18 | Angular-velocity collocation lift row. |
| `lower_pair_index3_weak_constraints` | 24 | Position, velocity, and acceleration constraint rows. |

Total certified proof-scope rows: `96`.

The excluded family is `newton_euler_weak_balance` with `36` rows. Those rows
remain part of the full 132-row runtime formula oracle, but their symbolic
defect proof is still open.

## Proof Statement

Let the smooth accepted-path FullVA lift be the local collocation object used in
Lemma `FullVA stage-row lift consistency` in the CMAME manuscript. On this lift:

1. The four collocation row families vanish by the defining Gauss collocation
   integral identities in the accepted local variables.
2. The lower-pair position, velocity, and acceleration rows vanish by the
   smooth constrained-branch identities `Phi=0`, `dot Phi=0`, and
   `ddot Phi=0`.
3. The formula-row oracle already checks that these 96 formula rows match the
   accepted runtime residual row families on the deterministic implementation
   probe.

Therefore these 96 non-dynamic rows satisfy the theorem's local residual-defect
budget on the smooth lift. This is stronger than `O(h^7)` for those row
families on the mathematical lift, but it is only a partial certificate because
the dynamic Newton-Euler weak-balance rows are not included.

## Boundary

This certificate does not prove:

- `stage_residual_O_h7_implementation_defect_proved` for all 132 rows;
- `dynamic_symbolic_oracle_complete`;
- `eta_h_O_h7_solver_policy_evidence`;
- `full_tfe_stage_replacement`;
- external same-test superiority;
- submission readiness.

It should be read as proof progress for B1/B3, not as blocker closure.

## Validator

Run:

```bash
../.venv_sbel/bin/python validate_kinematic_row_defect_certificate.py
```

Expected markers:

- `kinematic_row_defect_certificate=PASS`
- `certified_row_count=96`
- `excluded_row_family=newton_euler_weak_balance`
- `partial_stage_defect_certificate=True`
- `stage_residual_O_h7_implementation_defect_proved=False`
- `dynamic_symbolic_oracle_complete=False`
- `default_1e-4=False`
- `run_v047_invoked=False`
- `v048_runner_invoked=False`
- `submission_ready=False`
