# External Suite Disposition Audit

Status: **suite dispositions defined; B2/B4 not closed**.

- Suites classified: `4`.
- Accepted external-superiority suites: `0`.
- Same-test campaign status: `not_run`.
- Parallel-ready shards without default `1e-4`: `20`.
- Source-policy flagged rows: `15`.
- B2 can close now: `False`.
- B4 can close now: `False`.

## Suite Dispositions

| suite | current disposition | shards | required next action | claim allowed now |
|---|---|---:|---|---|
| `Chaturvedi--Sandu--Sandu TFE pendulum` | `encode_then_run_or_demote` | `0` | encode source pendulum setup, output policy, friction law, and norm; then run or demote | `diagnostic_or_literature_only` |
| `Kissel--Taves--Negrut absolute-coordinate suite` | `run_remaining_same_test_or_bound_claim` | `12` | finish or rerun coarse same-window shards and record setup identity, reference policy, order, and time | `diagnostic_or_literature_only` |
| `Fang--Kissel--Zhang--Negrut half-implicit suite` | `choose_full_T8_run_or_demote` | `8` | choose full T=8 public-policy reproduction or explicit demotion | `diagnostic_or_literature_only` |
| `Kissel--Bakke--Negrut velocity-partitioning suite` | `demote_until_code_path_resolved` | `0` | resolve public velocity-partitioning code path or state suite demotion | `diagnostic_or_literature_only` |

## Closure Boundary

- B2 remains open until included suites are completed under fair same-test policy or explicitly demoted.
- B4 remains open until fair implemented baselines and work/precision curves are available.
- The current manuscript states the no-external-superiority boundary; this audit makes the per-suite execution state explicit.
