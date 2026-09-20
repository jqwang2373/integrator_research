# Paper (LaTeX)

Everything needed to read, edit and compile the manuscript lives here; the evidence ledger,
builders and validators stay in `../paper_v047_cylindrical_chain/`.

| File / folder | What it is |
| --- | --- |
| `main_cmame.tex` | **The manuscript** (CMAME, `elsarticle`). The only hand-edited source. |
| `main_cmame.pdf`, `main_cmame.log`, `main_cmame.txt` | Compiled PDF, LaTeX log, `pdftotext -layout` dump (validators read the log and the dump). |
| `figures/` | Figure sources referenced as `\figpath/<name>.png`. |
| `cmame_submission_flat/` | Elsevier flat copy: same text, figures renamed `Figure_n_*.png` at the same level; `cmame_submission_flat.zip` is the upload archive. Derived. |
| `arxiv/` | arXiv preprint (`article` class), metadata `README.md`, `arxiv_submission.zip`. Derived by `../paper_v047_cylindrical_chain/build_arxiv_version.py`. |
| `highlights_cmame.txt`, `declarations_cmame.md`, `COVER_LETTER.md`, `README_CMAME_FLAT_SUBMISSION.md` | Journal sidecars. |
| `main.tex`, `main_concise.tex` (+ pdf/log/txt) | Legacy internal drafts, superseded; each carries a status note. |
| `notes/` | Pre-compaction backups and the proposed method-section revision. |

## Build

```bash
cd lie_group_integrator_work/paper
cmd.exe /c "latexmk -pdf -interaction=nonstopmode -halt-on-error main_cmame.tex"   # Windows TeX from WSL
cmd.exe /c "pdftotext -layout main_cmame.pdf main_cmame.txt"
```

After editing `main_cmame.tex`: regenerate the flat copy (substitute `\figpath{.}` and the
`Figure_n_*.png` names), run `python3 ../paper_v047_cylindrical_chain/build_arxiv_version.py`,
compile the flat copy and `arxiv/main_arxiv.tex` the same way, then run the builder sequence and
both validator chains described in `../CURRENT_PIPELINE_CONTRACT.md`.
