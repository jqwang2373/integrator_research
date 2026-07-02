# v048 Cross-Paper Same-Test Benchmark Harness

This version turns the cross-paper benchmark specification into an executable
experiment layer. It does not introduce a new integrator and it does not claim
that the external same-test campaign has passed.

The default run performs a short dependency/smoke check on the local 2021
SBEL `rA` single-pendulum path and writes the full external run plan. The
expensive public-code policy is opt-in:

```bash
../.venv_sbel/bin/python run_v048.py
../.venv_sbel/bin/python validate_v048_outputs.py
```

Current working policy is coarse-first: do not launch `h=1e-4` rows unless the
task explicitly asks for strict source-paper policy reproduction. For order
debugging and paper-table development, prefer three-step coarse sweeps such as
`h=[0.1,0.05,0.025]` or the selected `h=[0.02,0.01,0.005]` rows below.

To rebuild the TFE source-pendulum same-test candidate work/precision
artifact, run:

```bash
../.venv_sbel/bin/python build_tfe_source_pendulum_same_test_work_precision.py
../.venv_sbel/bin/python validate_tfe_source_pendulum_same_test_work_precision.py
```

This writes
`results/tfe_source_pendulum_same_test_work_precision_rows.csv`,
`results/tfe_source_pendulum_same_test_work_precision_summary.csv`,
`results/tfe_source_pendulum_same_test_work_precision.json`,
`results/tfe_source_pendulum_same_test_work_precision.md`, and
`results/tfe_source_pendulum_same_test_work_precision.png`. The rows compare
Newmark-beta, trapezoidal, TFE `m=1/2/3`, and the planar `Gauss6/FullVA`
candidate on the same frictionless source-pendulum `T=1`,
`h=[0.1,0.05,0.025]`, `h_ref=2.5e-4` grid. This is a candidate diagnostic,
not an original-source-policy reproduction or external-superiority claim.

To run the strict 2021 `rA/rp/reps` source-policy order rows, use this opt-in
command only when the exact public `h=1e-4` policy is required:

```bash
../.venv_sbel/bin/python run_v048.py --full-ra2021-order --allow-source-policy-1e-4
```

To run a bounded 2021 public-code target before launching any source-policy
campaign, select forms, models, step sizes, and horizon explicitly:

```bash
../.venv_sbel/bin/python run_v048.py \
  --ra2021-forms rA \
  --ra2021-models single_pendulum \
  --ra2021-step-sizes 0.1,0.05,0.025 \
  --ra2021-t-end 0.3 \
  --ra2021-reference-h 1e-3
```

Use `--ra2021-plan-only` with the same arguments to write planned rows and the
workload estimate without executing public code.

To add the first bounded `Gauss6/FullVA` same-mechanism pilot for the 2021
single-pendulum setup, run:

```bash
../.venv_sbel/bin/python run_v048.py \
  --ra2021-forms rA \
  --ra2021-models single_pendulum \
  --ra2021-step-sizes 0.1,0.05,0.025 \
  --ra2021-t-end 3 \
  --ra2021-reference-h 0.0125 \
  --gauss6-fullva-single \
  --gauss6-step-sizes 0.2,0.1,0.05 \
  --gauss6-t-end 0.2
```

This writes `gauss6_fullva_external_rows.csv`. It is a selected pilot, not the
full public-code time-window campaign.

To append a `Gauss6/FullVA` single-pendulum tranche on the actual 2021 public
time horizon without rerunning the public baseline, use:

```bash
../.venv_sbel/bin/python run_v048.py \
  --reuse-existing-results \
  --gauss6-public-single \
  --gauss6-public-step-sizes 1e-2,1e-3,1e-4 \
  --gauss6-public-t-end 3 \
  --gauss6-public-reference-h 1e-3 \
  --allow-source-policy-1e-4
```

This writes `gauss6_fullva_public_horizon_single_rows.csv`. The current table
has the exact public time window and all three public single-pendulum step
sizes; the finest position/orientation errors sit near roundoff, so the
reported final-error orders are not interpreted as a method-order claim.

To append the bounded closed-loop `Gauss6/FullVA` residual rows for the 2021
`four_link` and `slider_crank` mechanisms without rerunning the 2021 public
baseline, use:

```bash
../.venv_sbel/bin/python run_v048.py \
  --reuse-existing-results \
  --gauss6-closed-loop-2021
```

This writes `gauss6_fullva_closed_loop_external_rows.csv` and
`gauss6_fullva_closed_loop_same_window_comparison_rows.csv`. The first table
checks constraint, SO(3), and Newton-Euler reaction residuals on public
mechanisms. The second table puts public `rA` dynamics and local
`Gauss6/FullVA` closed-loop residual rows under the same selected
`T=0.2`, `h=[0.02,0.01,0.005]`, public-kinematic-reference final-error/work
columns. Both are selected-window artifacts; they are not the full public
`T=3` dynamic order/work campaign.
The same command also refreshes `ra2021_public_order_work_summary.csv` and
`gauss6_closed_loop_same_window_work_precision_summary.csv`, which are
paper-table summaries derived from the raw rows.

The default closed-loop follow-up policy is coarse-first and avoids `1e-4`.
To append a public-horizon closed-loop residual tranche for the 2021
`four_link` and `slider_crank` mechanisms at `T=3`, use:

```bash
../.venv_sbel/bin/python run_v048.py \
  --reuse-existing-results \
  --gauss6-public-closed-loop-2021 \
  --gauss6-public-closed-loop-models four_link,slider_crank \
  --gauss6-public-closed-loop-step-sizes 0.02,0.01,0.005 \
  --gauss6-public-closed-loop-t-end 3 \
  --gauss6-public-closed-loop-reference-h 1e-3
```

For faster local runs, split independent closed-loop rows by model/step-size
and merge once at the end:

```bash
../.venv_sbel/bin/python run_public_closed_loop_shard.py --model four_link
../.venv_sbel/bin/python run_public_closed_loop_shard.py --model slider_crank
../.venv_sbel/bin/python merge_public_closed_loop_shards.py
```

Those shard commands are independent and can be launched in parallel. The
merge writes the canonical `gauss6_fullva_public_horizon_closed_loop_rows.csv`
and refreshes `summary_v048.json`/`v048_report.md`.
The exact source-paper `h=[1e-2,1e-3,1e-4]` policy is now an explicit
opt-in reproduction run, not a default target; shard commands that include
`1e-4` must also pass `--allow-source-policy-1e-4`.

To add the coarse same-window public double-pendulum baseline used beside the
coarse `Gauss6/FullVA` tranche, run the three public forms independently and
merge:

```bash
../.venv_sbel/bin/python run_ra2021_double_coarse_shard.py --form rA
../.venv_sbel/bin/python run_ra2021_double_coarse_shard.py --form rp
../.venv_sbel/bin/python run_ra2021_double_coarse_shard.py --form reps
../.venv_sbel/bin/python merge_ra2021_double_coarse_shards.py
```

Those shard commands use `T=3`, `h=[0.1,0.05,0.025]`, reference `h=0.0125`,
and can be launched in parallel. They write
`ra2021_double_pendulum_coarse_order_rows.csv` and
`double_pendulum_coarse_same_window_work_precision_summary.csv`.

To rebuild and check the four-example performance coverage ledger, use:

```bash
../.venv_sbel/bin/python build_four_example_performance_matrix.py
../.venv_sbel/bin/python validate_four_example_performance_matrix.py
```

This writes `four_example_performance_matrix.csv`,
`four_example_performance_summary.json`, and
`four_example_performance_matrix.md`. It is a coverage/performance ledger, not
an external superiority claim.

To rebuild the coarse-first external readiness gate from existing rows, use:

```bash
../.venv_sbel/bin/python build_single_pendulum_coarse_same_window.py
../.venv_sbel/bin/python validate_single_pendulum_coarse_same_window.py
../.venv_sbel/bin/python build_closed_loop_surrogate_dynamic_gate.py
../.venv_sbel/bin/python validate_closed_loop_surrogate_dynamic_gate.py
../.venv_sbel/bin/python build_closed_loop_dynamic_error_floor_audit.py
../.venv_sbel/bin/python validate_closed_loop_dynamic_error_floor_audit.py
../.venv_sbel/bin/python build_closed_loop_coarse_dynamic_order_probe.py
../.venv_sbel/bin/python validate_closed_loop_coarse_dynamic_order_probe.py
../.venv_sbel/bin/python build_closed_loop_dynamic_order_closure_contract.py
../.venv_sbel/bin/python validate_closed_loop_dynamic_order_closure_contract.py
../.venv_sbel/bin/python build_closed_loop_true_dynamic_local_row_plan.py
../.venv_sbel/bin/python validate_closed_loop_true_dynamic_local_row_plan.py
../.venv_sbel/bin/python build_closed_loop_true_dynamic_interface_audit.py
../.venv_sbel/bin/python validate_closed_loop_true_dynamic_interface_audit.py
../.venv_sbel/bin/python build_closed_loop_true_dynamic_residual_scaffold.py
../.venv_sbel/bin/python validate_closed_loop_true_dynamic_residual_scaffold.py
../.venv_sbel/bin/python build_closed_loop_true_dynamic_stage_residual_audit.py
../.venv_sbel/bin/python validate_closed_loop_true_dynamic_stage_residual_audit.py
../.venv_sbel/bin/python build_closed_loop_true_dynamic_one_step_smoke.py
../.venv_sbel/bin/python validate_closed_loop_true_dynamic_one_step_smoke.py
../.venv_sbel/bin/python build_closed_loop_true_dynamic_newton_stage_smoke.py
../.venv_sbel/bin/python validate_closed_loop_true_dynamic_newton_stage_smoke.py
../.venv_sbel/bin/python build_closed_loop_true_dynamic_newton_coarse_order.py
../.venv_sbel/bin/python validate_closed_loop_true_dynamic_newton_coarse_order.py
../.venv_sbel/bin/python build_closed_loop_true_dynamic_public_work_precision.py
../.venv_sbel/bin/python validate_closed_loop_true_dynamic_public_work_precision.py
../.venv_sbel/bin/python build_closed_loop_true_dynamic_strict_common_reference.py
../.venv_sbel/bin/python validate_closed_loop_true_dynamic_strict_common_reference.py
../.venv_sbel/bin/python build_coarse_first_external_readiness_gate.py
../.venv_sbel/bin/python validate_coarse_first_external_readiness_gate.py
```

The surrogate step writes `closed_loop_surrogate_dynamic_gate.csv`,
`closed_loop_surrogate_dynamic_gate.json`, and
`closed_loop_surrogate_dynamic_gate.md`. It records two selected-window
four-link/slider-crank residual-to-error rows, but
`accepted_dynamic_order_count=0`; this is not a dynamic order/work or
external-superiority row.

The floor-audit step writes `closed_loop_dynamic_error_floor_audit.csv`,
`closed_loop_dynamic_error_floor_audit.json`, and
`closed_loop_dynamic_error_floor_audit.md`. It records two
velocity/acceleration floor-evidence rows for four-link/slider-crank and two
position-floor blockers, with `accepted_dynamic_order_count=0`.

The coarse dynamic-order probe writes
`closed_loop_coarse_dynamic_order_probe_rows.csv`,
`closed_loop_coarse_dynamic_order_probe_work_precision_summary.csv`,
`closed_loop_coarse_dynamic_order_probe.json`, and
`closed_loop_coarse_dynamic_order_probe.md`. It uses the lightweight
`T=0.2`, `h=[0.1,0.05,0.025]`, reference `h=0.0125` policy. Current result:
`11/12` rows ok, one public `slider_crank`/`rA` failure at `h=0.1`, two local
velocity/acceleration evidence rows, two local position-floor rows, and
`accepted_dynamic_order_count=0`. This confirms that larger steps do not yet
close the four-link/slider-crank dynamic-order blocker.

The closure-contract step writes
`closed_loop_dynamic_order_closure_contract.csv`,
`closed_loop_dynamic_order_closure_contract.json`, and
`closed_loop_dynamic_order_closure_contract.md`. It fixes the acceptance rule
for `four_link` and `slider_crank`: a true local `Gauss6/FullVA` dynamic
trajectory row has theorem order six, but the current kinematic/reaction rows
remain coverage evidence until either true dynamic trajectory order rows or a
reviewer-defensible residual-to-error theorem is added. It also keeps
`default_1e-4=False` and `external_superiority_claim=False`.

The true-dynamic residual scaffold writes
`closed_loop_true_dynamic_residual_scaffold.csv`,
`closed_loop_true_dynamic_residual_scaffold.json`, and
`closed_loop_true_dynamic_residual_scaffold.md`. It fixes the missing
closed-loop dynamic runner's square FullVA residual layout at 72
unknowns/residuals per stage and 216 per Gauss6 step. It does not advance a
trajectory, does not run `1e-4`, and records `accepted_dynamic_order_count=0`.

The true-dynamic stage residual audit writes
`closed_loop_true_dynamic_stage_residual_audit.csv`,
`closed_loop_true_dynamic_stage_residual_audit.json`, and
`closed_loop_true_dynamic_stage_residual_audit.md`. It evaluates the four
FullVA residual families at all three Gauss6 stage times for both missing
closed-loop mechanisms and currently gets `6/6` ok rows with max residual
about `5.51e-14`. It still does not advance an endpoint or accept dynamic
order.

The true-dynamic one-step smoke writes
`closed_loop_true_dynamic_one_step_smoke.csv`,
`closed_loop_true_dynamic_one_step_smoke.json`, and
`closed_loop_true_dynamic_one_step_smoke.md`. It advances one oracle-initialized
Gauss6 step at `h=0.1` for `four_link` and `slider_crank`; current result:
`2/2` rows ok, max stage residual about `1.55e-13`, and max endpoint position
error about `4.41e-08`. This is endpoint-stepper implementation evidence, not a
three-step convergence/order sweep.

The true-dynamic Newton stage smoke writes
`closed_loop_true_dynamic_newton_stage_smoke.csv`,
`closed_loop_true_dynamic_newton_stage_smoke.json`, and
`closed_loop_true_dynamic_newton_stage_smoke.md`. It advances one Gauss6 step
at `h=0.1` for `four_link` and `slider_crank` with stage Newton solves
initialized from the start-state extrapolation, not from stage-time kinematic
oracle roots. Current result: `2/2` rows ok, max initial stage residual about
`4.31e+01`, max final stage residual about `1.79e-13`,
`stage_oracle_used=false`, and `accepted_dynamic_order_count=0`. This is still
not a three-step convergence/order sweep.

The true-dynamic Newton coarse-order sweep writes
`closed_loop_true_dynamic_newton_coarse_order_rows.csv`,
`closed_loop_true_dynamic_newton_coarse_order.json`, and
`closed_loop_true_dynamic_newton_coarse_order.md`. It runs the local
non-oracle `Gauss6/FullVA` closed-loop dynamic stepper for `four_link` and
`slider_crank` at `T=0.1`, `h=[0.1,0.05,0.025]`, reference `h=0.0125`.
Current primary-state orders are `5.955/5.955/6.085/5.971` for `four_link`
and `6.164/6.159/7.341/6.426` for `slider_crank`; endpoint acceleration is
reported only as a diagnostic. This closes the local closed-loop dynamic-order
gap, but it is still not an external superiority claim because manuscript-grade
figure integration and broader external-suite closure/demotion remain open.

The true-dynamic public work/precision builder writes
`closed_loop_true_dynamic_public_work_precision_rows.csv`,
`closed_loop_true_dynamic_public_work_precision_summary.csv`,
`closed_loop_true_dynamic_public_work_precision.json`, and
`closed_loop_true_dynamic_public_work_precision.md`. It runs no default
`1e-4` policy and records `24/24` ok rows, with `18` public `rA/rp/reps` rows
and `6` local true-dynamic Newton rows. This closes the public
work/precision availability gap for `four_link` and `slider_crank`, but it is
still not external superiority because `strict_common_reference_error_columns`
is `false`.

The true-dynamic strict common-reference builder writes
`closed_loop_true_dynamic_strict_common_reference_rows.csv`,
`closed_loop_true_dynamic_strict_common_reference_summary.csv`,
`closed_loop_true_dynamic_strict_common_reference.json`,
`closed_loop_true_dynamic_strict_common_reference.md`, and
`closed_loop_true_dynamic_strict_common_reference_work_precision.png`. It
recomputes the public `rA/rp/reps` rows against the same
`v047_exact_kinematic_endpoint` reference used by the local true-dynamic Newton
rows. Current result: `24/24` rows ok,
`strict_common_reference_available=2/2`,
`strict_common_reference_gap=0`, and figure available. It still does not claim
external superiority.

This writes `coarse_first_external_readiness_gate.csv`,
`coarse_first_external_readiness_gate.json`, and
`coarse_first_external_readiness_gate.md`. It records the no-default-`1e-4`
policy explicitly: `single_pendulum` and `double_pendulum` currently have
coarse same-window order/time evidence for both local `Gauss6/FullVA` and
public baselines; `four_link` and `slider_crank` now have local true-dynamic
coarse order evidence, same-window public work/precision rows, and strict
common-reference columns, but still need manuscript figure integration and
broader external-suite closure/demotion before any external superiority claim.

Each run also writes `velocity_partitioning_code_search.csv`. That artifact
records the 2024 Kissel/Bakke/Negrut public-code claim, the EasyChair PDF
reference check, public web-search status, and local `sbel-reproducibility`
plus `public-metadata` tree searches over `origin/master` and
`origin/user/aaron/msd`. The current result does not resolve a distinct
velocity-partitioning code directory.

The current selected `Gauss6/FullVA` pilot completed 3/3 rows on the 2021
single-pendulum mechanism at `T=0.2` with `h=[0.2,0.1,0.05]`. It records
position/velocity/orientation/omega observed orders
`6.073/6.033/6.055/6.024`; the public kinematic reference at `h=1e-3` aligns
with the v047 analytic state at about `7e-10` or better in position, velocity,
and acceleration.

Current status:

- `same_test_campaign_status=not_run`
- `ra2021_selected_rows_status=passed`
- `full_ra2021_order_completed=true`
- `public_step_trio_group_count=9/9` after the full 2021 `rA/rp/reps`
  `single_pendulum`, `four_link`, and `slider_crank` run
- `ra2021_double_order_rows=9/9` and `ra2021_double_order_groups=3/3`
  after the public `double_pendulum` dynamic self-reference order run at
  `T=3`, `h=[1e-2,2e-3,1e-3]`, reference `h=1e-4`; the observed
  position/velocity/acceleration orders are about `0.775/0.816/0.701` for
  `rA`, `1.035/0.777/0.657` for `rp`, and `0.775/0.816/0.701` for `reps`
- `hi2022_halfimplicit_rows=24/24` and `hi2022_halfimplicit_groups=8/8`
  after the bounded 2022 `single_pendulum`, `double_pendulum`,
  `four_link`, and `slider_crank` `rA/rA_half` pilot; this is still
  bounded `T=0.1` source-wiring evidence, not the full `T=8` 2022 campaign
- `gauss6_fullva_selected_rows_completed=true` after the bounded
  single-pendulum pilot
- `gauss6_fullva_public_horizon_single_rows=3/3`,
  `gauss6_fullva_public_horizon_single_public_h_rows=3/3`, and
  `gauss6_fullva_public_horizon_single_step_trio_completed=true` after the
  exact public-horizon single-pendulum tranche at `T=3`,
  `h=[1e-2,1e-3,1e-4]`
- `gauss6_fullva_public_horizon_double_coarse_rows=3/3` after the
  cost-aware double-pendulum public-horizon coarse tranche at `T=3`,
  `h=[0.1,0.05,0.025]`, reference `h=0.0125`; this is not the public
  `1e-4` policy
- `ra2021_double_coarse_rows=6/9`, `ra2021_double_coarse_groups=2/3`, and
  `double_coarse_work_precision_rows=3` after the matching coarse same-window
  public baseline; `rp` is retained as a Newton-nonconvergence caveat
- `ra2021_single_coarse_rows=9/9`, `gauss6_single_coarse_rows=3/3`, and
  `single_coarse_work_precision_rows=4` after the single-pendulum coarse
  same-window tranche at `T=3`, `h=[0.1,0.05,0.025]`, reference `h=0.0125`;
  local position order is `6.054`, and velocity-like columns are read as
  finite-window/reference-floor diagnostics
- `coarse_first_external_readiness_gate_rows=4`,
  `coarse_first_ready_examples=2/4`,
  `local_true_dynamic_order_available=2`,
  `closed_loop_floor_audit_available=2`,
  `public_work_precision_available=2`,
  `public_work_precision_missing=0`,
  `strict_common_reference_available=2`,
  `strict_common_reference_gap=0`,
  `strict_common_reference_figure_available=True`, and
  `coarse_first_dynamic_order_missing=0`; this is a read-only CMAME readiness
  gate, not a numerical run or an external superiority claim
- `closed_loop_surrogate_dynamic_gate_rows=2`,
  `closed_loop_surrogate_available=2`, and
  `closed_loop_surrogate_accepted_dynamic_order=0`; this is the selected
  residual-to-error bridge for `four_link` and `slider_crank`, not a
  superiority claim
- `closed_loop_dynamic_error_floor_audit_rows=2`,
  `closed_loop_floor_audit_velocity_acceleration_evidence=2`, and
  `closed_loop_floor_audit_accepted_dynamic_order=0`; this narrows the
  four-link/slider-crank blocker to the position/reference floor and lack of
  accepted local dynamic trajectory/order rows
- `closed_loop_coarse_probe_rows=11/12` and
  `closed_loop_coarse_probe_accepted_dynamic_order=0`; the large-step
  `T=0.2`, `h=[0.1,0.05,0.025]` probe keeps the no-default-`1e-4` policy and
  shows that the closed-loop position floor still blocks accepted dynamic order
- `closed_loop_dynamic_order_closure_contract_rows=2`,
  `closed_loop_dynamic_order_closure_contract_theorem_order=6`, and
  `closed_loop_dynamic_order_closure_contract_true_dynamic_rows=2`; this
  machine-checks that local dynamic order is closed and the next external
  closure path is figure integration and broader external-suite closure, not
  reinterpretation of kinematic/reaction rows
- `closed_loop_true_dynamic_row_feasibility_audit_rows=2`,
  `closed_loop_true_dynamic_row_feasibility_audit_true_dynamic_rows=0`, and
  `closed_loop_true_dynamic_row_feasibility_audit_local_row_kind=kinematic_fullva_plus_reaction_reconstruction`;
  this source audit confirms that the current local closed-loop path calls
  `simulate_v046_local_kinematic_fullva`, uses `setup_system(..., "kinematics", ...)`,
  and reconstructs reactions after the kinematic solve, so it is not a local
  dynamic DAE trajectory integrator
- `closed_loop_true_dynamic_local_row_plan_rows=24`,
  `closed_loop_true_dynamic_local_row_plan_local_target_rows=6`, and
  `closed_loop_true_dynamic_local_row_plan_public_comparator_rows=18`; this
  plan-only contract fixes the next parallel batch to coarse rows with
  `h=[0.1,0.05,0.025]`, reference `h=0.0125`,
  `execution_status=not_run`, and `default_1e-4=False`
- `closed_loop_true_dynamic_interface_audit_dynamic_setup_ok=2/2` and
  `closed_loop_true_dynamic_interface_audit_do_step_called=false`; this
  setup-level audit confirms the public/v046 `rA` dynamics interfaces
  instantiate and initialize for both closed-loop models, while the local
  `Gauss6/FullVA` dynamic runner remains missing
- `closed_loop_true_dynamic_newton_coarse_order_rows=6/6`,
  `closed_loop_true_dynamic_newton_coarse_order_accepted_dynamic_order=2`,
  and `stage_oracle_used=false`; this is local true-dynamic coarse order for
  `four_link` and `slider_crank`, not public work/precision superiority
- `closed_loop_public_work_precision_rows=24/24`,
  `closed_loop_public_work_precision_available=2/2`, and
  `strict_common_reference_error_columns=false`; this closes the public
  work/precision availability gap but not external superiority
- `closed_loop_strict_common_reference_rows=24/24`,
  `closed_loop_strict_common_reference_available=2/2`, and
  `closed_loop_strict_common_reference_gap=0`; this closes the strict
  common-reference error-column gap at the coarse window but still does not
  authorize external superiority
- `closed_loop_residual_to_error_theorem_obligations_rows=7`,
  `closed_loop_residual_to_error_theorem_obligations_blocking=7`, and
  `accepted_residual_to_error_theorem=false`; this proof-obligation gate blocks
  promotion of small residuals to dynamic-order evidence until the stability,
  estimator, non-floor, and manuscript-theorem conditions are actually closed
- `gauss6_fullva_closed_loop_selected_rows_completed=true` after the bounded
  four-link/slider-crank closed-loop residual pilot
- `gauss6_fullva_closed_loop_same_window_comparison_completed=true` after the
  selected 12/12 same-window comparison rows
- `gauss6_fullva_public_horizon_closed_loop_rows=6/6`,
  `gauss6_fullva_public_horizon_closed_loop_public_h_rows=6/6`, and
  `gauss6_fullva_public_horizon_closed_loop_step_trios_completed=true` after
  the public-horizon closed-loop residual tranche for `four_link` and
  `slider_crank`
- `four_example_performance_matrix_rows=48`,
  `four_example_performance_matrix_completed=32`, and
  `four_example_performance_matrix_partial=0`
- `ra2021_public_order_work_summary_rows=9` and
  `gauss6_closed_loop_same_window_work_precision_summary_rows=4`; the double
  coarse work/precision summary contributes 3 additional manuscript-table rows
- `gauss6_fullva_external_rows_completed=false` for the full external campaign
- `velocity_partitioning_code_status=not_resolved_in_local_sbel_or_public_metadata_tree`

The bounded closed-loop pilot completes 6/6 rows on `four_link` and
`slider_crank`, with max dynamics residuals `1.338e-13` and `6.492e-15` and
max acceleration-constraint residuals `1.052e-14` and `1.204e-15`.
The public-horizon closed-loop tranche completes 6/6 rows at `T=3` and
`h=[1e-2,1e-3,1e-4]`; the finest `h=1e-4` rows have max dynamics residuals
`5.136e-13` for `four_link` and `1.113e-14` for `slider_crank`, with runtimes
`73.25s` and `89.49s`. These are still closed-loop constraint/reaction
residual rows, not dynamic order/work-superiority rows.
The double-pendulum coarse public-horizon tranche records position/velocity
orders `7.951/7.042` with max endpoint position/velocity residuals
`1.131e-05/3.533e-04`; it is the preferred next-step pattern for avoiding
new heavyweight `1e-4` runs unless that exact source policy is explicitly
needed.
The matching coarse same-window public double-pendulum baseline now records
`rA/reps` as 6/6 ok rows with position/velocity orders `0.703/0.754`; `rp`
keeps three Newton nonconvergence rows, which is a useful large-step caveat
rather than a completed superiority claim.
The single-pendulum coarse same-window tranche records 9/9 public rows and
3/3 local `Gauss6/FullVA` rows under `T=3`, `h=[0.1,0.05,0.025]`, reference
`h=0.0125`; the work/precision summary has 4 rows and the local position
order is `6.054`. This is the preferred single-pendulum evidence path because
it avoids default `1e-4` execution.
The selected same-window table completes 12/12 rows: public `rA` dynamics has
short-window velocity/acceleration orders around `1.05/1.10` on `four_link`
and `1.09/1.10` on `slider_crank`; the local `Gauss6/FullVA` rows sit on a
public-reference mismatch floor in this table, so their near-zero final-error
orders are not interpreted as dynamic convergence. The surrogate gate records
the local finest velocity-error ratios versus public `rA` as about `1.20e-7`
for `four_link` and `3.34e-5` for `slider_crank`, while still keeping accepted
dynamic order at zero.
The coarse closed-loop probe repeats that question at larger steps
`h=[0.1,0.05,0.025]`: local velocity/acceleration evidence remains present,
but the position floor persists and one public `slider_crank` coarse row fails,
so accepted dynamic order remains zero for that older probe. The newer
non-oracle Newton coarse-order sweep closes the local primary-state order gap
for `four_link` and `slider_crank`, but public same-window work/precision rows
are still missing.

The full campaign still requires running `Gauss6/FullVA` against the exact
external public-code tests and adding the resulting order/error/work tables to
the CMAME manuscript.
