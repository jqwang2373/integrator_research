#!/usr/bin/env python3
"""Validate the HI2022 source-policy row audit."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent


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
        audit = read_json(PAPER / "HI2022_SOURCE_POLICY_ROW_AUDIT.json")
        audit_md = read_text(PAPER / "HI2022_SOURCE_POLICY_ROW_AUDIT.md")
        b2 = read_json(PAPER / "B2_SOURCE_POLICY_REMAINING_WORK_MANIFEST.json")
        hi_policy = read_json(PAPER / "HI2022_POLICY_DECISION_AUDIT.json")
        acceptance = read_json(PAPER / "EXTERNAL_SAME_TEST_ACCEPTANCE_SHEET.json")
    except Exception as exc:  # noqa: BLE001
        print(f"HI2022 source-policy row audit validation: FAIL\n- {exc}")
        return 1

    flagged_b2_rows = [
        row
        for row in b2.get("rows", [])
        if row.get("suite_id") == "hi2022_half_implicit"
    ]
    active_b2_rows_after_demotion = [
        row for row in flagged_b2_rows if row.get("active_b2_requirement") is True
    ]
    demoted_b2_rows = [
        row
        for row in flagged_b2_rows
        if row.get("demoted_from_external_superiority_scope") is True
        or row.get("status") == "closed_by_explicit_source_policy_demotion"
    ]
    source_policy = hi_policy.get("source_policy_required_before_external_superiority", {})
    criteria = audit.get("closure_criteria", {})
    decision = audit.get("decision", {})
    queue_policy = audit.get("queue_policy", {})
    workload = audit.get("workload_estimate", {})
    t8_coarse = audit.get("t8_coarse_horizon_evidence", {})
    t8_selected = audit.get("t8_selected_candidate_evidence", {})
    t8_matrix = audit.get("t8_selected_candidate_matrix_preflight", {})
    figure_scope = audit.get("b4_b7_figure_scope_decision", {})
    rows = audit.get("rows", [])

    checks.check(audit.get("schema") == "hi2022-source-policy-row-audit-v1", "schema changed")
    checks.check(
        audit.get("status") == "bounded_T0p1_rows_complete_full_T8_source_policy_rows_not_closed",
        "status changed",
    )
    checks.check(audit.get("submission_ready") is False, "audit overclaims submission readiness")
    checks.check(audit.get("suite_id") == "hi2022_half_implicit", "suite id changed")
    checks.check(audit.get("source_suite") == "hi2022_fang_kissel_zhang_negrut", "source suite changed")
    checks.check(
        audit.get("evidence_class") == "bounded_pilot_only_not_source_policy_reproduction",
        "evidence class changed",
    )
    checks.check(audit.get("source_policy_external_superiority_allowed") is False, "source-policy superiority overclaimed")
    checks.check(audit.get("external_superiority_claim_allowed") is False, "external superiority overclaimed")
    checks.check(audit.get("active_b2_flagged_rows") == len(flagged_b2_rows) == 3, "active B2 row count changed")
    checks.check(
        audit.get("active_b2_flagged_rows_after_demotion") == len(active_b2_rows_after_demotion) == 0,
        "post-demotion active B2 row count changed",
    )
    checks.check(
        audit.get("demoted_b2_flagged_rows") == len(demoted_b2_rows) == 3,
        "demoted B2 row count changed",
    )
    checks.check(audit.get("audited_active_rows") == len(rows) == 3, "audited row count changed")
    checks.check(audit.get("source_policy_closed_rows") == 0, "source-policy rows unexpectedly closed")
    checks.check(audit.get("external_superiority_ready_rows") == 0, "external-superiority-ready rows unexpectedly present")
    checks.check(audit.get("bounded_row_count") == 24, "bounded row count changed")
    checks.check(audit.get("bounded_ok_row_count") == 24, "bounded ok count changed")
    checks.check(audit.get("bounded_group_count") == 8, "bounded group count changed")
    checks.check(audit.get("bounded_groups_with_three_step_sizes") == 8, "bounded three-step group count changed")
    checks.check(audit.get("bounded_t_end_values") == [0.1], "bounded horizon changed")
    checks.check(audit.get("bounded_step_sizes") == [0.005, 0.01, 0.02], "bounded h-grid changed")
    checks.check(audit.get("bounded_reference_h_values") == [0.001], "bounded reference h changed")
    checks.check(audit.get("bounded_pilot_groups_completed") == 8, "bounded pilot completed groups changed")
    checks.check(audit.get("bounded_pilot_groups_required") == 8, "bounded pilot required groups changed")
    checks.check(audit.get("bounded_pilot_rows_ok") == 24, "bounded pilot ok rows changed")
    checks.check(audit.get("full_T8_policy_required") is True, "full T8 requirement changed")
    checks.check(audit.get("full_T8_policy_completed") is False, "full T8 policy unexpectedly completed")
    checks.check(audit.get("source_policy_reproduction_closed") is False, "source-policy reproduction unexpectedly closed")
    checks.check(audit.get("accepted_for_bounded_evidence") is True, "bounded evidence acceptance changed")
    checks.check(audit.get("accepted_for_external_superiority") is False, "external superiority unexpectedly accepted")
    checks.check(
        audit.get("accepted_source_policy_dynamic_order_examples_count")
        == source_policy.get("accepted_source_policy_dynamic_order_examples_count")
        == 0,
        "source-policy dynamic-order count changed",
    )
    checks.check(
        audit.get("accepted_external_dynamic_order_examples_count")
        == acceptance.get("acceptance_counts", {}).get("accepted_external_dynamic_order_examples_count")
        == 0,
        "external dynamic-order count changed",
    )
    checks.check(t8_coarse.get("artifact_present") is True, "T=8 coarse audit artifact missing")
    checks.check(
        t8_coarse.get("policy") == "T8_coarse_horizon_sanity_not_source_policy",
        "T=8 coarse policy changed",
    )
    checks.check(t8_coarse.get("row_count") == 24, "T=8 coarse row count changed")
    checks.check(t8_coarse.get("ok_row_count") == 18, "T=8 coarse ok row count changed")
    checks.check(t8_coarse.get("failed_row_count") == 6, "T=8 coarse failed row count changed")
    checks.check(t8_coarse.get("group_count") == 8, "T=8 coarse group count changed")
    checks.check(
        t8_coarse.get("complete_form_model_groups") == 4,
        "T=8 coarse complete group count changed",
    )
    checks.check(t8_coarse.get("t_end_values") == [8.0], "T=8 coarse horizon changed")
    checks.check(t8_coarse.get("step_sizes") == [0.025, 0.05, 0.1], "T=8 coarse h-grid changed")
    checks.check(t8_coarse.get("reference_h_values") == [0.0125], "T=8 coarse reference h changed")
    checks.check(t8_coarse.get("source_policy_reproduction") is False, "T=8 coarse overclaims source policy")
    checks.check(t8_coarse.get("full_T8_policy_completed") is False, "T=8 coarse overclaims full policy")
    checks.check(t8_coarse.get("default_1e_4_required") is False, "T=8 coarse requires default 1e-4")
    checks.check(
        t8_coarse.get("contains_source_policy_1e_4_rows") is False,
        "T=8 coarse unexpectedly contains 1e-4 rows",
    )
    checks.check(
        t8_coarse.get("v048_runner_invoked_for_this_evidence") is True,
        "T=8 coarse runner provenance missing",
    )
    t8_groups = t8_coarse.get("groups", {})
    checks.check(
        {key for key, value in t8_groups.items() if value.get("complete_three_step_group")}
        == {
            "rA:double_pendulum",
            "rA:four_link",
            "rA:single_pendulum",
            "rA_half:single_pendulum",
        },
        "T=8 complete group set changed",
    )
    checks.check(
        t8_groups.get("rA_half:double_pendulum", {}).get("ok_row_count") == 0,
        "T=8 rA_half double-pendulum failure boundary changed",
    )
    checks.check(
        t8_groups.get("rA:slider_crank", {}).get("ok_row_count") == 2
        and t8_groups.get("rA_half:slider_crank", {}).get("ok_row_count") == 2,
        "T=8 slider-crank partial success boundary changed",
    )
    checks.check(t8_selected.get("artifact_present") is True, "T=8 selected candidate artifact missing")
    checks.check(
        t8_selected.get("artifact_status") == "executed_full_T8_selected_coarse_trio_not_promoted",
        "T=8 selected candidate status changed",
    )
    checks.check(t8_selected.get("form") == "rA", "T=8 selected candidate form changed")
    checks.check(t8_selected.get("model") == "double_pendulum", "T=8 selected candidate model changed")
    checks.check(t8_selected.get("selected_t_end") == 8.0, "T=8 selected candidate horizon changed")
    checks.check(t8_selected.get("selected_reference_h") == 0.001, "T=8 selected candidate reference h changed")
    checks.check(
        t8_selected.get("selected_step_sizes") == [0.02, 0.01, 0.005],
        "T=8 selected candidate h-grid changed",
    )
    checks.check(t8_selected.get("estimated_reference_steps") == 8000, "T=8 selected reference steps changed")
    checks.check(
        t8_selected.get("estimated_candidate_steps") == [400, 800, 1600],
        "T=8 selected candidate step counts changed",
    )
    checks.check(t8_selected.get("source_policy_time_window_selected") is True, "T=8 selected time marker missing")
    checks.check(t8_selected.get("source_policy_reference_h_selected") is True, "T=8 selected reference marker missing")
    checks.check(t8_selected.get("selected_coarse_trio") is True, "T=8 selected coarse-trio marker missing")
    checks.check(t8_selected.get("full_public_grid_selected") is False, "T=8 selected overclaims full public grid")
    checks.check(t8_selected.get("full_T8_policy_completed") is False, "T=8 selected overclaims full T8 completion")
    checks.check(t8_selected.get("source_policy_1e_4_included") is False, "T=8 selected unexpectedly includes 1e-4")
    checks.check(t8_selected.get("row_count") == 3, "T=8 selected row count changed")
    checks.check(t8_selected.get("ok_row_count") == 3, "T=8 selected ok count changed")
    checks.check(t8_selected.get("source_policy_candidate_rows_completed") == 3, "T=8 selected completed rows changed")
    checks.check(t8_selected.get("source_policy_rows_closed_by_this_evidence") == 0, "T=8 selected overcloses rows")
    checks.check(t8_selected.get("counts_as_full_public_grid_source_policy") is False, "T=8 selected overclaims source policy")
    checks.check(t8_selected.get("counts_as_complete_work_precision_curve") is False, "T=8 selected overclaims work/precision")
    checks.check(t8_selected.get("promotion_ready") is False, "T=8 selected unexpectedly promotion ready")
    checks.check(
        t8_selected.get("b4_b7_can_close_from_this_evidence") is False,
        "T=8 selected overcloses B4/B7",
    )
    checks.check(
        t8_selected.get("canonical_hi2022_output_untouched_by_writer") is True,
        "T=8 selected canonical-output marker missing",
    )
    checks.check(
        "selected coarse trio is not the full encoded HI2022 public step family"
        in t8_selected.get("promotion_blockers", []),
        "T=8 selected missing coarse-trio promotion blocker",
    )
    checks.check(
        t8_matrix.get("schema") == "hi2022-t8-selected-candidate-matrix-preflight-v1",
        "T=8 selected candidate matrix schema changed",
    )
    checks.check(
        t8_matrix.get("status") == "preflight_ready_existing_selected_candidate_matrix_incomplete",
        "T=8 selected candidate matrix status changed",
    )
    checks.check(t8_matrix.get("script_exists") is True, "T=8 selected candidate matrix script missing")
    checks.check(t8_matrix.get("models") == ["single_pendulum", "double_pendulum", "four_link", "slider_crank"], "T=8 matrix models changed")
    checks.check(t8_matrix.get("forms") == ["rA_half", "rA"], "T=8 matrix forms changed")
    checks.check(t8_matrix.get("expected_shard_count") == 8, "T=8 matrix shard count changed")
    checks.check(t8_matrix.get("completed_shard_count") == 7, "T=8 matrix completed shard count changed")
    checks.check(t8_matrix.get("existing_artifact_count") == 8, "T=8 matrix existing artifact count changed")
    checks.check(
        set(t8_matrix.get("completed_shards", []))
        == {
            "rA_half:single_pendulum",
            "rA_half:four_link",
            "rA_half:slider_crank",
            "rA:single_pendulum",
            "rA:double_pendulum",
            "rA:four_link",
            "rA:slider_crank",
        },
        "T=8 matrix completed shard set changed",
    )
    checks.check(
        set(t8_matrix.get("missing_or_unexecuted_shards", []))
        == {"rA_half:double_pendulum"},
        "T=8 matrix missing shard set changed",
    )
    checks.check(t8_matrix.get("command_count") == 8, "T=8 matrix command count changed")
    checks.check(t8_matrix.get("all_commands_avoid_1e_4") is True, "T=8 matrix commands unexpectedly include 1e-4")
    checks.check(t8_matrix.get("source_policy_1e_4_required") is False, "T=8 matrix requires 1e-4")
    checks.check(t8_matrix.get("heavy_numerical_run_invoked") is False, "T=8 matrix preflight invoked heavy run")
    checks.check(t8_matrix.get("run_v047_invoked") is False, "T=8 matrix preflight invoked run_v047")
    checks.check(t8_matrix.get("v048_runner_invoked") is False, "T=8 matrix preflight invoked v048 runner")
    checks.check(
        t8_matrix.get("source_policy_rows_closed_by_preflight") == 0,
        "T=8 matrix preflight overcloses rows",
    )
    checks.check(
        t8_matrix.get("source_policy_rows_closed_by_existing_candidates") == 0,
        "T=8 matrix existing candidates overclose rows",
    )
    checks.check(
        t8_matrix.get("counts_as_complete_work_precision_curve") is False,
        "T=8 matrix overclaims complete work/precision curve",
    )
    checks.check(
        t8_matrix.get("b4_b7_can_close_from_preflight") is False,
        "T=8 matrix overcloses B4/B7",
    )
    for gap in [
        "matrix preflight only enumerates isolated candidate shard commands",
        "existing selected candidates remain coarse-trio diagnostics, not full public-grid source-policy rows",
        "full source-policy promotion still requires executed rows, work metrics, and a figure policy over accepted rows",
    ]:
        checks.check(gap in t8_matrix.get("promotion_gap", []), f"T=8 matrix missing gap: {gap}")
    matrix_shards = t8_matrix.get("shards", [])
    checks.check(isinstance(matrix_shards, list) and len(matrix_shards) == 8, "T=8 matrix shard rows changed")
    observed_matrix = {item.get("shard_id"): item for item in matrix_shards if isinstance(item, dict)}
    checks.check(set(observed_matrix) == {
        "rA_half:double_pendulum",
        "rA_half:four_link",
        "rA_half:single_pendulum",
        "rA_half:slider_crank",
        "rA:double_pendulum",
        "rA:four_link",
        "rA:single_pendulum",
        "rA:slider_crank",
    }, "T=8 matrix shard ids changed")
    for shard_id, shard in observed_matrix.items():
        checks.check(shard.get("contains_1e_4") is False, f"{shard_id} command includes 1e-4")
        checks.check(shard.get("requires_source_policy_1e_4_opt_in") is False, f"{shard_id} requires 1e-4 opt-in")
        checks.check(shard.get("requires_heavy_run_opt_in") is True, f"{shard_id} missing heavy-run opt-in marker")
        checks.check(shard.get("counts_as_preflight_only") is True, f"{shard_id} lost preflight-only marker")
        checks.check(shard.get("source_policy_rows_closed_by_this_evidence") == 0, f"{shard_id} overcloses rows")
        checks.check(shard.get("b4_b7_can_close_from_this_shard") is False, f"{shard_id} overcloses B4/B7")
        checks.check("--execute" in shard.get("command", ""), f"{shard_id} command missing execute flag")
        checks.check("--allow-source-policy-1e-4" not in shard.get("command", ""), f"{shard_id} command includes 1e-4 opt-in")
    completed_shard_ids = {
        "rA_half:single_pendulum",
        "rA_half:four_link",
        "rA_half:slider_crank",
        "rA:single_pendulum",
        "rA:double_pendulum",
        "rA:four_link",
        "rA:slider_crank",
    }
    for shard_id in completed_shard_ids:
        completed_shard = observed_matrix.get(shard_id, {})
        checks.check(
            completed_shard.get("artifact_status") == "executed_full_T8_selected_coarse_trio_not_promoted",
            f"{shard_id} completed shard status changed",
        )
        checks.check(completed_shard.get("ok_row_count") == 3, f"{shard_id} completed shard ok count changed")
        checks.check(
            completed_shard.get("full_public_grid_selected") is False,
            f"{shard_id} completed shard overclaims full grid",
        )
        checks.check(
            completed_shard.get("counts_as_complete_work_precision_curve") is False,
            f"{shard_id} completed shard overclaims work/precision",
        )
    for shard_id in [
        "rA_half:double_pendulum",
    ]:
        checks.check(
            observed_matrix.get(shard_id, {}).get("artifact_status")
            == "partial_or_failed_full_T8_source_policy_candidate_not_promoted",
            f"{shard_id} should be partial/failed, not promoted",
        )
        checks.check(observed_matrix.get(shard_id, {}).get("ok_row_count") == 1, f"{shard_id} ok count changed")
    checks.check(
        figure_scope.get("status") == "demote_hi2022_from_b4_b7_source_policy_figures",
        "HI2022 figure-scope demotion status changed",
    )
    checks.check(
        figure_scope.get("source_policy_rows_closed_by_hi2022") == 0,
        "HI2022 figure-scope decision overcloses rows",
    )
    checks.check(
        figure_scope.get("counts_as_clean_work_precision_figure") is False,
        "HI2022 figure-scope decision overclaims clean work/precision figure",
    )
    checks.check(
        figure_scope.get("b4_b7_can_close_from_hi2022") is False,
        "HI2022 figure-scope decision overcloses B4/B7",
    )
    checks.check(
        "source-policy external-superiority curve" in figure_scope.get("forbidden_figure_use", []),
        "HI2022 figure-scope decision missing forbidden use",
    )
    for key in [
        "bounded_T0p1_rows_ok",
        "bounded_eight_form_model_groups_complete",
        "full_T8_public_policy_required",
        "selected_T8_candidate_artifact_present",
        "hi2022_b4_b7_figure_scope_demotion_recorded",
    ]:
        checks.check(criteria.get(key) is True, f"criterion {key} changed")
    for key in [
        "full_T8_public_policy_completed",
        "source_policy_reproduction_closed",
        "velocity_mapping_and_error_norm_closed",
        "runtime_iteration_metric_tied_to_source_policy_rows",
        "rerun_or_independent_verification_artifact_present",
        "selected_T8_candidate_promoted_to_source_policy",
    ]:
        checks.check(criteria.get(key) is False, f"criterion {key} unexpectedly closed")
    checks.check(
        criteria.get("explicit_demotion_recorded_for_hi2022") is True,
        "HI2022 demotion criterion not recorded",
    )
    checks.check(decision.get("can_close_hi2022_b2_requirement_now") is False, "HI2022 B2 requirement overclosed")
    checks.check(queue_policy.get("batch_id") == "hi2022_halfimplicit_full_policy_decision", "queue batch changed")
    checks.check(queue_policy.get("queue_status") == "parallel_ready_after_policy_selection", "queue status changed")
    checks.check(queue_policy.get("models") == ["single_pendulum", "double_pendulum", "four_link", "slider_crank"], "queue models changed")
    checks.check(queue_policy.get("public_forms") == ["rA_half", "rA"], "queue forms changed")
    checks.check(queue_policy.get("time_horizon") == 8.0, "queue horizon changed")
    checks.check(queue_policy.get("parallel_shard_count") == 8, "queue shard count changed")
    checks.check(queue_policy.get("source_policy_1e_4_required") is False, "queue requires default 1e-4")
    checks.check(workload.get("full_T8_estimated_public_steps_total") == 1243200, "full workload estimate changed")
    checks.check(workload.get("bounded_T0p1_estimated_public_steps_total") == 1080, "bounded workload estimate changed")
    checks.check(workload.get("full_T8_evidence_status") == "not_run_by_default", "full workload status changed")
    checks.check(workload.get("bounded_T0p1_evidence_status") == "will_run", "bounded workload status changed")

    expected = {
        (1, "four_link", "hi2022_rA", "rA:four_link"),
        (2, "double_pendulum", "hi2022_rA_half", "rA_half:double_pendulum"),
        (3, "four_link", "hi2022_rA_half", "rA_half:four_link"),
    }
    observed = {
        (row.get("row_index"), row.get("example"), row.get("method"), row.get("bounded_group_key"))
        for row in rows
    }
    checks.check(observed == expected, "audited active rows changed")
    for row in rows:
        checks.check(row.get("bounded_row_count") == 3, f"row {row.get('row_index')} bounded row count changed")
        checks.check(row.get("bounded_ok_row_count") == 3, f"row {row.get('row_index')} bounded ok count changed")
        checks.check(row.get("bounded_h_values") == [0.005, 0.01, 0.02], f"row {row.get('row_index')} h-grid changed")
        checks.check(row.get("bounded_t_end") == 0.1, f"row {row.get('row_index')} horizon changed")
        checks.check(row.get("bounded_reference_h") == 0.001, f"row {row.get('row_index')} reference h changed")
        checks.check(row.get("source_policy_reproduction") is False, f"row {row.get('row_index')} source-policy closed")
        checks.check(row.get("full_T8_source_policy_completed") is False, f"row {row.get('row_index')} full T8 closed")
        checks.check(row.get("source_policy_closed") is False, f"row {row.get('row_index')} source-policy closed")
        checks.check(row.get("external_superiority_ready") is False, f"row {row.get('row_index')} claim-ready")

    execution = audit.get("execution_policy", {})
    checks.check(execution.get("read_only_existing_artifacts") is True, "audit lost read-only marker")
    checks.check(execution.get("default_1e_4_required") is False, "audit requires default 1e-4")
    checks.check(execution.get("heavy_numerical_run_invoked") is False, "audit invoked heavy run")
    checks.check(execution.get("run_v047_invoked") is False, "audit invoked run_v047")
    checks.check(execution.get("v048_runner_invoked") is False, "audit invoked v048 runner")

    for token in [
        "Status: **bounded T=0.1 rows complete; full T=8 source-policy rows not closed**.",
        "Active B2 flagged HI2022 rows: `3`.",
        "Active/demoted B2 rows after HI2022 demotion: `0/3`.",
        "Bounded rows ok: `24/24`.",
        "Bounded form/model groups complete: `8/8`.",
        "Full T=8 source policy completed: `False`.",
        "T=8 coarse horizon rows ok: `18/24`.",
        "T=8 coarse complete form/model groups: `4/8`.",
        "T=8 coarse source-policy reproduction: `False`.",
        "T=8 selected candidate rows ok: `3/3`.",
        "T=8 selected candidate full public grid: `False`.",
        "T=8 selected candidate matrix preflight: `7/8` completed, commands `8`.",
        "T=8 selected candidate matrix source-policy rows closed: `0`.",
        "HI2022 B4/B7 figure-scope decision: `demote_hi2022_from_b4_b7_source_policy_figures`.",
        "B4/B7 can close from HI2022: `False`.",
        "Source-policy reproduction rows: `0/3`.",
        "Source-policy dynamic-order examples: `0/4`.",
        "Can close HI2022 B2 requirement now: `False`.",
        "The new T=8 coarse-horizon sanity rows are useful failure/stability evidence",
        "The selected T=8 candidate adds a finer rA double-pendulum shard",
        "## T=8 Coarse-Horizon Sanity Rows",
        "## T=8 Selected Candidate",
        "## T=8 Selected Candidate Matrix Preflight",
        "Status: `preflight_ready_existing_selected_candidate_matrix_incomplete`.",
        "Script exists: `True`.",
        "Expected/completed shards: `8/7`.",
        "Commands avoid 1e-4: `True`.",
        "Heavy numerical run invoked by preflight: `False`.",
        "Source-policy rows closed by preflight: `0`.",
        "B4/B7 can close from preflight: `False`.",
        "`rA_half:double_pendulum`",
        "`rA:slider_crank`",
        "Status: `executed_full_T8_selected_coarse_trio_not_promoted`.",
        "source-policy rows closed by this evidence: `0`.",
        "B4/B7 can close from selected candidate: `False`.",
        "The HI2022 rows remain bounded pilot diagnostics, not source-policy external-superiority evidence.",
    ]:
        checks.check(token in audit_md, f"markdown missing token: {token}")

    if checks.errors:
        print("HI2022 source-policy row audit validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("HI2022 source-policy row audit validation: PASS")
    print("active_b2_flagged_rows=3")
    print("active_after_demotion=0")
    print("demoted_b2_flagged_rows=3")
    print("bounded_rows=24/24")
    print("bounded_groups=8/8")
    print("t8_coarse_rows=18/24")
    print("t8_coarse_complete_groups=4/8")
    print("full_T8_policy_completed=False")
    print("source_policy_reproduction_rows=0/3")
    print("can_close_hi2022_b2_requirement_now=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
