# Closed-Loop True-Dynamic Strict Common Reference

Status: **strict common reference error columns available not external superiority**

- Rows: `24/24` ok.
- Strict common-reference examples available: `2`.
- Strict common-reference examples missing: `0`.
- Common reference: `v047_exact_kinematic_endpoint`, `h=0.0125`.
- Error columns: `pos_final_linf, vel_final_linf, acc_final_linf`.
- Acceleration column diagnostic: `True`.
- Publication figure available: `True`.
- Default `1e-4` required: `False`.
- External superiority claim: `False`.

The public `rA/rp/reps` rows are recomputed against the same v047 exact
endpoint reference used by the local true-dynamic Newton rows. This removes
the previous mixed-reference caveat for the tabulated translational error
columns. It still does not claim external superiority; broader baseline
coverage, figure integration, and paper review remain open.

| Model | Method | ok | pos order | vel order | acc order | finest pos | finest vel | runtime sum | pos ratio vs rA | vel ratio vs rA |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `four_link` | `Gauss6/FullVA-local-true-dynamic-newton` | `3/3` | `5.9548979111188078e+00` | `6.0848187309877098e+00` | `9.9466887815859806e-01` | `2.2888357875672227e-12` | `1.0927703186780491e-11` | `2.4778123860014603e+00` | `2.4318658795297808e-04` | `6.9953040932936633e-12` |
| `four_link` | `rA-public-dynamics` | `3/3` | `1.2745492529773102e+01` | `3.2298044389314925e-02` | `-1.0437389978219225e-01` | `9.4118504101459166e-09` | `1.5621484128555303e+00` | `1.6871375299524516e-01` | `1.0000000000000000e+00` | `1.0000000000000000e+00` |
| `four_link` | `reps-public-dynamics` | `3/3` | `1.2293793673936442e+01` | `1.9481803853809745e-01` | `8.9114006069334040e-01` | `1.7604545821114925e-08` | `1.2470259919663840e+00` | `1.2135473801754415e-01` | `1.8704659608845178e+00` | `7.9827625960767834e-01` |
| `four_link` | `rp-public-dynamics` | `3/3` | `1.5169760592507044e+01` | `1.9481660236170303e-01` | `5.8720829901825611e-01` | `3.2667824001464396e-10` | `1.2470284747517613e+00` | `6.4621153986081481e-02` | `3.4709246936445871e-02` | `7.9827784894794640e-01` |
| `slider_crank` | `Gauss6/FullVA-local-true-dynamic-newton` | `3/3` | `6.1636896425143544e+00` | `7.3409145102638718e+00` | `1.0541648128408896e+00` | `8.5831619589527008e-12` | `9.1888510689308589e-12` | `3.0849206619895995e+00` | `2.8626689930603662e-05` | `1.0641429717615531e-10` |
| `slider_crank` | `rA-public-dynamics` | `3/3` | `8.1294265914235506e+00` | `6.8495159529704808e-01` | `-3.2736056378739958e-01` | `2.9983075164330408e-07` | `8.6349779238027446e-02` | `1.0957849596161395e-01` | `1.0000000000000000e+00` | `1.0000000000000000e+00` |
| `slider_crank` | `reps-public-dynamics` | `3/3` | `1.1486414169025977e+01` | `6.8495294155236064e-01` | `3.7094842846990023e-01` | `2.8560661474719140e-09` | `8.6349618083053858e-02` | `7.4155008886009455e-02` | `9.5255944622706836e-03` | `9.9999813369559243e-01` |
| `slider_crank` | `rp-public-dynamics` | `3/3` | `1.0182223846947595e+01` | `6.8495292204078639e-01` | `6.7292056644532097e-02` | `1.7416828507199611e-08` | `8.6349620418706197e-02` | `8.8363854098133743e-02` | `5.8088866507994726e-02` | `9.9999816074432790e-01` |
