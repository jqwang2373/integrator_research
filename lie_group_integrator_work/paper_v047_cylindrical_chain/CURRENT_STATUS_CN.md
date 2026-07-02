# v047 当前状态说明

这份文件是给人读的短版 context。它不新增论文 claim，只把当前
artifact 已经证明的边界写清楚，避免把四个 ASME 验证、Gauss6/FullVA
六阶方法、以及 paper TFE replacement 三件事混在一起。

## 一句话结论

当前执行目标已经切回 full source-policy 复现/降级，不是只做窄化
formal-order comparison。主目标不是复现原 paper；formal-order comparison
只是当前 `Gauss6/FullVA` 条件六阶 claim 与本地 source-paper/local target
五阶目标之间的 bounded claim boundary。现有科学主线仍然是 `Gauss6/FullVA` 六阶路径：
四个 ASME examples 进入方法证据体系，其中 `single_pendulum` 和
`double_pendulum` 是 accepted dynamic-order evidence，`four_link` 和
`slider_crank` 是 mechanism-coverage/closed-loop consistency evidence；
smooth h-sweep 是 `7.161/7.066`。但全局投稿口径现在必须优先处理
source-policy：找不到公开代码的 suite 已按“公开代码缺失 -> 自复现/代理尝试
-> 不等价 -> attempted_not_reproducible / unable_to_reproduce_not_promoted”记录；有公开 source root
的 RA2021/HI2022 不能混同为无代码行，仍按 promotion/execution 边界处理。

## 当前顶层状态（当前权威）

- `validate_paper_package.py` 已经 `PASS`，但这只说明当前包和 claim
  boundary 自洽；它同时明确记录 `submission_ready=False`、
  `mechanical_preflight_passed=True`、全局 `quality_review_passed=False`。
  另一个窄化口径字段 `quality_review_passed_under_narrowed_claim=True`
  只表示 bounded subsidiary subcheck 已过，不是全局投稿质量门已过。
- 窄化 Gauss6/FullVA method/theorem/common-reference 口径：
  bounded subcheck satisfied，但不是全局投稿决定。机器兼容字段
  `narrowed_claim_submission_standard_met=true` 和
  `narrowed_claim_decision=submit_under_narrowed_claim` 只表示 bounded
  subsidiary subcheck；不要读成 global submit。B1--B8 已按窄化 claim
  closure policy 关闭。
- 全局 `submission_ready=true` 仍未达到，当前阻塞项只有
  `OC4/OC6/OC12`：source-policy rows 仍是 `0/40`，原始 TFE source-policy
  DAE runner 仍未闭合，完整 source-policy runner package 仍未 ready。
- 当前 source-policy 行状态是：40 个 external method/example cells 已映射；
  TFE 16 行和 VP2024 4 行已经是 `attempted_not_reproducible_not_promoted`
  / `unable_to_reproduce_not_promoted`
  （公开代码未找到，paper-spec/proxy 自复现不等价，底层账本
  `source_policy_rows_unable_to_reproduce=20`）；RA2021 12 行和
  HI2022 8 行仍是 `promotion_open/not_promoted`，需要 source-policy
  promotion 或显式 B4 执行授权后的 closeout。
- `SOURCE_POLICY_PUBLIC_CODE_REFRESH_20260614` 仍是下游 source-policy 账本
  使用的公开代码刷新证书；`SOURCE_POLICY_PUBLIC_CODE_REFRESH_20260620`
  是最新 read-only 补充查询证据。TFE/VP 共 `20` 行刷新，20260620
  记录 `current_query_count=11`、`positive_public_code_artifact_rows=0`、
  `source_policy_rows_closed/promoted=0/0`，不重新打开 execution queue，
  也不改变下游 source-policy promotion 状态。
- TFE 的 DAE/source-policy execution preflight 现在是
  `terminal_no_public_code_self_reproduction_attempted_not_promoted`，
  `explicit_user_opt_in_required=false`；只有出现新的公开代码或
  source-code-equivalent artifact 才重新打开这条 source-policy 路线。
- `RA_HI_SOURCE_POLICY_PROMOTION_BLOCKER_MATRIX` 是当前 RA/HI 的行级权威短表：
  20 行都是 public-source-root rows，`no_public_code_rows_included=0`，
  `source_policy_rows_closed/promoted/not_promoted=0/0/20`，
  `attempted_not_reproducible_rows=0`。这些 public-root 行的已有输出/诊断现在是
  `current_evidence_terminal_not_promotable_rows=20`，不是 source-policy
  reproduction complete；未来 promotion 需要显式授权的 B4 closeout 或新的
  source-policy promotion artifact。
- `B4_SOURCE_POLICY_EXECUTION_HANDOFF_PACKAGE` 是当前 source-policy 复现交接包：
  它不是 runner，也不授权执行。它记录 `source_policy_rows closed/total=0/40`，
  TFE/VP terminal unable-to-reproduce rows `20`，RA/HI 需要授权 closeout 或
  新 artifact 的 rows `20`，ready command batches/commands/mapped rows
  `2/13/20`，`execution_authorized=false`，`commands_not_run_by_handoff=true`。
  即使未来按精确 opt-in 跑完 13 条命令，也还要经过 post-execution
  promotion audit，不能直接把 rows 记为 closed。
- 注意不要把 `OC6` 和 proof 里的 `P6` 混在一起：`OC6` 是 objective
  completion 里的全局投稿阻塞项，指原始 TFE source-policy DAE runner
  还没闭合；`P6` 是条件六阶定理里的 solver-scale interface，指
  \(\eta_h^{tube} \le c_\eta h^7\) 这个 compact-tube Newton 残差尺度条件。
  当前 proof 可以在 retained `P6` 下成立，但这不会关闭 `OC6`，也不会把
  fixed-tolerance logs 升级成 theorem-level solver-policy proof。
- 严格证明主路线不是 primitive 162-subterm Taylor lane，而是
  direct residual-bridge/Kantorovich route：96 行 non-dynamic certificate
  加 36 行 Newton--Euler direct-substitution zero rows 给出 active PC2 的
  132-row residual-defect input。preferred marker 是
  `direct_pc2_proof_gap_closed=true`；legacy `proof_gap_closed` 只作为
  schema compatibility marker 保留，并且只在这个 direct route scope 下成立，
  不关闭 primitive/Taylor、P6、P7 或 source-policy。
- 当前 proof-writing validator 已把这个边界锁住：theorem/traceability、
  strict proof、Newton--Euler obligation gate、B3 direct review、D5 direct
  certificate、D5 conditional Taylor certificate 和 P6 solver-scale audit
  均通过；这些通过项证明的是 conditional direct theorem scope，不是
  global submission-ready。
- 当前 proof-style/equation hygiene 也已收紧为全局硬门：main/flat 的
  display equation labels 都已被正文引用，`291/291`；active order
  theorem/proof 的 display labels 是 `28/28`，未引用数为 `0/0`。
- Taylor/primitive route 保留为 diagnostic/appendix 方向：`0/162` primitive
  actual primitive-route Taylor subterm bounds certified，五个 primitive obligations 仍未闭合
  (`P_state`, `P_acc`, `P_lambda`, `P_geom`, `P_gyro`)。这不会削弱当前
  direct theorem，但也不能被写成已经证明。
- P6 的 `eta_h^{tube} <= c_eta h^7` 是 theorem-level solver-policy condition，
  不是 fixed-tolerance logs 证明出来的事实。P7 residual-to-error theorem
  仍未 promotion，所以 four-link/slider-crank 不能单独写成 accepted
  asymptotic dynamic-order proof。
- 不要运行 source-policy/B4 命令，除非明确给出 opt-in 句子：
  `I explicitly approve running the B4 source-policy execution commands listed in B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json.`
- 本轮安全验证状态：public-code refresh、self-reproduction audit、B4 row
  ledger、B4 opt-in packet、B4 execution handoff、existing-artifact promotion audit、RA/HI blocker
  matrix、objective completion audit、CMAME review agent、reproducibility
  manifest、submission bundle validator 均通过；全局结论仍是
  `do_not_submit_global`，open blockers 仍是 `OC4/OC6/OC12`。
- `FULL_SOURCE_POLICY_RUNNER_ARCHIVE_GAP_AUDIT` 现在把 OC12 package gap
  单独锁住：当前 narrowed/replay archive ready，但不是 full source-policy
  runner archive；`source_policy_rows closed/total=0/40`，
  `terminal_unable_to_reproduce_rows=20`，`ra_hi_rows_requiring_authorized_closeout_or_new_artifact=20`，
  `source_policy_handoff_ready_now=true`，`source_policy_handoff_authorized_now=false`，
  `full_archive_ready_now=false`，`can_use_current_archive_as_full_source_policy_runner_archive=false`。
- 当前 narrowed archive boundary matches the reproducibility manifest: `True`。
  精确边界 tuple 是
  `narrowed_archive_ready_not_full_source_policy_runner_archive/0/40/False/False/True`；
  blocking ids/status 是 `OC4,OC6,OC12` /
  `OC4=open,OC6=partial,OC12=partial`；current archive use 是
  `narrowed_claim_only`, not a full source-policy runner archive。
  Objective blocker matrix 是
  `blocker_open_by_id=OC4:True,OC6:True,OC12:True`、
  `blocker_closure_decision_by_id=OC4:remain_open_ready_for_authorized_execution_not_executed_not_promoted,OC6:remain_open_no_positive_source_equivalent_artifact,OC12:remain_partial_narrowed_replay_ready_full_source_policy_archive_not_ready`、
  `blocker_closure_allowed_by_id=OC4:False,OC6:False,OC12:False`；
  这些字段表示全局 blocker 仍未关闭，不是投稿 ready 信号。
- `B4_B7_NON_SUPERIORITY_ROUTE_AUDIT` 的口径已经改成防误读版本：
  `b4_b7_closed_by_narrowed_claim_policy=true` 只表示 bounded narrowed-claim
  subcheck 关闭，不是 global source-policy closure；同一 artifact 同时写明
  `global_source_policy_rows_closed=0/40`、`global_submission_ready=false`、
  `narrowed_closure_is_global_submission/source_policy_closure=false/false`。
  旧的 `paper_submission_b4_can_close_now` 字段只作为 legacy compatibility
  alias 保留，scope 是
  `legacy_bounded_narrowed_claim_subcheck_alias_not_global_submission_ready`。

| 问题 | 当前答案 |
| --- | --- |
| 原 paper 有没有 full TFE？ | 有，它提出的是 paper-style temporal finite-element method。 |
| 我们现在 accepted 的是什么？ | `Gauss6/FullVA` 六阶路径。 |
| 我们主 claim 是什么？ | 一个 bounded formal-order comparison：`Gauss6/FullVA` 是条件六阶，本地 paper-style `m=3` TFE 目标是五阶；pendulum rows 支持 dynamic order，closed-loop rows 支持 mechanism coverage。 |
| 我们有没有 accepted full TFE replacement？ | 没有，`full_tfe_stage_replacement=false`。 |
| 这影响主 claim 吗？ | 不影响；replacement 是复现原 paper residual 的更强附加目标。 |

## 原 paper / local target vs accepted v047 claim

- Source-paper/local target：当前比较用的是本地编码的 `m=3`
  Gauss-Lobatto TFE formula target，expected order 是 `5`。
- Accepted v047 claim：当前接受的是 `Gauss6/FullVA` 六阶 one-step map，
  smooth observed orders 是 `7.161/7.066`。四个 ASME examples 已纳入证据体系：
  pendulum examples 是 dynamic-order evidence，closed-loop examples 是
  lower-pair coverage 和 constraint/reaction consistency evidence。
- Not claimed：我们没有声称 complete source-paper residual reproduction；
  因为 `full_tfe_stage_replacement=false` 仍然打开。
- 实际读法：这是 conditional order-comparison，不是说 every source-paper
  TFE residual row 已经替换了 Newton 里的 accepted `Gauss6/FullVA`
  stage residual。

## 已经完成

- 四个 ASME-style examples 已经在当前 gate 中接受：
  `single_pendulum`、`double_pendulum`、`four_link`、`slider_crank`。
- 当前 accepted production path 是 `Gauss6/FullVA`。
- 这是六阶 Gauss collocation/FullVA 路径；smooth h-sweep 记录的 observed
  position/velocity orders 是 `7.161/7.066`。
- B1/B3 现在按 direct residual-bridge 口径闭合：B1 有 AD-expanded symbolic
  oracle closure，B3 direct proof review 通过。active PC2 由 96 行
  non-dynamic certificate 加 36 行 Newton--Euler direct-substitution zero rows
  关闭；active direct Newton--Euler open obligations 是 `0`。
- 证明仍然是 conditional theorem：P1/P2/P3 是 retained theorem
  interfaces，P6 是单独的 solver-scale interface；P4 的 binding convention
  retained，但 96-row non-dynamic certificate 是 proved/discharged input；P5
  是 direct-route discharged interface，P7 是 residual-to-error nonpromotion
  boundary。这个状态足以支撑窄化 theorem claim，但不等于全局 source-policy
  submission ready。
- `four_link`/`slider_crank` 现在有 closed-loop coarse-dynamics/local
  diagnostic orders 和 strict common-reference evidence，但 paper 中仍按
  mechanism coverage/constraint-reaction consistency 使用，不把它们单独升级成
  accepted asymptotic dynamic-order proof。
- LaTeX paper draft、flat submission source、PDF、figure snapshots、claim
  ledger、proof manifests、review agent report 和 package validators 已同步。

## Kissel/Negrut 外部基线

这里不能把 Kissel/Negrut 相关工作说成“一篇 paper”。当前需要分成三套
外部 baseline family：

- 2021/2022 `rA/rp/reps` absolute-coordinate suite：本地代码路径是
  `../external/sbel-reproducibility/2021/ASME/rA-formulation`。
- 2022 half-implicit suite：本地代码路径是
  `../external/sbel-reproducibility/2022/HalfImplicit_JCND`。
- 2024 velocity-partitioning Lie-group ODE suite：paper DOI 是
  `10.1115/1.4065254`。2024 performance-comparison preprint 也说有
  open-source Python code；v048 现在检查了 EasyChair PDF reference、public
  web search，以及本地 `sbel-reproducibility` 和 `public-metadata` 的
  `origin/master`/`origin/user/aaron/msd` tree，仍没有 resolve 到独立的
  velocity-partitioning 代码目录。这个证据记录在
  `velocity_partitioning_code_search.csv`。

v048 现在完成了一个完整 2021 public-code baseline 和两个 bounded pilot：

- public-code baseline：2021 `rA/rp/reps` 在 `single_pendulum`、
  `four_link`、`slider_crank` 上的完整 order table，`h=[1e-2,1e-3,1e-4]`，
  `T=3`，27/27 rows ok，9/9 个 2021 public-order groups。
- 2021 `double_pendulum` dynamic self-reference order：`rA/rp/reps`，
  `T=3`，`h=[1e-2,2e-3,1e-3]`，reference `h=1e-4`，9/9 rows ok，
  3/3 groups。这个补上了 public `order_analysis.py` 没有 double-pendulum
  kinematic-reference row 的缺口，但它仍然是单独的 dynamic-reference policy。
- 当前不再把 `1e-4` 作为默认执行策略。它只保留为“严格复现原文 public
  policy”时才运行的重任务；现在 order/debug/paper-table 默认走 coarse-first
  三步长。
- `EXTERNAL_SAME_TEST_ACCEPTANCE_SHEET` 现在把这个规则写成机器可查的
  B2/B4 acceptance boundary：`h=[0.1,0.05,0.025]`、reference `0.0125`、
  `default_1e-4_required=false`、`accepted_external_dynamic_order_examples=0`。
  也就是说，下一步要补的是粗步长 order/time/work-precision 的 fair
  comparison，不是默认重跑 `1e-4`。
- matching coarse same-window `double_pendulum` public baseline：`T=3`，
  `h=[0.1,0.05,0.025]`，reference `h=0.0125`。`rA/reps` 6/6 rows ok，
  position/velocity orders 是 `0.703/0.754`；`rp` 三个 coarse 步长都记录
  Newton nonconvergence。这正是为了避免默认跑很重的 `1e-4`。
- `Gauss6/FullVA` same-mechanism pilot：同一个 2021 single-pendulum 机制，
  `T=0.2`，`h=[0.2,0.1,0.05]`，3/3 rows ok，position/velocity/orientation/
  omega observed orders 是 `6.073/6.033/6.055/6.024`。
- `Gauss6/FullVA` public-horizon single-pendulum tranche：同一个 2021
  single-pendulum 机制，真实 public time window `T=3`，public step sizes
  `h=[1e-2,1e-3,1e-4]`，3/3 rows ok；finest row 的 position/velocity error 是
  `2.584e-14/7.012e-15`，30000 次 Newton iterations，runtime `76.625s`。
  这些 final-error order 已经受 roundoff/reference floor 影响；这关闭了 single-pendulum public-policy row set，但还不是完整 external campaign。
- `Gauss6/FullVA` closed-loop residual pilot：2021 public `four_link` 和
  `slider_crank` 机制，`T=0.2`，`h=[0.02,0.01,0.005]`，reference
  `h=0.001`，6/6 rows ok。它验证的是 constraint、SO(3) 和
  Newton-Euler reaction residual；four_link/slider_crank 的 max dynamics
  residual 分别是 `1.338e-13`/`6.492e-15`。这不是 dynamic order/work
  superiority rows。
- `Gauss6/FullVA` public-horizon closed-loop residual tranche：同样的
  `four_link` 和 `slider_crank`，真实 public time window `T=3`，public step
  sizes `h=[1e-2,1e-3,1e-4]`，6/6 rows ok；finest rows 的 max dynamics
  residual 是 `5.136e-13/1.113e-14`，runtime 是 `73.25s/89.49s`。这仍然
  是 residual/reaction rows，不是 dynamic order/work-superiority rows。
- selected same-window comparison：同样的 `four_link` 和 `slider_crank`，
  public `rA` dynamics vs local `Gauss6/FullVA` residual rows，`T=0.2`，
  `h=[0.02,0.01,0.005]`，12/12 rows ok。它把两边放进同一套
  public-kinematic-reference final-error/work columns，但仍然只是
  selected-window/table-shape evidence，不是 exact public `T=3` dynamic
  campaign。
- v048 同时派生了两个 paper-table summary：9 行 2021 public order/work
  summary，和 4 行 selected same-window work/precision summary。它们只是把
  raw rows 整理成论文表格，不改变 claim boundary。
- 2022 half-implicit public-code pilot：`single_pendulum`、`double_pendulum`、
  `four_link`、`slider_crank` 上的 `rA/rA_half`，`T=0.1`，
  `h=[0.02,0.01,0.005]`，24/24 rows ok，8/8 model-form groups。它只是
  bounded source-wiring evidence，不是完整 `T=8` convergence campaign。

这些 pilot 仍然不能支持 external superiority claim，因为它们不是完整的
same-test campaign。真正的 CMAME pre-submission gate 仍然是：在原 TFE
paper 的 pendulum tests 和 Kissel/Negrut 各套 public-code tests 上跑同参数、
同 reference、同 error/work metric 的 `Gauss6/FullVA` 对比。

## 容易混淆的点

- `TFE` 是 temporal finite element，不是 `FTE`。
- 原 paper 公式映射里当前编码的是 `m=3` Gauss-Lobatto TFE operator；
  这个 formula-mapping audit 的 expected order 是 `5`。
- 这个五阶 paper-TFE 公式映射不是当前 accepted `Gauss6/FullVA` 六阶
  production path。两者是不同 claim。

## full TFE replacement 的位置

这不是为了让四个 examples 通过。四个 examples 的 method gate 已经通过了。

继续做 `full_tfe_stage_replacement` 只是为了一个更强、更接近原 paper 的
claim：证明 nonlinear solve 里的 132-row stage residual 本身可以由
paper-derived temporal finite-element weak rows 替换，而不是用 accepted
`Gauss6/FullVA` 路径再加 endpoint/projection/terminal-bridge 诊断证据。

所以当前边界应该这样读：

- 工程/验证层面：`Gauss6/FullVA` 六阶路径和四个 ASME examples 已接受。
- paper-TFE 层面：`m=3` Gauss-Lobatto TFE formula mapping 是五阶诊断，
  但 full stage replacement 还没接受。
- 论文主线：我们只需要 claim 一个 bounded formal-order comparison，
  `Gauss6/FullVA` 六阶路径已经是主证据。
- 复现层面：如果要额外声称“实现的就是原 paper-style TFE nonlinear residual”，
  才需要继续补 `full_tfe_stage_replacement`。

## 当前 submission-ready 缺什么

这里要分清两个层级。

按窄化 `Gauss6/FullVA` method/theorem/common-reference 口径，当前包已经是
mechanically consistent：B1--B8 已关闭，direct residual-bridge/Kantorovich
证明路线已经支撑 conditional sixth-order theorem，TFE 只作为 formal-order
comparator 和 diagnostic/common-reference material 使用。

如果目标是全局 `submission_ready=true`，当前真正缺的是：

- `OC4`：apples-to-apples external source-policy reproduction rows 仍是
  `0/40`，所以不能声明 source-paper external superiority。
- `OC6`：原始 TFE source-policy pendulum DAE runner 仍然 partial；缺完整
  source-policy DAE runner、TFE/comparator source-policy method runners、
  Gauss6 source-policy runner、full-T10 endpoint policy、accepted
  work-precision source rows。
- `OC12`：完整 source-policy runner archive 仍未 ready；当前 runner package
  可支持窄化 claim replay/provenance，但不是 full source-policy archive。
  边界 tuple 固定为
  `narrowed_archive_ready_not_full_source_policy_runner_archive/0/40/False/False/True`，
  当前 archive use 是 `narrowed_claim_only`, not a full source-policy runner archive。

因此，submission-ready 的全局缺口不是“证明还没写够”，也不是四个 ASME
examples；它是 source-policy/TFE-runner/full-runner-package 三件事。

## full TFE replacement 研究缺口（不是当前窄化投稿缺口）

`full_tfe_stage_replacement=false` 仍然是打开的研究 gate。

它要求把 132-row stage residual 里的 stage equations 真正换成
paper-derived TFE weak rows，并且要满足：

- source-free：不用 endpoint-boundary source；
- 不用 terminal-row replacement；
- 不用 output projection；
- 不用 target-direction oracle；
- 非线性 h-sweep 中 raw terminal endpoint velocity closure 达标；
- smooth paper-TFE order target 恢复；
- Newton rank 仍为 `132`，residual 仍在容差内。

当前最强的 source-free terminal closure 已经能关闭 terminal velocity，
但 smooth position order 只有 `3.523`，所以不能接受为 full-TFE
replacement。

最新的 bounded JSON-only slope probe 也没有关闭这个缺口：4 个
`stage02_convex_pose_velocity_slope_*` local rows 用时 `25.8` 秒，rank
保持 `132`，但最好的
`stage02_convex_pose_velocity_slope_0p01_0p05_z` 只有 projection residual
`0.677034`，仍然是 rank-8/no-span。因此缺的不是 near-terminal convex
pose/velocity family 的一阶斜率 row。

最新的 bounded JSON-only curvature probe 也同样是负例：4 个
`stage02_convex_pose_velocity_curvature*` local rows 用时 `26.7` 秒，
rank 保持 `132`，但最好的
`stage02_convex_pose_velocity_curvature_0p01_0p05_0p10_z` 只有
projection residual `0.871228`，仍然是 rank-8/no-span。因此缺的也不是
near-terminal convex pose/velocity family 的二阶曲率 row。

最新的 bounded JSON-only source/history coefficient-feature matrix probe 也
是负例：16 个 local rows 用时 `44.8` 秒，rank 保持 `132`，但最好的
`source_curvature_shifted_column_broadcast_feature` 只有 projection residual
`0.898873`，仍然是 rank-8/no-span，缺口几乎完全在 stage 2 的
`translation_velocity_v`。

最新的 bounded JSON-only nonlinear recurrent curvature/history matrix-feature
probe 也是负例：16 个 local rows 用时 `45.5` 秒，rank 保持 `132`，
最好的
`source_curvature_minus_history_delta_diagonal_plus_row_broadcast_feature`
只有 projection residual `0.898865`，仍然是 rank-8/no-span，缺口还是
stage 2 的 `translation_velocity_v`，fraction `0.556051`，stage-2 fraction
`0.999996`。

最新的 bounded JSON-only terminal-limit source-lift matrix-difference probe
也没有关闭缺口：8 个 local rows 用时 `47.5` 秒，rank 保持 `132`，
最好的
`stage02_convex_pose_velocity_extrapolate_0p01_0p02_sourceliftmatrixdiff_curvature_m0p1_z`
只有 projection residual `5.298e-06`，仍然是 rank-8/no-span。它接近
未修正 terminal-limit residual `4.699e-06`，但没有变成 span。

刚补的 curvature source-lift scale refinement 也排除了“只是系数没扫准”
这个解释：11 个 local rows 用时 `52.9` 秒，测试未修正 terminal-limit row
以及曲率 lift 系数 `0.01/0.05/0.1/0.2/0.5` 的正负号，rank 保持 `132`，
最好的
`stage02_convex_pose_velocity_extrapolate_0p01_0p02_sourceliftmatrixdiff_curvature_p0p01_z`
仍然只有 projection residual `5.298e-06`，没有 span。这个点的
`source_curvature_norm` 只有 `1.076e-14`，所以简单调 source-lift scale
不会补上缺的 tangent。

刚补的 mean-acceleration bridge scale refinement 也排除了“`accel_m1/p1`
太大，换小系数就行”的解释：11 个 local rows 用时 `31.4` 秒，测试未修正
terminal-limit row 以及 mean-acceleration bridge 系数
`0.01/0.05/0.1/0.2/0.5` 的正负号，rank 保持 `132`，仍然没有 span。整体
best 还是 terminal-bridge-equivalent 的未修正 row，residual `5.298e-06`；
最好的非 terminal-equivalent 修正是
`stage02_convex_pose_velocity_extrapolate_0p01_0p02_accel_p0p01_z`，
residual `0.000867721`，主要缺口转成 `lie_position_u`，fraction
`0.706665`。

刚补的 generalized-acceleration Taylor-shift scale refinement 也没有关闭
这个 rank-8 缺口：11 个 local rows 用时 `30.2` 秒，测试同一个
terminal-limit extrapolated row，加上左右 convex 点分开的 stage-local
`h*zdot` Taylor shift，系数为 `0.01/0.05/0.1/0.2/0.5` 的正负号。
rank 保持 `132`，整体 best 仍然是 terminal-bridge-equivalent 的未修正
row，residual `5.298e-06`；最好的非 terminal-equivalent 修正是
`stage02_convex_pose_velocity_extrapolate_0p01_0p02_genaccel_p0p01_z`，
residual `0.000866899`，主要缺口还是 `lie_position_u`，fraction
`0.701135`。所以缺的那 8 个方向也不是这种简单的 generalized-acceleration
Taylor shift。

刚补的 pose-acceleration Taylor-shift scale refinement 往 `lie_position_u`
方向更直接，但仍然没有 span：11 个 local rows 用时 `29.9` 秒，测试同一个
terminal-limit extrapolated row，加上左右 convex 点分开的 stage-local
`h^2*zdot` pose shift。rank 保持 `132`，整体 best 仍然是
terminal-bridge-equivalent 的未修正 row，residual `5.298e-06`；最好的非
terminal-equivalent 修正是
`stage02_convex_pose_velocity_extrapolate_0p01_0p02_poseaccel_p0p01_z`，
residual `4.1835e-05`，主要缺口仍是 `lie_position_u`，fraction
`0.711570`，stage-2 fraction `0.771337`。这比只改 velocity 的
genaccel 更接近，但仍然不是缺的 independent full-TFE row。

刚补的 tiny pose-acceleration scale refinement 进一步排除了“只是
pose-shift 系数还不够小”的解释：10 个 local rows 用时 `30.0` 秒，测试
`0.0005/0.001/0.002/0.005` 的正负号以及之前的 `p0p01`。rank 保持
`132`，整体 best 仍然是 terminal-bridge-equivalent 的未修正 row，
residual `5.298e-06`；最好的非 terminal-equivalent 修正是
`stage02_convex_pose_velocity_extrapolate_0p01_0p02_poseaccel_p0p0005_z`，
residual `5.5898e-06`，主要缺口回到 `translation_acceleration_a`，
fraction `0.350240`。所以缩小 pose shift 只是贴近 terminal-equivalent
极限，仍然没有产生 independent full-TFE closure row。

刚补的 pose+velocity acceleration Taylor refinement 也没有补上缺口：11 个
local rows 用时 `30.7` 秒，把小的 `h^2*zdot` pose shift 和小的
`h*zdot` velocity shift 组合起来测试。rank 保持 `132`，整体 best 仍然是
terminal-bridge-equivalent 的未修正 row，residual `5.298e-06`；最好的非
terminal-equivalent 修正是
`stage02_convex_pose_velocity_extrapolate_0p01_0p02_posevelaccel_p0p0005_m0p0001_z`，
residual `1.0173e-05`，主要缺口是 `lie_position_u`，fraction
`0.544660`。所以简单的 pose/velocity Taylor 组合项也不是缺的
independent full-TFE closure row。

刚补的 component-split pose-acceleration Taylor refinement 把同一个
`h^2*zdot` pose shift 拆成 translation-only 和 angular/Lie-only 两支来测。
两个 JSON-only screen 共 26 个 local rows，用时 `32.3+32.3` 秒，rank 保持
`132`，仍然 no-span。translation-only 分支即使系数扫到 `0.1`，也基本等同
terminal-limit 未修正 row；最好的非 terminal-equivalent law 是
`stage02_convex_pose_velocity_extrapolate_0p01_0p02_transposeaccel_m0p01_z`，
residual `5.298e-06`，主要缺口还是 `translation_acceleration_a`，fraction
`0.407672`。angular-only 分支复现了之前 full poseaccel 的行为：
`angposeaccel_p0p002` residual `9.6511e-06`，`angposeaccel_p0p01` residual
`4.1835e-05`。所以之前 poseaccel 的有效扰动主要来自 angular/Lie pose，
translation-only pose shift 不是缺的 independent weak row。

刚补的 component-split velocity-acceleration Taylor refinement 把
`h*zdot` generalized-velocity shift 拆成 translational velocity 和 angular
velocity 两支。第一轮 JSON-only screen 共 13 个 local rows，用时 `31.8`
秒，rank 保持 `132`，仍然 no-span。最好的非 terminal-equivalent law 是
`stage02_convex_pose_velocity_extrapolate_0p01_0p02_transvelaccel_m0p01_z`，
residual `2.138e-04`，主要缺口是 `translation_acceleration_a`，fraction
`0.886603`，stage-2 fraction `0.812539`；最好的 angular velocity 分支
是 `angvelaccel_p0p01`，residual `0.000864560`，主要缺口转成
`lie_position_u`。随后 tiny translational scale screen 又测了
`0.0005/0.001/0.002/0.005` 的正负号，11 个 local rows 用时 `31.4` 秒，
仍然 no-span；最佳
`stage02_convex_pose_velocity_extrapolate_0p01_0p02_transvelaccel_m0p0005_z`
residual `9.8175e-06`，主要缺口 fraction `0.802349`，仍差于未修正
terminal-limit row 的 `5.298e-06`。所以缩小 translational velocity shift 也
只是接近 terminal-equivalent 极限，不是缺的 independent weak row。

刚补的 component-mixed pose/velocity Taylor refinement 把最有希望的两支
组合起来测：angular/Lie pose shift 加 translational velocity shift，以及
互补的 translation-pose/angular-velocity 分支。JSON-only screen 共 13 个
local rows，用时 `32.0` 秒，rank 保持 `132`，仍然 no-span。最好的非
terminal-equivalent law 是
`stage02_convex_pose_velocity_extrapolate_0p01_0p02_angpose_transvelaccel_p0p0005_m0p0005_z`，
residual `9.987e-06`，主要缺口还是 `translation_acceleration_a`，fraction
`0.774582`，stage-2 fraction `0.625975`。互补的 `transpose_angvelaccel`
分支只有 `0.000864560`。所以这个 component-mixed Taylor cross term 也不
是缺的 independent weak row。

刚补的 stage-2-fixed/delta acceleration velocity-shift refinement 继续针对
剩下的 `translation_acceleration_a` 主方向：把 velocity shift 的
acceleration source 换成 stage-2-only，或者 stage2-stage0 的 delta20。
JSON-only screen 共 13 个 local rows，用时 `31.8` 秒，rank 保持 `132`，
仍然 no-span。最佳非 terminal-equivalent law 是
`stage02_convex_pose_velocity_extrapolate_0p01_0p02_transvelaccelstage2_m0p0005_z`，
residual `9.8175e-06`，主要缺口 fraction `0.802349`，stage-2 fraction
`0.622536`；最佳 delta20 分支
`stage02_convex_pose_velocity_extrapolate_0p01_0p02_transvelacceldelta20_m0p0005_z`
只有 `1.0119e-05`。所以 stage-2-fixed/delta20 acceleration source 只是复现
tiny translational shift 极限，不是 independent full-TFE closure row。

刚补的 nonfinal terminal velocity/source predictor refinement 更独立一些：
只用 stage0/stage1 的 lower-pair velocity rows 和 source estimates 去预测
terminal closure。JSON-only screen 共 9 个 local rows，用时 `30.9` 秒，rank
保持 `132`，仍然 no-span。最佳 law 是
`nonfinal_velocity_terminal_euler1_z`，residual `0.923466`，主要缺口变成
`translation_velocity_v`，fraction `0.526951`，stage-2 fraction `0.959959`。
也就是说，普通的 nonfinal velocity/source integral predictor 缺了几乎全在
stage2 的 terminal-bridge Jacobian direction，不能作为 full-TFE replacement。

我又把这族 nonfinal predictor 放进 bounded trajectory h-sweep。stage0/1 的
8 个 law 用时 `135.3` 秒，rank `132`，24/24 rows 收敛，`projection_used=false`，
但 terminal velocity 没关：最好的 max terminal velocity 只有 `1.770e-07`；
order 比较好的 `euler1/ab01/source01linear1` 也还有 `3.584e-07`。然后我加了
stage0/1/2 版本：`linear012/euler2/ab12/source12mean2/source12linear2/hermite12`，
用时 `101.1` 秒，18/18 rows 收敛，但还是 `terminal_velocity_closed=false`。
最接近的 stage2 rows 在 `h=0.04` 有 `2.559e-11`，但到 `h=0.02` 反而跳到
`1.328e-07`，不是 convergent closure；最稳定的 `linear012` 也只有
`1.134e-07`。所以 nonfinal velocity/source 这条路线在 trajectory level 也被排除了。

刚补的 stage-2 source-to-velocity transport refinement 更接近缺口：直接在
stage-2 pose/velocity closure 上做 source/history 到 generalized velocity
的投影。第一轮 13 个 local rows 用时 `53.4` 秒，最佳
`stage02_convex_pose_velocity_0p00_sourceliftmatrixdiff_historydelta_m0p1_z`
residual `0.001251`，independent target rank 降到 `6`，主要缺口变成
`lie_position_u`。随后 scale refinement 测 11 个 rows，用时 `57.7` 秒，
最佳
`stage02_convex_pose_velocity_0p00_sourceliftmatrixdiff_historydelta_m0p01_z`
residual 降到 `0.0001251`，但仍然 no-span、rank 还是 `6`。这是目前最强的
nonterminal transport clue，但还不是 independent full-TFE closure row。

继续补的 ultra-fine scale refinement 把同一支 `historydelta`
matrix-difference source-to-velocity transport 系数缩小到
`0.0001/0.0002/0.0005/0.001`。JSON-only screen 共 9 个 local rows，用时
`49.6` 秒，最佳
`stage02_convex_pose_velocity_0p00_sourceliftmatrixdiff_historydelta_m0p0001_z`
residual 进一步降到 `1.251e-06`，但仍然 no-span、independent target rank
还是 `6`，主要缺口还是 `lie_position_u`，fraction `0.597231`。这说明这条
source-transport family 能逼近 stage-2 endpoint 极限，但单靠继续缩小系数
仍然不是 independent full-TFE closure row。

刚补的 source-transport + angular-pose 组合 probe 测试了一个更独立的
component：在最佳 `m0p0001` source transport 上叠加很小的 angular/Lie
pose acceleration shift。JSON-only screen 共 8 个 local rows，用时 `48.7`
秒。整体 best 仍然是 source-only
`stage02_convex_pose_velocity_0p00_sourceliftmatrixdiff_historydelta_m0p0001_z`
的 `1.251e-06`；最佳组合 row
`stage02_convex_pose_velocity_0p00_sourceliftmatrixdiff_historydelta_m0p0001_angposeaccel_p0p0001_z`
只有 `1.296e-06`，independent target rank 反而回到 `8`，仍然 no-span。
所以简单 angular/Lie pose Taylor component 不是缺的 independent row。

最新补的 bare endpoint-pose velocity check 解释了前面为什么一直往
`m0p0001` 缩放：`stage02_convex_pose_velocity_0p00_z` 本身在 local row-space
里已经 roundoff span，residual `1.327e-15`，3 个 rows 用时 `31.7` 秒，
`span_row_count=1`。这说明 `m0p0001` source transport 是在逼近这个 bare
endpoint row，不是在产生新的 independent tangent。这个结果很有用，但它
仍然是 local-span-not-full-TFE，不是 accepted full TFE replacement，因为它还没有 nonlinear trajectory
h-sweep、没有 order proof，也没有更新 artifact；所以
`full_tfe_stage_replacement=false` 仍然不变。

我刚把这个 local span 推进到真正的 nonlinear trajectory smoke 了，仍然是
JSON-only，没有写 artifact，也没有跑完整 generator。新 target 是
`lower_pair_endpoint_pose_velocity_predictor_h_sweep_smoke`。默认 smooth-only
`0p00` 两个 h 用时 `21.5` 秒，terminal velocity 关到 `7.29e-17`，但
velocity order 只有 `4.508`。三点 smooth-only refinement 用
`h=[0.04,0.02,0.01]`、`reference_h=0.005`、`t_final=0.04`，用时 `28.6`
秒，terminal velocity 还是很好，`8.124e-17`，但 position/velocity order
只有 `4.142/2.305`，所以 `smooth_order_ok=false`。附近的 nonterminal
`stage02_convex_pose_velocity_0p01_z` 也能收敛，但 terminal velocity 是
`6.255e-06`，orders 是 `2.345/1.878`，没有 closed。也就是说现在不是“还没测 trajectory”的问题了：
端点 row 能关 terminal 但掉 order，稍微离开端点又关不住 terminal。

我又把最接近的 source-transport clue 推进到同一个 bounded trajectory
smoke。三条 law 对照用时 `74.1` 秒，rank 还是 `132`，
`projection_used=false`，也没有写 artifact。source-only 的
`stage02_convex_pose_velocity_0p00_sourceliftmatrixdiff_historydelta_m0p0001_z`
orders 是 `6.588/4.508`，但 max terminal velocity 是 `8.020e-12`，
超过 `1e-12` tolerance；叠加 angular-pose shift 的版本反而恶化到
`2.102e-07`，velocity order 只有 `2.820`。所以这条 source-to-velocity
transport clue 也已经是 trajectory-level negative。

我又给 source-only transport 做了三点 refinement：
`h=[0.04,0.02,0.01]` 对 `reference_h=0.005`，用时 `46.4` 秒，7/7 steps
收敛，rank `132`，`projection_used=false`。结果还是不能 accept：max
terminal velocity 仍是 `8.020e-12`，虽然 finest-h 到了 `5.904e-13`；
position/velocity order 掉到 `4.142/2.305`，和 bare endpoint row 的掉阶
一致。也就是说这不是两个 h 的偶然，而是同一个 terminal/order split。

然后我把同一 source-transport 系数再缩小 10 倍到
`stage02_convex_pose_velocity_0p00_sourceliftmatrixdiff_historydelta_m0p00001_z`。
这次三点 smoke 用时 `43.6` 秒，7/7 steps 收敛，rank `132`，
`projection_used=false`，max/finest terminal velocity 是
`8.021e-13`/`5.910e-14`，所以 terminal tolerance 关上了。但
smooth order 仍然不行，position/velocity 还是 `4.142/2.305`，
`smooth_order_ok=false`。这说明缩小 coefficient 能关 terminal，但本质上
是在逼近同一个 order-limited endpoint row。

我又测了非 projection 的 terminal-limit extrapolation：
`stage02_convex_pose_velocity_extrapolate_0p01_0p02_z`。这个比裸 `0p01`
好，是这个 family 里一个重要 trajectory 负例。默认两个 h 用时
`21.8` 秒，`projection_used=false`，terminal velocity 降到
`1.254e-07`，orders `6.412/3.775`。三点 refinement 用时 `28.9` 秒，
finest-h terminal velocity 是 `1.244e-08`，但整体 position/velocity
orders 只有 `4.054/2.364`，所以还是不能 accept。

然后我把 extrapolation 的两个点继续往 terminal endpoint 靠。默认两个 h
测 `0p005/0p01`、`0p002/0p005`、`0p001/0p002`，用时 `55.2` 秒，
`projection_used=false`，rank 还是 `132`，terminal velocity 依次降到
`3.135e-08`、`6.270e-09`、`1.254e-09`，但 velocity order 仍然只有
`4.648`、`4.566`、`4.521`。`0p001/0p002` 的三点 refinement 用时
`27.6` 秒，terminal velocity 是 `1.254e-09`，finest-h 是
`1.244e-10`，但 order 只有 `4.143/2.307`。
最后的 ultra-near `0p00001/0p00002` 确实能不用 projection 把 terminal
velocity 关到 `1.254e-13`，三点 refinement 也有
`terminal_velocity_closed=true`，finest-h 是 `1.254e-14`，但
position/velocity order 还是 `4.142/2.305`。所以现在可以排除“只要把
nonterminal extrapolation 点靠近终点就能过”的想法；它只是退化回 endpoint
row 的 closure，同时保留 endpoint row 的 order loss。

我又补了一个三点 quadratic extrapolation，不直接用 terminal row，而是用
三个严格 nonterminal 的 `stage02` convex row 做 weight=0 的 Lagrange
外推。默认两个 h 测 `0p01/0p02/0p05`、`0p005/0p01/0p02`、
`0p002/0p005/0p01`，用时 `57.0` 秒，rank `132`，`projection_used=false`。
terminal velocity 依次是 `2.029e-11`、`2.029e-12`、`2.029e-13`，但
velocity order 都还是大约 `4.508`。最好的
`stage02_convex_pose_velocity_quadextrapolate_0p002_0p005_0p01_z` 做三点
refinement，用时 `28.4` 秒，terminal velocity 过了，max `2.029e-13`，
finest-h `8.254e-15`，但 position/velocity order 仍然是
`4.142/2.305`。所以更高阶的 nonterminal extrapolation 也没有解决；
它还是 terminal-limit evidence，不是 independent full-TFE replacement。

我又补了一个 projection-like 的 terminal-tangent 诊断，只是为了排除
“给 nonterminal row 加 terminal tangent correction 就能好”的可能性。full
`stage02_convex_pose_velocity_0p01_terminalproj_z` 在 reference run 里直接
发散，residual 到 `6.739e+08`。damped 版本能收敛但更差：
`stage02_convex_pose_velocity_0p01_terminalproj_p0p1_z` terminal velocity
`7.028e-06`，orders `2.301/1.788`；
`stage02_convex_pose_velocity_0p01_terminalproj_p0p5_z` terminal velocity
`1.321e-05`，orders `2.158/1.433`。
这些 law 都是 `projection_used=true`，所以本来也不能算 accepted；现在的
结论是 damped terminal projection 这条路也排除了。

最新的 bounded JSON-only Gauss endpoint-pose velocity-predictor probe 也是
负例：7 个 local rows 用时 `28.7` 秒，rank 保持 `132`，最好的
`gauss_endpoint_pose_positive_lagrange_z` 只有 projection residual
`0.208599`，仍然是 rank-8/no-span，主要缺口变成 `lie_position_u`
fraction `0.650605`。它比 paper endpoint-pose 的 `0.117782` 还差，所以
只是排除项，不值得做 h-sweep。

剩余 Gauss endpoint-pose predictor family 也补测完了：11 个 local rows
用时 `31.5` 秒，rank 保持 `132`，最好的
`gauss_endpoint_pose_stage02_convex_0p00_z` residual 是 `0.172659`，
independent target rank 变成 `6`，但仍然 no-span；主要缺口仍是
`lie_position_u`，fraction `0.952340`。这比第一轮 Gauss endpoint-pose
好，但仍然差于 paper endpoint-pose 的 `0.117782`。

最新补的 stage-2 active translation/angular cross refinement 也是负例：
JSON-only screen 覆盖 24 个 local rows，用时 `50.9` 秒，rank 保持 `132`，
没有写 artifact，也没有跑完整 generator。最好的
`stage2_velocity_symmetric_translation_angular_cross_feature` 在 gain `1e12`
时 projection residual 只有 `0.898843`，independent target rank 仍然是
`8`，主要缺口还是 `translation_velocity_v`，fraction `0.556036`，
stage-2 fraction `0.999999`。所以简单的 active-velocity
translation/angular cross compression 也不是缺的 8-row weak closure。

最新的 non-stage-2 mean/source/history feature matrix refinement 也是
JSON-only 负例：12 个 local rows 用时 `36.5` 秒，rank 保持 `132`，
没有写 artifact，也没有跑完整 generator。最好的
`stage01_mean_velocity_diagonal_plus_row_broadcast_feature` 在 gain `1e12`
时 projection residual 改善到 `0.827381`，但 independent target rank
仍然是 `8`；主要缺口仍是 `translation_velocity_v`，fraction `0.571311`，
stage-2 fraction `0.991949`。这说明 mean/source/history feature 有一点
localization value，但仍然不是 derived full-TFE weak closure。

## 为什么不该为了四个 examples 再跑完整脚本

`run_v047.py` 是累计 audit harness 和 artifact generator，不是紧凑参考
实现。它包含很多历史尝试、负例、local tangent/capacity probes 和 full
artifact generation。当前完整 regeneration 时间约 `2386.76` 秒。

如果只是检查四个 ASME examples、paper claim、full-TFE open boundary，
应该用 read-only validators：

```bash
../.venv_sbel/bin/python validate_paper_package.py
../.venv_sbel/bin/python validate_paper_claims.py
```

或者在 pipeline 目录里：

```bash
../.venv_sbel/bin/python validate_four_asme_minimal.py
../.venv_sbel/bin/python validate_full_tfe_gap.py
../.venv_sbel/bin/python validate_full_tfe_repair_spec.py
../.venv_sbel/bin/python validate_v047_outputs.py
```

只有在改了 numerical method code 或 artifact-producing audit code 后，
才应该重新跑完整 `run_v047.py`。

## 下一步技术目标（如果继续 full-TFE replacement 方向）

下一步不是再做四个 ASME examples。它们已经过了。也不是为了窄化
Gauss6/FullVA method paper 补证明；当前 direct proof route 已经足够支撑
conditional theorem。下面这个目标只适用于继续推进更强的
`full_tfe_stage_replacement_missing` 研究方向。

具体来说，下一步是真正推 `full_tfe_stage_replacement_missing`：推导一个
revised analytical weak-row formula，或者一个 richer
nonlinear recurrent history source law，把缺的 8 个 lower-pair closure rows
放进 nonlinear stage residual。这个 candidate 需要再通过
`h=[0.04,0.02,0.01]` 对
`reference_h=0.005` 的 smooth/sharp h-sweep，才能改变当前 open gate。
