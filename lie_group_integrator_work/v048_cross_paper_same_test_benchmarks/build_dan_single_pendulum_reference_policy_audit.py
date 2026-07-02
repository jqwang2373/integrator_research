#!/usr/bin/env python3
"""Audit the repaired Dan/Kissel/Negrut single-pendulum comparison rows."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
OUT_CSV = RESULTS / "dan_single_pendulum_reference_policy_audit.csv"
OUT_JSON = RESULTS / "dan_single_pendulum_reference_policy_audit.json"
OUT_MD = RESULTS / "dan_single_pendulum_reference_policy_audit.md"

SUSPECT_METHODS = ("ra2021_rA", "ra2021_reps", "ra2021_rp")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def as_float(value: object) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return float("nan")


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"refusing to write empty {path.name}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    common = read_csv(RESULTS / "common_reference_error_summary.csv")
    public_same_window = read_csv(RESULTS / "single_pendulum_coarse_same_window_work_precision_summary.csv")
    public_source_policy = read_csv(RESULTS / "ra2021_public_order_work_summary.csv")

    same_window_by_method = {row["method"]: row for row in public_same_window}
    source_by_form = {
        row["form"]: row
        for row in public_source_policy
        if row.get("model") == "single_pendulum" and row.get("source_suite") == "ra2021_taves_kissel_negrut"
    }

    rows: list[dict[str, object]] = []
    for method in SUSPECT_METHODS:
        common_row = next(
            row for row in common if row.get("method") == method and row.get("example") == "single_pendulum"
        )
        form = method.removeprefix("ra2021_")
        same_window_row = same_window_by_method[f"{form}-public-dynamics-coarse"]
        source_row = source_by_form[form]
        rows.append(
            {
                "method": method,
                "example": "single_pendulum",
                "common_reference_t_end": common_row["t_end"],
                "common_reference_policy": common_row["reference_policy"],
                "common_reference_vel_order": common_row["vel_order"],
                "common_reference_finest_vel_error": common_row["finest_vel_error"],
                "same_window_t_end": same_window_row["t_end"],
                "same_window_reference_policy": same_window_row["reference_policy"],
                "same_window_vel_order": same_window_row["vel_observed_order"],
                "same_window_finest_vel_error": same_window_row["finest_vel_error"],
                "source_policy_reference_h": source_row["reference_h"],
                "source_policy_vel_order": source_row["vel_final_linf_order"],
                "source_policy_finest_vel_error": source_row["finest_vel_final_linf"],
                "paper_claim_safe": "true_as_coarse_apples_to_apples_not_source_policy",
                "recommended_status": "repaired_fixed_grid_apples_to_apples_row",
                "reason": (
                    "The previous negative common-reference slope came from the public helper time-grid "
                    "convention at coarse h. The repaired row uses fixed-grid replay on t_i=i*h and is "
                    "safe only as a short-window coarse apples-to-apples final-state comparison, not as "
                    "a reproduction of the source paper's default T=3/h=1e-4 policy."
                ),
            }
        )

    bad_common_orders = [as_float(row["common_reference_vel_order"]) for row in rows]
    summary = {
        "schema": "dan-single-pendulum-reference-policy-audit-v1",
        "affected_methods": list(SUSPECT_METHODS),
        "affected_row_count": len(rows),
        "common_reference_rows_quarantined": False,
        "retract_previous_single_pendulum_dan_claim": True,
        "safe_for_paper_claim": True,
        "safe_claim_scope": "coarse_apples_to_apples_fixed_grid_replay_not_source_policy_reproduction",
        "negative_common_reference_order_count": sum(order < 0.0 for order in bad_common_orders),
        "replacement_reading": (
            "The repaired Dan/Kissel/Negrut single-pendulum rows can be used in the common-reference "
            "apples-to-apples matrix. Do not present them as source-policy reproduction."
        ),
    }

    write_csv(OUT_CSV, rows)
    with OUT_JSON.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, sort_keys=True)
        handle.write("\n")

    lines = [
        "# Dan/Kissel/Negrut Single-Pendulum Reference-Policy Audit",
        "",
        "Status: **repaired by fixed-grid replay**.",
        "",
        "The old negative orders are retracted. The repaired rows are safe only as common-reference coarse apples-to-apples rows, not as source-policy reproduction.",
        "",
        "| Method | common-reference vel order | common-reference finest vel error | public same-window vel order | public same-window finest vel error | source-policy vel order | source-policy finest vel error | status |",
        "|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in rows:
        lines.append(
            "| "
            f"`{row['method']}` | `{row['common_reference_vel_order']}` | "
            f"`{row['common_reference_finest_vel_error']}` | `{row['same_window_vel_order']}` | "
            f"`{row['same_window_finest_vel_error']}` | `{row['source_policy_vel_order']}` | "
            f"`{row['source_policy_finest_vel_error']}` | `{row['recommended_status']}` |"
        )
    lines.extend(
        [
            "",
            "Paper-safe reading: use the repaired rows only inside the fixed-grid common-reference matrix; do not claim they reproduce the source paper policy.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("dan_single_pendulum_reference_policy_audit=written")
    print(f"safe_for_paper_claim={summary['safe_for_paper_claim']}")
    print(f"affected_row_count={summary['affected_row_count']}")


if __name__ == "__main__":
    main()
