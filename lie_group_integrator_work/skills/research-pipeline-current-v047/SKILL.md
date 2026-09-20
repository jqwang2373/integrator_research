---
name: research-pipeline-current-v047
description: Use when continuing the current jingquan-autoresearch v047 Lie-group/multibody integrator research, especially validating artifacts, preserving the four-ASME/convergence/proof pipeline, or advancing the full-TFE stage-replacement gate without creating a new version.
---

# Current v047 Research Pipeline

## Core Discipline

Continue inside `lie_group_integrator_work/v047_cylindrical_chain_pipeline`
unless the user explicitly asks for a new version. Use current generated
artifacts as authority, not memory or stale summaries.

Every research round must preserve:

- math proof/status in `docs/ORDER_PROOF_LEDGER.md`;
- four ASME examples: `single_pendulum`, `double_pendulum`, `four_link`, `slider_crank`;
- convergence analysis with at least three step sizes;
- convergence and diagnostic plots;
- CSV/JSON/report artifacts plus top-level ledger synchronization.

Do not claim paper exceedance unless the comparator is explicit and the current
pipeline gate proves the claim.

## Current Accepted Evidence

As of the current validated v047 state:

- v047 validator passes over 158 result files, 80 CSVs, and 76 PNGs.
- Top-level pipeline validator passes over 397 result files, 148 CSVs, 154 PNGs, and 48 JSON files.
- Four ASME method rows are accepted:
  `single_pendulum`, `double_pendulum`, `four_link`, and `slider_crank`.
- Smooth cylindrical convergence is high order after compatible initial
  velocity repair.
- Sharp-friction coarse-regime order is reduced, but ultra fixed refinement
  recovers high order at finer tested scale.
- Sparse row-VJP is correctness-valid but not a dense-`jacfwd` speed win.

## Full-TFE Gate

`full_tfe_stage_replacement` means the independent paper-style TFE stage
residual has replaced the current stage solve and passed the accepted h-sweep
and pipeline gate. It is not satisfied by:

- endpoint-node weighted rows evaluated on another trajectory;
- diagonal-equivalent stage weighting;
- endpoint-boundary probe terms;
- one-step formula or Schur diagnostics;
- diagnostic-z0 all-row substitution;
- terminal-output diagnostics with `accepted_h_sweep_present=false`.

Current status remains:

```text
accepted_h_sweep_present=false
full_tfe_stage_replacement=false
```

The latest useful diagnostic is the paper lower-pair acceleration
terminal-output h-sweep: max terminal residual `8.35e-12`, rank `132`,
raw/scaled condition `4.37e8/5.83e3`, smooth orders `4.937/4.799`, and sharp
orders `2.555/1.918`. Treat it as localized evidence only.

The paired projection-dependence audit compares raw terminal paper output with
endpoint-velocity-projected output on the same 6 rows. It records
raw/projected endpoint velocity residuals `7.99e-06/9.66e-15`, max projection
delta `7.92e-06`, and `6/6` rows requiring projection. This makes the
remaining projection-free full-TFE blocker explicit.

The paper lower-pair acceleration terminal-velocity closure diagnostic closes
raw terminal endpoint velocity to `5.80e-16` without output projection, with
max closure residual `9.73e-12`, rank `132`, raw/scaled condition
`1.28e10/7.99e4`, smooth/sharp orders `3.459/4.838` and `2.555/1.918`, and
max replaced terminal lower-pair acceleration row `2.53e-4`. Treat it as a
projection-free terminal-velocity diagnostic only: it replaces terminal rows
rather than deriving an independent full-TFE stage functional.

The terminal-row homotopy audit solves 30 one-step rows over
beta=[0,0.25,0.5,0.75,1], with max residual `6.22e-12`, rank `132`,
raw/scaled condition `1.28e10/7.86e4`, and beta0/beta1 terminal velocity
residuals `2.34e-10/1.29e-12`. It is still a row-replacement diagnostic, not
full TFE stage replacement.

## Required Commands

From `lie_group_integrator_work/v047_cylindrical_chain_pipeline`:

```bash
../.venv_sbel/bin/python -m py_compile run_v047.py validate_v047_outputs.py
../.venv_sbel/bin/python run_v047.py
../.venv_sbel/bin/python validate_v047_outputs.py
```

From `lie_group_integrator_work`:

```bash
.venv_sbel/bin/python validate_pipeline_outputs.py
```

Run the full v047 script only after code or generated-artifact logic changes.
For documentation-only changes, run the relevant validator first and then the
top-level validator if the docs are part of the checked pipeline.

## Next Aligned Work

Prefer work that closes the full-TFE gate:

- derive stage-local weak rows instead of endpoint-boundary source probes;
- solve the independent residual over smooth and sharp h-sweeps;
- attach the accepted result to the four-ASME gate;
- keep all diagnostic failures explicit rather than weakening validators.

If a change only improves documentation or workflow, keep it separate from
algorithm claims and do not update `full_tfe_stage_replacement`.
