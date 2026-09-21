#!/usr/bin/env python3
"""Validate the result-to-manuscript traceability audit."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
AUDIT_JSON = PAPER / "RESULT_TO_MANUSCRIPT_TRACEABILITY_AUDIT.json"
AUDIT_MD = PAPER / "RESULT_TO_MANUSCRIPT_TRACEABILITY_AUDIT.md"


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
        manifest = read_json(PAPER / "SUBMISSION_ARTIFACT_MANIFEST.json")
        matrix = read_json(PAPER / "PAPER_NUMERICAL_RESULT_MATRIX.json")
    except Exception as exc:  # noqa: BLE001
        print(f"result-to-manuscript traceability validation: FAIL\n- {exc}")
        return 1

    coverage = audit.get("coverage", {})
    boundary = audit.get("claim_boundary", {})
    policy = audit.get("benchmark_policy_dictionary", {})
    ra2021_boundary = audit.get("ra2021_local_candidate_promotion_boundary", {})

    checks.check(audit.get("schema") == "result-to-manuscript-traceability-audit-v1", "schema changed")
    checks.check(
        audit.get("status") == "all_44_velocity_cells_trace_to_manuscript_and_pdf_source_policy_open",
        "status changed",
    )
    checks.check(audit.get("submission_ready") is False, "audit must not mark submission ready")
    checks.check(audit.get("read_only") is True, "audit must be read-only")
    checks.check(audit.get("run_v047_invoked") is False, "audit must not invoke run_v047")
    checks.check(audit.get("heavy_numerical_run_invoked") is False, "audit must not invoke heavy runs")
    checks.check(audit.get("matrix_schema") == matrix.get("schema") == "paper-numerical-result-matrix-v1", "matrix schema changed")
    checks.check(coverage.get("row_count") == coverage.get("expected_row_count") == 44, "row count changed")
    checks.check(coverage.get("velocity_cells_checked") == 44, "velocity cell count changed")
    checks.check(coverage.get("raw_row_count") == 132, "raw row count changed")
    checks.check(coverage.get("method_count") == 11, "method count changed")
    checks.check(len(coverage.get("examples", [])) == 4, "example count changed")
    checks.check(coverage.get("main_tex_velocity_cells_matched") == 44, "main TeX cells not all matched")
    checks.check(coverage.get("flat_tex_velocity_cells_matched") == 44, "flat TeX cells not all matched")
    checks.check(coverage.get("main_pdf_velocity_cells_matched") == 44, "main PDF cells not all matched")
    checks.check(coverage.get("flat_pdf_velocity_cells_matched") == 44, "flat PDF cells not all matched")
    checks.check(coverage.get("nonlocal_rows") == 40, "nonlocal row count changed")
    checks.check(coverage.get("source_policy_closed_nonlocal_rows") == 0, "source-policy closed nonlocal rows changed")
    checks.check(coverage.get("strict_external_error_claim_allowed_rows") == 0, "strict external error rows changed")
    checks.check(policy.get("main_tex_present") is True, "benchmark-policy dictionary missing from main TeX")
    checks.check(policy.get("flat_tex_present") is True, "benchmark-policy dictionary missing from flat TeX")
    checks.check(policy.get("main_pdf_present") is True, "benchmark-policy dictionary missing from main PDF text")
    checks.check(policy.get("flat_pdf_present") is True, "benchmark-policy dictionary missing from flat PDF text")
    checks.check(policy.get("main_tex_missing_tokens") == [], "main TeX benchmark-policy dictionary tokens missing")
    checks.check(policy.get("flat_tex_missing_tokens") == [], "flat TeX benchmark-policy dictionary tokens missing")
    checks.check(policy.get("main_pdf_missing_tokens") == [], "main PDF benchmark-policy dictionary tokens missing")
    checks.check(policy.get("flat_pdf_missing_tokens") == [], "flat PDF benchmark-policy dictionary tokens missing")
    checks.check(ra2021_boundary.get("main_tex_present") is True, "RA2021 local-candidate boundary missing from main TeX")
    checks.check(ra2021_boundary.get("flat_tex_present") is True, "RA2021 local-candidate boundary missing from flat TeX")
    checks.check(ra2021_boundary.get("main_pdf_present") is True, "RA2021 local-candidate boundary missing from main PDF text")
    checks.check(ra2021_boundary.get("flat_pdf_present") is True, "RA2021 local-candidate boundary missing from flat PDF text")
    checks.check(ra2021_boundary.get("main_tex_missing_tokens") == [], "main TeX RA2021 local-candidate tokens missing")
    checks.check(ra2021_boundary.get("flat_tex_missing_tokens") == [], "flat TeX RA2021 local-candidate tokens missing")
    checks.check(ra2021_boundary.get("main_pdf_missing_tokens") == [], "main PDF RA2021 local-candidate tokens missing")
    checks.check(ra2021_boundary.get("flat_pdf_missing_tokens") == [], "flat PDF RA2021 local-candidate tokens missing")
    checks.check(ra2021_boundary.get("source_policy_rows_closed") == 0, "RA2021 source-policy rows unexpectedly closed")
    checks.check(
        ra2021_boundary.get("public_order_groups_completed")
        == ra2021_boundary.get("public_order_groups_required")
        == 12,
        "RA2021 public order group boundary changed",
    )
    checks.check(
        ra2021_boundary.get("public_timing_rows_completed")
        == ra2021_boundary.get("public_timing_rows_required")
        == 12,
        "RA2021 public timing boundary changed",
    )
    expected_ra2021_statuses = {
        "single_pendulum": "not_promoted_floor_limited_public_h_tranche",
        "double_pendulum": "not_promoted_coarse_h_and_reference_policy_mismatch",
        "four_link": "not_promoted_true_dynamic_not_source_policy_and_public_horizon_not_dynamic_order",
        "slider_crank": "not_promoted_true_dynamic_not_source_policy_and_public_horizon_not_dynamic_order",
    }
    checks.check(
        ra2021_boundary.get("local_candidate_status_by_example") == expected_ra2021_statuses,
        "RA2021 local-candidate promotion statuses changed",
    )
    common_policy = policy.get("common_reference_policy", {})
    checks.check(common_policy.get("time_horizon") == 0.1, "common-reference policy horizon changed")
    checks.check(common_policy.get("step_sizes") == [0.1, 0.05, 0.025], "common-reference policy step sizes changed")
    checks.check(common_policy.get("reference_h") == 0.0125, "common-reference policy reference h changed")
    checks.check(
        common_policy.get("single_pendulum_reference") == "analytic_exact_final_state_final_l2",
        "single-pendulum reference policy changed",
    )
    checks.check(
        common_policy.get("double_pendulum_reference") == "local_fullva_h_ref_0.0125_final_state_final_linf",
        "double-pendulum reference policy changed",
    )
    checks.check(
        common_policy.get("four_link_slider_crank_reference")
        == "closed_loop_true_dynamic_common_reference_h_ref_0.0125",
        "closed-loop reference policy changed",
    )

    for location in ["main_tex", "flat_tex", "main_pdf_text", "flat_pdf_text"]:
        checks.check(audit.get(location, {}).get("table_found") is True, f"{location} table missing")
        checks.check(audit.get(location, {}).get("missing_items") == [], f"{location} has missing items")

    checks.check(
        boundary.get("result_to_manuscript_traceability_closed") is True,
        "result-to-manuscript traceability not closed",
    )
    checks.check(boundary.get("source_policy_reproduction_closed") is False, "source-policy overclaimed")
    checks.check(boundary.get("external_superiority_claim_allowed") is False, "external superiority overclaimed")
    checks.check(boundary.get("direct_error_superiority_claim_allowed") is False, "direct error superiority overclaimed")
    checks.check(boundary.get("submission_ready") is False, "boundary overclaims submission readiness")

    checks.check(
        manifest.get("result_to_manuscript_traceability_audit") == "RESULT_TO_MANUSCRIPT_TRACEABILITY_AUDIT.md",
        "manifest missing result-to-manuscript audit",
    )
    checks.check(
        manifest.get("result_to_manuscript_traceability_audit_json") == "RESULT_TO_MANUSCRIPT_TRACEABILITY_AUDIT.json",
        "manifest missing result-to-manuscript audit JSON",
    )
    checks.check(
        "RESULT_TO_MANUSCRIPT_TRACEABILITY_AUDIT.md" in manifest.get("evidence_anchors", []),
        "manifest missing result-to-manuscript audit anchor",
    )
    checks.check(
        "RESULT_TO_MANUSCRIPT_TRACEABILITY_AUDIT.json" in manifest.get("evidence_anchors", []),
        "manifest missing result-to-manuscript audit JSON anchor",
    )
    checks.check(
        "validate_result_to_manuscript_traceability_audit.py" in manifest.get("validators", []),
        "manifest missing result-to-manuscript audit validator",
    )

    for token in [
        "Velocity cells checked: `44/44`.",
        "Main TeX/PDF matched cells: `44/44`.",
        "Flat TeX/PDF matched cells: `44/44`.",
        "Source-policy-closed nonlocal rows: `0`.",
        "Benchmark-policy dictionary present in main/flat TeX and PDF: `True/True/True/True`.",
        "External superiority claim allowed: `False`.",
        "Submission ready: `False`.",
    ]:
        checks.check(token in audit_md, f"audit markdown missing token: {token}")

    if checks.errors:
        print("result-to-manuscript traceability validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("result-to-manuscript traceability validation: PASS")
    print("velocity_cells_checked=44/44")
    print("main_tex_pdf_cells=44/44")
    print("flat_tex_pdf_cells=44/44")
    print("source_policy_reproduction_closed=False")
    print("external_superiority_claim_allowed=False")
    print("submission_ready=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
