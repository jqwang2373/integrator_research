#!/usr/bin/env python3
"""Forensic all-example audit for the v048 same-grid comparison rows.

This is stricter than the row-level common-reference audit.  It checks every
method/example cell and separates a bounded common-reference diagnostic from a
source-policy external-superiority claim.
"""

from __future__ import annotations

import csv
import json
import math
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
PAPER = HERE.parent / "paper_v047_cylindrical_chain"

OUT_CSV = RESULTS / "all_examples_apples_to_apples_forensic_audit.csv"
OUT_JSON = RESULTS / "all_examples_apples_to_apples_forensic_audit.json"
OUT_MD = RESULTS / "all_examples_apples_to_apples_forensic_audit.md"

EXAMPLES = ("single_pendulum", "double_pendulum", "four_link", "slider_crank")
LOCAL = "local_Gauss6_FullVA"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def read_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"refusing to write empty {path.name}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def as_float(value: object) -> float:
    try:
        out = float(value)
    except (TypeError, ValueError):
        return float("nan")
    return out if math.isfinite(out) else float("nan")


def fmt(value: object) -> str:
    number = as_float(value)
    if not math.isfinite(number):
        return "nan"
    if abs(number) >= 1000.0 or (0.0 < abs(number) < 1.0e-3):
        return f"{number:.3e}"
    return f"{number:.6g}"


def bool_s(value: bool) -> str:
    return str(bool(value)).lower()


def method_source_level(method: str) -> tuple[str, str, str]:
    if method == LOCAL:
        return (
            "local_proposed_method",
            "local_v047_implementation",
            "internal method row; not an external baseline source-policy row",
        )
    if method.startswith("ra2021_"):
        return (
            "public_code_replay",
            "public SimEngineMBD setup and public rA/rp/reps stepper",
            "verify velocity mapping, time grid, norm, and runtime before source-policy superiority",
        )
    if method.startswith("hi2022_"):
        return (
            "public_code_bounded_replay",
            "public HI2022 setup and public half-implicit stepper",
            "bounded T=0.1 replay; full T=8 public policy is not closed",
        )
    if method.startswith("tfe2026_"):
        return (
            "local_formula_proxy",
            "RA2021 public setup with locally installed Newmark/TFE formulas",
            "encode the original TFE pendulum setup/error/output policy or demote",
        )
    if method.startswith("vp2024_"):
        return (
            "local_proxy_or_alias",
            "RA2021 public setup with coordinate-partitioning proxy stepper",
            "resolve independent VP2024 code path or demote as proxy evidence",
        )
    return ("unknown", "unknown", "manual review required")


def source_policy_closed(method: str) -> bool:
    return method == LOCAL


def paper_claim_scope(method: str) -> str:
    if method == LOCAL:
        return "internal_order_evidence"
    if method.startswith(("ra2021_", "hi2022_")):
        return "bounded_common_reference_diagnostic_not_source_policy_superiority"
    if method.startswith("tfe2026_"):
        return "formula_proxy_diagnostic_not_original_paper_superiority"
    if method.startswith("vp2024_"):
        return "proxy_or_alias_diagnostic_not_original_code_superiority"
    return "manual_review"


def monotone_decreasing(raw_rows: list[dict[str, str]], key: str) -> bool:
    pairs = sorted(
        [(as_float(row.get("h")), as_float(row.get(key))) for row in raw_rows if row.get("status") == "ok"],
        reverse=True,
    )
    values = [error for _h, error in pairs if math.isfinite(error)]
    if len(values) < 3:
        return False
    return all(left + 1.0e-30 >= right for left, right in zip(values, values[1:]))


def main() -> None:
    common = read_json(RESULTS / "common_reference_error_summary.json")
    common_rows = read_csv(RESULTS / "common_reference_error_summary.csv")
    raw_rows = read_csv(RESULTS / "common_reference_error_raw_rows.csv")
    apples = read_json(RESULTS / "apples_to_apples_policy_audit.json")
    source_policy = read_json(PAPER / "ALL_EXAMPLES_SOURCE_POLICY_AUDIT.json")

    raw_by_key: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in raw_rows:
        raw_by_key[(row["method"], row["example"])].append(row)

    forensic_rows: list[dict[str, object]] = []
    issue_counter: Counter[str] = Counter()
    example_counter: Counter[str] = Counter()
    method_counter: Counter[str] = Counter()
    source_level_counter: Counter[str] = Counter()

    for row in sorted(common_rows, key=lambda item: (item["example"], item["method"])):
        method = row["method"]
        example = row["example"]
        raw_group = raw_by_key[(method, example)]
        source_level, row_source, required_action = method_source_level(method)
        vel_order = as_float(row.get("vel_order"))
        finest_pos = as_float(row.get("finest_pos_error"))
        finest_vel = as_float(row.get("finest_vel_error"))
        same_grid_reference = (
            row.get("status") == "ok"
            and row.get("ok_count") == "3"
            and row.get("row_count") == "3"
            and bool(row.get("reference_policy"))
            and bool(row.get("error_norm"))
        )

        issues: list[str] = []
        if not same_grid_reference:
            issues.append("grid_or_reference_not_closed")
        if math.isfinite(finest_pos) and math.isfinite(finest_vel) and finest_pos < 1.0e-6 and finest_vel > 1.0e-2:
            issues.append("position_aligned_velocity_mismatch")
        if math.isfinite(finest_vel) and finest_vel < 1.0e-6 and math.isfinite(vel_order) and abs(vel_order) < 0.25:
            issues.append("near_floor_order_unidentifiable")
        if math.isfinite(vel_order) and vel_order < 0.0 and math.isfinite(finest_vel) and finest_vel > 1.0e-8:
            issues.append("negative_velocity_order")
        if not monotone_decreasing(raw_group, "vel_error"):
            issues.append("velocity_error_nonmonotone_or_floor_limited")
        if method != LOCAL and not source_policy_closed(method):
            issues.append("source_policy_not_closed")
        if method.startswith("tfe2026_"):
            issues.append("original_tfe_setup_not_encoded")
        if method.startswith("vp2024_"):
            issues.append("vp2024_code_path_unresolved_or_proxy")

        for issue in issues:
            issue_counter[issue] += 1
        example_counter[example] += 1
        method_counter[method] += 1
        source_level_counter[source_level] += 1

        strict_external_claim_allowed = False
        bounded_common_reference_diagnostic = bool(same_grid_reference and row.get("status") == "ok")
        forensic_rows.append(
            {
                "example": example,
                "method": method,
                "family": row.get("family", ""),
                "status": row.get("status", ""),
                "source_level": source_level,
                "row_source": row_source,
                "h_values": row.get("h_values", ""),
                "t_end": row.get("t_end", ""),
                "reference_h": row.get("reference_h", ""),
                "reference_policy": row.get("reference_policy", ""),
                "error_norm": row.get("error_norm", ""),
                "vel_order": row.get("vel_order", "nan"),
                "finest_vel_error": row.get("finest_vel_error", "nan"),
                "same_grid_reference_norm": bool_s(same_grid_reference),
                "bounded_common_reference_diagnostic": bool_s(bounded_common_reference_diagnostic),
                "source_policy_closed": bool_s(source_policy_closed(method)),
                "strict_external_error_claim_allowed": bool_s(strict_external_claim_allowed),
                "paper_claim_scope": paper_claim_scope(method),
                "issues": "|".join(issues) if issues else "none",
                "required_action": required_action,
            }
        )

    methods = sorted(method_counter)
    examples = sorted(example_counter)
    expected_cells = len(methods) * len(EXAMPLES)
    strict_allowed_count = sum(
        1 for row in forensic_rows if row["strict_external_error_claim_allowed"] == "true"
    )
    bounded_count = sum(
        1 for row in forensic_rows if row["bounded_common_reference_diagnostic"] == "true"
    )

    per_example: dict[str, dict[str, object]] = {}
    for example in EXAMPLES:
        rows = [row for row in forensic_rows if row["example"] == example]
        per_example[example] = {
            "row_count": len(rows),
            "method_count": len({row["method"] for row in rows}),
            "issue_count": sum(1 for row in rows if row["issues"] != "none"),
            "source_policy_open_count": sum(1 for row in rows if row["source_policy_closed"] != "true"),
            "strict_external_error_claim_allowed_count": sum(
                1 for row in rows if row["strict_external_error_claim_allowed"] == "true"
            ),
        }

    summary = {
        "schema": "all-examples-apples-to-apples-forensic-audit-v1",
        "status": "all_examples_all_methods_checked_source_policy_open",
        "all_examples_checked": examples == sorted(EXAMPLES),
        "all_method_example_cells_checked": len(forensic_rows) == expected_cells == 44,
        "example_count": len(examples),
        "method_count": len(methods),
        "row_count": len(forensic_rows),
        "raw_row_count": len(raw_rows),
        "bounded_common_reference_diagnostic_rows": bounded_count,
        "strict_external_error_claim_allowed_rows": strict_allowed_count,
        "direct_error_superiority_claim_allowed_for_paper": False,
        "external_superiority_claim_allowed": False,
        "source_policy_reproduction": False,
        "common_reference_arithmetic_passed": common.get("direct_error_superiority_claim") is True
        and apples.get("paper_safe_row_count") == apples.get("row_count") == 44,
        "source_policy_audit_status": source_policy.get("status"),
        "source_policy_superiority_claim_allowed": source_policy.get("source_policy_superiority_claim_allowed"),
        "issue_counts": dict(sorted(issue_counter.items())),
        "source_level_counts": dict(sorted(source_level_counter.items())),
        "methods": methods,
        "examples": examples,
        "per_example": per_example,
        "claim_boundary": (
            "All four examples and all 44 common-reference method/example cells have been checked. "
            "The fixed-grid common-reference arithmetic is a bounded diagnostic, but it is not enough "
            "for a CMAME paper to claim external error superiority over the source papers.  Source-policy "
            "reproduction, velocity/output mapping, original TFE setup, and VP code-path questions remain open."
        ),
    }

    write_csv(OUT_CSV, forensic_rows)
    with OUT_JSON.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, sort_keys=True)
        handle.write("\n")

    lines = [
        "# All-Examples Apples-To-Apples Forensic Audit",
        "",
        f"Status: **{summary['status']}**.",
        "",
        f"- Examples checked: `{', '.join(examples)}`.",
        f"- Method/example cells checked: `{summary['row_count']}/{expected_cells}`.",
        f"- Raw common-reference rows checked: `{summary['raw_row_count']}`.",
        f"- Bounded common-reference diagnostic rows: `{bounded_count}`.",
        f"- Strict external error-claim rows allowed: `{strict_allowed_count}`.",
        f"- Direct error superiority allowed for paper: `{summary['direct_error_superiority_claim_allowed_for_paper']}`.",
        f"- Source-policy reproduction: `{summary['source_policy_reproduction']}`.",
        "",
        "## Per Example",
        "",
        "| example | rows | methods | rows with issues | source-policy open | strict error-claim rows |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for example in EXAMPLES:
        item = per_example[example]
        lines.append(
            "| "
            f"`{example}` | `{item['row_count']}` | `{item['method_count']}` | "
            f"`{item['issue_count']}` | `{item['source_policy_open_count']}` | "
            f"`{item['strict_external_error_claim_allowed_count']}` |"
        )

    lines.extend(
        [
            "",
            "## Issue Counts",
            "",
            "| issue | count |",
            "|---|---:|",
        ]
    )
    for issue, count in sorted(issue_counter.items()):
        lines.append(f"| `{issue}` | `{count}` |")

    lines.extend(
        [
            "",
            "## Rows",
            "",
            "| example | method | source level | vel order | finest vel error | claim scope | issues |",
            "|---|---|---|---:|---:|---|---|",
        ]
    )
    for row in forensic_rows:
        lines.append(
            "| "
            f"`{row['example']}` | `{row['method']}` | `{row['source_level']}` | "
            f"`{fmt(row['vel_order'])}` | `{fmt(row['finest_vel_error'])}` | "
            f"`{row['paper_claim_scope']}` | {row['issues']} |"
        )
    lines.extend(["", "## Claim Boundary", "", summary["claim_boundary"]])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("all_examples_apples_to_apples_forensic_audit=written")
    print(f"rows={summary['row_count']}/{expected_cells}")
    print(f"strict_external_error_claim_allowed_rows={strict_allowed_count}")
    print("direct_error_superiority_claim_allowed_for_paper=False")


if __name__ == "__main__":
    main()
