# External Case Evidence Reconciliation

Status: **BOUNDED EVIDENCE PRESENT; FULL SOURCE-POLICY CAMPAIGN OPEN**.

- Same-test campaign status: `not_run`.
- Case inventory status counts: `{'code_path_unresolved': 1, 'not_run': 16}`.
- Bounded/public evidence suites: `ra2021_absolute_coordinate, hi2022_half_implicit`.
- Not-ready or demote suites: `tfe2026_original_pendulum, vp2024_velocity_partitioning`.
- 2021 public baseline order groups: `12/12`.
- 2021 public timing rows: `12/12`.
- Local Gauss6/FullVA source-policy dynamic-order examples accepted: `0/4`.
- Source-policy rows closed: `0/15`.
- External-superiority-ready rows: `0/15`.
- Accepted external dynamic-order examples: `0`.
- B2/B4 can close now: `False/False`.
- Default `1e-4` required: `False`.
- Heavy numerical run invoked: `False`.

## Suite Reconciliation

| suite | case inventory | bounded evidence | performance rows | source-policy closed | allowed use |
| --- | --- | --- | ---: | --- | --- |
| `ra2021_absolute_coordinate` | `{'not_run': 7}` | `True` | 16/16 | `False` | `baseline_order_time_summary_only` |
| `hi2022_half_implicit` | `{'not_run': 7}` | `True` | 8/8 | `False` | `bounded_pilot_only` |
| `tfe2026_original_pendulum` | `{'not_run': 2}` | `False` | 0/12 | `False` | `formal_order_literature_comparator_only` |
| `vp2024_velocity_partitioning` | `{'code_path_unresolved': 1}` | `False` | 0/4 | `False` | `code-path-unresolved_related_work_only` |

## Interpretation

The case inventory's `not_run` markers refer to the full source-policy
same-test campaign. They do not erase bounded/coarse evidence already
present in v048. They also do not close source-policy reproduction,
B2/B4, or any external-superiority claim.

The current 2021 public-code reading is more specific: the public
baseline order and timing rows are complete, but the local
Gauss6/FullVA rows are not yet complete source-policy dynamic
order/work rows for all four examples.
