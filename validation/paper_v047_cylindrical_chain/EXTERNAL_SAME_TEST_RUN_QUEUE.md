# External Same-Test Run Queue

Status: **COARSE-FIRST PARALLEL QUEUE READY - NOT RUN**

This is a read-only queue for the remaining cross-paper numerical campaign. It
does not invoke `run_v047.py`, any v048 runner, or a default `1e-4` campaign.
The purpose is to make the remaining order/time work explicit enough to launch
parallel shards later without confusing coarse-first evidence with a completed
external-superiority claim.

## Execution Policy

- default policy: `coarse_first_no_default_1e-4`
- coarse step sizes: `0.1`, `0.05`, `0.025`
- coarse reference step: `0.0125`
- strict public-policy `1e-4`: `opt_in_only`
- `default_1e-4_required=false`
- `heavy_numerical_run_invoked=false`
- `run_v047_invoked=false`
- `v048_runner_invoked=false`
- `same_test_campaign_status=not_run`
- `external_superiority_claim=false`

## Queue Summary

- external source count: `4`
- required case count from `CROSS_PAPER_BENCHMARK_CASES.json`: `17`
- queue batches: `4`
- parallel-ready coarse-first batches: `2`
- not-ready batches: `2`
- parallel shards without default `1e-4`: `20`
- source-policy `1e-4` opt-in batches: `1`
- unresolved code-path batches: `1`
- local evidence coverage examples: `4/4`
- accepted method dynamic-order examples: `2/4`
- mechanism-coverage examples: `2/4`
- source-policy external dynamic-order examples: `0/4`

## Parallel Batches

| Priority | Batch | Status | Parallel shards | Default `1e-4`? | Next action |
| ---: | --- | --- | ---: | --- | --- |
| 1 | `ra2021_coarse_same_window_order_time` | `parallel_ready_existing_interfaces` | `12` | no | Do not rerun completed 2021 public baselines by default; close or demote the local Gauss6/FullVA same-policy dynamic order/work rows. |
| 2 | `hi2022_halfimplicit_full_policy_decision` | `parallel_ready_after_policy_selection` | `8` | no | Choose full `T=8` reproduction or explicit demotion before any external-superiority claim. |
| 3 | `tfe2026_original_pendulum_encoding` | `not_ready_source_setup_encoding_required` | `0` | unknown until source policy is encoded | Resolve the source-policy DAE runner, Brown--McPhee source-code-equivalent friction law, full T=10 endpoint/output policy, and accepted work rows. |
| 4 | `vp2024_velocity_partitioning_code_resolution` | `not_ready_code_path_unresolved` | `0` | no | Resolve public code path or explicitly demote this suite from the external-superiority claim. |

The first batch is the closest match to the user's four-example requirement:
`single_pendulum`, `double_pendulum`, `four_link`, and `slider_crank` with
public `rA/rp/reps` baselines, order/time metrics, and coarse step sizes
`0.1`, `0.05`, `0.025`. The current v048 evidence now has 2021 public
baseline order groups `12/12` and public timing rows `12/12`. The remaining
gap is not the public baseline execution. The local evidence coverage layer is
`4/4`, but accepted method dynamic-order evidence is `2/4` and the closed-loop
four-link/slider-crank rows remain mechanism-coverage/coarse-candidate evidence.
The remaining gate is external source-policy closure: accepted source-policy
dynamic-order examples remain `0/4`, and no external-superiority claim is
allowed until included source suites are completed under a fair same-test policy
or explicitly demoted in the manuscript.

## Acceptance Rules

- order and time are both required;
- same-test setup identity is required;
- a common reference or declared reference policy is required;
- residual-only rows do not count as dynamic order;
- full external superiority requires every included external suite to be
  completed or explicitly demoted;
- suite demotions must be stated in the manuscript before submission.

## Validator

Run:

```bash
../../.venv_sbel/bin/python validate_external_same_test_run_queue.py
```

Expected markers:

- `external_same_test_run_queue=PASS`
- `required_case_count=17`
- `parallel_shard_count_without_default_1e-4=20`
- `default_1e-4=False`
- `run_v047_invoked=False`
- `v048_runner_invoked=False`
- `external_superiority_claim=False`
- `submission_ready=False`
