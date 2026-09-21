#!/usr/bin/env python3
"""Validate the RA2021 double-pendulum low-order diagnosis."""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
V048_RESULTS = PAPER.parent.parent / "numerics" / "v048_cross_paper_same_test_benchmarks" / "results"


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


def close(value: object, target: float, tol: float = 1.0e-9) -> bool:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return False
    return math.isfinite(number) and abs(number - target) <= tol


def main() -> int:
    checks = Checks()
    try:
        audit = read_json(PAPER / "RA2021_DOUBLE_SOURCE_POLICY_LOW_ORDER_DIAGNOSIS.json")
        audit_md = read_text(PAPER / "RA2021_DOUBLE_SOURCE_POLICY_LOW_ORDER_DIAGNOSIS.md")
        summary = read_json(V048_RESULTS / "ra2021_double_local_source_policy_candidate_summary.json")
    except Exception as exc:  # noqa: BLE001
        print(f"RA2021 double source-policy low-order diagnosis validation: FAIL\n- {exc}")
        return 1

    contract = audit.get("candidate_contract", {})
    public_audit = audit.get("public_step_family_audit", {})
    order = audit.get("order_evidence", {})
    diagnosis = audit.get("diagnosis", {})
    promotion = audit.get("promotion_decision", {})
    ledger_binding = audit.get("ledger_binding_reconciliation", {})
    pairwise = order.get("pairwise_orders", [])
    pairwise_error_family = order.get("pairwise_error_family", [])
    rows = audit.get("rows", [])
    pair_by_label = {item.get("label"): item for item in pairwise if isinstance(item, dict)}

    checks.check(
        audit.get("schema") == "ra2021-double-source-policy-low-order-diagnosis-v1",
        "schema changed",
    )
    checks.check(
        audit.get("status") == "diagnosis_only_low_order_floor_limited_not_promoted",
        "status changed",
    )
    checks.check(audit.get("read_only") is True, "audit should be read-only")
    checks.check(audit.get("heavy_numerical_run_invoked_by_this_builder") is False, "builder invoked heavy run")
    checks.check(audit.get("run_v047_invoked_by_this_builder") is False, "builder invoked run_v047")
    checks.check(audit.get("v048_runner_invoked_by_this_builder") is False, "builder invoked v048 runner")

    checks.check(contract.get("summary_status") == summary.get("status"), "summary status stale")
    checks.check(contract.get("summary_status") == "executed_isolated_source_policy_candidate", "candidate not executed")
    checks.check(contract.get("execution_mode") == summary.get("execution_mode") == "candidate", "execution mode changed")
    checks.check(contract.get("rows_complete") is True, "rows are not complete")
    checks.check(contract.get("row_count") == contract.get("ok_row_count") == 3, "row count changed")
    checks.check(contract.get("source_policy_contract_selected") is True, "source-policy contract not selected")
    checks.check(contract.get("source_policy_time_window_selected") is True, "source-policy time window not selected")
    checks.check(contract.get("source_policy_step_trio_selected") is True, "source-policy step trio not selected")
    checks.check(contract.get("source_policy_reference_h_selected") is True, "source-policy reference h not selected")
    checks.check(contract.get("selected_t_end") == 3.0, "selected horizon changed")
    checks.check(contract.get("selected_step_sizes") == [0.01, 0.002, 0.001], "selected h values changed")
    checks.check(contract.get("observed_h_values") == [0.001, 0.002, 0.01], "observed h values changed")
    checks.check(contract.get("selected_reference_h") == 0.0001, "selected reference h changed")
    checks.check(contract.get("observed_reference_h_values") == [0.0001], "observed reference h changed")
    checks.check(contract.get("reference_status") == "ok", "reference status changed")
    checks.check(contract.get("estimated_reference_steps") == 30000, "reference step estimate changed")
    checks.check(contract.get("estimated_candidate_steps") == [300, 1500, 3000], "candidate step estimates changed")
    checks.check(contract.get("jax_safe_small_angle_patch_enabled") is True, "JAX-safe patch marker missing")
    checks.check(
        contract.get("jax_safe_small_angle_patch_id") == "isolated_v013_jax_safe_small_angle_taylor_v1",
        "JAX-safe patch id changed",
    )
    checks.check(
        public_audit.get("generic_ra2021_public_order_step_sizes") == [0.01, 0.001, 0.0001],
        "generic public step family changed",
    )
    checks.check(
        public_audit.get("candidate_public_policy_h_values") == [0.001, 0.01],
        "candidate public-policy h marker values changed",
    )
    checks.check(public_audit.get("candidate_public_policy_h_count") == 2, "public-policy h count changed")
    checks.check(
        public_audit.get("generic_public_policy_h_required_count") == 3,
        "generic public-policy required count changed",
    )
    checks.check(
        public_audit.get("generic_public_policy_h_missing_as_candidate_values") == [0.0001],
        "missing generic public h marker changed",
    )
    checks.check(
        public_audit.get("non_public_selected_candidate_h_values") == [0.002],
        "non-public selected h marker changed",
    )
    checks.check(
        public_audit.get("selected_source_policy_h_values") == [0.001, 0.002, 0.01],
        "selected source-policy h audit changed",
    )
    checks.check(public_audit.get("source_policy_h_marker_count") == 3, "source-policy h marker count changed")
    checks.check(
        "h=0.002 is not a public-policy candidate h" in public_audit.get("scope_note", ""),
        "public/source h scope note missing h=0.002 distinction",
    )

    checks.check(close(order.get("source_policy_order_acceptance_threshold"), 5.5), "order threshold changed")
    checks.check(
        close(order.get("aggregate_pos_observed_order"), summary.get("source_policy_pos_observed_order")),
        "aggregate position order stale",
    )
    checks.check(
        close(order.get("aggregate_vel_observed_order"), summary.get("source_policy_vel_observed_order")),
        "aggregate velocity order stale",
    )
    checks.check(order.get("aggregate_order_acceptance_satisfied") is False, "order acceptance overclaimed")
    checks.check(order.get("aggregate_order_below_acceptance") is True, "low-order marker missing")
    checks.check(len(pairwise) == 2, "pairwise order count changed")
    checks.check(set(pair_by_label) == {"0.01_to_0.002", "0.002_to_0.001"}, "pairwise labels changed")
    checks.check(len(pairwise_error_family) == 8, "pairwise error-family count changed")
    checks.check(len(order.get("trajectory_error_pairwise_orders", [])) == 4, "trajectory error-family count changed")
    checks.check(len(order.get("final_error_pairwise_orders", [])) == 4, "final error-family count changed")
    family_by_metric_pair = {
        (item.get("metric"), item.get("label")): item
        for item in pairwise_error_family
        if isinstance(item, dict)
    }
    checks.check(
        ("pos_final_linf", "0.01_to_0.002") in family_by_metric_pair,
        "final position order sensitivity missing coarse pair",
    )
    checks.check(
        ("vel_final_linf", "0.01_to_0.002") in family_by_metric_pair,
        "final velocity order sensitivity missing coarse pair",
    )
    checks.check(
        family_by_metric_pair.get(("pos_final_linf", "0.01_to_0.002"), {}).get("pair_order", 9.0) < 5.5,
        "final position coarse pair unexpectedly rescues order",
    )
    checks.check(
        family_by_metric_pair.get(("vel_final_linf", "0.01_to_0.002"), {}).get("pair_order", 9.0) < 5.5,
        "final velocity coarse pair unexpectedly rescues order",
    )
    coarse_pair = pair_by_label.get("0.01_to_0.002", {})
    fine_pair = pair_by_label.get("0.002_to_0.001", {})
    checks.check(coarse_pair.get("pos_pair_order", 0.0) > 2.0, "coarse-to-mid position order changed")
    checks.check(coarse_pair.get("vel_pair_order", 0.0) > 3.0, "coarse-to-mid velocity order changed")
    checks.check(coarse_pair.get("pos_pair_order", 9.0) < 5.5, "coarse-to-mid position order overclaimed")
    checks.check(coarse_pair.get("vel_pair_order", 9.0) < 5.5, "coarse-to-mid velocity order overclaimed")
    checks.check(fine_pair.get("pos_pair_order", 1.0) < 0.2, "fine-pair position floor marker changed")
    checks.check(fine_pair.get("vel_pair_order", 1.0) < 0.2, "fine-pair velocity floor marker changed")
    checks.check(fine_pair.get("fine_pair_floor_limited") is True, "fine-pair floor-limited marker missing")
    checks.check(fine_pair.get("max_pair_error_scale", 1.0) < 1.0e-11, "fine-pair error scale changed")

    checks.check(diagnosis.get("fine_pair_floor_limited") is True, "diagnosis lost floor marker")
    checks.check(diagnosis.get("coarse_to_mid_pair_label") == "0.01_to_0.002", "diagnosis coarse-to-mid label changed")
    checks.check(diagnosis.get("coarse_to_mid_pos_pair_order", 9.0) < 5.5, "diagnosis coarse-to-mid pos order overclaimed")
    checks.check(diagnosis.get("coarse_to_mid_vel_pair_order", 9.0) < 5.5, "diagnosis coarse-to-mid vel order overclaimed")
    checks.check(diagnosis.get("coarse_to_mid_pair_below_acceptance") is True, "diagnosis coarse-to-mid below-acceptance marker missing")
    checks.check(diagnosis.get("fine_pair_label") == "0.002_to_0.001", "diagnosis fine-pair label changed")
    checks.check(diagnosis.get("fine_pair_pos_pair_order", 1.0) < 0.2, "diagnosis fine-pair pos order changed")
    checks.check(diagnosis.get("fine_pair_vel_pair_order", 1.0) < 0.2, "diagnosis fine-pair vel order changed")
    checks.check(
        diagnosis.get("coarse_h_constraint_threshold_satisfied") is False,
        "coarse h constraint threshold unexpectedly satisfied",
    )
    checks.check(close(diagnosis.get("constraint_threshold"), 1.0e-10), "constraint threshold changed")
    checks.check(
        diagnosis.get("coarse_h_constraint_failure_components") == ["endpoint_velocity_constraint"],
        "coarse h constraint failure component changed",
    )
    checks.check(
        close(diagnosis.get("coarse_h_endpoint_velocity_over_threshold_factor"), 1.805105192348697),
        "coarse h endpoint velocity over-threshold factor changed",
    )
    checks.check(close(diagnosis.get("fine_pair_floor_error_scale_threshold"), 1.0e-11), "floor threshold changed")
    checks.check(
        close(diagnosis.get("fine_pair_floor_margin_to_threshold"), 0.17550405573274475),
        "fine-pair floor margin changed",
    )
    checks.check(close(diagnosis.get("finest_to_reference_step_ratio"), 10.0), "finest/reference h ratio changed")
    checks.check(close(diagnosis.get("finest_h"), 0.001), "finest h changed")
    checks.check(close(diagnosis.get("reference_h"), 0.0001), "reference h changed in diagnosis")
    checks.check(
        diagnosis.get("reference_floor_sensitivity")
        == "fine_pair_errors_below_floor_threshold_and_only_ten_reference_steps_per_finest_step",
        "reference-floor sensitivity label changed",
    )
    for label in [
        "fine_pair_near_reference_or_roundoff_floor",
        "coarse_to_mid_pair_below_sixth_order_acceptance",
        "coarse_h_constraint_threshold_not_satisfied",
        "aggregate_order_below_sixth_order_acceptance",
        "local_double_source_policy_not_generic_public_order_step_family",
        "no_single_implementation_defect_proven_from_existing_read_only_evidence",
        "independent_rerun_missing",
        "error_runtime_newton_policy_binding_missing",
        "coarse_h_endpoint_velocity_constraint_exceeds_threshold",
        "final_error_orders_do_not_rescue_trajectory_order_acceptance",
    ]:
        checks.check(label in diagnosis.get("root_cause_labels", []), f"root-cause label missing: {label}")
    checks.check(
        "do not identify a single implementation defect" in diagnosis.get("proof_boundary", ""),
        "proof boundary no-defect caveat missing",
    )
    checks.check(
        ledger_binding.get("source") == "SOURCE_POLICY_ROW_CLOSURE_LEDGER.json",
        "ledger binding source changed",
    )
    checks.check(
        ledger_binding.get("candidate_local_error_runtime_newton_columns_present") is True,
        "candidate local metric columns are no longer present",
    )
    checks.check(
        ledger_binding.get("candidate_metric_columns_checked")
        == [
            "pos_traj_linf",
            "vel_traj_linf",
            "pos_final_linf",
            "vel_final_linf",
            "runtime_sec",
            "total_newton_iterations",
        ],
        "candidate metric column check changed",
    )
    checks.check(
        ledger_binding.get("accepted_source_policy_binding_closed") is False,
        "ledger binding overclaims accepted source-policy closure",
    )
    checks.check(
        ledger_binding.get("candidate_local_metrics_are_promotable_binding") is False,
        "ledger binding overclaims local metrics are promotable",
    )
    checks.check(
        ledger_binding.get("ledger_status") == "row_level_source_policy_closure_open",
        "ledger status changed in binding reconciliation",
    )
    checks.check(
        ledger_binding.get("ledger_rows_source_policy_closed") == 0,
        "ledger reconciliation overclosed source-policy rows",
    )
    checks.check(
        ledger_binding.get("ledger_rows_external_superiority_ready") == 0,
        "ledger reconciliation overclaims external-superiority rows",
    )
    checks.check(
        ledger_binding.get("ledger_ra2021_status") == "open_verify_or_rerun_public_rows",
        "ledger RA2021 status changed",
    )
    checks.check(
        ledger_binding.get("ledger_ra2021_source_identity_resolved_evidence_per_row") == 3,
        "ledger RA2021 resolved-evidence count changed",
    )
    checks.check(
        ledger_binding.get("ledger_ra2021_source_policy_promotion_evidence_remaining_per_row") == 4,
        "ledger RA2021 remaining-evidence count changed",
    )
    checks.check(ledger_binding.get("ledger_double_row_count") == 1, "ledger double row count changed")
    checks.check(
        ledger_binding.get("ledger_double_missing_evidence_counts") == [4],
        "ledger double missing-evidence count changed",
    )
    checks.check(
        ledger_binding.get("ledger_double_action_classes")
        == ["fix_or_rerun_public_velocity_mapping_time_grid_norm_runtime"],
        "ledger double action class changed",
    )
    checks.check(
        ledger_binding.get("ledger_double_allowed_uses") == ["diagnostic_common_reference_only"],
        "ledger double allowed use changed",
    )
    checks.check(
        ledger_binding.get("row_status_can_shrink_from_this_read_only_diagnosis") is False,
        "read-only diagnosis unexpectedly shrinks row status",
    )

    checks.check(promotion.get("promotion_ready") is False, "promotion readiness overclaimed")
    checks.check(promotion.get("source_policy_rows_promoted_by_this_diagnosis") == 0, "diagnosis promoted rows")
    checks.check(promotion.get("source_policy_rows_closed_by_this_diagnosis") == 0, "diagnosis closed rows")
    checks.check(promotion.get("b4_b7_can_close_from_this_diagnosis") is False, "diagnosis overcloses B4/B7")
    checks.check(promotion.get("external_superiority_claim_allowed") is False, "diagnosis overclaims superiority")
    checks.check(
        any("observed source-policy order is below sixth-order acceptance" in str(item) for item in promotion.get("promotion_blockers", [])),
        "low-order promotion blocker missing",
    )
    checks.check(len(rows) == 3, "diagnosis row count changed")
    checks.check(rows[0].get("h") == 0.01 and rows[0].get("constraint_threshold_satisfied") is False, "coarse row marker changed")
    checks.check(rows[1].get("h") == 0.002 and rows[1].get("constraint_threshold_satisfied") is True, "middle row marker changed")
    checks.check(rows[2].get("h") == 0.001 and rows[2].get("constraint_threshold_satisfied") is True, "fine row marker changed")
    checks.check(rows[0].get("source_policy_h") is True and rows[0].get("public_policy_h") is True, "h=0.01 h markers changed")
    checks.check(rows[1].get("source_policy_h") is True and rows[1].get("public_policy_h") is False, "h=0.002 h markers changed")
    checks.check(rows[2].get("source_policy_h") is True and rows[2].get("public_policy_h") is True, "h=0.001 h markers changed")

    for token in [
        "Status: **diagnosis only; low-order rows are not promoted**.",
        "Rows complete: `True` with `3` rows.",
        "Generic RA2021 public h represented as candidate rows: `2/3`.",
        "Non-public selected candidate h values: `[0.002]`.",
        "Aggregate pos/vel order: `2.148/2.463` below threshold `5.500`.",
        "Coarse-to-mid 0.01 -> 0.002 pos/vel order: `2.825/3.248`.",
        "Fine pair floor-limited: `True`.",
        "Fine pair 0.002 -> 0.001 pos/vel order: `0.097/0.084`.",
        "h=0.01 constraint threshold satisfied: `False`.",
        "Single implementation defect proven by this diagnosis: `False`.",
        "Coarse h constraint failure components: `['endpoint_velocity_constraint']`.",
        "Fine-pair floor margin to threshold: `0.176` with finest/reference h ratio `10.000`.",
        "Ledger binding reconciliation: local metrics present `True`, accepted binding `False`, ledger RA2021 remaining evidence per row `4`, row status shrink `False`.",
        "## Final-vs-Trajectory Order Sensitivity",
        "| `pos_final_linf` | `0.01_to_0.002` | `80.234` | `2.725` |",
        "| `vel_final_linf` | `0.01_to_0.002` | `40.379` | `2.298` |",
        "Promotion ready: `False`.",
        "Source-policy rows promoted by this diagnosis: `0`.",
        "B4/B7 can close from this diagnosis: `False`.",
        "These rows remain a root-cause diagnostic for B4/B7, not row-closure or external-superiority evidence.",
    ]:
        checks.check(token in audit_md, f"markdown missing token: {token}")

    if checks.errors:
        print("RA2021 double source-policy low-order diagnosis validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("RA2021 double source-policy low-order diagnosis validation: PASS")
    print("rows_complete=True")
    print("aggregate_order_acceptance_satisfied=False")
    print("fine_pair_floor_limited=True")
    print("source_policy_rows_promoted=0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
