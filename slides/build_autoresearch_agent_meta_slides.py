#!/usr/bin/env python3
"""Build Huzaifa-style meta slides about the auto-research agent pipeline."""

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
    FONT,
    FOOTER_TEXT,
    GREEN,
    LIGHT,
    MARGIN_X,
    MID,
    MUTED,
    ORANGE,
    OUT as _OLD_OUT,
    PAPER,
    RED,
    ROOT,
    SLIDE_H,
    SLIDE_W,
    TEMPLATE,
    WHITE,
    ImageRef,
    Rect,
    Slide,
    TextBox,
    app_xml,
    content_types_xml,
    extract_default_text_style,
    figure_slide,
    fit_rect,
    footer_shapes,
    number_cards_slide,
    presentation_xml,
    rect_xml,
    rels_xml,
    section_slide,
    slide_xml,
    statement_slide,
    text_box_xml,
    two_col_slide,
    xml_escape,
)


OUT = ROOT / "AutoResearch_Agent_Meta_Huzaifa_style_slides.pptx"
DATE_TEXT = "06/09/2026"


def bullets_slide(title: str, bullets: list[str], subtitle: str | None = None) -> Slide:
    s = Slide(title=title)
    y = 2_000_000 if subtitle else 1_650_000
    if subtitle:
        s.texts.append(TextBox([subtitle], MARGIN_X, 1_430_000, 10_515_600, 420_000, 16, MUTED, name="Subtitle"))
    for i, b in enumerate(bullets):
        yy = y + i * 720_000
        s.rects.append(Rect(MARGIN_X, yy + 68_000, 105_000, 105_000, RED if i == 0 else DARK, None, "Bullet mark"))
        s.texts.append(TextBox([b], MARGIN_X + 230_000, yy, 9_900_000, 500_000, 20, DARK, name=f"Bullet {i+1}"))
    return s


def process_slide(title: str, steps: list[tuple[str, str, str]]) -> Slide:
    s = Slide(title=title)
    x0 = MARGIN_X
    y = 1_760_000
    box_w = 1_890_000
    gap = 185_000
    for i, (num, head, desc) in enumerate(steps):
        x = x0 + i * (box_w + gap)
        color = [RED, BLUE, GREEN, ORANGE, DARK][i % 5]
        s.rects.append(Rect(x, y, box_w, 3_620_000, LIGHT, MID, "Process box"))
        s.texts.append(TextBox([num], x + 120_000, y + 230_000, 440_000, 440_000, 22, WHITE, True, align="ctr", valign="m", fill=color, name="Step num"))
        s.texts.append(TextBox([head], x + 140_000, y + 900_000, box_w - 280_000, 620_000, 18, DARK, True, name="Step head"))
        s.texts.append(TextBox([desc], x + 140_000, y + 1_620_000, box_w - 280_000, 1_420_000, 13, MUTED, name="Step desc"))
    return s


def architecture_slide() -> Slide:
    s = Slide(title="The agent is built around artifacts, not memory")
    rows = [
        ("Human objective", "broad research intent, stop conditions, opt-in gates", RED),
        ("Agent loop", "inspect -> choose gap -> edit/run -> verify -> update ledgers", BLUE),
        ("Artifact tree", "vNNN folders, CSV/JSON/PNG/MD reports, paper package", GREEN),
        ("Validators", "read-only checks that decide whether claims remain admissible", ORANGE),
    ]
    y0 = 1_560_000
    for i, (head, desc, color) in enumerate(rows):
        y = y0 + i * 950_000
        s.rects.append(Rect(MARGIN_X, y, 10_515_600, 660_000, LIGHT, MID, "Architecture row"))
        s.rects.append(Rect(MARGIN_X, y, 90_000, 660_000, color, None, "Architecture accent"))
        s.texts.append(TextBox([head], MARGIN_X + 260_000, y + 95_000, 2_450_000, 420_000, 20, DARK, True, name="Arch head"))
        s.texts.append(TextBox([desc], MARGIN_X + 3_020_000, y + 125_000, 7_050_000, 380_000, 17, DARK, name="Arch desc"))
    return s


def ledger_slide() -> Slide:
    s = Slide(title="Context is encoded as a contract")
    files = [
        ("CURRENT_PIPELINE_CONTRACT.md", "current claim boundary and command boundary"),
        ("CURRENT_STATUS_CN.md", "human-readable state, including recent negative probes"),
        ("ORDER_PROOF_LEDGER.md", "what is proved, conditional, or diagnostic"),
        ("VERSION_LEDGER.md / version_ledger.csv", "cross-version memory"),
        ("VALIDATION_QUICKSTART.md", "which command is safe for which question"),
    ]
    y = 1_520_000
    for i, (name, role) in enumerate(files):
        yy = y + i * 720_000
        s.rects.append(Rect(MARGIN_X, yy, 10_515_600, 520_000, WHITE if i % 2 else LIGHT, MID, "File row"))
        s.texts.append(TextBox([name], MARGIN_X + 180_000, yy + 105_000, 3_750_000, 280_000, 16, RED if i == 0 else DARK, True, name="File name"))
        s.texts.append(TextBox([role], MARGIN_X + 4_180_000, yy + 105_000, 6_150_000, 280_000, 16, MUTED, name="File role"))
    return s


def matrix_slide(title: str, rows: list[tuple[str, str, str, str]]) -> Slide:
    s = Slide(title=title)
    col_x = [MARGIN_X, MARGIN_X + 2_750_000, MARGIN_X + 5_900_000, MARGIN_X + 8_350_000]
    col_w = [2_540_000, 2_940_000, 2_230_000, 2_000_000]
    headers = ["Gate", "What it prevents", "Evidence", "Status"]
    y0 = 1_500_000
    for x, w, h in zip(col_x, col_w, headers):
        s.rects.append(Rect(x, y0, w, 420_000, DARK, None, "Header"))
        s.texts.append(TextBox([h], x + 80_000, y0 + 95_000, w - 160_000, 230_000, 12, WHITE, True, align="ctr", name="Header text"))
    for i, row in enumerate(rows):
        y = y0 + 420_000 + i * 690_000
        fill = LIGHT if i % 2 == 0 else WHITE
        for j, value in enumerate(row):
            s.rects.append(Rect(col_x[j], y, col_w[j], 690_000, fill, MID, "Cell"))
            color = RED if j == 0 else (GREEN if j == 3 and "closed" in value.lower() else DARK)
            s.texts.append(TextBox([value], col_x[j] + 85_000, y + 95_000, col_w[j] - 170_000, 500_000, 11, color, j == 0, name="Cell text"))
    return s


def build_meta_slides() -> list[Slide]:
    slides: list[Slide] = []

    title = Slide("", kind="title", show_footer=False)
    title.texts.extend([
        TextBox(["Building an Artifact-Grounded", "Auto-Research Agent"], 720_000, 930_000, 10_750_000, 1_550_000, 42, DARK, True, name="Deck title"),
        TextBox(["A meta deck on the research pipeline behind the Lie-group integrator work"], 760_000, 2_800_000, 9_600_000, 520_000, 20, MUTED, name="Subtitle"),
        TextBox(["Jingquan Wang", "Simulation-Based Engineering Laboratory", "University of Wisconsin - Madison"], 760_000, 4_070_000, 8_800_000, 850_000, 17, MUTED, name="Author"),
        TextBox([DATE_TEXT], 760_000, 5_310_000, 2_700_000, 340_000, 14, RED, True, name="Date"),
    ])
    slides.append(title)

    slides.append(statement_slide(
        "The problem is not just coding",
        ["Long-horizon research fails when the agent loses", "state, evidence, and claim boundaries."],
        ["The hard part is remembering what was proved, what merely ran, and what must not be claimed.",
         "The agent must carry months of negative results without turning them into noise.",
         "It must know when a cheap validator is enough and when a full campaign needs human opt-in."]
    ))

    slides.append(two_col_slide(
        "Why naive research agents drift",
        "Common failure mode",
        ["Runs one experiment and overstates the result.",
         "Forgets old counterexamples.",
         "Treats a plot, validator pass, or paper draft as proof.",
         "Reruns expensive scripts to answer read-only questions."],
        "What we need instead",
        ["Versioned memory.",
         "Executable claim gates.",
         "Negative evidence ledgers.",
         "Strict command boundaries."]
    ))

    slides.append(statement_slide(
        "Central thesis",
        ["An auto-research agent becomes useful when", "research state is an artifact graph", "and claims are executable contracts."],
        ["The agent does not rely on chat memory as the source of truth.",
         "It reads the current files, chooses the next missing gate, and verifies before updating status.",
         "The workflow is autonomous inside bounded tasks and conservative at claim boundaries."]
    ))

    slides.append(bullets_slide(
        "Defending the central thesis",
        ["Question 1 - How do we encode research memory so the agent can resume correctly?",
         "Question 2 - How do we make evidence and non-evidence machine-checkable?",
         "Question 3 - How do we keep the agent from promoting diagnostics into claims?",
         "Question 4 - What did this architecture enable in the v047/v048 case study?"]
    ))

    slides.append(process_slide(
        "Roadmap",
        [("1", "Research state", "artifact tree, version ledger, current contract"),
         ("2", "Agent loop", "inspect, choose gap, implement, verify, record"),
         ("3", "Guardrails", "claim boundary, validators, opt-in gates"),
         ("4", "Case study", "v047/v048 Lie-group integrator pipeline"),
         ("5", "Lessons", "what generalizes to other auto-research systems")]
    ))

    slides.append(section_slide("1 / Research State", "Make context durable", "The agent can only be persistent if the research state lives outside the conversation."))

    slides.append(architecture_slide())

    slides.append(number_cards_slide(
        "The workspace is a research artifact tree",
        [("48", "versioned vNNN research directories", RED),
         ("527", "generated result files checked by the top-level validator", BLUE),
         ("220", "CSV tables in the validation inventory", GREEN),
         ("198", "PNG plots checked by header", ORANGE)],
        "The tree is treated as evidence, not disposable build output."
    ))

    slides.append(ledger_slide())

    slides.append(bullets_slide(
        "Versions are kept, not overwritten",
        ["v001-v048 preserve the full path from SO(3) kinematics to external same-test scaffolds.",
         "Each version has a role: method candidate, diagnostic, baseline, proof audit, or paper gate.",
         "The version ledger lets the agent ask: what changed, what passed, what remains blocked?",
         "This is how the next action is selected from evidence rather than memory."]
    ))

    slides.append(section_slide("2 / Agent Loop", "Make progress auditable", "The loop is designed so every autonomous step leaves a checkable trace."))

    slides.append(process_slide(
        "The per-round research loop",
        [("1", "Inspect", "read current contract, summary JSON, ledgers, audit files"),
         ("2", "Select", "choose the next real missing gate, not a convenient subtask"),
         ("3", "Act", "edit code or run the bounded target audit"),
         ("4", "Verify", "run validators and inspect generated artifacts"),
         ("5", "Record", "update ledgers only when evidence changes the boundary")]
    ))

    slides.append(bullets_slide(
        "Validators are executable memory",
        ["They prevent stale README prose from becoming the source of truth.",
         "They distinguish accepted rows from diagnostic rows.",
         "They check figures, CSV, JSON, proof gates, and paper claim text together.",
         "They make the agent safe to resume after context compaction."]
    ))

    slides.append(two_col_slide(
        "Two command classes",
        "Read-only checks",
        ["validate_paper_package.py.",
         "validate_four_asme_minimal.py.",
         "validate_v047_outputs.py.",
         "validate_v048_outputs.py.",
         "Fast enough for routine state checks."],
        "Artifact generators",
        ["run_v047.py.",
         "v048 campaign runners.",
         "B4 source-policy execution commands.",
         "Used only after code changes or explicit opt-in."]
    ))

    slides.append(bullets_slide(
        "Negative evidence is first-class",
        ["A failed candidate is recorded with residual, rank, span, runtime, and missing direction.",
         "The agent uses those records to avoid re-testing ruled-out ideas.",
         "Recent full-TFE probes localize the gap instead of pretending it is closed.",
         "This turns failed experiments into search-space pruning."]
    ))

    slides.append(section_slide("3 / Guardrails", "Prevent claim inflation", "The pipeline is built to say exactly what is and is not known."))

    slides.append(matrix_slide(
        "Claim gates are explicit",
        [("Order gate", "observed slopes becoming theorem claims", "ORDER_ACCEPTANCE_GATE.json", "closed in scope"),
         ("Proof gate", "diagnostics becoming proof", "CMAME_PROOF_CONTRACT_GATE.json", "conditional"),
         ("External gate", "common-reference rows becoming superiority", "CMAME_EXTERNAL_BASELINE_GATE.json", "open"),
         ("TFE gate", "paper-style formula maps becoming full replacement", "FULL_TFE_REPLACEMENT_GAP_LEDGER.md", "open"),
         ("Submission gate", "validator pass becoming submission-ready", "CMAME_BLOCKER_CLOSURE_GATE.json", "global open")]
    ))

    slides.append(figure_slide(
        "Claim boundary as a visual artifact",
        "claim_boundary_limitations.png",
        "The paper package uses a figure to separate accepted evidence, bounded diagnostics, and open gates.",
        ["The agent can show the boundary instead of burying it in prose.",
         "This is valuable for humans reviewing a long autonomous run.",
         "It makes non-claims part of the presentation."]
    ))

    slides.append(two_col_slide(
        "Proof route versus proof residue",
        "Accepted direct route",
        ["Direct residual-bridge/Kantorovich route.",
         "96 non-dynamic certificate rows.",
         "36 Newton-Euler direct-substitution zero rows.",
         "Active PC2 closed in this route."],
        "Still diagnostic",
        ["Primitive 162-subterm Taylor lane.",
         "Residual-to-error promotion for closed-loop rows.",
         "Fixed-tolerance logs as theorem evidence.",
         "Source-policy superiority."]
    ))

    slides.append(number_cards_slide(
        "The agent has hard non-claims",
        [("false", "submission_ready", RED),
         ("false", "external_superiority_claim", ORANGE),
         ("false", "full_tfe_stage_replacement", BLUE),
         ("opt-in", "strict 1e-4 public-policy runs", GREEN)],
        "These fields are allowed to remain false while the narrower research claim is still useful."
    ))

    slides.append(section_slide("4 / Case Study", "v047/v048 as an agent-built research product", "The method is technical; here the point is how the agent managed the research."))

    slides.append(number_cards_slide(
        "What the agent helped assemble",
        [("v047", "cylindrical-chain method pipeline", RED),
         ("v048", "cross-paper same-test scaffold", BLUE),
         ("B1-B8", "narrowed claim blockers closed", GREEN),
         ("OC4/6/12", "global submission blockers still open", ORANGE)],
        "The architecture supports a useful narrowed result without hiding the global gaps."
    ))

    slides.append(figure_slide(
        "The paper result matrix is an agent-facing dashboard",
        "all_method_result_matrix.png",
        "The result matrix makes examples, methods, orders, and boundaries reviewable in one place.",
        ["This is not just a paper figure.",
         "It is a compressed state representation for the agent and the human.",
         "The matrix prevents isolated rows from being over-promoted."]
    ))

    slides.append(figure_slide(
        "Common-reference evidence is useful but bounded",
        "strict_common_reference_work_precision.png",
        "v048 records common-reference work/precision evidence without converting it into source-policy superiority.",
        ["The agent can run and summarize fairer rows.",
         "It still keeps source-policy rows at 0/40 promoted.",
         "The difference between useful and claim-ready evidence is explicit."]
    ))

    slides.append(figure_slide(
        "Closed-loop dynamics moved from plan to candidate evidence",
        "closed_loop_true_dynamic_order.png",
        "The v048 closed-loop true-dynamic rows are a good example of incremental autonomous progress.",
        ["First a feasibility audit.",
         "Then residual scaffold.",
         "Then one-step smoke.",
         "Then coarse order candidates and work/precision rows."]
    ))

    slides.append(figure_slide(
        "The hard open problem stays visible",
        "order_closure_blend.png",
        "Full-TFE replacement remains open because terminal closure and smooth order do not intersect.",
        ["The agent ruled out many nearby families.",
         "It localized the gap to lower-pair closure directions.",
         "It did not rewrite the conclusion to make the gap disappear."]
    ))

    slides.append(bullets_slide(
        "The case study shows the agent doing research work",
        ["It keeps a broad objective active across many small turns.",
         "It separates method evidence, proof evidence, paper evidence, and external evidence.",
         "It turns failed probes into structured exclusions.",
         "It creates reviewer-facing artifacts while preserving non-claims."]
    ))

    slides.append(section_slide("5 / Lessons", "What generalizes", "The pipeline is a pattern for agentic research, not only this integrator project."))

    slides.append(bullets_slide(
        "Design pattern: artifact-grounded autonomy",
        ["Use a current contract file as the first read on every turn.",
         "Represent claims as JSON/Markdown gates with validators.",
         "Store evidence in small, typed artifacts: CSV, JSON, PNG, reports.",
         "Make expensive or policy-sensitive commands opt-in.",
         "Treat negative evidence as part of the result."]
    ))

    slides.append(two_col_slide(
        "What the agent should do",
        "Autonomous",
        ["Read current state.",
         "Select the next missing gate.",
         "Run bounded checks.",
         "Generate artifacts.",
         "Summarize evidence and non-evidence."],
        "Human-controlled",
        ["Change the research objective.",
         "Approve strict source-policy campaigns.",
         "Decide when a narrowed claim is worth submitting.",
         "Accept broader claim promotion."]
    ))

    slides.append(bullets_slide(
        "What we would improve next",
        ["A smaller domain-specific language for claim gates.",
         "Better automatic figure and table generation from JSON ledgers.",
         "Subagent review roles for proof, numerical policy, and paper package audits.",
         "Cost-aware scheduling for external same-test campaigns.",
         "A compact dashboard that shows accepted, diagnostic, open, and forbidden claims."]
    ))

    slides.append(statement_slide(
        "Conclusion",
        ["The agent is not a magic scientist.", "It is a disciplined research operating system."],
        ["Its leverage comes from durable artifacts, validators, and conservative claim boundaries.",
         "The v047/v048 project shows that this can sustain months of technical search.",
         "The same pattern can be reused wherever research progress depends on evidence hygiene."]
    ))

    thanks = Slide("", kind="title", show_footer=False)
    thanks.texts.extend([
        TextBox(["Thank You"], 760_000, 1_570_000, 10_500_000, 850_000, 44, DARK, True, align="ctr", name="Thanks"),
        TextBox(["Questions?"], 760_000, 2_750_000, 10_500_000, 760_000, 32, RED, True, align="ctr", name="Questions"),
        TextBox(["Meta claim: autonomous research becomes reliable when claims are executable artifacts"],
                1_050_000, 4_360_000, 10_000_000, 500_000, 18, MUTED, align="ctr", name="Closing note"),
    ])
    slides.append(thanks)

    return slides


def core_xml() -> str:
    now = datetime(2026, 6, 9, 17, 30, 0, tzinfo=timezone.utc).isoformat().replace("+00:00", "Z")
    return (
        "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>"
        "<cp:coreProperties xmlns:cp=\"http://schemas.openxmlformats.org/package/2006/metadata/core-properties\" "
        "xmlns:dc=\"http://purl.org/dc/elements/1.1/\" "
        "xmlns:dcterms=\"http://purl.org/dc/terms/\" "
        "xmlns:dcmitype=\"http://purl.org/dc/dcmitype/\" "
        "xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\">"
        "<dc:title>Artifact-Grounded Auto-Research Agent Meta Slides</dc:title>"
        "<dc:creator>Codex</dc:creator>"
        "<cp:lastModifiedBy>Codex</cp:lastModifiedBy>"
        f"<dcterms:created xsi:type=\"dcterms:W3CDTF\">{now}</dcterms:created>"
        f"<dcterms:modified xsi:type=\"dcterms:W3CDTF\">{now}</dcterms:modified>"
        "</cp:coreProperties>"
    )


def build() -> None:
    slides = build_meta_slides()
    image_media: dict[Path, str] = {}
    for slide in slides:
        for im in slide.images:
            if im.path not in image_media:
                image_media[im.path] = f"meta_image{len(image_media) + 1}.png"

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
        expected = len(build_meta_slides())
        if len(slides) != expected:
            raise RuntimeError(f"Expected {expected} slides, found {len(slides)}")
        missing_rels = []
        for s in slides:
            idx = re.search(r"slide(\d+)\.xml", s).group(1)
            rel = f"ppt/slides/_rels/slide{idx}.xml.rels"
            if rel not in names:
                missing_rels.append(rel)
        if missing_rels:
            raise RuntimeError(f"Missing slide rels: {missing_rels[:5]}")
        print(f"Wrote {OUT.name} with {len(slides)} slides and {len([n for n in names if n.startswith('ppt/media/meta_image')])} embedded figures.")


if __name__ == "__main__":
    build()
    validate_package()
