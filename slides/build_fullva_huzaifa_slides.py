#!/usr/bin/env python3
"""Build a Huzaifa-style PPTX deck for the v047/v048 autoresearch paper.

This intentionally avoids third-party packages.  It reuses the theme, slide
master, and slide layouts from PhDDefense_Huzaifa.pptx, then writes new slide
parts and embeds the paper figures needed for the talk.
"""

from __future__ import annotations

import html
import re
import shutil
import struct
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


ROOT = Path(__file__).resolve().parent
TEMPLATE = ROOT / "PhDDefense_Huzaifa.pptx"
OUT = ROOT / "Jingquan_FullVA_Huzaifa_style_slides.pptx"
WORK = ROOT.parent / "lie_group_integrator_work"
PAPER = WORK / "paper_v047_cylindrical_chain"
FIG = PAPER / "figures"

SLIDE_W = 12_192_000
SLIDE_H = 6_858_000
FOOTER_Y = 6_356_350
MARGIN_X = 838_200
TITLE_Y = 365_125
TITLE_W = 10_515_600
CONTENT_TOP = 1_500_000
CONTENT_BOTTOM = 6_050_000

DATE_TEXT = "06/09/2026"
FOOTER_TEXT = "University of Wisconsin - Madison"

FONT = "Anthropic Sans"
FALLBACK_FONT = "Arial"

RED = "C00000"
DARK = "222222"
MUTED = "666666"
LIGHT = "F4F5F7"
MID = "D9DDE3"
BLUE = "4472C4"
GREEN = "2E7D32"
ORANGE = "ED7D31"
WHITE = "FFFFFF"
BLACK = "000000"


def emu(inches: float) -> int:
    return int(round(inches * 914_400))


def xml_escape(text: object) -> str:
    return html.escape(str(text), quote=False)


def png_size(path: Path) -> tuple[int, int]:
    with path.open("rb") as fh:
        sig = fh.read(8)
        if sig != b"\x89PNG\r\n\x1a\n":
            raise ValueError(f"Not a PNG: {path}")
        chunk_len = fh.read(4)
        chunk_type = fh.read(4)
        if chunk_type != b"IHDR":
            raise ValueError(f"Missing IHDR: {path}")
        data = fh.read(8)
        return struct.unpack(">II", data)


def fit_rect(path: Path, x: int, y: int, w: int, h: int) -> tuple[int, int, int, int]:
    pw, ph = png_size(path)
    scale = min(w / pw, h / ph)
    nw = int(pw * scale)
    nh = int(ph * scale)
    return x + (w - nw) // 2, y + (h - nh) // 2, nw, nh


@dataclass
class ImageRef:
    path: Path
    x: int
    y: int
    w: int
    h: int
    name: str = "Figure"


@dataclass
class TextBox:
    lines: list[str]
    x: int
    y: int
    w: int
    h: int
    size: int = 24
    color: str = DARK
    bold: bool = False
    align: str = "l"
    valign: str = "t"
    name: str = "TextBox"
    fill: str | None = None
    line: str | None = None
    margin: int = 0
    font: str = FONT


@dataclass
class Rect:
    x: int
    y: int
    w: int
    h: int
    fill: str = LIGHT
    line: str | None = None
    name: str = "Rect"


@dataclass
class Slide:
    title: str
    kind: str = "content"
    texts: list[TextBox] = field(default_factory=list)
    rects: list[Rect] = field(default_factory=list)
    images: list[ImageRef] = field(default_factory=list)
    notes: str = ""
    show_footer: bool = True


def text_box_xml(shape_id: int, tb: TextBox) -> str:
    fill = "<a:noFill/>" if tb.fill is None else (
        f"<a:solidFill><a:srgbClr val=\"{tb.fill}\"/></a:solidFill>"
    )
    line = "<a:ln><a:noFill/></a:ln>" if tb.line is None else (
        f"<a:ln w=\"12700\"><a:solidFill><a:srgbClr val=\"{tb.line}\"/></a:solidFill></a:ln>"
    )
    bold = " b=\"1\"" if tb.bold else ""
    anchor = {"t": "t", "m": "ctr", "b": "b"}.get(tb.valign, "t")
    body_pr = (
        f"<a:bodyPr wrap=\"square\" lIns=\"{tb.margin}\" tIns=\"{tb.margin}\" "
        f"rIns=\"{tb.margin}\" bIns=\"{tb.margin}\" anchor=\"{anchor}\"/>"
    )
    paragraphs = []
    for idx, line_text in enumerate(tb.lines):
        escaped = xml_escape(line_text)
        spc_before = "0" if idx == 0 else "650"
        paragraphs.append(
            f"<a:p><a:pPr algn=\"{tb.align}\"><a:spcBef><a:spcPts val=\"{spc_before}\"/>"
            f"</a:spcBef><a:buNone/></a:pPr><a:r><a:rPr lang=\"en-US\" "
            f"sz=\"{tb.size * 100}\"{bold}><a:solidFill><a:srgbClr val=\"{tb.color}\"/>"
            f"</a:solidFill><a:latin typeface=\"{xml_escape(tb.font)}\"/>"
            f"<a:ea typeface=\"{xml_escape(tb.font)}\"/><a:cs typeface=\"{xml_escape(tb.font)}\"/>"
            f"</a:rPr><a:t>{escaped}</a:t></a:r></a:p>"
        )
    return (
        f"<p:sp><p:nvSpPr><p:cNvPr id=\"{shape_id}\" name=\"{xml_escape(tb.name)}\"/>"
        f"<p:cNvSpPr txBox=\"1\"/><p:nvPr/></p:nvSpPr><p:spPr><a:xfrm>"
        f"<a:off x=\"{tb.x}\" y=\"{tb.y}\"/><a:ext cx=\"{tb.w}\" cy=\"{tb.h}\"/>"
        f"</a:xfrm><a:prstGeom prst=\"rect\"><a:avLst/></a:prstGeom>{fill}{line}"
        f"</p:spPr><p:txBody>{body_pr}<a:lstStyle/>{''.join(paragraphs)}</p:txBody></p:sp>"
    )


def rect_xml(shape_id: int, r: Rect) -> str:
    line = "<a:ln><a:noFill/></a:ln>" if r.line is None else (
        f"<a:ln w=\"12700\"><a:solidFill><a:srgbClr val=\"{r.line}\"/></a:solidFill></a:ln>"
    )
    return (
        f"<p:sp><p:nvSpPr><p:cNvPr id=\"{shape_id}\" name=\"{xml_escape(r.name)}\"/>"
        f"<p:cNvSpPr/><p:nvPr/></p:nvSpPr><p:spPr><a:xfrm>"
        f"<a:off x=\"{r.x}\" y=\"{r.y}\"/><a:ext cx=\"{r.w}\" cy=\"{r.h}\"/>"
        f"</a:xfrm><a:prstGeom prst=\"rect\"><a:avLst/></a:prstGeom>"
        f"<a:solidFill><a:srgbClr val=\"{r.fill}\"/></a:solidFill>{line}</p:spPr></p:sp>"
    )


def image_xml(shape_id: int, rel_id: str, im: ImageRef) -> str:
    return (
        f"<p:pic><p:nvPicPr><p:cNvPr id=\"{shape_id}\" name=\"{xml_escape(im.name)}\"/>"
        f"<p:cNvPicPr><a:picLocks noChangeAspect=\"1\"/></p:cNvPicPr><p:nvPr/></p:nvPicPr>"
        f"<p:blipFill><a:blip r:embed=\"{rel_id}\"/><a:stretch><a:fillRect/>"
        f"</a:stretch></p:blipFill><p:spPr><a:xfrm><a:off x=\"{im.x}\" y=\"{im.y}\"/>"
        f"<a:ext cx=\"{im.w}\" cy=\"{im.h}\"/></a:xfrm><a:prstGeom prst=\"rect\">"
        f"<a:avLst/></a:prstGeom></p:spPr></p:pic>"
    )


def footer_shapes(slide_num: int) -> list[TextBox]:
    return [
        TextBox([DATE_TEXT], MARGIN_X, FOOTER_Y, 2_743_200, 365_125, 10, MUTED, name="Date"),
        TextBox([FOOTER_TEXT], 4_038_600, FOOTER_Y, 4_114_800, 365_125, 10, MUTED, align="ctr", name="Footer"),
        TextBox([str(slide_num)], 8_610_600, FOOTER_Y, 2_743_200, 365_125, 10, MUTED, align="r", name="Slide Number"),
    ]


def slide_xml(slide: Slide, slide_num: int, image_rel_ids: list[str]) -> str:
    shape_id = 2
    parts: list[str] = []
    parts.append(rect_xml(shape_id, Rect(0, 0, SLIDE_W, SLIDE_H, WHITE, None, "White background")))
    shape_id += 1

    if slide.kind == "title":
        parts.append(rect_xml(shape_id, Rect(0, 0, 120_000, SLIDE_H, RED, None, "Red spine")))
        shape_id += 1
    elif slide.kind == "section":
        parts.append(rect_xml(shape_id, Rect(MARGIN_X, 2_200_000, 10_515_600, 35_000, RED, None, "Section rule")))
        shape_id += 1
    else:
        parts.append(rect_xml(shape_id, Rect(MARGIN_X, 1_240_000, 10_515_600, 25_000, RED, None, "Title rule")))
        shape_id += 1
        parts.append(text_box_xml(shape_id, TextBox([slide.title], MARGIN_X, TITLE_Y, TITLE_W, 850_000, 30, DARK, True, name="Title")))
        shape_id += 1

    for r in slide.rects:
        parts.append(rect_xml(shape_id, r))
        shape_id += 1
    for tb in slide.texts:
        parts.append(text_box_xml(shape_id, tb))
        shape_id += 1
    for rel_id, im in zip(image_rel_ids, slide.images):
        parts.append(image_xml(shape_id, rel_id, im))
        shape_id += 1
    if slide.show_footer:
        for tb in footer_shapes(slide_num):
            parts.append(text_box_xml(shape_id, tb))
            shape_id += 1

    return (
        "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>"
        "<p:sld xmlns:a=\"http://schemas.openxmlformats.org/drawingml/2006/main\" "
        "xmlns:r=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships\" "
        "xmlns:p=\"http://schemas.openxmlformats.org/presentationml/2006/main\">"
        "<p:cSld><p:spTree><p:nvGrpSpPr><p:cNvPr id=\"1\" name=\"\"/>"
        "<p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm>"
        "<a:off x=\"0\" y=\"0\"/><a:ext cx=\"0\" cy=\"0\"/><a:chOff x=\"0\" y=\"0\"/>"
        "<a:chExt cx=\"0\" cy=\"0\"/></a:xfrm></p:grpSpPr>"
        f"{''.join(parts)}</p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/>"
        "</p:clrMapOvr></p:sld>"
    )


def rels_xml(rels: list[tuple[str, str, str]]) -> str:
    body = "".join(
        f"<Relationship Id=\"{rid}\" Type=\"{typ}\" Target=\"{xml_escape(target)}\"/>"
        for rid, typ, target in rels
    )
    return (
        "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>"
        f"<Relationships xmlns=\"http://schemas.openxmlformats.org/package/2006/relationships\">{body}</Relationships>"
    )


def section_slide(label: str, title: str, subtitle: str = "") -> Slide:
    s = Slide(title=title, kind="section")
    s.texts.append(TextBox([label], MARGIN_X, 1_330_000, 2_800_000, 450_000, 18, RED, True, name="Section label"))
    s.texts.append(TextBox([title], MARGIN_X, 2_380_000, 10_200_000, 1_000_000, 38, DARK, True, name="Section title"))
    if subtitle:
        s.texts.append(TextBox([subtitle], MARGIN_X, 3_420_000, 9_200_000, 850_000, 20, MUTED, name="Section subtitle"))
    return s


def statement_slide(title: str, headline: list[str], support: list[str] | None = None) -> Slide:
    s = Slide(title=title)
    s.texts.append(TextBox(headline, MARGIN_X, 1_700_000, 10_515_600, 1_900_000, 34, DARK, True, name="Headline"))
    if support:
        s.texts.append(TextBox(support, MARGIN_X + 450_000, 3_900_000, 9_500_000, 1_350_000, 20, MUTED, name="Support"))
        s.rects.append(Rect(MARGIN_X, 3_890_000, 55_000, 1_200_000, RED, None, "Accent"))
    return s


def bullets_slide(title: str, bullets: list[str], subtitle: str | None = None) -> Slide:
    s = Slide(title=title)
    if subtitle:
        s.texts.append(TextBox([subtitle], MARGIN_X, 1_440_000, 10_515_600, 420_000, 16, MUTED, name="Subtitle"))
        y = 2_000_000
    else:
        y = 1_650_000
    for i, b in enumerate(bullets):
        yy = y + i * 760_000
        s.rects.append(Rect(MARGIN_X, yy + 70_000, 105_000, 105_000, RED if i == 0 else DARK, None, "Bullet mark"))
        s.texts.append(TextBox([b], MARGIN_X + 230_000, yy, 9_900_000, 520_000, 21, DARK, name=f"Bullet {i+1}"))
    return s


def two_col_slide(title: str, left_title: str, left: list[str], right_title: str, right: list[str]) -> Slide:
    s = Slide(title=title)
    gap = 260_000
    col_w = (10_515_600 - gap) // 2
    x1 = MARGIN_X
    x2 = MARGIN_X + col_w + gap
    for x, hdr, lines, color in [(x1, left_title, left, BLUE), (x2, right_title, right, ORANGE)]:
        s.rects.append(Rect(x, 1_560_000, col_w, 3_900_000, LIGHT, MID, "Column"))
        s.rects.append(Rect(x, 1_560_000, col_w, 90_000, color, None, "Column accent"))
        s.texts.append(TextBox([hdr], x + 220_000, 1_830_000, col_w - 440_000, 460_000, 21, DARK, True, name="Column title"))
        s.texts.append(TextBox(lines, x + 220_000, 2_440_000, col_w - 440_000, 2_600_000, 18, DARK, name="Column body"))
    return s


def figure_slide(title: str, fig_name: str, caption: str, bullets: list[str] | None = None) -> Slide:
    s = Slide(title=title)
    path = FIG / fig_name
    if bullets:
        s.texts.append(TextBox(bullets, MARGIN_X, 1_550_000, 3_150_000, 4_150_000, 17, DARK, name="Side bullets"))
        x, y, w, h = fit_rect(path, MARGIN_X + 3_450_000, 1_480_000, 7_050_000, 4_250_000)
    else:
        x, y, w, h = fit_rect(path, MARGIN_X, 1_420_000, 10_515_600, 4_550_000)
    s.images.append(ImageRef(path, x, y, w, h, fig_name))
    s.texts.append(TextBox([caption], MARGIN_X, 5_910_000, 10_515_600, 270_000, 10, MUTED, name="Caption"))
    return s


def number_cards_slide(title: str, cards: list[tuple[str, str, str]], note: str | None = None) -> Slide:
    s = Slide(title=title)
    n = len(cards)
    gap = 160_000
    total_w = 10_515_600
    card_w = (total_w - gap * (n - 1)) // n
    y = 1_850_000
    for i, (num, label, color) in enumerate(cards):
        x = MARGIN_X + i * (card_w + gap)
        s.rects.append(Rect(x, y, card_w, 2_300_000, LIGHT, MID, "Metric card"))
        s.rects.append(Rect(x, y, card_w, 80_000, color, None, "Metric accent"))
        s.texts.append(TextBox([num], x + 120_000, y + 420_000, card_w - 240_000, 660_000, 33, color, True, align="ctr", name="Metric value"))
        s.texts.append(TextBox([label], x + 160_000, y + 1_250_000, card_w - 320_000, 800_000, 15, DARK, align="ctr", name="Metric label"))
    if note:
        s.texts.append(TextBox([note], MARGIN_X, 4_780_000, 10_515_600, 720_000, 18, MUTED, align="ctr", name="Metric note"))
    return s


def roadmap_slide() -> Slide:
    s = Slide(title="Roadmap")
    items = [
        ("1", "Method", "Gauss6/FullVA residual"),
        ("2", "Claim boundary", "conditional sixth order"),
        ("3", "Evidence", "cylindrical chain and ASME examples"),
        ("4", "Diagnostics", "external comparison and open gates"),
    ]
    x0 = MARGIN_X
    y0 = 1_720_000
    box_w = 2_450_000
    gap = 230_000
    for i, (num, hdr, desc) in enumerate(items):
        x = x0 + i * (box_w + gap)
        color = [RED, BLUE, GREEN, ORANGE][i]
        s.rects.append(Rect(x, y0, box_w, 3_450_000, LIGHT, MID, "Roadmap box"))
        s.texts.append(TextBox([num], x + 180_000, y0 + 260_000, 540_000, 540_000, 24, WHITE, True, align="ctr", valign="m", fill=color, name="Roadmap num"))
        s.texts.append(TextBox([hdr], x + 180_000, y0 + 1_050_000, box_w - 360_000, 500_000, 21, DARK, True, name="Roadmap hdr"))
        s.texts.append(TextBox([desc], x + 180_000, y0 + 1_700_000, box_w - 360_000, 1_000_000, 15, MUTED, name="Roadmap desc"))
    return s


def build_slides() -> list[Slide]:
    slides: list[Slide] = []

    title = Slide("", kind="title", show_footer=False)
    title.texts.extend([
        TextBox(["A Conditional Sixth-Order", "Lie-Group FullVA Integrator", "for Lower-Pair Mechanisms"],
                720_000, 850_000, 10_700_000, 2_350_000, 36, DARK, True, name="Deck title"),
        TextBox(["Jingquan Wang", "Simulation-Based Engineering Laboratory", "Department of Mechanical Engineering, UW-Madison"],
                760_000, 3_600_000, 8_800_000, 920_000, 18, MUTED, name="Author"),
        TextBox([DATE_TEXT], 760_000, 5_160_000, 2_800_000, 360_000, 14, RED, True, name="Date"),
    ])
    slides.append(title)

    slides.append(statement_slide(
        "Lower-pair integration is hard",
        ["A position-accurate step can still carry", "velocity and reaction inconsistency."],
        ["Finite rotations live on SO(3).",
         "Lower-pair mechanisms are index-3 DAEs.",
         "The useful method must synchronize position, velocity, acceleration, and multipliers in one solve."]
    ))

    slides.append(two_col_slide(
        "The method tradeoff so far",
        "What existing tools do well",
        ["Lie-group integrators keep rotations on the manifold.",
         "DAE methods enforce holonomic constraints.",
         "TFE methods provide a high-order direct-integration route."],
        "What remains exposed",
        ["Endpoint velocity and acceleration rows can drift.",
         "Source-paper residual reproduction is not the same as a method claim.",
         "External same-test superiority needs stricter evidence than local runs."]
    ))

    slides.append(statement_slide(
        "Central thesis",
        ["A monolithic Gauss6/FullVA residual can deliver", "a conditional sixth-order smooth path", "while keeping lower-pair P/V/A constraints synchronized."],
        ["Accepted claim: Gauss6/FullVA order-six path.",
         "Comparator: local paper-style m=3 TFE formula target, expected order five.",
         "Non-claims stay explicit: full TFE replacement and external superiority remain open."]
    ))

    slides.append(bullets_slide(
        "Defending the central thesis",
        ["Question 1 - Can we build a square Lie-group FullVA residual?",
         "Question 2 - Does the accepted branch retain sixth-order behavior?",
         "Question 3 - Does the same residual vocabulary cover the four ASME examples?",
         "Question 4 - What does the evidence not claim?"]
    ))

    slides.append(roadmap_slide())

    slides.append(section_slide("1 / Method", "Gauss6/FullVA", "Build the lower-pair constraints into the Newton stage system."))

    slides.append(number_cards_slide(
        "FullVA means three constraint levels",
        [("P", "position: Phi(q) = 0", RED),
         ("V", "velocity: Phi_q(q) v = nu", BLUE),
         ("A", "acceleration: Phi_q a + dot(Phi_q) v = gamma", GREEN)],
        "The point is not to repair these rows after the step; they live inside the same nonlinear solve."
    ))

    slides.append(number_cards_slide(
        "The cylindrical-chain stage solve is square",
        [("3", "Gauss stages", RED),
         ("2", "bodies", BLUE),
         ("2", "lower-pair joints", GREEN),
         ("132", "unknowns and residual rows", ORANGE)],
        "For v047, 3 x {2 x 18 body variables + 2 x 4 multipliers} = 132."
    ))

    slides.append(figure_slide(
        "Method architecture",
        "method_stage_architecture.png",
        "Figure from the CMAME package: the accepted residual, proof boundary, and validators are kept separate.",
        ["The method path is Gauss6/FullVA.",
         "Paper TFE rows remain a comparator/diagnostic boundary.",
         "Artifacts bind figures, JSON, CSV, and validators."]
    ))

    slides.append(bullets_slide(
        "What Newton solves",
        ["Stage kinematics for r, Q, v, omega, a, alpha.",
         "Newton-Euler translational and rotational balance.",
         "Lower-pair position, velocity, and acceleration rows.",
         "Lagrange multipliers in the same 132-row stage vector."],
        "Compact form: R_G6FVA(q_n, v_n, a_n, Z; h) = 0."
    ))

    slides.append(figure_slide(
        "Endpoint closure is audited, not hidden",
        "endpoint_kkt_closure.png",
        "KKT endpoint closure is part of the accepted v047 audit trail; projection baselines are retained only for comparison.",
        ["Endpoint position and velocity closure are checked.",
         "Projection and KKT paths are separated.",
         "The accepted order claim is tied to the branch and solver contract."]
    ))

    slides.append(section_slide("2 / Claim Boundary", "Conditional order, not claim inflation", "The proof route and the paper-facing comparator have different jobs."))

    slides.append(bullets_slide(
        "The theorem is conditional by design",
        ["Assume a smooth FullVA lift on the accepted compact branch.",
         "Use the implemented 132-row residual and fixed row scaling.",
         "Require local residual defect O(h^7).",
         "Require branch-selected Newton scale eta_h^tube <= c_eta h^7."],
        "Observed slopes are downstream consistency evidence, not theorem premises."
    ))

    slides.append(two_col_slide(
        "Formal-order comparison",
        "Accepted method",
        ["Gauss6/FullVA.",
         "Method-order claim: 6.",
         "Smooth observed orders: 7.161 position, 7.066 velocity.",
         "Four ASME examples covered under the method gate."],
        "Comparator boundary",
        ["Local paper-style m=3 Gauss-Lobatto TFE target.",
         "Expected formula order: 2m - 1 = 5.",
         "Not a claim that the source-paper residual has been reimplemented.",
         "Not an external same-test superiority claim."]
    ))

    slides.append(two_col_slide(
        "Allowed and forbidden statements",
        "Allowed",
        ["Gauss6/FullVA is the accepted production path.",
         "The local formal-order comparator is order five.",
         "The current four-example mechanism coverage gate is accepted.",
         "Common-reference diagnostics can be shown as diagnostics."],
        "Forbidden for this deck",
        ["External superiority is accepted.",
         "Complete source-paper TFE residual reproduction is accepted.",
         "Full TFE stage replacement is solved.",
         "Default 1e-4 public-policy runs are required."]
    ))

    slides.append(section_slide("3 / Evidence", "What the artifacts show", "The talk follows the same evidence boundaries as the paper package."))

    slides.append(figure_slide(
        "Smooth cylindrical chain: high-order consistency",
        "convergence.png",
        "Headline v047 smooth h-sweep: position order 7.161, velocity order 7.066 against reference h=0.005.",
        ["Step sizes: h = 0.04, 0.02, 0.01.",
         "This supports the conditional order-six path.",
         "It is not a seventh-order theorem."]
    ))

    slides.append(figure_slide(
        "The four ASME mechanisms use the same constraint vocabulary",
        "asme_lower_pair_graph_bridge.png",
        "The bridge maps CD, DP1, DP2, and D lower-pair rows across single pendulum, double pendulum, four-link, and slider-crank.",
        ["The gate is about mechanism coverage.",
         "Rows are checked at position, velocity, and acceleration levels.",
         "The same FullVA vocabulary is used across the examples."]
    ))

    slides.append(number_cards_slide(
        "Example-level order boundary",
        [("6.024", "single pendulum min accepted dynamic order", RED),
         ("6.089", "double pendulum min accepted dynamic order", BLUE),
         ("1.34e-13", "four-link max reaction dynamics residual", GREEN),
         ("6.49e-15", "slider-crank max reaction dynamics residual", ORANGE)],
        "Single and double pendulum carry accepted dynamic-order evidence; four-link and slider-crank are coverage/reaction evidence."
    ))

    slides.append(bullets_slide(
        "Single and double pendulum carry dynamic-order rows",
        ["Single pendulum: absolute-coordinate driven FullVA residual, minimum observed order 6.024.",
         "Double pendulum: method-side FullVA mapping, nested local reference policy, minimum observed order 6.089.",
         "Both rows support the method-side dynamic order claim.",
         "They stay separate from external source-policy claims."]
    ))

    slides.append(figure_slide(
        "Four-link and slider-crank close the kinematic loop",
        "asme_closed_loop_kinematic_fullva.png",
        "Closed-loop FullVA solves enforce Phi=0, Phi_q qdot=nu, and Phi_q qdd=gamma for the two mechanisms.",
        ["These rows are accepted mechanism coverage.",
         "They are not promoted to external dynamic-order rows.",
         "Reaction reconstruction is checked separately."]
    ))

    slides.append(bullets_slide(
        "Reaction dynamics closes after kinematics",
        ["Four-link max full dynamics residual: 1.338e-13.",
         "Slider-crank max full dynamics residual: 6.492e-15.",
         "The multipliers are reconstructed from accepted kinematic states.",
         "This supports mechanism coverage, not source-policy superiority."]
    ))

    slides.append(figure_slide(
        "Closed-loop true-dynamic candidates are now visible",
        "closed_loop_true_dynamic_order.png",
        "v048 adds coarse true-dynamic local candidates for four-link and slider-crank, but keeps them out of external-superiority claims.",
        ["Four-link primary orders near 5.96 to 6.09.",
         "Slider-crank primary orders near 6.16 to 7.34.",
         "Same-test external promotion is still open."]
    ))

    slides.append(figure_slide(
        "Common-reference work/precision is diagnostic",
        "strict_common_reference_work_precision.png",
        "The same-window common-reference rows make error/work visible without closing source-policy superiority.",
        ["Common-reference cells are useful for comparison.",
         "Source-policy rows remain open.",
         "The deck should call this diagnostic evidence."]
    ))

    slides.append(figure_slide(
        "All-method result matrix",
        "all_method_result_matrix.png",
        "The paper package records all method/example cells while preserving the non-claim boundary for external rows.",
        ["44 method/example cells are checked in the current common-reference matrix.",
         "40/40 nonlocal velocity-order comparisons are positive.",
         "Those counts do not become source-paper superiority."]
    ))

    slides.append(section_slide("4 / Boundaries", "What remains open", "The negative space is part of the scientific result."))

    slides.append(number_cards_slide(
        "External comparison is not submission-ready",
        [("32/48", "performance matrix rows completed", RED),
         ("0/40", "source-policy rows promoted", ORANGE),
         ("not run", "full same-test campaign status", BLUE),
         ("false", "external superiority claim", GREEN)],
        "The current package supports a narrowed Gauss6/FullVA claim, not a global source-policy claim."
    ))

    slides.append(figure_slide(
        "Full TFE replacement remains open",
        "order_closure_blend.png",
        "The strongest source-free closures split terminal velocity closure from smooth order recovery.",
        ["Full TFE replacement is a stronger source-paper reproduction gate.",
         "It is not required for the accepted formal-order comparison.",
         "Current candidates do not satisfy both terminal closure and order."]
    ))

    slides.append(figure_slide(
        "The lower-pair closure gap is localized",
        "velocity_compression.png",
        "Velocity-compression audits show that target-free non-final rows do not span the missing closure directions.",
        ["The missing complement has eight lower-pair directions.",
         "Many terminal-limit and source-transport variants are ruled out.",
         "Next progress needs a revised analytical weak-row formula."]
    ))

    slides.append(figure_slide(
        "Sparse backend: correct, not yet faster",
        "sparse_speed_gap.png",
        "The sparse pattern is exact and row-VJP reduces colors, but dense jacfwd is still faster in the recorded wall-clock runs.",
        ["Exact pattern: 2637 entries.",
         "Row colors: 60 versus 90 column colors.",
         "Needed row-runtime reduction: about 18% to match dense."]
    ))

    slides.append(bullets_slide(
        "Sharp friction is a practical cost caveat",
        ["Smooth case: position/velocity orders 7.161/7.066.",
         "Sharp coarse h-sweep at vs=0.05: orders 1.894/2.683.",
         "Ultra refinement recovers high order: 7.521/5.725.",
         "Recovery costs about 7.25x runtime versus the h=0.01 baseline."],
        "The method claim rests on the smooth conditional path; sharp-friction coarse behavior is reported as a limitation."
    ))

    slides.append(figure_slide(
        "Claim boundary map",
        "claim_boundary_limitations.png",
        "The accepted claim, diagnostic evidence, and open gates are intentionally separated.",
        ["Green: accepted method/evidence.",
         "Orange: bounded diagnostic evidence.",
         "Open: source-policy rows, full TFE replacement, external superiority."]
    ))

    slides.append(statement_slide(
        "Conclusion",
        ["Gauss6/FullVA is a usable sixth-order lower-pair path", "when the smooth branch and solver-scale contracts hold."],
        ["It solves a monolithic 132-row stage residual for the cylindrical chain.",
         "It passes the four ASME mechanism gate under the stated evidence roles.",
         "It exceeds the local order-five m=3 TFE formula target at the formal-order level.",
         "It does not claim full source-paper residual replacement or external superiority."]
    ))

    slides.append(bullets_slide(
        "Open problems",
        ["Close or explicitly demote the remaining external source-policy suites.",
         "Derive an independent full-TFE weak-row replacement that closes terminal velocity and preserves smooth order.",
         "Turn exact sparse structure into a stable wall-clock win.",
         "Reduce sharp-friction cost while keeping high-order behavior in practical step ranges."]
    ))

    thanks = Slide("", kind="title", show_footer=False)
    thanks.texts.extend([
        TextBox(["Thank You"], 760_000, 1_470_000, 10_500_000, 880_000, 44, DARK, True, align="ctr", name="Thanks"),
        TextBox(["Questions?"], 760_000, 2_650_000, 10_500_000, 780_000, 32, RED, True, align="ctr", name="Questions"),
        TextBox(["Accepted claim: conditional sixth-order Gauss6/FullVA path", "Open boundary: source-policy/full-TFE/external superiority"],
                1_200_000, 4_350_000, 9_700_000, 900_000, 18, MUTED, align="ctr", name="Closing note"),
    ])
    slides.append(thanks)

    return slides


def content_types_xml(slide_count: int) -> str:
    overrides = [
        ("/ppt/presentation.xml", "application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"),
        ("/ppt/slideMasters/slideMaster1.xml", "application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml"),
        ("/ppt/theme/theme1.xml", "application/vnd.openxmlformats-officedocument.theme+xml"),
        ("/ppt/presProps.xml", "application/vnd.openxmlformats-officedocument.presentationml.presProps+xml"),
        ("/ppt/viewProps.xml", "application/vnd.openxmlformats-officedocument.presentationml.viewProps+xml"),
        ("/ppt/tableStyles.xml", "application/vnd.openxmlformats-officedocument.presentationml.tableStyles+xml"),
        ("/docProps/core.xml", "application/vnd.openxmlformats-package.core-properties+xml"),
        ("/docProps/app.xml", "application/vnd.openxmlformats-officedocument.extended-properties+xml"),
    ]
    for i in range(1, 9):
        overrides.append((f"/ppt/slideLayouts/slideLayout{i}.xml", "application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml"))
    for i in range(1, slide_count + 1):
        overrides.append((f"/ppt/slides/slide{i}.xml", "application/vnd.openxmlformats-officedocument.presentationml.slide+xml"))
    override_xml = "".join(
        f"<Override PartName=\"{part}\" ContentType=\"{ctype}\"/>" for part, ctype in overrides
    )
    return (
        "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>"
        "<Types xmlns=\"http://schemas.openxmlformats.org/package/2006/content-types\">"
        "<Default Extension=\"rels\" ContentType=\"application/vnd.openxmlformats-package.relationships+xml\"/>"
        "<Default Extension=\"xml\" ContentType=\"application/xml\"/>"
        "<Default Extension=\"png\" ContentType=\"image/png\"/>"
        f"{override_xml}</Types>"
    )


def presentation_xml(slide_count: int, default_text_style: str) -> str:
    sld_ids = "".join(
        f"<p:sldId id=\"{255 + i}\" r:id=\"rId{i + 1}\"/>" for i in range(1, slide_count + 1)
    )
    return (
        "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>"
        "<p:presentation xmlns:a=\"http://schemas.openxmlformats.org/drawingml/2006/main\" "
        "xmlns:r=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships\" "
        "xmlns:p=\"http://schemas.openxmlformats.org/presentationml/2006/main\" "
        "showSpecialPlsOnTitleSld=\"0\" saveSubsetFonts=\"1\">"
        "<p:sldMasterIdLst><p:sldMasterId id=\"2147483648\" r:id=\"rId1\"/></p:sldMasterIdLst>"
        f"<p:sldIdLst>{sld_ids}</p:sldIdLst>"
        "<p:sldSz cx=\"12192000\" cy=\"6858000\" type=\"wide\"/>"
        "<p:notesSz cx=\"6858000\" cy=\"9144000\"/>"
        f"{default_text_style}</p:presentation>"
    )


def core_xml() -> str:
    now = datetime(2026, 6, 9, 17, 0, 0, tzinfo=timezone.utc).isoformat().replace("+00:00", "Z")
    return (
        "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>"
        "<cp:coreProperties xmlns:cp=\"http://schemas.openxmlformats.org/package/2006/metadata/core-properties\" "
        "xmlns:dc=\"http://purl.org/dc/elements/1.1/\" "
        "xmlns:dcterms=\"http://purl.org/dc/terms/\" "
        "xmlns:dcmitype=\"http://purl.org/dc/dcmitype/\" "
        "xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\">"
        "<dc:title>Gauss6 FullVA Huzaifa-style Slides</dc:title>"
        "<dc:creator>Codex</dc:creator>"
        "<cp:lastModifiedBy>Codex</cp:lastModifiedBy>"
        f"<dcterms:created xsi:type=\"dcterms:W3CDTF\">{now}</dcterms:created>"
        f"<dcterms:modified xsi:type=\"dcterms:W3CDTF\">{now}</dcterms:modified>"
        "</cp:coreProperties>"
    )


def app_xml(slide_count: int) -> str:
    titles = "".join(f"<vt:lpstr>Slide {i}</vt:lpstr>" for i in range(1, slide_count + 1))
    return (
        "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>"
        "<Properties xmlns=\"http://schemas.openxmlformats.org/officeDocument/2006/extended-properties\" "
        "xmlns:vt=\"http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes\">"
        "<Application>Microsoft Office PowerPoint</Application>"
        "<PresentationFormat>Widescreen</PresentationFormat>"
        f"<Slides>{slide_count}</Slides><Notes>0</Notes><HiddenSlides>0</HiddenSlides>"
        "<ScaleCrop>false</ScaleCrop>"
        "<HeadingPairs><vt:vector size=\"2\" baseType=\"variant\"><vt:variant><vt:lpstr>Slide Titles</vt:lpstr></vt:variant>"
        f"<vt:variant><vt:i4>{slide_count}</vt:i4></vt:variant></vt:vector></HeadingPairs>"
        f"<TitlesOfParts><vt:vector size=\"{slide_count}\" baseType=\"lpstr\">{titles}</vt:vector></TitlesOfParts>"
        "<AppVersion>16.0000</AppVersion></Properties>"
    )


def extract_default_text_style(template: ZipFile) -> str:
    raw = template.read("ppt/presentation.xml").decode("utf-8")
    match = re.search(r"(<p:defaultTextStyle>.*?</p:defaultTextStyle>)", raw)
    if match:
        return match.group(1)
    return "<p:defaultTextStyle><a:defPPr><a:defRPr lang=\"en-US\"/></a:defPPr></p:defaultTextStyle>"


def build() -> None:
    if not TEMPLATE.exists():
        raise FileNotFoundError(TEMPLATE)
    slides = build_slides()
    image_media: dict[Path, str] = {}
    for slide in slides:
        for im in slide.images:
            if im.path not in image_media:
                image_media[im.path] = f"auto_image{len(image_media) + 1}.png"

    tmp = OUT.with_suffix(".tmp.pptx")
    if tmp.exists():
        tmp.unlink()

    with ZipFile(TEMPLATE, "r") as src, ZipFile(tmp, "w", ZIP_DEFLATED) as dst:
        keep_prefixes = (
            "ppt/slideMasters/",
            "ppt/slideLayouts/",
            "ppt/theme/",
        )
        keep_exact = {
            "ppt/presProps.xml",
            "ppt/viewProps.xml",
            "ppt/tableStyles.xml",
            "ppt/media/image1.png",
        }
        for name in src.namelist():
            if name in keep_exact or name.startswith(keep_prefixes):
                if name.startswith("ppt/slideLayouts/notes") or name.startswith("ppt/notes"):
                    continue
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
                rel_id = f"rId{j}"
                rel_ids.append(rel_id)
                rels.append((rel_id, "http://schemas.openxmlformats.org/officeDocument/2006/relationships/image", f"../media/{image_media[im.path]}"))
            dst.writestr(f"ppt/slides/slide{i}.xml", slide_xml(slide, i, rel_ids))
            dst.writestr(f"ppt/slides/_rels/slide{i}.xml.rels", rels_xml(rels))

    if OUT.exists():
        OUT.unlink()
    shutil.move(tmp, OUT)


def validate_package() -> None:
    with ZipFile(OUT, "r") as z:
        names = set(z.namelist())
        required = {
            "[Content_Types].xml",
            "_rels/.rels",
            "ppt/presentation.xml",
            "ppt/_rels/presentation.xml.rels",
            "ppt/slideMasters/slideMaster1.xml",
            "ppt/slideLayouts/slideLayout3.xml",
            "ppt/theme/theme1.xml",
        }
        missing = sorted(required - names)
        if missing:
            raise RuntimeError(f"Missing required parts: {missing}")
        slides = sorted(n for n in names if re.match(r"ppt/slides/slide\d+\.xml$", n))
        if len(slides) != len(build_slides()):
            raise RuntimeError(f"Expected {len(build_slides())} slides, found {len(slides)}")
        for s in slides:
            idx = re.search(r"slide(\d+)\.xml", s).group(1)
            rel = f"ppt/slides/_rels/slide{idx}.xml.rels"
            if rel not in names:
                raise RuntimeError(f"Missing rels for {s}")
            xml = z.read(s).decode("utf-8")
            for rid in re.findall(r'r:embed="([^"]+)"', xml):
                rel_xml = z.read(rel).decode("utf-8")
                if f'Id="{rid}"' not in rel_xml:
                    raise RuntimeError(f"{s} references missing relationship {rid}")
        print(f"Wrote {OUT.name} with {len(slides)} slides and {len([n for n in names if n.startswith('ppt/media/auto_image')])} embedded figures.")


if __name__ == "__main__":
    build()
    validate_package()
