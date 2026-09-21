# Closed-Loop Dynamic Error Floor Audit

Status: **floor audit only; accepted dynamic order remains zero**

- Default policy: `coarse_first_no_default_1e-4`.
- Selected window: `T=0.2`, `h=0.02|0.01|0.005`.
- Velocity/acceleration evidence rows: `2/2`.
- Position-floor blocker rows: `2/2`.
- Accepted dynamic order rows: `0`.
- External superiority claim: `False`.

Reading rule: this audit does not run default `1e-4` rows and does not convert kinematic/reaction rows into accepted dynamic order evidence.

| Model | Public vel order | Public acc order | Local vel ratio | Local acc ratio | Local residual | Position blocker |
|---|---:|---:|---:|---:|---:|---|
| `four_link` | 1.0526168857360827e+00 | 1.0984052242054554e+00 | 1.2017170945683198e-07 | 1.0490157994999220e-07 | 1.3382220299057966e-13 | position error is dominated by the public kinematic reference floor, while the local closed-loop row is still a kinematic FullVA plus reaction reconstruction row |
| `slider_crank` | 1.0900609543429600e+00 | 1.1025746410260142e+00 | 3.3415764751334156e-05 | 8.3691568244576971e-06 | 6.4924050158874451e-15 | position error is dominated by the public kinematic reference floor, while the local closed-loop row is still a kinematic FullVA plus reaction reconstruction row |
