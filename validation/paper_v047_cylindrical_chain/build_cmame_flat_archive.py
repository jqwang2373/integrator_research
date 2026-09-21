#!/usr/bin/env python3
"""Build the flat CMAME source archive with root-level entries."""

from __future__ import annotations

from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


PAPER = Path(__file__).resolve().parent
from paper_paths import LATEX, package_path as manuscript_path
FLAT = LATEX / "cmame_submission_flat"
OUT = LATEX / "cmame_submission_flat.zip"

FILES = [
    "main_cmame_submission.tex",
    "main_cmame_submission.pdf",
    "highlights_cmame.txt",
    "declarations_cmame.md",
    "Figure_1_convergence.png",
    "Figure_2_asme_lower_pair_graph_bridge.png",
    "Figure_3_asme_closed_loop_kinematic_fullva.png",
    "Figure_4_order_closure_blend.png",
    "Figure_5_velocity_compression.png",
    "Figure_6_sparse_speed_gap.png",
    "Figure_7_strict_common_reference_work_precision.png",
    "Figure_8_claim_boundary_limitations.png",
    "Figure_9_coarse_baseline_work_precision.png",
    "Figure_10_closed_loop_true_dynamic_order.png",
    "Figure_11_method_stage_architecture.png",
    "Figure_12_all_method_result_matrix.png",
    "Figure_13_work_precision_compendium.png",
]


def main() -> None:
    missing = [name for name in FILES if not (FLAT / name).exists()]
    if missing:
        raise FileNotFoundError(", ".join(missing))
    with ZipFile(OUT, "w", ZIP_DEFLATED) as archive:
        for name in FILES:
            archive.write(FLAT / name, arcname=name)
    print("cmame_flat_archive=written")
    print(f"entries={len(FILES)}")
    print(f"archive={OUT.name}")


if __name__ == "__main__":
    main()
