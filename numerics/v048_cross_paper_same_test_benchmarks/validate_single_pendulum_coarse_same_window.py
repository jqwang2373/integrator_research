#!/usr/bin/env python3
"""Validate the coarse-first same-window single-pendulum artifacts."""

from __future__ import annotations

import csv
import json
import math
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
FORMS = {"rA", "rp", "reps"}
STEP_SIZES = {0.1, 0.05, 0.025}


class Checks:
    def __init__(self) -> None:
        self.errors: list[str] = []

    def check(self, condition: bool, message: str) -> None:
        if not condition:
            self.errors.append(message)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def read_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def as_float(value: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return float("nan")


def main() -> int:
    checks = Checks()
    try:
        public_rows = read_csv(RESULTS / "ra2021_single_pendulum_coarse_order_rows.csv")
        local_rows = read_csv(RESULTS / "gauss6_fullva_public_horizon_single_coarse_rows.csv")
        work_rows = read_csv(RESULTS / "single_pendulum_coarse_same_window_work_precision_summary.csv")
        summary = read_json(RESULTS / "single_pendulum_coarse_same_window_work_precision_summary.json")
        report = (RESULTS / "single_pendulum_coarse_same_window_work_precision_summary.md").read_text(
            encoding="utf-8"
        )
    except Exception as exc:  # noqa: BLE001 - concise CLI failure.
        print(f"single-pendulum coarse same-window validation: FAIL\n- {exc}")
        return 1

    checks.check(len(public_rows) == 9, "public single coarse rows should be three forms x three steps")
    checks.check(len(local_rows) == 3, "local single coarse rows should have three steps")
    checks.check(len(work_rows) == 4, "work/precision summary should have four method rows")
    checks.check(summary.get("policy") == "ra2021_single_pendulum_coarse_same_window_work_precision_summary", "summary policy changed")
    checks.check(summary.get("default_policy") == "coarse_first_no_default_1e-4", "default policy changed")
    checks.check(summary.get("external_superiority_claim") is False, "must not claim external superiority")
    checks.check(summary.get("row_count") == 4, "summary row count changed")
    checks.check(summary.get("ok_row_count") == 4, "summary ok count changed")
    checks.check(summary.get("selected_step_sizes") == [0.1, 0.05, 0.025], "selected step sizes changed")
    checks.check(summary.get("selected_reference_h") == 0.0125, "selected reference h changed")

    forms = {row.get("form") for row in public_rows}
    checks.check(forms == FORMS, "public form set changed")
    checks.check({as_float(row.get("h", "nan")) for row in public_rows} == STEP_SIZES, "public step set changed")
    checks.check(all(row.get("status") == "ok" for row in public_rows), "public rows must all be ok")
    checks.check(all(row.get("public_policy_h") == "False" for row in public_rows), "public coarse rows must not be source h policy")
    checks.check(all(row.get("coarse_same_window_policy") == "True" for row in public_rows), "public coarse flag missing")

    checks.check({as_float(row.get("h", "nan")) for row in local_rows} == STEP_SIZES, "local step set changed")
    checks.check(all(row.get("status") == "ok" for row in local_rows), "local rows must all be ok")
    checks.check(all(row.get("public_policy_h") == "False" for row in local_rows), "local coarse rows must not be source h policy")
    checks.check(all(row.get("coarse_same_window_policy") == "True" for row in local_rows), "local coarse flag missing")

    by_method = {row.get("method"): row for row in work_rows}
    for method in [
        "Gauss6/FullVA-public-horizon-single-coarse",
        "rA-public-dynamics-coarse",
        "rp-public-dynamics-coarse",
        "reps-public-dynamics-coarse",
    ]:
        row = by_method.get(method, {})
        checks.check(row.get("ok_row_count") == "3", f"{method} should summarize three ok rows")
        checks.check(math.isfinite(as_float(row.get("pos_observed_order", "nan"))), f"{method} missing position order")
        checks.check(math.isfinite(as_float(row.get("vel_observed_order", "nan"))), f"{method} missing velocity order")
        checks.check(math.isfinite(as_float(row.get("finest_runtime_sec", "nan"))), f"{method} missing runtime")
    gauss = by_method.get("Gauss6/FullVA-public-horizon-single-coarse", {})
    checks.check(as_float(gauss.get("pos_observed_order", "nan")) > 5.0, "Gauss6 single coarse position order too low")

    checks.check("coarse-first evidence only; not external superiority" in report, "report missing claim boundary")
    checks.check("intentionally avoids default `1e-4` rows" in report, "report missing no-default-1e-4 boundary")

    if checks.errors:
        print("single-pendulum coarse same-window validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("single-pendulum coarse same-window validation: PASS")
    print("public_rows=9/9")
    print("local_rows=3/3")
    print("work_precision_rows=4/4")
    print(f"gauss6_pos_order={as_float(gauss.get('pos_observed_order', 'nan')):.3f}")
    print("external_superiority_claim=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
