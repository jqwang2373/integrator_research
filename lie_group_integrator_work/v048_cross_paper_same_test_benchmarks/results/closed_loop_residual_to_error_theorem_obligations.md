# Closed-Loop Residual-to-Error Theorem Obligations

Status: **open; residual-to-error promotion is not accepted**

- Accepted residual-to-error theorem: `False`.
- Accepted dynamic-order rows by this route: `0`.
- Blocking obligations: `7/7`.
- Default policy: `coarse_first_no_default_1e-4`.

This gate prevents the selected residual surrogate from being used as a
dynamic-order proof unless the missing theorem obligations are actually
closed. Small reaction residuals are useful evidence, but they do not by
themselves bound trajectory error or establish order.

| ID | Obligation | Status | Blocking | Next artifact |
|---|---|---|---:|---|
| `R2E-1` | dynamic residual identity | `not_satisfied` | true | `local_closed_loop_dynamic_dae_runner_or_identity_proof` |
| `R2E-2` | residual consistency rate | `partial_evidence_not_rate_proof` | true | `three_step_residual_rate_or_symbolic_defect_proof` |
| `R2E-3` | stability or inf-sup bound | `missing` | true | `closed_loop_dae_stability_bound` |
| `R2E-4` | calibrated error estimator | `partial_but_position_floor_blocked` | true | `non_floor_limited_estimator_calibration` |
| `R2E-5` | reference-floor exclusion | `not_satisfied` | true | `non_floor_limited_closed_loop_error_rows` |
| `R2E-6` | coarse-first acceptance campaign | `campaign_exists_but_not_accepted` | true | `accepted_coarse_dynamic_order_rows_or_repaired_public_baseline` |
| `R2E-7` | manuscript theorem and proof | `missing` | true | `cmame_residual_to_error_theorem_section` |

## Acceptance Rule

The residual-to-error route can close only after all blocking obligations
are satisfied, the estimator is calibrated on non-floor-limited errors,
and the manuscript contains a reviewer-defensible theorem. Until then,
`four_link` and `slider_crank` remain mechanism coverage rows, not
accepted dynamic-order rows.
