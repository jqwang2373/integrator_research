#!/usr/bin/env python3
"""Assemble the rewritten manuscript from paper/rewrite/parts/*.tex and sync the experiment figures.

Usage: python assemble.py [--target main_cmame]   (default target: paper/rewrite/main_rewrite.tex)

The parts are concatenated in lexical order.  Experiment figures are copied from
numerics/v049_paper_experiments/results/ into paper/figures/ under the names used by the manuscript.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PAPER = HERE.parent
REPO = PAPER.parent
PARTS = HERE / "parts"
RESULTS = REPO / "numerics" / "v049_paper_experiments" / "results"
FIGURES = PAPER / "figures"

FIGURE_MAP = {
    "E1_convergence.png": "e1_convergence.png",
    "E2_gauss_family.png": "e2_gauss_family.png",
    "E3_friction_sweep.png": "e3_friction_sweep.png",
    "E4_asme.png": "e4_benchmarks.png",
    "E5_double_pendulum.png": "e5_double_pendulum.png",
    "E6_long_time.png": "e6_regular_branch.png",
}


def main() -> int:
    target = PAPER / ("main_cmame.tex" if "--target" in sys.argv and "main_cmame" in sys.argv else "main_rewrite.tex")
    parts = sorted(PARTS.glob("*.tex"))
    text = "\n".join(p.read_text(encoding="utf-8").rstrip("\n") + "\n" for p in parts)
    target.write_text(text, encoding="utf-8")
    copied = []
    for src, dst in FIGURE_MAP.items():
        s = RESULTS / src
        if s.exists():
            shutil.copyfile(s, FIGURES / dst)
            copied.append(dst)
    print(f"wrote {target} ({text.count(chr(10))} lines) from {len(parts)} parts; figures: {', '.join(copied) or 'none'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
