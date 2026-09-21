#!/usr/bin/env python3
"""Read-only validator for P2_CONSTANTS_NUMERICAL_CHECK.json / .md / .csv (schema v2)."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

PAPER = Path(__file__).resolve().parent
JSON_PATH = PAPER / "P2_CONSTANTS_NUMERICAL_CHECK.json"
MD_PATH = PAPER / "P2_CONSTANTS_NUMERICAL_CHECK.md"
CSV_PATH = PAPER / "P2_CONSTANTS_NUMERICAL_CHECK.csv"

ALLOWED_STATUS = {
    "inverse_bound_observed_neumann_threshold_certified",
    "inverse_bound_observed_neumann_threshold_below_reported_h",
}
H_VALUES = [0.04, 0.02, 0.01]


class Checks:
    def __init__(self) -> None:
        self.errors: list[str] = []

    def check(self, condition: bool, message: str) -> None:
        if not condition:
            self.errors.append(message)


def check_rows(checks: Checks, rows: list[dict], label: str) -> None:
    checks.check(len(rows) == 3, f"{label}: row count changed")
    checks.check([r.get("h") for r in rows] == H_VALUES, f"{label}: h values changed")
    for row in rows:
        h = row.get("h")
        checks.check(row.get("variant") == label, f"{label} h={h}: variant label changed")
        checks.check(row.get("all_solves_converged") is True, f"{label} h={h}: Newton did not converge")
        checks.check(row.get("inverse_bound_observed") is True, f"{label} h={h}: inverse bound not observed")
        checks.check(float(row.get("max_Jh_inverse_over_J0_inverse", 9.0)) <= 2.0, f"{label} h={h}: ||J_h^-1|| exceeds 2 ||J_0^-1||")
        checks.check(float(row.get("max_h0_root_endpoint_deviation", 1.0)) <= 1.0e-9, f"{label} h={h}: h=0 root does not reproduce the endpoint state")
        m0 = float(row.get("max_J0_inverse_norm_M0", 0.0))
        cj = float(row.get("max_CJ_ratio", 0.0))
        checks.check(m0 > 0.0 and cj > 0.0, f"{label} h={h}: M0 or C_J not positive")
        checks.check(abs(float(row.get("implied_h0", -1.0)) - 1.0 / (2.0 * m0 * cj)) <= 1e-9 * (1.0 / (2.0 * m0 * cj)),
                     f"{label} h={h}: implied h0 not equal to 1/(2 M0 C_J)")
        wcj = float(row.get("weighted_norm_max_CJ_ratio", 0.0))
        checks.check(wcj > 0.0, f"{label} h={h}: weighted-norm C_J not positive")
        checks.check(abs(float(row.get("weighted_norm_implied_h0", -1.0)) - 1.0 / (2.0 * wcj)) <= 1e-9 / (2.0 * wcj),
                     f"{label} h={h}: weighted-norm implied h0 not equal to 1/(2 C_J)")
        checks.check(float(row.get("equilibrated_implied_h0", 0.0)) > 0.0, f"{label} h={h}: equilibrated h0 not positive")
        checks.check(row.get("neumann_condition_met") == (float(row.get("max_neumann_margin_M0_delta", 1.0)) <= 0.5),
                     f"{label} h={h}: Neumann flag inconsistent with the recorded margin")
        checks.check(row.get("weighted_norm_neumann_condition_met") == (float(row.get("weighted_norm_max_neumann_margin", 1.0)) <= 0.5),
                     f"{label} h={h}: weighted Neumann flag inconsistent with the recorded margin")
        checks.check(row.get("h_le_implied_h0") == (float(h) <= float(row.get("implied_h0", 0.0))), f"{label} h={h}: implied-h0 flag inconsistent")
        checks.check(row.get("h_le_weighted_norm_implied_h0") == (float(h) <= float(row.get("weighted_norm_implied_h0", 0.0))),
                     f"{label} h={h}: weighted implied-h0 flag inconsistent")
        checks.check(float(row.get("dominant_block_max_entry_ratio", 0.0)) >= float(row.get("next_block_max_entry_ratio", 1.0)),
                     f"{label} h={h}: dominant block is not the largest")
        checks.check(float(row.get("max_lifted_predictor_distance", 1.0)) < float(row.get("max_implemented_predictor_distance", 0.0)),
                     f"{label} h={h}: lifted predictor is not closer than the implemented predictor")
        checks.check(row.get("first_newton_step_contracts_from_implemented_predictor")
                     == (float(row.get("max_first_newton_contraction_from_implemented_predictor", 9.0)) < 1.0),
                     f"{label} h={h}: first-step contraction flag inconsistent")
    dists = [float(r.get("max_lifted_predictor_distance", 0.0)) for r in rows]
    checks.check(all(dists[i] > dists[i + 1] for i in range(len(dists) - 1)), f"{label}: lifted predictor distance does not decrease with h")


def main() -> int:
    checks = Checks()
    try:
        data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
        md = MD_PATH.read_text(encoding="utf-8")
        with CSV_PATH.open(encoding="utf-8") as handle:
            csv_rows = list(csv.DictReader(handle))
    except Exception as exc:  # noqa: BLE001
        print(f"p2_constants_numerical_check=FAIL\n- {exc}")
        return 1

    checks.check(data.get("schema") == "p2-constants-numerical-check-v2", "schema changed")
    checks.check(data.get("status") in ALLOWED_STATUS, f"status is {data.get('status')}")
    checks.check(data.get("case") == "cylindrical_smooth", "case changed")
    checks.check(data.get("h_values") == H_VALUES, "h values changed")
    checks.check(data.get("t_final") == 0.08, "t_final changed")
    checks.check(data.get("norm") == "euclidean_operator_norm_on_implemented_stage_layout", "norm changed")
    checks.check(data.get("additional_norms") == ["endpoint_linearized_J0_weighted_residual_norm", "row_column_equilibrated_euclidean_norm"],
                 "additional norms changed")
    checks.check(data.get("run_v047_invoked") is False, "check must not invoke run_v047.py")
    checks.check(data.get("default_1e-4_required") is False, "check must not require default 1e-4")
    checks.check(data.get("heavy_numerical_run_invoked") is False, "check must not be a heavy run")
    checks.check(data.get("all_rows_ok") is True, "not all rows observed the inverse bound")
    checks.check(data.get("lemmas") == ["lem:p2-from-p1", "lem:newton-envelope"], "lemma anchors changed")

    rows = data.get("rows", [])
    rows_nf = data.get("frictionless_rows", [])
    check_rows(checks, rows, "cylindrical_smooth")
    check_rows(checks, rows_nf, "cylindrical_smooth_frictionless")

    neumann = data.get("neumann_condition_met_on_all_reported_h")
    checks.check(neumann == all(r.get("neumann_condition_met") for r in rows), "Neumann summary flag stale")
    checks.check(data.get("weighted_norm_neumann_condition_met_on_all_reported_h") == all(r.get("weighted_norm_neumann_condition_met") for r in rows),
                 "weighted Neumann summary flag stale")
    expected_status = ("inverse_bound_observed_neumann_threshold_certified" if neumann
                       else "inverse_bound_observed_neumann_threshold_below_reported_h")
    checks.check(data.get("status") == expected_status, "status inconsistent with the Neumann flag")
    checks.check(bool(data.get("all_reported_h_below_implied_h0")) == bool(neumann), "implied-h0 flag inconsistent with the Neumann flag")
    checks.check(data.get("all_reported_h_below_weighted_norm_implied_h0") == all(r.get("h_le_weighted_norm_implied_h0") for r in rows),
                 "weighted implied-h0 summary flag stale")

    def close(a: float, b: float) -> bool:
        return abs(a - b) <= 1e-12 * max(1.0, abs(b))

    checks.check(close(float(data.get("M0_overall", -1.0)), max(float(r["max_J0_inverse_norm_M0"]) for r in rows)), "M0_overall stale")
    checks.check(close(float(data.get("CJ_overall", -1.0)), max(float(r["max_CJ_ratio"]) for r in rows)), "CJ_overall stale")
    checks.check(close(float(data.get("implied_h0_overall", -1.0)), min(float(r["implied_h0"]) for r in rows)), "implied_h0_overall stale")
    checks.check(close(float(data.get("weighted_norm_implied_h0_overall", -1.0)), min(float(r["weighted_norm_implied_h0"]) for r in rows)),
                 "weighted_norm_implied_h0_overall stale")

    friction = data.get("friction_attribution", {})
    checks.check(friction.get("stribeck_velocity") == 0.5, "Stribeck velocity of the smooth case changed")
    checks.check(friction.get("frictionless_variant_all_solves_converged") is True, "frictionless variant did not converge")
    checks.check(friction.get("frictionless_variant_inverse_bound_observed") is True, "frictionless variant inverse bound not observed")
    checks.check(close(float(friction.get("weighted_norm_CJ_overall_with_friction", -1.0)), max(float(r["weighted_norm_max_CJ_ratio"]) for r in rows)),
                 "friction attribution C_J (with friction) stale")
    checks.check(close(float(friction.get("weighted_norm_CJ_overall_frictionless", -1.0)), max(float(r["weighted_norm_max_CJ_ratio"]) for r in rows_nf)),
                 "friction attribution C_J (frictionless) stale")
    checks.check(float(friction.get("weighted_norm_CJ_overall_frictionless", 1.0)) < float(friction.get("weighted_norm_CJ_overall_with_friction", 0.0)),
                 "frictionless C_J is not smaller than the frictional one")
    checks.check(friction.get("dominant_block_with_friction") == [r.get("dominant_block_of_jacobian_difference") for r in rows],
                 "dominant block record (with friction) stale")
    checks.check(friction.get("dominant_block_frictionless") == [r.get("dominant_block_of_jacobian_difference") for r in rows_nf],
                 "dominant block record (frictionless) stale")
    checks.check(all(b == "dynxv" for b in friction.get("dominant_block_with_friction", [])),
                 "with friction the dominant block is expected to be Newton-Euler rows x stage velocities")

    checks.check(len(csv_rows) == len(rows) + len(rows_nf), "csv row count differs from json")
    checks.check(md.startswith("# P2 Constants Numerical Check"), "markdown header changed")
    checks.check(f"Status: `{data.get('status')}`" in md, "markdown status stale")

    if checks.errors:
        print("p2_constants_numerical_check=FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1
    print("p2_constants_numerical_check=PASS")
    print(f"status={data.get('status')}")
    print(f"M0_overall={data.get('M0_overall'):.3e}")
    print(f"CJ_overall={data.get('CJ_overall'):.3e}")
    print(f"implied_h0_overall={data.get('implied_h0_overall'):.3e}")
    print(f"weighted_norm_implied_h0_overall={data.get('weighted_norm_implied_h0_overall'):.3e}")
    print(f"frictionless_weighted_norm_implied_h0={friction.get('weighted_norm_implied_h0_frictionless'):.3e}")
    print(f"neumann_condition_met_on_all_reported_h={neumann}")
    print("run_v047_invoked=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
