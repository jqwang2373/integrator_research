# CMAME Narrowed Reproducibility Bundle

This directory is the reviewer-facing runnable entrypoint for the current
narrowed manuscript claim. It bundles the paper-matrix replay with the existing
local accepted-row runners.

Run from the paper directory:

```bash
../../../.venv_sbel/bin/python cmame_narrowed_repro_bundle/scripts/run_narrowed_repro_bundle.py
```

Expected boundary:

- source-policy external rows closed: `0/40`;
- B4 handoff status: `source_policy_execution_handoff_ready_not_authorized_not_run`;
- exact B4 approval statement: `I explicitly approve running the B4 source-policy execution commands listed in B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json.`;
- guarded B4 driver: `run_b4_source_policy_after_opt_in.sh`, requires exact approval, and does not authorize execution by itself;
- full source-policy runner package ready: `False`;
- external-superiority claim allowed: `False`;
- global submission ready: `False`.

The launcher does not run `run_v047.py`, v048 heavy campaigns, or B4
source-policy execution commands.
