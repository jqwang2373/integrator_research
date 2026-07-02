# Closed-Loop True-Dynamic Newton Stage Smoke

Status: **non-oracle stage Newton smoke passed; order rows not run**

- Rows: `2/2` ok.
- Max initial stage residual infinity norm: `4.306e+01`.
- Max final stage residual infinity norm: `1.790e-13`.
- Stage oracle used: `False`.
- Trajectory stepper executed: `True`.
- Accepted dynamic-order rows: `0`.
- Default `1e-4` required: `False`.

This artifact advances the missing closed-loop mechanisms one Gauss6
step using stage Newton solves initialized only from the start state.
No stage-time kinematic oracle is used. It removes the stage-time
oracle from the previous one-step smoke, but
it is still not a convergence sweep and must not be counted as order
or external-superiority evidence.

| Model | initial residual | final residual | Newton iters | endpoint pos error | status |
|---|---:|---:|---:|---:|---|
| `four_link` | `4.3061325916317529e+01` | `1.1013412404281553e-13` | `8` | `8.8068463632851035e-09` | `ok` |
| `slider_crank` | `1.2886358278365131e+00` | `1.7900264603909477e-13` | `8` | `4.4112151487141205e-08` | `ok` |
