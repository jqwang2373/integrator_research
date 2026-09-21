# Closed-Loop Coarse Dynamic-Order Probe

Status: **coarse probe only; accepted dynamic order remains zero**

- Default policy: `coarse_first_no_default_1e-4`.
- Step sizes: `0.1|0.05|0.025`; reference h: `0.0125`.
- Raw rows: `11/12` ok.
- Failed public rows: `1`.
- Work-summary rows: `4`.
- Local velocity evidence rows: `2/2`.
- Local acceleration evidence rows: `2/2`.
- Local position-floor rows: `2/2`.
- Accepted dynamic order rows: `0`.
- External superiority claim: `False`.

Reading rule: this artifact checks whether larger steps remove the closed-loop floor issue. It does not run default `1e-4` rows and does not turn kinematic/reaction rows into accepted dynamic trajectory rows.

Failed-row detail:

- `slider_crank` / `rA-public-dynamics` at `h=0.1`: `failed:ValueError:array must not contain infs or NaNs`.

| Model | Method | pos order | vel order | acc order | finest pos ratio | finest vel ratio | finest acc ratio | runtime ratio |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| `four_link` | `Gauss6/FullVA-local-closed-loop` | 1.9403193345764578e-07 | 2.3244109689721458e-07 | 1.1336575709753103e-07 | 1.4708800469499048e+01 | 2.1790551337525013e-08 | 1.7425119411121874e-08 | 9.0045222900889521e-01 |
| `four_link` | `rA-public-dynamics` | 2.1844222396597537e-01 | 1.5962049561937834e+00 | 1.6569267244763928e+00 | 1.0000000000000000e+00 | 1.0000000000000000e+00 | 1.0000000000000000e+00 | 1.0000000000000000e+00 |
| `slider_crank` | `Gauss6/FullVA-local-closed-loop` | 8.3745356968629436e-10 | -4.0436730753548902e-10 | -3.2407616528348959e-10 | 2.9812632330797294e+02 | 5.6468453350086487e-06 | 1.3865384920162775e-06 | 1.1235716039732297e+00 |
| `slider_crank` | `rA-public-dynamics` | -1.0098308617650038e+00 | 1.3379980169307284e+00 | 1.2841527250780693e+00 | 1.0000000000000000e+00 | 1.0000000000000000e+00 | 1.0000000000000000e+00 | 1.0000000000000000e+00 |
