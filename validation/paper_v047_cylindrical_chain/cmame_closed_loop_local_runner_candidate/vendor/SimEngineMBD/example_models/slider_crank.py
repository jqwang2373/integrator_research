"""Compact slider-crank setup extracted from public SBEL SimEngineMBD."""

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
