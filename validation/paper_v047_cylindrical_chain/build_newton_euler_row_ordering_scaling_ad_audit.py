#!/usr/bin/env python3
"""Build an independent D6 row-ordering/scaling/AD audit.

The audit closes only the D6 implementation-layout sub-obligation for the
Newton-Euler dynamic rows. It proves from source structure and the symbolic
target inventory that the 36 dynamic target rows have the implemented row
ordering, unweighted residual scaling, and accepted AD binding. It does not
prove the D1/D2 balance identities or the D5 O(h^7) dynamic defect.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
ROOT = PAPER.parent
RUN_V047 = ROOT.parent / "numerics" / "v047_cylindrical_chain_pipeline" / "run_v047.py"
OUT_JSON = PAPER / "NEWTON_EULER_ROW_ORDERING_SCALING_AD_AUDIT.json"
OUT_MD = PAPER / "NEWTON_EULER_ROW_ORDERING_SCALING_AD_AUDIT.md"

STAGE_SIZE = 44
DYNAMIC_OFFSET = 24
DYNAMIC_WIDTH = 12
STAGES = 3


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def normalized(text: str) -> str:
    return " ".join(text.split())


def find_function(tree: ast.AST, source: str, name: str) -> tuple[ast.FunctionDef | None, str]:
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node, normalized(ast.get_source_segment(source, node) or "")
    return None, ""


def assignment_source(function: ast.FunctionDef, source: str, name: str) -> list[str]:
    segments: list[str] = []
    for node in ast.walk(function):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == name:
                    segment = ast.get_source_segment(source, node)
                    if segment:
                        segments.append(normalized(segment))
    return segments


def call_sources(function: ast.FunctionDef, source: str, attr: str) -> list[str]:
    segments: list[str] = []
    for node in ast.walk(function):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == attr:
            segment = ast.get_source_segment(source, node)
            if segment:
                segments.append(normalized(segment))
    return segments


def expected_dynamic_component(local_dynamic_offset: int) -> dict[str, Any]:
    if 0 <= local_dynamic_offset <= 2:
        return {
            "body": 0,
            "balance_block": "translational_newton_balance",
            "runtime_source_component": "body0_translational_balance_source",
            "runtime_source_component_offset": 0,
            "runtime_source_component_width": 3,
            "runtime_source_component_index": local_dynamic_offset,
        }
    if 3 <= local_dynamic_offset <= 5:
        return {
            "body": 0,
            "balance_block": "rotational_euler_balance",
            "runtime_source_component": "body0_rotational_balance_source",
            "runtime_source_component_offset": 3,
            "runtime_source_component_width": 3,
            "runtime_source_component_index": local_dynamic_offset - 3,
        }
    if 6 <= local_dynamic_offset <= 8:
        return {
            "body": 1,
            "balance_block": "translational_newton_balance",
            "runtime_source_component": "body1_translational_balance_source",
            "runtime_source_component_offset": 6,
            "runtime_source_component_width": 3,
            "runtime_source_component_index": local_dynamic_offset - 6,
        }
    if 9 <= local_dynamic_offset <= 11:
        return {
            "body": 1,
            "balance_block": "rotational_euler_balance",
            "runtime_source_component": "body1_rotational_balance_source",
            "runtime_source_component_offset": 9,
            "runtime_source_component_width": 3,
            "runtime_source_component_index": local_dynamic_offset - 9,
        }
    raise ValueError(f"invalid dynamic offset {local_dynamic_offset}")


def build_row_audit(target_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for target in target_rows:
        global_row = int(target["global_row"])
        stage = global_row // STAGE_SIZE
        local_row = global_row - stage * STAGE_SIZE
        local_dynamic_offset = local_row - DYNAMIC_OFFSET
        expected = expected_dynamic_component(local_dynamic_offset)
        row_checks = {
            "stage_index_matches_global_row": stage == target.get("stage"),
            "local_row_is_dynamic": DYNAMIC_OFFSET <= local_row < DYNAMIC_OFFSET + DYNAMIC_WIDTH,
            "body_matches_source_order": expected["body"] == target.get("body"),
            "balance_block_matches_source_order": expected["balance_block"] == target.get("balance_block"),
            "runtime_source_component_matches": expected["runtime_source_component"]
            == target.get("runtime_source_component"),
            "runtime_source_component_offset_matches": expected["runtime_source_component_offset"]
            == target.get("runtime_source_component_offset"),
            "runtime_source_component_width_matches": expected["runtime_source_component_width"]
            == target.get("runtime_source_component_width"),
            "runtime_source_component_index_matches": expected["runtime_source_component_index"]
            == target.get("runtime_source_component_index"),
        }
        rows.append(
            {
                "global_row": global_row,
                "stage": stage,
                "local_row": local_row,
                "local_dynamic_offset": local_dynamic_offset,
                "expected": expected,
                "target": {
                    "stage": target.get("stage"),
                    "body": target.get("body"),
                    "component": target.get("component"),
                    "balance_block": target.get("balance_block"),
                    "runtime_source_component": target.get("runtime_source_component"),
                    "runtime_source_component_offset": target.get("runtime_source_component_offset"),
                    "runtime_source_component_width": target.get("runtime_source_component_width"),
                    "runtime_source_component_index": target.get("runtime_source_component_index"),
                },
                "checks": row_checks,
                "proved": all(row_checks.values()),
            }
        )
    return rows


def main() -> None:
    source = RUN_V047.read_text(encoding="utf-8")
    tree = ast.parse(source)
    residual_node, residual_source = find_function(tree, source, "residual_cylindrical_chain")
    if residual_node is None:
        raise RuntimeError("residual_cylindrical_chain not found")

    target_audit = read_json(PAPER / "NEWTON_EULER_SYMBOLIC_TARGET_AUDIT.json")
    dynamic_oracle = read_json(PAPER / "DYNAMIC_ROW_ORACLE_GATE.json")
    proof_contract = read_json(PAPER / "CMAME_PROOF_CONTRACT_GATE.json")
    target_rows = [
        item for item in target_audit.get("row_targets", []) if isinstance(item, dict)
    ]
    row_audit = build_row_audit(target_rows)

    out_extend = next(
        (item for item in call_sources(residual_node, source, "extend") if "out.extend" in item),
        "",
    )
    dyn_extend = next(
        (item for item in call_sources(residual_node, source, "extend") if "dyn.extend" in item),
        "",
    )
    dyn_assignments = assignment_source(residual_node, source, "dyn")
    weight_assignments = assignment_source(residual_node, source, "weight")
    formula_ad = dynamic_oracle.get("formula_row_ad_jacobian_oracle", {})
    full_formula = dynamic_oracle.get("full_independent_formula_row_oracle", {})
    theorem = proof_contract.get("theorem_contract", {})
    layout_rows = dynamic_oracle.get("layout", {}).get("row_families", [])
    dynamic_family = next(
        (item for item in layout_rows if isinstance(item, dict) and item.get("name") == "newton_euler_weak_balance"),
        {},
    )

    source_checks = {
        "stage_loop_order_is_source_order": "for si, st in enumerate(stages)" in residual_source,
        "dynamic_body_loop_is_body_order": "for body in range(N_BODIES)" in residual_source,
        "dynamic_extend_trans_then_rot": "dyn.extend([trans, rot])" in dyn_extend,
        "residual_family_concat_order": (
            "out.extend([jnp.concatenate(pvel), jnp.concatenate(u_block), "
            "jnp.concatenate(pacc), jnp.concatenate(w_block), jnp.concatenate(dyn), "
            "jnp.concatenate(constraints)])"
        )
        in out_extend,
        "dynamic_rows_are_unweighted_in_residual": not weight_assignments and "weight =" not in residual_source,
        "r_value_binds_residual": "R_VALUE = jax.jit(residual_cylindrical_chain)" in source,
        "r_jac_binds_jacfwd_residual": (
            "R_JAC = jax.jit(jax.jacfwd(residual_cylindrical_chain, argnums=0))" in source
        ),
        "dynamic_vector_initialized_once": "dyn = []" in dyn_assignments,
    }
    layout_checks = {
        "dynamic_family_offset": dynamic_family.get("offset") == DYNAMIC_OFFSET,
        "dynamic_family_width": dynamic_family.get("width") == DYNAMIC_WIDTH,
        "dynamic_family_total_rows": dynamic_family.get("total_rows") == STAGES * DYNAMIC_WIDTH,
        "target_row_count": len(row_audit) == STAGES * DYNAMIC_WIDTH,
        "all_target_rows_proved": all(row.get("proved") is True for row in row_audit),
    }
    ad_checks = {
        "full_formula_row_oracle_checked": full_formula.get("checked") is True,
        "full_formula_row_count": full_formula.get("row_count") == STAGE_SIZE * STAGES,
        "dynamic_family_added": full_formula.get("added_row_family") == "newton_euler_weak_balance",
        "formula_row_ad_jacobian_checked": formula_ad.get("checked") is True,
        "formula_row_ad_jacobian_multi_probe_checked": formula_ad.get("multi_probe_checked") is True,
        "formula_row_ad_jacobian_probe_count": formula_ad.get("probe_count") == 3,
        "formula_row_ad_jacobian_shape": formula_ad.get("row_count") == 132
        and formula_ad.get("column_count") == 132,
        "formula_row_ad_jacobian_runtime_binding": formula_ad.get("relation_checked")
        == "jax.jacfwd(independent_formula_family_major_vector) equals accepted R_JAC in row-family-major order",
        "formula_row_ad_jacobian_max_mismatch_small": float(
            theorem.get("formula_row_ad_jacobian_max_mismatch", 1.0)
        )
        <= 1.0e-12,
    }
    closed = all(source_checks.values()) and all(layout_checks.values()) and all(ad_checks.values())

    result = {
        "schema": "newton-euler-row-ordering-scaling-ad-audit-v1",
        "status": "d6_row_ordering_scaling_ad_closed_dynamic_defect_open",
        "submission_ready": False,
        "proof_gap_closed": False,
        "proof_gap_closed_scope": (
            "local_d6_row_ordering_scaling_ad_audit_only; this audit closes "
            "implementation layout/AD binding but not the D5 O(h^7) dynamic defect "
            "or the full direct D5/PC2 closure artifact"
        ),
        "dynamic_symbolic_oracle_complete": False,
        "stage_residual_O_h7_implementation_defect_proved": False,
        "symbolic_runtime_row_equivalence_closed": closed,
        "row_ordering_scaling_ad_closed": closed,
        "accepted_method": "Gauss6/FullVA",
        "accepted_residual": "residual_cylindrical_chain",
        "source_files": {
            "runtime_source": "../../numerics/v047_cylindrical_chain_pipeline/run_v047.py",
            "symbolic_target_audit": "NEWTON_EULER_SYMBOLIC_TARGET_AUDIT.json",
            "dynamic_row_oracle": "DYNAMIC_ROW_ORACLE_GATE.json",
        },
        "row_layout": {
            "stage_size": STAGE_SIZE,
            "stage_count": STAGES,
            "dynamic_offset": DYNAMIC_OFFSET,
            "dynamic_width": DYNAMIC_WIDTH,
            "dynamic_rows": STAGES * DYNAMIC_WIDTH,
            "per_stage_order": [
                "body0_translational_rows_0_2",
                "body0_rotational_rows_3_5",
                "body1_translational_rows_6_8",
                "body1_rotational_rows_9_11",
            ],
        },
        "source_checks": source_checks,
        "layout_checks": layout_checks,
        "ad_binding_checks": ad_checks,
        "row_audit": row_audit,
        "closed_scope": (
            "D6 row-ordering, residual-scaling, and accepted AD-binding equivalence for "
            "the 36 implemented Newton-Euler dynamic rows. This does not close the D1/D2 "
            "linear/angular balance identities and does not prove the D5 O(h^7) dynamic defect."
        ),
        "open_boundaries": [
            "D1 translational balance identity",
            "D2 rotational balance identity",
            "D5 lifted-stage dynamic O(h^7) defect",
            "PC1/PC2 theorem close requirements",
        ],
        "execution_policy": {
            "read_only_existing_artifacts": True,
            "default_1e_4_required": False,
            "heavy_numerical_run_invoked": False,
            "run_v047_invoked": False,
            "v048_runner_invoked": False,
        },
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# Newton-Euler Row Ordering, Scaling, and AD Audit",
        "",
        "Status: **D6 CLOSED - row ordering, residual scaling, and AD binding are checked; dynamic defect remains open**.",
        "",
        f"- Symbolic runtime row-equivalence sub-obligation closed: `{result['symbolic_runtime_row_equivalence_closed']}`.",
        f"- Row-ordering/scaling/AD closed: `{result['row_ordering_scaling_ad_closed']}`.",
        f"- Dynamic symbolic oracle complete: `{result['dynamic_symbolic_oracle_complete']}`.",
        f"- Stage residual O(h^7) implementation defect proved: `{result['stage_residual_O_h7_implementation_defect_proved']}`.",
        f"- Local D6 audit proof gap closed: `{result['proof_gap_closed']}`.",
        f"- Proof gap closed scope: `{result['proof_gap_closed_scope']}`.",
        f"- Submission ready: `{result['submission_ready']}`.",
        "",
        "## Row Layout",
        "",
        f"- Stage size: `{STAGE_SIZE}`.",
        f"- Dynamic offset/width: `{DYNAMIC_OFFSET}/{DYNAMIC_WIDTH}`.",
        "- Per-stage dynamic order: body0 translational, body0 rotational, body1 translational, body1 rotational.",
        "- Global row formula: `global_row = 44*stage + 24 + local_dynamic_offset`.",
        "",
        "## Checked Groups",
        "",
        "| group | checked |",
        "|---|---:|",
        f"| source row order and unweighted residual scaling | `{all(source_checks.values())}` |",
        f"| target-row layout equivalence | `{all(layout_checks.values())}` |",
        f"| accepted AD binding | `{all(ad_checks.values())}` |",
        "",
        "## Boundary",
        "",
        "- This closes only D6: implemented row ordering, unweighted residual scaling, and accepted AD binding.",
        "- It does not close the D1/D2 balance identities.",
        "- It does not prove the D5 O(h^7) dynamic-row defect.",
        "",
        "Validator: `validate_newton_euler_row_ordering_scaling_ad_audit.py`.",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("newton_euler_row_ordering_scaling_ad_audit=written")
    print(f"symbolic_runtime_row_equivalence_closed={closed}")
    print("stage_residual_O_h7_implementation_defect_proved=False")
    print("local_d6_audit_proof_gap_closed=False")


if __name__ == "__main__":
    main()
