"""Compact rA-only SystemRA derived from public SBEL SimEngineMBD."""

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
