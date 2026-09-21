#!/usr/bin/env python3
"""Rebuild the TFE(m=3) four-link common-reference smoke artifact.

This is a targeted reproducibility script, not part of the full coarse
benchmark runner.  It checks whether the TFE(m=3) Gauss-Lobatto wrapper gives
usable convergence on the four-link example when compared to the same exact
v047 endpoint reference used by the closed-loop common-reference artifacts.
"""

from __future__ import annotations

import csv
import math
from pathlib import Path

import numpy as np

import build_closed_loop_true_dynamic_strict_common_reference as common
import closed_loop_fullva_dynamic_residual as dynres
import run_coarse_four_example_order as coarse


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
OUT_CSV = RESULTS / "tfe_m3_four_link_common_reference_smoke.csv"
METHOD = "tfe2026_TFE_m3_GL"
EXAMPLE = "four_link"
REFERENCE_METHOD = "v047_exact_kinematic_endpoint"
STEP_SIZES = (0.1, 0.05, 0.025)
T_END = 0.1


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"refusing to write empty {path.name}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def fmt(value: object) -> str:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return "nan"
    return "nan" if not math.isfinite(number) else f"{number:.16e}"


def estimate_order(rows: list[dict[str, object]], key: str) -> float:
    clean = sorted(
        [(float(row["h"]), float(row[key])) for row in rows if float(row[key]) > 0.0],
        reverse=True,
    )
    if len(clean) < 2:
        return float("nan")
    slope, _ = np.polyfit(np.log([h for h, _ in clean]), np.log([err for _, err in clean]), 1)
    return float(slope)


def exact_endpoint_reference() -> dict[str, np.ndarray]:
    v047 = common.import_v047_module()
    v046 = v047.load_v046()
    v046.patch_modern_numpy_scalar_assignments()
    models = {model.name: model for model in v046.MODELS}
    reference_system = common.setup_exact_system(
        v047,
        v046,
        models[EXAMPLE],
        common.REFERENCE_H,
        T_END,
    )
    return common.public_like_endpoint(dynres.endpoint_state_from_system(reference_system))


def candidate_row(reference: dict[str, np.ndarray], h: float) -> dict[str, object]:
    candidate = coarse.run_ra2021_tfe_multinode_model(
        example=EXAMPLE,
        h=h,
        t_end=T_END,
        m=3,
        nu=coarse.TFE2026_TFE_M3_NU,
    )
    return {
        "method": METHOD,
        "example": EXAMPLE,
        "reference_method": REFERENCE_METHOD,
        "h": fmt(h),
        "t_end": fmt(T_END),
        "pos_error": fmt(common.final_error_to_reference(candidate, reference, "pos")),
        "vel_error": fmt(common.final_error_to_reference(candidate, reference, "vel")),
        "acc_error": fmt(common.final_error_to_reference(candidate, reference, "acc")),
        "pos_order": "nan",
        "vel_order": "nan",
        "acc_order": "nan",
        "interpretation": "candidate row",
    }


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    reference = exact_endpoint_reference()
    rows = [candidate_row(reference, h) for h in STEP_SIZES]
    pos_order = estimate_order(rows, "pos_error")
    vel_order = estimate_order(rows, "vel_error")
    acc_order = estimate_order(rows, "acc_error")
    rows.append(
        {
            "method": METHOD,
            "example": EXAMPLE,
            "reference_method": REFERENCE_METHOD,
            "h": "nan",
            "t_end": fmt(T_END),
            "pos_error": "nan",
            "vel_error": "nan",
            "acc_error": "nan",
            "pos_order": fmt(pos_order),
            "vel_order": fmt(vel_order),
            "acc_order": fmt(acc_order),
            "interpretation": (
                "negative observed order; candidate stage solve is not accepted "
                "for convergence evidence"
            ),
        }
    )
    write_csv(OUT_CSV, rows)
    print("tfe_m3_four_link_common_reference_smoke=written")
    print(f"pos_order={pos_order:.6f}")
    print(f"vel_order={vel_order:.6f}")
    print(f"acc_order={acc_order:.6f}")
    print(f"csv={OUT_CSV}")


if __name__ == "__main__":
    main()
