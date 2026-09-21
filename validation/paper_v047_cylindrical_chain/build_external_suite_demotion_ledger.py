#!/usr/bin/env python3
"""Build an explicit demotion ledger for external suites.

This ledger records source-policy suites that are deliberately excluded from
external-superiority claims.  It does not run numerical experiments.
"""

from __future__ import annotations

import json
from pathlib import Path


PAPER = Path(__file__).resolve().parent
OUT_JSON = PAPER / "EXTERNAL_SUITE_DEMOTION_LEDGER.json"
OUT_MD = PAPER / "EXTERNAL_SUITE_DEMOTION_LEDGER.md"


def read_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def main() -> None:
    vp = read_json(PAPER / "VP2024_CODE_PATH_DISPOSITION_AUDIT.json")
    hi = read_json(PAPER / "HI2022_SOURCE_POLICY_ROW_AUDIT.json")
    hi_repair = read_json(PAPER / "HI2022_T8_TOLERANCE_REPAIR_AUDIT.json")
    ra = read_json(PAPER / "RA2021_SOURCE_POLICY_ROW_AUDIT.json")
    tfe = read_json(PAPER / "TFE_SOURCE_POLICY_ROW_AUDIT.json")
    source_policy = read_json(PAPER / "ALL_EXAMPLES_SOURCE_POLICY_AUDIT.json")
    blocker = read_json(PAPER / "CMAME_BLOCKER_CLOSURE_GATE.json")

    vp_coverage = vp.get("coverage", {})
    vp_disposition = vp.get("source_code_path_disposition", {})
    flagged_by_suite = source_policy.get("coverage", {}).get("flagged_by_suite", {})
    original_b2_required = next(
        row.get("required_to_close", [])
        for row in blocker.get("blockers", [])
        if row.get("id") == "B2"
    )
    closed_subrequirements = [
        "vp2024_code_resolution_or_demotion",
        "hi2022_public_code_same_test_rows",
        "ra2021_public_code_same_test_rows",
        "original_tfe_pendulum_error_order_work_rows",
    ]
    remaining_b2_required = [
        item for item in original_b2_required if item not in closed_subrequirements
    ]
    demoted_flagged_rows = (
        flagged_by_suite.get("vp2024_velocity_partitioning", 0)
        + flagged_by_suite.get("hi2022_half_implicit", 0)
        + flagged_by_suite.get("ra2021_absolute_coordinate", 0)
        + flagged_by_suite.get("tfe2026_original_pendulum", 0)
    )
    vp_source_policy_rows = vp_coverage.get("source_policy_rows", 0)
    hi_source_policy_rows = flagged_by_suite.get("hi2022_half_implicit", 0)
    ra_source_policy_rows = flagged_by_suite.get("ra2021_absolute_coordinate", 0)
    tfe_source_policy_rows = flagged_by_suite.get("tfe2026_original_pendulum", 0)
    demoted_source_policy_rows = (
        vp_source_policy_rows
        + hi_source_policy_rows
        + ra_source_policy_rows
        + tfe_source_policy_rows
    )

    result = {
        "schema": "external-suite-demotion-ledger-v1",
        "status": "all_external_suites_demoted_from_external_superiority_scope",
        "submission_ready": False,
        "external_superiority_claim_allowed": False,
        "source_policy_external_superiority_allowed": False,
        "b2_subrequirements_closed_by_demotion": closed_subrequirements,
        "b2_required_to_close_after_demotions": remaining_b2_required,
        "demoted_suite_count": 4,
        "demoted_source_policy_flagged_rows": demoted_flagged_rows,
        "demoted_source_policy_rows": demoted_source_policy_rows,
        "vp2024_demoted_source_policy_rows": vp_source_policy_rows,
        "vp2024_demoted_source_policy_flagged_rows": flagged_by_suite.get("vp2024_velocity_partitioning", 0),
        "hi2022_demoted_source_policy_rows": hi_source_policy_rows,
        "hi2022_demoted_source_policy_flagged_rows": flagged_by_suite.get("hi2022_half_implicit", 0),
        "ra2021_demoted_source_policy_rows": ra_source_policy_rows,
        "ra2021_demoted_source_policy_flagged_rows": flagged_by_suite.get("ra2021_absolute_coordinate", 0),
        "tfe2026_demoted_source_policy_rows": tfe_source_policy_rows,
        "tfe2026_demoted_source_policy_flagged_rows": flagged_by_suite.get("tfe2026_original_pendulum", 0),
        "active_source_policy_flagged_rows_after_demotions": (
            source_policy.get("coverage", {}).get("flagged_row_count", 0)
            - demoted_flagged_rows
        ),
        "demoted_suites": [
            {
                "suite_id": "vp2024_velocity_partitioning",
                "decision": "attempted_not_reproducible_not_promoted_keep_proxy_diagnostic",
                "reason": (
                    "No distinct public velocity-partitioning code path is resolved; "
                    "the available proxy reconstruction is not source-policy equivalent; "
                    "the coordinate-partitioning proxy is retained only as a bounded "
                    "common-reference diagnostic."
                ),
                "examples_checked": vp_coverage.get("examples_checked"),
                "source_policy_rows": vp_coverage.get("source_policy_rows"),
                "source_policy_code_path_unresolved_rows": vp_coverage.get(
                    "source_policy_code_path_unresolved_rows"
                ),
                "self_reproduction_attempted_rows": vp_coverage.get(
                    "source_policy_rows_attempted_not_reproducible"
                ),
                "unable_to_reproduce_rows": vp_coverage.get("unable_to_reproduce_rows"),
                "final_nonpublic_code_disposition": vp_disposition.get(
                    "final_nonpublic_code_disposition"
                ),
                "source_policy_flagged_rows": flagged_by_suite.get("vp2024_velocity_partitioning", 0),
                "distinct_public_code_path_found": vp_disposition.get(
                    "distinct_public_vp_code_path_found"
                ),
                "proxy_is_source_policy_reproduction": vp_disposition.get(
                    "coordinate_partitioning_proxy_is_source_policy_reproduction"
                ),
                "claim_allowed_now": vp_disposition.get("claim_allowed_now"),
                "accepted_for_external_superiority": vp_disposition.get(
                    "accepted_for_external_superiority"
                ),
                "common_reference_proxy_retained": True,
            },
            {
                "suite_id": "hi2022_half_implicit",
                "decision": "explicitly_demoted_after_incomplete_full_T8_source_policy_evidence",
                "reason": (
                    "The bounded T=0.1 rows remain useful diagnostics, but the recorded T=8 "
                    "coarse and tolerance-repair evidence does not complete the source-policy "
                    "form/model groups; therefore HI2022 is excluded from external-superiority claims."
                ),
                "source_policy_rows": hi_source_policy_rows,
                "source_policy_flagged_rows": flagged_by_suite.get("hi2022_half_implicit", 0),
                "bounded_T0p1_rows_ok": hi.get("bounded_ok_row_count"),
                "bounded_T0p1_rows": hi.get("bounded_row_count"),
                "t8_coarse_ok_rows": hi.get("t8_coarse_horizon_evidence", {}).get("ok_row_count"),
                "t8_coarse_rows": hi.get("t8_coarse_horizon_evidence", {}).get("row_count"),
                "t8_coarse_complete_groups": hi.get("t8_coarse_horizon_evidence", {}).get(
                    "complete_form_model_groups"
                ),
                "t8_coarse_group_count": hi.get("t8_coarse_horizon_evidence", {}).get("group_count"),
                "t8_tolerance_repair_combined_best_complete_groups": hi_repair.get("combined_best", {}).get(
                    "complete_form_model_groups"
                ),
                "t8_tolerance_repair_combined_best_group_count": hi_repair.get("combined_best", {}).get(
                    "group_count"
                ),
                "source_policy_reproduction_closed": hi.get("source_policy_reproduction_closed"),
                "accepted_for_external_superiority": hi.get("accepted_for_external_superiority"),
                "claim_allowed_now": "demoted_incomplete_full_T8_source_policy_related_work_only",
                "bounded_common_reference_retained": True,
            },
            {
                "suite_id": "ra2021_absolute_coordinate",
                "decision": "route_b_demoted_keep_public_baseline_and_common_reference_diagnostics",
                "reason": (
                    "The RA2021 public order and timing diagnostics remain useful, but the "
                    "local Gauss6/FullVA rows are not promoted to same-source-policy dynamic "
                    "order rows; therefore RA2021 is excluded from external-superiority claims."
                ),
                "source_policy_rows": ra_source_policy_rows,
                "source_policy_flagged_rows": flagged_by_suite.get("ra2021_absolute_coordinate", 0),
                "public_order_groups_completed": ra.get("public_order_groups_completed"),
                "public_order_groups_required": ra.get("public_order_groups_required"),
                "public_timing_rows_completed": ra.get("public_timing_rows_completed"),
                "public_timing_rows_required": ra.get("public_timing_rows_required"),
                "source_policy_reproduction_rows": ra.get("source_policy_reproduction_rows"),
                "external_superiority_ready_rows": ra.get("external_superiority_ready_rows"),
                "source_policy_reproduction_closed": False,
                "accepted_for_external_superiority": False,
                "claim_allowed_now": "route_b_demoted_related_work_and_diagnostics_only",
                "bounded_common_reference_retained": True,
            },
            {
                "suite_id": "tfe2026_original_pendulum",
                "decision": "route_b_demoted_keep_formula_comparator_and_candidate_diagnostics",
                "reason": (
                    "The TFE source-pendulum scaffold and formula-order comparator remain in "
                    "the manuscript, but the source-equivalent DAE/friction/method runner is "
                    "not completed; therefore TFE is excluded from external-superiority claims."
                ),
                "source_policy_rows": tfe_source_policy_rows,
                "source_policy_flagged_rows": flagged_by_suite.get("tfe2026_original_pendulum", 0),
                "source_policy_rows_completed": tfe.get("source_policy_rows_completed"),
                "external_superiority_ready_rows": tfe.get("external_superiority_ready_rows"),
                "pendulum_dae_runner_implemented": tfe.get("pendulum_dae_runner_implemented"),
                "source_policy_dae_runner_equivalent": tfe.get("source_policy_dae_runner_equivalent"),
                "source_policy_method_runner_equivalent": tfe.get("source_policy_method_runner_equivalent"),
                "source_reference_h": tfe.get("source_reference_h"),
                "candidate_full_T10_probe_implemented": tfe.get(
                    "active_tfe_b2_full_T10_coarse_candidate_probe_implemented"
                ),
                "candidate_full_T10_probe_source_policy_rows": tfe.get(
                    "active_tfe_b2_full_T10_coarse_candidate_probe_source_policy_rows_completed"
                ),
                "source_policy_reproduction_closed": False,
                "accepted_for_external_superiority": False,
                "claim_allowed_now": "route_b_demoted_formal_comparator_and_diagnostics_only",
                "formal_order_comparator_retained": True,
            },
        ],
        "remaining_open_suites": [],
        "execution_policy": {
            "read_only_existing_artifacts": True,
            "default_1e_4_required": False,
            "heavy_numerical_run_invoked": False,
            "run_v047_invoked": False,
            "v048_runner_invoked": False,
        },
        "source_files": {
            "vp2024_code_path_disposition": "VP2024_CODE_PATH_DISPOSITION_AUDIT.json",
            "hi2022_source_policy_row_audit": "HI2022_SOURCE_POLICY_ROW_AUDIT.json",
            "hi2022_t8_tolerance_repair_audit": "HI2022_T8_TOLERANCE_REPAIR_AUDIT.json",
            "ra2021_source_policy_row_audit": "RA2021_SOURCE_POLICY_ROW_AUDIT.json",
            "tfe_source_policy_row_audit": "TFE_SOURCE_POLICY_ROW_AUDIT.json",
            "all_examples_source_policy": "ALL_EXAMPLES_SOURCE_POLICY_AUDIT.json",
            "blocker_gate": "CMAME_BLOCKER_CLOSURE_GATE.json",
        },
    }

    with OUT_JSON.open("w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, sort_keys=True)
        handle.write("\n")

    lines = [
        "# External Suite Demotion Ledger",
        "",
        "Status: **all external source-policy suites explicitly demoted from external-superiority scope**.",
        "",
        f"- Demoted suites: `{result['demoted_suite_count']}`.",
        f"- B2 subrequirements closed by demotion: `{', '.join(closed_subrequirements)}`.",
        f"- Remaining B2 required items: `{', '.join(remaining_b2_required) if remaining_b2_required else 'none'}`.",
        f"- Demoted source-policy rows: `{result['demoted_source_policy_rows']}`.",
        f"- Demoted flagged rows: `{result['demoted_source_policy_flagged_rows']}`.",
        f"- Demoted VP2024 source-policy rows/flagged rows: `{result['vp2024_demoted_source_policy_rows']}/{result['vp2024_demoted_source_policy_flagged_rows']}`.",
        f"- VP2024 attempted/unable/final disposition: `{vp_coverage.get('source_policy_rows_attempted_not_reproducible')}/{vp_coverage.get('unable_to_reproduce_rows')}/{vp_disposition.get('final_nonpublic_code_disposition')}`.",
        f"- Demoted HI2022 source-policy rows/flagged rows: `{result['hi2022_demoted_source_policy_rows']}/{result['hi2022_demoted_source_policy_flagged_rows']}`.",
        f"- Demoted RA2021 source-policy rows/flagged rows: `{result['ra2021_demoted_source_policy_rows']}/{result['ra2021_demoted_source_policy_flagged_rows']}`.",
        f"- Demoted TFE source-policy rows/flagged rows: `{result['tfe2026_demoted_source_policy_rows']}/{result['tfe2026_demoted_source_policy_flagged_rows']}`.",
        f"- Active source-policy flagged rows after demotions: `{result['active_source_policy_flagged_rows_after_demotions']}`.",
        f"- External-superiority claim allowed: `{result['external_superiority_claim_allowed']}`.",
        f"- Default `1e-4` required: `{result['execution_policy']['default_1e_4_required']}`.",
        f"- Heavy numerical run invoked: `{result['execution_policy']['heavy_numerical_run_invoked']}`.",
        "",
        "## Demoted Suites",
        "",
        "| suite | decision | rows | flagged rows | demotion evidence | claim allowed now |",
        "|---|---|---:|---:|---|---|",
    ]
    for suite in result["demoted_suites"]:
        if suite["suite_id"] == "vp2024_velocity_partitioning":
            evidence = (
                f"distinct code path `{suite['distinct_public_code_path_found']}`, "
                f"attempted/unable `{suite['self_reproduction_attempted_rows']}/"
                f"{suite['unable_to_reproduce_rows']}`, final "
                f"`{suite['final_nonpublic_code_disposition']}`"
            )
        elif suite["suite_id"] == "hi2022_half_implicit":
            evidence = (
                f"T=8 complete groups `{suite['t8_coarse_complete_groups']}/"
                f"{suite['t8_coarse_group_count']}`, repair combined "
                f"`{suite['t8_tolerance_repair_combined_best_complete_groups']}/"
                f"{suite['t8_tolerance_repair_combined_best_group_count']}`"
            )
        elif suite["suite_id"] == "ra2021_absolute_coordinate":
            evidence = (
                f"public order/timing `{suite['public_order_groups_completed']}/"
                f"{suite['public_order_groups_required']}` and "
                f"`{suite['public_timing_rows_completed']}/{suite['public_timing_rows_required']}`; "
                f"source-policy rows `{suite['source_policy_reproduction_rows']}`"
            )
        else:
            evidence = (
                f"runner `{suite['pendulum_dae_runner_implemented']}`, source-policy rows "
                f"`{suite['source_policy_rows_completed']}`, candidate rows "
                f"`{suite['candidate_full_T10_probe_source_policy_rows']}`"
            )
        lines.append(
            "| "
            f"`{suite['suite_id']}` | `{suite['decision']}` | `{suite['source_policy_rows']}` | "
            f"`{suite['source_policy_flagged_rows']}` | {evidence} | `{suite['claim_allowed_now']}` |"
        )
    lines.extend([
        "",
        "These demotions are claim-boundary decisions, not numerical wins.  VP2024 proxy rows, HI2022 bounded/T=8 diagnostic rows, RA2021 public diagnostics, and TFE formula/candidate diagnostics remain available only inside bounded diagnostic or formal-comparator tables.",
    ])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("external_suite_demotion_ledger=written")
    print("demoted_suites=4")
    print("vp2024_demoted=True")
    print("hi2022_demoted=True")
    print("ra2021_demoted=True")
    print("tfe2026_demoted=True")
    print(f"remaining_b2_required={len(remaining_b2_required)}")
    print("default_1e-4_required=False")
    print("run_v047_invoked=False")


if __name__ == "__main__":
    main()
