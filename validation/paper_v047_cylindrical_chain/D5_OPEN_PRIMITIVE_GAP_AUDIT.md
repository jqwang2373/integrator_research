# D5 Open Primitive Gap Audit

Status: **open primitive gaps recorded; primitive-and-Taylor PC2 route remains open**.

This read-only audit records the five D5 primitive obligations that
remain after the compact-tube constant primitive is closed. It is a
proof-gap ledger, not a closure certificate.

## Summary

- Open primitive obligations: `5/5`.
- Required future subproofs: `19`.
- Required future subproofs closed: `16/19`.
- Conditional reductions closed: `2`.
- Primitive dependency graph recorded: `True`.
- Root lift primitives: `['P_state', 'P_acc']`.
- Root-dependent conditional primitives: `['P_lambda']`.
- Conditional downstream primitives: `['P_geom', 'P_gyro']`.
- Dependency edges: `5`.
- Root, root-dependent, and downstream term-row totals: `162/72/54`.
- P_state direct full-residual route recorded: `True`.
- P_state direct-route PS3/state/h-acceleration rates closed: `True/True/True`.
- P_state direct-route strict proof steps closed: `4/4`.
- P_state primitive route closed by direct corollary: `False`.
- P_state primitive-route induced bounds by direct corollary: `0/162`.
- Induced Taylor bounds proved: `0/162`.
- Primitive/Taylor PC2 route closed: `False`.
- Reader-facing primitive obstruction map main/flat: `True/True`.
- Conditional primitive/Taylor non-closure implication main/flat: `True/True`.

## Open Interfaces

| primitive | term rows | future subproofs | subproofs closed | primitive closed |
|---|---:|---:|---:|---:|
| `P_state` | `126` | `4` | `3` | `False` |
| `P_acc` | `36` | `4` | `3` | `False` |
| `P_lambda` | `72` | `4` | `4` | `False` |
| `P_geom` | `36` | `4` | `3` | `False` |
| `P_gyro` | `18` | `3` | `3` | `False` |

## Primitive Dependency Graph

| source | target | reason |
|---|---|---|
| `P_state` | `P_lambda` | multiplier-rate proof propagates state lift errors through the constrained Newton-Euler linearization |
| `P_acc` | `P_lambda` | multiplier-rate proof propagates acceleration lift errors through the constrained Newton-Euler linearization |
| `P_state` | `P_geom` | accepted-chart multiplier geometry reduction needs the pose lift |
| `P_lambda` | `P_geom` | accepted-chart multiplier geometry reduction needs the multiplier lift |
| `P_state` | `P_gyro` | gyroscopic bilinear reduction needs the angular-velocity lift |

- Closure sequence: `['P_state', 'P_acc', 'P_lambda', 'P_geom', 'P_gyro']`.
- Root lift primitives: `['P_state', 'P_acc']`.
- Root-dependent conditional primitives: `['P_lambda']`.
- Conditional downstream primitives: `['P_geom', 'P_gyro']`.
- Primitive/Taylor PC2 route closes only after all five open primitive obligations close.

### Minimal Next Subproofs

- `P_state`: PS3 actual state-lift instantiation (independent h-weighted acceleration input remains open).
- `P_acc`: PA2 unweighted acceleration lift (current evidence controls h times acceleration, not the unweighted acceleration error).
- `P_lambda`: instantiate PL4 with P_state/P_acc lift inputs (PL4 conditional propagation is closed, but the actual state and unweighted acceleration lift inputs remain open).

## Direct-Route Corollary

The P_state full-residual route certificate closes a direct-route PS3
input corollary by combining the 96 non-dynamic rows, the 36-row D5
direct-substitution certificate, and the stage-residual perturbation
criterion. This bypasses the h-acceleration obstruction without using
velocity collocation or finite probes.

- The direct-route PS3 input is closed.
- The direct-route state and h-weighted acceleration rates are closed.
- The direct-route proof has `4/4` strict steps closed.
- The primitive-and-Taylor PC2 route remains open.
- Zero primitive-route induced Taylor bounds are certified by this corollary.

## Anti-Circularity Gate

- Lemma `stage-residual-defect` is disallowed as an input to every open primitive.
- The D5 dynamic residual defect is disallowed as an input to every open primitive.
- Residual identities alone do not prove variable-lift rates.
- Finite numerical slopes do not close the primitive-and-Taylor route to PC2.
- The PS2 kinematic-block certificate records a uniform Euclidean Gauss subblock bound.
- The PS2 Lie-chart binding audit records pure SO(3) norm-equivalence.
- The PS2 row-injection audit records 72-to-96 unweighted residual dominance.
- The PS2 nonlinear binding audit records rotational-row compact-tube mean-value control.
- The PS2 aggregate promotion audit closes the uniform weighted inverse while leaving PS3, P_state, and the primitive-and-Taylor route to PC2 open.
- The PS3 actual-instantiation gap audit records `2/4` PS3 inputs closed while the independent h-weighted acceleration input remains open.
- The finite PS2 linearization probe is full-rank on recorded solved-stage probes but does not prove a uniform compact-tube inf-sup constant.
- The closed P_state map definition, PS2 weighted target, PS2 aggregate promotion, PS3 conditional conversion, and anti-circularity route still depend on actual PS3 state-lift instantiation before they can imply primitive lift rates.
- The closed P_acc map definition, row binding, non-dynamic input boundary, and PA2 weighted-inverse diagnostic still depend on the unweighted acceleration lift-rate proof.
- The closed P_lambda interface, finite multiplier-column rank probe, PL2 geometric-margin route, PL2 symbolic normal/friction structure, PL2 axis-plane margin, PL2 compact-tube reduction, non-circular D3 algebraic mapping, and conditional PL4 propagation still depend on the actual P_state and P_acc lift inputs before P_lambda can close.
- The closed P_geom chart reduction still depends on the open P_state and P_lambda lifts.
- The closed P_gyro bilinear reduction still depends on the open P_state angular-velocity lift.

## Acceptance Boundary

- Five primitive obligations remain open.
- The P_state non-dynamic map definition, PS2 weighted target, PS2 aggregate promotion, finite PS2 linearization probe, PS3 conditional conversion, and anti-circularity subproof are recorded, but P_state is not closed.
- The P_acc acceleration map definition, row binding, and independence subproof are closed, but P_acc is not closed.
- The P_lambda multiplier interface, finite inf-sup probe, PL2 symbolic normal/friction structure, PL2 axis-plane margin, PL2 compact-tube reduction, non-circular D3 algebraic mapping, and conditional PL4 propagation are recorded, but P_lambda is not closed.
- The P_geom chart reduction is recorded only as a conditional reduction; P_geom is not closed.
- The P_gyro algebraic reduction is recorded only as a conditional reduction; P_gyro is not closed.
- Zero induced Taylor bounds are certified by this audit.
- Primitive/Taylor PC2 route remains open.
