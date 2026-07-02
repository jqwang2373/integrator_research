#!/usr/bin/env python3
"""Build the D5 P_state anti-circularity audit.

This audit closes only PS4 for P_state: the future local inverse/lift route is
kept independent of the D5 dynamic residual defect and of Lemma
stage-residual-defect. It does not prove the inverse bound, the state lift
rate, or PC2.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
OUT_JSON = PAPER / "D5_P_STATE_ANTICIRCULARITY_AUDIT.json"
OUT_MD = PAPER / "D5_P_STATE_ANTICIRCULARITY_AUDIT.md"


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
    kinematic_certificate = read_json(PAPER / "KINEMATIC_ROW_DEFECT_CERTIFICATE.json")
    p_state_map_definition = read_json(PAPER / "D5_P_STATE_MAP_DEFINITION_AUDIT.json")
    proof_manifest = read_json(PAPER / "PROOF_CLOSURE_MANIFEST.json")
    dynamic_readiness = read_json(PAPER / "D5_DYNAMIC_DEFECT_READINESS_AUDIT.json")
    main_tex = read_text(PAPER / "main_cmame.tex")
    flat_tex = read_text(PAPER / "cmame_submission_flat" / "main_cmame_submission.tex")

    proof_scope = kinematic_certificate.get("proof_scope", {})
    forbidden_inputs = [
        {
            "id": "F1",
            "source": "Lemma stage-residual-defect",
            "disallowed_for_ps2_ps3": True,
            "reason": "Using the stage residual perturbation lemma would make the P_state lift depend on a later residual-defect theorem.",
        },
        {
            "id": "F2",
            "source": "D5 dynamic Newton-Euler residual defect",
            "disallowed_for_ps2_ps3": True,
            "reason": "The state lift is an input to D5 and cannot depend on the D5 conclusion.",
        },
        {
            "id": "F3",
            "source": "accepted Newton-solution closeness without inverse bound",
            "disallowed_for_ps2_ps3": True,
            "reason": "Residual smallness must be converted to variable smallness by an independent inverse or inf-sup estimate.",
        },
    ]
    allowed_inputs = [
        {
            "id": "A1",
            "source": "accepted 96-row non-dynamic residual certificate",
            "available": proof_scope.get("certified_row_count") == 96,
            "role": "supplies row residual magnitudes only; it does not by itself supply variable lift rates",
        },
        {
            "id": "A2",
            "source": "P_state non-dynamic map definition",
            "available": p_state_map_definition.get("ps1_map_definition_closed") is True,
            "role": "defines the stage map whose inverse/inf-sup constant must be proved in PS2",
        },
        {
            "id": "A3",
            "source": "compact proof tube and smooth chart constants",
            "available": True,
            "role": "bounds derivatives after PS2 establishes a uniform inverse neighborhood",
        },
    ]
    future_route = [
        {
            "id": "PS2",
            "statement": "Prove a local inverse or inf-sup bound for the non-dynamic stage map on the compact proof tube.",
            "allowed_inputs": ["A1", "A2", "A3"],
            "forbidden_inputs": ["F1", "F2", "F3"],
            "closed_now": False,
        },
        {
            "id": "PS3",
            "statement": "Convert the 96-row non-dynamic residual certificate into O(h^7) pose and velocity lift rates.",
            "allowed_inputs": ["A1", "A2", "A3", "PS2"],
            "forbidden_inputs": ["F1", "F2", "F3"],
            "closed_now": False,
        },
    ]
    manuscript_tokens = [
        r"P_{\mathrm{state}}",
        r"\mathcal N_h^{\mathrm{nd}}",
        "compact proof-tube smoothness constants",
        "residual identities alone are disallowed as inputs",
        r"Likewise Lemma~\ref{lem:stage-residual-defect}",
        "The D5 dynamic residual defect is disallowed as an input to",
    ]
    result = {
        "schema": "d5-p-state-anticircularity-audit-v1",
        "status": "p_state_ps4_anticircularity_closed_lift_open",
        "read_only": True,
        "run_v047_invoked": False,
        "submission_ready": False,
        "pc2_closed": False,
        "proof_gap_closed": False,
        "primitive_id": "P_state_lift",
        "plan_id": "P_state",
        "primitive_closed": False,
        "ps4_anticircularity_closed": True,
        "state_lift_rate_proved": False,
        "certifies_dynamic_row_defect": False,
        "certifies_induced_taylor_bounds": False,
        "forbidden_inputs": forbidden_inputs,
        "allowed_inputs": allowed_inputs,
        "future_route": future_route,
        "dependency_gate": {
            "all_forbidden_inputs_disallowed": all(item["disallowed_for_ps2_ps3"] for item in forbidden_inputs),
            "all_allowed_inputs_available": all(item["available"] for item in allowed_inputs),
            "uses_stage_residual_defect": False,
            "uses_d5_dynamic_residual_defect": False,
            "uses_unproved_newton_solution_closeness": False,
            "closes_only_ps4": True,
        },
        "summary": {
            "closed_p_state_subproofs_after_ps4": 2,
            "open_p_state_subproofs_after_ps4": 2,
            "ps1_map_definition_closed": p_state_map_definition.get("ps1_map_definition_closed"),
            "ps2_inverse_or_infsup_closed": False,
            "ps3_state_lift_conversion_closed": False,
            "ps4_anticircularity_closed": True,
            "term_rows_using_p_state": next(
                (
                    row.get("term_rows_using_obligation")
                    for row in primitive_reduction.get("primitive_obligations", [])
                    if isinstance(row, dict) and row.get("id") == "P_state_lift"
                ),
                None,
            ),
            "induced_taylor_bounds_proved": 0,
        },
        "manuscript_link": {
            "main_tex_present": all(contains_normalized(main_tex, token) for token in manuscript_tokens),
            "flat_tex_present": all(contains_normalized(flat_tex, token) for token in manuscript_tokens),
            "tokens": manuscript_tokens,
        },
        "source_consistency": {
            "primitive_reduction_schema": primitive_reduction.get("schema"),
            "primitive_reduction_pc2_closed": primitive_reduction.get("pc2_closed"),
            "kinematic_certificate_schema": kinematic_certificate.get("schema"),
            "kinematic_certificate_status": kinematic_certificate.get("status"),
            "kinematic_certificate_certified_rows": proof_scope.get("certified_row_count"),
            "kinematic_certificate_excluded_dynamic_rows": proof_scope.get("excluded_row_count"),
            "p_state_map_definition_schema": p_state_map_definition.get("schema"),
            "p_state_map_definition_closed": p_state_map_definition.get("ps1_map_definition_closed"),
            "p_state_map_definition_primitive_closed": p_state_map_definition.get("primitive_closed"),
            "dynamic_readiness_pc2_closed": dynamic_readiness.get("pc2_closed"),
            "proof_manifest_proof_gap_closed": proof_manifest.get("closure_state", {}).get("proof_gap_closed"),
            "proof_manifest_direct_route_gap_closed": proof_manifest.get("closure_state", {}).get(
                "direct_pc2_proof_gap_closed"
            ),
            "proof_manifest_proof_gap_closed_scope": proof_manifest.get("closure_state", {}).get(
                "proof_gap_closed_scope"
            ),
        },
        "claim_boundary": {
            "allowed_now": "P_state PS4 anti-circularity is closed: PS2/PS3 may use only non-dynamic residual/map/tube inputs.",
            "forbidden_now": [
                "P_state primitive closure",
                "PS2 inverse or inf-sup closure",
                "PS3 state lift O(h^7) conversion",
                "Taylor term bounds certified from P_state",
                "primitive/Taylor PC2 route closure",
                "submission-ready proof",
            ],
            "close_condition": (
                "P_state closes only after PS2 proves a uniform inverse or inf-sup "
                "bound and PS3 converts the 96-row residual certificate into O(h^7) "
                "pose, translational-velocity, and angular-velocity lift rates."
            ),
        },
    }

    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# D5 P_state Anti-Circularity Audit",
        "",
        "Status: **P_state PS4 anti-circularity closed; lift remains open**.",
        "",
        "This read-only audit closes only PS4 for `P_state`: the future",
        "inverse and state-lift route is explicitly independent of the D5",
        "dynamic residual defect and of Lemma `stage-residual-defect`.",
        "",
        "## Summary",
        "",
        f"- Closed P_state subproofs after PS4: `{result['summary']['closed_p_state_subproofs_after_ps4']}/4`.",
        f"- Open P_state subproofs after PS4: `{result['summary']['open_p_state_subproofs_after_ps4']}`.",
        f"- PS1 map definition closed: `{result['summary']['ps1_map_definition_closed']}`.",
        f"- PS2 inverse or inf-sup closed: `{result['summary']['ps2_inverse_or_infsup_closed']}`.",
        f"- PS3 state lift conversion closed: `{result['summary']['ps3_state_lift_conversion_closed']}`.",
        f"- PS4 anti-circularity closed: `{result['summary']['ps4_anticircularity_closed']}`.",
        f"- P_state primitive closed: `{result['primitive_closed']}`.",
        f"- Primitive/Taylor PC2 route closed: `{result['pc2_closed']}`.",
        "",
        "## Dependency Gate",
        "",
        "- PS2 and PS3 cannot use Lemma `stage-residual-defect`.",
        "- PS2 and PS3 cannot use the D5 dynamic Newton-Euler residual defect.",
        "- PS2 and PS3 cannot infer variable lift rates from residual identities alone.",
        "- The allowed inputs are the 96-row non-dynamic certificate, the P_state map definition, and compact proof-tube smoothness constants.",
        "",
        "## Remaining P_state Work",
        "",
        "| id | closed | remaining statement |",
        "|---|---:|---|",
    ]
    for item in future_route:
        lines.append(f"| `{item['id']}` | `{item['closed_now']}` | {item['statement']} |")
    lines.extend(
        [
            "",
            "## Acceptance Boundary",
            "",
            "- PS4 is closed.",
            "- PS2 and PS3 remain open.",
            "- `P_state` remains open.",
            "- Zero P_state-induced Taylor bounds are certified.",
            "- Primitive/Taylor PC2 lane remains open.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("d5_p_state_anticircularity_audit=written")
    print("ps4_anticircularity_closed=True")
    print("closed_p_state_subproofs_after_ps4=2/4")
    print("pc2_closed=False")


if __name__ == "__main__":
    main()
