# v013 Gauss6 Quaternion Endpoint DAE Prototype

Purpose: move from representation/Jacobian work to a method-level higher-order
comparison on the verified quaternion residual.

This version keeps the v012 scalar-first unit-quaternion endpoint DAE residual
and adds a three-stage Gauss-Legendre collocation variant:

- `quaternion_gauss_lie4_endpoint_jax`: two-stage Gauss, 54 Newton unknowns;
- `quaternion_gauss_lie6_endpoint_jax`: three-stage Gauss, 75 Newton unknowns.

The target question is whether the sixth-order candidate is practically better
for smooth friction, and whether sharper Coulomb-like regularization still
dominates the observed order.

Run:

```bash
../.venv_sbel/bin/python run_v013.py
```

Primary outputs:
- `results/v013_report.md`
- `results/summary_v013.json`
- `results/gauss6_order.csv`
- `results/gauss6_dissipation.csv`
- `results/right_transport_validation.csv`

Current run:
- smooth friction: Gauss6 observed orientation order `5.994`, omega order
  `6.226`;
- smooth friction at `h=0.025`: Gauss6 orientation error `3.066e-11` versus
  Gauss4 `2.868e-07`, with only `1.15x` runtime;
- sharper friction: Gauss6 observed orientation order `2.689`, essentially the
  same order-limited behavior as Gauss4 but with about `2.7x` smaller
  orientation error at `h=0.025`;
- Gauss6 is the current best smooth-friction accuracy-per-cost candidate in the
  local benchmark, but not a universal default for near-nonsmooth friction.
