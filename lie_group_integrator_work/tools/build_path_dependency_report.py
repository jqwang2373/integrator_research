#!/usr/bin/env python3
"""Machine-readable map of the paper package: what every file is, and who reads it.

Writes `docs/PATH_DEPENDENCY_REPORT.md` and `docs/PATH_DEPENDENCY_REPORT.json`.  For each file in
`paper_v047_cylindrical_chain/` (top level plus the `arxiv/`, `lean/`, `notes/`, `figures/` and
`cmame_*` subtrees) the report records a family (manuscript, derived output, gate/record, builder,
validator, runner, bundle, note, ...), the scripts that mention it, and whether it is reachable
from the active validation machinery (the two validator chains, the builder sequence, the review
agent, the gate and arXiv generators).  Records whose JSON carries `superseded_by` are marked
retired.  Read-only; it moves nothing.  Run from anywhere: `python3 tools/build_path_dependency_report.py`.
"""

from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

WORK = Path(__file__).resolve().parent.parent
PAPER = WORK / "paper_v047_cylindrical_chain"
OUT_MD = WORK / "docs" / "PATH_DEPENDENCY_REPORT.md"
OUT_JSON = WORK / "docs" / "PATH_DEPENDENCY_REPORT.json"

ACTIVE_ROOTS = [
    "../validate_pipeline_outputs.py", "validate_paper_package.py", "build_cmame_flat_archive.py",
    "build_cmame_claim_hygiene_audit.py", "build_objective_completion_audit.py",
    "build_cmame_reproducibility_package_manifest.py", "sync_submission_artifact_manifest_boundary.py",
    "build_cmame_submission_integrity_audit.py", "build_cmame_runner_centered_reproducibility_audit.py",
    "build_cmame_minimal_reproducibility_candidate.py", "cmame_submission_review_agent.py",
    "build_exact_stage_identity_gate.py", "build_arxiv_version.py", "run_exact_stage_identity_numerical_check.py",
    "run_p2_constants_numerical_check.py", "generate_publication_figures.py",
]

MANUSCRIPTS = {"main_cmame.tex": "CMAME manuscript source (authoritative)",
               "cmame_submission_flat/main_cmame_submission.tex": "Elsevier flat copy (derived from main_cmame.tex)",
               "arxiv/main_arxiv.tex": "arXiv preprint (derived by build_arxiv_version.py)",
               "main.tex": "legacy internal status report (superseded, kept for the record)",
               "main_concise.tex": "legacy concise draft (superseded, kept for the record)"}
SUBMISSION_SIDECARS = {"highlights_cmame.txt", "declarations_cmame.md", "COVER_LETTER.md", "CMAME_SUBMISSION_CHECKLIST.md",
                       "SUBMISSION_PACKET.md", "SUBMISSION_ARTIFACT_MANIFEST.json", "SUBMISSION_FILE_INVENTORY.md",
                       "REVIEW_RESPONSE_TEMPLATE.md", "REVIEWER_CHECKLIST.md", "README_CMAME_FLAT_SUBMISSION.md"}


def family_of(rel: str) -> str:
    name = rel.split("/")[-1]
    if rel in MANUSCRIPTS:
        return "manuscript"
    if rel.startswith("figures/"):
        return "figure"
    if rel.startswith("lean/"):
        return "lean"
    if rel.startswith("notes/"):
        return "note"
    if rel.startswith("arxiv/") or rel.startswith("cmame_submission_flat/"):
        return "submission_copy"
    if rel.startswith("cmame_"):
        return "reproducibility_bundle"
    if name in SUBMISSION_SIDECARS:
        return "submission_sidecar"
    if name.startswith("build_") and name.endswith(".py"):
        return "builder"
    if name.startswith("validate_") and name.endswith(".py"):
        return "validator"
    if name.startswith("run_") and (name.endswith(".py") or name.endswith(".sh")):
        return "runner"
    if name.endswith(".py"):
        return "script"
    if name.endswith((".pdf", ".log", ".txt")) and name.split(".")[0] in {"main", "main_cmame", "main_concise"}:
        return "derived_output"
    if name.endswith(".zip"):
        return "archive"
    if name.endswith((".json", ".md", ".csv")):
        return "record"
    if name.endswith(".tex"):
        return "tex_fragment"
    return "other"


def main() -> int:
    byproducts = (".aux", ".fls", ".fdb_latexmk", ".spl", ".out", ".synctex.gz")
    files = sorted(p for p in PAPER.rglob("*") if p.is_file()
                   and "__pycache__" not in p.parts and ".lake" not in p.parts and not p.name.startswith(".")
                   and not p.name.endswith(byproducts))
    rels = [str(p.relative_to(PAPER)).replace("\\", "/") for p in files]
    scripts: dict[str, str] = {}
    for p, rel in zip(files, rels):
        if p.suffix == ".py" and "/" not in rel:
            scripts[rel] = p.read_text(encoding="utf-8", errors="replace")
    scripts["../validate_pipeline_outputs.py"] = (WORK / "validate_pipeline_outputs.py").read_text(encoding="utf-8", errors="replace")

    names = set(rels)
    basenames = {rel: rel.split("/")[-1] for rel in rels}
    refs: dict[str, set[str]] = {s: set() for s in scripts}
    for s, txt in scripts.items():
        for rel in rels:
            if rel == s:
                continue
            base = basenames[rel]
            stem = base.rsplit(".", 1)[0]
            if rel in txt or base in txt or (len(stem) > 12 and stem in txt):
                refs[s].add(rel)

    reach: set[str] = set()
    stack = list(ACTIVE_ROOTS)
    while stack:
        s = stack.pop()
        if s in reach or s not in scripts:
            continue
        reach.add(s)
        stack.extend(r for r in refs[s] if r.endswith(".py") and r not in reach)
    needed: set[str] = set()
    for s in reach:
        needed |= refs[s]
    needed |= {r for r in ACTIVE_ROOTS if r in names}

    readers: dict[str, list[str]] = defaultdict(list)
    for s, rs in refs.items():
        for r in rs:
            readers[r].append(s)

    superseded: dict[str, str] = {}
    for p, rel in zip(files, rels):
        if p.suffix == ".json":
            try:
                d = json.loads(p.read_text(encoding="utf-8"))
            except Exception:  # noqa: BLE001
                continue
            if isinstance(d, dict) and d.get("superseded_by"):
                superseded[rel.rsplit(".", 1)[0]] = str(d["superseded_by"])

    entries = []
    for rel in rels:
        fam = family_of(rel)
        stem = rel.rsplit(".", 1)[0]
        is_script = rel.endswith(".py") and "/" not in rel
        status = "active"
        if stem in superseded:
            status = "retired"
        elif is_script and rel not in reach:
            status = "manual_or_retired_script"
        elif not is_script and rel not in needed and fam in {"record", "tex_fragment", "other", "note"}:
            status = "not_read_by_active_scripts"
        entries.append({
            "path": rel, "family": fam, "status": status,
            "superseded_by": superseded.get(stem),
            "reachable_from_active_roots": (rel in reach) if is_script else None,
            "read_by_active_script": (rel in needed) if not is_script else None,
            "reader_count": len(readers.get(rel, [])),
            "readers": sorted(readers.get(rel, []))[:12],
            "description": MANUSCRIPTS.get(rel),
        })

    by_family = Counter(e["family"] for e in entries)
    by_status = Counter(e["status"] for e in entries)
    payload = {
        "schema": "path-dependency-report-v1",
        "paper_dir": "lie_group_integrator_work/paper_v047_cylindrical_chain",
        "active_roots": ACTIVE_ROOTS,
        "file_count": len(entries),
        "family_counts": dict(sorted(by_family.items())),
        "status_counts": dict(sorted(by_status.items())),
        "reachable_script_count": len([s for s in reach if not s.startswith("..")]),
        "superseded_records": superseded,
        "entries": entries,
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    def rows(pred, limit=None):
        sel = [e for e in entries if pred(e)]
        if limit:
            sel = sel[:limit]
        return "\n".join(f"| `{e['path']}` | {e['status']} | {e['reader_count']} |" for e in sel)

    md = [
        "# Path dependency report (paper package)",
        "",
        "Generated by `tools/build_path_dependency_report.py`; read-only. It answers two questions for every",
        "file under `paper_v047_cylindrical_chain/`: what family it belongs to, and which scripts read it.",
        "A script is *reachable* when the active machinery (the two validator chains, the builder sequence,",
        "the review agent, the gate/arXiv generators) invokes or imports it, transitively. A record is",
        "*retired* when its JSON carries `superseded_by`.",
        "",
        f"Files: **{len(entries)}**. Reachable scripts: **{payload['reachable_script_count']}**.",
        "",
        "## Families",
        "",
        "| family | count | meaning |",
        "| --- | ---: | --- |",
    ]
    meaning = {
        "manuscript": "LaTeX sources; `main_cmame.tex` is authoritative, the flat and arXiv copies are derived",
        "submission_copy": "files inside `cmame_submission_flat/` and `arxiv/` (derived; regenerate, do not edit)",
        "derived_output": "PDF / log / text dumps of the manuscripts (validators read the logs and text dumps)",
        "submission_sidecar": "highlights, declarations, cover letter, checklists, manifests",
        "figure": "figure sources under `figures/`",
        "lean": "byte-identical copy of the Lean development (`~/lean/integrator_order_proof`)",
        "note": "backups and working notes (`notes/`), not read by validators",
        "record": "JSON/Markdown/CSV audit records and gates (the evidence ledger)",
        "builder": "`build_*.py`: regenerate one record each; run on demand",
        "validator": "`validate_*.py`: read-only checks of one record each",
        "runner": "`run_*.py` / `run_*.sh`: numerical probes and guarded drivers",
        "script": "other scripts (review agent, figure generator, manifest sync, replay core)",
        "reproducibility_bundle": "runner candidates and the narrowed reproducibility bundle (`cmame_*` directories)",
        "archive": "zip archives",
        "tex_fragment": "TeX fragments that are not compiled on their own",
        "other": "everything else",
    }
    for fam, cnt in sorted(by_family.items()):
        md.append(f"| {fam} | {cnt} | {meaning.get(fam, '')} |")
    md += ["", "## Status", "", "| status | count |", "| --- | ---: |"]
    for st, cnt in sorted(by_status.items()):
        md.append(f"| {st} | {cnt} |")
    md += ["", "## Retired records (kept, marked `superseded_by`)", "", "| record | superseded by |", "| --- | --- |"]
    for stem, by in sorted(superseded.items()):
        md.append(f"| `{stem}` | `{by}` |")
    md += ["", "## Scripts not reachable from the active machinery", "",
           "Manual tools or builders of retired records. They are kept because their records are still",
           "validated read-only or because they are the reproducibility scripts of reported tables.", "",
           "| script | status | readers |", "| --- | --- | ---: |",
           rows(lambda e: e["family"] in {"builder", "validator", "runner", "script"} and e["status"] == "manual_or_retired_script")]
    md += ["", "## Records not read by any active script", "", "| file | status | readers |", "| --- | --- | ---: |",
           rows(lambda e: e["status"] == "not_read_by_active_scripts")]
    md += ["", "## Manuscripts and derived copies", "", "| file | status | readers |", "| --- | --- | ---: |",
           rows(lambda e: e["family"] in {"manuscript", "derived_output", "submission_sidecar"})]
    md += ["", "Full per-file detail (readers per file) is in `PATH_DEPENDENCY_REPORT.json`.", ""]
    OUT_MD.write_text("\n".join(md), encoding="utf-8")
    print(f"path_dependency_report=written files={len(entries)} reachable_scripts={payload['reachable_script_count']}")
    print("status_counts=" + json.dumps(payload["status_counts"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
