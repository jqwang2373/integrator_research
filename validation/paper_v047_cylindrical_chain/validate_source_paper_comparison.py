#!/usr/bin/env python3
"""Read-only check for the v047 source-paper comparison boundary."""

from __future__ import annotations

import json
import sys
from pathlib import Path


PAPER = Path(__file__).resolve().parent
ROOT = PAPER.parent
SOURCE_PDF = ROOT.parent / "external" / "literature" / "s11044-026-10153-w.pdf"

EXPECTED_EXAMPLES = {"single_pendulum", "double_pendulum", "four_link", "slider_crank"}


class Checks:
    def __init__(self) -> None:
        self.errors: list[str] = []

    def check(self, condition: bool, message: str) -> None:
        if not condition:
            self.errors.append(message)


def read_json(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(path)
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def read_text(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8", errors="replace")


def contains_normalized(text: str, token: str) -> bool:
    return token in text or " ".join(token.split()) in " ".join(text.split())


def main() -> int:
    checks = Checks()
    try:
        comparison = read_text(PAPER / "SOURCE_PAPER_COMPARISON.md")
        boundary = read_json(PAPER / "CLAIM_BOUNDARY.json")
        manifest = read_json(PAPER / "SUBMISSION_ARTIFACT_MANIFEST.json")
    except Exception as exc:  # noqa: BLE001 - concise CLI failure.
        print(f"v047 source-paper comparison validation: FAIL\n- {exc}")
        return 1

    primary = boundary.get("primary_claim", {})
    comparator = boundary.get("comparator", {})

    checks.check(SOURCE_PDF.exists() and SOURCE_PDF.stat().st_size > 100_000, "source PDF missing or unexpectedly small")
    checks.check(primary.get("accepted_method") == "Gauss6/FullVA", "accepted method changed")
    checks.check(primary.get("method_order_claim") == 6, "accepted method order changed")
    checks.check(comparator.get("expected_order") == 5, "source-paper comparator expected order changed")
    checks.check(boundary.get("full_tfe_stage_replacement") is False, "full-TFE marker changed")
    checks.check(set(primary.get("accepted_examples", [])) == EXPECTED_EXAMPLES, "accepted example set changed")
    checks.check("SOURCE_PAPER_COMPARISON.md" in manifest.get("evidence_anchors", []), "manifest missing comparison anchor")

    required_tokens = [
        "Source Paper Versus v047",
        "`../../external/literature/s11044-026-10153-w.pdf`",
        "higher-order integration of index-3 DAEs with friction using time finite elements on Lie groups",
        "`m=1`",
        "`m=2`",
        "`m=3`",
        "`2m-1`",
        "`2m-1=5`",
        "local `m=3` Gauss-Lobatto TFE formula target",
        "expected order `5`",
        "does not contain this repository's `Gauss6/FullVA` 132-row residual",
        "does not contain this repository's internal full-TFE replacement gate",
        "Accepted method: `Gauss6/FullVA`",
        "Method-order claim: `6`",
        "Smooth observed position/velocity orders: `7.161/7.066`",
        "`single_pendulum`",
        "`double_pendulum`",
        "`four_link`",
        "`slider_crank`",
        "formal-order alternative claim",
        "not an implemented source-paper superiority claim",
        "`CROSS_PAPER_BENCHMARK_CASES.json`",
        "Kissel/Bakke/Negrut",
        "code-resolution gate",
        "Complete source-paper residual reproduction is not claimed",
        "Accepted independent full-TFE stage replacement is not claimed",
        "`full_tfe_stage_replacement=false`",
        "temporal-finite-element weak rows inside Newton",
    ]
    for token in required_tokens:
        checks.check(contains_normalized(comparison, token), f"SOURCE_PAPER_COMPARISON.md missing token: {token}")

    forbidden_tokens = [
        "full_tfe_stage_replacement=true",
        "complete source-paper residual reproduction is accepted",
        "accepted independent full-TFE stage replacement is accepted",
        "source paper contains this repository's internal full-TFE replacement gate",
    ]
    normalized = " ".join(comparison.split()).lower()
    for token in forbidden_tokens:
        checks.check(token.lower() not in normalized, f"SOURCE_PAPER_COMPARISON.md has forbidden claim: {token}")

    if checks.errors:
        print("v047 source-paper comparison validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("v047 source-paper comparison validation: PASS")
    print("source_pdf_found=True")
    print("source_paper_m3_expected_order=5")
    print("accepted_method=Gauss6/FullVA")
    print("accepted_method_order=6")
    print("smooth_projected_orders=7.161/7.066")
    print("full_tfe_stage_replacement=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
