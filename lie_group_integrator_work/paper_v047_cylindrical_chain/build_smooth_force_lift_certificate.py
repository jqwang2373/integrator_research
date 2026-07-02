#!/usr/bin/env python3
"""Build a read-only smooth force/friction lift certificate.

This certificate strengthens the D4 Newton-Euler proof obligation by checking
that the accepted smooth cylindrical-chain branch uses a regularized smooth
Brown-McPhee force expression evaluated on the same stage-local FullVA lift.
It closes only the D4 smooth force/friction lift sub-obligation: the scalar
force law is C7 with bounded derivatives on the accepted compact smooth proof
tube. It does not close dynamic-row symbolic equivalence or the O(h^7) defect
proof.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
ROOT = PAPER.parent
V047 = ROOT / "v047_cylindrical_chain_pipeline" / "run_v047.py"
V043 = ROOT / "v043_skew_prismatic_lower_pair" / "run_v043.py"
SUMMARY = ROOT / "v047_cylindrical_chain_pipeline" / "results" / "summary_v047.json"
OUT_JSON = PAPER / "SMOOTH_FORCE_LIFT_CERTIFICATE.json"
OUT_MD = PAPER / "SMOOTH_FORCE_LIFT_CERTIFICATE.md"


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


def parse_tree(source: str) -> ast.Module:
    return ast.parse(source)


def find_function_source(tree: ast.AST, source: str, name: str) -> str:
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return normalized(ast.get_source_segment(source, node) or "")
    return ""


def find_assignment_value(tree: ast.AST, name: str) -> Any:
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == name:
                    try:
                        return ast.literal_eval(node.value)
                    except Exception:  # noqa: BLE001
                        return None
    return None


def source_has_all(source: str, tokens: list[str]) -> bool:
    return all(token in source for token in tokens)


def compact_tube_c7_audit(
    checked: bool,
    formula_checks: dict[str, bool],
    normal_load_checks: dict[str, bool],
    parameter_checks: dict[str, bool],
    stage_lift_checks: dict[str, bool],
    cases: dict[str, Any],
) -> dict[str, Any]:
    smooth_vs = cases.get("cylindrical_smooth")
    sharp_vs = cases.get("cylindrical_sharp")
    positive_lower_bounds = {
        "accepted_smooth_stribeck_velocity": smooth_vs,
        "sharp_stribeck_velocity_excluded": sharp_vs,
        "v043_stribeck_floor": 1.0e-12,
        "normal_load_sqrt_epsilon": 1.0e-24,
        "sqrt_argument_lower_bound": 1.0e-24,
        "rational_denominator_lower_bound": 0.75**2,
    }
    derivative_bound_clauses = [
        "The accepted smooth branch fixes stribeck_velocity=0.5, so v/vs has a positive constant denominator.",
        "The Brown-McPhee curve uses arithmetic, tanh, and a rational term with denominator (0.25*z^2+0.75)^2 >= 0.75^2.",
        "The normal load uses sqrt(||normal_force||^2 + 1e-24), so the square-root argument is bounded away from zero.",
        "Constant gravity, external forces, external torques, positive friction radius, and positive viscous damping are fixed parameters.",
        "On any compact accepted smooth proof tube for the stage variables and multipliers, every derivative through order seven is continuous and attains a finite maximum.",
    ]
    checks = {
        "source_structure_checked": checked,
        "smooth_branch_positive_vs": smooth_vs == 0.50,
        "sharp_branch_excluded": sharp_vs == 0.05,
        "formula_components_smooth": all(formula_checks.values()),
        "normal_load_regularized": normal_load_checks.get("positive_sqrt_regularization") is True,
        "denominator_bounded_below": formula_checks.get("positive_denominator_structure") is True,
        "fixed_positive_parameters": all(
            parameter_checks.get(key) is True
            for key in [
                "mu_s_positive",
                "mu_d_positive",
                "mu_s_ge_mu_d",
                "viscous_damping_positive",
                "friction_radius_positive",
            ]
        ),
        "stage_local_lift_checked": all(stage_lift_checks.values()),
    }
    proved = all(checks.values())
    return {
        "schema": "compact-smooth-force-c7-audit-v1",
        "proved": proved,
        "derivative_order": 7,
        "scope": (
            "accepted cylindrical_smooth branch only; assumes the already accepted smooth "
            "FullVA stage lift stays in a compact proof tube; excludes the sharp/small-stribeck "
            "diagnostic branch and does not prove dynamic-row O(h^7) defect"
        ),
        "positive_lower_bounds": positive_lower_bounds,
        "elementary_maps": [
            "addition",
            "multiplication",
            "dot_product",
            "cross_product",
            "tanh",
            "sqrt_on_[1e-24, infinity)",
            "rational_map_with_denominator_ge_0.75^2",
        ],
        "checks": checks,
        "derivative_bound_argument": derivative_bound_clauses,
    }


def main() -> None:
    v047_source = read_text(V047)
    v043_source = read_text(V043)
    summary = read_json(SUMMARY)
    v047_tree = parse_tree(v047_source)
    v043_tree = parse_tree(v043_source)

    cases = find_assignment_value(v047_tree, "CASES") or {}
    friction_velocities = find_assignment_value(v047_tree, "FRICTION_SMOOTHNESS_VELOCITIES") or []
    v043_friction = find_function_source(v043_tree, v043_source, "brown_mcphee_scalar_jax")
    v047_residual = find_function_source(v047_tree, v047_source, "residual_cylindrical_chain")
    v047_make_params = find_function_source(v047_tree, v047_source, "make_params")
    friction_sweep = summary.get("friction_smoothness_sweep", {})
    sweep_cases = friction_sweep.get("cases", {})

    formula_checks = {
        "delegates_v047_to_v043": (
            "def brown_mcphee_scalar_jax" in v047_source
            and "return v043.brown_mcphee_scalar_jax" in v047_source
        ),
        "positive_stribeck_floor": "jnp.maximum(stribeck_velocity, 1.0e-12)" in v043_friction,
        "tanh_dynamic_friction_term": "mu_d * jnp.tanh(4.0 * z)" in v043_friction,
        "rational_static_transition_term": "(mu_s - mu_d) * z / denom" in v043_friction,
        "positive_denominator_structure": "denom = (0.25 * z * z + 0.75) ** 2" in v043_friction,
        "normal_load_multiplies_curve": "-friction_radius * normal_load * curve" in v043_friction,
        "viscous_term_present": "- viscous_damping * v" in v043_friction,
        "no_state_sign_or_abs_branch": ("jnp.sign" not in v043_friction and "jnp.abs" not in v043_friction),
    }
    normal_load_checks = {
        "normal_force_from_lambda_basis": source_has_all(
            v047_residual,
            ["lam[0] * joint_basis[joint, 0]", "lam[1] * joint_basis[joint, 1]"],
        ),
        "positive_sqrt_regularization": "normal_force @ normal_force + jnp.array(1.0e-24" in v047_residual,
        "slide_velocity_stage_local": 'slide_vel = kin["rel_vel"][joint] @ kin["parent_axis"][joint]' in v047_residual,
        "friction_uses_stage_local_normal_load": source_has_all(
            v047_residual,
            ["brown_mcphee_scalar_jax(slide_vel, normal_load", "mu_s", "mu_d", "stribeck_velocity"],
        ),
        "friction_force_uses_parent_axis": 'joint_force.append(normal_force + friction * kin["parent_axis"][joint])'
        in v047_residual,
    }
    parameter_checks = {
        "smooth_case_present": cases.get("cylindrical_smooth") == 0.50,
        "sharp_case_separate": cases.get("cylindrical_sharp") == 0.05,
        "friction_smoothness_velocities_recorded": friction_velocities == [0.50, 0.20, 0.10, 0.05],
        "mu_s_positive": "mu_s=0.30" in v047_make_params,
        "mu_d_positive": "mu_d=0.20" in v047_make_params,
        "mu_s_ge_mu_d": "mu_s=0.30" in v047_make_params and "mu_d=0.20" in v047_make_params,
        "viscous_damping_positive": "viscous_damping=0.030" in v047_make_params,
        "friction_radius_positive": "friction_radius=1.0" in v047_make_params,
        "external_forces_constant_arrays": "external_forces_world=np.array" in v047_make_params,
        "external_torques_constant_arrays": "external_torques_body=np.array" in v047_make_params,
    }
    sweep_checks = {
        "summary_sweep_status_ok": friction_sweep.get("status") == "ok",
        "summary_sweep_velocity_grid_matches_source": friction_sweep.get("stribeck_velocities")
        == friction_velocities,
        "summary_sweep_cases_match_source": sorted(sweep_cases) == [
            "stribeck_0p05",
            "stribeck_0p1",
            "stribeck_0p2",
            "stribeck_0p5",
        ],
        "smooth_case_has_high_order": (
            float(sweep_cases.get("stribeck_0p5", {}).get("position_order", 0.0)) > 6.0
            and float(sweep_cases.get("stribeck_0p5", {}).get("velocity_order", 0.0)) > 6.0
        ),
        "sharp_case_kept_diagnostic": (
            float(sweep_cases.get("stribeck_0p05", {}).get("position_order", 99.0)) < 3.0
        ),
    }
    stage_lift_checks = {
        "uses_stage_kinematics": "stage_kin[si]" in v047_residual,
        "uses_stage_variables": "for si, st in enumerate(stages)" in v047_residual,
        "uses_same_joint_kinematics_for_force_and_constraints": source_has_all(
            v047_residual,
            ['kin["rel_vel"][joint]', 'kin["rel_acc"][joint]', 'kin["axis_res"][joint]'],
        ),
        "force_rows_share_dynamic_stage": source_has_all(
            v047_residual,
            ['trans = masses[body] * st["a"][body]', 'rot = ( Js[body] @ st["alpha"][body]'],
        ),
    }
    checked = all(
        all(group.values())
        for group in [formula_checks, normal_load_checks, parameter_checks, sweep_checks, stage_lift_checks]
    )
    compact_c7 = compact_tube_c7_audit(
        checked,
        formula_checks,
        normal_load_checks,
        parameter_checks,
        stage_lift_checks,
        cases,
    )
    smooth_force_closed = checked and compact_c7["proved"]

    result = {
        "schema": "smooth-force-lift-certificate-v1",
        "status": "smooth_force_lift_c7_tube_bound_closed_dynamic_defect_open",
        "submission_ready": False,
        "certificate_complete": True,
        "proof_gap_closed": False,
        "proof_gap_closed_scope": (
            "false only for this D4 smooth-force certificate; active direct PC2 closure is recorded "
            "separately by the D5 direct-substitution route"
        ),
        "smooth_force_lift_source_structure_checked": checked,
        "smooth_force_lift_consistency_closed": smooth_force_closed,
        "global_C7_tube_derivative_bound_proved": compact_c7["proved"],
        "stage_residual_O_h7_implementation_defect_proved": False,
        "stage_residual_O_h7_implementation_defect_proved_scope": (
            "not proved by this D4 smooth-force certificate alone; this artifact supplies only the "
            "compact-tube C7 force/friction lift input"
        ),
        "active_direct_pc2_route_source": "D5_DYNAMIC_DIRECT_SUBSTITUTION_CERTIFICATE.json",
        "accepted_method": "Gauss6/FullVA",
        "smooth_branch": {
            "case": "cylindrical_smooth",
            "stribeck_velocity": cases.get("cylindrical_smooth"),
            "role": "accepted smooth-order branch",
        },
        "sharp_branch": {
            "case": "cylindrical_sharp",
            "stribeck_velocity": cases.get("cylindrical_sharp"),
            "role": "diagnostic sharp-friction caveat, not the smooth proof branch",
        },
        "formula_checks": formula_checks,
        "normal_load_regularization_checks": normal_load_checks,
        "parameter_checks": parameter_checks,
        "stage_lift_checks": stage_lift_checks,
        "friction_smoothness_sweep_checks": sweep_checks,
        "friction_smoothness_sweep_summary": {
            "status": friction_sweep.get("status"),
            "stribeck_velocities": friction_sweep.get("stribeck_velocities"),
            "h_values": friction_sweep.get("h_values"),
            "reference_h": friction_sweep.get("reference_h"),
            "smooth_position_order": sweep_cases.get("stribeck_0p5", {}).get("position_order"),
            "smooth_velocity_order": sweep_cases.get("stribeck_0p5", {}).get("velocity_order"),
            "sharp_position_order": sweep_cases.get("stribeck_0p05", {}).get("position_order"),
            "sharp_velocity_order": sweep_cases.get("stribeck_0p05", {}).get("velocity_order"),
        },
        "mathematical_reading": {
            "regularized_normal_load": "sqrt(lambda-normal-force dot lambda-normal-force + 1e-24)",
            "brown_mcphee_curve": "mu_d*tanh(4*v/vs) + (mu_s-mu_d)*(v/vs)/(0.25*(v/vs)^2+0.75)^2",
            "smoothness_scope": (
                "For fixed positive parameters and the regularized normal-load map, the source expression "
                "is a composition of smooth arithmetic, tanh, sqrt on a positive argument, and a rational "
                "denominator bounded below by 0.75^2. On the accepted compact smooth proof tube this "
                "gives finite derivatives through order seven for the force/friction lift."
            ),
        },
        "compact_tube_c7_audit": compact_c7,
        "open_proof_boundaries": [
            "connect those bounds to each Newton-Euler dynamic row after full symbolic expansion",
            "combine the closed smooth-force certificate with D1-D3/D5-D6 to prove O(h^7) dynamic defect",
        ],
        "claim_policy": {
            "allowed_now": [
                "smooth Brown-McPhee source formula structure is checked",
                "normal-load regularization and stage-local force lift are checked",
                "accepted smooth-branch force/friction lift is C7 on the compact proof tube",
                "sharp-friction case remains a diagnostic caveat",
            ],
            "forbidden_now": [
                "stage_residual_O_h7_implementation_defect_proved",
                "proof_gap_closed",
                "submission_ready",
            ],
        },
        "execution_policy": {
            "read_only_existing_artifacts": True,
            "default_1e_4_required": False,
            "heavy_numerical_run_invoked": False,
            "run_v047_invoked": False,
            "v048_runner_invoked": False,
        },
        "source_files": {
            "v047_residual_source": "../v047_cylindrical_chain_pipeline/run_v047.py",
            "v043_brown_mcphee_source": "../v043_skew_prismatic_lower_pair/run_v043.py",
            "v047_summary": "../v047_cylindrical_chain_pipeline/results/summary_v047.json",
        },
    }

    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# Smooth Force Lift Certificate",
        "",
        "Status: **D4 CLOSED - smooth force/friction lift is C7 on the accepted compact proof tube; dynamic defect remains open**.",
        "",
        f"- Source structure checked: `{result['smooth_force_lift_source_structure_checked']}`.",
        f"- Smooth-force consistency closed: `{result['smooth_force_lift_consistency_closed']}`.",
        f"- Global C7 tube derivative bound proved: `{result['global_C7_tube_derivative_bound_proved']}`.",
        f"- Stage residual O(h^7) defect proved: `{result['stage_residual_O_h7_implementation_defect_proved']}`.",
        f"- Stage residual false scope: `{result['stage_residual_O_h7_implementation_defect_proved_scope']}`.",
        f"- Direct PC2 route source: `{result['active_direct_pc2_route_source']}`.",
        f"- Submission ready: `{result['submission_ready']}`.",
        "",
        "## Checked Structure",
        "",
        "| group | checked |",
        "|---|---:|",
        f"| Brown-McPhee formula | `{all(formula_checks.values())}` |",
        f"| normal-load regularization | `{all(normal_load_checks.values())}` |",
        f"| fixed smooth-branch parameters | `{all(parameter_checks.values())}` |",
        f"| stage-local FullVA lift | `{all(stage_lift_checks.values())}` |",
        f"| friction smoothness sweep present | `{all(sweep_checks.values())}` |",
        f"| compact smooth proof-tube C7 audit | `{compact_c7['proved']}` |",
        "",
        "## Compact Tube C7 Audit",
        "",
        f"- Derivative order: `{compact_c7['derivative_order']}`.",
        f"- Accepted smooth stribeck velocity: `{compact_c7['positive_lower_bounds']['accepted_smooth_stribeck_velocity']}`.",
        f"- Normal-load square-root lower bound: `{compact_c7['positive_lower_bounds']['sqrt_argument_lower_bound']}`.",
        f"- Brown-McPhee rational denominator lower bound: `{compact_c7['positive_lower_bounds']['rational_denominator_lower_bound']}`.",
        f"- Scope: {compact_c7['scope']}.",
        "",
        "## Sweep Summary",
        "",
        f"- Smooth branch stribeck velocity: `{cases.get('cylindrical_smooth')}`.",
        f"- Sharp branch stribeck velocity: `{cases.get('cylindrical_sharp')}`.",
        f"- Smooth branch position/velocity order: `{result['friction_smoothness_sweep_summary']['smooth_position_order']}` / `{result['friction_smoothness_sweep_summary']['smooth_velocity_order']}`.",
        f"- Sharp branch position/velocity order: `{result['friction_smoothness_sweep_summary']['sharp_position_order']}` / `{result['friction_smoothness_sweep_summary']['sharp_velocity_order']}`.",
        "",
        "## Boundary",
        "",
        "- This certificate closes only the D4 smooth force/friction lift sub-obligation on the accepted smooth branch.",
        "- It relies on the already accepted compact smooth FullVA proof tube and excludes the sharp/small-stribeck diagnostic branch.",
        "- It does not close the Newton-Euler dynamic O(h^7) defect certificate.",
        "",
        "Validator: `validate_smooth_force_lift_certificate.py`.",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("smooth_force_lift_certificate=written")
    print(f"source_structure_checked={checked}")
    print(f"smooth_force_lift_consistency_closed={smooth_force_closed}")
    print(f"global_C7_tube_derivative_bound_proved={compact_c7['proved']}")
    print("proof_gap_closed=False")


if __name__ == "__main__":
    main()
