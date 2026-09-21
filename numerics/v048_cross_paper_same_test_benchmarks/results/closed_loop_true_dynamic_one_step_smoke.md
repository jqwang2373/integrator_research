# Closed-Loop True-Dynamic One-Step Smoke

Status: **one-step smoke passed; order rows not run**

- Rows: `2/2` ok.
- Max stage residual infinity norm: `1.545e-13`.
- Max endpoint position error: `4.411e-08`.
- Trajectory stepper executed: `True`.
- Accepted dynamic-order rows: `0`.
- Default `1e-4` required: `False`.

This artifact advances exactly one Gauss6 step on each missing
closed-loop mechanism using oracle-initialized stage residual roots.
It is useful implementation progress toward the local dynamic runner,
but it is not a convergence sweep and must not be counted as order
or external-superiority evidence.

| Model | max stage residual | endpoint pos error | endpoint vel error | status |
|---|---:|---:|---:|---|
| `four_link` | `1.5454304502782179e-13` | `8.8068463632851035e-09` | `5.0344827418058458e-08` | `ok` |
| `slider_crank` | `7.1054273576010019e-15` | `4.4112151542652356e-08` | `2.4150835160191564e-07` | `ok` |
