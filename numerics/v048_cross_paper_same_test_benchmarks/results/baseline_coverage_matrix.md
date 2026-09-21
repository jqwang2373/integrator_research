# Baseline Coverage Matrix

Accepted same-grid four-example methods: `11`.
Implemented or alias-resolved methods: `12`.
Required methods resolved: `13/13`.
Source-unresolved methods: `none`.
Alias-resolved methods: `vp2024_lie_group_ode_partitioning`.
Scope-excluded methods: `tfe2026_TFE_m3_GL`.
Rejected partial methods: `none`.
VP larger-step local velocity-order wins: `4/4`.
VP larger-step local reported finest-velocity-error wins: `1/4`.
Direct error-vs-local comparable rows: `40`.
Common-reference local velocity-order wins: `40/40`.
Common-reference local finest-velocity-error wins: `40/40`.
Bounded common-reference direct error diagnostic: `True`.
Paper-level direct error superiority allowed: `False`.
Source-policy reproduction: `False`.

| Method | status | ok examples | non-ok examples | source status | role |
|---|---|---|---|---|---|
| `hi2022_rA` | `accepted_same_grid_four_examples` | `double_pendulum|four_link|single_pendulum|slider_crank` | `none` | `public_code_present` | Kissel-Negrut-related baseline |
| `hi2022_rA_half` | `accepted_same_grid_four_examples` | `double_pendulum|four_link|single_pendulum|slider_crank` | `none` | `public_code_present` | Kissel-Negrut-related baseline |
| `local_Gauss6_FullVA` | `accepted_same_grid_four_examples` | `double_pendulum|four_link|single_pendulum|slider_crank` | `none` | `implemented_local` | primary method under test |
| `ra2021_rA` | `accepted_same_grid_four_examples` | `double_pendulum|four_link|single_pendulum|slider_crank` | `none` | `public_code_present` | Kissel-Negrut baseline |
| `ra2021_reps` | `accepted_same_grid_four_examples` | `double_pendulum|four_link|single_pendulum|slider_crank` | `none` | `public_code_present` | Kissel-Negrut baseline |
| `ra2021_rp` | `accepted_same_grid_four_examples` | `double_pendulum|four_link|single_pendulum|slider_crank` | `none` | `public_code_present` | Kissel-Negrut baseline |
| `tfe2026_Newmark_beta` | `accepted_same_grid_four_examples` | `double_pendulum|four_link|single_pendulum|slider_crank` | `none` | `paper_formula_wrapped` | original-paper baseline |
| `tfe2026_TFE_m1` | `accepted_same_grid_four_examples` | `double_pendulum|four_link|single_pendulum|slider_crank` | `none` | `paper_formula_wrapped` | original-paper baseline |
| `tfe2026_TFE_m2` | `accepted_same_grid_four_examples` | `double_pendulum|four_link|single_pendulum|slider_crank` | `none` | `paper_formula_wrapped` | original-paper baseline |
| `tfe2026_TFE_m3_GL` | `scope_excluded_after_rejected_four_link` | `double_pendulum|single_pendulum|slider_crank` | `four_link:reference_failed` | `paper_formula_wrapped_scope_excluded_on_four_link` | original-paper diagnostic row outside required four-example matrix |
| `tfe2026_trapezoidal` | `accepted_same_grid_four_examples` | `double_pendulum|four_link|single_pendulum|slider_crank` | `none` | `paper_formula_wrapped` | original-paper baseline |
| `vp2024_coordinate_partitioning_rA` | `accepted_same_grid_four_examples` | `double_pendulum|four_link|single_pendulum|slider_crank` | `none` | `local_reimplementation_from_published_algorithm` | velocity-partitioning baseline subset |
| `vp2024_lie_group_ode_partitioning` | `alias_resolved_to_vp2024_coordinate_partitioning_rA` | `none` | `double_pendulum:not_implemented_for_four_examples|four_link:not_implemented_for_four_examples|single_pendulum:not_implemented_for_four_examples|slider_crank:not_implemented_for_four_examples` | `method_alias_resolved` | velocity-partitioning alias of implemented coordinate-partitioning wrapper |

Claim boundary: local velocity order can be compared against finite runnable rows. The main matrix's reported velocity errors use heterogeneous reference policies; the separate common-reference audit supplies bounded final-state velocity-error diagnostics for accepted runnable methods, but paper-level direct error superiority is blocked by the all-example forensic audit. The VP Lie-group ODE label is resolved as an alias of the implemented VP coordinate-partitioning wrapper. TFE(m=3) four-link is a source-backed excluded stress row rather than a required accepted baseline.
