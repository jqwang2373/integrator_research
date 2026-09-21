#!/usr/bin/env python3
"""Build residual-to-error theorem obligations for closed-loop rows.

This artifact is intentionally not a proof. It records the exact theorem
conditions that would be needed before the selected closed-loop residual rows
could be promoted to accepted dynamic-order evidence.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
OUT_CSV = RESULTS / "closed_loop_residual_to_error_theorem_obligations.csv"
OUT_JSON = RESULTS / "closed_loop_residual_to_error_theorem_obligations.json"
OUT_MD = RESULTS / "closed_loop_residual_to_error_theorem_obligations.md"


def read_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError("refusing to write empty residual-to-error obligation table")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def build_rows(
    surrogate: dict,
    floor: dict,
    coarse: dict,
    feasibility: dict,
    closure: dict,
) -> list[dict[str, object]]:
    return [
        {
            "obligation_id": "R2E-1",
            "obligation": "dynamic residual identity",
            "required_for_acceptance": (
                "The measured residual must be the residual of the same local dynamic DAE trajectory map whose "
                "error is being bounded."
            ),
            "current_evidence": (
                f"local row kind is {feasibility.get('current_local_row_kind')}; "
                f"true dynamic local rows={feasibility.get('true_dynamic_local_rows_available')}"
            ),
            "current_status": "not_satisfied",
            "blocking": "true",
            "next_artifact": "local_closed_loop_dynamic_dae_runner_or_identity_proof",
        },
        {
            "obligation_id": "R2E-2",
            "obligation": "residual consistency rate",
            "required_for_acceptance": "Show the closed-loop residual estimator is O(h^7) on the smooth branch.",
            "current_evidence": (
                f"surrogate rows={surrogate.get('surrogate_available_count')}; "
                f"coarse rows ok={coarse.get('ok_row_count')}/{coarse.get('row_count')}"
            ),
            "current_status": "partial_evidence_not_rate_proof",
            "blocking": "true",
            "next_artifact": "three_step_residual_rate_or_symbolic_defect_proof",
        },
        {
            "obligation_id": "R2E-3",
            "obligation": "stability or inf-sup bound",
            "required_for_acceptance": (
                "Prove a mesh-independent inverse/stability bound converting residual norm to trajectory error "
                "for the closed-loop constrained DAE."
            ),
            "current_evidence": "no stability constant, inf-sup constant, or inverse estimate is recorded",
            "current_status": "missing",
            "blocking": "true",
            "next_artifact": "closed_loop_dae_stability_bound",
        },
        {
            "obligation_id": "R2E-4",
            "obligation": "calibrated error estimator",
            "required_for_acceptance": (
                "Calibrate residual-to-position/velocity/acceleration error constants against a reference not "
                "dominated by floor effects."
            ),
            "current_evidence": (
                f"velocity/acceleration evidence rows={floor.get('velocity_acceleration_evidence_count')}; "
                f"position-floor blockers={floor.get('position_floor_blocker_count')}"
            ),
            "current_status": "partial_but_position_floor_blocked",
            "blocking": "true",
            "next_artifact": "non_floor_limited_estimator_calibration",
        },
        {
            "obligation_id": "R2E-5",
            "obligation": "reference-floor exclusion",
            "required_for_acceptance": (
                "Demonstrate that the position and velocity errors used for order are above reference/roundoff floors."
            ),
            "current_evidence": (
                f"local position-floor rows={coarse.get('local_position_floor_rows')}; "
                f"accepted dynamic order rows={coarse.get('accepted_dynamic_order_count')}"
            ),
            "current_status": "not_satisfied",
            "blocking": "true",
            "next_artifact": "non_floor_limited_closed_loop_error_rows",
        },
        {
            "obligation_id": "R2E-6",
            "obligation": "coarse-first acceptance campaign",
            "required_for_acceptance": (
                "Use h=[0.1,0.05,0.025] with reference_h=0.0125, avoid default 1e-4, and obtain accepted "
                "position/velocity dynamic-order evidence for both closed-loop mechanisms."
            ),
            "current_evidence": (
                f"step_sizes={coarse.get('step_sizes')}; reference_h={coarse.get('reference_h')}; "
                f"public_failed_rows={coarse.get('public_failed_row_count')}"
            ),
            "current_status": "campaign_exists_but_not_accepted",
            "blocking": "true",
            "next_artifact": "accepted_coarse_dynamic_order_rows_or_repaired_public_baseline",
        },
        {
            "obligation_id": "R2E-7",
            "obligation": "manuscript theorem and proof",
            "required_for_acceptance": (
                "State and prove the residual-to-error theorem in the CMAME manuscript, including assumptions, "
                "constants, estimator definition, and limitations."
            ),
            "current_evidence": (
                f"closure paths={closure.get('closure_paths')}; submission_ready={closure.get('submission_ready')}"
            ),
            "current_status": "missing",
            "blocking": "true",
            "next_artifact": "cmame_residual_to_error_theorem_section",
        },
    ]


def write_markdown(summary: dict, rows: list[dict[str, object]]) -> None:
    lines = [
        "# Closed-Loop Residual-to-Error Theorem Obligations",
        "",
        "Status: **open; residual-to-error promotion is not accepted**",
        "",
        f"- Accepted residual-to-error theorem: `{summary['accepted_residual_to_error_theorem']}`.",
        f"- Accepted dynamic-order rows by this route: `{summary['accepted_dynamic_order_count']}`.",
        f"- Blocking obligations: `{summary['blocking_obligation_count']}/{summary['obligation_count']}`.",
        f"- Default policy: `{summary['default_policy']}`.",
        "",
        "This gate prevents the selected residual surrogate from being used as a",
        "dynamic-order proof unless the missing theorem obligations are actually",
        "closed. Small reaction residuals are useful evidence, but they do not by",
        "themselves bound trajectory error or establish order.",
        "",
        "| ID | Obligation | Status | Blocking | Next artifact |",
        "|---|---|---|---:|---|",
    ]
    for row in rows:
        lines.append(
            "| "
            f"`{row['obligation_id']}` | {row['obligation']} | "
            f"`{row['current_status']}` | {row['blocking']} | `{row['next_artifact']}` |"
        )
    lines.extend(
        [
            "",
            "## Acceptance Rule",
            "",
            "The residual-to-error route can close only after all blocking obligations",
            "are satisfied, the estimator is calibrated on non-floor-limited errors,",
            "and the manuscript contains a reviewer-defensible theorem. Until then,",
            "`four_link` and `slider_crank` remain mechanism coverage rows, not",
            "accepted dynamic-order rows.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    surrogate = read_json(RESULTS / "closed_loop_surrogate_dynamic_gate.json")
    floor = read_json(RESULTS / "closed_loop_dynamic_error_floor_audit.json")
    coarse = read_json(RESULTS / "closed_loop_coarse_dynamic_order_probe.json")
    feasibility = read_json(RESULTS / "closed_loop_true_dynamic_row_feasibility_audit.json")
    closure = read_json(RESULTS / "closed_loop_dynamic_order_closure_contract.json")
    rows = build_rows(surrogate, floor, coarse, feasibility, closure)
    blocking_count = sum(1 for row in rows if row["blocking"] == "true")
    status_counts: dict[str, int] = {}
    for row in rows:
        status = str(row["current_status"])
        status_counts[status] = status_counts.get(status, 0) + 1
    summary = {
        "schema": "closed-loop-residual-to-error-theorem-obligations-v1",
        "default_policy": "coarse_first_no_default_1e-4",
        "models": ["four_link", "slider_crank"],
        "obligation_count": len(rows),
        "blocking_obligation_count": blocking_count,
        "status_counts": status_counts,
        "accepted_residual_to_error_theorem": False,
        "accepted_dynamic_order_count": 0,
        "true_dynamic_local_rows_available": feasibility.get("true_dynamic_local_rows_available"),
        "current_local_row_kind": feasibility.get("current_local_row_kind"),
        "position_floor_blocker_count": floor.get("position_floor_blocker_count"),
        "local_velocity_evidence_rows": coarse.get("local_velocity_evidence_rows"),
        "local_acceleration_evidence_rows": coarse.get("local_acceleration_evidence_rows"),
        "strict_public_policy_1e-4_required": False,
        "external_superiority_claim": False,
        "submission_ready": False,
        "required_next_artifacts": [row["next_artifact"] for row in rows if row["blocking"] == "true"],
        "interpretation": (
            "The residual-to-error proof route is not closed. Current artifacts provide useful surrogate "
            "and floor diagnostics, but they do not prove a residual-to-trajectory-error bound and do not "
            "promote four_link/slider_crank to accepted dynamic-order rows."
        ),
    }
    write_csv(OUT_CSV, rows)
    with OUT_JSON.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, sort_keys=True)
        handle.write("\n")
    write_markdown(summary, rows)
    print("closed_loop_residual_to_error_theorem_obligations=written")
    print(f"obligations={len(rows)}")
    print(f"blocking_obligations={blocking_count}")
    print("accepted_residual_to_error_theorem=False")
    print("accepted_dynamic_order=0")
    print("default_1e-4=False")
    print("external_superiority_claim=False")


if __name__ == "__main__":
    main()
