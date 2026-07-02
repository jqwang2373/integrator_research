# v009 Frictional Endpoint-Constrained DAE Prototype

Purpose: add friction/dissipation to the v008 endpoint-constrained Lie-group
DAE residual and test whether the high-order behavior survives.

Model:
- fixed-pivot rigid body with explicit Lagrange multipliers;
- endpoint-constrained 54-variable two-stage Gauss-Lie nonlinear solve;
- body-frame pivot friction torque

```text
tau_f(omega) = -c_v omega - mu tanh(omega / eps)
```

where `eps` controls regularization sharpness. Smaller `eps` is closer to a
Coulomb-like nonsmooth law and is expected to be more order-reducing.

Experiments:
- smooth friction (`eps=0.50`);
- sharper friction (`eps=0.05`);
- short-time order, endpoint/stage constraint residuals, energy dissipation,
  and Newton/runtime cost.

Run:

```bash
../.venv_sbel/bin/python run_v009.py
```

Outputs are written under `results/`.

Current run:
- `absolute_gauss_lie4_endpoint` with smooth friction measured orientation order
  3.979 and omega order 4.009.
- The sharper `eps=0.05` friction regularization reduced the observed endpoint
  orientation order to 2.462, which matches the expectation that near nonsmooth
  friction stresses high-order collocation.
- In both friction cases, 5s runs at `h=0.05` had monotone mechanical energy
  decay, negative friction power, and endpoint constraints at about 1e-14 or
  better.

Primary report:
- `results/v009_report.md`
