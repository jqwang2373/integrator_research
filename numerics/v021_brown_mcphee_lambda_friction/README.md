# v021 Brown-McPhee Lambda Friction

Purpose: replace v019's Gaussian/tanh Stribeck-inspired torque with a
Brown-McPhee-style continuous velocity friction curve while keeping the same
quaternion endpoint DAE and reaction-load coupling.

The componentwise scalar curve is:

```text
z = omega_i / v_s
mu_curve_i = mu_d tanh(4 z) + (mu_s - mu_d) z / (0.25 z^2 + 0.75)^2
tau_i = -r_f ||lambda|| mu_curve_i / sqrt(3) - c_v tanh(4) omega_i
```

This captures the Brown-McPhee continuous Coulomb term, the rational
stiction/Stribeck bump, and viscous friction. The stage Lagrange multiplier still
sets the normal-load scale, so JAX differentiates through the coupled
friction/multiplier residual.

Run:

```bash
../.venv_sbel/bin/python run_v021.py
```

Primary outputs:

- `results/v021_report.md`
- `results/summary_v021.json`
- `results/brown_mcphee_lambda_runs.csv`
- `results/brown_mcphee_lambda_error_runtime.png`

Completed run:

- Smooth Brown-McPhee velocity scale: fixed Gauss6 keeps the high-accuracy
  advantage. Gauss6 h=0.025 gives `5.161e-09` orientation error; fixed h=0.0125
  gives `1.088e-11`. Adaptive improves the coarse step but does not beat global
  halving.
- Sharp Brown-McPhee velocity scale: fixed-step order reduces strongly
  (Gauss6 observed orientation order `2.901`), but adaptive `tol=1e-7` reaches
  `1.186e-07` orientation error versus fixed Gauss6 h=0.0125 error
  `5.128e-07`. That is `4.3x` lower error at `1.77x` runtime.
- Conclusion: the v020 adaptive story survives the more realistic
  Brown-McPhee-style friction curve for high-accuracy sharp-friction work, but
  fixed Gauss6 remains the clean default for smooth friction.
