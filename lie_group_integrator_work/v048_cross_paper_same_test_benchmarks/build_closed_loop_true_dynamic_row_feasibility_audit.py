#!/usr/bin/env python3
"""Build the closed-loop true-dynamic-row feasibility audit.

This is a read-only source and artifact audit. It does not run any mechanism
simulation. Its purpose is to make the remaining four_link/slider_crank order
gap explicit: current local rows are kinematic solves plus reaction
reconstruction, while accepted dynamic-order evidence needs either true local
dynamic trajectory rows or a residual-to-error theorem.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
WORK_ROOT = HERE.parent
RESULTS = HERE / "results"
V047_RUN = WORK_ROOT / "v047_cylindrical_chain_pipeline" / "run_v047.py"
V048_RUN = HERE / "run_v048.py"
MODELS = ("four_link", "slider_crank")
OUT_CSV = RESULTS / "closed_loop_true_dynamic_row_feasibility_audit.csv"
OUT_JSON = RESULTS / "closed_loop_true_dynamic_row_feasibility_audit.json"
OUT_MD = RESULTS / "closed_loop_true_dynamic_row_feasibility_audit.md"


def read_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError("refusing to write empty feasibility audit")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def source_checks(v047_source: str, v048_source: str) -> dict[str, bool]:
    return {
        "v048_closed_loop_runner_uses_local_kinematic_fullva": (
            "run_gauss6_fullva_closed_loop_external_rows" in v048_source
            and "simulate_v046_local_kinematic_fullva" in v048_source
        ),
        "v047_local_runner_setup_mode_is_kinematics": (
            'v046.setup_system(model, "kinematics", h, t_final, tol)' in v047_source
        ),
        "v047_local_runner_reconstructs_reactions_after_kinematics": (
            "reconstruct_v046_reaction_dynamics(system, float(t))" in v047_source
        ),
        "v048_public_baseline_uses_public_dynamics": (
            'run_public_model(public_model, "rA", "dynamics", h, config.t_end, tol=None)' in v048_source
        ),
        "local_dynamic_fullva_runner_exists": (
            "simulate_v046_local_dynamic_fullva" in v047_source
            or "simulate_v046_local_dynamic_fullva" in v048_source
        ),
        "local_setup_system_dynamics_path_exists": (
            'setup_system(model, "dynamics"' in v047_source
            or 'setup_system(model, "dynamics"' in v048_source
        ),
    }


def build_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for model in MODELS:
        rows.append(
            {
                "model": model,
                "current_local_runner": "simulate_v046_local_kinematic_fullva",
                "current_local_setup_mode": "kinematics",
                "current_local_trajectory_kind": "time-node kinematic constraint solve",
                "current_multiplier_policy": "reaction multipliers reconstructed after the kinematic solve",
                "current_public_baseline": "rA_public_dynamics",
                "true_dynamic_local_row_available": "false",
                "accepted_dynamic_order": "false",
                "why_current_rows_do_not_close_order": (
                    "current local rows solve Phi/Phi_q qdot/Phi_q qdd at output times and then "
                    "reconstruct Newton-Euler reactions; the multiplier dynamics residual is not solved "
                    "inside a local Gauss6/FullVA dynamic trajectory step"
                ),
                "required_unknown_blocks": (
                    "stage/end-point positions, orientations, velocities, accelerations, and Lagrange multipliers"
                ),
                "required_residual_blocks": (
                    "Phi, Phi_q qdot-nu, Phi_q qddot-gamma, SO3 constraints, Newton-Euler force/moment balance, "
                    "and Gauss6/FullVA endpoint/stage collocation equations in one nonlinear solve"
                ),
                "accepted_order_campaign": (
                    "coarse nested h=[0.1,0.05,0.025] plus reference_h=0.0125; position and velocity errors "
                    "must be non-floor-limited and consistent with theorem order six"
                ),
                "alternative_acceptance_path": (
                    "residual-to-error theorem with calibrated estimator for the closed-loop rows"
                ),
                "default_policy": "coarse_first_no_default_1e-4",
                "strict_public_policy_1e-4_required": "false",
                "external_superiority_claim_allowed": "false",
            }
        )
    return rows


def write_markdown(summary: dict, rows: list[dict[str, object]]) -> None:
    lines = [
        "# Closed-Loop True-Dynamic-Row Feasibility Audit",
        "",
        "Status: **open; true local dynamic trajectory rows are not implemented**",
        "",
        f"- Local dynamic rows available: `{summary['true_dynamic_local_rows_available']}`.",
        f"- Accepted dynamic-order rows in this audit: `{summary['accepted_dynamic_order_count']}`.",
        f"- Default execution policy: `{summary['default_policy']}`.",
        f"- Strict public `1e-4` required: `{summary['strict_public_policy_1e-4_required']}`.",
        "",
        "## Source Finding",
        "",
        "The current v048 closed-loop local path calls",
        "`simulate_v046_local_kinematic_fullva`. In v047 that function calls",
        "`setup_system(..., \"kinematics\", ...)`, solves the driven constraints at",
        "output times, and reconstructs reaction multipliers afterward. That is",
        "valid coverage and residual evidence, but it is not a local dynamic DAE",
        "trajectory integrator.",
        "",
        "| Model | Current local row | True dynamic row | Required next implementation |",
        "|---|---|---:|---|",
    ]
    for row in rows:
        lines.append(
            "| "
            f"`{row['model']}` | `{row['current_local_runner']}` / `{row['current_local_setup_mode']}` | "
            f"{row['true_dynamic_local_row_available']} | local dynamic DAE Gauss6/FullVA solve or residual-to-error theorem |"
        )
    lines.extend(
        [
            "",
            "## Required Dynamic Row",
            "",
            "A reviewer-defensible true dynamic row would solve one nonlinear system",
            "containing positions, orientations, velocities, accelerations, and",
            "multipliers, with `Phi`, velocity constraints, acceleration",
            "constraints, SO(3) constraints, Newton-Euler balance, and Gauss6/FullVA",
            "stage/endpoint collocation coupled in the same step. Only then can the",
            "closed-loop `four_link` and `slider_crank` rows be interpreted as",
            "dynamic trajectory order rows.",
            "",
            "No default `1e-4` run is part of this closure path. The next executable",
            "test remains coarse-first: `h=[0.1,0.05,0.025]`,",
            "`reference_h=0.0125`, with non-floor-limited position and velocity",
            "orders consistent with order six.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    closure = read_json(RESULTS / "closed_loop_dynamic_order_closure_contract.json")
    coarse_probe = read_json(RESULTS / "closed_loop_coarse_dynamic_order_probe.json")
    v047_source = V047_RUN.read_text(encoding="utf-8")
    v048_source = V048_RUN.read_text(encoding="utf-8")
    checks = source_checks(v047_source, v048_source)
    rows = build_rows()
    summary = {
        "schema": "closed-loop-true-dynamic-row-feasibility-audit-v1",
        "default_policy": "coarse_first_no_default_1e-4",
        "models": list(MODELS),
        "row_count": len(rows),
        "true_dynamic_local_rows_available": 0,
        "accepted_dynamic_order_count": 0,
        "current_local_row_kind": "kinematic_fullva_plus_reaction_reconstruction",
        "current_local_setup_mode": "kinematics",
        "current_public_baseline_kind": "rA_public_dynamics",
        "source_identity_checks": checks,
        "missing_dynamic_order_models": closure.get("missing_dynamic_order_models"),
        "coarse_step_sizes": coarse_probe.get("step_sizes"),
        "reference_h": coarse_probe.get("reference_h"),
        "method_order_theorem": {
            "accepted_method": "Gauss6/FullVA",
            "global_order": 6,
            "applies_to": "true smooth dynamic trajectory row, not kinematic/reaction replay",
        },
        "required_next_implementation": (
            "local_closed_loop_dynamic_dae_gauss6_fullva_runner_or_residual_to_error_theorem"
        ),
        "strict_public_policy_1e-4_required": False,
        "external_superiority_claim": False,
        "submission_ready": False,
        "interpretation": (
            "The current source and artifacts prove that four_link/slider_crank local rows are "
            "kinematic/reaction rows. They should not be counted as accepted dynamic order rows "
            "until a true dynamic DAE trajectory row or residual-to-error theorem is added."
        ),
    }
    write_csv(OUT_CSV, rows)
    with OUT_JSON.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, sort_keys=True)
        handle.write("\n")
    write_markdown(summary, rows)
    print("closed_loop_true_dynamic_row_feasibility_audit=written")
    print("true_dynamic_local_rows=0")
    print("accepted_dynamic_order=0")
    print("local_row_kind=kinematic_fullva_plus_reaction_reconstruction")
    print("required_next=local_dynamic_dae_runner_or_residual_to_error_theorem")
    print("default_1e-4=False")
    print("external_superiority_claim=False")


if __name__ == "__main__":
    main()
