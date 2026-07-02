# Coarse-First External Readiness Gate

Status: **not submission ready; no external superiority claim**

- Default policy: `coarse_first_no_default_1e-4`.
- Coarse step sizes: `0.1|0.05|0.025`.
- Coarse reference h: `0.0125`.
- Coarse same-window ready examples: `2/4`.
- Local true-dynamic order available examples: `2`.
- Public work/precision available examples: `2`.
- Public work/precision missing examples: `0`.
- Strict common-reference available examples: `2`.
- Strict common-reference gap examples: `0`.
- Strict common-reference figure available: `True`.
- Closed-loop surrogate available examples: `0`.
- Closed-loop floor-audit available examples: `2`.
- Dynamic-order missing examples: `0`.
- Same-test campaign status: `not_run`.

Reading rule: `1e-4` is not a default execution target. Use it only for strict source-paper/public-code policy reproduction.

| Example | Readiness | Local status | Public baseline | Current order evidence | Next lightweight action | Blocker |
|---|---|---|---|---|---|---|
| `single_pendulum` | `coarse_same_window_order_time_available` | `3/3 coarse local rows ok` | 9/9 coarse public rows ok | Gauss6/FullVA pos/vel order 6.054/2.951; public rA/reps vel order 1.211/1.211; position columns near the public/reference floor are diagnostics. | Use this as the single-pendulum coarse-first row; do not rerun source h=1e-4 unless strict source-policy reproduction is explicitly requested. | Single-pendulum coarse evidence is available; full external superiority still requires public work/precision comparison for the closed-loop true-dynamic rows. |
| `double_pendulum` | `coarse_same_window_order_time_available` | `completed_public_horizon_coarse_double_pilot` | 6/9 coarse public rows ok | Gauss6/FullVA pos/vel order 7.951/7.042; public rA/reps pos/vel order 0.703/0.754; rp nonconverged | Use this as the coarse-first template; do not rerun source h=1e-4 unless strict source-policy reproduction is explicitly requested. | Closed-loop local true-dynamic order is now available, but same-window public work/precision comparison is still missing for four_link and slider_crank. |
| `four_link` | `local_true_dynamic_order_public_work_and_strict_common_reference_available` | `completed_public_horizon_residual_trio` | 3/3 public forms completed in matrix | Local true-dynamic Newton coarse row available: pos/orient/vel/omega order 5.955/5.955/6.085/5.971; stage oracle used=false; endpoint acceleration remains diagnostic. | Integrate the strict common-reference work/precision figure into the manuscript and keep source h=1e-4 opt-in. | Strict common-reference rows are available, but external superiority still needs publication-quality figure integration and the broader external-suite closure decisions. |
| `slider_crank` | `local_true_dynamic_order_public_work_and_strict_common_reference_available` | `completed_public_horizon_residual_trio` | 3/3 public forms completed in matrix | Local true-dynamic Newton coarse row available: pos/orient/vel/omega order 6.164/6.159/7.341/6.426; stage oracle used=false; endpoint acceleration remains diagnostic. | Integrate the strict common-reference work/precision figure into the manuscript and keep source h=1e-4 opt-in. | Strict common-reference rows are available, but external superiority still needs publication-quality figure integration and the broader external-suite closure decisions. |
