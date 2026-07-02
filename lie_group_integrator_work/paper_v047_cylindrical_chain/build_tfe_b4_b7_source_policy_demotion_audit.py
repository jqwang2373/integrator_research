#!/usr/bin/env python3
"""Build the TFE B4/B7 source-policy demotion audit.

The audit is read-only. It records why the TFE rows cannot be used as current
B4/B7 source-policy figure evidence, while preserving them as future
source-policy work and as related-work/formal-order context.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
OUT_JSON = PAPER / "TFE_B4_B7_SOURCE_POLICY_DEMOTION_AUDIT.json"
OUT_MD = PAPER / "TFE_B4_B7_SOURCE_POLICY_DEMOTION_AUDIT.md"


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def tfe_matrix_rows(matrix: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        row
        for row in matrix.get("rows", [])
        if isinstance(row, dict)
        and row.get("method") in {
            "tfe2026_Newmark_beta",
            "tfe2026_TFE_m1",
            "tfe2026_TFE_m2",
            "tfe2026_trapezoidal",
        }
    ]


def main() -> None:
    row_audit = read_json(PAPER / "TFE_SOURCE_POLICY_ROW_AUDIT.json")
    model_audit = read_json(PAPER / "TFE_SOURCE_PENDULUM_MODEL_AUDIT.json")
    grid_audit = read_json(PAPER / "TFE_SOURCE_GRID_COMPATIBILITY_AUDIT.json")
    spec = read_json(PAPER / "TFE_SOURCE_POLICY_SPEC.json")
    matrix = read_json(PAPER / "PAPER_NUMERICAL_RESULT_MATRIX.json")

    rows = tfe_matrix_rows(matrix)
    preflight = row_audit.get("source_policy_runner_equivalence_preflight", {})
    source_text_anchor = model_audit.get("brown_mcphee_source_text_anchor", {})
    endpoint_audit = grid_audit.get("source_text_endpoint_convention_audit", {})
    blocker_ids = [item.get("id") for item in preflight.get("open_blockers", []) if isinstance(item, dict)]
    method_count = len({row.get("method") for row in rows})
    example_count = len({row.get("example") for row in rows})
    row_count = len(rows)

    audit: dict[str, Any] = {
        "schema": "tfe-b4-b7-source-policy-demotion-audit-v1",
        "status": "tfe_source_policy_rows_demoted_from_current_b4_b7_figures",
        "read_only": True,
        "source_files": [
            "TFE_SOURCE_POLICY_ROW_AUDIT.json",
            "TFE_SOURCE_PENDULUM_MODEL_AUDIT.json",
            "TFE_SOURCE_GRID_COMPATIBILITY_AUDIT.json",
            "TFE_SOURCE_POLICY_SPEC.json",
            "PAPER_NUMERICAL_RESULT_MATRIX.json",
        ],
        "source_policy_rows_total": row_count,
        "source_policy_method_count": method_count,
        "source_policy_example_count": example_count,
        "source_policy_rows_closed": row_audit.get("source_policy_closed_rows"),
        "source_policy_rows_closed_by_demotion": 0,
        "current_claim_requires_tfe_source_policy_execution": False,
        "demoted_related_work_proxy_rows_for_current_claim": row_count,
        "future_reintroduction_requires_runner_or_code_path_rows": row_count,
        "future_source_policy_work_required": True,
        "source_policy_runner_equivalence_open": preflight.get("can_close_tfe_lane_from_preflight") is False,
        "runner_equivalence_preflight_status": preflight.get("status"),
        "runner_equivalence_closed_precondition_count": preflight.get("closed_precondition_count"),
        "runner_equivalence_open_blocker_count": preflight.get("open_blocker_count"),
        "runner_equivalence_open_blocker_ids": blocker_ids,
        "pendulum_dae_runner_implemented": preflight.get("pendulum_dae_runner_implemented"),
        "tfe_newmark_trapezoidal_source_policy_runners_implemented": preflight.get(
            "tfe_newmark_trapezoidal_source_policy_runners_implemented"
        ),
        "gauss6_fullva_source_policy_runner_implemented": preflight.get(
            "gauss6_fullva_source_policy_runner_implemented"
        ),
        "brown_mcphee_source_code_equivalent_law": preflight.get("brown_mcphee_source_code_equivalent_law"),
        "source_text_defers_brown_mcphee_law_to_refs_38_39": source_text_anchor.get(
            "defers_law_details_to_refs_38_39"
        ),
        "source_grid_policy_resolved_for_full_T10": preflight.get("source_grid_policy_resolved_for_full_T10"),
        "source_grid_endpoint_incompatible_rows": grid_audit.get(
            "endpoint_incompatible_rows_require_source_endpoint_policy"
        ),
        "source_text_endpoint_convention_resolved_for_error_sampling": endpoint_audit.get(
            "source_endpoint_convention_resolved_for_error_sampling"
        ),
        "current_figure_scope_policy": {
            "allowed_now": [
                "TFE formal-order and related-work discussion",
                "candidate same-test or formula-order diagnostics clearly labeled non-source-policy",
            ],
            "forbidden_now": [
                "TFE rows in current B4/B7 source-policy work/precision figures",
                "Gauss6/FullVA beats original TFE source-policy runs",
                "external-superiority claim from TFE source-policy evidence",
            ],
        },
        "b4_can_close_from_tfe_demotion": False,
        "b7_can_close_from_tfe_demotion": False,
        "external_superiority_claim_allowed": spec.get("external_superiority_claim"),
        "heavy_numerical_run_invoked": False,
        "run_v047_invoked": False,
        "v048_runner_invoked": False,
        "demotion_reasons": blocker_ids,
        "source_policy_row_ids": [
            f"{row.get('method')}:{row.get('example')}"
            for row in rows
        ],
    }

    with OUT_JSON.open("w", encoding="utf-8") as handle:
        json.dump(audit, handle, indent=2, sort_keys=True)
        handle.write("\n")

    lines = [
        "# TFE B4/B7 Source-Policy Demotion Audit",
        "",
        "Status: `tfe_source_policy_rows_demoted_from_current_b4_b7_figures`.",
        "",
        "This audit is read-only and does not run numerical experiments.",
        "",
        f"- TFE source-policy rows demoted for current B4/B7 figure scope: `{row_count}/{row_count}`.",
        "- Source-policy rows closed by demotion: `0`.",
        "- Current claim requires TFE source-policy execution: `False`.",
        f"- Future reintroduction requires runner/code-path rows: `{row_count}`.",
        "- B4/B7 can close from this demotion: `False/False`.",
        f"- Runner-equivalence preflight closed/open/source rows: `{audit['runner_equivalence_closed_precondition_count']}/{audit['runner_equivalence_open_blocker_count']}/{audit['source_policy_rows_closed']}`.",
        f"- Brown--McPhee source-code-equivalent law: `{audit['brown_mcphee_source_code_equivalent_law']}`.",
        f"- Source text defers Brown--McPhee law details to Refs. 38--39: `{audit['source_text_defers_brown_mcphee_law_to_refs_38_39']}`.",
        f"- Full T=10 endpoint/output policy resolved: `{audit['source_grid_policy_resolved_for_full_T10']}`.",
        f"- Endpoint-incompatible rows requiring policy: `{audit['source_grid_endpoint_incompatible_rows']}`.",
        f"- Source endpoint convention resolved for error sampling: `{audit['source_text_endpoint_convention_resolved_for_error_sampling']}`.",
        f"- pendulum DAE runner implemented: `{audit['pendulum_dae_runner_implemented']}`.",
        f"- TFE/Newmark/trapezoidal source-policy runners implemented: `{audit['tfe_newmark_trapezoidal_source_policy_runners_implemented']}`.",
        f"- Gauss6 FullVA source-policy runner implemented: `{audit['gauss6_fullva_source_policy_runner_implemented']}`.",
        f"- heavy/run_v047/v048 invoked: `{audit['heavy_numerical_run_invoked']}/{audit['run_v047_invoked']}/{audit['v048_runner_invoked']}`.",
        "",
        "Demotion reasons:",
        "",
    ]
    for reason in blocker_ids:
        lines.append(f"- `{reason}`")
    lines.extend(
        [
            "",
            "Allowed current use is related-work/formal-order context and explicitly labeled diagnostics.",
            "Forbidden current use is a source-policy B4/B7 work/precision figure or external-superiority claim.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("tfe_b4_b7_source_policy_demotion_audit=written")
    print(f"tfe_rows_demoted={row_count}/{row_count}")
    print("source_policy_rows_closed_by_demotion=0")
    print("b4_b7_can_close_from_tfe_demotion=False/False")


if __name__ == "__main__":
    main()
