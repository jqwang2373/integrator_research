#!/usr/bin/env python3
"""Read-only validation for the cross-paper benchmark case inventory."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
from paper_paths import LATEX, package_path as manuscript_path
ROOT = PAPER.parent
REPO = ROOT.parent
CASES = PAPER / "CROSS_PAPER_BENCHMARK_CASES.json"
SPEC = PAPER / "CROSS_PAPER_BENCHMARK_SPEC.md"
MATRIX = PAPER / "CROSS_PAPER_BENCHMARK_MATRIX.md"
MAIN = LATEX / "main_cmame.tex"
EXTERNAL = REPO / "external" / "sbel-reproducibility"
PUBLIC_METADATA = REPO / "external" / "public-metadata"
RA2021 = EXTERNAL / "2021" / "ASME" / "rA-formulation"
HI2022 = EXTERNAL / "2022" / "HalfImplicit_JCND"
SOURCE_PDF = REPO / "s11044-026-10153-w.pdf"
VP_SEARCH = ROOT / "v048_cross_paper_same_test_benchmarks" / "results" / "velocity_partitioning_code_search.csv"


REQUIRED_SOURCES = {
    "tfe2026_chaturvedi_sandu_sandu",
    "ra2021_taves_kissel_negrut",
    "hi2022_fang_kissel_zhang_negrut",
    "vp2024_kissel_bakke_negrut",
}

REQUIRED_GROUPS = {
    "tfe2026_original_pendulum",
    "ra2021_absolute_coordinate",
    "hi2022_half_implicit",
    "vp2024_velocity_partitioning",
}

REQUIRED_CASES = {
    "tfe2026_rigid_pendulum_no_friction",
    "tfe2026_rigid_pendulum_with_friction",
    "ra2021_single_pendulum_order",
    "ra2021_four_link_order",
    "ra2021_slider_crank_order",
    "ra2021_single_pendulum_timing_iterations",
    "ra2021_double_pendulum_timing_iterations",
    "ra2021_four_link_timing_iterations",
    "ra2021_slider_crank_timing_iterations",
    "hi2022_double_pendulum_open_loop_convergence",
    "hi2022_four_link_closed_loop_convergence",
    "hi2022_slider_crank_closed_loop_convergence",
    "hi2022_double_pendulum_energy",
    "hi2022_timing_iterations",
    "hi2022_n_pendulum_scaling",
    "hi2022_slider_crank_friction",
    "vp2024_velocity_partitioning_code_resolution",
}

ALLOWED_STATUSES = {"not_run", "code_path_unresolved"}


class Checks:
    def __init__(self) -> None:
        self.errors: list[str] = []

    def check(self, condition: bool, message: str) -> None:
        if not condition:
            self.errors.append(message)


def read_text(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8", errors="replace")


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(path)
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def contains_normalized(text: str, token: str) -> bool:
    return token in text or " ".join(token.split()) in " ".join(text.split())


def resolve_source(path_label: str) -> Path:
    if path_label.startswith("../external/"):
        return (ROOT / path_label).resolve()
    if path_label.startswith("../../"):
        return (manuscript_path(path_label)).resolve()
    return (manuscript_path(path_label)).resolve()


def require_tokens(checks: Checks, text: str, tokens: list[str], label: str) -> None:
    for token in tokens:
        checks.check(contains_normalized(text, token), f"{label} missing token: {token}")


def require_artifacts(checks: Checks, artifacts: Any, label: str) -> None:
    checks.check(isinstance(artifacts, list) and artifacts, f"{label} missing artifacts")
    if not isinstance(artifacts, list):
        return
    for artifact in artifacts:
        if not isinstance(artifact, str):
            checks.check(False, f"{label} has non-string artifact")
            continue
        path = resolve_source(artifact)
        checks.check(path.exists() and path.stat().st_size > 0, f"{label} artifact missing: {artifact}")


def main() -> int:
    checks = Checks()
    try:
        data = read_json(CASES)
        spec = read_text(SPEC)
        matrix = read_text(MATRIX)
        main_tex = read_text(MAIN)
        slider2021 = read_text(RA2021 / "C2" / "SimEngineMBD" / "example_models" / "slider_crank.py")
        slider2022 = read_text(HI2022 / "SimEngineMBD" / "example_models" / "slider_crank.py")
    except Exception as exc:  # noqa: BLE001 - concise CLI failure.
        print(f"cross_paper_benchmark_cases=FAIL\n- {exc}")
        return 1

    checks.check(data.get("schema") == "cross-paper-benchmark-cases-v1", "case inventory schema changed")
    checks.check(
        data.get("status") == "spec_extracted_partial_evidence_not_full_campaign",
        "case inventory status changed",
    )
    checks.check(data.get("same_test_campaign_status") == "not_run", "same-test status must remain not_run")
    checks.check(data.get("full_external_same_test_campaign_passed") is False, "full campaign overclaimed")
    checks.check(data.get("external_superiority_claim") is False, "external superiority overclaimed")
    checks.check(data.get("default_1e-4_required") is False, "case inventory requires default 1e-4")
    checks.check(data.get("accepted_internal_method") == "Gauss6/FullVA", "accepted method mismatch")
    checks.check(SOURCE_PDF.exists() and SOURCE_PDF.stat().st_size > 100_000, "source TFE PDF missing")
    checks.check(RA2021.exists(), "2021 rA suite missing")
    checks.check(HI2022.exists(), "2022 half-implicit suite missing")
    checks.check(PUBLIC_METADATA.exists(), "public-metadata mirror missing")
    checks.check(VP_SEARCH.exists() and VP_SEARCH.stat().st_size > 0, "velocity-partitioning search artifact missing")
    checks.check("sys.bodies[0].m = 0.12" in slider2021, "2021 slider-crank mass anchor missing")
    checks.check("sys.bodies[0].m = 1.2" in slider2022, "2022 slider-crank mass anchor missing")

    overlay = data.get("partial_evidence_overlay", {})
    checks.check(isinstance(overlay, dict), "partial_evidence_overlay missing")
    if isinstance(overlay, dict):
        claim_boundary = overlay.get("claim_boundary", {})
        checks.check(isinstance(claim_boundary, dict), "overlay claim boundary missing")
        if isinstance(claim_boundary, dict):
            checks.check(claim_boundary.get("same_test_campaign_status") == "not_run", "overlay same-test status changed")
            checks.check(claim_boundary.get("external_superiority_claim") is False, "overlay superiority overclaim")
            checks.check(
                claim_boundary.get("strict_public_policy_1e-4_required") is False,
                "overlay strict 1e-4 incorrectly required",
            )
            checks.check(
                claim_boundary.get("default_1e-4_required") is False,
                "overlay default 1e-4 incorrectly required",
            )

        tfe_overlay = overlay.get("tfe2026_original_pendulum", {})
        checks.check(isinstance(tfe_overlay, dict), "TFE overlay missing")
        if isinstance(tfe_overlay, dict):
            checks.check(tfe_overlay.get("evidence_status") == "spec_extracted_only", "TFE overlay status changed")
            checks.check(tfe_overlay.get("completed_required_cases") == 0, "TFE overlay overclaimed completed cases")
            checks.check(tfe_overlay.get("open_required_cases") == 2, "TFE overlay open case count changed")

        ra_overlay = overlay.get("ra2021_absolute_coordinate", {})
        checks.check(isinstance(ra_overlay, dict), "RA2021 overlay missing")
        if isinstance(ra_overlay, dict):
            checks.check(
                ra_overlay.get("evidence_status")
                == "partial_public_baseline_and_coarse_local_evidence_available_not_full_external_superiority",
                "RA2021 overlay status changed",
            )
            checks.check(ra_overlay.get("public_baseline_order_rows") == 27, "RA2021 public baseline row count changed")
            checks.check(ra_overlay.get("public_order_summary_rows") == 9, "RA2021 public summary row count changed")
            checks.check(
                ra_overlay.get("coarse_same_window_ready_examples") == ["single_pendulum", "double_pendulum"],
                "RA2021 coarse-ready examples changed",
            )
            checks.check(
                ra_overlay.get("local_true_dynamic_order_examples") == ["four_link", "slider_crank"],
                "RA2021 local true-dynamic examples changed",
            )
            checks.check(
                ra_overlay.get("public_work_precision_available_examples") == ["four_link", "slider_crank"],
                "RA2021 public work/precision examples changed",
            )
            checks.check(
                ra_overlay.get("strict_common_reference_available_examples") == ["four_link", "slider_crank"],
                "RA2021 strict common-reference examples changed",
            )
            require_artifacts(checks, ra_overlay.get("artifacts"), "RA2021 overlay")

        hi_overlay = overlay.get("hi2022_half_implicit", {})
        checks.check(isinstance(hi_overlay, dict), "HI2022 overlay missing")
        if isinstance(hi_overlay, dict):
            checks.check(
                hi_overlay.get("evidence_status") == "bounded_pilot_available_full_T8_policy_not_complete",
                "HI2022 overlay status changed",
            )
            checks.check(hi_overlay.get("bounded_rows") == 24, "HI2022 bounded row count changed")
            checks.check(hi_overlay.get("full_T8_policy_complete") is False, "HI2022 full T8 policy overclaimed")
            require_artifacts(checks, hi_overlay.get("artifacts"), "HI2022 overlay")

        vp_overlay = overlay.get("vp2024_velocity_partitioning", {})
        checks.check(isinstance(vp_overlay, dict), "VP2024 overlay missing")
        if isinstance(vp_overlay, dict):
            checks.check(vp_overlay.get("evidence_status") == "code_path_unresolved", "VP2024 overlay status changed")
            require_artifacts(checks, vp_overlay.get("artifacts"), "VP2024 overlay")

    sources = data.get("external_sources", [])
    groups = data.get("case_groups", [])
    cases = data.get("cases", [])
    checks.check(isinstance(sources, list) and len(sources) >= 4, "external_sources must list all source families")
    checks.check(isinstance(groups, list) and len(groups) >= 4, "case_groups must list all source families")
    checks.check(isinstance(cases, list) and len(cases) >= len(REQUIRED_CASES), "case list is too small")

    source_ids = {source.get("source_id") for source in sources if isinstance(source, dict)}
    group_ids = {group.get("group_id") for group in groups if isinstance(group, dict)}
    case_ids = {case.get("case_id") for case in cases if isinstance(case, dict)}
    checks.check(REQUIRED_SOURCES <= source_ids, f"missing sources: {sorted(REQUIRED_SOURCES - source_ids)}")
    checks.check(REQUIRED_GROUPS <= group_ids, f"missing groups: {sorted(REQUIRED_GROUPS - group_ids)}")
    checks.check(REQUIRED_CASES <= case_ids, f"missing cases: {sorted(REQUIRED_CASES - case_ids)}")

    source_by_id = {source.get("source_id"): source for source in sources if isinstance(source, dict)}
    vp_source = source_by_id.get("vp2024_kissel_bakke_negrut", {})
    checks.check(vp_source.get("doi") == "10.1115/1.4065254", "velocity-partitioning DOI missing")
    checks.check(
        vp_source.get("code_directory_status") == "not_resolved_in_local_sbel_or_public_metadata_tree",
        "velocity-partitioning code path must remain unresolved until located",
    )

    for case in cases:
        if not isinstance(case, dict):
            checks.check(False, "case entry is not an object")
            continue
        case_id = case.get("case_id", "<missing>")
        current_status = case.get("current_status")
        checks.check(current_status in ALLOWED_STATUSES, f"{case_id} has invalid current_status: {current_status}")
        checks.check(current_status != "passed", f"{case_id} incorrectly claims passed status")
        checks.check(case.get("group_id") in group_ids, f"{case_id} has unknown group")
        checks.check("metrics" in case and isinstance(case.get("metrics"), list), f"{case_id} missing metrics")
        checks.check("baseline_methods" in case and isinstance(case.get("baseline_methods"), list), f"{case_id} missing baselines")
        checks.check("reference_policy" in case, f"{case_id} missing reference_policy")
        checks.check("tolerance_policy" in case, f"{case_id} missing tolerance_policy")

        source_files = case.get("source_files", [])
        checks.check(isinstance(source_files, list), f"{case_id} source_files is not a list")
        if current_status != "code_path_unresolved":
            checks.check(source_files, f"{case_id} has no source_files")
        for source_file in source_files:
            if not isinstance(source_file, str):
                checks.check(False, f"{case_id} has non-string source file")
                continue
            path = resolve_source(source_file)
            checks.check(path.exists() and path.stat().st_size > 0, f"{case_id} source file missing: {source_file}")

    require_tokens(
        checks,
        spec,
        [
            "CROSS_PAPER_BENCHMARK_CASES.json",
            "partial_evidence_overlay",
            "coarse_first_no_default_1e-4",
            "strict public-policy `1e-4` rows are opt-in",
            "Velocity-partitioning Lie-group ODE suite",
            "code path unresolved",
            "10.1115/1.4065254",
            "velocity_partitioning_code_search.csv",
        ],
        "CROSS_PAPER_BENCHMARK_SPEC.md",
    )
    require_tokens(
        checks,
        matrix,
        [
            "CROSS_PAPER_BENCHMARK_CASES.json",
            "partial_evidence_overlay",
            "default_1e-4_required=false",
            "Kissel/Bakke/Negrut Velocity-Partitioning Suite",
            "code path unresolved",
            "public-metadata",
        ],
        "CROSS_PAPER_BENCHMARK_MATRIX.md",
    )
    require_tokens(
        checks,
        main_tex,
        [
            "public-code benchmark specification and row-level inventory",
            "Kissel--Bakke--Negrut velocity-partitioning",
            "The coordinate-partitioning proxy is identified through the implemented",
            "distinct public VP code path remains unresolved and demoted",
        ],
        "main_cmame.tex",
    )

    serialized = json.dumps(data, sort_keys=True).lower()
    forbidden = [
        "same_test_campaign_status=passed",
        "external-method superiority established",
        "kissel/negrut baselines beaten",
    ]
    for token in forbidden:
        checks.check(token not in serialized, f"forbidden completed claim present: {token}")

    if checks.errors:
        print("cross_paper_benchmark_cases=FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("cross_paper_benchmark_cases=PASS")
    print(f"case_count={len(cases)}")
    print("case_inventory_status=spec_extracted_partial_evidence_not_full_campaign")
    print("partial_evidence_overlay=True")
    print("same_test_campaign_status=not_run")
    print("external_superiority_claim=False")
    print("default_1e-4=False")
    print("velocity_partitioning_code_status=not_resolved_in_local_sbel_or_public_metadata_tree")
    print("next_gate=run_gauss6_fullva_on_external_public_code_tests")
    return 0


if __name__ == "__main__":
    sys.exit(main())
