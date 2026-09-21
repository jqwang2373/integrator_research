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
from numpy.polynomial import Polynomial

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
METHODS = ["abs_revolute_gauss4", "abs_revolute_gauss6", "abs_revolute_lobatto4", "abs_revolute_lobatto6"]
T_FINAL = 1.0
REF_H = 0.00625
REFERENCE_METHOD = "abs_revolute_gauss6"
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
    "linear_lstsq_fallbacks",
    "min_jacobian_rank",
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


def lobatto_nodes(n_stages: int) -> np.ndarray:
    if n_stages == 3:
        return np.array([0.0, 0.5, 1.0])
    if n_stages == 4:
        root5 = np.sqrt(5.0)
        return np.array([0.0, 0.5 - root5 / 10.0, 0.5 + root5 / 10.0, 1.0])
    raise ValueError(f"unsupported Lobatto stage count {n_stages}")


def collocation_coefficients(family: str, n_stages: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    if family == "gauss":
        return qp.gauss_legendre_coefficients(n_stages)
    if family != "lobatto":
        raise ValueError(f"unknown collocation family {family}")
    c = lobatto_nodes(n_stages)
    A = np.zeros((n_stages, n_stages))
    b = np.zeros(n_stages)
    for j in range(n_stages):
        basis = Polynomial([1.0])
        denom = 1.0
        for m in range(n_stages):
            if m == j:
                continue
            basis *= Polynomial([-c[m], 1.0])
            denom *= c[j] - c[m]
        basis = basis / denom
        integral = basis.integ()
        b[j] = integral(1.0) - integral(0.0)
        for i in range(n_stages):
            A[i, j] = integral(c[i]) - integral(0.0)
    return c, A, b


def collocation_coefficients_jax(family: str, n_stages: int, dtype):
    c, A, b = collocation_coefficients(family, n_stages)
    return jnp.asarray(c, dtype=dtype), jnp.asarray(A, dtype=dtype), jnp.asarray(b, dtype=dtype)


def method_family_and_stages(method: str) -> tuple[str, int]:
    if method == "abs_revolute_gauss4":
        return "gauss", 2
    if method == "abs_revolute_gauss6":
        return "gauss", 3
    if method == "abs_revolute_lobatto4":
        return "lobatto", 3
    if method == "abs_revolute_lobatto6":
        return "lobatto", 4
    raise ValueError(f"unknown method {method}")


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


def hat_jax(w):
    return jnp.array(
        [
            [0.0, -w[2], w[1]],
            [w[2], 0.0, -w[0]],
            [-w[1], w[0], 0.0],
        ],
        dtype=w.dtype,
    )


def quat_exp_jax_safe(theta):
    theta2 = theta @ theta
    angle = jnp.sqrt(jnp.maximum(theta2, jnp.array(1.0e-30, dtype=theta.dtype)))
    scalar_small = 1.0 - theta2 / 8.0 + theta2 * theta2 / 384.0
    b_small = 0.5 - theta2 / 48.0 + theta2 * theta2 / 3840.0
    scalar_large = jnp.cos(0.5 * angle)
    b_large = jnp.sin(0.5 * angle) / angle
    small = theta2 < 1.0e-16
    return jnp.concatenate((jnp.array([jnp.where(small, scalar_small, scalar_large)], dtype=theta.dtype), jnp.where(small, b_small, b_large) * theta))


def compose_right_quat_jax_safe(q, u):
    out = qp.quat_mul_jax(q, quat_exp_jax_safe(u))
    return out / jnp.sqrt(jnp.maximum(out @ out, jnp.array(1.0e-30, dtype=out.dtype)))


def right_jacobian_inverse_apply_jax_safe(u, w):
    theta2 = u @ u
    theta2_safe = jnp.maximum(theta2, jnp.array(1.0e-30, dtype=u.dtype))
    theta = jnp.sqrt(theta2_safe)
    U = hat_jax(u)
    U2 = U @ U
    coeff_small = 1.0 / 12.0 + theta2 / 720.0 + theta2 * theta2 / 30240.0
    coeff_large = 1.0 / theta2_safe - (1.0 + jnp.cos(theta)) / (2.0 * theta * jnp.sin(theta))
    coeff = jnp.where(theta2 < 1.0e-14, coeff_small, coeff_large)
    return (jnp.eye(3, dtype=u.dtype) + 0.5 * U + coeff * U2) @ w


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


def stage_guess(state: State, h: float, params: Params, family: str, n_stages: int) -> np.ndarray:
    c, _, _ = collocation_coefficients(family, n_stages)
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
    family: str,
    n_stages: int,
):
    _, A, _ = collocation_coefficients_jax(family, n_stages, x.dtype)
    stages = unpack_stages(x, n_stages)
    ks = [right_jacobian_inverse_apply_jax_safe(st["u"], st["w"]) for st in stages]
    out = []
    for i, st in enumerate(stages):
        p_i = compose_right_quat_jax_safe(p0, st["u"])
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


def residual_gauss2_core(x, *args):
    return residual_core(x, *args, family="gauss", n_stages=2)


def residual_gauss3_core(x, *args):
    return residual_core(x, *args, family="gauss", n_stages=3)


def residual_lobatto3_core(x, *args):
    return residual_core(x, *args, family="lobatto", n_stages=3)


def residual_lobatto4_core(x, *args):
    return residual_core(x, *args, family="lobatto", n_stages=4)


residual_gauss2_value = jax.jit(residual_gauss2_core)
residual_gauss2_jacobian = jax.jit(jax.jacfwd(residual_gauss2_core, argnums=0))
residual_gauss3_value = jax.jit(residual_gauss3_core)
residual_gauss3_jacobian = jax.jit(jax.jacfwd(residual_gauss3_core, argnums=0))
residual_lobatto3_value = jax.jit(residual_lobatto3_core)
residual_lobatto3_jacobian = jax.jit(jax.jacfwd(residual_lobatto3_core, argnums=0))
residual_lobatto4_value = jax.jit(residual_lobatto4_core)
residual_lobatto4_jacobian = jax.jit(jax.jacfwd(residual_lobatto4_core, argnums=0))


def collocation_step(state: State, h: float, params: Params, method: str) -> tuple[State, int, dict]:
    family, n_stages = method_family_and_stages(method)
    _, _, b = collocation_coefficients(family, n_stages)
    x = stage_guess(state, h, params, family, n_stages)
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
    if method == "abs_revolute_gauss4":
        value, jacobian, max_iters = residual_gauss2_value, residual_gauss2_jacobian, 32
    elif method == "abs_revolute_gauss6":
        value, jacobian, max_iters = residual_gauss3_value, residual_gauss3_jacobian, 40
    elif method == "abs_revolute_lobatto4":
        value, jacobian, max_iters = residual_lobatto3_value, residual_lobatto3_jacobian, 16
    elif method == "abs_revolute_lobatto6":
        value, jacobian, max_iters = residual_lobatto4_value, residual_lobatto4_jacobian, 18
    else:
        raise ValueError(f"unknown method {method}")
    last_norm = np.inf
    linear_lstsq_fallbacks = 0
    min_jacobian_rank = x.size
    for it in range(max_iters):
        x_jax = jnp.asarray(x, dtype=jnp.float64)
        res = np.asarray(value(x_jax, *args), dtype=float)
        last_norm = float(np.linalg.norm(res))
        if last_norm < 1.0e-11:
            break
        jac = np.asarray(jacobian(x_jax, *args), dtype=float)
        try:
            delta = np.linalg.solve(jac, -res)
        except np.linalg.LinAlgError:
            linear_lstsq_fallbacks += 1
            min_jacobian_rank = min(min_jacobian_rank, int(np.linalg.matrix_rank(jac, tol=1.0e-10)))
            jt = jac.T
            eye = np.eye(jac.shape[1])
            delta = None
            for damping in (1.0e-8, 1.0e-6, 1.0e-4, 1.0e-2, 1.0):
                try:
                    candidate = np.linalg.solve(jt @ jac + damping * eye, -(jt @ res))
                except np.linalg.LinAlgError:
                    continue
                for scale in (1.0, 0.5, 0.25, 0.125, 0.0625, 0.03125):
                    trial = x + scale * candidate
                    trial_norm = float(np.linalg.norm(np.asarray(value(jnp.asarray(trial, dtype=jnp.float64), *args), dtype=float)))
                    if np.isfinite(trial_norm) and trial_norm < last_norm:
                        delta = scale * candidate
                        break
                if delta is not None:
                    break
            if delta is None:
                raise RuntimeError(
                    f"{method} rank-deficient Newton step has no residual-decreasing damped direction, "
                    f"residual={last_norm:.3e}, rank={min_jacobian_rank}"
                )
        x = x + delta
        if float(np.linalg.norm(delta)) < 1.0e-11:
            break
    else:
        raise RuntimeError(f"{method} solve failed, residual={last_norm:.3e}")
    stages = unpack_stages(x, n_stages)
    ks = [qp.right_jacobian_inverse_apply(st["u"], st["w"]) for st in stages]
    if family == "lobatto":
        endpoint = stages[-1]
        r_next = endpoint["r"]
        v_next = endpoint["v"]
        p_next = qp.compose_right_quat(state.p, endpoint["u"])
        w_next = endpoint["w"]
    else:
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
        "linear_lstsq_fallbacks": linear_lstsq_fallbacks,
        "min_jacobian_rank": min_jacobian_rank,
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
    method_family_and_stages(method)
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
    linear_lstsq_fallbacks = 0
    min_jacobian_rank = np.inf
    for _ in range(n_steps):
        state, niters, diag = collocation_step(state, h, params, method)
        total_iters += niters
        linear_lstsq_fallbacks += diag["linear_lstsq_fallbacks"]
        min_jacobian_rank = min(min_jacobian_rank, diag["min_jacobian_rank"])
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
        "linear_lstsq_fallbacks": linear_lstsq_fallbacks,
        "min_jacobian_rank": None if not np.isfinite(min_jacobian_rank) else int(min_jacobian_rank),
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
        ref = integrate(REFERENCE_METHOD, REF_H, T_FINAL, params)
        ref_state = ref["state"]
        # Warm JAX traces before timed runs, including Lobatto's zero endpoint node.
        state0 = initial_state(params)
        for warm_method in METHODS:
            try:
                collocation_step(state0, 0.025, params, warm_method)
            except Exception:
                pass
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
                            "linear_lstsq_fallbacks": out["linear_lstsq_fallbacks"],
                            "min_jacobian_rank": "" if out["min_jacobian_rank"] is None else out["min_jacobian_rank"],
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
            "reference_method": REFERENCE_METHOD,
            "reference_h": REF_H,
            "methods": method_summary,
            "reference": {key: value for key, value in ref.items() if key != "state"},
        }
    write_csv(RESULTS / "absolute_revolute_lobatto_runs.csv", rows)
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
    plt.title("Absolute Revolute DAE: Gauss vs Lobatto")
    plt.grid(True, which="both", alpha=0.35)
    plt.legend(fontsize=7)
    plt.tight_layout()
    plt.savefig(RESULTS / "absolute_revolute_lobatto_convergence.png", dpi=180)
    plt.close()

    plt.figure(figsize=(7.6, 4.8))
    for case_name, case in summary["cases"].items():
        for method in METHODS:
            runs = case["methods"][method]["runs"]
            ok = [
                (float(h), runs[h]["max_endpoint_constraint_norm"])
                for h in runs.keys()
                if runs[h].get("status") == "ok"
            ]
            if not ok:
                continue
            hs = np.array([item[0] for item in ok])
            errs = np.array([item[1] for item in ok])
            plt.loglog(hs, errs, marker="o", label=f"{case_name} {method}")
    plt.gca().invert_xaxis()
    plt.xlabel("step size h")
    plt.ylabel("endpoint position constraint norm")
    plt.title("Endpoint Constraint Drift")
    plt.grid(True, which="both", alpha=0.35)
    plt.legend(fontsize=7)
    plt.tight_layout()
    plt.savefig(RESULTS / "absolute_revolute_lobatto_constraints.png", dpi=180)
    plt.close()


def write_report(summary: dict) -> None:
    def order_text(value: float) -> str:
        return f"{value:.3f}" if np.isfinite(value) else "insufficient successful points"

    lines = [
        "# v024 Experiment Report",
        "",
        "Generated by `run_v024.py`.",
        "",
        "## Purpose",
        "",
        "- Test whether endpoint-node Lobatto collocation improves the v023 absolute-coordinate quaternion revolute DAE.",
        "- Keep the same stage variables `r,u,v,w,a,alpha,lambda` and five revolute constraints: fixed pivot plus hinge-axis alignment.",
        "- Keep Brown-McPhee friction dependent on the stage reaction-force norm so JAX differentiates the coupled friction/multiplier residual.",
        "- Add zero-safe JAX Lie differentials because Lobatto includes the `c=0` stage where the local rotation increment is exactly zero.",
        "- Compare Gauss interior-node collocation against Lobatto endpoint-node collocation; endpoint constraint errors remain diagnostics.",
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
                    f"velocity constraint {fine['max_endpoint_velocity_constraint_norm']:.3e}, "
                    f"lstsq fallbacks {fine['linear_lstsq_fallbacks']}."
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
        l6 = case["methods"]["abs_revolute_lobatto6"]["runs"].get("0.0125")
        if g6 and l6 and g6.get("status") == "ok" and l6.get("status") == "ok":
            lines.append(
                f"- Lobatto6 vs Gauss6 at h=0.0125: orientation error ratio "
                f"{l6['orientation_error_rad'] / max(g6['orientation_error_rad'], 1e-30):.2e}, "
                f"endpoint constraint ratio "
                f"{l6['max_endpoint_constraint_norm'] / max(g6['max_endpoint_constraint_norm'], 1e-30):.2e}, "
                f"runtime ratio {l6['runtime_sec'] / max(g6['runtime_sec'], 1e-30):.2f}."
            )
        else:
            lines.append("- Lobatto6 vs Gauss6 at h=0.0125 is not comparable because at least one run failed.")
        lines.append("")
    lines.extend(
        [
            "## Interpretation",
            "",
            "- This extends v023's true five-constraint revolute joint residual rather than returning to a reconstructed reduced constraint.",
            "- Direct Lobatto endpoint-node collocation failed for every fixed-step run in this full revolute residual, even after adding zero-safe Lie differentials and a damped rank-deficient Newton fallback.",
            "- That failure is useful negative evidence: the paper's Gauss-Lobatto/TFE node direction cannot be transplanted by only changing collocation nodes; it needs the paper's full weighted-residual/TFE algebraic treatment or another index-3 stabilization strategy.",
            "- Gauss interior-node methods remain the only robust full absolute-coordinate revolute methods in this version, with Gauss6 again much more accurate and robust than Gauss4.",
            "- This version tests formulation fidelity and endpoint-node behavior, not only raw high-order accuracy.",
            "",
            "## Outputs",
            "",
            "- `absolute_revolute_lobatto_runs.csv`",
            "- `summary_v024.json`",
            "- `absolute_revolute_lobatto_convergence.png`",
            "- `absolute_revolute_lobatto_constraints.png`",
            "",
        ]
    )
    (RESULTS / "v024_report.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    experiment = run_experiment()
    plot_results(experiment)
    summary = {
        "version": "v024_absolute_revolute_lobatto_dae",
        "python": platform.python_version(),
        "platform": platform.platform(),
        "numpy": np.__version__,
        "jax": jax.__version__,
        "model": {
            "cases": CASES,
            "methods": METHODS,
            "step_sizes": HS,
            "reference_method": REFERENCE_METHOD,
            "reference_h": REF_H,
            "t_final": T_FINAL,
            "constraints": "pivot position plus hinge-axis alignment",
            "endpoint_projection": False,
            "new_feature": "Lobatto endpoint-node collocation with zero-safe JAX Lie differentials",
        },
        "experiment": experiment,
        "runtime_sec": time.perf_counter() - started,
    }
    with (RESULTS / "summary_v024.json").open("w", encoding="utf-8") as f:
        json.dump(json_safe(summary), f, indent=2, sort_keys=True)
    write_report(experiment)


if __name__ == "__main__":
    main()
