# v006 Fixed-Pivot Rigid-Body DAE Prototype

Purpose: move the v005 Gauss-Lie idea from an unconstrained Euler top to a
minimal constrained rigid-body DAE.

Model:
- one rigid body with center of mass position `r`, attitude `R in SO(3)`, and a
  body-fixed pivot vector `s`;
- index-3 holonomic constraint `g(r, R) = r + R s = 0`;
- gravity acts at the center of mass;
- the pivot reaction is recovered as the Lagrange multiplier/constraint force.

The integration is performed on the reduced fixed-pivot SO(3) dynamics, but the
script reconstructs `r`, `r_dot`, the pivot reaction, and DAE residuals at each
sample. This keeps the constraints exact while testing the Lie-group
time-integration candidate before wiring it into a full absolute-coordinate
Newton solve.

Run:

```bash
../.venv_sbel/bin/python run_v006.py
```

Outputs are written under `results/`.
