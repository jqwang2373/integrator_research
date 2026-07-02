#!/usr/bin/env python3
"""Build a machine-readable coverage matrix for the current same-grid baselines."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
COARSE_SUMMARY_CSV = RESULTS / "coarse_four_example_order_summary.csv"
VP_SEARCH_CSV = RESULTS / "velocity_partitioning_code_search.csv"
TFE_M3_SMOKE_CSV = RESULTS / "tfe_m3_four_link_common_reference_smoke.csv"
LARGE_STEP_VP_JSON = RESULTS / "large_step_vp_local_order_summary.json"
ERROR_REFERENCE_POLICY_JSON = RESULTS / "error_reference_policy_audit.json"
VP_METHOD_IDENTITY_JSON = RESULTS / "vp_method_identity_audit.json"
TFE_M3_SCOPE_JSON = RESULTS / "tfe_m3_scope_exclusion_audit.json"
ALL_EXAMPLES_FORENSIC_JSON = RESULTS / "all_examples_apples_to_apples_forensic_audit.json"
OUT_CSV = RESULTS / "baseline_coverage_matrix.csv"
OUT_JSON = RESULTS / "baseline_coverage_matrix.json"
OUT_MD = RESULTS / "baseline_coverage_matrix.md"
EXAMPLES = ("single_pendulum", "double_pendulum", "four_link", "slider_crank")


METHOD_SOURCE = {
    "local_Gauss6_FullVA": (
        "local proposed method",
        "implemented_local",
        "primary method under test",
    ),
    "ra2021_rA": (
        "Kissel/Taves/Negrut 2021-2022 public rA code",
        "public_code_present",
        "Kissel-Negrut baseline",
    ),
    "ra2021_rp": (
        "Kissel/Taves/Negrut 2021-2022 public rp code",
        "public_code_present",
        "Kissel-Negrut baseline",
    ),
    "ra2021_reps": (
        "Kissel/Taves/Negrut 2021-2022 public r-epsilon code",
        "public_code_present",
        "Kissel-Negrut baseline",
    ),
    "hi2022_rA": (
        "Fang/Kissel/Zhang/Negrut 2022 half-implicit public suite",
        "public_code_present",
        "Kissel-Negrut-related baseline",
    ),
    "hi2022_rA_half": (
        "Fang/Kissel/Zhang/Negrut 2022 half-implicit public suite",
        "public_code_present",
        "Kissel-Negrut-related baseline",
    ),
    "tfe2026_Newmark_beta": (
        "original TFE paper Algorithm 2 wrapper on 2021 rA geometry",
        "paper_formula_wrapped",
        "original-paper baseline",
    ),
    "tfe2026_trapezoidal": (
        "original TFE paper Algorithm 2 wrapper on 2021 rA geometry",
        "paper_formula_wrapped",
        "original-paper baseline",
    ),
    "tfe2026_TFE_m1": (
        "original TFE paper Appendix B m=1 wrapper",
        "paper_formula_wrapped",
        "original-paper baseline",
    ),
    "tfe2026_TFE_m2": (
        "original TFE paper Appendix B m=2 wrapper",
        "paper_formula_wrapped",
        "original-paper baseline",
    ),
    "tfe2026_TFE_m3_GL": (
        "original TFE paper Appendix B m=3 Gauss-Lobatto wrapper",
        "paper_formula_wrapped_scope_excluded_on_four_link",
        "original-paper diagnostic row outside required four-example matrix",
    ),
    "vp2024_coordinate_partitioning_rA": (
        "Kissel/Bakke/Negrut 2024 coordinate partitioning reimplementation",
        "local_reimplementation_from_published_algorithm",
        "velocity-partitioning baseline subset",
    ),
    "vp2024_lie_group_ode_partitioning": (
        "Kissel/Bakke/Negrut 2024 Lie-group ODE partitioning",
        "method_alias_resolved",
        "velocity-partitioning alias of implemented coordinate-partitioning wrapper",
    ),
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"refusing to write empty {path.name}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def method_status(method: str, statuses: list[str], ok_examples: list[str]) -> str:
    if method == "tfe2026_TFE_m3_GL":
        return "scope_excluded_after_rejected_four_link"
    if method == "vp2024_lie_group_ode_partitioning":
        return "alias_resolved_to_vp2024_coordinate_partitioning_rA"
    if len(ok_examples) == len(EXAMPLES) and all(status == "ok" for status in statuses):
        return "accepted_same_grid_four_examples"
    return "incomplete"


def notes_for(method: str) -> str:
    if method == "tfe2026_TFE_m3_GL":
        return (
            "single/double/slider rows run; four_link is source-backed excluded because the original "
            "paper's numerical scope is a single revolute-pendulum study, the paper reports DAE order "
            "loss for m=3, and the local four-link stress row gives negative common-reference orders"
        )
    if method == "vp2024_lie_group_ode_partitioning":
        return (
            "resolved by method-identity audit: ASME/Crossref metadata for DOI 10.1115/DETC2023-116950 "
            "describes the same coordinate-partitioning Lie-group ODE method implemented as "
            "vp2024_coordinate_partitioning_rA"
        )
    if method == "vp2024_coordinate_partitioning_rA":
        return (
            "runs all four examples; local velocity order wins on both the main coarse grid and "
            "the larger-step diagnostic audit, but VP has the smaller finest-step velocity error "
            "on three of four larger-step rows"
        )
    if method == "local_Gauss6_FullVA":
        return "local method; current main claim is velocity-order superiority"
    return "runs all four examples on the shared coarse h trio"


def main() -> None:
    summary_rows = read_csv(COARSE_SUMMARY_CSV)
    vp_rows = read_csv(VP_SEARCH_CSV)
    tfe_rows = read_csv(TFE_M3_SMOKE_CSV)
    large_step_vp = {}
    if LARGE_STEP_VP_JSON.exists():
        with LARGE_STEP_VP_JSON.open(encoding="utf-8") as handle:
            large_step_vp = json.load(handle)
    error_reference_policy = {}
    if ERROR_REFERENCE_POLICY_JSON.exists():
        with ERROR_REFERENCE_POLICY_JSON.open(encoding="utf-8") as handle:
            error_reference_policy = json.load(handle)
    vp_identity = {}
    if VP_METHOD_IDENTITY_JSON.exists():
        with VP_METHOD_IDENTITY_JSON.open(encoding="utf-8") as handle:
            vp_identity = json.load(handle)
    tfe_m3_scope = {}
    if TFE_M3_SCOPE_JSON.exists():
        with TFE_M3_SCOPE_JSON.open(encoding="utf-8") as handle:
            tfe_m3_scope = json.load(handle)
    all_examples_forensic = {}
    if ALL_EXAMPLES_FORENSIC_JSON.exists():
        with ALL_EXAMPLES_FORENSIC_JSON.open(encoding="utf-8") as handle:
            all_examples_forensic = json.load(handle)

    rows: list[dict[str, object]] = []
    by_method: dict[str, list[dict[str, str]]] = {}
    for row in summary_rows:
        by_method.setdefault(row["method"], []).append(row)

    for method in sorted(by_method):
        method_rows = by_method[method]
        family = method_rows[0]["family"]
        statuses = [row["status"] for row in method_rows]
        ok_examples = sorted(row["example"] for row in method_rows if row["status"] == "ok")
        non_ok = sorted(f"{row['example']}:{row['status']}" for row in method_rows if row["status"] != "ok")
        source_label, source_status, comparison_role = METHOD_SOURCE.get(
            method,
            ("unclassified", "unclassified", "unclassified"),
        )
        rows.append(
            {
                "family": family,
                "method": method,
                "comparison_role": comparison_role,
                "implementation_status": method_status(method, statuses, ok_examples),
                "source_status": source_status,
                "ok_examples": "|".join(ok_examples) if ok_examples else "none",
                "ok_example_count": len(ok_examples),
                "required_example_count": len(EXAMPLES),
                "non_ok_examples": "|".join(non_ok) if non_ok else "none",
                "shared_step_sizes": "0.1|0.05|0.025",
                "reference_h": "0.0125",
                "source_label": source_label,
                "primary_evidence": method_rows[0]["evidence"],
                "notes": notes_for(method),
            }
        )

    complete_methods = [row for row in rows if row["implementation_status"] == "accepted_same_grid_four_examples"]
    unresolved_methods = [row for row in rows if row["implementation_status"] == "source_unresolved_not_run"]
    rejected_methods = [row for row in rows if row["implementation_status"] == "partial_rejected_four_link"]
    scope_excluded_methods = [row for row in rows if row["implementation_status"].startswith("scope_excluded")]
    alias_methods = [row for row in rows if row["implementation_status"].startswith("alias_resolved")]
    required_complete_methods = complete_methods + alias_methods + scope_excluded_methods
    summary = {
        "schema": "baseline-coverage-matrix-v1",
        "row_count": len(rows),
        "accepted_same_grid_four_example_methods": len(complete_methods),
        "implemented_or_alias_resolved_methods": len(complete_methods) + len(alias_methods),
        "required_methods_resolved_count": len(required_complete_methods),
        "required_methods_resolved": len(required_complete_methods) == len(rows),
        "source_unresolved_methods": [row["method"] for row in unresolved_methods],
        "alias_resolved_methods": [row["method"] for row in alias_methods],
        "scope_excluded_methods": [row["method"] for row in scope_excluded_methods],
        "vp_method_identity_alias_resolved": vp_identity.get("alias_resolved", False),
        "vp_method_identity_implemented_as": vp_identity.get("implemented_method", ""),
        "tfe_m3_scope_exclusion_source_backed": tfe_m3_scope.get("source_backed_exclusion", False),
        "tfe_m3_required_accepted_matrix_excludes_method": tfe_m3_scope.get(
            "required_accepted_matrix_excludes_method",
            False,
        ),
        "rejected_partial_methods": [row["method"] for row in rejected_methods],
        "vp_code_search_rows": len(vp_rows),
        "tfe_m3_four_link_smoke_rows": len(tfe_rows),
        "vp_large_step_comparable_examples": large_step_vp.get("comparable_examples", 0),
        "vp_large_step_local_velocity_order_wins": large_step_vp.get("local_velocity_order_wins", 0),
        "vp_large_step_local_finest_velocity_error_wins": large_step_vp.get(
            "local_finest_velocity_error_wins",
            0,
        ),
        "observed_order_comparable_rows": error_reference_policy.get("observed_order_comparable_rows", 0),
        "direct_error_vs_local_comparable_rows": error_reference_policy.get(
            "direct_error_vs_local_comparable_rows",
            0,
        ),
        "common_reference_local_velocity_order_wins": error_reference_policy.get(
            "common_reference_local_velocity_order_wins",
            0,
        ),
        "common_reference_local_finest_velocity_error_wins": error_reference_policy.get(
            "common_reference_local_finest_velocity_error_wins",
            0,
        ),
        "common_reference_direct_error_superiority_claim": error_reference_policy.get(
            "common_reference_direct_error_superiority_claim",
            False,
        ),
        "paper_direct_error_superiority_claim_allowed": all_examples_forensic.get(
            "direct_error_superiority_claim_allowed_for_paper",
            False,
        ),
        "source_policy_reproduction": all_examples_forensic.get("source_policy_reproduction", False),
        "external_superiority_claim_allowed": all_examples_forensic.get(
            "external_superiority_claim_allowed",
            False,
        ),
        "claim_boundary": (
            "local velocity order can be compared against finite runnable rows; "
            "main-matrix reported velocity errors use heterogeneous reference policies, but "
            "the separate common-reference audit supplies bounded direct final-state velocity-error "
            "diagnostics for accepted runnable methods; the all-example forensic audit blocks "
            "paper-level direct error superiority until source-policy reproduction is closed; "
            "the VP Lie-group ODE label is resolved as an alias of the implemented VP coordinate-"
            "partitioning wrapper; TFE(m=3) four-link is a source-backed excluded stress row rather "
            "than a required accepted baseline"
        ),
    }

    write_csv(OUT_CSV, rows)
    with OUT_JSON.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, sort_keys=True)
        handle.write("\n")

    lines = [
        "# Baseline Coverage Matrix",
        "",
        f"Accepted same-grid four-example methods: `{summary['accepted_same_grid_four_example_methods']}`.",
        f"Implemented or alias-resolved methods: `{summary['implemented_or_alias_resolved_methods']}`.",
        f"Required methods resolved: `{summary['required_methods_resolved_count']}/{summary['row_count']}`.",
        f"Source-unresolved methods: `{', '.join(summary['source_unresolved_methods']) or 'none'}`.",
        f"Alias-resolved methods: `{', '.join(summary['alias_resolved_methods']) or 'none'}`.",
        f"Scope-excluded methods: `{', '.join(summary['scope_excluded_methods']) or 'none'}`.",
        f"Rejected partial methods: `{', '.join(summary['rejected_partial_methods']) or 'none'}`.",
        f"VP larger-step local velocity-order wins: `{summary['vp_large_step_local_velocity_order_wins']}/{summary['vp_large_step_comparable_examples']}`.",
        f"VP larger-step local reported finest-velocity-error wins: `{summary['vp_large_step_local_finest_velocity_error_wins']}/{summary['vp_large_step_comparable_examples']}`.",
        f"Direct error-vs-local comparable rows: `{summary['direct_error_vs_local_comparable_rows']}`.",
        f"Common-reference local velocity-order wins: `{summary['common_reference_local_velocity_order_wins']}/{summary['direct_error_vs_local_comparable_rows']}`.",
        f"Common-reference local finest-velocity-error wins: `{summary['common_reference_local_finest_velocity_error_wins']}/{summary['direct_error_vs_local_comparable_rows']}`.",
        f"Bounded common-reference direct error diagnostic: `{summary['common_reference_direct_error_superiority_claim']}`.",
        f"Paper-level direct error superiority allowed: `{summary['paper_direct_error_superiority_claim_allowed']}`.",
        f"Source-policy reproduction: `{summary['source_policy_reproduction']}`.",
        "",
        "| Method | status | ok examples | non-ok examples | source status | role |",
        "|---|---|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            "| "
            f"`{row['method']}` | `{row['implementation_status']}` | `{row['ok_examples']}` | "
            f"`{row['non_ok_examples']}` | `{row['source_status']}` | {row['comparison_role']} |"
        )
    lines.extend(
        [
            "",
            "Claim boundary: local velocity order can be compared against finite runnable rows. "
            "The main matrix's reported velocity errors use heterogeneous reference policies; the "
            "separate common-reference audit supplies bounded final-state velocity-error diagnostics "
            "for accepted runnable methods, but paper-level direct error superiority is blocked by "
            "the all-example forensic audit. The VP Lie-group ODE label is resolved as an alias of the "
            "implemented VP coordinate-partitioning wrapper. TFE(m=3) four-link is a source-backed "
            "excluded stress row rather than a required accepted baseline.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("baseline_coverage_matrix=written")
    print(f"rows={summary['row_count']}")
    print(f"accepted_same_grid_four_example_methods={summary['accepted_same_grid_four_example_methods']}")
    print(f"source_unresolved_methods={','.join(summary['source_unresolved_methods'])}")
    print(f"rejected_partial_methods={','.join(summary['rejected_partial_methods'])}")


if __name__ == "__main__":
    main()
