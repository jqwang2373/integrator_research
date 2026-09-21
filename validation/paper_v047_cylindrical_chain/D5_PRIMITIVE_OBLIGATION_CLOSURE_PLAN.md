# D5 Primitive-Obligation Closure Plan

Status: **closure plan recorded; primitive-and-Taylor PC2 route remains open**.

This read-only plan records the six proof interfaces that remain after
the D5 primitive-bound reduction. It records template coverage only:
the conditional implication from primitive obligations to D5 Taylor bounds
has no current primitive-route Taylor-bound instance. The compact-tube
primitive is closed, but the five lift and bilinear primitives and
all induced Taylor term bounds remain open (`0/162` actual primitive
Taylor bounds certified).

## Summary

- Primitive obligations: `6`.
- Primitive obligations with closure steps: `6/6`.
- Primitive obligations proved: `1/6`.
- Open primitive obligations: `5/6`.
- P_tube compact constants closed: `True`.
- P_state map definition closed: `True`.
- P_state anti-circularity closed: `True`.
- P_state PS2 weighted target specified: `True`.
- P_state PS2 kinematic-block certificate recorded/subblock/full-PS2: `True` / `True` / `False`.
- P_state PS2 Lie-chart binding recorded/SO3/full-mean: `True` / `True` / `False`.
- P_state PS2 row injection recorded/72-to-96/scaling/full-mean: `True` / `True` / `True` / `False`.
- P_state PS2 nonlinear binding recorded/rot-mean/full-mean/full-PS2: `True` / `True` / `True` / `False`.
- P_state PS2 aggregate promotion recorded/inverse/uniform/P_state/PC2: `True` / `True` / `True` / `False` / `False`.
- P_state finite PS2 linearization probe recorded/full-rank: `True` / `True`.
- P_state finite PS2 probe uniform constant proved: `False`.
- P_state PS3 conditional conversion recorded: `True`.
- P_state PS3 actual-instantiation gap inputs/h-input/PC2: `2`-`4` / `False` / `False`.
- P_acc map definition closed: `True`.
- P_acc row binding closed: `True`.
- P_acc independence closed: `True`.
- P_lambda interface closed: `True`.
- P_geom conditional chart reduction recorded; primitive remains open: `True`.
- P_gyro conditional bilinear reduction recorded; primitive remains open: `True`.
- Taylor subterms with reduction rules: `162/162`.
- Induced Taylor bounds proved: `0/162`.
- Primitive/Taylor PC2 route closed: `False`.

## Closure Plan

| order | plan id | primitive id | term rows | proved | lemma interface |
|---:|---|---|---:|---:|---|
| `1` | `P_tube` | `P_uniform_tube_constants` | `162` | `True` | compact smooth proof-tube constants are uniform for all D5 row maps |
| `2` | `P_state` | `P_state_lift` | `126` | `False` | stage pose, translational velocity, and angular velocity lifts are O(h^7) |
| `3` | `P_acc` | `P_acceleration_lift` | `36` | `False` | stage translational and angular acceleration lifts are O(h^7) |
| `4` | `P_lambda` | `P_multiplier_lift` | `72` | `False` | lower-pair multiplier lifts are O(h^7) |
| `5` | `P_geom` | `P_geometry_lift` | `36` | `False` | dynamic-row force and torque Jacobian geometry lifts are O(h^7) |
| `6` | `P_gyro` | `P_gyroscopic_lift` | `18` | `False` | body-frame gyroscopic bilinear lift is O(h^7) |

## Acceptance Boundary

- The manuscript records the conditional primitive-obligation implication.
- The compact-tube primitive obligation is proved.
- The P_state map definition, PS2 weighted target, PS2 aggregate promotion, finite PS2 linearization probe, PS3 conditional conversion, PS3 actual-instantiation gap, and anti-circularity subproof are recorded, but actual PS3 state-lift instantiation remains open.
- The P_acc map definition, row binding, and independence subproof are closed, but the acceleration lift proof remains open.
- The P_lambda interface, PL2 inf-sup, PL3 non-circularity, and conditional PL4 propagation are recorded, but the actual multiplier lift remains open until P_state and P_acc close.
- The P_geom chart reduction is recorded only as a conditional reduction under P_state and P_lambda; P_geom itself remains open.
- The P_gyro bilinear reduction is recorded only as a conditional reduction under P_state; P_gyro itself remains open.
- Five lift and bilinear primitive obligations remain open.
- Zero induced Taylor bounds are certified.
- Primitive/Taylor PC2 route remains open.
