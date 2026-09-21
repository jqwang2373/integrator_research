# 中文 Storyboard：方法是怎么被发现的

这个文件是后续改 `main.tex`、摘要、slides 时使用的中文工作板。它不是
submission prose，也不是在讲自动写论文。它的任务只有一个：把
`Gauss6/FullVA` 这个新方法是怎样被发现的讲清楚，并且让每一段话都受到
现有 artifact 和 claim boundary 约束。

## 一句话主线

Lie-group constrained multibody integrator 难，不是因为代码长，而是因为
state 在流形上、动力学是约束 DAE、lower-pair multiplier 和 friction 会把
position/velocity/acceleration 三层一致性缠在一起。我们的 pipeline 的关键
作用不是让 LLM 写 paper，而是把 48 个版本里的正例、负例、诊断和 claim
boundary 都保留下来；最终发现的技术转折是：不要在 Gauss step 之后修补
endpoint，而要把 lower-pair velocity/acceleration consistency 放进
Gauss6 的 stage residual 里。这条路形成了 bounded 的 conditional
sixth-order `Gauss6/FullVA` method claim。

## 论文必须回答的六个问题

1. 为什么 Lie-group constrained MBD integrator 本身是一个困难科学目标？
2. 之前已有的 baseline、paper target、public-code path 分别是什么角色？
3. 我们怎样搭了一个 verifier-centered environment，让 agent 可以探索但不能乱升 claim？
4. 四个 numerical examples 分别测试什么？哪些是 dynamic-order evidence，哪些只是 mechanism coverage？
5. 48 个版本到底怎么回事？每一段失败和保留的尝试怎样改变下一步假设？
6. 真正的新方法在哪里？为什么不是普通 Gauss6、不是 Lobatto node swap、也不是 projection repair？

如果某一段不能服务这六个问题之一，就应该删除、压缩，或者挪到 AI disclosure。

## 开场叙事：先让读者相信问题真的难

第一屏/第一段不要从“LLM agent 能做 research”开始。读者要先看到 numerical-method
target 的难度。

应该写成：

- 状态变量包含 rotation，不能把 attitude 当普通 Euclidean coordinate 随便插值。
- 机械系统是约束 DAE。Position constraint 看起来满足，不代表 velocity 和
  acceleration 层也满足。
- Lower-pair joint 引入 multipliers 和 reaction forces。方法不能只输出 pose，
  还要让 constraint force 和 Newton residual 里的方程身份一致。
- Friction 是 regime-dependent 的。Smooth regularization 和 sharp regularization
  不能共享同一个 order statement。
- Newton solve 本身是方法的一部分。Residual rows、stage variables、endpoint
  policy、Jacobian backend、tolerance policy 都会改变“实际算出来的是什么方法”。
- Baseline comparison 很容易错位。Local reproduction、reduced surrogate、
  paper-style formula target、public-code same-test row 和 source-policy
  superiority 是不同证据对象。

要给读者的感觉是：这个任务不是“让 agent 写一个 integrator 然后跑 benchmark”，
而是“在很多容易误判的数值证据之间，维持 method identity”。

## 前面已经有什么：把 prior work 写成 typed comparators

Related work 不要写成普通流水账。每个已有方向都要说明它在 discovery story
里提供了什么，以及它不能单独证明什么。

| 方向 | 在故事里的角色 | 不能单独证明 |
| --- | --- | --- |
| Lie-group kinematics, RKMK, commutator-free methods | 提供 SO(3)/quaternion update 和 right-action convention。 | 不能关闭 constrained DAE dynamics。 |
| Conservative Lie midpoint/Gauss mechanics | 说明 smooth rigid-body mechanics 可以做到高阶。 | 没有 lower-pair constraints、multipliers、friction。 |
| SBEL/Negrut-style ASME examples | 提供公开机制例子和 reproducibility anchor。 | 只是 baseline/reproduction，不是 `Gauss6/FullVA`。 |
| Trapezoidal/BDF/Lobatto reduced baselines | 测试低阶、damping、endpoint-node direction 是否解释提升。 | Reduced baseline 不能证明 full absolute-coordinate lower-pair method。 |
| Paper-style Gauss-Lobatto/TFE target | 给一个强 source-reproduction 方向和 expected order comparator。 | 当前 accepted method 没有声称 complete TFE residual replacement。 |
| Brown-McPhee/friction variants | 压力测试 multiplier-dependent load 和 smooth/sharp regimes。 | Smooth/sharp order 不能合并成一个 claim。 |
| v048 same-test external harness | 组织 external comparison 的执行路径。 | 目前只能作为 scaffold/boundary，不能写成外部比较已经胜出。 |

## Environment：不是 coding loop，而是科学状态机

这一节的核心句子：

> Agent 可以提出代码和实验，但 claim promotion 必须经过 verifier；verifier
> 同时检查 method identity、problem identity、evidence artifact 和 claim wording。

应该把环境拆成五类 durable objects：

| Object | 记录什么 | 为什么重要 |
| --- | --- | --- |
| `MethodSpec` | stage variables、residual rows、endpoint policy、solver tolerance、Jacobian backend、method name。 | 防止把 projection、diagnostic residual、source target 和 accepted method 混在一起。 |
| `ProblemSpec` | mechanism、geometry、mass、driver、friction law、time window、step sizes、reference policy、metric。 | 防止不同 horizon、reference 或 friction regime 被当作同一个 test。 |
| `EvidenceSpec` | CSV、JSON、plots、reports、proof notes、PDF text、validator outputs。 | 让每个 claim 都能回到 artifact，而不是回到对话记忆。 |
| `ClaimSpec` | accepted/open/forbidden state、required validators、nonpromotion rules。 | 让负例和 caveat 也成为正式研究状态。 |
| `Ledger` | version ledger、proof ledger、pipeline audit、claim boundary、order gate。 | 让 48 个版本能被重构成 discovery history。 |

Sandbox levels 要写成 claim-control mechanism：

| Level | 用途 | 例子 |
| --- | --- | --- |
| L0 read-only audit | 只检查现有文字和 artifact 是否一致。 | 读 `CLAIM_BOUNDARY.json`、`ORDER_ACCEPTANCE_GATE.md`、compiled PDF text。 |
| L1 bounded probe | 做一个局部假设测试，但不升 ledger claim。 | 测一个 residual row variant 或 rank diagnostic。 |
| L2 full generator | 受控改 implementation 后重新生成 CSV/JSON/plot/report。 | 跑某个 version script 并更新 ledgers。 |
| L3 source-policy campaign | 严格 external/public-code comparison。 | v048/B4 类 same-test execution，需要显式 opt-in。 |

这段要强调：失败不是被删掉的失败，而是被 ledger 记录为“为什么不能这么 claim”。

## 四个 numerical examples：先定义测试环境，再讨论结果

四个 examples 不能写成“四个都证明六阶 dynamic order”。正确写法是：

| Example | 角色 | 当前证据 | 不能越界写成 |
| --- | --- | --- | --- |
| `single_pendulum` | Dynamic method-order row。 | Exact driven ASME kinematics；absolute-coordinate driven FullVA residual；minimum accepted order `6.024`。 | 不是外部 superiority row。 |
| `double_pendulum` | Dynamic method-order row。 | Double-revolute FullVA local self-reference；minimum accepted order `6.089`。 | 不是 public `1e-4` source-policy campaign。 |
| `four_link` | Mechanism coverage / closed-loop consistency row。 | Closed-loop kinematic FullVA + reaction dynamics；max dynamics residual `1.338e-13`。 | 不能升成 accepted dynamic-order example。 |
| `slider_crank` | Mechanism coverage / closed-loop consistency row。 | Closed-loop kinematic FullVA + reaction dynamics；max dynamics residual `6.492e-15`。 | 不能升成 accepted dynamic-order example。 |

建议正文里用一句边界句反复保护：

> All four examples are evidence-system mechanisms, but only the single- and
> double-pendulum rows currently carry accepted dynamic-order evidence; the
> four-link and slider-crank rows support closed-loop coverage and reaction
> consistency.

## 48 个版本怎么讲：不要列账本，要讲 hypothesis evolution

正文不要把 v001-v048 全部摊开。正文用 block table，appendix 再放 expanded
ledger。每个 block 只回答三个问题：当时在问什么、做了什么、为什么影响最终方法。

| Versions | 当时的问题 | 关键动作 | 对最终方法的影响 |
| --- | --- | --- | --- |
| v001-v003 | representation 和 public baseline 可信吗？ | SO(3) benchmark、right-action CF4/RKMK4、SBEL/Negrut rA reproduction。 | 先固定 kinematics/reproduction，再谈新 integrator。 |
| v004-v005 | clean smooth mechanics 能不能高阶？ | Yoshida-composed midpoint、Gauss-Lie4。 | 高阶 smooth mechanics 可行，但 constraints/friction 未解决。 |
| v006-v008 | constraints 能否进入 DAE solve？ | Fixed-pivot DAE、absolute-coordinate multipliers、endpoint-constrained Newton solve。 | Constraint level 和 endpoint policy 成为 method identity。 |
| v009-v012 | friction/quaternion/AD backend 是否可靠？ | Smooth/sharp friction、JAX Jacobian、S3 transport、quaternion endpoint DAE。 | Smoothness、transport、AD backend 必须分开验证。 |
| v013-v015 | Gauss6 是否是 backbone？ | Three-stage Gauss6 endpoint collocation、adaptive Gauss6/Gauss4。 | Gauss6 在 smooth regime 强，但 lower-pair/full residual 仍未关闭。 |
| v016-v018 | trapezoidal/BDF/Lobatto 能否解释结果？ | Reduced trapezoidal、Lie-BDF2、Lobatto endpoint baseline。 | 这些是 comparators，不是 accepted full method。 |
| v019-v022 | multiplier-dependent friction 能否表达？ | Lambda-dependent Stribeck、Brown-McPhee-style revolute friction。 | AD-compatible，但 reduced one-DOF surrogate 不足以关 full DAE。 |
| v023-v025 | full absolute-coordinate revolute DAE 哪里坏？ | Five-constraint DAE、direct Lobatto swap failed、projection diagnostic。 | Projection 修 drift 但改 trajectory；node replacement 不够。 |
| v026-v028 | decisive residual change 是什么？ | Stage velocity rows、stage acceleration rows、off-axis FullVA rows。 | 发现核心：把 V/A consistency 放进 stage residual。 |
| v029 | FullVA 是否超过 single joint trick？ | Double-revolute interbody PivotVA/FullVA DAE。 | FullVA generalizes，但 residual 变大，暴露 sparse-solver needs。 |
| v030-v038 | 大 residual Newton solve 能否 practical？ | Sparse diagnostics、CSR Newton、GMRES fail、colored JVP、symbolic/JVP-pruned pattern、cache。 | Sparse structure 是 scaling direction，但 speed claim 要分开。 |
| v039-v045 | lower-pair 类型和规模能否扩展？ | Triple revolute、skew-axis、prismatic、double-prismatic、row-VJP。 | FullVA/sparse diagnostics 扩展到 lower-pair types；dense 仍可能更快。 |
| v046 | 四个 ASME examples 能否进入同一个 validation anchor？ | Single/double/four-link/slider-crank rA harness。 | 给 reproducibility/mechanism context，不是新方法本身。 |
| v047 | accepted local discovery 是什么？ | Cylindrical-chain `Gauss6/FullVA`、132-row residual、smooth orders `7.161/7.066`、four-example evidence、TFE/sparse/sharp caveats。 | Accepted bounded method: conditional sixth-order `Gauss6/FullVA`。 |
| v048 | external same-test comparison 能否组织？ | Public-code/common-window comparison harness。 | 是外部比较 scaffold，不改变 method claim。 |

## 真正的新方法：从 endpoint repair 到 FullVA

这一节是 paper 的技术心脏。写作顺序应该是 narrowing argument：

1. 保留 Gauss6 backbone。v013-v015 显示 smooth high-order backbone 可行。
2. 排除“换成 Lobatto endpoint node 就够了”。v018 是 reduced baseline；
   v024 direct full Lobatto swap rank/solve 不可靠，不能成为 accepted full DAE method。
3. 排除“projection 就是方法”。v025 说明 projection 可以关 endpoint drift，
   但也会改变 trajectory accuracy，因此只能是 diagnostic/repair path。
4. 提升 stage-level V/A consistency。v026-v028 把 pivot/full velocity 和
   acceleration consistency 放进 Newton residual，而不是做 post-step repair。
5. generalize。v029 证明它不是 single-pendulum trick；后续 v030-v045 把
   correctness、sparsity、lower-pair coverage 和 runtime caveat 分离。
6. 接受 bounded claim。v047 接受 `Gauss6/FullVA` order 6，但不接受 full TFE
   replacement、sparse speed win、sharp coarse default 或 external superiority。

可以反复使用的核心句：

> The method was discovered when the search moved from repairing endpoint
> defects after a Gauss step to enforcing lower-pair velocity and acceleration
> consistency inside the Gauss6 stage residual.

中文正文可译成：

> 方法真正出现的时刻，不是 agent 又试了一个更高阶节点，而是搜索方向从
> “step 之后修 endpoint”变成了“在 Gauss6 stage residual 里同时约束
> lower-pair 的 velocity 和 acceleration 一致性”。

## 正文段落级 storyboard

### Abstract

1. 第一句：定义 hard target。Lie-group constrained MBD integrator 需要在
   manifold state、DAE constraints、multipliers/friction 和 nonlinear solve identity
   之间维持一致。
2. 第二句：定义 pipeline 角色。Pipeline 是 verifier-centered method-discovery
   environment，不是 paper-writing automation。
3. 第三句：给出 discovery result。48-version record led to conditional
   sixth-order `Gauss6/FullVA` through the endpoint-repair-to-stage-FullVA turn。
4. 第四句：给出 evidence/boundary。Single/double carry accepted dynamic-order
   rows；four-link/slider-crank provide coverage；full TFE replacement、external
   comparison、sparse speed remain bounded/open。

### Introduction

Paragraph 1：直接讲难问题。不要讲 LLM hype。用 one paragraph 把 Lie group、
DAE、lower-pair multiplier、friction、Newton solve 绑在一起。

Paragraph 2：说明为什么普通 benchmark search 不够。Numerical method 的失败
可能是 residual row identity 错、reference policy 错、projection 改了 trajectory、
或者 source-policy comparison 没闭合。

Paragraph 3：引出我们的研究设置。Agent 的任务不是一次性给出 formula，而是在
versioned verifier environment 里提出、实现、测试、保留和拒绝 method hypotheses。

Paragraph 4：给出贡献。贡献一是 method-discovery case study；贡献二是
`Gauss6/FullVA` technical turn；贡献三是 four-example evidence system with
explicit nonpromotion boundaries。

Paragraph 5：明确不是哪些事。不是自动写 paper，不是 complete source-paper TFE
replacement，不是 external same-test superiority，不是 sparse runtime win。

### Related Work and Gap

Paragraph 1：LLM-for-science / agentic research work。只用来说明为什么需要
agentic exploration，不要把主贡献放在 writing automation。

Paragraph 2：Lie-group/constrained MBD methods。说明已有 methods 解决了各自
局部问题，但 method discovery 在这里需要把 manifold update、DAE residual、
lower-pair reaction、friction 和 source-policy evidence 同时管住。

Paragraph 3：Gap。现有 work 通常报告 final method 或 final benchmark；我们报告
一个 verifier-preserved discovery path，尤其是 negative evidence 怎样排除错误
method identity。

### How the New Method Was Discovered

Paragraph 1：重申 hard target，但从 discovery 角度说：每个版本都是一个假设，
不是 prompt attempt。

Paragraph 2：介绍四个 examples 是 test environment。先讲 roles，不讲 leaderboard。

Paragraph 3：介绍 48-version block map。正文只放 compressed table；appendix 放
expanded ledger。

Paragraph 4：解释 failed attempts 的价值。Lobatto、projection、sparse、TFE
substitution、external harness 都分别告诉我们 final method 不能怎样定义。

Paragraph 5：落到技术转折。v026-v028 把 stage velocity/acceleration consistency
放进 residual，形成 FullVA；v047 接受 bounded `Gauss6/FullVA`。

### Discovery Environment

Paragraph 1：定义 durable objects：`MethodSpec`、`ProblemSpec`、`EvidenceSpec`、
`ClaimSpec`、`Ledger`。

Paragraph 2：解释 L0-L3 sandbox。重点是 claim promotion requires validators，
not conversation confidence。

Paragraph 3：解释 accepted/open/forbidden state。Open caveat 不是坏事，而是
防止把 diagnostic 升成 result。

Paragraph 4：举一个具体例子。比如 projection path：v025 改善 endpoint drift，
但 ClaimSpec 阻止它被写成 accepted method identity。

### The New Method

Paragraph 1：Gauss6 backbone。保留原因是 smooth high-order evidence 强。

Paragraph 2：Lobatto negative evidence。Reduced Lobatto 是 comparator；direct
full Lobatto swap 不闭合 full DAE method identity。

Paragraph 3：Projection negative evidence。Projection 关闭 endpoint defect，
但改变 trajectory，因此不能作为 method definition。

Paragraph 4：FullVA positive evidence。Stage-level velocity 和 acceleration
rows 进入 nonlinear residual，形成不是 post-step repair 的 consistency。

Paragraph 5：Acceptance statement。Accepted method 是 `Gauss6/FullVA`，method
order claim 是 6；observed `7.161/7.066` 是 finite-window support，不要写成
高于六阶的 theorem。

### Numerical Test Environment

Paragraph 1：四个 examples 不是同一种证据。先给 table。

Paragraph 2：Single pendulum：exact driven and full absolute-coordinate FullVA
residual，minimum order `6.024`。

Paragraph 3：Double pendulum：double-revolute FullVA self-reference，minimum
order `6.089`。

Paragraph 4：Four-link/slider-crank：closed-loop constraint/reaction consistency，
residuals `1.338e-13` 和 `6.492e-15`，但不升 dynamic-order。

Paragraph 5：说明 v048 的边界。External/common-window harness useful，但
`external_superiority_claim_allowed=false`。

### Failed Attempts as Evidence

这一节不要写成“我们也失败过”。要写成“这些失败限定了正确方法的形状”。

- Direct Lobatto swap failed：排除 endpoint-node replacement。
- Projection path partially works：排除 post-step repair as method identity。
- Full TFE substitution diagnostics remain open：说明 source-paper reproduction
  是更强目标，不是当前 accepted method 的 prerequisite。
- Sparse AD exact but not faster：把 scaling direction 和 method correctness 分开。
- Sharp friction coarse regime order-reduced：把 smooth method-order claim 和
  practical sharp regime caveat 分开。
- External same-test harness incomplete for superiority：把 table scaffold 和
  promoted external claim 分开。

### Discussion

讨论要只 generalize 到 verifier-centered method discovery，不要泛化到“LLM 能自动做科学”。

可写三点：

1. Versioned negative evidence 是科学资产。它解释为什么 final method 不是更简单的替代解释。
2. Claim-state separation 是 agentic science 的关键机制。Agent 可以加快探索，
   但 verifier 决定 claim 是否升格。
3. Method discovery 和 source-policy superiority 是不同层级。前者可以在 bounded
   local evidence 下成立；后者需要更严格外部执行和 promotion。

### Limitations

必须主动写：

- Single case study，不能代表所有 scientific domains。
- 当前 accepted method 是 conditional sixth-order `Gauss6/FullVA`，不是 universal solver。
- Full TFE stage replacement remains open。
- Sparse structure is quantified, but sparse wall-clock win is not claimed。
- Sharp-friction coarse regime remains a practical caveat。
- Four-link/slider-crank 目前是 mechanism coverage / closed-loop consistency，
  not accepted dynamic-order rows。
- External same-test superiority is not claimed。

### Conclusion

最后一段只回到 discovery：

> The important scientific result is not that an agent wrote about an integrator,
> but that a verifier-preserved 48-version search identified which residual
> identity mattered: lower-pair velocity and acceleration consistency had to be
> moved inside the Gauss6 stage solve.

## Claim wording guardrails

| 不要写 | 应该写 |
| --- | --- |
| LLM 自动写出了一个 paper。 | Verifier-centered pipeline preserved a method-discovery path。 |
| 方法就是 Gauss6。 | Gauss6 is the backbone; FullVA residual identity is the technical turn。 |
| Projection 解释了成功。 | Projection was a rejected/diagnostic repair path; accepted identity is in-residual FullVA。 |
| 四个 examples 都证明 dynamic order。 | Four examples provide mechanism coverage; single/double carry accepted dynamic-order rows。 |
| `7.161/7.066` 证明 order above 6。 | These finite-window slopes support the sixth-order claim under the stated proof contract。 |
| 完成了 source-paper TFE residual reproduction。 | Full TFE stage replacement remains open。 |
| Sparse AD 已经有 wall-clock speed win。 | Sparse structure/cost is quantified; dense `jacfwd` can still be faster。 |
| 外部比较已经证明胜出。 | v048 is an external-comparison scaffold; source-policy promotion remains open。 |

## 下一轮优化建议

1. 把这个 storyboard 压成 `main.tex` 的 8-page main narrative：优先保留
   hard target、environment、48-version compressed map、FullVA turn、four-example
   role boundary。
2. 做一张 figure：横轴 v001-v048，颜色区分 retained path、negative evidence、
   scaling diagnostics、claim-boundary checks；中心标出 v026-v028 的 FullVA turn。
3. 做一张 table：四个 examples 的 role/evidence/boundary，防止 reviewer 误读。
4. 把 abstract 和 intro 改到“method discovery first”；所有 auto-writing 相关
   只留在 disclosure。
5. 每个 result paragraph 末尾加一句最近的 nonclaim，例如“this is coverage,
   not accepted dynamic order”。
