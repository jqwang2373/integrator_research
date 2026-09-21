# v030 Double-Revolute Jacobian Sparsity Diagnostics

Purpose: diagnose the dense Newton cost wall exposed by v029's two-body
double-revolute DAE.

This version reuses v029's equations and evaluates converged first-step
Jacobians for:

```text
raw, PivotVA, FullVA
Gauss4, Gauss6
smooth and sharp Brown-McPhee friction
```

It measures Jacobian density, condition number, dense `numpy.linalg.solve`
time, CSR conversion time, and generic SciPy `spsolve` time. It does not change
the integrator equations.

Run:

```bash
../.venv_sbel/bin/python run_v030.py
```

Primary outputs:

- `results/v030_report.md`
- `results/summary_v030.json`
- `results/double_revolute_jacobian_sparsity.csv`
- `results/double_revolute_sparse_solve_summary.png`
- `results/double_revolute_gauss6_fullva_sparsity.png`
