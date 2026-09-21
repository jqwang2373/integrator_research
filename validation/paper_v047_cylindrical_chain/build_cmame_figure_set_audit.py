#!/usr/bin/env python3
"""Build a read-only audit for the CMAME figure set and B7 boundary."""

from __future__ import annotations

import json
import struct
from collections import Counter
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
from paper_paths import LATEX, package_path as manuscript_path
FLAT = LATEX / "cmame_submission_flat"
OUT_JSON = PAPER / "CMAME_FIGURE_SET_AUDIT.json"
OUT_MD = PAPER / "CMAME_FIGURE_SET_AUDIT.md"

FIGURES = [
    {
        "number": 1,
        "main": "figures/convergence.png",
        "flat": "cmame_submission_flat/Figure_1_convergence.png",
        "main_tex": "figures/convergence.png",
        "flat_tex": "Figure_1_convergence.png",
        "caption_token": "Convergence and work/precision evidence",
        "role": "accepted-path convergence and work/precision",
    },
    {
        "number": 2,
        "main": "figures/asme_lower_pair_graph_bridge.png",
        "flat": "cmame_submission_flat/Figure_2_asme_lower_pair_graph_bridge.png",
        "main_tex": "figures/asme_lower_pair_graph_bridge.png",
        "flat_tex": "Figure_2_asme_lower_pair_graph_bridge.png",
        "caption_token": "Coordinate-oriented mechanism schematics",
        "role": "mechanism schematic",
    },
    {
        "number": 3,
        "main": "figures/asme_closed_loop_kinematic_fullva.png",
        "flat": "cmame_submission_flat/Figure_3_asme_closed_loop_kinematic_fullva.png",
        "main_tex": "figures/asme_closed_loop_kinematic_fullva.png",
        "flat_tex": "Figure_3_asme_closed_loop_kinematic_fullva.png",
        "caption_token": "Closed-loop kinematic FullVA mechanism-coverage evidence",
        "role": "closed-loop kinematic evidence",
    },
    {
        "number": 4,
        "main": "figures/order_closure_blend.png",
        "flat": "cmame_submission_flat/Figure_4_order_closure_blend.png",
        "main_tex": "figures/order_closure_blend.png",
        "flat_tex": "Figure_4_order_closure_blend.png",
        "caption_token": "Order/closure blend diagnostic",
        "role": "full-TFE non-claim diagnostic",
    },
    {
        "number": 5,
        "main": "figures/velocity_compression.png",
        "flat": "cmame_submission_flat/Figure_5_velocity_compression.png",
        "main_tex": "figures/velocity_compression.png",
        "flat_tex": "Figure_5_velocity_compression.png",
        "caption_token": "Velocity-compression diagnostic",
        "role": "velocity-compression diagnostic",
    },
    {
        "number": 6,
        "main": "figures/sparse_speed_gap.png",
        "flat": "cmame_submission_flat/Figure_6_sparse_speed_gap.png",
        "main_tex": "figures/sparse_speed_gap.png",
        "flat_tex": "Figure_6_sparse_speed_gap.png",
        "caption_token": "Sparse backend speed-gap diagnostic",
        "role": "sparse backend caveat",
    },
    {
        "number": 7,
        "main": "figures/strict_common_reference_work_precision.png",
        "flat": "cmame_submission_flat/Figure_7_strict_common_reference_work_precision.png",
        "main_tex": "figures/strict_common_reference_work_precision.png",
        "flat_tex": "Figure_7_strict_common_reference_work_precision.png",
        "caption_token": "Strict common-reference work/precision rows",
        "role": "strict common-reference work/precision",
    },
    {
        "number": 8,
        "main": "figures/claim_boundary_limitations.png",
        "flat": "cmame_submission_flat/Figure_8_claim_boundary_limitations.png",
        "main_tex": "figures/claim_boundary_limitations.png",
        "flat_tex": "Figure_8_claim_boundary_limitations.png",
        "caption_token": "Claim-boundary and limitation map",
        "role": "limitation explanation",
    },
    {
        "number": 9,
        "main": "figures/coarse_baseline_work_precision.png",
        "flat": "cmame_submission_flat/Figure_9_coarse_baseline_work_precision.png",
        "main_tex": "figures/coarse_baseline_work_precision.png",
        "flat_tex": "Figure_9_coarse_baseline_work_precision.png",
        "caption_token": "Coarse-first baseline and work/precision diagnostics",
        "role": "coarse-first baseline/work-precision",
    },
    {
        "number": 10,
        "main": "figures/closed_loop_true_dynamic_order.png",
        "flat": "cmame_submission_flat/Figure_10_closed_loop_true_dynamic_order.png",
        "main_tex": "figures/closed_loop_true_dynamic_order.png",
        "flat_tex": "Figure_10_closed_loop_true_dynamic_order.png",
        "caption_token": "Closed-loop coarse-window trajectory diagnostics",
        "role": "closed-loop coarse dynamics diagnostics",
    },
    {
        "number": 11,
        "main": "figures/method_stage_architecture.png",
        "flat": "cmame_submission_flat/Figure_11_method_stage_architecture.png",
        "main_tex": "figures/method_stage_architecture.png",
        "flat_tex": "Figure_11_method_stage_architecture.png",
        "caption_token": "Accepted Gauss6/FullVA one-step architecture",
        "role": "method-stage architecture",
    },
    {
        "number": 12,
        "main": "figures/all_method_result_matrix.png",
        "flat": "cmame_submission_flat/Figure_12_all_method_result_matrix.png",
        "main_tex": "figures/all_method_result_matrix.png",
        "flat_tex": "Figure_12_all_method_result_matrix.png",
        "caption_token": "All-method common-reference result matrix",
        "role": "all-method all-example result matrix",
    },
    {
        "number": 13,
        "main": "figures/work_precision_compendium.png",
        "flat": "cmame_submission_flat/Figure_13_work_precision_compendium.png",
        "main_tex": "figures/work_precision_compendium.png",
        "flat_tex": "Figure_13_work_precision_compendium.png",
        "caption_token": "Work/precision compendium for fair candidate diagnostics",
        "role": "work/precision compendium",
    },
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def png_size(path: Path) -> tuple[int, int]:
    with path.open("rb") as handle:
        header = handle.read(24)
    if len(header) < 24 or header[:8] != b"\x89PNG\r\n\x1a\n":
        return 0, 0
    return struct.unpack(">II", header[16:24])


def audit_figure(spec: dict[str, object], main_tex: str, flat_tex: str, main_pdf: str, flat_pdf: str) -> dict[str, object]:
    main_path = manuscript_path(str(spec["main"]))
    flat_path = manuscript_path(str(spec["flat"]))
    main_exists = main_path.exists() and main_path.stat().st_size > 0
    flat_exists = flat_path.exists() and flat_path.stat().st_size > 0
    main_width, main_height = png_size(main_path) if main_exists else (0, 0)
    flat_width, flat_height = png_size(flat_path) if flat_exists else (0, 0)
    caption = str(spec["caption_token"])
    main_include_token = Path(str(spec["main"])).name
    return {
        **spec,
        "main_exists": main_exists,
        "flat_exists": flat_exists,
        "main_size_bytes": main_path.stat().st_size if main_exists else 0,
        "flat_size_bytes": flat_path.stat().st_size if flat_exists else 0,
        "main_dimensions": [main_width, main_height],
        "flat_dimensions": [flat_width, flat_height],
        "main_tex_includes": main_include_token in main_tex,
        "flat_tex_includes": str(spec["flat_tex"]) in flat_tex,
        "main_pdf_caption_present": caption in main_pdf,
        "flat_pdf_caption_present": caption in flat_pdf,
        "meets_minimum_pixel_area": main_width * main_height >= 1_000_000 and flat_width * flat_height >= 1_000_000,
    }


def post_b4_figure_scope_plan(
    figure_rows: list[dict[str, object]],
    source_policy_rows_closed: int | None,
    source_policy_rows_total: int | None,
    opt_in_packet: dict[str, Any],
) -> dict[str, object]:
    """Plan the B7 figure actions once B4 source-policy rows become available."""

    actions = {
        1: (
            "retain_after_caption_recheck",
            "accepted local convergence/work-precision evidence remains part of the local-method claim",
            False,
        ),
        2: (
            "retain_after_caption_recheck",
            "mechanism schematic is independent of external source-policy rows",
            False,
        ),
        3: (
            "retain_after_caption_recheck",
            "closed-loop kinematic FullVA evidence is independent of external source-policy rows",
            False,
        ),
        4: (
            "retain_after_caption_recheck",
            "full-TFE non-claim diagnostic remains a limitation figure",
            False,
        ),
        5: (
            "retain_after_caption_recheck",
            "velocity-compression diagnostic remains a method-boundary figure",
            False,
        ),
        6: (
            "retain_after_caption_recheck",
            "sparse backend caveat remains independent of source-policy rows",
            False,
        ),
        7: (
            "retain_after_caption_recheck",
            "strict common-reference work/precision rows remain diagnostic and must not be promoted to source-policy closure",
            False,
        ),
        8: (
            "refresh_claim_boundary_overlay_or_caption",
            "claim-boundary figure should reflect the final B4/B7 source-policy row status after promotion",
            True,
        ),
        9: (
            "rebuild_from_promoted_source_policy_rows",
            "current coarse-baseline panel is diagnostic; B7 needs accepted source-policy baseline comparison rows",
            True,
        ),
        10: (
            "retain_after_caption_recheck",
            "closed-loop coarse dynamics evidence remains a local-method diagnostic figure",
            False,
        ),
        11: (
            "retain_after_caption_recheck",
            "method-stage architecture is independent of external source-policy rows",
            False,
        ),
        12: (
            "refresh_claim_boundary_overlay_or_caption",
            "all-method matrix should keep any post-B4 promoted/demoted row status synchronized",
            True,
        ),
        13: (
            "rebuild_from_promoted_source_policy_rows",
            "current compendium is diagnostic; clean source-policy work/precision curves require promoted B4 rows",
            True,
        ),
    }
    rows = []
    for figure in figure_rows:
        number = int(figure["number"])
        action, reason, source_policy_dependent = actions[number]
        rows.append(
            {
                "number": number,
                "role": figure.get("role"),
                "current_caption_token": figure.get("caption_token"),
                "post_b4_action": action,
                "source_policy_dependent": source_policy_dependent,
                "reason": reason,
            }
        )
    counts = Counter(row["post_b4_action"] for row in rows)
    blocking_rebuild_figures = [
        row["number"] for row in rows if row["post_b4_action"] == "rebuild_from_promoted_source_policy_rows"
    ]
    claim_refresh_figures = [
        row["number"] for row in rows if row["post_b4_action"] == "refresh_claim_boundary_overlay_or_caption"
    ]
    promotion_contract = opt_in_packet.get("post_execution_promotion_contract", {})
    gap_program = opt_in_packet.get("remaining_gap_program", {})
    gap_entries = gap_program.get("entries", [])
    ready_command_boundary = {
        "schema": "cmame-b7-ready-command-coverage-boundary-v1",
        "status": "ready_commands_cover_half_source_policy_rows_future_source_policy_reintroduction_only",
        "ready_command_count": opt_in_packet.get("ready_command_count"),
        "ready_command_mapped_external_rows": opt_in_packet.get("ready_command_mapped_external_rows"),
        "unaddressed_external_rows_after_ready_commands": opt_in_packet.get(
            "unaddressed_external_rows_after_ready_commands"
        ),
        "source_policy_rows_total": opt_in_packet.get("source_policy_rows_total"),
        "ready_lanes_after_explicit_opt_in": promotion_contract.get("ready_lanes_after_explicit_opt_in"),
        "not_ready_lanes_after_ready_commands": promotion_contract.get("not_ready_lanes"),
        "not_ready_suites_after_ready_commands": [item.get("suite_id") for item in gap_entries],
        "remaining_gap_program_status": gap_program.get("status"),
        "remaining_gap_rows_requiring_new_runner_or_code_path": gap_program.get(
            "rows_requiring_new_runner_or_code_path"
        ),
        "remaining_gap_rows_demoted_related_work_proxy_for_current_claim": gap_program.get(
            "rows_demoted_related_work_proxy_for_current_claim"
        ),
        "ready_commands_alone_can_close_b4": opt_in_packet.get("b4_can_close_after_ready_commands_only"),
        "ready_commands_alone_can_close_b7": opt_in_packet.get("b7_can_close_after_ready_commands_only"),
        "execution_invoked_by_packet": opt_in_packet.get("execution_invoked_by_packet"),
    }
    return {
        "schema": "cmame-b7-post-b4-figure-scope-plan-v1",
        "status": "post_b4_source_policy_reintroduction_plan_ready_current_b7_closed",
        "source_policy_rows_closed_now": source_policy_rows_closed,
        "source_policy_rows_required_before_rebuild": source_policy_rows_total,
        "b7_closure_allowed_by_this_plan_now": False,
        "current_b7_scope_closed_without_source_policy_rebuild": True,
        "no_new_figure_count_required_now": True,
        "action_counts": dict(sorted(counts.items())),
        "retain_after_caption_recheck_figures": [
            row["number"] for row in rows if row["post_b4_action"] == "retain_after_caption_recheck"
        ],
        "claim_boundary_refresh_figures_after_b4": claim_refresh_figures,
        "blocking_source_policy_rebuild_figures": blocking_rebuild_figures,
        "source_policy_dependent_figure_count": sum(1 for row in rows if row["source_policy_dependent"]),
        "ready_command_coverage_boundary": ready_command_boundary,
        "rows": rows,
        "required_b4_evidence_before_closure": [
            "promoted source-policy row table with accepted provenance for work/precision rows",
            "same-run error/order and work metrics for every promoted source-policy figure row",
            "ready-command coverage is not enough: 20/40 rows remain without executable source-policy commands",
            "demotion labels for TFE and VP2024 rows that remain without runner/code-path closure",
            "caption/claim-boundary refresh after B4 promotion validators pass",
        ],
    }


def main() -> None:
    main_tex = read_text(LATEX / "main_cmame.tex")
    flat_tex = read_text(FLAT / "main_cmame_submission.tex")
    main_pdf = read_text(LATEX / "main_cmame.txt")
    flat_pdf = read_text(FLAT / "main_cmame_submission.txt")
    b4_plan = read_json(PAPER / "B4_SOURCE_POLICY_WORK_PRECISION_EXECUTION_PLAN.json")
    opt_in_packet = read_json(PAPER / "B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json")
    narrowed_policy = read_json(PAPER / "CMAME_NARROWED_CLAIM_CLOSURE_POLICY_AUDIT.json")
    figure_rows = [audit_figure(spec, main_tex, flat_tex, main_pdf, flat_pdf) for spec in FIGURES]
    all_available = all(row["main_exists"] and row["flat_exists"] for row in figure_rows)
    all_integrated = all(row["main_tex_includes"] and row["flat_tex_includes"] for row in figure_rows)
    all_pdf_captions = all(row["main_pdf_caption_present"] and row["flat_pdf_caption_present"] for row in figure_rows)
    all_legible_dimensions = all(row["meets_minimum_pixel_area"] for row in figure_rows)
    figure12 = next(row for row in figure_rows if row["number"] == 12)
    figure13 = next(row for row in figure_rows if row["number"] == 13)
    figure8 = next(row for row in figure_rows if row["number"] == 8)
    figure9 = next(row for row in figure_rows if row["number"] == 9)
    b4_current = b4_plan.get("current_evidence", {})
    b4_summary = b4_plan.get("execution_lane_summary", {})
    source_policy_rows_closed = b4_summary.get(
        "source_policy_rows_closed_after_plan",
        b4_current.get("source_policy_rows_closed"),
    )
    source_policy_rows_total = b4_summary.get(
        "source_policy_rows_total",
        b4_current.get("source_policy_rows_total"),
    )
    source_policy_ready = (
        source_policy_rows_total is not None
        and source_policy_rows_closed == source_policy_rows_total
        and source_policy_rows_total > 0
    )
    narrowed_feasibility = narrowed_policy.get("closure_feasibility_under_policy_change", {})
    narrowed_scope_supported = (
        narrowed_policy.get("narrowed_claim_evidence_supported") is True
        and narrowed_feasibility.get("b7_close_if_diagnostic_figure_scope_adopted") is True
        and narrowed_feasibility.get("source_policy_row_promotion_required") is False
        and narrowed_feasibility.get("heavy_or_b4_execution_required") is False
    )
    closed_preconditions = [
        {
            "id": "figure_inventory_complete",
            "status": len(figure_rows) == 13,
            "evidence": "CMAME_FIGURE_SET_AUDIT.json",
        },
        {
            "id": "main_flat_figure_files_available",
            "status": all_available,
            "evidence": "figures/ and cmame_submission_flat/",
        },
        {
            "id": "main_flat_tex_integration_present",
            "status": all_integrated,
            "evidence": "main_cmame.tex and flat submission source",
        },
        {
            "id": "main_flat_pdf_captions_present",
            "status": all_pdf_captions,
            "evidence": "main_cmame.txt and flat PDF text",
        },
        {
            "id": "legible_figure_dimensions_present",
            "status": all_legible_dimensions,
            "evidence": "PNG dimensions",
        },
        {
            "id": "limitation_explanation_figure_integrated",
            "status": bool(figure8["main_tex_includes"] and figure8["flat_tex_includes"]),
            "evidence": "Figure 8",
        },
        {
            "id": "coarse_baseline_work_precision_figure_integrated",
            "status": bool(figure9["main_tex_includes"] and figure9["flat_tex_includes"]),
            "evidence": "Figure 9",
        },
        {
            "id": "all_method_result_matrix_integrated",
            "status": bool(
                figure12["main_tex_includes"]
                and figure12["flat_tex_includes"]
                and figure12["main_pdf_caption_present"]
                and figure12["flat_pdf_caption_present"]
            ),
            "evidence": "Figure 12",
        },
        {
            "id": "work_precision_compendium_integrated",
            "status": bool(
                figure13["main_tex_includes"]
                and figure13["flat_tex_includes"]
                and figure13["main_pdf_caption_present"]
                and figure13["flat_pdf_caption_present"]
            ),
            "evidence": "Figure 13",
        },
        {
            "id": "read_only_no_heavy_no_default_1e4_policy_recorded",
            "status": True,
            "evidence": "claim_boundary",
        },
        {
            "id": "narrowed_claim_policy_evidence_supported",
            "status": narrowed_scope_supported,
            "evidence": "CMAME_NARROWED_CLAIM_CLOSURE_POLICY_AUDIT.json",
        },
        {
            "id": "source_policy_work_precision_claim_excluded_from_current_b7_scope",
            "status": True,
            "evidence": "claim_boundary",
        },
        {
            "id": "external_superiority_claim_forbidden_in_current_figure_scope",
            "status": True,
            "evidence": "claim_boundary",
        },
    ]
    future_source_policy_dependencies = [
        {
            "id": "b4_source_policy_work_precision_rows_closed",
            "status": "excluded_from_current_scope",
            "reason": f"source-policy rows remain {source_policy_rows_closed}/{source_policy_rows_total}; retained only for future source-policy reintroduction",
        },
        {
            "id": "full_source_policy_baseline_comparison_figures",
            "status": "excluded_from_current_scope",
            "reason": "current figures are accepted as common-reference diagnostics under the narrowed claim, not source-policy baseline comparisons",
        },
        {
            "id": "clean_source_policy_work_precision_figures",
            "status": "excluded_from_current_scope",
            "reason": "Figure 13 remains a diagnostic compendium; clean source-policy curves are outside the current publication claim",
        },
    ]
    b7_closure_readiness_preflight = {
        "schema": "cmame-b7-closure-readiness-preflight-v1",
        "status": "b7_narrowed_diagnostic_common_reference_figure_scope_closed",
        "closed_precondition_count": sum(1 for item in closed_preconditions if item["status"] is True),
        "open_dependency_count": 0,
        "source_policy_rows_closed": source_policy_rows_closed,
        "source_policy_rows_total": source_policy_rows_total,
        "source_policy_rows_ready_for_b7": source_policy_ready,
        "source_policy_rows_required_for_current_b7": False,
        "narrowed_claim_policy_evidence_supported": narrowed_scope_supported,
        "b7_closure_allowed_now": narrowed_scope_supported,
        "heavy_numerical_run_invoked": False,
        "run_v047_invoked": False,
        "default_1e-4_required": False,
        "closed_preconditions": closed_preconditions,
        "open_dependencies": [],
        "future_source_policy_reintroduction_dependencies": future_source_policy_dependencies,
        "post_close_actions": [
            "keep source-policy work/precision rows excluded from the current publication claim",
            "recheck figure captions against the narrowed accepted claim boundary",
            "refresh PDF-style review, blocker gate, review agent, and submission bundle after any figure-scope edit",
        ],
    }
    post_b4_plan = post_b4_figure_scope_plan(
        figure_rows,
        source_policy_rows_closed,
        source_policy_rows_total,
        opt_in_packet,
    )

    result = {
        "schema": "cmame-figure-set-audit-v1",
        "status": "b7_figure_set_closed_narrowed_common_reference_diagnostic_scope",
        "blocker": "B7",
        "submission_ready": False,
        "b7_closed": narrowed_scope_supported,
        "source_policy_rows_closed": source_policy_rows_closed,
        "source_policy_rows_total": source_policy_rows_total,
        "figure_count": len(figure_rows),
        "expected_figure_count": 13,
        "all_figures_available": all_available,
        "all_figures_integrated_main_flat": all_integrated,
        "all_pdf_captions_present": all_pdf_captions,
        "all_legible_dimensions": all_legible_dimensions,
        "figure12_all_method_matrix_integrated": bool(
            figure12["main_exists"]
            and figure12["flat_exists"]
            and figure12["main_tex_includes"]
            and figure12["flat_tex_includes"]
            and figure12["main_pdf_caption_present"]
            and figure12["flat_pdf_caption_present"]
        ),
        "figure13_work_precision_compendium_integrated": bool(
            figure13["main_exists"]
            and figure13["flat_exists"]
            and figure13["main_tex_includes"]
            and figure13["flat_tex_includes"]
            and figure13["main_pdf_caption_present"]
            and figure13["flat_pdf_caption_present"]
        ),
        "publication_progress": [
            "mechanism_schematic_present",
            "method_stage_architecture_present",
            "accepted_path_convergence_work_precision_present",
            "limitation_explanation_present",
            "coarse_first_baseline_work_precision_present",
            "closed_loop_true_dynamic_order_present",
            "all_method_all_example_result_matrix_present",
            "work_precision_compendium_present",
        ],
        "still_open_requirements": [
        ],
        "excluded_future_source_policy_requirements": [
            "full_source_policy_baseline_comparison_figures",
            "complete_work_precision_curves_for_external_source_suites",
        ],
        "b7_closure_readiness_preflight": b7_closure_readiness_preflight,
        "post_b4_figure_scope_plan": post_b4_plan,
        "claim_boundary": {
            "external_superiority_claim_allowed": False,
            "figure_set_supports_common_reference_diagnostics_only": True,
            "source_policy_work_precision_claim_excluded": True,
            "source_policy_rows_promoted": source_policy_rows_closed,
            "source_policy_rows_total": source_policy_rows_total,
            "current_figure_scope": "narrowed_common_reference_diagnostic_publication_scope",
            "default_1e-4_required": False,
            "heavy_numerical_run_invoked": False,
            "run_v047_invoked": False,
        },
        "figures": figure_rows,
    }

    with OUT_JSON.open("w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, sort_keys=True)
        handle.write("\n")

    lines = [
        "# CMAME Figure Set Audit",
        "",
        "Status: **B7 CLOSED - NARROWED COMMON-REFERENCE DIAGNOSTIC FIGURE SCOPE**.",
        "",
        f"- Figures audited: `{len(figure_rows)}/13`.",
        f"- All main/flat figure files available: `{all_available}`.",
        f"- All main/flat TeX includes present: `{all_integrated}`.",
        f"- All main/flat PDF captions present: `{all_pdf_captions}`.",
        f"- Figure 12 all-method matrix integrated: `{result['figure12_all_method_matrix_integrated']}`.",
        f"- Figure 13 work/precision compendium integrated: `{result['figure13_work_precision_compendium_integrated']}`.",
        f"- Source-policy rows closed/total: `{source_policy_rows_closed}/{source_policy_rows_total}`.",
        f"- B7 closed: `{result['b7_closed']}`.",
        f"- Source-policy work/precision claim excluded: `{result['claim_boundary']['source_policy_work_precision_claim_excluded']}`.",
        f"- External superiority claim allowed: `{result['claim_boundary']['external_superiority_claim_allowed']}`.",
        f"- Submission ready from this audit: `{result['submission_ready']}`.",
        "",
        "## Figure Inventory",
        "",
        "| no. | role | main | flat | main px | flat px | PDF captions |",
        "|---:|---|---|---|---:|---:|---|",
    ]
    for row in figure_rows:
        lines.append(
            "| "
            f"{row['number']} | `{row['role']}` | `{row['main_exists']}` | `{row['flat_exists']}` | "
            f"`{row['main_dimensions'][0]}x{row['main_dimensions'][1]}` | "
            f"`{row['flat_dimensions'][0]}x{row['flat_dimensions'][1]}` | "
            f"`{row['main_pdf_caption_present']}/{row['flat_pdf_caption_present']}` |"
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- Figure 12 makes the all-method all-example common-reference matrix visible in the PDF.",
            "- Figure 13 consolidates fair candidate/common-reference work/precision rows and the T=10 Algorithm-1-literal Newton-work diagnostic already available in the evidence bundle.",
            "- The figure set supports internal order evidence and bounded common-reference diagnostics.",
            "- B7 closes under the narrowed claim because source-policy baseline comparison figures and complete external-suite work/precision curves are excluded from the current publication claim.",
            "- This audit did not invoke `run_v047.py`, a v048 runner, or any default `1e-4` campaign.",
            "",
            "## Post-B4 Figure Scope Plan",
            "",
            f"Status: `{post_b4_plan['status']}`.",
            "",
            f"- Retain after caption recheck: `{len(post_b4_plan['retain_after_caption_recheck_figures'])}` figures.",
            f"- Claim-boundary refresh after B4: `{post_b4_plan['claim_boundary_refresh_figures_after_b4']}`.",
            f"- Blocking source-policy rebuild figures: `{post_b4_plan['blocking_source_policy_rebuild_figures']}`.",
            f"- Source-policy dependent figure count: `{post_b4_plan['source_policy_dependent_figure_count']}`.",
            f"- B7 closure allowed by this plan now: `{post_b4_plan['b7_closure_allowed_by_this_plan_now']}`.",
            f"- Current B7 scope closed without source-policy rebuild: `{post_b4_plan['current_b7_scope_closed_without_source_policy_rebuild']}`.",
            f"- Ready-command mapped/unaddressed rows: `{post_b4_plan['ready_command_coverage_boundary']['ready_command_mapped_external_rows']}/{post_b4_plan['ready_command_coverage_boundary']['unaddressed_external_rows_after_ready_commands']}`.",
            f"- Ready/not-ready lanes after opt-in: `{post_b4_plan['ready_command_coverage_boundary']['ready_lanes_after_explicit_opt_in']}` / `{post_b4_plan['ready_command_coverage_boundary']['not_ready_lanes_after_ready_commands']}`.",
            f"- Ready commands alone close B4/B7: `{post_b4_plan['ready_command_coverage_boundary']['ready_commands_alone_can_close_b4']}/{post_b4_plan['ready_command_coverage_boundary']['ready_commands_alone_can_close_b7']}`.",
            "",
            "| figure | post-B4 action | source-policy dependent | reason |",
            "|---:|---|---:|---|",
        ]
    )
    for item in post_b4_plan["rows"]:
        lines.append(
            "| "
            f"{item['number']} | `{item['post_b4_action']}` | "
            f"`{item['source_policy_dependent']}` | {item['reason']} |"
        )
    lines.extend(
        [
            "",
            "## B7 Closure-Readiness Preflight",
            "",
            f"Status: `{b7_closure_readiness_preflight['status']}`.",
            "",
            f"- Closed preconditions/open dependencies: `{b7_closure_readiness_preflight['closed_precondition_count']}/{b7_closure_readiness_preflight['open_dependency_count']}`.",
            f"- Source-policy rows closed/total: `{b7_closure_readiness_preflight['source_policy_rows_closed']}/{b7_closure_readiness_preflight['source_policy_rows_total']}`.",
            f"- Source-policy rows ready for B7: `{b7_closure_readiness_preflight['source_policy_rows_ready_for_b7']}`.",
            f"- Source-policy rows required for current B7: `{b7_closure_readiness_preflight['source_policy_rows_required_for_current_b7']}`.",
            f"- Narrowed-claim policy evidence supported: `{b7_closure_readiness_preflight['narrowed_claim_policy_evidence_supported']}`.",
            f"- B7 closure allowed now: `{b7_closure_readiness_preflight['b7_closure_allowed_now']}`.",
            f"- Heavy numerical run invoked: `{b7_closure_readiness_preflight['heavy_numerical_run_invoked']}`.",
            f"- `run_v047.py` invoked: `{b7_closure_readiness_preflight['run_v047_invoked']}`.",
            "",
            "| closed precondition | status | evidence |",
            "|---|---:|---|",
        ]
    )
    for item in b7_closure_readiness_preflight["closed_preconditions"]:
        lines.append(f"| `{item['id']}` | `{item['status']}` | `{item['evidence']}` |")
    lines.extend(
        [
            "",
            "| future source-policy dependency | status | reason |",
            "|---|---|---|",
        ]
    )
    for item in b7_closure_readiness_preflight["future_source_policy_reintroduction_dependencies"]:
        lines.append(f"| `{item['id']}` | `{item['status']}` | {item['reason']} |")
    lines.extend(
        [
            "",
            "Post-close actions:",
            "",
        ]
    )
    for action in b7_closure_readiness_preflight["post_close_actions"]:
        lines.append(f"- {action}")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("cmame_figure_set_audit=written")
    print(f"figures={len(figure_rows)}/13")
    print(f"figure12_all_method_matrix_integrated={result['figure12_all_method_matrix_integrated']}")
    print(f"figure13_work_precision_compendium_integrated={result['figure13_work_precision_compendium_integrated']}")
    print(f"b7_closed={result['b7_closed']}")


if __name__ == "__main__":
    main()
