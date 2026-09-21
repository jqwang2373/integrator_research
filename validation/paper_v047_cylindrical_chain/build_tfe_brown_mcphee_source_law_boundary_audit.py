#!/usr/bin/env python3
"""Build a read-only boundary audit for the TFE Brown--McPhee friction law."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
ROOT = PAPER.parent
REPO = ROOT.parent
SOURCE_TXT = REPO / "external" / "literature" / "s11044-026-10153-w.txt"
MODEL_PATH = ROOT.parent / "numerics" / "v048_cross_paper_same_test_benchmarks" / "tfe_source_pendulum_model.py"
V021_README = ROOT.parent / "numerics" / "v021_brown_mcphee_lambda_friction" / "README.md"
V021_RUN = ROOT.parent / "numerics" / "v021_brown_mcphee_lambda_friction" / "run_v021.py"
V022_README = ROOT.parent / "numerics" / "v022_revolute_brown_mcphee" / "README.md"
V022_RUN = ROOT.parent / "numerics" / "v022_revolute_brown_mcphee" / "run_v022.py"
OUT_JSON = PAPER / "TFE_BROWN_MCPHEE_SOURCE_LAW_BOUNDARY_AUDIT.json"
OUT_MD = PAPER / "TFE_BROWN_MCPHEE_SOURCE_LAW_BOUNDARY_AUDIT.md"

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


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""


def load_model_module():
    spec = importlib.util.spec_from_file_location("tfe_source_pendulum_model", MODEL_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {MODEL_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def source_gap(row_audit: dict[str, Any]) -> dict[str, Any]:
    blockers = row_audit.get("source_policy_runner_equivalence_gap_matrix", {}).get("open_blockers", [])
    for row in blockers:
        if row.get("id") == "brown_mcphee_source_code_equivalent_law_open":
            return row
    return {}


def source_line_anchors(source_text: str) -> list[dict[str, Any]]:
    targets = [
        (
            "mu_static_parameter",
            "μs                   0.3",
            "source paper reports the static friction coefficient used in the pendulum case study",
        ),
        (
            "mu_dynamic_parameter",
            "μd                   0.2",
            "source paper reports the dynamic friction coefficient used in the pendulum case study",
        ),
        (
            "brown_mcphee_model_family",
            "McPhee’s velocity based continuous friction model",
            "source paper names the Brown--McPhee velocity-based model family",
        ),
        (
            "details_deferred",
            "For more details on continuous",
            "source paper defers continuous-friction model details to external references",
        ),
        (
            "reference_38_entry",
            "38. Brown, P., McPhee, J.",
            "reference 38 is the Brown--McPhee model paper, not local executable source code",
        ),
        (
            "reference_39_entry",
            "39. Chaturvedi, E., Mukherjee, J., Sandu, C.",
            "reference 39 is an additional friction-model paper, not local executable source code",
        ),
    ]
    lines = source_text.splitlines()
    anchors = []
    for anchor_id, token, role in targets:
        line_number = next((index for index, line in enumerate(lines, start=1) if token in line), None)
        anchors.append(
            {
                "id": anchor_id,
                "token": token,
                "line_number": line_number,
                "found": line_number is not None,
                "evidence_role": role,
            }
        )
    return anchors


def transition_velocity_sensitivity(model: Any) -> dict[str, Any]:
    tested_stribeck_velocities = (0.05, 0.5, 1.0)
    baseline_stribeck_velocity = 0.5
    states: dict[float, Any] = {}
    diagnostics_by_velocity: dict[float, dict[str, Any]] = {}
    contract_summaries: list[dict[str, Any]] = []
    contract_row_count = 0
    step_residual_row_count = 0
    all_contract_rows_finite = True
    all_contract_dae_residuals_below_1e_9 = True
    all_contract_friction_power_nonpositive = True
    all_contract_source_policy_rows_completed_zero = True
    all_contract_equivalence_flags_false = True

    for stribeck_velocity in tested_stribeck_velocities:
        config = model.BoundedSourcePolicyRunnerConfig(
            theta0=0.0,
            omega0=1.0,
            t_final=0.024,
            comparison_h=(0.012, 0.006, 0.003),
            reference_h=0.0001,
            axis="z",
            frictional=True,
            stribeck_velocity=stribeck_velocity,
            viscous_damping=0.0,
        )
        contract = model.candidate_frictional_dae_trajectory_contract_smoke(config)
        state, diagnostics = model.integrate_planar_case_with_method(
            method="rk4_reference",
            theta0=config.theta0,
            omega0=config.omega0,
            h=config.reference_h,
            t_final=config.t_final,
            frictional=True,
            axis=config.axis,
            stribeck_velocity=stribeck_velocity,
            viscous_damping=config.viscous_damping,
        )
        states[stribeck_velocity] = state
        diagnostics_by_velocity[stribeck_velocity] = diagnostics
        contract_row_count += int(contract.get("row_count", 0))
        step_residual_row_count += int(contract.get("step_residual_row_count", 0))
        all_contract_rows_finite = (
            all_contract_rows_finite and contract.get("all_rows_finite") is True
        )
        all_contract_dae_residuals_below_1e_9 = (
            all_contract_dae_residuals_below_1e_9
            and contract.get("all_dae_residuals_below_1e_9") is True
        )
        all_contract_friction_power_nonpositive = (
            all_contract_friction_power_nonpositive
            and contract.get("all_candidate_friction_power_nonpositive") is True
        )
        all_contract_source_policy_rows_completed_zero = (
            all_contract_source_policy_rows_completed_zero
            and contract.get("source_policy_rows_completed") == 0
        )
        all_contract_equivalence_flags_false = (
            all_contract_equivalence_flags_false
            and contract.get("source_policy_dae_runner_equivalent") is False
            and contract.get("source_policy_method_runner_equivalent") is False
            and contract.get("brown_mcphee_source_code_equivalent_law") is False
            and contract.get("monolithic_absolute_coordinate_dae_time_integrator") is False
        )
        contract_summaries.append(
            {
                "stribeck_velocity": stribeck_velocity,
                "row_count": contract.get("row_count"),
                "step_residual_row_count": contract.get("step_residual_row_count"),
                "all_rows_finite": contract.get("all_rows_finite"),
                "all_dae_residuals_below_1e_9": contract.get("all_dae_residuals_below_1e_9"),
                "all_candidate_friction_power_nonpositive": contract.get(
                    "all_candidate_friction_power_nonpositive"
                ),
                "max_candidate_step_residual_norm": contract.get(
                    "max_candidate_step_residual_norm"
                ),
                "source_policy_rows_completed": contract.get("source_policy_rows_completed"),
                "source_policy_dae_runner_equivalent": contract.get(
                    "source_policy_dae_runner_equivalent"
                ),
                "source_policy_method_runner_equivalent": contract.get(
                    "source_policy_method_runner_equivalent"
                ),
                "brown_mcphee_source_code_equivalent_law": contract.get(
                    "brown_mcphee_source_code_equivalent_law"
                ),
                "monolithic_absolute_coordinate_dae_time_integrator": contract.get(
                    "monolithic_absolute_coordinate_dae_time_integrator"
                ),
            }
        )

    baseline_state = states[baseline_stribeck_velocity]
    endpoint_delta_rows: list[dict[str, Any]] = []
    max_endpoint_coordinate_delta = 0.0
    max_endpoint_velocity_delta = 0.0
    for stribeck_velocity in tested_stribeck_velocities:
        state = states[stribeck_velocity]
        metrics = model.source_error_metrics(baseline_state, state, axis="z")
        max_endpoint_coordinate_delta = max(
            max_endpoint_coordinate_delta,
            float(metrics["coordinate_error_q"]),
        )
        max_endpoint_velocity_delta = max(
            max_endpoint_velocity_delta,
            float(metrics["velocity_error_v"]),
        )
        endpoint_delta_rows.append(
            {
                "stribeck_velocity": stribeck_velocity,
                "baseline_stribeck_velocity": baseline_stribeck_velocity,
                "theta_final": float(state.theta),
                "omega_final": float(state.omega),
                "diagnostics": diagnostics_by_velocity[stribeck_velocity],
                **metrics,
            }
        )

    return {
        "schema": "tfe-brown-mcphee-transition-velocity-sensitivity-v1",
        "status": "candidate_transition_velocity_sensitivity_recorded_not_source_policy",
        "runner_scope": "candidate_brown_mcphee_transition_velocity_sensitivity_not_source_policy",
        "accepted_use": "local_candidate_sensitivity_boundary_not_source_policy",
        "tested_stribeck_velocities": list(tested_stribeck_velocities),
        "baseline_stribeck_velocity": baseline_stribeck_velocity,
        "t_final": 0.024,
        "reference_h": 0.0001,
        "theta0": 0.0,
        "omega0": 1.0,
        "frictional": True,
        "endpoint_delta_row_count": len(endpoint_delta_rows),
        "contract_row_count": contract_row_count,
        "step_residual_row_count": step_residual_row_count,
        "all_contract_rows_finite": all_contract_rows_finite,
        "all_contract_dae_residuals_below_1e_9": all_contract_dae_residuals_below_1e_9,
        "all_contract_friction_power_nonpositive": all_contract_friction_power_nonpositive,
        "all_contract_source_policy_rows_completed_zero": all_contract_source_policy_rows_completed_zero,
        "all_contract_equivalence_flags_false": all_contract_equivalence_flags_false,
        "max_endpoint_coordinate_delta_vs_baseline": max_endpoint_coordinate_delta,
        "max_endpoint_velocity_delta_vs_baseline": max_endpoint_velocity_delta,
        "missing_transition_velocity_is_numerically_material": (
            max_endpoint_coordinate_delta > 1.0e-6
            and max_endpoint_velocity_delta > 1.0e-4
        ),
        "source_policy_rows_completed": 0,
        "source_policy_rows_promoted": 0,
        "source_policy_dae_runner_equivalent": False,
        "source_policy_method_runner_equivalent": False,
        "brown_mcphee_source_code_equivalent_law": False,
        "external_superiority_claim_allowed": False,
        "endpoint_delta_rows": endpoint_delta_rows,
        "contract_summaries": contract_summaries,
    }


def main() -> None:
    spec = read_json(PAPER / "TFE_SOURCE_POLICY_SPEC.json")
    model_audit = read_json(PAPER / "TFE_SOURCE_PENDULUM_MODEL_AUDIT.json")
    row_audit = read_json(PAPER / "TFE_SOURCE_POLICY_ROW_AUDIT.json")
    model = load_model_module()
    model_source = read_text(MODEL_PATH)
    source_text = read_text(SOURCE_TXT)
    v021_readme = read_text(V021_README)
    v021_run = read_text(V021_RUN)
    v022_readme = read_text(V022_README)
    v022_run = read_text(V022_RUN)

    friction_spec = spec.get("source_policy", {}).get("friction_parameters", {})
    source_anchor = model_audit.get("brown_mcphee_source_text_anchor", {})
    formula_boundary = model_audit.get("brown_mcphee_formula_boundary", {})
    candidate_trajectory_contract = model_audit.get(
        "candidate_frictional_dae_trajectory_contract_smoke", {}
    )
    velocity_sensitivity = transition_velocity_sensitivity(model)
    gap = source_gap(row_audit)

    code_scan = {
        "candidate_function_present": "def brown_mcphee_candidate_torque" in model_source,
        "candidate_docstring_names_surrogate": "local v022 surrogate" in model_source,
        "candidate_docstring_denies_source_policy_equivalence": (
            "not provide enough law detail" in model_source
            and "source-policy equivalence" in model_source
        ),
        "candidate_uses_tanh_coulomb_term": "np.tanh(4.0 * z)" in model_source,
        "candidate_uses_rational_stiction_term": "(0.25 * z * z + 0.75) ** 2" in model_source,
        "candidate_exposes_stribeck_velocity_parameter": "stribeck_velocity" in model_source,
        "candidate_exposes_viscous_damping_parameter": "viscous_damping" in model_source,
    }

    local_surrogate_provenance = {
        "v021_readme": "../../numerics/v021_brown_mcphee_lambda_friction/README.md",
        "v021_readme_present": bool(v021_readme),
        "v021_run_present": bool(v021_run),
        "v021_formula_mentions_componentwise_surrogate": (
            "componentwise scalar curve" in v021_readme
            and "tau_i = -r_f" in v021_readme
        ),
        "v022_readme": "../../numerics/v022_revolute_brown_mcphee/README.md",
        "v022_readme_present": bool(v022_readme),
        "v022_run_present": bool(v022_run),
        "v022_formula_matches_candidate_family": (
            "tau_f = -r_f ||lambda||" in v022_readme
            and "(0.25 z^2 + 0.75)^2" in v022_readme
        ),
        "v022_run_has_matching_candidate_function": "def brown_mcphee_torque" in v022_run,
        "v022_local_stribeck_velocity_cases": [0.50, 0.05]
        if '"revolute_bm_smooth": 0.50' in v022_run and '"revolute_bm_sharp": 0.05' in v022_run
        else [],
        "provenance_label": model_audit.get("candidate_friction_law_provenance"),
        "accepted_source_policy_equivalence": False,
    }

    unresolved = list(formula_boundary.get("missing_for_source_policy_equivalence", []))
    if friction_spec.get("requires_reference_38_39_or_existing_source_code") is True:
        unresolved.append("Brown--McPhee reference source code or Refs. 38--39 implementation details")
    if friction_spec.get("law_details_available_in_source_paper") is False:
        unresolved.append("complete law details are not available in the TFE source paper text")
    demotion_contract = {
        "frictional_source_policy_rows_demoted": True,
        "demotion_scope": "all original-TFE frictional pendulum rows whose acceptance depends on a Brown--McPhee source-code-equivalent law",
        "demotion_reason": (
            "The source paper supplies mu_s/mu_d and names the Brown--McPhee model family, but it "
            "does not provide the transition/Stribeck velocity, source-code normal-load coupling, "
            "viscous damping/default policy, or implementation-level coupling needed to bind the "
            "candidate law to source-policy rows."
        ),
        "candidate_evidence_allowed_use": "local_dissipativity_residual_sensitivity_diagnostic_only",
        "source_policy_rows_completed": 0,
        "source_policy_rows_promoted": 0,
        "required_to_promote": [
            "source-code or Refs. 38--39 transition/Stribeck velocity",
            "source-code normal-load and joint-multiplier coupling policy",
            "source-code viscous damping or zero-viscous default policy",
            "source implementation tolerance/Jacobian coupling for friction rows",
            "source-equivalent absolute-coordinate DAE and method-runner contracts",
        ],
    }

    output: dict[str, Any] = {
        "schema": "tfe-brown-mcphee-source-law-boundary-audit-v1",
        "status": "source_formula_structure_encoded_surrogate_not_source_code_equivalent",
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
        "source_policy_rows_completed": 0,
        "source_policy_rows_promoted": 0,
        "frictional_source_policy_rows_demoted": demotion_contract[
            "frictional_source_policy_rows_demoted"
        ],
        "nonheavy_contract_block_closed": False,
        "brown_mcphee_candidate_friction_law_encoded": model_audit.get(
            "brown_mcphee_candidate_friction_law_encoded"
        ),
        "brown_mcphee_published_formula_structure_encoded": model_audit.get(
            "brown_mcphee_published_formula_structure_encoded"
        ),
        "brown_mcphee_source_code_equivalent_law": model_audit.get(
            "brown_mcphee_source_code_equivalent_law"
        ),
        "brown_mcphee_transition_velocity_policy_resolved_from_source": model_audit.get(
            "brown_mcphee_transition_velocity_policy_resolved_from_source"
        ),
        "source_text_anchor": {
            "source_text": source_anchor.get("source_text"),
            "source_text_found": source_anchor.get("source_text_found"),
            "names_velocity_based_continuous_model": source_anchor.get(
                "names_velocity_based_continuous_model"
            ),
            "reports_mu_static_dynamic": source_anchor.get("reports_mu_static_dynamic"),
            "defers_law_details_to_refs_38_39": source_anchor.get("defers_law_details_to_refs_38_39"),
        },
        "source_policy_friction_spec_boundary": {
            "model_family": friction_spec.get("model_family"),
            "mu_static": friction_spec.get("mu_static"),
            "mu_dynamic": friction_spec.get("mu_dynamic"),
            "law_details_available_in_source_paper": friction_spec.get(
                "law_details_available_in_source_paper"
            ),
            "requires_reference_38_39_or_existing_source_code": friction_spec.get(
                "requires_reference_38_39_or_existing_source_code"
            ),
        },
        "formula_boundary": {
            "encoded_candidate_formula": formula_boundary.get("encoded_candidate_formula"),
            "encoded_parameters": formula_boundary.get("encoded_parameters"),
            "missing_for_source_policy_equivalence": unresolved,
        },
        "source_text_line_anchors": source_line_anchors(source_text),
        "referenced_detail_sources": {
            "reference_38": {
                "label": "Brown--McPhee continuous velocity-based friction model paper",
                "local_full_text_or_source_code_present": False,
                "source_text_entry_found": "38. Brown, P., McPhee, J." in source_text,
                "boundary": "bibliographic pointer only in current package; no implementation constants or code binding available",
            },
            "reference_39": {
                "label": "Chaturvedi--Mukherjee--Sandu dynamic dry friction model paper",
                "local_full_text_or_source_code_present": False,
                "source_text_entry_found": "39. Chaturvedi, E., Mukherjee, J., Sandu, C." in source_text,
                "boundary": "bibliographic pointer only in current package; no transition velocity or coupling policy extracted",
            },
        },
        "candidate_friction_torque_smoke": model_audit.get("candidate_friction_torque_smoke"),
        "frictional_candidate_smoke_trajectory": {
            "max_candidate_friction_power": model_audit.get(
                "frictional_candidate_smoke_trajectory", {}
            ).get("max_candidate_friction_power"),
            "min_candidate_friction_power": model_audit.get(
                "frictional_candidate_smoke_trajectory", {}
            ).get("min_candidate_friction_power"),
            "source_policy_rows_completed": model_audit.get(
                "frictional_candidate_smoke_trajectory", {}
            ).get("source_policy_rows_completed"),
        },
        "candidate_frictional_dae_trajectory_contract": {
            "implemented": model_audit.get(
                "candidate_frictional_dae_trajectory_contract_implemented"
            ),
            "schema": candidate_trajectory_contract.get("schema"),
            "runner_api": candidate_trajectory_contract.get("runner_api"),
            "runner_scope": candidate_trajectory_contract.get("runner_scope"),
            "accepted_use": candidate_trajectory_contract.get("accepted_use"),
            "row_count": candidate_trajectory_contract.get("row_count"),
            "step_residual_row_count": candidate_trajectory_contract.get(
                "step_residual_row_count"
            ),
            "method_count": candidate_trajectory_contract.get("method_count"),
            "comparison_h": candidate_trajectory_contract.get("comparison_h"),
            "reference_h": candidate_trajectory_contract.get("reference_h"),
            "t_final": candidate_trajectory_contract.get("t_final"),
            "theta0": candidate_trajectory_contract.get("theta0"),
            "omega0": candidate_trajectory_contract.get("omega0"),
            "frictional": candidate_trajectory_contract.get("frictional"),
            "all_rows_finite": candidate_trajectory_contract.get("all_rows_finite"),
            "all_dae_residuals_below_1e_9": candidate_trajectory_contract.get(
                "all_dae_residuals_below_1e_9"
            ),
            "all_candidate_friction_power_nonpositive": candidate_trajectory_contract.get(
                "all_candidate_friction_power_nonpositive"
            ),
            "max_candidate_step_residual_norm": candidate_trajectory_contract.get(
                "max_candidate_step_residual_norm"
            ),
            "max_candidate_friction_power": candidate_trajectory_contract.get(
                "max_candidate_friction_power"
            ),
            "min_candidate_friction_power": candidate_trajectory_contract.get(
                "min_candidate_friction_power"
            ),
            "source_policy_rows_completed": candidate_trajectory_contract.get(
                "source_policy_rows_completed"
            ),
            "source_policy_dae_runner_equivalent": candidate_trajectory_contract.get(
                "source_policy_dae_runner_equivalent"
            ),
            "source_policy_method_runner_equivalent": candidate_trajectory_contract.get(
                "source_policy_method_runner_equivalent"
            ),
            "brown_mcphee_source_code_equivalent_law": candidate_trajectory_contract.get(
                "brown_mcphee_source_code_equivalent_law"
            ),
            "monolithic_absolute_coordinate_dae_time_integrator": candidate_trajectory_contract.get(
                "monolithic_absolute_coordinate_dae_time_integrator"
            ),
        },
        "brown_mcphee_transition_velocity_sensitivity": velocity_sensitivity,
        "candidate_formula_code_scan": code_scan,
        "local_surrogate_provenance": local_surrogate_provenance,
        "frictional_source_policy_row_demotion_contract": demotion_contract,
        "row_audit_gap_status": {
            "gap_id": gap.get("id"),
            "gap_status": gap.get("status"),
            "first_required_artifact": gap.get("first_required_artifact"),
            "can_resolve_without_heavy_run": gap.get("can_resolve_without_heavy_run"),
            "blocking_source_fields": gap.get("blocking_source_fields", []),
        },
        "closure_decision": {
            "can_close_brown_mcphee_source_code_equivalent_law_now": False,
            "can_promote_frictional_tfe_source_policy_rows_now": False,
            "reason": (
                "The artifact confirms that a Brown--McPhee-style candidate formula is encoded and "
                "dissipative, with local v021/v022 surrogate provenance and a bounded multi-step "
                "candidate DAE trajectory contract. A bounded transition-velocity sensitivity check "
                "also shows that the unresolved Stribeck/transition velocity changes the candidate "
                "endpoint state. The TFE source paper does not provide the transition velocity, "
                "source-code coupling, or implementation details needed to certify "
                "source-code-equivalent friction rows."
            ),
        },
        "safe_next_actions": [
            "Keep the candidate law labeled as a surrogate in manuscript and package text.",
            "Use the candidate-friction DAE trajectory contract only as a local dissipativity/residual sanity check.",
            "Use the transition-velocity sensitivity only to justify the open source-law boundary.",
            "Only promote Brown--McPhee frictional rows after source code or Refs. 38--39 resolve the transition velocity and coupling policy.",
            "Do not close TFE source-policy work/precision rows from this boundary audit.",
        ],
        "source_files": {
            "source_policy_spec": "TFE_SOURCE_POLICY_SPEC.json",
            "source_pendulum_model_audit": "TFE_SOURCE_PENDULUM_MODEL_AUDIT.json",
            "source_policy_row_audit": "TFE_SOURCE_POLICY_ROW_AUDIT.json",
            "tfe_model_source": "../../numerics/v048_cross_paper_same_test_benchmarks/tfe_source_pendulum_model.py",
            "v021_readme": "../../numerics/v021_brown_mcphee_lambda_friction/README.md",
            "v022_readme": "../../numerics/v022_revolute_brown_mcphee/README.md",
        },
    }

    with OUT_JSON.open("w", encoding="utf-8") as handle:
        json.dump(output, handle, indent=2, sort_keys=True)
        handle.write("\n")

    lines = [
        "# TFE Brown--McPhee Source-Law Boundary Audit",
        "",
        "Status: **source formula structure encoded; surrogate is not source-code equivalent**.",
        "",
        "This audit is read-only over existing TFE artifacts, local v021/v022 provenance, and source text.",
        "",
        f"- Candidate friction law encoded: `{output['brown_mcphee_candidate_friction_law_encoded']}`.",
        f"- Published formula structure encoded: `{output['brown_mcphee_published_formula_structure_encoded']}`.",
        f"- Source-code-equivalent law: `{output['brown_mcphee_source_code_equivalent_law']}`.",
        (
            "- Transition velocity resolved from source: "
            f"`{output['brown_mcphee_transition_velocity_policy_resolved_from_source']}`."
        ),
        f"- Source-policy rows promoted: `{output['source_policy_rows_promoted']}`.",
        f"- Frictional source-policy rows demoted: `{output['frictional_source_policy_rows_demoted']}`.",
        f"- Non-heavy contract block closed: `{output['nonheavy_contract_block_closed']}`.",
        f"- Source-policy execution allowed now/invoked/exact opt-in required: `{output['source_policy_execution_allowed_now']}/{output['source_policy_execution_invoked']}/{output['exact_b4_opt_in_required_for_execution']}`.",
        f"- Safe action ids: `{','.join(output['safe_action_ids'])}`.",
        f"- Opt-in action ids: `{','.join(output['opt_in_action_ids'])}`.",
        "",
        "## Source Boundary",
        "",
        f"- Source text found: `{output['source_text_anchor']['source_text_found']}`.",
        (
            "- Source text names velocity-based continuous model: "
            f"`{output['source_text_anchor']['names_velocity_based_continuous_model']}`."
        ),
        f"- Source text reports mu_s/mu_d: `{output['source_text_anchor']['reports_mu_static_dynamic']}`.",
        (
            "- Source text defers law details to Refs. 38--39: "
            f"`{output['source_text_anchor']['defers_law_details_to_refs_38_39']}`."
        ),
        (
            "- Source paper law details available in this artifact: "
            f"`{output['source_policy_friction_spec_boundary']['law_details_available_in_source_paper']}`."
        ),
        (
            "- Requires Refs. 38--39 or source code: "
            f"`{output['source_policy_friction_spec_boundary']['requires_reference_38_39_or_existing_source_code']}`."
        ),
        "",
        "## Source Text Line Anchors",
        "",
        "| id | line | found | role |",
        "|---|---:|---|---|",
    ]
    for anchor in output["source_text_line_anchors"]:
        lines.append(
            f"| `{anchor['id']}` | `{anchor['line_number']}` | `{anchor['found']}` | {anchor['evidence_role']} |"
        )
    lines.extend(
        [
            "",
            "## Referenced Detail Sources",
            "",
            (
                "- Reference 38 local full text/source code present: "
                f"`{output['referenced_detail_sources']['reference_38']['local_full_text_or_source_code_present']}`."
            ),
            (
                "- Reference 39 local full text/source code present: "
                f"`{output['referenced_detail_sources']['reference_39']['local_full_text_or_source_code_present']}`."
            ),
            "- Reference 38 boundary: bibliographic pointer only in current package; no implementation constants or code binding available.",
            "- Reference 39 boundary: bibliographic pointer only in current package; no transition velocity or coupling policy extracted.",
            "",
            "## Local Surrogate Provenance",
            "",
            f"- Provenance label: `{local_surrogate_provenance['provenance_label']}`.",
            f"- v021 README/function present: `{local_surrogate_provenance['v021_readme_present']}/{local_surrogate_provenance['v021_run_present']}`.",
            f"- v022 README/function present: `{local_surrogate_provenance['v022_readme_present']}/{local_surrogate_provenance['v022_run_present']}`.",
            f"- v022 formula matches candidate family: `{local_surrogate_provenance['v022_formula_matches_candidate_family']}`.",
            f"- v022 local Stribeck velocity cases: `{local_surrogate_provenance['v022_local_stribeck_velocity_cases']}`.",
            f"- Accepted source-policy equivalence: `{local_surrogate_provenance['accepted_source_policy_equivalence']}`.",
            "",
            "## Frictional Source-Policy Demotion Contract",
            "",
            f"- Frictional source-policy rows demoted: `{demotion_contract['frictional_source_policy_rows_demoted']}`.",
            f"- Demotion scope: {demotion_contract['demotion_scope']}.",
            f"- Allowed use: `{demotion_contract['candidate_evidence_allowed_use']}`.",
            f"- Source-policy rows completed/promoted: `{demotion_contract['source_policy_rows_completed']}/{demotion_contract['source_policy_rows_promoted']}`.",
            f"- Reason: {demotion_contract['demotion_reason']}",
            "- Required before promotion:",
        ]
    )
    lines.extend(f"  - {item}." for item in demotion_contract["required_to_promote"])
    lines.extend(
        [
            "",
            "## Candidate-Friction DAE Trajectory Contract",
            "",
            f"- Implemented: `{output['candidate_frictional_dae_trajectory_contract']['implemented']}`.",
            (
                "- Rows/step residual rows/source-policy rows: "
                f"`{output['candidate_frictional_dae_trajectory_contract']['row_count']}/"
                f"{output['candidate_frictional_dae_trajectory_contract']['step_residual_row_count']}/"
                f"{output['candidate_frictional_dae_trajectory_contract']['source_policy_rows_completed']}`."
            ),
            (
                "- Finite/residual-below-1e-9/friction-power-nonpositive: "
                f"`{output['candidate_frictional_dae_trajectory_contract']['all_rows_finite']}/"
                f"{output['candidate_frictional_dae_trajectory_contract']['all_dae_residuals_below_1e_9']}/"
                f"{output['candidate_frictional_dae_trajectory_contract']['all_candidate_friction_power_nonpositive']}`."
            ),
            (
                "- Equivalent DAE/method/source-law/monolithic: "
                f"`{output['candidate_frictional_dae_trajectory_contract']['source_policy_dae_runner_equivalent']}/"
                f"{output['candidate_frictional_dae_trajectory_contract']['source_policy_method_runner_equivalent']}/"
                f"{output['candidate_frictional_dae_trajectory_contract']['brown_mcphee_source_code_equivalent_law']}/"
                f"{output['candidate_frictional_dae_trajectory_contract']['monolithic_absolute_coordinate_dae_time_integrator']}`."
            ),
            f"- Accepted use: `{output['candidate_frictional_dae_trajectory_contract']['accepted_use']}`.",
            f"- Runner scope: `{output['candidate_frictional_dae_trajectory_contract']['runner_scope']}`.",
            "",
            "## Transition-Velocity Sensitivity",
            "",
            (
                "- Sensitivity rows/contracts/source-policy rows: "
                f"`{velocity_sensitivity['endpoint_delta_row_count']}/"
                f"{velocity_sensitivity['contract_row_count']}/"
                f"{velocity_sensitivity['source_policy_rows_completed']}`."
            ),
            (
                "- Contract finite/residual/power/equivalence-false: "
                f"`{velocity_sensitivity['all_contract_rows_finite']}/"
                f"{velocity_sensitivity['all_contract_dae_residuals_below_1e_9']}/"
                f"{velocity_sensitivity['all_contract_friction_power_nonpositive']}/"
                f"{velocity_sensitivity['all_contract_equivalence_flags_false']}`."
            ),
            (
                "- Max endpoint coordinate/velocity delta vs baseline: "
                f"`{velocity_sensitivity['max_endpoint_coordinate_delta_vs_baseline']:.3e}/"
                f"{velocity_sensitivity['max_endpoint_velocity_delta_vs_baseline']:.3e}`."
            ),
            (
                "- Missing transition velocity numerically material: "
                f"`{velocity_sensitivity['missing_transition_velocity_is_numerically_material']}`."
            ),
            (
                "- Tested Stribeck velocities/baseline: "
                f"`{velocity_sensitivity['tested_stribeck_velocities']}/"
                f"{velocity_sensitivity['baseline_stribeck_velocity']}`."
            ),
            "",
            "## Missing For Source-Policy Equivalence",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in unresolved)
    lines.extend(
        [
            "",
            "## Decision",
            "",
            output["closure_decision"]["reason"],
            "",
            "No TFE source-policy rows are promoted by this audit.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("tfe_brown_mcphee_source_law_boundary_audit=written")
    print(f"status={output['status']}")
    print("source_policy_rows_promoted=0")
    print("source_policy_execution_invoked=False")
    print("source_policy_execution_allowed_now=False")
    print("brown_mcphee_source_code_equivalent_law=False")


if __name__ == "__main__":
    main()
