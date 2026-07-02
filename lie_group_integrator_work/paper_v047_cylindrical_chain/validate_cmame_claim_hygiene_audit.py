#!/usr/bin/env python3
"""Validate the CMAME claim-hygiene audit."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
EXPECTED_SUBMISSION_FILES = {
    "main_cmame.tex",
    "cmame_submission_flat/main_cmame_submission.tex",
    "main_cmame.txt",
    "cmame_submission_flat/main_cmame_submission.txt",
}
EXPECTED_SUPPORT_FILES = {
    "README.md",
    "REVIEWER_CHECKLIST.md",
    "PAPER_CLAIM_LEDGER.md",
    "COVER_LETTER.md",
    "SUBMISSION_PACKET.md",
    "CURRENT_STATUS_CN.md",
}


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


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def contains_normalized(text: str, token: str) -> bool:
    return " ".join(token.split()) in " ".join(text.split())


def main() -> int:
    checks = Checks()
    try:
        audit = read_json(PAPER / "CMAME_CLAIM_HYGIENE_AUDIT.json")
        audit_md = read_text(PAPER / "CMAME_CLAIM_HYGIENE_AUDIT.md")
        cmame_tex = read_text(PAPER / "main_cmame.tex")
        flat_tex = read_text(PAPER / "cmame_submission_flat" / "main_cmame_submission.tex")
        pdf_text = read_text(PAPER / "main_cmame.txt")
        flat_pdf_text = read_text(PAPER / "cmame_submission_flat" / "main_cmame_submission.txt")
    except Exception as exc:  # noqa: BLE001
        print(f"cmame claim-hygiene audit validation: FAIL\n- {exc}")
        return 1

    scope = audit.get("scope", {})
    claim = audit.get("claim_boundary", {})
    check_data = audit.get("checks", {})

    checks.check(audit.get("schema") == "cmame-claim-hygiene-audit-v1", "schema changed")
    checks.check(audit.get("status") == "pass", "claim hygiene audit must pass")
    checks.check(audit.get("submission_ready") is False, "audit must not mark submission ready")
    checks.check(audit.get("external_superiority_claim") is False, "external superiority boundary changed")
    checks.check(
        audit.get("source_policy_superiority_claim_allowed") is False,
        "source-policy superiority boundary changed",
    )
    checks.check(audit.get("default_1e_4_required") is False, "audit incorrectly requires default 1e-4")
    checks.check(audit.get("run_v047_invoked") is False, "audit invoked run_v047")
    checks.check(audit.get("heavy_numerical_run_invoked") is False, "audit invoked heavy run")
    checks.check(
        set(scope.get("submission_text_files", [])) == EXPECTED_SUBMISSION_FILES,
        "submission scan file set changed",
    )
    checks.check(
        set(scope.get("support_text_files", [])) == EXPECTED_SUPPORT_FILES,
        "support scan file set changed",
    )
    checks.check(check_data.get("required_missing_count") == 0, "required claim-boundary text missing")
    checks.check(
        check_data.get("proof_required_missing_count") == 0,
        "required proof-boundary text missing",
    )
    checks.check(check_data.get("submission_forbidden_hit_count") == 0, "submission overclaim text found")
    checks.check(
        check_data.get("proof_forbidden_hit_count") == 0,
        "proof overclaim text found",
    )
    checks.check(check_data.get("support_forbidden_hit_count") == 0, "support overclaim text found")
    checks.check(claim.get("accepted_method") == "Gauss6/FullVA", "accepted method changed")
    checks.check(claim.get("accepted_method_order") == 6, "accepted method order changed")
    checks.check(claim.get("comparator_expected_order") == 5, "comparator order changed")
    checks.check(claim.get("allowed_claim") == "conditional_formal_order_comparison", "allowed claim changed")
    for forbidden in [
        "source_policy_superiority",
        "external_same_test_superiority",
        "complete_source_paper_residual_reproduction",
        "independent_full_tfe_stage_replacement",
        "seventh_order_theorem",
        "unconditional_order_theorem_without_interfaces",
        "closed_eta_h_solver_policy_evidence",
        "fixed_tolerance_as_asymptotic_proof",
        "accepted_residual_to_error_transfer_theorem",
        "source_policy_full_tfe_package_readiness",
    ]:
        checks.check(forbidden in claim.get("not_allowed", []), f"missing not-allowed claim: {forbidden}")

    for text, label in [
        (cmame_tex, "main CMAME source"),
        (flat_tex, "flat CMAME source"),
        (pdf_text, "main CMAME PDF text"),
        (flat_pdf_text, "flat CMAME PDF text"),
    ]:
        for token in [
            "Conditional order comparison",
            "narrow order-comparison sense",
            "does not compare error constants",
            "not a complete source-paper temporal",
            "All-example source-policy status for the flagged baseline rows",
            "These rows remain",
            "not promoted to a CMAME paper-level",
        ]:
            checks.check(contains_normalized(text, token), f"{label} missing token: {token}")
        for token in [
            "conditional order-six theorem",
            "does not claim an unconditional",
            "does not close P6",
            "P7 residual-to-error promotion",
            "fixed-tolerance asymptotic proof",
        ]:
            checks.check(contains_normalized(text, token), f"{label} missing proof-boundary token: {token}")
        for token in [
            "Accepted comparative integrator theorem",
            "accepted external superiority",
            "source-policy superiority claim allowed",
            "full external same-test campaign passed",
            "submission ready=true",
            "then validates the resulting one-step map",
            "It validates the accepted Gauss collocation FullVA residual",
            "unconditional sixth-order theorem",
            "P6 solver-policy condition closed",
            "fixed-tolerance runs prove asymptotic",
            "residual-to-error transfer theorem is closed",
            "P7 residual-to-error theorem closed",
            "source-policy/full-TFE package ready=true",
        ]:
            checks.check(not contains_normalized(text, token), f"{label} has forbidden token: {token}")

    for token in [
        "Status: **PASS**",
        "Allowed claim: `conditional_formal_order_comparison`",
        "Source-policy superiority allowed: `False`",
        "External same-test superiority allowed: `False`",
        "Submission ready: `False`",
        "Required-token missing count: `0`",
        "Proof-boundary required-token missing count: `0`",
        "Submission forbidden-hit count: `0`",
        "Proof-overclaim forbidden-hit count: `0`",
        "Support forbidden-hit count: `0`",
    ]:
        checks.check(token in audit_md, f"markdown missing token: {token}")

    if checks.errors:
        print("cmame claim-hygiene audit validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("cmame claim-hygiene audit validation: PASS")
    print("status=pass")
    print("allowed_claim=conditional_formal_order_comparison")
    print("forbidden_hits=0")
    print("submission_ready=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
