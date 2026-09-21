#!/usr/bin/env python3
"""Validate the RA2021 source-code identity audit."""

from __future__ import annotations

import json
import sys
from pathlib import Path


PAPER = Path(__file__).resolve().parent
AUDIT_JSON = PAPER / "RA2021_SOURCE_IDENTITY_AUDIT.json"
AUDIT_MD = PAPER / "RA2021_SOURCE_IDENTITY_AUDIT.md"


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
        audit = read_json(AUDIT_JSON)
        audit_md = read_text(AUDIT_MD)
    except Exception as exc:  # noqa: BLE001
        print(f"RA2021 source identity audit validation: FAIL\n- {exc}")
        return 1

    checks.check(audit.get("schema") == "ra2021-source-identity-audit-v1", "schema changed")
    checks.check(
        audit.get("status") == "source_output_time_grid_policy_extracted_promotion_still_open",
        "status changed",
    )
    checks.check(audit.get("suite_id") == "ra2021_absolute_coordinate", "suite id changed")
    checks.check(audit.get("source_suite") == "ra2021_taves_kissel_negrut", "source suite changed")
    checks.check(audit.get("read_only") is True, "audit must be read-only")

    source_files = audit.get("source_files", {})
    for key in [
        "standard_setup",
        "four_link_model",
        "slider_crank_model",
        "double_pendulum_model",
        "system_ra",
        "system_rp",
        "system_reps",
    ]:
        checks.check(key in source_files, f"missing source file key {key}")

    setup = audit.get("setup_identity", {})
    checks.check(setup.get("form_choices_present") is True, "form choices not verified")
    checks.check(setup.get("mode_choices_present") is True, "mode choices not verified")
    checks.check(setup.get("tol_optional") is True, "optional tolerance not verified")
    checks.check(setup.get("form_dispatch") == {"rA": True, "reps": True, "rp": True}, "form dispatch changed")
    checks.check(setup.get("mode_dispatch") == {"dynamics": True, "kinematics": True}, "mode dispatch changed")

    outputs = audit.get("output_assignments", {})
    checks.check(set(outputs) == {"four_link", "slider_crank", "double_pendulum"}, "output models changed")
    for model, assignments in outputs.items():
        checks.check(set(assignments) == {"position", "velocity", "acceleration"}, f"{model} output mapping incomplete")
        for kind, anchor in assignments.items():
            checks.check(isinstance(anchor.get("line"), int) and anchor["line"] > 0, f"{model} {kind} anchor missing")
            checks.check("body." in anchor.get("needle", ""), f"{model} {kind} source needle changed")

    forms = audit.get("form_velocity_assignments", {})
    checks.check(set(forms) == {"rA", "rp", "reps"}, "form velocity assignments changed")
    checks.check("body.dr = dq[3*j:3*(j+1), :]" in forms.get("rA", {}).get("translational_velocity", {}).get("needle", ""), "rA body.dr mapping changed")
    checks.check("body.dr = dq[3*j:3*(j+1), :]" in forms.get("rp", {}).get("translational_velocity", {}).get("needle", ""), "rp body.dr mapping changed")
    checks.check("body.dr = dq[3*j:3*(j+1), :]" in forms.get("reps", {}).get("translational_velocity", {}).get("needle", ""), "reps body.dr mapping changed")
    checks.check("body.dr = body.dr_prev + self.h*body.ddr" in forms.get("rA", {}).get("dynamics_update", {}).get("needle", ""), "rA dynamics velocity update changed")

    time_grid = audit.get("time_grid_policy", {})
    checks.check(time_grid.get("public_point_count_formula") == "int(t_end / h)", "point-count policy changed")
    checks.check(
        time_grid.get("public_grid_formula") == "numpy.linspace(0, t_end, int(t_end / h), endpoint=True)",
        "time-grid policy changed",
    )
    checks.check(abs(time_grid.get("example_interval_T3_h1e_3", 0.0) - 0.0010003334444814938) < 1.0e-15, "T=3,h=1e-3 interval changed")

    artifact = audit.get("artifact_alignment", {})
    checks.check(artifact.get("public_order_summary_rows") == 9, "public order summary row count changed")
    checks.check(artifact.get("public_order_summary_completed_rows") == 9, "public order summary completion changed")
    checks.check(artifact.get("public_double_order_groups") == 3, "public double order group count changed")
    checks.check(artifact.get("public_order_groups_total") == 12, "public order group total changed")
    checks.check(artifact.get("raw_order_rows") == 36, "raw order row count changed")
    checks.check(artifact.get("raw_order_ok_rows") == 36, "raw order ok count changed")
    checks.check(artifact.get("timing_rows") == 12, "timing row count changed")
    checks.check(artifact.get("timing_ok_rows") == 12, "timing ok count changed")
    checks.check(artifact.get("forms") == ["rA", "reps", "rp"], "forms changed")
    checks.check(artifact.get("models") == ["double_pendulum", "four_link", "single_pendulum", "slider_crank"], "models changed")
    checks.check(artifact.get("t_end_values") == [3.0], "T values changed")
    checks.check(artifact.get("summary_finest_h_values") == [0.0001], "finest h values changed")

    issues = audit.get("forensic_issue_counts", {})
    checks.check(issues.get("ra2021_forensic_rows") == 12, "RA2021 forensic row count changed")
    checks.check(issues.get("position_aligned_velocity_mismatch_rows") == 9, "velocity mismatch count changed")
    checks.check(issues.get("velocity_nonmonotone_or_floor_limited_rows") == 1, "velocity floor count changed")

    boundary = audit.get("claim_boundary", {})
    checks.check(boundary.get("output_mapping_verified_from_source") is True, "output mapping not verified")
    checks.check(boundary.get("time_grid_policy_extracted_from_source") is True, "time grid not extracted")
    checks.check(boundary.get("source_policy_reproduction_rows_closed") == 0, "audit overcloses source-policy rows")
    checks.check(boundary.get("can_close_ra2021_b2_requirement_now") is False, "audit overcloses B2")
    checks.check(boundary.get("external_superiority_claim_allowed") is False, "audit overclaims external superiority")
    checks.check(boundary.get("default_1e_4_required") is False, "audit requires default 1e-4")
    checks.check(boundary.get("heavy_numerical_run_invoked") is False, "audit invoked heavy run")
    checks.check(boundary.get("run_v047_invoked") is False, "audit invoked run_v047")
    checks.check(boundary.get("v048_runner_invoked") is False, "audit invoked v048 runner")

    for token in [
        "Output mapping verified from source: `True`.",
        "Time-grid policy extracted from source: `True`.",
        "RA2021 forensic rows with position-aligned velocity mismatch: `9`.",
        "Source-policy rows closed by this audit: `0`.",
        "Can close RA2021 B2 requirement now: `False`.",
        "External-superiority claim allowed: `False`.",
    ]:
        checks.check(token in audit_md, f"missing MD token: {token}")

    if checks.errors:
        print("RA2021 source identity audit validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("RA2021 source identity audit validation: PASS")
    print("output_mapping_verified=True")
    print("time_grid_policy_extracted=True")
    print("source_policy_rows_closed=0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
