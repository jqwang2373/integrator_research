# RA/HI Source-Policy Closeout Checklist

Status: `ready_for_authorized_execution_closeout_not_executed_not_promoted`.

This read-only checklist does not run guarded source-policy commands.

- Rows: RA2021 `12`, HI2022 `8`, total `20`.
- Ready commands: `13` mapped to `20` rows.
- Output inventory: `existing_expected_outputs_present_not_promotion_evidence`; outputs/summaries/data rows `13/8/54`; source-policy rows closed `0`.
- Source-policy closed/ratio: `False/0/20`.
- Promoted/completed/external-ready rows now: `0`/`0`/`0`.
- Exact authorization phrase: `I explicitly approve running the B4 source-policy execution commands listed in B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json.`.
- Source-policy execution allowed now/invoked/exact opt-in required: `False/False/True`.
- Safe action ids: `['rebuild_read_only_audit_chain', 'rerun_read_only_validators', 'keep_narrowed_archive_provenance_only', 'monitor_reopen_conditions']`; opt-in action ids: `['authorized_b4_ra_hi_source_policy_execution']`.
- Source-policy execution handoff exact approval/driver: `I explicitly approve running the B4 source-policy execution commands listed in B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json./run_b4_source_policy_after_opt_in.sh/True/True/13/20/20`.
- Source-policy execution handoff authorized/commands-not-run: `False/True`.

| suite | rows | commands | 1e-4 opt-in | status | unresolved criteria |
|---|---:|---:|---:|---|---|
| `ra2021_absolute_coordinate` | `12` | `5` | `True` | `public_rows_complete_source_policy_rows_not_closed` | flagged_velocity_mapping_or_floor_issues_resolved, rerun_or_independent_verification_artifact_present, runtime_policy_tied_to_source_policy_order_rows, source_default_horizon_and_h_policy_reproduced |
| `hi2022_half_implicit` | `8` | `8` | `False` | `bounded_T0p1_rows_complete_full_T8_source_policy_rows_not_closed` | full_T8_public_policy_completed, rerun_or_independent_verification_artifact_present, runtime_iteration_metric_tied_to_source_policy_rows, selected_T8_candidate_promoted_to_source_policy, source_policy_reproduction_closed, velocity_mapping_and_error_norm_closed |

Post-execution promotion requirements:
- regenerate source-policy row audits from executed artifacts
- promote rows only after source-policy step/reference/output/runtime binding is verified
- rebuild B4 work/precision figures from promoted rows
- rerun blocker gate, review agent, reproducibility manifest, submission bundle, and full paper package validators

Closeout now: rows `0/20`, B4/B7 `False/False`.
