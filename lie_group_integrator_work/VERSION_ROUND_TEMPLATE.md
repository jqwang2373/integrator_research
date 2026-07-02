# Per-Version Round Template

Each new `vNNN_*` version is complete only after these artifacts exist.

## Required Artifacts

- `README.md`: purpose, run command, outputs, and interpretation.
- `run_vNNN.py`: reproducible script for the full experiment.
- `results/vNNN_report.md`: human-readable report.
- `results/summary_vNNN.json`: machine-readable summary.
- `results/*.csv`: raw convergence, validation, and diagnostic rows.
- `results/*.png`: convergence and diagnostic plots.
- top-level `pipeline_validation_results/`: refreshed by
  `validate_pipeline_outputs.py` before claiming the generated outputs are
  clean.

## Required Evidence

### Math Proof/Status

- Add an entry to `ORDER_PROOF_LEDGER.md`.
- State the expected order.
- Mark the status as `proved`, `conditional`, or `empirical/diagnostic`.
- List the assumptions needed for the claim.
- Explain any order reduction or non-asymptotic behavior.

### Four ASME Examples

Run or map the method onto all four examples:

- single pendulum;
- double pendulum;
- four link;
- slider crank.

The report must include pass/fail status, trajectory errors, constraint norms,
SO(3)/quaternion diagnostics, Newton iteration diagnostics, and runtime.

### Convergence Analysis

- Use at least three step sizes.
- Use a nested fine reference or a documented accepted baseline.
- Report observed orders for the main state errors and any constraint errors.
- Include smooth and sharp/friction-transition cases when relevant.

### Plots

At minimum, include:

- convergence/order plot;
- runtime or solver-cost plot;
- constraint/invariant diagnostic plot.

## Required Ledger Updates

- `README.md`
- `VERSION_LEDGER.md`
- `VERSION_TREE.md`
- `ORDER_PROOF_LEDGER.md`
- `version_ledger.csv`
- regenerate `version_progression.png` when the version ledger changes
- run `.venv_sbel/bin/python validate_pipeline_outputs.py` and inspect
  `pipeline_validation_results/pipeline_validation_report.md`

## Backfilling Historical Versions

A historical version may stay as local evidence without satisfying the current
gate. If it is promoted as a current method claim, add a fresh result set that
uses this template, marks any missing ASME mappings as incomplete, and keeps
the version open until proof/status, four-example validation, convergence
analysis, and plots are all present.
