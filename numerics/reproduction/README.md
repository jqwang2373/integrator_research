# Human-Runnable Reproduction Entry Point

This folder provides a compact entry point for reproducing the current
multi-method, multi-example result summaries from the existing v047/v048
artifacts.

The default command is intentionally artifact-level reproduction: it rebuilds
readable tables from checked CSV/JSON outputs without running the long
historical generators or strict public-policy `1e-4` campaigns.

## Quick Run

From the repository root:

```bash
.venv_sbel/bin/python numerics/reproduction/run_reproduction.py
```

This writes:

- `reproduction/outputs/method_example_matrix.csv`
- `reproduction/outputs/method_example_matrix.md`
- `reproduction/outputs/work_precision_summary.csv`
- `reproduction/outputs/work_precision_summary.md`
- `reproduction/outputs/reproduction_report.md`
- `reproduction/outputs/reproduction_manifest.json`

## Optional Validation

Run the same summary rebuild plus lightweight validators:

```bash
.venv_sbel/bin/python numerics/reproduction/run_reproduction.py --check
```

The validators are read-only and do not invoke `v047_cylindrical_chain_pipeline/run_v047.py`.

## What This Reproduces

The script consolidates:

- the 44-row paper numerical result matrix across four examples and multiple
  method families;
- coarse single/double-pendulum work-precision summaries;
- strict common-reference closed-loop work-precision summaries for four-link
  and slider-crank;
- current claim boundaries: no external superiority claim, no accepted full
  TFE stage replacement, and no submission-ready claim.

## Scope Boundary

This is the recommended human-facing entry point for checking and packaging the
current results. It is not a full numerical regeneration command. Use the
version-specific runners only when changing method code or intentionally
refreshing generated artifacts.

Heavy commands not run by default:

- `v047_cylindrical_chain_pipeline/run_v047.py`
- strict public-policy `1e-4` same-test campaigns
- full external same-test campaign

