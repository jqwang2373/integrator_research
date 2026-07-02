#!/usr/bin/env python3
"""Read-only static validator for the accepted v047 implementation path."""

from __future__ import annotations

import ast
import json
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
ROOT = PAPER.parent
RUN = ROOT / "v047_cylindrical_chain_pipeline" / "run_v047.py"
SUMMARY = ROOT / "v047_cylindrical_chain_pipeline" / "results" / "summary_v047.json"
AUDIT_MD = PAPER / "IMPLEMENTATION_PATH_AUDIT.md"
AUDIT_JSON = PAPER / "IMPLEMENTATION_PATH_AUDIT.json"
DYNAMIC_GATE = PAPER / "DYNAMIC_ROW_ORACLE_GATE.json"
PROOF_GATE = PAPER / "CMAME_PROOF_CONTRACT_GATE.json"
BLOCKER_GATE = PAPER / "CMAME_BLOCKER_CLOSURE_GATE.json"
MANIFEST = PAPER / "SUBMISSION_ARTIFACT_MANIFEST.json"

EXPECTED_ROW_FAMILIES = [
    ("translational_position_weak_defect", 0, 6, 18),
    ("rotational_lie_position_weak_defect", 6, 6, 18),
    ("translational_velocity_weak_defect", 12, 6, 18),
    ("angular_velocity_weak_defect", 18, 6, 18),
    ("newton_euler_weak_balance", 24, 12, 36),
    ("lower_pair_index3_weak_constraints", 36, 8, 24),
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


def require_tokens(checks: Checks, text: str, tokens: list[str], label: str) -> None:
    for token in tokens:
        checks.check(contains_normalized(text, token), f"{label} missing token: {token}")


def function_source(run_text: str, tree: ast.Module, name: str) -> str:
    lines = run_text.splitlines()
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == name:
            end = getattr(node, "end_lineno", node.lineno)
            return "\n".join(lines[node.lineno - 1 : end])
    return ""


def blocker_by_id(blocker_gate: dict[str, Any], blocker_id: str) -> dict[str, Any]:
    for blocker in blocker_gate.get("blockers", []):
        if isinstance(blocker, dict) and blocker.get("id") == blocker_id:
            return blocker
    return {}


def main() -> int:
    checks = Checks()
    try:
        run_text = read_text(RUN)
        tree = ast.parse(run_text)
        audit = read_json(AUDIT_JSON)
        audit_md = read_text(AUDIT_MD)
        dynamic_gate = read_json(DYNAMIC_GATE)
        proof_gate = read_json(PROOF_GATE)
        blocker_gate = read_json(BLOCKER_GATE)
        summary = read_json(SUMMARY)
        manifest = read_json(MANIFEST)
    except Exception as exc:  # noqa: BLE001 - concise CLI failure.
        print(f"implementation_path_audit=FAIL\n- {exc}")
        return 1

    function_names = {node.name for node in tree.body if isinstance(node, ast.FunctionDef)}
    assigned_names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    assigned_names.add(target.id)

    gauss_step_src = function_source(run_text, tree, "gauss_step")
    integrate_src = function_source(run_text, tree, "integrate")
    run_case_src = function_source(run_text, tree, "run_case")
    solve_stage_src = function_source(run_text, tree, "solve_gauss_stage_x")
    warm_jax_src = function_source(run_text, tree, "warm_jax")

    checks.check(audit.get("schema") == "implementation-path-audit-v1", "audit schema changed")
    checks.check(
        audit.get("status") == "read_only_static_code_path_checked_not_symbolic_proof",
        "audit status changed",
    )
    checks.check(audit.get("submission_ready") is False, "audit overclaims submission readiness")
    checks.check(audit.get("accepted_method") == "Gauss6/FullVA", "accepted method changed")
    checks.check(audit.get("source") == "../v047_cylindrical_chain_pipeline/run_v047.py", "source path changed")

    execution = audit.get("execution_policy", {})
    checks.check(execution.get("read_only_static_audit") is True, "audit lost read-only marker")
    checks.check(execution.get("default_step_policy") == "coarse_first_no_default_1e-4", "default policy changed")
    checks.check(execution.get("strict_public_policy_1e-4") == "opt_in_only", "strict policy changed")
    checks.check(execution.get("default_1e-4_required") is False, "audit incorrectly requires default 1e-4")
    checks.check(execution.get("heavy_numerical_run_invoked") is False, "audit invoked heavy numerical run")
    checks.check(execution.get("run_v047_invoked") is False, "audit invoked run_v047")
    checks.check(execution.get("v048_runner_invoked") is False, "audit invoked v048 runner")

    for token in [
        "N_BODIES = 2",
        "N_JOINTS = 2",
        "N_STAGES = 3",
        "BODY_SIZE = 18",
        "LAMBDA_SIZE = 4",
        "STAGE_SIZE = N_BODIES * BODY_SIZE + N_JOINTS * LAMBDA_SIZE",
        "DIM = N_STAGES * STAGE_SIZE",
        "R_VALUE = jax.jit(residual_cylindrical_chain)",
        "R_JAC = jax.jit(jax.jacfwd(residual_cylindrical_chain, argnums=0))",
    ]:
        checks.check(token in run_text, f"run_v047.py missing source token: {token}")

    for name in ["residual_cylindrical_chain", "gauss_step", "integrate", "run_case", "solve_gauss_stage_x", "warm_jax"]:
        checks.check(name in function_names, f"run_v047.py missing function: {name}")
    checks.check("R_VALUE" in assigned_names, "run_v047.py missing R_VALUE assignment")
    checks.check("R_JAC" in assigned_names, "run_v047.py missing R_JAC assignment")

    checks.check("np.asarray(R_VALUE" in gauss_step_src, "gauss_step does not evaluate R_VALUE")
    checks.check('"dense_jacfwd_csr"' in gauss_step_src, "gauss_step lost dense_jacfwd_csr branch")
    checks.check("np.asarray(R_JAC" in gauss_step_src, "gauss_step dense branch does not use R_JAC")
    checks.check("next_state_from_stages" in gauss_step_src, "gauss_step no longer advances from stages")
    checks.check("gauss_step(" in integrate_src, "integrate does not call gauss_step")
    checks.check("integrate(params, solver" in run_case_src, "run_case does not call integrate on solver path")
    checks.check("np.asarray(R_VALUE" in solve_stage_src, "solve_gauss_stage_x does not evaluate R_VALUE")
    checks.check("np.asarray(R_JAC" in solve_stage_src, "solve_gauss_stage_x does not evaluate R_JAC")
    checks.check("np.asarray(R_VALUE" in warm_jax_src and "np.asarray(R_JAC" in warm_jax_src, "warm_jax does not warm R_VALUE/R_JAC")

    shape = audit.get("shape_contract", {})
    checks.check(shape.get("n_bodies") == 2, "n_bodies changed")
    checks.check(shape.get("n_joints") == 2, "n_joints changed")
    checks.check(shape.get("n_stages") == 3, "n_stages changed")
    checks.check(shape.get("body_size") == 18, "body_size changed")
    checks.check(shape.get("lambda_size") == 4, "lambda_size changed")
    checks.check(shape.get("stage_size") == 44, "stage_size changed")
    checks.check(shape.get("dim") == 132, "dim changed")

    rows = audit.get("row_families", [])
    checks.check(len(rows) == len(EXPECTED_ROW_FAMILIES), "row family count changed")
    for row, expected in zip(rows, EXPECTED_ROW_FAMILIES):
        name, offset, width, total = expected
        checks.check(row.get("name") == name, f"row family name changed: {name}")
        checks.check(row.get("offset") == offset, f"row family offset changed: {name}")
        checks.check(row.get("width") == width, f"row family width changed: {name}")
        checks.check(row.get("total_rows") == total, f"row family total changed: {name}")

    audit_results = audit.get("audit_results", {})
    for key in [
        "residual_symbol_found",
        "value_symbol_found",
        "jacobian_symbol_found",
        "dense_branch_uses_r_jac",
        "stage_solve_uses_r_jac",
        "integrate_calls_gauss_step",
        "run_case_calls_integrate",
        "warmup_uses_r_value_and_r_jac",
        "implementation_path_check_for_132_row_residual",
    ]:
        checks.check(audit_results.get(key) is True, f"audit result changed: {key}")
    checks.check(audit_results.get("summary_dimension_contract") == 132, "summary dimension contract changed")

    proof_boundary = audit.get("proof_boundary", {})
    checks.check(proof_boundary.get("implementation_path_check_for_132_row_residual") is True, "implementation path check lost")
    checks.check(proof_boundary.get("runtime_formula_row_oracle_complete") is True, "runtime formula oracle marker lost")
    checks.check(proof_boundary.get("runtime_ad_oracle_complete") is True, "runtime AD oracle marker lost")
    for key in [
        "independent_symbolic_row_oracle_complete",
        "eta_h_O_h7_solver_policy_evidence",
        "full_tfe_stage_replacement",
        "external_superiority_claim",
    ]:
        checks.check(proof_boundary.get(key) is False, f"audit overclaims {key}")
    checks.check(
        proof_boundary.get("stage_residual_O_h7_implementation_defect_proved_by_this_static_path_audit") is False,
        "static path audit overclaims O(h^7) implementation-defect proof",
    )

    dynamic_acceptance = dynamic_gate.get("acceptance_boundary", {})
    checks.check(dynamic_acceptance.get("full_independent_formula_rows_checked") is True, "dynamic gate lost full row check")
    checks.check(dynamic_acceptance.get("formula_row_ad_jacobian_checked") is True, "dynamic gate lost AD Jacobian check")
    checks.check(dynamic_acceptance.get("independent_symbolic_row_oracle_complete") is False, "dynamic gate overclaims symbolic oracle")
    checks.check(dynamic_acceptance.get("stage_residual_O_h7_implementation_defect_proved") is False, "dynamic gate overclaims h7 defect")

    theorem = proof_gate.get("theorem_contract", {})
    checks.check(theorem.get("implementation_path_audit_checked") is True, "proof gate lost implementation path audit marker")
    checks.check(
        theorem.get("implementation_path_check_for_132_row_residual") is True,
        "proof gate lost implementation path check marker",
    )
    checks.check(
        theorem.get("stage_residual_O_h7_implementation_defect_proved") is True,
        "proof gate lost direct-substitution h7 defect proof",
    )
    checks.check(
        theorem.get("newton_euler_stage_defect_certificate_closed_by_direct_substitution") is True,
        "proof gate lost Newton-Euler direct-substitution closure marker",
    )
    checks.check(theorem.get("eta_h_O_h7_solver_policy_evidence") is False, "proof gate overclaims eta_h evidence")

    b1 = blocker_by_id(blocker_gate, "B1")
    checks.check("implementation_path_audit_added" in b1.get("partial_progress", []), "B1 lost path audit progress marker")
    checks.check(
        "implementation_path_check_for_132_row_residual" in b1.get("partial_progress", []),
        "B1 lost path check progress marker",
    )
    for artifact in ["IMPLEMENTATION_PATH_AUDIT.md", "IMPLEMENTATION_PATH_AUDIT.json", "validate_implementation_path_audit.py"]:
        checks.check(artifact in b1.get("partial_progress_evidence", []), f"B1 missing path audit evidence: {artifact}")
    checks.check(
        "implementation_path_check_for_132_row_residual" not in b1.get("required_to_close", []),
        "B1 still lists implementation path check as required to close",
    )

    checks.check(summary.get("model", {}).get("dimension") == 132, "summary model dimension changed")
    checks.check(summary.get("model", {}).get("method") == "two_body_cylindrical_chain_gauss6_fullva", "summary method changed")

    checks.check(manifest.get("implementation_path_audit") == "IMPLEMENTATION_PATH_AUDIT.md", "manifest path audit missing")
    checks.check(manifest.get("implementation_path_audit_json") == "IMPLEMENTATION_PATH_AUDIT.json", "manifest path audit JSON missing")
    checks.check("IMPLEMENTATION_PATH_AUDIT.md" in manifest.get("evidence_anchors", []), "manifest path audit anchor missing")
    checks.check("IMPLEMENTATION_PATH_AUDIT.json" in manifest.get("evidence_anchors", []), "manifest path audit JSON anchor missing")
    checks.check("validate_implementation_path_audit.py" in manifest.get("validators", []), "manifest path audit validator missing")

    require_tokens(
        checks,
        audit_md,
        [
            "Implementation Path Audit",
            "READ-ONLY STATIC CODE PATH CHECKED - NOT SYMBOLIC PROOF",
            "implementation_path_check_for_132_row_residual",
            "does not run `run_v047.py`",
            "default `1e-4` campaign",
            "residual_cylindrical_chain",
            "R_VALUE = jax.jit(residual_cylindrical_chain)",
            "R_JAC = jax.jit(jax.jacfwd(residual_cylindrical_chain, argnums=0))",
            "gauss_step(..., solver=\"dense_jacfwd_csr\", ...)",
            "integrate",
            "run_case",
            "DIM=132",
            "runtime_formula_row_oracle_complete=true",
            "runtime_ad_oracle_complete=true",
            "independent_symbolic_row_oracle_complete=false",
            "stage_residual_O_h7_implementation_defect_proved_by_this_static_path_audit=false",
            "eta_h_O_h7_solver_policy_evidence=false",
            "full_tfe_stage_replacement=false",
            "validate_implementation_path_audit.py",
        ],
        "IMPLEMENTATION_PATH_AUDIT.md",
    )

    forbidden = set(audit.get("forbidden_claims", []))
    for token in [
        "independent_symbolic_row_oracle_complete_true",
        "stage_residual_O_h7_implementation_defect_proved_by_this_static_path_audit_true",
        "eta_h_O_h7_solver_policy_evidence_true",
        "full_tfe_stage_replacement_true",
        "run_v047_invoked_true",
        "default_1e-4_required_true",
        "submission_ready_true",
    ]:
        checks.check(token in forbidden, f"forbidden claim missing: {token}")

    if checks.errors:
        print("implementation_path_audit=FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("implementation_path_audit=PASS")
    print("accepted_residual=residual_cylindrical_chain")
    print("accepted_jacobian=R_JAC_jacfwd_argnums0")
    print("implementation_path_check_for_132_row_residual=True")
    print("stage_rows=132")
    print("runtime_formula_row_oracle_complete=True")
    print("runtime_ad_oracle_complete=True")
    print("independent_symbolic_row_oracle_complete=False")
    print("stage_residual_O_h7_implementation_defect_proved_by_this_static_path_audit=False")
    print("eta_h_O_h7_solver_policy_evidence=False")
    print("default_1e-4=False")
    print("run_v047_invoked=False")
    print("v048_runner_invoked=False")
    print("submission_ready=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
