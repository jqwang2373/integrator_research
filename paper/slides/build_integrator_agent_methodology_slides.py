#!/usr/bin/env python3
"""Build Huzaifa-style slides about an agent for integrator research."""

from __future__ import annotations

import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from build_fullva_huzaifa_slides import (
    BLUE,
    DARK,
    FIG,
    GREEN,
    LIGHT,
    MARGIN_X,
    MID,
    MUTED,
    ORANGE,
    PAPER,
    RED,
    ROOT,
    TEMPLATE,
    WHITE,
    ImageRef,
    Rect,
    Slide,
    TextBox,
    app_xml,
    content_types_xml,
    extract_default_text_style,
    fit_rect,
    number_cards_slide,
    presentation_xml,
    rels_xml,
    section_slide,
    slide_xml,
    statement_slide,
    two_col_slide,
)


OUT = ROOT / "Integrator_AutoResearch_Agent_Methodology_Huzaifa_style_slides.pptx"
DATE_TEXT = "06/09/2026"

if not TEMPLATE.exists():
    TEMPLATE = ROOT / "Jingquan_FullVA_Huzaifa_style_slides.pptx"


def bullets_slide(title: str, bullets: list[str], subtitle: str | None = None, size: int = 20) -> Slide:
    s = Slide(title=title)
    y = 1_980_000 if subtitle else 1_620_000
    if subtitle:
        s.texts.append(TextBox([subtitle], MARGIN_X, 1_420_000, 10_515_600, 420_000, 16, MUTED, name="Subtitle"))
    for i, b in enumerate(bullets):
        yy = y + i * 690_000
        s.rects.append(Rect(MARGIN_X, yy + 65_000, 100_000, 100_000, RED if i == 0 else DARK, None, "Bullet mark"))
        s.texts.append(TextBox([b], MARGIN_X + 225_000, yy, 9_950_000, 500_000, size, DARK, name=f"Bullet {i+1}"))
    return s


def process_slide(title: str, steps: list[tuple[str, str, str]]) -> Slide:
    s = Slide(title=title)
    x0 = MARGIN_X
    y = 1_690_000
    box_w = 1_750_000
    gap = 125_000
    for i, (num, head, desc) in enumerate(steps):
        x = x0 + i * (box_w + gap)
        color = [RED, BLUE, GREEN, ORANGE, DARK, "7A4EA3"][i % 6]
        s.rects.append(Rect(x, y, box_w, 3_700_000, LIGHT, MID, "Process box"))
        s.texts.append(TextBox([num], x + 110_000, y + 210_000, 390_000, 390_000, 20, WHITE, True, align="ctr", valign="m", fill=color, name="Step num"))
        s.texts.append(TextBox([head], x + 120_000, y + 850_000, box_w - 240_000, 640_000, 16, DARK, True, name="Step head"))
        s.texts.append(TextBox([desc], x + 120_000, y + 1_560_000, box_w - 240_000, 1_600_000, 12, MUTED, name="Step desc"))
    return s


def table_slide(title: str, headers: list[str], rows: list[list[str]], widths: list[int]) -> Slide:
    s = Slide(title=title)
    x = MARGIN_X
    y0 = 1_470_000
    for j, h in enumerate(headers):
        s.rects.append(Rect(x, y0, widths[j], 395_000, DARK, None, "Header"))
        s.texts.append(TextBox([h], x + 70_000, y0 + 90_000, widths[j] - 140_000, 220_000, 11, WHITE, True, align="ctr", name="Header text"))
        x += widths[j]
    row_h = min(600_000, int(3_950_000 / max(1, len(rows))))
    for i, row in enumerate(rows):
        y = y0 + 395_000 + i * row_h
        x = MARGIN_X
        fill = LIGHT if i % 2 == 0 else WHITE
        for j, value in enumerate(row):
            s.rects.append(Rect(x, y, widths[j], row_h, fill, MID, "Cell"))
            color = RED if j == 0 else DARK
            s.texts.append(TextBox([value], x + 70_000, y + 85_000, widths[j] - 140_000, row_h - 150_000, 10, color, j == 0, name="Cell text"))
            x += widths[j]
    return s


def reference_landscape_slide() -> Slide:
    return table_slide(
        "Reference landscape the agent inherits",
        ["Stream", "Representative references", "Why the verifier needs them"],
        [
            ["index-3 DAE",
             "Hairer-Wanner 1996; Gear-Leimkuhler-Gupta 1985",
             "separate position, velocity, acceleration, and multiplier evidence"],
            ["Lie-group integration",
             "Munthe-Kaas 1998/1999; Bruls-Cardona-Arnold 2012; Wieloch-Arnold 2021",
             "keep rotations on the group while preserving the one-step method identity"],
            ["time finite elements",
             "Borri-Atluri 1988; Hughes-Hulbert 1988; Chaturvedi-Sandu-Sandu 2026",
             "treat source-paper residual reproduction as a specific claim gate"],
            ["SBEL baselines",
             "Taves-Kissel-Negrut 2020; Kissel-Negrut-Taves 2021/2022; Fang et al. 2023",
             "make ASME examples and external rows comparable under explicit policy"],
            ["friction/contact",
             "Brown-McPhee 2016; Stewart-Trinkle 1996; Anitescu-Potra 1997",
             "separate smooth regularized order from nonsmooth/contact diagnostics"],
        ],
        [1_900_000, 4_900_000, 3_715_600],
    )


def references_slide(title: str, refs: list[tuple[str, list[str]]]) -> Slide:
    s = Slide(title=title)
    y0 = 1_410_000
    row_h = min(690_000, int(4_650_000 / max(1, len(refs))))
    tag_w = 1_430_000
    body_w = 10_515_600 - tag_w
    for i, (tag, lines) in enumerate(refs):
        y = y0 + i * row_h
        fill = LIGHT if i % 2 == 0 else WHITE
        s.rects.append(Rect(MARGIN_X, y, 10_515_600, row_h, fill, MID, "Reference row"))
        s.rects.append(Rect(MARGIN_X, y, 95_000, row_h, RED if i == 0 else DARK, None, "Reference accent"))
        s.texts.append(TextBox([tag], MARGIN_X + 160_000, y + 105_000, tag_w - 250_000, row_h - 180_000, 11, RED, True, name="Reference tag"))
        s.texts.append(TextBox(lines, MARGIN_X + tag_w + 90_000, y + 72_000, body_w - 180_000, row_h - 120_000, 9, DARK, name="Reference text"))
    return s


def evolution_phase_slide(title: str, versions: str, trigger: str, response: list[str], lesson: list[str]) -> Slide:
    s = Slide(title=title)
    s.texts.append(TextBox([versions], MARGIN_X, 1_420_000, 10_515_600, 360_000, 17, RED, True, name="Version range"))
    x1 = MARGIN_X
    x2 = MARGIN_X + 3_530_000
    x3 = MARGIN_X + 7_060_000
    w = 3_260_000
    y = 1_950_000
    heads = [("Blocker", trigger, RED), ("Version response", response, BLUE), ("Agent lesson", lesson, GREEN)]
    for x, (head, body, color) in zip([x1, x2, x3], heads):
        s.rects.append(Rect(x, y, w, 3_650_000, LIGHT, MID, "Evolution box"))
        s.rects.append(Rect(x, y, w, 80_000, color, None, "Evolution accent"))
        s.texts.append(TextBox([head], x + 170_000, y + 260_000, w - 340_000, 390_000, 19, DARK, True, name="Evolution head"))
        if isinstance(body, str):
            lines = [body]
        else:
            lines = body
        s.texts.append(TextBox(lines, x + 170_000, y + 850_000, w - 340_000, 2_320_000, 14, DARK, name="Evolution body"))
    return s


def evolution_timeline_slide() -> Slide:
    s = Slide(title="From v001 to v048: blocker-driven evolution")
    phases = [
        ("v001-v005", "Lie-group basics", "SO(3) order\nsmooth mechanics", RED),
        ("v006-v013", "DAE consistency", "endpoint closure\nAD + Gauss6", BLUE),
        ("v014-v022", "Friction", "smoothness sweep\nadaptivity", GREEN),
        ("v023-v029", "FullVA", "velocity/acceleration\nconsistency", ORANGE),
        ("v030-v045", "Scaling", "sparse Newton\ncolored AD", "7A4EA3"),
        ("v046-v048", "Claim gates", "ASME + paper\nsame-test scaffold", DARK),
    ]
    x0 = MARGIN_X
    y = 2_000_000
    w = 1_620_000
    gap = 120_000
    for i, (vr, head, body, color) in enumerate(phases):
        x = x0 + i * (w + gap)
        s.rects.append(Rect(x, y, w, 1_580_000, LIGHT, MID, "Timeline block"))
        s.rects.append(Rect(x, y, w, 95_000, color, None, "Timeline accent"))
        s.texts.append(TextBox([vr], x + 90_000, y + 220_000, w - 180_000, 260_000, 12, color, True, align="ctr", name="Version label"))
        s.texts.append(TextBox([head], x + 90_000, y + 560_000, w - 180_000, 360_000, 15, DARK, True, align="ctr", name="Phase label"))
        s.texts.append(TextBox(body.split("\n"), x + 90_000, y + 1_000_000, w - 180_000, 430_000, 11, MUTED, align="ctr", name="Phase body"))
        if i < len(phases) - 1:
            ax = x + w + 18_000
            s.rects.append(Rect(ax, y + 720_000, gap - 36_000, 42_000, color, None, "Arrow shaft"))
            s.texts.append(TextBox([">"], ax + gap - 105_000, y + 615_000, 95_000, 200_000, 18, color, True, align="ctr", name="Arrow head"))
    s.texts.append(TextBox([
        "Reading rule: each arrow is a measured blocker, not a stylistic refactor.",
        "The agent's verifier set grows because each phase finds a new way an integrator can fail."
    ], MARGIN_X, 4_370_000, 10_515_600, 720_000, 18, DARK, align="ctr", name="Timeline takeaway"))
    return s


def impact_chain_slide() -> Slide:
    s = Slide(title="Why this integrator problem matters")
    nodes = [
        ("Mechanism model", "joints, finite rotations,\nconstraints, friction", RED),
        ("Time integrator", "one-step map,\nresidual, solver", BLUE),
        ("Simulation evidence", "orders, constraints,\nenergy, reactions", GREEN),
        ("Engineering use", "design, control,\ndigital twins", ORANGE),
    ]
    x0 = MARGIN_X
    y = 1_850_000
    w = 2_170_000
    gap = 430_000
    for i, (head, body, color) in enumerate(nodes):
        x = x0 + i * (w + gap)
        s.rects.append(Rect(x, y, w, 1_640_000, LIGHT, MID, "Impact node"))
        s.rects.append(Rect(x, y, w, 90_000, color, None, "Impact accent"))
        s.texts.append(TextBox([head], x + 120_000, y + 330_000, w - 240_000, 390_000, 17, DARK, True, align="ctr", name="Impact head"))
        s.texts.append(TextBox(body.split("\n"), x + 120_000, y + 900_000, w - 240_000, 420_000, 12, MUTED, align="ctr", name="Impact body"))
        if i < len(nodes) - 1:
            ax = x + w + 85_000
            s.rects.append(Rect(ax, y + 760_000, gap - 170_000, 42_000, color, None, "Impact arrow"))
            s.texts.append(TextBox([">"], ax + gap - 220_000, y + 657_000, 110_000, 210_000, 20, color, True, align="ctr", name="Impact arrow head"))
    s.rects.append(Rect(MARGIN_X, 4_360_000, 10_515_600, 700_000, "FFF7E8", ORANGE, "Impact warning"))
    s.texts.append(TextBox(["If the one-step map is wrong, the downstream engineering evidence is precise-looking but physically misleading."],
                           MARGIN_X + 240_000, 4_555_000, 10_035_600, 300_000, 18, DARK, True, align="ctr", name="Impact warning text"))
    return s


def lab_ecosystem_slide() -> Slide:
    s = Slide(title="This is a lab-scale research problem")
    center_x = MARGIN_X + 4_010_000
    center_y = 2_560_000
    s.rects.append(Rect(center_x, center_y, 2_520_000, 1_000_000, "FFF1F1", RED, "Center"))
    s.texts.append(TextBox(["Reliable multibody", "time integration"], center_x + 180_000, center_y + 220_000, 2_160_000, 520_000, 18, DARK, True, align="ctr", name="Center text"))
    nodes = [
        (MARGIN_X, 1_420_000, "Lie-group methods", "SO(3), SE(3), charts,\nGauss/RKMK/TFE", BLUE),
        (MARGIN_X + 7_570_000, 1_420_000, "Mechanism models", "pendula, four-link,\nslider-crank, chains", GREEN),
        (MARGIN_X, 3_900_000, "Solver infrastructure", "AD, sparse Newton,\npattern/coloring", ORANGE),
        (MARGIN_X + 7_570_000, 3_900_000, "Evidence and papers", "benchmarks, figures,\nclaims, reproducibility", "7A4EA3"),
    ]
    for x, y, head, body, color in nodes:
        s.rects.append(Rect(x, y, 3_000_000, 1_170_000, LIGHT, MID, "Lab node"))
        s.rects.append(Rect(x, y, 3_000_000, 80_000, color, None, "Node accent"))
        s.texts.append(TextBox([head], x + 140_000, y + 250_000, 2_720_000, 310_000, 17, DARK, True, align="ctr", name="Node head"))
        s.texts.append(TextBox(body.split("\n"), x + 140_000, y + 650_000, 2_720_000, 350_000, 12, MUTED, align="ctr", name="Node body"))
    s.texts.append(TextBox([
        "Many people can work on different parts of this stack at the same time.",
        "The agent's job is to keep their methods, examples, verifiers, and paper claims compatible."
    ], MARGIN_X, 5_540_000, 10_515_600, 420_000, 16, DARK, True, align="ctr", name="Lab note"))
    return s


def lab_workflow_slide() -> Slide:
    s = Slide(title="Why a lab needs this agent")
    cols = [
        ("Without shared gates", ["Each researcher keeps a private benchmark.", "Proof status lives in notes.", "External baselines drift.", "Paper claims are reconciled late."], RED),
        ("With an agent pipeline", ["Methods enter through MethodSpec.", "Examples enter through ProblemSpec.", "Claims enter through ClaimSpec.", "Validators reconcile everyone early."], GREEN),
    ]
    for i, (head, lines, color) in enumerate(cols):
        x = MARGIN_X + i * 5_260_000
        w = 5_000_000
        s.rects.append(Rect(x, 1_620_000, w, 3_800_000, LIGHT, MID, "Lab workflow col"))
        s.rects.append(Rect(x, 1_620_000, w, 90_000, color, None, "Lab workflow accent"))
        s.texts.append(TextBox([head], x + 220_000, 1_920_000, w - 440_000, 420_000, 20, DARK, True, align="ctr", name="Workflow head"))
        for j, line in enumerate(lines):
            yy = 2_650_000 + j * 600_000
            s.rects.append(Rect(x + 280_000, yy + 60_000, 85_000, 85_000, color, None, "Workflow bullet"))
            s.texts.append(TextBox([line], x + 470_000, yy, w - 700_000, 390_000, 15, DARK, name="Workflow item"))
    return s


def sandbox_stack_slide() -> Slide:
    s = Slide(title="Verifier sandbox stack")
    layers = [
        ("Level 3", "External source-policy campaigns", "published h grids, same references, human opt-in", RED),
        ("Level 2", "Full artifact generators", "run_v047.py, version-wide reports, plots, CSV/JSON", ORANGE),
        ("Level 1", "Target audits", "one hypothesis, bounded h-sweep, JSON-only when possible", BLUE),
        ("Level 0", "Read-only validators", "claim/package/proof checks, no regeneration", GREEN),
    ]
    y0 = 1_540_000
    for i, (lvl, head, desc, color) in enumerate(layers):
        y = y0 + i * 900_000
        x = MARGIN_X + i * 420_000
        w = 10_515_600 - i * 840_000
        s.rects.append(Rect(x, y, w, 720_000, LIGHT, MID, "Sandbox layer"))
        s.rects.append(Rect(x, y, 110_000, 720_000, color, None, "Layer accent"))
        s.texts.append(TextBox([lvl], x + 210_000, y + 100_000, 1_100_000, 230_000, 14, color, True, name="Level"))
        s.texts.append(TextBox([head], x + 1_440_000, y + 85_000, 3_400_000, 260_000, 18, DARK, True, name="Layer head"))
        s.texts.append(TextBox([desc], x + 1_440_000, y + 390_000, w - 1_700_000, 230_000, 13, MUTED, name="Layer desc"))
    s.texts.append(TextBox(["Default path moves upward only when the lower layer cannot answer the claim question."],
                           MARGIN_X, 5_420_000, 10_515_600, 360_000, 17, DARK, True, align="ctr", name="Sandbox note"))
    return s


def proof_flow_slide() -> Slide:
    s = Slide(title="Proof gate: what can enter the theorem")
    boxes = [
        ("Gauss defect", "classical order\nin smooth chart", RED),
        ("132-row residual bridge", "implemented rows\nAD-bound identity", BLUE),
        ("Endpoint closure", "raw/KKT closure\nO(h^7) perturbation", GREEN),
        ("Newton scale", "eta_h <= c h^7\nbranch-selected", ORANGE),
        ("Grid error", "conditional\nsixth-order claim", DARK),
    ]
    x0 = MARGIN_X
    y = 1_820_000
    w = 1_760_000
    gap = 245_000
    for i, (head, body, color) in enumerate(boxes):
        x = x0 + i * (w + gap)
        s.rects.append(Rect(x, y, w, 1_560_000, LIGHT, MID, "Proof box"))
        s.rects.append(Rect(x, y, w, 85_000, color, None, "Proof accent"))
        s.texts.append(TextBox([head], x + 110_000, y + 285_000, w - 220_000, 400_000, 15, DARK, True, align="ctr", name="Proof head"))
        s.texts.append(TextBox(body.split("\n"), x + 110_000, y + 850_000, w - 220_000, 460_000, 11, MUTED, align="ctr", name="Proof body"))
        if i < len(boxes) - 1:
            ax = x + w + 55_000
            s.rects.append(Rect(ax, y + 705_000, gap - 110_000, 40_000, color, None, "Proof arrow"))
            s.texts.append(TextBox([">"], ax + gap - 155_000, y + 603_000, 100_000, 200_000, 18, color, True, align="ctr", name="Proof arrow head"))
    s.rects.append(Rect(MARGIN_X, 4_200_000, 10_515_600, 620_000, "FFF1F1", RED, "Do not enter"))
    s.texts.append(TextBox(["Not theorem inputs: fixed production tolerance logs, residual-only surrogate rows, external source-policy rows, primitive Taylor fragments unless their gate closes."],
                           MARGIN_X + 220_000, 4_350_000, 10_070_000, 300_000, 15, DARK, True, align="ctr", name="Non inputs"))
    return s


def numerical_ladder_visual_slide() -> Slide:
    s = Slide(title="Numerical example ladder")
    rungs = [
        ("6", "External same-test", "same h/reference/work policy", RED),
        ("5", "ASME mechanisms", "single/double/four-link/slider-crank", ORANGE),
        ("4", "Friction regimes", "smoothness sweep and cost envelope", BLUE),
        ("3", "Constrained DAE", "Phi, Phi_q v, Phi_q a closure", GREEN),
        ("2", "Smooth mechanics", "invariants and Gauss order", "7A4EA3"),
        ("1", "SO(3) kinematics", "right-action and chart sanity", DARK),
    ]
    x0 = 1_250_000
    y0 = 1_420_000
    for i, (num, head, desc, color) in enumerate(rungs):
        y = y0 + i * 650_000
        x = x0 + i * 500_000
        w = 8_900_000 - i * 740_000
        s.rects.append(Rect(x, y, w, 480_000, LIGHT, MID, "Ladder rung"))
        s.texts.append(TextBox([num], x + 120_000, y + 80_000, 320_000, 280_000, 16, WHITE, True, align="ctr", valign="m", fill=color, name="Rung num"))
        s.texts.append(TextBox([head], x + 620_000, y + 90_000, 2_500_000, 250_000, 16, DARK, True, name="Rung head"))
        s.texts.append(TextBox([desc], x + 3_270_000, y + 105_000, w - 3_520_000, 220_000, 13, MUTED, name="Rung desc"))
    s.texts.append(TextBox(["The agent climbs this ladder only when the lower rung is already stable."],
                           MARGIN_X, 5_620_000, 10_515_600, 280_000, 17, DARK, True, align="ctr", name="Ladder note"))
    return s


def claim_state_machine_slide() -> Slide:
    s = Slide(title="Claim state machine")
    states = [
        ("Hypothesis", "candidate method\nor repair idea", MUTED),
        ("Diagnostic", "useful but\nnot claim-ready", BLUE),
        ("Accepted", "gate closed\nvalidators agree", GREEN),
        ("Open", "known blocker\nstill active", ORANGE),
        ("Forbidden", "wording conflicts\nwith gate state", RED),
    ]
    x0 = MARGIN_X
    y = 1_850_000
    w = 1_720_000
    gap = 240_000
    for i, (head, body, color) in enumerate(states):
        x = x0 + i * (w + gap)
        s.rects.append(Rect(x, y, w, 1_480_000, LIGHT, MID, "Claim state"))
        s.rects.append(Rect(x, y, w, 90_000, color if color != MUTED else DARK, None, "State accent"))
        s.texts.append(TextBox([head], x + 100_000, y + 330_000, w - 200_000, 360_000, 16, DARK, True, align="ctr", name="State head"))
        s.texts.append(TextBox(body.split("\n"), x + 100_000, y + 850_000, w - 200_000, 380_000, 11, MUTED, align="ctr", name="State body"))
        if i < len(states) - 1:
            ax = x + w + 50_000
            s.rects.append(Rect(ax, y + 680_000, gap - 100_000, 36_000, DARK, None, "State arrow"))
            s.texts.append(TextBox([">"], ax + gap - 145_000, y + 578_000, 100_000, 200_000, 18, DARK, True, align="ctr", name="State arrow head"))
    s.texts.append(TextBox(["Important: a claim can move backward. New evidence can demote accepted prose to diagnostic or forbidden wording."],
                           MARGIN_X, 4_300_000, 10_515_600, 520_000, 18, DARK, True, align="ctr", name="State note"))
    return s


def figure_slide(title: str, fig_name: str, caption: str, bullets: list[str] | None = None) -> Slide:
    s = Slide(title=title)
    path = FIG / fig_name
    if bullets:
        s.texts.append(TextBox(bullets, MARGIN_X, 1_520_000, 3_240_000, 4_170_000, 16, DARK, name="Side bullets"))
        x, y, w, h = fit_rect(path, MARGIN_X + 3_560_000, 1_470_000, 6_950_000, 4_250_000)
    else:
        x, y, w, h = fit_rect(path, MARGIN_X, 1_420_000, 10_515_600, 4_520_000)
    s.images.append(ImageRef(path, x, y, w, h, fig_name))
    s.texts.append(TextBox([caption], MARGIN_X, 5_900_000, 10_515_600, 280_000, 10, MUTED, name="Caption"))
    return s


def core_xml() -> str:
    now = datetime(2026, 6, 9, 18, 0, 0, tzinfo=timezone.utc).isoformat().replace("+00:00", "Z")
    return (
        "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>"
        "<cp:coreProperties xmlns:cp=\"http://schemas.openxmlformats.org/package/2006/metadata/core-properties\" "
        "xmlns:dc=\"http://purl.org/dc/elements/1.1/\" "
        "xmlns:dcterms=\"http://purl.org/dc/terms/\" "
        "xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\">"
        "<dc:title>Integrator Auto-Research Agent Methodology Slides</dc:title>"
        "<dc:creator>Codex</dc:creator><cp:lastModifiedBy>Codex</cp:lastModifiedBy>"
        f"<dcterms:created xsi:type=\"dcterms:W3CDTF\">{now}</dcterms:created>"
        f"<dcterms:modified xsi:type=\"dcterms:W3CDTF\">{now}</dcterms:modified>"
        "</cp:coreProperties>"
    )


def title_slide() -> Slide:
    s = Slide("", kind="title", show_footer=False)
    s.texts.extend([
        TextBox(["Building an Auto-Research Agent", "for Lie-Group Integrator Design"], 720_000, 930_000, 10_850_000, 1_550_000, 40, DARK, True, name="Title"),
        TextBox(["Verifier sandboxes, proof gates, and numerical examples for multibody DAE methods"], 760_000, 2_820_000, 10_200_000, 520_000, 20, MUTED, name="Subtitle"),
        TextBox(["Jingquan Wang", "Simulation-Based Engineering Laboratory", "University of Wisconsin - Madison"], 760_000, 4_090_000, 8_900_000, 830_000, 17, MUTED, name="Author"),
        TextBox([DATE_TEXT], 760_000, 5_300_000, 2_800_000, 340_000, 14, RED, True, name="Date"),
    ])
    return s


def build_slides() -> list[Slide]:
    slides: list[Slide] = [title_slide()]

    slides.append(statement_slide(
        "Integrator research has a special failure mode",
        ["A method can look good on one plot", "and still be wrong as an integrator."],
        ["It may violate velocity-level constraints.",
         "It may only work because of an endpoint projection.",
         "It may have high observed slopes but no theorem-level residual contract.",
         "It may compare against the wrong external reference policy."]
    ))

    slides.append(two_col_slide(
        "Why this needs a domain-specific agent",
        "Generic coding agent",
        ["Can edit scripts.",
         "Can run tests.",
         "Can summarize output.",
         "Usually optimizes for task completion."],
        "Integrator research agent",
        ["Must preserve method identity.",
         "Must separate proof, numerics, and claims.",
         "Must know DAE constraint levels.",
         "Must keep external baselines honest."]
    ))

    slides.append(statement_slide(
        "Central thesis",
        ["For integrator research, the agent must co-design", "the method, the verifier sandbox, and the proof ledger."],
        ["The method object defines the one-step map.",
         "The verifier sandbox decides what can be tested safely.",
         "The proof ledger decides what can be claimed.",
         "The numerical ladder decides what must be run next."]
    ))

    slides.append(bullets_slide(
        "The talk is about how to set the agent up",
        ["How to represent a candidate integrator so the agent cannot change its identity accidentally.",
         "How to build verifier sandboxes for residuals, constraints, convergence, runtime, and external policies.",
         "How to split proof obligations into accepted, conditional, and diagnostic lanes.",
         "How to choose numerical examples that expose failure modes before paper claims are made."]
    ))

    slides.append(statement_slide(
        "Why this problem is important",
        ["Multibody simulation is only useful if the integrator", "preserves the geometry and the constraints that define the mechanism."],
        ["Finite rotations must stay on the Lie group.",
         "Bilateral joints must satisfy position, velocity, and acceleration constraints.",
         "Reaction forces and friction laws can change the engineering conclusion.",
         "Small one-step defects become large design, control, and digital-twin errors."]
    ))

    slides.append(impact_chain_slide())

    slides.append(statement_slide(
        "This is not one person's integrator problem",
        ["Our lab has many people working around the same core issue:", "how to make multibody simulation accurate, stable, fast, and defensible."],
        ["Different projects touch different parts of the stack: Lie-group methods, constrained DAEs, friction/contact, sparse solvers, benchmark mechanisms, and reproducible papers.",
         "A research agent is useful only if it can coordinate this shared evidence space.",
         "The goal is not to replace researchers; it is to make lab-scale verification and claim hygiene durable."]
    ))

    slides.append(lab_ecosystem_slide())

    slides.append(lab_workflow_slide())

    slides.append(reference_landscape_slide())

    slides.append(two_col_slide(
        "What goes wrong with a weak integrator",
        "Numerical symptom",
        ["Position looks accurate but velocity constraints drift.",
         "Projection fixes constraints but changes the trajectory.",
         "Sharp friction gives attractive but pre-asymptotic slopes.",
         "Dense Jacobians make the method unusable at scale."],
        "Research consequence",
        ["Incorrect order claim.",
         "Wrong reaction-force evidence.",
         "Unfair comparison to external baselines.",
         "A paper result that cannot be reproduced or defended."]
    ))

    slides.append(bullets_slide(
        "Why an agent is useful here",
        ["The design space is too large for one linear experiment sequence.",
         "Every candidate needs both a theorem-facing proof route and numerical stress tests.",
         "Negative results are valuable because they localize missing residual directions.",
         "The agent can maintain the audit trail while the human chooses the research direction."]
    ))

    slides.append(process_slide(
        "Roadmap",
        [("1", "Evolution story", "why the project moved from v001 to v048"),
         ("2", "Method object", "what the agent is allowed to mutate and what defines the integrator"),
         ("3", "Verifier sandbox", "bounded checks, full generators, external opt-in"),
         ("4", "Proof + numerics", "obligations, examples, nonpromotion rules"),
         ("5", "Case study", "v047/v048 as the realized pipeline")]
    ))

    slides.append(section_slide("1 / Evolution Story", "Why v001 had to become v048", "The version sequence is the clearest evidence that this is an integrator-research agent, not a generic coding agent."))

    slides.append(statement_slide(
        "The versions are not a changelog",
        ["Each version exists because the previous evidence exposed", "a specific missing gate."],
        ["A new version is created only when the research question changes.",
         "The agent records the blocker, the new verifier, and the remaining caveat.",
         "This is how the project avoids looping on the same attractive but insufficient idea."]
    ))

    slides.append(table_slide(
        "Version evolution at a glance",
        ["Phase", "Versions", "Why the project evolved"],
        [
            ["Lie-group basics", "v001-v005", "establish SO(3) order, right-action conventions, and smooth Gauss mechanics"],
            ["Constrained DAE", "v006-v013", "endpoint constraints, AD Jacobians, quaternion transport, and Gauss6 order"],
            ["Friction regime", "v014-v022", "smoothness sweeps, adaptivity, multiplier-dependent Brown-McPhee friction"],
            ["FullVA emergence", "v023-v029", "absolute-coordinate revolute failures reveal endpoint velocity/acceleration consistency"],
            ["Solver scaling", "v030-v045", "dense Jacobians hit a cost wall; sparse/coloring/pattern audits become necessary"],
            ["Claim gates", "v046-v048", "ASME examples, proof ledgers, paper package, and external same-test scaffolds"],
        ],
        [2_150_000, 1_650_000, 6_715_600],
    ))

    slides.append(evolution_timeline_slide())

    slides.append(evolution_phase_slide(
        "Phase 1 - Make Lie-group order real",
        "v001-v005",
        "Before touching DAEs, the agent had to verify that the basic SO(3) and smooth mechanics integrators had the claimed order.",
        ["v001 builds the benchmark harness.",
         "v002 fixes right-action CF4/RKMK4 ordering.",
         "v004 tests Yoshida midpoint.",
         "v005 makes Gauss-Lie4 the smooth mechanics candidate."],
        ["Start with problems where the answer is hard to fake.",
         "Verifier: log-map errors, invariant drift, known order slopes.",
         "Do not add constraints until chart/order bugs are gone."]
    ))

    slides.append(evolution_phase_slide(
        "Phase 2 - Constraints expose endpoint inconsistency",
        "v006-v013",
        "A high-order rotation update is not enough for an index-3 multibody DAE; endpoint position, velocity, and acceleration can disagree.",
        ["v006 uses reduced fixed-pivot reconstruction.",
         "v007-v008 internalize absolute-coordinate endpoint constraints.",
         "v010 switches to JAX AD Jacobians.",
         "v011-v013 bind quaternion transport and Gauss6 endpoint collocation."],
        ["Every new DAE row needs a closure verifier.",
         "Endpoint projection must be audited separately.",
         "AD backend changes preserve order only if the residual is identical."]
    ))

    slides.append(evolution_phase_slide(
        "Phase 3 - Friction creates a smoothness boundary",
        "v014-v022",
        "The same high-order method behaves differently when regularized friction becomes sharp; the asymptotic regime can move out of the tested h range.",
        ["v014 sweeps friction smoothness.",
         "v015 and v020 add adaptive Gauss6/Gauss4 controllers.",
         "v019-v021 make friction multiplier-dependent.",
         "v022 builds a paper-like revolute Brown-McPhee benchmark."],
        ["The verifier must separate formal smooth order from practical coarse order.",
         "Record cost to recover high order.",
         "Do not let a sharp-friction failure invalidate a smooth theorem."]
    ))

    slides.append(evolution_phase_slide(
        "Phase 4 - FullVA emerges from failed absolute DAE repairs",
        "v023-v029",
        "Direct absolute-coordinate revolute solves exposed endpoint velocity drift and rank/consistency problems that position-only rows could not fix.",
        ["v023 tests full absolute revolute DAE.",
         "v024 rules out simple Lobatto node swap.",
         "v025 shows projection helps constraints but changes accuracy.",
         "v026-v028 add stage velocity and acceleration consistency.",
         "v029 generalizes PivotVA/FullVA to a two-body chain."],
        ["FullVA is not an aesthetic choice.",
         "It is the response to a measured endpoint-consistency blocker.",
         "The agent should evolve the method only after a verifier localizes the failure."]
    ))

    slides.append(evolution_phase_slide(
        "Phase 5 - Solver scaling becomes its own research problem",
        "v030-v045",
        "Once the residual works, dense Jacobian assembly and dense linear solves become the limiting factor for larger chains.",
        ["v030 measures Jacobian sparsity.",
         "v031 integrates CSR sparse Newton.",
         "v032 rules out unpreconditioned JVP-GMRES.",
         "v034-v038 develop colored JVP and cache reuse.",
         "v039-v045 scale to triple/prismatic chains and row-colored VJP."],
        ["A correct method is not automatically a usable method.",
         "Verifier: exact pattern, color count, dense agreement, wall-clock repeat.",
         "Sparse correctness and sparse speed are separate claims."]
    ))

    slides.append(evolution_phase_slide(
        "Phase 6 - Claim gates replace informal success",
        "v046-v048",
        "A good local method is still not a paper claim; the agent needs ASME examples, proof ledgers, and external comparison policy.",
        ["v046 ingests the four ASME public examples as a baseline.",
         "v047 builds the cylindrical-chain method/paper/proof pipeline.",
         "v048 creates the cross-paper same-test scaffold and public baseline rows.",
         "Submission gates keep source-policy superiority false."],
        ["The final verifier is a claim verifier.",
         "Accepted, diagnostic, open, forbidden are different states.",
         "External comparison requires same parameters, references, metrics, and work policy."]
    ))

    slides.append(bullets_slide(
        "Why this evolution matters for agent design",
        ["The agent's workflow is learned from the research sequence: every phase adds a verifier that the previous phase needed.",
         "Method evolution is not free-form generation; it is blocker-driven search.",
         "A version is complete only when proof status, numerical examples, plots, CSV/JSON reports, and ledgers agree.",
         "The user can inspect why the project moved, not just where it ended."]
    ))

    slides.append(section_slide("2 / Method Object", "Define the integrator before searching", "The agent cannot verify a method whose identity is not explicit."))

    slides.append(bullets_slide(
        "A candidate integrator is a structured object",
        ["State space: Euclidean variables plus Lie-group coordinates.",
         "Stage unknowns: positions, rotations, velocities, accelerations, multipliers.",
         "Residual: the square nonlinear equations solved by Newton.",
         "Endpoint map: how stage values become the next state.",
         "Solver policy: Jacobian, tolerance, initialization, fallback rules."]
    ))

    slides.append(table_slide(
        "MethodSpec for lower-pair multibody integrators",
        ["Field", "Question", "Verifier hook"],
        [
            ["chart", "Which local Lie coordinates define rotation increments?", "SO(3) retraction and log checks"],
            ["residual rows", "Which equations define the one-step map?", "row count, row order, AD binding"],
            ["constraint levels", "Are Phi, Phi_q v, Phi_q a all enforced?", "FullVA residual checks"],
            ["endpoint policy", "Is closure solved or projected?", "raw vs projected endpoint audit"],
            ["solver policy", "What tolerance is theorem-level?", "eta_h <= c h^7 gate"],
        ],
        [2_050_000, 4_050_000, 4_415_600],
    ))

    slides.append(number_cards_slide(
        "For v047, the accepted method object is concrete",
        [("3", "Gauss stages", RED),
         ("132", "FullVA residual rows", BLUE),
         ("6", "conditional method order", GREEN),
         ("4", "ASME mechanisms covered", ORANGE)],
        "The agent is not free to replace this with a paper-TFE residual unless that replacement passes its own gate."
    ))

    slides.append(figure_slide(
        "Method architecture as a verifier target",
        "method_stage_architecture.png",
        "The method stage architecture figure is not only explanatory; it tells the agent which objects must stay synchronized.",
        ["Accepted residual.",
         "Proof boundary.",
         "Validator and artifact layer."]
    ))

    slides.append(section_slide("3 / Verifier Sandbox", "Constrain what the agent can run", "Most research mistakes are caused by running the wrong test or promoting the wrong output."))

    slides.append(sandbox_stack_slide())

    slides.append(process_slide(
        "Four sandbox levels",
        [("0", "Read-only", "parse ledgers, summaries, validators; no numerical regeneration"),
         ("1", "Target audit", "one bounded hypothesis via V047_TARGET_AUDIT or a specific validator"),
         ("2", "Generator", "regenerate version artifacts after method-code changes"),
         ("3", "External", "source-policy campaigns, strict public h, human opt-in required")]
    ))

    slides.append(table_slide(
        "Sandbox contract",
        ["Sandbox", "Allowed", "Forbidden by default"],
        [
            ["read-only", "validate paper/package/current gates", "changing results or running full campaigns"],
            ["target audit", "JSON-only local probe or short h-sweep", "claim promotion or ledger status change"],
            ["full generator", "version-wide artifact regeneration", "using stale ledgers after code changes"],
            ["external policy", "published benchmark reproduction", "running strict 1e-4 without opt-in"],
        ],
        [2_150_000, 4_400_000, 3_965_600],
    ))

    slides.append(bullets_slide(
        "The verifier sandbox needs deterministic inputs",
        ["Pinned problem definitions: masses, inertias, joints, drivers, friction parameters.",
         "Pinned step-size policy: at least three h values plus a reference policy.",
         "Pinned metrics: position, velocity, acceleration, constraints, residuals, runtime, Newton counts.",
         "Pinned claim role: accepted order, mechanism coverage, diagnostic, or external-policy row."]
    ))

    slides.append(bullets_slide(
        "Why read-only validators matter",
        ["They answer: does the current claim still match the artifacts?",
         "They prevent expensive reruns for paper-edit questions.",
         "They detect stale text, missing plots, malformed CSV/JSON, and illegal claim wording.",
         "They let the agent resume after context loss by rereading the artifact contract."]
    ))

    slides.append(figure_slide(
        "Endpoint closure sandbox",
        "endpoint_kkt_closure.png",
        "Endpoint closure is split into raw residual, projection baseline, and KKT closure evidence.",
        ["A projection can make constraints look good while changing the map.",
         "The sandbox records raw closure and corrected closure separately.",
         "The agent cannot hide projection inside an order claim."]
    ))

    slides.append(section_slide("4 / Proof Sandbox", "Separate theorem inputs from diagnostics", "The proof gate is what keeps the agent from mistaking numerics for mathematics."))

    slides.append(proof_flow_slide())

    slides.append(table_slide(
        "Proof obligations for the integrator agent",
        ["ID", "Obligation", "Why it exists"],
        [
            ["P1", "smooth reduced chart and FullVA lift", "Gauss order must transfer through the constrained coordinates"],
            ["P2", "regular stage Jacobian / compact branch", "Newton must define a local one-step map"],
            ["P3", "implemented residual defect O(h^7)", "the actual rows must match the formal method"],
            ["P4", "endpoint closure perturbation O(h^7)", "endpoint repair must not lower order"],
            ["P5", "Newton-Euler dynamic rows discharged", "dynamics rows cannot be hand-waved"],
            ["P6", "solver residual eta_h <= c h^7", "fixed tolerance logs are not theorem evidence"],
            ["P7", "residual-to-error theorem for surrogates", "mechanism residuals are not automatically order rows"],
        ],
        [950_000, 4_250_000, 5_315_600],
    ))

    slides.append(two_col_slide(
        "The proof sandbox has lanes",
        "Accepted lane",
        ["Direct residual-bridge route.",
         "AD-expanded row identity checks.",
         "Newton-Euler direct substitution.",
         "Conditional theorem under compact-branch assumptions."],
        "Diagnostic lane",
        ["Primitive Taylor subterm budget.",
         "Residual-only closed-loop rows.",
         "Fixed production tolerances.",
         "External source-policy rows."]
    ))

    slides.append(bullets_slide(
        "The proof ledger tells the agent what not to say",
        ["Observed 7.161/7.066 slopes do not create a seventh-order theorem.",
         "A validator PASS is necessary but not sufficient for submission readiness.",
         "A residual row is not a dynamic-order row without a residual-to-error theorem.",
         "A local paper-style TFE formula map is not full source-paper residual reproduction."]
    ))

    slides.append(figure_slide(
        "Claim boundary is part of the proof interface",
        "claim_boundary_limitations.png",
        "The agent presents accepted evidence, bounded diagnostics, and open gates in the same visual frame.",
        ["Accepted method claim.",
         "Diagnostic evidence.",
         "Open source-policy and full-TFE gates."]
    ))

    slides.append(section_slide("5 / Numerical Ladder", "Examples should expose specific failure modes", "The agent should not jump from one toy plot to a paper claim."))

    slides.append(numerical_ladder_visual_slide())

    slides.append(process_slide(
        "Integrator test ladder",
        [("1", "Kinematics", "SO(3) prescribed rotations, chart consistency, CF/RKMK sanity"),
         ("2", "Smooth mechanics", "Euler top, invariant drift, Gauss order"),
         ("3", "Constrained DAE", "fixed pivot, endpoint position/velocity/acceleration"),
         ("4", "Friction", "regularization width, pre-asymptotic regimes"),
         ("5", "Mechanisms", "single, double, four-link, slider-crank"),
         ("6", "External", "same-test public baselines and source-policy rows")]
    ))

    slides.append(table_slide(
        "What each numerical example should test",
        ["Example", "Failure mode exposed", "Acceptance evidence"],
        [
            ["SO(3) kinematics", "wrong right/left action or chart derivative", "known order and log error"],
            ["Euler top", "energy/momentum drift", "order plus invariant diagnostics"],
            ["fixed pivot DAE", "constraint drift hidden by position accuracy", "Phi, Phi_q v, Phi_q a closure"],
            ["sharp friction", "delayed asymptotic regime", "smoothness sweep and cost envelope"],
            ["ASME mechanisms", "lower-pair row coverage", "four-example gate and reaction rows"],
            ["external baselines", "unfair reference policy", "same h, same reference, same metrics"],
        ],
        [2_050_000, 4_000_000, 4_465_600],
    ))

    slides.append(figure_slide(
        "Convergence verifier",
        "convergence.png",
        "Every accepted order row needs at least three step sizes, a reference policy, and the matching CSV/JSON/plot trail.",
        ["Report observed order.",
         "Report finest error.",
         "Record if the slope is floor-limited."]
    ))

    slides.append(figure_slide(
        "Four-example mechanism verifier",
        "asme_lower_pair_graph_bridge.png",
        "The ASME examples force the agent to cover CD, DP1, DP2, and D lower-pair constraints.",
        ["Single pendulum.",
         "Double pendulum.",
         "Four-link.",
         "Slider-crank."]
    ))

    slides.append(two_col_slide(
        "Dynamic-order rows versus coverage rows",
        "Accepted dynamic order",
        ["Single pendulum: driven absolute FullVA residual.",
         "Double pendulum: local FullVA reference policy.",
         "Used to support method-side order."],
        "Mechanism coverage",
        ["Four-link and slider-crank closed-loop FullVA.",
         "Reaction dynamics residuals checked.",
         "Not external dynamic-order rows unless a stronger theorem/campaign closes."]
    ))

    slides.append(figure_slide(
        "Friction verifier",
        "friction_smoothness_sweep.png",
        "The agent treats sharp friction as a smoothness and cost boundary, not as a contradiction of the smooth theorem.",
        ["Smooth regularization should recover high order.",
         "Sharp coarse regimes can be pre-asymptotic.",
         "Cost to recover order must be recorded."]
    ))

    slides.append(figure_slide(
        "Sparse backend verifier",
        "sparse_speed_gap.png",
        "Sparse structure correctness and runtime superiority are separate gates.",
        ["Exact sparse pattern is evidence.",
         "Dense jacfwd can still be faster.",
         "The claim remains an engineering caveat until wall-clock wins."]
    ))

    slides.append(section_slide("6 / Search Strategy", "How the agent chooses the next experiment", "The best next step is the one that closes a specific gate or rules out a real hypothesis."))

    slides.append(bullets_slide(
        "Candidate generation is gap-driven",
        ["Read the current open gate, not just the latest plot.",
         "Localize the missing residual direction, rank defect, or reference-policy blocker.",
         "Generate one bounded hypothesis that targets that gap.",
         "Run the smallest sandbox that can falsify it.",
         "Record negative evidence with enough detail to prevent repetition."]
    ))

    slides.append(table_slide(
        "What a negative result must record",
        ["Field", "Purpose", "Example"],
        [
            ["residual", "how close the candidate got", "projection residual 0.576548"],
            ["rank/span", "whether the missing directions are covered", "rank 8 / no span"],
            ["dominant family", "where the miss lives", "stage-2 angular_velocity_w"],
            ["runtime", "whether more scans are affordable", "51.2 seconds / 20 rows"],
            ["claim effect", "whether any gate changes", "full_tfe_stage_replacement=false"],
        ],
        [1_900_000, 3_350_000, 5_265_600],
    ))

    slides.append(figure_slide(
        "Full-TFE replacement search as an example",
        "order_closure_blend.png",
        "The agent keeps terminal closure, source-freedom, and smooth order as separate acceptance properties.",
        ["Terminal-closed candidates can lose order.",
         "Order-preserving candidates can miss terminal closure.",
         "No current candidate has the required intersection."]
    ))

    slides.append(figure_slide(
        "Velocity-compression probes prune the search space",
        "velocity_compression.png",
        "Many plausible lower-pair closure rows are ruled out because they do not span the missing directions.",
        ["Record span, rank, residual.",
         "Do not rerun equivalent terminal-limit rows.",
         "Move toward a revised analytical weak-row formula."]
    ))

    slides.append(section_slide("7 / Case Study", "v047/v048 pipeline", "The framework is not hypothetical; it is encoded in the current autoresearch tree."))

    slides.append(number_cards_slide(
        "Current realized pipeline",
        [("v047", "method, proof, ASME, full-TFE diagnostics", RED),
         ("v048", "external same-test scaffold", BLUE),
         ("B1-B8", "narrowed claim blockers closed", GREEN),
         ("OC4/6/12", "global submission blockers open", ORANGE)],
        "The agent can keep a narrowed method claim alive while refusing broader source-policy claims."
    ))

    slides.append(figure_slide(
        "Closed-loop dynamics progressed by staged sandboxes",
        "closed_loop_true_dynamic_order.png",
        "The closed-loop work moved from interface audit to residual scaffold to one-step smoke to coarse dynamic candidates.",
        ["This is the intended pattern.",
         "No single run jumps straight to superiority.",
         "Each sandbox unlocks the next one."]
    ))

    slides.append(figure_slide(
        "External comparison remains bounded",
        "strict_common_reference_work_precision.png",
        "Common-reference work/precision evidence is useful, but source-policy external superiority remains false.",
        ["Same-window rows are visible.",
         "Source-policy rows are not promoted.",
         "Strict public campaigns remain opt-in."]
    ))

    slides.append(claim_state_machine_slide())

    slides.append(table_slide(
        "The agent's final decision vocabulary",
        ["Verdict", "Meaning", "Action"],
        [
            ["accepted", "gate criteria are met and validators agree", "update claim ledger"],
            ["diagnostic", "useful evidence but not enough for claim", "record and keep boundary"],
            ["blocked", "same missing condition persists after bounded attempts", "ask human or change hypothesis"],
            ["opt-in", "expensive or policy-sensitive execution", "request explicit approval"],
            ["forbidden", "claim conflicts with gate state", "remove wording or demote claim"],
        ],
        [1_900_000, 4_000_000, 4_615_600],
    ))

    slides.append(statement_slide(
        "Conclusion",
        ["For integrator research, the agent is useful only when", "it can verify method identity, proof status, and numerical scope."],
        ["The sandbox limits what can be run.",
         "The proof ledger limits what can be claimed.",
         "The numerical ladder exposes DAE, Lie-group, friction, and external-policy failure modes.",
         "The v047/v048 tree is a working instance of this architecture."]
    ))

    slides.append(bullets_slide(
        "Open engineering improvements",
        ["A small DSL for MethodSpec, ProblemSpec, ClaimSpec, and EvidenceSpec.",
         "Automatic generation of validators from claim-gate schemas.",
         "A scheduler that chooses the cheapest sandbox capable of falsifying a hypothesis.",
         "Parallel subagent reviews for proof, numerical policy, and paper package boundaries."]
    ))

    slides.append(section_slide("8 / References", "What this agent is grounded in", "The methodology is tied to the integrator, DAE, TFE, friction/contact, and SBEL benchmark literature, plus the local v047/v048 evidence artifacts."))

    slides.append(references_slide(
        "References: integrator and DAE foundations",
        [
            ("DAE basics", [
                "Hairer and Wanner (1996). Solving Ordinary Differential Equations II: Stiff and Differential-Algebraic Problems.",
                "Gear, Leimkuhler, and Gupta (1985). Automatic integration of Euler-Lagrange equations with constraints. doi:10.1016/0377-0427(85)90008-1.",
            ]),
            ("Lie RK", [
                "Munthe-Kaas (1998). Runge-Kutta methods on Lie groups. BIT Numerical Mathematics.",
                "Munthe-Kaas (1999). High order Runge-Kutta methods on manifolds. Applied Numerical Mathematics.",
            ]),
            ("constrained Lie", [
                "Bruls, Cardona, and Arnold (2012). Lie group generalized-alpha time integration of constrained flexible multibody systems. doi:10.1016/j.mechmachtheory.2011.07.017.",
                "Wieloch and Arnold (2021). BDF integrators for constrained mechanical systems on Lie groups. doi:10.1016/j.cam.2019.112517.",
            ]),
            ("quaternions", [
                "Terze, Mueller, and Zlatar (2016). Singularity-free time integration of rotational quaternions. doi:10.1007/s11044-016-9518-7.",
                "Terze, Zlatar, and Pandza (2020). Aircraft attitude reconstruction via novel quaternion-integration procedure.",
            ]),
            ("variational", [
                "Jay (1996). Symplectic partitioned Runge-Kutta methods for constrained Hamiltonian systems. doi:10.1137/0733019.",
                "Marsden and West (2001); Leyendecker, Marsden, and Ortiz (2008); Leok and Shingel (2012).",
            ]),
        ],
    ))

    slides.append(references_slide(
        "References: TFE, friction, and contact context",
        [
            ("source TFE", [
                "Chaturvedi, Sandu, and Sandu (2026). Higher-order integration of index-3 DAE with friction using time finite elements on Lie groups.",
                "Multibody System Dynamics. doi:10.1007/s11044-026-10153-w.",
            ]),
            ("higher order", [
                "Kim and Reddy (2017). A new family of higher-order time integration algorithms for the analysis of structural dynamics.",
                "Journal of Applied Mechanics. doi:10.1115/1.4036821.",
            ]),
            ("time FEM", [
                "Borri and Atluri (1988). Time-finite element method for the constrained dynamics of a rigid body.",
                "Hughes and Hulbert (1988); Hulbert (1992); Jog, Agrawal, and Nandy (2016); Bauchau (2024).",
            ]),
            ("friction", [
                "Brown and McPhee (2016). A continuous velocity-based friction model for dynamics and control with physically meaningful parameters.",
                "Journal of Computational and Nonlinear Dynamics. doi:10.1115/1.4033658.",
            ]),
            ("contact", [
                "Stewart and Trinkle (1996). Implicit time-stepping for rigid body dynamics with inelastic collisions and Coulomb friction.",
                "Anitescu and Potra (1997); Tasora and Anitescu (2011).",
            ]),
        ],
    ))

    slides.append(references_slide(
        "References: SBEL / Negrut baseline family",
        [
            ("exp map", [
                "Taves, Kissel, and Negrut (2020). On an exponential map approach for rigid body kinematics and dynamics analysis.",
                "Technical Report TR-2020-08, Simulation-Based Engineering Laboratory, UW-Madison.",
            ]),
            ("SO(3) DAE", [
                "Kissel, Negrut, and Taves (2021). Dwelling on the connection between SO(3) and rotation matrices in rigid multibody dynamics.",
                "ASME IDETC-CIE2021. doi:10.1115/DETC2021-72057.",
            ]),
            ("absolute", [
                "Kissel, Negrut, and Taves (2022). Constrained multibody kinematics and dynamics in absolute coordinates.",
                "Journal of Computational and Nonlinear Dynamics. doi:10.1115/1.4055140.",
            ]),
            ("half implicit", [
                "Fang, Kissel, Zhang, and Negrut (2023). On the use of half-implicit numerical integration in multibody dynamics.",
                "Journal of Computational and Nonlinear Dynamics. doi:10.1115/1.4056183.",
            ]),
            ("VP Lie", [
                "Kissel, Bakke, and Negrut (2024). Reducing constrained MBD to ODE solution via velocity partitioning and Lie group integration.",
                "Journal of Computational and Nonlinear Dynamics. doi:10.1115/1.4065254.",
            ]),
        ],
    ))

    slides.append(references_slide(
        "Project artifacts used as references",
        [
            ("bibliography", [
                "paper_v047_cylindrical_chain/main_cmame.tex, thebibliography block.",
                "paper_v047_cylindrical_chain/REFERENCE_METADATA_AUDIT.md and .json: 28 references, 16/16 DOI rows verified, 12/12 local non-DOI rows verified.",
            ]),
            ("pipeline", [
                "CURRENT_PIPELINE_CONTRACT.md; VALIDATION_QUICKSTART.md; VERSION_LEDGER.md; VERSION_TREE.md; version_ledger.csv.",
                "Used to preserve v001-v048 blocker-driven evolution and current claim status.",
            ]),
            ("proof", [
                "ORDER_PROOF_LEDGER.md; paper_v047_cylindrical_chain/CURRENT_STATUS_CN.md; proof closure and claim traceability validator artifacts.",
                "Used to separate accepted, conditional, diagnostic, open, and forbidden claim lanes.",
            ]),
            ("numerics", [
                "v047_cylindrical_chain_pipeline/results/summary_v047.json plus CSV/PNG/report artifacts.",
                "Used for smooth convergence, ASME examples, endpoint closure, sparse backend, and source-policy boundary slides.",
            ]),
            ("v048", [
                "v048_cross_paper_same_test_benchmarks scaffolds and same-test campaign status.",
                "Used only as bounded external comparison infrastructure; external_superiority_claim remains false.",
            ]),
        ],
    ))

    thanks = Slide("", kind="title", show_footer=False)
    thanks.texts.extend([
        TextBox(["Thank You"], 760_000, 1_560_000, 10_500_000, 850_000, 44, DARK, True, align="ctr", name="Thanks"),
        TextBox(["Questions?"], 760_000, 2_740_000, 10_500_000, 760_000, 32, RED, True, align="ctr", name="Questions"),
        TextBox(["Key idea: integrator agents need verifier sandboxes before they need more autonomy."],
                1_050_000, 4_360_000, 10_000_000, 500_000, 18, MUTED, align="ctr", name="Closing note"),
    ])
    slides.append(thanks)

    return slides


def add_image_panel(s: Slide, fig_name: str, x: int, y: int, w: int, h: int, caption: str = "") -> None:
    path = FIG / fig_name
    caption_h = 230_000 if caption else 0
    s.rects.append(Rect(x, y, w, h, WHITE, MID, "Image panel"))
    ix, iy, iw, ih = fit_rect(path, x + 70_000, y + 70_000, w - 140_000, h - 140_000 - caption_h)
    s.images.append(ImageRef(path, ix, iy, iw, ih, fig_name))
    if caption:
        s.texts.append(TextBox([caption], x + 110_000, y + h - 200_000, w - 220_000, 145_000, 8, MUTED, align="ctr", name="Image caption"))


def compact_title_slide() -> Slide:
    s = Slide("", kind="title", show_footer=False)
    s.texts.extend([
        TextBox(["Building an Auto-Research Agent", "for Integrator Research"], 720_000, 850_000, 5_500_000, 1_300_000, 34, DARK, True, name="Title"),
        TextBox(["Verifier sandboxes, proof gates, and numerical test ladders for Lie-group multibody DAE methods"], 760_000, 2_520_000, 5_550_000, 680_000, 16, MUTED, name="Subtitle"),
        TextBox(["Jingquan Wang", "Simulation-Based Engineering Laboratory", "University of Wisconsin - Madison"], 760_000, 4_060_000, 5_400_000, 720_000, 16, MUTED, name="Author"),
        TextBox([DATE_TEXT], 760_000, 5_300_000, 2_800_000, 300_000, 13, RED, True, name="Date"),
    ])
    add_image_panel(s, "method_stage_architecture.png", 6_600_000, 760_000, 4_900_000, 1_520_000, "method object")
    add_image_panel(s, "convergence.png", 6_600_000, 2_520_000, 2_330_000, 1_760_000, "order verifier")
    add_image_panel(s, "asme_lower_pair_graph_bridge.png", 9_160_000, 2_520_000, 2_340_000, 1_760_000, "mechanism gate")
    add_image_panel(s, "claim_boundary_limitations.png", 6_600_000, 4_520_000, 4_900_000, 1_040_000, "claim boundary")
    return s


def compact_lab_problem_slide() -> Slide:
    s = Slide(title="Why this matters in our lab")
    s.texts.append(TextBox(["Many people are attacking the same hard object:"], MARGIN_X, 1_360_000, 10_515_600, 360_000, 21, DARK, True, align="ctr", name="Lead"))
    cx, cy = MARGIN_X + 3_760_000, 2_560_000
    s.rects.append(Rect(cx, cy, 3_000_000, 1_050_000, "FFF1F1", RED, "Center"))
    s.texts.append(TextBox(["defensible multibody", "time integration"], cx + 210_000, cy + 230_000, 2_580_000, 530_000, 20, DARK, True, align="ctr", name="Center"))
    nodes = [
        (MARGIN_X, 1_900_000, "Lie groups", "SO(3), SE(3), charts", BLUE),
        (MARGIN_X + 7_500_000, 1_900_000, "DAE mechanisms", "joints, drivers, reactions", GREEN),
        (MARGIN_X, 4_060_000, "friction/contact", "smooth vs nonsmooth tests", ORANGE),
        (MARGIN_X + 3_760_000, 4_480_000, "sparse solvers", "AD, coloring, Newton", "7A4EA3"),
        (MARGIN_X + 7_500_000, 4_060_000, "papers", "benchmarks, claims, refs", RED),
    ]
    for x, y, head, body, color in nodes:
        s.rects.append(Rect(x, y, 2_800_000, 880_000, LIGHT, MID, "Lab node"))
        s.rects.append(Rect(x, y, 2_800_000, 70_000, color, None, "Lab node accent"))
        s.texts.append(TextBox([head], x + 140_000, y + 220_000, 2_520_000, 240_000, 16, DARK, True, align="ctr", name="Lab head"))
        s.texts.append(TextBox([body], x + 140_000, y + 530_000, 2_520_000, 180_000, 10, MUTED, align="ctr", name="Lab body"))
    s.texts.append(TextBox(["Agent purpose: keep method identity, examples, proof status, and paper claims synchronized across this shared evidence space."],
                           MARGIN_X, 5_720_000, 10_515_600, 260_000, 14, DARK, True, align="ctr", name="Takeaway"))
    return s


def compact_reference_landscape_slide() -> Slide:
    return table_slide(
        "Reference landscape drives the verifier design",
        ["stream", "references", "agent obligation"],
        [
            ["index-3 DAE", "Hairer-Wanner; Gear-Leimkuhler-Gupta", "check Phi, Phi_q v, Phi_q a, multipliers"],
            ["Lie-group time integration", "Munthe-Kaas; Bruls-Cardona-Arnold; Wieloch-Arnold", "preserve rotation geometry and method identity"],
            ["time finite elements", "Borri-Atluri; Hughes-Hulbert; Chaturvedi-Sandu-Sandu", "separate source residual reproduction from local method claims"],
            ["SBEL baselines", "Taves-Kissel-Negrut; Kissel-Negrut-Taves; Fang et al.", "make external rows comparable under explicit policy"],
            ["friction/contact", "Brown-McPhee; Stewart-Trinkle; Anitescu-Potra", "separate smooth order from nonsmooth diagnostics"],
        ],
        [1_750_000, 4_750_000, 4_015_600],
    )


def compact_evolution_slide() -> Slide:
    s = Slide(title="Why v001 had to become v048")
    phases = [
        ("v001-005", "SO(3) order", RED),
        ("v006-013", "DAE closure", BLUE),
        ("v014-022", "friction", GREEN),
        ("v023-029", "FullVA", ORANGE),
        ("v030-045", "sparse scaling", "7A4EA3"),
        ("v046-048", "claim gates", DARK),
    ]
    x0, y = MARGIN_X, 1_520_000
    w, gap = 1_500_000, 115_000
    for i, (vr, head, color) in enumerate(phases):
        x = x0 + i * (w + gap)
        s.rects.append(Rect(x, y, w, 1_150_000, LIGHT, MID, "Evolution phase"))
        s.rects.append(Rect(x, y, w, 80_000, color, None, "Evolution accent"))
        s.texts.append(TextBox([vr], x + 70_000, y + 210_000, w - 140_000, 230_000, 11, color, True, align="ctr", name="Version"))
        s.texts.append(TextBox([head], x + 70_000, y + 575_000, w - 140_000, 300_000, 14, DARK, True, align="ctr", name="Phase"))
        if i < len(phases) - 1:
            s.texts.append(TextBox([">"], x + w + 20_000, y + 430_000, 75_000, 170_000, 14, color, True, align="ctr", name="Arrow"))
    add_image_panel(s, "all_method_result_matrix.png", MARGIN_X, 3_040_000, 4_950_000, 2_430_000, "evidence matrix")
    s.rects.append(Rect(MARGIN_X + 5_260_000, 3_040_000, 5_255_600, 2_430_000, "FFF7E8", ORANGE, "Evolution takeaway"))
    s.texts.append(TextBox(["Evolution rule"], MARGIN_X + 5_520_000, 3_250_000, 4_730_000, 300_000, 19, DARK, True, name="Rule head"))
    s.texts.append(TextBox([
        "Each version exists because the previous verifier found a missing gate.",
        "The agent is not a generic code loop; it is a blocker-driven research controller.",
        "v048 is the point where external same-test policy becomes a first-class object."
    ], MARGIN_X + 5_520_000, 3_720_000, 4_730_000, 1_170_000, 15, DARK, name="Rule body"))
    return s


def compact_agent_architecture_slide() -> Slide:
    s = Slide(title="The agent we need")
    cols = [
        ("MethodSpec", "what one-step map is being claimed", RED),
        ("ProblemSpec", "which mechanisms and parameters are pinned", BLUE),
        ("EvidenceSpec", "CSV, JSON, plots, validators", GREEN),
        ("ClaimSpec", "accepted, diagnostic, open, forbidden", ORANGE),
    ]
    x0, y = MARGIN_X, 1_610_000
    w, gap = 2_430_000, 210_000
    for i, (head, body, color) in enumerate(cols):
        x = x0 + i * (w + gap)
        s.rects.append(Rect(x, y, w, 1_360_000, LIGHT, MID, "Architecture card"))
        s.rects.append(Rect(x, y, w, 80_000, color, None, "Architecture accent"))
        s.texts.append(TextBox([head], x + 130_000, y + 270_000, w - 260_000, 300_000, 17, DARK, True, align="ctr", name="Arch head"))
        s.texts.append(TextBox([body], x + 130_000, y + 750_000, w - 260_000, 310_000, 11, MUTED, align="ctr", name="Arch body"))
    s.texts.append(TextBox(["closed loop"], MARGIN_X, 3_470_000, 10_515_600, 300_000, 19, RED, True, align="ctr", name="Loop label"))
    steps = [("generate", RED), ("sandbox", BLUE), ("prove", GREEN), ("test", ORANGE), ("write", DARK)]
    x0, y = MARGIN_X + 950_000, 4_000_000
    for i, (head, color) in enumerate(steps):
        x = x0 + i * 1_820_000
        s.texts.append(TextBox([head], x, y, 1_200_000, 400_000, 15, WHITE, True, align="ctr", valign="m", fill=color, name="Loop step"))
        if i < len(steps) - 1:
            s.texts.append(TextBox([">"], x + 1_280_000, y + 90_000, 160_000, 170_000, 16, color, True, align="ctr", name="Loop arrow"))
    s.texts.append(TextBox(["Human role: choose the research direction; agent role: enforce the gates before claims move."],
                           MARGIN_X, 5_260_000, 10_515_600, 360_000, 15, DARK, True, align="ctr", name="Arch note"))
    return s


def compact_method_slide() -> Slide:
    s = Slide(title="Method object: the agent cannot verify a moving target")
    s.rects.append(Rect(MARGIN_X, 1_520_000, 3_230_000, 4_360_000, LIGHT, MID, "Method notes"))
    s.texts.append(TextBox(["For v047"], MARGIN_X + 190_000, 1_790_000, 2_850_000, 280_000, 20, RED, True, name="For v047"))
    s.texts.append(TextBox([
        "3 Gauss stages",
        "132 FullVA rows",
        "position, velocity, acceleration constraints",
        "endpoint closure audited separately",
        "solver tolerance is a theorem gate"
    ], MARGIN_X + 250_000, 2_260_000, 2_720_000, 2_050_000, 15, DARK, name="Method bullets"))
    s.texts.append(TextBox(["Non-claim: full source-paper TFE replacement unless its own residual gate closes."],
                           MARGIN_X + 250_000, 4_980_000, 2_720_000, 450_000, 12, ORANGE, True, name="Non claim"))
    add_image_panel(s, "method_stage_architecture.png", MARGIN_X + 3_560_000, 1_520_000, 6_955_600, 4_360_000, "method architecture as verifier target")
    return s


def compact_sandbox_slide() -> Slide:
    s = Slide(title="Verifier sandbox: constrain what the agent can run")
    layers = [
        ("L0", "read-only validators", "paper/package/proof checks", GREEN),
        ("L1", "target audit", "one bounded hypothesis", BLUE),
        ("L2", "full generator", "version-wide artifacts", ORANGE),
        ("L3", "external source-policy", "same-test public campaigns, opt-in", RED),
    ]
    y0 = 1_560_000
    for i, (lvl, head, desc, color) in enumerate(layers):
        x = MARGIN_X + i * 420_000
        y = y0 + i * 780_000
        w = 10_515_600 - i * 840_000
        s.rects.append(Rect(x, y, w, 620_000, LIGHT, MID, "Sandbox layer"))
        s.rects.append(Rect(x, y, 100_000, 620_000, color, None, "Layer accent"))
        s.texts.append(TextBox([lvl], x + 210_000, y + 100_000, 620_000, 210_000, 13, color, True, name="Level"))
        s.texts.append(TextBox([head], x + 980_000, y + 85_000, 2_900_000, 230_000, 17, DARK, True, name="Layer head"))
        s.texts.append(TextBox([desc], x + 980_000, y + 360_000, w - 1_200_000, 170_000, 11, MUTED, name="Layer desc"))
    s.rects.append(Rect(MARGIN_X, 5_020_000, 10_515_600, 620_000, "FFF1F1", RED, "Sandbox warning"))
    s.texts.append(TextBox(["Promotion rule: outputs move upward only when the lower sandbox cannot answer the claim question."],
                           MARGIN_X + 200_000, 5_195_000, 10_115_600, 240_000, 16, DARK, True, align="ctr", name="Sandbox rule"))
    return s


def compact_proof_slide() -> Slide:
    s = Slide(title="Proof sandbox: only gated facts enter the theorem")
    boxes = [
        ("P1", "smooth chart", RED),
        ("P2", "regular branch", BLUE),
        ("P3", "residual defect O(h^7)", GREEN),
        ("P4", "endpoint perturbation O(h^7)", ORANGE),
        ("P5", "dynamic rows", "7A4EA3"),
        ("P6", "solver scale", DARK),
        ("P7", "residual-to-error", RED),
    ]
    x0, y = MARGIN_X, 1_520_000
    w, gap = 1_360_000, 150_000
    for i, (pid, head, color) in enumerate(boxes):
        x = x0 + i * (w + gap)
        s.rects.append(Rect(x, y, w, 1_080_000, LIGHT, MID, "Proof obligation"))
        s.rects.append(Rect(x, y, w, 75_000, color, None, "Proof accent"))
        s.texts.append(TextBox([pid], x + 110_000, y + 210_000, w - 220_000, 230_000, 15, color, True, align="ctr", name="PID"))
        s.texts.append(TextBox([head], x + 100_000, y + 565_000, w - 200_000, 300_000, 10, DARK, True, align="ctr", name="Proof head"))
    s.rects.append(Rect(MARGIN_X, 3_260_000, 4_980_000, 1_560_000, "EAF4EA", GREEN, "Accepted lane"))
    s.rects.append(Rect(MARGIN_X + 5_535_600, 3_260_000, 4_980_000, 1_560_000, "FFF7E8", ORANGE, "Diagnostic lane"))
    s.texts.append(TextBox(["Accepted lane"], MARGIN_X + 250_000, 3_560_000, 4_480_000, 270_000, 18, DARK, True, align="ctr", name="Accepted head"))
    s.texts.append(TextBox(["direct residual bridge", "AD row identity", "Newton-Euler substitution", "conditional sixth-order claim"],
                           MARGIN_X + 390_000, 3_980_000, 4_200_000, 640_000, 13, DARK, align="ctr", name="Accepted body"))
    s.texts.append(TextBox(["Diagnostic lane"], MARGIN_X + 5_785_600, 3_560_000, 4_480_000, 270_000, 18, DARK, True, align="ctr", name="Diag head"))
    s.texts.append(TextBox(["fixed tolerance logs", "primitive Taylor fragments", "external source-policy rows", "residual-only mechanism rows"],
                           MARGIN_X + 5_925_600, 3_980_000, 4_200_000, 640_000, 13, DARK, align="ctr", name="Diag body"))
    s.texts.append(TextBox(["The ledger tells the agent what not to say."],
                           MARGIN_X, 5_360_000, 10_515_600, 330_000, 18, RED, True, align="ctr", name="Proof note"))
    return s


def compact_numerical_ladder_slide() -> Slide:
    s = Slide(title="Numerical ladder: examples expose different failure modes")
    rungs = [
        ("6", "external same-test", RED),
        ("5", "ASME mechanisms", ORANGE),
        ("4", "friction regimes", BLUE),
        ("3", "constrained DAE", GREEN),
        ("2", "smooth mechanics", "7A4EA3"),
        ("1", "SO(3) kinematics", DARK),
    ]
    x0, y0 = 1_250_000, 1_430_000
    for i, (num, head, color) in enumerate(rungs):
        y = y0 + i * 620_000
        x = x0 + i * 520_000
        w = 8_900_000 - i * 750_000
        s.rects.append(Rect(x, y, w, 440_000, LIGHT, MID, "Numerical rung"))
        s.texts.append(TextBox([num], x + 115_000, y + 72_000, 300_000, 260_000, 15, WHITE, True, align="ctr", valign="m", fill=color, name="Rung num"))
        s.texts.append(TextBox([head], x + 560_000, y + 95_000, w - 700_000, 200_000, 15, DARK, True, name="Rung label"))
    s.texts.append(TextBox(["Acceptance evidence: at least three h values, pinned reference policy, CSV/JSON/plot trail, and claim role."],
                           MARGIN_X, 5_540_000, 10_515_600, 280_000, 15, DARK, True, align="ctr", name="Ladder note"))
    return s


def compact_convergence_slide() -> Slide:
    s = Slide(title="Case evidence: smooth order verifier")
    add_image_panel(s, "convergence.png", MARGIN_X, 1_360_000, 6_760_000, 4_560_000, "v047 smooth cylindrical-chain convergence")
    s.rects.append(Rect(MARGIN_X + 7_090_000, 1_520_000, 3_425_600, 3_980_000, LIGHT, MID, "Evidence notes"))
    s.texts.append(TextBox(["Accepted local method claim"], MARGIN_X + 7_330_000, 1_800_000, 2_945_600, 300_000, 18, RED, True, name="Evidence head"))
    s.texts.append(TextBox(["Gauss6 / FullVA", "conditional sixth-order path", "observed slopes about 7.16 / 7.07", "not an external superiority claim"],
                           MARGIN_X + 7_390_000, 2_300_000, 2_825_600, 1_450_000, 15, DARK, name="Evidence body"))
    s.texts.append(TextBox(["The agent must preserve this boundary exactly."],
                           MARGIN_X + 7_390_000, 4_570_000, 2_825_600, 360_000, 14, ORANGE, True, name="Boundary"))
    return s


def compact_asme_slide() -> Slide:
    s = Slide(title="Mechanism verifier: ASME lower-pair examples")
    add_image_panel(s, "asme_lower_pair_graph_bridge.png", MARGIN_X, 1_430_000, 4_980_000, 4_260_000, "lower-pair graph bridge")
    add_image_panel(s, "asme_closed_loop_kinematic_fullva.png", MARGIN_X + 5_320_000, 1_430_000, 5_195_600, 2_010_000, "closed-loop kinematic FullVA")
    add_image_panel(s, "closed_loop_true_dynamic_order.png", MARGIN_X + 5_320_000, 3_680_000, 5_195_600, 2_010_000, "dynamic-order staging")
    return s


def compact_endpoint_slide() -> Slide:
    s = Slide(title="Endpoint closure is its own sandbox")
    add_image_panel(s, "endpoint_kkt_closure.png", MARGIN_X, 1_500_000, 10_515_600, 2_360_000, "raw residual, projection baseline, and KKT closure must stay separated")
    s.rects.append(Rect(MARGIN_X, 4_230_000, 10_515_600, 980_000, "FFF7E8", ORANGE, "Endpoint warning"))
    s.texts.append(TextBox(["Why it matters"], MARGIN_X + 260_000, 4_430_000, 2_000_000, 300_000, 18, DARK, True, name="Endpoint head"))
    s.texts.append(TextBox(["A projection can make constraints look clean while changing the one-step map. The agent cannot hide that inside an order claim."],
                           MARGIN_X + 2_330_000, 4_455_000, 7_760_000, 280_000, 16, DARK, True, name="Endpoint text"))
    return s


def compact_caveats_slide() -> Slide:
    s = Slide(title="Caveats are first-class evidence")
    add_image_panel(s, "friction_smoothness_sweep.png", MARGIN_X, 1_430_000, 5_060_000, 2_450_000, "friction smoothness boundary")
    add_image_panel(s, "sparse_speed_gap.png", MARGIN_X + 5_455_600, 1_430_000, 5_060_000, 2_450_000, "sparse correctness vs sparse speed")
    s.rects.append(Rect(MARGIN_X, 4_300_000, 10_515_600, 820_000, LIGHT, MID, "Caveat note"))
    s.texts.append(TextBox(["Agent behavior"], MARGIN_X + 250_000, 4_530_000, 2_100_000, 250_000, 18, RED, True, name="Caveat head"))
    s.texts.append(TextBox(["Do not delete caveats. Promote smooth-order evidence, demote sharp-friction and runtime caveats to their correct claim lanes."],
                           MARGIN_X + 2_350_000, 4_545_000, 7_850_000, 250_000, 15, DARK, True, name="Caveat body"))
    return s


def compact_search_slide() -> Slide:
    s = Slide(title="Search strategy: negative results guide the next verifier")
    add_image_panel(s, "order_closure_blend.png", MARGIN_X, 1_430_000, 10_515_600, 2_040_000, "order and terminal closure do not automatically intersect")
    add_image_panel(s, "velocity_compression.png", MARGIN_X, 3_740_000, 10_515_600, 2_020_000, "velocity-compression probes prune rows that miss the required span")
    return s


def compact_external_slide() -> Slide:
    s = Slide(title="External comparison remains bounded")
    add_image_panel(s, "strict_common_reference_work_precision.png", MARGIN_X, 1_430_000, 5_060_000, 2_420_000, "common-reference work/precision")
    add_image_panel(s, "tfe_algorithm_literal_work_precision.png", MARGIN_X + 5_455_600, 1_430_000, 5_060_000, 2_420_000, "literal TFE algorithm diagnostics")
    s.rects.append(Rect(MARGIN_X, 4_280_000, 10_515_600, 910_000, "FFF1F1", RED, "External boundary"))
    s.texts.append(TextBox(["Boundary"], MARGIN_X + 250_000, 4_520_000, 1_800_000, 280_000, 18, RED, True, name="Boundary head"))
    s.texts.append(TextBox(["v048 provides same-test scaffolds, but source-policy external superiority remains false until the strict public campaigns close."],
                           MARGIN_X + 2_050_000, 4_535_000, 8_100_000, 260_000, 15, DARK, True, name="Boundary body"))
    return s


def compact_claim_slide() -> Slide:
    s = Slide(title="Claim state machine")
    add_image_panel(s, "claim_boundary_limitations.png", MARGIN_X, 1_360_000, 6_550_000, 4_420_000, "accepted, diagnostic, and open boundaries in one frame")
    states = [
        ("hypothesis", MUTED),
        ("diagnostic", BLUE),
        ("accepted", GREEN),
        ("open", ORANGE),
        ("forbidden", RED),
    ]
    x = MARGIN_X + 6_920_000
    y0 = 1_600_000
    for i, (name, color) in enumerate(states):
        y = y0 + i * 650_000
        s.texts.append(TextBox([name], x, y, 3_400_000, 360_000, 16, WHITE, True, align="ctr", valign="m", fill=color if color != MUTED else DARK, name="State"))
    s.texts.append(TextBox(["A claim can move backward when a validator exposes stale prose or unfair policy."],
                           x, 5_080_000, 3_400_000, 450_000, 13, DARK, True, align="ctr", name="Claim note"))
    return s


def compact_recipe_slide() -> Slide:
    s = Slide(title="How to build this agent for our integrator work")
    steps = [
        ("1", "encode MethodSpec", RED),
        ("2", "pin ProblemSpec", BLUE),
        ("3", "choose sandbox level", GREEN),
        ("4", "run numerical ladder", ORANGE),
        ("5", "update proof ledger", DARK),
        ("6", "gate paper claims", RED),
    ]
    x0, y0 = MARGIN_X, 1_520_000
    w, h = 3_220_000, 1_080_000
    for i, (num, head, color) in enumerate(steps):
        x = x0 + (i % 3) * 3_650_000
        y = y0 + (i // 3) * 1_650_000
        s.rects.append(Rect(x, y, w, h, LIGHT, MID, "Recipe box"))
        s.texts.append(TextBox([num], x + 170_000, y + 230_000, 360_000, 360_000, 18, WHITE, True, align="ctr", valign="m", fill=color, name="Step num"))
        s.texts.append(TextBox([head], x + 660_000, y + 285_000, w - 850_000, 310_000, 17, DARK, True, name="Recipe head"))
    s.rects.append(Rect(MARGIN_X, 5_130_000, 10_515_600, 620_000, "EAF4EA", GREEN, "Recipe takeaway"))
    s.texts.append(TextBox(["Good autonomy here means fewer unverified claims, not fewer human research decisions."],
                           MARGIN_X + 220_000, 5_300_000, 10_075_600, 250_000, 17, DARK, True, align="ctr", name="Recipe note"))
    return s


def compact_references_slide() -> Slide:
    s = Slide(title="References used by the agent design")
    refs = [
        ("DAE / Lie groups", "Hairer & Wanner 1996; Gear, Leimkuhler & Gupta 1985; Munthe-Kaas 1998/1999; Bruls, Cardona & Arnold 2012; Wieloch & Arnold 2021."),
        ("TFE / higher order", "Chaturvedi, Sandu & Sandu 2026, doi:10.1007/s11044-026-10153-w; Kim & Reddy 2017; Borri & Atluri 1988; Hughes & Hulbert 1988; Bauchau 2024."),
        ("SBEL baselines", "Taves, Kissel & Negrut 2020; Kissel, Negrut & Taves 2021/2022; Fang et al. 2023; Kissel, Bakke & Negrut 2024."),
        ("Friction/contact", "Brown & McPhee 2016; Stewart & Trinkle 1996; Anitescu & Potra 1997; Tasora & Anitescu 2011."),
        ("Local artifacts", "main_cmame.tex bibliography; REFERENCE_METADATA_AUDIT.md/json; CURRENT_PIPELINE_CONTRACT.md; ORDER_PROOF_LEDGER.md; summary_v047.json; v048 same-test scaffolds."),
    ]
    y0 = 1_420_000
    for i, (tag, body) in enumerate(refs):
        y = y0 + i * 820_000
        fill = LIGHT if i % 2 == 0 else WHITE
        s.rects.append(Rect(MARGIN_X, y, 10_515_600, 650_000, fill, MID, "Ref row"))
        s.rects.append(Rect(MARGIN_X, y, 95_000, 650_000, RED if i == 0 else DARK, None, "Ref accent"))
        s.texts.append(TextBox([tag], MARGIN_X + 170_000, y + 150_000, 1_780_000, 260_000, 11, RED, True, name="Ref tag"))
        s.texts.append(TextBox([body], MARGIN_X + 2_060_000, y + 105_000, 8_200_000, 360_000, 9, DARK, name="Ref body"))
    s.texts.append(TextBox(["Reference metadata audit status: 28 references; 16/16 DOI rows verified; 12/12 local non-DOI rows verified."],
                           MARGIN_X, 5_720_000, 10_515_600, 230_000, 10, MUTED, align="ctr", name="Ref audit"))
    return s


def build_slides() -> list[Slide]:
    slides: list[Slide] = [
        compact_title_slide(),
        compact_lab_problem_slide(),
        compact_reference_landscape_slide(),
        compact_evolution_slide(),
        compact_agent_architecture_slide(),
        compact_method_slide(),
        compact_sandbox_slide(),
        compact_proof_slide(),
        compact_numerical_ladder_slide(),
        compact_convergence_slide(),
        compact_asme_slide(),
        compact_endpoint_slide(),
        compact_caveats_slide(),
        compact_search_slide(),
        compact_external_slide(),
        compact_claim_slide(),
        compact_recipe_slide(),
        compact_references_slide(),
    ]
    return slides


def build() -> None:
    slides = build_slides()
    image_media: dict[Path, str] = {}
    for slide in slides:
        for im in slide.images:
            if im.path not in image_media:
                image_media[im.path] = f"integrator_agent_image{len(image_media) + 1}.png"

    tmp = OUT.with_suffix(".tmp.pptx")
    if tmp.exists():
        tmp.unlink()

    with ZipFile(TEMPLATE, "r") as src, ZipFile(tmp, "w", ZIP_DEFLATED) as dst:
        keep_prefixes = ("ppt/slideMasters/", "ppt/slideLayouts/", "ppt/theme/")
        keep_exact = {"ppt/presProps.xml", "ppt/viewProps.xml", "ppt/tableStyles.xml", "ppt/media/image1.png"}
        for name in src.namelist():
            if name in keep_exact or name.startswith(keep_prefixes):
                dst.writestr(name, src.read(name))

        default_text_style = extract_default_text_style(src)
        dst.writestr("[Content_Types].xml", content_types_xml(len(slides)))
        dst.writestr(
            "_rels/.rels",
            rels_xml([
                ("rId1", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument", "ppt/presentation.xml"),
                ("rId2", "http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties", "docProps/core.xml"),
                ("rId3", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties", "docProps/app.xml"),
            ]),
        )
        dst.writestr("docProps/core.xml", core_xml())
        dst.writestr("docProps/app.xml", app_xml(len(slides)))
        dst.writestr("ppt/presentation.xml", presentation_xml(len(slides), default_text_style))

        pres_rels = [("rId1", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster", "slideMasters/slideMaster1.xml")]
        for i in range(1, len(slides) + 1):
            pres_rels.append((f"rId{i + 1}", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide", f"slides/slide{i}.xml"))
        base = len(slides) + 2
        pres_rels.extend([
            (f"rId{base}", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme", "theme/theme1.xml"),
            (f"rId{base + 1}", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/presProps", "presProps.xml"),
            (f"rId{base + 2}", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/viewProps", "viewProps.xml"),
            (f"rId{base + 3}", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/tableStyles", "tableStyles.xml"),
        ])
        dst.writestr("ppt/_rels/presentation.xml.rels", rels_xml(pres_rels))

        for image_path, media_name in image_media.items():
            dst.writestr(f"ppt/media/{media_name}", image_path.read_bytes())

        for i, slide in enumerate(slides, 1):
            rels = [("rId1", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout", "../slideLayouts/slideLayout3.xml")]
            rel_ids = []
            for j, im in enumerate(slide.images, 2):
                rid = f"rId{j}"
                rel_ids.append(rid)
                rels.append((rid, "http://schemas.openxmlformats.org/officeDocument/2006/relationships/image", f"../media/{image_media[im.path]}"))
            dst.writestr(f"ppt/slides/slide{i}.xml", slide_xml(slide, i, rel_ids))
            dst.writestr(f"ppt/slides/_rels/slide{i}.xml.rels", rels_xml(rels))

    if OUT.exists():
        OUT.unlink()
    shutil.move(tmp, OUT)


def validate_package() -> None:
    with ZipFile(OUT, "r") as z:
        names = set(z.namelist())
        slides = sorted(n for n in names if re.match(r"ppt/slides/slide\d+\.xml$", n))
        expected = len(build_slides())
        if len(slides) != expected:
            raise RuntimeError(f"Expected {expected} slides, found {len(slides)}")
        for s in slides:
            idx = re.search(r"slide(\d+)\.xml", s).group(1)
            rel = f"ppt/slides/_rels/slide{idx}.xml.rels"
            if rel not in names:
                raise RuntimeError(f"Missing rels for slide {idx}")
        print(f"Wrote {OUT.name} with {len(slides)} slides and {len([n for n in names if n.startswith('ppt/media/integrator_agent_image')])} embedded figures.")


if __name__ == "__main__":
    build()
    validate_package()
