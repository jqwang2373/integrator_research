from __future__ import annotations

from dataclasses import dataclass

import jax

jax.config.update("jax_enable_x64", True)
import jax.numpy as jnp
import numpy as np


Array = np.ndarray


def hat(w: Array) -> Array:
    w = np.asarray(w, dtype=float).reshape(3)
    return np.array(
        [
            [0.0, -w[2], w[1]],
            [w[2], 0.0, -w[0]],
            [-w[1], w[0], 0.0],
        ]
    )


def vee(W: Array) -> Array:
    return np.array([W[2, 1], W[0, 2], W[1, 0]], dtype=float)


def exp_so3(w: Array) -> Array:
    w = np.asarray(w, dtype=float).reshape(3)
    theta = float(np.linalg.norm(w))
    W = hat(w)
    eye = np.eye(3)
    if theta < 1.0e-8:
        W2 = W @ W
        return eye + W + 0.5 * W2 + (W2 @ W) / 6.0
    return eye + np.sin(theta) / theta * W + (1.0 - np.cos(theta)) / (theta * theta) * (W @ W)


def log_so3(R: Array) -> Array:
    c = 0.5 * (np.trace(R) - 1.0)
    theta = float(np.arccos(np.clip(c, -1.0, 1.0)))
    if theta < 1.0e-8:
        return vee(0.5 * (R - R.T))
    return theta / (2.0 * np.sin(theta)) * vee(R - R.T)


def quat_normalize(q: Array) -> Array:
    q = np.asarray(q, dtype=float).reshape(4)
    return q / np.linalg.norm(q)


def quat_mul(q: Array, p: Array) -> Array:
    q = np.asarray(q, dtype=float).reshape(4)
    p = np.asarray(p, dtype=float).reshape(4)
    q0, qv = q[0], q[1:4]
    p0, pv = p[0], p[1:4]
    return np.concatenate(
        (
            np.array([q0 * p0 - float(qv @ pv)]),
            q0 * pv + p0 * qv + np.cross(qv, pv),
        )
    )


def quat_exp(theta: Array) -> Array:
    theta = np.asarray(theta, dtype=float).reshape(3)
    angle = float(np.linalg.norm(theta))
    if angle < 1.0e-8:
        angle2 = angle * angle
        scalar = 1.0 - angle2 / 8.0 + angle2 * angle2 / 384.0
        b = 0.5 - angle2 / 48.0 + angle2 * angle2 / 3840.0
        return np.concatenate((np.array([scalar]), b * theta))
    return np.concatenate((np.array([np.cos(0.5 * angle)]), np.sin(0.5 * angle) / angle * theta))


def quat_to_rot(q: Array) -> Array:
    q = quat_normalize(q)
    w, x, y, z = q
    return np.array(
        [
            [1.0 - 2.0 * (y * y + z * z), 2.0 * (x * y - z * w), 2.0 * (x * z + y * w)],
            [2.0 * (x * y + z * w), 1.0 - 2.0 * (x * x + z * z), 2.0 * (y * z - x * w)],
            [2.0 * (x * z - y * w), 2.0 * (y * z + x * w), 1.0 - 2.0 * (x * x + y * y)],
        ]
    )


def compose_right_quat(q: Array, u: Array) -> Array:
    return quat_normalize(quat_mul(q, quat_exp(u)))


def right_jacobian_inverse_apply(u: Array, w: Array) -> Array:
    u = np.asarray(u, dtype=float).reshape(3)
    w = np.asarray(w, dtype=float).reshape(3)
    theta = float(np.linalg.norm(u))
    U = hat(u)
    if theta < 1.0e-7:
        coeff = 1.0 / 12.0 + theta * theta / 720.0
    else:
        coeff = 1.0 / (theta * theta) - (1.0 + np.cos(theta)) / (2.0 * theta * np.sin(theta))
    return (np.eye(3) + 0.5 * U + coeff * (U @ U)) @ w


def exp_quat_derivative(theta: Array) -> Array:
    theta = np.asarray(theta, dtype=float).reshape(3)
    angle = float(np.linalg.norm(theta))
    angle2 = angle * angle
    if angle < 1.0e-6:
        b = 0.5 - angle2 / 48.0 + angle2 * angle2 / 3840.0
        dc_factor = -0.25 + angle2 / 96.0 - angle2 * angle2 / 7680.0
        vv_factor = -1.0 / 24.0 + angle2 / 960.0 - angle2 * angle2 / 107520.0
    else:
        b = np.sin(0.5 * angle) / angle
        dc_factor = -0.5 * np.sin(0.5 * angle) / angle
        vv_factor = (0.5 * angle * np.cos(0.5 * angle) - np.sin(0.5 * angle)) / (angle**3)
    out = np.zeros((4, 3))
    out[0, :] = dc_factor * theta
    out[1:4, :] = b * np.eye(3) + vv_factor * np.outer(theta, theta)
    return out


def right_update_wrt_delta_quat_matrix(q0: Array) -> Array:
    q0 = quat_normalize(q0)
    qs, qv = q0[0], q0[1:4]
    out = np.zeros((4, 4))
    out[0, 0] = qs
    out[0, 1:4] = -qv
    out[1:4, 0] = qv
    out[1:4, 1:4] = qs * np.eye(3) + hat(qv)
    return out


def right_transport_matrix(theta: Array, q0: Array) -> Array:
    """T_exp for the right-action update p(theta)=p0*exp(theta/2)."""

    return right_update_wrt_delta_quat_matrix(q0) @ exp_quat_derivative(theta)


def quat_mul_jax(q, p):
    q0, qv = q[0], q[1:4]
    p0, pv = p[0], p[1:4]
    return jnp.concatenate((jnp.array([q0 * p0 - qv @ pv], dtype=q.dtype), q0 * pv + p0 * qv + jnp.cross(qv, pv)))


def quat_exp_jax(theta):
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


def compose_right_quat_jax(q, u):
    out = quat_mul_jax(q, quat_exp_jax(u))
    return out / jnp.linalg.norm(out)


def quat_to_rot_jax(q):
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


def _hat_jax(w):
    return jnp.array(
        [
            [0.0, -w[2], w[1]],
            [w[2], 0.0, -w[0]],
            [-w[1], w[0], 0.0],
        ],
        dtype=w.dtype,
    )


def _right_jacobian_inverse_apply_jax(u, w):
    theta = jnp.linalg.norm(u)
    U = _hat_jax(u)
    U2 = U @ U
    theta_safe = jnp.where(theta < 1.0e-7, 1.0, theta)
    coeff_small = 1.0 / 12.0 + theta * theta / 720.0
    coeff_large = 1.0 / (theta_safe * theta_safe) - (1.0 + jnp.cos(theta_safe)) / (
        2.0 * theta_safe * jnp.sin(theta_safe)
    )
    coeff = jnp.where(theta < 1.0e-7, coeff_small, coeff_large)
    return (jnp.eye(3, dtype=u.dtype) + 0.5 * U + coeff * U2) @ w


def _friction_torque_jax(w, mu, eps, viscous):
    eps_safe = jnp.maximum(eps, 1.0e-12)
    return -viscous * w - mu * jnp.tanh(w / eps_safe)


@dataclass(frozen=True)
class Params:
    mass: float
    J_com: Array
    s_com_to_pivot: Array
    gravity: Array
    friction_mu: float
    friction_eps: float
    viscous_damping: float

    @property
    def J_pivot(self) -> Array:
        s = self.s_com_to_pivot.reshape(3)
        return self.J_com + self.mass * ((s @ s) * np.eye(3) - np.outer(s, s))


@dataclass
class State:
    r: Array
    p: Array
    v: Array
    w: Array


def make_params(
    friction_mu: float = 0.0,
    friction_eps: float = 0.5,
    viscous_damping: float = 0.0,
) -> Params:
    return Params(
        mass=4.0,
        J_com=np.diag([0.18, 0.32, 0.41]),
        s_com_to_pivot=np.array([0.0, 0.0, 0.75]),
        gravity=np.array([0.0, 0.0, -9.81]),
        friction_mu=float(friction_mu),
        friction_eps=float(friction_eps),
        viscous_damping=float(viscous_damping),
    )


def state_R(state: State) -> Array:
    return quat_to_rot(state.p)


def initial_state(params: Params | None = None) -> State:
    params = make_params() if params is None else params
    p = quat_exp(np.array([0.65, -0.35, 0.25]))
    R = quat_to_rot(p)
    w = np.array([0.15, -0.2, 0.55])
    s = params.s_com_to_pivot
    r = -R @ s
    v = -R @ np.cross(w, s)
    return State(r=r, p=p, v=v, w=w)


def friction_torque(w: Array, params: Params) -> Array:
    w = np.asarray(w, dtype=float).reshape(3)
    eps = max(float(params.friction_eps), 1.0e-12)
    return -params.viscous_damping * w - params.friction_mu * np.tanh(w / eps)


def friction_power(w: Array, params: Params) -> float:
    return float(friction_torque(w, params) @ np.asarray(w, dtype=float).reshape(3))


def reduced_rhs_w(p: Array, w: Array, params: Params) -> Array:
    R = quat_to_rot(p)
    Jp = params.J_pivot
    s = params.s_com_to_pivot
    g_body = R.T @ params.gravity
    torque_body = -params.mass * np.cross(s, g_body)
    return np.linalg.solve(Jp, torque_body + friction_torque(w, params) - np.cross(w, Jp @ w))


def energy_state(state: State, params: Params) -> float:
    R = state_R(state)
    kinetic = 0.5 * params.mass * float(state.v @ state.v) + 0.5 * float(state.w @ params.J_com @ state.w)
    potential = -params.mass * float(params.gravity @ state.r)
    return kinetic + potential


def orientation_error(R_ref: Array, R: Array) -> float:
    return float(np.linalg.norm(log_so3(R_ref.T @ R)))


def constraint_norms(state: State, params: Params) -> tuple[float, float]:
    R = state_R(state)
    s = params.s_com_to_pivot
    pos = state.r + R @ s
    vel = state.v + R @ np.cross(state.w, s)
    return float(np.linalg.norm(pos)), float(np.linalg.norm(vel))


def dae_residual_norms(state: State, a: Array, alpha: Array, lam: Array, params: Params) -> tuple[float, float]:
    R = state_R(state)
    trans = params.mass * a - params.mass * params.gravity - lam
    rot = params.J_com @ alpha + np.cross(state.w, params.J_com @ state.w) - np.cross(
        params.s_com_to_pivot, R.T @ lam
    ) - friction_torque(state.w, params)
    return float(np.linalg.norm(trans)), float(np.linalg.norm(rot))


def reduced_step_rkmk4(state: State, h: float, params: Params) -> tuple[State, int]:
    p = state.p
    w = state.w
    l1 = h * reduced_rhs_w(p, w, params)
    k1 = h * w

    u2 = 0.5 * k1
    w2 = w + 0.5 * l1
    p2 = compose_right_quat(p, u2)
    l2 = h * reduced_rhs_w(p2, w2, params)
    k2 = h * right_jacobian_inverse_apply(u2, w2)

    u3 = 0.5 * k2
    w3 = w + 0.5 * l2
    p3 = compose_right_quat(p, u3)
    l3 = h * reduced_rhs_w(p3, w3, params)
    k3 = h * right_jacobian_inverse_apply(u3, w3)

    u4 = k3
    w4 = w + l3
    p4 = compose_right_quat(p, u4)
    l4 = h * reduced_rhs_w(p4, w4, params)
    k4 = h * right_jacobian_inverse_apply(u4, w4)

    p_next = compose_right_quat(p, (k1 + 2.0 * k2 + 2.0 * k3 + k4) / 6.0)
    w_next = w + (l1 + 2.0 * l2 + 2.0 * l3 + l4) / 6.0
    R_next = quat_to_rot(p_next)
    s = params.s_com_to_pivot
    r_next = -R_next @ s
    v_next = -R_next @ np.cross(w_next, s)
    return State(r=r_next, p=p_next, v=v_next, w=w_next), 0


def _stage_guess(state: State, h: float, params: Params) -> Array:
    root3 = np.sqrt(3.0)
    cs = [0.5 - root3 / 6.0, 0.5 + root3 / 6.0]
    alpha0 = reduced_rhs_w(state.p, state.w, params)
    blocks = []
    for c in cs:
        u = c * h * state.w
        p_i = compose_right_quat(state.p, u)
        R_i = quat_to_rot(p_i)
        w_i = state.w + c * h * alpha0
        r_i = -R_i @ params.s_com_to_pivot
        v_i = -R_i @ np.cross(w_i, params.s_com_to_pivot)
        alpha_i = reduced_rhs_w(p_i, w_i, params)
        a_i = -R_i @ (
            np.cross(alpha_i, params.s_com_to_pivot)
            + np.cross(w_i, np.cross(w_i, params.s_com_to_pivot))
        )
        lam_i = params.mass * (a_i - params.gravity)
        blocks.extend([u, r_i, v_i, w_i, a_i, alpha_i, lam_i])
    return np.concatenate(blocks)


def _unpack_stages(x: Array) -> list[dict[str, Array]]:
    stages = []
    offset = 0
    for _ in range(2):
        stage = {}
        for key in ["u", "r", "v", "w", "a", "alpha", "lambda"]:
            stage[key] = x[offset : offset + 3]
            offset += 3
        stages.append(stage)
    return stages


def _endpoint_unpack(x: Array) -> tuple[list[dict[str, Array]], dict[str, Array]]:
    stages = _unpack_stages(x[:42])
    end = {
        "u": x[42:45],
        "r": x[45:48],
        "v": x[48:51],
        "w": x[51:54],
    }
    return stages, end


def _unpack_stages_jax(x):
    stages = []
    offset = 0
    for _ in range(2):
        stages.append(
            {
                "u": x[offset : offset + 3],
                "r": x[offset + 3 : offset + 6],
                "v": x[offset + 6 : offset + 9],
                "w": x[offset + 9 : offset + 12],
                "a": x[offset + 12 : offset + 15],
                "alpha": x[offset + 15 : offset + 18],
                "lambda": x[offset + 18 : offset + 21],
            }
        )
        offset += 21
    return stages


def _endpoint_residual_jax_core(
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
    friction_mu,
    friction_eps,
    viscous_damping,
):
    root3 = jnp.sqrt(jnp.array(3.0, dtype=x.dtype))
    A = jnp.array(
        [
            [0.25, 0.25 - root3 / 6.0],
            [0.25 + root3 / 6.0, 0.25],
        ],
        dtype=x.dtype,
    )
    stages = _unpack_stages_jax(x[:42])
    end_u = x[42:45]
    end_r = x[45:48]
    end_v = x[48:51]
    end_w = x[51:54]
    ks = [_right_jacobian_inverse_apply_jax(st["u"], st["w"]) for st in stages]
    out = []
    for i, st in enumerate(stages):
        p_i = compose_right_quat_jax(p0, st["u"])
        R_i = quat_to_rot_jax(p_i)
        u_coll = st["u"] - h * (A[i, 0] * ks[0] + A[i, 1] * ks[1])
        w_coll = st["w"] - w0 - h * (A[i, 0] * stages[0]["alpha"] + A[i, 1] * stages[1]["alpha"])
        trans_dyn = mass * st["a"] - mass * gravity - st["lambda"]
        rot_dyn = (
            J_com @ st["alpha"]
            + jnp.cross(st["w"], J_com @ st["w"])
            - jnp.cross(s, R_i.T @ st["lambda"])
            - _friction_torque_jax(st["w"], friction_mu, friction_eps, viscous_damping)
        )
        pos_con = st["r"] + R_i @ s
        vel_con = st["v"] + R_i @ jnp.cross(st["w"], s)
        acc_con = st["a"] + R_i @ (jnp.cross(st["alpha"], s) + jnp.cross(st["w"], jnp.cross(st["w"], s)))
        out.extend([u_coll, w_coll, trans_dyn, rot_dyn, pos_con, vel_con, acc_con])

    p_end = compose_right_quat_jax(p0, end_u)
    R_end = quat_to_rot_jax(p_end)
    out.extend(
        [
            end_u - 0.5 * h * (ks[0] + ks[1]),
            end_w - w0 - 0.5 * h * (stages[0]["alpha"] + stages[1]["alpha"]),
            end_r + R_end @ s,
            end_v + R_end @ jnp.cross(end_w, s),
        ]
    )
    _ = r0, v0
    return jnp.concatenate(out)


_endpoint_residual_value = jax.jit(_endpoint_residual_jax_core)
_endpoint_residual_jacobian = jax.jit(jax.jacfwd(_endpoint_residual_jax_core, argnums=0))


def absolute_gauss_endpoint_step(
    state: State,
    h: float,
    params: Params,
    tol: float = 1.0e-11,
    max_iters: int = 14,
) -> tuple[State, int, dict]:
    stage0 = _stage_guess(state, h, params)
    stages0 = _unpack_stages(stage0)
    ks0 = [right_jacobian_inverse_apply(st["u"], st["w"]) for st in stages0]
    u_end0 = 0.5 * h * (ks0[0] + ks0[1])
    p_end0 = compose_right_quat(state.p, u_end0)
    R_end0 = quat_to_rot(p_end0)
    w_end0 = state.w + 0.5 * h * (stages0[0]["alpha"] + stages0[1]["alpha"])
    r_end0 = -R_end0 @ params.s_com_to_pivot
    v_end0 = -R_end0 @ np.cross(w_end0, params.s_com_to_pivot)
    x = np.concatenate((stage0, u_end0, r_end0, v_end0, w_end0))

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
        jnp.asarray(params.friction_mu, dtype=jnp.float64),
        jnp.asarray(params.friction_eps, dtype=jnp.float64),
        jnp.asarray(params.viscous_damping, dtype=jnp.float64),
    )

    last_norm = np.inf
    for it in range(max_iters):
        x_jax = jnp.asarray(x, dtype=jnp.float64)
        res = np.asarray(_endpoint_residual_value(x_jax, *args), dtype=float)
        last_norm = float(np.linalg.norm(res))
        if last_norm < tol:
            break
        J = np.asarray(_endpoint_residual_jacobian(x_jax, *args), dtype=float)
        delta = np.linalg.solve(J, -res)
        x = x + delta
        if np.linalg.norm(delta) < tol:
            break
    else:
        raise RuntimeError(f"quaternion endpoint solve did not converge, residual={last_norm:.3e}")

    stages, end = _endpoint_unpack(x)
    p_end = compose_right_quat(state.p, end["u"])
    next_state = State(r=end["r"], p=p_end, v=end["v"], w=end["w"])
    max_stage_constraint = 0.0
    max_stage_force = 0.0
    max_stage_torque = 0.0
    max_lambda = 0.0
    for st in stages:
        p_i = compose_right_quat(state.p, st["u"])
        R_i = quat_to_rot(p_i)
        st_state = State(r=st["r"], p=p_i, v=st["v"], w=st["w"])
        max_stage_constraint = max(max_stage_constraint, float(np.linalg.norm(st["r"] + R_i @ params.s_com_to_pivot)))
        fr, tr = dae_residual_norms(st_state, st["a"], st["alpha"], st["lambda"], params)
        max_stage_force = max(max_stage_force, fr)
        max_stage_torque = max(max_stage_torque, tr)
        max_lambda = max(max_lambda, float(np.linalg.norm(st["lambda"])))
    diag = {
        "newton_iterations": it + 1,
        "stage_residual_norm": last_norm,
        "max_stage_constraint_norm": max_stage_constraint,
        "max_stage_force_residual_norm": max_stage_force,
        "max_stage_torque_residual_norm": max_stage_torque,
        "lambda_norm_max": max_lambda,
        "max_quaternion_unit_error": float(abs(np.linalg.norm(next_state.p) - 1.0)),
    }
    return next_state, it + 1, diag


def integrate(method: str, h: float, t_final: float, params: Params | None = None) -> dict:
    params = make_params() if params is None else params
    state = initial_state(params)
    n_steps = int(round(t_final / h))
    if abs(n_steps * h - t_final) > 1.0e-12:
        raise ValueError("h must divide t_final")

    E0 = energy_state(state, params)
    prev_energy = E0
    max_energy = 0.0
    max_step_energy_increase = 0.0
    max_constraint = 0.0
    max_velocity_constraint = 0.0
    max_stage_constraint = 0.0
    max_stage_force = 0.0
    max_stage_torque = 0.0
    max_lambda = 0.0
    max_quat_unit_error = abs(np.linalg.norm(state.p) - 1.0)
    max_friction_power = friction_power(state.w, params)
    min_friction_power = max_friction_power
    total_iters = 0
    for _ in range(n_steps):
        if method == "reduced_rkmk4":
            state, niters = reduced_step_rkmk4(state, h, params)
            total_iters += niters
        elif method == "quaternion_gauss_lie4_endpoint_jax":
            state, niters, diag = absolute_gauss_endpoint_step(state, h, params)
            total_iters += niters
            max_stage_constraint = max(max_stage_constraint, diag["max_stage_constraint_norm"])
            max_stage_force = max(max_stage_force, diag["max_stage_force_residual_norm"])
            max_stage_torque = max(max_stage_torque, diag["max_stage_torque_residual_norm"])
            max_lambda = max(max_lambda, diag["lambda_norm_max"])
            max_quat_unit_error = max(max_quat_unit_error, diag["max_quaternion_unit_error"])
        else:
            raise ValueError(f"unknown method: {method}")
        cn, cv = constraint_norms(state, params)
        energy = energy_state(state, params)
        max_step_energy_increase = max(max_step_energy_increase, energy - prev_energy)
        prev_energy = energy
        power = friction_power(state.w, params)
        max_friction_power = max(max_friction_power, power)
        min_friction_power = min(min_friction_power, power)
        max_constraint = max(max_constraint, cn)
        max_velocity_constraint = max(max_velocity_constraint, cv)
        max_energy = max(max_energy, abs(energy - E0) / max(abs(E0), 1.0e-30))
        max_quat_unit_error = max(max_quat_unit_error, float(abs(np.linalg.norm(state.p) - 1.0)))

    final_energy = energy_state(state, params)
    return {
        "state": state,
        "steps": n_steps,
        "max_energy_relative_error": max_energy,
        "final_energy_change": final_energy - E0,
        "final_energy_relative_change": (final_energy - E0) / max(abs(E0), 1.0e-30),
        "max_step_energy_increase": max_step_energy_increase,
        "max_friction_power": max_friction_power,
        "min_friction_power": min_friction_power,
        "max_endpoint_constraint_norm": max_constraint,
        "max_endpoint_velocity_constraint_norm": max_velocity_constraint,
        "max_stage_constraint_norm": max_stage_constraint,
        "max_stage_force_residual_norm": max_stage_force,
        "max_stage_torque_residual_norm": max_stage_torque,
        "max_lambda_norm": max_lambda,
        "max_quaternion_unit_error": max_quat_unit_error,
        "total_newton_iterations": total_iters,
    }


def estimate_order(hs: list[float], errors: list[float]) -> float:
    pairs = [(h, e) for h, e in zip(hs, errors) if np.isfinite(e) and e > 1.0e-13]
    if len(pairs) < 2:
        return float("nan")
    x = np.log([p[0] for p in pairs])
    y = np.log([p[1] for p in pairs])
    slope, _ = np.polyfit(x, y, 1)
    return float(slope)
