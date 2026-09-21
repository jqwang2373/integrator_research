#!/usr/bin/env python3
"""Draw the manuscript figures from the result files (results/E*.json); no computation.

Every figure of the numerical section is produced here from the JSON written by the experiment
scripts, so the figures can be restyled without rerunning anything.  Writes results/E*.png.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

RESULTS = Path(__file__).resolve().parent / "results"

plt.rcParams.update({
    "font.size": 9.5, "axes.titlesize": 10, "axes.labelsize": 9.5, "legend.fontsize": 8,
    "xtick.labelsize": 8.5, "ytick.labelsize": 8.5, "lines.markersize": 4.5, "lines.linewidth": 1.3,
    "figure.dpi": 220, "savefig.dpi": 220, "axes.grid": True, "grid.alpha": 0.3,
})
W = 6.4  # figure width in inches: the text column of the manuscript


def load(name: str) -> dict | None:
    path = RESULTS / name
    return json.loads(path.read_text()) if path.exists() else None


def slope_line(ax, hs, anchor_err, anchor_h, order, **kw):
    hs = np.asarray(hs, float)
    ax.loglog(hs, anchor_err * (hs / anchor_h) ** order, "k--", lw=0.9, **kw)


def fig_e1(d: dict) -> None:
    rows = [r for r in d["rows"] if r["converged"]]
    hs = [r["h"] for r in rows]
    fig, axes = plt.subplots(1, 2, figsize=(W, 3.0))
    labels = {"position": "position", "orientation": "orientation", "velocity": "velocity", "angular_velocity": "angular velocity"}
    markers = {"position": "o", "orientation": "s", "velocity": "^", "angular_velocity": "v"}
    for ax, prefix, title in zip(axes, ("final", "linf"), (r"error at $t=T$", r"$L^\infty$ error over $[0,T]$")):
        for q, lab in labels.items():
            ax.loglog(hs, [r[f"{prefix}_{q}"] for r in rows], marker=markers[q], label=lab)
        slope_line(ax, hs, rows[-1][f"{prefix}_position"], hs[-1], 6, label="slope 6")
        ax.axhline(d["richardson_floor"][f"{prefix}_position"], color="grey", ls=":", lw=1.0, label="reference floor")
        ax.set_xlabel("$h$"); ax.set_title(title)
    axes[0].set_ylabel("error"); axes[1].legend(loc="lower right")
    fig.tight_layout(); fig.savefig(RESULTS / "E1_convergence.png"); plt.close(fig)


def fig_e2(d: dict) -> None:
    order = {1: 2, 2: 4, 3: 6}
    fig, axes = plt.subplots(1, 2, figsize=(W, 3.0))
    for stages in (1, 2, 3):
        ok = [r for r in d["rows"] if r["stages"] == stages and r["converged"]]
        lab = f"{stages} stage{'s' if stages > 1 else ''} (order {order[stages]})"
        axes[0].loglog([r["h"] for r in ok], [r["final_position"] for r in ok], marker="o", label=lab)
        axes[1].loglog([r["total_newton_iterations"] for r in ok], [r["final_position"] for r in ok], marker="o", label=lab)
    ok3 = [r for r in d["rows"] if r["stages"] == 3 and r["converged"]]
    slope_line(axes[0], [r["h"] for r in ok3], ok3[-1]["final_position"], ok3[-1]["h"], 6, label="slope 6")
    axes[0].set_xlabel("$h$"); axes[0].set_ylabel("position error at $t=T$"); axes[0].set_title("convergence")
    axes[1].set_xlabel("total Newton iterations"); axes[1].set_title("work/precision")
    for ax in axes:
        ax.axhline(d["richardson_floor"]["final_position"], color="grey", ls=":", lw=1.0)
    axes[0].legend(loc="lower right")
    fig.tight_layout(); fig.savefig(RESULTS / "E2_gauss_family.png"); plt.close(fig)


def fig_e3(d: dict) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(W, 3.0))
    vs_list = [s["stribeck_velocity"] for s in d["summary"]]
    for vs in vs_list:
        ok = [r for r in d["rows"] if r["stribeck_velocity"] == vs and r["converged"]]
        axes[0].loglog([r["h"] for r in ok], [r["final_position"] for r in ok], marker="o", label=f"$v_s={vs:g}$")
    base = [r for r in d["rows"] if r["stribeck_velocity"] == vs_list[0] and r["converged"]][-1]
    slope_line(axes[0], d["h_values"], base["final_position"], base["h"], 6, label="slope 6")
    axes[0].set_xlabel("$h$"); axes[0].set_ylabel("position error at $t=T$"); axes[0].set_title("convergence by friction sharpness")
    axes[0].legend(loc="lower right")
    axes[1].semilogx(vs_list, [s["position_fit"] for s in d["summary"]], "o-", label="fitted position order")
    axes[1].semilogx(vs_list, [s["velocity_fit"] for s in d["summary"]], "s--", label="fitted velocity order")
    axes[1].semilogx(vs_list, [s["position_pairwise"][-1] for s in d["summary"]], "^:", label="finest pairwise order")
    axes[1].axhline(6, color="k", lw=0.9, ls=":")
    axes[1].set_xlabel("Stribeck velocity $v_s$"); axes[1].set_ylabel("observed order"); axes[1].set_title("observed order vs friction sharpness")
    axes[1].legend(loc="lower right")
    fig.tight_layout(); fig.savefig(RESULTS / "E3_friction_sweep.png"); plt.close(fig)


def fig_e4(d: dict) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(W, 5.6))
    titles = {"single_pendulum": "driven single pendulum (reconstruction only)", "double_pendulum": "double pendulum ($h_{\\rm ref}=0.1/128$)",
              "four_link": "four-link loop (driven)", "slider_crank": "slider-crank (driven)"}
    for ax, model in zip(axes.ravel(), titles):
        rows = [r for r in d["rows"] if r["model"] == model and r.get("status", "ok") in ("ok", "") and not r.get("is_floor_row")]
        hs = np.array([r["h"] for r in rows])
        if model == "single_pendulum":
            keys, labs = ["final_position", "final_orientation"], ("position", "orientation")
        elif model == "double_pendulum":
            keys, labs = ["final_position", "final_velocity"], ("position", "velocity")
        else:
            keys, labs = ["linf_position", "linf_velocity"], ("position", "velocity")
        for k, lab, mk in zip(keys, labs, ("o", "^")):
            ax.loglog(hs, [r[k] for r in rows], marker=mk, label=lab)
        if model == "double_pendulum":
            slope_line(ax, hs, rows[-1][keys[0]], hs[-1], 6, label="slope 6")
        if model == "single_pendulum":
            slope_line(ax, hs[:3], rows[2][keys[0]], hs[2], 6, label="slope 6")
        ax.set_title(titles[model]); ax.set_xlabel("$h$"); ax.set_ylabel("error at $t=T$" if model.endswith("pendulum") else "trajectory $L^\\infty$ error")
        if not model.endswith("pendulum"):
            ax.set_ylim(1e-16, 1e-12)
        ax.legend(loc="best")
    fig.tight_layout(); fig.savefig(RESULTS / "E4_asme.png"); plt.close(fig)


def fig_e5(d: dict) -> None:
    rows = d["double_pendulum_rows"]
    styles = {"Gauss6/FullVA": dict(marker="o", color="C3", lw=1.8), "2021 public rA": dict(marker="s", color="C0"),
              "2021 public rp": dict(marker="^", color="C1"), "2021 public reps": dict(marker="v", color="C2"),
              "2022 half-implicit rA": dict(marker="D", color="C4"), "2022 half-implicit rA_half": dict(marker="P", color="C5")}
    fig, axes = plt.subplots(1, 2, figsize=(W, 3.5))
    for method, st in styles.items():
        ok = [r for r in rows if r["method"] == method and r["status"] == "ok" and np.isfinite(r["pos_final_linf"]) and r["pos_final_linf"] > 0]
        if not ok:
            continue
        hs = [r["h"] for r in ok]
        axes[0].loglog(hs, [r["pos_final_linf"] for r in ok], label=method, **st)
        axes[1].loglog(hs, [r["vel_final_linf"] for r in ok], label=method, **st)
    axes[0].set_xlabel("$h$"); axes[0].set_ylabel("final position error ($L^\\infty$)"); axes[0].set_title("double pendulum, $T=3$: position")
    axes[1].set_xlabel("$h$"); axes[1].set_ylabel("final velocity error ($L^\\infty$)"); axes[1].set_title("velocity")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=3, fontsize=7.5, frameon=False, bbox_to_anchor=(0.5, -0.01))
    fig.tight_layout(rect=(0, 0.12, 1, 1)); fig.savefig(RESULTS / "E5_double_pendulum.png"); plt.close(fig)


def fig_e6(d6: dict) -> None:
    series_path = RESULTS / "E6_series.npz"
    fig, axes = plt.subplots(1, 2, figsize=(W, 3.0))
    if series_path.exists():
        z = np.load(series_path)
        t = z["t"]; drift = z["drift_conservative"]
        axes[0].semilogy(t, np.maximum(drift, 1e-17), color="C0")
        for name, style, col, lab in (("conservative", "-", "C0", "conservative"), ("smooth_friction", "--", "C1", "frictional")):
            axes[1].semilogy(t[1:], np.maximum(z[f"constraint_{name}"], 1e-17), style, color=col, label=f"position level, {lab}")
            axes[1].semilogy(t[1:], np.maximum(z[f"velocity_constraint_{name}"], 1e-17), style, color=col, alpha=0.45, label=f"velocity level, {lab}")
    axes[0].set_title("relative energy error, conservative variant"); axes[0].set_xlabel("$t$")
    axes[1].set_title("endpoint constraint norms"); axes[1].set_xlabel("$t$"); axes[1].legend(loc="lower right", fontsize=6.8)
    fig.tight_layout(); fig.savefig(RESULTS / "E6_long_time.png"); plt.close(fig)


def main() -> int:
    made = []
    for name, fn in (("E1_convergence.json", fig_e1), ("E2_gauss_family.json", fig_e2), ("E3_friction_sweep.json", fig_e3),
                     ("E4_asme.json", fig_e4), ("E5_public_baselines.json", fig_e5), ("E6_long_time.json", fig_e6)):
        d = load(name)
        if d is None:
            print("skip", name); continue
        fn(d); made.append(name.split("_")[0])
    print("figures:", ", ".join(made))
    return 0


if __name__ == "__main__":
    sys.exit(main())
