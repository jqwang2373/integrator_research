# v019 Lambda-Dependent Friction

Purpose: move closer to the paper's hardest engineering case: friction/load
terms whose Jacobian depends on the Lagrange multiplier or reaction load.

This version adds a Brown-McPhee/Stribeck-inspired pivot friction torque:

```text
N = ||lambda||
mu_eff = mu_d + (mu_s - mu_d) exp(-(||omega|| / v_s)^2)
tau_f = -c_v omega - r_f N mu_eff tanh(omega / eps) / sqrt(3)
```

The endpoint DAE residual uses this torque directly, so the rotational dynamics
depend on both angular velocity and the stage Lagrange multiplier. This is the
kind of nonlinear load where the paper's `S^3` transport and AD-friendly
Jacobian route matters.

Run:

```bash
../.venv_sbel/bin/python run_v019.py
```

Primary outputs:

- `results/v019_report.md`
- `results/summary_v019.json`
- `results/lambda_friction_order.csv`
- `results/lambda_friction_dissipation.csv`
- `results/lambda_friction_order.png`

Completed run:

- Runtime: about 15 s in `.venv_sbel`.
- Smooth lambda-friction: Gauss6 orientation order `5.410`; h=0.025 error
  `4.350e-11` versus Gauss4 `1.634e-07`, a `3.76e3x` reduction at `1.20x`
  runtime.
- Sharp lambda-friction: Gauss6 orientation order `3.911`; h=0.025 error
  `3.249e-07` versus Gauss4 `1.037e-06`, a `3.19x` reduction at `1.23x`
  runtime.
- 5s dissipation runs have zero measured positive step energy increase and
  negative stage friction power.
- Conclusion: the Gauss6/JAX quaternion endpoint candidate works beyond
  velocity-only friction and directly handles multiplier-dependent friction
  without hand Jacobians; sharp regularization still causes order reduction.
