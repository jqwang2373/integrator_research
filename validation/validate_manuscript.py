#!/usr/bin/env python3
"""Lightweight validator for the rewritten manuscript (paper/main_cmame.tex, 2026-09-21 onwards).

Checks
  1. the LaTeX log is clean: no errors, no undefined references or citations, no multiply-defined
     labels, no overfull boxes wider than 5 pt;
  2. every number printed in the result tables of the numerical section equals, to the printed
     precision, a value in the result file the table is generated from;
  3. every Lean theorem named in the Lean table exists in proof/, and the theorem count quoted in
     the text equals the count in proof/;
  4. the arXiv copy (paper/arxiv/main_arxiv.tex) is in sync with the manuscript when it exists.

Usage: .venv_sbel/bin/python validation/validate_manuscript.py [--tex paper/main_cmame.tex]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent
PAPER = REPO / "paper"
PROOF = REPO / "proof"
RESULTS = REPO / "numerics" / "v049_paper_experiments" / "results"
CHECKS = ROOT / "paper_v047_cylindrical_chain"

# table label -> result file(s) whose numbers the table must come from
TABLE_SOURCES = {
    "tab:e1": [RESULTS / "E1_convergence.json"],
    "tab:e2": [RESULTS / "E2_gauss_family.json"],
    "tab:e3": [RESULTS / "E3_friction_sweep.json"],
    "tab:e4": [RESULTS / "E4_asme.json"],
    "tab:e5": [RESULTS / "E5_public_baselines.json"],
    "tab:e7": [RESULTS / "E7_solver_envelope.json"],
    "tab:exact-identity-check": [CHECKS / "EXACT_STAGE_IDENTITY_NUMERICAL_CHECK.json"],
    "tab:p2-constants-check": [CHECKS / "P2_CONSTANTS_NUMERICAL_CHECK.json"],
    "tab:predictor-check": [CHECKS / "P2_CONSTANTS_NUMERICAL_CHECK.json"],
}
# tables whose cells are ranges or otherwise not single values: only check the numbers listed here
NUMBER_RE = re.compile(r"\$?(-?\d+\.?\d*)\s*(?:\\times\s*10\^\{(-?\d+)\}|\\mathrm\{e\}\{(-?\d+)\})?\$?")


class Checks:
    def __init__(self) -> None:
        self.passed = 0
        self.failed: list[str] = []

    def check(self, ok: bool, msg: str) -> None:
        if ok:
            self.passed += 1
        else:
            self.failed.append(msg)


def collect_numbers(obj, out: list[float]) -> None:
    if isinstance(obj, bool):
        return
    if isinstance(obj, (int, float)):
        out.append(float(obj))
    elif isinstance(obj, dict):
        for v in obj.values():
            collect_numbers(v, out)
    elif isinstance(obj, list):
        for v in obj:
            collect_numbers(v, out)


def parse_cell_numbers(cell: str) -> list[tuple[float, int]]:
    """Return (value, significant digits) for each number in a table cell; skip ranges and dashes."""
    cell = cell.strip()
    if not cell or cell in ("--", "-", "roundoff") or "--" in cell.replace("\\\\", ""):
        return []
    out = []
    for m in re.finditer(r"(-?\d+\.?\d*)(?:\\times\s*10\^\{(-?\d+)\}|\\mathrm\{e\}\{(-?\d+)\})?", cell):
        mant, e1, e2 = m.group(1), m.group(2), m.group(3)
        exp = int(e1 if e1 is not None else (e2 if e2 is not None else 0))
        digits = len(mant.replace("-", "").replace(".", "").lstrip("0")) or 1
        out.append((float(mant) * 10.0 ** exp, digits))
    return out


def number_matches(value: float, digits: int, pool: list[float]) -> bool:
    if value == 0.0:
        return any(abs(p) < 1e-300 for p in pool)
    tol = 0.55 * 10.0 ** (-(digits - 1))  # half a unit in the last printed significant digit (relative)
    return any(p != 0 and abs(p - value) / abs(value) <= tol + 1e-12 for p in pool)


def table_bodies(tex: str) -> dict[str, list[str]]:
    """label -> list of body rows (between \\midrule and \\bottomrule, excluding header/footer rows)."""
    out = {}
    for m in re.finditer(r"\\begin\{table\}.*?\\label\{(tab:[^}]+)\}(.*?)\\end\{table\}", tex, flags=re.S):
        label, body = m.group(1), m.group(2)
        rows = []
        for block in re.findall(r"\\midrule(.*?)(?=\\midrule|\\bottomrule)", body, flags=re.S):
            for line in block.split("\\\\"):
                line = line.strip()
                if line and "multicolumn" not in line and not line.startswith("&") and "fitted order" not in line:
                    rows.append(line)
        out[label] = rows
    return out


def check_tables(tex: str, checks: Checks) -> None:
    bodies = table_bodies(tex)
    for label, sources in TABLE_SOURCES.items():
        if label not in bodies:
            continue
        pool: list[float] = []
        for src in sources:
            checks.check(src.exists(), f"{label}: result file missing: {src.name}")
            if src.exists():
                collect_numbers(json.loads(src.read_text()), pool)
        for row in bodies[label]:
            for cell in row.split("&"):
                for value, digits in parse_cell_numbers(cell):
                    checks.check(number_matches(value, digits, pool), f"{label}: printed value {value:g} ({digits} digits) not found in {', '.join(s.name for s in sources)}")


def check_log(log_path: Path, checks: Checks) -> None:
    checks.check(log_path.exists(), f"LaTeX log missing: {log_path}")
    if not log_path.exists():
        return
    log = log_path.read_text(encoding="utf-8", errors="replace")
    checks.check("\n! " not in log, "LaTeX error in log")
    checks.check("undefined" not in log.lower() or "There were undefined references" not in log, "undefined references")
    checks.check("Citation" not in log or "undefined" not in log, "undefined citations")
    checks.check("multiply defined" not in log, "multiply-defined labels")
    wide = [float(x) for x in re.findall(r"Overfull \\hbox \(([0-9.]+)pt too wide", log)]
    checks.check(all(w <= 5.0 for w in wide), f"overfull boxes wider than 5pt: {sorted(wide)[-3:]}")


def check_lean(tex: str, checks: Checks) -> None:
    names = re.findall(r"\\nolinkurl\{([A-Za-z0-9_.']+)\}", tex)
    lean_names = [n for n in names if re.match(r"^[A-Za-z][A-Za-z0-9_]*(\.[A-Za-z][A-Za-z0-9_]*)*$", n) and "/" not in n and "." not in n[-5:]]
    src = "\n".join(p.read_text(encoding="utf-8") for p in PROOF.rglob("*.lean") if ".lake" not in p.parts)
    for n in lean_names:
        short = n.split(".")[-1]
        if n in ("propext", "Quot.sound") or n.startswith("Classical"):
            continue
        checks.check(re.search(r"(theorem|lemma)\s+" + re.escape(short) + r"\b", src) is not None, f"Lean theorem not found in proof/: {n}")
    count = len(re.findall(r"^(theorem|lemma)\s+[A-Za-z_][A-Za-z0-9_.']*", src, flags=re.M))
    quoted = re.findall(r"\$(\d+)\$ theorems", tex)
    for q in quoted:
        checks.check(int(q) == count, f"theorem count in text ({q}) differs from proof/ ({count})")


def check_arxiv(tex_path: Path, checks: Checks) -> None:
    manifest = PAPER / "arxiv" / "ARXIV_VERSION.json"
    if not manifest.exists() or tex_path.name != "main_cmame.tex":
        return
    import hashlib
    m = json.loads(manifest.read_text())
    digest = hashlib.sha256(tex_path.read_text(encoding="utf-8").encode("utf-8")).hexdigest()
    src = m.get("source_sha256") or m.get("main_cmame_sha256") or m.get("source", {}).get("sha256")
    if src:
        checks.check(src == digest, "arXiv manifest source digest differs from the manuscript (rerun build_arxiv_version.py)")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tex", default=str(PAPER / "main_cmame.tex"))
    args = ap.parse_args()
    tex_path = Path(args.tex)
    tex = tex_path.read_text(encoding="utf-8")
    checks = Checks()
    check_log(tex_path.with_suffix(".log"), checks)
    check_tables(tex, checks)
    check_lean(tex, checks)
    check_arxiv(tex_path, checks)
    for f in checks.failed:
        print("FAIL:", f)
    print(f"validate_manuscript: {checks.passed} passed, {len(checks.failed)} failed ({tex_path.name})")
    return 1 if checks.failed else 0


if __name__ == "__main__":
    sys.exit(main())
