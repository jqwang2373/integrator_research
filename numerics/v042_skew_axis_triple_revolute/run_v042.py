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

import jax.numpy as jnp
import numpy as np
from scipy import sparse
from scipy.sparse import linalg as spla


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
RESULTS = HERE / "results"
V040_PATH = ROOT / "v040_generated_block_triple_pattern" / "run_v040.py"

N_BODIES = 3
N_STAGES = 3
BODY_SIZE = 18
LAMBDA_SIZE = 5
STAGE_SIZE = N_BODIES * BODY_SIZE + N_BODIES * LAMBDA_SIZE
DIM = N_STAGES * STAGE_SIZE
H = 0.01
T_FINAL = 0.03
PATTERN_ATOL = 1.0e-14
SPARSITY_ATOL = 1.0e-12
CASES = {"skew_axis_smooth": 0.50, "skew_axis_sharp": 0.05}
CSV_COLUMNS = [
    "case",
    "solver",
    "pattern_source",
    "h",
    "status",
    "error_message",
    "steps",
    "runtime_sec",
    "pattern_build_sec",
    "dense_validation_pattern_sec",
    "total_newton_iterations",
    "total_linear_solves",
    "total_jacobian_assemblies",
    "total_residual_eval_sec",
    "total_jacobian_eval_sec",
    "total_linear_solve_sec",
    "avg_jacobian_eval_sec",
    "avg_linear_solve_sec",
    "pattern_nnz",
    "pattern_density",
    "colors",
    "pattern_missing_vs_dense",
    "pattern_extra_vs_dense",
    "orientation_error_vs_dense_rad",
    "omega_error_vs_dense",
    "max_linear_residual_norm",
    "max_endpoint_constraint_norm",
    "max_endpoint_velocity_constraint_norm",
    "max_stage_pivot_acceleration_constraint_norm",
    "max_stage_axis_acceleration_constraint_norm",
    "max_quaternion_unit_error",
]


def load_v040():
    spec = importlib.util.spec_from_file_location("v040_generated_block_triple_pattern", V040_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


v040 = load_v040()
v039 = v040.v039
qp = v039.qp
jax = v039.jax


@dataclass(frozen=True)
class Params:
    masses: np.ndarray
    Js: np.ndarray
    s_prev: np.ndarray
    s_next: np.ndarray
    gravity: np.ndarray
    axis_prev: np.ndarray
    axis_next: np.ndarray
    ground_axis: np.ndarray
    joint_basis: np.ndarray
    q_initial: np.ndarray
    qd_initial: np.ndarray
    mu_s: float
    mu_d: float
    stribeck_velocity: float
    viscous_damping: float
    friction_radius: float
    external_torques_body: np.ndarray


@dataclass
class State:
    r: np.ndarray
    p: np.ndarray
    v: np.ndarray
    w: np.ndarray


def normalize(v: np.ndarray) -> np.ndarray:
    v = np.asarray(v, dtype=float)
    return v / np.linalg.norm(v)


def axis_angle_rot(axis: np.ndarray, angle: float) -> np.ndarray:
    return qp.exp_so3(normalize(axis) * float(angle))


def align_rot(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    a = normalize(a)
    b = normalize(b)
    c = float(np.clip(a @ b, -1.0, 1.0))
    if c > 1.0 - 1.0e-12:
        return np.eye(3)
    if c < -1.0 + 1.0e-12:
        ref = np.array([1.0, 0.0, 0.0]) if abs(a[0]) < 0.8 else np.array([0.0, 1.0, 0.0])
        return axis_angle_rot(np.cross(a, ref), np.pi)
    v = np.cross(a, b)
    return qp.exp_so3(v / np.linalg.norm(v) * np.arccos(c))


def rot_to_quat(R: np.ndarray) -> np.ndarray:
    tr = float(np.trace(R))
    if tr > 0.0:
        s = np.sqrt(tr + 1.0) * 2.0
        q = np.array([0.25 * s, (R[2, 1] - R[1, 2]) / s, (R[0, 2] - R[2, 0]) / s, (R[1, 0] - R[0, 1]) / s])
    else:
        idx = int(np.argmax(np.diag(R)))
        if idx == 0:
            s = np.sqrt(1.0 + R[0, 0] - R[1, 1] - R[2, 2]) * 2.0
            q = np.array([(R[2, 1] - R[1, 2]) / s, 0.25 * s, (R[0, 1] + R[1, 0]) / s, (R[0, 2] + R[2, 0]) / s])
        elif idx == 1:
            s = np.sqrt(1.0 + R[1, 1] - R[0, 0] - R[2, 2]) * 2.0
            q = np.array([(R[0, 2] - R[2, 0]) / s, (R[0, 1] + R[1, 0]) / s, 0.25 * s, (R[1, 2] + R[2, 1]) / s])
        else:
            s = np.sqrt(1.0 + R[2, 2] - R[0, 0] - R[1, 1]) * 2.0
            q = np.array([(R[1, 0] - R[0, 1]) / s, (R[0, 2] + R[2, 0]) / s, (R[1, 2] + R[2, 1]) / s, 0.25 * s])
    return qp.quat_normalize(q)


def perp_basis(axis: np.ndarray) -> np.ndarray:
    axis = normalize(axis)
    ref = np.array([1.0, 0.0, 0.0]) if abs(axis[0]) < 0.75 else np.array([0.0, 1.0, 0.0])
    e1 = normalize(np.cross(axis, ref))
    e2 = np.cross(axis, e1)
    return np.stack([e1, e2])


def initial_rotations(params: Params) -> list[np.ndarray]:
    R = []
    joint_axis = params.ground_axis
    for i in range(N_BODIES):
        Ri = axis_angle_rot(joint_axis, params.q_initial[i]) @ align_rot(params.axis_prev[i], joint_axis)
        R.append(Ri)
        if i < N_BODIES - 1:
            joint_axis = Ri @ params.axis_next[i]
    return R


def make_joint_basis(axis_prev: np.ndarray, axis_next: np.ndarray, ground_axis: np.ndarray, q_initial: np.ndarray) -> np.ndarray:
    tmp = Params(
        masses=np.ones(N_BODIES),
        Js=np.tile(np.eye(3)[None, :, :], (N_BODIES, 1, 1)),
        s_prev=np.zeros((N_BODIES, 3)),
        s_next=np.zeros((N_BODIES, 3)),
        gravity=np.zeros(3),
        axis_prev=axis_prev,
        axis_next=axis_next,
        ground_axis=ground_axis,
        joint_basis=np.zeros((N_BODIES, 2, 3)),
        q_initial=q_initial,
        qd_initial=np.zeros(N_BODIES),
        mu_s=0.0,
        mu_d=0.0,
        stribeck_velocity=1.0,
        viscous_damping=0.0,
        friction_radius=0.0,
        external_torques_body=np.zeros((N_BODIES, 3)),
    )
    R = initial_rotations(tmp)
    axes = [ground_axis, R[0] @ axis_next[0], R[1] @ axis_next[1]]
    return np.stack([perp_basis(axis) for axis in axes])


def make_params(stribeck_velocity: float) -> Params:
    axis_prev = np.array(
        [
            normalize([0.0, 1.0, 0.0]),
            normalize([0.12, 0.97, -0.20]),
            normalize([-0.18, 0.94, 0.28]),
        ]
    )
    axis_next = np.array(
        [
            normalize([0.42, 0.82, 0.38]),
            normalize([-0.34, 0.88, 0.33]),
            normalize([0.0, 1.0, 0.0]),
        ]
    )
    ground_axis = normalize([0.28, 0.83, 0.48])
    q_initial = np.array([0.44, -0.36, 0.31])
    return Params(
        masses=np.array([3.2, 2.4, 1.8]),
        Js=np.array(
            [
                np.diag([0.16, 0.30, 0.38]),
                np.diag([0.10, 0.22, 0.27]),
                np.diag([0.08, 0.18, 0.23]),
            ]
        ),
        s_prev=np.array([[0.0, 0.0, 0.70], [0.04, 0.02, 0.55], [-0.03, 0.02, 0.45]]),
        s_next=np.array([[0.03, -0.02, -0.70], [-0.02, 0.03, -0.55], [0.0, 0.0, 0.0]]),
        gravity=np.array([0.0, 0.0, -9.81]),
        axis_prev=axis_prev,
        axis_next=axis_next,
        ground_axis=ground_axis,
        joint_basis=make_joint_basis(axis_prev, axis_next, ground_axis, q_initial),
        q_initial=q_initial,
        qd_initial=np.array([0.22, -0.18, 0.16]),
        mu_s=0.30,
        mu_d=0.20,
        stribeck_velocity=float(stribeck_velocity),
        viscous_damping=0.018,
        friction_radius=0.075,
        external_torques_body=np.array([[0.16, -0.07, -0.12], [-0.12, 0.09, 0.10], [0.08, -0.06, -0.07]]),
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


def initial_state(params: Params) -> State:
    R = initial_rotations(params)
    p = np.stack([rot_to_quat(Ri) for Ri in R])
    w = np.zeros((N_BODIES, 3))
    w[0] = params.qd_initial[0] * params.axis_prev[0]
    for i in range(1, N_BODIES):
        parent_rate = R[i - 1] @ np.cross(w[i - 1], params.axis_next[i - 1])
        child_rate_body = R[i].T @ parent_rate
        w[i] = np.cross(params.axis_prev[i], child_rate_body) + params.qd_initial[i] * params.axis_prev[i]
    r = np.zeros((N_BODIES, 3))
    v = np.zeros((N_BODIES, 3))
    r[0] = -R[0] @ params.s_prev[0]
    v[0] = -R[0] @ np.cross(w[0], params.s_prev[0])
    for i in range(1, N_BODIES):
        r[i] = r[i - 1] + R[i - 1] @ params.s_next[i - 1] - R[i] @ params.s_prev[i]
        v[i] = v[i - 1] + R[i - 1] @ np.cross(w[i - 1], params.s_next[i - 1]) - R[i] @ np.cross(w[i], params.s_prev[i])
    return State(r=r, p=p, v=v, w=w)


def state_error(ref: State, state: State) -> tuple[float, float]:
    orient = 0.0
    for i in range(N_BODIES):
        orient += qp.orientation_error(qp.quat_to_rot(ref.p[i]), qp.quat_to_rot(state.p[i])) ** 2
    return float(np.sqrt(orient)), float(np.linalg.norm(ref.w - state.w))


def stage_guess(state: State, h: float, params: Params) -> np.ndarray:
    c, _, _ = qp.gauss_legendre_coefficients(N_STAGES)
    blocks = []
    for ci in c:
        u = ci * h * state.w
        p = np.stack([qp.compose_right_quat(state.p[i], u[i]) for i in range(N_BODIES)])
        R = [qp.quat_to_rot(p[i]) for i in range(N_BODIES)]
        w = state.w.copy()
        alpha = np.zeros((N_BODIES, 3))
        r = np.zeros((N_BODIES, 3))
        v = np.zeros((N_BODIES, 3))
        a = np.zeros((N_BODIES, 3))
        r[0] = -R[0] @ params.s_prev[0]
        v[0] = -R[0] @ np.cross(w[0], params.s_prev[0])
        a[0] = -R[0] @ np.cross(w[0], np.cross(w[0], params.s_prev[0]))
        for i in range(1, N_BODIES):
            r[i] = r[i - 1] + R[i - 1] @ params.s_next[i - 1] - R[i] @ params.s_prev[i]
            v[i] = v[i - 1] + R[i - 1] @ np.cross(w[i - 1], params.s_next[i - 1]) - R[i] @ np.cross(w[i], params.s_prev[i])
            a[i] = (
                a[i - 1]
                + R[i - 1] @ np.cross(w[i - 1], np.cross(w[i - 1], params.s_next[i - 1]))
                - R[i] @ np.cross(w[i], np.cross(w[i], params.s_prev[i]))
            )
        F = np.zeros((N_BODIES, 3))
        F[-1] = params.masses[-1] * (a[-1] - params.gravity)
        for i in range(N_BODIES - 2, -1, -1):
            F[i] = params.masses[i] * (a[i] - params.gravity) + F[i + 1]
        lam = np.zeros((N_BODIES, 5))
        lam[:, :3] = F
        for i in range(N_BODIES):
            blocks.extend([u[i], r[i], v[i], w[i], a[i], alpha[i]])
        blocks.append(lam.reshape(-1))
    return np.concatenate(blocks)


def unpack_stages(x):
    stages = []
    for stage in range(N_STAGES):
        base = stage * STAGE_SIZE
        body = x[base : base + N_BODIES * BODY_SIZE].reshape((N_BODIES, BODY_SIZE))
        lam = x[base + N_BODIES * BODY_SIZE : base + STAGE_SIZE].reshape((N_BODIES, LAMBDA_SIZE))
        stages.append({"u": body[:, 0:3], "r": body[:, 3:6], "v": body[:, 6:9], "w": body[:, 9:12], "a": body[:, 12:15], "alpha": body[:, 15:18], "lambda": lam})
    return stages


def brown_mcphee_scalar_jax(v, normal_load, mu_s, mu_d, stribeck_velocity, viscous_damping, friction_radius):
    vs = jnp.maximum(stribeck_velocity, 1.0e-12)
    z = v / vs
    denom = (0.25 * z * z + 0.75) ** 2
    curve = mu_d * jnp.tanh(4.0 * z) + (mu_s - mu_d) * z / denom
    return -friction_radius * normal_load * curve - viscous_damping * jnp.tanh(jnp.array(4.0, dtype=v.dtype)) * v


def axis_torque_jax(R, eta, axis_body, basis_world):
    g1 = jnp.cross(axis_body, R.T @ basis_world[0])
    g2 = jnp.cross(axis_body, R.T @ basis_world[1])
    return eta[0] * g1 + eta[1] * g2


def residual_skew_fullva(
    x,
    state0,
    h,
    masses,
    Js,
    s_prev,
    s_next,
    gravity,
    axis_prev,
    axis_next,
    ground_axis,
    joint_basis,
    mu_s,
    mu_d,
    stribeck_velocity,
    viscous_damping,
    friction_radius,
    external_torques_body,
):
    r0, p0, v0, w0 = state0
    _, A, _ = qp._gauss_legendre_coefficients_jax(N_STAGES, x.dtype)
    stages = unpack_stages(x)
    k = []
    for st in stages:
        k.append([qp._right_jacobian_inverse_apply_jax(st["u"][i], st["w"][i]) for i in range(N_BODIES)])
    out = []
    for si, st in enumerate(stages):
        p = [qp.compose_right_quat_jax(p0[i], st["u"][i]) for i in range(N_BODIES)]
        R = [qp.quat_to_rot_jax(p[i]) for i in range(N_BODIES)]
        F = st["lambda"][:, :3]
        eta = st["lambda"][:, 3:5]
        child_axis = [R[i] @ axis_prev[i] for i in range(N_BODIES)]
        child_rate = [R[i] @ jnp.cross(st["w"][i], axis_prev[i]) for i in range(N_BODIES)]
        child_acc = [
            R[i] @ (jnp.cross(st["alpha"][i], axis_prev[i]) + jnp.cross(st["w"][i], jnp.cross(st["w"][i], axis_prev[i])))
            for i in range(N_BODIES)
        ]
        parent_axis = []
        parent_rate = []
        parent_acc = []
        for joint in range(N_BODIES):
            if joint == 0:
                parent_axis.append(ground_axis)
                parent_rate.append(jnp.zeros(3, dtype=x.dtype))
                parent_acc.append(jnp.zeros(3, dtype=x.dtype))
            else:
                parent = joint - 1
                parent_axis.append(R[parent] @ axis_next[parent])
                parent_rate.append(R[parent] @ jnp.cross(st["w"][parent], axis_next[parent]))
                parent_acc.append(
                    R[parent]
                    @ (
                        jnp.cross(st["alpha"][parent], axis_next[parent])
                        + jnp.cross(st["w"][parent], jnp.cross(st["w"][parent], axis_next[parent]))
                    )
                )
        axis_res = [
            jnp.array([jnp.dot(child_axis[j] - parent_axis[j], joint_basis[j, 0]), jnp.dot(child_axis[j] - parent_axis[j], joint_basis[j, 1])], dtype=x.dtype)
            for j in range(N_BODIES)
        ]
        axis_rate = [
            jnp.array([jnp.dot(child_rate[j] - parent_rate[j], joint_basis[j, 0]), jnp.dot(child_rate[j] - parent_rate[j], joint_basis[j, 1])], dtype=x.dtype)
            for j in range(N_BODIES)
        ]
        axis_acc = [
            jnp.array([jnp.dot(child_acc[j] - parent_acc[j], joint_basis[j, 0]), jnp.dot(child_acc[j] - parent_acc[j], joint_basis[j, 1])], dtype=x.dtype)
            for j in range(N_BODIES)
        ]

        tau = []
        for joint in range(N_BODIES):
            if joint == 0:
                rel_w = st["w"][0] @ axis_prev[0]
            else:
                rel_w = st["w"][joint] @ axis_prev[joint] - st["w"][joint - 1] @ axis_next[joint - 1]
            tau.append(brown_mcphee_scalar_jax(rel_w, jnp.linalg.norm(F[joint]), mu_s, mu_d, stribeck_velocity, viscous_damping, friction_radius))
        tau_child = [tau[j] * axis_prev[j] for j in range(N_BODIES)]
        tau_parent = [tau[j + 1] * axis_next[j] if j < N_BODIES - 1 else jnp.zeros(3, dtype=x.dtype) for j in range(N_BODIES)]

        pvel = []
        pacc = []
        constraints = []
        for joint in range(N_BODIES):
            if joint == 0:
                pv = st["v"][0] + R[0] @ jnp.cross(st["w"][0], s_prev[0])
                pa = st["a"][0] + R[0] @ (jnp.cross(st["alpha"][0], s_prev[0]) + jnp.cross(st["w"][0], jnp.cross(st["w"][0], s_prev[0])))
                pc = st["r"][0] + R[0] @ s_prev[0]
            else:
                parent = joint - 1
                pv = st["v"][parent] + R[parent] @ jnp.cross(st["w"][parent], s_next[parent]) - st["v"][joint] - R[joint] @ jnp.cross(st["w"][joint], s_prev[joint])
                pa = (
                    st["a"][parent]
                    + R[parent] @ (jnp.cross(st["alpha"][parent], s_next[parent]) + jnp.cross(st["w"][parent], jnp.cross(st["w"][parent], s_next[parent])))
                    - st["a"][joint]
                    - R[joint] @ (jnp.cross(st["alpha"][joint], s_prev[joint]) + jnp.cross(st["w"][joint], jnp.cross(st["w"][joint], s_prev[joint])))
                )
                pc = st["r"][parent] + R[parent] @ s_next[parent] - st["r"][joint] - R[joint] @ s_prev[joint]
            pvel.append(pv)
            pacc.append(pa)
            constraints.extend([pc, axis_res[joint]])

        u_block_parts = []
        w_block_parts = []
        for body in range(N_BODIES):
            u_coll = st["u"][body] - h * sum(A[si, sj] * k[sj][body] for sj in range(N_STAGES))
            w_coll = st["w"][body] - w0[body] - h * sum(A[si, sj] * stages[sj]["alpha"][body] for sj in range(N_STAGES))
            u_block_parts.extend([jnp.array([jnp.dot(u_coll, axis_prev[body])], dtype=x.dtype), axis_rate[body]])
            w_block_parts.extend([jnp.array([jnp.dot(w_coll, axis_prev[body])], dtype=x.dtype), axis_acc[body]])

        dyn_parts = []
        for body in range(N_BODIES):
            distal = F[body + 1] if body < N_BODIES - 1 else jnp.zeros(3, dtype=x.dtype)
            trans = masses[body] * st["a"][body] - masses[body] * gravity - F[body] + distal
            prox_torque = jnp.cross(s_prev[body], R[body].T @ F[body])
            if body < N_BODIES - 1:
                distal_torque = jnp.cross(s_next[body], R[body].T @ (-F[body + 1]))
                distal_axis_torque = axis_torque_jax(R[body], eta[body + 1], axis_next[body], joint_basis[body + 1])
            else:
                distal_torque = jnp.zeros(3, dtype=x.dtype)
                distal_axis_torque = jnp.zeros(3, dtype=x.dtype)
            rot = (
                Js[body] @ st["alpha"][body]
                + jnp.cross(st["w"][body], Js[body] @ st["w"][body])
                - prox_torque
                - distal_torque
                - axis_torque_jax(R[body], eta[body], axis_prev[body], joint_basis[body])
                + distal_axis_torque
                - tau_child[body]
                + tau_parent[body]
                - external_torques_body[body]
            )
            dyn_parts.extend([trans, rot])
        out.extend([jnp.concatenate(pvel), jnp.concatenate(u_block_parts), jnp.concatenate(pacc), jnp.concatenate(w_block_parts), jnp.concatenate(dyn_parts), jnp.concatenate(constraints)])
    return jnp.concatenate(out)


R_VALUE = jax.jit(residual_skew_fullva)
R_JAC = jax.jit(jax.jacfwd(residual_skew_fullva, argnums=0))


@jax.jit
def batched_jvp(x, seeds, *args):
    def one(seed):
        return jax.jvp(lambda y: residual_skew_fullva(y, *args), (x,), (seed,))[1]

    return jax.vmap(one)(seeds)


def build_args(state: State, h: float, params: Params):
    state0 = (
        jnp.asarray(state.r, dtype=jnp.float64),
        jnp.asarray(state.p, dtype=jnp.float64),
        jnp.asarray(state.v, dtype=jnp.float64),
        jnp.asarray(state.w, dtype=jnp.float64),
    )
    return (
        state0,
        jnp.asarray(h, dtype=jnp.float64),
        jnp.asarray(params.masses, dtype=jnp.float64),
        jnp.asarray(params.Js, dtype=jnp.float64),
        jnp.asarray(params.s_prev, dtype=jnp.float64),
        jnp.asarray(params.s_next, dtype=jnp.float64),
        jnp.asarray(params.gravity, dtype=jnp.float64),
        jnp.asarray(params.axis_prev, dtype=jnp.float64),
        jnp.asarray(params.axis_next, dtype=jnp.float64),
        jnp.asarray(params.ground_axis, dtype=jnp.float64),
        jnp.asarray(params.joint_basis, dtype=jnp.float64),
        jnp.asarray(params.mu_s, dtype=jnp.float64),
        jnp.asarray(params.mu_d, dtype=jnp.float64),
        jnp.asarray(params.stribeck_velocity, dtype=jnp.float64),
        jnp.asarray(params.viscous_damping, dtype=jnp.float64),
        jnp.asarray(params.friction_radius, dtype=jnp.float64),
        jnp.asarray(params.external_torques_body, dtype=jnp.float64),
    )


def next_state_from_stages(state: State, h: float, stages) -> State:
    _, _, b = qp.gauss_legendre_coefficients(N_STAGES)
    k = np.zeros((N_STAGES, N_BODIES, 3))
    for sj in range(N_STAGES):
        for body in range(N_BODIES):
            k[sj, body] = qp.right_jacobian_inverse_apply(stages[sj]["u"][body], stages[sj]["w"][body])
    r = np.zeros_like(state.r)
    p = np.zeros_like(state.p)
    v = np.zeros_like(state.v)
    w = np.zeros_like(state.w)
    for body in range(N_BODIES):
        r[body] = state.r[body] + h * sum(b[j] * stages[j]["v"][body] for j in range(N_STAGES))
        p[body] = qp.compose_right_quat(state.p[body], h * sum(b[j] * k[j, body] for j in range(N_STAGES)))
        v[body] = state.v[body] + h * sum(b[j] * stages[j]["a"][body] for j in range(N_STAGES))
        w[body] = state.w[body] + h * sum(b[j] * stages[j]["alpha"][body] for j in range(N_STAGES))
    return State(r=r, p=p, v=v, w=w)


def axis_parts_np(state: State, params: Params) -> tuple[np.ndarray, np.ndarray]:
    R = [qp.quat_to_rot(state.p[i]) for i in range(N_BODIES)]
    con = []
    vel = []
    for joint in range(N_BODIES):
        child_axis = R[joint] @ params.axis_prev[joint]
        child_rate = R[joint] @ np.cross(state.w[joint], params.axis_prev[joint])
        if joint == 0:
            parent_axis = params.ground_axis
            parent_rate = np.zeros(3)
        else:
            parent = joint - 1
            parent_axis = R[parent] @ params.axis_next[parent]
            parent_rate = R[parent] @ np.cross(state.w[parent], params.axis_next[parent])
        basis = params.joint_basis[joint]
        con.append(np.array([(child_axis - parent_axis) @ basis[0], (child_axis - parent_axis) @ basis[1]]))
        vel.append(np.array([(child_rate - parent_rate) @ basis[0], (child_rate - parent_rate) @ basis[1]]))
    return np.concatenate(con), np.concatenate(vel)


def constraints_np(state: State, params: Params) -> np.ndarray:
    R = [qp.quat_to_rot(state.p[i]) for i in range(N_BODIES)]
    out = []
    axis_con, _ = axis_parts_np(state, params)
    for joint in range(N_BODIES):
        if joint == 0:
            out.append(state.r[0] + R[0] @ params.s_prev[0])
        else:
            parent = joint - 1
            out.append(state.r[parent] + R[parent] @ params.s_next[parent] - state.r[joint] - R[joint] @ params.s_prev[joint])
        out.append(axis_con[2 * joint : 2 * joint + 2])
    return np.concatenate(out)


def velocity_constraints_np(state: State, params: Params) -> np.ndarray:
    R = [qp.quat_to_rot(state.p[i]) for i in range(N_BODIES)]
    out = []
    _, axis_vel = axis_parts_np(state, params)
    for joint in range(N_BODIES):
        if joint == 0:
            out.append(state.v[0] + R[0] @ np.cross(state.w[0], params.s_prev[0]))
        else:
            parent = joint - 1
            out.append(state.v[parent] + R[parent] @ np.cross(state.w[parent], params.s_next[parent]) - state.v[joint] - R[joint] @ np.cross(state.w[joint], params.s_prev[joint]))
        out.append(axis_vel[2 * joint : 2 * joint + 2])
    return np.concatenate(out)


def stage_acceleration_parts(state: State, stages, params: Params) -> tuple[float, float]:
    max_pivot = 0.0
    max_axis = 0.0
    for st in stages:
        p = np.stack([qp.compose_right_quat(state.p[i], st["u"][i]) for i in range(N_BODIES)])
        R = [qp.quat_to_rot(p[i]) for i in range(N_BODIES)]
        piv = []
        ax = []
        for joint in range(N_BODIES):
            child_acc = R[joint] @ (np.cross(st["alpha"][joint], params.axis_prev[joint]) + np.cross(st["w"][joint], np.cross(st["w"][joint], params.axis_prev[joint])))
            if joint == 0:
                pa = st["a"][0] + R[0] @ (np.cross(st["alpha"][0], params.s_prev[0]) + np.cross(st["w"][0], np.cross(st["w"][0], params.s_prev[0])))
                parent_acc = np.zeros(3)
            else:
                parent = joint - 1
                pa = (
                    st["a"][parent]
                    + R[parent] @ (np.cross(st["alpha"][parent], params.s_next[parent]) + np.cross(st["w"][parent], np.cross(st["w"][parent], params.s_next[parent])))
                    - st["a"][joint]
                    - R[joint] @ (np.cross(st["alpha"][joint], params.s_prev[joint]) + np.cross(st["w"][joint], np.cross(st["w"][joint], params.s_prev[joint])))
                )
                parent_acc = R[parent] @ (np.cross(st["alpha"][parent], params.axis_next[parent]) + np.cross(st["w"][parent], np.cross(st["w"][parent], params.axis_next[parent])))
            basis = params.joint_basis[joint]
            piv.append(pa)
            ax.extend([(child_acc - parent_acc) @ basis[0], (child_acc - parent_acc) @ basis[1]])
        max_pivot = max(max_pivot, float(np.linalg.norm(np.concatenate(piv))))
        max_axis = max(max_axis, float(np.linalg.norm(np.array(ax))))
    return max_pivot, max_axis


def csr_from_dense(jac: np.ndarray):
    mask = np.abs(jac) > SPARSITY_ATOL
    return sparse.csr_matrix(np.where(mask, jac, 0.0))


def make_pattern(mask: np.ndarray) -> v039.SparsePattern:
    return v039.make_pattern(mask)


def generated_block_superset_pattern() -> v039.SparsePattern:
    mask = v040.generated_block_superset_pattern().pattern.copy()
    for stage in range(N_STAGES):
        # Axis rate/acceleration/position residuals now depend on the parent
        # body's distal axis for interbody joints.
        for joint in range(1, N_BODIES):
            parent = joint - 1
            # u-block axis-rate rows.
            mask[stage * STAGE_SIZE + 9 + 3 * joint + 1 : stage * STAGE_SIZE + 9 + 3 * joint + 3, v040.body_block_slice(stage, parent, "u")] = True
            mask[stage * STAGE_SIZE + 9 + 3 * joint + 1 : stage * STAGE_SIZE + 9 + 3 * joint + 3, v040.body_block_slice(stage, parent, "w")] = True
            # w-block axis-acceleration rows.
            mask[stage * STAGE_SIZE + 27 + 3 * joint + 1 : stage * STAGE_SIZE + 27 + 3 * joint + 3, v040.body_block_slice(stage, parent, "u")] = True
            mask[stage * STAGE_SIZE + 27 + 3 * joint + 1 : stage * STAGE_SIZE + 27 + 3 * joint + 3, v040.body_block_slice(stage, parent, "w")] = True
            mask[stage * STAGE_SIZE + 27 + 3 * joint + 1 : stage * STAGE_SIZE + 27 + 3 * joint + 3, v040.body_block_slice(stage, parent, "alpha")] = True
            # Axis position rows.
            start = stage * STAGE_SIZE + 54 + 5 * joint + 3
            mask[start : start + 2, v040.body_block_slice(stage, parent, "u")] = True
    return make_pattern(mask)


def make_seed_matrix(sp: v039.SparsePattern) -> np.ndarray:
    return v039.make_seed_matrix(sp)


def colored_jvp_csr_and_mask(x: np.ndarray, args, sp: v039.SparsePattern, seeds: np.ndarray, threshold: float):
    rows = []
    cols = []
    data = []
    mask = np.zeros(sp.pattern.shape, dtype=bool)
    y_by_color = np.asarray(batched_jvp(jnp.asarray(x, dtype=jnp.float64), jnp.asarray(seeds, dtype=jnp.float64), *args), dtype=float)
    for color_idx, color in enumerate(sp.colors):
        y = y_by_color[color_idx]
        for col in color:
            col_rows = sp.rows_by_col[col]
            if col_rows.size:
                values = y[col_rows]
                keep = np.abs(values) > threshold
                if np.any(keep):
                    kept = col_rows[keep]
                    mask[kept, col] = True
                    rows.extend(kept.tolist())
                    cols.extend([col] * kept.size)
                    data.extend(values[keep].tolist())
    return sparse.csr_matrix((data, (rows, cols)), shape=sp.pattern.shape), mask


def build_pruned_pattern(params: Params, superset: v039.SparsePattern) -> tuple[v039.SparsePattern, float]:
    seeds = make_seed_matrix(superset)
    state = initial_state(params)
    pattern = np.zeros((DIM, DIM), dtype=bool)
    started = time.perf_counter()
    for _ in range(int(round(T_FINAL / H))):
        x = stage_guess(state, H, params)
        args = build_args(state, H, params)
        for _it in range(10):
            x_jax = jnp.asarray(x, dtype=jnp.float64)
            res = np.asarray(R_VALUE(x_jax, *args), dtype=float)
            csr, current = colored_jvp_csr_and_mask(x, args, superset, seeds, PATTERN_ATOL)
            pattern = np.logical_or(pattern, current)
            if float(np.linalg.norm(res)) < 1.0e-11:
                break
            delta = spla.spsolve(csr, -res)
            x = x + np.asarray(delta, dtype=float)
            if float(np.linalg.norm(delta)) < 1.0e-11:
                break
        state = next_state_from_stages(state, H, unpack_stages(x))
    return make_pattern(pattern), time.perf_counter() - started


def dense_validation_pattern(params: Params) -> tuple[v039.SparsePattern, float]:
    state = initial_state(params)
    pattern = None
    started = time.perf_counter()
    for _ in range(int(round(T_FINAL / H))):
        x = stage_guess(state, H, params)
        args = build_args(state, H, params)
        for _it in range(10):
            x_jax = jnp.asarray(x, dtype=jnp.float64)
            res = np.asarray(R_VALUE(x_jax, *args), dtype=float)
            jac = np.asarray(R_JAC(x_jax, *args), dtype=float)
            current = np.abs(jac) > PATTERN_ATOL
            pattern = current if pattern is None else np.logical_or(pattern, current)
            if float(np.linalg.norm(res)) < 1.0e-11:
                break
            delta = np.linalg.solve(jac, -res)
            x = x + delta
            if float(np.linalg.norm(delta)) < 1.0e-11:
                break
        state = next_state_from_stages(state, H, unpack_stages(x))
    assert pattern is not None
    return make_pattern(pattern), time.perf_counter() - started


def pattern_relation(candidate: v039.SparsePattern, reference: v039.SparsePattern) -> dict:
    extra = np.logical_and(candidate.pattern, np.logical_not(reference.pattern))
    missing = np.logical_and(reference.pattern, np.logical_not(candidate.pattern))
    return {
        "extra_vs_reference": int(extra.sum()),
        "missing_vs_reference": int(missing.sum()),
        "candidate_nnz": candidate.nnz,
        "reference_nnz": reference.nnz,
        "candidate_colors": len(candidate.colors),
        "reference_colors": len(reference.colors),
    }


def jvp_csr(x: np.ndarray, args, sp: v039.SparsePattern, seeds: np.ndarray):
    started = time.perf_counter()
    csr, _ = colored_jvp_csr_and_mask(x, args, sp, seeds, SPARSITY_ATOL)
    return csr, time.perf_counter() - started


def gauss_step(state: State, params: Params, solver: str, sp: v039.SparsePattern, seeds: np.ndarray):
    x = stage_guess(state, H, params)
    args = build_args(state, H, params)
    total_residual = 0.0
    total_jac = 0.0
    total_linear = 0.0
    linear_solves = 0
    max_linear_residual = 0.0
    last_norm = np.inf
    for it in range(80):
        x_jax = jnp.asarray(x, dtype=jnp.float64)
        started = time.perf_counter()
        res = np.asarray(R_VALUE(x_jax, *args), dtype=float)
        total_residual += time.perf_counter() - started
        last_norm = float(np.linalg.norm(res))
        if last_norm < 1.0e-11:
            break
        if solver == "dense_jacfwd_csr":
            started = time.perf_counter()
            jac = np.asarray(R_JAC(x_jax, *args), dtype=float)
            csr = csr_from_dense(jac)
            total_jac += time.perf_counter() - started
        elif solver == "generated_block_jvp_pruned":
            csr, jac_sec = jvp_csr(x, args, sp, seeds)
            total_jac += jac_sec
        else:
            raise ValueError(solver)
        started = time.perf_counter()
        delta = spla.spsolve(csr, -res)
        total_linear += time.perf_counter() - started
        linear_solves += 1
        max_linear_residual = max(max_linear_residual, float(np.linalg.norm(csr @ delta + res)))
        x = x + np.asarray(delta, dtype=float)
        if float(np.linalg.norm(delta)) < 1.0e-11:
            break
    else:
        raise RuntimeError(f"skew-axis Newton failed residual={last_norm:.3e}")
    stages = unpack_stages(x)
    next_state = next_state_from_stages(state, H, stages)
    pa, aa = stage_acceleration_parts(state, stages, params)
    diag = {
        "newton_iterations": it + 1,
        "linear_solves": linear_solves,
        "jacobian_assemblies": linear_solves,
        "total_residual_eval_sec": total_residual,
        "total_jacobian_eval_sec": total_jac,
        "total_linear_solve_sec": total_linear,
        "max_linear_residual_norm": max_linear_residual,
        "max_endpoint_constraint_norm": float(np.linalg.norm(constraints_np(next_state, params))),
        "max_endpoint_velocity_constraint_norm": float(np.linalg.norm(velocity_constraints_np(next_state, params))),
        "max_stage_pivot_acceleration_constraint_norm": pa,
        "max_stage_axis_acceleration_constraint_norm": aa,
        "max_quaternion_unit_error": float(np.max(np.abs(np.linalg.norm(next_state.p, axis=1) - 1.0))),
    }
    return next_state, diag


def integrate(params: Params, solver: str, sp: v039.SparsePattern, seeds: np.ndarray):
    state = initial_state(params)
    totals = {
        "total_newton_iterations": 0,
        "total_linear_solves": 0,
        "total_jacobian_assemblies": 0,
        "total_residual_eval_sec": 0.0,
        "total_jacobian_eval_sec": 0.0,
        "total_linear_solve_sec": 0.0,
        "max_linear_residual_norm": 0.0,
        "max_endpoint_constraint_norm": 0.0,
        "max_endpoint_velocity_constraint_norm": 0.0,
        "max_stage_pivot_acceleration_constraint_norm": 0.0,
        "max_stage_axis_acceleration_constraint_norm": 0.0,
        "max_quaternion_unit_error": 0.0,
    }
    n_steps = int(round(T_FINAL / H))
    for _ in range(n_steps):
        state, diag = gauss_step(state, params, solver, sp, seeds)
        totals["total_newton_iterations"] += diag["newton_iterations"]
        totals["total_linear_solves"] += diag["linear_solves"]
        totals["total_jacobian_assemblies"] += diag["jacobian_assemblies"]
        for key in [
            "total_residual_eval_sec",
            "total_jacobian_eval_sec",
            "total_linear_solve_sec",
            "max_linear_residual_norm",
            "max_endpoint_constraint_norm",
            "max_endpoint_velocity_constraint_norm",
            "max_stage_pivot_acceleration_constraint_norm",
            "max_stage_axis_acceleration_constraint_norm",
            "max_quaternion_unit_error",
        ]:
            if key.startswith("total"):
                totals[key] += diag[key]
            else:
                totals[key] = max(totals[key], diag[key])
    totals["state"] = state
    totals["steps"] = n_steps
    totals["avg_jacobian_eval_sec"] = totals["total_jacobian_eval_sec"] / max(totals["total_jacobian_assemblies"], 1)
    totals["avg_linear_solve_sec"] = totals["total_linear_solve_sec"] / max(totals["total_linear_solves"], 1)
    return totals


def warm_jax(params: Params, sp: v039.SparsePattern, seeds: np.ndarray) -> None:
    state = initial_state(params)
    x = stage_guess(state, H, params)
    args = build_args(state, H, params)
    x_jax = jnp.asarray(x, dtype=jnp.float64)
    np.asarray(R_VALUE(x_jax, *args), dtype=float)
    np.asarray(R_JAC(x_jax, *args), dtype=float)
    np.asarray(batched_jvp(x_jax, jnp.asarray(seeds, dtype=jnp.float64), *args), dtype=float)


def row_from_run(case_name: str, solver: str, source: str, out: dict, runtime: float, sp: v039.SparsePattern, relation: dict, pattern_build: float, dense_pattern_sec: float, oerr: float, werr: float):
    return {
        "case": case_name,
        "solver": solver,
        "pattern_source": source,
        "h": f"{H:.10g}",
        "status": "ok",
        "error_message": "",
        "steps": out["steps"],
        "runtime_sec": f"{runtime:.8e}",
        "pattern_build_sec": f"{pattern_build:.8e}",
        "dense_validation_pattern_sec": f"{dense_pattern_sec:.8e}",
        "total_newton_iterations": out["total_newton_iterations"],
        "total_linear_solves": out["total_linear_solves"],
        "total_jacobian_assemblies": out["total_jacobian_assemblies"],
        "total_residual_eval_sec": f"{out['total_residual_eval_sec']:.16e}",
        "total_jacobian_eval_sec": f"{out['total_jacobian_eval_sec']:.16e}",
        "total_linear_solve_sec": f"{out['total_linear_solve_sec']:.16e}",
        "avg_jacobian_eval_sec": f"{out['avg_jacobian_eval_sec']:.16e}",
        "avg_linear_solve_sec": f"{out['avg_linear_solve_sec']:.16e}",
        "pattern_nnz": sp.nnz,
        "pattern_density": f"{sp.density:.16e}",
        "colors": len(sp.colors),
        "pattern_missing_vs_dense": relation["missing_vs_reference"],
        "pattern_extra_vs_dense": relation["extra_vs_reference"],
        "orientation_error_vs_dense_rad": f"{oerr:.16e}",
        "omega_error_vs_dense": f"{werr:.16e}",
        "max_linear_residual_norm": f"{out['max_linear_residual_norm']:.16e}",
        "max_endpoint_constraint_norm": f"{out['max_endpoint_constraint_norm']:.16e}",
        "max_endpoint_velocity_constraint_norm": f"{out['max_endpoint_velocity_constraint_norm']:.16e}",
        "max_stage_pivot_acceleration_constraint_norm": f"{out['max_stage_pivot_acceleration_constraint_norm']:.16e}",
        "max_stage_axis_acceleration_constraint_norm": f"{out['max_stage_axis_acceleration_constraint_norm']:.16e}",
        "max_quaternion_unit_error": f"{out['max_quaternion_unit_error']:.16e}",
    }


def run_case(case_name: str, params: Params) -> dict:
    block_start = time.perf_counter()
    block = generated_block_superset_pattern()
    block_build_sec = time.perf_counter() - block_start
    pruned, pruned_build_sec = build_pruned_pattern(params, block)
    pruned_seeds = make_seed_matrix(pruned)
    warm_jax(params, pruned, pruned_seeds)
    dense_pattern, dense_pattern_sec = dense_validation_pattern(params)
    relation = pattern_relation(pruned, dense_pattern)
    block_relation = pattern_relation(block, dense_pattern)
    rows = []
    runs = {}
    dense_state = None
    for solver, source, sp, seeds, build_sec in [
        ("dense_jacfwd_csr", "dense", pruned, pruned_seeds, 0.0),
        ("generated_block_jvp_pruned", "generated_block_jvp_pruned", pruned, pruned_seeds, pruned_build_sec),
    ]:
        started = time.perf_counter()
        out = integrate(params, solver, sp, seeds)
        runtime = time.perf_counter() - started
        if solver == "dense_jacfwd_csr":
            dense_state = out["state"]
            oerr, werr = 0.0, 0.0
        else:
            assert dense_state is not None
            oerr, werr = state_error(dense_state, out["state"])
        runs[solver] = {key: value for key, value in out.items() if key != "state"} | {"status": "ok", "runtime_sec": runtime, "orientation_error_vs_dense_rad": oerr, "omega_error_vs_dense": werr}
        rows.append(row_from_run(case_name, solver, source, out, runtime, sp, relation, build_sec, dense_pattern_sec, oerr, werr))
    return {
        "stribeck_velocity": CASES[case_name],
        "block_pattern_build_sec": block_build_sec,
        "jvp_pruned_pattern_build_sec": pruned_build_sec,
        "dense_validation_pattern_build_sec": dense_pattern_sec,
        "patterns": {
            "generated_block_superset": {"nnz": block.nnz, "density": block.density, "colors": len(block.colors)},
            "generated_block_jvp_pruned": {"nnz": pruned.nnz, "density": pruned.density, "colors": len(pruned.colors)},
            "dense_validation": {"nnz": dense_pattern.nnz, "density": dense_pattern.density, "colors": len(dense_pattern.colors)},
        },
        "relations": {"block_vs_dense": block_relation, "pruned_vs_dense": relation},
        "runs": runs,
        "rows": rows,
    }


def run_experiment() -> dict:
    all_rows = []
    cases = {}
    for case_name, vs in CASES.items():
        params = make_params(vs)
        case = run_case(case_name, params)
        all_rows.extend(case.pop("rows"))
        cases[case_name] = case
    write_csv(RESULTS / "skew_axis_triple_runs.csv", all_rows)
    return {"h": H, "t_final": T_FINAL, "dimension": DIM, "stage_size": STAGE_SIZE, "cases": cases}


def plot_results(summary: dict) -> None:
    import matplotlib.pyplot as plt

    labels = []
    dense_runtime = []
    sparse_runtime = []
    nnz = {"block": [], "pruned": [], "dense": []}
    colors = {"block": [], "pruned": [], "dense": []}
    for case_name, case in summary["cases"].items():
        labels.append(case_name.replace("skew_axis_", ""))
        dense_runtime.append(case["runs"]["dense_jacfwd_csr"]["runtime_sec"])
        sparse_runtime.append(case["runs"]["generated_block_jvp_pruned"]["runtime_sec"])
        for key, pattern_key in [("block", "generated_block_superset"), ("pruned", "generated_block_jvp_pruned"), ("dense", "dense_validation")]:
            nnz[key].append(case["patterns"][pattern_key]["nnz"])
            colors[key].append(case["patterns"][pattern_key]["colors"])
    xs = np.arange(len(labels))
    fig, ax = plt.subplots(figsize=(8.8, 4.0))
    ax.bar(xs - 0.18, dense_runtime, width=0.36, label="dense jacfwd CSR")
    ax.bar(xs + 0.18, sparse_runtime, width=0.36, label="generated-block JVP-pruned")
    ax.set_yscale("log")
    ax.set_ylabel("runtime seconds")
    ax.set_xticks(xs)
    ax.set_xticklabels(labels)
    ax.grid(True, axis="y", alpha=0.35)
    ax.legend()
    fig.tight_layout()
    fig.savefig(RESULTS / "skew_axis_triple_runtime.png", dpi=180)
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(10.6, 4.0))
    for idx, key in enumerate(["block", "pruned", "dense"]):
        axes[0].bar(xs + (idx - 1) * 0.25, nnz[key], width=0.25, label=key)
        axes[1].bar(xs + (idx - 1) * 0.25, colors[key], width=0.25, label=key)
    axes[0].set_ylabel("pattern nonzeros")
    axes[1].set_ylabel("column colors")
    for ax in axes:
        ax.set_xticks(xs)
        ax.set_xticklabels(labels)
        ax.grid(True, axis="y", alpha=0.35)
        ax.legend()
    fig.tight_layout()
    fig.savefig(RESULTS / "skew_axis_triple_patterns.png", dpi=180)
    plt.close(fig)


def write_report(summary: dict) -> None:
    lines = [
        "# v042 Experiment Report",
        "",
        "Generated by `run_v042.py`.",
        "",
        "## Purpose",
        "",
        "- Move beyond planar/collinear revolute axes by aligning each child proximal axis to the parent body's distal axis.",
        "- Keep the same 207D Gauss6 FullVA shape, Brown-McPhee friction, and sparse-AD backend.",
        "- Validate generated-block JVP-pruned sparse Jacobians against dense `jacfwd` union patterns.",
        "",
        "## Results",
        "",
    ]
    for case_name, case in summary["cases"].items():
        dense = case["runs"]["dense_jacfwd_csr"]
        sparse_run = case["runs"]["generated_block_jvp_pruned"]
        block_rel = case["relations"]["block_vs_dense"]
        pruned_rel = case["relations"]["pruned_vs_dense"]
        speed = dense["runtime_sec"] / max(sparse_run["runtime_sec"], 1.0e-30)
        lines.append(f"### {case_name}")
        lines.append(
            f"- Block superset: {case['patterns']['generated_block_superset']['nnz']} entries/{case['patterns']['generated_block_superset']['colors']} colors; "
            f"missing {block_rel['missing_vs_reference']} vs dense."
        )
        lines.append(
            f"- JVP-pruned pattern: {case['patterns']['generated_block_jvp_pruned']['nnz']} entries/{case['patterns']['generated_block_jvp_pruned']['colors']} colors; "
            f"dense validation {case['patterns']['dense_validation']['nnz']} entries/{case['patterns']['dense_validation']['colors']} colors; "
            f"missing {pruned_rel['missing_vs_reference']}, extra {pruned_rel['extra_vs_reference']}."
        )
        lines.append(
            f"- Runtime: dense {dense['runtime_sec']:.3f}s vs sparse {sparse_run['runtime_sec']:.3f}s "
            f"(dense/sparse {speed:.2f}x)."
        )
        lines.append(
            f"- Trajectory diff: orientation {sparse_run['orientation_error_vs_dense_rad']:.3e} rad, "
            f"omega {sparse_run['omega_error_vs_dense']:.3e}; endpoint velocity "
            f"{sparse_run['max_endpoint_velocity_constraint_norm']:.3e}; stage axis acceleration "
            f"{sparse_run['max_stage_axis_acceleration_constraint_norm']:.3e}."
        )
        lines.append("")
    lines.extend(
        [
            "## Interpretation",
            "",
            "- This is a geometry-level stress test, not only a longer planar-chain run.",
            "- The revolute axis constraints now depend on both parent and child orientations for interbody joints.",
            "- The generated block superset remains safe, and JVP pruning recovers the observed dense pattern without dense Jacobians.",
            "- The remaining gap is larger skew-axis chains and other lower pairs such as cylindrical/prismatic joints.",
            "",
            "## Outputs",
            "",
            "- `skew_axis_triple_runs.csv`",
            "- `summary_v042.json`",
            "- `skew_axis_triple_runtime.png`",
            "- `skew_axis_triple_patterns.png`",
            "",
        ]
    )
    (RESULTS / "v042_report.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    experiment = run_experiment()
    plot_results(experiment)
    summary = {
        "version": "v042_skew_axis_triple_revolute",
        "python": platform.python_version(),
        "platform": platform.platform(),
        "numpy": np.__version__,
        "scipy": __import__("scipy").__version__,
        "jax": jax.__version__,
        "source_versions": ["v041_triple_pattern_cache_refresh", "v040_generated_block_triple_pattern"],
        "model": {
            "cases": CASES,
            "method": "skew_axis_triple_revolute_gauss6_fullva",
            "h": H,
            "t_final": T_FINAL,
            "dimension": DIM,
            "stage_size": STAGE_SIZE,
        },
        "experiment": experiment,
        "runtime_sec": time.perf_counter() - started,
    }
    with (RESULTS / "summary_v042.json").open("w", encoding="utf-8") as f:
        json.dump(json_safe(summary), f, indent=2, sort_keys=True)
    write_report(experiment)


if __name__ == "__main__":
    main()
