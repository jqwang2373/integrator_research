#!/usr/bin/env python3
"""Build a setup-level interface audit for closed-loop true-dynamic rows.

This is intentionally lightweight: it imports the current v047/v046 public
model interface, constructs kinematic and dynamic systems, initializes them,
and records dimensions/callable availability. It does not call do_step and
therefore does not run a trajectory campaign.
"""

from __future__ import annotations

import csv
import importlib.util
import json
import sys
import time
from pathlib import Path


HERE = Path(__file__).resolve().parent
WORK_ROOT = HERE.parent
RESULTS = HERE / "results"
V047_RUN = WORK_ROOT / "v047_cylindrical_chain_pipeline" / "run_v047.py"
MODELS = ("four_link", "slider_crank")
MODES = ("kinematics", "dynamics")
H = 0.1
T_END = 0.1
TOL = 1.0e-10
OUT_CSV = RESULTS / "closed_loop_true_dynamic_interface_audit.csv"
OUT_JSON = RESULTS / "closed_loop_true_dynamic_interface_audit.json"
OUT_MD = RESULTS / "closed_loop_true_dynamic_interface_audit.md"


def import_v047_module():
    module_name = "v047_cylindrical_chain_pipeline_run_v047_for_dynamic_interface_audit"
    if module_name in sys.modules:
        return sys.modules[module_name]
    spec = importlib.util.spec_from_file_location(module_name, V047_RUN)
    if spec is None or spec.loader is None:
        raise ImportError(f"could not load {V047_RUN}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def read_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def shape_text(value: object) -> str:
    shape = getattr(value, "shape", None)
    if shape is None:
        return "missing"
    return "x".join(str(int(item)) for item in shape)


def bool_text(value: bool) -> str:
    return str(bool(value)).lower()


def solver_name(system) -> str:
    solver_type = getattr(system, "solver_type", None)
    return str(getattr(solver_type, "name", solver_type))


def constraint_counts(v047_module, system) -> str:
    try:
        counts = v047_module.v046_constraint_type_counts(system)
    except Exception:  # noqa: BLE001 - audit field, not control flow.
        return "unavailable"
    return "|".join(f"{key}:{counts[key]}" for key in sorted(counts))


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError("refusing to write empty interface audit")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def audit_row(v047_module, v046, model, mode: str) -> dict[str, object]:
    started = time.perf_counter()
    row: dict[str, object] = {
        "model": model.name,
        "setup_mode": mode,
        "setup_status": "ok",
        "h": f"{H:.16e}",
        "t_end": f"{T_END:.16e}",
        "tol": f"{TOL:.16e}",
        "do_step_called": "false",
        "heavy_numerical_run_invoked": "false",
        "default_policy": "coarse_first_no_default_1e-4",
        "strict_public_policy_1e-4_required": "false",
        "accepted_dynamic_order": "false",
        "notes": "",
    }
    try:
        system, _params = v046.setup_system(model, mode, H, T_END, TOL)
        row["solver_type_before_initialize"] = solver_name(system)
        system.initialize()
        nb = int(system.nb)
        nc = int(system.nc)
        generalized_dim = 6 * nb
        row.update(
            {
                "solver_type_after_initialize": solver_name(system),
                "body_count": nb,
                "constraint_count": nc,
                "generalized_dim": generalized_dim,
                "constraint_count_equals_generalized_dim": bool_text(nc == generalized_dim),
                "lambda_dim": nc,
                "public_newton_unknown_dim": generalized_dim + nc if mode == "dynamics" else "not_applicable",
                "fullva_true_dynamic_min_unknown_blocks": (
                    "q|orientation|v|omega|a|alpha|lambda"
                    if mode == "dynamics"
                    else "not_applicable"
                ),
                "constraint_counts": constraint_counts(v047_module, system),
                "mass_matrix_shape": shape_text(getattr(system, "M", None)),
                "inertia_matrix_shape": shape_text(getattr(system, "J", None)),
                "force_vector_shape": shape_text(getattr(system, "F_ext", None)),
                "lambda_vector_shape": shape_text(getattr(system, "\u03bb", None)),
                "api_get_phi": bool_text(hasattr(system.g_cons, "get_phi")),
                "api_get_phi_q": bool_text(hasattr(system.g_cons, "get_phi_q")),
                "api_get_phi_r": bool_text(hasattr(system.g_cons, "get_phi_r")),
                "api_get_pi": bool_text(hasattr(system.g_cons, "get_pi")),
                "api_get_nu": bool_text(hasattr(system.g_cons, "get_nu")),
                "api_get_gamma": bool_text(hasattr(system.g_cons, "get_gamma")),
                "api_maybe_swap_gcons": bool_text(hasattr(system.g_cons, "maybe_swap_gcons")),
                "public_do_dynamics_step_available": bool_text(hasattr(system, "do_dynamics_step")),
                "local_gauss6_dynamic_runner_exists": bool_text(hasattr(v047_module, "simulate_v046_local_dynamic_fullva")),
                "runtime_sec": f"{time.perf_counter() - started:.16e}",
                "notes": (
                    "Setup and initialization only; public rA dynamic stepper exists, "
                    "but local Gauss6/FullVA true-dynamic runner is not implemented."
                ),
            }
        )
    except Exception as exc:  # noqa: BLE001 - keep audit row visible.
        row.update(
            {
                "setup_status": f"failed:{type(exc).__name__}:{str(exc).replace(chr(10), ' ')}",
                "solver_type_before_initialize": "nan",
                "solver_type_after_initialize": "nan",
                "body_count": "nan",
                "constraint_count": "nan",
                "generalized_dim": "nan",
                "constraint_count_equals_generalized_dim": "false",
                "lambda_dim": "nan",
                "public_newton_unknown_dim": "nan",
                "fullva_true_dynamic_min_unknown_blocks": "nan",
                "constraint_counts": "nan",
                "mass_matrix_shape": "nan",
                "inertia_matrix_shape": "nan",
                "force_vector_shape": "nan",
                "lambda_vector_shape": "nan",
                "api_get_phi": "false",
                "api_get_phi_q": "false",
                "api_get_phi_r": "false",
                "api_get_pi": "false",
                "api_get_nu": "false",
                "api_get_gamma": "false",
                "api_maybe_swap_gcons": "false",
                "public_do_dynamics_step_available": "false",
                "local_gauss6_dynamic_runner_exists": bool_text(hasattr(v047_module, "simulate_v046_local_dynamic_fullva")),
                "runtime_sec": f"{time.perf_counter() - started:.16e}",
            }
        )
    return row


def write_markdown(summary: dict, rows: list[dict[str, object]]) -> None:
    lines = [
        "# Closed-Loop True-Dynamic Interface Audit",
        "",
        "Status: **setup-level interface verified; no trajectory rows run**",
        "",
        f"- Models: `{', '.join(summary['models'])}`.",
        f"- Dynamic setup rows ok: `{summary['dynamic_setup_ok_count']}/{summary['dynamic_setup_required_count']}`.",
        f"- Local `Gauss6/FullVA` dynamic runner exists: `{summary['local_gauss6_dynamic_runner_exists']}`.",
        f"- `do_step` called: `{summary['do_step_called']}`.",
        f"- Heavy numerical run invoked: `{summary['heavy_numerical_run_invoked']}`.",
        f"- Default `1e-4` required: `{summary['default_1e-4_required']}`.",
        "",
        "The public/v046 `rA` system can be constructed in `dynamics` mode for",
        "`four_link` and `slider_crank`; the missing piece is not model access.",
        "The missing piece is the local `Gauss6/FullVA` dynamic trajectory",
        "stepper that couples state, velocity, acceleration, and multipliers",
        "inside the method residual.",
        "",
        "| Model | Mode | setup | solver | nb | nc | 6nb | public Newton dim | local runner |",
        "|---|---|---|---|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            "| "
            f"`{row['model']}` | `{row['setup_mode']}` | `{row['setup_status']}` | "
            f"`{row['solver_type_after_initialize']}` | `{row['body_count']}` | "
            f"`{row['constraint_count']}` | `{row['generalized_dim']}` | "
            f"`{row['public_newton_unknown_dim']}` | `{row['local_gauss6_dynamic_runner_exists']}` |"
        )
    lines.extend(
        [
            "",
            "## Consequence",
            "",
            "The next implementation should reuse the verified constraint and",
            "mass/inertia interfaces, but it must not call the public `do_step` as",
            "the local method. A valid row must assemble the local",
            "`Gauss6/FullVA` dynamic residual itself and then compare the resulting",
            "trajectory on the coarse-first row plan.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    plan = read_json(RESULTS / "closed_loop_true_dynamic_local_row_plan.json")
    v047_module = import_v047_module()
    v046 = v047_module.load_v046()
    v046.patch_modern_numpy_scalar_assignments()
    models = {model.name: model for model in v046.MODELS}
    rows = []
    for model_name in MODELS:
        if model_name not in models:
            raise ValueError(f"v046 model not found: {model_name}")
        for mode in MODES:
            rows.append(audit_row(v047_module, v046, models[model_name], mode))

    dynamic_rows = [row for row in rows if row["setup_mode"] == "dynamics"]
    dynamic_ok = [row for row in dynamic_rows if row["setup_status"] == "ok"]
    summary = {
        "schema": "closed-loop-true-dynamic-interface-audit-v1",
        "status": "setup_level_interface_verified_no_trajectory_run",
        "models": list(MODELS),
        "modes": list(MODES),
        "row_count": len(rows),
        "dynamic_setup_ok_count": len(dynamic_ok),
        "dynamic_setup_required_count": len(MODELS),
        "kinematic_setup_ok_count": len([row for row in rows if row["setup_mode"] == "kinematics" and row["setup_status"] == "ok"]),
        "local_gauss6_dynamic_runner_exists": False,
        "public_dynamic_setup_available": len(dynamic_ok) == len(MODELS),
        "public_do_dynamics_step_available": all(row.get("public_do_dynamics_step_available") == "true" for row in dynamic_rows),
        "do_step_called": False,
        "heavy_numerical_run_invoked": False,
        "default_policy": "coarse_first_no_default_1e-4",
        "strict_public_policy_1e-4_required": False,
        "default_1e-4_required": False,
        "accepted_dynamic_order_count": 0,
        "external_superiority_claim": False,
        "required_next_runner": plan.get("required_new_runner"),
        "row_plan_schema": plan.get("schema"),
        "row_plan_count": plan.get("row_count"),
        "interpretation": (
            "The real public/v046 dynamic setup interfaces are available for both closed-loop models. "
            "The missing implementation is the local Gauss6/FullVA dynamic DAE stepper, not another "
            "1e-4 public-policy run."
        ),
    }
    write_csv(OUT_CSV, rows)
    with OUT_JSON.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, sort_keys=True)
        handle.write("\n")
    write_markdown(summary, rows)
    print("closed_loop_true_dynamic_interface_audit=written")
    print("status=setup_level_interface_verified_no_trajectory_run")
    print(f"dynamic_setup_ok={len(dynamic_ok)}/{len(MODELS)}")
    print("local_gauss6_dynamic_runner_exists=False")
    print("do_step_called=False")
    print("default_1e-4=False")
    print("accepted_dynamic_order=0")


if __name__ == "__main__":
    main()
