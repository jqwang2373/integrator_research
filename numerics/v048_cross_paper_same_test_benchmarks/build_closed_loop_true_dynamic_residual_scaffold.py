#!/usr/bin/env python3
"""Build the closed-loop true-dynamic residual scaffold contract.

This artifact turns the verified public/v046 dynamics interface into a concrete
Gauss6/FullVA residual layout. It does not evaluate a residual or advance a
trajectory; it fixes the square unknown/residual dimensions and implementation
symbols required for the next local dynamic runner.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
MODELS = ("four_link", "slider_crank")
N_STAGES = 3
OUT_CSV = RESULTS / "closed_loop_true_dynamic_residual_scaffold.csv"
OUT_JSON = RESULTS / "closed_loop_true_dynamic_residual_scaffold.json"
OUT_MD = RESULTS / "closed_loop_true_dynamic_residual_scaffold.md"


def read_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError("refusing to write empty residual scaffold")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def scaffold_rows(interface_rows: list[dict]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for model in MODELS:
        dyn = next(
            row for row in interface_rows
            if row.get("model") == model and row.get("setup_mode") == "dynamics"
        )
        nb = int(dyn["body_count"])
        nc = int(dyn["constraint_count"])
        generalized_dim = int(dyn["generalized_dim"])
        lambda_dim = int(dyn["lambda_dim"])
        q_dim = generalized_dim
        v_dim = generalized_dim
        a_dim = generalized_dim
        stage_unknown_dim = q_dim + v_dim + a_dim + lambda_dim
        block_dims = {
            "position_constraints_phi": nc,
            "velocity_constraints_phiq_v_minus_nu": nc,
            "acceleration_constraints_phiq_a_minus_gamma": nc,
            "newton_euler_balance": generalized_dim,
        }
        stage_residual_dim = sum(block_dims.values())
        rows.append(
            {
                "model": model,
                "n_stages": N_STAGES,
                "body_count": nb,
                "constraint_count": nc,
                "generalized_dim": generalized_dim,
                "stage_q_dim": q_dim,
                "stage_v_dim": v_dim,
                "stage_a_dim": a_dim,
                "stage_lambda_dim": lambda_dim,
                "stage_unknown_dim": stage_unknown_dim,
                "total_unknown_dim": N_STAGES * stage_unknown_dim,
                "position_constraint_rows": block_dims["position_constraints_phi"],
                "velocity_constraint_rows": block_dims["velocity_constraints_phiq_v_minus_nu"],
                "acceleration_constraint_rows": block_dims["acceleration_constraints_phiq_a_minus_gamma"],
                "newton_euler_rows": block_dims["newton_euler_balance"],
                "stage_residual_dim": stage_residual_dim,
                "total_residual_dim": N_STAGES * stage_residual_dim,
                "square_stage_system": str(stage_unknown_dim == stage_residual_dim).lower(),
                "square_total_system": str(N_STAGES * stage_unknown_dim == N_STAGES * stage_residual_dim).lower(),
                "fullva_replacement_policy": (
                    "fully constrained closed-loop FullVA: replace all stage q/v collocation rows by "
                    "Phi, Phi_q v-nu, and Phi_q a-gamma; keep Newton-Euler balance with lambda"
                ),
                "endpoint_update_policy": (
                    "advance q/orientation and v/omega by Gauss6 quadrature from solved stage velocities "
                    "and accelerations; then audit endpoint Phi/Phi_q v/Phi_q a residuals"
                ),
                "implementation_symbol": "local_closed_loop_dynamic_dae_gauss6_fullva_runner",
                "accepted_dynamic_order": "false",
                "default_policy": "coarse_first_no_default_1e-4",
                "strict_public_policy_1e-4_required": "false",
            }
        )
    return rows


def read_interface_rows() -> list[dict]:
    with (RESULTS / "closed_loop_true_dynamic_interface_audit.csv").open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_markdown(summary: dict, rows: list[dict[str, object]]) -> None:
    lines = [
        "# Closed-Loop True-Dynamic Residual Scaffold",
        "",
        "Status: **residual layout specified; runner not implemented**",
        "",
        f"- Method: `{summary['method']}`.",
        f"- Gauss stages: `{summary['n_stages']}`.",
        f"- Stage unknown dimension: `{summary['stage_unknown_dim']}`.",
        f"- Total Newton dimension: `{summary['total_unknown_dim']}`.",
        f"- Square system: `{summary['square_total_system']}`.",
        f"- Local runner implemented: `{summary['local_runner_implemented']}`.",
        f"- Accepted dynamic-order rows: `{summary['accepted_dynamic_order_count']}`.",
        f"- Default `1e-4` required: `{summary['default_1e-4_required']}`.",
        "",
        "The scaffold follows the v029 FullVA idea: constrained collocation",
        "components are replaced by position/acceleration consistency rows, with",
        "velocity/acceleration consistency enforced explicitly at each stage. In",
        "these fully constrained driven closed loops, every generalized component",
        "is constrained, so each stage solves for `q`, `v`, `a`, and `lambda`",
        "using exactly four residual families: `Phi`, `Phi_q v - nu`,",
        "`Phi_q a - gamma`, and Newton-Euler balance.",
        "",
        "| Model | nb | nc | stage unknowns | stage residuals | total unknowns | square |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            "| "
            f"`{row['model']}` | `{row['body_count']}` | `{row['constraint_count']}` | "
            f"`{row['stage_unknown_dim']}` | `{row['stage_residual_dim']}` | "
            f"`{row['total_unknown_dim']}` | `{row['square_total_system']}` |"
        )
    lines.extend(
        [
            "",
            "## Implementation Contract",
            "",
            "The next code symbols should be:",
            "",
            "- `pack_closed_loop_fullva_stage_vector`",
            "- `unpack_closed_loop_fullva_stage_vector`",
            "- `closed_loop_fullva_stage_residual`",
            "- `gauss6_closed_loop_fullva_dynamic_step`",
            "- `simulate_v046_local_dynamic_fullva`",
            "",
            "A row is still not accepted until the runner produces trajectory rows",
            "on the coarse-first plan and the non-floor order gate passes.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    interface = read_json(RESULTS / "closed_loop_true_dynamic_interface_audit.json")
    plan = read_json(RESULTS / "closed_loop_true_dynamic_local_row_plan.json")
    rows = scaffold_rows(read_interface_rows())
    unique_stage_dims = sorted({int(row["stage_unknown_dim"]) for row in rows})
    unique_total_dims = sorted({int(row["total_unknown_dim"]) for row in rows})
    summary = {
        "schema": "closed-loop-true-dynamic-residual-scaffold-v1",
        "status": "residual_layout_specified_runner_not_implemented",
        "method": "Gauss6/FullVA",
        "models": list(MODELS),
        "n_stages": N_STAGES,
        "row_count": len(rows),
        "stage_unknown_dim": unique_stage_dims[0] if len(unique_stage_dims) == 1 else unique_stage_dims,
        "total_unknown_dim": unique_total_dims[0] if len(unique_total_dims) == 1 else unique_total_dims,
        "residual_families": [
            "position_constraints_phi",
            "velocity_constraints_phiq_v_minus_nu",
            "acceleration_constraints_phiq_a_minus_gamma",
            "newton_euler_balance",
        ],
        "square_total_system": all(row["square_total_system"] == "true" for row in rows),
        "local_runner_implemented": False,
        "required_runner": "local_closed_loop_dynamic_dae_gauss6_fullva_runner",
        "required_code_symbols": [
            "pack_closed_loop_fullva_stage_vector",
            "unpack_closed_loop_fullva_stage_vector",
            "closed_loop_fullva_stage_residual",
            "gauss6_closed_loop_fullva_dynamic_step",
            "simulate_v046_local_dynamic_fullva",
        ],
        "accepted_dynamic_order_count": 0,
        "default_policy": "coarse_first_no_default_1e-4",
        "strict_public_policy_1e-4_required": False,
        "default_1e-4_required": False,
        "heavy_numerical_run_invoked": False,
        "external_superiority_claim": False,
        "source_inputs": {
            "interface_audit_schema": interface.get("schema"),
            "interface_dynamic_setup_ok_count": interface.get("dynamic_setup_ok_count"),
            "row_plan_schema": plan.get("schema"),
            "row_plan_count": plan.get("row_count"),
        },
        "interpretation": (
            "The closed-loop FullVA dynamic residual can be made square at 216 unknowns/residuals "
            "for each model with three Gauss stages. This artifact specifies the runner layout but "
            "does not implement or accept trajectory-order rows."
        ),
    }
    write_csv(OUT_CSV, rows)
    with OUT_JSON.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, sort_keys=True)
        handle.write("\n")
    write_markdown(summary, rows)
    print("closed_loop_true_dynamic_residual_scaffold=written")
    print("status=residual_layout_specified_runner_not_implemented")
    print(f"stage_unknown_dim={summary['stage_unknown_dim']}")
    print(f"total_unknown_dim={summary['total_unknown_dim']}")
    print("square_total_system=True")
    print("local_runner_implemented=False")
    print("default_1e-4=False")
    print("accepted_dynamic_order=0")


if __name__ == "__main__":
    main()
