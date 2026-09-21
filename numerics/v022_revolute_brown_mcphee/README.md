# v022 Revolute Brown-McPhee Benchmark

Purpose: move closer to the paper's revolute-pendulum benchmark while keeping
the version small and reproducible.

The model is a one-DOF revolute pendulum:

```text
I qddot = -m g L sin(q) + tau_f(qdot, ||lambda(q, qdot, qddot)||)
p(q) = exp(e_y q / 2)
```

The Brown-McPhee friction torque is continuous in velocity and uses the pivot
reaction norm as the normal-load scale:

```text
z = qdot / v_s
tau_f = -r_f ||lambda|| [mu_d tanh(4 z)
        + (mu_s - mu_d) z / (0.25 z^2 + 0.75)^2]
        - c_v tanh(4) qdot
```

Because `lambda` depends on stage acceleration, the collocation residual still
has coupled friction/reaction Jacobians that are handled by JAX.

Run:

```bash
../.venv_sbel/bin/python run_v022.py
```

Primary outputs:

- `results/v022_report.md`
- `results/summary_v022.json`
- `results/revolute_brown_mcphee_runs.csv`
- `results/revolute_brown_mcphee_error_runtime.png`

Completed run:

- Smooth revolute Brown-McPhee friction: fixed Gauss6 reaches observed angle
  order `5.773`. Adaptive `tol=1e-8` and fixed Gauss6 h=0.00625 are
  essentially tied: `2.766e-12` versus `2.840e-12` angle error at similar
  runtime.
- Sharp revolute Brown-McPhee friction: fixed-step order reduces strongly
  (Gauss6 observed angle order `2.412`), but adaptive `tol=1e-7` reaches
  `3.072e-11` angle error versus fixed Gauss6 h=0.00625 error `3.246e-07`,
  while also running faster in the recorded run.
- Conclusion: for a paper-like revolute benchmark, fixed Gauss6 is still the
  clean smooth-friction default, while adaptive Gauss64 is the clear
  high-accuracy winner for sharp Brown-McPhee friction transitions.
