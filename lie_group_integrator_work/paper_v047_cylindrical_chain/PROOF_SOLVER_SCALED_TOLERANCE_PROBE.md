# Proof Solver Scaled-Tolerance Probe

Status: `finite_scaled_tolerance_probe_recorded_not_theorem_closure`.

This finite one-step probe imports the accepted v047 residual functions
and applies a residual stopping target `eta_h = c_eta h^7` on the
smooth initial state. It does not invoke `run_v047.py`, does not run a
default `1e-4` campaign, and does not close the optional primitive/global
dynamic symbolic lane; active direct PC2 remains closed by the separate
D5 direct-substitution route.

- Probe schema: `proof-solver-scaled-tolerance-probe-v1`.
- Case: `cylindrical_smooth`.
- h values: `[0.04, 0.02, 0.01, 0.005]`.
- c_eta: `10000.0`.
- Rows ok: `4/4`.
- Max final residual / h^7: `1.2758372278641149e+02`.
- Scaled policy exercised: `True`.
- Theorem-level solver proof closed: `False`.
- default_1e-4_required: `False`.
- run_v047_invoked: `False`.

| h | eta target | final residual | final residual / h^7 | Newton iters | status |
|---:|---:|---:|---:|---:|---|
| 0.04 | 1.638400e-06 | 1.029283e-14 | 6.282245e-05 | 6 | ok |
| 0.02 | 1.280000e-08 | 9.238507e-15 | 7.217583e-03 | 6 | ok |
| 0.01 | 1.000000e-10 | 1.221325e-14 | 1.221325e+00 | 6 | ok |
| 0.005 | 7.812500e-13 | 9.967478e-15 | 1.275837e+02 | 6 | ok |

Interpretation: this closes only a finite executable probe for the
solver-scale condition. It is not promoted to theorem-level solver
policy evidence; B3 closure is handled separately by retaining the
eta_h <= c_eta h^7 theorem condition and by the direct residual-bridge/Kantorovich
proof route.

Validator: `validate_proof_solver_scaled_tolerance_probe.py`.
