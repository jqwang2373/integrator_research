# Four-Example Source-Policy Dashboard

Status: **all_four_examples_checked_source_policy_dynamic_order_open**.

- Examples checked: `single_pendulum, double_pendulum, four_link, slider_crank`.
- Common-reference cells: `44`.
- Common-reference nonlocal order/error wins: `40/40` and `40/40`.
- Local evidence coverage examples: `4/4`.
- Accepted method dynamic-order examples: `2/4` (`single_pendulum, double_pendulum`).
- Closed-loop coarse-dynamics diagnostics: `2/2` at h=`[0.1, 0.05, 0.025]`.
- Source-policy dynamic-order examples: `0/4`.
- External-superiority claim allowed: `False`.

| Example | Local evidence layer | Local velocity order/error | Common-reference nonlocal wins | Accepted source-policy dynamic order | Source-policy status |
|---|---|---:|---:|---:|---|
| single_pendulum | method_side_order_gate (6.024) | 5.801 / 1.155e-12 | 10/10 order, 10/10 error | False | single public-policy rows completed but reference-floor limited; not accepted external dynamic order |
| double_pendulum | method_side_order_gate (6.089) | 6.010 / 2.346e-13 | 10/10 order, 10/10 error | False | gauss6_fullva_public_horizon_double_coarse_not_full_campaign; not the public policy dynamic-order campaign |
| four_link | closed_loop_coarse_dynamics_diagnostic (5.955) | 6.085 / 1.093e-11 | 10/10 order, 10/10 error | False | source-policy public-horizon rows completed as kinematic_reaction_residual_not_true_dynamic_order; separate closed-loop coarse-dynamics diagnostic rows are available, but not accepted as external source-policy dynamic order |
| slider_crank | closed_loop_coarse_dynamics_diagnostic (6.159) | 7.341 / 9.189e-12 | 10/10 order, 10/10 error | False | source-policy public-horizon rows completed as kinematic_reaction_residual_not_true_dynamic_order; separate closed-loop coarse-dynamics diagnostic rows are available, but not accepted as external source-policy dynamic order |

Reading rule: this dashboard has three layers. Accepted method dynamic-order evidence is the single/double pendulum layer; closed-loop mechanism evidence is the four-link/slider-crank layer; source-policy external dynamic-order closure is still `0/4`. The local evidence coverage count is `4/4`, but that is not a four-example dynamic-order claim and does not allow external superiority.
