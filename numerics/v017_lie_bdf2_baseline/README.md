# v017 Lie-BDF2 Baseline

Purpose: test a BLieDF/BDF-style low-order implicit multistep direction from the
paper's reference trail on the same reduced fixed-pivot quaternion problem.

The new method is a fixed-step right-action Lie-BDF2 scheme. For the endpoint
increment `u` from `p_n` to `p_{n+1}` and the previous relative increment
`u_prev = log(p_n^{-1} p_{n-1})`, it solves

```text
(3 u + u_prev) / (2 h) = J_r^{-1}(u) omega_{n+1}
(3 omega_{n+1} - 4 omega_n + omega_{n-1}) / (2 h) = f(p_{n+1}, omega_{n+1})
```

The first step is started with RKMK4 so the order study measures the BDF2
formula rather than startup error. Fixed-pivot position and velocity constraints
are reconstructed from `(p, omega)`.

Run:

```bash
../.venv_sbel/bin/python run_v017.py
```

Primary outputs:

- `results/v017_report.md`
- `results/summary_v017.json`
- `results/order_bdf2.csv`
- `results/longrun_bdf2.csv`
- `results/order_bdf2_comparison.png`

Completed run:

- Runtime: about 264 s in `.venv_sbel`.
- Lie-BDF2 observed orientation order is about 1.86-1.90 across frictionless,
  smooth-friction, and sharp-friction cases.
- At `h=0.025`, Gauss6 reduces orientation error versus Lie-BDF2 by `1.87e8x`
  in frictionless, `1.60e8x` in smooth friction, and `3.20e3x` in sharp
  friction, with comparable runtime.
- In the 20s frictionless long run at `h=0.05`, Lie-BDF2 has strong numerical
  damping: final relative energy change `-5.314e-02`, versus `-2.922e-11` for
  Gauss6.
- In the 20s sharp-friction long run, all methods dissipate energy, but BDF2
  over-dissipates relative to Gauss6/trapezoidal.
