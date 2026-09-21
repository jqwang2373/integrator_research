# P2 Constants Numerical Check

Status: `inverse_bound_observed_neumann_threshold_below_reported_h`.

Finite-window instantiation of the constants of Lemma p2-from-p1 (uniform stage inverse from the
h -> 0 Jacobian, Lean `uniform_inverse_of_perturbation`) and of the predictor distances used by
Lemma newton-envelope (Lean `simplified_newton_residual_decay`), computed with the implemented
Jacobian `R_JAC` on the smooth cylindrical chain.  Diagnostic only; not a proof input.

- Case: `cylindrical_smooth`; h values: `[0.04, 0.02, 0.01]`; t_final: `0.08`; Newton tolerance: `1e-13`.
- Rows with the lemma conclusion observed (||J_h^-1|| <= 2 ||J_0^-1||, all solves converged, h=0 root reproduces the endpoint): `3/3`.
- Euclidean norm: M0 = max ||J_0^-1|| `2.839e+01`, C_J = max ||J_h-J_0||/h `9.644e+02`, implied Neumann threshold h_0 `1.826e-05`; condition met on all reported h: `False`.
- Endpoint-linearized norm ||J_0^-1 F||: C_J `6.545e+02`, implied h_0 `7.640e-04`; condition met on all reported h: `False`.
- Equilibrated norm: implied h_0 `7.337e-04`.
- Dominant block of (J_h-J_0)/h: `['dynxv', 'dynxv', 'dynxv']` (Newton-Euler rows vs stage velocities: the Brown-McPhee friction curvature, Stribeck velocity `0.5`).
- Frictionless variant (mu_s = mu_d = viscous = 0): endpoint-linearized C_J `3.646e+01` vs `6.545e+02` with friction; implied h_0 `1.372e-02` vs `7.640e-04`; all reported h below the frictionless threshold: `False`; dominant block `['wblkxw', 'wblkxw', 'wblkxw']`.
- First full-Newton step contracts from the implemented predictor on all h: `False` (the implemented predictor zeroes angular velocity and acceleration guesses, so its distance to Z_G is O(1); the lifted endpoint predictor distance is O(h)).
- run_v047_invoked: `False`; default_1e-4_required: `False`.

| variant | h | M0 | C_J | inv ratio | h0 Euclid | C_J weighted | h0 weighted | h0 equilibrated | dominant block | lifted pred. | implemented pred. | first-step ratio | conclusion observed |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|---:|---:|---|
| cylindrical_smooth | 0.04 | 1.822e+01 | 7.470e+02 | 1.550 | 3.674e-05 | 5.095e+02 | 9.813e-04 | 8.060e-04 | dynxv | 3.234e+00 | 5.017e+01 | 1.122e+00 | True |
| cylindrical_smooth | 0.02 | 2.427e+01 | 8.220e+02 | 1.259 | 2.506e-05 | 5.632e+02 | 8.878e-04 | 7.337e-04 | dynxv | 2.108e+00 | 5.030e+01 | 1.160e+00 | True |
| cylindrical_smooth | 0.01 | 2.839e+01 | 9.644e+02 | 1.181 | 1.826e-05 | 6.545e+02 | 7.640e-04 | 8.649e-04 | dynxv | 1.069e+00 | 5.036e+01 | 1.181e+00 | True |
| cylindrical_smooth_frictionless | 0.04 | 1.292e+01 | 2.622e+01 | 1.028 | 1.476e-03 | 3.414e+01 | 1.465e-02 | 4.341e-03 | wblkxw | 1.062e+00 | 5.066e+01 | 1.088e+00 | True |
| cylindrical_smooth_frictionless | 0.02 | 1.308e+01 | 3.124e+01 | 1.018 | 1.224e-03 | 3.550e+01 | 1.408e-02 | 3.807e-03 | wblkxw | 5.930e-01 | 5.074e+01 | 1.126e+00 | True |
| cylindrical_smooth_frictionless | 0.01 | 1.320e+01 | 3.380e+01 | 1.010 | 1.121e-03 | 3.646e+01 | 1.372e-02 | 3.806e-03 | wblkxw | 3.134e-01 | 5.078e+01 | 1.147e+00 | True |

Validator: `validate_p2_constants_numerical_check.py`.
