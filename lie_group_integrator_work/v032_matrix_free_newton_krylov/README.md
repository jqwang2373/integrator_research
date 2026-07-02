# v032 Matrix-Free Newton-Krylov

This version tests the next solver-scaling idea after v031: avoid materializing
the dense JAX Jacobian by solving Newton systems with GMRES and JAX
Jacobian-vector products.

Run:

```bash
../.venv_sbel/bin/python run_v032.py
```

Outputs are written to `results/`.
