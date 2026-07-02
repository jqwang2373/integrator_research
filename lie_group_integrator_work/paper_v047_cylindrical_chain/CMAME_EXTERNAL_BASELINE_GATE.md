# CMAME External Baseline Gate

Status: **OPEN - NOT SUBMISSION READY**

This gate records the external same-test comparison boundary for the CMAME
manuscript. It is intentionally read-only. It does not invoke `run_v047.py`,
any v048 runner, or a default `1e-4` campaign.

## Execution Policy

- Default policy: `coarse_first_no_default_1e-4`.
- Coarse step sizes: `0.1`, `0.05`, `0.025`.
- Coarse reference step: `0.0125`.
- Strict public-policy `1e-4` rows: `opt_in_only`.
- `default_1e-4_required=false`.
- `heavy_numerical_run_invoked_by_gate=false`.

## Objective Blocker Matrix

The global objective blocker matrix remains:

- `blocker_open_by_id=OC4:True,OC6:True,OC12:True`
- `blocker_closure_decision_by_id=OC4:remain_open_ready_for_authorized_execution_not_executed_not_promoted,OC6:remain_open_no_positive_source_equivalent_artifact,OC12:remain_partial_narrowed_replay_ready_full_source_policy_archive_not_ready`
- `blocker_closure_allowed_by_id=OC4:False,OC6:False,OC12:False`

This matrix is inherited from `OBJECTIVE_COMPLETION_AUDIT.json`; it keeps
OC4, OC6, and OC12 open and does not authorize B4/source-policy execution.

## Current Acceptance Boundary

- `same_test_campaign_status=not_run`
- `external_superiority_claim=false`
- `full_external_same_test_campaign_passed=false`
- all-example common-reference comparison matrix closed: `true`
- common-reference examples checked: `single_pendulum`, `double_pendulum`,
  `four_link`, `slider_crank`
- common-reference cells checked: `44`
- raw rows recomputed for common-reference audit: `132`
- common-reference summary mismatches: `0`
- direct nonlocal velocity-order wins: `40/40`
- direct nonlocal finest-velocity-error wins: `40/40`
- original-paper velocity-error wins: `16/16`
- Kissel/Negrut-family velocity-error wins: `24/24`
- source-policy flagged rows: `15`
- source-policy flagged raw rows checked by all-example audit: `45`
- source-policy flagged examples checked: `single_pendulum`, `double_pendulum`,
  `four_link`, `slider_crank`
- source-policy velocity-mismatch rows: `10`
- source-policy superiority claim allowed: `false`
- B2/B4 can close from common-reference evidence alone: `false`
- coarse same-window order/time examples: `single_pendulum`, `double_pendulum`
- closed-loop coarse-window trajectory diagnostic examples: `four_link`, `slider_crank`
- public work/precision available examples: `four_link`, `slider_crank`
- public work/precision missing examples: none
- strict common-reference available examples: `four_link`, `slider_crank`
- strict common-reference gap examples: none
- strict common-reference figure available: `true`
- strict common-reference figure integrated in manuscript: `true`
- surrogate-only closed-loop examples: none
- accepted external dynamic-order examples: none
- closed-loop residual-to-error theorem accepted: `false`

The current v048 artifacts are useful but not enough for an external
source-policy superiority claim. `single_pendulum` and `double_pendulum` have coarse-first
same-window order/time evidence. `four_link` and `slider_crank` now have
closed-loop coarse-window trajectory diagnostic rows and same-window public
work/precision rows. They also now have strict common-reference error columns
against the v047 exact endpoint at the coarse window. The strict
common-reference figure is integrated into the manuscript, but no external
source-policy superiority claim is allowed until the remaining external suites
are closed or explicitly demoted.

`COMPARISON_OBJECTIVE_CLOSURE_RECONCILIATION_AUDIT.md/json` records the
all-example apples-to-apples result: the finite-grid common-reference
order/error matrix is closed for `single_pendulum`, `double_pendulum`,
`four_link`, and `slider_crank`. The audit recomputes all 44 summary cells from
132 raw rows with zero mismatches. Under this common-reference policy, the
bounded diagnostic records 40/40 positive direct nonlocal velocity-order
comparisons and 40/40 positive direct nonlocal finest-velocity-error
comparisons. This closes the
common-reference comparison objective; it does not close source-paper
default-policy reproduction.

`ALL_EXAMPLES_SOURCE_POLICY_AUDIT.md/json` checks every flagged source-policy
row across all four examples. It covers `15` flagged summary rows and `45` raw
coarse rows at `h=[0.1,0.05,0.025]`; it confirms the common-reference replay
uses fixed endpoint grids and `body.r/body.dr/body.ddr` output sources where
applicable. The audit keeps all suite-level source-policy reproduction rows
open and therefore keeps B2/B4 open.

`CROSS_PAPER_BENCHMARK_CASES.json` now separates full source-policy case
status from `partial_evidence_overlay`: the full external campaign remains
`not_run`, existing coarse-first and bounded rows are recorded as partial
evidence, and no row inventory field requires a default `1e-4` campaign.

`EXTERNAL_SAME_TEST_ACCEPTANCE_SHEET.md/json` now records the acceptance
requirements for B2/B4 without launching any numerical campaign: order, time,
work/precision, Newton iterations, constraint drift, reference policy, and
same-test setup identity are required before an external comparison row can be
promoted. It keeps `accepted_external_dynamic_order_examples=0`,
`local_evidence_coverage_examples=4/4`,
`accepted_method_dynamic_order_examples=2/4`,
`mechanism_coverage_examples=2/4`,
`accepted_source_policy_dynamic_order_examples=0/4`,
`parallel_shard_count_without_default_1e-4=20`, and
`default_1e-4_required=false`.

`HI2022_POLICY_DECISION_AUDIT.md/json` classifies the existing Fang--Kissel--
Zhang--Negrut half-implicit rows. The current HI2022 evidence has `24/24`
bounded rows and `8/8` model/form groups at `T=0.1` and
`h=[0.005,0.01,0.02]`; it is accepted only as bounded evidence. The full
`T=8` source policy remains open, source-policy dynamic-order examples remain
`0/4`, and the required decision is
`choose_full_T8_reproduction_or_explicit_demotion`.

`SOURCE_POLICY_CLOSURE_TRIAGE.md/json` turns the 15 flagged source-policy rows
into an execution-facing closure list without running new trajectories. The
triage covers all four examples and separates the next actions into 5 RA2021
public velocity-mapping/time-grid/norm rows, 4 original-TFE source-pendulum
encoding rows, 3 HI2022 full-`T=8` policy rows, and 3 VP code-path-demotion
rows. It keeps `b2_b4_can_close_now=false/false` and
`heavy_numerical_run_invoked=false`.

## Suite Status

| Suite | Current status | Claim allowed now |
| --- | --- | --- |
| Original Chaturvedi--Sandu--Sandu TFE pendulum | `open_not_encoded` | Specification extracted only. |
| 2021 Kissel/Taves/Negrut `rA/rp/reps` suite | `partial_coarse_first_and_public_baseline_evidence` | Public baseline, coarse local evidence, local closed-loop coarse-window trajectory diagnostics, public work/precision rows, and strict common-reference coarse-window columns/figure only; no external superiority until remaining external-suite decisions close. |
| 2022 Fang/Kissel/Zhang/Negrut half-implicit suite | `bounded_pilot_not_full_T8_policy` | Bounded pilot only; full `T=8` policy remains open. |
| 2024 Kissel/Bakke/Negrut velocity-partitioning suite | `code_path_unresolved`; the coordinate-partitioning proxy is identified through the implemented `rA` wrapper; a distinct public VP code path remains unresolved and demoted | Common-reference proxy evidence only; source-policy VP superiority remains disallowed. |

## Closure Rule

This gate closes only when the package has enough evidence for a fair
same-test comparison:

1. original TFE pendulum no-friction and friction rows are run or explicitly
   demoted from the claim;
2. the remaining same-test source suites are completed or explicitly demoted
   from the external-superiority claim;
3. the 2022 half-implicit full public policy is completed or explicitly
   demoted;
4. the 2024 velocity-partitioning code path is resolved or explicitly demoted;
5. work/precision and comparison figures are publication-grade;
6. no residual-only row is promoted to a dynamic-order claim.

## Next Parallel Batch

The next numerical batch should not be another full harness run or a default
`1e-4` run. It should be a targeted remaining external-suite closure or
claim-demotion pass now that the two closed-loop examples have local order,
public work/precision rows, strict common-reference columns, and an integrated
manuscript figure:

- target: `close_remaining_external_suites_or_demote_external_superiority_claim`;
- policy: `coarse_first_no_default_1e-4`;
- models: `four_link`, `slider_crank`;
- local method: `Gauss6/FullVA`;
- public baselines: `rA`, `rp`, `reps`;
- step sizes: `0.1`, `0.05`, `0.025`;
- reference step: `0.0125`;
- metrics: position, velocity, acceleration, observed order, runtime, Newton
  iterations, and constraint drift.

The closed-loop coarse-window trajectory diagnostic shard and public comparator
work/precision rows now exist, and the strict common-reference rows now put both
sides on the v047 exact endpoint reference. The remaining external-baseline work
is explicit closure/demotion of the other source suites and final review. Split
independent review or figure tasks by model, public form, and step where useful.
Do not run
`v047_cylindrical_chain_pipeline/run_v047.py`, do not run strict public
`1e-4` rows without explicit opt-in, and do not count residual-only
surrogates as dynamic order.

The plan-only row contract is now explicit:

- artifact: `v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_local_row_plan.json`;
- status: `plan_only_not_run`;
- rows: `24` total, with `6` local `Gauss6/FullVA` closed-loop diagnostic target rows
  and `18` public `rA/rp/reps` comparator rows;
- execution: `not_run`;
- `strict_public_policy_1e-4_required=false`;
- `heavy_numerical_run_invoked=false`.

The cross-suite execution queue is now explicit:

- artifact: `EXTERNAL_SAME_TEST_RUN_QUEUE.md/json`;
- status: `coarse_first_parallel_queue_ready_not_run`;
- required case count from `CROSS_PAPER_BENCHMARK_CASES.json`: `17`;
- parallel-ready coarse-first batches: `2`;
- parallel shards without default `1e-4`: `20`;
- `ra2021_coarse_same_window_order_time` has `12` independent
  model/form shards over `h=[0.1,0.05,0.025]`;
- `hi2022_halfimplicit_full_policy_decision` has `6` independent model/form
  shards after the full `T=8` policy decision;
- `tfe2026_original_pendulum_encoding` remains not ready until the source
  pendulum setup, error norm, friction law, and output policy are encoded;
- `vp2024_velocity_partitioning_code_resolution` remains not ready until the
  public code path is resolved or the suite is demoted;
- `default_1e-4_required=false`;
- `run_v047_invoked=false`;
- `v048_runner_invoked=false`;
- `external_superiority_claim=false`.

The external same-test acceptance sheet is now explicit:

- artifact: `EXTERNAL_SAME_TEST_ACCEPTANCE_SHEET.md/json`;
- status: `acceptance_requirements_defined_campaign_not_run`;
- accepted external dynamic-order examples: `0`;
- required metric columns: position error, velocity error, observed order,
  runtime, work/precision, Newton iterations, constraint drift, reference
  policy, and same-test setup identity;
- B2/B4 closure does not require a default `1e-4` campaign;
- `default_1e-4_required=false`;
- `run_v047_invoked=false`;
- `v048_runner_invoked=false`;
- `external_superiority_claim=false`.

The setup-level dynamic interface audit is also explicit:

- artifact: `v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_interface_audit.json`;
- status: `setup_level_interface_verified_no_trajectory_run`;
- dynamic setup: `2/2` closed-loop models instantiate and initialize through
  the public/v046 `rA` dynamics interface;
- local `Gauss6/FullVA` dynamic runner exists: `false`;
- `do_step_called=false`;
- `accepted_dynamic_order_count=0`.

The closed-loop residual scaffold is explicit as a code contract, not as a
trajectory result:

- artifact: `v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_residual_scaffold.json`;
- status: `residual_layout_specified_runner_not_implemented`;
- stage unknown dimension: `72`;
- total Newton dimension: `216`;
- square total system: `true`;
- local runner implemented: `false`;
- `default_1e-4_required=false`;
- `heavy_numerical_run_invoked=false`;
- `accepted_dynamic_order_count=0`.

The stage residual evaluator audit now verifies the first executable piece of
that contract:

- artifact: `v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_stage_residual_audit.json`;
- status: `stage_residual_evaluator_verified_stepper_not_implemented`;
- rows: `6/6` ok across the three Gauss6 stages for `four_link` and
  `slider_crank`;
- max stage residual infinity norm: `5.5067062021407764e-14`;
- stage residual evaluator implemented: `true`;
- trajectory stepper implemented: `false`;
- `default_1e-4_required=false`;
- `heavy_numerical_run_invoked=false`;
- `accepted_dynamic_order_count=0`.

The one-step smoke now exercises endpoint advancement once, but still not a
convergence/order campaign:

- artifact: `v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_one_step_smoke.json`;
- status: `one_step_smoke_passed_order_rows_not_run`;
- rows: `2/2` ok for `four_link` and `slider_crank`;
- step size: `0.1`;
- max stage residual infinity norm: `1.545430450278218e-13`;
- max endpoint position error: `4.4112151542652356e-08`;
- trajectory stepper executed: `true`;
- convergence sweep run: `false`;
- simulate runner implemented: `false`;
- `default_1e-4_required=false`;
- `heavy_numerical_run_invoked=false`;
- `accepted_dynamic_order_count=0`.

The non-oracle Newton stage smoke removes the stage-time kinematic oracle from
the previous one-step path, but still remains a smoke artifact:

- artifact: `v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_newton_stage_smoke.json`;
- status: `non_oracle_stage_newton_smoke_passed_order_rows_not_run`;
- rows: `2/2` ok for `four_link` and `slider_crank`;
- step size: `0.1`;
- stage predictor policy: `start_extrapolated_no_stage_oracle`;
- stage oracle used: `false`;
- max initial stage residual infinity norm: `4.306132591631753e+01`;
- max final stage residual infinity norm: `1.7900264603909477e-13`;
- trajectory stepper executed: `true`;
- convergence sweep run: `false`;
- `default_1e-4_required=false`;
- `heavy_numerical_run_invoked=false`;
- `accepted_dynamic_order_count=0`.

The non-oracle Newton coarse-order sweep is a closed-loop
coarse-window trajectory diagnostic artifact for the two previously missing examples:

- artifact: `v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_newton_coarse_order.json`;
- status: `coarse_true_dynamic_order_candidates_available_not_external_superiority`;
- rows: `6/6` ok for `four_link` and `slider_crank`;
- step sizes: `0.1`, `0.05`, `0.025`;
- reference step: `0.0125`;
- stage predictor policy: `start_extrapolated_no_stage_oracle`;
- stage oracle used: `false`;
- convergence sweep run: `true`;
- closed-loop coarse-window trajectory diagnostic examples: `2`;
- primary-state orders for `four_link`: `5.955/5.955/6.085/5.971`;
- primary-state orders for `slider_crank`: `6.164/6.159/7.341/6.426`;
- public work/precision available examples: `four_link`, `slider_crank`;
- public work/precision missing examples: none;
- strict common-reference available examples: `four_link`, `slider_crank`;
- strict common-reference gap examples: none;
- `default_1e-4_required=false`;
- `heavy_numerical_run_invoked=false`;
- `external_superiority_claim=false`.

The strict common-reference public work/precision artifact is now available, but
it still does not authorize an external superiority claim:

- artifact: `v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_strict_common_reference.json`;
- status: `strict_common_reference_error_columns_available_not_external_superiority`;
- rows: `24/24` ok, with `18` public rows and `6` local rows;
- common reference method: `v047_exact_kinematic_endpoint`;
- common reference step: `0.0125`;
- strict common-reference available examples: `four_link`, `slider_crank`;
- strict common-reference gap examples: none;
- strict common-reference error columns: `true`;
- figure: `v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_strict_common_reference_work_precision.png`;
- manuscript figure: `figures/strict_common_reference_work_precision.png`;
- `default_1e-4_required=false`;
- `heavy_numerical_run_invoked=false`;
- `external_superiority_claim=false`.

The same-window public work/precision artifact is now available, but it is
not an external superiority claim:

- artifact: `v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_public_work_precision.json`;
- status: `same_window_public_work_precision_available_reference_caveat_not_external_superiority`;
- rows: `24/24` ok, with `18` public rows and `6` local rows;
- summary rows: `8`;
- public work/precision available examples: `four_link`, `slider_crank`;
- public work/precision missing examples: none;
- strict common-reference error columns: `false`;
- `default_1e-4_required=false`;
- `heavy_numerical_run_invoked=false`;
- `external_superiority_claim=false`.

## Validator

Run:

```bash
../.venv_sbel/bin/python validate_cmame_external_baseline_gate.py
../.venv_sbel/bin/python validate_external_same_test_run_queue.py
../.venv_sbel/bin/python ../v048_cross_paper_same_test_benchmarks/validate_closed_loop_true_dynamic_local_row_plan.py
../.venv_sbel/bin/python ../v048_cross_paper_same_test_benchmarks/validate_closed_loop_true_dynamic_interface_audit.py
../.venv_sbel/bin/python ../v048_cross_paper_same_test_benchmarks/validate_closed_loop_true_dynamic_residual_scaffold.py
../.venv_sbel/bin/python ../v048_cross_paper_same_test_benchmarks/validate_closed_loop_true_dynamic_stage_residual_audit.py
../.venv_sbel/bin/python ../v048_cross_paper_same_test_benchmarks/validate_closed_loop_true_dynamic_one_step_smoke.py
../.venv_sbel/bin/python ../v048_cross_paper_same_test_benchmarks/validate_closed_loop_true_dynamic_newton_stage_smoke.py
../.venv_sbel/bin/python ../v048_cross_paper_same_test_benchmarks/validate_closed_loop_true_dynamic_newton_coarse_order.py
../.venv_sbel/bin/python ../v048_cross_paper_same_test_benchmarks/validate_closed_loop_true_dynamic_public_work_precision.py
../.venv_sbel/bin/python ../v048_cross_paper_same_test_benchmarks/validate_closed_loop_true_dynamic_strict_common_reference.py
```

Expected markers:

- `cmame_external_baseline_gate=PASS`
- `same_test_campaign_status=not_run`
- `external_superiority_claim=False`
- `default_1e-4=False`
- `external_same_test_run_queue=PASS`
- `true_dynamic_row_plan=plan_only_not_run`
- `true_dynamic_interface_audit=setup_level_interface_verified_no_trajectory_run`
- `true_dynamic_residual_scaffold=residual_layout_specified_runner_not_implemented`
- `true_dynamic_stage_residual_audit=stage_residual_evaluator_verified_stepper_not_implemented`
- `true_dynamic_one_step_smoke=one_step_smoke_passed_order_rows_not_run`
- `true_dynamic_newton_stage_smoke=non_oracle_stage_newton_smoke_passed_order_rows_not_run`
- `true_dynamic_newton_coarse_order=coarse_true_dynamic_order_candidates_available_not_external_superiority`
- `true_dynamic_public_work_precision=same_window_public_work_precision_available_reference_caveat_not_external_superiority`
- `true_dynamic_strict_common_reference=strict_common_reference_error_columns_available_not_external_superiority`
- `coarse_first_order_time_examples=single_pendulum,double_pendulum`
- `local_true_dynamic_order_examples=four_link,slider_crank` (schema field; reader-facing role is closed-loop coarse-window trajectory diagnostics)
- `public_work_precision_available_examples=four_link,slider_crank`
- `public_work_precision_missing_examples=none`
- `strict_common_reference_available_examples=four_link,slider_crank`
- `strict_common_reference_gap_examples=none`
- `strict_common_reference_figure_available=True`
- `strict_common_reference_figure_integrated_in_manuscript=True`
- `surrogate_only_examples=none`
- `accepted_external_dynamic_order_examples=none`
- `submission_ready=False`
