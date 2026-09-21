"""Repository layout as seen from the evidence ledger (this directory).

Since 2026-09-20 the repository has five top-level folders:

    paper/        the manuscript (LaTeX only)          proof/      Lean 4 / Mathlib development
    numerics/     method code, results, benchmarks      external/   mirrors and literature
    validation/   this ledger, validators, docs, tools  (.venv_sbel at the repository root)

Scripts here import the constants below instead of hard-coding parents, and route relative labels
stored in records through `package_path(label)`.
"""

from __future__ import annotations

import re
from pathlib import Path

PAPER = Path(__file__).resolve().parent                 # validation/paper_v047_cylindrical_chain
VALIDATION = PAPER.parent                                # validation/
REPO = VALIDATION.parent                                 # repository root
LATEX = REPO / "paper"                                   # manuscript, figures, submission copies, sidecars
PROOF = REPO / "proof"                                   # Lean development (byte-identical to ~/lean/integrator_order_proof)
NUMERICS = REPO / "numerics"                             # v001..v048, reproduction, scratch
V047 = NUMERICS / "v047_cylindrical_chain_pipeline"
V048 = NUMERICS / "v048_cross_paper_same_test_benchmarks"
EXTERNAL = REPO / "external"
LITERATURE = EXTERNAL / "literature"                     # reference PDFs and their text dumps
LEGACY = VALIDATION / "legacy_drafts"                    # superseded internal drafts (main.tex, main_concise.tex) kept for the ledger
VENV_PYTHON = REPO / ".venv_sbel" / "bin" / "python"

MANUSCRIPT_TOPLEVEL = {
    "main_cmame.tex", "main_cmame.pdf", "main_cmame.log", "main_cmame.txt",
    "highlights_cmame.txt", "declarations_cmame.md", "COVER_LETTER.md", "README_CMAME_FLAT_SUBMISSION.md",
    "cmame_submission_flat.zip",
}
MANUSCRIPT_DIRS = {"figures", "cmame_submission_flat", "arxiv"}
LEGACY_TOPLEVEL = {
    "main.tex", "main.pdf", "main.log", "main.txt",
    "main_concise.tex", "main_concise.pdf", "main_concise.log", "main_concise.txt",
}


def is_manuscript_label(label: str) -> bool:
    first = str(label).replace("\\", "/").lstrip("./").split("/")[0]
    return first in MANUSCRIPT_TOPLEVEL or first in MANUSCRIPT_DIRS


def is_legacy_label(label: str) -> bool:
    return str(label).replace("\\", "/").lstrip("./").split("/")[0] in LEGACY_TOPLEVEL


_VERSION_DIR = re.compile(r"v\d{3}_[A-Za-z0-9_]+")
_REPO_TOPLEVEL = {"paper", "proof", "numerics", "external", "validation"}
_VALIDATION_TOPLEVEL = {"legacy_drafts", "docs", "tools", "pipeline_validation_results", "skills", "paper_v047_cylindrical_chain"}


def _route(label: str, default: Path) -> Path:
    label = str(label).replace("\\", "/")
    if label.startswith("../"):
        return (PAPER / label).resolve()
    first = label.lstrip("./").split("/")[0]
    if _VERSION_DIR.fullmatch(first):          # logical work-relative label such as v048_.../results/x
        return NUMERICS / label
    if first in _REPO_TOPLEVEL:
        return REPO / label
    if first in _VALIDATION_TOPLEVEL and first != "paper_v047_cylindrical_chain":
        return VALIDATION / label
    if first == "paper_v047_cylindrical_chain":
        return VALIDATION / label
    if is_manuscript_label(label):
        return LATEX / label
    if is_legacy_label(label):
        return LEGACY / label
    return default / label


def package_path(label: str) -> Path:
    """Resolve a ledger-relative label. `../` labels resolve from this directory (they point into
    numerics/, paper/ or external/); logical work-relative labels (`v048_.../results/x`, `paper/x`,
    `numerics/x`, `legacy_drafts/x`, `docs/x`) go to their folders; manuscript names go to paper/;
    legacy draft names to validation/legacy_drafts/; everything else stays in the ledger."""
    return _route(label, PAPER)


def work_path(label: str) -> Path:
    """Same routing as `package_path`, but unqualified labels resolve against validation/ (the
    former work root) instead of the ledger."""
    return _route(label, VALIDATION)


def work_label(path: Path) -> str:
    """Logical work-relative label of a path, as records stored it before 2026-09-20: numerics
    paths become `v048_.../...`, paper paths `paper/...`, validation paths stay relative to
    validation/, anything else is relative to the repository root."""
    path = Path(path).resolve()
    for base in (NUMERICS, VALIDATION):
        try:
            return path.relative_to(base).as_posix()
        except ValueError:
            pass
    return path.relative_to(REPO).as_posix()
