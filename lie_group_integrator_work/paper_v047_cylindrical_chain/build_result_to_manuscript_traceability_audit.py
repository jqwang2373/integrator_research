#!/usr/bin/env python3
"""Build a traceability audit from numerical result JSON to manuscript tables.

This is a read-only manuscript/data consistency check.  It verifies that every
velocity order/error cell in the 44-cell all-method matrix is represented in
the CMAME manuscript source, flat submission source, and extracted PDF text.
It does not rerun numerical experiments or close external source-policy gates.
"""

from __future__ import annotations

import json
import math
import re
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
from paper_paths import LATEX, package_path as manuscript_path
OUT_JSON = PAPER / "RESULT_TO_MANUSCRIPT_TRACEABILITY_AUDIT.json"
OUT_MD = PAPER / "RESULT_TO_MANUSCRIPT_TRACEABILITY_AUDIT.md"

EXAMPLES = ["single_pendulum", "double_pendulum", "four_link", "slider_crank"]
METHODS = [
    "local_Gauss6_FullVA",
    "hi2022_rA",
    "hi2022_rA_half",
    "ra2021_rA",
    "ra2021_reps",
    "ra2021_rp",
    "tfe2026_Newmark_beta",
    "tfe2026_TFE_m1",
    "tfe2026_TFE_m2",
    "tfe2026_trapezoidal",
    "vp2024_coordinate_partitioning_rA",
]

POLICY_TEX_TOKENS = [
    r"\paragraph{Benchmark-policy dictionary}",
    r"The bounded common-reference policy used in",
    r"fixes $T=0.1$, $h\in\{0.1,0.05,0.025\}$",
    r"$h_{\rm ref}=0.0125$ for every runnable method",
    r"The single-pendulum row uses",
    r"the analytic exact final state",
    r"The double-pendulum row uses the local \method{}",
    r"and a final $L^\infty$ error",
    r"The four-link and slider-crank rows use closed-loop",
    r"true-dynamic common-reference trajectories",
    r"Source-policy rows, by contrast, must follow each source paper or public code",
    r"horizon, time grid, reference solution, error norm, tolerance, and output",
]

POLICY_PDF_TOKENS = [
    "Benchmark-policy dictionary",
    "bounded common-reference policy",
    "single-pendulum row uses",
    "analytic exact final state",
    "double-pendulum row uses the local",
    "FullVA href = 0.0125 final state",
    "four-link and slider",
    "crank rows use closed-loop",
    "true-dynamic common-reference trajectories",
    "Source-policy rows, by contrast",
    "horizon, time grid, reference solution, error norm, tolerance, and output",
]

RA2021_TEX_TOKENS = [
    r"\label{tab:ra2021-local-promotion-boundary}",
    r"RA2021 local-candidate promotion boundary",
    r"source identity is now closed",
    r"Source identity is checked; promotion still requires",
    r"position/velocity order $7.951/7.042$",
    r"$h=\{0.01,0.002,0.001\}$",
    r"$h_{\rm ref}=10^{-4}$",
    r"position/velocity order $5.955/6.085$",
    r"position/velocity order $6.164/7.341$",
]

RA2021_PDF_TOKENS = [
    "RA2021 local-candidate promotion boundary",
    "source identity is now closed",
    "Source identity is checked",
    "7.951/7.042",
    "h = {0.01, 0.002, 0.001}",
    "href = 10-4",
    "position/velocity order 5.955/6.085",
    "position/velocity order 6.164/7.341",
    "not the RA2021 source-policy horizon",
]

METHOD_TEX_LABELS = {
    "local_Gauss6_FullVA": r"\method{}",
    "hi2022_rA": r"HI 2022 $rA$",
    "hi2022_rA_half": r"HI 2022 $rA_{\mathrm{half}}$",
    "ra2021_rA": r"2021 public $rA$",
    "ra2021_reps": r"2021 public $r\epsilon$",
    "ra2021_rp": r"2021 public $rp$",
    "tfe2026_Newmark_beta": r"TFE Newmark--$\beta$",
    "tfe2026_TFE_m1": r"TFE $m=1$",
    "tfe2026_TFE_m2": r"TFE $m=2$",
    "tfe2026_trapezoidal": "TFE trapezoidal",
    "vp2024_coordinate_partitioning_rA": r"VP 2024 coordinate partitioning $rA$",
}

METHOD_PDF_LABELS = {
    "local_Gauss6_FullVA": "Gauss6/FullVA",
    "hi2022_rA": "HI 2022 rA",
    "hi2022_rA_half": "HI 2022 rAhalf",
    "ra2021_rA": "2021 public rA",
    "ra2021_reps": "2021 public rϵ",
    "ra2021_rp": "2021 public rp",
    "tfe2026_Newmark_beta": "TFE Newmark-β",
    "tfe2026_TFE_m1": "TFE m = 1",
    "tfe2026_TFE_m2": "TFE m = 2",
    "tfe2026_trapezoidal": "TFE trapezoidal",
    "vp2024_coordinate_partitioning_rA": "VP 2024 coordinate partitioning rA",
}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def tex_table_block(tex: str) -> str:
    label = r"\label{tab:common-reference-all-methods}"
    start = tex.find(label)
    if start < 0:
        return ""
    end = tex.find(r"\end{table}", start)
    if end < 0:
        return ""
    return tex[start : end + len(r"\end{table}")]


def normalize_pdf_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [line for line in text.split("\n") if not re.fullmatch(r"\s*\d+\s*", line)]
    text = "\n".join(lines)
    text = re.sub(r"([A-Za-z])-+\s*\n\s*([A-Za-z])", r"\1\2", text)
    return (
        " ".join(text.split())
        .replace("–", "-")
        .replace("—", "-")
        .replace("−", "-")
    )


def contains_normalized(text: str, token: str) -> bool:
    return token in text or " ".join(token.split()) in " ".join(text.split())


def pdf_table_block(pdf_text: str) -> str:
    start = pdf_text.find("All runnable common-reference velocity rows")
    if start < 0:
        return ""
    end = pdf_text.find("The full common-reference table", start)
    if end < 0:
        end = start + 6000
    return pdf_text[start:end]


def order_token(value: float | int | None) -> str:
    if value is None:
        return "nan"
    return f"{float(value):.3f}"


def error_parts(value: float | int | None) -> tuple[str, int | None]:
    if value is None:
        return "nan", None
    value = float(value)
    if value == 0.0:
        return "0.000", 0
    exponent = math.floor(math.log10(abs(value)))
    mantissa = value / (10**exponent)
    return f"{mantissa:.3f}", exponent


def error_tex(value: float | int | None) -> str:
    mantissa, exponent = error_parts(value)
    if exponent is None:
        return "$nan$"
    if exponent == 0:
        return f"${mantissa}$"
    return f"${mantissa}\\times10^{{{exponent}}}$"


def expected_tex_cell(row: dict[str, Any]) -> str:
    return f"{order_token(row.get('velocity_order'))} / {error_tex(row.get('finest_velocity_error'))}"


def expected_pdf_cell_tokens(row: dict[str, Any]) -> list[str]:
    tokens = [order_token(row.get("velocity_order"))]
    mantissa, exponent = error_parts(row.get("finest_velocity_error"))
    tokens.append(mantissa)
    if exponent is not None and exponent != 0:
        tokens.append(f"10{exponent}")
    return tokens


def cell_key(row: dict[str, Any]) -> str:
    return f"{row.get('example')}::{row.get('method')}"


def build_rows(matrix: dict[str, Any]) -> dict[str, dict[str, Any]]:
    rows = matrix.get("rows", [])
    if not isinstance(rows, list):
        raise ValueError("PAPER_NUMERICAL_RESULT_MATRIX.json rows is not a list")
    by_key = {cell_key(row): row for row in rows if isinstance(row, dict)}
    expected_keys = {f"{example}::{method}" for example in EXAMPLES for method in METHODS}
    missing = sorted(expected_keys - set(by_key))
    extra = sorted(set(by_key) - expected_keys)
    if missing or extra:
        raise ValueError(f"unexpected matrix keys missing={missing} extra={extra}")
    return by_key


def tex_cell_presence(table: str, by_key: dict[str, dict[str, Any]]) -> dict[str, list[str]]:
    missing: list[str] = []
    for method in METHODS:
        if METHOD_TEX_LABELS[method] not in table:
            missing.append(f"{method}::label")
        for example in EXAMPLES:
            row = by_key[f"{example}::{method}"]
            cell = expected_tex_cell(row)
            if cell not in table:
                missing.append(f"{example}::{method}::{cell}")
    return {"missing": missing}


def pdf_line_for_method(table: str, method: str) -> str:
    normalized_label = normalize_pdf_text(METHOD_PDF_LABELS[method])
    for line in table.splitlines():
        if normalize_pdf_text(line).startswith(normalized_label):
            return line
    return ""


def pdf_column_major_value_lines(table: str) -> list[str]:
    """Return value lines from pdftotext output when table columns are stacked.

    Narrow PDF extraction may emit the method labels first and then one value
    column per example. In that layout the 44 value rows still appear in method
    order within each example column.
    """

    lines = [line.strip() for line in table.splitlines() if line.strip()]
    last_label_index = -1
    for idx, line in enumerate(lines):
        normalized_line = normalize_pdf_text(line)
        if any(normalized_line == normalize_pdf_text(label) for label in METHOD_PDF_LABELS.values()):
            last_label_index = idx
    if last_label_index < 0:
        return []
    value_lines = []
    for line in lines[last_label_index + 1 :]:
        if re.match(r"^-?\d+\.\d{3}\s*/", line):
            value_lines.append(line)
    return value_lines


def pdf_cell_presence(table: str, by_key: dict[str, dict[str, Any]]) -> dict[str, Any]:
    missing: list[str] = []
    matched_cells = 0
    normalized_table = normalize_pdf_text(table)
    column_major_values = pdf_column_major_value_lines(table)
    use_column_major = len(column_major_values) >= len(EXAMPLES) * len(METHODS)
    for method in METHODS:
        if normalize_pdf_text(METHOD_PDF_LABELS[method]) not in normalized_table:
            missing.append(f"{method}::label")
            continue
        method_line = pdf_line_for_method(table, method)
        method_index = METHODS.index(method)
        if not method_line and not use_column_major:
            missing.append(f"{method}::line")
            continue
        for example in EXAMPLES:
            row = by_key[f"{example}::{method}"]
            tokens = expected_pdf_cell_tokens(row)
            if use_column_major:
                example_index = EXAMPLES.index(example)
                line_index = example_index * len(METHODS) + method_index
                normalized_line = normalize_pdf_text(column_major_values[line_index])
            else:
                normalized_line = normalize_pdf_text(method_line)
            if all(token in normalized_line for token in tokens):
                matched_cells += 1
            else:
                missing.append(f"{example}::{method}::{'/'.join(tokens)}")
    return {"missing": missing, "matched_cells": matched_cells}


def main() -> None:
    matrix = read_json(PAPER / "PAPER_NUMERICAL_RESULT_MATRIX.json")
    ra2021_audit = read_json(PAPER / "RA2021_SOURCE_POLICY_ROW_AUDIT.json")
    by_key = build_rows(matrix)
    main_tex = read_text(LATEX / "main_cmame.tex")
    flat_tex = read_text(LATEX / "cmame_submission_flat" / "main_cmame_submission.tex")
    main_pdf_text = read_text(LATEX / "main_cmame.txt")
    flat_pdf_text = read_text(LATEX / "cmame_submission_flat" / "main_cmame_submission.txt")

    main_table = tex_table_block(main_tex)
    flat_table = tex_table_block(flat_tex)
    main_pdf_table = pdf_table_block(main_pdf_text)
    flat_pdf_table = pdf_table_block(flat_pdf_text)

    main_tex_presence = tex_cell_presence(main_table, by_key)
    flat_tex_presence = tex_cell_presence(flat_table, by_key)
    main_pdf_presence = pdf_cell_presence(main_pdf_table, by_key)
    flat_pdf_presence = pdf_cell_presence(flat_pdf_table, by_key)
    main_tex_policy_missing = [token for token in POLICY_TEX_TOKENS if not contains_normalized(main_tex, token)]
    flat_tex_policy_missing = [token for token in POLICY_TEX_TOKENS if not contains_normalized(flat_tex, token)]
    main_pdf_norm = normalize_pdf_text(main_pdf_text)
    flat_pdf_norm = normalize_pdf_text(flat_pdf_text)
    main_pdf_policy_missing = [token for token in POLICY_PDF_TOKENS if token not in main_pdf_norm]
    flat_pdf_policy_missing = [token for token in POLICY_PDF_TOKENS if token not in flat_pdf_norm]
    main_tex_ra2021_missing = [token for token in RA2021_TEX_TOKENS if not contains_normalized(main_tex, token)]
    flat_tex_ra2021_missing = [token for token in RA2021_TEX_TOKENS if not contains_normalized(flat_tex, token)]
    main_pdf_ra2021_missing = [token for token in RA2021_PDF_TOKENS if token not in main_pdf_norm]
    flat_pdf_ra2021_missing = [token for token in RA2021_PDF_TOKENS if token not in flat_pdf_norm]

    row_count = len(by_key)
    nonlocal_rows = sum(1 for row in by_key.values() if row.get("method") != "local_Gauss6_FullVA")
    source_policy_closed_nonlocal_rows = sum(
        1
        for row in by_key.values()
        if row.get("method") != "local_Gauss6_FullVA" and row.get("source_policy_closed") is True
    )
    strict_external_error_rows = sum(1 for row in by_key.values() if row.get("strict_external_error_claim_allowed"))

    local_integrity_passed = (
        matrix.get("schema") == "paper-numerical-result-matrix-v1"
        and matrix.get("row_count") == 44
        and matrix.get("raw_row_count") == 132
        and matrix.get("method_count") == 11
        and matrix.get("examples") == EXAMPLES
        and matrix.get("methods") == METHODS
        and not main_tex_presence["missing"]
        and not flat_tex_presence["missing"]
        and not main_pdf_presence["missing"]
        and not flat_pdf_presence["missing"]
        and main_pdf_presence["matched_cells"] == 44
        and flat_pdf_presence["matched_cells"] == 44
        and not main_tex_policy_missing
        and not flat_tex_policy_missing
        and not main_pdf_policy_missing
        and not flat_pdf_policy_missing
        and not main_tex_ra2021_missing
        and not flat_tex_ra2021_missing
        and not main_pdf_ra2021_missing
        and not flat_pdf_ra2021_missing
    )

    result = {
        "schema": "result-to-manuscript-traceability-audit-v1",
        "status": "all_44_velocity_cells_trace_to_manuscript_and_pdf_source_policy_open"
        if local_integrity_passed
        else "result_to_manuscript_traceability_failed",
        "submission_ready": False,
        "read_only": True,
        "run_v047_invoked": False,
        "heavy_numerical_run_invoked": False,
        "matrix_source": "PAPER_NUMERICAL_RESULT_MATRIX.json",
        "matrix_schema": matrix.get("schema"),
        "coverage": {
            "examples": EXAMPLES,
            "methods": METHODS,
            "method_count": matrix.get("method_count"),
            "row_count": row_count,
            "expected_row_count": matrix.get("expected_row_count"),
            "raw_row_count": matrix.get("raw_row_count"),
            "velocity_cells_checked": row_count,
            "main_tex_velocity_cells_matched": row_count - len([m for m in main_tex_presence["missing"] if "::label" not in m]),
            "flat_tex_velocity_cells_matched": row_count - len([m for m in flat_tex_presence["missing"] if "::label" not in m]),
            "main_pdf_velocity_cells_matched": main_pdf_presence["matched_cells"],
            "flat_pdf_velocity_cells_matched": flat_pdf_presence["matched_cells"],
            "nonlocal_rows": nonlocal_rows,
            "source_policy_closed_nonlocal_rows": source_policy_closed_nonlocal_rows,
            "strict_external_error_claim_allowed_rows": strict_external_error_rows,
        },
        "main_tex": {
            "table_found": bool(main_table),
            "missing_items": main_tex_presence["missing"],
        },
        "flat_tex": {
            "table_found": bool(flat_table),
            "missing_items": flat_tex_presence["missing"],
        },
        "main_pdf_text": {
            "table_found": bool(main_pdf_table),
            "missing_items": main_pdf_presence["missing"],
        },
        "flat_pdf_text": {
            "table_found": bool(flat_pdf_table),
            "missing_items": flat_pdf_presence["missing"],
        },
        "claim_boundary": {
            "result_to_manuscript_traceability_closed": local_integrity_passed,
            "source_policy_reproduction_closed": False,
            "external_superiority_claim_allowed": False,
            "direct_error_superiority_claim_allowed": False,
            "submission_ready": False,
            "reason_open": "The 44-cell velocity table traces to the manuscript/PDF, but source-policy reproduction and external-superiority gates remain open.",
        },
        "benchmark_policy_dictionary": {
            "main_tex_missing_tokens": main_tex_policy_missing,
            "flat_tex_missing_tokens": flat_tex_policy_missing,
            "main_pdf_missing_tokens": main_pdf_policy_missing,
            "flat_pdf_missing_tokens": flat_pdf_policy_missing,
            "main_tex_present": not main_tex_policy_missing,
            "flat_tex_present": not flat_tex_policy_missing,
            "main_pdf_present": not main_pdf_policy_missing,
            "flat_pdf_present": not flat_pdf_policy_missing,
            "common_reference_policy": {
                "time_horizon": 0.1,
                "step_sizes": [0.1, 0.05, 0.025],
                "reference_h": 0.0125,
                "single_pendulum_reference": "analytic_exact_final_state_final_l2",
                "double_pendulum_reference": "local_fullva_h_ref_0.0125_final_state_final_linf",
                "four_link_slider_crank_reference": "closed_loop_true_dynamic_common_reference_h_ref_0.0125",
            },
            "source_policy_boundary": (
                "source-policy rows must follow each source paper/public code horizon, time grid, "
                "reference solution, error norm, tolerance, and output variables"
            ),
        },
        "ra2021_local_candidate_promotion_boundary": {
            "main_tex_missing_tokens": main_tex_ra2021_missing,
            "flat_tex_missing_tokens": flat_tex_ra2021_missing,
            "main_pdf_missing_tokens": main_pdf_ra2021_missing,
            "flat_pdf_missing_tokens": flat_pdf_ra2021_missing,
            "main_tex_present": not main_tex_ra2021_missing,
            "flat_tex_present": not flat_tex_ra2021_missing,
            "main_pdf_present": not main_pdf_ra2021_missing,
            "flat_pdf_present": not flat_pdf_ra2021_missing,
            "source_policy_rows_closed": ra2021_audit.get("source_policy_closed_rows"),
            "public_order_groups_completed": ra2021_audit.get("public_order_groups_completed"),
            "public_order_groups_required": ra2021_audit.get("public_order_groups_required"),
            "public_timing_rows_completed": ra2021_audit.get("public_timing_rows_completed"),
            "public_timing_rows_required": ra2021_audit.get("public_timing_rows_required"),
            "local_candidate_status_by_example": {
                example: item.get("promotion_status")
                for example, item in ra2021_audit.get("local_candidate_feasibility", {}).items()
                if isinstance(item, dict)
            },
            "claim_boundary": (
                "RA2021 source identity is checked, but local candidate rows are not promoted "
                "to source-policy external-superiority rows."
            ),
        },
    }

    with OUT_JSON.open("w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, sort_keys=True)
        handle.write("\n")

    lines = [
        "# Result-To-Manuscript Traceability Audit",
        "",
        "Status: **ALL 44 VELOCITY CELLS TRACE TO THE CMAME MANUSCRIPT AND PDF; SOURCE-POLICY GATES OPEN**."
        if local_integrity_passed
        else "Status: **RESULT-TO-MANUSCRIPT TRACEABILITY FAILED**.",
        "",
        "This read-only audit checks that the all-method common-reference velocity",
        "order/error table in the manuscript is generated from the current",
        "`PAPER_NUMERICAL_RESULT_MATRIX.json` values. It does not rerun any",
        "numerical campaign and does not close external source-policy reproduction.",
        "",
        "## Coverage",
        "",
        f"- Velocity cells checked: `{row_count}/44`.",
        f"- Methods/examples: `{matrix.get('method_count')}/11` methods and `{len(EXAMPLES)}/4` examples.",
        f"- Raw rows behind matrix: `{matrix.get('raw_row_count')}`.",
        f"- Main TeX/PDF matched cells: `{result['coverage']['main_tex_velocity_cells_matched']}/{result['coverage']['main_pdf_velocity_cells_matched']}`.",
        f"- Flat TeX/PDF matched cells: `{result['coverage']['flat_tex_velocity_cells_matched']}/{result['coverage']['flat_pdf_velocity_cells_matched']}`.",
        "",
        "## Boundary",
        "",
        f"- Nonlocal rows: `{nonlocal_rows}`.",
        f"- Source-policy-closed nonlocal rows: `{source_policy_closed_nonlocal_rows}`.",
        f"- Strict external error-claim rows: `{strict_external_error_rows}`.",
        f"- Benchmark-policy dictionary present in main/flat TeX and PDF: `{not main_tex_policy_missing}/{not flat_tex_policy_missing}/{not main_pdf_policy_missing}/{not flat_pdf_policy_missing}`.",
        f"- RA2021 local-candidate promotion boundary present in main/flat TeX and PDF: `{not main_tex_ra2021_missing}/{not flat_tex_ra2021_missing}/{not main_pdf_ra2021_missing}/{not flat_pdf_ra2021_missing}`.",
        "- External superiority claim allowed: `False`.",
        "- Submission ready: `False`.",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("result_to_manuscript_traceability_audit=written")
    print(f"velocity_cells_checked={row_count}")
    print(f"main_tex_velocity_cells_matched={result['coverage']['main_tex_velocity_cells_matched']}")
    print(f"main_pdf_velocity_cells_matched={result['coverage']['main_pdf_velocity_cells_matched']}")
    print("source_policy_reproduction_closed=False")
    print("submission_ready=False")


if __name__ == "__main__":
    main()
