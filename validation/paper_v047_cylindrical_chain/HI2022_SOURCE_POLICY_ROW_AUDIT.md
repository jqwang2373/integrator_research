# HI2022 Source-Policy Row Audit

Status: **bounded T=0.1 rows complete; full T=8 source-policy rows not closed**.

This audit is read-only over existing v048 and paper-package artifacts. It does not rerun HI2022.

- Active B2 flagged HI2022 rows: `3`.
- Active/demoted B2 rows after HI2022 demotion: `0/3`.
- Bounded rows ok: `24/24`.
- Bounded form/model groups complete: `8/8`.
- Existing bounded horizon: `[0.1]`.
- Existing bounded h-grid: `[0.005, 0.01, 0.02]`.
- Full T=8 source policy completed: `False`.
- T=8 coarse horizon rows ok: `18/24`.
- T=8 coarse complete form/model groups: `4/8`.
- T=8 coarse source-policy reproduction: `False`.
- T=8 selected candidate rows ok: `3/3`.
- T=8 selected candidate full public grid: `False`.
- T=8 selected candidate matrix preflight: `7/8` completed, commands `8`.
- T=8 selected candidate matrix source-policy rows closed: `0`.
- HI2022 B4/B7 figure-scope decision: `demote_hi2022_from_b4_b7_source_policy_figures`.
- B4/B7 can close from HI2022: `False`.
- Source-policy reproduction rows: `0/3`.
- Source-policy dynamic-order examples: `0/4`.
- External-superiority-ready rows: `0`.
- External superiority claim allowed: `False`.
- Default 1e-4/heavy/run_v047: `False/False/False`.

## Closure Decision

Can close HI2022 B2 requirement now: `False`.

The existing HI2022 rows are a bounded T=0.1 pilot with three coarse step sizes. They cover all four models and both public forms, but they do not reproduce the full T=8 source-paper policy and therefore cannot support a source-policy external-superiority claim. The B2 requirement is now removed from active external-superiority scope by explicit demotion.

The new T=8 coarse-horizon sanity rows are useful failure/stability evidence, but they use coarse h values and reference h=0.0125. They do not satisfy the full public source-policy h/reference contract.

The selected T=8 candidate adds a finer rA double-pendulum shard with h=[0.02,0.01,0.005] and reference h=0.001. It confirms executability for that shard, but it is still not the full public grid and is demoted from B4/B7 source-policy figures.

## T=8 Coarse-Horizon Sanity Rows

| group | ok rows | complete trio | velocity order | max iterations | status |
|---|---:|---:|---:|---:|---|
| `rA:double_pendulum` | `3/3` | `True` | `0.679` | `32` | `ok` |
| `rA:four_link` | `3/3` | `True` | `1.006` | `100` | `ok` |
| `rA:single_pendulum` | `3/3` | `True` | `1.004` | `12` | `ok` |
| `rA:slider_crank` | `2/3` | `False` | `nan` | `37` | `failed:ValueError:array must not contain infs or NaNs; ok` |
| `rA_half:double_pendulum` | `0/3` | `False` | `nan` | `0` | `failed:RuntimeError:Newton-Raphson not converging at t: 5.000, k: 100; failed:RuntimeError:Newton-Raphson not converging at t: 5.275, k: 100; failed:RuntimeError:Newton-Raphson not converging at t: 5.850, k: 100` |
| `rA_half:four_link` | `2/3` | `False` | `nan` | `25` | `failed:RuntimeError:Newton-Raphson not converging at t: 0.700, k: 100; ok` |
| `rA_half:single_pendulum` | `3/3` | `True` | `1.004` | `11` | `ok` |
| `rA_half:slider_crank` | `2/3` | `False` | `nan` | `19` | `failed:ValueError:array must not contain infs or NaNs; ok` |

## T=8 Selected Candidate

- Status: `executed_full_T8_selected_coarse_trio_not_promoted`.
- Form/model: `rA` / `double_pendulum`.
- h values: `[0.02, 0.01, 0.005]`.
- reference h: `0.001`.
- rows ok/total: `3/3`.
- full public grid selected: `False`.
- source-policy rows closed by this evidence: `0`.
- counts as complete work/precision curve: `False`.
- B4/B7 can close from selected candidate: `False`.

## T=8 Selected Candidate Matrix Preflight

- Status: `preflight_ready_existing_selected_candidate_matrix_incomplete`.
- Script exists: `True`.
- Expected/completed shards: `8/7`.
- Commands avoid 1e-4: `True`.
- Heavy numerical run invoked by preflight: `False`.
- Source-policy rows closed by preflight: `0`.
- B4/B7 can close from preflight: `False`.

| shard | artifact status | ok/total | command |
|---|---|---:|---|
| `rA_half:single_pendulum` | `executed_full_T8_selected_coarse_trio_not_promoted` | `3/3` | `../../.venv_sbel/bin/python run_hi2022_full_t8_source_policy_candidate.py --form rA_half --model single_pendulum --execute` |
| `rA_half:double_pendulum` | `partial_or_failed_full_T8_source_policy_candidate_not_promoted` | `1/3` | `../../.venv_sbel/bin/python run_hi2022_full_t8_source_policy_candidate.py --form rA_half --model double_pendulum --execute` |
| `rA_half:four_link` | `executed_full_T8_selected_coarse_trio_not_promoted` | `3/3` | `../../.venv_sbel/bin/python run_hi2022_full_t8_source_policy_candidate.py --form rA_half --model four_link --execute` |
| `rA_half:slider_crank` | `executed_full_T8_selected_coarse_trio_not_promoted` | `3/3` | `../../.venv_sbel/bin/python run_hi2022_full_t8_source_policy_candidate.py --form rA_half --model slider_crank --execute` |
| `rA:single_pendulum` | `executed_full_T8_selected_coarse_trio_not_promoted` | `3/3` | `../../.venv_sbel/bin/python run_hi2022_full_t8_source_policy_candidate.py --form rA --model single_pendulum --execute` |
| `rA:double_pendulum` | `executed_full_T8_selected_coarse_trio_not_promoted` | `3/3` | `../../.venv_sbel/bin/python run_hi2022_full_t8_source_policy_candidate.py --form rA --model double_pendulum --execute` |
| `rA:four_link` | `executed_full_T8_selected_coarse_trio_not_promoted` | `3/3` | `../../.venv_sbel/bin/python run_hi2022_full_t8_source_policy_candidate.py --form rA --model four_link --execute` |
| `rA:slider_crank` | `executed_full_T8_selected_coarse_trio_not_promoted` | `3/3` | `../../.venv_sbel/bin/python run_hi2022_full_t8_source_policy_candidate.py --form rA --model slider_crank --execute` |


## Active Rows

| # | example | method | bounded group | bounded vel order | full T=8 done | source-policy |
|---:|---|---|---|---:|---:|---:|
| 1 | `four_link` | `hi2022_rA` | `rA:four_link` | `1.003` | `False` | `False` |
| 2 | `double_pendulum` | `hi2022_rA_half` | `rA_half:double_pendulum` | `-1.182` | `False` | `False` |
| 3 | `four_link` | `hi2022_rA_half` | `rA_half:four_link` | `1.003` | `False` | `False` |

The HI2022 rows remain bounded pilot diagnostics, not source-policy external-superiority evidence.
