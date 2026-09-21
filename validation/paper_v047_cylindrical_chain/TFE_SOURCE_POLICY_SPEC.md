# TFE Source-Policy Specification

Status: **source policy extracted - candidate scaffold present; source-policy rows open**.

- Source PDF: `../../external/literature/s11044-026-10153-w.pdf`.
- Model: `rigid_pendulum_revolute_pair`.
- Mass/length/hinge radius/cmx: `10.0` / `2.0` / `0.5` / `3.09`.
- Friction coefficients mu_s/mu_d: `0.3` / `0.2`.
- Reference h for exact source reproduction: `0.0001`.
- Newton tolerance: `1e-07`.
- Source-policy rows completed: `0`.
- Source pendulum parameter model implemented: `True`.
- Frictionless planar RHS smoke implemented: `True`.
- Candidate comparator/TFE bounded/full-T10 scaffold: `True/True/True/True`.
- Gauss6 candidate smoke/source-policy DAE runner/source rows/equivalent: `True/False/0/False`.
- Candidate/source-policy boundary scaffold/use/DAE-equivalent/method-equivalent/rows: `True/diagnostic_scaffold_only_not_source_policy_reproduction/False/False/0`.
- Pendulum DAE runner implemented: `False`.
- External superiority allowed: `False`.
- Heavy numerical run invoked: `False`.

## Methods

| method | expected order | parameter |
|---|---:|---|
| `TFE_m1` | `1` | `nu=0.99` |
| `TFE_m2` | `3` | `nu=0.95` |
| `TFE_m3` | `5` | `nu=0.9` |
| `trapezoidal` | `2` | `none` |
| `Newmark_beta` | `2` | `gamma=0.5, beta=0.3` |

## Cases

| case | friction | h policy | reference h | t final |
|---|---:|---|---:|---:|
| `frictionless_pendulum` | `False` | comparison [0.003, 0.006], sweep [0.006, 0.012] | `0.0001` | `10.0` |
| `frictional_pendulum` | `True` | comparison [0.003, 0.008], large-step 0.2 | `0.0001` | `10.0` |

## Runner Gap

| obligation | satisfied |
|---|---:|
| `source_policy_spec_extracted` | `True` |
| `source_pendulum_parameter_model_implemented` | `True` |
| `frictionless_planar_rhs_smoke_implemented` | `True` |
| `absolute_coordinate_dae_residual_smoke_implemented` | `True` |
| `source_error_norm_and_output_policy_encoded` | `True` |
| `candidate_friction_law_encoded` | `True` |
| `newmark_trapezoidal_candidate_runner_smoke_implemented` | `True` |
| `tfe_m1_m2_m3_candidate_runner_smoke_implemented` | `True` |
| `bounded_candidate_runner_api_implemented` | `True` |
| `full_T10_coarse_candidate_probe_implemented` | `True` |
| `pendulum_dae_runner_implemented` | `False` |
| `brown_mcphee_friction_law_implemented` | `False` |
| `tfe_m1_m2_m3_runner_implemented` | `False` |
| `newmark_trapezoidal_runner_implemented` | `False` |
| `gauss6_fullva_on_source_pendulum_implemented` | `False` |
| `gauss6_fullva_source_pendulum_candidate_smoke_implemented` | `True` |
| `gauss6_fullva_source_pendulum_candidate_smoke_source_policy_rows_completed` | `0` |
| `gauss6_fullva_absolute_coordinate_source_policy_dae_runner_implemented` | `False` |
| `gauss6_fullva_absolute_coordinate_source_policy_dae_runner_equivalent` | `False` |
| `source_policy_rows_completed` | `0` |
| `external_superiority_allowed` | `False` |

## Candidate/Source-Policy Boundary

| item | value |
|---|---|
| `candidate_scaffold_present` | `True` |
| `candidate_scaffold_allowed_use` | `diagnostic_scaffold_only_not_source_policy_reproduction` |
| `source_policy_runner_required_for_promotion` | `True` |
| `gauss6_fullva_candidate_smoke_available` | `True` |
| `gauss6_fullva_candidate_smoke_allowed_use` | `candidate_smoke_only_not_source_policy_dae_runner` |
| `gauss6_fullva_candidate_smoke_source_policy_rows_completed` | `0` |
| `gauss6_fullva_absolute_coordinate_source_policy_dae_runner_required` | `True` |
| `gauss6_fullva_absolute_coordinate_source_policy_dae_runner_implemented` | `False` |
| `gauss6_fullva_absolute_coordinate_source_policy_dae_runner_equivalent` | `False` |
| `gauss6_fullva_absolute_coordinate_source_policy_dae_runner_rows_completed` | `0` |
| `source_policy_dae_runner_equivalent` | `False` |
| `source_policy_method_runner_equivalent` | `False` |
| `source_policy_rows_completed` | `0` |
| `external_superiority_allowed` | `False` |

Candidate scaffolds support implementation and diagnostic review only; promotion requires the listed source-policy runner obligations.

## Claim Policy

- Allowed now: source-policy specification extraction and formal order-target discussion.
- Forbidden now: completed original TFE reproduction, source-policy superiority, full friction-law encoding, and submission readiness.
