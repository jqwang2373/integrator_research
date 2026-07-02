# TFE Endpoint-Policy Sensitivity Audit

Status: **diagnostic endpoint-policy sensitivity; not source-policy closure**.

- Source-policy rows completed: `0`.
- Methods/policies/raw rows: `4/4/48`.
- Nominal h values: `[0.012, 0.006, 0.003]`.
- External superiority claim allowed: `False`.

## Method Sensitivity Summary

| method | velocity-order spread | finest velocity-error ratio |
|---|---:|---:|
| `tfe2026_Newmark_beta` | `0.00542356` | `1.00129` |
| `tfe2026_TFE_m1` | `0.0726852` | `1.00035` |
| `tfe2026_TFE_m2` | `0.0370532` | `1.02661` |
| `tfe2026_trapezoidal` | `0.00578138` | `1.00137` |

## Policy Rows

| policy | method | terminal times | velocity orders | finest velocity error |
|---|---|---|---|---:|
| `adjust_h_to_hit_T_exactly` | `tfe2026_Newmark_beta` | `[10.0, 10.0, 10.0]` | `[2.001613446673431, 1.9991051707782062]` | `6.688762e-05` |
| `adjust_h_to_hit_T_exactly` | `tfe2026_TFE_m1` | `[10.0, 10.0, 10.0]` | `[0.8643996442881129, 0.9360045737874282]` | `1.193936e-03` |
| `adjust_h_to_hit_T_exactly` | `tfe2026_TFE_m2` | `[10.0, 10.0, 10.0]` | `[2.994655984487747, 3.025313727217761]` | `4.055358e-09` |
| `adjust_h_to_hit_T_exactly` | `tfe2026_trapezoidal` | `[10.0, 10.0, 10.0]` | `[2.0016305383442115, 1.999109881004081]` | `5.126901e-05` |
| `algorithm_literal_fixed_h_until_tn_ge_tfinal` | `tfe2026_Newmark_beta` | `[10.008, 10.002, 10.002]` | `[2.003493460863907, 1.9999711328226417]` | `6.693157e-05` |
| `algorithm_literal_fixed_h_until_tn_ge_tfinal` | `tfe2026_TFE_m1` | `[10.008, 10.002, 10.002]` | `[0.8640890476934001, 0.9363605727868647]` | `1.194097e-03` |
| `algorithm_literal_fixed_h_until_tn_ge_tfinal` | `tfe2026_TFE_m2` | `[10.008, 10.002, 10.002]` | `[2.992781010533251, 2.988859666965654]` | `4.163289e-09` |
| `algorithm_literal_fixed_h_until_tn_ge_tfinal` | `tfe2026_trapezoidal` | `[10.008, 10.002, 10.002]` | `[2.003738103426359, 1.9999767354467843]` | `5.130543e-05` |
| `floor_horizon` | `tfe2026_Newmark_beta` | `[9.996, 9.996, 9.999]` | `[1.9998794125894865, 1.998069901489816]` | `6.684530e-05` |
| `floor_horizon` | `tfe2026_TFE_m1` | `[9.996, 9.996, 9.999]` | `[0.8638810952904655, 0.9359758259517841]` | `1.193682e-03` |
| `floor_horizon` | `tfe2026_TFE_m2` | `[9.996, 9.996, 9.999]` | `[2.991866402828207, 2.988260523436871]` | `4.161952e-09` |
| `floor_horizon` | `tfe2026_trapezoidal` | `[9.996, 9.996, 9.999]` | `[1.9998971523075002, 1.9979567243515972]` | `5.123514e-05` |
| `integer_steps_plus_final_partial_step` | `tfe2026_Newmark_beta` | `[10.0, 10.0, 10.0]` | `[1.9997164491777033, 1.9998050053631078]` | `6.686919e-05` |
| `integer_steps_plus_final_partial_step` | `tfe2026_TFE_m1` | `[10.0, 10.0, 10.0]` | `[0.8637388080826394, 0.936424034707735]` | `1.193822e-03` |
| `integer_steps_plus_final_partial_step` | `tfe2026_TFE_m2` | `[10.0, 10.0, 10.0]` | `[2.991857092647576, 2.9892614030780993]` | `4.161079e-09` |
| `integer_steps_plus_final_partial_step` | `tfe2026_trapezoidal` | `[10.0, 10.0, 10.0]` | `[1.9996834961193266, 1.9997602188520125]` | `5.125366e-05` |

Endpoint-policy choices can be measured with the current planar candidate runner, but this does not resolve the source paper's error-sampling convention or prove source-policy equivalence.
