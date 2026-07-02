#!/usr/bin/env python3
"""Validate the CMAME scalability/performance boundary audit."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
AUDIT_JSON = PAPER / "CMAME_SCALABILITY_BOUNDARY_AUDIT.json"
AUDIT_MD = PAPER / "CMAME_SCALABILITY_BOUNDARY_AUDIT.md"


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
        audit = read_json(AUDIT_JSON)
        audit_md = read_text(AUDIT_MD)
    except Exception as exc:  # noqa: BLE001
        print(f"cmame scalability boundary audit validation: FAIL\n- {exc}")
        return 1

    reference = audit.get("current_reference_implementation", {})
    work = audit.get("work_precision_boundary", {})
    campaign = audit.get("scalability_campaign_status", {})
    case_rows = audit.get("case_rows", [])

    checks.check(audit.get("schema") == "cmame-scalability-boundary-audit-v1", "schema changed")
    checks.check(
        audit.get("status") == "reference_implementation_scalability_boundary_recorded_b7_open",
        "status changed",
    )
    checks.check(audit.get("blocker") == "B7", "blocker changed")
    checks.check(audit.get("read_only") is True, "audit must be read-only")
    checks.check(audit.get("run_v047_invoked") is False, "audit must not invoke run_v047.py")
    checks.check(audit.get("submission_ready") is False, "audit must not mark submission ready")
    checks.check(audit.get("b7_closed") is False, "B7 must remain open")
    checks.check(
        audit.get("performance_superiority_claim_allowed") is False,
        "performance superiority overclaimed",
    )
    checks.check(
        audit.get("production_scalability_claim_allowed") is False,
        "production scalability overclaimed",
    )

    checks.check(reference.get("residual_dimension") == 132, "residual dimension changed")
    checks.check(reference.get("pattern_nnz") == [2637], "sparse pattern nnz changed")
    checks.check(reference.get("column_colors") == [90], "column color count changed")
    checks.check(reference.get("row_colors") == [60], "row color count changed")
    checks.check(reference.get("dense_beats_row_all_cases") is True, "dense must beat row in current evidence")
    checks.check(
        reference.get("component_block_assembly_required_all_cases") is True,
        "component/block assembly requirement missing",
    )
    checks.check(1.20 <= float(reference.get("row_runtime_over_dense_min", 0.0)) <= 1.21, "row/dense min drifted")
    checks.check(1.22 <= float(reference.get("row_runtime_over_dense_max", 0.0)) <= 1.23, "row/dense max drifted")
    checks.check(
        0.16 <= float(reference.get("row_runtime_reduction_needed_to_match_dense_min", 0.0)) <= 0.17,
        "dense-match reduction min drifted",
    )
    checks.check(
        0.18 <= float(reference.get("row_runtime_reduction_needed_to_match_dense_max", 0.0)) <= 0.19,
        "dense-match reduction max drifted",
    )
    checks.check(
        49.0 <= float(reference.get("effective_row_colors_at_dense_cost_min", 0.0)) <= 49.1,
        "effective row colors min drifted",
    )
    checks.check(
        49.8 <= float(reference.get("effective_row_colors_at_dense_cost_max", 0.0)) <= 50.0,
        "effective row colors max drifted",
    )

    checks.check(work.get("strict_common_reference_figure_present") is True, "strict work/precision figure missing")
    checks.check(
        work.get("coarse_baseline_work_precision_figure_present") is True,
        "coarse baseline work/precision figure missing",
    )
    checks.check(work.get("sparse_speed_gap_figure_present") is True, "sparse speed figure missing")
    checks.check(work.get("common_reference_order_wins") == 40, "common-reference order win count changed")
    checks.check(work.get("common_reference_error_wins") == 40, "common-reference error win count changed")
    checks.check(work.get("source_policy_closed_rows") == 0, "source-policy closure overclaimed")
    checks.check(work.get("source_policy_total_rows") == 40, "source-policy row total changed")
    checks.check(
        work.get("external_source_policy_superiority_allowed") is False,
        "external source-policy superiority overclaimed",
    )

    checks.check(campaign.get("n_body_chain_sweep_present") is False, "N-body sweep unexpectedly marked present")
    checks.check(campaign.get("requested_body_counts") == [2, 4, 8, 16, 32], "requested N sweep changed")
    checks.check(campaign.get("completed_body_counts") == [], "completed N sweep overclaimed")
    for key in [
        "wall_clock_vs_body_count_present",
        "newton_iterations_vs_body_count_present",
        "jacobian_assembly_vs_body_count_present",
        "linear_solve_time_vs_body_count_present",
        "condition_number_vs_body_count_present",
        "memory_scaling_vs_body_count_present",
    ]:
        checks.check(campaign.get(key) is False, f"scalability campaign overclaimed: {key}")

    checks.check(len(case_rows) == 2, "case row count changed")
    cases = {row.get("case") for row in case_rows if isinstance(row, dict)}
    checks.check(cases == {"cylindrical_smooth", "cylindrical_sharp"}, "case labels changed")
    for row in case_rows:
        if not isinstance(row, dict):
            checks.check(False, "case row is not an object")
            continue
        checks.check(row.get("pattern_nnz") == 2637, f"pattern nnz changed for {row.get('case')}")
        checks.check(row.get("dense_dimension") == 132, f"dense dimension changed for {row.get('case')}")
        checks.check(row.get("column_colors") == 90, f"column colors changed for {row.get('case')}")
        checks.check(row.get("row_colors") == 60, f"row colors changed for {row.get('case')}")
        checks.check(row.get("dense_beats_row") is True, f"dense no longer marked faster for {row.get('case')}")
        checks.check(
            row.get("component_block_assembly_required") is True,
            f"block assembly requirement missing for {row.get('case')}",
        )

    for token in [
        "reference implementation scalability boundary recorded",
        "B7 closed: `False`",
        "Production scalability claim allowed: `False`",
        "Reference residual dimension: `132`",
        "Sparse pattern nonzeros: `2637`",
        "Column/row colors: `90/60`",
        "N-body chain sweep present: `False`",
        "Requested body counts: `N=2,4,8,16,32`",
        "Completed body counts: `[]`",
    ]:
        checks.check(token in audit_md, f"audit markdown missing token: {token}")

    if checks.errors:
        print("cmame scalability boundary audit validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("cmame scalability boundary audit validation: PASS")
    print("b7_closed=False")
    print("residual_dimension=132")
    print("n_body_chain_sweep_present=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
