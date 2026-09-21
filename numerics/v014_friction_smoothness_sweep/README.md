# v014 Friction Smoothness Sweep

Purpose: turn the v013 smooth-vs-sharp observation into a decision boundary.

This version sweeps the regularization width in

```text
tau_f(omega) = -c_v omega - mu tanh(omega / eps)
```

and compares:

- `quaternion_gauss_lie4_endpoint_jax`;
- `quaternion_gauss_lie6_endpoint_jax`.

The result should answer when Gauss6 is worth its larger 75-variable Newton
system and when sharper friction makes higher smooth collocation order a poor
default.

Run:

```bash
../.venv_sbel/bin/python run_v014.py
```

Primary outputs:
- `results/v014_report.md`
- `results/summary_v014.json`
- `results/friction_smoothness_sweep.csv`
- `results/friction_smoothness_decision.csv`
- `results/error_ratio_vs_eps.png`

Completed run:
- Runtime: about 450 s in `.venv_sbel`.
- Gauss6 strong win for `eps=1.0, 0.5, 0.2`.
- Gauss6 useful at `eps=0.1`.
- Gauss6 marginal at `eps=0.05, 0.025`; this is the near-nonsmooth warning regime.
- The main report now includes a paper-by-paper comparison explaining why the Gauss6 quaternion endpoint candidate is better in the smooth-friction regime and where that claim does not hold.
