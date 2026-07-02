# External Same-Test Acceptance Sheet

Status: **ACCEPTANCE REQUIREMENTS DEFINED - CAMPAIGN NOT RUN**

This sheet is a read-only acceptance ledger for the remaining external
same-test comparison. It does not invoke `run_v047.py`, any v048 runner, or a
default `1e-4` campaign. The purpose is to prevent the external-baseline gate
from drifting back to a heavy source-policy run when the current next step is a
coarse-first order/time comparison.

## Execution Boundary

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

## Current Counts

- four examples required: `single_pendulum`, `double_pendulum`,
  `four_link`, `slider_crank`
- external required case count: `17`
- performance matrix rows: `48`
- completed performance rows: `32`
- not-complete performance rows: `16`
- partial performance rows: `0`
- local evidence coverage examples: `4/4`
- accepted method dynamic-order examples: `2/4`
- mechanism-coverage examples: `2/4`
- accepted source-policy dynamic-order examples: `0/4`
- accepted external dynamic-order examples: `0`
- parallel-ready batches: `2`
- parallel shards without default `1e-4`: `20`

## Required Acceptance Columns

Every row that is promoted to a same-test comparison must report:

- `position_error`
- `velocity_error`
- `observed_order`
- `runtime`
- `work_precision`
- `average_newton_iterations`
- `constraint_drift`
- `reference_policy`
- `same_test_setup_identity`

Residual-only rows do not count as dynamic order. A row with a different
reference policy can be retained as bounded evidence, but it cannot close an
external-superiority claim unless the policy distinction is stated in the
manuscript.

## Example-Level Acceptance

| Example | Current evidence | Accepted for method dynamic order? | Accepted for external superiority? | Missing before external claim |
| --- | --- | --- | --- | --- |
| `single_pendulum` | Coarse-first order/time evidence exists. | yes | no | Included source suites must be completed or demoted. |
| `double_pendulum` | Coarse-first order/time evidence exists. | yes | no | Included source suites must be completed or demoted. |
| `four_link` | Local closed-loop mechanism-coverage/coarse-dynamics diagnostic and strict common-reference work/precision rows exist. | no, mechanism coverage only | no | Fair public-source same-test decision remains open. |
| `slider_crank` | Local closed-loop mechanism-coverage/coarse-dynamics diagnostic and strict common-reference work/precision rows exist. | no, mechanism coverage only | no | Fair public-source same-test decision remains open. |

## Suite-Level Acceptance

| Suite | Acceptance status | Default `1e-4`? | Closure action |
| --- | --- | --- | --- |
| Original Chaturvedi--Sandu--Sandu TFE pendulum | `not_ready_source_setup_encoding_required` | unknown until source policy encoded | Resolve source-policy DAE runner, Brown--McPhee source-code-equivalent friction law, full T=10 endpoint/output policy, and accepted work rows, then decide run or demotion. |
| 2021 Kissel/Taves/Negrut `rA/rp/reps` suite | `partial_evidence_not_external_superiority` | no | Finish or rerun missing coarse shards, then make a bounded/no-superiority decision. |
| 2022 Fang/Kissel/Zhang/Negrut half-implicit suite | `policy_decision_open` | no | Choose full `T=8` reproduction or explicit demotion. |
| 2024 Kissel/Bakke/Negrut velocity-partitioning suite | `code_path_unresolved` | no | Resolve public code path or explicitly demote. |

## Closure Rules

B2 closes only when the included external source suites are completed under a
fair same-test policy or explicitly demoted in the manuscript. B4 closes only
when the package has fair implemented baseline work/precision curves and clean
order/time interpretation. Neither B2 nor B4 requires a default `1e-4`
campaign.

The current accepted next numerical policy, if execution is later approved, is
the coarse-first batch: `h=[0.1,0.05,0.025]` with reference `h=0.0125`, split
by model, form, and step across available cores.

## Validator

Run:

```bash
../.venv_sbel/bin/python validate_external_same_test_acceptance_sheet.py
```

Expected markers:

- `external_same_test_acceptance_sheet=PASS`
- `same_test_campaign_status=not_run`
- `accepted_external_dynamic_order_examples=0`
- `parallel_shard_count_without_default_1e-4=20`
- `default_1e-4=False`
- `heavy_numerical_run_invoked=False`
- `external_superiority_claim=False`
- `submission_ready=False`
