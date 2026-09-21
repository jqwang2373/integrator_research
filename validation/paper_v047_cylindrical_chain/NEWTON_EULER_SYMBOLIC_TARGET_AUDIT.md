# Newton-Euler Symbolic Target Audit

Status: **row-level symbolic targets extracted; dynamic defect proof open**.

This read-only audit turns the 36 `newton_euler_weak_balance` rows into
explicit stage/body/component proof targets. It does not invoke
`run_v047.py`, any v048 runner, or a default `1e-4` campaign.

- Row family: `newton_euler_weak_balance`.
- Dynamic rows: `36`.
- Translational/rotational rows: `18/18`.
- Symbolic target inventory complete: `True`.
- Newton-Euler symbolic defect certificate complete: `False`.
- Stage residual O(h^7) implementation defect proved: `False`.
- Dynamic symbolic oracle complete: `False`.
- Open/closed obligations: `1/5`.
- Obligation coverage matrix complete: `True`.
- Row-obligation links: `180`.
- Rows with complete obligation sets: `36`.
- Runtime source anchors present: `True`.
- Runtime source anchor scope: anchors prove the implemented row-order source locations used by the target audit; they do not prove symbolic algebraic equivalence or the O(h^7) defect bound.

## Target Equation Families

| id | rows | target |
|---|---:|---|
| `translational_balance_identity` | `18` | m_i a_i = f_i^ext + m_i g + f_i^joint(lambda) + f_i^friction |
| `rotational_balance_identity` | `18` | J_i alpha_i + omega_i x J_i omega_i = tau_i^ext + tau_i^joint(lambda) + tau_i^friction |
| `multiplier_wrench_consistency` | `36` | constraint multipliers induce identical generalized forces in constraint and dynamics rows |
| `smooth_force_lift_consistency` | `36` | all force, torque, and friction evaluations use the same smooth FullVA stage lift |
| `gauss_stage_dynamic_defect_rate` | `36` | dynamic rows evaluated on the mathematical smooth lift have O(h^7) defect |
| `symbolic_runtime_row_equivalence` | `36` | implemented runtime row ordering and symbolic target rows are identical |

## Obligation Coverage Matrix

This matrix assigns every dynamic row to its balance-specific proof obligation
and the four shared Newton-Euler consistency obligations. It is a coverage
specification, not a proof certificate.

| obligation | target rows | proof status |
|---|---:|---|
| `translational_balance_identity` | `18` | `closed_by_obligation_gate` |
| `rotational_balance_identity` | `18` | `closed_by_obligation_gate` |
| `multiplier_wrench_consistency` | `36` | `closed_by_obligation_gate` |
| `smooth_force_lift_consistency` | `36` | `closed_by_obligation_gate` |
| `gauss_stage_dynamic_defect_rate` | `36` | `open_not_closed_by_coverage_matrix` |
| `symbolic_runtime_row_equivalence` | `36` | `closed_by_obligation_gate` |

- Coverage matrix complete: `True`.
- Row-obligation links: `180`.
- Rows with complete obligation sets: `36`.
- Proof closure advanced by this matrix: `False`.

## Row Targets

| global row | stage | body | component | block | required identity |
|---:|---:|---:|---|---|---|
| `24` | `0` | `0` | `x` | `translational_newton_balance` | `translational_balance_identity` |
| `25` | `0` | `0` | `y` | `translational_newton_balance` | `translational_balance_identity` |
| `26` | `0` | `0` | `z` | `translational_newton_balance` | `translational_balance_identity` |
| `27` | `0` | `0` | `x` | `rotational_euler_balance` | `rotational_balance_identity` |
| `28` | `0` | `0` | `y` | `rotational_euler_balance` | `rotational_balance_identity` |
| `29` | `0` | `0` | `z` | `rotational_euler_balance` | `rotational_balance_identity` |
| `30` | `0` | `1` | `x` | `translational_newton_balance` | `translational_balance_identity` |
| `31` | `0` | `1` | `y` | `translational_newton_balance` | `translational_balance_identity` |
| `32` | `0` | `1` | `z` | `translational_newton_balance` | `translational_balance_identity` |
| `33` | `0` | `1` | `x` | `rotational_euler_balance` | `rotational_balance_identity` |
| `34` | `0` | `1` | `y` | `rotational_euler_balance` | `rotational_balance_identity` |
| `35` | `0` | `1` | `z` | `rotational_euler_balance` | `rotational_balance_identity` |
| `68` | `1` | `0` | `x` | `translational_newton_balance` | `translational_balance_identity` |
| `69` | `1` | `0` | `y` | `translational_newton_balance` | `translational_balance_identity` |
| `70` | `1` | `0` | `z` | `translational_newton_balance` | `translational_balance_identity` |
| `71` | `1` | `0` | `x` | `rotational_euler_balance` | `rotational_balance_identity` |
| `72` | `1` | `0` | `y` | `rotational_euler_balance` | `rotational_balance_identity` |
| `73` | `1` | `0` | `z` | `rotational_euler_balance` | `rotational_balance_identity` |
| `74` | `1` | `1` | `x` | `translational_newton_balance` | `translational_balance_identity` |
| `75` | `1` | `1` | `y` | `translational_newton_balance` | `translational_balance_identity` |
| `76` | `1` | `1` | `z` | `translational_newton_balance` | `translational_balance_identity` |
| `77` | `1` | `1` | `x` | `rotational_euler_balance` | `rotational_balance_identity` |
| `78` | `1` | `1` | `y` | `rotational_euler_balance` | `rotational_balance_identity` |
| `79` | `1` | `1` | `z` | `rotational_euler_balance` | `rotational_balance_identity` |
| `112` | `2` | `0` | `x` | `translational_newton_balance` | `translational_balance_identity` |
| `113` | `2` | `0` | `y` | `translational_newton_balance` | `translational_balance_identity` |
| `114` | `2` | `0` | `z` | `translational_newton_balance` | `translational_balance_identity` |
| `115` | `2` | `0` | `x` | `rotational_euler_balance` | `rotational_balance_identity` |
| `116` | `2` | `0` | `y` | `rotational_euler_balance` | `rotational_balance_identity` |
| `117` | `2` | `0` | `z` | `rotational_euler_balance` | `rotational_balance_identity` |
| `118` | `2` | `1` | `x` | `translational_newton_balance` | `translational_balance_identity` |
| `119` | `2` | `1` | `y` | `translational_newton_balance` | `translational_balance_identity` |
| `120` | `2` | `1` | `z` | `translational_newton_balance` | `translational_balance_identity` |
| `121` | `2` | `1` | `x` | `rotational_euler_balance` | `rotational_balance_identity` |
| `122` | `2` | `1` | `y` | `rotational_euler_balance` | `rotational_balance_identity` |
| `123` | `2` | `1` | `z` | `rotational_euler_balance` | `rotational_balance_identity` |

## Boundary

The full formula-row oracle and AD-Jacobian oracle are runtime evidence.
This audit adds row-level symbolic targets, but it does not prove the
`O(h^7)` dynamic defect or close the independent symbolic oracle.

Validator: `validate_newton_euler_symbolic_target_audit.py`.
