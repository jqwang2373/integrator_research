# D5 P_state Lift-Gap Audit

Status: **P_state lift gap recorded; separate primitive-route certificate remains open**.

This read-only audit records that the 96-row non-dynamic residual
certificate is not yet a state-variable lift-rate proof. The PS2
aggregate inverse is now closed; the missing step is the actual PS3
instantiation that combines it with the residual and h-weighted
acceleration inputs in the lift ledger.

## Summary

- P_state primitive closed: `False`.
- Term rows using P_state: `126/162`.
- Non-dynamic rows certified: `96/96`.
- Required future subproofs closed: `3/4`.
- PS1 map definition closed: `True`.
- PS4 anti-circularity closed: `True`.
- PS2 weighted target specification closed: `True`.
- PS2 kinematic-block certificate recorded/subblock/full-PS2/gaps: `True` / `True` / `False` / `3`.
- PS2 Lie-chart binding recorded/SO3/full-mean/gaps: `True` / `True` / `False` / `2`.
- PS2 row injection recorded/72-to-96/scaling/full-mean/gaps: `True` / `True` / `True` / `False` / `1`.
- PS2 nonlinear binding recorded/rot-mean/full-mean/full-PS2/gaps: `True` / `True` / `True` / `False` / `1`.
- PS2 aggregate promotion recorded/inverse/uniform/P_state/PC2: `True` / `True` / `True` / `False` / `False`.
- PS2 finite linearization probe recorded/full-rank: `True` / `True`.
- PS2 finite probe uniform constant proved: `False`.
- PS2 uniform constant proved: `True`.
- PS2 inverse or inf-sup closed: `True`.
- PS3 conditional conversion closed: `True`.
- PS3 actual-instantiation gap recorded/inputs/h-input: `True` / `2`-`4` / `False`.
- PS3 actual state lift conversion closed: `False`.
- Induced Taylor bounds proved: `0/162`.
- Primitive/Taylor PC2 route closed: `False`.

## Anti-Circularity Gate

- A residual-row identity is not by itself a variable-lift estimate.
- Lemma `stage-residual-defect` is disallowed as an input to P_state.
- The D5 dynamic residual defect is disallowed as an input to P_state.
- Accepted Newton-solution closeness needs an independent inverse bound.

## Required Future Proof

| id | status | statement |
|---|---|---|
| `PS1` | `True` | Define the non-dynamic stage map in the accepted Lie chart with pose, translational velocity, and angular velocity variables. |
| `PS2` | `True` | Prove a local inverse or inf-sup bound for that non-dynamic stage map on the compact proof tube. |
| `PS3` | `False` | Combine the 96-row non-dynamic residual certificate with the inverse bound to obtain O(h^7) state-variable lift rates. |
| `PS4` | `True` | Show the argument is independent of the D5 dynamic residual bound and of Lemma stage-residual perturbation. |

## Acceptance Boundary

- PS4 anti-circularity is closed.
- The PS2 weighted target specification is closed.
- The PS2 kinematic-block certificate records a uniform Euclidean Gauss subblock bound.
- The PS2 Lie-chart binding certificate records the pure SO(3) norm-equivalence constants.
- The PS2 row-injection audit records the 72-to-96 unweighted residual selection constant.
- The PS2 nonlinear binding audit records the rotational-row compact-tube mean-value estimate.
- Aggregate promotion of the component certificates to a full PS2 inverse is closed.
- The finite PS2 weighted linearization probe is recorded and full-rank on the finite solved-stage probes.
- The finite probe does not prove a uniform compact-tube inverse or inf-sup constant.
- The PS3 conditional conversion implication is recorded.
- PS2 local inverse or inf-sup proof is closed by the aggregate Taylor/mean-value proof.
- PS3 conversion to `O(h^7)` state lift rates remains open.
- P_state remains open.
- Zero P_state-induced Taylor bounds are certified.
- Primitive/Taylor PC2 lane remains open.
