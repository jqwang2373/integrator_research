#!/usr/bin/env python3
"""Figures for the agentic-research paper.  Every panel is drawn from repository data:

* fig_problem.png    : the benchmark mechanism, the measured convergence (E1 result file) and the
                       identity that became the theorem;
* fig_process.png    : the process, with one claim followed from hypothesis to manuscript cell;
* fig_tree.png       : the 49 versions as an exploration tree (version ledger) and the decisive
                       move v023 -> v027 measured from the run tables of those versions;
* fig_incidents.png  : four incidents, what the agent saw against what was true (E1, E4, E7 result
                       files and the cached branch factor from compute_branch_factor.py);
* fig_session.png    : the final session from the transcript, with the human's messages and the
                       incidents placed on the time axis.
Also writes stats.tex (\\nHuman etc.), session_stats.json and version_table.csv.
"""

from __future__ import annotations

import collections
import csv
import datetime
import glob
import json
import re
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import patches  # noqa: E402
import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
FIG = HERE / "figures"
RES = REPO / "numerics" / "v049_paper_experiments" / "results"
plt.rcParams.update({"font.size": 8, "axes.titlesize": 8.5, "axes.labelsize": 8, "legend.fontsize": 7,
                     "xtick.labelsize": 7, "ytick.labelsize": 7, "figure.dpi": 220, "savefig.dpi": 220,
                     "axes.spines.top": False, "axes.spines.right": False})
BLUE, ORANGE, GREEN, RED, PURPLE, GREY, YELLOW, CYAN = "#4C72B0", "#DD8452", "#55A868", "#C44E52", "#8172B2", "#8C8C8C", "#CCB974", "#64B5CD"

PHASES = [
    ("Lie-group basics", range(1, 6), "#4C72B0"),
    ("constrained DAE closure", range(6, 14), "#55A868"),
    ("friction and baselines", range(14, 23), "#C44E52"),
    ("absolute-coordinate FullVA", range(23, 30), "#8172B2"),
    ("sparse solver scaling", range(30, 46), "#CCB974"),
    ("validation anchors", range(46, 49), "#64B5CD"),
    ("paper experiments", range(49, 50), "#8C8C8C"),
]
# Role of each version in the record, condensed from validation/docs/version_ledger.csv.
KEPT = {5, 8, 10, 12, 13, 19, 21, 26, 27, 29, 42, 43, 44, 46, 47, 49}
RULED_OUT = {4, 16, 17, 18, 24, 25, 31, 32, 33}
MILESTONES = {5: "Gauss collocation\nchosen", 13: "first sixth-order\ncandidate", 21: "friction law\nkept", 27: "FullVA stage\nsystem",
              47: "chain benchmark,\naccepted code", 49: "paper\nexperiments"}
NEGATIVE = {4: "Yoshida\nsubsteps", 16: "trapezoidal", 17: "BDF2", 18: "Lobatto\nendpoint", 24: "Lobatto\nnodes", 25: "projection\nrepair",
            31: "sparse Newton\nnot faster", 32: "Newton–\nKrylov", 33: "Jacobian\nlagging"}


def phase_of(v: int):
    for name, rng, col in PHASES:
        if v in rng:
            return name, col
    return "other", "#999999"


def box(ax, x, y, w, h, title, lines, color, face="#ffffff", ts=8, bs=6.6, lw=1.2, title_gap=0.03, body_gap=0.11, italic=False):
    ax.add_patch(patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.006,rounding_size=0.01", ec=color, fc=face, lw=lw))
    if title:
        ax.text(x + w / 2, y + h - title_gap, title, ha="center", va="top", fontsize=ts, weight="bold", color="#222")
    body = ax.text(x + w / 2, y + h - (body_gap if title else title_gap), "\n".join(lines), ha="center", va="top", fontsize=bs,
                   color="#333", linespacing=1.25, style="italic" if italic else "normal")
    return body, w


def fit_texts(fig, ax, items, margin=0.92, min_size=5.2):
    fig.canvas.draw()
    for txt, w in items:
        for _ in range(12):
            bb = txt.get_window_extent(fig.canvas.get_renderer())
            box_px = ax.transData.transform((w, 0))[0] - ax.transData.transform((0, 0))[0]
            if bb.width <= margin * box_px or txt.get_fontsize() <= min_size:
                break
            txt.set_fontsize(max(min_size, txt.get_fontsize() * margin * box_px / bb.width))
            fig.canvas.draw()


def arrow(ax, p, q, color="#555", style="->", lw=1.0, ls="-"):
    ax.annotate("", xy=q, xytext=p, arrowprops={"arrowstyle": style, "lw": lw, "color": color, "shrinkA": 2, "shrinkB": 2, "linestyle": ls})


# ----------------------------------------------------------------------------------------------
# Figure 1: problem, measured result, identity
# ----------------------------------------------------------------------------------------------
def draw_mechanism(ax):
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    ang = np.deg2rad(26); d = np.array([np.cos(ang), np.sin(ang)]); n = np.array([-d[1], d[0]])
    o = np.array([0.04, 0.16])
    a, b = o - 0.02 * d, o + 0.86 * d
    ax.plot([a[0], b[0]], [a[1], b[1]], ls="--", color="#555", lw=1)
    for s_ in np.linspace(0.04, 0.84, 7):
        p = o + s_ * d; ax.plot([p[0], p[0] - 0.045 * n[0] + 0.02 * d[0]], [p[1], p[1] - 0.045 * n[1] + 0.02 * d[1]], color="#777", lw=0.8)
    ax.text(*(b + 0.02 * n), "ground axis", fontsize=6.3, color="#555", ha="right", va="bottom")

    def body(center, direction, L, W, color, face):
        dd = direction / np.linalg.norm(direction); nn = np.array([-dd[1], dd[0]])
        pts = [center + sx * L / 2 * dd + sy * W / 2 * nn for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
        ax.add_patch(patches.Polygon(pts, closed=True, ec=color, fc=face, lw=1.4))
    c0 = o + 0.36 * d
    body(c0, d, 0.30, 0.14, BLUE, "#e8eef7")
    ang2 = np.deg2rad(80); d2 = np.array([np.cos(ang2), np.sin(ang2)])
    j = c0 + 0.05 * d + 0.07 * n
    ax.plot([j[0] - 0.05 * d2[0], j[0] + 0.50 * d2[0]], [j[1] - 0.05 * d2[1], j[1] + 0.50 * d2[1]], ls="-.", color=ORANGE, lw=1)
    c1 = j + 0.37 * d2
    body(c1, d2, 0.26, 0.12, GREEN, "#eaf4ea")
    ax.text(0.99, 0.99, "body 1: slides ($s_1$) and turns ($\\theta_1$)\non an axis carried by body 0", fontsize=6.2, color=GREEN, ha="right", va="top")
    ax.text(0.99, 0.03, "body 0: slides ($s_0$) and turns ($\\theta_0$)\non the ground axis; both joints have friction", fontsize=6.2, color=BLUE, ha="right", va="bottom")
    ax.set_title("(a) the benchmark mechanism", fontsize=7.5, loc="left")


def draw_convergence(ax):
    e1 = json.load(open(RES / "E1_convergence.json"))
    hs = np.array([r["h"] for r in e1["rows"]])
    pos = np.array([r["final_position"] for r in e1["rows"]]); ori = np.array([r["final_orientation"] for r in e1["rows"]])
    ax.loglog(hs, pos, "o-", color=BLUE, ms=3.5, label="position")
    ax.loglog(hs, ori, "s-", color=ORANGE, ms=3.5, label="orientation")
    ax.loglog(hs, pos[0] * (hs / hs[0]) ** 6, "--", color="#333", lw=0.9, label="slope 6")
    fl = e1["richardson_floor"]["final_position"]
    ax.axhline(fl, color="#999", ls=":", lw=0.8); ax.text(hs[0], fl * 2.0, "reference floor", fontsize=5.8, color="#777", ha="right")
    ax.set_xlabel("step size $h$", labelpad=1); ax.set_ylabel("error at $t=0.5$", labelpad=1)
    ax.set_title("(b) measured convergence (E1)", fontsize=7.5, loc="left")
    ax.legend(frameon=False, loc="lower right", fontsize=6.0)
    ax.text(0.03, 0.97, "halving $h$ divides the\nerror by about $2^6=64$", transform=ax.transAxes, fontsize=6.0, va="top", color="#333")
    ax.grid(True, alpha=0.25); ax.tick_params(labelsize=6)


def draw_identity(ax):
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    items = []
    items.append(box(ax, 0.01, 0.60, 0.46, 0.36, "manuscript said", ["body-level collocation", "rows for position", "and rotation"], RED, face="#fbeeee", ts=7.2, bs=6.2, body_gap=0.12))
    items.append(box(ax, 0.53, 0.60, 0.46, 0.36, "code solved", ["joint-coordinate rows,", "constraints at 3 levels,", "Newton–Euler: 132 rows"], BLUE, face="#eef2f9", ts=7.2, bs=6.2, body_gap=0.12))
    arrow(ax, (0.24, 0.60), (0.40, 0.44), color="#666"); arrow(ax, (0.76, 0.60), (0.60, 0.44), color="#666")
    ax.text(0.5, 0.52, "audit: make them agree, row by row", ha="center", va="center", fontsize=6.2, style="italic", color="#444")
    items.append(box(ax, 0.01, 0.01, 0.98, 0.42, "found: an exact identity", ["the reduced Gauss stage, lifted to absolute coordinates,",
                                                                            "satisfies all 132 rows: $F_h(Z_G)=0$.  The method is classical",
                                                                            "Gauss collocation in disguise; sixth order follows from",
                                                                            "known theory; 57 Lean theorems check the algebra."], GREEN, face="#eef7ee", ts=7.2, bs=6.0, body_gap=0.11))
    ax.set_title("(c) the identity that became the theorem", fontsize=7.5, loc="left")
    return items


def fig_problem() -> None:
    fig = plt.figure(figsize=(6.6, 2.4))
    gs = fig.add_gridspec(1, 3, width_ratios=[1.0, 0.95, 1.15], wspace=0.30, left=0.01, right=0.99, top=0.90, bottom=0.16)
    ax0 = fig.add_subplot(gs[0]); ax1 = fig.add_subplot(gs[1]); ax2 = fig.add_subplot(gs[2])
    draw_mechanism(ax0); draw_convergence(ax1); items = draw_identity(ax2)
    fit_texts(fig, ax2, items)
    fig.savefig(FIG / "fig_problem.png", bbox_inches="tight"); plt.close(fig)


# ----------------------------------------------------------------------------------------------
# Figure 2: the process with a worked example
# ----------------------------------------------------------------------------------------------
def fig_process() -> None:
    e4 = json.load(open(RES / "E4_asme.json"))
    dp = [r for r in e4["rows"] if r.get("model") == "double_pendulum"]
    v_first, v_last = dp[0]["final_position"], dp[-1]["final_position"]
    fit = e4["orders"]["double_pendulum"]["final_position"]["fit"]
    fig, ax = plt.subplots(figsize=(6.6, 2.75)); ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    items = []
    steps = [("hypothesis", ["a claim", "to test"], PURPLE),
             ("version dir.", ["vNNN/: README,", "code, results/;", "read-only once", "superseded"], GREEN),
             ("run", ["fixed step grid,", "stated reference;", "heavy runs:", "ask first"], BLUE),
             ("result file", ["JSON/CSV with", "every number", "the paper", "may quote"], ORANGE),
             ("check", ["validator:", "manuscript vs.", "result file; gates", "guard claims"], RED),
             ("manuscript", ["table cell,", "figure, sentence;", "no number", "typed by hand"], GREY)]
    n = len(steps); x0, gap = 0.005, 0.030; w = (0.99 - gap * (n - 1)) / n; y, h = 0.58, 0.40
    xs = []
    for i, (t, lines, c) in enumerate(steps):
        x = x0 + i * (w + gap); xs.append(x)
        items.append(box(ax, x, y, w, h, t, lines, c, face="#fafafa", ts=7.4, bs=6.2, body_gap=0.12))
        if i < n - 1:
            arrow(ax, (x + w + 0.003, y + h / 2), (x + w + gap - 0.003, y + h / 2), color="#444", lw=1.1)
    ye, he = 0.16, 0.34
    ex = [["“the double", "pendulum converges", "at order 6”"],
          ["v049_paper_", "experiments/", "e4_asme_", "mechanisms.py"],
          ["h = 0.1 … 0.1/32;", "reference", "h = 0.1/128;", "fit above 100× floor"],
          ["results/", "E4_asme.json", f"h=0.1: {v_first:.1e}", f"h=0.1/32: {v_last:.1e}", f"fitted order {fit:.1f}"],
          ["validate_", "manuscript.py:", "359 numbers", "checked, LaTeX", "log clean"],
          ["Table 3 of the", "companion paper;", "caption states", "reference and floor"]]
    for i, lines in enumerate(ex):
        items.append(box(ax, xs[i], ye, w, he, "", lines, "#bbb", face="#f4f4f4", bs=6.0, lw=0.8, title_gap=0.05))
        ax.plot([xs[i] + w / 2, xs[i] + w / 2], [y, ye + he], color="#bbb", lw=0.7, ls=":")
    ax.text(0.005, ye + he + 0.015, "one claim, followed through the six steps:", fontsize=6.2, style="italic", color="#555", va="bottom")
    for i, lab in ((0, "human: goal"), (2, "human: authorization"), (5, "human: judgment")):
        arrow(ax, (xs[i] + w / 2, 0.02), (xs[i] + w / 2, ye - 0.005), color=RED, lw=1.0)
        ax.text(xs[i] + w / 2 + 0.012, 0.045, lab, fontsize=5.6, color=RED, ha="left", va="center")
    ax.text(xs[4] + w * 0.32, 0.065, "memory: one file per fact,\nread at the start of every\nsession; informs steps 1–3", fontsize=5.4, color=PURPLE, ha="center", va="center")
    fit_texts(fig, ax, items, min_size=5.4)
    fig.savefig(FIG / "fig_process.png", bbox_inches="tight"); plt.close(fig)


# ----------------------------------------------------------------------------------------------
# Figure 3: exploration tree and the decisive move
# ----------------------------------------------------------------------------------------------
def read_runs(version_glob: str) -> list[dict]:
    p = glob.glob(str(REPO / "numerics" / version_glob / "results" / "*runs.csv"))[0]
    return list(csv.DictReader(open(p, encoding="utf-8")))


NEG_GROUPS = [(4, "Yoshida\nsubsteps"), (17, "trapezoidal, BDF2,\nLobatto endpoint\n(v016–v018)"),
              (24.5, "Lobatto nodes (v024),\nprojection repair\n(v025)"), (33.5, "sparse Newton,\nNewton–Krylov, lagging\n(v031–v033)")]
MILESTONES2 = [(5, "Gauss collocation\nchosen", 1), (13, "first sixth-order\ncandidate", 2), (21, "friction law\nkept", 1),
               (27, "FullVA stage\nsystem", 2), (47, "chain benchmark, accepted\ncode (v047); paper\nexperiments (v049)", 1)]


def fig_tree() -> None:
    rows = []
    for d in sorted((REPO / "numerics").glob("v0*")):
        v = int(d.name[1:4]); py = list(d.glob("*.py"))
        lines = sum(sum(1 for _ in open(p, encoding="utf-8", errors="replace")) for p in py)
        results = sum(1 for _ in (d / "results").rglob("*") if _.is_file()) if (d / "results").exists() else 0
        rows.append((v, d.name, lines, results))
    with open(HERE / "version_table.csv", "w", newline="") as f:
        w = csv.writer(f); w.writerow(["version", "dir", "python_lines", "result_files", "phase", "role"])
        for r in rows:
            w.writerow([*r, phase_of(r[0])[0], "kept" if r[0] in KEPT else "ruled out" if r[0] in RULED_OUT else "infrastructure / diagnostic"])

    fig = plt.figure(figsize=(6.6, 3.7))
    gs = fig.add_gridspec(2, 1, height_ratios=[1.25, 1.0], hspace=0.62, left=0.075, right=0.99, top=0.97, bottom=0.13)
    ax = fig.add_subplot(gs[0]); ax.set_xlim(0, 50.5); ax.set_ylim(-3.1, 4.0); ax.set_yticks([]); ax.spines["left"].set_visible(False)
    for name, rng, col in PHASES:
        ax.axvspan(min(rng) - 0.5, max(rng) + 0.5, color=col, alpha=0.10, lw=0)
        if name == "paper experiments":
            continue
        label = {"validation anchors": "validation\nanchors (+v049)"}.get(name, name.replace(" ", "\n", 1) if len(name) > 14 else name)
        ax.text((min(rng) + max(rng)) / 2, 3.95, label, ha="center", va="top", fontsize=6.0, color=col)
    ax.plot([1, 49], [0, 0], color="#999", lw=1.0, zorder=1)
    for v, *_ in rows:
        if v in RULED_OUT:
            ax.plot([v, v], [0, -0.9], color=RED, lw=0.8); ax.plot(v, -0.9, "x", color=RED, ms=5, mew=1.4)
        elif v in KEPT:
            ax.plot(v, 0, "o", color=GREEN, ms=5, zorder=3)
        else:
            ax.plot(v, 0, "o", color="#bbb", ms=3.2, zorder=2)
    for x, txt in NEG_GROUPS:
        ax.text(min(x, 44.5) if x > 30 else x, -1.2, txt, ha="center", va="top", fontsize=5.6, color=RED)
    for v, txt, lvl in MILESTONES2:
        yy = 0.9 if lvl == 1 else 1.9
        ax.annotate(txt, xy=(v, 0.08), xytext=(v, yy), ha="center", va="bottom", fontsize=6.0, color="#222",
                    arrowprops={"arrowstyle": "-", "color": "#777", "lw": 0.6})
    ax.set_xlabel("version", labelpad=1); ax.set_xticks([1, 5, 10, 15, 20, 25, 30, 35, 40, 45, 49]); ax.tick_params(axis="x", labelsize=6)
    ax.plot([], [], "o", color=GREEN, ms=5, label="kept in the final method"); ax.plot([], [], "o", color="#bbb", ms=3.2, label="infrastructure, diagnostic")
    ax.plot([], [], "x", color=RED, ms=5, mew=1.4, label="ruled out (kept as a negative result)")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.30), ncol=3, fontsize=6.2, frameon=False, handletextpad=0.3, columnspacing=1.2)
    ax.text(-0.5, 3.9, "(a)", fontsize=8.5, weight="bold", va="bottom", ha="right")

    def pick(version_glob, method, h="0.0125"):
        for r in read_runs(version_glob):
            if r["case"] == "absolute_revolute_smooth" and r["method"] == method and r["h"] == h:
                return r
        raise KeyError(method)
    variants = [("v023: Gauss stages,\nendpoint constraints", pick("v023_*", "abs_revolute_gauss6")),
                ("v024: Lobatto nodes", pick("v024_*", "abs_revolute_lobatto6")),
                ("v025: project after\neach step", pick("v025_*", "abs_revolute_gauss6_projected")),
                ("v026: + velocity rows\nat the stages", pick("v026_*", "abs_revolute_gauss6_pivotvc")),
                ("v027: + acceleration\nrows (FullVA)", pick("v027_*", "abs_revolute_gauss6_pivotva"))]
    ax2 = fig.add_subplot(gs[1]); xs = np.arange(len(variants)); wbar = 0.36
    drift, err = [], []
    for _, r in variants:
        if r["status"] != "ok":
            drift.append(np.nan); err.append(np.nan); continue
        drift.append(float(r.get("max_raw_endpoint_velocity_constraint_norm") or r["max_endpoint_velocity_constraint_norm"]))
        err.append(float(r["orientation_error_rad"]))
    drift = np.array(drift); err = np.array(err)
    ax2.bar(xs - wbar / 2, np.nan_to_num(drift, nan=1e-20), wbar, color=RED, alpha=0.85, label="velocity-level constraint violation (before any repair)")
    ax2.bar(xs + wbar / 2, np.nan_to_num(err, nan=1e-20), wbar, color=BLUE, alpha=0.85, label="orientation error at the end of the run")
    ax2.set_yscale("log"); ax2.set_ylim(1e-14, 1e2)
    for i, (_, r) in enumerate(variants):
        if r["status"] != "ok":
            ax2.text(xs[i], 1e-7, "Newton failed\nat every $h$", ha="center", va="center", fontsize=6, color=RED)
    ax2.text(xs[2], err[2] * 8, f"violation hidden, but\nthe error grew {err[2]/err[0]:.0f}×", ha="center", va="bottom", fontsize=6.0, color="#444")
    ax2.text(xs[4], err[4] * 8, f"violation $10^{{{np.log10(drift[0]/drift[4]):.0f}}}\\times$ smaller,\nsame accuracy as v026", ha="center", va="bottom", fontsize=6.0, color="#444")
    ax2.set_xticks(xs); ax2.set_xticklabels([v[0] for v in variants], fontsize=6.4)
    ax2.set_ylabel("maximum over the run", fontsize=7); ax2.grid(True, axis="y", alpha=0.25); ax2.tick_params(axis="y", labelsize=6)
    ax2.legend(loc="upper left", fontsize=6.2, frameon=False, ncol=1)
    ax2.text(-0.85, 3e2, "(b)", fontsize=8.5, weight="bold", va="bottom", ha="right")
    ax2.set_title("the decisive move (v023 → v027), measured on the single revolute joint at $h=0.0125$", fontsize=7.2, pad=3)
    fig.savefig(FIG / "fig_tree.png", bbox_inches="tight"); plt.close(fig)


# ----------------------------------------------------------------------------------------------
# Figure 4: four incidents, what the agent saw against what was true
# ----------------------------------------------------------------------------------------------
def fig_incidents() -> None:
    fig, axes = plt.subplots(1, 4, figsize=(6.6, 2.2))
    fig.subplots_adjust(left=0.065, right=0.995, top=0.84, bottom=0.19, wspace=0.55)
    e1 = json.load(open(RES / "E1_convergence.json"))
    hs = np.array([r["h"] for r in e1["rows"]]); ori = np.array([r["final_orientation"] for r in e1["rows"]])
    acos_version = np.maximum(ori, 2 * np.arccos(1 - 2.0 ** -53))   # arccos of a double rounded to 1: the earlier formula's floor
    ax = axes[0]
    ax.loglog(hs, acos_version, "s--", color=RED, ms=3.5, label="first formula")
    ax.loglog(hs, ori, "o-", color=GREEN, ms=3.5, label="chord formula")
    ax.loglog(hs, ori[0] * (hs / hs[0]) ** 6, ":", color="#333", lw=0.8)
    ax.text(hs[-1] * 1.05, 1.2e-8, "arccos floor:\n$3\\times10^{-8}$ rad", fontsize=5.9, color=RED, ha="left", va="top")
    ax.set_title("Incident 2: orientation error", fontsize=7.4); ax.set_xlabel("$h$", labelpad=0); ax.set_ylabel("error", labelpad=1)
    ax.legend(fontsize=5.9, frameon=False, loc="upper left", bbox_to_anchor=(-0.04, 1.03), handlelength=1.6)
    ax.text(0.97, 0.05, "fitted order:\n2.2 → 6.3", transform=ax.transAxes, fontsize=6.0, color="#333", ha="right")
    z = np.load(FIG / "branch_factor.npz"); t = z["t"]; f = z["factor"]
    ax = axes[1]
    ax.plot(t, f, color=BLUE, lw=1.2); ax.axhline(0, color="#777", lw=0.6)
    ax.axvspan(0, 0.5, color=GREEN, alpha=0.10, lw=0); ax.text(0.25, 0.92, "all chain\nexperiments\nstop at $T=0.5$", ha="center", va="top", fontsize=6.0, color=GREEN)
    zc = t[np.where(np.diff(np.sign(f)) != 0)[0][0]]
    ax.axvline(zc, color=RED, lw=0.8, ls="--")
    ax.text(0.02, -0.62, f"sign change at $t\\approx{zc:.2f}$:\nsliding row degenerates,\nNewton fails soon after", fontsize=5.7, color=RED, ha="left", va="bottom")
    ax.set_xlim(0, 0.7); ax.set_ylim(-0.66, 1.05); ax.set_title("Incident 3: regular branch", fontsize=7.4); ax.set_xlabel("$t$", labelpad=0); ax.set_ylabel("$n_1\\cdot a_1(q)$", labelpad=1)
    e4 = json.load(open(RES / "E4_asme.json"))
    sp = [r for r in e4["rows"] if r.get("model") == "single_pendulum"]
    hs4 = np.array([r["h"] for r in sp]); pos = np.array([r["final_position"] for r in sp]); vel = np.array([r["final_velocity"] for r in sp])
    ax = axes[2]
    ax.loglog(hs4, vel, "s--", color=RED, ms=3.5, label="velocity")
    ax.loglog(hs4, pos, "o-", color=GREEN, ms=3.5, label="position")
    ax.loglog(hs4[:3], pos[0] * (hs4[:3] / hs4[0]) ** 6, ":", color="#333", lw=0.8)
    ax.set_ylim(1e-16, 1e-5); ax.set_title("Incident 4: driven pendulum", fontsize=7.4); ax.set_xlabel("$h$", labelpad=0); ax.set_ylabel("error", labelpad=1)
    ax.legend(fontsize=5.9, frameon=False, loc="upper left", bbox_to_anchor=(-0.04, 1.03), handlelength=1.6)
    ax.text(0.97, 0.05, "velocity = roundoff\n× cond($J$) ≈ $10^{10}$–$10^{13}$", transform=ax.transAxes, fontsize=5.9, color="#333", ha="right")
    e7 = json.load(open(RES / "E7_solver_envelope.json"))
    hs7 = np.array([r["h"] for r in e7["rows"]]); ratio = np.array([r["max_residual_over_h7"] for r in e7["rows"]])
    ax = axes[3]
    ax.loglog(hs7, ratio, "o-", color=BLUE, ms=3.5, label="measured (E7)")
    ax.axhline(1e4, color=RED, lw=0.9, ls="--"); ax.text(hs7[0], 3e3, "claimed bound\n$c_\\eta=10^4$", fontsize=6.0, color=RED, ha="right", va="top")
    ax.text(hs7[-1] * 1.8, ratio.max() * 1.3, f"measured: $10^{{{np.log10(ratio.max()):.1f}}}$\nat the finest $h$", fontsize=6.0, color=BLUE, ha="left", va="center")
    ax.set_ylim(1e-5, 1e9); ax.set_title("Incident 7: solver constant", fontsize=7.4); ax.set_xlabel("$h$", labelpad=0); ax.set_ylabel("accepted residual / $h^7$", labelpad=1)
    ax.legend(fontsize=5.9, frameon=False, loc="lower left", handlelength=1.6)
    for ax, lab in zip(axes, "abcd"):
        ax.text(-0.36, 1.10, f"({lab})", transform=ax.transAxes, fontsize=8.5, weight="bold", va="bottom")
        ax.grid(True, alpha=0.25); ax.tick_params(labelsize=6)
    fig.savefig(FIG / "fig_incidents.png", bbox_inches="tight"); plt.close(fig)


# ----------------------------------------------------------------------------------------------
# Figure 5: the final session
# ----------------------------------------------------------------------------------------------
def classify(cmd: str) -> str:
    c = cmd.lower()
    if "latexmk" in c or "assemble.py" in c or "build_derived" in c or "make_schematics" in c or "build_arxiv" in c:
        return "manuscript build"
    if "validate_" in c:
        return "validators"
    if re.search(r"e[1-7]_[a-z_]+\.py|make_figures|run_public_closed|e45\b|e14\b|e2v2|e4v4", c):
        return "experiments"
    if c.startswith("git ") or " git " in c or c.startswith("gh ") or "~/bin/gh" in c:
        return "git / GitHub"
    if "lake " in c or "lean" in c or "rsync" in c and "proof" in c:
        return "Lean"
    return "inspect / edit"


def load_session():
    proj = Path.home() / ".claude" / "projects"
    files = glob.glob(str(proj / "*uw-paper-integrator-research*" / "*.jsonl"))
    if not files:
        return None
    tools = []; humans = []; cats = collections.Counter(); first = None
    n_asst = n_entries = n_shell = 0
    for f in files:
        with open(f, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                try: d = json.loads(line)
                except Exception: continue
                ts = d.get("timestamp")
                if not ts: continue
                t = datetime.datetime.fromisoformat(ts.replace("Z", "+00:00"))
                first = first or t
                hrs = (t - first).total_seconds() / 3600
                if d.get("type") == "user":
                    c = d.get("message", {}).get("content")
                    if isinstance(c, str): txt = c
                    elif isinstance(c, list) and c and isinstance(c[0], dict) and c[0].get("type") == "text": txt = c[0].get("text", "")
                    else: continue
                    n_entries += 1
                    if d.get("isMeta") or d.get("isCompactSummary"): continue
                    if txt.lstrip().startswith("<bash-input>"): n_shell += 1; continue
                    if txt.lstrip().startswith("<"): continue
                    humans.append((hrs, txt.strip()))
                elif d.get("type") == "assistant":
                    n_asst += 1
                    for blk in d.get("message", {}).get("content", []) or []:
                        if isinstance(blk, dict) and blk.get("type") == "tool_use":
                            tools.append(hrs); name = blk.get("name")
                            cats[classify(blk.get("input", {}).get("command", "")) if name == "Bash" else f"file {name.lower()}"] += 1
    return {"first": first, "tools": np.array(tools), "humans": humans, "cats": cats, "n_asst": n_asst, "n_entries": n_entries, "n_shell": n_shell}


# Events on the session axis (UTC, read from the transcript).  kind: agent | goal | auth | dec | judg
EVENTS = [
    ("2026-09-17T19:53", "goal: can Lean prove the order?", "goal"),
    ("2026-09-17T21:07", "manuscript–code mismatch → identity", "agent"),
    ("2026-09-20T01:44", "57 Lean theorems, axioms clean", "agent"),
    ("2026-09-20T08:06", "arXiv version delivered", "agent"),
    ("2026-09-20T19:50", "“run B4”: external campaign, 0/40", "auth"),
    ("2026-09-21T03:37", "five-folder repository layout", "agent"),
    ("2026-09-21T06:11", "“paper quality feels poor” (I1)", "judg"),
    ("2026-09-21T06:29", "rewrite plan delivered", "agent"),
    ("2026-09-21T06:59", "regular-branch limit found (I3)", "agent"),
    ("2026-09-21T07:27", "“A”: keep the model, $T=0.5$", "dec"),
    ("2026-09-21T08:05", "E7 falsifies claimed constant (I7)", "agent"),
    ("2026-09-21T15:51", "44-page manuscript delivered", "agent"),
    ("2026-09-21T15:55", "“the PDF does not look good”", "judg"),
    ("2026-09-21T20:02", "“top-left panel strange?” (I4)", "judg"),
    ("2026-09-21T20:55", "goal: write this paper", "goal"),
    ("2026-09-22T07:09", "“figures unclear”: this paper redrawn", "judg"),
]


def fig_session() -> None:
    S = load_session()
    if S is None:
        print("no transcript found; skipping session figure"); return
    first = S["first"]; tools = S["tools"]
    fig = plt.figure(figsize=(6.6, 2.6))
    gs = fig.add_gridspec(2, 1, height_ratios=[0.5, 1.0], hspace=0.05, left=0.07, right=0.99, top=0.95, bottom=0.16)
    top = fig.add_subplot(gs[0]); ax = fig.add_subplot(gs[1], sharex=top)
    edges = np.arange(0, np.ceil(tools.max() / 3) * 3 + 3, 3)
    ax.hist(tools, bins=edges, color=BLUE, alpha=0.55)
    ax.set_xlabel("hours since the session started (2026-09-17, 19:51 UTC)", labelpad=1); ax.set_ylabel("agent tool calls\nper 3 h", labelpad=1)
    ax.set_xlim(-1.5, edges[-1]); ax.grid(True, axis="y", alpha=0.25); ax.tick_params(labelsize=6)
    ymax = ax.get_ylim()[1]; ax.set_ylim(0, ymax * 1.05)
    colors = {"agent": "#444", "judg": RED, "dec": PURPLE, "auth": ORANGE, "goal": GREEN}
    ev = sorted(((datetime.datetime.fromisoformat(ts + ":00+00:00") - first).total_seconds() / 3600, txt, kind) for ts, txt, kind in EVENTS)
    # top strip: human messages as ticks, events as numbered markers on two rows
    top.set_ylim(0, 1); top.set_yticks([]); top.tick_params(axis="x", labelbottom=False, length=0)
    for sp in ("left", "bottom"): top.spines[sp].set_visible(False)
    for hrs, _ in S["humans"]:
        top.plot([hrs, hrs], [0.02, 0.22], color="#333", lw=0.8)
    last = [-1e9] * 4
    for i, (x, txt, kind) in enumerate(ev, 1):
        row = next((r for r in range(4) if x - last[r] > 1.6), 0)
        last[row] = x
        yy = (0.30, 0.52, 0.74, 0.96)[row]
        top.plot(x, yy, "o", color=colors[kind], ms=6.8, zorder=3); top.text(x, yy, str(i), ha="center", va="center", fontsize=4.4, color="white", weight="bold", zorder=4)
        ax.axvline(x, color=colors[kind], lw=0.5, ls=":", alpha=0.8)
    # key inside the empty region of the histogram
    key_lines = [f"{i:>2}  {txt}" for i, (x, txt, kind) in enumerate(ev, 1)]
    half = (len(key_lines) + 1) // 2
    for col, chunk in enumerate((key_lines[:half], key_lines[half:])):
        xk = 6.5 + col * 25.0
        for j, line in enumerate(chunk):
            k = col * half + j
            ax.text(xk, ymax * (1.0 - 0.118 * j), line, fontsize=4.9, color=colors[ev[k][2]], ha="left", va="top", family="DejaVu Sans")
    for kind, lab in (("goal", "human goal"), ("auth", "human authorization"), ("dec", "human decision"), ("judg", "human judgment"), ("agent", "agent milestone")):
        top.plot([], [], "o", color=colors[kind], ms=5, label=lab)
    top.plot([], [], "|", color="#333", ms=7, mew=1.0, label=f"message typed by the human ({len(S['humans'])})")
    top.legend(loc="upper left", bbox_to_anchor=(-0.01, 1.32), ncol=6, fontsize=5.4, frameon=False, handletextpad=0.3, columnspacing=1.0)
    fig.savefig(FIG / "fig_session.png", bbox_inches="tight"); plt.close(fig)
    n_user = len(S["humans"]); n_tool = len(tools)
    fmt = lambda n: f"{n:,}".replace(",", "\\,")
    (HERE / "stats.tex").write_text(
        "\\newcommand{\\nHuman}{%d}\n\\newcommand{\\nTurns}{%s}\n\\newcommand{\\nTools}{%s}\n"
        "\\newcommand{\\nEntries}{%d}\n\\newcommand{\\nHarness}{%d}\n\\newcommand{\\nShell}{%d}\n"
        % (n_user, fmt(S["n_asst"]), fmt(n_tool), S["n_entries"], S["n_entries"] - n_user - S["n_shell"], S["n_shell"]))
    json.dump({"human_messages": n_user, "user_role_entries": S["n_entries"], "shell_commands_typed": S["n_shell"],
               "agent_turns": S["n_asst"], "tool_calls": n_tool, "categories": S["cats"].most_common(),
               "human_message_hours": [round(h, 2) for h, _ in S["humans"]]}, open(HERE / "session_stats.json", "w"), indent=1)


if __name__ == "__main__":
    FIG.mkdir(exist_ok=True)
    fig_problem(); fig_process(); fig_tree(); fig_incidents(); fig_session()
    print("figures written to", FIG)
