#!/usr/bin/env python3
"""Read-only validator for the derived arXiv version in `arxiv/`.

Regenerates the arXiv source in memory from `main_cmame.tex` (via `build_arxiv_version.build`)
and checks that the file on disk, the README, the manifest, the figures and the zip are in sync;
checks the compiled log is warning-free when present.  Writes nothing.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
import zipfile
from pathlib import Path

import build_arxiv_version as gen

PAPER = Path(__file__).resolve().parent
from paper_paths import LATEX, package_path as manuscript_path
ARXIV = LATEX / "arxiv"
LOG = ARXIV / "main_arxiv.log"
PDF = ARXIV / "main_arxiv.pdf"

LOG_PATTERNS = [r"Overfull", r"LaTeX Warning", r"Package .*Warning", r"pdfTeX warning"]


class Checks:
    def __init__(self) -> None:
        self.errors: list[str] = []

    def check(self, condition: bool, message: str) -> None:
        if not condition:
            self.errors.append(message)


def main() -> int:
    checks = Checks()
    try:
        expected = gen.build(write=False)
        tex = gen.OUT_TEX.read_text(encoding="utf-8")
        readme = gen.OUT_README.read_text(encoding="utf-8")
        manifest = json.loads(gen.OUT_MANIFEST.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        print(f"arxiv_version=FAIL\n- {exc}")
        return 1

    checks.check(tex == expected["tex"], "arxiv/main_arxiv.tex is stale relative to main_cmame.tex (rerun build_arxiv_version.py)")
    checks.check(readme == expected["readme"], "arxiv/README.md is stale")
    em = expected["manifest"]
    for key in ["schema", "source_sha256", "output_tex_sha256", "figures", "figure_count",
                "plain_abstract_characters", "plain_abstract_within_limit", "bibliography", "claim_state_change", "run_v047_invoked"]:
        checks.check(manifest.get(key) == em[key], f"manifest field stale: {key}")
    checks.check(manifest.get("claim_state_change") is False, "arXiv version must not change claim state")
    checks.check(em["plain_abstract_within_limit"], "plain abstract exceeds the arXiv limit")
    checks.check(tex.startswith("\\pdfoutput=1\n% arXiv preprint version"), "pdfoutput line or generated header missing")
    checks.check("\\documentclass[11pt,a4paper]{article}" in tex, "document class changed")
    checks.check("\\begin{frontmatter}" not in tex and "\\journal{" not in tex, "elsarticle frontmatter leaked into the arXiv source")
    checks.check("\\begin{thebibliography}" in tex, "inline bibliography missing")
    # body identity with the CMAME source modulo figure names
    main = gen.read_text(gen.MAIN_TEX)
    body_main = main[main.index("\\section{Introduction}"):]
    body_arxiv = tex[tex.index("\\section{Introduction}"):]
    mapping = gen.figure_map()
    body_main_mapped, _ = gen.substitute_figures(body_main, mapping)
    checks.check(body_main_mapped == body_arxiv, "arXiv body differs from the CMAME body beyond figure names")
    # figures on disk and in the zip
    for name in expected["figures"]:
        checks.check((ARXIV / name).exists(), f"figure missing in arxiv/: {name}")
        src = gen.FLAT_DIR / name
        if src.exists() and (ARXIV / name).exists():
            checks.check(hashlib.sha256(src.read_bytes()).digest() == hashlib.sha256((ARXIV / name).read_bytes()).digest(),
                         f"figure differs from the flat copy: {name}")
    checks.check(gen.OUT_ZIP.exists(), "arxiv_submission.zip missing")
    if gen.OUT_ZIP.exists():
        with zipfile.ZipFile(gen.OUT_ZIP) as zf:
            names = sorted(zf.namelist())
            checks.check(names == sorted(["main_arxiv.tex"] + expected["figures"]), "zip entries differ from source plus figures")
            if "main_arxiv.tex" in names:
                checks.check(zf.read("main_arxiv.tex").decode("utf-8") == expected["tex"], "zip source stale")
        checks.check(manifest.get("zip_sha256") == hashlib.sha256(gen.OUT_ZIP.read_bytes()).hexdigest(), "manifest zip digest stale")
    # compiled output
    checks.check(PDF.exists(), "arxiv/main_arxiv.pdf missing (compile with latexmk)")
    checks.check(LOG.exists(), "arxiv/main_arxiv.log missing (compile with latexmk)")
    if LOG.exists():
        bad = [line for line in LOG.read_text(errors="replace").splitlines() if any(re.search(p, line) for p in LOG_PATTERNS)]
        checks.check(not bad, "arXiv log has warnings: " + " | ".join(bad[:3]))

    if checks.errors:
        print("arxiv_version=FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1
    print("arxiv_version=PASS")
    print(f"figures={em['figure_count']}")
    print(f"plain_abstract_characters={em['plain_abstract_characters']}")
    print("body_identical_to_cmame_modulo_figure_names=True")
    print("claim_state_change=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
