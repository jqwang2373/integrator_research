#!/usr/bin/env python3
"""Validate the source-policy local candidate gap audit."""

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


def by_suite(audit: dict[str, Any]) -> dict[str, dict[str, Any]]:
    suites = audit.get("suite_summaries", [])
    return {str(item.get("suite_id")): item for item in suites if isinstance(item, dict)}


def main() -> int:
    checks = Checks()
    try:
        audit = read_json(PAPER / "SOURCE_POLICY_LOCAL_CANDIDATE_GAP_AUDIT.json")
        audit_md = read_text(PAPER / "SOURCE_POLICY_LOCAL_CANDIDATE_GAP_AUDIT.md")
        dashboard = read_json(PAPER / "FOUR_EXAMPLE_SOURCE_POLICY_DASHBOARD.json")
        comparison = read_json(PAPER / "COMPARISON_OBJECTIVE_CLOSURE_RECONCILIATION_AUDIT.json")
        b2 = read_json(PAPER / "B2_SOURCE_POLICY_REMAINING_WORK_MANIFEST.json")
        ledger = read_json(PAPER / "SOURCE_POLICY_ROW_CLOSURE_LEDGER.json")
    except Exception as exc:  # noqa: BLE001
        print(f"source-policy local candidate gap audit validation: FAIL\n- {exc}")
        return 1

    suites = by_suite(audit)
    execution = audit.get("execution_policy", {})
    ra = suites.get("ra2021_absolute_coordinate", {})
    hi = suites.get("hi2022_half_implicit", {})
    tfe = suites.get("tfe2026_original_pendulum", {})
    ra_single = ra.get("single_pendulum_public_policy_candidate", {})
    ra_double = ra.get("double_pendulum_public_horizon_candidate", {})
    ra_closed = ra.get("closed_loop_public_horizon_candidates", {})

    checks.check(audit.get("schema") == "source-policy-local-candidate-gap-audit-v1", "schema changed")
    checks.check(
        audit.get("status") == "local_candidate_gap_open_source_policy_not_closed",
        "status changed",
    )
    checks.check(audit.get("submission_ready") is False, "audit overclaims submission readiness")
    checks.check(audit.get("source_policy_superiority_claim_allowed") is False, "source-policy claim overclosed")
    checks.check(audit.get("external_superiority_claim_allowed") is False, "external claim overclosed")
    checks.check(audit.get("active_source_policy_suites") == 0, "active suite count changed")
    checks.check(audit.get("active_b2_flagged_rows") == b2.get("active_flagged_row_count") == 0, "active B2 rows changed")
    checks.check(audit.get("demoted_flagged_rows") == b2.get("demoted_flagged_row_count") == 15, "demoted rows changed")
    checks.check(
        audit.get("row_ledger_flagged_rows") == ledger.get("coverage", {}).get("flagged_row_count") == 15,
        "ledger flagged rows changed",
    )
    checks.check(
        audit.get("row_ledger_source_policy_closed_rows")
        == ledger.get("coverage", {}).get("rows_source_policy_closed")
        == 0,
        "ledger source-policy closure changed",
    )
    checks.check(
        audit.get("common_reference_claim_allowed")
        == comparison.get("common_reference_claim_allowed")
        is True,
        "common-reference boundary changed",
    )
    checks.check(
        audit.get("local_dynamic_order_examples")
        == dashboard.get("local_dynamic_order_closed_examples")
        == 2,
        "local dynamic-order example count changed",
    )
    checks.check(
        audit.get("local_dynamic_order_example_names")
        == dashboard.get("local_dynamic_order_closed_example_names")
        == ["single_pendulum", "double_pendulum"],
        "local dynamic-order example names changed",
    )
    checks.check(
        audit.get("source_policy_dynamic_order_examples")
        == dashboard.get("accepted_source_policy_dynamic_order_examples")
        == 0,
        "source-policy dynamic-order example count changed",
    )
    checks.check(audit.get("accepted_source_policy_dynamic_order_examples") == 0, "source-policy examples overclosed")
    checks.check(audit.get("source_policy_closed_rows") == 0, "source-policy closed rows changed")
    checks.check(audit.get("source_policy_total_rows") == 40, "source-policy total rows changed")
    checks.check(execution.get("read_only_existing_artifacts") is True, "audit lost read-only marker")
    checks.check(execution.get("heavy_numerical_run_invoked") is False, "audit invoked heavy run")
    checks.check(execution.get("default_1e_4_required") is False, "audit requires default 1e-4")
    checks.check(execution.get("run_v047_invoked") is False, "audit invoked run_v047")
    checks.check(execution.get("v048_runner_invoked") is False, "audit invoked v048")
    checks.check(set(suites) == {"ra2021_absolute_coordinate", "hi2022_half_implicit", "tfe2026_original_pendulum"}, "suite set changed")

    checks.check(ra.get("public_baseline_order_groups") == "9/9", "RA public order summary changed")
    checks.check(ra.get("public_baseline_timing_rows") == "12/12", "RA public timing summary changed")
    checks.check(ra_single.get("row_count") == 3 and ra_single.get("ok_row_count") == 3, "RA single candidate rows changed")
    checks.check(ra_single.get("h_values") == [0.0001, 0.001, 0.01], "RA single h-grid changed")
    checks.check(ra_single.get("t_end_values") == [3.0], "RA single horizon changed")
    checks.check(ra_single.get("reference_h_values") == [0.001], "RA single reference h changed")
    checks.check(ra_single.get("public_policy_h_rows") == 3, "RA single public h rows changed")
    checks.check(ra_single.get("public_policy_time_window_rows") == 3, "RA single public horizon rows changed")
    checks.check(ra_single.get("source_policy_candidate_grid_present") is True, "RA single candidate grid missing")
    checks.check(ra_single.get("accepted_source_policy_dynamic_order") is False, "RA single overaccepted")
    checks.check(ra_double.get("row_count") == 3 and ra_double.get("ok_row_count") == 3, "RA double candidate rows changed")
    checks.check(ra_double.get("h_values") == [0.025, 0.05, 0.1], "RA double h-grid changed")
    checks.check(ra_double.get("reference_h_values") == [0.0125], "RA double reference changed")
    checks.check(ra_double.get("public_policy_h_rows") == 0, "RA double public h rows changed")
    checks.check(ra_double.get("source_policy_candidate_grid_present") is False, "RA double overaccepted")
    checks.check(set(ra_closed) == {"four_link", "slider_crank"}, "RA closed-loop models changed")
    for model in ["four_link", "slider_crank"]:
        row = ra_closed.get(model, {})
        checks.check(row.get("row_count") == 3 and row.get("ok_row_count") == 3, f"{model} closed-loop rows changed")
        checks.check(row.get("h_values") == [0.0001, 0.001, 0.01], f"{model} closed-loop h-grid changed")
        checks.check(row.get("dynamic_order_work_row") is False, f"{model} dynamic row overaccepted")
        checks.check(row.get("kinematic_reaction_residual_row") is True, f"{model} residual marker missing")
    checks.check(ra.get("accepted_source_policy_dynamic_order_examples") == 0, "RA source-policy examples changed")
    checks.check(ra.get("source_policy_closed_rows") == 0, "RA source-policy rows changed")

    checks.check(hi.get("bounded_T0p1_rows") == "24/24", "HI bounded rows changed")
    checks.check(hi.get("bounded_T0p1_h_values") == [0.005, 0.01, 0.02], "HI bounded h-grid changed")
    checks.check(hi.get("bounded_T0p1_reference_h_values") == [0.001], "HI bounded reference changed")
    checks.check(hi.get("t8_coarse_rows") == "18/24", "HI T8 coarse rows changed")
    checks.check(hi.get("t8_coarse_h_values") == [0.025, 0.05, 0.1], "HI T8 h-grid changed")
    checks.check(hi.get("t8_coarse_reference_h_values") == [0.0125], "HI T8 reference changed")
    checks.check(hi.get("t8_complete_group_count") == 4 and hi.get("t8_group_count") == 8, "HI T8 group counts changed")
    checks.check(hi.get("full_T8_source_policy_completed") is False, "HI overclosed full T8")
    checks.check(hi.get("source_policy_closed_rows") == 0, "HI source-policy rows changed")

    checks.check(tfe.get("source_parameter_model_implemented") is True, "TFE parameter model changed")
    checks.check(
        tfe.get("status") == "nonpublic_code_attempted_not_reproducible_not_promoted",
        "TFE attempted-not-reproducible status changed",
    )
    checks.check(tfe.get("public_code_available") is False, "TFE public-code boundary changed")
    checks.check(tfe.get("self_reproduction_attempted") is True, "TFE self-reproduction attempt missing")
    checks.check(
        tfe.get("self_reproduction_attempt_status") == "attempted_not_reproducible_not_promoted",
        "TFE self-reproduction status changed",
    )
    checks.check(tfe.get("bounded_source_policy_runner_rows") == 4, "TFE bounded runner rows changed")
    checks.check(tfe.get("bounded_source_policy_runner_full_T10") is False, "TFE full T10 overclosed")
    checks.check(tfe.get("source_comparator_candidate_runners_implemented") is True, "TFE comparator smoke changed")
    checks.check(tfe.get("tfe_m1_m2_m3_candidate_runner_smoke_implemented") is True, "TFE m-runner smoke changed")
    checks.check(tfe.get("pendulum_dae_runner_implemented") is False, "TFE DAE runner overclosed")
    checks.check(tfe.get("brown_mcphee_friction_law_implemented") is False, "TFE friction overclosed")
    checks.check(tfe.get("source_policy_rows_completed") == 0, "TFE source rows changed")
    checks.check(tfe.get("integer_step_compatible_rows") == 2, "TFE compatible grid rows changed")
    checks.check(tfe.get("integer_step_incompatible_rows") == 4, "TFE incompatible grid rows changed")
    checks.check(
        tfe.get("exact_T_compatible_endpoint_grid_rows_resolved") == 2,
        "TFE exact-T endpoint-grid resolved count changed",
    )
    checks.check(
        tfe.get("endpoint_incompatible_rows_requiring_source_policy") == 4,
        "TFE endpoint-incompatible policy-required count changed",
    )
    checks.check(
        tfe.get("source_grid_policy_resolved_for_exact_T_compatible_rows") is True,
        "TFE exact-T compatible subset grid policy changed",
    )
    checks.check(
        tfe.get("source_grid_policy_resolved_for_full_T10") is False,
        "TFE full T10 grid policy overclosed",
    )
    checks.check(tfe.get("endpoint_sensitivity_raw_rows") == 48, "TFE endpoint sensitivity rows changed")

    for token in [
        "Status: **local candidate gap open; source-policy not closed**.",
        "Active source-policy suites: `0`.",
        "Active B2 flagged rows: `0`.",
        "Demoted flagged rows: `15`.",
        "Source-policy closed rows: `0/40`.",
        "Common-reference claim allowed: `True`.",
        "Local dynamic-order examples: `2/4`.",
        "Accepted source-policy dynamic-order examples: `0`.",
        "Source-policy dynamic-order examples: `0/4`.",
        "External superiority claim allowed: `False`.",
        "| `ra2021_absolute_coordinate` |",
        "| `hi2022_half_implicit` |",
        "| `tfe2026_original_pendulum` |",
        "attempted-not-reproducible",
        "Reading rule: this artifact explains why existing local candidate rows do not yet close source-policy external superiority.",
    ]:
        checks.check(token in audit_md, f"markdown missing token: {token}")
    checks.check(
        "implement the original TFE pendulum runner and complete the four active TFE source-policy rows, or demote"
        not in audit_md,
        "markdown retained stale TFE implementation action",
    )

    if checks.errors:
        print("source-policy local candidate gap audit validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("source-policy local candidate gap audit validation: PASS")
    print(f"active_source_policy_suites={audit.get('active_source_policy_suites')}")
    print(f"source_policy_closed={audit.get('source_policy_closed_rows')}/{audit.get('source_policy_total_rows')}")
    print(f"accepted_source_policy_dynamic_order_examples={audit.get('accepted_source_policy_dynamic_order_examples')}")
    print(f"external_superiority_claim_allowed={audit.get('external_superiority_claim_allowed')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
