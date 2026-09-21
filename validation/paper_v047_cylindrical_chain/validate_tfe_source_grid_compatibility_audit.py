#!/usr/bin/env python3
"""Validate the TFE source grid compatibility audit."""

from __future__ import annotations

import json
import math
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


def main() -> int:
    checks = Checks()
    try:
        audit = read_json(PAPER / "TFE_SOURCE_GRID_COMPATIBILITY_AUDIT.json")
        text = (PAPER / "TFE_SOURCE_GRID_COMPATIBILITY_AUDIT.md").read_text(
            encoding="utf-8", errors="replace"
        )
    except Exception as exc:  # noqa: BLE001
        print(f"TFE source grid compatibility audit validation: FAIL\n- {exc}")
        return 1

    rows = audit.get("rows", [])
    by_case_h = {(row.get("case_id"), float(row.get("h"))): row for row in rows}
    checks.check(audit.get("schema") == "tfe-source-grid-compatibility-audit-v1", "schema changed")
    checks.check(audit.get("status") == "source_horizon_step_grid_policy_open", "status changed")
    checks.check(audit.get("submission_ready") is False, "audit overclaims submission readiness")
    checks.check(audit.get("source_policy_rows_completed") == 0, "source-policy rows unexpectedly completed")
    checks.check(audit.get("external_superiority_claim_allowed") is False, "external superiority overclaimed")
    checks.check(audit.get("row_count") == len(rows) == 6, "row count changed")
    checks.check(audit.get("integer_step_compatible_rows") == 2, "compatible row count changed")
    checks.check(audit.get("integer_step_incompatible_rows") == 4, "incompatible row count changed")
    checks.check(audit.get("all_source_h_values_integer_step_compatible") is False, "grid overclosed")
    checks.check(audit.get("source_grid_policy_resolved_for_full_T10") is False, "grid policy overclosed")
    checks.check(
        audit.get("source_grid_policy_resolved_for_exact_T_compatible_rows") is True,
        "exact-T compatible subset was not marked endpoint-grid resolved",
    )
    checks.check(
        audit.get("endpoint_compatible_rows_source_endpoint_convention_resolved") == 2,
        "endpoint-compatible resolved row count changed",
    )
    checks.check(
        audit.get("endpoint_incompatible_rows_require_source_endpoint_policy") == 4,
        "endpoint-incompatible row count changed",
    )
    checks.check(
        audit.get("endpoint_incompatible_rows_demoted_from_source_policy") == 4,
        "endpoint-incompatible demotion count changed",
    )
    expected_compatible_ids = [
        "frictional_pendulum:h=0.008",
        "frictional_pendulum:h=0.2",
    ]
    expected_incompatible_ids = [
        "frictionless_pendulum:h=0.003",
        "frictionless_pendulum:h=0.006",
        "frictionless_pendulum:h=0.012",
        "frictional_pendulum:h=0.003",
    ]
    checks.check(
        audit.get("source_endpoint_compatible_row_ids") == expected_compatible_ids,
        "endpoint-compatible row IDs changed",
    )
    checks.check(
        audit.get("source_endpoint_incompatible_row_ids") == expected_incompatible_ids,
        "endpoint-incompatible row IDs changed",
    )
    checks.check(
        audit.get("source_endpoint_incompatible_row_ids_demoted_from_source_policy")
        == expected_incompatible_ids,
        "demoted endpoint-incompatible row IDs changed",
    )
    subclosure = audit.get("endpoint_grid_subclosure", {})
    checks.check(
        subclosure.get("source_grid_policy_resolved_for_exact_T_compatible_rows") is True
        and subclosure.get("endpoint_compatible_rows_source_endpoint_convention_resolved") == 2
        and subclosure.get("endpoint_incompatible_rows_require_source_endpoint_policy") == 4
        and subclosure.get("endpoint_incompatible_rows_demoted_from_source_policy") == 4
        and subclosure.get("source_endpoint_compatible_row_ids") == expected_compatible_ids
        and subclosure.get("source_endpoint_incompatible_row_ids") == expected_incompatible_ids
        and subclosure.get("source_endpoint_incompatible_row_ids_demoted_from_source_policy")
        == expected_incompatible_ids
        and subclosure.get("source_policy_rows_completed") == 0
        and subclosure.get("source_grid_policy_resolved_for_full_T10") is False,
        "endpoint-grid subclosure boundary changed",
    )
    dispositions = audit.get("row_level_promotion_disposition", [])
    checks.check(len(dispositions) == 6, "row-level promotion disposition count changed")
    disposition_by_id = {item.get("row_id"): item for item in dispositions}
    checks.check(set(disposition_by_id) == set(expected_compatible_ids + expected_incompatible_ids), "row disposition ids changed")
    for row_id in expected_compatible_ids:
        disposition = disposition_by_id.get(row_id, {})
        checks.check(
            disposition.get("endpoint_grid_disposition") == "endpoint_grid_resolved_pending_runner_contracts",
            f"{row_id} endpoint disposition changed",
        )
        checks.check(disposition.get("source_policy_row_completed") is False, f"{row_id} row completed unexpectedly")
        checks.check(
            disposition.get("source_policy_execution_eligible_now") is False,
            f"{row_id} execution eligibility overclaimed",
        )
        checks.check(
            disposition.get("source_policy_demoted_until_source_endpoint_sampling_policy") is False,
            f"{row_id} exact-T row demoted unexpectedly",
        )
        checks.check(
            "source-equivalent absolute-coordinate DAE runner" in disposition.get("required_before_promotion", []),
            f"{row_id} missing DAE runner promotion requirement",
        )
    for row_id in expected_incompatible_ids:
        disposition = disposition_by_id.get(row_id, {})
        checks.check(
            disposition.get("endpoint_grid_disposition") == "blocked_by_endpoint_sampling_policy",
            f"{row_id} endpoint disposition changed",
        )
        checks.check(disposition.get("source_policy_row_completed") is False, f"{row_id} row completed unexpectedly")
        checks.check(
            disposition.get("source_policy_execution_eligible_now") is False,
            f"{row_id} execution eligibility overclaimed",
        )
        checks.check(
            disposition.get("source_policy_demoted_until_source_endpoint_sampling_policy") is True,
            f"{row_id} missing endpoint demotion marker",
        )
        checks.check(
            "source-confirmed endpoint/output sampling convention for noninteger T/h"
            in disposition.get("required_before_promotion", []),
            f"{row_id} missing endpoint sampling promotion requirement",
        )
    contract = audit.get("endpoint_policy_acceptance_contract", {})
    checks.check(
        contract.get("exact_T_compatible_subset_can_enter_future_execution_after_runner_contracts") is True,
        "exact-T compatible future-execution marker changed",
    )
    checks.check(contract.get("exact_T_compatible_row_ids") == expected_compatible_ids, "contract compatible row ids changed")
    checks.check(
        contract.get("endpoint_incompatible_rows_blocked_until_source_sampling_policy") == expected_incompatible_ids,
        "contract incompatible row ids changed",
    )
    checks.check(
        contract.get("endpoint_incompatible_rows_demoted_from_source_policy")
        == expected_incompatible_ids,
        "contract demoted row ids changed",
    )
    checks.check(
        "diagnostic-only" in contract.get("endpoint_incompatible_demotion_contract", ""),
        "contract missing endpoint demotion wording",
    )
    checks.check(
        len(contract.get("full_T10_source_policy_promotion_requires", [])) == 4,
        "full-T10 promotion requirement count changed",
    )
    checks.check(
        len(contract.get("forbidden_without_contract", [])) == 3,
        "forbidden-without-contract count changed",
    )
    checks.check(
        any("overrun state" in item for item in contract.get("full_T10_source_policy_promotion_requires", [])),
        "contract missing overrun-state requirement",
    )
    checks.check(
        any("diagnostic algorithm-literal probes" in item for item in contract.get("forbidden_without_contract", [])),
        "contract missing diagnostic-probe promotion ban",
    )
    checks.check(audit.get("frictionless_incompatible_rows") == 3, "frictionless incompatibility count changed")
    checks.check(audit.get("frictional_incompatible_rows") == 1, "frictional incompatibility count changed")
    endpoint_candidates = audit.get("endpoint_convention_candidates", [])
    checks.check(len(endpoint_candidates) == 4, "endpoint convention candidate count changed")
    checks.check(
        {item.get("policy") for item in endpoint_candidates}
        == {
            "nearest_integer_horizon",
            "algorithm_literal_fixed_h_until_tn_ge_tfinal",
            "adjust_h_to_hit_T_exactly",
            "integer_steps_plus_final_partial_step",
        },
        "endpoint convention candidate policies changed",
    )
    checks.check(
        all(item.get("source_equivalent") is False for item in endpoint_candidates),
        "endpoint convention candidates must not be source-equivalent without source verification",
    )
    required = audit.get("required_to_accept_full_T10_rows", [])
    checks.check(len(required) == 6, "required-to-accept list changed")
    checks.check(
        any("source paper/source code endpoint convention" in item for item in required),
        "required-to-accept list missing source endpoint convention verification",
    )
    checks.check(
        any("demoted from the source-policy row set" in item for item in required),
        "required-to-accept list missing demotion requirement",
    )
    source_text = audit.get("source_text_endpoint_convention_audit", {})
    checks.check(source_text.get("source_text_available") is True, "source text not available")
    checks.check(source_text.get("anchor_count", 0) >= 8, "source text anchor count too small")
    checks.check(
        source_text.get("algorithm_literal_constant_h_until_tn_ge_tfinal") is True,
        "algorithm-literal fixed-h loop not detected",
    )
    checks.check(
        source_text.get("source_endpoint_convention_resolved_for_error_sampling") is False,
        "endpoint convention unexpectedly resolved",
    )
    checks.check(
        source_text.get("source_text_confirms_adjusted_h_for_exact_T") is False
        and source_text.get("source_text_confirms_partial_final_step") is False
        and source_text.get("source_text_confirms_interpolation_to_exact_T") is False
        and source_text.get("source_text_confirms_floor_or_nearest_endpoint_sampling") is False,
        "source text overconfirms an endpoint convention",
    )
    literal_rows = source_text.get("algorithm_literal_rows", [])
    checks.check(len(literal_rows) == 6, "algorithm-literal row count changed")
    by_literal_case_h = {(row.get("case_id"), float(row.get("h"))): row for row in literal_rows}
    checks.check(
        by_literal_case_h.get(("frictionless_pendulum", 0.003), {}).get("steps_to_reach_or_exceed_T") == 3334,
        "algorithm-literal h=0.003 step count changed",
    )
    checks.check(
        abs(float(by_literal_case_h.get(("frictionless_pendulum", 0.003), {}).get("algorithm_literal_terminal_time")) - 10.002)
        <= 1.0e-12,
        "algorithm-literal h=0.003 terminal time changed",
    )
    checks.check(
        by_literal_case_h.get(("frictional_pendulum", 0.008), {}).get("hits_exact_T") is True,
        "algorithm-literal h=0.008 exact-T marker changed",
    )

    expected = {
        ("frictionless_pendulum", 0.003): False,
        ("frictionless_pendulum", 0.006): False,
        ("frictionless_pendulum", 0.012): False,
        ("frictional_pendulum", 0.003): False,
        ("frictional_pendulum", 0.008): True,
        ("frictional_pendulum", 0.2): True,
    }
    checks.check(set(by_case_h) == set(expected), "case/h set changed")
    for key, compatible in expected.items():
        row = by_case_h.get(key, {})
        expected_row_id = f"{key[0]}:h={key[1]:.12g}"
        checks.check(row.get("row_id") == expected_row_id, f"{key} row id changed")
        checks.check(row.get("integer_step_compatible") is compatible, f"{key} compatibility changed")
        checks.check(
            row.get("source_endpoint_policy_needed_for_exact_T") is (not compatible),
            f"{key} endpoint-policy-needed marker changed",
        )
        checks.check(math.isfinite(float(row.get("exact_steps"))), f"{key} exact steps not finite")
        checks.check(math.isfinite(float(row.get("t_final_mismatch"))), f"{key} mismatch not finite")
        checks.check(int(row.get("floor_integer_steps")) <= int(row.get("ceil_integer_steps")), f"{key} floor/ceil invalid")
        checks.check(
            math.isfinite(float(row.get("adjusted_h_for_exact_T_using_nearest_steps"))),
            f"{key} adjusted h not finite",
        )
        checks.check(
            0.0 <= float(row.get("final_partial_step_fraction_of_h")) <= 1.0,
            f"{key} final partial step fraction invalid",
        )
        if compatible:
            checks.check(float(row.get("t_final_mismatch")) <= 1.0e-12, f"{key} compatible mismatch too large")
            checks.check(
                float(row.get("final_partial_step_fraction_of_h")) <= 1.0e-12
                or abs(float(row.get("final_partial_step_fraction_of_h")) - 1.0) <= 1.0e-12,
                f"{key} compatible row has unexpected partial step fraction",
            )
        else:
            checks.check(float(row.get("t_final_mismatch")) > 1.0e-12, f"{key} incompatible mismatch too small")
            checks.check(
                0.0 < float(row.get("final_partial_step_fraction_of_h")) < 1.0,
                f"{key} incompatible row should require a fractional final step under partial-step policy",
            )

    execution = audit.get("execution_policy", {})
    checks.check(execution.get("read_only_existing_artifacts") is True, "audit lost read-only marker")
    checks.check(execution.get("default_1e_4_required") is False, "audit requires default 1e-4")
    checks.check(execution.get("heavy_numerical_run_invoked") is False, "audit invoked heavy run")
    checks.check(execution.get("run_v047_invoked") is False, "audit invoked run_v047")
    checks.check(execution.get("v048_runner_invoked") is False, "audit invoked v048 runner")

    for token in [
        "Status: **source horizon step-grid policy open**.",
        "Integer-step compatible rows: `2`.",
        "Integer-step incompatible rows: `4`.",
        "Exact-T compatible rows with endpoint-grid convention resolved: `2`.",
        "Endpoint-incompatible rows requiring source endpoint policy: `4`.",
        "Endpoint-incompatible rows demoted from source-policy row set: `4`.",
        "Exact-T compatible subset grid policy resolved: `True`.",
        "Full T=10 grid policy resolved: `False`.",
        "External superiority claim allowed: `False`.",
        "Endpoint row dispositions recorded: `6`.",
        "Endpoint-compatible future-execution candidates: `2`.",
        "Endpoint-incompatible blocked rows: `4`.",
        "Endpoint-incompatible demoted rows: `4`.",
        "## Endpoint-Grid Subclosure",
        "Only rows whose published h divides T=10 exactly are endpoint-grid resolved.",
        "Demoted incompatible row IDs:",
        "frictional_pendulum:h=0.008",
        "frictional_pendulum:h=0.2",
        "frictionless_pendulum:h=0.003",
        "## Row-Level Promotion Disposition",
        "`endpoint_grid_resolved_pending_runner_contracts`",
        "`blocked_by_endpoint_sampling_policy`",
        "source-confirmed endpoint/output sampling convention for noninteger T/h",
        "## Endpoint Policy Acceptance Contract",
        "Exact-T compatible subset can enter future execution after runner contracts: `True`.",
        "Endpoint-incompatible demoted row IDs:",
        "Demotion contract:",
        "Full T=10 source-policy promotion requires:",
        "Forbidden without contract:",
        "promote endpoint-incompatible rows from diagnostic algorithm-literal probes",
        "Those endpoint-incompatible rows are explicitly demoted from source-policy promotion",
        "## Endpoint Convention Candidates",
        "`algorithm_literal_fixed_h_until_tn_ge_tfinal`",
        "`integer_steps_plus_final_partial_step`",
        "## Required To Accept Full T=10 Rows",
        "## Source-Text Endpoint Convention Audit",
        "Endpoint convention resolved for error sampling: `False`.",
        "Algorithm-Literal Terminal Times",
    ]:
        checks.check(token in text, f"markdown missing token: {token}")

    if checks.errors:
        print("TFE source grid compatibility audit validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("TFE source grid compatibility audit validation: PASS")
    print("rows=6")
    print("integer_step_compatible_rows=2")
    print("integer_step_incompatible_rows=4")
    print("endpoint_compatible_rows_source_endpoint_convention_resolved=2")
    print("source_grid_policy_resolved_for_full_T10=False")
    print("source_policy_rows_completed=0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
