#!/usr/bin/env python3
"""Build a source-code identity audit for the RA2021 public baseline rows."""

from __future__ import annotations

import csv
import json
from pathlib import Path


PAPER = Path(__file__).resolve().parent
WORK = PAPER.parent
PROJECT = WORK.parent
SOURCE = PROJECT / "external" / "sbel-reproducibility" / "2021" / "ASME" / "rA-formulation" / "C2" / "SimEngineMBD"
V048_RESULTS = WORK / "v048_cross_paper_same_test_benchmarks" / "results"
OUT_JSON = PAPER / "RA2021_SOURCE_IDENTITY_AUDIT.json"
OUT_MD = PAPER / "RA2021_SOURCE_IDENTITY_AUDIT.md"


SOURCE_FILES = {
    "standard_setup": SOURCE / "utils" / "tools.py",
    "four_link_model": SOURCE / "example_models" / "four_link.py",
    "slider_crank_model": SOURCE / "example_models" / "slider_crank.py",
    "double_pendulum_model": SOURCE / "example_models" / "double_pendulum.py",
    "system_ra": SOURCE / "rA" / "system_ra.py",
    "system_rp": SOURCE / "rp" / "system_rp.py",
    "system_reps": SOURCE / "rEps" / "system_reps.py",
}


def rel(path: Path) -> str:
    return str(path.relative_to(PROJECT))


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def find_line(path: Path, needle: str) -> int:
    for lineno, line in enumerate(read_text(path).splitlines(), start=1):
        if needle in line:
            return lineno
    raise ValueError(f"{needle!r} not found in {path}")


def has(path: Path, needle: str) -> bool:
    return needle in read_text(path)


def source_anchor(path: Path, needle: str) -> dict[str, object]:
    return {
        "file": rel(path),
        "line": find_line(path, needle),
        "needle": needle,
    }


def unique_sorted(rows: list[dict[str, str]], key: str) -> list[object]:
    values: set[object] = set()
    for row in rows:
        value = row.get(key, "")
        if value == "":
            continue
        try:
            values.add(float(value))
        except ValueError:
            values.add(value)
    return sorted(values)


def main() -> int:
    for path in SOURCE_FILES.values():
        if not path.exists():
            raise FileNotFoundError(path)

    order_rows = read_csv(V048_RESULTS / "ra2021_order_rows.csv")
    double_rows = read_csv(V048_RESULTS / "ra2021_double_pendulum_order_rows.csv")
    summary_rows = read_csv(V048_RESULTS / "ra2021_public_order_work_summary.csv")
    timing_rows = read_csv(V048_RESULTS / "ra2021_public_timing_rows.csv")
    forensic_rows = read_csv(V048_RESULTS / "all_examples_apples_to_apples_forensic_audit.csv")
    ra_forensic_rows = [row for row in forensic_rows if row.get("method", "").startswith("ra2021_")]

    output_assignments = {
        "four_link": {
            "position": source_anchor(SOURCE_FILES["four_link_model"], "pos_data[j, :, i] = body.r.T"),
            "velocity": source_anchor(SOURCE_FILES["four_link_model"], "vel_data[j, :, i] = body.dr.T"),
            "acceleration": source_anchor(SOURCE_FILES["four_link_model"], "acc_data[j, :, i] = body.ddr.T"),
        },
        "slider_crank": {
            "position": source_anchor(SOURCE_FILES["slider_crank_model"], "pos_data[j, :, i] = body.r.T"),
            "velocity": source_anchor(SOURCE_FILES["slider_crank_model"], "vel_data[j, :, i] = body.dr.T"),
            "acceleration": source_anchor(SOURCE_FILES["slider_crank_model"], "acc_data[j, :, i] = body.ddr.T"),
        },
        "double_pendulum": {
            "position": source_anchor(SOURCE_FILES["double_pendulum_model"], "pos_data[j, :, i] = body.r.T"),
            "velocity": source_anchor(SOURCE_FILES["double_pendulum_model"], "vel_data[j, :, i] = body.dr.T"),
            "acceleration": source_anchor(SOURCE_FILES["double_pendulum_model"], "acc_data[j, :, i] = body.ddr.T"),
        },
    }
    form_velocity_assignments = {
        "rA": {
            "translational_velocity": source_anchor(SOURCE_FILES["system_ra"], "body.dr = dq[3*j:3*(j+1), :]"),
            "dynamics_update": source_anchor(SOURCE_FILES["system_ra"], "body.dr = body.dr_prev + self.h*body.ddr"),
            "position_update": source_anchor(SOURCE_FILES["system_ra"], "body.r = body.r_prev + self.h*body.dr"),
        },
        "rp": {
            "translational_velocity": source_anchor(SOURCE_FILES["system_rp"], "body.dr = dq[3*j:3*(j+1), :]"),
        },
        "reps": {
            "translational_velocity": source_anchor(SOURCE_FILES["system_reps"], "body.dr = dq[3*j:3*(j+1), :]"),
        },
    }
    time_grid_policy = {
        "t_end_argument": source_anchor(SOURCE_FILES["standard_setup"], "parser.add_argument('-t', '--end_time', type=float, default=3, dest='t_end')"),
        "h_argument": source_anchor(SOURCE_FILES["standard_setup"], "parser.add_argument('--step_size', type=float, default=1e-3, dest='h')"),
        "time_step_count_four_link": source_anchor(SOURCE_FILES["four_link_model"], "t_steps = int(params.t_end/params.h)"),
        "time_grid_four_link": source_anchor(SOURCE_FILES["four_link_model"], "t_grid = np.linspace(0, params.t_end, t_steps, endpoint=True)"),
        "step_call_four_link": source_anchor(SOURCE_FILES["four_link_model"], "sys.do_step(i, t)"),
        "time_step_count_slider_crank": source_anchor(SOURCE_FILES["slider_crank_model"], "t_steps = int(params.t_end/params.h)"),
        "time_grid_slider_crank": source_anchor(SOURCE_FILES["slider_crank_model"], "t_grid = np.linspace(0, params.t_end, t_steps, endpoint=True)"),
        "step_call_slider_crank": source_anchor(SOURCE_FILES["slider_crank_model"], "sys.do_step(i, t)"),
        "time_step_count_double_pendulum": source_anchor(SOURCE_FILES["double_pendulum_model"], "t_steps = int(params.t_end/params.h)"),
        "time_grid_double_pendulum": source_anchor(SOURCE_FILES["double_pendulum_model"], "t_grid = np.linspace(0, params.t_end, t_steps, endpoint=True)"),
        "step_call_double_pendulum": source_anchor(SOURCE_FILES["double_pendulum_model"], "sys.do_step(i, t)"),
        "public_point_count_formula": "int(t_end / h)",
        "public_grid_formula": "numpy.linspace(0, t_end, int(t_end / h), endpoint=True)",
        "public_grid_interval_formula": "t_end / (int(t_end / h) - 1) for saved output times when int(t_end / h) > 1",
        "example_interval_T3_h1e_3": 3.0 / (int(3.0 / 0.001) - 1),
    }
    setup_identity = {
        "form_choices_present": has(SOURCE_FILES["standard_setup"], "choices=['rp', 'rA', 'reps']"),
        "mode_choices_present": has(SOURCE_FILES["standard_setup"], "choices=['kin', 'dyn', 'kinematics', 'dynamics']"),
        "tol_optional": has(SOURCE_FILES["standard_setup"], "parser.add_argument('--tol', type=float)"),
        "form_dispatch": {
            "rp": has(SOURCE_FILES["standard_setup"], "SystemRP.init_from_file(model_file)"),
            "rA": has(SOURCE_FILES["standard_setup"], "SystemRA.init_from_file(model_file)"),
            "reps": has(SOURCE_FILES["standard_setup"], "SystemREps.init_from_file(model_file)"),
        },
        "mode_dispatch": {
            "kinematics": has(SOURCE_FILES["standard_setup"], "sys.set_kinematics()"),
            "dynamics": has(SOURCE_FILES["standard_setup"], "sys.set_dynamics()"),
        },
    }

    ra_summary_rows = [row for row in summary_rows if row.get("source_suite") == "ra2021_taves_kissel_negrut"]
    ra_timing_rows = [row for row in timing_rows if row.get("source_suite") == "ra2021_taves_kissel_negrut"]
    status_ok = sum(1 for row in order_rows + double_rows if row.get("status") == "ok")
    position_mismatch_rows = [
        row for row in ra_forensic_rows if "position_aligned_velocity_mismatch" in row.get("issues", "")
    ]
    floor_rows = [
        row for row in ra_forensic_rows if "velocity_error_nonmonotone_or_floor_limited" in row.get("issues", "")
    ]

    double_group_count = len({(row.get("form"), row.get("model")) for row in double_rows})
    summary_models = {row.get("model") for row in ra_summary_rows if row.get("model")}
    double_models = {row.get("model") for row in double_rows if row.get("model")}
    artifact_alignment = {
        "public_order_summary_rows": len(ra_summary_rows),
        "public_order_summary_completed_rows": sum(
            1 for row in ra_summary_rows if row.get("public_step_trio_completed") == "True"
        ),
        "public_double_order_groups": double_group_count,
        "public_order_groups_total": len(ra_summary_rows) + double_group_count,
        "raw_order_rows": len(order_rows) + len(double_rows),
        "raw_order_ok_rows": status_ok,
        "timing_rows": len(ra_timing_rows),
        "timing_ok_rows": sum(1 for row in ra_timing_rows if row.get("status") == "ok"),
        "forms": unique_sorted(ra_summary_rows, "form"),
        "models": sorted(summary_models | double_models),
        "t_end_values": unique_sorted(ra_summary_rows, "t_end"),
        "summary_finest_h_values": unique_sorted(ra_summary_rows, "finest_h"),
        "single_four_slider_reference_mode": sorted(
            {row.get("reference_mode") for row in order_rows if row.get("reference_mode")}
        ),
        "double_reference_policy": sorted(
            {row.get("reference_policy") for row in double_rows if row.get("reference_policy")}
        ),
    }

    output_mapping_verified = (
        len(output_assignments) == 3
        and all(set(assignments) == {"position", "velocity", "acceleration"} for assignments in output_assignments.values())
        and all("translational_velocity" in assignments for assignments in form_velocity_assignments.values())
    )
    time_grid_policy_extracted = all(
        isinstance(value, dict) and value.get("line")
        for key, value in time_grid_policy.items()
        if key.endswith(("four_link", "slider_crank", "double_pendulum")) or key in {"t_end_argument", "h_argument"}
    )
    status = "source_output_time_grid_policy_extracted_promotion_still_open"
    output = {
        "schema": "ra2021-source-identity-audit-v1",
        "status": status,
        "suite_id": "ra2021_absolute_coordinate",
        "source_suite": "ra2021_taves_kissel_negrut",
        "read_only": True,
        "source_files": {key: rel(path) for key, path in SOURCE_FILES.items()},
        "setup_identity": setup_identity,
        "output_assignments": output_assignments,
        "form_velocity_assignments": form_velocity_assignments,
        "time_grid_policy": time_grid_policy,
        "artifact_alignment": artifact_alignment,
        "forensic_issue_counts": {
            "ra2021_forensic_rows": len(ra_forensic_rows),
            "position_aligned_velocity_mismatch_rows": len(position_mismatch_rows),
            "velocity_nonmonotone_or_floor_limited_rows": len(floor_rows),
        },
        "subrequirements_resolved_by_this_audit": [
            "document_public_code_path_and_source_setup_identity",
            "verify_body_r_body_dr_body_ddr_output_mapping_from_source",
            "extract_public_endpoint_time_grid_convention_from_source",
        ],
        "subrequirements_still_open": [
            "run_or_promote_local_Gauss6_FullVA_under_the_same_RA2021_source_time_grid_and_dynamic_policy",
            "bind_error_norm_columns_to_accepted_source_policy_order_rows",
            "tie_runtime_and_Newton_iteration_policy_to_the_accepted_source_policy_order_rows",
            "produce_rerun_or_independent_verification_artifact_for_promoted_rows",
        ],
        "claim_boundary": {
            "output_mapping_verified_from_source": output_mapping_verified,
            "time_grid_policy_extracted_from_source": bool(time_grid_policy_extracted),
            "existing_velocity_mismatch_rows_reinterpreted_as_policy_mismatch_not_unknown_output_mapping": True,
            "source_policy_reproduction_rows_closed": 0,
            "can_close_ra2021_b2_requirement_now": False,
            "external_superiority_claim_allowed": False,
            "default_1e_4_required": False,
            "heavy_numerical_run_invoked": False,
            "run_v047_invoked": False,
            "v048_runner_invoked": False,
        },
    }

    OUT_JSON.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    md = [
        "# RA2021 Source Identity Audit",
        "",
        f"Status: `{status}`.",
        "",
        "This read-only audit inspects the public RA2021 C2 SimEngineMBD source path and the existing v048 RA2021 rows. It does not rerun `run_v047.py`, does not launch v048 runners, and does not run a default `1e-4` campaign.",
        "",
        "## Confirmed From Source",
        "",
        "- The public setup exposes `form in {rp,rA,reps}`, `mode in {kin,dyn,kinematics,dynamics}`, optional `--tol`, default `T=3`, and default `h=1e-3`.",
        "- The example model output arrays store `pos_data=body.r`, `vel_data=body.dr`, and `acc_data=body.ddr` for four-link, slider-crank, and double-pendulum.",
        "- The formulation systems assign translational velocity from the first translational block into `body.dr`.",
        "- The public saved output time grid is `np.linspace(0, T, int(T/h), endpoint=True)`, so the saved-time interval is `T/(int(T/h)-1)` while the integrator step size remains `h`.",
        "",
        "## Existing Artifact Alignment",
        "",
        f"- Public order summary rows: `{artifact_alignment['public_order_summary_completed_rows']}/{artifact_alignment['public_order_summary_rows']}` plus double-pendulum groups `{artifact_alignment['public_double_order_groups']}`.",
        f"- Public order groups total: `{artifact_alignment['public_order_groups_total']}/12`.",
        f"- Raw order rows: `{artifact_alignment['raw_order_ok_rows']}/{artifact_alignment['raw_order_rows']}`.",
        f"- Timing rows: `{artifact_alignment['timing_ok_rows']}/{artifact_alignment['timing_rows']}`.",
        f"- Forms: `{','.join(artifact_alignment['forms'])}`.",
        f"- Models: `{','.join(artifact_alignment['models'])}`.",
        f"- T values: `{artifact_alignment['t_end_values']}`.",
        "",
        "## Claim Boundary",
        "",
        f"- Output mapping verified from source: `{output_mapping_verified}`.",
        f"- Time-grid policy extracted from source: `{bool(time_grid_policy_extracted)}`.",
        f"- RA2021 forensic rows with position-aligned velocity mismatch: `{len(position_mismatch_rows)}`.",
        f"- RA2021 forensic rows with velocity nonmonotone/floor-limited issues: `{len(floor_rows)}`.",
        "- The velocity-mismatch rows are no longer treated as an unknown `body.dr` output-mapping problem; they remain source-policy promotion blockers because the local Gauss6 row, error norm, time-grid, runtime, and Newton policy are not yet bound into one accepted RA2021 same-policy comparison.",
        "- Source-policy rows closed by this audit: `0`.",
        "- Can close RA2021 B2 requirement now: `False`.",
        "- External-superiority claim allowed: `False`.",
        "",
        "Validator: `validate_ra2021_source_identity_audit.py`.",
        "",
    ]
    OUT_MD.write_text("\n".join(md), encoding="utf-8")
    print("ra2021_source_identity_audit=written")
    print(f"output_mapping_verified={output_mapping_verified}")
    print(f"time_grid_policy_extracted={bool(time_grid_policy_extracted)}")
    print("source_policy_rows_closed=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
