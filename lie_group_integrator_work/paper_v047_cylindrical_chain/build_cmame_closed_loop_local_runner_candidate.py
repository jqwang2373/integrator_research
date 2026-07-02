#!/usr/bin/env python3
"""Build an executable closed-loop local runner candidate for B6."""

from __future__ import annotations

import ast
import csv
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


PAPER = Path(__file__).resolve().parent
ROOT = PAPER.parent
SBEL = ROOT.parent / "external" / "sbel-reproducibility" / "2021" / "ASME" / "rA-formulation" / "C2"
V048 = ROOT / "v048_cross_paper_same_test_benchmarks"
CANDIDATE = PAPER / "cmame_closed_loop_local_runner_candidate"
OUT_JSON = PAPER / "CMAME_CLOSED_LOOP_LOCAL_RUNNER_CANDIDATE_MANIFEST.json"
OUT_MD = PAPER / "CMAME_CLOSED_LOOP_LOCAL_RUNNER_CANDIDATE_MANIFEST.md"
PYTHON_LINE_LIMIT = 2000

VENDOR_FILES = [
    ("SimEngineMBD/example_models/models/four_link.json", "vendor/SimEngineMBD/example_models/models/four_link.json"),
    ("SimEngineMBD/example_models/models/slider_crank.json", "vendor/SimEngineMBD/example_models/models/slider_crank.json"),
    ("SimEngineMBD/rA/gcons_ra.py", "vendor/SimEngineMBD/rA/gcons_ra.py"),
    ("SimEngineMBD/utils/systems.py", "vendor/SimEngineMBD/utils/systems.py"),
]


COMPACT_PHYSICS = r'''"""Compact rA-only physics helpers derived from public SBEL SimEngineMBD."""

from __future__ import annotations

import logging
from collections import namedtuple
from enum import Enum, auto

import numpy as np
import sympy as sp


I3 = np.identity(3)
X_AXIS = np.array([[1], [0], [0]])
Y_AXIS = np.array([[0], [1], [0]])
Z_AXIS = np.array([[0], [0], [1]])
BDFVals = namedtuple("BDFVals", ["β", "α"])
bdf1 = BDFVals(β=1, α=[-1, 1, 0])
bdf2 = BDFVals(β=2 / 3, α=[-1, 4 / 3, -1 / 3])


class Constraints(Enum):
    DP1 = auto()
    DP2 = auto()
    D = auto()
    CD = auto()
    EULER = auto()


class SolverType(Enum):
    KINEMATICS = auto()
    DYNAMICS = auto()


def check_vector(v, n):
    if v.shape == (1, n):
        logging.warning("Input was a row vector, automatically transposed it")
        return v.T
    if v.shape != (n, 1):
        raise ValueError(f"Input vector v did not have dimension {n}")
    return v


def check_unit_vector(k, n):
    k = check_vector(k, n)
    norm = np.linalg.norm(k)
    if abs(norm - 1) > 1.0e-6:
        raise ValueError("k was not a unit vector")
    return k


def check_SO3(mat):
    if mat.shape != (3, 3):
        raise ValueError("Non 3x3 matrix passed to check_SO3")
    det_diff = abs(np.linalg.det(mat) - 1)
    if det_diff > 1.0e-1:
        raise ValueError(f"Matrix was non-orthogonal: |det(mat) -1| = {det_diff}")
    if det_diff > 1.0e-2:
        logging.warning("|det(mat) -1| = " + str(det_diff))


def skew(v):
    v = check_vector(v, 3)
    return np.array([[0, -v[2, 0], v[1, 0]], [v[2, 0], 0, -v[0, 0]], [-v[1, 0], v[0, 0], 0]])


def cross_vec(mat):
    return np.array([[mat[2, 1]], [mat[0, 2]], [mat[1, 0]]])


def R(u, chi):
    u = check_unit_vector(u, 3)
    return np.cos(chi) * I3 + (1 - np.cos(chi)) * (u @ u.T) + np.sin(chi) * skew(u)


def exp(mat):
    v = cross_vec(mat)
    norm = np.linalg.norm(v)
    return I3 if norm == 0 else R(v / norm, norm)


def block_mat(mats):
    rows, cols = np.shape(mats[0])
    out = np.zeros((rows * len(mats), cols * len(mats)))
    for i, mat in enumerate(mats):
        out[rows * i : rows * (i + 1), cols * i : cols * (i + 1)] = mat
    return out


def generate_sympy_constraint(f_sym, var):
    df_sym = sp.diff(f_sym, var)
    ddf_sym = sp.diff(df_sym, var)
    return sp.lambdify(var, f_sym), sp.lambdify(var, df_sym), sp.lambdify(var, ddf_sym)


def create_col_slice(i_id, j_id, dim):
    if i_id is None:
        return dim * j_id + np.arange(0, dim)
    if j_id is None:
        return dim * i_id + np.arange(0, dim)
    return np.concatenate((dim * i_id + np.arange(0, dim), dim * j_id + np.arange(0, dim)))
'''


COMPACT_SYSTEM_RA = r'''"""Compact rA-only SystemRA derived from public SBEL SimEngineMBD."""

from __future__ import annotations

import logging

import numpy as np

from .gcons_ra import Body, CD, ConGroup, Constraints, D, DP1, DP2
from ..utils.physics import SolverType, Z_AXIS, block_mat
from ..utils.systems import read_model_file


class SystemRA:
    def __init__(self, bodies, constraints):
        self.bodies = bodies
        self.g_cons = constraints
        self.solver_type = SolverType.KINEMATICS
        self.solver_order = 1
        self.nc = self.g_cons.nc
        self.nb = self.g_cons.nb
        if self.nb != len(self.bodies):
            raise ValueError("Mismatch on number of bodies")
        self.g_acc = np.zeros((3, 1))
        self.is_initialized = False
        self.h = 1e-3
        self.tol = None
        self.max_iters = 50
        self.k = 0
        self.M = np.zeros((3 * self.nb, 3 * self.nb))
        self.J = np.zeros((3 * self.nb, 3 * self.nb))
        self.F_ext = np.zeros((3 * self.nb, 1))
        self.Φ = np.zeros((self.nc, 1))
        self.Φ_r = np.zeros((self.nc, 3 * self.nb))
        self.Π = np.zeros((self.nc, 3 * self.nb))
        self.Φq = np.zeros((self.nc, 6 * self.nb))
        self.λ = np.zeros((self.nc, 1))

    @classmethod
    def init_from_file(cls, filename):
        file_info = read_model_file(filename)
        return cls(*process_system(*file_info))

    def set_g_acc(self, g=-9.81 * Z_AXIS):
        self.g_acc = g

    def set_dynamics(self):
        if self.is_initialized:
            logging.warning("Cannot change solver type on an initialized system")
        else:
            self.solver_type = SolverType.DYNAMICS

    def set_kinematics(self):
        if self.is_initialized:
            logging.warning("Cannot change solver type on an initialized system")
        else:
            self.solver_type = SolverType.KINEMATICS

    def initialize(self):
        for body in self.bodies:
            body.F += body.m * self.g_acc
        self.M = np.diagflat([[body.m] * 3 for body in self.bodies])
        self.J = block_mat([body.J for body in self.bodies])
        self.F_ext = np.vstack([body.F for body in self.bodies])
        if self.solver_type == SolverType.KINEMATICS:
            if self.nc == 6 * self.nb:
                self.tol = 1e-6 if self.tol is None else self.tol
            else:
                self.solver_type = SolverType.DYNAMICS
        if self.solver_type == SolverType.DYNAMICS:
            if self.nc > 6 * self.nb:
                logging.warning("System is overconstrained")
            self.tol = 1e-3 if self.tol is None else self.tol
            self.initialize_dynamics()
        self.is_initialized = True

    def initialize_dynamics(self):
        t_start = 0.0
        self.Φ_r = self.g_cons.get_phi_r(t_start)
        self.Π = self.g_cons.get_pi(t_start)
        tau = np.vstack([body.get_tau() for body in self.bodies])
        gamma = self.g_cons.get_gamma(t_start)
        gyro_j = block_mat([body.get_J_term(self.h) for body in self.bodies])
        zeros = np.zeros((3 * self.nb, 3 * self.nb))
        gmat = np.block([[self.M, zeros, self.Φ_r.T], [zeros, gyro_j, self.Π.T], [self.Φ_r, self.Π, np.zeros((self.nc, self.nc))]])
        rhs = np.block([[self.F_ext], [tau], [gamma]])
        sol = np.linalg.solve(gmat, rhs)
        for i, body in enumerate(self.bodies):
            body.ddr = sol[3 * i : 3 * (i + 1)]
            body.dω = sol[3 * self.nb + 3 * i : 3 * self.nb + 3 * (i + 1)]
            body.cache_rA_values()
        self.λ = sol[6 * self.nb :]


def create_constraint(json_con, body_i, body_j):
    con_type = Constraints[json_con["type"]]
    if con_type == Constraints.DP1:
        return DP1.init_from_dict(json_con, body_i, body_j)
    if con_type == Constraints.CD:
        return CD.init_from_dict(json_con, body_i, body_j)
    if con_type == Constraints.DP2:
        return DP2.init_from_dict(json_con, body_i, body_j)
    if con_type == Constraints.D:
        return D.init_from_dict(json_con, body_i, body_j)
    raise ValueError("Unmapped enum value")


def process_system(file_bodies, file_constraints):
    all_bodies = {}
    bodies = []
    for file_body in file_bodies:
        body = Body.init_from_dict(file_body)
        all_bodies[file_body["id"]] = body
        if not body.is_ground:
            body.id = len(bodies)
            bodies.append(body)
    cons = [
        create_constraint(f_con, all_bodies[f_con["body_i"]], all_bodies[f_con["body_j"]])
        for f_con in file_constraints
    ]
    return bodies, ConGroup(cons, len(bodies))
'''


COMPACT_TOOLS = r'''"""Compact rA-only setup helper derived from public SBEL SimEngineMBD."""

from __future__ import annotations

import logging

from ..rA.system_ra import SystemRA


def standard_setup(parser, model_file, args=None):
    parser.add_argument("--form", choices=["rA"], default="rA")
    parser.add_argument("--mode", choices=["kin", "dyn", "kinematics", "dynamics"], default="kinematics")
    parser.add_argument("--tol", type=float)
    parser.add_argument("-t", "--end_time", type=float, default=3, dest="t_end")
    parser.add_argument("--step_size", type=float, default=1e-3, dest="h")
    parser.add_argument("-l", "--log", choices=["debug", "info", "warning", "error"], default="info")
    parser.add_argument("-o", "--output")
    parser.add_argument("--plot", default=False, action="store_true")
    parser.add_argument("--no-plot", dest="plot", action="store_false")
    parser.add_argument("--save_data", default=False, action="store_true")
    parser.add_argument("--read_data", default=False, action="store_true")
    out_args = parser.parse_args() if args is None else parser.parse_args(args)
    system = SystemRA.init_from_file(model_file)
    if out_args.mode.startswith("kin"):
        system.set_kinematics()
    elif out_args.mode.startswith("dyn"):
        system.set_dynamics()
    else:
        raise ValueError(f"Unmapped mode {out_args.mode} encountered")
    logging.basicConfig(filename=out_args.output, level=getattr(logging, out_args.log.upper()), format="%(message)s")
    return system, out_args
'''


COMPACT_FOUR_LINK = r'''"""Compact four-link setup extracted from public SBEL SimEngineMBD."""

from __future__ import annotations

import argparse as arg
import os
from copy import copy

import numpy as np
import sympy as sp

from ..utils.physics import Y_AXIS, Z_AXIS
from ..utils.tools import standard_setup


π = np.pi


def setup_four_link(args=None):
    parser = arg.ArgumentParser(description="Simulation of Haug's four-link mechanism")
    model_file = os.path.join(os.path.dirname(__file__), "models/four_link.json")
    system, params = standard_setup(parser, model_file, args)
    system.set_g_acc(-9.81 * Z_AXIS)
    system.h = params.h
    system.tol = params.tol
    system.solver_order = 2
    system.bodies[0].m = 2
    system.bodies[0].J = np.diag([4, 2, 0])
    system.bodies[1].m = 1
    system.bodies[1].J = np.diag([12.4, 0.01, 0])
    system.bodies[2].m = 1
    system.bodies[2].J = np.diag([4.54, 0.01, 0])
    t = sp.symbols("t")
    ang_sym = π * t + π / 2
    ang_alt = ang_sym - π / 2
    system.g_cons.cons[-1].set_constraint_fn(sp.cos(ang_sym), t)
    system.g_cons.alt_gcon = copy(system.g_cons.cons[-1])
    system.g_cons.alt_gcon.set_constraint_fn(sp.cos(ang_alt), t)
    system.g_cons.alt_gcon.aj = Z_AXIS
    system.g_cons.alt_index = len(system.g_cons.cons) - 1
    return system, params
'''


COMPACT_SLIDER_CRANK = r'''"""Compact slider-crank setup extracted from public SBEL SimEngineMBD."""

from __future__ import annotations

import argparse as arg
import os
from copy import copy

import numpy as np
import sympy as sp

from ..utils.physics import Z_AXIS
from ..utils.tools import standard_setup


π = np.pi


def setup_slider_crank(args=None):
    parser = arg.ArgumentParser(description="Simulation of Haug's slider-crank model")
    model_file = os.path.join(os.path.dirname(__file__), "models/slider_crank.json")
    system, params = standard_setup(parser, model_file, args)
    system.set_g_acc(-9.81 * Z_AXIS)
    system.h = params.h
    system.tol = params.tol
    system.solver_order = 1
    system.bodies[0].m = 0.12
    system.bodies[0].J = np.diag([1e-4, 1e-5, 1e-4])
    system.bodies[1].m = 0.5
    system.bodies[1].J = np.diag([4e-3, 4e-4, 4e-3])
    system.bodies[2].m = 2
    system.bodies[2].J = np.diag([1e-4, 1e-4, 1e-4])
    t = sp.symbols("t")
    ang_sym = -2 * π * t + π / 2
    ang_alt = ang_sym - π / 2
    system.g_cons.cons[-1].set_constraint_fn(sp.cos(ang_sym), t)
    system.g_cons.cons[-2].set_constraint_fn(1, t)
    system.g_cons.alt_gcon = copy(system.g_cons.cons[-1])
    system.g_cons.alt_gcon.set_constraint_fn(sp.cos(ang_alt), t)
    system.g_cons.alt_gcon.ai = Z_AXIS
    system.g_cons.alt_index = len(system.g_cons.cons) - 1
    return system, params
'''


RUNNER = r'''#!/usr/bin/env python3
"""Run the B6 closed-loop local Gauss6/FullVA candidate rows."""

from __future__ import annotations

import csv
import importlib
import json
import math
import sys
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
VENDOR = ROOT / "vendor"
RESULTS = ROOT / "results"
for path in (SRC, VENDOR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import closed_loop_fullva_dynamic_residual as dynres
import local_closed_loop_helpers as helpers


MODELS = ("four_link", "slider_crank")
STEP_SIZES = (0.1, 0.05, 0.025)
T0 = 0.0
T_END = 0.1
KINEMATIC_TOL = 1.0e-12
NEWTON_TOL = 1.0e-10
MAX_NEWTON_ITERS = 12
OUT_CSV = RESULTS / "closed_loop_local_rows.csv"
OUT_JSON = RESULTS / "closed_loop_local_summary.json"
OUT_MD = RESULTS / "closed_loop_local_summary.md"


@dataclass(frozen=True)
class ModelSpec:
    name: str
    module: str
    setup_name: str


MODEL_SPECS = {
    "four_link": ModelSpec("four_link", "SimEngineMBD.example_models.four_link", "setup_four_link"),
    "slider_crank": ModelSpec("slider_crank", "SimEngineMBD.example_models.slider_crank", "setup_slider_crank"),
}


class LocalV047Shim:
    reconstruct_v046_reaction_dynamics = staticmethod(helpers.reconstruct_v046_reaction_dynamics)


def scalarize(value: object) -> float:
    arr = np.asarray(value)
    if arr.size != 1:
        raise ValueError(f"expected scalar-like constraint value, got shape {arr.shape}")
    return float(arr.reshape(-1)[0])


def patch_modern_numpy_scalar_assignments() -> None:
    module = importlib.import_module("SimEngineMBD.rA.gcons_ra")
    cls = module.ConGroup

    def get_phi(self, t):
        store = getattr(self, "Φ")
        for i, con in enumerate(self.cons):
            store[i, 0] = scalarize(con.get_phi(t))
        return store

    def get_gamma(self, t):
        store = getattr(self, "γ")
        for i, con in enumerate(self.cons):
            store[i, 0] = scalarize(con.get_gamma(t))
        return store

    def get_nu(self, t):
        store = self.nu
        for i, con in enumerate(self.cons):
            store[i, 0] = scalarize(con.get_nu(t))
        return store

    cls.get_phi = get_phi
    cls.get_gamma = get_gamma
    cls.get_nu = get_nu


def setup_system(model_name: str, mode: str, h: float, t_end: float, tol: float):
    spec = MODEL_SPECS[model_name]
    setup_fn = getattr(importlib.import_module(spec.module), spec.setup_name)
    args = [
        "--form",
        "rA",
        "--mode",
        mode,
        "--step_size",
        str(h),
        "--end_time",
        str(t_end),
        "--tol",
        str(tol),
        "--log",
        "warning",
        "--no-plot",
    ]
    system, params = setup_fn(args)
    system.h = params.h
    system.tol = params.tol
    return system, params


def setup_exact_system(model_name: str, h: float, t: float):
    system, _params = setup_system(model_name, "dynamics", h, T_END, KINEMATIC_TOL)
    system.initialize()
    helpers.project_v046_system_to_so3(system)
    helpers.solve_v046_local_kinematic_fullva_time(system, t, KINEMATIC_TOL)
    return system


def finite(value: object) -> float | None:
    try:
        out = float(value)
    except Exception:
        return None
    return out if math.isfinite(out) else None


def observed_order(rows: list[dict[str, object]], key: str) -> tuple[float, list[float]]:
    pairs: list[tuple[float, float]] = []
    for row in rows:
        h = finite(row.get("h"))
        err = finite(row.get(key))
        if h is not None and err is not None and h > 0.0 and err > 0.0:
            pairs.append((h, err))
    pairs.sort(reverse=True)
    if len(pairs) < 3:
        return float("nan"), []
    logs_h = np.log([pair[0] for pair in pairs])
    logs_e = np.log([pair[1] for pair in pairs])
    fit_order = float(np.polyfit(logs_h, logs_e, 1)[0])
    pairwise = [
        float(np.log(pairs[i][1] / pairs[i + 1][1]) / np.log(pairs[i][0] / pairs[i + 1][0]))
        for i in range(len(pairs) - 1)
    ]
    return fit_order, pairwise


def simulate_model_h(model_name: str, h: float, reference: dict[str, np.ndarray]) -> dict[str, object]:
    started = time.perf_counter()
    steps = int(round((T_END - T0) / h))
    row: dict[str, object] = {
        "model": model_name,
        "method": "Gauss6/FullVA-local-closed-loop-true-dynamic-newton",
        "row_type": "self_contained_closed_loop_candidate",
        "h": f"{h:.16e}",
        "t0": f"{T0:.16e}",
        "t_end": f"{T_END:.16e}",
        "steps": steps,
        "status": "ok",
        "stage_oracle_used": "false",
        "max_initial_stage_residual_inf": "nan",
        "max_stage_residual_inf": "nan",
        "total_stage_newton_iterations": "nan",
        "line_search_failures": "nan",
        "all_stages_converged": "false",
        "endpoint_pos_error_inf": "nan",
        "endpoint_vel_error_inf": "nan",
        "endpoint_acc_error_inf": "nan",
        "endpoint_orientation_error_inf": "nan",
        "endpoint_omega_error_inf": "nan",
        "endpoint_alpha_error_inf": "nan",
        "endpoint_position_constraint_norm": "nan",
        "endpoint_velocity_constraint_norm": "nan",
        "endpoint_acceleration_constraint_norm": "nan",
        "endpoint_so3_fro": "nan",
        "runtime_sec": "nan",
        "trajectory_stepper_executed": "false",
        "simulate_runner_implemented": "true",
        "source_policy_external_superiority_allowed": "false",
        "submission_ready": "false",
    }
    try:
        if not np.isclose(T0 + steps * h, T_END):
            raise ValueError(f"h={h} does not divide T_END={T_END}")
        system = setup_exact_system(model_name, h, T0)
        max_initial = 0.0
        max_final = 0.0
        total_iters = 0
        line_search_failures = 0
        all_converged = True
        for step_index in range(steps):
            t_step = T0 + step_index * h
            out = dynres.gauss6_closed_loop_fullva_dynamic_step_newton_smoke(
                system,
                t_step,
                h,
                LocalV047Shim,
                tol=NEWTON_TOL,
                max_iters=MAX_NEWTON_ITERS,
            )
            max_initial = max(max_initial, float(out["max_initial_stage_residual_inf"]))
            max_final = max(max_final, float(out["max_stage_residual_inf"]))
            total_iters += int(out["total_stage_newton_iterations"])
            line_search_failures += int(out["line_search_failures"])
            all_converged = all_converged and bool(out["all_stages_converged"])

        candidate = dynres.endpoint_state_from_system(system)
        err = dynres.endpoint_state_error_inf(candidate, reference)
        phi, vel, acc = helpers.v046_constraint_level_residuals(system, T_END)
        so3 = helpers.orthogonality_error(system)
        ok = all_converged and max_final < 1.0e-8 and all(math.isfinite(err[key]) for key in err)
        row.update(
            {
                "status": "ok" if ok else "diagnostic_failed_threshold",
                "max_initial_stage_residual_inf": f"{max_initial:.16e}",
                "max_stage_residual_inf": f"{max_final:.16e}",
                "total_stage_newton_iterations": total_iters,
                "line_search_failures": line_search_failures,
                "all_stages_converged": str(all_converged).lower(),
                "endpoint_pos_error_inf": f"{err['pos']:.16e}",
                "endpoint_vel_error_inf": f"{err['vel']:.16e}",
                "endpoint_acc_error_inf": f"{err['acc']:.16e}",
                "endpoint_orientation_error_inf": f"{err['orientation']:.16e}",
                "endpoint_omega_error_inf": f"{err['omega']:.16e}",
                "endpoint_alpha_error_inf": f"{err['alpha']:.16e}",
                "endpoint_position_constraint_norm": f"{phi:.16e}",
                "endpoint_velocity_constraint_norm": f"{vel:.16e}",
                "endpoint_acceleration_constraint_norm": f"{acc:.16e}",
                "endpoint_so3_fro": f"{so3:.16e}",
                "runtime_sec": f"{time.perf_counter() - started:.16e}",
                "trajectory_stepper_executed": "true",
            }
        )
    except Exception as exc:
        row.update(
            {
                "status": f"failed:{type(exc).__name__}:{str(exc).replace(chr(10), ' ')}",
                "runtime_sec": f"{time.perf_counter() - started:.16e}",
            }
        )
    return row


def build_model_summary(model_name: str, rows: list[dict[str, object]]) -> dict[str, object]:
    pos_order, pos_pairwise = observed_order(rows, "endpoint_pos_error_inf")
    orientation_order, orientation_pairwise = observed_order(rows, "endpoint_orientation_error_inf")
    vel_order, vel_pairwise = observed_order(rows, "endpoint_vel_error_inf")
    omega_order, omega_pairwise = observed_order(rows, "endpoint_omega_error_inf")
    ok_rows = [row for row in rows if row.get("status") == "ok"]
    primary_orders = [pos_order, orientation_order, vel_order, omega_order]
    min_primary_order = min(primary_orders) if all(math.isfinite(value) for value in primary_orders) else float("nan")
    accepted = len(ok_rows) == len(STEP_SIZES) and math.isfinite(min_primary_order) and min_primary_order >= 4.5
    return {
        "model": model_name,
        "row_count": len(rows),
        "ok_row_count": len(ok_rows),
        "pos_observed_order": pos_order,
        "orientation_observed_order": orientation_order,
        "vel_observed_order": vel_order,
        "omega_observed_order": omega_order,
        "pos_pairwise_orders": pos_pairwise,
        "orientation_pairwise_orders": orientation_pairwise,
        "vel_pairwise_orders": vel_pairwise,
        "omega_pairwise_orders": omega_pairwise,
        "min_primary_order": min_primary_order,
        "accepted_dynamic_order_candidate": accepted,
    }


def annotate_rows_with_orders(rows: list[dict[str, object]], summaries: dict[str, dict[str, object]]) -> None:
    for row in rows:
        summary = summaries[row["model"]]
        row["model_pos_observed_order"] = f"{float(summary['pos_observed_order']):.16e}"
        row["model_orientation_observed_order"] = f"{float(summary['orientation_observed_order']):.16e}"
        row["model_vel_observed_order"] = f"{float(summary['vel_observed_order']):.16e}"
        row["model_omega_observed_order"] = f"{float(summary['omega_observed_order']):.16e}"
        row["accepted_dynamic_order"] = str(bool(summary["accepted_dynamic_order_candidate"])).lower()


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError("refusing to write empty closed-loop rows")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    RESULTS.mkdir(parents=True, exist_ok=True)
    patch_modern_numpy_scalar_assignments()
    rows: list[dict[str, object]] = []
    for model_name in MODELS:
        reference_system = setup_exact_system(model_name, min(STEP_SIZES), T_END)
        reference = dynres.endpoint_state_from_system(reference_system)
        for h in STEP_SIZES:
            rows.append(simulate_model_h(model_name, h, reference))

    summaries = {
        model_name: build_model_summary(model_name, [row for row in rows if row["model"] == model_name])
        for model_name in MODELS
    }
    annotate_rows_with_orders(rows, summaries)
    ok_count = sum(1 for row in rows if row.get("status") == "ok")
    accepted_count = sum(1 for item in summaries.values() if item.get("accepted_dynamic_order_candidate") is True)
    summary = {
        "schema": "cmame-closed-loop-local-runner-candidate-summary-v1",
        "status": (
            "closed_loop_self_contained_candidate_rows_passed_not_source_policy"
            if ok_count == len(rows) and accepted_count == len(MODELS)
            else "closed_loop_self_contained_candidate_rows_incomplete"
        ),
        "self_contained_simulation_runner": True,
        "imports_v046_v047_v048": False,
        "submission_ready": False,
        "source_policy_external_superiority_allowed": False,
        "models": list(MODELS),
        "step_sizes": list(STEP_SIZES),
        "row_count": len(rows),
        "ok_row_count": ok_count,
        "accepted_dynamic_order_count": accepted_count,
        "model_summaries": summaries,
        "run_v047_invoked": False,
        "run_v048_invoked": False,
        "heavy_numerical_run_invoked": False,
    }
    write_csv(OUT_CSV, rows)
    OUT_JSON.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text(
        "\n".join(
            [
                "# Closed-Loop Local Runner Candidate",
                "",
                f"Status: **{summary['status']}**.",
                f"Self-contained simulation runner: `{summary['self_contained_simulation_runner']}`.",
                f"Rows ok: `{ok_count}/{len(rows)}`.",
                f"Accepted dynamic-order candidates: `{accepted_count}`.",
                f"Source-policy external superiority allowed: `{summary['source_policy_external_superiority_allowed']}`.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    print("cmame_closed_loop_local_runner_candidate=PASS" if summary["status"].endswith("not_source_policy") else "cmame_closed_loop_local_runner_candidate=FAIL")
    print(f"rows_ok={ok_count}/{len(rows)}")
    for model_name, model_summary in summaries.items():
        print(
            f"{model_name}_orders="
            f"{float(model_summary['pos_observed_order']):.6f}/"
            f"{float(model_summary['orientation_observed_order']):.6f}/"
            f"{float(model_summary['vel_observed_order']):.6f}/"
            f"{float(model_summary['omega_observed_order']):.6f}"
        )
    print("self_contained_simulation_runner=True")
    print("source_policy_external_superiority_allowed=False")
    return 0 if summary["status"].endswith("not_source_policy") else 1


if __name__ == "__main__":
    sys.exit(main())
'''

HELPERS = r'''"""Local helper functions for the closed-loop runner candidate."""

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
'''


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def python_line_count(path: Path) -> int:
    return len(read_text(path).splitlines()) if path.suffix == ".py" else 0


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def copy_file(source: Path, target: Path) -> dict[str, object]:
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)
    item: dict[str, object] = {
        "path": str(target.relative_to(CANDIDATE)),
        "source": str(source.relative_to(PAPER)) if source.is_relative_to(PAPER) else str(source),
        "bytes": target.stat().st_size,
        "sha256": sha256(target),
    }
    lines = python_line_count(target)
    if lines:
        item["python_lines"] = lines
    return item


def remove_generated_tree() -> None:
    if CANDIDATE.exists():
        shutil.rmtree(CANDIDATE)


def import_modules(path: Path) -> list[str]:
    try:
        tree = ast.parse(read_text(path))
    except SyntaxError:
        return []
    modules: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            modules.append(node.module or "")
    return modules


def forbidden_imports() -> list[dict[str, object]]:
    out: list[dict[str, object]] = []
    forbidden = ("run_v047", "run_v048", "v046", "v047", "v048", "v029")
    for path in sorted(CANDIDATE.rglob("*.py")):
        imports = import_modules(path)
        bad = [module for module in imports if any(token in module for token in forbidden)]
        if bad:
            out.append({"path": str(path.relative_to(CANDIDATE)), "imports": bad})
    return out


def run_candidate() -> dict[str, object]:
    script = CANDIDATE / "scripts" / "run_closed_loop_fullva_candidate.py"
    env = os.environ.copy()
    env.setdefault("MPLCONFIGDIR", "/tmp")
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    proc = subprocess.run(
        [sys.executable, str(script)],
        cwd=CANDIDATE,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=120,
    )
    return {
        "returncode": proc.returncode,
        "output_tail": proc.stdout.strip().splitlines()[-12:],
    }


def read_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> None:
    remove_generated_tree()
    files: list[dict[str, object]] = []
    for source_rel, target_rel in VENDOR_FILES:
        files.append(copy_file(SBEL / source_rel, CANDIDATE / target_rel))
    files.append(copy_file(V048 / "closed_loop_fullva_dynamic_residual.py", CANDIDATE / "src" / "closed_loop_fullva_dynamic_residual.py"))
    write_text(CANDIDATE / "vendor" / "SimEngineMBD" / "example_models" / "four_link.py", COMPACT_FOUR_LINK)
    write_text(CANDIDATE / "vendor" / "SimEngineMBD" / "example_models" / "slider_crank.py", COMPACT_SLIDER_CRANK)
    write_text(CANDIDATE / "vendor" / "SimEngineMBD" / "rA" / "system_ra.py", COMPACT_SYSTEM_RA)
    write_text(CANDIDATE / "vendor" / "SimEngineMBD" / "utils" / "physics.py", COMPACT_PHYSICS)
    write_text(CANDIDATE / "vendor" / "SimEngineMBD" / "utils" / "tools.py", COMPACT_TOOLS)
    write_text(CANDIDATE / "src" / "local_closed_loop_helpers.py", HELPERS)
    write_text(CANDIDATE / "scripts" / "run_closed_loop_fullva_candidate.py", RUNNER)
    write_text(
        CANDIDATE / "README.md",
        """# CMAME Closed-Loop Local Runner Candidate

Compact executable candidate for the B6 closed-loop local rows.

Run from this directory:

```bash
python3 scripts/run_closed_loop_fullva_candidate.py
```

Expected markers:

- `cmame_closed_loop_local_runner_candidate=PASS`
- `rows_ok=6/6`
- `models=four_link,slider_crank`
- `source_policy_external_superiority_allowed=False`

Boundary:

- regenerates six local four-link/slider-crank closed-loop rows;
- does not import `run_v046.py`, `run_v047.py`, `run_v048.py`, or `run_v029.py`;
- does not run source-policy external benchmarks;
- keeps source-policy external rows closed at `0/40`;
- does not make the paper submission ready.
""",
    )

    generated = [
        CANDIDATE / "vendor" / "SimEngineMBD" / "example_models" / "four_link.py",
        CANDIDATE / "vendor" / "SimEngineMBD" / "example_models" / "slider_crank.py",
        CANDIDATE / "vendor" / "SimEngineMBD" / "rA" / "system_ra.py",
        CANDIDATE / "vendor" / "SimEngineMBD" / "utils" / "physics.py",
        CANDIDATE / "vendor" / "SimEngineMBD" / "utils" / "tools.py",
        CANDIDATE / "src" / "local_closed_loop_helpers.py",
        CANDIDATE / "scripts" / "run_closed_loop_fullva_candidate.py",
        CANDIDATE / "README.md",
    ]
    for path in generated:
        item: dict[str, object] = {
            "path": str(path.relative_to(CANDIDATE)),
            "source": "generated",
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
        }
        lines = python_line_count(path)
        if lines:
            item["python_lines"] = lines
        files.append(item)

    run = run_candidate()
    summary_path = CANDIDATE / "results" / "closed_loop_local_summary.json"
    rows_path = CANDIDATE / "results" / "closed_loop_local_rows.csv"
    summary = read_json(summary_path) if summary_path.exists() else {}
    rows = read_csv(rows_path) if rows_path.exists() else []
    for path in [summary_path, rows_path, CANDIDATE / "results" / "closed_loop_local_summary.md"]:
        if path.exists():
            item = {
                "path": str(path.relative_to(CANDIDATE)),
                "source": "generated_by_runner",
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
            files.append(item)

    python_files = [path for path in CANDIDATE.rglob("*.py")]
    python_lines = sum(python_line_count(path) for path in python_files)
    bad_imports = forbidden_imports()
    runner_passed = (
        run["returncode"] == 0
        and summary.get("status") == "closed_loop_self_contained_candidate_rows_passed_not_source_policy"
        and len(rows) == 6
        and summary.get("ok_row_count") == 6
        and summary.get("accepted_dynamic_order_count") == 2
        and not bad_imports
    )
    compact_ok = python_lines <= PYTHON_LINE_LIMIT
    manifest = {
        "schema": "cmame-closed-loop-local-runner-candidate-v1",
        "status": (
            "closed_loop_local_runner_candidate_passed_not_compact"
            if runner_passed and not compact_ok
            else "closed_loop_local_runner_candidate_passed_compact"
            if runner_passed
            else "closed_loop_local_runner_candidate_failed"
        ),
        "submission_ready": False,
        "self_contained_simulation_runner": runner_passed,
        "runner_passed": runner_passed,
        "package_dir": "cmame_closed_loop_local_runner_candidate",
        "candidate_file_count": len(files),
        "candidate_python_file_count": len(python_files),
        "candidate_python_line_count": python_lines,
        "candidate_python_line_limit": PYTHON_LINE_LIMIT,
        "candidate_python_line_limit_ok": compact_ok,
        "imports_v046_v047_v048_or_v029": bool(bad_imports),
        "forbidden_imports": bad_imports,
        "source_policy_external_superiority_allowed": False,
        "source_policy_external_rows_closed": 0,
        "source_policy_external_rows_total": 40,
        "run_v047_invoked": False,
        "run_v048_invoked": False,
        "heavy_numerical_run_invoked": False,
        "closed_loop_local_rows": len(rows),
        "closed_loop_models": summary.get("models", []),
        "step_sizes": summary.get("step_sizes", []),
        "summary": summary,
        "runner_invocation": run,
        "files": files,
        "next_concrete_step": (
            "keep this compact closed-loop candidate in the B6/repro manifest set while B4/B7 "
            "source-policy gates remain open"
            if runner_passed and compact_ok
            else "reduce the vendored source footprint below the reviewer-facing line limit or split the candidate "
            "into a compact runner API plus provenance archive"
        ),
    }
    write_text(CANDIDATE / "MANIFEST.json", json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    manifest["files"].append(
        {
            "path": "MANIFEST.json",
            "source": "generated",
            "bytes": (CANDIDATE / "MANIFEST.json").stat().st_size,
            "sha256": sha256(CANDIDATE / "MANIFEST.json"),
        }
    )
    manifest["candidate_file_count"] = len(manifest["files"])
    OUT_JSON.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# CMAME Closed-Loop Local Runner Candidate Manifest",
        "",
        f"Status: **{manifest['status']}**.",
        f"Runner passed: `{manifest['runner_passed']}`.",
        f"Self-contained simulation runner: `{manifest['self_contained_simulation_runner']}`.",
        f"Candidate Python files/lines: `{manifest['candidate_python_file_count']}/{manifest['candidate_python_line_count']}`.",
        f"Line limit ok: `{manifest['candidate_python_line_limit_ok']}`.",
        f"Forbidden imports present: `{manifest['imports_v046_v047_v048_or_v029']}`.",
        f"Closed-loop local rows: `{manifest['closed_loop_local_rows']}`.",
        f"Source-policy rows closed: `{manifest['source_policy_external_rows_closed']}/{manifest['source_policy_external_rows_total']}`.",
        "",
        "## Runner Output",
        "",
    ]
    lines.extend(f"- {line}" for line in run["output_tail"])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("cmame_closed_loop_local_runner_candidate=written")
    print(f"status={manifest['status']}")
    print(f"runner_passed={runner_passed}")
    print(f"candidate_python={manifest['candidate_python_file_count']}/{python_lines}")
    print(f"line_limit_ok={compact_ok}")
    print(f"closed_loop_local_rows={len(rows)}")


if __name__ == "__main__":
    main()
