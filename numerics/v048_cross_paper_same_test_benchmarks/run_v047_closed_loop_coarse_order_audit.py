#!/usr/bin/env python3
"""Coarse-h observed-order audit for v047 closed-loop kinematic FullVA rows."""

from __future__ import annotations

import argparse
import importlib.util
import sys

import run_v048


def load_v047():
    module_name = "v047_for_closed_loop_coarse_order_audit"
    if module_name in sys.modules:
        return sys.modules[module_name]
    path = run_v048.WORK_ROOT / "v047_cylindrical_chain_pipeline" / "run_v047.py"
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--step-sizes", default="0.1,0.05,0.025")
    parser.add_argument("--reference-h", type=float, default=0.001)
    parser.add_argument("--t-final", type=float, default=0.2)
    args = parser.parse_args()

    v047 = load_v047()
    v046 = v047.load_v046()
    v046.patch_modern_numpy_scalar_assignments()
    step_sizes = run_v048.parse_float_csv(args.step_sizes)
    rows: list[dict] = []
    for model in [item for item in v046.MODELS if item.name in {"four_link", "slider_crank"}]:
        reference = v047.simulate_v046_local_kinematic_fullva(
            v046, model, args.reference_h, args.t_final, v047.ASME_CLOSED_LOOP_KINEMATIC_TOL
        )
        pos_errors: list[float] = []
        vel_errors: list[float] = []
        acc_errors: list[float] = []
        model_rows: list[dict] = []
        for h in step_sizes:
            candidate = v047.simulate_v046_local_kinematic_fullva(
                v046, model, h, args.t_final, v047.ASME_CLOSED_LOOP_KINEMATIC_TOL
            )
            err = v047.compare_nested_trajectory_with_acc(reference, candidate)
            pos_errors.append(err["pos_traj_linf"])
            vel_errors.append(err["vel_traj_linf"])
            acc_errors.append(err["acc_traj_linf"])
            model_rows.append(
                {
                    "policy": "v047_closed_loop_kinematic_fullva_coarse_order_audit",
                    "model": model.name,
                    "method": "local_phi_phiq_kinematic_fullva_newton",
                    "h": h,
                    "reference_h": args.reference_h,
                    "t_final": args.t_final,
                    "status": "ok",
                    "pos_traj_linf": f"{err['pos_traj_linf']:.16e}",
                    "vel_traj_linf": f"{err['vel_traj_linf']:.16e}",
                    "acc_traj_linf": f"{err['acc_traj_linf']:.16e}",
                    "max_position_constraint_norm": f"{candidate['max_position_constraint_norm']:.16e}",
                    "max_velocity_constraint_norm": f"{candidate['max_velocity_constraint_norm']:.16e}",
                    "max_acceleration_constraint_norm": f"{candidate['max_acceleration_constraint_norm']:.16e}",
                    "runtime_sec": f"{candidate['runtime_sec']:.16e}",
                    "notes": (
                        "Coarse observed-slope diagnostic for the accepted v047 closed-loop kinematic "
                        "FullVA scaffold. This is a numeric slope audit, not a dynamic method-order claim."
                    ),
                }
            )
        orders = {
            "pos_observed_order": v047.observed_order(list(step_sizes), pos_errors),
            "vel_observed_order": v047.observed_order(list(step_sizes), vel_errors),
            "acc_observed_order": v047.observed_order(list(step_sizes), acc_errors),
        }
        for row in model_rows:
            row.update({key: f"{value:.16e}" for key, value in orders.items()})
        rows.extend(model_rows)

    run_v048.write_csv(run_v048.RESULTS / "v047_closed_loop_coarse_order_audit.csv", rows)
    for model in ("four_link", "slider_crank"):
        model_rows = [row for row in rows if row["model"] == model]
        first = model_rows[0]
        print(
            f"{model}: "
            f"{float(first['pos_observed_order']):.3f}/"
            f"{float(first['vel_observed_order']):.3f}/"
            f"{float(first['acc_observed_order']):.3f}"
        )


if __name__ == "__main__":
    main()
