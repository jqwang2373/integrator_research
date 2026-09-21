#!/usr/bin/env python3
"""Validate the finite scaled-tolerance solver probe."""

from __future__ import annotations

import csv
import json
import math
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
PROBE_JSON = PAPER / "PROOF_SOLVER_SCALED_TOLERANCE_PROBE.json"
PROBE_CSV = PAPER / "PROOF_SOLVER_SCALED_TOLERANCE_PROBE.csv"
PROBE_MD = PAPER / "PROOF_SOLVER_SCALED_TOLERANCE_PROBE.md"
SOLVER_AUDIT_JSON = PAPER / "PROOF_SOLVER_SCALE_AUDIT.json"
SOLVER_AUDIT_MD = PAPER / "PROOF_SOLVER_SCALE_AUDIT.md"
MANIFEST = PAPER / "SUBMISSION_ARTIFACT_MANIFEST.json"

EXPECTED_H = [0.04, 0.02, 0.01, 0.005]
EXPECTED_C_ETA = 1.0e4


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


def close(left: Any, right: Any, tol: float = 1.0e-12) -> bool:
    left_f = float(left)
    right_f = float(right)
    return abs(left_f - right_f) <= tol * max(1.0, abs(left_f), abs(right_f))


def contains_normalized(text: str, token: str) -> bool:
    return token in text or " ".join(token.split()) in " ".join(text.split())


def main() -> int:
    checks = Checks()
    try:
        probe = read_json(PROBE_JSON)
        audit = read_json(SOLVER_AUDIT_JSON)
        manifest = read_json(MANIFEST)
        probe_md = read_text(PROBE_MD)
        audit_md = read_text(SOLVER_AUDIT_MD)
        with PROBE_CSV.open(newline="", encoding="utf-8") as handle:
            csv_rows = list(csv.DictReader(handle))
    except Exception as exc:  # noqa: BLE001
        print(f"proof_solver_scaled_tolerance_probe=FAIL\n- {exc}")
        return 1

    rows = probe.get("rows", [])
    checks.check(probe.get("schema") == "proof-solver-scaled-tolerance-probe-v1", "probe schema changed")
    checks.check(
        probe.get("status") == "finite_scaled_tolerance_probe_recorded_not_theorem_closure",
        "probe status changed",
    )
    checks.check(probe.get("case") == "cylindrical_smooth", "probe case changed")
    checks.check(probe.get("accepted_method") == "Gauss6/FullVA", "accepted method changed")
    checks.check(probe.get("h_values") == EXPECTED_H, "probe h values changed")
    checks.check(close(probe.get("c_eta"), EXPECTED_C_ETA), "c_eta changed")
    checks.check(probe.get("row_count") == len(EXPECTED_H), "row count changed")
    checks.check(probe.get("ok_row_count") == len(EXPECTED_H), "ok row count changed")
    checks.check(len(rows) == len(EXPECTED_H), "rows length changed")
    checks.check(len(csv_rows) == len(EXPECTED_H), "CSV row count changed")
    checks.check(probe.get("scaled_policy_exercised") is True, "scaled policy was not exercised")
    checks.check(probe.get("theorem_level_solver_proof_closed") is False, "probe overclaims theorem closure")
    checks.check(probe.get("dynamic_symbolic_oracle_complete") is False, "probe overclaims symbolic oracle")
    checks.check(
        probe.get("stage_residual_O_h7_implementation_defect_proved") is False,
        "probe overclaims implementation defect",
    )
    checks.check(probe.get("submission_ready") is False, "probe overclaims submission")

    max_ratio = 0.0
    for row, h in zip(rows, EXPECTED_H):
        checks.check(row.get("case") == "cylindrical_smooth", "row case changed")
        checks.check(close(row.get("h"), h), f"h row changed: {row.get('h')} != {h}")
        checks.check(close(row.get("c_eta"), EXPECTED_C_ETA), "row c_eta changed")
        checks.check(row.get("status") == "ok", f"row status not ok for h={h}")
        eta_target = EXPECTED_C_ETA * math.pow(h, 7)
        checks.check(close(row.get("eta_target"), eta_target, tol=1.0e-10), f"eta target changed for h={h}")
        checks.check(float(row.get("final_residual_norm", math.inf)) <= eta_target, f"residual exceeds target for h={h}")
        ratio = float(row.get("final_residual_over_h7", math.inf))
        max_ratio = max(max_ratio, ratio)
        checks.check(ratio <= EXPECTED_C_ETA, f"residual/h^7 exceeds c_eta for h={h}")
        checks.check(int(row.get("final_jacobian_rank", 0)) == 132, f"Jacobian rank changed for h={h}")
        checks.check(float(row.get("final_jacobian_condition", math.inf)) > 1.0, f"Jacobian condition invalid for h={h}")

    checks.check(close(probe.get("max_final_residual_over_h7"), max_ratio), "max residual ratio changed")

    execution = probe.get("execution_policy", {})
    checks.check(execution.get("imports_accepted_residual_functions") is True, "probe no longer imports accepted residuals")
    checks.check(execution.get("heavy_numerical_run_invoked") is False, "probe invoked heavy numerical run")
    checks.check(execution.get("default_1e-4_required") is False, "probe requires default 1e-4")
    checks.check(execution.get("run_v047_invoked") is False, "probe invoked run_v047")

    finite_probe = audit.get("finite_scaled_tolerance_probe", {})
    checks.check(
        finite_probe.get("schema") == "proof-solver-scaled-tolerance-probe-v1",
        "solver audit missing finite probe schema",
    )
    checks.check(
        finite_probe.get("source_json") == "PROOF_SOLVER_SCALED_TOLERANCE_PROBE.json",
        "solver audit missing probe JSON path",
    )
    checks.check(
        finite_probe.get("source_csv") == "PROOF_SOLVER_SCALED_TOLERANCE_PROBE.csv",
        "solver audit missing probe CSV path",
    )
    checks.check(
        finite_probe.get("source_md") == "PROOF_SOLVER_SCALED_TOLERANCE_PROBE.md",
        "solver audit missing probe MD path",
    )
    checks.check(finite_probe.get("row_count") == len(EXPECTED_H), "solver audit finite probe row count changed")
    checks.check(finite_probe.get("ok_row_count") == len(EXPECTED_H), "solver audit finite probe ok count changed")
    checks.check(finite_probe.get("scaled_policy_exercised") is True, "solver audit finite probe policy marker changed")
    checks.check(
        finite_probe.get("theorem_level_solver_proof_closed") is False,
        "solver audit finite probe overclaims theorem closure",
    )
    checks.check(
        close(finite_probe.get("max_final_residual_over_h7"), max_ratio),
        "solver audit finite probe max ratio changed",
    )
    boundary = audit.get("proof_boundary", {})
    checks.check(
        boundary.get("finite_scaled_tolerance_probe_recorded") is True,
        "solver audit proof boundary missing finite probe marker",
    )
    checks.check(
        boundary.get("scaled_tolerance_sweep_recorded") is False,
        "solver audit overclaims theorem-level scaled sweep",
    )
    checks.check(
        boundary.get("eta_h_O_h7_solver_policy_evidence") is False,
        "solver audit overclaims eta_h proof evidence",
    )

    for file_label in [
        "PROOF_SOLVER_SCALED_TOLERANCE_PROBE.md",
        "PROOF_SOLVER_SCALED_TOLERANCE_PROBE.json",
        "PROOF_SOLVER_SCALED_TOLERANCE_PROBE.csv",
    ]:
        checks.check(file_label in manifest.get("evidence_anchors", []), f"manifest missing {file_label}")
    checks.check(
        "validate_proof_solver_scaled_tolerance_probe.py" in manifest.get("validators", []),
        "manifest missing scaled-tolerance probe validator",
    )

    for token in [
        "Proof Solver Scaled-Tolerance Probe",
        "eta_h = c_eta h^7",
        "does not invoke `run_v047.py`",
        "Theorem-level solver proof closed: `False`",
        "validate_proof_solver_scaled_tolerance_probe.py",
    ]:
        checks.check(contains_normalized(probe_md, token), f"probe MD missing token: {token}")
    for token in [
        "finite scaled-tolerance probe",
        "PROOF_SOLVER_SCALED_TOLERANCE_PROBE.json",
        "theorem-level scaled tolerance sweep",
    ]:
        checks.check(contains_normalized(audit_md, token), f"solver audit MD missing token: {token}")

    forbidden = set(probe.get("forbidden_claims", []))
    for claim in [
        "theorem_level_solver_proof_closed_true",
        "dynamic_symbolic_oracle_complete_true",
        "stage_residual_O_h7_implementation_defect_proved_true",
        "submission_ready_true",
        "external_superiority_claim_true",
    ]:
        checks.check(claim in forbidden, f"probe forbidden claim missing: {claim}")

    if checks.errors:
        print("proof_solver_scaled_tolerance_probe=FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("proof_solver_scaled_tolerance_probe=PASS")
    print(f"rows_ok={probe.get('ok_row_count')}/{probe.get('row_count')}")
    print(f"max_final_residual_over_h7={max_ratio:.6e}")
    print("theorem_level_solver_proof_closed=False")
    print("scaled_tolerance_sweep_recorded=False")
    print("eta_h_O_h7_solver_policy_evidence=False")
    print("default_1e-4=False")
    print("run_v047_invoked=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
