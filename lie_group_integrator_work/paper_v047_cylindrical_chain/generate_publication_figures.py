#!/usr/bin/env python3
"""Generate publication-oriented figures for the CMAME draft."""

from __future__ import annotations

import csv
import json
import math
import textwrap
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib import patches


PAPER = Path(__file__).resolve().parent
from paper_paths import LATEX, package_path as manuscript_path
FIGURES = LATEX / "figures"
FLAT = LATEX / "cmame_submission_flat"
RESULTS = PAPER.parent / "v047_cylindrical_chain_pipeline" / "results"
V048_RESULTS = PAPER.parent / "v048_cross_paper_same_test_benchmarks" / "results"


INK = "#1f2933"
MUTED = "#52616b"
BLUE = "#2f6f9f"
GREEN = "#5f8f3f"
ORANGE = "#c46a2b"
RED = "#a43d3d"
PURPLE = "#7a5195"


def read_csv(name: str) -> list[dict[str, str]]:
    path = RESULTS / name
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def read_v048_csv(name: str) -> list[dict[str, str]]:
    path = V048_RESULTS / name
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def read_paper_csv(name: str) -> list[dict[str, str]]:
    path = manuscript_path(name)
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def read_json(name: str) -> dict:
    path = manuscript_path(name)
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def as_float(row: dict[str, str], key: str) -> float:
    return float(row[key])


def finite_float(row: dict[str, str], key: str, default: float = 0.0) -> float:
    value = row.get(key, "")
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return default
    if parsed != parsed:
        return default
    return parsed


def filter_rows(rows: list[dict[str, str]], **criteria: str) -> list[dict[str, str]]:
    selected = [
        row
        for row in rows
        if all(row.get(key) == value for key, value in criteria.items())
    ]
    return sorted(selected, key=lambda row: as_float(row, "h"), reverse=True)


def style_axes(ax, title: str, xlabel: str, ylabel: str) -> None:
    ax.set_title(title, fontsize=10, weight="bold", color=INK)
    ax.set_xlabel(xlabel, fontsize=8.5)
    ax.set_ylabel(ylabel, fontsize=8.5)
    ax.grid(True, which="both", color="#d9e2ec", lw=0.55, alpha=0.8)
    ax.tick_params(axis="both", labelsize=7.5)
    for spine in ax.spines.values():
        spine.set_color("#9fb3c8")
        spine.set_linewidth(0.8)


def plot_xy(ax, rows: list[dict[str, str]], xkey: str, ykey: str, label: str, color: str, marker: str) -> None:
    xs = [as_float(row, xkey) for row in rows]
    ys = [as_float(row, ykey) for row in rows]
    ax.loglog(xs, ys, marker=marker, color=color, lw=1.6, ms=4.5, label=label)


def add_status_row(ax, y: float, label: str, detail: str, color: str, status: str) -> None:
    ax.add_patch(
        patches.FancyBboxPatch(
            (0.03, y - 0.045),
            0.23,
            0.07,
            boxstyle="round,pad=0.01,rounding_size=0.012",
            ec=color,
            fc="#ffffff",
            lw=1.15,
        )
    )
    ax.text(0.145, y - 0.01, status, ha="center", va="center", fontsize=7.6, weight="bold", color=color)
    ax.text(0.30, y + 0.012, label, ha="left", va="center", fontsize=8.4, weight="bold", color=INK)
    ax.text(
        0.30,
        y - 0.026,
        "\n".join(textwrap.wrap(detail, width=55)),
        ha="left",
        va="top",
        fontsize=6.8,
        color=MUTED,
        linespacing=1.05,
    )


def setup_status_panel(ax, title: str) -> None:
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.text(0.03, 0.96, title, ha="left", va="top", fontsize=10, weight="bold", color=INK)
    ax.plot([0.03, 0.97], [0.905, 0.905], color="#d9e2ec", lw=0.8)


def add_flow_box(
    ax,
    xy: tuple[float, float],
    size: tuple[float, float],
    title: str,
    detail: str,
    edge: str,
    face: str = "#ffffff",
) -> None:
    x, y = xy
    w, h = size
    ax.add_patch(
        patches.FancyBboxPatch(
            (x, y),
            w,
            h,
            boxstyle="round,pad=0.012,rounding_size=0.018",
            ec=edge,
            fc=face,
            lw=1.25,
        )
    )
    ax.text(
        x + w / 2,
        y + h - 0.030,
        title,
        ha="center",
        va="top",
        fontsize=7.2,
        weight="bold",
        color=INK,
        linespacing=0.95,
    )
    ax.text(
        x + 0.018,
        y + h - 0.075,
        "\n".join(textwrap.wrap(detail, width=18)),
        ha="left",
        va="top",
        fontsize=5.9,
        color=MUTED,
        linespacing=1.05,
    )


def add_arrow(ax, start: tuple[float, float], end: tuple[float, float], color: str = MUTED) -> None:
    ax.annotate(
        "",
        xy=end,
        xytext=start,
        arrowprops={"arrowstyle": "->", "lw": 1.1, "color": color, "shrinkA": 2, "shrinkB": 2},
    )


def generate_method_stage_architecture_figure() -> None:
    fig, ax = plt.subplots(figsize=(8.25, 4.9), constrained_layout=True)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    ax.text(0.03, 0.96, "Accepted Gauss6/FullVA one-step architecture", ha="left", va="top", fontsize=13, weight="bold", color=INK)
    ax.text(
        0.03,
        0.90,
        "The figure separates the mathematical one-step map from open source-paper TFE replacement and external-superiority claims.",
        ha="left",
        va="top",
        fontsize=7.8,
        color=MUTED,
    )

    top_y = 0.66
    box_w = 0.15
    box_h = 0.16
    xs = [0.04, 0.235, 0.43, 0.625, 0.82]
    boxes = [
        ("input\nstate", r"q_n, v_n, a_n, h", BLUE),
        ("stage\nunknowns", r"3 Gauss stages", GREEN),
        ("132-row\nresidual", r"dynamics + constraints", ORANGE),
        ("Newton\nsolve", r"AD Jacobian R_JAC", PURPLE),
        ("endpoint\nmap", r"quadrature + audit", BLUE),
    ]
    for x, (title, detail, color) in zip(xs, boxes):
        add_flow_box(ax, (x, top_y), (box_w, box_h), title, detail, color)
    for x0, x1 in zip(xs[:-1], xs[1:]):
        add_arrow(ax, (x0 + box_w, top_y + 0.042), (x1, top_y + 0.042))

    residual_x, residual_y = 0.26, 0.28
    residual_w, residual_h = 0.48, 0.27
    ax.add_patch(
        patches.FancyBboxPatch(
            (residual_x, residual_y),
            residual_w,
            residual_h,
            boxstyle="round,pad=0.014,rounding_size=0.018",
            ec="#9fb3c8",
            fc="#f7fbff",
            lw=1.1,
        )
    )
    ax.text(residual_x + residual_w / 2, residual_y + residual_h - 0.035, "residual families inside R_G6FVA", ha="center", va="top", fontsize=8.6, weight="bold", color=INK)
    family_labels = [
        ("Newton-Euler balance", BLUE),
        ("SO(3) kinematics", GREEN),
        ("Phi rows", ORANGE),
        ("dPhi rows", PURPLE),
        ("ddPhi rows", RED),
        ("endpoint audit", MUTED),
    ]
    for index, (label, color) in enumerate(family_labels):
        col = index % 2
        row = index // 2
        x = residual_x + 0.055 + col * 0.235
        y = residual_y + 0.150 - row * 0.058
        ax.add_patch(patches.Circle((x, y), 0.012, ec=color, fc="white", lw=1.2))
        ax.text(x + 0.024, y, label, ha="left", va="center", fontsize=6.8, color=INK)

    add_arrow(ax, (0.505, top_y), (0.50, residual_y + residual_h), color="#9fb3c8")
    ax.text(0.515, 0.595, "evaluates", ha="left", va="center", fontsize=6.4, color="#6b7c93")

    add_flow_box(
        ax,
        (0.04, 0.30),
        (0.17, 0.20),
        "proof\nboundary",
        r"regular flow; eta_h <= c_eta h^7; conditional theorem",
        GREEN,
        face="#fbfff7",
    )
    add_flow_box(
        ax,
        (0.79, 0.30),
        (0.17, 0.20),
        "non-\nclaims",
        r"not full-TFE; no default 1e-4; no superiority claim",
        RED,
        face="#fffafa",
    )
    add_arrow(ax, (0.21, 0.40), (residual_x, 0.40), color=GREEN)
    add_arrow(ax, (residual_x + residual_w, 0.40), (0.79, 0.40), color=RED)

    ax.text(
        0.04,
        0.12,
        "\n".join(
            textwrap.wrap(
                "Accepted claim: a conditional sixth-order Gauss6/FullVA path for lower-pair mechanisms. "
                "Open gates remain explicit rather than hidden in the method diagram.",
                width=120,
            )
        ),
        ha="left",
        va="center",
        fontsize=7.5,
        color=MUTED,
    )

    out = FIGURES / "method_stage_architecture.png"
    flat_out = FLAT / "Figure_11_method_stage_architecture.png"
    fig.savefig(out, dpi=300, bbox_inches="tight")
    fig.savefig(flat_out, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(out)
    print(flat_out)


def generate_claim_boundary_limitations_figure() -> None:
    fig, axes = plt.subplots(2, 2, figsize=(7.6, 5.9), constrained_layout=True)

    ax = axes[0, 0]
    setup_status_panel(ax, "accepted method claim")
    add_status_row(ax, 0.78, "Gauss6/FullVA order", "conditional sixth-order path; observed smooth slopes 7.161/7.066 are finite-window support, not a seventh-order theorem", GREEN, "accepted")
    add_status_row(ax, 0.56, "mechanism coverage", "four ASME-style mechanisms are covered; dynamic order is accepted only for single and double pendula", GREEN, "accepted")
    add_status_row(ax, 0.34, "source-paper comparison", "local m=3 TFE formula target has expected order five; complete source-paper residual replacement is outside the claim", ORANGE, "bounded")
    add_status_row(ax, 0.15, "external superiority", "not claimed until the same-test public-code campaign and work metrics are complete", RED, "open")

    ax = axes[0, 1]
    setup_status_panel(ax, "four-example evidence split")
    examples = [
        ("single", "dynamic order accepted", GREEN),
        ("double", "dynamic order accepted", GREEN),
        ("four-link", "coarse dynamics / common-ref diagnostics; residual-to-error theorem open", ORANGE),
        ("slider-crank", "coarse dynamics / common-ref diagnostics; residual-to-error theorem open", ORANGE),
    ]
    ys = [0.78, 0.58, 0.38, 0.18]
    for (name, detail, color), y in zip(examples, ys):
        ax.add_patch(patches.Circle((0.08, y), 0.035, ec=color, fc="white", lw=1.6))
        ax.text(0.08, y, "✓" if color == GREEN else "!", ha="center", va="center", fontsize=10, color=color, weight="bold")
        ax.text(0.15, y + 0.014, name, ha="left", va="center", fontsize=8.8, weight="bold", color=INK)
        ax.text(0.15, y - 0.028, "\n".join(textwrap.wrap(detail, width=48)), ha="left", va="top", fontsize=6.9, color=MUTED)

    ax = axes[1, 0]
    setup_status_panel(ax, "proof and solver limitations")
    add_status_row(ax, 0.78, "conditional theorem", "requires regular reduced flow, smooth lift, isolated Newton solve, and stage residual defect O(h^7)", ORANGE, "conditional")
    add_status_row(ax, 0.56, "implementation oracle", "runtime layout, AD-expanded oracle, and direct dynamic row closure pass; primitive symbolic lane remains diagnostic", GREEN, "direct route")
    add_status_row(ax, 0.34, "nonlinear tolerance", "proof-level policy is eta_h = O(h^7); fixed absolute tolerances are finite-run evidence", RED, "open")
    add_status_row(ax, 0.15, "residual-to-error route", "closed-loop residual rows are not promoted to order claims without the missing theorem", RED, "open")

    ax = axes[1, 1]
    setup_status_panel(ax, "same-test benchmark limitations")
    add_status_row(ax, 0.78, "original TFE pendulum", "source-paper pendulum rows remain to be reproduced on the same policies", RED, "open")
    add_status_row(ax, 0.56, "2021 rA/rp/reps suite", "public baselines and coarse pilots exist; full dynamic work/precision comparison remains open", ORANGE, "partial")
    add_status_row(ax, 0.34, "2022 half-implicit suite", "bounded pilot is present; full T=8 policy and method rows remain open", ORANGE, "partial")
    add_status_row(ax, 0.15, "velocity partitioning", "code path unresolved in the local public-code mirror and metadata search", RED, "open")

    fig.suptitle("Claim boundary and remaining limitations", fontsize=13, weight="bold", color=INK)
    out = FIGURES / "claim_boundary_limitations.png"
    flat_out = FLAT / "Figure_8_claim_boundary_limitations.png"
    fig.savefig(out, dpi=300, bbox_inches="tight")
    fig.savefig(flat_out, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(out)
    print(flat_out)


def method_label(method: str) -> str:
    if method.startswith("Gauss6"):
        return "Gauss6/FullVA"
    if method.startswith("rA"):
        return "rA"
    if method.startswith("reps"):
        return "r-epsilon"
    if method.startswith("rp"):
        return "rp"
    return method


def method_color(label: str) -> str:
    return {
        "Gauss6/FullVA": BLUE,
        "rA": MUTED,
        "r-epsilon": ORANGE,
        "rp": PURPLE,
    }.get(label, MUTED)


def bar_labels(ax, bars, values: list[float], fmt: str = "{:.2g}") -> None:
    ymax = max(max(values), 1.0)
    for bar, value in zip(bars, values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            min(value * 1.08, ymax * 1.45),
            fmt.format(value),
            ha="center",
            va="bottom",
            fontsize=6.5,
            color=INK,
            rotation=0,
        )


def setup_bar_axis(ax, title: str, ylabel: str, logy: bool = False) -> None:
    ax.set_title(title, fontsize=10, weight="bold", color=INK)
    ax.set_ylabel(ylabel, fontsize=8.5)
    ax.grid(True, axis="y", color="#d9e2ec", lw=0.55, alpha=0.8)
    ax.tick_params(axis="both", labelsize=7.2)
    for spine in ax.spines.values():
        spine.set_color("#9fb3c8")
        spine.set_linewidth(0.8)
    if logy:
        ax.set_yscale("log")


def matrix_method_label(method: str) -> str:
    labels = {
        "local_Gauss6_FullVA": "Gauss6/FullVA",
        "hi2022_rA": "HI22 rA",
        "hi2022_rA_half": "HI22 half",
        "ra2021_rA": "RA21 rA",
        "ra2021_reps": "RA21 reps",
        "ra2021_rp": "RA21 rp",
        "tfe2026_Newmark_beta": "TFE Newmark",
        "tfe2026_TFE_m1": "TFE m1",
        "tfe2026_TFE_m2": "TFE m2",
        "tfe2026_trapezoidal": "TFE trap.",
        "vp2024_coordinate_partitioning_rA": "VP24 rA proxy",
    }
    return labels.get(method, method)


def matrix_example_label(example: str) -> str:
    labels = {
        "single_pendulum": "Single",
        "double_pendulum": "Double",
        "four_link": "Four-link",
        "slider_crank": "Slider-crank",
    }
    return labels.get(example, example)


def order_color(order: float) -> str:
    if not math.isfinite(order):
        return "#edf2f7"
    if order >= 5.5:
        return "#d8f0cf"
    if order >= 3.0:
        return "#dcecff"
    if order >= 1.5:
        return "#fff0c7"
    if order >= 0.5:
        return "#f9d9be"
    return "#f6c7c7"


def matrix_error_text(value: float) -> str:
    if not math.isfinite(value):
        return "nan"
    if value == 0.0:
        return "0"
    return f"{value:.1e}"


def generate_all_method_result_matrix_figure() -> None:
    matrix = read_json("PAPER_NUMERICAL_RESULT_MATRIX.json")
    examples = list(matrix["examples"])
    methods = list(matrix["methods"])
    rows = matrix["rows"]
    by_key = {(row["method"], row["example"]): row for row in rows}

    fig, ax = plt.subplots(figsize=(8.3, 6.7), constrained_layout=True)
    ax.set_xlim(-1.68, len(examples) + 0.25)
    ax.set_ylim(len(methods) + 1.20, -1.25)
    ax.axis("off")

    ax.text(
        -1.65,
        -1.00,
        "All-method common-reference result matrix",
        ha="left",
        va="center",
        fontsize=13,
        weight="bold",
        color=INK,
    )
    ax.text(
        -1.65,
        -0.62,
        "Each cell reports observed velocity order p and finest-step velocity error e.",
        ha="left",
        va="center",
        fontsize=7.4,
        color=MUTED,
    )

    for j, example in enumerate(examples):
        ax.text(j + 0.5, -0.08, matrix_example_label(example), ha="center", va="bottom", fontsize=8.5, weight="bold", color=INK)

    for i, method in enumerate(methods):
        y = i + 0.20
        label = matrix_method_label(method)
        role = "internal" if method == "local_Gauss6_FullVA" else "diagnostic"
        color = BLUE if method == "local_Gauss6_FullVA" else MUTED
        ax.text(-1.58, y + 0.42, label, ha="left", va="center", fontsize=7.4, weight="bold", color=color)
        ax.text(-0.62, y + 0.42, role, ha="left", va="center", fontsize=6.2, color=MUTED)
        for j, example in enumerate(examples):
            cell = by_key[(method, example)]
            order = float(cell["velocity_order"])
            error = float(cell["finest_velocity_error"])
            issues = cell.get("issues", [])
            source_closed = bool(cell.get("source_policy_closed"))
            face = order_color(order)
            edge = BLUE if method == "local_Gauss6_FullVA" else ("#8ca0b3" if source_closed else "#c99a6b")
            line_width = 1.8 if method == "local_Gauss6_FullVA" else 0.9
            ax.add_patch(
                patches.Rectangle(
                    (j, y),
                    1.0,
                    0.84,
                    ec=edge,
                    fc=face,
                    lw=line_width,
                )
            )
            issue_marker = "*" if issues else ""
            ax.text(j + 0.50, y + 0.30, f"p={order:.2f}{issue_marker}", ha="center", va="center", fontsize=6.8, weight="bold", color=INK)
            ax.text(j + 0.50, y + 0.58, f"e={matrix_error_text(error)}", ha="center", va="center", fontsize=6.0, color=MUTED)

    legend_y = len(methods) + 0.38
    legend = [
        ("p >= 5.5", "#d8f0cf"),
        ("3 <= p < 5.5", "#dcecff"),
        ("1.5 <= p < 3", "#fff0c7"),
        ("0.5 <= p < 1.5", "#f9d9be"),
        ("p < 0.5", "#f6c7c7"),
    ]
    x0 = -1.58
    for label, color in legend:
        ax.add_patch(patches.Rectangle((x0, legend_y), 0.22, 0.22, ec="#9fb3c8", fc=color, lw=0.7))
        ax.text(x0 + 0.27, legend_y + 0.11, label, ha="left", va="center", fontsize=6.2, color=INK)
        x0 += 0.95
    ax.text(
        -1.58,
        legend_y + 0.55,
        "* marks a row with diagnostic/source-policy caveats. Nonlocal rows are common-reference diagnostics only; they are not source-paper superiority claims.",
        ha="left",
        va="center",
        fontsize=6.6,
        color=MUTED,
    )
    ax.text(
        -1.58,
        legend_y + 0.86,
        "Source: PAPER_NUMERICAL_RESULT_MATRIX.json; h = 0.1, 0.05, 0.025; reference h = 0.0125; 44/44 method-example cells.",
        ha="left",
        va="center",
        fontsize=6.4,
        color=MUTED,
    )

    out = FIGURES / "all_method_result_matrix.png"
    flat_out = FLAT / "Figure_12_all_method_result_matrix.png"
    fig.savefig(out, dpi=300, bbox_inches="tight")
    fig.savefig(flat_out, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(out)
    print(flat_out)


def generate_coarse_baseline_work_precision_figure() -> None:
    single = read_v048_csv("single_pendulum_coarse_same_window_work_precision_summary.csv")
    double = read_v048_csv("double_pendulum_coarse_same_window_work_precision_summary.csv")
    strict = read_v048_csv("closed_loop_true_dynamic_strict_common_reference_summary.csv")

    fig, axes = plt.subplots(2, 2, figsize=(8.35, 6.35), constrained_layout=True)

    ax = axes[0, 0]
    single_labels = [method_label(row["method"]) for row in single]
    x = range(len(single))
    pos = [max(finite_float(row, "pos_observed_order"), 1e-6) for row in single]
    vel = [max(finite_float(row, "vel_observed_order"), 1e-6) for row in single]
    width = 0.36
    ax.bar([i - width / 2 for i in x], pos, width=width, color=[method_color(label) for label in single_labels], alpha=0.95, label="position")
    ax.bar([i + width / 2 for i in x], vel, width=width, color=[method_color(label) for label in single_labels], alpha=0.45, hatch="//", label="velocity")
    ax.axhline(6.0, color=GREEN, lw=1.0, ls="--", alpha=0.8)
    ax.axhline(1.0, color=MUTED, lw=0.8, ls=":", alpha=0.9)
    ax.set_xticks(list(x), single_labels, rotation=18, ha="right")
    setup_bar_axis(ax, "single pendulum: coarse same-window order", "observed order")
    ax.set_ylim(0, max(pos + vel + [6.0]) * 1.22)
    ax.legend(fontsize=6.6, frameon=False, loc="upper right")
    ax.text(
        0.02,
        0.92,
        "T=3, h=0.1,0.05,0.025; reference h=0.0125",
        transform=ax.transAxes,
        fontsize=6.8,
        color=MUTED,
        va="top",
        bbox=text_box(),
    )

    ax = axes[0, 1]
    double_labels = [method_label(row["method"]) for row in double]
    x = range(len(double))
    pos = [max(finite_float(row, "pos_observed_order"), 1e-6) for row in double]
    vel = [max(finite_float(row, "vel_observed_order"), 1e-6) for row in double]
    ax.bar([i - width / 2 for i in x], pos, width=width, color=[method_color(label) for label in double_labels], alpha=0.95, label="position")
    ax.bar([i + width / 2 for i in x], vel, width=width, color=[method_color(label) for label in double_labels], alpha=0.45, hatch="//", label="velocity")
    ax.axhline(6.0, color=GREEN, lw=1.0, ls="--", alpha=0.8)
    ax.axhline(1.0, color=MUTED, lw=0.8, ls=":", alpha=0.9)
    ax.set_xticks(list(x), double_labels, rotation=18, ha="right")
    setup_bar_axis(ax, "double pendulum: coarse same-window order", "observed order")
    ax.set_ylim(0, max(pos + vel + [6.0]) * 1.22)
    ax.legend(fontsize=6.6, frameon=False, loc="upper right")
    ax.text(
        0.02,
        0.92,
        "coarse public rows; not the source h=1e-4 policy",
        transform=ax.transAxes,
        fontsize=6.8,
        color=MUTED,
        va="top",
        bbox=text_box(),
    )

    ax = axes[1, 0]
    closed = [row for row in strict if row["model"] in {"four_link", "slider_crank"}]
    local = {
        row["model"]: row
        for row in closed
        if row["method"].startswith("Gauss6")
    }
    public_ra = {
        row["model"]: row
        for row in closed
        if row["method"].startswith("rA")
    }
    models = ["four_link", "slider_crank"]
    labels = ["four-link", "slider-crank"]
    local_err = [max(finite_float(local[model], "finest_pos_error_ratio_vs_public_rA"), 1e-8) for model in models]
    public_err = [max(finite_float(public_ra[model], "finest_pos_error_ratio_vs_public_rA"), 1e-8) for model in models]
    x = range(len(models))
    ax.bar([i - width / 2 for i in x], local_err, width=width, color=BLUE, label="Gauss6/FullVA")
    ax.bar([i + width / 2 for i in x], public_err, width=width, color=MUTED, label="public rA")
    ax.set_xticks(list(x), labels)
    setup_bar_axis(ax, "closed loops: strict common-reference position error", "finest error ratio vs public rA", logy=True)
    ax.legend(
        fontsize=6.6,
        frameon=True,
        loc="upper center",
        bbox_to_anchor=(0.5, 1.18),
        ncol=2,
        borderaxespad=0.2,
    )

    ax = axes[1, 1]
    local_time = [max(finite_float(local[model], "finest_runtime_ratio_vs_public_rA"), 1e-4) for model in models]
    public_time = [max(finite_float(public_ra[model], "finest_runtime_ratio_vs_public_rA"), 1e-4) for model in models]
    ax.bar([i - width / 2 for i in x], local_time, width=width, color=BLUE, label="Gauss6/FullVA")
    ax.bar([i + width / 2 for i in x], public_time, width=width, color=MUTED, label="public rA")
    ax.set_xticks(list(x), labels)
    setup_bar_axis(ax, "closed loops: finest-row runtime ratio", "runtime ratio vs public rA", logy=True)
    ax.legend(
        fontsize=6.6,
        frameon=True,
        loc="upper center",
        bbox_to_anchor=(0.5, 1.18),
        ncol=2,
        borderaxespad=0.2,
    )

    fig.suptitle("Coarse-first baseline comparison and work/precision evidence", fontsize=13, weight="bold", color=INK)
    out = FIGURES / "coarse_baseline_work_precision.png"
    flat_out = FLAT / "Figure_9_coarse_baseline_work_precision.png"
    fig.savefig(out, dpi=300, bbox_inches="tight")
    fig.savefig(flat_out, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(out)
    print(flat_out)


def short_method_label(method: str) -> str:
    if method.startswith("tfe2026_"):
        return short_method_label(method.removeprefix("tfe2026_"))
    if method.startswith("Gauss6"):
        return "Gauss6"
    if method.startswith("Newmark"):
        return "Newmark"
    if method.startswith("trapezoidal"):
        return "trap"
    if method.startswith("TFE_m"):
        return method.replace("_GL", "")
    if method.startswith("rA"):
        return "rA"
    if method.startswith("rp"):
        return "rp"
    if method.startswith("reps"):
        return "r eps"
    return method.replace("-public-dynamics-coarse", "").replace("-public-dynamics", "")


def work_method_color(method: str) -> str | None:
    if method.startswith("tfe2026_"):
        return work_method_color(method.removeprefix("tfe2026_"))
    if method.startswith("Gauss6"):
        return BLUE
    if method.startswith("TFE_m3") or method.startswith("TFE_m2"):
        return GREEN
    if method.startswith("TFE_m1"):
        return ORANGE
    if method.startswith("Newmark"):
        return PURPLE
    if method.startswith("trapezoidal"):
        return RED
    return None


def generate_work_precision_compendium_figure() -> None:
    tfe_rows = [row for row in read_v048_csv("tfe_source_pendulum_same_test_work_precision_rows.csv") if row["status"] == "ok"]
    tfe_algorithm_rows = read_paper_csv("TFE_ALGORITHM_LITERAL_WORK_PRECISION_AUDIT.csv")
    single = read_v048_csv("single_pendulum_coarse_same_window_work_precision_summary.csv")
    double = read_v048_csv("double_pendulum_coarse_same_window_work_precision_summary.csv")
    closed = [
        row
        for row in read_v048_csv("closed_loop_true_dynamic_strict_common_reference_rows.csv")
        if row["status"] == "ok"
    ]

    fig, axes = plt.subplots(2, 3, figsize=(10.4, 6.35), constrained_layout=True)

    ax = axes[0, 0]
    methods = []
    for row in tfe_rows:
        if row["method"] not in methods:
            methods.append(row["method"])
    marker_cycle = ["o", "s", "^", "D", "v", "P", "X"]
    for idx, method in enumerate(methods):
        selected = sorted([row for row in tfe_rows if row["method"] == method], key=lambda item: as_float(item, "runtime_sec"))
        xs = [max(as_float(row, "runtime_sec"), 1e-8) for row in selected]
        ys = [max(as_float(row, "velocity_error_v"), 1e-16) for row in selected]
        color = work_method_color(method)
        ax.loglog(xs, ys, marker=marker_cycle[idx % len(marker_cycle)], lw=1.2, ms=4.2, label=short_method_label(method), color=color)
    style_axes(ax, "TFE candidate: wall time (T=1)", "runtime per row (s)", "velocity error")
    ax.legend(fontsize=5.9, frameon=False, ncol=2, loc="lower left")

    ax = axes[0, 1]
    for idx, method in enumerate(methods):
        selected = sorted([row for row in tfe_rows if row["method"] == method], key=lambda item: as_float(item, "work_units_newton_iterations"))
        xs = [max(as_float(row, "work_units_newton_iterations"), 1e-8) for row in selected]
        ys = [max(as_float(row, "velocity_error_v"), 1e-16) for row in selected]
        color = work_method_color(method)
        ax.loglog(xs, ys, marker=marker_cycle[idx % len(marker_cycle)], lw=1.2, ms=4.2, label=short_method_label(method), color=color)
    style_axes(ax, "TFE candidate: Newton work (T=1)", "Newton iterations", "velocity error")
    ax.legend(fontsize=5.9, frameon=False, ncol=2, loc="lower left")

    algorithm_methods = []
    for row in tfe_algorithm_rows:
        if row["paper_method"] not in algorithm_methods:
            algorithm_methods.append(row["paper_method"])

    ax = axes[0, 2]
    for idx, method in enumerate(algorithm_methods):
        selected = sorted(
            [row for row in tfe_algorithm_rows if row["paper_method"] == method],
            key=lambda item: as_float(item, "work_units_newton_iterations"),
        )
        xs = [max(as_float(row, "work_units_newton_iterations"), 1e-8) for row in selected]
        ys = [max(as_float(row, "velocity_error_v"), 1e-16) for row in selected]
        ax.loglog(
            xs,
            ys,
            marker=marker_cycle[idx % len(marker_cycle)],
            lw=1.2,
            ms=4.2,
            label=short_method_label(method),
            color=work_method_color(method),
        )
    style_axes(ax, "Alg. literal T=10: velocity", "Newton iterations", "velocity error")
    ax.legend(fontsize=5.8, frameon=False, ncol=2, loc="lower left")

    ax = axes[1, 0]
    for idx, method in enumerate(algorithm_methods):
        selected = sorted(
            [row for row in tfe_algorithm_rows if row["paper_method"] == method],
            key=lambda item: as_float(item, "work_units_newton_iterations"),
        )
        xs = [max(as_float(row, "work_units_newton_iterations"), 1e-8) for row in selected]
        ys = [max(as_float(row, "coordinate_error_q"), 1e-16) for row in selected]
        ax.loglog(
            xs,
            ys,
            marker=marker_cycle[idx % len(marker_cycle)],
            lw=1.2,
            ms=4.2,
            label=short_method_label(method),
            color=work_method_color(method),
        )
    style_axes(ax, "Alg. literal T=10: coordinate", "Newton iterations", "coordinate error")
    ax.legend(fontsize=5.8, frameon=False, ncol=2, loc="lower left")

    ax = axes[1, 1]
    pendulum_rows = [("single", row) for row in single] + [("double", row) for row in double]
    seen_labels: set[str] = set()
    for model, row in pendulum_rows:
        method = row["method"]
        x = max(finite_float(row, "finest_runtime_ratio_vs_rA"), 1e-8)
        y = max(finite_float(row, "finest_vel_error_ratio_vs_rA"), 1e-16)
        color = BLUE if method.startswith("Gauss6") else MUTED
        marker = "o" if model == "single" else "s"
        family = "Gauss6" if method.startswith("Gauss6") else "public"
        label = f"{model} {family}"
        plot_label = label if label not in seen_labels else None
        seen_labels.add(label)
        ax.loglog([x], [y], marker=marker, color=color, ms=5.0, lw=0.0, label=plot_label)
    ax.axhline(1.0, color=MUTED, lw=0.8, ls=":")
    ax.axvline(1.0, color=MUTED, lw=0.8, ls=":")
    style_axes(ax, "RA2021 pendula: finest-row ratios", "runtime ratio vs rA", "velocity-error ratio vs rA")
    ax.legend(fontsize=6.0, frameon=False, loc="lower left")

    ax = axes[1, 2]
    closed_methods = []
    for row in closed:
        key = (row["model"], row["method"])
        if key not in closed_methods:
            closed_methods.append(key)
    for idx, (model, method) in enumerate(closed_methods):
        selected = sorted(
            [row for row in closed if row["model"] == model and row["method"] == method],
            key=lambda item: as_float(item, "runtime_sec"),
        )
        xs = [max(as_float(row, "runtime_sec"), 1e-8) for row in selected]
        ys = [max(as_float(row, "vel_final_linf"), 1e-16) for row in selected]
        is_local = method.startswith("Gauss6")
        color = BLUE if is_local else MUTED
        marker = "o" if model == "four_link" else "s"
        line_style = "-" if is_local else "--"
        label = f"{'four' if model == 'four_link' else 'slider'}:{short_method_label(method)}"
        ax.loglog(xs, ys, marker=marker, lw=1.25, ms=4.2, label=label, color=color, ls=line_style)
    style_axes(ax, "Closed loops: strict common-reference work", "runtime per row (s)", "velocity error")
    ax.legend(fontsize=5.4, frameon=False, ncol=2, loc="lower left")

    fig.suptitle("Work/precision compendium for fair candidate diagnostics", fontsize=13, weight="bold", color=INK)
    out = FIGURES / "work_precision_compendium.png"
    flat_out = FLAT / "Figure_13_work_precision_compendium.png"
    fig.savefig(out, dpi=300, bbox_inches="tight")
    fig.savefig(flat_out, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(out)
    print(flat_out)


def generate_closed_loop_true_dynamic_order_figure() -> None:
    rows = read_v048_csv("closed_loop_true_dynamic_newton_coarse_order_rows.csv")
    model_rows = {
        model: sorted(
            [row for row in rows if row["model"] == model],
            key=lambda row: as_float(row, "h"),
            reverse=True,
        )
        for model in ["four_link", "slider_crank"]
    }
    metric_specs = [
        ("endpoint_pos_error_inf", "position", "model_pos_observed_order", BLUE, "o"),
        ("endpoint_orientation_error_inf", "orientation", "model_orientation_observed_order", GREEN, "s"),
        ("endpoint_vel_error_inf", "velocity", "model_vel_observed_order", ORANGE, "^"),
        ("endpoint_omega_error_inf", "omega", "model_omega_observed_order", PURPLE, "D"),
    ]

    fig, axes = plt.subplots(2, 2, figsize=(7.8, 5.9), constrained_layout=True)

    for ax, model, title in [
        (axes[0, 0], "four_link", "four-link: coarse dynamics errors"),
        (axes[0, 1], "slider_crank", "slider-crank: coarse dynamics errors"),
    ]:
        selected = model_rows[model]
        for ykey, label, _, color, marker in metric_specs:
            plot_xy(ax, selected, "h", ykey, label, color, marker)
        h_values = [as_float(row, "h") for row in selected]
        pos_values = [as_float(row, "endpoint_pos_error_inf") for row in selected]
        h0 = h_values[0]
        y0 = pos_values[0]
        ref = [y0 * (h / h0) ** 6 for h in h_values]
        ax.loglog(h_values, ref, color=INK, lw=1.0, ls="--", label=r"$O(h^6)$ guide")
        ax.invert_xaxis()
        style_axes(ax, title, "step size h", "endpoint error")
        ax.legend(fontsize=6.2, frameon=False, loc="lower right")
        ax.text(
            0.03,
            0.10,
            "non-oracle Newton stages; no stage-time kinematic oracle",
            transform=ax.transAxes,
            fontsize=6.7,
            color=MUTED,
            bbox=text_box(),
        )

    ax = axes[1, 0]
    order_metrics = ["position", "orientation", "velocity", "omega"]
    x = list(range(len(order_metrics)))
    width = 0.36
    four_orders = [
        finite_float(model_rows["four_link"][0], "model_pos_observed_order"),
        finite_float(model_rows["four_link"][0], "model_orientation_observed_order"),
        finite_float(model_rows["four_link"][0], "model_vel_observed_order"),
        finite_float(model_rows["four_link"][0], "model_omega_observed_order"),
    ]
    slider_orders = [
        finite_float(model_rows["slider_crank"][0], "model_pos_observed_order"),
        finite_float(model_rows["slider_crank"][0], "model_orientation_observed_order"),
        finite_float(model_rows["slider_crank"][0], "model_vel_observed_order"),
        finite_float(model_rows["slider_crank"][0], "model_omega_observed_order"),
    ]
    ax.bar([i - width / 2 for i in x], four_orders, width=width, color=BLUE, label="four-link")
    ax.bar([i + width / 2 for i in x], slider_orders, width=width, color=ORANGE, label="slider-crank")
    ax.axhline(6.0, color=GREEN, lw=1.0, ls="--", alpha=0.9)
    ax.set_xticks(x, order_metrics, rotation=12, ha="right")
    setup_bar_axis(ax, "primary-state observed orders", "observed order")
    ax.set_ylim(0, max(four_orders + slider_orders + [6.0]) * 1.20)
    ax.legend(fontsize=6.8, frameon=False, loc="upper right")
    ax.text(0.04, 0.08, "dashed line: order 6", transform=ax.transAxes, fontsize=6.9, color=MUTED, bbox=text_box())

    ax = axes[1, 1]
    for model, label, color, marker in [
        ("four_link", "four-link Newton iterations", BLUE, "o"),
        ("slider_crank", "slider-crank Newton iterations", ORANGE, "s"),
    ]:
        selected = model_rows[model]
        xs = [as_float(row, "h") for row in selected]
        ys = [as_float(row, "total_stage_newton_iterations") for row in selected]
        ax.plot(xs, ys, marker=marker, color=color, lw=1.6, ms=4.5, label=label)
    ax.invert_xaxis()
    style_axes(ax, "non-oracle stage-solve work", "step size h", "total Newton iterations")
    ax.legend(fontsize=6.6, frameon=False, loc="upper right")
    ax.text(
        0.04,
        0.12,
        "T=0.1; h=0.1,0.05,0.025; reference h=0.0125\n"
        "acceleration order is diagnostic only",
        transform=ax.transAxes,
        fontsize=6.8,
        color=MUTED,
        bbox=text_box(),
    )

    fig.suptitle("Closed-loop coarse-dynamics diagnostic evidence", fontsize=13, weight="bold", color=INK)
    out = FIGURES / "closed_loop_true_dynamic_order.png"
    flat_out = FLAT / "Figure_10_closed_loop_true_dynamic_order.png"
    fig.savefig(out, dpi=300, bbox_inches="tight")
    fig.savefig(flat_out, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(out)
    print(flat_out)


def generate_convergence_figure() -> None:
    convergence = read_csv("cylindrical_chain_convergence.csv")
    smooth = filter_rows(convergence, case="cylindrical_smooth", endpoint_mode="projected_velocity")
    sharp = filter_rows(convergence, case="cylindrical_sharp", endpoint_mode="projected_velocity")
    tfe_diag = filter_rows(
        read_csv("cylindrical_chain_endpoint_tfe_paper_all_row_consistent_z0_scaled_newton_audit.csv"),
        case="cylindrical_smooth",
    )
    sharp_fixed = read_csv("cylindrical_chain_sharp_fixed_refinement_audit.csv")
    sharp_ultra = read_csv("cylindrical_chain_sharp_ultra_refinement_audit.csv")
    sharp_work = sorted(sharp_fixed + sharp_ultra, key=lambda row: as_float(row, "runtime_sec"))

    fig, axes = plt.subplots(2, 2, figsize=(7.4, 5.9), constrained_layout=True)

    ax = axes[0, 0]
    plot_xy(ax, smooth, "h", "position_error", "position", BLUE, "o")
    plot_xy(ax, smooth, "h", "velocity_error", "velocity", GREEN, "s")
    plot_xy(
        ax,
        tfe_diag,
        "h",
        "position_error_vs_paper_consistent_scaled_terminal_reference",
        "paper-TFE diag. position",
        ORANGE,
        "^",
    )
    plot_xy(
        ax,
        tfe_diag,
        "h",
        "velocity_error_vs_paper_consistent_scaled_terminal_reference",
        "paper-TFE diag. velocity",
        RED,
        "D",
    )
    ax.invert_xaxis()
    style_axes(ax, "smooth branch: accepted vs paper-TFE diagnostic", "step size h", "error")
    ax.legend(fontsize=6.2, frameon=False, loc="lower right")
    ax.text(0.03, 0.08, "accepted: 7.161 / 7.066; diagnostic: 4.046 / 4.420", transform=ax.transAxes, fontsize=7.0, color=MUTED)

    ax = axes[0, 1]
    plot_xy(ax, smooth, "total_newton_iterations", "position_error", "accepted position", BLUE, "o")
    plot_xy(ax, smooth, "total_newton_iterations", "velocity_error", "accepted velocity", GREEN, "s")
    plot_xy(
        ax,
        tfe_diag,
        "total_newton_iterations",
        "position_error_vs_paper_consistent_scaled_terminal_reference",
        "paper-TFE diag. position",
        ORANGE,
        "^",
    )
    plot_xy(
        ax,
        tfe_diag,
        "total_newton_iterations",
        "velocity_error_vs_paper_consistent_scaled_terminal_reference",
        "paper-TFE diag. velocity",
        RED,
        "D",
    )
    style_axes(ax, "smooth branch: Newton work/precision", "Newton iterations", "error")
    ax.legend(fontsize=6.2, frameon=False, loc="upper right")
    ax.text(0.03, 0.08, "paper-TFE curve is diagnostic, not accepted baseline", transform=ax.transAxes, fontsize=7.0, color=MUTED)

    ax = axes[1, 0]
    plot_xy(ax, sharp, "h", "position_error", "coarse position", ORANGE, "o")
    plot_xy(ax, sharp, "h", "velocity_error", "coarse velocity", RED, "s")
    plot_xy(ax, sharp_ultra, "h", "position_error", "ultra position", BLUE, "^")
    plot_xy(ax, sharp_ultra, "h", "velocity_error", "ultra velocity", PURPLE, "D")
    ax.invert_xaxis()
    style_axes(ax, "sharp branch: coarse vs ultra", "step size h", "error")
    ax.legend(fontsize=6.8, frameon=False, loc="lower right")

    ax = axes[1, 1]
    plot_xy(ax, sharp_work, "runtime_sec", "position_error", "position", BLUE, "o")
    plot_xy(ax, sharp_work, "runtime_sec", "velocity_error", "velocity", RED, "s")
    style_axes(ax, "sharp branch: cost envelope", "runtime (s)", "error")
    ax.legend(fontsize=7.4, frameon=False, loc="upper right")
    ax.text(0.03, 0.08, "high order recovered only after refinement", transform=ax.transAxes, fontsize=7.5, color=MUTED)

    fig.suptitle("Convergence and work/precision evidence for the accepted path", fontsize=13, weight="bold", color=INK)
    out = FIGURES / "convergence.png"
    flat_out = FLAT / "Figure_1_convergence.png"
    fig.savefig(out, dpi=300, bbox_inches="tight")
    fig.savefig(flat_out, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(out)
    print(flat_out)


def add_ground(ax, x: float, y: float, w: float = 0.28) -> None:
    ax.plot([x - w, x + w], [y, y], color=INK, lw=1.2)
    for k in range(5):
        xx = x - w + 0.08 + 0.08 * k
        ax.plot([xx - 0.035, xx + 0.015], [y - 0.035, y], color=INK, lw=0.8)


def add_pin(ax, x: float, y: float, color: str = INK) -> None:
    ax.add_patch(patches.Circle((x, y), 0.035, ec=color, fc="white", lw=1.1, zorder=5))


def text_box() -> dict[str, object]:
    return {"facecolor": "white", "edgecolor": "none", "alpha": 0.82, "pad": 0.8}


def add_bar(
    ax,
    x0: float,
    y0: float,
    x1: float,
    y1: float,
    color: str,
    label: str,
    label_offset: tuple[float, float] = (0.0, 0.065),
) -> None:
    ax.plot([x0, x1], [y0, y1], color=color, lw=5.0, solid_capstyle="round", zorder=2)
    ax.plot([x0, x1], [y0, y1], color="white", lw=1.0, alpha=0.8, zorder=3)
    ax.text(
        (x0 + x1) / 2 + label_offset[0],
        (y0 + y1) / 2 + label_offset[1],
        label,
        ha="center",
        va="bottom",
        fontsize=7.2,
        color=INK,
        bbox=text_box(),
        zorder=8,
    )


def add_block(ax, x: float, y: float, w: float, h: float, color: str, label: str) -> None:
    ax.add_patch(
        patches.FancyBboxPatch(
            (x - w / 2, y - h / 2),
            w,
            h,
            boxstyle="round,pad=0.01,rounding_size=0.015",
            ec=color,
            fc="white",
            lw=1.5,
        )
    )
    ax.text(x, y, label, ha="center", va="center", fontsize=7.2, color=INK, bbox=text_box(), zorder=8)


def add_global_axes(ax, x: float = 0.08, y: float = 0.08) -> None:
    ax.annotate("", xy=(x + 0.16, y), xytext=(x, y), arrowprops={"arrowstyle": "->", "lw": 0.9, "color": INK})
    ax.annotate("", xy=(x, y + 0.16), xytext=(x, y), arrowprops={"arrowstyle": "->", "lw": 0.9, "color": INK})
    ax.text(x + 0.18, y - 0.01, r"$x$", fontsize=8, color=INK, ha="left", va="top")
    ax.text(x - 0.01, y + 0.18, r"$y$", fontsize=8, color=INK, ha="right", va="bottom")


def add_body_frame(ax, x: float, y: float, angle_label: str, color: str = MUTED) -> None:
    ax.annotate("", xy=(x + 0.11, y), xytext=(x, y), arrowprops={"arrowstyle": "->", "lw": 0.75, "color": color})
    ax.annotate("", xy=(x, y + 0.11), xytext=(x, y), arrowprops={"arrowstyle": "->", "lw": 0.75, "color": color})
    ax.text(x + 0.12, y - 0.005, r"$e_x$", fontsize=6.8, color=color, ha="left", va="top")
    ax.text(x - 0.005, y + 0.12, r"$e_y$", fontsize=6.8, color=color, ha="right", va="bottom")
    if angle_label:
        ax.text(x + 0.025, y + 0.025, angle_label, fontsize=6.8, color=color, ha="left", va="bottom", bbox=text_box(), zorder=8)


def label_joint(ax, x: float, y: float, label: str) -> None:
    ax.text(x + 0.035, y + 0.035, label, ha="left", va="bottom", fontsize=8.2, color=INK, weight="bold")


def setup_panel(ax, title: str, subtitle: str) -> None:
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.text(0.02, 0.96, title, ha="left", va="top", fontsize=10, weight="bold", color=INK)
    ax.text(0.02, 0.89, subtitle, ha="left", va="top", fontsize=7.5, color=MUTED)


def draw_single(ax) -> None:
    setup_panel(ax, "single pendulum", "CD(3) + DP1(3); driven theta(t)")
    add_global_axes(ax)
    pivot = (0.50, 0.73)
    tip = (0.72, 0.28)
    add_ground(ax, *pivot)
    add_pin(ax, *pivot)
    label_joint(ax, *pivot, "A")
    add_bar(ax, pivot[0], pivot[1], tip[0], tip[1], BLUE, "bar L=4", label_offset=(0.065, 0.045))
    add_body_frame(ax, 0.54, 0.49, "")
    ax.annotate(
        r"$\theta(t)$",
        xy=(0.63, 0.54),
        xytext=(0.78, 0.65),
        arrowprops={"arrowstyle": "->", "lw": 0.8, "color": MUTED},
        fontsize=9,
        color=INK,
    )
    ax.text(0.08, 0.16, r"$s_1=(-2,0,0)$", fontsize=7.4, color=MUTED)
    ax.text(0.08, 0.11, "FullVA: Phi, dPhi, ddPhi", fontsize=7.4, color=MUTED)


def draw_double(ax) -> None:
    setup_panel(ax, "double pendulum", "CD(6) + DP1(4); nested FullVA reference")
    add_global_axes(ax)
    p0 = (0.35, 0.76)
    p1 = (0.55, 0.47)
    p2 = (0.76, 0.23)
    add_ground(ax, *p0)
    add_pin(ax, *p0)
    label_joint(ax, *p0, "A")
    add_bar(ax, *p0, *p1, color=GREEN, label="body 1", label_offset=(0.04, 0.075))
    add_pin(ax, *p1)
    label_joint(ax, *p1, "B")
    add_bar(ax, *p1, *p2, color=BLUE, label="body 2", label_offset=(0.055, 0.035))
    add_pin(ax, *p2)
    add_body_frame(ax, 0.45, 0.57, "")
    add_body_frame(ax, 0.64, 0.34, "")
    ax.text(0.08, 0.16, r"$s_1=(-2,0,0)$, $s_2=(-1,0,0)$", fontsize=7.2, color=MUTED)
    ax.text(0.08, 0.11, r"$h_{\rm ref}=0.005$; friction disabled", fontsize=7.2, color=MUTED)


def draw_four_link(ax) -> None:
    setup_panel(ax, "four-link loop", "CD(12) + DP1(6); driven closed loop")
    add_global_axes(ax)
    pts = [(0.25, 0.30), (0.36, 0.68), (0.68, 0.62), (0.76, 0.28)]
    add_ground(ax, pts[0][0], pts[0][1] - 0.04, 0.16)
    add_ground(ax, pts[3][0], pts[3][1] - 0.04, 0.16)
    add_bar(ax, *pts[0], *pts[1], color=BLUE, label="1")
    add_bar(ax, *pts[1], *pts[2], color=GREEN, label="2")
    add_bar(ax, *pts[2], *pts[3], color=ORANGE, label="3")
    for label, pt in zip(["A", "B", "C", "D"], pts):
        add_pin(ax, *pt)
        label_joint(ax, *pt, label)
    add_body_frame(ax, 0.30, 0.48, "")
    add_body_frame(ax, 0.52, 0.68, "")
    add_body_frame(ax, 0.72, 0.44, "")
    ax.plot([pts[0][0], pts[3][0]], [pts[0][1] - 0.04, pts[3][1] - 0.04], color=MUTED, lw=1.0, ls="--")
    ax.annotate(r"$\cos(\pi t+\pi/2)$", xy=pts[0], xytext=(0.08, 0.50),
                arrowprops={"arrowstyle": "->", "lw": 0.75, "color": MUTED}, fontsize=7.2, color=MUTED)
    ax.text(0.08, 0.15, r"$D=(-4,-8.5,0)$ ground mark", fontsize=7.2, color=MUTED)
    ax.text(0.08, 0.10, "Phi=0, Phi_q qdot=nu, Phi_q qdd=gamma", fontsize=7.2, color=MUTED)


def draw_slider(ax) -> None:
    setup_panel(ax, "slider-crank", "CD(6) + DP1(7) + DP2(4) + D(1)")
    add_global_axes(ax)
    crank0 = (0.23, 0.43)
    crank1 = (0.43, 0.63)
    slider = (0.76, 0.43)
    add_ground(ax, crank0[0], crank0[1] - 0.05, 0.16)
    add_pin(ax, *crank0)
    label_joint(ax, *crank0, "A")
    add_bar(ax, *crank0, *crank1, color=BLUE, label="crank", label_offset=(0.025, 0.065))
    add_pin(ax, *crank1)
    label_joint(ax, *crank1, "B")
    add_bar(ax, *crank1, *slider, color=GREEN, label="rod", label_offset=(0.055, 0.04))
    add_block(ax, slider[0], slider[1], 0.18, 0.10, ORANGE, "slider")
    label_joint(ax, slider[0] - 0.09, slider[1], "C")
    label_joint(ax, slider[0] + 0.09, slider[1], "D")
    add_body_frame(ax, 0.30, 0.53, "")
    add_body_frame(ax, 0.58, 0.55, "")
    ax.plot([0.58, 0.94], [0.34, 0.34], color=INK, lw=1.0)
    ax.plot([0.58, 0.94], [0.52, 0.52], color=INK, lw=1.0)
    ax.annotate("", xy=(0.91, 0.36), xytext=(0.62, 0.36), arrowprops={"arrowstyle": "<->", "lw": 0.9, "color": MUTED})
    ax.annotate(r"$\cos(-2\pi t+\pi/2)$", xy=crank0, xytext=(0.10, 0.70),
                arrowprops={"arrowstyle": "->", "lw": 0.75, "color": MUTED}, fontsize=7.2, color=MUTED)
    ax.text(0.08, 0.16, r"$s_4=(0,0.1,0.12)$; distance row $f=1$", fontsize=7.0, color=MUTED)
    ax.text(0.08, 0.11, r"prismatic DP1/DP2 rows; residual $6.49\,10^{-15}$", fontsize=7.0, color=MUTED)


def main() -> int:
    FIGURES.mkdir(exist_ok=True)
    FLAT.mkdir(exist_ok=True)
    generate_convergence_figure()
    generate_method_stage_architecture_figure()
    fig, axes = plt.subplots(2, 2, figsize=(7.8, 5.75), constrained_layout=True)
    draw_single(axes[0, 0])
    draw_double(axes[0, 1])
    draw_four_link(axes[1, 0])
    draw_slider(axes[1, 1])
    fig.suptitle("ASME-style lower-pair validation mechanisms", fontsize=13, weight="bold", color=INK)
    out = FIGURES / "asme_lower_pair_graph_bridge.png"
    flat_out = FLAT / "Figure_2_asme_lower_pair_graph_bridge.png"
    fig.savefig(out, dpi=300, bbox_inches="tight")
    fig.savefig(flat_out, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(out)
    print(flat_out)
    generate_claim_boundary_limitations_figure()
    generate_coarse_baseline_work_precision_figure()
    generate_closed_loop_true_dynamic_order_figure()
    generate_all_method_result_matrix_figure()
    generate_work_precision_compendium_figure()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
