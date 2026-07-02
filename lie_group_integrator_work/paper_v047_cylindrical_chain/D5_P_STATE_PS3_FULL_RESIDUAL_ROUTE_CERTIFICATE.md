# D5 P_state PS3 Full-Residual Route Certificate

Status: **full residual route certificate closed; primitive route boundary retained**.

This certificate records the strict direct-route proof that bypasses the
`h delta A` obstruction without using velocity collocation or a finite
rank probe. It is a proof artifact, not a numerical diagnostic.

## Summary

- Full 132-row residual route closed: `True`.
- Direct-route PS3 corollary closed, not primitive P_state closure: `True`.
- Direct-route state lift rate closed: `True`.
- Direct-route h-weighted acceleration input closed: `True`.
- Proof gap closed scope: `direct_residual_bridge_ps3_corollary_only`.
- Primitive/Taylor route closed: `False`.
- Residual-to-error route closed: `False`.
- Multiplier/reaction output order claimed: `False`.
- P_state primitive closed by primitive route: `False`.
- Primitive-route induced Taylor bounds proved: `0/162`.
- Direct-route feedback into primitive P_state blocked main/flat: `True/True`.
- Strict proof steps closed: `4/4`.
- Submission ready: `False`.

## Strict Proof Route

| id | status | statement |
|---|---:|---|
| `FR1` | `True` | The 96 non-dynamic rows have O(h^7) residual on the smooth lifted Gauss stage. |
| `FR2` | `True` | The 36 Newton-Euler rows have zero direct-route residual remainder by direct substitution. |
| `FR3` | `True` | The full 132-row residual therefore satisfies the O(h^7) stage-residual perturbation hypothesis. |
| `FR4` | `True` | The aggregate PS2 estimate converts the full-route bound into ||delta S||=O(h^7) and h||delta A||=O(h^7). |

The 36 Newton-Euler rows are handled by direct-route residual decomposition with
zero residual remainder after direct substitution of the smooth Gauss FullVA lift.
Together with the 96 certified non-dynamic rows, this supplies the full
132-row residual hypothesis in the stage-residual perturbation lemma.
This is not a certification of the primitive 162-subterm Taylor lane:
the primitive-route induced Taylor bounds remain `0/162`, all 162
subterms remain blocked by open primitives, and the 36 h-weighted
acceleration primitive terms remain insufficient.

Applying the aggregate PS2 estimate

`||delta S|| <= C_PS2 (||delta N_h^nd|| + h ||delta A||)`

to the full-route perturbation bound gives `||delta S||=O(h^7)` and
`h||delta A||=O(h^7)` without the circular
`delta_A = h^{-1} (A_G^{-1} \otimes I)(delta_V-rho_V)` route.

## Non-Circularity

- Does not use actual PS3 as an input.
- Does not use `P_acc` or `P_lambda` lift estimates as inputs.
- Does not use velocity collocation as an h-inverse acceleration proof.
- Does not promote finite rank probes to compact-tube theorems.
- Does not use residual-to-error promotion.

## Primitive-Route Boundary

This certificate closes only the direct-route PS3 corollary. It does not
certify the alternative primitive/Taylor route, does not prove the 162
induced Taylor subterm bounds, and does not close B1's independent
implementation-oracle boundary.
The reader-facing feedback-prohibition lemma records that the direct-route
state estimate is a theorem-route corollary, not an admissible primitive-route
input for `P_state`; the 126 P_state-dependent primitive subterms and the
`0/162` primitive Taylor inventory remains unchanged.
