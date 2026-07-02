# TFE(m=3) Scope Exclusion Audit

Method: `tfe2026_TFE_m3_GL`.
Failed example: `four_link`.
Source-backed exclusion: `True`.
Required accepted matrix excludes method: `True`.

TFE(m=3) Gauss-Lobatto is not counted as a required accepted four-example baseline because the original paper validates a single revolute-pendulum setting, explicitly reports DAE order loss for m=3, and the local four-link wrapper gives rejected negative-order evidence rather than convergence.

| Source | evidence | status | interpretation |
|---|---|---|---|
| `s11044-026-10153-w.txt` | `paper_numerical_scope` | `single_revolute_pendulum_scope` | The original TFE paper's numerical experiments use a single revolute-pair pendulum with friction/frictionless variants, not the ASME four-link benchmark. |
| `s11044-026-10153-w.txt` | `paper_order_caveat` | `paper_reports_m3_order_loss` | The paper states that the DAE TFE(m=3) implementation reaches only fourth-order accuracy rather than the ideal fifth-order ODE result, and attributes this to DAE stiffness/truncation effects. |
| `results/tfe_m3_four_link_solver_audit.csv` | `local_four_link_failure` | `not_accepted_on_four_link` | The local wrapper executes on single, double, and slider examples, but the four-link row fails strict reference solves and shows negative common-reference orders on the coarse h sweep. |
| `results/tfe_m3_four_link_common_reference_smoke.csv` | `negative_order_evidence` | `exclude_from_required_four_example_accepted_matrix` | The m=3 four-link row is a rejected out-of-scope stress test of the paper formula, not a missing required accepted baseline. The accepted original-paper comparison uses Newmark-beta, trapezoidal, TFE(m=1), and TFE(m=2), plus the m=3 rows that run on the remaining examples as diagnostic evidence. |
