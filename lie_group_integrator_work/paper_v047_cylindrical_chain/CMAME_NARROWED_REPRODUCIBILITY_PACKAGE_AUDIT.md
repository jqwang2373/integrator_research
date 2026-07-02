# CMAME Narrowed Reproducibility Package Audit

Status: **narrowed_claim_reproducibility_package_ready_full_source_policy_open**.

- Narrowed-claim reproducibility package ready: `True`.
- Global submission ready: `False`.
- Submission standard scope: `global_submission_standard`.
- Full source-policy runner package ready: `False`.
- Source-policy rows closed: `0/40`.
- Source-policy execution allowed now/invoked/exact opt-in required: `False/False/True`.
- Safe action ids: `['rebuild_read_only_audit_chain', 'rerun_read_only_validators', 'keep_narrowed_archive_provenance_only', 'monitor_reopen_conditions']`; opt-in action ids: `['authorized_b4_ra_hi_source_policy_execution']`.
- Source-policy execution handoff exact approval/driver: `I explicitly approve running the B4 source-policy execution commands listed in B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json./run_b4_source_policy_after_opt_in.sh/True/True/13/20`.
- Source-policy execution handoff authorized/commands-not-run/terminal-unable: `False/True/20`.

## Included Current-Scope Evidence

- Minimal replay package/status/files/Python lines: `candidate_replay_package_built_not_submission_ready/10/180`.
- Local accepted-row companion/status/rows/Python lines: `local_accepted_runner_companion_ready_source_policy_package_open/12/150`.
- Self-contained examples: `['single_pendulum', 'double_pendulum', 'four_link', 'slider_crank']`.
- Replay-only examples: `[]`.
- P1 single/double runner ready: `True/True`.
- Closed-loop runner/models/rows: `['four_link', 'slider_crank']/6`.
- Narrowed bundle/status/report: `pass/results/narrowed_repro_bundle_report.md`.

## Boundary

This is a reviewer-facing package for the narrowed current claim. It is not a full source-policy runner archive, and it does not promote any source-policy rows.
