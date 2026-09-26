#!/usr/bin/env python3
"""Figures for the agentic-research paper.  Every plotted number comes from repository data.

Data plots (matplotlib, vector PDF, STIX/Times to match the ACL body font, designed at print size):
* figures/fig_convergence.pdf : E1 convergence of the final method (Figure 1b);
* figures/fig_tree.pdf        : the 49 versions as an exploration tree, and the decisive move
                                v023 -> v027 read from those versions' run tables (Figure 3);
* figures/fig_incidents.pdf   : four incidents as the agent saw them and as they were (Figure 4);
* figures/fig_session.pdf     : the final session from the transcript, broken axis over the idle
                                days (Figure 5).
Diagrams are TikZ.  figures/mechanism.tikz and figures/identity.tikz are static; figures/process.tikz
is generated here so that the traced numbers (E4 result file) are never typed by hand.
Also writes stats.tex (\\nHuman ...), figures/session_events.tex (the caption key of Figure 5),
session_stats.json and version_table.csv.
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
from matplotlib.lines import Line2D  # noqa: E402
import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
FIG = HERE / "figures"
RES = REPO / "numerics" / "v049_paper_experiments" / "results"

# Validated categorical palette (dataviz reference instance, light mode) and ink tokens.
BLUE, ORANGE, AQUA, VIOLET, RED = "#2a78d6", "#eb6834", "#1baf7a", "#4a3aa7", "#e34948"
INK, INK2, MUTED, GRID, AXIS = "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7"
MK = {"ms": 4.5, "mec": "white", "mew": 0.6}          # markers with a surface ring

plt.rcParams.update({
    "font.family": "serif", "font.serif": ["STIXGeneral"], "mathtext.fontset": "stix",
    "font.size": 8, "axes.titlesize": 8, "axes.labelsize": 8, "legend.fontsize": 7,
    "xtick.labelsize": 7, "ytick.labelsize": 7, "text.color": INK,
    "axes.edgecolor": AXIS, "axes.linewidth": 0.6, "axes.labelcolor": INK,
    "axes.spines.top": False, "axes.spines.right": False,
    "xtick.color": AXIS, "ytick.color": AXIS, "xtick.labelcolor": INK2, "ytick.labelcolor": INK2,
    "xtick.major.width": 0.6, "ytick.major.width": 0.6, "xtick.major.size": 2.5, "ytick.major.size": 2.5,
    "grid.color": GRID, "grid.linewidth": 0.5, "grid.linestyle": "-",
    "lines.linewidth": 1.3, "legend.frameon": False, "legend.handlelength": 1.8,
    "pdf.fonttype": 42, "savefig.dpi": 300,
})

PHASES = [
    ("Lie-group basics", range(1, 6)), ("constrained DAE closure", range(6, 14)),
    ("friction and baselines", range(14, 23)), ("absolute-coordinate FullVA", range(23, 30)),
    ("sparse solver scaling", range(30, 46)), ("validation anchors", range(46, 49)), ("paper exp.", range(49, 50)),
]
# Role of each version in the record, condensed from validation/docs/version_ledger.csv.
KEPT = {5, 8, 10, 12, 13, 19, 21, 26, 27, 29, 42, 43, 44, 46, 47, 49}
RULED_OUT = {4, 16, 17, 18, 24, 25, 31, 32, 33}


def phase_of(v: int) -> str:
    for name, rng in PHASES:
        if v in rng:
            return name
    return "other"


def style(ax, grid_axis="both"):
    ax.grid(True, axis=grid_axis)
    ax.set_axisbelow(True)


# ----------------------------------------------------------------------------------------------
# Figure 1b: convergence of the final method (E1)
# ----------------------------------------------------------------------------------------------
def fig_convergence() -> None:
    e1 = json.load(open(RES / "E1_convergence.json"))
    hs = np.array([r["h"] for r in e1["rows"]])
    pos = np.array([r["final_position"] for r in e1["rows"]]); ori = np.array([r["final_orientation"] for r in e1["rows"]])
    fig, ax = plt.subplots(figsize=(1.85, 1.85))
    ax.loglog(hs, pos[0] * (hs / hs[0]) ** 6, "--", color=INK2, lw=0.8, label="slope 6", zorder=1)
    ax.loglog(hs, pos, "o-", color=BLUE, label="position", zorder=3, **MK)
    ax.loglog(hs, ori, "s-", color=ORANGE, label="orientation", zorder=3, **MK)
    fl = e1["richardson_floor"]["final_position"]
    ax.axhline(fl, color=AXIS, lw=0.6, zorder=0)
    ax.text(hs[0], fl * 1.7, "reference floor", fontsize=6, color=MUTED, ha="right", va="bottom")
    ax.set_xlabel("step size $h$", labelpad=1); ax.set_ylabel("error at $t=0.5$", labelpad=1)
    ax.set_ylim(1e-15, 3e-3); style(ax)
    ax.legend(loc="upper left", fontsize=6.5, borderaxespad=0.1, handletextpad=0.5)
    fig.tight_layout(pad=0.25); fig.savefig(FIG / "fig_convergence.pdf"); plt.close(fig)


# ----------------------------------------------------------------------------------------------
# Figure 2: the process diagram (TikZ, generated so the traced numbers come from the result file)
# ----------------------------------------------------------------------------------------------
PROCESS_TIKZ = r"""% Generated by make_figures.py from results/E4_asme.json; do not edit by hand.
\begin{tikzpicture}[font=\scriptsize, >={Stealth[length=3pt]}, line cap=round,
  stepbox/.style={draw, line width=0.7pt, rounded corners=2pt, align=center, inner sep=3pt, text width=2.18cm, minimum height=1.45cm, fill=white},
  exbox/.style={draw=gray!55, line width=0.4pt, rounded corners=2pt, align=center, inner sep=3pt, text width=2.18cm, minimum height=1.45cm, fill=gray!8}]
  \pgfmathsetmacro{\dx}{2.64}
  \node[stepbox, draw=vizviolet] (s1) at (0,0) {\textbf{hypothesis}\\[2pt] a claim to test};
  \node[stepbox, draw=vizaqua!70!black] (s2) at (\dx,0) {\textbf{version directory}\\[2pt] \texttt{vNNN/}: README, code, results; read-only once superseded};
  \node[stepbox, draw=vizblue] (s3) at (2*\dx,0) {\textbf{run}\\[2pt] fixed step grid, stated reference; heavy runs need authorization};
  \node[stepbox, draw=vizorange] (s4) at (3*\dx,0) {\textbf{result file}\\[2pt] JSON or CSV holding every number the paper may quote};
  \node[stepbox, draw=vizred] (s5) at (4*\dx,0) {\textbf{check}\\[2pt] validator: manuscript against result file; gates guard strong claims};
  \node[stepbox, draw=gray!60!black] (s6) at (5*\dx,0) {\textbf{manuscript}\\[2pt] table cell, figure, sentence; no number typed by hand};
  \foreach \i/\j in {1/2,2/3,3/4,4/5,5/6} \draw[->, line width=0.7pt, inkgray] (s\i) -- (s\j);
  \node[exbox] (e1) at (0,-2.15) {``the double pendulum converges at order 6''};
  \node[exbox] (e2) at (\dx,-2.15) {\texttt{v049\_paper\_}\\ \texttt{experiments/}\\ \texttt{e4\_asme\_}\\ \texttt{mechanisms.py}};
  \node[exbox] (e3) at (2*\dx,-2.15) {$h$ from 0.1 to 0.1/32; reference at 0.1/128; order fitted only above 100$\times$ floor};
  \node[exbox] (e4) at (3*\dx,-2.15) {\texttt{results/}\\ \texttt{E4\_asme.json}\\ $h{=}0.1$: $@VFIRST@$\\ $h{=}0.1/32$: $@VLAST@$\\ fitted order @FIT@};
  \node[exbox] (e5) at (4*\dx,-2.15) {\texttt{validate\_}\\ \texttt{manuscript.py}\\ 359 numbers checked, LaTeX log clean};
  \node[exbox] (e6) at (5*\dx,-2.15) {Table~3 of the companion paper; the caption states reference and floor};
  \foreach \i in {1,...,6} \draw[gray!55, densely dotted, line width=0.5pt] (s\i.south) -- (e\i.north);
  \node[anchor=south west, inkgray, font=\scriptsize\itshape] at ($(e1.north west)+(0,0.04)$) {one claim, followed through the six steps:};
  \foreach \i/\t in {1/{human: goal}, 3/{human: authorization}, 6/{human: judgment}} {
    \draw[->, vizred, line width=0.7pt] ($(e\i.south)+(0,-0.55)$) -- ($(e\i.south)+(0,-0.06)$);
    \node[anchor=north, inkgray] at ($(e\i.south)+(0,-0.58)$) {\t};
  }
  \node[anchor=north, inkgray, align=center, text width=4.6cm] at ($(e4.south)!0.5!(e5.south)+(0,-0.12)$) {memory: one file per fact, read at the start of\\ every session; it informs the first three steps};
\end{tikzpicture}%
"""


def sci(x: float) -> str:
    m, e = f"{x:.1e}".split("e")
    return f"{m}\\cdot10^{{{int(e)}}}"


def write_process_tikz() -> None:
    e4 = json.load(open(RES / "E4_asme.json"))
    dp = [r for r in e4["rows"] if r.get("model") == "double_pendulum"]
    fit = e4["orders"]["double_pendulum"]["final_position"]["fit"]
    tex = PROCESS_TIKZ.replace("@VFIRST@", sci(dp[0]["final_position"])).replace("@VLAST@", sci(dp[-1]["final_position"])).replace("@FIT@", f"{fit:.1f}")
    (FIG / "process.tikz").write_text(tex, encoding="utf-8")


# ----------------------------------------------------------------------------------------------
# Figure 3: exploration tree and the decisive move
# ----------------------------------------------------------------------------------------------
def read_runs(version_glob: str) -> list[dict]:
    p = glob.glob(str(REPO / "numerics" / version_glob / "results" / "*runs.csv"))[0]
    return list(csv.DictReader(open(p, encoding="utf-8")))


MILESTONES = [(5, "Gauss collocation\nchosen", 1.0), (13, "first sixth-order\ncandidate", 1.75), (21, "friction law\nkept", 1.0),
              (27, "FullVA stage\nsystem", 1.75), (47, "chain benchmark,\naccepted code", 1.0)]
NEGATIVE = [(4, "Yoshida\nsubsteps"), (17, "trapezoidal, BDF2,\nLobatto endpoint"), (24.5, "Lobatto nodes;\nprojection repair"),
            (32, "sparse Newton; Newton–\nKrylov; Jacobian lagging")]


PHASE_LABELS = [("Lie-group basics", 1, 5), ("constrained DAE closure", 6, 13), ("friction and baselines", 14, 22),
                ("absolute-coordinate FullVA", 23, 29), ("sparse solver scaling", 30, 45), ("validation anchors,\npaper experiments", 46, 49)]


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
            w.writerow([*r, phase_of(r[0]), "kept" if r[0] in KEPT else "ruled out" if r[0] in RULED_OUT else "infrastructure / diagnostic"])

    fig = plt.figure(figsize=(6.3, 3.6))
    ax = fig.add_axes([0.075, 0.52, 0.92, 0.44]); ax.set_xlim(0.2, 49.8); ax.set_ylim(-2.4, 3.3)
    ax.set_yticks([]); ax.spines["left"].set_visible(False); ax.spines["bottom"].set_visible(False)
    for k, (name, lo, hi) in enumerate(PHASE_LABELS):
        if k % 2 == 0:
            ax.axvspan(lo - 0.5, hi + 0.5, color="#f1f1ee", lw=0, zorder=0)
        yy = 3.3 if k % 2 == 0 else 2.75
        ax.text(min((lo + hi) / 2, 49.8) if k < 5 else 49.8, yy, name, ha="center" if k < 5 else "right", va="top", fontsize=6.3, color=INK2, linespacing=1.05)
    ax.plot([1, 49], [0, 0], color=AXIS, lw=0.8, zorder=1)
    for v, *_ in rows:
        if v in RULED_OUT:
            ax.plot([v, v], [0, -0.65], color=RED, lw=0.7, zorder=2); ax.plot(v, -0.65, "x", color=RED, ms=5, mew=1.2, zorder=3)
        elif v in KEPT:
            ax.plot(v, 0, "o", color=AQUA, ms=6.5, mec="white", mew=0.6, zorder=4)
        else:
            ax.plot(v, 0, "o", color=MUTED, ms=3.6, mec="white", mew=0.4, zorder=3)
    for x, txt in NEGATIVE:
        ax.text(x, -0.95, txt, ha="center", va="top", fontsize=6.2, color=INK2, linespacing=1.1)
    for v, txt, yy in MILESTONES:
        ax.annotate(txt, xy=(v, 0.12), xytext=(v, yy), ha="center", va="bottom", fontsize=6.4, color=INK, linespacing=1.1,
                    arrowprops={"arrowstyle": "-", "color": INK2, "lw": 0.5})
    ax.set_xticks([1, 5, 10, 15, 20, 25, 30, 35, 40, 45, 49]); ax.tick_params(axis="x", length=0, pad=1)
    ax.set_xlabel("version", labelpad=1)
    handles = [Line2D([], [], marker="o", color=AQUA, ls="", ms=6.5, mec="white", label="kept in the final method"),
               Line2D([], [], marker="o", color=MUTED, ls="", ms=3.6, label="infrastructure or diagnostic"),
               Line2D([], [], marker="x", color=RED, ls="", ms=5, mew=1.2, label="ruled out, kept as a negative result")]
    fig.legend(handles=handles, loc="center", bbox_to_anchor=(0.53, 0.445), ncol=3, fontsize=6.6, handletextpad=0.4, columnspacing=1.6)
    ax.text(-0.012, 1.0, "(a)", transform=ax.transAxes, fontsize=8, weight="bold", ha="right", va="top")

    def pick(version_glob, method, h="0.0125"):
        for r in read_runs(version_glob):
            if r["case"] == "absolute_revolute_smooth" and r["method"] == method and r["h"] == h:
                return r
        raise KeyError(method)
    variants = [("v023\nGauss stages,\nendpoint constraints", pick("v023_*", "abs_revolute_gauss6")),
                ("v024\nLobatto nodes", pick("v024_*", "abs_revolute_lobatto6")),
                ("v025\nproject after\neach step", pick("v025_*", "abs_revolute_gauss6_projected")),
                ("v026\n+ velocity rows\nat the stages", pick("v026_*", "abs_revolute_gauss6_pivotvc")),
                ("v027\n+ acceleration rows\n(FullVA)", pick("v027_*", "abs_revolute_gauss6_pivotva"))]
    ax2 = fig.add_axes([0.075, 0.1, 0.92, 0.3]); xs = np.arange(len(variants)); wbar = 0.3
    drift, err = [], []
    for _, r in variants:
        ok = r["status"] == "ok"
        drift.append(float(r.get("max_raw_endpoint_velocity_constraint_norm") or r["max_endpoint_velocity_constraint_norm"]) if ok else np.nan)
        err.append(float(r["orientation_error_rad"]) if ok else np.nan)
    drift = np.array(drift); err = np.array(err)
    ax2.bar(xs - wbar / 2 - 0.01, np.nan_to_num(drift, nan=1e-30), wbar, color=BLUE, lw=0, label="velocity-level constraint violation, before any repair")
    ax2.bar(xs + wbar / 2 + 0.01, np.nan_to_num(err, nan=1e-30), wbar, color=ORANGE, lw=0, label="orientation error at the end of the run")
    ax2.set_yscale("log"); ax2.set_ylim(1e-14, 1e0); style(ax2, "y")
    ax2.text(xs[1], 3e-7, "Newton failed\nat every $h$", ha="center", va="center", fontsize=6.4, color=INK2, linespacing=1.1)
    ax2.text(xs[2], err[2] * 6, f"error grew {err[2]/err[0]:.0f}$\\times$", ha="center", va="bottom", fontsize=6.4, color=INK2)
    ax2.text(xs[4] - wbar / 2, drift[4] * 6, f"violation\n$10^{{{np.log10(drift[0]/drift[4]):.0f}}}\\times$ smaller", ha="center", va="bottom", fontsize=6.4, color=INK2, linespacing=1.1)
    ax2.set_xticks(xs); ax2.set_xticklabels([v[0] for v in variants], fontsize=6.6, linespacing=1.1); ax2.tick_params(axis="x", length=0, pad=2)
    ax2.set_ylabel("maximum over the run", labelpad=1)
    ax2.legend(loc="upper right", fontsize=6.6, handlelength=1.2, handleheight=0.8, borderaxespad=0.1)
    ax2.text(-0.012, 1.0, "(b)", transform=ax2.transAxes, fontsize=8, weight="bold", ha="right", va="top")
    fig.savefig(FIG / "fig_tree.pdf"); plt.close(fig)


# ----------------------------------------------------------------------------------------------
# Figure 4: four incidents, what the agent saw against what was true
# ----------------------------------------------------------------------------------------------
def fig_incidents() -> None:
    fig, axes = plt.subplots(1, 4, figsize=(6.3, 2.0))
    fig.subplots_adjust(left=0.07, right=0.99, top=0.88, bottom=0.19, wspace=0.62)
    e1 = json.load(open(RES / "E1_convergence.json"))
    hs = np.array([r["h"] for r in e1["rows"]]); ori = np.array([r["final_orientation"] for r in e1["rows"]])
    floor = 2 * np.arccos(1 - 2.0 ** -53)                      # smallest angle arccos of a double resolves
    ax = axes[0]
    ax.loglog(hs, ori[0] * (hs / hs[0]) ** 6, ":", color=INK2, lw=0.7, zorder=1)
    ax.loglog(hs, np.maximum(ori, floor), "s--", color=ORANGE, label="first formula", zorder=3, **MK)
    ax.loglog(hs, ori, "o-", color=BLUE, label="chord formula", zorder=4, **MK)
    ax.text(hs[-1], floor * 2.6, "arccos floor $3{\\times}10^{-8}$", fontsize=6, color=INK2, ha="left", va="bottom")
    ax.set_ylim(1e-14, 1e-3); ax.set_title("(a) Incident 2", loc="left", fontsize=7.5, pad=3)
    ax.set_xlabel("$h$", labelpad=0); ax.set_ylabel("error", labelpad=1)
    ax.legend(loc="upper left", fontsize=6.2, borderaxespad=0.05, handletextpad=0.5)
    z = np.load(FIG / "branch_factor.npz"); t = z["t"]; f = z["factor"]
    zc = t[np.where(np.diff(np.sign(f)) != 0)[0][0]]
    ax = axes[1]
    ax.axvspan(0, 0.5, color=AQUA, alpha=0.09, lw=0, zorder=0)
    ax.plot(t, f, color=BLUE, lw=1.3, zorder=3); ax.axhline(0, color=AXIS, lw=0.6, zorder=1)
    ax.axvline(zc, color=INK2, lw=0.6, zorder=2)
    ax.text(0.25, 0.88, "chain experiments\nstop at $T=0.5$", ha="center", va="top", fontsize=6.2, color=INK2, linespacing=1.1)
    ax.text(0.03, -0.44, f"sign change at\n$t\\approx{zc:.2f}$; Newton\nfails soon after", ha="left", va="bottom", fontsize=6.2, color=INK2, linespacing=1.1)
    ax.set_xlim(0, 0.7); ax.set_ylim(-0.5, 1.05); ax.set_title("(b) Incident 3", loc="left", fontsize=7.5, pad=3)
    ax.set_xlabel("$t$", labelpad=0); ax.set_ylabel("$n_1\\cdot a_1(q)$", labelpad=1)
    e4 = json.load(open(RES / "E4_asme.json"))
    sp = [r for r in e4["rows"] if r.get("model") == "single_pendulum"]
    hs4 = np.array([r["h"] for r in sp]); pos = np.array([r["final_position"] for r in sp]); vel = np.array([r["final_velocity"] for r in sp])
    ax = axes[2]
    ax.loglog(hs4[:3], pos[0] * (hs4[:3] / hs4[0]) ** 6, ":", color=INK2, lw=0.7, zorder=1)
    ax.loglog(hs4, vel, "s--", color=ORANGE, label="velocity", zorder=3, **MK)
    ax.loglog(hs4, pos, "o-", color=BLUE, label="position", zorder=4, **MK)
    ax.set_ylim(1e-16, 1e-5); ax.set_title("(c) Incident 4", loc="left", fontsize=7.5, pad=3)
    ax.set_xlabel("$h$", labelpad=0); ax.set_ylabel("error", labelpad=1)
    ax.legend(loc="upper left", fontsize=6.2, borderaxespad=0.05, handletextpad=0.5)
    e7 = json.load(open(RES / "E7_solver_envelope.json"))
    hs7 = np.array([r["h"] for r in e7["rows"]]); ratio = np.array([r["max_residual_over_h7"] for r in e7["rows"]])
    ax = axes[3]
    ax.axhline(1e4, color=INK2, lw=0.7, ls="--", zorder=1)
    ax.text(hs7[0], 1e4 * 2.4, "claimed bound\n$c_\\eta=10^{4}$", fontsize=6.2, color=INK2, ha="right", va="bottom", linespacing=1.1)
    ax.loglog(hs7, ratio, "o-", color=BLUE, zorder=3, **MK)
    ax.annotate(f"$10^{{{np.log10(ratio.max()):.1f}}}$", (hs7[-1], ratio.max()), xytext=(5, -1), textcoords="offset points", fontsize=6.6, color=INK, va="center")
    ax.set_ylim(1e-5, 1e9); ax.set_title("(d) Incident 7", loc="left", fontsize=7.5, pad=3)
    ax.set_xlabel("$h$", labelpad=0); ax.set_ylabel("accepted residual / $h^7$", labelpad=1)
    for ax in axes:
        style(ax)
    fig.savefig(FIG / "fig_incidents.pdf"); plt.close(fig)


# ----------------------------------------------------------------------------------------------
# Figure 5: the final session
# ----------------------------------------------------------------------------------------------
def classify(cmd: str) -> str:
    c = cmd.lower()
    if "latexmk" in c or "assemble.py" in c or "build_derived" in c or "make_schematics" in c or "build_arxiv" in c:
        return "manuscript build"
    if "validate_" in c:
        return "validators"
    if re.search(r"e[1-7]_[a-z_]+\.py|make_figures|run_public_closed|compute_branch|e45\b|e14\b|e2v2|e4v4", c):
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
    ("2026-09-17T21:07", "manuscript--code mismatch found: the identity", "agent"),
    ("2026-09-20T01:44", "57 Lean theorems, axiom audit clean", "agent"),
    ("2026-09-20T08:06", "arXiv version delivered", "agent"),
    ("2026-09-20T19:50", "``run B4'': external campaign, 0/40 rows", "auth"),
    ("2026-09-21T03:37", "five-folder repository layout", "agent"),
    ("2026-09-21T06:11", "``the paper quality feels poor'' (Incident~1)", "judg"),
    ("2026-09-21T06:29", "rewrite plan delivered for approval", "agent"),
    ("2026-09-21T06:59", "regular-branch limit found (Incident~3)", "agent"),
    ("2026-09-21T07:27", "``A'': keep the model, $T=0.5$", "dec"),
    ("2026-09-21T08:05", "E7 written; claimed constant falsified (Incident~7)", "agent"),
    ("2026-09-21T15:51", "rewritten 44-page manuscript delivered", "agent"),
    ("2026-09-21T15:55", "``the PDF does not look good''", "judg"),
    ("2026-09-21T20:02", "``why is the top-left panel strange?'' (Incident~4)", "judg"),
    ("2026-09-21T20:55", "goal: write this paper", "goal"),
    ("2026-09-22T07:09", "``figures and content unclear'': this paper redrawn", "judg"),
    ("2026-09-26T19:15", "``the figures are too poor'': figures redrawn as vector graphics", "judg"),
]
KIND_COLOR = {"agent": INK2, "goal": AQUA, "auth": ORANGE, "dec": VIOLET, "judg": RED}
KIND_LABEL = {"goal": "human goal", "auth": "human authorization", "dec": "human decision", "judg": "human judgment", "agent": "agent milestone"}


def fig_session() -> None:
    S = load_session()
    if S is None:
        print("no transcript found; skipping session figure"); return
    first = S["first"]; tools = np.sort(S["tools"])
    ev = sorted(((datetime.datetime.fromisoformat(ts + ":00+00:00") - first).total_seconds() / 3600, txt, kind) for ts, txt, kind in EVENTS)
    # break the axis at the longest idle gap (> 24 h) between tool calls
    gaps = np.diff(tools); k = int(np.argmax(gaps))
    if gaps[k] > 24:
        segs = [(-2.0, np.ceil((tools[k] + 1) / 3) * 3), (np.floor((tools[k + 1] - 2) / 3) * 3, np.ceil((tools[-1] + 1) / 3) * 3)]
    else:
        segs = [(-2.0, np.ceil((tools[-1] + 1) / 3) * 3)]
    widths = [max(seg[1] - seg[0], 12.0) for seg in segs]
    fig = plt.figure(figsize=(6.3, 2.15))
    gs = fig.add_gridspec(2, len(segs), height_ratios=[0.55, 1.0], width_ratios=widths, hspace=0.06, wspace=0.05,
                          left=0.075, right=0.995, top=0.90, bottom=0.17)
    strips, plots = [], []
    for j, (lo, hi) in enumerate(segs):
        top = fig.add_subplot(gs[0, j]); ax = fig.add_subplot(gs[1, j], sharex=top)
        edges = np.arange(max(lo, 0.0), hi + 3, 3)
        ax.hist(tools, bins=edges, color="#5598e7", edgecolor="white", linewidth=0.5, zorder=3)
        ax.set_xlim(lo, hi); style(ax, "y")
        ax.set_xticks(np.arange(np.ceil(lo / 6) * 6, hi + 0.1, 6 if hi - lo < 30 else 20))
        top.set_xlim(lo, hi); top.set_ylim(0, 1); top.set_yticks([]); top.tick_params(axis="x", labelbottom=False, length=0)
        for sp in ("left", "bottom", "top", "right"): top.spines[sp].set_visible(False)
        for hrs, _ in S["humans"]:
            if lo <= hrs <= hi: top.plot([hrs, hrs], [0.02, 0.2], color=INK, lw=0.8, zorder=2)
        strips.append(top); plots.append(ax)
    ymax = max(ax.get_ylim()[1] for ax in plots)
    for ax in plots: ax.set_ylim(0, ymax)
    for j in range(1, len(segs)):
        plots[j].spines["left"].set_visible(False); plots[j].tick_params(axis="y", length=0, labelleft=False)
        strips[j].tick_params(labelleft=False)
        # break marks
        for a in (plots[j - 1],):
            a.spines["right"].set_visible(False)
        d = 0.012
        for a, x in ((plots[j - 1], 1.0), (plots[j], 0.0)):
            a.plot([x - d, x + d], [-0.02, 0.02], transform=a.transAxes, color=AXIS, lw=0.8, clip_on=False)
    last = [-1e9] * 4
    for i, (x, txt, kind) in enumerate(ev, 1):
        seg = next((j for j, (lo, hi) in enumerate(segs) if lo <= x <= hi), None)
        if seg is None: continue
        row = next((r for r in range(4) if x - last[r] > 1.9), 0); last[row] = x
        yy = (0.3, 0.52, 0.74, 0.96)[row]
        strips[seg].plot(x, yy, "o", color=KIND_COLOR[kind], ms=6.8, mec="white", mew=0.5, zorder=3, clip_on=False)
        strips[seg].text(x, yy, str(i), ha="center", va="center", fontsize=4.4, color="white", weight="bold", zorder=4, clip_on=False)
        plots[seg].axvline(x, color=KIND_COLOR[kind], lw=0.6, alpha=0.55, zorder=2)
    plots[0].set_ylabel("agent tool calls\nper 3 h", labelpad=1)
    fig.text(0.5, 0.01, "hours since the session started (2026-09-17, 19:51 UTC)", ha="center", va="bottom", fontsize=8)
    handles = [Line2D([], [], marker="o", ls="", color=KIND_COLOR[k], ms=6, label=KIND_LABEL[k]) for k in ("goal", "auth", "dec", "judg", "agent")]
    handles.append(Line2D([], [], marker="|", ls="", color=INK, ms=7, mew=0.9, label=f"message typed by the human ({len(S['humans'])})"))
    strips[0].legend(handles=handles, loc="lower left", bbox_to_anchor=(-0.01, 1.02), ncol=6, fontsize=6.2, handletextpad=0.3, columnspacing=1.1, borderaxespad=0)
    fig.savefig(FIG / "fig_session.pdf"); plt.close(fig)
    # caption key and statistics
    key = "; ".join(f"\\textbf{{{i}}}~{txt} ({x:.0f}\\,h)" for i, (x, txt, kind) in enumerate(ev, 1))
    (FIG / "session_events.tex").write_text("\\newcommand{\\sessionEvents}{" + key + "}\n", encoding="utf-8")
    n_user = len(S["humans"]); n_tool = len(tools)
    fmt = lambda n: f"{n:,}".replace(",", "\\,")
    (HERE / "stats.tex").write_text(
        "\\newcommand{\\nHuman}{%d}\n\\newcommand{\\nTurns}{%s}\n\\newcommand{\\nTools}{%s}\n"
        "\\newcommand{\\nEntries}{%d}\n\\newcommand{\\nHarness}{%d}\n\\newcommand{\\nShell}{%d}\n"
        % (n_user, fmt(S["n_asst"]), fmt(n_tool), S["n_entries"], S["n_entries"] - n_user - S["n_shell"], S["n_shell"]))
    json.dump({"human_messages": n_user, "user_role_entries": S["n_entries"], "shell_commands_typed": S["n_shell"],
               "agent_turns": S["n_asst"], "tool_calls": n_tool, "categories": S["cats"].most_common(),
               "human_message_hours": [round(h, 2) for h, _ in S["humans"]], "axis_segments_hours": segs},
              open(HERE / "session_stats.json", "w"), indent=1, default=float)


if __name__ == "__main__":
    FIG.mkdir(exist_ok=True)
    fig_convergence(); write_process_tikz(); fig_tree(); fig_incidents(); fig_session()
    print("figures written to", FIG)
