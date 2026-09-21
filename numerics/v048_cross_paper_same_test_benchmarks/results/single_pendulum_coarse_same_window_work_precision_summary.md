# Single-Pendulum Coarse Same-Window Work/Precision

Status: **coarse-first evidence only; not external superiority**

- Selected window: `T=3.0`, `h=0.1|0.05|0.025`.
- Reference h: `0.0125`.
- Rows: `4/4`.
- Default policy: `coarse_first_no_default_1e-4`.

Reading rule: this artifact intentionally avoids default `1e-4` rows.

| Method | Pos. order | Vel. order | Acc./omega order | Finest pos error | Finest vel error | Runtime ratio vs rA |
|---|---:|---:|---:|---:|---:|---:|
| `Gauss6/FullVA-public-horizon-single-coarse` | 6.0536844057777284e+00 | 2.9512084019522611e+00 | 1.6776718859354993e+00 | 6.0049155547547005e-14 | 8.1802564919008774e-11 | 3.2825731371952624e+00 |
| `rA-public-dynamics-coarse` | 1.2935249923518318e-05 | 1.2112827155787522e+00 | 2.0703764779305294e+00 | 1.2877732213922854e-09 | 1.6978660358093418e+01 | 1.0000000000000000e+00 |
| `reps-public-dynamics-coarse` | 1.1318371986421942e-05 | 1.2112827155787473e+00 | 2.0703764779305960e+00 | 1.2877714450354460e-09 | 1.6978660358093588e+01 | 1.4032469695961844e+00 |
| `rp-public-dynamics-coarse` | 2.8547475125053592e-05 | 1.0479039687095881e+00 | 2.0463396589486225e+00 | 1.6551238157802572e-09 | 1.5474440030363905e+01 | 2.2198034590482747e+00 |
