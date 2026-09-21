"""Compact rA-only physics helpers derived from public SBEL SimEngineMBD."""

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
