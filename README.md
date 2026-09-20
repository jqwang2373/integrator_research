# integrator_research

Research tree for the **Gauss6/FullVA Lie-group integrator** for lower-pair mechanisms and its
CMAME manuscript. Start here:

| What you want | Open |
| --- | --- |
| The paper (journal version, authoritative source) | `lie_group_integrator_work/paper/main_cmame.tex` → `main_cmame.pdf` (LaTeX only lives in `paper/`) |
| The arXiv preprint (derived, `article` class) | `lie_group_integrator_work/paper/arxiv/` (`README.md` there has the metadata) |
| Elsevier flat source + zip | `lie_group_integrator_work/paper/cmame_submission_flat/`, `paper/cmame_submission_flat.zip` |
| The Lean 4 / Mathlib proofs | `lie_group_integrator_work/paper_v047_cylindrical_chain/lean/` (copy of `~/lean/integrator_order_proof`); pointer: `lie_group_integrator_work/docs/LEAN_FORMALIZATION.md` |
| Current status in Chinese | `lie_group_integrator_work/paper_v047_cylindrical_chain/CURRENT_STATUS_CN.md` |
| Claim boundary and command rules | `lie_group_integrator_work/CURRENT_PIPELINE_CONTRACT.md` |
| Method code (the integrator) | `lie_group_integrator_work/v047_cylindrical_chain_pipeline/run_v047.py` |
| Cross-paper benchmark harness | `lie_group_integrator_work/v048_cross_paper_same_test_benchmarks/` |
| Version history (v001–v048), ledgers, audits | `lie_group_integrator_work/docs/` |
| What every paper-package file is and who reads it | `lie_group_integrator_work/docs/PATH_DEPENDENCY_REPORT.md` |

## Layout

```
integrator_research/
  README.md                          this map
  lie_group_integrator_work/         all research code, records and the paper package
    README.md                        map of the work tree + version policy
    CURRENT_PIPELINE_CONTRACT.md     claim boundary, command boundary, change log
    validate_pipeline_outputs.py     top-level validator (runs under .venv_sbel automatically)
    docs/                            ledgers, audits, plans, Lean pointer, path dependency report
    tools/                           plot_version_ledger.py, build_path_dependency_report.py
    paper/                           the manuscript: main_cmame.tex, figures/, cmame_submission_flat/, arxiv/, sidecars
    paper_v047_cylindrical_chain/    evidence ledger: records, builders, validators, Lean copy (see its README)
    v047_cylindrical_chain_pipeline/ accepted method implementation and its validators
    v048_cross_paper_same_test_benchmarks/  external same-test benchmark layer
    v001_… v046_…                    development history, one directory per version (read-only record)
    pipeline_validation_results/     output of the top-level validator
    reproduction/                    human-runnable table rebuild from checked artifacts
    .venv_sbel/                      Python 3.11 virtualenv (uv; untracked)
  external/
    sbel-reproducibility/            SBEL/Negrut public reproducibility code (local mirror)
    public-metadata/                 no-checkout clone of uwsbel/public-metadata (untracked)
  slides/                            talk material
  s11044-026-10153-w.pdf/.txt        source paper for the TFE comparison (read by validators; do not move)
  1-s2.0-S0377042719305229-main.pdf  additional reference
```

## Rules of the tree

- `paper/main_cmame.tex` is the only hand-edited manuscript. The flat copy, the arXiv version, the PDFs and
  the text dumps are regenerated from it (see `CURRENT_PIPELINE_CONTRACT.md`, "rebuild order").
- Files under `paper_v047_cylindrical_chain/` are an evidence ledger: almost every JSON/Markdown record
  is read by a validator. Do not move or rename them without `docs/PATH_DEPENDENCY_REPORT.md`.
- Never run `v047_cylindrical_chain_pipeline/run_v047.py` (the historical campaign) or default
  `1e-4` reruns as a routine check; use the read-only validators.
- Source-policy (B4) execution requires the explicit opt-in sentence recorded in the contract.
- Run `python3 lie_group_integrator_work/validate_pipeline_outputs.py` and
  `.venv_sbel/bin/python paper_v047_cylindrical_chain/validate_paper_package.py` after any change.
