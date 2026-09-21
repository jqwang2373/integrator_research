# Closed-Loop Dynamic-Order Closure Contract

Status: **local dynamic order and strict common-reference rows closed; external superiority still open**

- Default execution policy: `coarse_first_no_default_1e-4`.
- Coarse step sizes: `[0.1, 0.05, 0.025]`; reference h: `0.0125`.
- Missing accepted local dynamic-order models: `none`.
- Current accepted local dynamic-order examples: `2`.
- Public work/precision available examples: `four_link, slider_crank`.
- Public work/precision missing examples: `none`.
- Strict common-reference available examples: `four_link, slider_crank`.
- Strict common-reference gap examples: `none`.
- Theorem order for a true `Gauss6/FullVA` dynamic trajectory row: `6`.

This contract now records that `four_link` and `slider_crank` have
local non-oracle true-dynamic `Gauss6/FullVA` coarse order evidence.
It still does not allow an external superiority claim because publication
quality figure integration and broader external-suite closure decisions
remain open.

| Model | Current status | pos floor | velocity evidence | acceleration evidence | public failures | finest pos ratio | finest vel ratio | finest acc ratio |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| `four_link` | `local_true_dynamic_order_public_work_and_strict_common_reference_available` | false | true | true | 0 | 1.470880e+01 | 2.179055e-08 | 1.742512e-08 |
| `slider_crank` | `local_true_dynamic_order_public_work_and_strict_common_reference_available` | false | true | true | 0 | 2.981263e+02 | 5.646845e-06 | 1.386538e-06 |

## Acceptance Paths

1. Local true dynamic trajectory path: closed by the non-oracle
   Newton coarse-order rows at `h=[0.1,0.05,0.025]`,
   `reference_h=0.0125`, and primary-state orders near six.
2. Residual-to-error theorem path: prove and validate a bound that
   turns the existing closed-loop residual/reaction rows into trajectory
   error estimates. This is no longer needed for local order, but remains
   a possible proof route for residual-only artifacts.
3. External comparison path: same-window public work/precision rows
   and strict common-reference error columns are now available for
   `four_link` and `slider_crank`; the remaining blocker before any
   external superiority claim is figure integration and broader suite closure.

No `1e-4` row is required by this closure contract. Strict public-policy
`1e-4` rows remain opt-in reproduction rows only.
