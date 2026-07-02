# v047 Full TFE Repair Specification

This file turns the open full-TFE blocker into an implementation target. It is
not an acceptance claim. It describes the next candidate that should be added
to `run_v047.py`, the evidence it must produce, and the shortcuts it must not
use.

## Implementation Slot

Add the next candidate beside the existing lower-pair source-free functions in
`run_v047.py`:

- `paper_tfe_lower_pair_source_free_mean_velocity_closure_rows_jax`
- `paper_tfe_lower_pair_source_free_final_stage_velocity_closure_rows_jax`
- `paper_tfe_lower_pair_source_free_order_closure_blend_rows_jax`

The initial scaffold is implemented as separate functions, not by mutating the
existing diagnostics:

```text
paper_tfe_lower_pair_source_free_recurrent_weak_closure_rows_jax(...)
residual_cylindrical_chain_endpoint_tfe_paper_lower_pair_source_free_recurrent_weak_closure_candidate(...)
```

This scaffold is not accepted evidence by itself. It still needs regenerated
CSV/PNG/report/summary artifacts from a nonlinear trajectory h-sweep before any
claim can move beyond `full_tfe_stage_replacement=false`.

The scaffold is wired into JAX value/Jacobian callables so the next full
regeneration can run a Newton solve without adding another residual wrapper:

```text
R_ENDPOINT_TFE_PAPER_LOWER_PAIR_SOURCE_FREE_RECURRENT_WEAK_CLOSURE_VALUE
R_ENDPOINT_TFE_PAPER_LOWER_PAIR_SOURCE_FREE_RECURRENT_WEAK_CLOSURE_JAC
PAPER_TFE_LOWER_PAIR_SOURCE_FREE_RECURRENT_WEAK_CLOSURE_ROWS_VALUE
PAPER_TFE_LOWER_PAIR_SOURCE_FREE_RECURRENT_WEAK_CLOSURE_ROWS_JAC
```

It also has a Newton step and trajectory integration entry point:

```text
endpoint_tfe_paper_lower_pair_source_free_recurrent_weak_closure_step(...)
integrate_endpoint_tfe_paper_lower_pair_source_free_recurrent_weak_closure(...)
```

The current history-source policy is diagnostic: `zero_initial_then_stage0_source_estimate`.
That bootstrap must be replaced or justified before any accepted paper-TFE
claim.

The scaffold has a bounded targeted smoke entry that avoids full regeneration:

```bash
V047_TARGET_AUDIT=lower_pair_recurrent_weak_closure_smoke ../.venv_sbel/bin/python run_v047.py
```

By default this prints a static wiring JSON only. A one-step numerical smoke can
be requested explicitly:

```bash
V047_TARGET_AUDIT=lower_pair_recurrent_weak_closure_smoke V047_RECURRENT_WEAK_SMOKE_NUMERIC=1 ../.venv_sbel/bin/python run_v047.py
```

Both modes must report `diagnostic_smoke_only=true`,
`trajectory_h_sweep_present=false`, `accepted_h_sweep_present=false`, and
`full_tfe_stage_replacement=false`. The target prints JSON only; it does not
write artifacts, update `summary_v047.json`, or invoke the full `main()` run.

The latest bounded one-step numerical smokes were run at `h=0.04` with
`V047_RECURRENT_WEAK_SMOKE_NUMERIC=1`. The `cylindrical_smooth` case converged
in four Newton iterations with rank `132`, residual `6.737e-13`, raw terminal
endpoint velocity `2.337e-10`, and scaled Jacobian condition `1.809e+02`. The
`cylindrical_sharp` case converged in four Newton iterations with rank `132`,
residual `6.484e-13`, raw terminal endpoint velocity `2.319e-10`, and scaled
Jacobian condition `6.582e+01`. This is useful callability evidence for the
scaffold, not acceptance evidence: it has no trajectory h-sweep, does not write
artifacts, and still reports `accepted_h_sweep_present=false` and
`full_tfe_stage_replacement=false`.

A bounded short-trajectory smoke is also available:

```bash
V047_TARGET_AUDIT=lower_pair_recurrent_weak_closure_trajectory_smoke ../.venv_sbel/bin/python run_v047.py
```

It runs `cylindrical_smooth` and `cylindrical_sharp` at `h=0.04`,
`t_final=0.08` by default. The latest run converged all `4` short-trajectory
steps with rank `132`, max residual `2.483e-12`, max raw terminal endpoint
velocity `7.994e-06`, and max scaled Jacobian condition `2.622e+03`. This is
stronger than the one-step smoke because it advances recurrent history over
two steps per case, but it still reports `trajectory_h_sweep_present=false`,
`terminal_velocity_closed=false`, `accepted_h_sweep_present=false`, and
`full_tfe_stage_replacement=false`.

A bounded h-sweep smoke is available:

```bash
V047_TARGET_AUDIT=lower_pair_recurrent_weak_closure_h_sweep_smoke ../.venv_sbel/bin/python run_v047.py
```

By default it runs smooth and sharp over `h=[0.04,0.02]` against
`reference_h=0.01`. The full acceptance-shaped version is opt-in:

```bash
V047_TARGET_AUDIT=lower_pair_recurrent_weak_closure_h_sweep_smoke V047_RECURRENT_WEAK_H_SWEEP_FULL=1 ../.venv_sbel/bin/python run_v047.py
```

The latest bounded h-sweep smoke converged all `12` trajectory steps with rank
`132`, max residual `4.463e-12`, max raw terminal endpoint velocity
`8.234e-06`, min position order `3.204`, min velocity order `-0.428`, and max
scaled Jacobian condition `5.320e+03`. It reports
`bounded_h_sweep_smoke_present=true`, `trajectory_h_sweep_present=false`,
`terminal_velocity_closed=false`, `smooth_order_ok=false`, and
`accepted_h_sweep_present=false`.

The latest opt-in full acceptance-shaped h-sweep used
`V047_RECURRENT_WEAK_H_SWEEP_FULL=1`, smooth and sharp cases,
`h=[0.04,0.02,0.01]`, and `reference_h=0.005`. It converged all `28`
trajectory steps with rank `132`, max residual `9.998e-12`, max raw terminal
endpoint velocity `8.234e-06`, smooth position/velocity orders `5.317/6.782`,
sharp position/velocity orders `2.555/1.918`, and max scaled Jacobian condition
`6.079e+03`. It reports `mode=full_acceptance_shape_h_sweep`,
`trajectory_h_sweep_present=true`, `smooth_order_ok=true`, but
`terminal_velocity_closed=false` and `accepted_h_sweep_present=false`.
Therefore the current recurrent weak-closure scaffold is a callable
source-free 132-row trajectory residual, but not a full-TFE replacement.

A recurrent/terminal blend one-step smoke is available:

```bash
V047_TARGET_AUDIT=lower_pair_recurrent_terminal_blend_one_step_smoke ../.venv_sbel/bin/python run_v047.py
```

It blends the recurrent weak closure with the final-stage velocity closure over
`gamma=[0,0.5,1]` at `h=0.04`. The latest run converged all `6` one-step rows
with rank `132`. The best residual gamma was `0.5` in both smooth and sharp
cases, with residuals `6.071e-13` and `3.533e-13`, but terminal velocity stayed
at about `2.30e-10`. The best terminal gamma was `1.0` in both cases, with raw
terminal endpoint velocities `7.845e-17` and `9.479e-17`, but this is the
known final-stage-velocity endpoint of the family whose full h-sweep is
smooth-order limited. Thus the blend exposes the same order/terminal split
rather than closing the full-TFE gate.

A recurrent/terminal blend h-sweep smoke is also available:

```bash
V047_TARGET_AUDIT=lower_pair_recurrent_terminal_blend_h_sweep_smoke ../.venv_sbel/bin/python run_v047.py
```

It promotes the one-step gamma blend to a trajectory h-sweep. The default
target runs smooth and sharp over `gamma=[0.5,1.0]`, `h=[0.04,0.02]`, and
`reference_h=0.01`; the acceptance-shaped sweep is explicit opt-in with
`V047_RECURRENT_TERMINAL_BLEND_H_SWEEP_FULL=1`. A shorter smooth-only screen is
available with `V047_RECURRENT_TERMINAL_BLEND_H_SWEEP_CASES=cylindrical_smooth`.
The latest bounded default run
converged all `24` requested trajectory steps with rank `132`, max residual
`4.766e-12`, and max scaled Jacobian condition `6.523e+03`. It found best
terminal gamma `1.0`, with raw terminal endpoint velocities `3.049e-16` and
`2.941e-16` in the smooth and sharp cases, but smooth minimum order `4.397`;
gamma `0.5` had the best smooth minimum order `4.413` but raw terminal endpoint
velocity reached `8.105e-06` on the sharp case. The overall bounded screen has
min position/velocity orders `3.204/-0.428` and reports
`any_gamma_terminal_velocity_closed=true`, `smooth_order_ok=false`, and
`accepted_h_sweep_present=false`.

A denser scalar-gamma exclusion screen is available through the same target:

```bash
V047_TARGET_AUDIT=lower_pair_recurrent_terminal_blend_h_sweep_smoke V047_RECURRENT_TERMINAL_BLEND_H_SWEEP_GAMMAS=0,0.25,0.5,0.75,1 ../.venv_sbel/bin/python run_v047.py
```

The latest dense bounded run converged all `60` requested trajectory steps with
rank `132`, elapsed time `114.2` seconds, max residual `4.766e-12`, and max raw
terminal endpoint velocity `8.234e-06`. The best smooth-order gamma was `0.75`
with smooth minimum order `4.414`; the best terminal gamma remained `1.0` with
terminal velocity `3.049e-16`; the overall sharp minimum velocity order stayed
`-0.428`. Thus a scalar gamma sweep over this bracket does not produce an
order/terminal intersection, and the next repair still needs a new row formula
rather than another scalar interpolation between these endpoints.

A near-terminal scalar-gamma screen checks the remaining loophole that a gamma
very close to the terminal-closing endpoint might restore order while nearly
closing terminal velocity:

```bash
V047_TARGET_AUDIT=lower_pair_recurrent_terminal_blend_h_sweep_smoke V047_RECURRENT_TERMINAL_BLEND_H_SWEEP_GAMMAS=0.9,0.99,0.999,1 ../.venv_sbel/bin/python run_v047.py
```

The latest near-terminal bounded run converged all `48` requested trajectory
steps with rank `132`, elapsed time `91.6` seconds, max residual `4.766e-12`,
and max raw terminal endpoint velocity `7.196e-06`. The best smooth-order gamma
was `0.99` with smooth minimum order `4.415`, but its sharp terminal velocity
was still `3.081e-06`. Gamma `0.999` reduced the sharp terminal velocity to
`4.678e-07`, still far above the `1e-12` tolerance, while gamma `1.0` was the
only terminal-closed branch and kept smooth minimum order `4.397`. Therefore
near-terminal scalar policies are excluded as full-TFE repairs.

A component-wise one-step gamma sensitivity target checks whether the remaining
blocker is concentrated in one of the eight lower-pair terminal directions:

```bash
V047_TARGET_AUDIT=lower_pair_recurrent_terminal_component_one_step_smoke ../.venv_sbel/bin/python run_v047.py
```

Optional controls are `V047_RECURRENT_TERMINAL_COMPONENT_RELEASE_VALUE`,
`V047_RECURRENT_TERMINAL_COMPONENT_H`, and
`V047_RECURRENT_TERMINAL_COMPONENT_CASES`. The target prints JSON only, sets
`one_step_component_gamma_sweep_present=true`, and keeps
`trajectory_h_sweep_present=false`, `accepted_h_sweep_present=false`, and
`full_tfe_stage_replacement=false`.

The latest component run used release value `0.999`, both smooth and sharp
cases, and `10` gamma vectors, producing `20` one-step rows in `31.6` seconds.
All rows had rank `132`; the max residual was `1.766e-12`, the max raw terminal
endpoint velocity was `1.368e-11`, and `7` rows terminal-closed at the `1e-12`
tolerance. Among nontrivial vectors, `5` terminal-closed; the best component
release was `component_2_release_0p999` with terminal velocity `3.456e-17`,
while the worst was `component_7_release_0p999` with terminal velocity
`1.234e-11`. This is useful component localization, but it is not a trajectory
h-sweep and cannot close the full-TFE gate.

A component-wise trajectory h-sweep promotes the one-step localization to a
bounded short-trajectory check:

```bash
V047_TARGET_AUDIT=lower_pair_recurrent_terminal_component_h_sweep_smoke ../.venv_sbel/bin/python run_v047.py
```

Optional controls are `V047_RECURRENT_TERMINAL_COMPONENT_H_SWEEP_LABELS`,
`V047_RECURRENT_TERMINAL_COMPONENT_H_SWEEP_RELEASE_VALUE`,
`V047_RECURRENT_TERMINAL_COMPONENT_H_SWEEP_VALUES`,
`V047_RECURRENT_TERMINAL_COMPONENT_H_SWEEP_REFERENCE_H`, and
`V047_RECURRENT_TERMINAL_COMPONENT_H_SWEEP_CASES`. The target prints JSON only,
sets `component_trajectory_h_sweep_smoke_present=true`, and keeps
`accepted_h_sweep_present=false` and `full_tfe_stage_replacement=false`.

The latest default run used labels `all_ones`, `all_0p999`,
`component_2_release_0p999`, and `component_7_release_0p999` over both smooth
and sharp cases, `h=[0.04,0.02]`, and `reference_h=0.01`. It converged all
`48` short-trajectory steps in `98.4` seconds with rank `132`, max residual
`4.766e-12`, and max raw terminal endpoint velocity `4.678e-07`. The best
terminal vector was `component_2_release_0p999` with terminal velocity
`2.696e-16`, but its smooth minimum order remained about `4.397`. The best
smooth-order vector was `all_0p999` with smooth minimum order `4.401`, but it
left terminal velocity `4.678e-07`. Therefore
`order_terminal_intersection_present=false`; component-wise gamma tuning does
not close the full-TFE gate.

A recurrent history-gamma h-sweep checks a simple nonlinear source law that
sets the component-wise terminal blend from the previous step's `history_source`
rather than from a hand-picked gamma vector:

```bash
V047_TARGET_AUDIT=lower_pair_recurrent_history_gamma_h_sweep_smoke ../.venv_sbel/bin/python run_v047.py
```

Optional controls are `V047_RECURRENT_HISTORY_GAMMA_POLICIES`,
`V047_RECURRENT_HISTORY_GAMMA_RELEASES`,
`V047_RECURRENT_HISTORY_GAMMA_FLOOR`,
`V047_RECURRENT_HISTORY_GAMMA_H_SWEEP_VALUES`,
`V047_RECURRENT_HISTORY_GAMMA_REFERENCE_H`,
`V047_RECURRENT_HISTORY_GAMMA_T_FINAL`, and
`V047_RECURRENT_HISTORY_GAMMA_CASES`. The target prints JSON only, sets
`history_gamma_h_sweep_smoke_present=true`, and keeps
`accepted_h_sweep_present=false` and `full_tfe_stage_replacement=false`.

The latest default smooth-only run used policy `history_abs_inf`, releases
`[0.001,0.01]`, `h=[0.04,0.02]`, and `reference_h=0.01`. It converged all
`12` short-trajectory steps in `38.9` seconds with rank `132`, max residual
`2.586e-12`, max raw terminal endpoint velocity `9.365e-07`, and max history
gamma release `0.010000000000000009`. The best terminal and smooth-order
branch was release `0.001`, with terminal velocity `1.451e-07` and smooth
minimum order `4.402`. Thus `order_terminal_intersection_present=false`.

A signed-policy follow-up used policies `history_signed_positive` and
`history_signed_negative` with release `0.001`. It converged all `12` requested
steps in `36.9` seconds with rank `132`, max residual `3.869e-12`, and max raw
terminal endpoint velocity `1.763e-07`. The best terminal branch was
`history_signed_positive` with terminal velocity `1.452e-07`, while the best
smooth-order branch was `history_signed_negative` with smooth minimum order
`4.415`. This also leaves `order_terminal_intersection_present=false`, so the
simple explicit recurrent history-gamma law is excluded as an accepted full-TFE
repair. A revised analytical weak-row formula remains the next target.

A recurrent weak-row differential audit then checks the current weak-row
formula directly against the terminal-bridge tangent, without running a
trajectory h-sweep:

```bash
V047_TARGET_AUDIT=lower_pair_recurrent_weak_differential_audit ../.venv_sbel/bin/python run_v047.py
```

Optional controls are `V047_RECURRENT_WEAK_DIFFERENTIAL_CASES`,
`V047_RECURRENT_WEAK_DIFFERENTIAL_HISTORY_MODES`, and
`V047_RECURRENT_WEAK_DIFFERENTIAL_H`. The target prints JSON only, sets
`recurrent_weak_differential_audit_present=true`, and keeps
`accepted_h_sweep_present=false` and `full_tfe_stage_replacement=false`.

The latest default run used the smooth case at `h=0.04` with history modes
`zero_initial` and `post_one_step`. It produced `2` local rows in `26.0`
seconds, kept rank `132`, and had max residual `2.483e-12`. The current
recurrent weak row did not span the terminal bridge in either mode:
`any_recurrent_weak_spans_terminal_bridge=false`, recurrent projection
relative residuals ranged from `0.899` to `0.974`, and the independent target
rank stayed `8`. In contrast, the final-stage terminal-closing row had
projection residual at the `1.456e-15` scale. The recurrent-vs-final closure
Jacobian gap reached relative size `6.872`; the missing direction was
stage-2-local with `stage2` fraction `1.0` and dominant variable family
`translation_velocity_v`. This records `coefficient_gradient_gap_present=true`
for the current formula and narrows the next repair to a revised analytical
weak-row closure whose nonlinear row Jacobian supplies that stage-2 velocity
direction without substituting the final-stage terminal row.

A stage-2 coefficient-gradient differential audit checks the next obvious
source/history-modulated correction direction:

```bash
V047_TARGET_AUDIT=lower_pair_recurrent_stage2_gradient_differential_audit ../.venv_sbel/bin/python run_v047.py
```

Optional controls are `V047_RECURRENT_STAGE2_GRADIENT_CASES`,
`V047_RECURRENT_STAGE2_GRADIENT_HISTORY_MODES`,
`V047_RECURRENT_STAGE2_GRADIENT_FEATURES`,
`V047_RECURRENT_STAGE2_GRADIENT_GAINS`, and
`V047_RECURRENT_STAGE2_GRADIENT_H`. The target prints JSON only, sets
`recurrent_stage2_gradient_differential_audit_present=true`, and keeps
`accepted_h_sweep_present=false` and `full_tfe_stage_replacement=false`.

The latest default run used the smooth case, history modes `zero_initial` and
`post_one_step`, features `curvature_plus_history_delta` and
`normalized_curvature_plus_history_delta`, gains `[1e8,1e12]`, and `h=0.04`.
It produced `8` local rows in `35.3` seconds, kept rank `132`, and had max
residual `2.483e-12`. No candidate spanned the terminal bridge:
`any_candidate_spans_terminal_bridge=false`. The best row used
`curvature_plus_history_delta` with gain `1e12`, but still had projection
relative residual `0.899` and independent target rank `8`. The largest closure
value perturbation from the recurrent weak row was `1.246e-09`, a relative
perturbation of `2.861e+04`, so the tested source/history coefficient-gradient
features change values without supplying the missing tangent. This excludes
that simple stage-2 velocity coefficient-gradient law and leaves the repair at
a richer analytical weak-row formula.

A stage-2 matrix-gradient differential audit checks the next richer but still
target-free row/column mixing direction:

```bash
V047_TARGET_AUDIT=lower_pair_recurrent_stage2_matrix_gradient_differential_audit ../.venv_sbel/bin/python run_v047.py
```

Optional controls are `V047_RECURRENT_STAGE2_MATRIX_CASES`,
`V047_RECURRENT_STAGE2_MATRIX_HISTORY_MODES`,
`V047_RECURRENT_STAGE2_MATRIX_LAWS`, `V047_RECURRENT_STAGE2_MATRIX_GAINS`,
and `V047_RECURRENT_STAGE2_MATRIX_H`. The target prints JSON only, sets
`recurrent_stage2_matrix_gradient_differential_audit_present=true`, and keeps
`accepted_h_sweep_present=false` and `full_tfe_stage_replacement=false`.

The latest default run used the smooth case, history modes `zero_initial` and
`post_one_step`, eight target-free row/column/bilinear matrix laws, gains
`[1e8,1e12]`, and `h=0.04`. It produced `32` local rows in `68.1` seconds,
kept rank `132`, and had max residual `2.483e-12`. No candidate spanned the
terminal bridge: `any_candidate_spans_terminal_bridge=false`. The best row
used `diagonal_plus_row_broadcast_feature` with gain `1e12`, but still had
projection relative residual `0.898873` and independent target rank `8`. The
largest closure value perturbation from the recurrent weak row was
`4.005e-09`, a relative perturbation of `9.197e+04`, so target-free
row/column/bilinear matrix mixing changes values without supplying the missing
tangent. This excludes the tested matrix-premultiplied stage-2 velocity laws
and leaves the repair at a genuinely revised analytical weak-row formula.

A stage-2 translation-velocity matrix differential audit narrows that
matrix-gradient gap by masking the active stage-2 feature to the translational
velocity components:

```bash
V047_TARGET_AUDIT=lower_pair_recurrent_stage2_translation_velocity_matrix_differential_audit ../.venv_sbel/bin/python run_v047.py
```

Optional controls are `V047_RECURRENT_STAGE2_TRANSLATION_MATRIX_CASES`,
`V047_RECURRENT_STAGE2_TRANSLATION_MATRIX_HISTORY_MODES`,
`V047_RECURRENT_STAGE2_TRANSLATION_MATRIX_LAWS`,
`V047_RECURRENT_STAGE2_TRANSLATION_MATRIX_GAINS`, and
`V047_RECURRENT_STAGE2_TRANSLATION_MATRIX_H`. The target prints JSON only,
sets `recurrent_stage2_translation_velocity_matrix_differential_audit_present=true`,
and keeps `accepted_h_sweep_present=false` and
`full_tfe_stage_replacement=false`.

The latest default run used the smooth case, history modes `zero_initial` and
`post_one_step`, ten target-free translation-velocity matrix laws, gains
`[1e8,1e12]`, and `h=0.04`. It produced `40` local rows, kept rank `132`, and
had max residual `2.483e-12`. No candidate spanned the terminal bridge:
`any_candidate_spans_terminal_bridge=false`. The best row used
`stage2_translation_velocity_symmetric_broadcast_feature` with gain `1e12`,
improving the projection relative residual to `0.671049`, but the independent
target rank remained `8` and the dominant missing family became
`angular_velocity_w`. Translation-only matrix features therefore reduce the
local residual but leave a coupled angular-velocity tangent gap.

A translation/angular coupled stage-2 matrix differential audit then tests
whether paired row masks, pair swaps, and local lower-pair 4-row blocks supply
the missing tangent:

```bash
V047_TARGET_AUDIT=lower_pair_recurrent_stage2_translation_angular_coupled_matrix_differential_audit ../.venv_sbel/bin/python run_v047.py
```

Optional controls are `V047_RECURRENT_STAGE2_COUPLED_MATRIX_CASES`,
`V047_RECURRENT_STAGE2_COUPLED_MATRIX_HISTORY_MODES`,
`V047_RECURRENT_STAGE2_COUPLED_MATRIX_LAWS`,
`V047_RECURRENT_STAGE2_COUPLED_MATRIX_GAINS`, and
`V047_RECURRENT_STAGE2_COUPLED_MATRIX_H`. The target prints JSON only, sets
`recurrent_stage2_translation_angular_coupled_matrix_differential_audit_present=true`,
and keeps `accepted_h_sweep_present=false` and
`full_tfe_stage_replacement=false`.

The latest default run used the smooth case, history modes `zero_initial` and
`post_one_step`, twelve target-free translation/angular coupled matrix laws,
gains `[1e8,1e12]`, and `h=0.04`. It produced `48` local rows, kept rank
`132`, and had max residual `2.483e-12`. No candidate spanned the terminal
bridge: `any_candidate_spans_terminal_bridge=false`. The best row used
`stage2_velocity_bidirectional_rowmask_translation_angular_feature` with gain
`1e12`, but its projection relative residual was `0.742069`, with independent
target rank `8`, dominant missing family `translation_velocity_v`, and
stage-2 missing-direction fraction `0.942285`. This is worse than the
translation-only matrix residual `0.671049` and the active-law residual
`0.576548`, so the paired rowmask/pair-swap/local-block matrix laws are also
negative evidence rather than a full-TFE replacement.

An active-velocity extension reuses the same JSON-only target but overrides the
matrix law list:

```bash
V047_TARGET_AUDIT=lower_pair_recurrent_stage2_matrix_gradient_differential_audit V047_RECURRENT_STAGE2_MATRIX_LAWS=stage2_velocity_row_broadcast_feature,stage2_velocity_column_broadcast_feature,stage2_minus_stage1_velocity_row_broadcast_feature,velocity_curvature_diagonal_plus_row_broadcast_feature V047_RECURRENT_STAGE2_MATRIX_GAINS=1e8,1e12 ../.venv_sbel/bin/python run_v047.py
```

The latest run produced `16` local rows in `46.6` seconds, kept rank `132`, and
had max residual `2.483e-12`. No active-velocity candidate spanned the terminal
bridge: `any_candidate_spans_terminal_bridge=false`. The best row used
`stage2_velocity_column_broadcast_feature` with gain `1e12`, improving the
projection relative residual to `0.585746`, but the independent target rank
remained `8`. The largest closure value perturbation from the recurrent weak
row was `1.460e-06`, a relative perturbation of `3.353e+07`. Active stage-2
velocity features therefore contain more of the missing local tangent than the
source/history features, but the tested target-free laws still do not close the
span gap and cannot be promoted to an accepted h-sweep.

An expanded active-law grid reuses the same target with:

```bash
V047_TARGET_AUDIT=lower_pair_recurrent_stage2_matrix_gradient_differential_audit V047_RECURRENT_STAGE2_MATRIX_LAWS=stage2_velocity_symmetric_broadcast_feature,stage2_velocity_diagonal_plus_row_broadcast_feature,stage2_velocity_shifted_column_broadcast_feature,stage2_minus_stage1_velocity_column_broadcast_feature,stage01_mean_velocity_column_broadcast_feature V047_RECURRENT_STAGE2_MATRIX_GAINS=1e8,1e12 ../.venv_sbel/bin/python run_v047.py
```

The latest run produced `20` local rows in `51.2` seconds, kept rank `132`, and
had max residual `2.483e-12`. No row spanned the terminal bridge:
`any_candidate_spans_terminal_bridge=false`. The best row used
`stage2_velocity_shifted_column_broadcast_feature` with gain `1e12`, improving
the projection relative residual only to `0.576548`, while the independent
target rank remained `8`. The largest closure value perturbation from the
recurrent weak row was `1.460e-06`, a relative perturbation of `3.353e+07`.
This widens the active-velocity negative result and leaves the next repair at
a genuinely new weak-row formula rather than another target-free matrix
premultiplication of existing stage velocity rows.

The best active-law row/gain was then rerun as a JSON-only missing-direction
decomposition:

```bash
V047_TARGET_AUDIT=lower_pair_recurrent_stage2_matrix_gradient_differential_audit V047_RECURRENT_STAGE2_MATRIX_LAWS=stage2_velocity_shifted_column_broadcast_feature V047_RECURRENT_STAGE2_MATRIX_GAINS=1e12 ../.venv_sbel/bin/python run_v047.py
```

That targeted run produced `2` local rows in `27.8` seconds, kept rank `132`,
and did not invoke the full pipeline: `full_run_invoked=false`,
`artifact_written=false`, and `summary_updated=false`. The best post-one-step
row still had projection residual `0.576548`, missing-direction rank `8`,
dominant variable family `angular_velocity_w` at fraction `0.502991`, and
stage fractions `0.018511`, `0.018451`, and `0.963038`. The zero-initial row
had projection residual `0.909693`, dominant variable family
`translation_velocity_v` at fraction `0.487135`, and stage-2 fraction
`0.964696`. The next formula target is therefore a stage-2 lower-pair weak row
with an angular-velocity coefficient-derivative coupling, not a wider generic
matrix-law family.

A stage-2 angular-velocity mask follow-up tests that localization directly by
using only the angular components of the stage-2 lower-pair velocity row as the
coefficient feature:

```bash
V047_TARGET_AUDIT=lower_pair_recurrent_stage2_matrix_gradient_differential_audit V047_RECURRENT_STAGE2_MATRIX_LAWS=stage2_angular_velocity_shifted_column_broadcast_feature,stage2_angular_velocity_diagonal_plus_row_broadcast_feature,stage2_angular_velocity_feature_outer_stage2_velocity,stage2_angular_velocity_diagonal_plus_hadamard_row_feature_stage2_velocity V047_RECURRENT_STAGE2_MATRIX_GAINS=1e12 ../.venv_sbel/bin/python run_v047.py
```

The latest run produced `8` local rows in `35.3` seconds, kept rank `132`, and
did not invoke the full pipeline. No angular-mask row spanned the terminal
bridge: `any_candidate_spans_terminal_bridge=false`. The best row used
`stage2_angular_velocity_shifted_column_broadcast_feature` with gain `1e12`,
but its projection relative residual was only `0.752997`, worse than the
unmasked active-law residual `0.576548`; the independent target rank remained
`8`. The best missing-direction decomposition shifted back to dominant
`translation_velocity_v` at fraction `0.660361`, with stage fractions
`0.011550`, `0.010357`, and `0.978093`. This rules out a simple angular-only
mask and points instead to a coupled translation/angular stage-2 weak-row
formula.

A direct translation/angular cross-coupling follow-up then tests the simplest
coupled matrix forms:

```bash
V047_TARGET_AUDIT=lower_pair_recurrent_stage2_matrix_gradient_differential_audit V047_RECURRENT_STAGE2_MATRIX_LAWS=stage2_velocity_translation_to_angular_cross_feature,stage2_velocity_angular_to_translation_cross_feature,stage2_velocity_symmetric_translation_angular_cross_feature,stage2_velocity_shifted_translation_angular_cross_feature V047_RECURRENT_STAGE2_MATRIX_GAINS=1e12 ../.venv_sbel/bin/python run_v047.py
```

The latest run produced `8` local rows in `35.3` seconds, kept rank `132`, and
did not invoke the full pipeline. No cross-coupled row spanned the terminal
bridge: `any_candidate_spans_terminal_bridge=false`. The best row used
`stage2_velocity_angular_to_translation_cross_feature` with gain `1e12`, but
its projection relative residual was only `0.898812`, with independent target
rank `8`. The best missing direction was again dominated by
`translation_velocity_v` at fraction `0.556004`, with stage fractions
`0.00000293`, `0.00000298`, and `0.999994`. This excludes the tested simple
translation/angular outer-cross coupling and leaves the repair target at a
new lower-pair weak-row formula, not another stage-2 velocity matrix
premultiplication.

A new endpoint-pose generalized-velocity predictor probe then tests that
weak-row direction directly, without using the terminal bridge as a formula:

```bash
V047_TARGET_AUDIT=lower_pair_recurrent_stage2_matrix_gradient_differential_audit V047_RECURRENT_STAGE2_MATRIX_LAWS=paper_endpoint_pose_lagrange_z,paper_endpoint_pose_positive_lagrange_z,paper_endpoint_pose_stage1_half_lagrange_z,paper_endpoint_pose_stage12_linear_z,paper_endpoint_pose_stage02_linear_z V047_RECURRENT_STAGE2_MATRIX_GAINS=0 ../.venv_sbel/bin/python run_v047.py
```

The latest run produced `10` local rows in `31.2` seconds, kept rank `132`,
and did not invoke the full pipeline. No endpoint-pose predictor row spanned
the terminal bridge: `any_candidate_spans_terminal_bridge=false`. The best row
used `paper_endpoint_pose_positive_lagrange_z`, which evaluates the lower-pair
velocity constraint at the paper terminal pose with the positive part of the
Gauss-node terminal Lagrange velocity predictor. Its projection relative
residual improved to `0.117782`, but the independent target rank remained `8`.
The remaining missing direction was dominated by `translation_velocity_v` at
fraction `0.514237`, with stage fractions `0.961546`, `0.004167`, and
`0.034287`. This is the sharpest current local repair probe, but it is still a
gap rather than a full-TFE replacement.

A Gauss endpoint-pose generalized-velocity predictor screen checks whether the
same idea works better when the pose extrapolator is built directly from Gauss
stage positions:

```bash
V047_TARGET_AUDIT=lower_pair_recurrent_stage2_matrix_gradient_differential_audit V047_RECURRENT_STAGE2_MATRIX_LAWS=gauss_endpoint_pose_lagrange_z,gauss_endpoint_pose_positive_lagrange_z,gauss_endpoint_pose_paper_m3_y2_z,gauss_endpoint_pose_paper_m3_y2_positive_average_z,gauss_endpoint_pose_stage12_linear_z,gauss_endpoint_pose_stage02_linear_z,gauss_endpoint_pose_integrated_acceleration_z V047_RECURRENT_STAGE2_MATRIX_GAINS=0 ../.venv_sbel/bin/python run_v047.py
```

The run produced `7` local rows in `28.7` seconds, kept rank `132`, and did not
invoke the full pipeline. No Gauss endpoint-pose predictor row spanned the
terminal bridge: `any_candidate_spans_terminal_bridge=false`. The best row used
`gauss_endpoint_pose_positive_lagrange_z`, with projection residual `0.208599`,
independent target rank `8`, and a remaining rank-eight direction dominated by
`lie_position_u` at fraction `0.650605`; the stage fractions were `0.524567`,
`0.209731`, and `0.265702`. Since this is worse than the paper endpoint-pose
positive-Lagrange residual `0.117782`, it is recorded as a ruled-out
endpoint-pose alternative.

The untried Gauss endpoint-pose rows then get a separate bounded completion
screen:

```bash
V047_TARGET_AUDIT=lower_pair_recurrent_stage2_matrix_gradient_differential_audit V047_RECURRENT_STAGE2_MATRIX_LAWS=gauss_endpoint_pose_paper_m3_y2_positive_quarter_z,gauss_endpoint_pose_paper_m3_y2_positive_three_quarter_z,gauss_endpoint_pose_stage1_half_lagrange_z,gauss_endpoint_pose_stage02_convex_0p00_z,gauss_endpoint_pose_stage02_convex_0p05_z,gauss_endpoint_pose_stage02_convex_0p10_z,gauss_endpoint_pose_stage02_convex_0p15_z,gauss_endpoint_pose_stage02_convex_0p20_z,gauss_endpoint_pose_stage02_convex_0p25_z,gauss_endpoint_pose_stage01_mean_z,gauss_endpoint_pose_stage012_mean_z V047_RECURRENT_STAGE2_MATRIX_HISTORY_MODES=post_one_step V047_RECURRENT_STAGE2_MATRIX_GAINS=0 ../.venv_sbel/bin/python run_v047.py
```

This run produced `11` local rows in `31.5` seconds, kept rank `132`, and did
not invoke the full pipeline. The best row was
`gauss_endpoint_pose_stage02_convex_0p00_z`, with projection residual
`0.172659`, independent target rank `6`, and
`any_candidate_spans_terminal_bridge=false`. The remaining rank-six direction
was dominated by `lie_position_u` at fraction `0.952340`, with stage fractions
`0.320394`, `0.305625`, and `0.373981`. This completes the simple Gauss
endpoint-pose predictor family as a negative local screen.

A near-terminal stage-0/stage-2 convex predictor screen then separates a
degenerate local span from the first useful nonterminal row:

```bash
V047_TARGET_AUDIT=lower_pair_recurrent_stage2_matrix_gradient_differential_audit V047_RECURRENT_STAGE2_MATRIX_LAWS=paper_endpoint_pose_stage02_convex_0p00_z,paper_endpoint_pose_stage02_convex_0p05_z,paper_endpoint_pose_stage02_convex_0p10_z,paper_endpoint_pose_positive_lagrange_z,paper_endpoint_pose_stage02_convex_0p15_z,paper_endpoint_pose_stage02_convex_0p20_z,paper_endpoint_pose_stage02_convex_0p25_z V047_RECURRENT_STAGE2_MATRIX_GAINS=0 ../.venv_sbel/bin/python run_v047.py
```

The latest run produced `14` local rows in `31.7` seconds. The exact
stage-2-only law `paper_endpoint_pose_stage02_convex_0p00_z` spanned the
terminal bridge at roundoff, but it is marked
`terminal_bridge_equivalent_predictor=true`: it is the terminal-stage bridge
row already covered by the order-limited terminal/final-stage h-sweep, not an
independent full-TFE row. The best nonterminal law was
`paper_endpoint_pose_stage02_convex_0p05_z`, with projection residual
`0.049317`, independent target rank `8`, and
`any_nonterminal_candidate_spans_terminal_bridge=false`. Its remaining
direction was dominated by `translation_velocity_v` at fraction `0.510336`,
with stage fractions `0.976149`, `0.005850`, and `0.018002`. This is the best
current nonterminal local repair probe, but the full-TFE gate remains open.

A focused h-scaling spot check repeats the same three-law grid at `h=0.02`
and `h=0.01`, without invoking the full pipeline. The terminal-equivalent
`paper_endpoint_pose_stage02_convex_0p00_z` row spans at roundoff for both
steps (`1.082e-15` and `1.227e-15`), while the nonterminal
`paper_endpoint_pose_stage02_convex_0p05_z` row remains rank `8` with
projection residuals `0.051890` and `0.052472`. The h-scaling evidence
therefore points to a genuine missing nonterminal tangent, not a coarse-step
artifact or a weight-continuation path toward the terminal-equivalent row.
The next repair target remains a nonterminal analytical weak-row formula that
removes the stage-0-dominated lower-pair tangent.

A synchronized pose/velocity near-terminal follow-up then evaluates
`C_v(q_alpha,z_alpha)` at the same stage-0/stage-2 convex point instead of
using the terminal pose with only a nonterminal velocity predictor:

```bash
V047_TARGET_AUDIT=lower_pair_recurrent_stage2_matrix_gradient_differential_audit V047_RECURRENT_STAGE2_MATRIX_LAWS=paper_endpoint_pose_stage02_convex_0p05_z,stage02_convex_pose_velocity_0p01_z,stage02_convex_pose_velocity_0p02_z,stage02_convex_pose_velocity_0p05_z,stage02_convex_pose_velocity_0p10_z V047_RECURRENT_STAGE2_MATRIX_GAINS=0 ../.venv_sbel/bin/python run_v047.py
```

The latest run produced `10` local rows in `29.7` seconds, without invoking
the full pipeline. The best synchronized law
`stage02_convex_pose_velocity_0p01_z` improved the local projection residual
to `0.009512`, with independent target rank `8` and
`any_nonterminal_candidate_spans_terminal_bridge=false`. The residual remains
near `0.01` under h-scaling (`0.009978` at `h=0.02` and `0.010085` at
`h=0.01`). The weight sweep is also nearly proportional to the nonterminal
offset: `0p02` gives `0.019205`, `0p05` gives `0.049390`, and `0p10` gives
`0.103464`. This is stronger localization evidence, but it is still a
near-terminal limit toward the terminal bridge rather than an independent full
TFE replacement.

A terminal-limit extrapolation audit then combines two nonterminal synchronized
pose/velocity rows to remove the leading alpha offset. The law
`stage02_convex_pose_velocity_extrapolate_0p01_0p02_z` improves the local
residual to `4.699e-06` at `h=0.04`; a wider
`stage02_convex_pose_velocity_extrapolate_0p01_0p05_z` check gives
`1.175e-05`. The `0p01/0p02` residual halves under h-scaling (`2.335e-06` at
`h=0.02` and `1.168e-06` at `h=0.01`), but it still has no span
(`independent_target_rank=8` at `h=0.04/0.02`, `7` at `h=0.01`). These
extrapolated laws are marked `terminal_bridge_equivalent_predictor=true`: they
confirm the synchronized rows are approaching the terminal bridge, but they do
not supply an independent full-TFE stage row.

A mean-acceleration bridge correction follow-up tests whether the remaining
translation-acceleration tangent is simply the centered bridge's acceleration
term. The signed laws
`stage02_convex_pose_velocity_extrapolate_0p01_0p02_accel_m1_z` and
`stage02_convex_pose_velocity_extrapolate_0p01_0p02_accel_p1_z` add
`-1` or `+1` times `sqrt(b_2) h` times the mean acceleration closure to the
terminal-limit extrapolated row. They worsen the projection residual from
`4.699e-06` to at least `0.076159` and shift the missing direction to
`lie_position_u`. Thus the remaining tangent is not removed by directly adding
the existing bridge acceleration term; the next repair still needs a different
nonterminal analytical weak-row correction.

A bilinear active-velocity outer-product follow-up adds component-pair
coupling without using the target bridge to construct the formula:

```bash
V047_TARGET_AUDIT=lower_pair_recurrent_stage2_matrix_gradient_differential_audit V047_RECURRENT_STAGE2_MATRIX_LAWS=stage2_velocity_feature_outer_stage2_velocity,stage2_velocity_stage2_velocity_outer_feature,stage2_velocity_symmetric_stage2_velocity_outer_feature,stage2_minus_stage1_velocity_feature_outer_stage2_velocity,velocity_curvature_feature_outer_stage2_velocity,stage01_mean_velocity_feature_outer_stage2_velocity V047_RECURRENT_STAGE2_MATRIX_GAINS=1e8,1e12 ../.venv_sbel/bin/python run_v047.py
```

The latest run produced `24` local rows in `57.3` seconds, kept rank `132`, and
had max residual `2.483e-12`. No bilinear outer-product row spanned the
terminal bridge: `any_candidate_spans_terminal_bridge=false`. The best row used
`stage2_velocity_feature_outer_stage2_velocity` with gain `1e12`, but its
projection relative residual was only `0.898720`, with independent target rank
`8`. The largest closure value perturbation from the recurrent weak row was
`3.631e-09`, a relative perturbation of `8.340e+04`. This excludes the tested
feature/stage-2-velocity outer-product coefficient matrices and reinforces that
the better shifted-column active-law residual `0.576548` is localization
evidence, not a derived full-TFE weak row.

A componentwise active-velocity diagonal follow-up tests whether the missing
tangent is more local than the outer-product family:

```bash
V047_TARGET_AUDIT=lower_pair_recurrent_stage2_matrix_gradient_differential_audit V047_RECURRENT_STAGE2_MATRIX_LAWS=stage2_velocity_hadamard_diagonal_feature_stage2_velocity,stage2_velocity_shifted_hadamard_diagonal_feature_stage2_velocity,stage2_velocity_diagonal_plus_hadamard_row_feature_stage2_velocity,stage2_velocity_diagonal_plus_hadamard_column_feature_stage2_velocity,stage2_minus_stage1_velocity_shifted_hadamard_diagonal_feature_stage2_velocity,velocity_curvature_shifted_hadamard_diagonal_feature_stage2_velocity V047_RECURRENT_STAGE2_MATRIX_GAINS=1e8,1e12 ../.venv_sbel/bin/python run_v047.py
```

The latest run produced `24` local rows in `56.7` seconds, kept rank `132`, and
had max residual `2.483e-12`. No componentwise diagonal row spanned the
terminal bridge: `any_candidate_spans_terminal_bridge=false`. The best row used
`stage2_velocity_diagonal_plus_hadamard_row_feature_stage2_velocity` with gain
`1e12`, but its projection relative residual was only `0.898530`, with
independent target rank `8`. The largest closure value perturbation from the
recurrent weak row was `9.733e-09`, a relative perturbation of `2.235e+05`.
This excludes the tested componentwise and shifted-diagonal active-velocity
couplings as the missing weak row.

A stage-2 active translation/angular cross follow-up then tests six
target-free cross laws over zero-initial and post-one-step history modes:

```bash
V047_TARGET_AUDIT=lower_pair_recurrent_stage2_matrix_gradient_differential_audit V047_RECURRENT_STAGE2_MATRIX_LAWS=stage2_velocity_translation_to_angular_cross_feature,stage2_velocity_symmetric_translation_angular_cross_feature,stage2_velocity_shifted_translation_angular_cross_feature,stage2_minus_stage1_velocity_translation_to_angular_cross_feature,stage2_minus_stage1_velocity_symmetric_translation_angular_cross_feature,stage2_minus_stage1_velocity_shifted_translation_angular_cross_feature V047_RECURRENT_STAGE2_MATRIX_GAINS=1e8,1e12 ../.venv_sbel/bin/python run_v047.py
```

The latest run produced `24` local rows in `50.9` seconds, kept rank `132`,
and had max residual `2.483e-12`. No active translation/angular cross row
spanned the terminal bridge: `any_candidate_spans_terminal_bridge=false`. The
best row used `stage2_velocity_symmetric_translation_angular_cross_feature`
with gain `1e12`, but its projection relative residual was still `0.898843`,
with independent target rank `8`. The remaining missing direction was
dominated by `translation_velocity_v` with fraction `0.556036`, and its
stage-2 fraction was `0.999999`. This excludes simple active-velocity
translation/angular cross compression as the missing eight-row weak closure.

A non-stage-2 feature matrix follow-up then tests whether using a smoother
mean/history/source feature instead of raw stage-2 velocity provides the
missing coefficient-gradient closure:

```bash
V047_TARGET_AUDIT=lower_pair_recurrent_stage2_matrix_gradient_differential_audit V047_RECURRENT_STAGE2_MATRIX_LAWS=stage01_mean_velocity_shifted_column_broadcast_feature,stage01_mean_velocity_diagonal_plus_row_broadcast_feature,source02_delta_shifted_column_broadcast_feature,source02_delta_diagonal_plus_row_broadcast_feature,history_unit_delta_shifted_column_broadcast_feature,history_unit_delta_diagonal_plus_row_broadcast_feature V047_RECURRENT_STAGE2_MATRIX_HISTORY_MODES=post_one_step V047_RECURRENT_STAGE2_MATRIX_GAINS=1e8,1e12 ../.venv_sbel/bin/python run_v047.py
```

The latest run produced `12` local rows in `36.5` seconds, kept rank `132`,
and had max residual `2.483e-12`. No mean/source/history feature row spanned
the terminal bridge: `any_candidate_spans_terminal_bridge=false`. The best row
used `stage01_mean_velocity_diagonal_plus_row_broadcast_feature` with gain
`1e12`, improving the projection relative residual to `0.827381`, but the
independent target rank remained `8`. The largest closure value perturbation
from the recurrent weak row was `1.460e-06`, a relative perturbation of
`3.353e+07`. The remaining missing direction was still dominated by
`translation_velocity_v` with fraction `0.571311`, and its stage-2 fraction
was `0.991949`. This is useful localization but still not a derived full-TFE
weak closure.

A nonterminal acceleration-correction follow-up then tests whether the
near-terminal synchronized pose/velocity row only needs a simple acceleration
Taylor term. The first grid adds the centered bridge mean-acceleration closure
directly to `stage02_convex_pose_velocity_0p01_z` and `0p02` with signed
coefficients `m0p1`, `p0p1`, `m1`, and `p1`. The run produced `18` local rows
in `33.5` seconds, kept rank `132`, and still had
`any_nonterminal_candidate_spans_terminal_bridge=false`. The best row remained
the uncorrected `stage02_convex_pose_velocity_0p01_z` with residual `0.009512`;
the best small signed acceleration correction worsened to `0.012376` or
`0.014059`, and the unit corrections worsened to at least `0.077874`. This
excludes the tested nonterminal mean-acceleration closure corrections.
Representative laws include `stage02_convex_pose_velocity_0p01_accel_m0p1_z`
and `stage02_convex_pose_velocity_0p01_accel_p0p1_z`.

A second acceleration-correction follow-up adds the same signed coefficient as
a generalized-velocity Taylor shift, `z_alpha + gamma*h*zdot_alpha`, before
evaluating the lower-pair velocity constraint. This grid also produced `18`
local rows, in `33.8` seconds, with rank `132` and no nonterminal span. Again
the best row remained `stage02_convex_pose_velocity_0p01_z` at `0.009512`; the
best generalized-acceleration correction was `0.012376`, and unit corrections
were no better than `0.077874`. Thus neither direct lower-pair acceleration
closure nor generalized-velocity acceleration prediction supplies the missing
nonterminal weak row.
Representative laws include `stage02_convex_pose_velocity_0p01_genaccel_m0p1_z`
and `stage02_convex_pose_velocity_0p01_genaccel_p0p1_z`.

A kinematic pose-slope predictor follow-up then tests whether the missing
tangent is a geometry-consistent velocity estimate rather than a dynamic
acceleration term. It replaces or perturbs `z_alpha` toward the
stage-0/stage-2 pose slope `(q_2-q_0)/(h(c_2-c_0))` for the synchronized
`stage02_convex_pose_velocity_0p01_z` and `0p02` rows, with signed
coefficients `m0p1`, `p0p1`, `m0p5`, `p0p5`, `m1`, and `p1`. The targeted
audit produced `26` local rows in `37.1` seconds, kept rank `132`, and still
had `any_nonterminal_candidate_spans_terminal_bridge=false`. The best row
remained the uncorrected `stage02_convex_pose_velocity_0p01_z` with residual
`0.009512`; the best pose-slope correction,
`stage02_convex_pose_velocity_0p02_poseslope_m0p1_z`, had residual only
`0.878519`, with a stage-2-dominated remaining direction. This excludes the
tested nonterminal stage-pose-slope velocity predictor as the missing weak
row.

A source-to-velocity lift follow-up then tests a richer target-free source
law. It evaluates the current lower-pair endpoint velocity matrix
`C_{v,z}(q_alpha)` and maps source rows into a minimum-norm generalized
velocity correction by solving
`C_{v,z} C_{v,z}^{T} y = source`, then using
`delta z = C_{v,z}^{T} y`. The tested sources are the mean acceleration
closure, stage-0 and stage-2 source estimates, source curvature, and the
history/source delta. The full grid produced `34` local rows in `76.4` seconds
and kept rank `132`, but again had
`any_nonterminal_candidate_spans_terminal_bridge=false`. The best row overall
remained the uncorrected `stage02_convex_pose_velocity_0p01_z` with residual
`0.009512`. A focused rerun over the best source-lift rows found
`stage02_convex_pose_velocity_0p01_sourcelift_historydelta_p1_z` and
`stage02_convex_pose_velocity_0p01_sourcelift_source0_p1_z` tied as the best
source-lift corrections at residual `0.609803`, with independent target rank
`8`. Thus even a current-pose velocity-matrix lift of stage source data is not
the missing independent weak row.

A matrix-difference source-to-velocity lift then tests whether the missing
coefficient-gradient term is the change in `C_v` between the stage-0 and
stage-2 poses. It maps the same lower-pair source rows through both stage-pose
endpoint velocity matrices and inserts the difference of the resulting
minimum-norm generalized-velocity shifts. The first targeted JSON-only screen
covers `14` local rows in `58.7` seconds and has
`any_nonterminal_candidate_spans_terminal_bridge=false`; its coarse `10`
scale reaches only residual `0.042593`. A refined scale sweep over `0.1`,
`1`, and `10` then covers `26` local rows in `92.5` seconds. The best row
overall remains the uncorrected `stage02_convex_pose_velocity_0p01_z` at
residual `0.009512`; the best matrix-difference correction is
`stage02_convex_pose_velocity_0p01_sourceliftmatrixdiff_historydelta_p0p1_z`
at residual `0.009527`, still with independent target rank `8` and
`nonterminal_span_row_count=0`. Thus the direct stage-0/stage-2 `C_v`
coefficient-difference lift is also not the missing independent weak row, and
the failure is not just an overly large gain.

A nonlinear normalized-history source law then replaces the raw
`source0-history` vector by its direction, scaled by `||source0||`, before the
same stage-0/stage-2 `C_v` matrix-difference lift. This targeted JSON-only
screen covers `10` local rows in `49.4` seconds. It again has
`any_nonterminal_candidate_spans_terminal_bridge=false`; the best row overall
remains the uncorrected `stage02_convex_pose_velocity_0p01_z` at residual
`0.009512`, while the best normalized-history correction
`stage02_convex_pose_velocity_0p01_sourceliftmatrixdiff_historyunitdelta_p0p1_z`
reaches only residual `0.009590` with independent target rank `8`. Thus the
tested nonlinear recurrent-history source direction is also not the missing
independent weak row.

A near-terminal slope follow-up then tests whether the missing coefficient
gradient is the finite-difference slope of the synchronized
`stage02_convex_pose_velocity_*_z` family rather than the terminal-limit
intercept. The targeted command is:

```bash
V047_TARGET_AUDIT=lower_pair_recurrent_stage2_matrix_gradient_differential_audit V047_RECURRENT_STAGE2_MATRIX_LAWS=stage02_convex_pose_velocity_slope_0p01_0p02_z,stage02_convex_pose_velocity_slope_0p01_0p05_z,stage02_convex_pose_velocity_slopeh_0p01_0p02_z,stage02_convex_pose_velocity_slopeh_0p01_0p05_z V047_RECURRENT_STAGE2_MATRIX_HISTORY_MODES=post_one_step V047_RECURRENT_STAGE2_MATRIX_GAINS=0 ../.venv_sbel/bin/python run_v047.py
```

The latest JSON-only run produced `4` local rows in `25.8` seconds, kept rank
`132`, and had max residual `2.483e-12`. No slope row spanned the terminal
bridge: `any_candidate_spans_terminal_bridge=false`. The best law was
`stage02_convex_pose_velocity_slope_0p01_0p05_z`, with projection residual
`0.677034`, independent target rank `8`, dominant remaining variable family
`translation_velocity_v` at fraction `0.490108`, and stage fractions
`0.488191`, `0.030411`, and `0.481399`. Thus the first nonterminal slope of
the near-terminal convex pose/velocity family is also not the missing
independent weak row.

A near-terminal curvature follow-up then tests whether the missing coefficient
gradient is the second finite-difference curvature of the synchronized
`stage02_convex_pose_velocity_*_z` family. The targeted command is:

```bash
V047_TARGET_AUDIT=lower_pair_recurrent_stage2_matrix_gradient_differential_audit V047_RECURRENT_STAGE2_MATRIX_LAWS=stage02_convex_pose_velocity_curvature_0p01_0p02_0p05_z,stage02_convex_pose_velocity_curvatureh2_0p01_0p02_0p05_z,stage02_convex_pose_velocity_curvaturew2_0p01_0p02_0p05_z,stage02_convex_pose_velocity_curvature_0p01_0p05_0p10_z V047_RECURRENT_STAGE2_MATRIX_HISTORY_MODES=post_one_step V047_RECURRENT_STAGE2_MATRIX_GAINS=0 ../.venv_sbel/bin/python run_v047.py
```

The latest JSON-only run produced `4` local rows in `26.7` seconds, kept rank
`132`, and had max residual `2.483e-12`. No curvature row spanned the terminal
bridge: `any_candidate_spans_terminal_bridge=false`. The best law was
`stage02_convex_pose_velocity_curvature_0p01_0p05_0p10_z`, with projection
residual `0.871228`, independent target rank `8`, dominant remaining variable
family `translation_velocity_v` at fraction `0.591909`, and stage fractions
`0.092772`, `0.021144`, and `0.886084`. Thus the local curvature of the
near-terminal convex pose/velocity family is also not the missing independent
weak row.

A source/history coefficient-feature matrix follow-up then tests whether the
missing coefficient gradient is supplied by recurrent source features used as
shifted-column coefficient matrices on the stage-2 lower-pair velocity row.
The targeted command is:

```bash
V047_TARGET_AUDIT=lower_pair_recurrent_stage2_matrix_gradient_differential_audit V047_RECURRENT_STAGE2_MATRIX_LAWS=history_delta_shifted_column_broadcast_feature,history_unit_delta_shifted_column_broadcast_feature,source0_shifted_column_broadcast_feature,source2_shifted_column_broadcast_feature,source02_mean_shifted_column_broadcast_feature,source02_delta_shifted_column_broadcast_feature,source_curvature_shifted_column_broadcast_feature,source_curvature_history_delta_shifted_column_broadcast_feature V047_RECURRENT_STAGE2_MATRIX_HISTORY_MODES=post_one_step V047_RECURRENT_STAGE2_MATRIX_GAINS=1e8,1e12 ../.venv_sbel/bin/python run_v047.py
```

The latest JSON-only run produced `16` local rows in `44.8` seconds, kept rank
`132`, and had max residual `2.483e-12`. No source/history coefficient row
spanned the terminal bridge: `any_candidate_spans_terminal_bridge=false`. The
best law was `source_curvature_shifted_column_broadcast_feature`, with
projection residual `0.898873`, independent target rank `8`, dominant
remaining variable family `translation_velocity_v` at fraction `0.556060`, and
stage fractions `0.000000`, `0.000000`, and `1.000000`. Thus the tested
recurrent source/history coefficient-feature matrix rows are also not the
missing independent weak row.

A nonlinear recurrent curvature/history matrix-feature follow-up then mirrors
the scalar curvature/history features in the matrix-gradient family:

```bash
V047_TARGET_AUDIT=lower_pair_recurrent_stage2_matrix_gradient_differential_audit V047_RECURRENT_STAGE2_MATRIX_LAWS=source_curvature_minus_history_delta_shifted_column_broadcast_feature,source_curvature_minus_history_delta_diagonal_plus_row_broadcast_feature,source_curvature_history_hadamard_shifted_column_broadcast_feature,source_curvature_history_hadamard_diagonal_plus_row_broadcast_feature,source_curvature_history_unit_hadamard_shifted_column_broadcast_feature,source_curvature_history_unit_hadamard_diagonal_plus_row_broadcast_feature,normalized_source_curvature_history_delta_shifted_column_broadcast_feature,normalized_source_curvature_history_delta_diagonal_plus_row_broadcast_feature V047_RECURRENT_STAGE2_MATRIX_HISTORY_MODES=post_one_step V047_RECURRENT_STAGE2_MATRIX_GAINS=1e8,1e12 ../.venv_sbel/bin/python run_v047.py
```

The run produced `16` local rows in `45.5` seconds, kept rank `132`, and did
not invoke the full pipeline. No nonlinear curvature/history matrix-feature row
spanned the terminal bridge: `any_candidate_spans_terminal_bridge=false`. The
best law was
`source_curvature_minus_history_delta_diagonal_plus_row_broadcast_feature`,
with projection residual `0.898865`, independent target rank `8`, dominant
remaining family `translation_velocity_v` at fraction `0.556051`, and stage-2
fraction `0.999996`. Thus the tested nonlinear curvature/history matrix
features also remain a ruled-out local repair direction.

A terminal-limit source-lift matrix-difference follow-up then tests whether
the best near-terminal extrapolated intercept can be repaired by adding a
stage-local `C_v` source-to-velocity lift before extrapolation. The targeted
command is:

```bash
V047_TARGET_AUDIT=lower_pair_recurrent_stage2_matrix_gradient_differential_audit V047_RECURRENT_STAGE2_MATRIX_LAWS=stage02_convex_pose_velocity_extrapolate_0p01_0p02_sourceliftmatrixdiff_source0_m0p1_z,stage02_convex_pose_velocity_extrapolate_0p01_0p02_sourceliftmatrixdiff_source0_p0p1_z,stage02_convex_pose_velocity_extrapolate_0p01_0p02_sourceliftmatrixdiff_historydelta_m0p1_z,stage02_convex_pose_velocity_extrapolate_0p01_0p02_sourceliftmatrixdiff_historydelta_p0p1_z,stage02_convex_pose_velocity_extrapolate_0p01_0p02_sourceliftmatrixdiff_historyunitdelta_m0p1_z,stage02_convex_pose_velocity_extrapolate_0p01_0p02_sourceliftmatrixdiff_historyunitdelta_p0p1_z,stage02_convex_pose_velocity_extrapolate_0p01_0p02_sourceliftmatrixdiff_curvature_m0p1_z,stage02_convex_pose_velocity_extrapolate_0p01_0p02_sourceliftmatrixdiff_curvature_p0p1_z V047_RECURRENT_STAGE2_MATRIX_HISTORY_MODES=post_one_step V047_RECURRENT_STAGE2_MATRIX_GAINS=0 ../.venv_sbel/bin/python run_v047.py
```

The latest JSON-only run produced `8` local rows in `47.5` seconds, kept rank
`132`, and had max residual `2.483e-12`. No terminal-limit source-lift row
spanned the terminal bridge: `any_candidate_spans_terminal_bridge=false`. The
best law was
`stage02_convex_pose_velocity_extrapolate_0p01_0p02_sourceliftmatrixdiff_curvature_m0p1_z`,
with projection residual `5.298e-06`, independent target rank `8`, dominant
remaining variable family `translation_acceleration_a` at fraction `0.407672`,
and stage fractions `0.549481`, `0.005742`, and `0.444777`. Thus the tested
stage-local `C_v` source-lift correction of the terminal-limit extrapolated
row is also not the missing independent weak row.

A curvature source-lift scale refinement then tests whether the `0.1`
curvature lift coefficient was simply mis-scaled. The targeted JSON-only
command is:

```bash
V047_TARGET_AUDIT=lower_pair_recurrent_stage2_matrix_gradient_differential_audit V047_RECURRENT_STAGE2_MATRIX_LAWS=stage02_convex_pose_velocity_extrapolate_0p01_0p02_z,stage02_convex_pose_velocity_extrapolate_0p01_0p02_sourceliftmatrixdiff_curvature_m0p01_z,stage02_convex_pose_velocity_extrapolate_0p01_0p02_sourceliftmatrixdiff_curvature_p0p01_z,stage02_convex_pose_velocity_extrapolate_0p01_0p02_sourceliftmatrixdiff_curvature_m0p05_z,stage02_convex_pose_velocity_extrapolate_0p01_0p02_sourceliftmatrixdiff_curvature_p0p05_z,stage02_convex_pose_velocity_extrapolate_0p01_0p02_sourceliftmatrixdiff_curvature_m0p1_z,stage02_convex_pose_velocity_extrapolate_0p01_0p02_sourceliftmatrixdiff_curvature_p0p1_z,stage02_convex_pose_velocity_extrapolate_0p01_0p02_sourceliftmatrixdiff_curvature_m0p2_z,stage02_convex_pose_velocity_extrapolate_0p01_0p02_sourceliftmatrixdiff_curvature_p0p2_z,stage02_convex_pose_velocity_extrapolate_0p01_0p02_sourceliftmatrixdiff_curvature_m0p5_z,stage02_convex_pose_velocity_extrapolate_0p01_0p02_sourceliftmatrixdiff_curvature_p0p5_z V047_RECURRENT_STAGE2_MATRIX_HISTORY_MODES=post_one_step V047_RECURRENT_STAGE2_MATRIX_GAINS=0 ../.venv_sbel/bin/python run_v047.py
```

It produced `11` local rows in `52.9` seconds, kept rank `132`, did not invoke
the full pipeline, and found no span. The best law was
`stage02_convex_pose_velocity_extrapolate_0p01_0p02_sourceliftmatrixdiff_curvature_p0p01_z`,
with projection residual `5.298e-06`, independent target rank `8`, dominant
remaining family `translation_acceleration_a` at fraction `0.407672`, and
stage fractions `0.549481`, `0.005742`, and `0.444777`. The local
`source_curvature_norm` was only `1.076e-14`, so changing the lift coefficient
over `0.01`, `0.05`, `0.1`, `0.2`, and `0.5` does not change the tangent
enough to create a span. This rules out a simple curvature source-lift
coefficient-scale repair.

A mean-acceleration bridge scale refinement then tests whether the earlier
`accel_m1/accel_p1` bridge correction failed only because the coefficient was
too large. The targeted JSON-only command is:

```bash
V047_TARGET_AUDIT=lower_pair_recurrent_stage2_matrix_gradient_differential_audit V047_RECURRENT_STAGE2_MATRIX_LAWS=stage02_convex_pose_velocity_extrapolate_0p01_0p02_z,stage02_convex_pose_velocity_extrapolate_0p01_0p02_accel_m0p01_z,stage02_convex_pose_velocity_extrapolate_0p01_0p02_accel_p0p01_z,stage02_convex_pose_velocity_extrapolate_0p01_0p02_accel_m0p05_z,stage02_convex_pose_velocity_extrapolate_0p01_0p02_accel_p0p05_z,stage02_convex_pose_velocity_extrapolate_0p01_0p02_accel_m0p1_z,stage02_convex_pose_velocity_extrapolate_0p01_0p02_accel_p0p1_z,stage02_convex_pose_velocity_extrapolate_0p01_0p02_accel_m0p2_z,stage02_convex_pose_velocity_extrapolate_0p01_0p02_accel_p0p2_z,stage02_convex_pose_velocity_extrapolate_0p01_0p02_accel_m0p5_z,stage02_convex_pose_velocity_extrapolate_0p01_0p02_accel_p0p5_z V047_RECURRENT_STAGE2_MATRIX_HISTORY_MODES=post_one_step V047_RECURRENT_STAGE2_MATRIX_GAINS=0 ../.venv_sbel/bin/python run_v047.py
```

It produced `11` local rows in `31.4` seconds, kept rank `132`, did not invoke
the full pipeline, and found no span. The overall best row remained the
terminal-bridge-equivalent uncorrected extrapolated row, with residual
`5.298e-06`. The best nonterminal bridge-correction law was
`stage02_convex_pose_velocity_extrapolate_0p01_0p02_accel_p0p01_z`, but its
projection residual was still `0.000867721`, with independent target rank `8`
and dominant remaining family `lie_position_u` at fraction `0.706665`. Thus
small mean-acceleration bridge coefficients do not provide the missing
independent row either.

A generalized-acceleration Taylor-shift scale refinement then applies the
same terminal-limit extrapolation to stage-local generalized acceleration
shifts, using the left and right convex-point accelerations separately. The
targeted JSON-only command is:

```bash
V047_TARGET_AUDIT=lower_pair_recurrent_stage2_matrix_gradient_differential_audit V047_RECURRENT_STAGE2_MATRIX_LAWS=stage02_convex_pose_velocity_extrapolate_0p01_0p02_z,stage02_convex_pose_velocity_extrapolate_0p01_0p02_genaccel_m0p01_z,stage02_convex_pose_velocity_extrapolate_0p01_0p02_genaccel_p0p01_z,stage02_convex_pose_velocity_extrapolate_0p01_0p02_genaccel_m0p05_z,stage02_convex_pose_velocity_extrapolate_0p01_0p02_genaccel_p0p05_z,stage02_convex_pose_velocity_extrapolate_0p01_0p02_genaccel_m0p1_z,stage02_convex_pose_velocity_extrapolate_0p01_0p02_genaccel_p0p1_z,stage02_convex_pose_velocity_extrapolate_0p01_0p02_genaccel_m0p2_z,stage02_convex_pose_velocity_extrapolate_0p01_0p02_genaccel_p0p2_z,stage02_convex_pose_velocity_extrapolate_0p01_0p02_genaccel_m0p5_z,stage02_convex_pose_velocity_extrapolate_0p01_0p02_genaccel_p0p5_z V047_RECURRENT_STAGE2_MATRIX_HISTORY_MODES=post_one_step V047_RECURRENT_STAGE2_MATRIX_GAINS=0 ../.venv_sbel/bin/python run_v047.py
```

It produced `11` local rows in `30.2` seconds, kept rank `132`, did not invoke
the full pipeline, and found no span. The overall best row again remained the
terminal-bridge-equivalent uncorrected extrapolated row, with residual
`5.298e-06`. The best nonterminal generalized-acceleration law was
`stage02_convex_pose_velocity_extrapolate_0p01_0p02_genaccel_p0p01_z`, but its
projection residual was still `0.000866899`, with independent target rank `8`
and dominant remaining family `lie_position_u` at fraction `0.701135`. This
slightly improves the small mean-acceleration bridge residual but still does
not supply an independent spanning row.

A pose-acceleration Taylor-shift scale refinement then applies the same
terminal-limit extrapolation to stage-local `h^2*zdot` pose shifts, using the
left and right convex-point accelerations separately before evaluating the
endpoint velocity matrix. The targeted JSON-only command is:

```bash
V047_TARGET_AUDIT=lower_pair_recurrent_stage2_matrix_gradient_differential_audit V047_RECURRENT_STAGE2_MATRIX_LAWS=stage02_convex_pose_velocity_extrapolate_0p01_0p02_z,stage02_convex_pose_velocity_extrapolate_0p01_0p02_poseaccel_m0p01_z,stage02_convex_pose_velocity_extrapolate_0p01_0p02_poseaccel_p0p01_z,stage02_convex_pose_velocity_extrapolate_0p01_0p02_poseaccel_m0p05_z,stage02_convex_pose_velocity_extrapolate_0p01_0p02_poseaccel_p0p05_z,stage02_convex_pose_velocity_extrapolate_0p01_0p02_poseaccel_m0p1_z,stage02_convex_pose_velocity_extrapolate_0p01_0p02_poseaccel_p0p1_z,stage02_convex_pose_velocity_extrapolate_0p01_0p02_poseaccel_m0p2_z,stage02_convex_pose_velocity_extrapolate_0p01_0p02_poseaccel_p0p2_z,stage02_convex_pose_velocity_extrapolate_0p01_0p02_poseaccel_m0p5_z,stage02_convex_pose_velocity_extrapolate_0p01_0p02_poseaccel_p0p5_z V047_RECURRENT_STAGE2_MATRIX_HISTORY_MODES=post_one_step V047_RECURRENT_STAGE2_MATRIX_GAINS=0 ../.venv_sbel/bin/python run_v047.py
```

It produced `11` local rows in `29.9` seconds, kept rank `132`, did not invoke
the full pipeline, and found no span. The overall best row again remained the
terminal-bridge-equivalent uncorrected extrapolated row, with residual
`5.298e-06`. The best nonterminal pose-acceleration law was
`stage02_convex_pose_velocity_extrapolate_0p01_0p02_poseaccel_p0p01_z`, with
projection residual `4.1835e-05`, independent target rank `8`, dominant
remaining family `lie_position_u` at fraction `0.711570`, and stage-2 fraction
`0.771337`. This is a stronger pose-directed local perturbation than the
velocity-only generalized-acceleration shift, but it still does not supply an
independent spanning row.

A tiny pose-acceleration scale refinement then tests whether that result is
just a missed small coefficient. The targeted JSON-only command is:

```bash
V047_TARGET_AUDIT=lower_pair_recurrent_stage2_matrix_gradient_differential_audit V047_RECURRENT_STAGE2_MATRIX_LAWS=stage02_convex_pose_velocity_extrapolate_0p01_0p02_z,stage02_convex_pose_velocity_extrapolate_0p01_0p02_poseaccel_m0p0005_z,stage02_convex_pose_velocity_extrapolate_0p01_0p02_poseaccel_p0p0005_z,stage02_convex_pose_velocity_extrapolate_0p01_0p02_poseaccel_m0p001_z,stage02_convex_pose_velocity_extrapolate_0p01_0p02_poseaccel_p0p001_z,stage02_convex_pose_velocity_extrapolate_0p01_0p02_poseaccel_m0p002_z,stage02_convex_pose_velocity_extrapolate_0p01_0p02_poseaccel_p0p002_z,stage02_convex_pose_velocity_extrapolate_0p01_0p02_poseaccel_m0p005_z,stage02_convex_pose_velocity_extrapolate_0p01_0p02_poseaccel_p0p005_z,stage02_convex_pose_velocity_extrapolate_0p01_0p02_poseaccel_p0p01_z V047_RECURRENT_STAGE2_MATRIX_HISTORY_MODES=post_one_step V047_RECURRENT_STAGE2_MATRIX_GAINS=0 ../.venv_sbel/bin/python run_v047.py
```

It produced `10` local rows in `30.0` seconds, kept rank `132`, did not invoke
the full pipeline, and found no span. The overall best row again remained the
terminal-bridge-equivalent uncorrected extrapolated row, with residual
`5.298e-06`. The best nonterminal tiny pose-acceleration law was
`stage02_convex_pose_velocity_extrapolate_0p01_0p02_poseaccel_p0p0005_z`, with
projection residual `5.5898e-06`, independent target rank `8`, and dominant
remaining family `translation_acceleration_a` at fraction `0.350240`. Thus
small coefficients only approach the terminal-equivalent row and still do not
create an independent spanning row.

A pose+velocity acceleration Taylor refinement then combines the small
`h^2*zdot` pose shift with signed small `h*zdot` velocity shifts. The targeted
JSON-only command is:

```bash
V047_TARGET_AUDIT=lower_pair_recurrent_stage2_matrix_gradient_differential_audit V047_RECURRENT_STAGE2_MATRIX_LAWS=stage02_convex_pose_velocity_extrapolate_0p01_0p02_z,stage02_convex_pose_velocity_extrapolate_0p01_0p02_posevelaccel_p0p0005_m0p0001_z,stage02_convex_pose_velocity_extrapolate_0p01_0p02_posevelaccel_p0p0005_p0p0001_z,stage02_convex_pose_velocity_extrapolate_0p01_0p02_posevelaccel_p0p0005_m0p0005_z,stage02_convex_pose_velocity_extrapolate_0p01_0p02_posevelaccel_p0p0005_p0p0005_z,stage02_convex_pose_velocity_extrapolate_0p01_0p02_posevelaccel_p0p0005_m0p001_z,stage02_convex_pose_velocity_extrapolate_0p01_0p02_posevelaccel_p0p0005_p0p001_z,stage02_convex_pose_velocity_extrapolate_0p01_0p02_posevelaccel_m0p0005_m0p0005_z,stage02_convex_pose_velocity_extrapolate_0p01_0p02_posevelaccel_m0p0005_p0p0005_z,stage02_convex_pose_velocity_extrapolate_0p01_0p02_posevelaccel_p0p001_m0p0005_z,stage02_convex_pose_velocity_extrapolate_0p01_0p02_posevelaccel_p0p001_p0p0005_z V047_RECURRENT_STAGE2_MATRIX_HISTORY_MODES=post_one_step V047_RECURRENT_STAGE2_MATRIX_GAINS=0 ../.venv_sbel/bin/python run_v047.py
```

It produced `11` local rows in `30.7` seconds, kept rank `132`, did not invoke
the full pipeline, and found no span. The overall best row again remained the
terminal-bridge-equivalent uncorrected extrapolated row, with residual
`5.298e-06`. The best nonterminal combined law was
`stage02_convex_pose_velocity_extrapolate_0p01_0p02_posevelaccel_p0p0005_m0p0001_z`,
with projection residual `1.0173e-05`, independent target rank `8`, and
dominant remaining family `lie_position_u` at fraction `0.544660`. Thus the
simple combined Taylor pose/velocity shift still does not create an
independent spanning row.

The component-split pose-acceleration refinement separates the same `h^2*zdot`
pose shift into translation-only and angular/Lie-only branches:

```bash
V047_TARGET_AUDIT=lower_pair_recurrent_stage2_matrix_gradient_differential_audit V047_RECURRENT_STAGE2_MATRIX_LAWS=stage02_convex_pose_velocity_extrapolate_0p01_0p02_z,stage02_convex_pose_velocity_extrapolate_0p01_0p02_transposeaccel_m0p01_z,stage02_convex_pose_velocity_extrapolate_0p01_0p02_transposeaccel_p0p01_z,stage02_convex_pose_velocity_extrapolate_0p01_0p02_transposeaccel_m0p05_z,stage02_convex_pose_velocity_extrapolate_0p01_0p02_transposeaccel_p0p05_z,stage02_convex_pose_velocity_extrapolate_0p01_0p02_transposeaccel_m0p1_z,stage02_convex_pose_velocity_extrapolate_0p01_0p02_transposeaccel_p0p1_z,stage02_convex_pose_velocity_extrapolate_0p01_0p02_angposeaccel_m0p002_z,stage02_convex_pose_velocity_extrapolate_0p01_0p02_angposeaccel_p0p002_z,stage02_convex_pose_velocity_extrapolate_0p01_0p02_angposeaccel_m0p005_z,stage02_convex_pose_velocity_extrapolate_0p01_0p02_angposeaccel_p0p005_z,stage02_convex_pose_velocity_extrapolate_0p01_0p02_angposeaccel_m0p01_z,stage02_convex_pose_velocity_extrapolate_0p01_0p02_angposeaccel_p0p01_z V047_RECURRENT_STAGE2_MATRIX_HISTORY_MODES=post_one_step V047_RECURRENT_STAGE2_MATRIX_GAINS=0 ../.venv_sbel/bin/python run_v047.py
```

Together with the tiny-scale split, the two JSON-only screens cover `26` local
rows in `32.3+32.3` seconds, keep rank `132`, do not invoke the full pipeline,
and find no span. Translation-only shifts up to coefficient `0.1` remain
locally indistinguishable from the uncorrected terminal-limit row; the best
nonterminal law is
`stage02_convex_pose_velocity_extrapolate_0p01_0p02_transposeaccel_m0p01_z`,
with projection residual `5.298e-06`, independent target rank `8`, and
dominant remaining family `translation_acceleration_a` at fraction `0.407672`.
The angular-only branch reproduces the earlier full pose-acceleration behavior:
`angposeaccel_p0p002` reaches `9.6511e-06`, while `angposeaccel_p0p01` reaches
`4.1835e-05`. Thus translation-only pose motion is not the missing weak row,
and the pose-acceleration effect is angular/Lie-pose dominated.

A component-split velocity-acceleration Taylor refinement then separates the
same `h*zdot` generalized-velocity shift into translational and angular
velocity branches:

```bash
V047_TARGET_AUDIT=lower_pair_recurrent_stage2_matrix_gradient_differential_audit V047_RECURRENT_STAGE2_MATRIX_LAWS=stage02_convex_pose_velocity_extrapolate_0p01_0p02_z,stage02_convex_pose_velocity_extrapolate_0p01_0p02_transvelaccel_m0p01_z,stage02_convex_pose_velocity_extrapolate_0p01_0p02_transvelaccel_p0p01_z,stage02_convex_pose_velocity_extrapolate_0p01_0p02_angvelaccel_m0p01_z,stage02_convex_pose_velocity_extrapolate_0p01_0p02_angvelaccel_p0p01_z V047_RECURRENT_STAGE2_MATRIX_HISTORY_MODES=post_one_step V047_RECURRENT_STAGE2_MATRIX_GAINS=0 ../.venv_sbel/bin/python run_v047.py
```

The full first screen covers `13` local rows in `31.8` seconds, keeps rank
`132`, does not invoke the full pipeline, and finds no span. The best
nonterminal velocity-acceleration law is
`stage02_convex_pose_velocity_extrapolate_0p01_0p02_transvelaccel_m0p01_z`,
with projection residual `2.138e-04`, independent target rank `8`, and
dominant remaining family `translation_acceleration_a` at fraction `0.886603`.
The best angular velocity branch is `angvelaccel_p0p01`, with residual
`0.000864560` and dominant `lie_position_u`.

A tiny translational scale follow-up then tests coefficients `0.0005`,
`0.001`, `0.002`, and `0.005` with both signs. It covers `11` local rows in
`31.4` seconds, keeps rank `132`, and also has no span. The best nonterminal
tiny law is
`stage02_convex_pose_velocity_extrapolate_0p01_0p02_transvelaccel_m0p0005_z`,
with projection residual `9.8175e-06`, independent target rank `8`, dominant
remaining family `translation_acceleration_a` at fraction `0.802349`, and
stage-2 fraction `0.622536`. Since the uncorrected terminal-limit row remains
better at `5.298e-06`, this rules out the tested component-split
velocity-acceleration Taylor shift as the missing independent row.

A component-mixed pose/velocity Taylor refinement then combines the most
plausible split directions from the preceding two probes: angular/Lie pose
shift with translational velocity shift, plus the complementary
translation-pose/angular-velocity branch.

```bash
V047_TARGET_AUDIT=lower_pair_recurrent_stage2_matrix_gradient_differential_audit V047_RECURRENT_STAGE2_MATRIX_LAWS=stage02_convex_pose_velocity_extrapolate_0p01_0p02_z,stage02_convex_pose_velocity_extrapolate_0p01_0p02_angpose_transvelaccel_p0p0005_m0p0005_z,stage02_convex_pose_velocity_extrapolate_0p01_0p02_transpose_angvelaccel_m0p01_p0p01_z V047_RECURRENT_STAGE2_MATRIX_HISTORY_MODES=post_one_step V047_RECURRENT_STAGE2_MATRIX_GAINS=0 ../.venv_sbel/bin/python run_v047.py
```

The full screen covers `13` local rows in `32.0` seconds, keeps rank `132`,
does not invoke the full pipeline, and finds no span. The best nonterminal law
is
`stage02_convex_pose_velocity_extrapolate_0p01_0p02_angpose_transvelaccel_p0p0005_m0p0005_z`,
with projection residual `9.987e-06`, independent target rank `8`, dominant
remaining family `translation_acceleration_a` at fraction `0.774582`, and
stage-2 fraction `0.625975`. The complementary
`transpose_angvelaccel` branch reaches only `0.000864560`. Since the
uncorrected terminal-limit row remains better at `5.298e-06`, this rules out
the tested component-mixed Taylor cross term.

A stage-2-fixed/delta acceleration velocity-shift refinement then tests whether
the remaining `translation_acceleration_a` direction is caused by the
interpolated acceleration source in the velocity shift:

```bash
V047_TARGET_AUDIT=lower_pair_recurrent_stage2_matrix_gradient_differential_audit V047_RECURRENT_STAGE2_MATRIX_LAWS=stage02_convex_pose_velocity_extrapolate_0p01_0p02_z,stage02_convex_pose_velocity_extrapolate_0p01_0p02_transvelaccelstage2_m0p0005_z,stage02_convex_pose_velocity_extrapolate_0p01_0p02_transvelacceldelta20_m0p0005_z V047_RECURRENT_STAGE2_MATRIX_HISTORY_MODES=post_one_step V047_RECURRENT_STAGE2_MATRIX_GAINS=0 ../.venv_sbel/bin/python run_v047.py
```

The full screen covers `13` local rows in `31.8` seconds, keeps rank `132`,
does not invoke the full pipeline, and finds no span. The best nonterminal law
is
`stage02_convex_pose_velocity_extrapolate_0p01_0p02_transvelaccelstage2_m0p0005_z`,
with projection residual `9.8175e-06`, independent target rank `8`, dominant
remaining family `translation_acceleration_a` at fraction `0.802349`, and
stage-2 fraction `0.622536`. The best delta20 branch,
`stage02_convex_pose_velocity_extrapolate_0p01_0p02_transvelacceldelta20_m0p0005_z`,
reaches only `1.0119e-05`. This reproduces the earlier tiny translational
velocity-shift limit and rules out stage-2-fixed or delta20 acceleration
sources as the independent correction.

A nonfinal terminal velocity/source predictor refinement then tests a more
independent weak-row shape: predict the terminal lower-pair velocity closure
from only stage-0/stage-1 velocity rows and source estimates.

```bash
V047_TARGET_AUDIT=lower_pair_recurrent_stage2_matrix_gradient_differential_audit V047_RECURRENT_STAGE2_MATRIX_LAWS=stage02_convex_pose_velocity_extrapolate_0p01_0p02_z,nonfinal_velocity_terminal_linear01_z,nonfinal_velocity_terminal_euler0_z,nonfinal_velocity_terminal_euler1_z,nonfinal_velocity_terminal_ab01_z,nonfinal_velocity_terminal_source01mean0_z,nonfinal_velocity_terminal_source01linear0_z,nonfinal_velocity_terminal_source01linear1_z,nonfinal_velocity_terminal_hermite01_z V047_RECURRENT_STAGE2_MATRIX_HISTORY_MODES=post_one_step V047_RECURRENT_STAGE2_MATRIX_GAINS=0 ../.venv_sbel/bin/python run_v047.py
```

The full screen covers `9` local rows in `30.9` seconds, keeps rank `132`,
does not invoke the full pipeline, and finds no span. The best nonterminal law
is `nonfinal_velocity_terminal_euler1_z`, with projection residual `0.923466`,
independent target rank `8`, dominant remaining family `translation_velocity_v`
at fraction `0.526951`, and stage-2 fraction `0.959959`. The Hermite, linear,
Adams-Bashforth, source-mean, and source-linear variants all stay between
`0.923466` and `0.930013`. This rules out plain nonfinal velocity/source
terminal extrapolation and points the next repair toward a nonlinear stage-2
transport/source mechanism rather than a stage0/1 integral predictor.

The same family was then promoted to the bounded nonlinear trajectory h-sweep
target. The stage-0/stage-1 rows
`nonfinal_velocity_terminal_linear01/euler0/euler1/ab01/source01mean0/source01linear0/source01linear1/hermite01`
run in `135.3` seconds with `projection_used=false`, rank `132`, and all `24`
trajectory rows converged, but the terminal velocity remains open: the best
max terminal velocity is `1.770e-07`, and the order-friendlier
`euler1/ab01/source01linear1` rows remain at `3.584e-07`. The stage-0/1/2
extension adds `nonfinal_velocity_terminal_linear012_z`,
`nonfinal_velocity_terminal_euler2_z`, `ab12`, `source12mean2`,
`source12linear2`, and `hermite12`; it runs in `101.1` seconds, keeps rank
`132`, and converges all `18` rows, but again has
`terminal_velocity_closed=false`. Its near-terminal stage-2 rows reach
`2.559e-11` at `h=0.04` but jump to `1.328e-07` at `h=0.02`, while the best
stable terminal magnitude is `1.134e-07` from `linear012`. Thus the next repair
cannot be a plain nonfinal terminal velocity/source predictor, even when the
third Gauss stage is included.

A stage-2 source-to-velocity transport refinement then applies the existing
source/history-to-generalized-velocity projection directly at the stage-2
pose/velocity closure:

```bash
V047_TARGET_AUDIT=lower_pair_recurrent_stage2_matrix_gradient_differential_audit V047_RECURRENT_STAGE2_MATRIX_LAWS=stage02_convex_pose_velocity_extrapolate_0p01_0p02_z,stage02_convex_pose_velocity_0p00_sourcelift_source0_m0p1_z,stage02_convex_pose_velocity_0p00_sourcelift_source0_p0p1_z,stage02_convex_pose_velocity_0p00_sourceliftmatrixdiff_historydelta_m0p1_z,stage02_convex_pose_velocity_0p00_sourceliftmatrixdiff_historydelta_p0p1_z V047_RECURRENT_STAGE2_MATRIX_HISTORY_MODES=post_one_step V047_RECURRENT_STAGE2_MATRIX_GAINS=0 ../.venv_sbel/bin/python run_v047.py
```

The first full screen covers `13` local rows in `53.4` seconds, keeps rank
`132`, does not invoke the full pipeline, and finds no span. The best
nonterminal law is
`stage02_convex_pose_velocity_0p00_sourceliftmatrixdiff_historydelta_m0p1_z`,
with projection residual `0.001251`, independent target rank `6`, dominant
remaining family `lie_position_u` at fraction `0.597218`, and stage-2 fraction
`0.476626`. A scale refinement over the same matrix-difference history-delta
family covers `11` local rows in `57.7` seconds and improves the best residual
to `0.0001251` at
`stage02_convex_pose_velocity_0p00_sourceliftmatrixdiff_historydelta_m0p01_z`,
still with independent target rank `6` and no span. An ultra-fine scale
follow-up over `0.0001`, `0.0002`, `0.0005`, and `0.001` covers `9` local rows
in `49.6` seconds and pushes the best nonterminal residual to `1.251e-06` at
`stage02_convex_pose_velocity_0p00_sourceliftmatrixdiff_historydelta_m0p0001_z`,
again with rank `6`, dominant `lie_position_u`, and no span. A combined
source-transport/angular-pose follow-up then tests whether this clue needs a
small independent Lie-pose acceleration component. It covers `8` local rows in
`48.7` seconds. The source-only row remains best at `1.251e-06`; the best
combined row is
`stage02_convex_pose_velocity_0p00_sourceliftmatrixdiff_historydelta_m0p0001_angposeaccel_p0p0001_z`
at residual `1.296e-06`, independent target rank `8`, dominant
`lie_position_u`, and no span. A final bare endpoint-pose velocity probe adds
`stage02_convex_pose_velocity_0p00_z` next to the ultra-fine transport row and
`stage02_convex_pose_velocity_0p01_z`. It covers `3` local rows in `31.7`
seconds, does not invoke the full pipeline, and finds a local row-space span at
roundoff for the bare row: projection residual `1.327e-15`, independent target
rank `0`, `span_row_count=1`, and `nonterminal_span_row_count=1`. The
ultra-fine transported row remains no-span at `1.251e-06`, confirming that the
transport family was converging toward the bare endpoint row rather than
adding the missing independent tangent. This is local-span-not-full-TFE
evidence: it has no nonlinear trajectory h-sweep, no order proof, and still
reports `full_tfe_stage_replacement=false`. The next bounded repair target is
therefore to promote the best target-free endpoint-pose predictor to a
trajectory h-sweep before making any acceptance claim.

That promotion is now implemented as a JSON-only target:

```bash
V047_TARGET_AUDIT=lower_pair_endpoint_pose_velocity_predictor_h_sweep_smoke ../.venv_sbel/bin/python run_v047.py
```

The default target is intentionally bounded: smooth-only,
`stage02_convex_pose_velocity_0p00_z`, `h=[0.04,0.02]`,
`reference_h=0.01`, and `t_final=0.04`. It runs in `21.5` seconds, keeps rank
`132`, converges all `3` requested steps, and closes terminal velocity to
`7.29e-17`, but the two-point position/velocity orders are `6.588/4.508`, so
`smooth_order_ok=false` and `accepted_h_sweep_present=false`. A smooth-only
three-h refinement,

```bash
V047_TARGET_AUDIT=lower_pair_endpoint_pose_velocity_predictor_h_sweep_smoke V047_ENDPOINT_POSE_VELOCITY_H_SWEEP_VALUES=0.04,0.02,0.01 V047_ENDPOINT_POSE_VELOCITY_H_SWEEP_REFERENCE_H=0.005 V047_ENDPOINT_POSE_VELOCITY_H_SWEEP_T_FINAL=0.04 V047_ENDPOINT_POSE_VELOCITY_H_SWEEP_CASES=cylindrical_smooth ../.venv_sbel/bin/python run_v047.py
```

runs in `28.6` seconds, keeps rank `132`, converges all `7` requested steps,
and closes terminal velocity to `8.124e-17`, but the position/velocity orders
are only `4.142/2.305`. The neighboring nonterminal predictor
`stage02_convex_pose_velocity_0p01_z` also converges in the default smoke, but
terminal velocity remains `6.255e-06` and the two-point orders are
`2.345/1.878`. Thus the next repair target is no longer merely to promote the
local span; it is to derive a nonterminal endpoint-pose predictor that closes
terminal velocity on trajectory without the order loss.

The best source-transport local clue has also been tested at trajectory level.
The source-only row
`stage02_convex_pose_velocity_0p00_sourceliftmatrixdiff_historydelta_m0p0001_z`
fails the three-h smooth smoke with max/finest terminal velocity
`8.020e-12`/`5.904e-13` and orders `4.142/2.305`. A ten-times smaller
coefficient,
`stage02_convex_pose_velocity_0p00_sourceliftmatrixdiff_historydelta_m0p00001_z`,
does close the terminal tolerance in `43.6` seconds with rank `132`,
`projection_used=false`, max/finest terminal velocity `8.021e-13`/`5.910e-14`,
and all `7` short-sweep steps converged. It still has
`smooth_order_ok=false` with orders `4.142/2.305`. This rules out simple
source-transport coefficient shrinking: it can close terminal velocity only by
approaching the same order-limited endpoint-row behavior.

The non-projection terminal-limit extrapolation
`stage02_convex_pose_velocity_extrapolate_0p01_0p02_z` is better than the raw
`0p01` row but still not an acceptance candidate. The default bounded
smooth-only smoke runs in `21.8` seconds, keeps rank `132`, uses
`projection_used=false`, reduces max terminal velocity to `1.254e-07`, and
has two-point orders `6.412/3.775`. The three-h smooth refinement runs in
`28.9` seconds, converges all `7` requested steps, keeps rank `132`, has max
terminal velocity `1.254e-07` with the finest-h row at `1.244e-08`, and gives
only `4.054/2.364` position/velocity order. This is the best non-projection
trajectory clue so far, but it still fails terminal closure and smooth-order
acceptance.

A closer non-projection extrapolation sweep confirms that this is a
terminal-limit degeneracy rather than a missing scalar offset. The default
two-h smoke for `0p005/0p01`, `0p002/0p005`, and `0p001/0p002` runs in `55.2`
seconds with rank `132`, `projection_used=false`, and terminal velocities
`3.135e-08`, `6.270e-09`, and `1.254e-09`, but the velocity orders are still
only `4.648`, `4.566`, and `4.521`. A three-h refinement of
`stage02_convex_pose_velocity_extrapolate_0p001_0p002_z` runs in `27.6`
seconds and has max/finest terminal velocities `1.254e-09`/`1.244e-10`, but
orders `4.143/2.307`. The ultra-near
`stage02_convex_pose_velocity_extrapolate_0p00001_0p00002_z` case closes the
terminal velocity tolerance without projection: the two-h smoke gives terminal
velocity `1.254e-13`, and the three-h refinement runs in `30.4` seconds with
`terminal_velocity_closed=true`, max terminal velocity `1.254e-13`, finest-h
terminal velocity `1.254e-14`, and orders `4.142/2.305`. Therefore the repair
cannot be "move the nonterminal extrapolation points closer to the endpoint";
that recovers the terminal row's closure and the terminal row's order loss.

A quadratic nonterminal extrapolation branch tests the next obvious variant:
estimate the terminal closure from three strictly nonterminal stage-0/stage-2
convex rows instead of two. The new
`stage02_convex_pose_velocity_quadextrapolate_*` laws use Lagrange
extrapolation to weight zero, without terminal-row evaluation or projection.
The default two-h smoke over `0p01/0p02/0p05`, `0p005/0p01/0p02`, and
`0p002/0p005/0p01` runs in `57.0` seconds, keeps rank `132`, and gives
terminal velocities `2.029e-11`, `2.029e-12`, and `2.029e-13`; the velocity
orders stay at about `4.508`. The best row,
`stage02_convex_pose_velocity_quadextrapolate_0p002_0p005_0p01_z`, closes the
terminal velocity tolerance in a three-h smooth refinement, with max/finest
terminal velocities `2.029e-13`/`8.254e-15`, but its orders are only
`4.142/2.305`. Thus the next repair also cannot be a purely higher-order
nonterminal extrapolation of this synchronized pose/velocity family.

A projection-like terminal-tangent diagnostic was then added to test whether
the nonterminal row only lacked a terminal velocity tangent correction. These
laws are explicitly non-acceptance evidence because they use a terminal-pose
minimum-norm velocity correction and set `projection_used=true`. The full correction
`stage02_convex_pose_velocity_0p01_terminalproj_z` fails during the reference
run, with the residual diverging to `6.739e+08`. Damped variants converge but
move away from the target: `stage02_convex_pose_velocity_0p01_terminalproj_p0p1_z`
runs in `28.0` seconds with rank `132`, max terminal velocity `7.028e-06`,
and two-point orders `2.301/1.788`; `stage02_convex_pose_velocity_0p01_terminalproj_p0p5_z`
runs in `28.7` seconds with max terminal velocity `1.321e-05` and orders
`2.158/1.433`. This rules out a simple terminal-projection damping repair and
keeps the next target at a non-projection nonterminal endpoint-pose predictor.

A nonterminal Hermite endpoint pose/velocity predictor then tests whether the
missing row is the nonlinear kinematic endpoint extrapolation itself rather
than an extrapolation of already-evaluated constraint rows. The implementation
adds `nonfinal_hermite_endpoint_pose_velocity_01_z`,
`nonfinal_hermite_endpoint_pose_velocity_12_z`, and
`nonfinal_hermite_endpoint_pose_velocity_02_z`; each predicts endpoint
`(r,u,v,w)` from internal Gauss stage `(r,u,v,w,a,alpha)` data and evaluates
`C_v` at that predicted point, with no endpoint source, terminal row, or
projection. The local differential audit keeps rank `132` and runs in `24.1`
seconds, but the best row,
`nonfinal_hermite_endpoint_pose_velocity_02_z`, has projection residual
`0.072816`, independent target rank `8`, and
`any_nonterminal_candidate_spans_terminal_bridge=false`. The bounded nonlinear
h-sweep smoke for that best row runs in `20.9` seconds, converges all `3`
smooth steps with rank `132`, but leaves terminal velocity at `5.827e-06` and
only gives two-point position/velocity orders `2.693/2.004`. This excludes the
tested Hermite endpoint predictor as a full-TFE repair.

A recurrent-history terminal velocity source predictor then tests whether the
missing row can be supplied by using the previous accepted step's lower-pair
source estimate in the terminal velocity predictor. The implementation adds
`recurrent_history_velocity_terminal_source0linear_z`,
`recurrent_history_velocity_terminal_source0boundedlinear_z`,
`recurrent_history_velocity_terminal_source0curvature_z`,
`recurrent_history_velocity_terminal_source01historyblend_z`, and
`recurrent_history_velocity_terminal_source1linear_z`. These rows retain the
same 16 centered source-consistency rows and replace only the final 8 closure
rows; they use no endpoint source, terminal row, or projection. The local audit
runs in `31.4` seconds with rank `132`, but the best row,
`recurrent_history_velocity_terminal_source1linear_z`, has projection residual
`0.923100`, independent target rank `8`, and a stage-2
`translation_velocity_v` dominated missing direction at fraction `0.527377`.
The bounded nonlinear h-sweep smoke for the full five-law family runs in
`85.5` seconds, converges all `15` source-free smooth steps with rank `132`,
and reaches maximum residual `4.314e-12`, but writes no accepted artifact or
summary (`artifact_written=false`, `summary_updated=false`). The best terminal
closure is
`recurrent_history_velocity_terminal_source01historyblend_z`, with terminal
velocity `1.010e-07` and two-point position/velocity orders `6.596/4.805`.
The stage-0 source variants retain velocity order above `5` but leave terminal
velocity near `2.016e-07`; the local-audit best
`recurrent_history_velocity_terminal_source1linear_z` keeps orders
`6.505/5.042`, but terminal velocity remains `4.418e-07`. Therefore
`smooth_order_ok=false` and `terminal_velocity_closed=false`. This excludes the
tested one-step recurrent-history source predictors as a full-TFE repair and
shows that preserving order is not enough without the missing terminal-closure
coefficient-gradient row.

A recurrent-history Adams/source-slope extension then tests whether the
previous accepted source should enter as an AB-style source value rather than
only as a history-delta slope. The implementation adds
`recurrent_history_velocity_terminal_source0ab2_z`,
`recurrent_history_velocity_terminal_source0boundedab2_z`,
`recurrent_history_velocity_terminal_source0ab2curvature_z`,
`recurrent_history_velocity_terminal_source01historyslope_z`, and
`recurrent_history_velocity_terminal_source1ab2_z`. These rows keep the same
source-free lower-pair structure: 16 centered source-consistency rows plus 8
terminal velocity predictor rows, with no endpoint source, projection, or
terminal-row replacement. The bounded smooth h-sweep smoke runs in `83.2`
seconds, converges all `15` source-free steps with rank `132`, and reaches max
residual `4.189e-12`, but still writes no accepted artifact or summary. The
best terminal law is
`recurrent_history_velocity_terminal_source01historyslope_z`, with terminal
velocity `2.016e-07` and orders `6.566/5.264`; the `source0ab2*` laws preserve
orders around `6.561/5.319` but leave terminal velocity near `2.354e-07`, and
`source1ab2` worsens the terminal velocity to `5.104e-07`. Thus
`terminal_velocity_closed=false`; this rules out the tested AB-style
one-step recurrent history extension as the missing coefficient-gradient row.

A two-history recurrent source-state extension then tests whether the previous
two accepted lower-pair source estimates should enter as an AB3-style
shift-register state rather than a single one-step history:

```bash
V047_TARGET_AUDIT=lower_pair_endpoint_pose_velocity_predictor_h_sweep_smoke V047_ENDPOINT_POSE_VELOCITY_PREDICTOR_LAWS=recurrent_twohistory_velocity_terminal_source0ab3_z,recurrent_twohistory_velocity_terminal_source0ab3curvature_z,recurrent_twohistory_velocity_terminal_source0historycurvature_z,recurrent_twohistory_velocity_terminal_source01historyslopecurvature_z,recurrent_twohistory_velocity_terminal_source1ab3_z V047_ENDPOINT_POSE_VELOCITY_H_SWEEP_CASES=cylindrical_smooth V047_ENDPOINT_POSE_VELOCITY_H_SWEEP_T_FINAL=0.08 ../.venv_sbel/bin/python run_v047.py
```

The implementation stores two 8-entry source blocks with
`two_zero_initial_blocks_then_stage0_source_estimate_shift_register` for these
laws and leaves the older one-history weak/blend helpers at one 8-entry block.
The bounded smooth smoke runs in `176.1` seconds, converges all `30`
source-free steps with rank `132`, reaches max residual `4.213e-12`, and
writes no accepted artifact or summary. The best terminal laws,
`recurrent_twohistory_velocity_terminal_source0historycurvature_z` and
`recurrent_twohistory_velocity_terminal_source01historyslopecurvature_z`, leave
max terminal velocity at `9.319e-07` (`7.354e-07` on the `h=0.02` row) despite
two-point orders about `4.400/7.681`. The `source0ab3*` variants leave terminal
velocity at `1.453e-06`, and `source1ab3` worsens it to `2.042e-06`.
Therefore `terminal_velocity_closed=false`; the tested two-history AB3 and
curvature shift-register source laws are not the missing full-TFE row and are
worse on terminal closure than the one-step AB/source-slope best case.

A nonlinear recurrent feedback extension then tests whether the best
order-preserving recurrent source row can be blended with the terminal-closing
final-stage velocity row using only current residual magnitudes as the
coefficient feature. The implementation adds
`recurrent_history_velocity_terminal_feedbackcomp_source01historyslope_rel_p1_z`,
`recurrent_history_velocity_terminal_feedbackcomp_source01historyslope_rel_p5_z`,
`recurrent_history_velocity_terminal_feedbacknorm_source01historyslope_rel_p5_z`,
`recurrent_history_velocity_terminal_feedbacknorm_source01historyslope_rel_p20_z`,
and `recurrent_history_velocity_terminal_feedbackcomp_source0ab2_rel_p5_z`.
These rows use no endpoint-boundary source, projection, terminal-row
replacement, target Jacobian, or frozen fitted coefficient; the feedback
coefficient is a JAX expression of the current candidate and final-stage
velocity row norms, so its derivative enters Newton. Two bounded two-h smooth
screens over the five laws converge all `30` source-free steps with rank
`132`. The low-gain branch leaves terminal velocity open
(`6.437e-07` for componentwise gain `1`), medium gains improve the closure to
`8.876e-11` or `4.244e-08`, and the strongest tested norm-feedback law
`recurrent_history_velocity_terminal_feedbacknorm_source01historyslope_rel_p20_z`
closes terminal velocity to `3.287e-16` while keeping residuals below
`8.699e-12`. A smooth three-h refinement of that best law over
`h=[0.04,0.02,0.01]` against `reference_h=0.005` converges all `14` requested
source-free steps with rank `132`, max residual `7.601e-12`, and
`terminal_velocity_closed=true` with max terminal velocity `3.287e-16`.
It is still not accepted: position/velocity orders are only `3.523/4.828`,
`smooth_order_ok=false`, and no accepted artifact or summary is written. This
feedback family therefore reproduces the same terminal/order split as the
final-stage velocity closure rather than closing the full-TFE gate.

The componentwise recurrent feedback gain-boundary audit
`cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_component_feedback_gain_boundary_audit.{csv,json}`
then checks that the split is not only a norm-feedback artifact. It runs the
target-free law
`recurrent_history_velocity_terminal_feedbackcomp_source01historyslope_rel_p*_z`
over gains [1,2,5,8,10,12,15,20] on the smooth short prefilter with no
endpoint-boundary source, target Jacobian, target-direction oracle,
terminal-row replacement, or projection. The only high-order row is gain 1
with min order `5.214`, but terminal velocity remains `1.857e-07`. Gains 8,
10, 12, 15, and 20 close terminal velocity, with the best terminal row at
gain 12, terminal velocity `7.538e-17`, and min order `4.508`. Therefore
`order_terminal_intersection_present=false`,
`terminal_closure_requires_order_collapse=true`, and
`full_tfe_stage_replacement=false`; componentwise feedback tuning also falls
into the terminal/order split.

The h-scaled recurrent feedback gain-boundary audit
`cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_hscaled_feedback_gain_boundary_audit.{csv,json}`
then tests whether a step-size-dependent scalar feedback coefficient can avoid
the fixed-gain split. It runs the target-free law
`recurrent_history_velocity_terminal_feedbacknormhscaled_source01historyslope_rel_*_pow_*_z`
with effective gain `gain*(h/0.02)^power` over gains [2,5,8,12,20] and
h-powers [-2,-1,1,2], again with no endpoint-boundary source, target Jacobian,
target-direction oracle, terminal-row replacement, or projection. Seven of the
20 rows close terminal velocity; the best terminal row is gain 12, h-power 1,
terminal velocity `1.036e-16`, and min order `4.508`. No row reaches the
smooth-order floor. The best-order row is gain 2, h-power 2, min order
`4.711`, and terminal velocity `1.316e-08`. Therefore
`order_terminal_intersection_present=false`,
`terminal_closure_requires_order_collapse=true`, and
`full_tfe_stage_replacement=false`; simple h-dependent scalar feedback scaling
does not supply the independent lower-pair closure.

The recurrent source-law trajectory screen
`cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_source_law_trajectory_screen_audit.{csv,json}`
then removes feedback entirely and tests the target-free source/history laws
selected by `V047_RECURRENT_SOURCE_LAW_SCREEN_LAWS` (default six
one-history/two-history source and curvature rows). All six default rows
converge at rank `132` on the smooth short prefilter. They record
`terminal_closed_row_count=0`, `smooth_order_ok_count=5`, best terminal
velocity `2.016e-07`, best smooth min order `5.355`, and
`order_terminal_intersection_present=false`. Therefore the current
non-feedback recurrent history source laws preserve order but leave the
terminal endpoint velocity open; they do not supply the independent full-TFE
lower-pair closure.

The three-history recurrent source-law trajectory screen
`cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_three_history_source_law_trajectory_screen_audit.{csv,json}`
extends the same target-free source-law prefilter to four three-block
shift-register laws. It is run with
`V047_TARGET_AUDIT=lower_pair_recurrent_three_history_source_law_trajectory_screen`
and optionally narrowed by `V047_RECURRENT_THREE_HISTORY_SOURCE_LAW_SCREEN_LAWS`.
The implementation uses
`three_zero_initial_blocks_then_stage0_source_estimate_shift_register`, adds
`threehistory_source01historyslopejerk_terminal_raw`, and tests laws including
`recurrent_threehistory_velocity_terminal_source0ab4_z` and
`recurrent_threehistory_velocity_terminal_source01historyslopejerk_z`. All
four rows converge at rank `132` without endpoint-boundary source, target
Jacobian, target-direction oracle, terminal-row replacement, or projection. The
best law is
`recurrent_threehistory_velocity_terminal_source01historyslopejerk_z`, with
terminal velocity `2.923e-07` and min order `5.345`; the aggregate remains
`terminal_closed_row_count=0`, `smooth_order_ok_count=2`,
`order_terminal_intersection_present=false`, and
`full_tfe_stage_replacement=false`. Therefore the three-history recurrent source law
family is also negative evidence; the next repair still needs a revised
analytical weak-row formula or a richer nonlinear recurrent history source law
for the coefficient-gradient closure.

The four-history recurrent source-law trajectory screen
`cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_four_history_source_law_trajectory_screen_audit.{csv,json}`
extends the same target-free source-law prefilter to four four-block
shift-register laws. It is run with
`V047_TARGET_AUDIT=lower_pair_recurrent_four_history_source_law_trajectory_screen`
and optionally narrowed by `V047_RECURRENT_FOUR_HISTORY_SOURCE_LAW_SCREEN_LAWS`.
The implementation uses
`four_zero_initial_blocks_then_stage0_source_estimate_shift_register`, adds
`fourhistory_source01historyslopejerksnap_terminal_raw`, and tests laws
including `recurrent_fourhistory_velocity_terminal_source0ab5_z` and
`recurrent_fourhistory_velocity_terminal_source01historyslopejerksnap_z`. All
four rows converge at rank `132` without endpoint-boundary source, target
Jacobian, target-direction oracle, terminal-row replacement, or projection. The
best terminal law is
`recurrent_fourhistory_velocity_terminal_source01historyslopejerksnap_z`, with
terminal velocity `2.950e-07`; the best smooth-order law keeps min order
`5.342`. The aggregate remains `terminal_closed_row_count=0`,
`smooth_order_ok_count=2`,
`four_history_source_law_trajectory_screen_present=true`,
`order_terminal_intersection_present=false`, and
`full_tfe_stage_replacement=false`. Therefore AB5 and fourth-difference snap
source-law extrapolations are also negative evidence. The four-history recurrent source law family
does not supply the missing closure, so the next repair still needs a revised
analytical weak-row formula or a richer nonlinear recurrent history source law
than the tested AB/history-difference family.

The nonlinear-history recurrent source law trajectory screen
`cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_nonlinear_history_source_law_trajectory_screen_audit.{csv,json}`
then tests that richer source-law direction directly. It is run with
`V047_TARGET_AUDIT=lower_pair_recurrent_nonlinear_history_source_law_trajectory_screen`
and optionally narrowed by `V047_RECURRENT_NONLINEAR_HISTORY_SOURCE_LAW_SCREEN_LAWS`.
The implementation uses
`two_zero_initial_blocks_then_stage0_source_estimate_shift_register`, adds
`nonlinearhistory_terminal_raw`, and tests laws including
`recurrent_nonlinearhistory_velocity_terminal_source0normhistorydelta_z`,
`recurrent_nonlinearhistory_velocity_terminal_source0historyhadamard_z`, and
`recurrent_nonlinearhistory_velocity_terminal_source0normseconddiff_z`. All
five rows converge at rank `132` without endpoint-boundary source, target
Jacobian, target-direction oracle, terminal-row replacement, or projection. The
best law is
`recurrent_nonlinearhistory_velocity_terminal_source0historyhadamard_z`, with
terminal velocity `1.954e-07` and min order `3.525`; the aggregate remains
`terminal_closed_row_count=0`, `smooth_order_ok_count=0`,
`order_terminal_intersection_present=false`, and
`full_tfe_stage_replacement=false`. Therefore this nonlinear-history recurrent
source law family is also negative evidence; the remaining repair target must
derive a different analytical weak-row formula or a richer closure basis.

The source-law final-retain boundary audit
`cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_source_law_final_retain_boundary_audit.{csv,json}`
then tests the near transition between the source-history branch and the
final-stage velocity-row branch using
`V047_TARGET_AUDIT=lower_pair_recurrent_source_law_final_retain_boundary`.
It evaluates 16 target-free rows over retain values [1e-6,1e-5,1e-4,1e-3]
and h-powers [0,2], with no endpoint-boundary source, target Jacobian,
target-direction oracle, terminal-row replacement, or projection. All rows
converge at rank `132`; `terminal_closed_row_count=4`,
`smooth_order_ok_count=0`, best terminal velocity `3.171e-13`, best terminal
min order `4.508`, best smooth min order `4.510`, and
`order_terminal_intersection_present=false`. Therefore even the source-law
retention boundary closes terminal velocity only on an order-collapsed branch.

The current stage-2 differential artifacts keep that local tangent blocker
explicit. The scalar coefficient-gradient audit
`cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_stage2_gradient_differential_audit.{csv,json}`
tests `8` source/history-modulated rows, and the target-free matrix-gradient
audit
`cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_stage2_matrix_gradient_differential_audit.{csv,json}`
tests `32` row/column/bilinear matrix rows. Both keep rank `132`, both record
`span_row_count=0`, both leave independent target rank `8`, and their best
projection residuals remain about `0.899` with the missing direction localized
to stage-2 translational velocity. The translation-velocity matrix audit
`cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_stage2_translation_velocity_matrix_differential_audit.{csv,json}`
tests `40` target-free rows and improves the best projection residual to
`0.671049`, but still records `span_row_count=0`, independent target rank `8`,
and a dominant `angular_velocity_w` missing direction. The translation/angular
coupled matrix audit
`cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_stage2_translation_angular_coupled_matrix_differential_audit.{csv,json}`
tests `48` paired rowmask, pair-swap, and local-block rows; it records
`span_row_count=0`, best residual `0.742069`, independent target rank `8`, and
dominant `translation_velocity_v`, so it rules out that coupled local block
family without improving the full-TFE gap. The feature-dictionary span audit
`cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_stage2_feature_dictionary_span_audit.{csv,json}`
then records `feature_dictionary_row_count=12`, `span_row_count=8`,
`combined_all_dictionary_span_count=2`, and best dictionary
`stage2_matrix_core` with residual `1.084e-14`. This is positive target-free
local capacity evidence, but `target_jacobian_used_for_formula=false`,
`target_direction_oracle_used=false`, `formula_coefficient_law_present=false`,
`accepted_h_sweep_present=false`, and `full_tfe_stage_replacement=false`
remain explicit. The next missing object is a bounded target-free
coefficient/selection law over the spanning dictionary plus a nonlinear h-sweep.
The frozen coefficient-law screen
`cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_stage2_feature_coefficient_law_screen_audit.{csv,json}`
tests that next simplest object with `coefficient_law_row_count=60`, five
target-free bounded laws, and six dictionaries. It records `span_count=0`;
the best row is `combined_all_target_free_dictionary` with
`closure_delta_norm_weights` and residual `5.596e-01`. Because
`coefficient_derivative_included=false`,
`target_jacobian_used_for_formula=false`, `target_direction_oracle_used=false`,
`accepted_h_sweep_present=false`, and `full_tfe_stage_replacement=false`, the
remaining formula target is state-dependent bounded coefficients with
derivative terms over the spanning dictionary followed by a nonlinear h-sweep.
The state-feature coefficient-derivative screen
`cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_stage2_state_feature_coefficient_derivative_screen_audit.{csv,json}`
then differentiates that next simplest target-free coefficient family. It tests
`state_feature_coefficient_derivative_row_count=36` rows over three
differentiable coefficient laws and six dictionaries. It still records
`span_count=0`; the best row is `stage2_matrix_core` with
`inverse_closure_delta_norm_weights_derivative` and residual `5.908e-01`.
Because `coefficient_derivative_included=true`,
`target_jacobian_used_for_formula=false`, `target_direction_oracle_used=false`,
`accepted_h_sweep_present=false`, and `full_tfe_stage_replacement=false`,
direct closure-norm coefficient differentiation is excluded. The remaining
formula target is richer state-dependent coefficient features or a new weak-row
formula followed by a nonlinear h-sweep.
The endpoint-pose trajectory artifact
`cylindrical_chain_endpoint_tfe_paper_lower_pair_endpoint_pose_velocity_predictor_h_sweep_smoke.{csv,json}`
runs `stage02_convex_pose_velocity_0p00_z` on smooth
`h=[0.04,0.02,0.01]`, `reference_h=0.005`, `T=0.08`. It converges all `14`
source-free steps at rank `132` and closes terminal velocity to
`3.455e-16`, but gives only `3.523/4.828` position/velocity orders. Thus the
stage2 coefficient-gradient and endpoint-pose predictor branches are useful
diagnostics, not the accepted full-TFE stage replacement.

The endpoint-pose reference/output follow-up
`cylindrical_chain_endpoint_tfe_paper_lower_pair_endpoint_pose_velocity_predictor_reference_output_audit.{csv,json}`
records `10` rows across output-pose prefilters, three-h short order checks,
and a finer-reference check. It finds `terminal_closed_row_count=5` but
`smooth_order_ok_count=0`: `stage02_convex_pose_velocity_0p00_z` and
`paper_endpoint_pose_stage02_convex_0p00_z` are equivalent on the two-h
prefilter with `6.588/4.508` orders and terminal velocity at roundoff; Gauss
endpoint pose, paper-y velocity, and Lagrange velocity variants reopen terminal
velocity; the three-h short check is still only `4.142/2.305`; and
`reference_h=0.0025` gives `3.672/1.956` rather than rescuing the order. This
rules out output-node relabeling and reference-floor policy as the repair; the
next candidate must change the independent lower-pair closure formula.

The h-adaptive endpoint-pose velocity predictor audit
`cylindrical_chain_endpoint_tfe_paper_lower_pair_endpoint_pose_velocity_hscaled_predictor_h_sweep_audit.{csv,json}`
is run with:

```bash
V047_TARGET_AUDIT=lower_pair_endpoint_pose_velocity_hscaled_predictor_h_sweep_audit ../.venv_sbel/bin/python run_v047.py
```

The target `lower_pair_endpoint_pose_velocity_hscaled_predictor_h_sweep_audit`
uses `V047_ENDPOINT_POSE_HSCALED_VELOCITY_H_SWEEP_VALUES`,
`V047_ENDPOINT_POSE_HSCALED_VELOCITY_H_SWEEP_REFERENCE_H`,
`V047_ENDPOINT_POSE_HSCALED_VELOCITY_H_SWEEP_T_FINAL`,
`V047_ENDPOINT_POSE_HSCALED_VELOCITY_PREDICTOR_LAWS`, and
`V047_ENDPOINT_POSE_HSCALED_VELOCITY_H_SWEEP_CASES`, and writes
`endpoint_pose_velocity_hscaled_predictor_h_sweep_audit_present=true`. It
tests `12` smooth rows over four h-scaled endpoint-pose velocity predictor
laws without projection or terminal-row replacement. The best terminal-closing
law is
`stage02_convex_pose_velocity_extrapolate_0p00001_0p00002_hpow_m1_z`, which
reaches terminal velocity `5.004e-13` but only `3.523/4.828`
position/velocity order. Stronger negative powers reopen terminal velocity,
so the aggregate audit keeps `terminal_velocity_closed=false`,
`smooth_order_ok=false`, `accepted_h_sweep_present=false`, and
`full_tfe_stage_replacement=false`. This is useful negative evidence, not a
full-TFE replacement.

The h-adaptive endpoint-pose velocity response audit is run with:

```bash
V047_TARGET_AUDIT=lower_pair_endpoint_pose_velocity_hscaled_response_audit ../.venv_sbel/bin/python run_v047.py
```

The target `lower_pair_endpoint_pose_velocity_hscaled_response_audit` writes
`cylindrical_chain_endpoint_tfe_paper_lower_pair_endpoint_pose_velocity_hscaled_response_audit.{csv,json}`
and `endpoint_pose_velocity_hscaled_response_audit_present=true`. It records
one response row per h-scaled predictor law: `terminal_closed_row_count=1`,
`smooth_order_ok_count=0`, `accepted_candidate_count=0`, and
`order_terminal_intersection_present=false`. The only terminal-closing row is
`stage02_convex_pose_velocity_extrapolate_0p00001_0p00002_hpow_m1_z`, with
terminal velocity `5.004e-13`, minimum terminal-closed order `3.523`, and a
`1.477` gap to the order floor, so terminal closure still requires order
collapse.

The lower-pair candidate frontier audit is run with:

```bash
V047_TARGET_AUDIT=lower_pair_candidate_frontier_audit ../.venv_sbel/bin/python run_v047.py
```

The target `lower_pair_candidate_frontier_audit` writes
`cylindrical_chain_endpoint_tfe_paper_lower_pair_candidate_frontier_audit.{csv,json}`
and compares `11` source-present candidate families totaling `115` rows. It
records `total_candidate_row_count=115`, `terminal_closed_candidate_count=35`,
`smooth_order_candidate_count=17`, `order_terminal_intersection_count=0`, and
`family_intersection_count=0`. The best terminal-closing row reaches
`7.538e-17` terminal velocity with min order `4.508`, while the best-order row
has min order `5.355` with terminal velocity `2.771e-07`; no family or
candidate closes both gates. The repair target therefore remains a bounded
target-free stage-local weak-row tangent, not another scalar gain or output
node relabeling.

The accepted residual must keep the total v047 stage row budget at `132` rows.
The lower-pair replacement budget is `24` rows:

- The bounded tangent requirement audit is run with:

```bash
V047_TARGET_AUDIT=lower_pair_bounded_tangent_requirement_audit ../.venv_sbel/bin/python run_v047.py
```

The target `lower_pair_bounded_tangent_requirement_audit` writes
`cylindrical_chain_endpoint_tfe_paper_lower_pair_bounded_tangent_requirement_audit.{csv,json}`
and records `requirement_row_count=7`, `row_space_oracle_span_count=36`,
`target_free_formula_span_count=0`,
`row_space_target_free_span_count=0`,
`weak_row_structure_span_count=0`, and
`bounded_gradient_practical_cap_spanning_row_count=12`. This keeps the
coefficient-derivative row-space span as an oracle-only upper bound and makes
the next accepted formula target a bounded target-free stage-local weak-row
tangent with no target Jacobian/direction oracle.

- The recurrent stage2 feature-dictionary span audit is run with:

```bash
V047_TARGET_AUDIT=lower_pair_recurrent_stage2_feature_dictionary_span_audit ../.venv_sbel/bin/python run_v047.py
```

The target `lower_pair_recurrent_stage2_feature_dictionary_span_audit` writes
`cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_stage2_feature_dictionary_span_audit.{csv,json}`
and records `feature_dictionary_row_count=12`, `span_row_count=8`,
`combined_all_dictionary_span_count=2`, best dictionary `stage2_matrix_core`,
best residual `1.084e-14`, `target_jacobian_used_for_formula=false`,
`target_direction_oracle_used=false`, `formula_coefficient_law_present=false`,
and `full_tfe_stage_replacement=false`. It narrows the next accepted formula
target to a bounded target-free coefficient/selection law followed by a
nonlinear h-sweep.

- The recurrent stage2 frozen coefficient-law screen is run with:

```bash
V047_TARGET_AUDIT=lower_pair_recurrent_stage2_feature_coefficient_law_screen_audit ../.venv_sbel/bin/python run_v047.py
```

The target `lower_pair_recurrent_stage2_feature_coefficient_law_screen_audit`
writes
`cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_stage2_feature_coefficient_law_screen_audit.{csv,json}`
and records `coefficient_law_row_count=60`, `span_count=0`, best dictionary
`combined_all_target_free_dictionary`, best law `closure_delta_norm_weights`,
best residual `5.596e-01`, `coefficient_derivative_included=false`,
`target_jacobian_used_for_formula=false`, `target_direction_oracle_used=false`,
and `full_tfe_stage_replacement=false`. It narrows the next accepted formula
target to state-dependent bounded coefficients with derivative terms over the
spanning dictionary followed by a nonlinear h-sweep.

- The recurrent stage2 state-feature coefficient-derivative screen is run with:

```bash
V047_TARGET_AUDIT=lower_pair_recurrent_stage2_state_feature_coefficient_derivative_screen_audit ../.venv_sbel/bin/python run_v047.py
```

The target
`lower_pair_recurrent_stage2_state_feature_coefficient_derivative_screen_audit`
writes
`cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_stage2_state_feature_coefficient_derivative_screen_audit.{csv,json}`
and records `state_feature_coefficient_derivative_row_count=36`,
`span_count=0`, best dictionary `stage2_matrix_core`, best law
`inverse_closure_delta_norm_weights_derivative`, best residual `5.908e-01`,
`coefficient_derivative_included=true`, `target_jacobian_used_for_formula=false`,
`target_direction_oracle_used=false`, and `full_tfe_stage_replacement=false`.
It narrows the next accepted formula target to richer state-dependent
coefficient features or a new weak-row formula followed by a nonlinear h-sweep.

- `16` source-consistency rows from centered stage acceleration/source
  consistency;
- `8` new closure rows from the revised weak-row formula or nonlinear recurrent
  history source law.

## Required Inputs

The candidate may use stage-local paper TFE quantities already available in the
current residual:

- `x_q`, `y_q`, `z_q`;
- body position, quaternion, velocity, and angular velocity stage values;
- lower-pair velocity and acceleration row values;
- multiplier values required by the `newton_euler_weak_balance` family;
- previous accepted step state needed for a recurrent paper-TFE start/source
  policy.

The candidate must not use:

- endpoint-boundary source data;
- terminal-row replacement;
- output projection;
- the target terminal-bridge Jacobian as a formula input;
- a target-direction oracle;
- frozen state-dependent coefficients without their derivative contribution;
- a fit that exists only at the local tangent/capacity level.

## Formula Target

The current artifacts show that the all-stage velocity row space can span the
terminal-bridge tangent, but tested eight-row source-free compressions do not.
The row-space coefficient-derivative audit
`cylindrical_chain_endpoint_tfe_paper_lower_pair_velocity_compression_row_space_coefficient_derivative_audit.{csv,json}`
shows that adding the local target-perp-minus-closure-perp derivative oracle
spans all `36` local tangents and gives value-balanced spans 24/36, with best
residual `8.915e-16`; however it uses a target-direction oracle and reaches a
maximum required coefficient-gradient norm of `6.777e+18`. The next formula
must therefore supply the missing bounded target-free coefficient-gradient
closure inside the nonlinear residual, not just replay the oracle.

The closure should be tested as a nonlinear residual, not only as a local span:

```text
centered_source_consistency_rows(x, z0, history) = 0
recurrent_weak_closure_rows(x, z0, history) = 0
```

The eight closure rows must be independent of terminal-boundary rows and must
carry the derivative of any state-dependent coefficients used to compress the
all-stage lower-pair velocity row space.

## Acceptance Evidence

The candidate can change `full_tfe_stage_replacement` only if all items below
are true and recorded in CSV, PNG, report, and summary artifacts:

- smooth and sharp h-sweeps over `h=[0.04,0.02,0.01]` with reference
  `h=0.005`;
- terminal endpoint velocity closed to the accepted tolerance, currently
  checked at the `1e-12` scale;
- smooth trajectory order at least `5.0` for the paper-TFE replacement path;
- no endpoint source, no terminal-row replacement, and no projection;
- full Newton rank `132`;
- residual norm below `1e-10`;
- accepted h-sweep count greater than `0`;
- a paper-derived recurrent history/source initialization policy, or a clear
  proof that the diagnostic bootstrap does not affect the accepted order claim;
- four-ASME method gate still accepted under
  `four_asme_method_rows_accepted_projection_sharp_sparse_caveats`;
- paper claim ledger and full-TFE gap ledger updated to replace the current
  open status.

## Rejection Evidence To Preserve

If the candidate fails, it should be recorded as a diagnostic with a new
artifact family and should keep `full_tfe_stage_replacement=false`. Do not
overwrite these existing negative controls:

- `source_free_final_stage_velocity_closure`: terminal-closed but
  smooth-order limited;
- `source_free_order_closure_blend`: no order/closure intersection;
- `velocity_compression_row_space_coefficient_derivative`: local tangent span
  only through a target-direction coefficient-gradient oracle; value-balanced
  spans `24/36`, no bounded target-free formula, no h-sweep;
- `lower_pair_source_free_near_final_beta_boundary`: the targeted
  `run_endpoint_tfe_paper_lower_pair_source_free_near_final_beta_boundary_audit`
  writes
  `cylindrical_chain_endpoint_tfe_paper_lower_pair_source_free_near_final_beta_boundary_audit.{csv,json}`;
  beta=`0.99999999` reaches only `1.255e-12` terminal velocity with min order
  `4.508`, beta=0.9/0.99 give the only high-order rows, and
  `near_final_collapse_confirmed=true`, so scalar beta tuning is not the
  independent lower-pair closure repair;
- `lower_pair_recurrent_feedback_gain_boundary`: the targeted
  `run_endpoint_tfe_paper_lower_pair_recurrent_feedback_gain_boundary_audit`
  writes
  `cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_feedback_gain_boundary_audit.{csv,json}`;
  the target-free norm-feedback law closes terminal velocity for gains
  8, 10, 12, 15, and 20, with `feedback_gain=12` reaching `1.036e-16`, but
  every terminal-closed gain has min order about `4.508`; gain 1 is the only
  high-order row and leaves terminal velocity `1.868e-07`, so
  `terminal_closure_requires_order_collapse=true`;
- `lower_pair_recurrent_stage2_gradient_differential_audit`: the targeted
  `run_endpoint_tfe_paper_lower_pair_recurrent_stage2_gradient_differential_audit`
  writes
  `cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_stage2_gradient_differential_audit.{csv,json}`;
  it covers 8 scalar source/history coefficient-gradient rows, records
  `span_row_count=0`, best residual about `0.899`, and keeps the missing
  terminal-bridge direction stage-2-local;
- `lower_pair_recurrent_stage2_matrix_gradient_differential_audit`: the
  targeted
  `run_endpoint_tfe_paper_lower_pair_recurrent_stage2_matrix_gradient_differential_audit`
  writes
  `cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_stage2_matrix_gradient_differential_audit.{csv,json}`;
  it covers 32 target-free row/column/bilinear matrix rows, records
  `span_row_count=0`, best law `diagonal_plus_row_broadcast_feature`, best
  residual about `0.898873`, and keeps the same stage-2-local missing
  direction;
- `lower_pair_recurrent_stage2_translation_velocity_matrix_differential_audit`:
  the targeted
  `run_endpoint_tfe_paper_lower_pair_recurrent_stage2_translation_velocity_matrix_differential_audit`
  writes
  `cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_stage2_translation_velocity_matrix_differential_audit.{csv,json}`;
  it covers 40 target-free translation-velocity matrix rows, records
  `span_row_count=0`, best law
  `stage2_translation_velocity_symmetric_broadcast_feature`, best residual
  about `0.671049`, and leaves a stage-2-dominant `angular_velocity_w`
  missing direction;
- `lower_pair_recurrent_stage2_translation_angular_coupled_matrix_differential_audit`:
  the targeted
  `run_endpoint_tfe_paper_lower_pair_recurrent_stage2_translation_angular_coupled_matrix_differential_audit`
  writes
  `cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_stage2_translation_angular_coupled_matrix_differential_audit.{csv,json}`;
  it covers 48 target-free paired rowmask, pair-swap, and local-block matrix
  rows, records `span_row_count=0`, best law
  `stage2_velocity_bidirectional_rowmask_translation_angular_feature`, best
  residual about `0.742069`, and leaves a stage-2-dominant
  `translation_velocity_v` missing direction;
- `lower_pair_recurrent_stage2_feature_dictionary_span_audit`: the targeted
  `run_endpoint_tfe_paper_lower_pair_recurrent_stage2_feature_dictionary_span_audit`
  writes
  `cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_stage2_feature_dictionary_span_audit.{csv,json}`;
  it covers 12 target-free dictionary rows, records `span_row_count=8`,
  `combined_all_dictionary_span_count=2`, best dictionary
  `stage2_matrix_core`, best residual about `1.084e-14`, and still keeps
  `formula_coefficient_law_present=false` with no accepted nonlinear h-sweep;
- `lower_pair_recurrent_stage2_feature_coefficient_law_screen_audit`: the
  targeted
  `run_endpoint_tfe_paper_lower_pair_recurrent_stage2_feature_coefficient_law_screen_audit`
  writes
  `cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_stage2_feature_coefficient_law_screen_audit.{csv,json}`;
  it covers 60 frozen coefficient-law rows, records `span_count=0`, best
  dictionary `combined_all_target_free_dictionary`, best law
  `closure_delta_norm_weights`, best residual about `5.596e-01`, and still
  keeps `coefficient_derivative_included=false`,
  `target_jacobian_used_for_formula=false`, and no accepted nonlinear h-sweep;
- `lower_pair_recurrent_stage2_state_feature_coefficient_derivative_screen_audit`:
  the targeted
  `run_endpoint_tfe_paper_lower_pair_recurrent_stage2_state_feature_coefficient_derivative_screen_audit`
  writes
  `cylindrical_chain_endpoint_tfe_paper_lower_pair_recurrent_stage2_state_feature_coefficient_derivative_screen_audit.{csv,json}`;
  it covers 36 target-free coefficient-derivative rows, records
  `span_count=0`, best dictionary `stage2_matrix_core`, best law
  `inverse_closure_delta_norm_weights_derivative`, best residual about
  `5.908e-01`, and still keeps `coefficient_derivative_included=true`,
  `target_jacobian_used_for_formula=false`, `target_direction_oracle_used=false`,
  and no accepted nonlinear h-sweep;
- `velocity_compression_*`: local/capacity probes that do not give an accepted
  nonlinear replacement;
- `FULL_TFE_REPLACEMENT_GAP_LEDGER.md`: current claim boundary guard.

## Minimal Read-Only Guard

Run:

```bash
../.venv_sbel/bin/python validate_full_tfe_repair_spec.py
```

This guard checks that the implementation target stays synchronized with the
current summary and with the full-TFE gap ledger. It does not run simulations
and does not invoke `run_v047.py`.
