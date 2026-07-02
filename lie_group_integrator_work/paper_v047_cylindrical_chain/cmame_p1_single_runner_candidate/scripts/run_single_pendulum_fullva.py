#!/usr/bin/env python3
"""Self-contained single-pendulum Gauss6/FullVA candidate runner.

This is a small NumPy-only extraction of the local single-pendulum
absolute-coordinate driven FullVA row. It intentionally covers only the
single-pendulum P1 slice. It does not import the v047 or v048 research runners
and it does not close source-policy or proof gates.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import time
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "results"

H_VALUES = (0.1, 0.05, 0.025)
T_FINAL = 0.1
STAGES = 3
STAGE_SIZE = 24
DIM = STAGES * STAGE_SIZE


def gauss3() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    s15 = math.sqrt(15.0)
    c = np.array([0.5 - s15 / 10.0, 0.5, 0.5 + s15 / 10.0], dtype=float)
    b = np.array([5.0 / 18.0, 4.0 / 9.0, 5.0 / 18.0], dtype=float)
    a = np.array(
        [
            [5.0 / 36.0, 2.0 / 9.0 - s15 / 15.0, 5.0 / 36.0 - s15 / 30.0],
            [5.0 / 36.0 + s15 / 24.0, 2.0 / 9.0, 5.0 / 36.0 - s15 / 24.0],
            [5.0 / 36.0 + s15 / 30.0, 2.0 / 9.0 + s15 / 15.0, 5.0 / 36.0],
        ],
        dtype=float,
    )
    return c, a, b


def skew(v: np.ndarray) -> np.ndarray:
    x, y, z = np.asarray(v, dtype=float)
    return np.array([[0.0, -z, y], [z, 0.0, -x], [-y, x, 0.0]], dtype=float)


def exp_so3(u: np.ndarray) -> np.ndarray:
    u = np.asarray(u, dtype=float)
    theta = float(np.linalg.norm(u))
    K = skew(u)
    if theta < 1.0e-12:
        return np.eye(3) + K + 0.5 * K @ K
    return np.eye(3) + math.sin(theta) / theta * K + (1.0 - math.cos(theta)) / (theta * theta) * K @ K


def log_so3(R: np.ndarray) -> np.ndarray:
    cos_theta = (float(np.trace(R)) - 1.0) * 0.5
    cos_theta = max(-1.0, min(1.0, cos_theta))
    theta = math.acos(cos_theta)
    vee = np.array([R[2, 1] - R[1, 2], R[0, 2] - R[2, 0], R[1, 0] - R[0, 1]], dtype=float)
    if theta < 1.0e-12:
        return 0.5 * vee
    return theta / (2.0 * math.sin(theta)) * vee


def right_jacobian_inverse_apply(u: np.ndarray, w: np.ndarray) -> np.ndarray:
    u = np.asarray(u, dtype=float)
    w = np.asarray(w, dtype=float)
    theta = float(np.linalg.norm(u))
    K = skew(u)
    if theta < 1.0e-8:
        Jinv = np.eye(3) + 0.5 * K + (1.0 / 12.0) * K @ K
    else:
        coeff = 1.0 / (theta * theta) - (1.0 + math.cos(theta)) / (2.0 * theta * math.sin(theta))
        Jinv = np.eye(3) + 0.5 * K + coeff * K @ K
    return Jinv @ w


def theta_ref(t: float) -> float:
    return 0.5 * math.pi + 0.25 * math.pi * math.cos(2.0 * t)


def theta_dot_ref(t: float) -> float:
    return -0.5 * math.pi * math.sin(2.0 * t)


def theta_ddot_ref(t: float) -> float:
    return -math.pi * math.cos(2.0 * t)


def single_rot(theta: float) -> np.ndarray:
    c = math.cos(theta)
    s = math.sin(theta)
    return np.array([[0.0, 0.0, 1.0], [-c, s, 0.0], [-s, -c, 0.0]], dtype=float)


def bar_mass_inertia(length: float = 4.0) -> tuple[float, float, float]:
    side = 0.05
    density = 7800.0
    mass = density * length * side * side
    j_length = (1.0 / 6.0) * mass * side * side
    j_transverse = (1.0 / 12.0) * mass * (side * side + length * length)
    return mass, j_length, j_transverse


def kinematic_state(theta: float, theta_dot: float, theta_ddot: float) -> dict[str, np.ndarray]:
    length_to_pivot = 2.0
    c = math.cos(theta)
    s = math.sin(theta)
    R = single_rot(theta)
    return {
        "r": np.array([0.0, -length_to_pivot * c, -length_to_pivot * s], dtype=float),
        "R": R,
        "v": np.array([0.0, length_to_pivot * s * theta_dot, -length_to_pivot * c * theta_dot], dtype=float),
        "a": np.array(
            [
                0.0,
                length_to_pivot * (c * theta_dot * theta_dot + s * theta_ddot),
                length_to_pivot * (s * theta_dot * theta_dot - c * theta_ddot),
            ],
            dtype=float,
        ),
        "w": np.array([0.0, 0.0, theta_dot], dtype=float),
        "alpha": np.array([0.0, 0.0, theta_ddot], dtype=float),
    }


def exact_state(t: float) -> dict[str, np.ndarray]:
    return kinematic_state(theta_ref(t), theta_dot_ref(t), theta_ddot_ref(t))


def reaction_dynamics(theta: float, theta_dot: float, theta_ddot: float) -> dict[str, np.ndarray | float]:
    state = kinematic_state(theta, theta_dot, theta_ddot)
    mass, j_length, j_transverse = bar_mass_inertia()
    J = np.diag([j_length, j_transverse, j_transverse])
    gravity = np.array([0.0, 0.0, -9.81])
    s_body = np.array([-2.0, 0.0, 0.0])
    R = state["R"]
    force = mass * (state["a"] - gravity)
    body_force = R.T @ force
    inertial_torque = J @ state["alpha"] + np.cross(state["w"], J @ state["w"])
    pivot_torque = np.cross(s_body, body_force)
    world_x = np.array([1.0, 0.0, 0.0])
    world_neg_z = np.array([0.0, 0.0, -1.0])
    body_x = np.array([1.0, 0.0, 0.0])
    body_y = np.array([0.0, 1.0, 0.0])
    torque_basis = np.column_stack(
        [
            np.cross(body_x, R.T @ world_x),
            np.cross(body_y, R.T @ world_x),
            np.cross(body_y, R.T @ world_neg_z),
        ]
    )
    multipliers, *_ = np.linalg.lstsq(torque_basis, inertial_torque - pivot_torque, rcond=None)
    return {
        "pivot_force": force,
        "axis_multipliers": multipliers[:2],
        "drive_multiplier": float(multipliers[2]),
    }


def unpack_stage(x: np.ndarray, index: int) -> dict[str, np.ndarray]:
    offset = STAGE_SIZE * index
    return {
        "u": x[offset : offset + 3],
        "r": x[offset + 3 : offset + 6],
        "v": x[offset + 6 : offset + 9],
        "w": x[offset + 9 : offset + 12],
        "a": x[offset + 12 : offset + 15],
        "alpha": x[offset + 15 : offset + 18],
        "lambda": x[offset + 18 : offset + 24],
    }


def stage_guess(state: dict[str, np.ndarray], t0: float, h: float) -> np.ndarray:
    c_nodes, _, _ = gauss3()
    R0 = state["R"]
    blocks: list[np.ndarray] = []
    for ci in c_nodes:
        t = t0 + float(ci) * h
        exact = exact_state(t)
        reaction = reaction_dynamics(theta_ref(t), theta_dot_ref(t), theta_ddot_ref(t))
        lam = np.concatenate(
            [
                np.asarray(reaction["pivot_force"], dtype=float),
                np.asarray(reaction["axis_multipliers"], dtype=float),
                np.array([float(reaction["drive_multiplier"])], dtype=float),
            ]
        )
        blocks.extend(
            [
                log_so3(R0.T @ exact["R"]),
                exact["r"],
                exact["v"],
                exact["w"],
                exact["a"],
                exact["alpha"],
                lam,
            ]
        )
    return np.concatenate(blocks)


def residual(x: np.ndarray, state: dict[str, np.ndarray], t0: float, h: float) -> np.ndarray:
    c_nodes, a_matrix, _ = gauss3()
    stages = [unpack_stage(x, i) for i in range(STAGES)]
    mass, j_length, j_transverse = bar_mass_inertia()
    J = np.diag([j_length, j_transverse, j_transverse])
    gravity = np.array([0.0, 0.0, -9.81])
    s_body = np.array([-2.0, 0.0, 0.0])
    world_x = np.array([1.0, 0.0, 0.0])
    world_neg_z = np.array([0.0, 0.0, -1.0])
    body_x = np.array([1.0, 0.0, 0.0])
    body_y = np.array([0.0, 1.0, 0.0])
    k = [right_jacobian_inverse_apply(st["u"], st["w"]) for st in stages]
    out: list[np.ndarray] = []
    for i, st in enumerate(stages):
        R = state["R"] @ exp_so3(st["u"])
        force = st["lambda"][:3]
        eta = st["lambda"][3:5]
        drive_lam = st["lambda"][5]
        axis0 = np.array([R[:, 0] @ world_x], dtype=float)
        axis1 = np.array([R[:, 1] @ world_x], dtype=float)
        drive_body_world = R.T @ world_neg_z
        drive_basis = np.cross(body_y, drive_body_world)
        drive_basis_dot = np.cross(body_y, -np.cross(st["w"], drive_body_world))
        axis_torque = eta[0] * np.cross(body_x, R.T @ world_x) + eta[1] * np.cross(body_y, R.T @ world_x)
        drive_torque = drive_lam * drive_basis
        pivot_velocity = st["v"] + R @ np.cross(st["w"], s_body)
        pivot_acceleration = st["a"] + R @ (
            np.cross(st["alpha"], s_body) + np.cross(st["w"], np.cross(st["w"], s_body))
        )
        t_stage = t0 + float(c_nodes[i]) * h
        ref_theta = theta_ref(t_stage)
        ref_dot = theta_dot_ref(t_stage)
        ref_ddot = theta_ddot_ref(t_stage)
        drive_acc = drive_basis_dot @ st["w"] + drive_basis @ st["alpha"]
        drive_acc += math.cos(ref_theta) * ref_dot * ref_dot + math.sin(ref_theta) * ref_ddot
        out.extend(
            [
                pivot_velocity,
                st["u"] - h * sum(float(a_matrix[i, j]) * k[j] for j in range(STAGES)),
                pivot_acceleration,
                st["w"] - state["w"] - h * sum(float(a_matrix[i, j]) * stages[j]["alpha"] for j in range(STAGES)),
                mass * st["a"] - mass * gravity - force,
                J @ st["alpha"] + np.cross(st["w"], J @ st["w"]) - np.cross(s_body, R.T @ force) - axis_torque - drive_torque,
                st["r"] + R @ s_body,
                np.array([axis0[0], axis1[0], drive_acc], dtype=float),
            ]
        )
    return np.concatenate(out)


def finite_difference_jacobian(x: np.ndarray, state: dict[str, np.ndarray], t0: float, h: float) -> np.ndarray:
    base = residual(x, state, t0, h)
    jac = np.empty((base.size, x.size), dtype=float)
    eps = 1.0e-7
    for j in range(x.size):
        step = eps * max(1.0, abs(float(x[j])))
        xp = x.copy()
        xp[j] += step
        jac[:, j] = (residual(xp, state, t0, h) - base) / step
    return jac


def solve_step(state: dict[str, np.ndarray], t0: float, h: float) -> tuple[dict[str, np.ndarray], int, dict[str, float]]:
    x = stage_guess(state, t0, h)
    last_norm = float("inf")
    for iteration in range(24):
        res = residual(x, state, t0, h)
        last_norm = float(np.linalg.norm(res))
        if last_norm < 1.0e-10:
            break
        jac = finite_difference_jacobian(x, state, t0, h)
        delta = np.linalg.solve(jac, -res)
        x = x + delta
        if float(np.linalg.norm(delta)) < 1.0e-12:
            last_norm = float(np.linalg.norm(residual(x, state, t0, h)))
            break
    else:
        raise RuntimeError(f"single-pendulum FullVA Newton solve failed: residual={last_norm:.3e}")

    _, _, b_weights = gauss3()
    stages = [unpack_stage(x, i) for i in range(STAGES)]
    k = [right_jacobian_inverse_apply(st["u"], st["w"]) for st in stages]
    r_next = state["r"] + h * sum(float(b_weights[i]) * stages[i]["v"] for i in range(STAGES))
    v_next = state["v"] + h * sum(float(b_weights[i]) * stages[i]["a"] for i in range(STAGES))
    u_next = h * sum(float(b_weights[i]) * k[i] for i in range(STAGES))
    R_next = state["R"] @ exp_so3(u_next)
    w_next = state["w"] + h * sum(float(b_weights[i]) * stages[i]["alpha"] for i in range(STAGES))
    diag = {
        "stage_residual_norm": last_norm,
        "max_trans_dynamics_residual": max(
            float(np.linalg.norm(bar_mass_inertia()[0] * st["a"] - bar_mass_inertia()[0] * np.array([0.0, 0.0, -9.81]) - st["lambda"][:3]))
            for st in stages
        ),
    }
    return {"r": r_next, "R": R_next, "v": v_next, "w": w_next}, iteration + 1, diag


def endpoint_errors(state: dict[str, np.ndarray], t: float) -> dict[str, float]:
    exact = exact_state(t)
    return {
        "position_l2_error": float(np.linalg.norm(state["r"] - exact["r"])),
        "velocity_l2_error": float(np.linalg.norm(state["v"] - exact["v"])),
        "orientation_error_rad": float(np.linalg.norm(log_so3(exact["R"].T @ state["R"]))),
        "omega_l2_error": float(np.linalg.norm(state["w"] - exact["w"])),
    }


def integrate(h: float, t_final: float) -> dict[str, float | int]:
    n_steps = int(round(t_final / h))
    if abs(n_steps * h - t_final) > 1.0e-12:
        raise ValueError("h must divide t_final")
    state = exact_state(0.0)
    total_newton = 0
    max_residual = 0.0
    for step in range(n_steps):
        state, niters, diag = solve_step(state, step * h, h)
        total_newton += niters
        max_residual = max(max_residual, float(diag["stage_residual_norm"]))
    errors = endpoint_errors(state, n_steps * h)
    return {
        "steps": n_steps,
        "total_newton_iterations": total_newton,
        "max_stage_residual_norm": max_residual,
        **errors,
    }


def observed_order(hs: list[float], errors: list[float]) -> float:
    values = [(h, e) for h, e in zip(hs, errors, strict=True) if np.isfinite(e) and e > 0.0]
    if len(values) < 2:
        return float("nan")
    x = np.log([item[0] for item in values])
    y = np.log([item[1] for item in values])
    slope, _ = np.polyfit(x, y, 1)
    return float(slope)


def run(out_dir: Path) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    hs: list[float] = []
    pos: list[float] = []
    vel: list[float] = []
    orient: list[float] = []
    omega: list[float] = []
    for h in H_VALUES:
        started = time.perf_counter()
        result = integrate(h, T_FINAL)
        runtime = time.perf_counter() - started
        hs.append(h)
        pos.append(float(result["position_l2_error"]))
        vel.append(float(result["velocity_l2_error"]))
        orient.append(float(result["orientation_error_rad"]))
        omega.append(float(result["omega_l2_error"]))
        rows.append(
            {
                "example": "single_pendulum",
                "method": "local_Gauss6_FullVA_single_only_candidate",
                "h": h,
                "t_end": T_FINAL,
                "steps": int(result["steps"]),
                "position_l2_error": float(result["position_l2_error"]),
                "velocity_l2_error": float(result["velocity_l2_error"]),
                "orientation_error_rad": float(result["orientation_error_rad"]),
                "omega_l2_error": float(result["omega_l2_error"]),
                "max_stage_residual_norm": float(result["max_stage_residual_norm"]),
                "total_newton_iterations": int(result["total_newton_iterations"]),
                "runtime_sec": runtime,
                "source_policy_external_superiority_allowed": False,
                "proof_gap_closed": False,
            }
        )

    orders = {
        "position_order": observed_order(hs, pos),
        "velocity_order": observed_order(hs, vel),
        "orientation_order": observed_order(hs, orient),
        "omega_order": observed_order(hs, omega),
    }
    for row in rows:
        row.update(orders)

    summary = {
        "schema": "cmame-p1-single-runner-candidate-v1",
        "status": "single_runner_candidate_not_p1_complete",
        "example": "single_pendulum",
        "h_values": list(H_VALUES),
        "t_final": T_FINAL,
        "rows": len(rows),
        "p1_single_only_ready": True,
        "p1_complete": False,
        "imports_v047_or_v048": False,
        "source_policy_external_superiority_allowed": False,
        "proof_gap_closed": False,
        **orders,
    }

    csv_path = out_dir / "single_pendulum_rows.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    (out_dir / "single_pendulum_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    summary = run(args.out_dir)
    ok = (
        summary["rows"] == 3
        and summary["p1_single_only_ready"] is True
        and summary["p1_complete"] is False
        and summary["source_policy_external_superiority_allowed"] is False
        and summary["proof_gap_closed"] is False
        and summary["position_order"] > 5.0
        and summary["velocity_order"] > 5.0
    )
    print("p1_single_runner_candidate=PASS" if ok else "p1_single_runner_candidate=FAIL")
    print("example=single_pendulum")
    print(f"rows={summary['rows']}")
    print(f"position_order={summary['position_order']:.6f}")
    print(f"velocity_order={summary['velocity_order']:.6f}")
    print(f"p1_single_only_ready={summary['p1_single_only_ready']}")
    print(f"p1_complete={summary['p1_complete']}")
    print(f"source_policy_external_superiority_allowed={summary['source_policy_external_superiority_allowed']}")
    print(f"local_runner_proof_gap_closed={summary['proof_gap_closed']}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
