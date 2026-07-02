# Dynamic Row Oracle Gate

Status: **RUNTIME ROW AND BLOCK-FUNCTIONAL ORACLE PASSABLE - SYMBOLIC ORACLE OPEN**

Plain status: runtime row and block-functional oracle passable; symbolic
oracle open.

This gate is a lightweight runtime implementation-fidelity check for the
accepted cylindrical-chain `Gauss6/FullVA` residual. It imports
`../v047_cylindrical_chain_pipeline/run_v047.py`, constructs the canonical
smooth cylindrical-chain initial state, evaluates the accepted residual at a
finite canonical stage vector, evaluates the dense AD Jacobian path, and
cross-checks the six weighted block-functional outputs against the accepted
residual row families.

This is stronger than the static source-identity certificate because it
executes the row layout, AD path, and block-functional decomposition. It is
still not the final independent symbolic row oracle for the symbolic/primitive
lane. Later direct-substitution sidecars close the accepted direct stage-row
residual route separately; this runtime gate is not a dynamic symbolic-
equivalence proof and does not control the current global direct proof status.

## Runtime Probe

- accepted residual: `residual_cylindrical_chain`
- accepted Jacobian: `R_JAC = jax.jacfwd(residual_cylindrical_chain, argnums=0)`
- canonical case: smooth cylindrical chain with `stribeck_velocity=0.50`
- step size: `h=0.04`
- canonical stage vector: zero vector in the accepted 132-dimensional stage
  unknown space
- residual shape: `(132,)`
- Jacobian shape: `(132,132)`
- residual finite: true
- Jacobian finite: true

## Runtime Block-Functional Cross-Check

The validator also evaluates `R_INDEPENDENT_STAGE_FUNCTIONAL_BLOCKS` on a
deterministic small sine stage vector. For each of the six row families, it
checks

```text
block_family_i = sqrt(h b_i) * accepted_residual_family_i
```

stage by stage, where `b_i` are the three Gauss weights. The accepted tolerance
is `1e-10`; the expected validator marker is
`block_functional_crosscheck=PASS`, with a reported max weighted-family
mismatch. This is the runtime block-functional cross-check.

This block-functional check is a Gauss6-equivalent decomposition of the
accepted residual. It does not prove that the residual equals an independently
generated symbolic TFE row formula, and it does not make
`full_tfe_stage_replacement` true.

## Formula-Row Oracles

The validator now also reassembles five row families from formula-level
kinematic and lower-pair constraint expressions, without reading those values
back from residual slices or from the weighted block-functional path. The
checked families are:

- `translational_position_weak_defect`;
- `rotational_lie_position_weak_defect`;
- `translational_velocity_weak_defect`;
- `angular_velocity_weak_defect`;
- `lower_pair_index3_weak_constraints`.

Together these cover 96 non-dynamic rows on the same deterministic small sine
stage vector. The accepted tolerance is `1e-10`, and the expected validator
marker is `partial_formula_row_oracle=PASS`, with a reported max formula-row
mismatch. This is a partial independent formula-row oracle. It narrows the B1
implementation gap.

The validator now extends the same formula-level reassembly to
`newton_euler_weak_balance`. The full independent formula-row oracle covers all
132 runtime formula rows:

- 96 kinematic/lower-pair rows;
- 36 Newton--Euler weak-balance rows.

The expected validator markers are `full_formula_row_oracle=PASS`,
`full_formula_row_count=132`, and a reported max full formula-row mismatch.
This closes the runtime formula-row coverage gap for the accepted cylindrical
chain residual.

The validator also differentiates the independent formula-row vector with
`jax.jacfwd` and compares the resulting 132 by 132 matrix with the accepted
`R_JAC` path after applying the same row-family-major ordering. The expected
marker is `formula_row_ad_jacobian_oracle=PASS`, with a reported max
formula-row Jacobian mismatch. This is the formula-row AD Jacobian oracle. It
checks the AD-expanded runtime path on three finite deterministic probes:

- `deterministic_small_sine_DIM_vector`;
- `deterministic_small_cosine_DIM_vector`;
- `deterministic_mixed_sine_cosine_DIM_vector`.

This is the multi-probe formula-row AD Jacobian oracle. It still does not close
the independent symbolic row oracle: the check executes formula-level JAX
expressions on finite probes, but it does not prove a symbolic identity or the
`O(h^7)`
implementation-defect condition required by the theorem.

## Partial Kinematic Defect Certificate

`KINEMATIC_ROW_DEFECT_CERTIFICATE.md/json` now records a proof-scope
certificate for the 96 non-dynamic rows covered by the partial formula-row
oracle: the four collocation lift families and the lower-pair index-3
constraint family. On the smooth accepted FullVA lift, these rows vanish by the
collocation and constrained-branch identities, so they satisfy the theorem's
local defect budget for those row families.

This is still a partial certificate. The `newton_euler_weak_balance` family
has 36 rows and remains excluded from this proof-scope certificate. Therefore,
within this runtime/symbolic-oracle gate only,
`stage_residual_O_h7_proved_by_this_runtime_gate=false`,
`dynamic_symbolic_oracle_complete_by_this_runtime_gate=false`, and
`full_tfe_stage_replacement=false` remain the accepted boundary. Current
direct-substitution proof sidecars record the accepted direct stage-residual
route separately.

## Row-Family Partition

The runtime oracle requires the imported layout to partition the 132 residual
rows as six row families repeated over three Gauss stages:

| Row family | Offset | Width | Total rows |
| --- | ---: | ---: | ---: |
| `translational_position_weak_defect` | 0 | 6 | 18 |
| `rotational_lie_position_weak_defect` | 6 | 6 | 18 |
| `translational_velocity_weak_defect` | 12 | 6 | 18 |
| `angular_velocity_weak_defect` | 18 | 6 | 18 |
| `newton_euler_weak_balance` | 24 | 12 | 36 |
| `lower_pair_index3_weak_constraints` | 36 | 8 | 24 |

The validator checks that these slices are non-overlapping, cover exactly
rows `0..131`, and that each family evaluates to finite runtime values.

## Remaining Gap

This gate does not prove that each AD-expanded row equals an independently
generated symbolic formula to `O(h^7)`. It proves that the accepted runtime
residual and Jacobian path expose the claimed row partition on a finite
smooth-state probe, that the Gauss6-equivalent weighted block-functional view
matches those row families, and that all 132 runtime formula rows match an
independently reassembled formula-level oracle. It also proves that the
formula-row AD Jacobian and accepted `R_JAC` agree on the deterministic
runtime probe. The independent symbolic row oracle remains open on this
runtime/symbolic lane; this statement is not a reopening of the separate
direct-substitution stage-residual proof closure.

## Validator

Run:

```bash
../.venv_sbel/bin/python validate_dynamic_row_oracle_gate.py
```

Expected markers:

- `dynamic_row_oracle_gate=PASS`
- `residual_shape=132`
- `jacobian_shape=132x132`
- `row_family_count=6`
- `block_functional_crosscheck=PASS`
- `partial_formula_row_oracle=PASS`
- `partial_formula_row_count=96`
- `full_formula_row_oracle=PASS`
- `full_formula_row_count=132`
- `formula_row_ad_jacobian_oracle=PASS`
- `formula_row_ad_jacobian_probe_count=3`
- `partial_kinematic_stage_defect_certificate_checked=True`
- `symbolic_oracle_complete=False`
