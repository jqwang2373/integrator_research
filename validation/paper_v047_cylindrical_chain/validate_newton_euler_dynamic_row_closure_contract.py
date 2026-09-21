#!/usr/bin/env python3
"""Validate the Newton-Euler dynamic-row closure contract."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
CONTRACT_JSON = PAPER / "NEWTON_EULER_DYNAMIC_ROW_CLOSURE_CONTRACT.json"
CONTRACT_MD = PAPER / "NEWTON_EULER_DYNAMIC_ROW_CLOSURE_CONTRACT.md"


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


def expected_rows() -> list[int]:
    rows: list[int] = []
    for stage in range(3):
        rows.extend(range(stage * 44 + 24, stage * 44 + 36))
    return rows


def main() -> int:
    checks = Checks()
    try:
        contract = read_json(CONTRACT_JSON)
        contract_md = read_text(CONTRACT_MD)
        manifest = read_json(PAPER / "SUBMISSION_ARTIFACT_MANIFEST.json")
        virtual_work_wrench = read_json(PAPER / "NEWTON_EULER_VIRTUAL_WORK_WRENCH_AUDIT.json")
        proof_closure = read_json(PAPER / "PROOF_CLOSURE_MANIFEST.json")
        direct_substitution = read_json(PAPER / "D5_DYNAMIC_DIRECT_SUBSTITUTION_CERTIFICATE.json")
    except Exception as exc:  # noqa: BLE001
        print(f"newton_euler_dynamic_row_closure_contract=FAIL\n- {exc}")
        return 1

    summary = contract.get("summary", {})
    rows = contract.get("row_contracts", [])
    actions = contract.get("proof_actions", [])
    checks.check(contract.get("schema") == "newton-euler-dynamic-row-closure-contract-v1", "schema changed")
    checks.check(
        contract.get("status") == "direct_substitution_contract_closed_primitive_taylor_route_open",
        "status changed",
    )
    checks.check(contract.get("submission_ready") is False, "submission readiness overclaimed")
    checks.check(contract.get("proof_gap_closed") is True, "proof gap not closed by direct substitution")
    checks.check(
        contract.get("dynamic_symbolic_oracle_complete") is False,
        "dynamic symbolic oracle should remain diagnostic/open",
    )
    checks.check(
        contract.get("stage_residual_O_h7_implementation_defect_proved") is True,
        "O(h^7) implementation defect not proved by direct substitution",
    )
    checks.check(summary.get("row_count") == 36, "row count changed")
    checks.check(summary.get("translational_row_count") == 18, "translational count changed")
    checks.check(summary.get("rotational_row_count") == 18, "rotational count changed")
    checks.check(summary.get("rows_with_full_runtime_traceability") == 36, "runtime traceability not complete")
    checks.check(
        summary.get("rows_with_direct_pc2_input_closure") == 36,
        "direct-PC2 input row count changed",
    )
    checks.check(summary.get("open_row_count") == 0, "open row count changed")
    checks.check(summary.get("row_obligation_link_count") == 180, "row-obligation link count changed")
    checks.check(summary.get("close_requirements_satisfied") == 2, "close requirements satisfied count changed")
    checks.check(summary.get("close_requirements_open") == 0, "open close requirements changed")
    checks.check(summary.get("unsatisfied_close_requirements") == [], "unsatisfied PCs changed")
    checks.check(summary.get("template_level_evidence_is_not_proof_closure") is True, "template boundary marker missing")
    checks.check(
        summary.get("virtual_work_wrench_sign_skeleton_checked") is True,
        "virtual-work sign skeleton not checked",
    )
    checks.check(
        summary.get("virtual_work_wrench_sign_skeleton_rows") == 36,
        "virtual-work sign skeleton rows changed",
    )
    checks.check(
        summary.get("virtual_work_template_identity_proved") is True,
        "virtual-work template identity not proved",
    )
    checks.check(
        summary.get("virtual_work_template_identity_rows") == 36,
        "virtual-work template identity rows changed",
    )
    checks.check(
        summary.get("row_expanded_virtual_work_identity_proved") is True,
        "row-expanded virtual-work identity not proved",
    )
    checks.check(
        summary.get("row_expanded_virtual_work_identity_rows") == 36,
        "row-expanded virtual-work identity rows changed",
    )
    checks.check(
        summary.get("multiplier_wrench_consistency_closed") is True,
        "multiplier wrench consistency not closed",
    )
    checks.check(
        virtual_work_wrench.get("summary", {}).get("checked_rows") == 36,
        "source virtual-work audit row count changed",
    )
    checks.check(summary.get("symbolic_target_inventory_complete") is True, "target inventory should be complete")
    checks.check(summary.get("obligation_gate_open_count") == 1, "open obligation count changed")
    checks.check(
        summary.get("smooth_force_lift_consistency_closed_rows") == 36,
        "smooth force-lift closed row count changed",
    )
    checks.check(
        summary.get("row_ordering_scaling_ad_closed_rows") == 36,
        "row-ordering/scaling/AD closed row count changed",
    )
    checks.check(summary.get("balance_identity_closed_rows") == 36, "balance identity closed row count changed")
    checks.check(summary.get("d5_dynamic_defect_blueprint_rows") == 36, "D5 blueprint row count changed")
    checks.check(summary.get("d5_open_lifted_stage_terms") == 0, "D5 open lifted-stage term count changed")
    checks.check(summary.get("d5_direct_substitution_closed_terms") == 36, "D5 direct closed term count changed")
    checks.check(
        summary.get("d5_direct_substitution_dynamic_zero_rows")
        == direct_substitution.get("summary", {}).get("dynamic_zero_residual_rows")
        == 36,
        "D5 direct zero-row count changed",
    )
    checks.check(summary.get("d5_direct_substitution_non_circular") is True, "D5 direct route circular")
    checks.check(summary.get("d5_primitive_taylor_route_closed") is False, "primitive/Taylor route unexpectedly closed")
    checks.check(
        summary.get("d5_rows_requiring_power_at_least_seven") == 36,
        "D5 required power row count changed",
    )
    checks.check(
        summary.get("d5_finite_probe_sufficient_rows") == 0,
        "D5 incorrectly accepts finite-probe-only rows",
    )
    checks.check(
        summary.get("d5_residual_to_error_promotion_allowed_rows") == 0,
        "D5 incorrectly allows residual-to-error promotion",
    )
    checks.check(summary.get("d5_blueprint_is_not_closure") is False, "D5 direct closure marker missing")
    checks.check(len(actions) == 6, "proof action count changed")
    checks.check({action.get("id") for action in actions} == {"D1", "D2", "D3", "D4", "D5", "D6"}, "D actions changed")
    for action in actions:
        if action.get("id") == "D3":
            checks.check(action.get("status") == "closed_row_expanded_identity", "D3 status changed")
            checks.check(
                action.get("closure_evidence") == "NEWTON_EULER_VIRTUAL_WORK_WRENCH_AUDIT.md/json",
                "D3 closure evidence changed",
            )
        elif action.get("id") == "D4":
            checks.check(action.get("status") == "closed_smooth_c7_lift", "D4 status changed")
            checks.check(
                action.get("closure_evidence") == "SMOOTH_FORCE_LIFT_CERTIFICATE.md/json",
                "D4 closure evidence changed",
            )
        elif action.get("id") in {"D1", "D2"}:
            checks.check(action.get("status") == "closed_balance_identity", f"{action.get('id')} status changed")
            checks.check(
                action.get("closure_evidence") == "NEWTON_EULER_BALANCE_IDENTITY_AUDIT.md/json",
                f"{action.get('id')} closure evidence changed",
            )
        elif action.get("id") == "D6":
            checks.check(action.get("status") == "closed_row_ordering_scaling_ad", "D6 status changed")
            checks.check(
                action.get("closure_evidence") == "NEWTON_EULER_ROW_ORDERING_SCALING_AD_AUDIT.md/json",
                "D6 closure evidence changed",
            )
        else:
            checks.check(action.get("status") == "closed_direct_substitution_zero_residual", "D5 status changed")
            checks.check(
                action.get("closure_evidence") == "D5_DYNAMIC_DIRECT_SUBSTITUTION_CERTIFICATE.md/json",
                "D5 closure evidence changed",
            )

    actual_counts = summary.get("actual_obligation_counts", {})
    expected_counts = {
        "translational_balance_identity": 18,
        "rotational_balance_identity": 18,
        "multiplier_wrench_consistency": 36,
        "smooth_force_lift_consistency": 36,
        "gauss_stage_dynamic_defect_rate": 36,
        "symbolic_runtime_row_equivalence": 36,
    }
    checks.check(actual_counts == expected_counts, "obligation coverage counts changed")
    checks.check(summary.get("expected_obligation_counts") == expected_counts, "expected obligation counts changed")

    row_ids = [row.get("global_row") for row in rows]
    checks.check(row_ids == expected_rows(), "global row sequence changed")
    evidence_keys = [
        "symbolic_expansion_present",
        "runtime_row_mapping_present",
        "runtime_template_instantiation_checked",
        "body_specific_wrench_expansion_checked",
        "virtual_work_wrench_sign_skeleton_checked",
        "virtual_work_template_identity_proved",
        "row_expanded_virtual_work_identity_proved",
        "multiplier_wrench_consistency_closed",
        "template_algebraic_equivalence_checked",
        "runtime_formula_row_oracle_link_checked",
        "row_ordering_scaling_ad_equivalence_closed",
        "smooth_force_lift_source_structure_checked",
        "smooth_force_lift_consistency_closed",
        "balance_identity_closed",
    ]
    for row in rows:
        evidence = row.get("evidence_present", {})
        closure = row.get("closure_state", {})
        checks.check(all(evidence.get(key) is True for key in evidence_keys), f"row {row.get('global_row')} traceability incomplete")
        checks.check(closure.get("runtime_row_equivalence_proved") is True, f"row {row.get('global_row')} runtime equivalence not closed")
        checks.check(closure.get("defect_bound_O_h7_proved") is True, f"row {row.get('global_row')} O(h^7) direct bound not closed")
        checks.check(closure.get("smooth_force_lift_consistency_closed") is True, f"row {row.get('global_row')} force lift not closed")
        checks.check(closure.get("balance_identity_closed") is True, f"row {row.get('global_row')} balance identity not closed")
        checks.check(closure.get("certified_for_theorem") is True, f"row {row.get('global_row')} theorem certification missing")
        checks.check(closure.get("blocks_close_requirements") == [], f"row {row.get('global_row')} PC blockers changed")
        d5 = row.get("d5_dynamic_defect_blueprint", {})
        checks.check(isinstance(d5, dict), f"row {row.get('global_row')} missing D5 blueprint")
        checks.check(d5.get("required_defect_power") == 7, f"row {row.get('global_row')} D5 power changed")
        checks.check(
            d5.get("required_certificate_kind") == "direct_substitution_row_oracle",
            f"row {row.get('global_row')} D5 certificate kind changed",
        )
        checks.check(
            d5.get("finite_probe_evidence_sufficient") is False,
            f"row {row.get('global_row')} D5 accepts finite-probe evidence",
        )
        checks.check(
            d5.get("residual_to_error_promotion_allowed") is False,
            f"row {row.get('global_row')} D5 allows residual-to-error promotion",
        )
        checks.check(
            d5.get("certifies_theorem_now") is True,
            f"row {row.get('global_row')} D5 does not certify theorem",
        )
        checks.check(
            d5.get("direct_substitution_closed") is True,
            f"row {row.get('global_row')} direct substitution not closed",
        )
        checks.check(
            d5.get("direct_substitution_residual_after_substitution") == "0",
            f"row {row.get('global_row')} direct residual is not zero",
        )
        checks.check(
            d5.get("primitive_taylor_route_closed") is False,
            f"row {row.get('global_row')} primitive/Taylor route unexpectedly closed",
        )
        decomposition = d5.get("defect_decomposition", [])
        checks.check(isinstance(decomposition, list) and len(decomposition) == 5, f"row {row.get('global_row')} D5 decomposition changed")
        by_obligation = {
            item.get("obligation"): item
            for item in decomposition
            if isinstance(item, dict) and isinstance(item.get("obligation"), str)
        }
        checks.check(set(by_obligation) == {"D1", "D3", "D4", "D5", "D6"} or set(by_obligation) == {"D2", "D3", "D4", "D5", "D6"}, f"row {row.get('global_row')} D5 obligations changed")
        checks.check(
            by_obligation.get("D5", {}).get("status") == "closed_direct_substitution_zero_residual",
            f"row {row.get('global_row')} D5 closed term changed",
        )
        checks.check(
            by_obligation.get("D5", {}).get("required_bound") == "0, hence O(h^7)",
            f"row {row.get('global_row')} D5 bound changed",
        )
        checks.check(
            isinstance(d5.get("acceptance_tests"), list) and len(d5.get("acceptance_tests")) == 5,
            f"row {row.get('global_row')} D5 acceptance tests changed",
        )
        checks.check(
            "Z_G" in str(d5.get("accepted_lift_substitution", "")),
            f"row {row.get('global_row')} D5 lift substitution missing",
        )
        block = row.get("balance_block")
        primary = row.get("primary_balance_obligation")
        if block == "translational_newton_balance":
            checks.check(primary == "D1", f"row {row.get('global_row')} primary D1 mismatch")
            checks.check("R_tr" in str(d5.get("residual_symbol")), f"row {row.get('global_row')} translational residual symbol missing")
            checks.check("D1" in by_obligation, f"row {row.get('global_row')} D1 D5 decomposition missing")
        if block == "rotational_euler_balance":
            checks.check(primary == "D2", f"row {row.get('global_row')} primary D2 mismatch")
            checks.check("R_rot" in str(d5.get("residual_symbol")), f"row {row.get('global_row')} rotational residual symbol missing")
            checks.check("D2" in by_obligation, f"row {row.get('global_row')} D2 D5 decomposition missing")
        checks.check(row.get("obligation_count") == 5, f"row {row.get('global_row')} obligation count changed")

    for token in [
        "Rows with full runtime traceability: `36`",
        "Rows certified for direct-PC2 theorem input: `36`",
        "Virtual-work wrench sign-skeleton rows: `36`",
        "Virtual-work template identity rows: `36`",
        "Virtual-work template identity proved: `True`",
        "Row-expanded virtual-work identity rows: `36`",
        "Row-expanded virtual-work identity proved: `True`",
        "Multiplier wrench consistency closed: `True`",
        "Smooth force-lift consistency closed rows: `36`",
        "Row-ordering/scaling/AD closed rows: `36`",
        "Balance identity closed rows: `36`",
        "D5 dynamic-defect blueprint rows: `36`",
        "D5 open lifted-stage terms: `0`",
        "D5 direct-substitution closed terms: `36`",
        "D5 direct-substitution dynamic zero rows: `36`",
        "D5 primitive/Taylor route closed: `False`",
        "D5 rows requiring power at least seven: `36`",
        "D5 finite-probe-sufficient rows: `0`",
        "D5 residual-to-error promotion allowed rows: `0`",
        "D5 direct-substitution blueprint nonclosure flag: `False`",
        "## D5 Direct-Substitution Closure",
        "| row | stage | body | comp. | block | primary | traceability | direct-PC2 input |",
        "`R_dyn(Z_G) = E_balance_identity + E_multiplier_wrench + E_smooth_force_lift + E_row_binding + E_lifted_stage_dynamics`.",
        "| `D5 lifted-stage dynamics` | `36` | `closed direct substitution` | use `D5_DYNAMIC_DIRECT_SUBSTITUTION_CERTIFICATE.md/json`: residual after substituting `Z_G` is `0` row-by-row |",
        "Unsatisfied close requirements: ``",
        "Direct PC2 proof gap closed: `True`",
        "Stage residual O(h^7) implementation defect proved: `True`",
        "D5 direct-substitution closure only as a direct-PC2 theorem input",
        "they do not close the primitive/Taylor route, P6 solver-policy evidence, P7 residual-to-error promotion",
        "D4 note: smooth force/friction C7 lift is closed",
        "D6 note: row ordering, unweighted residual scaling, and accepted AD binding are closed",
        "Validator: `validate_newton_euler_dynamic_row_closure_contract.py`.",
    ]:
        checks.check(token in contract_md, f"MD missing token: {token}")

    checks.check(
        manifest.get("newton_euler_dynamic_row_closure_contract")
        == "NEWTON_EULER_DYNAMIC_ROW_CLOSURE_CONTRACT.md",
        "manifest missing MD path",
    )
    checks.check(
        manifest.get("newton_euler_dynamic_row_closure_contract_json")
        == "NEWTON_EULER_DYNAMIC_ROW_CLOSURE_CONTRACT.json",
        "manifest missing JSON path",
    )
    checks.check(
        "NEWTON_EULER_DYNAMIC_ROW_CLOSURE_CONTRACT.md" in manifest.get("evidence_anchors", []),
        "manifest evidence anchor missing MD",
    )
    checks.check(
        "NEWTON_EULER_DYNAMIC_ROW_CLOSURE_CONTRACT.json" in manifest.get("evidence_anchors", []),
        "manifest evidence anchor missing JSON",
    )
    checks.check(
        "validate_newton_euler_dynamic_row_closure_contract.py" in manifest.get("validators", []),
        "manifest validator missing",
    )
    proof_summary = proof_closure.get("evidence_summary", {})
    checks.check(
        proof_summary.get("newton_euler_dynamic_row_closure_contract_rows") == 36,
        "proof closure manifest missing contract row count",
    )
    checks.check(
        proof_summary.get("newton_euler_dynamic_row_closure_contract_theorem_closed_rows") == 36,
        "proof closure manifest missing direct-route row-defect closed contract rows",
    )
    checks.check(
        proof_summary.get("newton_euler_dynamic_row_closure_contract_traceability_rows") == 36,
        "proof closure manifest missing traceability row count",
    )

    if checks.errors:
        print("newton_euler_dynamic_row_closure_contract=FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("newton_euler_dynamic_row_closure_contract=PASS")
    print("rows=36")
    print("rows_with_full_runtime_traceability=36")
    print("rows_with_direct_pc2_input_closure=36")
    print("unsatisfied_close_requirements=none")
    print("direct_pc2_proof_gap_closed=True")
    print("legacy_proof_gap_closed=True")
    return 0


if __name__ == "__main__":
    sys.exit(main())
