"""Shared driver for the paper experiments E1–E7.

Imports the accepted Gauss6/FullVA step from `v047_cylindrical_chain_pipeline/run_v047.py`
(`gauss_step`, `make_params`, `initial_state`, ...) and adds what the experiments need on top:
trajectory recording, error measures against a fine reference on common output times, energy of
the chain, reference caching, order fits with a floor, and CSV/JSON/PNG writers.  Nothing here
calls the v047 campaign entry point.

Error measures (all at the coarse-grid output times `t_k = k h`, which are output times of the
reference because every `h` is an integer multiple of `h_ref`):

* position: Frobenius norm over bodies of `r - r_ref` (same as `run_v047.state_error`);
* orientation: maximum over bodies of the geodesic angle between the quaternions;
* velocity: Frobenius norm of `v - v_ref`; angular velocity: Frobenius norm of `w - w_ref`
  (body-frame angular velocities, as stored in the state).

`final_*` is the value at `t = T`, `linf_*` the maximum over all output times.
"""

from __future__ import annotations

import csv
import dataclasses
import json
import math
import os
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np

os.environ.setdefault("MPLCONFIGDIR", "/tmp/mplconfig")

HERE = Path(__file__).resolve().parent
NUMERICS = HERE.parent
V047_DIR = NUMERICS / "v047_cylindrical_chain_pipeline"
RESULTS = HERE / "results"
REFS = RESULTS / "refs"
if str(V047_DIR) not in sys.path:
    sys.path.insert(0, str(V047_DIR))

import run_v047 as v047  # noqa: E402

SOLVER = "dense_jacfwd_csr"
GRAVITY = np.array([0.0, 0.0, -9.81])

# The accepted implementation freezes the sliding direction n_1 of the second pair at t = 0 while its
# rotation axis a_1(q) moves with body 0; the implemented sliding row carries the factor n_1 . a_1(q),
# which reaches zero at t ~ 0.605 for the benchmark initial conditions.  The regular branch of the
# accepted method therefore ends there; the paper experiments use T = 0.5 (n_1 . a_1 >= 0.36).
T_REGULAR_BRANCH_END = 0.605

_orig_gl = v047.qp.gauss_legendre_coefficients
_orig_gl_jax = v047.qp._gauss_legendre_coefficients_jax


def _gl_with_midpoint(n_stages):
    if n_stages == 1:  # implicit midpoint = one-stage Gauss
        return np.array([0.5]), np.array([[0.5]]), np.array([1.0])
    return _orig_gl(n_stages)


def _gl_jax_with_midpoint(n_stages, dtype):
    if n_stages == 1:
        import jax.numpy as jnp
        return jnp.asarray([0.5], dtype=dtype), jnp.asarray([[0.5]], dtype=dtype), jnp.asarray([1.0], dtype=dtype)
    return _orig_gl_jax(n_stages, dtype)


v047.qp.gauss_legendre_coefficients = _gl_with_midpoint
v047.qp._gauss_legendre_coefficients_jax = _gl_jax_with_midpoint


def set_stages(k: int) -> None:
    """Switch the implementation to a k-stage Gauss method (k in {1, 2, 3}); 3 is the accepted method."""
    v047.N_STAGES = k
    v047.DIM = k * v047.STAGE_SIZE


def branch_factor(params, r: np.ndarray, p: np.ndarray) -> float:
    """n_1 . a_1(q): the factor multiplying the implemented sliding row of the second pair."""
    n1 = np.cross(params.joint_basis[1, 0], params.joint_basis[1, 1]); n1 = n1 / np.linalg.norm(n1)
    R0 = np.asarray(v047.qp.quat_to_rot(np.asarray(p[0], float)), float)
    return float(n1 @ (R0 @ np.asarray(params.axis_next[0], float)))


def empty_seeds() -> np.ndarray:
    return np.zeros((0, v047.N_STAGES * v047.STAGE_SIZE), dtype=float)


def smooth_params(stribeck_velocity: float = 0.5):
    return v047.make_params(stribeck_velocity)


def conservative_params(stribeck_velocity: float = 0.5):
    """Frictionless chain without external loads: total mechanical energy is conserved."""
    base = v047.make_params(stribeck_velocity)
    return dataclasses.replace(
        base, mu_s=0.0, mu_d=0.0, viscous_damping=0.0,
        external_forces_world=np.zeros_like(base.external_forces_world),
        external_torques_body=np.zeros_like(base.external_torques_body),
    )


@dataclass
class Trajectory:
    h: float
    t_final: float
    t: np.ndarray                      # (n+1,)
    r: np.ndarray                      # (n+1, bodies, 3)
    p: np.ndarray                      # (n+1, bodies, 4)
    v: np.ndarray                      # (n+1, bodies, 3)
    w: np.ndarray                      # (n+1, bodies, 3)
    newton_iterations: np.ndarray      # (n,)
    constraint_norm: np.ndarray        # (n,) endpoint position-level constraint norm
    velocity_constraint_norm: np.ndarray
    acc_position_constraint_norm: np.ndarray
    acc_orientation_constraint_norm: np.ndarray
    quaternion_unit_error: np.ndarray
    runtime_sec: float
    converged: bool
    failure: str = ""
    extra: dict[str, Any] = field(default_factory=dict)

    @property
    def steps(self) -> int:
        return len(self.t) - 1

    def state_at(self, k: int):
        return v047.State(r=self.r[k].copy(), p=self.p[k].copy(), v=self.v[k].copy(), w=self.w[k].copy())


def integrate_trajectory(params, h: float, t_final: float, project_velocity: bool = True,
                         solver: str = SOLVER, state0=None) -> Trajectory:
    """Fixed-step Gauss6/FullVA integration recording the endpoint state after every step."""
    state = state0 if state0 is not None else v047.project_endpoint_velocity(v047.initial_state(params), params)
    n_steps = int(round(t_final / h))
    seeds = empty_seeds()
    r = [np.asarray(state.r, float).copy()]; p = [np.asarray(state.p, float).copy()]
    v = [np.asarray(state.v, float).copy()]; w = [np.asarray(state.w, float).copy()]
    diag_keys = ["newton_iterations", "max_endpoint_constraint_norm", "max_endpoint_velocity_constraint_norm",
                 "max_stage_position_acceleration_constraint_norm", "max_stage_orientation_acceleration_constraint_norm",
                 "max_quaternion_unit_error"]
    diags: dict[str, list[float]] = {k: [] for k in diag_keys}
    converged, failure = True, ""
    started = time.perf_counter()
    for _ in range(n_steps):
        try:
            state, diag = v047.gauss_step(state, params, solver, None, seeds, h, project_velocity)
        except RuntimeError as exc:  # Newton failure
            converged, failure = False, str(exc)
            break
        for k in diag_keys:
            diags[k].append(float(diag[k]))
        r.append(np.asarray(state.r, float).copy()); p.append(np.asarray(state.p, float).copy())
        v.append(np.asarray(state.v, float).copy()); w.append(np.asarray(state.w, float).copy())
    runtime = time.perf_counter() - started
    n_done = len(r) - 1
    return Trajectory(
        h=h, t_final=t_final, t=np.arange(n_done + 1) * h, r=np.array(r), p=np.array(p), v=np.array(v), w=np.array(w),
        newton_iterations=np.array(diags["newton_iterations"]),
        constraint_norm=np.array(diags["max_endpoint_constraint_norm"]),
        velocity_constraint_norm=np.array(diags["max_endpoint_velocity_constraint_norm"]),
        acc_position_constraint_norm=np.array(diags["max_stage_position_acceleration_constraint_norm"]),
        acc_orientation_constraint_norm=np.array(diags["max_stage_orientation_acceleration_constraint_norm"]),
        quaternion_unit_error=np.array(diags["max_quaternion_unit_error"]),
        runtime_sec=runtime, converged=converged, failure=failure,
    )


def quaternion_angle(p: np.ndarray, q: np.ndarray) -> float:
    """Geodesic angle on SO(3) between unit quaternions, sign-insensitive.  Uses the chord length
    `min(|p - q|, |p + q|)` and `2 asin(chord / 2)`, which stays accurate for angles far below the
    1e-8 rad resolution floor of the `acos(p . q)` form."""
    p = np.asarray(p, float) / np.linalg.norm(p); q = np.asarray(q, float) / np.linalg.norm(q)
    chord = min(np.linalg.norm(p - q), np.linalg.norm(p + q))
    return 2.0 * math.asin(min(1.0, 0.5 * chord))


def compare(traj: Trajectory, ref: Trajectory) -> dict[str, float]:
    """Errors of `traj` against `ref` on the output times of `traj`."""
    ratio = traj.h / ref.h
    assert abs(ratio - round(ratio)) < 1e-9, f"h = {traj.h} is not a multiple of h_ref = {ref.h}"
    ratio = int(round(ratio))
    n = traj.steps
    idx = np.arange(n + 1) * ratio
    assert idx[-1] <= ref.steps, "reference trajectory shorter than the coarse trajectory"
    pos = np.array([np.linalg.norm(traj.r[k] - ref.r[idx[k]]) for k in range(n + 1)])
    vel = np.array([np.linalg.norm(traj.v[k] - ref.v[idx[k]]) for k in range(n + 1)])
    ang = np.array([np.linalg.norm(traj.w[k] - ref.w[idx[k]]) for k in range(n + 1)])
    ori = np.array([max(quaternion_angle(traj.p[k][b], ref.p[idx[k]][b]) for b in range(traj.p.shape[1])) for k in range(n + 1)])
    return {
        "final_position": float(pos[-1]), "final_orientation": float(ori[-1]), "final_velocity": float(vel[-1]), "final_angular_velocity": float(ang[-1]),
        "linf_position": float(pos.max()), "linf_orientation": float(ori.max()), "linf_velocity": float(vel.max()), "linf_angular_velocity": float(ang.max()),
    }


def energy(params, r: np.ndarray, p: np.ndarray, v: np.ndarray, w: np.ndarray) -> tuple[float, float]:
    """Kinetic and potential energy of the chain (body-frame angular velocity, gravity from params)."""
    kinetic = 0.0
    potential = 0.0
    g = np.asarray(params.gravity, float)
    for b in range(r.shape[0]):
        m = float(params.masses[b]); J = np.asarray(params.Js[b], float)
        kinetic += 0.5 * m * float(v[b] @ v[b]) + 0.5 * float(w[b] @ (J @ w[b]))
        potential += -m * float(g @ r[b])
    return kinetic, potential


def pairwise_orders(hs: list[float], errs: list[float]) -> list[float]:
    out = []
    for k in range(len(hs) - 1):
        e0, e1 = errs[k], errs[k + 1]
        out.append(float(math.log(e0 / e1) / math.log(hs[k] / hs[k + 1])) if e0 > 0 and e1 > 0 else float("nan"))
    return out


def fit_order(hs: list[float], errs: list[float], floor: float, factor: float = 100.0) -> tuple[float, int]:
    """Least-squares slope over the points whose error exceeds `factor * floor`."""
    pts = [(h, e) for h, e in zip(hs, errs) if np.isfinite(e) and e > factor * floor]
    if len(pts) < 2:
        return float("nan"), len(pts)
    hs_a = np.log([q[0] for q in pts]); es_a = np.log([q[1] for q in pts])
    return float(np.polyfit(hs_a, es_a, 1)[0]), len(pts)


def reference_path(name: str) -> Path:
    REFS.mkdir(parents=True, exist_ok=True)
    return REFS / f"{name}.npz"


def load_or_compute_reference(name: str, params, h: float, t_final: float, project_velocity: bool = True) -> Trajectory:
    path = reference_path(name)
    if path.exists():
        z = np.load(path)
        if abs(float(z["h"]) - h) < 1e-15 and abs(float(z["t_final"]) - t_final) < 1e-12:
            return Trajectory(h=h, t_final=t_final, t=z["t"], r=z["r"], p=z["p"], v=z["v"], w=z["w"],
                              newton_iterations=z["newton_iterations"], constraint_norm=z["constraint_norm"],
                              velocity_constraint_norm=z["velocity_constraint_norm"],
                              acc_position_constraint_norm=z["acc_position_constraint_norm"],
                              acc_orientation_constraint_norm=z["acc_orientation_constraint_norm"],
                              quaternion_unit_error=z["quaternion_unit_error"], runtime_sec=float(z["runtime_sec"]),
                              converged=bool(z["converged"]))
    traj = integrate_trajectory(params, h, t_final, project_velocity)
    if not traj.converged:
        raise RuntimeError(f"reference {name} failed: {traj.failure}")
    np.savez(path, h=h, t_final=t_final, t=traj.t, r=traj.r, p=traj.p, v=traj.v, w=traj.w,
             newton_iterations=traj.newton_iterations, constraint_norm=traj.constraint_norm,
             velocity_constraint_norm=traj.velocity_constraint_norm, acc_position_constraint_norm=traj.acc_position_constraint_norm,
             acc_orientation_constraint_norm=traj.acc_orientation_constraint_norm, quaternion_unit_error=traj.quaternion_unit_error,
             runtime_sec=traj.runtime_sec, converged=traj.converged)
    return traj


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    """Write rows with the union of all keys (first-seen order); missing cells are left empty."""
    if not rows:
        raise ValueError(f"refusing to write empty {path.name}")
    fields: list[str] = []
    for row in rows:
        fields.extend(k for k in row if k not in fields)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, restval="")
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, default=float) + "\n", encoding="utf-8")


def fmt(x: float) -> str:
    return f"{x:.3e}"
