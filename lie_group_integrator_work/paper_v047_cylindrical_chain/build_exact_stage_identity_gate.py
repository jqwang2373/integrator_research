#!/usr/bin/env python3
"""Build the exact-stage-identity proof gate for the compacted CMAME manuscript.

The gate pins the proof structure introduced on 2026-09-17: the implemented Gauss6/FullVA stage
system is exactly reduced joint-coordinate Gauss collocation (Lemma exact-stage-identity), the
stage residual at the lifted Gauss stage is identically zero, and the local defect is the
three-term sum C_G + C_E + C_N c_eta.  It supersedes the proof-route gates that pinned the
retired 96-row / PS2 / primitive-Taylor route (PROOF_CLOSURE_MANIFEST,
PROOF_CLAIM_TRACEABILITY_AUDIT, CMAME_STRICT_PROOF_AUDIT,
CMAME_STRICT_PROOF_POLICY_RECONCILIATION_AUDIT, CMAME_PROOF_STYLE_AUDIT,
NEWTON_EULER_SYMBOLIC_DEFECT_CERTIFICATE).

Read-only with respect to the numerical pipeline: it reads the two TeX sources, optionally runs
the Lean axiom check when the Lean toolchain is available, and writes
EXACT_STAGE_IDENTITY_GATE.json / .md.  It never invokes run_v047.py.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any

PAPER = Path(__file__).resolve().parent
MAIN_TEX = PAPER / "main_cmame.tex"
FLAT_TEX = PAPER / "cmame_submission_flat" / "main_cmame_submission.tex"
OUT_JSON = PAPER / "EXACT_STAGE_IDENTITY_GATE.json"
OUT_MD = PAPER / "EXACT_STAGE_IDENTITY_GATE.md"

LEAN_DIR = Path(os.environ.get("INTEGRATOR_LEAN_DIR", str(Path.home() / "lean" / "integrator_order_proof")))
LEAN_FILES = [
    "IntegratorOrderProof/Basic.lean",
    "IntegratorOrderProof/PerturbationChain/Contraction.lean",
    "IntegratorOrderProof/PerturbationChain/EndpointClosure.lean",
    "IntegratorOrderProof/PerturbationChain/LocalToGlobal.lean",
    "IntegratorOrderProof/PerturbationChain/MainTheorem.lean",
    "IntegratorOrderProof/PerturbationChain/JacobianPerturbation.lean",
    "IntegratorOrderProof/NewtonEuler/DynamicRows.lean",
    "IntegratorOrderProof/FullVA/NonDynamicRows.lean",
    "IntegratorOrderProof/Gauss/Tableau.lean",
    "IntegratorOrderProof/Gauss/QuadratureError.lean",
]
LEAN_THEOREMS = {
    "exact_stage_identity_nondynamic": "IntegratorOrderProof.FullVA.Transition.nondynamic_rows_iff",
    "exact_stage_identity_dynamic": "IntegratorOrderProof.NewtonEuler.dynamic_rows_vanish",
    "branch_selection": "IntegratorOrderProof.root_unique_of_linearization",
    "endpoint_closure": "IntegratorOrderProof.endpoint_correction_bound_h7",
    "inexact_newton": "IntegratorOrderProof.inexact_newton_output_bound",
    "local_to_global": "IntegratorOrderProof.local_to_global",
    "grid_bound": "IntegratorOrderProof.conditional_sixth_order_grid_bound",
    "gauss_tableau_order_conditions": "IntegratorOrderProof.Gauss6.butcher_order_six_hypotheses",
    "gauss_tableau_not_order_seven": "IntegratorOrderProof.Gauss6.not_B_seven",
    "quadrature_defect": "IntegratorOrderProof.gauss6_step_defect",
    "uniform_inverse_perturbation": "IntegratorOrderProof.uniform_inverse_of_perturbation",
    "newton_residual_decay": "IntegratorOrderProof.simplified_newton_residual_decay",
}
STANDARD_AXIOMS = "[propext, Classical.choice, Quot.sound]"

REQUIRED_LABELS = [
    "eq:joint-coordinates",
    "eq:collocation-defect-operator",
    "eq:g6fullva-expanded-stage",
    "eq:reduced-ode",
    "eq:reduced-gauss-stages",
    "ass:regularity",
    "eq:assumption-stability-scale",
    "eq:gauss-local-truncation",
    "lem:exact-stage-identity",
    "eq:exact-stage-identity",
    "lem:stage-residual-defect",
    "eq:branch-selection-chain",
    "lem:gauss-endpoint-defect",
    "eq:gauss-endpoint-defect",
    "eq:gauss-quadrature-defect",
    "lem:endpoint-closure",
    "eq:endpoint-correction-bound",
    "lem:inexact-newton",
    "eq:inexact-newton-stage-output-bounds",
    "lem:local-global-transfer",
    "eq:local-global-lemma-gronwall-factor",
    "eq:local-global-lemma-grid-bound",
    "def:accepted-branch-map",
    "thm:g6fullva-order",
    "eq:g6fva-local-defect-theorem",
    "eq:g6fva-reduced-grid-bound",
    "eq:g6fva-reported-grid-bound",
    "eq:three-term-local-defect-sum",
    "lem:tfe-target-order",
    "prop:order-comparison",
    "def:p7-transfer-certificate-template",
    "tab:proof-traceability",
    "tab:algorithm",
    "lem:p2-from-p1",
    "lem:newton-envelope",
    "tab:exact-identity-check",
    "tab:p2-constants-check",
    "tab:predictor-check",
    "tab:lean-development",
]

REQUIRED_TOKENS = [
    r"\item[P1.]",
    r"\item[P2.]",
    r"\item[P6.]",
    "$72$ constraint rows, $24$ joint-coordinate\ncollocation rows, and $36$ Newton--Euler rows",
    r"F_{A,h}(Z_G;x_n)=0",
    r"C_{\rm loc}=C_G+C_E+C_Nc_\eta",
    r"C_E=2M_{E,\mathrm{ri}}C_{E,\mathrm{raw}}",
    r"C_N=2MM_N",
    r"C_{\rm red}=C_{\rm loc}\Gamma_s(T)",
    r"C_{qv}=C_{\mathcal R}C_{\rm red}",
    "the residual value at the lifted Gauss stage is not\nsmall, it is zero",
    "exactly three-stage Gauss collocation of the\nreduced joint-coordinate equation of motion",
    "machine-checked in a Lean~4/Mathlib development",
    "satisfies Butcher's simplifying assumptions\n$B(6)$, $C(3)$, $D(3)$ and fails $B(7)$",
    r"Theorem~\ref{thm:g6fullva-order} is therefore",
    "no\nresidual-to-trajectory-error transfer theorem is accepted in this\nmanuscript",
    r"\paragraph{Implementation fidelity}",
    "one residual/Jacobian implementation path",
    "theorem-level solver policy",
    "fixed absolute Newton tolerance is a finite-run engineering choice",
    "not inferred from finite rank probes, residual tables, or observed convergence slopes",
    "Those probes are finite solver-policy diagnostics only",
    "consistency diagnostics of the accepted branch, not proof inputs",
    "no additional stage-level approximation",
]

RETIRED_TOKENS = [
    "primitive/Taylor",
    "primitive-route",
    "primitive route",
    "PS2",
    "PS3",
    "162",
    "96-row",
    "residual bridge",
    "residual-bridge",
    "D5 direct-substitution",
    r"P_{\mathrm{state}}",
    r"P_{\mathrm{acc}}",
    r"A_{ij}J_r^{-1}(\eta_j)\omega_j",
    r"r_i-r_n-h\sum_{j=1}^3 A_{ij}v_j",
    "Stage Jacobian structure",
    "72 kinematic",
    "implementation-binding",
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def contains_normalized(text: str, token: str) -> bool:
    return token in text or " ".join(token.split()) in " ".join(text.split())


def display_equation_hygiene(text: str) -> dict[str, Any]:
    checked_envs = ["equation", "align", "subequations"]
    missing_label_locations: list[dict[str, Any]] = []
    env_counts: dict[str, int] = {}
    for env in checked_envs:
        pattern = re.compile(rf"\\begin\{{{env}\}}(.*?)\\end\{{{env}\}}", re.S)
        matches = list(pattern.finditer(text))
        env_counts[env] = len(matches)
        for match in matches:
            if r"\label{" not in match.group(0):
                missing_label_locations.append({"env": env, "line": text[: match.start()].count("\n") + 1})
    bare_display_patterns = [r"^\s*\\\[", r"^\s*\\\]", r"\\begin\{align\*\}", r"\\begin\{equation\*\}",
                             r"\\begin\{displaymath\}", r"\$\$"]
    bare_display_locations: list[dict[str, Any]] = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        for pattern in bare_display_patterns:
            if re.search(pattern, line):
                bare_display_locations.append({"line": lineno, "pattern": pattern})
                break
    return {
        "env_counts": env_counts,
        "missing_label_count": len(missing_label_locations),
        "bare_display_count": len(bare_display_locations),
        "all_checked_displays_labelled": not missing_label_locations,
        "no_bare_display_math": not bare_display_locations,
    }


def display_equation_reference_hygiene(text: str) -> dict[str, Any]:
    checked_envs = ["equation", "align", "subequations"]
    labels: list[str] = []
    for env in checked_envs:
        pattern = re.compile(rf"\\begin\{{{env}\}}(.*?)\\end\{{{env}\}}", re.S)
        for match in pattern.finditer(text):
            labels.extend(re.findall(r"\\label\{([^}]+)\}", match.group(0)))
    unreferenced = []
    for label in labels:
        stripped = re.sub(rf"\\label\{{{re.escape(label)}\}}", "", text)
        if not re.search(rf"\\(?:eqref|ref)\{{{re.escape(label)}\}}", stripped):
            unreferenced.append(label)
    return {
        "display_label_count": len(labels),
        "unreferenced_label_count": len(unreferenced),
        "unreferenced_labels": unreferenced,
        "all_display_labels_referenced": not unreferenced,
    }


def manuscript_checks(tex: str) -> dict[str, Any]:
    labels_present = {label: (rf"\label{{{label}}}" in tex) for label in REQUIRED_LABELS}
    tokens_present = {token: contains_normalized(tex, token) for token in REQUIRED_TOKENS}
    retired_present = {token: contains_normalized(tex, token) for token in RETIRED_TOKENS}
    return {
        "labels_present": labels_present,
        "all_labels_present": all(labels_present.values()),
        "tokens_present": tokens_present,
        "all_tokens_present": all(tokens_present.values()),
        "retired_tokens_present": retired_present,
        "no_retired_tokens": not any(retired_present.values()),
        "lemma_count": tex.count(r"\begin{lemma}"),
        "theorem_count": tex.count(r"\begin{theorem}"),
        "line_count": tex.count("\n") + 1,
        "display_equation_hygiene": display_equation_hygiene(tex),
        "display_equation_reference_hygiene": display_equation_reference_hygiene(tex),
    }


PACKAGE_LEAN_DIR = PAPER / "lean"


def _sha256(path: Path) -> str:
    import hashlib
    return hashlib.sha256(path.read_bytes()).hexdigest()


def package_copy_sync() -> dict[str, Any]:
    """The Lean sources distributed with the paper package must equal the built development."""
    tracked = LEAN_FILES + ["IntegratorOrderProof.lean", "lakefile.toml", "lean-toolchain",
                            "lake-manifest.json", "scripts/Axioms.lean"]
    per_file = {}
    for name in tracked:
        pkg = PACKAGE_LEAN_DIR / name
        dev = LEAN_DIR / name
        per_file[name] = {
            "package_present": pkg.exists(),
            "package_sha256": _sha256(pkg) if pkg.exists() else None,
            "development_sha256": _sha256(dev) if dev.exists() else None,
            "in_sync": pkg.exists() and dev.exists() and _sha256(pkg) == _sha256(dev),
        }
    return {
        "package_lean_dir": str(PACKAGE_LEAN_DIR.relative_to(PAPER)),
        "all_package_files_present": all(v["package_present"] for v in per_file.values()),
        "all_in_sync_with_development": all(v["in_sync"] for v in per_file.values()),
        "development_present": LEAN_DIR.exists(),
        "files": per_file,
    }


def lean_binding(run_lean: bool) -> dict[str, Any]:
    files_present = {name: (LEAN_DIR / name).exists() for name in LEAN_FILES}
    axioms_script = LEAN_DIR / "scripts" / "Axioms.lean"
    lake = shutil.which("lake") or str(Path.home() / ".elan" / "bin" / "lake")
    info: dict[str, Any] = {
        "package_copy": package_copy_sync(),
        "lean_project_dir": str(LEAN_DIR),
        "lean_project_present": LEAN_DIR.exists(),
        "files_present": files_present,
        "all_files_present": all(files_present.values()),
        "theorem_names": LEAN_THEOREMS,
        "lean_check_run": False,
        "lean_status": "not_run_in_this_environment",
        "axiom_lines": [],
        "all_standard_axioms": None,
        "sorry_count": None,
    }
    if not (run_lean and LEAN_DIR.exists() and axioms_script.exists() and Path(lake).exists()):
        return info
    proc = subprocess.run([lake, "env", "lean", str(axioms_script)], cwd=LEAN_DIR, text=True,
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=900)
    # Lean wraps long lines; parse the flattened output instead of line by line.
    flat_output = " ".join(proc.stdout.split())
    entries = re.findall(r"'([^']+)' depends on axioms: \[([^\]]*)\]", flat_output)
    lines = [f"'{name}' depends on axioms: [{axioms}]" for name, axioms in entries]
    standard = {"propext", "Classical.choice", "Quot.sound"}
    info["lean_check_run"] = True
    info["axiom_lines"] = lines
    info["all_standard_axioms"] = bool(entries) and all(
        set(a.strip() for a in axioms.split(",")) <= standard for _, axioms in entries)
    info["sorry_count"] = proc.stdout.count("sorryAx")
    checked_names = {name for name, _ in entries}
    info["required_theorems_checked"] = {key: (name in checked_names) for key, name in LEAN_THEOREMS.items()}
    info["all_required_theorems_checked"] = all(info["required_theorems_checked"].values())
    info["lean_status"] = (
        "all_required_theorems_checked_standard_axioms_no_sorry"
        if info["all_standard_axioms"] and info["sorry_count"] == 0 and info["all_required_theorems_checked"]
        else "lean_check_failed"
    )
    return info


def main() -> None:
    run_lean = os.environ.get("EXACT_STAGE_IDENTITY_GATE_SKIP_LEAN") != "1"
    main_tex = read_text(MAIN_TEX)
    flat_tex = read_text(FLAT_TEX)
    main_checks = manuscript_checks(main_tex)
    flat_checks = manuscript_checks(flat_tex)
    lean = lean_binding(run_lean)

    def clean(checks: dict[str, Any]) -> bool:
        return (
            checks["all_labels_present"]
            and checks["all_tokens_present"]
            and checks["no_retired_tokens"]
            and checks["display_equation_hygiene"]["all_checked_displays_labelled"]
            and checks["display_equation_hygiene"]["no_bare_display_math"]
            and checks["display_equation_reference_hygiene"]["all_display_labels_referenced"]
        )

    manuscript_clean = clean(main_checks) and clean(flat_checks)
    pkg = lean["package_copy"]
    package_ok = pkg["all_package_files_present"] and (
        not pkg["development_present"] or pkg["all_in_sync_with_development"])
    lean_ok = package_ok and lean["lean_status"] in {
        "all_required_theorems_checked_standard_axioms_no_sorry", "not_run_in_this_environment"}
    status = (
        "exact_stage_identity_route_pinned_lean_checked"
        if manuscript_clean and lean["lean_check_run"] and lean_ok
        else "exact_stage_identity_route_pinned_lean_not_run_here"
        if manuscript_clean and lean_ok
        else "exact_stage_identity_gate_failed"
    )
    gate = {
        "schema": "exact-stage-identity-gate-v1",
        "status": status,
        "read_only": True,
        "run_v047_invoked": False,
        "submission_ready": False,
        "claim_state_change": False,
        "scope": "proof-route pin for the compacted manuscript; replaces the retired 96-row/PS2/primitive-Taylor gates",
        "superseded_artifacts": [
            "PROOF_CLOSURE_MANIFEST",
            "PROOF_CLAIM_TRACEABILITY_AUDIT",
            "CMAME_STRICT_PROOF_AUDIT",
            "CMAME_STRICT_PROOF_POLICY_RECONCILIATION_AUDIT",
            "CMAME_PROOF_STYLE_AUDIT",
            "NEWTON_EULER_SYMBOLIC_DEFECT_CERTIFICATE",
            "CMAME_PROOF_CONTRACT_GATE",
        ],
        "proof_route": {
            "stage_residual_at_lifted_gauss_stage": "identically_zero",
            "residual_certificate_constant_C_R": 0,
            "stage_root_perturbation_constant_C_A": 0,
            "local_defect_constant": "C_loc = C_G + C_E + C_N c_eta",
            "endpoint_closure_constant": "C_E = 2 M_E,ri C_E,raw",
            "inexact_newton_constant": "C_N = 2 M M_N",
            "retained_interfaces": ["P1", "P2", "P6"],
            "output_boundary": "P7",
            "removed_interfaces": ["P3", "P4", "P5"],
            "implemented_row_structure": {
                "constraint_rows": 72,
                "joint_coordinate_collocation_rows": 24,
                "newton_euler_rows": 36,
                "total_rows": 132,
            },
        },
        "manuscript": {"main": main_checks, "flat": flat_checks, "clean": manuscript_clean},
        "lean_binding": lean,
    }
    OUT_JSON.write_text(json.dumps(gate, indent=2) + "\n", encoding="utf-8")

    md = [
        "# Exact Stage Identity Gate",
        "",
        f"Status: **{status}**.",
        "",
        "This gate pins the compacted proof route of the CMAME manuscript: the implemented",
        "Gauss6/FullVA stage system is exactly reduced joint-coordinate Gauss collocation, the stage",
        "residual at the lifted Gauss stage is identically zero (`C_R = C_A = 0`), and the local defect is",
        "`C_loc = C_G + C_E + C_N c_eta`. Retained interfaces: P1, P2, P6; output boundary: P7; removed:",
        "P3, P4, P5. It changes no claim state and keeps `submission_ready=false`.",
        "",
        "## Manuscript checks",
        "",
        f"- main: labels `{sum(main_checks['labels_present'].values())}/{len(REQUIRED_LABELS)}`, "
        f"tokens `{sum(main_checks['tokens_present'].values())}/{len(REQUIRED_TOKENS)}`, "
        f"retired tokens present `{sum(main_checks['retired_tokens_present'].values())}`, "
        f"lines `{main_checks['line_count']}`, lemmas `{main_checks['lemma_count']}`, theorems `{main_checks['theorem_count']}`.",
        f"- flat: labels `{sum(flat_checks['labels_present'].values())}/{len(REQUIRED_LABELS)}`, "
        f"tokens `{sum(flat_checks['tokens_present'].values())}/{len(REQUIRED_TOKENS)}`, "
        f"retired tokens present `{sum(flat_checks['retired_tokens_present'].values())}`.",
        f"- display hygiene (main): unlabelled `{main_checks['display_equation_hygiene']['missing_label_count']}`, "
        f"bare `{main_checks['display_equation_hygiene']['bare_display_count']}`, "
        f"unreferenced labels `{main_checks['display_equation_reference_hygiene']['unreferenced_label_count']}` "
        f"of `{main_checks['display_equation_reference_hygiene']['display_label_count']}`.",
        "",
        "## Lean binding",
        "",
        f"- project: `{lean['lean_project_dir']}` present=`{lean['lean_project_present']}`, files `{sum(lean['files_present'].values())}/{len(LEAN_FILES)}`.",
        f"- lean check run here: `{lean['lean_check_run']}`; status `{lean['lean_status']}`; sorry count `{lean['sorry_count']}`.",
        f"- package copy `{lean['package_copy']['package_lean_dir']}/`: files present `{lean['package_copy']['all_package_files_present']}`, in sync with the built development `{lean['package_copy']['all_in_sync_with_development']}`.",
        "",
        "| role | Lean theorem |",
        "| --- | --- |",
    ]
    md += [f"| `{k}` | `{v}` |" for k, v in LEAN_THEOREMS.items()]
    md += ["", "## Superseded artifacts", ""]
    md += [f"- `{name}`" for name in gate["superseded_artifacts"]]
    md += ["", "Validator: `validate_exact_stage_identity_gate.py`.", ""]
    OUT_MD.write_text("\n".join(md), encoding="utf-8")
    print(f"exact_stage_identity_gate={status}")
    print(f"manuscript_clean={manuscript_clean}")
    print(f"lean_status={lean['lean_status']}")


if __name__ == "__main__":
    main()
