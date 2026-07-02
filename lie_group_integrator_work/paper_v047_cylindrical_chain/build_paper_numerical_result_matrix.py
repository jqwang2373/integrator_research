#!/usr/bin/env python3
"""Build a paper-facing numerical order/error matrix from audited v048 rows."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
ROOT = PAPER.parent
V048 = ROOT / "v048_cross_paper_same_test_benchmarks" / "results"

COMMON_JSON = V048 / "common_reference_error_summary.json"
COMMON_CSV = V048 / "common_reference_error_summary.csv"
FORENSIC_JSON = V048 / "all_examples_apples_to_apples_forensic_audit.json"
FORENSIC_CSV = V048 / "all_examples_apples_to_apples_forensic_audit.csv"

OUT_JSON = PAPER / "PAPER_NUMERICAL_RESULT_MATRIX.json"
OUT_CSV = PAPER / "PAPER_NUMERICAL_RESULT_MATRIX.csv"
OUT_MD = PAPER / "PAPER_NUMERICAL_RESULT_MATRIX.md"

EXAMPLES = ("single_pendulum", "double_pendulum", "four_link", "slider_crank")
METHODS = (
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
)


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def as_float(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() == "true"


def fmt_number(value: Any) -> str:
    number = as_float(value)
    if number is None:
        return "nan"
    if number == 0.0:
        return "0"
    if abs(number) >= 1000.0 or abs(number) < 1.0e-3:
        return f"{number:.3e}"
    return f"{number:.3f}"


def compact_order_error(order: Any, error: Any) -> str:
    return f"{fmt_number(order)} / {fmt_number(error)}"


def source_key(row: dict[str, str]) -> tuple[str, str]:
    return row["method"], row["example"]


def paper_facing_issues(method: str, raw_issues: str) -> list[str]:
    if raw_issues == "none":
        issues: list[str] = []
    else:
        issues = raw_issues.split("|")
    if method.startswith("tfe2026_"):
        return [
            "original_tfe_runner_and_friction_source_policy_open"
            if issue == "original_tfe_setup_not_encoded"
            else issue
            for issue in issues
        ]
    return issues


def paper_facing_required_action(method: str, action: str) -> str:
    if method.startswith("tfe2026_") and action == "encode the original TFE pendulum setup/error/output policy or demote":
        return (
            "resolve the original TFE source-policy DAE runner, Brown--McPhee source-code-equivalent "
            "friction law, full T=10 endpoint/output policy, and work rows or demote"
        )
    return action


def build_rows(common_rows: list[dict[str, str]], forensic_rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    common_by_key = {source_key(row): row for row in common_rows}
    forensic_by_key = {source_key(row): row for row in forensic_rows}
    rows: list[dict[str, Any]] = []
    for example in EXAMPLES:
        for method in METHODS:
            key = (method, example)
            common = common_by_key.get(key)
            forensic = forensic_by_key.get(key)
            if common is None or forensic is None:
                raise KeyError(f"missing common/forensic row for {method}/{example}")
            rows.append(
                {
                    "example": example,
                    "method": method,
                    "family": common["family"],
                    "status": common["status"],
                    "source_level": forensic["source_level"],
                    "row_source": forensic["row_source"],
                    "h_values": common["h_values"],
                    "t_end": as_float(common["t_end"]),
                    "reference_h": as_float(common["reference_h"]),
                    "reference_policy": common["reference_policy"],
                    "error_norm": common["error_norm"],
                    "position_order": as_float(common["pos_order"]),
                    "velocity_order": as_float(common["vel_order"]),
                    "acceleration_order": as_float(common["acc_order"]),
                    "finest_position_error": as_float(common["finest_pos_error"]),
                    "finest_velocity_error": as_float(common["finest_vel_error"]),
                    "finest_acceleration_error": as_float(common["finest_acc_error"]),
                    "local_velocity_order_win": as_bool(common.get("local_vel_order_win")),
                    "local_finest_velocity_error_win": as_bool(common.get("local_finest_vel_error_win")),
                    "bounded_common_reference_diagnostic": as_bool(
                        forensic["bounded_common_reference_diagnostic"]
                    ),
                    "source_policy_closed": as_bool(forensic["source_policy_closed"]),
                    "strict_external_error_claim_allowed": as_bool(forensic["strict_external_error_claim_allowed"]),
                    "paper_claim_scope": forensic["paper_claim_scope"],
                    "issues": paper_facing_issues(method, forensic["issues"]),
                    "required_action": paper_facing_required_action(method, forensic["required_action"]),
                }
            )
    return rows


def summarize_by_example(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    summary: dict[str, dict[str, Any]] = {}
    for example in EXAMPLES:
        group = [row for row in rows if row["example"] == example]
        local = next(row for row in group if row["method"] == "local_Gauss6_FullVA")
        nonlocal_rows = [row for row in group if row["method"] != "local_Gauss6_FullVA"]
        open_source_policy = [row for row in nonlocal_rows if not row["source_policy_closed"]]
        strict_allowed = [row for row in group if row["strict_external_error_claim_allowed"]]
        summary[example] = {
            "method_rows": len(group),
            "local_velocity_order": local["velocity_order"],
            "local_finest_velocity_error": local["finest_velocity_error"],
            "source_policy_open_nonlocal_rows": len(open_source_policy),
            "strict_external_error_claim_allowed_rows": len(strict_allowed),
        }
    return summary


def write_csv(rows: list[dict[str, Any]]) -> None:
    fieldnames = [
        "example",
        "method",
        "family",
        "status",
        "source_level",
        "h_values",
        "t_end",
        "reference_h",
        "reference_policy",
        "error_norm",
        "position_order",
        "velocity_order",
        "acceleration_order",
        "finest_position_error",
        "finest_velocity_error",
        "finest_acceleration_error",
        "source_policy_closed",
        "strict_external_error_claim_allowed",
        "paper_claim_scope",
        "issues",
        "required_action",
    ]
    with OUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    **{name: row.get(name) for name in fieldnames if name not in {"issues"}},
                    "issues": "none" if not row["issues"] else "|".join(row["issues"]),
                }
            )


def write_markdown(result: dict[str, Any]) -> None:
    rows = result["rows"]
    lines = [
        "# Paper Numerical Result Matrix",
        "",
        "Status: **paper-ready table with source-policy boundary open**.",
        "",
        f"- Method/example cells: `{result['row_count']}/{result['expected_row_count']}`.",
        f"- Examples: `{', '.join(result['examples'])}`.",
        f"- Methods: `{result['method_count']}`.",
        f"- Step sizes: `{', '.join(str(value) for value in result['step_sizes'])}`.",
        f"- Reference h: `{result['reference_h']}`.",
        f"- Raw rows behind this matrix: `{result['raw_row_count']}`.",
        f"- Source-policy external superiority allowed: `{result['source_policy_external_superiority_allowed']}`.",
        f"- Paper-level direct error superiority allowed: `{result['paper_direct_error_superiority_allowed']}`.",
        f"- Strict external error-claim rows: `{result['strict_external_error_claim_allowed_rows']}`.",
        "",
        "Each row reports `observed order / finest-step error`. The velocity column is the primary",
        "comparison column used by the current common-reference diagnostic; the position and",
        "acceleration columns are included for auditability.",
        "",
    ]
    for example in EXAMPLES:
        lines.extend(
            [
                f"## {example}",
                "",
                "| Method | Source level | Position | Velocity | Acceleration | Claim scope | Issues |",
                "|---|---|---:|---:|---:|---|---|",
            ]
        )
        for row in [item for item in rows if item["example"] == example]:
            issues = "none" if not row["issues"] else ", ".join(row["issues"])
            lines.append(
                "| "
                f"`{row['method']}` | `{row['source_level']}` | "
                f"`{compact_order_error(row['position_order'], row['finest_position_error'])}` | "
                f"`{compact_order_error(row['velocity_order'], row['finest_velocity_error'])}` | "
                f"`{compact_order_error(row['acceleration_order'], row['finest_acceleration_error'])}` | "
                f"`{row['paper_claim_scope']}` | `{issues}` |"
            )
        lines.append("")
    lines.extend(
        [
            "## Reading Rule",
            "",
            "This matrix is safe for reporting observed order/error under the bounded common-reference",
            "diagnostic. It is not a source-policy reproduction and it does not authorize a blanket",
            "external-superiority claim over the cited source papers.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    common = read_json(COMMON_JSON)
    forensic = read_json(FORENSIC_JSON)
    common_rows = read_csv(COMMON_CSV)
    forensic_rows = read_csv(FORENSIC_CSV)
    rows = build_rows(common_rows, forensic_rows)
    per_example = summarize_by_example(rows)
    result = {
        "schema": "paper-numerical-result-matrix-v1",
        "status": "paper_ready_table_source_policy_boundary_open",
        "source_files": {
            "common_reference_json": str(COMMON_JSON.relative_to(ROOT)),
            "common_reference_csv": str(COMMON_CSV.relative_to(ROOT)),
            "forensic_json": str(FORENSIC_JSON.relative_to(ROOT)),
            "forensic_csv": str(FORENSIC_CSV.relative_to(ROOT)),
        },
        "examples": list(EXAMPLES),
        "methods": list(METHODS),
        "method_count": len(METHODS),
        "row_count": len(rows),
        "expected_row_count": len(EXAMPLES) * len(METHODS),
        "raw_row_count": common.get("raw_row_count"),
        "step_sizes": common.get("step_sizes"),
        "reference_h": common.get("reference_h"),
        "t_end": common.get("t_end"),
        "source_policy_reproduction": common.get("source_policy_reproduction"),
        "source_policy_external_superiority_allowed": forensic.get("source_policy_superiority_claim_allowed"),
        "external_superiority_claim_allowed": forensic.get("external_superiority_claim_allowed"),
        "paper_direct_error_superiority_allowed": forensic.get(
            "direct_error_superiority_claim_allowed_for_paper"
        ),
        "strict_external_error_claim_allowed_rows": forensic.get("strict_external_error_claim_allowed_rows"),
        "direct_nonlocal_velocity_order_wins": common.get("local_velocity_order_wins"),
        "direct_nonlocal_velocity_order_comparisons": common.get("local_velocity_order_comparisons"),
        "direct_nonlocal_velocity_error_wins": common.get("local_finest_velocity_error_wins"),
        "direct_nonlocal_velocity_error_comparisons": common.get("local_finest_velocity_error_comparisons"),
        "per_example": per_example,
        "rows": rows,
    }
    with OUT_JSON.open("w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, sort_keys=True)
        handle.write("\n")
    write_csv(rows)
    write_markdown(result)
    print("paper_numerical_result_matrix=written")
    print(f"rows={len(rows)}/{len(EXAMPLES) * len(METHODS)}")
    print(f"source_policy_external_superiority_allowed={result['source_policy_external_superiority_allowed']}")


if __name__ == "__main__":
    main()
