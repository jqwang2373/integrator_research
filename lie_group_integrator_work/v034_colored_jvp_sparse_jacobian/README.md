# v034 Colored-JVP Sparse Jacobian

This version tests structured sparse AD through column coloring. A sparsity
pattern is extracted once, columns are colored so same-color columns have
disjoint row supports, and JAX JVPs assemble only the sparse Jacobian values.

Run:

```bash
../.venv_sbel/bin/python run_v034.py
```

Outputs are written to `results/`.
