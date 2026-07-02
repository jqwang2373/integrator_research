# v047 Full TFE Replacement Gap Ledger

This ledger records the exact remaining gap between the accepted v047
Gauss6/FullVA method evidence and an independent full TFE stage replacement
claim. It is intentionally conservative: it explains what is already strong,
what is still open, and what evidence would be required before changing
`full_tfe_stage_replacement=false`.

## Current Status

- Four ASME method rows are accepted under
  `four_asme_method_rows_accepted_projection_sharp_sparse_caveats`.
- The source-free final-stage lower-pair velocity closure closes raw terminal
  endpoint velocity to about `4.011e-16`.
- The order/closure blend audit has
  `order_and_terminal_intersection_present=false`: beta values that preserve
  smooth order leave terminal velocity open, while beta `1` closes terminal
  velocity but has smooth position order `3.523`.
- The closure acceptance matrix has `accepted_candidate_count=0`.
- The velocity-compression audit keeps
  `accepted_h_sweep_present=false` and `full_tfe_stage_replacement=false`.
- The row-space compression audit tests `36` target-free rows with `0` spans,
  best projection residual `7.378e-01`, and best non-final projection residual
  `9.815e-01`.
- The row-space coefficient-derivative follow-up tests the same `36`
  rows after adding a target-direction coefficient-derivative oracle. It spans
  all `36` local tangents and has `24` value-balanced spans, with best
  derivative-inclusive residual `8.915e-16`; however it uses a target-direction
  oracle and requires coefficient-gradient norms up to `6.777e+18`, so the
  bounded target-free formula and nonlinear h-sweep remain missing.
- The weak-row structure-capacity audit tests `216` rows with `0` spans.
- The recurrent weak-row differential audit tests the current nonlinear weak
  row locally with `2` smooth rows, rank `132`, recurrent projection residuals
  `0.899` to `0.974`, final-stage comparison residual `1.456e-15`, and
  `any_recurrent_weak_spans_terminal_bridge=false`; the missing direction is
  stage-2 translational velocity.
- The recurrent stage-2 coefficient-gradient audit tests `8` target-free
  source/history-modulated stage-2 velocity rows with gains `[1e8,1e12]`,
  rank `132`, best projection residual `0.899`, independent target rank `8`,
  and `any_candidate_spans_terminal_bridge=false`.
- The recurrent stage-2 matrix-gradient audit tests `32` target-free
  row/column/bilinear matrix-mixed stage-2 velocity rows with gains
  `[1e8,1e12]`, rank `132`, best law
  `diagonal_plus_row_broadcast_feature`, best projection residual `0.898873`,
  independent target rank `8`, and
  `any_candidate_spans_terminal_bridge=false`.
- The recurrent stage-2 translation-velocity matrix-gradient audit tests `40`
  target-free translation-velocity matrix rows with gains `[1e8,1e12]`, rank
  `132`, best law
  `stage2_translation_velocity_symmetric_broadcast_feature`, best projection
  residual `0.671049`, independent target rank `8`, and
  `any_candidate_spans_terminal_bridge=false`. The remaining missing direction
  is dominated by `angular_velocity_w`, so translation-only matrix features
  improve the local projection but do not supply the coupled terminal bridge.
- The recurrent stage-2 translation/angular coupled matrix-gradient audit
  tests `48` target-free rowmask, pair-swap, and lower-pair local block rows
  with gains `[1e8,1e12]`, rank `132`, best law
  `stage2_velocity_bidirectional_rowmask_translation_angular_feature`, best
  projection residual `0.742069`, independent target rank `8`, and
  `any_candidate_spans_terminal_bridge=false`. This is worse than both the
  active-law residual `0.576548` and the translation-only residual `0.671049`,
  so paired translation/angular rowmask coupling is excluded as the missing
  weak-row formula.
- The componentwise recurrent feedback gain-boundary audit tests `8`
  target-free rows over gains [1,2,5,8,10,12,15,20]. It has no
  order/terminal intersection: gain 1 preserves the smooth-order floor but
  leaves terminal velocity `1.857e-07`, while gains 8 and above close terminal
  velocity only after the min order drops to about `4.508`.
- The h-scaled recurrent feedback gain-boundary audit tests `20` target-free
  rows over gains [2,5,8,12,20] and h-powers [-2,-1,1,2]. It has
  `terminal_closed_row_count=7`, `smooth_order_ok_count=0`, best terminal
  velocity `1.036e-16`, and best min order only `4.711`; h-dependent scalar
  gain scaling does not create an order/terminal intersection.
- The recurrent source-law trajectory screen tests `6` target-free
  one-history/two-history source and curvature rows. It has
  `terminal_closed_row_count=0`, `smooth_order_ok_count=5`, best terminal
  velocity `2.016e-07`, best smooth min order `5.355`, and
  `order_terminal_intersection_present=false`; the tested non-feedback
  recurrent history source laws preserve order but leave the endpoint velocity
  open.
- The three-history recurrent source-law trajectory screen
  `cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_three_history_source_law_trajectory_screen_audit.{csv,json}`
  tests `4` target-free three-block shift-register source laws. It has
  `terminal_closed_row_count=0`, `smooth_order_ok_count=2`, best law
  `recurrent_threehistory_velocity_terminal_source01historyslopejerk_z`, best
  terminal velocity `2.923e-07`, best smooth min order `5.345`, and
  `order_terminal_intersection_present=false`; the tested three-history
  recurrent source law family preserves order only while terminal velocity
  remains open.
- The four-history recurrent source-law trajectory screen
  `cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_four_history_source_law_trajectory_screen_audit.{csv,json}`
  tests `4` target-free four-block shift-register laws, including AB5 and
  fourth-difference snap variants. It has `terminal_closed_row_count=0`,
  `smooth_order_ok_count=2`, best law
  `recurrent_fourhistory_velocity_terminal_source01historyslopejerksnap_z`,
  best terminal velocity `2.950e-07`, best smooth min order `5.342`, and
  `order_terminal_intersection_present=false`; adding one more history block
  does not close the independent lower-pair endpoint velocity.
- The nonlinear-history recurrent source law trajectory screen
  `cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_nonlinear_history_source_law_trajectory_screen_audit.{csv,json}`
  tests `5` target-free nonlinear history laws. It has
  `terminal_closed_row_count=0`, `smooth_order_ok_count=0`, best law
  `recurrent_nonlinearhistory_velocity_terminal_source0historyhadamard_z`,
  best terminal velocity `1.954e-07`, best smooth min order `3.525`, and
  `order_terminal_intersection_present=false`; the tested nonlinear recurrent
  history source law family is also ruled out as the missing closure.
- The source-law final-retain boundary audit tests `16` target-free rows that
  blend high-order recurrent source-law terminal rows toward final-stage
  velocity rows. It has `terminal_closed_row_count=4`,
  `smooth_order_ok_count=0`, best terminal velocity `3.171e-13`, best terminal
  min order `4.508`, best smooth min order `4.510`, and
  `order_terminal_intersection_present=false`; retaining a small source-law
  component near the final-stage branch still requires order collapse.
- The active-velocity extension of the same matrix-gradient audit tests `16`
  target-free stage-2 velocity-feature rows, rank `132`, best law
  `stage2_velocity_column_broadcast_feature`, best projection residual
  `0.585746`, independent target rank `8`, and
  `any_candidate_spans_terminal_bridge=false`.
- The expanded active-law grid tests `20` target-free stage-velocity matrix
  rows, rank `132`, best law
  `stage2_velocity_shifted_column_broadcast_feature`, best projection residual
  `0.576548`, independent target rank `8`, and
  `any_candidate_spans_terminal_bridge=false`.
- A JSON-only missing-direction decomposition reruns that best law/gain over
  `2` local rows in `27.8` seconds. The best post-one-step row still has
  projection residual `0.576548` and missing-direction rank `8`; its dominant
  variable family is `angular_velocity_w` at fraction `0.502991`, with stage
  fractions `0.018511`, `0.018451`, and `0.963038`. The zero-initial row has
  residual `0.909693`, dominant variable family `translation_velocity_v` at
  fraction `0.487135`, and stage-2 fraction `0.964696`. The gap is therefore
  localized to stage-2 angular velocity coupling, not to a missing generic
  matrix-law sweep.
- A stage-2 angular-velocity mask follow-up tests `8` target-free angular-only
  matrix rows in `35.3` seconds, rank `132`, best law
  `stage2_angular_velocity_shifted_column_broadcast_feature`, best projection
  residual `0.752997`, independent target rank `8`, and
  `any_candidate_spans_terminal_bridge=false`. Its remaining missing direction
  is still rank `8`, now dominated by `translation_velocity_v` at fraction
  `0.660361` with stage-2 fraction `0.978093`, so simple angular-only masking
  is excluded and the next target is coupled translation/angular stage-2
  weak-row structure.
- A direct translation/angular cross-coupling follow-up tests `8` target-free
  outer-cross matrix rows in `35.3` seconds, rank `132`, best law
  `stage2_velocity_angular_to_translation_cross_feature`, best projection
  residual `0.898812`, independent target rank `8`, and
  `any_candidate_spans_terminal_bridge=false`. Its remaining missing direction
  is rank `8`, dominated by `translation_velocity_v` at fraction `0.556004`
  with stage-2 fraction `0.999994`, so the tested simple cross-coupled matrix
  laws are excluded.
- An endpoint-pose generalized-velocity predictor follow-up tests `10`
  target-free rows in `31.2` seconds, rank `132`, best law
  `paper_endpoint_pose_positive_lagrange_z`, best projection residual
  `0.117782`, independent target rank `8`, and
  `any_candidate_spans_terminal_bridge=false`. Its remaining missing direction
  is rank `8`, dominated by `translation_velocity_v` at fraction `0.514237`,
  with stage fractions `0.961546`, `0.004167`, and `0.034287`. This is the
  best current local repair probe, but it still does not close the independent
  full-TFE replacement.
- A Gauss endpoint-pose generalized-velocity predictor screen tests `7`
  target-free rows in `28.7` seconds, rank `132`, best law
  `gauss_endpoint_pose_positive_lagrange_z`, best projection residual
  `0.208599`, independent target rank `8`, and
  `any_candidate_spans_terminal_bridge=false`. Its remaining missing direction
  is rank `8`, dominated by `lie_position_u` at fraction `0.650605`, with
  stage fractions `0.524567`, `0.209731`, and `0.265702`. This is worse than
  the paper endpoint-pose positive-Lagrange predictor, so it is a ruled-out
  endpoint-pose alternative rather than a repair direction.
- A remaining Gauss endpoint-pose screen tests the untried quarter,
  stage1-half, convex, and mean predictor rows: `11` target-free rows in
  `31.5` seconds, rank `132`, best law
  `gauss_endpoint_pose_stage02_convex_0p00_z`, best projection residual
  `0.172659`, independent target rank `6`, and
  `any_candidate_spans_terminal_bridge=false`. Its remaining missing direction
  is rank `6`, dominated by `lie_position_u` at fraction `0.952340`, with
  stage fractions `0.320394`, `0.305625`, and `0.373981`. It improves over the
  first Gauss endpoint-pose screen but remains worse than the paper
  endpoint-pose positive-Lagrange row and still does not span.
- A near-terminal stage-0/stage-2 convex predictor follow-up tests `14` rows
  in `31.7` seconds. The overall best law
  `paper_endpoint_pose_stage02_convex_0p00_z` spans locally at roundoff
  (`1.327e-15`) but is `terminal_bridge_equivalent_predictor=true`, so it is
  the already known terminal-stage bridge row, not an independent full-TFE
  replacement. The best nonterminal law
  `paper_endpoint_pose_stage02_convex_0p05_z` reaches projection residual
  `0.049317` with independent target rank `8`,
  `nonterminal_span_row_count=0`, and
  `any_nonterminal_candidate_spans_terminal_bridge=false`; its remaining
  direction is dominated by `translation_velocity_v` at fraction `0.510336`
  with stage fractions `0.976149`, `0.005850`, and `0.018002`.
- A focused h-scaling spot check at `h=0.02` and `h=0.01` repeats the
  three-law near-terminal grid without invoking the full pipeline. The
  terminal-equivalent `paper_endpoint_pose_stage02_convex_0p00_z` row still
  spans at roundoff (`1.082e-15` and `1.227e-15`), but the best nonterminal
  `paper_endpoint_pose_stage02_convex_0p05_z` row remains rank `8` with
  projection residuals `0.051890` and `0.052472`; this rules out treating the
  nonterminal gap as an h=0.04 artifact or solving it by sliding the weight
  back to the terminal bridge.
- A synchronized pose/velocity near-terminal follow-up evaluates
  `C_v(q_alpha,z_alpha)` at matching stage-0/stage-2 convex points. It tests
  `10` local rows in `29.7` seconds. The best law
  `stage02_convex_pose_velocity_0p01_z` improves the local residual to
  `0.009512`, but independent target rank remains `8` and
  `any_nonterminal_candidate_spans_terminal_bridge=false`. The residual stays
  near `0.01` at smaller steps (`0.009978` for `h=0.02`, `0.010085` for
  `h=0.01`), while the weight sweep `0p02/0p05/0p10` gives
  `0.019205/0.049390/0.103464`. This is a useful near-terminal asymptote, not
  an accepted independent row.
- A terminal-limit extrapolation follow-up combines nonterminal synchronized
  rows. `stage02_convex_pose_velocity_extrapolate_0p01_0p02_z` reaches
  residual `4.699e-06` at `h=0.04`, while the wider
  `stage02_convex_pose_velocity_extrapolate_0p01_0p05_z` reaches
  `1.175e-05`. The `0p01/0p02` residual halves to `2.335e-06` at `h=0.02`
  and `1.168e-06` at `h=0.01`, but there is still no span and the independent
  target rank remains `8`, `8`, and `7`. These laws are
  `terminal_bridge_equivalent_predictor=true`, so they are diagnostic
  terminal-limit evidence rather than independent full-TFE rows.
- A nonterminal slope follow-up tests the near-terminal convex slope itself
  rather than the terminal-limit intercept. The JSON-only run covers `4`
  local rows in `25.8` seconds at `h=0.04`, history mode `post_one_step`,
  rank `132`, and max residual `2.483e-12`. The best law is
  `stage02_convex_pose_velocity_slope_0p01_0p05_z`, but its projection
  residual is only `0.677034`; independent target rank remains `8`, and
  `any_candidate_spans_terminal_bridge=false`. The remaining direction is
  dominated by `translation_velocity_v` at fraction `0.490108`, with stage
  fractions `0.488191`, `0.030411`, and `0.481399`. Thus the missing row is
  not the first finite-difference slope of the near-terminal convex
  pose/velocity family.
- A nonterminal curvature follow-up tests the second finite-difference
  curvature of the same synchronized near-terminal pose/velocity family. The
  JSON-only run covers `4` local rows in `26.7` seconds at `h=0.04`, history
  mode `post_one_step`, rank `132`, and max residual `2.483e-12`. The best
  law is `stage02_convex_pose_velocity_curvature_0p01_0p05_0p10_z`, but its
  projection residual is only `0.871228`; independent target rank remains `8`,
  and `any_candidate_spans_terminal_bridge=false`. The remaining direction is
  dominated by `translation_velocity_v` at fraction `0.591909`, with stage
  fractions `0.092772`, `0.021144`, and `0.886084`. Thus the missing row is
  not the local second derivative/curvature of the near-terminal convex
  pose/velocity family.
- A source/history coefficient-feature matrix follow-up tests recurrent
  source features (`history_delta`, `history_unit_delta`, `source0`,
  `source2`, `source02_mean`, `source02_delta`, `source_curvature`, and
  `source_curvature_history_delta`) as target-free shifted-column coefficient
  matrices multiplying the stage-2 lower-pair velocity row. The JSON-only run
  covers `16` local rows in `44.8` seconds at `h=0.04`, history mode
  `post_one_step`, rank `132`, and max residual `2.483e-12`. The best law is
  `source_curvature_shifted_column_broadcast_feature`, but its projection
  residual is only `0.898873`; independent target rank remains `8`, and
  `any_candidate_spans_terminal_bridge=false`. The remaining direction is
  dominated by `translation_velocity_v` at fraction `0.556060`, with stage-2
  fraction `1.000000`. Thus the missing row is not supplied by these tested
  recurrent source/history coefficient features.
- A nonlinear recurrent curvature/history matrix-feature follow-up adds
  source-curvature minus history-delta, source/history Hadamard, unit-Hadamard,
  and normalized curvature-plus-history feature prefixes. The JSON-only run
  covers `16` local rows in `45.5` seconds at `h=0.04`, history mode
  `post_one_step`, rank `132`, and max residual `2.483e-12`. The best law is
  `source_curvature_minus_history_delta_diagonal_plus_row_broadcast_feature`,
  but its projection residual is only `0.898865`; independent target rank
  remains `8`, and `any_candidate_spans_terminal_bridge=false`. The remaining
  direction is dominated by `translation_velocity_v` at fraction `0.556051`,
  with stage-2 fraction `0.999996`. Thus these tested nonlinear
  curvature/history matrix features also do not supply the missing weak row.
- A terminal-limit source-lift matrix-difference follow-up tests whether the
  best near-terminal extrapolated intercept can be repaired by adding a
  stage-local `C_v` source-to-velocity lift before extrapolation. The
  JSON-only run covers `8` local rows in `47.5` seconds at `h=0.04`, history
  mode `post_one_step`, rank `132`, and max residual `2.483e-12`. The best
  law is
  `stage02_convex_pose_velocity_extrapolate_0p01_0p02_sourceliftmatrixdiff_curvature_m0p1_z`,
  but its projection residual is only `5.298e-06`; independent target rank
  remains `8`, and `any_candidate_spans_terminal_bridge=false`. The remaining
  direction is dominated by `translation_acceleration_a` at fraction
  `0.407672`, with stage fractions `0.549481`, `0.005742`, and `0.444777`.
  This is close to the uncorrected terminal-limit residual `4.699e-06` but
  does not improve it into a span, so the missing weak row is not the tested
  terminal-limit `C_v` source-lift matrix-difference correction.
- A curvature source-lift scale refinement follows the closest terminal-limit
  source-lift candidate and tests the uncorrected extrapolated row plus
  curvature lift coefficients `0.01`, `0.05`, `0.1`, `0.2`, and `0.5` with
  both signs. The JSON-only run covers `11` local rows in `52.9` seconds,
  keeps rank `132`, and again has `any_candidate_spans_terminal_bridge=false`.
  The best law is
  `stage02_convex_pose_velocity_extrapolate_0p01_0p02_sourceliftmatrixdiff_curvature_p0p01_z`,
  with residual `5.298e-06`, independent target rank `8`, dominant remaining
  family `translation_acceleration_a` at fraction `0.407672`, and stage
  fractions `0.549481`, `0.005742`, and `0.444777`. The local
  `source_curvature_norm` is only `1.076e-14`, so the tested scale change does
  not supply the missing tangent.
- A mean-acceleration bridge scale refinement follows the earlier
  `accel_m1/accel_p1` negative result and tests the uncorrected terminal-limit
  row plus signed bridge coefficients `0.01`, `0.05`, `0.1`, `0.2`, and `0.5`.
  The JSON-only run covers `11` local rows in `31.4` seconds, keeps rank
  `132`, and again has `any_candidate_spans_terminal_bridge=false`. The
  overall best row remains the terminal-bridge-equivalent uncorrected
  extrapolated row with residual `5.298e-06`; the best nonterminal correction
  is
  `stage02_convex_pose_velocity_extrapolate_0p01_0p02_accel_p0p01_z`, with
  residual `0.000867721`, independent target rank `8`, and dominant remaining
  family `lie_position_u` at fraction `0.706665`. Thus this is not just a
  missed small acceleration-bridge coefficient.
- A generalized-acceleration Taylor-shift scale refinement then applies the
  same terminal-limit extrapolation to left/right stage-local generalized
  acceleration shifts with coefficients `0.01`, `0.05`, `0.1`, `0.2`, and
  `0.5`. The JSON-only run covers `11` local rows in `30.2` seconds, keeps
  rank `132`, and again has `any_candidate_spans_terminal_bridge=false`. The
  overall best row remains the terminal-bridge-equivalent uncorrected row with
  residual `5.298e-06`; the best nonterminal correction is
  `stage02_convex_pose_velocity_extrapolate_0p01_0p02_genaccel_p0p01_z`, with
  residual `0.000866899`, independent target rank `8`, and dominant remaining
  family `lie_position_u` at fraction `0.701135`. Thus the missing row is not
  the tested stage-local $h\dot z$ Taylor shift either.
- A pose-acceleration Taylor-shift scale refinement then applies separate
  left/right stage-local `h^2*zdot` shifts to the evaluated pose before forming
  the same endpoint velocity extrapolation. The JSON-only run covers `11`
  local rows in `29.9` seconds, keeps rank `132`, and again has
  `any_candidate_spans_terminal_bridge=false`. The overall best row remains the
  terminal-bridge-equivalent uncorrected row with residual `5.298e-06`; the
  best nonterminal correction is
  `stage02_convex_pose_velocity_extrapolate_0p01_0p02_poseaccel_p0p01_z`, with
  residual `4.1835e-05`, independent target rank `8`, dominant remaining
  family `lie_position_u` at fraction `0.711570`, and stage-2 fraction
  `0.771337`. This moves more directly in the missing pose direction than the
  velocity-only generalized-acceleration shift, but it still does not supply an
  independent spanning full-TFE row.
- A tiny pose-acceleration scale refinement then tests the same pose-shift law
  with signed coefficients `0.0005`, `0.001`, `0.002`, and `0.005`, plus the
  prior positive `0.01` row. The JSON-only run covers `10` local rows in
  `30.0` seconds, keeps rank `132`, and again has
  `any_candidate_spans_terminal_bridge=false`. The overall best row remains the
  terminal-bridge-equivalent uncorrected row with residual `5.298e-06`; the
  best nonterminal correction is
  `stage02_convex_pose_velocity_extrapolate_0p01_0p02_poseaccel_p0p0005_z`, with
  residual `5.5898e-06`, independent target rank `8`, and dominant remaining
  family `translation_acceleration_a` at fraction `0.350240`. Thus shrinking
  the pose-shift coefficient approaches the terminal-equivalent row but still
  does not create an independent full-TFE closure row.
- A pose+velocity acceleration Taylor refinement then combines the small
  `h^2*zdot` pose shift with signed small `h*zdot` velocity shifts. The
  JSON-only run covers `11` local rows in `30.7` seconds, keeps rank `132`, and
  again has `any_candidate_spans_terminal_bridge=false`. The overall best row
  remains the terminal-bridge-equivalent uncorrected row with residual
  `5.298e-06`; the best nonterminal correction is
  `stage02_convex_pose_velocity_extrapolate_0p01_0p02_posevelaccel_p0p0005_m0p0001_z`,
  with residual `1.0173e-05`, independent target rank `8`, and dominant
  remaining family `lie_position_u` at fraction `0.544660`. Thus the simple
  combined Taylor pose/velocity shift still does not create an independent
  full-TFE closure row.
- A component-split pose-acceleration Taylor refinement then separates the
  same pose shift into translation-only and angular/Lie-only parts. Two
  JSON-only screens cover `26` local rows in `32.3+32.3` seconds, keep rank
  `132`, and have `any_candidate_spans_terminal_bridge=false`. Translation-only
  shifts through coefficients up to `0.1` are locally indistinguishable from the
  uncorrected terminal-limit row: the best nonterminal law is
  `stage02_convex_pose_velocity_extrapolate_0p01_0p02_transposeaccel_m0p01_z`,
  with residual `5.298e-06`, independent target rank `8`, and dominant
  remaining family `translation_acceleration_a` at fraction `0.407672`.
  Angular-only shifts reproduce the earlier full pose-acceleration behavior:
  the larger-scale screen reaches best angular residual `9.6511e-06` at
  `angposeaccel_p0p002`, while `angposeaccel_p0p01` reaches `4.1835e-05`.
  Therefore the tested full pose-acceleration effect comes from the angular/Lie
  pose part, and the translation-only pose shift is not the missing row.
- A component-split velocity-acceleration Taylor refinement then separates the
  same `h*zdot` generalized-velocity shift into translational and angular
  velocity branches. The first JSON-only screen covers `13` local rows in
  `31.8` seconds, keeps rank `132`, and has
  `any_candidate_spans_terminal_bridge=false`. The best nonterminal row is
  `stage02_convex_pose_velocity_extrapolate_0p01_0p02_transvelaccel_m0p01_z`,
  with residual `2.138e-04`, independent target rank `8`, dominant remaining
  family `translation_acceleration_a` at fraction `0.886603`, and stage-2
  fraction `0.812539`. The best angular velocity branch is
  `angvelaccel_p0p01` at residual `0.000864560`, with dominant
  `lie_position_u`. A follow-up tiny translational scale screen covers `11`
  local rows in `31.4` seconds and again has no span; the best nonterminal row
  is
  `stage02_convex_pose_velocity_extrapolate_0p01_0p02_transvelaccel_m0p0005_z`,
  with residual `9.8175e-06`, dominant remaining family
  `translation_acceleration_a` at fraction `0.802349`, and stage-2 fraction
  `0.622536`, still worse than the terminal-bridge-equivalent uncorrected
  residual `5.298e-06`. Thus shrinking the translational velocity shift only
  approaches the terminal-equivalent row; the tested
  velocity-acceleration split is not the independent weak row.
- A component-mixed pose/velocity Taylor refinement then combines the two most
  plausible split directions: angular/Lie pose shift with translational
  velocity shift, plus the complementary translation-pose/angular-velocity
  branch. The JSON-only screen covers `13` local rows in `32.0` seconds, keeps
  rank `132`, and again has `any_candidate_spans_terminal_bridge=false`. The
  best nonterminal law is
  `stage02_convex_pose_velocity_extrapolate_0p01_0p02_angpose_transvelaccel_p0p0005_m0p0005_z`,
  with residual `9.987e-06`, independent target rank `8`, dominant remaining
  family `translation_acceleration_a` at fraction `0.774582`, and stage-2
  fraction `0.625975`. The complementary `transpose_angvelaccel` branch only
  reaches `0.000864560`. This combined component Taylor correction is still
  worse than the terminal-bridge-equivalent uncorrected residual `5.298e-06`,
  so the missing row is not a simple angular-pose/translational-velocity
  acceleration cross term.
- A stage-2-fixed/delta acceleration velocity-shift refinement then tests
  whether the remaining `translation_acceleration_a` direction comes from using
  only the final active-stage acceleration or the stage-2 minus stage-0
  acceleration difference in the velocity shift. The JSON-only screen covers
  `13` local rows in `31.8` seconds, keeps rank `132`, and has
  `any_candidate_spans_terminal_bridge=false`. The best nonterminal row is
  `stage02_convex_pose_velocity_extrapolate_0p01_0p02_transvelaccelstage2_m0p0005_z`,
  with residual `9.8175e-06`, independent target rank `8`, dominant remaining
  family `translation_acceleration_a` at fraction `0.802349`, and stage-2
  fraction `0.622536`. The best delta branch,
  `stage02_convex_pose_velocity_extrapolate_0p01_0p02_transvelacceldelta20_m0p0005_z`,
  reaches only `1.0119e-05`. Thus replacing the interpolated translational
  acceleration by a stage-2-fixed or delta20 acceleration source reproduces the
  earlier tiny-shift limit and is not the independent full-TFE closure row.
- A nonfinal terminal velocity/source predictor refinement then tests a more
  independent weak-row formula: use only the stage-0/stage-1 lower-pair
  velocity rows plus source estimates to extrapolate the terminal closure.
  The JSON-only screen covers `9` local rows in `30.9` seconds, keeps rank
  `132`, and has `any_candidate_spans_terminal_bridge=false`. The best
  nonterminal law is `nonfinal_velocity_terminal_euler1_z`, with residual
  `0.923466`, independent target rank `8`, dominant remaining family
  `translation_velocity_v` at fraction `0.526951`, and stage-2 fraction
  `0.959959`. The Hermite, linear, Adams-Bashforth, source-mean, and
  source-linear variants all stay between `0.923466` and `0.930013`. Thus
  nonfinal velocity/source extrapolation does not supply the missing stage-2
  terminal-bridge Jacobian direction; the replacement must contain a richer
  nonlinear stage-2 transport/source mechanism rather than a plain nonfinal
  integral predictor.
- Promoting those nonfinal terminal velocity/source rows into the bounded
  nonlinear trajectory h-sweep confirms the local negative at trajectory level.
  The stage-0/stage-1 set
  `nonfinal_velocity_terminal_linear01/euler0/euler1/ab01/source01mean0/source01linear0/source01linear1/hermite01`
  runs in `135.3` seconds, keeps rank `132`, converges all `24` requested
  rows, and sets `projection_used=false`, but never closes terminal velocity:
  the best max terminal velocity is `1.770e-07` for the euler0/source01mean0
  family, while `euler1/ab01/source01linear1` has velocity order `5.057` but
  terminal velocity `3.584e-07`; `hermite01` worsens to `2.146e-05` and
  velocity order `0.367`. A stage-0/1/2 extension then adds
  `nonfinal_velocity_terminal_linear012_z`,
  `nonfinal_velocity_terminal_euler2_z`, `ab12`, `source12mean2`,
  `source12linear2`, and `hermite12`; the smoke runs in `101.1` seconds, keeps rank `132`, and
  converges all `18` rows, but again has `terminal_velocity_closed=false`.
  The closest stage-2 rows have `2.559e-11` at `h=0.04` but jump to
  `1.328e-07` at `h=0.02`, so they are not convergent terminal closure. The
  best stable terminal magnitude is only `1.134e-07` from `linear012`.
  Therefore simple nonfinal velocity/source terminal prediction is ruled out
  both locally and on trajectory.
- A stage-2 source-to-velocity transport refinement then applies the existing
  source/history-to-generalized-velocity projection directly at the stage-2
  pose/velocity closure. The first screen covers `13` local rows in `53.4`
  seconds, keeps rank `132`, and has no span. The best nonterminal law is
  `stage02_convex_pose_velocity_0p00_sourceliftmatrixdiff_historydelta_m0p1_z`,
  with residual `0.001251`, independent target rank `6`, dominant remaining
  family `lie_position_u` at fraction `0.597218`, and stage-2 fraction
  `0.476626`. A scale refinement over the same matrix-difference history-delta
  family covers `11` local rows in `57.7` seconds and improves the best
  residual to `0.0001251` at
  `stage02_convex_pose_velocity_0p00_sourceliftmatrixdiff_historydelta_m0p01_z`,
  still with independent target rank `6`, dominant `lie_position_u`, and no
  span. An ultra-fine scale refinement over `0.0001`, `0.0002`, `0.0005`, and
  `0.001` covers `9` local rows in `49.6` seconds and pushes the best
  nonterminal residual to `1.251e-06` at
  `stage02_convex_pose_velocity_0p00_sourceliftmatrixdiff_historydelta_m0p0001_z`.
  The independent target rank is still `6`, the dominant family remains
  `lie_position_u` at fraction `0.597231`, and no row spans. A follow-up then
  combines this ultra-fine source transport with small angular/Lie pose
  acceleration shifts. It covers `8` local rows in `48.7` seconds; the
  source-only row remains best at `1.251e-06`, while the best combined row
  `stage02_convex_pose_velocity_0p00_sourceliftmatrixdiff_historydelta_m0p0001_angposeaccel_p0p0001_z`
  reaches only `1.296e-06`, raises the independent target rank to `8`, keeps
  dominant `lie_position_u` at fraction `0.608336`, and still has no span.
  A final bare endpoint-pose velocity check then tests
  `stage02_convex_pose_velocity_0p00_z` directly beside the ultra-fine
  transport row and `stage02_convex_pose_velocity_0p01_z`. This JSON-only
  three-row probe runs in `31.7` seconds, does not invoke the full pipeline,
  and finds a local row-space span at roundoff: best residual
  `1.327e-15`, independent target rank `0`, `span_row_count=1`, and
  `nonterminal_span_row_count=1`. The ultra-fine transported row still remains
  no-span at `1.251e-06`, so this confirms that shrinking the source-transport
  coefficient was approaching the bare `0p00` endpoint row. The audit status is
  local-span-not-full-TFE: there is still no nonlinear trajectory h-sweep,
  order proof, or artifact update, and `full_tfe_stage_replacement=false`
  remains the claim boundary.
- The local span was then promoted into a bounded JSON-only nonlinear
  trajectory h-sweep smoke without invoking the full pipeline. The new target
  `lower_pair_endpoint_pose_velocity_predictor_h_sweep_smoke` substitutes the
  endpoint-pose velocity predictor rows into the full `132`-row residual. The
  short smooth-only `stage02_convex_pose_velocity_0p00_z` run covers
  `h=[0.04,0.02]` against `reference_h=0.01`, uses `t_final=0.04`, runs in
  `21.5` seconds, keeps rank `132`, converges all `3` requested steps, and
  closes terminal velocity to `7.29e-17`, but the two-point position/velocity
  orders are only `6.588/4.508`. A three-h smooth-only refinement over `h=[0.04,0.02,0.01]`
  against `reference_h=0.005` runs in `28.6` seconds, converges all `7`
  requested steps, keeps rank `132`, closes terminal velocity to `8.124e-17`,
  but drops to position/velocity orders `4.142/2.305` with
  `smooth_order_ok=false` and `accepted_h_sweep_present=false`. The nearby
  nonterminal `stage02_convex_pose_velocity_0p01_z` trajectory smoke runs in
  `21.2` seconds and converges, but terminal velocity remains `6.255e-06` and
  the two-point orders are only `2.345/1.878`. Thus the trajectory evidence
  exposes the same split as earlier closure families: the endpoint row closes
  terminal velocity but loses trajectory order, while a nonterminal offset loses
  terminal closure.
- The strongest local source-transport clue was also promoted to the same
  bounded trajectory smoke. A three-law source-transport comparison runs in
  `74.1` seconds, writes no artifacts, invokes no full pipeline, and keeps
  rank `132` with `projection_used=false`. The bare
  `stage02_convex_pose_velocity_0p00_z` row again closes terminal velocity to
  `7.29e-17` with two-point orders `6.588/4.508`. The source-only transported
  row
  `stage02_convex_pose_velocity_0p00_sourceliftmatrixdiff_historydelta_m0p0001_z`
  has the same two-point orders `6.588/4.508`, but its max terminal velocity is
  `8.020e-12`, above the `1e-12` closure tolerance. Adding the small angular
  pose shift
  `stage02_convex_pose_velocity_0p00_sourceliftmatrixdiff_historydelta_m0p0001_angposeaccel_p0p0001_z`
  worsens terminal velocity to `2.102e-07` and lowers the velocity order to
  `2.820`. Thus the local source-to-velocity transport clue does not survive
  as an accepted nonlinear trajectory replacement.
  A three-h refinement of the source-only transported row over
  `h=[0.04,0.02,0.01]` against `reference_h=0.005` runs in `46.4` seconds,
  converges all `7` requested steps, keeps rank `132`, and remains
  `projection_used=false`; however, the max terminal velocity is still
  `8.020e-12` even though the finest-h value drops to `5.904e-13`, and the
  position/velocity orders collapse to `4.142/2.305`. Therefore the
  source-transport row follows the same terminal/order split as the bare
  endpoint row rather than supplying the missing full-TFE closure formula.
  Shrinking the same source-transport coefficient by another factor of ten to
  `stage02_convex_pose_velocity_0p00_sourceliftmatrixdiff_historydelta_m0p00001_z`
  then closes the terminal tolerance in the same three-h smoke: it runs in
  `43.6` seconds, converges all `7` steps, keeps rank `132`, has
  `terminal_velocity_closed=true` with max/finest terminal velocity
  `8.021e-13`/`5.910e-14`, and remains `projection_used=false`. This still
  does not pass acceptance, because `smooth_order_ok=false` and the
  position/velocity orders remain `4.142/2.305`. Thus coefficient shrinking can
  recover terminal closure in this family, but only by converging to the same
  order-limited endpoint-row behavior.
- A non-projection terminal-limit extrapolation
  `stage02_convex_pose_velocity_extrapolate_0p01_0p02_z` then improves the
  trajectory split but still fails acceptance. The default two-h smoke runs in
  `21.8` seconds, keeps rank `132`, sets `projection_used=false`, reduces max
  terminal velocity to `1.254e-07`, and gives orders `6.412/3.775`. The
  three-h smooth refinement runs in `28.9` seconds, converges all `7` requested
  steps, keeps rank `132`, has max terminal velocity `1.254e-07` and finest-h
  terminal velocity `1.244e-08`, but gives only `4.054/2.364` position/velocity
  order. This is useful non-projection trajectory evidence, not an accepted
  full-TFE replacement.
- A closer non-projection extrapolation sweep then slides the two extrapolation
  points toward the terminal limit. A default two-h smoke over
  `stage02_convex_pose_velocity_extrapolate_0p005_0p01_z`,
  `stage02_convex_pose_velocity_extrapolate_0p002_0p005_z`, and
  `stage02_convex_pose_velocity_extrapolate_0p001_0p002_z` runs in `55.2`
  seconds, keeps rank `132`, converges all `9` rows, and sets
  `projection_used=false`; the terminal velocities are
  `3.135e-08`/`6.270e-09`/`1.254e-09`, while the two-point orders remain below
  the target at `6.621/4.648`, `6.599/4.566`, and `6.591/4.521`. The three-h
  smooth refinement for `0p001/0p002` runs in `27.6` seconds, has max terminal
  velocity `1.254e-09` and finest-h terminal velocity `1.244e-10`, but drops to
  `4.143/2.307` order. An ultra-near check over `0p0001/0p0002` and
  `stage02_convex_pose_velocity_extrapolate_0p00001_0p00002_z` runs in `39.4`
  seconds; the latter closes the terminal
  velocity tolerance at `1.254e-13` with two-point orders `6.588/4.508`. Its
  three-h refinement runs in `30.4` seconds with `projection_used=false`,
  `terminal_velocity_closed=true`, max terminal velocity `1.254e-13`, finest-h
  terminal velocity `1.254e-14`, and position/velocity orders `4.142/2.305`.
  Thus arbitrarily close nonterminal extrapolation can mimic terminal closure,
  but it recovers the same terminal-equivalent order loss and is not an
  accepted full-TFE replacement.
- A three-point quadratic nonterminal extrapolation check then tests whether a
  higher-order-in-weight terminal-limit formula avoids the same trap. The new
  `stage02_convex_pose_velocity_quadextrapolate_*` row family evaluates the
  closure at weight `0` by Lagrange extrapolation from three strictly
  nonterminal stage-0/stage-2 convex rows, so it uses no terminal row and sets
  `projection_used=false`. The default two-h smoke over `0p01/0p02/0p05`,
  `0p005/0p01/0p02`, and `0p002/0p005/0p01` runs in `57.0` seconds, keeps rank
  `132`, converges all `9` rows, and gives terminal velocities
  `2.029e-11`/`2.029e-12`/`2.029e-13`; the two-point orders remain
  `6.588/4.508` for all three rows. The best row,
  `stage02_convex_pose_velocity_quadextrapolate_0p002_0p005_0p01_z`, then runs
  a three-h refinement in `28.4` seconds with
  `terminal_velocity_closed=true`, max terminal velocity `2.029e-13`,
  finest-h terminal velocity `8.254e-15`, but only `4.142/2.305`
  position/velocity order. This rules out simply replacing the linear
  terminal-limit extrapolation by a quadratic nonterminal extrapolation.
- A projection-like terminal-tangent diagnostic then tests whether the
  nonterminal `0p01` row can be rescued by applying a minimum-norm terminal-pose
  velocity correction before evaluating the nonterminal row. This is
  diagnostic only: it sets `projection_used=true` and cannot directly satisfy
  the independent full-TFE gate. The full
  `stage02_convex_pose_velocity_0p01_terminalproj_z` correction fails in the
  reference run with residual divergence `6.739e+08`. Damped corrections still
  do not help: `stage02_convex_pose_velocity_0p01_terminalproj_p0p1_z` runs in
  `28.0` seconds with rank `132`, terminal velocity `7.028e-06`, and orders
  `2.301/1.788`; `stage02_convex_pose_velocity_0p01_terminalproj_p0p5_z` runs
  in `28.7` seconds with terminal velocity `1.321e-05` and orders
  `2.158/1.433`. The next repair therefore remains a non-projection
  nonterminal endpoint-pose predictor, not a damped terminal projection.
- A nonterminal Hermite endpoint pose/velocity predictor follow-up tests
  `nonfinal_hermite_endpoint_pose_velocity_01_z`,
  `nonfinal_hermite_endpoint_pose_velocity_12_z`, and
  `nonfinal_hermite_endpoint_pose_velocity_02_z`. The JSON-only local
  differential audit runs in `24.1` seconds with rank `132`; the best row is
  `nonfinal_hermite_endpoint_pose_velocity_02_z`, but its projection residual
  is only `0.072816`, independent target rank remains `8`, and
  `any_nonterminal_candidate_spans_terminal_bridge=false`. Promoting that best
  row to the bounded nonlinear endpoint-pose velocity h-sweep smoke runs in
  `20.9` seconds, keeps rank `132`, and converges all `3` requested smooth
  steps, but terminal velocity remains `5.827e-06` and the two-point
  position/velocity orders are only `2.693/2.004`. Therefore Hermite
  extrapolation of nonterminal stage pose and generalized velocity is another
  ruled-out endpoint-pose predictor, not the missing full-TFE row.
- A recurrent-history terminal velocity source predictor follow-up tests five
  target-free source laws:
  `recurrent_history_velocity_terminal_source0linear_z`,
  `recurrent_history_velocity_terminal_source0boundedlinear_z`,
  `recurrent_history_velocity_terminal_source0curvature_z`,
  `recurrent_history_velocity_terminal_source01historyblend_z`, and
  `recurrent_history_velocity_terminal_source1linear_z`. These rows use the
  previous accepted step's lower-pair source estimate as a recurrent source
  input, but still use no endpoint-boundary source, terminal-row replacement,
  or projection. The JSON-only local audit runs in `31.4` seconds with rank
  `132`; the best law is
  `recurrent_history_velocity_terminal_source1linear_z`, but its projection
  residual is only `0.923100`, independent target rank remains `8`, and the
  missing direction is still dominated by stage-2 `translation_velocity_v` at
  fraction `0.527377`. Promoting the full five-law family to the bounded
  nonlinear h-sweep smoke runs in `85.5` seconds, keeps rank `132`, and
  converges all `15` source-free smooth steps with maximum residual
  `4.314e-12`, but writes no accepted artifact or summary
  (`artifact_written=false`, `summary_updated=false`). The best terminal
  closure in that family is
  `recurrent_history_velocity_terminal_source01historyblend_z`, with terminal
  velocity `1.010e-07` and two-point orders `6.596/4.805`; the stage-0 source
  variants retain velocity order above `5` but leave terminal velocity near
  `2.016e-07`, and the local-audit best
  `recurrent_history_velocity_terminal_source1linear_z` keeps order
  `6.505/5.042` but leaves terminal velocity at `4.418e-07`. Therefore
  `smooth_order_ok=false` and `terminal_velocity_closed=false`; none of the
  tested one-step recurrent-history source predictors supplies the missing
  `1e-12` terminal-closure row.
- A two-history recurrent source-state follow-up tests five AB3/curvature
  shift-register source laws:
  `recurrent_twohistory_velocity_terminal_source0ab3_z`,
  `recurrent_twohistory_velocity_terminal_source0ab3curvature_z`,
  `recurrent_twohistory_velocity_terminal_source0historycurvature_z`,
  `recurrent_twohistory_velocity_terminal_source01historyslopecurvature_z`,
  and `recurrent_twohistory_velocity_terminal_source1ab3_z`. These rows carry
  two previous 8-entry source blocks but still use no endpoint-boundary source,
  terminal-row replacement, or projection. The bounded smooth smoke converges
  all `30` source-free steps at rank `132`, max residual `4.213e-12`, and no
  accepted artifact/summary. The best terminal laws,
  `source0historycurvature` and `source01historyslopecurvature`, still leave
  max terminal velocity at `9.319e-07`; `source0ab3*` leaves `1.453e-06`, and
  `source1ab3` leaves `2.042e-06`. Thus `terminal_velocity_closed=false`, and
  the two-history extension is worse on terminal closure than the one-step
  AB/source-slope best case.
- A nonlinear recurrent feedback follow-up tests five target-free residual
  feedback rows that blend the current recurrent terminal source predictor with
  the final-stage velocity row using only current candidate/final-row magnitude
  ratios as JAX-differentiated coefficients. The two bounded two-h smooth
  screens converge all `30` source-free steps at rank `132`. The best
  terminal-closing law is
  `recurrent_history_velocity_terminal_feedbacknorm_source01historyslope_rel_p20_z`,
  which reaches max terminal velocity `3.287e-16`; medium-gain feedback laws
  reach `8.876e-11` or `4.244e-08`, and the low-gain branch leaves
  `6.437e-07`. A smooth three-h refinement of the best law over
  `h=[0.04,0.02,0.01]`, `reference_h=0.005`, converges all `14` source-free
  steps at rank `132` with max residual `7.601e-12` and
  `terminal_velocity_closed=true`, but its position/velocity orders are only
  `3.523/4.828`. Thus this feedback law closes terminal velocity without
  projection but falls into the same order-limited branch as the final-stage
  velocity closure; `smooth_order_ok=false` and the full-TFE gate remains open.
- A mean-acceleration bridge correction follow-up tests
  `stage02_convex_pose_velocity_extrapolate_0p01_0p02_accel_m1_z` and
  `stage02_convex_pose_velocity_extrapolate_0p01_0p02_accel_p1_z`. Adding
  `-1` or `+1` times the centered bridge mean-acceleration term worsens the
  best residual from `4.699e-06` to at least `0.076159` and shifts the dominant
  missing direction to `lie_position_u`, so the existing bridge acceleration
  term is not the required nonterminal correction.
- The bilinear active-velocity outer-product follow-up tests `24`
  target-free feature/stage-2-velocity matrix rows, rank `132`, best law
  `stage2_velocity_feature_outer_stage2_velocity`, best projection residual
  `0.898720`, independent target rank `8`, and
  `any_candidate_spans_terminal_bridge=false`. This excludes the tested
  component-pair outer-product coupling family and does not supersede the
  earlier shifted-column localization residual `0.576548`.
- The componentwise active-velocity diagonal follow-up tests `24`
  target-free Hadamard/shifted-diagonal matrix rows, rank `132`, best law
  `stage2_velocity_diagonal_plus_hadamard_row_feature_stage2_velocity`, best
  projection residual `0.898530`, independent target rank `8`, and
  `any_candidate_spans_terminal_bridge=false`. This excludes the tested
  componentwise and shifted-diagonal coupling family.
- The nonterminal synchronized pose/velocity mean-acceleration correction
  follow-up tests `18` local rows over
  `stage02_convex_pose_velocity_0p01_accel_m0p1_z`,
  `stage02_convex_pose_velocity_0p01_accel_p0p1_z`,
  `stage02_convex_pose_velocity_0p01_accel_m1_z`,
  `stage02_convex_pose_velocity_0p01_accel_p1_z`, and the analogous `0p02`
  laws. The best row remains the uncorrected
  `stage02_convex_pose_velocity_0p01_z` with residual `0.009512`; the best
  small signed correction is only `0.012376`, unit corrections are at least
  `0.077874`, independent target rank remains `8`, and
  `nonterminal_span_row_count=0`.
- The generalized-velocity acceleration predictor follow-up tests another
  `18` local rows over `stage02_convex_pose_velocity_0p01_genaccel_m0p1_z`,
  `stage02_convex_pose_velocity_0p01_genaccel_p0p1_z`,
  `stage02_convex_pose_velocity_0p01_genaccel_m1_z`,
  `stage02_convex_pose_velocity_0p01_genaccel_p1_z`, and the analogous `0p02`
  laws. It also leaves the uncorrected row best at `0.009512`, with best
  acceleration-shift residual `0.012376`, no nonterminal span, and
  `full_tfe_stage_replacement=false`.
- The kinematic pose-slope predictor follow-up tests `26` local rows over
  `stage02_convex_pose_velocity_0p01_poseslope_m0p1_z`,
  `stage02_convex_pose_velocity_0p01_poseslope_p0p1_z`,
  `stage02_convex_pose_velocity_0p01_poseslope_m1_z`, and the analogous
  `0p02` laws. It keeps the uncorrected row best at `0.009512`; the best
  pose-slope row is `stage02_convex_pose_velocity_0p02_poseslope_m0p1_z` with
  projection residual `0.878519`, independent target rank `8`, and
  `nonterminal_span_row_count=0`.
- The source-to-velocity lift follow-up tests `34` local rows that map
  mean-acceleration, stage-source, curvature, and history/source-delta rows
  through the current `C_v` velocity matrix into a minimum-norm generalized
  velocity correction. It keeps the uncorrected row best at `0.009512`; the
  best source-lift corrections are
  `stage02_convex_pose_velocity_0p01_sourcelift_historydelta_p1_z` and
  `stage02_convex_pose_velocity_0p01_sourcelift_source0_p1_z`, both at
  residual `0.609803`, with independent target rank `8` and
  `nonterminal_span_row_count=0`.
- The matrix-difference source-to-velocity lift follow-up tests `14` local
  rows that map the same source rows through stage-0 and stage-2 `C_v`
  matrices and insert the difference of the two minimum-norm velocity shifts.
  It runs in `58.7` seconds, leaves the uncorrected row best at `0.009512`,
  and gives the coarse-scale residual `0.042593`. The refined scale sweep
  covers `26` local rows in `92.5` seconds over `0.1`, `1`, and `10` gains;
  it still leaves the uncorrected row best at `0.009512`, with best corrected
  law
  `stage02_convex_pose_velocity_0p01_sourceliftmatrixdiff_historydelta_p0p1_z`
  at residual `0.009527`, independent target rank `8`, and
  `nonterminal_span_row_count=0`.
- The normalized-history matrix-difference source law tests `10` local rows by
  replacing `source0-history` with its direction scaled by `||source0||`
  before the same stage-0/stage-2 `C_v` lift. It runs in `49.4` seconds,
  again leaves the uncorrected row best at `0.009512`, and gives best
  corrected law
  `stage02_convex_pose_velocity_0p01_sourceliftmatrixdiff_historyunitdelta_p0p1_z`
  at residual `0.009590`, with independent target rank `8` and
  `nonterminal_span_row_count=0`.
- The recurrent stage-2 coefficient-gradient differential artifact
  `cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_stage2_gradient_differential_audit.{csv,json}`
  covers `8` smooth local rows over zero/post-one-step history modes,
  `curvature_plus_history_delta` and
  `normalized_curvature_plus_history_delta`, and gains `[1e8,1e12]`. It
  keeps rank `132`, writes `span_row_count=0`, and records best residual
  `0.898872799` with independent target rank `8`; the missing direction is
  still stage-2-local translational velocity.
- The recurrent stage-2 matrix-gradient differential artifact
  `cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_stage2_matrix_gradient_differential_audit.{csv,json}`
  covers `32` smooth local rows over zero/post-one-step history modes and
  eight target-free row/column/bilinear matrix laws. It keeps rank `132`,
  writes `span_row_count=0`, and records best law
  `diagonal_plus_row_broadcast_feature` with residual `0.898873317`,
  independent target rank `8`, and stage-2-local translational-velocity
  missing direction. Thus neither scalar nor matrix coefficient-gradient
  correction supplies the terminal-bridge tangent.
- The recurrent stage-2 translation-velocity matrix differential artifact
  `cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_stage2_translation_velocity_matrix_differential_audit.{csv,json}`
  covers `40` smooth local rows over zero/post-one-step history modes and ten
  target-free stage2 translation-velocity matrix laws. It keeps rank `132`,
  writes `span_row_count=0`, and records best law
  `stage2_translation_velocity_symmetric_broadcast_feature` with residual
  `0.671049`, independent target rank `8`, dominant remaining family
  `angular_velocity_w`, and stage-2 fraction `0.936964`. The translation-only
  mask therefore reduces the projection residual relative to the default
  matrix-gradient audit but leaves a coupled angular-velocity tangent gap and
  still keeps `full_tfe_stage_replacement=false`.
- The recurrent stage-2 translation/angular coupled matrix differential
  artifact
  `cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_stage2_translation_angular_coupled_matrix_differential_audit.{csv,json}`
  covers `48` smooth local rows over zero/post-one-step history modes and 12
  target-free rowmask, pair-swap, and local lower-pair block laws. It keeps
  rank `132`, writes `span_row_count=0`, and records best law
  `stage2_velocity_bidirectional_rowmask_translation_angular_feature` with
  residual `0.742069`, independent target rank `8`, dominant remaining family
  `translation_velocity_v`, and stage-2 fraction `0.942285`. The coupled
  block/pair-swap forms therefore do not recover the terminal bridge and keep
  `full_tfe_stage_replacement=false`.
- The endpoint-pose trajectory smoke artifact
  `cylindrical_chain_endpoint_tfe_paper_lower_pair_endpoint_pose_velocity_predictor_h_sweep_smoke.{csv,json}`
  promotes the terminal-closing `stage02_convex_pose_velocity_0p00_z` law to
  smooth `h=[0.04,0.02,0.01]`,
  `reference_h=0.005`, `T=0.08`: all `14` source-free steps converge at rank
  `132`, terminal velocity closes to `3.455e-16`, but position/velocity orders
  are only `3.523/4.828`. Therefore `terminal_velocity_closed=true`,
  `smooth_order_ok=false`, and `full_tfe_stage_replacement=false`; this local
  span reproduces the same order-limited trajectory branch as the final-stage
  velocity closure.
- The endpoint-pose predictor reference/output audit
  `cylindrical_chain_endpoint_tfe_paper_lower_pair_endpoint_pose_velocity_predictor_reference_output_audit.{csv,json}`
  records `10` short diagnostic rows. It confirms that paper-terminal pose and
  stage2-pose variants are numerically equivalent on the two-h prefilter
  (`6.588/4.508` two-point orders with terminal velocity at roundoff), while
  Gauss-output pose, paper-y velocity, and Lagrange-velocity variants reopen
  terminal velocity. The three-h short check remains order-limited at
  `4.142/2.305`, and the finer `reference_h=0.0025` check drops to
  `3.672/1.956`; `terminal_closed_row_count=5`,
  `smooth_order_ok_count=0`, and `full_tfe_stage_replacement=false`.
  Therefore the next repair must change the independent lower-pair closure
  formula rather than the output-pose node or reference policy.
- The h-adaptive endpoint-pose velocity predictor artifact
  `cylindrical_chain_endpoint_tfe_paper_lower_pair_endpoint_pose_velocity_hscaled_predictor_h_sweep_audit.{csv,json}`
  records `12` smooth rows over four nonterminal h-scaled endpoint-pose
  velocity laws. It uses no projection and no terminal-row replacement. The
  best terminal-closing law is
  `stage02_convex_pose_velocity_extrapolate_0p00001_0p00002_hpow_m1_z`, which
  reaches terminal velocity `5.004e-13` but only `3.523/4.828`
  position/velocity order. The stronger h-powers move away from the terminal
  row but reopen terminal velocity, so the aggregate audit keeps
  `terminal_velocity_closed=false`, `smooth_order_ok=false`,
  `accepted_h_sweep_present=false`, and `full_tfe_stage_replacement=false`.
- The h-adaptive endpoint-pose velocity response audit
  `cylindrical_chain_endpoint_tfe_paper_lower_pair_endpoint_pose_velocity_hscaled_response_audit.{csv,json}`
  reduces the same four laws to one response row per law. It records
  `terminal_closed_row_count=1`, `smooth_order_ok_count=0`,
  `accepted_candidate_count=0`, and
  `order_terminal_intersection_present=false`. The best terminal-closing law is
  still
  `stage02_convex_pose_velocity_extrapolate_0p00001_0p00002_hpow_m1_z`,
  with terminal velocity `5.004e-13`, minimum terminal-closed order `3.523`,
  and gap `1.477` to the order floor. Therefore h-adaptive terminal closure
  still requires order collapse and `full_tfe_stage_replacement=false`.
- The lower-pair candidate frontier audit
  `cylindrical_chain_endpoint_tfe_paper_lower_pair_candidate_frontier_audit.{csv,json}`
  aggregates `11` source-present candidate families and `115` candidate rows
  across h-scaled endpoint-pose response, recurrent source laws, recurrent
  feedback laws, near-final beta, order/closure blend, and centered terminal
  bridge artifacts. It records `total_candidate_row_count=115`,
  `terminal_closed_candidate_count=35`,
  `smooth_order_candidate_count=17`, `order_terminal_intersection_count=0`,
  and `family_intersection_count=0`. The best terminal-closing row is the
  component feedback law with terminal velocity `7.538e-17` but min order
  `4.508`; the best-order row is the recurrent source-law trajectory screen
  with min order `5.355` but terminal velocity `2.771e-07`. Therefore the
  accumulated frontier still has `full_tfe_stage_replacement=false`, and the
  next repair target is a bounded target-free stage-local weak-row tangent.
- The bounded tangent requirement audit
  `cylindrical_chain_endpoint_tfe_paper_lower_pair_bounded_tangent_requirement_audit.{csv,json}`
  records `requirement_row_count=7`, combining the frontier split with the
  row-space and bounded-formula evidence. It preserves
  `row_space_oracle_span_count=36` as a positive but invalid oracle result,
  while `row_space_target_free_span_count=0`,
  `target_free_formula_span_count=0`, `weak_row_structure_span_count=0`, and
  `bounded_gradient_practical_cap_spanning_row_count=12` show that no bounded
  target-free stage-local weak-row tangent has been found yet.
  `full_tfe_stage_replacement=false` and `accepted_h_sweep_present=false`.
- The recurrent stage2 feature-dictionary span audit
  `cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_stage2_feature_dictionary_span_audit.{csv,json}`
  records a positive target-free local capacity result with
  `feature_dictionary_row_count=12`, `span_row_count=8`,
  `combined_all_dictionary_span_count=2`, and best dictionary
  `stage2_matrix_core` at residual `1.084e-14`. The formula path still uses no
  target Jacobian or target-direction oracle, and records
  `formula_coefficient_law_present=false`,
  `accepted_h_sweep_present=false`, and `full_tfe_stage_replacement=false`.
  The next blocker is a bounded target-free coefficient/selection law over the
  spanning feature dictionary plus an accepted nonlinear h-sweep.
- The recurrent stage2 frozen coefficient-law screen
  `cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_stage2_feature_coefficient_law_screen_audit.{csv,json}`
  records `coefficient_law_row_count=60`, `span_count=0`, five target-free
  bounded coefficient laws, and six feature dictionaries. The best row is
  `combined_all_target_free_dictionary` with law `closure_delta_norm_weights`
  and residual `5.596e-01`. It keeps
  `coefficient_derivative_included=false`,
  `target_jacobian_used_for_formula=false`,
  `target_direction_oracle_used=false`,
  `accepted_h_sweep_present=false`, and `full_tfe_stage_replacement=false`.
  Therefore frozen target-free coefficient laws do not close the local
  terminal bridge; the next blocker is state-dependent bounded coefficients
  with derivative terms over the spanning dictionary plus an accepted nonlinear
  h-sweep.
- The recurrent stage2 state-feature coefficient-derivative screen
  `cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_stage2_state_feature_coefficient_derivative_screen_audit.{csv,json}`
  records `state_feature_coefficient_derivative_row_count=36`, `span_count=0`,
  three differentiable target-free coefficient laws, and six feature
  dictionaries. The best row is `stage2_matrix_core` with law
  `inverse_closure_delta_norm_weights_derivative` and residual `5.908e-01`;
  the best improvement over its frozen local row is only `8.199e-03`. It keeps
  `coefficient_derivative_included=true`,
  `target_jacobian_used_for_formula=false`,
  `target_direction_oracle_used=false`,
  `accepted_h_sweep_present=false`, and `full_tfe_stage_replacement=false`.
  Therefore directly differentiating the tested closure-norm coefficient laws
  is also excluded; the next blocker is richer state-dependent coefficient
  features or a new weak-row formula plus an accepted nonlinear h-sweep.
- The near-final beta boundary audit
  `cylindrical_chain_endpoint_tfe_paper_lower_pair_source_free_near_final_beta_boundary_audit.{csv,json}`
  records `8` smooth short-prefilter rows for
  beta=[0.9,0.99,0.999,0.9999,0.99999,0.999999,0.99999999,1.0].
  The high-order endpoint is still beta=0.9/0.99
  (`smooth_order_ok_count=2`), but the terminal velocity is open there. The
  best nonfinal terminal row beta=`0.99999999` reaches only `1.255e-12`
  terminal velocity with min order `4.508`, while beta=1 closes terminal
  velocity by collapsing to the same final-stage branch. Thus
  `order_terminal_intersection_present=false`,
  `near_final_collapse_confirmed=true`, and
  `full_tfe_stage_replacement=false`; the remaining repair must change the
  lower-pair closure formula rather than scalar beta tuning.
- The recurrent feedback gain-boundary audit
  `cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_feedback_gain_boundary_audit.{csv,json}`
  records `8` smooth short-prefilter rows for the target-free nonlinear
  feedback law
  `recurrent_history_velocity_terminal_feedbacknorm_source01historyslope_rel_p*_z`
  over gains [1,2,5,8,10,12,15,20]. It uses no endpoint-boundary source,
  target Jacobian, target-direction oracle, terminal-row replacement, or
  projection. The only high-order row is gain 1 with min order `5.215`, but
  terminal velocity remains `1.868e-07`. Terminal velocity closes for gains
  8, 10, 12, 15, and 20; the best terminal row has `feedback_gain=12`,
  terminal velocity `1.036e-16`, and min order `4.508`. Thus
  `order_terminal_intersection_present=false`,
  `terminal_closure_requires_order_collapse=true`, and
  `full_tfe_stage_replacement=false`; target-free recurrent feedback gain
  tuning also collapses to the already-ruled-out final-stage branch.
- The componentwise recurrent feedback gain-boundary audit
  `cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_component_feedback_gain_boundary_audit.{csv,json}`
  repeats the same short prefilter for
  `recurrent_history_velocity_terminal_feedbackcomp_source01historyslope_rel_p*_z`
  over gains [1,2,5,8,10,12,15,20]. It also uses no endpoint-boundary source,
  target Jacobian, target-direction oracle, terminal-row replacement, or
  projection. The only high-order row is gain 1 with min order `5.214`, but
  terminal velocity remains `1.857e-07`. Gains 8, 10, 12, 15, and 20 close
  terminal velocity; the best terminal row is gain 12 with terminal velocity
  `7.538e-17` and min order `4.508`. Thus
  `order_terminal_intersection_present=false`,
  `terminal_closure_requires_order_collapse=true`, and
  `full_tfe_stage_replacement=false`; the tradeoff is not an artifact of the
  norm-feedback scalar coefficient.
- The h-scaled recurrent feedback gain-boundary audit
  `cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_hscaled_feedback_gain_boundary_audit.{csv,json}`
  tests the target-free law
  `recurrent_history_velocity_terminal_feedbacknormhscaled_source01historyslope_rel_*_pow_*_z`
  over gains [2,5,8,12,20] and h-powers [-2,-1,1,2], with effective gain
  `gain*(h/0.02)^power`. It also uses no endpoint-boundary source, target
  Jacobian, target-direction oracle, terminal-row replacement, or projection.
  Seven rows close terminal velocity, with the best terminal row at gain 12,
  h-power 1, terminal velocity `1.036e-16`, and min order `4.508`. No row
  reaches the smooth-order floor; the best-order row is gain 2, h-power 2,
  min order `4.711`, and terminal velocity `1.316e-08`. Thus
  `order_terminal_intersection_present=false`,
  `terminal_closure_requires_order_collapse=true`, and
  `full_tfe_stage_replacement=false`; h-dependent scalar feedback scaling is
  not the missing independent lower-pair closure.
- The recurrent source-law trajectory screen
  `cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_source_law_trajectory_screen_audit.{csv,json}`
  then removes feedback entirely and tests six target-free one-history and
  two-history source/curvature laws, including `source0curvature`,
  `source0ab2curvature`, `source01historyslope`, and two-history curvature
  variants. All six rows converge at rank `132` on the smooth short prefilter.
  Five rows keep the smooth-order floor; no row closes terminal velocity. The
  best terminal row is `source01historyslope` with terminal velocity
  `2.016e-07` and min order `5.264`; the best-order row is the two-history
  source/history-slope curvature law with min order `5.355` and terminal
  velocity `2.771e-07`. Thus
  `order_terminal_intersection_present=false` and
  `full_tfe_stage_replacement=false`; the tested recurrent source-history
  formulas are order-preserving diagnostics, not the independent closure.
- The three-history recurrent source-law trajectory screen
  `cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_three_history_source_law_trajectory_screen_audit.{csv,json}`
  extends this source-law family with four target-free three-history laws,
  including `recurrent_threehistory_velocity_terminal_source0ab4_z`,
  `recurrent_threehistory_velocity_terminal_source0historyjerk_z`, and
  `recurrent_threehistory_velocity_terminal_source01historyslopejerk_z`. The
  rows use
  `three_zero_initial_blocks_then_stage0_source_estimate_shift_register`, no
  endpoint-boundary source, target Jacobian, target-direction oracle,
  terminal-row replacement, or projection. All rows converge at rank `132` on
  the smooth short prefilter. The jerk laws keep the smooth-order floor; the
  AB4 laws fall to min order about `4.464`. No row closes terminal velocity:
  the best law is
  `recurrent_threehistory_velocity_terminal_source01historyslopejerk_z` with
  terminal velocity `2.923e-07` and min order `5.345`. Therefore
  `terminal_closed_row_count=0`, `smooth_order_ok_count=2`,
  `order_terminal_intersection_present=false`, and
  `full_tfe_stage_replacement=false`; three-history recurrent source laws are
  also ruled out as the missing independent lower-pair closure.
- The four-history recurrent source-law trajectory screen
  `cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_four_history_source_law_trajectory_screen_audit.{csv,json}`
  extends the same prefilter to four target-free four-history laws, including
  `recurrent_fourhistory_velocity_terminal_source0ab5_z`,
  `recurrent_fourhistory_velocity_terminal_source0historysnap_z`, and
  `recurrent_fourhistory_velocity_terminal_source01historyslopejerksnap_z`.
  The rows use
  `four_zero_initial_blocks_then_stage0_source_estimate_shift_register`, no
  endpoint-boundary source, target Jacobian, target-direction oracle,
  terminal-row replacement, or projection. All rows converge at rank `132` on
  the smooth short prefilter. The snap laws keep the smooth-order floor, while
  the AB5 laws fall to min order about `4.090` and leave terminal velocity near
  `6.303e-07`. No row closes terminal velocity: the best law is
  `recurrent_fourhistory_velocity_terminal_source01historyslopejerksnap_z`
  with terminal velocity `2.950e-07` and min order `5.342`. Therefore
  `terminal_closed_row_count=0`, `smooth_order_ok_count=2`,
  `four_history_source_law_trajectory_screen_present=true`,
  `order_terminal_intersection_present=false`, and
  `full_tfe_stage_replacement=false`; four-history recurrent source-law
  extrapolation is also negative evidence.
- The nonlinear-history recurrent source law trajectory screen
  `cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_nonlinear_history_source_law_trajectory_screen_audit.{csv,json}`
  then tests five target-free nonlinear two-history laws, including
  `recurrent_nonlinearhistory_velocity_terminal_source0normhistorydelta_z`,
  `recurrent_nonlinearhistory_velocity_terminal_source0historyhadamard_z`, and
  `recurrent_nonlinearhistory_velocity_terminal_source0normseconddiff_z`. The
  rows use `two_zero_initial_blocks_then_stage0_source_estimate_shift_register`,
  no endpoint-boundary source, target Jacobian, target-direction oracle,
  terminal-row replacement, or projection. All rows converge at rank `132` on
  the smooth short prefilter. No row closes terminal velocity or preserves the
  smooth-order floor: the best law is
  `recurrent_nonlinearhistory_velocity_terminal_source0historyhadamard_z` with
  terminal velocity `1.954e-07` and min order `3.525`. Therefore
  `terminal_closed_row_count=0`, `smooth_order_ok_count=0`,
  `order_terminal_intersection_present=false`, and
  `full_tfe_stage_replacement=false`; nonlinear recurrent history source laws
  are negative evidence, not a full-TFE replacement.
- The source-law final-retain boundary audit
  `cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_source_law_final_retain_boundary_audit.{csv,json}`
  then tests the near transition between the high-order source-law branch and
  the final-stage velocity-row branch. It uses no endpoint-boundary source,
  target Jacobian, target-direction oracle, terminal-row replacement, or
  projection. Across `16` rows over retain values [1e-6,1e-5,1e-4,1e-3] and
  h-powers [0,2], all rows converge at rank `132`. Four rows close terminal
  velocity, all at retain `1e-6`; the best terminal row has velocity
  `3.171e-13` and min order `4.508`. No row reaches the smooth-order floor;
  the best-order row has min order `4.510` and terminal velocity `5.491e-10`.
  Thus `order_terminal_intersection_present=false`,
  `terminal_closure_requires_order_collapse=true`, and
  `full_tfe_stage_replacement=false`; the final-stage/source-law boundary is
  also an order-limited diagnostic, not the missing independent closure.

## Acceptance Definition

The full TFE replacement gate can be flipped only after a single independent
lower-pair stage residual satisfies all of these conditions:

- It is source-free at the method level: no endpoint-boundary source, no
  external endpoint source, no terminal-row replacement, and no output
  projection.
- It supplies the missing eight lower-pair closure rows inside the nonlinear
  stage residual, rather than only as a local tangent, capacity, or oracle fit.
- It passes a nonlinear smooth and sharp h-sweep over the accepted step-size
  set, with terminal velocity closed to the accepted tolerance and without
  sacrificing the expected paper-TFE order.
- It keeps the Newton system full rank, residuals below tolerance, and
  diagnostics/report/CSV/PNG/summary entries synchronized.
- It is attached to the accepted four-ASME method gate and reflected in the
  paper claim ledger.

## Ruled-Out Families

The current artifact set rules out the tested members of these families as
accepted full-TFE replacements:

- fixed final-stage-equivalent compression;
- fixed stage-0/stage-1 nondegenerate injection;
- diagonal state-local direction oracles;
- non-final full component mixing;
- value-balanced non-final compression without derivative correction;
- bounded target-direction oracle saturation laws;
- target-free source/closure/velocity direction laws;
- linear non-final active/source feature spaces;
- finite-difference second-differential source features;
- higher-order and simple nonlocal source features;
- one-step and two-step history-transport features;
- recurrent curvature and bilinear history features;
- source-active cross-Gram, Hadamard, cross-Hadamard, and shifted-commutator
  weak-row structure features;
- frozen target-free row-space compression laws.
- target-direction row-space coefficient-derivative oracle rows as an accepted
  repair, because they close the local tangent only by using the target
  direction and unbounded coefficient-gradient magnitudes.
- the current explicit recurrent weak-row formula, whose local Jacobian still
  misses the stage-2 translational-velocity terminal-bridge direction.
- simple source/history scalar coefficient-gradient modulations of the
  stage-2 lower-pair velocity row.
- target-free row/column matrix coefficient-gradient mixing of the stage-2
  lower-pair velocity row.
- target-free active-velocity coefficient-gradient mixing of the stage-2
  lower-pair velocity row.
- the current shifted-column best row's stage-2 angular velocity missing
  direction, which remains rank eight and unspanned.
- simple stage-2 angular-velocity mask coefficient-gradient rows, which leave
  a rank-eight translation-velocity dominated missing direction.
- simple translation/angular outer-cross coefficient-gradient rows, which also
  leave a rank-eight stage-2 translation-velocity dominated missing direction.
- endpoint-pose positive-Lagrange generalized-velocity predictor rows, which
  improve the local residual to `0.117782` but still leave rank-eight missing
  tangent directions.
- Gauss endpoint-pose generalized-velocity predictor rows, which reach only
  residual `0.208599` and still leave a rank-eight `lie_position_u` gap.
- remaining Gauss endpoint-pose quarter/convex/mean predictor rows, which
  reach only residual `0.172659` and still leave a rank-six `lie_position_u`
  gap.
- near-terminal stage-0/stage-2 convex predictor rows: the stage-2-only row
  spans but is terminal-bridge equivalent, while the best nonterminal row
  reaches `0.049317` and still has no span.
- nonterminal near-terminal convex slope rows, which reach only residual
  `0.677034` and keep a rank-eight `translation_velocity_v` gap.
- nonterminal near-terminal convex curvature rows, which reach only residual
  `0.871228` and keep a rank-eight stage-2 dominated
  `translation_velocity_v` gap.
- recurrent source/history coefficient-feature shifted-column matrix rows,
  which reach only residual `0.898873` and keep a rank-eight stage-2
  `translation_velocity_v` gap.
- nonlinear recurrent curvature/history matrix-feature rows, which reach only
  residual `0.898865` and keep a rank-eight stage-2 `translation_velocity_v`
  gap.
- terminal-limit `C_v` source-lift matrix-difference corrections, which reach
  only residual `5.298e-06` and keep a rank-eight
  `translation_acceleration_a` gap.
- simple nonterminal acceleration corrections of the synchronized
  pose/velocity row, both as direct lower-pair acceleration closure rows and as
  generalized-velocity Taylor predictor shifts.
- kinematic stage-pose-slope velocity predictors for the synchronized
  pose/velocity row.
- current-pose `C_v` source-to-velocity lift predictors for the synchronized
  pose/velocity row.
- stage-0/stage-2 `C_v` matrix-difference source-to-velocity lift predictors
  for the synchronized pose/velocity row.
- normalized recurrent-history source-direction variants of the stage-0/stage-2
  `C_v` matrix-difference lift.
- nonterminal Hermite endpoint pose/velocity predictor rows, which reach only
  local residual `0.072816` and leave trajectory terminal velocity at
  `5.827e-06` with smooth two-point orders `2.693/2.004`.
- one-step recurrent-history terminal velocity source predictors, whose full
  five-law bounded smoke converges all `15` source-free steps at rank `132` but
  has best terminal velocity only `1.010e-07`; the local residual remains
  `0.923100` for `recurrent_history_velocity_terminal_source1linear_z`, and no
  tested law reaches the `1e-12` terminal-closure gate.
- recurrent-history Adams/AB-style terminal source predictors, which test
  `source0ab2`, `source0boundedab2`, `source0ab2curvature`,
  `source01historyslope`, and `source1ab2` as target-free terminal velocity
  closures. The bounded smooth smoke converges all `15` source-free steps at
  rank `132` with max residual `4.189e-12`, but the best terminal law
  `recurrent_history_velocity_terminal_source01historyslope_z` still leaves
  terminal velocity at `2.016e-07` despite orders `6.566/5.264`; the global
  five-law smoke has `terminal_velocity_closed=false` and
  `smooth_order_ok=false`.
- two-history recurrent source-state AB3/curvature terminal source predictors,
  which converge all `30` source-free smooth smoke steps at rank `132` with max
  residual `4.213e-12`, but whose best terminal laws
  `recurrent_twohistory_velocity_terminal_source0historycurvature_z` and
  `recurrent_twohistory_velocity_terminal_source01historyslopecurvature_z`
  still leave terminal velocity at `9.319e-07`; this is worse than the
  one-step AB/source-slope best case and still far above `1e-12`.
- nonlinear recurrent candidate/final-row feedback predictors, whose strongest
  tested norm-feedback law
  `recurrent_history_velocity_terminal_feedbacknorm_source01historyslope_rel_p20_z`
  closes terminal velocity to `3.287e-16` without projection in a smooth
  three-h refinement, but only gives `3.523/4.828` position/velocity orders, so
  it is terminal-closed but order-limited rather than accepted.
- h-adaptive endpoint-pose velocity predictor rows, whose best terminal law
  `stage02_convex_pose_velocity_extrapolate_0p00001_0p00002_hpow_m1_z` closes
  terminal velocity to `5.004e-13` without projection or terminal-row
  replacement, but only gives `3.523/4.828` position/velocity orders while the
  stronger h-powers reopen terminal velocity.
- three-history recurrent source laws, whose best jerk law
  `recurrent_threehistory_velocity_terminal_source01historyslopejerk_z`
  preserves smooth order at `5.345` but leaves terminal velocity at
  `2.923e-07`, with `terminal_closed_row_count=0`.
- four-history recurrent source-law extrapolations, whose best snap law
  `recurrent_fourhistory_velocity_terminal_source01historyslopejerksnap_z`
  preserves smooth order at `5.342` but leaves terminal velocity at
  `2.950e-07`, with `terminal_closed_row_count=0`; the AB5 variants are lower
  order at about `4.090` and still leave terminal velocity near `6.303e-07`.

## Next Implementation Target

The next real method step is a revised analytical weak-row formula or a richer
nonlinear recurrent history source law. It must be inserted into the nonlinear
lower-pair stage residual and then validated by a trajectory h-sweep. A local
span/capacity result alone is not enough to satisfy the gate.

The implementation contract for that next attempt is fixed in
`FULL_TFE_REPAIR_SPEC.md`.

Use the read-only guard:

```bash
../.venv_sbel/bin/python validate_full_tfe_gap.py
../.venv_sbel/bin/python validate_full_tfe_repair_spec.py
```

This guard passes only while the current claim boundary remains explicit. It
must be updated together with the numerical artifacts when a genuine full TFE
replacement candidate is implemented and accepted.
