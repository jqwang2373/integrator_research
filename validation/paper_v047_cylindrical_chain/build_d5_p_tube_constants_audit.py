#!/usr/bin/env python3
"""Build the D5 P_tube compact-constants audit.

This audit closes only the compact proof-tube constant primitive used by the
D5 Taylor reductions. It does not prove any O(h^7) lift rate and does not close
PC2.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
from paper_paths import LATEX, package_path as manuscript_path
OUT_JSON = PAPER / "D5_P_TUBE_CONSTANTS_AUDIT.json"
OUT_MD = PAPER / "D5_P_TUBE_CONSTANTS_AUDIT.md"


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def contains_normalized(text: str, token: str) -> bool:
    return token in text or " ".join(token.split()) in " ".join(text.split())


def main() -> None:
    primitive_reduction = read_json(PAPER / "D5_PRIMITIVE_BOUND_REDUCTION_AUDIT.json")
    term_budget = read_json(PAPER / "D5_TAYLOR_TERM_BUDGET_AUDIT.json")
    smooth_force = read_json(PAPER / "SMOOTH_FORCE_LIFT_CERTIFICATE.json")
    proof_manifest = read_json(PAPER / "PROOF_CLOSURE_MANIFEST.json")
    main_tex = read_text(LATEX / "main_cmame.tex")
    flat_tex = read_text(LATEX / "cmame_submission_flat" / "main_cmame_submission.tex")

    primitive_rows = primitive_reduction.get("primitive_obligations", [])
    p_tube_row = next(
        (
            row
            for row in primitive_rows
            if isinstance(row, dict) and row.get("id") == "P_uniform_tube_constants"
        ),
        {},
    )
    manuscript_tokens = [
        "Compact proof-tube constants for D5",
        r"\label{lem:d5-compact-tube-constants}",
        r"P_{\mathrm{tube}}\) holds",
        "five lift and bilinear obligations remain open",
        "does not prove the state,",
    ]
    result = {
        "schema": "d5-p-tube-constants-audit-v1",
        "status": "p_tube_compact_constants_closed_pc2_open",
        "read_only": True,
        "run_v047_invoked": False,
        "submission_ready": False,
        "pc2_closed": False,
        "proof_gap_closed": False,
        "primitive_id": "P_uniform_tube_constants",
        "plan_id": "P_tube",
        "primitive_closed": True,
        "closure_mode": "closed_by_regular_compact_tube_lemma",
        "certifies_dynamic_row_defect": False,
        "certifies_induced_taylor_bounds": False,
        "remaining_primitive_obligations": [
            "P_state_lift",
            "P_acceleration_lift",
            "P_multiplier_lift",
            "P_geometry_lift",
            "P_gyroscopic_lift",
        ],
        "summary": {
            "primitive_obligation_count": 6,
            "primitive_obligations_closed": 1,
            "primitive_obligations_remaining": 5,
            "term_rows_using_p_tube": p_tube_row.get("term_rows_using_obligation"),
            "term_rows": primitive_reduction.get("summary", {}).get("term_rows"),
            "induced_taylor_bounds_proved": 0,
        },
        "manuscript_link": {
            "lemma_label": "lem:d5-compact-tube-constants",
            "main_tex_present": all(contains_normalized(main_tex, token) for token in manuscript_tokens),
            "flat_tex_present": all(contains_normalized(flat_tex, token) for token in manuscript_tokens),
            "tokens": manuscript_tokens,
        },
        "source_consistency": {
            "primitive_reduction_schema": primitive_reduction.get("schema"),
            "primitive_reduction_pc2_closed": primitive_reduction.get("pc2_closed"),
            "term_budget_schema": term_budget.get("schema"),
            "term_budget_pc2_closed": term_budget.get("pc2_closed"),
            "smooth_force_schema": smooth_force.get("schema"),
            "smooth_force_submission_ready": smooth_force.get("submission_ready"),
            "proof_manifest_proof_gap_closed": proof_manifest.get("closure_state", {}).get("proof_gap_closed"),
            "proof_manifest_direct_route_gap_closed": proof_manifest.get("closure_state", {}).get(
                "direct_pc2_proof_gap_closed"
            ),
            "proof_manifest_proof_gap_closed_scope": proof_manifest.get("closure_state", {}).get(
                "proof_gap_closed_scope"
            ),
        },
        "claim_boundary": {
            "allowed_now": "P_tube uniform compact-tube constants are closed for D5.",
            "forbidden_now": [
                "all primitive obligations closed",
                "Taylor term bounds certified",
                "O(h^7) dynamic-row defect proof",
                "primitive/Taylor PC2 route closure",
                "submission-ready proof",
            ],
            "close_condition": (
                "separate primitive-route certificate remains open until the five open primitive "
                "obligations are proved and every induced D5 Taylor term bound is certified."
            ),
        },
    }

    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# D5 P_tube Constants Audit",
        "",
        "Status: **P_tube compact constants closed; separate primitive-route certificate remains open**.",
        "",
        "This read-only audit records that the compact proof-tube constant",
        "primitive is supplied by the manuscript compactness lemma. It does not",
        "prove any lift-rate primitive and does not certify any D5 Taylor term",
        "bound by itself.",
        "",
        "## Summary",
        "",
        "- Primitive closed: `P_uniform_tube_constants`.",
        f"- Primitive obligations closed: `{result['summary']['primitive_obligations_closed']}/6`.",
        f"- Primitive obligations remaining: `{result['summary']['primitive_obligations_remaining']}/6`.",
        f"- Term rows using P_tube: `{result['summary']['term_rows_using_p_tube']}/162`.",
        f"- Induced Taylor bounds proved: `{result['summary']['induced_taylor_bounds_proved']}/162`.",
        f"- Primitive/Taylor PC2 route closed: `{result['pc2_closed']}`.",
        "",
        "## Remaining Primitive Obligations",
        "",
    ]
    for item in result["remaining_primitive_obligations"]:
        lines.append(f"- `{item}`")
    lines.extend(
        [
            "",
            "## Acceptance Boundary",
            "",
            "- P_tube is closed only as a compact-constant obligation.",
            "- Five lift and bilinear primitive obligations remain open.",
            "- Zero induced Taylor bounds are certified.",
            "- Primitive/Taylor PC2 lane remains open.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("d5_p_tube_constants_audit=written")
    print("primitive_obligations_closed=1/6")
    print("induced_taylor_bounds_proved=0/162")
    print("pc2_closed=False")


if __name__ == "__main__":
    main()
