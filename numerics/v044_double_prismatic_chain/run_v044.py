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
V043_PATH = ROOT / "v043_skew_prismatic_lower_pair" / "run_v043.py"

N_BODIES = 2
N_JOINTS = 2
N_STAGES = 3
BODY_SIZE = 18
LAMBDA_SIZE = 5
STAGE_SIZE = N_BODIES * BODY_SIZE + N_JOINTS * LAMBDA_SIZE
DIM = N_STAGES * STAGE_SIZE
H = 0.02
T_FINAL = 0.08
PATTERN_ATOL = 1.0e-14
SPARSITY_ATOL = 1.0e-12
CASES = {"double_prismatic_smooth": 0.50, "double_prismatic_sharp": 0.05}

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


def load_v043():
    spec = importlib.util.spec_from_file_location("v043_skew_prismatic_lower_pair", V043_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


v043 = load_v043()
qp = v043.qp
jax = v043.jax


@dataclass(frozen=True)
class Params:
    masses: np.ndarray
    Js: np.ndarray
    s_prev: np.ndarray
    s_next: np.ndarray
    axis_prev: np.ndarray
    axis_next: np.ndarray
    twist_prev: np.ndarray
    twist_next: np.ndarray
    ground_axis: np.ndarray
    ground_twist: np.ndarray
    joint_basis: np.ndarray
    gravity: np.ndarray
    external_forces_world: np.ndarray
    external_torques_body: np.ndarray
    mu_s: float
    mu_d: float
    stribeck_velocity: float
    viscous_damping: float
    friction_radius: float
    slide0: np.ndarray
    slide_rate0: np.ndarray


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
    return v043.rot_to_quat(R)


def perp_basis(axis: np.ndarray) -> np.ndarray:
    return v043.perp_basis(axis)


def rotate_axis_twist_to_targets(axis_body: np.ndarray, twist_body: np.ndarray, axis_world: np.ndarray, twist_world: np.ndarray) -> np.ndarray:
    axis_world = normalize(axis_world)
    twist_world = normalize(twist_world - axis_world * float(twist_world @ axis_world))
    R_align = align_rot(axis_body, axis_world)
    twist_aligned = R_align @ twist_body
    basis_a = twist_world
    basis_b = np.cross(axis_world, basis_a)
    angle = np.arctan2(float(twist_aligned @ basis_b), float(twist_aligned @ basis_a))
    return axis_angle_rot(axis_world, -angle) @ R_align


def make_params(stribeck_velocity: float) -> Params:
    ground_axis = normalize([0.31, 0.78, 0.54])
    ground_basis = perp_basis(ground_axis)
    ground_twist = ground_basis[0]

    axis_prev = np.array(
        [
            normalize([0.18, 0.91, -0.37]),
            normalize([-0.24, 0.87, 0.43]),
        ]
    )
    axis_next = np.array(
        [
            normalize([0.42, 0.69, 0.59]),
            normalize([0.0, 1.0, 0.0]),
        ]
    )
    twist_prev = np.array(
        [
            normalize(np.cross(axis_prev[0], normalize([0.7, -0.2, 0.4]))),
            normalize(np.cross(axis_prev[1], normalize([0.2, 0.6, -0.7]))),
        ]
    )
    twist_next = np.array(
        [
            normalize(np.cross(axis_next[0], normalize([-0.1, 0.9, 0.2]))),
            normalize([1.0, 0.0, 0.0]),
        ]
    )
    R0 = rotate_axis_twist_to_targets(axis_prev[0], twist_prev[0], ground_axis, ground_twist)
    parent_axis = R0 @ axis_next[0]
    parent_twist = R0 @ twist_next[0]
    R1 = rotate_axis_twist_to_targets(axis_prev[1], twist_prev[1], parent_axis, parent_twist)
    joint_basis = np.stack([perp_basis(ground_axis), perp_basis(parent_axis)])
    return Params(
        masses=np.array([2.7, 1.9]),
        Js=np.array([np.diag([0.11, 0.24, 0.31]), np.diag([0.08, 0.19, 0.27])]),
        s_prev=np.array([[0.12, -0.04, 0.18], [-0.08, 0.05, 0.16]]),
        s_next=np.array([[0.16, 0.02, -0.20], [0.0, 0.0, 0.0]]),
        axis_prev=axis_prev,
        axis_next=axis_next,
        twist_prev=twist_prev,
        twist_next=twist_next,
        ground_axis=ground_axis,
        ground_twist=ground_twist,
        joint_basis=joint_basis,
        gravity=np.array([0.0, 0.0, -9.81]),
        external_forces_world=np.array([[0.8, -0.35, 0.25], [-0.25, 0.45, -0.10]]),
        external_torques_body=np.array([[0.03, -0.02, 0.015], [-0.018, 0.026, -0.014]]),
        mu_s=0.30,
        mu_d=0.20,
        stribeck_velocity=float(stribeck_velocity),
        viscous_damping=0.030,
        friction_radius=1.0,
        slide0=np.array([0.35, 0.42]),
        slide_rate0=np.array([0.42, -0.26]),
    )


def initial_rotations(params: Params) -> list[np.ndarray]:
    R0 = rotate_axis_twist_to_targets(params.axis_prev[0], params.twist_prev[0], params.ground_axis, params.ground_twist)
    parent_axis = R0 @ params.axis_next[0]
    parent_twist = R0 @ params.twist_next[0]
    R1 = rotate_axis_twist_to_targets(params.axis_prev[1], params.twist_prev[1], parent_axis, parent_twist)
    return [R0, R1]


def initial_state(params: Params) -> State:
    R = initial_rotations(params)
    p = np.array([rot_to_quat(R[i]) for i in range(N_BODIES)])
    p0 = params.slide0[0] * params.ground_axis
    r0 = p0 - R[0] @ params.s_prev[0]
    parent_point = r0 + R[0] @ params.s_next[0]
    parent_axis = R[0] @ params.axis_next[0]
    p1 = parent_point + params.slide0[1] * parent_axis
    r1 = p1 - R[1] @ params.s_prev[1]
    v0 = params.slide_rate0[0] * params.ground_axis
    v1 = v0 + params.slide_rate0[1] * parent_axis
    return State(r=np.array([r0, r1]), p=p, v=np.array([v0, v1]), w=np.zeros((N_BODIES, 3)))


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


def body_slice(stage: int, body: int, field: str) -> slice:
    offsets = {"u": 0, "r": 3, "v": 6, "w": 9, "a": 12, "alpha": 15}
    base = stage * STAGE_SIZE + body * BODY_SIZE + offsets[field]
    return slice(base, base + 3)


def lambda_slice(stage: int, joint: int) -> slice:
    base = stage * STAGE_SIZE + N_BODIES * BODY_SIZE + joint * LAMBDA_SIZE
    return slice(base, base + LAMBDA_SIZE)


def row_slice(stage: int, start: int, stop: int) -> slice:
    base = stage * STAGE_SIZE
    return slice(base + start, base + stop)


def unpack_stages(x):
    stages = []
    for stage in range(N_STAGES):
        base = stage * STAGE_SIZE
        bodies = x[base : base + N_BODIES * BODY_SIZE].reshape((N_BODIES, BODY_SIZE))
        lam = x[base + N_BODIES * BODY_SIZE : base + STAGE_SIZE].reshape((N_JOINTS, LAMBDA_SIZE))
        stages.append(
            {
                "u": bodies[:, 0:3],
                "r": bodies[:, 3:6],
                "v": bodies[:, 6:9],
                "w": bodies[:, 9:12],
                "a": bodies[:, 12:15],
                "alpha": bodies[:, 15:18],
                "lambda": lam,
            }
        )
    return stages


def joint_axes_from_state(state: State, params: Params) -> tuple[np.ndarray, np.ndarray]:
    R0 = qp.quat_to_rot(state.p[0])
    return params.ground_axis, R0 @ params.axis_next[0]


def stage_guess(state: State, h: float, params: Params) -> np.ndarray:
    c, _, _ = qp.gauss_legendre_coefficients(N_STAGES)
    axis0, axis1 = joint_axes_from_state(state, params)
    accel0 = float(axis0 @ (params.gravity + params.external_forces_world[0] / params.masses[0])) * axis0
    rel_accel1 = float(axis1 @ (params.gravity + params.external_forces_world[1] / params.masses[1] - accel0)) * axis1
    accel = np.array([accel0, accel0 + rel_accel1])
    blocks = []
    for ci in c:
        u = np.zeros((N_BODIES, 3))
        w = np.zeros((N_BODIES, 3))
        alpha = np.zeros((N_BODIES, 3))
        v = state.v + ci * h * accel
        r = state.r + ci * h * state.v + 0.5 * (ci * h) ** 2 * accel
        lam = np.zeros((N_JOINTS, LAMBDA_SIZE))
        force1 = params.masses[1] * accel[1] - params.masses[1] * params.gravity - params.external_forces_world[1]
        force0 = params.masses[0] * accel[0] - params.masses[0] * params.gravity - params.external_forces_world[0] + force1
        for joint, force in enumerate([force0, force1]):
            lam[joint, 0] = force @ params.joint_basis[joint, 0]
            lam[joint, 1] = force @ params.joint_basis[joint, 1]
        blocks.extend([u.reshape(-1), r.reshape(-1), v.reshape(-1), w.reshape(-1), accel.reshape(-1), alpha.reshape(-1), lam.reshape(-1)])
    return np.concatenate(blocks)


def brown_mcphee_scalar_jax(v, normal_load, mu_s, mu_d, stribeck_velocity, viscous_damping, friction_radius):
    return v043.brown_mcphee_scalar_jax(v, normal_load, mu_s, mu_d, stribeck_velocity, viscous_damping, friction_radius)


def compose_right_quat_jax_safe(q, u):
    return v043.compose_right_quat_jax_safe(q, u)


def right_jacobian_inverse_apply_jax_safe(u, w):
    return v043.right_jacobian_inverse_apply_jax_safe(u, w)


def joint_kinematics_jax(st, R, params_arrays, x_dtype):
    s_prev, s_next, axis_prev, axis_next, twist_prev, twist_next, ground_axis, ground_twist, joint_basis = params_arrays
    child_point = [st["r"][j] + R[j] @ s_prev[j] for j in range(N_JOINTS)]
    child_vel = [st["v"][j] + R[j] @ jnp.cross(st["w"][j], s_prev[j]) for j in range(N_JOINTS)]
    child_acc = [
        st["a"][j] + R[j] @ (jnp.cross(st["alpha"][j], s_prev[j]) + jnp.cross(st["w"][j], jnp.cross(st["w"][j], s_prev[j])))
        for j in range(N_JOINTS)
    ]
    child_axis = [R[j] @ axis_prev[j] for j in range(N_JOINTS)]
    child_twist = [R[j] @ twist_prev[j] for j in range(N_JOINTS)]
    child_axis_rate = [R[j] @ jnp.cross(st["w"][j], axis_prev[j]) for j in range(N_JOINTS)]
    child_twist_rate = [R[j] @ jnp.cross(st["w"][j], twist_prev[j]) for j in range(N_JOINTS)]
    child_axis_acc = [
        R[j] @ (jnp.cross(st["alpha"][j], axis_prev[j]) + jnp.cross(st["w"][j], jnp.cross(st["w"][j], axis_prev[j])))
        for j in range(N_JOINTS)
    ]
    child_twist_acc = [
        R[j] @ (jnp.cross(st["alpha"][j], twist_prev[j]) + jnp.cross(st["w"][j], jnp.cross(st["w"][j], twist_prev[j])))
        for j in range(N_JOINTS)
    ]
    parent_point = [jnp.zeros(3, dtype=x_dtype), st["r"][0] + R[0] @ s_next[0]]
    parent_vel = [jnp.zeros(3, dtype=x_dtype), st["v"][0] + R[0] @ jnp.cross(st["w"][0], s_next[0])]
    parent_acc = [
        jnp.zeros(3, dtype=x_dtype),
        st["a"][0] + R[0] @ (jnp.cross(st["alpha"][0], s_next[0]) + jnp.cross(st["w"][0], jnp.cross(st["w"][0], s_next[0]))),
    ]
    parent_axis = [ground_axis, R[0] @ axis_next[0]]
    parent_twist = [ground_twist, R[0] @ twist_next[0]]
    parent_axis_rate = [jnp.zeros(3, dtype=x_dtype), R[0] @ jnp.cross(st["w"][0], axis_next[0])]
    parent_twist_rate = [jnp.zeros(3, dtype=x_dtype), R[0] @ jnp.cross(st["w"][0], twist_next[0])]
    parent_axis_acc = [
        jnp.zeros(3, dtype=x_dtype),
        R[0] @ (jnp.cross(st["alpha"][0], axis_next[0]) + jnp.cross(st["w"][0], jnp.cross(st["w"][0], axis_next[0]))),
    ]
    parent_twist_acc = [
        jnp.zeros(3, dtype=x_dtype),
        R[0] @ (jnp.cross(st["alpha"][0], twist_next[0]) + jnp.cross(st["w"][0], jnp.cross(st["w"][0], twist_next[0]))),
    ]
    rel_point = [child_point[j] - parent_point[j] for j in range(N_JOINTS)]
    rel_vel = [child_vel[j] - parent_vel[j] for j in range(N_JOINTS)]
    rel_acc = [child_acc[j] - parent_acc[j] for j in range(N_JOINTS)]
    axis_res = [
        jnp.array([(child_axis[j] - parent_axis[j]) @ joint_basis[j, 0], (child_axis[j] - parent_axis[j]) @ joint_basis[j, 1]], dtype=x_dtype)
        for j in range(N_JOINTS)
    ]
    twist_res = [jnp.array([(child_twist[j] - parent_twist[j]) @ joint_basis[j, 1]], dtype=x_dtype) for j in range(N_JOINTS)]
    axis_rate = [
        jnp.array([(child_axis_rate[j] - parent_axis_rate[j]) @ joint_basis[j, 0], (child_axis_rate[j] - parent_axis_rate[j]) @ joint_basis[j, 1]], dtype=x_dtype)
        for j in range(N_JOINTS)
    ]
    twist_rate = [jnp.array([(child_twist_rate[j] - parent_twist_rate[j]) @ joint_basis[j, 1]], dtype=x_dtype) for j in range(N_JOINTS)]
    axis_acc = [
        jnp.array([(child_axis_acc[j] - parent_axis_acc[j]) @ joint_basis[j, 0], (child_axis_acc[j] - parent_axis_acc[j]) @ joint_basis[j, 1]], dtype=x_dtype)
        for j in range(N_JOINTS)
    ]
    twist_acc = [jnp.array([(child_twist_acc[j] - parent_twist_acc[j]) @ joint_basis[j, 1]], dtype=x_dtype) for j in range(N_JOINTS)]
    return {
        "rel_point": rel_point,
        "rel_vel": rel_vel,
        "rel_acc": rel_acc,
        "parent_axis": parent_axis,
        "axis_res": axis_res,
        "twist_res": twist_res,
        "axis_rate": axis_rate,
        "twist_rate": twist_rate,
        "axis_acc": axis_acc,
        "twist_acc": twist_acc,
    }


def residual_double_prismatic(
    x,
    state0,
    h,
    masses,
    Js,
    s_prev,
    s_next,
    axis_prev,
    axis_next,
    twist_prev,
    twist_next,
    ground_axis,
    ground_twist,
    joint_basis,
    gravity,
    external_forces_world,
    external_torques_body,
    mu_s,
    mu_d,
    stribeck_velocity,
    viscous_damping,
    friction_radius,
):
    r0, p0, v0, w0 = state0
    _, A, _ = qp._gauss_legendre_coefficients_jax(N_STAGES, x.dtype)
    stages = unpack_stages(x)
    params_arrays = (s_prev, s_next, axis_prev, axis_next, twist_prev, twist_next, ground_axis, ground_twist, joint_basis)
    stage_kin = []
    k = []
    for st in stages:
        p = [compose_right_quat_jax_safe(p0[i], st["u"][i]) for i in range(N_BODIES)]
        R = [qp.quat_to_rot_jax(p[i]) for i in range(N_BODIES)]
        stage_kin.append(joint_kinematics_jax(st, R, params_arrays, x.dtype) | {"R": R})
        k.append([right_jacobian_inverse_apply_jax_safe(st["u"][i], st["w"][i]) for i in range(N_BODIES)])

    initial_rel_point = []
    initial_rel_vel = []
    R0_np = [qp.quat_to_rot_jax(p0[i]) for i in range(N_BODIES)]
    state_st = {"r": r0, "v": v0, "w": w0, "a": jnp.zeros_like(v0), "alpha": jnp.zeros_like(w0)}
    initial_kin = joint_kinematics_jax(state_st, R0_np, params_arrays, x.dtype)
    initial_rel_point = initial_kin["rel_point"]
    initial_rel_vel = initial_kin["rel_vel"]

    out = []
    for si, st in enumerate(stages):
        kin = stage_kin[si]
        R = kin["R"]
        joint_force = []
        for joint in range(N_JOINTS):
            lam = st["lambda"][joint]
            normal_force = lam[0] * joint_basis[joint, 0] + lam[1] * joint_basis[joint, 1]
            normal_load = jnp.sqrt(normal_force @ normal_force + jnp.array(1.0e-24, dtype=x.dtype))
            slide_vel = kin["rel_vel"][joint] @ kin["parent_axis"][joint]
            friction = brown_mcphee_scalar_jax(slide_vel, normal_load, mu_s, mu_d, stribeck_velocity, viscous_damping, friction_radius)
            joint_force.append(normal_force + friction * kin["parent_axis"][joint])

        pvel = []
        pacc = []
        constraints = []
        u_block = []
        w_block = []
        for joint in range(N_JOINTS):
            axis = kin["parent_axis"][joint]
            r_coll_axis = (kin["rel_point"][joint] - initial_rel_point[joint] - h * sum(A[si, sj] * stage_kin[sj]["rel_vel"][joint] for sj in range(N_STAGES))) @ axis
            v_coll_axis = (kin["rel_vel"][joint] - initial_rel_vel[joint] - h * sum(A[si, sj] * stage_kin[sj]["rel_acc"][joint] for sj in range(N_STAGES))) @ axis
            pvel.append(jnp.array([kin["rel_vel"][joint] @ joint_basis[joint, 0], kin["rel_vel"][joint] @ joint_basis[joint, 1], r_coll_axis], dtype=x.dtype))
            pacc.append(jnp.array([kin["rel_acc"][joint] @ joint_basis[joint, 0], kin["rel_acc"][joint] @ joint_basis[joint, 1], v_coll_axis], dtype=x.dtype))
            u_block.append(jnp.concatenate([kin["axis_rate"][joint], kin["twist_rate"][joint]]))
            w_block.append(jnp.concatenate([kin["axis_acc"][joint], kin["twist_acc"][joint]]))
            constraints.append(jnp.concatenate([joint_basis[joint] @ kin["rel_point"][joint], kin["axis_res"][joint], kin["twist_res"][joint]]))

        dyn = []
        for body in range(N_BODIES):
            force = joint_force[body]
            if body == 0:
                force = force - joint_force[1]
            trans = masses[body] * st["a"][body] - masses[body] * gravity - external_forces_world[body] - force
            prox_torque = jnp.cross(s_prev[body], R[body].T @ joint_force[body])
            if body == 0:
                distal_torque = jnp.cross(s_next[0], R[0].T @ (-joint_force[1]))
            else:
                distal_torque = jnp.zeros(3, dtype=x.dtype)
            eta_prox = st["lambda"][body, 2:5]
            axis_torque = eta_prox[0] * jnp.cross(axis_prev[body], R[body].T @ joint_basis[body, 0])
            axis_torque += eta_prox[1] * jnp.cross(axis_prev[body], R[body].T @ joint_basis[body, 1])
            twist_torque = eta_prox[2] * jnp.cross(twist_prev[body], R[body].T @ joint_basis[body, 1])
            if body == 0:
                eta_dist = st["lambda"][1, 2:5]
                dist_axis_torque = eta_dist[0] * jnp.cross(axis_next[0], R[0].T @ joint_basis[1, 0])
                dist_axis_torque += eta_dist[1] * jnp.cross(axis_next[0], R[0].T @ joint_basis[1, 1])
                dist_twist_torque = eta_dist[2] * jnp.cross(twist_next[0], R[0].T @ joint_basis[1, 1])
            else:
                dist_axis_torque = jnp.zeros(3, dtype=x.dtype)
                dist_twist_torque = jnp.zeros(3, dtype=x.dtype)
            rot = (
                Js[body] @ st["alpha"][body]
                + jnp.cross(st["w"][body], Js[body] @ st["w"][body])
                - prox_torque
                - distal_torque
                - axis_torque
                - twist_torque
                + dist_axis_torque
                + dist_twist_torque
                - external_torques_body[body]
            )
            dyn.extend([trans, rot])
        out.extend([jnp.concatenate(pvel), jnp.concatenate(u_block), jnp.concatenate(pacc), jnp.concatenate(w_block), jnp.concatenate(dyn), jnp.concatenate(constraints)])
    return jnp.concatenate(out)


R_VALUE = jax.jit(residual_double_prismatic)
R_JAC = jax.jit(jax.jacfwd(residual_double_prismatic, argnums=0))


@jax.jit
def batched_jvp(x, seeds, *args):
    def one(seed):
        return jax.jvp(lambda y: residual_double_prismatic(y, *args), (x,), (seed,))[1]

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
        jnp.asarray(params.axis_prev, dtype=jnp.float64),
        jnp.asarray(params.axis_next, dtype=jnp.float64),
        jnp.asarray(params.twist_prev, dtype=jnp.float64),
        jnp.asarray(params.twist_next, dtype=jnp.float64),
        jnp.asarray(params.ground_axis, dtype=jnp.float64),
        jnp.asarray(params.ground_twist, dtype=jnp.float64),
        jnp.asarray(params.joint_basis, dtype=jnp.float64),
        jnp.asarray(params.gravity, dtype=jnp.float64),
        jnp.asarray(params.external_forces_world, dtype=jnp.float64),
        jnp.asarray(params.external_torques_body, dtype=jnp.float64),
        jnp.asarray(params.mu_s, dtype=jnp.float64),
        jnp.asarray(params.mu_d, dtype=jnp.float64),
        jnp.asarray(params.stribeck_velocity, dtype=jnp.float64),
        jnp.asarray(params.viscous_damping, dtype=jnp.float64),
        jnp.asarray(params.friction_radius, dtype=jnp.float64),
    )


def next_state_from_stages(state: State, h: float, stages) -> State:
    _, _, b = qp.gauss_legendre_coefficients(N_STAGES)
    k = [[qp.right_jacobian_inverse_apply(st["u"][i], st["w"][i]) for i in range(N_BODIES)] for st in stages]
    r = state.r + h * sum(b[j] * stages[j]["v"] for j in range(N_STAGES))
    p = np.array([qp.compose_right_quat(state.p[i], h * sum(b[j] * k[j][i] for j in range(N_STAGES))) for i in range(N_BODIES)])
    v = state.v + h * sum(b[j] * stages[j]["a"] for j in range(N_STAGES))
    w = state.w + h * sum(b[j] * stages[j]["alpha"] for j in range(N_STAGES))
    return State(r=r, p=p, v=v, w=w)


def constraint_parts_np(state: State, params: Params) -> tuple[np.ndarray, np.ndarray]:
    args = build_args(state, H, params)
    state0 = args[0]
    p0 = state0[1]
    R = [qp.quat_to_rot_jax(p0[i]) for i in range(N_BODIES)]
    st = {"r": state0[0], "v": state0[2], "w": state0[3], "a": jnp.zeros_like(state0[2]), "alpha": jnp.zeros_like(state0[3])}
    kin = joint_kinematics_jax(
        st,
        R,
        (
            args[4],
            args[5],
            args[6],
            args[7],
            args[8],
            args[9],
            args[10],
            args[11],
            args[12],
        ),
        jnp.float64,
    )
    con = []
    vel = []
    for joint in range(N_JOINTS):
        con.extend(np.asarray(args[12][joint] @ kin["rel_point"][joint], dtype=float).tolist())
        con.extend(np.asarray(kin["axis_res"][joint], dtype=float).tolist())
        con.extend(np.asarray(kin["twist_res"][joint], dtype=float).tolist())
        vel.extend([float(kin["rel_vel"][joint] @ args[12][joint, 0]), float(kin["rel_vel"][joint] @ args[12][joint, 1])])
        vel.extend(np.asarray(kin["axis_rate"][joint], dtype=float).tolist())
        vel.extend(np.asarray(kin["twist_rate"][joint], dtype=float).tolist())
    return np.array(con), np.array(vel)


def stage_acceleration_parts(state: State, stages, params: Params) -> tuple[float, float]:
    max_pos = 0.0
    max_ori = 0.0
    for st in stages:
        p = [qp.compose_right_quat(state.p[i], st["u"][i]) for i in range(N_BODIES)]
        R = [qp.quat_to_rot(p[i]) for i in range(N_BODIES)]
        rel_acc = []
        child_acc0 = st["a"][0] + R[0] @ (np.cross(st["alpha"][0], params.s_prev[0]) + np.cross(st["w"][0], np.cross(st["w"][0], params.s_prev[0])))
        rel_acc.append(child_acc0)
        parent_acc1 = st["a"][0] + R[0] @ (np.cross(st["alpha"][0], params.s_next[0]) + np.cross(st["w"][0], np.cross(st["w"][0], params.s_next[0])))
        child_acc1 = st["a"][1] + R[1] @ (np.cross(st["alpha"][1], params.s_prev[1]) + np.cross(st["w"][1], np.cross(st["w"][1], params.s_prev[1])))
        rel_acc.append(child_acc1 - parent_acc1)
        for joint in range(N_JOINTS):
            max_pos = max(max_pos, float(np.linalg.norm([rel_acc[joint] @ params.joint_basis[joint, 0], rel_acc[joint] @ params.joint_basis[joint, 1]])))
        axis_acc0 = R[0] @ (np.cross(st["alpha"][0], params.axis_prev[0]) + np.cross(st["w"][0], np.cross(st["w"][0], params.axis_prev[0])))
        twist_acc0 = R[0] @ (np.cross(st["alpha"][0], params.twist_prev[0]) + np.cross(st["w"][0], np.cross(st["w"][0], params.twist_prev[0])))
        axis_parent1 = R[0] @ (np.cross(st["alpha"][0], params.axis_next[0]) + np.cross(st["w"][0], np.cross(st["w"][0], params.axis_next[0])))
        twist_parent1 = R[0] @ (np.cross(st["alpha"][0], params.twist_next[0]) + np.cross(st["w"][0], np.cross(st["w"][0], params.twist_next[0])))
        axis_child1 = R[1] @ (np.cross(st["alpha"][1], params.axis_prev[1]) + np.cross(st["w"][1], np.cross(st["w"][1], params.axis_prev[1])))
        twist_child1 = R[1] @ (np.cross(st["alpha"][1], params.twist_prev[1]) + np.cross(st["w"][1], np.cross(st["w"][1], params.twist_prev[1])))
        max_ori = max(
            max_ori,
            float(
                np.linalg.norm(
                    [
                        axis_acc0 @ params.joint_basis[0, 0],
                        axis_acc0 @ params.joint_basis[0, 1],
                        twist_acc0 @ params.joint_basis[0, 1],
                        (axis_child1 - axis_parent1) @ params.joint_basis[1, 0],
                        (axis_child1 - axis_parent1) @ params.joint_basis[1, 1],
                        (twist_child1 - twist_parent1) @ params.joint_basis[1, 1],
                    ]
                )
            ),
        )
    return max_pos, max_ori


def csr_from_dense(jac: np.ndarray):
    mask = np.abs(jac) > SPARSITY_ATOL
    return sparse.csr_matrix(np.where(mask, jac, 0.0))


def make_pattern(mask: np.ndarray):
    return v043.make_pattern(mask)


def make_seed_matrix(sp):
    return v043.make_seed_matrix(sp)


def mark_body(mask: np.ndarray, rows: slice, stage: int, body: int, fields: list[str]) -> None:
    for field in fields:
        mask[rows, body_slice(stage, body, field)] = True


def mark_lambda(mask: np.ndarray, rows: slice, stage: int, joint: int) -> None:
    mask[rows, lambda_slice(stage, joint)] = True


def generated_block_superset_pattern():
    mask = np.zeros((DIM, DIM), dtype=bool)
    for stage in range(N_STAGES):
        pvel_rows = row_slice(stage, 0, 6)
        u_rows = row_slice(stage, 6, 12)
        pacc_rows = row_slice(stage, 12, 18)
        w_rows = row_slice(stage, 18, 24)
        dyn_rows = row_slice(stage, 24, 36)
        con_rows = row_slice(stage, 36, 46)
        for body in range(N_BODIES):
            mark_body(mask, pvel_rows, stage, body, ["u", "r", "v", "w"])
            mark_body(mask, u_rows, stage, body, ["u", "w"])
            mark_body(mask, pacc_rows, stage, body, ["u", "v", "w", "a", "alpha"])
            mark_body(mask, w_rows, stage, body, ["u", "w", "alpha"])
            mark_body(mask, dyn_rows, stage, body, ["u", "v", "w", "a", "alpha"])
            mark_body(mask, con_rows, stage, body, ["u", "r"])
        for joint in range(N_JOINTS):
            mark_lambda(mask, dyn_rows, stage, joint)
        for sj in range(N_STAGES):
            for body in range(N_BODIES):
                mark_body(mask, pvel_rows, sj, body, ["u", "v", "w"])
                mark_body(mask, pacc_rows, sj, body, ["u", "w", "a", "alpha"])
    return make_pattern(mask)


def colored_jvp_csr_and_mask(x: np.ndarray, args, sp, seeds: np.ndarray, threshold: float):
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


def build_pruned_pattern(params: Params, superset) -> tuple[object, float]:
    seeds = make_seed_matrix(superset)
    state = initial_state(params)
    pattern = np.zeros((DIM, DIM), dtype=bool)
    started = time.perf_counter()
    for _ in range(int(round(T_FINAL / H))):
        x = stage_guess(state, H, params)
        args = build_args(state, H, params)
        for _it in range(12):
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


def dense_validation_pattern(params: Params) -> tuple[object, float]:
    state = initial_state(params)
    pattern = None
    started = time.perf_counter()
    for _ in range(int(round(T_FINAL / H))):
        x = stage_guess(state, H, params)
        args = build_args(state, H, params)
        for _it in range(12):
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


def pattern_relation(candidate, reference) -> dict:
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


def jvp_csr(x: np.ndarray, args, sp, seeds: np.ndarray):
    started = time.perf_counter()
    csr, _ = colored_jvp_csr_and_mask(x, args, sp, seeds, SPARSITY_ATOL)
    return csr, time.perf_counter() - started


def gauss_step(state: State, params: Params, solver: str, sp, seeds: np.ndarray):
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
        raise RuntimeError(f"double-prismatic Newton failed residual={last_norm:.3e}")
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
        "max_quaternion_unit_error": float(np.max(np.abs(np.linalg.norm(next_state.p, axis=1) - 1.0))),
    }
    return next_state, diag


def integrate(params: Params, solver: str, sp, seeds: np.ndarray):
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


def warm_jax(params: Params, sp, seeds: np.ndarray) -> None:
    state = initial_state(params)
    x = stage_guess(state, H, params)
    args = build_args(state, H, params)
    x_jax = jnp.asarray(x, dtype=jnp.float64)
    np.asarray(R_VALUE(x_jax, *args), dtype=float)
    np.asarray(R_JAC(x_jax, *args), dtype=float)
    np.asarray(batched_jvp(x_jax, jnp.asarray(seeds, dtype=jnp.float64), *args), dtype=float)


def warm_integrators(params: Params, sp, seeds: np.ndarray) -> None:
    integrate(params, "dense_jacfwd_csr", sp, seeds)
    integrate(params, "generated_block_jvp_pruned", sp, seeds)


def row_from_run(case_name: str, solver: str, out: dict, runtime: float, sp, relation: dict, pattern_build: float, dense_pattern_sec: float, perr: float, verr: float):
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
    pruned, pruned_build_sec = build_pruned_pattern(params, block)
    seeds = make_seed_matrix(pruned)
    warm_jax(params, pruned, seeds)
    dense_pattern, dense_pattern_sec = dense_validation_pattern(params)
    warm_integrators(params, pruned, seeds)
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
    write_csv(RESULTS / "double_prismatic_runs.csv", rows)
    return {"h": H, "t_final": T_FINAL, "dimension": DIM, "stage_size": STAGE_SIZE, "cases": cases}


def plot_results(summary: dict) -> None:
    import matplotlib.pyplot as plt

    labels = []
    dense_runtime = []
    sparse_runtime = []
    nnz = {"block": [], "pruned": [], "dense": []}
    colors = {"block": [], "pruned": [], "dense": []}
    for case_name, case in summary["cases"].items():
        labels.append(case_name.replace("double_prismatic_", ""))
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
    fig.savefig(RESULTS / "double_prismatic_runtime.png", dpi=180)
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
    fig.savefig(RESULTS / "double_prismatic_patterns.png", dpi=180)
    plt.close(fig)


def write_report(summary: dict) -> None:
    lines = [
        "# v044 Experiment Report",
        "",
        "Generated by `run_v044.py`.",
        "",
        "## Purpose",
        "",
        "- Extend v043 from one ground prismatic joint to a two-body chain with one ground prismatic and one interbody prismatic joint.",
        "- Keep the square Gauss6 FullVA residual: perpendicular velocity/acceleration rows, orientation-lock rows, axial collocation rows, and constraint rows.",
        "- Test whether generated-block JVP-pruned sparse AD remains exact on a 138D non-revolute lower-pair system.",
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
            "- v044 is the first interbody non-revolute lower-pair test in the local sequence.",
            "- Compared with v043, the second sliding joint couples child and parent positions, velocities, orientations, reaction forces, and friction loads.",
            "- Dense Jacobians are still used for validation only; sparse pattern acquisition uses a generated block superset plus batched JVP pruning.",
            "- The remaining gap is a mixed revolute-prismatic or cylindrical chain where the prismatic axis rotates with a moving parent.",
            "",
            "## Outputs",
            "",
            "- `double_prismatic_runs.csv`",
            "- `summary_v044.json`",
            "- `double_prismatic_runtime.png`",
            "- `double_prismatic_patterns.png`",
            "",
        ]
    )
    (RESULTS / "v044_report.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    experiment = run_experiment()
    plot_results(experiment)
    summary = {
        "version": "v044_double_prismatic_chain",
        "python": platform.python_version(),
        "platform": platform.platform(),
        "numpy": np.__version__,
        "scipy": __import__("scipy").__version__,
        "jax": jax.__version__,
        "source_versions": ["v043_skew_prismatic_lower_pair", "v040_generated_block_triple_pattern"],
        "model": {
            "cases": CASES,
            "method": "two_body_double_prismatic_gauss6_fullva",
            "h": H,
            "t_final": T_FINAL,
            "dimension": DIM,
            "stage_size": STAGE_SIZE,
        },
        "experiment": experiment,
        "runtime_sec": time.perf_counter() - started,
    }
    with (RESULTS / "summary_v044.json").open("w", encoding="utf-8") as f:
        json.dump(json_safe(summary), f, indent=2, sort_keys=True)
    write_report(experiment)


if __name__ == "__main__":
    main()
