#!/usr/bin/env python3
"""Build row-level AD-expanded oracle coverage for Newton-Euler rows."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
OUT_JSON = PAPER / "NEWTON_EULER_AD_EXPANDED_ROW_ORACLE_AUDIT.json"
OUT_MD = PAPER / "NEWTON_EULER_AD_EXPANDED_ROW_ORACLE_AUDIT.md"

STAGE_SIZE = 44
FULL_FORMULA_FAMILY_ORDER = [
    ("translational_position_weak_defect", 18),
    ("rotational_lie_position_weak_defect", 18),
    ("translational_velocity_weak_defect", 18),
    ("angular_velocity_weak_defect", 18),
    ("newton_euler_weak_balance", 36),
    ("lower_pair_index3_weak_constraints", 24),
]
NEWTON_EULER_FAMILY = "newton_euler_weak_balance"
NEWTON_EULER_FAMILY_OFFSET = 24
NEWTON_EULER_FAMILY_WIDTH = 12


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def formula_family_major_offset() -> int:
    offset = 0
    for family, width in FULL_FORMULA_FAMILY_ORDER:
        if family == NEWTON_EULER_FAMILY:
            return offset
        offset += width
    raise ValueError(f"{NEWTON_EULER_FAMILY} missing from formula family order")


def dynamic_row_family(dynamic_oracle: dict[str, Any]) -> dict[str, Any]:
    families = dynamic_oracle.get("layout", {}).get("row_families", [])
    for item in families:
        if isinstance(item, dict) and item.get("name") == NEWTON_EULER_FAMILY:
            return item
    return {}


def main() -> None:
    dynamic_oracle = read_json(PAPER / "DYNAMIC_ROW_ORACLE_GATE.json")
    target_audit = read_json(PAPER / "NEWTON_EULER_SYMBOLIC_TARGET_AUDIT.json")
    proof_contract = read_json(PAPER / "CMAME_PROOF_CONTRACT_GATE.json")

    full_formula = dynamic_oracle.get("full_independent_formula_row_oracle", {})
    formula_jacobian = dynamic_oracle.get("formula_row_ad_jacobian_oracle", {})
    boundary = dynamic_oracle.get("acceptance_boundary", {})
    family = dynamic_row_family(dynamic_oracle)
    theorem_contract = proof_contract.get("theorem_contract", {})
    family_major_offset = formula_family_major_offset()
    rows = []
    for target in target_audit.get("row_targets", []):
        local_block_row = int(target["local_block_row"])
        stage = int(target["stage"])
        accepted_row = int(target["global_row"])
        expected_accepted_row = stage * STAGE_SIZE + NEWTON_EULER_FAMILY_OFFSET + local_block_row
        formula_row = family_major_offset + stage * NEWTON_EULER_FAMILY_WIDTH + local_block_row
        rows.append(
            {
                "global_row": accepted_row,
                "expected_global_row": expected_accepted_row,
                "formula_family_major_row": formula_row,
                "stage": stage,
                "body": target.get("body"),
                "component": target.get("component"),
                "balance_block": target.get("balance_block"),
                "local_block_row": local_block_row,
                "runtime_source_component": target.get("runtime_source_component"),
                "accepted_residual_row_covered": accepted_row == expected_accepted_row,
                "formula_family_major_row_covered": family_major_offset <= formula_row < family_major_offset + 36,
                "ad_jacobian_columns_covered": int(formula_jacobian.get("column_count", 0)),
                "probe_count": int(formula_jacobian.get("probe_count", 0)),
                "row_ad_binding_checked": (
                    formula_jacobian.get("checked") is True
                    and formula_jacobian.get("multi_probe_checked") is True
                    and formula_jacobian.get("runtime_ad_oracle_complete") is True
                    and full_formula.get("checked") is True
                    and full_formula.get("runtime_formula_row_oracle_complete") is True
                    and accepted_row == expected_accepted_row
                ),
                "row_ad_binding_scope": (
                    "formula-family-major AD row is covered by the 132x132 jacfwd-vs-R_JAC "
                    "runtime oracle; this is an AD-expanded implementation binding, not a "
                    "symbolic identity proof and not an O(h^7) dynamic-defect proof"
                ),
            }
        )

    formula_rows = [row["formula_family_major_row"] for row in rows]
    accepted_rows = [row["global_row"] for row in rows]
    all_rows_bound = all(row["row_ad_binding_checked"] for row in rows)
    max_mismatch = theorem_contract.get("formula_row_ad_jacobian_max_mismatch")
    result = {
        "schema": "newton-euler-ad-expanded-row-oracle-audit-v1",
        "status": "ad_expanded_runtime_formula_binding_complete_symbolic_oracle_open",
        "submission_ready": False,
        "accepted_method": "Gauss6/FullVA",
        "row_family": NEWTON_EULER_FAMILY,
        "row_count": len(rows),
        "translational_row_count": sum(1 for row in rows if row["balance_block"] == "translational_newton_balance"),
        "rotational_row_count": sum(1 for row in rows if row["balance_block"] == "rotational_euler_balance"),
        "stage_count": target_audit.get("stage_count"),
        "formula_family_major_offset": family_major_offset,
        "formula_family_major_rows": formula_rows,
        "accepted_residual_rows": accepted_rows,
        "ad_jacobian_column_count": formula_jacobian.get("column_count"),
        "formula_row_ad_jacobian_probe_count": formula_jacobian.get("probe_count"),
        "formula_row_ad_jacobian_probe_vectors": formula_jacobian.get("probe_vectors", []),
        "formula_row_ad_jacobian_max_mismatch": max_mismatch,
        "formula_row_ad_jacobian_tolerance": formula_jacobian.get("tolerance"),
        "full_formula_row_oracle_132_rows_checked": (
            full_formula.get("checked") is True
            and full_formula.get("row_count") == 132
            and full_formula.get("added_row_family") == NEWTON_EULER_FAMILY
        ),
        "formula_row_ad_jacobian_oracle_132x132_checked": (
            formula_jacobian.get("checked") is True
            and formula_jacobian.get("row_count") == 132
            and formula_jacobian.get("column_count") == 132
        ),
        "formula_row_ad_jacobian_multi_probe_checked": formula_jacobian.get("multi_probe_checked") is True,
        "runtime_ad_oracle_complete": formula_jacobian.get("runtime_ad_oracle_complete") is True,
        "ad_expanded_row_oracle_closed": all_rows_bound,
        "ad_expanded_row_oracle_rows": sum(1 for row in rows if row["row_ad_binding_checked"]),
        "ad_expanded_row_oracle_columns_per_row": formula_jacobian.get("column_count"),
        "ad_expanded_symbolic_oracle_closure": False,
        "independent_symbolic_row_by_row_oracle_closed": False,
        "dynamic_symbolic_oracle_complete": False,
        "stage_residual_O_h7_implementation_defect_proved": False,
        "proof_gap_closed": False,
        "dynamic_row_family": family,
        "acceptance_boundary": {
            "independent_symbolic_row_oracle_complete": boundary.get(
                "independent_symbolic_row_oracle_complete"
            ),
            "stage_residual_O_h7_implementation_defect_proved": boundary.get(
                "stage_residual_O_h7_implementation_defect_proved"
            ),
            "submission_ready": boundary.get("submission_ready"),
        },
        "review_requirement_mapping": {
            "AD_expanded_symbolic_oracle_closure": (
                "closed only as row-level runtime formula/AD binding coverage for all 36 "
                "Newton-Euler rows; independent symbolic row identity and O(h^7) dynamic "
                "defect closure remain open"
            ),
            "independent_symbolic_row_by_row_oracle_for_expanded_fullva_rows": "not closed by this audit",
        },
        "row_ad_coverage": rows,
        "claim_policy": {
            "allowed_now": [
                "all 36 Newton-Euler dynamic rows have explicit AD-expanded runtime formula binding coverage",
                "each covered row has 132 AD columns checked under the existing multi-probe runtime oracle",
            ],
            "forbidden_now": [
                "independent_symbolic_row_by_row_oracle_closed",
                "ad_expanded_symbolic_oracle_closure",
                "dynamic_symbolic_oracle_complete",
                "stage_residual_O_h7_implementation_defect_proved",
                "proof_gap_closed",
                "submission_ready",
            ],
        },
        "source_files": {
            "dynamic_row_oracle_gate": "DYNAMIC_ROW_ORACLE_GATE.json",
            "newton_euler_symbolic_target_audit": "NEWTON_EULER_SYMBOLIC_TARGET_AUDIT.json",
            "cmame_proof_contract_gate": "CMAME_PROOF_CONTRACT_GATE.json",
        },
    }

    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# Newton-Euler AD-Expanded Row Oracle Audit",
        "",
        "Status: **AD-expanded runtime formula binding complete; symbolic oracle open**.",
        "",
        f"- AD-expanded row oracle closed: `{result['ad_expanded_row_oracle_closed']}`.",
        f"- AD-expanded rows: `{result['ad_expanded_row_oracle_rows']}/{result['row_count']}`.",
        f"- AD columns per row: `{result['ad_expanded_row_oracle_columns_per_row']}`.",
        f"- Formula-family-major offset: `{result['formula_family_major_offset']}`.",
        f"- Formula-row AD Jacobian probes: `{result['formula_row_ad_jacobian_probe_count']}`.",
        f"- Formula-row AD Jacobian max mismatch: `{result['formula_row_ad_jacobian_max_mismatch']}`.",
        f"- AD-expanded symbolic oracle closure: `{result['ad_expanded_symbolic_oracle_closure']}`.",
        f"- Independent symbolic row-by-row oracle closed: `{result['independent_symbolic_row_by_row_oracle_closed']}`.",
        f"- Dynamic symbolic oracle complete: `{result['dynamic_symbolic_oracle_complete']}`.",
        f"- Stage residual O(h^7) implementation defect proved: `{result['stage_residual_O_h7_implementation_defect_proved']}`.",
        "",
        "## Row Coverage",
        "",
        "| accepted row | formula-major row | stage | body | component | block | columns | probes | binding |",
        "|---:|---:|---:|---:|---|---|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| `{row['global_row']}` | `{row['formula_family_major_row']}` | `{row['stage']}` | "
            f"`{row['body']}` | `{row['component']}` | `{row['balance_block']}` | "
            f"`{row['ad_jacobian_columns_covered']}` | `{row['probe_count']}` | "
            f"`{row['row_ad_binding_checked']}` |"
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "This audit closes row-level AD-expanded runtime/formula binding coverage only.",
            "It does not prove a symbolic identity for the expanded rows, and it does not",
            "prove the Newton-Euler stage residual is O(h^7).",
            "",
            "Validator: `validate_newton_euler_ad_expanded_row_oracle_audit.py`.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("newton_euler_ad_expanded_row_oracle_audit=written")
    print(f"ad_expanded_rows={result['ad_expanded_row_oracle_rows']}")
    print(f"ad_columns_per_row={result['ad_expanded_row_oracle_columns_per_row']}")
    print("dynamic_symbolic_oracle_complete=False")


if __name__ == "__main__":
    main()
