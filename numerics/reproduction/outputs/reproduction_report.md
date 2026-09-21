# Human-Runnable Reproduction Report

## Claim Boundary

- Accepted method: `Gauss6/FullVA`
- Method-order claim: `6`
- ASME gate status: `four_asme_method_rows_accepted_projection_sharp_sparse_caveats`
- `full_tfe_stage_replacement`: `False`
- `same_test_campaign_status`: `not_run`
- `external_superiority_claim`: `False`

## Rebuilt Tables

- Paper method/example matrix rows: `44`
- Work-precision summary rows: `15`
- Examples in matrix: `double_pendulum, four_link, single_pendulum, slider_crank`
- Methods in matrix: `hi2022_rA, hi2022_rA_half, local_Gauss6_FullVA, ra2021_rA, ra2021_reps, ra2021_rp, tfe2026_Newmark_beta, tfe2026_TFE_m1, tfe2026_TFE_m2, tfe2026_trapezoidal, vp2024_coordinate_partitioning_rA`

## Outputs

- `method_example_matrix.csv` / `.md`
- `work_precision_summary.csv` / `.md`
- `reproduction_manifest.json`

## Validation

- `paper numerical matrix`: `PASS`
- `v047 four-ASME minimal`: `PASS`
- `v048 performance matrix`: `PASS`
- `v048 strict common reference`: `PASS`

## Scope Notes

- This command rebuilds human-readable result summaries from existing checked artifacts.
- It does not invoke `v047_cylindrical_chain_pipeline/run_v047.py`.
- It does not run strict public-policy `1e-4` campaigns.
- It does not upgrade any open claim gate.
