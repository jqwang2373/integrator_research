#!/usr/bin/env python3
"""Validate the paper-core-to-manuscript audit."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent


class Checks:
    def __init__(self) -> None:
        self.errors: list[str] = []

    def check(self, condition: bool, message: str) -> None:
        if not condition:
            self.errors.append(message)


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def main() -> int:
    checks = Checks()
    try:
        audit = read_json(PAPER / "PAPER_CORE_TO_MANUSCRIPT_AUDIT.json")
        md = (PAPER / "PAPER_CORE_TO_MANUSCRIPT_AUDIT.md").read_text(encoding="utf-8")
        core = read_json(PAPER / "PAPER_CORE_RESULT_CONSOLIDATION.json")
    except Exception as exc:  # noqa: BLE001
        print(f"paper core to manuscript audit validation: FAIL\n- {exc}")
        return 1

    checks.check(audit.get("schema") == "paper-core-to-manuscript-audit-v1", "schema changed")
    checks.check(audit.get("status") == "paper_core_results_visible_in_tex_pdf", "status changed")
    checks.check(audit.get("submission_ready") is False, "submission ready overclaimed")
    checks.check(audit.get("core_result_status") == core.get("status"), "core status not carried")
    checks.check(audit.get("paper_core_traceability_closed") is True, "paper core traceability not closed")
    checks.check(audit.get("main_tex_pdf_core_values_present") is True, "main values missing")
    checks.check(audit.get("main_tex_pdf_core_structure_present") is True, "main structure missing")
    checks.check(audit.get("flat_tex_pdf_core_present") is True, "flat core missing")
    execution = audit.get("execution_policy", {})
    checks.check(execution.get("read_only_existing_artifacts") is True, "read-only marker missing")
    checks.check(execution.get("experiments_launched") is False, "experiment launch overclaimed")
    checks.check(execution.get("run_v047_invoked") is False, "run_v047 marker changed")
    checks.check(execution.get("run_v048_invoked") is False, "run_v048 marker changed")
    checks.check(len(audit.get("value_rows", [])) == 7, "value row count changed")
    checks.check(len(audit.get("structure_rows", [])) == 5, "structure row count changed")
    for row in audit.get("value_rows", []) + audit.get("structure_rows", []):
        checks.check(row.get("tex_present") is True, f"{row.get('label')} TeX missing")
        checks.check(row.get("pdf_present") is True, f"{row.get('label')} PDF missing")
    for row in audit.get("flat_rows", []):
        checks.check(row.get("flat_tex_present") is True, f"{row.get('label')} flat TeX missing")
        checks.check(row.get("flat_pdf_present") is True, f"{row.get('label')} flat PDF missing")
    forbidden = audit.get("claim_boundary", {}).get("forbidden_claims", [])
    checks.check("strict source-paper policy external superiority" in forbidden, "source-policy forbidden boundary missing")
    checks.check("submission-ready manuscript/package" in forbidden, "submission-ready forbidden boundary missing")

    for token in [
        "Status: **paper core results visible in TeX/PDF**.",
        "Paper-core traceability closed: `True`.",
        "Experiments launched: `False`.",
        "Submission ready: `False`.",
        "`single_pendulum_order_error` | `True` | `True`",
        "`closed_loop_true_dynamic_figure` | `True` | `True`",
        "does not authorize source-policy superiority",
    ]:
        checks.check(token in md, f"markdown missing token: {token}")

    if checks.errors:
        print("paper core to manuscript audit validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("paper core to manuscript audit validation: PASS")
    print("paper_core_traceability_closed=True")
    print("main_tex_pdf_core_values_present=True")
    print("flat_tex_pdf_core_present=True")
    print("experiments_launched=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
