#!/usr/bin/env python3
"""Record a source-backed scope decision for the TFE(m=3) four-link failure."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
OUT_CSV = RESULTS / "tfe_m3_scope_exclusion_audit.csv"
OUT_JSON = RESULTS / "tfe_m3_scope_exclusion_audit.json"
OUT_MD = RESULTS / "tfe_m3_scope_exclusion_audit.md"


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"refusing to write empty {path.name}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    rows = [
        {
            "source": "s11044-026-10153-w.txt",
            "evidence_type": "paper_numerical_scope",
            "evidence_location": "Section 4, lines around 1005-1049 in extracted text",
            "status": "single_revolute_pendulum_scope",
            "interpretation": (
                "The original TFE paper's numerical experiments use a single revolute-pair "
                "pendulum with friction/frictionless variants, not the ASME four-link benchmark."
            ),
        },
        {
            "source": "s11044-026-10153-w.txt",
            "evidence_type": "paper_order_caveat",
            "evidence_location": "Section 4, lines around 1078-1087 in extracted text",
            "status": "paper_reports_m3_order_loss",
            "interpretation": (
                "The paper states that the DAE TFE(m=3) implementation reaches only fourth-order "
                "accuracy rather than the ideal fifth-order ODE result, and attributes this to "
                "DAE stiffness/truncation effects."
            ),
        },
        {
            "source": "results/tfe_m3_four_link_solver_audit.csv",
            "evidence_type": "local_four_link_failure",
            "evidence_location": "strict/reference/relaxed/common-reference smoke rows",
            "status": "not_accepted_on_four_link",
            "interpretation": (
                "The local wrapper executes on single, double, and slider examples, but the "
                "four-link row fails strict reference solves and shows negative common-reference "
                "orders on the coarse h sweep."
            ),
        },
        {
            "source": "results/tfe_m3_four_link_common_reference_smoke.csv",
            "evidence_type": "negative_order_evidence",
            "evidence_location": "summary row",
            "status": "exclude_from_required_four_example_accepted_matrix",
            "interpretation": (
                "The m=3 four-link row is a rejected out-of-scope stress test of the paper formula, "
                "not a missing required accepted baseline. The accepted original-paper comparison "
                "uses Newmark-beta, trapezoidal, TFE(m=1), and TFE(m=2), plus the m=3 rows that "
                "run on the remaining examples as diagnostic evidence."
            ),
        },
    ]
    summary = {
        "schema": "tfe-m3-scope-exclusion-audit-v1",
        "row_count": len(rows),
        "method": "tfe2026_TFE_m3_GL",
        "failed_example": "four_link",
        "paper_numerical_scope": "single_revolute_pendulum",
        "paper_four_link_claim_found": False,
        "local_wrapper_partial_rows_run": ["single_pendulum", "double_pendulum", "slider_crank"],
        "source_backed_exclusion": True,
        "required_accepted_matrix_excludes_method": True,
        "claim": (
            "TFE(m=3) Gauss-Lobatto is not counted as a required accepted four-example baseline "
            "because the original paper validates a single revolute-pendulum setting, explicitly "
            "reports DAE order loss for m=3, and the local four-link wrapper gives rejected "
            "negative-order evidence rather than convergence."
        ),
    }
    write_csv(OUT_CSV, rows)
    with OUT_JSON.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, sort_keys=True)
        handle.write("\n")

    lines = [
        "# TFE(m=3) Scope Exclusion Audit",
        "",
        f"Method: `{summary['method']}`.",
        f"Failed example: `{summary['failed_example']}`.",
        f"Source-backed exclusion: `{summary['source_backed_exclusion']}`.",
        f"Required accepted matrix excludes method: `{summary['required_accepted_matrix_excludes_method']}`.",
        "",
        summary["claim"],
        "",
        "| Source | evidence | status | interpretation |",
        "|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            "| "
            f"`{row['source']}` | `{row['evidence_type']}` | `{row['status']}` | "
            f"{row['interpretation']} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("tfe_m3_scope_exclusion_audit=written")
    print(f"source_backed_exclusion={summary['source_backed_exclusion']}")


if __name__ == "__main__":
    main()
