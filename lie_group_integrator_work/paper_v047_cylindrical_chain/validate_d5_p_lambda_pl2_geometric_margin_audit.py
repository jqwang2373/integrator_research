#!/usr/bin/env python3
"""Validate the D5 P_lambda PL2 geometric-margin audit."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
AUDIT_JSON = PAPER / "D5_P_LAMBDA_PL2_GEOMETRIC_MARGIN_AUDIT.json"
AUDIT_MD = PAPER / "D5_P_LAMBDA_PL2_GEOMETRIC_MARGIN_AUDIT.md"


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


def main() -> int:
    checks = Checks()
    try:
        audit = read_json(AUDIT_JSON)
        audit_md = AUDIT_MD.read_text(encoding="utf-8", errors="replace")
        p_lambda_interface = read_json(PAPER / "D5_P_LAMBDA_INTERFACE_AUDIT.json")
        p_lambda_inf_sup_probe = read_json(PAPER / "D5_P_LAMBDA_INF_SUP_PROBE.json")
        p_lambda_d3 = read_json(PAPER / "D5_P_LAMBDA_D3_NONCIRCULARITY_AUDIT.json")
        p_tube = read_json(PAPER / "D5_P_TUBE_CONSTANTS_AUDIT.json")
        proof_manifest = read_json(PAPER / "PROOF_CLOSURE_MANIFEST.json")
    except Exception as exc:  # noqa: BLE001
        print(f"D5 P_lambda PL2 geometric-margin audit validation: FAIL\n- {exc}")
        return 1

    summary = audit.get("summary", {})
    source = audit.get("source_consistency", {})
    claim = audit.get("claim_boundary", {})
    compactness = audit.get("compact_tube_reduction", {})
    structure = audit.get("symbolic_structure_certificate", {})
    axis_cert = audit.get("axis_plane_margin_certificate", {})
    rows = audit.get("rows", [])

    checks.check(audit.get("schema") == "d5-p-lambda-pl2-geometric-margin-audit-v1", "schema changed")
    checks.check(
        audit.get("status") == "pl2_uniform_inf_sup_bound_proved_p_lambda_rate_open",
        "status changed",
    )
    checks.check(audit.get("read_only") is True, "audit must be read-only")
    checks.check(audit.get("run_v047_invoked") is False, "run_v047 must not be invoked")
    checks.check(audit.get("one_step_stage_newton_invoked") is True, "finite stage probe not recorded")
    checks.check(audit.get("submission_ready") is False, "submission readiness overclaimed")
    checks.check(audit.get("pc2_closed") is False, "PC2 unexpectedly closed")
    checks.check(audit.get("proof_gap_closed") is False, "proof gap unexpectedly closed")
    checks.check(audit.get("primitive_closed") is False, "P_lambda unexpectedly closed")
    checks.check(audit.get("pl2_uniform_inf_sup_bound_proved") is True, "PL2 uniform inf-sup not proved")
    checks.check(audit.get("uniform_compact_tube_margin_proved") is True, "uniform margin not proved")
    checks.check(
        audit.get("symbolic_transversality_over_compact_tube_proved") is True,
        "symbolic compact-tube transversality not proved",
    )
    checks.check(audit.get("multiplier_lift_rate_proved") is False, "multiplier lift overclaimed")
    checks.check(audit.get("term_bounds_proved") == 0, "Taylor bounds unexpectedly proved")
    checks.check(audit.get("pl2_geometric_margin_route_recorded") is True, "PL2 route not recorded")
    checks.check(audit.get("finite_stage_margin_probe_recorded") is True, "finite margin probe not recorded")
    checks.check(audit.get("h_values") == [0.04, 0.02, 0.01], "h-values changed")
    checks.check(audit.get("stage_count") == 3, "stage count changed")

    checks.check(summary.get("probe_stage_rows") == 9, "probe stage row count changed")
    checks.check(summary.get("finite_full_stage_rank_all") is True, "full stage rank diagnostic missing")
    checks.check(
        summary.get("finite_translational_normal_rank_all") is True,
        "translational normal rank diagnostic missing",
    )
    checks.check(
        summary.get("finite_rotational_axis_torque_rank_all") is True,
        "rotational torque rank diagnostic missing",
    )
    checks.check(summary.get("finite_direct_sum_rank_all") is True, "direct-sum rank diagnostic missing")
    checks.check(summary.get("compact_tube_reduction_recorded") is True, "compact-tube reduction missing")
    checks.check(
        summary.get("symbolic_structure_certificate_recorded") is True,
        "symbolic structure certificate missing",
    )
    checks.check(summary.get("normal_force_margin_proved") is True, "normal-force margin not proved")
    checks.check(
        summary.get("smooth_friction_orthogonal_perturbation_proved") is True,
        "smooth-friction orthogonal perturbation proof missing",
    )
    checks.check(
        summary.get("translational_normal_subblock_lower_bound_proved") is True,
        "translational normal lower-bound proof missing",
    )
    checks.check(
        abs(float(summary.get("translational_normal_subblock_symbolic_lower_bound", 0.0)) - 0.6180339887498949)
        < 1.0e-12,
        "translational normal symbolic lower bound changed",
    )
    checks.check(
        summary.get("axis_torque_margin_formula_recorded") is True,
        "axis-torque margin formula not recorded",
    )
    checks.check(
        summary.get("axis_torque_compact_axis_margin_proved") is True,
        "axis-torque compact axis-plane margin not proved",
    )
    checks.check(
        summary.get("rotational_axis_torque_lower_bound_conditional") is False,
        "rotational axis-torque bound still marked conditional",
    )
    checks.check(
        summary.get("rotational_axis_torque_lower_bound_proved") is True,
        "rotational axis-torque lower bound not proved",
    )
    checks.check(
        summary.get("full_dynamic_lambda_lower_bound_conditional") is False,
        "full dynamic-lambda bound still marked conditional",
    )
    checks.check(
        summary.get("full_dynamic_lambda_lower_bound_proved") is True,
        "full dynamic-lambda lower bound not proved",
    )
    checks.check(summary.get("symbolic_margin_premise_proved") is True, "symbolic margin premise not proved")
    for key in [
        "min_full_dynamic_lambda_singular",
        "min_translational_normal_singular",
        "min_rotational_axis_torque_singular",
        "min_direct_sum_singular",
    ]:
        checks.check(float(summary.get(key, 0.0)) > 0.0, f"{key} is not positive")
    checks.check(summary.get("pl2_uniform_inf_sup_bound_proved") is True, "summary does not close PL2")
    checks.check(summary.get("pc2_closed") is False, "summary overclaims PC2")
    checks.check(compactness.get("reduction_recorded") is True, "compactness reduction not recorded")
    checks.check(
        compactness.get("conditional_uniform_inf_sup_if_symbolic_margin") is True,
        "conditional compactness implication missing",
    )
    checks.check(
        compactness.get("symbolic_margin_premise_proved") is True,
        "compactness premise not proved",
    )
    checks.check(
        compactness.get("finite_probe_sufficient_for_symbolic_margin") is False,
        "finite probe incorrectly proves symbolic margin",
    )
    checks.check(compactness.get("closes_pl2") is True, "compactness reduction does not close PL2")
    checks.check(compactness.get("uses_stage_residual_defect") is False, "compactness reduction uses stage residual")
    checks.check(
        compactness.get("uses_direct_substitution_as_proof") is False,
        "compactness reduction uses direct substitution proof",
    )
    checks.check(
        "continuity plus compactness" in compactness.get("compactness_argument", ""),
        "compactness argument missing continuity/compactness text",
    )
    checks.check(
        len(compactness.get("required_symbolic_premises", [])) == 4,
        "required symbolic premise count changed",
    )
    checks.check(
        len(compactness.get("proved_symbolic_premises", [])) == 6,
        "proved symbolic premise count changed",
    )
    checks.check(compactness.get("open_symbolic_premises", []) == [], "symbolic premises still open")
    checks.check("PL4 multiplier-rate" in compactness.get("remaining_gap", ""), "PL4 remaining-gap boundary missing")

    checks.check(axis_cert.get("certificate_recorded") is True, "axis-plane margin certificate not recorded")
    checks.check(axis_cert.get("proved") is True, "axis-plane margin certificate not proved")
    checks.check(axis_cert.get("uses_finite_probe_as_proof") is False, "axis-plane margin uses finite probe")
    checks.check(axis_cert.get("uses_stage_residual_defect") is False, "axis-plane margin uses stage residual")
    checks.check(
        axis_cert.get("uses_direct_substitution_as_proof") is False,
        "axis-plane margin uses direct substitution as proof",
    )
    checks.check(
        "sigma_min(C(a,R,B))" in axis_cert.get("singular_identity", ""),
        "axis-plane singular identity missing",
    )
    checks.check("m_j(z)" in axis_cert.get("margin_function", ""), "axis-plane margin function missing")
    checks.check(
        "constant-rank active lower-pair constraint Jacobian" in axis_cert.get("regularity_source", ""),
        "axis-plane regularity source missing",
    )
    checks.check("chi_axis" in axis_cert.get("compactness_argument", ""), "axis-plane compactness margin missing")
    checks.check(axis_cert.get("axis_torque_compact_axis_margin_proved") is True, "axis margin flag missing")

    checks.check(structure.get("certificate_recorded") is True, "symbolic structure certificate not recorded")
    checks.check(structure.get("uses_finite_probe_as_proof") is False, "symbolic structure uses finite probe")
    checks.check(structure.get("uses_stage_residual_defect") is False, "symbolic structure uses stage residual")
    checks.check(
        structure.get("uses_direct_substitution_as_proof") is False,
        "symbolic structure uses direct substitution as proof",
    )
    normal = structure.get("normal_force_and_friction_subblock", {})
    checks.check(normal.get("proved") is True, "normal-force/friction subblock not proved")
    checks.check("B + a c^T" in normal.get("jacobian_formula", ""), "normal-force Jacobian formula missing")
    checks.check("I + c c^T" in normal.get("gram_identity", ""), "normal-force Gram identity missing")
    checks.check(
        float(normal.get("joint_subblock_sigma_min_lower_bound", 0.0)) == 1.0,
        "normal-force joint lower bound changed",
    )
    checks.check(
        normal.get("friction_derivative_can_reduce_rank") is False,
        "friction derivative incorrectly allowed to reduce rank",
    )
    trans = structure.get("translational_action_reaction_subblock", {})
    checks.check(trans.get("proved") is True, "translational action-reaction bound not proved")
    checks.check(trans.get("assembly") == "[[-A0, A1], [0, -A1]]", "translational assembly changed")
    checks.check(
        abs(float(trans.get("sigma_min_lower_bound", 0.0)) - 0.6180339887498949) < 1.0e-12,
        "translational action-reaction lower bound changed",
    )
    axis = structure.get("axis_torque_subblock", {})
    checks.check(axis.get("formula_recorded") is True, "axis-torque formula missing")
    checks.check("sigma_min(C)=|(R a).n_B|" in axis.get("single_joint_formula", ""), "axis formula missing")
    checks.check(axis.get("compact_axis_plane_margin_required") is True, "axis-plane margin requirement missing")
    checks.check(axis.get("compact_axis_plane_margin_proved") is True, "axis-plane margin not proved")
    checks.check(axis.get("margin_source") == "axis_plane_margin_certificate", "axis margin source missing")
    rot = structure.get("rotational_action_reaction_subblock", {})
    checks.check(rot.get("conditional_bound_recorded") is False, "rotational bound still conditional")
    checks.check(
        rot.get("compact_axis_plane_margin_proved") is True,
        "rotational subblock does not carry axis-plane margin",
    )
    checks.check(rot.get("lower_bound_proved") is True, "rotational lower bound not proved")
    checks.check("beta_D" in rot.get("bound_formula", ""), "rotational bound formula missing beta_D")
    checks.check("gamma_R" in rot.get("lower_bound_symbol", ""), "rotational bound symbol missing")
    full = structure.get("full_dynamic_lambda_block", {})
    checks.check(full.get("conditional_bound_recorded") is False, "full block still conditional")
    checks.check(full.get("lower_bound_proved") is True, "full block lower bound not proved")
    checks.check(full.get("translational_lower_bound_proved") is True, "full block lost translational proof")
    checks.check(
        full.get("rotational_lower_bound_requires_axis_margin") is False,
        "full block still requires unproved axis margin",
    )
    checks.check(full.get("rotational_lower_bound_proved") is True, "full block lost rotational proof")
    checks.check("gamma_PL2" in full.get("lower_bound_symbol", ""), "full PL2 bound symbol missing")
    checks.check(full.get("closes_pl2") is True, "symbolic structure does not close PL2")
    checks.check(
        "PL4 multiplier-rate" in structure.get("remaining_gap", ""),
        "symbolic structure PL4 remaining gap missing",
    )

    checks.check(isinstance(rows, list) and len(rows) == 9, "row diagnostics missing")
    for row in rows:
        if not isinstance(row, dict):
            checks.check(False, "row diagnostic is not an object")
            continue
        checks.check(row.get("case") == "cylindrical_smooth", "case changed")
        checks.check(row.get("stage") in [0, 1, 2], "stage changed")
        for block_key in [
            "full_dynamic_lambda_block",
            "translational_normal_subblock",
            "rotational_axis_torque_subblock",
            "direct_sum_subblock",
        ]:
            block = row.get(block_key, {})
            checks.check(block.get("full_column_rank") is True, f"{block_key} not full column rank")
            checks.check(float(block.get("min_singular_value", 0.0)) > 0.0, f"{block_key} singular value not positive")

    checks.check(audit.get("source_trace", {}).get("complete") is True, "source trace incomplete")
    for token, present in audit.get("source_trace", {}).get("tokens", {}).items():
        checks.check(present is True, f"source trace token missing: {token}")

    checks.check(source.get("p_lambda_interface_schema") == p_lambda_interface.get("schema"), "PL1 schema link missing")
    checks.check(
        source.get("p_lambda_interface_closed") is True
        and p_lambda_interface.get("pl1_interface_closed") is True,
        "PL1 interface closure missing",
    )
    checks.check(source.get("p_lambda_inf_sup_probe_schema") == p_lambda_inf_sup_probe.get("schema"), "PL2 probe schema link missing")
    checks.check(
        source.get("p_lambda_inf_sup_probe_full_column_rank_all") is True
        and p_lambda_inf_sup_probe.get("summary", {}).get("finite_probe_full_column_rank_all") is True,
        "finite inf-sup probe rank missing",
    )
    checks.check(
        source.get("p_lambda_inf_sup_probe_uniform_constant_proved") is False
        and p_lambda_inf_sup_probe.get("uniform_constant_proved") is False,
        "finite inf-sup probe overclaims uniform constant",
    )
    checks.check(source.get("p_lambda_d3_schema") == p_lambda_d3.get("schema"), "PL3 schema link missing")
    checks.check(
        source.get("p_lambda_d3_closed") is True and p_lambda_d3.get("pl3_d3_noncircularity_closed") is True,
        "PL3 closure link missing",
    )
    checks.check(source.get("p_tube_schema") == p_tube.get("schema"), "P_tube schema link missing")
    checks.check(source.get("p_tube_closed") is True, "P_tube closure link missing")
    checks.check(source.get("proof_manifest_pc2_closed") is True, "proof manifest direct PC2 closure not reflected")
    checks.check(
        source.get("proof_manifest_proof_gap_closed") is True
        and proof_manifest.get("closure_state", {}).get("pc2_closed_by_direct_substitution") is True,
        "proof manifest direct-substitution closure not reflected",
    )
    checks.check(
        proof_manifest.get("closure_state", {}).get("primitive_lift_route_closed") is False,
        "proof manifest unexpectedly closes primitive lift route",
    )

    checks.check(
        audit.get("conditional_pl2_implication", {}).get("finite_probe_sufficient_for_uniform_proof") is False,
        "finite probe incorrectly marked sufficient for PL2",
    )
    checks.check(
        audit.get("conditional_pl2_implication", {}).get("required_missing_uniform_inputs", []) == [],
        "PL2 uniform inputs still marked missing",
    )
    checks.check(
        len(audit.get("conditional_pl2_implication", {}).get("closed_uniform_inputs", [])) == 3,
        "closed PL2 uniform inputs changed",
    )
    checks.check(audit.get("manuscript_link", {}).get("main_tex_present") is True, "main TeX link missing")
    checks.check(audit.get("manuscript_link", {}).get("flat_tex_present") is True, "flat TeX link missing")
    checks.check(
        audit.get("manuscript_link", {}).get("tokens")
        == [
            "PL2 geometric-margin diagnostic",
            r"\label{lem:d5-p-lambda-pl2-symbolic-structure}",
            "PL2 multiplier-column symbolic structure",
            "normal-force and smooth-friction subblock",
            "axis-plane margin",
            r"\label{lem:d5-p-lambda-pl2-axis-plane-margin}",
            "PL2 axis-plane margin on the accepted compact tube",
            r"\label{lem:d5-p-lambda-pl2-compact-reduction}",
            "PL2 compact-tube reduction",
            "These finite margins identify the geometric proof target",
            "not a uniform compact-tube inf-sup proof",
            "PL2 is closed as a uniform inf-sup subproof",
            "the PC2 route both remain open",
        ],
        "manuscript token set changed",
    )

    for forbidden in [
        "P_lambda primitive closure",
        "multiplier lift-rate proof",
        "D5 Taylor term certification through P_lambda",
        "primitive/Taylor PC2 route closure",
    ]:
        checks.check(forbidden in claim.get("forbidden_now", []), f"forbidden claim missing: {forbidden}")

    for token in [
        "Status: **PL2 uniform inf-sup bound proved; P_lambda rate remains open**.",
        "Probe stage rows: `9`.",
        "Full dynamic-lambda blocks full column rank: `True`.",
        "Translational normal-force subblocks full column rank: `True`.",
        "Rotational axis-torque subblocks full column rank: `True`.",
        "Direct-sum subblocks full column rank: `True`.",
        "Compact-tube reduction recorded: `True`.",
        "Symbolic structure certificate recorded: `True`.",
        "Normal-force margin proved: `True`.",
        "Smooth-friction orthogonal perturbation proved: `True`.",
        "Translational normal symbolic lower bound: `6.1803398874989490e-01`.",
        "Axis-torque compact axis-plane margin proved: `True`.",
        "Symbolic Structure Certificate",
        "normal-load derivative is",
        "chart transversality certificate",
        "Axis-Plane Margin Certificate",
        "chi_axis=min_K min_j m_j>0",
        "Symbolic margin premise proved: `True`.",
        "Compact-Tube Reduction",
        "establish that premise.",
        "Uniform compact-tube margin proved: `True`.",
        "PL2 uniform inf-sup bound proved: `True`.",
        "P_lambda primitive closed: `False`.",
        "Primitive/Taylor PC2 route closed: `False`.",
        "Finite margin probes do not prove the compact-tube transversality margin.",
        "PL2 is closed as a uniform inf-sup subproof.",
        "`P_lambda` remains open.",
    ]:
        checks.check(token in audit_md, f"markdown missing token: {token}")

    if checks.errors:
        print("D5 P_lambda PL2 geometric-margin audit validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("D5 P_lambda PL2 geometric-margin audit validation: PASS")
    print("probe_stage_rows=9")
    print("pl2_uniform_inf_sup_bound_proved=True")
    print("pc2_closed=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
