#!/usr/bin/env python3
"""Validate the TFE Brown--McPhee source-code-equivalence certificate."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
EXPECTED_SAFE_ACTION_IDS = [
    "rebuild_read_only_audit_chain",
    "rerun_read_only_validators",
    "keep_narrowed_archive_provenance_only",
    "monitor_reopen_conditions",
]
EXPECTED_OPT_IN_ACTION_IDS = ["authorized_b4_ra_hi_source_policy_execution"]
EXPECTED_APPROVAL_STATEMENT = (
    "I explicitly approve running the B4 source-policy execution commands listed in "
    "B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json."
)
EXPECTED_BLOCKER_OPEN_BY_ID = {"OC4": True, "OC6": True, "OC12": True}
EXPECTED_BLOCKER_CLOSURE_DECISION_BY_ID = {
    "OC4": "remain_open_ready_for_authorized_execution_not_executed_not_promoted",
    "OC6": "remain_open_no_positive_source_equivalent_artifact",
    "OC12": "remain_partial_narrowed_replay_ready_full_source_policy_archive_not_ready",
}
EXPECTED_BLOCKER_CLOSURE_ALLOWED_BY_ID = {"OC4": False, "OC6": False, "OC12": False}
EXPECTED_BLOCKER_OPEN_TOKEN = "blocker_open_by_id=OC4:True,OC6:True,OC12:True"
EXPECTED_BLOCKER_CLOSURE_DECISION_TOKEN = (
    "blocker_closure_decision_by_id="
    "OC4:remain_open_ready_for_authorized_execution_not_executed_not_promoted,"
    "OC6:remain_open_no_positive_source_equivalent_artifact,"
    "OC12:remain_partial_narrowed_replay_ready_full_source_policy_archive_not_ready"
)
EXPECTED_BLOCKER_CLOSURE_ALLOWED_TOKEN = (
    "blocker_closure_allowed_by_id=OC4:False,OC6:False,OC12:False"
)


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


def main() -> int:
    checks = Checks()
    try:
        cert = read_json(PAPER / "TFE_BROWN_MCPHEE_SOURCE_CODE_EQUIVALENCE_CERTIFICATE.json")
        cert_md = read_text(PAPER / "TFE_BROWN_MCPHEE_SOURCE_CODE_EQUIVALENCE_CERTIFICATE.md")
        boundary = read_json(PAPER / "TFE_BROWN_MCPHEE_SOURCE_LAW_BOUNDARY_AUDIT.json")
        row_audit = read_json(PAPER / "TFE_SOURCE_POLICY_ROW_AUDIT.json")
    except Exception as exc:  # noqa: BLE001
        print(f"TFE Brown-McPhee source-code-equivalence certificate validation: FAIL\n- {exc}")
        return 1

    source_text = cert.get("source_text_evidence", {})
    detail_sources = cert.get("referenced_detail_sources", {})
    formula_gap = cert.get("formula_equivalence_gap", {})
    transition = cert.get("transition_velocity_sensitivity", {})
    candidate_contract = cert.get("candidate_frictional_dae_trajectory_contract", {})
    row_gap = cert.get("row_audit_gap_status", {})
    closure = cert.get("closure_decision", {})
    boundary_transition = boundary.get("brown_mcphee_transition_velocity_sensitivity", {})
    boundary_contract = boundary.get("candidate_frictional_dae_trajectory_contract", {})
    row_gap_ids = {
        row.get("id")
        for row in row_audit.get("source_policy_runner_equivalence_gap_matrix", {}).get(
            "open_blockers",
            [],
        )
    }

    checks.check(
        cert.get("schema") == "tfe-brown-mcphee-source-code-equivalence-certificate-v1",
        "schema changed",
    )
    checks.check(
        cert.get("status") == "negative_source_code_equivalence_certificate_not_source_policy",
        "status changed",
    )
    checks.check(cert.get("read_only") is True, "certificate must remain read-only")
    checks.check(cert.get("heavy_numerical_run_invoked") is False, "certificate invoked heavy run")
    checks.check(cert.get("run_v047_invoked") is False, "certificate invoked run_v047")
    checks.check(cert.get("v048_runner_invoked") is False, "certificate invoked v048 runner")
    checks.check(
        cert.get("b4_source_policy_execution_invoked") is False,
        "certificate invoked B4 source-policy execution",
    )
    checks.check(
        cert.get("source_policy_execution_invoked") is False,
        "certificate invoked source-policy execution",
    )
    checks.check(cert.get("source_policy_execution_allowed_now") is False, "certificate allowed source-policy execution")
    checks.check(
        cert.get("exact_b4_opt_in_required_for_execution") is True,
        "certificate lost exact opt-in requirement",
    )
    checks.check(cert.get("safe_action_ids") == EXPECTED_SAFE_ACTION_IDS, "safe action ids changed")
    checks.check(cert.get("next_safe_action_ids") == EXPECTED_SAFE_ACTION_IDS, "next safe action ids changed")
    checks.check(cert.get("opt_in_action_ids") == EXPECTED_OPT_IN_ACTION_IDS, "opt-in action ids changed")
    checks.check(
        cert.get("required_user_approval_statement") == EXPECTED_APPROVAL_STATEMENT,
        "approval statement changed",
    )
    checks.check(
        cert.get("guarded_execution_driver") == "run_b4_source_policy_after_opt_in.sh",
        "guarded driver changed",
    )
    checks.check(cert.get("submission_ready") is False, "certificate overclaims submission readiness")
    checks.check(
        cert.get("external_superiority_claim_allowed") is False,
        "certificate overclaims external superiority",
    )
    checks.check(cert.get("can_close_now") is False, "certificate overclaims closure readiness")
    checks.check(
        cert.get("objective_blocker_matrix_status") == "global_objective_blockers_remain_open",
        "objective blocker matrix status changed",
    )
    checks.check(
        cert.get("blocker_open_by_id") == EXPECTED_BLOCKER_OPEN_BY_ID,
        "objective blocker open map changed",
    )
    checks.check(
        cert.get("blocker_closure_decision_by_id") == EXPECTED_BLOCKER_CLOSURE_DECISION_BY_ID,
        "objective blocker closure-decision map changed",
    )
    checks.check(
        cert.get("blocker_closure_allowed_by_id") == EXPECTED_BLOCKER_CLOSURE_ALLOWED_BY_ID,
        "objective blocker closure-allowed map changed",
    )
    checks.check(cert.get("certificate_available") is True, "certificate availability marker missing")
    checks.check(
        cert.get("certificate_kind") == "current_package_negative_equivalence_certificate",
        "certificate kind changed",
    )
    checks.check(
        cert.get("positive_source_code_equivalence_certified") is False,
        "certificate overclaims positive equivalence",
    )
    checks.check(
        cert.get("brown_mcphee_source_code_equivalent_law")
        == boundary.get("brown_mcphee_source_code_equivalent_law")
        is False,
        "source-code-equivalent law overclaimed",
    )
    checks.check(
        cert.get("brown_mcphee_transition_velocity_policy_resolved_from_source")
        == boundary.get("brown_mcphee_transition_velocity_policy_resolved_from_source")
        is False,
        "transition velocity source policy overclaimed",
    )
    checks.check(cert.get("source_policy_rows_completed") == 0, "certificate completed source-policy rows")
    checks.check(cert.get("source_policy_rows_promoted") == 0, "certificate promoted source-policy rows")
    checks.check(cert.get("nonheavy_contract_block_closed") is False, "certificate closed non-heavy block")
    checks.check(
        cert.get("candidate_evidence_allowed_use")
        == "local_dissipativity_residual_sensitivity_diagnostic_only",
        "candidate allowed-use boundary changed",
    )

    checks.check(source_text.get("source_text_found") is True, "source text marker missing")
    checks.check(
        source_text.get("names_velocity_based_continuous_model") is True,
        "model-family source text marker missing",
    )
    checks.check(source_text.get("reports_mu_static_dynamic") is True, "mu_s/mu_d marker missing")
    checks.check(
        source_text.get("defers_law_details_to_refs_38_39") is True,
        "detail-source deferral marker missing",
    )
    checks.check(source_text.get("line_anchor_count") == 6, "line anchor count changed")
    checks.check(source_text.get("line_anchors_found") == 6, "not all source text anchors were found")
    checks.check(
        detail_sources.get("reference_38_local_full_text_or_source_code_present") is False
        and detail_sources.get("reference_39_local_full_text_or_source_code_present") is False,
        "reference detail source availability changed",
    )
    checks.check(
        "bibliographic pointer only" in str(detail_sources.get("reference_38_boundary"))
        and "bibliographic pointer only" in str(detail_sources.get("reference_39_boundary")),
        "detail-source boundary wording changed",
    )
    checks.check(
        formula_gap.get("missing_item_count") >= 6,
        "formula equivalence gap is unexpectedly short",
    )
    checks.check(
        any(
            "transition/Stribeck velocity" in item
            for item in formula_gap.get("missing_for_source_policy_equivalence", [])
        ),
        "formula equivalence gap lost transition velocity",
    )
    checks.check(
        any(
            "normal-load coupling" in item
            for item in formula_gap.get("missing_for_source_policy_equivalence", [])
        ),
        "formula equivalence gap lost normal-load coupling",
    )
    checks.check(
        formula_gap.get("required_to_promote_count") == 5,
        "promotion requirement count changed",
    )
    checks.check(
        any("transition/Stribeck velocity" in item for item in formula_gap.get("required_to_promote", [])),
        "promotion requirements lost transition velocity",
    )
    checks.check(
        transition.get("status") == boundary_transition.get("status"),
        "transition sensitivity status drifted",
    )
    checks.check(
        transition.get("endpoint_delta_row_count")
        == boundary_transition.get("endpoint_delta_row_count")
        == 3,
        "transition sensitivity endpoint row count changed",
    )
    checks.check(
        transition.get("contract_row_count") == boundary_transition.get("contract_row_count") == 36,
        "transition sensitivity contract row count changed",
    )
    checks.check(
        transition.get("source_policy_rows_completed") == 0,
        "transition sensitivity overclosed source-policy rows",
    )
    checks.check(
        transition.get("missing_transition_velocity_is_numerically_material") is True,
        "transition velocity materiality marker changed",
    )
    checks.check(
        transition.get("all_contract_equivalence_flags_false") is True,
        "transition sensitivity equivalence flags changed",
    )
    checks.check(
        candidate_contract.get("row_count") == boundary_contract.get("row_count") == 12,
        "candidate frictional DAE contract row count changed",
    )
    checks.check(
        candidate_contract.get("step_residual_row_count")
        == boundary_contract.get("step_residual_row_count")
        == 56,
        "candidate frictional DAE contract step residual count changed",
    )
    checks.check(
        candidate_contract.get("source_policy_rows_completed") == 0,
        "candidate frictional DAE contract overclosed rows",
    )
    checks.check(
        candidate_contract.get("source_policy_dae_runner_equivalent") is False
        and candidate_contract.get("source_policy_method_runner_equivalent") is False
        and candidate_contract.get("brown_mcphee_source_code_equivalent_law") is False
        and candidate_contract.get("monolithic_absolute_coordinate_dae_time_integrator") is False,
        "candidate frictional DAE contract overclaims equivalence",
    )
    checks.check(
        row_gap.get("gap_id") == "brown_mcphee_source_code_equivalent_law_open",
        "row gap id changed",
    )
    checks.check(row_gap.get("gap_status") == "open", "row gap unexpectedly closed")
    checks.check(row_gap.get("can_resolve_without_heavy_run") is True, "non-heavy flag changed")
    checks.check(
        "brown_mcphee_source_code_equivalent_law_open" in row_gap_ids,
        "row audit no longer carries Brown-McPhee open blocker",
    )
    checks.check(
        closure.get("can_certify_source_code_equivalent_law_now") is False
        and closure.get("can_close_brown_mcphee_source_code_equivalent_law_now") is False
        and closure.get("can_promote_frictional_tfe_source_policy_rows_now") is False,
        "closure decision overclaims Brown-McPhee source policy",
    )

    for token in [
        "Status: **negative source-code equivalence certificate; not source policy**.",
        "## Objective Blocker Matrix",
        "This certificate records a negative OC6 source-equivalence sub-decision. It does not close the global objective blockers.",
        f"`{EXPECTED_BLOCKER_OPEN_TOKEN}`",
        f"`{EXPECTED_BLOCKER_CLOSURE_DECISION_TOKEN}`",
        f"`{EXPECTED_BLOCKER_CLOSURE_ALLOWED_TOKEN}`",
        "Certificate available: `True`.",
        "Positive source-code equivalence certified: `False`.",
        "Brown--McPhee source-code-equivalent law: `False`.",
        "Transition velocity resolved from source: `False`.",
        "Source-policy rows completed/promoted: `0/0`.",
        "Source-policy execution invoked / can close now: `False/False`.",
        "Source-policy execution allowed now/invoked/exact opt-in required: `False/False/True`.",
        "Safe action ids: `rebuild_read_only_audit_chain,rerun_read_only_validators,keep_narrowed_archive_provenance_only,monitor_reopen_conditions`.",
        "Opt-in action ids: `authorized_b4_ra_hi_source_policy_execution`.",
        "Non-heavy contract block closed: `False`.",
        "Source text anchors found/total: `6/6`.",
        "Reference 38/39 local full text or source code present: `False/False`.",
        "Formula missing items / promotion requirements:",
        "Transition sensitivity rows/contracts/source rows/material/equivalence-false: `3/36/0/True/True`.",
        "Candidate frictional DAE contract rows/step residual rows/source rows/equivalent DAE/method/source-law/monolithic: `12/56/0/False/False/False/False`.",
        "Row-audit gap status/can-resolve-without-heavy-run: `open/True`.",
    ]:
        checks.check(token in cert_md, f"markdown missing token: {token}")

    if checks.errors:
        print("TFE Brown-McPhee source-code-equivalence certificate validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("TFE Brown-McPhee source-code-equivalence certificate validation: PASS")
    print("status=negative_source_code_equivalence_certificate_not_source_policy")
    print("brown_mcphee_source_code_equivalent_law=False")
    print("source_policy_rows_completed=0")
    print("source_policy_execution_invoked=False")
    print("source_policy_execution_allowed_now=False")
    print("can_close_now=False")
    print(EXPECTED_BLOCKER_OPEN_TOKEN)
    print(EXPECTED_BLOCKER_CLOSURE_DECISION_TOKEN)
    print(EXPECTED_BLOCKER_CLOSURE_ALLOWED_TOKEN)
    return 0


if __name__ == "__main__":
    sys.exit(main())
