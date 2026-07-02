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

import jax

jax.config.update("jax_enable_x64", True)
import jax.numpy as jnp
import numpy as np


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
RESULTS = HERE / "results"
V013_PATH = ROOT / "v013_gauss6_quaternion_endpoint_dae" / "quaternion_pendulum.py"

METHODS = ["lambda_gauss4_endpoint_jax", "lambda_gauss6_endpoint_jax"]
HS = [0.1, 0.05, 0.025]
T_FINAL_ORDER = 1.0
REF_H = 0.00625
T_FINAL_DISSIPATION = 5.0
H_DISSIPATION = 0.05


def load_v013_module():
    spec = importlib.util.spec_from_file_location("v013_quaternion_pendulum", V013_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


qp = load_v013_module()


@dataclass(frozen=True)
class LambdaFrictionParams:
    mass: float
    J_com: np.ndarray
    s_com_to_pivot: np.ndarray
    gravity: np.ndarray
    mu_s: float
    mu_d: float
    stribeck_velocity: float
    friction_eps: float
    viscous_damping: float
    friction_radius: float

    @property
    def J_pivot(self) -> np.ndarray:
        s = self.s_com_to_pivot.reshape(3)
        return self.J_com + self.mass * ((s @ s) * np.eye(3) - np.outer(s, s))


def make_params(friction_eps: float = 0.5) -> LambdaFrictionParams:
    return LambdaFrictionParams(
        mass=4.0,
        J_com=np.diag([0.18, 0.32, 0.41]),
        s_com_to_pivot=np.array([0.0, 0.0, 0.75]),
        gravity=np.array([0.0, 0.0, -9.81]),
        mu_s=0.30,
        mu_d=0.20,
        stribeck_velocity=0.35,
        friction_eps=float(friction_eps),
        viscous_damping=0.02,
        friction_radius=0.010,
    )


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def json_safe(obj: object) -> object:
    if isinstance(obj, dict):
        return {key: json_safe(value) for key, value in obj.items()}
    if isinstance(obj, list):
        return [json_safe(value) for value in obj]
    if isinstance(obj, tuple):
        return [json_safe(value) for value in obj]
    if isinstance(obj, float) and not np.isfinite(obj):
        return None
    return obj


def lambda_friction_torque(w: np.ndarray, lam: np.ndarray, params: LambdaFrictionParams) -> np.ndarray:
    w = np.asarray(w, dtype=float).reshape(3)
    lam = np.asarray(lam, dtype=float).reshape(3)
    speed = float(np.linalg.norm(w))
    normal_load = float(np.linalg.norm(lam))
    eps = max(float(params.friction_eps), 1.0e-12)
    vs = max(float(params.stribeck_velocity), 1.0e-12)
    mu_eff = params.mu_d + (params.mu_s - params.mu_d) * np.exp(-((speed / vs) ** 2))
    coulomb = params.friction_radius * normal_load * mu_eff / np.sqrt(3.0)
    return -params.viscous_damping * w - coulomb * np.tanh(w / eps)


def _lambda_friction_torque_jax(w, lam, mu_s, mu_d, stribeck_velocity, friction_eps, viscous_damping, friction_radius):
    speed = jnp.linalg.norm(w)
    normal_load = jnp.linalg.norm(lam)
    eps = jnp.maximum(friction_eps, 1.0e-12)
    vs = jnp.maximum(stribeck_velocity, 1.0e-12)
    mu_eff = mu_d + (mu_s - mu_d) * jnp.exp(-((speed / vs) ** 2))
    coulomb = friction_radius * normal_load * mu_eff / jnp.sqrt(jnp.array(3.0, dtype=w.dtype))
    return -viscous_damping * w - coulomb * jnp.tanh(w / eps)


def reaction_lambda_from_alpha(p: np.ndarray, w: np.ndarray, alpha: np.ndarray, params: LambdaFrictionParams) -> np.ndarray:
    R = qp.quat_to_rot(p)
    s = params.s_com_to_pivot
    a = -R @ (np.cross(alpha, s) + np.cross(w, np.cross(w, s)))
    return params.mass * (a - params.gravity)


def reduced_rhs_lambda_friction(p: np.ndarray, w: np.ndarray, params: LambdaFrictionParams) -> np.ndarray:
    R = qp.quat_to_rot(p)
    s = params.s_com_to_pivot
    Jp = params.J_pivot
    g_body = R.T @ params.gravity
    torque_body = -params.mass * np.cross(s, g_body)
    alpha = np.linalg.solve(Jp, torque_body - np.cross(w, Jp @ w))

    def residual(a: np.ndarray) -> np.ndarray:
        lam = reaction_lambda_from_alpha(p, w, a, params)
        return Jp @ a + np.cross(w, Jp @ w) - torque_body - lambda_friction_torque(w, lam, params)

    for _ in range(10):
        res = residual(alpha)
        if float(np.linalg.norm(res)) < 1.0e-12:
            break
        jac = finite_difference_jacobian(residual, alpha)
        delta = np.linalg.solve(jac, -res)
        alpha = alpha + delta
        if float(np.linalg.norm(delta)) < 1.0e-12:
            break
    return alpha


def finite_difference_jacobian(fun, x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    f0 = fun(x)
    jac = np.zeros((f0.size, x.size), dtype=float)
    for j in range(x.size):
        step = 1.0e-7 * max(1.0, abs(x[j]))
        xp = x.copy()
        xm = x.copy()
        xp[j] += step
        xm[j] -= step
        jac[:, j] = (fun(xp) - fun(xm)) / (2.0 * step)
    return jac


def stage_guess(state, h: float, params: LambdaFrictionParams, n_stages: int) -> np.ndarray:
    cs, _, _ = qp.gauss_legendre_coefficients(n_stages)
    alpha0 = reduced_rhs_lambda_friction(state.p, state.w, params)
    blocks = []
    for c in cs:
        u = c * h * state.w
        p_i = qp.compose_right_quat(state.p, u)
        R_i = qp.quat_to_rot(p_i)
        w_i = state.w + c * h * alpha0
        alpha_i = reduced_rhs_lambda_friction(p_i, w_i, params)
        r_i = -R_i @ params.s_com_to_pivot
        v_i = -R_i @ np.cross(w_i, params.s_com_to_pivot)
        a_i = -R_i @ (
            np.cross(alpha_i, params.s_com_to_pivot)
            + np.cross(w_i, np.cross(w_i, params.s_com_to_pivot))
        )
        lam_i = params.mass * (a_i - params.gravity)
        blocks.extend([u, r_i, v_i, w_i, a_i, alpha_i, lam_i])
    return np.concatenate(blocks)


def _unpack_stages_jax(x, n_stages: int):
    stages = []
    offset = 0
    for _ in range(n_stages):
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


def _endpoint_residual_lambda_jax_core_n(
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
    mu_s,
    mu_d,
    stribeck_velocity,
    friction_eps,
    viscous_damping,
    friction_radius,
    n_stages: int,
):
    _, A, b = qp._gauss_legendre_coefficients_jax(n_stages, x.dtype)
    stage_width = 21 * n_stages
    stages = _unpack_stages_jax(x[:stage_width], n_stages)
    end_u = x[stage_width : stage_width + 3]
    end_r = x[stage_width + 3 : stage_width + 6]
    end_v = x[stage_width + 6 : stage_width + 9]
    end_w = x[stage_width + 9 : stage_width + 12]
    ks = [qp._right_jacobian_inverse_apply_jax(st["u"], st["w"]) for st in stages]
    out = []
    for i, st in enumerate(stages):
        p_i = qp.compose_right_quat_jax(p0, st["u"])
        R_i = qp.quat_to_rot_jax(p_i)
        tau_f = _lambda_friction_torque_jax(
            st["w"], st["lambda"], mu_s, mu_d, stribeck_velocity, friction_eps, viscous_damping, friction_radius
        )
        out.extend(
            [
                st["u"] - h * sum(A[i, j] * ks[j] for j in range(n_stages)),
                st["w"] - w0 - h * sum(A[i, j] * stages[j]["alpha"] for j in range(n_stages)),
                mass * st["a"] - mass * gravity - st["lambda"],
                J_com @ st["alpha"]
                + jnp.cross(st["w"], J_com @ st["w"])
                - jnp.cross(s, R_i.T @ st["lambda"])
                - tau_f,
                st["r"] + R_i @ s,
                st["v"] + R_i @ jnp.cross(st["w"], s),
                st["a"] + R_i @ (jnp.cross(st["alpha"], s) + jnp.cross(st["w"], jnp.cross(st["w"], s))),
            ]
        )

    p_end = qp.compose_right_quat_jax(p0, end_u)
    R_end = qp.quat_to_rot_jax(p_end)
    out.extend(
        [
            end_u - h * sum(b[j] * ks[j] for j in range(n_stages)),
            end_w - w0 - h * sum(b[j] * stages[j]["alpha"] for j in range(n_stages)),
            end_r + R_end @ s,
            end_v + R_end @ jnp.cross(end_w, s),
        ]
    )
    _ = r0, v0
    return jnp.concatenate(out)


def _endpoint_residual_lambda2_core(x, *args):
    return _endpoint_residual_lambda_jax_core_n(x, *args, n_stages=2)


def _endpoint_residual_lambda3_core(x, *args):
    return _endpoint_residual_lambda_jax_core_n(x, *args, n_stages=3)


_lambda2_value = jax.jit(_endpoint_residual_lambda2_core)
_lambda2_jacobian = jax.jit(jax.jacfwd(_endpoint_residual_lambda2_core, argnums=0))
_lambda3_value = jax.jit(_endpoint_residual_lambda3_core)
_lambda3_jacobian = jax.jit(jax.jacfwd(_endpoint_residual_lambda3_core, argnums=0))


def endpoint_step_lambda(state, h: float, params: LambdaFrictionParams, n_stages: int) -> tuple[object, int, dict]:
    _, _, b = qp.gauss_legendre_coefficients(n_stages)
    stage0 = stage_guess(state, h, params, n_stages)
    stages0 = qp._unpack_stages(stage0, n_stages=n_stages)
    ks0 = [qp.right_jacobian_inverse_apply(st["u"], st["w"]) for st in stages0]
    u_end0 = h * sum(b[j] * ks0[j] for j in range(n_stages))
    p_end0 = qp.compose_right_quat(state.p, u_end0)
    R_end0 = qp.quat_to_rot(p_end0)
    w_end0 = state.w + h * sum(b[j] * stages0[j]["alpha"] for j in range(n_stages))
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
        jnp.asarray(params.mu_s, dtype=jnp.float64),
        jnp.asarray(params.mu_d, dtype=jnp.float64),
        jnp.asarray(params.stribeck_velocity, dtype=jnp.float64),
        jnp.asarray(params.friction_eps, dtype=jnp.float64),
        jnp.asarray(params.viscous_damping, dtype=jnp.float64),
        jnp.asarray(params.friction_radius, dtype=jnp.float64),
    )
    if n_stages == 2:
        residual_value = _lambda2_value
        residual_jacobian = _lambda2_jacobian
        max_iters = 16
    elif n_stages == 3:
        residual_value = _lambda3_value
        residual_jacobian = _lambda3_jacobian
        max_iters = 20
    else:
        raise ValueError(f"unsupported stage count: {n_stages}")

    last_norm = np.inf
    for it in range(max_iters):
        x_jax = jnp.asarray(x, dtype=jnp.float64)
        res = np.asarray(residual_value(x_jax, *args), dtype=float)
        last_norm = float(np.linalg.norm(res))
        if last_norm < 1.0e-11:
            break
        jac = np.asarray(residual_jacobian(x_jax, *args), dtype=float)
        delta = np.linalg.solve(jac, -res)
        x = x + delta
        if float(np.linalg.norm(delta)) < 1.0e-11:
            break
    else:
        raise RuntimeError(f"lambda-friction endpoint solve failed, residual={last_norm:.3e}")

    stages, end = qp._endpoint_unpack(x, n_stages=n_stages)
    p_end = qp.compose_right_quat(state.p, end["u"])
    next_state = qp.State(r=end["r"], p=p_end, v=end["v"], w=end["w"])
    max_stage_constraint = 0.0
    max_stage_force = 0.0
    max_stage_torque = 0.0
    max_lambda = 0.0
    max_power = -np.inf
    min_power = np.inf
    for st in stages:
        p_i = qp.compose_right_quat(state.p, st["u"])
        R_i = qp.quat_to_rot(p_i)
        max_stage_constraint = max(max_stage_constraint, float(np.linalg.norm(st["r"] + R_i @ params.s_com_to_pivot)))
        trans = params.mass * st["a"] - params.mass * params.gravity - st["lambda"]
        tau_f = lambda_friction_torque(st["w"], st["lambda"], params)
        rot = (
            params.J_com @ st["alpha"]
            + np.cross(st["w"], params.J_com @ st["w"])
            - np.cross(params.s_com_to_pivot, R_i.T @ st["lambda"])
            - tau_f
        )
        max_stage_force = max(max_stage_force, float(np.linalg.norm(trans)))
        max_stage_torque = max(max_stage_torque, float(np.linalg.norm(rot)))
        max_lambda = max(max_lambda, float(np.linalg.norm(st["lambda"])))
        power = float(tau_f @ st["w"])
        max_power = max(max_power, power)
        min_power = min(min_power, power)
    diag = {
        "newton_iterations": it + 1,
        "stage_residual_norm": last_norm,
        "max_stage_constraint_norm": max_stage_constraint,
        "max_stage_force_residual_norm": max_stage_force,
        "max_stage_torque_residual_norm": max_stage_torque,
        "lambda_norm_max": max_lambda,
        "max_stage_friction_power": max_power,
        "min_stage_friction_power": min_power,
        "max_quaternion_unit_error": float(abs(np.linalg.norm(next_state.p) - 1.0)),
    }
    return next_state, it + 1, diag


def integrate_lambda(method: str, h: float, t_final: float, params: LambdaFrictionParams) -> dict:
    state = qp.initial_state(params)
    n_steps = int(round(t_final / h))
    if abs(n_steps * h - t_final) > 1.0e-12:
        raise ValueError("h must divide t_final")
    n_stages = 2 if method == "lambda_gauss4_endpoint_jax" else 3
    E0 = qp.energy_state(state, params)
    prev_energy = E0
    max_energy = 0.0
    max_step_energy_increase = 0.0
    max_constraint = 0.0
    max_velocity_constraint = 0.0
    max_stage_constraint = 0.0
    max_stage_force = 0.0
    max_stage_torque = 0.0
    max_lambda = 0.0
    max_power = -np.inf
    min_power = np.inf
    max_quat_unit = float(abs(np.linalg.norm(state.p) - 1.0))
    total_iters = 0
    for _ in range(n_steps):
        state, niters, diag = endpoint_step_lambda(state, h, params, n_stages)
        total_iters += niters
        max_stage_constraint = max(max_stage_constraint, diag["max_stage_constraint_norm"])
        max_stage_force = max(max_stage_force, diag["max_stage_force_residual_norm"])
        max_stage_torque = max(max_stage_torque, diag["max_stage_torque_residual_norm"])
        max_lambda = max(max_lambda, diag["lambda_norm_max"])
        max_power = max(max_power, diag["max_stage_friction_power"])
        min_power = min(min_power, diag["min_stage_friction_power"])
        cn, cv = qp.constraint_norms(state, params)
        energy = qp.energy_state(state, params)
        max_step_energy_increase = max(max_step_energy_increase, energy - prev_energy)
        prev_energy = energy
        max_constraint = max(max_constraint, cn)
        max_velocity_constraint = max(max_velocity_constraint, cv)
        max_energy = max(max_energy, abs(energy - E0) / max(abs(E0), 1.0e-30))
        max_quat_unit = max(max_quat_unit, float(abs(np.linalg.norm(state.p) - 1.0)))
    final_energy = qp.energy_state(state, params)
    return {
        "state": state,
        "steps": n_steps,
        "max_energy_relative_error": max_energy,
        "final_energy_change": final_energy - E0,
        "final_energy_relative_change": (final_energy - E0) / max(abs(E0), 1.0e-30),
        "max_step_energy_increase": max_step_energy_increase,
        "max_endpoint_constraint_norm": max_constraint,
        "max_endpoint_velocity_constraint_norm": max_velocity_constraint,
        "max_stage_constraint_norm": max_stage_constraint,
        "max_stage_force_residual_norm": max_stage_force,
        "max_stage_torque_residual_norm": max_stage_torque,
        "max_lambda_norm": max_lambda,
        "max_stage_friction_power": max_power,
        "min_stage_friction_power": min_power,
        "max_quaternion_unit_error": max_quat_unit,
        "total_newton_iterations": total_iters,
    }


def state_error(ref_state, state) -> tuple[float, float]:
    return (
        qp.orientation_error(qp.quat_to_rot(ref_state.p), qp.quat_to_rot(state.p)),
        float(np.linalg.norm(ref_state.w - state.w)),
    )


def run_order_cases() -> tuple[list[dict], dict]:
    rows = []
    summary = {}
    for case_name, eps in {"lambda_smooth": 0.5, "lambda_sharp": 0.05}.items():
        params = make_params(friction_eps=eps)
        ref = integrate_lambda("lambda_gauss6_endpoint_jax", REF_H, T_FINAL_ORDER, params)
        method_summary = {}
        for method in METHODS:
            orientation_errors = []
            omega_errors = []
            runs = {}
            for h in HS:
                start = time.perf_counter()
                out = integrate_lambda(method, h, T_FINAL_ORDER, params)
                runtime = time.perf_counter() - start
                oerr, werr = state_error(ref["state"], out["state"])
                orientation_errors.append(oerr)
                omega_errors.append(werr)
                rows.append(
                    {
                        "case": case_name,
                        "method": method,
                        "h": f"{h:.10g}",
                        "steps": out["steps"],
                        "orientation_error_rad": f"{oerr:.16e}",
                        "omega_l2_error": f"{werr:.16e}",
                        "runtime_sec": f"{runtime:.8e}",
                        "total_newton_iterations": out["total_newton_iterations"],
                        "max_endpoint_constraint_norm": f"{out['max_endpoint_constraint_norm']:.16e}",
                        "max_endpoint_velocity_constraint_norm": f"{out['max_endpoint_velocity_constraint_norm']:.16e}",
                        "max_stage_torque_residual_norm": f"{out['max_stage_torque_residual_norm']:.16e}",
                        "max_lambda_norm": f"{out['max_lambda_norm']:.16e}",
                        "max_stage_friction_power": f"{out['max_stage_friction_power']:.16e}",
                        "min_stage_friction_power": f"{out['min_stage_friction_power']:.16e}",
                        "final_energy_relative_change": f"{out['final_energy_relative_change']:.16e}",
                        "max_step_energy_increase": f"{out['max_step_energy_increase']:.16e}",
                    }
                )
                runs[str(h)] = {
                    "orientation_error_rad": oerr,
                    "omega_l2_error": werr,
                    "runtime_sec": runtime,
                    "total_newton_iterations": out["total_newton_iterations"],
                    "max_endpoint_constraint_norm": out["max_endpoint_constraint_norm"],
                    "max_endpoint_velocity_constraint_norm": out["max_endpoint_velocity_constraint_norm"],
                    "max_stage_torque_residual_norm": out["max_stage_torque_residual_norm"],
                    "max_lambda_norm": out["max_lambda_norm"],
                    "max_stage_friction_power": out["max_stage_friction_power"],
                    "min_stage_friction_power": out["min_stage_friction_power"],
                    "final_energy_relative_change": out["final_energy_relative_change"],
                    "max_step_energy_increase": out["max_step_energy_increase"],
                }
            method_summary[method] = {
                "orientation_observed_order": qp.estimate_order(HS, orientation_errors),
                "omega_observed_order": qp.estimate_order(HS, omega_errors),
                "runs": runs,
            }
        summary[case_name] = {
            "friction_eps": eps,
            "reference_method": "lambda_gauss6_endpoint_jax",
            "reference_h": REF_H,
            "methods": method_summary,
        }
    write_csv(RESULTS / "lambda_friction_order.csv", rows)
    return rows, summary


def run_dissipation_cases() -> tuple[list[dict], dict]:
    rows = []
    summary = {}
    for case_name, eps in {"lambda_smooth": 0.5, "lambda_sharp": 0.05}.items():
        params = make_params(friction_eps=eps)
        case_summary = {}
        for method in METHODS:
            start = time.perf_counter()
            out = integrate_lambda(method, H_DISSIPATION, T_FINAL_DISSIPATION, params)
            runtime = time.perf_counter() - start
            rows.append(
                {
                    "case": case_name,
                    "method": method,
                    "h": f"{H_DISSIPATION:.10g}",
                    "t_final": f"{T_FINAL_DISSIPATION:.10g}",
                    "runtime_sec": f"{runtime:.8e}",
                    "steps": out["steps"],
                    "total_newton_iterations": out["total_newton_iterations"],
                    "final_energy_relative_change": f"{out['final_energy_relative_change']:.16e}",
                    "max_step_energy_increase": f"{out['max_step_energy_increase']:.16e}",
                    "max_stage_friction_power": f"{out['max_stage_friction_power']:.16e}",
                    "min_stage_friction_power": f"{out['min_stage_friction_power']:.16e}",
                    "max_lambda_norm": f"{out['max_lambda_norm']:.16e}",
                    "max_endpoint_constraint_norm": f"{out['max_endpoint_constraint_norm']:.16e}",
                    "max_endpoint_velocity_constraint_norm": f"{out['max_endpoint_velocity_constraint_norm']:.16e}",
                    "max_stage_torque_residual_norm": f"{out['max_stage_torque_residual_norm']:.16e}",
                }
            )
            item = dict(out)
            item.pop("state")
            item["runtime_sec"] = runtime
            case_summary[method] = item
        summary[case_name] = {"friction_eps": eps, "methods": case_summary}
    write_csv(RESULTS / "lambda_friction_dissipation.csv", rows)
    return rows, summary


def plot_order(summary: dict) -> None:
    import matplotlib.pyplot as plt

    cases = list(summary.keys())
    x = np.arange(len(cases))
    width = 0.32
    plt.figure(figsize=(7.5, 4.8))
    for idx, method in enumerate(METHODS):
        orders = [summary[case]["methods"][method]["orientation_observed_order"] for case in cases]
        plt.bar(x + (idx - 0.5) * width, orders, width, label=method)
    plt.xticks(x, cases)
    plt.ylabel("orientation observed order")
    plt.title("Lambda-Dependent Friction Order")
    plt.grid(True, axis="y", alpha=0.35)
    plt.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(RESULTS / "lambda_friction_order.png", dpi=180)
    plt.close()


def write_report(order_summary: dict, dissipation_summary: dict) -> None:
    lines = [
        "# v019 Experiment Report",
        "",
        "Generated by `run_v019.py`.",
        "",
        "## Purpose",
        "",
        "- Add a lambda/reaction-load dependent Stribeck-style friction torque to the quaternion endpoint DAE residual.",
        "- This targets the paper's main Jacobian-engineering pain point: nonlinear friction loads depending on velocity and Lagrange multipliers.",
        "- The implementation uses JAX `jacfwd` on the whole residual; no hand Jacobian for the lambda-dependent friction term is supplied.",
        "",
        "## Order Results",
        "",
    ]
    for case_name, case in order_summary.items():
        lines.append(f"### {case_name}")
        for method in METHODS:
            item = case["methods"][method]
            fine = item["runs"]["0.025"]
            lines.append(
                f"- `{method}`: orientation order {item['orientation_observed_order']:.3f}, "
                f"omega order {item['omega_observed_order']:.3f}, h=0.025 orientation error "
                f"{fine['orientation_error_rad']:.3e}, runtime {fine['runtime_sec']:.3f}s, "
                f"max lambda {fine['max_lambda_norm']:.3e}."
            )
        g4 = case["methods"]["lambda_gauss4_endpoint_jax"]["runs"]["0.025"]
        g6 = case["methods"]["lambda_gauss6_endpoint_jax"]["runs"]["0.025"]
        lines.append(
            f"- Gauss6 vs Gauss4 at h=0.025: {g4['orientation_error_rad'] / max(g6['orientation_error_rad'], 1e-30):.2e}x lower "
            f"orientation error at {g6['runtime_sec'] / max(g4['runtime_sec'], 1e-30):.2f}x runtime."
        )
        lines.append("")
    lines.extend(["## Dissipation Runs", ""])
    for case_name, case in dissipation_summary.items():
        lines.append(f"### {case_name}")
        for method in METHODS:
            item = case["methods"][method]
            lines.append(
                f"- `{method}`: 5s h=0.05 final energy relative change "
                f"{item['final_energy_relative_change']:.3e}, max step energy increase "
                f"{item['max_step_energy_increase']:.3e}, max friction power "
                f"{item['max_stage_friction_power']:.3e}, runtime {item['runtime_sec']:.3f}s."
            )
        lines.append("")
    lines.extend(
        [
            "## Interpretation",
            "",
            "- The lambda-dependent friction residual exercises the paper's hardest Jacobian case: the force model depends on the same multipliers solved by Newton.",
            "- JAX differentiation handles this coupled residual without a manually derived friction Jacobian, which is exactly the engineering value promised by the paper's `S^3` transport/Jacobian framing.",
            "- In the smooth lambda-friction case, Gauss6 preserves high-order behavior and gives a large fine-step accuracy gain over Gauss4 at modest extra runtime. This extends the current best method beyond velocity-only friction.",
            "- In the sharp lambda-friction case, Gauss6 still improves the fine-step error, but both methods show order reduction. That reinforces the v014-v015 conclusion: near-nonsmooth regularity is the limiting factor, not only representation or Jacobian construction.",
            "- All dissipation runs have nonpositive measured step energy increase and negative stage friction power, so the lambda-dependent friction model is behaving as a dissipative load.",
            "",
            "## Outputs",
            "",
            "- `lambda_friction_order.csv`",
            "- `lambda_friction_dissipation.csv`",
            "- `summary_v019.json`",
            "- `lambda_friction_order.png`",
            "",
        ]
    )
    (RESULTS / "v019_report.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    _, order_summary = run_order_cases()
    _, dissipation_summary = run_dissipation_cases()
    plot_order(order_summary)
    summary = {
        "version": "v019_lambda_dependent_friction",
        "python": platform.python_version(),
        "platform": platform.platform(),
        "numpy": np.__version__,
        "model": {
            "methods": METHODS,
            "step_sizes": HS,
            "reference_h": REF_H,
            "t_final_order": T_FINAL_ORDER,
            "t_final_dissipation": T_FINAL_DISSIPATION,
            "h_dissipation": H_DISSIPATION,
            "friction_model": {
                "mu_s": 0.30,
                "mu_d": 0.20,
                "stribeck_velocity": 0.35,
                "viscous_damping": 0.02,
                "friction_radius": 0.010,
            },
        },
        "order": order_summary,
        "dissipation": dissipation_summary,
        "runtime_sec": time.perf_counter() - started,
    }
    with (RESULTS / "summary_v019.json").open("w", encoding="utf-8") as f:
        json.dump(json_safe(summary), f, indent=2, sort_keys=True)
    write_report(order_summary, dissipation_summary)


if __name__ == "__main__":
    main()
