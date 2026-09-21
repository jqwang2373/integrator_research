"""Compact rA-only setup helper derived from public SBEL SimEngineMBD."""

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
