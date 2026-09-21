# CMAME Local Accepted-Row Runner Companion

Status: local accepted-row companion ready, source-policy package open.

This companion is a small reviewer-facing index and launcher for the existing
local self-contained runner candidates. It intentionally does not copy those
runner sources into the minimal replay package, and it does not claim full
source-policy or submission readiness.

Run:

```bash
python scripts/run_local_accepted_runner_companion.py
```

Expected terminal markers:

- `cmame_local_accepted_runner_companion=PASS`.
- `minimal_replay_boundary=preserved`.
- `self_contained_examples=single_pendulum,double_pendulum,four_link,slider_crank`.
- `local_rows=12`.
- `source_policy_external_rows=0/40`.
- `source_policy_handoff_status=source_policy_execution_handoff_ready_not_authorized_not_run`.
- `source_policy_handoff_authorized=False`.
- `source_policy_handoff_driver=run_b4_source_policy_after_opt_in.sh`.
- `source_policy_handoff_opt_in=13/20`.
- `full_source_policy_runner_package_ready=False`.
- `submission_ready=False`.

B4 handoff boundary:

- exact approval statement: `I explicitly approve running the B4 source-policy execution commands listed in B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json.`;
- guarded driver: `run_b4_source_policy_after_opt_in.sh`, requires exact approval, and does not authorize execution by itself.
