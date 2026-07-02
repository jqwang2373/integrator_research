#!/usr/bin/env python3
"""Audit whether the unresolved VP label is a distinct missing method."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
OUT_CSV = RESULTS / "vp_method_identity_audit.csv"
OUT_JSON = RESULTS / "vp_method_identity_audit.json"
OUT_MD = RESULTS / "vp_method_identity_audit.md"


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
            "source_id": "asme_2023_vp_doi",
            "source_url": "https://doi.org/10.1115/DETC2023-116950",
            "evidence_type": "primary_metadata_abstract",
            "observed_method_feature": (
                "independent coordinates integrated directly; dependent coordinates recovered "
                "from position and velocity constraints; Lie-group integration obtains A"
            ),
            "local_wrapper_feature": (
                "pivoted QR selects independent/dependent coordinates; independent velocities "
                "are advanced explicitly; dependent positions are recovered by constraint Newton; "
                "dependent velocities are recovered from velocity constraints; orientations use rA "
                "matrix updates"
            ),
            "status": "matches_local_coordinate_partitioning_wrapper",
            "interpretation": (
                "The paper title 'Using Velocity Partitioning in the rA Formulation...' and "
                "the DOI metadata describe the same coordinate-partitioning Lie-group ODE "
                "method implemented as vp2024_coordinate_partitioning_rA."
            ),
        },
        {
            "source_id": "easychair_performance_preprint_13546",
            "source_url": "results/vp_easychair_preprint_13546.txt",
            "evidence_type": "reference_chain",
            "observed_method_feature": (
                "performance preprint compares fully implicit, half implicit, and velocity "
                "coordinate partitioning; reference [5] is the ASME 2023 velocity-partitioning "
                "paper"
            ),
            "local_wrapper_feature": "vp2024_coordinate_partitioning_rA covers the coordinate-partitioning method",
            "status": "no_extra_distinct_vp_method_identified",
            "interpretation": (
                "The preprint's coordinate-partitioning method points to the ASME 2023 VP paper. "
                "It does not expose a second distinct Lie-group ODE partitioning method beyond "
                "that coordinate-partitioning VP method."
            ),
        },
        {
            "source_id": "local_v048_wrapper",
            "source_url": "run_coarse_four_example_order.py",
            "evidence_type": "implementation_identity",
            "observed_method_feature": "vp2024_coordinate_partitioning_rA",
            "local_wrapper_feature": (
                "implements the VP coordinate partitioning rA update on all four benchmark examples"
            ),
            "status": "alias_resolved",
            "interpretation": (
                "vp2024_lie_group_ode_partitioning should be treated as an alias of the accepted "
                "vp2024_coordinate_partitioning_rA wrapper, not as a separate source-unresolved "
                "baseline row."
            ),
        },
    ]
    summary = {
        "schema": "vp-method-identity-audit-v1",
        "row_count": len(rows),
        "alias_method": "vp2024_lie_group_ode_partitioning",
        "implemented_method": "vp2024_coordinate_partitioning_rA",
        "alias_resolved": True,
        "distinct_unresolved_vp_method_remaining": False,
        "claim": (
            "The VP Lie-group ODE partitioning label is resolved as the same method already "
            "implemented as vp2024_coordinate_partitioning_rA. This does not create a new "
            "independent comparison row; it removes the duplicate unresolved VP gate."
        ),
    }
    write_csv(OUT_CSV, rows)
    with OUT_JSON.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, sort_keys=True)
        handle.write("\n")

    lines = [
        "# VP Method Identity Audit",
        "",
        f"Alias method: `{summary['alias_method']}`.",
        f"Implemented method: `{summary['implemented_method']}`.",
        f"Alias resolved: `{summary['alias_resolved']}`.",
        f"Distinct unresolved VP method remaining: `{summary['distinct_unresolved_vp_method_remaining']}`.",
        "",
        summary["claim"],
        "",
        "| Source | evidence | status | interpretation |",
        "|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            "| "
            f"`{row['source_id']}` | `{row['evidence_type']}` | `{row['status']}` | "
            f"{row['interpretation']} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("vp_method_identity_audit=written")
    print(f"alias_resolved={summary['alias_resolved']}")
    print(f"implemented_method={summary['implemented_method']}")


if __name__ == "__main__":
    main()
