#!/usr/bin/env python3
"""Build the original TFE pendulum source-policy specification.

This is a read-only extraction from the local source-paper text.  It records the
numerical setup that must be implemented before the Chaturvedi/Sandu/Sandu TFE
suite can be used as a source-policy baseline.
"""

from __future__ import annotations

import json
from pathlib import Path


PAPER = Path(__file__).resolve().parent
REPO = PAPER.parent.parent
ROOT = PAPER.parent
SOURCE_TXT = REPO / "s11044-026-10153-w.txt"
SOURCE_PDF = REPO / "s11044-026-10153-w.pdf"
MODEL_PATH = ROOT / "v048_cross_paper_same_test_benchmarks" / "tfe_source_pendulum_model.py"
OUT_JSON = PAPER / "TFE_SOURCE_POLICY_SPEC.json"
OUT_MD = PAPER / "TFE_SOURCE_POLICY_SPEC.md"


SOURCE_TOKENS = [
    "Table 2 Case study",
    "m                    10",
    "l                    2",
    "R                    0.5",
    "cmx                  3.09",
    "μs                   0.3",
    "μd                   0.2",
    "gravity acts along the −Y axis",
    "Two cases of the pendulum are simulated",
    "frictionless pendulum",
    "pendulum with friction",
    "Brown",
    "McPhee",
    "convergence criteria of ε = 1e − 7",
    "6e − 3 ≤",
    "h ≤ 1.2e − 2",
    "step-size 1e − 4",
    "tf inal = 10 s",
    "TFE (m = 1)",
    "TFE (m = 2)",
    "TFE (m = 3)",
    "Newmark-β (γ = 0.5)",
    "β                             0.3",
    "2m − 1 order",
]


def read_source_text() -> str:
    text = SOURCE_TXT.read_text(encoding="utf-8", errors="replace")
    missing = [token for token in SOURCE_TOKENS if token not in text]
    if missing:
        raise ValueError(f"source text missing expected TFE tokens: {missing}")
    return text


def main() -> None:
    read_source_text()

    candidate_vs_source_policy_boundary = {
        "candidate_scaffold_present": MODEL_PATH.exists(),
        "candidate_scaffold_allowed_use": "diagnostic_scaffold_only_not_source_policy_reproduction",
        "candidate_scaffold_components": [
            "source_pendulum_parameter_model",
            "frictionless_planar_rhs_smoke",
            "absolute_coordinate_dae_residual_smoke",
            "bounded_candidate_runner_api",
            "full_T10_coarse_candidate_probe",
            "Gauss6_FullVA_source_pendulum_candidate_smoke",
        ],
        "source_policy_runner_required_for_promotion": True,
        "gauss6_fullva_candidate_smoke_available": MODEL_PATH.exists(),
        "gauss6_fullva_candidate_smoke_allowed_use": (
            "candidate_smoke_only_not_source_policy_dae_runner"
        ),
        "gauss6_fullva_candidate_smoke_source_policy_rows_completed": 0,
        "gauss6_fullva_absolute_coordinate_source_policy_dae_runner_required": True,
        "gauss6_fullva_absolute_coordinate_source_policy_dae_runner_implemented": False,
        "gauss6_fullva_absolute_coordinate_source_policy_dae_runner_equivalent": False,
        "gauss6_fullva_absolute_coordinate_source_policy_dae_runner_rows_completed": 0,
        "source_policy_runner_obligations": [
            "monolithic_absolute_coordinate_DAE_time_integrator",
            "source_code_equivalent_Brown_McPhee_friction_law",
            "TFE_m1_m2_m3_Newmark_beta_trapezoidal_source_policy_method_runners",
            "Gauss6_FullVA_absolute_coordinate_source_policy_DAE_runner",
            "accepted_T10_source_policy_work_precision_rows",
        ],
        "source_policy_dae_runner_equivalent": False,
        "source_policy_method_runner_equivalent": False,
        "source_policy_rows_completed": 0,
        "external_superiority_allowed": False,
    }

    result = {
        "schema": "tfe-source-policy-spec-v1",
        "status": "source_policy_extracted_candidate_scaffold_present_source_policy_open",
        "submission_ready": False,
        "external_superiority_claim": False,
        "source_files": {
            "pdf": "../../s11044-026-10153-w.pdf",
            "text": "../../s11044-026-10153-w.txt",
        },
        "source_policy": {
            "paper": "Chaturvedi--Sandu--Sandu TFE pendulum suite",
            "model": "rigid_pendulum_revolute_pair",
            "gravity_axis": "-Y",
            "hinge_pin": "massless_fixed_at_both_ends",
            "body_parameters": {
                "mass_kg": 10.0,
                "inertia_kg_m2": [
                    [0.05, 0.0, 0.0],
                    [0.0, 0.03, 0.015],
                    [0.0, 0.015, 0.028],
                ],
                "length_m": 2.0,
                "hinge_pin_radius_m": 0.5,
                "center_of_mass_x_m": 3.09,
            },
            "friction_parameters": {
                "mu_static": 0.3,
                "mu_dynamic": 0.2,
                "model_family": "Brown--McPhee velocity-based continuous friction model",
                "law_details_available_in_source_paper": False,
                "requires_reference_38_39_or_existing_source_code": True,
            },
            "cases": [
                {
                    "case_id": "frictionless_pendulum",
                    "friction_enabled": False,
                    "comparison_step_sizes": [0.003, 0.006],
                    "error_sweep_h_min": 0.006,
                    "error_sweep_h_max": 0.012,
                    "reference_h": 1.0e-4,
                    "t_final": 10.0,
                },
                {
                    "case_id": "frictional_pendulum",
                    "friction_enabled": True,
                    "comparison_step_sizes": [0.003, 0.008],
                    "large_step_stability_h": 0.2,
                    "reference_h": 1.0e-4,
                    "t_final": 10.0,
                },
            ],
            "methods": [
                {"method": "TFE_m1", "expected_order": 1, "damping_parameter_nu": 0.99},
                {"method": "TFE_m2", "expected_order": 3, "damping_parameter_nu": 0.95},
                {"method": "TFE_m3", "expected_order": 5, "damping_parameter_nu": 0.9},
                {"method": "trapezoidal", "expected_order": 2, "damping_parameter": None},
                {"method": "Newmark_beta", "expected_order": 2, "gamma": 0.5, "beta": 0.3},
            ],
            "tfe_nodes": {
                "m1": ["0", "1"],
                "m2": ["0", "1/2", "1"],
                "m3_gauss_lobatto": ["0", "1/2-sqrt(5)/10", "1/2+sqrt(5)/10", "1"],
                "m3_equally_spaced": ["0", "1/3", "2/3", "1"],
            },
            "solver_policy": {
                "newton_tolerance": 1.0e-7,
                "jacobian_policy": "central finite difference with sqrt(machine precision) perturbation",
                "source_reference_h_for_exact_reproduction": 1.0e-4,
                "default_1e_4_campaign_invoked": False,
            },
            "metrics": [
                "coordinate_error_order_q",
                "velocity_error_order_v",
                "Frobenius_error_norm_eta",
                "mechanical_energy_deviation",
                "newton_iterations_per_step",
                "total_simulation_time",
                "large_step_stability",
            ],
            "reported_source_observations": {
                "formula_expected_order": "2m-1",
                "frictionless_TFE_m3_observed_order": "about_fourth_order_in_DAE_experiment",
                "frictional_order_loss": "larger_than_frictionless_case",
                "trapezoidal_stability": "unstable_across_reported_step_sizes",
                "newmark_beta": "stable_with_beta_0p3_but_large_step_failure_reported_for_friction_case",
            },
        },
        "runner_gap": {
            "source_policy_spec_extracted": True,
            "source_pendulum_parameter_model_implemented": MODEL_PATH.exists(),
            "frictionless_planar_rhs_smoke_implemented": MODEL_PATH.exists(),
            "absolute_coordinate_dae_residual_smoke_implemented": MODEL_PATH.exists(),
            "source_error_norm_and_output_policy_encoded": MODEL_PATH.exists(),
            "candidate_friction_law_encoded": MODEL_PATH.exists(),
            "newmark_trapezoidal_candidate_runner_smoke_implemented": MODEL_PATH.exists(),
            "tfe_m1_m2_m3_candidate_runner_smoke_implemented": MODEL_PATH.exists(),
            "bounded_candidate_runner_api_implemented": MODEL_PATH.exists(),
            "full_T10_coarse_candidate_probe_implemented": MODEL_PATH.exists(),
            "pendulum_dae_runner_implemented": False,
            "brown_mcphee_friction_law_implemented": False,
            "tfe_m1_m2_m3_runner_implemented": False,
            "newmark_trapezoidal_runner_implemented": False,
            "gauss6_fullva_on_source_pendulum_implemented": False,
            "gauss6_fullva_source_pendulum_candidate_smoke_implemented": MODEL_PATH.exists(),
            "gauss6_fullva_source_pendulum_candidate_smoke_source_policy_rows_completed": 0,
            "gauss6_fullva_absolute_coordinate_source_policy_dae_runner_implemented": False,
            "gauss6_fullva_absolute_coordinate_source_policy_dae_runner_equivalent": False,
            "source_policy_rows_completed": 0,
            "external_superiority_allowed": False,
        },
        "candidate_vs_source_policy_boundary": candidate_vs_source_policy_boundary,
        "required_next_artifacts": [
            "promote_source_pendulum_parameter_model_to_absolute_coordinate_dae_runner",
            "replace_candidate_brown_mcphee_surrogate_with_source_code_equivalent_friction_law",
            "promote_TFE_m1_m2_m3_Newmark_beta_trapezoidal_candidate_runners_to_source_policy_equivalence",
            "run_frictionless_and_frictional_h_sweeps_with_source_reference_policy",
            "add_order_time_work_precision_rows_and_figures",
            "compare_Gauss6_FullVA_on_identical_source_pendulum_policy_or_demote_suite",
        ],
        "claim_policy": {
            "allowed_now": [
                "source-policy specification extracted from the TFE paper",
                "TFE m=3 formal expected order is five",
                "source paper reports DAE order loss for m=3",
                "candidate planar source-output runners and a full T=10 coarse probe exist outside source-policy closure",
            ],
            "forbidden_now": [
                "original TFE pendulum rows completed",
                "TFE source-policy reproduction passed",
                "Gauss6/FullVA beats original TFE source-policy runs",
                "source Brown--McPhee friction law fully encoded",
                "submission ready",
            ],
        },
        "execution_policy": {
            "read_only_extraction": True,
            "heavy_numerical_run_invoked": False,
            "run_v047_invoked": False,
            "v048_runner_invoked": False,
        },
    }

    with OUT_JSON.open("w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, sort_keys=True)
        handle.write("\n")

    lines = [
        "# TFE Source-Policy Specification",
        "",
        "Status: **source policy extracted - candidate scaffold present; source-policy rows open**.",
        "",
        f"- Source PDF: `{result['source_files']['pdf']}`.",
        f"- Model: `{result['source_policy']['model']}`.",
        f"- Mass/length/hinge radius/cmx: `{result['source_policy']['body_parameters']['mass_kg']}` / `{result['source_policy']['body_parameters']['length_m']}` / `{result['source_policy']['body_parameters']['hinge_pin_radius_m']}` / `{result['source_policy']['body_parameters']['center_of_mass_x_m']}`.",
        f"- Friction coefficients mu_s/mu_d: `{result['source_policy']['friction_parameters']['mu_static']}` / `{result['source_policy']['friction_parameters']['mu_dynamic']}`.",
        f"- Reference h for exact source reproduction: `{result['source_policy']['solver_policy']['source_reference_h_for_exact_reproduction']}`.",
        f"- Newton tolerance: `{result['source_policy']['solver_policy']['newton_tolerance']}`.",
        f"- Source-policy rows completed: `{result['runner_gap']['source_policy_rows_completed']}`.",
        f"- Source pendulum parameter model implemented: `{result['runner_gap']['source_pendulum_parameter_model_implemented']}`.",
        f"- Frictionless planar RHS smoke implemented: `{result['runner_gap']['frictionless_planar_rhs_smoke_implemented']}`.",
        f"- Candidate comparator/TFE bounded/full-T10 scaffold: `{result['runner_gap']['newmark_trapezoidal_candidate_runner_smoke_implemented']}/{result['runner_gap']['tfe_m1_m2_m3_candidate_runner_smoke_implemented']}/{result['runner_gap']['bounded_candidate_runner_api_implemented']}/{result['runner_gap']['full_T10_coarse_candidate_probe_implemented']}`.",
        (
            "- Gauss6 candidate smoke/source-policy DAE runner/source rows/equivalent: "
            f"`{result['runner_gap']['gauss6_fullva_source_pendulum_candidate_smoke_implemented']}/"
            f"{result['runner_gap']['gauss6_fullva_absolute_coordinate_source_policy_dae_runner_implemented']}/"
            f"{result['runner_gap']['gauss6_fullva_source_pendulum_candidate_smoke_source_policy_rows_completed']}/"
            f"{result['runner_gap']['gauss6_fullva_absolute_coordinate_source_policy_dae_runner_equivalent']}`."
        ),
        (
            "- Candidate/source-policy boundary scaffold/use/DAE-equivalent/method-equivalent/rows: "
            f"`{candidate_vs_source_policy_boundary['candidate_scaffold_present']}/"
            f"{candidate_vs_source_policy_boundary['candidate_scaffold_allowed_use']}/"
            f"{candidate_vs_source_policy_boundary['source_policy_dae_runner_equivalent']}/"
            f"{candidate_vs_source_policy_boundary['source_policy_method_runner_equivalent']}/"
            f"{candidate_vs_source_policy_boundary['source_policy_rows_completed']}`."
        ),
        f"- Pendulum DAE runner implemented: `{result['runner_gap']['pendulum_dae_runner_implemented']}`.",
        f"- External superiority allowed: `{result['runner_gap']['external_superiority_allowed']}`.",
        f"- Heavy numerical run invoked: `{result['execution_policy']['heavy_numerical_run_invoked']}`.",
        "",
        "## Methods",
        "",
        "| method | expected order | parameter |",
        "|---|---:|---|",
    ]
    for method in result["source_policy"]["methods"]:
        parameter = []
        if method.get("damping_parameter_nu") is not None:
            parameter.append(f"nu={method['damping_parameter_nu']}")
        if method.get("gamma") is not None:
            parameter.append(f"gamma={method['gamma']}")
        if method.get("beta") is not None:
            parameter.append(f"beta={method['beta']}")
        lines.append(f"| `{method['method']}` | `{method['expected_order']}` | `{', '.join(parameter) or 'none'}` |")

    lines.extend(
        [
            "",
            "## Cases",
            "",
            "| case | friction | h policy | reference h | t final |",
            "|---|---:|---|---:|---:|",
        ]
    )
    for case in result["source_policy"]["cases"]:
        h_policy = (
            f"comparison {case.get('comparison_step_sizes')}"
            + (f", large-step {case.get('large_step_stability_h')}" if case.get("large_step_stability_h") else "")
            + (f", sweep [{case.get('error_sweep_h_min')}, {case.get('error_sweep_h_max')}]" if case.get("error_sweep_h_min") else "")
        )
        lines.append(
            f"| `{case['case_id']}` | `{case['friction_enabled']}` | {h_policy} | `{case['reference_h']}` | `{case['t_final']}` |"
        )

    lines.extend(
        [
            "",
            "## Runner Gap",
            "",
            "| obligation | satisfied |",
            "|---|---:|",
        ]
    )
    for key, value in result["runner_gap"].items():
        lines.append(f"| `{key}` | `{value}` |")

    lines.extend(
        [
            "",
            "## Candidate/Source-Policy Boundary",
            "",
            "| item | value |",
            "|---|---|",
            f"| `candidate_scaffold_present` | `{candidate_vs_source_policy_boundary['candidate_scaffold_present']}` |",
            f"| `candidate_scaffold_allowed_use` | `{candidate_vs_source_policy_boundary['candidate_scaffold_allowed_use']}` |",
            f"| `source_policy_runner_required_for_promotion` | `{candidate_vs_source_policy_boundary['source_policy_runner_required_for_promotion']}` |",
            f"| `gauss6_fullva_candidate_smoke_available` | `{candidate_vs_source_policy_boundary['gauss6_fullva_candidate_smoke_available']}` |",
            f"| `gauss6_fullva_candidate_smoke_allowed_use` | `{candidate_vs_source_policy_boundary['gauss6_fullva_candidate_smoke_allowed_use']}` |",
            f"| `gauss6_fullva_candidate_smoke_source_policy_rows_completed` | `{candidate_vs_source_policy_boundary['gauss6_fullva_candidate_smoke_source_policy_rows_completed']}` |",
            f"| `gauss6_fullva_absolute_coordinate_source_policy_dae_runner_required` | `{candidate_vs_source_policy_boundary['gauss6_fullva_absolute_coordinate_source_policy_dae_runner_required']}` |",
            f"| `gauss6_fullva_absolute_coordinate_source_policy_dae_runner_implemented` | `{candidate_vs_source_policy_boundary['gauss6_fullva_absolute_coordinate_source_policy_dae_runner_implemented']}` |",
            f"| `gauss6_fullva_absolute_coordinate_source_policy_dae_runner_equivalent` | `{candidate_vs_source_policy_boundary['gauss6_fullva_absolute_coordinate_source_policy_dae_runner_equivalent']}` |",
            f"| `gauss6_fullva_absolute_coordinate_source_policy_dae_runner_rows_completed` | `{candidate_vs_source_policy_boundary['gauss6_fullva_absolute_coordinate_source_policy_dae_runner_rows_completed']}` |",
            f"| `source_policy_dae_runner_equivalent` | `{candidate_vs_source_policy_boundary['source_policy_dae_runner_equivalent']}` |",
            f"| `source_policy_method_runner_equivalent` | `{candidate_vs_source_policy_boundary['source_policy_method_runner_equivalent']}` |",
            f"| `source_policy_rows_completed` | `{candidate_vs_source_policy_boundary['source_policy_rows_completed']}` |",
            f"| `external_superiority_allowed` | `{candidate_vs_source_policy_boundary['external_superiority_allowed']}` |",
            "",
            "Candidate scaffolds support implementation and diagnostic review only; promotion requires the listed source-policy runner obligations.",
        ]
    )

    lines.extend(
        [
            "",
            "## Claim Policy",
            "",
            "- Allowed now: source-policy specification extraction and formal order-target discussion.",
            "- Forbidden now: completed original TFE reproduction, source-policy superiority, full friction-law encoding, and submission readiness.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
