#!/usr/bin/env python3
"""Closed-loop FullVA dynamic stage residual utilities.

This module implements the local stage residual evaluator needed before a
closed-loop Gauss6 trajectory stepper can be accepted. The one-step routines in
this module are smoke paths, not accepted order runners.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


GAUSS6_C = np.array(
    [
        0.5 - np.sqrt(15.0) / 10.0,
        0.5,
        0.5 + np.sqrt(15.0) / 10.0,
    ],
    dtype=float,
)
GAUSS6_B = np.array([5.0 / 18.0, 4.0 / 9.0, 5.0 / 18.0], dtype=float)


@dataclass(frozen=True)
class ClosedLoopStageContext:
    nb: int
    nc: int
    base_orientations: tuple[np.ndarray, ...]


def exp_so3(rotvec: np.ndarray) -> np.ndarray:
    vec = np.asarray(rotvec, dtype=float).reshape(3)
    angle = float(np.linalg.norm(vec))
    if angle < 1.0e-14:
        skew = skew3(vec)
        return np.eye(3) + skew
    axis = vec / angle
    skew = skew3(axis)
    return np.eye(3) + np.sin(angle) * skew + (1.0 - np.cos(angle)) * (skew @ skew)


def log_so3(rotmat: np.ndarray) -> np.ndarray:
    matrix = np.asarray(rotmat, dtype=float).reshape(3, 3)
    cos_angle = float(np.clip((np.trace(matrix) - 1.0) * 0.5, -1.0, 1.0))
    angle = float(np.arccos(cos_angle))
    if angle < 1.0e-14:
        return np.array(
            [
                0.5 * (matrix[2, 1] - matrix[1, 2]),
                0.5 * (matrix[0, 2] - matrix[2, 0]),
                0.5 * (matrix[1, 0] - matrix[0, 1]),
            ],
            dtype=float,
        )
    if np.pi - angle < 1.0e-7:
        eigvals, eigvecs = np.linalg.eig(matrix)
        axis = np.real(eigvecs[:, int(np.argmin(np.abs(eigvals - 1.0)))])
        axis = axis / np.linalg.norm(axis)
        return angle * axis
    scale = angle / (2.0 * np.sin(angle))
    return scale * np.array(
        [
            matrix[2, 1] - matrix[1, 2],
            matrix[0, 2] - matrix[2, 0],
            matrix[1, 0] - matrix[0, 1],
        ],
        dtype=float,
    )


def right_jacobian_inverse_so3(rotvec: np.ndarray) -> np.ndarray:
    vec = np.asarray(rotvec, dtype=float).reshape(3)
    angle = float(np.linalg.norm(vec))
    skew = skew3(vec)
    if angle < 1.0e-10:
        return np.eye(3) + 0.5 * skew + (skew @ skew) / 12.0
    coeff = (1.0 / (angle * angle)) - ((1.0 + np.cos(angle)) / (2.0 * angle * np.sin(angle)))
    return np.eye(3) + 0.5 * skew + coeff * (skew @ skew)


def skew3(vec: np.ndarray) -> np.ndarray:
    x, y, z = np.asarray(vec, dtype=float).reshape(3)
    return np.array(
        [
            [0.0, -z, y],
            [z, 0.0, -x],
            [-y, x, 0.0],
        ],
        dtype=float,
    )


def capture_stage_context(system) -> ClosedLoopStageContext:
    return ClosedLoopStageContext(
        nb=int(system.nb),
        nc=int(system.nc),
        base_orientations=tuple(np.asarray(body.A, dtype=float).copy() for body in system.bodies),
    )


def _snapshot_system_state(system) -> list[dict[str, np.ndarray]]:
    snapshot = []
    for body in system.bodies:
        snapshot.append(
            {
                "r": np.asarray(body.r, dtype=float).copy(),
                "dr": np.asarray(body.dr, dtype=float).copy(),
                "ddr": np.asarray(body.ddr, dtype=float).copy(),
                "A": np.asarray(body.A, dtype=float).copy(),
                "omega": np.asarray(body.ω, dtype=float).copy(),
                "domega": np.asarray(body.dω, dtype=float).copy(),
            }
        )
    return snapshot


def _restore_system_state(system, snapshot: list[dict[str, np.ndarray]]) -> None:
    for body, state in zip(system.bodies, snapshot, strict=True):
        body.r = state["r"].copy()
        body.dr = state["dr"].copy()
        body.ddr = state["ddr"].copy()
        body.A = state["A"].copy()
        body.ω = state["omega"].copy()
        body.dω = state["domega"].copy()


def generalized_qva_from_system(
    system,
    context: ClosedLoopStageContext | None = None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    q_r = np.vstack([np.asarray(body.r, dtype=float).reshape(3, 1) for body in system.bodies]).reshape(-1)
    if context is None:
        q_theta = np.zeros(3 * int(system.nb), dtype=float)
    else:
        q_theta = np.concatenate(
            [
                log_so3(context.base_orientations[j].T @ np.asarray(body.A, dtype=float))
                for j, body in enumerate(system.bodies)
            ]
        )
    v_r = np.vstack([np.asarray(body.dr, dtype=float).reshape(3, 1) for body in system.bodies]).reshape(-1)
    v_omega = np.vstack([np.asarray(body.ω, dtype=float).reshape(3, 1) for body in system.bodies]).reshape(-1)
    a_r = np.vstack([np.asarray(body.ddr, dtype=float).reshape(3, 1) for body in system.bodies]).reshape(-1)
    a_omega = np.vstack([np.asarray(body.dω, dtype=float).reshape(3, 1) for body in system.bodies]).reshape(-1)
    return (
        np.concatenate([q_r, q_theta]),
        np.concatenate([v_r, v_omega]),
        np.concatenate([a_r, a_omega]),
    )


def pack_closed_loop_fullva_stage_vector(
    q: np.ndarray,
    v: np.ndarray,
    a: np.ndarray,
    lam: np.ndarray,
) -> np.ndarray:
    qv = np.asarray(q, dtype=float).reshape(-1)
    vv = np.asarray(v, dtype=float).reshape(-1)
    av = np.asarray(a, dtype=float).reshape(-1)
    lv = np.asarray(lam, dtype=float).reshape(-1)
    if not (qv.shape == vv.shape == av.shape):
        raise ValueError(f"q/v/a dimensions differ: {qv.shape}, {vv.shape}, {av.shape}")
    return np.concatenate([qv, vv, av, lv])


def unpack_closed_loop_fullva_stage_vector(
    stage_vector: np.ndarray,
    nb: int,
    nc: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    generalized_dim = 6 * int(nb)
    lambda_dim = int(nc)
    expected = 3 * generalized_dim + lambda_dim
    vec = np.asarray(stage_vector, dtype=float).reshape(-1)
    if vec.size != expected:
        raise ValueError(f"stage vector has {vec.size} entries; expected {expected}")
    q = vec[:generalized_dim]
    v = vec[generalized_dim : 2 * generalized_dim]
    a = vec[2 * generalized_dim : 3 * generalized_dim]
    lam = vec[3 * generalized_dim :]
    return q, v, a, lam


def set_system_stage_state(
    system,
    q: np.ndarray,
    v: np.ndarray,
    a: np.ndarray,
    context: ClosedLoopStageContext,
) -> None:
    nb = context.nb
    qv = np.asarray(q, dtype=float).reshape(-1)
    vv = np.asarray(v, dtype=float).reshape(-1)
    av = np.asarray(a, dtype=float).reshape(-1)
    expected = 6 * nb
    if qv.size != expected or vv.size != expected or av.size != expected:
        raise ValueError("q/v/a dimensions do not match 6*nb")
    for j, body in enumerate(system.bodies):
        body.r = qv[3 * j : 3 * (j + 1)].reshape(3, 1)
        theta = qv[3 * (nb + j) : 3 * (nb + j + 1)]
        body.A = context.base_orientations[j] @ exp_so3(theta)
        body.dr = vv[3 * j : 3 * (j + 1)].reshape(3, 1)
        body.ω = vv[3 * (nb + j) : 3 * (nb + j + 1)].reshape(3, 1)
        body.ddr = av[3 * j : 3 * (j + 1)].reshape(3, 1)
        body.dω = av[3 * (nb + j) : 3 * (nb + j + 1)].reshape(3, 1)


def closed_loop_fullva_stage_residual_blocks(
    system,
    t: float,
    stage_vector: np.ndarray,
    context: ClosedLoopStageContext | None = None,
    *,
    restore: bool = True,
) -> dict[str, np.ndarray]:
    if context is None:
        context = capture_stage_context(system)
    q, v, a, lam = unpack_closed_loop_fullva_stage_vector(stage_vector, context.nb, context.nc)
    snapshot = _snapshot_system_state(system) if restore else []
    try:
        system.g_cons.maybe_swap_gcons(float(t))
        set_system_stage_state(system, q, v, a, context)
        phi = np.asarray(system.g_cons.get_phi(float(t)), dtype=float).reshape(-1)
        phi_q = np.asarray(system.g_cons.get_phi_q(float(t)), dtype=float)
        nu = np.asarray(system.g_cons.get_nu(float(t)), dtype=float).reshape(-1)
        gamma = np.asarray(system.g_cons.get_gamma(float(t)), dtype=float).reshape(-1)
        phi_r = np.asarray(system.g_cons.get_phi_r(float(t)), dtype=float)
        pi = np.asarray(system.g_cons.get_pi(float(t)), dtype=float)
        lam_col = np.asarray(lam, dtype=float).reshape(context.nc, 1)
        acc_vec = np.vstack([np.asarray(body.ddr, dtype=float).reshape(3, 1) for body in system.bodies])
        alpha_vec = np.vstack([np.asarray(body.dω, dtype=float).reshape(3, 1) for body in system.bodies])
        gyro = np.vstack(
            [
                np.asarray(body.ω_tilde, dtype=float) @ np.asarray(body.J, dtype=float) @ np.asarray(body.ω, dtype=float)
                for body in system.bodies
            ]
        )
        trans = np.asarray(system.M, dtype=float) @ acc_vec + phi_r.T @ lam_col - np.asarray(system.F_ext, dtype=float)
        rot = np.asarray(system.J, dtype=float) @ alpha_vec + gyro + pi.T @ lam_col
        return {
            "position_constraints_phi": phi,
            "velocity_constraints_phiq_v_minus_nu": phi_q @ v.reshape(-1) - nu,
            "acceleration_constraints_phiq_a_minus_gamma": phi_q @ a.reshape(-1) - gamma,
            "newton_euler_balance": np.vstack([trans, rot]).reshape(-1),
        }
    finally:
        if restore:
            _restore_system_state(system, snapshot)


def closed_loop_fullva_stage_residual(
    system,
    t: float,
    stage_vector: np.ndarray,
    context: ClosedLoopStageContext | None = None,
) -> np.ndarray:
    blocks = closed_loop_fullva_stage_residual_blocks(system, t, stage_vector, context)
    return np.concatenate(
        [
            blocks["position_constraints_phi"],
            blocks["velocity_constraints_phiq_v_minus_nu"],
            blocks["acceleration_constraints_phiq_a_minus_gamma"],
            blocks["newton_euler_balance"],
        ]
    )


def _body_vectors(system, attr: str) -> np.ndarray:
    return np.vstack([np.asarray(getattr(body, attr), dtype=float).reshape(3, 1) for body in system.bodies]).reshape(-1)


def _set_body_vectors(system, attr: str, values: np.ndarray) -> None:
    flat = np.asarray(values, dtype=float).reshape(-1)
    for j, body in enumerate(system.bodies):
        setattr(body, attr, flat[3 * j : 3 * (j + 1)].reshape(3, 1))


def endpoint_state_from_system(system) -> dict[str, np.ndarray]:
    return {
        "r": _body_vectors(system, "r"),
        "dr": _body_vectors(system, "dr"),
        "ddr": _body_vectors(system, "ddr"),
        "omega": _body_vectors(system, "ω"),
        "domega": _body_vectors(system, "dω"),
        "A": np.stack([np.asarray(body.A, dtype=float).copy() for body in system.bodies], axis=0),
    }


def endpoint_state_error_inf(candidate: dict[str, np.ndarray], reference: dict[str, np.ndarray]) -> dict[str, float]:
    orientation_error = 0.0
    for cand_a, ref_a in zip(candidate["A"], reference["A"], strict=True):
        orientation_error = max(orientation_error, float(np.linalg.norm(cand_a - ref_a, ord=np.inf)))
    return {
        "pos": float(np.linalg.norm(candidate["r"] - reference["r"], ord=np.inf)),
        "vel": float(np.linalg.norm(candidate["dr"] - reference["dr"], ord=np.inf)),
        "acc": float(np.linalg.norm(candidate["ddr"] - reference["ddr"], ord=np.inf)),
        "omega": float(np.linalg.norm(candidate["omega"] - reference["omega"], ord=np.inf)),
        "alpha": float(np.linalg.norm(candidate["domega"] - reference["domega"], ord=np.inf)),
        "orientation": orientation_error,
    }


def solve_closed_loop_fullva_stage(
    system,
    t: float,
    context: ClosedLoopStageContext,
    initial_stage_vector: np.ndarray,
    *,
    tol: float = 1.0e-11,
) -> dict[str, object]:
    residual = closed_loop_fullva_stage_residual(system, t, initial_stage_vector, context)
    residual_norm = float(np.linalg.norm(residual, ord=np.inf))
    if residual_norm > tol:
        raise RuntimeError(
            "oracle-initialized stage residual solve expected a near-root; "
            f"got residual {residual_norm:.3e} at t={float(t):.6g}"
        )
    q, v, a, lam = unpack_closed_loop_fullva_stage_vector(initial_stage_vector, context.nb, context.nc)
    return {
        "stage_vector": np.asarray(initial_stage_vector, dtype=float).reshape(-1).copy(),
        "q": q.copy(),
        "v": v.copy(),
        "a": a.copy(),
        "lambda": lam.copy(),
        "residual_inf": residual_norm,
        "newton_iterations": 0,
        "solve_policy": "oracle_initialized_residual_check",
    }


def finite_difference_jacobian(
    residual_fn,
    x: np.ndarray,
    f0: np.ndarray,
    *,
    rel_step: float = 1.0e-6,
    abs_step: float = 1.0e-8,
) -> np.ndarray:
    """Forward finite-difference Jacobian for a small dense stage system."""

    x0 = np.asarray(x, dtype=float).reshape(-1)
    base = np.asarray(f0, dtype=float).reshape(-1)
    jac = np.empty((base.size, x0.size), dtype=float)
    for j in range(x0.size):
        step = abs_step + rel_step * max(1.0, abs(float(x0[j])))
        xp = x0.copy()
        xp[j] += step
        jac[:, j] = (np.asarray(residual_fn(xp), dtype=float).reshape(-1) - base) / step
    return jac


def newton_solve_closed_loop_fullva_stage(
    system,
    t: float,
    context: ClosedLoopStageContext,
    initial_stage_vector: np.ndarray,
    *,
    tol: float = 1.0e-10,
    max_iters: int = 12,
    rel_step: float = 1.0e-6,
    abs_step: float = 1.0e-8,
    min_damping: float = 1.0e-4,
) -> dict[str, object]:
    """Damped Newton solve from a non-oracle predictor.

    This intentionally uses a dense finite-difference Jacobian because the
    current closed-loop runner is still a single-step smoke path. It is not the
    production Jacobian strategy for the eventual convergence campaign.
    """

    x = np.asarray(initial_stage_vector, dtype=float).reshape(-1).copy()

    def residual_fn(vec: np.ndarray) -> np.ndarray:
        return closed_loop_fullva_stage_residual(system, t, vec, context)

    f = residual_fn(x)
    residual_initial = float(np.linalg.norm(f, ord=np.inf))
    residual_norm = residual_initial
    iteration_log: list[dict[str, float]] = []
    line_search_failures = 0
    converged = residual_norm <= tol
    last_step_norm = 0.0

    for iteration in range(1, max_iters + 1):
        if converged:
            break
        jac = finite_difference_jacobian(residual_fn, x, f, rel_step=rel_step, abs_step=abs_step)
        delta, *_ = np.linalg.lstsq(jac, -f, rcond=None)
        last_step_norm = float(np.linalg.norm(delta, ord=np.inf))
        damping = 1.0
        accepted = False
        candidate_norm = residual_norm
        candidate_f = f
        candidate_x = x
        while damping >= min_damping:
            trial_x = x + damping * delta
            trial_f = residual_fn(trial_x)
            trial_norm = float(np.linalg.norm(trial_f, ord=np.inf))
            if np.isfinite(trial_norm) and trial_norm < residual_norm:
                accepted = True
                candidate_x = trial_x
                candidate_f = trial_f
                candidate_norm = trial_norm
                break
            damping *= 0.5
        iteration_log.append(
            {
                "iteration": float(iteration),
                "residual_inf_before": residual_norm,
                "residual_inf_after": candidate_norm,
                "step_inf": last_step_norm,
                "damping": damping if accepted else 0.0,
            }
        )
        if not accepted:
            line_search_failures += 1
            break
        x = candidate_x
        f = candidate_f
        residual_norm = candidate_norm
        converged = residual_norm <= tol

    q, v, a, lam = unpack_closed_loop_fullva_stage_vector(x, context.nb, context.nc)
    return {
        "stage_vector": x.copy(),
        "q": q.copy(),
        "v": v.copy(),
        "a": a.copy(),
        "lambda": lam.copy(),
        "residual_inf_initial": residual_initial,
        "residual_inf": residual_norm,
        "newton_iterations": len(iteration_log),
        "line_search_failures": line_search_failures,
        "last_step_inf": last_step_norm,
        "converged": converged,
        "iteration_log": iteration_log,
        "solve_policy": "damped_finite_difference_newton_from_start_extrapolated_predictor",
    }


def start_extrapolated_closed_loop_stage_vector(
    system,
    context: ClosedLoopStageContext,
    tau: float,
    lambda0: np.ndarray,
) -> np.ndarray:
    q0, v0, a0 = generalized_qva_from_system(system, context)
    tau_f = float(tau)
    q_guess = q0 + tau_f * v0 + 0.5 * tau_f * tau_f * a0
    v_guess = v0 + tau_f * a0
    a_guess = a0
    return pack_closed_loop_fullva_stage_vector(q_guess, v_guess, a_guess, lambda0)


def _apply_gauss6_endpoint_update(
    system,
    start: dict[str, np.ndarray],
    stage_solutions: list[dict[str, object]],
    h: float,
) -> None:
    stage_v = np.vstack([np.asarray(solution["v"], dtype=float).reshape(1, -1) for solution in stage_solutions])
    stage_a = np.vstack([np.asarray(solution["a"], dtype=float).reshape(1, -1) for solution in stage_solutions])
    nb = int(system.nb)
    r_end = start["r"] + float(h) * (GAUSS6_B @ stage_v[:, : 3 * nb])
    dr_end = start["dr"] + float(h) * (GAUSS6_B @ stage_a[:, : 3 * nb])
    omega_end = start["omega"] + float(h) * (GAUSS6_B @ stage_a[:, 3 * nb : 6 * nb])
    avg_acc = GAUSS6_B @ stage_a[:, : 3 * nb]
    avg_alpha = GAUSS6_B @ stage_a[:, 3 * nb : 6 * nb]

    _set_body_vectors(system, "r", r_end)
    _set_body_vectors(system, "dr", dr_end)
    _set_body_vectors(system, "ddr", avg_acc)
    _set_body_vectors(system, "ω", omega_end)
    _set_body_vectors(system, "dω", avg_alpha)
    for j, body in enumerate(system.bodies):
        theta_dot_stages = []
        for solution in stage_solutions:
            q = np.asarray(solution["q"], dtype=float).reshape(-1)
            v = np.asarray(solution["v"], dtype=float).reshape(-1)
            theta = q[3 * (nb + j) : 3 * (nb + j + 1)]
            omega = v[3 * (nb + j) : 3 * (nb + j + 1)]
            theta_dot_stages.append(right_jacobian_inverse_so3(theta) @ omega)
        dtheta = float(h) * (GAUSS6_B @ np.vstack(theta_dot_stages))
        body.A = start["A"][j] @ exp_so3(dtheta)


def gauss6_closed_loop_fullva_dynamic_step_newton_smoke(
    system,
    t0: float,
    h: float,
    v047_module,
    *,
    tol: float = 1.0e-10,
    max_iters: int = 12,
) -> dict[str, object]:
    """Run one non-oracle-predicted Gauss6/FullVA dynamic step smoke.

    The stage predictor is built only from the accepted start-of-step state and
    a constant-acceleration extrapolation. It does not call the kinematic oracle
    at stage times. The endpoint update is still a single-step smoke, not a
    three-step convergence/order runner.
    """

    start = endpoint_state_from_system(system)
    context = capture_stage_context(system)
    system.g_cons.maybe_swap_gcons(float(t0))
    lambda0, *_ = v047_module.reconstruct_v046_reaction_dynamics(system, float(t0))
    stage_solutions: list[dict[str, object]] = []
    max_initial_residual = 0.0
    max_stage_residual = 0.0
    for c_i in GAUSS6_C:
        tau = float(h * c_i)
        t_stage = float(t0 + tau)
        initial_stage_vector = start_extrapolated_closed_loop_stage_vector(system, context, tau, lambda0)
        solved = newton_solve_closed_loop_fullva_stage(
            system,
            t_stage,
            context,
            initial_stage_vector,
            tol=tol,
            max_iters=max_iters,
        )
        stage_solutions.append(solved)
        max_initial_residual = max(max_initial_residual, float(solved["residual_inf_initial"]))
        max_stage_residual = max(max_stage_residual, float(solved["residual_inf"]))

    _apply_gauss6_endpoint_update(system, start, stage_solutions, h)

    return {
        "step_policy": "non_oracle_newton_one_step_smoke_not_order",
        "stage_predictor_policy": "start_extrapolated_no_stage_oracle",
        "stage_oracle_used": False,
        "stage_solutions": stage_solutions,
        "max_initial_stage_residual_inf": max_initial_residual,
        "max_stage_residual_inf": max_stage_residual,
        "total_stage_newton_iterations": sum(int(solution["newton_iterations"]) for solution in stage_solutions),
        "line_search_failures": sum(int(solution["line_search_failures"]) for solution in stage_solutions),
        "all_stages_converged": all(bool(solution["converged"]) for solution in stage_solutions),
        "endpoint_state": endpoint_state_from_system(system),
        "trajectory_stepper_implemented": True,
        "simulate_runner_implemented": False,
        "accepted_dynamic_order": False,
    }


def gauss6_closed_loop_fullva_dynamic_step(
    system,
    t0: float,
    h: float,
    v047_module,
    *,
    tol: float = 1.0e-12,
) -> dict[str, object]:
    """Run one oracle-initialized Gauss6/FullVA dynamic step smoke.

    Stage states are initialized with the existing kinematic oracle and then
    checked against the local dynamic residual. This exercises endpoint
    quadrature and residual assembly, but it is not a standalone trajectory
    integrator and must not be used as accepted order evidence.
    """

    start = endpoint_state_from_system(system)
    context = capture_stage_context(system)
    stage_solutions: list[dict[str, object]] = []
    max_stage_residual = 0.0
    for c_i in GAUSS6_C:
        t_stage = float(t0 + h * c_i)
        v047_module.solve_v046_local_kinematic_fullva_time(system, t_stage, tol)
        lam, *_ = v047_module.reconstruct_v046_reaction_dynamics(system, t_stage)
        q, v, a = generalized_qva_from_system(system, context)
        stage_vector = pack_closed_loop_fullva_stage_vector(q, v, a, lam)
        solved = solve_closed_loop_fullva_stage(system, t_stage, context, stage_vector, tol=max(1.0e-10, 100.0 * tol))
        stage_solutions.append(solved)
        max_stage_residual = max(max_stage_residual, float(solved["residual_inf"]))

    _apply_gauss6_endpoint_update(system, start, stage_solutions, h)

    return {
        "step_policy": "oracle_initialized_one_step_smoke_not_order",
        "stage_solutions": stage_solutions,
        "max_stage_residual_inf": max_stage_residual,
        "endpoint_state": endpoint_state_from_system(system),
        "trajectory_stepper_implemented": True,
        "simulate_runner_implemented": False,
        "accepted_dynamic_order": False,
    }


def simulate_v046_local_dynamic_fullva(*_args, **_kwargs):
    raise NotImplementedError("closed-loop local dynamic FullVA trajectory simulator is not implemented yet")
