#!/usr/bin/env python3
"""Validate the 2026-06-21 OC6 external source-artifact recheck."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
AUDIT_JSON = PAPER / "OC6_EXTERNAL_SOURCE_ARTIFACT_RECHECK_20260621.json"
AUDIT_MD = PAPER / "OC6_EXTERNAL_SOURCE_ARTIFACT_RECHECK_20260621.md"


class Checks:
    def __init__(self) -> None:
        self.errors: list[str] = []

    def check(self, condition: bool, message: str) -> None:
        if not condition:
            self.errors.append(message)


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def main() -> int:
    checks = Checks()
    try:
        audit = read_json(AUDIT_JSON)
        text = AUDIT_MD.read_text(encoding="utf-8", errors="replace")
        public_refresh = read_json(PAPER / "SOURCE_POLICY_PUBLIC_CODE_REFRESH_20260620.json")
        oc6_readiness = read_json(PAPER / "OC6_SOURCE_EQUIVALENT_REOPEN_READINESS_AUDIT_20260620.json")
    except Exception as exc:  # noqa: BLE001
        print(f"OC6 external source-artifact recheck 20260621 validation: FAIL\n- {exc}")
        return 1

    rows = [row for row in audit.get("rows", []) if isinstance(row, dict)]
    by_suite = {
        suite: [row for row in rows if row.get("suite_id") == suite]
        for suite in ["tfe2026_original_pendulum", "vp2024_velocity_partitioning"]
    }
    flags = audit.get("forbidden_execution_flags", {})
    policy = audit.get("evidence_policy", {})

    checks.check(audit.get("schema") == "oc6-external-source-artifact-recheck-20260621-v1", "schema changed")
    checks.check(
        audit.get("status") == "no_positive_external_source_artifact_found_reopen_conditions_remain_open",
        "status changed",
    )
    checks.check(audit.get("date_checked") == "2026-06-21", "date changed")
    checks.check(audit.get("read_only") is True, "audit must remain read-only")
    checks.check(audit.get("query_count") == 10, "query count changed")
    checks.check(len(rows) == audit.get("query_count") == 10, "row count changed")
    checks.check(audit.get("suite_count") == 2, "suite count changed")
    checks.check(len(by_suite["tfe2026_original_pendulum"]) == 5, "TFE query count changed")
    checks.check(len(by_suite["vp2024_velocity_partitioning"]) == 5, "VP query count changed")
    checks.check(
        audit.get("prior_latest_external_probe_marker") == public_refresh.get("latest_external_probe_marker"),
        "prior marker mismatch",
    )
    checks.check(
        audit.get("prior_oc6_readiness_status") == oc6_readiness.get("status"),
        "OC6 readiness status mismatch",
    )
    checks.check(audit.get("positive_public_code_artifact_rows") == 0, "positive artifact rows changed")
    checks.check(audit.get("source_code_equivalent_artifact_rows") == 0, "source-equivalent rows changed")
    checks.check(audit.get("source_policy_rows_closed_by_recheck") == 0, "recheck overclosed source-policy rows")
    checks.check(audit.get("source_policy_reopen_triggered") is False, "recheck triggered reopen unexpectedly")
    checks.check(audit.get("source_policy_closed") is False, "audit overclosed source policy")
    checks.check(audit.get("submission_ready") is False, "audit overclaims submission readiness")
    checks.check(audit.get("global_absence_proved") is False, "audit overproved global absence")
    checks.check(
        all(row.get("positive_public_code_artifact_found") is False for row in rows),
        "row overclaims positive artifact",
    )
    checks.check(
        all(row.get("source_code_equivalent_artifact_found") is False for row in rows),
        "row overclaims source-equivalent artifact",
    )
    checks.check(
        all(int(row.get("source_policy_rows_closed_by_recheck") or 0) == 0 for row in rows),
        "row closed source-policy rows",
    )
    checks.check(
        all(row.get("source_policy_reopen_triggered") is False for row in rows),
        "row triggered reopen",
    )
    checks.check(
        all(row.get("accepted_use") == "reopen_monitoring_only_not_source_policy_evidence" for row in rows),
        "row accepted-use boundary changed",
    )
    checks.check(
        any("10.1007/s11044-026-10153-w" in str(row.get("query")) for row in rows),
        "DOI query missing",
    )
    checks.check(
        any("DETC2023-116950" in str(row.get("query")) for row in rows),
        "DETC query missing",
    )
    checks.check(
        any(row.get("non_source_result_example") == "https://arxiv.org/abs/1112.6037" for row in rows),
        "TFE unrelated-result boundary missing",
    )
    checks.check(
        any(row.get("non_source_result_example") == "https://arxiv.org/abs/1205.6697" for row in rows),
        "VP unrelated-result boundary missing",
    )
    checks.check(
        policy.get("browser_search_absence_is_global_absence_proof") is False,
        "search absence overclaimed",
    )
    checks.check(
        policy.get("unrelated_publication_refs_are_source_code_artifacts") is False,
        "unrelated refs overclaimed",
    )
    checks.check(
        policy.get("not_reproducible_rows_are_source_policy_closed") is False,
        "not-reproducible rows overclosed",
    )
    checks.check(
        audit.get("reopen_conditions", {}).get("tfe2026_original_pendulum")
        == "new_public_or_source_code_equivalent_tfe_implementation_artifact",
        "TFE reopen condition changed",
    )
    checks.check(
        audit.get("reopen_conditions", {}).get("vp2024_velocity_partitioning")
        == "new_distinct_public_vp2024_velocity_partitioning_code_path",
        "VP reopen condition changed",
    )
    for key in [
        "source_policy_execution_invoked",
        "heavy_numerical_run_invoked",
        "run_v047_invoked",
        "v048_runner_invoked",
    ]:
        checks.check(flags.get(key) is False, f"{key} changed")

    for token in [
        "Status: `no_positive_external_source_artifact_found_reopen_conditions_remain_open`.",
        "Query count: `10`.",
        "Positive public-code artifact rows: `0`.",
        "Source-code-equivalent artifact rows: `0`.",
        "Source-policy rows closed by recheck: `0`.",
        "Source-policy reopen triggered: `False`.",
        "Global absence proved: `False`.",
        "OC6 remains open until a public/source-code-equivalent TFE artifact or distinct VP2024 code path appears.",
    ]:
        checks.check(token in text, f"markdown missing token: {token}")

    if checks.errors:
        print("OC6 external source-artifact recheck 20260621 validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("OC6 external source-artifact recheck 20260621 validation: PASS")
    print("queries=10")
    print("positive_public_code_artifact_rows=0")
    print("source_code_equivalent_artifact_rows=0")
    print("source_policy_rows_closed_by_recheck=0")
    print("source_policy_reopen_triggered=False")
    print("global_absence_proved=False")
    print("submission_ready=False")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
