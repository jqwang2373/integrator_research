#!/usr/bin/env python3
"""Build a row-level symbolic target audit for the Newton-Euler rows."""

from __future__ import annotations

import json
from pathlib import Path


PAPER = Path(__file__).resolve().parent
WORK = PAPER.parent
RUN_V047 = WORK.parent / "numerics" / "v047_cylindrical_chain_pipeline" / "run_v047.py"
OUT_JSON = PAPER / "NEWTON_EULER_SYMBOLIC_TARGET_AUDIT.json"
OUT_MD = PAPER / "NEWTON_EULER_SYMBOLIC_TARGET_AUDIT.md"

STAGE_SIZE = 44
ROW_FAMILY_OFFSET = 24
STAGES = 3
BODIES = 2
COMPONENTS = ["x", "y", "z"]
RUNTIME_SOURCE_COMPONENT_LAYOUT = [
    ("body0_translational_balance_source", 0, 3, 0, "translational_newton_balance", "translational_balance_identity"),
    ("body0_rotational_balance_source", 3, 3, 0, "rotational_euler_balance", "rotational_balance_identity"),
    ("body1_translational_balance_source", 6, 3, 1, "translational_newton_balance", "translational_balance_identity"),
    ("body1_rotational_balance_source", 9, 3, 1, "rotational_euler_balance", "rotational_balance_identity"),
]
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


def read_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def source_anchor(path: Path, needle: str, role: str, *, after: str | None = None, before: str | None = None) -> dict:
    lines = read_text(path).splitlines()
    after_line = 0
    before_line = len(lines) + 1
    if after is not None:
        for lineno, line in enumerate(lines, start=1):
            if after in line:
                after_line = lineno
                break
        else:
            raise ValueError(f"{after!r} not found in {path}")
    if before is not None:
        for lineno, line in enumerate(lines, start=1):
            if lineno > after_line and before in line:
                before_line = lineno
                break
        else:
            raise ValueError(f"{before!r} not found after {after!r} in {path}")
    for lineno, line in enumerate(lines, start=1):
        if after_line < lineno < before_line and needle in line:
            return {
                "role": role,
                "file": str(path.relative_to(WORK)),
                "line": lineno,
                "needle": needle,
            }
    raise ValueError(f"{needle!r} not found in {path}")


def runtime_source_anchors() -> dict:
    component_tuples = []
    for source_name, source_offset, source_width, body, block, _ in RUNTIME_SOURCE_COMPONENT_LAYOUT:
        source_kind = "translational_balance" if block == "translational_newton_balance" else "rotational_balance"
        component_tuples.append(
            {
                "name": source_name,
                "offset": source_offset,
                "width": source_width,
                "body": body,
                "balance_block": block,
                "source_component_kind": source_kind,
                "anchor": source_anchor(
                    RUN_V047,
                    f'("{source_name}", {source_offset}, {source_width}, {body}, "{source_kind}")',
                    f"runtime layout tuple for {source_name}",
                ),
            }
        )
    residual_start = "def residual_cylindrical_chain("
    residual_end = "R_VALUE = jax.jit(residual_cylindrical_chain)"
    return {
        "run_v047_path": str(RUN_V047.relative_to(WORK)),
        "layout_definition": source_anchor(
            RUN_V047,
            "NEWTON_EULER_SOURCE_COMPONENT_LAYOUT = [",
            "runtime source component layout definition",
        ),
        "component_tuple_anchors": component_tuples,
        "primary_residual_definition": source_anchor(
            RUN_V047,
            residual_start,
            "primary Gauss6/FullVA residual definition",
        ),
        "primary_residual_dyn_extend": source_anchor(
            RUN_V047,
            "dyn.extend([trans, rot])",
            "primary residual appends translational then rotational balances inside each body loop",
            after=residual_start,
            before=residual_end,
        ),
        "source_anchor_scope": (
            "anchors prove the implemented row-order source locations used by the target audit; "
            "they do not prove symbolic algebraic equivalence or the O(h^7) defect bound"
        ),
    }


def row_targets() -> list[dict]:
    rows: list[dict] = []
    for stage in range(STAGES):
        stage_base = stage * STAGE_SIZE + ROW_FAMILY_OFFSET
        for source_name, source_offset, source_width, body, block, identity in RUNTIME_SOURCE_COMPONENT_LAYOUT:
            for component_index, component in enumerate(COMPONENTS):
                local = source_offset + component_index
                is_trans = block == "translational_newton_balance"
                rows.append(
                    {
                        "global_row": stage_base + local,
                        "stage": stage,
                        "body": body,
                        "component": component,
                        "balance_block": block,
                        "local_block_row": local,
                        "runtime_source_component": source_name,
                        "runtime_source_component_offset": source_offset,
                        "runtime_source_component_width": source_width,
                        "runtime_source_component_index": component_index,
                        "target_equation": "m_i a_i - f_i^ext - m_i g - f_i^joint(lambda) - f_i^friction = 0"
                        if is_trans
                        else "J_i alpha_i + omega_i x J_i omega_i - tau_i^ext - tau_i^joint(lambda) - tau_i^friction = 0",
                        "required_symbolic_identity": identity,
                    }
                )
    return rows


def row_obligations(row: dict) -> list[str]:
    if row["balance_block"] == "translational_newton_balance":
        return ["translational_balance_identity", *SHARED_ROW_OBLIGATIONS]
    if row["balance_block"] == "rotational_euler_balance":
        return ["rotational_balance_identity", *SHARED_ROW_OBLIGATIONS]
    raise ValueError(f"unknown balance block: {row['balance_block']}")


def build_obligation_coverage(
    rows: list[dict], open_obligations: list[dict], closed_obligations: list[dict], closure: dict
) -> tuple[dict, list[dict]]:
    status_by_id = {
        item.get("id"): item
        for item in [*open_obligations, *closed_obligations]
        if isinstance(item, dict)
    }
    row_coverage: list[dict] = []
    for row in rows:
        obligation_ids = row_obligations(row)
        row_coverage.append(
            {
                "global_row": row["global_row"],
                "stage": row["stage"],
                "body": row["body"],
                "component": row["component"],
                "balance_block": row["balance_block"],
                "obligation_ids": obligation_ids,
                "obligation_count": len(obligation_ids),
                "complete_obligation_set": len(obligation_ids) == 5,
            }
        )

    per_obligation = []
    for obligation_id in EXPECTED_OBLIGATIONS:
        target_rows = [
            item["global_row"]
            for item in row_coverage
            if obligation_id in item["obligation_ids"]
        ]
        obligation = status_by_id.get(obligation_id, {})
        source_status = obligation.get("status", "unknown")
        per_obligation.append(
            {
                "id": obligation_id,
                "target_row_count": len(target_rows),
                "target_global_rows": target_rows,
                "source_gate_status": source_status,
                "required_proof": obligation.get("required_proof"),
                "proof_status": (
                    "closed_by_obligation_gate"
                    if source_status == "closed"
                    else "open_not_closed_by_coverage_matrix"
                ),
            }
        )

    rows_with_complete_sets = sum(1 for item in row_coverage if item["complete_obligation_set"])
    row_obligation_link_count = sum(item["obligation_count"] for item in row_coverage)
    coverage = {
        "coverage_matrix_complete": (
            rows_with_complete_sets == len(rows)
            and row_obligation_link_count == len(rows) * 5
            and all(item["target_row_count"] > 0 for item in per_obligation)
        ),
        "row_count": len(rows),
        "obligation_count": len(EXPECTED_OBLIGATIONS),
        "expected_obligations_per_row": 5,
        "rows_with_complete_obligation_sets": rows_with_complete_sets,
        "obligations_with_target_rows": sum(1 for item in per_obligation if item["target_row_count"] > 0),
        "row_obligation_link_count": row_obligation_link_count,
        "all_rows_have_required_obligations": rows_with_complete_sets == len(rows),
        "all_obligations_have_target_rows": all(item["target_row_count"] > 0 for item in per_obligation),
        "per_obligation": per_obligation,
        "proof_closure_advanced": False,
        "dynamic_symbolic_oracle_complete": closure.get("dynamic_symbolic_oracle_complete"),
        "stage_residual_O_h7_implementation_defect_proved": closure.get(
            "stage_residual_O_h7_implementation_defect_proved"
        ),
        "submission_ready": False,
        "reading_rule": (
            "complete coverage matrix specifies row-level obligations and mirrors the "
            "obligation gate status; it does not by itself prove any obligation"
        ),
    }
    return coverage, row_coverage


def main() -> None:
    dynamic_oracle = read_json(PAPER / "DYNAMIC_ROW_ORACLE_GATE.json")
    obligation_gate = read_json(PAPER / "NEWTON_EULER_DEFECT_OBLIGATION_GATE.json")
    source_anchors = runtime_source_anchors()
    rows = row_targets()
    translational_rows = [row for row in rows if row["balance_block"] == "translational_newton_balance"]
    rotational_rows = [row for row in rows if row["balance_block"] == "rotational_euler_balance"]
    full_formula = dynamic_oracle.get("full_independent_formula_row_oracle", {})
    formula_jac = dynamic_oracle.get("formula_row_ad_jacobian_oracle", {})
    closure = obligation_gate.get("closure_state", {})
    open_obligations = obligation_gate.get("open_obligations", [])
    closed_obligations = obligation_gate.get("closed_obligations", [])
    obligation_coverage, row_obligation_coverage = build_obligation_coverage(
        rows, open_obligations, closed_obligations, closure
    )

    result = {
        "schema": "newton-euler-symbolic-target-audit-v1",
        "status": "row_level_symbolic_targets_extracted_dynamic_defect_proof_open",
        "submission_ready": False,
        "accepted_method": "Gauss6/FullVA",
        "row_family": "newton_euler_weak_balance",
        "row_count": len(rows),
        "translational_row_count": len(translational_rows),
        "rotational_row_count": len(rotational_rows),
        "stage_count": STAGES,
        "body_count": BODIES,
        "rows_per_body_stage": 6,
        "row_indexing": {
            "stage_size": STAGE_SIZE,
            "row_family_offset": ROW_FAMILY_OFFSET,
            "stage_major_formula": "global_row = stage * 44 + 24 + local_block_row",
            "local_rows_0_to_2": "body0 translational xyz",
            "local_rows_3_to_5": "body0 rotational xyz",
            "local_rows_6_to_8": "body1 translational xyz",
            "local_rows_9_to_11": "body1 rotational xyz",
            "runtime_source_order": "matches run_v047.py NEWTON_EULER_SOURCE_COMPONENT_LAYOUT and dyn.extend([trans, rot]) inside the body loop",
        },
        "target_equation_families": [
            {
                "id": "translational_balance_identity",
                "rows": len(translational_rows),
                "target": "m_i a_i = f_i^ext + m_i g + f_i^joint(lambda) + f_i^friction",
                "required_terms": [
                    "mass times translational acceleration",
                    "gravity force",
                    "applied body force",
                    "lower-pair multiplier force",
                    "smooth friction force",
                    "Gauss stage weight and row ordering",
                ],
            },
            {
                "id": "rotational_balance_identity",
                "rows": len(rotational_rows),
                "target": "J_i alpha_i + omega_i x J_i omega_i = tau_i^ext + tau_i^joint(lambda) + tau_i^friction",
                "required_terms": [
                    "body inertia times angular acceleration",
                    "gyroscopic angular momentum term",
                    "applied body torque",
                    "lower-pair multiplier moment arm",
                    "smooth friction torque",
                    "Gauss stage weight and row ordering",
                ],
            },
            {
                "id": "multiplier_wrench_consistency",
                "rows": len(rows),
                "target": "constraint multipliers induce identical generalized forces in constraint and dynamics rows",
                "required_terms": ["lambda normal components", "joint basis", "moment arms", "equal and opposite body wrenches"],
            },
            {
                "id": "smooth_force_lift_consistency",
                "rows": len(rows),
                "target": "all force, torque, and friction evaluations use the same smooth FullVA stage lift",
                "required_terms": ["Brown-McPhee smooth friction", "stage kinematics", "bounded derivatives on proof tube"],
            },
            {
                "id": "gauss_stage_dynamic_defect_rate",
                "rows": len(rows),
                "target": "dynamic rows evaluated on the mathematical smooth lift have O(h^7) defect",
                "required_terms": ["Gauss collocation order", "smooth force composition", "constraint force consistency"],
            },
            {
                "id": "symbolic_runtime_row_equivalence",
                "rows": len(rows),
                "target": "implemented runtime row ordering and symbolic target rows are identical",
                "required_terms": ["row-family-major ordering", "stage-major slices", "AD-expanded residual path"],
            },
        ],
        "row_targets": rows,
        "obligation_coverage_matrix": obligation_coverage,
        "row_obligation_coverage": row_obligation_coverage,
        "supporting_runtime_evidence": {
            "full_formula_row_oracle_132_rows_checked": full_formula.get("checked"),
            "newton_euler_formula_row_family_added": full_formula.get("added_row_family"),
            "formula_row_ad_jacobian_oracle_checked": formula_jac.get("checked"),
            "formula_row_ad_jacobian_probe_count": formula_jac.get("probe_count"),
            "runtime_formula_row_oracle_complete": full_formula.get("runtime_formula_row_oracle_complete"),
            "runtime_ad_oracle_complete": formula_jac.get("runtime_ad_oracle_complete"),
            "runtime_source_component_layout": [
                {
                    "name": name,
                    "offset": offset,
                    "width": width,
                    "body": body,
                    "balance_block": block,
                }
                for name, offset, width, body, block, _ in RUNTIME_SOURCE_COMPONENT_LAYOUT
            ],
            "runtime_source_component_layout_matches_targets": True,
            "runtime_source_anchors_present": True,
            "runtime_source_anchors": source_anchors,
        },
        "closure_boundary": {
            "symbolic_target_inventory_complete": True,
            "newton_euler_symbolic_defect_certificate_complete": closure.get(
                "newton_euler_symbolic_defect_certificate_complete"
            ),
            "stage_residual_O_h7_implementation_defect_proved": closure.get(
                "stage_residual_O_h7_implementation_defect_proved"
            ),
            "dynamic_symbolic_oracle_complete": closure.get("dynamic_symbolic_oracle_complete"),
            "closed_obligation_count": closure.get("closed_obligation_count"),
            "open_obligation_count": closure.get("open_obligation_count"),
            "submission_ready": False,
        },
        "open_obligations": open_obligations,
        "execution_policy": {
            "read_only_audit": True,
            "default_1e-4_required": False,
            "run_v047_invoked": False,
            "v048_runner_invoked": False,
            "heavy_numerical_run_invoked": False,
        },
        "source_files": {
            "dynamic_oracle": "DYNAMIC_ROW_ORACLE_GATE.json",
            "newton_euler_defect_obligation_gate": "NEWTON_EULER_DEFECT_OBLIGATION_GATE.json",
        },
        "forbidden_claims": [
            "newton_euler_symbolic_defect_certificate_complete_true",
            "stage_residual_O_h7_implementation_defect_proved_true",
            "dynamic_symbolic_oracle_complete_true",
            "submission_ready_true",
        ],
    }

    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# Newton-Euler Symbolic Target Audit",
        "",
        "Status: **row-level symbolic targets extracted; dynamic defect proof open**.",
        "",
        "This read-only audit turns the 36 `newton_euler_weak_balance` rows into",
        "explicit stage/body/component proof targets. It does not invoke",
        "`run_v047.py`, any v048 runner, or a default `1e-4` campaign.",
        "",
        f"- Row family: `{result['row_family']}`.",
        f"- Dynamic rows: `{result['row_count']}`.",
        f"- Translational/rotational rows: `{result['translational_row_count']}/{result['rotational_row_count']}`.",
        f"- Symbolic target inventory complete: `{result['closure_boundary']['symbolic_target_inventory_complete']}`.",
        f"- Newton-Euler symbolic defect certificate complete: `{result['closure_boundary']['newton_euler_symbolic_defect_certificate_complete']}`.",
        f"- Stage residual O(h^7) implementation defect proved: `{result['closure_boundary']['stage_residual_O_h7_implementation_defect_proved']}`.",
        f"- Dynamic symbolic oracle complete: `{result['closure_boundary']['dynamic_symbolic_oracle_complete']}`.",
        f"- Open/closed obligations: `{result['closure_boundary']['open_obligation_count']}/{result['closure_boundary']['closed_obligation_count']}`.",
        f"- Obligation coverage matrix complete: `{result['obligation_coverage_matrix']['coverage_matrix_complete']}`.",
        f"- Row-obligation links: `{result['obligation_coverage_matrix']['row_obligation_link_count']}`.",
        f"- Rows with complete obligation sets: `{result['obligation_coverage_matrix']['rows_with_complete_obligation_sets']}`.",
        f"- Runtime source anchors present: `{result['supporting_runtime_evidence']['runtime_source_anchors_present']}`.",
        f"- Runtime source anchor scope: {result['supporting_runtime_evidence']['runtime_source_anchors']['source_anchor_scope']}.",
        "",
        "## Target Equation Families",
        "",
        "| id | rows | target |",
        "|---|---:|---|",
    ]
    for item in result["target_equation_families"]:
        lines.append(f"| `{item['id']}` | `{item['rows']}` | {item['target']} |")
    lines.extend(
        [
            "",
            "## Obligation Coverage Matrix",
            "",
            "This matrix assigns every dynamic row to its balance-specific proof obligation",
            "and the four shared Newton-Euler consistency obligations. It is a coverage",
            "specification, not a proof certificate.",
            "",
            "| obligation | target rows | proof status |",
            "|---|---:|---|",
        ]
    )
    for item in result["obligation_coverage_matrix"]["per_obligation"]:
        lines.append(f"| `{item['id']}` | `{item['target_row_count']}` | `{item['proof_status']}` |")
    lines.extend(
        [
            "",
            f"- Coverage matrix complete: `{result['obligation_coverage_matrix']['coverage_matrix_complete']}`.",
            f"- Row-obligation links: `{result['obligation_coverage_matrix']['row_obligation_link_count']}`.",
            f"- Rows with complete obligation sets: `{result['obligation_coverage_matrix']['rows_with_complete_obligation_sets']}`.",
            f"- Proof closure advanced by this matrix: `{result['obligation_coverage_matrix']['proof_closure_advanced']}`.",
        ]
    )
    lines.extend(
        [
            "",
            "## Row Targets",
            "",
            "| global row | stage | body | component | block | required identity |",
            "|---:|---:|---:|---|---|---|",
        ]
    )
    for row in rows:
        lines.append(
            f"| `{row['global_row']}` | `{row['stage']}` | `{row['body']}` | `{row['component']}` | "
            f"`{row['balance_block']}` | `{row['required_symbolic_identity']}` |"
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "The full formula-row oracle and AD-Jacobian oracle are runtime evidence.",
            "This audit adds row-level symbolic targets, but it does not prove the",
            "`O(h^7)` dynamic defect or close the independent symbolic oracle.",
            "",
            "Validator: `validate_newton_euler_symbolic_target_audit.py`.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("newton_euler_symbolic_target_audit=written")
    print(f"row_count={len(rows)}")
    print("symbolic_target_inventory_complete=True")
    print(f"obligation_coverage_matrix_complete={obligation_coverage['coverage_matrix_complete']}")
    print(f"row_obligation_links={obligation_coverage['row_obligation_link_count']}")
    print("stage_residual_O_h7_implementation_defect_proved=False")


if __name__ == "__main__":
    main()
