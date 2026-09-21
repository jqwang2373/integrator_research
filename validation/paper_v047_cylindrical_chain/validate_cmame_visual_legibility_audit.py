#!/usr/bin/env python3
"""Read-only validator for the CMAME visual legibility audit."""

from __future__ import annotations

import json
import re
import struct
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
from paper_paths import LATEX, package_path as manuscript_path
AUDIT_MD = PAPER / "CMAME_VISUAL_LEGIBILITY_AUDIT.md"
AUDIT_JSON = PAPER / "CMAME_VISUAL_LEGIBILITY_AUDIT.json"
MAIN_FIGURE = LATEX / "figures" / "asme_lower_pair_graph_bridge.png"
FLAT_FIGURE = LATEX / "cmame_submission_flat" / "Figure_2_asme_lower_pair_graph_bridge.png"
MAIN_PDF_TEXT = LATEX / "main_cmame.txt"
FLAT_PDF_TEXT = LATEX / "cmame_submission_flat" / "main_cmame_submission.txt"
MAIN_LOG = LATEX / "main_cmame.log"
FLAT_LOG = LATEX / "cmame_submission_flat" / "main_cmame_submission.log"


class Checks:
    def __init__(self) -> None:
        self.errors: list[str] = []

    def check(self, condition: bool, message: str) -> None:
        if not condition:
            self.errors.append(message)


def read_text(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8", errors="replace")


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(path)
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def contains_normalized(text: str, token: str) -> bool:
    return token in text or " ".join(token.split()) in " ".join(text.split())


def png_size(path: Path) -> tuple[int, int]:
    data = path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"{path} is not a PNG")
    return struct.unpack(">II", data[16:24])


def log_clean(path: Path) -> bool:
    patterns = [
        r"Overfull",
        r"LaTeX Warning",
        r"Package .*Warning",
        r"pdfTeX warning",
        r"Undefined control sequence",
        r"Emergency stop",
    ]
    text = read_text(path)
    return not any(re.search(pattern, line) for line in text.splitlines() for pattern in patterns)


def main() -> int:
    checks = Checks()
    try:
        audit_md = read_text(AUDIT_MD)
        audit = read_json(AUDIT_JSON)
        main_text = read_text(MAIN_PDF_TEXT)
        flat_text = read_text(FLAT_PDF_TEXT)
        main_w, main_h = png_size(MAIN_FIGURE)
        flat_w, flat_h = png_size(FLAT_FIGURE)
    except Exception as exc:  # noqa: BLE001
        print(f"cmame_visual_legibility_audit=FAIL\n- {exc}")
        return 1

    checks.check(audit.get("schema") == "cmame-visual-legibility-audit-v1", "audit schema changed")
    checks.check(
        audit.get("status") == "b5_closed_mechanism_visual_reproducibility_checked",
        "audit status changed",
    )
    checks.check(audit.get("submission_ready") is False, "visual audit must not claim submission ready")
    checks.check(audit.get("quality_review_passed") is False, "visual audit must not claim quality review passed")
    checks.check(audit.get("execution_policy", {}).get("default_1e-4_required") is False, "visual audit requires default 1e-4")
    checks.check(
        audit.get("execution_policy", {}).get("heavy_numerical_run_invoked_by_audit") is False,
        "visual audit must remain non-numerical",
    )

    closed = audit.get("closed_blocker", {})
    checks.check(closed.get("id") == "B5", "closed blocker is not B5")
    checks.check(closed.get("status") == "closed", "B5 not marked closed in visual audit")
    checks.check(closed.get("closure_basis") == "final_pdf_legibility_check", "B5 closure basis changed")
    checks.check(closed.get("split_mechanism_diagrams_required") is False, "visual audit unexpectedly requires split diagrams")

    figure_checks = audit.get("figure_checks", {})
    min_w = int(figure_checks.get("minimum_width_px", 0))
    min_h = int(figure_checks.get("minimum_height_px", 0))
    checks.check(main_w >= min_w >= 2000, f"main Figure 2 width too small: {main_w}")
    checks.check(main_h >= min_h >= 1700, f"main Figure 2 height too small: {main_h}")
    checks.check(flat_w == main_w and flat_h == main_h, "flat Figure 2 dimensions differ from main Figure 2")
    checks.check(figure_checks.get("main_figure_width_px") == main_w, "main Figure 2 width marker stale")
    checks.check(figure_checks.get("main_figure_height_px") == main_h, "main Figure 2 height marker stale")
    checks.check(figure_checks.get("flat_figure_width_px") == flat_w, "flat Figure 2 width marker stale")
    checks.check(figure_checks.get("flat_figure_height_px") == flat_h, "flat Figure 2 height marker stale")
    for key in [
        "label_layout_pass_completed",
        "source_image_visually_inspected",
        "final_pdf_recompiled_after_regeneration",
        "main_pdf_text_caption_present",
        "flat_pdf_text_caption_present",
        "latex_logs_clean",
    ]:
        checks.check(figure_checks.get(key) is True, f"visual audit figure check not true: {key}")
    checks.check(log_clean(MAIN_LOG), "main CMAME log is not clean")
    checks.check(log_clean(FLAT_LOG), "flat CMAME log is not clean")

    caption = "Coordinate-oriented mechanism schematics and lower-pair constraint inventory"
    checks.check(contains_normalized(main_text, caption), "main PDF text missing Figure 2 caption")
    checks.check(contains_normalized(flat_text, caption), "flat PDF text missing Figure 2 caption")
    checks.check(audit.get("open_blocker_count_after_closure") == 7, "open blocker count after B5 closure changed")
    checks.check(audit.get("closed_blockers") == ["B5"], "closed blocker list changed")
    checks.check(audit.get("open_blockers") == ["B1", "B2", "B3", "B4", "B6", "B7", "B8"], "open blocker list changed")
    checks.check(audit.get("remaining_figure_blocker", {}).get("id") == "B7", "remaining figure blocker marker missing")
    override = audit.get("current_narrowed_claim_override", {})
    checks.check(
        override.get("status") == "historical_b5_audit_current_b7_closed_elsewhere",
        "current narrowed-claim override missing",
    )
    checks.check(
        override.get("b7_current_status") == "closed_under_narrowed_claim_policy",
        "current B7 narrowed-claim status missing",
    )
    checks.check(override.get("full_source_policy_figures_ready") is False, "source-policy figure readiness overclaimed")

    for token in [
        "Status: **B5 CLOSED - MECHANISM VISUAL REPRODUCIBILITY CHECKED**",
        "default `1e-4` campaign",
        "Figure 2 image size is at least `2000 x 1700`",
        "`open_blockers=7`",
        "`closed_blockers=B5`",
        "This does not close the broader publication figure-set blocker `B7`",
        "Current Narrowed-Claim Override",
        "current narrowed-claim package closes B7 elsewhere",
        "full source-policy comparison figures remain future work",
    ]:
        checks.check(contains_normalized(audit_md, token), f"visual audit markdown missing token: {token}")

    if checks.errors:
        print("cmame_visual_legibility_audit=FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("cmame_visual_legibility_audit=PASS")
    print("b5_status=closed")
    print("open_blockers=7")
    print("closed_blockers=B5")
    print(f"figure2_dimensions={main_w}x{main_h}")
    print("default_1e-4=False")
    print("submission_ready=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
