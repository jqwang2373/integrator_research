#!/usr/bin/env python3
"""Read-only validator for the CMAME related-work depth audit."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
AUDIT_MD = PAPER / "CMAME_RELATED_WORK_AUDIT.md"
AUDIT_JSON = PAPER / "CMAME_RELATED_WORK_AUDIT.json"
MAIN_TEX = PAPER / "main_cmame.tex"
FLAT_TEX = PAPER / "cmame_submission_flat" / "main_cmame_submission.tex"
MAIN_TEXT = PAPER / "main_cmame.txt"
FLAT_TEXT = PAPER / "cmame_submission_flat" / "main_cmame_submission.txt"


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


def require_tokens(checks: Checks, text: str, tokens: list[str], label: str) -> None:
    for token in tokens:
        checks.check(contains_normalized(text, token), f"{label} missing token: {token}")


def main() -> int:
    checks = Checks()
    try:
        audit_md = read_text(AUDIT_MD)
        audit = read_json(AUDIT_JSON)
        main_tex = read_text(MAIN_TEX)
        flat_tex = read_text(FLAT_TEX)
        main_text = read_text(MAIN_TEXT)
        flat_text = read_text(FLAT_TEXT)
    except Exception as exc:  # noqa: BLE001 - concise CLI failure.
        print(f"cmame_related_work_audit=FAIL\n- {exc}")
        return 1

    checks.check(audit.get("schema") == "cmame-related-work-audit-v1", "audit schema changed")
    checks.check(audit.get("status") == "b8_closed_related_work_depth_checked", "audit status changed")
    checks.check(audit.get("submission_ready") is False, "audit must not claim submission ready")
    checks.check(audit.get("mechanical_preflight_passed") is True, "mechanical preflight marker changed")
    checks.check(audit.get("quality_review_passed") is False, "quality review marker changed")
    checks.check(audit.get("execution_policy", {}).get("default_step_policy") == "coarse_first_no_default_1e-4", "default policy changed")
    checks.check(audit.get("execution_policy", {}).get("strict_public_policy_1e-4") == "opt_in_only", "strict 1e-4 policy changed")
    checks.check(audit.get("execution_policy", {}).get("default_1e-4_required") is False, "audit requires default 1e-4")
    checks.check(audit.get("execution_policy", {}).get("heavy_numerical_run_invoked_by_audit") is False, "audit invokes heavy numerical run")
    checks.check(audit.get("closed_blocker", {}).get("id") == "B8", "audit does not close B8")
    checks.check(audit.get("open_blocker_count_after_closure") == 6, "open blocker count changed")
    checks.check(audit.get("closed_blockers") == ["B5", "B8"], "closed blocker list changed")
    checks.check(audit.get("open_blockers") == ["B1", "B2", "B3", "B4", "B6", "B7"], "open blocker list changed")

    expected_clusters = {
        "lie_group_integration",
        "absolute_coordinate_lie_group_dae_multibody",
        "constrained_collocation_and_index_reduction",
        "variational_and_symplectic_integrators",
        "nonsmooth_contact_friction_complementarity",
        "time_finite_elements",
    }
    checks.check(set(audit.get("required_clusters", [])) == expected_clusters, "related-work cluster set changed")
    expected_refs = {
        "gear1985automatic",
        "jay1996symplectic",
        "marsden2001discrete",
        "leyendecker2008variational",
        "leok2012prolongation",
        "stewart1996implicit",
        "anitescu1997formulating",
        "tasora2011matrixfree",
    }
    checks.check(set(audit.get("added_reference_keys", [])) == expected_refs, "added related-work reference set changed")
    boundary = audit.get("positioning_boundaries", {})
    checks.check(boundary.get("not_new_gauss_collocation_claim") is True, "Gauss-collocation non-claim changed")
    checks.check(boundary.get("not_discrete_variational_principle_claim") is True, "variational-principle non-claim changed")
    checks.check(boundary.get("not_nonsmooth_contact_integrator_claim") is True, "contact-integrator non-claim changed")

    tex_tokens = [
        "The relevant literature separates into six clusters",
        "high-order collocation and index-reduction methods",
        "Symplectic partitioned Runge--Kutta methods",
        "variational and symplectic integrators",
        "Constrained variational integrators",
        "does not construct a discrete variational principle",
        "nonsmooth contact and friction solvers",
        "contact complementarity or cone-complementarity solve",
        "does not claim a new nonsmooth contact integrator",
        "implemented Lie-group lower-pair stage residual",
        "\\bibitem{gear1985automatic}",
        "\\bibitem{jay1996symplectic}",
        "\\bibitem{marsden2001discrete}",
        "\\bibitem{leyendecker2008variational}",
        "\\bibitem{leok2012prolongation}",
        "\\bibitem{stewart1996implicit}",
        "\\bibitem{anitescu1997formulating}",
        "\\bibitem{tasora2011matrixfree}",
        "doi:10.1016/0377-0427(85)90008-1",
        "doi:10.1137/0733019",
        "doi:10.1017/S096249290100006X",
        "doi:10.1002/zamm.200700173",
        "doi:10.1093/imanum/drr042",
        "doi:10.1002/(SICI)1097-0207(19960815)39:15<2673::AID-NME972>3.0.CO;2-I",
        "doi:10.1023/A:1008292328909",
        "doi:10.1016/j.cma.2010.06.030",
    ]
    for label, text in [("main_cmame.tex", main_tex), ("flat main_cmame_submission.tex", flat_tex)]:
        require_tokens(checks, text, tex_tokens, label)

    text_tokens = [
        "Related work",
        "six clusters",
        "constrained collocation",
        "variational and symplectic integrators",
        "nonsmooth contact and friction solvers",
        "not claim a new nonsmooth contact integrator",
    ]
    for label, text in [("main_cmame.txt", main_text), ("flat main_cmame_submission.txt", flat_text)]:
        require_tokens(checks, text, text_tokens, label)

    require_tokens(
        checks,
        audit_md,
        [
            "Status: **B8 CLOSED - RELATED-WORK DEPTH CHECKED**",
            "Legacy compatibility alias only, not global readiness:",
            "These markers describe the bounded narrowed-claim subcheck only; they do not",
            "override `submission_ready=false` or close OC4/OC6/OC12.",
            "`open_narrowed_claim_blockers=0`",
            "`closed_narrowed_claim_blockers=B1,B2,B3,B4,B5,B6,B7,B8`",
            "`default_1e-4_required=false`",
            "constrained collocation",
            "variational integrator",
            "friction/contact multibody",
            "Lie-group DAE positioning",
        ],
        "CMAME_RELATED_WORK_AUDIT.md",
    )

    if checks.errors:
        print("cmame_related_work_audit=FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("cmame_related_work_audit=PASS")
    print("b8_status=closed")
    print("open_narrowed_claim_blockers=0")
    print("closed_narrowed_claim_blockers=B1,B2,B3,B4,B5,B6,B7,B8")
    print("related_work_clusters=6")
    print("added_reference_count=8")
    print("default_1e-4=False")
    print("submission_ready=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
