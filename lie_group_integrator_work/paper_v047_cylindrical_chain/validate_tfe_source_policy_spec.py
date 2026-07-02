#!/usr/bin/env python3
"""Validate the original TFE source-policy specification."""

from __future__ import annotations

import json
import sys
from pathlib import Path


PAPER = Path(__file__).resolve().parent
REPO = PAPER.parent.parent
SPEC_JSON = PAPER / "TFE_SOURCE_POLICY_SPEC.json"
SPEC_MD = PAPER / "TFE_SOURCE_POLICY_SPEC.md"
SOURCE_PDF = REPO / "s11044-026-10153-w.pdf"
SOURCE_TXT = REPO / "s11044-026-10153-w.txt"


class Checks:
    def __init__(self) -> None:
        self.errors: list[str] = []

    def check(self, condition: bool, message: str) -> None:
        if not condition:
            self.errors.append(message)


def read_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def main() -> int:
    checks = Checks()
    try:
        spec = read_json(SPEC_JSON)
        spec_md = read_text(SPEC_MD)
        source_text = read_text(SOURCE_TXT)
    except Exception as exc:  # noqa: BLE001
        print(f"TFE source-policy spec validation: FAIL\n- {exc}")
        return 1

    policy = spec.get("source_policy", {})
    body = policy.get("body_parameters", {})
    friction = policy.get("friction_parameters", {})
    solver = policy.get("solver_policy", {})
    runner_gap = spec.get("runner_gap", {})
    boundary = spec.get("candidate_vs_source_policy_boundary", {})
    execution = spec.get("execution_policy", {})
    methods = {row.get("method"): row for row in policy.get("methods", [])}
    cases = {row.get("case_id"): row for row in policy.get("cases", [])}

    checks.check(SOURCE_PDF.exists() and SOURCE_PDF.stat().st_size > 100_000, "source PDF missing")
    checks.check(SOURCE_TXT.exists() and SOURCE_TXT.stat().st_size > 10_000, "source text missing")
    for token in [
        "Table 2 Case study",
        "m                    10",
        "R                    0.5",
        "cmx                  3.09",
        "μs                   0.3",
        "μd                   0.2",
        "Brown",
        "McPhee",
        "convergence criteria of ε = 1e − 7",
        "step-size 1e − 4",
        "Figure 6 compares the evolution of error",
        "Fig. 17 com",
    ]:
        checks.check(token in source_text, f"source text missing anchor: {token}")

    checks.check(spec.get("schema") == "tfe-source-policy-spec-v1", "schema changed")
    checks.check(
        spec.get("status") == "source_policy_extracted_candidate_scaffold_present_source_policy_open",
        "status changed",
    )
    checks.check(spec.get("submission_ready") is False, "spec must not mark submission ready")
    checks.check(spec.get("external_superiority_claim") is False, "spec must not claim external superiority")
    checks.check(policy.get("model") == "rigid_pendulum_revolute_pair", "model changed")
    checks.check(policy.get("gravity_axis") == "-Y", "gravity axis changed")
    checks.check(policy.get("hinge_pin") == "massless_fixed_at_both_ends", "hinge pin changed")
    checks.check(body.get("mass_kg") == 10.0, "mass changed")
    checks.check(body.get("length_m") == 2.0, "length changed")
    checks.check(body.get("hinge_pin_radius_m") == 0.5, "hinge radius changed")
    checks.check(body.get("center_of_mass_x_m") == 3.09, "center of mass changed")
    checks.check(body.get("inertia_kg_m2") == [[0.05, 0.0, 0.0], [0.0, 0.03, 0.015], [0.0, 0.015, 0.028]], "inertia changed")
    checks.check(friction.get("mu_static") == 0.3, "mu_static changed")
    checks.check(friction.get("mu_dynamic") == 0.2, "mu_dynamic changed")
    checks.check(friction.get("requires_reference_38_39_or_existing_source_code") is True, "friction-law gap changed")
    checks.check(solver.get("newton_tolerance") == 1.0e-7, "Newton tolerance changed")
    checks.check(solver.get("source_reference_h_for_exact_reproduction") == 1.0e-4, "source reference h changed")
    checks.check(solver.get("default_1e_4_campaign_invoked") is False, "spec invoked default 1e-4 campaign")
    checks.check(set(methods) == {"TFE_m1", "TFE_m2", "TFE_m3", "trapezoidal", "Newmark_beta"}, "method set changed")
    checks.check(methods.get("TFE_m1", {}).get("expected_order") == 1, "TFE m1 order changed")
    checks.check(methods.get("TFE_m2", {}).get("expected_order") == 3, "TFE m2 order changed")
    checks.check(methods.get("TFE_m3", {}).get("expected_order") == 5, "TFE m3 order changed")
    checks.check(methods.get("TFE_m3", {}).get("damping_parameter_nu") == 0.9, "TFE m3 damping changed")
    checks.check(methods.get("Newmark_beta", {}).get("gamma") == 0.5, "Newmark gamma changed")
    checks.check(methods.get("Newmark_beta", {}).get("beta") == 0.3, "Newmark beta changed")
    checks.check(set(cases) == {"frictionless_pendulum", "frictional_pendulum"}, "case set changed")
    checks.check(cases.get("frictionless_pendulum", {}).get("comparison_step_sizes") == [0.003, 0.006], "frictionless comparison steps changed")
    checks.check(cases.get("frictionless_pendulum", {}).get("error_sweep_h_min") == 0.006, "frictionless h min changed")
    checks.check(cases.get("frictionless_pendulum", {}).get("error_sweep_h_max") == 0.012, "frictionless h max changed")
    checks.check(cases.get("frictional_pendulum", {}).get("comparison_step_sizes") == [0.003, 0.008], "frictional comparison steps changed")
    checks.check(cases.get("frictional_pendulum", {}).get("large_step_stability_h") == 0.2, "large-step h changed")
    checks.check(runner_gap.get("source_policy_spec_extracted") is True, "source-policy extraction marker missing")
    checks.check(runner_gap.get("source_pendulum_parameter_model_implemented") is True, "source pendulum parameter model missing")
    checks.check(runner_gap.get("frictionless_planar_rhs_smoke_implemented") is True, "frictionless planar RHS smoke missing")
    checks.check(
        runner_gap.get("absolute_coordinate_dae_residual_smoke_implemented") is True,
        "absolute-coordinate DAE residual smoke marker missing",
    )
    checks.check(
        runner_gap.get("source_error_norm_and_output_policy_encoded") is True,
        "source output policy marker missing",
    )
    checks.check(runner_gap.get("candidate_friction_law_encoded") is True, "candidate friction marker missing")
    checks.check(
        runner_gap.get("newmark_trapezoidal_candidate_runner_smoke_implemented") is True,
        "Newmark/trapezoidal candidate marker missing",
    )
    checks.check(
        runner_gap.get("tfe_m1_m2_m3_candidate_runner_smoke_implemented") is True,
        "TFE candidate runner marker missing",
    )
    checks.check(
        runner_gap.get("bounded_candidate_runner_api_implemented") is True,
        "bounded candidate runner marker missing",
    )
    checks.check(
        runner_gap.get("full_T10_coarse_candidate_probe_implemented") is True,
        "full T=10 coarse probe marker missing",
    )
    checks.check(runner_gap.get("pendulum_dae_runner_implemented") is False, "pendulum runner should remain open")
    checks.check(runner_gap.get("brown_mcphee_friction_law_implemented") is False, "friction law should remain open")
    checks.check(
        runner_gap.get("gauss6_fullva_source_pendulum_candidate_smoke_implemented") is True,
        "Gauss6 candidate smoke marker missing",
    )
    checks.check(
        runner_gap.get("gauss6_fullva_source_pendulum_candidate_smoke_source_policy_rows_completed") == 0,
        "Gauss6 candidate smoke overclosed source-policy rows",
    )
    checks.check(
        runner_gap.get("gauss6_fullva_absolute_coordinate_source_policy_dae_runner_implemented") is False
        and runner_gap.get("gauss6_fullva_absolute_coordinate_source_policy_dae_runner_equivalent")
        is False,
        "Gauss6 source-policy DAE runner overclaims implementation/equivalence",
    )
    checks.check(runner_gap.get("source_policy_rows_completed") == 0, "source-policy rows should remain zero")
    checks.check(runner_gap.get("external_superiority_allowed") is False, "external superiority should remain blocked")
    checks.check(boundary.get("candidate_scaffold_present") is True, "candidate/source boundary missing scaffold marker")
    checks.check(
        boundary.get("candidate_scaffold_allowed_use")
        == "diagnostic_scaffold_only_not_source_policy_reproduction",
        "candidate/source boundary allowed-use changed",
    )
    checks.check(
        boundary.get("candidate_scaffold_components")
        == [
            "source_pendulum_parameter_model",
            "frictionless_planar_rhs_smoke",
            "absolute_coordinate_dae_residual_smoke",
            "bounded_candidate_runner_api",
            "full_T10_coarse_candidate_probe",
            "Gauss6_FullVA_source_pendulum_candidate_smoke",
        ],
        "candidate/source boundary component list changed",
    )
    checks.check(
        boundary.get("source_policy_runner_required_for_promotion") is True,
        "candidate/source boundary must require source-policy runner promotion",
    )
    checks.check(
        boundary.get("gauss6_fullva_candidate_smoke_available") is True,
        "Gauss6 candidate/source boundary missing candidate smoke marker",
    )
    checks.check(
        boundary.get("gauss6_fullva_candidate_smoke_allowed_use")
        == "candidate_smoke_only_not_source_policy_dae_runner",
        "Gauss6 candidate smoke allowed-use boundary changed",
    )
    checks.check(
        boundary.get("gauss6_fullva_candidate_smoke_source_policy_rows_completed") == 0,
        "Gauss6 candidate boundary overclosed source-policy rows",
    )
    checks.check(
        boundary.get("gauss6_fullva_absolute_coordinate_source_policy_dae_runner_required")
        is True
        and boundary.get("gauss6_fullva_absolute_coordinate_source_policy_dae_runner_implemented")
        is False
        and boundary.get("gauss6_fullva_absolute_coordinate_source_policy_dae_runner_equivalent")
        is False
        and boundary.get("gauss6_fullva_absolute_coordinate_source_policy_dae_runner_rows_completed")
        == 0,
        "Gauss6 source-policy DAE runner boundary overclaims readiness",
    )
    checks.check(
        boundary.get("source_policy_runner_obligations")
        == [
            "monolithic_absolute_coordinate_DAE_time_integrator",
            "source_code_equivalent_Brown_McPhee_friction_law",
            "TFE_m1_m2_m3_Newmark_beta_trapezoidal_source_policy_method_runners",
            "Gauss6_FullVA_absolute_coordinate_source_policy_DAE_runner",
            "accepted_T10_source_policy_work_precision_rows",
        ],
        "candidate/source boundary obligation list changed",
    )
    checks.check(
        boundary.get("source_policy_dae_runner_equivalent") is False
        and boundary.get("source_policy_method_runner_equivalent") is False
        and boundary.get("source_policy_rows_completed") == 0
        and boundary.get("external_superiority_allowed") is False,
        "candidate/source boundary overclaims source-policy readiness",
    )
    checks.check(execution.get("read_only_extraction") is True, "read-only marker missing")
    checks.check(execution.get("heavy_numerical_run_invoked") is False, "heavy run invoked")
    checks.check(execution.get("run_v047_invoked") is False, "run_v047 invoked")
    checks.check(execution.get("v048_runner_invoked") is False, "v048 runner invoked")

    for token in [
        "source policy extracted - candidate scaffold present; source-policy rows open",
        "Mass/length/hinge radius/cmx: `10.0` / `2.0` / `0.5` / `3.09`.",
        "Friction coefficients mu_s/mu_d: `0.3` / `0.2`.",
        "Reference h for exact source reproduction: `0.0001`.",
        "Source-policy rows completed: `0`.",
        "Source pendulum parameter model implemented: `True`.",
        "Frictionless planar RHS smoke implemented: `True`.",
        "Candidate comparator/TFE bounded/full-T10 scaffold: `True/True/True/True`.",
        "Gauss6 candidate smoke/source-policy DAE runner/source rows/equivalent: `True/False/0/False`.",
        "Candidate/source-policy boundary scaffold/use/DAE-equivalent/method-equivalent/rows: `True/diagnostic_scaffold_only_not_source_policy_reproduction/False/False/0`.",
        "## Candidate/Source-Policy Boundary",
        "`source_policy_runner_required_for_promotion` | `True`",
        "`gauss6_fullva_candidate_smoke_allowed_use` | `candidate_smoke_only_not_source_policy_dae_runner`",
        "`gauss6_fullva_absolute_coordinate_source_policy_dae_runner_implemented` | `False`",
        "`gauss6_fullva_absolute_coordinate_source_policy_dae_runner_equivalent` | `False`",
        "Candidate scaffolds support implementation and diagnostic review only; promotion requires the listed source-policy runner obligations.",
        "Pendulum DAE runner implemented: `False`.",
        "External superiority allowed: `False`.",
        "`TFE_m3` | `5` | `nu=0.9`",
        "`Newmark_beta` | `2` | `gamma=0.5, beta=0.3`",
        "`pendulum_dae_runner_implemented` | `False`",
        "Forbidden now: completed original TFE reproduction",
    ]:
        checks.check(token in spec_md, f"markdown missing token: {token}")

    if checks.errors:
        print("TFE source-policy spec validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("TFE source-policy spec validation: PASS")
    print("status=source_policy_extracted_candidate_scaffold_present_source_policy_open")
    print("source_reference_h=1e-4")
    print("source_policy_rows_completed=0")
    print("external_superiority_claim=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
