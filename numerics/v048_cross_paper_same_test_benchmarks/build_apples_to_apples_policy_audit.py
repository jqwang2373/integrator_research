#!/usr/bin/env python3
"""Build a row-level apples-to-apples policy audit for v048 comparison rows."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
OUT_CSV = RESULTS / "apples_to_apples_policy_audit.csv"
OUT_JSON = RESULTS / "apples_to_apples_policy_audit.json"
OUT_MD = RESULTS / "apples_to_apples_policy_audit.md"

EXAMPLES = ("single_pendulum", "double_pendulum", "four_link", "slider_crank")
STEP_SIZES = "1.0000000000000001e-01|5.0000000000000003e-02|2.5000000000000001e-02"
REFERENCE_H = "1.2500000000000001e-02"
T_END = "1.0000000000000001e-01"
LOCAL = "local_Gauss6_FullVA"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def read_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"refusing to write empty {path.name}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def bool_s(value: bool) -> str:
    return str(value).lower()


def method_uses_public_source_helper(method: str) -> bool:
    return method.startswith(("ra2021_", "hi2022_"))


def main() -> None:
    summary_rows = read_csv(RESULTS / "common_reference_error_summary.csv")
    raw_rows = read_csv(RESULTS / "common_reference_error_raw_rows.csv")
    common_summary = read_json(RESULTS / "common_reference_error_summary.json")
    source_text_2021 = (
        Path("../../external/sbel-reproducibility/2021/ASME/rA-formulation/C2/SimEngineMBD/example_models/single_pendulum.py")
        .resolve()
        .read_text(encoding="utf-8")
    )
    source_text_2022 = (
        Path("../../external/sbel-reproducibility/2022/HalfImplicit_JCND/SimEngineMBD/example_models/single_pendulum.py")
        .resolve()
        .read_text(encoding="utf-8")
    )
    builder_text = (HERE / "build_common_reference_error_audit.py").read_text(encoding="utf-8")

    source_grid_caveat_present = "np.linspace(0, params.t_end, t_steps, endpoint=True)" in source_text_2021
    source_grid_caveat_present = (
        source_grid_caveat_present
        and "np.linspace(0, params.t_end, t_steps, endpoint=True)" in source_text_2022
    )
    fixed_grid_wrapper_present = (
        "def run_public_fixed_grid_model" in builder_text
        and "steps + 1" in builder_text
        and "system.do_step(i, t)" in builder_text
    )

    local_by_example = {
        row["example"]: row for row in summary_rows if row.get("method") == LOCAL and row.get("status") == "ok"
    }
    raw_by_key: dict[tuple[str, str], list[dict[str, str]]] = {}
    for row in raw_rows:
        raw_by_key.setdefault((row["method"], row["example"]), []).append(row)

    audit_rows: list[dict[str, object]] = []
    for row in summary_rows:
        method = row["method"]
        example = row["example"]
        local = local_by_example.get(example, {})
        same_reference = bool(
            row.get("reference_policy") == local.get("reference_policy")
            and row.get("error_norm") == local.get("error_norm")
        )
        same_grid = bool(
            row.get("h_values") == STEP_SIZES
            and row.get("reference_h") == REFERENCE_H
            and row.get("t_end") == T_END
            and row.get("ok_count") == "3"
            and row.get("row_count") == "3"
        )
        raw_group = raw_by_key.get((method, example), [])
        fixed_grid_used = bool(
            method == LOCAL
            or not method_uses_public_source_helper(method)
            or (
                fixed_grid_wrapper_present
                and raw_group
                and all("fixed-grid" in raw.get("evidence", "") for raw in raw_group)
            )
        )
        paper_safe = bool(same_reference and same_grid and fixed_grid_used and row.get("status") == "ok")
        audit_rows.append(
            {
                "method": method,
                "example": example,
                "status": row.get("status", ""),
                "same_h_grid": bool_s(same_grid),
                "same_reference_and_norm_as_local": bool_s(same_reference),
                "public_source_time_grid_caveat_applies": bool_s(method_uses_public_source_helper(method)),
                "public_source_time_grid_caveat_detected": bool_s(
                    source_grid_caveat_present if method_uses_public_source_helper(method) else False
                ),
                "fixed_grid_replay_used": bool_s(fixed_grid_used),
                "source_policy_reproduction": "false",
                "paper_safe_coarse_apples_to_apples": bool_s(paper_safe),
                "vel_order": row.get("vel_order", "nan"),
                "finest_vel_error": row.get("finest_vel_error", "nan"),
                "notes": (
                    "paper-safe coarse common-reference row"
                    if paper_safe
                    else "not paper-safe until grid/reference policy is repaired"
                ),
            }
        )

    nonlocal_safe = [
        row for row in audit_rows if row["method"] != LOCAL and row["paper_safe_coarse_apples_to_apples"] == "true"
    ]
    public_safe = [
        row
        for row in audit_rows
        if method_uses_public_source_helper(str(row["method"]))
        and row["paper_safe_coarse_apples_to_apples"] == "true"
    ]
    failed = [row for row in audit_rows if row["paper_safe_coarse_apples_to_apples"] != "true"]
    summary = {
        "schema": "apples-to-apples-policy-audit-v1",
        "row_count": len(audit_rows),
        "paper_safe_row_count": len(audit_rows) - len(failed),
        "nonlocal_paper_safe_comparison_count": len(nonlocal_safe),
        "public_source_time_grid_caveat_detected": source_grid_caveat_present,
        "fixed_grid_wrapper_present": fixed_grid_wrapper_present,
        "public_fixed_grid_paper_safe_count": len(public_safe),
        "failed_rows": [
            {"method": row["method"], "example": row["example"], "notes": row["notes"]} for row in failed
        ],
        "common_reference_apples_to_apples_coarse_claim": common_summary.get("apples_to_apples_coarse_claim"),
        "source_policy_reproduction": False,
        "claim": (
            "The common-reference matrix is paper-safe only as a coarse apples-to-apples final-state "
            "comparison. It is not a reproduction of the source papers' default time horizons or h policies. "
            "Public-code rows are accepted only after fixed-grid replay on t_i=i*h."
        ),
    }

    write_csv(OUT_CSV, audit_rows)
    with OUT_JSON.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, sort_keys=True)
        handle.write("\n")

    lines = [
        "# Apples-To-Apples Policy Audit",
        "",
        f"Paper-safe rows: `{summary['paper_safe_row_count']}/{summary['row_count']}`.",
        f"Nonlocal paper-safe comparisons: `{summary['nonlocal_paper_safe_comparison_count']}`.",
        f"Public source time-grid caveat detected: `{summary['public_source_time_grid_caveat_detected']}`.",
        f"Fixed-grid wrapper present: `{summary['fixed_grid_wrapper_present']}`.",
        f"Source-policy reproduction: `{summary['source_policy_reproduction']}`.",
        "",
        "| Method | Example | same h/reference | fixed-grid replay | paper safe | vel order | finest vel error |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for row in audit_rows:
        lines.append(
            "| "
            f"`{row['method']}` | `{row['example']}` | "
            f"`{row['same_h_grid']}/{row['same_reference_and_norm_as_local']}` | "
            f"`{row['fixed_grid_replay_used']}` | `{row['paper_safe_coarse_apples_to_apples']}` | "
            f"`{row['vel_order']}` | `{row['finest_vel_error']}` |"
        )
    lines.extend(["", summary["claim"]])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("apples_to_apples_policy_audit=written")
    print(f"paper_safe_rows={summary['paper_safe_row_count']}/{summary['row_count']}")
    print(f"nonlocal_paper_safe_comparisons={summary['nonlocal_paper_safe_comparison_count']}")
    print(f"source_policy_reproduction={summary['source_policy_reproduction']}")


if __name__ == "__main__":
    main()
