#!/usr/bin/env python3
"""Build a lightweight TFE runner-contract preflight certificate.

This certificate imports the source-pendulum model module and calls the three
source-policy-facing contract entrypoints. It records that the entrypoints are
callable and candidate-backed while preserving the non-equivalence/source-policy
open boundary.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
ROOT = PAPER.parent
MODEL_PATH = ROOT.parent / "numerics" / "v048_cross_paper_same_test_benchmarks" / "tfe_source_pendulum_model.py"
OUT_JSON = PAPER / "TFE_RUNNER_CONTRACT_PREFLIGHT_CERTIFICATE.json"
OUT_MD = PAPER / "TFE_RUNNER_CONTRACT_PREFLIGHT_CERTIFICATE.md"


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def load_model_module() -> Any:
    spec = importlib.util.spec_from_file_location("tfe_source_pendulum_model", MODEL_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {MODEL_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def bool_all(values: list[object]) -> bool:
    return all(value is True for value in values)


def source_policy_equivalent(entrypoint: dict[str, Any] | None) -> bool:
    if entrypoint is None:
        return False
    return (
        entrypoint.get("source_policy_dae_runner_equivalent") is True
        or entrypoint.get("source_policy_method_runner_equivalent") is True
        or entrypoint.get("fullva_dae_source_policy_equivalent") is True
    )


def main() -> None:
    gap = read_json(PAPER / "TFE_DAE_RUNNER_CONTRACT_GAP_AUDIT.json")
    self_reproduction = read_json(PAPER / "TFE_SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_CERTIFICATE.json")
    model = load_model_module()

    absolute_contract = model.source_policy_absolute_coordinate_dae_runner()
    method_contract = model.source_policy_tfe_newmark_trapezoidal_method_runners()
    gauss6_contract = model.source_policy_gauss6_fullva_absolute_coordinate_dae_runner()

    entrypoints = [
        {
            "id": "absolute_coordinate_dae_runner_contract",
            "api": "source_policy_absolute_coordinate_dae_runner",
            "schema": absolute_contract.get("schema"),
            "runner_scope": absolute_contract.get("runner_scope"),
            "contract_present": absolute_contract.get(
                "source_policy_absolute_coordinate_dae_runner_contract_present"
            ),
            "implemented": absolute_contract.get("source_policy_absolute_coordinate_dae_runner_implemented"),
            "candidate_backed": absolute_contract.get("candidate_runner_api")
            == "monolithic_absolute_coordinate_dae_candidate_runner_smoke",
            "row_count": absolute_contract.get("row_count"),
            "metric_row_count": absolute_contract.get("metric_row_count"),
            "step_residual_row_count": absolute_contract.get("step_residual_row_count"),
            "all_rows_finite": absolute_contract.get("all_rows_finite"),
            "residual_gate": absolute_contract.get("all_dae_residuals_below_1e_10"),
            "source_policy_rows_completed": absolute_contract.get("source_policy_rows_completed"),
            "source_policy_dae_runner_equivalent": absolute_contract.get("source_policy_dae_runner_equivalent"),
            "source_policy_method_runner_equivalent": absolute_contract.get(
                "source_policy_method_runner_equivalent"
            ),
            "monolithic_absolute_coordinate_dae_time_integrator": absolute_contract.get(
                "monolithic_absolute_coordinate_dae_time_integrator"
            ),
            "accepted_use": absolute_contract.get("accepted_use"),
        },
        {
            "id": "tfe_newmark_trapezoidal_method_runner_contract",
            "api": "source_policy_tfe_newmark_trapezoidal_method_runners",
            "schema": method_contract.get("schema"),
            "runner_scope": method_contract.get("runner_scope"),
            "contract_present": method_contract.get("source_policy_method_runner_contract_present"),
            "implemented": method_contract.get(
                "source_policy_tfe_newmark_trapezoidal_method_runners_implemented"
            ),
            "candidate_backed": method_contract.get("candidate_contract_api")
            == "source_method_candidate_runner_contract_smoke",
            "row_count": method_contract.get("row_count"),
            "metric_row_count": None,
            "step_residual_row_count": None,
            "all_rows_finite": method_contract.get("all_step_states_finite"),
            "residual_gate": method_contract.get("all_candidate_residuals_below_1e_8"),
            "source_policy_rows_completed": method_contract.get("source_policy_rows_completed"),
            "source_policy_dae_runner_equivalent": method_contract.get("source_policy_dae_runner_equivalent"),
            "source_policy_method_runner_equivalent": method_contract.get(
                "source_policy_method_runner_equivalent"
            ),
            "monolithic_absolute_coordinate_dae_time_integrator": False,
            "accepted_use": method_contract.get("accepted_use"),
        },
        {
            "id": "gauss6_fullva_absolute_coordinate_dae_runner_contract",
            "api": "source_policy_gauss6_fullva_absolute_coordinate_dae_runner",
            "schema": gauss6_contract.get("schema"),
            "runner_scope": gauss6_contract.get("runner_scope"),
            "contract_present": gauss6_contract.get(
                "source_policy_gauss6_fullva_absolute_coordinate_dae_runner_contract_present"
            ),
            "implemented": gauss6_contract.get(
                "source_policy_gauss6_fullva_absolute_coordinate_dae_runner_implemented"
            ),
            "candidate_backed": gauss6_contract.get("candidate_contract_api")
            == "source_gauss6_fullva_dae_candidate_contract_smoke",
            "row_count": gauss6_contract.get("row_count"),
            "metric_row_count": None,
            "step_residual_row_count": None,
            "all_rows_finite": gauss6_contract.get("all_step_states_finite"),
            "residual_gate": gauss6_contract.get("all_candidate_residuals_below_1e_8"),
            "source_policy_rows_completed": gauss6_contract.get("source_policy_rows_completed"),
            "source_policy_dae_runner_equivalent": gauss6_contract.get("source_policy_dae_runner_equivalent"),
            "source_policy_method_runner_equivalent": gauss6_contract.get(
                "source_policy_method_runner_equivalent"
            ),
            "fullva_dae_source_policy_equivalent": gauss6_contract.get("fullva_dae_source_policy_equivalent"),
            "monolithic_absolute_coordinate_dae_time_integrator": gauss6_contract.get(
                "monolithic_absolute_coordinate_dae_time_integrator"
            ),
            "accepted_use": gauss6_contract.get("accepted_use"),
        },
    ]

    entrypoint_count = len(entrypoints)
    candidate_backed_count = sum(1 for item in entrypoints if item["candidate_backed"] is True)
    callable_contract_count = sum(1 for item in entrypoints if item["contract_present"] is True)
    total_source_policy_rows_completed = sum(
        int(item.get("source_policy_rows_completed") or 0) for item in entrypoints
    )
    all_non_equivalent = all(
        item.get("source_policy_dae_runner_equivalent") is False
        and item.get("source_policy_method_runner_equivalent") is False
        for item in entrypoints
    )
    all_candidate_rows_finite = bool_all([item.get("all_rows_finite") for item in entrypoints])
    all_residual_gates_passed = bool_all([item.get("residual_gate") for item in entrypoints])

    execution_blocks = list(gap.get("source_policy_execution_missing_contract_blocks", []))
    required_runner_contracts = list(
        gap.get("source_policy_execution_preflight", {}).get("runner_contracts_required_before_execution", [])
    )
    missing_by_id = {
        item.get("id"): item
        for item in gap.get("missing_contract_blocks", [])
        if isinstance(item, dict)
    }
    entrypoint_by_id = {item["id"]: item for item in entrypoints}
    block_specs = [
        (
            "pendulum_absolute_coordinate_source_policy_dae_runner_missing",
            "monolithic_absolute_coordinate_DAE_time_integrator",
            "absolute_coordinate_dae_runner_contract",
        ),
        (
            "tfe_newmark_trapezoidal_source_policy_method_runners_missing",
            "TFE_m1_m2_m3_Newmark_beta_trapezoidal_source_policy_method_runners",
            "tfe_newmark_trapezoidal_method_runner_contract",
        ),
        (
            "gauss6_fullva_absolute_coordinate_source_policy_runner_missing",
            "Gauss6_FullVA_absolute_coordinate_source_policy_DAE_runner",
            "gauss6_fullva_absolute_coordinate_dae_runner_contract",
        ),
        (
            "accepted_source_policy_work_precision_rows_not_executed_or_bound",
            "accepted_T10_source_policy_work_precision_rows",
            None,
        ),
    ]
    execution_block_matrix = []
    for block_id, required_contract, entrypoint_id in block_specs:
        blocker = missing_by_id.get(block_id, {})
        entrypoint = entrypoint_by_id.get(entrypoint_id) if entrypoint_id is not None else None
        rows_completed = int(entrypoint.get("source_policy_rows_completed") or 0) if entrypoint else 0
        equivalent = source_policy_equivalent(entrypoint)
        candidate_backed = entrypoint.get("candidate_backed") is True if entrypoint else False
        contract_present = entrypoint.get("contract_present") is True if entrypoint else False
        implemented = entrypoint.get("implemented") is True if entrypoint else False
        if entrypoint is None:
            closure_status = "open_no_candidate_entrypoint_work_precision_rows"
        elif candidate_backed and not equivalent:
            closure_status = "open_candidate_backed_not_source_policy_equivalent"
        else:
            closure_status = "open_missing_source_policy_equivalence"
        execution_block_matrix.append(
            {
                "id": block_id,
                "required_runner_contract": required_contract,
                "mapped_entrypoint_id": entrypoint_id,
                "mapped_entrypoint_api": entrypoint.get("api") if entrypoint else None,
                "contract_present": contract_present,
                "candidate_backed": candidate_backed,
                "implemented": implemented,
                "source_policy_equivalent": equivalent,
                "source_policy_rows_completed": rows_completed,
                "can_resolve_without_heavy_run": blocker.get("can_resolve_without_heavy_run"),
                "first_required_artifact": blocker.get("first_required_artifact"),
                "blocking_scope": blocker.get("blocking_scope"),
                "closure_status": closure_status,
            }
        )
    execution_block_matrix_summary = {
        "execution_block_count": len(execution_block_matrix),
        "candidate_backed_entrypoint_blocks": sum(
            1 for item in execution_block_matrix if item["candidate_backed"] is True
        ),
        "blocks_without_candidate_entrypoint": sum(
            1 for item in execution_block_matrix if item["mapped_entrypoint_id"] is None
        ),
        "source_policy_equivalent_blocks": sum(
            1 for item in execution_block_matrix if item["source_policy_equivalent"] is True
        ),
        "source_policy_rows_completed": sum(
            int(item.get("source_policy_rows_completed") or 0) for item in execution_block_matrix
        ),
        "can_resolve_without_heavy_run_blocks": sum(
            1 for item in execution_block_matrix if item["can_resolve_without_heavy_run"] is True
        ),
        "requires_new_artifact_or_execution_blocks": sum(
            1 for item in execution_block_matrix if item["can_resolve_without_heavy_run"] is False
        ),
        "closure_status": "all_source_policy_execution_blocks_open",
    }
    certificate = {
        "schema": "tfe-runner-contract-preflight-certificate-v1",
        "status": "contract_entrypoints_callable_candidate_backed_source_policy_open",
        "read_only": True,
        "heavy_numerical_run_invoked": False,
        "run_v047_invoked": False,
        "v048_runner_invoked": False,
        "model_source": "../../numerics/v048_cross_paper_same_test_benchmarks/tfe_source_pendulum_model.py",
        "generated_from": [
            "TFE_DAE_RUNNER_CONTRACT_GAP_AUDIT.json",
            "TFE_SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_CERTIFICATE.json",
            "../../numerics/v048_cross_paper_same_test_benchmarks/tfe_source_pendulum_model.py",
        ],
        "entrypoint_count": entrypoint_count,
        "callable_contract_count": callable_contract_count,
        "candidate_backed_contract_count": candidate_backed_count,
        "all_candidate_rows_finite": all_candidate_rows_finite,
        "all_residual_gates_passed": all_residual_gates_passed,
        "all_non_equivalent": all_non_equivalent,
        "source_policy_rows_completed": total_source_policy_rows_completed,
        "source_policy_closed": False,
        "source_policy_dae_runner_equivalent": False,
        "source_policy_method_runner_equivalent": False,
        "monolithic_absolute_coordinate_dae_time_integrator": False,
        "external_superiority_claim_allowed": False,
        "submission_ready": False,
        "entrypoints": entrypoints,
        "source_policy_execution_preflight_status": gap.get("source_policy_execution_preflight", {}).get("status"),
        "source_policy_execution_blocks": execution_blocks,
        "source_policy_execution_block_count": len(execution_blocks),
        "source_policy_execution_block_matrix": execution_block_matrix,
        "source_policy_execution_block_matrix_summary": execution_block_matrix_summary,
        "required_runner_contracts_before_execution": required_runner_contracts,
        "tfe_self_reproduction_status": self_reproduction.get("status"),
        "tfe_self_reproduction_reopen_condition": self_reproduction.get("reopen_condition"),
        "safe_current_use": "runner_contract_preflight_only_not_source_policy_reproduction",
        "next_to_close": (
            "Replace candidate-backed contract entrypoints with source-code-equivalent "
            "absolute-coordinate DAE and method runners, then execute accepted source-policy rows."
        ),
    }

    OUT_JSON.write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# TFE Runner Contract Preflight Certificate",
        "",
        f"Status: **{certificate['status']}**.",
        f"Entry points callable/candidate-backed: `{callable_contract_count}/{entrypoint_count}` / `{candidate_backed_count}/{entrypoint_count}`.",
        f"Candidate rows finite/residual gates: `{all_candidate_rows_finite}/{all_residual_gates_passed}`.",
        f"Source-policy rows completed: `{total_source_policy_rows_completed}`.",
        f"Source-policy equivalent DAE/method: `{certificate['source_policy_dae_runner_equivalent']}/{certificate['source_policy_method_runner_equivalent']}`.",
        f"Execution blocks remaining: `{len(execution_blocks)}` / `{execution_blocks}`.",
        "",
        "| entrypoint | rows | metrics | candidate-backed | implemented | equivalent | accepted use |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    for item in entrypoints:
        equivalent = (
            item.get("source_policy_dae_runner_equivalent") is True
            or item.get("source_policy_method_runner_equivalent") is True
            or item.get("fullva_dae_source_policy_equivalent") is True
        )
        lines.append(
            f"| `{item['api']}` | `{item['row_count']}` | `{item['metric_row_count']}` | "
            f"`{item['candidate_backed']}` | `{item['implemented']}` | `{equivalent}` | "
            f"{item['accepted_use']} |"
        )
    lines.extend(
        [
            "",
            "| execution block | mapped entrypoint | candidate-backed | equivalent | rows completed | first required artifact |",
            "|---|---|---:|---:|---:|---|",
        ]
    )
    for item in execution_block_matrix:
        lines.append(
            f"| `{item['id']}` | `{item['mapped_entrypoint_api']}` | "
            f"`{item['candidate_backed']}` | `{item['source_policy_equivalent']}` | "
            f"`{item['source_policy_rows_completed']}` | {item['first_required_artifact']} |"
        )
    lines.extend(
        [
            "",
            (
                "Execution block closure summary: "
                f"`{execution_block_matrix_summary['candidate_backed_entrypoint_blocks']}/"
                f"{execution_block_matrix_summary['execution_block_count']}` candidate-backed, "
                f"`{execution_block_matrix_summary['source_policy_equivalent_blocks']}` source-policy equivalent, "
                f"`{execution_block_matrix_summary['source_policy_rows_completed']}` rows completed, "
                f"`{execution_block_matrix_summary['can_resolve_without_heavy_run_blocks']}` closable without heavy/source-policy execution."
            ),
            "",
            "This certificate is a runner-contract preflight only. It does not close OC6,",
            "does not run a source-policy campaign, and does not authorize external-superiority claims.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("tfe_runner_contract_preflight_certificate=written")
    print(f"entrypoints={callable_contract_count}/{entrypoint_count}")
    print(f"candidate_backed={candidate_backed_count}/{entrypoint_count}")
    print(f"source_policy_rows_completed={total_source_policy_rows_completed}")
    print(f"execution_blocks={len(execution_blocks)}")


if __name__ == "__main__":
    main()
