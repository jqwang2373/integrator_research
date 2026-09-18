#!/usr/bin/env python3
"""Read-only validator for EXACT_STAGE_IDENTITY_GATE.json / .md.

Recomputes the manuscript checks from the two TeX sources and compares them with the recorded
gate; never runs Lean, never runs run_v047.py.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import build_exact_stage_identity_gate as gate_builder

PAPER = Path(__file__).resolve().parent
GATE_JSON = PAPER / "EXACT_STAGE_IDENTITY_GATE.json"
GATE_MD = PAPER / "EXACT_STAGE_IDENTITY_GATE.md"


class Checks:
    def __init__(self) -> None:
        self.errors: list[str] = []

    def check(self, condition: bool, message: str) -> None:
        if not condition:
            self.errors.append(message)


def main() -> int:
    checks = Checks()
    try:
        gate = json.loads(GATE_JSON.read_text(encoding="utf-8"))
        gate_md = GATE_MD.read_text(encoding="utf-8")
        main_tex = gate_builder.read_text(gate_builder.MAIN_TEX)
        flat_tex = gate_builder.read_text(gate_builder.FLAT_TEX)
    except Exception as exc:  # noqa: BLE001
        print(f"exact_stage_identity_gate=FAIL\n- {exc}")
        return 1

    checks.check(gate.get("schema") == "exact-stage-identity-gate-v1", "schema changed")
    checks.check(gate.get("read_only") is True, "gate must be read-only")
    checks.check(gate.get("run_v047_invoked") is False, "gate must not invoke run_v047.py")
    checks.check(gate.get("submission_ready") is False, "gate must not claim submission ready")
    checks.check(gate.get("claim_state_change") is False, "gate must not change claim state")
    checks.check(
        gate.get("status") in {
            "exact_stage_identity_route_pinned_lean_checked",
            "exact_stage_identity_route_pinned_lean_not_run_here",
        },
        f"gate status is not a pinned status: {gate.get('status')}",
    )

    for label, tex in [("main", main_tex), ("flat", flat_tex)]:
        recorded = gate.get("manuscript", {}).get(label, {})
        expected = gate_builder.manuscript_checks(tex)
        checks.check(recorded == expected, f"{label} manuscript checks are stale")
        checks.check(expected["all_labels_present"], f"{label}: required labels missing: "
                     + ",".join(k for k, v in expected["labels_present"].items() if not v))
        checks.check(expected["all_tokens_present"], f"{label}: required tokens missing: "
                     + " | ".join(k for k, v in expected["tokens_present"].items() if not v))
        checks.check(expected["no_retired_tokens"], f"{label}: retired-route tokens present: "
                     + ",".join(k for k, v in expected["retired_tokens_present"].items() if v))
        hygiene = expected["display_equation_hygiene"]
        checks.check(hygiene["all_checked_displays_labelled"], f"{label}: unlabelled display math")
        checks.check(hygiene["no_bare_display_math"], f"{label}: bare display math")
        checks.check(expected["display_equation_reference_hygiene"]["all_display_labels_referenced"],
                     f"{label}: unreferenced display labels")

    route = gate.get("proof_route", {})
    checks.check(route.get("stage_residual_at_lifted_gauss_stage") == "identically_zero", "stage residual status changed")
    checks.check(route.get("residual_certificate_constant_C_R") == 0, "C_R must be recorded as 0")
    checks.check(route.get("retained_interfaces") == ["P1", "P2", "P6"], "retained interfaces changed")
    checks.check(route.get("removed_interfaces") == ["P3", "P4", "P5"], "removed interfaces changed")
    rows = route.get("implemented_row_structure", {})
    checks.check(
        (rows.get("constraint_rows"), rows.get("joint_coordinate_collocation_rows"), rows.get("newton_euler_rows"),
         rows.get("total_rows")) == (72, 24, 36, 132),
        "implemented row structure changed",
    )

    lean = gate.get("lean_binding", {})
    checks.check(lean.get("theorem_names") == gate_builder.LEAN_THEOREMS, "Lean theorem map changed")
    pkg = lean.get("package_copy", {})
    checks.check(pkg.get("all_package_files_present") is True, "Lean sources missing from the paper package (lean/)")
    checks.check(pkg == gate_builder.package_copy_sync(), "Lean package-copy sync record is stale")
    if pkg.get("development_present"):
        checks.check(pkg.get("all_in_sync_with_development") is True,
                     "paper-package Lean copy differs from the built development")
    if lean.get("lean_check_run"):
        checks.check(lean.get("all_standard_axioms") is True, "Lean axioms are not the standard three")
        checks.check(lean.get("sorry_count") == 0, "Lean development contains sorry")
        checks.check(lean.get("all_required_theorems_checked") is True, "Lean required theorems not all checked")
    else:
        checks.check(lean.get("lean_status") == "not_run_in_this_environment", "Lean status inconsistent")

    checks.check(gate_md.startswith("# Exact Stage Identity Gate"), "gate markdown header changed")
    checks.check(f"Status: **{gate.get('status')}**" in gate_md, "gate markdown status is stale")

    if checks.errors:
        print("exact_stage_identity_gate=FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1
    print("exact_stage_identity_gate=PASS")
    print(f"status={gate.get('status')}")
    print(f"lean_status={lean.get('lean_status')}")
    print(f"main_lines={gate['manuscript']['main']['line_count']}")
    print("superseded_artifacts=" + ",".join(gate.get("superseded_artifacts", [])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
