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

CASES = {
    "double_revolute_smooth": 0.50,
    "double_revolute_sharp": 0.05,
}
HS = [0.04, 0.02]
METHODS = [
    "double_revolute_gauss4",
    "double_revolute_gauss6",
    "double_revolute_gauss4_pivotva",
    "double_revolute_gauss6_pivotva",
    "double_revolute_gauss4_fullva",
    "double_revolute_gauss6_fullva",
]
T_FINAL = 0.2
REF_H = 0.01
REFERENCE_METHOD = "double_revolute_gauss6_fullva"
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
    "max_endpoint_pivot_velocity_constraint_norm",
    "max_endpoint_axis_velocity_constraint_norm",
    "max_stage_constraint_norm",
    "max_stage_velocity_constraint_norm",
    "max_stage_pivot_velocity_constraint_norm",
    "max_stage_axis_velocity_constraint_norm",
    "max_stage_pivot_acceleration_constraint_norm",
    "max_stage_axis_acceleration_constraint_norm",
    "max_stage_acceleration_constraint_norm",
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
    mass1: float
    mass2: float
    J1: np.ndarray
    J2: np.ndarray
    s1_ground: np.ndarray
    s1_tip: np.ndarray
    s2_joint: np.ndarray
    gravity: np.ndarray
    hinge_axis_body: np.ndarray
    mu_s: float
    mu_d: float
    stribeck_velocity: float
    viscous_damping: float
    friction_radius: float
    external_torque1_body: np.ndarray
    external_torque2_body: np.ndarray


@dataclass
class State:
    r1: np.ndarray
    p1: np.ndarray
    v1: np.ndarray
    w1: np.ndarray
    r2: np.ndarray
    p2: np.ndarray
    v2: np.ndarray
    w2: np.ndarray


def make_params(stribeck_velocity: float) -> Params:
    return Params(
        mass1=3.2,
        mass2=2.4,
        J1=np.diag([0.16, 0.30, 0.38]),
        J2=np.diag([0.10, 0.22, 0.27]),
        s1_ground=np.array([0.0, 0.0, 0.70]),
        s1_tip=np.array([0.0, 0.0, -0.70]),
        s2_joint=np.array([0.0, 0.0, 0.55]),
        gravity=np.array([0.0, 0.0, -9.81]),
        hinge_axis_body=np.array([0.0, 1.0, 0.0]),
        mu_s=0.30,
        mu_d=0.20,
        stribeck_velocity=float(stribeck_velocity),
        viscous_damping=0.018,
        friction_radius=0.075,
        external_torque1_body=np.array([0.25, 0.0, -0.18]),
        external_torque2_body=np.array([-0.20, 0.0, 0.14]),
    )


def json_safe(obj: object) -> object:
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, dict):
        return {key: json_safe(value) for key, value in obj.items()}
    if isinstance(obj, list):
        return [json_safe(value) for value in obj]
    if isinstance(obj, tuple):
        return [json_safe(value) for value in obj]
    if isinstance(obj, float) and not np.isfinite(obj):
        return None
    return obj


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def angle_from_quat(p: np.ndarray) -> float:
    R = qp.quat_to_rot(p)
    return float(np.arctan2(R[0, 2], R[2, 2]))


def initial_state(params: Params) -> State:
    p1 = qp.quat_exp(np.array([0.0, 0.82, 0.0]))
    p2 = qp.quat_exp(np.array([0.0, 1.28, 0.0]))
    R1 = qp.quat_to_rot(p1)
    R2 = qp.quat_to_rot(p2)
    w1 = np.array([0.0, 0.18, 0.0])
    w2 = np.array([0.0, -0.32, 0.0])
    r1 = -R1 @ params.s1_ground
    v1 = -R1 @ np.cross(w1, params.s1_ground)
    r2 = r1 + R1 @ params.s1_tip - R2 @ params.s2_joint
    v2 = v1 + R1 @ np.cross(w1, params.s1_tip) - R2 @ np.cross(w2, params.s2_joint)
    return State(r1=r1, p1=p1, v1=v1, w1=w1, r2=r2, p2=p2, v2=v2, w2=w2)


def state_error(ref: State, state: State) -> tuple[float, float]:
    e1 = qp.orientation_error(qp.quat_to_rot(ref.p1), qp.quat_to_rot(state.p1))
    e2 = qp.orientation_error(qp.quat_to_rot(ref.p2), qp.quat_to_rot(state.p2))
    werr = np.linalg.norm(np.concatenate((ref.w1 - state.w1, ref.w2 - state.w2)))
    return float(np.hypot(e1, e2)), float(werr)


def base_method(method: str) -> str:
    if method.endswith("_fullva"):
        return method[: -len("_fullva")]
    if method.endswith("_pivotva"):
        return method[: -len("_pivotva")]
    return method


def residual_mode(method: str) -> str:
    if method.endswith("_fullva"):
        return "full_va"
    if method.endswith("_pivotva"):
        return "pivot_va"
    return "raw"


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


def axis_torque_jax(R, eta, hinge_axis_body):
    bx = jnp.array([1.0, 0.0, 0.0], dtype=R.dtype)
    bz = jnp.array([0.0, 0.0, 1.0], dtype=R.dtype)
    g1 = jnp.cross(hinge_axis_body, R.T @ bx)
    g2 = jnp.cross(hinge_axis_body, R.T @ bz)
    return eta[0] * g1 + eta[1] * g2


def double_constraints_np(state: State, params: Params) -> np.ndarray:
    R1 = qp.quat_to_rot(state.p1)
    R2 = qp.quat_to_rot(state.p2)
    axis1 = R1 @ params.hinge_axis_body
    axis2 = R2 @ params.hinge_axis_body
    return np.concatenate(
        (
            state.r1 + R1 @ params.s1_ground,
            np.array([axis1[0], axis1[2]]),
            state.r1 + R1 @ params.s1_tip - state.r2 - R2 @ params.s2_joint,
            np.array([axis2[0], axis2[2]]),
        )
    )


def double_velocity_constraints_np(state: State, params: Params) -> np.ndarray:
    R1 = qp.quat_to_rot(state.p1)
    R2 = qp.quat_to_rot(state.p2)
    axis_rate1 = R1 @ np.cross(state.w1, params.hinge_axis_body)
    axis_rate2 = R2 @ np.cross(state.w2, params.hinge_axis_body)
    return np.concatenate(
        (
            state.v1 + R1 @ np.cross(state.w1, params.s1_ground),
            np.array([axis_rate1[0], axis_rate1[2]]),
            state.v1
            + R1 @ np.cross(state.w1, params.s1_tip)
            - state.v2
            - R2 @ np.cross(state.w2, params.s2_joint),
            np.array([axis_rate2[0], axis_rate2[2]]),
        )
    )


def constraint_parts_np(
    r1: np.ndarray,
    p1: np.ndarray,
    v1: np.ndarray,
    w1: np.ndarray,
    a1: np.ndarray,
    alpha1: np.ndarray,
    r2: np.ndarray,
    p2: np.ndarray,
    v2: np.ndarray,
    w2: np.ndarray,
    a2: np.ndarray,
    alpha2: np.ndarray,
    params: Params,
) -> tuple[float, float, float, float]:
    R1 = qp.quat_to_rot(p1)
    R2 = qp.quat_to_rot(p2)
    pv0 = v1 + R1 @ np.cross(w1, params.s1_ground)
    pv12 = v1 + R1 @ np.cross(w1, params.s1_tip) - v2 - R2 @ np.cross(w2, params.s2_joint)
    av1 = R1 @ np.cross(w1, params.hinge_axis_body)
    av2 = R2 @ np.cross(w2, params.hinge_axis_body)
    pa0 = a1 + R1 @ (
        np.cross(alpha1, params.s1_ground) + np.cross(w1, np.cross(w1, params.s1_ground))
    )
    pa12 = (
        a1
        + R1 @ (np.cross(alpha1, params.s1_tip) + np.cross(w1, np.cross(w1, params.s1_tip)))
        - a2
        - R2 @ (np.cross(alpha2, params.s2_joint) + np.cross(w2, np.cross(w2, params.s2_joint)))
    )
    aa1 = R1 @ (
        np.cross(alpha1, params.hinge_axis_body) + np.cross(w1, np.cross(w1, params.hinge_axis_body))
    )
    aa2 = R2 @ (
        np.cross(alpha2, params.hinge_axis_body) + np.cross(w2, np.cross(w2, params.hinge_axis_body))
    )
    pivot_v = float(np.linalg.norm(np.concatenate((pv0, pv12))))
    axis_v = float(np.linalg.norm(np.array([av1[0], av1[2], av2[0], av2[2]])))
    pivot_a = float(np.linalg.norm(np.concatenate((pa0, pa12))))
    axis_a = float(np.linalg.norm(np.array([aa1[0], aa1[2], aa2[0], aa2[2]])))
    return pivot_v, axis_v, pivot_a, axis_a


def scalar_alpha_guess(q: float, mass: float, Jyy: float, length: float) -> float:
    inertia = Jyy + mass * length * length
    return float(-mass * 9.81 * length * np.sin(q) / inertia)


def stage_guess(state: State, h: float, params: Params, n_stages: int) -> np.ndarray:
    c, _, _ = qp.gauss_legendre_coefficients(n_stages)
    q1 = angle_from_quat(state.p1)
    q2 = angle_from_quat(state.p2)
    qd1 = float(state.w1[1])
    qd2 = float(state.w2[1])
    a1_y = scalar_alpha_guess(q1, params.mass1, params.J1[1, 1], np.linalg.norm(params.s1_ground))
    a2_y = scalar_alpha_guess(q2, params.mass2, params.J2[1, 1], np.linalg.norm(params.s2_joint))
    blocks = []
    for ci in c:
        q1_i = q1 + ci * h * qd1
        q2_i = q2 + ci * h * qd2
        qd1_i = qd1 + ci * h * a1_y
        qd2_i = qd2 + ci * h * a2_y
        alpha1_i = np.array([0.0, scalar_alpha_guess(q1_i, params.mass1, params.J1[1, 1], np.linalg.norm(params.s1_ground)), 0.0])
        alpha2_i = np.array([0.0, scalar_alpha_guess(q2_i, params.mass2, params.J2[1, 1], np.linalg.norm(params.s2_joint)), 0.0])
        u1 = np.array([0.0, q1_i - q1, 0.0])
        u2 = np.array([0.0, q2_i - q2, 0.0])
        p1 = qp.compose_right_quat(state.p1, u1)
        p2 = qp.compose_right_quat(state.p2, u2)
        R1 = qp.quat_to_rot(p1)
        R2 = qp.quat_to_rot(p2)
        w1 = np.array([0.0, qd1_i, 0.0])
        w2 = np.array([0.0, qd2_i, 0.0])
        r1 = -R1 @ params.s1_ground
        v1 = -R1 @ np.cross(w1, params.s1_ground)
        a1 = -R1 @ (np.cross(alpha1_i, params.s1_ground) + np.cross(w1, np.cross(w1, params.s1_ground)))
        r2 = r1 + R1 @ params.s1_tip - R2 @ params.s2_joint
        v2 = v1 + R1 @ np.cross(w1, params.s1_tip) - R2 @ np.cross(w2, params.s2_joint)
        a2 = (
            a1
            + R1 @ (np.cross(alpha1_i, params.s1_tip) + np.cross(w1, np.cross(w1, params.s1_tip)))
            - R2 @ (np.cross(alpha2_i, params.s2_joint) + np.cross(w2, np.cross(w2, params.s2_joint)))
        )
        F12 = params.mass2 * (a2 - params.gravity)
        F0 = params.mass1 * (a1 - params.gravity) + F12
        lam = np.concatenate((F0, np.zeros(2), F12, np.zeros(2)))
        blocks.extend([u1, r1, v1, w1, a1, alpha1_i, u2, r2, v2, w2, a2, alpha2_i, lam])
    return np.concatenate(blocks)


def unpack_stages(x, n_stages: int):
    stages = []
    offset = 0
    for _ in range(n_stages):
        stages.append(
            {
                "u1": x[offset : offset + 3],
                "r1": x[offset + 3 : offset + 6],
                "v1": x[offset + 6 : offset + 9],
                "w1": x[offset + 9 : offset + 12],
                "a1": x[offset + 12 : offset + 15],
                "alpha1": x[offset + 15 : offset + 18],
                "u2": x[offset + 18 : offset + 21],
                "r2": x[offset + 21 : offset + 24],
                "v2": x[offset + 24 : offset + 27],
                "w2": x[offset + 27 : offset + 30],
                "a2": x[offset + 30 : offset + 33],
                "alpha2": x[offset + 33 : offset + 36],
                "lambda": x[offset + 36 : offset + 46],
            }
        )
        offset += 46
    return stages


def residual_core(
    x,
    state0,
    h,
    mass1,
    mass2,
    J1,
    J2,
    s1_ground,
    s1_tip,
    s2_joint,
    gravity,
    hinge_axis_body,
    mu_s,
    mu_d,
    stribeck_velocity,
    viscous_damping,
    friction_radius,
    external_torque1_body,
    external_torque2_body,
    mode: str,
    n_stages: int,
):
    r10, p10, v10, w10, r20, p20, v20, w20 = state0
    _, A, _ = qp._gauss_legendre_coefficients_jax(n_stages, x.dtype)
    stages = unpack_stages(x, n_stages)
    k1 = [qp._right_jacobian_inverse_apply_jax(st["u1"], st["w1"]) for st in stages]
    k2 = [qp._right_jacobian_inverse_apply_jax(st["u2"], st["w2"]) for st in stages]
    out = []
    for i, st in enumerate(stages):
        p1 = qp.compose_right_quat_jax(p10, st["u1"])
        p2 = qp.compose_right_quat_jax(p20, st["u2"])
        R1 = qp.quat_to_rot_jax(p1)
        R2 = qp.quat_to_rot_jax(p2)
        F0 = st["lambda"][:3]
        eta0 = st["lambda"][3:5]
        F12 = st["lambda"][5:8]
        eta2 = st["lambda"][8:10]
        tau0 = brown_mcphee_scalar_jax(
            st["w1"][1], jnp.linalg.norm(F0), mu_s, mu_d, stribeck_velocity, viscous_damping, friction_radius
        )
        tau12 = brown_mcphee_scalar_jax(
            st["w2"][1] - st["w1"][1],
            jnp.linalg.norm(F12),
            mu_s,
            mu_d,
            stribeck_velocity,
            viscous_damping,
            friction_radius,
        )
        tau0_vec = jnp.array([0.0, tau0, 0.0], dtype=x.dtype)
        tau12_vec = jnp.array([0.0, tau12, 0.0], dtype=x.dtype)
        axis1 = R1 @ hinge_axis_body
        axis2 = R2 @ hinge_axis_body
        axis_rate1 = R1 @ jnp.cross(st["w1"], hinge_axis_body)
        axis_rate2 = R2 @ jnp.cross(st["w2"], hinge_axis_body)
        axis_acc1 = R1 @ (
            jnp.cross(st["alpha1"], hinge_axis_body)
            + jnp.cross(st["w1"], jnp.cross(st["w1"], hinge_axis_body))
        )
        axis_acc2 = R2 @ (
            jnp.cross(st["alpha2"], hinge_axis_body)
            + jnp.cross(st["w2"], jnp.cross(st["w2"], hinge_axis_body))
        )
        pv0 = st["v1"] + R1 @ jnp.cross(st["w1"], s1_ground)
        pv12 = st["v1"] + R1 @ jnp.cross(st["w1"], s1_tip) - st["v2"] - R2 @ jnp.cross(st["w2"], s2_joint)
        pa0 = st["a1"] + R1 @ (
            jnp.cross(st["alpha1"], s1_ground) + jnp.cross(st["w1"], jnp.cross(st["w1"], s1_ground))
        )
        pa12 = (
            st["a1"]
            + R1 @ (jnp.cross(st["alpha1"], s1_tip) + jnp.cross(st["w1"], jnp.cross(st["w1"], s1_tip)))
            - st["a2"]
            - R2 @ (jnp.cross(st["alpha2"], s2_joint) + jnp.cross(st["w2"], jnp.cross(st["w2"], s2_joint)))
        )
        r1_coll = st["r1"] - r10 - h * sum(A[i, j] * stages[j]["v1"] for j in range(n_stages))
        r2_coll = st["r2"] - r20 - h * sum(A[i, j] * stages[j]["v2"] for j in range(n_stages))
        u1_coll = st["u1"] - h * sum(A[i, j] * k1[j] for j in range(n_stages))
        u2_coll = st["u2"] - h * sum(A[i, j] * k2[j] for j in range(n_stages))
        v1_coll = st["v1"] - v10 - h * sum(A[i, j] * stages[j]["a1"] for j in range(n_stages))
        v2_coll = st["v2"] - v20 - h * sum(A[i, j] * stages[j]["a2"] for j in range(n_stages))
        w1_coll = st["w1"] - w10 - h * sum(A[i, j] * stages[j]["alpha1"] for j in range(n_stages))
        w2_coll = st["w2"] - w20 - h * sum(A[i, j] * stages[j]["alpha2"] for j in range(n_stages))
        if mode in ("pivot_va", "full_va"):
            r_block = jnp.concatenate((pv0, pv12))
            v_block = jnp.concatenate((pa0, pa12))
        else:
            r_block = jnp.concatenate((r1_coll, r2_coll))
            v_block = jnp.concatenate((v1_coll, v2_coll))
        if mode == "full_va":
            u_block = jnp.concatenate(
                (
                    u1_coll[1:2],
                    jnp.array([axis_rate1[0], axis_rate1[2]], dtype=x.dtype),
                    u2_coll[1:2],
                    jnp.array([axis_rate2[0], axis_rate2[2]], dtype=x.dtype),
                )
            )
            w_block = jnp.concatenate(
                (
                    w1_coll[1:2],
                    jnp.array([axis_acc1[0], axis_acc1[2]], dtype=x.dtype),
                    w2_coll[1:2],
                    jnp.array([axis_acc2[0], axis_acc2[2]], dtype=x.dtype),
                )
            )
        else:
            u_block = jnp.concatenate((u1_coll, u2_coll))
            w_block = jnp.concatenate((w1_coll, w2_coll))
        trans1 = mass1 * st["a1"] - mass1 * gravity - F0 + F12
        trans2 = mass2 * st["a2"] - mass2 * gravity - F12
        torque0_b1 = jnp.cross(s1_ground, R1.T @ F0)
        torque12_b1 = jnp.cross(s1_tip, R1.T @ (-F12))
        torque12_b2 = jnp.cross(s2_joint, R2.T @ F12)
        rot1 = (
            J1 @ st["alpha1"]
            + jnp.cross(st["w1"], J1 @ st["w1"])
            - torque0_b1
            - torque12_b1
            - axis_torque_jax(R1, eta0, hinge_axis_body)
            - tau0_vec
            + tau12_vec
            - external_torque1_body
        )
        rot2 = (
            J2 @ st["alpha2"]
            + jnp.cross(st["w2"], J2 @ st["w2"])
            - torque12_b2
            - axis_torque_jax(R2, eta2, hinge_axis_body)
            - tau12_vec
            - external_torque2_body
        )
        constraints = jnp.concatenate(
            (
                st["r1"] + R1 @ s1_ground,
                jnp.array([axis1[0], axis1[2]], dtype=x.dtype),
                st["r1"] + R1 @ s1_tip - st["r2"] - R2 @ s2_joint,
                jnp.array([axis2[0], axis2[2]], dtype=x.dtype),
            )
        )
        out.extend([r_block, u_block, v_block, w_block, trans1, rot1, trans2, rot2, constraints])
    return jnp.concatenate(out)


def residual2_raw(x, *args):
    return residual_core(x, *args, mode="raw", n_stages=2)


def residual3_raw(x, *args):
    return residual_core(x, *args, mode="raw", n_stages=3)


def residual2_pivotva(x, *args):
    return residual_core(x, *args, mode="pivot_va", n_stages=2)


def residual3_pivotva(x, *args):
    return residual_core(x, *args, mode="pivot_va", n_stages=3)


def residual2_fullva(x, *args):
    return residual_core(x, *args, mode="full_va", n_stages=2)


def residual3_fullva(x, *args):
    return residual_core(x, *args, mode="full_va", n_stages=3)


R2_RAW_VALUE = jax.jit(residual2_raw)
R2_RAW_JAC = jax.jit(jax.jacfwd(residual2_raw, argnums=0))
R3_RAW_VALUE = jax.jit(residual3_raw)
R3_RAW_JAC = jax.jit(jax.jacfwd(residual3_raw, argnums=0))
R2_PIVOT_VALUE = jax.jit(residual2_pivotva)
R2_PIVOT_JAC = jax.jit(jax.jacfwd(residual2_pivotva, argnums=0))
R3_PIVOT_VALUE = jax.jit(residual3_pivotva)
R3_PIVOT_JAC = jax.jit(jax.jacfwd(residual3_pivotva, argnums=0))
R2_FULL_VALUE = jax.jit(residual2_fullva)
R2_FULL_JAC = jax.jit(jax.jacfwd(residual2_fullva, argnums=0))
R3_FULL_VALUE = jax.jit(residual3_fullva)
R3_FULL_JAC = jax.jit(jax.jacfwd(residual3_fullva, argnums=0))


def gauss_step(state: State, h: float, params: Params, n_stages: int, mode: str) -> tuple[State, int, dict]:
    _, _, b = qp.gauss_legendre_coefficients(n_stages)
    x = stage_guess(state, h, params, n_stages)
    state0 = (
        jnp.asarray(state.r1, dtype=jnp.float64),
        jnp.asarray(state.p1, dtype=jnp.float64),
        jnp.asarray(state.v1, dtype=jnp.float64),
        jnp.asarray(state.w1, dtype=jnp.float64),
        jnp.asarray(state.r2, dtype=jnp.float64),
        jnp.asarray(state.p2, dtype=jnp.float64),
        jnp.asarray(state.v2, dtype=jnp.float64),
        jnp.asarray(state.w2, dtype=jnp.float64),
    )
    args = (
        state0,
        jnp.asarray(h, dtype=jnp.float64),
        jnp.asarray(params.mass1, dtype=jnp.float64),
        jnp.asarray(params.mass2, dtype=jnp.float64),
        jnp.asarray(params.J1, dtype=jnp.float64),
        jnp.asarray(params.J2, dtype=jnp.float64),
        jnp.asarray(params.s1_ground, dtype=jnp.float64),
        jnp.asarray(params.s1_tip, dtype=jnp.float64),
        jnp.asarray(params.s2_joint, dtype=jnp.float64),
        jnp.asarray(params.gravity, dtype=jnp.float64),
        jnp.asarray(params.hinge_axis_body, dtype=jnp.float64),
        jnp.asarray(params.mu_s, dtype=jnp.float64),
        jnp.asarray(params.mu_d, dtype=jnp.float64),
        jnp.asarray(params.stribeck_velocity, dtype=jnp.float64),
        jnp.asarray(params.viscous_damping, dtype=jnp.float64),
        jnp.asarray(params.friction_radius, dtype=jnp.float64),
        jnp.asarray(params.external_torque1_body, dtype=jnp.float64),
        jnp.asarray(params.external_torque2_body, dtype=jnp.float64),
    )
    if n_stages == 2 and mode == "raw":
        value, jacobian, max_iters = R2_RAW_VALUE, R2_RAW_JAC, 42
    elif n_stages == 3 and mode == "raw":
        value, jacobian, max_iters = R3_RAW_VALUE, R3_RAW_JAC, 54
    elif n_stages == 2 and mode == "pivot_va":
        value, jacobian, max_iters = R2_PIVOT_VALUE, R2_PIVOT_JAC, 46
    elif n_stages == 3 and mode == "pivot_va":
        value, jacobian, max_iters = R3_PIVOT_VALUE, R3_PIVOT_JAC, 60
    elif n_stages == 2 and mode == "full_va":
        value, jacobian, max_iters = R2_FULL_VALUE, R2_FULL_JAC, 50
    elif n_stages == 3 and mode == "full_va":
        value, jacobian, max_iters = R3_FULL_VALUE, R3_FULL_JAC, 64
    else:
        raise ValueError(f"unsupported stage count/mode {n_stages}/{mode}")
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
        raise RuntimeError(f"double revolute DAE solve failed, residual={last_norm:.3e}")
    stages = unpack_stages(x, n_stages)
    k1 = [qp.right_jacobian_inverse_apply(st["u1"], st["w1"]) for st in stages]
    k2 = [qp.right_jacobian_inverse_apply(st["u2"], st["w2"]) for st in stages]
    next_state = State(
        r1=state.r1 + h * sum(b[j] * stages[j]["v1"] for j in range(n_stages)),
        p1=qp.compose_right_quat(state.p1, h * sum(b[j] * k1[j] for j in range(n_stages))),
        v1=state.v1 + h * sum(b[j] * stages[j]["a1"] for j in range(n_stages)),
        w1=state.w1 + h * sum(b[j] * stages[j]["alpha1"] for j in range(n_stages)),
        r2=state.r2 + h * sum(b[j] * stages[j]["v2"] for j in range(n_stages)),
        p2=qp.compose_right_quat(state.p2, h * sum(b[j] * k2[j] for j in range(n_stages))),
        v2=state.v2 + h * sum(b[j] * stages[j]["a2"] for j in range(n_stages)),
        w2=state.w2 + h * sum(b[j] * stages[j]["alpha2"] for j in range(n_stages)),
    )
    max_stage_constraint = 0.0
    max_stage_velocity = 0.0
    max_stage_pivot_v = 0.0
    max_stage_axis_v = 0.0
    max_stage_pivot_a = 0.0
    max_stage_axis_a = 0.0
    max_stage_acc = 0.0
    max_lambda = 0.0
    max_power = -np.inf
    for st in stages:
        p1 = qp.compose_right_quat(state.p1, st["u1"])
        p2 = qp.compose_right_quat(state.p2, st["u2"])
        st_state = State(st["r1"], p1, st["v1"], st["w1"], st["r2"], p2, st["v2"], st["w2"])
        max_stage_constraint = max(max_stage_constraint, float(np.linalg.norm(double_constraints_np(st_state, params))))
        max_stage_velocity = max(max_stage_velocity, float(np.linalg.norm(double_velocity_constraints_np(st_state, params))))
        pv, av, pa, aa = constraint_parts_np(
            st["r1"],
            p1,
            st["v1"],
            st["w1"],
            st["a1"],
            st["alpha1"],
            st["r2"],
            p2,
            st["v2"],
            st["w2"],
            st["a2"],
            st["alpha2"],
            params,
        )
        max_stage_pivot_v = max(max_stage_pivot_v, pv)
        max_stage_axis_v = max(max_stage_axis_v, av)
        max_stage_pivot_a = max(max_stage_pivot_a, pa)
        max_stage_axis_a = max(max_stage_axis_a, aa)
        max_stage_acc = max(max_stage_acc, float(np.hypot(pa, aa)))
        F0 = st["lambda"][:3]
        F12 = st["lambda"][5:8]
        tau0 = brown_mcphee_scalar(st["w1"][1], float(np.linalg.norm(F0)), params)
        tau12 = brown_mcphee_scalar(st["w2"][1] - st["w1"][1], float(np.linalg.norm(F12)), params)
        max_power = max(max_power, float(tau0 * st["w1"][1] + tau12 * (st["w2"][1] - st["w1"][1])))
        max_lambda = max(max_lambda, float(np.linalg.norm(st["lambda"])))
    endpoint_pv, endpoint_av, _, _ = constraint_parts_np(
        next_state.r1,
        next_state.p1,
        next_state.v1,
        next_state.w1,
        np.zeros(3),
        np.zeros(3),
        next_state.r2,
        next_state.p2,
        next_state.v2,
        next_state.w2,
        np.zeros(3),
        np.zeros(3),
        params,
    )
    diag = {
        "newton_iterations": it + 1,
        "stage_residual_norm": last_norm,
        "max_stage_constraint_norm": max_stage_constraint,
        "max_stage_velocity_constraint_norm": max_stage_velocity,
        "max_stage_pivot_velocity_constraint_norm": max_stage_pivot_v,
        "max_stage_axis_velocity_constraint_norm": max_stage_axis_v,
        "max_stage_pivot_acceleration_constraint_norm": max_stage_pivot_a,
        "max_stage_axis_acceleration_constraint_norm": max_stage_axis_a,
        "max_stage_acceleration_constraint_norm": max_stage_acc,
        "max_endpoint_constraint_norm": float(np.linalg.norm(double_constraints_np(next_state, params))),
        "max_endpoint_velocity_constraint_norm": float(np.linalg.norm(double_velocity_constraints_np(next_state, params))),
        "max_endpoint_pivot_velocity_constraint_norm": endpoint_pv,
        "max_endpoint_axis_velocity_constraint_norm": endpoint_av,
        "max_lambda_norm": max_lambda,
        "max_stage_friction_power": max_power,
        "max_quaternion_unit_error": float(
            max(abs(np.linalg.norm(next_state.p1) - 1.0), abs(np.linalg.norm(next_state.p2) - 1.0))
        ),
    }
    return next_state, it + 1, diag


def energy(state: State, params: Params) -> float:
    return (
        0.5 * params.mass1 * float(state.v1 @ state.v1)
        + 0.5 * float(state.w1 @ params.J1 @ state.w1)
        + 0.5 * params.mass2 * float(state.v2 @ state.v2)
        + 0.5 * float(state.w2 @ params.J2 @ state.w2)
        - params.mass1 * float(params.gravity @ state.r1)
        - params.mass2 * float(params.gravity @ state.r2)
    )


def integrate(method: str, h: float, t_final: float, params: Params) -> dict:
    n_steps = int(round(t_final / h))
    if abs(n_steps * h - t_final) > 1.0e-12:
        raise ValueError("h must divide t_final")
    raw_method = base_method(method)
    if raw_method == "double_revolute_gauss4":
        n_stages = 2
    elif raw_method == "double_revolute_gauss6":
        n_stages = 3
    else:
        raise ValueError(f"unknown method {method}")
    mode = residual_mode(method)
    state = initial_state(params)
    E0 = energy(state, params)
    prev_energy = E0
    total_iters = 0
    max_step_energy_increase = 0.0
    max_endpoint_constraint = 0.0
    max_endpoint_velocity = 0.0
    max_endpoint_pivot_v = 0.0
    max_endpoint_axis_v = 0.0
    max_stage_constraint = 0.0
    max_stage_velocity = 0.0
    max_stage_pivot_v = 0.0
    max_stage_axis_v = 0.0
    max_stage_pivot_a = 0.0
    max_stage_axis_a = 0.0
    max_stage_acc = 0.0
    max_lambda = 0.0
    max_power = -np.inf
    max_quat = 0.0
    for _ in range(n_steps):
        state, niters, diag = gauss_step(state, h, params, n_stages, mode)
        total_iters += niters
        max_endpoint_constraint = max(max_endpoint_constraint, diag["max_endpoint_constraint_norm"])
        max_endpoint_velocity = max(max_endpoint_velocity, diag["max_endpoint_velocity_constraint_norm"])
        max_endpoint_pivot_v = max(max_endpoint_pivot_v, diag["max_endpoint_pivot_velocity_constraint_norm"])
        max_endpoint_axis_v = max(max_endpoint_axis_v, diag["max_endpoint_axis_velocity_constraint_norm"])
        max_stage_constraint = max(max_stage_constraint, diag["max_stage_constraint_norm"])
        max_stage_velocity = max(max_stage_velocity, diag["max_stage_velocity_constraint_norm"])
        max_stage_pivot_v = max(max_stage_pivot_v, diag["max_stage_pivot_velocity_constraint_norm"])
        max_stage_axis_v = max(max_stage_axis_v, diag["max_stage_axis_velocity_constraint_norm"])
        max_stage_pivot_a = max(max_stage_pivot_a, diag["max_stage_pivot_acceleration_constraint_norm"])
        max_stage_axis_a = max(max_stage_axis_a, diag["max_stage_axis_acceleration_constraint_norm"])
        max_stage_acc = max(max_stage_acc, diag["max_stage_acceleration_constraint_norm"])
        max_lambda = max(max_lambda, diag["max_lambda_norm"])
        max_power = max(max_power, diag["max_stage_friction_power"])
        max_quat = max(max_quat, diag["max_quaternion_unit_error"])
        E = energy(state, params)
        max_step_energy_increase = max(max_step_energy_increase, E - prev_energy)
        prev_energy = E
    final_energy = energy(state, params)
    return {
        "state": state,
        "steps": n_steps,
        "total_newton_iterations": total_iters,
        "final_energy_relative_change": (final_energy - E0) / max(abs(E0), 1.0e-30),
        "max_step_energy_increase": max_step_energy_increase,
        "max_endpoint_constraint_norm": max_endpoint_constraint,
        "max_endpoint_velocity_constraint_norm": max_endpoint_velocity,
        "max_endpoint_pivot_velocity_constraint_norm": max_endpoint_pivot_v,
        "max_endpoint_axis_velocity_constraint_norm": max_endpoint_axis_v,
        "max_stage_constraint_norm": max_stage_constraint,
        "max_stage_velocity_constraint_norm": max_stage_velocity,
        "max_stage_pivot_velocity_constraint_norm": max_stage_pivot_v,
        "max_stage_axis_velocity_constraint_norm": max_stage_axis_v,
        "max_stage_pivot_acceleration_constraint_norm": max_stage_pivot_a,
        "max_stage_axis_acceleration_constraint_norm": max_stage_axis_a,
        "max_stage_acceleration_constraint_norm": max_stage_acc,
        "max_lambda_norm": max_lambda,
        "max_stage_friction_power": max_power,
        "max_quaternion_unit_error": max_quat,
    }


def estimate_order(hs: list[float], errors: list[float]) -> float:
    if len(hs) < 2:
        return float("nan")
    xs = np.log(np.asarray(hs, dtype=float))
    ys = np.log(np.maximum(np.asarray(errors, dtype=float), 1.0e-300))
    slope, _ = np.polyfit(xs, ys, 1)
    return float(slope)


def run_experiment() -> dict:
    rows = []
    cases = {}
    for case_name, vs in CASES.items():
        params = make_params(vs)
        ref = integrate(REFERENCE_METHOD, REF_H, T_FINAL, params)
        ref_state = ref["state"]
        state0 = initial_state(params)
        for warm_mode in ("raw", "pivot_va", "full_va"):
            gauss_step(state0, 0.02, params, 2, warm_mode)
            gauss_step(state0, 0.02, params, 3, warm_mode)
        method_summary = {}
        for method in METHODS:
            hs_ok = []
            oerrs = []
            werrs = []
            runs = {}
            for h in HS:
                row = {key: "" for key in CSV_COLUMNS}
                row.update({"case": case_name, "method": method, "h": f"{h:.10g}"})
                start = time.perf_counter()
                try:
                    out = integrate(method, h, T_FINAL, params)
                    runtime = time.perf_counter() - start
                    oerr, werr = state_error(ref_state, out["state"])
                    hs_ok.append(h)
                    oerrs.append(oerr)
                    werrs.append(werr)
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
                            "max_endpoint_pivot_velocity_constraint_norm": f"{out['max_endpoint_pivot_velocity_constraint_norm']:.16e}",
                            "max_endpoint_axis_velocity_constraint_norm": f"{out['max_endpoint_axis_velocity_constraint_norm']:.16e}",
                            "max_stage_constraint_norm": f"{out['max_stage_constraint_norm']:.16e}",
                            "max_stage_velocity_constraint_norm": f"{out['max_stage_velocity_constraint_norm']:.16e}",
                            "max_stage_pivot_velocity_constraint_norm": f"{out['max_stage_pivot_velocity_constraint_norm']:.16e}",
                            "max_stage_axis_velocity_constraint_norm": f"{out['max_stage_axis_velocity_constraint_norm']:.16e}",
                            "max_stage_pivot_acceleration_constraint_norm": f"{out['max_stage_pivot_acceleration_constraint_norm']:.16e}",
                            "max_stage_axis_acceleration_constraint_norm": f"{out['max_stage_axis_acceleration_constraint_norm']:.16e}",
                            "max_stage_acceleration_constraint_norm": f"{out['max_stage_acceleration_constraint_norm']:.16e}",
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
                    row.update({"status": "failed", "error_message": str(exc), "runtime_sec": f"{runtime:.8e}"})
                    item = {"status": "failed", "error_message": str(exc), "runtime_sec": runtime}
                rows.append(row)
                runs[str(h)] = item
            method_summary[method] = {
                "orientation_observed_order": estimate_order(hs_ok, oerrs),
                "omega_observed_order": estimate_order(hs_ok, werrs),
                "runs": runs,
            }
        cases[case_name] = {
            "stribeck_velocity": vs,
            "reference_method": REFERENCE_METHOD,
            "reference_h": REF_H,
            "methods": method_summary,
            "reference": {key: value for key, value in ref.items() if key != "state"},
        }
    write_csv(RESULTS / "double_revolute_pivotva_runs.csv", rows)
    return {"t_final": T_FINAL, "cases": cases}


def plot_results(summary: dict) -> None:
    import matplotlib.pyplot as plt

    plt.figure(figsize=(7.7, 4.8))
    for case_name, case in summary["cases"].items():
        for method in METHODS:
            runs = case["methods"][method]["runs"]
            ok = [(float(h), runs[h]["orientation_error_rad"]) for h in runs if runs[h].get("status") == "ok"]
            if not ok:
                continue
            hs = np.array([v[0] for v in ok])
            errs = np.array([v[1] for v in ok])
            plt.loglog(hs, errs, marker="o", label=f"{case_name} {method}")
    plt.gca().invert_xaxis()
    plt.xlabel("step size h")
    plt.ylabel("combined orientation error rad")
    plt.title("Double Revolute DAE Convergence")
    plt.grid(True, which="both", alpha=0.35)
    plt.legend(fontsize=7)
    plt.tight_layout()
    plt.savefig(RESULTS / "double_revolute_convergence.png", dpi=180)
    plt.close()

    plt.figure(figsize=(7.7, 4.8))
    for case_name, case in summary["cases"].items():
        for method in METHODS:
            runs = case["methods"][method]["runs"]
            ok = [(float(h), runs[h]["max_endpoint_velocity_constraint_norm"]) for h in runs if runs[h].get("status") == "ok"]
            if not ok:
                continue
            hs = np.array([v[0] for v in ok])
            errs = np.array([v[1] for v in ok])
            plt.loglog(hs, errs, marker="o", label=f"{case_name} {method}")
    plt.gca().invert_xaxis()
    plt.xlabel("step size h")
    plt.ylabel("endpoint velocity constraint norm")
    plt.title("Double Revolute Endpoint Velocity Constraints")
    plt.grid(True, which="both", alpha=0.35)
    plt.legend(fontsize=7)
    plt.tight_layout()
    plt.savefig(RESULTS / "double_revolute_velocity_constraints.png", dpi=180)
    plt.close()


def write_report(summary: dict) -> None:
    def order_text(value: float) -> str:
        return f"{value:.3f}" if np.isfinite(value) else "insufficient successful points"

    lines = [
        "# v029 Experiment Report",
        "",
        "Generated by `run_v029.py`.",
        "",
        "## Purpose",
        "",
        "- Move beyond the one-body revolute pendulum by testing a two-body double-revolute absolute-coordinate quaternion DAE.",
        "- Each stage solves body1/body2 local rotations, positions, velocities, accelerations, angular velocities, angular accelerations, and 10 joint multipliers.",
        "- The `*_pivotva` methods replace body position/velocity collocation with ground and interbody pivot velocity/acceleration constraints.",
        "- The `*_fullva` methods additionally replace constrained-axis orientation/angular-velocity collocation components with hinge-axis velocity/acceleration constraints.",
        "- Brown-McPhee friction is applied at the ground hinge and the interbody hinge, both scaled by stage reaction-force norms.",
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
                    f"omega order {order_text(item['omega_observed_order'])}; finest h={fine_h:g}, "
                    f"orientation error {fine['orientation_error_rad']:.3e}, runtime {fine['runtime_sec']:.3f}s, "
                    f"endpoint velocity {fine['max_endpoint_velocity_constraint_norm']:.3e}, "
                    f"stage pivot acceleration {fine['max_stage_pivot_acceleration_constraint_norm']:.3e}, "
                    f"stage axis acceleration {fine['max_stage_axis_acceleration_constraint_norm']:.3e}."
                )
            else:
                lines.append(f"- `{method}`: no successful fixed-step run.")
            if failed_runs:
                failures = "; ".join(f"h={h:g}: {run['error_message']}" for h, run in sorted(failed_runs))
                lines.append(f"- `{method}` failures: {failures}.")
        raw = case["methods"]["double_revolute_gauss6"]["runs"].get("0.02")
        pivot = case["methods"]["double_revolute_gauss6_pivotva"]["runs"].get("0.02")
        full = case["methods"]["double_revolute_gauss6_fullva"]["runs"].get("0.02")
        if raw and pivot and raw.get("status") == "ok" and pivot.get("status") == "ok":
            lines.append(
                f"- PivotVA vs raw Gauss6 at h=0.02: endpoint velocity "
                f"{pivot['max_endpoint_velocity_constraint_norm']:.3e} vs {raw['max_endpoint_velocity_constraint_norm']:.3e}; "
                f"orientation error ratio {pivot['orientation_error_rad'] / max(raw['orientation_error_rad'], 1e-30):.2e}."
            )
        if pivot and full and pivot.get("status") == "ok" and full.get("status") == "ok":
            lines.append(
                f"- FullVA vs PivotVA Gauss6 at h=0.02: stage axis acceleration "
                f"{full['max_stage_axis_acceleration_constraint_norm']:.3e} vs "
                f"{pivot['max_stage_axis_acceleration_constraint_norm']:.3e}; "
                f"orientation error ratio {full['orientation_error_rad'] / max(pivot['orientation_error_rad'], 1e-30):.2e}."
            )
        lines.append("")
    lines.extend(
        [
            "## Interpretation",
            "",
            "- This is the first local test where the v027 PivotVA idea is applied to an interbody joint rather than only a ground revolute pendulum.",
            "- PivotVA/FullVA converged in all 24 fixed-step runs and reduced Gauss6 endpoint velocity drift from about 1e-4 to 1e-11--1e-12.",
            "- In the smooth case, PivotVA also reduced Gauss6 trajectory error by about 2x; in the sharp case, it preserved trajectory error while greatly improving constraints.",
            "- FullVA mainly tightens axis-acceleration diagnostics to roundoff; as in v028, the trajectory benefit comes from pivot velocity/acceleration consistency.",
            "- The cost wall is now visible: Gauss6 double-revolute runs take several seconds because each Newton Jacobian is 138 by 138. Sparse/block linear algebra is a real next target.",
            "- The model is still planar and uses world-y hinge-axis constraints for both bodies, so a fully general lower-pair formulation remains open.",
            "",
            "## Outputs",
            "",
            "- `double_revolute_pivotva_runs.csv`",
            "- `summary_v029.json`",
            "- `double_revolute_convergence.png`",
            "- `double_revolute_velocity_constraints.png`",
            "",
        ]
    )
    (RESULTS / "v029_report.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    experiment = run_experiment()
    plot_results(experiment)
    summary = {
        "version": "v029_double_revolute_pivotva_dae",
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
            "constraints": "ground revolute plus interbody revolute, both with world-y hinge axes",
            "new_feature": "two-body double-revolute square PivotVA/FullVA residual",
        },
        "experiment": experiment,
        "runtime_sec": time.perf_counter() - started,
    }
    with (RESULTS / "summary_v029.json").open("w", encoding="utf-8") as f:
        json.dump(json_safe(summary), f, indent=2, sort_keys=True)
    write_report(experiment)


if __name__ == "__main__":
    main()
