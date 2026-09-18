#!/usr/bin/env python3
"""Read-only validator for P2_CONSTANTS_NUMERICAL_CHECK.json / .md / .csv."""

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


class Checks:
    def __init__(self) -> None:
        self.errors: list[str] = []

    def check(self, condition: bool, message: str) -> None:
        if not condition:
            self.errors.append(message)


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

    checks.check(data.get("schema") == "p2-constants-numerical-check-v1", "schema changed")
    checks.check(data.get("status") in ALLOWED_STATUS, f"status is {data.get('status')}")
    checks.check(data.get("case") == "cylindrical_smooth", "case changed")
    checks.check(data.get("h_values") == [0.04, 0.02, 0.01], "h values changed")
    checks.check(data.get("t_final") == 0.08, "t_final changed")
    checks.check(data.get("norm") == "euclidean_operator_norm_on_implemented_stage_layout", "norm changed")
    checks.check(data.get("run_v047_invoked") is False, "check must not invoke run_v047.py")
    checks.check(data.get("default_1e-4_required") is False, "check must not require default 1e-4")
    checks.check(data.get("heavy_numerical_run_invoked") is False, "check must not be a heavy run")
    checks.check(data.get("all_rows_ok") is True, "not all rows observed the inverse bound")
    checks.check(data.get("lemmas") == ["lem:p2-from-p1", "lem:newton-envelope"], "lemma anchors changed")
    # status must agree with the recorded Neumann flag
    neumann = data.get("neumann_condition_met_on_all_reported_h")
    expected_status = ("inverse_bound_observed_neumann_threshold_certified" if neumann
                       else "inverse_bound_observed_neumann_threshold_below_reported_h")
    checks.check(data.get("status") == expected_status, "status inconsistent with the Neumann flag")
    checks.check(bool(data.get("all_reported_h_below_implied_h0")) == bool(neumann),
                 "implied-h0 flag inconsistent with the Neumann flag")
    rows = data.get("rows", [])
    checks.check(len(rows) == 3, "row count changed")
    m0_overall = 0.0
    for row in rows:
        checks.check(row.get("all_solves_converged") is True, f"h={row.get('h')}: Newton did not converge")
        checks.check(row.get("inverse_bound_observed") is True, f"h={row.get('h')}: inverse bound not observed")
        checks.check(float(row.get("max_Jh_inverse_over_J0_inverse", 9.0)) <= 2.0,
                     f"h={row.get('h')}: ||J_h^-1|| exceeds 2 ||J_0^-1||")
        checks.check(float(row.get("max_h0_root_endpoint_deviation", 1.0)) <= 1.0e-9,
                     f"h={row.get('h')}: h=0 root does not reproduce the endpoint state")
        checks.check(float(row.get("max_J0_inverse_norm_M0", 0.0)) > 0.0, f"h={row.get('h')}: M0 not positive")
        checks.check(float(row.get("max_CJ_ratio", 0.0)) > 0.0, f"h={row.get('h')}: C_J not positive")
        checks.check(row.get("neumann_condition_met") == (float(row.get("max_neumann_margin_M0_delta", 1.0)) <= 0.5),
                     f"h={row.get('h')}: Neumann flag inconsistent with the recorded margin")
        checks.check(row.get("h_le_implied_h0") == (float(row.get("h")) <= float(row.get("implied_h0", 0.0))),
                     f"h={row.get('h')}: implied-h0 flag inconsistent")
        checks.check(float(row.get("max_lifted_predictor_distance", 1.0)) < float(row.get("max_implemented_predictor_distance", 0.0)),
                     f"h={row.get('h')}: lifted predictor is not closer than the implemented predictor")
        m0_overall = max(m0_overall, float(row.get("max_J0_inverse_norm_M0", 0.0)))
    # lifted predictor distance must decrease with h (O(h) behaviour)
    dists = [float(r.get("max_lifted_predictor_distance", 0.0)) for r in rows]
    checks.check(all(dists[i] > dists[i + 1] for i in range(len(dists) - 1)),
                 "lifted predictor distance does not decrease with h")
    checks.check(abs(float(data.get("M0_overall", -1.0)) - m0_overall) <= 1e-12 * max(1.0, m0_overall), "M0_overall stale")
    checks.check(len(csv_rows) == len(rows), "csv row count differs from json")
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
    print(f"neumann_condition_met_on_all_reported_h={neumann}")
    print("run_v047_invoked=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
