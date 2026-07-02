# B4 Source-Policy Work/Precision Execution Plan

Status: `execution_plan_ready_b4_b7_remain_open`.

This is a read-only execution plan. It records the next source-policy work/precision lanes but does not run new numerical experiments.

- Open blockers after plan: `[]`.
- B4/B7 can close now: `False/False`.
- Route B closes B2/B4/B7: `True/False/False`.
- Source-policy work/precision rows closed/total: `0/40`.
- Source-policy flagged rows: `15`.
- External-superiority-ready rows: `0`.
- Common-reference order/error matrix closed: `True`.
- Common-reference velocity order wins: `40/40`.
- Common-reference finest velocity error wins: `40/40`.
- TFE same-test diagnostic rows/source-policy rows: `18/0`.
- TFE algorithm-literal work proxy/runtime proxy/source-policy rows: `total_newton_iterations` / `False` / `0`.
- TFE runner-equivalence preflight: `preflight_ready_runner_equivalence_open`.
- TFE runner-equivalence preflight closed/open/source rows: `25/6/0`.
- TFE runner-equivalence preflight can close lane: `False`.
- TFE B4/B7 figure-scope demotion: `tfe_source_policy_rows_demoted_from_current_b4_b7_figures`.
- TFE demoted/source-policy rows closed: `16/0`.
- TFE current claim requires source-policy execution: `False`.
- Default 1e-4/heavy/run_v047/v048: `False/False/False/False`.
- Next heavy source-policy execution requires user opt-in: `True`.
- Execution lane ready/not-ready count: `2/2`.
- RA2021 launch preflight: `b4-ra2021-source-policy-launch-preflight-v1` / `ready_not_run_requires_user_opt_in`.
- RA2021 runner files ready: `True`.
- RA2021 launch commands: `5`.
- RA2021 runner CLI contract: `runner_cli_contract_satisfied`.
- RA2021 preflight closes B4/B7: `False/False`.
- HI2022 launch preflight: `b4-hi2022-source-policy-launch-preflight-v1` / `preflight_ready_existing_selected_candidate_matrix_incomplete`.
- HI2022 runner files ready: `True`.
- HI2022 launch commands/completed/missing: `8/7/1`.
- HI2022 runner CLI contract: `runner_cli_contract_satisfied`.
- HI2022 commands avoid 1e-4/source rows closed: `True/0`.
- HI2022 preflight closes B4/B7: `False/False`.
- RA2021 executed shard evidence: `all_public_baseline_source_policy_shards_completed_not_promoted`.
- RA2021 executed shard forms completed: `['rA', 'rp', 'reps']`.
- RA2021 executed shard rows/source-policy rows closed: `9/0`.
- Gauss6 local source-policy evidence: `partial_local_source_policy_evidence_single_complete_closed_loop_residual_only_not_promoted`.
- Gauss6 single public-horizon rows/source-policy rows closed: `3/0`.
- Gauss6 closed-loop combined ok/failed rows: `6/0`.
- RA2021 closed-loop same-window public work/precision: `same_window_public_work_precision_available_reference_caveat_not_external_superiority`.
- RA2021 closed-loop same-window rows/available/source-policy rows closed: `24/2/0`.
- RA2021 closed-loop strict common-reference/external superiority: `False` / `False`.
- RA2021 double local source-policy candidate: `executed_order_below_acceptance_not_promoted`.
- RA2021 double local candidate rows/order accepted/source-policy rows closed: `3/False/0`.
- HI2022 full T=8 source-policy candidate: `selected_candidate_matrix_partially_executed_not_promoted`.
- HI2022 full T=8 candidate rows/full grid/source-policy rows closed: `22/False/0`.
- HI2022 B4/B7 figure-scope demotion: `demote_hi2022_from_b4_b7_source_policy_figures`.
- HI2022 B4/B7 demotion rows/clean figure/can close: `0/False/False`.
- HI2022 selected-candidate matrix completed/expected/rows closed: `7/8/0`.

## Publication Contract

- Contract: `b4-source-policy-work-precision-publication-contract-v1`.
- Plan-only closes rows: `False`.
- B4 required items: `[]`.
- B7 required items: `[]`.
- Current figure set closes B7: `True`.
- Current figure set supports common-reference diagnostics only: `True`.

## Execution Lanes

| lane | ready after opt-in | source rows | status | first missing item |
|---|---:|---:|---|---|
| `ra2021_source_policy_work_precision` | `True` | `0` | `public_baseline_rows_complete_source_policy_work_precision_promotion_open` | promote or rerun local Gauss6/FullVA rows under the RA2021 source time grid and output norm |
| `tfe_source_policy_work_precision` | `False` | `0` | `diagnostic_same_test_work_precision_available_source_policy_runner_equivalence_open` | prove or replace the candidate planar runner with a source-policy equivalent DAE runner |
| `hi2022_full_T8_work_precision` | `True` | `0` | `bounded_T0p1_rows_complete_full_T8_source_policy_work_precision_open` | select and document the full T=8 public-policy step/reference grid |
| `vp2024_source_code_path_work_precision` | `False` | `0` | `not_ready_distinct_public_velocity_partitioning_code_path_unresolved` | resolve a distinct public velocity-partitioning code path |

## Next Decision

- Recommended first lane: `ra2021_source_policy_work_precision`.
- Requires explicit 1e-4 opt-in: `True`.
- Do not run by default: `True`.
- Alternative without heavy runs: keep Route B claim demotion and do a final prose/figure review for a narrower no-external-superiority paper; this still does not close B4/B7 under the current gate.

The current TFE work/precision rows are diagnostic same-test or algorithm-literal rows.
They are useful for scope and figure development, but they do not close B4 or B7 because they do not establish a source-policy-closed external same-test row.

## TFE Runner-Equivalence Preflight

- Status: `preflight_ready_runner_equivalence_open`.
- Closed preconditions/open blockers: `25/6`.
- Source-policy rows closed by preflight: `0`.
- Can close TFE lane from preflight: `False`.
- Heavy numerical run invoked: `False`.
- Open blocker ids: `['brown_mcphee_source_code_equivalent_law_open', 'pendulum_absolute_coordinate_source_policy_dae_runner_missing', 'tfe_newmark_trapezoidal_source_policy_method_runners_missing', 'gauss6_fullva_absolute_coordinate_source_policy_runner_missing', 'full_T10_source_grid_endpoint_policy_open', 'accepted_source_policy_work_precision_rows_not_executed_or_bound']`.

## TFE B4/B7 Figure-Scope Demotion

- Status: `tfe_source_policy_rows_demoted_from_current_b4_b7_figures`.
- Source audit: `TFE_B4_B7_SOURCE_POLICY_DEMOTION_AUDIT.json`.
- TFE rows demoted for current claim/source-policy rows closed: `16/0`.
- Source-policy rows closed by demotion: `0`.
- Future reintroduction runner/code-path rows: `16`.
- Current claim requires TFE source-policy execution: `False`.
- Brown--McPhee source-code-equivalent law: `False`.
- Full T=10 source grid policy resolved: `False`.
- pendulum DAE runner implemented: `False`.
- Counts as clean work/precision figure: `False`.
- B4/B7 can close from TFE demotion: `False`.
- Allowed figure use: `related-work/formal-order context and explicitly labeled diagnostics only`.
- Forbidden figure use: `current B4/B7 source-policy work/precision figures or external-superiority claim`.

## RA2021 Launch Preflight

| command id | output after run | purpose |
|---|---|---|
| `ra2021_public_timing_all_forms_models` | `../v048_cross_paper_same_test_benchmarks/results/ra2021_public_timing_rows.csv` | bind runtime and Newton-iteration metrics to source-policy/public-code timing rows |
| `gauss6_public_single_source_policy_trio` | `../v048_cross_paper_same_test_benchmarks/results/gauss6_fullva_public_horizon_single_rows.csv` | produce Gauss6/FullVA source-policy single-pendulum rows over the source h trio |
| `ra2021_double_order_all_forms` | `../v048_cross_paper_same_test_benchmarks/results/ra2021_double_pendulum_order_rows.csv` | produce RA2021 double-pendulum public dynamic self-reference order rows |
| `gauss6_public_four_link_source_policy_trio` | `../v048_cross_paper_same_test_benchmarks/results/public_closed_loop_shards/four_link_1em02_1em03_1em04.csv` | produce public-horizon Gauss6/FullVA four-link source-policy rows |
| `gauss6_public_slider_crank_source_policy_trio` | `../v048_cross_paper_same_test_benchmarks/results/public_closed_loop_shards/slider_crank_1em02_1em03_1em04.csv` | produce public-horizon Gauss6/FullVA slider-crank source-policy rows |

Every RA2021 launch command requires `--allow-source-policy-1e-4` and remains unexecuted by this plan.
The preflight only proves that the runner interfaces and outputs are specified; it closes zero source-policy rows.
RA2021 runner CLI contract: `runner_cli_contract_satisfied` with `4` runner checks and `5` command checks.

## HI2022 Launch Preflight

- Status: `preflight_ready_existing_selected_candidate_matrix_incomplete`.
- Runner files ready: `True`.
- Expected/completed/missing shards: `8/7/1`.
- Commands avoid 1e-4: `True`.
- Source-policy 1e-4 required: `False`.
- Heavy numerical run invoked by preflight: `False`.
- Source-policy rows closed by preflight: `0`.
- B4/B7 can close from HI2022 preflight: `False/False`.
- Runner CLI contract: `runner_cli_contract_satisfied` with `1` runner checks and `8` command checks.

| command id | shard | output after run | current artifact status |
|---|---|---|---|
| `hi2022_selected_t8_rA_half_single_pendulum` | `rA_half:single_pendulum` | `../v048_cross_paper_same_test_benchmarks/results/hi2022_full_t8_source_policy_candidate_rA_half_single_pendulum_rows.csv` | `executed_full_T8_selected_coarse_trio_not_promoted` |
| `hi2022_selected_t8_rA_half_double_pendulum` | `rA_half:double_pendulum` | `../v048_cross_paper_same_test_benchmarks/results/hi2022_full_t8_source_policy_candidate_rA_half_double_pendulum_rows.csv` | `partial_or_failed_full_T8_source_policy_candidate_not_promoted` |
| `hi2022_selected_t8_rA_half_four_link` | `rA_half:four_link` | `../v048_cross_paper_same_test_benchmarks/results/hi2022_full_t8_source_policy_candidate_rA_half_four_link_rows.csv` | `executed_full_T8_selected_coarse_trio_not_promoted` |
| `hi2022_selected_t8_rA_half_slider_crank` | `rA_half:slider_crank` | `../v048_cross_paper_same_test_benchmarks/results/hi2022_full_t8_source_policy_candidate_rA_half_slider_crank_rows.csv` | `executed_full_T8_selected_coarse_trio_not_promoted` |
| `hi2022_selected_t8_rA_single_pendulum` | `rA:single_pendulum` | `../v048_cross_paper_same_test_benchmarks/results/hi2022_full_t8_source_policy_candidate_rA_single_pendulum_rows.csv` | `executed_full_T8_selected_coarse_trio_not_promoted` |
| `hi2022_selected_t8_rA_double_pendulum` | `rA:double_pendulum` | `../v048_cross_paper_same_test_benchmarks/results/hi2022_full_t8_source_policy_candidate_rA_double_pendulum_rows.csv` | `executed_full_T8_selected_coarse_trio_not_promoted` |
| `hi2022_selected_t8_rA_four_link` | `rA:four_link` | `../v048_cross_paper_same_test_benchmarks/results/hi2022_full_t8_source_policy_candidate_rA_four_link_rows.csv` | `executed_full_T8_selected_coarse_trio_not_promoted` |
| `hi2022_selected_t8_rA_slider_crank` | `rA:slider_crank` | `../v048_cross_paper_same_test_benchmarks/results/hi2022_full_t8_source_policy_candidate_rA_slider_crank_rows.csv` | `executed_full_T8_selected_coarse_trio_not_promoted` |

This read-only plan does not execute HI2022 commands. Existing selected-candidate artifacts are summarized separately; reruns still require explicit heavy-run opt-in.
The preflight only enumerates isolated candidate shard commands; it closes zero source-policy rows.

## Executed RA2021 Shards

- Forms completed: `['rA', 'rp', 'reps']`.
- Rows ok/total: `9/9`.
- Shared h values: `[0.01, 0.002, 0.001]`.
- reference h values: `[0.0001]`.
- Velocity pair orders by form: `{'rA': [0.7169574830975796, 1.1175597094775156], 'rp': [0.7073874526843799, 0.989617671737206], 'reps': [0.7169574830935925, 1.1175597094633662]}`.
- Public-baseline shard rows executed: `9`.
- Counts as complete work/precision curve: `False`.
- B4/B7 can close from this evidence: `False/False`.

| form | path | ok/total | velocity pair orders |
|---|---|---:|---|
| `rA` | `../v048_cross_paper_same_test_benchmarks/results/ra2021_double_order_shards/rA_double_pendulum_0p0001.csv` | `3/3` | `[0.7169574830975796, 1.1175597094775156]` |
| `rp` | `../v048_cross_paper_same_test_benchmarks/results/ra2021_double_order_shards/rp_double_pendulum_0p0001.csv` | `3/3` | `[0.7073874526843799, 0.989617671737206]` |
| `reps` | `../v048_cross_paper_same_test_benchmarks/results/ra2021_double_order_shards/reps_double_pendulum_0p0001.csv` | `3/3` | `[0.7169574830935925, 1.1175597094633662]` |

## Gauss6 Local Source-Policy Evidence

- Status: `partial_local_source_policy_evidence_single_complete_closed_loop_residual_only_not_promoted`.
- Single public-horizon step trio completed: `True`.
- Single h values: `[0.01, 0.001, 0.0001]`.
- Closed-loop h=1e-4 standalone ok models: `2`.
- Closed-loop public step trios completed: `True`.
- Closed-loop rows are dynamic work/precision: `False`.
- Counts as B4 accepted source-policy rows: `False`.
- B4/B7 can close from Gauss6 evidence: `False/False`.

| shard | ok/total | failed | h values | status notes |
|---|---:|---:|---|---|
| `single_public_horizon` | `3/3` | `0` | `[0.01, 0.001, 0.0001]` | public-horizon local trio |
| `four_link_combined` | `3/3` | `0` | `[0.01, 0.001, 0.0001]` | residual/kinematic, not dynamic work/precision |
| `slider_crank_combined` | `3/3` | `0` | `[0.01, 0.001, 0.0001]` | residual/kinematic, not dynamic work/precision |
| `four_link_h1e4_standalone` | `1/1` | `0` | `[0.0001]` | residual/kinematic standalone h=1e-4 |
| `slider_crank_h1e4_standalone` | `1/1` | `0` | `[0.0001]` | residual/kinematic standalone h=1e-4 |

## RA2021 Closed-Loop Same-Window Work/Precision

- Status: `same_window_public_work_precision_available_reference_caveat_not_external_superiority`.
- Rows ok/total: `24/24`.
- Public work/precision available examples: `['four_link', 'slider_crank']`.
- Public work/precision missing count: `0`.
- T/h/reference h: `0.1` / `[0.1, 0.05, 0.025]` / `0.0125`.
- Strict common-reference error columns: `False`.
- Reference alignment status: `mixed_reference_family_requires_manuscript_caveat`.
- External superiority claim: `False`.
- Counts as bounded same-window diagnostic: `True`.
- Counts as complete RA2021 work/precision curve: `False`.
- Source-policy rows closed by same-window evidence: `0`.
- B4/B7 can close from same-window evidence: `False/False`.

| model | local velocity order | public methods | runtime ratio vs rA |
|---|---:|---|---:|
| `four_link` | `6.08481873098771` | `['rA-public-dynamics', 'reps-public-dynamics', 'rp-public-dynamics']` | `64.79499358020124` |
| `slider_crank` | `7.340914510263872` | `['rA-public-dynamics', 'reps-public-dynamics', 'rp-public-dynamics']` | `80.79864653298493` |

## RA2021 Double Local Source-Policy Candidate

- Status: `executed_order_below_acceptance_not_promoted`.
- Runner status: `executed_isolated_source_policy_candidate`.
- Rows ok/total: `3/3`.
- h values: `[0.01, 0.002, 0.001]`.
- reference h: `0.0001`.
- Reference status/cache/runtime: `ok` / `True` / `5707.131385425993`.
- Candidate position/velocity order: `2.148202286933232` / `2.463397024938419`.
- Position pair orders: `[2.824757355346447, 0.09680243299693665]`.
- Velocity pair orders: `[3.248066380656726, 0.08418108693039757]`.
- Finest pair position/velocity order: `0.09680243299693665` / `0.08418108693039757`.
- Constraint-threshold failed h values: `[0.01]`.
- Low-order failure modes: `['aggregate_observed_order_below_5p5_threshold', 'position_pair_order_below_5p5_threshold', 'velocity_pair_order_below_5p5_threshold', 'at_least_one_candidate_row_fails_endpoint_constraint_threshold']`.
- Order acceptance threshold/satisfied: `5.5` / `False`.
- Promotion ready: `False`.
- Counts as B4 accepted source-policy rows: `False`.
- B4/B7 can close from double candidate: `False/False`.

Promotion blockers:

- source-policy rows are complete but not yet independently rerun
- observed source-policy order is below sixth-order acceptance (pos=2.148, vel=2.463)
- error norm/output mapping not yet bound to accepted source-policy rows
- runtime/Newton-iteration policy not yet tied to accepted source-policy rows
- independent rerun or verification artifact not yet produced

## HI2022 Full T=8 Source-Policy Candidate

- Status: `selected_candidate_matrix_partially_executed_not_promoted`.
- Runner statuses: `['executed_full_T8_selected_coarse_trio_not_promoted', 'partial_or_failed_full_T8_source_policy_candidate_not_promoted']`.
- Forms/models: `['rA', 'rA_half']` / `['double_pendulum', 'four_link', 'single_pendulum', 'slider_crank']`.
- Summary/rows artifacts: `8/8`.
- Completed/expected shards: `7/8`.
- Partial-or-failed shards: `['rA_half:double_pendulum']`.
- Missing artifact shards: `[]`.
- Rows ok/total: `22/24`.
- T=8/reference h selected: `True` / `True`.
- h values: `[0.02, 0.01, 0.005]`.
- reference h values: `[0.001]`.
- Full public grid selected/completed: `False` / `False`.
- Source-policy 1e-4 included: `False`.
- Reference statuses/runtime values: `['ok']` / `[8.460787251009606, 12.791629565996118, 16.809752425993793, 15.855694137047976, 8.652628500014544, 13.354955013026483, 16.873604504973628, 19.182942087063566]`.
- Position pair orders by shard: `{'rA_half:single_pendulum': [-0.01122725542325414, -0.28339349346837284], 'rA_half:double_pendulum': [], 'rA_half:four_link': [0.01814734671025952, -0.022994418841639917], 'rA_half:slider_crank': [3.24906198377441, 0.0791438847197366], 'rA:single_pendulum': [0.04306872189188594, -0.43133931160794425], 'rA:double_pendulum': [0.30212137477335393, 1.0774892160989], 'rA:four_link': [0.45711722252133086, -0.3949107994269268], 'rA:slider_crank': [3.9055197135865356, 3.026325826597138]}`.
- Velocity pair orders by shard: `{'rA_half:single_pendulum': [1.0007568147469175, 1.000359627081342], 'rA_half:double_pendulum': [], 'rA_half:four_link': [1.002952997656428, 1.0015593303432058], 'rA_half:slider_crank': [0.9985830190096858, 0.9996582944124607], 'rA:single_pendulum': [1.0007568147446453, 1.0003596270948678], 'rA:double_pendulum': [0.3416453126642631, 1.062670620819211], 'rA:four_link': [1.0029529977079763, 1.0015593303001036], 'rA:slider_crank': [0.9985830192150059, 0.9996582944257089]}`.
- Acceleration pair orders by shard: `{'rA_half:single_pendulum': [0.9517541301647995, 0.9767914062085483], 'rA_half:double_pendulum': [], 'rA_half:four_link': [1.0203148605658712, 1.0100160556065236], 'rA_half:slider_crank': [1.0056582034571655, 1.0055390633370984], 'rA:single_pendulum': [0.9517541309284435, 0.9767913986928394], 'rA:double_pendulum': [0.15772788977030902, 0.4447263931480143], 'rA:four_link': [1.020314858981941, 1.0100160558274491], 'rA:slider_crank': [1.0056581746390023, 1.005539083404113]}`.
- Runtime values: `[0.343863989925012, 0.5749531000619754, 1.066894399933517, 2.684584806091152, 0.8733523009577766, 1.3845398660050705, 2.356148340040818, 0.6810450529446825, 1.1745680769672617, 1.8977922629565, 0.4279602989554405, 0.6765915929572657, 1.1198868829524145, 0.8930995169794187, 1.6052946330746636, 3.1232164630200714, 1.7729512569494545, 2.895835777046159, 4.014201128971763, 1.88135419995524, 2.5026896389899775, 5.0250493419589475]`.
- Counts as full public-grid source-policy: `False`.
- Counts as B4 accepted source-policy rows: `False`.
- Counts as complete work/precision curve: `False`.
- Source-policy rows closed by HI2022 candidate: `0`.
- Promotion ready: `False`.
- B4/B7 can close from HI2022 candidate: `False/False`.

HI2022 promotion blockers:

- full HI2022 public step grid is not selected or not completed
- runtime and error/order rows are not yet bound into a publication-grade full-policy figure
- selected coarse trio is not the full encoded HI2022 public step family
- work/precision figure rows are not promoted from this isolated shard

## HI2022 B4/B7 Figure-Scope Demotion

- Status: `demote_hi2022_from_b4_b7_source_policy_figures`.
- Source audit: `HI2022_SOURCE_POLICY_ROW_AUDIT.json`.
- Bounded rows ok/total: `24/24`.
- T=8 coarse rows ok/total: `18/24`.
- T=8 coarse complete groups: `4/8`.
- T=8 selected candidate rows ok/total: `3/3`.
- T=8 selected candidate full public grid: `False`.
- T=8 selected candidate matrix status: `preflight_ready_existing_selected_candidate_matrix_incomplete`.
- T=8 selected candidate matrix completed/expected: `7/8`.
- T=8 selected candidate matrix rows ok/total: `22/24`.
- T=8 selected candidate matrix commands/count avoid 1e-4: `8` / `True`.
- T=8 selected candidate matrix heavy run invoked: `False`.
- T=8 selected candidate matrix rows closed/can close: `0` / `False`.
- T=8 selected candidate matrix partial-or-failed shards: `['rA_half:double_pendulum']`.
- T=8 selected candidate matrix missing artifact shards: `[]`.
- Source-policy rows closed by HI2022: `0`.
- Counts as clean work/precision figure: `False`.
- B4/B7 can close from HI2022: `False`.
- Allowed figure use: `['bounded diagnostic rows', 'T=8 failure/stability demotion evidence']`.
- Forbidden figure use: `['source-policy external-superiority curve', 'publication-grade B4/B7 work/precision closure row']`.

HI2022 demotion gaps:

- HI2022 full T=8 public grid remains incomplete
- HI2022 selected-candidate matrix has 7/8 completed coarse-trio shards; remaining partial/missing shards are ['rA_half:double_pendulum']
- current HI2022 T=8 evidence is demoted from B4/B7 source-policy figures
- HI2022 contributes zero accepted source-policy work/precision rows
