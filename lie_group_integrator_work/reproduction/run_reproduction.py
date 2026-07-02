#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import math
import subprocess
import sys
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
OUT_DEFAULT = Path(__file__).resolve().parent / "outputs"

PAPER_MATRIX = ROOT / "paper_v047_cylindrical_chain" / "PAPER_NUMERICAL_RESULT_MATRIX.csv"
CLAIM_BOUNDARY = ROOT / "paper_v047_cylindrical_chain" / "CLAIM_BOUNDARY.json"
V047_SUMMARY = ROOT / "v047_cylindrical_chain_pipeline" / "results" / "summary_v047.json"
V048_SUMMARY = ROOT / "v048_cross_paper_same_test_benchmarks" / "results" / "summary_v048.json"

WORK_PRECISION_SOURCES = [
    ROOT
    / "v048_cross_paper_same_test_benchmarks"
    / "results"
    / "single_pendulum_coarse_same_window_work_precision_summary.csv",
    ROOT
    / "v048_cross_paper_same_test_benchmarks"
    / "results"
    / "double_pendulum_coarse_same_window_work_precision_summary.csv",
    ROOT
    / "v048_cross_paper_same_test_benchmarks"
    / "results"
    / "closed_loop_true_dynamic_strict_common_reference_summary.csv",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise RuntimeError(f"{path} has no CSV header")
        return list(reader)


def read_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise RuntimeError(f"{path} is not a JSON object")
    return data


def write_csv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def split_filter(value: str | None) -> set[str] | None:
    if not value:
        return None
    return {part.strip() for part in value.split(",") if part.strip()}


def keep_row(row: dict[str, str], examples: set[str] | None, methods: set[str] | None) -> bool:
    if examples and row.get("example", row.get("model", "")) not in examples:
        return False
    if methods and row.get("method", "") not in methods:
        return False
    return True


def format_value(value: object) -> str:
    if value is None:
        return ""
    text = str(value)
    if text == "":
        return ""
    try:
        number = float(text)
    except ValueError:
        return text
    if math.isnan(number):
        return "nan"
    if math.isinf(number):
        return "inf" if number > 0 else "-inf"
    if number == 0:
        return "0"
    if abs(number) >= 1.0e4 or abs(number) < 1.0e-3:
        return f"{number:.3e}"
    return f"{number:.3f}"


def markdown_table(rows: list[dict[str, object]], fields: list[str]) -> str:
    if not rows:
        return "_No rows selected._\n"
    lines = []
    lines.append("| " + " | ".join(fields) + " |")
    lines.append("| " + " | ".join("---" for _ in fields) + " |")
    for row in rows:
        values = [format_value(row.get(field, "")).replace("|", "\\|") for field in fields]
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines) + "\n"


def normalize_paper_matrix(
    examples: set[str] | None,
    methods: set[str] | None,
) -> list[dict[str, object]]:
    rows = []
    for row in read_csv(PAPER_MATRIX):
        if not keep_row(row, examples, methods):
            continue
        rows.append(
            {
                "example": row.get("example", ""),
                "method": row.get("method", ""),
                "family": row.get("family", ""),
                "status": row.get("status", ""),
                "source_level": row.get("source_level", ""),
                "h_values": row.get("h_values", ""),
                "t_end": row.get("t_end", ""),
                "reference_h": row.get("reference_h", ""),
                "pos_order": row.get("position_order", ""),
                "vel_order": row.get("velocity_order", ""),
                "acc_order": row.get("acceleration_order", ""),
                "finest_pos_error": row.get("finest_position_error", ""),
                "finest_vel_error": row.get("finest_velocity_error", ""),
                "finest_acc_error": row.get("finest_acceleration_error", ""),
                "paper_claim_scope": row.get("paper_claim_scope", ""),
                "source_policy_closed": row.get("source_policy_closed", ""),
            }
        )
    return rows


def normalize_work_precision(
    examples: set[str] | None,
    methods: set[str] | None,
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for source in WORK_PRECISION_SOURCES:
        for row in read_csv(source):
            model = row.get("model", row.get("example", ""))
            method = row.get("method", "")
            synthetic = {"example": model, "method": method}
            if not keep_row(synthetic, examples, methods):
                continue
            rows.append(
                {
                    "example": model,
                    "method": method,
                    "policy": row.get("policy", source.stem),
                    "source_suite": row.get("source_suite", ""),
                    "row_count": row.get("row_count", ""),
                    "ok_count": row.get("ok_row_count", ""),
                    "t_end": row.get("t_end", ""),
                    "reference_h": row.get("reference_h", row.get("common_reference_h", "")),
                    "finest_h": row.get("finest_h", ""),
                    "pos_order": row.get("pos_observed_order", ""),
                    "vel_order": row.get("vel_observed_order", ""),
                    "acc_order": row.get("acc_observed_order", row.get("acc_or_omega_observed_order", "")),
                    "finest_pos_error": row.get("finest_pos_error", row.get("finest_pos_final_linf", "")),
                    "finest_vel_error": row.get("finest_vel_error", row.get("finest_vel_final_linf", "")),
                    "finest_acc_error": row.get(
                        "finest_acc_error",
                        row.get("finest_acc_or_omega_error", row.get("finest_acc_final_linf", "")),
                    ),
                    "runtime_sec_sum": row.get("runtime_sec_sum", ""),
                    "finest_runtime_ratio_vs_rA": row.get(
                        "finest_runtime_ratio_vs_rA",
                        row.get("finest_runtime_ratio_vs_public_rA", ""),
                    ),
                    "accepted_dynamic_order": row.get("accepted_dynamic_order", ""),
                    "external_superiority_claim_allowed": row.get("external_superiority_claim_allowed", ""),
                    "source_file": str(source.relative_to(ROOT)),
                }
            )
    return rows


def run_checks() -> list[dict[str, object]]:
    commands = [
        (
            "paper numerical matrix",
            ROOT / "paper_v047_cylindrical_chain",
            [sys.executable, "validate_paper_numerical_result_matrix.py"],
        ),
        (
            "v047 four-ASME minimal",
            ROOT / "v047_cylindrical_chain_pipeline",
            [sys.executable, "validate_four_asme_minimal.py"],
        ),
        (
            "v048 performance matrix",
            ROOT / "v048_cross_paper_same_test_benchmarks",
            [sys.executable, "validate_four_example_performance_matrix.py"],
        ),
        (
            "v048 strict common reference",
            ROOT / "v048_cross_paper_same_test_benchmarks",
            [sys.executable, "validate_closed_loop_true_dynamic_strict_common_reference.py"],
        ),
    ]
    results = []
    for label, cwd, command in commands:
        proc = subprocess.run(
            command,
            cwd=cwd,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        results.append(
            {
                "label": label,
                "returncode": proc.returncode,
                "status": "PASS" if proc.returncode == 0 else "FAIL",
                "output": proc.stdout.strip(),
            }
        )
    return results


def count_by(rows: Iterable[dict[str, object]], field: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        key = str(row.get(field, ""))
        counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items()))


def build_report(
    paper_rows: list[dict[str, object]],
    work_rows: list[dict[str, object]],
    manifest: dict,
    check_results: list[dict[str, object]],
) -> str:
    claim = manifest["claim_boundary"].get("primary_claim", {})
    lines = [
        "# Human-Runnable Reproduction Report",
        "",
        "## Claim Boundary",
        "",
        f"- Accepted method: `{claim.get('accepted_method', 'Gauss6/FullVA')}`",
        f"- Method-order claim: `{claim.get('method_order_claim', 6)}`",
        f"- ASME gate status: `{claim.get('asme_gate_status', '')}`",
        f"- `full_tfe_stage_replacement`: `{manifest['full_tfe_stage_replacement']}`",
        f"- `same_test_campaign_status`: `{manifest['same_test_campaign_status']}`",
        f"- `external_superiority_claim`: `{manifest['external_superiority_claim']}`",
        "",
        "## Rebuilt Tables",
        "",
        f"- Paper method/example matrix rows: `{len(paper_rows)}`",
        f"- Work-precision summary rows: `{len(work_rows)}`",
        f"- Examples in matrix: `{', '.join(count_by(paper_rows, 'example'))}`",
        f"- Methods in matrix: `{', '.join(count_by(paper_rows, 'method'))}`",
        "",
        "## Outputs",
        "",
        "- `method_example_matrix.csv` / `.md`",
        "- `work_precision_summary.csv` / `.md`",
        "- `reproduction_manifest.json`",
        "",
        "## Validation",
        "",
    ]
    if not check_results:
        lines.append("Checks were not requested. Re-run with `--check` for read-only validators.")
    else:
        for result in check_results:
            lines.append(f"- `{result['label']}`: `{result['status']}`")
    lines.extend(
        [
            "",
            "## Scope Notes",
            "",
            "- This command rebuilds human-readable result summaries from existing checked artifacts.",
            "- It does not invoke `v047_cylindrical_chain_pipeline/run_v047.py`.",
            "- It does not run strict public-policy `1e-4` campaigns.",
            "- It does not upgrade any open claim gate.",
            "",
        ]
    )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Rebuild human-readable multi-method/multi-example reproduction summaries.",
    )
    parser.add_argument("--outdir", type=Path, default=OUT_DEFAULT, help="Directory for rebuilt tables and report.")
    parser.add_argument("--examples", help="Comma-separated example filter, e.g. single_pendulum,double_pendulum.")
    parser.add_argument("--methods", help="Comma-separated method filter using exact method labels.")
    parser.add_argument("--check", action="store_true", help="Run read-only validators after rebuilding summaries.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    examples = split_filter(args.examples)
    methods = split_filter(args.methods)
    outdir = args.outdir if args.outdir.is_absolute() else ROOT / args.outdir

    claim_boundary = read_json(CLAIM_BOUNDARY)
    v047_summary = read_json(V047_SUMMARY)
    v048_summary = read_json(V048_SUMMARY)

    paper_rows = normalize_paper_matrix(examples, methods)
    work_rows = normalize_work_precision(examples, methods)

    paper_fields = [
        "example",
        "method",
        "family",
        "status",
        "source_level",
        "h_values",
        "t_end",
        "reference_h",
        "pos_order",
        "vel_order",
        "acc_order",
        "finest_pos_error",
        "finest_vel_error",
        "finest_acc_error",
        "paper_claim_scope",
        "source_policy_closed",
    ]
    work_fields = [
        "example",
        "method",
        "policy",
        "source_suite",
        "row_count",
        "ok_count",
        "t_end",
        "reference_h",
        "finest_h",
        "pos_order",
        "vel_order",
        "acc_order",
        "finest_pos_error",
        "finest_vel_error",
        "finest_acc_error",
        "runtime_sec_sum",
        "finest_runtime_ratio_vs_rA",
        "accepted_dynamic_order",
        "external_superiority_claim_allowed",
        "source_file",
    ]

    write_csv(outdir / "method_example_matrix.csv", paper_rows, paper_fields)
    write_text(outdir / "method_example_matrix.md", markdown_table(paper_rows, paper_fields))
    write_csv(outdir / "work_precision_summary.csv", work_rows, work_fields)
    write_text(outdir / "work_precision_summary.md", markdown_table(work_rows, work_fields))

    check_results = run_checks() if args.check else []
    failed_checks = [result for result in check_results if result["returncode"] != 0]

    manifest = {
        "schema": "human-runnable-reproduction-v1",
        "root": str(ROOT),
        "sources": {
            "paper_matrix": str(PAPER_MATRIX.relative_to(ROOT)),
            "claim_boundary": str(CLAIM_BOUNDARY.relative_to(ROOT)),
            "v047_summary": str(V047_SUMMARY.relative_to(ROOT)),
            "v048_summary": str(V048_SUMMARY.relative_to(ROOT)),
            "work_precision_sources": [str(path.relative_to(ROOT)) for path in WORK_PRECISION_SOURCES],
        },
        "outputs": {
            "method_example_matrix_csv": str((outdir / "method_example_matrix.csv").relative_to(ROOT)),
            "method_example_matrix_md": str((outdir / "method_example_matrix.md").relative_to(ROOT)),
            "work_precision_summary_csv": str((outdir / "work_precision_summary.csv").relative_to(ROOT)),
            "work_precision_summary_md": str((outdir / "work_precision_summary.md").relative_to(ROOT)),
            "report": str((outdir / "reproduction_report.md").relative_to(ROOT)),
        },
        "filters": {
            "examples": sorted(examples) if examples else "all",
            "methods": sorted(methods) if methods else "all",
        },
        "counts": {
            "paper_matrix_rows": len(paper_rows),
            "work_precision_rows": len(work_rows),
            "paper_matrix_examples": count_by(paper_rows, "example"),
            "paper_matrix_methods": count_by(paper_rows, "method"),
            "work_precision_examples": count_by(work_rows, "example"),
            "work_precision_methods": count_by(work_rows, "method"),
        },
        "claim_boundary": claim_boundary,
        "full_tfe_stage_replacement": bool(
            claim_boundary.get("full_tfe_stage_replacement", v047_summary.get("full_tfe_stage_replacement", False))
        ),
        "same_test_campaign_status": v048_summary.get("same_test_campaign_status", "not_run"),
        "external_superiority_claim": bool(v048_summary.get("external_superiority_claim", False)),
        "checks_requested": bool(args.check),
        "checks": check_results,
    }
    write_text(outdir / "reproduction_report.md", build_report(paper_rows, work_rows, manifest, check_results))
    write_json(outdir / "reproduction_manifest.json", manifest)

    print(f"wrote {outdir / 'method_example_matrix.csv'}")
    print(f"wrote {outdir / 'work_precision_summary.csv'}")
    print(f"wrote {outdir / 'reproduction_report.md'}")
    if args.check:
        for result in check_results:
            print(f"{result['label']}: {result['status']}")
    if failed_checks:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
