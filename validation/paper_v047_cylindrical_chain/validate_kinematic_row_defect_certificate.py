#!/usr/bin/env python3
"""Read-only validator for the partial kinematic row defect certificate."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
CERT_MD = PAPER / "KINEMATIC_ROW_DEFECT_CERTIFICATE.md"
CERT_JSON = PAPER / "KINEMATIC_ROW_DEFECT_CERTIFICATE.json"
DYNAMIC_ORACLE = PAPER / "DYNAMIC_ROW_ORACLE_GATE.json"
PROOF_CONTRACT = PAPER / "CMAME_PROOF_CONTRACT_GATE.json"
BLOCKER_GATE = PAPER / "CMAME_BLOCKER_CLOSURE_GATE.json"
MANIFEST = PAPER / "SUBMISSION_ARTIFACT_MANIFEST.json"

CERTIFIED_FAMILIES = [
    "translational_position_weak_defect",
    "rotational_lie_position_weak_defect",
    "translational_velocity_weak_defect",
    "angular_velocity_weak_defect",
    "lower_pair_index3_weak_constraints",
]


class Checks:
    def __init__(self) -> None:
        self.errors: list[str] = []

    def check(self, condition: bool, message: str) -> None:
        if not condition:
            self.errors.append(message)


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(path)
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def read_text(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8", errors="replace")


def contains_normalized(text: str, token: str) -> bool:
    return token in text or " ".join(token.split()) in " ".join(text.split())


def blocker_by_id(blocker_gate: dict[str, Any], blocker_id: str) -> dict[str, Any]:
    for blocker in blocker_gate.get("blockers", []):
        if isinstance(blocker, dict) and blocker.get("id") == blocker_id:
            return blocker
    return {}


def main() -> int:
    checks = Checks()
    try:
        cert = read_json(CERT_JSON)
        cert_md = read_text(CERT_MD)
        dynamic_oracle = read_json(DYNAMIC_ORACLE)
        proof_contract = read_json(PROOF_CONTRACT)
        blocker_gate = read_json(BLOCKER_GATE)
        manifest = read_json(MANIFEST)
    except Exception as exc:  # noqa: BLE001
        print(f"kinematic_row_defect_certificate=FAIL\n- {exc}")
        return 1

    proof_scope = cert.get("proof_scope", {})
    certificate = cert.get("certificate", {})
    execution = cert.get("execution_policy", {})
    partial_oracle = dynamic_oracle.get("partial_independent_formula_row_oracle", {})
    theorem = proof_contract.get("theorem_contract", {})
    b1 = blocker_by_id(blocker_gate, "B1")
    b3 = blocker_by_id(blocker_gate, "B3")

    checks.check(cert.get("schema") == "kinematic-row-defect-certificate-v1", "schema changed")
    checks.check(
        cert.get("status") == "partial_96_row_proof_certificate_not_submission_ready",
        "status changed",
    )
    checks.check(cert.get("submission_ready") is False, "certificate must not claim submission ready")
    checks.check(cert.get("accepted_method") == "Gauss6/FullVA", "accepted method changed")
    checks.check(cert.get("accepted_residual") == "residual_cylindrical_chain", "accepted residual changed")

    checks.check(proof_scope.get("certified_row_count") == 96, "certified row count changed")
    checks.check(proof_scope.get("certified_row_families") == CERTIFIED_FAMILIES, "certified row families changed")
    checks.check(proof_scope.get("excluded_row_family") == "newton_euler_weak_balance", "excluded family changed")
    checks.check(proof_scope.get("excluded_row_count") == 36, "excluded row count changed")
    checks.check(proof_scope.get("total_runtime_rows") == 132, "total runtime row count changed")

    checks.check(certificate.get("partial_stage_defect_certificate") is True, "partial certificate marker missing")
    checks.check(
        certificate.get("collocation_lift_rows_zero_on_smooth_lift") is True,
        "collocation lift marker missing",
    )
    checks.check(
        certificate.get("lower_pair_index3_rows_zero_on_smooth_constrained_branch") is True,
        "lower-pair lift marker missing",
    )
    checks.check(
        certificate.get("formula_row_oracle_supports_runtime_mapping") is True,
        "formula-row oracle support marker missing",
    )
    checks.check(
        certificate.get("compatible_with_local_h7_defect_budget_for_certified_rows") is True,
        "local h7 compatibility marker missing",
    )
    checks.check(
        certificate.get("stage_residual_O_h7_implementation_defect_proved") is False,
        "certificate overclaims full O(h^7) defect proof",
    )
    checks.check(certificate.get("dynamic_symbolic_oracle_complete") is False, "certificate overclaims symbolic oracle")
    checks.check(certificate.get("full_tfe_stage_replacement") is False, "certificate overclaims full TFE replacement")

    checks.check(execution.get("default_1e-4_required") is False, "certificate requires default 1e-4")
    checks.check(execution.get("run_v047_invoked") is False, "certificate invoked run_v047")
    checks.check(execution.get("v048_runner_invoked") is False, "certificate invoked v048 runner")
    checks.check(execution.get("heavy_numerical_run_invoked") is False, "certificate invoked heavy numerical run")

    checks.check(partial_oracle.get("checked") is True, "dynamic oracle partial formula rows not checked")
    checks.check(partial_oracle.get("row_count") == 96, "dynamic oracle partial row count changed")
    checks.check(partial_oracle.get("row_families") == CERTIFIED_FAMILIES, "dynamic oracle partial row family mismatch")
    checks.check(
        partial_oracle.get("excluded_row_family") == "newton_euler_weak_balance",
        "dynamic oracle excluded family mismatch",
    )

    checks.check(
        theorem.get("partial_kinematic_stage_defect_certificate_checked") is True,
        "proof contract missing partial kinematic certificate marker",
    )
    checks.check(
        theorem.get("partial_kinematic_stage_defect_rows_checked") == 96,
        "proof contract partial kinematic row count changed",
    )
    checks.check(
        theorem.get("newton_euler_stage_defect_certificate_open") is False,
        "proof contract still marks Newton-Euler direct-substitution certificate open",
    )
    checks.check(
        theorem.get("newton_euler_stage_defect_certificate_closed_by_direct_substitution") is True,
        "proof contract lost Newton-Euler direct-substitution closure marker",
    )
    checks.check(
        theorem.get("newton_euler_stage_defect_certificate_satisfaction_mode")
        == "D5 same-branch residual-value certificate: 96-row O(h^7) non-dynamic certificate plus 36 dynamic zero rows at Z_G",
        "proof contract Newton-Euler satisfaction mode changed",
    )
    checks.check(
        theorem.get("stage_residual_O_h7_implementation_defect_proved") is True,
        "proof contract lost direct-substitution O(h^7) implementation-defect proof",
    )

    checks.check(
        "partial_kinematic_stage_defect_certificate_96_rows" in b1.get("partial_progress", []),
        "B1 missing partial kinematic defect progress marker",
    )
    checks.check(
        "KINEMATIC_ROW_DEFECT_CERTIFICATE.md" in b1.get("partial_progress_evidence", []),
        "B1 missing certificate evidence",
    )
    checks.check(
        "partial_kinematic_stage_defect_certificate_added" in b3.get("partial_progress", []),
        "B3 missing partial kinematic defect progress marker",
    )
    checks.check(
        "KINEMATIC_ROW_DEFECT_CERTIFICATE.json" in b3.get("partial_progress_evidence", []),
        "B3 missing certificate JSON evidence",
    )

    checks.check("KINEMATIC_ROW_DEFECT_CERTIFICATE.md" in manifest.get("evidence_anchors", []), "manifest missing certificate")
    checks.check("KINEMATIC_ROW_DEFECT_CERTIFICATE.json" in manifest.get("evidence_anchors", []), "manifest missing certificate JSON")
    checks.check(
        "validate_kinematic_row_defect_certificate.py" in manifest.get("validators", []),
        "manifest missing certificate validator",
    )

    for token in [
        "Kinematic Row Defect Certificate",
        "PARTIAL PROOF CERTIFICATE - 96 ROWS - NOT SUBMISSION READY",
        "Total certified proof-scope rows: `96`",
        "excluded family is `newton_euler_weak_balance`",
        "partial certificate",
        "stage_residual_O_h7_implementation_defect_proved",
        "dynamic_symbolic_oracle_complete",
        "full_tfe_stage_replacement",
        "default `1e-4` campaign",
        "validate_kinematic_row_defect_certificate.py",
    ]:
        checks.check(contains_normalized(cert_md, token), f"certificate markdown missing token: {token}")

    forbidden = set(cert.get("forbidden_claims", []))
    for token in [
        "stage_residual_O_h7_implementation_defect_proved_true",
        "dynamic_symbolic_oracle_complete_true",
        "full_tfe_stage_replacement_true",
        "external_superiority_claim_true",
        "submission_ready_true",
    ]:
        checks.check(token in forbidden, f"forbidden claim missing: {token}")

    if checks.errors:
        print("kinematic_row_defect_certificate=FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("kinematic_row_defect_certificate=PASS")
    print("accepted_method=Gauss6/FullVA")
    print("accepted_residual=residual_cylindrical_chain")
    print("certified_row_count=96")
    print("excluded_row_family=newton_euler_weak_balance")
    print("partial_stage_defect_certificate=True")
    print("stage_residual_O_h7_implementation_defect_proved=False")
    print("dynamic_symbolic_oracle_complete=False")
    print("full_tfe_stage_replacement=False")
    print("default_1e-4=False")
    print("run_v047_invoked=False")
    print("v048_runner_invoked=False")
    print("submission_ready=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
