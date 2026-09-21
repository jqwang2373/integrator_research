# v018 Reduced Lie-Lobatto Endpoint Baseline

Purpose: test a TFE/Gauss-Lobatto-style endpoint-node collocation direction on
the same reduced fixed-pivot quaternion benchmark.

This version solves reduced local-coordinate collocation equations for

```text
u_dot = J_r^{-1}(u) omega
omega_dot = f(p0 * exp(u/2), omega)
```

using Lobatto endpoint nodes:

- `reduced_lie_lobatto4_fd`: 3-stage Lobatto IIIA, order 4 target;
- `reduced_lie_lobatto6_fd`: 4-stage Lobatto IIIA, order 6 target.

The fixed-pivot position and velocity constraints are reconstructed from
`(p, omega)`, so this is a reduced endpoint-node baseline rather than the
paper's full absolute-coordinate TFE formulation.

Run:

```bash
../.venv_sbel/bin/python run_v018.py
```

Primary outputs:

- `results/v018_report.md`
- `results/summary_v018.json`
- `results/order_lobatto.csv`
- `results/longrun_lobatto.csv`
- `results/order_lobatto_comparison.png`

Completed run:

- Runtime: about 236 s in `.venv_sbel`.
- Lobatto4 reaches about fourth order for frictionless/smooth cases; Lobatto6
  reaches about sixth order for frictionless/smooth cases.
- Smooth friction h=0.025: Lobatto6 orientation error `1.161e-11` versus Gauss6
  `1.579e-11`, but Lobatto6 runtime `0.631 s` versus Gauss6 `0.149 s`.
- Sharp friction h=0.025: Lobatto6 orientation error `9.131e-07` versus Gauss6
  `7.566e-07`, with Lobatto6 runtime `0.601 s` versus Gauss6 `0.131 s`.
- Conclusion: Lobatto endpoint nodes are accuracy-competitive, but not the
  current best accuracy-per-cost method. They remain relevant for a future full
  TFE residual if endpoint conditioning becomes the key issue.
