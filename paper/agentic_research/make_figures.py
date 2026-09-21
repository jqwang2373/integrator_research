#!/usr/bin/env python3
"""Figures for the agentic-research meta-paper, all drawn from repository data.

* fig_versions.png   : the 49 versioned experiments by phase, with code size and result count;
* fig_session.png    : activity of the final agent session (tool calls and human messages per 6 h,
                       and the category split of the tool calls), from the session transcript;
* fig_pipeline.png   : schematic of the process (human, agent, versioned tree, evidence ledger,
                       proof sandbox, memory, manuscript pipeline).
"""

from __future__ import annotations

import collections
import csv
import datetime
import glob
import json
import os
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
plt.rcParams.update({"font.size": 9, "axes.titlesize": 9.5, "axes.labelsize": 9, "legend.fontsize": 8,
                     "xtick.labelsize": 8, "ytick.labelsize": 8, "figure.dpi": 220, "savefig.dpi": 220})

PHASES = [
    ("Lie-group basics", range(1, 6), "#4C72B0"),
    ("constrained DAE closure", range(6, 14), "#55A868"),
    ("friction and baselines", range(14, 23), "#C44E52"),
    ("absolute-coordinate FullVA", range(23, 30), "#8172B2"),
    ("sparse solver scaling", range(30, 46), "#CCB974"),
    ("validation anchors", range(46, 49), "#64B5CD"),
    ("paper experiments", range(49, 50), "#8C8C8C"),
]


def phase_of(v: int):
    for name, rng, col in PHASES:
        if v in rng:
            return name, col
    return "other", "#999999"


def fig_versions() -> None:
    rows = []
    for d in sorted((REPO / "numerics").glob("v0*")):
        v = int(d.name[1:4])
        py = list(d.glob("*.py"))
        lines = sum(sum(1 for _ in open(p, encoding="utf-8", errors="replace")) for p in py)
        results = sum(1 for _ in (d / "results").rglob("*") if _.is_file()) if (d / "results").exists() else 0
        rows.append((v, d.name, lines, results))
    fig, axes = plt.subplots(2, 1, figsize=(6.6, 3.6), sharex=True)
    xs = [r[0] for r in rows]
    cols = [phase_of(r[0])[1] for r in rows]
    axes[0].bar(xs, [r[2] for r in rows], color=cols, width=0.8)
    axes[0].set_yscale("log"); axes[0].set_ylabel("Python lines")
    axes[1].bar(xs, [r[3] for r in rows], color=cols, width=0.8)
    axes[1].set_yscale("log"); axes[1].set_ylabel("result files"); axes[1].set_xlabel("version")
    handles = [patches.Patch(color=c, label=f"{n} (v{min(r):03d}–v{max(r):03d})") for n, r, c in PHASES]
    axes[0].legend(handles=handles, ncol=2, fontsize=6.8, loc="upper left", frameon=False)
    for ax in axes:
        ax.grid(True, axis="y", alpha=0.3); ax.set_xlim(0, 50)
    axes[1].set_xticks(range(1, 50, 4))
    fig.tight_layout(); fig.savefig(FIG / "fig_versions.png"); plt.close(fig)
    with open(HERE / "version_table.csv", "w", newline="") as f:
        w = csv.writer(f); w.writerow(["version", "dir", "python_lines", "result_files", "phase"])
        for r in rows: w.writerow([*r, phase_of(r[0])[0]])


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


def fig_session() -> None:
    proj = Path.home() / ".claude" / "projects"
    files = glob.glob(str(proj / "*uw-paper-integrator-research*" / "*.jsonl"))
    if not files:
        print("no transcript found; skipping session figure"); return
    tools = collections.Counter(); users = collections.Counter(); cats = collections.Counter(); first = None
    n_user = n_asst = n_tool = n_entries = n_shell = 0
    for f in files:
        with open(f, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                try: d = json.loads(line)
                except Exception: continue
                ts = d.get("timestamp")
                if not ts: continue
                t = datetime.datetime.fromisoformat(ts.replace("Z", "+00:00"))
                first = first or t
                b = int((t - first).total_seconds() // (6 * 3600))
                if d.get("type") == "user":
                    c = d.get("message", {}).get("content")
                    if isinstance(c, str):
                        txt = c
                    elif isinstance(c, list) and c and isinstance(c[0], dict) and c[0].get("type") == "text":
                        txt = c[0].get("text", "")
                    else:
                        continue  # tool results
                    n_entries += 1
                    # Harness-generated user-role entries: compaction summaries, image attachments, task
                    # notifications, slash-command and shell echoes (all start with an XML-like tag).
                    if d.get("isMeta") or d.get("isCompactSummary"):
                        continue
                    if txt.lstrip().startswith("<bash-input>"):
                        n_shell += 1; continue
                    if txt.lstrip().startswith("<"):
                        continue
                    users[b] += 1; n_user += 1
                elif d.get("type") == "assistant":
                    n_asst += 1
                    for blk in d.get("message", {}).get("content", []) or []:
                        if isinstance(blk, dict) and blk.get("type") == "tool_use":
                            tools[b] += 1; n_tool += 1
                            name = blk.get("name")
                            cats[classify(blk.get("input", {}).get("command", "")) if name == "Bash" else f"file {name.lower()}"] += 1
    fig, axes = plt.subplots(1, 2, figsize=(6.6, 2.35), gridspec_kw={"width_ratios": [1.6, 1]})
    bins = sorted(set(tools) | set(users))
    axes[0].bar([b * 6 for b in bins], [tools[b] for b in bins], width=5, color="#4C72B0", label="agent tool calls")
    ax2 = axes[0].twinx(); ax2.plot([b * 6 + 3 for b in bins], [users[b] for b in bins], "o-", color="#C44E52", ms=3, label="human messages")
    axes[0].set_xlabel("hours since session start"); axes[0].set_ylabel("tool calls per 6 h"); ax2.set_ylabel("human messages per 6 h")
    h1, l1 = axes[0].get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels(); axes[0].legend(h1 + h2, l1 + l2, loc="upper center", fontsize=7)
    axes[0].set_title("activity over the session", fontsize=8.5)
    order = [k for k, _ in cats.most_common()]
    axes[1].barh(range(len(order)), [cats[k] for k in order], color="#55A868")
    axes[1].set_yticks(range(len(order))); axes[1].set_yticklabels(order, fontsize=7); axes[1].invert_yaxis()
    axes[1].set_xlabel("tool calls"); axes[1].set_title("what the tool calls did", fontsize=8.5)
    for ax in axes: ax.grid(True, axis="x" if ax is axes[1] else "y", alpha=0.3)
    fig.tight_layout(); fig.savefig(FIG / "fig_session.png"); plt.close(fig)
    fmt = lambda n: f"{n:,}".replace(",", "\\,")
    (HERE / "stats.tex").write_text(
        "\\newcommand{\\nHuman}{%d}\n\\newcommand{\\nTurns}{%s}\n\\newcommand{\\nTools}{%s}\n"
        "\\newcommand{\\nEntries}{%d}\n\\newcommand{\\nHarness}{%d}\n\\newcommand{\\nShell}{%d}\n"
        % (n_user, fmt(n_asst), fmt(n_tool), n_entries, n_entries - n_user - n_shell, n_shell))
    json.dump({"human_messages": n_user, "user_role_entries": n_entries, "shell_commands_typed": n_shell,
               "agent_turns": n_asst, "tool_calls": n_tool, "categories": cats.most_common(),
               "tool_calls_per_6h": {str(b * 6): tools[b] for b in bins}, "human_per_6h": {str(b * 6): users[b] for b in bins}},
              open(HERE / "session_stats.json", "w"), indent=1)


def box(ax, x, y, w, h, title, lines, color, face="#ffffff", ts=8.5, bs=7.2):
    """Rounded box with a bold title and body lines; returns the body Text and the box width."""
    ax.add_patch(patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.008,rounding_size=0.012", ec=color, fc=face, lw=1.3))
    ax.text(x + w / 2, y + h - 0.03, title, ha="center", va="top", fontsize=ts, weight="bold", color="#222")
    body = ax.text(x + w / 2, y + h - 0.13, "\n".join(lines), ha="center", va="top", fontsize=bs, color="#444", linespacing=1.3)
    return body, w


def fit_texts(fig, ax, items, margin=0.90, min_size=5.5):
    """Shrink each body text until its widest line fits inside `margin` of its box width."""
    fig.canvas.draw()
    for txt, w in items:
        for _ in range(12):
            bb = txt.get_window_extent(fig.canvas.get_renderer())
            box_px = ax.transData.transform((w, 0))[0] - ax.transData.transform((0, 0))[0]
            if bb.width <= margin * box_px or txt.get_fontsize() <= min_size:
                break
            txt.set_fontsize(max(min_size, txt.get_fontsize() * margin * box_px / bb.width))
            fig.canvas.draw()


def arrow(ax, p, q, color="#555", style="->", lw=1.1):
    ax.annotate("", xy=q, xytext=p, arrowprops={"arrowstyle": style, "lw": lw, "color": color, "shrinkA": 2, "shrinkB": 2})


def fig_pipeline() -> None:
    fig, ax = plt.subplots(figsize=(6.6, 3.3)); ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    items = []
    yt, ht = 0.66, 0.31
    items.append(box(ax, 0.01, yt, 0.25, ht, "human", ["goal, taste,", "authorizations,", "review of figures and prose"], "#C44E52", ts=9, bs=7.2))
    items.append(box(ax, 0.32, yt, 0.36, ht, "coding agent", ["reads and writes files;", "runs scripts, LaTeX, Lean, git;", "one context window at a time"], "#4C72B0", ts=9, bs=7.2))
    items.append(box(ax, 0.74, yt, 0.25, ht, "memory", ["one file per fact:", "decisions, constraints,", "feedback; loaded each session"], "#8172B2", ts=9, bs=7.2))
    ym = yt + ht / 2
    arrow(ax, (0.26, ym), (0.32, ym), style="<->"); arrow(ax, (0.68, ym), (0.74, ym), style="<->")
    y, h = 0.11, 0.44
    items.append(box(ax, 0.01, y, 0.23, h, "versioned tree", ["one directory per", "hypothesis (v001–v049);", "read-only once superseded;", "negative results kept"], "#55A868", face="#f3f9f3", ts=9, bs=7.0))
    items.append(box(ax, 0.26, y, 0.23, h, "evidence ledger", ["146 builders write records;", "183 validators pin claims,", "numbers, phrases, hashes;", "gates and blockers;", "frozen at the old paper"], "#CCB974", face="#fbf8ec", ts=9, bs=7.0))
    items.append(box(ax, 0.51, y, 0.23, h, "proof sandbox", ["Lean 4 + Mathlib;", "57 theorems;", "exhaustive axiom audit;", "implemented residual", "transcribed row by row"], "#64B5CD", face="#eef7fa", ts=9, bs=7.0))
    items.append(box(ax, 0.76, y, 0.23, h, "manuscript", ["sections → assemble → PDF,", "flat and arXiv copies;", "validator: every table", "number equals its", "result-file value"], "#8C8C8C", face="#f4f4f4", ts=9, bs=7.0))
    for x in (0.125, 0.375, 0.625, 0.875):
        arrow(ax, (0.50, yt), (x, y + h), color="#4C72B0")
    ax.text(0.5, 0.0, "command boundary: no heavy campaign as a routine check;\nthe external campaign runs only after an explicit approval sentence",
            ha="center", va="bottom", fontsize=7, color="#666", style="italic", linespacing=1.2)
    fit_texts(fig, ax, items)
    fig.savefig(FIG / "fig_pipeline.png", bbox_inches="tight"); plt.close(fig)


if __name__ == "__main__":
    FIG.mkdir(exist_ok=True)
    fig_versions(); fig_session(); fig_pipeline()
    print("figures written to", FIG)
