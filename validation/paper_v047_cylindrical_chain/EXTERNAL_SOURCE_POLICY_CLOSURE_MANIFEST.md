# External Source-Policy Closure Manifest

Status: **not closed - source-policy reproduction required**.

- Examples: `single_pendulum, double_pendulum, four_link, slider_crank`.
- Performance rows: `32/48` completed.
- Not-complete performance rows: `16`.
- Bounded common-reference diagnostic rows: `44`.
- Strict external error-claim rows allowed: `0`.
- Source-policy flagged rows/raw rows: `15/45`.
- Parallel-ready shards without default `1e-4`: `20`.
- B2/B4 can close now: `False/False`.
- External superiority claim allowed: `False`.

## Suite Closure State

| suite | status | rows completed/total | flagged rows | shards | claim allowed now | next action |
|---|---|---:|---:|---:|---|---|
| `Kissel--Taves--Negrut absolute-coordinate suite` | `partial_public_policy_evidence_not_same-policy_superiority` | `16/16` | `5` | `12` | `baseline_order_time_summary_only` | do not rerun completed 2021 public baselines by default; close source-policy external rows or explicitly demote suites before any external-superiority claim |
| `Fang--Kissel--Zhang--Negrut half-implicit suite` | `bounded_T0p1_pilot_not_full_T8_public_policy` | `8/8` | `3` | `8` | `bounded_pilot_only` | choose full T8 reproduction or explicit demotion before an external-superiority claim |
| `Chaturvedi--Sandu--Sandu TFE pendulum` | `source_policy_runner_friction_endpoint_and_work_rows_open` | `0/12` | `4` | `0` | `formal_order_literature_comparator_only` | resolve the source-policy DAE runner, Brown-McPhee source-code-equivalent friction law, full T=10 endpoint/output policy, and accepted work rows before running |
| `Kissel--Bakke--Negrut velocity-partitioning suite` | `public_code_path_unresolved_or_proxy_only` | `0/4` | `3` | `0` | `code-path-unresolved_related_work_only` | resolve public code path or explicitly demote this suite from the external-superiority claim |

## Closure Requirements

| id | requirement | satisfied |
|---|---|---:|
| `SP1` | all included suites have source time horizon, h-grid, reference, norm, output map, and runtime policy closed | `False` |
| `SP2` | all four examples have accepted external dynamic-order rows under source policy | `False` |
| `SP3` | paper-level direct external error superiority is allowed only after source-policy reproduction | `False` |
| `SP4` | B2/B4 close only after fair implemented baselines and work/precision evidence are complete | `False` |

## Claim Policy

- Allowed now: conditional formal order comparison, bounded common-reference diagnostics, and public baseline summaries as non-superiority evidence.
- Forbidden now: paper-level external direct-error superiority, complete source-paper reproduction, VP2024 reproduction, full T=8 HI2022 superiority, and original TFE pendulum superiority.
