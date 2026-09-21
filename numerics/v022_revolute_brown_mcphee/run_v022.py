from __future__ import annotations

import csv
import json
import os
import platform
import time
from dataclasses import dataclass
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")
os.environ.setdefault("MPLCONFIGDIR", "/tmp/mplconfig")

import jax

jax.config.update("jax_enable_x64", True)
import jax.numpy as jnp
import numpy as np


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"

CASES = {"revolute_bm_smooth": 0.50, "revolute_bm_sharp": 0.05}
HS = [0.05, 0.025, 0.0125, 0.00625]
FIXED_METHODS = ["gauss4", "gauss6"]
TOLERANCES = [1.0e-5, 1.0e-6, 1.0e-7, 1.0e-8]
T_FINAL = 1.0
REF_H = 0.0015625
H_INITIAL = 0.1
H_MAX = 0.1
H_MIN = 1.0e-5
SAFETY = 0.85


@dataclass(frozen=True)
class Params:
    mass: float
    length: float
    inertia_about_joint: float
    gravity: float
    mu_s: float
    mu_d: float
    stribeck_velocity: float
    viscous_damping: float
    friction_radius: float


@dataclass
class State:
    q: float
    v: float


def make_params(stribeck_velocity: float) -> Params:
    mass = 4.0
    length = 0.75
    return Params(
        mass=mass,
        length=length,
        inertia_about_joint=0.32 + mass * length * length,
        gravity=9.81,
        mu_s=0.30,
        mu_d=0.20,
        stribeck_velocity=float(stribeck_velocity),
        viscous_damping=0.02,
        friction_radius=0.08,
    )


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def json_safe(obj: object) -> object:
    if isinstance(obj, dict):
        return {key: json_safe(value) for key, value in obj.items()}
    if isinstance(obj, list):
        return [json_safe(value) for value in obj]
    if isinstance(obj, tuple):
        return [json_safe(value) for value in obj]
    if isinstance(obj, float) and not np.isfinite(obj):
        return None
    return obj


def angle_error(q_ref: float, q: float) -> float:
    return float(abs(np.arctan2(np.sin(q - q_ref), np.cos(q - q_ref))))


def estimate_order(hs: list[float], errors: list[float]) -> float:
    xs = np.log(np.asarray(hs, dtype=float))
    ys = np.log(np.maximum(np.asarray(errors, dtype=float), 1.0e-300))
    slope, _ = np.polyfit(xs, ys, 1)
    return float(slope)


def quat_from_revolute_angle(q: float) -> np.ndarray:
    half = 0.5 * q
    return np.array([np.cos(half), 0.0, np.sin(half), 0.0], dtype=float)


def pivot_reaction(q: float, v: float, alpha: float, params: Params) -> np.ndarray:
    length = params.length
    xdd = length * np.sin(q) * v * v - length * np.cos(q) * alpha
    zdd = length * np.cos(q) * v * v + length * np.sin(q) * alpha
    return params.mass * np.array([xdd, 0.0, zdd + params.gravity], dtype=float)


def brown_mcphee_torque(v: float, normal_load: float, params: Params) -> float:
    vs = max(params.stribeck_velocity, 1.0e-12)
    z = v / vs
    denom = (0.25 * z * z + 0.75) ** 2
    coulomb_stiction = params.mu_d * np.tanh(4.0 * z) + (params.mu_s - params.mu_d) * z / denom
    return -params.friction_radius * normal_load * coulomb_stiction - params.viscous_damping * np.tanh(4.0) * v


def stage_power(q: float, v: float, alpha: float, params: Params) -> float:
    normal = float(np.linalg.norm(pivot_reaction(q, v, alpha, params)))
    return float(brown_mcphee_torque(v, normal, params) * v)


def energy(state: State, params: Params) -> float:
    return 0.5 * params.inertia_about_joint * state.v * state.v - params.mass * params.gravity * params.length * np.cos(
        state.q
    )


def acceleration_initial_guess(q: float, v: float, params: Params) -> float:
    tau_g = -params.mass * params.gravity * params.length * np.sin(q)
    alpha = tau_g / params.inertia_about_joint
    for _ in range(8):
        normal = float(np.linalg.norm(pivot_reaction(q, v, alpha, params)))
        tau_f = brown_mcphee_torque(v, normal, params)
        next_alpha = (tau_g + tau_f) / params.inertia_about_joint
        if abs(next_alpha - alpha) < 1.0e-13:
            return float(next_alpha)
        alpha = next_alpha
    return float(alpha)


def gauss_legendre_coefficients(n_stages: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    if n_stages == 2:
        root3 = np.sqrt(3.0)
        c = np.array([0.5 - root3 / 6.0, 0.5 + root3 / 6.0])
        A = np.array([[0.25, 0.25 - root3 / 6.0], [0.25 + root3 / 6.0, 0.25]])
        b = np.array([0.5, 0.5])
        return c, A, b
    if n_stages == 3:
        root15 = np.sqrt(15.0)
        c = np.array([0.5 - root15 / 10.0, 0.5, 0.5 + root15 / 10.0])
        A = np.array(
            [
                [5.0 / 36.0, 2.0 / 9.0 - root15 / 15.0, 5.0 / 36.0 - root15 / 30.0],
                [5.0 / 36.0 + root15 / 24.0, 2.0 / 9.0, 5.0 / 36.0 - root15 / 24.0],
                [5.0 / 36.0 + root15 / 30.0, 2.0 / 9.0 + root15 / 15.0, 5.0 / 36.0],
            ]
        )
        b = np.array([5.0 / 18.0, 4.0 / 9.0, 5.0 / 18.0])
        return c, A, b
    raise ValueError(f"unsupported stage count {n_stages}")


def gauss_legendre_coefficients_jax(n_stages: int, dtype) -> tuple[object, object, object]:
    c, A, b = gauss_legendre_coefficients(n_stages)
    return jnp.asarray(c, dtype=dtype), jnp.asarray(A, dtype=dtype), jnp.asarray(b, dtype=dtype)


def pivot_reaction_jax(q, v, alpha, mass, length, gravity):
    xdd = length * jnp.sin(q) * v * v - length * jnp.cos(q) * alpha
    zdd = length * jnp.cos(q) * v * v + length * jnp.sin(q) * alpha
    return mass * jnp.array([xdd, 0.0, zdd + gravity], dtype=q.dtype)


def brown_mcphee_torque_jax(v, normal_load, mu_s, mu_d, stribeck_velocity, viscous_damping, friction_radius):
    vs = jnp.maximum(stribeck_velocity, 1.0e-12)
    z = v / vs
    denom = (0.25 * z * z + 0.75) ** 2
    coulomb_stiction = mu_d * jnp.tanh(4.0 * z) + (mu_s - mu_d) * z / denom
    return -friction_radius * normal_load * coulomb_stiction - viscous_damping * jnp.tanh(
        jnp.array(4.0, dtype=v.dtype)
    ) * v


def unpack_stages(x, n_stages: int):
    return [{"q": x[3 * i], "v": x[3 * i + 1], "a": x[3 * i + 2]} for i in range(n_stages)]


def residual_core(
    x,
    q0,
    v0,
    h,
    mass,
    length,
    inertia,
    gravity,
    mu_s,
    mu_d,
    stribeck_velocity,
    viscous_damping,
    friction_radius,
    n_stages: int,
):
    _, A, _ = gauss_legendre_coefficients_jax(n_stages, x.dtype)
    stages = unpack_stages(x, n_stages)
    out = []
    for i, stage in enumerate(stages):
        q_coll = stage["q"] - q0 - h * sum(A[i, j] * stages[j]["v"] for j in range(n_stages))
        v_coll = stage["v"] - v0 - h * sum(A[i, j] * stages[j]["a"] for j in range(n_stages))
        reaction = pivot_reaction_jax(stage["q"], stage["v"], stage["a"], mass, length, gravity)
        normal_load = jnp.linalg.norm(reaction)
        tau_g = -mass * gravity * length * jnp.sin(stage["q"])
        tau_f = brown_mcphee_torque_jax(
            stage["v"], normal_load, mu_s, mu_d, stribeck_velocity, viscous_damping, friction_radius
        )
        dyn = inertia * stage["a"] - tau_g - tau_f
        out.extend([q_coll, v_coll, dyn])
    return jnp.asarray(out, dtype=x.dtype)


def residual2_core(x, *args):
    return residual_core(x, *args, n_stages=2)


def residual3_core(x, *args):
    return residual_core(x, *args, n_stages=3)


residual2_value = jax.jit(residual2_core)
residual2_jacobian = jax.jit(jax.jacfwd(residual2_core, argnums=0))
residual3_value = jax.jit(residual3_core)
residual3_jacobian = jax.jit(jax.jacfwd(residual3_core, argnums=0))


def stage_guess(state: State, h: float, params: Params, n_stages: int) -> np.ndarray:
    c, _, _ = gauss_legendre_coefficients(n_stages)
    alpha0 = acceleration_initial_guess(state.q, state.v, params)
    blocks = []
    for ci in c:
        q_i = state.q + ci * h * state.v
        v_i = state.v + ci * h * alpha0
        a_i = acceleration_initial_guess(q_i, v_i, params)
        blocks.extend([q_i, v_i, a_i])
    return np.asarray(blocks, dtype=float)


def gauss_step(state: State, h: float, params: Params, n_stages: int) -> tuple[State, int, dict]:
    _, _, b = gauss_legendre_coefficients(n_stages)
    x = stage_guess(state, h, params, n_stages)
    args = (
        jnp.asarray(state.q, dtype=jnp.float64),
        jnp.asarray(state.v, dtype=jnp.float64),
        jnp.asarray(h, dtype=jnp.float64),
        jnp.asarray(params.mass, dtype=jnp.float64),
        jnp.asarray(params.length, dtype=jnp.float64),
        jnp.asarray(params.inertia_about_joint, dtype=jnp.float64),
        jnp.asarray(params.gravity, dtype=jnp.float64),
        jnp.asarray(params.mu_s, dtype=jnp.float64),
        jnp.asarray(params.mu_d, dtype=jnp.float64),
        jnp.asarray(params.stribeck_velocity, dtype=jnp.float64),
        jnp.asarray(params.viscous_damping, dtype=jnp.float64),
        jnp.asarray(params.friction_radius, dtype=jnp.float64),
    )
    if n_stages == 2:
        value, jacobian, max_iters = residual2_value, residual2_jacobian, 12
    elif n_stages == 3:
        value, jacobian, max_iters = residual3_value, residual3_jacobian, 16
    else:
        raise ValueError(f"unsupported stage count {n_stages}")
    last_norm = np.inf
    for it in range(max_iters):
        x_jax = jnp.asarray(x, dtype=jnp.float64)
        res = np.asarray(value(x_jax, *args), dtype=float)
        last_norm = float(np.linalg.norm(res))
        if last_norm < 1.0e-12:
            break
        jac = np.asarray(jacobian(x_jax, *args), dtype=float)
        delta = np.linalg.solve(jac, -res)
        x = x + delta
        if float(np.linalg.norm(delta)) < 1.0e-12:
            break
    else:
        raise RuntimeError(f"revolute Brown-McPhee Gauss solve failed, residual={last_norm:.3e}")

    stages = [{"q": x[3 * i], "v": x[3 * i + 1], "a": x[3 * i + 2]} for i in range(n_stages)]
    q_next = state.q + h * sum(b[i] * stages[i]["v"] for i in range(n_stages))
    v_next = state.v + h * sum(b[i] * stages[i]["a"] for i in range(n_stages))
    powers = [stage_power(stage["q"], stage["v"], stage["a"], params) for stage in stages]
    reactions = [np.linalg.norm(pivot_reaction(stage["q"], stage["v"], stage["a"], params)) for stage in stages]
    diag = {
        "newton_iterations": it + 1,
        "stage_residual_norm": last_norm,
        "min_stage_friction_power": float(np.min(powers)),
        "max_stage_friction_power": float(np.max(powers)),
        "max_reaction_norm": float(np.max(reactions)),
        "max_quaternion_unit_error": float(abs(np.linalg.norm(quat_from_revolute_angle(q_next)) - 1.0)),
    }
    return State(q=float(q_next), v=float(v_next)), it + 1, diag


def initial_state() -> State:
    return State(q=0.95, v=0.0)


def integrate(method: str, h: float, t_final: float, params: Params) -> dict:
    n_steps = int(round(t_final / h))
    if abs(n_steps * h - t_final) > 1.0e-12:
        raise ValueError("h must divide t_final")
    n_stages = 2 if method == "gauss4" else 3
    state = initial_state()
    E0 = energy(state, params)
    prev_energy = E0
    total_iters = 0
    max_step_energy_increase = 0.0
    max_power = -np.inf
    min_power = np.inf
    max_reaction = 0.0
    max_quat_unit = float(abs(np.linalg.norm(quat_from_revolute_angle(state.q)) - 1.0))
    for _ in range(n_steps):
        state, niters, diag = gauss_step(state, h, params, n_stages)
        total_iters += niters
        max_power = max(max_power, diag["max_stage_friction_power"])
        min_power = min(min_power, diag["min_stage_friction_power"])
        max_reaction = max(max_reaction, diag["max_reaction_norm"])
        max_quat_unit = max(max_quat_unit, diag["max_quaternion_unit_error"])
        E = energy(state, params)
        max_step_energy_increase = max(max_step_energy_increase, E - prev_energy)
        prev_energy = E
    final_energy = energy(state, params)
    return {
        "state": state,
        "steps": n_steps,
        "total_newton_iterations": total_iters,
        "final_energy_change": final_energy - E0,
        "final_energy_relative_change": (final_energy - E0) / max(abs(E0), 1.0e-30),
        "max_step_energy_increase": max_step_energy_increase,
        "max_stage_friction_power": max_power,
        "min_stage_friction_power": min_power,
        "max_reaction_norm": max_reaction,
        "max_quaternion_unit_error": max_quat_unit,
    }


def state_error(ref: State, state: State) -> tuple[float, float]:
    return angle_error(ref.q, state.q), abs(ref.v - state.v)


def embedded_error(state4: State, state6: State, q_tol: float, v_tol: float) -> tuple[float, float, float]:
    q_diff = angle_error(state6.q, state4.q)
    v_diff = abs(state6.v - state4.v)
    return max(q_diff / q_tol, v_diff / v_tol), q_diff, v_diff


def next_step_size(h: float, err_norm: float, accepted: bool) -> float:
    if err_norm <= 1.0e-14:
        factor = 2.0
    else:
        factor = SAFETY * err_norm ** (-0.2)
    if accepted:
        factor = min(2.0, max(0.35, factor))
    else:
        factor = min(0.8, max(0.1, factor))
    return min(H_MAX, max(H_MIN, h * factor))


def adaptive_integrate(params: Params, q_tol: float, v_tol: float) -> dict:
    state = initial_state()
    h = H_INITIAL
    t = 0.0
    E0 = energy(state, params)
    prev_energy = E0
    accepted = 0
    rejected = 0
    total_iters4 = 0
    total_iters6 = 0
    h_values = []
    err_values = []
    max_q_diff = 0.0
    max_v_diff = 0.0
    max_power = -np.inf
    min_power = np.inf
    max_reaction = 0.0
    max_step_energy_increase = 0.0
    max_quat_unit = float(abs(np.linalg.norm(quat_from_revolute_angle(state.q)) - 1.0))
    while t < T_FINAL - 1.0e-14:
        h = min(h, T_FINAL - t)
        try:
            state6, n6, diag6 = gauss_step(state, h, params, n_stages=3)
            state4, n4, _diag4 = gauss_step(state, h, params, n_stages=2)
        except RuntimeError:
            rejected += 1
            h = max(H_MIN, 0.5 * h)
            continue
        total_iters6 += n6
        total_iters4 += n4
        err_norm, q_diff, v_diff = embedded_error(state4, state6, q_tol, v_tol)
        if err_norm <= 1.0 or h <= H_MIN * (1.0 + 1.0e-12):
            state = state6
            t += h
            accepted += 1
            h_values.append(h)
            err_values.append(err_norm)
            max_q_diff = max(max_q_diff, q_diff)
            max_v_diff = max(max_v_diff, v_diff)
            max_power = max(max_power, diag6["max_stage_friction_power"])
            min_power = min(min_power, diag6["min_stage_friction_power"])
            max_reaction = max(max_reaction, diag6["max_reaction_norm"])
            max_quat_unit = max(max_quat_unit, diag6["max_quaternion_unit_error"])
            E = energy(state, params)
            max_step_energy_increase = max(max_step_energy_increase, E - prev_energy)
            prev_energy = E
            h = next_step_size(h, err_norm, accepted=True)
        else:
            rejected += 1
            h = next_step_size(h, err_norm, accepted=False)
    final_energy = energy(state, params)
    return {
        "state": state,
        "accepted_steps": accepted,
        "rejected_steps": rejected,
        "total_steps_attempted": accepted + rejected,
        "total_newton_iterations": total_iters4 + total_iters6,
        "total_gauss4_newton_iterations": total_iters4,
        "total_gauss6_newton_iterations": total_iters6,
        "min_h": float(np.min(h_values)) if h_values else float("nan"),
        "max_h": float(np.max(h_values)) if h_values else float("nan"),
        "mean_h": float(np.mean(h_values)) if h_values else float("nan"),
        "max_embedded_error_norm": float(np.max(err_values)) if err_values else float("nan"),
        "max_embedded_angle_diff": max_q_diff,
        "max_embedded_velocity_diff": max_v_diff,
        "final_energy_change": final_energy - E0,
        "final_energy_relative_change": (final_energy - E0) / max(abs(E0), 1.0e-30),
        "max_step_energy_increase": max_step_energy_increase,
        "max_stage_friction_power": max_power,
        "min_stage_friction_power": min_power,
        "max_reaction_norm": max_reaction,
        "max_quaternion_unit_error": max_quat_unit,
    }


def fixed_run(case_name: str, method: str, h: float, params: Params, ref_state: State) -> tuple[dict, dict]:
    start = time.perf_counter()
    out = integrate(method, h, T_FINAL, params)
    runtime = time.perf_counter() - start
    q_err, v_err = state_error(ref_state, out["state"])
    row = {
        "case": case_name,
        "run_type": "fixed",
        "label": f"{method}_fixed_h{str(h).replace('.', '')}",
        "method": method,
        "tolerance": "",
        "h": f"{h:.10g}",
        "steps": out["steps"],
        "accepted_steps": out["steps"],
        "rejected_steps": 0,
        "angle_error_rad": f"{q_err:.16e}",
        "velocity_error": f"{v_err:.16e}",
        "runtime_sec": f"{runtime:.8e}",
        "total_newton_iterations": out["total_newton_iterations"],
        "min_h": f"{h:.16e}",
        "max_h": f"{h:.16e}",
        "mean_h": f"{h:.16e}",
        "max_reaction_norm": f"{out['max_reaction_norm']:.16e}",
        "max_stage_friction_power": f"{out['max_stage_friction_power']:.16e}",
        "final_energy_relative_change": f"{out['final_energy_relative_change']:.16e}",
        "max_step_energy_increase": f"{out['max_step_energy_increase']:.16e}",
        "max_quaternion_unit_error": f"{out['max_quaternion_unit_error']:.16e}",
    }
    summary = dict(out)
    summary.pop("state")
    summary.update(
        {
            "label": row["label"],
            "method": method,
            "h": h,
            "angle_error_rad": q_err,
            "velocity_error": v_err,
            "runtime_sec": runtime,
        }
    )
    return row, summary


def adaptive_run(case_name: str, tol: float, params: Params, ref_state: State) -> tuple[dict, dict]:
    start = time.perf_counter()
    out = adaptive_integrate(params, q_tol=tol, v_tol=tol)
    runtime = time.perf_counter() - start
    q_err, v_err = state_error(ref_state, out["state"])
    row = {
        "case": case_name,
        "run_type": "adaptive",
        "label": f"adaptive_revolute_bm_gauss64_tol{tol:.0e}",
        "method": "adaptive_revolute_bm_gauss64",
        "tolerance": f"{tol:.1e}",
        "h": "",
        "steps": out["accepted_steps"],
        "accepted_steps": out["accepted_steps"],
        "rejected_steps": out["rejected_steps"],
        "angle_error_rad": f"{q_err:.16e}",
        "velocity_error": f"{v_err:.16e}",
        "runtime_sec": f"{runtime:.8e}",
        "total_newton_iterations": out["total_newton_iterations"],
        "min_h": f"{out['min_h']:.16e}",
        "max_h": f"{out['max_h']:.16e}",
        "mean_h": f"{out['mean_h']:.16e}",
        "max_reaction_norm": f"{out['max_reaction_norm']:.16e}",
        "max_stage_friction_power": f"{out['max_stage_friction_power']:.16e}",
        "final_energy_relative_change": f"{out['final_energy_relative_change']:.16e}",
        "max_step_energy_increase": f"{out['max_step_energy_increase']:.16e}",
        "max_quaternion_unit_error": f"{out['max_quaternion_unit_error']:.16e}",
    }
    summary = dict(out)
    summary.pop("state")
    summary.update(
        {
            "label": row["label"],
            "method": row["method"],
            "tolerance": tol,
            "angle_error_rad": q_err,
            "velocity_error": v_err,
            "runtime_sec": runtime,
        }
    )
    return row, summary


def warm_jax(params: Params) -> None:
    state = initial_state()
    gauss_step(state, 0.025, params, 2)
    gauss_step(state, 0.025, params, 3)


def run_experiment() -> dict:
    rows = []
    cases = {}
    for case_name, vs in CASES.items():
        params = make_params(vs)
        ref = integrate("gauss6", REF_H, T_FINAL, params)
        ref_state = ref["state"]
        warm_jax(params)
        fixed_summaries = []
        adaptive_summaries = []
        for method in FIXED_METHODS:
            for h in HS:
                row, summary = fixed_run(case_name, method, h, params, ref_state)
                rows.append(row)
                fixed_summaries.append(summary)
        for tol in TOLERANCES:
            row, summary = adaptive_run(case_name, tol, params, ref_state)
            rows.append(row)
            adaptive_summaries.append(summary)
        fixed_orders = {}
        for method in FIXED_METHODS:
            method_runs = sorted([item for item in fixed_summaries if item["method"] == method], key=lambda item: item["h"], reverse=True)
            fixed_orders[method] = {
                "angle_observed_order": estimate_order(
                    [item["h"] for item in method_runs], [item["angle_error_rad"] for item in method_runs]
                ),
                "velocity_observed_order": estimate_order(
                    [item["h"] for item in method_runs], [item["velocity_error"] for item in method_runs]
                ),
            }
        baseline = next(item for item in fixed_summaries if item["method"] == "gauss6" and abs(item["h"] - 0.025) < 1e-15)
        fine = next(item for item in fixed_summaries if item["method"] == "gauss6" and abs(item["h"] - 0.0125) < 1e-15)
        finest = next(item for item in fixed_summaries if item["method"] == "gauss6" and abs(item["h"] - 0.00625) < 1e-15)
        best_adaptive = min(adaptive_summaries, key=lambda item: item["angle_error_rad"])
        fastest_better = [
            item
            for item in adaptive_summaries
            if item["angle_error_rad"] < baseline["angle_error_rad"] and item["runtime_sec"] <= 1.25 * baseline["runtime_sec"]
        ]
        cases[case_name] = {
            "stribeck_velocity": vs,
            "reference_method": "gauss6",
            "reference_h": REF_H,
            "fixed": fixed_summaries,
            "adaptive": adaptive_summaries,
            "fixed_orders": fixed_orders,
            "gauss6_h0025_baseline": baseline,
            "gauss6_h00125_fine": fine,
            "gauss6_h000625_finest": finest,
            "best_adaptive": best_adaptive,
            "fastest_adaptive_better_than_gauss6_h0025": min(fastest_better, key=lambda item: item["runtime_sec"])
            if fastest_better
            else None,
            "reference": {key: value for key, value in ref.items() if key != "state"},
        }
    write_csv(RESULTS / "revolute_brown_mcphee_runs.csv", rows)
    return {"t_final": T_FINAL, "cases": cases, "tolerances": TOLERANCES}


def plot_results(summary: dict) -> None:
    import matplotlib.pyplot as plt

    plt.figure(figsize=(8.0, 4.8))
    markers = {"fixed": "o", "adaptive": "s"}
    for case_name, case in summary["cases"].items():
        for group_name in ["fixed", "adaptive"]:
            group = case[group_name]
            xs = [item["runtime_sec"] for item in group]
            ys = [item["angle_error_rad"] for item in group]
            labels = [item["label"] for item in group]
            plt.loglog(xs, ys, marker=markers[group_name], linestyle="none", label=f"{case_name} {group_name}")
            for x, y, label in zip(xs, ys, labels):
                short = label.replace("adaptive_revolute_bm_gauss64_", "adap_").replace("gauss6_fixed_", "g6_")
                short = short.replace("gauss4_fixed_", "g4_")
                plt.annotate(short, (x, y), fontsize=7, xytext=(3, 3), textcoords="offset points")
    plt.xlabel("runtime seconds")
    plt.ylabel("angle/orientation error rad")
    plt.title("Revolute Brown-McPhee Benchmark")
    plt.grid(True, which="both", alpha=0.35)
    plt.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(RESULTS / "revolute_brown_mcphee_error_runtime.png", dpi=180)
    plt.close()


def write_report(summary: dict) -> None:
    lines = [
        "# v022 Experiment Report",
        "",
        "Generated by `run_v022.py`.",
        "",
        "## Purpose",
        "",
        "- Move from the v021 fixed-pivot surrogate to a paper-like one-DOF revolute pendulum with Brown-McPhee continuous velocity friction.",
        "- Keep quaternion/Lie output through `p(q)=exp(e_y q / 2)` and compare Gauss4, Gauss6, and embedded adaptive Gauss64.",
        "- Let the friction torque depend on pivot reaction load, which depends on stage acceleration, so the Newton residual still includes friction/reaction coupling.",
        "",
        "## Results",
        "",
    ]
    for case_name, case in summary["cases"].items():
        g4_order = case["fixed_orders"]["gauss4"]
        g6_order = case["fixed_orders"]["gauss6"]
        baseline = case["gauss6_h0025_baseline"]
        fine = case["gauss6_h00125_fine"]
        finest = case["gauss6_h000625_finest"]
        best = case["best_adaptive"]
        fastest = case["fastest_adaptive_better_than_gauss6_h0025"]
        error_ratio_vs_baseline = best["angle_error_rad"] / baseline["angle_error_rad"]
        runtime_ratio_vs_baseline = best["runtime_sec"] / baseline["runtime_sec"]
        error_ratio_vs_fine = best["angle_error_rad"] / fine["angle_error_rad"]
        runtime_ratio_vs_fine = best["runtime_sec"] / fine["runtime_sec"]
        error_ratio_vs_finest = best["angle_error_rad"] / finest["angle_error_rad"]
        runtime_ratio_vs_finest = best["runtime_sec"] / finest["runtime_sec"]
        value_vs_fine = (fine["angle_error_rad"] / best["angle_error_rad"]) / max(
            best["runtime_sec"] / fine["runtime_sec"], 1.0e-30
        )
        value_vs_finest = (finest["angle_error_rad"] / best["angle_error_rad"]) / max(
            best["runtime_sec"] / finest["runtime_sec"], 1.0e-30
        )
        lines.append(
            f"- `{case_name}` fixed-step observed angle order: Gauss4 {g4_order['angle_observed_order']:.3f}, "
            f"Gauss6 {g6_order['angle_observed_order']:.3f}."
        )
        lines.append(
            f"- `{case_name}` Gauss6 h=0.025: error {baseline['angle_error_rad']:.3e}, "
            f"runtime {baseline['runtime_sec']:.3f}s."
        )
        lines.append(
            f"- `{case_name}` Gauss6 h=0.0125: error {fine['angle_error_rad']:.3e}, "
            f"runtime {fine['runtime_sec']:.3f}s."
        )
        lines.append(
            f"- `{case_name}` Gauss6 h=0.00625: error {finest['angle_error_rad']:.3e}, "
            f"runtime {finest['runtime_sec']:.3f}s."
        )
        lines.append(
            f"- `{case_name}` best adaptive `{best['label']}`: error {best['angle_error_rad']:.3e}, "
            f"runtime {best['runtime_sec']:.3f}s, accepted/rejected {best['accepted_steps']}/{best['rejected_steps']}, "
            f"h range [{best['min_h']:.3e}, {best['max_h']:.3e}]."
        )
        lines.append(
            f"- `{case_name}` best adaptive ratios: error/runtime vs Gauss6 h=0.025 = "
            f"{error_ratio_vs_baseline:.2e}/{runtime_ratio_vs_baseline:.2e}; "
            f"error/runtime vs Gauss6 h=0.0125 = {error_ratio_vs_fine:.2e}/{runtime_ratio_vs_fine:.2e}; "
            f"error/runtime vs Gauss6 h=0.00625 = {error_ratio_vs_finest:.2e}/{runtime_ratio_vs_finest:.2e}."
        )
        lines.append(
            f"- `{case_name}` adaptive value ratios: vs h=0.0125 = {value_vs_fine:.2e}, "
            f"vs h=0.00625 = {value_vs_finest:.2e}."
        )
        if fastest is None:
            lines.append(f"- `{case_name}` no adaptive tolerance beat Gauss6 h=0.025 within 1.25x runtime.")
        else:
            lines.append(
                f"- `{case_name}` fastest adaptive better than Gauss6 h=0.025 within 1.25x runtime: "
                f"`{fastest['label']}` with error {fastest['angle_error_rad']:.3e} and runtime "
                f"{fastest['runtime_sec']:.3f}s."
            )
        if error_ratio_vs_finest < 0.8 and value_vs_finest > 1.0:
            lines.append(
                f"- `{case_name}` conclusion: adaptive is a high-accuracy accuracy-per-cost win over the finest fixed Gauss6 run."
            )
        elif 0.8 <= error_ratio_vs_finest <= 1.25 and 0.8 <= runtime_ratio_vs_finest <= 1.25:
            lines.append(
                f"- `{case_name}` conclusion: adaptive and fixed Gauss6 h=0.00625 are essentially tied; fixed Gauss6 is the cleaner default."
            )
        elif error_ratio_vs_baseline < 1.0:
            lines.append(
                f"- `{case_name}` conclusion: adaptive improves the coarse step, but finer fixed Gauss6 remains the stronger high-accuracy reference."
            )
        else:
            lines.append(f"- `{case_name}` conclusion: fixed Gauss6 is the better default.")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- This benchmark is not a full index-3 absolute-coordinate revolute DAE, but it is closer to the paper's revolute-pendulum friction setting than the fixed-pivot componentwise surrogate.",
            "- The scalar revolute coordinate removes irrelevant 3D rotational freedoms while preserving the Lie/quaternion attitude output and the reaction-load dependent Brown-McPhee friction coupling.",
            "- The main question is whether the v021 conclusion survives on a paper-like revolute benchmark: fixed Gauss6 for smooth friction and targeted adaptivity for sharp friction.",
            "- Friction power and step energy changes are recorded in the CSV; all accepted runs should have nonpositive stage friction power up to roundoff.",
            "",
            "## Outputs",
            "",
            "- `revolute_brown_mcphee_runs.csv`",
            "- `summary_v022.json`",
            "- `revolute_brown_mcphee_error_runtime.png`",
            "",
        ]
    )
    (RESULTS / "v022_report.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    experiment = run_experiment()
    plot_results(experiment)
    summary = {
        "version": "v022_revolute_brown_mcphee",
        "python": platform.python_version(),
        "platform": platform.platform(),
        "numpy": np.__version__,
        "jax": jax.__version__,
        "model": {
            "cases": CASES,
            "step_sizes": HS,
            "tolerances": TOLERANCES,
            "reference_h": REF_H,
            "t_final": T_FINAL,
            "h_initial": H_INITIAL,
            "h_max": H_MAX,
            "h_min": H_MIN,
            "friction_curve": "Brown-McPhee continuous velocity curve with reaction-load scaling",
        },
        "experiment": experiment,
        "runtime_sec": time.perf_counter() - started,
    }
    with (RESULTS / "summary_v022.json").open("w", encoding="utf-8") as f:
        json.dump(json_safe(summary), f, indent=2, sort_keys=True)
    write_report(experiment)


if __name__ == "__main__":
    main()
