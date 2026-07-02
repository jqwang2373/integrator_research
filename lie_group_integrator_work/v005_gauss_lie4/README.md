# v005 Gauss-Lie Fourth-Order Candidate

Purpose: test a fourth-order candidate that avoids the negative time substep
used by v004's Yoshida composition.

Main new method:
- `gauss_lie4`: two-stage Gauss-Legendre collocation for the body angular
  velocity of the torque-free rigid body, followed by the same right-action CF4
  reconstruction for `R_dot = R hat(omega)`.

Why this version matters:
- The Gauss stage times are both inside the step: `0.5 +/- sqrt(3)/6`.
- The body-angular-velocity update is fourth-order and preserves quadratic
  invariants to nonlinear solve tolerance in this test.
- It is closer in spirit to collocation/time-finite-element methods than a
  negative-substep composition, so it is a better candidate direction for
  future constrained/friction DAE work.

Run:

```bash
../.venv_sbel/bin/python run_v005.py
```

Results are written under `results/`.
