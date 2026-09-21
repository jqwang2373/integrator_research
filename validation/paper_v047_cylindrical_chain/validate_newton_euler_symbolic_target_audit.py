#!/usr/bin/env python3
"""Validate the Newton-Euler symbolic target audit."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
WORK = PAPER.parent
from paper_paths import work_path
AUDIT_JSON = PAPER / "NEWTON_EULER_SYMBOLIC_TARGET_AUDIT.json"
AUDIT_MD = PAPER / "NEWTON_EULER_SYMBOLIC_TARGET_AUDIT.md"
OBLIGATION_GATE = PAPER / "NEWTON_EULER_DEFECT_OBLIGATION_GATE.json"
DYNAMIC_ORACLE = PAPER / "DYNAMIC_ROW_ORACLE_GATE.json"
MANIFEST = PAPER / "SUBMISSION_ARTIFACT_MANIFEST.json"

EXPECTED_OBLIGATIONS = [
    "translational_balance_identity",
    "rotational_balance_identity",
    "multiplier_wrench_consistency",
    "smooth_force_lift_consistency",
    "gauss_stage_dynamic_defect_rate",
    "symbolic_runtime_row_equivalence",
]
SHARED_ROW_OBLIGATIONS = [
    "multiplier_wrench_consistency",
    "smooth_force_lift_consistency",
    "gauss_stage_dynamic_defect_rate",
    "symbolic_runtime_row_equivalence",
]
RUNTIME_SOURCE_COMPONENT_LAYOUT = [
    ("body0_translational_balance_source", 0, 3, 0, "translational_newton_balance", "translational_balance_identity"),
    ("body0_rotational_balance_source", 3, 3, 0, "rotational_euler_balance", "rotational_balance_identity"),
    ("body1_translational_balance_source", 6, 3, 1, "translational_newton_balance", "translational_balance_identity"),
    ("body1_rotational_balance_source", 9, 3, 1, "rotational_euler_balance", "rotational_balance_identity"),
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


def validate_source_anchor(checks: Checks, anchor: dict[str, Any], role: str) -> None:
    checks.check(anchor.get("role") == role, f"source anchor role changed for {role}")
    file_name = anchor.get("file")
    needle = anchor.get("needle")
    line_no = anchor.get("line")
    checks.check(file_name == "v047_cylindrical_chain_pipeline/run_v047.py", f"source anchor file changed for {role}")
    checks.check(isinstance(needle, str) and bool(needle), f"source anchor needle missing for {role}")
    checks.check(isinstance(line_no, int) and line_no > 0, f"source anchor line missing for {role}")
    if isinstance(file_name, str) and isinstance(needle, str) and isinstance(line_no, int):
        path = work_path(file_name)
        checks.check(path.exists(), f"source anchor target missing for {role}: {file_name}")
        if path.exists():
            lines = read_text(path).splitlines()
            checks.check(line_no <= len(lines), f"source anchor line out of range for {role}")
            if line_no <= len(lines):
                checks.check(needle in lines[line_no - 1], f"source anchor needle not found for {role}")


def contains_normalized(text: str, token: str) -> bool:
    return token in text or " ".join(token.split()) in " ".join(text.split())


def expected_global_rows() -> list[int]:
    rows = []
    for stage in range(3):
        base = stage * 44 + 24
        rows.extend(range(base, base + 12))
    return rows


def expected_row_targets() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for stage in range(3):
        base = stage * 44 + 24
        for source_name, source_offset, source_width, body, block, identity in RUNTIME_SOURCE_COMPONENT_LAYOUT:
            for component_index, component in enumerate(["x", "y", "z"]):
                local = source_offset + component_index
                rows.append(
                    {
                        "global_row": base + local,
                        "stage": stage,
                        "body": body,
                        "component": component,
                        "balance_block": block,
                        "local_block_row": local,
                        "runtime_source_component": source_name,
                        "runtime_source_component_offset": source_offset,
                        "runtime_source_component_width": source_width,
                        "runtime_source_component_index": component_index,
                        "required_symbolic_identity": identity,
                    }
                )
    return rows


def expected_obligations_for_row(row: dict[str, Any]) -> list[str]:
    if row.get("balance_block") == "translational_newton_balance":
        return ["translational_balance_identity", *SHARED_ROW_OBLIGATIONS]
    if row.get("balance_block") == "rotational_euler_balance":
        return ["rotational_balance_identity", *SHARED_ROW_OBLIGATIONS]
    return []


def main() -> int:
    checks = Checks()
    try:
        audit = read_json(AUDIT_JSON)
        audit_md = read_text(AUDIT_MD)
        obligation_gate = read_json(OBLIGATION_GATE)
        dynamic_oracle = read_json(DYNAMIC_ORACLE)
        manifest = read_json(MANIFEST)
    except Exception as exc:  # noqa: BLE001
        print(f"newton_euler_symbolic_target_audit=FAIL\n- {exc}")
        return 1

    checks.check(audit.get("schema") == "newton-euler-symbolic-target-audit-v1", "schema changed")
    checks.check(
        audit.get("status") == "row_level_symbolic_targets_extracted_dynamic_defect_proof_open",
        "status changed",
    )
    checks.check(audit.get("submission_ready") is False, "audit must not mark submission ready")
    checks.check(audit.get("accepted_method") == "Gauss6/FullVA", "accepted method changed")
    checks.check(audit.get("row_family") == "newton_euler_weak_balance", "row family changed")
    checks.check(audit.get("row_count") == 36, "row count changed")
    checks.check(audit.get("translational_row_count") == 18, "translational row count changed")
    checks.check(audit.get("rotational_row_count") == 18, "rotational row count changed")
    checks.check(audit.get("stage_count") == 3, "stage count changed")
    checks.check(audit.get("body_count") == 2, "body count changed")
    checks.check(audit.get("rows_per_body_stage") == 6, "rows per body-stage changed")

    indexing = audit.get("row_indexing", {})
    checks.check(indexing.get("stage_size") == 44, "stage size changed")
    checks.check(indexing.get("row_family_offset") == 24, "row family offset changed")
    checks.check(indexing.get("local_rows_0_to_2") == "body0 translational xyz", "local rows 0-2 mapping changed")
    checks.check(indexing.get("local_rows_3_to_5") == "body0 rotational xyz", "local rows 3-5 mapping changed")
    checks.check(indexing.get("local_rows_6_to_8") == "body1 translational xyz", "local rows 6-8 mapping changed")
    checks.check(indexing.get("local_rows_9_to_11") == "body1 rotational xyz", "local rows 9-11 mapping changed")

    rows = audit.get("row_targets", [])
    expected_targets = expected_row_targets()
    checks.check(isinstance(rows, list) and len(rows) == 36, "row target list length changed")
    checks.check([row.get("global_row") for row in rows] == expected_global_rows(), "global row map changed")
    for row, expected in zip(rows, expected_targets, strict=True):
        for key, expected_value in expected.items():
            checks.check(row.get(key) == expected_value, f"row {expected.get('global_row')} {key} changed")
    checks.check(
        sum(1 for row in rows if row.get("balance_block") == "translational_newton_balance") == 18,
        "translational target count changed",
    )
    checks.check(
        sum(1 for row in rows if row.get("balance_block") == "rotational_euler_balance") == 18,
        "rotational target count changed",
    )
    checks.check(
        {row.get("required_symbolic_identity") for row in rows}
        == {"translational_balance_identity", "rotational_balance_identity"},
        "row required symbolic identities changed",
    )

    families = audit.get("target_equation_families", [])
    checks.check([item.get("id") for item in families] == EXPECTED_OBLIGATIONS, "target family ids changed")
    checks.check(sum(int(item.get("rows", 0)) for item in families[:2]) == 36, "balance family rows changed")
    checks.check(all(int(item.get("rows", 0)) > 0 for item in families), "target family rows missing")

    coverage = audit.get("obligation_coverage_matrix", {})
    row_coverage = audit.get("row_obligation_coverage", [])
    checks.check(coverage.get("coverage_matrix_complete") is True, "obligation coverage matrix incomplete")
    checks.check(coverage.get("row_count") == 36, "coverage row count changed")
    checks.check(coverage.get("obligation_count") == 6, "coverage obligation count changed")
    checks.check(coverage.get("expected_obligations_per_row") == 5, "expected obligations per row changed")
    checks.check(
        coverage.get("rows_with_complete_obligation_sets") == 36,
        "coverage matrix does not cover every row",
    )
    checks.check(coverage.get("obligations_with_target_rows") == 6, "some obligations have no target rows")
    checks.check(coverage.get("row_obligation_link_count") == 180, "row-obligation link count changed")
    checks.check(coverage.get("all_rows_have_required_obligations") is True, "not every row has required obligations")
    checks.check(coverage.get("all_obligations_have_target_rows") is True, "not every obligation has target rows")
    checks.check(coverage.get("proof_closure_advanced") is False, "coverage matrix must not advance proof closure")
    checks.check(
        coverage.get("dynamic_symbolic_oracle_complete") is False,
        "coverage matrix overclaims dynamic symbolic oracle closure",
    )
    checks.check(
        coverage.get("stage_residual_O_h7_implementation_defect_proved") is False,
        "coverage matrix overclaims O(h^7) proof",
    )
    checks.check(coverage.get("submission_ready") is False, "coverage matrix overclaims submission readiness")
    checks.check(isinstance(row_coverage, list) and len(row_coverage) == 36, "row coverage list length changed")
    for target, row_cov in zip(rows, row_coverage, strict=False):
        expected_obligations = expected_obligations_for_row(target)
        checks.check(row_cov.get("global_row") == target.get("global_row"), "row coverage global row map changed")
        checks.check(row_cov.get("obligation_ids") == expected_obligations, "row coverage obligation ids changed")
        checks.check(row_cov.get("obligation_count") == 5, "row coverage obligation count changed")
        checks.check(row_cov.get("complete_obligation_set") is True, "row coverage set incomplete")

    per_obligation = coverage.get("per_obligation", [])
    expected_counts = {
        "translational_balance_identity": 18,
        "rotational_balance_identity": 18,
        "multiplier_wrench_consistency": 36,
        "smooth_force_lift_consistency": 36,
        "gauss_stage_dynamic_defect_rate": 36,
        "symbolic_runtime_row_equivalence": 36,
    }
    expected_proof_status = {
        "translational_balance_identity": "closed_by_obligation_gate",
        "rotational_balance_identity": "closed_by_obligation_gate",
        "multiplier_wrench_consistency": "closed_by_obligation_gate",
        "smooth_force_lift_consistency": "closed_by_obligation_gate",
        "gauss_stage_dynamic_defect_rate": "open_not_closed_by_coverage_matrix",
        "symbolic_runtime_row_equivalence": "closed_by_obligation_gate",
    }
    expected_source_gate_status = {
        "translational_balance_identity": "closed",
        "rotational_balance_identity": "closed",
        "multiplier_wrench_consistency": "closed",
        "smooth_force_lift_consistency": "closed",
        "gauss_stage_dynamic_defect_rate": "symbolic_primitive_route_open",
        "symbolic_runtime_row_equivalence": "closed",
    }
    expected_target_rows_by_obligation = {
        obligation_id: [
            row["global_row"]
            for row in expected_targets
            if obligation_id in expected_obligations_for_row(row)
        ]
        for obligation_id in EXPECTED_OBLIGATIONS
    }
    checks.check([item.get("id") for item in per_obligation] == EXPECTED_OBLIGATIONS, "coverage obligation ids changed")
    for item in per_obligation:
        obligation_id = item.get("id")
        checks.check(
            item.get("target_row_count") == expected_counts.get(obligation_id),
            f"target row count changed for {obligation_id}",
        )
        checks.check(
            len(item.get("target_global_rows", [])) == expected_counts.get(obligation_id),
            f"target row list changed for {obligation_id}",
        )
        checks.check(
            item.get("target_global_rows") == expected_target_rows_by_obligation.get(obligation_id),
            f"target global rows changed for {obligation_id}",
        )
        checks.check(
            item.get("proof_status") == expected_proof_status.get(obligation_id),
            f"coverage matrix proof status changed for {obligation_id}",
        )
        checks.check(
            item.get("source_gate_status") == expected_source_gate_status.get(obligation_id),
            f"coverage matrix source gate status changed for {obligation_id}",
        )
        if obligation_id == "gauss_stage_dynamic_defect_rate":
            checks.check(bool(item.get("required_proof")), "open D5 obligation proof text missing")
        else:
            checks.check(item.get("required_proof") is None, f"closed obligation proof text changed for {obligation_id}")

    runtime = audit.get("supporting_runtime_evidence", {})
    checks.check(runtime.get("full_formula_row_oracle_132_rows_checked") is True, "full formula oracle marker missing")
    checks.check(runtime.get("newton_euler_formula_row_family_added") == "newton_euler_weak_balance", "added row family changed")
    checks.check(runtime.get("formula_row_ad_jacobian_oracle_checked") is True, "AD oracle marker missing")
    checks.check(runtime.get("formula_row_ad_jacobian_probe_count") == 3, "AD probe count changed")
    checks.check(runtime.get("runtime_formula_row_oracle_complete") is True, "runtime formula oracle not complete")
    checks.check(runtime.get("runtime_ad_oracle_complete") is True, "runtime AD oracle not complete")
    checks.check(runtime.get("runtime_source_component_layout_matches_targets") is True, "runtime layout target marker missing")
    expected_runtime_layout = [
        {
            "name": name,
            "offset": offset,
            "width": width,
            "body": body,
            "balance_block": block,
        }
        for name, offset, width, body, block, _ in RUNTIME_SOURCE_COMPONENT_LAYOUT
    ]
    checks.check(
        runtime.get("runtime_source_component_layout") == expected_runtime_layout,
        "runtime source component layout changed",
    )
    checks.check(runtime.get("runtime_source_anchors_present") is True, "runtime source anchors marker missing")
    anchors = runtime.get("runtime_source_anchors", {})
    checks.check(anchors.get("run_v047_path") == "v047_cylindrical_chain_pipeline/run_v047.py", "runtime source path changed")
    validate_source_anchor(
        checks,
        anchors.get("layout_definition", {}),
        "runtime source component layout definition",
    )
    validate_source_anchor(
        checks,
        anchors.get("primary_residual_definition", {}),
        "primary Gauss6/FullVA residual definition",
    )
    validate_source_anchor(
        checks,
        anchors.get("primary_residual_dyn_extend", {}),
        "primary residual appends translational then rotational balances inside each body loop",
    )
    tuple_anchors = anchors.get("component_tuple_anchors", [])
    checks.check(isinstance(tuple_anchors, list) and len(tuple_anchors) == 4, "runtime component tuple anchors changed")
    expected_tuple_names = [item["name"] for item in expected_runtime_layout]
    checks.check([item.get("name") for item in tuple_anchors] == expected_tuple_names, "runtime component tuple anchor names changed")
    for item, expected in zip(tuple_anchors, expected_runtime_layout, strict=False):
        checks.check(item.get("offset") == expected.get("offset"), f"tuple anchor offset changed for {expected.get('name')}")
        checks.check(item.get("width") == expected.get("width"), f"tuple anchor width changed for {expected.get('name')}")
        checks.check(item.get("body") == expected.get("body"), f"tuple anchor body changed for {expected.get('name')}")
        checks.check(item.get("balance_block") == expected.get("balance_block"), f"tuple anchor balance block changed for {expected.get('name')}")
        validate_source_anchor(checks, item.get("anchor", {}), f"runtime layout tuple for {expected.get('name')}")
    checks.check(
        "do not prove symbolic algebraic equivalence" in anchors.get("source_anchor_scope", ""),
        "runtime source anchor proof boundary missing",
    )

    closure = audit.get("closure_boundary", {})
    checks.check(closure.get("symbolic_target_inventory_complete") is True, "symbolic target inventory missing")
    checks.check(
        closure.get("newton_euler_symbolic_defect_certificate_complete") is False,
        "symbolic defect certificate unexpectedly closed",
    )
    checks.check(
        closure.get("stage_residual_O_h7_implementation_defect_proved") is False,
        "O(h^7) implementation defect unexpectedly proved",
    )
    checks.check(closure.get("dynamic_symbolic_oracle_complete") is False, "dynamic symbolic oracle unexpectedly closed")
    checks.check(closure.get("closed_obligation_count") == 5, "closed obligation count changed")
    checks.check(closure.get("open_obligation_count") == 1, "open obligation count changed")

    execution = audit.get("execution_policy", {})
    checks.check(execution.get("read_only_audit") is True, "audit lost read-only marker")
    checks.check(execution.get("default_1e-4_required") is False, "audit requires default 1e-4")
    checks.check(execution.get("run_v047_invoked") is False, "audit invoked run_v047")
    checks.check(execution.get("v048_runner_invoked") is False, "audit invoked v048 runner")
    checks.check(execution.get("heavy_numerical_run_invoked") is False, "audit invoked heavy numerical run")

    gate_closure = obligation_gate.get("closure_state", {})
    checks.check(gate_closure.get("open_obligation_count") == 1, "obligation gate open count changed")
    checks.check(gate_closure.get("closed_obligation_count") == 5, "obligation gate closed count changed")
    full_formula = dynamic_oracle.get("full_independent_formula_row_oracle", {})
    checks.check(full_formula.get("row_count") == 132, "dynamic oracle row count changed")
    checks.check(full_formula.get("added_row_family") == "newton_euler_weak_balance", "dynamic oracle added family changed")

    for file_label in [
        "NEWTON_EULER_SYMBOLIC_TARGET_AUDIT.md",
        "NEWTON_EULER_SYMBOLIC_TARGET_AUDIT.json",
    ]:
        checks.check(file_label in manifest.get("evidence_anchors", []), f"manifest missing {file_label}")
    checks.check(
        "validate_newton_euler_symbolic_target_audit.py" in manifest.get("validators", []),
        "manifest missing symbolic target audit validator",
    )

    for token in [
        "Newton-Euler Symbolic Target Audit",
        "Dynamic rows: `36`.",
        "Translational/rotational rows: `18/18`.",
        "Symbolic target inventory complete: `True`.",
        "Obligation coverage matrix complete: `True`.",
        "Row-obligation links: `180`.",
        "Rows with complete obligation sets: `36`.",
        "Runtime source anchors present: `True`.",
        "do not prove symbolic algebraic equivalence or the O(h^7) defect bound",
        "Stage residual O(h^7) implementation defect proved: `False`.",
        "Proof closure advanced by this matrix: `False`.",
        "`translational_balance_identity`",
        "`rotational_balance_identity`",
        "Validator: `validate_newton_euler_symbolic_target_audit.py`.",
    ]:
        checks.check(contains_normalized(audit_md, token), f"audit markdown missing token: {token}")

    forbidden = set(audit.get("forbidden_claims", []))
    for claim in [
        "newton_euler_symbolic_defect_certificate_complete_true",
        "stage_residual_O_h7_implementation_defect_proved_true",
        "dynamic_symbolic_oracle_complete_true",
        "submission_ready_true",
    ]:
        checks.check(claim in forbidden, f"forbidden claim missing: {claim}")

    if checks.errors:
        print("newton_euler_symbolic_target_audit=FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("newton_euler_symbolic_target_audit=PASS")
    print("row_count=36")
    print("translational_rotational_rows=18/18")
    print("symbolic_target_inventory_complete=True")
    print("obligation_coverage_matrix_complete=True")
    print("row_obligation_links=180")
    print("stage_residual_O_h7_implementation_defect_proved=False")
    print("dynamic_symbolic_oracle_complete=False")
    print("submission_ready=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
