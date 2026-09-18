#!/usr/bin/env python3
"""Read-only validator for EXACT_STAGE_IDENTITY_NUMERICAL_CHECK.json / .md / .csv."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

PAPER = Path(__file__).resolve().parent
JSON_PATH = PAPER / "EXACT_STAGE_IDENTITY_NUMERICAL_CHECK.json"
MD_PATH = PAPER / "EXACT_STAGE_IDENTITY_NUMERICAL_CHECK.md"
CSV_PATH = PAPER / "EXACT_STAGE_IDENTITY_NUMERICAL_CHECK.csv"


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
        print(f"exact_stage_identity_numerical_check=FAIL\n- {exc}")
        return 1

    checks.check(data.get("schema") == "exact-stage-identity-numerical-check-v1", "schema changed")
    checks.check(data.get("status") == "reduced_collocation_recovered_at_roundoff", f"status is {data.get('status')}")
    checks.check(data.get("case") == "cylindrical_smooth", "case changed")
    checks.check(data.get("h_values") == [0.04, 0.02, 0.01], "h values changed")
    checks.check(data.get("t_final") == 0.08, "t_final changed")
    checks.check(data.get("run_v047_invoked") is False, "check must not invoke run_v047.py")
    checks.check(data.get("default_1e-4_required") is False, "check must not require default 1e-4")
    checks.check(data.get("heavy_numerical_run_invoked") is False, "check must not be a heavy run")
    checks.check(data.get("all_rows_ok") is True, "not all rows ok")
    checks.check(data.get("lemma") == "lem:exact-stage-identity", "lemma anchor changed")
    threshold = float(data.get("threshold", 0.0))
    checks.check(threshold == 1.0e-10, "threshold changed")
    rows = data.get("rows", [])
    checks.check(len(rows) == 3, "row count changed")
    for row in rows:
        checks.check(row.get("all_steps_converged") is True, f"h={row.get('h')}: Newton did not converge")
        checks.check(float(row.get("max_reduced_collocation_defect", 1.0)) <= threshold,
                     f"h={row.get('h')}: reduced collocation defect above threshold")
        checks.check(max(float(row.get("max_perpendicular_rel_point", 1.0)), float(row.get("max_perpendicular_rel_vel", 1.0)),
                         float(row.get("max_perpendicular_rel_acc", 1.0))) <= threshold,
                     f"h={row.get('h')}: relative vectors not parallel to the fixed direction")
        checks.check(float(row.get("max_factorization_mismatch", 1.0)) <= threshold,
                     f"h={row.get('h')}: implemented sliding row does not factor as reduced defect times n.axis")
        checks.check(float(row.get("min_abs_n_dot_axis", 0.0)) > 0.1, f"h={row.get('h')}: n.axis too small")
        checks.check(row.get("identity_within_threshold") is True, f"h={row.get('h')}: row not ok")
    checks.check(len(csv_rows) == len(rows), "csv row count differs from json")
    checks.check(md.startswith("# Exact Stage Identity Numerical Check"), "markdown header changed")
    checks.check(f"Status: `{data.get('status')}`" in md, "markdown status stale")
    checks.check(f"Rows ok: `{data.get('rows_ok')}`" in md, "markdown rows-ok marker stale")

    if checks.errors:
        print("exact_stage_identity_numerical_check=FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1
    print("exact_stage_identity_numerical_check=PASS")
    print(f"rows_ok={data.get('rows_ok')}")
    print(f"max_reduced_collocation_defect_overall={data.get('max_reduced_collocation_defect_overall'):.3e}")
    print("run_v047_invoked=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
