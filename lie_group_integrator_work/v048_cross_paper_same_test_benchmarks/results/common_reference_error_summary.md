# Common-Reference Error Audit

Step sizes: `[0.1, 0.05, 0.025]`; reference h: `0.0125`; t_end: `0.1`.
Runnable methods audited: `11`.
Omitted methods: `{"tfe2026_TFE_m3_GL": "source_backed_scope_excluded_four_link"}`.
Alias methods: `{"vp2024_lie_group_ode_partitioning": "vp2024_coordinate_partitioning_rA"}`.

Local velocity-order wins: `40/40`.
Local finest-velocity-error wins: `40/40`.
Original-paper finest-velocity-error wins: `16/16`.
Kissel/Negrut-family finest-velocity-error wins: `24/24`.
Direct all-row error superiority claim: `True`.
Apples-to-apples coarse claim: `True`.
Source-policy reproduction: `False`.
Public-code fixed-grid replay: `True`.

| Example | Method | status | norm | vel order | finest vel error | ratio vs local | local error win | local order win |
|---|---|---:|---|---:|---:|---:|---:|---:|
| `double_pendulum` | `hi2022_rA` | `ok` | `final_linf` | `1.0490615714663509e+00` | `4.9441369128544466e-05` | `2.1078445163039330e+08` | `true` | `true` |
| `four_link` | `hi2022_rA` | `ok` | `final_linf` | `1.0154495376032771e+00` | `1.9704228795189360e-01` | `1.8031445820221439e+10` | `true` | `true` |
| `single_pendulum` | `hi2022_rA` | `ok` | `final_l2` | `1.0048086154087903e+00` | `7.7245125691446065e-02` | `6.6868025507974876e+10` | `true` | `true` |
| `slider_crank` | `hi2022_rA` | `ok` | `final_linf` | `9.4051356277214782e-01` | `3.2807249617700630e-02` | `3.5703320656298132e+09` | `true` | `true` |
| `double_pendulum` | `hi2022_rA_half` | `ok` | `final_linf` | `-7.9899483617845046e-01` | `2.9699545025454039e+00` | `1.2661870862812012e+13` | `true` | `true` |
| `four_link` | `hi2022_rA_half` | `ok` | `final_linf` | `1.5896477837323830e+00` | `1.9704228794818812e-01` | `1.8031445819882351e+10` | `true` | `true` |
| `single_pendulum` | `hi2022_rA_half` | `ok` | `final_l2` | `1.8406313645741985e+00` | `7.7245125691111166e-02` | `6.6868025507684967e+10` | `true` | `true` |
| `slider_crank` | `hi2022_rA_half` | `ok` | `final_linf` | `2.4585355719204536e+00` | `3.2807249645112481e-02` | `3.5703320686129775e+09` | `true` | `true` |
| `double_pendulum` | `local_Gauss6_FullVA` | `ok` | `final_linf` | `6.0097049897199657e+00` | `2.3455890008072799e-13` | `nan` | `nan` | `nan` |
| `four_link` | `local_Gauss6_FullVA` | `ok` | `final_linf` | `6.0848187309877098e+00` | `1.0927703186780491e-11` | `nan` | `nan` | `nan` |
| `single_pendulum` | `local_Gauss6_FullVA` | `ok` | `final_l2` | `5.8013285781956512e+00` | `1.1551877762897842e-12` | `nan` | `nan` | `nan` |
| `slider_crank` | `local_Gauss6_FullVA` | `ok` | `final_linf` | `7.3409145102638718e+00` | `9.1888510689308589e-12` | `nan` | `nan` | `nan` |
| `double_pendulum` | `ra2021_rA` | `ok` | `final_linf` | `1.0524410322831526e+00` | `4.9241208753159071e-05` | `2.0993110360004142e+08` | `true` | `true` |
| `four_link` | `ra2021_rA` | `ok` | `final_linf` | `1.0154496752651214e+00` | `1.9704229997398626e-01` | `1.8031446920369610e+10` | `true` | `true` |
| `single_pendulum` | `ra2021_rA` | `ok` | `final_l2` | `6.1685108829740876e-01` | `1.3048835859820088e+01` | `1.1295856940012086e+13` | `true` | `true` |
| `slider_crank` | `ra2021_rA` | `ok` | `final_linf` | `9.4052367340401100e-01` | `3.2806789771223969e-02` | `3.5702820216718459e+09` | `true` | `true` |
| `double_pendulum` | `ra2021_reps` | `ok` | `final_linf` | `1.0524410322506259e+00` | `4.9241208755379517e-05` | `2.0993110360950789e+08` | `true` | `true` |
| `four_link` | `ra2021_reps` | `ok` | `final_linf` | `2.8937856370268396e+00` | `1.4577680790537340e-02` | `1.3340114149670825e+09` | `true` | `true` |
| `single_pendulum` | `ra2021_reps` | `ok` | `final_l2` | `6.1685109004913041e-01` | `1.3048835859331048e+01` | `1.1295856939588744e+13` | `true` | `true` |
| `slider_crank` | `ra2021_reps` | `ok` | `final_linf` | `9.4049617308149369e-01` | `3.2806989825758422e-02` | `3.5703037931134496e+09` | `true` | `true` |
| `double_pendulum` | `ra2021_rp` | `ok` | `final_linf` | `3.6138964506466209e-01` | `5.2409826098226073e-05` | `2.2343993802916119e+08` | `true` | `true` |
| `four_link` | `ra2021_rp` | `ok` | `final_linf` | `2.8937319455975068e+00` | `1.4578766190558312e-02` | `1.3341107405071728e+09` | `true` | `true` |
| `single_pendulum` | `ra2021_rp` | `ok` | `final_l2` | `5.1681250447797089e-01` | `1.4989978093112290e+01` | `1.2976226377028408e+13` | `true` | `true` |
| `slider_crank` | `ra2021_rp` | `ok` | `final_linf` | `9.4046112904867141e-01` | `3.2806857900343982e-02` | `3.5702894359959545e+09` | `true` | `true` |
| `double_pendulum` | `tfe2026_Newmark_beta` | `ok` | `final_linf` | `1.7865093685563540e+00` | `4.2455003435534419e-04` | `1.8099932861606491e+09` | `true` | `true` |
| `four_link` | `tfe2026_Newmark_beta` | `ok` | `final_linf` | `1.8724735896635301e+00` | `1.6721971482511755e-02` | `1.5302366102641525e+09` | `true` | `true` |
| `single_pendulum` | `tfe2026_Newmark_beta` | `ok` | `final_l2` | `9.0079709543472231e-01` | `1.4790935093291326e+01` | `1.2803922788030742e+13` | `true` | `true` |
| `slider_crank` | `tfe2026_Newmark_beta` | `ok` | `final_linf` | `2.0511649404517280e+00` | `1.5312303900446508e-03` | `1.6664002698030588e+08` | `true` | `true` |
| `double_pendulum` | `tfe2026_TFE_m1` | `ok` | `final_linf` | `1.9960575232876485e+00` | `2.7079647030569566e-04` | `1.1544924119805124e+09` | `true` | `true` |
| `four_link` | `tfe2026_TFE_m1` | `ok` | `final_linf` | `3.8656552505883761e+00` | `5.2533587706848905e-04` | `4.8073768850530334e+07` | `true` | `true` |
| `single_pendulum` | `tfe2026_TFE_m1` | `ok` | `final_l2` | `1.0208211940993241e+00` | `1.4982446288217862e+01` | `1.2969706393828258e+13` | `true` | `true` |
| `slider_crank` | `tfe2026_TFE_m1` | `ok` | `final_linf` | `2.4813573655672228e+00` | `6.2636005420357160e-04` | `6.8165219950229302e+07` | `true` | `true` |
| `double_pendulum` | `tfe2026_TFE_m2` | `ok` | `final_linf` | `1.8699294113299130e+00` | `8.7111007524081144e-05` | `3.7138223062139273e+08` | `true` | `true` |
| `four_link` | `tfe2026_TFE_m2` | `ok` | `final_linf` | `1.0213293368837018e+00` | `6.7113114390737749e-04` | `6.1415572187141873e+07` | `true` | `true` |
| `single_pendulum` | `tfe2026_TFE_m2` | `ok` | `final_l2` | `5.3729817787625797e-02` | `1.1022022919229548e+02` | `9.5413257874229984e+13` | `true` | `true` |
| `slider_crank` | `tfe2026_TFE_m2` | `ok` | `final_linf` | `2.2898993941964103e+00` | `9.8806935735641643e-05` | `1.0752915135356311e+07` | `true` | `true` |
| `double_pendulum` | `tfe2026_trapezoidal` | `ok` | `final_linf` | `1.9996592986304731e+00` | `2.7080818333363559e-04` | `1.1545423483842723e+09` | `true` | `true` |
| `four_link` | `tfe2026_trapezoidal` | `ok` | `final_linf` | `3.8881084589425803e+00` | `5.3058211830681046e-04` | `4.8553855209818341e+07` | `true` | `true` |
| `single_pendulum` | `tfe2026_trapezoidal` | `ok` | `final_l2` | `1.0244641243403070e+00` | `1.4982640405168288e+01` | `1.2969874433132699e+13` | `true` | `true` |
| `slider_crank` | `tfe2026_trapezoidal` | `ok` | `final_linf` | `2.3293486660896003e+00` | `7.3277595798711820e-04` | `7.9746200312764257e+07` | `true` | `true` |
| `double_pendulum` | `vp2024_coordinate_partitioning_rA` | `ok` | `final_linf` | `1.0000540448902970e+00` | `2.1651164257470200e-03` | `9.2305873919167137e+09` | `true` | `true` |
| `four_link` | `vp2024_coordinate_partitioning_rA` | `ok` | `final_linf` | `-5.3315082332409090e-04` | `1.0874561251483783e-08` | `9.9513695289958139e+02` | `true` | `true` |
| `single_pendulum` | `vp2024_coordinate_partitioning_rA` | `ok` | `final_l2` | `6.1493372218877035e-15` | `3.1628033526739321e-11` | `2.7379127598044530e+01` | `true` | `true` |
| `slider_crank` | `vp2024_coordinate_partitioning_rA` | `ok` | `final_linf` | `-3.2531547519751702e-07` | `1.3318257655048349e-07` | `1.4493931346955604e+04` | `true` | `true` |

These rows are direct final-state error comparisons under one shared reference and norm per example on the coarse h grid. Public-code baselines are replayed on fixed times t_i=i*h to avoid the source helper time-grid convention at coarse h. This is an apples-to-apples coarse comparison, not source-policy reproduction.
