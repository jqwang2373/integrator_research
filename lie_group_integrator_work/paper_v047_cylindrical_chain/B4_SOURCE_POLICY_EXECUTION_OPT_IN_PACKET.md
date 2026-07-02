# B4 Source-Policy Execution Opt-In Packet

Status: `ready_for_user_opt_in_packet_not_authorized_not_run`.

This packet is read-only. It does not authorize or run numerical execution.

- Explicit user opt-in required: `True`.
- Ready command batches/count: `2/13`.
- Ready command mapped external rows: `20/40`.
- Unaddressed external rows after ready commands: `0`.
- Attempted-not-reproducible external rows: `20`.
- External rows still requiring execution/promotion: `20`.
- Source-policy rows closed now: `0/40`.
- Source-policy execution allowed now/invoked/exact opt-in required: `False/False/True`.
- Safe action ids: `rebuild_read_only_audit_chain,rerun_read_only_validators,keep_narrowed_archive_provenance_only,monitor_reopen_conditions`.
- Opt-in action ids: `authorized_b4_ra_hi_source_policy_execution`.
- B4/B7 can close now: `False/False`.
- B4/B7 can close after ready commands only: `False/False`.
- Heavy/run_v047/v048 invoked: `False/False/False`.
- Command preflight parse/runner/python/shell-safe: `True/True/True/True`.
- Remaining gap program rows/entries: `0/0`.
- TFE rows attempted-not-reproducible: `16`.
- VP2024 rows attempted-not-reproducible: `4`.
- Rows demoted related-work/proxy for current claim: `0`.
- Post-execution promotion contract: `b4-source-policy-post-execution-promotion-contract-v1` / `promotion_contract_defined_no_rows_promoted`.
- Promotion checklist satisfied now: `False`.

## Objective Blocker Matrix

This packet is an OC4 execution handoff artifact. It does not close the global objective blockers.

- `blocker_open_by_id=OC4:True,OC6:True,OC12:True`
- `blocker_closure_decision_by_id=OC4:remain_open_ready_for_authorized_execution_not_executed_not_promoted,OC6:remain_open_no_positive_source_equivalent_artifact,OC12:remain_partial_narrowed_replay_ready_full_source_policy_archive_not_ready`
- `blocker_closure_allowed_by_id=OC4:False,OC6:False,OC12:False`

Required approval statement:

`I explicitly approve running the B4 source-policy execution commands listed in B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json.`

Guarded execution driver:

- `run_b4_source_policy_after_opt_in.sh` is a prepared local driver for the packet commands.
- It refuses to execute unless the exact approval statement above is passed as its first argument.
- It is not an authorization artifact and does not change the current read-only packet status.

## Ready Batches

| batch | commands | mapped rows | 1e-4 opt-in |
|---|---:|---:|---:|
| `ra2021_ready_after_explicit_1e_4_opt_in` | `5` | `12` | `True` |
| `hi2022_ready_no_1e_4_selected_candidate` | `8` | `8` | `False` |

## Guarded Execution Protocol

- Status: `dry_run_preflight_complete_execution_requires_exact_user_approval`.
- Execution working directory: `../v048_cross_paper_same_test_benchmarks`.
- Command preflights: `13`.
- All commands parse: `True`.
- All runner scripts exist: `True`.
- All Python executables exist: `True`.
- All commands shell-safe single command: `True`.
- Execute commands now: `False`.
- Dry-run only until approved: `True`.


## Unaddressed Rows

- TFE rows without launch commands: `0`.
- VP2024 rows without launch commands: `0`.
- TFE current-claim disposition: `attempted_not_reproducible; related-work/formal-order comparator only; source-policy rows remain 0/16`.
- VP2024 current-claim disposition: `attempted_not_reproducible; related-work/proxy only; source-policy rows remain 0/4`.
- HI2022 single-pendulum rows outside selected-candidate preflight: `0`.
- Terminal attempted-not-reproducible rows: `20`.
- Terminal attempted-not-reproducible evidence: `SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_AUDIT.json`.

## Remaining Gap Program

Status: `remaining_0_rows_programmed_no_execution_invoked`.

| gap | rows | first required artifact | ready now |
|---|---:|---|---:|

Post-execution promotion is still required before any B4/B7 closure claim.

## Post-Execution Promotion Contract

- Contract: `b4-source-policy-post-execution-promotion-contract-v1`.
- Status: `promotion_contract_defined_no_rows_promoted`.
- Source publication contract: `b4-source-policy-work-precision-publication-contract-v1`.
- Rows closed now: `0/40`.
- Attempted-not-reproducible rows: `20`.
- Rows still requiring execution/promotion: `20`.
- Ready mapped/unaddressed rows: `20/0`.
- Existing-artifact promotion-ready count: `0`.
- Ready/not-ready lanes: `2/2`.
- Remaining gap rows requiring runner/code path: `0`.
- Remaining gap rows demoted related-work/proxy for current claim: `0`.
- After ready commands only can close B4/B7: `False/False`.
- All required promotion checks satisfied now: `False`.

| check | satisfied now | acceptance condition |
|---|---:|---|
| `source_policy_row_provenance` | `False` | each promoted row has a source-policy suite, method, example, horizon, step grid, reference policy, output variable set, and norm bound to the executed artifact |
| `same_run_error_and_work_metrics` | `False` | error/order rows and runtime/Newton/Jacobian/linear-solve work metrics come from the same accepted run records |
| `diagnostic_rows_not_promoted` | `True` | common-reference, proxy, candidate, bounded-window, and same-window diagnostics remain labeled diagnostic unless their source-policy binding is separately verified |
| `ready_command_rows_are_insufficient_by_themselves` | `True` | ready RA2021/HI2022 command output may be promoted only after row audits close; ready-command coverage alone cannot close B4/B7 |
| `remaining_gap_rows_stay_open_or_demoted` | `True` | TFE runner-equivalence rows and VP2024 distinct-code-path rows are either closed by new source-policy evidence or remain explicitly demoted from B4/B7 figures |
| `nonpublic_code_self_reproduction_disposition_recorded` | `True` | rows without usable public code are explicitly attempted from the paper/source specification and marked not reproducible rather than left as unresolved execution work |
| `publication_figures_rebuilt_from_promoted_rows` | `False` | B4 work/precision figures and B7 baseline/work-precision figures are regenerated from promoted source-policy rows, with limitation labels for demoted suites |
| `closure_validators_rerun_after_promotion` | `False` | after any promotion, rerun B4 row/readiness/promotion audits, blocker gate, review agent, reproducibility manifest, submission bundle, and full paper package validators |
