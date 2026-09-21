# Closed-Loop True-Dynamic Residual Scaffold

Status: **residual layout specified; runner not implemented**

- Method: `Gauss6/FullVA`.
- Gauss stages: `3`.
- Stage unknown dimension: `72`.
- Total Newton dimension: `216`.
- Square system: `True`.
- Local runner implemented: `False`.
- Accepted dynamic-order rows: `0`.
- Default `1e-4` required: `False`.

The scaffold follows the v029 FullVA idea: constrained collocation
components are replaced by position/acceleration consistency rows, with
velocity/acceleration consistency enforced explicitly at each stage. In
these fully constrained driven closed loops, every generalized component
is constrained, so each stage solves for `q`, `v`, `a`, and `lambda`
using exactly four residual families: `Phi`, `Phi_q v - nu`,
`Phi_q a - gamma`, and Newton-Euler balance.

| Model | nb | nc | stage unknowns | stage residuals | total unknowns | square |
|---|---:|---:|---:|---:|---:|---:|
| `four_link` | `3` | `18` | `72` | `72` | `216` | `true` |
| `slider_crank` | `3` | `18` | `72` | `72` | `216` | `true` |

## Implementation Contract

The next code symbols should be:

- `pack_closed_loop_fullva_stage_vector`
- `unpack_closed_loop_fullva_stage_vector`
- `closed_loop_fullva_stage_residual`
- `gauss6_closed_loop_fullva_dynamic_step`
- `simulate_v046_local_dynamic_fullva`

A row is still not accepted until the runner produces trajectory rows
on the coarse-first plan and the non-floor order gate passes.
