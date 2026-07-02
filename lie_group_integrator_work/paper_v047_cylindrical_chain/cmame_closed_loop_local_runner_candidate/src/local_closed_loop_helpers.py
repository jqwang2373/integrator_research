"""Local helper functions for the closed-loop runner candidate."""

from __future__ import annotations

import numpy as np


def skew3(vec: np.ndarray) -> np.ndarray:
    x, y, z = np.asarray(vec, dtype=float).reshape(3)
    return np.array([[0.0, -z, y], [z, 0.0, -x], [-y, x, 0.0]], dtype=float)


def exp_so3(rotvec: np.ndarray) -> np.ndarray:
    vec = np.asarray(rotvec, dtype=float).reshape(3)
    angle = float(np.linalg.norm(vec))
    if angle < 1.0e-14:
        return np.eye(3) + skew3(vec)
    axis = vec / angle
    skew = skew3(axis)
    return np.eye(3) + np.sin(angle) * skew + (1.0 - np.cos(angle)) * (skew @ skew)


def project_matrix_to_so3(a_matrix: np.ndarray) -> np.ndarray:
    u, _, vt = np.linalg.svd(a_matrix)
    out = u @ vt
    if np.linalg.det(out) < 0.0:
        u[:, -1] *= -1.0
        out = u @ vt
    return out


def project_v046_system_to_so3(system) -> None:
    for body in system.bodies:
        body.A = project_matrix_to_so3(np.asarray(body.A, dtype=float))


def v046_generalized_velocity(system) -> np.ndarray:
    return np.vstack([*[body.dr for body in system.bodies], *[body.ω for body in system.bodies]])


def v046_generalized_acceleration(system) -> np.ndarray:
    return np.vstack([*[body.ddr for body in system.bodies], *[body.dω for body in system.bodies]])


def v046_constraint_level_residuals(system, t: float) -> tuple[float, float, float]:
    phi = system.g_cons.get_phi(t)
    phi_q = system.g_cons.get_phi_q(t)
    velocity = phi_q @ v046_generalized_velocity(system) - system.g_cons.get_nu(t)
    acceleration = phi_q @ v046_generalized_acceleration(system) - system.g_cons.get_gamma(t)
    return float(np.linalg.norm(phi)), float(np.linalg.norm(velocity)), float(np.linalg.norm(acceleration))


def orthogonality_error(system) -> float:
    out = 0.0
    for body in system.bodies:
        out = max(out, float(np.linalg.norm(body.A.T @ body.A - np.eye(3), ord="fro")))
    return out


def solve_v046_local_kinematic_fullva_time(system, t: float, tol: float, max_iters: int = 30) -> tuple[int, float, float, float]:
    if system.nc != 6 * system.nb:
        raise ValueError(f"local kinematic FullVA solve requires nc=6*nb, got nc={system.nc}, nb={system.nb}")
    system.g_cons.maybe_swap_gcons(t)
    project_v046_system_to_so3(system)
    max_correction = 0.0
    iterations = 0
    for iterations in range(1, max_iters + 1):
        phi_q = np.asarray(system.g_cons.get_phi_q(t), dtype=float).copy()
        phi = np.asarray(system.g_cons.get_phi(t), dtype=float).copy()
        delta = np.linalg.solve(phi_q, -phi).reshape(-1)
        correction = float(np.linalg.norm(delta))
        max_correction = max(max_correction, correction)
        for j, body in enumerate(system.bodies):
            body.r = body.r + delta[3 * j : 3 * (j + 1)].reshape(3, 1)
            dtheta = delta[3 * (system.nb + j) : 3 * (system.nb + j + 1)].reshape(3)
            if np.linalg.norm(dtheta) > 0.0:
                body.A = body.A @ exp_so3(dtheta)
            body.A = project_matrix_to_so3(np.asarray(body.A, dtype=float))
        if correction < tol:
            break
    else:
        raise RuntimeError(f"local kinematic FullVA position Newton failed at t={t:.6g}, correction={max_correction:.3e}")

    phi_q = np.asarray(system.g_cons.get_phi_q(t), dtype=float).copy()
    sigma = np.linalg.svd(phi_q, compute_uv=False)
    min_sigma = float(np.min(sigma))
    max_sigma = float(np.max(sigma))
    cond = max_sigma / min_sigma if min_sigma > 0.0 else float("inf")
    dq = np.linalg.solve(phi_q, np.asarray(system.g_cons.get_nu(t), dtype=float).copy()).reshape(-1)
    for j, body in enumerate(system.bodies):
        body.dr = dq[3 * j : 3 * (j + 1)].reshape(3, 1)
        body.ω = dq[3 * (system.nb + j) : 3 * (system.nb + j + 1)].reshape(3, 1)
    ddq = np.linalg.solve(phi_q, np.asarray(system.g_cons.get_gamma(t), dtype=float).copy()).reshape(-1)
    for j, body in enumerate(system.bodies):
        body.ddr = ddq[3 * j : 3 * (j + 1)].reshape(3, 1)
        body.dω = ddq[3 * (system.nb + j) : 3 * (system.nb + j + 1)].reshape(3, 1)
    return iterations, max_correction, min_sigma, cond


def reconstruct_v046_reaction_dynamics(system, t: float) -> tuple[np.ndarray, float, float, float, float]:
    phi_r = np.asarray(system.g_cons.get_phi_r(t), dtype=float).copy()
    pi = np.asarray(system.g_cons.get_pi(t), dtype=float).copy()
    phi_q = np.concatenate((phi_r, pi), axis=1)
    acc_vec = np.vstack([body.ddr for body in system.bodies])
    alpha_vec = np.vstack([body.dω for body in system.bodies])
    gyro = np.vstack([body.ω_tilde @ body.J @ body.ω for body in system.bodies])
    rhs = np.vstack([system.F_ext - system.M @ acc_vec, -(system.J @ alpha_vec + gyro)])
    lam = np.linalg.solve(phi_q.T, rhs)
    trans = system.M @ acc_vec + phi_r.T @ lam - system.F_ext
    rot = system.J @ alpha_vec + gyro + pi.T @ lam
    trans_norm = float(np.linalg.norm(trans))
    rot_norm = float(np.linalg.norm(rot))
    dyn_norm = float(np.linalg.norm(np.vstack([trans, rot])))
    lam_norm = float(np.linalg.norm(lam))
    return lam, trans_norm, rot_norm, dyn_norm, lam_norm
