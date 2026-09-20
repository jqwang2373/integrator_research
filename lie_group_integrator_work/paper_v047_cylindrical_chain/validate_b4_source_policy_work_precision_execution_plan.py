#!/usr/bin/env python3
"""Validate the B4 source-policy work/precision execution plan."""

from __future__ import annotations

import json
import csv
import math
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
from paper_paths import LATEX, package_path as manuscript_path
EXPECTED_LANES = {
    "ra2021_source_policy_work_precision",
    "tfe_source_policy_work_precision",
    "hi2022_full_T8_work_precision",
    "vp2024_source_code_path_work_precision",
}
EXPECTED_RA2021_FORMS = ["rA", "rp", "reps"]


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


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def pair_orders(rows: list[dict[str, str]], metric: str) -> list[float]:
    pairs = sorted(
        [(float(row["h"]), float(row[metric])) for row in rows if row.get("status") == "ok"],
        reverse=True,
    )
    return [
        math.log(e0 / e1) / math.log(h0 / h1)
        for (h0, e0), (h1, e1) in zip(pairs, pairs[1:])
    ]


def blocker_by_id(blocker_gate: dict[str, Any], blocker_id: str) -> dict[str, Any]:
    for item in blocker_gate.get("blockers", []):
        if isinstance(item, dict) and item.get("id") == blocker_id:
            return item
    raise ValueError(f"blocker {blocker_id} not found")


def main() -> int:
    checks = Checks()
    try:
        plan = read_json(PAPER / "B4_SOURCE_POLICY_WORK_PRECISION_EXECUTION_PLAN.json")
        plan_md = read_text(PAPER / "B4_SOURCE_POLICY_WORK_PRECISION_EXECUTION_PLAN.md")
        blocker = read_json(PAPER / "CMAME_BLOCKER_CLOSURE_GATE.json")
        b4_b7 = read_json(PAPER / "B4_B7_NON_SUPERIORITY_ROUTE_AUDIT.json")
        row_ledger = read_json(PAPER / "SOURCE_POLICY_ROW_CLOSURE_LEDGER.json")
        tfe_literal_work = read_json(PAPER / "TFE_ALGORITHM_LITERAL_WORK_PRECISION_AUDIT.json")
        tfe_demotion_audit = read_json(PAPER / "TFE_B4_B7_SOURCE_POLICY_DEMOTION_AUDIT.json")
        figure_set = read_json(PAPER / "CMAME_FIGURE_SET_AUDIT.json")
    except Exception as exc:  # noqa: BLE001
        print(f"b4 source-policy work/precision execution plan validation: FAIL\n- {exc}")
        return 1

    b4 = blocker_by_id(blocker, "B4")
    b7 = blocker_by_id(blocker, "B7")
    b4_audit = b4_b7.get("b4", {})
    b7_audit = b4_b7.get("b7", {})
    current = plan.get("current_evidence", {})
    execution = plan.get("execution_policy", {})
    contract = plan.get("publication_grade_acceptance_contract", {})
    lane_summary = plan.get("execution_lane_summary", {})
    preflight = plan.get("ra2021_launch_preflight", {})
    hi2022_preflight = plan.get("hi2022_launch_preflight", {})
    ra2021_cli_contract = preflight.get("runner_cli_contract", {})
    hi2022_cli_contract = hi2022_preflight.get("runner_cli_contract", {})
    executed_shard = plan.get("ra2021_executed_shard_evidence", {})
    gauss6_local = plan.get("gauss6_local_source_policy_evidence", {})
    closed_loop_same_window = plan.get("ra2021_closed_loop_same_window_public_work_precision_evidence", {})
    double_candidate = plan.get("ra2021_double_local_source_policy_candidate_evidence", {})
    hi2022_t8_candidate = plan.get("hi2022_full_t8_source_policy_candidate_evidence", {})
    hi2022_demotion = plan.get("hi2022_b4_b7_figure_scope_demotion_evidence", {})
    tfe_demotion = plan.get("tfe_b4_b7_figure_scope_demotion_evidence", {})
    tfe_runner_preflight = plan.get("tfe_source_policy_runner_equivalence_preflight_evidence", {})
    lanes = {item.get("lane_id"): item for item in plan.get("execution_lanes", []) if isinstance(item, dict)}

    checks.check(
        plan.get("schema") == "b4-source-policy-work-precision-execution-plan-v1",
        "schema changed",
    )
    checks.check(
        plan.get("status") == "execution_plan_ready_b4_b7_remain_open",
        "status changed",
    )
    checks.check(plan.get("submission_ready") is False, "plan overclaims submission readiness")
    checks.check(plan.get("submission_standard_met") is False, "plan overclaims submission standard")
    checks.check(plan.get("b4_can_close_now") is False, "plan overcloses B4")
    checks.check(plan.get("b7_can_close_now") is False, "plan overcloses B7")
    checks.check(plan.get("b6_can_close_now") is False, "plan overcloses B6")
    checks.check(plan.get("route_b_closes_b2") is True, "Route B should still close B2")
    checks.check(plan.get("route_b_closes_b4") is False, "Route B incorrectly closes B4")
    checks.check(plan.get("route_b_closes_b7") is False, "Route B incorrectly closes B7")
    checks.check(plan.get("open_blockers_after_plan") == [], "open blocker set changed")

    checks.check(current.get("common_reference_order_error_matrix_closed") is True, "common-reference matrix lost")
    checks.check(current.get("direct_nonlocal_velocity_order_wins") == 40, "order win count changed")
    checks.check(current.get("direct_nonlocal_velocity_order_comparisons") == 40, "order comparison count changed")
    checks.check(current.get("direct_nonlocal_finest_velocity_error_wins") == 40, "error win count changed")
    checks.check(
        current.get("direct_nonlocal_finest_velocity_error_comparisons") == 40,
        "error comparison count changed",
    )
    checks.check(
        current.get("source_policy_rows_closed")
        == b4_audit.get("source_policy_execution_rows_closed")
        == 0,
        "source-policy rows unexpectedly closed",
    )
    checks.check(
        current.get("source_policy_rows_total")
        == b4_audit.get("source_policy_execution_total_rows")
        == 40,
        "source-policy total row count changed",
    )
    checks.check(
        current.get("source_policy_flagged_rows")
        == row_ledger.get("coverage", {}).get("flagged_row_count")
        == 15,
        "flagged source-policy row count changed",
    )
    checks.check(current.get("external_superiority_ready_rows") == 0, "external-ready rows unexpectedly present")
    checks.check(
        current.get("source_policy_publication_grade_work_precision_open") is True,
        "B4 publication-grade work/precision should remain open",
    )
    diagnostic = current.get("diagnostic_work_precision_rows", {})
    checks.check(diagnostic.get("tfe_same_test_rows") == 18, "TFE same-test row count changed")
    checks.check(diagnostic.get("tfe_same_test_ok_rows") == 18, "TFE same-test ok row count changed")
    checks.check(diagnostic.get("tfe_same_test_source_policy_rows_completed") == 0, "TFE same-test overclosed rows")
    checks.check(diagnostic.get("tfe_algorithm_literal_rows") == 12, "TFE algorithm-literal row count changed")
    checks.check(diagnostic.get("tfe_algorithm_literal_summary_rows") == 4, "TFE algorithm-literal summary changed")
    checks.check(
        diagnostic.get("tfe_algorithm_literal_runtime_proxy_available") is False,
        "TFE algorithm-literal runtime proxy unexpectedly available",
    )
    checks.check(
        current.get("tfe_algorithm_literal_work_precision_source_policy_rows_completed")
        == tfe_literal_work.get("source_policy_rows_completed")
        == 0,
        "TFE algorithm-literal overclosed source-policy rows",
    )
    checks.check(
        current.get("tfe_algorithm_literal_runtime_proxy_available")
        == tfe_literal_work.get("runtime_proxy_available")
        is False,
        "TFE algorithm-literal runtime proxy boundary changed",
    )
    checks.check(
        current.get("tfe_runner_equivalence_preflight_status")
        == tfe_runner_preflight.get("status")
        == "preflight_ready_runner_equivalence_open",
        "TFE runner-equivalence preflight status changed",
    )
    checks.check(
        current.get("tfe_runner_equivalence_preflight_rows_closed")
        == tfe_runner_preflight.get("source_policy_rows_closed_by_preflight")
        == 0,
        "TFE runner-equivalence preflight overclosed rows",
    )
    checks.check(
        current.get("tfe_runner_equivalence_preflight_can_close_lane")
        == tfe_runner_preflight.get("can_close_tfe_lane_from_preflight")
        is False,
        "TFE runner-equivalence preflight overcloses lane",
    )
    checks.check(
        current.get("tfe_b4_b7_rows_demoted_related_work_proxy_for_current_claim")
        == tfe_demotion.get("demoted_related_work_proxy_rows_for_current_claim")
        == tfe_demotion_audit.get("demoted_related_work_proxy_rows_for_current_claim")
        == 16,
        "TFE current-claim demotion row count changed",
    )
    checks.check(
        current.get("tfe_current_claim_requires_source_policy_execution")
        == tfe_demotion.get("current_claim_requires_tfe_source_policy_execution")
        == tfe_demotion_audit.get("current_claim_requires_tfe_source_policy_execution")
        is False,
        "TFE current claim unexpectedly requires source-policy execution",
    )
    checks.check(
        current.get("ra2021_public_baseline_progress", {}).get("order_groups_completed") == 12,
        "RA2021 public order group count changed",
    )
    checks.check(
        current.get("ra2021_public_baseline_progress", {}).get("timing_rows_completed") == 12,
        "RA2021 public timing row count changed",
    )

    checks.check(
        contract.get("contract_id") == "b4-source-policy-work-precision-publication-contract-v1",
        "publication contract id changed",
    )
    checks.check(contract.get("plan_only_closes_rows") is False, "contract overcloses rows")
    checks.check(contract.get("required_to_close_b4") == b4.get("required_to_close"), "B4 required items drifted")
    checks.check(contract.get("required_to_close_b7") == b7.get("required_to_close"), "B7 required items drifted")
    checks.check(contract.get("current_figure_set_b7_closed") is figure_set.get("b7_closed") is True, "B7 figure status changed")
    checks.check(
        contract.get("current_figure_set_supports_common_reference_diagnostics_only")
        == b7_audit.get("figure_set_supports_common_reference_diagnostics_only")
        is True,
        "figure-set diagnostic boundary changed",
    )
    for required in [
        "source-policy time horizon, step grid, reference, output variables, and norm are declared",
        "error/order rows and work metrics come from the same accepted run records",
        "diagnostic common-reference rows are not promoted into source-policy figures",
    ]:
        checks.check(required in contract.get("required_row_properties", []), f"contract missing row rule: {required}")

    checks.check(execution.get("read_only_existing_artifacts") is True, "plan should be read-only")
    checks.check(execution.get("default_1e_4_required") is False, "default 1e-4 guard changed")
    checks.check(
        execution.get("source_policy_1e_4_requires_explicit_flag") is True,
        "explicit 1e-4 opt-in guard missing",
    )
    checks.check(execution.get("heavy_numerical_run_invoked") is False, "plan invoked heavy run")
    checks.check(execution.get("run_v047_invoked") is False, "plan invoked run_v047")
    checks.check(execution.get("v048_runner_invoked") is False, "plan invoked v048 runner")
    checks.check(
        execution.get("next_heavy_source_policy_execution_requires_user_opt_in") is True,
        "heavy execution opt-in marker missing",
    )
    checks.check(execution.get("parallel_ready_shards_without_default_1e_4") == 20, "parallel shard count changed")

    checks.check(set(lanes) == EXPECTED_LANES, "execution lane set changed")
    checks.check(lane_summary.get("lane_count") == 4, "lane count changed")
    checks.check(lane_summary.get("ready_to_launch_after_explicit_opt_in_count") == 2, "ready lane count changed")
    checks.check(lane_summary.get("not_ready_lane_count") == 2, "not-ready lane count changed")
    checks.check(lane_summary.get("plan_only_closed_rows") == 0, "plan-only closed rows changed")
    checks.check(lane_summary.get("source_policy_rows_closed_after_plan") == 0, "plan overclosed rows")
    checks.check(lane_summary.get("source_policy_rows_total") == 40, "plan source-policy total rows changed")
    checks.check(
        preflight.get("schema") == "b4-ra2021-source-policy-launch-preflight-v1",
        "RA2021 launch preflight schema changed",
    )
    checks.check(
        preflight.get("status") == "ready_not_run_requires_user_opt_in",
        "RA2021 launch preflight status changed",
    )
    checks.check(preflight.get("read_only_preflight") is True, "RA2021 preflight must be read-only")
    checks.check(
        preflight.get("ready_to_execute_without_code_changes") is True,
        "RA2021 preflight should be executable without code changes",
    )
    checks.check(preflight.get("runner_files_available") is True, "RA2021 runner files missing")
    checks.check(preflight.get("launch_command_count") == 5, "RA2021 launch command count changed")
    checks.check(
        preflight.get("all_launch_commands_require_explicit_1e_4_opt_in") is True,
        "RA2021 launch commands lost explicit 1e-4 guard",
    )
    checks.check(preflight.get("heavy_numerical_run_invoked") is False, "RA2021 preflight invoked heavy run")
    checks.check(preflight.get("run_v047_invoked") is False, "RA2021 preflight invoked run_v047")
    checks.check(preflight.get("v048_runner_invoked") is False, "RA2021 preflight invoked v048 runner")
    checks.check(preflight.get("source_policy_rows_closed_by_preflight") == 0, "RA2021 preflight overclosed rows")
    checks.check(preflight.get("b4_can_close_after_preflight_only") is False, "RA2021 preflight overcloses B4")
    checks.check(preflight.get("b7_can_close_after_preflight_only") is False, "RA2021 preflight overcloses B7")
    runner_files = {item.get("path"): item for item in preflight.get("runner_files", [])}
    for runner in [
        "../v048_cross_paper_same_test_benchmarks/run_v048.py",
        "../v048_cross_paper_same_test_benchmarks/run_ra2021_double_order_shard.py",
        "../v048_cross_paper_same_test_benchmarks/run_ra2021_timing_shard.py",
        "../v048_cross_paper_same_test_benchmarks/run_public_closed_loop_shard.py",
    ]:
        checks.check(runner_files.get(runner, {}).get("exists") is True, f"RA2021 runner missing: {runner}")
    commands = {item.get("id"): item.get("command", "") for item in preflight.get("launch_commands", [])}
    expected_command_ids = {
        "ra2021_public_timing_all_forms_models",
        "gauss6_public_single_source_policy_trio",
        "ra2021_double_order_all_forms",
        "gauss6_public_four_link_source_policy_trio",
        "gauss6_public_slider_crank_source_policy_trio",
    }
    checks.check(set(commands) == expected_command_ids, "RA2021 launch command ids changed")
    checks.check(
        all("--allow-source-policy-1e-4" in command for command in commands.values()),
        "not every RA2021 launch command has explicit 1e-4 opt-in",
    )
    checks.check(
        "--gauss6-public-step-sizes 1e-2,1e-3,1e-4" in commands.get("gauss6_public_single_source_policy_trio", ""),
        "Gauss6 public single source-policy h trio changed",
    )
    checks.check(
        "--model four_link --step-sizes 1e-2,1e-3,1e-4"
        in commands.get("gauss6_public_four_link_source_policy_trio", ""),
        "four-link source-policy shard command changed",
    )
    checks.check(
        "--model slider_crank --step-sizes 1e-2,1e-3,1e-4"
        in commands.get("gauss6_public_slider_crank_source_policy_trio", ""),
        "slider-crank source-policy shard command changed",
    )
    checks.check(
        ra2021_cli_contract.get("schema") == "b4-ra2021-runner-cli-contract-v1",
        "RA2021 CLI contract schema changed",
    )
    checks.check(
        ra2021_cli_contract.get("status") == "runner_cli_contract_satisfied",
        "RA2021 CLI contract not satisfied",
    )
    checks.check(ra2021_cli_contract.get("runner_contract_count") == 4, "RA2021 runner contract count changed")
    checks.check(ra2021_cli_contract.get("command_contract_count") == 5, "RA2021 command contract count changed")
    checks.check(ra2021_cli_contract.get("all_contracts_satisfied") is True, "RA2021 CLI contracts not all satisfied")
    checks.check(
        ra2021_cli_contract.get("heavy_numerical_run_invoked") is False,
        "RA2021 CLI contract invoked heavy run",
    )
    checks.check(
        ra2021_cli_contract.get("source_policy_rows_closed_by_preflight") == 0,
        "RA2021 CLI contract overclosed source-policy rows",
    )
    for item in ra2021_cli_contract.get("runner_option_contracts", []):
        checks.check(item.get("exists") is True, f"RA2021 runner source missing: {item.get('path')}")
        checks.check(item.get("missing_tokens") == [], f"RA2021 runner source token missing: {item.get('path')}")
        checks.check(item.get("contract_satisfied") is True, f"RA2021 runner source contract open: {item.get('path')}")
    for item in ra2021_cli_contract.get("launch_command_contracts", []):
        checks.check(item.get("missing_tokens") == [], f"RA2021 launch command missing token: {item.get('id')}")
        checks.check(item.get("present_forbidden_tokens") == [], f"RA2021 launch command has forbidden token: {item.get('id')}")
        checks.check(item.get("contract_satisfied") is True, f"RA2021 launch command contract open: {item.get('id')}")

    checks.check(
        hi2022_preflight.get("schema") == "b4-hi2022-source-policy-launch-preflight-v1",
        "HI2022 launch preflight schema changed",
    )
    checks.check(
        hi2022_preflight.get("status") == hi2022_demotion.get("t8_selected_candidate_matrix_status"),
        "HI2022 launch preflight status drifted from source row audit",
    )
    checks.check(hi2022_preflight.get("read_only_preflight") is True, "HI2022 preflight must be read-only")
    checks.check(
        hi2022_preflight.get("ready_to_execute_without_code_changes") is True,
        "HI2022 preflight should be executable without code changes",
    )
    checks.check(hi2022_preflight.get("runner_files_available") is True, "HI2022 runner file missing")
    hi_runner_files = {item.get("path"): item for item in hi2022_preflight.get("runner_files", [])}
    checks.check(
        hi_runner_files.get(
            "../v048_cross_paper_same_test_benchmarks/run_hi2022_full_t8_source_policy_candidate.py",
            {},
        ).get("exists")
        is True,
        "HI2022 selected-candidate runner missing",
    )
    checks.check(hi2022_preflight.get("launch_command_count") == 8, "HI2022 launch command count changed")
    checks.check(hi2022_preflight.get("expected_shard_count") == 8, "HI2022 expected shard count changed")
    checks.check(hi2022_preflight.get("completed_shard_count") == 7, "HI2022 completed shard count changed")
    checks.check(
        set(hi2022_preflight.get("completed_shards", []))
        == {
            "rA_half:single_pendulum",
            "rA_half:four_link",
            "rA_half:slider_crank",
            "rA:single_pendulum",
            "rA:double_pendulum",
            "rA:four_link",
            "rA:slider_crank",
        },
        "HI2022 completed shard changed",
    )
    checks.check(
        set(hi2022_preflight.get("missing_or_unexecuted_shards", []))
        == {"rA_half:double_pendulum"},
        "HI2022 missing shard set changed",
    )
    checks.check(hi2022_preflight.get("all_launch_commands_avoid_1e_4") is True, "HI2022 commands include 1e-4")
    checks.check(hi2022_preflight.get("source_policy_1e_4_required") is False, "HI2022 unexpectedly requires 1e-4")
    checks.check(
        hi2022_preflight.get("all_launch_commands_require_heavy_run_opt_in") is True,
        "HI2022 heavy-run opt-in marker missing",
    )
    checks.check(hi2022_preflight.get("heavy_numerical_run_invoked") is False, "HI2022 preflight invoked heavy run")
    checks.check(hi2022_preflight.get("run_v047_invoked") is False, "HI2022 preflight invoked run_v047")
    checks.check(hi2022_preflight.get("v048_runner_invoked") is False, "HI2022 preflight invoked v048 runner")
    checks.check(
        hi2022_preflight.get("source_policy_rows_closed_by_preflight") == 0,
        "HI2022 preflight overclosed rows",
    )
    checks.check(
        hi2022_preflight.get("source_policy_rows_closed_by_existing_candidates") == 0,
        "HI2022 existing candidates overclosed rows",
    )
    checks.check(
        hi2022_preflight.get("counts_as_complete_work_precision_curve") is False,
        "HI2022 preflight overclaims complete work/precision curve",
    )
    checks.check(
        hi2022_preflight.get("b4_can_close_after_preflight_only") is False,
        "HI2022 preflight overcloses B4",
    )
    checks.check(
        hi2022_preflight.get("b7_can_close_after_preflight_only") is False,
        "HI2022 preflight overcloses B7",
    )
    hi_commands = {
        item.get("shard_id"): item.get("command", "")
        for item in hi2022_preflight.get("launch_commands", [])
        if isinstance(item, dict)
    }
    checks.check(
        set(hi_commands)
        == {
            "rA_half:double_pendulum",
            "rA_half:four_link",
            "rA_half:single_pendulum",
            "rA_half:slider_crank",
            "rA:double_pendulum",
            "rA:four_link",
            "rA:single_pendulum",
            "rA:slider_crank",
        },
        "HI2022 launch command shard ids changed",
    )
    for shard_id, command in hi_commands.items():
        checks.check("--execute" in command, f"HI2022 launch command missing execute flag: {shard_id}")
        checks.check("--allow-source-policy-1e-4" not in command, f"HI2022 launch command includes 1e-4 opt-in: {shard_id}")
        checks.check("run_hi2022_full_t8_source_policy_candidate.py" in command, f"HI2022 launch command script changed: {shard_id}")
    checks.check(
        hi2022_cli_contract.get("schema") == "b4-hi2022-runner-cli-contract-v1",
        "HI2022 CLI contract schema changed",
    )
    checks.check(
        hi2022_cli_contract.get("status") == "runner_cli_contract_satisfied",
        "HI2022 CLI contract not satisfied",
    )
    checks.check(hi2022_cli_contract.get("runner_contract_count") == 1, "HI2022 runner contract count changed")
    checks.check(hi2022_cli_contract.get("command_contract_count") == 8, "HI2022 command contract count changed")
    checks.check(hi2022_cli_contract.get("all_contracts_satisfied") is True, "HI2022 CLI contracts not all satisfied")
    checks.check(
        hi2022_cli_contract.get("heavy_numerical_run_invoked") is False,
        "HI2022 CLI contract invoked heavy run",
    )
    checks.check(
        hi2022_cli_contract.get("source_policy_rows_closed_by_preflight") == 0,
        "HI2022 CLI contract overclosed source-policy rows",
    )
    for item in hi2022_cli_contract.get("runner_option_contracts", []):
        checks.check(item.get("exists") is True, f"HI2022 runner source missing: {item.get('path')}")
        checks.check(item.get("missing_tokens") == [], f"HI2022 runner source token missing: {item.get('path')}")
        checks.check(item.get("contract_satisfied") is True, f"HI2022 runner source contract open: {item.get('path')}")
    for item in hi2022_cli_contract.get("launch_command_contracts", []):
        checks.check(item.get("missing_tokens") == [], f"HI2022 launch command missing token: {item.get('id')}")
        checks.check(item.get("present_forbidden_tokens") == [], f"HI2022 launch command has forbidden token: {item.get('id')}")
        checks.check(item.get("contract_satisfied") is True, f"HI2022 launch command contract open: {item.get('id')}")
    checks.check(
        executed_shard.get("schema") == "b4-ra2021-executed-source-policy-shard-evidence-v2",
        "executed RA2021 shard schema changed",
    )
    checks.check(
        executed_shard.get("status") == "all_public_baseline_source_policy_shards_completed_not_promoted",
        "executed RA2021 shard status changed",
    )
    checks.check(executed_shard.get("exists") is True, "executed RA2021 shard CSVs missing")
    checks.check(executed_shard.get("expected_forms") == EXPECTED_RA2021_FORMS, "RA2021 expected forms changed")
    checks.check(executed_shard.get("completed_forms") == EXPECTED_RA2021_FORMS, "RA2021 completed forms changed")
    checks.check(executed_shard.get("expected_form_count") == 3, "RA2021 expected form count changed")
    checks.check(executed_shard.get("completed_form_count") == 3, "RA2021 completed form count changed")
    checks.check(executed_shard.get("row_count") == 9, "executed shard aggregate row count changed")
    checks.check(executed_shard.get("ok_row_count") == 9, "executed shard aggregate ok row count changed")
    checks.check(
        executed_shard.get("source_suite") == ["ra2021_taves_kissel_negrut"],
        "executed shard suite changed",
    )
    checks.check(executed_shard.get("model") == ["double_pendulum"], "executed shard model changed")
    checks.check(executed_shard.get("mode") == ["dynamics"], "executed shard mode changed")
    checks.check(executed_shard.get("shared_h_values") == [0.01, 0.002, 0.001], "executed shard h grid changed")
    checks.check(executed_shard.get("reference_h_values") == [0.0001], "executed shard reference h changed")
    shards = executed_shard.get("shards", [])
    checks.check(isinstance(shards, list) and len(shards) == 3, "executed shard list changed")
    shard_by_form = {item.get("form"): item for item in shards if isinstance(item, dict)}
    checks.check(list(shard_by_form) == EXPECTED_RA2021_FORMS, "executed shard form order changed")
    for form in EXPECTED_RA2021_FORMS:
        shard = shard_by_form.get(form, {})
        checks.check(shard.get("exists") is True, f"executed RA2021 shard CSV missing: {form}")
        shard_path = (manuscript_path(str(shard.get("path")))).resolve()
        shard_rows = read_csv(shard_path)
        checks.check(shard.get("row_count") == len(shard_rows) == 3, f"executed shard row count changed: {form}")
        checks.check(shard.get("ok_row_count") == 3, f"executed shard ok row count changed: {form}")
        checks.check(shard.get("source_suite") == ["ra2021_taves_kissel_negrut"], f"executed shard suite changed: {form}")
        checks.check({row.get("form") for row in shard_rows} == {form}, f"executed shard CSV form changed: {form}")
        checks.check(shard.get("model") == ["double_pendulum"], f"executed shard model changed: {form}")
        checks.check(shard.get("mode") == ["dynamics"], f"executed shard mode changed: {form}")
        checks.check(shard.get("h_values") == [0.01, 0.002, 0.001], f"executed shard h grid changed: {form}")
        checks.check(shard.get("reference_h_values") == [0.0001], f"executed shard reference h changed: {form}")
        checks.check(
            shard.get("public_double_order_policy_values") == ["True"],
            f"executed shard public-policy marker changed: {form}",
        )
        checks.check(
            len(shard.get("runtime_sec_values", [])) == 3
            and all(float(value) > 0.0 for value in shard.get("runtime_sec_values", [])),
            f"executed shard runtime values missing: {form}",
        )
        checks.check(
            len(shard.get("avg_iteration_values", [])) == 3
            and all(float(value) > 0.0 for value in shard.get("avg_iteration_values", [])),
            f"executed shard iteration values missing: {form}",
        )
        checks.check(
            shard.get("position_pair_orders") == pair_orders(shard_rows, "pos_final_linf"),
            f"position pair orders changed: {form}",
        )
        checks.check(
            shard.get("velocity_pair_orders") == pair_orders(shard_rows, "vel_final_linf"),
            f"velocity pair orders changed: {form}",
        )
        checks.check(
            shard.get("acceleration_pair_orders") == pair_orders(shard_rows, "acc_final_linf"),
            f"acceleration pair orders changed: {form}",
        )
    checks.check(
        executed_shard.get("velocity_pair_orders_by_form", {}).get("rA")
        == shard_by_form.get("rA", {}).get("velocity_pair_orders"),
        "aggregate velocity pair orders changed",
    )
    checks.check(
        executed_shard.get("baseline_source_policy_rows_completed_by_shards") == 9,
        "executed shard baseline row count changed",
    )
    checks.check(executed_shard.get("heavy_numerical_run_invoked") is True, "executed shard run marker missing")
    checks.check(
        executed_shard.get("builder_invoked_heavy_numerical_run") is False,
        "builder should not claim it invoked a heavy run",
    )
    checks.check(executed_shard.get("run_v047_invoked") is False, "executed shard invoked run_v047")
    checks.check(
        executed_shard.get("counts_as_source_policy_baseline_shards") is True,
        "executed shards should count as completed baseline shards",
    )
    checks.check(
        executed_shard.get("counts_as_gauss6_fullva_local_source_policy_row") is False,
        "executed shard overclaims local Gauss6 row",
    )
    checks.check(
        executed_shard.get("counts_as_complete_work_precision_curve") is False,
        "executed shard overclaims complete work/precision curve",
    )
    checks.check(
        executed_shard.get("source_policy_rows_closed_by_this_evidence") == 0,
        "executed shard evidence overcloses source-policy rows",
    )
    checks.check(
        executed_shard.get("source_policy_rows_closed_by_this_shard") == 0,
        "executed shard overcloses source-policy rows",
    )
    checks.check(executed_shard.get("b4_can_close_from_this_evidence") is False, "executed shard overcloses B4")
    checks.check(executed_shard.get("b7_can_close_from_this_evidence") is False, "executed shard overcloses B7")
    checks.check(executed_shard.get("b4_can_close_from_this_shard") is False, "executed shard overcloses B4")
    checks.check(executed_shard.get("b7_can_close_from_this_shard") is False, "executed shard overcloses B7")

    checks.check(
        gauss6_local.get("schema") == "b4-gauss6-local-source-policy-evidence-v1",
        "Gauss6 local evidence schema changed",
    )
    checks.check(
        gauss6_local.get("status")
        == "partial_local_source_policy_evidence_single_complete_closed_loop_residual_only_not_promoted",
        "Gauss6 local evidence status changed",
    )
    single = gauss6_local.get("single_public_horizon_rows", {})
    checks.check(
        gauss6_local.get("single_public_horizon_step_trio_completed") is True,
        "Gauss6 single public-horizon trio should be complete",
    )
    single_rows = read_csv((manuscript_path(str(single.get("path")))).resolve())
    checks.check(single.get("row_count") == len(single_rows) == 3, "Gauss6 single row count changed")
    checks.check(single.get("ok_row_count") == 3, "Gauss6 single ok row count changed")
    checks.check(single.get("failed_row_count") == 0, "Gauss6 single unexpectedly has failed rows")
    checks.check(single.get("method") == ["Gauss6/FullVA"], "Gauss6 single method changed")
    checks.check(single.get("row_type") == ["public_horizon_single_pendulum_tranche"], "Gauss6 single row type changed")
    checks.check(single.get("h_values") == [0.01, 0.001, 0.0001], "Gauss6 single h grid changed")
    checks.check(single.get("reference_h_values") == [0.001], "Gauss6 single reference h changed")
    checks.check(single.get("public_policy_time_window_values") == ["True"], "Gauss6 single public time flag changed")
    checks.check(single.get("public_policy_h_values") == ["True"], "Gauss6 single public h flag changed")
    checks.check(
        len(single.get("runtime_sec_values", [])) == 3
        and all(float(value) > 0.0 for value in single.get("runtime_sec_values", [])),
        "Gauss6 single runtime values missing",
    )
    combined = gauss6_local.get("closed_loop_combined_shards", [])
    legacy_reference_nesting = gauss6_local.get("closed_loop_legacy_reference_nesting_shards", [])
    h1e4 = gauss6_local.get("closed_loop_h1e4_standalone_shards", [])
    checks.check(isinstance(combined, list) and len(combined) == 2, "Gauss6 closed-loop combined shard count changed")
    checks.check(
        isinstance(legacy_reference_nesting, list) and len(legacy_reference_nesting) == 2,
        "Gauss6 legacy reference-nesting shard count changed",
    )
    checks.check(isinstance(h1e4, list) and len(h1e4) == 2, "Gauss6 closed-loop h1e4 shard count changed")
    combined_by_model = {item.get("model"): item for item in combined if isinstance(item, dict)}
    legacy_by_model = {item.get("model"): item for item in legacy_reference_nesting if isinstance(item, dict)}
    h1e4_by_model = {item.get("model"): item for item in h1e4 if isinstance(item, dict)}
    for model in ["four_link", "slider_crank"]:
        shard = combined_by_model.get(model, {})
        rows = read_csv((manuscript_path(str(shard.get("path")))).resolve())
        checks.check(shard.get("row_count") == len(rows) == 3, f"Gauss6 combined row count changed: {model}")
        checks.check(shard.get("ok_row_count") == 3, f"Gauss6 combined ok count changed: {model}")
        checks.check(shard.get("failed_row_count") == 0, f"Gauss6 combined failure count changed: {model}")
        checks.check(shard.get("h_values") == [0.01, 0.001, 0.0001], f"Gauss6 combined h grid changed: {model}")
        checks.check(shard.get("reference_h_values") == [0.001], f"Gauss6 combined reference h changed: {model}")
        checks.check(shard.get("public_policy_time_window_values") == ["True"], f"Gauss6 combined public T flag changed: {model}")
        checks.check(shard.get("public_policy_h_values") == ["True"], f"Gauss6 combined public h flag changed: {model}")
        legacy = legacy_by_model.get(model, {})
        checks.check(
            legacy.get("row_count") == 2 and legacy.get("failed_row_count") == 1,
            f"Gauss6 legacy reference-nesting diagnostic changed: {model}",
        )
        checks.check(
            any(str(status).startswith("failed:ValueError:reference h=0.001") for status in legacy.get("failed_statuses", [])),
            f"Gauss6 legacy failure mode changed: {model}",
        )
        checks.check(
            shard.get("row_type") == ["public_horizon_closed_loop_kinematic_reaction"],
            f"Gauss6 combined row type changed: {model}",
        )
        standalone = h1e4_by_model.get(model, {})
        standalone_rows = read_csv((manuscript_path(str(standalone.get("path")))).resolve())
        checks.check(
            standalone.get("row_count") == len(standalone_rows) == 1,
            f"Gauss6 h1e4 standalone row count changed: {model}",
        )
        checks.check(standalone.get("ok_row_count") == 1, f"Gauss6 h1e4 standalone ok count changed: {model}")
        checks.check(standalone.get("failed_row_count") == 0, f"Gauss6 h1e4 standalone failed: {model}")
        checks.check(standalone.get("h_values") == [0.0001], f"Gauss6 h1e4 standalone h changed: {model}")
    checks.check(gauss6_local.get("closed_loop_combined_ok_rows") == 6, "Gauss6 combined ok aggregate changed")
    checks.check(gauss6_local.get("closed_loop_combined_failed_rows") == 0, "Gauss6 combined failure aggregate changed")
    checks.check(
        gauss6_local.get("closed_loop_legacy_reference_nesting_failed_rows") == 2,
        "Gauss6 legacy reference-nesting failure aggregate changed",
    )
    checks.check(
        gauss6_local.get("closed_loop_h1e4_standalone_ok_models") == 2,
        "Gauss6 h1e4 standalone ok aggregate changed",
    )
    checks.check(
        gauss6_local.get("closed_loop_public_step_trios_completed") is True,
        "Gauss6 closed-loop public step trios should be complete in latest shards",
    )
    checks.check(
        gauss6_local.get("closed_loop_rows_are_dynamic_work_precision") is False,
        "Gauss6 closed-loop rows overclaim dynamic work/precision",
    )
    checks.check(
        gauss6_local.get("counts_as_partial_local_source_policy_evidence") is True,
        "Gauss6 partial local evidence marker missing",
    )
    checks.check(
        gauss6_local.get("counts_as_b4_accepted_source_policy_rows") is False,
        "Gauss6 local evidence overclaims B4 accepted rows",
    )
    checks.check(
        gauss6_local.get("counts_as_complete_ra2021_work_precision_curve") is False,
        "Gauss6 local evidence overclaims complete RA2021 work/precision",
    )
    checks.check(
        gauss6_local.get("source_policy_rows_closed_by_this_evidence") == 0,
        "Gauss6 local evidence overcloses source-policy rows",
    )
    checks.check(gauss6_local.get("b4_can_close_from_this_evidence") is False, "Gauss6 evidence overcloses B4")
    checks.check(gauss6_local.get("b7_can_close_from_this_evidence") is False, "Gauss6 evidence overcloses B7")

    checks.check(
        closed_loop_same_window.get("schema")
        == "b4-ra2021-closed-loop-same-window-public-work-precision-evidence-v1",
        "RA2021 closed-loop same-window evidence schema changed",
    )
    checks.check(
        closed_loop_same_window.get("status")
        == "same_window_public_work_precision_available_reference_caveat_not_external_superiority",
        "RA2021 closed-loop same-window evidence status changed",
    )
    same_window_summary_path = (manuscript_path(str(closed_loop_same_window.get("summary_path")))).resolve()
    same_window_rows_path = (manuscript_path(str(closed_loop_same_window.get("rows_path")))).resolve()
    same_window_summary_rows_path = (manuscript_path(str(closed_loop_same_window.get("summary_rows_path")))).resolve()
    same_window_summary = read_json(same_window_summary_path)
    same_window_rows = read_csv(same_window_rows_path)
    same_window_summary_rows = read_csv(same_window_summary_rows_path)
    checks.check(closed_loop_same_window.get("summary_exists") is True, "same-window summary JSON missing")
    checks.check(closed_loop_same_window.get("rows_exists") is True, "same-window rows CSV missing")
    checks.check(closed_loop_same_window.get("summary_rows_exists") is True, "same-window summary CSV missing")
    checks.check(
        closed_loop_same_window.get("row_count")
        == same_window_summary.get("row_count")
        == len(same_window_rows)
        == 24,
        "same-window row count changed",
    )
    checks.check(
        closed_loop_same_window.get("ok_row_count")
        == same_window_summary.get("ok_row_count")
        == 24,
        "same-window ok row count changed",
    )
    checks.check(
        closed_loop_same_window.get("summary_row_count")
        == same_window_summary.get("summary_row_count")
        == len(same_window_summary_rows)
        == 8,
        "same-window summary row count changed",
    )
    checks.check(
        set(closed_loop_same_window.get("models", [])) == {"four_link", "slider_crank"},
        "same-window model set changed",
    )
    checks.check(closed_loop_same_window.get("public_forms") == ["rA", "rp", "reps"], "same-window forms changed")
    checks.check(closed_loop_same_window.get("t_end") == 0.1, "same-window T changed")
    checks.check(closed_loop_same_window.get("step_sizes") == [0.1, 0.05, 0.025], "same-window h values changed")
    checks.check(closed_loop_same_window.get("reference_h") == 0.0125, "same-window reference h changed")
    checks.check(closed_loop_same_window.get("public_work_precision_available_count") == 2, "same-window available count changed")
    checks.check(
        set(closed_loop_same_window.get("public_work_precision_available_examples", []))
        == {"four_link", "slider_crank"},
        "same-window available example set changed",
    )
    checks.check(closed_loop_same_window.get("public_work_precision_missing_count") == 0, "same-window missing count changed")
    checks.check(
        closed_loop_same_window.get("local_true_dynamic_order_available_count") == 2,
        "same-window local dynamic order count changed",
    )
    checks.check(
        closed_loop_same_window.get("strict_common_reference_error_columns") is False,
        "same-window overclaims strict common-reference columns",
    )
    checks.check(
        closed_loop_same_window.get("reference_alignment_status")
        == "mixed_reference_family_requires_manuscript_caveat",
        "same-window reference caveat changed",
    )
    checks.check(
        closed_loop_same_window.get("external_superiority_claim") is False,
        "same-window overclaims external superiority",
    )
    checks.check(
        closed_loop_same_window.get("accepted_external_dynamic_order_examples") == [],
        "same-window unexpectedly accepts external dynamic order examples",
    )
    checks.check(
        closed_loop_same_window.get("counts_as_bounded_same_window_diagnostic") is True,
        "same-window diagnostic marker missing",
    )
    checks.check(
        closed_loop_same_window.get("counts_as_source_policy_reproduction") is False,
        "same-window overclaims source-policy reproduction",
    )
    checks.check(
        closed_loop_same_window.get("counts_as_b4_accepted_source_policy_rows") is False,
        "same-window overclaims B4 accepted rows",
    )
    checks.check(
        closed_loop_same_window.get("counts_as_complete_ra2021_work_precision_curve") is False,
        "same-window overclaims complete RA2021 work/precision",
    )
    checks.check(
        closed_loop_same_window.get("source_policy_rows_closed_by_this_evidence") == 0,
        "same-window overcloses source-policy rows",
    )
    checks.check(
        closed_loop_same_window.get("b4_can_close_from_this_evidence") is False,
        "same-window overcloses B4",
    )
    checks.check(
        closed_loop_same_window.get("b7_can_close_from_this_evidence") is False,
        "same-window overcloses B7",
    )
    for gap in [
        "same-window public work/precision rows are available for four-link and slider-crank",
        "local and public error columns use different reference families",
        "bounded T=0.1 diagnostic rows are not the RA2021 T=3 source-policy dynamic-order rows",
        "source-policy figures still need promoted rows with one reference/output/runtime policy",
    ]:
        checks.check(gap in closed_loop_same_window.get("promotion_gap", []), f"same-window missing gap: {gap}")
    same_window_models = closed_loop_same_window.get("model_summaries", {})
    checks.check(set(same_window_models) == {"four_link", "slider_crank"}, "same-window model summaries changed")
    for model, min_vel_order in [("four_link", 6.0), ("slider_crank", 7.0)]:
        model_summary = same_window_models.get(model, {})
        checks.check(model_summary.get("local_summary_present") is True, f"{model} same-window local summary missing")
        checks.check(model_summary.get("public_summary_count") == 3, f"{model} same-window public count changed")
        checks.check(
            model_summary.get("public_methods") == ["rA-public-dynamics", "reps-public-dynamics", "rp-public-dynamics"],
            f"{model} same-window methods changed",
        )
        checks.check(
            isinstance(model_summary.get("local_vel_observed_order"), (int, float))
            and model_summary.get("local_vel_observed_order") > min_vel_order,
            f"{model} same-window local velocity order changed",
        )
        checks.check(
            model_summary.get("external_superiority_claim_allowed") is False,
            f"{model} same-window overclaims external superiority",
        )

    checks.check(
        double_candidate.get("schema") == "b4-ra2021-double-local-source-policy-candidate-evidence-v1",
        "RA2021 double local candidate evidence schema changed",
    )
    checks.check(
        double_candidate.get("status") == "executed_order_below_acceptance_not_promoted",
        "RA2021 double local candidate evidence status changed",
    )
    candidate_summary_path = (manuscript_path(str(double_candidate.get("summary_path")))).resolve()
    candidate_rows_path = (manuscript_path(str(double_candidate.get("rows_path")))).resolve()
    candidate_validator_path = (manuscript_path(str(double_candidate.get("validator_path")))).resolve()
    candidate_summary = read_json(candidate_summary_path)
    candidate_rows = read_csv(candidate_rows_path)
    checks.check(double_candidate.get("summary_exists") is True, "double candidate summary missing")
    checks.check(double_candidate.get("rows_exists") is True, "double candidate rows missing")
    checks.check(
        double_candidate.get("validator_exists") is True and candidate_validator_path.exists(),
        "double candidate validator missing",
    )
    checks.check(
        double_candidate.get("runner_schema")
        == candidate_summary.get("schema")
        == "ra2021-double-local-source-policy-candidate-v1",
        "double candidate runner schema changed",
    )
    checks.check(
        double_candidate.get("runner_status")
        == candidate_summary.get("status")
        == "executed_isolated_source_policy_candidate",
        "double candidate runner status changed",
    )
    checks.check(double_candidate.get("execution_mode") == "candidate", "double candidate execution mode changed")
    checks.check(double_candidate.get("heavy_numerical_run_invoked") is True, "double candidate heavy-run marker missing")
    checks.check(
        double_candidate.get("builder_invoked_heavy_numerical_run") is False,
        "B4 builder should not claim it invoked the double candidate run",
    )
    checks.check(double_candidate.get("reference_status") == "ok", "double candidate reference status changed")
    checks.check(double_candidate.get("reference_cache_exists") is True, "double candidate reference cache missing")
    checks.check(float(double_candidate.get("reference_runtime_sec")) > 0.0, "double candidate reference runtime missing")
    checks.check(double_candidate.get("estimated_reference_steps") == 30000, "double candidate reference step count changed")
    checks.check(double_candidate.get("source_policy_contract_selected") is True, "double candidate source-policy contract lost")
    checks.check(double_candidate.get("source_policy_time_window_selected") is True, "double candidate time window changed")
    checks.check(double_candidate.get("source_policy_step_trio_selected") is True, "double candidate h trio changed")
    checks.check(double_candidate.get("source_policy_reference_h_selected") is True, "double candidate reference h changed")
    checks.check(double_candidate.get("selected_step_sizes") == [0.01, 0.002, 0.001], "double candidate selected h changed")
    checks.check(double_candidate.get("selected_reference_h") == 0.0001, "double candidate selected reference h changed")
    checks.check(double_candidate.get("selected_t_end") == 3.0, "double candidate horizon changed")
    checks.check(double_candidate.get("row_count") == len(candidate_rows) == 3, "double candidate row count changed")
    checks.check(double_candidate.get("ok_row_count") == 3, "double candidate ok row count changed")
    checks.check(double_candidate.get("source_policy_candidate_rows_completed") == 3, "double candidate completed rows changed")
    checks.check(double_candidate.get("h_values") == [0.01, 0.002, 0.001], "double candidate h values changed")
    checks.check(
        len(double_candidate.get("runtime_sec_values", [])) == 3
        and all(float(value) > 0.0 for value in double_candidate.get("runtime_sec_values", [])),
        "double candidate runtime values missing",
    )
    checks.check(
        len(double_candidate.get("total_newton_iteration_values", [])) == 3
        and all(float(value) > 0.0 for value in double_candidate.get("total_newton_iteration_values", [])),
        "double candidate Newton iteration values missing",
    )
    checks.check(
        len(double_candidate.get("max_endpoint_constraint_norm_values", [])) == 3
        and all(float(value) >= 0.0 for value in double_candidate.get("max_endpoint_constraint_norm_values", [])),
        "double candidate endpoint constraint values missing",
    )
    checks.check(
        len(double_candidate.get("max_endpoint_velocity_constraint_norm_values", [])) == 3
        and all(float(value) >= 0.0 for value in double_candidate.get("max_endpoint_velocity_constraint_norm_values", [])),
        "double candidate endpoint velocity constraint values missing",
    )
    checks.check(
        double_candidate.get("constraint_threshold_satisfied_values") == ["False", "True"],
        "double candidate constraint threshold boundary changed",
    )
    checks.check(
        double_candidate.get("constraint_threshold_failed_h_values") == [0.01],
        "double candidate constraint-failed h values changed",
    )
    checks.check(
        double_candidate.get("position_pair_orders") == pair_orders(candidate_rows, "pos_traj_linf"),
        "double candidate position pair orders changed",
    )
    checks.check(
        double_candidate.get("velocity_pair_orders") == pair_orders(candidate_rows, "vel_traj_linf"),
        "double candidate velocity pair orders changed",
    )
    checks.check(
        double_candidate.get("minimum_position_pair_order") == min(pair_orders(candidate_rows, "pos_traj_linf")),
        "double candidate minimum position pair order changed",
    )
    checks.check(
        double_candidate.get("minimum_velocity_pair_order") == min(pair_orders(candidate_rows, "vel_traj_linf")),
        "double candidate minimum velocity pair order changed",
    )
    checks.check(
        float(double_candidate.get("finest_pair_position_order")) < 0.25
        and float(double_candidate.get("finest_pair_velocity_order")) < 0.25,
        "double candidate finest-pair floor diagnostic changed",
    )
    checks.check(
        double_candidate.get("source_policy_order_acceptance_threshold") == 5.5,
        "double candidate order threshold changed",
    )
    checks.check(
        double_candidate.get("source_policy_pos_observed_order")
        == candidate_summary.get("source_policy_pos_observed_order"),
        "double candidate position order drifted",
    )
    checks.check(
        double_candidate.get("source_policy_vel_observed_order")
        == candidate_summary.get("source_policy_vel_observed_order"),
        "double candidate velocity order drifted",
    )
    checks.check(
        float(double_candidate.get("source_policy_pos_observed_order")) < 5.5
        and float(double_candidate.get("source_policy_vel_observed_order")) < 5.5,
        "double candidate unexpectedly meets order threshold",
    )
    checks.check(
        double_candidate.get("source_policy_order_acceptance_satisfied") is False,
        "double candidate overclaims source-policy order acceptance",
    )
    for mode in [
        "aggregate_observed_order_below_5p5_threshold",
        "position_pair_order_below_5p5_threshold",
        "velocity_pair_order_below_5p5_threshold",
        "at_least_one_candidate_row_fails_endpoint_constraint_threshold",
    ]:
        checks.check(mode in double_candidate.get("low_order_failure_modes", []), f"double candidate missing mode: {mode}")
    checks.check(double_candidate.get("promotion_ready") is False, "double candidate unexpectedly promotion ready")
    checks.check(
        "observed source-policy order is below sixth-order acceptance (pos=2.148, vel=2.463)"
        in double_candidate.get("promotion_blockers", []),
        "double candidate missing order blocker",
    )
    checks.check(
        double_candidate.get("source_policy_reproduction_rows_promoted") == 0,
        "double candidate unexpectedly promoted rows",
    )
    checks.check(
        double_candidate.get("counts_as_executed_local_candidate") is True,
        "double candidate executed marker missing",
    )
    checks.check(
        double_candidate.get("counts_as_b4_accepted_source_policy_rows") is False,
        "double candidate overclaims B4 accepted rows",
    )
    checks.check(
        double_candidate.get("counts_as_complete_work_precision_curve") is False,
        "double candidate overclaims complete work/precision",
    )
    checks.check(
        double_candidate.get("source_policy_rows_closed_by_this_evidence") == 0,
        "double candidate overcloses source-policy rows",
    )
    checks.check(double_candidate.get("b4_can_close_from_this_evidence") is False, "double candidate overcloses B4")
    checks.check(double_candidate.get("b7_can_close_from_this_evidence") is False, "double candidate overcloses B7")

    checks.check(
        hi2022_t8_candidate.get("schema") == "b4-hi2022-full-t8-source-policy-candidate-evidence-v2",
        "HI2022 full T8 candidate evidence schema changed",
    )
    checks.check(
        hi2022_t8_candidate.get("status") == "selected_candidate_matrix_partially_executed_not_promoted",
        "HI2022 full T8 candidate status changed",
    )
    hi2022_validator_path = (manuscript_path(str(hi2022_t8_candidate.get("validator_path")))).resolve()
    checks.check(
        hi2022_t8_candidate.get("validator_exists") is True and hi2022_validator_path.exists(),
        "HI2022 T8 validator missing",
    )
    checks.check(
        hi2022_t8_candidate.get("runner_schema") == ["hi2022-full-t8-source-policy-candidate-v1"],
        "HI2022 T8 runner schema changed",
    )
    checks.check(
        set(hi2022_t8_candidate.get("runner_statuses", []))
        == {
            "executed_full_T8_selected_coarse_trio_not_promoted",
            "partial_or_failed_full_T8_source_policy_candidate_not_promoted",
        },
        "HI2022 T8 runner status changed",
    )
    checks.check(hi2022_t8_candidate.get("execution_phase") == ["candidate"], "HI2022 T8 phase changed")
    checks.check(hi2022_t8_candidate.get("heavy_numerical_run_invoked") is True, "HI2022 T8 heavy-run marker missing")
    checks.check(
        hi2022_t8_candidate.get("builder_invoked_heavy_numerical_run") is False,
        "B4 builder should not claim it invoked the HI2022 T8 candidate run",
    )
    checks.check(
        hi2022_t8_candidate.get("canonical_v048_main_invoked") is False,
        "HI2022 T8 candidate should not invoke canonical v048 main",
    )
    checks.check(
        hi2022_t8_candidate.get("canonical_hi2022_output_untouched_by_writer") is True,
        "HI2022 T8 canonical-output protection marker missing",
    )
    checks.check(hi2022_t8_candidate.get("forms") == ["rA", "rA_half"], "HI2022 T8 forms changed")
    checks.check(
        hi2022_t8_candidate.get("models") == ["double_pendulum", "four_link", "single_pendulum", "slider_crank"],
        "HI2022 T8 models changed",
    )
    checks.check(hi2022_t8_candidate.get("summary_artifact_count") == 8, "HI2022 T8 summary artifact count changed")
    checks.check(hi2022_t8_candidate.get("rows_artifact_count") == 8, "HI2022 T8 rows artifact count changed")
    checks.check(hi2022_t8_candidate.get("expected_shard_count") == 8, "HI2022 T8 expected shard count changed")
    checks.check(hi2022_t8_candidate.get("completed_shard_count") == 7, "HI2022 T8 completed shard count changed")
    checks.check(
        hi2022_t8_candidate.get("partial_or_failed_shards") == ["rA_half:double_pendulum"],
        "HI2022 T8 partial shard set changed",
    )
    checks.check(hi2022_t8_candidate.get("missing_artifact_shards") == [], "HI2022 T8 missing artifacts changed")
    checks.check(hi2022_t8_candidate.get("source_policy_time_window_selected") is True, "HI2022 T8 marker missing")
    checks.check(hi2022_t8_candidate.get("source_policy_reference_h_selected") is True, "HI2022 reference marker missing")
    checks.check(hi2022_t8_candidate.get("selected_coarse_trio") is True, "HI2022 coarse trio marker missing")
    checks.check(hi2022_t8_candidate.get("full_public_grid_selected") is False, "HI2022 full grid overclaimed")
    checks.check(hi2022_t8_candidate.get("full_T8_policy_completed") is False, "HI2022 full T8 overclosed")
    checks.check(hi2022_t8_candidate.get("source_policy_1e_4_included") is False, "HI2022 T8 unexpectedly includes 1e-4")
    checks.check(hi2022_t8_candidate.get("selected_step_sizes") == [0.02, 0.01, 0.005], "HI2022 T8 h trio changed")
    checks.check(hi2022_t8_candidate.get("selected_reference_h_values") == [0.001], "HI2022 T8 reference h changed")
    checks.check(hi2022_t8_candidate.get("selected_t_end_values") == [8.0], "HI2022 T8 horizon changed")
    checks.check(hi2022_t8_candidate.get("estimated_reference_steps_values") == [8000], "HI2022 T8 reference step estimate changed")
    checks.check(hi2022_t8_candidate.get("estimated_candidate_steps_values") == [400, 800, 1600], "HI2022 T8 candidate steps changed")
    checks.check(hi2022_t8_candidate.get("reference_statuses") == ["ok"], "HI2022 T8 reference status changed")
    checks.check(
        len(hi2022_t8_candidate.get("reference_runtime_sec_values", [])) == 8
        and all(float(value) > 0.0 for value in hi2022_t8_candidate.get("reference_runtime_sec_values", [])),
        "HI2022 T8 reference runtime missing",
    )
    checks.check(hi2022_t8_candidate.get("row_count") == 24, "HI2022 T8 row count changed")
    checks.check(hi2022_t8_candidate.get("ok_row_count") == 22, "HI2022 T8 ok row count changed")
    checks.check(hi2022_t8_candidate.get("source_policy_candidate_rows_completed") == 22, "HI2022 T8 completed rows changed")
    checks.check(hi2022_t8_candidate.get("selected_step_trio_completed_count") == 7, "HI2022 T8 selected trio count changed")
    checks.check(hi2022_t8_candidate.get("h_values") == [0.02, 0.01, 0.005], "HI2022 T8 h values changed")
    checks.check(
        len(hi2022_t8_candidate.get("runtime_sec_values", [])) == 22
        and all(float(value) > 0.0 for value in hi2022_t8_candidate.get("runtime_sec_values", [])),
        "HI2022 T8 runtime values missing",
    )
    checks.check(
        len(hi2022_t8_candidate.get("avg_iteration_values", [])) == 22
        and all(float(value) > 0.0 for value in hi2022_t8_candidate.get("avg_iteration_values", [])),
        "HI2022 T8 average iterations missing",
    )
    checks.check(
        len(hi2022_t8_candidate.get("position_pair_orders_by_shard", {})) == 8,
        "HI2022 T8 position pair-order shard map changed",
    )
    checks.check(
        hi2022_t8_candidate.get("source_policy_reproduction_rows_promoted") == 0,
        "HI2022 T8 unexpectedly promoted rows",
    )
    checks.check(
        hi2022_t8_candidate.get("counts_as_executed_full_T8_candidate") is False,
        "HI2022 T8 overclaims complete matrix execution",
    )
    checks.check(
        hi2022_t8_candidate.get("counts_as_full_public_grid_source_policy") is False,
        "HI2022 T8 overclaims full public-grid source-policy",
    )
    checks.check(
        hi2022_t8_candidate.get("counts_as_b4_accepted_source_policy_rows") is False,
        "HI2022 T8 overclaims B4 accepted rows",
    )
    checks.check(
        hi2022_t8_candidate.get("counts_as_complete_work_precision_curve") is False,
        "HI2022 T8 overclaims complete work/precision",
    )
    checks.check(
        hi2022_t8_candidate.get("source_policy_rows_closed_by_this_evidence") == 0,
        "HI2022 T8 overcloses source-policy rows",
    )
    checks.check(hi2022_t8_candidate.get("promotion_ready") is False, "HI2022 T8 unexpectedly promotion ready")
    checks.check(
        "selected coarse trio is not the full encoded HI2022 public step family"
        in hi2022_t8_candidate.get("promotion_blockers", []),
        "HI2022 T8 missing coarse-trio blocker",
    )
    checks.check(hi2022_t8_candidate.get("b4_can_close_from_this_evidence") is False, "HI2022 T8 overcloses B4")
    checks.check(hi2022_t8_candidate.get("b7_can_close_from_this_evidence") is False, "HI2022 T8 overcloses B7")

    checks.check(
        hi2022_demotion.get("schema") == "b4-hi2022-b4-b7-figure-scope-demotion-evidence-v1",
        "HI2022 B4/B7 demotion schema changed",
    )
    checks.check(
        hi2022_demotion.get("status") == "demote_hi2022_from_b4_b7_source_policy_figures",
        "HI2022 B4/B7 demotion status changed",
    )
    checks.check(
        hi2022_demotion.get("source_audit") == "HI2022_SOURCE_POLICY_ROW_AUDIT.json",
        "HI2022 demotion source audit changed",
    )
    checks.check(
        hi2022_demotion.get("source_audit_status")
        == "bounded_T0p1_rows_complete_full_T8_source_policy_rows_not_closed",
        "HI2022 demotion source audit status changed",
    )
    checks.check(hi2022_demotion.get("bounded_rows_ok") == 24, "HI2022 demotion bounded ok rows changed")
    checks.check(hi2022_demotion.get("bounded_rows_total") == 24, "HI2022 demotion bounded total rows changed")
    checks.check(hi2022_demotion.get("t8_coarse_rows_ok") == 18, "HI2022 demotion T8 coarse ok rows changed")
    checks.check(hi2022_demotion.get("t8_coarse_rows_total") == 24, "HI2022 demotion T8 coarse total rows changed")
    checks.check(
        hi2022_demotion.get("t8_coarse_complete_form_model_groups") == 4,
        "HI2022 demotion T8 coarse complete groups changed",
    )
    checks.check(hi2022_demotion.get("t8_coarse_group_count") == 8, "HI2022 demotion T8 group count changed")
    checks.check(
        hi2022_demotion.get("t8_selected_candidate_status")
        == "executed_full_T8_selected_coarse_trio_not_promoted",
        "HI2022 demotion selected candidate status changed",
    )
    checks.check(hi2022_demotion.get("t8_selected_candidate_rows_ok") == 3, "HI2022 demotion selected ok rows changed")
    checks.check(
        hi2022_demotion.get("t8_selected_candidate_rows_total") == 3,
        "HI2022 demotion selected total rows changed",
    )
    checks.check(
        hi2022_demotion.get("t8_selected_candidate_full_public_grid_selected") is False,
        "HI2022 demotion selected candidate overclaims full grid",
    )
    checks.check(
        hi2022_demotion.get("t8_selected_candidate_source_policy_rows_closed") == 0,
        "HI2022 demotion selected candidate overcloses rows",
    )
    checks.check(
        hi2022_demotion.get("t8_selected_candidate_matrix_status")
        == "preflight_ready_existing_selected_candidate_matrix_incomplete",
        "HI2022 selected-candidate matrix status changed",
    )
    checks.check(
        hi2022_demotion.get("t8_selected_candidate_matrix_expected_shards") == 8,
        "HI2022 selected-candidate matrix expected shard count changed",
    )
    checks.check(
        hi2022_demotion.get("t8_selected_candidate_matrix_completed_shards") == 7,
        "HI2022 selected-candidate matrix completed shard count changed",
    )
    checks.check(
        hi2022_demotion.get("t8_selected_candidate_matrix_command_count") == 8,
        "HI2022 selected-candidate matrix command count changed",
    )
    checks.check(
        hi2022_demotion.get("t8_selected_candidate_matrix_commands_avoid_1e_4") is True,
        "HI2022 selected-candidate matrix commands unexpectedly include 1e-4",
    )
    checks.check(
        hi2022_demotion.get("t8_selected_candidate_matrix_heavy_run_invoked") is False,
        "HI2022 selected-candidate matrix invoked heavy run",
    )
    checks.check(
        hi2022_demotion.get("t8_selected_candidate_matrix_rows_closed") == 0,
        "HI2022 selected-candidate matrix overcloses rows",
    )
    checks.check(
        hi2022_demotion.get("t8_selected_candidate_matrix_b4_b7_can_close") is False,
        "HI2022 selected-candidate matrix overcloses B4/B7",
    )
    checks.check(
        set(hi2022_demotion.get("t8_selected_candidate_matrix_missing_or_unexecuted_shards", []))
        == {"rA_half:double_pendulum"},
        "HI2022 selected-candidate matrix missing shards changed",
    )
    checks.check(hi2022_demotion.get("full_T8_policy_completed") is False, "HI2022 demotion overcloses full T8")
    checks.check(
        hi2022_demotion.get("source_policy_reproduction_closed") is False,
        "HI2022 demotion overcloses source-policy reproduction",
    )
    checks.check(
        hi2022_demotion.get("source_policy_rows_closed_by_hi2022") == 0,
        "HI2022 demotion overcloses HI2022 rows",
    )
    checks.check(
        hi2022_demotion.get("counts_as_clean_work_precision_figure") is False,
        "HI2022 demotion overclaims clean work/precision figure",
    )
    checks.check(
        "T=8 failure/stability demotion evidence" in hi2022_demotion.get("allowed_figure_use", []),
        "HI2022 demotion missing allowed figure use",
    )
    checks.check(
        "publication-grade B4/B7 work/precision closure row" in hi2022_demotion.get("forbidden_figure_use", []),
        "HI2022 demotion missing forbidden figure use",
    )
    checks.check(
        hi2022_demotion.get("b4_b7_can_close_from_hi2022") is False,
        "HI2022 demotion overcloses B4/B7",
    )
    checks.check(
        hi2022_demotion.get("source_policy_rows_closed_by_this_evidence") == 0,
        "HI2022 demotion evidence overcloses rows",
    )
    checks.check(hi2022_demotion.get("b4_can_close_from_this_evidence") is False, "HI2022 demotion overcloses B4")
    checks.check(hi2022_demotion.get("b7_can_close_from_this_evidence") is False, "HI2022 demotion overcloses B7")
    for gap in [
        "HI2022 full T=8 public grid remains incomplete",
        "HI2022 selected-candidate matrix has 7/8 completed coarse-trio shards; remaining partial/missing shards are ['rA_half:double_pendulum']",
        "current HI2022 T=8 evidence is demoted from B4/B7 source-policy figures",
        "HI2022 contributes zero accepted source-policy work/precision rows",
    ]:
        checks.check(gap in hi2022_demotion.get("promotion_gap", []), f"HI2022 demotion missing gap: {gap}")

    checks.check(
        tfe_demotion.get("schema") == "b4-tfe-figure-scope-demotion-evidence-v1",
        "TFE B4/B7 demotion schema changed",
    )
    checks.check(
        tfe_demotion.get("status") == tfe_demotion_audit.get("status"),
        "TFE B4/B7 demotion status drifted",
    )
    checks.check(
        tfe_demotion.get("source_audit") == "TFE_B4_B7_SOURCE_POLICY_DEMOTION_AUDIT.json",
        "TFE B4/B7 demotion audit source missing",
    )
    checks.check(
        tfe_demotion.get("source_policy_rows_total") == tfe_demotion_audit.get("source_policy_rows_total") == 16,
        "TFE B4/B7 demotion total rows changed",
    )
    checks.check(
        tfe_demotion.get("source_policy_rows_closed")
        == tfe_demotion_audit.get("source_policy_rows_closed")
        == 0,
        "TFE B4/B7 demotion overcloses source rows",
    )
    checks.check(
        tfe_demotion.get("source_policy_rows_closed_by_demotion")
        == tfe_demotion_audit.get("source_policy_rows_closed_by_demotion")
        == 0,
        "TFE B4/B7 demotion closes rows",
    )
    checks.check(
        tfe_demotion.get("demoted_related_work_proxy_rows_for_current_claim")
        == tfe_demotion_audit.get("demoted_related_work_proxy_rows_for_current_claim")
        == 16,
        "TFE demoted current-claim row count changed",
    )
    checks.check(
        tfe_demotion.get("future_reintroduction_requires_runner_or_code_path_rows")
        == tfe_demotion_audit.get("future_reintroduction_requires_runner_or_code_path_rows")
        == 16,
        "TFE future runner/code-path row count changed",
    )
    checks.check(
        tfe_demotion.get("current_claim_requires_tfe_source_policy_execution")
        == tfe_demotion_audit.get("current_claim_requires_tfe_source_policy_execution")
        is False,
        "TFE demotion current-claim execution boundary changed",
    )
    checks.check(
        tfe_demotion.get("brown_mcphee_source_code_equivalent_law")
        == tfe_demotion_audit.get("brown_mcphee_source_code_equivalent_law")
        is False,
        "TFE Brown--McPhee boundary changed",
    )
    checks.check(
        tfe_demotion.get("source_grid_policy_resolved_for_full_T10")
        == tfe_demotion_audit.get("source_grid_policy_resolved_for_full_T10")
        is False,
        "TFE full T=10 grid boundary changed",
    )
    checks.check(
        tfe_demotion.get("pendulum_dae_runner_implemented")
        == tfe_demotion_audit.get("pendulum_dae_runner_implemented")
        is False,
        "TFE pendulum DAE runner boundary changed",
    )
    checks.check(
        tfe_demotion.get("counts_as_clean_work_precision_figure") is False
        and tfe_demotion.get("b4_b7_can_close_from_tfe") is False,
        "TFE demotion overcloses B4/B7 or figure scope",
    )

    ra_lane = lanes.get("ra2021_source_policy_work_precision", {})
    checks.check(ra_lane.get("ready_to_launch_after_explicit_opt_in") is True, "RA2021 lane should be opt-in ready")
    checks.check(ra_lane.get("source_policy_1e_4_opt_in_required") is True, "RA2021 lane lost 1e-4 opt-in")
    checks.check(ra_lane.get("source_policy_rows_completed") == 0, "RA2021 lane overclosed rows")
    checks.check(ra_lane.get("public_order_groups_completed") == 12, "RA2021 lane order groups changed")
    checks.check(ra_lane.get("public_timing_rows_completed") == 12, "RA2021 lane timing rows changed")
    checks.check(ra_lane.get("source_output_mapping_verified") is True, "RA2021 lane output mapping missing")
    checks.check(ra_lane.get("source_time_grid_policy_extracted") is True, "RA2021 lane time-grid extraction missing")
    checks.check(ra_lane.get("parallel_shard_count") == 12, "RA2021 lane parallel shard count changed")
    checks.check(
        any("--allow-source-policy-1e-4" in item for item in ra_lane.get("representative_commands", [])),
        "RA2021 opt-in command missing",
    )

    tfe_lane = lanes.get("tfe_source_policy_work_precision", {})
    checks.check(tfe_lane.get("ready_to_launch_after_explicit_opt_in") is False, "TFE lane should not be ready")
    checks.check(tfe_lane.get("source_reference_h") == 1e-4, "TFE source reference h changed")
    checks.check(tfe_lane.get("same_test_candidate_work_precision_methods") == 6, "TFE method count changed")
    checks.check(tfe_lane.get("same_test_candidate_work_precision_rows") == 18, "TFE metric row count changed")
    checks.check(tfe_lane.get("same_test_candidate_source_policy_rows_completed") == 0, "TFE lane overclosed rows")
    checks.check(tfe_lane.get("candidate_full_T10_probe_implemented") is True, "TFE full T=10 probe missing")
    checks.check(tfe_lane.get("candidate_full_T10_probe_finite_rows") == 4, "TFE full T=10 finite rows changed")
    checks.check(tfe_lane.get("candidate_full_T10_probe_residual_ok_rows") == 4, "TFE full T=10 residual rows changed")
    checks.check(tfe_lane.get("pendulum_dae_runner_implemented") is False, "TFE runner unexpectedly implemented")
    checks.check(tfe_lane.get("source_policy_dae_runner_equivalent") is False, "TFE DAE equivalence overclaimed")
    checks.check(tfe_lane.get("source_policy_method_runner_equivalent") is False, "TFE method equivalence overclaimed")
    checks.check(
        tfe_lane.get("runner_equivalence_preflight_status")
        == tfe_runner_preflight.get("status")
        == "preflight_ready_runner_equivalence_open",
        "TFE lane runner-equivalence preflight status changed",
    )
    checks.check(
        tfe_lane.get("runner_equivalence_preflight_closed_preconditions")
        == tfe_runner_preflight.get("closed_precondition_count")
        == 25,
        "TFE lane runner-equivalence precondition count changed",
    )
    checks.check(
        tfe_lane.get("runner_equivalence_preflight_open_blockers")
        == tfe_runner_preflight.get("open_blocker_count")
        == 6,
        "TFE lane runner-equivalence blocker count changed",
    )
    checks.check(
        tfe_lane.get("runner_equivalence_preflight_rows_closed")
        == tfe_runner_preflight.get("source_policy_rows_closed_by_preflight")
        == 0,
        "TFE lane runner-equivalence preflight overclosed rows",
    )
    checks.check(
        tfe_lane.get("runner_equivalence_preflight_can_close_lane")
        == tfe_runner_preflight.get("can_close_tfe_lane_from_preflight")
        is False,
        "TFE lane runner-equivalence preflight overcloses lane",
    )
    checks.check(tfe_lane.get("demotion_audit_consumed") is True, "TFE lane did not consume demotion audit")
    checks.check(
        tfe_lane.get("demotion_audit") == "TFE_B4_B7_SOURCE_POLICY_DEMOTION_AUDIT.json",
        "TFE lane demotion audit path changed",
    )
    checks.check(
        tfe_lane.get("current_claim_requires_tfe_source_policy_execution") is False
        and tfe_lane.get("current_claim_requires_source_policy_execution") is False,
        "TFE lane current-claim execution boundary changed",
    )
    checks.check(
        tfe_lane.get("demoted_related_work_proxy_rows_for_current_claim") == 16,
        "TFE lane demotion row count changed",
    )
    checks.check(
        tfe_lane.get("future_reintroduction_requires_runner_or_code_path_rows") == 16,
        "TFE lane future runner/code-path row count changed",
    )
    checks.check(tfe_lane.get("representative_commands") == [], "TFE lane should not expose runnable commands")

    checks.check(
        tfe_runner_preflight.get("schema") == "tfe-source-policy-runner-equivalence-preflight-v1",
        "TFE runner-equivalence preflight schema changed",
    )
    checks.check(
        tfe_runner_preflight.get("closed_precondition_count") == 25,
        "TFE runner-equivalence preflight precondition count changed",
    )
    checks.check(
        tfe_runner_preflight.get("open_blocker_count") == 6,
        "TFE runner-equivalence preflight blocker count changed",
    )
    checks.check(
        tfe_runner_preflight.get("source_policy_rows_closed_by_preflight") == 0,
        "TFE runner-equivalence preflight overcloses rows",
    )
    checks.check(
        tfe_runner_preflight.get("b4_b7_can_close_from_preflight") is False,
        "TFE runner-equivalence preflight overcloses B4/B7",
    )
    checks.check(
        tfe_runner_preflight.get("heavy_numerical_run_invoked") is False,
        "TFE runner-equivalence preflight invoked heavy run",
    )
    checks.check(
        set(tfe_runner_preflight.get("open_blocker_ids", []))
        == {
            "brown_mcphee_source_code_equivalent_law_open",
            "pendulum_absolute_coordinate_source_policy_dae_runner_missing",
            "tfe_newmark_trapezoidal_source_policy_method_runners_missing",
            "gauss6_fullva_absolute_coordinate_source_policy_runner_missing",
            "full_T10_source_grid_endpoint_policy_open",
            "accepted_source_policy_work_precision_rows_not_executed_or_bound",
        },
        "TFE runner-equivalence blocker ids changed",
    )

    hi_lane = lanes.get("hi2022_full_T8_work_precision", {})
    checks.check(hi_lane.get("ready_to_launch_after_explicit_opt_in") is True, "HI2022 lane should be policy-ready")
    checks.check(hi_lane.get("source_policy_1e_4_opt_in_required") is False, "HI2022 lane should not require 1e-4")
    checks.check(hi_lane.get("bounded_T0p1_rows") == 24, "HI2022 bounded row count changed")
    checks.check(hi_lane.get("bounded_T0p1_ok_rows") == 24, "HI2022 bounded ok row count changed")
    checks.check(hi_lane.get("full_T8_policy_completed") is False, "HI2022 full T8 unexpectedly closed")
    checks.check(hi_lane.get("parallel_shard_count") == 8, "HI2022 parallel shard count changed")
    hi_lane_commands = hi_lane.get("representative_commands", [])
    checks.check(isinstance(hi_lane_commands, list) and len(hi_lane_commands) == 8, "HI2022 lane command count changed")
    checks.check(
        all("run_hi2022_full_t8_source_policy_candidate.py" in item for item in hi_lane_commands),
        "HI2022 lane command script changed",
    )
    checks.check(all("--execute" in item for item in hi_lane_commands), "HI2022 lane command missing execute flag")
    checks.check(
        all("--allow-source-policy-1e-4" not in item for item in hi_lane_commands),
        "HI2022 lane command unexpectedly includes 1e-4 opt-in",
    )

    vp_lane = lanes.get("vp2024_source_code_path_work_precision", {})
    checks.check(vp_lane.get("ready_to_launch_after_explicit_opt_in") is False, "VP lane should not be ready")
    checks.check(vp_lane.get("code_path_resolved") is False, "VP code path unexpectedly resolved")
    checks.check(vp_lane.get("source_policy_rows_completed") == 0, "VP lane overclosed rows")

    for token in [
        "Status: `execution_plan_ready_b4_b7_remain_open`.",
        "Open blockers after plan: `[]`.",
        "B4/B7 can close now: `False/False`.",
        "Route B closes B2/B4/B7: `True/False/False`.",
        "Source-policy work/precision rows closed/total: `0/40`.",
        "Source-policy flagged rows: `15`.",
        "External-superiority-ready rows: `0`.",
        "Common-reference velocity order wins: `40/40`.",
        "Common-reference finest velocity error wins: `40/40`.",
        "TFE same-test diagnostic rows/source-policy rows: `18/0`.",
        "Default 1e-4/heavy/run_v047/v048: `False/False/False/False`.",
        "TFE runner-equivalence preflight: `preflight_ready_runner_equivalence_open`.",
        "TFE runner-equivalence preflight closed/open/source rows: `25/6/0`.",
        "TFE runner-equivalence preflight can close lane: `False`.",
        "TFE B4/B7 figure-scope demotion: `tfe_source_policy_rows_demoted_from_current_b4_b7_figures`.",
        "TFE demoted/source-policy rows closed: `16/0`.",
        "TFE current claim requires source-policy execution: `False`.",
        "Next heavy source-policy execution requires user opt-in: `True`.",
        "Execution lane ready/not-ready count: `2/2`.",
        "Plan-only closes rows: `False`.",
        "Current figure set closes B7: `True`.",
        "Current figure set supports common-reference diagnostics only: `True`.",
        "RA2021 launch preflight: `b4-ra2021-source-policy-launch-preflight-v1` / `ready_not_run_requires_user_opt_in`.",
        "RA2021 runner files ready: `True`.",
        "RA2021 launch commands: `5`.",
        "RA2021 runner CLI contract: `runner_cli_contract_satisfied`.",
        "RA2021 preflight closes B4/B7: `False/False`.",
        "HI2022 launch preflight: `b4-hi2022-source-policy-launch-preflight-v1` / `preflight_ready_existing_selected_candidate_matrix_incomplete`.",
        "HI2022 runner files ready: `True`.",
        "HI2022 launch commands/completed/missing: `8/7/1`.",
        "HI2022 runner CLI contract: `runner_cli_contract_satisfied`.",
        "HI2022 commands avoid 1e-4/source rows closed: `True/0`.",
        "HI2022 preflight closes B4/B7: `False/False`.",
        "RA2021 executed shard evidence: `all_public_baseline_source_policy_shards_completed_not_promoted`.",
        "RA2021 executed shard forms completed: `['rA', 'rp', 'reps']`.",
        "RA2021 executed shard rows/source-policy rows closed: `9/0`.",
        "Gauss6 local source-policy evidence: `partial_local_source_policy_evidence_single_complete_closed_loop_residual_only_not_promoted`.",
        "Gauss6 single public-horizon rows/source-policy rows closed: `3/0`.",
        "Gauss6 closed-loop combined ok/failed rows: `6/0`.",
        "RA2021 closed-loop same-window public work/precision: `same_window_public_work_precision_available_reference_caveat_not_external_superiority`.",
        "RA2021 closed-loop same-window rows/available/source-policy rows closed: `24/2/0`.",
        "RA2021 closed-loop strict common-reference/external superiority: `False` / `False`.",
        "RA2021 double local source-policy candidate: `executed_order_below_acceptance_not_promoted`.",
        "RA2021 double local candidate rows/order accepted/source-policy rows closed: `3/False/0`.",
        "HI2022 full T=8 source-policy candidate: `selected_candidate_matrix_partially_executed_not_promoted`.",
        "HI2022 full T=8 candidate rows/full grid/source-policy rows closed: `22/False/0`.",
        "HI2022 B4/B7 figure-scope demotion: `demote_hi2022_from_b4_b7_source_policy_figures`.",
        "HI2022 B4/B7 demotion rows/clean figure/can close: `0/False/False`.",
        "HI2022 selected-candidate matrix completed/expected/rows closed: `7/8/0`.",
        "Recommended first lane: `ra2021_source_policy_work_precision`.",
        "The current TFE work/precision rows are diagnostic same-test or algorithm-literal rows.",
        "they do not close B4 or B7 because they do not establish a source-policy-closed external same-test row.",
        "## TFE Runner-Equivalence Preflight",
        "Closed preconditions/open blockers: `25/6`.",
        "Source-policy rows closed by preflight: `0`.",
        "Can close TFE lane from preflight: `False`.",
        "Heavy numerical run invoked: `False`.",
        "accepted_source_policy_work_precision_rows_not_executed_or_bound",
        "## TFE B4/B7 Figure-Scope Demotion",
        "TFE rows demoted for current claim/source-policy rows closed: `16/0`.",
        "Source-policy rows closed by demotion: `0`.",
        "Future reintroduction runner/code-path rows: `16`.",
        "B4/B7 can close from TFE demotion: `False`.",
        "## RA2021 Launch Preflight",
        "Every RA2021 launch command requires `--allow-source-policy-1e-4` and remains unexecuted by this plan.",
        "The preflight only proves that the runner interfaces and outputs are specified; it closes zero source-policy rows.",
        "RA2021 runner CLI contract: `runner_cli_contract_satisfied` with `4` runner checks and `5` command checks.",
        "## HI2022 Launch Preflight",
        "Expected/completed/missing shards: `8/7/1`.",
        "Commands avoid 1e-4: `True`.",
        "Source-policy 1e-4 required: `False`.",
        "Heavy numerical run invoked by preflight: `False`.",
        "Source-policy rows closed by preflight: `0`.",
        "B4/B7 can close from HI2022 preflight: `False/False`.",
        "Runner CLI contract: `runner_cli_contract_satisfied` with `1` runner checks and `8` command checks.",
        "This read-only plan does not execute HI2022 commands.",
        "Existing selected-candidate artifacts are summarized separately; reruns still require explicit heavy-run opt-in.",
        "The preflight only enumerates isolated candidate shard commands; it closes zero source-policy rows.",
        "## Executed RA2021 Shards",
        "Forms completed: `['rA', 'rp', 'reps']`.",
        "Public-baseline shard rows executed: `9`.",
        "Counts as complete work/precision curve: `False`.",
        "B4/B7 can close from this evidence: `False/False`.",
        "## Gauss6 Local Source-Policy Evidence",
        "Single public-horizon step trio completed: `True`.",
        "Closed-loop h=1e-4 standalone ok models: `2`.",
        "Closed-loop public step trios completed: `True`.",
        "Closed-loop rows are dynamic work/precision: `False`.",
        "Counts as B4 accepted source-policy rows: `False`.",
        "B4/B7 can close from Gauss6 evidence: `False/False`.",
        "## RA2021 Closed-Loop Same-Window Work/Precision",
        "Public work/precision available examples: `['four_link', 'slider_crank']`.",
        "Public work/precision missing count: `0`.",
        "Strict common-reference error columns: `False`.",
        "Reference alignment status: `mixed_reference_family_requires_manuscript_caveat`.",
        "External superiority claim: `False`.",
        "Counts as bounded same-window diagnostic: `True`.",
        "Counts as complete RA2021 work/precision curve: `False`.",
        "Source-policy rows closed by same-window evidence: `0`.",
        "B4/B7 can close from same-window evidence: `False/False`.",
        "## RA2021 Double Local Source-Policy Candidate",
        "Runner status: `executed_isolated_source_policy_candidate`.",
        "Rows ok/total: `3/3`.",
        "reference h: `0.0001`.",
        "Position pair orders:",
        "Velocity pair orders:",
        "Finest pair position/velocity order:",
        "Constraint-threshold failed h values: `[0.01]`.",
        "aggregate_observed_order_below_5p5_threshold",
        "at_least_one_candidate_row_fails_endpoint_constraint_threshold",
        "Order acceptance threshold/satisfied: `5.5` / `False`.",
        "Promotion ready: `False`.",
        "B4/B7 can close from double candidate: `False/False`.",
        "observed source-policy order is below sixth-order acceptance (pos=2.148, vel=2.463)",
        "## HI2022 Full T=8 Source-Policy Candidate",
        "Runner statuses: `['executed_full_T8_selected_coarse_trio_not_promoted', 'partial_or_failed_full_T8_source_policy_candidate_not_promoted']`.",
        "Forms/models: `['rA', 'rA_half']` / `['double_pendulum', 'four_link', 'single_pendulum', 'slider_crank']`.",
        "Summary/rows artifacts: `8/8`.",
        "Completed/expected shards: `7/8`.",
        "Partial-or-failed shards: `['rA_half:double_pendulum']`.",
        "Missing artifact shards: `[]`.",
        "Rows ok/total: `22/24`.",
        "T=8/reference h selected: `True` / `True`.",
        "Full public grid selected/completed: `False` / `False`.",
        "Source-policy 1e-4 included: `False`.",
        "Counts as full public-grid source-policy: `False`.",
        "Counts as complete work/precision curve: `False`.",
        "Source-policy rows closed by HI2022 candidate: `0`.",
        "B4/B7 can close from HI2022 candidate: `False/False`.",
        "selected coarse trio is not the full encoded HI2022 public step family",
        "## HI2022 B4/B7 Figure-Scope Demotion",
        "Source audit: `HI2022_SOURCE_POLICY_ROW_AUDIT.json`.",
        "T=8 coarse rows ok/total: `18/24`.",
        "T=8 selected candidate rows ok/total: `3/3`.",
        "T=8 selected candidate matrix status: `preflight_ready_existing_selected_candidate_matrix_incomplete`.",
        "T=8 selected candidate matrix completed/expected: `7/8`.",
        "T=8 selected candidate matrix commands/count avoid 1e-4: `8` / `True`.",
        "T=8 selected candidate matrix heavy run invoked: `False`.",
        "T=8 selected candidate matrix rows closed/can close: `0` / `False`.",
        "T=8 selected candidate matrix rows ok/total: `22/24`.",
        "T=8 selected candidate matrix partial-or-failed shards: `['rA_half:double_pendulum']`.",
        "T=8 selected candidate matrix missing artifact shards: `[]`.",
        "Source-policy rows closed by HI2022: `0`.",
        "Counts as clean work/precision figure: `False`.",
        "B4/B7 can close from HI2022: `False`.",
        "publication-grade B4/B7 work/precision closure row",
        "HI2022 selected-candidate matrix has 7/8 completed coarse-trio shards; remaining partial/missing shards are ['rA_half:double_pendulum']",
        "HI2022 contributes zero accepted source-policy work/precision rows",
    ]:
        checks.check(token in plan_md, f"markdown missing token: {token}")

    if checks.errors:
        print("b4 source-policy work/precision execution plan validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("b4 source-policy work/precision execution plan validation: PASS")
    print("source_policy_rows_closed=0")
    print("source_policy_rows_total=40")
    print("open_blockers_after_plan=")
    print("ready_to_launch_after_explicit_opt_in_count=2")
    print("not_ready_lane_count=2")
    print("b4_can_close_now=False")
    print("b7_can_close_now=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
