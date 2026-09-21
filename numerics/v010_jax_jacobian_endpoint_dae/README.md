# v010 JAX-Jacobian Frictional Endpoint DAE Prototype

Purpose: keep the v009 endpoint-constrained frictional Gauss-Lie DAE method,
but replace the finite-difference Newton Jacobian with a JAX automatic
differentiation Jacobian for the 54-variable endpoint residual.

Why this version matters:
- the 2026 TFE/Lie-group friction paper identifies nonlinear friction-load
  Jacobian construction as a practical bottleneck;
- v009 still used finite differences for Newton;
- v010 checks whether an AD-friendly residual gives the same mechanics while
  reducing runtime enough to support larger friction/contact experiments.

Implemented paths:
- `absolute_gauss_lie4_endpoint`: original finite-difference Jacobian path;
- `absolute_gauss_lie4_endpoint_jax`: same residual equations, JAX `jacfwd`
  Jacobian.

Run:

```bash
../.venv_sbel/bin/python run_v010.py
```

Primary outputs:
- `results/v010_report.md`
- `results/summary_v010.json`
- `results/jax_order_runtime.csv`
- `results/jax_equivalence_dissipation.csv`

Current run:
- finite-difference and JAX Jacobian paths match to roundoff-level final-state
  differences in 5s frictional runs;
- warm JAX Jacobian speedup at `h=0.05` is 33.40x for smooth friction and
  38.59x for sharper friction in the short order benchmark;
- 5s dissipation equivalence speedup is 35.42x for smooth friction and 29.50x
  for sharper friction.
