#!/usr/bin/env python3
"""Validate the TFE B4/B7 source-policy demotion audit."""

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
        audit = read_json(PAPER / "TFE_B4_B7_SOURCE_POLICY_DEMOTION_AUDIT.json")
        audit_md = read_text(PAPER / "TFE_B4_B7_SOURCE_POLICY_DEMOTION_AUDIT.md")
        row_audit = read_json(PAPER / "TFE_SOURCE_POLICY_ROW_AUDIT.json")
        model_audit = read_json(PAPER / "TFE_SOURCE_PENDULUM_MODEL_AUDIT.json")
        grid_audit = read_json(PAPER / "TFE_SOURCE_GRID_COMPATIBILITY_AUDIT.json")
        spec = read_json(PAPER / "TFE_SOURCE_POLICY_SPEC.json")
    except Exception as exc:  # noqa: BLE001
        print(f"TFE B4/B7 source-policy demotion audit validation: FAIL\n- {exc}")
        return 1

    preflight = row_audit.get("source_policy_runner_equivalence_preflight", {})
    source_text_anchor = model_audit.get("brown_mcphee_source_text_anchor", {})
    endpoint_audit = grid_audit.get("source_text_endpoint_convention_audit", {})
    expected_blockers = [
        "brown_mcphee_source_code_equivalent_law_open",
        "pendulum_absolute_coordinate_source_policy_dae_runner_missing",
        "tfe_newmark_trapezoidal_source_policy_method_runners_missing",
        "gauss6_fullva_absolute_coordinate_source_policy_runner_missing",
        "full_T10_source_grid_endpoint_policy_open",
        "accepted_source_policy_work_precision_rows_not_executed_or_bound",
    ]

    checks.check(audit.get("schema") == "tfe-b4-b7-source-policy-demotion-audit-v1", "schema changed")
    checks.check(
        audit.get("status") == "tfe_source_policy_rows_demoted_from_current_b4_b7_figures",
        "status changed",
    )
    checks.check(audit.get("read_only") is True, "audit must be read-only")
    checks.check(audit.get("source_policy_rows_total") == 16, "TFE B4/B7 row count changed")
    checks.check(audit.get("source_policy_method_count") == 4, "TFE B4/B7 method count changed")
    checks.check(audit.get("source_policy_example_count") == 4, "TFE B4/B7 example count changed")
    checks.check(
        audit.get("source_policy_rows_closed") == row_audit.get("source_policy_closed_rows") == 0,
        "TFE source-policy rows unexpectedly closed",
    )
    checks.check(audit.get("source_policy_rows_closed_by_demotion") == 0, "demotion closed source rows")
    checks.check(
        audit.get("current_claim_requires_tfe_source_policy_execution") is False,
        "current claim unexpectedly requires TFE execution",
    )
    checks.check(
        audit.get("demoted_related_work_proxy_rows_for_current_claim") == 16,
        "TFE current-claim demotion count changed",
    )
    checks.check(
        audit.get("future_reintroduction_requires_runner_or_code_path_rows") == 16,
        "future TFE runner/code-path row count changed",
    )
    checks.check(audit.get("future_source_policy_work_required") is True, "future TFE work guard missing")
    checks.check(
        audit.get("source_policy_runner_equivalence_open") is True,
        "TFE runner-equivalence unexpectedly closed",
    )
    checks.check(
        audit.get("runner_equivalence_preflight_status") == preflight.get("status"),
        "runner-equivalence status drifted",
    )
    checks.check(
        audit.get("runner_equivalence_closed_precondition_count") == preflight.get("closed_precondition_count") == 25,
        "runner-equivalence closed precondition count changed",
    )
    checks.check(
        audit.get("runner_equivalence_open_blocker_count") == preflight.get("open_blocker_count") == 6,
        "runner-equivalence open blocker count changed",
    )
    checks.check(
        audit.get("runner_equivalence_open_blocker_ids") == expected_blockers,
        "runner-equivalence blocker IDs changed",
    )
    checks.check(audit.get("demotion_reasons") == expected_blockers, "demotion reasons changed")
    checks.check(
        audit.get("pendulum_dae_runner_implemented") is preflight.get("pendulum_dae_runner_implemented") is False,
        "pendulum DAE runner unexpectedly implemented",
    )
    checks.check(
        audit.get("tfe_newmark_trapezoidal_source_policy_runners_implemented")
        is preflight.get("tfe_newmark_trapezoidal_source_policy_runners_implemented")
        is False,
        "TFE/Newmark/trapezoidal runners unexpectedly implemented",
    )
    checks.check(
        audit.get("gauss6_fullva_source_policy_runner_implemented")
        is preflight.get("gauss6_fullva_source_policy_runner_implemented")
        is False,
        "Gauss6 source-policy runner unexpectedly implemented",
    )
    checks.check(
        audit.get("brown_mcphee_source_code_equivalent_law")
        is preflight.get("brown_mcphee_source_code_equivalent_law")
        is False,
        "Brown--McPhee source-code law unexpectedly closed",
    )
    checks.check(
        audit.get("source_text_defers_brown_mcphee_law_to_refs_38_39")
        is source_text_anchor.get("defers_law_details_to_refs_38_39")
        is True,
        "Brown--McPhee source-text deferral changed",
    )
    checks.check(
        audit.get("source_grid_policy_resolved_for_full_T10")
        is preflight.get("source_grid_policy_resolved_for_full_T10")
        is False,
        "full T=10 source-grid policy unexpectedly resolved",
    )
    checks.check(
        audit.get("source_grid_endpoint_incompatible_rows")
        == grid_audit.get("endpoint_incompatible_rows_require_source_endpoint_policy")
        == 4,
        "endpoint-incompatible row count changed",
    )
    checks.check(
        audit.get("source_text_endpoint_convention_resolved_for_error_sampling")
        is endpoint_audit.get("source_endpoint_convention_resolved_for_error_sampling")
        is False,
        "endpoint error-sampling convention unexpectedly resolved",
    )
    checks.check(audit.get("b4_can_close_from_tfe_demotion") is False, "TFE demotion overcloses B4")
    checks.check(audit.get("b7_can_close_from_tfe_demotion") is False, "TFE demotion overcloses B7")
    checks.check(
        audit.get("external_superiority_claim_allowed") is spec.get("external_superiority_claim") is False,
        "TFE external-superiority claim unexpectedly allowed",
    )
    checks.check(audit.get("heavy_numerical_run_invoked") is False, "audit invoked heavy run")
    checks.check(audit.get("run_v047_invoked") is False, "audit invoked run_v047")
    checks.check(audit.get("v048_runner_invoked") is False, "audit invoked v048 runner")
    checks.check(len(audit.get("source_policy_row_ids", [])) == 16, "TFE row-id count changed")

    for token in [
        "Status: `tfe_source_policy_rows_demoted_from_current_b4_b7_figures`.",
        "TFE source-policy rows demoted for current B4/B7 figure scope: `16/16`.",
        "Source-policy rows closed by demotion: `0`.",
        "Current claim requires TFE source-policy execution: `False`.",
        "Future reintroduction requires runner/code-path rows: `16`.",
        "B4/B7 can close from this demotion: `False/False`.",
        "Runner-equivalence preflight closed/open/source rows: `25/6/0`.",
        "Brown--McPhee source-code-equivalent law: `False`.",
        "Source text defers Brown--McPhee law details to Refs. 38--39: `True`.",
        "Full T=10 endpoint/output policy resolved: `False`.",
        "Endpoint-incompatible rows requiring policy: `4`.",
        "Source endpoint convention resolved for error sampling: `False`.",
        "pendulum DAE runner implemented: `False`.",
        "TFE/Newmark/trapezoidal source-policy runners implemented: `False`.",
        "Gauss6 FullVA source-policy runner implemented: `False`.",
        "heavy/run_v047/v048 invoked: `False/False/False`.",
    ]:
        checks.check(token in audit_md, f"markdown missing token: {token}")

    if checks.errors:
        print("TFE B4/B7 source-policy demotion audit validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("TFE B4/B7 source-policy demotion audit validation: PASS")
    print("tfe_rows_demoted=16/16")
    print("source_policy_rows_closed_by_demotion=0")
    print("b4_b7_can_close_from_tfe_demotion=False/False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
