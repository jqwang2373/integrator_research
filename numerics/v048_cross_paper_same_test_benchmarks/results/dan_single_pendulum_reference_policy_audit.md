# Dan/Kissel/Negrut Single-Pendulum Reference-Policy Audit

Status: **repaired by fixed-grid replay**.

The old negative orders are retracted. The repaired rows are safe only as common-reference coarse apples-to-apples rows, not as source-policy reproduction.

| Method | common-reference vel order | common-reference finest vel error | public same-window vel order | public same-window finest vel error | source-policy vel order | source-policy finest vel error | status |
|---|---:|---:|---:|---:|---:|---:|---|
| `ra2021_rA` | `6.1685108829740876e-01` | `1.3048835859820088e+01` | `1.2112827155787522e+00` | `1.6978660358093418e+01` | `5.0947226808572510e-01` | `5.7580836862149876e-01` | `repaired_fixed_grid_apples_to_apples_row` |
| `ra2021_reps` | `6.1685109004913041e-01` | `1.3048835859331048e+01` | `1.2112827155787473e+00` | `1.6978660358093588e+01` | `5.0947226808574331e-01` | `5.7580836862148355e-01` | `repaired_fixed_grid_apples_to_apples_row` |
| `ra2021_rp` | `5.1681250447797089e-01` | `1.4989978093112290e+01` | `1.0479039687095881e+00` | `1.5474440030363905e+01` | `5.0077047183675816e-01` | `5.7583167674917235e-01` | `repaired_fixed_grid_apples_to_apples_row` |

Paper-safe reading: use the repaired rows only inside the fixed-grid common-reference matrix; do not claim they reproduce the source paper policy.
