# Folder Map

This file is a navigation layer for the research tree. It does not change the
pipeline contract; authoritative claim boundaries remain in
`../CURRENT_PIPELINE_CONTRACT.md`, `PIPELINE_AUDIT.md`, and the paper gates under
`../paper_v047_cylindrical_chain/`.

## Layout since 2026-09-20

```
integrator_research/
  paper/         the manuscript (rewritten 2026-09-21): rewrite/parts/ -> main_cmame.tex (+pdf/log), figures/,
                 cmame_submission_flat/ (+zip), arxiv/, highlights/declarations/cover letter, slides/,
                 agentic_research/ (the process paper, ACL/NAACL template; own README.md and make_figures.py)
  proof/         Lean 4 development copy (IntegratorOrderProof/, scripts/, README.md)
  numerics/      v001_… v048_… (v047 = accepted method, v048 = benchmarks), reproduction/, scratch
  external/      sbel-reproducibility/, public-metadata/ (untracked clone), literature/ (reference PDFs)
  validation/    README.md, CURRENT_PIPELINE_CONTRACT.md, validate_pipeline_outputs.py
    docs/        this file, the ledgers and audits below, LEAN_FORMALIZATION.md, PATH_DEPENDENCY_REPORT.md
    tools/       plot_version_ledger.py, build_path_dependency_report.py
    paper_v047_cylindrical_chain/   the evidence ledger (records, build_*/validate_*/run_*.py, paper_paths.py,
                                    cmame_*/ bundles, notes/)
    legacy_drafts/   superseded main.tex / main_concise.tex (+pdf) and manuscript backups
    pipeline_validation_results/, skills/
  .venv_sbel/    Python virtualenv (untracked)
```

## Current Status Files (all in `docs/` except the contract)

| File | Use |
| --- | --- |
| `../CURRENT_PIPELINE_CONTRACT.md` | Short current-state contract and command boundary. |
| `VALIDATION_QUICKSTART.md` | Which validator to run for each routine check. |
| `PIPELINE_AUDIT.md` | Pipeline-level gate status across v047/v048. |
| `ORDER_PROOF_LEDGER.md` | Mathematical proof/order status by version. |
| `VERSION_LEDGER.md` | Human-readable version history. |
| `VERSION_TREE.md` | Version lineage. |
| `version_ledger.csv` | Machine-readable version ledger. |
| `version_progression.png` | Plot generated from `version_ledger.csv` by `../tools/plot_version_ledger.py`. |
| `LEAN_FORMALIZATION.md` | What the Lean development proves and where it lives. |
| `PATH_DEPENDENCY_REPORT.md` | Family and readers of every paper-package file; consult before moving anything. |

## Main Working Areas

| Path | Role | Notes |
| --- | --- | --- |
| `paper_v047_cylindrical_chain/` | Current CMAME paper package, claim gates, audits, manuscript sources, and submission bundle. | Mechanically buildable, not submission ready. |
| `v047_cylindrical_chain_pipeline/` | Current method artifact generator and v047 validators. | Do not run `run_v047.py` for routine checks; it is the full historical generator. |
| `v048_cross_paper_same_test_benchmarks/` | External same-test benchmark layer and coarse-first evidence. | No external superiority claim yet. |
| `pipeline_validation_results/` | Output from `validate_pipeline_outputs.py`. | Generated validation evidence. |
| `reproduction/` | Human-runnable entry point for rebuilding multi-method/multi-example summary tables from checked artifacts. | Safe wrapper; does not run heavy generators by default. |
| `scratch_v046_cylindrical_chain_pending/` | Historical scratch/pending context. | Keep separate from accepted gates. |
| `skills/` | Local workflow skill material. | Process support, not primary evidence. |

## Version Directory Groups

| Range | Theme |
| --- | --- |
| `v001`-`v003` | SO(3) setup and SBEL/Negrut baseline reproduction. |
| `v004`-`v006` | Conservative Lie mechanics and reduced fixed-pivot constraints. |
| `v007`-`v015` | Absolute-coordinate DAE, friction, quaternion endpoint, and Gauss6/adaptive methods. |
| `v016`-`v018` | Reference-family baselines: trapezoidal, BDF2, Lobatto. |
| `v019`-`v022` | Multiplier-dependent and Brown-McPhee-style friction path. |
| `v023`-`v029` | Full absolute-coordinate lower-pair and FullVA residual path. |
| `v030`-`v038` | Sparse/JAX/colored Jacobian and pattern-cache experiments. |
| `v039`-`v045` | Larger topology, skew-axis, prismatic, and row-colored VJP coverage. |
| `v046` | Four-ASME public baseline anchor. |
| `v047` | Current cylindrical-chain method and paper-facing claim artifacts. |
| `v048` | Current external same-test benchmark harness. |

## Claim Boundary Snapshot

- Accepted method: `Gauss6/FullVA`.
- Accepted method order claim: `6`.
- Four ASME examples are accepted under the current method gate.
- `full_tfe_stage_replacement=false`.
- `same_test_campaign_status=not_run`.
- `external_superiority_claim=false`.
- `submission_ready=false`.

## Routine Checks

From `validation/`:

```bash
../.venv_sbel/bin/python validate_pipeline_outputs.py
```

From `validation/paper_v047_cylindrical_chain/`:

```bash
../../.venv_sbel/bin/python validate_paper_package.py
../../.venv_sbel/bin/python validate_paper_claims.py
../../.venv_sbel/bin/python validate_cmame_submission.py
```

From `numerics/v047_cylindrical_chain_pipeline/`:

```bash
../../.venv_sbel/bin/python validate_four_asme_minimal.py
../../.venv_sbel/bin/python validate_full_tfe_gap.py
../../.venv_sbel/bin/python validate_full_tfe_repair_spec.py
../../.venv_sbel/bin/python validate_v047_outputs.py
```
