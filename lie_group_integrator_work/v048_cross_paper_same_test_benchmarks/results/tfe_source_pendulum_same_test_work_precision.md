# TFE Source-Pendulum Same-Test Work/Precision

Status: **same test candidate work precision available not source policy**.

- Rows: `18/18` ok.
- Methods: `Newmark_beta,trapezoidal,TFE_m1,TFE_m2,TFE_m3_GL,Gauss6_FullVA`.
- Time/reference/grid: `T=1.0`, `h_ref=0.00025`, `h=[0.1, 0.05, 0.025]`.
- Figure available: `True`.
- Source-policy rows completed: `0`.
- External superiority claim: `False`.

All rows share the frictionless extracted source-pendulum parameters, output
policy, RK4 reference, time horizon, and step grid. Runtime and Newton
iteration counts are recorded as work proxies. This is candidate-level
same-test evidence only.

| Method | expected | ok | coord order | vel order | Frobenius order | finest vel | Newton sum | runtime sum |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `Newmark-beta` | `2` | `3/3` | `1.9957368439811132e+00` | `1.9973428612090549e+00` | `1.9957359048635259e+00` | `1.9010449705181287e-04` | `1.1400000000000000e+02` | `4.6203140009311028e-03` |
| `trapezoidal` | `2` | `3/3` | `1.9966999705678214e+00` | `1.9978864993121155e+00` | `1.9966994132860196e+00` | `2.4157646564892943e-04` | `1.1300000000000000e+02` | `2.6986419979948550e-03` |
| `TFE m=1` | `1` | `3/3` | `2.1934153421124032e+00` | `1.5959422577251188e+00` | `2.1934148627623919e+00` | `5.6002401063315332e-04` | `1.3200000000000000e+02` | `4.0036279970081523e-03` |
| `TFE m=2` | `3` | `3/3` | `2.7299295269506842e+00` | `3.1033790310399842e+00` | `2.7299295327459245e+00` | `7.5088541162671163e-08` | `1.2500000000000000e+02` | `7.7050800027791411e-03` |
| `TFE m=3 GL` | `5` | `3/3` | `7.3409199487157526e+00` | `5.2399215952355496e+00` | `7.3450597431607276e+00` | `4.9480419761493977e-12` | `1.3500000000000000e+02` | `1.2395270001434255e-02` |
| `Gauss6/FullVA` | `6` | `3/3` | `6.0432129341837602e+00` | `6.0259645124691312e+00` | `6.0432289640990149e+00` | `4.0367709175370692e-13` | `1.1100000000000000e+02` | `4.4366080997860990e-02` |
