"""Small SO(3) integrator library for the v005 benchmark.

The implementation is intentionally dependency-light.  It uses row-major NumPy
arrays and right-trivialized angular velocity:

    R_dot = R * hat(omega)

where omega is expressed in the body frame.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, Iterable, List, Tuple

import numpy as np


Array = np.ndarray
OmegaFun = Callable[[float, Array], Array]


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
    A = np.sin(theta) / theta
    B = (1.0 - np.cos(theta)) / (theta * theta)
    return I + A * W + B * (W @ W)


def log_so3(R: Array) -> Array:
    R = np.asarray(R, dtype=float).reshape(3, 3)
    c = 0.5 * (np.trace(R) - 1.0)
    c = float(np.clip(c, -1.0, 1.0))
    theta = float(np.arccos(c))
    if theta < 1.0e-8:
        return vee(0.5 * (R - R.T))
    if np.pi - theta < 1.0e-6:
        # Robust enough for diagnostics; benchmark trajectories avoid this edge.
        A = (R + np.eye(3)) * 0.5
        axis = np.sqrt(np.maximum(np.diag(A), 0.0))
        if np.linalg.norm(axis) < 1.0e-12:
            axis = np.array([1.0, 0.0, 0.0])
        axis = axis / np.linalg.norm(axis)
        return theta * axis
    return theta / (2.0 * np.sin(theta)) * vee(R - R.T)


def right_jacobian_inverse_apply(u: Array, w: Array) -> Array:
    """Apply J_r(u)^{-1} to w.

    This is dexp_{-u}^{-1}(w), the correction needed when
    R(t) = R_n exp(u(t)) and R_dot = R hat(omega).
    """

    u = np.asarray(u, dtype=float).reshape(3)
    w = np.asarray(w, dtype=float).reshape(3)
    theta = float(np.linalg.norm(u))
    U = hat(u)
    if theta < 1.0e-7:
        coeff = 1.0 / 12.0 + theta * theta / 720.0
    else:
        coeff = 1.0 / (theta * theta) - (1.0 + np.cos(theta)) / (
            2.0 * theta * np.sin(theta)
        )
    return (np.eye(3) + 0.5 * U + coeff * (U @ U)) @ w


def compose_right(R: Array, w: Array) -> Array:
    return R @ exp_so3(w)


def orientation_error(R_ref: Array, R: Array) -> float:
    return float(np.linalg.norm(log_so3(R_ref.T @ R)))


def orthogonality_error(R: Array) -> float:
    return float(np.linalg.norm(R.T @ R - np.eye(3), ord="fro"))


def determinant_error(R: Array) -> float:
    return float(abs(np.linalg.det(R) - 1.0))


def project_so3(R: Array) -> Array:
    U, _, Vt = np.linalg.svd(R)
    Q = U @ Vt
    if np.linalg.det(Q) < 0.0:
        U[:, -1] *= -1.0
        Q = U @ Vt
    return Q


def omega_noncommuting(t: float, R: Array | None = None) -> Array:
    del R
    return np.array(
        [
            0.7 + 0.25 * np.cos(1.7 * t),
            0.55 * np.sin(0.9 * t + 0.2) + 0.15 * np.cos(2.3 * t),
            0.35 * np.cos(1.3 * t) + 0.2 * np.sin(2.1 * t + 0.3),
        ],
        dtype=float,
    )


def step_lie_euler(R: Array, t: float, h: float, omega_fun: OmegaFun) -> Array:
    return compose_right(R, h * omega_fun(t, R))


def step_exp_midpoint(R: Array, t: float, h: float, omega_fun: OmegaFun) -> Array:
    return compose_right(R, h * omega_fun(t + 0.5 * h, R))


def step_cf4(R: Array, t: float, h: float, omega_fun: OmegaFun) -> Array:
    """Fourth-order commutator-free two-exponential step for omega(t).

    The familiar left-action formula applies the `a,b` exponential first and
    the `b,a` exponential second.  This benchmark uses right multiplication
    (`R_dot = R hat(omega)`), so the two factors are applied in reverse order.
    """

    root3 = np.sqrt(3.0)
    c1 = 0.5 - root3 / 6.0
    c2 = 0.5 + root3 / 6.0
    w1 = omega_fun(t + c1 * h, R)
    w2 = omega_fun(t + c2 * h, R)
    a = (3.0 - 2.0 * root3) / 12.0
    b = (3.0 + 2.0 * root3) / 12.0
    first_right_factor = h * (b * w1 + a * w2)
    second_right_factor = h * (a * w1 + b * w2)
    return compose_right(compose_right(R, first_right_factor), second_right_factor)


def step_rkmk4(R: Array, t: float, h: float, omega_fun: OmegaFun) -> Array:
    """Classical RK4 lifted by the right-trivialized Munthe-Kaas equation."""

    k1 = h * omega_fun(t, R)
    u2 = 0.5 * k1
    k2 = h * right_jacobian_inverse_apply(
        u2, omega_fun(t + 0.5 * h, compose_right(R, u2))
    )
    u3 = 0.5 * k2
    k3 = h * right_jacobian_inverse_apply(
        u3, omega_fun(t + 0.5 * h, compose_right(R, u3))
    )
    u4 = k3
    k4 = h * right_jacobian_inverse_apply(u4, omega_fun(t + h, compose_right(R, u4)))
    return compose_right(R, (k1 + 2.0 * k2 + 2.0 * k3 + k4) / 6.0)


def step_matrix_rk4(R: Array, t: float, h: float, omega_fun: OmegaFun) -> Array:
    """Non-intrinsic RK4 on the embedded matrix ODE, without projection."""

    def rhs(tt: float, RR: Array) -> Array:
        return RR @ hat(omega_fun(tt, RR))

    k1 = rhs(t, R)
    k2 = rhs(t + 0.5 * h, R + 0.5 * h * k1)
    k3 = rhs(t + 0.5 * h, R + 0.5 * h * k2)
    k4 = rhs(t + h, R + h * k3)
    return R + h * (k1 + 2.0 * k2 + 2.0 * k3 + k4) / 6.0


def integrate_orientation(
    method: str,
    h: float,
    t_final: float,
    omega_fun: OmegaFun = omega_noncommuting,
    R0: Array | None = None,
) -> Array:
    steppers = {
        "lie_euler": step_lie_euler,
        "exp_midpoint": step_exp_midpoint,
        "cf4": step_cf4,
        "rkmk4": step_rkmk4,
        "matrix_rk4": step_matrix_rk4,
    }
    if method not in steppers:
        raise ValueError(f"unknown orientation method: {method}")
    stepper = steppers[method]
    R = np.eye(3) if R0 is None else np.array(R0, dtype=float)
    n_steps = int(round(t_final / h))
    if abs(n_steps * h - t_final) > 1.0e-12:
        raise ValueError("h must divide t_final in this benchmark")
    t = 0.0
    for _ in range(n_steps):
        R = stepper(R, t, h, omega_fun)
        t += h
    return R


def euler_top_rhs(w: Array, inertia: Array) -> Array:
    w = np.asarray(w, dtype=float).reshape(3)
    m = inertia @ w
    return np.linalg.solve(inertia, np.cross(m, w))


def euler_energy(w: Array, inertia: Array) -> float:
    w = np.asarray(w, dtype=float).reshape(3)
    return float(0.5 * w @ inertia @ w)


def angular_momentum_body_norm(w: Array, inertia: Array) -> float:
    return float(np.linalg.norm(inertia @ np.asarray(w, dtype=float).reshape(3)))


def step_euler_top_lie_euler(R: Array, w: Array, h: float, inertia: Array) -> Tuple[Array, Array, int]:
    w_next = w + h * euler_top_rhs(w, inertia)
    return compose_right(R, h * w), w_next, 0


def step_euler_top_rkmk4(R: Array, w: Array, h: float, inertia: Array) -> Tuple[Array, Array, int]:
    def f(ww: Array) -> Array:
        return euler_top_rhs(ww, inertia)

    kw1 = h * f(w)
    kr1 = h * w

    w2 = w + 0.5 * kw1
    u2 = 0.5 * kr1
    kw2 = h * f(w2)
    kr2 = h * right_jacobian_inverse_apply(u2, w2)

    w3 = w + 0.5 * kw2
    u3 = 0.5 * kr2
    kw3 = h * f(w3)
    kr3 = h * right_jacobian_inverse_apply(u3, w3)

    w4 = w + kw3
    u4 = kr3
    kw4 = h * f(w4)
    kr4 = h * right_jacobian_inverse_apply(u4, w4)

    w_next = w + (kw1 + 2.0 * kw2 + 2.0 * kw3 + kw4) / 6.0
    R_next = compose_right(R, (kr1 + 2.0 * kr2 + 2.0 * kr3 + kr4) / 6.0)
    return R_next, w_next, 0


def _finite_difference_jacobian(fun: Callable[[Array], Array], x: Array) -> Array:
    x = np.asarray(x, dtype=float).reshape(3)
    J = np.zeros((3, 3))
    eps = 1.0e-7 * max(1.0, float(np.linalg.norm(x)))
    for i in range(3):
        dx = np.zeros(3)
        dx[i] = eps
        J[:, i] = (fun(x + dx) - fun(x - dx)) / (2.0 * eps)
    return J


def step_euler_top_lie_midpoint(
    R: Array,
    w: Array,
    h: float,
    inertia: Array,
    tol: float = 1.0e-12,
    max_iters: int = 20,
) -> Tuple[Array, Array, int]:
    """Implicit midpoint for Euler equations plus exp(h*w_mid) on SO(3)."""

    w = np.asarray(w, dtype=float).reshape(3)

    def residual(w_mid: Array) -> Array:
        return w_mid - w - 0.5 * h * euler_top_rhs(w_mid, inertia)

    w_mid = w + 0.5 * h * euler_top_rhs(w, inertia)
    for it in range(max_iters):
        res = residual(w_mid)
        if np.linalg.norm(res) < tol:
            break
        J = _finite_difference_jacobian(residual, w_mid)
        delta = np.linalg.solve(J, -res)
        w_mid = w_mid + delta
        if np.linalg.norm(delta) < tol:
            break
    else:
        raise RuntimeError("implicit midpoint did not converge")

    w_next = 2.0 * w_mid - w
    R_next = compose_right(R, h * w_mid)
    return R_next, w_next, it + 1


def step_euler_top_lie_midpoint_yoshida4(
    R: Array,
    w: Array,
    h: float,
    inertia: Array,
) -> Tuple[Array, Array, int]:
    """Fourth-order symmetric composition of the Lie midpoint step.

    The base Lie midpoint step is symmetric and preserves the Euler top's two
    quadratic invariants.  The Yoshida triple jump composes it with coefficients
    c1, c0, c1 to obtain fourth order for smooth reversible dynamics.
    """

    c1 = 1.0 / (2.0 - 2.0 ** (1.0 / 3.0))
    c0 = -(2.0 ** (1.0 / 3.0)) / (2.0 - 2.0 ** (1.0 / 3.0))
    total_iters = 0
    for coeff in (c1, c0, c1):
        R, w, niters = step_euler_top_lie_midpoint(R, w, coeff * h, inertia)
        total_iters += niters
    return R, w, total_iters


def step_euler_top_gauss_lie4(
    R: Array,
    w: Array,
    h: float,
    inertia: Array,
    tol: float = 1.0e-12,
    max_iters: int = 20,
) -> Tuple[Array, Array, int]:
    """Two-stage Gauss collocation for omega plus CF4 reconstruction on SO(3).

    The stage equations are the classical fourth-order Gauss-Legendre RK method
    applied to Euler's body angular-velocity equation.  The final attitude uses
    the right-action two-exponential CF4 formula with the two stage velocities.
    """

    w = np.asarray(w, dtype=float).reshape(3)
    root3 = np.sqrt(3.0)
    a11 = 0.25
    a12 = 0.25 - root3 / 6.0
    a21 = 0.25 + root3 / 6.0
    a22 = 0.25

    def split(x: Array) -> Tuple[Array, Array]:
        return x[:3], x[3:]

    def residual(x: Array) -> Array:
        w1, w2 = split(x)
        f1 = euler_top_rhs(w1, inertia)
        f2 = euler_top_rhs(w2, inertia)
        return np.concatenate(
            (
                w1 - w - h * (a11 * f1 + a12 * f2),
                w2 - w - h * (a21 * f1 + a22 * f2),
            )
        )

    f0 = euler_top_rhs(w, inertia)
    x = np.concatenate((w + (0.5 - root3 / 6.0) * h * f0, w + (0.5 + root3 / 6.0) * h * f0))
    for it in range(max_iters):
        res = residual(x)
        if np.linalg.norm(res) < tol:
            break
        J = np.zeros((6, 6))
        eps_base = 1.0e-7 * max(1.0, float(np.linalg.norm(x)))
        for j in range(6):
            dx = np.zeros(6)
            dx[j] = eps_base
            J[:, j] = (residual(x + dx) - residual(x - dx)) / (2.0 * eps_base)
        delta = np.linalg.solve(J, -res)
        x = x + delta
        if np.linalg.norm(delta) < tol:
            break
    else:
        raise RuntimeError("two-stage Gauss solve did not converge")

    w1, w2 = split(x)
    f1 = euler_top_rhs(w1, inertia)
    f2 = euler_top_rhs(w2, inertia)
    w_next = w + 0.5 * h * (f1 + f2)

    cf_a = (3.0 - 2.0 * root3) / 12.0
    cf_b = (3.0 + 2.0 * root3) / 12.0
    first_right_factor = h * (cf_b * w1 + cf_a * w2)
    second_right_factor = h * (cf_a * w1 + cf_b * w2)
    R_next = compose_right(compose_right(R, first_right_factor), second_right_factor)
    return R_next, w_next, it + 1


def integrate_euler_top(
    method: str,
    h: float,
    t_final: float,
    inertia: Array,
    w0: Array,
    R0: Array | None = None,
) -> Dict[str, Array | float | int]:
    steppers = {
        "lie_euler": step_euler_top_lie_euler,
        "rkmk4": step_euler_top_rkmk4,
        "lie_midpoint": step_euler_top_lie_midpoint,
        "lie_midpoint_yoshida4": step_euler_top_lie_midpoint_yoshida4,
        "gauss_lie4": step_euler_top_gauss_lie4,
    }
    if method not in steppers:
        raise ValueError(f"unknown euler-top method: {method}")

    stepper = steppers[method]
    R = np.eye(3) if R0 is None else np.array(R0, dtype=float)
    w = np.array(w0, dtype=float).reshape(3)
    n_steps = int(round(t_final / h))
    if abs(n_steps * h - t_final) > 1.0e-12:
        raise ValueError("h must divide t_final in this benchmark")

    E0 = euler_energy(w, inertia)
    Lb0 = angular_momentum_body_norm(w, inertia)
    Ls0 = R @ (inertia @ w)
    max_energy_rel = 0.0
    max_body_momentum_rel = 0.0
    max_spatial_momentum_abs = 0.0
    max_ortho = 0.0
    total_newton = 0

    for _ in range(n_steps):
        R, w, niters = stepper(R, w, h, inertia)
        total_newton += niters
        E = euler_energy(w, inertia)
        Lb = angular_momentum_body_norm(w, inertia)
        Ls = R @ (inertia @ w)
        max_energy_rel = max(max_energy_rel, abs(E - E0) / max(abs(E0), 1.0e-30))
        max_body_momentum_rel = max(max_body_momentum_rel, abs(Lb - Lb0) / max(abs(Lb0), 1.0e-30))
        max_spatial_momentum_abs = max(max_spatial_momentum_abs, float(np.linalg.norm(Ls - Ls0)))
        max_ortho = max(max_ortho, orthogonality_error(R))

    return {
        "R": R,
        "w": w,
        "steps": n_steps,
        "max_energy_rel": max_energy_rel,
        "max_body_momentum_rel": max_body_momentum_rel,
        "max_spatial_momentum_abs": max_spatial_momentum_abs,
        "max_orthogonality_error": max_ortho,
        "total_newton_iterations": total_newton,
    }


def estimate_order(hs: Iterable[float], errors: Iterable[float]) -> float:
    pairs = [
        (float(h), float(err))
        for h, err in zip(hs, errors)
        if err > 1.0e-13 and np.isfinite(err)
    ]
    if len(pairs) < 2:
        return float("nan")
    x = np.log([p[0] for p in pairs])
    y = np.log([p[1] for p in pairs])
    slope, _ = np.polyfit(x, y, 1)
    return float(slope)


@dataclass
class MethodResult:
    method: str
    h: float
    error: float
    orthogonality_error: float
    determinant_error: float
    runtime_sec: float
    steps: int
