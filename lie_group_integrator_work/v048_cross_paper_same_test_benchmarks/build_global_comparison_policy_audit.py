#!/usr/bin/env python3
"""Build a global comparison-policy audit for all v048 claim artifacts."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
OUT_CSV = RESULTS / "global_comparison_policy_audit.csv"
OUT_JSON = RESULTS / "global_comparison_policy_audit.json"
OUT_MD = RESULTS / "global_comparison_policy_audit.md"

EXAMPLES = ("single_pendulum", "double_pendulum", "four_link", "slider_crank")
LOCAL = "local_Gauss6_FullVA"
OLD_CONTAMINATED_COMMON_REFERENCE_TOKENS = (
    "-2.5083061643786033e+00",
    "-2.3697060455723036e+00",
)


def read_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"refusing to write empty {path.name}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def row(requirement: str, status: bool, evidence: str, interpretation: str) -> dict[str, object]:
    return {
        "requirement": requirement,
        "status": "pass" if status else "fail",
        "evidence": evidence,
        "interpretation": interpretation,
    }


def result_text_corpus() -> tuple[str, list[str]]:
    paths = [
        path
        for path in RESULTS.rglob("*")
        if path.is_file()
        and path.suffix in {".md", ".json"}
        and not path.name.startswith("global_comparison_policy_audit.")
    ]
    texts: list[str] = []
    names: list[str] = []
    for path in sorted(paths):
        texts.append(read_text(path))
        names.append(path.name)
    return "\n".join(texts), names


def common_reference_section(text: str) -> str:
    marker = "## Common-Reference Error Audit"
    if marker not in text:
        return ""
    section = text.split(marker, 1)[1]
    next_marker = "\n## "
    if next_marker in section:
        section = section.split(next_marker, 1)[0]
    return section


def main() -> None:
    common = read_json(RESULTS / "common_reference_error_summary.json")
    common_rows = read_csv(RESULTS / "common_reference_error_summary.csv")
    common_report = read_text(RESULTS / "common_reference_error_summary.md")
    apples = read_json(RESULTS / "apples_to_apples_policy_audit.json")
    apples_rows = read_csv(RESULTS / "apples_to_apples_policy_audit.csv")
    error_policy = read_json(RESULTS / "error_reference_policy_audit.json")
    error_policy_report = read_text(RESULTS / "error_reference_policy_audit.md")
    coarse = read_json(RESULTS / "coarse_four_example_order_summary.json")
    coarse_report = read_text(RESULTS / "coarse_four_example_order_summary.md")
    conclusion = read_text(RESULTS / "coarse_four_example_order_conclusion.md")
    large_vp = read_json(RESULTS / "large_step_vp_local_order_summary.json")
    vp_audit = read_json(RESULTS / "vp_coordinate_partitioning_order_audit.json")
    performance = read_json(RESULTS / "four_example_performance_summary.json")
    performance_report = read_text(RESULTS / "four_example_performance_matrix.md")
    baseline = read_json(RESULTS / "baseline_coverage_matrix.json")
    baseline_report = read_text(RESULTS / "baseline_coverage_matrix.md")
    strict_closed_loop = read_json(RESULTS / "closed_loop_true_dynamic_strict_common_reference.json")
    strict_closed_loop_report = read_text(RESULTS / "closed_loop_true_dynamic_strict_common_reference.md")
    public_work = read_json(RESULTS / "closed_loop_true_dynamic_public_work_precision.json")
    public_work_report = read_text(RESULTS / "closed_loop_true_dynamic_public_work_precision.md")
    single_same_window = read_json(RESULTS / "single_pendulum_coarse_same_window_work_precision_summary.json")
    single_same_window_report = read_text(RESULTS / "single_pendulum_coarse_same_window_work_precision_summary.md")
    dan_single = read_json(RESULTS / "dan_single_pendulum_reference_policy_audit.json")
    forensic = read_json(RESULTS / "all_examples_apples_to_apples_forensic_audit.json")
    forensic_report = read_text(RESULTS / "all_examples_apples_to_apples_forensic_audit.md")
    summary = read_json(RESULTS / "summary_v048.json")
    report = read_text(RESULTS / "v048_report.md")

    corpus, corpus_names = result_text_corpus()
    common_section = common_reference_section(conclusion)
    common_by_example: dict[str, list[dict[str, str]]] = {}
    for item in common_rows:
        common_by_example.setdefault(item["example"], []).append(item)

    bounded_direct_diagnostic_files_ok = (
        "Direct all-row error superiority claim: `True`" in common_report
        and "Bounded direct all-row error diagnostic over accepted runnable rows: `True`" in conclusion
        and "Paper-level direct error superiority allowed after all-example forensic audit: `False`" in conclusion
        and "Direct error superiority allowed for paper: `False`" in forensic_report
    )
    common_section_fresh = (
        "Public-code fixed-grid replay: `True`" in common_report
        and all(token not in common_section for token in OLD_CONTAMINATED_COMMON_REFERENCE_TOKENS)
        and "`single_pendulum` | `5.8013285781956512e+00` | `6.1493372218877035e-15`" in common_section
    )
    all_common_examples_have_local = all(
        any(row.get("method") == LOCAL and row.get("status") == "ok" for row in common_by_example.get(example, []))
        for example in EXAMPLES
    )

    rows = [
        row(
            "common_reference_direct_error_claim_is_bounded_not_paper_superiority",
            common.get("schema") == "common-reference-error-audit-v1"
            and common.get("apples_to_apples_coarse_claim") is True
            and common.get("direct_error_superiority_claim") is True
            and common.get("source_policy_reproduction") is False
            and common.get("public_code_fixed_grid_replay") is True
            and common.get("local_finest_velocity_error_wins") == common.get("local_finest_velocity_error_comparisons") == 40
            and forensic.get("direct_error_superiority_claim_allowed_for_paper") is False
            and bounded_direct_diagnostic_files_ok
            and all_common_examples_have_local,
            "common_reference_error_summary.{json,csv,md}; all_examples_apples_to_apples_forensic_audit.{json,md}",
            "fixed-grid common-reference arithmetic is bounded diagnostic evidence, not a paper-level external-superiority claim",
        ),
        row(
            "all_examples_all_methods_forensic_audit_blocks_external_error_claim",
            forensic.get("schema") == "all-examples-apples-to-apples-forensic-audit-v1"
            and forensic.get("all_examples_checked") is True
            and forensic.get("all_method_example_cells_checked") is True
            and forensic.get("row_count") == 44
            and forensic.get("raw_row_count") == 132
            and forensic.get("strict_external_error_claim_allowed_rows") == 0
            and forensic.get("external_superiority_claim_allowed") is False
            and set(forensic.get("examples", [])) == set(EXAMPLES),
            "all_examples_apples_to_apples_forensic_audit.{json,csv,md}",
            "all four examples and all 44 common-reference method/example cells were checked; no strict external error claim is allowed",
        ),
        row(
            "row_level_apples_to_apples_policy_passes",
            apples.get("schema") == "apples-to-apples-policy-audit-v1"
            and apples.get("row_count") == apples.get("paper_safe_row_count") == 44
            and apples.get("nonlocal_paper_safe_comparison_count") == 40
            and apples.get("public_source_time_grid_caveat_detected") is True
            and apples.get("fixed_grid_wrapper_present") is True
            and apples.get("source_policy_reproduction") is False
            and {item.get("paper_safe_coarse_apples_to_apples") for item in apples_rows} == {"true"},
            "apples_to_apples_policy_audit.{json,csv}",
            "every common-reference summary row shares h-grid, t_end, reference policy, norm, and fixed-grid public replay when needed",
        ),
        row(
            "mixed_policy_direct_error_is_blocked",
            error_policy.get("schema") == "error-reference-policy-audit-v1"
            and error_policy.get("main_row_count") == 52
            and error_policy.get("mixed_policy_direct_error_vs_local_comparable_rows") == 0
            and error_policy.get("direct_error_vs_local_comparable_rows") == 40
            and "mixed reference policies" in error_policy_report
            and "separate common-reference audit" in error_policy_report,
            "error_reference_policy_audit.{json,md}",
            "the main coarse table may support order comparisons, but its mixed-reference error columns are not direct cross-method error claims",
        ),
        row(
            "coarse_conclusion_uses_current_common_reference_numbers",
            common_section_fresh,
            "coarse_four_example_order_conclusion.md",
            "the conclusion common-reference section was regenerated after fixed-grid replay and no longer carries the old Dan/Kissel/Negrut negative-order contamination",
        ),
        row(
            "main_coarse_table_is_not_blanket_error_superiority",
            coarse.get("schema") == "coarse-four-example-order-v1"
            and coarse.get("local_velocity_order_wins") == 43
            and coarse.get("local_velocity_error_wins") == 40
            and coarse.get("local_velocity_error_comparisons") == 43
            and "under each row's own reference policy" in coarse_report
            and "Paper-level direct error superiority allowed: `False`" in conclusion,
            "coarse_four_example_order_summary.{json,md}; coarse_four_example_order_conclusion.md",
            "the coarse matrix reports observed order and row-local errors; direct common-reference error wins remain bounded diagnostics",
        ),
        row(
            "vp_error_order_boundary_is_preserved",
            vp_audit.get("schema") == "vp-coordinate-partitioning-order-audit-v1"
            and vp_audit.get("local_velocity_order_wins") == 4
            and vp_audit.get("vp_finest_velocity_error_wins") == 3
            and vp_audit.get("large_step_local_velocity_order_wins") == 4
            and vp_audit.get("large_step_local_finest_velocity_error_wins") == 1
            and large_vp.get("local_velocity_order_wins") == 4
            and large_vp.get("local_finest_velocity_error_wins") == 1,
            "vp_coordinate_partitioning_order_audit.json; large_step_vp_local_order_summary.json",
            "VP rows preserve the distinction between higher observed order and not winning every reported finest-step error",
        ),
        row(
            "large_step_vp_direct_error_not_overclaimed",
            error_policy.get("large_step_local_velocity_order_wins_vs_vp") == 4
            and error_policy.get("large_step_local_reported_finest_velocity_error_wins_vs_vp") == 1
            and error_policy.get("large_step_local_direct_common_reference_error_wins_vs_vp") == 0,
            "error_reference_policy_audit.json; large_step_vp_local_order_summary.md",
            "larger-step VP diagnostics support an order claim, not a universal direct-error claim",
        ),
        row(
            "coverage_matrix_not_same_test_superiority",
            performance.get("schema") == "four-example-method-performance-matrix-v1"
            and performance.get("same_test_campaign_status") == "not_run"
            and performance.get("external_superiority_claim") is False
            and "coverage ledger, not a completed external superiority claim" in performance_report,
            "four_example_performance_summary.json; four_example_performance_matrix.md",
            "the broad performance matrix is a coverage ledger and does not merge source policies into one same-test claim",
        ),
        row(
            "baseline_resolution_scope_is_explicit",
            baseline.get("schema") == "baseline-coverage-matrix-v1"
            and baseline.get("required_methods_resolved") is True
            and baseline.get("scope_excluded_methods") == ["tfe2026_TFE_m3_GL"]
            and baseline.get("alias_resolved_methods") == ["vp2024_lie_group_ode_partitioning"]
            and baseline.get("common_reference_direct_error_superiority_claim") is True,
            "baseline_coverage_matrix.{json,md}",
            "VP is an alias-resolved method row and TFE(m=3) four-link is excluded; direct-error wording is bounded by the forensic audit",
        ),
        row(
            "closed_loop_strict_common_reference_not_external_superiority",
            strict_closed_loop.get("schema") == "closed-loop-true-dynamic-strict-common-reference-v1"
            and strict_closed_loop.get("strict_common_reference_error_columns") is True
            and strict_closed_loop.get("strict_common_reference_available_count") == 2
            and strict_closed_loop.get("external_superiority_claim") is False
            and "External superiority claim: `False`" in strict_closed_loop_report,
            "closed_loop_true_dynamic_strict_common_reference.{json,md}",
            "closed-loop strict common-reference rows remove a local caveat for two examples but still do not claim full external superiority",
        ),
        row(
            "same_window_and_public_work_rows_are_bounded",
            public_work.get("external_superiority_claim") is False
            and single_same_window.get("external_superiority_claim") is False
            and "not external superiority" in public_work_report
            and "not external superiority" in single_same_window_report,
            "closed_loop_true_dynamic_public_work_precision.json; single_pendulum_coarse_same_window_work_precision_summary.json",
            "same-window work/precision rows are labeled as bounded evidence, not final external superiority",
        ),
        row(
            "dan_single_repair_is_scoped",
            dan_single.get("schema") == "dan-single-pendulum-reference-policy-audit-v1"
            and dan_single.get("negative_common_reference_order_count") == 0
            and dan_single.get("safe_claim_scope") == "coarse_apples_to_apples_fixed_grid_replay_not_source_policy_reproduction"
            and dan_single.get("retract_previous_single_pendulum_dan_claim") is True,
            "dan_single_pendulum_reference_policy_audit.json",
            "the repaired Dan/Kissel/Negrut single-pendulum rows are scoped to fixed-grid apples-to-apples evidence only",
        ),
        row(
            "global_external_superiority_not_claimed",
            summary.get("external_superiority_claim") is False
            and "external_superiority_claim" in summary
            and '"external_superiority_claim": true' not in corpus
            and "External superiority claim: `True`" not in corpus
            and "Gauss6/FullVA has beaten the external baselines" not in corpus
            and "same_test_campaign_status=passed" not in (corpus + "\n" + report),
            f"{len(corpus_names)} result markdown/json files; summary_v048.json; v048_report.md",
            "no generated result artifact claims full external superiority or a completed same-test campaign",
        ),
    ]

    passed = sum(1 for item in rows if item["status"] == "pass")
    summary_out = {
        "schema": "global-comparison-policy-audit-v1",
        "reasonable_apples_to_apples_claims": passed == len(rows),
        "row_count": len(rows),
        "passed_count": passed,
        "failed_requirements": [item["requirement"] for item in rows if item["status"] != "pass"],
        "common_reference_direct_error_superiority_claim": common.get("direct_error_superiority_claim"),
        "paper_direct_error_superiority_claim_allowed": forensic.get(
            "direct_error_superiority_claim_allowed_for_paper"
        ),
        "common_reference_apples_to_apples_rows": apples.get("paper_safe_row_count"),
        "common_reference_total_rows": apples.get("row_count"),
        "mixed_policy_direct_error_vs_local_comparable_rows": error_policy.get(
            "mixed_policy_direct_error_vs_local_comparable_rows"
        ),
        "direct_error_vs_local_comparable_rows": error_policy.get("direct_error_vs_local_comparable_rows"),
        "direct_error_rows_allowed_for_paper": forensic.get("strict_external_error_claim_allowed_rows"),
        "source_policy_reproduction": common.get("source_policy_reproduction"),
        "public_code_fixed_grid_replay": common.get("public_code_fixed_grid_replay"),
        "external_superiority_claim": False,
        "claim_boundary": (
            "The fixed-grid common-reference matrix is a bounded diagnostic. The all-example forensic "
            "audit blocks paper-level direct error superiority until source-policy reproduction, "
            "velocity/output mapping, original TFE setup, and VP code-path issues are closed."
        ),
    }

    write_csv(OUT_CSV, rows)
    with OUT_JSON.open("w", encoding="utf-8") as handle:
        json.dump(summary_out, handle, indent=2, sort_keys=True)
        handle.write("\n")

    lines = [
        "# Global Comparison Policy Audit",
        "",
        f"Reasonable apples-to-apples claims: `{summary_out['reasonable_apples_to_apples_claims']}`.",
        f"Passed requirements: `{summary_out['passed_count']}/{summary_out['row_count']}`.",
        f"Common-reference apples-to-apples rows: `{summary_out['common_reference_apples_to_apples_rows']}/{summary_out['common_reference_total_rows']}`.",
        f"Mixed-policy direct error rows allowed: `{summary_out['mixed_policy_direct_error_vs_local_comparable_rows']}`.",
        f"Direct error rows allowed: `{summary_out['direct_error_vs_local_comparable_rows']}`.",
        f"Paper direct error rows allowed: `{summary_out['direct_error_rows_allowed_for_paper']}`.",
        f"Source-policy reproduction: `{summary_out['source_policy_reproduction']}`.",
        f"Public-code fixed-grid replay: `{summary_out['public_code_fixed_grid_replay']}`.",
        f"External superiority claim: `{summary_out['external_superiority_claim']}`.",
        "",
        "| Requirement | status | evidence | interpretation |",
        "|---|---:|---|---|",
    ]
    for item in rows:
        lines.append(
            "| "
            f"`{item['requirement']}` | `{item['status']}` | `{item['evidence']}` | "
            f"{item['interpretation']} |"
        )
    lines.extend(["", summary_out["claim_boundary"]])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("global_comparison_policy_audit=written")
    print(f"reasonable_apples_to_apples_claims={summary_out['reasonable_apples_to_apples_claims']}")
    print(f"passed={summary_out['passed_count']}/{summary_out['row_count']}")


if __name__ == "__main__":
    main()
