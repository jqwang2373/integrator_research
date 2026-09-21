# Exact Stage Identity Numerical Check

Status: `reduced_collocation_recovered_at_roundoff`.

Converged FullVA stage vectors of the smooth cylindrical chain are read in the reduced
joint-coordinate chart; the reduced three-stage Gauss collocation defects must be at roundoff
(Lemma exact-stage-identity, Lean `FullVA.Transition.nondynamic_rows_iff`).

- Case: `cylindrical_smooth`; h values: `[0.04, 0.02, 0.01]`; t_final: `0.08`; Newton tolerance: `1e-13`.
- Rows ok: `3/3`; threshold: `1e-10`.
- Max reduced collocation defect overall: `9.014e-15`.
- run_v047_invoked: `False`; default_1e-4_required: `False`.

| h | steps | Newton iters | max residual | max reduced defect (s, ṡ, θ, θ̇) | max ⊥ component | factorization mismatch | ok |
|---:|---:|---:|---:|---|---:|---:|---|
| 0.04 | 2 | 12 | 6.785e-14 | 9.01e-15, 1.73e-16, 3.85e-16, 2.78e-16 | 1.46e-15 | 9.05e-15 | True |
| 0.02 | 4 | 24 | 1.530e-14 | 4.19e-16, 1.67e-16, 5.45e-16, 2.30e-16 | 1.88e-15 | 3.78e-16 | True |
| 0.01 | 8 | 48 | 1.594e-14 | 1.50e-16, 5.76e-16, 4.34e-16, 5.13e-16 | 2.04e-15 | 7.36e-17 | True |

Validator: `validate_exact_stage_identity_numerical_check.py`.
