# paper

The manuscript and nothing else. The evidence ledger, builders and validators are in
`../validation/paper_v047_cylindrical_chain/`; the proofs in `../proof/`; the results in `../numerics/`.

| File / folder | What it is |
| --- | --- |
| `main_cmame.tex` | **The manuscript** (CMAME, `elsarticle`). The only hand-edited source. |
| `main_cmame.pdf`, `main_cmame.log`, `main_cmame.txt` | Compiled PDF, LaTeX log, `pdftotext -layout` dump (validators read the log and the dump). |
| `figures/` | Figure sources referenced as `\figpath/<name>.png`. |
| `cmame_submission_flat/`, `cmame_submission_flat.zip` | Elsevier flat copy: same text, figures renamed `Figure_n_*.png` at the same level; the zip is the upload archive. Derived. |
| `arxiv/` | arXiv preprint (`article` class), metadata `README.md`, `arxiv_submission.zip`. Derived by `../validation/paper_v047_cylindrical_chain/build_arxiv_version.py`. |
| `highlights_cmame.txt`, `declarations_cmame.md`, `COVER_LETTER.md`, `README_CMAME_FLAT_SUBMISSION.md` | Journal sidecars. |
| `slides/` | Talks and the autoresearch-methodology write-up (separate documents). |

Superseded drafts (`main.tex`, `main_concise.tex`) and pre-compaction backups are not here; they
live in `../validation/legacy_drafts/` because the ledger still validates them.

## Build

```bash
cd paper
cmd.exe /c "latexmk -pdf -interaction=nonstopmode -halt-on-error main_cmame.tex"   # Windows TeX from WSL
cmd.exe /c "pdftotext -layout main_cmame.pdf main_cmame.txt"
```

After editing `main_cmame.tex`: regenerate the flat copy (substitute `\figpath{.}` and the
`Figure_n_*.png` names), run `python3 ../validation/paper_v047_cylindrical_chain/build_arxiv_version.py`,
compile the flat copy and `arxiv/main_arxiv.tex` the same way, then run the builder sequence and
both validator chains described in `../validation/CURRENT_PIPELINE_CONTRACT.md`.
