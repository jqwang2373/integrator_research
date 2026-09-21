#!/usr/bin/env python3
"""Validate the row-level source-policy closure ledger."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
EXPECTED_EXAMPLES = {"single_pendulum", "double_pendulum", "four_link", "slider_crank"}
EXPECTED_EXAMPLE_COUNTS = {
    "single_pendulum": 8,
    "double_pendulum": 2,
    "four_link": 4,
    "slider_crank": 1,
}
EXPECTED_ACTION_COUNTS = {
    "choose_full_T8_public_policy_or_demote": 3,
    "demote_until_velocity_partitioning_code_path_resolved": 3,
    "fix_or_rerun_public_velocity_mapping_time_grid_norm_runtime": 5,
    "resolve_tfe_runner_friction_endpoint_then_rerun_or_demote": 4,
}
EXPECTED_SUITE_COUNTS = {
    "hi2022_half_implicit": 3,
    "ra2021_absolute_coordinate": 5,
    "tfe2026_original_pendulum": 4,
    "vp2024_velocity_partitioning": 3,
}


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
        ledger = read_json(PAPER / "SOURCE_POLICY_ROW_CLOSURE_LEDGER.json")
        ledger_md = read_text(PAPER / "SOURCE_POLICY_ROW_CLOSURE_LEDGER.md")
        triage = read_json(PAPER / "SOURCE_POLICY_CLOSURE_TRIAGE.json")
        all_source = read_json(PAPER / "ALL_EXAMPLES_SOURCE_POLICY_AUDIT.json")
        queue = read_json(PAPER / "EXTERNAL_SAME_TEST_RUN_QUEUE.json")
        manifest = read_json(PAPER / "SUBMISSION_ARTIFACT_MANIFEST.json")
        ra2021_source_identity = read_json(PAPER / "RA2021_SOURCE_IDENTITY_AUDIT.json")
        source_policy_self_reproduction = read_json(PAPER / "SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_AUDIT.json")
        tfe_public_code_recheck = read_json(PAPER / "TFE_PUBLIC_CODE_RECHECK_20260613.json")
        vp2024_public_code_recheck = read_json(PAPER / "VP2024_PUBLIC_CODE_RECHECK_20260613.json")
    except Exception as exc:  # noqa: BLE001
        print(f"source-policy row closure ledger validation: FAIL\n- {exc}")
        return 1

    coverage = ledger.get("coverage", {})
    execution = ledger.get("execution_policy", {})
    closure = ledger.get("closure_rule", {})
    rows = ledger.get("rows", [])

    checks.check(ledger.get("schema") == "source-policy-row-closure-ledger-v1", "schema changed")
    checks.check(ledger.get("status") == "row_level_source_policy_closure_open", "status changed")
    checks.check(ledger.get("submission_ready") is False, "ledger must not mark submission ready")
    checks.check(ledger.get("external_superiority_claim") is False, "ledger must not claim external superiority")
    checks.check(ledger.get("source_policy_superiority_claim_allowed") is False, "source-policy boundary changed")
    checks.check(coverage.get("flagged_row_count") == len(rows) == 15, "flagged row count changed")
    checks.check(set(coverage.get("flagged_examples", [])) == EXPECTED_EXAMPLES, "flagged examples changed")
    checks.check(coverage.get("all_four_examples_covered") is True, "all-four-example marker missing")
    checks.check(coverage.get("flagged_by_example") == EXPECTED_EXAMPLE_COUNTS, "by-example counts changed")
    checks.check(coverage.get("flagged_by_suite") == EXPECTED_SUITE_COUNTS, "suite counts changed")
    checks.check(coverage.get("action_counts") == EXPECTED_ACTION_COUNTS, "action counts changed")
    checks.check(coverage.get("rows_source_policy_closed") == 0, "source-policy rows unexpectedly closed")
    checks.check(coverage.get("rows_external_superiority_ready") == 0, "rows unexpectedly external-superiority ready")
    checks.check(execution.get("read_only_existing_artifacts") is True, "ledger is not read-only")
    checks.check(execution.get("default_1e_4_required") is False, "ledger requires default 1e-4")
    checks.check(execution.get("heavy_numerical_run_invoked") is False, "ledger invoked a heavy run")
    checks.check(execution.get("run_v047_invoked") is False, "ledger invoked run_v047")
    checks.check(execution.get("v048_runner_invoked") is False, "ledger invoked v048 runner")
    checks.check(
        execution.get("parallel_ready_shards_without_default_1e_4")
        == queue.get("coverage_counts", {}).get("parallel_shard_count_without_default_1e-4")
        == 20,
        "parallel shard count changed",
    )
    checks.check(closure.get("b2_can_close_now") is False, "ledger incorrectly closes B2")
    checks.check(closure.get("b4_can_close_now") is False, "ledger incorrectly closes B4")
    checks.check(closure.get("all_rows_must_be_closed_or_demoted") is True, "closure rule weakened")
    checks.check(closure.get("row_demotions_must_be_stated_in_manuscript") is True, "demotion rule missing")
    ra_status = ledger.get("suite_closure_status", {}).get("ra2021_absolute_coordinate", {})
    checks.check(
        ra_status.get("source_identity_status") == ra2021_source_identity.get("status"),
        "RA2021 identity status not propagated",
    )
    checks.check(
        ra_status.get("source_identity_resolved_evidence_per_row") == 3,
        "RA2021 resolved evidence count changed",
    )
    checks.check(
        ra_status.get("source_policy_promotion_evidence_remaining_per_row") == 4,
        "RA2021 remaining promotion count changed",
    )
    checks.check(
        ra_status.get("output_mapping_verified_from_source") is True,
        "RA2021 source output mapping not propagated",
    )
    checks.check(
        ra_status.get("time_grid_policy_extracted_from_source") is True,
        "RA2021 source time-grid policy not propagated",
    )
    tfe_status = ledger.get("suite_closure_status", {}).get("tfe2026_original_pendulum", {})
    checks.check(
        tfe_status.get("status") == "attempted_not_reproducible_not_promoted_source_policy_rows_not_closed",
        "TFE suite status stale",
    )
    checks.check(
        tfe_status.get("public_code_recheck_status") == tfe_public_code_recheck.get("status"),
        "TFE public-code recheck status not propagated",
    )
    checks.check(
        tfe_status.get("self_reproduction_attempt_status") == source_policy_self_reproduction.get("status"),
        "TFE self-reproduction status not propagated",
    )
    checks.check(tfe_status.get("attempted_not_reproducible_rows") == 16, "TFE attempted rows changed")
    vp_status = ledger.get("suite_closure_status", {}).get("vp2024_velocity_partitioning", {})
    checks.check(
        vp_status.get("status") == "attempted_not_reproducible_not_promoted_no_distinct_public_code_path",
        "VP2024 suite status stale",
    )
    checks.check(
        vp_status.get("public_code_recheck_status") == vp2024_public_code_recheck.get("status"),
        "VP2024 public-code recheck status not propagated",
    )
    checks.check(
        vp_status.get("self_reproduction_attempt_status") == source_policy_self_reproduction.get("status"),
        "VP2024 self-reproduction status not propagated",
    )
    checks.check(vp_status.get("attempted_not_reproducible_rows") == 4, "VP2024 attempted rows changed")
    checks.check(
        coverage.get("flagged_row_count") == triage.get("triage_scope", {}).get("flagged_row_count"),
        "ledger/triage flagged row mismatch",
    )
    checks.check(
        coverage.get("flagged_row_count") == all_source.get("coverage", {}).get("flagged_row_count"),
        "ledger/all-source audit flagged row mismatch",
    )
    checks.check(
        coverage.get("flagged_by_example") == triage.get("triage_scope", {}).get("flagged_by_example"),
        "ledger/triage by-example count mismatch",
    )
    checks.check(
        coverage.get("flagged_by_example") == all_source.get("coverage", {}).get("flagged_by_example"),
        "ledger/all-source audit by-example count mismatch",
    )

    ledger_keys = {
        (row.get("suite"), row.get("method"), row.get("example"), row.get("action_class"))
        for row in rows
        if isinstance(row, dict)
    }
    triage_keys = {
        (row.get("suite"), row.get("method"), row.get("example"), row.get("action_class"))
        for row in triage.get("triage_rows", [])
        if isinstance(row, dict)
    }
    all_source_keys = {
        (row.get("suite"), row.get("method"), row.get("example"))
        for row in all_source.get("row_audits", [])
        if isinstance(row, dict)
    }
    ledger_source_keys = {(suite, method, example) for suite, method, example, _action in ledger_keys}
    checks.check(ledger_keys == triage_keys, "ledger rows do not exactly match source-policy triage rows")
    checks.check(ledger_source_keys == all_source_keys, "ledger rows do not exactly match all-example audit rows")
    for example, count in EXPECTED_EXAMPLE_COUNTS.items():
        checks.check(
            sum(1 for row in rows if row.get("example") == example) == count,
            f"ledger row count changed for {example}",
        )
    for row in rows:
        checks.check(row.get("source_policy_closed") is False, f"row unexpectedly closed: {row}")
        checks.check(row.get("can_support_external_superiority") is False, f"row unexpectedly claim-ready: {row}")
        if row.get("suite") in {"tfe2026_original_pendulum", "vp2024_velocity_partitioning"}:
            checks.check(
                row.get("current_allowed_use") == "attempted_not_reproducible_not_promoted_diagnostic_only",
                f"row attempted-not-reproducible use not propagated: {row}",
            )
            checks.check(
                row.get("display_action") == "attempted_not_reproducible_not_promoted",
                f"row display action stale: {row}",
            )
            checks.check(
                row.get("post_public_code_disposition") == "attempted_not_reproducible_not_promoted",
                f"row public-code disposition missing: {row}",
            )
        else:
            checks.check(row.get("current_allowed_use") == "diagnostic_common_reference_only", f"row use changed: {row}")
        checks.check(
            isinstance(row.get("current_evidence", {}).get("velocity_order"), (int, float)),
            f"row missing velocity order: {row}",
        )
        checks.check(
            isinstance(row.get("current_evidence", {}).get("finest_velocity_error"), (int, float)),
            f"row missing finest velocity error: {row}",
        )
        if row.get("suite") == "ra2021_absolute_coordinate":
            checks.check(len(row.get("required_evidence", [])) == 4, f"RA2021 row remaining evidence count changed: {row}")
            checks.check(row.get("missing_evidence_count") == 4, f"RA2021 missing evidence count changed: {row}")
            checks.check(row.get("resolved_evidence_count") == 3, f"RA2021 resolved evidence count changed: {row}")
            joined_missing = " ".join(str(item) for item in row.get("missing_evidence", []))
            checks.check("public code path" not in joined_missing, f"RA2021 row keeps resolved code path open: {row}")
            checks.check("body.r/body.dr/body.ddr" not in joined_missing, f"RA2021 row keeps resolved output mapping open: {row}")
            checks.check("endpoint time-grid convention" not in joined_missing, f"RA2021 row keeps resolved time grid open: {row}")
            risks = row.get("current_evidence", {}).get("source_policy_risks", [])
            checks.check(
                "state_velocity_output_mapping_requires_recheck" not in risks,
                f"RA2021 row keeps resolved velocity-mapping risk open: {row}",
            )
            checks.check(
                "local_Gauss6_FullVA_source_policy_promotion_open" in risks,
                f"RA2021 row missing local-promotion risk: {row}",
            )
        elif row.get("suite") == "tfe2026_original_pendulum":
            checks.check(len(row.get("required_evidence", [])) == 5, f"TFE row remaining evidence count changed: {row}")
            checks.check(row.get("missing_evidence_count") == 5, f"TFE missing evidence count changed: {row}")
            checks.check(row.get("resolved_evidence_count") == 3, f"TFE resolved evidence count changed: {row}")
            joined_resolved = " ".join(str(item) for item in row.get("resolved_evidence", []))
            checks.check("source pendulum body/setup parameters encoded" in joined_resolved, f"TFE setup evidence missing: {row}")
            checks.check("source coordinate/velocity output and error norm policy encoded" in joined_resolved, f"TFE output evidence missing: {row}")
            checks.check("source-reference feasibility probe completed" in joined_resolved, f"TFE source-reference probe evidence missing: {row}")
            joined_missing = " ".join(str(item) for item in row.get("missing_evidence", []))
            checks.check("source-code-equivalent Brown--McPhee friction law" in joined_missing, f"TFE Brown-McPhee missing evidence absent: {row}")
            checks.check("monolithic absolute-coordinate source-policy DAE runner" in joined_missing, f"TFE DAE runner missing evidence absent: {row}")
            risks = row.get("current_evidence", {}).get("source_policy_risks", [])
            checks.check("source_pendulum_setup_not_encoded" not in risks, f"TFE row keeps stale setup risk: {row}")
            checks.check("source_error_norm_and_output_policy_not_encoded" not in risks, f"TFE row keeps stale output-policy risk: {row}")
            checks.check("source_policy_DAE_runner_equivalence_open" in risks, f"TFE row missing DAE-equivalence risk: {row}")
            checks.check("brown_mcphee_source_code_equivalent_law_open" in risks, f"TFE row missing Brown-McPhee risk: {row}")
            checks.check("full_T10_endpoint_policy_open" in risks, f"TFE row missing endpoint-policy risk: {row}")
        else:
            checks.check(len(row.get("required_evidence", [])) >= 5, f"row missing evidence requirements: {row}")
            checks.check(row.get("missing_evidence_count") == len(row.get("required_evidence", [])), f"row missing evidence count stale: {row}")
            checks.check(row.get("resolved_evidence_count") == 0, f"non-RA2021 row unexpectedly has resolved evidence: {row}")
        checks.check(row.get("missing_evidence") == row.get("required_evidence"), f"row missing-evidence list stale: {row}")
        checks.check(row.get("queue", {}).get("batch_id"), f"row missing queue batch: {row}")

    checks.check(
        manifest.get("source_policy_row_closure_ledger") == "SOURCE_POLICY_ROW_CLOSURE_LEDGER.md",
        "manifest ledger path missing",
    )
    checks.check(
        manifest.get("source_policy_row_closure_ledger_json") == "SOURCE_POLICY_ROW_CLOSURE_LEDGER.json",
        "manifest ledger JSON path missing",
    )
    checks.check(
        "SOURCE_POLICY_ROW_CLOSURE_LEDGER.md" in manifest.get("evidence_anchors", []),
        "manifest ledger MD anchor missing",
    )
    checks.check(
        "SOURCE_POLICY_ROW_CLOSURE_LEDGER.json" in manifest.get("evidence_anchors", []),
        "manifest ledger JSON anchor missing",
    )
    checks.check(
        "validate_source_policy_row_closure_ledger.py" in manifest.get("validators", []),
        "manifest ledger validator missing",
    )

    for token in [
        "ROW-LEVEL SOURCE-POLICY CLOSURE OPEN",
        "Flagged source-policy rows: `15`",
        "Rows source-policy closed: `0`",
        "Rows external-superiority ready: `0`",
        "B2/B4 can close now: `False/False`",
        "RA2021 resolved source-identity evidence per active row: `3`; remaining promotion evidence per active row: `4`.",
        "Parallel-ready shards without default `1e-4`: `20`",
        "| `single_pendulum` | 8 |",
        "| `double_pendulum` | 2 |",
        "| `four_link` | 4 |",
        "| `slider_crank` | 1 |",
        "| suite | example | method | velocity order | finest velocity error | disposition/action | missing evidence count | allowed use |",
        "| `hi2022_half_implicit` | `four_link` | `hi2022_rA` | 1.02 | 1.970e-01 |",
        "| `tfe2026_original_pendulum` | `single_pendulum` | `tfe2026_Newmark_beta` | 0.901 | 1.479e+01 | `attempted_not_reproducible_not_promoted` |",
        "| `vp2024_velocity_partitioning` |",
        "`attempted_not_reproducible_not_promoted_diagnostic_only`",
        "Fixed-grid common-reference arithmetic alone is not a",
    ]:
        checks.check(token in ledger_md, f"ledger markdown missing token: {token}")

    if checks.errors:
        print("source-policy row closure ledger validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("source-policy row closure ledger validation: PASS")
    print("flagged_rows=15")
    print("examples=single_pendulum,double_pendulum,four_link,slider_crank")
    print("rows_source_policy_closed=0")
    print("rows_external_superiority_ready=0")
    print("parallel_ready_shards_without_default_1e_4=20")
    print("b2_b4_can_close_now=False/False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
