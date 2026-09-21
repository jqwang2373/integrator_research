#!/usr/bin/env python3
"""Source-paper pendulum parameter model for the TFE benchmark suite.

This module implements the source-paper pendulum parameters, the published
metric/output policy at a planar smoke-test level, an absolute-coordinate
constraint/dynamics residual smoke, and a Brown--McPhee-style candidate
friction scaffold whose provenance is local v022 surrogate code. It is still
not the TFE/Newmark/trapezoidal source-policy runner and not a verified
source-code equivalent of the original Brown--McPhee friction law.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import time

import numpy as np


GRAVITY = 9.81


@dataclass(frozen=True)
class SourcePendulumParameters:
    mass_kg: float = 10.0
    length_m: float = 2.0
    hinge_pin_radius_m: float = 0.5
    center_of_mass_x_m: float = 3.09
    mu_static: float = 0.3
    mu_dynamic: float = 0.2
    gravity_axis: str = "-Y"

    def inertia_kg_m2(self) -> np.ndarray:
        return np.array(
            [
                [0.05, 0.0, 0.0],
                [0.0, 0.03, 0.015],
                [0.0, 0.015, 0.028],
            ],
            dtype=float,
        )


@dataclass(frozen=True)
class SourcePlanarState:
    theta: float
    omega: float


@dataclass(frozen=True)
class SourceAbsoluteState:
    position_m: np.ndarray
    velocity_m_s: np.ndarray
    rotation: np.ndarray
    angular_velocity_rad_s: np.ndarray


@dataclass(frozen=True)
class BoundedSourcePolicyRunnerConfig:
    theta0: float = 0.0
    omega0: float = 0.0
    t_final: float = 0.024
    comparison_h: tuple[float, ...] = (0.012, 0.006, 0.003)
    reference_h: float = 0.0001
    axis: str = "z"
    frictional: bool = False
    stribeck_velocity: float = 0.5
    viscous_damping: float = 0.0


def source_parameters() -> SourcePendulumParameters:
    return SourcePendulumParameters()


def planar_rotation_matrix(theta: float, *, axis: str = "z") -> np.ndarray:
    c = float(np.cos(theta))
    s = float(np.sin(theta))
    if axis == "x":
        return np.array([[1.0, 0.0, 0.0], [0.0, c, -s], [0.0, s, c]], dtype=float)
    if axis == "y":
        return np.array([[c, 0.0, s], [0.0, 1.0, 0.0], [-s, 0.0, c]], dtype=float)
    if axis == "z":
        return np.array([[c, -s, 0.0], [s, c, 0.0], [0.0, 0.0, 1.0]], dtype=float)
    raise ValueError(f"unsupported hinge axis: {axis}")


def wrapped_angle_error(reference: float, candidate: float) -> float:
    return float((candidate - reference + np.pi) % (2.0 * np.pi) - np.pi)


def frobenius_orientation_error(reference_theta: float, candidate_theta: float, *, axis: str = "z") -> float:
    reference_rotation = planar_rotation_matrix(reference_theta, axis=axis)
    candidate_rotation = planar_rotation_matrix(candidate_theta, axis=axis)
    return float(np.linalg.norm(candidate_rotation - reference_rotation, ord="fro"))


def source_output_policy() -> dict[str, str]:
    """Return the source-paper output metrics encoded by this scaffold."""

    return {
        "coordinate_error_order_q": "absolute wrapped planar coordinate error |theta_h - theta_ref|",
        "velocity_error_order_v": "absolute planar angular-velocity error |omega_h - omega_ref|",
        "Frobenius_error_norm_eta": "Frobenius norm of the planar rotation-matrix difference",
        "mechanical_energy_deviation": "candidate minus reference planar mechanical energy",
    }


def source_error_metrics(
    reference: SourcePlanarState,
    candidate: SourcePlanarState,
    *,
    axis: str = "z",
    params: SourcePendulumParameters | None = None,
) -> dict[str, float]:
    angle_error = wrapped_angle_error(reference.theta, candidate.theta)
    velocity_error = float(candidate.omega - reference.omega)
    return {
        "coordinate_error_q": abs(angle_error),
        "signed_coordinate_error_q": angle_error,
        "velocity_error_v": abs(velocity_error),
        "signed_velocity_error_v": velocity_error,
        "frobenius_error_norm_eta": frobenius_orientation_error(reference.theta, candidate.theta, axis=axis),
        "mechanical_energy_deviation": frictionless_planar_energy(
            candidate.theta, candidate.omega, axis=axis, params=params
        )
        - frictionless_planar_energy(reference.theta, reference.omega, axis=axis, params=params),
    }


def candidate_planar_reductions(params: SourcePendulumParameters | None = None) -> dict[str, dict[str, float]]:
    """Return hinge-axis planar reductions implied by the source parameters.

    The source paper's table fixes the body parameters but the full
    source-policy runner still needs the exact DAE output/norm and friction
    policy. These reductions are therefore smoke-test scaffolds only.
    """

    params = params or source_parameters()
    inertia = params.inertia_kg_m2()
    r = np.array([params.center_of_mass_x_m, 0.0, 0.0], dtype=float)
    gravity = np.array([0.0, -GRAVITY, 0.0], dtype=float)
    axes = {
        "x": np.array([1.0, 0.0, 0.0]),
        "y": np.array([0.0, 1.0, 0.0]),
        "z": np.array([0.0, 0.0, 1.0]),
    }
    reductions: dict[str, dict[str, float]] = {}
    for name, axis in axes.items():
        parallel = float(axis @ inertia @ axis)
        perpendicular_sq = float(np.dot(r, r) - np.dot(axis, r) ** 2)
        inertia_about_pin = parallel + params.mass_kg * perpendicular_sq
        torque_scale = float(np.linalg.norm(np.cross(r, params.mass_kg * gravity) @ axis))
        reductions[name] = {
            "body_inertia_about_axis": parallel,
            "parallel_axis_inertia_about_pin": inertia_about_pin,
            "gravity_torque_scale": torque_scale,
            "nondegenerate_frictionless_planar_candidate": bool(inertia_about_pin > 0.0 and torque_scale > 0.0),
        }
    return reductions


@lru_cache(maxsize=None)
def _cached_planar_reduction(
    params: SourcePendulumParameters,
    axis: str,
) -> tuple[float, float, bool]:
    reductions = candidate_planar_reductions(params)
    if axis not in reductions:
        raise ValueError(f"unsupported hinge axis: {axis}")
    reduction = reductions[axis]
    return (
        float(reduction["parallel_axis_inertia_about_pin"]),
        float(reduction["gravity_torque_scale"]),
        bool(reduction["nondegenerate_frictionless_planar_candidate"]),
    )


def planar_reduction_constants(
    axis: str = "z",
    *,
    params: SourcePendulumParameters | None = None,
) -> tuple[float, float]:
    params = params or source_parameters()
    inertia, torque_scale, nondegenerate = _cached_planar_reduction(params, axis)
    if not nondegenerate:
        raise ValueError(f"hinge axis {axis} is degenerate for the planar gravity smoke model")
    return inertia, torque_scale


def frictionless_planar_rhs(
    theta: float,
    omega: float,
    *,
    axis: str = "z",
    params: SourcePendulumParameters | None = None,
) -> tuple[float, float]:
    params = params or source_parameters()
    inertia, torque_scale = planar_reduction_constants(axis, params=params)
    return float(omega), float(-(torque_scale / inertia) * np.cos(theta))


def frictionless_planar_energy(
    theta: float,
    omega: float,
    *,
    axis: str = "z",
    params: SourcePendulumParameters | None = None,
) -> float:
    params = params or source_parameters()
    inertia, torque_scale = planar_reduction_constants(axis, params=params)
    return float(0.5 * inertia * omega * omega + torque_scale * np.sin(theta))


def planar_pivot_reaction_norm(
    theta: float,
    omega: float,
    alpha: float,
    *,
    axis: str = "z",
    params: SourcePendulumParameters | None = None,
) -> float:
    """Return a planar candidate pivot-reaction norm for friction-load coupling."""

    if axis != "z":
        raise ValueError("candidate frictional reaction smoke currently supports only the z hinge axis")
    params = params or source_parameters()
    d = params.center_of_mass_x_m
    rddot = d * np.array(
        [
            -np.cos(theta) * omega * omega - np.sin(theta) * alpha,
            -np.sin(theta) * omega * omega + np.cos(theta) * alpha,
            0.0,
        ],
        dtype=float,
    )
    gravity = np.array([0.0, -GRAVITY, 0.0], dtype=float)
    reaction = params.mass_kg * (rddot - gravity)
    return float(np.linalg.norm(reaction))


def brown_mcphee_candidate_torque(
    omega: float,
    normal_load: float,
    *,
    stribeck_velocity: float,
    viscous_damping: float = 0.0,
    params: SourcePendulumParameters | None = None,
) -> float:
    """Brown--McPhee-style candidate torque from the local v022 surrogate.

    This is intentionally named ``candidate`` because the source TFE paper does
    not provide enough law detail here to certify source-policy equivalence.
    """

    params = params or source_parameters()
    vs = max(float(stribeck_velocity), 1.0e-12)
    z = float(omega) / vs
    denominator = (0.25 * z * z + 0.75) ** 2
    coulomb_stiction = params.mu_dynamic * np.tanh(4.0 * z) + (
        params.mu_static - params.mu_dynamic
    ) * z / denominator
    load = max(float(normal_load), 0.0)
    return float(
        -params.hinge_pin_radius_m * load * coulomb_stiction
        - float(viscous_damping) * np.tanh(4.0) * float(omega)
    )


def frictional_planar_rhs(
    theta: float,
    omega: float,
    *,
    axis: str = "z",
    stribeck_velocity: float = 0.5,
    viscous_damping: float = 0.0,
    params: SourcePendulumParameters | None = None,
) -> tuple[float, float]:
    """Candidate frictional planar RHS with a fixed-point normal-load update."""

    if axis != "z":
        raise ValueError("candidate frictional RHS currently supports only the z hinge axis")
    params = params or source_parameters()
    inertia, torque_scale = planar_reduction_constants(axis, params=params)
    gravity_torque = -torque_scale * float(np.cos(theta))
    alpha = gravity_torque / inertia
    for _ in range(12):
        normal_load = planar_pivot_reaction_norm(theta, omega, alpha, axis=axis, params=params)
        friction_torque = brown_mcphee_candidate_torque(
            omega,
            normal_load,
            stribeck_velocity=stribeck_velocity,
            viscous_damping=viscous_damping,
            params=params,
        )
        next_alpha = (gravity_torque + friction_torque) / inertia
        if abs(next_alpha - alpha) < 1.0e-13:
            alpha = next_alpha
            break
        alpha = next_alpha
    return float(omega), float(alpha)


def absolute_state_from_planar(
    theta: float,
    omega: float,
    *,
    axis: str = "z",
    params: SourcePendulumParameters | None = None,
) -> SourceAbsoluteState:
    if axis != "z":
        raise ValueError("absolute-coordinate smoke currently supports only the z hinge axis")
    params = params or source_parameters()
    rotation = planar_rotation_matrix(theta, axis=axis)
    body_hinge_to_com = np.array([params.center_of_mass_x_m, 0.0, 0.0], dtype=float)
    position = rotation @ body_hinge_to_com
    angular_velocity = np.array([0.0, 0.0, float(omega)], dtype=float)
    velocity = np.cross(angular_velocity, position)
    return SourceAbsoluteState(
        position_m=position,
        velocity_m_s=velocity,
        rotation=rotation,
        angular_velocity_rad_s=angular_velocity,
    )


def absolute_coordinate_dae_residual_smoke(
    theta: float = 0.2,
    omega: float = 0.3,
    *,
    frictional: bool = False,
    stribeck_velocity: float = 0.5,
    axis: str = "z",
    params: SourcePendulumParameters | None = None,
) -> dict[str, float]:
    """Return an absolute-coordinate pendulum residual smoke.

    The residual reconstructs hinge reaction force and constrained joint torque
    for the source pendulum geometry. It is a consistency smoke, not a TFE
    time-integration runner.
    """

    if axis != "z":
        raise ValueError("absolute-coordinate smoke currently supports only the z hinge axis")
    params = params or source_parameters()
    state = absolute_state_from_planar(theta, omega, axis=axis, params=params)
    if frictional:
        _, alpha = frictional_planar_rhs(
            theta,
            omega,
            axis=axis,
            stribeck_velocity=stribeck_velocity,
            params=params,
        )
    else:
        _, alpha = frictionless_planar_rhs(theta, omega, axis=axis, params=params)

    body_hinge_to_com = np.array([params.center_of_mass_x_m, 0.0, 0.0], dtype=float)
    hinge_position = state.position_m - state.rotation @ body_hinge_to_com
    hinge_velocity = state.velocity_m_s - np.cross(
        state.angular_velocity_rad_s,
        state.rotation @ body_hinge_to_com,
    )
    angular_acceleration = np.array([0.0, 0.0, float(alpha)], dtype=float)
    acceleration = np.cross(angular_acceleration, state.position_m) + np.cross(
        state.angular_velocity_rad_s,
        np.cross(state.angular_velocity_rad_s, state.position_m),
    )
    gravity = np.array([0.0, -GRAVITY, 0.0], dtype=float)
    hinge_reaction = params.mass_kg * (acceleration - gravity)
    translational_residual = params.mass_kg * acceleration - params.mass_kg * gravity - hinge_reaction

    inertia_world = state.rotation @ params.inertia_kg_m2() @ state.rotation.T
    angular_left = inertia_world @ angular_acceleration + np.cross(
        state.angular_velocity_rad_s,
        inertia_world @ state.angular_velocity_rad_s,
    )
    friction_torque = 0.0
    if frictional:
        friction_torque = brown_mcphee_candidate_torque(
            omega,
            float(np.linalg.norm(hinge_reaction)),
            stribeck_velocity=stribeck_velocity,
            params=params,
        )
    axis_vector = np.array([0.0, 0.0, 1.0], dtype=float)
    hinge_moment_about_com = np.cross(-state.position_m, hinge_reaction)
    unconstrained_rotational_residual = angular_left - hinge_moment_about_com - friction_torque * axis_vector
    axis_projected_rotational_residual = float(unconstrained_rotational_residual @ axis_vector)
    constrained_joint_torque = unconstrained_rotational_residual - axis_projected_rotational_residual * axis_vector

    return {
        "theta": float(theta),
        "omega": float(omega),
        "alpha": float(alpha),
        "frictional": bool(frictional),
        "hinge_position_constraint_norm": float(np.linalg.norm(hinge_position)),
        "hinge_velocity_constraint_norm": float(np.linalg.norm(hinge_velocity)),
        "rotation_orthogonality_residual_norm": float(np.linalg.norm(state.rotation.T @ state.rotation - np.eye(3))),
        "angular_velocity_axis_constraint_norm": float(np.linalg.norm(state.angular_velocity_rad_s[:2])),
        "translational_balance_residual_norm": float(np.linalg.norm(translational_residual)),
        "axis_projected_rotational_residual": axis_projected_rotational_residual,
        "axis_projected_rotational_residual_abs": abs(axis_projected_rotational_residual),
        "constrained_joint_torque_required_norm": float(np.linalg.norm(constrained_joint_torque)),
        "hinge_reaction_norm": float(np.linalg.norm(hinge_reaction)),
        "candidate_friction_torque": float(friction_torque),
        "candidate_friction_power": float(friction_torque * omega),
        "source_policy_dae_runner_equivalent": False,
    }


def rk4_step(theta: float, omega: float, h: float, *, axis: str = "z") -> tuple[float, float]:
    def rhs(state: np.ndarray) -> np.ndarray:
        dtheta, domega = frictionless_planar_rhs(float(state[0]), float(state[1]), axis=axis)
        return np.array([dtheta, domega], dtype=float)

    y0 = np.array([theta, omega], dtype=float)
    k1 = rhs(y0)
    k2 = rhs(y0 + 0.5 * h * k1)
    k3 = rhs(y0 + 0.5 * h * k2)
    k4 = rhs(y0 + h * k3)
    y1 = y0 + (h / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)
    return float(y1[0]), float(y1[1])


def rk4_step_frictional(
    theta: float,
    omega: float,
    h: float,
    *,
    axis: str = "z",
    stribeck_velocity: float = 0.5,
    viscous_damping: float = 0.0,
) -> tuple[float, float]:
    def rhs(state: np.ndarray) -> np.ndarray:
        dtheta, domega = frictional_planar_rhs(
            float(state[0]),
            float(state[1]),
            axis=axis,
            stribeck_velocity=stribeck_velocity,
            viscous_damping=viscous_damping,
        )
        return np.array([dtheta, domega], dtype=float)

    y0 = np.array([theta, omega], dtype=float)
    k1 = rhs(y0)
    k2 = rhs(y0 + 0.5 * h * k1)
    k3 = rhs(y0 + 0.5 * h * k2)
    k4 = rhs(y0 + h * k3)
    y1 = y0 + (h / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)
    return float(y1[0]), float(y1[1])


def planar_acceleration(
    theta: float,
    omega: float,
    *,
    frictional: bool = False,
    axis: str = "z",
    stribeck_velocity: float = 0.5,
    viscous_damping: float = 0.0,
) -> float:
    if frictional:
        _, alpha = frictional_planar_rhs(
            theta,
            omega,
            axis=axis,
            stribeck_velocity=stribeck_velocity,
            viscous_damping=viscous_damping,
        )
    else:
        _, alpha = frictionless_planar_rhs(theta, omega, axis=axis)
    return float(alpha)


def _finite_difference_jacobian(residual, x: np.ndarray) -> np.ndarray:
    jac = np.zeros((x.size, x.size), dtype=float)
    root_eps = float(np.sqrt(np.finfo(float).eps))
    for idx in range(x.size):
        delta = root_eps * max(1.0, abs(float(x[idx])))
        xp = x.copy()
        xm = x.copy()
        xp[idx] += delta
        xm[idx] -= delta
        jac[:, idx] = (residual(xp) - residual(xm)) / (2.0 * delta)
    return jac


def _newton_solve_2d(initial: np.ndarray, residual, *, tolerance: float = 1.0e-12) -> tuple[np.ndarray, int, float]:
    x = np.array(initial, dtype=float)
    last_norm = np.inf
    for iteration in range(12):
        value = residual(x)
        last_norm = float(np.linalg.norm(value))
        if last_norm <= tolerance:
            return x, iteration, last_norm
        jacobian = _finite_difference_jacobian(residual, x)
        try:
            delta = np.linalg.solve(jacobian, -value)
        except np.linalg.LinAlgError:
            delta = np.linalg.lstsq(jacobian, -value, rcond=None)[0]
        x = x + delta
        if float(np.linalg.norm(delta)) <= tolerance * max(1.0, float(np.linalg.norm(x))):
            value = residual(x)
            last_norm = float(np.linalg.norm(value))
            return x, iteration + 1, last_norm
    return x, 12, last_norm


def trapezoidal_candidate_step(
    theta: float,
    omega: float,
    h: float,
    *,
    frictional: bool = False,
    axis: str = "z",
    stribeck_velocity: float = 0.5,
    viscous_damping: float = 0.0,
) -> tuple[float, float, int, float]:
    a0 = planar_acceleration(
        theta,
        omega,
        frictional=frictional,
        axis=axis,
        stribeck_velocity=stribeck_velocity,
        viscous_damping=viscous_damping,
    )

    def residual(x: np.ndarray) -> np.ndarray:
        theta1 = float(x[0])
        omega1 = float(x[1])
        a1 = planar_acceleration(
            theta1,
            omega1,
            frictional=frictional,
            axis=axis,
            stribeck_velocity=stribeck_velocity,
            viscous_damping=viscous_damping,
        )
        return np.array(
            [
                theta1 - theta - 0.5 * h * (omega + omega1),
                omega1 - omega - 0.5 * h * (a0 + a1),
            ],
            dtype=float,
        )

    guess = np.array([theta + h * omega + 0.5 * h * h * a0, omega + h * a0], dtype=float)
    solution, iterations, residual_norm = _newton_solve_2d(guess, residual)
    return float(solution[0]), float(solution[1]), int(iterations), float(residual_norm)


def newmark_beta_candidate_step(
    theta: float,
    omega: float,
    h: float,
    *,
    beta: float = 0.3,
    gamma: float = 0.5,
    frictional: bool = False,
    axis: str = "z",
    stribeck_velocity: float = 0.5,
    viscous_damping: float = 0.0,
) -> tuple[float, float, int, float]:
    a0 = planar_acceleration(
        theta,
        omega,
        frictional=frictional,
        axis=axis,
        stribeck_velocity=stribeck_velocity,
        viscous_damping=viscous_damping,
    )

    def residual(x: np.ndarray) -> np.ndarray:
        theta1 = float(x[0])
        omega1 = float(x[1])
        a1 = planar_acceleration(
            theta1,
            omega1,
            frictional=frictional,
            axis=axis,
            stribeck_velocity=stribeck_velocity,
            viscous_damping=viscous_damping,
        )
        return np.array(
            [
                theta1 - theta - h * omega - h * h * ((0.5 - beta) * a0 + beta * a1),
                omega1 - omega - h * ((1.0 - gamma) * a0 + gamma * a1),
            ],
            dtype=float,
        )

    guess = np.array([theta + h * omega + 0.5 * h * h * a0, omega + h * a0], dtype=float)
    solution, iterations, residual_norm = _newton_solve_2d(guess, residual)
    return float(solution[0]), float(solution[1]), int(iterations), float(residual_norm)


def gauss6_fullva_candidate_step(
    theta: float,
    omega: float,
    h: float,
    *,
    frictional: bool = False,
    axis: str = "z",
    stribeck_velocity: float = 0.5,
    viscous_damping: float = 0.0,
) -> tuple[float, float, int, float]:
    """Three-stage Gauss candidate for the source-pendulum same-test scaffold.

    This is the scalar planar specialization used to put the paper's sixth-order
    Gauss-collocation target on the same source-pendulum metric runner as the
    TFE/Newmark/trapezoidal candidates. It is not the absolute-coordinate
    monolithic FullVA DAE source-policy runner.
    """

    sqrt15 = float(np.sqrt(15.0))
    nodes = np.array([0.5 - sqrt15 / 10.0, 0.5, 0.5 + sqrt15 / 10.0], dtype=float)
    butcher_a = np.array(
        [
            [5.0 / 36.0, 2.0 / 9.0 - sqrt15 / 15.0, 5.0 / 36.0 - sqrt15 / 30.0],
            [5.0 / 36.0 + sqrt15 / 24.0, 2.0 / 9.0, 5.0 / 36.0 - sqrt15 / 24.0],
            [5.0 / 36.0 + sqrt15 / 30.0, 2.0 / 9.0 + sqrt15 / 15.0, 5.0 / 36.0],
        ],
        dtype=float,
    )
    butcher_b = np.array([5.0 / 18.0, 4.0 / 9.0, 5.0 / 18.0], dtype=float)
    a0 = planar_acceleration(
        theta,
        omega,
        frictional=frictional,
        axis=axis,
        stribeck_velocity=stribeck_velocity,
        viscous_damping=viscous_damping,
    )

    def rhs_pair(stage_theta: float, stage_omega: float) -> np.ndarray:
        return np.array(
            [
                stage_omega,
                planar_acceleration(
                    stage_theta,
                    stage_omega,
                    frictional=frictional,
                    axis=axis,
                    stribeck_velocity=stribeck_velocity,
                    viscous_damping=viscous_damping,
                ),
            ],
            dtype=float,
        )

    def unpack(x: np.ndarray) -> np.ndarray:
        return np.asarray(x, dtype=float).reshape((3, 2))

    def residual(x: np.ndarray) -> np.ndarray:
        stages = unpack(x)
        stage_rhs = np.array([rhs_pair(float(row[0]), float(row[1])) for row in stages], dtype=float)
        y0 = np.array([theta, omega], dtype=float)
        values = []
        for idx in range(3):
            defect = stages[idx] - y0 - h * np.sum(butcher_a[idx, :, None] * stage_rhs, axis=0)
            values.extend([float(defect[0]), float(defect[1])])
        return np.array(values, dtype=float)

    guess_rows = []
    for node in nodes:
        dt = float(node) * h
        guess_rows.append([theta + dt * omega + 0.5 * dt * dt * a0, omega + dt * a0])
    solution, iterations, residual_norm = _newton_solve_2d(np.array(guess_rows, dtype=float).reshape(6), residual)
    stages = unpack(solution)
    stage_rhs = np.array([rhs_pair(float(row[0]), float(row[1])) for row in stages], dtype=float)
    y1 = np.array([theta, omega], dtype=float) + h * np.sum(butcher_b[:, None] * stage_rhs, axis=0)
    return float(y1[0]), float(y1[1]), int(iterations), float(residual_norm)


def tfe_m1_candidate_step(
    theta: float,
    omega: float,
    h: float,
    *,
    nu: float = 0.99,
    frictional: bool = False,
    axis: str = "z",
    stribeck_velocity: float = 0.5,
    viscous_damping: float = 0.0,
) -> tuple[float, float, int, float]:
    """One-node TFE candidate step from the Appendix-B coefficient pattern."""

    alpha, beta, gamma, _ = tfe_m1_coefficients(h, nu)
    denom = float(alpha[0, 0] * h)
    vel_prev_acc_coeff = -float(gamma[0]) / denom
    vel_new_acc_coeff = 1.0 / denom
    pos_prev_acc_coeff = -float(gamma[0]) / denom**2
    pos_new_acc_coeff = 1.0 / denom**2
    a0 = planar_acceleration(
        theta,
        omega,
        frictional=frictional,
        axis=axis,
        stribeck_velocity=stribeck_velocity,
        viscous_damping=viscous_damping,
    )

    def residual(x: np.ndarray) -> np.ndarray:
        a1 = float(x[0])
        theta1 = theta + h * omega + h * h * (pos_prev_acc_coeff * a0 + pos_new_acc_coeff * a1)
        omega1 = omega + h * (vel_prev_acc_coeff * a0 + vel_new_acc_coeff * a1)
        return np.array(
            [
                a1
                - planar_acceleration(
                    theta1,
                    omega1,
                    frictional=frictional,
                    axis=axis,
                    stribeck_velocity=stribeck_velocity,
                    viscous_damping=viscous_damping,
                )
            ],
            dtype=float,
        )

    solution, iterations, residual_norm = _newton_solve_2d(np.array([a0], dtype=float), residual)
    a1 = float(solution[0])
    theta1 = theta + h * omega + h * h * (pos_prev_acc_coeff * a0 + pos_new_acc_coeff * a1)
    omega1 = omega + h * (vel_prev_acc_coeff * a0 + vel_new_acc_coeff * a1)
    return float(theta1), float(omega1), int(iterations), float(residual_norm)


def tfe_m1_coefficients(h: float, nu: float) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    return (
        np.array([[1.0 + nu]], dtype=float) / h,
        np.array([-(1.0 + nu)], dtype=float) / h,
        np.array([-nu], dtype=float),
        np.array([1.0], dtype=float),
    )


def tfe_m2_coefficients(h: float, nu: float) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    alpha_dimless = np.array(
        [
            [1.0 + nu, (3.0 - nu) / 4.0],
            [-4.0 * (1.0 + nu), nu + 3.0],
        ],
        dtype=float,
    )
    beta_dimless = np.array([-(7.0 + 3.0 * nu) / 4.0, 3.0 * nu + 1.0], dtype=float)
    gamma = np.array([-(1.0 + nu) / 4.0, nu], dtype=float)
    tau_nodes = np.array([0.5, 1.0], dtype=float)
    return alpha_dimless / h, beta_dimless / h, gamma, tau_nodes


def tfe_m3_gauss_lobatto_coefficients(
    h: float,
    nu: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    sqrt5 = float(np.sqrt(5.0))
    alpha_nu = np.array(
        [
            [1.0, (sqrt5 - 3.0) / 2.0, (sqrt5 - 1.0) / 10.0],
            [-(sqrt5 + 3.0) / 2.0, 1.0, -(sqrt5 + 1.0) / 10.0],
            [5.0 * (1.0 + sqrt5) / 2.0, 5.0 * (1.0 - sqrt5) / 2.0, 1.0],
        ],
        dtype=float,
    )
    alpha_constant = np.array(
        [
            [(3.0 + sqrt5) / 2.0, -1.0 + sqrt5, (3.0 - 2.0 * sqrt5) / 5.0],
            [-1.0 - sqrt5, (3.0 - sqrt5) / 2.0, (3.0 + 2.0 * sqrt5) / 5.0],
            [5.0 * (sqrt5 - 1.0) / 2.0, -5.0 * (sqrt5 + 1.0) / 2.0, 6.0],
        ],
        dtype=float,
    )
    beta_dimless = np.array(
        [
            (6.0 * nu * (1.0 - sqrt5) - 11.0 * (1.0 + sqrt5)) / 10.0,
            (6.0 * nu * (1.0 + sqrt5) - 11.0 * (1.0 - sqrt5)) / 10.0,
            -6.0 * nu - 1.0,
        ],
        dtype=float,
    )
    gamma = np.array(
        [
            (nu * (1.0 - sqrt5) - 1.0 - sqrt5) / 10.0,
            (nu * (1.0 + sqrt5) - 1.0 + sqrt5) / 10.0,
            -nu,
        ],
        dtype=float,
    )
    tau_nodes = np.array([0.5 - sqrt5 / 10.0, 0.5 + sqrt5 / 10.0, 1.0], dtype=float)
    return (nu * alpha_nu + alpha_constant) / h, beta_dimless / h, gamma, tau_nodes


def tfe_appendix_b_coefficient_certificate(
    *,
    h: float = 0.012,
    nu_m1: float = 0.99,
    nu_m2: float = 0.95,
    nu_m3: float = 0.9,
) -> dict[str, object]:
    """Check implemented TFE coefficients against Appendix-B source formulas.

    This is a source-formula certificate for the scalar coefficient matrices
    only. It does not certify the absolute-coordinate DAE runner, the
    Brown--McPhee friction implementation, or any full source-policy rows.
    """

    sqrt5 = float(np.sqrt(5.0))
    source: dict[str, tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]] = {
        "TFE_m1": (
            np.array([[1.0 + nu_m1]], dtype=float) / h,
            np.array([-(1.0 + nu_m1)], dtype=float) / h,
            np.array([-nu_m1], dtype=float),
            np.array([1.0], dtype=float),
        ),
        "TFE_m2": (
            np.array(
                [
                    [1.0 + nu_m2, (3.0 - nu_m2) / 4.0],
                    [-4.0 * (1.0 + nu_m2), nu_m2 + 3.0],
                ],
                dtype=float,
            )
            / h,
            np.array([-(7.0 + 3.0 * nu_m2) / 4.0, 3.0 * nu_m2 + 1.0], dtype=float) / h,
            np.array([-(1.0 + nu_m2) / 4.0, nu_m2], dtype=float),
            np.array([0.5, 1.0], dtype=float),
        ),
        "TFE_m3_GL": (
            (
                nu_m3
                * np.array(
                    [
                        [1.0, (sqrt5 - 3.0) / 2.0, (sqrt5 - 1.0) / 10.0],
                        [-(sqrt5 + 3.0) / 2.0, 1.0, -(sqrt5 + 1.0) / 10.0],
                        [5.0 * (1.0 + sqrt5) / 2.0, 5.0 * (1.0 - sqrt5) / 2.0, 1.0],
                    ],
                    dtype=float,
                )
                + np.array(
                    [
                        [(3.0 + sqrt5) / 2.0, -1.0 + sqrt5, (3.0 - 2.0 * sqrt5) / 5.0],
                        [-1.0 - sqrt5, (3.0 - sqrt5) / 2.0, (3.0 + 2.0 * sqrt5) / 5.0],
                        [5.0 * (sqrt5 - 1.0) / 2.0, -5.0 * (sqrt5 + 1.0) / 2.0, 6.0],
                    ],
                    dtype=float,
                )
            )
            / h,
            np.array(
                [
                    (6.0 * nu_m3 * (1.0 - sqrt5) - 11.0 * (1.0 + sqrt5)) / 10.0,
                    (6.0 * nu_m3 * (1.0 + sqrt5) - 11.0 * (1.0 - sqrt5)) / 10.0,
                    -6.0 * nu_m3 - 1.0,
                ],
                dtype=float,
            )
            / h,
            np.array(
                [
                    (nu_m3 * (1.0 - sqrt5) - 1.0 - sqrt5) / 10.0,
                    (nu_m3 * (1.0 + sqrt5) - 1.0 + sqrt5) / 10.0,
                    -nu_m3,
                ],
                dtype=float,
            ),
            np.array([0.5 - sqrt5 / 10.0, 0.5 + sqrt5 / 10.0, 1.0], dtype=float),
        ),
    }
    implemented = {
        "TFE_m1": tfe_m1_coefficients(h, nu_m1),
        "TFE_m2": tfe_m2_coefficients(h, nu_m2),
        "TFE_m3_GL": tfe_m3_gauss_lobatto_coefficients(h, nu_m3),
    }

    rows: list[dict[str, object]] = []
    max_abs_diff = 0.0
    for method, source_parts in source.items():
        impl_parts = implemented[method]
        part_diffs = {
            name: float(np.max(np.abs(source_part - impl_part)))
            for name, source_part, impl_part in zip(("alpha", "beta", "gamma", "nodes"), source_parts, impl_parts)
        }
        method_max = max(part_diffs.values())
        max_abs_diff = max(max_abs_diff, method_max)
        rows.append(
            {
                "method": method,
                "max_abs_diff": method_max,
                "part_max_abs_diff": part_diffs,
                "appendix_b_formula_match": bool(method_max <= 1.0e-14),
            }
        )

    return {
        "schema": "tfe-appendix-b-coefficient-certificate-v1",
        "source": "Chaturvedi--Sandu--Sandu Appendix B, equations (40), (41), and (43)",
        "h": float(h),
        "nu": {"TFE_m1": float(nu_m1), "TFE_m2": float(nu_m2), "TFE_m3_GL": float(nu_m3)},
        "checked_methods": [row["method"] for row in rows],
        "row_count": len(rows),
        "max_abs_diff": max_abs_diff,
        "all_appendix_b_formula_matches": bool(max_abs_diff <= 1.0e-14),
        "scope": "coefficient_formula_certificate_only_not_source_policy_runner_equivalence",
        "source_policy_method_runner_equivalent": False,
        "source_policy_rows_completed": 0,
        "rows": rows,
    }


def tfe_multinode_candidate_step(
    theta: float,
    omega: float,
    h: float,
    *,
    m: int,
    nu: float,
    frictional: bool = False,
    axis: str = "z",
    stribeck_velocity: float = 0.5,
    viscous_damping: float = 0.0,
) -> tuple[float, float, int, float]:
    """Planar scalar specialization of source Appendix-B Algorithm 1."""

    if m == 2:
        alpha, beta, gamma, tau_nodes = tfe_m2_coefficients(h, nu)
    elif m == 3:
        alpha, beta, gamma, tau_nodes = tfe_m3_gauss_lobatto_coefficients(h, nu)
    else:
        raise ValueError(f"unsupported TFE candidate m={m}")

    z_prev = planar_acceleration(
        theta,
        omega,
        frictional=frictional,
        axis=axis,
        stribeck_velocity=stribeck_velocity,
        viscous_damping=viscous_damping,
    )
    u_prev = float(theta)
    y_prev = float(omega)
    guess = np.array(
        [
            u_prev + float(tau) * h * y_prev + 0.5 * (float(tau) * h) ** 2 * z_prev
            for tau in tau_nodes
        ],
        dtype=float,
    )

    def stage_velocity_acceleration(u_stages: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        y_stages = alpha @ u_stages + beta * u_prev + gamma * y_prev
        z_stages = alpha @ y_stages + beta * y_prev + gamma * z_prev
        return y_stages, z_stages

    def residual(u_stages: np.ndarray) -> np.ndarray:
        y_stages, z_stages = stage_velocity_acceleration(u_stages)
        values = []
        for theta_stage, omega_stage, accel_stage in zip(u_stages, y_stages, z_stages):
            rhs_accel = planar_acceleration(
                float(theta_stage),
                float(omega_stage),
                frictional=frictional,
                axis=axis,
                stribeck_velocity=stribeck_velocity,
                viscous_damping=viscous_damping,
            )
            values.append(float(accel_stage - rhs_accel))
        return np.array(values, dtype=float)

    solution, iterations, residual_norm = _newton_solve_2d(guess, residual)
    y_solution, _ = stage_velocity_acceleration(solution)
    return float(solution[-1]), float(y_solution[-1]), int(iterations), float(residual_norm)


def smoke_trajectory(
    *,
    theta0: float = 0.0,
    omega0: float = 0.0,
    h: float = 1.0e-3,
    steps: int = 10,
    axis: str = "z",
) -> dict[str, float]:
    theta = float(theta0)
    omega = float(omega0)
    initial_energy = frictionless_planar_energy(theta, omega, axis=axis)
    for _ in range(steps):
        theta, omega = rk4_step(theta, omega, h, axis=axis)
    final_energy = frictionless_planar_energy(theta, omega, axis=axis)
    return {
        "theta0": float(theta0),
        "omega0": float(omega0),
        "theta_final": theta,
        "omega_final": omega,
        "h": float(h),
        "steps": int(steps),
        "energy_initial": initial_energy,
        "energy_final": final_energy,
        "energy_delta": final_energy - initial_energy,
    }


def frictional_smoke_trajectory(
    *,
    theta0: float = 0.0,
    omega0: float = 1.0,
    h: float = 1.0e-3,
    steps: int = 10,
    axis: str = "z",
    stribeck_velocity: float = 0.5,
    viscous_damping: float = 0.0,
) -> dict[str, float]:
    theta = float(theta0)
    omega = float(omega0)
    initial_energy = frictionless_planar_energy(theta, omega, axis=axis)
    max_candidate_friction_power = -np.inf
    min_candidate_friction_power = np.inf
    max_normal_load = 0.0
    for _ in range(steps):
        _, alpha = frictional_planar_rhs(
            theta,
            omega,
            axis=axis,
            stribeck_velocity=stribeck_velocity,
            viscous_damping=viscous_damping,
        )
        normal_load = planar_pivot_reaction_norm(theta, omega, alpha, axis=axis)
        torque = brown_mcphee_candidate_torque(
            omega,
            normal_load,
            stribeck_velocity=stribeck_velocity,
            viscous_damping=viscous_damping,
        )
        power = float(torque * omega)
        max_candidate_friction_power = max(max_candidate_friction_power, power)
        min_candidate_friction_power = min(min_candidate_friction_power, power)
        max_normal_load = max(max_normal_load, normal_load)
        theta, omega = rk4_step_frictional(
            theta,
            omega,
            h,
            axis=axis,
            stribeck_velocity=stribeck_velocity,
            viscous_damping=viscous_damping,
        )
    final_energy = frictionless_planar_energy(theta, omega, axis=axis)
    return {
        "theta0": float(theta0),
        "omega0": float(omega0),
        "theta_final": theta,
        "omega_final": omega,
        "h": float(h),
        "steps": int(steps),
        "stribeck_velocity": float(stribeck_velocity),
        "viscous_damping": float(viscous_damping),
        "energy_initial": initial_energy,
        "energy_final": final_energy,
        "energy_delta": final_energy - initial_energy,
        "max_candidate_friction_power": float(max_candidate_friction_power),
        "min_candidate_friction_power": float(min_candidate_friction_power),
        "max_normal_load": float(max_normal_load),
    }


def integrate_planar_case(
    *,
    theta0: float,
    omega0: float,
    h: float,
    t_final: float,
    frictional: bool = False,
    axis: str = "z",
    stribeck_velocity: float = 0.5,
    viscous_damping: float = 0.0,
) -> SourcePlanarState:
    steps_float = float(t_final) / float(h)
    steps = int(round(steps_float))
    if steps <= 0 or abs(steps_float - steps) > 1.0e-12:
        raise ValueError("t_final must be a positive integer multiple of h")
    theta = float(theta0)
    omega = float(omega0)
    for _ in range(steps):
        if frictional:
            theta, omega = rk4_step_frictional(
                theta,
                omega,
                h,
                axis=axis,
                stribeck_velocity=stribeck_velocity,
                viscous_damping=viscous_damping,
            )
        else:
            theta, omega = rk4_step(theta, omega, h, axis=axis)
    return SourcePlanarState(theta=theta, omega=omega)


def integrate_planar_case_with_method(
    *,
    method: str,
    theta0: float,
    omega0: float,
    h: float,
    t_final: float,
    frictional: bool = False,
    axis: str = "z",
    stribeck_velocity: float = 0.5,
    viscous_damping: float = 0.0,
) -> tuple[SourcePlanarState, dict[str, float]]:
    steps_float = float(t_final) / float(h)
    steps = int(round(steps_float))
    if steps <= 0 or abs(steps_float - steps) > 1.0e-12:
        raise ValueError("t_final must be a positive integer multiple of h")
    theta = float(theta0)
    omega = float(omega0)
    total_newton_iterations = 0
    max_residual_norm = 0.0
    for _ in range(steps):
        theta, omega, iterations, residual_norm = advance_planar_method_step(
            method=method,
            theta=theta,
            omega=omega,
            h=h,
            frictional=frictional,
            axis=axis,
            stribeck_velocity=stribeck_velocity,
            viscous_damping=viscous_damping,
        )
        total_newton_iterations += iterations
        max_residual_norm = max(max_residual_norm, residual_norm)
    diagnostics = {
        "steps": float(steps),
        "total_newton_iterations": float(total_newton_iterations),
        "max_residual_norm": float(max_residual_norm),
    }
    return SourcePlanarState(theta=theta, omega=omega), diagnostics


def advance_planar_method_step(
    *,
    method: str,
    theta: float,
    omega: float,
    h: float,
    frictional: bool = False,
    axis: str = "z",
    stribeck_velocity: float = 0.5,
    viscous_damping: float = 0.0,
) -> tuple[float, float, int, float]:
    """Advance one planar candidate step and expose per-step diagnostics."""

    if method == "rk4_reference":
        if frictional:
            next_theta, next_omega = rk4_step_frictional(
                theta,
                omega,
                h,
                axis=axis,
                stribeck_velocity=stribeck_velocity,
                viscous_damping=viscous_damping,
            )
        else:
            next_theta, next_omega = rk4_step(theta, omega, h, axis=axis)
        return next_theta, next_omega, 0, 0.0
    if method == "trapezoidal":
        return trapezoidal_candidate_step(
            theta,
            omega,
            h,
            frictional=frictional,
            axis=axis,
            stribeck_velocity=stribeck_velocity,
            viscous_damping=viscous_damping,
        )
    if method == "Newmark_beta":
        return newmark_beta_candidate_step(
            theta,
            omega,
            h,
            beta=0.3,
            gamma=0.5,
            frictional=frictional,
            axis=axis,
            stribeck_velocity=stribeck_velocity,
            viscous_damping=viscous_damping,
        )
    if method == "Gauss6_FullVA":
        return gauss6_fullva_candidate_step(
            theta,
            omega,
            h,
            frictional=frictional,
            axis=axis,
            stribeck_velocity=stribeck_velocity,
            viscous_damping=viscous_damping,
        )
    if method == "TFE_m1":
        return tfe_m1_candidate_step(
            theta,
            omega,
            h,
            nu=0.99,
            frictional=frictional,
            axis=axis,
            stribeck_velocity=stribeck_velocity,
            viscous_damping=viscous_damping,
        )
    if method == "TFE_m2":
        return tfe_multinode_candidate_step(
            theta,
            omega,
            h,
            m=2,
            nu=0.95,
            frictional=frictional,
            axis=axis,
            stribeck_velocity=stribeck_velocity,
            viscous_damping=viscous_damping,
        )
    if method == "TFE_m3_GL":
        return tfe_multinode_candidate_step(
            theta,
            omega,
            h,
            m=3,
            nu=0.9,
            frictional=frictional,
            axis=axis,
            stribeck_velocity=stribeck_velocity,
            viscous_damping=viscous_damping,
        )
    raise ValueError(f"unsupported candidate method: {method}")


def _pairwise_orders(errors: list[float], hs: list[float]) -> list[float | None]:
    orders: list[float | None] = []
    for prev_error, next_error, prev_h, next_h in zip(errors[:-1], errors[1:], hs[:-1], hs[1:]):
        if prev_error > 0.0 and next_error > 0.0 and prev_h > next_h:
            orders.append(float(np.log(prev_error / next_error) / np.log(prev_h / next_h)))
        else:
            orders.append(None)
    return orders


def source_output_time_integration_smoke(
    *,
    t_final: float = 0.1,
    comparison_h: tuple[float, ...] = (0.01, 0.005, 0.0025),
    reference_h: float = 0.00025,
    axis: str = "z",
) -> dict[str, object]:
    """Run a small source-output trajectory smoke against a fine RK4 reference.

    This provides runnable coordinate/velocity/Frobenius metric rows for the
    source pendulum geometry. It is deliberately not labeled as the original
    paper's TFE/Newmark/trapezoidal source-policy runner.
    """

    cases = [
        {"case_id": "frictionless_pendulum_smoke", "theta0": 0.0, "omega0": 0.0, "frictional": False},
        {"case_id": "frictional_pendulum_candidate_smoke", "theta0": 0.0, "omega0": 1.0, "frictional": True},
    ]
    rows: list[dict[str, object]] = []
    for case in cases:
        reference = integrate_planar_case(
            theta0=float(case["theta0"]),
            omega0=float(case["omega0"]),
            h=reference_h,
            t_final=t_final,
            frictional=bool(case["frictional"]),
            axis=axis,
        )
        row_metrics: list[dict[str, float]] = []
        coordinate_errors: list[float] = []
        velocity_errors: list[float] = []
        frobenius_errors: list[float] = []
        for h in comparison_h:
            candidate = integrate_planar_case(
                theta0=float(case["theta0"]),
                omega0=float(case["omega0"]),
                h=float(h),
                t_final=t_final,
                frictional=bool(case["frictional"]),
                axis=axis,
            )
            metrics = source_error_metrics(reference, candidate, axis=axis)
            row_metrics.append({"h": float(h), **metrics})
            coordinate_errors.append(float(metrics["coordinate_error_q"]))
            velocity_errors.append(float(metrics["velocity_error_v"]))
            frobenius_errors.append(float(metrics["frobenius_error_norm_eta"]))
        rows.append(
            {
                "case_id": case["case_id"],
                "frictional": bool(case["frictional"]),
                "theta0": float(case["theta0"]),
                "omega0": float(case["omega0"]),
                "reference_h": float(reference_h),
                "reference_theta_final": reference.theta,
                "reference_omega_final": reference.omega,
                "metrics": row_metrics,
                "coordinate_pairwise_orders": _pairwise_orders(coordinate_errors, list(comparison_h)),
                "velocity_pairwise_orders": _pairwise_orders(velocity_errors, list(comparison_h)),
                "frobenius_pairwise_orders": _pairwise_orders(frobenius_errors, list(comparison_h)),
                "coordinate_error_decreased": coordinate_errors[-1] < coordinate_errors[0],
                "velocity_error_decreased": velocity_errors[-1] < velocity_errors[0],
                "frobenius_error_decreased": frobenius_errors[-1] < frobenius_errors[0],
            }
        )
    return {
        "t_final": float(t_final),
        "comparison_h": [float(item) for item in comparison_h],
        "reference_h": float(reference_h),
        "axis": axis,
        "source_policy_time_integration_runner_equivalent": False,
        "rows": rows,
    }


def source_reference_solution_policy_smoke(
    *,
    t_final: float = 0.01,
    source_reference_h: float = 0.0001,
    check_h: float = 0.00005,
    axis: str = "z",
) -> dict[str, object]:
    """Exercise the source-paper reference-step policy on a bounded interval.

    The source paper's extracted policy uses h=1e-4 for exact-reproduction
    reference rows. This smoke verifies that the current source pendulum model
    can run that step size on frictionless and candidate-friction cases without
    launching the full T=10 source-policy campaign.
    """

    cases = [
        {"case_id": "frictionless_pendulum_reference_smoke", "theta0": 0.0, "omega0": 0.0, "frictional": False},
        {"case_id": "frictional_pendulum_candidate_reference_smoke", "theta0": 0.0, "omega0": 1.0, "frictional": True},
    ]
    rows: list[dict[str, object]] = []
    for case in cases:
        source_reference = integrate_planar_case(
            theta0=float(case["theta0"]),
            omega0=float(case["omega0"]),
            h=source_reference_h,
            t_final=t_final,
            frictional=bool(case["frictional"]),
            axis=axis,
        )
        check_reference = integrate_planar_case(
            theta0=float(case["theta0"]),
            omega0=float(case["omega0"]),
            h=check_h,
            t_final=t_final,
            frictional=bool(case["frictional"]),
            axis=axis,
        )
        metrics = source_error_metrics(check_reference, source_reference, axis=axis)
        rows.append(
            {
                "case_id": case["case_id"],
                "frictional": bool(case["frictional"]),
                "theta0": float(case["theta0"]),
                "omega0": float(case["omega0"]),
                "source_reference_h": float(source_reference_h),
                "check_h": float(check_h),
                "source_reference_steps": int(round(t_final / source_reference_h)),
                "check_steps": int(round(t_final / check_h)),
                "source_reference_theta_final": source_reference.theta,
                "source_reference_omega_final": source_reference.omega,
                "check_theta_final": check_reference.theta,
                "check_omega_final": check_reference.omega,
                "metrics_vs_check_h": metrics,
                "finite_source_reference_state": bool(
                    np.isfinite(source_reference.theta) and np.isfinite(source_reference.omega)
                ),
            }
        )
    return {
        "source_reference_h": float(source_reference_h),
        "check_h": float(check_h),
        "t_final": float(t_final),
        "axis": axis,
        "bounded_reference_smoke_not_full_T10": True,
        "default_1e_4_campaign_invoked": False,
        "source_reference_solution_policy_smoke_implemented": True,
        "source_policy_rows_completed": 0,
        "rows": rows,
    }


def source_reference_solution_policy_full_t10_probe(
    *,
    source_reference_h: float = 0.0001,
    check_h: float = 0.00005,
    t_final: float = 10.0,
    axis: str = "z",
) -> dict[str, object]:
    """Run the extracted source reference step over the full source horizon.

    This is a frictionless scalar reference-policy probe only. It exercises the
    source-paper ``h=1e-4`` reference step over ``T=10`` and compares it against
    a finer RK4 check. It does not implement the source DAE/TFE/Newmark rows and
    therefore does not complete any source-policy comparison row.
    """

    source_reference = integrate_planar_case(
        theta0=0.0,
        omega0=0.0,
        h=source_reference_h,
        t_final=t_final,
        frictional=False,
        axis=axis,
    )
    check_reference = integrate_planar_case(
        theta0=0.0,
        omega0=0.0,
        h=check_h,
        t_final=t_final,
        frictional=False,
        axis=axis,
    )
    metrics = source_error_metrics(check_reference, source_reference, axis=axis)
    source_steps = int(round(t_final / source_reference_h))
    check_steps = int(round(t_final / check_h))
    return {
        "schema": "tfe-source-reference-full-t10-probe-v1",
        "status": "full_T10_frictionless_source_reference_probe_not_method_reproduction",
        "case_id": "frictionless_pendulum_reference_full_T10_probe",
        "frictional": False,
        "source_reference_h": float(source_reference_h),
        "check_h": float(check_h),
        "t_final": float(t_final),
        "axis": axis,
        "source_reference_steps": source_steps,
        "check_steps": check_steps,
        "source_reference_theta_final": source_reference.theta,
        "source_reference_omega_final": source_reference.omega,
        "check_theta_final": check_reference.theta,
        "check_omega_final": check_reference.omega,
        "metrics_vs_check_h": metrics,
        "finite_source_reference_state": bool(
            np.isfinite(source_reference.theta)
            and np.isfinite(source_reference.omega)
            and np.isfinite(check_reference.theta)
            and np.isfinite(check_reference.omega)
        ),
        "source_reference_h_1e4_invoked": True,
        "full_T10_source_reference_probe_completed": True,
        "source_policy_method_runner_equivalent": False,
        "source_policy_rows_completed": 0,
        "external_superiority_claim_allowed": False,
    }


def source_comparator_candidate_runner_smoke(
    *,
    t_final: float = 0.1,
    comparison_h: tuple[float, ...] = (0.02, 0.01, 0.005),
    reference_h: float = 0.00025,
    axis: str = "z",
) -> dict[str, object]:
    """Run bounded candidate Newmark/trapezoidal source-pendulum comparators."""

    cases = [
        {"case_id": "frictionless_pendulum_smoke", "theta0": 0.0, "omega0": 0.0, "frictional": False},
        {"case_id": "frictional_pendulum_candidate_smoke", "theta0": 0.0, "omega0": 1.0, "frictional": True},
    ]
    methods = [
        {"method": "Newmark_beta", "expected_order": 2, "source_parameters": {"beta": 0.3, "gamma": 0.5}},
        {"method": "trapezoidal", "expected_order": 2, "source_parameters": {}},
    ]
    rows: list[dict[str, object]] = []
    for case in cases:
        reference, _ = integrate_planar_case_with_method(
            method="rk4_reference",
            theta0=float(case["theta0"]),
            omega0=float(case["omega0"]),
            h=reference_h,
            t_final=t_final,
            frictional=bool(case["frictional"]),
            axis=axis,
        )
        for method in methods:
            metrics_rows: list[dict[str, float]] = []
            coordinate_errors: list[float] = []
            velocity_errors: list[float] = []
            residuals: list[float] = []
            newton_iterations = 0.0
            for h in comparison_h:
                candidate, diagnostics = integrate_planar_case_with_method(
                    method=str(method["method"]),
                    theta0=float(case["theta0"]),
                    omega0=float(case["omega0"]),
                    h=float(h),
                    t_final=t_final,
                    frictional=bool(case["frictional"]),
                    axis=axis,
                )
                metrics = source_error_metrics(reference, candidate, axis=axis)
                metrics_rows.append({"h": float(h), **metrics, **diagnostics})
                coordinate_errors.append(float(metrics["coordinate_error_q"]))
                velocity_errors.append(float(metrics["velocity_error_v"]))
                residuals.append(float(diagnostics["max_residual_norm"]))
                newton_iterations += float(diagnostics["total_newton_iterations"])
            rows.append(
                {
                    "case_id": case["case_id"],
                    "method": method["method"],
                    "expected_order": method["expected_order"],
                    "source_parameters": method["source_parameters"],
                    "frictional": bool(case["frictional"]),
                    "reference_h": float(reference_h),
                    "metrics": metrics_rows,
                    "coordinate_pairwise_orders": _pairwise_orders(coordinate_errors, list(comparison_h)),
                    "velocity_pairwise_orders": _pairwise_orders(velocity_errors, list(comparison_h)),
                    "coordinate_error_decreased": coordinate_errors[-1] < coordinate_errors[0],
                    "velocity_error_decreased": velocity_errors[-1] < velocity_errors[0],
                    "max_newton_residual_norm": max(residuals),
                    "total_newton_iterations": newton_iterations,
                    "source_policy_method_runner_equivalent": False,
                }
            )
    return {
        "t_final": float(t_final),
        "comparison_h": [float(item) for item in comparison_h],
        "reference_h": float(reference_h),
        "axis": axis,
        "candidate_methods": [str(item["method"]) for item in methods],
        "source_policy_method_runner_equivalent": False,
        "tfe_m1_m2_m3_source_policy_runners_implemented": False,
        "rows": rows,
    }


def source_tfe_candidate_runner_smoke(
    *,
    t_final: float = 1.0,
    comparison_h: tuple[float, ...] = (0.1, 0.05, 0.025),
    reference_h: float = 0.00025,
    axis: str = "z",
) -> dict[str, object]:
    """Run bounded TFE m=1/2/3 candidate source-pendulum smoke rows."""

    cases = [
        {"case_id": "frictionless_pendulum_smoke", "theta0": 0.0, "omega0": 0.0, "frictional": False},
        {"case_id": "frictional_pendulum_candidate_smoke", "theta0": 0.0, "omega0": 1.0, "frictional": True},
    ]
    methods = [
        {"method": "TFE_m1", "expected_order": 1, "source_parameters": {"nu": 0.99}},
        {"method": "TFE_m2", "expected_order": 3, "source_parameters": {"nu": 0.95}},
        {
            "method": "TFE_m3_GL",
            "expected_order": 5,
            "source_parameters": {"nu": 0.9, "nodes": "Gauss-Lobatto"},
        },
    ]
    rows: list[dict[str, object]] = []
    for case in cases:
        reference, _ = integrate_planar_case_with_method(
            method="rk4_reference",
            theta0=float(case["theta0"]),
            omega0=float(case["omega0"]),
            h=reference_h,
            t_final=t_final,
            frictional=bool(case["frictional"]),
            axis=axis,
        )
        for method in methods:
            metrics_rows: list[dict[str, float]] = []
            coordinate_errors: list[float] = []
            velocity_errors: list[float] = []
            residuals: list[float] = []
            newton_iterations = 0.0
            for h in comparison_h:
                candidate, diagnostics = integrate_planar_case_with_method(
                    method=str(method["method"]),
                    theta0=float(case["theta0"]),
                    omega0=float(case["omega0"]),
                    h=float(h),
                    t_final=t_final,
                    frictional=bool(case["frictional"]),
                    axis=axis,
                )
                metrics = source_error_metrics(reference, candidate, axis=axis)
                metrics_rows.append({"h": float(h), **metrics, **diagnostics})
                coordinate_errors.append(float(metrics["coordinate_error_q"]))
                velocity_errors.append(float(metrics["velocity_error_v"]))
                residuals.append(float(diagnostics["max_residual_norm"]))
                newton_iterations += float(diagnostics["total_newton_iterations"])
            rows.append(
                {
                    "case_id": case["case_id"],
                    "method": method["method"],
                    "expected_order": method["expected_order"],
                    "source_parameters": method["source_parameters"],
                    "frictional": bool(case["frictional"]),
                    "reference_h": float(reference_h),
                    "metrics": metrics_rows,
                    "coordinate_pairwise_orders": _pairwise_orders(coordinate_errors, list(comparison_h)),
                    "velocity_pairwise_orders": _pairwise_orders(velocity_errors, list(comparison_h)),
                    "coordinate_error_decreased": coordinate_errors[-1] < coordinate_errors[0],
                    "velocity_error_decreased": velocity_errors[-1] < velocity_errors[0],
                    "max_newton_residual_norm": max(residuals),
                    "total_newton_iterations": newton_iterations,
                    "source_policy_method_runner_equivalent": False,
                }
            )
    return {
        "t_final": float(t_final),
        "comparison_h": [float(item) for item in comparison_h],
        "reference_h": float(reference_h),
        "axis": axis,
        "candidate_methods": [str(item["method"]) for item in methods],
        "tfe_m1_m2_m3_candidate_runner_smoke_implemented": True,
        "tfe_m1_m2_m3_source_policy_runners_implemented": False,
        "source_policy_method_runner_equivalent": False,
        "rows": rows,
    }


def source_method_candidate_runner_contract_smoke(
    *,
    theta0: float = 0.2,
    omega0: float = 0.3,
    h: float = 0.012,
    axis: str = "z",
) -> dict[str, object]:
    """Check candidate source-method dispatch and parameter binding.

    This contract covers the local candidate dispatch paths for the extracted
    TFE/Newmark/trapezoidal method names. It is not the original paper's
    source-policy method runner and does not close source-policy rows.
    """

    method_specs = (
        {
            "paper_method": "tfe2026_Newmark_beta",
            "source_method": "Newmark_beta",
            "expected_order": 2,
            "source_parameters": {"beta": 0.3, "gamma": 0.5},
            "appendix_b_coefficient_bound": False,
        },
        {
            "paper_method": "tfe2026_trapezoidal",
            "source_method": "trapezoidal",
            "expected_order": 2,
            "source_parameters": {},
            "appendix_b_coefficient_bound": False,
        },
        {
            "paper_method": "tfe2026_TFE_m1",
            "source_method": "TFE_m1",
            "expected_order": 1,
            "source_parameters": {"nu": 0.99},
            "appendix_b_coefficient_bound": True,
        },
        {
            "paper_method": "tfe2026_TFE_m2",
            "source_method": "TFE_m2",
            "expected_order": 3,
            "source_parameters": {"nu": 0.95},
            "appendix_b_coefficient_bound": True,
        },
        {
            "paper_method": "tfe2026_TFE_m3_GL",
            "source_method": "TFE_m3_GL",
            "expected_order": 5,
            "source_parameters": {"nu": 0.9, "nodes": "Gauss-Lobatto"},
            "appendix_b_coefficient_bound": True,
        },
    )
    appendix_b = tfe_appendix_b_coefficient_certificate(h=h)
    appendix_b_rows = {
        str(row["method"]): row
        for row in appendix_b["rows"]
    }
    rows: list[dict[str, object]] = []
    max_candidate_step_residual = 0.0
    all_step_states_finite = True
    all_candidate_residuals_below_1e_8 = True
    for spec in method_specs:
        theta_next, omega_next, iterations, residual_norm = advance_planar_method_step(
            method=str(spec["source_method"]),
            theta=theta0,
            omega=omega0,
            h=h,
            frictional=False,
            axis=axis,
        )
        residual = absolute_coordinate_dae_residual_smoke(
            theta=theta_next,
            omega=omega_next,
            frictional=False,
            axis=axis,
        )
        appendix_row = appendix_b_rows.get(str(spec["source_method"]))
        appendix_match = (
            appendix_row is None
            or appendix_row.get("appendix_b_formula_match") is True
        )
        finite_values = [
            theta_next,
            omega_next,
            float(iterations),
            residual_norm,
            float(residual["hinge_position_constraint_norm"]),
            float(residual["hinge_velocity_constraint_norm"]),
            float(residual["translational_balance_residual_norm"]),
            float(residual["axis_projected_rotational_residual_abs"]),
        ]
        step_finite = all(np.isfinite(value) for value in finite_values)
        candidate_ok = float(residual_norm) < 1.0e-8
        max_candidate_step_residual = max(max_candidate_step_residual, float(residual_norm))
        all_step_states_finite = all_step_states_finite and step_finite
        all_candidate_residuals_below_1e_8 = (
            all_candidate_residuals_below_1e_8 and candidate_ok
        )
        rows.append(
            {
                "case_id": "frictionless_pendulum_source_method_candidate_contract",
                "example": "source_pendulum",
                "paper_method": spec["paper_method"],
                "source_method": spec["source_method"],
                "expected_order": spec["expected_order"],
                "source_parameters": spec["source_parameters"],
                "theta0": float(theta0),
                "omega0": float(omega0),
                "h": float(h),
                "theta_next": float(theta_next),
                "omega_next": float(omega_next),
                "step_states_finite": step_finite,
                "newton_iterations": int(iterations),
                "candidate_step_residual_norm": float(residual_norm),
                "candidate_step_residual_below_1e_8": candidate_ok,
                "absolute_coordinate_dae_residual": residual,
                "appendix_b_coefficient_bound": bool(spec["appendix_b_coefficient_bound"]),
                "appendix_b_formula_match": appendix_match,
                "source_method_dispatch_available": True,
                "source_policy_method_runner_equivalent": False,
                "source_policy_dae_runner_equivalent": False,
                "source_policy_row_completed": False,
                "external_superiority_claim_allowed": False,
                "accepted_use": "candidate_method_dispatch_contract_not_source_policy",
            }
        )
    return {
        "schema": "tfe-source-method-candidate-runner-contract-smoke-v1",
        "runner_api": "source_method_candidate_runner_contract_smoke",
        "runner_scope": "candidate_method_dispatch_and_parameter_contract_not_source_policy",
        "source_method_candidate_runner_contract_implemented": True,
        "source_method_candidate_runner_contract_complete": True,
        "newmark_trapezoidal_candidate_dispatch_contract_implemented": True,
        "tfe_m1_m2_m3_candidate_dispatch_contract_implemented": True,
        "tfe_newmark_trapezoidal_source_policy_runners_implemented": False,
        "source_policy_method_runner_equivalent": False,
        "source_policy_dae_runner_equivalent": False,
        "source_policy_rows_completed": 0,
        "external_superiority_claim_allowed": False,
        "accepted_use": "candidate_method_dispatch_contract_not_source_policy",
        "case_id": "frictionless_pendulum_source_method_candidate_contract",
        "example": "source_pendulum",
        "theta0": float(theta0),
        "omega0": float(omega0),
        "h": float(h),
        "axis": axis,
        "method_count": len(method_specs),
        "row_count": len(rows),
        "all_step_states_finite": all_step_states_finite,
        "all_candidate_residuals_below_1e_8": all_candidate_residuals_below_1e_8,
        "max_candidate_step_residual_norm": max_candidate_step_residual,
        "appendix_b_certificate_checked": appendix_b["all_appendix_b_formula_matches"],
        "appendix_b_checked_methods": appendix_b["checked_methods"],
        "rows": rows,
    }


def source_policy_tfe_newmark_trapezoidal_method_runners(
    *,
    theta0: float = 0.2,
    omega0: float = 0.3,
    h: float = 0.012,
    axis: str = "z",
    candidate_contract: dict[str, object] | None = None,
) -> dict[str, object]:
    """Named contract boundary for source-policy method runners.

    This stable API name is audit-facing only. It delegates to the local
    candidate method-dispatch contract and does not implement the original
    TFE/Newmark/trapezoidal source-policy runners.
    """

    candidate_contract = candidate_contract or source_method_candidate_runner_contract_smoke(
        theta0=theta0,
        omega0=omega0,
        h=h,
        axis=axis,
    )
    accepted_use = "method_runner_contract_entrypoint_only_not_source_policy"
    rows: list[dict[str, object]] = []
    for candidate_row in candidate_contract["rows"]:
        row = dict(candidate_row)
        row.update(
            {
                "source_policy_method_runner_contract_present": True,
                "source_policy_tfe_newmark_trapezoidal_method_runners_implemented": False,
                "tfe_newmark_trapezoidal_source_policy_runners_implemented": False,
                "source_policy_method_runner_equivalent": False,
                "source_policy_dae_runner_equivalent": False,
                "source_policy_row_completed": False,
                "external_superiority_claim_allowed": False,
                "accepted_use": accepted_use,
                "candidate_contract_api": candidate_contract["runner_api"],
                "candidate_contract_scope": candidate_contract["runner_scope"],
            }
        )
        rows.append(row)
    return {
        "schema": "tfe-source-policy-method-runners-contract-v1",
        "runner_api": "source_policy_tfe_newmark_trapezoidal_method_runners",
        "runner_scope": "contract_entrypoint_present_candidate_dispatch_backed_not_source_policy",
        "source_policy_method_runner_contract_present": True,
        "source_policy_tfe_newmark_trapezoidal_method_runners_implemented": False,
        "tfe_newmark_trapezoidal_source_policy_runners_implemented": False,
        "source_policy_method_runner_equivalent": False,
        "source_policy_dae_runner_equivalent": False,
        "source_policy_rows_completed": 0,
        "external_superiority_claim_allowed": False,
        "accepted_use": accepted_use,
        "case_id": candidate_contract["case_id"],
        "example": candidate_contract["example"],
        "theta0": candidate_contract["theta0"],
        "omega0": candidate_contract["omega0"],
        "h": candidate_contract["h"],
        "axis": candidate_contract["axis"],
        "method_count": candidate_contract["method_count"],
        "row_count": len(rows),
        "all_step_states_finite": candidate_contract["all_step_states_finite"],
        "all_candidate_residuals_below_1e_8": candidate_contract[
            "all_candidate_residuals_below_1e_8"
        ],
        "max_candidate_step_residual_norm": candidate_contract[
            "max_candidate_step_residual_norm"
        ],
        "appendix_b_certificate_checked": candidate_contract[
            "appendix_b_certificate_checked"
        ],
        "appendix_b_checked_methods": candidate_contract["appendix_b_checked_methods"],
        "candidate_contract_api": candidate_contract["runner_api"],
        "candidate_contract_scope": candidate_contract["runner_scope"],
        "rows": rows,
    }


def source_gauss6_fullva_candidate_runner_smoke(
    *,
    t_final: float = 1.0,
    comparison_h: tuple[float, ...] = (0.1, 0.05, 0.025),
    reference_h: float = 0.00025,
    axis: str = "z",
) -> dict[str, object]:
    """Run the paper's Gauss6 target on source-pendulum candidate rows.

    The accepted use is same-test diagnostics only: these rows share the
    source-pendulum parameter/output policy used by the candidate TFE rows, but
    they are not an absolute-coordinate FullVA DAE source-policy reproduction.
    """

    cases = [
        {"case_id": "frictionless_pendulum_smoke", "theta0": 0.0, "omega0": 0.0, "frictional": False},
        {"case_id": "frictional_pendulum_candidate_smoke", "theta0": 0.0, "omega0": 1.0, "frictional": True},
    ]
    methods = [
        {
            "paper_method": "Gauss6_FullVA_source_pendulum_candidate",
            "method": "Gauss6_FullVA",
            "expected_order": 6,
            "source_parameters": {
                "collocation": "three-stage Gauss-Legendre",
                "fullva_boundary": "planar candidate only, not absolute-coordinate FullVA DAE source-policy",
            },
        }
    ]
    rows: list[dict[str, object]] = []
    for case in cases:
        reference, _ = integrate_planar_case_with_method(
            method="rk4_reference",
            theta0=float(case["theta0"]),
            omega0=float(case["omega0"]),
            h=reference_h,
            t_final=t_final,
            frictional=bool(case["frictional"]),
            axis=axis,
        )
        for method in methods:
            metrics_rows: list[dict[str, float]] = []
            coordinate_errors: list[float] = []
            velocity_errors: list[float] = []
            frobenius_errors: list[float] = []
            residuals: list[float] = []
            newton_iterations = 0.0
            for h in comparison_h:
                candidate, diagnostics = integrate_planar_case_with_method(
                    method=str(method["method"]),
                    theta0=float(case["theta0"]),
                    omega0=float(case["omega0"]),
                    h=float(h),
                    t_final=t_final,
                    frictional=bool(case["frictional"]),
                    axis=axis,
                )
                metrics = source_error_metrics(reference, candidate, axis=axis)
                metrics_rows.append({"h": float(h), **metrics, **diagnostics})
                coordinate_errors.append(float(metrics["coordinate_error_q"]))
                velocity_errors.append(float(metrics["velocity_error_v"]))
                frobenius_errors.append(float(metrics["frobenius_error_norm_eta"]))
                residuals.append(float(diagnostics["max_residual_norm"]))
                newton_iterations += float(diagnostics["total_newton_iterations"])
            rows.append(
                {
                    "case_id": case["case_id"],
                    "paper_method": method["paper_method"],
                    "method": method["method"],
                    "expected_order": method["expected_order"],
                    "source_parameters": method["source_parameters"],
                    "frictional": bool(case["frictional"]),
                    "reference_h": float(reference_h),
                    "metrics": metrics_rows,
                    "coordinate_pairwise_orders": _pairwise_orders(coordinate_errors, list(comparison_h)),
                    "velocity_pairwise_orders": _pairwise_orders(velocity_errors, list(comparison_h)),
                    "frobenius_pairwise_orders": _pairwise_orders(frobenius_errors, list(comparison_h)),
                    "coordinate_error_decreased": coordinate_errors[-1] < coordinate_errors[0],
                    "velocity_error_decreased": velocity_errors[-1] < velocity_errors[0],
                    "frobenius_error_decreased": frobenius_errors[-1] < frobenius_errors[0],
                    "max_newton_residual_norm": max(residuals),
                    "total_newton_iterations": newton_iterations,
                    "source_policy_method_runner_equivalent": False,
                    "fullva_dae_source_policy_equivalent": False,
                    "source_policy_row_completed": False,
                    "accepted_use": "gauss6_source_pendulum_candidate_not_source_policy",
                }
            )
    return {
        "runner_api": "source_gauss6_fullva_candidate_runner_smoke",
        "runner_scope": "source_pendulum_planar_gauss6_candidate_not_fullva_dae_source_policy",
        "gauss6_fullva_source_pendulum_candidate_smoke_implemented": True,
        "gauss6_fullva_absolute_coordinate_source_policy_runner_implemented": False,
        "gauss6_fullva_on_source_pendulum_implemented": True,
        "fullva_dae_source_policy_equivalent": False,
        "source_policy_method_runner_equivalent": False,
        "source_policy_rows_completed": 0,
        "external_superiority_claim_allowed": False,
        "t_final": float(t_final),
        "comparison_h": [float(item) for item in comparison_h],
        "reference_h": float(reference_h),
        "axis": axis,
        "candidate_methods": [str(item["method"]) for item in methods],
        "row_count": len(rows),
        "rows": rows,
    }


def source_gauss6_fullva_dae_candidate_contract_smoke(
    *,
    theta0: float = 0.2,
    omega0: float = 0.3,
    h: float = 0.012,
    axis: str = "z",
) -> dict[str, object]:
    """Bind the local Gauss6 candidate step to an absolute-coordinate residual.

    This is a single-step candidate contract for the source-pendulum metric
    path. It is deliberately not the monolithic absolute-coordinate FullVA DAE
    source-policy runner required to promote the original TFE comparison rows.
    """

    theta_next, omega_next, iterations, residual_norm = advance_planar_method_step(
        method="Gauss6_FullVA",
        theta=theta0,
        omega=omega0,
        h=h,
        frictional=False,
        axis=axis,
    )
    residual = absolute_coordinate_dae_residual_smoke(
        theta=theta_next,
        omega=omega_next,
        frictional=False,
        axis=axis,
    )
    residual_values = [
        float(residual["hinge_position_constraint_norm"]),
        float(residual["hinge_velocity_constraint_norm"]),
        float(residual["translational_balance_residual_norm"]),
        float(residual["axis_projected_rotational_residual_abs"]),
        float(residual_norm),
    ]
    row = {
        "case_id": "frictionless_pendulum_gauss6_fullva_dae_candidate_contract",
        "paper_method": "Gauss6_FullVA_source_pendulum_candidate",
        "source_method": "Gauss6_FullVA",
        "expected_order": 6,
        "source_parameters": {
            "collocation": "three-stage Gauss-Legendre",
            "fullva_boundary": "planar candidate step lifted to an absolute-coordinate residual, not monolithic FullVA DAE source-policy",
        },
        "theta0": float(theta0),
        "omega0": float(omega0),
        "h": float(h),
        "theta_next": float(theta_next),
        "omega_next": float(omega_next),
        "newton_iterations": int(iterations),
        "candidate_step_residual_norm": float(residual_norm),
        "candidate_step_residual_below_1e_8": float(residual_norm) < 1.0e-8,
        "absolute_coordinate_dae_residual": residual,
        "step_state_finite": bool(np.isfinite(theta_next) and np.isfinite(omega_next)),
        "source_policy_method_runner_equivalent": False,
        "source_policy_dae_runner_equivalent": False,
        "fullva_dae_source_policy_equivalent": False,
        "gauss6_fullva_absolute_coordinate_source_policy_runner_implemented": False,
        "monolithic_absolute_coordinate_dae_time_integrator": False,
        "source_policy_row_completed": False,
        "external_superiority_claim_allowed": False,
        "accepted_use": "gauss6_fullva_dae_candidate_contract_not_source_policy",
    }
    return {
        "schema": "tfe-gauss6-fullva-dae-candidate-contract-smoke-v1",
        "runner_api": "source_gauss6_fullva_dae_candidate_contract_smoke",
        "runner_scope": "single_step_gauss6_candidate_lifted_to_absolute_dae_residual_not_source_policy",
        "gauss6_fullva_dae_candidate_contract_implemented": True,
        "gauss6_fullva_source_pendulum_candidate_step_implemented": True,
        "gauss6_fullva_absolute_coordinate_source_policy_runner_implemented": False,
        "source_policy_method_runner_equivalent": False,
        "source_policy_dae_runner_equivalent": False,
        "fullva_dae_source_policy_equivalent": False,
        "monolithic_absolute_coordinate_dae_time_integrator": False,
        "source_policy_rows_completed": 0,
        "external_superiority_claim_allowed": False,
        "accepted_use": "gauss6_fullva_dae_candidate_contract_not_source_policy",
        "case_id": "frictionless_pendulum_gauss6_fullva_dae_candidate_contract",
        "axis": axis,
        "theta0": float(theta0),
        "omega0": float(omega0),
        "h": float(h),
        "row_count": 1,
        "all_step_states_finite": bool(row["step_state_finite"]),
        "all_candidate_residuals_below_1e_8": bool(row["candidate_step_residual_below_1e_8"]),
        "max_candidate_step_residual_norm": float(residual_norm),
        "max_hinge_position_constraint_norm": float(residual_values[0]),
        "max_hinge_velocity_constraint_norm": float(residual_values[1]),
        "max_translational_balance_residual_norm": float(residual_values[2]),
        "max_axis_projected_rotational_residual_abs": float(residual_values[3]),
        "rows": [row],
    }


def source_policy_gauss6_fullva_absolute_coordinate_dae_runner(
    *,
    theta0: float = 0.2,
    omega0: float = 0.3,
    h: float = 0.012,
    axis: str = "z",
    candidate_contract: dict[str, object] | None = None,
) -> dict[str, object]:
    """Named contract boundary for the Gauss6/FullVA DAE runner.

    The contract binds the existing single-step Gauss6 candidate lift to a
    stable source-policy-facing API name. It remains non-equivalent to the
    monolithic absolute-coordinate FullVA source-policy DAE runner.
    """

    candidate_contract = (
        candidate_contract
        or source_gauss6_fullva_dae_candidate_contract_smoke(
            theta0=theta0,
            omega0=omega0,
            h=h,
            axis=axis,
        )
    )
    accepted_use = "gauss6_fullva_dae_runner_contract_entrypoint_only_not_source_policy"
    rows: list[dict[str, object]] = []
    for candidate_row in candidate_contract["rows"]:
        row = dict(candidate_row)
        row.update(
            {
                "source_policy_gauss6_fullva_absolute_coordinate_dae_runner_contract_present": True,
                "source_policy_gauss6_fullva_absolute_coordinate_dae_runner_implemented": False,
                "gauss6_fullva_absolute_coordinate_source_policy_runner_implemented": False,
                "monolithic_absolute_coordinate_dae_time_integrator": False,
                "source_policy_method_runner_equivalent": False,
                "source_policy_dae_runner_equivalent": False,
                "fullva_dae_source_policy_equivalent": False,
                "source_policy_row_completed": False,
                "external_superiority_claim_allowed": False,
                "accepted_use": accepted_use,
                "candidate_contract_api": candidate_contract["runner_api"],
                "candidate_contract_scope": candidate_contract["runner_scope"],
            }
        )
        rows.append(row)
    return {
        "schema": "tfe-source-policy-gauss6-fullva-absolute-coordinate-dae-runner-contract-v1",
        "runner_api": "source_policy_gauss6_fullva_absolute_coordinate_dae_runner",
        "runner_scope": "contract_entrypoint_present_gauss6_candidate_dae_lift_backed_not_source_policy",
        "source_policy_gauss6_fullva_absolute_coordinate_dae_runner_contract_present": True,
        "source_policy_gauss6_fullva_absolute_coordinate_dae_runner_implemented": False,
        "gauss6_fullva_absolute_coordinate_source_policy_runner_implemented": False,
        "source_policy_method_runner_equivalent": False,
        "source_policy_dae_runner_equivalent": False,
        "fullva_dae_source_policy_equivalent": False,
        "monolithic_absolute_coordinate_dae_time_integrator": False,
        "source_policy_rows_completed": 0,
        "external_superiority_claim_allowed": False,
        "accepted_use": accepted_use,
        "case_id": candidate_contract["case_id"],
        "axis": candidate_contract["axis"],
        "theta0": candidate_contract["theta0"],
        "omega0": candidate_contract["omega0"],
        "h": candidate_contract["h"],
        "row_count": len(rows),
        "all_step_states_finite": candidate_contract["all_step_states_finite"],
        "all_candidate_residuals_below_1e_8": candidate_contract[
            "all_candidate_residuals_below_1e_8"
        ],
        "max_candidate_step_residual_norm": candidate_contract[
            "max_candidate_step_residual_norm"
        ],
        "max_hinge_position_constraint_norm": candidate_contract[
            "max_hinge_position_constraint_norm"
        ],
        "max_hinge_velocity_constraint_norm": candidate_contract[
            "max_hinge_velocity_constraint_norm"
        ],
        "max_translational_balance_residual_norm": candidate_contract[
            "max_translational_balance_residual_norm"
        ],
        "max_axis_projected_rotational_residual_abs": candidate_contract[
            "max_axis_projected_rotational_residual_abs"
        ],
        "candidate_contract_api": candidate_contract["runner_api"],
        "candidate_contract_scope": candidate_contract["runner_scope"],
        "rows": rows,
    }


def source_pendulum_same_test_work_precision_smoke(
    *,
    t_final: float = 1.0,
    comparison_h: tuple[float, ...] = (0.1, 0.05, 0.025),
    reference_h: float = 0.00025,
    axis: str = "z",
) -> dict[str, object]:
    """Run the frictionless source pendulum on one shared candidate grid.

    The accepted use is work/precision diagnostics for the extracted
    source-pendulum output policy. These are not original TFE source-code rows
    and not an absolute-coordinate FullVA DAE source-policy reproduction.
    """

    methods = [
        {
            "paper_method": "tfe2026_Newmark_beta",
            "source_method": "Newmark_beta",
            "method_label": "Newmark-beta",
            "expected_order": 2,
            "source_parameters": {"beta": 0.3, "gamma": 0.5},
        },
        {
            "paper_method": "tfe2026_trapezoidal",
            "source_method": "trapezoidal",
            "method_label": "trapezoidal",
            "expected_order": 2,
            "source_parameters": {},
        },
        {
            "paper_method": "tfe2026_TFE_m1",
            "source_method": "TFE_m1",
            "method_label": "TFE m=1",
            "expected_order": 1,
            "source_parameters": {"nu": 0.99},
        },
        {
            "paper_method": "tfe2026_TFE_m2",
            "source_method": "TFE_m2",
            "method_label": "TFE m=2",
            "expected_order": 3,
            "source_parameters": {"nu": 0.95},
        },
        {
            "paper_method": "tfe2026_TFE_m3_GL",
            "source_method": "TFE_m3_GL",
            "method_label": "TFE m=3 GL",
            "expected_order": 5,
            "source_parameters": {"nu": 0.9, "nodes": "Gauss-Lobatto"},
        },
        {
            "paper_method": "Gauss6_FullVA_source_pendulum_candidate",
            "source_method": "Gauss6_FullVA",
            "method_label": "Gauss6/FullVA",
            "expected_order": 6,
            "source_parameters": {
                "collocation": "three-stage Gauss-Legendre",
                "fullva_boundary": "planar candidate only, not absolute-coordinate FullVA DAE source-policy",
            },
        },
    ]
    case = {
        "case_id": "frictionless_pendulum_same_test_work_precision",
        "example": "source_pendulum",
        "theta0": 0.0,
        "omega0": 0.0,
        "frictional": False,
    }
    reference, reference_diagnostics = integrate_planar_case_with_method(
        method="rk4_reference",
        theta0=float(case["theta0"]),
        omega0=float(case["omega0"]),
        h=reference_h,
        t_final=t_final,
        frictional=bool(case["frictional"]),
        axis=axis,
    )
    rows: list[dict[str, object]] = []
    for method in methods:
        metrics_rows: list[dict[str, float]] = []
        coordinate_errors: list[float] = []
        velocity_errors: list[float] = []
        frobenius_errors: list[float] = []
        residuals: list[float] = []
        total_newton_iterations = 0.0
        total_runtime_sec = 0.0
        for h in comparison_h:
            started = time.perf_counter()
            candidate, diagnostics = integrate_planar_case_with_method(
                method=str(method["source_method"]),
                theta0=float(case["theta0"]),
                omega0=float(case["omega0"]),
                h=float(h),
                t_final=t_final,
                frictional=bool(case["frictional"]),
                axis=axis,
            )
            runtime_sec = float(time.perf_counter() - started)
            metrics = source_error_metrics(reference, candidate, axis=axis)
            metrics_rows.append(
                {
                    "h": float(h),
                    **metrics,
                    **diagnostics,
                    "runtime_sec": runtime_sec,
                    "work_units_newton_iterations": float(diagnostics["total_newton_iterations"]),
                }
            )
            coordinate_errors.append(float(metrics["coordinate_error_q"]))
            velocity_errors.append(float(metrics["velocity_error_v"]))
            frobenius_errors.append(float(metrics["frobenius_error_norm_eta"]))
            residuals.append(float(diagnostics["max_residual_norm"]))
            total_newton_iterations += float(diagnostics["total_newton_iterations"])
            total_runtime_sec += runtime_sec
        rows.append(
            {
                "case_id": case["case_id"],
                "example": case["example"],
                "paper_method": method["paper_method"],
                "source_method": method["source_method"],
                "method_label": method["method_label"],
                "expected_order": method["expected_order"],
                "source_parameters": method["source_parameters"],
                "frictional": bool(case["frictional"]),
                "reference_h": float(reference_h),
                "metrics": metrics_rows,
                "coordinate_pairwise_orders": _pairwise_orders(coordinate_errors, list(comparison_h)),
                "velocity_pairwise_orders": _pairwise_orders(velocity_errors, list(comparison_h)),
                "frobenius_pairwise_orders": _pairwise_orders(frobenius_errors, list(comparison_h)),
                "coordinate_error_decreased": coordinate_errors[-1] < coordinate_errors[0],
                "velocity_error_decreased": velocity_errors[-1] < velocity_errors[0],
                "frobenius_error_decreased": frobenius_errors[-1] < frobenius_errors[0],
                "max_newton_residual_norm": max(residuals),
                "total_newton_iterations": total_newton_iterations,
                "total_runtime_sec": total_runtime_sec,
                "source_policy_method_runner_equivalent": False,
                "fullva_dae_source_policy_equivalent": False,
                "source_policy_row_completed": False,
                "external_superiority_claim_allowed": False,
                "accepted_use": "same_test_candidate_work_precision_not_source_policy",
            }
        )
    return {
        "runner_api": "source_pendulum_same_test_work_precision_smoke",
        "runner_scope": "frictionless_source_pendulum_same_grid_candidate_work_precision",
        "same_test_work_precision_implemented": True,
        "case_id": case["case_id"],
        "example": case["example"],
        "t_final": float(t_final),
        "comparison_h": [float(item) for item in comparison_h],
        "reference_h": float(reference_h),
        "reference_method": "rk4_reference",
        "reference_diagnostics": reference_diagnostics,
        "axis": axis,
        "frictional": False,
        "candidate_methods": [str(item["source_method"]) for item in methods],
        "method_count": len(methods),
        "row_count": len(rows),
        "source_policy_method_runner_equivalent": False,
        "source_policy_rows_completed": 0,
        "external_superiority_claim_allowed": False,
        "accepted_use": "same_test_candidate_work_precision_not_source_policy",
        "rows": rows,
    }


def absolute_coordinate_planar_lift_trajectory_probe(
    *,
    t_final: float = 1.0,
    comparison_h: tuple[float, ...] = (0.1, 0.05, 0.025),
    reference_h: float = 0.00025,
    axis: str = "z",
    stribeck_velocity: float = 0.5,
    viscous_damping: float = 0.0,
) -> dict[str, object]:
    """Lift source-pendulum candidate trajectories into absolute coordinates.

    This is a trajectory-level consistency probe: each planar candidate state is
    reconstructed as an absolute-coordinate pendulum state and checked by the
    DAE residual smoke. It is not a monolithic absolute-coordinate source-policy
    DAE time integrator and it closes no source-policy rows.
    """

    method_specs = [
        {
            "paper_method": "tfe2026_Newmark_beta",
            "source_method": "Newmark_beta",
            "method_label": "Newmark-beta",
            "expected_order": 2,
        },
        {
            "paper_method": "tfe2026_trapezoidal",
            "source_method": "trapezoidal",
            "method_label": "trapezoidal",
            "expected_order": 2,
        },
        {
            "paper_method": "tfe2026_TFE_m1",
            "source_method": "TFE_m1",
            "method_label": "TFE m=1",
            "expected_order": 1,
        },
        {
            "paper_method": "tfe2026_TFE_m2",
            "source_method": "TFE_m2",
            "method_label": "TFE m=2",
            "expected_order": 3,
        },
        {
            "paper_method": "tfe2026_TFE_m3_GL",
            "source_method": "TFE_m3_GL",
            "method_label": "TFE m=3 GL",
            "expected_order": 5,
        },
        {
            "paper_method": "Gauss6_FullVA_source_pendulum_candidate",
            "source_method": "Gauss6_FullVA",
            "method_label": "Gauss6/FullVA",
            "expected_order": 6,
        },
    ]
    cases = [
        {
            "case_id": "frictionless_pendulum_absolute_lift_probe",
            "theta0": 0.0,
            "omega0": 0.0,
            "frictional": False,
        },
        {
            "case_id": "frictional_pendulum_candidate_absolute_lift_probe",
            "theta0": 0.0,
            "omega0": 1.0,
            "frictional": True,
        },
    ]
    rows: list[dict[str, object]] = []
    max_hinge_position = 0.0
    max_hinge_velocity = 0.0
    max_translational_balance = 0.0
    max_axis_rotational = 0.0
    for case in cases:
        reference, _ = integrate_planar_case_with_method(
            method="rk4_reference",
            theta0=float(case["theta0"]),
            omega0=float(case["omega0"]),
            h=reference_h,
            t_final=t_final,
            frictional=bool(case["frictional"]),
            axis=axis,
            stribeck_velocity=stribeck_velocity,
            viscous_damping=viscous_damping,
        )
        for method in method_specs:
            metrics_rows: list[dict[str, float]] = []
            coordinate_errors: list[float] = []
            velocity_errors: list[float] = []
            frobenius_errors: list[float] = []
            residuals: list[float] = []
            total_newton_iterations = 0.0
            for h in comparison_h:
                candidate, diagnostics = integrate_planar_case_with_method(
                    method=str(method["source_method"]),
                    theta0=float(case["theta0"]),
                    omega0=float(case["omega0"]),
                    h=float(h),
                    t_final=t_final,
                    frictional=bool(case["frictional"]),
                    axis=axis,
                    stribeck_velocity=stribeck_velocity,
                    viscous_damping=viscous_damping,
                )
                metrics = source_error_metrics(reference, candidate, axis=axis)
                residual = absolute_coordinate_dae_residual_smoke(
                    theta=candidate.theta,
                    omega=candidate.omega,
                    frictional=bool(case["frictional"]),
                    stribeck_velocity=stribeck_velocity,
                    axis=axis,
                )
                row = {
                    "h": float(h),
                    **metrics,
                    **diagnostics,
                    "hinge_position_constraint_norm": residual["hinge_position_constraint_norm"],
                    "hinge_velocity_constraint_norm": residual["hinge_velocity_constraint_norm"],
                    "translational_balance_residual_norm": residual["translational_balance_residual_norm"],
                    "axis_projected_rotational_residual_abs": residual[
                        "axis_projected_rotational_residual_abs"
                    ],
                    "candidate_friction_power": residual["candidate_friction_power"],
                    "source_policy_dae_runner_equivalent": False,
                }
                metrics_rows.append(row)
                coordinate_errors.append(float(metrics["coordinate_error_q"]))
                velocity_errors.append(float(metrics["velocity_error_v"]))
                frobenius_errors.append(float(metrics["frobenius_error_norm_eta"]))
                residuals.append(float(diagnostics["max_residual_norm"]))
                total_newton_iterations += float(diagnostics["total_newton_iterations"])
                max_hinge_position = max(max_hinge_position, float(residual["hinge_position_constraint_norm"]))
                max_hinge_velocity = max(max_hinge_velocity, float(residual["hinge_velocity_constraint_norm"]))
                max_translational_balance = max(
                    max_translational_balance,
                    float(residual["translational_balance_residual_norm"]),
                )
                max_axis_rotational = max(
                    max_axis_rotational,
                    float(residual["axis_projected_rotational_residual_abs"]),
                )
            rows.append(
                {
                    "case_id": case["case_id"],
                    "paper_method": method["paper_method"],
                    "source_method": method["source_method"],
                    "method_label": method["method_label"],
                    "expected_order": method["expected_order"],
                    "frictional": bool(case["frictional"]),
                    "reference_h": float(reference_h),
                    "metrics": metrics_rows,
                    "coordinate_pairwise_orders": _pairwise_orders(coordinate_errors, list(comparison_h)),
                    "velocity_pairwise_orders": _pairwise_orders(velocity_errors, list(comparison_h)),
                    "frobenius_pairwise_orders": _pairwise_orders(frobenius_errors, list(comparison_h)),
                    "coordinate_error_decreased": coordinate_errors[-1] < coordinate_errors[0],
                    "velocity_error_decreased": velocity_errors[-1] < velocity_errors[0],
                    "frobenius_error_decreased": frobenius_errors[-1] < frobenius_errors[0],
                    "max_newton_residual_norm": max(residuals),
                    "total_newton_iterations": total_newton_iterations,
                    "source_policy_dae_runner_equivalent": False,
                    "monolithic_absolute_coordinate_dae_time_integrator": False,
                    "source_policy_method_runner_equivalent": False,
                    "source_policy_row_completed": False,
                    "accepted_use": "absolute_coordinate_planar_lift_probe_not_source_policy",
                }
            )
    return {
        "runner_api": "absolute_coordinate_planar_lift_trajectory_probe",
        "runner_scope": "planar_candidate_trajectory_lifted_to_absolute_coordinate_residuals_not_source_policy",
        "absolute_coordinate_planar_lift_trajectory_probe_implemented": True,
        "monolithic_absolute_coordinate_dae_time_integrator": False,
        "source_policy_dae_runner_equivalent": False,
        "source_policy_method_runner_equivalent": False,
        "source_policy_rows_completed": 0,
        "external_superiority_claim_allowed": False,
        "t_final": float(t_final),
        "comparison_h": [float(item) for item in comparison_h],
        "reference_h": float(reference_h),
        "axis": axis,
        "case_count": len(cases),
        "method_count": len(method_specs),
        "row_count": len(rows),
        "metric_row_count": sum(len(row["metrics"]) for row in rows),
        "max_hinge_position_constraint_norm": max_hinge_position,
        "max_hinge_velocity_constraint_norm": max_hinge_velocity,
        "max_translational_balance_residual_norm": max_translational_balance,
        "max_axis_projected_rotational_residual_abs": max_axis_rotational,
        "accepted_use": "absolute_coordinate_planar_lift_probe_not_source_policy",
        "rows": rows,
    }


def active_tfe_b2_source_method_specs() -> tuple[dict[str, object], ...]:
    return (
        {
            "paper_method": "tfe2026_Newmark_beta",
            "source_method": "Newmark_beta",
            "expected_order": 2,
            "source_parameters": {"beta": 0.3, "gamma": 0.5},
        },
        {
            "paper_method": "tfe2026_TFE_m1",
            "source_method": "TFE_m1",
            "expected_order": 1,
            "source_parameters": {"nu": 0.99},
        },
        {
            "paper_method": "tfe2026_TFE_m2",
            "source_method": "TFE_m2",
            "expected_order": 3,
            "source_parameters": {"nu": 0.95},
        },
        {
            "paper_method": "tfe2026_trapezoidal",
            "source_method": "trapezoidal",
            "expected_order": 2,
            "source_parameters": {},
        },
    )


def bounded_absolute_coordinate_dae_trajectory_runner_smoke(
    config: BoundedSourcePolicyRunnerConfig | None = None,
    *,
    method_specs: tuple[dict[str, object], ...] | None = None,
) -> dict[str, object]:
    """Check bounded active-B2 candidate trajectories with stepwise DAE lifts.

    This runner streams every accepted planar candidate step through the
    absolute-coordinate DAE residual smoke. It is still a short bounded
    diagnostic and does not implement the monolithic T=10 source-policy DAE
    integrator.
    """

    config = config or BoundedSourcePolicyRunnerConfig()
    method_specs = method_specs or active_tfe_b2_source_method_specs()
    reference, reference_diagnostics = integrate_planar_case_with_method(
        method="rk4_reference",
        theta0=config.theta0,
        omega0=config.omega0,
        h=config.reference_h,
        t_final=config.t_final,
        frictional=config.frictional,
        axis=config.axis,
        stribeck_velocity=config.stribeck_velocity,
        viscous_damping=config.viscous_damping,
    )
    rows: list[dict[str, object]] = []
    max_hinge_position = 0.0
    max_hinge_velocity = 0.0
    max_translational_balance = 0.0
    max_axis_rotational = 0.0
    max_candidate_step_residual = 0.0
    total_step_residual_rows = 0
    all_step_states_finite = True
    for method in method_specs:
        metrics_rows: list[dict[str, object]] = []
        coordinate_errors: list[float] = []
        velocity_errors: list[float] = []
        frobenius_errors: list[float] = []
        method_total_newton_iterations = 0.0
        method_step_rows = 0
        method_max_hinge_position = 0.0
        method_max_hinge_velocity = 0.0
        method_max_translational_balance = 0.0
        method_max_axis_rotational = 0.0
        method_max_candidate_step_residual = 0.0
        for h in config.comparison_h:
            steps_float = config.t_final / float(h)
            steps = int(round(steps_float))
            if steps <= 0 or abs(steps_float - steps) > 1.0e-12:
                raise ValueError("bounded trajectory h must divide t_final")
            theta = config.theta0
            omega = config.omega0
            h_total_newton_iterations = 0.0
            h_max_hinge_position = 0.0
            h_max_hinge_velocity = 0.0
            h_max_translational_balance = 0.0
            h_max_axis_rotational = 0.0
            h_max_candidate_step_residual = 0.0
            h_step_states_finite = True
            for step_index in range(1, steps + 1):
                theta, omega, iterations, residual_norm = advance_planar_method_step(
                    method=str(method["source_method"]),
                    theta=theta,
                    omega=omega,
                    h=float(h),
                    frictional=config.frictional,
                    axis=config.axis,
                    stribeck_velocity=config.stribeck_velocity,
                    viscous_damping=config.viscous_damping,
                )
                residual = absolute_coordinate_dae_residual_smoke(
                    theta=theta,
                    omega=omega,
                    frictional=config.frictional,
                    stribeck_velocity=config.stribeck_velocity,
                    axis=config.axis,
                )
                residual_values = [
                    float(residual["hinge_position_constraint_norm"]),
                    float(residual["hinge_velocity_constraint_norm"]),
                    float(residual["translational_balance_residual_norm"]),
                    float(residual["axis_projected_rotational_residual_abs"]),
                    float(residual_norm),
                    float(theta),
                    float(omega),
                ]
                step_finite = all(np.isfinite(value) for value in residual_values)
                h_step_states_finite = h_step_states_finite and step_finite
                h_total_newton_iterations += float(iterations)
                h_max_hinge_position = max(h_max_hinge_position, residual_values[0])
                h_max_hinge_velocity = max(h_max_hinge_velocity, residual_values[1])
                h_max_translational_balance = max(h_max_translational_balance, residual_values[2])
                h_max_axis_rotational = max(h_max_axis_rotational, residual_values[3])
                h_max_candidate_step_residual = max(h_max_candidate_step_residual, residual_values[4])
                total_step_residual_rows += 1
                method_step_rows += 1
                if step_index == steps:
                    final_residual = residual
            candidate = SourcePlanarState(theta=theta, omega=omega)
            metrics = source_error_metrics(reference, candidate, axis=config.axis)
            coordinate_errors.append(float(metrics["coordinate_error_q"]))
            velocity_errors.append(float(metrics["velocity_error_v"]))
            frobenius_errors.append(float(metrics["frobenius_error_norm_eta"]))
            method_total_newton_iterations += h_total_newton_iterations
            method_max_hinge_position = max(method_max_hinge_position, h_max_hinge_position)
            method_max_hinge_velocity = max(method_max_hinge_velocity, h_max_hinge_velocity)
            method_max_translational_balance = max(
                method_max_translational_balance,
                h_max_translational_balance,
            )
            method_max_axis_rotational = max(method_max_axis_rotational, h_max_axis_rotational)
            method_max_candidate_step_residual = max(
                method_max_candidate_step_residual,
                h_max_candidate_step_residual,
            )
            all_step_states_finite = all_step_states_finite and h_step_states_finite
            metrics_rows.append(
                {
                    "h": float(h),
                    "step_count": steps,
                    "step_residual_rows": steps,
                    "step_states_finite": h_step_states_finite,
                    **metrics,
                    "total_newton_iterations": h_total_newton_iterations,
                    "max_candidate_step_residual_norm": h_max_candidate_step_residual,
                    "max_hinge_position_constraint_norm": h_max_hinge_position,
                    "max_hinge_velocity_constraint_norm": h_max_hinge_velocity,
                    "max_translational_balance_residual_norm": h_max_translational_balance,
                    "max_axis_projected_rotational_residual_abs": h_max_axis_rotational,
                    "final_hinge_position_constraint_norm": final_residual[
                        "hinge_position_constraint_norm"
                    ],
                    "final_hinge_velocity_constraint_norm": final_residual[
                        "hinge_velocity_constraint_norm"
                    ],
                    "source_policy_dae_runner_equivalent": False,
                }
            )
        max_hinge_position = max(max_hinge_position, method_max_hinge_position)
        max_hinge_velocity = max(max_hinge_velocity, method_max_hinge_velocity)
        max_translational_balance = max(max_translational_balance, method_max_translational_balance)
        max_axis_rotational = max(max_axis_rotational, method_max_axis_rotational)
        max_candidate_step_residual = max(
            max_candidate_step_residual,
            method_max_candidate_step_residual,
        )
        rows.append(
            {
                "case_id": "frictionless_pendulum_active_b2_bounded_dae_trajectory",
                "example": "single_pendulum",
                "paper_method": method["paper_method"],
                "source_method": method["source_method"],
                "expected_order": method["expected_order"],
                "source_parameters": method["source_parameters"],
                "frictional": config.frictional,
                "reference_h": float(config.reference_h),
                "metrics": metrics_rows,
                "coordinate_pairwise_orders": _pairwise_orders(coordinate_errors, list(config.comparison_h)),
                "velocity_pairwise_orders": _pairwise_orders(velocity_errors, list(config.comparison_h)),
                "frobenius_pairwise_orders": _pairwise_orders(frobenius_errors, list(config.comparison_h)),
                "step_residual_rows": method_step_rows,
                "step_states_finite": all(row["step_states_finite"] for row in metrics_rows),
                "total_newton_iterations": method_total_newton_iterations,
                "max_candidate_step_residual_norm": method_max_candidate_step_residual,
                "max_hinge_position_constraint_norm": method_max_hinge_position,
                "max_hinge_velocity_constraint_norm": method_max_hinge_velocity,
                "max_translational_balance_residual_norm": method_max_translational_balance,
                "max_axis_projected_rotational_residual_abs": method_max_axis_rotational,
                "monolithic_absolute_coordinate_dae_time_integrator": False,
                "source_policy_dae_runner_equivalent": False,
                "source_policy_method_runner_equivalent": False,
                "source_policy_row_completed": False,
                "accepted_use": "bounded_stepwise_absolute_dae_residual_runner_not_source_policy",
            }
        )
    return {
        "runner_api": "bounded_absolute_coordinate_dae_trajectory_runner_smoke",
        "runner_scope": "bounded_stepwise_absolute_dae_residual_runner_not_source_policy",
        "bounded_absolute_coordinate_dae_trajectory_runner_implemented": True,
        "monolithic_absolute_coordinate_dae_time_integrator": False,
        "source_policy_dae_runner_equivalent": False,
        "source_policy_method_runner_equivalent": False,
        "source_policy_rows_completed": 0,
        "external_superiority_claim_allowed": False,
        "accepted_use": "bounded_stepwise_absolute_dae_residual_runner_not_source_policy",
        "case_id": "frictionless_pendulum_active_b2_bounded_dae_trajectory",
        "example": "single_pendulum",
        "t_final": float(config.t_final),
        "comparison_h": [float(item) for item in config.comparison_h],
        "reference_h": float(config.reference_h),
        "reference_method": "rk4_reference",
        "reference_diagnostics": reference_diagnostics,
        "axis": config.axis,
        "frictional": config.frictional,
        "method_count": len(method_specs),
        "row_count": len(rows),
        "metric_row_count": sum(len(row["metrics"]) for row in rows),
        "step_residual_row_count": total_step_residual_rows,
        "all_step_states_finite": all_step_states_finite,
        "max_candidate_step_residual_norm": max_candidate_step_residual,
        "max_hinge_position_constraint_norm": max_hinge_position,
        "max_hinge_velocity_constraint_norm": max_hinge_velocity,
        "max_translational_balance_residual_norm": max_translational_balance,
        "max_axis_projected_rotational_residual_abs": max_axis_rotational,
        "rows": rows,
    }


def monolithic_absolute_coordinate_dae_candidate_runner_smoke(
    config: BoundedSourcePolicyRunnerConfig | None = None,
    *,
    method_specs: tuple[dict[str, object], ...] | None = None,
) -> dict[str, object]:
    """Expose a single candidate entrypoint over the bounded DAE trajectory rows.

    The entrypoint is intentionally a local candidate orchestrator over the
    bounded stepwise residual runner. It is not the original TFE source-policy
    DAE solver and does not close any source-policy comparison row.
    """

    config = config or BoundedSourcePolicyRunnerConfig()
    method_specs = method_specs or active_tfe_b2_source_method_specs()
    bounded_runner = bounded_absolute_coordinate_dae_trajectory_runner_smoke(
        config,
        method_specs=method_specs,
    )
    rows: list[dict[str, object]] = []
    all_rows_finite = True
    all_dae_residuals_below_1e_10 = True
    accepted_use = "monolithic_absolute_coordinate_candidate_runner_not_source_policy"
    dae_residual_fields = (
        "max_hinge_position_constraint_norm",
        "max_hinge_velocity_constraint_norm",
        "max_translational_balance_residual_norm",
        "max_axis_projected_rotational_residual_abs",
    )
    metric_residual_fields = (
        "max_hinge_position_constraint_norm",
        "max_hinge_velocity_constraint_norm",
        "max_translational_balance_residual_norm",
        "max_axis_projected_rotational_residual_abs",
    )
    for bounded_row in bounded_runner["rows"]:
        metrics: list[dict[str, object]] = []
        method_metrics_finite = True
        method_dae_residuals_below_1e_10 = True
        for bounded_metric in bounded_row["metrics"]:
            metric = dict(bounded_metric)
            metric.update(
                {
                    "monolithic_candidate_time_integration_entrypoint": True,
                    "monolithic_absolute_coordinate_dae_time_integrator": False,
                    "source_policy_dae_runner_equivalent": False,
                    "source_policy_method_runner_equivalent": False,
                    "source_policy_row_completed": False,
                    "accepted_use": accepted_use,
                }
            )
            residual_values = [float(metric[field]) for field in metric_residual_fields]
            finite_values = residual_values + [
                float(metric["coordinate_error_q"]),
                float(metric["velocity_error_v"]),
                float(metric["frobenius_error_norm_eta"]),
                float(metric["max_candidate_step_residual_norm"]),
            ]
            metric_finite = bool(metric.get("step_states_finite")) and all(
                np.isfinite(value) for value in finite_values
            )
            metric_dae_ok = all(value < 1.0e-10 for value in residual_values)
            method_metrics_finite = method_metrics_finite and metric_finite
            method_dae_residuals_below_1e_10 = (
                method_dae_residuals_below_1e_10 and metric_dae_ok
            )
            metrics.append(metric)
        row = {
            "case_id": "frictionless_pendulum_active_b2_monolithic_dae_candidate",
            "example": bounded_row["example"],
            "paper_method": bounded_row["paper_method"],
            "source_method": bounded_row["source_method"],
            "expected_order": bounded_row["expected_order"],
            "source_parameters": bounded_row["source_parameters"],
            "frictional": bounded_row["frictional"],
            "reference_h": bounded_row["reference_h"],
            "metrics": metrics,
            "coordinate_pairwise_orders": bounded_row["coordinate_pairwise_orders"],
            "velocity_pairwise_orders": bounded_row["velocity_pairwise_orders"],
            "frobenius_pairwise_orders": bounded_row["frobenius_pairwise_orders"],
            "step_residual_rows": bounded_row["step_residual_rows"],
            "step_states_finite": bounded_row["step_states_finite"],
            "all_metrics_finite": method_metrics_finite,
            "all_dae_residuals_below_1e_10": method_dae_residuals_below_1e_10,
            "total_newton_iterations": bounded_row["total_newton_iterations"],
            "max_candidate_step_residual_norm": bounded_row[
                "max_candidate_step_residual_norm"
            ],
            "max_hinge_position_constraint_norm": bounded_row[
                "max_hinge_position_constraint_norm"
            ],
            "max_hinge_velocity_constraint_norm": bounded_row[
                "max_hinge_velocity_constraint_norm"
            ],
            "max_translational_balance_residual_norm": bounded_row[
                "max_translational_balance_residual_norm"
            ],
            "max_axis_projected_rotational_residual_abs": bounded_row[
                "max_axis_projected_rotational_residual_abs"
            ],
            "bounded_stepwise_runner_api": bounded_runner["runner_api"],
            "bounded_stepwise_runner_scope": bounded_runner["runner_scope"],
            "monolithic_candidate_time_integration_entrypoint": True,
            "monolithic_absolute_coordinate_dae_time_integrator": False,
            "source_policy_dae_runner_equivalent": False,
            "source_policy_method_runner_equivalent": False,
            "source_policy_row_completed": False,
            "accepted_use": accepted_use,
        }
        method_row_finite = bool(row["step_states_finite"]) and method_metrics_finite and all(
            np.isfinite(float(row[field])) for field in dae_residual_fields
        )
        method_row_dae_ok = all(float(row[field]) < 1.0e-10 for field in dae_residual_fields)
        all_rows_finite = all_rows_finite and method_row_finite
        all_dae_residuals_below_1e_10 = all_dae_residuals_below_1e_10 and method_row_dae_ok
        rows.append(row)
    return {
        "runner_api": "monolithic_absolute_coordinate_dae_candidate_runner_smoke",
        "runner_scope": "single_entrypoint_absolute_dae_candidate_runner_not_source_policy",
        "monolithic_absolute_coordinate_dae_candidate_runner_implemented": True,
        "monolithic_candidate_time_integration_entrypoint": True,
        "monolithic_absolute_coordinate_dae_time_integrator": False,
        "source_policy_dae_runner_equivalent": False,
        "source_policy_method_runner_equivalent": False,
        "source_policy_rows_completed": 0,
        "external_superiority_claim_allowed": False,
        "accepted_use": accepted_use,
        "case_id": "frictionless_pendulum_active_b2_monolithic_dae_candidate",
        "example": "single_pendulum",
        "t_final": bounded_runner["t_final"],
        "comparison_h": bounded_runner["comparison_h"],
        "reference_h": bounded_runner["reference_h"],
        "reference_method": bounded_runner["reference_method"],
        "reference_diagnostics": bounded_runner["reference_diagnostics"],
        "axis": bounded_runner["axis"],
        "frictional": bounded_runner["frictional"],
        "method_count": bounded_runner["method_count"],
        "row_count": len(rows),
        "metric_row_count": sum(len(row["metrics"]) for row in rows),
        "step_residual_row_count": bounded_runner["step_residual_row_count"],
        "all_step_states_finite": bounded_runner["all_step_states_finite"],
        "all_rows_finite": all_rows_finite,
        "all_dae_residuals_below_1e_10": all_dae_residuals_below_1e_10,
        "max_candidate_step_residual_norm": bounded_runner[
            "max_candidate_step_residual_norm"
        ],
        "max_hinge_position_constraint_norm": bounded_runner[
            "max_hinge_position_constraint_norm"
        ],
        "max_hinge_velocity_constraint_norm": bounded_runner[
            "max_hinge_velocity_constraint_norm"
        ],
        "max_translational_balance_residual_norm": bounded_runner[
            "max_translational_balance_residual_norm"
        ],
        "max_axis_projected_rotational_residual_abs": bounded_runner[
            "max_axis_projected_rotational_residual_abs"
        ],
        "bounded_stepwise_runner_api": bounded_runner["runner_api"],
        "bounded_stepwise_runner_scope": bounded_runner["runner_scope"],
        "rows": rows,
    }


def source_policy_absolute_coordinate_dae_runner(
    config: BoundedSourcePolicyRunnerConfig | None = None,
    *,
    method_specs: tuple[dict[str, object], ...] | None = None,
    candidate_runner: dict[str, object] | None = None,
) -> dict[str, object]:
    """Named source-policy DAE runner contract boundary.

    This entrypoint is intentionally contract-only: it exposes a stable API
    name for audits while delegating to the local monolithic candidate runner.
    It is not a source-code-equivalent TFE DAE integrator and closes no
    source-policy rows.
    """

    candidate_runner = candidate_runner or monolithic_absolute_coordinate_dae_candidate_runner_smoke(
        config,
        method_specs=method_specs,
    )
    accepted_use = "contract_entrypoint_only_not_source_policy_reproduction"
    rows: list[dict[str, object]] = []
    for candidate_row in candidate_runner["rows"]:
        metrics: list[dict[str, object]] = []
        for candidate_metric in candidate_row["metrics"]:
            metric = dict(candidate_metric)
            metric.update(
                {
                    "source_policy_absolute_coordinate_dae_runner_contract_present": True,
                    "source_policy_absolute_coordinate_dae_runner_implemented": False,
                    "source_policy_absolute_coordinate_dae_runner_equivalent": False,
                    "monolithic_absolute_coordinate_dae_time_integrator": False,
                    "source_policy_dae_runner_equivalent": False,
                    "source_policy_method_runner_equivalent": False,
                    "source_policy_row_completed": False,
                    "accepted_use": accepted_use,
                    "candidate_runner_api": candidate_runner["runner_api"],
                    "candidate_runner_scope": candidate_runner["runner_scope"],
                }
            )
            metrics.append(metric)
        row = dict(candidate_row)
        row.update(
            {
                "case_id": "frictionless_pendulum_active_b2_source_policy_dae_contract",
                "metrics": metrics,
                "source_policy_absolute_coordinate_dae_runner_contract_present": True,
                "source_policy_absolute_coordinate_dae_runner_implemented": False,
                "source_policy_absolute_coordinate_dae_runner_equivalent": False,
                "monolithic_absolute_coordinate_dae_time_integrator": False,
                "source_policy_dae_runner_equivalent": False,
                "source_policy_method_runner_equivalent": False,
                "source_policy_row_completed": False,
                "accepted_use": accepted_use,
                "candidate_runner_api": candidate_runner["runner_api"],
                "candidate_runner_scope": candidate_runner["runner_scope"],
            }
        )
        rows.append(row)
    return {
        "schema": "tfe-source-policy-absolute-coordinate-dae-runner-contract-v1",
        "runner_api": "source_policy_absolute_coordinate_dae_runner",
        "runner_scope": "contract_entrypoint_present_candidate_backed_not_source_policy_equivalent",
        "source_policy_absolute_coordinate_dae_runner_contract_present": True,
        "source_policy_absolute_coordinate_dae_runner_implemented": False,
        "source_policy_absolute_coordinate_dae_runner_equivalent": False,
        "monolithic_candidate_time_integration_entrypoint": candidate_runner[
            "monolithic_candidate_time_integration_entrypoint"
        ],
        "monolithic_absolute_coordinate_dae_time_integrator": False,
        "source_policy_dae_runner_equivalent": False,
        "source_policy_method_runner_equivalent": False,
        "source_policy_rows_completed": 0,
        "external_superiority_claim_allowed": False,
        "accepted_use": accepted_use,
        "case_id": "frictionless_pendulum_active_b2_source_policy_dae_contract",
        "example": "single_pendulum",
        "t_final": candidate_runner["t_final"],
        "comparison_h": candidate_runner["comparison_h"],
        "reference_h": candidate_runner["reference_h"],
        "reference_method": candidate_runner["reference_method"],
        "reference_diagnostics": candidate_runner["reference_diagnostics"],
        "axis": candidate_runner["axis"],
        "frictional": candidate_runner["frictional"],
        "method_count": candidate_runner["method_count"],
        "row_count": len(rows),
        "metric_row_count": sum(len(row["metrics"]) for row in rows),
        "step_residual_row_count": candidate_runner["step_residual_row_count"],
        "all_step_states_finite": candidate_runner["all_step_states_finite"],
        "all_rows_finite": candidate_runner["all_rows_finite"],
        "all_dae_residuals_below_1e_10": candidate_runner[
            "all_dae_residuals_below_1e_10"
        ],
        "max_candidate_step_residual_norm": candidate_runner[
            "max_candidate_step_residual_norm"
        ],
        "max_hinge_position_constraint_norm": candidate_runner[
            "max_hinge_position_constraint_norm"
        ],
        "max_hinge_velocity_constraint_norm": candidate_runner[
            "max_hinge_velocity_constraint_norm"
        ],
        "max_translational_balance_residual_norm": candidate_runner[
            "max_translational_balance_residual_norm"
        ],
        "max_axis_projected_rotational_residual_abs": candidate_runner[
            "max_axis_projected_rotational_residual_abs"
        ],
        "candidate_runner_api": candidate_runner["runner_api"],
        "candidate_runner_scope": candidate_runner["runner_scope"],
        "bounded_stepwise_runner_api": candidate_runner["bounded_stepwise_runner_api"],
        "bounded_stepwise_runner_scope": candidate_runner["bounded_stepwise_runner_scope"],
        "rows": rows,
    }


def dae_trajectory_bridge_contract_smoke(
    config: BoundedSourcePolicyRunnerConfig | None = None,
    *,
    method_specs: tuple[dict[str, object], ...] | None = None,
) -> dict[str, object]:
    """Bind bounded source metrics to stepwise absolute-coordinate residuals.

    This is a contract matrix over the same active-B2 method/grid rows used by
    the bounded source-shaped runner and the bounded DAE residual runner. It
    makes the runner evidence auditable without claiming the original
    source-policy DAE integrator, full T=10 source-code execution, or any
    source-policy comparison row.
    """

    config = config or BoundedSourcePolicyRunnerConfig()
    method_specs = method_specs or active_tfe_b2_source_method_specs()
    source_runner = bounded_source_policy_runner_smoke(config, method_specs=method_specs)
    dae_runner = bounded_absolute_coordinate_dae_trajectory_runner_smoke(
        config,
        method_specs=method_specs,
    )
    dae_rows_by_method = {
        str(row["source_method"]): row
        for row in dae_runner["rows"]
    }
    contract_rows: list[dict[str, object]] = []
    max_hinge_position = 0.0
    max_hinge_velocity = 0.0
    max_translational_balance = 0.0
    max_axis_rotational = 0.0
    max_candidate_step_residual = 0.0
    all_rows_finite = True
    all_dae_residuals_below_threshold = True
    for source_row in source_runner["rows"]:
        source_method = str(source_row["source_method"])
        dae_row = dae_rows_by_method[source_method]
        dae_metrics_by_h = {
            float(metric["h"]): metric
            for metric in dae_row["metrics"]
        }
        for source_metric in source_row["metrics"]:
            h = float(source_metric["h"])
            dae_metric = dae_metrics_by_h[h]
            finite_values = [
                float(source_metric["coordinate_error_q"]),
                float(source_metric["velocity_error_v"]),
                float(source_metric["frobenius_error_norm_eta"]),
                float(dae_metric["max_candidate_step_residual_norm"]),
                float(dae_metric["max_hinge_position_constraint_norm"]),
                float(dae_metric["max_hinge_velocity_constraint_norm"]),
                float(dae_metric["max_translational_balance_residual_norm"]),
                float(dae_metric["max_axis_projected_rotational_residual_abs"]),
            ]
            row_finite = all(np.isfinite(value) for value in finite_values)
            row_dae_ok = max(finite_values[3:]) < 1.0e-10
            all_rows_finite = all_rows_finite and row_finite
            all_dae_residuals_below_threshold = all_dae_residuals_below_threshold and row_dae_ok
            max_candidate_step_residual = max(max_candidate_step_residual, finite_values[3])
            max_hinge_position = max(max_hinge_position, finite_values[4])
            max_hinge_velocity = max(max_hinge_velocity, finite_values[5])
            max_translational_balance = max(max_translational_balance, finite_values[6])
            max_axis_rotational = max(max_axis_rotational, finite_values[7])
            contract_rows.append(
                {
                    "case_id": source_row["case_id"],
                    "example": source_row["example"],
                    "paper_method": source_row["paper_method"],
                    "source_method": source_method,
                    "expected_order": source_row["expected_order"],
                    "h": h,
                    "step_count": dae_metric["step_count"],
                    "source_metric_row_matched": True,
                    "dae_metric_row_matched": True,
                    "coordinate_error_q": source_metric["coordinate_error_q"],
                    "velocity_error_v": source_metric["velocity_error_v"],
                    "frobenius_error_norm_eta": source_metric["frobenius_error_norm_eta"],
                    "work_units_newton_iterations": source_metric["total_newton_iterations"],
                    "step_residual_rows": dae_metric["step_residual_rows"],
                    "step_states_finite": dae_metric["step_states_finite"],
                    "max_candidate_step_residual_norm": dae_metric[
                        "max_candidate_step_residual_norm"
                    ],
                    "max_hinge_position_constraint_norm": dae_metric[
                        "max_hinge_position_constraint_norm"
                    ],
                    "max_hinge_velocity_constraint_norm": dae_metric[
                        "max_hinge_velocity_constraint_norm"
                    ],
                    "max_translational_balance_residual_norm": dae_metric[
                        "max_translational_balance_residual_norm"
                    ],
                    "max_axis_projected_rotational_residual_abs": dae_metric[
                        "max_axis_projected_rotational_residual_abs"
                    ],
                    "row_finite": row_finite,
                    "dae_residual_below_1e_10": row_dae_ok,
                    "source_policy_dae_runner_equivalent": False,
                    "source_policy_method_runner_equivalent": False,
                    "source_policy_row_completed": False,
                    "accepted_use": "dae_trajectory_bridge_contract_not_source_policy",
                }
            )

    return {
        "schema": "tfe-dae-trajectory-bridge-contract-smoke-v1",
        "runner_api": "dae_trajectory_bridge_contract_smoke",
        "runner_scope": "bounded_source_metrics_bound_to_stepwise_absolute_dae_residuals_not_source_policy",
        "dae_trajectory_bridge_contract_implemented": True,
        "source_runner_api": source_runner["runner_api"],
        "dae_runner_api": dae_runner["runner_api"],
        "t_final": float(config.t_final),
        "comparison_h": [float(item) for item in config.comparison_h],
        "reference_h": float(config.reference_h),
        "axis": config.axis,
        "frictional": bool(config.frictional),
        "method_count": len(method_specs),
        "source_metric_row_count": sum(len(row["metrics"]) for row in source_runner["rows"]),
        "dae_metric_row_count": sum(len(row["metrics"]) for row in dae_runner["rows"]),
        "row_count": len(contract_rows),
        "matched_contract_row_count": sum(
            int(row["source_metric_row_matched"] and row["dae_metric_row_matched"])
            for row in contract_rows
        ),
        "all_rows_finite": all_rows_finite,
        "all_dae_residuals_below_1e_10": all_dae_residuals_below_threshold,
        "max_candidate_step_residual_norm": max_candidate_step_residual,
        "max_hinge_position_constraint_norm": max_hinge_position,
        "max_hinge_velocity_constraint_norm": max_hinge_velocity,
        "max_translational_balance_residual_norm": max_translational_balance,
        "max_axis_projected_rotational_residual_abs": max_axis_rotational,
        "monolithic_absolute_coordinate_dae_time_integrator": False,
        "source_policy_dae_runner_equivalent": False,
        "source_policy_method_runner_equivalent": False,
        "source_policy_rows_completed": 0,
        "external_superiority_claim_allowed": False,
        "accepted_use": "dae_trajectory_bridge_contract_not_source_policy",
        "rows": contract_rows,
    }


def candidate_frictional_dae_trajectory_contract_smoke(
    config: BoundedSourcePolicyRunnerConfig | None = None,
    *,
    method_specs: tuple[dict[str, object], ...] | None = None,
) -> dict[str, object]:
    """Run a bounded candidate-friction trajectory through DAE residual checks.

    This closes a candidate-friction consistency layer only. The Brown--McPhee
    source code, transition-velocity policy, and monolithic source-policy DAE
    integrator are still open, so this contract must not be counted as a
    source-policy comparison row.
    """

    config = config or BoundedSourcePolicyRunnerConfig(theta0=0.0, omega0=1.0, frictional=True)
    if not config.frictional:
        raise ValueError("candidate frictional DAE trajectory contract requires frictional=True")
    method_specs = method_specs or active_tfe_b2_source_method_specs()
    reference, reference_diagnostics = integrate_planar_case_with_method(
        method="rk4_reference",
        theta0=config.theta0,
        omega0=config.omega0,
        h=config.reference_h,
        t_final=config.t_final,
        frictional=True,
        axis=config.axis,
        stribeck_velocity=config.stribeck_velocity,
        viscous_damping=config.viscous_damping,
    )
    rows: list[dict[str, object]] = []
    max_hinge_position = 0.0
    max_hinge_velocity = 0.0
    max_translational_balance = 0.0
    max_axis_rotational = 0.0
    max_candidate_step_residual = 0.0
    max_candidate_friction_power = -np.inf
    min_candidate_friction_power = np.inf
    total_step_residual_rows = 0
    all_rows_finite = True
    all_dae_residuals_below_threshold = True
    all_candidate_friction_power_nonpositive = True
    for method in method_specs:
        for h in config.comparison_h:
            steps_float = config.t_final / float(h)
            steps = int(round(steps_float))
            if steps <= 0 or abs(steps_float - steps) > 1.0e-12:
                raise ValueError("candidate frictional trajectory h must divide t_final")
            theta = config.theta0
            omega = config.omega0
            h_total_newton_iterations = 0.0
            h_max_hinge_position = 0.0
            h_max_hinge_velocity = 0.0
            h_max_translational_balance = 0.0
            h_max_axis_rotational = 0.0
            h_max_candidate_step_residual = 0.0
            h_max_candidate_friction_power = -np.inf
            h_min_candidate_friction_power = np.inf
            h_all_friction_power_nonpositive = True
            h_step_states_finite = True
            for _ in range(steps):
                theta, omega, iterations, residual_norm = advance_planar_method_step(
                    method=str(method["source_method"]),
                    theta=theta,
                    omega=omega,
                    h=float(h),
                    frictional=True,
                    axis=config.axis,
                    stribeck_velocity=config.stribeck_velocity,
                    viscous_damping=config.viscous_damping,
                )
                residual = absolute_coordinate_dae_residual_smoke(
                    theta=theta,
                    omega=omega,
                    frictional=True,
                    stribeck_velocity=config.stribeck_velocity,
                    axis=config.axis,
                )
                friction_power = float(residual["candidate_friction_power"])
                residual_values = [
                    float(residual["hinge_position_constraint_norm"]),
                    float(residual["hinge_velocity_constraint_norm"]),
                    float(residual["translational_balance_residual_norm"]),
                    float(residual["axis_projected_rotational_residual_abs"]),
                    float(residual_norm),
                    float(residual["candidate_friction_torque"]),
                    friction_power,
                    float(residual["hinge_reaction_norm"]),
                    float(theta),
                    float(omega),
                ]
                step_finite = all(np.isfinite(value) for value in residual_values)
                h_step_states_finite = h_step_states_finite and step_finite
                h_total_newton_iterations += float(iterations)
                h_max_hinge_position = max(h_max_hinge_position, residual_values[0])
                h_max_hinge_velocity = max(h_max_hinge_velocity, residual_values[1])
                h_max_translational_balance = max(h_max_translational_balance, residual_values[2])
                h_max_axis_rotational = max(h_max_axis_rotational, residual_values[3])
                h_max_candidate_step_residual = max(h_max_candidate_step_residual, residual_values[4])
                h_max_candidate_friction_power = max(h_max_candidate_friction_power, friction_power)
                h_min_candidate_friction_power = min(h_min_candidate_friction_power, friction_power)
                h_all_friction_power_nonpositive = (
                    h_all_friction_power_nonpositive and friction_power <= 1.0e-12
                )
                total_step_residual_rows += 1
            candidate = SourcePlanarState(theta=theta, omega=omega)
            metrics = source_error_metrics(reference, candidate, axis=config.axis)
            finite_values = [
                float(metrics["coordinate_error_q"]),
                float(metrics["velocity_error_v"]),
                float(metrics["frobenius_error_norm_eta"]),
                h_max_candidate_step_residual,
                h_max_hinge_position,
                h_max_hinge_velocity,
                h_max_translational_balance,
                h_max_axis_rotational,
                h_max_candidate_friction_power,
                h_min_candidate_friction_power,
            ]
            row_finite = h_step_states_finite and all(np.isfinite(value) for value in finite_values)
            row_dae_ok = max(finite_values[3:8]) < 1.0e-9
            all_rows_finite = all_rows_finite and row_finite
            all_dae_residuals_below_threshold = all_dae_residuals_below_threshold and row_dae_ok
            all_candidate_friction_power_nonpositive = (
                all_candidate_friction_power_nonpositive and h_all_friction_power_nonpositive
            )
            max_hinge_position = max(max_hinge_position, h_max_hinge_position)
            max_hinge_velocity = max(max_hinge_velocity, h_max_hinge_velocity)
            max_translational_balance = max(max_translational_balance, h_max_translational_balance)
            max_axis_rotational = max(max_axis_rotational, h_max_axis_rotational)
            max_candidate_step_residual = max(max_candidate_step_residual, h_max_candidate_step_residual)
            max_candidate_friction_power = max(max_candidate_friction_power, h_max_candidate_friction_power)
            min_candidate_friction_power = min(min_candidate_friction_power, h_min_candidate_friction_power)
            rows.append(
                {
                    "case_id": "candidate_frictional_pendulum_dae_trajectory_contract",
                    "example": "single_pendulum",
                    "paper_method": method["paper_method"],
                    "source_method": method["source_method"],
                    "expected_order": method["expected_order"],
                    "h": float(h),
                    "step_count": steps,
                    "step_residual_rows": steps,
                    "step_states_finite": h_step_states_finite,
                    **metrics,
                    "total_newton_iterations": h_total_newton_iterations,
                    "max_candidate_step_residual_norm": h_max_candidate_step_residual,
                    "max_hinge_position_constraint_norm": h_max_hinge_position,
                    "max_hinge_velocity_constraint_norm": h_max_hinge_velocity,
                    "max_translational_balance_residual_norm": h_max_translational_balance,
                    "max_axis_projected_rotational_residual_abs": h_max_axis_rotational,
                    "max_candidate_friction_power": h_max_candidate_friction_power,
                    "min_candidate_friction_power": h_min_candidate_friction_power,
                    "candidate_friction_power_nonpositive": h_all_friction_power_nonpositive,
                    "row_finite": row_finite,
                    "dae_residual_below_1e_9": row_dae_ok,
                    "frictional": True,
                    "brown_mcphee_candidate_law_encoded": True,
                    "brown_mcphee_source_code_equivalent_law": False,
                    "source_policy_dae_runner_equivalent": False,
                    "source_policy_method_runner_equivalent": False,
                    "source_policy_row_completed": False,
                    "accepted_use": "candidate_frictional_dae_trajectory_contract_not_source_policy",
                }
            )
    return {
        "schema": "tfe-candidate-frictional-dae-trajectory-contract-smoke-v1",
        "runner_api": "candidate_frictional_dae_trajectory_contract_smoke",
        "runner_scope": "candidate_brown_mcphee_friction_bound_to_stepwise_absolute_dae_residuals_not_source_policy",
        "candidate_frictional_dae_trajectory_contract_implemented": True,
        "brown_mcphee_candidate_law_encoded": True,
        "brown_mcphee_source_code_equivalent_law": False,
        "brown_mcphee_friction_law_implemented": False,
        "pendulum_dae_runner_implemented": False,
        "monolithic_absolute_coordinate_dae_time_integrator": False,
        "source_policy_dae_runner_equivalent": False,
        "source_policy_method_runner_equivalent": False,
        "source_policy_rows_completed": 0,
        "external_superiority_claim_allowed": False,
        "accepted_use": "candidate_frictional_dae_trajectory_contract_not_source_policy",
        "t_final": float(config.t_final),
        "comparison_h": [float(item) for item in config.comparison_h],
        "reference_h": float(config.reference_h),
        "reference_method": "rk4_reference",
        "reference_diagnostics": reference_diagnostics,
        "axis": config.axis,
        "theta0": float(config.theta0),
        "omega0": float(config.omega0),
        "frictional": True,
        "stribeck_velocity": float(config.stribeck_velocity),
        "viscous_damping": float(config.viscous_damping),
        "method_count": len(method_specs),
        "row_count": len(rows),
        "step_residual_row_count": total_step_residual_rows,
        "all_rows_finite": all_rows_finite,
        "all_dae_residuals_below_1e_9": all_dae_residuals_below_threshold,
        "all_candidate_friction_power_nonpositive": all_candidate_friction_power_nonpositive,
        "max_candidate_step_residual_norm": max_candidate_step_residual,
        "max_hinge_position_constraint_norm": max_hinge_position,
        "max_hinge_velocity_constraint_norm": max_hinge_velocity,
        "max_translational_balance_residual_norm": max_translational_balance,
        "max_axis_projected_rotational_residual_abs": max_axis_rotational,
        "max_candidate_friction_power": max_candidate_friction_power,
        "min_candidate_friction_power": min_candidate_friction_power,
        "rows": rows,
    }


def bounded_source_policy_runner_smoke(
    config: BoundedSourcePolicyRunnerConfig | None = None,
    *,
    method_specs: tuple[dict[str, object], ...] | None = None,
) -> dict[str, object]:
    """Run active TFE rows through one bounded source-shaped runner API.

    This promotes the previous per-smoke dispatch into a single reproducible
    runner entry point. It remains a short-interval candidate runner and does
    not claim original source-code or full T=10 source-policy equivalence.
    """

    config = config or BoundedSourcePolicyRunnerConfig()
    method_specs = method_specs or active_tfe_b2_source_method_specs()
    reference, _ = integrate_planar_case_with_method(
        method="rk4_reference",
        theta0=config.theta0,
        omega0=config.omega0,
        h=config.reference_h,
        t_final=config.t_final,
        frictional=config.frictional,
        axis=config.axis,
        stribeck_velocity=config.stribeck_velocity,
        viscous_damping=config.viscous_damping,
    )
    rows: list[dict[str, object]] = []
    for method in method_specs:
        metrics_rows: list[dict[str, float]] = []
        coordinate_errors: list[float] = []
        velocity_errors: list[float] = []
        frobenius_errors: list[float] = []
        residuals: list[float] = []
        total_newton_iterations = 0.0
        for h in config.comparison_h:
            candidate, diagnostics = integrate_planar_case_with_method(
                method=str(method["source_method"]),
                theta0=config.theta0,
                omega0=config.omega0,
                h=float(h),
                t_final=config.t_final,
                frictional=config.frictional,
                axis=config.axis,
                stribeck_velocity=config.stribeck_velocity,
                viscous_damping=config.viscous_damping,
            )
            metrics = source_error_metrics(reference, candidate, axis=config.axis)
            metrics_rows.append({"h": float(h), **metrics, **diagnostics})
            coordinate_errors.append(float(metrics["coordinate_error_q"]))
            velocity_errors.append(float(metrics["velocity_error_v"]))
            frobenius_errors.append(float(metrics["frobenius_error_norm_eta"]))
            residuals.append(float(diagnostics["max_residual_norm"]))
            total_newton_iterations += float(diagnostics["total_newton_iterations"])
        rows.append(
            {
                "case_id": "frictionless_pendulum_active_b2_source_shape_smoke",
                "example": "single_pendulum",
                "paper_method": method["paper_method"],
                "source_method": method["source_method"],
                "expected_order": method["expected_order"],
                "source_parameters": method["source_parameters"],
                "frictional": bool(config.frictional),
                "reference_h": float(config.reference_h),
                "metrics": metrics_rows,
                "coordinate_pairwise_orders": _pairwise_orders(coordinate_errors, list(config.comparison_h)),
                "velocity_pairwise_orders": _pairwise_orders(velocity_errors, list(config.comparison_h)),
                "frobenius_pairwise_orders": _pairwise_orders(frobenius_errors, list(config.comparison_h)),
                "coordinate_error_decreased": coordinate_errors[-1] < coordinate_errors[0],
                "velocity_error_decreased": velocity_errors[-1] < velocity_errors[0],
                "frobenius_error_decreased": frobenius_errors[-1] < frobenius_errors[0],
                "max_newton_residual_norm": max(residuals),
                "total_newton_iterations": total_newton_iterations,
                "source_policy_method_runner_equivalent": False,
                "source_policy_row_completed": False,
                "accepted_use": "bounded_candidate_runner_api_only_not_source_policy",
            }
        )
    return {
        "runner_api": "bounded_source_policy_runner_smoke",
        "runner_scope": "short_interval_source_shaped_candidate_rows",
        "unified_method_dispatch": True,
        "bounded_source_policy_runner_api_implemented": True,
        "bounded_source_policy_runner_smoke_implemented": True,
        "t_final": float(config.t_final),
        "comparison_h": [float(item) for item in config.comparison_h],
        "reference_h": float(config.reference_h),
        "axis": config.axis,
        "frictional": bool(config.frictional),
        "theta0": float(config.theta0),
        "omega0": float(config.omega0),
        "active_b2_candidate_row_smoke_implemented": True,
        "method_count": len(method_specs),
        "row_count": len(rows),
        "candidate_methods": [str(item["paper_method"]) for item in method_specs],
        "full_T10_source_policy_reproduction": False,
        "source_policy_rows_completed": 0,
        "source_policy_method_runner_equivalent": False,
        "source_policy_runner_equivalent": False,
        "rows": rows,
    }


def active_tfe_b2_candidate_row_smoke(
    *,
    t_final: float = 0.024,
    comparison_h: tuple[float, ...] = (0.012, 0.006, 0.003),
    reference_h: float = 0.0001,
    axis: str = "z",
) -> dict[str, object]:
    """Run the four active original-TFE B2 rows on a source-shaped grid.

    The active B2 rows are the original paper's single-pendulum Newmark-beta,
    TFE(m=1), TFE(m=2), and trapezoidal methods. This bounded smoke uses the
    source reference h=1e-4 and a short frictionless interval whose step sizes
    mirror the extracted source error-sweep scale. It is not the full T=10
    source-policy reproduction.
    """

    config = BoundedSourcePolicyRunnerConfig(
        theta0=0.0,
        omega0=0.0,
        t_final=t_final,
        comparison_h=comparison_h,
        reference_h=reference_h,
        axis=axis,
        frictional=False,
    )
    return bounded_source_policy_runner_smoke(config)


def active_tfe_b2_full_t10_coarse_candidate_probe(
    *,
    comparison_h: tuple[float, ...] = (0.1, 0.05, 0.025),
    reference_h: float = 0.0125,
    axis: str = "z",
) -> dict[str, object]:
    """Run a non-heavy full-horizon candidate probe for the active TFE rows.

    This uses the original TFE pendulum horizon, but deliberately keeps a
    coarse reference rather than invoking the extracted h=1e-4 source-policy
    reference campaign. It is useful for checking full-horizon feasibility and
    order behavior at large steps; it is not a source-policy reproduction.
    """

    config = BoundedSourcePolicyRunnerConfig(
        theta0=0.0,
        omega0=0.0,
        t_final=10.0,
        comparison_h=comparison_h,
        reference_h=reference_h,
        axis=axis,
        frictional=False,
    )
    result = bounded_source_policy_runner_smoke(config)
    rows = result["rows"]
    finite_rows = 0
    residual_ok_rows = 0
    velocity_decrease_rows = 0
    coordinate_decrease_rows = 0
    for row in rows:
        metrics = row.get("metrics", [])
        finite = all(
            np.isfinite(float(metric["coordinate_error_q"]))
            and np.isfinite(float(metric["velocity_error_v"]))
            and np.isfinite(float(metric["frobenius_error_norm_eta"]))
            for metric in metrics
        )
        finite_rows += int(finite)
        residual_ok_rows += int(float(row.get("max_newton_residual_norm", np.inf)) < 1.0e-8)
        velocity_decrease_rows += int(bool(row.get("velocity_error_decreased")))
        coordinate_decrease_rows += int(bool(row.get("coordinate_error_decreased")))
        row["accepted_use"] = "full_T10_coarse_candidate_probe_not_source_policy"
    result.update(
        {
            "runner_api": "active_tfe_b2_full_t10_coarse_candidate_probe",
            "runner_scope": "full_T10_large_step_candidate_probe",
            "full_T10_candidate_probe_completed": True,
            "full_T10_source_policy_reproduction": False,
            "source_policy_reference_h": 0.0001,
            "source_policy_reference_not_invoked": True,
            "default_1e_4_campaign_invoked": False,
            "source_policy_rows_completed": 0,
            "finite_row_count": finite_rows,
            "residual_ok_row_count": residual_ok_rows,
            "coordinate_error_decrease_row_count": coordinate_decrease_rows,
            "velocity_error_decrease_row_count": velocity_decrease_rows,
        }
    )
    return result


def active_tfe_b2_source_reference_full_t10_candidate_probe(
    *,
    comparison_h: tuple[float, ...] = (0.1, 0.05, 0.025),
    source_reference_h: float = 0.0001,
    axis: str = "z",
) -> dict[str, object]:
    """Run the active TFE B2 rows over T=10 against the h=1e-4 source reference.

    This closes the candidate-runner gap between the short active-B2 smoke and
    the full-horizon coarse probe. It deliberately remains outside the
    source-policy row contract because it does not reproduce the original
    absolute-coordinate DAE/source-code runner or accepted work-precision rows.
    """

    config = BoundedSourcePolicyRunnerConfig(
        theta0=0.0,
        omega0=0.0,
        t_final=10.0,
        comparison_h=comparison_h,
        reference_h=source_reference_h,
        axis=axis,
        frictional=False,
    )
    result = bounded_source_policy_runner_smoke(config)
    rows = result["rows"]
    finite_rows = 0
    residual_ok_rows = 0
    velocity_decrease_rows = 0
    coordinate_decrease_rows = 0
    for row in rows:
        metrics = row.get("metrics", [])
        finite = all(
            np.isfinite(float(metric["coordinate_error_q"]))
            and np.isfinite(float(metric["velocity_error_v"]))
            and np.isfinite(float(metric["frobenius_error_norm_eta"]))
            for metric in metrics
        )
        finite_rows += int(finite)
        residual_ok_rows += int(float(row.get("max_newton_residual_norm", np.inf)) < 1.0e-8)
        velocity_decrease_rows += int(bool(row.get("velocity_error_decreased")))
        coordinate_decrease_rows += int(bool(row.get("coordinate_error_decreased")))
        row["accepted_use"] = "full_T10_source_reference_candidate_probe_not_source_policy"
    result.update(
        {
            "runner_api": "active_tfe_b2_source_reference_full_t10_candidate_probe",
            "runner_scope": "full_T10_source_reference_active_b2_candidate_probe_not_source_policy",
            "full_T10_candidate_probe_completed": True,
            "full_T10_source_policy_reproduction": False,
            "source_policy_reference_h": float(source_reference_h),
            "source_policy_reference_invoked": True,
            "source_policy_reference_not_invoked": False,
            "default_1e_4_campaign_invoked": False,
            "source_policy_rows_completed": 0,
            "finite_row_count": finite_rows,
            "residual_ok_row_count": residual_ok_rows,
            "coordinate_error_decrease_row_count": coordinate_decrease_rows,
            "velocity_error_decrease_row_count": velocity_decrease_rows,
            "source_policy_method_runner_equivalent": False,
            "source_policy_runner_equivalent": False,
            "source_policy_dae_runner_equivalent": False,
        }
    )
    return result


def tfe_m3_gl_full_t10_coarse_formula_probe(
    *,
    comparison_h: tuple[float, ...] = (0.1, 0.05, 0.025),
    reference_h: float = 0.0125,
    axis: str = "z",
) -> dict[str, object]:
    """Run the Appendix-B m=3 Gauss-Lobatto formula over the full T=10 window.

    This is a coverage probe for the source-paper fifth-order formula target.
    It uses the same non-heavy full-horizon policy as the active B2 coarse
    candidate probe and deliberately remains outside source-policy closure.
    """

    method_specs = (
        {
            "paper_method": "tfe2026_TFE_m3_GL_formula_target",
            "source_method": "TFE_m3_GL",
            "expected_order": 5,
            "source_parameters": {"nu": 0.9, "nodes": "Gauss-Lobatto"},
        },
    )
    config = BoundedSourcePolicyRunnerConfig(
        theta0=0.0,
        omega0=0.0,
        t_final=10.0,
        comparison_h=comparison_h,
        reference_h=reference_h,
        axis=axis,
        frictional=False,
    )
    result = bounded_source_policy_runner_smoke(config, method_specs=method_specs)
    rows = result["rows"]
    finite_rows = 0
    residual_ok_rows = 0
    for row in rows:
        metrics = row.get("metrics", [])
        finite = all(
            np.isfinite(float(metric["coordinate_error_q"]))
            and np.isfinite(float(metric["velocity_error_v"]))
            and np.isfinite(float(metric["frobenius_error_norm_eta"]))
            for metric in metrics
        )
        finite_rows += int(finite)
        residual_ok_rows += int(float(row.get("max_newton_residual_norm", np.inf)) < 1.0e-8)
        row["accepted_use"] = "full_T10_m3_formula_probe_not_source_policy"
    result.update(
        {
            "runner_api": "tfe_m3_gl_full_t10_coarse_formula_probe",
            "runner_scope": "full_T10_m3_formula_probe_not_source_policy",
            "appendix_b_coefficient_certificate_required": True,
            "full_T10_formula_probe_completed": True,
            "full_T10_source_policy_reproduction": False,
            "source_policy_reference_h": 0.0001,
            "source_policy_reference_not_invoked": True,
            "default_1e_4_campaign_invoked": False,
            "source_policy_rows_completed": 0,
            "finite_row_count": finite_rows,
            "residual_ok_row_count": residual_ok_rows,
            "formal_expected_order": 5,
        }
    )
    return result
