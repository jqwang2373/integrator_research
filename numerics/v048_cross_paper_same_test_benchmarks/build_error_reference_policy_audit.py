#!/usr/bin/env python3
"""Audit whether reported errors are directly comparable across methods."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
SUMMARY_CSV = RESULTS / "coarse_four_example_order_summary.csv"
LARGE_STEP_CSV = RESULTS / "large_step_vp_local_order_summary.csv"
COMMON_REFERENCE_CSV = RESULTS / "common_reference_error_summary.csv"
COMMON_REFERENCE_JSON = RESULTS / "common_reference_error_summary.json"
OUT_CSV = RESULTS / "error_reference_policy_audit.csv"
OUT_JSON = RESULTS / "error_reference_policy_audit.json"
OUT_MD = RESULTS / "error_reference_policy_audit.md"

LOCAL = "local_Gauss6_FullVA"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"refusing to write empty {path.name}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def reference_policy(row: dict[str, str]) -> tuple[str, str]:
    method = row.get("method", "")
    example = row.get("example", "")
    notes = row.get("notes", "")
    evidence = row.get("evidence", "")
    if method == "vp2024_lie_group_ode_partitioning":
        return (
            "resolved_alias",
            "this VP label is resolved by vp_method_identity_audit as an alias of vp2024_coordinate_partitioning_rA",
        )
    if method == LOCAL and example == "single_pendulum":
        return (
            "local_analytic_reference",
            "local single-pendulum errors are produced against the local analytic/driven reference",
        )
    if method == LOCAL and example == "double_pendulum":
        return (
            "local_fullva_self_reference",
            "local double-pendulum errors use a local FullVA finer-step self-reference",
        )
    if method == LOCAL and example in {"four_link", "slider_crank"}:
        return (
            "local_v047_exact_endpoint_reference",
            "local closed-loop errors use the v047 exact endpoint reference",
        )
    if "self-reference" in notes:
        return (
            "method_self_reference",
            "this method is compared to its own finer-step trajectory, so its finest error is not a common-reference error",
        )
    if "public kinematics reference" in notes:
        return (
            "public_kinematics_reference",
            "public dynamics are compared against the public kinematics reference, not the local reference",
        )
    if "finer public dynamics reference" in notes:
        return (
            "public_dynamics_self_reference",
            "public double-pendulum dynamics are compared against finer public dynamics",
        )
    if "in-suite rA reference" in notes:
        return (
            "hi2022_in_suite_rA_reference",
            "HI2022 rows use the in-suite rA reference, not the local reference",
        )
    if method.startswith("tfe2026_") and row.get("status") == "ok":
        return (
            "tfe_method_self_reference",
            "TFE rows are compared against the same wrapped TFE method at the reference h",
        )
    if "strict reference skipped" in notes or "Common-reference candidate smoke" in notes:
        return (
            "rejected_candidate_smoke",
            "this row is rejected diagnostic evidence, not accepted error evidence",
        )
    if row.get("status") != "ok":
        return ("not_accepted", "row is not accepted for direct error comparison")
    return ("unclassified", f"unclassified reference policy from evidence={evidence}")


def main() -> None:
    rows = read_csv(SUMMARY_CSV)
    large_step_rows = read_csv(LARGE_STEP_CSV) if LARGE_STEP_CSV.exists() else []
    common_reference_rows = read_csv(COMMON_REFERENCE_CSV) if COMMON_REFERENCE_CSV.exists() else []
    common_reference_summary = {}
    if COMMON_REFERENCE_JSON.exists():
        with COMMON_REFERENCE_JSON.open(encoding="utf-8") as handle:
            common_reference_summary = json.load(handle)
    out_rows: list[dict[str, object]] = []
    accepted_nonlocal_rows = 0
    mixed_policy_direct_error_comparable_vs_local = 0
    order_comparable_rows = 0

    for row in rows:
        policy, reason = reference_policy(row)
        is_local = row.get("method") == LOCAL
        accepted = row.get("status") == "ok"
        order_valid = accepted and not is_local
        direct_error_valid = False
        if accepted and not is_local:
            accepted_nonlocal_rows += 1
            order_comparable_rows += 1
        out_rows.append(
            {
                "dataset": "main_coarse_h_0.1_0.05_0.025",
                "method": row.get("method", ""),
                "example": row.get("example", ""),
                "status": row.get("status", ""),
                "reference_policy": policy,
                "observed_order_comparable": order_valid,
                "direct_error_vs_local_comparable": direct_error_valid,
                "reported_finest_vel_error": row.get("finest_vel_error", "nan"),
                "reported_vel_error_ratio_vs_local": row.get("vel_error_ratio_vs_local", "nan"),
                "reason": reason,
            }
        )
        mixed_policy_direct_error_comparable_vs_local += int(direct_error_valid)

    large_step_local_order_wins = 0
    large_step_reported_error_wins = 0
    large_step_direct_error_wins = 0
    if large_step_rows:
        by_key = {(row["method"], row["example"]): row for row in large_step_rows}
        examples = sorted({row["example"] for row in large_step_rows})
        for example in examples:
            local = by_key.get((LOCAL, example), {})
            vp = by_key.get(("vp2024_coordinate_partitioning_rA", example), {})
            if not local or not vp:
                continue
            try:
                large_step_local_order_wins += int(float(local["vel_order"]) > float(vp["vel_order"]))
                large_step_reported_error_wins += int(
                    float(local["finest_vel_error"]) < float(vp["finest_vel_error"])
                )
            except (KeyError, ValueError):
                pass
            out_rows.append(
                {
                    "dataset": "large_step_vp_audit_h_0.15_0.075_0.0375",
                    "method": "vp2024_coordinate_partitioning_rA",
                    "example": example,
                    "status": vp.get("status", ""),
                    "reference_policy": "mixed_local_vs_vp_self_reference",
                    "observed_order_comparable": True,
                    "direct_error_vs_local_comparable": False,
                    "reported_finest_vel_error": vp.get("finest_vel_error", "nan"),
                    "reported_vel_error_ratio_vs_local": "nan",
                    "reason": (
                        "large-step audit compares observed slopes, but local and VP finest errors still "
                        "come from different reference policies; reported error wins are not direct "
                        "common-reference error wins"
                    ),
                }
            )

    common_direct_error_rows = 0
    common_local_error_wins = 0
    common_local_order_wins = 0
    for row in common_reference_rows:
        if row.get("method") == LOCAL or row.get("status") != "ok":
            continue
        common_direct_error_rows += 1
        common_local_error_wins += int(row.get("local_finest_vel_error_win") == "true")
        common_local_order_wins += int(row.get("local_vel_order_win") == "true")
        out_rows.append(
            {
                "dataset": "common_reference_h_0.1_0.05_0.025",
                "method": row.get("method", ""),
                "example": row.get("example", ""),
                "status": row.get("status", ""),
                "reference_policy": row.get("reference_policy", ""),
                "observed_order_comparable": True,
                "direct_error_vs_local_comparable": True,
                "reported_finest_vel_error": row.get("finest_vel_error", "nan"),
                "reported_vel_error_ratio_vs_local": row.get("vel_error_ratio_vs_local", "nan"),
                "reason": (
                    "separate common-reference audit: this method and the local method share the same "
                    "per-example final-state reference and norm, so the velocity error ratio is direct "
                    "cross-method error evidence"
                ),
            }
        )

    summary = {
        "schema": "error-reference-policy-audit-v1",
        "main_row_count": len(rows),
        "accepted_nonlocal_rows": accepted_nonlocal_rows,
        "observed_order_comparable_rows": order_comparable_rows,
        "mixed_policy_direct_error_vs_local_comparable_rows": mixed_policy_direct_error_comparable_vs_local,
        "common_reference_direct_error_vs_local_comparable_rows": common_direct_error_rows,
        "direct_error_vs_local_comparable_rows": common_direct_error_rows,
        "common_reference_local_velocity_order_wins": common_local_order_wins,
        "common_reference_local_finest_velocity_error_wins": common_local_error_wins,
        "common_reference_direct_error_superiority_claim": common_reference_summary.get(
            "direct_error_superiority_claim",
            False,
        ),
        "large_step_local_velocity_order_wins_vs_vp": large_step_local_order_wins,
        "large_step_local_reported_finest_velocity_error_wins_vs_vp": large_step_reported_error_wins,
        "large_step_local_direct_common_reference_error_wins_vs_vp": large_step_direct_error_wins,
        "claim": (
            "Observed order comparisons are usable because each method has a consistent step-size "
            "sweep. The main coarse matrix still has mixed reference policies, but the separate "
            "common-reference audit supplies direct final-state velocity-error evidence for the "
            "runnable accepted methods. Rejected/source-unresolved methods remain outside that claim."
        ),
    }

    write_csv(OUT_CSV, out_rows)
    with OUT_JSON.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, sort_keys=True)
        handle.write("\n")

    lines = [
        "# Error Reference Policy Audit",
        "",
        f"Observed-order comparable rows: `{summary['observed_order_comparable_rows']}`.",
        f"Direct error-vs-local comparable rows: `{summary['direct_error_vs_local_comparable_rows']}`.",
        f"Mixed-policy direct error-vs-local comparable rows: `{summary['mixed_policy_direct_error_vs_local_comparable_rows']}`.",
        f"Common-reference direct error-vs-local comparable rows: `{summary['common_reference_direct_error_vs_local_comparable_rows']}`.",
        f"Common-reference local velocity-order wins: `{summary['common_reference_local_velocity_order_wins']}/{summary['common_reference_direct_error_vs_local_comparable_rows']}`.",
        f"Common-reference local finest-velocity-error wins: `{summary['common_reference_local_finest_velocity_error_wins']}/{summary['common_reference_direct_error_vs_local_comparable_rows']}`.",
        f"Larger-step local velocity-order wins vs VP: `{summary['large_step_local_velocity_order_wins_vs_vp']}/4`.",
        f"Larger-step local reported finest-velocity-error wins vs VP: `{summary['large_step_local_reported_finest_velocity_error_wins_vs_vp']}/4`.",
        f"Larger-step local direct common-reference error wins vs VP: `{summary['large_step_local_direct_common_reference_error_wins_vs_vp']}/4`.",
        "",
        summary["claim"],
        "",
        "| Dataset | Method | Example | reference policy | order comparable | direct error comparable | reason |",
        "|---|---|---|---|---:|---:|---|",
    ]
    for row in out_rows:
        lines.append(
            "| "
            f"`{row['dataset']}` | `{row['method']}` | `{row['example']}` | `{row['reference_policy']}` | "
            f"`{row['observed_order_comparable']}` | `{row['direct_error_vs_local_comparable']}` | "
            f"{row['reason']} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("error_reference_policy_audit=written")
    print(f"observed_order_comparable_rows={summary['observed_order_comparable_rows']}")
    print(f"direct_error_vs_local_comparable_rows={summary['direct_error_vs_local_comparable_rows']}")
    print(
        "common_reference_local_finest_velocity_error_wins="
        f"{summary['common_reference_local_finest_velocity_error_wins']}/"
        f"{summary['common_reference_direct_error_vs_local_comparable_rows']}"
    )
    print(
        "large_step_local_reported_finest_velocity_error_wins_vs_vp="
        f"{summary['large_step_local_reported_finest_velocity_error_wins_vs_vp']}/4"
    )


if __name__ == "__main__":
    main()
