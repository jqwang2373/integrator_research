# Proof Solver Tolerance-Regime Sweep

Status: `finite_tolerance_regime_sweep_recorded_not_theorem_closure`.

This finite smooth short-trajectory sweep compares three Newton
stopping policies: fixed `1e-10`, `c h^7`, and `c h^8`. It imports the
accepted v047 residual functions directly, does not invoke
`run_v047.py`, and does not close the optional primitive/global dynamic
symbolic lane; active direct PC2 remains closed by the separate
D5 direct-substitution route.

- Schema: `proof-solver-tolerance-regime-sweep-v1`.
- Case: `cylindrical_smooth`.
- h values: `[0.04, 0.02, 0.01, 0.005]`.
- t_final: `0.08`.
- Reference h/tolerance: `0.0025` / `1e-13`.
- Policy count: `3`.
- Total rows/steps checked: `12` / `90`.
- All rows converged: `True`.
- Finite tolerance regime sweep recorded: `True`.
- Finite h-scaled tolerance sweep recorded: `True`.
- Finite h-scaled policy names: `['scaled_h7_c1e4', 'scaled_h8_c1e6']`.
- Finite h-scaled policy rows/steps: `8` / `60`.
- Finite h-scaled position/velocity order floor: `6.946` / `6.608`.
- Scaled residual bounds satisfied: `h7=True`, `h8=True`.
- Theorem-level scaled tolerance sweep recorded: `False`.
- eta_h_O_h7_solver_policy_evidence: `False`.
- Theorem-level solver proof closed: `False`.
- default_1e-4_required: `False`.
- run_v047_invoked: `False`.

## Policy Summary

| policy | target | rows | steps | pos order | vel order | orient order | omega order | max res/h^7 | max res/h^8 |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| fixed_1e-10 | 1e-10 | 4/4 | 30 | 6.946 | 6.608 | 6.966 | 6.607 | 2.109e+02 | 4.218e+04 |
| scaled_h7_c1e4 | 1.0e+04 h^7 | 4/4 | 30 | 6.946 | 6.608 | 6.966 | 6.607 | 2.109e+02 | 4.218e+04 |
| scaled_h8_c1e6 | 1.0e+06 h^8 | 4/4 | 30 | 6.946 | 6.608 | 6.966 | 6.607 | 1.213e+04 | 3.032e+05 |

## Interpretation

The fixed policy is sufficient only for this finite short smooth
diagnostic window, while its residual divided by `h^7` grows on
refinement. The `h^7` and `h^8` policies exercise residual targets
that shrink with `h`; they therefore better match the inexact-Newton
theorem condition as finite diagnostics, not as theorem evidence.
This finite h-scaled comparison is explicitly recorded separately
from the theorem-level scaled-tolerance gate. It is still not a
global solver proof over every reported trajectory, does not close
P6 theorem-level solver-policy evidence, and does not close the
optional primitive/global dynamic symbolic lane. The active 36-row
direct D5 stage-residual certificate is closed separately.

Validator: `validate_proof_solver_tolerance_regime_sweep.py`.
