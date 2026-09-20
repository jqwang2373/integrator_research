#!/usr/bin/env python3
"""Build a read-only claim-hygiene audit for the CMAME package.

The audit is intentionally narrow: it checks the CMAME-facing manuscript,
flat source, extracted PDF text, and submission-facing support notes for
over-strong comparative wording. It does not rewrite the paper and does not
run numerical campaigns.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
from paper_paths import LATEX, package_path as manuscript_path
OUT_JSON = PAPER / "CMAME_CLAIM_HYGIENE_AUDIT.json"
OUT_MD = PAPER / "CMAME_CLAIM_HYGIENE_AUDIT.md"

SUBMISSION_TEXT_FILES = [
    "main_cmame.tex",
    "cmame_submission_flat/main_cmame_submission.tex",
    "main_cmame.txt",
    "cmame_submission_flat/main_cmame_submission.txt",
]

SUPPORT_TEXT_FILES = [
    "README.md",
    "REVIEWER_CHECKLIST.md",
    "PAPER_CLAIM_LEDGER.md",
    "COVER_LETTER.md",
    "SUBMISSION_PACKET.md",
    "CURRENT_STATUS_CN.md",
]

REQUIRED_SUBMISSION_TOKENS = [
    "Conditional order comparison",
    "narrow order-comparison sense",
    "does not compare error constants",
    "not a complete source-paper temporal",
    "All-example source-policy status for the flagged baseline rows",
    "These rows remain",
    "not promoted to a CMAME paper-level",
]

REQUIRED_PROOF_BOUNDARY_TOKENS = [
    "conditional order-six theorem",
    "does not claim an unconditional",
    "does not close P6",
    "P7 residual-to-error promotion",
    "fixed-tolerance asymptotic proof",
]

FORBIDDEN_SUBMISSION_TOKENS = [
    "Accepted comparative integrator theorem",
    "accepted external superiority",
    "source-policy superiority claim allowed",
    "full external same-test campaign passed",
    "submission ready=true",
    "then validates the resulting one-step map",
    "It validates the accepted Gauss collocation FullVA residual",
]

FORBIDDEN_PROOF_OVERCLAIM_TOKENS = [
    "unconditional sixth-order theorem",
    "P6 solver-policy condition closed",
    "fixed-tolerance runs prove asymptotic",
    "residual-to-error transfer theorem is closed",
    "P7 residual-to-error theorem closed",
    "source-policy/full-TFE package ready=true",
]

FORBIDDEN_SUPPORT_TOKENS = [
    "Accepted comparative integrator theorem",
    "accepted better-integrator theorem",
    "The theorem proves only the comparative integrator claim",
]


def read_text(rel_path: str) -> str:
    return (manuscript_path(rel_path)).read_text(encoding="utf-8", errors="replace")


def count_token(text: str, token: str) -> int:
    normalized_text = " ".join(text.split())
    normalized_token = " ".join(token.split())
    return normalized_text.count(normalized_token)


def scan_tokens(files: list[str], tokens: list[str]) -> dict[str, dict[str, int]]:
    out: dict[str, dict[str, int]] = {}
    for rel_path in files:
        text = read_text(rel_path)
        out[rel_path] = {token: count_token(text, token) for token in tokens}
    return out


def missing_required(files: list[str], tokens: list[str]) -> list[dict[str, str]]:
    missing: list[dict[str, str]] = []
    for rel_path in files:
        text = read_text(rel_path)
        for token in tokens:
            if count_token(text, token) == 0:
                missing.append({"file": rel_path, "token": token})
    return missing


def positive_counts(scan: dict[str, dict[str, int]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for rel_path, token_counts in scan.items():
        for token, count in token_counts.items():
            if count:
                rows.append({"file": rel_path, "token": token, "count": count})
    return rows


def main() -> None:
    submission_forbidden_scan = scan_tokens(SUBMISSION_TEXT_FILES, FORBIDDEN_SUBMISSION_TOKENS)
    proof_forbidden_scan = scan_tokens(SUBMISSION_TEXT_FILES, FORBIDDEN_PROOF_OVERCLAIM_TOKENS)
    support_forbidden_scan = scan_tokens(SUPPORT_TEXT_FILES, FORBIDDEN_SUPPORT_TOKENS)
    required_missing = missing_required(SUBMISSION_TEXT_FILES, REQUIRED_SUBMISSION_TOKENS)
    proof_required_missing = missing_required(SUBMISSION_TEXT_FILES, REQUIRED_PROOF_BOUNDARY_TOKENS)
    submission_forbidden_hits = positive_counts(submission_forbidden_scan)
    proof_forbidden_hits = positive_counts(proof_forbidden_scan)
    support_forbidden_hits = positive_counts(support_forbidden_scan)

    result = {
        "schema": "cmame-claim-hygiene-audit-v1",
        "status": (
            "pass"
            if not required_missing
            and not proof_required_missing
            and not submission_forbidden_hits
            and not proof_forbidden_hits
            and not support_forbidden_hits
            else "open"
        ),
        "audit_mode": "read_only_text_scan_existing_artifacts",
        "submission_ready": False,
        "external_superiority_claim": False,
        "source_policy_superiority_claim_allowed": False,
        "default_1e_4_required": False,
        "run_v047_invoked": False,
        "heavy_numerical_run_invoked": False,
        "scope": {
            "submission_text_files": SUBMISSION_TEXT_FILES,
            "support_text_files": SUPPORT_TEXT_FILES,
            "required_submission_tokens": REQUIRED_SUBMISSION_TOKENS,
            "required_proof_boundary_tokens": REQUIRED_PROOF_BOUNDARY_TOKENS,
            "forbidden_submission_tokens": FORBIDDEN_SUBMISSION_TOKENS,
            "forbidden_proof_overclaim_tokens": FORBIDDEN_PROOF_OVERCLAIM_TOKENS,
            "forbidden_support_tokens": FORBIDDEN_SUPPORT_TOKENS,
        },
        "checks": {
            "required_missing_count": len(required_missing),
            "proof_required_missing_count": len(proof_required_missing),
            "submission_forbidden_hit_count": len(submission_forbidden_hits),
            "proof_forbidden_hit_count": len(proof_forbidden_hits),
            "support_forbidden_hit_count": len(support_forbidden_hits),
            "required_missing": required_missing,
            "proof_required_missing": proof_required_missing,
            "submission_forbidden_hits": submission_forbidden_hits,
            "proof_forbidden_hits": proof_forbidden_hits,
            "support_forbidden_hits": support_forbidden_hits,
        },
        "claim_boundary": {
            "accepted_method": "Gauss6/FullVA",
            "accepted_method_order": 6,
            "comparator": "local paper-style m=3 Gauss-Lobatto TFE formula target",
            "comparator_expected_order": 5,
            "allowed_claim": "conditional_formal_order_comparison",
            "not_allowed": [
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
            ],
        },
    }

    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# CMAME Claim Hygiene Audit",
        "",
        f"Status: **{result['status'].upper()}**",
        "",
        "- Accepted method: `Gauss6/FullVA`.",
        "- Allowed claim: `conditional_formal_order_comparison`.",
        "- Source-policy superiority allowed: `False`.",
        "- External same-test superiority allowed: `False`.",
        "- Submission ready: `False`.",
        "- Default `1e-4` required: `False`.",
        "",
        "## Text-Scan Results",
        "",
        f"- Required-token missing count: `{len(required_missing)}`.",
        f"- Proof-boundary required-token missing count: `{len(proof_required_missing)}`.",
        f"- Submission forbidden-hit count: `{len(submission_forbidden_hits)}`.",
        f"- Proof-overclaim forbidden-hit count: `{len(proof_forbidden_hits)}`.",
        f"- Support forbidden-hit count: `{len(support_forbidden_hits)}`.",
        "",
        "## Claim Boundary",
        "",
        "The CMAME manuscript is allowed to state a conditional formal-order comparison: "
        "`Gauss6/FullVA` is the accepted sixth-order method path and the local "
        "`m=3` Gauss-Lobatto TFE formula target has expected order five. This audit "
        "does not authorize source-policy superiority, external same-test superiority, "
        "complete source-paper residual reproduction, independent full-TFE stage "
        "replacement, or a seventh-order theorem. It also guards the proof boundary: "
        "the manuscript may state the conditional order-six theorem only under its "
        "retained interfaces, and may not promote P6 solver-policy evidence, fixed "
        "production tolerances, P7 residual-to-error boundary, or source-policy/full-TFE "
        "package readiness into theorem inputs.",
    ]

    if required_missing:
        lines.extend(["", "## Missing Required Tokens", ""])
        for row in required_missing:
            lines.append(f"- `{row['file']}` missing `{row['token']}`")
    if submission_forbidden_hits:
        lines.extend(["", "## Submission Forbidden Hits", ""])
        for row in submission_forbidden_hits:
            lines.append(f"- `{row['file']}` has `{row['token']}` x `{row['count']}`")
    if proof_required_missing:
        lines.extend(["", "## Missing Proof-Boundary Tokens", ""])
        for row in proof_required_missing:
            lines.append(f"- `{row['file']}` missing `{row['token']}`")
    if proof_forbidden_hits:
        lines.extend(["", "## Proof-Overclaim Forbidden Hits", ""])
        for row in proof_forbidden_hits:
            lines.append(f"- `{row['file']}` has `{row['token']}` x `{row['count']}`")
    if support_forbidden_hits:
        lines.extend(["", "## Support Forbidden Hits", ""])
        for row in support_forbidden_hits:
            lines.append(f"- `{row['file']}` has `{row['token']}` x `{row['count']}`")

    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("cmame_claim_hygiene_audit=written")
    print(f"status={result['status']}")
    print(f"required_missing_count={len(required_missing)}")
    print(f"proof_required_missing_count={len(proof_required_missing)}")
    print(f"submission_forbidden_hit_count={len(submission_forbidden_hits)}")
    print(f"proof_forbidden_hit_count={len(proof_forbidden_hits)}")
    print(f"support_forbidden_hit_count={len(support_forbidden_hits)}")


if __name__ == "__main__":
    main()
