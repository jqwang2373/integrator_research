# v020 Adaptive Lambda-Dependent Friction

Purpose: combine v015's embedded adaptive Gauss64 idea with v019's
multiplier-dependent Stribeck-style friction.

The adaptive method:

- computes one Gauss6 endpoint step with lambda-dependent friction;
- computes one Gauss4 endpoint step from the same state and step size;
- estimates local error from final attitude and angular velocity differences;
- accepts the Gauss6 state when the normalized embedded error is below one;
- adjusts the next step with a conservative fifth-root controller.

This tests whether the high-accuracy near-nonsmooth win from v015 survives when
friction depends on the Lagrange multiplier.

Run:

```bash
../.venv_sbel/bin/python run_v020.py
```

Primary outputs:

- `results/v020_report.md`
- `results/summary_v020.json`
- `results/adaptive_lambda_runs.csv`
- `results/adaptive_lambda_error_runtime.png`

Main result from the recorded run:

- Smooth lambda-friction: fixed Gauss6 h=0.025 remains the better default;
  adaptive `tol=1e-7` is still 4.41x less accurate and 1.74x slower.
- Sharp lambda-friction: adaptive `tol=1e-7` beats fixed Gauss6 h=0.0125 by
  51.8x in orientation error at 1.17x runtime, so adaptivity is useful when the
  multiplier-dependent friction transition is sharp.
