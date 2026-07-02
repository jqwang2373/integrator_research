#!/usr/bin/env python3
"""Build a Brown--McPhee source-code-equivalence certificate for TFE."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
OUT_JSON = PAPER / "TFE_BROWN_MCPHEE_SOURCE_CODE_EQUIVALENCE_CERTIFICATE.json"
OUT_MD = PAPER / "TFE_BROWN_MCPHEE_SOURCE_CODE_EQUIVALENCE_CERTIFICATE.md"

SAFE_ACTIONS_WITHOUT_B4_OPT_IN = [
    {
        "action_id": "rebuild_read_only_audit_chain",
        "description": "Regenerate read-only audit/manifest/review artifacts from existing evidence.",
    },
    {
        "action_id": "rerun_read_only_validators",
        "description": "Run validators that inspect artifacts without launching numerical campaigns.",
    },
    {
        "action_id": "keep_narrowed_archive_provenance_only",
        "description": "Use the current archive only for narrowed-claim replay and provenance evidence.",
    },
    {
        "action_id": "monitor_reopen_conditions",
        "description": "Refresh read-only reopen-condition monitors for new local/public-code evidence.",
    },
]
SAFE_ACTION_IDS = [item["action_id"] for item in SAFE_ACTIONS_WITHOUT_B4_OPT_IN]
OPT_IN_ACTION_IDS = ["authorized_b4_ra_hi_source_policy_execution"]
REQUIRED_USER_APPROVAL_STATEMENT = (
    "I explicitly approve running the B4 source-policy execution commands listed in "
    "B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json."
)
BLOCKER_IDS = ["OC4", "OC6", "OC12"]
BLOCKER_OPEN_BY_ID = {"OC4": True, "OC6": True, "OC12": True}
BLOCKER_CLOSURE_DECISION_BY_ID = {
    "OC4": "remain_open_ready_for_authorized_execution_not_executed_not_promoted",
    "OC6": "remain_open_no_positive_source_equivalent_artifact",
    "OC12": "remain_partial_narrowed_replay_ready_full_source_policy_archive_not_ready",
}
BLOCKER_CLOSURE_ALLOWED_BY_ID = {"OC4": False, "OC6": False, "OC12": False}


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def blocker_token(values: dict[str, Any]) -> str:
    return ",".join(f"{blocker_id}:{values[blocker_id]}" for blocker_id in BLOCKER_IDS)


def main() -> None:
    boundary = read_json(PAPER / "TFE_BROWN_MCPHEE_SOURCE_LAW_BOUNDARY_AUDIT.json")
    row_audit = read_json(PAPER / "TFE_SOURCE_POLICY_ROW_AUDIT.json")
    spec = read_json(PAPER / "TFE_SOURCE_POLICY_SPEC.json")

    gap_rows = row_audit.get("source_policy_runner_equivalence_gap_matrix", {}).get(
        "open_blockers",
        [],
    )
    brown_gap = next(
        (row for row in gap_rows if row.get("id") == "brown_mcphee_source_code_equivalent_law_open"),
        {},
    )
    demotion = boundary.get("frictional_source_policy_row_demotion_contract", {})
    formula = boundary.get("formula_boundary", {})
    transition = boundary.get("brown_mcphee_transition_velocity_sensitivity", {})
    detail_sources = boundary.get("referenced_detail_sources", {})
    line_anchors = boundary.get("source_text_line_anchors", [])
    missing_items = list(formula.get("missing_for_source_policy_equivalence", []))
    required_to_promote = list(demotion.get("required_to_promote", []))

    output: dict[str, Any] = {
        "schema": "tfe-brown-mcphee-source-code-equivalence-certificate-v1",
        "status": "negative_source_code_equivalence_certificate_not_source_policy",
        "read_only": True,
        "heavy_numerical_run_invoked": False,
        "run_v047_invoked": False,
        "v048_runner_invoked": False,
        "b4_source_policy_execution_invoked": False,
        "source_policy_execution_invoked": False,
        "source_policy_execution_allowed_now": False,
        "exact_b4_opt_in_required_for_execution": True,
        "safe_actions_without_b4_opt_in": SAFE_ACTIONS_WITHOUT_B4_OPT_IN,
        "safe_action_ids": SAFE_ACTION_IDS,
        "opt_in_action_ids": OPT_IN_ACTION_IDS,
        "next_safe_actions": SAFE_ACTIONS_WITHOUT_B4_OPT_IN,
        "next_safe_action_ids": SAFE_ACTION_IDS,
        "required_user_approval_statement": REQUIRED_USER_APPROVAL_STATEMENT,
        "guarded_execution_driver": "run_b4_source_policy_after_opt_in.sh",
        "submission_ready": False,
        "external_superiority_claim_allowed": False,
        "can_close_now": False,
        "objective_blocker_matrix_status": "global_objective_blockers_remain_open",
        "blocker_open_by_id": BLOCKER_OPEN_BY_ID,
        "blocker_closure_decision_by_id": BLOCKER_CLOSURE_DECISION_BY_ID,
        "blocker_closure_allowed_by_id": BLOCKER_CLOSURE_ALLOWED_BY_ID,
        "certificate_available": True,
        "certificate_kind": "current_package_negative_equivalence_certificate",
        "positive_source_code_equivalence_certified": False,
        "brown_mcphee_source_code_equivalent_law": False,
        "brown_mcphee_transition_velocity_policy_resolved_from_source": False,
        "source_policy_rows_completed": 0,
        "source_policy_rows_promoted": 0,
        "nonheavy_contract_block_closed": False,
        "candidate_evidence_allowed_use": demotion.get("candidate_evidence_allowed_use"),
        "source_policy_friction_spec_boundary": boundary.get("source_policy_friction_spec_boundary", {}),
        "source_text_evidence": {
            "source_text_found": boundary.get("source_text_anchor", {}).get("source_text_found"),
            "names_velocity_based_continuous_model": boundary.get("source_text_anchor", {}).get(
                "names_velocity_based_continuous_model"
            ),
            "reports_mu_static_dynamic": boundary.get("source_text_anchor", {}).get(
                "reports_mu_static_dynamic"
            ),
            "defers_law_details_to_refs_38_39": boundary.get("source_text_anchor", {}).get(
                "defers_law_details_to_refs_38_39"
            ),
            "line_anchor_count": len(line_anchors),
            "line_anchors_found": sum(1 for row in line_anchors if row.get("found") is True),
        },
        "referenced_detail_sources": {
            "reference_38_local_full_text_or_source_code_present": detail_sources.get(
                "reference_38",
                {},
            ).get("local_full_text_or_source_code_present"),
            "reference_39_local_full_text_or_source_code_present": detail_sources.get(
                "reference_39",
                {},
            ).get("local_full_text_or_source_code_present"),
            "reference_38_boundary": detail_sources.get("reference_38", {}).get("boundary"),
            "reference_39_boundary": detail_sources.get("reference_39", {}).get("boundary"),
        },
        "local_surrogate_provenance": boundary.get("local_surrogate_provenance", {}),
        "formula_equivalence_gap": {
            "encoded_candidate_formula": formula.get("encoded_candidate_formula"),
            "missing_for_source_policy_equivalence": missing_items,
            "missing_item_count": len(missing_items),
            "required_to_promote": required_to_promote,
            "required_to_promote_count": len(required_to_promote),
        },
        "transition_velocity_sensitivity": {
            "status": transition.get("status"),
            "endpoint_delta_row_count": transition.get("endpoint_delta_row_count"),
            "contract_row_count": transition.get("contract_row_count"),
            "source_policy_rows_completed": transition.get("source_policy_rows_completed"),
            "all_contract_equivalence_flags_false": transition.get(
                "all_contract_equivalence_flags_false"
            ),
            "missing_transition_velocity_is_numerically_material": transition.get(
                "missing_transition_velocity_is_numerically_material"
            ),
            "max_endpoint_coordinate_delta_vs_baseline": transition.get(
                "max_endpoint_coordinate_delta_vs_baseline"
            ),
            "max_endpoint_velocity_delta_vs_baseline": transition.get(
                "max_endpoint_velocity_delta_vs_baseline"
            ),
        },
        "candidate_frictional_dae_trajectory_contract": {
            "row_count": boundary.get("candidate_frictional_dae_trajectory_contract", {}).get(
                "row_count"
            ),
            "step_residual_row_count": boundary.get(
                "candidate_frictional_dae_trajectory_contract",
                {},
            ).get("step_residual_row_count"),
            "source_policy_rows_completed": boundary.get(
                "candidate_frictional_dae_trajectory_contract",
                {},
            ).get("source_policy_rows_completed"),
            "source_policy_dae_runner_equivalent": boundary.get(
                "candidate_frictional_dae_trajectory_contract",
                {},
            ).get("source_policy_dae_runner_equivalent"),
            "source_policy_method_runner_equivalent": boundary.get(
                "candidate_frictional_dae_trajectory_contract",
                {},
            ).get("source_policy_method_runner_equivalent"),
            "brown_mcphee_source_code_equivalent_law": boundary.get(
                "candidate_frictional_dae_trajectory_contract",
                {},
            ).get("brown_mcphee_source_code_equivalent_law"),
            "monolithic_absolute_coordinate_dae_time_integrator": boundary.get(
                "candidate_frictional_dae_trajectory_contract",
                {},
            ).get("monolithic_absolute_coordinate_dae_time_integrator"),
        },
        "row_audit_gap_status": {
            "gap_id": brown_gap.get("id"),
            "gap_status": brown_gap.get("status"),
            "first_required_artifact": brown_gap.get("first_required_artifact"),
            "can_resolve_without_heavy_run": brown_gap.get("can_resolve_without_heavy_run"),
        },
        "closure_decision": {
            "can_certify_source_code_equivalent_law_now": False,
            "can_close_brown_mcphee_source_code_equivalent_law_now": False,
            "can_promote_frictional_tfe_source_policy_rows_now": False,
            "reason": (
                "The current package proves only a Brown--McPhee-family surrogate: the source text "
                "reports mu_s/mu_d and names the model family, but the transition velocity, "
                "normal-load coupling, damping/default policy, and implementation-level source code "
                "binding remain unavailable. This certificate therefore records a negative "
                "source-code-equivalence decision."
            ),
        },
        "source_files": {
            "source_policy_spec": "TFE_SOURCE_POLICY_SPEC.json",
            "source_policy_friction_spec_status": spec.get("source_policy", {}).get(
                "friction_parameters",
                {},
            ).get("law_details_available_in_source_paper"),
            "brown_mcphee_source_law_boundary": "TFE_BROWN_MCPHEE_SOURCE_LAW_BOUNDARY_AUDIT.json",
            "source_policy_row_audit": "TFE_SOURCE_POLICY_ROW_AUDIT.json",
        },
    }

    with OUT_JSON.open("w", encoding="utf-8") as handle:
        json.dump(output, handle, indent=2, sort_keys=True)
        handle.write("\n")

    lines = [
        "# TFE Brown--McPhee Source-Code Equivalence Certificate",
        "",
        "Status: **negative source-code equivalence certificate; not source policy**.",
        "",
        "## Objective Blocker Matrix",
        "",
        "This certificate records a negative OC6 source-equivalence sub-decision. It does not close the global objective blockers.",
        "",
        f"- `blocker_open_by_id={blocker_token(output['blocker_open_by_id'])}`",
        f"- `blocker_closure_decision_by_id={blocker_token(output['blocker_closure_decision_by_id'])}`",
        f"- `blocker_closure_allowed_by_id={blocker_token(output['blocker_closure_allowed_by_id'])}`",
        "",
        f"- Certificate available: `{output['certificate_available']}`.",
        f"- Positive source-code equivalence certified: `{output['positive_source_code_equivalence_certified']}`.",
        f"- Brown--McPhee source-code-equivalent law: `{output['brown_mcphee_source_code_equivalent_law']}`.",
        f"- Transition velocity resolved from source: `{output['brown_mcphee_transition_velocity_policy_resolved_from_source']}`.",
        f"- Source-policy rows completed/promoted: `{output['source_policy_rows_completed']}/{output['source_policy_rows_promoted']}`.",
        f"- Source-policy execution invoked / can close now: `{output['source_policy_execution_invoked']}/{output['can_close_now']}`.",
        f"- Source-policy execution allowed now/invoked/exact opt-in required: `{output['source_policy_execution_allowed_now']}/{output['source_policy_execution_invoked']}/{output['exact_b4_opt_in_required_for_execution']}`.",
        f"- Safe action ids: `{','.join(output['safe_action_ids'])}`.",
        f"- Opt-in action ids: `{','.join(output['opt_in_action_ids'])}`.",
        f"- Non-heavy contract block closed: `{output['nonheavy_contract_block_closed']}`.",
        (
            "- Source text anchors found/total: "
            f"`{output['source_text_evidence']['line_anchors_found']}/"
            f"{output['source_text_evidence']['line_anchor_count']}`."
        ),
        (
            "- Reference 38/39 local full text or source code present: "
            f"`{output['referenced_detail_sources']['reference_38_local_full_text_or_source_code_present']}/"
            f"{output['referenced_detail_sources']['reference_39_local_full_text_or_source_code_present']}`."
        ),
        (
            "- Formula missing items / promotion requirements: "
            f"`{output['formula_equivalence_gap']['missing_item_count']}/"
            f"{output['formula_equivalence_gap']['required_to_promote_count']}`."
        ),
        (
            "- Transition sensitivity rows/contracts/source rows/material/equivalence-false: "
            f"`{output['transition_velocity_sensitivity']['endpoint_delta_row_count']}/"
            f"{output['transition_velocity_sensitivity']['contract_row_count']}/"
            f"{output['transition_velocity_sensitivity']['source_policy_rows_completed']}/"
            f"{output['transition_velocity_sensitivity']['missing_transition_velocity_is_numerically_material']}/"
            f"{output['transition_velocity_sensitivity']['all_contract_equivalence_flags_false']}`."
        ),
        (
            "- Candidate frictional DAE contract rows/step residual rows/source rows/equivalent DAE/method/source-law/monolithic: "
            f"`{output['candidate_frictional_dae_trajectory_contract']['row_count']}/"
            f"{output['candidate_frictional_dae_trajectory_contract']['step_residual_row_count']}/"
            f"{output['candidate_frictional_dae_trajectory_contract']['source_policy_rows_completed']}/"
            f"{output['candidate_frictional_dae_trajectory_contract']['source_policy_dae_runner_equivalent']}/"
            f"{output['candidate_frictional_dae_trajectory_contract']['source_policy_method_runner_equivalent']}/"
            f"{output['candidate_frictional_dae_trajectory_contract']['brown_mcphee_source_code_equivalent_law']}/"
            f"{output['candidate_frictional_dae_trajectory_contract']['monolithic_absolute_coordinate_dae_time_integrator']}`."
        ),
        (
            "- Row-audit gap status/can-resolve-without-heavy-run: "
            f"`{output['row_audit_gap_status']['gap_status']}/"
            f"{output['row_audit_gap_status']['can_resolve_without_heavy_run']}`."
        ),
        "",
        "## Decision",
        "",
        output["closure_decision"]["reason"],
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("tfe_brown_mcphee_source_code_equivalence_certificate=written")
    print(f"status={output['status']}")
    print("brown_mcphee_source_code_equivalent_law=False")
    print("source_policy_rows_completed=0")
    print("source_policy_execution_invoked=False")
    print("source_policy_execution_allowed_now=False")
    print("can_close_now=False")


if __name__ == "__main__":
    main()
