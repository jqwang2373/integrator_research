#!/usr/bin/env python3
"""Audit whether the paper-core result consolidation is visible in TeX/PDF."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
OUT_JSON = PAPER / "PAPER_CORE_TO_MANUSCRIPT_AUDIT.json"
OUT_MD = PAPER / "PAPER_CORE_TO_MANUSCRIPT_AUDIT.md"


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def normalize(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [line for line in text.split("\n") if not re.fullmatch(r"\s*\d+\s*", line)]
    text = "\n".join(lines)
    text = re.sub(r"([A-Za-z])-+\s*\n\s*([A-Za-z])", r"\1\2", text)
    text = text.replace("−", "-").replace("–", "-").replace("—", "-")
    text = text.replace("\\", " ")
    text = re.sub(r"\s+", " ", text)
    return text


def contains_any(text: str, tokens: list[str]) -> bool:
    normalized = normalize(text)
    return any(normalize(token) in normalized for token in tokens)


def token_row(label: str, tex_tokens: list[str], pdf_tokens: list[str], tex: str, pdf: str) -> dict[str, object]:
    return {
        "label": label,
        "tex_present": contains_any(tex, tex_tokens),
        "pdf_present": contains_any(pdf, pdf_tokens),
        "tex_tokens": tex_tokens,
        "pdf_tokens": pdf_tokens,
    }


def main() -> None:
    core = read_json(PAPER / "PAPER_CORE_RESULT_CONSOLIDATION.json")
    tex = read_text(PAPER / "main_cmame.tex")
    pdf = read_text(PAPER / "main_cmame.txt")
    flat_tex = read_text(PAPER / "cmame_submission_flat" / "main_cmame_submission.tex")
    flat_pdf = read_text(PAPER / "cmame_submission_flat" / "main_cmame_submission.txt")

    token_rows = [
        token_row(
            "single_pendulum_order_error",
            ["Single pendulum & 5.801", "5.801 / $1.155\\times10^{-12}$"],
            ["Single pendulum 5.801", "5.801 / 1.155"],
            tex,
            pdf,
        ),
        token_row(
            "double_pendulum_order_error",
            ["Double pendulum & 6.010", "6.010 / $2.346\\times10^{-13}$"],
            ["Double pendulum 6.010", "6.010 / 2.346"],
            tex,
            pdf,
        ),
        token_row(
            "four_link_order_error",
            ["Four-link & 6.085", "6.085 / $1.093\\times10^{-11}$"],
            ["Four-link 6.085", "6.085 / 1.093"],
            tex,
            pdf,
        ),
        token_row(
            "slider_crank_order_error",
            ["Slider-crank & 7.341", "7.341 / $9.189\\times10^{-12}$"],
            ["Slider-crank 7.341", "7.341 / 9.189"],
            tex,
            pdf,
        ),
        token_row(
            "closed_loop_four_link_true_dynamic",
            ["Four-link primary-state orders $5.955/5.955/6.085/5.971$", "position/velocity order $5.955/6.085$"],
            ["5.955/5.955/6.085/5.971", "position/velocity order 5.955/6.085"],
            tex,
            pdf,
        ),
        token_row(
            "closed_loop_slider_crank_true_dynamic",
            ["slider-crank orders $6.164/6.159/7.341/6.426$", "position/velocity order $6.164/7.341$"],
            ["6.164/6.159/7.341/6.426", "position/velocity order 6.164/7.341"],
            tex,
            pdf,
        ),
        token_row(
            "source_policy_boundary",
            [
                "no source-policy-closed external same-test error row is established",
                "Strict external error-claim rows & 0",
            ],
            [
                "no source-policy-closed external same-test error row is established",
                "strict external error-claim rows",
            ],
            tex,
            pdf,
        ),
    ]

    structure_rows = [
        token_row(
            "common_reference_pack_table",
            ["\\label{tab:common-reference-pack}", "Bounded common-reference velocity evidence"],
            ["Bounded common-reference velocity evidence"],
            tex,
            pdf,
        ),
        token_row(
            "all_method_matrix_table",
            ["\\label{tab:common-reference-all-methods}", "All runnable common-reference velocity rows"],
            ["All runnable common-reference velocity rows"],
            tex,
            pdf,
        ),
        token_row(
            "strict_common_reference_figure",
            ["\\label{fig:strict-common-reference}", "Strict common-reference work/precision rows"],
            ["Strict common-reference work/precision rows"],
            tex,
            pdf,
        ),
        token_row(
            "closed_loop_true_dynamic_figure",
            ["\\label{fig:closed-loop-true-dynamic-order}", "Closed-loop coarse-dynamics diagnostic evidence"],
            ["Closed-loop coarse-dynamics diagnostic evidence"],
            tex,
            pdf,
        ),
        token_row(
            "all_method_result_matrix_figure",
            ["\\label{fig:all-method-result-matrix}", "All-method common-reference result matrix"],
            ["All-method common-reference result matrix"],
            tex,
            pdf,
        ),
    ]

    flat_rows = [
        {
            "label": row["label"],
            "flat_tex_present": contains_any(flat_tex, list(row["tex_tokens"])),
            "flat_pdf_present": contains_any(flat_pdf, list(row["pdf_tokens"])),
        }
        for row in token_rows + structure_rows
    ]

    token_ok = all(row["tex_present"] and row["pdf_present"] for row in token_rows)
    structure_ok = all(row["tex_present"] and row["pdf_present"] for row in structure_rows)
    flat_ok = all(row["flat_tex_present"] and row["flat_pdf_present"] for row in flat_rows)

    result = {
        "schema": "paper-core-to-manuscript-audit-v1",
        "status": "paper_core_results_visible_in_tex_pdf",
        "submission_ready": False,
        "execution_policy": {
            "read_only_existing_artifacts": True,
            "experiments_launched": False,
            "run_v047_invoked": False,
            "run_v048_invoked": False,
        },
        "core_result_status": core.get("status"),
        "paper_core_traceability_closed": token_ok and structure_ok and flat_ok,
        "main_tex_pdf_core_values_present": token_ok,
        "main_tex_pdf_core_structure_present": structure_ok,
        "flat_tex_pdf_core_present": flat_ok,
        "claim_boundary": {
            "allowed_non_policy_core_claim": core.get("claim_boundary", {}).get("allowed_core_claim"),
            "allowed_closed_loop_claim": core.get("claim_boundary", {}).get("allowed_closed_loop_claim"),
            "forbidden_claims": core.get("claim_boundary", {}).get("forbidden_claims", []),
            "submission_ready": False,
        },
        "value_rows": token_rows,
        "structure_rows": structure_rows,
        "flat_rows": flat_rows,
        "source_files": {
            "core_consolidation": "PAPER_CORE_RESULT_CONSOLIDATION.json",
            "main_tex": "main_cmame.tex",
            "main_pdf_text": "main_cmame.txt",
            "flat_tex": "cmame_submission_flat/main_cmame_submission.tex",
            "flat_pdf_text": "cmame_submission_flat/main_cmame_submission.txt",
        },
    }

    with OUT_JSON.open("w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, sort_keys=True)
        handle.write("\n")

    lines = [
        "# Paper Core To Manuscript Audit",
        "",
        "Status: **paper core results visible in TeX/PDF**.",
        "",
        f"- Core result status: `{result['core_result_status']}`.",
        f"- Main TeX/PDF values present: `{result['main_tex_pdf_core_values_present']}`.",
        f"- Main TeX/PDF structure present: `{result['main_tex_pdf_core_structure_present']}`.",
        f"- Flat TeX/PDF core present: `{result['flat_tex_pdf_core_present']}`.",
        f"- Paper-core traceability closed: `{result['paper_core_traceability_closed']}`.",
        f"- Experiments launched: `{result['execution_policy']['experiments_launched']}`.",
        f"- Submission ready: `{result['submission_ready']}`.",
        "",
        "## Value Checks",
        "",
        "| label | main TeX | main PDF |",
        "|---|---:|---:|",
    ]
    for row in token_rows:
        lines.append(f"| `{row['label']}` | `{row['tex_present']}` | `{row['pdf_present']}` |")
    lines.extend(
        [
            "",
            "## Structure Checks",
            "",
            "| label | main TeX | main PDF |",
            "|---|---:|---:|",
        ]
    )
    for row in structure_rows:
        lines.append(f"| `{row['label']}` | `{row['tex_present']}` | `{row['pdf_present']}` |")
    lines.extend(
        [
            "",
            "Reading rule: this audit checks paper visibility for the non-policy core result map. It does not authorize source-policy superiority, proof closure, or submission-ready claims.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("paper_core_to_manuscript_audit=written")
    print(f"paper_core_traceability_closed={result['paper_core_traceability_closed']}")
    print(f"main_values={token_ok}")
    print(f"main_structure={structure_ok}")
    print(f"flat_core={flat_ok}")
    print("experiments_launched=False")


if __name__ == "__main__":
    main()
