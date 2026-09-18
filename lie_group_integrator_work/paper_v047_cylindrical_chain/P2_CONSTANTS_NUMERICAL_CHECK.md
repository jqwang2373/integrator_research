# P2 Constants Numerical Check

Status: `inverse_bound_observed_neumann_threshold_below_reported_h`.

Finite-window instantiation of the constants of Lemma p2-from-p1 (uniform stage inverse from the
h -> 0 Jacobian, Lean `uniform_inverse_of_perturbation`) and of the predictor distances used by
Lemma newton-envelope (Lean `simplified_newton_residual_decay`), computed with the implemented
Jacobian `R_JAC` on the smooth cylindrical chain.  Euclidean operator norm on the implemented
stage layout.  Diagnostic only; not a proof input.

- Case: `cylindrical_smooth`; h values: `[0.04, 0.02, 0.01]`; t_final: `0.08`; Newton tolerance: `1e-13`.
- Rows with the lemma conclusion observed (||J_h^-1|| <= 2 ||J_0^-1||, all solves converged, h=0 root reproduces the endpoint): `3/3`.
- M0 = max ||J_0^-1||: `2.839e+01`; C_J = max ||J_h-J_0||/h: `9.644e+02`; implied Neumann threshold h_0 = 1/(2 M0 C_J): `2.488e-05`.
- Neumann sufficient condition M0*||J_h-J_0|| <= 1/2 met on all reported h: `False` (expected False: the sufficient condition is pessimistic in this norm; the conclusion is checked directly).
- First full-Newton step contracts from the implemented predictor on all h: `False` (the implemented predictor zeroes angular velocity and acceleration guesses, so its distance to Z_G is O(1); the lifted endpoint predictor distance is O(h)).
- run_v047_invoked: `False`; default_1e-4_required: `False`.

| h | steps | M0 | cond J0 | C_J | M0*delta | inv ratio | implied h0 | lifted pred. dist | implemented pred. dist | first-step contraction | conclusion observed |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 0.04 | 2 | 1.822e+01 | 2.720e+02 | 7.470e+02 | 5.443e+02 | 1.550 | 3.674e-05 | 3.234e+00 | 5.017e+01 | 1.122e+00 | True |
| 0.02 | 4 | 2.427e+01 | 7.774e+02 | 8.220e+02 | 2.995e+02 | 1.259 | 3.339e-05 | 2.108e+00 | 5.030e+01 | 1.160e+00 | True |
| 0.01 | 8 | 2.839e+01 | 1.162e+03 | 9.644e+02 | 2.010e+02 | 1.181 | 2.488e-05 | 1.069e+00 | 5.036e+01 | 1.181e+00 | True |

Validator: `validate_p2_constants_numerical_check.py`.
