# Closed-Loop True-Dynamic-Row Feasibility Audit

Status: **open; true local dynamic trajectory rows are not implemented**

- Local dynamic rows available: `0`.
- Accepted dynamic-order rows in this audit: `0`.
- Default execution policy: `coarse_first_no_default_1e-4`.
- Strict public `1e-4` required: `False`.

## Source Finding

The current v048 closed-loop local path calls
`simulate_v046_local_kinematic_fullva`. In v047 that function calls
`setup_system(..., "kinematics", ...)`, solves the driven constraints at
output times, and reconstructs reaction multipliers afterward. That is
valid coverage and residual evidence, but it is not a local dynamic DAE
trajectory integrator.

| Model | Current local row | True dynamic row | Required next implementation |
|---|---|---:|---|
| `four_link` | `simulate_v046_local_kinematic_fullva` / `kinematics` | false | local dynamic DAE Gauss6/FullVA solve or residual-to-error theorem |
| `slider_crank` | `simulate_v046_local_kinematic_fullva` / `kinematics` | false | local dynamic DAE Gauss6/FullVA solve or residual-to-error theorem |

## Required Dynamic Row

A reviewer-defensible true dynamic row would solve one nonlinear system
containing positions, orientations, velocities, accelerations, and
multipliers, with `Phi`, velocity constraints, acceleration
constraints, SO(3) constraints, Newton-Euler balance, and Gauss6/FullVA
stage/endpoint collocation coupled in the same step. Only then can the
closed-loop `four_link` and `slider_crank` rows be interpreted as
dynamic trajectory order rows.

No default `1e-4` run is part of this closure path. The next executable
test remains coarse-first: `h=[0.1,0.05,0.025]`,
`reference_h=0.0125`, with non-floor-limited position and velocity
orders consistent with order six.
