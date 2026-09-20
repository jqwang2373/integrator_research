"""Location of the manuscript assets.

Since 2026-09-20 the LaTeX sources, figures, submission copies and journal sidecars live in
`lie_group_integrator_work/paper/` (sibling of this package); the evidence ledger, builders and
validators stay here.  Scripts import `LATEX` for direct joins and `package_path(label)` when a
relative label may name either a manuscript asset or a package record.
"""

from __future__ import annotations

from pathlib import Path

PAPER = Path(__file__).resolve().parent
LATEX = PAPER.parent / "paper"

MANUSCRIPT_TOPLEVEL = {
    "main_cmame.tex", "main_cmame.pdf", "main_cmame.log", "main_cmame.txt",
    "main.tex", "main.pdf", "main.log", "main.txt",
    "main_concise.tex", "main_concise.pdf", "main_concise.log", "main_concise.txt",
    "highlights_cmame.txt", "declarations_cmame.md", "COVER_LETTER.md", "README_CMAME_FLAT_SUBMISSION.md",
    "cmame_submission_flat.zip",
}
MANUSCRIPT_DIRS = {"figures", "cmame_submission_flat", "arxiv"}


def is_manuscript_label(label: str) -> bool:
    first = str(label).replace("\\", "/").lstrip("./").split("/")[0]
    return first in MANUSCRIPT_TOPLEVEL or first in MANUSCRIPT_DIRS


def package_path(label: str) -> Path:
    """Resolve a package-relative label to the manuscript folder or the package folder."""
    label = str(label)
    if label.startswith("../"):
        return (PAPER / label).resolve()
    return (LATEX / label) if is_manuscript_label(label) else (PAPER / label)
