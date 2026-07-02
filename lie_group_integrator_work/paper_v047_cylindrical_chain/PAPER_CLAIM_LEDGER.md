# v047 Paper Claim Ledger

`PAPER_CLAIM_LEDGER.md` fixes the claim boundary for the v047 paper package. It is a
read-only map from paper claims to generated artifacts; it is not a numerical
regeneration recipe.

## Claim Boundary

| Claim | Status | Evidence | Lightweight check |
| --- | --- | --- | --- |
| Conditional formal-order comparison with the local paper-style TFE target | Accepted within current artifact scope | The accepted `Gauss6/FullVA` path is sixth order and records smooth position/velocity orders `7.161/7.066`; the encoded paper-style `m=3` Gauss-Lobatto TFE formula map has expected order five. This is a bounded order-comparison statement, not a full residual reproduction, source-policy, work/precision, or external-superiority claim. | `validate_cmame_submission.py`, `validate_cmame_blocker_closure_gate.py`, `validate_proof_evidence_matrix.py`, `validate_order_acceptance_gate.py`, `validate_source_paper_comparison.py`, `validate_paper_claims.py`, and `validate_paper_package.py` |
| Example-level order boundary | Accepted as a claim guard | `ORDER_ACCEPTANCE_GATE.md` and `ORDER_ACCEPTANCE_GATE.json` record that `single_pendulum` and `double_pendulum` have accepted dynamic order rows, while `four_link` and `slider_crank` are mechanism-coverage rows with `not_accepted_dynamic_order` for external closed-loop dynamic order. | `validate_order_acceptance_gate.py` |
| Four ASME method rows | Accepted | `results/summary_v047.json` status `four_asme_method_rows_accepted_projection_sharp_sparse_caveats`; `cylindrical_chain_asme_gate.csv`; `cylindrical_chain_asme_single_absolute_fullva_runs.csv`; `cylindrical_chain_asme_double_method_runs.csv`; `cylindrical_chain_asme_closed_loop_kinematic_fullva.csv`; `cylindrical_chain_asme_closed_loop_reaction_dynamics.csv` | `validate_four_asme_minimal.py` |
| Smooth cylindrical Gauss6/FullVA order | Accepted method path | `summary_v047.json` and `cylindrical_chain_convergence.csv` record smooth projected position/velocity orders `7.161/7.066` over `h=[0.04,0.02,0.01]` | `validate_paper_claims.py` and `validate_v047_outputs.py` |
| Paper TFE formula mapping | Diagnostic, not a replacement | `main.tex` separates the `m=3` Gauss-Lobatto TFE expected order-five mapping from the accepted Gauss6 method claim | `validate_paper_claims.py` |
| Source-free final-stage lower-pair closure | Diagnostic, terminal-closed but order-limited | `summary_v047.json`; source-free final-stage closure closes raw terminal velocity but remains order-limited | `validate_v047_outputs.py` |
| Recurrent weak-closure full-TFE repair scaffold | Diagnostic smoke only | `FULL_TFE_REPAIR_SPEC.md`; `run_v047.py` targets `lower_pair_recurrent_weak_closure_smoke`, `lower_pair_recurrent_weak_closure_trajectory_smoke`, `lower_pair_recurrent_weak_closure_h_sweep_smoke`, `lower_pair_recurrent_terminal_blend_one_step_smoke`, `lower_pair_recurrent_terminal_blend_h_sweep_smoke`, `lower_pair_recurrent_terminal_component_one_step_smoke`, `lower_pair_recurrent_terminal_component_h_sweep_smoke`, `lower_pair_recurrent_history_gamma_h_sweep_smoke`, `lower_pair_recurrent_weak_differential_audit`, `lower_pair_recurrent_stage2_gradient_differential_audit`, and `lower_pair_recurrent_stage2_matrix_gradient_differential_audit` print non-acceptance JSON without running full `main()`; latest one-step smokes at `h=0.04` have rank `132`, smooth/sharp residuals `6.737e-13`/`6.484e-13`, and raw terminal endpoint velocities `2.337e-10`/`2.319e-10`; latest short-trajectory smoke has `4` converged steps, rank `132`, max residual `2.483e-12`, max raw terminal endpoint velocity `7.994e-06`, and `terminal_velocity_closed=false`; latest bounded h-sweep smoke over `h=[0.04,0.02]` against `reference_h=0.01` has `12` converged steps, rank `132`, max residual `4.463e-12`, max raw terminal endpoint velocity `8.234e-06`, min position order `3.204`, min velocity order `-0.428`, and `accepted_h_sweep_present=false`; latest full-shaped h-sweep over `h=[0.04,0.02,0.01]` against `reference_h=0.005` has `28` converged steps, rank `132`, max residual `9.998e-12`, max raw terminal endpoint velocity `8.234e-06`, smooth orders `5.317/6.782`, sharp orders `2.555/1.918`, and `accepted_h_sweep_present=false`; latest recurrent/terminal blend one-step smoke found best terminal gamma `1.0` with smooth/sharp terminal velocities `7.845e-17`/`9.479e-17`, while best residual gamma `0.5` had smooth/sharp residuals `6.071e-13`/`3.533e-13` and still had terminal velocity about `2.30e-10`; latest smooth+sharp recurrent/terminal blend h-sweep converged `24` steps with rank `132`, max residual `4.766e-12`, best terminal gamma `1.0` with smooth/sharp terminal velocities `3.049e-16`/`2.941e-16`, best smooth-order gamma `0.5` with smooth minimum order `4.413`, gamma `1.0` smooth minimum order `4.397`, sharp min velocity order `-0.428`, and `accepted_h_sweep_present=false`; latest dense scalar-gamma screen over `gamma=[0,0.25,0.5,0.75,1]` converged `60` steps, best smooth-order gamma `0.75` with smooth minimum order `4.414`, best terminal gamma `1.0`, max terminal velocity `8.234e-06`, and still no accepted order/terminal intersection; latest near-terminal gamma screen over `gamma=[0.9,0.99,0.999,1]` converged `48` steps, best smooth-order gamma `0.99` with smooth minimum order `4.415`, gamma `0.999` still had terminal velocity `4.678e-07`, and only gamma `1.0` terminal-closed; latest component-wise one-step gamma screen used `10` vectors and `20` one-step rows in `31.6` seconds, kept rank `132` with max residual `1.766e-12`, had `5` nontrivial terminal-closed rows, best nontrivial terminal row `component_2_release_0p999` at `3.456e-17`, and worst component release `component_7_release_0p999` at `1.234e-11`; latest component-wise trajectory screen used four vectors and `48` short-trajectory steps in `98.4` seconds, kept rank `132` with max residual `4.766e-12`, best terminal vector `component_2_release_0p999` at `2.696e-16`, best smooth-order vector `all_0p999` at `4.401`, terminal blocker `4.678e-07`, and `order_terminal_intersection_present=false`; latest recurrent history-gamma default screen has `history_gamma_h_sweep_smoke_present=true`, uses `12` smooth-only short-trajectory steps in `38.9` seconds, keeps rank `132` with max residual `2.586e-12`, max terminal velocity `9.365e-07`, best terminal velocity `1.451e-07`, best smooth order `4.402`, and `order_terminal_intersection_present=false`; signed history policies converge in `36.9` seconds with max residual `3.869e-12`, best terminal velocity `1.452e-07`, best smooth order `4.415`, and still no accepted order/terminal intersection; latest recurrent weak differential audit has `recurrent_weak_differential_audit_present=true`, uses `2` smooth local rows in `26.0` seconds, keeps rank `132` with max residual `2.483e-12`, recurrent projection residuals `0.899` to `0.974`, final-stage comparison residual `1.456e-15`, relative closure-Jacobian gap `6.872`, `any_recurrent_weak_spans_terminal_bridge=false`, `coefficient_gradient_gap_present=true`, and missing direction `stage2`/`translation_velocity_v`; latest stage-2 coefficient-gradient audit has `recurrent_stage2_gradient_differential_audit_present=true`, uses `8` local rows in `35.3` seconds, keeps rank `132`, best feature `curvature_plus_history_delta`, best gain `1e12`, best projection residual `0.899`, independent target rank `8`, max closure value delta `1.246e-09`, and `any_candidate_spans_terminal_bridge=false`; latest target-free row/column/bilinear stage-2 matrix-gradient audit has `recurrent_stage2_matrix_gradient_differential_audit_present=true`, uses `32` local rows in `68.1` seconds, keeps rank `132`, best law `diagonal_plus_row_broadcast_feature`, best gain `1e12`, best projection residual `0.898873`, independent target rank `8`, max closure value delta `4.005e-09`, and `any_candidate_spans_terminal_bridge=false`; latest active-velocity stage-2 matrix-gradient extension uses `16` local rows in `46.6` seconds, keeps rank `132`, best law `stage2_velocity_column_broadcast_feature`, best gain `1e12`, best projection residual `0.585746`, independent target rank `8`, max closure value delta `1.460e-06`, and `any_candidate_spans_terminal_bridge=false`; latest expanded active-law grid uses `20` local rows in `51.2` seconds, keeps rank `132`, best law `stage2_velocity_shifted_column_broadcast_feature`, best gain `1e12`, best projection residual `0.576548`, independent target rank `8`, max closure value delta `1.460e-06`, and `any_candidate_spans_terminal_bridge=false`; latest best-law missing-direction decomposition uses `2` local rows in `27.8` seconds, keeps rank `132`, best residual `0.576548`, missing-direction rank `8`, dominant variable family `angular_velocity_w` at fraction `0.502991`, stage-2 fraction `0.963038`, and zero-initial dominant variable family `translation_velocity_v` at fraction `0.487135` | `validate_full_tfe_repair_spec.py` |
| Independent full TFE stage replacement | Open | `full_tfe_stage_replacement=false`; `accepted_h_sweep_present=false`; `FULL_TFE_REPLACEMENT_GAP_LEDGER.md`; `FULL_TFE_REPAIR_SPEC.md`; row-space compression audit has 36 target-free rows, 0 spans, best residual about `7.378e-01`, best non-final residual about `9.815e-01`; expanded active-stage velocity matrix-gradient localization has 20 local rows, best law `stage2_velocity_shifted_column_broadcast_feature`, best residual `0.576548`, independent target rank `8`, and no terminal-bridge span; best-law missing-direction decomposition localizes that residual to stage 2, dominant variable family `angular_velocity_w`, fraction `0.502991`, and stage-2 fraction `0.963038`; angular-only mask follow-up has 8 local rows, best law `stage2_angular_velocity_shifted_column_broadcast_feature`, best residual `0.752997`, independent target rank `8`, and no terminal-bridge span; bilinear outer-product follow-up has 24 local rows, best law `stage2_velocity_feature_outer_stage2_velocity`, best residual `0.898720`, independent target rank `8`, and no terminal-bridge span; componentwise diagonal follow-up has 24 local rows, best law `stage2_velocity_diagonal_plus_hadamard_row_feature_stage2_velocity`, best residual `0.898530`, independent target rank `8`, and no terminal-bridge span; latest source-to-velocity lift follow-up has 34 local rows, best corrected laws `stage02_convex_pose_velocity_0p01_sourcelift_historydelta_p1_z` and `stage02_convex_pose_velocity_0p01_sourcelift_source0_p1_z`, best corrected residual `0.609803`, independent target rank `8`, and no terminal-bridge span; latest near-terminal slope follow-up has 4 local rows, best law `stage02_convex_pose_velocity_slope_0p01_0p05_z`, residual `0.677034`, independent target rank `8`, and no terminal-bridge span; latest near-terminal curvature follow-up has 4 local rows, best law `stage02_convex_pose_velocity_curvature_0p01_0p05_0p10_z`, residual `0.871228`, independent target rank `8`, dominant remaining family `translation_velocity_v` at fraction `0.591909`, and no terminal-bridge span; latest source/history coefficient-feature matrix follow-up has 16 local rows, best law `source_curvature_shifted_column_broadcast_feature`, residual `0.898873`, independent target rank `8`, dominant remaining family `translation_velocity_v` at fraction `0.556060`, stage-2 fraction `1.000000`, and no terminal-bridge span; latest terminal-limit source-lift matrix-difference follow-up has 8 local rows, best law `stage02_convex_pose_velocity_extrapolate_0p01_0p02_sourceliftmatrixdiff_curvature_m0p1_z`, residual `5.298e-06`, independent target rank `8`, dominant remaining family `translation_acceleration_a` at fraction `0.407672`, and no terminal-bridge span; latest curvature source-lift scale refinement has 11 local rows, best law `stage02_convex_pose_velocity_extrapolate_0p01_0p02_sourceliftmatrixdiff_curvature_p0p01_z`, residual `5.298e-06`, source-curvature norm `1.076e-14`, and no terminal-bridge span; latest mean-acceleration bridge scale refinement has 11 local rows, best nonterminal law `stage02_convex_pose_velocity_extrapolate_0p01_0p02_accel_p0p01_z`, residual `0.000867721`, dominant remaining family `lie_position_u` at fraction `0.706665`, and no terminal-bridge span; latest generalized-acceleration Taylor-shift refinement has 11 local rows, best nonterminal law `stage02_convex_pose_velocity_extrapolate_0p01_0p02_genaccel_p0p01_z`, residual `0.000866899`, dominant remaining family `lie_position_u` at fraction `0.701135`, and no terminal-bridge span; latest pose-acceleration Taylor-shift refinement has 11 local rows, best nonterminal law `stage02_convex_pose_velocity_extrapolate_0p01_0p02_poseaccel_p0p01_z`, residual `4.1835e-05`, dominant remaining family `lie_position_u` at fraction `0.711570`, stage-2 fraction `0.771337`, and no terminal-bridge span; latest tiny pose-acceleration scale refinement has 10 local rows, best nonterminal law `stage02_convex_pose_velocity_extrapolate_0p01_0p02_poseaccel_p0p0005_z`, residual `5.5898e-06`, dominant remaining family `translation_acceleration_a` at fraction `0.350240`, and no terminal-bridge span; latest remaining Gauss endpoint-pose follow-up has 11 local rows, best law `gauss_endpoint_pose_stage02_convex_0p00_z`, residual `0.172659`, independent target rank `6`, dominant remaining family `lie_position_u` at fraction `0.952340`, and no terminal-bridge span | `validate_full_tfe_gap.py`, `validate_full_tfe_repair_spec.py`, `validate_paper_claims.py`, and `validate_v047_outputs.py` |
| Sparse backend speed | Open engineering caveat | sparse speed is quantified but is not a stable dense-`jacfwd` wall-clock win | `validate_v047_outputs.py` |
| Sharp-friction coarse regime | Open practical caveat | sharp coarse h-sweep is order-reduced while ultra fixed refinement recovers high order at higher cost | `validate_v047_outputs.py` |

## Original Paper Versus Accepted v047 Claim

This ledger mirrors Table `tab:source-paper-v047-boundary` in `main.tex`.

| Boundary question | Source-paper/local target | Accepted v047 claim |
| --- | --- | --- |
| Comparator | Local paper-style `m=3` Gauss-Lobatto TFE formula target with expected order five. | Accepted `Gauss6/FullVA` path with smooth observed orders `7.161/7.066`. |
| Implemented method | Complete source-paper TFE residual is not the accepted comparator while the independent replacement gate is open. | Accepted 132-row Gauss/FullVA residual with audited projection/KKT endpoint closure. |
| Artifact-backed result | Local formula-mapping target boundary, not source-paper residual reproduction. | Conditional formal-order comparison inside the current v047 artifact scope and four-example ASME gate. |
| Outside the claim | Full source-paper residual reproduction requires accepted paper-derived stage rows inside Newton. | `full_tfe_stage_replacement=false` remains an explicit caveat and future stronger gate. |

## Order-Comparison Acceptance Criteria

This ledger mirrors the paper-facing order-comparison acceptance table in
`main.tex`. The paper-facing statement is accepted only when all six read-only criteria remain
synchronized:

| Criterion | Ledger evidence | Status |
| --- | --- | --- |
| Accepted method path | `Gauss6/FullVA` is the claimed production path; paper-TFE substitution rows remain diagnostic unless independently accepted. | Pass |
| Order exceedance | Smooth position/velocity orders `7.161/7.066` exceed the local paper-style `m=3` Gauss-Lobatto TFE expected order five target. | Pass |
| Four-example gate | `single_pendulum`, `double_pendulum`, `four_link`, and `slider_crank` are accepted under the ASME method gate. | Pass |
| Comparator boundary | The comparator is the local paper-style formula target; complete source-paper residual reproduction is separate. | Pass |
| Caveat separation | Sparse speed, sharp-friction coarse-regime behavior, source-policy reproduction, and `full_tfe_stage_replacement=false` remain explicit caveats. | Pass |
| Read-only reproducibility | `validate_cmame_submission.py`, `validate_cmame_blocker_closure_gate.py`, `validate_paper_claims.py`, `validate_proof_evidence_matrix.py`, `validate_order_acceptance_gate.py`, `validate_source_paper_comparison.py`, `validate_submission_bundle.py`, `validate_paper_package.py`, `validate_four_asme_minimal.py`, `validate_full_tfe_gap.py`, `validate_full_tfe_repair_spec.py`, and `validate_pipeline_outputs.py` check the claim without invoking the full v047 generator. | Pass |

Latest full-TFE local probe note: the stage-2 source-to-velocity transport
ultra-fine scale refinement has 9 local rows, best nonterminal law
`stage02_convex_pose_velocity_0p00_sourceliftmatrixdiff_historydelta_m0p0001_z`,
residual `1.251e-06`, independent target rank `6`, dominant remaining family
`lie_position_u`, and no terminal-bridge span. It is the strongest
nonterminal transport clue so far, but it does not change the open
`full_tfe_stage_replacement=false` boundary.
The latest combined source-transport/angular-pose follow-up has 8 local rows,
best combined law
`stage02_convex_pose_velocity_0p00_sourceliftmatrixdiff_historydelta_m0p0001_angposeaccel_p0p0001_z`,
residual `1.296e-06`, independent target rank `8`, dominant remaining family
`lie_position_u`, and no terminal-bridge span; the source-only row remains the
overall best.
The latest bare endpoint-pose velocity follow-up has 3 local rows, elapsed
`31.7` seconds, best law `stage02_convex_pose_velocity_0p00_z`, residual
`1.327e-15`, independent target rank `0`, `span_row_count=1`, and
`nonterminal_span_row_count=1`. It is recorded as local-span-not-full-TFE
evidence because no trajectory h-sweep, order proof, or artifact update
accepts the row; `full_tfe_stage_replacement=false` remains unchanged.
The bounded nonlinear trajectory follow-up
`lower_pair_endpoint_pose_velocity_predictor_h_sweep_smoke` then inserts the
same predictor family into the full `132`-row residual. The default smooth-only
`stage02_convex_pose_velocity_0p00_z` smoke runs in `21.5` seconds over
`h=[0.04,0.02]`, keeps rank `132`, converges all `3` requested steps, and
closes terminal velocity to `7.29e-17`, but has two-point orders
`6.588/4.508`. The smooth-only three-h refinement runs in `28.6` seconds over
`h=[0.04,0.02,0.01]` against `reference_h=0.005`, converges all `7` requested
steps, closes terminal velocity to `8.124e-17`, but has only `4.142/2.305`
position/velocity order. The nearby nonterminal
`stage02_convex_pose_velocity_0p01_z` default smoke runs in `21.2` seconds,
keeps rank `132`, but leaves terminal velocity at `6.255e-06` with orders
`2.345/1.878`.
The non-projection extrapolated row
`stage02_convex_pose_velocity_extrapolate_0p01_0p02_z` improves the
nonterminal trajectory behavior but still fails acceptance. The default
two-h smoke runs in `21.8` seconds with `projection_used=false`, rank `132`,
max terminal velocity `1.254e-07`, and orders `6.412/3.775`. The three-h
smooth refinement runs in `28.9` seconds, converges all `7` requested steps,
has max terminal velocity `1.254e-07`, finest-h terminal velocity
`1.244e-08`, and orders `4.054/2.364`.
The projection-like terminal-tangent follow-up is also negative. The full
`stage02_convex_pose_velocity_0p01_terminalproj_z` correction fails in the
reference run with residual divergence `6.739e+08`. Damped
`stage02_convex_pose_velocity_0p01_terminalproj_p0p1_z` converges in `28.0`
seconds but leaves terminal velocity `7.028e-06` with orders `2.301/1.788`;
`stage02_convex_pose_velocity_0p01_terminalproj_p0p5_z` converges in `28.7`
seconds but leaves terminal velocity `1.321e-05` with orders `2.158/1.433`.
Because these laws set `projection_used=true`, they are diagnostic exclusions,
not candidate acceptance evidence.

## ASME Quantitative Evidence

The paper's four-example table is synchronized to the current
`summary_v047.json` and the minimal validator output:

- `single_absolute_min_order=6.024`
- `single_absolute_max_stage_residual=3.664e-12`
- `double_method_min_order=6.089`
- `double_endpoint_position_constraint=7.034e-13`
- `double_endpoint_velocity_constraint=8.323e-12`
- `four_link_closed_loop_max_constraint_norm=1.052e-14`
- `four_link_reaction_max_dynamics_residual=1.338e-13`
- `slider_crank_closed_loop_max_constraint_norm=1.204e-15`
- `slider_crank_reaction_max_dynamics_residual=6.492e-15`

The lightweight validator `validate_paper_claims.py` recomputes these values
from `summary_v047.json` and checks that the paper and README retain the
matching numbers.

## Proof/Status Evidence

The paper's proof-status section is synchronized with the scoped direct-route
proof manifests and the current `ORDER_PROOF_LEDGER.md` boundary.
The accepted method claim is a conditional Gauss6/FullVA order-six argument for
a regular smooth FullVA residual; sparse AD is an order-preserving backend
change. The independent paper-TFE replacement is not proved and remains an
open proof obligation while `full_tfe_stage_replacement=false`.

The paper now records an accepted method-order theorem plus a separate
conditional order-comparison proposition in `main_cmame.tex`. The proof chain
is deliberately scoped: the smooth accepted-path assumptions imply
conditional sixth-order inheritance for `Gauss6/FullVA`, the artifact contract
adds the 7.161/7.066 h-sweep and four-example validation evidence, and the
claim boundary keeps source-policy reproduction, external superiority, and
`full_tfe_stage_replacement=false` outside the accepted statement.

The same proof boundary now explicitly keeps residual-to-error promotion out of
the accepted order claim. No residual error theorem is accepted in the
manuscript. Seven residual-to-error obligations remain blocking, and the
`four_link`/`slider_crank` residual rows remain mechanism-coverage evidence;
they are not accepted dynamic order rows.

The independent full-TFE row also records the newest direct
translation/angular cross-coupling follow-up: 8 local rows in 35.3 seconds,
best law `stage2_velocity_angular_to_translation_cross_feature`, projection
residual `0.898812`, rank-eight/no-span, dominant remaining family
`translation_velocity_v` at fraction `0.556004`, and stage-2 fraction
`0.999994`. This is worse than the expanded active-law grid's `0.576548`, so
the simple translation/angular outer-cross coefficient-gradient rows are
excluded before the bilinear and componentwise follow-ups.

The newest endpoint-pose velocity-predictor localization improves the same
local residual to `0.117782` using
`paper_endpoint_pose_positive_lagrange_z`, but it still has rank-eight/no-span,
dominant remaining family `translation_velocity_v` at fraction `0.514237`, and
stage fractions `0.961546`, `0.004167`, and `0.034287`. The full-TFE gate
therefore stays open.

A Gauss endpoint-pose velocity-predictor screen tests the analogous predictor
family built directly from Gauss stage positions. It covers `7` local rows in
`28.7` seconds. The best law is `gauss_endpoint_pose_positive_lagrange_z`, with
projection residual `0.208599`, rank-eight/no-span, dominant remaining family
`lie_position_u` at fraction `0.650605`, and stage fractions `0.524567`,
`0.209731`, and `0.265702`. Because this is worse than the paper endpoint-pose
positive-Lagrange residual `0.117782`, it is a ruled-out endpoint-pose
alternative.

A remaining Gauss endpoint-pose completion screen covers the untried quarter,
stage1-half, convex, and mean predictor rows: `11` local rows in `31.5`
seconds. The best law is `gauss_endpoint_pose_stage02_convex_0p00_z`, with
projection residual `0.172659`, independent target rank `6`, rank-six/no-span,
dominant remaining family `lie_position_u` at fraction `0.952340`, and stage
fractions `0.320394`, `0.305625`, and `0.373981`. This improves over the first
Gauss endpoint-pose screen but still does not beat the paper endpoint-pose
positive-Lagrange residual `0.117782`, so the simple Gauss endpoint-pose family
is excluded.

A near-terminal convex predictor screen adds the degeneracy boundary:
`paper_endpoint_pose_stage02_convex_0p00_z` spans locally at roundoff but is
terminal-bridge equivalent, while the best nonterminal law
`paper_endpoint_pose_stage02_convex_0p05_z` reaches residual `0.049317` with
rank-eight/no-span and `nonterminal_span_row_count=0`. Focused h-scaling
reruns at `h=0.02` and `h=0.01` keep the terminal-equivalent row at roundoff
span but leave the same nonterminal law at residuals `0.051890` and `0.052472`,
so the paper records this as a persistent nonterminal weak-row gap rather than
an h=0.04 artifact.

The synchronized pose/velocity near-terminal follow-up improves localization:
`stage02_convex_pose_velocity_0p01_z` reaches residual `0.009512`, while
`h=0.02` and `h=0.01` reruns give `0.009978` and `0.010085`. It still has
rank-eight/no-span, and the larger offsets `0p02`, `0p05`, and `0p10` give
`0.019205`, `0.049390`, and `0.103464`, so this remains a near-terminal
asymptote rather than an accepted independent full-TFE row.

The terminal-limit extrapolation follow-up reaches residual `4.699e-06` with
`stage02_convex_pose_velocity_extrapolate_0p01_0p02_z`; `h=0.02` and `h=0.01`
give `2.335e-06` and `1.168e-06`, while `0p01/0p05` gives `1.175e-05`. It is
marked `terminal_bridge_equivalent_predictor=true` and still has no span, so
the claim remains open.

A nonterminal slope follow-up then tests the finite-difference slope of the
same near-terminal convex pose/velocity rows. It covers 4 local rows in 25.8
seconds at `h=0.04`, keeps rank `132`, and has max residual `2.483e-12`. The
best law is `stage02_convex_pose_velocity_slope_0p01_0p05_z`, but its
projection residual is only `0.677034`, independent target rank remains `8`,
and `any_candidate_spans_terminal_bridge=false`; this rules out the first
nonterminal slope as the missing coefficient-gradient row.

A nonterminal curvature follow-up then tests the second finite-difference
curvature of the same near-terminal convex pose/velocity rows. It covers 4
local rows in 26.7 seconds at `h=0.04`, keeps rank `132`, and has max residual
`2.483e-12`. The best law is
`stage02_convex_pose_velocity_curvature_0p01_0p05_0p10_z`, but its projection
residual is only `0.871228`, independent target rank remains `8`, dominant
remaining family is `translation_velocity_v` at fraction `0.591909`, and
`any_candidate_spans_terminal_bridge=false`; this rules out the local
second-derivative curvature as the missing coefficient-gradient row.

A source/history coefficient-feature matrix follow-up then tests recurrent
source features as shifted-column coefficient matrices on the stage-2
lower-pair velocity row. It covers 16 local rows in 44.8 seconds at `h=0.04`,
keeps rank `132`, and has max residual `2.483e-12`. The best law is
`source_curvature_shifted_column_broadcast_feature`, but its projection
residual is only `0.898873`, independent target rank remains `8`, dominant
remaining family is `translation_velocity_v` at fraction `0.556060`, stage-2
fraction is `1.000000`, and `any_candidate_spans_terminal_bridge=false`; this
rules out the tested recurrent source/history coefficient features as the
missing coefficient-gradient row.

A nonlinear recurrent curvature/history matrix-feature follow-up tests
source-curvature minus history-delta, source/history Hadamard, unit-Hadamard,
and normalized curvature-plus-history feature prefixes. It covers 16 local rows
in 45.5 seconds at `h=0.04`, keeps rank `132`, and has
`any_candidate_spans_terminal_bridge=false`. The best law is
`source_curvature_minus_history_delta_diagonal_plus_row_broadcast_feature`, but
its projection residual is only `0.898865`, independent target rank remains
`8`, dominant remaining family is `translation_velocity_v` at fraction
`0.556051`, and stage-2 fraction is `0.999996`; this rules out these nonlinear
recurrent curvature/history matrix features.

A terminal-limit source-lift matrix-difference follow-up then tests whether
the best near-terminal extrapolated intercept can be repaired by adding a
stage-local `C_v` source-to-velocity lift before extrapolation. It covers 8
local rows in 47.5 seconds at `h=0.04`, keeps rank `132`, and has max residual
`2.483e-12`. The best law is
`stage02_convex_pose_velocity_extrapolate_0p01_0p02_sourceliftmatrixdiff_curvature_m0p1_z`,
but its projection residual is only `5.298e-06`, independent target rank
remains `8`, dominant remaining family is `translation_acceleration_a` at
fraction `0.407672`, and `any_candidate_spans_terminal_bridge=false`; this
rules out the tested terminal-limit `C_v` source-lift matrix-difference
correction as the missing coefficient-gradient row.

A curvature source-lift scale refinement then tests the uncorrected
terminal-limit extrapolated row plus signed curvature lift coefficients
`0.01`, `0.05`, `0.1`, `0.2`, and `0.5`. It covers 11 local rows in 52.9
seconds, keeps rank `132`, and has max residual `2.483e-12`. The best law is
`stage02_convex_pose_velocity_extrapolate_0p01_0p02_sourceliftmatrixdiff_curvature_p0p01_z`,
but its projection residual remains `5.298e-06`, independent target rank
remains `8`, dominant remaining family is `translation_acceleration_a` at
fraction `0.407672`, stage fractions are `0.549481`, `0.005742`, and
`0.444777`, and `source_curvature_norm` is only `1.076e-14`. This rules out a
simple source-lift scale correction as the missing coefficient-gradient row.

A mean-acceleration bridge scale refinement then tests the same terminal-limit
extrapolated row plus signed bridge coefficients `0.01`, `0.05`, `0.1`,
`0.2`, and `0.5`. It covers 11 local rows in 31.4 seconds, keeps rank `132`,
and has max residual `2.483e-12`. The overall best row remains the
terminal-bridge-equivalent uncorrected extrapolated row at residual
`5.298e-06`. The best nonterminal law is
`stage02_convex_pose_velocity_extrapolate_0p01_0p02_accel_p0p01_z`, but its
projection residual is still `0.000867721`, independent target rank remains
`8`, dominant remaining family is `lie_position_u` at fraction `0.706665`, and
`any_candidate_spans_terminal_bridge=false`. This rules out a simple small
mean-acceleration bridge coefficient as the missing coefficient-gradient row.

A generalized-acceleration Taylor-shift scale refinement then tests the same
terminal-limit extrapolation with separate left/right $h\dot z$ shifts and
signed coefficients `0.01`, `0.05`, `0.1`, `0.2`, and `0.5`. It covers 11
local rows in 30.2 seconds, keeps rank `132`, and has max residual
`2.483e-12`. The overall best row remains the terminal-bridge-equivalent
uncorrected extrapolated row at residual `5.298e-06`. The best nonterminal law
is
`stage02_convex_pose_velocity_extrapolate_0p01_0p02_genaccel_p0p01_z`, but its
projection residual is still `0.000866899`, independent target rank remains
`8`, dominant remaining family is `lie_position_u` at fraction `0.701135`, and
`any_candidate_spans_terminal_bridge=false`. This rules out the tested
stage-local generalized-acceleration Taylor shift as the missing
coefficient-gradient row.

A pose-acceleration Taylor-shift scale refinement then tests the same
terminal-limit extrapolation with separate left/right $h^2\dot z$ shifts added
to the evaluated pose before forming the endpoint velocity row. It covers 11
local rows in 29.9 seconds, keeps rank `132`, and has max residual
`2.483e-12`. The overall best row remains the terminal-bridge-equivalent
uncorrected extrapolated row at residual `5.298e-06`. The best nonterminal law
is
`stage02_convex_pose_velocity_extrapolate_0p01_0p02_poseaccel_p0p01_z`, but its
projection residual is still `4.1835e-05`, independent target rank remains
`8`, dominant remaining family is `lie_position_u` at fraction `0.711570`,
stage-2 fraction is `0.771337`, and
`any_candidate_spans_terminal_bridge=false`. This pose-directed perturbation
improves on the velocity-only generalized-acceleration shift but still does
not provide the independent correction row.

A tiny pose-acceleration scale refinement then tests the same law with signed
coefficients `0.0005`, `0.001`, `0.002`, and `0.005`, plus the prior positive
`0.01` row. It covers 10 local rows in 30.0 seconds, keeps rank `132`, and has
max residual `2.483e-12`. The overall best row remains the
terminal-bridge-equivalent uncorrected extrapolated row at residual
`5.298e-06`. The best nonterminal law is
`stage02_convex_pose_velocity_extrapolate_0p01_0p02_poseaccel_p0p0005_z`, but
its projection residual is still `5.5898e-06`, independent target rank remains
`8`, dominant remaining family is `translation_acceleration_a` at fraction
`0.350240`, and `any_candidate_spans_terminal_bridge=false`. This shows the
small-coefficient limit only approaches the terminal-equivalent row and still
does not provide an independent correction row.

A pose+velocity acceleration Taylor refinement then combines the small
`h^2*zdot` pose shift with signed small `h*zdot` velocity shifts. It covers 11
local rows in 30.7 seconds, keeps rank `132`, and has max residual
`2.483e-12`. The overall best row remains the terminal-bridge-equivalent
uncorrected extrapolated row at residual `5.298e-06`. The best nonterminal law
is
`stage02_convex_pose_velocity_extrapolate_0p01_0p02_posevelaccel_p0p0005_m0p0001_z`,
but its projection residual is still `1.0173e-05`, independent target rank
remains `8`, dominant remaining family is `lie_position_u` at fraction
`0.544660`, and `any_candidate_spans_terminal_bridge=false`. This simple
combined Taylor correction also does not provide an independent correction row.

A component-split pose-acceleration Taylor refinement then splits the same
`h^2*zdot` pose shift into translation-only and angular/Lie-only branches. Two
JSON-only screens cover 26 local rows in `32.3+32.3` seconds, keep rank `132`,
and have max residual `2.483e-12`. The overall best row remains the
terminal-bridge-equivalent uncorrected extrapolated row at residual
`5.298e-06`. The best nonterminal split law is
`stage02_convex_pose_velocity_extrapolate_0p01_0p02_transposeaccel_m0p01_z`,
also at residual `5.298e-06`, independent target rank `8`, dominant remaining
family `translation_acceleration_a` at fraction `0.407672`, and
`any_candidate_spans_terminal_bridge=false`. The angular-only branch reproduces
the full pose-acceleration trend: `angposeaccel_p0p002` reaches `9.6511e-06`
and `angposeaccel_p0p01` reaches `4.1835e-05`. This rules out translation-only
pose acceleration as the missing independent row and localizes the previous
pose-acceleration effect to angular/Lie pose.

A component-split velocity-acceleration Taylor refinement then splits the
`h*zdot` generalized-velocity shift into translational and angular velocity
branches. The first JSON-only screen covers 13 local rows in `31.8` seconds,
keeps rank `132`, and has no span. The best nonterminal row is
`stage02_convex_pose_velocity_extrapolate_0p01_0p02_transvelaccel_m0p01_z`,
with projection residual `2.138e-04`, independent target rank `8`, dominant
remaining family `translation_acceleration_a` at fraction `0.886603`, and
stage-2 fraction `0.812539`. The best angular velocity branch is
`angvelaccel_p0p01`, with residual `0.000864560` and dominant
`lie_position_u`. A tiny translational scale follow-up covers 11 local rows in
`31.4` seconds and still has no span; its best law is
`stage02_convex_pose_velocity_extrapolate_0p01_0p02_transvelaccel_m0p0005_z`,
with residual `9.8175e-06`, still worse than the uncorrected terminal-limit
residual `5.298e-06`. This rules out the tested component-split
velocity-acceleration Taylor shift as the missing independent row.

A component-mixed pose/velocity Taylor refinement then combines angular/Lie
pose shift with translational velocity shift, plus the complementary
translation-pose/angular-velocity branch. The JSON-only screen covers 13 local
rows in `32.0` seconds, keeps rank `132`, and has no span. The best
nonterminal law is
`stage02_convex_pose_velocity_extrapolate_0p01_0p02_angpose_transvelaccel_p0p0005_m0p0005_z`,
with projection residual `9.987e-06`, independent target rank `8`, dominant
remaining family `translation_acceleration_a` at fraction `0.774582`, and
stage-2 fraction `0.625975`. The complementary `transpose_angvelaccel` branch
reaches only `0.000864560`. This is still worse than the uncorrected
terminal-limit residual `5.298e-06`, so the tested component-mixed Taylor
cross term is also excluded.

A stage-2-fixed/delta acceleration velocity-shift refinement then tests whether
the remaining `translation_acceleration_a` direction comes from using the
interpolated acceleration source. The JSON-only screen covers 13 local rows in
`31.8` seconds, keeps rank `132`, and has no span. The best nonterminal law is
`stage02_convex_pose_velocity_extrapolate_0p01_0p02_transvelaccelstage2_m0p0005_z`,
with projection residual `9.8175e-06`, independent target rank `8`, dominant
remaining family `translation_acceleration_a` at fraction `0.802349`, and
stage-2 fraction `0.622536`. The best delta20 branch,
`stage02_convex_pose_velocity_extrapolate_0p01_0p02_transvelacceldelta20_m0p0005_z`,
reaches only `1.0119e-05`. This reproduces the earlier tiny translational
velocity-shift limit and is also excluded.

A nonfinal terminal velocity/source predictor refinement then tests whether a
stage0/1-only integral predictor can supply the terminal closure Jacobian. The
JSON-only screen covers 9 local rows in `30.9` seconds, keeps rank `132`, and
has no span. The best nonterminal law is `nonfinal_velocity_terminal_euler1_z`,
with projection residual `0.923466`, independent target rank `8`, dominant
remaining family `translation_velocity_v` at fraction `0.526951`, and stage-2
fraction `0.959959`. The other tested linear, Euler0, Adams-Bashforth,
source-mean, source-linear, and Hermite variants all stay between `0.923466`
and `0.930013`. This rules out the plain nonfinal velocity/source terminal
predictor family.
The bounded trajectory promotion of this family is also negative. The stage0/1
set converges all `24` rows in `135.3` seconds with rank `132` and
`projection_used=false`, but the best max terminal velocity is only
`1.770e-07`; `euler1/ab01/source01linear1` remain at `3.584e-07`. The stage0/1/2
extension converges all `18` rows in `101.1` seconds but has
`terminal_velocity_closed=false`: `euler2/ab12/source12mean2/source12linear2`
reach `2.559e-11` at `h=0.04` and `1.328e-07` at `h=0.02`, while `linear012`
is only `1.134e-07`.

A stage-2 source-to-velocity transport refinement then applies the existing
source/history-to-generalized-velocity projection directly at the stage-2
pose/velocity closure. The first JSON-only screen covers 13 local rows in
`53.4` seconds, keeps rank `132`, and has no span. The best nonterminal law is
`stage02_convex_pose_velocity_0p00_sourceliftmatrixdiff_historydelta_m0p1_z`,
with projection residual `0.001251`, independent target rank `6`, dominant
remaining family `lie_position_u` at fraction `0.597218`, and stage-2 fraction
`0.476626`. A scale refinement over the same matrix-difference history-delta
family covers 11 local rows in `57.7` seconds and improves the best residual to
`0.0001251` at
`stage02_convex_pose_velocity_0p00_sourceliftmatrixdiff_historydelta_m0p01_z`,
still with independent target rank `6` and no span. An ultra-fine scale
refinement covers 9 local rows in `49.6` seconds and pushes the best
nonterminal residual to `1.251e-06` at
`stage02_convex_pose_velocity_0p00_sourceliftmatrixdiff_historydelta_m0p0001_z`,
again with independent target rank `6` and no span. This is the strongest
nonterminal transport clue so far, but not an accepted full-TFE row. A combined
source-transport/angular-pose follow-up covers 8 local rows in `48.7` seconds.
The source-only row remains best at `1.251e-06`; the best combined row is
`stage02_convex_pose_velocity_0p00_sourceliftmatrixdiff_historydelta_m0p0001_angposeaccel_p0p0001_z`
at residual `1.296e-06`, independent target rank `8`, and no span.
The bare endpoint-pose velocity follow-up covers `3` local rows in `31.7`
seconds and finds that `stage02_convex_pose_velocity_0p00_z` spans locally at
residual `1.327e-15`, with independent target rank `0` and
`span_row_count=1`. The ultra-fine transported row remains no-span, so the
paper records this as local-span-not-full-TFE evidence rather than an accepted
replacement.
The bounded nonlinear trajectory smoke then promotes the same family into the
full residual. The smooth-only three-h `0p00` refinement closes terminal
velocity to `8.124e-17`, but yields position/velocity orders `4.142/2.305`.
The default `0p01` smoke leaves terminal velocity at `6.255e-06`. This records
a trajectory-level terminal/order split, not an acceptance claim.
The non-projection `0p01/0p02` extrapolated row improves terminal velocity to
`1.254e-07` and gives default orders `6.412/3.775`, but the three-h refinement
falls to `4.054/2.364`, so it remains diagnostic.
Closer non-projection extrapolation confirms that the improvement is a terminal
limit rather than an accepted repair. The `0p005/0p01`, `0p002/0p005`, and
`0p001/0p002` default smokes have terminal velocities
`3.135e-08`/`6.270e-09`/`1.254e-09`, but velocity orders only
`4.648`/`4.566`/`4.521`; the three-h `0p001/0p002` refinement has orders
`4.143/2.307`. The ultra-near
`stage02_convex_pose_velocity_extrapolate_0p00001_0p00002_z` row closes
terminal velocity without projection at `1.254e-13` and finest-h
`1.254e-14`, but the three-h order remains `4.142/2.305` with
`smooth_order_ok=false`.
The quadratic nonterminal extrapolation follow-up adds
`stage02_convex_pose_velocity_quadextrapolate_*` laws. The two-h
`0p01/0p02/0p05`, `0p005/0p01/0p02`, and `0p002/0p005/0p01` smokes have
terminal velocities `2.029e-11`/`2.029e-12`/`2.029e-13` and velocity order
about `4.508`. The best three-h row,
`stage02_convex_pose_velocity_quadextrapolate_0p002_0p005_0p01_z`, has
`projection_used=false`, terminal velocity `2.029e-13`, finest-h terminal
velocity `8.254e-15`, and order `4.142/2.305`.
Projection-like terminal-tangent damping does not repair that split: the full
`0p01_terminalproj` law diverges at `6.739e+08`, while damped `p0p1` and
`p0p5` variants leave terminal velocities `7.028e-06` and `1.321e-05` with
orders `2.301/1.788` and `2.158/1.433`.

The mean-acceleration bridge correction follow-up tests
`stage02_convex_pose_velocity_extrapolate_0p01_0p02_accel_m1_z` and
`stage02_convex_pose_velocity_extrapolate_0p01_0p02_accel_p1_z`. The best
signed bridge correction residual is only `0.076159`, and the missing direction
shifts to `lie_position_u`; this excludes the direct centered-bridge
acceleration term as the independent correction.

## Status Tokens

The paper deliberately keeps these machine-readable status tokens visible:

- `four_asme_method_rows_accepted_projection_sharp_sparse_caveats`
- `full_tfe_stage_replacement=false`
- `lower_pair_recurrent_weak_closure_smoke`
- `lower_pair_recurrent_terminal_blend_h_sweep_smoke`
- `lower_pair_recurrent_terminal_component_one_step_smoke`
- `lower_pair_recurrent_terminal_component_h_sweep_smoke`
- `lower_pair_recurrent_stage2_gradient_differential_audit`
- `lower_pair_recurrent_stage2_matrix_gradient_differential_audit`
- recurrent weak-closure smoke residual `6.737e-13`
- recurrent weak-closure smoke residual `6.484e-13`
- recurrent weak-closure trajectory-smoke residual `2.483e-12`
- recurrent weak-closure trajectory-smoke terminal velocity `7.994e-06`
- recurrent weak-closure h-sweep-smoke residual `4.463e-12`
- recurrent weak-closure h-sweep-smoke terminal velocity `8.234e-06`
- recurrent weak-closure h-sweep-smoke min velocity order `-0.428`
- recurrent weak-closure full-shaped h-sweep residual `9.998e-12`
- recurrent weak-closure full-shaped h-sweep smooth orders `5.317/6.782`
- recurrent weak-closure full-shaped h-sweep sharp orders `2.555/1.918`
- recurrent-terminal blend best terminal gamma `1.0`
- recurrent-terminal blend best terminal velocities `7.845e-17`/`9.479e-17`
- recurrent-terminal blend best residuals `6.071e-13`/`3.533e-13`
- recurrent-terminal blend h-sweep residual `3.260e-12`
- recurrent-terminal blend h-sweep residual `4.766e-12`
- recurrent-terminal blend h-sweep terminal velocity `3.049e-16`
- recurrent-terminal blend h-sweep sharp terminal velocity `2.941e-16`
- recurrent-terminal blend h-sweep best smooth order `4.413`
- recurrent-terminal blend h-sweep gamma-one smooth order `4.397`
- recurrent-terminal blend h-sweep sharp velocity order `-0.428`
- recurrent-terminal dense gamma grid `0,0.25,0.5,0.75,1`
- recurrent-terminal dense gamma steps `60`
- recurrent-terminal dense gamma best smooth order `4.414`
- recurrent-terminal dense gamma best smooth-order gamma `0.75`
- recurrent-terminal dense gamma max terminal velocity `8.234e-06`
- recurrent-terminal near-terminal gamma grid `0.9,0.99,0.999,1`
- recurrent-terminal near-terminal gamma steps `48`
- recurrent-terminal near-terminal best smooth order `4.415`
- recurrent-terminal near-terminal best smooth-order gamma `0.99`
- recurrent-terminal near-terminal gamma 0.999 terminal velocity `4.678e-07`
- recurrent-terminal component gamma vectors `10`
- recurrent-terminal component one-step rows `20`
- recurrent-terminal component max residual `1.766e-12`
- recurrent-terminal component nontrivial terminal-closed count `5`
- recurrent-terminal component best nontrivial `component_2_release_0p999`
- recurrent-terminal component best terminal velocity `3.456e-17`
- recurrent-terminal component worst release `component_7_release_0p999`
- recurrent-terminal component worst terminal velocity `1.234e-11`
- recurrent-terminal component trajectory steps `48`
- recurrent-terminal component trajectory elapsed `98.4`
- recurrent-terminal component trajectory residual `4.766e-12`
- recurrent-terminal component trajectory best terminal `2.696e-16`
- recurrent-terminal component trajectory best smooth order `4.401`
- recurrent-terminal component trajectory terminal blocker `4.678e-07`
- recurrent-terminal component trajectory intersection `order_terminal_intersection_present=false`
- recurrent stage-2 matrix-gradient elapsed `68.1`
- recurrent stage-2 matrix-gradient rows `32`
- recurrent stage-2 matrix-gradient best law `diagonal_plus_row_broadcast_feature`
- recurrent stage-2 matrix-gradient residual `0.898873`
- recurrent stage-2 matrix-gradient max closure delta `4.005e-09`
- recurrent stage-2 active-velocity matrix-gradient elapsed `46.6`
- recurrent stage-2 active-velocity matrix-gradient best law `stage2_velocity_column_broadcast_feature`
- recurrent stage-2 active-velocity matrix-gradient residual `0.585746`
- recurrent stage-2 active-velocity matrix-gradient max closure delta `1.460e-06`
- recurrent stage-2 expanded active-law grid elapsed `51.2`
- recurrent stage-2 expanded active-law grid best law `stage2_velocity_shifted_column_broadcast_feature`
- recurrent stage-2 expanded active-law grid residual `0.576548`
- recurrent stage-2 best-law missing-direction elapsed `27.8`
- recurrent stage-2 best-law missing-direction dominant variable `angular_velocity_w`
- recurrent stage-2 best-law missing-direction dominant fraction `0.502991`
- recurrent stage-2 best-law missing-direction stage-2 fraction `0.963038`
- recurrent stage-2 angular-mask grid elapsed `35.3`
- recurrent stage-2 angular-mask rows `8`
- recurrent stage-2 angular-mask best law `stage2_angular_velocity_shifted_column_broadcast_feature`
- recurrent stage-2 angular-mask residual `0.752997`
- recurrent stage-2 angular-mask remaining dominant variable `translation_velocity_v`
- recurrent stage-2 angular-mask remaining dominant fraction `0.660361`
- recurrent stage-2 angular-mask stage-2 fraction `0.978093`
- recurrent stage-2 translation/angular cross grid elapsed `35.3`
- recurrent stage-2 translation/angular cross rows `8`
- recurrent stage-2 translation/angular cross best law `stage2_velocity_angular_to_translation_cross_feature`
- recurrent stage-2 translation/angular cross residual `0.898812`
- recurrent stage-2 translation/angular cross remaining dominant variable `translation_velocity_v`
- recurrent stage-2 translation/angular cross remaining dominant fraction `0.556004`
- recurrent stage-2 translation/angular cross stage-2 fraction `0.999994`
- endpoint-pose velocity-predictor grid elapsed `31.2`
- endpoint-pose velocity-predictor rows `10`
- endpoint-pose velocity-predictor best law `paper_endpoint_pose_positive_lagrange_z`
- endpoint-pose velocity-predictor residual `0.117782`
- endpoint-pose velocity-predictor remaining dominant variable `translation_velocity_v`
- endpoint-pose velocity-predictor remaining dominant fraction `0.514237`
- endpoint-pose velocity-predictor stage fractions `0.961546/0.004167/0.034287`
- gauss endpoint-pose velocity-predictor rows `7`
- gauss endpoint-pose velocity-predictor elapsed `28.7`
- gauss endpoint-pose velocity-predictor best law `gauss_endpoint_pose_positive_lagrange_z`
- gauss endpoint-pose velocity-predictor residual `0.208599`
- gauss endpoint-pose velocity-predictor remaining dominant variable `lie_position_u`
- gauss endpoint-pose velocity-predictor remaining dominant fraction `0.650605`
- gauss endpoint-pose velocity-predictor stage fractions `0.524567/0.209731/0.265702`
- remaining gauss endpoint-pose rows `11`
- remaining gauss endpoint-pose elapsed `31.5`
- remaining gauss endpoint-pose best law `gauss_endpoint_pose_stage02_convex_0p00_z`
- remaining gauss endpoint-pose residual `0.172659`
- remaining gauss endpoint-pose independent target rank `6`
- remaining gauss endpoint-pose dominant variable `lie_position_u`
- remaining gauss endpoint-pose dominant fraction `0.952340`
- remaining gauss endpoint-pose stage fractions `0.320394/0.305625/0.373981`
- near-terminal convex predictor rows `14`
- near-terminal convex predictor elapsed `31.7`
- near-terminal convex predictor terminal-equivalent law `paper_endpoint_pose_stage02_convex_0p00_z`
- near-terminal convex predictor nonterminal best law `paper_endpoint_pose_stage02_convex_0p05_z`
- near-terminal convex predictor nonterminal residual `0.049317`
- near-terminal convex predictor nonterminal h=0.02 residual `0.051890`
- near-terminal convex predictor nonterminal h=0.01 residual `0.052472`
- near-terminal convex predictor h-scaling persistent nonterminal gap
- near-terminal convex predictor nonterminal span count `0`
- synchronized pose/velocity predictor best law `stage02_convex_pose_velocity_0p01_z`
- synchronized pose/velocity predictor residual `0.009512`
- synchronized pose/velocity predictor h=0.02 residual `0.009978`
- synchronized pose/velocity predictor h=0.01 residual `0.010085`
- synchronized pose/velocity predictor offset residuals `0.019205/0.049390/0.103464`
- synchronized pose/velocity predictor rank-eight/no-span
- synchronized pose/velocity extrapolate law `stage02_convex_pose_velocity_extrapolate_0p01_0p02_z`
- synchronized pose/velocity extrapolate residual `4.699e-06`
- synchronized pose/velocity extrapolate h=0.02 residual `2.335e-06`
- synchronized pose/velocity extrapolate h=0.01 residual `1.168e-06`
- synchronized pose/velocity extrapolate wide residual `1.175e-05`
- synchronized pose/velocity extrapolate terminal-equivalent no-span
- synchronized pose/velocity accel correction laws `stage02_convex_pose_velocity_extrapolate_0p01_0p02_accel_m1_z` and `stage02_convex_pose_velocity_extrapolate_0p01_0p02_accel_p1_z`
- synchronized pose/velocity accel correction best residual `0.076159`
- synchronized pose/velocity accel correction missing direction `lie_position_u`
- recurrent stage-2 bilinear outer-product grid elapsed `57.3`
- recurrent stage-2 bilinear outer-product grid rows `24`
- recurrent stage-2 bilinear outer-product best law `stage2_velocity_feature_outer_stage2_velocity`
- recurrent stage-2 bilinear outer-product residual `0.898720`
- recurrent stage-2 componentwise diagonal grid elapsed `56.7`
- recurrent stage-2 componentwise diagonal grid rows `24`
- recurrent stage-2 componentwise diagonal best law `stage2_velocity_diagonal_plus_hadamard_row_feature_stage2_velocity`
- recurrent stage-2 componentwise diagonal residual `0.898530`
- nonterminal mean-acceleration correction rows `18`
- nonterminal mean-acceleration correction best law `stage02_convex_pose_velocity_0p01_z`
- nonterminal mean-acceleration correction best corrected residual `0.012376`
- nonterminal mean-acceleration correction unit-correction floor `0.077874`
- nonterminal mean-acceleration correction span count `0`
- generalized-velocity acceleration predictor rows `18`
- generalized-velocity acceleration predictor best law `stage02_convex_pose_velocity_0p01_z`
- generalized-velocity acceleration predictor best corrected residual `0.012376`
- generalized-velocity acceleration predictor unit-correction floor `0.077874`
- generalized-velocity acceleration predictor span count `0`
- kinematic pose-slope predictor rows `26`
- kinematic pose-slope predictor best law `stage02_convex_pose_velocity_0p01_z`
- kinematic pose-slope predictor best corrected law `stage02_convex_pose_velocity_0p02_poseslope_m0p1_z`
- kinematic pose-slope predictor best corrected residual `0.878519`
- kinematic pose-slope predictor span count `0`
- source-to-velocity lift predictor rows `34`
- source-to-velocity lift predictor elapsed `76.4`
- source-to-velocity lift predictor best law `stage02_convex_pose_velocity_0p01_z`
- source-to-velocity lift predictor best corrected law `stage02_convex_pose_velocity_0p01_sourcelift_historydelta_p1_z`
- source-to-velocity lift predictor tied corrected law `stage02_convex_pose_velocity_0p01_sourcelift_source0_p1_z`
- source-to-velocity lift predictor best corrected residual `0.609803`
- source-to-velocity lift predictor span count `0`
- matrix-difference source-to-velocity lift predictor rows `14`
- matrix-difference source-to-velocity lift predictor elapsed `58.7`
- matrix-difference source-to-velocity lift predictor coarse residual `0.042593`
- matrix-difference source-to-velocity lift scale-sweep rows `26`
- matrix-difference source-to-velocity lift scale-sweep elapsed `92.5`
- matrix-difference source-to-velocity lift scale-sweep best corrected law `stage02_convex_pose_velocity_0p01_sourceliftmatrixdiff_historydelta_p0p1_z`
- matrix-difference source-to-velocity lift scale-sweep best corrected residual `0.009527`
- matrix-difference source-to-velocity lift predictor span count `0`
- normalized-history source-law rows `10`
- normalized-history source-law elapsed `49.4`
- normalized-history source-law best corrected law `stage02_convex_pose_velocity_0p01_sourceliftmatrixdiff_historyunitdelta_p0p1_z`
- normalized-history source-law best corrected residual `0.009590`
- normalized-history source-law span count `0`
- near-terminal slope follow-up rows `4`
- near-terminal slope follow-up elapsed `25.8`
- near-terminal slope follow-up best law `stage02_convex_pose_velocity_slope_0p01_0p05_z`
- near-terminal slope follow-up best residual `0.677034`
- near-terminal slope follow-up span count `0`
- near-terminal curvature follow-up rows `4`
- near-terminal curvature follow-up elapsed `26.7`
- near-terminal curvature follow-up best law `stage02_convex_pose_velocity_curvature_0p01_0p05_0p10_z`
- near-terminal curvature follow-up best residual `0.871228`
- near-terminal curvature follow-up dominant family `translation_velocity_v`
- near-terminal curvature follow-up span count `0`
- source/history coefficient-feature matrix follow-up rows `16`
- source/history coefficient-feature matrix follow-up elapsed `44.8`
- source/history coefficient-feature matrix follow-up best law `source_curvature_shifted_column_broadcast_feature`
- source/history coefficient-feature matrix follow-up best residual `0.898873`
- source/history coefficient-feature matrix follow-up dominant family `translation_velocity_v`
- source/history coefficient-feature matrix follow-up stage2 fraction `1.000000`
- source/history coefficient-feature matrix follow-up span count `0`
- nonlinear curvature/history matrix-feature follow-up rows `16`
- nonlinear curvature/history matrix-feature follow-up elapsed `45.5`
- nonlinear curvature/history matrix-feature follow-up best law `source_curvature_minus_history_delta_diagonal_plus_row_broadcast_feature`
- nonlinear curvature/history matrix-feature follow-up best residual `0.898865`
- nonlinear curvature/history matrix-feature follow-up dominant family `translation_velocity_v`
- nonlinear curvature/history matrix-feature follow-up dominant fraction `0.556051`
- nonlinear curvature/history matrix-feature follow-up stage2 fraction `0.999996`
- nonlinear curvature/history matrix-feature follow-up span count `0`
- terminal-limit source-lift matrix-difference follow-up rows `8`
- terminal-limit source-lift matrix-difference follow-up elapsed `47.5`
- terminal-limit source-lift matrix-difference follow-up best law `stage02_convex_pose_velocity_extrapolate_0p01_0p02_sourceliftmatrixdiff_curvature_m0p1_z`
- terminal-limit source-lift matrix-difference follow-up best residual `5.298e-06`
- terminal-limit source-lift matrix-difference follow-up dominant family `translation_acceleration_a`
- terminal-limit source-lift matrix-difference follow-up span count `0`
- curvature source-lift scale refinement rows `11`
- curvature source-lift scale refinement elapsed `52.9`
- curvature source-lift scale refinement best law `stage02_convex_pose_velocity_extrapolate_0p01_0p02_sourceliftmatrixdiff_curvature_p0p01_z`
- curvature source-lift scale refinement best residual `5.298e-06`
- curvature source-lift scale refinement source curvature norm `1.076e-14`
- curvature source-lift scale refinement span count `0`
- mean-acceleration bridge scale refinement rows `11`
- mean-acceleration bridge scale refinement elapsed `31.4`
- mean-acceleration bridge scale refinement best nonterminal law `stage02_convex_pose_velocity_extrapolate_0p01_0p02_accel_p0p01_z`
- mean-acceleration bridge scale refinement best nonterminal residual `0.000867721`
- mean-acceleration bridge scale refinement dominant family `lie_position_u`
- mean-acceleration bridge scale refinement span count `0`
- generalized-acceleration Taylor-shift scale refinement rows `11`
- generalized-acceleration Taylor-shift scale refinement elapsed `30.2`
- generalized-acceleration Taylor-shift scale refinement best nonterminal law `stage02_convex_pose_velocity_extrapolate_0p01_0p02_genaccel_p0p01_z`
- generalized-acceleration Taylor-shift scale refinement best nonterminal residual `0.000866899`
- generalized-acceleration Taylor-shift scale refinement dominant family `lie_position_u`
- generalized-acceleration Taylor-shift scale refinement span count `0`
- pose-acceleration Taylor-shift scale refinement rows `11`
- pose-acceleration Taylor-shift scale refinement elapsed `29.9`
- pose-acceleration Taylor-shift scale refinement best nonterminal law `stage02_convex_pose_velocity_extrapolate_0p01_0p02_poseaccel_p0p01_z`
- pose-acceleration Taylor-shift scale refinement best nonterminal residual `4.1835e-05`
- pose-acceleration Taylor-shift scale refinement dominant family `lie_position_u`
- pose-acceleration Taylor-shift scale refinement stage-2 fraction `0.771337`
- pose-acceleration Taylor-shift scale refinement span count `0`
- tiny pose-acceleration scale refinement rows `10`
- tiny pose-acceleration scale refinement elapsed `30.0`
- tiny pose-acceleration scale refinement best nonterminal law `stage02_convex_pose_velocity_extrapolate_0p01_0p02_poseaccel_p0p0005_z`
- tiny pose-acceleration scale refinement best nonterminal residual `5.5898e-06`
- tiny pose-acceleration scale refinement dominant family `translation_acceleration_a`
- tiny pose-acceleration scale refinement dominant fraction `0.350240`
- tiny pose-acceleration scale refinement span count `0`
- pose+velocity acceleration Taylor refinement rows `11`
- pose+velocity acceleration Taylor refinement elapsed `30.7`
- pose+velocity acceleration Taylor refinement best nonterminal law `stage02_convex_pose_velocity_extrapolate_0p01_0p02_posevelaccel_p0p0005_m0p0001_z`
- pose+velocity acceleration Taylor refinement best nonterminal residual `1.0173e-05`
- pose+velocity acceleration Taylor refinement dominant family `lie_position_u`
- pose+velocity acceleration Taylor refinement dominant fraction `0.544660`
- pose+velocity acceleration Taylor refinement span count `0`
- component-split pose-acceleration refinement rows `26`
- component-split pose-acceleration refinement elapsed `32.3+32.3`
- component-split pose-acceleration refinement best nonterminal law `stage02_convex_pose_velocity_extrapolate_0p01_0p02_transposeaccel_m0p01_z`
- component-split pose-acceleration refinement best nonterminal residual `5.298e-06`
- component-split pose-acceleration refinement angular residual `9.6511e-06`
- component-split pose-acceleration refinement span count `0`
- component-split velocity-acceleration refinement rows `13`
- component-split velocity-acceleration refinement elapsed `31.8`
- component-split velocity-acceleration refinement best nonterminal law `stage02_convex_pose_velocity_extrapolate_0p01_0p02_transvelaccel_m0p01_z`
- component-split velocity-acceleration refinement best nonterminal residual `2.138e-04`
- component-split velocity-acceleration refinement best angular law `angvelaccel_p0p01`
- component-split velocity-acceleration refinement best angular residual `0.000864560`
- component-split velocity-acceleration refinement span count `0`
- tiny translational velocity-acceleration scale rows `11`
- tiny translational velocity-acceleration scale elapsed `31.4`
- tiny translational velocity-acceleration scale best nonterminal law `stage02_convex_pose_velocity_extrapolate_0p01_0p02_transvelaccel_m0p0005_z`
- tiny translational velocity-acceleration scale best nonterminal residual `9.8175e-06`
- tiny translational velocity-acceleration scale span count `0`
- component-mixed pose/velocity Taylor refinement rows `13`
- component-mixed pose/velocity Taylor refinement elapsed `32.0`
- component-mixed pose/velocity Taylor refinement best nonterminal law `stage02_convex_pose_velocity_extrapolate_0p01_0p02_angpose_transvelaccel_p0p0005_m0p0005_z`
- component-mixed pose/velocity Taylor refinement best nonterminal residual `9.987e-06`
- component-mixed pose/velocity Taylor refinement dominant family `translation_acceleration_a`
- component-mixed pose/velocity Taylor refinement dominant fraction `0.774582`
- component-mixed pose/velocity Taylor refinement stage-2 fraction `0.625975`
- component-mixed pose/velocity Taylor refinement span count `0`
- stage-2-fixed/delta acceleration velocity-shift refinement rows `13`
- stage-2-fixed/delta acceleration velocity-shift refinement elapsed `31.8`
- stage-2-fixed/delta acceleration velocity-shift refinement best nonterminal law `stage02_convex_pose_velocity_extrapolate_0p01_0p02_transvelaccelstage2_m0p0005_z`
- stage-2-fixed/delta acceleration velocity-shift refinement best nonterminal residual `9.8175e-06`
- stage-2-fixed/delta acceleration velocity-shift refinement delta law `stage02_convex_pose_velocity_extrapolate_0p01_0p02_transvelacceldelta20_m0p0005_z`
- stage-2-fixed/delta acceleration velocity-shift refinement delta residual `1.0119e-05`
- stage-2-fixed/delta acceleration velocity-shift refinement dominant fraction `0.802349`
- stage-2-fixed/delta acceleration velocity-shift refinement stage-2 fraction `0.622536`
- stage-2-fixed/delta acceleration velocity-shift refinement span count `0`
- nonfinal terminal velocity/source predictor refinement rows `9`
- nonfinal terminal velocity/source predictor refinement elapsed `30.9`
- nonfinal terminal velocity/source predictor refinement best nonterminal law `nonfinal_velocity_terminal_euler1_z`
- nonfinal terminal velocity/source predictor refinement best nonterminal residual `0.923466`
- nonfinal terminal velocity/source predictor refinement dominant family `translation_velocity_v`
- nonfinal terminal velocity/source predictor refinement dominant fraction `0.526951`
- nonfinal terminal velocity/source predictor refinement stage-2 fraction `0.959959`
- nonfinal terminal velocity/source predictor refinement residual band `0.923466` to `0.930013`
- nonfinal terminal velocity/source predictor refinement span count `0`
- nonfinal velocity/source trajectory stage0/1 elapsed `135.3`
- nonfinal velocity/source trajectory stage0/1 rows `24`
- nonfinal velocity/source trajectory stage0/1 best terminal velocity `1.770e-07`
- nonfinal velocity/source trajectory stage0/1 order-friendly terminal velocity `3.584e-07`
- nonfinal velocity/source trajectory stage0/1 projection flag `projection_used=false`
- nonfinal velocity/source trajectory stage0/1/2 elapsed `101.1`
- nonfinal velocity/source trajectory stage0/1/2 rows `18`
- nonfinal velocity/source trajectory stage0/1/2 coarse terminal velocity `2.559e-11`
- nonfinal velocity/source trajectory stage0/1/2 fine terminal velocity `1.328e-07`
- nonfinal velocity/source trajectory stage0/1/2 stable terminal velocity `1.134e-07`
- stage-2 source-to-velocity transport refinement rows `13`
- stage-2 source-to-velocity transport refinement elapsed `53.4`
- stage-2 source-to-velocity transport refinement best nonterminal law `stage02_convex_pose_velocity_0p00_sourceliftmatrixdiff_historydelta_m0p1_z`
- stage-2 source-to-velocity transport refinement best nonterminal residual `0.001251`
- stage-2 source-to-velocity transport refinement scale rows `11`
- stage-2 source-to-velocity transport refinement scale elapsed `57.7`
- stage-2 source-to-velocity transport refinement scaled best law `stage02_convex_pose_velocity_0p00_sourceliftmatrixdiff_historydelta_m0p01_z`
- stage-2 source-to-velocity transport refinement scaled best residual `0.0001251`
- stage-2 source-to-velocity transport refinement ultra-fine rows `9`
- stage-2 source-to-velocity transport refinement ultra-fine elapsed `49.6`
- stage-2 source-to-velocity transport refinement ultra-fine best law `stage02_convex_pose_velocity_0p00_sourceliftmatrixdiff_historydelta_m0p0001_z`
- stage-2 source-to-velocity transport refinement ultra-fine best residual `1.251e-06`
- stage-2 source-to-velocity angular-pose combined rows `8`
- stage-2 source-to-velocity angular-pose combined elapsed `48.7`
- stage-2 source-to-velocity angular-pose combined best law `stage02_convex_pose_velocity_0p00_sourceliftmatrixdiff_historydelta_m0p0001_angposeaccel_p0p0001_z`
- stage-2 source-to-velocity angular-pose combined best residual `1.296e-06`
- stage-2 source-to-velocity angular-pose combined independent target rank `8`
- stage-2 source-to-velocity transport refinement independent target rank `6`
- stage-2 source-to-velocity transport refinement dominant family `lie_position_u`
- stage-2 source-to-velocity transport refinement dominant fraction `0.597218`
- stage-2 source-to-velocity transport refinement span count `0`
- bare endpoint-pose velocity local-span rows `3`
- bare endpoint-pose velocity local-span elapsed `31.7`
- bare endpoint-pose velocity local-span law `stage02_convex_pose_velocity_0p00_z`
- bare endpoint-pose velocity local-span residual `1.327e-15`
- bare endpoint-pose velocity local-span independent target rank `0`
- bare endpoint-pose velocity local-span span count `1`
- bare endpoint-pose velocity local-span status `local-span-not-full-TFE`
- endpoint-pose velocity predictor h-sweep target `lower_pair_endpoint_pose_velocity_predictor_h_sweep_smoke`
- endpoint-pose velocity predictor h-sweep default elapsed `21.5`
- endpoint-pose velocity predictor h-sweep default terminal velocity `7.29e-17`
- endpoint-pose velocity predictor h-sweep default orders `6.588/4.508`
- endpoint-pose velocity predictor h-sweep three-h elapsed `28.6`
- endpoint-pose velocity predictor h-sweep three-h terminal velocity `8.124e-17`
- endpoint-pose velocity predictor h-sweep three-h orders `4.142/2.305`
- endpoint-pose velocity predictor h-sweep nonterminal law `stage02_convex_pose_velocity_0p01_z`
- endpoint-pose velocity predictor h-sweep nonterminal terminal velocity `6.255e-06`
- endpoint-pose velocity predictor h-sweep nonterminal orders `2.345/1.878`
- source-transport trajectory follow-up elapsed `74.1`
- source-transport trajectory follow-up rank `132`
- source-transport trajectory follow-up source-only law `stage02_convex_pose_velocity_0p00_sourceliftmatrixdiff_historydelta_m0p0001_z`
- source-transport trajectory follow-up source-only terminal velocity `8.020e-12`
- source-transport trajectory follow-up source-only orders `6.588/4.508`
- source-transport trajectory follow-up angular-pose terminal velocity `2.102e-07`
- source-transport trajectory follow-up angular-pose velocity order `2.820`
- source-transport trajectory follow-up projection flag `projection_used=false`
- source-transport three-h refinement elapsed `46.4`
- source-transport three-h refinement max terminal velocity `8.020e-12`
- source-transport three-h refinement finest-h terminal velocity `5.904e-13`
- source-transport three-h refinement orders `4.142/2.305`
- source-transport three-h refinement rank `132`
- source-transport three-h refinement projection flag `projection_used=false`
- source-transport coefficient-limit law `stage02_convex_pose_velocity_0p00_sourceliftmatrixdiff_historydelta_m0p00001_z`
- source-transport coefficient-limit elapsed `43.6`
- source-transport coefficient-limit max terminal velocity `8.021e-13`
- source-transport coefficient-limit finest-h terminal velocity `5.910e-14`
- source-transport coefficient-limit terminal flag `terminal_velocity_closed=true`
- source-transport coefficient-limit orders `4.142/2.305`
- source-transport coefficient-limit smooth-order flag `smooth_order_ok=false`
- endpoint-pose extrapolated non-projection law `stage02_convex_pose_velocity_extrapolate_0p01_0p02_z`
- endpoint-pose extrapolated non-projection flag `projection_used=false`
- endpoint-pose extrapolated default elapsed `21.8`
- endpoint-pose extrapolated default terminal velocity `1.254e-07`
- endpoint-pose extrapolated default orders `6.412/3.775`
- endpoint-pose extrapolated three-h elapsed `28.9`
- endpoint-pose extrapolated three-h terminal velocity `1.254e-07`
- endpoint-pose extrapolated finest-h terminal velocity `1.244e-08`
- endpoint-pose extrapolated three-h orders `4.054/2.364`
- endpoint-pose closer extrapolated laws `0p005/0p01`, `0p002/0p005`, and `0p001/0p002`
- endpoint-pose closer extrapolated terminal velocities `3.135e-08/6.270e-09/1.254e-09`
- endpoint-pose closer extrapolated velocity orders `4.648/4.566/4.521`
- endpoint-pose ultra-near extrapolated law `stage02_convex_pose_velocity_extrapolate_0p00001_0p00002_z`
- endpoint-pose ultra-near extrapolated flag `projection_used=false`
- endpoint-pose ultra-near terminal velocity `1.254e-13`
- endpoint-pose ultra-near finest-h terminal velocity `1.254e-14`
- endpoint-pose ultra-near three-h orders `4.142/2.305`
- endpoint-pose ultra-near smooth-order flag `smooth_order_ok=false`
- endpoint-pose quadratic extrapolated laws `0p01/0p02/0p05`, `0p005/0p01/0p02`, and `0p002/0p005/0p01`
- endpoint-pose quadratic extrapolated terminal velocities `2.029e-11/2.029e-12/2.029e-13`
- endpoint-pose quadratic extrapolated best law `stage02_convex_pose_velocity_quadextrapolate_0p002_0p005_0p01_z`
- endpoint-pose quadratic extrapolated flag `projection_used=false`
- endpoint-pose quadratic extrapolated finest-h terminal velocity `8.254e-15`
- endpoint-pose quadratic extrapolated three-h orders `4.142/2.305`
- endpoint-pose terminal projection diagnostic law `stage02_convex_pose_velocity_0p01_terminalproj_z`
- endpoint-pose terminal projection full residual divergence `6.739e+08`
- endpoint-pose terminal projection damped p0p1 terminal velocity `7.028e-06`
- endpoint-pose terminal projection damped p0p1 orders `2.301/1.788`
- endpoint-pose terminal projection damped p0p5 terminal velocity `1.321e-05`
- endpoint-pose terminal projection damped p0p5 orders `2.158/1.433`
- endpoint-pose terminal projection diagnostic flag `projection_used=true`
- endpoint-pose velocity predictor h-sweep accepted flag `accepted_h_sweep_present=false`
- `run_v047.py` latest recorded full regeneration time: `2386.76` seconds
- ASME model tokens: `single_pendulum`, `double_pendulum`, `four_link`,
  `slider_crank`

## Validation Commands

Run from `paper_v047_cylindrical_chain`:

```bash
../.venv_sbel/bin/python validate_paper_package.py
../.venv_sbel/bin/python validate_paper_claims.py
```

Run from `v047_cylindrical_chain_pipeline`:

```bash
../.venv_sbel/bin/python validate_four_asme_minimal.py
../.venv_sbel/bin/python validate_full_tfe_gap.py
../.venv_sbel/bin/python validate_full_tfe_repair_spec.py
../.venv_sbel/bin/python validate_v047_outputs.py
```

Run the full numerical regeneration only after changing numerical method or
artifact-producing code:

```bash
../.venv_sbel/bin/python run_v047.py
```
