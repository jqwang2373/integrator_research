#!/usr/bin/env python3
"""Read-only validator for the Newton-Euler dynamic defect obligation gate."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
GATE_MD = PAPER / "NEWTON_EULER_DEFECT_OBLIGATION_GATE.md"
GATE_JSON = PAPER / "NEWTON_EULER_DEFECT_OBLIGATION_GATE.json"
DYNAMIC_ORACLE = PAPER / "DYNAMIC_ROW_ORACLE_GATE.json"
KINEMATIC_DEFECT = PAPER / "KINEMATIC_ROW_DEFECT_CERTIFICATE.json"
SYMBOLIC_TARGET_AUDIT = PAPER / "NEWTON_EULER_SYMBOLIC_TARGET_AUDIT.json"
PROOF_CONTRACT = PAPER / "CMAME_PROOF_CONTRACT_GATE.json"
BLOCKER_GATE = PAPER / "CMAME_BLOCKER_CLOSURE_GATE.json"
MANIFEST = PAPER / "SUBMISSION_ARTIFACT_MANIFEST.json"

EXPECTED_OBLIGATIONS = [
    "gauss_stage_dynamic_defect_rate",
]
EXPECTED_CLOSED_OBLIGATIONS = [
    "translational_balance_identity",
    "rotational_balance_identity",
    "multiplier_wrench_consistency",
    "smooth_force_lift_consistency",
    "symbolic_runtime_row_equivalence",
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
        gate = read_json(GATE_JSON)
        gate_md = read_text(GATE_MD)
        dynamic_oracle = read_json(DYNAMIC_ORACLE)
        kinematic_defect = read_json(KINEMATIC_DEFECT)
        symbolic_target_audit = read_json(SYMBOLIC_TARGET_AUDIT)
        proof_contract = read_json(PROOF_CONTRACT)
        blocker_gate = read_json(BLOCKER_GATE)
        manifest = read_json(MANIFEST)
    except Exception as exc:  # noqa: BLE001
        print(f"newton_euler_defect_obligation_gate=FAIL\n- {exc}")
        return 1

    proof_scope = gate.get("proof_scope", {})
    runtime_oracles = gate.get("supporting_runtime_oracles", {})
    closure = gate.get("closure_state", {})
    execution = gate.get("execution_policy", {})
    obligations = gate.get("open_obligations", [])
    closed_obligations = gate.get("closed_obligations", [])
    theorem = proof_contract.get("theorem_contract", {})
    b1 = blocker_by_id(blocker_gate, "B1")
    b3 = blocker_by_id(blocker_gate, "B3")

    checks.check(gate.get("schema") == "newton-euler-defect-obligation-gate-v1", "schema changed")
    checks.check(
        gate.get("status") == "d5_symbolic_primitive_route_open_active_direct_pc2_closed_not_submission_ready",
        "status changed",
    )
    checks.check(gate.get("submission_ready") is False, "gate must not claim submission ready")
    checks.check(gate.get("accepted_method") == "Gauss6/FullVA", "accepted method changed")
    checks.check(gate.get("accepted_residual") == "residual_cylindrical_chain", "accepted residual changed")

    checks.check(proof_scope.get("row_family") == "newton_euler_weak_balance", "row family changed")
    checks.check(proof_scope.get("dynamic_row_count") == 36, "dynamic row count changed")
    checks.check(proof_scope.get("stage_count") == 3, "stage count changed")
    checks.check(proof_scope.get("body_count") == 2, "body count changed")
    checks.check(proof_scope.get("rows_per_body_stage") == 6, "rows per body-stage changed")
    checks.check(proof_scope.get("translational_balance_rows") == 18, "translational row count changed")
    checks.check(proof_scope.get("rotational_balance_rows") == 18, "rotational row count changed")
    checks.check(proof_scope.get("total_runtime_rows") == 132, "total runtime row count changed")
    checks.check(
        proof_scope.get("kinematic_certificate_rows_already_certified") == 96,
        "kinematic certificate row count changed",
    )

    checks.check(
        runtime_oracles.get("full_formula_row_oracle_132_rows_checked") is True,
        "full formula-row oracle marker missing",
    )
    checks.check(
        runtime_oracles.get("newton_euler_formula_oracle_complete") is True,
        "Newton-Euler formula oracle marker missing",
    )
    checks.check(
        runtime_oracles.get("formula_row_ad_jacobian_oracle_checked") is True,
        "formula-row AD Jacobian marker missing",
    )
    checks.check(runtime_oracles.get("formula_row_ad_jacobian_probe_count") == 3, "AD probe count changed")
    checks.check(
        runtime_oracles.get("partial_kinematic_stage_defect_certificate_checked") is True,
        "kinematic defect support marker missing",
    )
    checks.check(runtime_oracles.get("partial_kinematic_stage_defect_rows_checked") == 96, "kinematic support rows changed")
    checks.check(runtime_oracles.get("symbolic_target_audit_checked") is True, "symbolic target audit support marker missing")
    checks.check(runtime_oracles.get("symbolic_target_audit_rows") == 36, "symbolic target audit row count changed")
    checks.check(
        runtime_oracles.get("symbolic_target_audit_translational_rotational_rows") == "18/18",
        "symbolic target audit translational/rotational count changed",
    )
    checks.check(
        runtime_oracles.get("balance_identity_audit_checked") is True,
        "balance identity audit support marker missing",
    )
    checks.check(
        runtime_oracles.get("balance_identity_closed_rows") == 36,
        "balance identity closed rows changed",
    )

    checks.check(isinstance(obligations, list) and len(obligations) == 1, "obligation list length changed")
    checks.check([item.get("id") for item in obligations if isinstance(item, dict)] == EXPECTED_OBLIGATIONS, "obligation IDs changed")
    for item in obligations:
        if not isinstance(item, dict):
            checks.check(False, "obligation entry is not an object")
            continue
        checks.check(item.get("status") == "symbolic_primitive_route_open", f"{item.get('id')} has wrong lane status")
        checks.check(isinstance(item.get("row_count"), int) and item.get("row_count") > 0, f"{item.get('id')} row count invalid")
        checks.check(isinstance(item.get("required_proof"), str) and item.get("required_proof"), f"{item.get('id')} proof text missing")

    checks.check(isinstance(closed_obligations, list) and len(closed_obligations) == 5, "closed obligation list length changed")
    checks.check(
        [item.get("id") for item in closed_obligations if isinstance(item, dict)] == EXPECTED_CLOSED_OBLIGATIONS,
        "closed obligation IDs changed",
    )
    for item in closed_obligations:
        if not isinstance(item, dict):
            checks.check(False, "closed obligation entry is not an object")
            continue
        checks.check(item.get("status") == "closed", f"{item.get('id')} is not closed")
        expected_rows = {
            "translational_balance_identity": 18,
            "rotational_balance_identity": 18,
            "multiplier_wrench_consistency": 36,
            "smooth_force_lift_consistency": 36,
            "symbolic_runtime_row_equivalence": 36,
        }.get(item.get("id"))
        checks.check(item.get("row_count") == expected_rows, f"{item.get('id')} row count changed")
        expected_evidence = {
            "translational_balance_identity": "NEWTON_EULER_BALANCE_IDENTITY_AUDIT.md/json",
            "rotational_balance_identity": "NEWTON_EULER_BALANCE_IDENTITY_AUDIT.md/json",
            "multiplier_wrench_consistency": "NEWTON_EULER_VIRTUAL_WORK_WRENCH_AUDIT.md/json",
            "smooth_force_lift_consistency": "SMOOTH_FORCE_LIFT_CERTIFICATE.md/json",
            "symbolic_runtime_row_equivalence": "NEWTON_EULER_ROW_ORDERING_SCALING_AD_AUDIT.md/json",
        }.get(item.get("id"))
        checks.check(item.get("closure_evidence") == expected_evidence, f"{item.get('id')} closure evidence changed")

    checks.check(closure.get("open_obligation_count") == 1, "open obligation count changed")
    checks.check(
        closure.get("open_obligation_scope") == "symbolic_primitive_certificate_route_not_active_direct_pc2",
        "open obligation scope changed",
    )
    checks.check(closure.get("active_direct_pc2_closed") is True, "active direct PC2 closure marker missing")
    checks.check(
        closure.get("active_direct_stage_residual_O_h7_implementation_defect_proved") is True,
        "active direct O(h^7) implementation-defect marker missing",
    )
    checks.check(closure.get("active_direct_dynamic_zero_residual_rows") == 36, "active direct zero-row count changed")
    checks.check(closure.get("active_direct_forbidden_shortcuts_used") == 0, "active direct shortcut count changed")
    checks.check(closure.get("closed_obligation_count") == 5, "closed obligation count changed")
    checks.check(
        closure.get("closed_obligation_ids") == EXPECTED_CLOSED_OBLIGATIONS,
        "closed obligation id summary changed",
    )
    checks.check(closure.get("symbolic_target_inventory_complete") is True, "symbolic target inventory marker missing")
    checks.check(closure.get("balance_identity_audit_complete") is True, "balance identity audit marker missing")
    checks.check(
        closure.get("newton_euler_symbolic_defect_certificate_complete") is False,
        "Newton-Euler symbolic certificate overclaimed",
    )
    checks.check(
        closure.get("stage_residual_O_h7_implementation_defect_proved") is False,
        "symbolic/primitive route O(h^7) implementation defect overclaimed",
    )
    checks.check(
        closure.get("stage_residual_O_h7_implementation_defect_proved_scope")
        == "symbolic_primitive_certificate_route_only",
        "stage-residual proof scope changed",
    )
    checks.check(closure.get("dynamic_symbolic_oracle_complete") is False, "dynamic symbolic oracle overclaimed")
    checks.check(closure.get("full_tfe_stage_replacement") is False, "full TFE replacement overclaimed")

    checks.check(execution.get("default_1e-4_required") is False, "gate requires default 1e-4")
    checks.check(execution.get("run_v047_invoked") is False, "gate invoked run_v047")
    checks.check(execution.get("v048_runner_invoked") is False, "gate invoked v048 runner")
    checks.check(execution.get("heavy_numerical_run_invoked") is False, "gate invoked heavy numerical run")

    full_oracle = dynamic_oracle.get("full_independent_formula_row_oracle", {})
    checks.check(full_oracle.get("checked") is True, "dynamic oracle full formula rows not checked")
    checks.check(full_oracle.get("row_count") == 132, "dynamic oracle full row count changed")
    checks.check(full_oracle.get("added_row_family") == "newton_euler_weak_balance", "dynamic oracle added family changed")
    checks.check(
        dynamic_oracle.get("formula_row_ad_jacobian_oracle", {}).get("probe_count") == 3,
        "dynamic oracle AD probe count changed",
    )
    checks.check(
        kinematic_defect.get("proof_scope", {}).get("certified_row_count") == 96,
        "kinematic certificate support changed",
    )
    checks.check(
        kinematic_defect.get("proof_scope", {}).get("excluded_row_family") == "newton_euler_weak_balance",
        "kinematic certificate excluded family changed",
    )
    checks.check(
        symbolic_target_audit.get("schema") == "newton-euler-symbolic-target-audit-v1",
        "symbolic target audit schema changed",
    )
    checks.check(symbolic_target_audit.get("row_count") == 36, "symbolic target audit row count changed")
    checks.check(symbolic_target_audit.get("translational_row_count") == 18, "symbolic target translational rows changed")
    checks.check(symbolic_target_audit.get("rotational_row_count") == 18, "symbolic target rotational rows changed")
    checks.check(
        symbolic_target_audit.get("closure_boundary", {}).get("stage_residual_O_h7_implementation_defect_proved")
        is False,
        "symbolic target audit overclaims O(h^7)",
    )

    checks.check(
        theorem.get("newton_euler_defect_obligation_gate_checked") is True,
        "proof contract missing Newton-Euler obligation marker",
    )
    checks.check(
        theorem.get("newton_euler_defect_obligation_rows") == 36,
        "proof contract Newton-Euler row count changed",
    )
    checks.check(
        theorem.get("newton_euler_defect_open_obligation_count") == 1,
        "proof contract open obligation count changed",
    )
    checks.check(
        theorem.get("newton_euler_defect_closed_obligation_count") == 5,
        "proof contract closed obligation count changed",
    )
    checks.check(
        theorem.get("newton_euler_defect_closed_obligation_ids") == EXPECTED_CLOSED_OBLIGATIONS,
        "proof contract closed obligation ids changed",
    )
    checks.check(
        theorem.get("newton_euler_symbolic_defect_certificate_complete") is False,
        "proof contract overclaims Newton-Euler certificate",
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
    checks.check(theorem.get("dynamic_symbolic_oracle_complete") is False, "proof contract overclaims symbolic oracle")

    checks.check(
        "newton_euler_dynamic_defect_obligation_gate_added" in b1.get("partial_progress", []),
        "B1 missing Newton-Euler obligation progress marker",
    )
    checks.check(
        "NEWTON_EULER_DEFECT_OBLIGATION_GATE.md" in b1.get("partial_progress_evidence", []),
        "B1 missing Newton-Euler obligation MD evidence",
    )
    checks.check(
        "newton_euler_dynamic_defect_obligations_decomposed" in b3.get("partial_progress", []),
        "B3 missing Newton-Euler obligation progress marker",
    )
    checks.check(
        "NEWTON_EULER_DEFECT_OBLIGATION_GATE.json" in b3.get("partial_progress_evidence", []),
        "B3 missing Newton-Euler obligation JSON evidence",
    )

    checks.check(
        "NEWTON_EULER_DEFECT_OBLIGATION_GATE.md" in manifest.get("evidence_anchors", []),
        "manifest missing Newton-Euler obligation gate",
    )
    checks.check(
        "NEWTON_EULER_DEFECT_OBLIGATION_GATE.json" in manifest.get("evidence_anchors", []),
        "manifest missing Newton-Euler obligation gate JSON",
    )
    checks.check(
        "NEWTON_EULER_SYMBOLIC_TARGET_AUDIT.md" in manifest.get("evidence_anchors", []),
        "manifest missing Newton-Euler symbolic target audit",
    )
    checks.check(
        "NEWTON_EULER_SYMBOLIC_TARGET_AUDIT.json" in manifest.get("evidence_anchors", []),
        "manifest missing Newton-Euler symbolic target audit JSON",
    )
    checks.check(
        "validate_newton_euler_defect_obligation_gate.py" in manifest.get("validators", []),
        "manifest missing Newton-Euler obligation validator",
    )
    checks.check(
        "validate_newton_euler_symbolic_target_audit.py" in manifest.get("validators", []),
        "manifest missing Newton-Euler symbolic target audit validator",
    )
    checks.check(
        "NEWTON_EULER_BALANCE_IDENTITY_AUDIT.md" in manifest.get("evidence_anchors", []),
        "manifest missing Newton-Euler balance identity audit",
    )
    checks.check(
        "NEWTON_EULER_BALANCE_IDENTITY_AUDIT.json" in manifest.get("evidence_anchors", []),
        "manifest missing Newton-Euler balance identity audit JSON",
    )
    checks.check(
        "validate_newton_euler_balance_identity_audit.py" in manifest.get("validators", []),
        "manifest missing Newton-Euler balance identity validator",
    )

    for token in [
        "Newton-Euler Defect Obligation Gate",
        "D5 SYMBOLIC/PRIMITIVE ROUTE OPEN; ACTIVE DIRECT PC2 CLOSED - NOT SUBMISSION READY",
        "`newton_euler_weak_balance`",
        "Symbolic/primitive-route open obligation count: `1`",
        "Active direct PC2 closed: `True`",
        "Active direct dynamic zero residual rows: `36`",
        "Closed obligation count: `5`",
        "Closed obligation ids: `translational_balance_identity, rotational_balance_identity, multiplier_wrench_consistency, smooth_force_lift_consistency, symbolic_runtime_row_equivalence`",
        "Symbolic target inventory complete: `true`",
        "NEWTON_EULER_SYMBOLIC_TARGET_AUDIT.md/json",
        "NEWTON_EULER_BALANCE_IDENTITY_AUDIT.md/json",
        "`translational_newton_balance`: 18 rows",
        "`rotational_euler_balance`: 18 rows",
        "translational_balance_identity",
        "rotational_balance_identity",
        "Closed Sub-Obligations",
        "multiplier_wrench_consistency",
        "smooth_force_lift_consistency",
        "gauss_stage_dynamic_defect_rate",
        "symbolic_runtime_row_equivalence",
        "symbolic_primitive_stage_residual_O_h7_certificate_complete",
        "dynamic_symbolic_oracle_complete",
        "remains conditional under retained P1, P2, and P3 theorem interfaces",
        "the separate P6 solver-scale interface, and the P4 binding convention",
        "P7 residual-to-error nonpromotion recorded elsewhere",
        "default_1e-4_required=false",
        "validate_newton_euler_defect_obligation_gate.py",
    ]:
        checks.check(contains_normalized(gate_md, token), f"gate markdown missing token: {token}")

    forbidden = set(gate.get("forbidden_claims", []))
    for token in [
        "newton_euler_symbolic_defect_certificate_complete_true",
        "symbolic_primitive_stage_residual_O_h7_certificate_complete_true",
        "dynamic_symbolic_oracle_complete_true",
        "full_tfe_stage_replacement_true",
        "external_superiority_claim_true",
        "submission_ready_true",
        "default_1e-4_required_true",
    ]:
        checks.check(token in forbidden, f"forbidden claim missing: {token}")

    if checks.errors:
        print("newton_euler_defect_obligation_gate=FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("newton_euler_defect_obligation_gate=PASS")
    print("accepted_method=Gauss6/FullVA")
    print("accepted_residual=residual_cylindrical_chain")
    print("row_family=newton_euler_weak_balance")
    print("dynamic_row_count=36")
    print("translational_balance_rows=18")
    print("rotational_balance_rows=18")
    print("symbolic_primitive_open_obligation_count=1")
    print("active_direct_pc2_closed=True")
    print("closed_obligation_count=5")
    print("newton_euler_symbolic_defect_certificate_complete=False")
    print("symbolic_primitive_stage_residual_O_h7_certificate_complete=False")
    print("dynamic_symbolic_oracle_complete=False")
    print("full_tfe_stage_replacement=False")
    print("default_1e-4=False")
    print("run_v047_invoked=False")
    print("v048_runner_invoked=False")
    print("submission_ready=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
