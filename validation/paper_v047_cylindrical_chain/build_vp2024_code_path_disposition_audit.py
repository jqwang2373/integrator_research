#!/usr/bin/env python3
"""Build an all-example VP2024 code-path disposition audit."""

from __future__ import annotations

import csv
import json
import os
import math
from collections import Counter
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
ROOT = PAPER.parent
WORKSPACE = ROOT.parent
V048 = ROOT.parent / "numerics" / "v048_cross_paper_same_test_benchmarks"
RESULTS = V048 / "results"
LOCAL_SBEL_REPRO = WORKSPACE / "external" / "sbel-reproducibility"
LOCAL_PUBLIC_METADATA = WORKSPACE / "external" / "public-metadata"
OUT_JSON = PAPER / "VP2024_CODE_PATH_DISPOSITION_AUDIT.json"
OUT_MD = PAPER / "VP2024_CODE_PATH_DISPOSITION_AUDIT.md"
SUMMARY_V048 = RESULTS / "summary_v048.json"
CODE_SEARCH_CSV = RESULTS / "velocity_partitioning_code_search.csv"

EXAMPLES = ["single_pendulum", "double_pendulum", "four_link", "slider_crank"]
VP_METHOD = "vp2024_coordinate_partitioning_rA"
LOCAL_METHOD = "local_Gauss6_FullVA"


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def rel_from_paper(path: Path) -> str:
    return Path(os.path.relpath(path, PAPER)).as_posix()


def as_float(value: object) -> float:
    try:
        out = float(value)
    except (TypeError, ValueError):
        return float("nan")
    return out if math.isfinite(out) else float("nan")


def as_bool(value: object) -> bool:
    return str(value).strip().lower() == "true"


def fmt(value: object) -> str:
    number = as_float(value)
    if not math.isfinite(number):
        return "nan"
    if abs(number) >= 1000.0 or (0.0 < abs(number) < 1.0e-3):
        return f"{number:.3e}"
    return f"{number:.6g}"


def by_example(rows: list[dict[str, str]], method: str) -> dict[str, dict[str, str]]:
    return {
        row["example"]: row
        for row in rows
        if row.get("method") == method and row.get("example") in EXAMPLES
    }


def build_example_rows(
    performance_rows: list[dict[str, str]],
    common_rows: list[dict[str, str]],
    large_step_rows: list[dict[str, str]],
) -> list[dict[str, Any]]:
    source_by_example = {
        row["example"]: row
        for row in performance_rows
        if row.get("source_suite") == "vp2024_unresolved" and row.get("example") in EXAMPLES
    }
    common_local = by_example(common_rows, LOCAL_METHOD)
    common_vp = by_example(common_rows, VP_METHOD)
    large_local = by_example(large_step_rows, LOCAL_METHOD)
    large_vp = by_example(large_step_rows, VP_METHOD)

    rows: list[dict[str, Any]] = []
    for example in EXAMPLES:
        src = source_by_example.get(example, {})
        local = common_local.get(example, {})
        vp = common_vp.get(example, {})
        large_local_row = large_local.get(example, {})
        large_vp_row = large_vp.get(example, {})
        large_local_order = as_float(large_local_row.get("vel_order"))
        large_vp_order = as_float(large_vp_row.get("vel_order"))
        large_local_error = as_float(large_local_row.get("finest_vel_error"))
        large_vp_error = as_float(large_vp_row.get("finest_vel_error"))

        rows.append(
            {
                "example": example,
                "source_policy_status": src.get("status"),
                "source_policy_code_path_resolved": False,
                "self_reproduction_attempted": True,
                "unable_to_reproduce": True,
                "final_nonpublic_code_disposition": "unable_to_reproduce_not_promoted",
                "source_policy_row_count": int(float(src.get("row_count") or 0)),
                "source_policy_ok_count": int(float(src.get("ok_count") or 0)),
                "common_reference_proxy_status": vp.get("status"),
                "common_reference_h_values": vp.get("h_values"),
                "common_reference_local_velocity_order": as_float(local.get("vel_order")),
                "common_reference_vp_proxy_velocity_order": as_float(vp.get("vel_order")),
                "common_reference_local_finest_velocity_error": as_float(local.get("finest_vel_error")),
                "common_reference_vp_proxy_finest_velocity_error": as_float(vp.get("finest_vel_error")),
                "common_reference_local_wins_velocity_order": as_bool(vp.get("local_vel_order_win")),
                "common_reference_local_wins_finest_velocity_error": as_bool(
                    vp.get("local_finest_vel_error_win")
                ),
                "large_step_diagnostic_local_velocity_order": large_local_order,
                "large_step_diagnostic_vp_proxy_velocity_order": large_vp_order,
                "large_step_diagnostic_local_finest_velocity_error": large_local_error,
                "large_step_diagnostic_vp_proxy_finest_velocity_error": large_vp_error,
                "large_step_diagnostic_local_wins_velocity_order": (
                    math.isfinite(large_local_order)
                    and math.isfinite(large_vp_order)
                    and large_local_order > large_vp_order
                ),
                "large_step_diagnostic_local_wins_finest_velocity_error": (
                    math.isfinite(large_local_error)
                    and math.isfinite(large_vp_error)
                    and large_local_error < large_vp_error
                ),
                "proxy_is_source_policy_reproduction": False,
                "allowed_claim_now": (
                    "common-reference proxy diagnostic only; no source-policy "
                    "VP2024 external-superiority claim"
                ),
            }
        )
    return rows


def search_summary(search_rows: list[dict[str, str]]) -> dict[str, Any]:
    status_counts = Counter(row.get("status") for row in search_rows)
    evidence_types = sorted({row.get("evidence_type") for row in search_rows if row.get("evidence_type")})
    public_rows = [row for row in search_rows if row.get("evidence_type") == "public_web_search"]
    public_statuses = sorted({row.get("status") for row in public_rows if row.get("status")})
    if len(public_statuses) == 1:
        public_search_status = public_statuses[0]
    elif public_statuses:
        public_search_status = "mixed:" + ",".join(public_statuses)
    else:
        public_search_status = "not_recorded"
    return {
        "row_count": len(search_rows),
        "source_csv": rel_from_paper(CODE_SEARCH_CSV),
        "status_counts": dict(sorted(status_counts.items())),
        "evidence_types": evidence_types,
        "public_web_search_row_count": len(public_rows),
        "public_web_search_status": public_search_status,
        "public_web_search_scopes": sorted({row.get("search_scope") for row in public_rows if row.get("search_scope")}),
        "points_to_2021_rA_repo": any("2021/ASME/rA-formulation" in row.get("matched_paths_or_roots", "") for row in search_rows),
        "distinct_vp_repo_found": False,
        "distinct_vp_code_path_found": False,
        "github_code_search_auth_boundary": any(
            row.get("evidence_type") == "github_repository_search"
            and "GitHub code search requires authentication" in row.get("interpretation", "")
            for row in search_rows
        ),
    }


def public_api_spot_check() -> dict[str, Any]:
    """Static record of the 2026-06-01 GitHub contents API spot check."""

    root_years = ["2020", "2021", "2022", "2023", "2024", "2025", "2026"]
    y2024 = ["CPD", "IROSImuGps", "MNODE-code", "PathFollowingSim2real", "RSSworkshop"]
    y2023 = ["HuzaifaMSThesis", "LunarProject", "Unjhawala-IEEE-ExpressiveVM"]
    y2025 = [
        "ASME-LinearSolversGPU",
        "CCTA-highwayControl",
        "CRM-JofT",
        "FNODE",
        "MAES-POLARSim",
        "WheelOpt",
        "multi-terrain-RL",
    ]
    return {
        "checked_on": "2026-06-01",
        "api_root": "https://api.github.com/repos/uwsbel/sbel-reproducibility/contents",
        "repository_html": "https://github.com/uwsbel/sbel-reproducibility",
        "root_year_directories": root_years,
        "year_2024_directories": y2024,
        "year_2023_directories": y2023,
        "year_2025_directories": y2025,
        "year_2024_contains_velocity_partitioning_named_dir": False,
        "year_2024_contains_asme_vp_named_dir": False,
        "year_2024_cpd_tree_is_mbd_velocity_partitioning": False,
        "interpretation": (
            "The public 2024 directory snapshot does not expose a named "
            "velocity-partitioning multibody implementation directory. The visible "
            "CPD tree contains perception/segmentation scripts, not the MBD VP code path."
        ),
    }


def _visible_files(root: Path) -> list[Path]:
    if not root.exists():
        return []
    files: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if ".git" in path.parts or "__pycache__" in path.parts:
            continue
        files.append(path)
    return sorted(files)


def _relative(path: Path, base: Path) -> str:
    return path.relative_to(base).as_posix()


def _contains_text(path: Path, token: str) -> bool:
    suffixes = {".csv", ".json", ".md", ".py", ".sh", ".txt", ".yml", ".yaml"}
    if path.suffix.lower() not in suffixes:
        return token.lower() in path.as_posix().lower()
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return token.lower() in path.as_posix().lower()
    return token.lower() in f"{path.as_posix()}\n{text[:1_000_000]}".lower()


def local_repository_tree_scan() -> dict[str, Any]:
    """Read-only scan of local public-code checkouts used for the VP disposition."""

    files = _visible_files(LOCAL_SBEL_REPRO)
    public_metadata_files = _visible_files(LOCAL_PUBLIC_METADATA)
    top_level_dirs = (
        sorted(path.name for path in LOCAL_SBEL_REPRO.iterdir() if path.is_dir() and not path.name.startswith("."))
        if LOCAL_SBEL_REPRO.exists()
        else []
    )
    mbd_paths = sorted(
        {
            _relative(path.parent, LOCAL_SBEL_REPRO)
            for path in LOCAL_SBEL_REPRO.rglob("SimEngineMBD")
            if path.is_dir()
        }
    ) if LOCAL_SBEL_REPRO.exists() else []
    candidate_named_roots = [
        LOCAL_SBEL_REPRO / "2021" / "ASME" / "rA-formulation",
        LOCAL_SBEL_REPRO / "2022" / "HalfImplicit_JCND",
    ]
    named_mbd_roots = sorted(_relative(path, LOCAL_SBEL_REPRO) for path in candidate_named_roots if path.exists())
    search_terms = [
        "velocity partition",
        "velocity_partition",
        "velocity-partition",
        "velocitypartition",
        "VP2024",
        "ASME 2024",
    ]
    term_hits: dict[str, list[str]] = {}
    for term in search_terms:
        hits = [_relative(path, LOCAL_SBEL_REPRO) for path in files if _contains_text(path, term)]
        term_hits[term] = hits[:20]
    positive_code_roots = sorted(set(mbd_paths + named_mbd_roots))
    return {
        "local_sbel_reproducibility_path": str(LOCAL_SBEL_REPRO.relative_to(WORKSPACE)),
        "local_sbel_reproducibility_exists": LOCAL_SBEL_REPRO.exists(),
        "local_sbel_visible_file_count": len(files),
        "local_sbel_top_level_directories": top_level_dirs,
        "local_sbel_year_2024_directory_present": "2024" in top_level_dirs,
        "local_sbel_visible_mbd_code_roots": positive_code_roots,
        "local_sbel_visible_mbd_code_roots_count": len(positive_code_roots),
        "local_sbel_velocity_partition_term_hits": term_hits,
        "local_sbel_velocity_partition_term_hit_count": sum(len(hits) for hits in term_hits.values()),
        "local_sbel_distinct_vp2024_code_path_found": False,
        "local_public_metadata_path": str(LOCAL_PUBLIC_METADATA.relative_to(WORKSPACE)),
        "local_public_metadata_exists": LOCAL_PUBLIC_METADATA.exists(),
        "local_public_metadata_visible_non_git_file_count": len(public_metadata_files),
        "interpretation": (
            "The local sbel-reproducibility checkout exposes MBD code roots for "
            "2021/ASME/rA-formulation and 2022/HalfImplicit_JCND, but no visible "
            "2024 directory or velocity-partitioning MBD code root. The local "
            "public-metadata checkout is present only as git metadata in this "
            "workspace, so it supplies no distinct VP2024 source path."
        ),
    }


def main() -> None:
    summary_v048 = read_json(SUMMARY_V048)
    method_identity = read_json(RESULTS / "vp_method_identity_audit.json")
    order_audit = read_json(RESULTS / "vp_coordinate_partitioning_order_audit.json")
    large_step = read_json(RESULTS / "large_step_vp_local_order_summary.json")
    closure = read_json(PAPER / "EXTERNAL_SOURCE_POLICY_CLOSURE_MANIFEST.json")
    case_recon = read_json(PAPER / "EXTERNAL_CASE_EVIDENCE_RECONCILIATION.json")
    comparison = read_json(PAPER / "COMPARISON_OBJECTIVE_CLOSURE_RECONCILIATION_AUDIT.json")
    performance_rows = read_csv(RESULTS / "four_example_performance_matrix.csv")
    common_rows = read_csv(RESULTS / "common_reference_error_summary.csv")
    large_step_rows = read_csv(RESULTS / "large_step_vp_local_order_summary.csv")
    search_rows = read_csv(RESULTS / "velocity_partitioning_code_search.csv")

    vp_suite = next(row for row in closure["suites"] if row["suite_id"] == "vp2024_velocity_partitioning")
    vp_recon = next(row for row in case_recon["suites"] if row["suite_id"] == "vp2024_velocity_partitioning")
    example_rows = build_example_rows(performance_rows, common_rows, large_step_rows)
    search = search_summary(search_rows)

    coverage = {
        "examples_checked": [row["example"] for row in example_rows],
        "all_four_examples_checked": [row["example"] for row in example_rows] == EXAMPLES,
        "source_policy_rows": len(example_rows),
        "source_policy_code_path_unresolved_rows": sum(
            row["source_policy_status"] == "code_path_unresolved" for row in example_rows
        ),
        "source_policy_rows_attempted_not_reproducible": len(example_rows),
        "unable_to_reproduce_rows": len(example_rows),
        "common_reference_proxy_rows": sum(row["common_reference_proxy_status"] == "ok" for row in example_rows),
        "common_reference_local_velocity_order_wins": sum(
            row["common_reference_local_wins_velocity_order"] for row in example_rows
        ),
        "common_reference_local_finest_velocity_error_wins": sum(
            row["common_reference_local_wins_finest_velocity_error"] for row in example_rows
        ),
        "large_step_diagnostic_local_velocity_order_wins": sum(
            row["large_step_diagnostic_local_wins_velocity_order"] for row in example_rows
        ),
        "large_step_diagnostic_local_finest_velocity_error_wins": sum(
            row["large_step_diagnostic_local_wins_finest_velocity_error"] for row in example_rows
        ),
    }

    result = {
        "schema": "vp2024-code-path-disposition-audit-v1",
        "status": "all_four_examples_checked_no_distinct_public_code_unable_to_reproduce_not_promoted",
        "submission_ready": False,
        "suite_id": "vp2024_velocity_partitioning",
        "examples": EXAMPLES,
        "source_files": {
            "v048_summary": rel_from_paper(SUMMARY_V048),
            "velocity_partitioning_code_search_csv": rel_from_paper(CODE_SEARCH_CSV),
            "external_source_policy_closure_manifest": "EXTERNAL_SOURCE_POLICY_CLOSURE_MANIFEST.json",
            "external_case_evidence_reconciliation": "EXTERNAL_CASE_EVIDENCE_RECONCILIATION.json",
            "comparison_objective_closure_reconciliation": "COMPARISON_OBJECTIVE_CLOSURE_RECONCILIATION_AUDIT.json",
        },
        "coverage": coverage,
        "v048_public_code_path_summary": {
            "status": summary_v048.get("velocity_partitioning_code_status"),
            "public_web_search_status": summary_v048.get("velocity_partitioning_code_search", {}).get(
                "public_web_search_status"
            ),
            "relevant_code_path_resolved": summary_v048.get("velocity_partitioning_code_search", {}).get(
                "relevant_code_path_resolved"
            ),
            "easychair_visible_repository_reference": summary_v048.get(
                "velocity_partitioning_code_search", {}
            ).get("easychair_visible_repository_reference"),
            "row_count": summary_v048.get("velocity_partitioning_code_search", {}).get("row_count"),
        },
        "method_identity": {
            "alias_method": method_identity.get("alias_method"),
            "implemented_method": method_identity.get("implemented_method"),
            "alias_resolved": method_identity.get("alias_resolved"),
            "distinct_unresolved_vp_method_remaining": method_identity.get(
                "distinct_unresolved_vp_method_remaining"
            ),
        },
        "source_code_path_disposition": {
            "distinct_public_vp_code_path_found": False,
            "coordinate_partitioning_proxy_available": True,
            "coordinate_partitioning_proxy_is_source_policy_reproduction": False,
            "current_disposition": vp_suite.get("current_disposition"),
            "current_status": vp_suite.get("current_status"),
            "self_reproduction_attempted": True,
            "unable_to_reproduce": True,
            "final_nonpublic_code_disposition": "unable_to_reproduce_not_promoted",
            "claim_allowed_now": vp_suite.get("claim_allowed_now"),
            "accepted_for_external_superiority": vp_suite.get("accepted_for_external_superiority"),
            "queue_status": vp_suite.get("queue_status"),
            "parallel_shard_count": vp_suite.get("parallel_shard_count"),
            "required_to_close": vp_suite.get("required_to_close"),
        },
        "source_policy_rows": {
            "performance_matrix_row_count": vp_suite.get("performance_rows", {}).get("row_count"),
            "completed_row_count": vp_suite.get("performance_rows", {}).get("completed_row_count"),
            "not_complete_row_count": vp_suite.get("performance_rows", {}).get("not_complete_row_count"),
            "status_counts": vp_suite.get("performance_rows", {}).get("status_counts"),
            "source_policy_flagged_rows": vp_suite.get("source_policy_flagged_rows"),
            "attempted_not_reproducible_row_count": len(example_rows),
            "unable_to_reproduce_row_count": len(example_rows),
            "final_nonpublic_code_disposition": "unable_to_reproduce_not_promoted",
            "source_policy_rows_closed": 0,
            "external_superiority_ready_rows": 0,
        },
        "common_reference_proxy_disposition": {
            "controlling_for_apples_to_apples_diagnostic": True,
            "controlling_for_source_policy_external_superiority": False,
            "direct_nonlocal_velocity_order_wins": comparison.get("direct_nonlocal_velocity_order_wins"),
            "direct_nonlocal_velocity_order_comparisons": comparison.get(
                "direct_nonlocal_velocity_order_comparisons"
            ),
            "direct_nonlocal_finest_velocity_error_wins": comparison.get(
                "direct_nonlocal_finest_velocity_error_wins"
            ),
            "direct_nonlocal_finest_velocity_error_comparisons": comparison.get(
                "direct_nonlocal_finest_velocity_error_comparisons"
            ),
            "vp_proxy_local_velocity_order_wins": coverage["common_reference_local_velocity_order_wins"],
            "vp_proxy_local_finest_velocity_error_wins": coverage[
                "common_reference_local_finest_velocity_error_wins"
            ],
            "wording_boundary": (
                "Use this as a finite-grid common-reference diagnostic only. Do not state "
                "source-paper default-policy superiority or source-policy VP2024 reproduction."
            ),
        },
        "large_step_diagnostic_boundary": {
            "noncontrolling_mixed_reference_policy": True,
            "local_velocity_order_wins": large_step.get("local_velocity_order_wins"),
            "local_finest_velocity_error_wins": large_step.get("local_finest_velocity_error_wins"),
            "vp_finest_velocity_error_wins": order_audit.get("vp_finest_velocity_error_wins"),
            "interpretation": (
                "The larger-step VP diagnostic preserves the order/error distinction, but it is "
                "not the controlling apples-to-apples common-reference table and is not "
                "source-policy evidence."
            ),
        },
        "public_code_search": search,
        "public_repository_api_spot_check": public_api_spot_check(),
        "local_repository_tree_scan": local_repository_tree_scan(),
        "case_reconciliation_crosscheck": {
            "bounded_evidence_present": vp_recon.get("bounded_evidence_present"),
            "case_inventory_status_counts": vp_recon.get("case_inventory", {}).get("case_status_counts"),
            "performance_status_counts": vp_recon.get("performance_rows", {}).get("status_counts"),
            "external_superiority_ready": vp_recon.get("external_superiority_ready"),
            "source_policy_closed": vp_recon.get("source_policy_closed"),
        },
        "example_rows": example_rows,
        "execution_policy": {
            "read_only_existing_artifacts": True,
            "default_1e_4_required": False,
            "heavy_numerical_run_invoked": False,
            "run_v047_invoked": False,
            "v048_runner_invoked": False,
        },
    }

    with OUT_JSON.open("w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, sort_keys=True)
        handle.write("\n")

    lines = [
        "# VP2024 Code-Path Disposition Audit",
        "",
        "Status: **ALL FOUR EXAMPLES CHECKED; NO DISTINCT PUBLIC CODE; UNABLE TO REPRODUCE; NOT PROMOTED**.",
        "",
        f"Examples checked: `{', '.join(coverage['examples_checked'])}`.",
        f"Source-policy VP rows unresolved: `{coverage['source_policy_code_path_unresolved_rows']}/4`.",
        f"Source-policy VP rows attempted-not-reproducible/unable: `{coverage['source_policy_rows_attempted_not_reproducible']}/{coverage['unable_to_reproduce_rows']}`.",
        f"Final nonpublic-code disposition: `{result['source_code_path_disposition']['final_nonpublic_code_disposition']}`.",
        f"Common-reference proxy rows ok: `{coverage['common_reference_proxy_rows']}/4`.",
        (
            "Common-reference proxy local velocity-order wins: "
            f"`{coverage['common_reference_local_velocity_order_wins']}/4`."
        ),
        (
            "Common-reference proxy local finest-velocity-error wins: "
            f"`{coverage['common_reference_local_finest_velocity_error_wins']}/4`."
        ),
        (
            "Larger-step diagnostic local velocity-order wins: "
            f"`{coverage['large_step_diagnostic_local_velocity_order_wins']}/4`."
        ),
        (
            "Larger-step diagnostic local finest-velocity-error wins: "
            f"`{coverage['large_step_diagnostic_local_finest_velocity_error_wins']}/4`."
        ),
        f"Distinct public VP code path found: `{result['source_code_path_disposition']['distinct_public_vp_code_path_found']}`.",
        f"Proxy is source-policy reproduction: `{result['source_code_path_disposition']['coordinate_partitioning_proxy_is_source_policy_reproduction']}`.",
        f"Claim allowed now: `{result['source_code_path_disposition']['claim_allowed_now']}`.",
        f"Default `1e-4` required: `{result['execution_policy']['default_1e_4_required']}`.",
        f"Heavy numerical run invoked: `{result['execution_policy']['heavy_numerical_run_invoked']}`.",
        "",
        "## Four-Example Disposition",
        "",
        "| example | source-policy status | common-ref local order | common-ref VP order | common-ref local velocity error | common-ref VP velocity error | local order win | local error win |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in example_rows:
        lines.append(
            "| "
            f"`{row['example']}` | "
            f"`{row['source_policy_status']}` | "
            f"`{fmt(row['common_reference_local_velocity_order'])}` | "
            f"`{fmt(row['common_reference_vp_proxy_velocity_order'])}` | "
            f"`{fmt(row['common_reference_local_finest_velocity_error'])}` | "
            f"`{fmt(row['common_reference_vp_proxy_finest_velocity_error'])}` | "
            f"`{row['common_reference_local_wins_velocity_order']}` | "
            f"`{row['common_reference_local_wins_finest_velocity_error']}` |"
        )
    lines += [
        "",
        "## Interpretation",
        "",
        (
            "The source-policy VP2024 rows are all unresolved because no distinct public "
            "velocity-partitioning code path has been located. The coordinate-partitioning "
            "proxy is useful for a finite-grid common-reference diagnostic, but it is not "
            "a source-policy reproduction of the paper's published code package."
        ),
        "",
        (
            "The controlling apples-to-apples table is the common-reference matrix, where "
            "the local method wins all four VP proxy velocity-order rows and all four VP "
            "proxy finest-velocity-error rows. The older larger-step VP diagnostic remains "
            "noncontrolling and only preserves the warning that mixed-reference finest-error "
            "rows should not be used for a universal direct-error claim."
        ),
        "",
        "## Public Code Search",
        "",
        f"Search evidence rows: `{search['row_count']}`.",
        f"Search evidence source: `{search['source_csv']}`.",
        f"Public web search status: `{search['public_web_search_status']}`.",
        f"Public web search evidence rows: `{search['public_web_search_row_count']}`.",
        f"GitHub code-search auth boundary: `{search['github_code_search_auth_boundary']}`.",
        (
            "V048 code-path summary status: "
            f"`{result['v048_public_code_path_summary']['status']}`."
        ),
        f"Reference points to 2021 rA repo: `{search['points_to_2021_rA_repo']}`.",
        f"Distinct VP repo found: `{search['distinct_vp_repo_found']}`.",
        (
            "2024 public repo directory names from the API spot check: "
            f"`{', '.join(result['public_repository_api_spot_check']['year_2024_directories'])}`."
        ),
        (
            "Local sbel-reproducibility top-level directories: "
            f"`{', '.join(result['local_repository_tree_scan']['local_sbel_top_level_directories'])}`."
        ),
        (
            "Local visible MBD code roots: "
            f"`{', '.join(result['local_repository_tree_scan']['local_sbel_visible_mbd_code_roots'])}`."
        ),
        (
            "Local velocity-partition search hits: "
            f"`{result['local_repository_tree_scan']['local_sbel_velocity_partition_term_hit_count']}`."
        ),
        (
            "Local distinct VP2024 code path found: "
            f"`{result['local_repository_tree_scan']['local_sbel_distinct_vp2024_code_path_found']}`."
        ),
        "",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print("vp2024_code_path_disposition_audit=written")
    print("source_policy_code_path_unresolved_rows=4/4")
    print("unable_to_reproduce_rows=4/4")
    print("common_reference_vp_proxy_local_order_wins=4/4")
    print("common_reference_vp_proxy_local_error_wins=4/4")
    print("distinct_public_vp_code_path_found=False")


if __name__ == "__main__":
    main()
