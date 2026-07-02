#!/usr/bin/env python3
"""Read-only checks for the concise v047 paper draft."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


PAPER = Path(__file__).resolve().parent
ROOT = PAPER.parent
PIPELINE = ROOT / "v047_cylindrical_chain_pipeline"
RESULTS = PIPELINE / "results"


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


def read_json(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(path)
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def contains_normalized(text: str, token: str) -> bool:
    return token in text or " ".join(token.split()) in " ".join(text.split())


def rounded(value: float, digits: int = 3) -> str:
    return f"{value:.{digits}f}"


def latex_sci(value: float, digits: int = 3) -> str:
    mantissa, exponent = f"{value:.{digits}e}".split("e")
    return f"{mantissa}\\times10^{{{int(exponent)}}}"


def check_required_files(checks: Checks) -> None:
    for path in [
        PAPER / "main_concise.tex",
        PAPER / "main_concise.pdf",
        PAPER / "main_concise.log",
        PAPER / "CLAIM_BOUNDARY.json",
        PAPER / "ORDER_ACCEPTANCE_GATE.md",
        PAPER / "ORDER_ACCEPTANCE_GATE.json",
        RESULTS / "summary_v047.json",
        ROOT / "CURRENT_PIPELINE_CONTRACT.md",
    ]:
        checks.check(path.exists() and path.stat().st_size > 0, f"missing or empty file: {path}")


def check_latex_log(checks: Checks) -> None:
    log_path = PAPER / "main_concise.log"
    if not log_path.exists():
        checks.check(False, "main_concise.log missing")
        return
    patterns = [
        r"Overfull",
        r"LaTeX Warning",
        r"Package .*Warning",
        r"pdfTeX warning",
    ]
    matches: list[str] = []
    for line in log_path.read_text(errors="replace").splitlines():
        if any(re.search(pattern, line) for pattern in patterns):
            matches.append(line)
    checks.check(not matches, f"main_concise.log has warnings: {matches[-3:]}")


def check_claim_boundary(checks: Checks, boundary: dict, summary: dict, tex: str) -> None:
    primary = boundary.get("primary_claim", {})
    comparator = boundary.get("comparator", {})
    asme = boundary.get("asme_acceptance", {})
    caveats = set(boundary.get("open_caveats", []))
    summary_asme = summary.get("asme_gate", {})
    smooth = summary["convergence"]["cases"]["cylindrical_smooth"]["projected_velocity"]
    sharp = summary["convergence"]["cases"]["cylindrical_sharp"]["projected_velocity"]

    smooth_pos = rounded(float(smooth["position_order"]))
    smooth_vel = rounded(float(smooth["velocity_order"]))
    sharp_pos = rounded(float(sharp["position_order"]))
    sharp_vel = rounded(float(sharp["velocity_order"]))

    checks.check(primary.get("accepted_method") == "Gauss6/FullVA", "accepted method changed")
    checks.check(primary.get("method_order_claim") == 6, "method order claim changed")
    checks.check(primary.get("smooth_projected_orders", {}).get("position") == 7.161, "position order changed")
    checks.check(primary.get("smooth_projected_orders", {}).get("velocity") == 7.066, "velocity order changed")
    checks.check(comparator.get("expected_order") == 5, "comparator order changed")
    checks.check(comparator.get("complete_source_paper_residual_accepted") is False, "comparator boundary changed")
    checks.check(boundary.get("full_tfe_stage_replacement") is False, "full-TFE boundary changed")
    checks.check(asme.get("full_tfe_required_for_gate") is False, "ASME gate now depends on full-TFE")
    checks.check(summary_asme.get("status") == primary.get("asme_gate_status"), "summary ASME status mismatch")
    checks.check(set(summary_asme.get("models", {})) == {"single_pendulum", "double_pendulum", "four_link", "slider_crank"}, "ASME model set mismatch")
    checks.check(
        caveats
        == {
            "sparse_speed_quantified",
            "full_tfe_stage_replacement_missing",
            "sharp_friction_coarse_order_reduction_ultra_recovered",
        },
        "open caveat set changed",
    )

    required_tex = [
        "This concise draft states only the accepted v047 paper claim",
        "A Conditional Sixth-Order Lie-Group FullVA Integrator for Lower-Pair Mechanisms",
        "\\newtheorem{theorem}{Theorem}",
        "Accepted formal-order comparison theorem",
        "\\label{thm:formal-order}",
        "Proof obligations and artifact evidence",
        "\\label{tab:proof-evidence}",
        "PROOF_EVIDENCE_MATRIX.md",
        "cylindrical_chain_convergence.csv",
        "reference_h=0.005",
        "The theorem excludes complete source-paper",
        "residual reproduction",
        "full_tfe_stage_replacement=false",
        "not an accepted independent full-\\tfe{} replacement",
        "local paper-style $m=3$ Gauss--Lobatto temporal finite-element target",
        "p_{\\mathrm{TFE}}(m)=2m-1",
        "p_{\\mathrm{TFE}}(3)=5",
        "order-six \\method{} versus an order-five paper-style target",
        "conditional sixth-order Gauss",
        "SOURCE_PAPER_COMPARISON.md",
        "ORDER_ACCEPTANCE_GATE.md",
        "accepted dynamic order rows",
        "not accepted external dynamic-order rows",
        "coarse_first_no_default_1e-4",
        "validate_order_acceptance_gate.py",
        "expected order five",
        "single pendulum",
        "double pendulum",
        "four link",
        "slider crank",
        smooth_pos,
        smooth_vel,
        sharp_pos,
        sharp_vel,
        latex_sci(float(asme["single_pendulum"]["max_stage_residual_norm"])),
        rounded(float(asme["single_pendulum"]["absolute_fullva_min_order"])),
        rounded(float(asme["double_pendulum"]["method_min_order"])),
        latex_sci(float(asme["four_link"]["max_closed_loop_constraint_norm"])),
        latex_sci(float(asme["four_link"]["max_dynamics_residual_norm"])),
        latex_sci(float(asme["slider_crank"]["max_closed_loop_constraint_norm"])),
        latex_sci(float(asme["slider_crank"]["max_dynamics_residual_norm"])),
        "Sparse AD structure is correct and quantified",
        "sharp-friction coarse regime is order-reduced",
        "Complete source-paper \\tfe{} residual replacement remains future work",
    ]
    for token in required_tex:
        checks.check(contains_normalized(tex, token), f"main_concise.tex missing token: {token}")

    forbidden = [
        "full_tfe_stage_replacement=true",
        "complete source-paper residual reproduction is accepted",
        "complete source-paper \\tfe{} residual replacement is accepted",
        "full-\\tfe{} replacement is accepted",
    ]
    for token in forbidden:
        checks.check(token not in tex, f"main_concise.tex has forbidden claim: {token}")


def main() -> int:
    checks = Checks()
    try:
        tex = read_text(PAPER / "main_concise.tex")
        boundary = read_json(PAPER / "CLAIM_BOUNDARY.json")
        summary = read_json(RESULTS / "summary_v047.json")
    except Exception as exc:  # noqa: BLE001 - validator should report a concise failure.
        print(f"v047 concise paper validation: FAIL\n- {exc}")
        return 1

    check_required_files(checks)
    check_latex_log(checks)
    check_claim_boundary(checks, boundary, summary, tex)

    pdf_path = PAPER / "main_concise.pdf"
    if pdf_path.exists():
        checks.check(pdf_path.stat().st_size > 100_000, "main_concise.pdf is unexpectedly small")

    if checks.errors:
        print("v047 concise paper validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("v047 concise paper validation: PASS")
    print("accepted_method=Gauss6/FullVA")
    print("smooth_projected_orders=7.161/7.066")
    print("comparator_expected_order=5")
    print("asme_models=double_pendulum,four_link,single_pendulum,slider_crank")
    print("full_tfe_stage_replacement=False")
    print(f"pdf_size_bytes={pdf_path.stat().st_size}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
