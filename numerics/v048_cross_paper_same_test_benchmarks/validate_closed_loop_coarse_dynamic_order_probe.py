#!/usr/bin/env python3
"""Read-only validator for the coarse closed-loop dynamic-order probe."""

from __future__ import annotations

import csv
import json
import math
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
MODELS = {"four_link", "slider_crank"}


class Checks:
    def __init__(self) -> None:
        self.errors: list[str] = []

    def check(self, condition: bool, message: str) -> None:
        if not condition:
            self.errors.append(message)


def read_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def as_float(value: object) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return float("nan")


def main() -> int:
    checks = Checks()
    try:
        rows = read_csv(RESULTS / "closed_loop_coarse_dynamic_order_probe_rows.csv")
        work_rows = read_csv(RESULTS / "closed_loop_coarse_dynamic_order_probe_work_precision_summary.csv")
        summary = read_json(RESULTS / "closed_loop_coarse_dynamic_order_probe.json")
        report = (RESULTS / "closed_loop_coarse_dynamic_order_probe.md").read_text(encoding="utf-8")
    except Exception as exc:  # noqa: BLE001 - concise CLI failure.
        print(f"closed-loop coarse dynamic-order probe validation: FAIL\n- {exc}")
        return 1

    checks.check(summary.get("schema") == "closed-loop-coarse-dynamic-order-probe-v1", "schema changed")
    checks.check(summary.get("default_policy") == "coarse_first_no_default_1e-4", "default policy changed")
    checks.check(summary.get("step_sizes") == [0.1, 0.05, 0.025], "coarse step sizes changed")
    checks.check(math.isclose(float(summary.get("reference_h")), 0.0125), "reference h changed")
    checks.check(math.isclose(float(summary.get("t_end")), 0.2), "time horizon changed")
    checks.check(set(summary.get("models", [])) == MODELS, "model set changed")
    checks.check(summary.get("row_count") == 12, "expected 12 raw rows")
    checks.check(summary.get("ok_row_count") == 11, "expected 11 ok raw rows")
    checks.check(summary.get("failed_row_count") == 1, "expected one failed coarse probe row")
    checks.check(summary.get("public_failed_row_count") == 1, "expected one failed public coarse probe row")
    failed_rows = summary.get("failed_rows", [])
    checks.check(
        failed_rows
        == [
            {
                "model": "slider_crank",
                "method": "rA-public-dynamics",
                "h": 0.1,
                "status": "failed:ValueError:array must not contain infs or NaNs",
            }
        ],
        "failed-row detail changed",
    )
    checks.check(summary.get("work_summary_row_count") == 4, "expected four work-summary rows")
    checks.check(summary.get("local_method_count") == 2, "expected two local method summary rows")
    checks.check(summary.get("public_method_count") == 2, "expected two public method summary rows")
    checks.check(summary.get("accepted_dynamic_order_count") == 0, "dynamic order must remain unaccepted")
    checks.check(summary.get("external_superiority_claim") is False, "external superiority must remain false")
    checks.check(summary.get("same_test_campaign_status") == "not_run", "same-test campaign status changed")

    raw_methods = {row.get("method") for row in rows}
    checks.check(raw_methods == {"rA-public-dynamics", "Gauss6/FullVA-local-closed-loop"}, "raw methods changed")
    checks.check({row.get("model") for row in rows} == MODELS, "raw model set changed")
    checks.check(all(row.get("coarse_probe_policy") == "True" for row in rows), "raw rows missing coarse probe flag")
    checks.check(all(row.get("accepted_dynamic_order") == "false" for row in rows), "raw rows promoted dynamic order")
    checks.check(all(row.get("external_superiority_claim_allowed") == "false" for row in rows), "raw rows allow superiority")
    checks.check(all(row.get("default_policy") == "coarse_first_no_default_1e-4" for row in rows), "raw rows lost default policy")

    local_work = [row for row in work_rows if row.get("method") == "Gauss6/FullVA-local-closed-loop"]
    public_work = [row for row in work_rows if row.get("method") == "rA-public-dynamics"]
    checks.check(len(local_work) == 2, "expected two local work rows")
    checks.check(len(public_work) == 2, "expected two public work rows")
    checks.check(all(row.get("coarse_probe_policy") == "True" for row in work_rows), "work rows missing coarse probe flag")
    checks.check(all(row.get("accepted_dynamic_order") == "false" for row in work_rows), "work rows promoted dynamic order")
    checks.check(
        all(row.get("external_superiority_claim_allowed") == "false" for row in work_rows),
        "work rows allow superiority",
    )
    checks.check(
        any(as_float(row.get("finest_runtime_ratio_vs_rA")) > 1.0 for row in local_work),
        "probe should expose local runtime ratio data",
    )
    checks.check("Raw rows: `11/12` ok" in report, "report missing 11/12 ok count")
    checks.check("Failed public rows: `1`" in report, "report missing failed public row count")
    checks.check("array must not contain infs or NaNs" in report, "report missing public failure detail")
    checks.check("accepted dynamic order remains zero" in report, "report missing accepted-order boundary")
    checks.check("does not run default `1e-4` rows" in report, "report missing no-default-1e-4 boundary")
    checks.check("kinematic/reaction rows" in report, "report missing kinematic/reaction caveat")

    if checks.errors:
        print("closed-loop coarse dynamic-order probe validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("closed-loop coarse dynamic-order probe validation: PASS")
    print(f"rows={summary.get('ok_row_count')}/{summary.get('row_count')}")
    print(f"work_summary_rows={summary.get('work_summary_row_count')}")
    print(f"local_velocity_evidence={summary.get('local_velocity_evidence_rows')}/{summary.get('local_method_count')}")
    print(f"local_acceleration_evidence={summary.get('local_acceleration_evidence_rows')}/{summary.get('local_method_count')}")
    print(f"local_position_floor_rows={summary.get('local_position_floor_rows')}/{summary.get('local_method_count')}")
    print(f"accepted_dynamic_order={summary.get('accepted_dynamic_order_count')}")
    print("external_superiority_claim=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
