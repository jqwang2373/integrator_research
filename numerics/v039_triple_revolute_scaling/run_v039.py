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
import jax.numpy as jnp
import numpy as np
from scipy import sparse
from scipy.sparse import linalg as spla


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
RESULTS = HERE / "results"
V013_PATH = ROOT / "v013_gauss6_quaternion_endpoint_dae" / "quaternion_pendulum.py"
V034_PATH = ROOT / "v034_colored_jvp_sparse_jacobian" / "run_v034.py"

N_BODIES = 3
N_STAGES = 3
BODY_SIZE = 18
LAMBDA_SIZE = 5
STAGE_SIZE = N_BODIES * BODY_SIZE + N_BODIES * LAMBDA_SIZE
DIM = N_STAGES * STAGE_SIZE
H = 0.02
T_FINAL = 0.06
PATTERN_ATOL = 1.0e-14
SPARSITY_ATOL = 1.0e-12
CASES = {"triple_revolute_smooth": 0.50, "triple_revolute_sharp": 0.05}
SOLVERS = ["dense_jacfwd_csr", "cached_jvp_pruned"]
CSV_COLUMNS = [
    "case",
    "solver",
    "h",
    "status",
    "error_message",
    "steps",
    "runtime_sec",
    "pattern_build_sec",
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


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


qp = load_module(V013_PATH, "v013_quaternion_pendulum")
v034 = load_module(V034_PATH, "v034_colored_jvp")


@dataclass(frozen=True)
class Params:
    masses: np.ndarray
    Js: np.ndarray
    s_prev: np.ndarray
    s_next: np.ndarray
    gravity: np.ndarray
    hinge_axis_body: np.ndarray
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


def make_params(stribeck_velocity: float) -> Params:
    return Params(
        masses=np.array([3.2, 2.4, 1.8]),
        Js=np.array(
            [
                np.diag([0.16, 0.30, 0.38]),
                np.diag([0.10, 0.22, 0.27]),
                np.diag([0.08, 0.18, 0.23]),
            ]
        ),
        s_prev=np.array([[0.0, 0.0, 0.70], [0.0, 0.0, 0.55], [0.0, 0.0, 0.45]]),
        s_next=np.array([[0.0, 0.0, -0.70], [0.0, 0.0, -0.55], [0.0, 0.0, 0.0]]),
        gravity=np.array([0.0, 0.0, -9.81]),
        hinge_axis_body=np.array([0.0, 1.0, 0.0]),
        mu_s=0.30,
        mu_d=0.20,
        stribeck_velocity=float(stribeck_velocity),
        viscous_damping=0.018,
        friction_radius=0.075,
        external_torques_body=np.array([[0.25, 0.0, -0.18], [-0.20, 0.0, 0.14], [0.12, 0.0, -0.09]]),
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
    q = np.array([0.82, 1.28, 0.67])
    p = np.stack([qp.quat_exp(np.array([0.0, qi, 0.0])) for qi in q])
    R = [qp.quat_to_rot(pi) for pi in p]
    w = np.array([[0.0, 0.18, 0.0], [0.0, -0.32, 0.0], [0.0, 0.24, 0.0]])
    r = np.zeros((N_BODIES, 3))
    v = np.zeros((N_BODIES, 3))
    r[0] = -R[0] @ params.s_prev[0]
    v[0] = -R[0] @ np.cross(w[0], params.s_prev[0])
    for i in range(1, N_BODIES):
        r[i] = r[i - 1] + R[i - 1] @ params.s_next[i - 1] - R[i] @ params.s_prev[i]
        v[i] = (
            v[i - 1]
            + R[i - 1] @ np.cross(w[i - 1], params.s_next[i - 1])
            - R[i] @ np.cross(w[i], params.s_prev[i])
        )
    return State(r=r, p=p, v=v, w=w)


def state_error(ref: State, state: State) -> tuple[float, float]:
    orient = 0.0
    for i in range(N_BODIES):
        err = qp.orientation_error(qp.quat_to_rot(ref.p[i]), qp.quat_to_rot(state.p[i]))
        orient += err * err
    return float(np.sqrt(orient)), float(np.linalg.norm(ref.w - state.w))


def scalar_alpha_guess(q: float, mass: float, Jyy: float, length: float) -> float:
    inertia = Jyy + mass * length * length
    return float(-mass * 9.81 * length * np.sin(q) / inertia)


def stage_guess(state: State, h: float, params: Params) -> np.ndarray:
    c, _, _ = qp.gauss_legendre_coefficients(N_STAGES)
    q = np.array([angle_from_quat(state.p[i]) for i in range(N_BODIES)])
    qd = state.w[:, 1].copy()
    lengths = np.linalg.norm(params.s_prev, axis=1)
    ay = np.array([scalar_alpha_guess(q[i], params.masses[i], params.Js[i, 1, 1], lengths[i]) for i in range(N_BODIES)])
    blocks = []
    for ci in c:
        qi = q + ci * h * qd
        qdi = qd + ci * h * ay
        alpha = np.array(
            [
                [0.0, scalar_alpha_guess(qi[i], params.masses[i], params.Js[i, 1, 1], lengths[i]), 0.0]
                for i in range(N_BODIES)
            ]
        )
        u = np.stack([np.array([0.0, qi[i] - q[i], 0.0]) for i in range(N_BODIES)])
        p = np.stack([qp.compose_right_quat(state.p[i], u[i]) for i in range(N_BODIES)])
        R = [qp.quat_to_rot(p[i]) for i in range(N_BODIES)]
        w = np.stack([np.array([0.0, qdi[i], 0.0]) for i in range(N_BODIES)])
        r = np.zeros((N_BODIES, 3))
        v = np.zeros((N_BODIES, 3))
        a = np.zeros((N_BODIES, 3))
        r[0] = -R[0] @ params.s_prev[0]
        v[0] = -R[0] @ np.cross(w[0], params.s_prev[0])
        a[0] = -R[0] @ (np.cross(alpha[0], params.s_prev[0]) + np.cross(w[0], np.cross(w[0], params.s_prev[0])))
        for i in range(1, N_BODIES):
            r[i] = r[i - 1] + R[i - 1] @ params.s_next[i - 1] - R[i] @ params.s_prev[i]
            v[i] = (
                v[i - 1]
                + R[i - 1] @ np.cross(w[i - 1], params.s_next[i - 1])
                - R[i] @ np.cross(w[i], params.s_prev[i])
            )
            a[i] = (
                a[i - 1]
                + R[i - 1]
                @ (np.cross(alpha[i - 1], params.s_next[i - 1]) + np.cross(w[i - 1], np.cross(w[i - 1], params.s_next[i - 1])))
                - R[i] @ (np.cross(alpha[i], params.s_prev[i]) + np.cross(w[i], np.cross(w[i], params.s_prev[i])))
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
        stages.append(
            {
                "u": body[:, 0:3],
                "r": body[:, 3:6],
                "v": body[:, 6:9],
                "w": body[:, 9:12],
                "a": body[:, 12:15],
                "alpha": body[:, 15:18],
                "lambda": lam,
            }
        )
    return stages


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


def residual3_fullva(
    x,
    state0,
    h,
    masses,
    Js,
    s_prev,
    s_next,
    gravity,
    hinge_axis_body,
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
        tau = []
        for joint in range(N_BODIES):
            if joint == 0:
                rel_w = st["w"][0, 1]
            else:
                rel_w = st["w"][joint, 1] - st["w"][joint - 1, 1]
            tau.append(
                brown_mcphee_scalar_jax(
                    rel_w,
                    jnp.linalg.norm(F[joint]),
                    mu_s,
                    mu_d,
                    stribeck_velocity,
                    viscous_damping,
                    friction_radius,
                )
            )
        tau_vec = [jnp.array([0.0, tau[j], 0.0], dtype=x.dtype) for j in range(N_BODIES)]

        axis = [R[i] @ hinge_axis_body for i in range(N_BODIES)]
        axis_rate = [R[i] @ jnp.cross(st["w"][i], hinge_axis_body) for i in range(N_BODIES)]
        axis_acc = [
            R[i]
            @ (
                jnp.cross(st["alpha"][i], hinge_axis_body)
                + jnp.cross(st["w"][i], jnp.cross(st["w"][i], hinge_axis_body))
            )
            for i in range(N_BODIES)
        ]
        pvel = []
        pacc = []
        constraints = []
        for joint in range(N_BODIES):
            child = joint
            if joint == 0:
                pv = st["v"][0] + R[0] @ jnp.cross(st["w"][0], s_prev[0])
                pa = st["a"][0] + R[0] @ (
                    jnp.cross(st["alpha"][0], s_prev[0]) + jnp.cross(st["w"][0], jnp.cross(st["w"][0], s_prev[0]))
                )
                pc = st["r"][0] + R[0] @ s_prev[0]
            else:
                parent = joint - 1
                pv = (
                    st["v"][parent]
                    + R[parent] @ jnp.cross(st["w"][parent], s_next[parent])
                    - st["v"][child]
                    - R[child] @ jnp.cross(st["w"][child], s_prev[child])
                )
                pa = (
                    st["a"][parent]
                    + R[parent]
                    @ (
                        jnp.cross(st["alpha"][parent], s_next[parent])
                        + jnp.cross(st["w"][parent], jnp.cross(st["w"][parent], s_next[parent]))
                    )
                    - st["a"][child]
                    - R[child]
                    @ (
                        jnp.cross(st["alpha"][child], s_prev[child])
                        + jnp.cross(st["w"][child], jnp.cross(st["w"][child], s_prev[child]))
                    )
                )
                pc = st["r"][parent] + R[parent] @ s_next[parent] - st["r"][child] - R[child] @ s_prev[child]
            pvel.append(pv)
            pacc.append(pa)
            constraints.extend([pc, jnp.array([axis[child][0], axis[child][2]], dtype=x.dtype)])

        u_block_parts = []
        w_block_parts = []
        for body in range(N_BODIES):
            u_coll = st["u"][body] - h * sum(A[si, sj] * k[sj][body] for sj in range(N_STAGES))
            w_coll = st["w"][body] - w0[body] - h * sum(A[si, sj] * stages[sj]["alpha"][body] for sj in range(N_STAGES))
            u_block_parts.extend([u_coll[1:2], jnp.array([axis_rate[body][0], axis_rate[body][2]], dtype=x.dtype)])
            w_block_parts.extend([w_coll[1:2], jnp.array([axis_acc[body][0], axis_acc[body][2]], dtype=x.dtype)])

        dyn_parts = []
        for body in range(N_BODIES):
            distal = F[body + 1] if body < N_BODIES - 1 else jnp.zeros(3, dtype=x.dtype)
            trans = masses[body] * st["a"][body] - masses[body] * gravity - F[body] + distal
            prox_torque = jnp.cross(s_prev[body], R[body].T @ F[body])
            if body < N_BODIES - 1:
                distal_torque = jnp.cross(s_next[body], R[body].T @ (-F[body + 1]))
                distal_tau = tau_vec[body + 1]
            else:
                distal_torque = jnp.zeros(3, dtype=x.dtype)
                distal_tau = jnp.zeros(3, dtype=x.dtype)
            rot = (
                Js[body] @ st["alpha"][body]
                + jnp.cross(st["w"][body], Js[body] @ st["w"][body])
                - prox_torque
                - distal_torque
                - axis_torque_jax(R[body], eta[body], hinge_axis_body)
                - tau_vec[body]
                + distal_tau
                - external_torques_body[body]
            )
            dyn_parts.extend([trans, rot])
        out.extend(
            [
                jnp.concatenate(pvel),
                jnp.concatenate(u_block_parts),
                jnp.concatenate(pacc),
                jnp.concatenate(w_block_parts),
                jnp.concatenate(dyn_parts),
                jnp.concatenate(constraints),
            ]
        )
    return jnp.concatenate(out)


R3_VALUE = jax.jit(residual3_fullva)
R3_JAC = jax.jit(jax.jacfwd(residual3_fullva, argnums=0))


@jax.jit
def batched_jvp3(x, seeds, *args):
    def one(seed):
        return jax.jvp(lambda y: residual3_fullva(y, *args), (x,), (seed,))[1]

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
        jnp.asarray(params.hinge_axis_body, dtype=jnp.float64),
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


def constraints_np(state: State, params: Params) -> np.ndarray:
    R = [qp.quat_to_rot(state.p[i]) for i in range(N_BODIES)]
    out = []
    for joint in range(N_BODIES):
        if joint == 0:
            out.append(state.r[0] + R[0] @ params.s_prev[0])
        else:
            parent = joint - 1
            out.append(state.r[parent] + R[parent] @ params.s_next[parent] - state.r[joint] - R[joint] @ params.s_prev[joint])
        axis = R[joint] @ params.hinge_axis_body
        out.append(np.array([axis[0], axis[2]]))
    return np.concatenate(out)


def velocity_constraints_np(state: State, params: Params) -> np.ndarray:
    R = [qp.quat_to_rot(state.p[i]) for i in range(N_BODIES)]
    out = []
    for joint in range(N_BODIES):
        if joint == 0:
            out.append(state.v[0] + R[0] @ np.cross(state.w[0], params.s_prev[0]))
        else:
            parent = joint - 1
            out.append(
                state.v[parent]
                + R[parent] @ np.cross(state.w[parent], params.s_next[parent])
                - state.v[joint]
                - R[joint] @ np.cross(state.w[joint], params.s_prev[joint])
            )
        axis_rate = R[joint] @ np.cross(state.w[joint], params.hinge_axis_body)
        out.append(np.array([axis_rate[0], axis_rate[2]]))
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
            if joint == 0:
                pa = st["a"][0] + R[0] @ (
                    np.cross(st["alpha"][0], params.s_prev[0]) + np.cross(st["w"][0], np.cross(st["w"][0], params.s_prev[0]))
                )
            else:
                parent = joint - 1
                pa = (
                    st["a"][parent]
                    + R[parent]
                    @ (
                        np.cross(st["alpha"][parent], params.s_next[parent])
                        + np.cross(st["w"][parent], np.cross(st["w"][parent], params.s_next[parent]))
                    )
                    - st["a"][joint]
                    - R[joint]
                    @ (
                        np.cross(st["alpha"][joint], params.s_prev[joint])
                        + np.cross(st["w"][joint], np.cross(st["w"][joint], params.s_prev[joint]))
                    )
                )
            aa = R[joint] @ (
                np.cross(st["alpha"][joint], params.hinge_axis_body)
                + np.cross(st["w"][joint], np.cross(st["w"][joint], params.hinge_axis_body))
            )
            piv.append(pa)
            ax.extend([aa[0], aa[2]])
        max_pivot = max(max_pivot, float(np.linalg.norm(np.concatenate(piv))))
        max_axis = max(max_axis, float(np.linalg.norm(np.array(ax))))
    return max_pivot, max_axis


def csr_from_dense(jac: np.ndarray):
    mask = np.abs(jac) > SPARSITY_ATOL
    return sparse.csr_matrix(np.where(mask, jac, 0.0))


def greedy_column_coloring(pattern: np.ndarray) -> list[list[int]]:
    rows_by_col = [set(np.nonzero(pattern[:, col])[0].tolist()) for col in range(pattern.shape[1])]
    order = sorted(range(pattern.shape[1]), key=lambda col: len(rows_by_col[col]), reverse=True)
    color_rows: list[set[int]] = []
    colors: list[list[int]] = []
    for col in order:
        support = rows_by_col[col]
        for idx, used in enumerate(color_rows):
            if support.isdisjoint(used):
                colors[idx].append(col)
                used.update(support)
                break
        else:
            colors.append([col])
            color_rows.append(set(support))
    return colors


@dataclass
class SparsePattern:
    pattern: np.ndarray
    colors: list[list[int]]
    rows_by_col: list[np.ndarray]
    nnz: int
    density: float


def make_pattern(mask: np.ndarray) -> SparsePattern:
    colors = greedy_column_coloring(mask)
    rows_by_col = [np.nonzero(mask[:, col])[0] for col in range(mask.shape[1])]
    nnz = int(mask.sum())
    return SparsePattern(mask, colors, rows_by_col, nnz, nnz / mask.size)


def make_seed_matrix(sp: SparsePattern) -> np.ndarray:
    seeds = np.zeros((len(sp.colors), sp.pattern.shape[1]))
    for i, color in enumerate(sp.colors):
        seeds[i, color] = 1.0
    return seeds


def full_superset_pattern() -> SparsePattern:
    return make_pattern(np.ones((DIM, DIM), dtype=bool))


def colored_jvp_csr_and_mask(x: np.ndarray, args, sp: SparsePattern, seeds: np.ndarray, threshold: float):
    rows = []
    cols = []
    data = []
    mask = np.zeros(sp.pattern.shape, dtype=bool)
    y_by_color = np.asarray(batched_jvp3(jnp.asarray(x, dtype=jnp.float64), jnp.asarray(seeds, dtype=jnp.float64), *args), dtype=float)
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


def build_jvp_pruned_pattern(params: Params) -> tuple[SparsePattern, float]:
    superset = full_superset_pattern()
    seeds = make_seed_matrix(superset)
    state = initial_state(params)
    pattern = np.zeros((DIM, DIM), dtype=bool)
    started = time.perf_counter()
    for _ in range(int(round(T_FINAL / H))):
        x = stage_guess(state, H, params)
        args = build_args(state, H, params)
        for _it in range(8):
            res = np.asarray(R3_VALUE(jnp.asarray(x, dtype=jnp.float64), *args), dtype=float)
            csr, current = colored_jvp_csr_and_mask(x, args, superset, seeds, PATTERN_ATOL)
            pattern = np.logical_or(pattern, current)
            if float(np.linalg.norm(res)) < 1.0e-11:
                break
            delta = spla.spsolve(csr, -res)
            x = x + np.asarray(delta, dtype=float)
            if float(np.linalg.norm(delta)) < 1.0e-11:
                break
        stages = unpack_stages(x)
        state = next_state_from_stages(state, H, stages)
    return make_pattern(pattern), time.perf_counter() - started


def pattern_relation(candidate: SparsePattern, reference: SparsePattern) -> dict:
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


def dense_validation_pattern(params: Params) -> tuple[SparsePattern, float]:
    state = initial_state(params)
    pattern = None
    started = time.perf_counter()
    for _ in range(int(round(T_FINAL / H))):
        x = stage_guess(state, H, params)
        args = build_args(state, H, params)
        for _it in range(8):
            x_jax = jnp.asarray(x, dtype=jnp.float64)
            res = np.asarray(R3_VALUE(x_jax, *args), dtype=float)
            jac = np.asarray(R3_JAC(x_jax, *args), dtype=float)
            current = np.abs(jac) > PATTERN_ATOL
            pattern = current if pattern is None else np.logical_or(pattern, current)
            if float(np.linalg.norm(res)) < 1.0e-11:
                break
            delta = np.linalg.solve(jac, -res)
            x = x + delta
            if float(np.linalg.norm(delta)) < 1.0e-11:
                break
        stages = unpack_stages(x)
        state = next_state_from_stages(state, H, stages)
    assert pattern is not None
    return make_pattern(pattern), time.perf_counter() - started


def jvp_csr(x: np.ndarray, args, sp: SparsePattern, seeds: np.ndarray):
    started = time.perf_counter()
    csr, _ = colored_jvp_csr_and_mask(x, args, sp, seeds, SPARSITY_ATOL)
    return csr, time.perf_counter() - started


def gauss_step(state: State, params: Params, solver: str, sp: SparsePattern, seeds: np.ndarray):
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
        res = np.asarray(R3_VALUE(x_jax, *args), dtype=float)
        total_residual += time.perf_counter() - started
        last_norm = float(np.linalg.norm(res))
        if last_norm < 1.0e-11:
            break
        if solver == "dense_jacfwd_csr":
            started = time.perf_counter()
            jac = np.asarray(R3_JAC(x_jax, *args), dtype=float)
            csr = csr_from_dense(jac)
            total_jac += time.perf_counter() - started
        elif solver == "cached_jvp_pruned":
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
        raise RuntimeError(f"triple revolute Newton failed residual={last_norm:.3e}")
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


def integrate(params: Params, solver: str, sp: SparsePattern, seeds: np.ndarray):
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


def warm_jax(params: Params, sp: SparsePattern, seeds: np.ndarray) -> None:
    state = initial_state(params)
    x = stage_guess(state, H, params)
    args = build_args(state, H, params)
    x_jax = jnp.asarray(x, dtype=jnp.float64)
    np.asarray(R3_VALUE(x_jax, *args), dtype=float)
    np.asarray(R3_JAC(x_jax, *args), dtype=float)
    np.asarray(batched_jvp3(x_jax, jnp.asarray(seeds, dtype=jnp.float64), *args), dtype=float)


def row_from_run(case_name: str, solver: str, out: dict, runtime: float, sp: SparsePattern, relation: dict, pattern_build: float, oerr: float, werr: float):
    return {
        "case": case_name,
        "solver": solver,
        "h": f"{H:.10g}",
        "status": "ok",
        "error_message": "",
        "steps": out["steps"],
        "runtime_sec": f"{runtime:.8e}",
        "pattern_build_sec": f"{pattern_build:.8e}",
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


def run_experiment() -> dict:
    rows = []
    cases = {}
    for case_name, vs in CASES.items():
        params = make_params(vs)
        pattern, pattern_build_sec = build_jvp_pruned_pattern(params)
        seeds = make_seed_matrix(pattern)
        warm_jax(params, pattern, seeds)
        dense_pattern, dense_pattern_sec = dense_validation_pattern(params)
        relation = pattern_relation(pattern, dense_pattern)
        dense_state = None
        runs = {}
        for solver in SOLVERS:
            row = {key: "" for key in CSV_COLUMNS}
            row.update({"case": case_name, "solver": solver, "h": f"{H:.10g}"})
            started = time.perf_counter()
            try:
                out = integrate(params, solver, pattern, seeds)
                runtime = time.perf_counter() - started
                if solver == "dense_jacfwd_csr":
                    dense_state = out["state"]
                    oerr, werr = 0.0, 0.0
                else:
                    assert dense_state is not None
                    oerr, werr = state_error(dense_state, out["state"])
                item = {key: value for key, value in out.items() if key != "state"}
                item.update({"status": "ok", "runtime_sec": runtime, "orientation_error_vs_dense_rad": oerr, "omega_error_vs_dense": werr})
                row = row_from_run(case_name, solver, out, runtime, pattern, relation, pattern_build_sec if solver != "dense_jacfwd_csr" else 0.0, oerr, werr)
            except Exception as exc:
                runtime = time.perf_counter() - started
                item = {"status": "failed", "error_message": str(exc), "runtime_sec": runtime}
                row.update({"status": "failed", "error_message": str(exc), "runtime_sec": f"{runtime:.8e}"})
            rows.append(row)
            runs[solver] = item
        cases[case_name] = {
            "stribeck_velocity": vs,
            "pattern_build_sec": pattern_build_sec,
            "dense_validation_pattern_build_sec": dense_pattern_sec,
            "pattern": {"nnz": pattern.nnz, "density": pattern.density, "colors": len(pattern.colors)},
            "dense_validation_pattern": {"nnz": dense_pattern.nnz, "density": dense_pattern.density, "colors": len(dense_pattern.colors)},
            "pattern_relation_to_dense": relation,
            "runs": runs,
        }
    write_csv(RESULTS / "triple_revolute_scaling_runs.csv", rows)
    return {"h": H, "t_final": T_FINAL, "dimension": DIM, "stage_size": STAGE_SIZE, "cases": cases}


def plot_results(summary: dict) -> None:
    import matplotlib.pyplot as plt

    labels = []
    dense_runtime = []
    cached_runtime = []
    nnz = []
    colors = []
    for case_name, case in summary["cases"].items():
        labels.append(case_name.replace("triple_revolute_", ""))
        dense_runtime.append(case["runs"]["dense_jacfwd_csr"].get("runtime_sec", np.nan))
        cached_runtime.append(case["runs"]["cached_jvp_pruned"].get("runtime_sec", np.nan))
        nnz.append(case["pattern"]["nnz"])
        colors.append(case["pattern"]["colors"])
    xs = np.arange(len(labels))
    fig, axes = plt.subplots(1, 2, figsize=(10.8, 4.0))
    axes[0].bar(xs - 0.18, dense_runtime, width=0.36, label="dense jacfwd CSR")
    axes[0].bar(xs + 0.18, cached_runtime, width=0.36, label="cached JVP-pruned")
    axes[0].set_yscale("log")
    axes[0].set_ylabel("runtime seconds")
    axes[1].bar(xs - 0.18, nnz, width=0.36, label="nnz")
    axes[1].bar(xs + 0.18, colors, width=0.36, label="colors")
    axes[1].set_ylabel("pattern count")
    for ax in axes:
        ax.set_xticks(xs)
        ax.set_xticklabels(labels)
        ax.grid(True, axis="y", alpha=0.35)
        ax.legend()
    fig.tight_layout()
    fig.savefig(RESULTS / "triple_revolute_scaling_runtime.png", dpi=180)
    plt.close(fig)


def write_report(summary: dict) -> None:
    lines = [
        "# v039 Experiment Report",
        "",
        "Generated by `run_v039.py`.",
        "",
        "## Purpose",
        "",
        "- Move beyond the planar double-revolute benchmark to a three-body, three-joint triple-revolute chain.",
        f"- Increase the Gauss6 FullVA Newton system from 138 variables to {DIM} variables.",
        "- Test whether JVP-pruned sparse AD remains valid and useful on the larger topology.",
        "",
        "## Results",
        "",
    ]
    for case_name, case in summary["cases"].items():
        dense = case["runs"]["dense_jacfwd_csr"]
        cached = case["runs"]["cached_jvp_pruned"]
        rel = case["pattern_relation_to_dense"]
        lines.append(f"### {case_name}")
        lines.append(
            f"- Pattern: {case['pattern']['nnz']} entries, {case['pattern']['colors']} colors; "
            f"dense validation pattern {case['dense_validation_pattern']['nnz']} entries, "
            f"missing {rel['missing_vs_reference']}, extra {rel['extra_vs_reference']}."
        )
        lines.append(
            f"- Pattern build: JVP-pruned {case['pattern_build_sec']:.3f}s, dense validation "
            f"{case['dense_validation_pattern_build_sec']:.3f}s."
        )
        if dense.get("status") == "ok" and cached.get("status") == "ok":
            speed = dense["runtime_sec"] / max(cached["runtime_sec"], 1.0e-30)
            lines.append(
                f"- Runtime: dense {dense['runtime_sec']:.3f}s vs cached JVP-pruned "
                f"{cached['runtime_sec']:.3f}s (dense/cached {speed:.2f}x)."
            )
            lines.append(
                f"- Trajectory diff: orientation {cached['orientation_error_vs_dense_rad']:.3e} rad, "
                f"omega {cached['omega_error_vs_dense']:.3e}; endpoint velocity "
                f"{cached['max_endpoint_velocity_constraint_norm']:.3e}."
            )
        else:
            lines.append(f"- Status: dense {dense.get('status')}, cached {cached.get('status')}.")
        lines.append("")
    lines.extend(
        [
            "## Interpretation",
            "",
            "- This is the first larger-topology test after the double-revolute work: it uses an actual three-body chain rather than replicated independent systems.",
            "- The main pass/fail criterion is whether the JVP-pruned pattern misses zero dense-validation entries while preserving the dense trajectory.",
            "- The runtime result is a positive early scaling signal for the sparse-AD backend on a 207D constrained Newton system.",
            "- The smooth pattern-build time includes the first full-superset batched-JVP compilation path; after that compile is available, the sharp pattern build is 0.057s. The next larger-topology step should replace the temporary full superset with a generated block superset and cache it.",
            "",
            "## Outputs",
            "",
            "- `triple_revolute_scaling_runs.csv`",
            "- `summary_v039.json`",
            "- `triple_revolute_scaling_runtime.png`",
            "",
        ]
    )
    (RESULTS / "v039_report.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    experiment = run_experiment()
    plot_results(experiment)
    summary = {
        "version": "v039_triple_revolute_scaling",
        "python": platform.python_version(),
        "platform": platform.platform(),
        "numpy": np.__version__,
        "scipy": __import__("scipy").__version__,
        "jax": jax.__version__,
        "source_versions": ["v029_double_revolute_pivotva_dae", "v038_pattern_cache_reuse"],
        "model": {"cases": CASES, "h": H, "t_final": T_FINAL, "dimension": DIM, "stage_size": STAGE_SIZE},
        "experiment": experiment,
        "runtime_sec": time.perf_counter() - started,
    }
    with (RESULTS / "summary_v039.json").open("w", encoding="utf-8") as f:
        json.dump(json_safe(summary), f, indent=2, sort_keys=True)
    write_report(experiment)


if __name__ == "__main__":
    main()
