from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

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
    I = np.eye(3)
    if theta < 1.0e-8:
        W2 = W @ W
        return I + W + 0.5 * W2 + (W2 @ W) / 6.0
    return I + np.sin(theta) / theta * W + (1.0 - np.cos(theta)) / (theta * theta) * (W @ W)


def log_so3(R: Array) -> Array:
    c = 0.5 * (np.trace(R) - 1.0)
    theta = float(np.arccos(np.clip(c, -1.0, 1.0)))
    if theta < 1.0e-8:
        return vee(0.5 * (R - R.T))
    return theta / (2.0 * np.sin(theta)) * vee(R - R.T)


def compose_right(R: Array, u: Array) -> Array:
    return R @ exp_so3(u)


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


def finite_difference_jacobian(fun: Callable[[Array], Array], x: Array) -> Array:
    y0 = fun(x)
    J = np.zeros((y0.size, x.size))
    eps = 1.0e-7 * max(1.0, float(np.linalg.norm(x)))
    for i in range(x.size):
        dx = np.zeros_like(x)
        dx[i] = eps
        J[:, i] = (fun(x + dx) - fun(x - dx)) / (2.0 * eps)
    return J


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
    R: Array
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


def default_params() -> Params:
    return make_params()


def initial_state(params: Params | None = None) -> State:
    params = default_params() if params is None else params
    R = exp_so3(np.array([0.65, -0.35, 0.25]))
    w = np.array([0.15, -0.2, 0.55])
    s = params.s_com_to_pivot
    r = -R @ s
    v = -R @ np.cross(w, s)
    return State(r=r, R=R, v=v, w=w)


def friction_torque(w: Array, params: Params) -> Array:
    w = np.asarray(w, dtype=float).reshape(3)
    eps = max(float(params.friction_eps), 1.0e-12)
    return -params.viscous_damping * w - params.friction_mu * np.tanh(w / eps)


def friction_power(w: Array, params: Params) -> float:
    return float(friction_torque(w, params) @ np.asarray(w, dtype=float).reshape(3))


def reduced_rhs_w(R: Array, w: Array, params: Params) -> Array:
    Jp = params.J_pivot
    s = params.s_com_to_pivot
    g_body = R.T @ params.gravity
    torque_body = -params.mass * np.cross(s, g_body)
    return np.linalg.solve(Jp, torque_body + friction_torque(w, params) - np.cross(w, Jp @ w))


def energy_state(state: State, params: Params) -> float:
    s = params.s_com_to_pivot
    v_pivot = state.v + state.R @ np.cross(state.w, s)
    kinetic = 0.5 * params.mass * float(state.v @ state.v) + 0.5 * float(state.w @ params.J_com @ state.w)
    potential = -params.mass * float(params.gravity @ state.r)
    # v_pivot should be zero; include no penalty, but keep this line easy to inspect.
    _ = v_pivot
    return kinetic + potential


def orientation_error(R_ref: Array, R: Array) -> float:
    return float(np.linalg.norm(log_so3(R_ref.T @ R)))


def orthogonality_error(R: Array) -> float:
    return float(np.linalg.norm(R.T @ R - np.eye(3), ord="fro"))


def constraint_norms(state: State, params: Params) -> tuple[float, float]:
    s = params.s_com_to_pivot
    pos = state.r + state.R @ s
    vel = state.v + state.R @ np.cross(state.w, s)
    return float(np.linalg.norm(pos)), float(np.linalg.norm(vel))


def dae_residual_norms(state: State, a: Array, alpha: Array, lam: Array, params: Params) -> tuple[float, float]:
    trans = params.mass * a - params.mass * params.gravity - lam
    rot = params.J_com @ alpha + np.cross(state.w, params.J_com @ state.w) - np.cross(
        params.s_com_to_pivot, state.R.T @ lam
    ) - friction_torque(state.w, params)
    return float(np.linalg.norm(trans)), float(np.linalg.norm(rot))


def reduced_step_rkmk4(state: State, h: float, params: Params) -> tuple[State, int]:
    R = state.R
    w = state.w

    l1 = h * reduced_rhs_w(R, w, params)
    k1 = h * w

    u2 = 0.5 * k1
    w2 = w + 0.5 * l1
    R2 = compose_right(R, u2)
    l2 = h * reduced_rhs_w(R2, w2, params)
    k2 = h * right_jacobian_inverse_apply(u2, w2)

    u3 = 0.5 * k2
    w3 = w + 0.5 * l2
    R3 = compose_right(R, u3)
    l3 = h * reduced_rhs_w(R3, w3, params)
    k3 = h * right_jacobian_inverse_apply(u3, w3)

    u4 = k3
    w4 = w + l3
    R4 = compose_right(R, u4)
    l4 = h * reduced_rhs_w(R4, w4, params)
    k4 = h * right_jacobian_inverse_apply(u4, w4)

    R_next = compose_right(R, (k1 + 2.0 * k2 + 2.0 * k3 + k4) / 6.0)
    w_next = w + (l1 + 2.0 * l2 + 2.0 * l3 + l4) / 6.0
    s = params.s_com_to_pivot
    r_next = -R_next @ s
    v_next = -R_next @ np.cross(w_next, s)
    return State(r=r_next, R=R_next, v=v_next, w=w_next), 0


def _stage_guess(state: State, h: float, params: Params) -> Array:
    root3 = np.sqrt(3.0)
    cs = [0.5 - root3 / 6.0, 0.5 + root3 / 6.0]
    alpha0 = reduced_rhs_w(state.R, state.w, params)
    blocks = []
    for c in cs:
        u = c * h * state.w
        R_i = compose_right(state.R, u)
        w_i = state.w + c * h * alpha0
        r_i = -R_i @ params.s_com_to_pivot
        v_i = -R_i @ np.cross(w_i, params.s_com_to_pivot)
        alpha_i = reduced_rhs_w(R_i, w_i, params)
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
        keys = ["u", "r", "v", "w", "a", "alpha", "lambda"]
        stage = {}
        for key in keys:
            stage[key] = x[offset : offset + 3]
            offset += 3
        stages.append(stage)
    return stages


def absolute_gauss_step(
    state: State,
    h: float,
    params: Params,
    tol: float = 1.0e-11,
    max_iters: int = 14,
    stage_velocity_constraints: bool = False,
    stage_acceleration_constraints: bool = False,
) -> tuple[State, int, dict]:
    root3 = np.sqrt(3.0)
    A = np.array(
        [
            [0.25, 0.25 - root3 / 6.0],
            [0.25 + root3 / 6.0, 0.25],
        ]
    )

    def residual(x: Array) -> Array:
        stages = _unpack_stages(x)
        ks = [right_jacobian_inverse_apply(st["u"], st["w"]) for st in stages]
        out = []
        for i, st in enumerate(stages):
            R_i = compose_right(state.R, st["u"])
            u_coll = st["u"] - h * sum(A[i, j] * ks[j] for j in range(2))
            w_coll = st["w"] - state.w - h * sum(A[i, j] * stages[j]["alpha"] for j in range(2))
            trans_dyn = params.mass * st["a"] - params.mass * params.gravity - st["lambda"]
            rot_dyn = (
                params.J_com @ st["alpha"]
                + np.cross(st["w"], params.J_com @ st["w"])
                - np.cross(params.s_com_to_pivot, R_i.T @ st["lambda"])
                - friction_torque(st["w"], params)
            )
            pos_con = st["r"] + R_i @ params.s_com_to_pivot
            vel_con = st["v"] + R_i @ np.cross(st["w"], params.s_com_to_pivot)
            acc_con = st["a"] + R_i @ (
                np.cross(st["alpha"], params.s_com_to_pivot)
                + np.cross(st["w"], np.cross(st["w"], params.s_com_to_pivot))
            )
            if stage_acceleration_constraints:
                out.extend([u_coll, w_coll, trans_dyn, rot_dyn, pos_con, vel_con, acc_con])
            else:
                if stage_velocity_constraints:
                    r_or_v_residual = vel_con
                else:
                    r_or_v_residual = st["r"] - state.r - h * sum(A[i, j] * stages[j]["v"] for j in range(2))
                v_coll = st["v"] - state.v - h * sum(A[i, j] * stages[j]["a"] for j in range(2))
                out.extend([u_coll, r_or_v_residual, v_coll, w_coll, trans_dyn, rot_dyn, pos_con])
        return np.concatenate(out)

    x = _stage_guess(state, h, params)
    last_norm = np.inf
    for it in range(max_iters):
        res = residual(x)
        last_norm = float(np.linalg.norm(res))
        if last_norm < tol:
            break
        J = finite_difference_jacobian(residual, x)
        delta = np.linalg.solve(J, -res)
        x = x + delta
        if np.linalg.norm(delta) < tol:
            break
    else:
        raise RuntimeError(f"absolute Gauss DAE solve did not converge, residual={last_norm:.3e}")

    stages = _unpack_stages(x)
    ks = [right_jacobian_inverse_apply(st["u"], st["w"]) for st in stages]
    u_end = 0.5 * h * (ks[0] + ks[1])
    R_next = compose_right(state.R, u_end)
    r_next = state.r + 0.5 * h * (stages[0]["v"] + stages[1]["v"])
    v_next = state.v + 0.5 * h * (stages[0]["a"] + stages[1]["a"])
    w_next = state.w + 0.5 * h * (stages[0]["alpha"] + stages[1]["alpha"])
    next_state = State(r=r_next, R=R_next, v=v_next, w=w_next)
    max_stage_constraint = max(
        float(np.linalg.norm(st["r"] + compose_right(state.R, st["u"]) @ params.s_com_to_pivot))
        for st in stages
    )
    max_stage_force = 0.0
    max_stage_torque = 0.0
    for st in stages:
        R_i = compose_right(state.R, st["u"])
        st_state = State(r=st["r"], R=R_i, v=st["v"], w=st["w"])
        fr, tr = dae_residual_norms(st_state, st["a"], st["alpha"], st["lambda"], params)
        max_stage_force = max(max_stage_force, fr)
        max_stage_torque = max(max_stage_torque, tr)
    diag = {
        "newton_iterations": it + 1,
        "stage_residual_norm": last_norm,
        "max_stage_constraint_norm": max_stage_constraint,
        "max_stage_force_residual_norm": max_stage_force,
        "max_stage_torque_residual_norm": max_stage_torque,
        "lambda_norm_max": max(float(np.linalg.norm(st["lambda"])) for st in stages),
    }
    return next_state, it + 1, diag


def _endpoint_unpack(x: Array) -> tuple[list[dict[str, Array]], dict[str, Array]]:
    stages = _unpack_stages(x[:42])
    end = {
        "u": x[42:45],
        "r": x[45:48],
        "v": x[48:51],
        "w": x[51:54],
    }
    return stages, end


def absolute_gauss_endpoint_step(
    state: State,
    h: float,
    params: Params,
    tol: float = 1.0e-11,
    max_iters: int = 14,
) -> tuple[State, int, dict]:
    """Two-stage Gauss-Lie DAE step with endpoint algebraic constraints inside Newton."""

    root3 = np.sqrt(3.0)
    A = np.array(
        [
            [0.25, 0.25 - root3 / 6.0],
            [0.25 + root3 / 6.0, 0.25],
        ]
    )

    stage0 = _stage_guess(state, h, params)
    stages0 = _unpack_stages(stage0)
    ks0 = [right_jacobian_inverse_apply(st["u"], st["w"]) for st in stages0]
    u_end0 = 0.5 * h * (ks0[0] + ks0[1])
    R_end0 = compose_right(state.R, u_end0)
    w_end0 = state.w + 0.5 * h * (stages0[0]["alpha"] + stages0[1]["alpha"])
    r_end0 = -R_end0 @ params.s_com_to_pivot
    v_end0 = -R_end0 @ np.cross(w_end0, params.s_com_to_pivot)
    x = np.concatenate((stage0, u_end0, r_end0, v_end0, w_end0))

    def residual(xx: Array) -> Array:
        stages, end = _endpoint_unpack(xx)
        ks = [right_jacobian_inverse_apply(st["u"], st["w"]) for st in stages]
        out = []
        for i, st in enumerate(stages):
            R_i = compose_right(state.R, st["u"])
            u_coll = st["u"] - h * sum(A[i, j] * ks[j] for j in range(2))
            w_coll = st["w"] - state.w - h * sum(A[i, j] * stages[j]["alpha"] for j in range(2))
            trans_dyn = params.mass * st["a"] - params.mass * params.gravity - st["lambda"]
            rot_dyn = (
                params.J_com @ st["alpha"]
                + np.cross(st["w"], params.J_com @ st["w"])
                - np.cross(params.s_com_to_pivot, R_i.T @ st["lambda"])
                - friction_torque(st["w"], params)
            )
            pos_con = st["r"] + R_i @ params.s_com_to_pivot
            vel_con = st["v"] + R_i @ np.cross(st["w"], params.s_com_to_pivot)
            acc_con = st["a"] + R_i @ (
                np.cross(st["alpha"], params.s_com_to_pivot)
                + np.cross(st["w"], np.cross(st["w"], params.s_com_to_pivot))
            )
            out.extend([u_coll, w_coll, trans_dyn, rot_dyn, pos_con, vel_con, acc_con])

        R_end = compose_right(state.R, end["u"])
        out.extend(
            [
                end["u"] - 0.5 * h * (ks[0] + ks[1]),
                end["w"] - state.w - 0.5 * h * (stages[0]["alpha"] + stages[1]["alpha"]),
                end["r"] + R_end @ params.s_com_to_pivot,
                end["v"] + R_end @ np.cross(end["w"], params.s_com_to_pivot),
            ]
        )
        return np.concatenate(out)

    last_norm = np.inf
    for it in range(max_iters):
        res = residual(x)
        last_norm = float(np.linalg.norm(res))
        if last_norm < tol:
            break
        J = finite_difference_jacobian(residual, x)
        delta = np.linalg.solve(J, -res)
        x = x + delta
        if np.linalg.norm(delta) < tol:
            break
    else:
        raise RuntimeError(f"endpoint Gauss DAE solve did not converge, residual={last_norm:.3e}")

    stages, end = _endpoint_unpack(x)
    R_end = compose_right(state.R, end["u"])
    next_state = State(r=end["r"], R=R_end, v=end["v"], w=end["w"])

    max_stage_constraint = max(
        float(np.linalg.norm(st["r"] + compose_right(state.R, st["u"]) @ params.s_com_to_pivot))
        for st in stages
    )
    max_stage_force = 0.0
    max_stage_torque = 0.0
    for st in stages:
        R_i = compose_right(state.R, st["u"])
        st_state = State(r=st["r"], R=R_i, v=st["v"], w=st["w"])
        fr, tr = dae_residual_norms(st_state, st["a"], st["alpha"], st["lambda"], params)
        max_stage_force = max(max_stage_force, fr)
        max_stage_torque = max(max_stage_torque, tr)
    diag = {
        "newton_iterations": it + 1,
        "stage_residual_norm": last_norm,
        "max_stage_constraint_norm": max_stage_constraint,
        "max_stage_force_residual_norm": max_stage_force,
        "max_stage_torque_residual_norm": max_stage_torque,
        "lambda_norm_max": max(float(np.linalg.norm(st["lambda"])) for st in stages),
    }
    return next_state, it + 1, diag


def endpoint_project(state: State, params: Params) -> State:
    s = params.s_com_to_pivot
    r = -state.R @ s
    v = -state.R @ np.cross(state.w, s)
    return State(r=r, R=state.R, v=v, w=state.w)


def integrate(
    method: str,
    h: float,
    t_final: float,
    params: Params | None = None,
    project_endpoint: bool = False,
) -> dict:
    params = default_params() if params is None else params
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
    max_ortho = 0.0
    max_lambda = 0.0
    max_friction_power = friction_power(state.w, params)
    min_friction_power = max_friction_power
    total_iters = 0
    for _ in range(n_steps):
        if method == "absolute_gauss_lie4":
            state, niters, diag = absolute_gauss_step(state, h, params)
            if project_endpoint:
                state = endpoint_project(state, params)
            total_iters += niters
            max_stage_constraint = max(max_stage_constraint, diag["max_stage_constraint_norm"])
            max_stage_force = max(max_stage_force, diag["max_stage_force_residual_norm"])
            max_stage_torque = max(max_stage_torque, diag["max_stage_torque_residual_norm"])
            max_lambda = max(max_lambda, diag["lambda_norm_max"])
        elif method == "absolute_gauss_lie4_vc":
            state, niters, diag = absolute_gauss_step(state, h, params, stage_velocity_constraints=True)
            if project_endpoint:
                state = endpoint_project(state, params)
            total_iters += niters
            max_stage_constraint = max(max_stage_constraint, diag["max_stage_constraint_norm"])
            max_stage_force = max(max_stage_force, diag["max_stage_force_residual_norm"])
            max_stage_torque = max(max_stage_torque, diag["max_stage_torque_residual_norm"])
            max_lambda = max(max_lambda, diag["lambda_norm_max"])
        elif method == "absolute_gauss_lie4_acc":
            state, niters, diag = absolute_gauss_step(
                state, h, params, stage_velocity_constraints=True, stage_acceleration_constraints=True
            )
            if project_endpoint:
                state = endpoint_project(state, params)
            total_iters += niters
            max_stage_constraint = max(max_stage_constraint, diag["max_stage_constraint_norm"])
            max_stage_force = max(max_stage_force, diag["max_stage_force_residual_norm"])
            max_stage_torque = max(max_stage_torque, diag["max_stage_torque_residual_norm"])
            max_lambda = max(max_lambda, diag["lambda_norm_max"])
        elif method == "absolute_gauss_lie4_endpoint":
            state, niters, diag = absolute_gauss_endpoint_step(state, h, params)
            total_iters += niters
            max_stage_constraint = max(max_stage_constraint, diag["max_stage_constraint_norm"])
            max_stage_force = max(max_stage_force, diag["max_stage_force_residual_norm"])
            max_stage_torque = max(max_stage_torque, diag["max_stage_torque_residual_norm"])
            max_lambda = max(max_lambda, diag["lambda_norm_max"])
        elif method == "reduced_rkmk4":
            state, niters = reduced_step_rkmk4(state, h, params)
            total_iters += niters
        else:
            raise ValueError(f"unknown method: {method}")
        cn, cv = constraint_norms(state, params)
        energy = energy_state(state, params)
        step_delta_energy = energy - prev_energy
        max_step_energy_increase = max(max_step_energy_increase, step_delta_energy)
        prev_energy = energy
        power = friction_power(state.w, params)
        max_friction_power = max(max_friction_power, power)
        min_friction_power = min(min_friction_power, power)
        max_constraint = max(max_constraint, cn)
        max_velocity_constraint = max(max_velocity_constraint, cv)
        max_energy = max(max_energy, abs(energy - E0) / max(abs(E0), 1.0e-30))
        max_ortho = max(max_ortho, orthogonality_error(state.R))

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
        "max_orthogonality_fro": max_ortho,
        "max_lambda_norm": max_lambda,
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
