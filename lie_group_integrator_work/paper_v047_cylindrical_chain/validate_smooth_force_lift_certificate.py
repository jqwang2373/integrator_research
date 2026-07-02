#!/usr/bin/env python3
"""Validate the smooth force/friction lift certificate."""

from __future__ import annotations

import ast
import json
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
ROOT = PAPER.parent
CERT_JSON = PAPER / "SMOOTH_FORCE_LIFT_CERTIFICATE.json"
CERT_MD = PAPER / "SMOOTH_FORCE_LIFT_CERTIFICATE.md"
V047 = ROOT / "v047_cylindrical_chain_pipeline" / "run_v047.py"
V043 = ROOT / "v043_skew_prismatic_lower_pair" / "run_v043.py"
SUMMARY = ROOT / "v047_cylindrical_chain_pipeline" / "results" / "summary_v047.json"


class Checks:
    def __init__(self) -> None:
        self.errors: list[str] = []

    def check(self, condition: bool, message: str) -> None:
        if not condition:
            self.errors.append(message)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def normalized(text: str) -> str:
    return " ".join(text.split())


def find_function_source(source: str, name: str) -> str:
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return normalized(ast.get_source_segment(source, node) or "")
    return ""


def main() -> int:
    checks = Checks()
    try:
        cert = read_json(CERT_JSON)
        cert_md = read_text(CERT_MD)
        v047_source = read_text(V047)
        v043_source = read_text(V043)
        summary = read_json(SUMMARY)
    except Exception as exc:  # noqa: BLE001
        print(f"smooth_force_lift_certificate=FAIL\n- {exc}")
        return 1

    v043_friction = find_function_source(v043_source, "brown_mcphee_scalar_jax")
    v047_residual = find_function_source(v047_source, "residual_cylindrical_chain")
    v047_make_params = find_function_source(v047_source, "make_params")
    friction_sweep = summary.get("friction_smoothness_sweep", {})
    sweep_cases = friction_sweep.get("cases", {})

    checks.check(cert.get("schema") == "smooth-force-lift-certificate-v1", "schema changed")
    checks.check(
        cert.get("status") == "smooth_force_lift_c7_tube_bound_closed_dynamic_defect_open",
        "status changed",
    )
    checks.check(cert.get("submission_ready") is False, "certificate overclaims submission readiness")
    checks.check(cert.get("certificate_complete") is True, "D4 certificate should now be complete")
    checks.check(cert.get("proof_gap_closed") is False, "certificate unexpectedly closes proof gap")
    checks.check(
        "false only for this D4 smooth-force certificate" in cert.get("proof_gap_closed_scope", ""),
        "smooth-force proof-gap scope missing",
    )
    checks.check(
        cert.get("smooth_force_lift_source_structure_checked") is True,
        "source structure check not recorded",
    )
    checks.check(
        cert.get("smooth_force_lift_consistency_closed") is True,
        "smooth-force consistency should be closed by compact-tube C7 audit",
    )
    checks.check(
        cert.get("global_C7_tube_derivative_bound_proved") is True,
        "global C7 tube derivative bound should be proved for the accepted smooth proof tube",
    )
    checks.check(
        cert.get("stage_residual_O_h7_implementation_defect_proved") is False,
        "dynamic O(h^7) proof overclaimed",
    )
    checks.check(
        "not proved by this D4 smooth-force certificate alone"
        in cert.get("stage_residual_O_h7_implementation_defect_proved_scope", ""),
        "smooth-force stage-residual scope missing",
    )
    checks.check(
        cert.get("active_direct_pc2_route_source") == "D5_DYNAMIC_DIRECT_SUBSTITUTION_CERTIFICATE.json",
        "smooth-force direct PC2 route source missing",
    )
    checks.check(cert.get("smooth_branch", {}).get("stribeck_velocity") == 0.5, "smooth branch changed")
    checks.check(cert.get("sharp_branch", {}).get("stribeck_velocity") == 0.05, "sharp branch changed")

    formula_checks = cert.get("formula_checks", {})
    for key in [
        "delegates_v047_to_v043",
        "positive_stribeck_floor",
        "tanh_dynamic_friction_term",
        "rational_static_transition_term",
        "positive_denominator_structure",
        "normal_load_multiplies_curve",
        "viscous_term_present",
        "no_state_sign_or_abs_branch",
    ]:
        checks.check(formula_checks.get(key) is True, f"formula check failed or missing: {key}")
    checks.check("jnp.maximum(stribeck_velocity, 1.0e-12)" in v043_friction, "stribeck floor missing in source")
    checks.check("mu_d * jnp.tanh(4.0 * z)" in v043_friction, "tanh term missing in source")
    checks.check("(mu_s - mu_d) * z / denom" in v043_friction, "rational transition missing in source")
    checks.check("denom = (0.25 * z * z + 0.75) ** 2" in v043_friction, "positive denominator missing")
    checks.check("jnp.sign" not in v043_friction and "jnp.abs" not in v043_friction, "state sign/abs branch added")

    normal_checks = cert.get("normal_load_regularization_checks", {})
    for key in [
        "normal_force_from_lambda_basis",
        "positive_sqrt_regularization",
        "slide_velocity_stage_local",
        "friction_uses_stage_local_normal_load",
        "friction_force_uses_parent_axis",
    ]:
        checks.check(normal_checks.get(key) is True, f"normal/load check failed or missing: {key}")
    checks.check("normal_force @ normal_force + jnp.array(1.0e-24" in v047_residual, "normal-load epsilon missing")
    checks.check('slide_vel = kin["rel_vel"][joint] @ kin["parent_axis"][joint]' in v047_residual, "stage slide velocity missing")
    checks.check('joint_force.append(normal_force + friction * kin["parent_axis"][joint])' in v047_residual, "joint force assembly changed")

    parameter_checks = cert.get("parameter_checks", {})
    for key in [
        "smooth_case_present",
        "sharp_case_separate",
        "friction_smoothness_velocities_recorded",
        "mu_s_positive",
        "mu_d_positive",
        "mu_s_ge_mu_d",
        "viscous_damping_positive",
        "friction_radius_positive",
        "external_forces_constant_arrays",
        "external_torques_constant_arrays",
    ]:
        checks.check(parameter_checks.get(key) is True, f"parameter check failed or missing: {key}")
    checks.check("mu_s=0.30" in v047_make_params and "mu_d=0.20" in v047_make_params, "friction coefficients changed")
    checks.check("viscous_damping=0.030" in v047_make_params, "viscous damping changed")
    checks.check("friction_radius=1.0" in v047_make_params, "friction radius changed")

    stage_checks = cert.get("stage_lift_checks", {})
    for key in [
        "uses_stage_kinematics",
        "uses_stage_variables",
        "uses_same_joint_kinematics_for_force_and_constraints",
        "force_rows_share_dynamic_stage",
    ]:
        checks.check(stage_checks.get(key) is True, f"stage-lift check failed or missing: {key}")

    sweep_checks = cert.get("friction_smoothness_sweep_checks", {})
    for key in [
        "summary_sweep_status_ok",
        "summary_sweep_velocity_grid_matches_source",
        "summary_sweep_cases_match_source",
        "smooth_case_has_high_order",
        "sharp_case_kept_diagnostic",
    ]:
        checks.check(sweep_checks.get(key) is True, f"sweep check failed or missing: {key}")
    checks.check(friction_sweep.get("status") == "ok", "friction smoothness sweep not ok")
    checks.check(sorted(sweep_cases) == ["stribeck_0p05", "stribeck_0p1", "stribeck_0p2", "stribeck_0p5"], "sweep cases changed")
    checks.check(float(sweep_cases.get("stribeck_0p5", {}).get("position_order", 0.0)) > 6.0, "smooth position order no longer high")
    checks.check(float(sweep_cases.get("stribeck_0p5", {}).get("velocity_order", 0.0)) > 6.0, "smooth velocity order no longer high")

    c7_audit = cert.get("compact_tube_c7_audit", {})
    checks.check(c7_audit.get("schema") == "compact-smooth-force-c7-audit-v1", "compact C7 schema changed")
    checks.check(c7_audit.get("proved") is True, "compact C7 audit not proved")
    checks.check(c7_audit.get("derivative_order") == 7, "compact C7 derivative order changed")
    c7_checks = c7_audit.get("checks", {})
    for key in [
        "source_structure_checked",
        "smooth_branch_positive_vs",
        "sharp_branch_excluded",
        "formula_components_smooth",
        "normal_load_regularized",
        "denominator_bounded_below",
        "fixed_positive_parameters",
        "stage_local_lift_checked",
    ]:
        checks.check(c7_checks.get(key) is True, f"compact C7 check failed or missing: {key}")
    bounds = c7_audit.get("positive_lower_bounds", {})
    checks.check(bounds.get("accepted_smooth_stribeck_velocity") == 0.5, "accepted smooth stribeck bound changed")
    checks.check(bounds.get("sharp_stribeck_velocity_excluded") == 0.05, "sharp branch exclusion changed")
    checks.check(bounds.get("sqrt_argument_lower_bound") == 1.0e-24, "normal-load lower bound changed")
    checks.check(bounds.get("rational_denominator_lower_bound") == 0.75**2, "rational denominator bound changed")
    checks.check(
        "excludes the sharp/small-stribeck diagnostic branch" in c7_audit.get("scope", ""),
        "compact C7 scope should exclude sharp branch",
    )
    checks.check(
        "does not prove dynamic-row O(h^7) defect" in c7_audit.get("scope", ""),
        "compact C7 scope should preserve dynamic-defect boundary",
    )

    execution = cert.get("execution_policy", {})
    checks.check(execution.get("read_only_existing_artifacts") is True, "certificate not read-only")
    checks.check(execution.get("default_1e_4_required") is False, "certificate requires default 1e-4")
    checks.check(execution.get("heavy_numerical_run_invoked") is False, "certificate invoked heavy run")
    checks.check(execution.get("run_v047_invoked") is False, "certificate invoked run_v047")
    checks.check(execution.get("v048_runner_invoked") is False, "certificate invoked v048 runner")

    forbidden = cert.get("claim_policy", {}).get("forbidden_now", [])
    for token in [
        "stage_residual_O_h7_implementation_defect_proved",
        "proof_gap_closed",
        "submission_ready",
    ]:
        checks.check(token in forbidden, f"forbidden claim missing: {token}")

    for token in [
        "Smooth Force Lift Certificate",
        "D4 CLOSED - smooth force/friction lift is C7 on the accepted compact proof tube",
        "Source structure checked: `True`.",
        "Smooth-force consistency closed: `True`.",
        "Global C7 tube derivative bound proved: `True`.",
        "Stage residual O(h^7) defect proved: `False`.",
        "Stage residual false scope:",
        "Direct PC2 route source:",
        "Compact Tube C7 Audit",
        "Brown-McPhee formula",
        "normal-load regularization",
        "stage-local FullVA lift",
        "closes only the D4 smooth force/friction lift sub-obligation",
        "validate_smooth_force_lift_certificate.py",
    ]:
        checks.check(token in cert_md, f"markdown missing token: {token}")

    if checks.errors:
        print("smooth_force_lift_certificate=FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("smooth_force_lift_certificate=PASS")
    print("source_structure_checked=True")
    print("smooth_force_lift_consistency_closed=True")
    print("global_C7_tube_derivative_bound_proved=True")
    print("proof_gap_closed=False")
    print("submission_ready=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
