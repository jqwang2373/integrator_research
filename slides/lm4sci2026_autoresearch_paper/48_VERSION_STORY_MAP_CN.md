# 48 个版本的中文故事地图

这个文件服务于 LM4Sci method-discovery paper 的叙事打磨。它不是实验
ledger 的替代品，也不新增 claim；它把 `version_ledger.csv` 和 `main.tex`
appendix 里的 48 个版本翻译成“方法是怎样被发现的”这条故事线。

读法：每个版本不是一次 prompt attempt，而是一个研究假设的状态转移。重要的
不是“做了很多版本”，而是每个版本怎样保留一个组件、排除一个错误解释、或者
把一个 claim 放进 accepted/open/forbidden 状态。

## 三条硬规则

1. **Prior work 是 verifier questions，不是 leaderboard**：继承的
   Lie kinematics、Gauss、ASME examples、Lobatto/TFE、friction、sparse、
   external harness 分别回答 representation trust、local validity、
   endpoint-map change、scaling、external nonpromotion 等问题。
2. **四个 examples 是 ordered ambiguity ladder**：single/double pendulum 的
   order gate 通过后，只是打开 closed-loop / mixed lower-pair 的下一层歧义；
   它不会把同一个 dynamic-order claim 自动转移给 four-link/slider-crank。
3. **v023-v029 是 FullVA three-gate filter**：v025 之后 endpoint drift 变小
   已经不够；候选必须在同一个 Gauss6 stage solve 内、以 `MethodSpec`
   residual rows 表达 lower-pair V/A consistency，并经受 off-axis/interbody
   stress 而不发生 reference-policy drift。

## 每个 version 的叙事语法

写 48 个版本时，每一版都按同一个语法理解：

```text
candidate explanation
  -> bounded implementation/artifacts
  -> verifier verdict
  -> next constraint
  -> claim-state movement
```

这比“成功/失败”更精确。失败版本也有价值，但价值必须落在一个可审计的
claim-state movement 上：

- `unknown -> reproducible`：证明测量、表示、baseline 可复用。
- `hypothesis -> backbone`：保留一个技术组件作为后续主干。
- `hypothesis -> rejected comparator`：排除一个看起来合理但错误的解释。
- `diagnostic -> open caveat`：保留有用现象，但阻止它变成 accepted claim。
- `coverage -> nonpromoted order claim`：接受机制覆盖，但不升成动态阶证明。
- `scaffold -> forbidden stronger claim`：保留 harness，但禁止 superiority claim。

所以正文里说“48 versions”时，真正要让读者看到的是：

> 每个版本都改变了下一版能问的问题；版本的科学价值来自它改变了哪个
> claim state，而不是来自它是否单独成功。

## 总体主线

1. v001-v003：先固定 Lie-group 表示和 public baseline，否则后面的误差都不可解释。
2. v004-v012：从 clean mechanics 走到 constrained/quaternion/frictional DAE，发现 constraint level 和 endpoint policy 本身就是方法身份。
3. v013-v022：确认 Gauss6 是 smooth high-order backbone，同时把 friction、baseline、source target 写成 verifier questions，而不是最终 leaderboard。
4. v023-v029：进入 full absolute-coordinate lower-pair DAE；排除 Lobatto node swap 和 projection repair，并通过 FullVA three-gate filter 发现 stage residual。
5. v030-v045：证明 FullVA residual 需要 solver/scaling 工程，但 sparse correctness 不等于 sparse speed claim。
6. v046-v048：把方法放进四个 ASME examples 和 external comparison harness，但继续阻止 overclaim。

## 版本角色分类：48 个版本不是流水账

讲这 48 个版本时，最容易失败的写法是逐条报菜名。更好的写法是先告诉读者：
每一版都承担一个 discovery role。一个版本可能失败，但只要它改变了下一步
能问的问题，它就是科学发现路径的一部分。

| 角色类型 | Versions | 这些版本在问什么 | 它们给最终方法留下什么 |
| --- | --- | --- | --- |
| Measurement / representation calibration | v001-v003 | 误差、SO(3) convention、public baseline 是否可信？ | 让后续 failure 可解释；避免把表示错误误认为方法错误。 |
| Clean high-order component search | v004-v005 | 在没有复杂 constraints/friction 时，高阶 Lie mechanics 是否可行？ | 说明高阶不是不可能；Gauss 路线比负步长 composition 更适合后续。 |
| Constraint identity discovery | v006-v012 | constrained DAE、endpoint policy、velocity/acceleration level、quaternion transport 哪些会改变方法身份？ | 把“方法”从一个公式变成 residual identity + endpoint policy。 |
| Backbone and comparator separation | v013-v022 | Gauss6、adaptive、trapezoidal/BDF/Lobatto、friction source target 各自解释什么？ | 保留 Gauss6 backbone，同时把 baseline、friction caveat、source target 分开。 |
| FullVA hinge / method identity | v023-v029 | full lower-pair DAE 中真正缺的 residual object 是什么？ | 排除 node swap 和 projection；把 V/A consistency 放进 Gauss6 stage residual。 |
| Scaling and lower-pair generality | v030-v045 | FullVA 变大后能否通过 sparse/block engineering 扩展？ | 证明 sparsity/lower-pair coverage 有价值，但不把 correctness 写成 speed claim。 |
| Reviewer-facing evidence and claim boundaries | v046-v048 | 四个 ASME examples 和 external harness 能支持哪些 claim？ | 四个 examples 形成 ordered ambiguity ladder：单/双摆给 dynamic-order evidence；four-link/slider-crank 给 coverage；external superiority 仍 open/forbidden。 |

这张角色表的用途是决定论文主文的叙事顺序。它不是 topical bins，而是 ordered
dependencies：前一块让后一块的 failure 可解释。主文不需要逐版展开，但每一段都要
能落回一个角色：先校准 measurement，再继承 baseline，再拆开 constraint identity，
再找到 FullVA hinge，最后管理 scaling、examples、external policy 的 claim 边界。

## Claim-state 视角：每个版本改变的不是同一种东西

另一个压缩 48 个版本的办法，是按 claim-state movement 来讲：

| Claim-state movement | 典型 versions | 论文里应该怎么说 | 不能怎么说 |
| --- | --- | --- | --- |
| `unknown -> reproducible` | v001-v003, v046 | 建立测量和 public-style anchor。 | 不能说这已经是新方法。 |
| `hypothesis -> backbone` | v013-v015 | Gauss6 成为 smooth high-order backbone。 | 不能说最终方法只是 Gauss6。 |
| `hypothesis -> rejected comparator` | v016-v018, v024-v025 | trapezoidal/BDF/Lobatto/projection 是重要 negative evidence。 | 不能把 projection repair 写成 method identity。 |
| `hypothesis -> method-defining component` | v026-v029 | FullVA V/A rows 进入 stage residual，是新方法的技术转折。 | 不能把 FullVA 写成 post-step projection。 |
| `diagnostic -> open caveat` | v030-v045, TFE diagnostics inside v047 | sparse/TFE/source-replacement 方向有证据，但还未 close stronger claim。 | 不能说 sparse speed win 或 full TFE reproduced。 |
| `coverage -> nonpromoted order claim` | four-link/slider-crank rows in v047 | closed-loop lower-pair coverage accepted。 | 不能说它们已是 accepted asymptotic dynamic-order examples。 |
| `scaffold -> forbidden stronger claim` | v048 | external same-test harness useful but superiority not claimed。 | 不能说 external superiority evidence。 |

这个视角直接对应 verifier：一个版本结束时，不是简单地“成功/失败”，而是把某个
claim 放进 reproducible、backbone、rejected comparator、accepted component、open caveat、
coverage、或 forbidden stronger claim 之一。

## 三层讲法：同一 48-version story 怎么压缩

同一组 48 个版本要能在不同场景下讲清楚。主文、slides、rebuttal 不应该各讲一套
不同故事，而应该共享同一个因果链，只改变展开深度。

### 30 秒版本：给 abstract / opening

> The 48 versions were not 48 prompt attempts. They were a verifier-preserved
> narrowing process: first calibrate Lie-group representation and public
> baselines, then expose constrained-DAE method identity, keep Gauss6 as the
> smooth high-order backbone, reject endpoint-node and projection explanations,
> move lower-pair velocity/acceleration consistency into the stage residual,
> and finally separate method validity from sparse speed, four-example
> coverage, TFE replacement, and external superiority.

这个版本只回答一个问题：为什么 48 versions 是 discovery evidence，而不是 trial log。

### 2 分钟版本：给 introduction / slides

| Step | Versions | 要讲给读者的因果句 |
| --- | --- | --- |
| 1. Measurement first | v001-v003 | 如果 SO(3) error、right-action convention 和 public rA anchor 不可信，后面的 order row 都不可解释。 |
| 2. Constraints make the method fragile | v004-v012 | Clean Lie/Gauss mechanics 可以高阶，但一进 constrained DAE，endpoint policy、velocity/acceleration level、friction 和 quaternion transport 都会改变 method identity。 |
| 3. Gauss6 becomes backbone, not answer | v013-v022 | Gauss6 解释 smooth high-order behavior，但 trapezoidal/BDF/Lobatto、friction source target 和 reduced surrogates 只能作为 comparator 或 boundary。 |
| 4. FullVA is discovered by rejection | v023-v029 | Full revolute DAE 暴露 endpoint velocity defects；Lobatto node swap 和 projection repair 被 verifier 拒绝；之后只有同一 Gauss6 stage solve、MethodSpec 内 V/A rows、off-axis/interbody survival 三个 gate 都通过，V/A consistency 才能被提升为 stage residual。 |
| 5. Later work manages boundaries | v030-v048 | Sparse/backend、larger lower pairs、four ASME examples 和 external harness 扩展 evidence system，但不扩大成 sparse speed、all-four dynamic order、full TFE replacement 或 external superiority claim。 |

这个版本适合主文或一页 slide。它保留了所有版本块，但不逐版展开。

### 可直接放进英文主文的 causal block narration

下面这组段落不是新的 claim，而是把 48-version map 翻成主文可用的英文句子。
它们的功能是避免主文只写“v001-v048 做了很多事”，而是逐块说明：
这个版本块排除了什么、保留了什么、如何让下一块问题变窄。

**Representation and reproducibility (v001-v003).**
The first three versions did not try to discover the final integrator. They
made later failures interpretable by fixing SO(3) error measurements,
right-action kinematic conventions, and a public-style SBEL/Negrut anchor.
Without this block, a later order defect could be a representation bug, a
baseline mismatch, or a method failure. With it, subsequent versions could ask
method questions rather than measurement questions.

**Constraint identity (v004-v012).**
The next block showed why the problem was not ordinary high-order integration.
Clean Lie and Gauss mechanics could be high order, but adding constrained DAE
structure made endpoint policy, velocity and acceleration levels, friction
smoothness, automatic-differentiation backend, and quaternion transport part of
the method identity. This block converted "which formula is high order?" into
"which residual object and problem policy are being solved?"

**Backbone and comparators (v013-v022).**
Gauss6 became the smooth high-order backbone, but this block also prevented
nearby explanations from becoming the final method. Adaptivity, trapezoidal,
BDF, reduced Lobatto, multiplier-dependent friction, and Brown--McPhee-style
surrogates each explained part of the behavior, yet each remained a comparator
or caveat rather than the accepted full lower-pair DAE method. This is why the
paper can say that the final method uses Gauss6 but is not merely Gauss6.

**FullVA hinge (v023-v029).**
The central discovery block moved into the full absolute-coordinate lower-pair
DAE. v023 exposed endpoint velocity defects; v024 rejected direct Lobatto node
replacement; v025 demoted projection because it repaired visible drift while
changing the trajectory map. The next versions moved velocity and acceleration
consistency into the stage residual and then showed that the idea survived an
interbody double-revolute system. This is the technical turn that makes the
accepted method `Gauss6/FullVA`.

The verifier did not promote smaller endpoint drift by itself. After v025, a
candidate had to pass three gates: it had to remain inside the same Gauss6
stage solve, encode lower-pair velocity/acceleration consistency as MethodSpec
residual rows, and survive off-axis or interbody stress without changing the
reference policy.

**Scaling and lower-pair breadth (v030-v045).**
After FullVA enlarged the Newton systems, the later sparse and lower-pair
versions asked whether the method could be engineered and generalized without
changing the claim. Sparse structure, CSR solves, colored JVP/VJP assembly,
block patterns, cache rules, skew-axis revolute geometry, and prismatic pairs
all produced useful coverage or diagnostics. The verifier kept these results
separate from the method-order claim: sparse correctness and lower-pair breadth
are useful, but sparse wall-clock superiority remains open.

**Evidence and claim boundaries (v046-v048).**
The final block made the paper reviewer-facing. v046 brought four ASME-style
examples into one validation anchor, v047 recorded the accepted bounded
`Gauss6/FullVA` claim and caveats, and v048 organized external same-test
comparison work. This block does not enlarge the theorem: single and double
pendulum carry accepted dynamic-order evidence, four-link and slider-crank
carry closed-loop coverage and reaction consistency, and external superiority
remains unpromoted.

### Reviewer 深答：如果被问“48 个版本到底都做了什么”

回答时先不要逐条背 v001-v048。先给 reviewer 一个分类框架：

1. **Representation/reproducibility block**：v001-v003 让 measurement 和 public anchor
   可信。
2. **Constraint-identity block**：v004-v012 证明 problem 难点不是普通 high-order
   integration，而是 constrained residual identity。
3. **Backbone/comparator block**：v013-v022 保留 Gauss6，降级低阶、Lobatto、adaptive、
   friction surrogate 等替代解释。
4. **FullVA hinge block**：v023-v029 是真正 discovery center，排除 endpoint-node /
   projection，把 velocity/acceleration rows 放进 stage residual。
5. **Boundary-management block**：v030-v048 证明 sparse/lower-pair/example/external
   方向有用，但把它们保持在 open、coverage 或 forbidden-superiority 状态。

然后只在 reviewer 追问时展开单个 block。展开格式固定为：

```text
版本块问了什么？
-> verifier 拒绝了什么解释？
-> 哪个技术组件被保留？
-> 哪个 claim 被接受、保持 open、或 forbidden？
```

这样回答可以避免两个错误：一是把 48 versions 讲成“我们试了很多次”；二是把后期
sparse/external harness 误讲成方法贡献。

## Version-by-Version Map

| Version | 当时问的问题 | 做了什么 | 发现/排除了什么 | 对下一步的影响 |
| --- | --- | --- | --- | --- |
| v001 | Lie-group 误差和 invariant 能不能稳定测？ | 建了 SO(3) prescribed rotation 和 torque-free rigid-body benchmark。 | 只建立测量环境，还没有新方法。 | 后面所有方法都可以复用稳定 error/invariant checks。 |
| v002 | right-action Lie kinematics 是否可靠？ | 修正 CF4/RKMK4 right-action 公式并验证四阶 kinematics。 | 表示和局部 Lie update convention 可以可信。 | 先固定 rotation convention，再加入 constraints。 |
| v003 | public SBEL/Negrut rA baseline 能不能复现？ | 在现代环境中复现 rA formulation，同时保留 upstream source。 | 得到 reproducibility anchor，但它不是 high-order competitor。 | 后面的 ASME examples 有了 public-style reference context。 |
| v004 | clean conservative mechanics 能否做到高阶？ | 加入 Yoshida-composed Lie midpoint。 | 可做到四阶且 invariant 好，但 negative substeps 不适合 friction/contact。 | 搜索方向转向 Gauss collocation。 |
| v005 | 不用 negative substeps 的 smooth mechanics 路径如何？ | 加入 two-stage Gauss-Legendre body-angular-velocity solve。 | smooth conservative mechanics 可以高阶，但还没有 constrained DAE。 | 下一步把 Gauss mechanics 放进 constrained setting。 |
| v006 | 高阶 Lie mechanics 能否进入 fixed-pivot DAE？ | 做 reduced fixed-pivot DAE，exact holonomic reconstruction，恢复 multipliers。 | 高阶和 constraints 可共存，但这是 reduced formulation。 | 需要 full absolute-coordinate DAE Newton solve。 |
| v007 | full absolute-coordinate stage DAE 需要哪些 constraint level？ | 加入 explicit multipliers 的 absolute-coordinate stage solve。 | 发现 position、velocity、acceleration consistency 都重要。 | endpoint projection 仍在 Newton 外，下一步要内化 endpoint。 |
| v008 | endpoint constraints 能不能放进 nonlinear solve？ | 将 endpoint algebraic variables 和 constraints 放入 54-variable Newton solve。 | projection-free fixed-pivot prototype 可行，但 Jacobian cost 变大。 | 需要更强 AD/Jacobian backend。 |
| v009 | friction 会怎样影响 order？ | 在 endpoint DAE residual 中加入 smooth/sharp regularized pivot friction。 | smooth friction 保持高阶，sharp friction order reduction。 | friction smoothness 必须成为独立变量。 |
| v010 | finite-difference Jacobian 是否成为瓶颈？ | 用 JAX `jacfwd` 替换 finite-difference Newton Jacobian。 | 与 FD 结果一致且更快，但仍是 SO(3) local-vector residual。 | 可以继续走 quaternion/source-style transport。 |
| v011 | paper-style quaternion derivative transport 是否可信？ | 独立验证 `S^3` transport operator `Pi/Theta`。 | operator bridge 成立，但还不是 integrator residual。 | 可以把 quaternion transport 放进 DAE residual。 |
| v012 | quaternion endpoint DAE 能否复现 SO(3) residual 行为？ | 用 scalar-first unit quaternion right-action update 重建 endpoint DAE。 | 匹配 SO(3) residual，保持 unit norm，但仍是四阶且 sharp-friction limited。 | 高阶候选需要 Gauss6。 |
| v013 | Gauss6 是否能成为 smooth high-order backbone？ | 加入 three-stage Gauss-Legendre sixth-order endpoint collocation。 | smooth friction 接近六阶，Gauss6 成为 backbone；sharp friction 仍受限。 | 后续要分开 smooth claim 和 sharp caveat。 |
| v014 | Gauss6 在哪些 friction smoothness 下值得用？ | 对 friction regularization width 做 sweep。 | Gauss6 在 smooth/中等 smooth 处强，near-nonsmooth 下优势变窄。 | 建立 smoothness decision boundary。 |
| v015 | near-sharp friction 能否靠 adaptivity 改善？ | 加入 embedded adaptive Gauss6/Gauss4 endpoint controller。 | near-sharp 精度可改善，但 adaptive path 不是 fixed-step method identity。 | 方法身份仍要回到 fixed residual。 |
| v016 | trapezoidal 是否可解释提升？ | 加入 favorable reduced Lie-trapezoidal baseline。 | Gauss6 在 local accuracy 上强于该 baseline。 | trapezoidal 成为 comparator，不是主路线。 |
| v017 | BDF/BLieDF 方向是否更稳？ | 加入 reduced Lie-BDF2 baseline。 | 作为 damping/robustness reference 有用，但不是 high-accuracy winner。 | BDF 留作 baseline comparison。 |
| v018 | Lobatto endpoint-node/TFE-like 方向是否就是答案？ | 做 reduced Lie-Lobatto endpoint collocation。 | reduced Lobatto 准确但慢；endpoint nodes alone 不足以解释 final method。 | 需要在 full DAE 中测试 Lobatto，而不能只看 reduced case。 |
| v019 | multiplier-dependent friction 能否进 residual？ | 加入 lambda-dependent Stribeck friction。 | AD 可以处理 reaction-load dependent nonlinear friction。 | friction/multiplier coupling 可以继续纳入 full DAE。 |
| v020 | adaptive Gauss64 能否处理 lambda-friction sharp regime？ | 将 adaptivity 与 multiplier-dependent friction 结合。 | sharp lambda-friction 精度改善，但仍是 smooth regularized model。 | 不把 adaptive 结果写成 fixed method claim。 |
| v021 | Brown-McPhee-style friction 是否可进入路径？ | 用 continuous Brown-McPhee-style velocity friction 替换简单 friction law。 | 更接近目标 friction，但仍是 fixed-pivot surrogate。 | 需要进入 paper-like revolute/full DAE。 |
| v022 | paper-like revolute Brown-McPhee benchmark 是否够？ | 做 one-DOF revolute pendulum benchmark with Brown-McPhee friction。 | 比前面更接近目标，但还是 reduced one-DOF。 | 必须进入 full absolute-coordinate index-3 revolute DAE。 |
| v023 | full absolute-coordinate revolute DAE 会暴露什么问题？ | 加入 five-constraint quaternion revolute DAE，friction scaled by reaction multipliers。 | endpoint velocity defects 和 formulation fragility 暴露。 | 需要控制 endpoint/stage velocity channels。 |
| v024 | direct full Lobatto node swap 能否关闭 full DAE？ | 在 full revolute residual 中测试 direct Lobatto endpoint-node collocation。 | rank-deficient/divergent；简单 Gauss-to-Lobatto swap 被排除。 | 新方法不能只是 endpoint-node replacement。 |
| v025 | projection repair 能否成为方法？ | 加入 SHAKE/RATTLE-style endpoint projection。 | endpoint drift 可见地改善，但 trajectory accuracy 改变。 | projection 是 diagnostic/repair，不是 method identity。 |
| v026 | velocity consistency 能不能放进 residual？ | 用 square pivot-velocity constraint residual 替换 stage r-collocation。 | endpoint velocity drift 大幅下降，不靠 post-step projection。 | 指向 in-residual velocity consistency。 |
| v027 | acceleration consistency 是否也必须进入 residual？ | 加入 pivot acceleration rows，替换 stage v-collocation。 | endpoint velocity drift 到 roundoff scale。 | velocity+acceleration residual 成为 leading repair idea。 |
| v028 | Full-axis/off-axis lower-pair consistency 是否可 enforced？ | 加入 off-axis body torque 和 hinge-axis velocity/acceleration rows。 | axis consistency 可在 residual 内 enforced；single-joint trajectory bottleneck 未完全解决。 | 下一步必须 generalize 到 interbody/multi-joint。 |
| v029 | FullVA 是否超过 single-pendulum trick？ | 做 two-body ground-plus-interbody double-revolute PivotVA/FullVA DAE。 | FullVA generalizes 到 interbody joint，但 Newton system 变成 138D。 | solver scaling/sparse Newton 成为必要分支。 |
| v030 | FullVA residual 的 Jacobian 是否有 sparse structure？ | 测量 v029 converged Newton systems 的 sparsity/conditioning/dense-vs-CSR。 | Jacobian 高度 sparse；dense AD materialization 是瓶颈。 | 进入 sparse Newton 路线。 |
| v031 | CSR sparse solve 能否进 actual Newton loop？ | 将 CSR sparse linear solves 集成到 Newton loop。 | trajectory 保持，target solve time 改善，但 dense Jacobian materialization 仍在。 | 需要 structured sparse AD 或 matrix-free。 |
| v032 | matrix-free JVP+GMRES 能否替代 dense Jacobian？ | 测试 JAX JVP 和 unpreconditioned GMRES。 | JVP 正确，但 GMRES 不收敛为默认路径。 | 需要 preconditioner/block structure，而不是 naive matrix-free。 |
| v033 | lagged Jacobian reuse 能否加速？ | 测试 reused CSR Jacobians 的 lagged sparse Newton。 | trajectory 保持，但 end-to-end speedup 不显著。 | 排除 simple lagging 作为主 scaling solution。 |
| v034 | column-colored JVP sparse assembly 是否可行？ | 用 warm-up union pattern 做 colored JVP sparse Jacobian。 | 数值匹配 dense，但小系统上更慢。 | sparse correctness 与 speed claim 分离。 |
| v035 | batched colored JVP 能否改进 sparse AD？ | 用 compiled `vmap(jvp)` 批量处理 color seeds。 | 成为 double-revolute sparse-AD backend 的较好路径，但仍依赖 dense warm-up mask。 | 需要 symbolic/block pattern。 |
| v036 | hand/block symbolic pattern 能否去掉 dense warm-up？ | 构建 conservative block-symbolic sparse pattern。 | 避免 dense discovery，但 overcolored。 | 需要 JVP pruning 细化 pattern。 |
| v037 | JVP-pruned pattern 能否恢复 exact observed pattern？ | 用 block superset 和 batched JVP dry-runs prune。 | 不 materialize dense Jacobian 也能恢复 observed pattern，但仍是 path-sampled。 | 引入 cache/reuse policy。 |
| v038 | sparse pattern 能否跨 smooth/sharp reused？ | 用一次 smooth short dry-run pattern 复用到 smooth/sharp longer solves。 | 局部可行，形成 pattern cache idea。 | 下一步 larger topology。 |
| v039 | triple-revolute larger topology 是否可行？ | 从 double-revolute 扩展到 three-body triple-revolute FullVA sparse-AD benchmark。 | 第一次 larger-topology scaling evidence。 | 需要更系统的 generated block pattern。 |
| v040 | generated block dependency 能否替代 full-matrix superset？ | 构建 generated block-dependency superset 并 pruning。 | 更接近 production sparse pattern route。 | 继续加入 cache refresh/union。 |
| v041 | pattern cache 如何处理 longer/perturbed runs？ | 加入 discover-once cache reuse 和 refresh/union policy。 | sparse-pattern reuse 更稳健。 | 可以测试 non-planar lower-pair geometry。 |
| v042 | FullVA 能否处理 skew-axis non-coplanar revolute chains？ | 将 planar/global-axis revolute 换成 parent-child skew-axis alignment。 | FullVA/sparse path 扩展到 non-coplanar lower-pair geometry。 | 下一步 non-revolute lower pairs。 |
| v043 | prismatic lower-pair 是否可进入 FullVA？ | 加入 skew-axis prismatic FullVA benchmark with sliding friction。 | 首个 non-revolute lower-pair coverage；sparse AD 正确但小系统不快。 | 需要 interbody prismatic/cylindrical。 |
| v044 | interbody non-revolute lower-pair 是否可扩展？ | 做 double-prismatic chain。 | 90-color pattern 使 sparse AD 更慢，但 trajectory correctness 保持。 | 需要 row-color/VJP 或 block assembly。 |
| v045 | row-colored VJP 能否减少 sparse seed count？ | 用 row-colored batched VJP 替换 column-colored JVP。 | seed count 降低，但仍未 beat dense `jacfwd`。 | sparse speed 被降级为 caveat，不纳入 accepted method superiority。 |
| v046 | 四个 ASME examples 能否成为 validation anchor？ | 验证 upstream SBEL/Negrut rA on single/double/four-link/slider-crank。 | 形成 four-example reproducibility harness，但不是新 `Gauss6/FullVA` 方法。 | 给 v047/v048 提供 reviewer-facing example structure。 |
| v047 | 当前 accepted local discovery 是什么？ | 建立 cylindrical-chain `Gauss6/FullVA` pipeline，132-row residual，four-example evidence，TFE/sparse/sharp caveats。 | 接受 bounded conditional sixth-order `Gauss6/FullVA`；不接受 full TFE replacement、sparse speed win、sharp coarse default、external superiority。 | 形成 paper 的主科学 claim。 |
| v048 | external same-test comparison 能否组织？ | 建立 cross-paper run-plan 和 public-code runner。 | 可组织 public/local comparison rows，但 `external_superiority_claim=false`。 | external harness 留作 scaffold，不改变 method discovery claim。 |

## 论文里怎么压缩这 48 个版本

主文不应该逐条写 48 个版本；主文应该写成五个转折：

1. **表示与复现先行**：v001-v003 先让 SO(3) update 和 public baseline 可解释。
2. **约束 DAE 让问题变难**：v006-v012 显示 endpoint、velocity、acceleration、friction、quaternion transport 都会改变 method identity。
3. **Gauss6 是 backbone，不是完整答案**：v013-v022 建立 smooth high-order backbone，但同时保留 friction/baseline/source-target 边界。
4. **FullVA turn 是核心发现**：v023-v029 排除 Lobatto swap 和 projection repair，并用 three-gate filter 把 V/A consistency 放入 stage residual。
5. **后续版本是边界管理**：v030-v048 处理 sparse scaling、lower-pair coverage、four-example validation、external harness，同时阻止 overclaim。

一句话版本：

> 48 个版本不是“试了 48 次”，而是一个 verifier-preserved narrowing process：
> 先固定表示和 baseline，再发现 DAE constraint-level 问题，保留 Gauss6 backbone，
> 排除 endpoint-node/projection 路线，最后把 lower-pair velocity/acceleration
> consistency 放进 stage residual，形成 `Gauss6/FullVA`。

## 不能从这个 map 推出的 claim

- 不能说 v001-v045 都满足后来的 four-example gate。
- 不能说 v048 已经证明 external superiority。
- 不能说 sparse AD 已经有 wall-clock speed win。
- 不能说 full source-paper TFE residual 已经 reproduced。
- 不能说 four-link/slider-crank 已经是 accepted asymptotic dynamic-order rows。
- 不能说 `7.161/7.066` 是 seventh-order theorem。
