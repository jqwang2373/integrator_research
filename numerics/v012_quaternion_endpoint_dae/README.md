# v012 Quaternion Endpoint-Constrained DAE Prototype

Purpose: move the v010/v011 line into a true quaternion attitude residual.

This version keeps the same fixed-pivot frictional DAE and the same 54-variable
endpoint-constrained Gauss-Lie solve, but stage and endpoint attitudes are now
computed as scalar-first unit quaternions:

```text
p(theta) = p0 * exp(theta/2)
```

The right-action convention is chosen to match the earlier SO(3) update
`R_next = R exp(theta)`. A right-action `T_exp` is validated against direct JAX
AD as the counterpart of the paper/v011 transport operator.

Run:

```bash
../.venv_sbel/bin/python run_v012.py
```

Primary outputs:
- `results/v012_report.md`
- `results/summary_v012.json`
- `results/right_transport_validation.csv`
- `results/quaternion_order.csv`
- `results/so3_quaternion_equivalence.csv`
- `results/quaternion_dissipation.csv`

Current run:
- right-action `T_exp` matches direct AD with max absolute error `1.110e-16`;
- smooth friction endpoint order: orientation `3.979`, omega `4.009`;
- sharper friction endpoint order: orientation `2.462`, omega `2.064`;
- quaternion/SO3 5s h=0.05 final-state differences are at roundoff scale
  (`1.771e-15` orientation for smooth friction and `2.996e-15` for sharper
  friction);
- quaternion unit norm error stays at `1e-16` scale, while endpoint constraints
  stay around `1e-14` in 5s frictional runs.
