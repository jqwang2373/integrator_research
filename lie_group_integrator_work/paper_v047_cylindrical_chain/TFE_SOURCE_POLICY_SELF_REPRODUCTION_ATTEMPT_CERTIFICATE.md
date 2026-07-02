# TFE Source-Policy Self-Reproduction Attempt Certificate

Status: **attempted not reproducible; not promoted**.

- Rows audited: `16`.
- Self-reproduction attempted rows: `16`.
- Attempted-not-reproducible rows: `16`.
- Unable-to-reproduce rows: `16`.
- Final nonpublic-code disposition: `unable_to_reproduce_not_promoted`.
- Source-policy closed rows: `0`.
- External-superiority ready rows: `0`.
- Public-code recheck status/repo hits/user hits/code-search/attempted/closed: `public_code_rechecked_no_distinct_tfe_code_artifact_attempted_not_reproducible/0/0/requires_authentication/16/0`.
- Latest public-code refresh status/date/rows/queries/positive/closed: `public_code_refresh_20260620_no_positive_new_source_artifact_rows_remain_unable_to_reproduce/2026-06-20/20/11/0/0/20`.
- Single-pendulum attempted / source-scope-unsupported mechanism rows: `4/12`.
- Candidate same-test raw/summary/ok rows: `18/6/18`.
- Source-method candidate contract rows/B4 coverage/source rows/equivalent method/DAE: `5/4/0/False/False`.
- Source-method candidate contract finite/residual-below-1e-8/max residual: `True/True/3.204e-11`.
- Gauss6/FullVA DAE candidate contract rows/source rows/equivalent DAE/FullVA: `1/0/False/False`.
- Full-T10 DAE-lift completed / step residual rows: `True/2800`.
- Source-policy DAE/method/monolithic equivalence: `False/False/False`.
- Brown--McPhee source law / transition policy / full-T10 grid policy: `False/False/False`.
- Non-heavy negative certificates Brown/endpoint status: `negative_source_code_equivalence_certificate_not_source_policy/negative_full_T10_endpoint_policy_certificate_not_source_policy`.
- Non-heavy certificates closed source-policy rows/blocks: `0/False`.
- Source-policy execution preflight status/blocks/ready/promote: `terminal_no_public_code_self_reproduction_attempted_not_promoted/4/False/False`.
- Source-policy execution preflight route/reopen/source rows: `no_public_code_self_reproduction_attempted_unable_to_reproduce_not_promoted/new_public_or_source_code_equivalent_tfe_implementation_artifact/0`.

## Required Next Actions

- Keep TFE source-policy rows attempted-not-reproducible/not-promoted under the current no_public_code_self_reproduction_attempted_unable_to_reproduce_not_promoted route.
- Reopen the TFE source-policy lane only if a new public or source-code-equivalent TFE implementation artifact appears.
- Do not execute or promote TFE source-policy work/precision rows until the required runner contracts exist: monolithic_absolute_coordinate_DAE_time_integrator, TFE_m1_m2_m3_Newmark_beta_trapezoidal_source_policy_method_runners, Gauss6_FullVA_absolute_coordinate_source_policy_DAE_runner, accepted_T10_source_policy_work_precision_rows.

## B4 Method Summary

| method | candidate rows | velocity floor | finest velocity error | source-policy row |
|---|---:|---:|---:|---:|
| `tfe2026_Newmark_beta` | `3` | `1.996` | `1.901e-04` | `False` |
| `tfe2026_TFE_m1` | `3` | `1.516` | `5.600e-04` | `False` |
| `tfe2026_TFE_m2` | `3` | `3.074` | `7.509e-08` | `False` |
| `tfe2026_trapezoidal` | `3` | `1.997` | `2.416e-04` | `False` |

## Row Disposition

| method | example | disposition | reason |
|---|---|---|---|
| `tfe2026_Newmark_beta` | `single_pendulum` | `attempted_not_reproducible` | `paper_spec_candidate_runner_not_source_policy_equivalent` |
| `tfe2026_Newmark_beta` | `double_pendulum` | `attempted_not_reproducible` | `tfe_source_paper_pendulum_suite_does_not_define_this_mechanism_runner` |
| `tfe2026_Newmark_beta` | `four_link` | `attempted_not_reproducible` | `tfe_source_paper_pendulum_suite_does_not_define_this_mechanism_runner` |
| `tfe2026_Newmark_beta` | `slider_crank` | `attempted_not_reproducible` | `tfe_source_paper_pendulum_suite_does_not_define_this_mechanism_runner` |
| `tfe2026_TFE_m1` | `single_pendulum` | `attempted_not_reproducible` | `paper_spec_candidate_runner_not_source_policy_equivalent` |
| `tfe2026_TFE_m1` | `double_pendulum` | `attempted_not_reproducible` | `tfe_source_paper_pendulum_suite_does_not_define_this_mechanism_runner` |
| `tfe2026_TFE_m1` | `four_link` | `attempted_not_reproducible` | `tfe_source_paper_pendulum_suite_does_not_define_this_mechanism_runner` |
| `tfe2026_TFE_m1` | `slider_crank` | `attempted_not_reproducible` | `tfe_source_paper_pendulum_suite_does_not_define_this_mechanism_runner` |
| `tfe2026_TFE_m2` | `single_pendulum` | `attempted_not_reproducible` | `paper_spec_candidate_runner_not_source_policy_equivalent` |
| `tfe2026_TFE_m2` | `double_pendulum` | `attempted_not_reproducible` | `tfe_source_paper_pendulum_suite_does_not_define_this_mechanism_runner` |
| `tfe2026_TFE_m2` | `four_link` | `attempted_not_reproducible` | `tfe_source_paper_pendulum_suite_does_not_define_this_mechanism_runner` |
| `tfe2026_TFE_m2` | `slider_crank` | `attempted_not_reproducible` | `tfe_source_paper_pendulum_suite_does_not_define_this_mechanism_runner` |
| `tfe2026_trapezoidal` | `single_pendulum` | `attempted_not_reproducible` | `paper_spec_candidate_runner_not_source_policy_equivalent` |
| `tfe2026_trapezoidal` | `double_pendulum` | `attempted_not_reproducible` | `tfe_source_paper_pendulum_suite_does_not_define_this_mechanism_runner` |
| `tfe2026_trapezoidal` | `four_link` | `attempted_not_reproducible` | `tfe_source_paper_pendulum_suite_does_not_define_this_mechanism_runner` |
| `tfe2026_trapezoidal` | `slider_crank` | `attempted_not_reproducible` | `tfe_source_paper_pendulum_suite_does_not_define_this_mechanism_runner` |

The self-reproduction reaches a paper-spec candidate layer with same-test work/precision, a five-method candidate dispatch contract, absolute-coordinate residual checks, and a full-T10 DAE-lift diagnostic. The current package also carries negative Brown--McPhee source-code-equivalence and full-T10 endpoint-policy certificates; those certificates document non-promotion boundaries but close zero source-policy rows. The package still lacks source-code-equivalent method runners, a monolithic absolute-coordinate source-policy DAE integrator, a Gauss6/FullVA source-policy runner, and accepted source-policy work/precision row bindings.
