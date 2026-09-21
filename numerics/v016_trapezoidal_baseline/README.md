# v016 Lie-Trapezoidal Baseline

Purpose: add a paper-style low-order implicit baseline on the same fixed-pivot
quaternion test problem used by v012-v015.

This version implements a reduced right-action Lie-trapezoidal step for
`(p, omega)`:

```text
u_{n+1} = h/2 * (omega_n + J_r^{-1}(u_{n+1}) omega_{n+1})
omega_{n+1} = omega_n + h/2 * (f(p_n, omega_n) + f(p_{n+1}, omega_{n+1}))
p_{n+1} = p_n * exp(u_{n+1}/2)
```

The fixed-pivot holonomic position and velocity constraints are reconstructed
from `(p, omega)`, so this is a favorable baseline for trapezoidal behavior,
not a deliberately weak one.

Run:

```bash
../.venv_sbel/bin/python run_v016.py
```

Primary outputs:

- `results/v016_report.md`
- `results/summary_v016.json`
- `results/order_baseline.csv`
- `results/longrun_baseline.csv`
- `results/order_comparison.png`

Completed run:

- Runtime: about 276 s in `.venv_sbel`.
- Lie-trapezoidal observed orientation order is about 1.96-1.98 across
  frictionless, smooth-friction, and sharp-friction cases.
- At `h=0.025`, Gauss6 reduces orientation error versus Lie-trapezoidal by
  `4.84e7x` in frictionless, `4.16e7x` in smooth friction, and `8.57e2x` in
  sharp friction, with roughly similar runtime.
- In the 20s frictionless long run at `h=0.05`, Gauss6 max relative energy error
  is `1.105e-10`, versus `4.299e-04` for Lie-trapezoidal.
