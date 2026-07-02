# Closed-Loop True-Dynamic Stage Residual Audit

Status: **stage residual evaluator verified; stepper not implemented**

- Rows: `6/6` ok.
- Max stage residual infinity norm: `5.507e-14`.
- Stage evaluator implemented: `True`.
- Trajectory stepper implemented: `False`.
- Accepted dynamic-order rows: `0`.
- Default `1e-4` required: `False`.

This audit evaluates the four residual families at the three Gauss6
stage times for `four_link` and `slider_crank`. It proves that the
local residual evaluator can assemble and evaluate the square 72-row
stage system on the public/v046 dynamic interface. It still does not
advance an endpoint and must not be counted as a trajectory order row.

| Model | Stage | stage residual inf | Newton-Euler inf | status |
|---|---:|---:|---:|---|
| `four_link` | `1` | `4.9737991503207013e-14` | `4.9737991503207013e-14` | `ok` |
| `four_link` | `2` | `5.5067062021407764e-14` | `5.5067062021407764e-14` | `ok` |
| `four_link` | `3` | `1.4210854715202004e-14` | `1.4210854715202004e-14` | `ok` |
| `slider_crank` | `1` | `3.5527136788005009e-15` | `3.5527136788005009e-15` | `ok` |
| `slider_crank` | `2` | `2.6645352591003757e-15` | `2.6645352591003757e-15` | `ok` |
| `slider_crank` | `3` | `1.7763568394002505e-15` | `1.7763568394002505e-15` | `ok` |
