# Closed-Loop True-Dynamic Local Row Plan

Status: **plan only; no numerical rows have been run**

- Default policy: `coarse_first_no_default_1e-4`.
- Step sizes: `[0.1, 0.05, 0.025]` with reference `0.0125`.
- Plan rows: `24`.
- Local true-dynamic target rows: `6`.
- Public comparator rows: `18`.
- Strict public `1e-4` required: `False`.
- Heavy numerical run invoked: `False`.

This artifact is the next-row contract for the closed-loop
`four_link` and `slider_crank` blocker. It deliberately uses
`h=[0.1,0.05,0.025]`, `reference_h=0.0125`, and `plan_only=true`.
It is not a source-paper `1e-4` reproduction campaign.

| Model | Method | Role | h | Runner | New code | Execution |
|---|---|---|---:|---|---:|---|
| `four_link` | `Gauss6/FullVA` | `local_dynamic_target` | `0.10000000000000001` | `local_closed_loop_dynamic_dae_gauss6_fullva_runner` | `true` | `not_run` |
| `four_link` | `Gauss6/FullVA` | `local_dynamic_target` | `0.050000000000000003` | `local_closed_loop_dynamic_dae_gauss6_fullva_runner` | `true` | `not_run` |
| `four_link` | `Gauss6/FullVA` | `local_dynamic_target` | `0.025000000000000001` | `local_closed_loop_dynamic_dae_gauss6_fullva_runner` | `true` | `not_run` |
| `four_link` | `rA` | `public_baseline_comparator` | `0.10000000000000001` | `ra2021_public_dynamic_runner` | `false` | `not_run` |
| `four_link` | `rA` | `public_baseline_comparator` | `0.050000000000000003` | `ra2021_public_dynamic_runner` | `false` | `not_run` |
| `four_link` | `rA` | `public_baseline_comparator` | `0.025000000000000001` | `ra2021_public_dynamic_runner` | `false` | `not_run` |
| `four_link` | `rp` | `public_baseline_comparator` | `0.10000000000000001` | `ra2021_public_dynamic_runner` | `false` | `not_run` |
| `four_link` | `rp` | `public_baseline_comparator` | `0.050000000000000003` | `ra2021_public_dynamic_runner` | `false` | `not_run` |
| `four_link` | `rp` | `public_baseline_comparator` | `0.025000000000000001` | `ra2021_public_dynamic_runner` | `false` | `not_run` |
| `four_link` | `reps` | `public_baseline_comparator` | `0.10000000000000001` | `ra2021_public_dynamic_runner` | `false` | `not_run` |
| `four_link` | `reps` | `public_baseline_comparator` | `0.050000000000000003` | `ra2021_public_dynamic_runner` | `false` | `not_run` |
| `four_link` | `reps` | `public_baseline_comparator` | `0.025000000000000001` | `ra2021_public_dynamic_runner` | `false` | `not_run` |
| `slider_crank` | `Gauss6/FullVA` | `local_dynamic_target` | `0.10000000000000001` | `local_closed_loop_dynamic_dae_gauss6_fullva_runner` | `true` | `not_run` |
| `slider_crank` | `Gauss6/FullVA` | `local_dynamic_target` | `0.050000000000000003` | `local_closed_loop_dynamic_dae_gauss6_fullva_runner` | `true` | `not_run` |
| `slider_crank` | `Gauss6/FullVA` | `local_dynamic_target` | `0.025000000000000001` | `local_closed_loop_dynamic_dae_gauss6_fullva_runner` | `true` | `not_run` |
| `slider_crank` | `rA` | `public_baseline_comparator` | `0.10000000000000001` | `ra2021_public_dynamic_runner` | `false` | `not_run` |
| `slider_crank` | `rA` | `public_baseline_comparator` | `0.050000000000000003` | `ra2021_public_dynamic_runner` | `false` | `not_run` |
| `slider_crank` | `rA` | `public_baseline_comparator` | `0.025000000000000001` | `ra2021_public_dynamic_runner` | `false` | `not_run` |
| `slider_crank` | `rp` | `public_baseline_comparator` | `0.10000000000000001` | `ra2021_public_dynamic_runner` | `false` | `not_run` |
| `slider_crank` | `rp` | `public_baseline_comparator` | `0.050000000000000003` | `ra2021_public_dynamic_runner` | `false` | `not_run` |
| `slider_crank` | `rp` | `public_baseline_comparator` | `0.025000000000000001` | `ra2021_public_dynamic_runner` | `false` | `not_run` |
| `slider_crank` | `reps` | `public_baseline_comparator` | `0.10000000000000001` | `ra2021_public_dynamic_runner` | `false` | `not_run` |
| `slider_crank` | `reps` | `public_baseline_comparator` | `0.050000000000000003` | `ra2021_public_dynamic_runner` | `false` | `not_run` |
| `slider_crank` | `reps` | `public_baseline_comparator` | `0.025000000000000001` | `ra2021_public_dynamic_runner` | `false` | `not_run` |

## Acceptance Boundary

The local `Gauss6/FullVA` rows remain unaccepted until a true
closed-loop dynamic DAE runner solves the dynamic trajectory rather
than replaying kinematic constraints plus reaction reconstruction.
The public rows are comparator rows, not a replacement for the local
dynamic-order evidence. No row in this plan permits an external
superiority claim.
