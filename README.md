# integrator_research

A sixth-order Lie-group integrator (**Gauss6/FullVA**) for lower-pair mechanisms: the paper, its
machine-checked proofs, the numerical evidence, and the audit ledger that ties them together.

```
integrator_research/
  paper/        the manuscript (LaTeX only)                 → paper/README.md
  proof/        Lean 4 / Mathlib development                → proof/README.md
  numerics/     method code, results, benchmarks, history   → numerics/README.md
  external/     public code mirrors and reference papers    → external/README.md
  validation/   evidence ledger, validators, ledgers, docs  → validation/README.md
  .venv_sbel/   Python 3.11 virtualenv (uv; not tracked)
```

| What you want | Open |
| --- | --- |
| Read or edit the paper | `paper/rewrite/parts/*.tex` → `paper/rewrite/assemble.py --target main_cmame` → `paper/main_cmame.tex`, `paper/main_cmame.pdf` (rewritten 2026-09-21; see `paper/README.md`) |
| arXiv preprint / Elsevier flat source | `paper/arxiv/` (`README.md` has the metadata) / `paper/cmame_submission_flat/`, `paper/cmame_submission_flat.zip`; both written by `paper/rewrite/build_derived.py` |
| Experiments behind the paper's tables and figures | `numerics/v049_paper_experiments/` (`e1_…`–`e7_…`, `make_figures.py`, `results/`) |
| The proofs | `proof/` (`scripts/check.sh` = build + axiom audit + lint); what they cover: `validation/docs/LEAN_FORMALIZATION.md` |
| The integrator | `numerics/v047_cylindrical_chain_pipeline/run_v047.py`; results in `results/` |
| Benchmarks against public code | `numerics/v048_cross_paper_same_test_benchmarks/` |
| Current status (Chinese, dated) | `validation/paper_v047_cylindrical_chain/CURRENT_STATUS_CN.md` |
| Claim boundary and command rules | `validation/CURRENT_PIPELINE_CONTRACT.md` |
| What every ledger file is and who reads it | `validation/docs/PATH_DEPENDENCY_REPORT.md` |

## Checks

```bash
.venv_sbel/bin/python validation/validate_pipeline_outputs.py                       # whole tree (~4900 checks)
.venv_sbel/bin/python validation/validate_manuscript.py                                     # the paper: log, table numbers, Lean names, arXiv sync
.venv_sbel/bin/python validation/paper_v047_cylindrical_chain/validate_paper_package.py   # frozen ledger (pre-rewrite package)
```

Both are read-only. Never run `numerics/v047_cylindrical_chain_pipeline/run_v047.py` or default
`h = 1e-4` reruns as a routine check, and never run the B4 source-policy driver without the exact
approval sentence recorded in the contract.

## Rules of the tree

- `paper/main_cmame.tex` is generated from `paper/rewrite/parts/`; edit the parts. The flat copy and the arXiv
  version are derived by `paper/rewrite/build_derived.py`; never edit them by hand.
- `validation/paper_v047_cylindrical_chain/` is the frozen evidence ledger of the pre-rewrite manuscript (snapshot in
  `validation/legacy_drafts/main_cmame_pre_rewrite/`): nearly every JSON/Markdown record
  there is read by a validator. Consult `validation/docs/PATH_DEPENDENCY_REPORT.md` before moving
  anything; scripts locate the other folders through `paper_paths.py`.
- `numerics/vNNN_*` directories are a read-only record; new work gets a new version directory.
- `proof/` must stay byte-identical to `~/lean/integrator_order_proof` (the gate checks it); edit
  there, run `scripts/check.sh`, then `rsync` here.
