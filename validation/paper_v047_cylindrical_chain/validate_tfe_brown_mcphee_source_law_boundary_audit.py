#!/usr/bin/env python3
"""Validate the TFE Brown--McPhee source-law boundary audit."""

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
        audit = read_json(PAPER / "TFE_BROWN_MCPHEE_SOURCE_LAW_BOUNDARY_AUDIT.json")
        audit_md = read_text(PAPER / "TFE_BROWN_MCPHEE_SOURCE_LAW_BOUNDARY_AUDIT.md")
        spec = read_json(PAPER / "TFE_SOURCE_POLICY_SPEC.json")
        model = read_json(PAPER / "TFE_SOURCE_PENDULUM_MODEL_AUDIT.json")
        row_audit = read_json(PAPER / "TFE_SOURCE_POLICY_ROW_AUDIT.json")
    except Exception as exc:  # noqa: BLE001
        print(f"TFE Brown-McPhee source-law boundary audit validation: FAIL\n- {exc}")
        return 1

    friction_spec = spec.get("source_policy", {}).get("friction_parameters", {})
    source_anchor = audit.get("source_text_anchor", {})
    formula_boundary = audit.get("formula_boundary", {})
    local_provenance = audit.get("local_surrogate_provenance", {})
    demotion_contract = audit.get("frictional_source_policy_row_demotion_contract", {})
    code_scan = audit.get("candidate_formula_code_scan", {})
    candidate_contract = audit.get("candidate_frictional_dae_trajectory_contract", {})
    transition_sensitivity = audit.get("brown_mcphee_transition_velocity_sensitivity", {})
    closure = audit.get("closure_decision", {})
    gap_status = audit.get("row_audit_gap_status", {})
    line_anchors = audit.get("source_text_line_anchors", [])
    detail_sources = audit.get("referenced_detail_sources", {})
    row_gap_matrix = row_audit.get("source_policy_runner_equivalence_gap_matrix", {})

    checks.check(
        audit.get("schema") == "tfe-brown-mcphee-source-law-boundary-audit-v1",
        "schema changed",
    )
    checks.check(
        audit.get("status") == "source_formula_structure_encoded_surrogate_not_source_code_equivalent",
        "status changed",
    )
    checks.check(audit.get("read_only") is True, "audit must be read-only")
    checks.check(audit.get("heavy_numerical_run_invoked") is False, "audit invoked heavy run")
    checks.check(audit.get("run_v047_invoked") is False, "audit invoked run_v047")
    checks.check(audit.get("v048_runner_invoked") is False, "audit invoked v048 runner")
    checks.check(audit.get("b4_source_policy_execution_invoked") is False, "audit invoked B4 source-policy execution")
    checks.check(audit.get("source_policy_execution_invoked") is False, "audit invoked source-policy execution")
    checks.check(audit.get("source_policy_execution_allowed_now") is False, "audit allowed source-policy execution")
    checks.check(
        audit.get("exact_b4_opt_in_required_for_execution") is True,
        "audit lost exact opt-in requirement",
    )
    checks.check(audit.get("safe_action_ids") == EXPECTED_SAFE_ACTION_IDS, "safe action ids changed")
    checks.check(audit.get("next_safe_action_ids") == EXPECTED_SAFE_ACTION_IDS, "next safe action ids changed")
    checks.check(audit.get("opt_in_action_ids") == EXPECTED_OPT_IN_ACTION_IDS, "opt-in action ids changed")
    checks.check(
        audit.get("required_user_approval_statement") == EXPECTED_APPROVAL_STATEMENT,
        "approval statement changed",
    )
    checks.check(
        audit.get("guarded_execution_driver") == "run_b4_source_policy_after_opt_in.sh",
        "guarded driver changed",
    )
    checks.check(audit.get("submission_ready") is False, "audit overclaims submission readiness")
    checks.check(audit.get("external_superiority_claim_allowed") is False, "audit overclaims superiority")
    checks.check(audit.get("source_policy_rows_completed") == 0, "audit completed source-policy rows")
    checks.check(audit.get("source_policy_rows_promoted") == 0, "audit promoted source-policy rows")
    checks.check(
        audit.get("frictional_source_policy_rows_demoted") is True,
        "audit lost frictional source-policy demotion marker",
    )
    checks.check(audit.get("nonheavy_contract_block_closed") is False, "audit closes non-heavy block")

    checks.check(
        audit.get("brown_mcphee_candidate_friction_law_encoded")
        == model.get("brown_mcphee_candidate_friction_law_encoded")
        is True,
        "candidate friction law encoding not carried from model audit",
    )
    checks.check(
        audit.get("brown_mcphee_published_formula_structure_encoded")
        == model.get("brown_mcphee_published_formula_structure_encoded")
        is True,
        "published formula structure marker changed",
    )
    checks.check(
        audit.get("brown_mcphee_source_code_equivalent_law")
        == model.get("brown_mcphee_source_code_equivalent_law")
        is False,
        "source-code-equivalent law overclaimed",
    )
    checks.check(
        audit.get("brown_mcphee_transition_velocity_policy_resolved_from_source")
        == model.get("brown_mcphee_transition_velocity_policy_resolved_from_source")
        is False,
        "transition velocity policy overclaimed",
    )

    checks.check(source_anchor.get("source_text_found") is True, "source text anchor missing")
    checks.check(
        source_anchor.get("names_velocity_based_continuous_model") is True,
        "source text Brown-McPhee model anchor missing",
    )
    checks.check(source_anchor.get("reports_mu_static_dynamic") is True, "source text mu_s/mu_d anchor missing")
    checks.check(
        source_anchor.get("defers_law_details_to_refs_38_39") is True,
        "source text deferral boundary missing",
    )
    checks.check(
        audit.get("source_policy_friction_spec_boundary", {}).get("law_details_available_in_source_paper")
        == friction_spec.get("law_details_available_in_source_paper")
        is False,
        "source paper law-details boundary changed",
    )
    checks.check(
        audit.get("source_policy_friction_spec_boundary", {}).get(
            "requires_reference_38_39_or_existing_source_code"
        )
        == friction_spec.get("requires_reference_38_39_or_existing_source_code")
        is True,
        "source code/reference requirement boundary changed",
    )

    checks.check(
        "tau = -R N" in str(formula_boundary.get("encoded_candidate_formula")),
        "encoded candidate formula missing torque form",
    )
    checks.check(
        len(formula_boundary.get("missing_for_source_policy_equivalence", [])) >= 6,
        "missing source-policy-equivalence list too short",
    )
    checks.check(
        any(
            "transition/Stribeck velocity" in item
            for item in formula_boundary.get("missing_for_source_policy_equivalence", [])
        ),
        "missing list does not mention transition/Stribeck velocity",
    )
    checks.check(
        all(code_scan.get(key) is True for key in [
            "candidate_function_present",
            "candidate_docstring_names_surrogate",
            "candidate_docstring_denies_source_policy_equivalence",
            "candidate_uses_tanh_coulomb_term",
            "candidate_uses_rational_stiction_term",
            "candidate_exposes_stribeck_velocity_parameter",
            "candidate_exposes_viscous_damping_parameter",
        ]),
        "candidate formula code scan changed",
    )
    checks.check(
        local_provenance.get("provenance_label")
        == "v022_revolute_brown_mcphee_surrogate_not_source_policy_equivalent",
        "local surrogate provenance label changed",
    )
    checks.check(local_provenance.get("v021_readme_present") is True, "v021 README missing")
    checks.check(local_provenance.get("v022_readme_present") is True, "v022 README missing")
    checks.check(local_provenance.get("v022_run_has_matching_candidate_function") is True, "v022 function missing")
    checks.check(
        local_provenance.get("v022_local_stribeck_velocity_cases") == [0.5, 0.05],
        "v022 local Stribeck velocity cases changed",
    )
    checks.check(
        local_provenance.get("accepted_source_policy_equivalence") is False,
        "local surrogate overclaims source-policy equivalence",
    )
    checks.check(
        demotion_contract.get("frictional_source_policy_rows_demoted") is True,
        "frictional source-policy row demotion contract missing",
    )
    checks.check(
        "Brown--McPhee source-code-equivalent law" in demotion_contract.get("demotion_scope", ""),
        "frictional demotion scope missing Brown-McPhee source-code-equivalent law",
    )
    checks.check(
        "transition/Stribeck velocity" in demotion_contract.get("demotion_reason", ""),
        "frictional demotion reason missing transition velocity",
    )
    checks.check(
        demotion_contract.get("candidate_evidence_allowed_use")
        == "local_dissipativity_residual_sensitivity_diagnostic_only",
        "candidate evidence allowed-use boundary changed",
    )
    checks.check(
        demotion_contract.get("source_policy_rows_completed") == 0
        and demotion_contract.get("source_policy_rows_promoted") == 0,
        "frictional demotion contract overcloses source-policy rows",
    )
    required_to_promote = demotion_contract.get("required_to_promote", [])
    checks.check(len(required_to_promote) == 5, "frictional demotion promotion requirement count changed")
    checks.check(
        any("transition/Stribeck velocity" in item for item in required_to_promote),
        "frictional demotion contract missing transition-velocity promotion requirement",
    )
    checks.check(
        any("normal-load" in item for item in required_to_promote),
        "frictional demotion contract missing normal-load promotion requirement",
    )
    checks.check(
        any("absolute-coordinate DAE" in item for item in required_to_promote),
        "frictional demotion contract missing DAE/method runner promotion requirement",
    )
    checks.check(
        candidate_contract.get("implemented")
        == model.get("candidate_frictional_dae_trajectory_contract_implemented")
        is True,
        "candidate-friction DAE trajectory contract implementation marker missing",
    )
    checks.check(
        candidate_contract.get("schema") == "tfe-candidate-frictional-dae-trajectory-contract-smoke-v1",
        "candidate-friction DAE trajectory contract schema changed",
    )
    checks.check(
        candidate_contract.get("runner_api") == "candidate_frictional_dae_trajectory_contract_smoke",
        "candidate-friction DAE trajectory contract runner API changed",
    )
    checks.check(
        candidate_contract.get("runner_scope")
        == "candidate_brown_mcphee_friction_bound_to_stepwise_absolute_dae_residuals_not_source_policy",
        "candidate-friction DAE trajectory contract scope changed",
    )
    checks.check(
        candidate_contract.get("accepted_use")
        == "candidate_frictional_dae_trajectory_contract_not_source_policy",
        "candidate-friction DAE trajectory contract accepted-use boundary changed",
    )
    checks.check(
        candidate_contract.get("row_count") == 12
        and model.get("candidate_frictional_dae_trajectory_contract_rows") == 12,
        "candidate-friction DAE trajectory row count changed",
    )
    checks.check(
        candidate_contract.get("step_residual_row_count") == 56
        and model.get("candidate_frictional_dae_trajectory_contract_step_residual_rows") == 56,
        "candidate-friction DAE trajectory step residual row count changed",
    )
    checks.check(candidate_contract.get("method_count") == 4, "candidate-friction method count changed")
    checks.check(
        candidate_contract.get("comparison_h") == [0.012, 0.006, 0.003],
        "candidate-friction comparison grid changed",
    )
    checks.check(candidate_contract.get("reference_h") == 0.0001, "candidate-friction reference h changed")
    checks.check(candidate_contract.get("t_final") == 0.024, "candidate-friction t_final changed")
    checks.check(candidate_contract.get("theta0") == 0.0, "candidate-friction theta0 changed")
    checks.check(candidate_contract.get("omega0") == 1.0, "candidate-friction omega0 changed")
    checks.check(candidate_contract.get("frictional") is True, "candidate-friction case is no longer frictional")
    checks.check(
        candidate_contract.get("all_rows_finite") is True
        and model.get("candidate_frictional_dae_trajectory_contract_all_rows_finite") is True,
        "candidate-friction finite-row evidence changed",
    )
    checks.check(
        candidate_contract.get("all_dae_residuals_below_1e_9") is True
        and model.get("candidate_frictional_dae_trajectory_contract_all_dae_residuals_below_1e_9")
        is True,
        "candidate-friction DAE residual evidence changed",
    )
    checks.check(
        candidate_contract.get("all_candidate_friction_power_nonpositive") is True
        and model.get("candidate_frictional_dae_trajectory_contract_all_friction_power_nonpositive")
        is True,
        "candidate-friction dissipativity evidence changed",
    )
    checks.check(
        candidate_contract.get("source_policy_rows_completed") == 0
        and model.get("candidate_frictional_dae_trajectory_contract_source_policy_rows_completed") == 0,
        "candidate-friction contract completed source-policy rows",
    )
    checks.check(
        candidate_contract.get("source_policy_dae_runner_equivalent") is False
        and model.get("candidate_frictional_dae_trajectory_contract_dae_runner_equivalent") is False,
        "candidate-friction contract overclaims DAE runner equivalence",
    )
    checks.check(
        candidate_contract.get("source_policy_method_runner_equivalent") is False
        and model.get("candidate_frictional_dae_trajectory_contract_method_runner_equivalent") is False,
        "candidate-friction contract overclaims method runner equivalence",
    )
    checks.check(
        candidate_contract.get("brown_mcphee_source_code_equivalent_law") is False
        and model.get(
            "candidate_frictional_dae_trajectory_contract_brown_mcphee_source_code_equivalent_law"
        )
        is False,
        "candidate-friction contract overclaims Brown-McPhee source-code equivalence",
    )
    checks.check(
        candidate_contract.get("monolithic_absolute_coordinate_dae_time_integrator") is False
        and model.get("candidate_frictional_dae_trajectory_contract_monolithic_integrator") is False,
        "candidate-friction contract overclaims monolithic DAE integration",
    )
    checks.check(
        transition_sensitivity.get("schema")
        == "tfe-brown-mcphee-transition-velocity-sensitivity-v1",
        "transition-velocity sensitivity schema changed",
    )
    checks.check(
        transition_sensitivity.get("status")
        == "candidate_transition_velocity_sensitivity_recorded_not_source_policy",
        "transition-velocity sensitivity status changed",
    )
    checks.check(
        transition_sensitivity.get("runner_scope")
        == "candidate_brown_mcphee_transition_velocity_sensitivity_not_source_policy",
        "transition-velocity sensitivity scope changed",
    )
    checks.check(
        transition_sensitivity.get("accepted_use")
        == "local_candidate_sensitivity_boundary_not_source_policy",
        "transition-velocity sensitivity accepted-use boundary changed",
    )
    checks.check(
        transition_sensitivity.get("tested_stribeck_velocities") == [0.05, 0.5, 1.0],
        "transition-velocity sensitivity tested velocities changed",
    )
    checks.check(
        transition_sensitivity.get("baseline_stribeck_velocity") == 0.5,
        "transition-velocity sensitivity baseline changed",
    )
    checks.check(transition_sensitivity.get("t_final") == 0.024, "transition sensitivity t_final changed")
    checks.check(transition_sensitivity.get("reference_h") == 0.0001, "transition sensitivity reference h changed")
    checks.check(transition_sensitivity.get("theta0") == 0.0, "transition sensitivity theta0 changed")
    checks.check(transition_sensitivity.get("omega0") == 1.0, "transition sensitivity omega0 changed")
    checks.check(transition_sensitivity.get("frictional") is True, "transition sensitivity is not frictional")
    checks.check(
        transition_sensitivity.get("endpoint_delta_row_count") == 3,
        "transition sensitivity endpoint row count changed",
    )
    checks.check(
        transition_sensitivity.get("contract_row_count") == 36
        and transition_sensitivity.get("step_residual_row_count") == 168,
        "transition sensitivity contract row counts changed",
    )
    checks.check(
        transition_sensitivity.get("all_contract_rows_finite") is True
        and transition_sensitivity.get("all_contract_dae_residuals_below_1e_9") is True
        and transition_sensitivity.get("all_contract_friction_power_nonpositive") is True,
        "transition sensitivity contract finite/residual/power evidence changed",
    )
    checks.check(
        transition_sensitivity.get("all_contract_source_policy_rows_completed_zero") is True
        and transition_sensitivity.get("source_policy_rows_completed") == 0
        and transition_sensitivity.get("source_policy_rows_promoted") == 0,
        "transition sensitivity overcloses source-policy rows",
    )
    checks.check(
        transition_sensitivity.get("all_contract_equivalence_flags_false") is True
        and transition_sensitivity.get("source_policy_dae_runner_equivalent") is False
        and transition_sensitivity.get("source_policy_method_runner_equivalent") is False
        and transition_sensitivity.get("brown_mcphee_source_code_equivalent_law") is False,
        "transition sensitivity overclaims source-policy equivalence",
    )
    checks.check(
        transition_sensitivity.get("missing_transition_velocity_is_numerically_material") is True,
        "transition sensitivity no longer records material endpoint change",
    )
    checks.check(
        float(transition_sensitivity.get("max_endpoint_coordinate_delta_vs_baseline", 0.0)) > 1.0e-6,
        "transition sensitivity coordinate delta too small",
    )
    checks.check(
        float(transition_sensitivity.get("max_endpoint_velocity_delta_vs_baseline", 0.0)) > 1.0e-4,
        "transition sensitivity velocity delta too small",
    )
    sensitivity_rows = transition_sensitivity.get("endpoint_delta_rows", [])
    checks.check(len(sensitivity_rows) == 3, "transition sensitivity endpoint rows missing")
    checks.check(
        {row.get("stribeck_velocity") for row in sensitivity_rows} == {0.05, 0.5, 1.0},
        "transition sensitivity endpoint velocity ids changed",
    )
    expected_line_anchors = {
        "mu_static_parameter": 1040,
        "mu_dynamic_parameter": 1041,
        "brown_mcphee_model_family": 1056,
        "details_deferred": 1056,
        "reference_38_entry": 1579,
        "reference_39_entry": 1581,
    }
    anchors_by_id = {anchor.get("id"): anchor for anchor in line_anchors}
    checks.check(set(anchors_by_id) == set(expected_line_anchors), "source text line anchor ids changed")
    for anchor_id, line_number in expected_line_anchors.items():
        anchor = anchors_by_id.get(anchor_id, {})
        checks.check(anchor.get("found") is True, f"{anchor_id} source text anchor missing")
        checks.check(anchor.get("line_number") == line_number, f"{anchor_id} line number changed")
    for reference_key in ["reference_38", "reference_39"]:
        reference = detail_sources.get(reference_key, {})
        checks.check(reference.get("source_text_entry_found") is True, f"{reference_key} entry not found")
        checks.check(
            reference.get("local_full_text_or_source_code_present") is False,
            f"{reference_key} local full text/source code unexpectedly present",
        )
    checks.check(
        "implementation constants" in detail_sources.get("reference_38", {}).get("boundary", ""),
        "reference 38 boundary missing implementation-constants wording",
    )
    checks.check(
        "transition velocity" in detail_sources.get("reference_39", {}).get("boundary", ""),
        "reference 39 boundary missing transition-velocity wording",
    )
    checks.check(
        gap_status.get("gap_id") == "brown_mcphee_source_code_equivalent_law_open",
        "row-audit Brown-McPhee gap not carried",
    )
    checks.check(gap_status.get("gap_status") == "open", "row-audit Brown-McPhee gap unexpectedly closed")
    checks.check(gap_status.get("can_resolve_without_heavy_run") is True, "Brown-McPhee gap non-heavy flag changed")
    checks.check(
        any(
            row.get("id") == "brown_mcphee_source_code_equivalent_law_open"
            for row in row_gap_matrix.get("open_blockers", [])
        ),
        "row audit no longer carries Brown-McPhee open blocker",
    )
    checks.check(
        closure.get("can_close_brown_mcphee_source_code_equivalent_law_now") is False
        and closure.get("can_promote_frictional_tfe_source_policy_rows_now") is False,
        "closure decision overclaims Brown-McPhee source policy",
    )

    for token in [
        "Status: **source formula structure encoded; surrogate is not source-code equivalent**.",
        "Candidate friction law encoded: `True`.",
        "Published formula structure encoded: `True`.",
        "Source-code-equivalent law: `False`.",
        "Transition velocity resolved from source: `False`.",
        "Source-policy rows promoted: `0`.",
        "Frictional source-policy rows demoted: `True`.",
        "Non-heavy contract block closed: `False`.",
        "Source-policy execution allowed now/invoked/exact opt-in required: `False/False/True`.",
        "Safe action ids: `rebuild_read_only_audit_chain,rerun_read_only_validators,keep_narrowed_archive_provenance_only,monitor_reopen_conditions`.",
        "Opt-in action ids: `authorized_b4_ra_hi_source_policy_execution`.",
        "Source text defers law details to Refs. 38--39: `True`.",
        "`mu_static_parameter` | `1040` | `True`",
        "`mu_dynamic_parameter` | `1041` | `True`",
        "`brown_mcphee_model_family` | `1056` | `True`",
        "`reference_38_entry` | `1579` | `True`",
        "`reference_39_entry` | `1581` | `True`",
        "Reference 38 local full text/source code present: `False`.",
        "Reference 39 local full text/source code present: `False`.",
        "Reference 38 boundary: bibliographic pointer only",
        "Reference 39 boundary: bibliographic pointer only",
        "Provenance label: `v022_revolute_brown_mcphee_surrogate_not_source_policy_equivalent`.",
        "v022 local Stribeck velocity cases: `[0.5, 0.05]`.",
        "Accepted source-policy equivalence: `False`.",
        "## Frictional Source-Policy Demotion Contract",
        "Demotion scope: all original-TFE frictional pendulum rows",
        "Allowed use: `local_dissipativity_residual_sensitivity_diagnostic_only`.",
        "Source-policy rows completed/promoted: `0/0`.",
        "Required before promotion:",
        "source-code or Refs. 38--39 transition/Stribeck velocity",
        "Rows/step residual rows/source-policy rows: `12/56/0`.",
        "Finite/residual-below-1e-9/friction-power-nonpositive: `True/True/True`.",
        "Equivalent DAE/method/source-law/monolithic: `False/False/False/False`.",
        "Accepted use: `candidate_frictional_dae_trajectory_contract_not_source_policy`.",
        "Runner scope: `candidate_brown_mcphee_friction_bound_to_stepwise_absolute_dae_residuals_not_source_policy`.",
        "Sensitivity rows/contracts/source-policy rows: `3/36/0`.",
        "Contract finite/residual/power/equivalence-false: `True/True/True/True`.",
        "Missing transition velocity numerically material: `True`.",
        "Tested Stribeck velocities/baseline: `[0.05, 0.5, 1.0]/0.5`.",
        "No TFE source-policy rows are promoted by this audit.",
    ]:
        checks.check(token in audit_md, f"markdown missing token: {token}")

    if checks.errors:
        print("TFE Brown-McPhee source-law boundary audit validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("TFE Brown-McPhee source-law boundary audit validation: PASS")
    print(f"status={audit.get('status')}")
    print("source_policy_rows_promoted=0")
    print("source_policy_execution_invoked=False")
    print("source_policy_execution_allowed_now=False")
    print("brown_mcphee_source_code_equivalent_law=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
