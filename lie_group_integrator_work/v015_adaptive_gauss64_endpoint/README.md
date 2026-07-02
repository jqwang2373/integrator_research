# v015 Adaptive Gauss64 Quaternion Endpoint

Purpose: test whether an embedded adaptive Gauss6/Gauss4 endpoint Lie-collocation
method improves the sharp-friction regime exposed by v014.

The adaptive stepper:

- computes a three-stage Gauss6 endpoint step;
- computes a two-stage Gauss4 endpoint step from the same state and step size;
- estimates local error from the final attitude and angular-velocity difference;
- accepts the Gauss6 state when the normalized embedded error is below one;
- shrinks or grows the next step with a conservative fifth-root controller.

This version is aimed at frictional/dissipative index-3 DAE behavior, not exact
symplecticity. The question is whether adaptivity beats fixed global small steps
for `eps=0.05` and `eps=0.025`.

Run:

```bash
../.venv_sbel/bin/python run_v015.py
```

Primary outputs:

- `results/v015_report.md`
- `results/summary_v015.json`
- `results/adaptive_gauss64_runs.csv`
- `results/adaptive_error_runtime.png`

Completed run:

- Runtime: about 195 s in `.venv_sbel`, with JAX kernels warmed before timed
  fixed/adaptive runs.
- `eps=0.05`: adaptive `tol=1e-6` reached orientation error `8.713e-09` in
  `0.472 s`, versus fixed Gauss6 `h=0.0125` error `3.189e-08` in `0.552 s`.
- `eps=0.025`: adaptive `tol=1e-6` reached orientation error `3.538e-08` in
  `0.547 s`, versus fixed Gauss6 `h=0.0125` error `1.762e-07` in `0.659 s`.
- Low-cost conclusion: fixed Gauss6 `h=0.025` remains a pragmatic cheap
  default; adaptive Gauss64 is better for high-accuracy near-nonsmooth
  regularized friction.
