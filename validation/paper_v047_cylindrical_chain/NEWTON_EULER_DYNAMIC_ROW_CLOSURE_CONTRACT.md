# Newton-Euler Dynamic Row Closure Contract

Status: **DIRECT-SUBSTITUTION CONTRACT CLOSED - primitive/Taylor route remains open**.

- Row count: `36`.
- Translational/rotational rows: `18/18`.
- Rows with full runtime traceability: `36`.
- Rows certified for direct-PC2 theorem input: `36`.
- Row-obligation links: `180`.
- Virtual-work wrench sign-skeleton rows: `36`.
- Virtual-work template identity rows: `36`.
- Virtual-work template identity proved: `True`.
- Row-expanded virtual-work identity rows: `36`.
- Row-expanded virtual-work identity proved: `True`.
- Multiplier wrench consistency closed: `True`.
- Smooth force-lift consistency closed rows: `36`.
- Row-ordering/scaling/AD closed rows: `36`.
- Balance identity closed rows: `36`.
- D5 dynamic-defect blueprint rows: `36`.
- D5 open lifted-stage terms: `0`.
- D5 direct-substitution closed terms: `36`.
- D5 direct-substitution dynamic zero rows: `36`.
- D5 primitive/Taylor route closed: `False`.
- D5 rows requiring power at least seven: `36`.
- D5 finite-probe-sufficient rows: `0`.
- D5 residual-to-error promotion allowed rows: `0`.
- D5 direct-substitution blueprint nonclosure flag: `False`.
- Unsatisfied close requirements: ``.
- Direct PC2 proof gap closed: `True`.
- Dynamic symbolic oracle complete: `False`.
- Stage residual O(h^7) implementation defect proved: `True`.

This contract distinguishes two routes. The direct-substitution route is
closed row-by-row by the D5 certificate: after substituting the smooth
Gauss lift `Z_G`, every dynamic residual row is zero and therefore
`O(h^7)`. The primitive/Taylor route remains open and is not used as the
closure mechanism.

## Proof Actions

| id | rows | action | status |
|---|---:|---|---|
| `D1` | `18` | prove the implemented translational rows equal the accepted linear-momentum balance identity | `closed_balance_identity` |
| `D2` | `18` | prove the implemented rotational rows equal the accepted body-frame angular-momentum balance identity | `closed_balance_identity` |
| `D3` | `36` | derive the lower-pair virtual-work identity tying Phi_q^T lambda to the implemented body wrenches | `closed_row_expanded_identity` |
| `D4` | `36` | prove smooth C7 force/friction lift and bounded derivatives on the accepted smooth proof tube | `closed_smooth_c7_lift` |
| `D5` | `36` | substitute the lifted Gauss stage into the assembled dynamic rows and prove the residual is O(h^7) | `closed_direct_substitution_zero_residual` |
| `D6` | `36` | replace finite-probe formula/Jacobian evidence with an independent symbolic row-ordering and scaling oracle | `closed_row_ordering_scaling_ad` |

## D5 Direct-Substitution Closure

For every dynamic row, the proof target is decomposed as

`R_dyn(Z_G) = E_balance_identity + E_multiplier_wrench + E_smooth_force_lift + E_row_binding + E_lifted_stage_dynamics`.

The first, second, fourth, and row-binding terms are closed inputs.
The D5 term is closed by direct substitution: the accepted smooth
FullVA lift satisfies the row-expanded Newton--Euler balance, so the
residual after substitution is `0`, hence `O(h^7)`. Finite probes and
residual-to-error promotion are still not accepted as D5 closure.

| item | rows | status | closure condition |
|---|---:|---|---|
| `D1/D2 balance identity` | `36` | `closed input` | use the closed balance identities row-by-row |
| `D3 multiplier wrench` | `36` | `closed input` | use the row-expanded lower-pair virtual-work identity |
| `D4 smooth force lift` | `36` | `closed input` | use the compact smooth-tube C7 derivative bound |
| `D6 row binding` | `36` | `closed input` | use row ordering, unweighted scaling, and AD binding closure |
| `D5 lifted-stage dynamics` | `36` | `closed direct substitution` | use `D5_DYNAMIC_DIRECT_SUBSTITUTION_CERTIFICATE.md/json`: residual after substituting `Z_G` is `0` row-by-row |

## Row Contract Summary

| row | stage | body | comp. | block | primary | traceability | direct-PC2 input |
|---:|---:|---:|---|---|---|---:|---:|
| `24` | `0` | `0` | `x` | `translational_newton_balance` | `D1` | `True` | `True` |
| `25` | `0` | `0` | `y` | `translational_newton_balance` | `D1` | `True` | `True` |
| `26` | `0` | `0` | `z` | `translational_newton_balance` | `D1` | `True` | `True` |
| `27` | `0` | `0` | `x` | `rotational_euler_balance` | `D2` | `True` | `True` |
| `28` | `0` | `0` | `y` | `rotational_euler_balance` | `D2` | `True` | `True` |
| `29` | `0` | `0` | `z` | `rotational_euler_balance` | `D2` | `True` | `True` |
| `30` | `0` | `1` | `x` | `translational_newton_balance` | `D1` | `True` | `True` |
| `31` | `0` | `1` | `y` | `translational_newton_balance` | `D1` | `True` | `True` |
| `32` | `0` | `1` | `z` | `translational_newton_balance` | `D1` | `True` | `True` |
| `33` | `0` | `1` | `x` | `rotational_euler_balance` | `D2` | `True` | `True` |
| `34` | `0` | `1` | `y` | `rotational_euler_balance` | `D2` | `True` | `True` |
| `35` | `0` | `1` | `z` | `rotational_euler_balance` | `D2` | `True` | `True` |
| `68` | `1` | `0` | `x` | `translational_newton_balance` | `D1` | `True` | `True` |
| `69` | `1` | `0` | `y` | `translational_newton_balance` | `D1` | `True` | `True` |
| `70` | `1` | `0` | `z` | `translational_newton_balance` | `D1` | `True` | `True` |
| `71` | `1` | `0` | `x` | `rotational_euler_balance` | `D2` | `True` | `True` |
| `72` | `1` | `0` | `y` | `rotational_euler_balance` | `D2` | `True` | `True` |
| `73` | `1` | `0` | `z` | `rotational_euler_balance` | `D2` | `True` | `True` |
| `74` | `1` | `1` | `x` | `translational_newton_balance` | `D1` | `True` | `True` |
| `75` | `1` | `1` | `y` | `translational_newton_balance` | `D1` | `True` | `True` |
| `76` | `1` | `1` | `z` | `translational_newton_balance` | `D1` | `True` | `True` |
| `77` | `1` | `1` | `x` | `rotational_euler_balance` | `D2` | `True` | `True` |
| `78` | `1` | `1` | `y` | `rotational_euler_balance` | `D2` | `True` | `True` |
| `79` | `1` | `1` | `z` | `rotational_euler_balance` | `D2` | `True` | `True` |
| `112` | `2` | `0` | `x` | `translational_newton_balance` | `D1` | `True` | `True` |
| `113` | `2` | `0` | `y` | `translational_newton_balance` | `D1` | `True` | `True` |
| `114` | `2` | `0` | `z` | `translational_newton_balance` | `D1` | `True` | `True` |
| `115` | `2` | `0` | `x` | `rotational_euler_balance` | `D2` | `True` | `True` |
| `116` | `2` | `0` | `y` | `rotational_euler_balance` | `D2` | `True` | `True` |
| `117` | `2` | `0` | `z` | `rotational_euler_balance` | `D2` | `True` | `True` |
| `118` | `2` | `1` | `x` | `translational_newton_balance` | `D1` | `True` | `True` |
| `119` | `2` | `1` | `y` | `translational_newton_balance` | `D1` | `True` | `True` |
| `120` | `2` | `1` | `z` | `translational_newton_balance` | `D1` | `True` | `True` |
| `121` | `2` | `1` | `x` | `rotational_euler_balance` | `D2` | `True` | `True` |
| `122` | `2` | `1` | `y` | `rotational_euler_balance` | `D2` | `True` | `True` |
| `123` | `2` | `1` | `z` | `rotational_euler_balance` | `D2` | `True` | `True` |

## Claim Policy

- Allowed now: runtime traceability, template-level C2 evidence, D1/D2 balance-identity closure, and D5 direct-substitution closure only as a direct-PC2 theorem input.
- D3 note: row-expanded lower-pair multiplier-wrench virtual-work identity is closed for all 36 rows.
- D4 note: smooth force/friction C7 lift is closed for the accepted compact smooth proof tube.
- D6 note: row ordering, unweighted residual scaling, and accepted AD binding are closed for all 36 rows.
- Scope: these row flags certify the direct-PC2 stage-residual input only; they do not close the primitive/Taylor route, P6 solver-policy evidence, P7 residual-to-error promotion, multiplier/reaction output order, source-policy readiness, or full-TFE replacement.
- Boundary: dynamic symbolic oracle completion and primitive/Taylor-route closure remain false.
- Forbidden now: symbolic defect certificate completion, dynamic symbolic oracle completion, finite-probe-only D5 closure, residual-to-error D5 closure, and submission readiness.

Validator: `validate_newton_euler_dynamic_row_closure_contract.py`.
