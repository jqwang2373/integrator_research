#!/usr/bin/env python3
"""Schematic figures for the rewritten manuscript: one-step overview, chain sketch, benchmark
mechanisms.  Writes paper/figures/method_overview.png, chain_schematic.png, mechanisms.png.

The mechanism panels reuse the drawing helpers of the 2026 figure generator
(validation/paper_v047_cylindrical_chain/generate_publication_figures.py) with the internal
annotations removed.
"""

from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import patches  # noqa: E402
import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
PAPER = HERE.parent
REPO = PAPER.parent
FIGURES = PAPER / "figures"
GPF = REPO / "validation" / "paper_v047_cylindrical_chain" / "generate_publication_figures.py"

INK, MUTED, BLUE, GREEN, ORANGE, PURPLE = "#1f2933", "#52616b", "#2f6f9f", "#5f8f3f", "#c46a2b", "#7a5195"


def load_gpf():
    if str(GPF.parent) not in sys.path:
        sys.path.insert(0, str(GPF.parent))
    spec = importlib.util.spec_from_file_location("gpf", GPF)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def box(ax, x, y, w, h, title, lines, edge, face="#ffffff", title_size=11.5, body_size=10, title_gap=0.03, body_gap=0.12):
    ax.add_patch(patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.01,rounding_size=0.015", ec=edge, fc=face, lw=1.4))
    ax.text(x + w / 2, y + h - title_gap, title, ha="center", va="top", fontsize=title_size, weight="bold", color=INK)
    ax.text(x + w / 2, y + h - body_gap, "\n".join(lines), ha="center", va="top", fontsize=body_size, color=MUTED, linespacing=1.25)


def arrow(ax, p, q, color=MUTED):
    ax.annotate("", xy=q, xytext=p, arrowprops={"arrowstyle": "->", "lw": 1.3, "color": color, "shrinkA": 2, "shrinkB": 2})


def method_overview() -> None:
    fig, ax = plt.subplots(figsize=(6.4, 6.0))
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    # left column: the flow of one step
    x, w, h = 0.02, 0.42, 0.20
    ys = [0.78, 0.53, 0.28, 0.03]
    box(ax, x, ys[0], w, h, "endpoint state", ["$x_n=(q_n,v_n)$", "predictor $Z^{(0)}$"], BLUE, title_size=10.5, body_size=8.5, body_gap=0.09)
    box(ax, x, ys[1], w, h, "stage system", ["$F_h(Z;x_n)=0$", "132 rows, 132 unknowns", "3 stages $\\times$ $(r,\\eta,v,\\omega,a,\\alpha,\\lambda)$"], ORANGE, title_size=10.5, body_size=8, body_gap=0.085)
    box(ax, x, ys[2], w, h, "Newton solve", ["AD Jacobian, dense LU", "5--6 iterations, $\\|F_h\\|\\leq 10^{-11}$"], PURPLE, title_size=10.5, body_size=8.5, body_gap=0.09)
    box(ax, x, ys[3], w, h, "endpoint", ["$r_{n+1},v_{n+1},\\omega_{n+1}$: Gauss weights", "$Q_{n+1}=Q_n\\mathrm{Exp}(h\\sum_i b_iJ_r^{-1}\\omega_i)$", "velocity-level closure $\\mathcal{C}_h$"], GREEN, title_size=10.5, body_size=8, body_gap=0.085)
    for a, b in zip(ys[:-1], ys[1:]):
        arrow(ax, (x + w / 2, a), (x + w / 2, b + h))
    # right column: row families and the identity
    rx, rw = 0.52, 0.46
    ax.add_patch(patches.FancyBboxPatch((rx, 0.46), rw, 0.52, boxstyle="round,pad=0.01,rounding_size=0.015", ec=ORANGE, fc="#fff7f0", lw=1.2))
    ax.text(rx + rw / 2, 0.955, "row families (per stage)", ha="center", va="top", fontsize=10.5, weight="bold", color=INK)
    rows = [
        ("constraints, three levels", "24 rows", "$\\Phi(q_i)=0$, $\\Phi_qv_i=0$,\n$\\Phi_qa_i+\\dot\\Phi_qv_i=0$"),
        ("joint collocation", "8 rows", "$\\Delta_i[s_j]=\\Delta_i[\\dot s_j]=0$,\n$\\Delta_i[\\theta_j]=\\Delta_i[\\dot\\theta_j]=0$"),
        ("Newton--Euler balance", "12 rows", "$m_ba_{b,i}=F^r_{b,i}$,\n$J_b\\alpha_{b,i}+\\omega_{b,i}\\times J_b\\omega_{b,i}=T^\\theta_{b,i}$"),
    ]
    for k, (name, count, formula) in enumerate(rows):
        yy = 0.875 - 0.145 * k
        ax.text(rx + 0.02, yy, name, fontsize=9, color=INK, va="center")
        ax.text(rx + rw - 0.02, yy, count, fontsize=9, color=INK, va="center", ha="right")
        ax.text(rx + 0.04, yy - 0.055, formula, fontsize=8, color=MUTED, va="center", linespacing=1.2)
    arrow(ax, (x + w, ys[1] + h / 2), (rx, ys[1] + h / 2 + 0.06), color=ORANGE)
    ax.text(rx, 0.40, "exact stage identity (Lemma 1)", fontsize=10.5, weight="bold", color=INK, va="top")
    ax.text(rx, 0.33, "$F_h(Z_G;x_n)=0$ for the lifted reduced Gauss\nstage $Z_G$; on the regular branch every root\nof the 96 non-dynamic rows is such a lift.\nThe step is Gauss collocation of the reduced\nequations $\\dot y=f(y,t)$ in absolute coordinates.",
            fontsize=8.5, color=MUTED, va="top", linespacing=1.3)
    fig.savefig(FIGURES / "method_overview.png", dpi=220, bbox_inches="tight"); plt.close(fig)


def chain_schematic() -> None:
    fig, ax = plt.subplots(figsize=(6.4, 4.4))
    ax.set_xlim(0, 1); ax.set_ylim(0, 1.05); ax.set_aspect("equal"); ax.axis("off")
    # ground axis
    g0, g1 = np.array([0.08, 0.22]), np.array([0.62, 0.62])
    u = (g1 - g0) / np.linalg.norm(g1 - g0)
    ax.plot([g0[0] - 0.05 * u[0], g1[0] + 0.05 * u[0]], [g0[1] - 0.05 * u[1], g1[1] + 0.05 * u[1]], color=MUTED, lw=1.2, ls="--")
    ax.annotate("", xy=g1 + 0.12 * u, xytext=g1, arrowprops={"arrowstyle": "->", "lw": 1.2, "color": MUTED})
    ax.text(*(g1 + 0.13 * u + np.array([0.01, -0.09])), "ground axis $n_0=a_0$", fontsize=9, color=MUTED)
    for s in np.linspace(0.05, 0.95, 6):
        p = g0 + s * (g1 - g0)
        ax.plot([p[0] - 0.02, p[0] + 0.02], [p[1] - 0.03, p[1] - 0.07], color=MUTED, lw=0.8)
    # body 0: box sliding along the ground axis at parameter s_0
    c0 = g0 + 0.45 * (g1 - g0)
    ang0 = np.degrees(np.arctan2(u[1], u[0]))
    body0 = patches.FancyBboxPatch((-0.11, -0.05), 0.22, 0.10, boxstyle="round,pad=0.005,rounding_size=0.01", ec=BLUE, fc="#eaf2f8", lw=1.6,
                                   transform=matplotlib.transforms.Affine2D().rotate_deg(ang0).translate(*c0) + ax.transData)
    ax.add_patch(body0)
    ax.text(c0[0] - 0.22, c0[1] + 0.02, "body 0", fontsize=9.5, color=BLUE, weight="bold")
    ax.annotate("", xy=c0 + 0.16 * u, xytext=c0 + 0.09 * u, arrowprops={"arrowstyle": "->", "lw": 1.4, "color": BLUE})
    ax.text(*(c0 + 0.10 * u + np.array([0.02, -0.07])), "$s_0,\\ \\dot s_0$", fontsize=9, color=BLUE)
    # spin arrow about the ground axis at body 0
    arc = patches.Arc(c0 - 0.03 * u, 0.09, 0.16, angle=ang0, theta1=200, theta2=340, color=BLUE, lw=1.2)
    ax.add_patch(arc); ax.text(c0[0] - 0.12, c0[1] - 0.14, "$\\theta_0$", fontsize=9, color=BLUE)
    # second axis fixed in body 0, inclined
    a1 = np.array([0.42, 0.91]); a1 /= np.linalg.norm(a1)
    p1 = c0 + 0.05 * u + np.array([0.0, 0.0])
    ax.plot([p1[0] - 0.02 * a1[0], p1[0] + 0.42 * a1[0]], [p1[1] - 0.02 * a1[1], p1[1] + 0.42 * a1[1]], color=MUTED, lw=1.2, ls="--")
    ax.annotate("", xy=p1 + 0.46 * a1, xytext=p1 + 0.40 * a1, arrowprops={"arrowstyle": "->", "lw": 1.2, "color": MUTED})
    ax.text(*(p1 + 0.44 * a1 + np.array([0.03, -0.01])), "moving axis\n$a_1(q)=Q_0\\hat a_0^{\\rm next}$", fontsize=9, color=MUTED, va="top")
    ax.plot([p1[0] - 0.02 * a1[0], p1[0] + 0.36 * a1[0]], [p1[1] - 0.02 * a1[1] + 0.0, p1[1] + 0.36 * a1[1]], color=ORANGE, lw=0.9, ls=":")
    ax.text(*(p1 + 0.40 * a1 + np.array([-0.50, 0.03])), "frozen direction $n_1=a_1(0)$,\nbasis $e_{1,1},e_{1,2}\\perp n_1$", fontsize=8.5, color=ORANGE, va="center")
    # body 1 on the second axis
    c1 = p1 + 0.27 * a1
    ang1 = np.degrees(np.arctan2(a1[1], a1[0]))
    body1 = patches.FancyBboxPatch((-0.05, -0.09), 0.10, 0.18, boxstyle="round,pad=0.005,rounding_size=0.01", ec=GREEN, fc="#eef5e6", lw=1.6,
                                   transform=matplotlib.transforms.Affine2D().rotate_deg(ang1 - 90).translate(*c1) + ax.transData)
    ax.add_patch(body1)
    ax.text(c1[0] - 0.20, c1[1] + 0.04, "body 1", fontsize=9.5, color=GREEN, weight="bold")
    ax.text(c1[0] - 0.20, c1[1] - 0.02, "$s_1,\\ \\theta_1$", fontsize=9, color=GREEN)
    ax.text(0.02, 0.05, "pair 0: slide $s_0$ and spin $\\theta_0$ about the ground axis;   pair 1: slide $s_1$ and spin $\\theta_1$ about $a_1(q)$,\n"
            "four constraint rows each ($e_{j,m}\\cdot d_j=0$, $e_{j,m}\\cdot\\psi_j=0$); regular while $n_1\\cdot a_1(q)\\neq0$",
            fontsize=8.5, color=INK, va="bottom")
    fig.savefig(FIGURES / "chain_schematic.png", dpi=220, bbox_inches="tight"); plt.close(fig)


JARGON = re.compile(r"FullVA|nested|h_\{\\rm ref\}|friction disabled|Phi|residual|ground mark|distance row|prismatic", re.I)


def mechanisms() -> None:
    gpf = load_gpf()
    subtitles = {"single pendulum": "driven revolute joint, $\\theta(t)$ prescribed", "double pendulum": "two revolute joints, released from rest",
                 "four-link loop": "driven closed loop, revolute/universal/spherical joints", "slider-crank": "driven crank, spherical and prismatic joints"}
    orig_setup = gpf.setup_panel

    def setup_panel(ax, title, subtitle):
        orig_setup(ax, title, subtitles.get(title, ""))
    gpf.setup_panel = setup_panel
    fig, axes = plt.subplots(2, 2, figsize=(6.4, 5.8))
    for ax, draw in zip(axes.ravel(), (gpf.draw_single, gpf.draw_double, gpf.draw_four_link, gpf.draw_slider)):
        draw(ax)
        for txt in list(ax.texts):
            if JARGON.search(txt.get_text()) or txt.get_text().startswith("$s_") or txt.get_text().startswith("$D="):
                txt.remove()
    fig.savefig(FIGURES / "mechanisms.png", dpi=220, bbox_inches="tight"); plt.close(fig)


def main() -> int:
    method_overview(); chain_schematic(); mechanisms()
    print("schematics written to", FIGURES)
    return 0


if __name__ == "__main__":
    sys.exit(main())
