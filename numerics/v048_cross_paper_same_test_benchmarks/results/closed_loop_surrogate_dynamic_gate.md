# Closed-Loop Surrogate Dynamic Gate

Status: **surrogate evidence only; not external superiority**

- Models: `four_link,slider_crank`.
- Selected window: `T=0.2`, `h=0.02|0.01|0.005`.
- Reference: `rA-public-kinematics`, `h=0.001`.
- Surrogate available rows: `2`.
- Accepted dynamic order rows: `0`.
- Default policy: `coarse_first_no_default_1e-4`.

Reading rule: this is the lightweight residual-to-error bridge requested by the coarse-first policy. It does not use default `1e-4` runs and does not close the CMAME same-test superiority gate.

| Model | Public vel order | Local surrogate vel order | Local vel-error ratio | Local runtime ratio | Max local dynamics residual | Blocker |
|---|---:|---:|---:|---:|---:|---|
| `four_link` | 1.0526168857360827e+00 | -7.1023698211133252e-07 | 1.2017170945683198e-07 | 2.1584174353651067e+00 | 1.3382220299057966e-13 | local row is kinematic FullVA plus reaction reconstruction; promote only after a true local dynamic order/work row or a reviewer-defensible residual-to-error acceptance argument is added |
| `slider_crank` | 1.0900609543429600e+00 | 2.6697646021638326e-15 | 3.3415764751334156e-05 | 1.7974118549080003e+00 | 6.4924050158874451e-15 | local row is kinematic FullVA plus reaction reconstruction; promote only after a true local dynamic order/work row or a reviewer-defensible residual-to-error acceptance argument is added |
