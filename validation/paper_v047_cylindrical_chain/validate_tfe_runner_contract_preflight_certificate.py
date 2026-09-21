#!/usr/bin/env python3
"""Validate the TFE runner-contract preflight certificate."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
ROOT = PAPER.parent
MODEL_PATH = ROOT.parent / "numerics" / "v048_cross_paper_same_test_benchmarks" / "tfe_source_pendulum_model.py"


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


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def main() -> int:
    checks = Checks()
    try:
        cert = read_json(PAPER / "TFE_RUNNER_CONTRACT_PREFLIGHT_CERTIFICATE.json")
        cert_md = read_text(PAPER / "TFE_RUNNER_CONTRACT_PREFLIGHT_CERTIFICATE.md")
        gap = read_json(PAPER / "TFE_DAE_RUNNER_CONTRACT_GAP_AUDIT.json")
        self_reproduction = read_json(PAPER / "TFE_SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_CERTIFICATE.json")
        model_source = read_text(MODEL_PATH)
    except Exception as exc:  # noqa: BLE001
        print(f"TFE runner contract preflight certificate validation: FAIL\n- {exc}")
        return 1

    checks.check(
        cert.get("schema") == "tfe-runner-contract-preflight-certificate-v1",
        "schema changed",
    )
    checks.check(
        cert.get("status") == "contract_entrypoints_callable_candidate_backed_source_policy_open",
        "status changed",
    )
    checks.check(cert.get("read_only") is True, "certificate must be read-only")
    checks.check(cert.get("heavy_numerical_run_invoked") is False, "certificate invoked heavy run")
    checks.check(cert.get("run_v047_invoked") is False, "certificate invoked run_v047")
    checks.check(cert.get("v048_runner_invoked") is False, "certificate invoked v048 runner")
    checks.check(
        "TFE_DAE_RUNNER_CONTRACT_GAP_AUDIT.json" in cert.get("generated_from", [])
        and "TFE_SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_CERTIFICATE.json" in cert.get("generated_from", [])
        and "../../numerics/v048_cross_paper_same_test_benchmarks/tfe_source_pendulum_model.py"
        in cert.get("generated_from", []),
        "certificate provenance missing required inputs",
    )
    for symbol in [
        "def source_policy_absolute_coordinate_dae_runner",
        "def source_policy_tfe_newmark_trapezoidal_method_runners",
        "def source_policy_gauss6_fullva_absolute_coordinate_dae_runner",
    ]:
        checks.check(symbol in model_source, f"model source missing symbol: {symbol}")

    entrypoints = cert.get("entrypoints", [])
    by_id = {item.get("id"): item for item in entrypoints if isinstance(item, dict)}
    checks.check(cert.get("entrypoint_count") == 3 == len(entrypoints), "entrypoint count changed")
    checks.check(cert.get("callable_contract_count") == 3, "callable contract count changed")
    checks.check(cert.get("candidate_backed_contract_count") == 3, "candidate-backed count changed")
    checks.check(cert.get("all_candidate_rows_finite") is True, "candidate rows not finite")
    checks.check(cert.get("all_residual_gates_passed") is True, "candidate residual gates failed")
    checks.check(cert.get("all_non_equivalent") is True, "certificate overclaims equivalence")
    checks.check(cert.get("source_policy_rows_completed") == 0, "certificate overclosed source-policy rows")
    checks.check(cert.get("source_policy_closed") is False, "certificate overclosed source-policy")
    checks.check(cert.get("source_policy_dae_runner_equivalent") is False, "certificate overclaims DAE equivalence")
    checks.check(cert.get("source_policy_method_runner_equivalent") is False, "certificate overclaims method equivalence")
    checks.check(
        cert.get("monolithic_absolute_coordinate_dae_time_integrator") is False,
        "certificate overclaims monolithic source-policy DAE integrator",
    )
    checks.check(cert.get("external_superiority_claim_allowed") is False, "certificate overclaims superiority")
    checks.check(cert.get("submission_ready") is False, "certificate overclaims submission readiness")

    absolute = by_id.get("absolute_coordinate_dae_runner_contract", {})
    method = by_id.get("tfe_newmark_trapezoidal_method_runner_contract", {})
    gauss6 = by_id.get("gauss6_fullva_absolute_coordinate_dae_runner_contract", {})
    checks.check(
        absolute.get("api") == "source_policy_absolute_coordinate_dae_runner"
        and absolute.get("contract_present") is True
        and absolute.get("candidate_backed") is True
        and absolute.get("implemented") is False
        and absolute.get("row_count") == 4
        and absolute.get("metric_row_count") == 12
        and absolute.get("step_residual_row_count") == 56
        and absolute.get("source_policy_rows_completed") == 0
        and absolute.get("source_policy_dae_runner_equivalent") is False
        and absolute.get("monolithic_absolute_coordinate_dae_time_integrator") is False,
        "absolute-coordinate DAE runner preflight boundary changed",
    )
    checks.check(
        method.get("api") == "source_policy_tfe_newmark_trapezoidal_method_runners"
        and method.get("contract_present") is True
        and method.get("candidate_backed") is True
        and method.get("implemented") is False
        and method.get("row_count") == 5
        and method.get("source_policy_rows_completed") == 0
        and method.get("source_policy_method_runner_equivalent") is False
        and method.get("source_policy_dae_runner_equivalent") is False,
        "method runner preflight boundary changed",
    )
    checks.check(
        gauss6.get("api") == "source_policy_gauss6_fullva_absolute_coordinate_dae_runner"
        and gauss6.get("contract_present") is True
        and gauss6.get("candidate_backed") is True
        and gauss6.get("implemented") is False
        and gauss6.get("row_count") == 1
        and gauss6.get("source_policy_rows_completed") == 0
        and gauss6.get("source_policy_dae_runner_equivalent") is False
        and gauss6.get("fullva_dae_source_policy_equivalent") is False
        and gauss6.get("monolithic_absolute_coordinate_dae_time_integrator") is False,
        "Gauss6 FullVA runner preflight boundary changed",
    )
    checks.check(
        cert.get("source_policy_execution_preflight_status")
        == gap.get("source_policy_execution_preflight", {}).get("status")
        == "terminal_no_public_code_self_reproduction_attempted_not_promoted",
        "source-policy execution preflight status changed",
    )
    checks.check(
        cert.get("source_policy_execution_blocks")
        == gap.get("source_policy_execution_missing_contract_blocks")
        == [
            "pendulum_absolute_coordinate_source_policy_dae_runner_missing",
            "tfe_newmark_trapezoidal_source_policy_method_runners_missing",
            "gauss6_fullva_absolute_coordinate_source_policy_runner_missing",
            "accepted_source_policy_work_precision_rows_not_executed_or_bound",
        ],
        "source-policy execution blocks changed",
    )
    checks.check(cert.get("source_policy_execution_block_count") == 4, "execution block count changed")
    matrix = cert.get("source_policy_execution_block_matrix", [])
    matrix_by_id = {item.get("id"): item for item in matrix if isinstance(item, dict)}
    matrix_summary = cert.get("source_policy_execution_block_matrix_summary", {})
    missing_by_id = {
        item.get("id"): item
        for item in gap.get("missing_contract_blocks", [])
        if isinstance(item, dict)
    }
    expected_block_specs = {
        "pendulum_absolute_coordinate_source_policy_dae_runner_missing": (
            "monolithic_absolute_coordinate_DAE_time_integrator",
            "absolute_coordinate_dae_runner_contract",
            "source_policy_absolute_coordinate_dae_runner",
        ),
        "tfe_newmark_trapezoidal_source_policy_method_runners_missing": (
            "TFE_m1_m2_m3_Newmark_beta_trapezoidal_source_policy_method_runners",
            "tfe_newmark_trapezoidal_method_runner_contract",
            "source_policy_tfe_newmark_trapezoidal_method_runners",
        ),
        "gauss6_fullva_absolute_coordinate_source_policy_runner_missing": (
            "Gauss6_FullVA_absolute_coordinate_source_policy_DAE_runner",
            "gauss6_fullva_absolute_coordinate_dae_runner_contract",
            "source_policy_gauss6_fullva_absolute_coordinate_dae_runner",
        ),
        "accepted_source_policy_work_precision_rows_not_executed_or_bound": (
            "accepted_T10_source_policy_work_precision_rows",
            None,
            None,
        ),
    }
    checks.check(len(matrix) == 4, "execution block matrix row count changed")
    checks.check(set(matrix_by_id) == set(expected_block_specs), "execution block matrix ids changed")
    for block_id, (required_contract, entrypoint_id, api) in expected_block_specs.items():
        item = matrix_by_id.get(block_id, {})
        blocker = missing_by_id.get(block_id, {})
        checks.check(item.get("required_runner_contract") == required_contract, f"{block_id} required contract changed")
        checks.check(item.get("mapped_entrypoint_id") == entrypoint_id, f"{block_id} entrypoint mapping changed")
        checks.check(item.get("mapped_entrypoint_api") == api, f"{block_id} API mapping changed")
        checks.check(
            item.get("first_required_artifact") == blocker.get("first_required_artifact"),
            f"{block_id} first required artifact stale",
        )
        checks.check(
            item.get("blocking_scope") == blocker.get("blocking_scope"),
            f"{block_id} blocking scope stale",
        )
        checks.check(
            item.get("can_resolve_without_heavy_run") is False,
            f"{block_id} unexpectedly closable without heavy/source-policy execution",
        )
        checks.check(item.get("source_policy_equivalent") is False, f"{block_id} overclaims source-policy equivalence")
        checks.check(item.get("source_policy_rows_completed") == 0, f"{block_id} overclosed source-policy rows")
    for block_id in [
        "pendulum_absolute_coordinate_source_policy_dae_runner_missing",
        "tfe_newmark_trapezoidal_source_policy_method_runners_missing",
        "gauss6_fullva_absolute_coordinate_source_policy_runner_missing",
    ]:
        item = matrix_by_id.get(block_id, {})
        checks.check(item.get("contract_present") is True, f"{block_id} contract entrypoint missing")
        checks.check(item.get("candidate_backed") is True, f"{block_id} candidate-backed marker missing")
        checks.check(item.get("implemented") is False, f"{block_id} overclaims source-policy implementation")
        checks.check(
            item.get("closure_status") == "open_candidate_backed_not_source_policy_equivalent",
            f"{block_id} closure status changed",
        )
    work_item = matrix_by_id.get("accepted_source_policy_work_precision_rows_not_executed_or_bound", {})
    checks.check(work_item.get("contract_present") is False, "work-precision block unexpectedly has contract entrypoint")
    checks.check(work_item.get("candidate_backed") is False, "work-precision block unexpectedly candidate-backed")
    checks.check(
        work_item.get("closure_status") == "open_no_candidate_entrypoint_work_precision_rows",
        "work-precision closure status changed",
    )
    checks.check(
        matrix_summary
        == {
            "execution_block_count": 4,
            "candidate_backed_entrypoint_blocks": 3,
            "blocks_without_candidate_entrypoint": 1,
            "source_policy_equivalent_blocks": 0,
            "source_policy_rows_completed": 0,
            "can_resolve_without_heavy_run_blocks": 0,
            "requires_new_artifact_or_execution_blocks": 4,
            "closure_status": "all_source_policy_execution_blocks_open",
        },
        "execution block matrix summary changed",
    )
    checks.check(
        cert.get("tfe_self_reproduction_status") == self_reproduction.get("status"),
        "self-reproduction status mirror stale",
    )
    checks.check(
        cert.get("tfe_self_reproduction_reopen_condition")
        == "new_public_or_source_code_equivalent_tfe_implementation_artifact",
        "self-reproduction reopen condition changed",
    )
    checks.check(
        cert.get("safe_current_use") == "runner_contract_preflight_only_not_source_policy_reproduction",
        "safe-current-use boundary changed",
    )

    for token in [
        "Status: **contract_entrypoints_callable_candidate_backed_source_policy_open**.",
        "Entry points callable/candidate-backed: `3/3` / `3/3`.",
        "Candidate rows finite/residual gates: `True/True`.",
        "Source-policy rows completed: `0`.",
        "Source-policy equivalent DAE/method: `False/False`.",
        "Execution blocks remaining: `4`",
        "`source_policy_absolute_coordinate_dae_runner` | `4` | `12` | `True` | `False` | `False`",
        "`source_policy_tfe_newmark_trapezoidal_method_runners` | `5` | `None` | `True` | `False` | `False`",
        "`source_policy_gauss6_fullva_absolute_coordinate_dae_runner` | `1` | `None` | `True` | `False` | `False`",
        "`pendulum_absolute_coordinate_source_policy_dae_runner_missing` | `source_policy_absolute_coordinate_dae_runner` | `True` | `False` | `0`",
        "`accepted_source_policy_work_precision_rows_not_executed_or_bound` | `None` | `False` | `False` | `0`",
        "Execution block closure summary: `3/4` candidate-backed, `0` source-policy equivalent, `0` rows completed, `0` closable without heavy/source-policy execution.",
        "This certificate is a runner-contract preflight only.",
    ]:
        checks.check(token in cert_md, f"certificate markdown missing token: {token}")

    if checks.errors:
        print("TFE runner contract preflight certificate validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("TFE runner contract preflight certificate validation: PASS")
    print("entrypoints=3/3")
    print("candidate_backed=3/3")
    print("source_policy_rows_completed=0")
    print("execution_blocks=4")
    print("source_policy_equivalent=False/False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
