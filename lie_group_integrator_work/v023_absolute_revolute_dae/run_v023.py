from __future__ import annotations

import csv
import importlib.util
import json
import os
import platform
import sys
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
ROOT = HERE.parent
RESULTS = HERE / "results"
QP_PATH = ROOT / "v013_gauss6_quaternion_endpoint_dae" / "quaternion_pendulum.py"

CASES = {"absolute_revolute_smooth": 0.50, "absolute_revolute_sharp": 0.05}
HS = [0.05, 0.025, 0.0125]
METHODS = ["abs_revolute_gauss4", "abs_revolute_gauss6"]
T_FINAL = 1.0
REF_H = 0.00625
CSV_COLUMNS = [
    "case",
    "method",
    "h",
    "status",
    "error_message",
    "steps",
    "orientation_error_rad",
    "omega_l2_error",
    "runtime_sec",
    "total_newton_iterations",
    "max_endpoint_constraint_norm",
    "max_endpoint_velocity_constraint_norm",
    "max_stage_constraint_norm",
    "max_stage_velocity_constraint_norm",
    "max_lambda_norm",
    "max_stage_friction_power",
    "final_energy_relative_change",
    "max_step_energy_increase",
    "max_quaternion_unit_error",
]


def load_qp_module():
    spec = importlib.util.spec_from_file_location("v013_quaternion_pendulum", QP_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


qp = load_qp_module()


@dataclass(frozen=True)
class Params:
    mass: float
    J_com: np.ndarray
    s_com_to_pivot: np.ndarray
    gravity: np.ndarray
    hinge_axis_body: np.ndarray
    hinge_axis_world: np.ndarray
    mu_s: float
    mu_d: float
    stribeck_velocity: float
    viscous_damping: float
    friction_radius: float


@dataclass
class State:
    r: np.ndarray
    p: np.ndarray
    v: np.ndarray
    w: np.ndarray


def make_params(stribeck_velocity: float) -> Params:
    return Params(
        mass=4.0,
        J_com=np.diag([0.18, 0.32, 0.41]),
        s_com_to_pivot=np.array([0.0, 0.0, 0.75]),
        gravity=np.array([0.0, 0.0, -9.81]),
        hinge_axis_body=np.array([0.0, 1.0, 0.0]),
        hinge_axis_world=np.array([0.0, 1.0, 0.0]),
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
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
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


def initial_state(params: Params) -> State:
    p = qp.quat_exp(np.array([0.0, 0.95, 0.0]))
    R = qp.quat_to_rot(p)
    w = np.array([0.0, 0.25, 0.0])
    r = -R @ params.s_com_to_pivot
    v = -R @ np.cross(w, params.s_com_to_pivot)
    return State(r=r, p=p, v=v, w=w)


def revolute_angle(state: State) -> float:
    R = qp.quat_to_rot(state.p)
    return float(np.arctan2(R[0, 2], R[2, 2]))


def state_error(ref: State, state: State) -> tuple[float, float]:
    rot = qp.orientation_error(qp.quat_to_rot(ref.p), qp.quat_to_rot(state.p))
    vel = float(np.linalg.norm(ref.w - state.w))
    return rot, vel


def estimate_order(hs: list[float], errors: list[float]) -> float:
    if len(hs) < 2:
        return float("nan")
    xs = np.log(np.asarray(hs, dtype=float))
    ys = np.log(np.maximum(np.asarray(errors, dtype=float), 1.0e-300))
    slope, _ = np.polyfit(xs, ys, 1)
    return float(slope)


def brown_mcphee_scalar(v: float, normal_load: float, params: Params) -> float:
    vs = max(params.stribeck_velocity, 1.0e-12)
    z = v / vs
    denom = (0.25 * z * z + 0.75) ** 2
    curve = params.mu_d * np.tanh(4.0 * z) + (params.mu_s - params.mu_d) * z / denom
    return -params.friction_radius * normal_load * curve - params.viscous_damping * np.tanh(4.0) * v


def brown_mcphee_scalar_jax(v, normal_load, mu_s, mu_d, stribeck_velocity, viscous_damping, friction_radius):
    vs = jnp.maximum(stribeck_velocity, 1.0e-12)
    z = v / vs
    denom = (0.25 * z * z + 0.75) ** 2
    curve = mu_d * jnp.tanh(4.0 * z) + (mu_s - mu_d) * z / denom
    return -friction_radius * normal_load * curve - viscous_damping * jnp.tanh(jnp.array(4.0, dtype=v.dtype)) * v


def revolute_constraints_np(r: np.ndarray, p: np.ndarray, params: Params) -> np.ndarray:
    R = qp.quat_to_rot(p)
    axis = R @ params.hinge_axis_body
    return np.concatenate((r + R @ params.s_com_to_pivot, np.array([axis[0], axis[2]])))


def velocity_constraints_np(v: np.ndarray, p: np.ndarray, w: np.ndarray, params: Params) -> np.ndarray:
    R = qp.quat_to_rot(p)
    axis_rate = R @ np.cross(w, params.hinge_axis_body)
    return np.concatenate((v + R @ np.cross(w, params.s_com_to_pivot), np.array([axis_rate[0], axis_rate[2]])))


def scalar_acceleration_guess(q: float, qdot: float, params: Params) -> float:
    mass = params.mass
    length = float(np.linalg.norm(params.s_com_to_pivot))
    inertia = float(params.J_com[1, 1] + mass * length * length)
    alpha = -mass * 9.81 * length * np.sin(q) / inertia
    for _ in range(8):
        xdd = length * np.sin(q) * qdot * qdot - length * np.cos(q) * alpha
        zdd = length * np.cos(q) * qdot * qdot + length * np.sin(q) * alpha
        reaction = mass * np.array([xdd, 0.0, zdd + 9.81])
        tau = brown_mcphee_scalar(qdot, float(np.linalg.norm(reaction)), params)
        next_alpha = (-mass * 9.81 * length * np.sin(q) + tau) / inertia
        if abs(next_alpha - alpha) < 1.0e-13:
            break
        alpha = next_alpha
    return float(alpha)


def stage_guess(state: State, h: float, params: Params, n_stages: int) -> np.ndarray:
    c, _, _ = qp.gauss_legendre_coefficients(n_stages)
    q0 = revolute_angle(state)
    qdot0 = float(state.w[1])
    alpha0 = scalar_acceleration_guess(q0, qdot0, params)
    blocks = []
    for ci in c:
        q_i = q0 + ci * h * qdot0
        qdot_i = qdot0 + ci * h * alpha0
        alpha_i_y = scalar_acceleration_guess(q_i, qdot_i, params)
        u_i = np.array([0.0, q_i - q0, 0.0])
        p_i = qp.compose_right_quat(state.p, u_i)
        R_i = qp.quat_to_rot(p_i)
        w_i = np.array([0.0, qdot_i, 0.0])
        alpha_i = np.array([0.0, alpha_i_y, 0.0])
        r_i = -R_i @ params.s_com_to_pivot
        v_i = -R_i @ np.cross(w_i, params.s_com_to_pivot)
        a_i = -R_i @ (
            np.cross(alpha_i, params.s_com_to_pivot)
            + np.cross(w_i, np.cross(w_i, params.s_com_to_pivot))
        )
        force_lambda = params.mass * (a_i - params.gravity)
        eta = np.zeros(2)
        blocks.extend([u_i, r_i, v_i, w_i, a_i, alpha_i, np.concatenate((force_lambda, eta))])
    return np.concatenate(blocks)


def unpack_stages(x, n_stages: int):
    stages = []
    offset = 0
    for _ in range(n_stages):
        stages.append(
            {
                "u": x[offset : offset + 3],
                "r": x[offset + 3 : offset + 6],
                "v": x[offset + 6 : offset + 9],
                "w": x[offset + 9 : offset + 12],
                "a": x[offset + 12 : offset + 15],
                "alpha": x[offset + 15 : offset + 18],
                "lambda": x[offset + 18 : offset + 23],
            }
        )
        offset += 23
    return stages


def axis_torque_jax(R, eta, hinge_axis_body):
    bx = jnp.array([1.0, 0.0, 0.0], dtype=R.dtype)
    bz = jnp.array([0.0, 0.0, 1.0], dtype=R.dtype)
    g1 = jnp.cross(hinge_axis_body, R.T @ bx)
    g2 = jnp.cross(hinge_axis_body, R.T @ bz)
    return eta[0] * g1 + eta[1] * g2


def residual_core(
    x,
    r0,
    p0,
    v0,
    w0,
    h,
    mass,
    J_com,
    s,
    gravity,
    hinge_axis_body,
    mu_s,
    mu_d,
    stribeck_velocity,
    viscous_damping,
    friction_radius,
    n_stages: int,
):
    _, A, _ = qp._gauss_legendre_coefficients_jax(n_stages, x.dtype)
    stages = unpack_stages(x, n_stages)
    ks = [qp._right_jacobian_inverse_apply_jax(st["u"], st["w"]) for st in stages]
    out = []
    for i, st in enumerate(stages):
        p_i = qp.compose_right_quat_jax(p0, st["u"])
        R_i = qp.quat_to_rot_jax(p_i)
        lam_force = st["lambda"][:3]
        eta = st["lambda"][3:5]
        normal_load = jnp.linalg.norm(lam_force)
        tau_scalar = brown_mcphee_scalar_jax(
            st["w"][1], normal_load, mu_s, mu_d, stribeck_velocity, viscous_damping, friction_radius
        )
        tau_f = jnp.array([0.0, tau_scalar, 0.0], dtype=x.dtype)
        reaction_torque = jnp.cross(s, R_i.T @ lam_force)
        joint_torque = axis_torque_jax(R_i, eta, hinge_axis_body)
        axis = R_i @ hinge_axis_body
        axis_rate = R_i @ jnp.cross(st["w"], hinge_axis_body)
        out.extend(
            [
                st["r"] - r0 - h * sum(A[i, j] * stages[j]["v"] for j in range(n_stages)),
                st["u"] - h * sum(A[i, j] * ks[j] for j in range(n_stages)),
                st["v"] - v0 - h * sum(A[i, j] * stages[j]["a"] for j in range(n_stages)),
                st["w"] - w0 - h * sum(A[i, j] * stages[j]["alpha"] for j in range(n_stages)),
                mass * st["a"] - mass * gravity - lam_force,
                J_com @ st["alpha"] + jnp.cross(st["w"], J_com @ st["w"]) - reaction_torque - joint_torque - tau_f,
                st["r"] + R_i @ s,
                jnp.array([axis[0], axis[2]], dtype=x.dtype),
            ]
        )
    return jnp.concatenate(out)


def residual2_core(x, *args):
    return residual_core(x, *args, n_stages=2)


def residual3_core(x, *args):
    return residual_core(x, *args, n_stages=3)


residual2_value = jax.jit(residual2_core)
residual2_jacobian = jax.jit(jax.jacfwd(residual2_core, argnums=0))
residual3_value = jax.jit(residual3_core)
residual3_jacobian = jax.jit(jax.jacfwd(residual3_core, argnums=0))


def gauss_step(state: State, h: float, params: Params, n_stages: int) -> tuple[State, int, dict]:
    _, _, b = qp.gauss_legendre_coefficients(n_stages)
    x = stage_guess(state, h, params, n_stages)
    args = (
        jnp.asarray(state.r, dtype=jnp.float64),
        jnp.asarray(state.p, dtype=jnp.float64),
        jnp.asarray(state.v, dtype=jnp.float64),
        jnp.asarray(state.w, dtype=jnp.float64),
        jnp.asarray(h, dtype=jnp.float64),
        jnp.asarray(params.mass, dtype=jnp.float64),
        jnp.asarray(params.J_com, dtype=jnp.float64),
        jnp.asarray(params.s_com_to_pivot, dtype=jnp.float64),
        jnp.asarray(params.gravity, dtype=jnp.float64),
        jnp.asarray(params.hinge_axis_body, dtype=jnp.float64),
        jnp.asarray(params.mu_s, dtype=jnp.float64),
        jnp.asarray(params.mu_d, dtype=jnp.float64),
        jnp.asarray(params.stribeck_velocity, dtype=jnp.float64),
        jnp.asarray(params.viscous_damping, dtype=jnp.float64),
        jnp.asarray(params.friction_radius, dtype=jnp.float64),
    )
    if n_stages == 2:
        value, jacobian, max_iters = residual2_value, residual2_jacobian, 32
    elif n_stages == 3:
        value, jacobian, max_iters = residual3_value, residual3_jacobian, 40
    else:
        raise ValueError(f"unsupported stage count {n_stages}")
    last_norm = np.inf
    for it in range(max_iters):
        x_jax = jnp.asarray(x, dtype=jnp.float64)
        res = np.asarray(value(x_jax, *args), dtype=float)
        last_norm = float(np.linalg.norm(res))
        if last_norm < 1.0e-11:
            break
        jac = np.asarray(jacobian(x_jax, *args), dtype=float)
        delta = np.linalg.solve(jac, -res)
        x = x + delta
        if float(np.linalg.norm(delta)) < 1.0e-11:
            break
    else:
        raise RuntimeError(f"absolute revolute DAE solve failed, residual={last_norm:.3e}")
    stages = unpack_stages(x, n_stages)
    ks = [qp.right_jacobian_inverse_apply(st["u"], st["w"]) for st in stages]
    r_next = state.r + h * sum(b[j] * stages[j]["v"] for j in range(n_stages))
    v_next = state.v + h * sum(b[j] * stages[j]["a"] for j in range(n_stages))
    u_next = h * sum(b[j] * ks[j] for j in range(n_stages))
    p_next = qp.compose_right_quat(state.p, u_next)
    w_next = state.w + h * sum(b[j] * stages[j]["alpha"] for j in range(n_stages))
    next_state = State(r=r_next, p=p_next, v=v_next, w=w_next)
    max_stage_constraint = 0.0
    max_stage_velocity_constraint = 0.0
    max_lambda = 0.0
    max_power = -np.inf
    min_power = np.inf
    for st in stages:
        p_i = qp.compose_right_quat(state.p, st["u"])
        max_stage_constraint = max(
            max_stage_constraint, float(np.linalg.norm(revolute_constraints_np(st["r"], p_i, params)))
        )
        max_stage_velocity_constraint = max(
            max_stage_velocity_constraint,
            float(np.linalg.norm(velocity_constraints_np(st["v"], p_i, st["w"], params))),
        )
        lam_force = st["lambda"][:3]
        tau = brown_mcphee_scalar(st["w"][1], float(np.linalg.norm(lam_force)), params)
        max_power = max(max_power, float(tau * st["w"][1]))
        min_power = min(min_power, float(tau * st["w"][1]))
        max_lambda = max(max_lambda, float(np.linalg.norm(st["lambda"])))
    diag = {
        "newton_iterations": it + 1,
        "stage_residual_norm": last_norm,
        "max_stage_constraint_norm": max_stage_constraint,
        "max_stage_velocity_constraint_norm": max_stage_velocity_constraint,
        "max_endpoint_constraint_norm": float(np.linalg.norm(revolute_constraints_np(next_state.r, next_state.p, params))),
        "max_endpoint_velocity_constraint_norm": float(
            np.linalg.norm(velocity_constraints_np(next_state.v, next_state.p, next_state.w, params))
        ),
        "max_lambda_norm": max_lambda,
        "max_stage_friction_power": max_power,
        "min_stage_friction_power": min_power,
        "max_quaternion_unit_error": float(abs(np.linalg.norm(next_state.p) - 1.0)),
    }
    return next_state, it + 1, diag


def energy(state: State, params: Params) -> float:
    kinetic = 0.5 * params.mass * float(state.v @ state.v) + 0.5 * float(state.w @ params.J_com @ state.w)
    potential = -params.mass * float(params.gravity @ state.r)
    return kinetic + potential


def integrate(method: str, h: float, t_final: float, params: Params) -> dict:
    n_steps = int(round(t_final / h))
    if abs(n_steps * h - t_final) > 1.0e-12:
        raise ValueError("h must divide t_final")
    n_stages = 2 if method == "abs_revolute_gauss4" else 3
    state = initial_state(params)
    E0 = energy(state, params)
    prev_energy = E0
    total_iters = 0
    max_energy_increase = 0.0
    max_endpoint_constraint = 0.0
    max_endpoint_velocity_constraint = 0.0
    max_stage_constraint = 0.0
    max_stage_velocity_constraint = 0.0
    max_lambda = 0.0
    max_power = -np.inf
    min_power = np.inf
    max_quat_unit = float(abs(np.linalg.norm(state.p) - 1.0))
    for _ in range(n_steps):
        state, niters, diag = gauss_step(state, h, params, n_stages)
        total_iters += niters
        max_endpoint_constraint = max(max_endpoint_constraint, diag["max_endpoint_constraint_norm"])
        max_endpoint_velocity_constraint = max(
            max_endpoint_velocity_constraint, diag["max_endpoint_velocity_constraint_norm"]
        )
        max_stage_constraint = max(max_stage_constraint, diag["max_stage_constraint_norm"])
        max_stage_velocity_constraint = max(max_stage_velocity_constraint, diag["max_stage_velocity_constraint_norm"])
        max_lambda = max(max_lambda, diag["max_lambda_norm"])
        max_power = max(max_power, diag["max_stage_friction_power"])
        min_power = min(min_power, diag["min_stage_friction_power"])
        max_quat_unit = max(max_quat_unit, diag["max_quaternion_unit_error"])
        E = energy(state, params)
        max_energy_increase = max(max_energy_increase, E - prev_energy)
        prev_energy = E
    final_energy = energy(state, params)
    return {
        "state": state,
        "steps": n_steps,
        "total_newton_iterations": total_iters,
        "final_energy_change": final_energy - E0,
        "final_energy_relative_change": (final_energy - E0) / max(abs(E0), 1.0e-30),
        "max_step_energy_increase": max_energy_increase,
        "max_endpoint_constraint_norm": max_endpoint_constraint,
        "max_endpoint_velocity_constraint_norm": max_endpoint_velocity_constraint,
        "max_stage_constraint_norm": max_stage_constraint,
        "max_stage_velocity_constraint_norm": max_stage_velocity_constraint,
        "max_lambda_norm": max_lambda,
        "max_stage_friction_power": max_power,
        "min_stage_friction_power": min_power,
        "max_quaternion_unit_error": max_quat_unit,
    }


def run_experiment() -> dict:
    rows = []
    cases = {}
    for case_name, vs in CASES.items():
        params = make_params(vs)
        ref = integrate("abs_revolute_gauss6", REF_H, T_FINAL, params)
        ref_state = ref["state"]
        # Warm both JAX traces before timed runs.
        state0 = initial_state(params)
        gauss_step(state0, 0.025, params, 2)
        gauss_step(state0, 0.025, params, 3)
        method_summary = {}
        for method in METHODS:
            orientation_hs = []
            omega_hs = []
            orientation_errors = []
            omega_errors = []
            runs = {}
            for h in HS:
                start = time.perf_counter()
                runtime = time.perf_counter() - start
                row = {key: "" for key in CSV_COLUMNS}
                row.update({"case": case_name, "method": method, "h": f"{h:.10g}", "runtime_sec": f"{runtime:.8e}"})
                try:
                    out = integrate(method, h, T_FINAL, params)
                    runtime = time.perf_counter() - start
                    oerr, werr = state_error(ref_state, out["state"])
                    orientation_hs.append(h)
                    omega_hs.append(h)
                    orientation_errors.append(oerr)
                    omega_errors.append(werr)
                    row.update(
                        {
                            "status": "ok",
                            "error_message": "",
                            "steps": out["steps"],
                            "orientation_error_rad": f"{oerr:.16e}",
                            "omega_l2_error": f"{werr:.16e}",
                            "runtime_sec": f"{runtime:.8e}",
                            "total_newton_iterations": out["total_newton_iterations"],
                            "max_endpoint_constraint_norm": f"{out['max_endpoint_constraint_norm']:.16e}",
                            "max_endpoint_velocity_constraint_norm": f"{out['max_endpoint_velocity_constraint_norm']:.16e}",
                            "max_stage_constraint_norm": f"{out['max_stage_constraint_norm']:.16e}",
                            "max_stage_velocity_constraint_norm": f"{out['max_stage_velocity_constraint_norm']:.16e}",
                            "max_lambda_norm": f"{out['max_lambda_norm']:.16e}",
                            "max_stage_friction_power": f"{out['max_stage_friction_power']:.16e}",
                            "final_energy_relative_change": f"{out['final_energy_relative_change']:.16e}",
                            "max_step_energy_increase": f"{out['max_step_energy_increase']:.16e}",
                            "max_quaternion_unit_error": f"{out['max_quaternion_unit_error']:.16e}",
                        }
                    )
                    item = {key: value for key, value in out.items() if key != "state"}
                    item.update({"status": "ok", "orientation_error_rad": oerr, "omega_l2_error": werr, "runtime_sec": runtime})
                except Exception as exc:
                    runtime = time.perf_counter() - start
                    message = str(exc)
                    row.update({"status": "failed", "error_message": message, "runtime_sec": f"{runtime:.8e}"})
                    item = {"status": "failed", "error_message": message, "runtime_sec": runtime}
                rows.append(row)
                runs[str(h)] = item
            method_summary[method] = {
                "orientation_observed_order": estimate_order(orientation_hs, orientation_errors),
                "omega_observed_order": estimate_order(omega_hs, omega_errors),
                "runs": runs,
            }
        cases[case_name] = {
            "stribeck_velocity": vs,
            "reference_method": "abs_revolute_gauss6",
            "reference_h": REF_H,
            "methods": method_summary,
            "reference": {key: value for key, value in ref.items() if key != "state"},
        }
    write_csv(RESULTS / "absolute_revolute_dae_runs.csv", rows)
    return {"t_final": T_FINAL, "cases": cases}


def plot_results(summary: dict) -> None:
    import matplotlib.pyplot as plt

    plt.figure(figsize=(7.6, 4.8))
    for case_name, case in summary["cases"].items():
        for method in METHODS:
            runs = case["methods"][method]["runs"]
            ok = [(float(h), runs[h]["orientation_error_rad"]) for h in runs.keys() if runs[h].get("status") == "ok"]
            if not ok:
                continue
            hs = np.array([item[0] for item in ok])
            errs = np.array([item[1] for item in ok])
            plt.loglog(hs, errs, marker="o", label=f"{case_name} {method}")
    plt.gca().invert_xaxis()
    plt.xlabel("step size h")
    plt.ylabel("orientation error rad")
    plt.title("Absolute Revolute DAE Brown-McPhee Convergence")
    plt.grid(True, which="both", alpha=0.35)
    plt.legend(fontsize=7)
    plt.tight_layout()
    plt.savefig(RESULTS / "absolute_revolute_dae_convergence.png", dpi=180)
    plt.close()


def write_report(summary: dict) -> None:
    def order_text(value: float) -> str:
        return f"{value:.3f}" if np.isfinite(value) else "insufficient successful points"

    lines = [
        "# v023 Experiment Report",
        "",
        "Generated by `run_v023.py`.",
        "",
        "## Purpose",
        "",
        "- Move from v022's reduced one-DOF revolute model to an absolute-coordinate quaternion DAE.",
        "- Use stage variables `r,u,v,w,a,alpha,lambda` with five revolute constraints: fixed pivot plus hinge-axis alignment.",
        "- Keep Brown-McPhee friction dependent on the stage reaction-force norm so JAX differentiates the coupled friction/multiplier residual.",
        "- This version does not endpoint-project; endpoint constraint errors are diagnostics.",
        "",
        "## Results",
        "",
    ]
    for case_name, case in summary["cases"].items():
        lines.append(f"### {case_name}")
        for method in METHODS:
            item = case["methods"][method]
            ok_runs = [(float(h), run) for h, run in item["runs"].items() if run.get("status") == "ok"]
            failed_runs = [(float(h), run) for h, run in item["runs"].items() if run.get("status") == "failed"]
            if ok_runs:
                fine_h, fine = sorted(ok_runs, key=lambda pair: pair[0])[0]
                lines.append(
                    f"- `{method}`: orientation order {order_text(item['orientation_observed_order'])}, "
                    f"omega order {order_text(item['omega_observed_order'])}; finest successful h={fine_h:g} "
                    f"orientation error {fine['orientation_error_rad']:.3e}, runtime {fine['runtime_sec']:.3f}s, "
                    f"endpoint constraint {fine['max_endpoint_constraint_norm']:.3e}, "
                    f"velocity constraint {fine['max_endpoint_velocity_constraint_norm']:.3e}."
                )
            else:
                lines.append(f"- `{method}`: no successful fixed-step run.")
            if failed_runs:
                failures = "; ".join(f"h={h:g}: {run['error_message']}" for h, run in sorted(failed_runs))
                lines.append(f"- `{method}` failures: {failures}.")
        g4 = case["methods"]["abs_revolute_gauss4"]["runs"].get("0.0125")
        g6 = case["methods"]["abs_revolute_gauss6"]["runs"].get("0.0125")
        if g4 and g6 and g4.get("status") == "ok" and g6.get("status") == "ok":
            lines.append(
                f"- Gauss6 vs Gauss4 at h=0.0125: "
                f"{g4['orientation_error_rad'] / max(g6['orientation_error_rad'], 1e-30):.2e}x lower "
                f"orientation error at {g6['runtime_sec'] / max(g4['runtime_sec'], 1e-30):.2f}x runtime."
            )
        else:
            lines.append("- Gauss6 vs Gauss4 at h=0.0125 is not comparable because at least one run failed.")
        lines.append("")
    lines.extend(
        [
            "## Interpretation",
            "",
            "- This is the first local test with a true five-constraint revolute joint residual rather than a reconstructed reduced constraint.",
            "- It is deliberately not endpoint-projected, so endpoint constraint drift measures whether the stage-collocation DAE residual is strong enough.",
            "- If the method order is lower than v022, that is useful evidence: the missing endpoint/velocity/acceleration constraint treatment matters for full index-3 DAE behavior.",
            "- This version tests model/formulation fidelity, not only raw high-order accuracy.",
            "",
            "## Outputs",
            "",
            "- `absolute_revolute_dae_runs.csv`",
            "- `summary_v023.json`",
            "- `absolute_revolute_dae_convergence.png`",
            "",
        ]
    )
    (RESULTS / "v023_report.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    experiment = run_experiment()
    plot_results(experiment)
    summary = {
        "version": "v023_absolute_revolute_dae",
        "python": platform.python_version(),
        "platform": platform.platform(),
        "numpy": np.__version__,
        "jax": jax.__version__,
        "model": {
            "cases": CASES,
            "methods": METHODS,
            "step_sizes": HS,
            "reference_h": REF_H,
            "t_final": T_FINAL,
            "constraints": "pivot position plus hinge-axis alignment",
            "endpoint_projection": False,
        },
        "experiment": experiment,
        "runtime_sec": time.perf_counter() - started,
    }
    with (RESULTS / "summary_v023.json").open("w", encoding="utf-8") as f:
        json.dump(json_safe(summary), f, indent=2, sort_keys=True)
    write_report(experiment)


if __name__ == "__main__":
    main()
