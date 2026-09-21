# HI2022 Policy Decision Audit

Status: **BOUNDED T=0.1 ROWS COMPLETE; FULL T=8 SOURCE POLICY OPEN**

This audit classifies the existing Fang--Kissel--Zhang--Negrut half-implicit evidence.
It does not run any numerical shard and does not promote the bounded pilot to an external-superiority claim.

## Existing Evidence

- source suite: `hi2022_fang_kissel_zhang_negrut`
- evidence class: `bounded_pilot_only_not_source_policy_reproduction`
- existing policy: `hi2022_bounded_four_example_pilot_not_full_campaign`
- existing horizon: `[0.1]`
- existing h-grid: `[0.005, 0.01, 0.02]`
- reference h: `[0.001]`
- rows ok: `24/24`
- model/form groups with three h values: `8/8`

## Source-Policy Boundary

- full `T=8` source policy completed: `False`
- accepted for bounded evidence: `True`
- accepted for external superiority: `False`
- local evidence coverage examples carried from dashboard: `4/4`
- accepted method dynamic-order examples carried from dashboard: `2/4`
- mechanism-coverage examples carried from dashboard: `2/4`
- source-policy dynamic-order examples: `0/4`
- external-superiority claim allowed: `False`

## Existing Row Groups

| Group | Rows ok | h values | Reference policy | Execution path |
| --- | ---: | --- | --- | --- |
| `rA:double_pendulum` | `3/3` | `[0.005, 0.01, 0.02]` | `bounded_rA_dynamics_self_reference` | `public_run_function` |
| `rA:four_link` | `3/3` | `[0.005, 0.01, 0.02]` | `bounded_rA_kinematics_reference` | `state_history_replay` |
| `rA:single_pendulum` | `3/3` | `[0.005, 0.01, 0.02]` | `bounded_rA_kinematics_reference` | `public_run_function` |
| `rA:slider_crank` | `3/3` | `[0.005, 0.01, 0.02]` | `bounded_rA_kinematics_reference` | `state_history_replay` |
| `rA_half:double_pendulum` | `3/3` | `[0.005, 0.01, 0.02]` | `bounded_rA_dynamics_self_reference` | `public_run_function` |
| `rA_half:four_link` | `3/3` | `[0.005, 0.01, 0.02]` | `bounded_rA_kinematics_reference` | `state_history_replay` |
| `rA_half:single_pendulum` | `3/3` | `[0.005, 0.01, 0.02]` | `bounded_rA_kinematics_reference` | `public_run_function` |
| `rA_half:slider_crank` | `3/3` | `[0.005, 0.01, 0.02]` | `bounded_rA_kinematics_reference` | `state_history_replay` |

## Decision

`choose_full_T8_reproduction_or_explicit_demotion`.

Before any CMAME external-superiority statement, either run the full `T=8` source-policy reproduction
or explicitly demote this suite to bounded diagnostic evidence in the manuscript.

## Validator

Run:

```bash
../../.venv_sbel/bin/python validate_hi2022_policy_decision_audit.py
```
