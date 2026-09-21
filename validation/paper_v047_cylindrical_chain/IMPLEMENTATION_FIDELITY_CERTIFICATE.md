# Implementation Fidelity Certificate

This certificate is a read-only source trace for the accepted cylindrical-chain
`Gauss6/FullVA` implementation path. Its purpose is to narrow the proof gap
between the manuscript's mathematical residual and the code path used to
generate the reported artifacts.

It does not claim complete source-paper TFE residual reproduction, and it does
not mark `full_tfe_stage_replacement` as accepted.

## Source Boundary

Authoritative source:

- `../../numerics/v047_cylindrical_chain_pipeline/run_v047.py`

Accepted residual and AD symbols:

- `residual_cylindrical_chain`
- `R_VALUE = jax.jit(residual_cylindrical_chain)`
- `R_JAC = jax.jit(jax.jacfwd(residual_cylindrical_chain, argnums=0))`

Static row-layout constants:

- `N_BODIES = 2`
- `N_JOINTS = 2`
- `N_STAGES = 3`
- `BODY_SIZE = 18`
- `LAMBDA_SIZE = 4`
- `STAGE_SIZE = N_BODIES * BODY_SIZE + N_JOINTS * LAMBDA_SIZE = 44`
- `DIM = N_STAGES * STAGE_SIZE = 132`

## Row-Family Map

The accepted cylindrical-chain residual uses the following 44-row per-stage
layout, repeated for three Gauss stages.

| Code row-family symbol | Offset | Width | Total rows | Source tokens in `residual_cylindrical_chain` |
| --- | ---: | ---: | ---: | --- |
| `translational_position_weak_defect` | 0 | 6 | 18 | `pvel.append`, `rel_vel`, `r_coll_axis` |
| `rotational_lie_position_weak_defect` | 6 | 6 | 18 | `u_block.append`, `axis_rate`, `spin_coll_axis` |
| `translational_velocity_weak_defect` | 12 | 6 | 18 | `pacc.append`, `rel_acc`, `v_coll_axis` |
| `angular_velocity_weak_defect` | 18 | 6 | 18 | `w_block.append`, `axis_acc`, `spin_acc_coll_axis` |
| `newton_euler_weak_balance` | 24 | 12 | 36 | `dyn.extend`, `trans`, `rot`, `brown_mcphee_scalar_jax` |
| `lower_pair_index3_weak_constraints` | 36 | 8 | 24 | `constraints.append`, `rel_point`, `axis_res` |

The layout is declared in `STAGE_FUNCTIONAL_BLOCK_LAYOUT`. The helper
`stage_row_family_slices_np()` turns this layout into row slices, and
`stage_variable_family_slices_np()` records the corresponding stage unknown
families.

## Manuscript Correspondence

The manuscript's accepted one-step map is `R_G6FVA(q_n,v_n,a_n,Z;h)=0`.
For the cylindrical-chain code path, this symbol corresponds to
`residual_cylindrical_chain`. The proof-level row families in the manuscript
map to the implementation as follows:

| Manuscript row concept | Implementation evidence |
| --- | --- |
| Stage kinematic defects | `pvel`, `u_block`, `pacc`, and `w_block` assembled with Gauss matrix `A[si, sj]`. |
| Lie retraction and local angular velocity | `compose_right_quat_jax_safe` and `right_jacobian_inverse_apply_jax_safe`. |
| Lower-pair position, velocity, and acceleration vocabulary | `joint_kinematics_jax` returns `rel_point`, `rel_vel`, `rel_acc`, `axis_res`, `axis_rate`, and `axis_acc`. |
| Newton-Euler balance with Brown-McPhee friction | `dyn.extend([trans, rot])` with `brown_mcphee_scalar_jax`. |
| Dense reference automatic differentiation | `R_JAC = jax.jit(jax.jacfwd(residual_cylindrical_chain, argnums=0))`. |

## Remaining Gap

This certificate is a static source-identity audit. It proves that the paper's
accepted residual boundary is tied to one JAX residual function and one AD
Jacobian path, and it records the row-family layout used by that function.

The companion runtime oracle
\artifact{DYNAMIC_ROW_ORACLE_GATE.md} /
\artifact{DYNAMIC_ROW_ORACLE_GATE.json} imports `run_v047.py`, evaluates
`residual_cylindrical_chain` and `R_JAC` on a canonical finite smooth-state
probe, checks that the six row families partition the 132 residual rows
without overlap, and verifies that `R_INDEPENDENT_STAGE_FUNCTIONAL_BLOCKS`
matches the weighted residual row families on a deterministic small stage
vector. That runtime row and block-functional check is stronger than this
static certificate. The same dynamic gate now also provides a partial
independent formula-row oracle for 96 non-dynamic rows and a full independent
formula-row oracle for all 132 runtime formula rows, including
`newton_euler_weak_balance`. The formula rows are reassembled from
formula-level expressions and checked against the accepted residual. The same
gate differentiates the independent formula-row vector with `jax.jacfwd` and
checks the resulting 132 by 132 matrix against the accepted `R_JAC` path on
three deterministic probes. This is the multi-probe formula-row AD Jacobian
oracle. It closes the runtime formula-row and finite-probe AD Jacobian coverage
gap, but it is still not an independent symbolic-equivalence proof. In the older
proof-ledger wording, it is not a dynamic symbolic-equivalence proof. A
separate path audit, \artifact{IMPLEMENTATION_PATH_AUDIT.md} /
\artifact{IMPLEMENTATION_PATH_AUDIT.json}, checks
`implementation_path_check_for_132_row_residual=true` by tracing the accepted
path `residual_cylindrical_chain -> R_VALUE/R_JAC -> gauss_step ->
integrate/run_case -> summary_v047.json` without invoking `run_v047.py`, a
v048 runner, or a default `1e-4` campaign. This closes the narrow source-path
traceability item but not the symbolic residual-defect proof. A
stronger future certificate must evaluate each AD-expanded row family against
independently generated symbolic rows and establish the implementation defect
needed by the proof as `O(h^7)`. The CMAME readiness gate therefore remains false until this
implementation-fidelity evidence is paired with fair baselines and the scaled
nonlinear-solver policy.

## Validator

Read-only static check:

```bash
../../.venv_sbel/bin/python validate_implementation_fidelity_certificate.py
../../.venv_sbel/bin/python validate_implementation_path_audit.py
../../.venv_sbel/bin/python validate_dynamic_row_oracle_gate.py
```

Expected status:

- `implementation_fidelity_certificate=PASS`
- `accepted_residual=residual_cylindrical_chain`
- `accepted_jacobian=R_JAC_jacfwd_argnums0`
- `implementation_path_audit=PASS`
- `implementation_path_check_for_132_row_residual=True`
- `dynamic_row_oracle_gate=PASS`
- `block_functional_crosscheck=PASS`
- `full_formula_row_count=132`
- `formula_row_ad_jacobian_oracle=PASS`
- `formula_row_ad_jacobian_probe_count=3`
- `full_tfe_stage_replacement=False`
