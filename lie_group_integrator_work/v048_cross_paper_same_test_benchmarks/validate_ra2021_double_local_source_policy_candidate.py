#!/usr/bin/env python3
"""Validate the isolated RA2021 double local source-policy candidate artifact."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
STEM = "ra2021_double_local_source_policy_candidate"


class Checks:
    def __init__(self) -> None:
        self.errors: list[str] = []

    def check(self, condition: bool, message: str) -> None:
        if not condition:
            self.errors.append(message)


def read_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    checks = Checks()
    rows_path = RESULTS / f"{STEM}_rows.csv"
    summary_path = RESULTS / f"{STEM}_summary.json"
    md_path = RESULTS / f"{STEM}.md"
    try:
        rows = read_csv(rows_path)
        summary = read_json(summary_path)
        md = md_path.read_text(encoding="utf-8")
    except Exception as exc:  # noqa: BLE001
        print(f"RA2021 double local source-policy candidate validation: FAIL\n- {exc}")
        return 1

    ok_rows = [row for row in rows if row.get("status") == "ok"]
    planned_rows = [row for row in rows if row.get("status") == "planned_not_run"]
    phase = summary.get("execution_phase", summary.get("execution_mode"))
    status = summary.get("status")
    allowed_statuses = {
        "planned_isolated_source_policy_candidate",
        "reference_failed_isolated_source_policy_candidate",
        "reference_checkpointed_isolated_source_policy_candidate",
        "reference_cached_isolated_source_policy_candidate",
        "partially_executed_isolated_source_policy_candidate",
        "executed_isolated_source_policy_candidate",
    }
    checks.check(summary.get("schema") == "ra2021-double-local-source-policy-candidate-v1", "schema changed")
    checks.check(status in allowed_statuses, "status changed")
    checks.check(phase in {"plan", "reference", "candidate", "all", "plan_only"}, "execution phase changed")
    if phase in {"plan", "plan_only"}:
        checks.check(summary.get("execute_requested") is False, "plan artifact unexpectedly requested execution")
        checks.check(summary.get("heavy_numerical_run_invoked") is False, "plan artifact invoked heavy numerical run")
    else:
        checks.check(summary.get("execute_requested") is True, "executed artifact did not record execution request")
        checks.check(summary.get("heavy_numerical_run_invoked") is True, "executed artifact did not record heavy run")
    checks.check(summary.get("source_policy_contract_selected") is True, "source-policy contract not selected")
    checks.check(summary.get("source_policy_time_window_selected") is True, "source-policy T window not selected")
    checks.check(summary.get("source_policy_step_trio_selected") is True, "source-policy h trio not selected")
    checks.check(summary.get("source_policy_reference_h_selected") is True, "source-policy reference h not selected")
    checks.check(summary.get("selected_step_sizes") == [0.01, 0.002, 0.001], "selected h trio changed")
    checks.check(summary.get("selected_reference_h") == 0.0001, "selected reference h changed")
    checks.check(summary.get("selected_t_end") == 3.0, "selected T changed")
    checks.check(summary.get("estimated_reference_steps") == 30000, "reference step estimate changed")
    checks.check(summary.get("estimated_candidate_steps") == [300, 1500, 3000], "candidate step estimates changed")
    checks.check(summary.get("row_count") == len(rows) == 3, "row count changed")
    checks.check(summary.get("ok_row_count") == len(ok_rows), "ok-row count stale")
    checks.check(summary.get("planned_row_count") == len(planned_rows), "planned-row count stale")
    checks.check(
        summary.get("source_policy_candidate_rows_completed") == len(ok_rows),
        "candidate row completion count stale",
    )
    checks.check(summary.get("source_policy_reproduction_rows_promoted") == 0, "source-policy rows overpromoted")
    checks.check(summary.get("promotion_ready") is False, "promotion readiness overclaimed")
    checks.check(
        summary.get("source_policy_order_acceptance_threshold") == 5.5,
        "source-policy order acceptance threshold changed",
    )
    if len(ok_rows) == len(rows):
        checks.check(
            summary.get("source_policy_order_acceptance_satisfied") is False,
            "low-order isolated rows should not satisfy source-policy order acceptance",
        )
        checks.check(
            any("observed source-policy order is below sixth-order acceptance" in item for item in summary.get("promotion_blockers", [])),
            "summary missing low-order promotion blocker",
        )
    checks.check(
        summary.get("canonical_coarse_output_untouched_by_writer") is True,
        "canonical coarse output protection marker missing",
    )
    checks.check(
        summary.get("isolated_rows_output") == f"{STEM}_rows.csv",
        "isolated rows output name changed",
    )
    checks.check(summary.get("reference_cache_path") == f"{STEM}_reference_h0p0001_T3.npz", "reference cache name changed")
    checks.check(
        summary.get("reference_checkpoint_path") == f"{STEM}_reference_h0p0001_T3_checkpoint.npz",
        "reference checkpoint name changed",
    )
    checks.check(isinstance(summary.get("reference_cache_exists"), bool), "reference cache marker missing")
    checks.check(isinstance(summary.get("reference_checkpoint_exists"), bool), "reference checkpoint marker missing")
    checks.check(
        summary.get("jax_safe_small_angle_patch_enabled") is True,
        "JAX-safe small-angle patch should be enabled for the isolated candidate",
    )
    checks.check(
        summary.get("jax_safe_small_angle_patch_id") == "isolated_v013_jax_safe_small_angle_taylor_v1",
        "JAX-safe small-angle patch id changed",
    )
    checks.check(
        summary.get("jax_safe_small_angle_patch_scope") == "isolated_runtime_loaded_v029_module_only",
        "JAX-safe small-angle patch scope changed",
    )
    if status == "reference_failed_isolated_source_policy_candidate":
        checks.check(str(summary.get("reference_status", "")).startswith("reference_failed"), "failed status without reference failure")
        checks.check(summary.get("reference_completed") is False, "failed reference should not be complete")
        checks.check(summary.get("reference_cache_exists") is False, "failed reference should not write final cache")
        checks.check(isinstance(summary.get("reference_failure_kind"), str), "reference failure kind missing")
        checks.check(isinstance(summary.get("reference_failure_message"), str), "reference failure message missing")
    if status == "reference_checkpointed_isolated_source_policy_candidate":
        checks.check(summary.get("reference_checkpoint_exists") is True, "checkpointed status without checkpoint")
        checks.check(summary.get("reference_completed") is False, "checkpointed status should not complete reference")
        checks.check(isinstance(summary.get("reference_checkpoint_step"), int), "checkpoint step missing")
        checks.check(summary.get("reference_cache_exists") is False, "checkpointed status should not have final cache")

    hs = sorted(float(row["h"]) for row in rows)
    checks.check(hs == [0.001, 0.002, 0.01], "row h values changed")
    for row in rows:
        checks.check(row.get("status") in {"planned_not_run", "ok"} or str(row.get("status", "")).startswith("failed:"), f"row {row.get('h')} status changed")
        checks.check(row.get("execution_mode") in {"plan", "reference", "candidate", "all", "plan_only"}, f"row {row.get('h')} execution mode changed")
        checks.check(row.get("source_policy_contract_selected") == "True", f"row {row.get('h')} contract marker missing")
        checks.check(row.get("source_policy_reference_h") == "True", f"row {row.get('h')} reference marker missing")
        checks.check(row.get("reference_h") == "0.0001", f"row {row.get('h')} reference h changed")
        checks.check(row.get("t_end") == "3.0", f"row {row.get('h')} T changed")
        checks.check(row.get("jax_safe_small_angle_patch_enabled") == "True", f"row {row.get('h')} patch marker missing")
        checks.check(
            row.get("jax_safe_small_angle_patch_id") == "isolated_v013_jax_safe_small_angle_taylor_v1",
            f"row {row.get('h')} patch id changed",
        )
        checks.check(
            row.get("row_type") == "source_policy_local_fullva_dynamic_order_candidate",
            f"row {row.get('h')} row type changed",
        )

    for token in [
        "Source-policy contract selected: `True`.",
        "Estimated reference steps: `30000`.",
        "Reference checkpoint exists:",
        "Reference completed:",
        "Reference status:",
        "JAX-safe small-angle patch enabled: `True`.",
        "JAX-safe small-angle patch id: `isolated_v013_jax_safe_small_angle_taylor_v1`.",
        "Promotion ready: `False`.",
        "Canonical coarse output untouched by this writer: `True`.",
        "execute the exact h_ref=1e-4 reference and three candidate rows",
    ]:
        checks.check(token in md, f"markdown missing token: {token}")
    checks.check(f"Status: **{status}**." in md, "markdown status stale")
    checks.check(f"Execution phase: `{phase}`." in md, "markdown phase stale")
    checks.check(
        f"Rows completed in this artifact: `{len(ok_rows)}`." in md,
        "markdown completed-row count stale",
    )

    if checks.errors:
        print("RA2021 double local source-policy candidate validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("RA2021 double local source-policy candidate validation: PASS")
    print(f"phase={phase}")
    print("source_policy_contract_selected=True")
    print("estimated_reference_steps=30000")
    print(f"source_policy_candidate_rows_completed={len(ok_rows)}/3")
    return 0


if __name__ == "__main__":
    sys.exit(main())
