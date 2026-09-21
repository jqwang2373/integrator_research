# v033 Lagged Sparse Newton

This version tests a practical way to reduce dense AD Jacobian materialization
after v031/v032: reuse a sparse Newton Jacobian for more than one Newton
correction.

Run:

```bash
../.venv_sbel/bin/python run_v033.py
```

Outputs are written to `results/`.
