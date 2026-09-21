from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import jax

jax.config.update("jax_enable_x64", True)
import jax.numpy as jnp
import numpy as np


Array = np.ndarray


def hat_np(w: Array) -> Array:
    w = np.asarray(w, dtype=float).reshape(3)
    return np.array(
        [
            [0.0, -w[2], w[1]],
            [w[2], 0.0, -w[0]],
            [-w[1], w[0], 0.0],
        ]
    )


def quat_normalize_np(q: Array) -> Array:
    q = np.asarray(q, dtype=float).reshape(4)
    return q / np.linalg.norm(q)


def quat_mul_np(q: Array, p: Array) -> Array:
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


def quat_exp_np(theta: Array) -> Array:
    theta = np.asarray(theta, dtype=float).reshape(3)
    angle = float(np.linalg.norm(theta))
    if angle < 1.0e-8:
        angle2 = angle * angle
        scalar = 1.0 - angle2 / 8.0 + angle2 * angle2 / 384.0
        b = 0.5 - angle2 / 48.0 + angle2 * angle2 / 3840.0
        return np.concatenate((np.array([scalar]), b * theta))
    return np.concatenate((np.array([np.cos(0.5 * angle)]), np.sin(0.5 * angle) / angle * theta))


def left_quat_update_np(theta: Array, p0: Array) -> Array:
    return quat_normalize_np(quat_mul_np(quat_exp_np(theta), p0))


def exp_quat_derivative_np(theta: Array) -> Array:
    """Return d exp(theta/2) / d theta as a 4x3 matrix."""

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


def left_update_wrt_delta_quat_matrix_np(p0: Array) -> Array:
    """Matrix B(p0) such that d(q_delta * p0) = B(p0) dq_delta."""

    p0 = quat_normalize_np(p0)
    ps, pv = p0[0], p0[1:4]
    out = np.zeros((4, 4))
    out[0, 0] = ps
    out[0, 1:4] = -pv
    out[1:4, 0] = pv
    out[1:4, 1:4] = ps * np.eye(3) - hat_np(pv)
    return out


def transport_matrix_np(theta: Array, p0: Array) -> Array:
    """Transportation matrix T_exp = d(exp(theta/2) * p0) / d theta."""

    return left_update_wrt_delta_quat_matrix_np(p0) @ exp_quat_derivative_np(theta)


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


def left_quat_update_jax(theta, p0):
    p = quat_mul_jax(quat_exp_jax(theta), p0)
    return p / jnp.linalg.norm(p)


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


@dataclass(frozen=True)
class LoadInputs:
    r: Array
    p0: Array
    theta: Array
    v: Array
    omega: Array
    lam: Array
    mu: float
    eps: float
    viscous: float


def default_inputs(mu: float = 0.08, eps: float = 0.5, scale: float = 1.0) -> LoadInputs:
    return LoadInputs(
        r=np.array([0.15, -0.35, 0.72]) * scale,
        p0=quat_normalize_np(np.array([0.91, 0.22, -0.28, 0.19])),
        theta=np.array([0.18, -0.11, 0.27]) * scale,
        v=np.array([0.45, -0.21, 0.34]) * scale,
        omega=np.array([0.31, -0.48, 0.24]) * scale,
        lam=np.array([4.2, -1.3, 2.8]) * scale,
        mu=mu,
        eps=eps,
        viscous=0.04,
    )


def friction_like_load_jax(r, p, theta, v, omega, lam, mu, eps, viscous):
    R = quat_to_rot_jax(p)
    s = jnp.array([0.19, -0.31, 0.73], dtype=r.dtype)
    axis = R @ jnp.array([0.35, -0.20, 0.91], dtype=r.dtype)
    contact_arm = R @ s
    slip = v + jnp.cross(omega, contact_arm) + 0.07 * r + 0.04 * axis
    normal_raw = lam @ axis + 0.25 * jnp.linalg.norm(lam) + 0.8
    normal = jnp.logaddexp(normal_raw, 0.0) + 0.05
    eps_safe = jnp.maximum(jnp.asarray(eps, dtype=r.dtype), 1.0e-12)
    force = -mu * normal * jnp.tanh(slip / eps_safe) - viscous * slip
    force = force + 0.03 * jnp.sin(theta + p[1:4]) + 0.02 * jnp.array(
        [p[0] * p[2], p[1] * p[3], p[0] * p[1]], dtype=r.dtype
    )
    torque = jnp.cross(contact_arm, force) - 0.05 * jnp.tanh(omega + theta) + 0.01 * normal * p[1:4]
    return jnp.concatenate((force, torque))


def finite_difference_jacobian(fun: Callable[[Array], Array], x: Array, eps: float = 1.0e-6) -> Array:
    x = np.asarray(x, dtype=float)
    y0 = np.asarray(fun(x), dtype=float)
    J = np.zeros((y0.size, x.size))
    step_base = eps * max(1.0, float(np.linalg.norm(x)))
    for i in range(x.size):
        dx = np.zeros_like(x)
        dx[i] = step_base
        J[:, i] = (np.asarray(fun(x + dx)) - np.asarray(fun(x - dx))) / (2.0 * step_base)
    return J


def pi_operator(load_inputs: LoadInputs) -> dict:
    r = jnp.asarray(load_inputs.r, dtype=jnp.float64)
    p0 = jnp.asarray(load_inputs.p0, dtype=jnp.float64)
    theta = jnp.asarray(load_inputs.theta, dtype=jnp.float64)
    v = jnp.asarray(load_inputs.v, dtype=jnp.float64)
    omega = jnp.asarray(load_inputs.omega, dtype=jnp.float64)
    lam = jnp.asarray(load_inputs.lam, dtype=jnp.float64)
    p = left_quat_update_jax(theta, p0)
    args = (v, omega, lam, load_inputs.mu, load_inputs.eps, load_inputs.viscous)

    g_p = np.asarray(jax.jacfwd(lambda pp: friction_like_load_jax(r, pp, theta, *args))(p))
    g_theta = np.asarray(jax.jacfwd(lambda th: friction_like_load_jax(r, p, th, *args))(theta))
    g_r = np.asarray(jax.jacfwd(lambda rr: friction_like_load_jax(rr, p, theta, *args))(r))
    t_exp = transport_matrix_np(np.asarray(theta), np.asarray(p0))
    pi = g_p @ t_exp + g_theta
    theta_op = np.concatenate((g_r, pi), axis=1)

    direct_pi = np.asarray(
        jax.jacfwd(
            lambda th: friction_like_load_jax(r, left_quat_update_jax(th, p0), th, *args)
        )(theta)
    )
    direct_theta = np.asarray(
        jax.jacfwd(
            lambda u: friction_like_load_jax(
                u[:3],
                left_quat_update_jax(u[3:6], p0),
                u[3:6],
                *args,
            )
        )(jnp.concatenate((r, theta)))
    )

    fd_pi = finite_difference_jacobian(
        lambda th_np: np.asarray(
            friction_like_load_jax(
                r,
                left_quat_update_jax(jnp.asarray(th_np, dtype=jnp.float64), p0),
                jnp.asarray(th_np, dtype=jnp.float64),
                *args,
            )
        ),
        np.asarray(theta),
    )
    return {
        "p": np.asarray(p),
        "g_p": g_p,
        "g_theta": g_theta,
        "g_r": g_r,
        "t_exp": t_exp,
        "pi": pi,
        "theta_op": theta_op,
        "direct_pi": direct_pi,
        "direct_theta": direct_theta,
        "fd_pi": fd_pi,
    }
