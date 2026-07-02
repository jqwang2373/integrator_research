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
    x = np.asarray(x, dtype=float)
    y0 = fun(x)
    J = np.zeros((y0.size, x.size))
    eps = 1.0e-7 * max(1.0, float(np.linalg.norm(x)))
    for i in range(x.size):
        dx = np.zeros_like(x)
        dx[i] = eps
        J[:, i] = (fun(x + dx) - fun(x - dx)) / (2.0 * eps)
    return J


@dataclass(frozen=True)
class PendulumParams:
    mass: float
    J_com: Array
    s_com_to_pivot: Array
    gravity: Array

    @property
    def J_pivot(self) -> Array:
        s = self.s_com_to_pivot.reshape(3)
        return self.J_com + self.mass * ((s @ s) * np.eye(3) - np.outer(s, s))


def default_params() -> PendulumParams:
    mass = 4.0
    J_com = np.diag([0.18, 0.32, 0.41])
    s = np.array([0.0, 0.0, 0.75])
    gravity = np.array([0.0, 0.0, -9.81])
    return PendulumParams(mass=mass, J_com=J_com, s_com_to_pivot=s, gravity=gravity)


def initial_state() -> tuple[Array, Array]:
    R0 = exp_so3(np.array([0.65, -0.35, 0.25]))
    w0 = np.array([0.15, -0.2, 0.55])
    return R0, w0


def rhs_w(R: Array, w: Array, params: PendulumParams) -> Array:
    Jp = params.J_pivot
    s = params.s_com_to_pivot.reshape(3)
    g_body = R.T @ params.gravity.reshape(3)
    torque_body = -params.mass * np.cross(s, g_body)
    return np.linalg.solve(Jp, torque_body - np.cross(w, Jp @ w))


def energy(R: Array, w: Array, params: PendulumParams) -> float:
    kinetic = 0.5 * float(w @ params.J_pivot @ w)
    r = -R @ params.s_com_to_pivot.reshape(3)
    potential = -params.mass * float(params.gravity.reshape(3) @ r)
    return kinetic + potential


def reconstruct_dae(R: Array, w: Array, params: PendulumParams) -> dict:
    s = params.s_com_to_pivot.reshape(3)
    wdot = rhs_w(R, w, params)
    r = -R @ s
    rdot = -R @ (np.cross(w, s))
    rddot = -R @ (np.cross(wdot, s) + np.cross(w, np.cross(w, s)))
    reaction = params.mass * (rddot - params.gravity.reshape(3))
    trans_res = params.mass * rddot - params.mass * params.gravity.reshape(3) - reaction
    rot_res = params.J_com @ wdot + np.cross(w, params.J_com @ w) - np.cross(s, R.T @ reaction)
    constraint = r + R @ s
    velocity_constraint = rdot + R @ np.cross(w, s)
    return {
        "r": r,
        "rdot": rdot,
        "rddot": rddot,
        "wdot": wdot,
        "reaction": reaction,
        "constraint_norm": float(np.linalg.norm(constraint)),
        "velocity_constraint_norm": float(np.linalg.norm(velocity_constraint)),
        "dae_force_residual_norm": float(np.linalg.norm(trans_res)),
        "dae_torque_residual_norm": float(np.linalg.norm(rot_res)),
    }


def orientation_error(R_ref: Array, R: Array) -> float:
    return float(np.linalg.norm(log_so3(R_ref.T @ R)))


def orthogonality_error(R: Array) -> float:
    return float(np.linalg.norm(R.T @ R - np.eye(3), ord="fro"))


def step_lie_euler(R: Array, w: Array, h: float, params: PendulumParams) -> tuple[Array, Array, int]:
    w_next = w + h * rhs_w(R, w, params)
    return compose_right(R, h * w_next), w_next, 0


def step_rkmk4(R: Array, w: Array, h: float, params: PendulumParams) -> tuple[Array, Array, int]:
    l1 = h * rhs_w(R, w, params)
    k1 = h * w

    u2 = 0.5 * k1
    w2 = w + 0.5 * l1
    R2 = compose_right(R, u2)
    l2 = h * rhs_w(R2, w2, params)
    k2 = h * right_jacobian_inverse_apply(u2, w2)

    u3 = 0.5 * k2
    w3 = w + 0.5 * l2
    R3 = compose_right(R, u3)
    l3 = h * rhs_w(R3, w3, params)
    k3 = h * right_jacobian_inverse_apply(u3, w3)

    u4 = k3
    w4 = w + l3
    R4 = compose_right(R, u4)
    l4 = h * rhs_w(R4, w4, params)
    k4 = h * right_jacobian_inverse_apply(u4, w4)

    w_next = w + (l1 + 2.0 * l2 + 2.0 * l3 + l4) / 6.0
    R_next = compose_right(R, (k1 + 2.0 * k2 + 2.0 * k3 + k4) / 6.0)
    return R_next, w_next, 0


def step_gauss_lie4(
    R: Array,
    w: Array,
    h: float,
    params: PendulumParams,
    tol: float = 1.0e-12,
    max_iters: int = 20,
) -> tuple[Array, Array, int]:
    root3 = np.sqrt(3.0)
    a11 = 0.25
    a12 = 0.25 - root3 / 6.0
    a21 = 0.25 + root3 / 6.0
    a22 = 0.25

    def split(x: Array) -> tuple[Array, Array, Array, Array]:
        return x[0:3], x[3:6], x[6:9], x[9:12]

    f0 = rhs_w(R, w, params)
    c1 = 0.5 - root3 / 6.0
    c2 = 0.5 + root3 / 6.0
    guess = np.concatenate((c1 * h * w, c2 * h * w, w + c1 * h * f0, w + c2 * h * f0))

    def residual(x: Array) -> Array:
        u1, u2, w1, w2 = split(x)
        R1 = compose_right(R, u1)
        R2 = compose_right(R, u2)
        k1 = right_jacobian_inverse_apply(u1, w1)
        k2 = right_jacobian_inverse_apply(u2, w2)
        l1 = rhs_w(R1, w1, params)
        l2 = rhs_w(R2, w2, params)
        return np.concatenate(
            (
                u1 - h * (a11 * k1 + a12 * k2),
                u2 - h * (a21 * k1 + a22 * k2),
                w1 - w - h * (a11 * l1 + a12 * l2),
                w2 - w - h * (a21 * l1 + a22 * l2),
            )
        )

    x = guess
    for it in range(max_iters):
        res = residual(x)
        if np.linalg.norm(res) < tol:
            break
        J = finite_difference_jacobian(residual, x)
        delta = np.linalg.solve(J, -res)
        x = x + delta
        if np.linalg.norm(delta) < tol:
            break
    else:
        raise RuntimeError("gauss_lie4 fixed-pivot solve did not converge")

    u1, u2, w1, w2 = split(x)
    R1 = compose_right(R, u1)
    R2 = compose_right(R, u2)
    k1 = right_jacobian_inverse_apply(u1, w1)
    k2 = right_jacobian_inverse_apply(u2, w2)
    l1 = rhs_w(R1, w1, params)
    l2 = rhs_w(R2, w2, params)
    R_next = compose_right(R, 0.5 * h * (k1 + k2))
    w_next = w + 0.5 * h * (l1 + l2)
    return R_next, w_next, it + 1


def integrate(method: str, h: float, t_final: float, params: PendulumParams | None = None) -> dict:
    params = default_params() if params is None else params
    steppers = {
        "lie_euler": step_lie_euler,
        "rkmk4": step_rkmk4,
        "gauss_lie4": step_gauss_lie4,
    }
    if method not in steppers:
        raise ValueError(f"unknown method: {method}")
    R, w = initial_state()
    stepper = steppers[method]
    n_steps = int(round(t_final / h))
    if abs(n_steps * h - t_final) > 1.0e-12:
        raise ValueError("h must divide t_final")
    E0 = energy(R, w, params)
    max_energy = 0.0
    max_constraint = 0.0
    max_velocity_constraint = 0.0
    max_force_residual = 0.0
    max_torque_residual = 0.0
    max_ortho = 0.0
    total_iters = 0
    for _ in range(n_steps):
        R, w, niters = stepper(R, w, h, params)
        total_iters += niters
        dae = reconstruct_dae(R, w, params)
        max_energy = max(max_energy, abs(energy(R, w, params) - E0) / max(abs(E0), 1.0e-30))
        max_constraint = max(max_constraint, dae["constraint_norm"])
        max_velocity_constraint = max(max_velocity_constraint, dae["velocity_constraint_norm"])
        max_force_residual = max(max_force_residual, dae["dae_force_residual_norm"])
        max_torque_residual = max(max_torque_residual, dae["dae_torque_residual_norm"])
        max_ortho = max(max_ortho, orthogonality_error(R))
    dae = reconstruct_dae(R, w, params)
    return {
        "R": R,
        "w": w,
        "r": dae["r"],
        "reaction": dae["reaction"],
        "steps": n_steps,
        "max_energy_relative_error": max_energy,
        "max_constraint_norm": max_constraint,
        "max_velocity_constraint_norm": max_velocity_constraint,
        "max_dae_force_residual_norm": max_force_residual,
        "max_dae_torque_residual_norm": max_torque_residual,
        "max_orthogonality_fro": max_ortho,
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
