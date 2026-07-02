#!/usr/bin/env python3
"""Self-contained double-pendulum Gauss6/FullVA candidate runner.

This is a compact extraction of the local double-revolute FullVA row used for
the paper matrix. It intentionally avoids importing the v047, v048, or v029
research runners. The nonlinear residual is the ASME double-pendulum
specialization of the v029 FullVA residual with friction and external torques
set to zero, matching the local paper row.
"""

from __future__ import annotations

import csv
import json
import math
import time
from dataclasses import dataclass
from pathlib import Path

import jax

jax.config.update("jax_enable_x64", True)
import jax.numpy as jnp
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "results"

H_VALUES = (0.1, 0.05, 0.025)
REFERENCE_H = 0.0125
T_FINAL = 0.1
STAGES = 3
STAGE_SIZE = 46


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


def hat(w: np.ndarray) -> np.ndarray:
    x, y, z = np.asarray(w, dtype=float).reshape(3)
    return np.array([[0.0, -z, y], [z, 0.0, -x], [-y, x, 0.0]], dtype=float)


def hat_jax(w: jnp.ndarray) -> jnp.ndarray:
    return jnp.array(
        [[0.0, -w[2], w[1]], [w[2], 0.0, -w[0]], [-w[1], w[0], 0.0]],
        dtype=w.dtype,
    )


def quat_normalize(q: np.ndarray) -> np.ndarray:
    q = np.asarray(q, dtype=float).reshape(4)
    return q / np.linalg.norm(q)


def quat_mul(q: np.ndarray, p: np.ndarray) -> np.ndarray:
    q = np.asarray(q, dtype=float).reshape(4)
    p = np.asarray(p, dtype=float).reshape(4)
    q0, qv = q[0], q[1:4]
    p0, pv = p[0], p[1:4]
    return np.concatenate((np.array([q0 * p0 - float(qv @ pv)]), q0 * pv + p0 * qv + np.cross(qv, pv)))


def quat_exp(theta: np.ndarray) -> np.ndarray:
    theta = np.asarray(theta, dtype=float).reshape(3)
    angle = float(np.linalg.norm(theta))
    if angle < 1.0e-8:
        angle2 = angle * angle
        scalar = 1.0 - angle2 / 8.0 + angle2 * angle2 / 384.0
        b = 0.5 - angle2 / 48.0 + angle2 * angle2 / 3840.0
        return np.concatenate((np.array([scalar]), b * theta))
    return np.concatenate((np.array([math.cos(0.5 * angle)]), math.sin(0.5 * angle) / angle * theta))


def quat_to_rot(q: np.ndarray) -> np.ndarray:
    q = quat_normalize(q)
    w, x, y, z = q
    return np.array(
        [
            [1.0 - 2.0 * (y * y + z * z), 2.0 * (x * y - z * w), 2.0 * (x * z + y * w)],
            [2.0 * (x * y + z * w), 1.0 - 2.0 * (x * x + z * z), 2.0 * (y * z - x * w)],
            [2.0 * (x * z - y * w), 2.0 * (y * z + x * w), 1.0 - 2.0 * (x * x + y * y)],
        ],
        dtype=float,
    )


def compose_right_quat(q: np.ndarray, u: np.ndarray) -> np.ndarray:
    return quat_normalize(quat_mul(q, quat_exp(u)))


def quat_mul_jax(q: jnp.ndarray, p: jnp.ndarray) -> jnp.ndarray:
    q0, qv = q[0], q[1:4]
    p0, pv = p[0], p[1:4]
    return jnp.concatenate((jnp.array([q0 * p0 - qv @ pv], dtype=q.dtype), q0 * pv + p0 * qv + jnp.cross(qv, pv)))


def quat_exp_jax(theta: jnp.ndarray) -> jnp.ndarray:
    angle = jnp.linalg.norm(theta)
    angle2 = angle * angle
    scalar_small = 1.0 - angle2 / 8.0 + angle2 * angle2 / 384.0
    b_small = 0.5 - angle2 / 48.0 + angle2 * angle2 / 3840.0
    angle_safe = jnp.where(angle < 1.0e-8, 1.0, angle)
    scalar_large = jnp.cos(0.5 * angle_safe)
    b_large = jnp.sin(0.5 * angle_safe) / angle_safe
    scalar = jnp.where(angle < 1.0e-8, scalar_small, scalar_large)
    b = jnp.where(angle < 1.0e-8, b_small, b_large)
    return jnp.concatenate((jnp.array([scalar], dtype=theta.dtype), b * theta))


def compose_right_quat_jax(q: jnp.ndarray, u: jnp.ndarray) -> jnp.ndarray:
    out = quat_mul_jax(q, quat_exp_jax(u))
    return out / jnp.linalg.norm(out)


def quat_to_rot_jax(q: jnp.ndarray) -> jnp.ndarray:
    q = q / jnp.linalg.norm(q)
    w, x, y, z = q
    return jnp.array(
        [
            [1.0 - 2.0 * (y * y + z * z), 2.0 * (x * y - z * w), 2.0 * (x * z + y * w)],
            [2.0 * (x * y + z * w), 1.0 - 2.0 * (x * x + z * z), 2.0 * (y * z - x * w)],
            [2.0 * (x * z - y * w), 2.0 * (y * z + x * w), 1.0 - 2.0 * (x * x + y * y)],
        ],
        dtype=q.dtype,
    )


def right_jacobian_inverse_apply(u: np.ndarray, w: np.ndarray) -> np.ndarray:
    u = np.asarray(u, dtype=float).reshape(3)
    w = np.asarray(w, dtype=float).reshape(3)
    theta = float(np.linalg.norm(u))
    U = hat(u)
    if theta < 1.0e-7:
        coeff = 1.0 / 12.0 + theta * theta / 720.0
    else:
        coeff = 1.0 / (theta * theta) - (1.0 + math.cos(theta)) / (2.0 * theta * math.sin(theta))
    return (np.eye(3) + 0.5 * U + coeff * (U @ U)) @ w


def right_jacobian_inverse_apply_jax(u: jnp.ndarray, w: jnp.ndarray) -> jnp.ndarray:
    theta = jnp.linalg.norm(u)
    U = hat_jax(u)
    U2 = U @ U
    theta_safe = jnp.where(theta < 1.0e-7, 1.0, theta)
    coeff_small = 1.0 / 12.0 + theta * theta / 720.0
    coeff_large = 1.0 / (theta_safe * theta_safe) - (1.0 + jnp.cos(theta_safe)) / (
        2.0 * theta_safe * jnp.sin(theta_safe)
    )
    coeff = jnp.where(theta < 1.0e-7, coeff_small, coeff_large)
    return (jnp.eye(3, dtype=u.dtype) + 0.5 * U + coeff * U2) @ w


def gauss3() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    root15 = math.sqrt(15.0)
    c = np.array([0.5 - root15 / 10.0, 0.5, 0.5 + root15 / 10.0], dtype=float)
    A = np.array(
        [
            [5.0 / 36.0, 2.0 / 9.0 - root15 / 15.0, 5.0 / 36.0 - root15 / 30.0],
            [5.0 / 36.0 + root15 / 24.0, 2.0 / 9.0, 5.0 / 36.0 - root15 / 24.0],
            [5.0 / 36.0 + root15 / 30.0, 2.0 / 9.0 + root15 / 15.0, 5.0 / 36.0],
        ],
        dtype=float,
    )
    b = np.array([5.0 / 18.0, 4.0 / 9.0, 5.0 / 18.0], dtype=float)
    return c, A, b


def gauss3_jax(dtype) -> tuple[jnp.ndarray, jnp.ndarray, jnp.ndarray]:
    root15 = jnp.sqrt(jnp.array(15.0, dtype=dtype))
    c = jnp.array([0.5 - root15 / 10.0, 0.5, 0.5 + root15 / 10.0], dtype=dtype)
    A = jnp.array(
        [
            [5.0 / 36.0, 2.0 / 9.0 - root15 / 15.0, 5.0 / 36.0 - root15 / 30.0],
            [5.0 / 36.0 + root15 / 24.0, 2.0 / 9.0, 5.0 / 36.0 - root15 / 24.0],
            [5.0 / 36.0 + root15 / 30.0, 2.0 / 9.0 + root15 / 15.0, 5.0 / 36.0],
        ],
        dtype=dtype,
    )
    b = jnp.array([5.0 / 18.0, 4.0 / 9.0, 5.0 / 18.0], dtype=dtype)
    return c, A, b


def asme_bar_mass_inertia(length: float) -> tuple[float, float, float]:
    side = 0.05
    density = 7800.0
    mass = density * length * side * side
    j_length = (1.0 / 6.0) * mass * side * side
    j_transverse = (1.0 / 12.0) * mass * (side * side + length * length)
    return mass, j_length, j_transverse


def make_asme_params() -> Params:
    mass1, j1_length, j1_transverse = asme_bar_mass_inertia(4.0)
    mass2, j2_length, j2_transverse = asme_bar_mass_inertia(2.0)
    return Params(
        mass1=mass1,
        mass2=mass2,
        J1=np.diag([j1_transverse, j1_transverse, j1_length]),
        J2=np.diag([j2_transverse, j2_transverse, j2_length]),
        s1_ground=np.array([0.0, 0.0, 2.0], dtype=float),
        s1_tip=np.array([0.0, 0.0, -2.0], dtype=float),
        s2_joint=np.array([0.0, 0.0, 1.0], dtype=float),
        gravity=np.array([0.0, 0.0, -9.81], dtype=float),
        hinge_axis_body=np.array([0.0, 1.0, 0.0], dtype=float),
    )


def initial_state(params: Params) -> State:
    q1 = -0.5 * math.pi
    q2 = 0.0
    qd1 = 1.0e-12
    qd2 = -1.0e-12
    p1 = quat_exp(np.array([0.0, q1, 0.0], dtype=float))
    p2 = quat_exp(np.array([0.0, q2, 0.0], dtype=float))
    R1 = quat_to_rot(p1)
    R2 = quat_to_rot(p2)
    w1 = np.array([0.0, qd1, 0.0], dtype=float)
    w2 = np.array([0.0, qd2, 0.0], dtype=float)
    r1 = -R1 @ params.s1_ground
    v1 = -R1 @ np.cross(w1, params.s1_ground)
    r2 = r1 + R1 @ params.s1_tip - R2 @ params.s2_joint
    v2 = v1 + R1 @ np.cross(w1, params.s1_tip) - R2 @ np.cross(w2, params.s2_joint)
    return State(r1=r1, p1=p1, v1=v1, w1=w1, r2=r2, p2=p2, v2=v2, w2=w2)


def angle_from_quat(p: np.ndarray) -> float:
    R = quat_to_rot(p)
    return float(np.arctan2(R[0, 2], R[2, 2]))


def scalar_alpha_guess(q: float, mass: float, jyy: float, length: float) -> float:
    inertia = jyy + mass * length * length
    return float(-mass * 9.81 * length * math.sin(q) / inertia)


def stage_guess(state: State, h: float, params: Params) -> np.ndarray:
    c_nodes, _, _ = gauss3()
    q1 = angle_from_quat(state.p1)
    q2 = angle_from_quat(state.p2)
    qd1 = float(state.w1[1])
    qd2 = float(state.w2[1])
    a1_y = scalar_alpha_guess(q1, params.mass1, params.J1[1, 1], np.linalg.norm(params.s1_ground))
    a2_y = scalar_alpha_guess(q2, params.mass2, params.J2[1, 1], np.linalg.norm(params.s2_joint))
    blocks: list[np.ndarray] = []
    for ci in c_nodes:
        q1_i = q1 + float(ci) * h * qd1
        q2_i = q2 + float(ci) * h * qd2
        qd1_i = qd1 + float(ci) * h * a1_y
        qd2_i = qd2 + float(ci) * h * a2_y
        alpha1 = np.array([0.0, scalar_alpha_guess(q1_i, params.mass1, params.J1[1, 1], np.linalg.norm(params.s1_ground)), 0.0])
        alpha2 = np.array([0.0, scalar_alpha_guess(q2_i, params.mass2, params.J2[1, 1], np.linalg.norm(params.s2_joint)), 0.0])
        u1 = np.array([0.0, q1_i - q1, 0.0], dtype=float)
        u2 = np.array([0.0, q2_i - q2, 0.0], dtype=float)
        p1 = compose_right_quat(state.p1, u1)
        p2 = compose_right_quat(state.p2, u2)
        R1 = quat_to_rot(p1)
        R2 = quat_to_rot(p2)
        w1 = np.array([0.0, qd1_i, 0.0], dtype=float)
        w2 = np.array([0.0, qd2_i, 0.0], dtype=float)
        r1 = -R1 @ params.s1_ground
        v1 = -R1 @ np.cross(w1, params.s1_ground)
        a1 = -R1 @ (np.cross(alpha1, params.s1_ground) + np.cross(w1, np.cross(w1, params.s1_ground)))
        r2 = r1 + R1 @ params.s1_tip - R2 @ params.s2_joint
        v2 = v1 + R1 @ np.cross(w1, params.s1_tip) - R2 @ np.cross(w2, params.s2_joint)
        a2 = (
            a1
            + R1 @ (np.cross(alpha1, params.s1_tip) + np.cross(w1, np.cross(w1, params.s1_tip)))
            - R2 @ (np.cross(alpha2, params.s2_joint) + np.cross(w2, np.cross(w2, params.s2_joint)))
        )
        force12 = params.mass2 * (a2 - params.gravity)
        force0 = params.mass1 * (a1 - params.gravity) + force12
        lam = np.concatenate((force0, np.zeros(2), force12, np.zeros(2)))
        blocks.extend([u1, r1, v1, w1, a1, alpha1, u2, r2, v2, w2, a2, alpha2, lam])
    return np.concatenate(blocks)


def unpack_stages(x, n_stages: int = STAGES) -> list[dict[str, object]]:
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
        offset += STAGE_SIZE
    return stages


def axis_torque_jax(R: jnp.ndarray, eta: jnp.ndarray, hinge_axis_body: jnp.ndarray) -> jnp.ndarray:
    bx = jnp.array([1.0, 0.0, 0.0], dtype=R.dtype)
    bz = jnp.array([0.0, 0.0, 1.0], dtype=R.dtype)
    return eta[0] * jnp.cross(hinge_axis_body, R.T @ bx) + eta[1] * jnp.cross(hinge_axis_body, R.T @ bz)


def residual_fullva(
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
):
    r10, p10, v10, w10, r20, p20, v20, w20 = state0
    _, A, _ = gauss3_jax(x.dtype)
    stages = unpack_stages(x)
    k1 = [right_jacobian_inverse_apply_jax(st["u1"], st["w1"]) for st in stages]
    k2 = [right_jacobian_inverse_apply_jax(st["u2"], st["w2"]) for st in stages]
    out = []
    for i, st in enumerate(stages):
        p1 = compose_right_quat_jax(p10, st["u1"])
        p2 = compose_right_quat_jax(p20, st["u2"])
        R1 = quat_to_rot_jax(p1)
        R2 = quat_to_rot_jax(p2)
        force0 = st["lambda"][:3]
        eta0 = st["lambda"][3:5]
        force12 = st["lambda"][5:8]
        eta2 = st["lambda"][8:10]
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
        pivot_v0 = st["v1"] + R1 @ jnp.cross(st["w1"], s1_ground)
        pivot_v12 = st["v1"] + R1 @ jnp.cross(st["w1"], s1_tip) - st["v2"] - R2 @ jnp.cross(st["w2"], s2_joint)
        pivot_a0 = st["a1"] + R1 @ (
            jnp.cross(st["alpha1"], s1_ground) + jnp.cross(st["w1"], jnp.cross(st["w1"], s1_ground))
        )
        pivot_a12 = (
            st["a1"]
            + R1 @ (jnp.cross(st["alpha1"], s1_tip) + jnp.cross(st["w1"], jnp.cross(st["w1"], s1_tip)))
            - st["a2"]
            - R2 @ (jnp.cross(st["alpha2"], s2_joint) + jnp.cross(st["w2"], jnp.cross(st["w2"], s2_joint)))
        )
        u1_coll = st["u1"] - h * sum(A[i, j] * k1[j] for j in range(STAGES))
        u2_coll = st["u2"] - h * sum(A[i, j] * k2[j] for j in range(STAGES))
        w1_coll = st["w1"] - w10 - h * sum(A[i, j] * stages[j]["alpha1"] for j in range(STAGES))
        w2_coll = st["w2"] - w20 - h * sum(A[i, j] * stages[j]["alpha2"] for j in range(STAGES))
        trans1 = mass1 * st["a1"] - mass1 * gravity - force0 + force12
        trans2 = mass2 * st["a2"] - mass2 * gravity - force12
        torque0_b1 = jnp.cross(s1_ground, R1.T @ force0)
        torque12_b1 = jnp.cross(s1_tip, R1.T @ (-force12))
        torque12_b2 = jnp.cross(s2_joint, R2.T @ force12)
        rot1 = (
            J1 @ st["alpha1"]
            + jnp.cross(st["w1"], J1 @ st["w1"])
            - torque0_b1
            - torque12_b1
            - axis_torque_jax(R1, eta0, hinge_axis_body)
        )
        rot2 = (
            J2 @ st["alpha2"]
            + jnp.cross(st["w2"], J2 @ st["w2"])
            - torque12_b2
            - axis_torque_jax(R2, eta2, hinge_axis_body)
        )
        constraints = jnp.concatenate(
            (
                st["r1"] + R1 @ s1_ground,
                jnp.array([axis1[0], axis1[2]], dtype=x.dtype),
                st["r1"] + R1 @ s1_tip - st["r2"] - R2 @ s2_joint,
                jnp.array([axis2[0], axis2[2]], dtype=x.dtype),
            )
        )
        out.extend(
            [
                jnp.concatenate((pivot_v0, pivot_v12)),
                jnp.concatenate(
                    (
                        u1_coll[1:2],
                        jnp.array([axis_rate1[0], axis_rate1[2]], dtype=x.dtype),
                        u2_coll[1:2],
                        jnp.array([axis_rate2[0], axis_rate2[2]], dtype=x.dtype),
                    )
                ),
                jnp.concatenate((pivot_a0, pivot_a12)),
                jnp.concatenate(
                    (
                        w1_coll[1:2],
                        jnp.array([axis_acc1[0], axis_acc1[2]], dtype=x.dtype),
                        w2_coll[1:2],
                        jnp.array([axis_acc2[0], axis_acc2[2]], dtype=x.dtype),
                    )
                ),
                trans1,
                rot1,
                trans2,
                rot2,
                constraints,
            ]
        )
    return jnp.concatenate(out)


RES_VALUE = jax.jit(residual_fullva)
RES_JAC = jax.jit(jax.jacfwd(residual_fullva, argnums=0))


def double_constraints_np(state: State, params: Params) -> np.ndarray:
    R1 = quat_to_rot(state.p1)
    R2 = quat_to_rot(state.p2)
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
    R1 = quat_to_rot(state.p1)
    R2 = quat_to_rot(state.p2)
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
    R1 = quat_to_rot(p1)
    R2 = quat_to_rot(p2)
    pivot_v0 = v1 + R1 @ np.cross(w1, params.s1_ground)
    pivot_v12 = v1 + R1 @ np.cross(w1, params.s1_tip) - v2 - R2 @ np.cross(w2, params.s2_joint)
    axis_v1 = R1 @ np.cross(w1, params.hinge_axis_body)
    axis_v2 = R2 @ np.cross(w2, params.hinge_axis_body)
    pivot_a0 = a1 + R1 @ (np.cross(alpha1, params.s1_ground) + np.cross(w1, np.cross(w1, params.s1_ground)))
    pivot_a12 = (
        a1
        + R1 @ (np.cross(alpha1, params.s1_tip) + np.cross(w1, np.cross(w1, params.s1_tip)))
        - a2
        - R2 @ (np.cross(alpha2, params.s2_joint) + np.cross(w2, np.cross(w2, params.s2_joint)))
    )
    axis_a1 = R1 @ (
        np.cross(alpha1, params.hinge_axis_body) + np.cross(w1, np.cross(w1, params.hinge_axis_body))
    )
    axis_a2 = R2 @ (
        np.cross(alpha2, params.hinge_axis_body) + np.cross(w2, np.cross(w2, params.hinge_axis_body))
    )
    pivot_v = float(np.linalg.norm(np.concatenate((pivot_v0, pivot_v12))))
    axis_v = float(np.linalg.norm(np.array([axis_v1[0], axis_v1[2], axis_v2[0], axis_v2[2]])))
    pivot_a = float(np.linalg.norm(np.concatenate((pivot_a0, pivot_a12))))
    axis_a = float(np.linalg.norm(np.array([axis_a1[0], axis_a1[2], axis_a2[0], axis_a2[2]])))
    return pivot_v, axis_v, pivot_a, axis_a


def gauss_step(state: State, h: float, params: Params) -> tuple[State, int, dict[str, float]]:
    _, _, b = gauss3()
    x = stage_guess(state, h, params)
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
    )
    last_norm = float("inf")
    for iteration in range(64):
        x_jax = jnp.asarray(x, dtype=jnp.float64)
        res = np.asarray(RES_VALUE(x_jax, *args), dtype=float)
        last_norm = float(np.linalg.norm(res))
        if last_norm < 1.0e-11:
            break
        jac = np.asarray(RES_JAC(x_jax, *args), dtype=float)
        delta = np.linalg.solve(jac, -res)
        x = x + delta
        if float(np.linalg.norm(delta)) < 1.0e-11:
            last_norm = float(np.linalg.norm(np.asarray(RES_VALUE(jnp.asarray(x, dtype=jnp.float64), *args))))
            break
    else:
        raise RuntimeError(f"double-pendulum FullVA Newton solve failed: residual={last_norm:.3e}")

    stages = unpack_stages(x)
    k1 = [right_jacobian_inverse_apply(st["u1"], st["w1"]) for st in stages]
    k2 = [right_jacobian_inverse_apply(st["u2"], st["w2"]) for st in stages]
    next_state = State(
        r1=state.r1 + h * sum(float(b[j]) * stages[j]["v1"] for j in range(STAGES)),
        p1=compose_right_quat(state.p1, h * sum(float(b[j]) * k1[j] for j in range(STAGES))),
        v1=state.v1 + h * sum(float(b[j]) * stages[j]["a1"] for j in range(STAGES)),
        w1=state.w1 + h * sum(float(b[j]) * stages[j]["alpha1"] for j in range(STAGES)),
        r2=state.r2 + h * sum(float(b[j]) * stages[j]["v2"] for j in range(STAGES)),
        p2=compose_right_quat(state.p2, h * sum(float(b[j]) * k2[j] for j in range(STAGES))),
        v2=state.v2 + h * sum(float(b[j]) * stages[j]["a2"] for j in range(STAGES)),
        w2=state.w2 + h * sum(float(b[j]) * stages[j]["alpha2"] for j in range(STAGES)),
    )
    max_stage_constraint = 0.0
    max_stage_velocity = 0.0
    max_stage_acceleration = 0.0
    max_lambda = 0.0
    for st in stages:
        p1 = compose_right_quat(state.p1, st["u1"])
        p2 = compose_right_quat(state.p2, st["u2"])
        stage_state = State(st["r1"], p1, st["v1"], st["w1"], st["r2"], p2, st["v2"], st["w2"])
        max_stage_constraint = max(max_stage_constraint, float(np.linalg.norm(double_constraints_np(stage_state, params))))
        max_stage_velocity = max(max_stage_velocity, float(np.linalg.norm(double_velocity_constraints_np(stage_state, params))))
        _pv, _av, pivot_a, axis_a = constraint_parts_np(
            st["r1"], p1, st["v1"], st["w1"], st["a1"], st["alpha1"],
            st["r2"], p2, st["v2"], st["w2"], st["a2"], st["alpha2"], params
        )
        max_stage_acceleration = max(max_stage_acceleration, float(np.hypot(pivot_a, axis_a)))
        max_lambda = max(max_lambda, float(np.linalg.norm(st["lambda"])))
    diag = {
        "stage_residual_norm": last_norm,
        "max_stage_constraint_norm": max_stage_constraint,
        "max_stage_velocity_constraint_norm": max_stage_velocity,
        "max_stage_acceleration_constraint_norm": max_stage_acceleration,
        "max_endpoint_constraint_norm": float(np.linalg.norm(double_constraints_np(next_state, params))),
        "max_endpoint_velocity_constraint_norm": float(np.linalg.norm(double_velocity_constraints_np(next_state, params))),
        "max_lambda_norm": max_lambda,
        "max_quaternion_unit_error": float(
            max(abs(np.linalg.norm(next_state.p1) - 1.0), abs(np.linalg.norm(next_state.p2) - 1.0))
        ),
    }
    return next_state, iteration + 1, diag


def world_rotation() -> np.ndarray:
    return np.array([[0.0, -1.0, 0.0], [1.0, 0.0, 0.0], [0.0, 0.0, 1.0]], dtype=float)


def integrate_trajectory(h: float, t_final: float, params: Params) -> dict[str, object]:
    n_steps = int(round(t_final / h))
    if abs(n_steps * h - t_final) > 1.0e-12:
        raise ValueError("h must divide t_final")
    transform = world_rotation()
    state = initial_state(params)
    pos = np.zeros((2, 3, n_steps + 1))
    vel = np.zeros_like(pos)

    def record(index: int, current: State) -> None:
        pos[0, :, index] = transform @ current.r1
        pos[1, :, index] = transform @ current.r2
        vel[0, :, index] = transform @ current.v1
        vel[1, :, index] = transform @ current.v2

    record(0, state)
    total_newton = 0
    max_stage_residual = 0.0
    max_endpoint_constraint = 0.0
    max_endpoint_velocity = 0.0
    max_stage_acceleration = 0.0
    max_quat = 0.0
    for step in range(n_steps):
        state, niters, diag = gauss_step(state, h, params)
        total_newton += niters
        max_stage_residual = max(max_stage_residual, float(diag["stage_residual_norm"]))
        max_endpoint_constraint = max(max_endpoint_constraint, float(diag["max_endpoint_constraint_norm"]))
        max_endpoint_velocity = max(max_endpoint_velocity, float(diag["max_endpoint_velocity_constraint_norm"]))
        max_stage_acceleration = max(max_stage_acceleration, float(diag["max_stage_acceleration_constraint_norm"]))
        max_quat = max(max_quat, float(diag["max_quaternion_unit_error"]))
        record(step + 1, state)
    return {
        "h": h,
        "steps": n_steps,
        "pos": pos,
        "vel": vel,
        "total_newton_iterations": total_newton,
        "max_stage_residual_norm": max_stage_residual,
        "max_endpoint_constraint_norm": max_endpoint_constraint,
        "max_endpoint_velocity_constraint_norm": max_endpoint_velocity,
        "max_stage_acceleration_constraint_norm": max_stage_acceleration,
        "max_quaternion_unit_error": max_quat,
    }


def compare_nested(reference: dict[str, object], candidate: dict[str, object]) -> dict[str, float]:
    ratio = float(candidate["h"]) / float(reference["h"])
    stride = int(round(ratio))
    if not np.isclose(stride, ratio):
        raise ValueError("reference grid is not nested in candidate grid")
    ref_pos = np.asarray(reference["pos"])[:, :, ::stride]
    ref_vel = np.asarray(reference["vel"])[:, :, ::stride]
    cand_pos = np.asarray(candidate["pos"])
    cand_vel = np.asarray(candidate["vel"])
    pos_diff = cand_pos - ref_pos
    vel_diff = cand_vel - ref_vel
    return {
        "pos_traj_linf": float(np.max(np.abs(pos_diff))),
        "vel_traj_linf": float(np.max(np.abs(vel_diff))),
        "pos_final_linf": float(np.max(np.abs(pos_diff[:, :, -1]))),
        "vel_final_linf": float(np.max(np.abs(vel_diff[:, :, -1]))),
    }


def observed_order(hs: list[float], errors: list[float]) -> float:
    values = [(h, e) for h, e in zip(hs, errors, strict=True) if np.isfinite(e) and e > 0.0]
    if len(values) < 2:
        return float("nan")
    slope, _ = np.polyfit(np.log([item[0] for item in values]), np.log([item[1] for item in values]), 1)
    return float(slope)


def run(out_dir: Path) -> dict[str, object]:
    out_dir.mkdir(parents=True, exist_ok=True)
    params = make_asme_params()
    started_ref = time.perf_counter()
    reference = integrate_trajectory(REFERENCE_H, T_FINAL, params)
    reference_runtime = time.perf_counter() - started_ref
    rows: list[dict[str, object]] = []
    hs: list[float] = []
    pos_errors: list[float] = []
    vel_errors: list[float] = []
    for h in H_VALUES:
        started = time.perf_counter()
        candidate = integrate_trajectory(h, T_FINAL, params)
        runtime = time.perf_counter() - started
        err = compare_nested(reference, candidate)
        hs.append(h)
        pos_errors.append(err["pos_final_linf"])
        vel_errors.append(err["vel_final_linf"])
        rows.append(
            {
                "example": "double_pendulum",
                "method": "local_Gauss6_FullVA_double_only_candidate",
                "h": h,
                "t_end": T_FINAL,
                "reference_h": REFERENCE_H,
                "reference_policy": "local_fullva_h_0.0125_final_state",
                "steps": candidate["steps"],
                **err,
                "max_stage_residual_norm": candidate["max_stage_residual_norm"],
                "max_endpoint_constraint_norm": candidate["max_endpoint_constraint_norm"],
                "max_endpoint_velocity_constraint_norm": candidate["max_endpoint_velocity_constraint_norm"],
                "max_stage_acceleration_constraint_norm": candidate["max_stage_acceleration_constraint_norm"],
                "max_quaternion_unit_error": candidate["max_quaternion_unit_error"],
                "total_newton_iterations": candidate["total_newton_iterations"],
                "runtime_sec": runtime,
                "source_policy_external_superiority_allowed": False,
                "proof_gap_closed": False,
            }
        )
    pos_order = observed_order(hs, pos_errors)
    vel_order = observed_order(hs, vel_errors)
    for row in rows:
        row["position_order"] = pos_order
        row["velocity_order"] = vel_order

    csv_path = out_dir / "double_pendulum_rows.csv"
    fieldnames = list(rows[0].keys())
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    summary = {
        "schema": "cmame-p1-double-runner-candidate-v1",
        "status": "double_runner_candidate_not_source_policy_or_proof_complete",
        "example": "double_pendulum",
        "rows": len(rows),
        "h_values": list(H_VALUES),
        "reference_h": REFERENCE_H,
        "t_final": T_FINAL,
        "position_order": pos_order,
        "velocity_order": vel_order,
        "finest_position_error": pos_errors[-1],
        "finest_velocity_error": vel_errors[-1],
        "reference_runtime_sec": reference_runtime,
        "p1_double_only_ready": bool(len(rows) == 3 and pos_order > 5.0 and vel_order > 5.0),
        "p1_complete": False,
        "imports_v047_v048_or_v029": False,
        "source_policy_external_superiority_allowed": False,
        "proof_gap_closed": False,
    }
    (out_dir / "double_pendulum_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return summary


def main() -> int:
    summary = run(DEFAULT_OUT)
    ok = (
        summary["rows"] == 3
        and summary["p1_double_only_ready"] is True
        and summary["p1_complete"] is False
        and summary["imports_v047_v048_or_v029"] is False
        and summary["source_policy_external_superiority_allowed"] is False
        and summary["proof_gap_closed"] is False
    )
    print("p1_double_runner_candidate=PASS" if ok else "p1_double_runner_candidate=FAIL")
    print("example=double_pendulum")
    print(f"rows={summary['rows']}")
    print(f"position_order={float(summary['position_order']):.6f}")
    print(f"velocity_order={float(summary['velocity_order']):.6f}")
    print(f"finest_position_error={float(summary['finest_position_error']):.6e}")
    print(f"finest_velocity_error={float(summary['finest_velocity_error']):.6e}")
    print(f"p1_double_only_ready={summary['p1_double_only_ready']}")
    print(f"p1_complete={summary['p1_complete']}")
    print(f"imports_v047_v048_or_v029={summary['imports_v047_v048_or_v029']}")
    print(f"source_policy_external_superiority_allowed={summary['source_policy_external_superiority_allowed']}")
    print(f"local_runner_proof_gap_closed={summary['proof_gap_closed']}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
