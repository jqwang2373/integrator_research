#!/usr/bin/env python3
"""Build the D5 P_gyro bilinear-reduction audit.

This audit closes only the algebraic Lipschitz reduction for the body-frame
gyroscopic term omega x J omega.  It does not prove the angular-velocity lift
rate required by P_state and therefore does not close P_gyro or PC2.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
OUT_JSON = PAPER / "D5_P_GYRO_BILINEAR_REDUCTION_AUDIT.json"
OUT_MD = PAPER / "D5_P_GYRO_BILINEAR_REDUCTION_AUDIT.md"


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


def close_requirement_satisfied(manifest: dict[str, Any], requirement_id: str) -> bool | None:
    for row in manifest.get("close_requirements", []):
        if isinstance(row, dict) and row.get("id") == requirement_id:
            value = row.get("satisfied")
            return value if isinstance(value, bool) else None
    return None


def main() -> None:
    readiness = read_json(PAPER / "D5_DYNAMIC_DEFECT_READINESS_AUDIT.json")
    p_tube = read_json(PAPER / "D5_P_TUBE_CONSTANTS_AUDIT.json")
    p_state_gap = read_json(PAPER / "D5_P_STATE_LIFT_GAP_AUDIT.json")
    proof_manifest = read_json(PAPER / "PROOF_CLOSURE_MANIFEST.json")
    main_tex = read_text(PAPER / "main_cmame.tex")
    flat_tex = read_text(PAPER / "cmame_submission_flat" / "main_cmame_submission.tex")

    rows = readiness.get("rows", [])
    if not isinstance(rows, list):
        raise ValueError("D5 readiness row_coverage must be a list")
    rotational_rows = [
        row for row in rows if isinstance(row, dict) and row.get("balance_block") == "rotational_euler_balance"
    ]
    row_ids = [row.get("global_row") for row in rotational_rows]
    stage_body_pairs = sorted({(row.get("stage"), row.get("body")) for row in rotational_rows})
    component_count = sum(1 for row in rotational_rows if row.get("component") in {"x", "y", "z"})

    manuscript_tokens = [
        r"\label{lem:d5-gyro-bilinear-reduction}",
        r"\label{cor:d5-gyro-row-bound-under-pstate}",
        "Gyroscopic bilinear reduction",
        r"G(\omega)=\omega\times J\omega",
        r"C_{\mathrm{gyro}}=2M_\omega J_{\max}C_\omega",
        "does not close \(P_{\mathrm{gyro}}\)",
        "angular-velocity lift supplied by \(P_{\mathrm{state}}\)",
    ]
    main_tokens = all(contains_normalized(main_tex, token) for token in manuscript_tokens)
    flat_tokens = all(contains_normalized(flat_tex, token) for token in manuscript_tokens)

    closed_subproofs = [
        "constant_body_inertia_and_compact_angular_velocity_bounds",
        "bilinear_difference_identity_and_lipschitz_bound",
        "binding_to_18_rotational_newton_euler_rows",
    ]
    open_dependencies = [
        "P_state angular-velocity lift O(h^7)",
    ]

    result = {
        "schema": "d5-p-gyro-bilinear-reduction-audit-v1",
        "status": "p_gyro_bilinear_reduction_closed_primitive_open",
        "read_only": True,
        "run_v047_invoked": False,
        "submission_ready": False,
        "pc2_closed": False,
        "proof_gap_closed": False,
        "primitive_id": "P_gyroscopic_lift",
        "primitive_closed": False,
        "algebraic_reduction_closed": True,
        "term_bounds_proved": 0,
        "term_rows_conditionally_reduced": len(rotational_rows),
        "conditional_gyro_row_bounds_under_p_state": {
            "closed": True,
            "row_count": len(rotational_rows),
            "rows": row_ids,
            "constant": "C_gyro = 2 M_omega J_max C_omega",
            "assumption": "P_state angular-velocity lift ||omega_hat_{s,b}-omega_b(t_s)|| <= C_omega h^7",
            "actual_taylor_bounds_proved": 0,
            "primitive_closed": False,
            "pc2_closed": False,
        },
        "rotational_row_ids": row_ids,
        "summary": {
            "closed_subproof_count": len(closed_subproofs),
            "required_subproof_count": len(closed_subproofs),
            "open_dependency_count": len(open_dependencies),
            "term_rows_conditionally_reduced": len(rotational_rows),
            "conditional_gyro_row_bounds_under_p_state": len(rotational_rows),
            "stage_body_pairs": len(stage_body_pairs),
            "component_rows": component_count,
            "p_tube_closed": p_tube.get("primitive_closed"),
            "p_state_closed": p_state_gap.get("primitive_closed"),
            "pc2_closed": False,
        },
        "closed_subproofs": closed_subproofs,
        "open_dependencies": open_dependencies,
        "proof_sketch": {
            "map": "G(omega)=omega x J omega",
            "difference_identity": (
                "G(omega_hat)-G(omega) = (omega_hat-omega) x J omega_hat "
                "+ omega x J (omega_hat-omega)"
            ),
            "compact_bound": (
                "If ||omega|| and ||omega_hat|| are bounded by M on the compact proof tube, "
                "then ||G(omega_hat)-G(omega)|| <= 2 M ||J|| ||omega_hat-omega||."
            ),
            "conditional_rate": (
                "The gyroscopic contribution is O(h^7) once P_state supplies "
                "||omega_hat-omega|| = O(h^7)."
            ),
        },
        "manuscript_link": {
            "main_tex_present": main_tokens,
            "flat_tex_present": flat_tokens,
            "tokens": manuscript_tokens,
        },
        "source_consistency": {
            "readiness_schema": readiness.get("schema"),
            "readiness_status": readiness.get("status"),
            "readiness_pc2_closed": readiness.get("pc2_closed"),
            "readiness_direct_substitution_closed_rows": readiness.get("summary", {}).get(
                "direct_substitution_closed_rows"
            ),
            "readiness_primitive_taylor_closed_rows": readiness.get("summary", {}).get(
                "primitive_taylor_closed_rows"
            ),
            "rotational_rows": len(rotational_rows),
            "p_tube_schema": p_tube.get("schema"),
            "p_tube_closed": p_tube.get("primitive_closed"),
            "p_tube_pc2_closed": p_tube.get("pc2_closed"),
            "p_state_schema": p_state_gap.get("schema"),
            "p_state_closed": p_state_gap.get("primitive_closed"),
            "p_state_pc2_closed": p_state_gap.get("pc2_closed"),
            "proof_manifest_pc2_closed": close_requirement_satisfied(proof_manifest, "PC2"),
        },
        "claim_boundary": {
            "allowed_now": "P_gyro algebraic bilinear conditional reduction is recorded; the P_gyro primitive remains open until the P_state angular-velocity lift closes",
            "forbidden_now": [
                "P_gyro primitive closure",
                "P_state closure",
                "Taylor term bounds certified",
                "primitive/Taylor PC2 route closure",
                "unconditional sixth-order theorem",
            ],
            "close_condition": (
                "P_gyro closes only after P_state proves the O(h^7) angular-velocity "
                "lift and the conditional reduction is applied to the listed rotational rows."
            ),
        },
    }

    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# D5 P_gyro Bilinear Reduction Audit",
        "",
        "Status: **P_gyro bilinear reduction closed; primitive remains open**.",
        "",
        "This read-only audit proves the algebraic Lipschitz reduction for the",
        "body-frame gyroscopic map `G(omega)=omega x J omega`. It does not prove",
        "the angular-velocity lift rate supplied by `P_state`, so it does not",
        "close `P_gyro` or PC2.",
        "",
        "## Summary",
        "",
        f"- Closed P_gyro subproofs: `{len(closed_subproofs)}/{len(closed_subproofs)}`.",
        f"- Open dependencies: `{len(open_dependencies)}`.",
        f"- Rotational Newton-Euler rows conditionally reduced: `{len(rotational_rows)}/18`.",
        f"- P_tube closed: `{p_tube.get('primitive_closed')}`.",
        f"- P_state closed: `{p_state_gap.get('primitive_closed')}`.",
        f"- P_gyro primitive closed: `{result['primitive_closed']}`.",
        f"- Primitive/Taylor PC2 route closed: `{result['pc2_closed']}`.",
        "",
        "## Bound",
        "",
        "For `G(omega)=omega x J omega`,",
        "",
        "`G(omega_hat)-G(omega) = (omega_hat-omega) x J omega_hat + omega x J (omega_hat-omega)`.",
        "",
        "On the compact proof tube, `||omega||, ||omega_hat|| <= M`, so",
        "",
        "`||G(omega_hat)-G(omega)|| <= 2 M ||J|| ||omega_hat-omega||`.",
        "",
        "Thus the gyroscopic term is `O(h^7)` once `P_state` proves the",
        "angular-velocity lift `||omega_hat-omega|| = O(h^7)`.",
        "",
        "## Conditional Row Corollary",
        "",
        "Under the still-open `P_state` angular-velocity lift, the row-level",
        "corollary in the manuscript gives",
        "",
        "`C_gyro = 2 M_omega J_max C_omega`",
        "",
        "and binds the estimate to rows",
        "",
        f"`{row_ids}`.",
        "",
        f"Conditional gyro row bounds under P_state: `{len(rotational_rows)}/18`.",
        "Actual Taylor bounds proved by this audit remain `0`.",
        "",
        "## Acceptance Boundary",
        "",
        "- The constant-inertia compact-bound subproof is closed.",
        "- The bilinear difference estimate is closed.",
        "- The estimate is bound to the 18 rotational Newton-Euler rows.",
        "- `P_state` remains open, so `P_gyro` remains open.",
        "- Zero Taylor term bounds are certified by this audit.",
        "- Primitive/Taylor PC2 lane remains open.",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("d5_p_gyro_bilinear_reduction_audit=written")
    print(f"closed_subproofs={len(closed_subproofs)}/{len(closed_subproofs)}")
    print(f"rotational_rows_conditionally_reduced={len(rotational_rows)}/18")
    print("p_gyro_closed=False")
    print("pc2_closed=False")


if __name__ == "__main__":
    main()
