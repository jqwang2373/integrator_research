# Apples-To-Apples Policy Audit

Paper-safe rows: `44/44`.
Nonlocal paper-safe comparisons: `40`.
Public source time-grid caveat detected: `True`.
Fixed-grid wrapper present: `True`.
Source-policy reproduction: `False`.

| Method | Example | same h/reference | fixed-grid replay | paper safe | vel order | finest vel error |
|---|---|---:|---:|---:|---:|---:|
| `hi2022_rA` | `double_pendulum` | `true/true` | `true` | `true` | `1.0490615714663509e+00` | `4.9441369128544466e-05` |
| `hi2022_rA` | `four_link` | `true/true` | `true` | `true` | `1.0154495376032771e+00` | `1.9704228795189360e-01` |
| `hi2022_rA` | `single_pendulum` | `true/true` | `true` | `true` | `1.0048086154087903e+00` | `7.7245125691446065e-02` |
| `hi2022_rA` | `slider_crank` | `true/true` | `true` | `true` | `9.4051356277214782e-01` | `3.2807249617700630e-02` |
| `hi2022_rA_half` | `double_pendulum` | `true/true` | `true` | `true` | `-7.9899483617845046e-01` | `2.9699545025454039e+00` |
| `hi2022_rA_half` | `four_link` | `true/true` | `true` | `true` | `1.5896477837323830e+00` | `1.9704228794818812e-01` |
| `hi2022_rA_half` | `single_pendulum` | `true/true` | `true` | `true` | `1.8406313645741985e+00` | `7.7245125691111166e-02` |
| `hi2022_rA_half` | `slider_crank` | `true/true` | `true` | `true` | `2.4585355719204536e+00` | `3.2807249645112481e-02` |
| `local_Gauss6_FullVA` | `double_pendulum` | `true/true` | `true` | `true` | `6.0097049897199657e+00` | `2.3455890008072799e-13` |
| `local_Gauss6_FullVA` | `four_link` | `true/true` | `true` | `true` | `6.0848187309877098e+00` | `1.0927703186780491e-11` |
| `local_Gauss6_FullVA` | `single_pendulum` | `true/true` | `true` | `true` | `5.8013285781956512e+00` | `1.1551877762897842e-12` |
| `local_Gauss6_FullVA` | `slider_crank` | `true/true` | `true` | `true` | `7.3409145102638718e+00` | `9.1888510689308589e-12` |
| `ra2021_rA` | `double_pendulum` | `true/true` | `true` | `true` | `1.0524410322831526e+00` | `4.9241208753159071e-05` |
| `ra2021_rA` | `four_link` | `true/true` | `true` | `true` | `1.0154496752651214e+00` | `1.9704229997398626e-01` |
| `ra2021_rA` | `single_pendulum` | `true/true` | `true` | `true` | `6.1685108829740876e-01` | `1.3048835859820088e+01` |
| `ra2021_rA` | `slider_crank` | `true/true` | `true` | `true` | `9.4052367340401100e-01` | `3.2806789771223969e-02` |
| `ra2021_reps` | `double_pendulum` | `true/true` | `true` | `true` | `1.0524410322506259e+00` | `4.9241208755379517e-05` |
| `ra2021_reps` | `four_link` | `true/true` | `true` | `true` | `2.8937856370268396e+00` | `1.4577680790537340e-02` |
| `ra2021_reps` | `single_pendulum` | `true/true` | `true` | `true` | `6.1685109004913041e-01` | `1.3048835859331048e+01` |
| `ra2021_reps` | `slider_crank` | `true/true` | `true` | `true` | `9.4049617308149369e-01` | `3.2806989825758422e-02` |
| `ra2021_rp` | `double_pendulum` | `true/true` | `true` | `true` | `3.6138964506466209e-01` | `5.2409826098226073e-05` |
| `ra2021_rp` | `four_link` | `true/true` | `true` | `true` | `2.8937319455975068e+00` | `1.4578766190558312e-02` |
| `ra2021_rp` | `single_pendulum` | `true/true` | `true` | `true` | `5.1681250447797089e-01` | `1.4989978093112290e+01` |
| `ra2021_rp` | `slider_crank` | `true/true` | `true` | `true` | `9.4046112904867141e-01` | `3.2806857900343982e-02` |
| `tfe2026_Newmark_beta` | `double_pendulum` | `true/true` | `true` | `true` | `1.7865093685563540e+00` | `4.2455003435534419e-04` |
| `tfe2026_Newmark_beta` | `four_link` | `true/true` | `true` | `true` | `1.8724735896635301e+00` | `1.6721971482511755e-02` |
| `tfe2026_Newmark_beta` | `single_pendulum` | `true/true` | `true` | `true` | `9.0079709543472231e-01` | `1.4790935093291326e+01` |
| `tfe2026_Newmark_beta` | `slider_crank` | `true/true` | `true` | `true` | `2.0511649404517280e+00` | `1.5312303900446508e-03` |
| `tfe2026_TFE_m1` | `double_pendulum` | `true/true` | `true` | `true` | `1.9960575232876485e+00` | `2.7079647030569566e-04` |
| `tfe2026_TFE_m1` | `four_link` | `true/true` | `true` | `true` | `3.8656552505883761e+00` | `5.2533587706848905e-04` |
| `tfe2026_TFE_m1` | `single_pendulum` | `true/true` | `true` | `true` | `1.0208211940993241e+00` | `1.4982446288217862e+01` |
| `tfe2026_TFE_m1` | `slider_crank` | `true/true` | `true` | `true` | `2.4813573655672228e+00` | `6.2636005420357160e-04` |
| `tfe2026_TFE_m2` | `double_pendulum` | `true/true` | `true` | `true` | `1.8699294113299130e+00` | `8.7111007524081144e-05` |
| `tfe2026_TFE_m2` | `four_link` | `true/true` | `true` | `true` | `1.0213293368837018e+00` | `6.7113114390737749e-04` |
| `tfe2026_TFE_m2` | `single_pendulum` | `true/true` | `true` | `true` | `5.3729817787625797e-02` | `1.1022022919229548e+02` |
| `tfe2026_TFE_m2` | `slider_crank` | `true/true` | `true` | `true` | `2.2898993941964103e+00` | `9.8806935735641643e-05` |
| `tfe2026_trapezoidal` | `double_pendulum` | `true/true` | `true` | `true` | `1.9996592986304731e+00` | `2.7080818333363559e-04` |
| `tfe2026_trapezoidal` | `four_link` | `true/true` | `true` | `true` | `3.8881084589425803e+00` | `5.3058211830681046e-04` |
| `tfe2026_trapezoidal` | `single_pendulum` | `true/true` | `true` | `true` | `1.0244641243403070e+00` | `1.4982640405168288e+01` |
| `tfe2026_trapezoidal` | `slider_crank` | `true/true` | `true` | `true` | `2.3293486660896003e+00` | `7.3277595798711820e-04` |
| `vp2024_coordinate_partitioning_rA` | `double_pendulum` | `true/true` | `true` | `true` | `1.0000540448902970e+00` | `2.1651164257470200e-03` |
| `vp2024_coordinate_partitioning_rA` | `four_link` | `true/true` | `true` | `true` | `-5.3315082332409090e-04` | `1.0874561251483783e-08` |
| `vp2024_coordinate_partitioning_rA` | `single_pendulum` | `true/true` | `true` | `true` | `6.1493372218877035e-15` | `3.1628033526739321e-11` |
| `vp2024_coordinate_partitioning_rA` | `slider_crank` | `true/true` | `true` | `true` | `-3.2531547519751702e-07` | `1.3318257655048349e-07` |

The common-reference matrix is paper-safe only as a coarse apples-to-apples final-state comparison. It is not a reproduction of the source papers' default time horizons or h policies. Public-code rows are accepted only after fixed-grid replay on t_i=i*h.
