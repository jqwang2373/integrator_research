from __future__ import annotations

import argparse
import csv
import importlib
import importlib.util
import json
import os
import platform
import re
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import numpy as np


os.environ.setdefault("MPLBACKEND", "Agg")
os.environ.setdefault("MPLCONFIGDIR", "/tmp/mplconfig")

HERE = Path(__file__).resolve().parent
WORK_ROOT = HERE.parent
REPO_ROOT = WORK_ROOT.parent
RESULTS = HERE / "results"
PAPER = REPO_ROOT / "validation" / "paper_v047_cylindrical_chain"
CASES_JSON = PAPER / "CROSS_PAPER_BENCHMARK_CASES.json"
SBEL_ROOT = REPO_ROOT / "external" / "sbel-reproducibility"
PUBLIC_METADATA_ROOT = REPO_ROOT / "external" / "public-metadata"
SBEL_C2 = SBEL_ROOT / "2021" / "ASME" / "rA-formulation" / "C2"
HI2022_ROOT = SBEL_ROOT / "2022" / "HalfImplicit_JCND"

if str(SBEL_C2) not in sys.path:
    sys.path.insert(0, str(SBEL_C2))


RA2021_FORMS = ["rA", "rp", "reps"]
RA2021_ORDER_STEP_SIZES = [1e-2, 1e-3, 1e-4]
RA2021_PUBLIC_REFERENCE_H = 1e-3
RA2021_PUBLIC_T_END = 3.0
RA2021_DOUBLE_ORDER_STEP_SIZES = [1e-2, 2e-3, 1e-3]
RA2021_DOUBLE_ORDER_REFERENCE_H = 1e-4
RA2021_DOUBLE_COARSE_STEP_SIZES = [0.1, 0.05, 0.025]
RA2021_DOUBLE_COARSE_REFERENCE_H = 0.0125
SOURCE_POLICY_1E4_H = 1e-4
SOURCE_POLICY_1E4_EPS = 1e-15
HI2022_FORMS = ["rA", "rA_half"]
HI2022_MODELS = ["single_pendulum", "double_pendulum", "four_link", "slider_crank"]
HI2022_PUBLIC_STEP_SIZES = [1e-4, 2e-4, 4e-4, 1e-3, 2e-3, 4e-3, 1e-2, 2e-2, 4e-2]
HI2022_PUBLIC_T_END = 8.0
HI2022_REFERENCE_H = 1e-3
HI2022_TOLERANCE_BASE = 1e-10
VP_CODE_STATUS = "not_resolved_in_local_sbel_or_public_metadata_tree"
VP_EXACT_PATH_PATTERNS = (
    "velocity.*partition",
    "partition.*velocity",
    "coordinate.*partition",
    "partition.*coordinate",
    "performance.*lie",
    "lie.*performance",
    "kissel",
    "bakke",
)
VP_MECHANISM_PATTERNS = ("pendulum", "slider", "crank", "four")
VP_SEARCH_REFS = ("origin/master", "origin/user/aaron/msd")


@dataclass(frozen=True)
class PublicModel:
    name: str
    module: str
    run_name: str
    body_count: int


RA2021_ORDER_MODELS = [
    PublicModel("single_pendulum", "SimEngineMBD.example_models.single_pendulum", "run_single_pendulum", 1),
    PublicModel("four_link", "SimEngineMBD.example_models.four_link", "run_four_link", 3),
    PublicModel("slider_crank", "SimEngineMBD.example_models.slider_crank", "run_slider_crank", 3),
]
RA2021_MODEL_BY_NAME = {model.name: model for model in RA2021_ORDER_MODELS}
RA2021_TIMING_MODELS = [
    PublicModel("single_pendulum", "SimEngineMBD.example_models.single_pendulum", "run_single_pendulum", 1),
    PublicModel("double_pendulum", "SimEngineMBD.example_models.double_pendulum", "run_double_pendulum", 2),
    PublicModel("four_link", "SimEngineMBD.example_models.four_link", "run_four_link", 3),
    PublicModel("slider_crank", "SimEngineMBD.example_models.slider_crank", "run_slider_crank", 3),
]
RA2021_TIMING_MODEL_BY_NAME = {model.name: model for model in RA2021_TIMING_MODELS}


@dataclass(frozen=True)
class RA2021OrderConfig:
    policy: str
    run_mode: str
    forms: tuple[str, ...]
    models: tuple[PublicModel, ...]
    groups: tuple[tuple[str, PublicModel], ...]
    step_sizes: tuple[float, ...]
    reference_h: float
    t_end: float
    run_public_code: bool
    full_ra2021_order_completed: bool


@dataclass(frozen=True)
class RA2021TimingConfig:
    policy: str
    run_mode: str
    forms: tuple[str, ...]
    models: tuple[PublicModel, ...]
    groups: tuple[tuple[str, PublicModel], ...]
    h: float
    t_end: float
    tolerance: float | None
    mode: str
    run_public_code: bool
    full_ra2021_timing_completed: bool


@dataclass(frozen=True)
class RA2021DoubleOrderConfig:
    policy: str
    run_mode: str
    forms: tuple[str, ...]
    step_sizes: tuple[float, ...]
    reference_h: float
    t_end: float
    tolerance: float | None
    run_public_code: bool
    full_ra2021_double_order_completed: bool


@dataclass(frozen=True)
class Gauss6FullVAConfig:
    policy: str
    run_mode: str
    step_sizes: tuple[float, ...]
    reference_h: float
    t_end: float
    run_model: bool


@dataclass(frozen=True)
class Gauss6PublicSingleConfig:
    policy: str
    run_mode: str
    step_sizes: tuple[float, ...]
    reference_h: float
    t_end: float
    run_model: bool


@dataclass(frozen=True)
class Gauss6PublicDoubleCoarseConfig:
    policy: str
    run_mode: str
    step_sizes: tuple[float, ...]
    reference_h: float
    t_end: float
    run_model: bool


@dataclass(frozen=True)
class Gauss6ClosedLoopConfig:
    policy: str
    run_mode: str
    models: tuple[str, ...]
    step_sizes: tuple[float, ...]
    reference_h: float
    t_end: float
    run_model: bool


@dataclass(frozen=True)
class HI2022Config:
    policy: str
    run_mode: str
    forms: tuple[str, ...]
    models: tuple[str, ...]
    step_sizes: tuple[float, ...]
    reference_h: float
    t_end: float
    tolerance_base: float
    run_public_code: bool
    full_hi2022_campaign_completed: bool


def scalarize(value: object) -> float:
    arr = np.asarray(value)
    if arr.size != 1:
        raise ValueError(f"expected scalar-like constraint value, got shape {arr.shape}")
    return float(arr.reshape(-1)[0])


def patch_congroup_scalar_assignments(module_names: tuple[str, ...]) -> list[str]:
    patched: list[str] = []

    for module_name in module_names:
        module = importlib.import_module(module_name)
        cls = module.ConGroup

        def get_phi(self, t):
            store = getattr(self, "\u03a6")
            for i, con in enumerate(self.cons):
                store[i, 0] = scalarize(con.get_phi(t))
            return store

        def get_gamma(self, t):
            store = getattr(self, "\u03b3")
            for i, con in enumerate(self.cons):
                store[i, 0] = scalarize(con.get_gamma(t))
            return store

        def get_nu(self, t):
            store = self.nu
            for i, con in enumerate(self.cons):
                store[i, 0] = scalarize(con.get_nu(t))
            return store

        cls.get_phi = get_phi
        cls.get_gamma = get_gamma
        cls.get_nu = get_nu
        patched.append(module_name)

    return patched


def patch_modern_numpy_scalar_assignments() -> list[str]:
    patched: list[str] = []

    def euler_to_rot_scalar(eps):
        phi, theta, psi = np.asarray(eps, dtype=float).reshape(-1)[:3]
        rot = np.zeros((3, 3))
        rot[0, 0] = -np.sin(psi) * np.sin(phi) * np.cos(theta) + np.cos(psi) * np.cos(phi)
        rot[0, 1] = -np.sin(psi) * np.cos(phi) - np.sin(phi) * np.cos(theta) * np.cos(psi)
        rot[0, 2] = np.sin(theta) * np.sin(phi)
        rot[1, 0] = np.sin(psi) * np.cos(theta) * np.cos(phi) + np.sin(phi) * np.cos(psi)
        rot[1, 1] = -np.sin(psi) * np.sin(phi) + np.cos(theta) * np.cos(psi) * np.cos(phi)
        rot[1, 2] = -np.sin(theta) * np.cos(phi)
        rot[2, 0] = np.sin(theta) * np.sin(psi)
        rot[2, 1] = np.sin(theta) * np.cos(psi)
        rot[2, 2] = np.cos(theta)
        return rot

    patched.extend(
        patch_congroup_scalar_assignments(
            ("SimEngineMBD.rA.gcons_ra", "SimEngineMBD.rp.gcons_rp", "SimEngineMBD.rEps.gcons_reps")
        )
    )
    physics = importlib.import_module("SimEngineMBD.utils.physics")
    reps_gcons = importlib.import_module("SimEngineMBD.rEps.gcons_reps")
    physics.euler_to_rot = euler_to_rot_scalar
    reps_gcons.euler_to_rot = euler_to_rot_scalar
    patched.extend(["SimEngineMBD.utils.physics.euler_to_rot", "SimEngineMBD.rEps.gcons_reps.euler_to_rot"])
    return patched


def read_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def write_json_atomic(path: Path, data: dict) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, sort_keys=True)
        handle.write("\n")
    os.replace(tmp, path)


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def read_csv_rows_if_exists(path: Path) -> list[dict[str, str]]:
    return read_csv_rows(path) if path.exists() else []


def git_commit(path: Path) -> str:
    try:
        return subprocess.check_output(["git", "-C", str(path), "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return "unknown"


def git_tree_paths(path: Path, scope: str = "origin/master") -> list[str]:
    if not path.exists():
        return []
    try:
        raw = subprocess.check_output(
            ["git", "-C", str(path), "ls-tree", "-r", "--name-only", scope],
            text=True,
            stderr=subprocess.DEVNULL,
        )
    except Exception:
        return []
    return [line.strip() for line in raw.splitlines() if line.strip()]


def filter_paths(paths: list[str], patterns: tuple[str, ...], prefix: str | None = None) -> list[str]:
    regex = re.compile("|".join(f"(?:{pattern})" for pattern in patterns), re.IGNORECASE)
    return [path for path in paths if (prefix is None or path.startswith(prefix)) and regex.search(path)]


def compact_roots(paths: list[str], limit: int = 8) -> str:
    if not paths:
        return "none"
    roots = sorted({"/".join(path.split("/")[:2]) for path in paths})
    return ";".join(roots[:limit])


def velocity_partitioning_code_search_rows() -> tuple[list[dict], dict]:
    rows: list[dict] = [
        {
            "source_id": "easychair_preprint_13546",
            "evidence_type": "literature_claim",
            "repository": "",
            "commit": "",
            "search_scope": "preprint_abstract_and_reference_snippet",
            "search_terms": "open-source Python code; public repository",
            "matched_path_count": 0,
            "matched_paths_or_roots": "public-code claim; visible reference points to 2021/ASME/rA-formulation",
            "status": "claim_requires_code_path_resolution",
            "interpretation": (
                "The 2024 performance-comparison preprint reports open-source Python code, "
                "but the visible public-repository reference is the 2021 rA-formulation entry."
            ),
        },
        {
            "source_id": "easychair_preprint_13546",
            "evidence_type": "pdf_reference_check",
            "repository": "https://easychair.org/publications/preprint/nVxd/open",
            "commit": "",
            "search_scope": "pdf_pages_1_to_2_reference_6",
            "search_terms": "open-source Python code; public repository; reference [6]",
            "matched_path_count": 1,
            "matched_paths_or_roots": (
                "https://github.com/uwsbel/public-metadata/tree/master/2021/ASME/rA-formulation"
            ),
            "status": "points_to_2021_rA_repo_not_distinct_vp_repo",
            "interpretation": (
                "The EasyChair PDF states that Python code is open-source, but the visible "
                "repository citation is the 2021 rA-formulation public-metadata path rather "
                "than a distinct velocity-partitioning implementation."
            ),
        },
        {
            "source_id": "easychair_preprint_13546",
            "evidence_type": "pdf_full_reference_extraction",
            "repository": "results/vp_easychair_preprint_13546.pdf",
            "commit": "",
            "search_scope": "full_easychair_pdf_text_extracted_2026_05_31",
            "search_terms": (
                "References [1]-[6]; open-source Python code; public repository; "
                "velocity coordinate partitioning"
            ),
            "matched_path_count": 1,
            "matched_paths_or_roots": (
                "reference [6] = https://github.com/uwsbel/public-metadata/tree/master/2021/ASME/rA-formulation"
            ),
            "status": "full_pdf_references_point_to_2021_rA_repo_only",
            "interpretation": (
                "A full text extraction of EasyChair preprint 13546 shows that the public-code "
                "reference [6] is the 2021 r-A formulation repository. The references list does "
                "not expose a distinct velocity-partitioning or Lie-group ODE partitioning code path."
            ),
        },
        {
            "source_id": "vp2024_kissel_bakke_negrut",
            "evidence_type": "crossref_primary_metadata_check",
            "repository": "https://api.crossref.org/works/10.1115/DETC2023-116950",
            "commit": "",
            "search_scope": "doi_10.1115_DETC2023_116950_metadata_2026_05_31",
            "search_terms": (
                "Using Velocity Partitioning in the rA Formulation; independent coordinates; "
                "dependent coordinates; Lie group integration; orientation matrix A"
            ),
            "matched_path_count": 1,
            "matched_paths_or_roots": (
                "https://asmedigitalcollection.asme.org/IDETC-CIE/proceedings/"
                "IDETC-CIE2023/87387/V010T10A003/1170764"
            ),
            "status": "method_identity_matches_coordinate_partitioning_wrapper",
            "interpretation": (
                "Crossref/ASME primary metadata for DOI 10.1115/DETC2023-116950 describes "
                "the VP method as direct integration of independent coordinates, recovery of "
                "dependent coordinates through position/velocity constraints, and Lie-group "
                "updates of orientation matrix A. This matches the local coordinate-partitioning "
                "wrapper rather than identifying a second distinct unresolved VP implementation."
            ),
        },
        {
            "source_id": "vp2024_kissel_bakke_negrut",
            "evidence_type": "public_web_search",
            "repository": "web",
            "commit": "",
            "search_scope": "web_search_2026_05_31",
            "search_terms": (
                '"Using Velocity Partitioning in the rA Formulation" GitHub; '
                "site:github.com/uwsbel velocity partitioning rA; 10.1115/1.4065254 code"
            ),
            "matched_path_count": 0,
            "matched_paths_or_roots": "none",
            "status": "no_distinct_repo_found",
            "interpretation": (
                "Public web search found the paper/preprint/code claim and the 2021 SBEL "
                "public-metadata repository, but did not expose a separate public velocity-"
                "partitioning code path."
            ),
        },
        {
            "source_id": "vp2024_kissel_bakke_negrut",
            "evidence_type": "metadata_abstract_check",
            "repository": (
                "https://www.citedrive.com/en/discovery/reducing-the-constrained-"
                "multibody-dynamics-problem-to-the-solution-of-a-system-of-odes-via-"
                "velocity-partitioning-and-lie-group-integration/"
            ),
            "commit": "",
            "search_scope": "citedrive_metadata_2026_05_31",
            "search_terms": "open-source Python code; public repository [2]; DOI 10.1115/1.4065254",
            "matched_path_count": 0,
            "matched_paths_or_roots": "public-code claim present; reference [2] URL not exposed in HTML",
            "status": "claim_without_resolved_code_path",
            "interpretation": (
                "CiteDrive metadata repeats the paper abstract's public Python-code claim, "
                "but the HTML exposes no clone URL or public-metadata path for reference [2]."
            ),
        },
        {
            "source_id": "vp2024_kissel_bakke_negrut",
            "evidence_type": "github_org_repo_inventory",
            "repository": "https://api.github.com/orgs/uwsbel/repos?per_page=100",
            "commit": "",
            "search_scope": "github_org_repos_2026_05_31",
            "search_terms": "uwsbel public repository names, descriptions, languages, pushed_at",
            "matched_path_count": 46,
            "matched_paths_or_roots": "uwsbel/sbel-reproducibility; no separate VP repository",
            "status": "no_distinct_vp_repo_found",
            "interpretation": (
                "GitHub org inventory listed the public uwsbel repositories, including "
                "sbel-reproducibility, but no repository name or description exposed a "
                "separate velocity-partitioning or performance-comparison implementation."
            ),
        },
        {
            "source_id": "vp2024_kissel_bakke_negrut",
            "evidence_type": "github_repository_search",
            "repository": "https://api.github.com/search/repositories",
            "commit": "",
            "search_scope": "github_repo_search_2026_05_31",
            "search_terms": '"velocity partitioning" Kissel Negrut; "10.1115/1.4065254"',
            "matched_path_count": 0,
            "matched_paths_or_roots": "none",
            "status": "no_repository_candidate_found",
            "interpretation": (
                "Unauthenticated GitHub repository search returned zero repository candidates "
                "for the VP title/author/DOI terms. GitHub code search requires authentication, "
                "so this does not replace the local mirror content searches."
            ),
        },
        {
            "source_id": "vp2024_kissel_bakke_negrut",
            "evidence_type": "local_reimplementation",
            "repository": "run_coarse_four_example_order.py",
            "commit": "",
            "search_scope": "coordinate_partitioning_rA",
            "search_terms": (
                "10.1115/1.4065254 coordinate partitioning; pivoted QR dependent "
                "coordinates; explicit independent velocity update"
            ),
            "matched_path_count": 1,
            "matched_paths_or_roots": "run_vp2024_coordinate_partitioning_rows",
            "status": "implemented_partial_vp_baseline",
            "interpretation": (
                "Implemented the coordinate-partitioning rA baseline from the published "
                "algorithm on the 2021 public rA geometry. Primary metadata for the ASME "
                "2023 VP paper indicates that the previous 'Lie-group ODE partitioning' label "
                "is an alias of this coordinate-partitioning VP method, not a separate method."
            ),
        },
        {
            "source_id": "vp2024_kissel_bakke_negrut",
            "evidence_type": "local_workspace_full_text_scan",
            "repository": "workspace",
            "commit": "",
            "search_scope": "pdf_and_text_scan_2026_05_31",
            "search_terms": (
                "4065254; velocity partition; Reducing the Constrained Multibody Dynamics "
                "Problem; Lie Group ODE"
            ),
            "matched_path_count": 0,
            "matched_paths_or_roots": "none",
            "status": "no_local_pdf_or_code_found",
            "interpretation": (
                "Workspace scan found the v047/v048 audit/manuscript references, the targeted "
                "EasyChair PDF extraction artifact, and the implemented coordinate-partitioning "
                "wrapper; no source file, repository path, or symbol for the separate Lie-group "
                "ODE partitioning implementation was present."
            ),
        }
    ]
    repository_summaries: list[dict] = []
    for label, repo in (
        ("sbel-reproducibility", SBEL_ROOT),
        ("public-metadata", PUBLIC_METADATA_ROOT),
    ):
        repo_summary = {
            "repository": label,
            "root": str(repo),
            "commit": git_commit(repo),
            "searched_refs": ",".join(VP_SEARCH_REFS),
            "tree_path_count": 0,
            "exact_velocity_partitioning_path_hits": 0,
            "mechanism_candidate_2024_path_hits": 0,
            "mechanism_candidate_roots": "none",
        }
        all_mechanism_hits: list[str] = []
        for ref in VP_SEARCH_REFS:
            paths = git_tree_paths(repo, ref)
            exact_hits = filter_paths(paths, VP_EXACT_PATH_PATTERNS)
            mechanism_hits_2024 = filter_paths(paths, VP_MECHANISM_PATTERNS, prefix="2024/")
            repo_summary["tree_path_count"] += len(paths)
            repo_summary["exact_velocity_partitioning_path_hits"] += len(exact_hits)
            repo_summary["mechanism_candidate_2024_path_hits"] += len(mechanism_hits_2024)
            all_mechanism_hits.extend(mechanism_hits_2024)
            rows.append(
                {
                    "source_id": "vp2024_kissel_bakke_negrut",
                    "evidence_type": "local_git_tree_path_search",
                    "repository": label,
                    "commit": git_commit(repo),
                    "search_scope": f"{ref}_all_paths",
                    "search_terms": "|".join(VP_EXACT_PATH_PATTERNS),
                    "matched_path_count": len(exact_hits),
                    "matched_paths_or_roots": compact_roots(exact_hits),
                    "status": "not_resolved",
                    "interpretation": (
                        "No pathname identifies a distinct velocity-partitioning or "
                        "performance-comparison code directory in this ref."
                    ),
                }
            )
            rows.append(
                {
                    "source_id": "vp2024_kissel_bakke_negrut",
                    "evidence_type": "local_git_tree_mechanism_candidate_search",
                    "repository": label,
                    "commit": git_commit(repo),
                    "search_scope": f"{ref}_2024_paths",
                    "search_terms": "|".join(VP_MECHANISM_PATTERNS),
                    "matched_path_count": len(mechanism_hits_2024),
                    "matched_paths_or_roots": compact_roots(mechanism_hits_2024),
                    "status": "candidate_rejected" if mechanism_hits_2024 else "no_mechanism_hits",
                    "interpretation": (
                        "2024 mechanism-name hits are rooted in unrelated MBD-NODE, "
                        "PathFollowingSim2real, or RSSworkshop paths when present; "
                        "they are not the velocity-partitioning baseline."
                    ),
                }
            )
        repo_summary["mechanism_candidate_roots"] = compact_roots(all_mechanism_hits)
        repository_summaries.append(
            repo_summary
        )

    summary = {
        "status": VP_CODE_STATUS,
        "row_count": len(rows),
        "relevant_code_path_resolved": False,
        "method_identity_resolved": True,
        "resolved_method_alias": {
            "alias": "vp2024_lie_group_ode_partitioning",
            "implemented_as": "vp2024_coordinate_partitioning_rA",
        },
        "searched_refs": list(VP_SEARCH_REFS),
        "public_web_search_status": "no_distinct_repo_found",
        "easychair_visible_repository_reference": (
            "https://github.com/uwsbel/public-metadata/tree/master/2021/ASME/rA-formulation"
        ),
        "searched_repositories": repository_summaries,
    }
    return rows, summary


def model_callable(model: PublicModel) -> Callable:
    return getattr(importlib.import_module(model.module), model.run_name)


def clear_simengine_modules() -> None:
    for name in list(sys.modules):
        if name == "SimEngineMBD" or name.startswith("SimEngineMBD."):
            sys.modules.pop(name, None)


def switch_simengine_root(root: Path) -> None:
    for path in (str(SBEL_C2), str(HI2022_ROOT)):
        while path in sys.path:
            sys.path.remove(path)
    sys.path.insert(0, str(root))
    clear_simengine_modules()


def patch_hi2022_modern_numpy_scalar_assignments() -> list[str]:
    return patch_congroup_scalar_assignments(("SimEngineMBD.rA.gcons_ra", "SimEngineMBD.rA_half.gcons_ra_half"))


def run_public_model_state_history(model: PublicModel, args: list[str]) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Replay a public example loop when its plotting-only diagnostics fail under modern NumPy."""
    module = importlib.import_module(model.module)
    setup = getattr(module, f"setup_{model.name}")
    system, params = setup(args)
    system.initialize()
    t_steps = int(params.t_end / params.h)
    t_grid = np.linspace(0.0, params.t_end, t_steps, endpoint=True)
    pos_data = np.zeros((system.nb, 3, t_steps))
    vel_data = np.zeros((system.nb, 3, t_steps))
    acc_data = np.zeros((system.nb, 3, t_steps))
    num_iters = np.zeros(t_steps)
    for i, t in enumerate(t_grid):
        system.do_step(i, t)
        num_iters[i] = system.k
        for j, body in enumerate(system.bodies):
            pos_data[j, :, i] = np.asarray(body.r).reshape(3)
            vel_data[j, :, i] = np.asarray(body.dr).reshape(3)
            acc_data[j, :, i] = np.asarray(body.ddr).reshape(3)
    return pos_data, vel_data, acc_data, num_iters, t_grid


def hi2022_tolerance(form: str, h: float, tolerance_base: float) -> float:
    if form == "rA":
        return tolerance_base / h**2
    return tolerance_base


def hi2022_model_callable(model_name: str) -> Callable:
    return getattr(importlib.import_module(f"SimEngineMBD.example_models.{model_name}"), f"run_{model_name}")


def run_hi2022_model_state_history(
    model_name: str, form: str, mode: str, h: float, t_end: float, tolerance: float
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    module = importlib.import_module(f"SimEngineMBD.example_models.{model_name}")
    setup = getattr(module, f"setup_{model_name}")
    args = [
        "--form",
        form,
        "--mode",
        mode,
        "--tol",
        str(tolerance),
        "--step_size",
        str(h),
        "-t",
        str(t_end),
        "--log",
        "warning",
        "--no-plot",
    ]
    system, params = setup(args)
    system.initialize()
    t_steps = round(params.t_end / params.h)
    if model_name == "single_pendulum":
        t_grid = np.linspace(0.0, params.t_end, t_steps, endpoint=True)
    else:
        t_grid = np.linspace(params.h, params.t_end, t_steps, endpoint=True)
    pos_data = np.zeros((system.nb, 3, t_steps))
    vel_data = np.zeros((system.nb, 3, t_steps))
    acc_data = np.zeros((system.nb, 3, t_steps))
    num_iters = np.zeros(t_steps)
    for i, t in enumerate(t_grid):
        system.do_step(i, t)
        num_iters[i] = system.k
        for j, body in enumerate(system.bodies):
            pos_data[j, :, i] = np.asarray(body.r).reshape(3)
            vel_data[j, :, i] = np.asarray(body.dr).reshape(3)
            acc_data[j, :, i] = np.asarray(body.ddr).reshape(3)
    return pos_data, vel_data, acc_data, num_iters, t_grid


def run_hi2022_model(model_name: str, form: str, mode: str, h: float, t_end: float, tolerance: float) -> dict:
    started = time.perf_counter()
    execution_path = "public_run_function"
    if model_name in {"four_link", "slider_crank"}:
        pos, vel, acc, iters, t_grid = run_hi2022_model_state_history(model_name, form, mode, h, t_end, tolerance)
        execution_path = "state_history_replay"
    else:
        args = [
            "--form",
            form,
            "--mode",
            mode,
            "--tol",
            str(tolerance),
            "--step_size",
            str(h),
            "-t",
            str(t_end),
            "--log",
            "warning",
            "--no-plot",
        ]
        out = hi2022_model_callable(model_name)(args)
        if len(out) == 5:
            pos, vel, acc, iters, t_grid = out
        elif model_name == "slider_crank" and len(out) == 8:
            pos, vel, acc, _, _, _, iters, t_grid = out
        else:
            raise ValueError(f"unexpected 2022 model output length for {model_name}: {len(out)}")
    return {
        "pos": pos,
        "vel": vel,
        "acc": acc,
        "iters": iters,
        "t_grid": t_grid,
        "runtime_sec": time.perf_counter() - started,
        "avg_iterations": float(np.mean(iters)),
        "max_iterations": float(np.max(iters)),
        "execution_path": execution_path,
    }


def import_v047_single_fullva_module():
    module_name = "v047_cylindrical_chain_pipeline_for_v048"
    if module_name in sys.modules:
        return sys.modules[module_name]
    path = WORK_ROOT / "v047_cylindrical_chain_pipeline" / "run_v047.py"
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"could not load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def run_public_model(model: PublicModel, form: str, mode: str, h: float, t_end: float, tol: float | None) -> dict:
    args = [
        "--form",
        form,
        "--mode",
        mode,
        "--step_size",
        str(h),
        "--end_time",
        str(t_end),
        "--log",
        "warning",
        "--no-plot",
    ]
    if tol is not None:
        args.extend(["--tol", str(tol)])

    started = time.perf_counter()
    if model.name in {"double_pendulum", "four_link"}:
        pos, vel, acc, iters, t_grid = run_public_model_state_history(model, args)
    else:
        pos, vel, acc, iters, t_grid = model_callable(model)(args)
    return {
        "pos": pos,
        "vel": vel,
        "acc": acc,
        "iters": iters,
        "t_grid": t_grid,
        "runtime_sec": time.perf_counter() - started,
        "avg_iterations": float(np.mean(iters)),
        "max_iterations": float(np.max(iters)),
    }


def final_error(reference: dict, candidate: dict, key: str) -> float:
    return float(np.max(np.abs(reference[key][:, :, -1] - candidate[key][:, :, -1])))


def estimate_order(hs: list[float], errors: list[float]) -> float:
    clean = [(h, e) for h, e in zip(hs, errors) if np.isfinite(e) and e > 0.0]
    if len(clean) < 2:
        return float("nan")
    slope, _ = np.polyfit(np.log([h for h, _ in clean]), np.log([e for _, e in clean]), 1)
    return float(slope)


def finite_or_none(value: float) -> float | None:
    return value if np.isfinite(value) else None


def as_float(row: dict, key: str) -> float:
    try:
        return float(row.get(key, "nan"))
    except (TypeError, ValueError):
        return float("nan")


def format_float(value: float | None) -> str:
    if value is None:
        return "nan"
    return "nan" if not np.isfinite(value) else f"{value:.16e}"


def finite_sum(values: list[float]) -> float:
    clean = [value for value in values if np.isfinite(value)]
    return float(sum(clean)) if clean else float("nan")


def failure_status(prefix: str, exc: Exception) -> str:
    message = str(exc).replace("\n", " ").replace("\r", " ")
    return f"{prefix}:{type(exc).__name__}:{message}"


def compare_common_grid_arrays(reference: dict, candidate: dict, key: str) -> np.ndarray:
    ratio_candidate_to_reference = candidate["h"] / reference["h"]
    if ratio_candidate_to_reference >= 1.0:
        stride = int(round(ratio_candidate_to_reference))
        if not np.isclose(stride, ratio_candidate_to_reference):
            raise ValueError(f"reference h={reference['h']} is not nested in candidate h={candidate['h']}")
        ref = reference[key][..., ::stride]
        cand = candidate[key]
    else:
        ratio_reference_to_candidate = reference["h"] / candidate["h"]
        stride = int(round(ratio_reference_to_candidate))
        if not np.isclose(stride, ratio_reference_to_candidate):
            raise ValueError(f"candidate h={candidate['h']} is not nested in reference h={reference['h']}")
        ref = reference[key]
        cand = candidate[key][..., ::stride]
    if ref.shape != cand.shape:
        raise ValueError(f"{key} shape mismatch on common grid {ref.shape} vs {cand.shape}")
    return cand - ref


def compare_common_grid_with_acc(reference: dict, candidate: dict) -> dict:
    pos_diff = compare_common_grid_arrays(reference, candidate, "pos")
    vel_diff = compare_common_grid_arrays(reference, candidate, "vel")
    acc_diff = compare_common_grid_arrays(reference, candidate, "acc")
    return {
        "pos_traj_linf": float(np.max(np.abs(pos_diff))),
        "pos_traj_l2": float(np.linalg.norm(pos_diff.reshape(-1))),
        "pos_final_linf": float(np.max(np.abs(pos_diff[:, :, -1]))),
        "pos_final_l2": float(np.linalg.norm(pos_diff[:, :, -1].reshape(-1))),
        "vel_traj_linf": float(np.max(np.abs(vel_diff))),
        "vel_traj_l2": float(np.linalg.norm(vel_diff.reshape(-1))),
        "vel_final_linf": float(np.max(np.abs(vel_diff[:, :, -1]))),
        "vel_final_l2": float(np.linalg.norm(vel_diff[:, :, -1].reshape(-1))),
        "acc_traj_linf": float(np.max(np.abs(acc_diff))),
        "acc_traj_l2": float(np.linalg.norm(acc_diff.reshape(-1))),
        "acc_final_linf": float(np.max(np.abs(acc_diff[:, :, -1]))),
        "acc_final_l2": float(np.linalg.norm(acc_diff[:, :, -1].reshape(-1))),
    }


def compare_common_grid_lambda(reference: dict, candidate: dict) -> float:
    lam_diff = compare_common_grid_arrays(reference, candidate, "lambda")
    return float(np.max(np.abs(lam_diff)))


def parse_csv_tokens(raw: str) -> list[str]:
    return [token.strip() for token in raw.split(",") if token.strip()]


def parse_float_csv(raw: str) -> tuple[float, ...]:
    values = tuple(float(token) for token in parse_csv_tokens(raw))
    if not values:
        raise ValueError("at least one step size is required")
    return values


def contains_source_policy_1e4(values: tuple[float, ...]) -> bool:
    return any(float(value) <= SOURCE_POLICY_1E4_H + SOURCE_POLICY_1E4_EPS for value in values)


def require_source_policy_1e4_allow(
    parser: argparse.ArgumentParser,
    allowed: bool,
    label: str,
    values: tuple[float, ...],
) -> None:
    if contains_source_policy_1e4(values) and not allowed:
        parser.error(
            f"{label} touches h<=1e-4 or reference_h<=1e-4; "
            "use coarse-first rows or pass --allow-source-policy-1e-4 for an explicit source-policy reproduction run"
        )


def select_forms(raw: str) -> tuple[str, ...]:
    forms = tuple(parse_csv_tokens(raw))
    invalid = [form for form in forms if form not in RA2021_FORMS]
    if invalid:
        raise ValueError(f"unknown 2021 forms: {invalid}; allowed={RA2021_FORMS}")
    if not forms:
        raise ValueError("at least one form is required")
    return forms


def select_models(raw: str) -> tuple[PublicModel, ...]:
    names = parse_csv_tokens(raw)
    invalid = [name for name in names if name not in RA2021_MODEL_BY_NAME]
    if invalid:
        raise ValueError(f"unknown 2021 models: {invalid}; allowed={sorted(RA2021_MODEL_BY_NAME)}")
    if not names:
        raise ValueError("at least one model is required")
    return tuple(RA2021_MODEL_BY_NAME[name] for name in names)


def select_timing_models(raw: str) -> tuple[PublicModel, ...]:
    names = parse_csv_tokens(raw)
    invalid = [name for name in names if name not in RA2021_TIMING_MODEL_BY_NAME]
    if invalid:
        raise ValueError(f"unknown 2021 timing models: {invalid}; allowed={sorted(RA2021_TIMING_MODEL_BY_NAME)}")
    if not names:
        raise ValueError("at least one timing model is required")
    return tuple(RA2021_TIMING_MODEL_BY_NAME[name] for name in names)


def cartesian_groups(forms: tuple[str, ...], models: tuple[PublicModel, ...]) -> tuple[tuple[str, PublicModel], ...]:
    return tuple((form, model) for form in forms for model in models)


def unique_group_forms(groups: tuple[tuple[str, PublicModel], ...]) -> tuple[str, ...]:
    seen: list[str] = []
    for form, _ in groups:
        if form not in seen:
            seen.append(form)
    return tuple(seen)


def unique_group_models(groups: tuple[tuple[str, PublicModel], ...]) -> tuple[PublicModel, ...]:
    seen: list[PublicModel] = []
    names: set[str] = set()
    for _, model in groups:
        if model.name not in names:
            names.add(model.name)
            seen.append(model)
    return tuple(seen)


def select_groups(raw: str) -> tuple[tuple[str, PublicModel], ...]:
    groups: list[tuple[str, PublicModel]] = []
    for token in parse_csv_tokens(raw):
        if ":" not in token:
            raise ValueError(f"invalid 2021 group '{token}'; expected form:model")
        form, model_name = (part.strip() for part in token.split(":", 1))
        if form not in RA2021_FORMS:
            raise ValueError(f"unknown 2021 form in group '{token}'; allowed={RA2021_FORMS}")
        if model_name not in RA2021_MODEL_BY_NAME:
            raise ValueError(f"unknown 2021 model in group '{token}'; allowed={sorted(RA2021_MODEL_BY_NAME)}")
        groups.append((form, RA2021_MODEL_BY_NAME[model_name]))
    if not groups:
        raise ValueError("at least one 2021 group is required")
    return tuple(groups)


def select_hi2022_forms(raw: str) -> tuple[str, ...]:
    forms = tuple(parse_csv_tokens(raw))
    invalid = [form for form in forms if form not in HI2022_FORMS]
    if invalid:
        raise ValueError(f"unknown 2022 half-implicit forms: {invalid}; allowed={HI2022_FORMS}")
    if not forms:
        raise ValueError("at least one 2022 half-implicit form is required")
    return forms


def select_hi2022_models(raw: str) -> tuple[str, ...]:
    models = tuple(parse_csv_tokens(raw))
    invalid = [model for model in models if model not in HI2022_MODELS]
    if invalid:
        raise ValueError(f"unknown 2022 half-implicit models: {invalid}; allowed={HI2022_MODELS}")
    if not models:
        raise ValueError("at least one 2022 half-implicit model is required")
    return models


def select_gauss6_closed_loop_models(raw: str) -> tuple[str, ...]:
    models = tuple(parse_csv_tokens(raw))
    allowed = ("four_link", "slider_crank")
    invalid = [model for model in models if model not in allowed]
    if invalid:
        raise ValueError(f"unknown closed-loop Gauss6/FullVA models: {invalid}; allowed={allowed}")
    if not models:
        raise ValueError("at least one closed-loop Gauss6/FullVA model is required")
    return models


def public_step_count(t_end: float, h: float) -> int:
    return int(round(t_end / h))


def ra2021_workload_estimate(config: RA2021OrderConfig) -> list[dict]:
    full_group_steps = public_step_count(RA2021_PUBLIC_T_END, RA2021_PUBLIC_REFERENCE_H) + sum(
        public_step_count(RA2021_PUBLIC_T_END, h) for h in RA2021_ORDER_STEP_SIZES
    )
    selected_group_steps = public_step_count(config.t_end, config.reference_h) + sum(
        public_step_count(config.t_end, h) for h in config.step_sizes
    )
    selected_group_count = len(config.groups)
    full_group_count = len(RA2021_FORMS) * len(RA2021_ORDER_MODELS)
    return [
        {
            "scope": "ra2021_full_public_order_policy",
            "policy": "ra2021_public_order_policy",
            "forms": ",".join(RA2021_FORMS),
            "models": ",".join(model.name for model in RA2021_ORDER_MODELS),
            "groups": ",".join(f"{form}:{model.name}" for form, model in cartesian_groups(tuple(RA2021_FORMS), tuple(RA2021_ORDER_MODELS))),
            "t_end": f"{RA2021_PUBLIC_T_END:.16e}",
            "reference_h": f"{RA2021_PUBLIC_REFERENCE_H:.16e}",
            "step_sizes": ",".join(f"{h:.16e}" for h in RA2021_ORDER_STEP_SIZES),
            "form_model_groups": full_group_count,
            "estimated_public_steps_per_group": full_group_steps,
            "estimated_public_steps_total": full_group_count * full_group_steps,
            "evidence_status": "not_run_by_default",
            "note": "Includes h=1e-4 over T=3 and is intentionally opt-in.",
        },
        {
            "scope": "ra2021_selected_run",
            "policy": config.policy,
            "forms": ",".join(config.forms),
            "models": ",".join(model.name for model in config.models),
            "groups": ",".join(f"{form}:{model.name}" for form, model in config.groups),
            "t_end": f"{config.t_end:.16e}",
            "reference_h": f"{config.reference_h:.16e}",
            "step_sizes": ",".join(f"{h:.16e}" for h in config.step_sizes),
            "form_model_groups": selected_group_count,
            "estimated_public_steps_per_group": selected_group_steps,
            "estimated_public_steps_total": selected_group_count * selected_group_steps,
            "evidence_status": "will_run" if config.run_public_code else "plan_only",
            "note": "Selected workload is a scaffold/pilot unless it exactly matches the full public policy.",
        },
    ]


def hi2022_workload_estimate(config: HI2022Config) -> list[dict]:
    full_group_count = len(HI2022_FORMS) * len(HI2022_MODELS)
    full_steps_per_form = sum(public_step_count(HI2022_PUBLIC_T_END, h) for h in HI2022_PUBLIC_STEP_SIZES)
    selected_steps_per_form = public_step_count(config.t_end, config.reference_h) + sum(
        public_step_count(config.t_end, h) for h in config.step_sizes
    )
    selected_group_count = len(config.forms) * len(config.models)
    return [
        {
            "scope": "hi2022_full_open_loop_policy",
            "policy": "hi2022_public_open_loop_or_closed_loop_policy",
            "models": ",".join(HI2022_MODELS),
            "forms": ",".join(HI2022_FORMS),
            "t_end": f"{HI2022_PUBLIC_T_END:.16e}",
            "reference_h": "source_policy_reference_or_saved_ground_truth",
            "step_sizes": ",".join(f"{h:.16e}" for h in HI2022_PUBLIC_STEP_SIZES),
            "form_model_groups": full_group_count,
            "estimated_public_steps_per_form": full_steps_per_form,
            "estimated_public_steps_total": full_group_count * full_steps_per_form,
            "evidence_status": "not_run_by_default",
            "note": "Mirrors the source scripts' T=8 step-size family where encoded; full campaign is opt-in.",
        },
        {
            "scope": "hi2022_selected_run",
            "policy": config.policy,
            "models": ",".join(config.models),
            "forms": ",".join(config.forms),
            "t_end": f"{config.t_end:.16e}",
            "reference_h": f"{config.reference_h:.16e}",
            "step_sizes": ",".join(f"{h:.16e}" for h in config.step_sizes),
            "form_model_groups": selected_group_count,
            "estimated_public_steps_per_form": selected_steps_per_form,
            "estimated_public_steps_total": selected_group_count * selected_steps_per_form,
            "evidence_status": "will_run" if config.run_public_code else "plan_only",
            "note": "Bounded three-step pilot against an in-suite rA reference, not the full source-paper T=8 campaign.",
        },
    ]


def benchmark_run_plan() -> list[dict]:
    cases = read_json(CASES_JSON)
    rows = []
    for case in cases.get("cases", []):
        rows.append(
            {
                "case_id": case.get("case_id", ""),
                "group_id": case.get("group_id", ""),
                "model": case.get("model", ""),
                "baseline_methods": ";".join(case.get("baseline_methods", [])),
                "current_status": case.get("current_status", ""),
                "required_gauss6_run": str(case.get("required_gauss6_run", "")),
                "metrics": ";".join(case.get("metrics", [])),
            }
        )
    return rows


def run_ra2021_order_rows(config: RA2021OrderConfig) -> tuple[list[dict], dict]:
    forms = list(config.forms)
    models = list(config.models)
    groups = list(config.groups)
    t_end = config.t_end
    reference_h = config.reference_h
    step_sizes = list(config.step_sizes)
    policy = config.policy

    rows: list[dict] = []
    order_groups: dict[str, dict] = {}
    for form, model in groups:
        reference = None
        reference_status = "ok" if config.run_public_code else "planned_not_run"
        reference_runtime_sec = float("nan")
        reference_execution_path = "not_run"
        if config.run_public_code:
            try:
                reference = run_public_model(model, form, "kinematics", reference_h, t_end, tol=1e-12)
                reference_runtime_sec = float(reference["runtime_sec"])
            except Exception as exc:  # noqa: BLE001 - record group-level reference failure.
                reference_status = failure_status("reference_failed", exc)
        pos_errors: list[float] = []
        vel_errors: list[float] = []
        acc_errors: list[float] = []
        for h in step_sizes:
            row = {
                "policy": policy,
                "source_suite": "ra2021_taves_kissel_negrut",
                "case_id": f"ra2021_{model.name}_order",
                "form": form,
                "model": model.name,
                "mode": "dynamics",
                "t_end": t_end,
                "reference_mode": "kinematics",
                "reference_h": reference_h,
                "reference_status": reference_status,
                "reference_runtime_sec": "nan" if not np.isfinite(reference_runtime_sec) else f"{reference_runtime_sec:.16e}",
                "h": h,
                "status": "ok",
                "pos_final_linf": "nan",
                "vel_final_linf": "nan",
                "acc_final_linf": "nan",
                "avg_iterations": "nan",
                "max_iterations": "nan",
                "runtime_sec": "nan",
            }
            if not config.run_public_code:
                row["status"] = "planned_not_run"
                pos_error = vel_error = acc_error = float("nan")
            elif reference is None:
                row["status"] = reference_status
                pos_error = vel_error = acc_error = float("nan")
            else:
                try:
                    candidate = run_public_model(model, form, "dynamics", h, t_end, tol=None)
                    pos_error = final_error(reference, candidate, "pos")
                    vel_error = final_error(reference, candidate, "vel")
                    acc_error = final_error(reference, candidate, "acc")
                    row.update(
                        {
                            "pos_final_linf": f"{pos_error:.16e}",
                            "vel_final_linf": f"{vel_error:.16e}",
                            "acc_final_linf": f"{acc_error:.16e}",
                            "avg_iterations": f"{candidate['avg_iterations']:.16e}",
                            "max_iterations": f"{candidate['max_iterations']:.16e}",
                            "runtime_sec": f"{candidate['runtime_sec']:.16e}",
                        }
                    )
                except Exception as exc:  # noqa: BLE001 - record and continue.
                    row["status"] = failure_status("failed", exc)
                    pos_error = vel_error = acc_error = float("nan")
            pos_errors.append(pos_error)
            vel_errors.append(vel_error)
            acc_errors.append(acc_error)
            rows.append(row)

        key = f"{form}:{model.name}"
        order_groups[key] = {
            "pos_final_linf_order": finite_or_none(estimate_order(step_sizes, pos_errors)),
            "vel_final_linf_order": finite_or_none(estimate_order(step_sizes, vel_errors)),
            "acc_final_linf_order": finite_or_none(estimate_order(step_sizes, acc_errors)),
            "step_sizes": step_sizes,
            "completed": config.full_ra2021_order_completed,
            "reference_status": reference_status,
            "public_step_trio_completed": bool(
                config.run_public_code
                and reference_status == "ok"
                and np.isclose(config.t_end, RA2021_PUBLIC_T_END)
                and np.isclose(config.reference_h, RA2021_PUBLIC_REFERENCE_H)
                and list(config.step_sizes) == RA2021_ORDER_STEP_SIZES
                and all(row["status"] == "ok" for row in rows if row["form"] == form and row["model"] == model.name)
            ),
        }

    public_step_trio_group_count = sum(1 for group in order_groups.values() if group["public_step_trio_completed"])
    summary = {
        "policy": policy,
        "full_ra2021_order_completed": config.full_ra2021_order_completed,
        "public_step_trio_group_count": public_step_trio_group_count,
        "public_step_trio_required_group_count": len(RA2021_FORMS) * len(RA2021_ORDER_MODELS),
        "row_count": len(rows),
        "ok_row_count": sum(1 for row in rows if row["status"] == "ok"),
        "planned_row_count": sum(1 for row in rows if row["status"] == "planned_not_run"),
        "run_public_code": config.run_public_code,
        "selected_forms": forms,
        "selected_models": [model.name for model in models],
        "selected_groups": [f"{form}:{model.name}" for form, model in groups],
        "selected_step_sizes": step_sizes,
        "selected_t_end": t_end,
        "selected_reference_h": reference_h,
        "groups": order_groups,
    }
    return rows, summary


def run_ra2021_timing_rows(config: RA2021TimingConfig) -> tuple[list[dict], dict]:
    if config.run_public_code:
        switch_simengine_root(SBEL_C2)
        patch_modern_numpy_scalar_assignments()

    rows: list[dict] = []
    group_summaries: dict[str, dict] = {}
    exact_public_timing_policy = bool(
        np.isclose(config.t_end, RA2021_PUBLIC_T_END)
        and np.isclose(config.h, RA2021_PUBLIC_REFERENCE_H)
        and config.tolerance is None
        and config.mode == "dynamics"
    )
    notes = (
        "2021 public-code timing/iteration row matching time.py: T=3, h=1e-3, dynamics mode, "
        "and no explicit --tol so the public dynamics default tolerance is used. "
        "This fills the public four-example performance ledger, including double_pendulum, "
        "whose public order-analysis script has no kinematic-reference order row."
    )
    for form, model in config.groups:
        row = {
            "policy": config.policy,
            "source_suite": "ra2021_taves_kissel_negrut",
            "case_id": f"ra2021_{model.name}_{config.mode}_timing",
            "form": form,
            "model": model.name,
            "mode": config.mode,
            "t_end": config.t_end,
            "h": config.h,
            "tolerance": "nan" if config.tolerance is None else f"{config.tolerance:.16e}",
            "public_timing_policy": exact_public_timing_policy,
            "status": "planned_not_run",
            "steps": "nan",
            "runtime_sec": "nan",
            "avg_iterations": "nan",
            "max_iterations": "nan",
            "notes": notes,
        }
        if config.run_public_code:
            try:
                candidate = run_public_model(model, form, config.mode, config.h, config.t_end, tol=config.tolerance)
                row.update(
                    {
                        "status": "ok",
                        "steps": public_step_count(config.t_end, config.h),
                        "runtime_sec": f"{candidate['runtime_sec']:.16e}",
                        "avg_iterations": f"{candidate['avg_iterations']:.16e}",
                        "max_iterations": f"{candidate['max_iterations']:.16e}",
                    }
                )
            except Exception as exc:  # noqa: BLE001 - keep public-code failures audit-visible.
                row["status"] = failure_status("failed", exc)
        rows.append(row)
        group_summaries[f"{form}:{model.name}"] = {
            "status": row["status"],
            "runtime_sec": as_float(row, "runtime_sec"),
            "avg_iterations": as_float(row, "avg_iterations"),
            "max_iterations": as_float(row, "max_iterations"),
            "public_timing_policy": exact_public_timing_policy,
        }

    ok_row_count = sum(1 for row in rows if row["status"] == "ok")
    public_timing_rows_completed = sum(
        1 for row in rows if row["status"] == "ok" and bool(row.get("public_timing_policy"))
    )
    public_timing_required_count = len(RA2021_FORMS) * len(RA2021_TIMING_MODELS)
    return rows, {
        "policy": config.policy,
        "run_mode": config.run_mode,
        "run_public_code": config.run_public_code,
        "full_ra2021_timing_completed": bool(
            config.full_ra2021_timing_completed and public_timing_rows_completed == public_timing_required_count
        ),
        "row_count": len(rows),
        "ok_row_count": ok_row_count,
        "planned_row_count": sum(1 for row in rows if row["status"] == "planned_not_run"),
        "selected_rows_completed": bool(rows and ok_row_count == len(rows)),
        "public_timing_policy": exact_public_timing_policy,
        "public_timing_rows_completed": public_timing_rows_completed,
        "public_timing_required_count": public_timing_required_count,
        "selected_forms": list(config.forms),
        "selected_models": [model.name for model in config.models],
        "selected_groups": [f"{form}:{model.name}" for form, model in config.groups],
        "selected_h": config.h,
        "selected_t_end": config.t_end,
        "selected_tolerance": config.tolerance,
        "mode": config.mode,
        "groups": group_summaries,
        "notes": notes,
    }


def run_ra2021_double_pendulum_order_rows(config: RA2021DoubleOrderConfig) -> tuple[list[dict], dict]:
    if config.run_public_code:
        switch_simengine_root(SBEL_C2)
        patch_modern_numpy_scalar_assignments()

    model = RA2021_TIMING_MODEL_BY_NAME["double_pendulum"]
    rows: list[dict] = []
    groups: dict[str, dict] = {}
    exact_policy = bool(
        np.isclose(config.t_end, RA2021_PUBLIC_T_END)
        and np.isclose(config.reference_h, RA2021_DOUBLE_ORDER_REFERENCE_H)
        and list(config.step_sizes) == RA2021_DOUBLE_ORDER_STEP_SIZES
        and config.tolerance is None
    )
    notes = (
        "2021 public double_pendulum dynamic self-reference order row. The public "
        "order_analysis.py script does not include double_pendulum because the model "
        "has no kinematics mode; this row compares public dynamics final states "
        "against a finer public-dynamics reference, not against a kinematic reference."
    )
    for form in config.forms:
        reference = None
        reference_status = "ok" if config.run_public_code else "planned_not_run"
        reference_runtime_sec = float("nan")
        if config.run_public_code:
            try:
                reference = run_public_model(
                    model,
                    form,
                    "dynamics",
                    config.reference_h,
                    config.t_end,
                    tol=config.tolerance,
                )
                reference_runtime_sec = float(reference["runtime_sec"])
            except Exception as exc:  # noqa: BLE001 - record group-level reference failure.
                reference_status = failure_status("reference_failed", exc)
        pos_errors: list[float] = []
        vel_errors: list[float] = []
        acc_errors: list[float] = []
        for h in config.step_sizes:
            row = {
                "policy": config.policy,
                "source_suite": "ra2021_taves_kissel_negrut",
                "case_id": "ra2021_double_pendulum_dynamic_self_reference_order",
                "form": form,
                "model": "double_pendulum",
                "mode": "dynamics",
                "t_end": config.t_end,
                "reference_mode": "dynamics",
                "reference_policy": "finer_public_dynamics_self_reference",
                "reference_h": config.reference_h,
                "reference_status": reference_status,
                "reference_runtime_sec": "nan"
                if not np.isfinite(reference_runtime_sec)
                else f"{reference_runtime_sec:.16e}",
                "h": h,
                "tolerance": "nan" if config.tolerance is None else f"{config.tolerance:.16e}",
                "public_double_order_policy": exact_policy,
                "status": "ok",
                "pos_final_linf": "nan",
                "vel_final_linf": "nan",
                "acc_final_linf": "nan",
                "avg_iterations": "nan",
                "max_iterations": "nan",
                "runtime_sec": "nan",
                "notes": notes,
            }
            if not config.run_public_code:
                row["status"] = "planned_not_run"
                pos_error = vel_error = acc_error = float("nan")
            elif reference is None:
                row["status"] = reference_status
                pos_error = vel_error = acc_error = float("nan")
            else:
                try:
                    candidate = run_public_model(
                        model,
                        form,
                        "dynamics",
                        h,
                        config.t_end,
                        tol=config.tolerance,
                    )
                    pos_error = final_error(reference, candidate, "pos")
                    vel_error = final_error(reference, candidate, "vel")
                    acc_error = final_error(reference, candidate, "acc")
                    row.update(
                        {
                            "pos_final_linf": f"{pos_error:.16e}",
                            "vel_final_linf": f"{vel_error:.16e}",
                            "acc_final_linf": f"{acc_error:.16e}",
                            "avg_iterations": f"{candidate['avg_iterations']:.16e}",
                            "max_iterations": f"{candidate['max_iterations']:.16e}",
                            "runtime_sec": f"{candidate['runtime_sec']:.16e}",
                        }
                    )
                except Exception as exc:  # noqa: BLE001 - record and continue.
                    row["status"] = failure_status("failed", exc)
                    pos_error = vel_error = acc_error = float("nan")
            pos_errors.append(pos_error)
            vel_errors.append(vel_error)
            acc_errors.append(acc_error)
            rows.append(row)

        group_rows = [row for row in rows if row["form"] == form]
        groups[f"{form}:double_pendulum"] = {
            "row_count": len(group_rows),
            "ok_row_count": sum(1 for row in group_rows if row["status"] == "ok"),
            "reference_status": reference_status,
            "reference_runtime_sec": reference_runtime_sec,
            "pos_final_linf_order": finite_or_none(estimate_order(list(config.step_sizes), pos_errors)),
            "vel_final_linf_order": finite_or_none(estimate_order(list(config.step_sizes), vel_errors)),
            "acc_final_linf_order": finite_or_none(estimate_order(list(config.step_sizes), acc_errors)),
            "public_double_order_policy": exact_policy,
            "selected_step_trio_completed": bool(
                exact_policy
                and reference_status == "ok"
                and len(group_rows) == len(config.step_sizes)
                and all(row["status"] == "ok" for row in group_rows)
            ),
        }

    completed_groups = sum(1 for group in groups.values() if group["selected_step_trio_completed"])
    return rows, {
        "policy": config.policy,
        "run_mode": config.run_mode,
        "run_public_code": config.run_public_code,
        "full_ra2021_double_order_completed": config.full_ra2021_double_order_completed,
        "row_count": len(rows),
        "ok_row_count": sum(1 for row in rows if row["status"] == "ok"),
        "planned_row_count": sum(1 for row in rows if row["status"] == "planned_not_run"),
        "selected_forms": list(config.forms),
        "selected_groups": [f"{form}:double_pendulum" for form in config.forms],
        "selected_step_sizes": list(config.step_sizes),
        "selected_reference_h": config.reference_h,
        "selected_t_end": config.t_end,
        "selected_tolerance": config.tolerance,
        "public_double_order_policy": exact_policy,
        "selected_step_trio_group_count": completed_groups,
        "selected_step_trio_required_group_count": len(config.forms),
        "groups": groups,
        "notes": notes,
    }


def summarize_ra2021_public_order_work_rows(rows: list[dict], ra2021_summary: dict) -> tuple[list[dict], dict]:
    grouped: dict[tuple[str, str], list[dict]] = {}
    for row in rows:
        grouped.setdefault((str(row.get("form", "")), str(row.get("model", ""))), []).append(row)

    summary_rows: list[dict] = []
    for (form, model), group_rows in sorted(grouped.items()):
        ok_rows = [row for row in group_rows if row.get("status") == "ok"]
        sorted_ok = sorted(ok_rows, key=lambda row: as_float(row, "h"))
        finest = sorted_ok[0] if sorted_ok else {}
        h_ref_rows = sorted(ok_rows, key=lambda row: abs(as_float(row, "h") - RA2021_PUBLIC_REFERENCE_H))
        h_ref = h_ref_rows[0] if h_ref_rows else {}
        group_key = f"{form}:{model}"
        group_summary = ra2021_summary.get("groups", {}).get(group_key, {})
        runtime_values = [as_float(row, "runtime_sec") for row in ok_rows]
        avg_iter_values = [as_float(row, "avg_iterations") for row in ok_rows]
        max_iter_values = [as_float(row, "max_iterations") for row in ok_rows]
        summary_rows.append(
            {
                "policy": "ra2021_public_order_work_summary",
                "source_suite": "ra2021_taves_kissel_negrut",
                "case_id": f"ra2021_{model}_order_work_summary",
                "form": form,
                "model": model,
                "mode": "dynamics",
                "t_end": ra2021_summary.get("selected_t_end", "nan"),
                "reference_mode": "kinematics",
                "reference_h": ra2021_summary.get("selected_reference_h", "nan"),
                "row_count": len(group_rows),
                "ok_row_count": len(ok_rows),
                "public_step_trio_completed": group_summary.get("public_step_trio_completed", False),
                "pos_final_linf_order": format_float(float(group_summary.get("pos_final_linf_order", float("nan")) or float("nan"))),
                "vel_final_linf_order": format_float(float(group_summary.get("vel_final_linf_order", float("nan")) or float("nan"))),
                "acc_final_linf_order": format_float(float(group_summary.get("acc_final_linf_order", float("nan")) or float("nan"))),
                "finest_h": format_float(as_float(finest, "h")),
                "finest_pos_final_linf": format_float(as_float(finest, "pos_final_linf")),
                "finest_vel_final_linf": format_float(as_float(finest, "vel_final_linf")),
                "finest_acc_final_linf": format_float(as_float(finest, "acc_final_linf")),
                "runtime_sec_sum": format_float(finite_sum(runtime_values)),
                "runtime_sec_at_reference_h": format_float(as_float(h_ref, "runtime_sec")),
                "avg_iterations_at_reference_h": format_float(as_float(h_ref, "avg_iterations")),
                "max_iterations_at_reference_h": format_float(as_float(h_ref, "max_iterations")),
                "avg_iterations_mean_over_steps": format_float(float(np.mean(avg_iter_values)) if avg_iter_values else float("nan")),
                "max_iterations_over_steps": format_float(max(max_iter_values) if max_iter_values else float("nan")),
                "reference_runtime_sec": format_float(as_float(h_ref, "reference_runtime_sec")),
                "notes": (
                    "Paper-ready summary of completed 2021 public-code order rows. "
                    "It summarizes existing public baseline data; it is not a Gauss6/FullVA superiority row."
                ),
            }
        )

    return summary_rows, {
        "policy": "ra2021_public_order_work_summary",
        "row_count": len(summary_rows),
        "ok_row_count": sum(1 for row in summary_rows if int(row["ok_row_count"]) >= 1),
        "public_step_trio_group_count": sum(1 for row in summary_rows if row["public_step_trio_completed"] is True),
        "selected_t_end": ra2021_summary.get("selected_t_end"),
        "selected_reference_h": ra2021_summary.get("selected_reference_h"),
        "notes": "Summarizes public baseline error-order-work rows for manuscript tables.",
    }


def run_hi2022_halfimplicit_rows(config: HI2022Config) -> tuple[list[dict], dict]:
    forms = list(config.forms)
    models = list(config.models)
    step_sizes = list(config.step_sizes)
    rows: list[dict] = []
    order_groups: dict[str, dict] = {}
    patched: list[str] = []

    if config.run_public_code:
        try:
            switch_simengine_root(HI2022_ROOT)
            patched = patch_hi2022_modern_numpy_scalar_assignments()
        except Exception as exc:  # noqa: BLE001 - record in-suite reference failure.
            patched = [failure_status("patch_failed", exc)]

    for model_name in models:
        reference = None
        reference_status = "ok" if config.run_public_code else "planned_not_run"
        reference_runtime_sec = float("nan")
        reference_execution_path = "not_run"
        reference_mode = "dynamics" if model_name == "double_pendulum" else "kinematics"
        reference_policy = (
            "bounded_rA_dynamics_self_reference"
            if model_name == "double_pendulum"
            else "bounded_rA_kinematics_reference"
        )
        reference_tolerance = (
            hi2022_tolerance("rA", config.reference_h, config.tolerance_base)
            if reference_mode == "dynamics"
            else config.tolerance_base
        )
        if config.run_public_code:
            if patched and patched[0].startswith("patch_failed"):
                reference_status = patched[0]
            else:
                try:
                    reference = run_hi2022_model(
                        model_name,
                        "rA",
                        reference_mode,
                        config.reference_h,
                        config.t_end,
                        reference_tolerance,
                    )
                    reference_runtime_sec = float(reference["runtime_sec"])
                    reference_execution_path = str(reference.get("execution_path", "unknown"))
                except Exception as exc:  # noqa: BLE001 - record in-suite reference failure.
                    reference_status = failure_status("reference_failed", exc)

        for form in forms:
            pos_errors: list[float] = []
            vel_errors: list[float] = []
            acc_errors: list[float] = []
            for h in step_sizes:
                tolerance = hi2022_tolerance(form, h, config.tolerance_base)
                row = {
                    "policy": config.policy,
                    "source_suite": "hi2022_fang_kissel_zhang_negrut",
                    "case_id": f"hi2022_{model_name}_bounded_convergence",
                    "form": form,
                    "model": model_name,
                    "mode": "dynamics",
                    "t_end": config.t_end,
                    "reference_form": "rA",
                    "reference_mode": reference_mode,
                    "reference_policy": reference_policy,
                    "reference_h": config.reference_h,
                    "reference_tolerance": f"{reference_tolerance:.16e}",
                    "reference_status": reference_status,
                    "reference_execution_path": reference_execution_path,
                    "reference_runtime_sec": "nan"
                    if not np.isfinite(reference_runtime_sec)
                    else f"{reference_runtime_sec:.16e}",
                    "h": h,
                    "tolerance": f"{tolerance:.16e}",
                    "status": "ok",
                    "pos_final_linf": "nan",
                    "vel_final_linf": "nan",
                    "acc_final_linf": "nan",
                    "avg_iterations": "nan",
                    "max_iterations": "nan",
                    "runtime_sec": "nan",
                    "execution_path": "not_run",
                }
                if not config.run_public_code:
                    row["status"] = "planned_not_run"
                    pos_error = vel_error = acc_error = float("nan")
                elif reference is None:
                    row["status"] = reference_status
                    pos_error = vel_error = acc_error = float("nan")
                else:
                    try:
                        candidate = run_hi2022_model(model_name, form, "dynamics", h, config.t_end, tolerance)
                        pos_error = final_error(reference, candidate, "pos")
                        vel_error = final_error(reference, candidate, "vel")
                        acc_error = final_error(reference, candidate, "acc")
                        row.update(
                            {
                                "pos_final_linf": f"{pos_error:.16e}",
                                "vel_final_linf": f"{vel_error:.16e}",
                                "acc_final_linf": f"{acc_error:.16e}",
                                "avg_iterations": f"{candidate['avg_iterations']:.16e}",
                                "max_iterations": f"{candidate['max_iterations']:.16e}",
                                "runtime_sec": f"{candidate['runtime_sec']:.16e}",
                                "execution_path": str(candidate.get("execution_path", "unknown")),
                            }
                        )
                    except Exception as exc:  # noqa: BLE001 - keep failed rows audit-visible.
                        row["status"] = failure_status("failed", exc)
                        pos_error = vel_error = acc_error = float("nan")
                pos_errors.append(pos_error)
                vel_errors.append(vel_error)
                acc_errors.append(acc_error)
                rows.append(row)

            group_rows = [row for row in rows if row["form"] == form and row["model"] == model_name]
            order_groups[f"{form}:{model_name}"] = {
                "row_count": len(group_rows),
                "ok_row_count": sum(1 for row in group_rows if row["status"] == "ok"),
                "planned_row_count": sum(1 for row in group_rows if row["status"] == "planned_not_run"),
                "pos_final_linf_order": finite_or_none(estimate_order(step_sizes, pos_errors)),
                "vel_final_linf_order": finite_or_none(estimate_order(step_sizes, vel_errors)),
                "acc_final_linf_order": finite_or_none(estimate_order(step_sizes, acc_errors)),
                "step_sizes": step_sizes,
                "completed": False,
                "reference_mode": reference_mode,
                "reference_policy": reference_policy,
                "reference_status": reference_status,
                "reference_execution_path": reference_execution_path,
                "reference_runtime_sec": reference_runtime_sec,
                "selected_step_trio_completed": bool(
                    config.run_public_code
                    and reference_status == "ok"
                    and len(config.step_sizes) >= 3
                    and all(row["status"] == "ok" for row in group_rows)
                ),
            }

    selected_step_trio_group_count = sum(1 for group in order_groups.values() if group["selected_step_trio_completed"])
    summary = {
        "policy": config.policy,
        "run_mode": config.run_mode,
        "full_hi2022_campaign_completed": config.full_hi2022_campaign_completed,
        "selected_step_trio_group_count": selected_step_trio_group_count,
        "selected_step_trio_required_group_count": len(config.forms) * len(config.models),
        "row_count": len(rows),
        "ok_row_count": sum(1 for row in rows if row["status"] == "ok"),
        "planned_row_count": sum(1 for row in rows if row["status"] == "planned_not_run"),
        "run_public_code": config.run_public_code,
        "selected_models": models,
        "selected_forms": forms,
        "selected_groups": [f"{form}:{model_name}" for form in forms for model_name in models],
        "selected_step_sizes": step_sizes,
        "selected_t_end": config.t_end,
        "selected_reference_h": config.reference_h,
        "tolerance_base": config.tolerance_base,
        "runtime_patches": patched,
        "groups": order_groups,
    }
    return rows, summary


def public_single_reference_alignment(v047_module, t_end: float, reference_h: float) -> dict:
    switch_simengine_root(SBEL_C2)
    patch_modern_numpy_scalar_assignments()
    reference = run_public_model(RA2021_MODEL_BY_NAME["single_pendulum"], "rA", "kinematics", reference_h, t_end, tol=1e-12)
    exact = v047_module.asme_single_state_from_time(t_end)
    return {
        "public_reference_pos_final_linf": float(np.max(np.abs(reference["pos"][0, :, -1] - exact["r"]))),
        "public_reference_vel_final_linf": float(np.max(np.abs(reference["vel"][0, :, -1] - exact["v"]))),
        "public_reference_acc_final_linf": float(np.max(np.abs(reference["acc"][0, :, -1] - exact["a"]))),
    }


def run_gauss6_fullva_external_rows(config: Gauss6FullVAConfig) -> tuple[list[dict], dict]:
    rows: list[dict] = []
    pos_errors: list[float] = []
    vel_errors: list[float] = []
    orient_errors: list[float] = []
    omega_errors: list[float] = []
    alignment = {
        "public_reference_pos_final_linf": float("nan"),
        "public_reference_vel_final_linf": float("nan"),
        "public_reference_acc_final_linf": float("nan"),
    }
    v047_module = None
    if config.run_model:
        v047_module = import_v047_single_fullva_module()
        alignment = public_single_reference_alignment(v047_module, config.t_end, config.reference_h)

    for h in config.step_sizes:
        row = {
            "policy": config.policy,
            "source_suite": "ra2021_taves_kissel_negrut",
            "case_id": "ra2021_single_pendulum_order",
            "method": "Gauss6/FullVA",
            "model": "single_pendulum",
            "t_end": config.t_end,
            "reference_policy": "analytic_exact_with_public_kinematic_alignment",
            "reference_h": config.reference_h,
            "h": h,
            "status": "planned_not_run",
            "steps": "nan",
            "position_l2_error": "nan",
            "velocity_l2_error": "nan",
            "orientation_error_rad": "nan",
            "omega_l2_error": "nan",
            "position_observed_order": "nan",
            "velocity_observed_order": "nan",
            "orientation_observed_order": "nan",
            "omega_observed_order": "nan",
            "max_stage_residual_norm": "nan",
            "max_trans_dynamics_residual": "nan",
            "max_rot_dynamics_residual": "nan",
            "max_endpoint_drive_constraint_abs": "nan",
            "total_newton_iterations": "nan",
            "runtime_sec": "nan",
            "public_reference_pos_final_linf": f"{alignment['public_reference_pos_final_linf']:.16e}",
            "public_reference_vel_final_linf": f"{alignment['public_reference_vel_final_linf']:.16e}",
            "public_reference_acc_final_linf": f"{alignment['public_reference_acc_final_linf']:.16e}",
            "notes": (
                "Selected Gauss6/FullVA same-mechanism pilot for the 2021 public single-pendulum setup; "
                "not the full public-code time-window campaign."
            ),
        }
        if config.run_model:
            started = time.perf_counter()
            try:
                assert v047_module is not None
                out = v047_module.integrate_asme_single_driven_absolute_fullva(h, config.t_end, False)
                runtime = time.perf_counter() - started
                row.update(
                    {
                        "status": "ok",
                        "steps": out["steps"],
                        "position_l2_error": f"{out['position_l2_error']:.16e}",
                        "velocity_l2_error": f"{out['velocity_l2_error']:.16e}",
                        "orientation_error_rad": f"{out['orientation_error_rad']:.16e}",
                        "omega_l2_error": f"{out['omega_l2_error']:.16e}",
                        "max_stage_residual_norm": f"{out['max_stage_residual_norm']:.16e}",
                        "max_trans_dynamics_residual": f"{out['max_trans_dynamics_residual']:.16e}",
                        "max_rot_dynamics_residual": f"{out['max_rot_dynamics_residual']:.16e}",
                        "max_endpoint_drive_constraint_abs": f"{out['max_endpoint_drive_constraint_abs']:.16e}",
                        "total_newton_iterations": out["total_newton_iterations"],
                        "runtime_sec": f"{runtime:.16e}",
                    }
                )
                pos_errors.append(float(out["position_l2_error"]))
                vel_errors.append(float(out["velocity_l2_error"]))
                orient_errors.append(float(out["orientation_error_rad"]))
                omega_errors.append(float(out["omega_l2_error"]))
            except Exception as exc:  # noqa: BLE001 - record failed rows for audit.
                row["status"] = f"failed:{type(exc).__name__}:{exc}"
                row["runtime_sec"] = f"{time.perf_counter() - started:.16e}"
                pos_errors.append(float("nan"))
                vel_errors.append(float("nan"))
                orient_errors.append(float("nan"))
                omega_errors.append(float("nan"))
        else:
            pos_errors.append(float("nan"))
            vel_errors.append(float("nan"))
            orient_errors.append(float("nan"))
            omega_errors.append(float("nan"))
        rows.append(row)

    orders = {
        "position_observed_order": finite_or_none(estimate_order(list(config.step_sizes), pos_errors)),
        "velocity_observed_order": finite_or_none(estimate_order(list(config.step_sizes), vel_errors)),
        "orientation_observed_order": finite_or_none(estimate_order(list(config.step_sizes), orient_errors)),
        "omega_observed_order": finite_or_none(estimate_order(list(config.step_sizes), omega_errors)),
    }
    for row in rows:
        for key, value in orders.items():
            row[key] = "nan" if value is None else f"{value:.16e}"

    summary = {
        "policy": config.policy,
        "run_model": config.run_model,
        "row_count": len(rows),
        "ok_row_count": sum(1 for row in rows if row["status"] == "ok"),
        "planned_row_count": sum(1 for row in rows if row["status"] == "planned_not_run"),
        "selected_rows_completed": config.run_model and all(row["status"] == "ok" for row in rows),
        "full_external_campaign_completed": False,
        "selected_models": ["single_pendulum"],
        "selected_step_sizes": list(config.step_sizes),
        "selected_t_end": config.t_end,
        "selected_reference_h": config.reference_h,
        **orders,
        **alignment,
    }
    return rows, summary


def run_gauss6_fullva_public_horizon_single_rows(config: Gauss6PublicSingleConfig) -> tuple[list[dict], dict]:
    rows: list[dict] = []
    pos_errors: list[float] = []
    vel_errors: list[float] = []
    orient_errors: list[float] = []
    omega_errors: list[float] = []
    alignment = {
        "public_reference_pos_final_linf": float("nan"),
        "public_reference_vel_final_linf": float("nan"),
        "public_reference_acc_final_linf": float("nan"),
    }
    v047_module = None
    exact_public_window = bool(
        np.isclose(config.t_end, RA2021_PUBLIC_T_END)
        and np.isclose(config.reference_h, RA2021_PUBLIC_REFERENCE_H)
    )
    if config.run_model:
        v047_module = import_v047_single_fullva_module()
        alignment = public_single_reference_alignment(v047_module, config.t_end, config.reference_h)

    public_h_values = set(RA2021_ORDER_STEP_SIZES)
    notes = (
        "Gauss6/FullVA single-pendulum tranche on the 2021 public-code time horizon. "
        "Rows count toward the exact public-policy single-pendulum campaign only when "
        "T=3, reference_h=1e-3, and h is one of [1e-2, 1e-3, 1e-4]. This is still not "
        "a full external campaign until all three public h rows and the remaining source suites are complete."
    )
    public_h_row_ok_count = 0
    for h in config.step_sizes:
        public_policy_h = any(np.isclose(h, public_h) for public_h in public_h_values)
        row = {
            "policy": config.policy,
            "source_suite": "ra2021_taves_kissel_negrut",
            "case_id": "ra2021_single_pendulum_order",
            "method": "Gauss6/FullVA",
            "model": "single_pendulum",
            "row_type": "public_horizon_single_pendulum_tranche",
            "t_end": config.t_end,
            "reference_policy": "analytic_exact_with_public_kinematic_alignment",
            "reference_h": config.reference_h,
            "public_policy_time_window": exact_public_window,
            "public_policy_h": public_policy_h,
            "h": h,
            "status": "planned_not_run",
            "steps": "nan",
            "position_l2_error": "nan",
            "velocity_l2_error": "nan",
            "orientation_error_rad": "nan",
            "omega_l2_error": "nan",
            "position_observed_order": "nan",
            "velocity_observed_order": "nan",
            "orientation_observed_order": "nan",
            "omega_observed_order": "nan",
            "max_stage_residual_norm": "nan",
            "max_trans_dynamics_residual": "nan",
            "max_rot_dynamics_residual": "nan",
            "max_endpoint_drive_constraint_abs": "nan",
            "total_newton_iterations": "nan",
            "runtime_sec": "nan",
            "public_reference_pos_final_linf": f"{alignment['public_reference_pos_final_linf']:.16e}",
            "public_reference_vel_final_linf": f"{alignment['public_reference_vel_final_linf']:.16e}",
            "public_reference_acc_final_linf": f"{alignment['public_reference_acc_final_linf']:.16e}",
            "notes": notes,
        }
        if config.run_model:
            started = time.perf_counter()
            try:
                assert v047_module is not None
                out = v047_module.integrate_asme_single_driven_absolute_fullva(h, config.t_end, False)
                runtime = time.perf_counter() - started
                row.update(
                    {
                        "status": "ok",
                        "steps": out["steps"],
                        "position_l2_error": f"{out['position_l2_error']:.16e}",
                        "velocity_l2_error": f"{out['velocity_l2_error']:.16e}",
                        "orientation_error_rad": f"{out['orientation_error_rad']:.16e}",
                        "omega_l2_error": f"{out['omega_l2_error']:.16e}",
                        "max_stage_residual_norm": f"{out['max_stage_residual_norm']:.16e}",
                        "max_trans_dynamics_residual": f"{out['max_trans_dynamics_residual']:.16e}",
                        "max_rot_dynamics_residual": f"{out['max_rot_dynamics_residual']:.16e}",
                        "max_endpoint_drive_constraint_abs": f"{out['max_endpoint_drive_constraint_abs']:.16e}",
                        "total_newton_iterations": out["total_newton_iterations"],
                        "runtime_sec": f"{runtime:.16e}",
                    }
                )
                if exact_public_window and public_policy_h:
                    public_h_row_ok_count += 1
                pos_errors.append(float(out["position_l2_error"]))
                vel_errors.append(float(out["velocity_l2_error"]))
                orient_errors.append(float(out["orientation_error_rad"]))
                omega_errors.append(float(out["omega_l2_error"]))
            except Exception as exc:  # noqa: BLE001 - record failed rows for audit.
                row["status"] = failure_status("failed", exc)
                row["runtime_sec"] = f"{time.perf_counter() - started:.16e}"
                pos_errors.append(float("nan"))
                vel_errors.append(float("nan"))
                orient_errors.append(float("nan"))
                omega_errors.append(float("nan"))
        else:
            pos_errors.append(float("nan"))
            vel_errors.append(float("nan"))
            orient_errors.append(float("nan"))
            omega_errors.append(float("nan"))
        rows.append(row)

    orders = {
        "position_observed_order": finite_or_none(estimate_order(list(config.step_sizes), pos_errors)),
        "velocity_observed_order": finite_or_none(estimate_order(list(config.step_sizes), vel_errors)),
        "orientation_observed_order": finite_or_none(estimate_order(list(config.step_sizes), orient_errors)),
        "omega_observed_order": finite_or_none(estimate_order(list(config.step_sizes), omega_errors)),
    }
    for row in rows:
        for key, value in orders.items():
            row[key] = "nan" if value is None else f"{value:.16e}"

    public_single_step_trio_completed = bool(
        exact_public_window
        and config.run_model
        and len(config.step_sizes) >= 3
        and all(
            any(np.isclose(float(row["h"]), public_h) and row["status"] == "ok" for row in rows)
            for public_h in RA2021_ORDER_STEP_SIZES
        )
    )
    summary = {
        "policy": config.policy,
        "run_mode": config.run_mode,
        "run_model": config.run_model,
        "row_count": len(rows),
        "ok_row_count": sum(1 for row in rows if row["status"] == "ok"),
        "planned_row_count": sum(1 for row in rows if row["status"] == "planned_not_run"),
        "selected_rows_completed": config.run_model and all(row["status"] == "ok" for row in rows),
        "full_external_campaign_completed": False,
        "public_policy_time_window": exact_public_window,
        "public_step_size_rows_completed": public_h_row_ok_count,
        "public_step_size_required_count": len(RA2021_ORDER_STEP_SIZES),
        "public_single_step_trio_completed": public_single_step_trio_completed,
        "selected_models": ["single_pendulum"],
        "selected_step_sizes": list(config.step_sizes),
        "selected_t_end": config.t_end,
        "selected_reference_h": config.reference_h,
        **orders,
        **alignment,
        "notes": notes,
    }
    return rows, summary


def run_gauss6_fullva_public_horizon_double_coarse_rows(
    config: Gauss6PublicDoubleCoarseConfig,
) -> tuple[list[dict], dict]:
    rows: list[dict] = []
    pos_errors: list[float] = []
    vel_errors: list[float] = []
    reference_runtime_sec = float("nan")
    reference_status = "ok" if config.run_model else "planned_not_run"
    exact_public_window = bool(np.isclose(config.t_end, RA2021_PUBLIC_T_END))
    public_h_values = set(RA2021_ORDER_STEP_SIZES)
    notes = (
        "Gauss6/FullVA double-pendulum coarse public-horizon pilot using the local v029 "
        "double-revolute FullVA self-reference at T=3. The h values are intentionally "
        "coarser than the 2021 public h=[1e-2,1e-3,1e-4] policy, so this is an order/work "
        "feasibility tranche rather than a completed public-policy superiority row."
    )
    v047_module = None
    v029 = None
    params = None
    reference = None
    method = "double_revolute_gauss6_fullva"
    if config.run_model:
        try:
            v047_module = import_v047_single_fullva_module()
            v029 = v047_module.load_v029()
            params = v047_module.make_asme_double_pendulum_params(v029)
            started = time.perf_counter()
            reference = v047_module.integrate_v029_asme_double_trajectory(
                v029, method, config.reference_h, config.t_end, params
            )
            reference_runtime_sec = time.perf_counter() - started
        except Exception as exc:  # noqa: BLE001 - record failed reference policy.
            reference_status = failure_status("reference_failed", exc)

    for h in config.step_sizes:
        public_policy_h = any(np.isclose(h, public_h) for public_h in public_h_values)
        row = {
            "policy": config.policy,
            "source_suite": "ra2021_taves_kissel_negrut",
            "case_id": "ra2021_double_pendulum_public_horizon_coarse_order",
            "method": "Gauss6/FullVA-local-double-revolute",
            "model": "double_pendulum",
            "row_type": "public_horizon_double_pendulum_coarse_order_work",
            "t_end": config.t_end,
            "reference_policy": "local_v029_fullva_self_reference_coarse",
            "reference_h": config.reference_h,
            "reference_status": reference_status,
            "reference_runtime_sec": "nan"
            if not np.isfinite(reference_runtime_sec)
            else f"{reference_runtime_sec:.16e}",
            "public_policy_time_window": exact_public_window,
            "public_policy_h": public_policy_h,
            "h": h,
            "status": "planned_not_run",
            "steps": "nan",
            "pos_traj_linf": "nan",
            "vel_traj_linf": "nan",
            "pos_final_linf": "nan",
            "vel_final_linf": "nan",
            "pos_observed_order": "nan",
            "vel_observed_order": "nan",
            "max_endpoint_constraint_norm": "nan",
            "max_endpoint_velocity_constraint_norm": "nan",
            "constraint_threshold_satisfied": "nan",
            "total_newton_iterations": "nan",
            "runtime_sec": "nan",
            "notes": notes,
        }
        if config.run_model and reference is not None:
            started = time.perf_counter()
            try:
                assert v047_module is not None
                assert v029 is not None
                assert params is not None
                candidate = v047_module.integrate_v029_asme_double_trajectory(
                    v029, method, h, config.t_end, params
                )
                runtime = time.perf_counter() - started
                err = v047_module.compare_nested_trajectory(reference, candidate)
                pos_error = float(err["pos_traj_linf"])
                vel_error = float(err["vel_traj_linf"])
                accepted_row = (
                    candidate["max_endpoint_constraint_norm"] < 1.0e-10
                    and candidate["max_endpoint_velocity_constraint_norm"] < 1.0e-10
                )
                row.update(
                    {
                        "status": "ok",
                        "steps": candidate["steps"],
                        "pos_traj_linf": f"{err['pos_traj_linf']:.16e}",
                        "vel_traj_linf": f"{err['vel_traj_linf']:.16e}",
                        "pos_final_linf": f"{err['pos_final_linf']:.16e}",
                        "vel_final_linf": f"{err['vel_final_linf']:.16e}",
                        "max_endpoint_constraint_norm": f"{candidate['max_endpoint_constraint_norm']:.16e}",
                        "max_endpoint_velocity_constraint_norm": f"{candidate['max_endpoint_velocity_constraint_norm']:.16e}",
                        "constraint_threshold_satisfied": str(accepted_row),
                        "total_newton_iterations": candidate["total_newton_iterations"],
                        "runtime_sec": f"{runtime:.16e}",
                    }
                )
            except Exception as exc:  # noqa: BLE001 - keep failure in artifact.
                row["status"] = failure_status("failed", exc)
                row["runtime_sec"] = f"{time.perf_counter() - started:.16e}"
                pos_error = float("nan")
                vel_error = float("nan")
        else:
            if config.run_model and reference is None:
                row["status"] = reference_status
            pos_error = float("nan")
            vel_error = float("nan")
        pos_errors.append(pos_error)
        vel_errors.append(vel_error)
        rows.append(row)

    orders = {
        "pos_observed_order": finite_or_none(estimate_order(list(config.step_sizes), pos_errors)),
        "vel_observed_order": finite_or_none(estimate_order(list(config.step_sizes), vel_errors)),
    }
    for row in rows:
        for key, value in orders.items():
            row[key] = "nan" if value is None else f"{value:.16e}"

    ok_rows = [row for row in rows if row["status"] == "ok"]
    return rows, {
        "policy": config.policy,
        "run_mode": config.run_mode,
        "run_model": config.run_model,
        "row_count": len(rows),
        "ok_row_count": len(ok_rows),
        "planned_row_count": sum(1 for row in rows if row["status"] == "planned_not_run"),
        "selected_rows_completed": bool(rows and len(ok_rows) == len(rows)),
        "full_external_campaign_completed": False,
        "public_policy_time_window": exact_public_window,
        "public_policy_h_rows_completed": sum(
            1
            for row in ok_rows
            if bool(row.get("public_policy_time_window")) and bool(row.get("public_policy_h"))
        ),
        "public_policy_h_required_count": len(RA2021_ORDER_STEP_SIZES),
        "public_double_step_trio_completed": False,
        "selected_models": ["double_pendulum"],
        "selected_step_sizes": list(config.step_sizes),
        "selected_t_end": config.t_end,
        "selected_reference_h": config.reference_h,
        "reference_status": reference_status,
        "reference_runtime_sec": reference_runtime_sec,
        **orders,
        "notes": notes,
    }


def run_gauss6_fullva_closed_loop_external_rows(config: Gauss6ClosedLoopConfig) -> tuple[list[dict], dict]:
    rows: list[dict] = []
    model_summaries: dict[str, dict] = {}
    public_horizon = "public_horizon" in config.policy
    row_type = (
        "public_horizon_closed_loop_kinematic_reaction"
        if public_horizon
        else "closed_loop_kinematic_reaction"
    )
    case_suffix = (
        "public_horizon_closed_loop_kinematic_reaction"
        if public_horizon
        else "closed_loop_kinematic_reaction"
    )
    notes = (
        "Public-horizon 2021 closed-loop tranche using the accepted local kinematic FullVA solve and "
        "reaction reconstruction on the public four_link/slider_crank mechanisms. These rows use the "
        "2021 public time window and public h policy when selected, but they remain constraint/reaction "
        "residual rows rather than dynamic order/work-superiority rows."
        if public_horizon
        else (
            "Selected 2021 closed-loop external rows using the accepted local kinematic FullVA solve and "
            "reaction reconstruction for four_link and slider_crank. These rows verify constraint, SO(3), "
            "and Newton-Euler residuals on the public mechanisms, but are not dynamic order or work-superiority rows."
        )
    )
    exact_public_window = bool(
        np.isclose(config.t_end, RA2021_PUBLIC_T_END)
        and np.isclose(config.reference_h, RA2021_PUBLIC_REFERENCE_H)
    )
    if not config.run_model:
        for model in config.models:
            for h in config.step_sizes:
                rows.append(
                    {
                        "policy": config.policy,
                        "source_suite": "ra2021_taves_kissel_negrut",
                        "case_id": f"ra2021_{model}_{case_suffix}",
                        "method": "Gauss6/FullVA-local-closed-loop",
                        "model": model,
                        "row_type": row_type,
                        "t_end": config.t_end,
                        "reference_policy": "local_kinematic_fullva_nested_reference",
                        "reference_h": config.reference_h,
                        "h": h,
                        "public_policy_time_window": exact_public_window,
                        "public_policy_h": h in RA2021_ORDER_STEP_SIZES,
                        "status": "planned_not_run",
                        "steps": "nan",
                        "pos_traj_linf": "nan",
                        "vel_traj_linf": "nan",
                        "acc_traj_linf": "nan",
                        "lambda_traj_linf": "nan",
                        "pos_observed_order": "nan",
                        "vel_observed_order": "nan",
                        "acc_observed_order": "nan",
                        "lambda_observed_order": "nan",
                        "max_position_constraint_norm": "nan",
                        "max_velocity_constraint_norm": "nan",
                        "max_acceleration_constraint_norm": "nan",
                        "max_so3_fro": "nan",
                        "max_trans_dynamics_residual": "nan",
                        "max_rot_dynamics_residual": "nan",
                        "max_dynamics_residual_norm": "nan",
                        "max_multiplier_norm": "nan",
                        "total_newton_iterations": "nan",
                        "max_newton_iterations": "nan",
                        "max_step_correction_norm": "nan",
                        "min_singular_value": "nan",
                        "max_condition_number": "nan",
                        "runtime_sec": "nan",
                        "reference_runtime_sec": "nan",
                        "notes": notes,
                    }
                )
            model_summaries[model] = {
                "status": "planned_not_run",
                "step_sizes": list(config.step_sizes),
                "reference_h": config.reference_h,
                "t_end": config.t_end,
            }
        return rows, {
            "policy": config.policy,
            "run_mode": config.run_mode,
            "run_model": False,
            "row_count": len(rows),
            "ok_row_count": 0,
            "planned_row_count": len(rows),
            "selected_rows_completed": False,
            "full_external_campaign_completed": False,
            "public_policy_time_window": exact_public_window,
            "public_step_size_rows_completed": 0,
            "public_step_size_required_count": len(config.models) * len(RA2021_ORDER_STEP_SIZES),
            "public_closed_loop_step_trios_completed": False,
            "selected_models": list(config.models),
            "selected_step_sizes": list(config.step_sizes),
            "selected_t_end": config.t_end,
            "selected_reference_h": config.reference_h,
            "models": model_summaries,
            "notes": notes,
        }

    v047_module = import_v047_single_fullva_module()
    v046 = v047_module.load_v046()
    v046.patch_modern_numpy_scalar_assignments()
    public_models = {model.name: model for model in v046.MODELS}

    for model_name in config.models:
        if model_name not in public_models:
            raise ValueError(f"v046 public model not found: {model_name}")
        model = public_models[model_name]
        reference = v047_module.simulate_v046_local_kinematic_fullva(
            v046,
            model,
            config.reference_h,
            config.t_end,
            1.0e-12,
        )
        h_values: list[float] = []
        pos_errors: list[float] = []
        vel_errors: list[float] = []
        acc_errors: list[float] = []
        lambda_errors: list[float] = []
        model_row_indices: list[int] = []
        max_phi = max_vel = max_acc = max_so3 = 0.0
        max_trans = max_rot = max_dyn = max_lambda = 0.0
        max_correction = 0.0
        min_sigma = float("inf")
        max_cond = 0.0
        total_iters = 0
        max_iters = 0
        model_ok = True

        for h in config.step_sizes:
            row = {
                "policy": config.policy,
                "source_suite": "ra2021_taves_kissel_negrut",
                "case_id": f"ra2021_{model_name}_{case_suffix}",
                "method": "Gauss6/FullVA-local-closed-loop",
                "model": model_name,
                "row_type": row_type,
                "t_end": config.t_end,
                "reference_policy": "local_kinematic_fullva_nested_reference",
                "reference_h": config.reference_h,
                "h": h,
                "public_policy_time_window": exact_public_window,
                "public_policy_h": h in RA2021_ORDER_STEP_SIZES,
                "status": "ok",
                "steps": "nan",
                "pos_traj_linf": "nan",
                "vel_traj_linf": "nan",
                "acc_traj_linf": "nan",
                "lambda_traj_linf": "nan",
                "pos_observed_order": "nan",
                "vel_observed_order": "nan",
                "acc_observed_order": "nan",
                "lambda_observed_order": "nan",
                "max_position_constraint_norm": "nan",
                "max_velocity_constraint_norm": "nan",
                "max_acceleration_constraint_norm": "nan",
                "max_so3_fro": "nan",
                "max_trans_dynamics_residual": "nan",
                "max_rot_dynamics_residual": "nan",
                "max_dynamics_residual_norm": "nan",
                "max_multiplier_norm": "nan",
                "total_newton_iterations": "nan",
                "max_newton_iterations": "nan",
                "max_step_correction_norm": "nan",
                "min_singular_value": "nan",
                "max_condition_number": "nan",
                "runtime_sec": "nan",
                "reference_runtime_sec": f"{reference['runtime_sec']:.16e}",
                "notes": notes,
            }
            try:
                candidate = v047_module.simulate_v046_local_kinematic_fullva(v046, model, h, config.t_end, 1.0e-12)
                err = compare_common_grid_with_acc(reference, candidate)
                lambda_error = compare_common_grid_lambda(reference, candidate)
                accepted_row = (
                    candidate["max_position_constraint_norm"] < 1.0e-10
                    and candidate["max_velocity_constraint_norm"] < 1.0e-10
                    and candidate["max_acceleration_constraint_norm"] < 1.0e-10
                    and candidate["max_so3_fro"] < 1.0e-10
                    and candidate["max_dynamics_residual_norm"] < 1.0e-10
                )
                if not accepted_row:
                    model_ok = False
                h_values.append(h)
                pos_errors.append(err["pos_traj_linf"])
                vel_errors.append(err["vel_traj_linf"])
                acc_errors.append(err["acc_traj_linf"])
                lambda_errors.append(lambda_error)
                max_phi = max(max_phi, candidate["max_position_constraint_norm"])
                max_vel = max(max_vel, candidate["max_velocity_constraint_norm"])
                max_acc = max(max_acc, candidate["max_acceleration_constraint_norm"])
                max_so3 = max(max_so3, candidate["max_so3_fro"])
                max_trans = max(max_trans, candidate["max_trans_dynamics_residual"])
                max_rot = max(max_rot, candidate["max_rot_dynamics_residual"])
                max_dyn = max(max_dyn, candidate["max_dynamics_residual_norm"])
                max_lambda = max(max_lambda, candidate["max_multiplier_norm"])
                max_correction = max(max_correction, candidate["max_step_correction_norm"])
                min_sigma = min(min_sigma, candidate["min_singular_value"])
                max_cond = max(max_cond, candidate["max_condition_number"])
                total_iters += candidate["total_newton_iterations"]
                max_iters = max(max_iters, candidate["max_newton_iterations"])
                row.update(
                    {
                        "status": "ok" if accepted_row else "diagnostic_failed_threshold",
                        "steps": candidate["steps"],
                        "pos_traj_linf": f"{err['pos_traj_linf']:.16e}",
                        "vel_traj_linf": f"{err['vel_traj_linf']:.16e}",
                        "acc_traj_linf": f"{err['acc_traj_linf']:.16e}",
                        "lambda_traj_linf": f"{lambda_error:.16e}",
                        "max_position_constraint_norm": f"{candidate['max_position_constraint_norm']:.16e}",
                        "max_velocity_constraint_norm": f"{candidate['max_velocity_constraint_norm']:.16e}",
                        "max_acceleration_constraint_norm": f"{candidate['max_acceleration_constraint_norm']:.16e}",
                        "max_so3_fro": f"{candidate['max_so3_fro']:.16e}",
                        "max_trans_dynamics_residual": f"{candidate['max_trans_dynamics_residual']:.16e}",
                        "max_rot_dynamics_residual": f"{candidate['max_rot_dynamics_residual']:.16e}",
                        "max_dynamics_residual_norm": f"{candidate['max_dynamics_residual_norm']:.16e}",
                        "max_multiplier_norm": f"{candidate['max_multiplier_norm']:.16e}",
                        "total_newton_iterations": candidate["total_newton_iterations"],
                        "max_newton_iterations": candidate["max_newton_iterations"],
                        "max_step_correction_norm": f"{candidate['max_step_correction_norm']:.16e}",
                        "min_singular_value": f"{candidate['min_singular_value']:.16e}",
                        "max_condition_number": f"{candidate['max_condition_number']:.16e}",
                        "runtime_sec": f"{candidate['runtime_sec']:.16e}",
                    }
                )
            except Exception as exc:  # noqa: BLE001 - keep failures in the table.
                model_ok = False
                row["status"] = failure_status("failed", exc)
            model_row_indices.append(len(rows))
            rows.append(row)

        orders = {
            "pos_observed_order": finite_or_none(v047_module.observed_order(h_values, pos_errors)),
            "vel_observed_order": finite_or_none(v047_module.observed_order(h_values, vel_errors)),
            "acc_observed_order": finite_or_none(v047_module.observed_order(h_values, acc_errors)),
            "lambda_observed_order": finite_or_none(v047_module.observed_order(h_values, lambda_errors)),
        }
        for idx in model_row_indices:
            for key, value in orders.items():
                rows[idx][key] = "nan" if value is None else f"{value:.16e}"
        model_summaries[model_name] = {
            "status": "accepted_closed_loop_kinematic_reaction" if model_ok else "partial_failed",
            "step_sizes": list(config.step_sizes),
            "reference_h": config.reference_h,
            "t_end": config.t_end,
            "row_count": len(model_row_indices),
            "ok_row_count": sum(1 for idx in model_row_indices if rows[idx]["status"] == "ok"),
            "max_position_constraint_norm": max_phi,
            "max_velocity_constraint_norm": max_vel,
            "max_acceleration_constraint_norm": max_acc,
            "max_so3_fro": max_so3,
            "max_trans_dynamics_residual": max_trans,
            "max_rot_dynamics_residual": max_rot,
            "max_dynamics_residual_norm": max_dyn,
            "max_multiplier_norm": max_lambda,
            "max_step_correction_norm": max_correction,
            "min_singular_value": min_sigma if np.isfinite(min_sigma) else None,
            "max_condition_number": max_cond,
            "total_newton_iterations": total_iters,
            "max_newton_iterations": max_iters,
            **orders,
        }

    public_h_ok_count = sum(
        1
        for row in rows
        if row["status"] == "ok"
        and bool(row.get("public_policy_time_window"))
        and bool(row.get("public_policy_h"))
    )
    public_h_required_count = len(config.models) * len(RA2021_ORDER_STEP_SIZES)
    return rows, {
        "policy": config.policy,
        "run_mode": config.run_mode,
        "run_model": config.run_model,
        "row_count": len(rows),
        "ok_row_count": sum(1 for row in rows if row["status"] == "ok"),
        "planned_row_count": sum(1 for row in rows if row["status"] == "planned_not_run"),
        "selected_rows_completed": bool(rows and all(row["status"] == "ok" for row in rows)),
        "full_external_campaign_completed": False,
        "public_policy_time_window": exact_public_window,
        "public_step_size_rows_completed": public_h_ok_count,
        "public_step_size_required_count": public_h_required_count,
        "public_closed_loop_step_trios_completed": bool(
            rows and exact_public_window and public_h_ok_count == public_h_required_count
        ),
        "selected_models": list(config.models),
        "selected_step_sizes": list(config.step_sizes),
        "selected_t_end": config.t_end,
        "selected_reference_h": config.reference_h,
        "models": model_summaries,
        "notes": notes,
    }


def run_gauss6_fullva_closed_loop_same_window_comparison_rows(
    config: Gauss6ClosedLoopConfig,
) -> tuple[list[dict], dict]:
    rows: list[dict] = []
    model_summaries: dict[str, dict] = {}
    methods = ("rA-public-dynamics", "Gauss6/FullVA-local-closed-loop")
    policy = "ra2021_selected_closed_loop_same_window_comparison_not_full_campaign"
    notes = (
        "Selected same-window comparison on 2021 public closed-loop mechanisms. Both methods use the same "
        "public kinematic reference, T, h-sweep, and final position/velocity/acceleration error columns. "
        "The Gauss6/FullVA row is the accepted local kinematic/reaction residual policy for fully constrained "
        "driven closed loops, so this is not the full public T=3 dynamic order/work campaign."
    )

    def blank_row(model: str, method: str, h: float, status: str) -> dict:
        return {
            "policy": policy,
            "source_suite": "ra2021_taves_kissel_negrut",
            "case_id": f"ra2021_{model}_selected_same_window_comparison",
            "method": method,
            "model": model,
            "row_type": "selected_same_window_final_error_work",
            "t_end": config.t_end,
            "reference_method": "rA-public-kinematics",
            "reference_h": config.reference_h,
            "h": h,
            "status": status,
            "steps": "nan",
            "pos_final_linf": "nan",
            "vel_final_linf": "nan",
            "acc_final_linf": "nan",
            "pos_observed_order": "nan",
            "vel_observed_order": "nan",
            "acc_observed_order": "nan",
            "avg_iterations_or_newton_per_output": "nan",
            "max_iterations_or_newton": "nan",
            "total_newton_iterations": "nan",
            "runtime_sec": "nan",
            "reference_runtime_sec": "nan",
            "max_position_constraint_norm": "nan",
            "max_velocity_constraint_norm": "nan",
            "max_acceleration_constraint_norm": "nan",
            "max_so3_fro": "nan",
            "max_dynamics_residual_norm": "nan",
            "notes": notes,
        }

    if not config.run_model:
        for model in config.models:
            for method in methods:
                for h in config.step_sizes:
                    rows.append(blank_row(model, method, h, "planned_not_run"))
        return rows, {
            "policy": policy,
            "run_model": False,
            "row_count": len(rows),
            "ok_row_count": 0,
            "planned_row_count": len(rows),
            "selected_rows_completed": False,
            "full_external_campaign_completed": False,
            "selected_models": list(config.models),
            "selected_step_sizes": list(config.step_sizes),
            "selected_t_end": config.t_end,
            "selected_reference_h": config.reference_h,
            "models": {},
            "notes": notes,
        }

    switch_simengine_root(SBEL_C2)
    patch_modern_numpy_scalar_assignments()
    v047_module = import_v047_single_fullva_module()
    v046 = v047_module.load_v046()
    v046.patch_modern_numpy_scalar_assignments()
    v046_models = {model.name: model for model in v046.MODELS}

    for model_name in config.models:
        if model_name not in RA2021_MODEL_BY_NAME:
            raise ValueError(f"2021 public model not found: {model_name}")
        if model_name not in v046_models:
            raise ValueError(f"v046 model not found: {model_name}")
        public_model = RA2021_MODEL_BY_NAME[model_name]
        v046_model = v046_models[model_name]
        reference = run_public_model(public_model, "rA", "kinematics", config.reference_h, config.t_end, tol=1e-12)
        reference_runtime_sec = float(reference["runtime_sec"])
        method_errors: dict[str, dict[str, list[float]]] = {
            method: {"pos": [], "vel": [], "acc": []} for method in methods
        }
        model_row_indices: list[int] = []

        for h in config.step_sizes:
            row = blank_row(model_name, "rA-public-dynamics", h, "ok")
            row["reference_runtime_sec"] = f"{reference_runtime_sec:.16e}"
            try:
                candidate = run_public_model(public_model, "rA", "dynamics", h, config.t_end, tol=None)
                pos_error = final_error(reference, candidate, "pos")
                vel_error = final_error(reference, candidate, "vel")
                acc_error = final_error(reference, candidate, "acc")
                method_errors["rA-public-dynamics"]["pos"].append(pos_error)
                method_errors["rA-public-dynamics"]["vel"].append(vel_error)
                method_errors["rA-public-dynamics"]["acc"].append(acc_error)
                row.update(
                    {
                        "steps": int(round(config.t_end / h)),
                        "pos_final_linf": f"{pos_error:.16e}",
                        "vel_final_linf": f"{vel_error:.16e}",
                        "acc_final_linf": f"{acc_error:.16e}",
                        "avg_iterations_or_newton_per_output": f"{candidate['avg_iterations']:.16e}",
                        "max_iterations_or_newton": f"{candidate['max_iterations']:.16e}",
                        "runtime_sec": f"{candidate['runtime_sec']:.16e}",
                    }
                )
            except Exception as exc:  # noqa: BLE001 - keep failures visible.
                row["status"] = failure_status("failed", exc)
                for key in ("pos", "vel", "acc"):
                    method_errors["rA-public-dynamics"][key].append(float("nan"))
            model_row_indices.append(len(rows))
            rows.append(row)

            row = blank_row(model_name, "Gauss6/FullVA-local-closed-loop", h, "ok")
            row["reference_runtime_sec"] = f"{reference_runtime_sec:.16e}"
            try:
                candidate = v047_module.simulate_v046_local_kinematic_fullva(v046, v046_model, h, config.t_end, 1.0e-12)
                pos_error = final_error(reference, candidate, "pos")
                vel_error = final_error(reference, candidate, "vel")
                acc_error = final_error(reference, candidate, "acc")
                method_errors["Gauss6/FullVA-local-closed-loop"]["pos"].append(pos_error)
                method_errors["Gauss6/FullVA-local-closed-loop"]["vel"].append(vel_error)
                method_errors["Gauss6/FullVA-local-closed-loop"]["acc"].append(acc_error)
                outputs = int(candidate["steps"]) + 1
                row.update(
                    {
                        "steps": candidate["steps"],
                        "pos_final_linf": f"{pos_error:.16e}",
                        "vel_final_linf": f"{vel_error:.16e}",
                        "acc_final_linf": f"{acc_error:.16e}",
                        "avg_iterations_or_newton_per_output": f"{candidate['total_newton_iterations'] / outputs:.16e}",
                        "max_iterations_or_newton": candidate["max_newton_iterations"],
                        "total_newton_iterations": candidate["total_newton_iterations"],
                        "runtime_sec": f"{candidate['runtime_sec']:.16e}",
                        "max_position_constraint_norm": f"{candidate['max_position_constraint_norm']:.16e}",
                        "max_velocity_constraint_norm": f"{candidate['max_velocity_constraint_norm']:.16e}",
                        "max_acceleration_constraint_norm": f"{candidate['max_acceleration_constraint_norm']:.16e}",
                        "max_so3_fro": f"{candidate['max_so3_fro']:.16e}",
                        "max_dynamics_residual_norm": f"{candidate['max_dynamics_residual_norm']:.16e}",
                    }
                )
            except Exception as exc:  # noqa: BLE001 - keep failures visible.
                row["status"] = failure_status("failed", exc)
                for key in ("pos", "vel", "acc"):
                    method_errors["Gauss6/FullVA-local-closed-loop"][key].append(float("nan"))
            model_row_indices.append(len(rows))
            rows.append(row)

        method_summary: dict[str, dict] = {}
        for method in methods:
            orders = {
                "pos_observed_order": finite_or_none(estimate_order(list(config.step_sizes), method_errors[method]["pos"])),
                "vel_observed_order": finite_or_none(estimate_order(list(config.step_sizes), method_errors[method]["vel"])),
                "acc_observed_order": finite_or_none(estimate_order(list(config.step_sizes), method_errors[method]["acc"])),
            }
            for idx in model_row_indices:
                if rows[idx]["method"] != method:
                    continue
                for key, value in orders.items():
                    rows[idx][key] = "nan" if value is None else f"{value:.16e}"
            method_rows = [rows[idx] for idx in model_row_indices if rows[idx]["method"] == method]
            method_summary[method] = {
                "row_count": len(method_rows),
                "ok_row_count": sum(1 for row in method_rows if row["status"] == "ok"),
                "step_sizes": list(config.step_sizes),
                **orders,
            }
        model_summaries[model_name] = {
            "reference_method": "rA-public-kinematics",
            "reference_h": config.reference_h,
            "t_end": config.t_end,
            "methods": method_summary,
        }

    return rows, {
        "policy": policy,
        "run_model": config.run_model,
        "row_count": len(rows),
        "ok_row_count": sum(1 for row in rows if row["status"] == "ok"),
        "planned_row_count": sum(1 for row in rows if row["status"] == "planned_not_run"),
        "selected_rows_completed": bool(rows and all(row["status"] == "ok" for row in rows)),
        "full_external_campaign_completed": False,
        "selected_models": list(config.models),
        "selected_step_sizes": list(config.step_sizes),
        "selected_t_end": config.t_end,
        "selected_reference_h": config.reference_h,
        "models": model_summaries,
        "notes": notes,
    }


def summarize_closed_loop_same_window_work_precision_rows(rows: list[dict]) -> tuple[list[dict], dict]:
    grouped: dict[tuple[str, str], list[dict]] = {}
    for row in rows:
        grouped.setdefault((str(row.get("model", "")), str(row.get("method", ""))), []).append(row)

    rA_finest_by_model: dict[str, dict] = {}
    for (model, method), group_rows in grouped.items():
        if method != "rA-public-dynamics":
            continue
        ok_rows = [row for row in group_rows if row.get("status") == "ok"]
        if ok_rows:
            rA_finest_by_model[model] = sorted(ok_rows, key=lambda row: as_float(row, "h"))[0]

    summary_rows: list[dict] = []
    for (model, method), group_rows in sorted(grouped.items()):
        ok_rows = [row for row in group_rows if row.get("status") == "ok"]
        sorted_ok = sorted(ok_rows, key=lambda row: as_float(row, "h"))
        finest = sorted_ok[0] if sorted_ok else {}
        baseline = rA_finest_by_model.get(model, {})
        runtime_values = [as_float(row, "runtime_sec") for row in ok_rows]
        total_newton_values = [as_float(row, "total_newton_iterations") for row in ok_rows]

        def ratio_to_baseline(key: str) -> str:
            numerator = as_float(finest, key)
            denominator = as_float(baseline, key)
            if not np.isfinite(numerator) or not np.isfinite(denominator) or denominator == 0.0:
                return "nan"
            return f"{numerator / denominator:.16e}"

        summary_rows.append(
            {
                "policy": "ra2021_selected_closed_loop_same_window_work_precision_summary",
                "source_suite": "ra2021_taves_kissel_negrut",
                "case_id": f"ra2021_{model}_selected_same_window_work_precision",
                "model": model,
                "method": method,
                "row_count": len(group_rows),
                "ok_row_count": len(ok_rows),
                "t_end": finest.get("t_end", "nan"),
                "reference_method": finest.get("reference_method", "rA-public-kinematics"),
                "reference_h": finest.get("reference_h", "nan"),
                "finest_h": format_float(as_float(finest, "h")),
                "pos_observed_order": format_float(as_float(finest, "pos_observed_order")),
                "vel_observed_order": format_float(as_float(finest, "vel_observed_order")),
                "acc_observed_order": format_float(as_float(finest, "acc_observed_order")),
                "finest_pos_final_linf": format_float(as_float(finest, "pos_final_linf")),
                "finest_vel_final_linf": format_float(as_float(finest, "vel_final_linf")),
                "finest_acc_final_linf": format_float(as_float(finest, "acc_final_linf")),
                "finest_runtime_sec": format_float(as_float(finest, "runtime_sec")),
                "runtime_sec_sum": format_float(finite_sum(runtime_values)),
                "finest_avg_iterations_or_newton_per_output": format_float(
                    as_float(finest, "avg_iterations_or_newton_per_output")
                ),
                "finest_max_iterations_or_newton": format_float(as_float(finest, "max_iterations_or_newton")),
                "total_newton_iterations_sum": format_float(finite_sum(total_newton_values)),
                "finest_pos_error_ratio_vs_rA": ratio_to_baseline("pos_final_linf"),
                "finest_vel_error_ratio_vs_rA": ratio_to_baseline("vel_final_linf"),
                "finest_acc_error_ratio_vs_rA": ratio_to_baseline("acc_final_linf"),
                "finest_runtime_ratio_vs_rA": ratio_to_baseline("runtime_sec"),
                "max_dynamics_residual_norm": format_float(as_float(finest, "max_dynamics_residual_norm")),
                "notes": (
                    "Paper-ready summary of the selected same-window comparison. "
                    "Ratios use public rA dynamics at the same model and finest selected h as the baseline."
                ),
            }
        )

    return summary_rows, {
        "policy": "ra2021_selected_closed_loop_same_window_work_precision_summary",
        "row_count": len(summary_rows),
        "ok_row_count": sum(1 for row in summary_rows if int(row["ok_row_count"]) >= 1),
        "models": sorted({row["model"] for row in summary_rows}),
        "methods": sorted({row["method"] for row in summary_rows}),
        "notes": "Summarizes selected same-window final-error/work rows for manuscript tables.",
    }


def summarize_double_pendulum_coarse_same_window_work_precision_rows(
    ra_rows: list[dict],
    gauss_rows: list[dict],
) -> tuple[list[dict], dict]:
    grouped: dict[str, list[dict]] = {}
    for row in ra_rows:
        if row.get("status") == "ok":
            grouped.setdefault(f"{row.get('form', '')}-public-dynamics-coarse", []).append(row)
    if any(row.get("status") == "ok" for row in gauss_rows):
        grouped["Gauss6/FullVA-public-horizon-double-coarse"] = [
            row for row in gauss_rows if row.get("status") == "ok"
        ]

    rA_finest = {}
    rA_rows = grouped.get("rA-public-dynamics-coarse", [])
    if rA_rows:
        rA_finest = sorted(rA_rows, key=lambda row: as_float(row, "h"))[0]

    def row_error(row: dict, key: str) -> float:
        if "Gauss6/FullVA" in row.get("method", "") or row.get("row_type") == "public_horizon_double_pendulum_coarse_order_work":
            if key == "pos_final_linf":
                return as_float(row, "pos_traj_linf")
            if key == "vel_final_linf":
                return as_float(row, "vel_traj_linf")
        return as_float(row, key)

    def group_order(rows: list[dict], key: str) -> float | None:
        ok_rows = sorted(rows, key=lambda row: as_float(row, "h"), reverse=True)
        return finite_or_none(estimate_order([as_float(row, "h") for row in ok_rows], [row_error(row, key) for row in ok_rows]))

    summary_rows: list[dict] = []
    for method, method_rows in sorted(grouped.items()):
        sorted_rows = sorted(method_rows, key=lambda row: as_float(row, "h"))
        finest = sorted_rows[0] if sorted_rows else {}
        runtime_values = [as_float(row, "runtime_sec") for row in method_rows]
        iteration_values = [
            as_float(row, "avg_iterations")
            if np.isfinite(as_float(row, "avg_iterations"))
            else as_float(row, "total_newton_iterations")
            for row in method_rows
        ]

        def ratio_to_rA(key: str) -> str:
            numerator = row_error(finest, key)
            denominator = row_error(rA_finest, key)
            if not np.isfinite(numerator) or not np.isfinite(denominator) or denominator == 0.0:
                return "nan"
            return f"{numerator / denominator:.16e}"

        runtime_denominator = as_float(rA_finest, "runtime_sec")
        runtime_numerator = as_float(finest, "runtime_sec")
        runtime_ratio = (
            runtime_numerator / runtime_denominator
            if np.isfinite(runtime_numerator) and np.isfinite(runtime_denominator) and runtime_denominator != 0.0
            else float("nan")
        )
        summary_rows.append(
            {
                "policy": "ra2021_double_pendulum_coarse_same_window_work_precision_summary",
                "source_suite": "ra2021_taves_kissel_negrut",
                "case_id": "ra2021_double_pendulum_coarse_same_window_work_precision",
                "model": "double_pendulum",
                "method": method,
                "row_count": len(method_rows),
                "ok_row_count": len(method_rows),
                "t_end": finest.get("t_end", finest.get("t_final", "nan")),
                "reference_policy": finest.get("reference_policy", ""),
                "reference_h": finest.get("reference_h", "nan"),
                "finest_h": format_float(as_float(finest, "h")),
                "pos_observed_order": format_float(group_order(method_rows, "pos_final_linf")),
                "vel_observed_order": format_float(group_order(method_rows, "vel_final_linf")),
                "acc_observed_order": format_float(group_order(method_rows, "acc_final_linf")),
                "finest_pos_error": format_float(row_error(finest, "pos_final_linf")),
                "finest_vel_error": format_float(row_error(finest, "vel_final_linf")),
                "finest_acc_error": format_float(row_error(finest, "acc_final_linf")),
                "finest_runtime_sec": format_float(runtime_numerator),
                "runtime_sec_sum": format_float(finite_sum(runtime_values)),
                "finest_pos_error_ratio_vs_rA": ratio_to_rA("pos_final_linf"),
                "finest_vel_error_ratio_vs_rA": ratio_to_rA("vel_final_linf"),
                "finest_acc_error_ratio_vs_rA": ratio_to_rA("acc_final_linf"),
                "finest_runtime_ratio_vs_rA": format_float(runtime_ratio),
                "iteration_or_newton_sum": format_float(finite_sum(iteration_values)),
                "notes": (
                    "Coarse same-window double-pendulum work/precision summary. "
                    "All rows use T=3, h=0.1|0.05|0.025, reference h=0.0125; "
                    "this is not the public h=1e-4 policy and not an external superiority claim."
                ),
            }
        )

    return summary_rows, {
        "policy": "ra2021_double_pendulum_coarse_same_window_work_precision_summary",
        "row_count": len(summary_rows),
        "ok_row_count": sum(1 for row in summary_rows if int(row["ok_row_count"]) >= 1),
        "methods": sorted({row["method"] for row in summary_rows}),
        "selected_step_sizes": RA2021_DOUBLE_COARSE_STEP_SIZES,
        "selected_reference_h": RA2021_DOUBLE_COARSE_REFERENCE_H,
        "selected_t_end": RA2021_PUBLIC_T_END,
        "full_external_campaign_completed": False,
        "notes": "Coarse same-window double-pendulum order/time summary; no external superiority claim.",
    }


def ordered_values(rows: list[dict], key: str, allowed: list[str] | None = None) -> list[str]:
    values = {str(row.get(key, "")) for row in rows if row.get(key, "") != ""}
    if allowed is not None:
        return [value for value in allowed if value in values]
    return sorted(values)


def ordered_float_values(rows: list[dict], key: str) -> list[float]:
    values = sorted({as_float(row, key) for row in rows if np.isfinite(as_float(row, key))}, reverse=True)
    return values


def rows_order(rows: list[dict], h_key: str, error_key: str) -> float | None:
    ok_rows = [row for row in rows if row.get("status") == "ok"]
    return finite_or_none(estimate_order([as_float(row, h_key) for row in ok_rows], [as_float(row, error_key) for row in ok_rows]))


def rows_first_float(rows: list[dict], key: str) -> float | None:
    for row in rows:
        value = as_float(row, key)
        if np.isfinite(value):
            return value
    return None


def summarize_ra2021_rows_from_csv(rows: list[dict]) -> dict:
    groups: dict[str, dict] = {}
    selected_forms = ordered_values(rows, "form", RA2021_FORMS)
    selected_models = ordered_values(rows, "model", [model.name for model in RA2021_ORDER_MODELS])
    selected_groups: list[str] = []
    for form in selected_forms:
        for model in selected_models:
            group_rows = [row for row in rows if row.get("form") == form and row.get("model") == model]
            if not group_rows:
                continue
            group_key = f"{form}:{model}"
            selected_groups.append(group_key)
            public_ok = [
                row
                for row in group_rows
                if row.get("status") == "ok"
                and np.isclose(as_float(row, "t_end"), RA2021_PUBLIC_T_END)
                and np.isclose(as_float(row, "reference_h"), RA2021_PUBLIC_REFERENCE_H)
                and as_float(row, "h") in RA2021_ORDER_STEP_SIZES
            ]
            groups[group_key] = {
                "row_count": len(group_rows),
                "ok_row_count": sum(1 for row in group_rows if row.get("status") == "ok"),
                "planned_row_count": sum(1 for row in group_rows if row.get("status") == "planned_not_run"),
                "reference_status": group_rows[0].get("reference_status", "unknown"),
                "reference_runtime_sec": rows_first_float(group_rows, "reference_runtime_sec"),
                "pos_final_linf_order": rows_order(group_rows, "h", "pos_final_linf"),
                "vel_final_linf_order": rows_order(group_rows, "h", "vel_final_linf"),
                "acc_final_linf_order": rows_order(group_rows, "h", "acc_final_linf"),
                "runtime_sec_at_reference_h": rows_first_float(
                    [row for row in group_rows if np.isclose(as_float(row, "h"), RA2021_PUBLIC_REFERENCE_H)],
                    "runtime_sec",
                ),
                "avg_iterations_at_reference_h": rows_first_float(
                    [row for row in group_rows if np.isclose(as_float(row, "h"), RA2021_PUBLIC_REFERENCE_H)],
                    "avg_iterations",
                ),
                "public_step_trio_completed": len(public_ok) == len(RA2021_ORDER_STEP_SIZES),
            }
    public_group_count = sum(1 for group in groups.values() if group.get("public_step_trio_completed"))
    return {
        "policy": rows[0].get("policy", "ra2021_rebuilt_from_csv") if rows else "ra2021_rebuilt_from_csv",
        "run_mode": "full_ra2021_order" if public_group_count == 9 else "rebuilt_ra2021_order",
        "run_public_code": any(row.get("status") == "ok" for row in rows),
        "row_count": len(rows),
        "ok_row_count": sum(1 for row in rows if row.get("status") == "ok"),
        "planned_row_count": sum(1 for row in rows if row.get("status") == "planned_not_run"),
        "selected_forms": selected_forms,
        "selected_models": selected_models,
        "selected_groups": selected_groups,
        "selected_step_sizes": ordered_float_values(rows, "h"),
        "selected_t_end": rows_first_float(rows, "t_end"),
        "selected_reference_h": rows_first_float(rows, "reference_h"),
        "public_step_trio_group_count": public_group_count,
        "public_step_trio_required_group_count": len(RA2021_FORMS) * len(RA2021_ORDER_MODELS),
        "full_ra2021_order_completed": public_group_count == len(RA2021_FORMS) * len(RA2021_ORDER_MODELS),
        "groups": groups,
        "notes": "Rebuilt from existing ra2021_order_rows.csv after a summary write interruption.",
    }


def summarize_ra2021_timing_rows_from_csv(rows: list[dict]) -> dict:
    groups: dict[str, dict] = {}
    selected_forms = ordered_values(rows, "form", RA2021_FORMS)
    selected_models = ordered_values(rows, "model", [model.name for model in RA2021_TIMING_MODELS])
    selected_groups: list[str] = []
    for form in selected_forms:
        for model in selected_models:
            group_rows = [row for row in rows if row.get("form") == form and row.get("model") == model]
            if not group_rows:
                continue
            selected_groups.append(f"{form}:{model}")
            ok_rows = [row for row in group_rows if row.get("status") == "ok"]
            finest = ok_rows[0] if ok_rows else group_rows[0]
            groups[f"{form}:{model}"] = {
                "status": finest.get("status", "unknown"),
                "runtime_sec": rows_first_float(group_rows, "runtime_sec"),
                "avg_iterations": rows_first_float(group_rows, "avg_iterations"),
                "max_iterations": rows_first_float(group_rows, "max_iterations"),
                "public_timing_policy": finest.get("public_timing_policy") == "True",
            }
    public_timing_rows_completed = sum(
        1
        for row in rows
        if row.get("status") == "ok" and row.get("public_timing_policy") == "True"
    )
    public_timing_required_count = len(RA2021_FORMS) * len(RA2021_TIMING_MODELS)
    return {
        "policy": rows[0].get("policy", "ra2021_public_timing_rebuilt_from_csv")
        if rows
        else "ra2021_public_timing_rebuilt_from_csv",
        "run_mode": "rebuilt_ra2021_public_timing",
        "run_public_code": any(row.get("status") == "ok" for row in rows),
        "full_ra2021_timing_completed": public_timing_rows_completed == public_timing_required_count,
        "row_count": len(rows),
        "ok_row_count": sum(1 for row in rows if row.get("status") == "ok"),
        "planned_row_count": sum(1 for row in rows if row.get("status") == "planned_not_run"),
        "selected_rows_completed": bool(rows and all(row.get("status") == "ok" for row in rows)),
        "public_timing_policy": public_timing_rows_completed > 0,
        "public_timing_rows_completed": public_timing_rows_completed,
        "public_timing_required_count": public_timing_required_count,
        "selected_forms": selected_forms,
        "selected_models": selected_models,
        "selected_groups": selected_groups,
        "selected_h": rows_first_float(rows, "h"),
        "selected_t_end": rows_first_float(rows, "t_end"),
        "selected_tolerance": rows_first_float(rows, "tolerance"),
        "mode": rows[0].get("mode", "") if rows else "",
        "groups": groups,
        "notes": "Rebuilt from existing ra2021_public_timing_rows.csv.",
    }


def summarize_ra2021_double_pendulum_order_rows_from_csv(rows: list[dict]) -> dict:
    groups: dict[str, dict] = {}
    selected_forms = ordered_values(rows, "form", RA2021_FORMS)
    selected_groups: list[str] = []
    for form in selected_forms:
        group_rows = [row for row in rows if row.get("form") == form]
        if not group_rows:
            continue
        selected_groups.append(f"{form}:double_pendulum")
        public_rows = [
            row
            for row in group_rows
            if row.get("status") == "ok" and row.get("public_double_order_policy") == "True"
        ]
        groups[f"{form}:double_pendulum"] = {
            "row_count": len(group_rows),
            "ok_row_count": sum(1 for row in group_rows if row.get("status") == "ok"),
            "reference_status": group_rows[0].get("reference_status", "unknown"),
            "reference_runtime_sec": rows_first_float(group_rows, "reference_runtime_sec"),
            "pos_final_linf_order": rows_order(group_rows, "h", "pos_final_linf"),
            "vel_final_linf_order": rows_order(group_rows, "h", "vel_final_linf"),
            "acc_final_linf_order": rows_order(group_rows, "h", "acc_final_linf"),
            "public_double_order_policy": bool(public_rows),
            "selected_step_trio_completed": len(public_rows) == len(RA2021_DOUBLE_ORDER_STEP_SIZES),
        }
    completed_groups = sum(1 for group in groups.values() if group["selected_step_trio_completed"])
    return {
        "policy": rows[0].get("policy", "ra2021_double_pendulum_order_rebuilt_from_csv")
        if rows
        else "ra2021_double_pendulum_order_rebuilt_from_csv",
        "run_mode": "rebuilt_ra2021_double_pendulum_order",
        "run_public_code": any(row.get("status") == "ok" for row in rows),
        "full_ra2021_double_order_completed": completed_groups == len(RA2021_FORMS),
        "row_count": len(rows),
        "ok_row_count": sum(1 for row in rows if row.get("status") == "ok"),
        "planned_row_count": sum(1 for row in rows if row.get("status") == "planned_not_run"),
        "selected_forms": selected_forms,
        "selected_groups": selected_groups,
        "selected_step_sizes": ordered_float_values(rows, "h"),
        "selected_reference_h": rows_first_float(rows, "reference_h"),
        "selected_t_end": rows_first_float(rows, "t_end"),
        "selected_tolerance": rows_first_float(rows, "tolerance"),
        "public_double_order_policy": completed_groups > 0,
        "selected_step_trio_group_count": completed_groups,
        "selected_step_trio_required_group_count": len(RA2021_FORMS),
        "groups": groups,
        "notes": "Rebuilt from existing ra2021_double_pendulum_order_rows.csv.",
    }


def summarize_ra2021_double_pendulum_coarse_order_rows_from_csv(rows: list[dict]) -> dict:
    groups: dict[str, dict] = {}
    selected_forms = ordered_values(rows, "form", RA2021_FORMS)
    selected_groups: list[str] = []
    for form in selected_forms:
        group_rows = [row for row in rows if row.get("form") == form]
        if not group_rows:
            continue
        ok_rows = [row for row in group_rows if row.get("status") == "ok"]
        selected_groups.append(f"{form}:double_pendulum")
        groups[f"{form}:double_pendulum"] = {
            "row_count": len(group_rows),
            "ok_row_count": len(ok_rows),
            "reference_status": group_rows[0].get("reference_status", "unknown"),
            "reference_runtime_sec": rows_first_float(group_rows, "reference_runtime_sec"),
            "pos_final_linf_order": rows_order(group_rows, "h", "pos_final_linf"),
            "vel_final_linf_order": rows_order(group_rows, "h", "vel_final_linf"),
            "acc_final_linf_order": rows_order(group_rows, "h", "acc_final_linf"),
            "coarse_same_window_policy": True,
            "selected_step_trio_completed": len(ok_rows) == len(group_rows) and len(group_rows) >= 3,
        }
    completed_groups = sum(1 for group in groups.values() if group["selected_step_trio_completed"])
    return {
        "policy": rows[0].get("policy", "ra2021_double_pendulum_coarse_order_rebuilt_from_csv")
        if rows
        else "ra2021_double_pendulum_coarse_order_rebuilt_from_csv",
        "run_mode": "rebuilt_ra2021_double_pendulum_coarse_order",
        "run_public_code": any(row.get("status") == "ok" for row in rows),
        "full_external_campaign_completed": False,
        "row_count": len(rows),
        "ok_row_count": len([row for row in rows if row.get("status") == "ok"]),
        "planned_row_count": sum(1 for row in rows if row.get("status") == "planned_not_run"),
        "selected_forms": selected_forms,
        "selected_groups": selected_groups,
        "selected_step_sizes": ordered_float_values(rows, "h"),
        "selected_reference_h": rows_first_float(rows, "reference_h"),
        "selected_t_end": rows_first_float(rows, "t_end"),
        "selected_tolerance": rows_first_float(rows, "tolerance"),
        "selected_step_trio_group_count": completed_groups,
        "selected_step_trio_required_group_count": len(selected_forms),
        "groups": groups,
        "notes": (
            "Coarse same-window public rA/rp/reps double-pendulum order rows using "
            "T=3, h=0.1|0.05|0.025, and reference h=0.0125. This is not the public h=1e-4 policy."
        ),
    }


def summarize_ra2021_single_pendulum_coarse_order_rows_from_csv(rows: list[dict]) -> dict:
    groups: dict[str, dict] = {}
    selected_forms = ordered_values(rows, "form", RA2021_FORMS)
    selected_groups: list[str] = []
    for form in selected_forms:
        group_rows = [row for row in rows if row.get("form") == form]
        if not group_rows:
            continue
        ok_rows = [row for row in group_rows if row.get("status") == "ok"]
        selected_groups.append(f"{form}:single_pendulum")
        groups[f"{form}:single_pendulum"] = {
            "row_count": len(group_rows),
            "ok_row_count": len(ok_rows),
            "reference_status": group_rows[0].get("reference_status", "unknown"),
            "reference_runtime_sec": rows_first_float(group_rows, "reference_runtime_sec"),
            "pos_final_linf_order": rows_order(group_rows, "h", "pos_final_linf"),
            "vel_final_linf_order": rows_order(group_rows, "h", "vel_final_linf"),
            "acc_final_linf_order": rows_order(group_rows, "h", "acc_final_linf"),
            "coarse_same_window_policy": True,
            "selected_step_trio_completed": len(ok_rows) == len(group_rows) and len(group_rows) >= 3,
        }
    completed_groups = sum(1 for group in groups.values() if group["selected_step_trio_completed"])
    return {
        "policy": rows[0].get("policy", "ra2021_single_pendulum_coarse_order_rebuilt_from_csv")
        if rows
        else "ra2021_single_pendulum_coarse_order_rebuilt_from_csv",
        "run_mode": "rebuilt_ra2021_single_pendulum_coarse_order",
        "run_public_code": any(row.get("status") == "ok" for row in rows),
        "full_external_campaign_completed": False,
        "full_ra2021_order_completed": False,
        "row_count": len(rows),
        "ok_row_count": len([row for row in rows if row.get("status") == "ok"]),
        "planned_row_count": sum(1 for row in rows if row.get("status") == "planned_not_run"),
        "selected_forms": selected_forms,
        "selected_models": ["single_pendulum"] if rows else [],
        "selected_groups": selected_groups,
        "selected_step_sizes": ordered_float_values(rows, "h"),
        "selected_reference_h": rows_first_float(rows, "reference_h"),
        "selected_t_end": rows_first_float(rows, "t_end"),
        "selected_tolerance": rows_first_float(rows, "tolerance"),
        "coarse_same_window_policy": True,
        "selected_step_trio_group_count": completed_groups,
        "selected_step_trio_required_group_count": len(selected_forms),
        "groups": groups,
        "notes": (
            "Coarse same-window public rA/rp/reps single-pendulum order rows using "
            "T=3, h=0.1|0.05|0.025, and reference h=0.0125. This is not the public h=1e-4 policy."
        ),
    }


def summarize_gauss6_single_rows_from_csv(rows: list[dict], public_horizon: bool) -> dict:
    ok_rows = [row for row in rows if row.get("status") == "ok"]
    orders = {
        "position_observed_order": rows_first_float(rows, "position_observed_order")
        if rows_first_float(rows, "position_observed_order") is not None
        else rows_order(rows, "h", "position_l2_error"),
        "velocity_observed_order": rows_first_float(rows, "velocity_observed_order")
        if rows_first_float(rows, "velocity_observed_order") is not None
        else rows_order(rows, "h", "velocity_l2_error"),
        "orientation_observed_order": rows_first_float(rows, "orientation_observed_order")
        if rows_first_float(rows, "orientation_observed_order") is not None
        else rows_order(rows, "h", "orientation_error_rad"),
        "omega_observed_order": rows_first_float(rows, "omega_observed_order")
        if rows_first_float(rows, "omega_observed_order") is not None
        else rows_order(rows, "h", "omega_l2_error"),
    }
    public_h_count = sum(
        1
        for row in ok_rows
        if row.get("public_policy_time_window") == "True" and row.get("public_policy_h") == "True"
    )
    summary = {
        "policy": rows[0].get("policy", "gauss6_single_rebuilt_from_csv") if rows else "gauss6_single_rebuilt_from_csv",
        "run_mode": (
            "gauss6_fullva_public_horizon_single_pendulum" if public_horizon else "gauss6_fullva_single_pilot"
        ),
        "run_model": bool(ok_rows),
        "row_count": len(rows),
        "ok_row_count": len(ok_rows),
        "planned_row_count": sum(1 for row in rows if row.get("status") == "planned_not_run"),
        "selected_rows_completed": bool(rows and len(ok_rows) == len(rows)),
        "full_external_campaign_completed": False,
        "selected_models": ["single_pendulum"],
        "selected_step_sizes": ordered_float_values(rows, "h"),
        "selected_t_end": rows_first_float(rows, "t_end"),
        "selected_reference_h": rows_first_float(rows, "reference_h"),
        "public_reference_pos_final_linf": rows_first_float(rows, "public_reference_pos_final_linf"),
        "public_reference_vel_final_linf": rows_first_float(rows, "public_reference_vel_final_linf"),
        "public_reference_acc_final_linf": rows_first_float(rows, "public_reference_acc_final_linf"),
        **orders,
    }
    if public_horizon:
        summary.update(
            {
                "public_policy_time_window": all(row.get("public_policy_time_window") == "True" for row in rows),
                "public_step_size_rows_completed": public_h_count,
                "public_step_size_required_count": len(RA2021_ORDER_STEP_SIZES),
                "public_single_step_trio_completed": public_h_count == len(RA2021_ORDER_STEP_SIZES),
                "notes": rows[0].get("notes", "") if rows else "",
            }
        )
    return summary


def summarize_gauss6_double_public_horizon_coarse_rows_from_csv(rows: list[dict]) -> dict:
    ok_rows = [row for row in rows if row.get("status") == "ok"]
    public_h_count = sum(
        1
        for row in ok_rows
        if row.get("public_policy_time_window") == "True" and row.get("public_policy_h") == "True"
    )
    return {
        "policy": rows[0].get("policy", "gauss6_double_public_horizon_coarse_rebuilt_from_csv")
        if rows
        else "gauss6_double_public_horizon_coarse_rebuilt_from_csv",
        "run_mode": "gauss6_fullva_public_horizon_double_coarse",
        "run_model": bool(ok_rows),
        "row_count": len(rows),
        "ok_row_count": len(ok_rows),
        "planned_row_count": sum(1 for row in rows if row.get("status") == "planned_not_run"),
        "selected_rows_completed": bool(rows and len(ok_rows) == len(rows)),
        "full_external_campaign_completed": False,
        "public_policy_time_window": all(row.get("public_policy_time_window") == "True" for row in rows)
        if rows
        else False,
        "public_policy_h_rows_completed": public_h_count,
        "public_policy_h_required_count": len(RA2021_ORDER_STEP_SIZES),
        "public_double_step_trio_completed": False,
        "selected_models": ["double_pendulum"],
        "selected_step_sizes": ordered_float_values(rows, "h"),
        "selected_t_end": rows_first_float(rows, "t_end"),
        "selected_reference_h": rows_first_float(rows, "reference_h"),
        "reference_status": rows[0].get("reference_status", "unknown") if rows else "unknown",
        "reference_runtime_sec": rows_first_float(rows, "reference_runtime_sec"),
        "pos_observed_order": rows_first_float(rows, "pos_observed_order")
        if rows_first_float(rows, "pos_observed_order") is not None
        else rows_order(rows, "h", "pos_traj_linf"),
        "vel_observed_order": rows_first_float(rows, "vel_observed_order")
        if rows_first_float(rows, "vel_observed_order") is not None
        else rows_order(rows, "h", "vel_traj_linf"),
        "max_endpoint_constraint_norm": max(
            (as_float(row, "max_endpoint_constraint_norm") for row in ok_rows), default=0.0
        ),
        "max_endpoint_velocity_constraint_norm": max(
            (as_float(row, "max_endpoint_velocity_constraint_norm") for row in ok_rows), default=0.0
        ),
        "total_newton_iterations": int(sum(as_float(row, "total_newton_iterations") for row in ok_rows)),
        "notes": rows[0].get("notes", "") if rows else "",
    }


def summarize_closed_loop_rows_from_csv(rows: list[dict], public_horizon: bool) -> dict:
    model_summaries: dict[str, dict] = {}
    for model in ordered_values(rows, "model", ["four_link", "slider_crank"]):
        model_rows = [row for row in rows if row.get("model") == model]
        ok_rows = [row for row in model_rows if row.get("status") == "ok"]
        model_summaries[model] = {
            "status": "accepted_closed_loop_kinematic_reaction" if model_rows and len(ok_rows) == len(model_rows) else "partial_failed",
            "step_sizes": ordered_float_values(model_rows, "h"),
            "reference_h": rows_first_float(model_rows, "reference_h"),
            "t_end": rows_first_float(model_rows, "t_end"),
            "row_count": len(model_rows),
            "ok_row_count": len(ok_rows),
            "max_position_constraint_norm": max((as_float(row, "max_position_constraint_norm") for row in ok_rows), default=0.0),
            "max_velocity_constraint_norm": max((as_float(row, "max_velocity_constraint_norm") for row in ok_rows), default=0.0),
            "max_acceleration_constraint_norm": max((as_float(row, "max_acceleration_constraint_norm") for row in ok_rows), default=0.0),
            "max_so3_fro": max((as_float(row, "max_so3_fro") for row in ok_rows), default=0.0),
            "max_trans_dynamics_residual": max((as_float(row, "max_trans_dynamics_residual") for row in ok_rows), default=0.0),
            "max_rot_dynamics_residual": max((as_float(row, "max_rot_dynamics_residual") for row in ok_rows), default=0.0),
            "max_dynamics_residual_norm": max((as_float(row, "max_dynamics_residual_norm") for row in ok_rows), default=0.0),
            "max_multiplier_norm": max((as_float(row, "max_multiplier_norm") for row in ok_rows), default=0.0),
            "max_step_correction_norm": max((as_float(row, "max_step_correction_norm") for row in ok_rows), default=0.0),
            "min_singular_value": min((as_float(row, "min_singular_value") for row in ok_rows), default=None),
            "max_condition_number": max((as_float(row, "max_condition_number") for row in ok_rows), default=0.0),
            "total_newton_iterations": int(sum(as_float(row, "total_newton_iterations") for row in ok_rows)),
            "max_newton_iterations": int(max((as_float(row, "max_newton_iterations") for row in ok_rows), default=0.0)),
            "pos_observed_order": rows_order(model_rows, "h", "pos_traj_linf"),
            "vel_observed_order": rows_order(model_rows, "h", "vel_traj_linf"),
            "acc_observed_order": rows_order(model_rows, "h", "acc_traj_linf"),
            "lambda_observed_order": rows_order(model_rows, "h", "lambda_traj_linf"),
        }
    ok_count = sum(1 for row in rows if row.get("status") == "ok")
    public_h_count = sum(
        1
        for row in rows
        if row.get("status") == "ok"
        and row.get("public_policy_time_window") == "True"
        and row.get("public_policy_h") == "True"
    )
    selected_models = ordered_values(rows, "model", ["four_link", "slider_crank"])
    summary = {
        "policy": rows[0].get("policy", "gauss6_closed_loop_rebuilt_from_csv") if rows else "gauss6_closed_loop_rebuilt_from_csv",
        "run_mode": (
            "gauss6_fullva_public_horizon_closed_loop_2021_tranche"
            if public_horizon
            else "gauss6_fullva_closed_loop_2021_pilot"
        ),
        "run_model": ok_count > 0,
        "row_count": len(rows),
        "ok_row_count": ok_count,
        "planned_row_count": sum(1 for row in rows if row.get("status") == "planned_not_run"),
        "selected_rows_completed": bool(rows and ok_count == len(rows)),
        "full_external_campaign_completed": False,
        "selected_models": selected_models,
        "selected_step_sizes": ordered_float_values(rows, "h"),
        "selected_t_end": rows_first_float(rows, "t_end"),
        "selected_reference_h": rows_first_float(rows, "reference_h"),
        "models": model_summaries,
        "notes": rows[0].get("notes", "") if rows else "",
    }
    if public_horizon:
        summary.update(
            {
                "public_policy_time_window": all(row.get("public_policy_time_window") == "True" for row in rows),
                "public_step_size_rows_completed": public_h_count,
                "public_step_size_required_count": len(selected_models) * len(RA2021_ORDER_STEP_SIZES),
                "public_closed_loop_step_trios_completed": public_h_count == len(selected_models) * len(RA2021_ORDER_STEP_SIZES),
            }
        )
    return summary


def summarize_same_window_rows_from_csv(rows: list[dict]) -> dict:
    model_summaries: dict[str, dict] = {}
    for model in ordered_values(rows, "model", ["four_link", "slider_crank"]):
        model_rows = [row for row in rows if row.get("model") == model]
        method_summaries: dict[str, dict] = {}
        for method in ordered_values(model_rows, "method"):
            method_rows = [row for row in model_rows if row.get("method") == method]
            method_summaries[method] = {
                "row_count": len(method_rows),
                "ok_row_count": sum(1 for row in method_rows if row.get("status") == "ok"),
                "step_sizes": ordered_float_values(method_rows, "h"),
                "pos_observed_order": rows_first_float(method_rows, "pos_observed_order"),
                "vel_observed_order": rows_first_float(method_rows, "vel_observed_order"),
                "acc_observed_order": rows_first_float(method_rows, "acc_observed_order"),
            }
        model_summaries[model] = {
            "methods": method_summaries,
            "reference_h": rows_first_float(model_rows, "reference_h"),
            "reference_method": model_rows[0].get("reference_method", "unknown") if model_rows else "unknown",
            "t_end": rows_first_float(model_rows, "t_end"),
        }
    ok_count = sum(1 for row in rows if row.get("status") == "ok")
    return {
        "policy": rows[0].get("policy", "same_window_rebuilt_from_csv") if rows else "same_window_rebuilt_from_csv",
        "run_model": ok_count > 0,
        "row_count": len(rows),
        "ok_row_count": ok_count,
        "planned_row_count": sum(1 for row in rows if row.get("status") == "planned_not_run"),
        "selected_rows_completed": bool(rows and ok_count == len(rows)),
        "full_external_campaign_completed": False,
        "selected_models": ordered_values(rows, "model", ["four_link", "slider_crank"]),
        "selected_step_sizes": ordered_float_values(rows, "h"),
        "selected_t_end": rows_first_float(rows, "t_end"),
        "selected_reference_h": rows_first_float(rows, "reference_h"),
        "models": model_summaries,
        "notes": rows[0].get("notes", "") if rows else "",
    }


def summarize_hi2022_rows_from_csv(rows: list[dict]) -> dict:
    groups: dict[str, dict] = {}
    selected_forms = ordered_values(rows, "form", HI2022_FORMS)
    selected_models = ordered_values(rows, "model", HI2022_MODELS)
    for form in selected_forms:
        for model in selected_models:
            group_rows = [row for row in rows if row.get("form") == form and row.get("model") == model]
            if not group_rows:
                continue
            ok_public = [row for row in group_rows if row.get("status") == "ok"]
            groups[f"{form}:{model}"] = {
                "row_count": len(group_rows),
                "ok_row_count": len(ok_public),
                "planned_row_count": sum(1 for row in group_rows if row.get("status") == "planned_not_run"),
                "reference_mode": group_rows[0].get("reference_mode", "unknown") if group_rows else "unknown",
                "reference_policy": group_rows[0].get("reference_policy", "unknown") if group_rows else "unknown",
                "reference_status": group_rows[0].get("reference_status", "unknown") if group_rows else "unknown",
                "reference_execution_path": group_rows[0].get("reference_execution_path", "unknown")
                if group_rows
                else "unknown",
                "execution_paths": ordered_values(group_rows, "execution_path", ["public_run_function", "state_history_replay"]),
                "pos_final_linf_order": rows_order(group_rows, "h", "pos_final_linf"),
                "vel_final_linf_order": rows_order(group_rows, "h", "vel_final_linf"),
                "acc_final_linf_order": rows_order(group_rows, "h", "acc_final_linf"),
                "selected_step_trio_completed": len(ok_public) >= 3,
            }
    return {
        "policy": rows[0].get("policy", "hi2022_rebuilt_from_csv") if rows else "hi2022_rebuilt_from_csv",
        "run_mode": rows[0].get("run_mode", "hi2022_bounded_pilot") if rows else "hi2022_bounded_pilot",
        "run_public_code": any(row.get("status") == "ok" for row in rows),
        "row_count": len(rows),
        "ok_row_count": sum(1 for row in rows if row.get("status") == "ok"),
        "planned_row_count": sum(1 for row in rows if row.get("status") == "planned_not_run"),
        "selected_forms": selected_forms,
        "selected_models": selected_models,
        "selected_groups": list(groups),
        "selected_step_sizes": ordered_float_values(rows, "h"),
        "selected_t_end": rows_first_float(rows, "t_end"),
        "selected_reference_h": rows_first_float(rows, "reference_h"),
        "selected_step_trio_group_count": sum(1 for group in groups.values() if group.get("selected_step_trio_completed")),
        "selected_step_trio_required_group_count": len(selected_forms) * len(selected_models),
        "full_hi2022_campaign_completed": False,
        "groups": groups,
        "notes": "Rebuilt from existing hi2022_halfimplicit_rows.csv after a summary write interruption.",
    }


def rebuild_summary_from_existing_results() -> dict:
    run_plan = read_csv_rows(RESULTS / "cross_paper_run_plan.csv")
    order_rows = read_csv_rows(RESULTS / "ra2021_order_rows.csv")
    timing_rows = read_csv_rows_if_exists(RESULTS / "ra2021_public_timing_rows.csv")
    double_order_rows = read_csv_rows_if_exists(RESULTS / "ra2021_double_pendulum_order_rows.csv")
    double_coarse_rows = read_csv_rows_if_exists(RESULTS / "ra2021_double_pendulum_coarse_order_rows.csv")
    single_coarse_public_rows = read_csv_rows_if_exists(RESULTS / "ra2021_single_pendulum_coarse_order_rows.csv")
    gauss6_rows = read_csv_rows(RESULTS / "gauss6_fullva_external_rows.csv")
    public_single_rows = read_csv_rows(RESULTS / "gauss6_fullva_public_horizon_single_rows.csv")
    public_single_coarse_rows = read_csv_rows_if_exists(
        RESULTS / "gauss6_fullva_public_horizon_single_coarse_rows.csv"
    )
    public_double_coarse_rows = read_csv_rows_if_exists(
        RESULTS / "gauss6_fullva_public_horizon_double_coarse_rows.csv"
    )
    closed_loop_rows = read_csv_rows(RESULTS / "gauss6_fullva_closed_loop_external_rows.csv")
    public_closed_loop_rows = read_csv_rows(RESULTS / "gauss6_fullva_public_horizon_closed_loop_rows.csv")
    comparison_rows = read_csv_rows(RESULTS / "gauss6_fullva_closed_loop_same_window_comparison_rows.csv")
    hi2022_rows = read_csv_rows(RESULTS / "hi2022_halfimplicit_rows.csv")
    vp_rows = read_csv_rows(RESULTS / "velocity_partitioning_code_search.csv")

    ra2021_summary = summarize_ra2021_rows_from_csv(order_rows)
    timing_summary = summarize_ra2021_timing_rows_from_csv(timing_rows)
    double_order_summary = summarize_ra2021_double_pendulum_order_rows_from_csv(double_order_rows)
    double_coarse_summary = summarize_ra2021_double_pendulum_coarse_order_rows_from_csv(double_coarse_rows)
    single_coarse_public_summary = summarize_ra2021_single_pendulum_coarse_order_rows_from_csv(
        single_coarse_public_rows
    )
    order_work_rows, order_work_summary = summarize_ra2021_public_order_work_rows(order_rows, ra2021_summary)
    write_csv(RESULTS / "ra2021_public_order_work_summary.csv", order_work_rows)
    comparison_work_rows, comparison_work_summary = summarize_closed_loop_same_window_work_precision_rows(
        comparison_rows
    )
    write_csv(RESULTS / "gauss6_closed_loop_same_window_work_precision_summary.csv", comparison_work_rows)
    gauss6_summary = summarize_gauss6_single_rows_from_csv(gauss6_rows, public_horizon=False)
    public_single_summary = summarize_gauss6_single_rows_from_csv(public_single_rows, public_horizon=True)
    public_single_coarse_summary = summarize_gauss6_single_rows_from_csv(
        public_single_coarse_rows,
        public_horizon=True,
    )
    public_single_coarse_summary.update(
        {
            "run_mode": "gauss6_fullva_public_horizon_single_coarse",
            "coarse_same_window_policy": bool(public_single_coarse_rows),
            "public_policy_h_rows_completed": 0,
            "public_single_step_trio_completed": False,
            "full_external_campaign_completed": False,
            "notes": (
                "Coarse same-window Gauss6/FullVA single-pendulum rows rebuilt from CSV; "
                "no default h=1e-4 execution."
            ),
        }
    )
    public_double_coarse_summary = summarize_gauss6_double_public_horizon_coarse_rows_from_csv(
        public_double_coarse_rows
    )
    double_coarse_work_rows, double_coarse_work_summary = (
        summarize_double_pendulum_coarse_same_window_work_precision_rows(
            double_coarse_rows,
            public_double_coarse_rows,
        )
    )
    write_csv(RESULTS / "double_pendulum_coarse_same_window_work_precision_summary.csv", double_coarse_work_rows)
    single_work_json_path = RESULTS / "single_pendulum_coarse_same_window_work_precision_summary.json"
    if single_work_json_path.exists():
        single_coarse_work_summary = read_json(single_work_json_path)
    else:
        single_work_rows = read_csv_rows_if_exists(
            RESULTS / "single_pendulum_coarse_same_window_work_precision_summary.csv"
        )
        single_coarse_work_summary = {
            "policy": "ra2021_single_pendulum_coarse_same_window_work_precision_summary",
            "row_count": len(single_work_rows),
            "ok_row_count": len(single_work_rows),
            "methods": ordered_values(single_work_rows, "method"),
            "selected_step_sizes": [0.1, 0.05, 0.025] if single_work_rows else [],
            "selected_reference_h": rows_first_float(single_work_rows, "reference_h"),
            "selected_t_end": rows_first_float(single_work_rows, "t_end"),
            "full_external_campaign_completed": False,
            "external_superiority_claim": False,
            "default_policy": "coarse_first_no_default_1e-4",
        }
    floor_audit_json_path = RESULTS / "closed_loop_dynamic_error_floor_audit.json"
    if floor_audit_json_path.exists():
        closed_loop_floor_audit_summary = read_json(floor_audit_json_path)
    else:
        closed_loop_floor_audit_summary = {
            "row_count": 0,
            "velocity_acceleration_evidence_count": 0,
            "position_floor_blocker_count": 0,
            "accepted_dynamic_order_count": 0,
            "external_superiority_claim": False,
            "default_policy": "coarse_first_no_default_1e-4",
        }
    coarse_probe_json_path = RESULTS / "closed_loop_coarse_dynamic_order_probe.json"
    if coarse_probe_json_path.exists():
        closed_loop_coarse_probe_summary = read_json(coarse_probe_json_path)
    else:
        closed_loop_coarse_probe_summary = {
            "row_count": 0,
            "ok_row_count": 0,
            "failed_row_count": 0,
            "public_failed_row_count": 0,
            "local_velocity_evidence_rows": 0,
            "local_acceleration_evidence_rows": 0,
            "local_position_floor_rows": 0,
            "accepted_dynamic_order_count": 0,
            "external_superiority_claim": False,
            "default_policy": "coarse_first_no_default_1e-4",
        }
    feasibility_audit_json_path = RESULTS / "closed_loop_true_dynamic_row_feasibility_audit.json"
    if feasibility_audit_json_path.exists():
        closed_loop_feasibility_audit_summary = read_json(feasibility_audit_json_path)
    else:
        closed_loop_feasibility_audit_summary = {
            "row_count": 0,
            "true_dynamic_local_rows_available": 0,
            "accepted_dynamic_order_count": 0,
            "current_local_row_kind": "kinematic_fullva_plus_reaction_reconstruction",
            "required_next_implementation": (
                "local_closed_loop_dynamic_dae_gauss6_fullva_runner_or_residual_to_error_theorem"
            ),
            "strict_public_policy_1e-4_required": False,
            "external_superiority_claim": False,
            "default_policy": "coarse_first_no_default_1e-4",
        }
    residual_to_error_json_path = RESULTS / "closed_loop_residual_to_error_theorem_obligations.json"
    if residual_to_error_json_path.exists():
        closed_loop_residual_to_error_summary = read_json(residual_to_error_json_path)
    else:
        closed_loop_residual_to_error_summary = {
            "obligation_count": 0,
            "blocking_obligation_count": 0,
            "accepted_residual_to_error_theorem": False,
            "accepted_dynamic_order_count": 0,
            "external_superiority_claim": False,
            "default_policy": "coarse_first_no_default_1e-4",
        }
    closed_loop_summary = summarize_closed_loop_rows_from_csv(closed_loop_rows, public_horizon=False)
    public_closed_loop_summary = summarize_closed_loop_rows_from_csv(public_closed_loop_rows, public_horizon=True)
    comparison_summary = summarize_same_window_rows_from_csv(comparison_rows)
    hi2022_summary = summarize_hi2022_rows_from_csv(hi2022_rows)
    public_web_search_status = next(
        (
            row.get("status", "")
            for row in vp_rows
            if row.get("evidence_type") == "public_web_search"
        ),
        "not_recorded",
    )
    vp_summary = {
        "status": VP_CODE_STATUS,
        "row_count": len(vp_rows),
        "relevant_code_path_resolved": False,
        "searched_refs": list(VP_SEARCH_REFS),
        "public_web_search_status": public_web_search_status,
        "easychair_visible_repository_reference": (
            "https://github.com/uwsbel/public-metadata/tree/master/2021/ASME/rA-formulation"
        ),
    }
    return {
        "version": "v048_cross_paper_same_test_benchmarks",
        "schema": "v048-cross-paper-benchmark-harness-v1",
        "python": platform.python_version(),
        "platform": platform.platform(),
        "numpy": np.__version__,
        "sbel_root": str(SBEL_ROOT),
        "sbel_commit": git_commit(SBEL_ROOT),
        "runtime_patches": [],
        "run_mode": ra2021_summary["run_mode"],
        "same_test_campaign_status": "not_run",
        "external_superiority_claim": False,
        "gauss6_fullva_external_rows_completed": False,
        "gauss6_fullva_selected_rows_completed": gauss6_summary["selected_rows_completed"],
        "gauss6_fullva_external": gauss6_summary,
        "gauss6_fullva_public_horizon_single": public_single_summary,
        "gauss6_fullva_public_horizon_single_coarse": public_single_coarse_summary,
        "gauss6_fullva_public_horizon_double_coarse": public_double_coarse_summary,
        "gauss6_fullva_closed_loop_selected_rows_completed": closed_loop_summary["selected_rows_completed"],
        "gauss6_fullva_closed_loop_external": closed_loop_summary,
        "gauss6_fullva_closed_loop_same_window_comparison_completed": comparison_summary["selected_rows_completed"],
        "gauss6_fullva_closed_loop_same_window_comparison": comparison_summary,
        "gauss6_fullva_public_horizon_closed_loop": public_closed_loop_summary,
        "ra2021_public_order_work_summary": order_work_summary,
        "ra2021_public_timing": timing_summary,
        "ra2021_double_pendulum_order": double_order_summary,
        "ra2021_double_pendulum_coarse_order": double_coarse_summary,
        "ra2021_single_pendulum_coarse_order": single_coarse_public_summary,
        "double_pendulum_coarse_same_window_work_precision_summary": double_coarse_work_summary,
        "single_pendulum_coarse_same_window_work_precision_summary": single_coarse_work_summary,
        "gauss6_closed_loop_same_window_work_precision_summary": comparison_work_summary,
        "closed_loop_dynamic_error_floor_audit": closed_loop_floor_audit_summary,
        "closed_loop_coarse_dynamic_order_probe": closed_loop_coarse_probe_summary,
        "closed_loop_true_dynamic_row_feasibility_audit": closed_loop_feasibility_audit_summary,
        "closed_loop_residual_to_error_theorem_obligations": closed_loop_residual_to_error_summary,
        "ra2021_order": ra2021_summary,
        "hi2022_halfimplicit": hi2022_summary,
        "hi2022_halfimplicit_rows_completed": (
            hi2022_summary["selected_step_trio_group_count"]
            == hi2022_summary["selected_step_trio_required_group_count"]
        ),
        "case_inventory_rows": len(run_plan),
        "velocity_partitioning_code_status": VP_CODE_STATUS,
        "velocity_partitioning_code_search": vp_summary,
        "runtime_sec": None,
        "summary_rebuilt_from_existing_csv": True,
    }


def read_or_rebuild_summary() -> dict:
    try:
        summary = read_json(RESULTS / "summary_v048.json")
        floor_audit_json_path = RESULTS / "closed_loop_dynamic_error_floor_audit.json"
        if floor_audit_json_path.exists():
            summary["closed_loop_dynamic_error_floor_audit"] = read_json(floor_audit_json_path)
        coarse_probe_json_path = RESULTS / "closed_loop_coarse_dynamic_order_probe.json"
        if coarse_probe_json_path.exists():
            summary["closed_loop_coarse_dynamic_order_probe"] = read_json(coarse_probe_json_path)
        feasibility_audit_json_path = RESULTS / "closed_loop_true_dynamic_row_feasibility_audit.json"
        if feasibility_audit_json_path.exists():
            summary["closed_loop_true_dynamic_row_feasibility_audit"] = read_json(feasibility_audit_json_path)
        residual_to_error_json_path = RESULTS / "closed_loop_residual_to_error_theorem_obligations.json"
        if residual_to_error_json_path.exists():
            summary["closed_loop_residual_to_error_theorem_obligations"] = read_json(residual_to_error_json_path)
        return summary
    except Exception:
        return rebuild_summary_from_existing_results()


def write_report(summary: dict) -> None:
    ra2021 = summary["ra2021_order"]
    gauss6 = summary["gauss6_fullva_external"]
    gauss6_public_single = summary.get(
        "gauss6_fullva_public_horizon_single",
        {
            "ok_row_count": 0,
            "row_count": 0,
            "selected_rows_completed": False,
            "public_step_size_rows_completed": 0,
            "public_step_size_required_count": len(RA2021_ORDER_STEP_SIZES),
            "public_single_step_trio_completed": False,
            "selected_step_sizes": [],
            "selected_t_end": "nan",
        },
    )
    gauss6_public_double_coarse = summary.get(
        "gauss6_fullva_public_horizon_double_coarse",
        {
            "ok_row_count": 0,
            "row_count": 0,
            "selected_rows_completed": False,
            "public_policy_h_rows_completed": 0,
            "public_policy_h_required_count": len(RA2021_ORDER_STEP_SIZES),
            "public_double_step_trio_completed": False,
            "selected_step_sizes": [],
            "selected_t_end": "nan",
            "pos_observed_order": None,
            "vel_observed_order": None,
        },
    )
    closed_loop = summary.get(
        "gauss6_fullva_closed_loop_external",
        {
            "ok_row_count": 0,
            "row_count": 0,
            "selected_rows_completed": False,
            "selected_models": [],
            "models": {},
        },
    )
    closed_loop_comparison = summary.get(
        "gauss6_fullva_closed_loop_same_window_comparison",
        {
            "ok_row_count": 0,
            "row_count": 0,
            "selected_rows_completed": False,
            "selected_models": [],
            "models": {},
        },
    )
    public_closed_loop = summary.get(
        "gauss6_fullva_public_horizon_closed_loop",
        {
            "ok_row_count": 0,
            "row_count": 0,
            "selected_rows_completed": False,
            "public_step_size_rows_completed": 0,
            "public_step_size_required_count": 2 * len(RA2021_ORDER_STEP_SIZES),
            "public_closed_loop_step_trios_completed": False,
            "selected_models": [],
            "models": {},
        },
    )
    ra2021_work = summary.get("ra2021_public_order_work_summary", {"ok_row_count": 0, "row_count": 0})
    ra2021_timing = summary.get(
        "ra2021_public_timing",
        {
            "ok_row_count": 0,
            "row_count": 0,
            "public_timing_rows_completed": 0,
            "public_timing_required_count": len(RA2021_FORMS) * len(RA2021_TIMING_MODELS),
            "groups": {},
        },
    )
    ra2021_double_order = summary.get(
        "ra2021_double_pendulum_order",
        {
            "ok_row_count": 0,
            "row_count": 0,
            "selected_step_trio_group_count": 0,
            "selected_step_trio_required_group_count": len(RA2021_FORMS),
            "groups": {},
        },
    )
    ra2021_double_coarse = summary.get(
        "ra2021_double_pendulum_coarse_order",
        {
            "ok_row_count": 0,
            "row_count": 0,
            "selected_step_trio_group_count": 0,
            "selected_step_trio_required_group_count": 0,
            "groups": {},
        },
    )
    double_coarse_work = summary.get(
        "double_pendulum_coarse_same_window_work_precision_summary",
        {"ok_row_count": 0, "row_count": 0, "methods": []},
    )
    single_coarse_public = summary.get(
        "ra2021_single_pendulum_coarse_order",
        {"ok_row_count": 0, "row_count": 0, "selected_step_trio_group_count": 0, "selected_step_trio_required_group_count": 0},
    )
    single_coarse_local = summary.get(
        "gauss6_fullva_public_horizon_single_coarse",
        {"ok_row_count": 0, "row_count": 0, "position_observed_order": None, "velocity_observed_order": None},
    )
    single_coarse_work = summary.get(
        "single_pendulum_coarse_same_window_work_precision_summary",
        {"ok_row_count": 0, "row_count": 0, "methods": []},
    )
    same_window_work = summary.get(
        "gauss6_closed_loop_same_window_work_precision_summary",
        {"ok_row_count": 0, "row_count": 0, "models": [], "methods": []},
    )
    closed_loop_surrogate = (
        read_json(RESULTS / "closed_loop_surrogate_dynamic_gate.json")
        if (RESULTS / "closed_loop_surrogate_dynamic_gate.json").exists()
        else {
            "row_count": 0,
            "surrogate_available_count": 0,
            "accepted_dynamic_order_count": 0,
            "dynamic_superiority_claim": False,
        }
    )
    closed_loop_floor_audit = (
        read_json(RESULTS / "closed_loop_dynamic_error_floor_audit.json")
        if (RESULTS / "closed_loop_dynamic_error_floor_audit.json").exists()
        else {
            "row_count": 0,
            "velocity_acceleration_evidence_count": 0,
            "position_floor_blocker_count": 0,
            "accepted_dynamic_order_count": 0,
            "external_superiority_claim": False,
        }
    )
    closed_loop_coarse_probe = (
        read_json(RESULTS / "closed_loop_coarse_dynamic_order_probe.json")
        if (RESULTS / "closed_loop_coarse_dynamic_order_probe.json").exists()
        else {
            "row_count": 0,
            "ok_row_count": 0,
            "failed_row_count": 0,
            "public_failed_row_count": 0,
            "local_velocity_evidence_rows": 0,
            "local_acceleration_evidence_rows": 0,
            "local_position_floor_rows": 0,
            "accepted_dynamic_order_count": 0,
            "external_superiority_claim": False,
        }
    )
    closed_loop_feasibility_audit = (
        read_json(RESULTS / "closed_loop_true_dynamic_row_feasibility_audit.json")
        if (RESULTS / "closed_loop_true_dynamic_row_feasibility_audit.json").exists()
        else {
            "true_dynamic_local_rows_available": 0,
            "accepted_dynamic_order_count": 0,
            "current_local_row_kind": "kinematic_fullva_plus_reaction_reconstruction",
        }
    )
    closed_loop_residual_to_error = (
        read_json(RESULTS / "closed_loop_residual_to_error_theorem_obligations.json")
        if (RESULTS / "closed_loop_residual_to_error_theorem_obligations.json").exists()
        else {
            "obligation_count": 0,
            "blocking_obligation_count": 0,
            "accepted_residual_to_error_theorem": False,
            "accepted_dynamic_order_count": 0,
        }
    )
    hi2022 = summary["hi2022_halfimplicit"]
    vp_search = summary["velocity_partitioning_code_search"]
    lines = [
        "# v048 Experiment Report",
        "",
        "Generated by `run_v048.py`.",
        "",
        "## Purpose",
        "",
        "Current external-comparison execution scaffold for CMAME same-test evidence.",
        "This version creates the executable cross-paper same-test benchmark layer.",
        "It is not a new integrator version and it does not claim that the external",
        "same-test campaign has passed.",
        "",
        "## Current Status",
        "",
        f"- Same-test campaign status: `{summary['same_test_campaign_status']}`.",
        f"- Run mode: `{summary['run_mode']}`.",
        f"- 2021 rA/rp/reps full order policy completed: `{ra2021['full_ra2021_order_completed']}`.",
        f"- 2021 public step-size trio groups completed: `{ra2021['public_step_trio_group_count']}/{ra2021['public_step_trio_required_group_count']}`.",
        f"- 2021 selected rows: `{ra2021['ok_row_count']}/{ra2021['row_count']}` ok, `{ra2021['planned_row_count']}` planned.",
        f"- 2021 selected forms: `{', '.join(ra2021['selected_forms'])}`.",
        f"- 2021 selected models: `{', '.join(ra2021['selected_models'])}`.",
        f"- 2021 selected groups: `{', '.join(ra2021['selected_groups'])}`.",
        f"- 2021 selected step sizes: `{', '.join(str(h) for h in ra2021['selected_step_sizes'])}`.",
        f"- 2021 public order/work summary rows: `{ra2021_work['ok_row_count']}/{ra2021_work['row_count']}`.",
        f"- 2021 double-pendulum dynamic order rows: `{ra2021_double_order['ok_row_count']}/{ra2021_double_order['row_count']}` ok.",
        f"- 2021 double-pendulum dynamic order groups completed: `{ra2021_double_order['selected_step_trio_group_count']}/{ra2021_double_order['selected_step_trio_required_group_count']}`.",
        f"- 2021 double-pendulum coarse same-window public rows: `{ra2021_double_coarse['ok_row_count']}/{ra2021_double_coarse['row_count']}` ok.",
        f"- 2021 double-pendulum coarse same-window groups completed: `{ra2021_double_coarse['selected_step_trio_group_count']}/{ra2021_double_coarse['selected_step_trio_required_group_count']}`.",
        f"- Double-pendulum coarse same-window work/precision summary rows: `{double_coarse_work['ok_row_count']}/{double_coarse_work['row_count']}`.",
        f"- 2021 single-pendulum coarse same-window public rows: `{single_coarse_public['ok_row_count']}/{single_coarse_public['row_count']}` ok.",
        f"- Gauss6/FullVA single-pendulum coarse rows: `{single_coarse_local['ok_row_count']}/{single_coarse_local['row_count']}` ok.",
        f"- Single-pendulum coarse same-window work/precision summary rows: `{single_coarse_work['ok_row_count']}/{single_coarse_work['row_count']}`.",
        f"- 2021 public timing rows: `{ra2021_timing['ok_row_count']}/{ra2021_timing['row_count']}` ok.",
        f"- 2021 public timing policy rows completed: `{ra2021_timing['public_timing_rows_completed']}/{ra2021_timing['public_timing_required_count']}`.",
        f"- Gauss6/FullVA selected external rows: `{gauss6['ok_row_count']}/{gauss6['row_count']}` ok.",
        f"- Gauss6/FullVA selected rows completed: `{gauss6['selected_rows_completed']}`.",
        f"- Gauss6/FullVA public-horizon single rows: `{gauss6_public_single['ok_row_count']}/{gauss6_public_single['row_count']}` ok.",
        f"- Gauss6/FullVA public-horizon single public h rows completed: `{gauss6_public_single['public_step_size_rows_completed']}/{gauss6_public_single['public_step_size_required_count']}`.",
        f"- Gauss6/FullVA public-horizon single step trio completed: `{gauss6_public_single['public_single_step_trio_completed']}`.",
        f"- Gauss6/FullVA public-horizon double coarse rows: `{gauss6_public_double_coarse['ok_row_count']}/{gauss6_public_double_coarse['row_count']}` ok.",
        f"- Gauss6/FullVA public-horizon double coarse public h rows completed: `{gauss6_public_double_coarse['public_policy_h_rows_completed']}/{gauss6_public_double_coarse['public_policy_h_required_count']}`.",
        f"- Gauss6/FullVA public-horizon double coarse step trio completed: `{gauss6_public_double_coarse['public_double_step_trio_completed']}`.",
        f"- Gauss6/FullVA closed-loop external rows: `{closed_loop['ok_row_count']}/{closed_loop['row_count']}` ok.",
        f"- Gauss6/FullVA closed-loop selected rows completed: `{closed_loop['selected_rows_completed']}`.",
        f"- Gauss6/FullVA closed-loop selected models: `{', '.join(closed_loop.get('selected_models', []))}`.",
        f"- Closed-loop same-window comparison rows: `{closed_loop_comparison['ok_row_count']}/{closed_loop_comparison['row_count']}` ok.",
        f"- Closed-loop same-window comparison completed: `{closed_loop_comparison['selected_rows_completed']}`.",
        f"- Closed-loop same-window work/precision summary rows: `{same_window_work['ok_row_count']}/{same_window_work['row_count']}`.",
        f"- Closed-loop surrogate dynamic gate rows: `{closed_loop_surrogate['surrogate_available_count']}/{closed_loop_surrogate['row_count']}` available.",
        f"- Closed-loop accepted dynamic order rows: `{closed_loop_surrogate['accepted_dynamic_order_count']}`.",
        f"- Closed-loop dynamic error floor audit rows: `{closed_loop_floor_audit['velocity_acceleration_evidence_count']}/{closed_loop_floor_audit['row_count']}` velocity/acceleration evidence, `{closed_loop_floor_audit['position_floor_blocker_count']}` position-floor blockers.",
        f"- Closed-loop floor-audit accepted dynamic order rows: `{closed_loop_floor_audit['accepted_dynamic_order_count']}`.",
        f"- Closed-loop coarse dynamic-order probe rows: `{closed_loop_coarse_probe['ok_row_count']}/{closed_loop_coarse_probe['row_count']}` ok, `{closed_loop_coarse_probe['public_failed_row_count']}` public failures.",
        f"- Closed-loop coarse probe local velocity/acceleration evidence rows: `{closed_loop_coarse_probe['local_velocity_evidence_rows']}/{closed_loop_coarse_probe.get('local_method_count', 0)}` and `{closed_loop_coarse_probe['local_acceleration_evidence_rows']}/{closed_loop_coarse_probe.get('local_method_count', 0)}`.",
        f"- Closed-loop coarse probe accepted dynamic order rows: `{closed_loop_coarse_probe['accepted_dynamic_order_count']}`.",
        f"- Closed-loop true dynamic-row feasibility audit true local rows: `{closed_loop_feasibility_audit['true_dynamic_local_rows_available']}`.",
        f"- Closed-loop true dynamic-row feasibility audit accepted dynamic order rows: `{closed_loop_feasibility_audit['accepted_dynamic_order_count']}`.",
        f"- Closed-loop true dynamic-row feasibility audit local row kind: `{closed_loop_feasibility_audit['current_local_row_kind']}`.",
        f"- Closed-loop residual-to-error theorem obligations: `{closed_loop_residual_to_error['blocking_obligation_count']}/{closed_loop_residual_to_error['obligation_count']}` blocking.",
        f"- Closed-loop residual-to-error theorem accepted: `{closed_loop_residual_to_error['accepted_residual_to_error_theorem']}`.",
        f"- Closed-loop residual-to-error route accepted dynamic order rows: `{closed_loop_residual_to_error['accepted_dynamic_order_count']}`.",
        f"- Gauss6/FullVA public-horizon closed-loop rows: `{public_closed_loop['ok_row_count']}/{public_closed_loop['row_count']}` ok.",
        f"- Gauss6/FullVA public-horizon closed-loop public h rows completed: `{public_closed_loop['public_step_size_rows_completed']}/{public_closed_loop['public_step_size_required_count']}`.",
        f"- Gauss6/FullVA public-horizon closed-loop step trios completed: `{public_closed_loop['public_closed_loop_step_trios_completed']}`.",
        f"- Gauss6/FullVA full external campaign completed: `{gauss6['full_external_campaign_completed']}`.",
        f"- 2022 half-implicit selected rows: `{hi2022['ok_row_count']}/{hi2022['row_count']}` ok, `{hi2022['planned_row_count']}` planned.",
        f"- 2022 half-implicit selected groups completed: `{hi2022['selected_step_trio_group_count']}/{hi2022['selected_step_trio_required_group_count']}`.",
        f"- 2022 half-implicit selected models: `{', '.join(hi2022.get('selected_models', []))}`.",
        f"- 2022 half-implicit full campaign completed: `{hi2022['full_hi2022_campaign_completed']}`.",
        f"- Velocity-partitioning code status: `{summary['velocity_partitioning_code_status']}`.",
        f"- Velocity-partitioning code-search rows: `{vp_search['row_count']}`.",
        f"- Velocity-partitioning searched refs: `{', '.join(vp_search.get('searched_refs', []))}`.",
        f"- Velocity-partitioning public web search status: `{vp_search.get('public_web_search_status', 'not_recorded')}`.",
        "",
        "## 2021 Public-Code Group Orders",
        "",
        "| Group | Position order | Velocity order | Acceleration order | Reference status | Public trio |",
        "|---|---:|---:|---:|---|---|",
    ]
    for group, group_summary in sorted(ra2021["groups"].items()):
        pos_order = group_summary["pos_final_linf_order"]
        vel_order = group_summary["vel_final_linf_order"]
        acc_order = group_summary["acc_final_linf_order"]
        lines.append(
            "| "
            f"`{group}` | "
            f"{'nan' if pos_order is None else f'{pos_order:.3f}'} | "
            f"{'nan' if vel_order is None else f'{vel_order:.3f}'} | "
            f"{'nan' if acc_order is None else f'{acc_order:.3f}'} | "
            f"`{group_summary.get('reference_status', 'unknown')}` | "
            f"`{group_summary['public_step_trio_completed']}` |"
        )
    ra_work_rows = read_csv_rows(RESULTS / "ra2021_public_order_work_summary.csv") if (RESULTS / "ra2021_public_order_work_summary.csv").exists() else []
    lines.extend(
        [
            "",
            "## 2021 Public Order/Work Summary",
            "",
            "| Form | Model | Pos. order | Vel. order | Acc. order | Runtime at h=1e-3 | Avg. iterations at h=1e-3 |",
            "|---|---|---:|---:|---:|---:|---:|",
        ]
    )
    for row in ra_work_rows:
        lines.append(
            "| "
            f"`{row['form']}` | "
            f"`{row['model']}` | "
            f"{float(row['pos_final_linf_order']):.3f} | "
            f"{float(row['vel_final_linf_order']):.3f} | "
            f"{float(row['acc_final_linf_order']):.3f} | "
            f"{float(row['runtime_sec_at_reference_h']):.3e} | "
            f"{float(row['avg_iterations_at_reference_h']):.3f} |"
        )
    double_order_rows = read_csv_rows_if_exists(RESULTS / "ra2021_double_pendulum_order_rows.csv")
    if double_order_rows:
        lines.extend(
            [
                "",
                "## 2021 Double-Pendulum Dynamic Self-Reference Order Rows",
                "",
                "| Form | h | Reference h | Position error | Velocity error | Acceleration error | Runtime | Status |",
                "|---|---:|---:|---:|---:|---:|---:|---|",
            ]
        )
        for row in sorted(double_order_rows, key=lambda item: (item.get("form", ""), as_float(item, "h"))):
            lines.append(
                "| "
                f"`{row.get('form', '')}` | "
                f"{as_float(row, 'h'):.3e} | "
                f"{as_float(row, 'reference_h'):.3e} | "
                f"{as_float(row, 'pos_final_linf'):.3e} | "
                f"{as_float(row, 'vel_final_linf'):.3e} | "
                f"{as_float(row, 'acc_final_linf'):.3e} | "
                f"{as_float(row, 'runtime_sec'):.3e} | "
                f"`{row.get('status', '')}` |"
            )
        lines.extend(
            [
                "",
                "| Group | Position order | Velocity order | Acceleration order | Completed |",
                "|---|---:|---:|---:|---|",
            ]
        )
        for group, group_summary in sorted(ra2021_double_order.get("groups", {}).items()):
            pos_order = group_summary.get("pos_final_linf_order")
            vel_order = group_summary.get("vel_final_linf_order")
            acc_order = group_summary.get("acc_final_linf_order")
            lines.append(
                "| "
                f"`{group}` | "
                f"{'nan' if pos_order is None else f'{pos_order:.3f}'} | "
                f"{'nan' if vel_order is None else f'{vel_order:.3f}'} | "
                f"{'nan' if acc_order is None else f'{acc_order:.3f}'} | "
                f"`{group_summary.get('selected_step_trio_completed', False)}` |"
            )
    double_coarse_rows = read_csv_rows_if_exists(RESULTS / "ra2021_double_pendulum_coarse_order_rows.csv")
    if double_coarse_rows:
        lines.extend(
            [
                "",
                "## 2021 Double-Pendulum Coarse Same-Window Public Rows",
                "",
                "| Form | h | Reference h | Position error | Velocity error | Acceleration error | Runtime | Status |",
                "|---|---:|---:|---:|---:|---:|---:|---|",
            ]
        )
        for row in sorted(double_coarse_rows, key=lambda item: (item.get("form", ""), as_float(item, "h"))):
            lines.append(
                "| "
                f"`{row.get('form', '')}` | "
                f"{as_float(row, 'h'):.3e} | "
                f"{as_float(row, 'reference_h'):.3e} | "
                f"{as_float(row, 'pos_final_linf'):.3e} | "
                f"{as_float(row, 'vel_final_linf'):.3e} | "
                f"{as_float(row, 'acc_final_linf'):.3e} | "
                f"{as_float(row, 'runtime_sec'):.3e} | "
                f"`{row.get('status', '')}` |"
            )
        lines.extend(
            [
                "",
                "| Group | Position order | Velocity order | Acceleration order | Completed |",
                "|---|---:|---:|---:|---|",
            ]
        )
        for group, group_summary in sorted(ra2021_double_coarse.get("groups", {}).items()):
            pos_order = group_summary.get("pos_final_linf_order")
            vel_order = group_summary.get("vel_final_linf_order")
            acc_order = group_summary.get("acc_final_linf_order")
            lines.append(
                "| "
                f"`{group}` | "
                f"{'nan' if pos_order is None else f'{pos_order:.3f}'} | "
                f"{'nan' if vel_order is None else f'{vel_order:.3f}'} | "
                f"{'nan' if acc_order is None else f'{acc_order:.3f}'} | "
                f"`{group_summary.get('selected_step_trio_completed', False)}` |"
            )

    double_coarse_work_rows = read_csv_rows_if_exists(
        RESULTS / "double_pendulum_coarse_same_window_work_precision_summary.csv"
    )
    if double_coarse_work_rows:
        lines.extend(
            [
                "",
                "## Double-Pendulum Coarse Same-Window Work/Precision Summary",
                "",
                "| Method | Finest h | Pos. order | Vel. order | Pos. error | Vel. error | Runtime | Runtime ratio vs rA |",
                "|---|---:|---:|---:|---:|---:|---:|---:|",
            ]
        )
        for row in double_coarse_work_rows:
            lines.append(
                "| "
                f"`{row['method']}` | "
                f"{float(row['finest_h']):.3e} | "
                f"{float(row['pos_observed_order']):.3f} | "
                f"{float(row['vel_observed_order']):.3f} | "
                f"{float(row['finest_pos_error']):.3e} | "
                f"{float(row['finest_vel_error']):.3e} | "
                f"{float(row['finest_runtime_sec']):.3e} | "
                f"{float(row['finest_runtime_ratio_vs_rA']):.3f} |"
            )
    single_coarse_work_rows = read_csv_rows_if_exists(
        RESULTS / "single_pendulum_coarse_same_window_work_precision_summary.csv"
    )
    if single_coarse_work_rows:
        lines.extend(
            [
                "",
                "## Single-Pendulum Coarse Same-Window Work/Precision Summary",
                "",
                "| Method | Finest h | Pos. order | Vel. order | Pos. error | Vel. error | Runtime | Runtime ratio vs rA |",
                "|---|---:|---:|---:|---:|---:|---:|---:|",
            ]
        )
        for row in single_coarse_work_rows:
            lines.append(
                "| "
                f"`{row['method']}` | "
                f"{float(row['finest_h']):.3e} | "
                f"{float(row['pos_observed_order']):.3f} | "
                f"{float(row['vel_observed_order']):.3f} | "
                f"{float(row['finest_pos_error']):.3e} | "
                f"{float(row['finest_vel_error']):.3e} | "
                f"{float(row['finest_runtime_sec']):.3e} | "
                f"{float(row['finest_runtime_ratio_vs_rA']):.3f} |"
            )
    timing_rows = read_csv_rows_if_exists(RESULTS / "ra2021_public_timing_rows.csv")
    if timing_rows:
        lines.extend(
            [
                "",
                "## 2021 Public Timing/Iteration Rows",
                "",
                "| Form | Model | Mode | Runtime | Avg. iterations | Max iterations |",
                "|---|---|---|---:|---:|---:|",
            ]
        )
        for row in sorted(timing_rows, key=lambda item: (item.get("form", ""), item.get("model", ""))):
            lines.append(
                "| "
                f"`{row.get('form', '')}` | "
                f"`{row.get('model', '')}` | "
                f"`{row.get('mode', '')}` | "
                f"{as_float(row, 'runtime_sec'):.3e} | "
                f"{as_float(row, 'avg_iterations'):.3f} | "
                f"{as_float(row, 'max_iterations'):.0f} |"
            )
    lines.extend(
        [
            "",
            "## 2022 Half-Implicit Group Orders",
            "",
            "| Group | Position order | Velocity order | Acceleration order | Reference status | Selected trio |",
            "|---|---:|---:|---:|---|---|",
        ]
    )
    for group, group_summary in sorted(hi2022["groups"].items()):
        pos_order = group_summary["pos_final_linf_order"]
        vel_order = group_summary["vel_final_linf_order"]
        acc_order = group_summary["acc_final_linf_order"]
        lines.append(
            "| "
            f"`{group}` | "
            f"{'nan' if pos_order is None else f'{pos_order:.3f}'} | "
            f"{'nan' if vel_order is None else f'{vel_order:.3f}'} | "
            f"{'nan' if acc_order is None else f'{acc_order:.3f}'} | "
            f"`{group_summary.get('reference_status', 'unknown')}` | "
            f"`{group_summary['selected_step_trio_completed']}` |"
        )
    public_single_rows = (
        read_csv_rows(RESULTS / "gauss6_fullva_public_horizon_single_rows.csv")
        if (RESULTS / "gauss6_fullva_public_horizon_single_rows.csv").exists()
        else []
    )
    lines.extend(
        [
            "",
            "## Gauss6/FullVA Public-Horizon Single-Pendulum Tranche",
            "",
            "| h | Status | Public h | Steps | Position error | Velocity error | Runtime | Newton iterations |",
            "|---:|---|---|---:|---:|---:|---:|---:|",
        ]
    )
    for row in public_single_rows:
        runtime = as_float(row, "runtime_sec")
        lines.append(
            "| "
            f"{float(row['h']):.3e} | "
            f"`{row['status']}` | "
            f"`{row['public_policy_h']}` | "
            f"{row['steps']} | "
            f"{as_float(row, 'position_l2_error'):.3e} | "
            f"{as_float(row, 'velocity_l2_error'):.3e} | "
            f"{runtime:.3e} | "
            f"{row['total_newton_iterations']} |"
        )
    public_double_coarse_rows = read_csv_rows_if_exists(
        RESULTS / "gauss6_fullva_public_horizon_double_coarse_rows.csv"
    )
    if public_double_coarse_rows:
        lines.extend(
            [
                "",
                "## Gauss6/FullVA Public-Horizon Double-Pendulum Coarse Tranche",
                "",
                "| h | Status | Public h | Steps | Position trajectory error | Velocity trajectory error | Runtime | Newton iterations |",
                "|---:|---|---|---:|---:|---:|---:|---:|",
            ]
        )
        for row in public_double_coarse_rows:
            lines.append(
                "| "
                f"{as_float(row, 'h'):.3e} | "
                f"`{row.get('status', '')}` | "
                f"`{row.get('public_policy_h', '')}` | "
                f"{row.get('steps', '')} | "
                f"{as_float(row, 'pos_traj_linf'):.3e} | "
                f"{as_float(row, 'vel_traj_linf'):.3e} | "
                f"{as_float(row, 'runtime_sec'):.3e} | "
                f"{row.get('total_newton_iterations', '')} |"
            )
    lines.extend(
        [
            "",
            "## Gauss6/FullVA Closed-Loop External Rows",
            "",
            "| Model | Rows | Max dynamics residual | Max constraint residual | Max SO(3) residual | Status |",
            "|---|---:|---:|---:|---:|---|",
        ]
    )
    for model, model_summary in sorted(closed_loop.get("models", {}).items()):
        max_constraint = max(
            float(model_summary.get("max_position_constraint_norm") or 0.0),
            float(model_summary.get("max_velocity_constraint_norm") or 0.0),
            float(model_summary.get("max_acceleration_constraint_norm") or 0.0),
        )
        lines.append(
            "| "
            f"`{model}` | "
            f"{model_summary.get('ok_row_count', 0)}/{model_summary.get('row_count', 0)} | "
            f"{float(model_summary.get('max_dynamics_residual_norm') or 0.0):.3e} | "
            f"{max_constraint:.3e} | "
            f"{float(model_summary.get('max_so3_fro') or 0.0):.3e} | "
            f"`{model_summary.get('status', 'unknown')}` |"
        )
    public_closed_loop_rows = (
        read_csv_rows(RESULTS / "gauss6_fullva_public_horizon_closed_loop_rows.csv")
        if (RESULTS / "gauss6_fullva_public_horizon_closed_loop_rows.csv").exists()
        else []
    )
    lines.extend(
        [
            "",
            "## Gauss6/FullVA Public-Horizon Closed-Loop Tranche",
            "",
            "| Model | h | Status | Public h | Steps | Position trajectory error | Velocity trajectory error | Max dynamics residual | Runtime |",
            "|---|---:|---|---|---:|---:|---:|---:|---:|",
        ]
    )
    for row in public_closed_loop_rows:
        lines.append(
            "| "
            f"`{row['model']}` | "
            f"{float(row['h']):.3e} | "
            f"`{row['status']}` | "
            f"`{row['public_policy_h']}` | "
            f"{row['steps']} | "
            f"{as_float(row, 'pos_traj_linf'):.3e} | "
            f"{as_float(row, 'vel_traj_linf'):.3e} | "
            f"{as_float(row, 'max_dynamics_residual_norm'):.3e} | "
            f"{as_float(row, 'runtime_sec'):.3e} |"
        )
    lines.extend(
        [
            "",
            "## Selected Closed-Loop Same-Window Comparison",
            "",
            "| Model | Method | Rows | Position order | Velocity order | Acceleration order |",
            "|---|---|---:|---:|---:|---:|",
        ]
    )
    for model, model_summary in sorted(closed_loop_comparison.get("models", {}).items()):
        for method, method_summary in sorted(model_summary.get("methods", {}).items()):
            pos_order = method_summary.get("pos_observed_order")
            vel_order = method_summary.get("vel_observed_order")
            acc_order = method_summary.get("acc_observed_order")
            lines.append(
                "| "
                f"`{model}` | "
                f"`{method}` | "
                f"{method_summary.get('ok_row_count', 0)}/{method_summary.get('row_count', 0)} | "
                f"{'nan' if pos_order is None else f'{float(pos_order):.3f}'} | "
                f"{'nan' if vel_order is None else f'{float(vel_order):.3f}'} | "
                f"{'nan' if acc_order is None else f'{float(acc_order):.3f}'} |"
            )
    same_window_work_rows = (
        read_csv_rows(RESULTS / "gauss6_closed_loop_same_window_work_precision_summary.csv")
        if (RESULTS / "gauss6_closed_loop_same_window_work_precision_summary.csv").exists()
        else []
    )
    lines.extend(
        [
            "",
            "## Selected Same-Window Work/Precision Summary",
            "",
            "| Model | Method | Finest h | Pos. error | Vel. error | Acc. error | Runtime | Runtime ratio vs rA |",
            "|---|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in same_window_work_rows:
        lines.append(
            "| "
            f"`{row['model']}` | "
            f"`{row['method']}` | "
            f"{float(row['finest_h']):.3e} | "
            f"{float(row['finest_pos_final_linf']):.3e} | "
            f"{float(row['finest_vel_final_linf']):.3e} | "
            f"{float(row['finest_acc_final_linf']):.3e} | "
            f"{float(row['finest_runtime_sec']):.3e} | "
            f"{float(row['finest_runtime_ratio_vs_rA']):.3f} |"
        )
    closed_loop_surrogate_rows = read_csv_rows_if_exists(RESULTS / "closed_loop_surrogate_dynamic_gate.csv")
    if closed_loop_surrogate_rows:
        lines.extend(
            [
                "",
                "## Closed-Loop Surrogate Dynamic Gate",
                "",
                "| Model | Public velocity order | Local surrogate velocity order | Local velocity-error ratio | Runtime ratio vs rA | Accepted dynamic order |",
                "|---|---:|---:|---:|---:|---|",
            ]
        )
        for row in closed_loop_surrogate_rows:
            lines.append(
                "| "
                f"`{row['model']}` | "
                f"{as_float(row, 'public_vel_order'):.3f} | "
                f"{as_float(row, 'local_surrogate_vel_order'):.3f} | "
                f"{as_float(row, 'local_vel_error_ratio_vs_public'):.3e} | "
                f"{as_float(row, 'local_runtime_ratio_vs_public'):.3f} | "
                "`false` |"
            )
    closed_loop_floor_audit_rows = read_csv_rows_if_exists(RESULTS / "closed_loop_dynamic_error_floor_audit.csv")
    if closed_loop_floor_audit_rows:
        lines.extend(
            [
                "",
                "## Closed-Loop Dynamic Error Floor Audit",
                "",
                "| Model | Public velocity order | Public acceleration order | Local velocity ratio | Local acceleration ratio | Position-floor blocker | Accepted dynamic order |",
                "|---|---:|---:|---:|---:|---|---|",
            ]
        )
        for row in closed_loop_floor_audit_rows:
            lines.append(
                "| "
                f"`{row['model']}` | "
                f"{as_float(row, 'public_vel_order'):.3f} | "
                f"{as_float(row, 'public_acc_order'):.3f} | "
                f"{as_float(row, 'local_vel_error_ratio_vs_public'):.3e} | "
                f"{as_float(row, 'local_acc_error_ratio_vs_public'):.3e} | "
                f"`{row.get('position_floor_blocker', 'True')}` | "
                "`false` |"
            )
    closed_loop_coarse_probe_rows = read_csv_rows_if_exists(
        RESULTS / "closed_loop_coarse_dynamic_order_probe_work_precision_summary.csv"
    )
    if closed_loop_coarse_probe_rows:
        lines.extend(
            [
                "",
                "## Closed-Loop Coarse Dynamic-Order Probe",
                "",
                "| Model | Method | Pos. order | Vel. order | Acc. order | Finest pos ratio | Finest vel ratio | Finest acc ratio | Runtime ratio vs rA | Accepted dynamic order |",
                "|---|---|---:|---:|---:|---:|---:|---:|---:|---|",
            ]
        )
        for row in closed_loop_coarse_probe_rows:
            lines.append(
                "| "
                f"`{row.get('model', '')}` | "
                f"`{row.get('method', '')}` | "
                f"{as_float(row, 'pos_observed_order'):.3f} | "
                f"{as_float(row, 'vel_observed_order'):.3f} | "
                f"{as_float(row, 'acc_observed_order'):.3f} | "
                f"{as_float(row, 'finest_pos_error_ratio_vs_rA'):.3e} | "
                f"{as_float(row, 'finest_vel_error_ratio_vs_rA'):.3e} | "
                f"{as_float(row, 'finest_acc_error_ratio_vs_rA'):.3e} | "
                f"{as_float(row, 'finest_runtime_ratio_vs_rA'):.3f} | "
                "`false` |"
            )
    lines.extend(
        [
            "",
            "## Outputs",
        "",
        "- `cross_paper_run_plan.csv`",
        "- `same_test_workload_estimate.csv`",
        "- `hi2022_workload_estimate.csv`",
        "- `ra2021_order_rows.csv`",
        "- `ra2021_public_order_work_summary.csv`",
        "- `ra2021_double_pendulum_order_rows.csv`",
        "- `ra2021_double_pendulum_coarse_order_rows.csv`",
        "- `double_pendulum_coarse_same_window_work_precision_summary.csv`",
        "- `ra2021_single_pendulum_coarse_order_rows.csv`",
        "- `gauss6_fullva_public_horizon_single_coarse_rows.csv`",
        "- `single_pendulum_coarse_same_window_work_precision_summary.csv`",
        "- `single_pendulum_coarse_same_window_work_precision_summary.json`",
        "- `single_pendulum_coarse_same_window_work_precision_summary.md`",
        "- `ra2021_public_timing_rows.csv`",
        "- `hi2022_halfimplicit_rows.csv`",
        "- `gauss6_fullva_external_rows.csv`",
        "- `gauss6_fullva_public_horizon_single_rows.csv`",
        "- `gauss6_fullva_public_horizon_double_coarse_rows.csv`",
        "- `gauss6_fullva_closed_loop_external_rows.csv`",
        "- `v047_closed_loop_coarse_order_audit.csv`",
        "- `gauss6_fullva_public_horizon_closed_loop_rows.csv`",
        "- `gauss6_fullva_closed_loop_same_window_comparison_rows.csv`",
        "- `gauss6_closed_loop_same_window_work_precision_summary.csv`",
        "- `closed_loop_surrogate_dynamic_gate.csv`",
        "- `closed_loop_surrogate_dynamic_gate.json`",
        "- `closed_loop_surrogate_dynamic_gate.md`",
        "- `closed_loop_dynamic_error_floor_audit.csv`",
        "- `closed_loop_dynamic_error_floor_audit.json`",
        "- `closed_loop_dynamic_error_floor_audit.md`",
        "- `closed_loop_coarse_dynamic_order_probe_rows.csv`",
        "- `closed_loop_coarse_dynamic_order_probe_work_precision_summary.csv`",
        "- `closed_loop_coarse_dynamic_order_probe.json`",
        "- `closed_loop_coarse_dynamic_order_probe.md`",
        "- `coarse_first_external_readiness_gate.csv`",
        "- `coarse_first_external_readiness_gate.json`",
        "- `coarse_first_external_readiness_gate.md`",
        "- `velocity_partitioning_code_search.csv`",
        "- `summary_v048.json`",
        "",
        "## Interpretation",
        "",
        "The 2021 `rA/rp/reps` public-code order policy is now complete for",
        "the three source order-analysis mechanisms. This closes the 2021",
        "public baseline order table, but it does not by itself include a",
        "complete `Gauss6/FullVA` external campaign.",
        "",
        "The 2021 double-pendulum dynamic self-reference order rows fill the",
        "order-first gap left by public `order_analysis.py`, which has no",
        "`double_pendulum` kinematic-reference order case. These rows use the",
        "same public dynamics model and a finer public-dynamics reference; they",
        "must be read separately from the kinematic-reference order rows.",
        "",
        "The 2021 public timing rows are a separate performance/iteration policy",
        "matching `time.py`: `T=3`, `h=1e-3`, dynamics mode, and no explicit",
        "`--tol` so the public dynamics default tolerance is used. They are used to",
        "fill public-code four-example performance coverage, especially",
        "`double_pendulum`, which is absent from the 2021 public order-analysis",
        "script. Timing rows do not replace missing order rows.",
        "",
        "The optional `Gauss6/FullVA` selected rows use the v047 absolute-coordinate",
        "driven FullVA single-pendulum residual on the same 2021 public mechanism",
        "definition. They are a bounded same-mechanism pilot unless the public",
        "time window, public step-size policy, and remaining external suites are",
        "also completed.",
        "",
        "The public-horizon single-pendulum tranche records `Gauss6/FullVA`",
        "rows on the actual 2021 public time window. The current rows complete",
        "the `h=[1e-2,1e-3,1e-4]` single-pendulum public step-size trio, but the",
        "finest position/orientation errors sit near roundoff and the table does",
        "not imply that the multi-mechanism external campaign is complete.",
        "",
        "The public-horizon double-pendulum coarse tranche runs the local",
        "`Gauss6/FullVA` double-revolute self-reference over the same `T=3`",
        "time horizon with `h=[0.1,0.05,0.025]` and reference `h=0.0125`.",
        "It adds executable double-pendulum order/work evidence at larger step",
        "sizes, but it is intentionally not the public `h=[1e-2,1e-3,1e-4]`",
        "policy and does not close the external-superiority gate.",
        "",
        "The double-pendulum coarse same-window public rows run the public",
        "`rA/rp/reps` dynamics on the same `T=3`, `h=[0.1,0.05,0.025]`,",
        "reference `h=0.0125` policy used by the coarse `Gauss6/FullVA` tranche.",
        "They give an order/time baseline at the large steps requested for",
        "diagnosis; they do not replace the source paper's public `1e-4` policy.",
        "",
        "The single-pendulum coarse same-window rows apply the same coarse-first",
        "`T=3`, `h=[0.1,0.05,0.025]`, reference `h=0.0125` policy to the",
        "2021 public single-pendulum model and the local `Gauss6/FullVA`",
        "single-pendulum tranche. They provide lightweight order/time evidence",
        "without launching the source `1e-4` policy; the local position order is",
        "sixth order while velocity-like columns are treated as finite-window",
        "diagnostics because they are close to the reference floor.",
        "The coarse-first external readiness gate records this policy explicitly:",
        "`1e-4` is not a default execution target, only the double-pendulum row",
        "and single-pendulum row currently have coarse same-window order/time evidence, and four-link plus",
        "slider-crank still need dynamic order/work rows rather than residual-only",
        "or selected-window table-shape evidence.",
        "",
        "The optional closed-loop `Gauss6/FullVA` rows use the accepted local",
        "kinematic FullVA solve and reaction reconstruction on the 2021",
        "`four_link` and `slider_crank` mechanisms. They verify public-mechanism",
        "constraint closure and Newton-Euler reaction residuals, but they are",
        "not dynamic order/work rows.",
        "",
        "The public-horizon closed-loop tranche extends those residual checks",
        "to the 2021 public time window and public step sizes when rows are",
        "selected. It is still not the full public dynamic order/work campaign,",
        "because the local rows use kinematic FullVA plus reaction reconstruction",
        "rather than the public `rA/rp/reps` dynamics error policy.",
        "",
        "The v047 closed-loop coarse-order audit repeats the accepted",
        "four-link/slider-crank kinematic FullVA scaffold at larger",
        "`h=[0.1,0.05,0.025]`. The errors remain near double-precision floor,",
        "so the resulting slopes are recorded as a roundoff/sampling diagnostic",
        "rather than a dynamic method-order claim.",
        "",
        "The selected same-window closed-loop comparison puts public `rA` dynamics",
        "and local `Gauss6/FullVA` closed-loop residual rows under the same",
        "`T=0.2`, `h=[0.02,0.01,0.005]`, public-kinematic-reference final-error",
        "columns. This is closer to the paper's error/order/work table shape,",
        "but it remains selected-window evidence rather than the exact public",
        "`T=3`, `h=[1e-2,1e-3,1e-4]` campaign.",
        "The derived order/work summary CSVs are manuscript-table helpers over",
        "already recorded rows; they do not change the external-superiority",
        "claim boundary.",
        "",
        "The closed-loop surrogate dynamic gate promotes the selected-window",
        "four-link and slider-crank residual-to-error table into a two-row",
        "planning artifact: surrogate evidence only. It is useful evidence",
        "that the local residual rows are small against the public `rA` error",
        "scale, but it records zero accepted dynamic order rows and does not",
        "claim superiority.",
        "",
        "The closed-loop coarse dynamic-order probe runs the requested large-step",
        "`T=0.2`, `h=[0.1,0.05,0.025]`, reference `h=0.0125` diagnostic.",
        "It avoids default `1e-4` rows. The current artifact has `11/12` rows",
        "ok, one public `slider_crank`/`rA` failure at `h=0.1`, two local",
        "velocity/acceleration evidence rows, two local position-floor rows,",
        "and zero accepted dynamic-order rows. Large steps therefore did not",
        "remove the four-link/slider-crank dynamic-order blocker.",
        "",
        "The closed-loop true-dynamic-row feasibility audit source-checks that",
        "the current local closed-loop rows call `simulate_v046_local_kinematic_fullva`,",
        "use `setup_system(..., \"kinematics\", ...)`, and reconstruct reaction",
        "multipliers after the kinematic solve. Therefore the existing rows are",
        "coverage/residual evidence, not local dynamic DAE trajectory rows; the",
        "accepted dynamic-order count remains zero until a true dynamic row or a",
        "residual-to-error theorem is added.",
        "",
        "The residual-to-error theorem-obligation gate records seven blocking",
        "conditions before the residual surrogate can be promoted to order",
        "evidence: dynamic residual identity, an `O(h^7)` residual rate, a",
        "closed-loop DAE stability or inf-sup bound, calibrated non-floor-limited",
        "error estimation, reference-floor exclusion, a coarse-first accepted",
        "campaign, and a manuscript theorem/proof. The current status is open.",
        "",
        "The 2022 half-implicit rows are bounded three-step pilots using the",
        "source suite's `rA` and `rA_half` forms. Double-pendulum rows use a",
        "dynamics self-reference, while single/four-link/slider-crank rows use",
        "the suite's `rA` kinematics reference when selected. They do not replace",
        "the source paper's full `T=8` step-size family, saved ground-truth",
        "campaigns, energy comparison, or work metrics.",
        "",
        "The velocity-partitioning code-search artifact records the 2024",
        "public-code claim and the local tree searches over both",
        "`sbel-reproducibility` and `public-metadata`. No distinct",
        "velocity-partitioning code path is resolved, so the placeholder case",
        "must not be converted into benchmark rows yet.",
        "",
        "The CMAME paper must still run `Gauss6/FullVA` against the exact",
        "external public-code tests, complete the 2022 full half-implicit",
        "campaign, reproduce the original TFE paper tests, resolve the",
        "velocity-partitioning code path, and add order/error/work rows before",
        "claiming external-method superiority.",
        "",
        ]
    )
    (RESULTS / "v048_report.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--full-ra2021-order",
        action="store_true",
        help="run the opt-in 2021 rA/rp/reps order-policy rows instead of the short smoke",
    )
    parser.add_argument(
        "--allow-source-policy-1e-4",
        action="store_true",
        help="permit explicit h<=1e-4 source-policy rows; default runs stay coarse-first",
    )
    parser.add_argument(
        "--ra2021-plan-only",
        action="store_true",
        help="write selected 2021 order rows as planned_not_run without executing public code",
    )
    parser.add_argument(
        "--ra2021-forms",
        default=None,
        help="comma-separated subset of forms for a targeted 2021 run, e.g. rA or rA,rp",
    )
    parser.add_argument(
        "--ra2021-models",
        default=None,
        help="comma-separated subset of 2021 order models: single_pendulum,four_link,slider_crank",
    )
    parser.add_argument(
        "--ra2021-groups",
        default=None,
        help="comma-separated explicit 2021 form:model groups, e.g. rA:single_pendulum,rp:single_pendulum,rA:four_link",
    )
    parser.add_argument(
        "--ra2021-step-sizes",
        default=None,
        help="comma-separated step sizes for targeted 2021 runs, e.g. 1e-2,1e-3",
    )
    parser.add_argument(
        "--ra2021-t-end",
        type=float,
        default=None,
        help="override 2021 order horizon for targeted runs",
    )
    parser.add_argument(
        "--ra2021-reference-h",
        type=float,
        default=None,
        help="override 2021 kinematic-reference step for targeted runs",
    )
    parser.add_argument(
        "--gauss6-fullva-single",
        action="store_true",
        help="run selected Gauss6/FullVA rows for the 2021 single-pendulum mechanism",
    )
    parser.add_argument(
        "--ra2021-public-timing",
        action="store_true",
        help="run selected 2021 public timing/iteration rows",
    )
    parser.add_argument(
        "--ra2021-public-timing-plan-only",
        action="store_true",
        help="write selected 2021 public timing/iteration rows as planned_not_run",
    )
    parser.add_argument(
        "--ra2021-timing-forms",
        default="rA,rp,reps",
        help="comma-separated forms for 2021 public timing rows",
    )
    parser.add_argument(
        "--ra2021-timing-models",
        default="single_pendulum,double_pendulum,four_link,slider_crank",
        help="comma-separated 2021 timing models",
    )
    parser.add_argument(
        "--ra2021-timing-mode",
        default="dynamics",
        help="2021 timing mode; use dynamics for the four-example performance ledger",
    )
    parser.add_argument(
        "--ra2021-timing-h",
        type=float,
        default=RA2021_PUBLIC_REFERENCE_H,
        help="2021 timing step size",
    )
    parser.add_argument(
        "--ra2021-timing-t-end",
        type=float,
        default=RA2021_PUBLIC_T_END,
        help="2021 timing horizon",
    )
    parser.add_argument(
        "--ra2021-timing-tol",
        type=float,
        default=None,
        help="2021 timing tolerance; omit to match public time.py default dynamics tolerance",
    )
    parser.add_argument(
        "--ra2021-double-order",
        action="store_true",
        help="run 2021 public double-pendulum dynamic self-reference order rows",
    )
    parser.add_argument(
        "--ra2021-double-order-plan-only",
        action="store_true",
        help="write 2021 double-pendulum dynamic self-reference order rows as planned_not_run",
    )
    parser.add_argument(
        "--ra2021-double-order-forms",
        default="rA,rp,reps",
        help="comma-separated forms for 2021 double-pendulum dynamic order rows",
    )
    parser.add_argument(
        "--ra2021-double-order-step-sizes",
        default=",".join(str(h) for h in RA2021_DOUBLE_ORDER_STEP_SIZES),
        help="comma-separated step sizes for 2021 double-pendulum dynamic order rows",
    )
    parser.add_argument(
        "--ra2021-double-order-reference-h",
        type=float,
        default=RA2021_DOUBLE_ORDER_REFERENCE_H,
        help="finer public-dynamics reference step for 2021 double-pendulum order rows",
    )
    parser.add_argument(
        "--ra2021-double-order-t-end",
        type=float,
        default=RA2021_PUBLIC_T_END,
        help="time horizon for 2021 double-pendulum dynamic order rows",
    )
    parser.add_argument(
        "--ra2021-double-order-tol",
        type=float,
        default=None,
        help="tolerance for 2021 double-pendulum order rows; omit to match public dynamics default",
    )
    parser.add_argument(
        "--gauss6-plan-only",
        action="store_true",
        help="write selected Gauss6/FullVA rows as planned_not_run without importing v047",
    )
    parser.add_argument(
        "--gauss6-step-sizes",
        default="0.2,0.1,0.05",
        help="comma-separated Gauss6/FullVA selected pilot step sizes",
    )
    parser.add_argument(
        "--gauss6-t-end",
        type=float,
        default=0.2,
        help="Gauss6/FullVA selected pilot horizon",
    )
    parser.add_argument(
        "--gauss6-reference-h",
        type=float,
        default=RA2021_PUBLIC_REFERENCE_H,
        help="public kinematic reference step used only for alignment diagnostics",
    )
    parser.add_argument(
        "--gauss6-public-single",
        action="store_true",
        help="run Gauss6/FullVA single-pendulum rows on the 2021 public-code time horizon",
    )
    parser.add_argument(
        "--gauss6-public-plan-only",
        action="store_true",
        help="write public-horizon Gauss6/FullVA single-pendulum rows as planned_not_run",
    )
    parser.add_argument(
        "--gauss6-public-step-sizes",
        default="1e-2",
        help="comma-separated public-horizon Gauss6/FullVA single-pendulum step sizes",
    )
    parser.add_argument(
        "--gauss6-public-t-end",
        type=float,
        default=RA2021_PUBLIC_T_END,
        help="Gauss6/FullVA public-horizon single-pendulum time horizon",
    )
    parser.add_argument(
        "--gauss6-public-reference-h",
        type=float,
        default=RA2021_PUBLIC_REFERENCE_H,
        help="public kinematic reference step used for public-horizon single-pendulum alignment",
    )
    parser.add_argument(
        "--gauss6-closed-loop-2021",
        action="store_true",
        help="run selected Gauss6/FullVA closed-loop rows for the 2021 four_link/slider_crank mechanisms",
    )
    parser.add_argument(
        "--gauss6-closed-loop-plan-only",
        action="store_true",
        help="write selected Gauss6/FullVA closed-loop rows as planned_not_run",
    )
    parser.add_argument(
        "--gauss6-closed-loop-models",
        default="four_link,slider_crank",
        help="comma-separated 2021 closed-loop models for selected Gauss6/FullVA rows",
    )
    parser.add_argument(
        "--gauss6-closed-loop-step-sizes",
        default="0.02,0.01,0.005",
        help="comma-separated closed-loop selected row step sizes",
    )
    parser.add_argument(
        "--gauss6-closed-loop-t-end",
        type=float,
        default=0.2,
        help="closed-loop selected row horizon",
    )
    parser.add_argument(
        "--gauss6-closed-loop-reference-h",
        type=float,
        default=0.001,
        help="closed-loop nested reference step",
    )
    parser.add_argument(
        "--gauss6-public-closed-loop-2021",
        action="store_true",
        help="run public-horizon Gauss6/FullVA closed-loop rows for the 2021 four_link/slider_crank mechanisms",
    )
    parser.add_argument(
        "--gauss6-public-closed-loop-plan-only",
        action="store_true",
        help="write public-horizon Gauss6/FullVA closed-loop rows as planned_not_run",
    )
    parser.add_argument(
        "--gauss6-public-closed-loop-models",
        default="four_link,slider_crank",
        help="comma-separated 2021 closed-loop models for public-horizon Gauss6/FullVA rows",
    )
    parser.add_argument(
        "--gauss6-public-closed-loop-step-sizes",
        default="1e-2",
        help="comma-separated public-horizon closed-loop row step sizes",
    )
    parser.add_argument(
        "--gauss6-public-closed-loop-t-end",
        type=float,
        default=RA2021_PUBLIC_T_END,
        help="public-horizon closed-loop row horizon",
    )
    parser.add_argument(
        "--gauss6-public-closed-loop-reference-h",
        type=float,
        default=RA2021_PUBLIC_REFERENCE_H,
        help="public-horizon closed-loop nested reference step",
    )
    parser.add_argument(
        "--reuse-existing-results",
        action="store_true",
        help="reuse existing v048 result tables and only add newly selected optional rows",
    )
    parser.add_argument(
        "--hi2022-double-pendulum",
        action="store_true",
        help="run selected 2022 half-implicit rows; kept for compatibility with the original double-pendulum pilot",
    )
    parser.add_argument(
        "--hi2022-plan-only",
        action="store_true",
        help="write selected 2022 half-implicit rows as planned_not_run",
    )
    parser.add_argument(
        "--hi2022-forms",
        default="rA,rA_half",
        help="comma-separated 2022 forms for the selected pilot: rA,rA_half",
    )
    parser.add_argument(
        "--hi2022-models",
        default="double_pendulum",
        help="comma-separated 2022 models for the selected pilot: single_pendulum,double_pendulum,four_link,slider_crank",
    )
    parser.add_argument(
        "--hi2022-step-sizes",
        default="0.02,0.01,0.005",
        help="comma-separated 2022 half-implicit selected pilot step sizes",
    )
    parser.add_argument(
        "--hi2022-t-end",
        type=float,
        default=0.1,
        help="2022 half-implicit selected pilot horizon",
    )
    parser.add_argument(
        "--hi2022-reference-h",
        type=float,
        default=HI2022_REFERENCE_H,
        help="2022 half-implicit selected in-suite rA reference step",
    )
    args = parser.parse_args()

    RESULTS.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()

    closed_loop_config = Gauss6ClosedLoopConfig(
        policy="gauss6_fullva_selected_closed_loop_kinematic_reaction_not_full_campaign",
        run_mode="gauss6_fullva_closed_loop_2021_pilot",
        models=select_gauss6_closed_loop_models(args.gauss6_closed_loop_models),
        step_sizes=parse_float_csv(args.gauss6_closed_loop_step_sizes),
        reference_h=float(args.gauss6_closed_loop_reference_h),
        t_end=float(args.gauss6_closed_loop_t_end),
        run_model=bool(args.gauss6_closed_loop_2021 and not args.gauss6_closed_loop_plan_only),
    )
    gauss6_public_single_config = Gauss6PublicSingleConfig(
        policy="gauss6_fullva_public_horizon_single_pendulum_tranche_not_full_campaign",
        run_mode="gauss6_fullva_public_horizon_single_pendulum",
        step_sizes=parse_float_csv(args.gauss6_public_step_sizes),
        reference_h=float(args.gauss6_public_reference_h),
        t_end=float(args.gauss6_public_t_end),
        run_model=bool(args.gauss6_public_single and not args.gauss6_public_plan_only),
    )
    public_closed_loop_config = Gauss6ClosedLoopConfig(
        policy="gauss6_fullva_public_horizon_closed_loop_kinematic_reaction_not_full_campaign",
        run_mode="gauss6_fullva_public_horizon_closed_loop_2021_tranche",
        models=select_gauss6_closed_loop_models(args.gauss6_public_closed_loop_models),
        step_sizes=parse_float_csv(args.gauss6_public_closed_loop_step_sizes),
        reference_h=float(args.gauss6_public_closed_loop_reference_h),
        t_end=float(args.gauss6_public_closed_loop_t_end),
        run_model=bool(args.gauss6_public_closed_loop_2021 and not args.gauss6_public_closed_loop_plan_only),
    )
    timing_forms = select_forms(args.ra2021_timing_forms)
    timing_models = select_timing_models(args.ra2021_timing_models)
    timing_config = RA2021TimingConfig(
        policy="ra2021_public_timing_iteration_policy_not_order_rows",
        run_mode="ra2021_public_timing_iteration",
        forms=timing_forms,
        models=timing_models,
        groups=cartesian_groups(timing_forms, timing_models),
        h=float(args.ra2021_timing_h),
        t_end=float(args.ra2021_timing_t_end),
        tolerance=None if args.ra2021_timing_tol is None else float(args.ra2021_timing_tol),
        mode=str(args.ra2021_timing_mode),
        run_public_code=bool(args.ra2021_public_timing and not args.ra2021_public_timing_plan_only),
        full_ra2021_timing_completed=bool(
            args.ra2021_public_timing
            and not args.ra2021_public_timing_plan_only
            and set(timing_forms) == set(RA2021_FORMS)
            and {model.name for model in timing_models} == {model.name for model in RA2021_TIMING_MODELS}
        ),
    )
    double_order_forms = select_forms(args.ra2021_double_order_forms)
    double_order_step_sizes = parse_float_csv(args.ra2021_double_order_step_sizes)
    double_order_config = RA2021DoubleOrderConfig(
        policy="ra2021_double_pendulum_dynamic_self_reference_order_policy",
        run_mode="ra2021_double_pendulum_dynamic_self_reference_order",
        forms=double_order_forms,
        step_sizes=double_order_step_sizes,
        reference_h=float(args.ra2021_double_order_reference_h),
        t_end=float(args.ra2021_double_order_t_end),
        tolerance=None if args.ra2021_double_order_tol is None else float(args.ra2021_double_order_tol),
        run_public_code=bool(args.ra2021_double_order and not args.ra2021_double_order_plan_only),
        full_ra2021_double_order_completed=bool(
            args.ra2021_double_order
            and not args.ra2021_double_order_plan_only
            and set(double_order_forms) == set(RA2021_FORMS)
            and list(double_order_step_sizes) == RA2021_DOUBLE_ORDER_STEP_SIZES
            and np.isclose(float(args.ra2021_double_order_reference_h), RA2021_DOUBLE_ORDER_REFERENCE_H)
            and np.isclose(float(args.ra2021_double_order_t_end), RA2021_PUBLIC_T_END)
            and args.ra2021_double_order_tol is None
        ),
    )
    hi2022_config = HI2022Config(
        policy="hi2022_bounded_four_example_pilot_not_full_campaign",
        run_mode="hi2022_bounded_four_example_pilot",
        forms=select_hi2022_forms(args.hi2022_forms),
        models=select_hi2022_models(args.hi2022_models),
        step_sizes=parse_float_csv(args.hi2022_step_sizes),
        reference_h=float(args.hi2022_reference_h),
        t_end=float(args.hi2022_t_end),
        tolerance_base=HI2022_TOLERANCE_BASE,
        run_public_code=bool(args.hi2022_double_pendulum and not args.hi2022_plan_only),
        full_hi2022_campaign_completed=False,
    )
    targeted = any(
        value is not None
        for value in (
            args.ra2021_forms,
            args.ra2021_models,
            args.ra2021_groups,
            args.ra2021_step_sizes,
            args.ra2021_t_end,
            args.ra2021_reference_h,
        )
    )
    if args.full_ra2021_order and not args.ra2021_plan_only:
        require_source_policy_1e4_allow(
            parser,
            args.allow_source_policy_1e_4,
            "--full-ra2021-order",
            tuple(RA2021_ORDER_STEP_SIZES) + (RA2021_PUBLIC_REFERENCE_H,),
        )
    if targeted and not args.ra2021_plan_only:
        require_source_policy_1e4_allow(
            parser,
            args.allow_source_policy_1e_4,
            "targeted --ra2021-* rows",
            parse_float_csv(args.ra2021_step_sizes or "1e-2")
            + (float(args.ra2021_reference_h or RA2021_PUBLIC_REFERENCE_H),),
        )
    if args.ra2021_public_timing and not args.ra2021_public_timing_plan_only:
        require_source_policy_1e4_allow(
            parser,
            args.allow_source_policy_1e_4,
            "--ra2021-public-timing",
            (float(args.ra2021_timing_h),),
        )
    if args.ra2021_double_order and not args.ra2021_double_order_plan_only:
        require_source_policy_1e4_allow(
            parser,
            args.allow_source_policy_1e_4,
            "--ra2021-double-order",
            double_order_step_sizes + (double_order_config.reference_h,),
        )
    if args.gauss6_fullva_single and not args.gauss6_plan_only:
        require_source_policy_1e4_allow(
            parser,
            args.allow_source_policy_1e_4,
            "--gauss6-fullva-single",
            parse_float_csv(args.gauss6_step_sizes) + (float(args.gauss6_reference_h),),
        )
    if args.gauss6_public_single and not args.gauss6_public_plan_only:
        require_source_policy_1e4_allow(
            parser,
            args.allow_source_policy_1e_4,
            "--gauss6-public-single",
            gauss6_public_single_config.step_sizes + (gauss6_public_single_config.reference_h,),
        )
    if args.gauss6_closed_loop_2021 and not args.gauss6_closed_loop_plan_only:
        require_source_policy_1e4_allow(
            parser,
            args.allow_source_policy_1e_4,
            "--gauss6-closed-loop-2021",
            closed_loop_config.step_sizes + (closed_loop_config.reference_h,),
        )
    if args.gauss6_public_closed_loop_2021 and not args.gauss6_public_closed_loop_plan_only:
        require_source_policy_1e4_allow(
            parser,
            args.allow_source_policy_1e_4,
            "--gauss6-public-closed-loop-2021",
            public_closed_loop_config.step_sizes + (public_closed_loop_config.reference_h,),
        )
    if args.hi2022_double_pendulum and not args.hi2022_plan_only:
        require_source_policy_1e4_allow(
            parser,
            args.allow_source_policy_1e_4,
            "--hi2022-double-pendulum",
            hi2022_config.step_sizes + (hi2022_config.reference_h,),
        )
    if args.reuse_existing_results:
        summary = read_or_rebuild_summary()
        vp_search_rows, vp_search_summary = velocity_partitioning_code_search_rows()
        write_csv(RESULTS / "velocity_partitioning_code_search.csv", vp_search_rows)
        summary["velocity_partitioning_code_search"] = vp_search_summary
        summary["velocity_partitioning_code_status"] = VP_CODE_STATUS
        if args.ra2021_public_timing or args.ra2021_public_timing_plan_only:
            timing_rows, timing_summary = run_ra2021_timing_rows(timing_config)
            write_csv(RESULTS / "ra2021_public_timing_rows.csv", timing_rows)
            summary["ra2021_public_timing"] = timing_summary
        if args.ra2021_double_order or args.ra2021_double_order_plan_only:
            double_order_rows, double_order_summary = run_ra2021_double_pendulum_order_rows(double_order_config)
            write_csv(RESULTS / "ra2021_double_pendulum_order_rows.csv", double_order_rows)
            summary["ra2021_double_pendulum_order"] = double_order_summary
        if args.gauss6_closed_loop_2021 or args.gauss6_closed_loop_plan_only:
            closed_loop_rows, closed_loop_summary = run_gauss6_fullva_closed_loop_external_rows(closed_loop_config)
            write_csv(RESULTS / "gauss6_fullva_closed_loop_external_rows.csv", closed_loop_rows)
            comparison_rows, comparison_summary = run_gauss6_fullva_closed_loop_same_window_comparison_rows(
                closed_loop_config
            )
            write_csv(RESULTS / "gauss6_fullva_closed_loop_same_window_comparison_rows.csv", comparison_rows)
            summary["gauss6_fullva_closed_loop_external"] = closed_loop_summary
            summary["gauss6_fullva_closed_loop_selected_rows_completed"] = closed_loop_summary[
                "selected_rows_completed"
            ]
            summary["gauss6_fullva_closed_loop_same_window_comparison"] = comparison_summary
            summary["gauss6_fullva_closed_loop_same_window_comparison_completed"] = comparison_summary[
                "selected_rows_completed"
            ]
        else:
            comparison_path = RESULTS / "gauss6_fullva_closed_loop_same_window_comparison_rows.csv"
            comparison_rows = read_csv_rows(comparison_path) if comparison_path.exists() else []
        if (RESULTS / "ra2021_order_rows.csv").exists():
            order_work_rows, order_work_summary = summarize_ra2021_public_order_work_rows(
                read_csv_rows(RESULTS / "ra2021_order_rows.csv"),
                summary["ra2021_order"],
            )
            write_csv(RESULTS / "ra2021_public_order_work_summary.csv", order_work_rows)
            summary["ra2021_public_order_work_summary"] = order_work_summary
        if comparison_rows:
            comparison_work_rows, comparison_work_summary = summarize_closed_loop_same_window_work_precision_rows(
                comparison_rows
            )
            write_csv(RESULTS / "gauss6_closed_loop_same_window_work_precision_summary.csv", comparison_work_rows)
            summary["gauss6_closed_loop_same_window_work_precision_summary"] = comparison_work_summary
        if args.gauss6_public_single or args.gauss6_public_plan_only:
            public_single_rows, public_single_summary = run_gauss6_fullva_public_horizon_single_rows(
                gauss6_public_single_config
            )
            write_csv(RESULTS / "gauss6_fullva_public_horizon_single_rows.csv", public_single_rows)
            summary["gauss6_fullva_public_horizon_single"] = public_single_summary
        if args.gauss6_public_closed_loop_2021 or args.gauss6_public_closed_loop_plan_only:
            public_closed_loop_rows, public_closed_loop_summary = run_gauss6_fullva_closed_loop_external_rows(
                public_closed_loop_config
            )
            write_csv(RESULTS / "gauss6_fullva_public_horizon_closed_loop_rows.csv", public_closed_loop_rows)
            summary["gauss6_fullva_public_horizon_closed_loop"] = public_closed_loop_summary
        if args.hi2022_double_pendulum or args.hi2022_plan_only:
            write_csv(RESULTS / "hi2022_workload_estimate.csv", hi2022_workload_estimate(hi2022_config))
            hi2022_rows, hi2022_summary = run_hi2022_halfimplicit_rows(hi2022_config)
            write_csv(RESULTS / "hi2022_halfimplicit_rows.csv", hi2022_rows)
            summary["hi2022_halfimplicit"] = hi2022_summary
            summary["hi2022_halfimplicit_rows_completed"] = (
                hi2022_summary["selected_step_trio_group_count"]
                == hi2022_summary["selected_step_trio_required_group_count"]
            )
        summary["last_reuse_existing_results_runtime_sec"] = time.perf_counter() - started
        write_json_atomic(RESULTS / "summary_v048.json", summary)
        write_report(summary)
        return

    patched = patch_modern_numpy_scalar_assignments()
    run_plan = benchmark_run_plan()
    write_csv(RESULTS / "cross_paper_run_plan.csv", run_plan)
    vp_search_rows, vp_search_summary = velocity_partitioning_code_search_rows()
    write_csv(RESULTS / "velocity_partitioning_code_search.csv", vp_search_rows)

    if args.full_ra2021_order and targeted:
        raise ValueError("--full-ra2021-order cannot be combined with targeted --ra2021-* overrides")
    if args.ra2021_groups and (args.ra2021_forms or args.ra2021_models):
        raise ValueError("--ra2021-groups cannot be combined with --ra2021-forms or --ra2021-models")
    if args.full_ra2021_order:
        forms = tuple(RA2021_FORMS)
        models = tuple(RA2021_ORDER_MODELS)
        config = RA2021OrderConfig(
            policy="ra2021_public_order_policy",
            run_mode="full_ra2021_order",
            forms=forms,
            models=models,
            groups=cartesian_groups(forms, models),
            step_sizes=tuple(RA2021_ORDER_STEP_SIZES),
            reference_h=RA2021_PUBLIC_REFERENCE_H,
            t_end=RA2021_PUBLIC_T_END,
            run_public_code=not args.ra2021_plan_only,
            full_ra2021_order_completed=not args.ra2021_plan_only,
        )
    elif targeted or args.ra2021_plan_only:
        if args.ra2021_groups:
            groups = select_groups(args.ra2021_groups)
            forms = unique_group_forms(groups)
            models = unique_group_models(groups)
        else:
            forms = select_forms(args.ra2021_forms or "rA")
            models = select_models(args.ra2021_models or "single_pendulum")
            groups = cartesian_groups(forms, models)
        config = RA2021OrderConfig(
            policy="ra2021_targeted_order_pilot_not_full_campaign",
            run_mode="targeted_ra2021_order",
            forms=forms,
            models=models,
            groups=groups,
            step_sizes=parse_float_csv(args.ra2021_step_sizes or "1e-2"),
            reference_h=float(args.ra2021_reference_h or RA2021_PUBLIC_REFERENCE_H),
            t_end=float(args.ra2021_t_end or RA2021_PUBLIC_T_END),
            run_public_code=not args.ra2021_plan_only,
            full_ra2021_order_completed=False,
        )
    else:
        forms = ("rA",)
        models = (RA2021_ORDER_MODELS[0],)
        config = RA2021OrderConfig(
            policy="dependency_smoke_only_not_same_test_evidence",
            run_mode="smoke",
            forms=forms,
            models=models,
            groups=cartesian_groups(forms, models),
            step_sizes=(1e-2,),
            reference_h=1e-3,
            t_end=0.03,
            run_public_code=True,
            full_ra2021_order_completed=False,
        )

    write_csv(RESULTS / "same_test_workload_estimate.csv", ra2021_workload_estimate(config))
    rows, ra2021_summary = run_ra2021_order_rows(config)
    write_csv(RESULTS / "ra2021_order_rows.csv", rows)
    order_work_rows, order_work_summary = summarize_ra2021_public_order_work_rows(rows, ra2021_summary)
    write_csv(RESULTS / "ra2021_public_order_work_summary.csv", order_work_rows)
    if args.ra2021_public_timing or args.ra2021_public_timing_plan_only:
        timing_rows, timing_summary = run_ra2021_timing_rows(timing_config)
        write_csv(RESULTS / "ra2021_public_timing_rows.csv", timing_rows)
    else:
        timing_summary = summarize_ra2021_timing_rows_from_csv(
            read_csv_rows_if_exists(RESULTS / "ra2021_public_timing_rows.csv")
        )
    if args.ra2021_double_order or args.ra2021_double_order_plan_only:
        double_order_rows, double_order_summary = run_ra2021_double_pendulum_order_rows(double_order_config)
        write_csv(RESULTS / "ra2021_double_pendulum_order_rows.csv", double_order_rows)
    else:
        double_order_summary = summarize_ra2021_double_pendulum_order_rows_from_csv(
            read_csv_rows_if_exists(RESULTS / "ra2021_double_pendulum_order_rows.csv")
        )

    gauss6_config = Gauss6FullVAConfig(
        policy="gauss6_fullva_selected_single_pendulum_pilot_not_full_campaign",
        run_mode="gauss6_fullva_single_pilot",
        step_sizes=parse_float_csv(args.gauss6_step_sizes),
        reference_h=float(args.gauss6_reference_h),
        t_end=float(args.gauss6_t_end),
        run_model=bool(args.gauss6_fullva_single and not args.gauss6_plan_only),
    )
    gauss6_rows, gauss6_summary = run_gauss6_fullva_external_rows(gauss6_config)
    write_csv(RESULTS / "gauss6_fullva_external_rows.csv", gauss6_rows)

    public_single_rows, public_single_summary = run_gauss6_fullva_public_horizon_single_rows(
        gauss6_public_single_config
    )
    write_csv(RESULTS / "gauss6_fullva_public_horizon_single_rows.csv", public_single_rows)
    public_double_coarse_summary = summarize_gauss6_double_public_horizon_coarse_rows_from_csv(
        read_csv_rows_if_exists(RESULTS / "gauss6_fullva_public_horizon_double_coarse_rows.csv")
    )

    closed_loop_rows, closed_loop_summary = run_gauss6_fullva_closed_loop_external_rows(closed_loop_config)
    write_csv(RESULTS / "gauss6_fullva_closed_loop_external_rows.csv", closed_loop_rows)
    comparison_rows, comparison_summary = run_gauss6_fullva_closed_loop_same_window_comparison_rows(closed_loop_config)
    write_csv(RESULTS / "gauss6_fullva_closed_loop_same_window_comparison_rows.csv", comparison_rows)
    comparison_work_rows, comparison_work_summary = summarize_closed_loop_same_window_work_precision_rows(comparison_rows)
    write_csv(RESULTS / "gauss6_closed_loop_same_window_work_precision_summary.csv", comparison_work_rows)
    public_closed_loop_rows, public_closed_loop_summary = run_gauss6_fullva_closed_loop_external_rows(
        public_closed_loop_config
    )
    write_csv(RESULTS / "gauss6_fullva_public_horizon_closed_loop_rows.csv", public_closed_loop_rows)

    write_csv(RESULTS / "hi2022_workload_estimate.csv", hi2022_workload_estimate(hi2022_config))
    hi2022_rows, hi2022_summary = run_hi2022_halfimplicit_rows(hi2022_config)
    write_csv(RESULTS / "hi2022_halfimplicit_rows.csv", hi2022_rows)

    summary = {
        "version": "v048_cross_paper_same_test_benchmarks",
        "schema": "v048-cross-paper-benchmark-harness-v1",
        "python": platform.python_version(),
        "platform": platform.platform(),
        "numpy": np.__version__,
        "sbel_root": str(SBEL_ROOT),
        "sbel_commit": git_commit(SBEL_ROOT),
        "runtime_patches": patched,
        "run_mode": config.run_mode if config.run_public_code else f"{config.run_mode}_plan_only",
        "same_test_campaign_status": "not_run",
        "external_superiority_claim": False,
        "gauss6_fullva_external_rows_completed": gauss6_summary["full_external_campaign_completed"],
        "gauss6_fullva_selected_rows_completed": gauss6_summary["selected_rows_completed"],
        "gauss6_fullva_external": gauss6_summary,
        "gauss6_fullva_public_horizon_single": public_single_summary,
        "gauss6_fullva_public_horizon_double_coarse": public_double_coarse_summary,
        "gauss6_fullva_closed_loop_selected_rows_completed": closed_loop_summary["selected_rows_completed"],
        "gauss6_fullva_closed_loop_external": closed_loop_summary,
        "gauss6_fullva_closed_loop_same_window_comparison_completed": comparison_summary[
            "selected_rows_completed"
        ],
        "gauss6_fullva_closed_loop_same_window_comparison": comparison_summary,
        "gauss6_fullva_public_horizon_closed_loop": public_closed_loop_summary,
        "ra2021_public_order_work_summary": order_work_summary,
        "ra2021_public_timing": timing_summary,
        "ra2021_double_pendulum_order": double_order_summary,
        "gauss6_closed_loop_same_window_work_precision_summary": comparison_work_summary,
        "ra2021_order": ra2021_summary,
        "hi2022_halfimplicit": hi2022_summary,
        "hi2022_halfimplicit_rows_completed": hi2022_summary["selected_step_trio_group_count"] == hi2022_summary["selected_step_trio_required_group_count"],
        "case_inventory_rows": len(run_plan),
        "velocity_partitioning_code_status": VP_CODE_STATUS,
        "velocity_partitioning_code_search": vp_search_summary,
        "runtime_sec": time.perf_counter() - started,
    }
    write_json_atomic(RESULTS / "summary_v048.json", summary)
    write_report(summary)


if __name__ == "__main__":
    main()
