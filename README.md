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
| Read or edit the paper | `paper/main_cmame.tex` (the only hand-edited source) → `paper/main_cmame.pdf` |
| arXiv preprint / Elsevier flat source | `paper/arxiv/` (`README.md` has the metadata) / `paper/cmame_submission_flat/`, `paper/cmame_submission_flat.zip` |
| The proofs | `proof/` (`scripts/check.sh` = build + axiom audit + lint); what they cover: `validation/docs/LEAN_FORMALIZATION.md` |
| The integrator | `numerics/v047_cylindrical_chain_pipeline/run_v047.py`; results in `results/` |
| Benchmarks against public code | `numerics/v048_cross_paper_same_test_benchmarks/` |
| Current status (Chinese, dated) | `validation/paper_v047_cylindrical_chain/CURRENT_STATUS_CN.md` |
| Claim boundary and command rules | `validation/CURRENT_PIPELINE_CONTRACT.md` |
| What every ledger file is and who reads it | `validation/docs/PATH_DEPENDENCY_REPORT.md` |

## Checks

```bash
.venv_sbel/bin/python validation/validate_pipeline_outputs.py                       # whole tree (~4900 checks)
.venv_sbel/bin/python validation/paper_v047_cylindrical_chain/validate_paper_package.py   # paper chain
```

Both are read-only. Never run `numerics/v047_cylindrical_chain_pipeline/run_v047.py` or default
`h = 1e-4` reruns as a routine check, and never run the B4 source-policy driver without the exact
approval sentence recorded in the contract.

## Rules of the tree

- `paper/main_cmame.tex` is the only hand-edited manuscript. The flat copy, the arXiv version, the
  PDFs and the text dumps are regenerated from it (rebuild order in the contract).
- `validation/paper_v047_cylindrical_chain/` is an evidence ledger: nearly every JSON/Markdown record
  there is read by a validator. Consult `validation/docs/PATH_DEPENDENCY_REPORT.md` before moving
  anything; scripts locate the other folders through `paper_paths.py`.
- `numerics/vNNN_*` directories are a read-only record; new work gets a new version directory.
- `proof/` must stay byte-identical to `~/lean/integrator_order_proof` (the gate checks it); edit
  there, run `scripts/check.sh`, then `rsync` here.
