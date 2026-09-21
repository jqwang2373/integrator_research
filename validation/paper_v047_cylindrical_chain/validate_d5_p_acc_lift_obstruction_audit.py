#!/usr/bin/env python3
"""Validate the D5 P_acc PA2 lift-obstruction audit."""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
ROOT = PAPER.parent.parent
REF_TXT = ROOT / "external" / "literature" / "s11044-026-10153-w.txt"
RUN_V047 = PAPER.parent.parent / "numerics" / "v047_cylindrical_chain_pipeline" / "run_v047.py"
AUDIT_JSON = PAPER / "D5_P_ACC_LIFT_OBSTRUCTION_AUDIT.json"
AUDIT_MD = PAPER / "D5_P_ACC_LIFT_OBSTRUCTION_AUDIT.md"


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


def contains_normalized(text: str, token: str) -> bool:
    return token in text or " ".join(token.split()) in " ".join(text.split())


def main() -> int:
    checks = Checks()
    try:
        audit = read_json(AUDIT_JSON)
        audit_md = read_text(AUDIT_MD)
        reference_text = read_text(REF_TXT)
        run_v047_text = read_text(RUN_V047)
        p_acc_independence = read_json(PAPER / "D5_P_ACC_INDEPENDENCE_AUDIT.json")
        p_acc_row_binding = read_json(PAPER / "D5_P_ACC_ROW_BINDING_AUDIT.json")
        p_state_gap = read_json(PAPER / "D5_P_STATE_LIFT_GAP_AUDIT.json")
        kinematic = read_json(PAPER / "KINEMATIC_ROW_DEFECT_CERTIFICATE.json")
    except Exception as exc:  # noqa: BLE001
        print(f"D5 P_acc lift-obstruction audit validation: FAIL\n- {exc}")
        return 1

    gauss = audit.get("gauss_matrix", {})
    algebra = audit.get("rate_algebra", {})
    reference = audit.get("reference_paper_scaling_context", {})
    implementation = audit.get("implementation_row_scaling_evidence", {})
    source = audit.get("source_consistency", {})
    claim = audit.get("claim_boundary", {})

    checks.check(audit.get("schema") == "d5-p-acc-lift-obstruction-audit-v1", "schema changed")
    checks.check(
        audit.get("status") == "p_acc_pa2_obstruction_recorded_lift_open",
        "status changed",
    )
    checks.check(audit.get("read_only") is True, "audit must be read-only")
    checks.check(audit.get("run_v047_invoked") is False, "run_v047 must not be invoked")
    checks.check(audit.get("submission_ready") is False, "submission readiness overclaimed")
    checks.check(audit.get("pc2_closed") is False, "PC2 unexpectedly closed")
    checks.check(audit.get("proof_gap_closed") is False, "proof gap unexpectedly closed")
    checks.check(audit.get("primitive_id") == "P_acceleration_lift", "primitive id changed")
    checks.check(audit.get("primitive_closed") is False, "P_acc unexpectedly closed")
    checks.check(audit.get("pa2_closed") is False, "PA2 unexpectedly closed")
    checks.check(audit.get("pa2_obstruction_recorded") is True, "PA2 obstruction not recorded")
    checks.check(
        audit.get("velocity_collocation_alone_sufficient_for_O_h7_acceleration") is False,
        "velocity-collocation sufficiency overclaimed",
    )
    checks.check(
        audit.get("current_recorded_inputs_imply_only_unweighted_acceleration_rate") == "O(h^6)",
        "rate-loss conclusion changed",
    )
    checks.check(audit.get("acceleration_lift_rate_proved") is False, "acceleration lift overclaimed")
    checks.check(audit.get("term_bounds_proved") == 0, "Taylor bounds unexpectedly proved")
    checks.check(gauss.get("stage_count") == 3, "Gauss stage count changed")
    checks.check(gauss.get("invertible") is True, "Gauss matrix should be invertible")
    checks.check(math.isfinite(float(gauss.get("determinant"))), "determinant not finite")
    checks.check(abs(float(gauss.get("determinant"))) > 1.0e-6, "determinant too small")
    checks.check(math.isfinite(float(gauss.get("inverse_inf_norm"))), "inverse inf norm not finite")
    checks.check(float(gauss.get("inverse_inf_norm")) > 1.0, "inverse inf norm unexpectedly small")
    checks.check(math.isfinite(float(gauss.get("condition_2"))), "condition number not finite")
    checks.check(
        algebra.get("velocity_collocation_difference")
        == "delta_V - h (A_G \\otimes I) delta_A = rho_V",
        "velocity-collocation algebra changed",
    )
    checks.check(
        algebra.get("acceleration_difference")
        == "delta_A = h^{-1} (A_G^{-1} \\otimes I) (delta_V - rho_V)",
        "acceleration inversion algebra changed",
    )
    checks.check(
        algebra.get("if_delta_v_and_rho_v_are_O_h7") == "delta_A is bounded only as O(h^6)",
        "rate-loss statement changed",
    )
    close_conditions = algebra.get("needed_for_unweighted_delta_A_O_h7", [])
    checks.check(len(close_conditions) == 3, "PA2 close-condition count changed")
    checks.check(
        any("delta_V=O(h^8)" in item for item in close_conditions),
        "stronger velocity-stage condition missing",
    )
    checks.check(
        any("non-dynamic stage-map inverse" in item for item in close_conditions),
        "non-dynamic inverse condition missing",
    )
    checks.check(
        any("P_acceleration_lift=O(h^7)" in item for item in close_conditions),
        "explicit P_acc assumption condition missing",
    )
    checks.check(
        algebra.get("weighted_h_delta_A_O_h7_is_not_enough_for_current_D5_budget") is True,
        "weighted-norm boundary missing",
    )
    checks.check(
        reference.get("reference_text") == "../../external/literature/s11044-026-10153-w.txt",
        "reference paper text path changed",
    )
    checks.check(
        reference.get("supports_obstruction_not_closure") is True,
        "reference scaling context must support obstruction only",
    )
    checks.check(reference.get("usable_as_p_acc_proof") is False, "reference context overclaims P_acc proof")
    checks.check(
        "does not supply the missing unweighted O(h^7)" in reference.get("interpretation", ""),
        "reference interpretation missing unweighted-bound limitation",
    )
    checks.check(
        "without an extra h factor" in reference.get("why_not", ""),
        "reference why-not explanation missing unweighted D5 scaling",
    )
    checks.check(
        "P_acceleration_lift=O(h^7)" in reference.get("strict_consequence", ""),
        "reference strict consequence missing explicit assumption route",
    )
    reference_tokens = reference.get("tokens", {})
    reference_features = reference.get("features", {})
    expected_reference_tokens = {
        "tfe_section_present": "3 Higher order time integration in absolute coordinates using TFE",
        "first_order_derivative_scaling_present": "δv = h1 δu and δ v̇ = h12 δu",
        "differential_residuals_present": "res1 (t) = ẋ(t) − y(t),       res2 (t) = ẏ(t) − z(t)",
        "velocity_from_position_relation_present": "ȳ = x̄˙ = 𝜶¯ x̄",
        "acceleration_from_velocity_relation_present": "z̄ = x̄¨ = 𝜶¯ ȳ",
        "newton_correction_derivative_relation_present": "δ x̄˙ = 𝜶¯ δ x̄,   δ x̄¨ = 𝜶¯ δ x̄˙",
    }
    checks.check(reference_tokens == expected_reference_tokens, "reference token set changed")
    for key, token in expected_reference_tokens.items():
        checks.check(contains_normalized(reference_text, token), f"reference source missing token: {key}")
        checks.check(reference_features.get(key) is True, f"reference feature not recorded true: {key}")
    expected_implementation_tokens = {
        "runtime_newton_euler_row_layout_present": '("newton_euler_weak_balance", 24, 12)',
        "runtime_lower_pair_acceleration_constraint_layout_present": (
            '("lower_pair_index3_weak_constraints", 36, 8)'
        ),
        "runtime_velocity_row_layout_present": '("translational_velocity_weak_defect", 12, 6)',
        "runtime_angular_velocity_row_layout_present": '("angular_velocity_weak_defect", 18, 6)',
        "translational_velocity_collocation_uses_h_times_acceleration": (
            'v_coll_axis = (kin["rel_vel"][joint] - initial_rel_vel[joint] - h * sum('
        ),
        "translational_velocity_collocation_uses_relative_acceleration": (
            'stage_kin[sj]["rel_acc"][joint]'
        ),
        "angular_velocity_collocation_uses_h_times_acceleration": (
            'spin_acc_coll_axis = kin["rel_spin_vel"][joint] - initial_rel_spin_vel[joint] - h * sum('
        ),
        "angular_velocity_collocation_uses_relative_spin_acceleration": (
            'stage_kin[sj]["rel_spin_acc"][joint]'
        ),
        "dynamic_translational_rows_use_unweighted_acceleration": (
            'trans = masses[body] * st["a"][body]'
        ),
        "dynamic_rotational_rows_use_unweighted_angular_acceleration": (
            'Js[body] @ st["alpha"][body]'
        ),
        "runtime_stage_row_assembly_order_present": (
            "out.extend([jnp.concatenate(pvel), jnp.concatenate(u_block), "
            "jnp.concatenate(pacc), jnp.concatenate(w_block), "
            "jnp.concatenate(dyn), jnp.concatenate(constraints)])"
        ),
    }
    checks.check(
        implementation.get("run_v047_path") == "../../numerics/v047_cylindrical_chain_pipeline/run_v047.py",
        "implementation run_v047 path changed",
    )
    checks.check(
        implementation.get("tokens") == expected_implementation_tokens,
        "implementation token set changed",
    )
    implementation_features = implementation.get("features", {})
    for key, token in expected_implementation_tokens.items():
        checks.check(contains_normalized(run_v047_text, token), f"run_v047 source missing token: {key}")
        checks.check(implementation_features.get(key) is True, f"implementation feature not recorded true: {key}")
    checks.check(
        "h*A_G" in implementation.get("row_layout_conclusion", "")
        and "without an extra h factor" in implementation.get("row_layout_conclusion", ""),
        "implementation row-layout conclusion missing h-scaling contrast",
    )
    checks.check(
        "do not provide a full unweighted inverse" in implementation.get("lower_pair_boundary", ""),
        "lower-pair boundary missing full-inverse limitation",
    )
    checks.check(
        implementation.get("supports_obstruction_not_closure") is True,
        "implementation scaling context must support obstruction only",
    )
    checks.check(
        implementation.get("usable_as_unweighted_acceleration_lift_proof") is False,
        "implementation context overclaims unweighted acceleration proof",
    )
    checks.check(
        "delta A=O(h^7)" in implementation.get("strict_consequence", ""),
        "implementation strict consequence missing unweighted acceleration requirement",
    )
    checks.check(
        source.get("p_acc_independence_schema") == p_acc_independence.get("schema")
        and source.get("p_acc_independence_closed") is True
        and p_acc_independence.get("pa3_independence_closed") is True,
        "P_acc independence link missing",
    )
    checks.check(source.get("p_acc_independence_pa2_open") is True, "PA2 open marker missing")
    checks.check(
        source.get("p_acc_row_binding_schema") == p_acc_row_binding.get("schema")
        and source.get("p_acc_row_binding_closed") is True,
        "P_acc row-binding link missing",
    )
    checks.check(
        source.get("p_state_gap_schema") == p_state_gap.get("schema")
        and source.get("p_state_closed") is False
        and source.get("p_state_future_subproofs_closed") == 3,
        "P_state gap link missing",
    )
    checks.check(
        source.get("kinematic_certificate_schema") == kinematic.get("schema")
        and source.get("certified_non_dynamic_rows") == 96
        and source.get("dynamic_family_excluded") == "newton_euler_weak_balance",
        "kinematic certificate link missing",
    )
    checks.check(audit.get("manuscript_link", {}).get("main_tex_present") is True, "main TeX lemma link missing")
    checks.check(audit.get("manuscript_link", {}).get("flat_tex_present") is True, "flat TeX lemma link missing")
    for forbidden in [
        "P_acc primitive closure",
        "PA2 closure",
        "acceleration lift O(h^7) proved",
        "Taylor term bounds certified from P_acc",
        "primitive/Taylor PC2 route closure",
        "unconditional sixth-order theorem",
    ]:
        checks.check(forbidden in claim.get("forbidden_now", []), f"forbidden claim missing: {forbidden}")

    for token in [
        "Status: **PA2 obstruction recorded; P_acc lift remains open**.",
        "PA2 closed: `False`.",
        "P_acc primitive closed: `False`.",
        "Velocity-collocation alone sufficient for O(h^7) acceleration: `False`.",
        "Current recorded inputs imply only: `O(h^6)`.",
        "Acceleration lift rate proved: `False`.",
        "Taylor bounds proved: `0/36`.",
        "Primitive/Taylor PC2 route closed: `False`.",
        "delta_V - h (A_G \\otimes I) delta_A = rho_V",
        "delta_A = h^{-1} (A_G^{-1} \\otimes I) (delta_V - rho_V)",
        "External TFE Scaling Context (Diagnostic Only)",
        "Runtime Row-Scaling Evidence",
        "velocity-collocation rows contain acceleration through `h A_G`",
        "Newton-Euler rows use `m_b a` and `J_b alpha` without an",
        "do not form a full unweighted inverse",
        "This supports the",
        "PA2 obstruction rather than closing it",
        "unweighted `delta A=O(h^7)` estimate",
        "This audit sharpens PA2; it does not close PA2.",
        "`P_acc` remains open.",
        "Primitive/Taylor PC2 lane remains open.",
    ]:
        checks.check(token in audit_md, f"markdown missing token: {token}")

    if checks.errors:
        print("D5 P_acc lift-obstruction audit validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("D5 P_acc lift-obstruction audit validation: PASS")
    print("pa2_closed=False")
    print("velocity_collocation_alone_sufficient=False")
    print("current_unweighted_acceleration_rate=O(h^6)")
    print("pc2_closed=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
