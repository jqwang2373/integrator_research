# v031 Sparse Newton Double-Revolute

This version turns the v030 sparsity diagnostic into an actual Newton-loop
experiment. It reuses the v029 double-revolute quaternion DAE residual and
compares dense `numpy.linalg.solve` with thresholded CSR `scipy.sparse.linalg`
solves inside each Newton iteration.

Run:

```bash
../.venv_sbel/bin/python run_v031.py
```

Outputs are written to `results/`.
