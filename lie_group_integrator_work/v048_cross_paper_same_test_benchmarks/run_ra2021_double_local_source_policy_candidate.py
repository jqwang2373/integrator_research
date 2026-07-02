#!/usr/bin/env python3
"""Create an isolated RA2021 double-pendulum local FullVA source-policy candidate.

By default this writes a plan-only artifact for the exact source-policy
configuration. Pass ``--execute`` and ``--allow-source-policy-1e-4`` to run the
heavy h_ref=1e-4 numerical reference.
"""

from __future__ import annotations

import argparse
import csv
import time
from pathlib import Path

import numpy as np

import run_v048 as rv


STEM = "ra2021_double_local_source_policy_candidate"
JAX_SAFE_SMALL_ANGLE_PATCH_ID = "isolated_v013_jax_safe_small_angle_taylor_v1"


def close(a: float, b: float) -> bool:
    return abs(float(a) - float(b)) <= 1.0e-15


def step_count(t_end: float, h: float) -> int:
    return int(round(float(t_end) / float(h)))


def source_policy_selected(step_sizes: tuple[float, ...], reference_h: float, t_end: float) -> bool:
    return (
        list(step_sizes) == list(rv.RA2021_DOUBLE_ORDER_STEP_SIZES)
        and close(reference_h, rv.RA2021_DOUBLE_ORDER_REFERENCE_H)
        and close(t_end, rv.RA2021_PUBLIC_T_END)
    )


def tag_float(value: float) -> str:
    return f"{float(value):g}".replace(".", "p").replace("-", "m")


def reference_cache_path(output_stem: str, reference_h: float, t_end: float) -> Path:
    return rv.RESULTS / f"{output_stem}_reference_h{tag_float(reference_h)}_T{tag_float(t_end)}.npz"


def reference_checkpoint_path(output_stem: str, reference_h: float, t_end: float) -> Path:
    return rv.RESULTS / f"{output_stem}_reference_h{tag_float(reference_h)}_T{tag_float(t_end)}_checkpoint.npz"


def save_trajectory(path: Path, trajectory: dict, runtime_sec: float) -> None:
    np.savez_compressed(
        path,
        h=float(trajectory["h"]),
        steps=int(trajectory["steps"]),
        pos=np.asarray(trajectory["pos"], dtype=float),
        vel=np.asarray(trajectory["vel"], dtype=float),
        total_newton_iterations=int(trajectory["total_newton_iterations"]),
        max_endpoint_constraint_norm=float(trajectory["max_endpoint_constraint_norm"]),
        max_endpoint_velocity_constraint_norm=float(trajectory["max_endpoint_velocity_constraint_norm"]),
        runtime_sec=float(runtime_sec),
    )


def load_trajectory(path: Path) -> tuple[dict, float]:
    with np.load(path) as data:
        trajectory = {
            "h": float(data["h"]),
            "steps": int(data["steps"]),
            "pos": np.asarray(data["pos"], dtype=float),
            "vel": np.asarray(data["vel"], dtype=float),
            "total_newton_iterations": int(data["total_newton_iterations"]),
            "max_endpoint_constraint_norm": float(data["max_endpoint_constraint_norm"]),
            "max_endpoint_velocity_constraint_norm": float(data["max_endpoint_velocity_constraint_norm"]),
        }
        runtime_sec = float(data["runtime_sec"])
    return trajectory, runtime_sec


def install_v029_jax_safe_small_angle_patch(v029) -> None:
    """Patch only this loaded v029 module with AD-safe small-angle Taylor helpers."""
    jnp = v029.jnp
    qp = v029.qp

    def quat_exp_jax(theta):
        theta2 = jnp.dot(theta, theta)
        small = theta2 < 1.0e-16
        safe_theta2 = jnp.where(small, jnp.array(1.0, dtype=theta.dtype), theta2)
        angle = jnp.sqrt(safe_theta2)
        scalar_small = 1.0 - theta2 / 8.0 + theta2 * theta2 / 384.0
        b_small = 0.5 - theta2 / 48.0 + theta2 * theta2 / 3840.0
        scalar_large = jnp.cos(0.5 * angle)
        b_large = jnp.sin(0.5 * angle) / angle
        scalar = jnp.where(small, scalar_small, scalar_large)
        b = jnp.where(small, b_small, b_large)
        return jnp.concatenate((jnp.array([scalar], dtype=theta.dtype), b * theta))

    def compose_right_quat_jax(q, u):
        out = qp.quat_mul_jax(q, quat_exp_jax(u))
        return out / jnp.linalg.norm(out)

    def right_jacobian_inverse_apply_jax(u, w):
        theta2 = jnp.dot(u, u)
        small = theta2 < 1.0e-14
        safe_theta2 = jnp.where(small, jnp.array(1.0, dtype=u.dtype), theta2)
        theta = jnp.sqrt(safe_theta2)
        U = qp._hat_jax(u)
        U2 = U @ U
        coeff_small = 1.0 / 12.0 + theta2 / 720.0 + theta2 * theta2 / 30240.0
        coeff_large = 1.0 / safe_theta2 - (1.0 + jnp.cos(theta)) / (2.0 * theta * jnp.sin(theta))
        coeff = jnp.where(small, coeff_small, coeff_large)
        return (jnp.eye(3, dtype=u.dtype) + 0.5 * U + coeff * U2) @ w

    qp.quat_exp_jax = quat_exp_jax
    qp.compose_right_quat_jax = compose_right_quat_jax
    qp._right_jacobian_inverse_apply_jax = right_jacobian_inverse_apply_jax
    v029._ra2021_candidate_jax_safe_small_angle_patch = JAX_SAFE_SMALL_ANGLE_PATCH_ID


def load_v029_for_candidate(v047_module, use_jax_safe_small_angle_patch: bool):
    v029 = v047_module.load_v029()
    if use_jax_safe_small_angle_patch:
        install_v029_jax_safe_small_angle_patch(v029)
    return v029


def state_payload(state) -> dict[str, np.ndarray]:
    return {
        "state_r1": np.asarray(state.r1, dtype=float),
        "state_p1": np.asarray(state.p1, dtype=float),
        "state_v1": np.asarray(state.v1, dtype=float),
        "state_w1": np.asarray(state.w1, dtype=float),
        "state_r2": np.asarray(state.r2, dtype=float),
        "state_p2": np.asarray(state.p2, dtype=float),
        "state_v2": np.asarray(state.v2, dtype=float),
        "state_w2": np.asarray(state.w2, dtype=float),
    }


def payload_state(v029, data) -> object:
    return v029.State(
        r1=np.asarray(data["state_r1"], dtype=float),
        p1=np.asarray(data["state_p1"], dtype=float),
        v1=np.asarray(data["state_v1"], dtype=float),
        w1=np.asarray(data["state_w1"], dtype=float),
        r2=np.asarray(data["state_r2"], dtype=float),
        p2=np.asarray(data["state_p2"], dtype=float),
        v2=np.asarray(data["state_v2"], dtype=float),
        w2=np.asarray(data["state_w2"], dtype=float),
    )


def save_reference_checkpoint(
    path: Path,
    *,
    h: float,
    t_end: float,
    current_step: int,
    pos: np.ndarray,
    vel: np.ndarray,
    state,
    total_iters: int,
    max_endpoint_constraint: float,
    max_endpoint_velocity_constraint: float,
    runtime_sec: float,
) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("wb") as handle:
        np.savez(
            handle,
            h=float(h),
            t_end=float(t_end),
            current_step=int(current_step),
            total_steps=int(round(float(t_end) / float(h))),
            pos=np.asarray(pos, dtype=float),
            vel=np.asarray(vel, dtype=float),
            total_newton_iterations=int(total_iters),
            max_endpoint_constraint_norm=float(max_endpoint_constraint),
            max_endpoint_velocity_constraint_norm=float(max_endpoint_velocity_constraint),
            runtime_sec=float(runtime_sec),
            **state_payload(state),
        )
    tmp.replace(path)


def load_reference_checkpoint(path: Path, v029) -> dict:
    with np.load(path) as data:
        return {
            "h": float(data["h"]),
            "t_end": float(data["t_end"]),
            "current_step": int(data["current_step"]),
            "total_steps": int(data["total_steps"]),
            "pos": np.asarray(data["pos"], dtype=float),
            "vel": np.asarray(data["vel"], dtype=float),
            "state": payload_state(v029, data),
            "total_newton_iterations": int(data["total_newton_iterations"]),
            "max_endpoint_constraint_norm": float(data["max_endpoint_constraint_norm"]),
            "max_endpoint_velocity_constraint_norm": float(data["max_endpoint_velocity_constraint_norm"]),
            "runtime_sec": float(data["runtime_sec"]),
        }


def read_existing_rows(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def rows_match_policy(rows: list[dict], step_sizes: tuple[float, ...], reference_h: float, t_end: float) -> bool:
    if len(rows) != len(step_sizes):
        return False
    try:
        row_h = sorted(float(row["h"]) for row in rows)
    except (KeyError, ValueError):
        return False
    return (
        row_h == sorted(float(h) for h in step_sizes)
        and all(close(float(row.get("reference_h", "nan")), reference_h) for row in rows)
        and all(close(float(row.get("t_end", "nan")), t_end) for row in rows)
    )


def make_base_rows(
    *,
    step_sizes: tuple[float, ...],
    reference_h: float,
    t_end: float,
    output_stem: str,
    execution_mode: str,
) -> tuple[list[dict], dict]:
    config = rv.Gauss6PublicDoubleCoarseConfig(
        policy="gauss6_fullva_ra2021_double_local_source_policy_candidate",
        run_mode="ra2021_double_local_fullva_source_policy_candidate",
        step_sizes=step_sizes,
        reference_h=reference_h,
        t_end=t_end,
        run_model=False,
    )
    rows, raw_summary = rv.run_gauss6_fullva_public_horizon_double_coarse_rows(config)
    selected = source_policy_selected(step_sizes, reference_h, t_end)
    row_notes = (
        "Isolated local Gauss6/FullVA double-pendulum candidate for the exact RA2021 "
        "double-pendulum source-policy h trio and h_ref=1e-4. Promotion remains open "
        "until the heavy run is executed and independently verified."
    )
    for row in rows:
        h = float(row["h"])
        row.update(
            {
                "policy": config.policy,
                "case_id": "ra2021_double_pendulum_local_fullva_source_policy_candidate",
                "row_type": "source_policy_local_fullva_dynamic_order_candidate",
                "reference_policy": "local_v029_fullva_self_reference_source_policy_h_ref_1e-4",
                "source_policy_time_window": selected and close(t_end, rv.RA2021_PUBLIC_T_END),
                "source_policy_h": selected and any(close(h, policy_h) for policy_h in rv.RA2021_DOUBLE_ORDER_STEP_SIZES),
                "source_policy_reference_h": selected and close(reference_h, rv.RA2021_DOUBLE_ORDER_REFERENCE_H),
                "source_policy_contract_selected": selected,
                "execution_mode": execution_mode,
                "estimated_steps": step_count(t_end, h),
                "reference_cache": str(reference_cache_path(output_stem, reference_h, t_end).name),
                "notes": row_notes,
            }
        )
    return rows, raw_summary


def merge_existing_rows(base_rows: list[dict], existing_rows: list[dict]) -> list[dict]:
    existing_by_h = {float(row["h"]): row for row in existing_rows if row.get("h") not in {None, ""}}
    merged = []
    for base in base_rows:
        h = float(base["h"])
        prior = existing_by_h.get(h)
        if prior and prior.get("status") == "ok":
            merged_row = dict(base)
            merged_row.update(prior)
            merged.append(merged_row)
        else:
            merged.append(base)
    return merged


def update_orders(rows: list[dict], step_sizes: tuple[float, ...]) -> None:
    pos_errors = []
    vel_errors = []
    for h in step_sizes:
        row = next((item for item in rows if close(float(item["h"]), h)), {})
        try:
            pos_errors.append(float(row.get("pos_traj_linf", "nan")))
        except (TypeError, ValueError):
            pos_errors.append(float("nan"))
        try:
            vel_errors.append(float(row.get("vel_traj_linf", "nan")))
        except (TypeError, ValueError):
            vel_errors.append(float("nan"))
    orders = {
        "pos_observed_order": rv.finite_or_none(rv.estimate_order(list(step_sizes), pos_errors)),
        "vel_observed_order": rv.finite_or_none(rv.estimate_order(list(step_sizes), vel_errors)),
    }
    for row in rows:
        for key, value in orders.items():
            row[key] = "nan" if value is None else f"{value:.16e}"


def integrate_reference_checkpointed(
    *,
    cache_path: Path,
    checkpoint_path: Path,
    reference_h: float,
    t_end: float,
    checkpoint_every: int,
    max_reference_steps: int | None,
    force: bool,
    use_jax_safe_small_angle_patch: bool,
) -> tuple[dict | None, float, bool, dict]:
    checkpoint_every = max(1, int(checkpoint_every))
    if cache_path.exists() and not force:
        reference, runtime_sec = load_trajectory(cache_path)
        return reference, runtime_sec, False, {
            "reference_status": "ok",
            "reference_completed": True,
            "reference_checkpoint_exists": checkpoint_path.exists(),
            "reference_checkpoint_step": None,
            "reference_cache_reused": True,
        }
    v047_module = rv.import_v047_single_fullva_module()
    v029 = load_v029_for_candidate(v047_module, use_jax_safe_small_angle_patch)
    params = v047_module.make_asme_double_pendulum_params(v029)

    n_steps = step_count(t_end, reference_h)
    if abs(n_steps * reference_h - t_end) > 1.0e-12:
        raise ValueError("reference_h must divide t_end")
    raw_method = v029.base_method("double_revolute_gauss6_fullva")
    if raw_method != "double_revolute_gauss6":
        raise ValueError(f"unexpected double method {raw_method}")
    mode = v029.residual_mode("double_revolute_gauss6_fullva")
    transform = v047_module.asme_double_world_rotation()

    if checkpoint_path.exists() and not force:
        checkpoint = load_reference_checkpoint(checkpoint_path, v029)
        if not close(checkpoint["h"], reference_h) or not close(checkpoint["t_end"], t_end):
            raise ValueError(f"checkpoint {checkpoint_path.name} does not match selected h/T")
        state = checkpoint["state"]
        pos = checkpoint["pos"]
        vel = checkpoint["vel"]
        current_step = int(checkpoint["current_step"])
        total_iters = int(checkpoint["total_newton_iterations"])
        max_endpoint_constraint = float(checkpoint["max_endpoint_constraint_norm"])
        max_endpoint_velocity_constraint = float(checkpoint["max_endpoint_velocity_constraint_norm"])
        prior_runtime_sec = float(checkpoint["runtime_sec"])
    else:
        state = v047_module.asme_double_pendulum_initial_state(v029, params)
        pos = np.zeros((2, 3, n_steps + 1))
        vel = np.zeros_like(pos)
        current_step = 0
        total_iters = 0
        max_endpoint_constraint = 0.0
        max_endpoint_velocity_constraint = 0.0
        prior_runtime_sec = 0.0

        pos[0, :, 0] = transform @ state.r1
        pos[1, :, 0] = transform @ state.r2
        vel[0, :, 0] = transform @ state.v1
        vel[1, :, 0] = transform @ state.v2

    stop_step = n_steps if max_reference_steps is None else min(n_steps, int(max_reference_steps))
    if stop_step < current_step:
        stop_step = current_step

    started = time.perf_counter()
    for step in range(current_step, stop_step):
        state, niters, diag = v029.gauss_step(state, reference_h, params, 3, mode)
        total_iters += niters
        max_endpoint_constraint = max(max_endpoint_constraint, diag["max_endpoint_constraint_norm"])
        max_endpoint_velocity_constraint = max(
            max_endpoint_velocity_constraint,
            diag["max_endpoint_velocity_constraint_norm"],
        )
        idx = step + 1
        pos[0, :, idx] = transform @ state.r1
        pos[1, :, idx] = transform @ state.r2
        vel[0, :, idx] = transform @ state.v1
        vel[1, :, idx] = transform @ state.v2
        if idx % checkpoint_every == 0 or idx == stop_step:
            save_reference_checkpoint(
                checkpoint_path,
                h=reference_h,
                t_end=t_end,
                current_step=idx,
                pos=pos,
                vel=vel,
                state=state,
                total_iters=total_iters,
                max_endpoint_constraint=max_endpoint_constraint,
                max_endpoint_velocity_constraint=max_endpoint_velocity_constraint,
                runtime_sec=prior_runtime_sec + (time.perf_counter() - started),
            )

    runtime_sec = prior_runtime_sec + (time.perf_counter() - started)
    if stop_step < n_steps:
        return None, runtime_sec, False, {
            "reference_status": "checkpointed",
            "reference_completed": False,
            "reference_checkpoint_exists": checkpoint_path.exists(),
            "reference_checkpoint_step": stop_step,
            "reference_cache_reused": False,
        }

    reference = {
        "h": reference_h,
        "steps": n_steps,
        "pos": pos,
        "vel": vel,
        "total_newton_iterations": total_iters,
        "max_endpoint_constraint_norm": max_endpoint_constraint,
        "max_endpoint_velocity_constraint_norm": max_endpoint_velocity_constraint,
    }
    save_trajectory(cache_path, reference, runtime_sec)
    return reference, runtime_sec, True, {
        "reference_status": "ok",
        "reference_completed": True,
        "reference_checkpoint_exists": checkpoint_path.exists(),
        "reference_checkpoint_step": n_steps,
        "reference_cache_reused": False,
    }


def execute_candidate_row(
    row: dict,
    reference: dict,
    h: float,
    t_end: float,
    *,
    use_jax_safe_small_angle_patch: bool,
) -> dict:
    v047_module = rv.import_v047_single_fullva_module()
    v029 = load_v029_for_candidate(v047_module, use_jax_safe_small_angle_patch)
    params = v047_module.make_asme_double_pendulum_params(v029)
    started = time.perf_counter()
    try:
        candidate = v047_module.integrate_v029_asme_double_trajectory(
            v029,
            "double_revolute_gauss6_fullva",
            h,
            t_end,
            params,
        )
        runtime = time.perf_counter() - started
        err = v047_module.compare_nested_trajectory(reference, candidate)
        accepted_row = (
            candidate["max_endpoint_constraint_norm"] < 1.0e-10
            and candidate["max_endpoint_velocity_constraint_norm"] < 1.0e-10
        )
        row.update(
            {
                "status": "ok",
                "steps": candidate["steps"],
                "pos_traj_linf": f"{err['pos_traj_linf']:.16e}",
                "vel_traj_linf": f"{err['vel_traj_linf']:.16e}",
                "pos_final_linf": f"{err['pos_final_linf']:.16e}",
                "vel_final_linf": f"{err['vel_final_linf']:.16e}",
                "max_endpoint_constraint_norm": f"{candidate['max_endpoint_constraint_norm']:.16e}",
                "max_endpoint_velocity_constraint_norm": f"{candidate['max_endpoint_velocity_constraint_norm']:.16e}",
                "constraint_threshold_satisfied": str(accepted_row),
                "total_newton_iterations": candidate["total_newton_iterations"],
                "runtime_sec": f"{runtime:.16e}",
            }
        )
    except Exception as exc:  # noqa: BLE001 - keep row-level failure in artifact.
        row["status"] = rv.failure_status("failed", exc)
        row["runtime_sec"] = f"{time.perf_counter() - started:.16e}"
    return row


def write_markdown(path: Path, summary: dict) -> None:
    lines = [
        "# RA2021 Double Local Source-Policy Candidate",
        "",
        f"Status: **{summary['status']}**.",
        "",
        "This artifact is isolated from the existing coarse double-pendulum rows.",
        "It does not update the canonical coarse CSV and does not close source-policy rows.",
        "",
        f"- Execution phase: `{summary['execution_phase']}`.",
        f"- Source-policy contract selected: `{summary['source_policy_contract_selected']}`.",
        f"- Step sizes: `{summary['selected_step_sizes']}`.",
        f"- Reference h: `{summary['selected_reference_h']}`.",
        f"- T end: `{summary['selected_t_end']}`.",
        f"- Estimated reference steps: `{summary['estimated_reference_steps']}`.",
        f"- Estimated candidate steps: `{summary['estimated_candidate_steps']}`.",
        f"- Reference cache exists: `{summary['reference_cache_exists']}`.",
        f"- Reference cache: `{summary['reference_cache_path']}`.",
        f"- Reference checkpoint exists: `{summary['reference_checkpoint_exists']}`.",
        f"- Reference checkpoint step: `{summary['reference_checkpoint_step']}`.",
        f"- Reference completed: `{summary['reference_completed']}`.",
        f"- Reference status: `{summary['reference_status']}`.",
        f"- Reference failure kind: `{summary['reference_failure_kind']}`.",
        f"- Reference failure message: `{summary['reference_failure_message']}`.",
        f"- JAX-safe small-angle patch enabled: `{summary['jax_safe_small_angle_patch_enabled']}`.",
        f"- JAX-safe small-angle patch id: `{summary['jax_safe_small_angle_patch_id']}`.",
        f"- Rows completed in this artifact: `{summary['source_policy_candidate_rows_completed']}`.",
        f"- Promotion ready: `{summary['promotion_ready']}`.",
        f"- Canonical coarse output untouched by this writer: `{summary['canonical_coarse_output_untouched_by_writer']}`.",
        "",
        "Required before promotion:",
        "",
        "- execute the exact h_ref=1e-4 reference and three candidate rows",
        "- bind the error norm and output mapping to the RA2021 source policy",
        "- bind runtime and Newton-iteration policy to the accepted rows",
        "- produce an independent rerun or verification artifact",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--step-sizes",
        default=",".join(str(h) for h in rv.RA2021_DOUBLE_ORDER_STEP_SIZES),
    )
    parser.add_argument("--reference-h", type=float, default=rv.RA2021_DOUBLE_ORDER_REFERENCE_H)
    parser.add_argument("--t-end", type=float, default=rv.RA2021_PUBLIC_T_END)
    parser.add_argument("--output-stem", default=STEM)
    parser.add_argument(
        "--phase",
        choices=("plan", "reference", "candidate", "all"),
        default=None,
        help="execution phase; default is plan unless --execute is supplied",
    )
    parser.add_argument(
        "--candidate-h",
        default="",
        help="comma-separated candidate h values for --phase candidate; default runs all planned candidate rows",
    )
    parser.add_argument(
        "--force-reference",
        action="store_true",
        help="recompute the cached reference even if it already exists",
    )
    parser.add_argument(
        "--checkpoint-every",
        type=int,
        default=500,
        help="save reference checkpoint every N steps during --phase reference/all",
    )
    parser.add_argument(
        "--max-reference-steps",
        type=int,
        default=None,
        help="stop reference phase after this many total reference steps; used for bounded smoke/resume runs",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="backward-compatible alias for --phase all",
    )
    parser.add_argument(
        "--allow-source-policy-1e-4",
        action="store_true",
        help="required with --execute because the source-policy reference uses h_ref=1e-4",
    )
    parser.add_argument(
        "--disable-jax-safe-small-angle-patch",
        action="store_true",
        help="diagnostic mode only: use the unpatched historical v013/v029 JAX small-angle helpers",
    )
    args = parser.parse_args()

    step_sizes = tuple(rv.parse_float_csv(args.step_sizes))
    phase = args.phase or ("all" if args.execute else "plan")
    if phase != "plan":
        rv.require_source_policy_1e4_allow(
            parser,
            args.allow_source_policy_1e_4,
            "RA2021 double local FullVA source-policy candidate",
            step_sizes + (float(args.reference_h),),
        )
    if args.force_reference and phase == "plan":
        parser.error("--force-reference requires --phase reference or --phase all")
    use_jax_safe_small_angle_patch = not bool(args.disable_jax_safe_small_angle_patch)

    rv.RESULTS.mkdir(parents=True, exist_ok=True)
    rows_path = rv.RESULTS / f"{args.output_stem}_rows.csv"
    summary_path = rv.RESULTS / f"{args.output_stem}_summary.json"
    md_path = rv.RESULTS / f"{args.output_stem}.md"
    cache_path = reference_cache_path(args.output_stem, float(args.reference_h), float(args.t_end))
    checkpoint_path = reference_checkpoint_path(args.output_stem, float(args.reference_h), float(args.t_end))
    selected = source_policy_selected(step_sizes, float(args.reference_h), float(args.t_end))
    started = time.perf_counter()
    base_rows, raw_summary = make_base_rows(
        step_sizes=step_sizes,
        reference_h=float(args.reference_h),
        t_end=float(args.t_end),
        output_stem=args.output_stem,
        execution_mode=phase,
    )
    existing_rows = read_existing_rows(rows_path)
    rows = merge_existing_rows(base_rows, existing_rows) if rows_match_policy(existing_rows, step_sizes, float(args.reference_h), float(args.t_end)) else base_rows

    reference = None
    reference_runtime_sec = float("nan")
    reference_cache_written_this_run = False
    reference_status = "planned_not_run"
    reference_failure_kind = None
    reference_failure_message = None
    reference_meta = {
        "reference_completed": False,
        "reference_checkpoint_exists": checkpoint_path.exists(),
        "reference_checkpoint_step": None,
        "reference_cache_reused": False,
    }
    if phase in {"reference", "all"}:
        try:
            (
                reference,
                reference_runtime_sec,
                reference_cache_written_this_run,
                reference_meta,
            ) = integrate_reference_checkpointed(
                cache_path=cache_path,
                checkpoint_path=checkpoint_path,
                reference_h=float(args.reference_h),
                t_end=float(args.t_end),
                checkpoint_every=int(args.checkpoint_every),
                max_reference_steps=args.max_reference_steps,
                force=bool(args.force_reference),
                use_jax_safe_small_angle_patch=use_jax_safe_small_angle_patch,
            )
            reference_status = str(reference_meta["reference_status"])
        except Exception as exc:  # noqa: BLE001 - write a reviewable failure artifact.
            reference_runtime_sec = time.perf_counter() - started
            reference_failure_kind = type(exc).__name__
            reference_failure_message = str(exc)
            reference_status = rv.failure_status("reference_failed", exc)
            reference_meta = {
                "reference_status": reference_status,
                "reference_completed": False,
                "reference_checkpoint_exists": checkpoint_path.exists(),
                "reference_checkpoint_step": None,
                "reference_cache_reused": False,
            }
    elif cache_path.exists():
        reference, reference_runtime_sec = load_trajectory(cache_path)
        reference_status = "ok"
        reference_meta = {
            "reference_completed": True,
            "reference_checkpoint_exists": checkpoint_path.exists(),
            "reference_checkpoint_step": None,
            "reference_cache_reused": True,
        }

    for row in rows:
        row.update(
            {
                "reference_status": reference_status,
                "reference_runtime_sec": "nan"
                if not np.isfinite(reference_runtime_sec)
                else f"{reference_runtime_sec:.16e}",
                "execution_mode": phase,
                "jax_safe_small_angle_patch_enabled": str(use_jax_safe_small_angle_patch),
                "jax_safe_small_angle_patch_id": (
                    JAX_SAFE_SMALL_ANGLE_PATCH_ID if use_jax_safe_small_angle_patch else "disabled"
                ),
                "reference_failure_kind": "nan" if reference_failure_kind is None else reference_failure_kind,
                "reference_failure_message": "nan" if reference_failure_message is None else reference_failure_message,
            }
        )

    if phase in {"candidate", "all"}:
        if reference is None:
            if phase == "candidate":
                parser.error(f"--phase {phase} requires reference cache {cache_path.name}; run --phase reference first")
            selected_candidate_h = ()
        else:
            selected_candidate_h = step_sizes if not args.candidate_h else rv.parse_float_csv(args.candidate_h)
        invalid_h = [h for h in selected_candidate_h if not any(close(h, allowed) for allowed in step_sizes)]
        if invalid_h:
            parser.error(f"--candidate-h contains values outside selected step sizes: {invalid_h}")
        for h in selected_candidate_h:
            row = next(item for item in rows if close(float(item["h"]), h))
            if row.get("status") == "ok":
                continue
            assert reference is not None
            execute_candidate_row(
                row,
                reference,
                float(h),
                float(args.t_end),
                use_jax_safe_small_angle_patch=use_jax_safe_small_angle_patch,
            )

    update_orders(rows, step_sizes)
    elapsed = time.perf_counter() - started
    ok_rows = [row for row in rows if row.get("status") == "ok"]
    status = "planned_isolated_source_policy_candidate"
    if cache_path.exists() and not ok_rows:
        status = "reference_cached_isolated_source_policy_candidate"
    elif reference_meta.get("reference_checkpoint_exists") and not ok_rows:
        status = "reference_checkpointed_isolated_source_policy_candidate"
    if str(reference_status).startswith("reference_failed"):
        status = "reference_failed_isolated_source_policy_candidate"
    if ok_rows and len(ok_rows) < len(rows):
        status = "partially_executed_isolated_source_policy_candidate"
    if ok_rows and len(ok_rows) == len(rows):
        status = "executed_isolated_source_policy_candidate"
    try:
        source_policy_pos_observed_order = float(rows[0].get("pos_observed_order", "nan"))
    except (TypeError, ValueError):
        source_policy_pos_observed_order = float("nan")
    try:
        source_policy_vel_observed_order = float(rows[0].get("vel_observed_order", "nan"))
    except (TypeError, ValueError):
        source_policy_vel_observed_order = float("nan")
    source_policy_order_acceptance_threshold = 5.5
    source_policy_order_acceptance_satisfied = (
        np.isfinite(source_policy_pos_observed_order)
        and np.isfinite(source_policy_vel_observed_order)
        and source_policy_pos_observed_order >= source_policy_order_acceptance_threshold
        and source_policy_vel_observed_order >= source_policy_order_acceptance_threshold
    )
    promotion_blockers = [
        "heavy h_ref=1e-4 local FullVA run not completed for all rows"
        if len(ok_rows) < len(rows)
        else "source-policy rows are complete but not yet independently rerun",
        "error norm/output mapping not yet bound to accepted source-policy rows",
        "runtime/Newton-iteration policy not yet tied to accepted source-policy rows",
        "independent rerun or verification artifact not yet produced",
    ]
    if len(ok_rows) == len(rows) and not source_policy_order_acceptance_satisfied:
        promotion_blockers.insert(
            1,
            (
                "observed source-policy order is below sixth-order acceptance "
                f"(pos={source_policy_pos_observed_order:.3f}, vel={source_policy_vel_observed_order:.3f})"
            ),
        )
    summary = {
        "schema": "ra2021-double-local-source-policy-candidate-v1",
        "status": status,
        "policy": "gauss6_fullva_ra2021_double_local_source_policy_candidate",
        "run_mode": "ra2021_double_local_fullva_source_policy_candidate",
        "execution_phase": phase,
        "execution_mode": phase,
        "execute_requested": bool(args.execute or phase != "plan"),
        "heavy_numerical_run_invoked": bool(phase != "plan"),
        "source_policy_contract_selected": selected,
        "source_policy_time_window_selected": close(float(args.t_end), rv.RA2021_PUBLIC_T_END),
        "source_policy_step_trio_selected": list(step_sizes) == list(rv.RA2021_DOUBLE_ORDER_STEP_SIZES),
        "source_policy_reference_h_selected": close(float(args.reference_h), rv.RA2021_DOUBLE_ORDER_REFERENCE_H),
        "selected_step_sizes": list(step_sizes),
        "selected_reference_h": float(args.reference_h),
        "selected_t_end": float(args.t_end),
        "estimated_reference_steps": step_count(float(args.t_end), float(args.reference_h)),
        "estimated_candidate_steps": [step_count(float(args.t_end), h) for h in step_sizes],
        "row_count": len(rows),
        "ok_row_count": len(ok_rows),
        "planned_row_count": sum(1 for row in rows if row.get("status") == "planned_not_run"),
        "source_policy_candidate_rows_completed": len(ok_rows) if selected else 0,
        "source_policy_reproduction_rows_promoted": 0,
        "promotion_ready": False,
        "source_policy_pos_observed_order": source_policy_pos_observed_order,
        "source_policy_vel_observed_order": source_policy_vel_observed_order,
        "source_policy_order_acceptance_threshold": source_policy_order_acceptance_threshold,
        "source_policy_order_acceptance_satisfied": source_policy_order_acceptance_satisfied,
        "promotion_blockers": promotion_blockers,
        "reference_cache_path": str(cache_path.name),
        "reference_checkpoint_path": str(checkpoint_path.name),
        "reference_cache_exists": cache_path.exists(),
        "reference_checkpoint_exists": checkpoint_path.exists(),
        "reference_checkpoint_step": reference_meta.get("reference_checkpoint_step"),
        "reference_completed": reference_meta.get("reference_completed"),
        "reference_cache_reused": reference_meta.get("reference_cache_reused"),
        "reference_cache_written_this_run": reference_cache_written_this_run,
        "reference_status": reference_status,
        "reference_failure_kind": reference_failure_kind,
        "reference_failure_message": reference_failure_message,
        "reference_runtime_sec": reference_runtime_sec,
        "jax_safe_small_angle_patch_enabled": use_jax_safe_small_angle_patch,
        "jax_safe_small_angle_patch_id": (
            JAX_SAFE_SMALL_ANGLE_PATCH_ID if use_jax_safe_small_angle_patch else "disabled"
        ),
        "jax_safe_small_angle_patch_scope": "isolated_runtime_loaded_v029_module_only",
        "canonical_coarse_output": "gauss6_fullva_public_horizon_double_coarse_rows.csv",
        "isolated_rows_output": f"{args.output_stem}_rows.csv",
        "isolated_summary_output": f"{args.output_stem}_summary.json",
        "isolated_markdown_output": f"{args.output_stem}.md",
        "canonical_coarse_output_untouched_by_writer": True,
        "raw_runner_summary": raw_summary,
        "elapsed_sec": elapsed,
    }

    rv.write_csv(rows_path, rows)
    rv.write_json_atomic(summary_path, summary)
    write_markdown(md_path, summary)

    print(
        "ra2021_double_local_source_policy_candidate=ok "
        f"phase={phase} rows={summary['ok_row_count']}/{summary['row_count']} "
        f"reference_cache_exists={summary['reference_cache_exists']} "
        f"source_policy_contract_selected={summary['source_policy_contract_selected']}"
    )


if __name__ == "__main__":
    main()
