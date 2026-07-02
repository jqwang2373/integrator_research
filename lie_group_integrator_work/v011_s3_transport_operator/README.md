# v011 S3 Transport Operator Prototype

Purpose: isolate and verify the paper's quaternion derivative-transport glue:

```text
p(theta) = exp(theta/2) * p0
T_exp = dp / dtheta
Pi(g) = g_p T_exp + g_theta
Theta(g) = [g_r, Pi(g)]
```

This is not a full TFE integrator yet. It is the missing operator-level bridge
between v010's AD-accelerated frictional DAE residual and the paper's explicit
quaternion `S^3` formulation.

Validation:
- compare the analytic `T_exp` against direct JAX differentiation of the
  quaternion update;
- compare transported `Pi(g)` and `Theta(g)` against direct AD of a composite
  nonlinear friction-like load;
- also compare `Pi(g)` against central finite differences to show the expected
  finite-difference error floor.

Run:

```bash
../.venv_sbel/bin/python run_v011.py
```

Primary outputs:
- `results/v011_report.md`
- `results/summary_v011.json`
- `results/transport_matrix_validation.csv`
- `results/pi_theta_validation.csv`
- `results/pi_validation_errors.png`

Current run:
- analytic `T_exp` matches direct AD of the quaternion update with max absolute
  error `1.110e-16`;
- transported `Pi(g)` matches direct composite AD of the nonlinear
  friction-like load with max absolute error `2.429e-15`;
- transported `Theta(g)` matches direct composite AD with max absolute error
  `2.429e-15`;
- central finite-difference agreement is limited to about `2.165e-10`, which is
  the expected differencing floor and motivates AD for production Jacobians.
