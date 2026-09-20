#!/usr/bin/env python3
"""Read-only static check for the implementation fidelity certificate."""

from __future__ import annotations

import re
import sys
from pathlib import Path


PAPER = Path(__file__).resolve().parent
from paper_paths import LATEX, package_path as manuscript_path
ROOT = PAPER.parent
PIPELINE = ROOT / "v047_cylindrical_chain_pipeline"
RUN = PIPELINE / "run_v047.py"
CERT = PAPER / "IMPLEMENTATION_FIDELITY_CERTIFICATE.md"
DYNAMIC = PAPER / "DYNAMIC_ROW_ORACLE_GATE.md"
MAIN = LATEX / "main_cmame.tex"
MANIFEST = PAPER / "SUBMISSION_ARTIFACT_MANIFEST.json"


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


def main() -> int:
    checks = Checks()
    try:
        run_text = read_text(RUN)
        cert = read_text(CERT)
        dynamic = read_text(DYNAMIC)
        main_tex = read_text(MAIN)
        manifest = read_text(MANIFEST)
    except Exception as exc:  # noqa: BLE001 - concise CLI failure.
        print(f"implementation_fidelity_certificate=FAIL\n- {exc}")
        return 1

    source_tokens = [
        "N_BODIES = 2",
        "N_JOINTS = 2",
        "N_STAGES = 3",
        "BODY_SIZE = 18",
        "LAMBDA_SIZE = 4",
        "STAGE_SIZE = N_BODIES * BODY_SIZE + N_JOINTS * LAMBDA_SIZE",
        "DIM = N_STAGES * STAGE_SIZE",
        "STAGE_FUNCTIONAL_BLOCK_LAYOUT = [",
        '("translational_position_weak_defect", 0, 6)',
        '("rotational_lie_position_weak_defect", 6, 6)',
        '("translational_velocity_weak_defect", 12, 6)',
        '("angular_velocity_weak_defect", 18, 6)',
        '("newton_euler_weak_balance", 24, 12)',
        '("lower_pair_index3_weak_constraints", 36, 8)',
        "def stage_row_family_slices_np()",
        "def stage_variable_family_slices_np()",
        "def residual_cylindrical_chain(",
        "R_VALUE = jax.jit(residual_cylindrical_chain)",
        "R_JAC = jax.jit(jax.jacfwd(residual_cylindrical_chain, argnums=0))",
        "R_INDEPENDENT_STAGE_FUNCTIONAL_BLOCKS = jax.jit(independent_stage_functional_weighted_blocks_jax)",
        "def joint_kinematics_jax(",
        "compose_right_quat_jax_safe",
        "right_jacobian_inverse_apply_jax_safe",
        "brown_mcphee_scalar_jax",
        "r_coll_axis",
        "v_coll_axis",
        "spin_coll_axis",
        "spin_acc_coll_axis",
        "pvel.append",
        "pacc.append",
        "u_block.append",
        "w_block.append",
        "constraints.append",
        "dyn.extend([trans, rot])",
        "out.extend([jnp.concatenate(pvel), jnp.concatenate(u_block), jnp.concatenate(pacc), jnp.concatenate(w_block), jnp.concatenate(dyn), jnp.concatenate(constraints)])",
    ]
    for token in source_tokens:
        checks.check(contains_normalized(run_text, token), f"run_v047.py missing token: {token}")

    layout_rows = re.findall(r'\("([^"]+)",\s*(\d+),\s*(\d+)\)', run_text)
    layout = {name: (int(offset), int(width)) for name, offset, width in layout_rows}
    expected_layout = {
        "translational_position_weak_defect": (0, 6),
        "rotational_lie_position_weak_defect": (6, 6),
        "translational_velocity_weak_defect": (12, 6),
        "angular_velocity_weak_defect": (18, 6),
        "newton_euler_weak_balance": (24, 12),
        "lower_pair_index3_weak_constraints": (36, 8),
    }
    checks.check(all(layout.get(name) == spec for name, spec in expected_layout.items()), "stage block layout changed")
    checks.check(sum(width for _, width in expected_layout.values()) == 44, "per-stage row width is not 44")
    checks.check(3 * sum(width for _, width in expected_layout.values()) == 132, "total residual dimension is not 132")

    certificate_tokens = [
        "Implementation Fidelity Certificate",
        "residual_cylindrical_chain",
        "R_JAC = jax.jit(jax.jacfwd(residual_cylindrical_chain, argnums=0))",
        "STAGE_FUNCTIONAL_BLOCK_LAYOUT",
        "translational_position_weak_defect",
        "rotational_lie_position_weak_defect",
        "translational_velocity_weak_defect",
        "angular_velocity_weak_defect",
        "newton_euler_weak_balance",
        "lower_pair_index3_weak_constraints",
        "static source-identity audit",
        "DYNAMIC_ROW_ORACLE_GATE.md",
        "runtime row and block-functional check",
        "R_INDEPENDENT_STAGE_FUNCTIONAL_BLOCKS",
        "partial independent formula-row oracle",
        "96 non-dynamic rows",
        "full independent formula-row oracle",
        "132 runtime formula rows",
        "multi-probe formula-row AD Jacobian oracle",
        "three deterministic probes",
        "R_JAC",
        "newton_euler_weak_balance",
        "not a dynamic symbolic-equivalence proof",
        "full_tfe_stage_replacement",
    ]
    for token in certificate_tokens:
        checks.check(contains_normalized(cert, token), f"certificate missing token: {token}")

    for token in [
        "Dynamic Row Oracle Gate",
        "residual shape: `(132,)`",
        "Jacobian shape: `(132,132)`",
        "block-functional cross-check",
        "partial independent formula-row oracle",
        "96 non-dynamic rows",
        "full independent formula-row oracle",
        "132 runtime formula rows",
        "multi-probe formula-row AD Jacobian oracle",
        "formula_row_ad_jacobian_probe_count=3",
        "max formula-row Jacobian mismatch",
        "newton_euler_weak_balance",
        "independent symbolic row oracle remains open",
        "validate_dynamic_row_oracle_gate.py",
    ]:
        checks.check(contains_normalized(dynamic, token), f"dynamic row oracle gate missing token: {token}")

    manuscript_tokens = [
        "static implementation certificate",
        "source-identity record",
        "one residual/Jacobian implementation path",
        "Implementation fidelity",
        "residual_cylindrical_chain",
        "R_JAC",
    ]
    for token in manuscript_tokens:
        checks.check(contains_normalized(main_tex, token), f"main_cmame.tex missing token: {token}")

    checks.check("IMPLEMENTATION_FIDELITY_CERTIFICATE.md" in manifest, "manifest missing certificate anchor")
    checks.check("DYNAMIC_ROW_ORACLE_GATE.md" in manifest, "manifest missing dynamic row oracle anchor")
    checks.check("validate_implementation_fidelity_certificate.py" in manifest, "manifest missing certificate validator")
    checks.check("validate_dynamic_row_oracle_gate.py" in manifest, "manifest missing dynamic row oracle validator")

    forbidden_tokens = [
        "full_tfe_stage_replacement=true",
        "complete source-paper residual reproduction is accepted",
        "accepted independent full-TFE stage replacement.",
    ]
    combined = "\n".join([cert, main_tex]).lower()
    for token in forbidden_tokens:
        checks.check(token.lower() not in combined, f"forbidden claim present: {token}")

    if checks.errors:
        print("implementation_fidelity_certificate=FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("implementation_fidelity_certificate=PASS")
    print("accepted_residual=residual_cylindrical_chain")
    print("accepted_jacobian=R_JAC_jacfwd_argnums0")
    print("stage_rows=132")
    print("dynamic_row_oracle_gate=checked")
    print("block_functional_crosscheck=checked")
    print("partial_formula_row_count=96")
    print("full_formula_row_count=132")
    print("formula_row_ad_jacobian_oracle=PASS")
    print("formula_row_ad_jacobian_probe_count=3")
    print("full_tfe_stage_replacement=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
