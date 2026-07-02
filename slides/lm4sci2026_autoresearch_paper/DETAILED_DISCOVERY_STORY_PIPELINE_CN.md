# 详细发现叙事 Pipeline：从困难问题到新方法

这个文件把主线固定成一个因果叙事，而不是把 48 个版本写成流水账，也不是把
auto research 本身写成论文对象。它服务于 `main.tex`、slides、abstract 和
rebuttal draft 的反复优化。核心目标只有一个：让读者清楚看到
`Gauss6/FullVA` 是怎样被发现的。

## 总控判断

这篇 LM4Sci paper 应该讲的是：

> Lie-group constrained multibody integrator 本身很难，因为 manifold state、
> constrained DAE、lower-pair reaction、friction regime、Newton residual identity
> 和 reference policy 会互相缠绕。我们的 verifier-centered pipeline 的科学价值，
> 不是让 LLM 自动写论文，而是把 48 个版本中的成功、失败、诊断和 claim boundary
> 保存成一个可审计的发现过程；这个过程最终排除了 Lobatto endpoint swap、
> endpoint projection、full TFE replacement、sparse speed 和 external superiority
> 等替代解释，把方法收束到 stage-level FullVA velocity/acceleration rows inside
> the Gauss6 nonlinear residual。

一句更短的版本：

> 新方法不是从一次模型建议里跳出来的，而是在 verifier 持续拒绝错误 method identity
> 之后，被收束成 `Gauss6/FullVA`。

当前主文必须保留三条硬规则：

1. **Comparator-to-verifier-question**：前人方法、继承代码和 public harness 不是
   leaderboard，而是 verifier questions：representation trust、local validity、
   endpoint-map change、scaling/external nonpromotion。
2. **Ordered ambiguity ladder**：四个 numerical examples 不是单一分数榜；single
   pendulum 的 order gate 只打开下一层 ambiguity，不能把 dynamic-order claim
   转移给 four-link/slider-crank coverage gates。
3. **FullVA three-gate filter**：v025 之后 endpoint drift 变小已经不够；候选方法
   必须仍在同一个 Gauss6 stage solve 里、把 lower-pair V/A rows 放进 MethodSpec、
   并通过 off-axis/interbody 检查且不改变 reference policy。

## 读者应该按什么顺序理解

正文叙事建议按下面八步走。每一步都回答一个 reviewer 可能会问的问题。

| 顺序 | Reviewer 心里会问 | 正文必须给出的答案 |
| --- | --- | --- |
| 1 | 这个 numerical problem 为什么值得用 discovery pipeline？ | 因为 Lie-group constrained MBD 的 method identity 很脆弱；只看 error table 会掩盖 residual row、constraint level、projection、reference policy 的错位，甚至让候选方法静默变成另一条 one-step map。 |
| 2 | 前面已经有什么，为什么还需要新方法？ | 已有 Lie kinematics、conservative Gauss、ASME examples、trapezoidal/BDF/Lobatto、TFE target、friction variants、external harness；它们都是 verifier questions / typed verifier questions，不是一个已经闭合的 `Gauss6/FullVA` method。 |
| 3 | Agent 的环境到底怎么设？ | 环境不是 chat loop，而是 `MethodSpec`、`ProblemSpec`、`EvidenceSpec`、`ClaimSpec`、`Ledger` 加 L0-L3 verifier sandbox。 |
| 4 | 四个 numerical examples 是什么角色？ | 它们组成 ordered ambiguity ladder；single/double 是 accepted dynamic-order rows，four-link/slider-crank 是 closed-loop coverage/reaction consistency rows。 |
| 5 | 48 个版本为什么不是乱试？ | 每个 version 是一个 research contract：hypothesis、implementation/artifacts、verifier verdict、next constraint。 |
| 6 | 哪些失败真的改变了方向？ | Lobatto node swap、projection repair、TFE substitution、sparse backend、external harness 都变成 nonpromotion rule，而不是被删掉的失败。 |
| 7 | 真正的新方法在哪里？ | v026-v029 通过 FullVA three-gate filter：同一 Gauss6 stage solve、MethodSpec 内 lower-pair V/A rows、off-axis/interbody survival。 |
| 8 | 最终可以 claim 到哪里？ | Bounded local claim：conditional sixth-order `Gauss6/FullVA`；不 claim full TFE replacement、sparse speed win、external superiority、all-four dynamic order。 |

## 第一部分：先写困难问题，不要先写 LLM

开场应该让读者先相信这是一个真实 numerical-method discovery problem。

### 应该强调的困难

1. **Manifold state**  
   Rotation lives on SO(3) or unit-quaternion charts. A stage update can look
   numerically small while violating the intended Lie-group transport convention.

2. **Constrained DAE levels**  
   Holonomic constraints have position, velocity, and acceleration consequences.
   A method can satisfy `Phi(q)=0` while leaving `Phi_q qdot = nu` or
   `Phi_q qddot = gamma` inconsistent.

3. **Lower-pair reactions**  
   Lower-pair joints introduce multipliers and reaction forces. A method that
   only reports pose error is not enough; the reaction-dynamics residual must
   remain interpretable.

4. **Friction regime**  
   Smooth regularized friction and sharp regularized friction do not justify the
   same order statement. Smooth FullVA order and practical sharp-regime cost are
   separate claims.

5. **Newton residual identity**  
   The numerical method is not just the named quadrature rule. It is the exact
   set of stage variables, residual rows, endpoint equations, tolerances,
   Jacobian backend, and linear solve policy.

6. **Reference/comparison policy**  
   Local reproduction, source-paper TFE formula target, public-code row,
   same-window comparison, and source-policy superiority are different evidence
   objects. Mixing them creates a false conclusion.

### 开场段落的功能

开场不是说“LLM agent 很强”。开场要说：

- 这个领域里最危险的错误不是代码跑不动，而是方法身份被悄悄改掉。
- 所以 pipeline 的价值是保留 method identity 和 claim boundary。
- 48 个版本的意义，是把错误解释一个个排除掉。

## 第二部分：前面已有工作要写成 typed verifier questions

不要把 prior work 写成普通 related work 清单。每类已有东西都要回答：
它帮助我们什么？它不能单独证明什么？

| 已有对象 | 给 discovery 的帮助 | 为什么还不够 |
| --- | --- | --- |
| RKMK/commutator-free/Lie kinematics | 固定 right-action convention 和 SO(3)/S3 transport 的基本正确性。 | 只解决 kinematics，不解决 constrained dynamics。 |
| Conservative midpoint/Gauss mechanics | 证明 clean smooth rigid-body mechanics 中高阶结构可行。 | 没有 lower-pair constraints、multipliers、friction。 |
| SBEL/Negrut ASME examples and rA path | 给四个 mechanism 的 public-style anchor 和 reproducibility context。 | 它是 baseline/reproduction anchor，不是新方法本身。 |
| Trapezoidal/BDF baselines | 测试低阶 implicit/damping direction 是否足够。 | 它们不能解释 smooth high-order FullVA result。 |
| Lobatto / TFE direction | 给 endpoint-node 和 source-paper weighted-residual target。 | Reduced Lobatto 或 direct node swap 不等于 accepted full DAE method。 |
| Brown-McPhee/friction variants | 压力测试 multiplier-dependent friction and smooth/sharp regimes。 | Friction surrogate 不能替代 full lower-pair method identity。 |
| Sparse/block backend work | 说明 FullVA residual 的 scaling pressure 真实存在。 | Backend correctness/speed 是 separate claim，不定义 method order。 |
| v048 external harness | 把 public-code same-test comparison 组织成可执行 scaffold。 | 目前不能升成 external superiority。 |

这个表在正文里的作用是把“已有工作”接到“为什么需要 48-version search”：
每个 comparator 都解决一部分，但没有一个能单独保证最终 method identity。

### 从 prior work 到 48-version search 的桥

这部分要避免写成“我们读了很多相关工作”。更准确的说法是：

> Prior work initialized the search constraints. Some inherited work fixed the
> representation and measurement convention; some provided clean high-order or
> low-order baselines; some became plausible but rejected explanations; and some
> set comparison boundaries that the final claim was not allowed to exceed.

可以按四类来讲：

| Prior role | 对应版本块 | 它带来的约束 |
| --- | --- | --- |
| Representation/reproducibility anchors | A: v001-v003 | 先证明 SO(3)/right-action/error measurement/public rA anchor 可复现，否则后面所有 order row 都不可信。 |
| Clean mechanics and local baselines | B-D: v004-v018 | 证明高阶 Gauss/Lie mechanics 可行，同时把 trapezoidal/BDF/Lobatto 降为 comparator 或 rejected shortcut。 |
| Full lower-pair stressors | E-F: v019-v029 | friction、multiplier、full revolute DAE、projection failure 共同逼出 stage-level FullVA V/A residual。 |
| Scaling/external-policy boundaries | G-I: v030-v048 | sparse/backend、four-example harness、external same-test matrix 组织证据，但不定义 method order 或 superiority。 |

正文里一句压缩版：

> The inherited literature and code base did not provide the final method; it
> provided the typed constraints under which wrong explanations could be ruled
> out.

## 第三部分：环境设置要写成 verifier state machine

正文不要写成“agent 写代码、跑实验、看结果”。应该写成：

> The agent can propose and implement hypotheses, but the verifier controls
> claim promotion.

### 五个 durable objects

| Object | 必须记录 | 防止什么错误 |
| --- | --- | --- |
| `MethodSpec` | method name, stage variables, residual row families, endpoint policy, tolerance, AD/backend policy。 | 防止把 Gauss6、projection、TFE probe、FullVA residual 混成同一个 method。 |
| `ProblemSpec` | mechanism, geometry, mass/inertia, driver, friction law, time horizon, step sizes, reference, metric。 | 防止不同 problem/window/reference 被当作同一个 evidence row。 |
| `EvidenceSpec` | CSV/JSON/PNG/report/PDF/proof note/validator output。 | 防止 claim 只依赖对话记忆或单个截图。 |
| `ClaimSpec` | accepted/open/forbidden, required validators, nonpromotion rule, exact wording。 | 防止 diagnostic 结果被写成 theorem 或 superiority claim。 |
| `Ledger` | version ledger, proof ledger, audit, claim boundary, order gate。 | 让 48 versions 可以被重构和审计。 |

### 环境设置的三把锁

这部分在正文里要写得像实验设计，而不是像 workflow 说明。

| Lock | 固定什么 | 为什么重要 |
| --- | --- | --- |
| Identity lock | stage variables、residual row families、endpoint equations、tolerance、backend policy。 | 保证每次 promote claim 时，真正测试的是同一个 one-step map。 |
| Evidence lock | 每个 example 的 `ProblemSpec`、reference policy、step-size set、CSV/JSON/plot/report/proof bundle、gate role。 | 保证更复杂的 mechanism 不会自动变成更强 theorem。 |
| Claim lock | 允许写进论文的 claim wording、nonpromotion rule、accepted/open/forbidden state。 | 允许 numerical run 增加 evidence，但不一定扩大 public claim；也允许 stale prose 被降级。 |

最关键的表达：

> A failed run is useful only if the environment can say which lock failed.
> The verifier returns a typed next constraint rather than a hidden score:
> method identity failure leads to a new residual constraint; evidence failure
> leads to a new artifact/reference constraint; claim failure leads to demotion
> or forbidden wording, not to deletion.

### 四层 sandbox

| Level | 能做什么 | 不能做什么 |
| --- | --- | --- |
| L0 read-only audit | 读 artifact、扫 stale wording、检查 PDF/text/claim boundary。 | 不改变 numerical evidence。 |
| L1 bounded probe | 对一个 local hypothesis 做小规模 diagnostic。 | 不把结果直接升成 paper claim。 |
| L2 full generator | 受控改 implementation 并生成 CSV/JSON/plots/report。 | 不跳过 ledger/proof/audit 同步。 |
| L3 source-policy campaign | 跑 public-code/external same-test policy。 | 没有 opt-in 和完整 policy 时不 claim superiority。 |

### 失败如何变成下一版约束

这条规则是 story 的核心之一：

| 失败类型 | 下一版必须怎么变窄 | 例子 |
| --- | --- | --- |
| Method identity mismatch | 直接测试缺失 residual row 或 stage variable。 | v025 projection 被降级，v026-v027 把 V/A rows 放进 residual。 |
| Reference drift | 先冻结 `ProblemSpec` 和 reference policy。 | v046 rows 保留为 diagnostic；double pendulum 用 method-side FullVA self-reference。 |
| Proof/artifact incomplete | 放入 proof/diagnostic lane，不升 accepted claim。 | `7.161/7.066` 支持 sixth-order claim，但不是 seventh-order theorem。 |
| Coverage without order theorem | 接受 coverage，不接受 dynamic-order promotion。 | four-link/slider-crank 是 mechanism coverage/reaction consistency。 |
| Backend/source-policy caveat | 把 method validity 和 speed/superiority 分开。 | sparse exactness useful，但 sparse speed win/open；v048 scaffold useful，但 superiority/open。 |

## 第四部分：四个 numerical examples 是 test environment

这四个 example 的写法必须防止一个常见误读：它们不是四个等价的 order proof。

| Example | Verifier gate | 它测试什么 | 当前证据 | 可以 claim | 不能 claim |
| --- | --- | --- | --- | --- | --- |
| `single_pendulum` | Clean dynamic-order gate | 最干净的 driven lower-pair FullVA dynamic-order row。 | Exact driven ASME kinematics；absolute-coordinate driven FullVA residual；minimum accepted order `6.024`。 | Local dynamic-order evidence。 | External superiority。 |
| `double_pendulum` | Interbody transfer/order gate | FullVA 是否能穿过 interbody double-revolute joint 和 self-reference policy。 | Double-revolute FullVA local self-reference；minimum accepted order `6.089`。 | Local dynamic-order evidence under accepted policy。 | Public `1e-4` source-policy row。 |
| `four_link` | Closed-loop coverage/reaction gate | Closed-loop mechanism mapping、constraint graph、reaction-dynamics consistency。 | Closed-loop kinematic FullVA plus reaction dynamics；max dynamics residual `1.338e-13`。 | Mechanism coverage and reaction consistency。 | Accepted asymptotic dynamic-order row。 |
| `slider_crank` | Mixed lower-pair coverage/reaction gate | Prismatic/revolute closed-loop mapping and reaction consistency。 | Closed-loop kinematic FullVA plus reaction dynamics；max dynamics residual `6.492e-15`。 | Mechanism coverage and reaction consistency。 | Accepted asymptotic dynamic-order row。 |

正文可反复使用的边界句：

> The four examples form an evidence ladder, not four identical order proofs:
> single and double pendulum carry accepted dynamic-order evidence; four-link
> and slider-crank currently certify closed-loop coverage and reaction
> consistency.

更短的 verifier 说法：

> The examples are selected by the ambiguity they can expose: clean order,
> interbody transfer, loop closure, and mixed lower-pair coverage.

更像 discovery pipeline 的说法：

> A failed rung returns a typed next constraint--method order, reference policy,
> loop closure, or lower-pair coverage--rather than one generic pass/fail score.

## 第五部分：48 个版本应该解释成 hypothesis evolution

48 个版本不要写成“我们试了 48 次”。应该写成：

> 每个 version 是一个 research contract：提出一个 candidate explanation，生成
> bounded artifacts，接受 verifier verdict，然后把 verdict 转成 next constraint。

更细一点，每个 version 的叙事语法是：

```text
candidate explanation
  -> bounded implementation/artifacts
  -> verifier verdict
  -> next constraint
  -> claim-state movement
```

最后一项很重要。版本不是二元成功/失败，而是在改变 claim state：例如
`unknown -> reproducible`、`hypothesis -> backbone`、`hypothesis -> rejected
comparator`、`diagnostic -> open caveat`、`coverage -> nonpromoted order claim`、
或 `scaffold -> forbidden stronger claim`。这就是为什么 failed version 不能删；
它们告诉读者哪个解释已经不再可用。

### 四个同时演化的东西

1. **Method identity evolves**  
   从 SO(3) update，到 Gauss endpoint DAE，到 quaternion DAE，到 Gauss6，
   到 PivotVA/FullVA lower-pair residual。

2. **Problem identity evolves**  
   从 prescribed kinematics，到 fixed pivot，到 frictional revolute，到 interbody
   lower-pair chains，到 four ASME examples 和 external same-test scaffold。

3. **Evidence identity evolves**  
   从 simple error/order tables，到 CSV/JSON/plots/report/proof/audit/claim boundary。

4. **Claim identity evolves**  
   从 “this candidate looks good” 到 accepted/open/forbidden state:
   method validity, dynamic order, coverage, sparse speed, TFE replacement, external
   superiority are separated.

### 48-version block story

| Block | 版本 | Discovery role | 最终留下的知识 |
| --- | --- | --- | --- |
| A | v001-v003 | Measurement and reproducibility calibration。 | 先锁定 SO(3) measurement、right-action convention、public baseline reproducibility。 |
| B | v004-v005 | Clean high-order mechanics。 | 高阶 Lie/Gauss mechanics 在 clean smooth setting 可行。 |
| C | v006-v012 | Constraint and representation identity。 | Constraint levels、endpoint policy、friction、AD Jacobian、S3 transport 都会改变 method identity。 |
| D | v013-v018 | Backbone/comparator separation。 | Gauss6 是 strong smooth backbone；trapezoidal/BDF/Lobatto 是 comparator 或 rejected shortcut。 |
| E | v019-v025 | Full revolute DAE stress and failed repairs。 | Multiplier-dependent friction 可表达；direct Lobatto swap 和 projection repair 都不是 accepted method identity。 |
| F | v026-v029 | FullVA hinge。 | Stage-level velocity/acceleration consistency inside residual 是真正的新方法转折。 |
| G | v030-v038 | Sparse/scaling diagnostics。 | FullVA residual has real sparse structure, but speed/backend is separate from method validity。 |
| H | v039-v045 | Larger and non-revolute lower-pair coverage。 | FullVA/sparse diagnostics extend beyond one planar revolute setup, but sparse win remains caveat。 |
| I | v046-v048 | Reviewer-facing evidence and claim boundary。 | Four-example evidence system and external scaffold become controlled claim-boundary artifacts。 |

### 为什么 v026-v029 是核心转折

- v023 shows the full absolute-coordinate revolute DAE is the real stress test.
- v024 shows direct Lobatto endpoint-node swap fails as a simple explanation.
- v025 shows projection repairs endpoint drift but cannot define the method.
- v026 moves pivot velocity consistency into the stage residual.
- v027 moves pivot acceleration consistency into the stage residual.
- v028 expands the residual toward off-axis FullVA constraints.
- v029 shows PivotVA/FullVA survives an interbody double-revolute DAE.

这段应该成为 paper 的 technical center，而不是被 sparse/backend 或 external comparison
淹没。

## 第六部分：真正的新方法怎么说

正确表述：

> `Gauss6/FullVA` is Gauss6 collocation with lower-pair velocity and acceleration
> consistency enforced as stage-level residual rows. The discovery was not that
> Gauss6 is useful, but that the lower-pair V/A rows must be inside the nonlinear
> stage solve rather than repaired at the endpoint.

中文口述版：

> 我们最终发现的不是“Gauss6 比较好”这么简单。Gauss6 只是 backbone。真正的新
> method identity 是 FullVA：lower-pair 的 velocity 和 acceleration 一致性必须
> 在 stage residual 里解出来，而不是在一步结束之后 projection 修补。

## 第七部分：每一节该承担什么任务

| Section | 必须完成的叙事任务 | 不该做的事 |
| --- | --- | --- |
| Abstract | 一句话 hard problem，一句话 verifier pipeline，一句话 48-version FullVA discovery，一句话 boundary。 | 不要把 paper writing 放进中心。 |
| Introduction | 让读者先相信 problem hard；再说为什么 verifier-centered discovery 有意义。 | 不要从 LLM hype 开始。 |
| Related Work | 把 prior work 写成 typed verifier questions。 | 不要把所有 baseline 写成一个 leaderboard。 |
| How Discovered | 定义 version，给 48-version block map，解释每个 block 做什么，再解释 failure-to-constraint。 | 不要逐条复述 appendix 成流水账。 |
| Discovery Environment | 定义 MethodSpec/ProblemSpec/EvidenceSpec/ClaimSpec/Ledger 和 L0-L3。 | 不要写成 generic agent loop。 |
| New Method | 集中讲 v023-v029，特别是 v026-v028 FullVA hinge。 | 不要让 sparse/external/TFE open paths 抢主线。 |
| Numerical Examples | 把四个 examples 写成 evidence ladder。 | 不要说 all four prove dynamic order。 |
| Failed Attempts | 把失败写成 nonpromotion rules。 | 不要写成“我们也失败过”的附带故事。 |
| Discussion | 只 generalize 到 verifier-centered method discovery。 | 不要 generalize 成 LLM 自动做科学或自动写论文。 |

## 第八部分：主文逐段 playbook

这一节是给反复改 `main.tex` 用的。压缩、改标题、改 LM4Sci framing 时，可以换
句子和长度，但不要改变段落角色的顺序：hard problem -> inherited comparators ->
verifier setup -> four-example test environment -> 48-version evolution ->
48-version block meaning -> FullVA technical turn -> claim boundary。

| 主文位置 | 段落功能 | 必须说 | 不能说 | 当前锚点 |
| --- | --- | --- | --- | --- |
| Abstract opening | 让读者第一眼看到 numerical-method target。 | Lie-group constrained MBD 难在 manifold、index-3 constraints、friction/multipliers、residual identity、reference policy，并按 dependency chain 提前交代 typed verifier questions、verifier testbed、48-version ledger、FullVA hinge、boundary。 | 不要先讲 LLM 自动写论文，也不要把 artifact count 当贡献。 | `main.tex:60-83` |
| Introduction P1 | 解释为什么普通 benchmark iteration 不安全。 | Method identity 不只是 update formula；projection、surrogate、reference policy 都会改变 claim。 | 不要把 clean convergence plot 写成充分证据。 | `main.tex:88-99` |
| Introduction P2 | 把 agent 的价值和危险一起说清楚。 | Agent 能探索，但 claim drift 是核心风险；verifier 必须控制 promotion。 | 不要写成 agent 能自动替代 domain judgment。 | `main.tex:101-109` |
| Inherited comparators | 说明前人工作和代码如何进入 search。 | Inherited work 是 verifier questions / typed verifier questions：representation trust、local validity、endpoint-map changes、scaling/external nonpromotion。 | 不要把它们合成一个 leaderboard。 | `main.tex:111-118`, `main.tex:171-220` |
| Verifier/testbed introduction | 第一次交代环境如何防 claim drift。 | Method/problem/evidence/claim/ledger objects；four examples 是 test environment。 | 不要把四个 examples 写成四个同类 order proofs。 | `main.tex:120-128` |
| 48-version narrowing intro | 在 introduction 中给一眼能懂的 causal chain。 | 五块收束：representation locks、DAE identity、Gauss6/comparators、FullVA hinge、claim boundaries。 | 不要说“试了很多次最后成功”。 | `main.tex:130-139` |
| LLM-for-science bridge | 把 LM4Sci 目标接到本 case，但必须在 numerical-method dependency 之后。 | 只说我们研究一个 narrow scientific-computing case。 | 不要把 paper writing/formatting 变成科学对象，也不要放到 inherited comparators 之前。 | `main.tex:141-151` |
| Contribution paragraph | 把 paper 定义成 method-discovery case study。 | 三个贡献：conditional sixth-order `Gauss6/FullVA`、stage-level FullVA residual、verifier-preserved failed alternatives。 | 不要说 generic prompt recipe、auto research paper writing、external superiority。 | `main.tex:153-168` |
| Story contract | 明确告诉 reviewer 文章按什么顺序读。 | 七问顺序：hard problem、prior work、verifier setup、four examples、48-version evolution、version-block meaning、technical move。 | 不要把 broader agentic-science implication 提前。 | `main.tex:255-276` |
| Hard-problem paragraph | 把 discovery section 拉回 numerical analysis。 | 失败类型要分开：different one-step map、projection damage、wrong residual、wrong reference。 | 不要只说“这是复杂系统”。 | `main.tex:279-290` |
| Inherited-baseline paragraph | 把 prior work 压缩成 typed verifier-question memory，并连到 ledger shape。 | local reproduction、reduced baseline、endpoint surrogate、source-policy comparison 不能 close 同一个 claim；representation anchors -> v001-v003，reduced/endpoint alternatives -> v013-v025，external harnesses -> v046-v048。 | 不要让 Lobatto/TFE 听起来已经被完整复现。 | `main.tex:292-302` |
| Verifier setup paragraph | 解释 agent 环境的最小可读版本。 | 每个 run 带 MethodSpec、ProblemSpec、EvidenceSpec、ClaimSpec、ledger 和 verdict-to-next-constraint。 | 不要写成 generic chat loop。 | `main.tex:304-310` |
| Four-example paragraph | 在 discovery section 中先锁定 claim type。 | Four examples 是 ordered ambiguity ladder；每个 rung 返回 gate-specific verdict，不是 hidden score。 | 不要让复杂 mechanism 自动继承 order claim。 | `main.tex:312-321` |
| Version grammar paragraph | 定义“version”而不是列流水账。 | Version = candidate explanation + artifacts + verifier verdict + next constraint + claim-state movement；主文还明确 retention verbs：calibrate measurement、reject explanation、promote component、quarantine caveat。 | 不要写成 prompt attempts 或 hyperparameter samples。 | `main.tex:323-338` |
| Discovery spine/table | 给读者压缩的 48-version map。 | 至少保留一个 visual/table 显示 A-I role map 和 FullVA hinge。 | 不要只留 appendix 的 v001-v048 列表。 | `main.tex:340-414` |
| Failure-to-constraint trace | 用 v023-v029 展示 discovery mechanism。 | Lobatto node swap 和 projection 被拒绝；V/A rows 进入 stage residual。 | 不要把 projection 描述成 accepted method。 | `main.tex:419-432` |
| Discovery Environment | 展开 verifier 怎么控制 promotion。 | Promotion checklist、identity/evidence/claim locks、per-example gate roles、verdict-to-constraint table、L0-L3 sandbox。 | 不要让 validator 看起来替代 proof。 | `main.tex:436-549` |
| New Method | 技术中心。 | Gauss6 是 backbone；new method 是 stage-level lower-pair V/A consistency inside residual；v026-v029 必须读成 FullVA three-gate filter。 | 不要让 sparse/backend/external harness 抢主线。 | `main.tex:561-624` |
| Numerical Examples | 证据边界。 | Single/double local dynamic order；four-link/slider-crank coverage and reaction consistency。 | 不要 claim all-four accepted asymptotic dynamic order。 | `main.tex:627-685` |
| Claim snapshot and close | 防 overclaim，并把失败写成 verifier rules。 | Accepted/open/forbidden states；limitations；failed paths as nonpromotion rules。 | 不要 claim full TFE replacement、sparse speed、external superiority、seventh-order theorem。 | `main.tex:688-759` |

### 段落级压缩规则

如果之后必须压到 8 页，优先压缩每个段落里的解释长度，而不是移动段落顺序。可以把
story contract 合成一句、把 durable objects table 合成 prose、把 sparse/external 细节移到
appendix，但必须保留三个锚点：

1. `Verifier setup` 必须出现在 four-example testbed 之前。
2. `What a version means` 必须出现在 48-version figure/table 之前。
3. `FullVA hinge` 必须出现在 sparse/backend/external discussion 之前。

## 第九部分：一口气完整中文叙事稿

这一节是给写 abstract、introduction、slides opening、和 reviewer response 时使用的
连续叙事版本。它不替代主文结构，也不新增 claim；它的作用是校准整篇 paper 是否
始终在讲“新方法是怎么被发现的”。

**第一段：困难问题。**  
我们研究的不是一个普通 benchmark，也不是简单比较哪个 integrator error 更小。
Lie-group constrained multibody integration 难在 method identity 本身很脆弱：
rotation state 在 manifold 上，mechanical equations 是带 position/velocity/
acceleration consequence 的 constrained DAE，lower-pair joints 会引入 multipliers
和 reaction forces，friction smoothness 会改变可声明的 order，而 Newton solve 中
到底有哪些 stage variables、residual rows、endpoint equations、tolerance 和
backend policy，都会改变实际被求解的一步映射。也就是说，一个漂亮的 convergence
plot 可能来自 projection、surrogate、reference-policy drift，或者一个 diagnostic
residual，而不是来自我们声称的新方法。

**第二段：已有工作和继承对象。**  
这个项目不是从空白开始，也不是从一个干净 leaderboard 开始。我们继承了
right-action Lie kinematics、clean conservative Gauss/Lie mechanics、
SBEL/Negrut-style ASME examples、trapezoidal/BDF/Lobatto baselines、
Gauss-Lobatto/TFE source target、Brown--McPhee/friction variants、sparse/backend
diagnostics、以及 external same-test harness。它们的角色不是同一种 baseline。
有的固定 representation，有的提供 clean high-order 可能性，有的是 lower-order
或者 endpoint-node alternative，有的是 source-policy 或 external-comparison
边界。论文必须把它们写成 typed verifier questions：它们帮助约束 search，但没有一个
可以单独证明最终的 `Gauss6/FullVA` claim。

**第三段：为什么需要 verifier 环境。**  
正因为已有对象很多，agent 很容易把不同 evidence 类型混在一起。我们的环境设置
不是 generic chat loop，而是一个 verifier state machine。每个 run 都带有
`MethodSpec`、`ProblemSpec`、`EvidenceSpec`、`ClaimSpec` 和 ledger：它记录
解的是哪个 residual，机制和 reference policy 是什么，哪些 CSV/JSON/plot/report/
proof artifact 存在，当前文字允许 claim 到哪里，以及 verifier verdict 怎样约束
下一版。Agent 可以 propose hypothesis、写代码、跑 bounded experiments，但不能
自己把 diagnostic 升成 accepted method；claim promotion 必须通过 method identity、
problem identity、evidence artifact、wording boundary 这些 gate。

**第四段：四个 numerical examples 是 test environment。**  
四个 ASME examples 的作用也不是四个等价 demo。它们是 verifier-controlled test
environment。single pendulum 是 clean exact-driven lower-pair dynamic-order gate；
double pendulum 测试 FullVA 能不能穿过 interbody double-revolute joint 和
self-reference policy；four-link 测试 closed-loop lower-pair graph、rank、
kinematic closure 和 reaction consistency；slider-crank 测试 mixed revolute/
prismatic closed loop 和 reaction residual。当前 claim 必须分开：single/double
提供 accepted local dynamic-order evidence；four-link/slider-crank 提供 coverage
and reaction-consistency evidence，但不提供 accepted asymptotic dynamic-order row。

**第五段：48 个版本不是流水账。**  
在这个环境里，一个 version 不是一次 prompt attempt，也不是一个 hyperparameter
sample。一个 version 是 research contract：candidate explanation ->
bounded artifacts -> verifier verdict -> next constraint -> claim-state movement。
v001-v003 先让 SO(3) measurement、right-action convention 和 public anchor 可信；
v004-v012 证明 clean high-order mechanics 一旦进入 constrained/frictional/
quaternion DAE，endpoint policy、constraint level、friction regime 和 transport
都会成为 method identity 的一部分；v013-v022 保留 Gauss6 作为 smooth high-order
backbone，同时把 adaptive、trapezoidal、BDF、Lobatto、friction surrogate 和
source target 降级为 comparator 或 caveat。

**第六段：技术转折。**  
真正的新方法不是“试了 Gauss6 后成功”。Gauss6 只是 backbone。v023 把问题推进到
full absolute-coordinate lower-pair DAE，并暴露 endpoint velocity defects；v024
证明 direct Lobatto endpoint-node swap 不是答案；v025 证明 projection 可以修补
可见 drift，但会改变 trajectory map，因此不能作为 method identity。于是下一版
约束变窄：v026 把 velocity consistency 移入 stage residual，v027 把 acceleration
consistency 也移入 stage residual，v028 扩展到 off-axis lower-pair rows，v029
证明 PivotVA/FullVA survives an interbody double-revolute DAE。这个 v026-v029
block 才是 discovery center：被接受的不是“某个 nonlinear solve residual 很小”，
而是这些 position/velocity/acceleration rows 属于同一个 MethodSpec；lower-pair
velocity/acceleration consistency 必须
inside the Gauss6 nonlinear residual。

**第七段：后续版本管理边界，而不是改写贡献。**  
v030-v045 之后的 sparse、block、cache、skew-axis、prismatic、row-colored VJP
工作很重要，但它们的作用是管理 scaling 和 lower-pair breadth，不是把 method
claim 改成 sparse speed superiority。v046-v048 把 four-example harness 和 external
same-test comparison 组织起来，给 reviewer-facing evidence system 和未来比较
路径，但也同时固定边界：external superiority 不 claim，full TFE replacement 不
claim，sparse wall-clock speed win 不 claim，four-link/slider-crank dynamic order
不 claim，`7.161/7.066` 也只支持 conditional sixth-order claim，而不是 seventh-order
theorem。

**第八段：一句话收束。**  
所以这篇 paper 的核心不是“LLM 自动做研究”或“LLM 自动写论文”。核心是：
在一个很容易发生 claim drift 的 numerical-method search 中，verifier-centered
agent pipeline 保存了 48 个版本里被保留和被拒绝的技术路径，最终把方法身份收束到
conditional sixth-order `Gauss6/FullVA`：stage-level lower-pair velocity and
acceleration residual rows inside the Gauss6 nonlinear solve。这个发现路径本身，
包括失败和 nonpromotion rules，是 paper 最应该讲清楚的科学对象。

## 第十部分：反复优化时的检查表

每次改 `main.tex` 前后都检查：

1. 第一屏是否先讲 hard Lie-group integrator，而不是先讲 LLM？
2. Prior work 是否被写成 verifier questions / typed verifier questions，而不是散乱 related work？
3. Verifier environment 是否明确控制 claim promotion？
4. 四个 examples 是否先被定义成 ordered ambiguity ladder / test environment？
5. 48 versions 是否被解释成 hypothesis evolution？
6. v026-v029 是否仍然是 FullVA three-gate filter 的技术中心？
7. FullVA 是否被写成 in-residual stage V/A consistency，而不是 output projection？
8. `7.161/7.066` 是否只支持 sixth-order claim，而不是 higher-order theorem？
9. Four-link/slider-crank 是否没有被写成 accepted dynamic-order rows？
10. TFE replacement、sparse speed、external superiority 是否仍然 open/forbidden？

如果某段文字不能通过这些问题，它应该被压缩、移动到 appendix，或者删除。

## 可以直接复用的 transition sentences

- "The difficult part is not proposing another quadrature rule; it is preserving
  the identity of the residual being solved."
- "We therefore treat inherited numerical methods as typed verifier questions rather
  than as a single leaderboard."
- "We treat inherited methods as verifier questions, not a leaderboard."
- "A version is not a prompt attempt. It is a bounded research contract with a
  hypothesis, artifacts, a verifier verdict, and a next constraint."
- "The four mechanisms form an evidence ladder, not four interchangeable demos."
- "Passing an order gate opens the next ambiguity; it does not transfer the
  same claim type to a coverage gate."
- "Projection closed a visible symptom, but the verifier rejected it as the
  method identity."
- "After v025, endpoint drift reduction was no longer sufficient; the candidate
  had to live inside the same Gauss6 stage solve as lower-pair V/A rows in the
  MethodSpec."
- "The accepted turn was to move lower-pair velocity and acceleration
  consistency into the Gauss6 stage residual."
- "The strongest paper is not the broadest claim; it is the claim whose
  promotion path can be reconstructed."
