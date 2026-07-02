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
V039_PATH = ROOT / "v039_triple_revolute_scaling" / "run_v039.py"

N_STAGES = 3
BODY_SIZE = 18
LAMBDA_SIZE = 5
STAGE_SIZE = BODY_SIZE + LAMBDA_SIZE
DIM = N_STAGES * STAGE_SIZE
H = 0.02
T_FINAL = 0.08
PATTERN_ATOL = 1.0e-14
SPARSITY_ATOL = 1.0e-12
CASES = {"skew_prismatic_smooth": 0.50, "skew_prismatic_sharp": 0.05}
CSV_COLUMNS = [
    "case",
    "solver",
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
    "position_error_vs_dense",
    "velocity_error_vs_dense",
    "max_linear_residual_norm",
    "max_endpoint_constraint_norm",
    "max_endpoint_velocity_constraint_norm",
    "max_stage_position_acceleration_constraint_norm",
    "max_stage_orientation_acceleration_constraint_norm",
    "max_quaternion_unit_error",
]


def load_v039():
    spec = importlib.util.spec_from_file_location("v039_triple_revolute_scaling", V039_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


v039 = load_v039()
qp = v039.qp
jax = v039.jax


@dataclass(frozen=True)
class Params:
    mass: float
    J: np.ndarray
    s: np.ndarray
    axis_world: np.ndarray
    axis_body: np.ndarray
    twist_body: np.ndarray
    basis_world: np.ndarray
    gravity: np.ndarray
    mu_s: float
    mu_d: float
    stribeck_velocity: float
    viscous_damping: float
    friction_radius: float
    external_force_world: np.ndarray
    external_torque_body: np.ndarray
    slide0: float
    slide_rate0: float


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


def make_params(stribeck_velocity: float) -> Params:
    axis_world = normalize([0.31, 0.78, 0.54])
    axis_body = normalize([0.18, 0.91, -0.37])
    basis_world = perp_basis(axis_world)
    twist_body = normalize(np.cross(axis_body, normalize([0.7, -0.2, 0.4])))
    return Params(
        mass=2.7,
        J=np.diag([0.11, 0.24, 0.31]),
        s=np.array([0.12, -0.04, 0.18]),
        axis_world=axis_world,
        axis_body=axis_body,
        twist_body=twist_body,
        basis_world=basis_world,
        gravity=np.array([0.0, 0.0, -9.81]),
        mu_s=0.30,
        mu_d=0.20,
        stribeck_velocity=float(stribeck_velocity),
        viscous_damping=0.035,
        friction_radius=1.0,
        external_force_world=np.array([0.8, -0.35, 0.25]),
        external_torque_body=np.array([0.03, -0.02, 0.015]),
        slide0=0.35,
        slide_rate0=0.42,
    )


def initial_orientation(params: Params) -> np.ndarray:
    R_align = align_rot(params.axis_body, params.axis_world)
    twist_world = R_align @ params.twist_body
    angle = np.arctan2(twist_world @ params.basis_world[1], twist_world @ params.basis_world[0])
    return axis_angle_rot(params.axis_world, -angle) @ R_align


def initial_state(params: Params) -> State:
    R = initial_orientation(params)
    p = rot_to_quat(R)
    r = params.slide0 * params.axis_world - R @ params.s
    v = params.slide_rate0 * params.axis_world
    w = np.zeros(3)
    return State(r=r, p=p, v=v, w=w)


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


def state_error(ref: State, state: State) -> tuple[float, float]:
    return float(np.linalg.norm(ref.r - state.r)), float(np.linalg.norm(ref.v - state.v))


def stage_guess(state: State, h: float, params: Params) -> np.ndarray:
    c, _, _ = qp.gauss_legendre_coefficients(N_STAGES)
    axial_acc = float(params.axis_world @ (params.gravity + params.external_force_world / params.mass))
    blocks = []
    for ci in c:
        u = np.zeros(3)
        w = np.zeros(3)
        alpha = np.zeros(3)
        v = state.v + ci * h * axial_acc * params.axis_world
        r = state.r + ci * h * state.v + 0.5 * (ci * h) ** 2 * axial_acc * params.axis_world
        a = axial_acc * params.axis_world
        lam = np.zeros(5)
        force_balance = params.mass * a - params.mass * params.gravity - params.external_force_world
        lam[0] = force_balance @ params.basis_world[0]
        lam[1] = force_balance @ params.basis_world[1]
        blocks.extend([u, r, v, w, a, alpha, lam])
    return np.concatenate(blocks)


def unpack_stages(x):
    stages = []
    for stage in range(N_STAGES):
        base = stage * STAGE_SIZE
        body = x[base : base + BODY_SIZE]
        lam = x[base + BODY_SIZE : base + STAGE_SIZE]
        stages.append({"u": body[0:3], "r": body[3:6], "v": body[6:9], "w": body[9:12], "a": body[12:15], "alpha": body[15:18], "lambda": lam})
    return stages


def brown_mcphee_scalar_jax(v, normal_load, mu_s, mu_d, stribeck_velocity, viscous_damping, friction_radius):
    vs = jnp.maximum(stribeck_velocity, 1.0e-12)
    z = v / vs
    denom = (0.25 * z * z + 0.75) ** 2
    curve = mu_d * jnp.tanh(4.0 * z) + (mu_s - mu_d) * z / denom
    return -friction_radius * normal_load * curve - viscous_damping * v


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
    scalar = jnp.where(small, scalar_small, scalar_large)
    b = jnp.where(small, b_small, b_large)
    return jnp.concatenate((jnp.array([scalar], dtype=theta.dtype), b * theta))


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


def residual_prismatic(
    x,
    state0,
    h,
    mass,
    J,
    s,
    axis_world,
    axis_body,
    twist_body,
    basis_world,
    gravity,
    mu_s,
    mu_d,
    stribeck_velocity,
    viscous_damping,
    friction_radius,
    external_force_world,
    external_torque_body,
):
    r0, p0, v0, w0 = state0
    _, A, _ = qp._gauss_legendre_coefficients_jax(N_STAGES, x.dtype)
    stages = unpack_stages(x)
    k = [right_jacobian_inverse_apply_jax_safe(st["u"], st["w"]) for st in stages]
    out = []
    for si, st in enumerate(stages):
        p = compose_right_quat_jax_safe(p0, st["u"])
        R = qp.quat_to_rot_jax(p)
        lam = st["lambda"]
        normal_force = lam[0] * basis_world[0] + lam[1] * basis_world[1]
        eta = lam[2:5]
        point = st["r"] + R @ s
        point_vel = st["v"] + R @ jnp.cross(st["w"], s)
        point_acc = st["a"] + R @ (jnp.cross(st["alpha"], s) + jnp.cross(st["w"], jnp.cross(st["w"], s)))
        axis = R @ axis_body
        twist = R @ twist_body
        axis_rate = R @ jnp.cross(st["w"], axis_body)
        twist_rate = R @ jnp.cross(st["w"], twist_body)
        axis_acc = R @ (jnp.cross(st["alpha"], axis_body) + jnp.cross(st["w"], jnp.cross(st["w"], axis_body)))
        twist_acc = R @ (jnp.cross(st["alpha"], twist_body) + jnp.cross(st["w"], jnp.cross(st["w"], twist_body)))
        slide_vel = point_vel @ axis_world
        normal_load = jnp.sqrt(normal_force @ normal_force + jnp.array(1.0e-24, dtype=x.dtype))
        friction = brown_mcphee_scalar_jax(slide_vel, normal_load, mu_s, mu_d, stribeck_velocity, viscous_damping, friction_radius)
        friction_force = friction * axis_world

        r_coll_axis = (st["r"] - r0 - h * sum(A[si, sj] * stages[sj]["v"] for sj in range(N_STAGES))) @ axis_world
        v_coll_axis = (st["v"] - v0 - h * sum(A[si, sj] * stages[sj]["a"] for sj in range(N_STAGES))) @ axis_world
        pvel = jnp.array([point_vel @ basis_world[0], point_vel @ basis_world[1], r_coll_axis], dtype=x.dtype)
        pacc = jnp.array([point_acc @ basis_world[0], point_acc @ basis_world[1], v_coll_axis], dtype=x.dtype)

        u_block = jnp.array([axis_rate @ basis_world[0], axis_rate @ basis_world[1], twist_rate @ basis_world[1]], dtype=x.dtype)
        w_block = jnp.array([axis_acc @ basis_world[0], axis_acc @ basis_world[1], twist_acc @ basis_world[1]], dtype=x.dtype)
        trans = mass * st["a"] - mass * gravity - external_force_world - normal_force - friction_force
        axis_torque = eta[0] * jnp.cross(axis_body, R.T @ basis_world[0]) + eta[1] * jnp.cross(axis_body, R.T @ basis_world[1])
        twist_torque = eta[2] * jnp.cross(twist_body, R.T @ basis_world[1])
        rot = J @ st["alpha"] + jnp.cross(st["w"], J @ st["w"]) - jnp.cross(s, R.T @ normal_force) - axis_torque - twist_torque - external_torque_body
        constraints = jnp.array(
            [
                point @ basis_world[0],
                point @ basis_world[1],
                (axis - axis_world) @ basis_world[0],
                (axis - axis_world) @ basis_world[1],
                (twist - basis_world[0]) @ basis_world[1],
            ],
            dtype=x.dtype,
        )
        out.extend([pvel, u_block, pacc, w_block, trans, rot, constraints])
    return jnp.concatenate(out)


R_VALUE = jax.jit(residual_prismatic)
R_JAC = jax.jit(jax.jacfwd(residual_prismatic, argnums=0))


@jax.jit
def batched_jvp(x, seeds, *args):
    def one(seed):
        return jax.jvp(lambda y: residual_prismatic(y, *args), (x,), (seed,))[1]

    return jax.vmap(one)(seeds)


def build_args(state: State, h: float, params: Params):
    return (
        (
            jnp.asarray(state.r, dtype=jnp.float64),
            jnp.asarray(state.p, dtype=jnp.float64),
            jnp.asarray(state.v, dtype=jnp.float64),
            jnp.asarray(state.w, dtype=jnp.float64),
        ),
        jnp.asarray(h, dtype=jnp.float64),
        jnp.asarray(params.mass, dtype=jnp.float64),
        jnp.asarray(params.J, dtype=jnp.float64),
        jnp.asarray(params.s, dtype=jnp.float64),
        jnp.asarray(params.axis_world, dtype=jnp.float64),
        jnp.asarray(params.axis_body, dtype=jnp.float64),
        jnp.asarray(params.twist_body, dtype=jnp.float64),
        jnp.asarray(params.basis_world, dtype=jnp.float64),
        jnp.asarray(params.gravity, dtype=jnp.float64),
        jnp.asarray(params.mu_s, dtype=jnp.float64),
        jnp.asarray(params.mu_d, dtype=jnp.float64),
        jnp.asarray(params.stribeck_velocity, dtype=jnp.float64),
        jnp.asarray(params.viscous_damping, dtype=jnp.float64),
        jnp.asarray(params.friction_radius, dtype=jnp.float64),
        jnp.asarray(params.external_force_world, dtype=jnp.float64),
        jnp.asarray(params.external_torque_body, dtype=jnp.float64),
    )


def next_state_from_stages(state: State, h: float, stages) -> State:
    _, _, b = qp.gauss_legendre_coefficients(N_STAGES)
    k = [qp.right_jacobian_inverse_apply(st["u"], st["w"]) for st in stages]
    r = state.r + h * sum(b[j] * stages[j]["v"] for j in range(N_STAGES))
    p = qp.compose_right_quat(state.p, h * sum(b[j] * k[j] for j in range(N_STAGES)))
    v = state.v + h * sum(b[j] * stages[j]["a"] for j in range(N_STAGES))
    w = state.w + h * sum(b[j] * stages[j]["alpha"] for j in range(N_STAGES))
    return State(r=r, p=p, v=v, w=w)


def constraint_parts_np(state: State, params: Params) -> tuple[np.ndarray, np.ndarray]:
    R = qp.quat_to_rot(state.p)
    point = state.r + R @ params.s
    point_vel = state.v + R @ np.cross(state.w, params.s)
    axis = R @ params.axis_body
    twist = R @ params.twist_body
    axis_rate = R @ np.cross(state.w, params.axis_body)
    twist_rate = R @ np.cross(state.w, params.twist_body)
    con = np.array(
        [
            point @ params.basis_world[0],
            point @ params.basis_world[1],
            (axis - params.axis_world) @ params.basis_world[0],
            (axis - params.axis_world) @ params.basis_world[1],
            (twist - params.basis_world[0]) @ params.basis_world[1],
        ]
    )
    vel = np.array(
        [
            point_vel @ params.basis_world[0],
            point_vel @ params.basis_world[1],
            axis_rate @ params.basis_world[0],
            axis_rate @ params.basis_world[1],
            twist_rate @ params.basis_world[1],
        ]
    )
    return con, vel


def stage_acceleration_parts(state: State, stages, params: Params) -> tuple[float, float]:
    max_pos = 0.0
    max_ori = 0.0
    for st in stages:
        p = qp.compose_right_quat(state.p, st["u"])
        R = qp.quat_to_rot(p)
        point_acc = st["a"] + R @ (np.cross(st["alpha"], params.s) + np.cross(st["w"], np.cross(st["w"], params.s)))
        axis_acc = R @ (np.cross(st["alpha"], params.axis_body) + np.cross(st["w"], np.cross(st["w"], params.axis_body)))
        twist_acc = R @ (np.cross(st["alpha"], params.twist_body) + np.cross(st["w"], np.cross(st["w"], params.twist_body)))
        max_pos = max(max_pos, float(np.linalg.norm([point_acc @ params.basis_world[0], point_acc @ params.basis_world[1]])))
        max_ori = max(max_ori, float(np.linalg.norm([axis_acc @ params.basis_world[0], axis_acc @ params.basis_world[1], twist_acc @ params.basis_world[1]])))
    return max_pos, max_ori


def csr_from_dense(jac: np.ndarray):
    mask = np.abs(jac) > SPARSITY_ATOL
    return sparse.csr_matrix(np.where(mask, jac, 0.0))


def make_pattern(mask: np.ndarray) -> v039.SparsePattern:
    return v039.make_pattern(mask)


def make_seed_matrix(sp: v039.SparsePattern) -> np.ndarray:
    return v039.make_seed_matrix(sp)


def row_slice(stage: int, start: int, stop: int) -> slice:
    base = stage * STAGE_SIZE
    return slice(base + start, base + stop)


def col_slice(stage: int, start: int, stop: int) -> slice:
    base = stage * STAGE_SIZE
    return slice(base + start, base + stop)


def generated_block_superset_pattern() -> v039.SparsePattern:
    mask = np.zeros((DIM, DIM), dtype=bool)
    for stage in range(N_STAGES):
        # pvel: perpendicular point velocity plus axial r collocation.
        mask[row_slice(stage, 0, 2), col_slice(stage, 0, 12)] = True
        mask[row_slice(stage, 2, 3), col_slice(stage, 3, 6)] = True
        for sj in range(N_STAGES):
            mask[row_slice(stage, 2, 3), col_slice(sj, 6, 9)] = True

        # u-block orientation velocity constraints.
        mask[row_slice(stage, 3, 6), col_slice(stage, 0, 12)] = True

        # pacc: perpendicular point acceleration plus axial v collocation.
        mask[row_slice(stage, 6, 8), col_slice(stage, 0, 18)] = True
        mask[row_slice(stage, 8, 9), col_slice(stage, 6, 9)] = True
        for sj in range(N_STAGES):
            mask[row_slice(stage, 8, 9), col_slice(sj, 12, 15)] = True

        # w-block orientation acceleration constraints.
        mask[row_slice(stage, 9, 12), col_slice(stage, 0, 18)] = True

        # Dynamics.
        mask[row_slice(stage, 12, 15), col_slice(stage, 0, 23)] = True
        mask[row_slice(stage, 15, 18), col_slice(stage, 0, 23)] = True

        # Position/orientation constraints.
        mask[row_slice(stage, 18, 23), col_slice(stage, 0, 6)] = True
    return make_pattern(mask)


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
            csr = csr_from_dense(np.asarray(R_JAC(x_jax, *args), dtype=float))
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
        raise RuntimeError(f"prismatic Newton failed residual={last_norm:.3e}")
    stages = unpack_stages(x)
    next_state = next_state_from_stages(state, H, stages)
    con, vel = constraint_parts_np(next_state, params)
    pa, oa = stage_acceleration_parts(state, stages, params)
    diag = {
        "newton_iterations": it + 1,
        "linear_solves": linear_solves,
        "jacobian_assemblies": linear_solves,
        "total_residual_eval_sec": total_residual,
        "total_jacobian_eval_sec": total_jac,
        "total_linear_solve_sec": total_linear,
        "max_linear_residual_norm": max_linear_residual,
        "max_endpoint_constraint_norm": float(np.linalg.norm(con)),
        "max_endpoint_velocity_constraint_norm": float(np.linalg.norm(vel)),
        "max_stage_position_acceleration_constraint_norm": pa,
        "max_stage_orientation_acceleration_constraint_norm": oa,
        "max_quaternion_unit_error": float(abs(np.linalg.norm(next_state.p) - 1.0)),
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
        "max_stage_position_acceleration_constraint_norm": 0.0,
        "max_stage_orientation_acceleration_constraint_norm": 0.0,
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
            "max_stage_position_acceleration_constraint_norm",
            "max_stage_orientation_acceleration_constraint_norm",
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


def row_from_run(case_name: str, solver: str, out: dict, runtime: float, sp: v039.SparsePattern, relation: dict, pattern_build: float, dense_pattern_sec: float, perr: float, verr: float):
    return {
        "case": case_name,
        "solver": solver,
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
        "position_error_vs_dense": f"{perr:.16e}",
        "velocity_error_vs_dense": f"{verr:.16e}",
        "max_linear_residual_norm": f"{out['max_linear_residual_norm']:.16e}",
        "max_endpoint_constraint_norm": f"{out['max_endpoint_constraint_norm']:.16e}",
        "max_endpoint_velocity_constraint_norm": f"{out['max_endpoint_velocity_constraint_norm']:.16e}",
        "max_stage_position_acceleration_constraint_norm": f"{out['max_stage_position_acceleration_constraint_norm']:.16e}",
        "max_stage_orientation_acceleration_constraint_norm": f"{out['max_stage_orientation_acceleration_constraint_norm']:.16e}",
        "max_quaternion_unit_error": f"{out['max_quaternion_unit_error']:.16e}",
    }


def run_case(case_name: str, params: Params) -> dict:
    block = generated_block_superset_pattern()
    started = time.perf_counter()
    pruned, pruned_build_sec = build_pruned_pattern(params, block)
    pruned_build_sec += time.perf_counter() - started - pruned_build_sec
    seeds = make_seed_matrix(pruned)
    warm_jax(params, pruned, seeds)
    dense_pattern, dense_pattern_sec = dense_validation_pattern(params)
    relation = pattern_relation(pruned, dense_pattern)
    block_relation = pattern_relation(block, dense_pattern)
    rows = []
    runs = {}
    dense_state = None
    for solver, build_sec in [("dense_jacfwd_csr", 0.0), ("generated_block_jvp_pruned", pruned_build_sec)]:
        started = time.perf_counter()
        out = integrate(params, solver, pruned, seeds)
        runtime = time.perf_counter() - started
        if solver == "dense_jacfwd_csr":
            dense_state = out["state"]
            perr, verr = 0.0, 0.0
        else:
            assert dense_state is not None
            perr, verr = state_error(dense_state, out["state"])
        runs[solver] = {key: value for key, value in out.items() if key != "state"} | {"status": "ok", "runtime_sec": runtime, "position_error_vs_dense": perr, "velocity_error_vs_dense": verr}
        rows.append(row_from_run(case_name, solver, out, runtime, pruned, relation, build_sec, dense_pattern_sec, perr, verr))
    return {
        "stribeck_velocity": CASES[case_name],
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
    rows = []
    cases = {}
    for case_name, vs in CASES.items():
        params = make_params(vs)
        case = run_case(case_name, params)
        rows.extend(case.pop("rows"))
        cases[case_name] = case
    write_csv(RESULTS / "skew_prismatic_runs.csv", rows)
    return {"h": H, "t_final": T_FINAL, "dimension": DIM, "stage_size": STAGE_SIZE, "cases": cases}


def plot_results(summary: dict) -> None:
    import matplotlib.pyplot as plt

    labels = []
    dense_runtime = []
    sparse_runtime = []
    nnz = {"block": [], "pruned": [], "dense": []}
    colors = {"block": [], "pruned": [], "dense": []}
    for case_name, case in summary["cases"].items():
        labels.append(case_name.replace("skew_prismatic_", ""))
        dense_runtime.append(case["runs"]["dense_jacfwd_csr"]["runtime_sec"])
        sparse_runtime.append(case["runs"]["generated_block_jvp_pruned"]["runtime_sec"])
        for key, pattern_key in [("block", "generated_block_superset"), ("pruned", "generated_block_jvp_pruned"), ("dense", "dense_validation")]:
            nnz[key].append(case["patterns"][pattern_key]["nnz"])
            colors[key].append(case["patterns"][pattern_key]["colors"])
    xs = np.arange(len(labels))
    fig, ax = plt.subplots(figsize=(8.6, 4.0))
    ax.bar(xs - 0.18, dense_runtime, width=0.36, label="dense jacfwd CSR")
    ax.bar(xs + 0.18, sparse_runtime, width=0.36, label="generated-block JVP-pruned")
    ax.set_yscale("log")
    ax.set_ylabel("runtime seconds")
    ax.set_xticks(xs)
    ax.set_xticklabels(labels)
    ax.grid(True, axis="y", alpha=0.35)
    ax.legend()
    fig.tight_layout()
    fig.savefig(RESULTS / "skew_prismatic_runtime.png", dpi=180)
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(10.2, 4.0))
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
    fig.savefig(RESULTS / "skew_prismatic_patterns.png", dpi=180)
    plt.close(fig)


def write_report(summary: dict) -> None:
    lines = [
        "# v043 Experiment Report",
        "",
        "Generated by `run_v043.py`.",
        "",
        "## Purpose",
        "",
        "- Add a prismatic lower-pair test instead of another revolute-chain variant.",
        "- Keep a square FullVA residual: two perpendicular slide constraints, three orientation-lock constraints, and one free sliding coordinate.",
        "- Include Brown-McPhee-style sliding friction whose Jacobian depends on the constraint normal load.",
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
            f"- Trajectory diff: position {sparse_run['position_error_vs_dense']:.3e}, "
            f"velocity {sparse_run['velocity_error_vs_dense']:.3e}; endpoint velocity constraint "
            f"{sparse_run['max_endpoint_velocity_constraint_norm']:.3e}; orientation acceleration "
            f"{sparse_run['max_stage_orientation_acceleration_constraint_norm']:.3e}."
        )
        lines.append("")
    lines.extend(
        [
            "## Interpretation",
            "",
            "- This is the first non-revolute lower-pair test in the local sequence.",
            "- The free sliding coordinate is handled by axial translation collocation, while perpendicular position/velocity/acceleration and orientation-lock rows enforce the prismatic joint.",
            "- Dense Jacobians are used for validation only; the sparse path builds a generated block superset and prunes it with batched JVPs.",
            "- The next gap is an interbody prismatic/cylindrical joint in a larger chain.",
            "",
            "## Outputs",
            "",
            "- `skew_prismatic_runs.csv`",
            "- `summary_v043.json`",
            "- `skew_prismatic_runtime.png`",
            "- `skew_prismatic_patterns.png`",
            "",
        ]
    )
    (RESULTS / "v043_report.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    experiment = run_experiment()
    plot_results(experiment)
    summary = {
        "version": "v043_skew_prismatic_lower_pair",
        "python": platform.python_version(),
        "platform": platform.platform(),
        "numpy": np.__version__,
        "scipy": __import__("scipy").__version__,
        "jax": jax.__version__,
        "source_versions": ["v042_skew_axis_triple_revolute", "v040_generated_block_triple_pattern"],
        "model": {
            "cases": CASES,
            "method": "single_body_skew_prismatic_gauss6_fullva",
            "h": H,
            "t_final": T_FINAL,
            "dimension": DIM,
            "stage_size": STAGE_SIZE,
        },
        "experiment": experiment,
        "runtime_sec": time.perf_counter() - started,
    }
    with (RESULTS / "summary_v043.json").open("w", encoding="utf-8") as f:
        json.dump(json_safe(summary), f, indent=2, sort_keys=True)
    write_report(experiment)


if __name__ == "__main__":
    main()
