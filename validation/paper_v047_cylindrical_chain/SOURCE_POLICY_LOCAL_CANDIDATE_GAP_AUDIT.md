# Source-Policy Local Candidate Gap Audit

Status: **local candidate gap open; source-policy not closed**.

- Active source-policy suites: `0`.
- Active B2 flagged rows: `0`.
- Demoted flagged rows: `15`.
- Source-policy closed rows: `0/40`.
- Common-reference claim allowed: `True`.
- Local dynamic-order examples: `2/4`.
- Accepted source-policy dynamic-order examples: `0`.
- Source-policy dynamic-order examples: `0/4`.
- Active row requirements: `0` rows; external-superiority-ready `0`.
- External superiority claim allowed: `False`.
- Heavy/default `1e-4`/run_v047 invoked: `False/False/False`.

## Local Candidate And Demotion Evidence

| suite | current local evidence | accepted source-policy rows | blocking gap |
|---|---|---:|---|
| `ra2021_absolute_coordinate` | single public-grid `3/3`, double coarse `3/3`, closed-loop public-grid rows present; closed-loop true-dynamic coarse candidates `2/2` | 0 | near-roundoff/floor-limited public-policy tranche; not enough to close all four RA2021 source-policy examples |
| `hi2022_half_implicit` | demoted; bounded T=0.1 `24/24`, T=8 coarse `18/24`, complete T=8 groups `4/8` | 0 | T=8 coarse rows are useful stability/failure evidence, but only 4/8 form-model groups are complete and the source-policy h/reference contract is not met |
| `tfe2026_original_pendulum` | bounded runner rows `4`, endpoint sensitivity rows `48` | 0 | no distinct public TFE code artifact was found; paper-spec/proxy self-reproduction is not source-policy equivalent, so these rows stay attempted-not-reproducible and not promoted |

## Active Row Requirements

| suite | example | method | action | resolved/missing | queue | 1e-4 policy |
|---|---|---|---|---:|---|---|

## RA2021 Coarse True-Dynamic Evidence

- Closed-loop true-dynamic coarse candidates: `2/2` models, rows `6/6`.
- Step sizes/time window: `0.1|0.05|0.025`/`0.1`.
- Public work/precision rows: `24/24`; available examples `2`.
- Coarse-first gate: ready examples `2/4`, strict common-reference gap `0`, same-test campaign `not_run`.

| model | pos order | orient order | vel order | omega order | accepted coarse candidate |
|---|---:|---:|---:|---:|---|
| `four_link` | `5.955` | `5.955` | `6.085` | `5.971` | `True` |
| `slider_crank` | `6.164` | `6.159` | `7.341` | `6.426` | `True` |

## Closure Gaps

| suite | gap | next action |
|---|---|---|
| `ra2021_absolute_coordinate` | single pendulum has source-grid candidate rows, but double-pendulum and closed-loop examples are not accepted source-policy dynamic-order/work rows | run or demote the remaining RA2021 local same-policy dynamic rows after resolving velocity/output mapping and floor policy |
| `hi2022_half_implicit` | demoted after bounded T=0.1 evidence plus incomplete T=8 coarse/tolerance-repair source-policy evidence | keep HI2022 in bounded diagnostic/related-work scope only unless a new source-policy campaign is explicitly requested |
| `tfe2026_original_pendulum` | public TFE source code is absent and the available paper-spec/proxy reconstruction is not source-policy equivalent | keep TFE rows attempted-not-reproducible/not-promoted unless a new source-code-equivalent public or author artifact appears |

Reading rule: this artifact explains why existing local candidate rows do not yet close source-policy external superiority. It is not a new numerical campaign and does not promote any row to a source-policy claim.
