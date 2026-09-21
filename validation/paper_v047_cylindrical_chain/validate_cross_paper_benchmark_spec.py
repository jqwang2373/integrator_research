#!/usr/bin/env python3
"""Read-only validation for the cross-paper benchmark specification."""

from __future__ import annotations

import sys
from pathlib import Path


PAPER = Path(__file__).resolve().parent
from paper_paths import LATEX, package_path as manuscript_path
ROOT = PAPER.parent
REPO = ROOT.parent
SPEC = PAPER / "CROSS_PAPER_BENCHMARK_SPEC.md"
MATRIX = PAPER / "CROSS_PAPER_BENCHMARK_MATRIX.md"
CASES = PAPER / "CROSS_PAPER_BENCHMARK_CASES.json"
MAIN = LATEX / "main_cmame.tex"
EXTERNAL = REPO / "external" / "sbel-reproducibility"
PUBLIC_METADATA = REPO / "external" / "public-metadata"
RA2021 = EXTERNAL / "2021" / "ASME" / "rA-formulation"
HI2022 = EXTERNAL / "2022" / "HalfImplicit_JCND"
SOURCE_PDF = REPO / "external" / "literature" / "s11044-026-10153-w.pdf"
VP_SEARCH = ROOT.parent / "numerics" / "v048_cross_paper_same_test_benchmarks" / "results" / "velocity_partitioning_code_search.csv"


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


def contains_normalized(text: str, token: str) -> bool:
    return token in text or " ".join(token.split()) in " ".join(text.split())


def require_tokens(checks: Checks, text: str, tokens: list[str], label: str) -> None:
    for token in tokens:
        checks.check(contains_normalized(text, token), f"{label} missing token: {token}")


def main() -> int:
    checks = Checks()
    try:
        spec = read_text(SPEC)
        matrix = read_text(MATRIX)
        cases = read_text(CASES)
        main_tex = read_text(MAIN)
        order_script = read_text(RA2021 / "profiling_scripts" / "order_analysis.sh")
        time_script = read_text(RA2021 / "profiling_scripts" / "time.sh")
        iter_script = read_text(RA2021 / "profiling_scripts" / "check_iters.sh")
        single2021 = read_text(RA2021 / "C2" / "SimEngineMBD" / "example_models" / "single_pendulum.py")
        double2021 = read_text(RA2021 / "C2" / "SimEngineMBD" / "example_models" / "double_pendulum.py")
        four2021 = read_text(RA2021 / "C2" / "SimEngineMBD" / "example_models" / "four_link.py")
        slider2021 = read_text(RA2021 / "C2" / "SimEngineMBD" / "example_models" / "slider_crank.py")
        ode2022 = read_text(HI2022 / "run_double_pendulum_ode.py")
        dae2022 = read_text(HI2022 / "run_double_pendulum_dae.py")
        closed2022 = read_text(HI2022 / "run_closed_loop_setups.py")
        numitr2022 = read_text(HI2022 / "run_num_itr.py")
        energy2022 = read_text(HI2022 / "plot_double_pendulum_energy.py")
        scaling2022 = read_text(HI2022 / "run_scaling_analysis.py")
        friction2022 = read_text(HI2022 / "run_slider_crank_frictional.py")
        slider2022 = read_text(HI2022 / "SimEngineMBD" / "example_models" / "slider_crank.py")
    except Exception as exc:  # noqa: BLE001 - concise CLI failure.
        print(f"cross_paper_benchmark_spec=FAIL\n- {exc}")
        return 1

    checks.check(SOURCE_PDF.exists() and SOURCE_PDF.stat().st_size > 100_000, "source TFE PDF missing")
    checks.check(RA2021.exists(), "2021 rA suite missing")
    checks.check(HI2022.exists(), "2022 half-implicit suite missing")
    checks.check(PUBLIC_METADATA.exists(), "public-metadata mirror missing")
    checks.check(VP_SEARCH.exists() and VP_SEARCH.stat().st_size > 0, "velocity-partitioning search artifact missing")

    require_tokens(
        checks,
        spec,
        [
            "Cross-Paper Benchmark Specification",
            "spec extracted, partial evidence recorded, full same-test campaign not yet run",
            "CROSS_PAPER_BENCHMARK_CASES.json",
            "partial_evidence_overlay",
            "coarse_first_no_default_1e-4",
            "strict public-policy `1e-4` rows are opt-in",
            "../external/sbel-reproducibility/2021/ASME/rA-formulation",
            "../external/sbel-reproducibility/2022/HalfImplicit_JCND",
            "`origin/master` or `origin/user/aaron/msd` trees",
            "public web search",
            "Velocity-partitioning Lie-group ODE suite",
            "code path unresolved",
            "velocity_partitioning_code_search.csv",
            "10.1115/1.4065254",
            "Forms: `rA`, `rp`, `reps`.",
            "Dynamics order-analysis step sizes are `1e-2`, `1e-3`, and `1e-4`.",
            "`--end_time 3 --step_size 1e-3 --tol 1e-10`",
            "Geometry and drive match; v047 uses `t_f=0.2`",
            "v047 regularizes angular speeds to `+/-1e-12`",
            "Model graph and parameter values match the 2021 C2 source",
            "not the `rA/rp/reps` public-code order campaign",
            "Forms: `rA_half` and `rA`, labelled half-implicit and fully implicit.",
            "Open-loop double-pendulum reference: ODE solution with `dt_exact=1e-6`, `t_end=8`.",
            "Closed-loop reference: kinematic `rA` reference with `tol_ref=1e-10`, `dt_ref=1e-5`, `t_end=8`.",
            "The 2021 rA slider-crank code uses crank mass `0.12`.",
            "The 2022 half-implicit slider-crank code uses crank mass `1.2`.",
            "vp2024_velocity_partitioning_code_resolution",
            "The local cylindrical-chain all-row TFE diagnostic is not this pendulum reproduction.",
            "It cannot state that the external same-test benchmark campaign has passed.",
        ],
        "CROSS_PAPER_BENCHMARK_SPEC.md",
    )

    require_tokens(
        checks,
        matrix,
        [
            "Cross-Paper Benchmark Matrix",
            "CROSS_PAPER_BENCHMARK_CASES.json",
            "Kissel/Taves/Negrut rA Suite",
            "Fang/Kissel/Zhang/Negrut Half-Implicit Suite",
            "Kissel/Bakke/Negrut Velocity-Partitioning Suite",
            "full external same-test comparison remains open",
        ],
        "CROSS_PAPER_BENCHMARK_MATRIX.md",
    )

    require_tokens(
        checks,
        cases,
        [
            '"schema": "cross-paper-benchmark-cases-v1"',
            '"status": "spec_extracted_partial_evidence_not_full_campaign"',
            '"same_test_campaign_status": "not_run"',
            '"partial_evidence_overlay"',
            '"default_1e-4_required": false',
            '"ra2021_taves_kissel_negrut"',
            '"hi2022_fang_kissel_zhang_negrut"',
            '"vp2024_kissel_bakke_negrut"',
            '"code_directory_status": "not_resolved_in_local_sbel_or_public_metadata_tree"',
            '"vp2024_velocity_partitioning_code_resolution"',
        ],
        "CROSS_PAPER_BENCHMARK_CASES.json",
    )

    require_tokens(
        checks,
        main_tex,
        [
            "Cross-paper same-test comparison criterion",
            "Chaturvedi--Sandu--Sandu",
            "Kissel--Taves--Negrut",
            "Fang--Kissel--Zhang--Negrut",
            "Kissel--Bakke--Negrut velocity-partitioning",
            "public-code benchmark specification and row-level inventory",
            "The coordinate-partitioning proxy is identified through the implemented",
            "distinct public VP code path remains unresolved and demoted",
            "2021 public baselines complete",
            "full source-policy dynamic-comparison rows remain unaccepted",
            "32 completed rows",
        ],
        "main_cmame.tex",
    )

    require_tokens(
        checks,
        order_script,
        [
            "for form in rA rp reps",
            "for model in single_pendulum four_link slider_crank",
            "--mode kin --tol 1e-12 --output $tmp_file --save_data",
            "for steps in 1e-2 1e-3 1e-4",
        ],
        "2021 order_analysis.sh",
    )
    require_tokens(
        checks,
        time_script,
        [
            "for model in single_pendulum double_pendulum four_link slider_crank",
            "--end_time 3 --step_size 1e-3 --tol 1e-10",
        ],
        "2021 time.sh",
    )
    require_tokens(checks, iter_script, ["Avg. iterations:"], "2021 check_iters.sh")
    require_tokens(checks, single2021, ["ang_sym = π/2 + π/4 * sp.cos(2*t)"], "2021 single_pendulum.py")
    require_tokens(checks, double2021, ["pend_len = [2*L, L]"], "2021 double_pendulum.py")
    require_tokens(checks, four2021, ["np.diag([4, 2, 0])", "np.diag([12.4, 0.01, 0])"], "2021 four_link.py")
    require_tokens(checks, slider2021, ["sys.bodies[0].m = 0.12", "ang_sym = -2*π*t + π/2"], "2021 slider_crank.py")

    require_tokens(checks, ode2022, ["dt_exact = 1e-6", "t_end = 8"], "2022 run_double_pendulum_ode.py")
    require_tokens(
        checks,
        dae2022,
        ["tolerance = 1e-10", "step_sizes = [1e-4, 2e-4, 4e-4, 1e-3, 2e-3, 4e-3, 1e-2, 2e-2, 4e-2]", "tolerance/step_size**2"],
        "2022 run_double_pendulum_dae.py",
    )
    require_tokens(checks, closed2022, ["t_end = 8", "dt_ref = 1e-5", "tol_ref = 1e-10"], "2022 run_closed_loop_setups.py")
    require_tokens(checks, numitr2022, ["step_sizes = [1e-4, 1e-4, 1e-3, 1e-3, 1e-2, 1e-2]"], "2022 run_num_itr.py")
    require_tokens(checks, energy2022, ["step_size = 1e-3", "t_end = 10"], "2022 plot_double_pendulum_energy.py")
    require_tokens(checks, scaling2022, ["bodies = [2, 4, 6, 8, 16, 32]", "tolerances = [1e-7, 1e-5]"], "2022 run_scaling_analysis.py")
    require_tokens(checks, friction2022, ["t_end = 2", "step_size = 1e-3", "for mu in [0, 0.2, 0.4]"], "2022 run_slider_crank_frictional.py")
    require_tokens(checks, slider2022, ["sys.bodies[0].m = 1.2"], "2022 slider_crank.py")

    forbidden_claims = [
        "same_test_campaign_status=passed",
        "Kissel/Negrut baselines have been beaten",
        "same-test superiority is established",
    ]
    normalized = " ".join(spec.split()).lower()
    for token in forbidden_claims:
        checks.check(token.lower() not in normalized, f"forbidden completed claim present: {token}")

    if checks.errors:
        print("cross_paper_benchmark_spec=FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("cross_paper_benchmark_spec=PASS")
    print("ra2021_suite_present=True")
    print("halfimplicit2022_suite_present=True")
    print("same_test_campaign_status=not_run")
    print("next_gate=run_gauss6_fullva_on_external_public_code_tests")
    return 0


if __name__ == "__main__":
    sys.exit(main())
