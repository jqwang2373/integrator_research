# Larger-Step VP/Local Order Audit

Step sizes: `[0.15, 0.075, 0.0375]`; reference h: `0.01875`; t_end: `0.15`.

Comparable examples: `4/4`.
Local velocity-order wins: `4/4`.
Local finest-velocity-error wins: `1/4`.

| Method | Example | status | vel order | pairwise vel orders | finest vel error |
|---|---|---|---:|---:|---:|
| `local_Gauss6_FullVA` | `single_pendulum` | `ok` | `6.0135643426036260e+00` | `6.0269622272073766e+00|6.0001664579998755e+00` | `1.4182787749464959e-11` |
| `local_Gauss6_FullVA` | `double_pendulum` | `ok` | `6.0090107704951414e+00` | `5.9965534507707101e+00|6.0214680902195630e+00` | `5.0263508633019427e-12` |
| `local_Gauss6_FullVA` | `four_link` | `ok` | `5.0528931248450188e+00` | `4.4457909628886316e+00|5.6599952868014061e+00` | `4.7075232600946038e-11` |
| `local_Gauss6_FullVA` | `slider_crank` | `ok` | `6.3108972490961275e+00` | `6.4767331590471544e+00|6.1450613391450997e+00` | `1.6179349388023567e-09` |
| `vp2024_coordinate_partitioning_rA` | `single_pendulum` | `ok` | `-3.5286613417865970e-15` | `0.0000000000000000e+00|0.0000000000000000e+00` | `1.1102230246251565e-16` |
| `vp2024_coordinate_partitioning_rA` | `double_pendulum` | `ok` | `1.4037663832547063e+00` | `1.2222938292036851e+00|1.5852389373057281e+00` | `3.6540878301565480e-03` |
| `vp2024_coordinate_partitioning_rA` | `four_link` | `ok` | `1.6484873456452285e+00` | `6.1268912685712298e+00|-2.8299165772807884e+00` | `4.4932946252629336e-12` |
| `vp2024_coordinate_partitioning_rA` | `slider_crank` | `ok` | `1.0626008446907540e+00` | `1.3303883746645189e+00|7.9481331471698813e-01` | `3.1173674752693614e-13` |

This larger-step audit is diagnostic evidence for the VP coordinate-partitioning comparison. It is not a replacement for the full 13-method coarse matrix.
