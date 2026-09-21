# Order Acceptance Gate

This gate separates three statements that were previously too easy to mix:
the proof-level method order, the four-example mechanism coverage, and the
external same-test dynamic-order campaign.

## Accepted Method Claim

- Accepted method: `Gauss6/FullVA`.
- Method-order claim: `6`.
- Proof-level local defect: `O(h^7)`.
- Proof-level global error: `O(h^6)`.
- Smooth cylindrical-chain observed position/velocity orders:
  `7.161/7.066`.
- Comparator: local paper-style `m=3` Gauss-Lobatto TFE formula target.
- Comparator expected order: `2m-1=5`.

The method-order statement is conditional on the smooth FullVA proof contract:
a regular constrained branch, a smooth FullVA lift, a uniformly invertible
stage Jacobian, an implemented residual defect of `O(h^7)`, and an inexact
Newton compact-tube scale `eta_h^tube <= c_eta h^7`. The current implementation certificate is a
static source-identity certificate; the stronger dynamic symbolic oracle
remains open.

## Observed Order Interpretation

The smooth observed slopes `7.161/7.066` are post-theorem finite-window
consistency evidence for the sixth-order claim, not a seventh-order theorem.
The manuscript now states that these larger fitted slopes can arise from a
short smooth projected-endpoint window with a small leading sixth-order
coefficient and finest-step values near reference, nonlinear-tolerance, and
floating-point floors. The accepted
method-order claim remains `6`; claiming order above six would require a wider
asymptotic sweep with the proof-level scaled nonlinear tolerance
`eta_h^tube <= c_eta h^7`.

## Example-Level Order Boundary

| Example | Current role | Accepted order status | Evidence |
| --- | --- | --- | --- |
| `single_pendulum` | Dynamic method-order row | `accepted_order` | Absolute-coordinate driven FullVA residual, minimum observed order `6.024`. |
| `double_pendulum` | Dynamic method-order row | `accepted_order` | Double-revolute FullVA local self-reference, minimum observed order `6.089`. |
| `four_link` | Mechanism coverage row | `not_accepted_dynamic_order` | Closed-loop kinematic FullVA plus reaction dynamics, max dynamics residual `1.338e-13`. |
| `slider_crank` | Mechanism coverage row | `not_accepted_dynamic_order` | Closed-loop kinematic FullVA plus reaction dynamics, max dynamics residual `6.492e-15`. |

The four ASME-style examples are accepted as mechanism coverage under the
current method-side contract. Only `single_pendulum` and `double_pendulum`
currently support accepted dynamic method-order rows. The closed-loop
`four_link` and `slider_crank` rows verify constraints and reaction dynamics,
but their trajectory errors are at a reference or roundoff floor, so their
orders are not promoted to accepted dynamic order.

## Local Closed-Loop Coarse-Dynamics Candidate Evidence

The v048 non-oracle Newton coarse sweep gives closed-loop coarse-dynamics
candidate diagnostics for the two previously missing mechanisms
without making `1e-4` part of the default route:

- artifact:
  `v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_newton_coarse_order.json`;
- artifact filename: `closed_loop_true_dynamic_newton_coarse_order.json`;
- status: `coarse_true_dynamic_order_candidates_available_not_external_superiority`;
- step sizes: `h=[0.1,0.05,0.025]`;
- reference step: `reference_h=0.0125`;
- rows: `6/6` ok;
- stage predictor policy: `start_extrapolated_no_stage_oracle`;
- stage oracle used: `false`;
- convergence sweep run: `true`;
- closed-loop coarse-dynamics diagnostic examples: `2`;
- primary-state orders for `four_link`: `5.955/5.955/6.085/5.971`;
- primary-state orders for `slider_crank`: `6.164/6.159/7.341/6.426`;
- endpoint acceleration order is diagnostic only;
- finite-window diagnostics only;
- do not instantiate the residual-to-error implication;
- do not close P7;
- do not promote four-link or slider-crank to accepted dynamic-order examples;
- `default_1e-4_required=false`;
- `heavy_numerical_run_invoked=false`;
- `external_superiority_claim=false`.

These rows are useful local method evidence and remove the immediate need for
a heavy default `1e-4` order campaign. They do not close the external
same-test claim because the public baseline/work-precision comparison and
source-policy decisions remain separate gates. They also remain finite-window
diagnostics only: they do not instantiate the residual-to-error implication,
do not close P7, and do not promote `four_link` or `slider_crank` to accepted
dynamic-order examples.

## Coarse External Dynamic-Order Probe

The v048 closed-loop probe tests the user's large-step diagnostic path without
making `1e-4` a default run:

- step sizes: `h=[0.1,0.05,0.025]`;
- reference step: `reference_h=0.0125`;
- row status: `11/12` ok;
- one failed row: public `slider_crank`/`rA` at `h=0.1`;
- local velocity evidence rows: `2`;
- local acceleration evidence rows: `2`;
- local position-floor rows: `2`;
- accepted external dynamic-order rows: `0`;
- same-test campaign status: `not_run`;
- external superiority claim: `false`.

This means the large-step probe did not close the four-link/slider-crank
dynamic-order blocker. The next accepted-order route is either a true local
dynamic trajectory/order row for these closed-loop examples or a
reviewer-defensible residual-to-error theorem for promoting the
kinematic/reaction rows.

## Residual-To-Error Proof Route

The v048 `closed_loop_residual_to_error_theorem_obligations` gate records the
proof conditions required before small closed-loop residuals can be promoted to
accepted dynamic-order evidence. There are currently seven blocking
obligations:

- dynamic residual identity for the same local DAE trajectory map;
- `O(h^7)` residual consistency rate;
- closed-loop DAE stability or inf-sup bound;
- calibrated non-floor-limited residual-to-error estimator;
- reference-floor exclusion for position and velocity errors;
- coarse-first accepted campaign under `h=[0.1,0.05,0.025]`,
  `reference_h=0.0125`;
- manuscript theorem and proof.

Current status: `accepted_residual_to_error_theorem=false` and
`accepted_dynamic_order_count=0`. Therefore the residual surrogate is useful
planning evidence, but it is not an order proof.

## Execution Policy

The default evidence path is `coarse_first_no_default_1e-4`.
Strict public-policy `1e-4` rows are opt-in only. They may be needed to
reproduce a published table exactly, but they are too expensive to be the
routine order-gate path and they are not required for the current local
formal-order comparison.

## Allowed And Forbidden Claims

Allowed:

- `Gauss6/FullVA` has method-order claim `6` under the stated smooth FullVA
  proof contract.
- The local paper-style `m=3` Gauss-Lobatto TFE comparator has expected order
  `5`.
- The four ASME-style examples are accepted as mechanism coverage under the
  current method-side contract.

Forbidden:

- external same-test superiority is accepted;
- complete source-paper residual reproduction is accepted;
- independent full-TFE stage replacement is accepted;
- `four_link` and `slider_crank` external dynamic order is accepted;
- default `1e-4` execution is required for the current order gate.
