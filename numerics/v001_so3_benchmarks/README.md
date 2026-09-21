# v001 SO(3) Benchmarks

Purpose: build a small, dependency-light benchmark that can falsify or support candidate "better" Lie group integrators before porting anything into the full index-3 DAE/friction setting.

Scope of this version:
- Compare intrinsic SO(3) orientation steppers on a non-commuting, time-varying angular-velocity field.
- Compare torque-free rigid-body steppers on long-time invariant drift.
- Save CSV and JSON outputs under `results/`.

Methods included:
- `lie_euler`: first-order exponential update, similar in spirit to the first-order exponential-map update used in the SBEL r-A baseline.
- `exp_midpoint`: second-order one-exponential midpoint update.
- `cf4`: fourth-order commutator-free Magnus-type two-exponential update for time-dependent kinematics.
- `rkmk4`: fourth-order Runge-Kutta-Munthe-Kaas update with right-trivialized `dexp^{-1}`.
- `matrix_rk4`: classical RK4 applied to the matrix ODE, included only as a non-intrinsic comparison.
- `lie_midpoint`: implicit midpoint for torque-free Euler equations plus exponential pose update; included as a structure-preserving baseline for quadratic invariants.

Key literature/source hooks:
- Chaturvedi, Sandu, Sandu (2026), "Higher-order integration of index-3 DAE with friction using time finite elements on Lie groups", DOI `10.1007/s11044-026-10153-w`.
- SBEL/Negrut reproducibility source: `https://github.com/uwsbel/sbel-reproducibility/tree/master/2021/ASME/rA-formulation`.
- Munthe-Kaas (1998, 1999): high-order Runge-Kutta methods on Lie groups/manifolds.
- Wieloch and Arnold (2021): BLieDF for constrained mechanical systems on Lie groups.
- Hall and Leok (2017): Lie group spectral variational integrators.
- Bogfjellmo and Marthinsen (2016/2017): high-order symplectic partitioned Lie group methods.

Run:

```bash
conda run -n base python lie_group_integrator_work/v001_so3_benchmarks/run_v001.py
```

The script uses only NumPy from Python dependencies.

