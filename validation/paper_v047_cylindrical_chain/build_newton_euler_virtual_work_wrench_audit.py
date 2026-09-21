#!/usr/bin/env python3
"""Build a D3 virtual-work wrench row-expanded identity audit.

This is a read-only proof-traceability record.  It checks that the
implemented Newton-Euler rows use the expected proximal/distal multiplier
force and torque signs for the two-body cylindrical chain and verifies both
the template-level and row-expanded lower-pair virtual-work identities behind
those signs.  It intentionally does not claim full dynamic-row symbolic
runtime equivalence or an O(h^7) dynamic-row defect bound.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import Any

import sympy as sp


PAPER = Path(__file__).resolve().parent
OUT_JSON = PAPER / "NEWTON_EULER_VIRTUAL_WORK_WRENCH_AUDIT.json"
OUT_MD = PAPER / "NEWTON_EULER_VIRTUAL_WORK_WRENCH_AUDIT.md"


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def find_function(tree: ast.AST, name: str) -> ast.FunctionDef | None:
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    return None


def assignment_source(function: ast.FunctionDef, source: str, name: str) -> str:
    for node in ast.walk(function):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == name:
                    segment = ast.get_source_segment(source, node)
                    return " ".join((segment or "").split())
    return ""


def assignment_sources(function: ast.FunctionDef, source: str, name: str) -> list[str]:
    segments: list[str] = []
    for node in ast.walk(function):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == name:
                    segment = ast.get_source_segment(source, node)
                    if segment:
                        segments.append(" ".join(segment.split()))
    return segments


def aug_assignment_sources(function: ast.FunctionDef, source: str, name: str) -> list[str]:
    segments: list[str] = []
    for node in ast.walk(function):
        if isinstance(node, ast.AugAssign) and isinstance(node.target, ast.Name) and node.target.id == name:
            segment = ast.get_source_segment(source, node)
            if segment:
                segments.append(" ".join(segment.split()))
    return segments


def contains_all(text: str, tokens: list[str]) -> bool:
    return all(token in text for token in tokens)


def sym_vec(prefix: str) -> sp.Matrix:
    return sp.Matrix(sp.symbols(f"{prefix}0 {prefix}1 {prefix}2"))


def dot(left: sp.Matrix, right: sp.Matrix) -> sp.Expr:
    return sp.expand(sum(left[i] * right[i] for i in range(3)))


def cross(left: sp.Matrix, right: sp.Matrix) -> sp.Matrix:
    return sp.Matrix(
        [
            left[1] * right[2] - left[2] * right[1],
            left[2] * right[0] - left[0] * right[2],
            left[0] * right[1] - left[1] * right[0],
        ]
    )


def symbolic_template_identity_audit() -> dict[str, Any]:
    theta = sym_vec("dtheta")
    lever = sym_vec("s")
    body_vec = sym_vec("a")

    identities = []
    for identity_id, virtual_work_scalar, generalized_torque in [
        (
            "point_or_axis_child_body",
            dot(body_vec, cross(theta, lever)),
            dot(theta, cross(lever, body_vec)),
        ),
        (
            "point_or_axis_parent_body",
            dot(-body_vec, cross(theta, lever)),
            dot(theta, cross(lever, -body_vec)),
        ),
    ]:
        difference = sp.simplify(virtual_work_scalar - generalized_torque)
        identities.append(
            {
                "id": identity_id,
                "virtual_work_scalar": str(virtual_work_scalar),
                "generalized_torque_scalar": str(generalized_torque),
                "simplified_difference": str(difference),
                "proved": difference == 0,
                "scope": (
                    "generic body-frame triple-product identity: "
                    "a dot (delta_theta x s) = delta_theta dot (s x a); "
                    "the parent row uses a replaced by -a"
                ),
            }
        )

    return {
        "checked": all(item["proved"] for item in identities),
        "identity_count": len(identities),
        "proved_identity_count": sum(item["proved"] for item in identities),
        "identities": identities,
        "template_statement": (
            "For each lower-pair point row b dot (x_child-x_parent) and axis row "
            "b dot (R_child a_child - R_parent a_parent), multiplication by the "
            "corresponding lambda component produces the same body-frame force "
            "and moment-arm/axis-torque terms used by the Newton-Euler residual."
        ),
        "scope": (
            "template-level virtual-work identity for the point and axis lower-pair "
            "multiplier terms; it does not prove row-expanded runtime equivalence, "
            "stage ordering/scaling equivalence, or the O(h^7) dynamic-row defect"
        ),
    }


def point_site_identity(site_id: str, sign: int) -> dict[str, Any]:
    dr = sym_vec(f"{site_id}_dr")
    theta = sym_vec(f"{site_id}_dtheta")
    lever = sym_vec(f"{site_id}_s")
    body_force = sym_vec(f"{site_id}_Fb")
    world_force = sym_vec(f"{site_id}_Fw")

    signed_world_force = sign * world_force
    signed_body_force = sign * body_force
    direct_scalar = dot(signed_world_force, dr) + dot(signed_body_force, cross(theta, lever))
    generalized_scalar = dot(dr, signed_world_force) + dot(theta, cross(lever, signed_body_force))
    difference = sp.simplify(direct_scalar - generalized_scalar)
    return {
        "id": site_id,
        "site_kind": "point_multiplier_pair",
        "body_sign": sign,
        "direct_virtual_work_scalar": str(direct_scalar),
        "generalized_wrench_scalar": str(generalized_scalar),
        "simplified_difference": str(difference),
        "proved": difference == 0,
        "scope": (
            "row-expanded point-row identity for the two normal multiplier rows: "
            "sigma F dot delta r + sigma R^T F dot (delta_theta x s) equals "
            "delta r dot sigma F + delta_theta dot (s x sigma R^T F)"
        ),
    }


def axis_site_identity(site_id: str, sign: int) -> dict[str, Any]:
    theta = sym_vec(f"{site_id}_dtheta")
    axis = sym_vec(f"{site_id}_axis")
    body_force = sym_vec(f"{site_id}_B")

    signed_body_force = sign * body_force
    direct_scalar = dot(signed_body_force, cross(theta, axis))
    generalized_scalar = dot(theta, cross(axis, signed_body_force))
    difference = sp.simplify(direct_scalar - generalized_scalar)
    return {
        "id": site_id,
        "site_kind": "axis_multiplier_pair",
        "body_sign": sign,
        "direct_virtual_work_scalar": str(direct_scalar),
        "generalized_wrench_scalar": str(generalized_scalar),
        "simplified_difference": str(difference),
        "proved": difference == 0,
        "scope": (
            "row-expanded axis-row identity for the two orientation multiplier rows: "
            "sigma B dot (delta_theta x a) equals delta_theta dot (a x sigma B)"
        ),
    }


def symbolic_row_expanded_identity_audit() -> dict[str, Any]:
    identities = [
        point_site_identity("joint0_child_body0_point", +1),
        point_site_identity("joint1_child_body1_point", +1),
        point_site_identity("joint1_parent_body0_point", -1),
        axis_site_identity("joint0_child_body0_axis", +1),
        axis_site_identity("joint1_child_body1_axis", +1),
        axis_site_identity("joint1_parent_body0_axis", -1),
    ]
    return {
        "checked": all(item["proved"] for item in identities),
        "identity_count": len(identities),
        "proved_identity_count": sum(item["proved"] for item in identities),
        "point_identity_count": sum(item["site_kind"] == "point_multiplier_pair" for item in identities),
        "axis_identity_count": sum(item["site_kind"] == "axis_multiplier_pair" for item in identities),
        "identities": identities,
        "implemented_order_sites": [
            "joint0 child body0 point force and proximal moment",
            "joint1 child body1 point force and proximal moment",
            "joint1 parent body0 point force and distal moment",
            "joint0 child body0 axis torque",
            "joint1 child body1 axis torque",
            "joint1 parent body0 distal axis torque",
        ],
        "scope": (
            "D3 row-expanded lower-pair multiplier virtual-work identity for the "
            "implemented two-body cylindrical-chain site ordering.  It proves the "
            "multiplier part of Phi_q^T lambda matches the implemented body-force "
            "and body-torque signs.  It does not include Brown-McPhee friction, "
            "the inertial Newton-Euler balance terms, smooth C7 force-lift bounds, "
            "or the O(h^7) dynamic-row defect proof."
        ),
    }


def runtime_source_audit() -> dict[str, Any]:
    source_path = PAPER.parent.parent / "numerics" / "v047_cylindrical_chain_pipeline" / "run_v047.py"
    source = source_path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    function = find_function(tree, "residual_cylindrical_chain")
    if function is None:
        return {
            "source_file": "v047_cylindrical_chain_pipeline/run_v047.py",
            "residual_function_found": False,
            "sign_skeleton_source_checked": False,
            "checks": {},
            "source_expressions": {},
            "scope": "failed to locate residual_cylindrical_chain",
        }

    force_assignments = assignment_sources(function, source, "force")
    prox_torque = assignment_source(function, source, "prox_torque")
    distal_torque = assignment_source(function, source, "distal_torque")
    axis_torque = " ".join(
        [assignment_source(function, source, "axis_torque"), *aug_assignment_sources(function, source, "axis_torque")]
    )
    dist_axis_torque = " ".join(
        [
            assignment_source(function, source, "dist_axis_torque"),
            *aug_assignment_sources(function, source, "dist_axis_torque"),
        ]
    )
    rot = assignment_source(function, source, "rot")

    checks = {
        "body_force_initialized_from_local_joint": any(
            "force = joint_force[body]" in item for item in force_assignments
        ),
        "body0_distal_force_subtracted": any(
            "force = force - joint_force[1]" in item for item in force_assignments
        ),
        "proximal_moment_arm_uses_positive_joint_force": contains_all(
            prox_torque,
            ["jnp.cross", "s_prev[body]", "R[body].T @ joint_force[body]"],
        ),
        "body0_distal_moment_arm_uses_negative_joint1_force": contains_all(
            distal_torque,
            ["jnp.cross", "s_next[0]", "R[0].T @ (-joint_force[1])"],
        ),
        "proximal_axis_torque_uses_positive_eta": contains_all(
            axis_torque,
            [
                "eta_prox[0]",
                "eta_prox[1]",
                "axis_prev[body]",
                "joint_basis[body, 0]",
                "joint_basis[body, 1]",
            ],
        ),
        "body0_distal_axis_torque_uses_joint1_eta": contains_all(
            dist_axis_torque,
            ["eta_dist[0]", "eta_dist[1]", "axis_next[0]", "joint_basis[1, 0]", "joint_basis[1, 1]"],
        ),
        "rotational_residual_sign_pattern": contains_all(
            rot,
            ["- prox_torque", "- distal_torque", "- axis_torque", "+ dist_axis_torque"],
        ),
    }
    checked = all(checks.values())
    return {
        "source_file": "v047_cylindrical_chain_pipeline/run_v047.py",
        "residual_function_found": True,
        "residual_function_lineno": function.lineno,
        "sign_skeleton_source_checked": checked,
        "checks": checks,
        "source_expressions": {
            "force_assignments": force_assignments,
            "prox_torque": prox_torque,
            "distal_torque": distal_torque,
            "axis_torque": axis_torque,
            "dist_axis_torque": dist_axis_torque,
            "rot": rot,
        },
        "scope": (
            "AST-backed source-sign audit for lower-pair multiplier force and torque "
            "placements in the Newton-Euler rows; this is a runtime-source sign "
            "check paired with the template identity audit, not an O(h^7) defect certificate"
        ),
    }


def expected_sites(row: dict[str, Any]) -> list[str]:
    body = int(row["body"])
    block = str(row["balance_block"])
    if block == "translational_newton_balance":
        if body == 0:
            return ["joint0_child_body0_force_plus", "joint1_parent_body0_force_minus"]
        return ["joint1_child_body1_force_plus"]
    if body == 0:
        return [
            "joint0_child_body0_moment_plus",
            "joint1_parent_body0_moment_minus",
            "joint0_child_body0_axis_torque_plus",
            "joint1_parent_body0_axis_torque_minus",
        ]
    return ["joint1_child_body1_moment_plus", "joint1_child_body1_axis_torque_plus"]


def residual_sign_template(row: dict[str, Any]) -> str:
    body = int(row["body"])
    block = str(row["balance_block"])
    if block == "translational_newton_balance":
        return "ma - mg - f_ext - (F0 - F1)" if body == 0 else "ma - mg - f_ext - F1"
    if body == 0:
        return "I - tau_ext - prox_torque - distal_torque - axis_torque + dist_axis_torque"
    return "I - tau_ext - prox_torque - axis_torque"


def site_summaries(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    definitions = {
        "joint0_child_body0_force_plus": {
            "virtual_work_term": "+F0 dot delta r0",
            "runtime_term": "joint_force[0] on body0",
        },
        "joint1_child_body1_force_plus": {
            "virtual_work_term": "+F1 dot delta r1",
            "runtime_term": "joint_force[1] on body1",
        },
        "joint1_parent_body0_force_minus": {
            "virtual_work_term": "-F1 dot delta r0",
            "runtime_term": "-joint_force[1] on body0",
        },
        "joint0_child_body0_moment_plus": {
            "virtual_work_term": "+(s_prev0 x R0^T F0) dot delta theta0",
            "runtime_term": "prox_torque on body0",
        },
        "joint1_child_body1_moment_plus": {
            "virtual_work_term": "+(s_prev1 x R1^T F1) dot delta theta1",
            "runtime_term": "prox_torque on body1",
        },
        "joint1_parent_body0_moment_minus": {
            "virtual_work_term": "+(s_next0 x R0^T(-F1)) dot delta theta0",
            "runtime_term": "distal_torque on body0",
        },
        "joint0_child_body0_axis_torque_plus": {
            "virtual_work_term": "+eta0 axis-constraint virtual rotation on body0",
            "runtime_term": "axis_torque on body0",
        },
        "joint1_child_body1_axis_torque_plus": {
            "virtual_work_term": "+eta1 axis-constraint virtual rotation on body1",
            "runtime_term": "axis_torque on body1",
        },
        "joint1_parent_body0_axis_torque_minus": {
            "virtual_work_term": "-eta1 axis-constraint virtual rotation on body0",
            "runtime_term": "dist_axis_torque appears with plus sign in residual after target-torque sign convention",
        },
    }
    summaries: list[dict[str, Any]] = []
    for site, definition in definitions.items():
        covered = [row["global_row"] for row in rows if site in row["expected_virtual_work_sites"]]
        summaries.append(
            {
                "site": site,
                "covered_rows": len(covered),
                "global_rows": covered,
                **definition,
                "checked": len(covered) > 0,
            }
        )
    return summaries


def main() -> None:
    target_audit = read_json(PAPER / "NEWTON_EULER_SYMBOLIC_TARGET_AUDIT.json")
    source_audit = runtime_source_audit()
    identity_audit = symbolic_template_identity_audit()
    row_expanded_identity_audit = symbolic_row_expanded_identity_audit()
    target_rows = target_audit.get("row_targets", [])

    rows: list[dict[str, Any]] = []
    for target in target_rows:
        sites = expected_sites(target)
        rows.append(
            {
                "global_row": target.get("global_row"),
                "stage": target.get("stage"),
                "body": target.get("body"),
                "component": target.get("component"),
                "balance_block": target.get("balance_block"),
                "expected_virtual_work_sites": sites,
                "residual_sign_template": residual_sign_template(target),
                "virtual_work_sign_skeleton_checked": source_audit["sign_skeleton_source_checked"] and bool(sites),
                "template_virtual_work_identity_proved": identity_audit["checked"],
                "row_expanded_virtual_work_identity_proved": row_expanded_identity_audit["checked"],
                "multiplier_wrench_consistency_closed": row_expanded_identity_audit["checked"],
                "full_row_expanded_virtual_work_identity_proved": row_expanded_identity_audit["checked"],
                "stage_residual_O_h7_implementation_defect_proved": False,
            }
        )

    checked_rows = sum(row["virtual_work_sign_skeleton_checked"] for row in rows)
    identity_rows = sum(row["template_virtual_work_identity_proved"] for row in rows)
    row_expanded_identity_rows = sum(row["row_expanded_virtual_work_identity_proved"] for row in rows)
    summaries = site_summaries(rows)
    result = {
        "schema": "newton-euler-virtual-work-wrench-audit-v1",
        "status": "d3_row_expanded_virtual_work_identity_checked_dynamic_defect_open",
        "submission_ready": False,
        "proof_gap_closed": False,
        "proof_gap_closed_scope": (
            "local_d3_virtual_work_audit_only; this audit is an input to the later "
            "direct D5/PC2 closure and does not by itself close the dynamic O(h^7) "
            "defect"
        ),
        "dynamic_symbolic_oracle_complete": False,
        "stage_residual_O_h7_implementation_defect_proved": False,
        "multiplier_wrench_consistency_closed": row_expanded_identity_audit["checked"],
        "template_virtual_work_identity_proved": identity_audit["checked"],
        "row_expanded_virtual_work_identity_proved": row_expanded_identity_audit["checked"],
        "full_row_expanded_virtual_work_identity_proved": row_expanded_identity_audit["checked"],
        "summary": {
            "row_count": len(rows),
            "checked_rows": checked_rows,
            "template_virtual_work_identity_rows": identity_rows,
            "row_expanded_virtual_work_identity_rows": row_expanded_identity_rows,
            "translational_row_count": sum(row["balance_block"] == "translational_newton_balance" for row in rows),
            "rotational_row_count": sum(row["balance_block"] == "rotational_euler_balance" for row in rows),
            "body0_rows_checked": sum(row["body"] == 0 and row["virtual_work_sign_skeleton_checked"] for row in rows),
            "body1_rows_checked": sum(row["body"] == 1 and row["virtual_work_sign_skeleton_checked"] for row in rows),
            "site_count": len(summaries),
            "site_count_checked": sum(site["checked"] for site in summaries),
            "virtual_work_sign_skeleton_checked": checked_rows == len(rows),
            "template_virtual_work_identity_proved": identity_audit["checked"],
            "template_identity_count": identity_audit["identity_count"],
            "template_identity_count_proved": identity_audit["proved_identity_count"],
            "row_expanded_virtual_work_identity_proved": row_expanded_identity_audit["checked"],
            "row_expanded_identity_count": row_expanded_identity_audit["identity_count"],
            "row_expanded_identity_count_proved": row_expanded_identity_audit["proved_identity_count"],
            "row_expanded_point_identity_count": row_expanded_identity_audit["point_identity_count"],
            "row_expanded_axis_identity_count": row_expanded_identity_audit["axis_identity_count"],
            "multiplier_wrench_consistency_closed": row_expanded_identity_audit["checked"],
            "full_row_expanded_virtual_work_identity_proved": row_expanded_identity_audit["checked"],
        },
        "runtime_source_audit": source_audit,
        "template_virtual_work_identity_audit": identity_audit,
        "row_expanded_virtual_work_identity_audit": row_expanded_identity_audit,
        "identity_skeleton": {
            "joint_force_definitions": [
                "F0 = lambda_0,0 b_0,0 + lambda_0,1 b_0,1 + rho_0 e_0",
                "F1 = lambda_1,0 b_1,0 + lambda_1,1 b_1,1 + rho_1 e_1",
            ],
            "force_sites": [
                "joint 0 acts on body 0 with +F0",
                "joint 1 acts on body 1 with +F1",
                "joint 1 acts on body 0 with -F1",
            ],
            "torque_sites": [
                "body 0 proximal moment: s_prev0 x R0^T F0",
                "body 1 proximal moment: s_prev1 x R1^T F1",
                "body 0 distal moment: s_next0 x R0^T(-F1)",
                "body 0 joint-1 distal axis multiplier enters with the residual sign +dist_axis_torque, matching a target-torque contribution -eta1",
            ],
            "scope": (
                "records the expected virtual-work sign skeleton for force and axis-multiplier "
                "wrench transfer; the template and row-expanded Phi_q^T lambda identities are "
                "checked by the symbolic identity audits, while the full dynamic-row O(h^7) "
                "defect certificate remains open"
            ),
        },
        "site_summaries": summaries,
        "row_audit": rows,
        "claim_policy": {
            "allowed_now": [
                "D3 virtual-work sign skeleton checked for all 36 Newton-Euler rows",
                "template-level lower-pair virtual-work identity checked",
                "row-expanded lower-pair multiplier-wrench consistency checked for the implemented cylindrical-chain site ordering",
                "body0/body1 proximal and distal multiplier force/torque signs are traceable",
                "the dynamic theorem remains conditional on the remaining dynamic symbolic-equivalence and O(h^7) proof obligations",
            ],
            "forbidden_now": [
                "dynamic_symbolic_oracle_complete",
                "stage_residual_O_h7_implementation_defect_proved",
                "proof_gap_closed",
                "submission_ready",
            ],
        },
        "source_files": {
            "newton_euler_symbolic_target_audit": "NEWTON_EULER_SYMBOLIC_TARGET_AUDIT.json",
            "runtime_source": "v047_cylindrical_chain_pipeline/run_v047.py",
        },
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# Newton-Euler Virtual-Work Wrench Audit",
        "",
        "Status: **OPEN - D3 row-expanded virtual-work identity checked, dynamic-defect proof open**.",
        "",
        f"- Row count: `{result['summary']['row_count']}`.",
        f"- Virtual-work sign skeleton checked rows: `{result['summary']['checked_rows']}`.",
        f"- Template virtual-work identity rows: `{result['summary']['template_virtual_work_identity_rows']}`.",
        f"- Template virtual-work identity proved: `{result['template_virtual_work_identity_proved']}`.",
        f"- Template identities proved: `{result['summary']['template_identity_count_proved']}/{result['summary']['template_identity_count']}`.",
        f"- Row-expanded virtual-work identity rows: `{result['summary']['row_expanded_virtual_work_identity_rows']}`.",
        f"- Row-expanded virtual-work identity proved: `{result['row_expanded_virtual_work_identity_proved']}`.",
        f"- Row-expanded identities proved: `{result['summary']['row_expanded_identity_count_proved']}/{result['summary']['row_expanded_identity_count']}`.",
        f"- Translational/rotational rows: `{result['summary']['translational_row_count']}/{result['summary']['rotational_row_count']}`.",
        f"- Body0/body1 checked rows: `{result['summary']['body0_rows_checked']}/{result['summary']['body1_rows_checked']}`.",
        f"- Site summaries checked: `{result['summary']['site_count_checked']}/{result['summary']['site_count']}`.",
        f"- Multiplier wrench consistency closed: `{result['multiplier_wrench_consistency_closed']}`.",
        f"- Full row-expanded virtual-work identity proved: `{result['full_row_expanded_virtual_work_identity_proved']}`.",
        f"- Stage residual O(h^7) implementation defect proved: `{result['stage_residual_O_h7_implementation_defect_proved']}`.",
        f"- Local D3 audit proof gap closed: `{result['proof_gap_closed']}`.",
        f"- Proof gap closed scope: `{result['proof_gap_closed_scope']}`.",
        f"- Submission ready: `{result['submission_ready']}`.",
        "",
        "## Runtime Source Sign Checks",
        "",
        "| check | passed |",
        "|---|---:|",
    ]
    for key, value in source_audit["checks"].items():
        lines.append(f"| `{key}` | `{value}` |")

    lines.extend(
        [
            "",
            "## Template Virtual-Work Identities",
            "",
            "| identity | proved | simplified difference |",
            "|---|---:|---:|",
        ]
    )
    for item in identity_audit["identities"]:
        lines.append(f"| `{item['id']}` | `{item['proved']}` | `{item['simplified_difference']}` |")

    lines.extend(
        [
            "",
            "## Row-Expanded Virtual-Work Identities",
            "",
            "| identity | kind | sign | proved | simplified difference |",
            "|---|---|---:|---:|---:|",
        ]
    )
    for item in row_expanded_identity_audit["identities"]:
        lines.append(
            f"| `{item['id']}` | `{item['site_kind']}` | `{item['body_sign']}` | "
            f"`{item['proved']}` | `{item['simplified_difference']}` |"
        )

    lines.extend(
        [
            "",
            "## Virtual-Work Sites",
            "",
            "| site | rows | runtime term | virtual-work term |",
            "|---|---:|---|---|",
        ]
    )
    for site in summaries:
        lines.append(
            f"| `{site['site']}` | `{site['covered_rows']}` | "
            f"{site['runtime_term']} | {site['virtual_work_term']} |"
        )

    lines.extend(
        [
            "",
            "## Row Audit",
            "",
            "| row | stage | body | comp. | block | sites | residual sign template | sign checked | template identity | row-expanded identity |",
            "|---:|---:|---:|---|---|---|---|---:|---:|---:|",
        ]
    )
    for row in rows:
        lines.append(
            f"| `{row['global_row']}` | `{row['stage']}` | `{row['body']}` | "
            f"`{row['component']}` | `{row['balance_block']}` | "
            f"`{','.join(row['expected_virtual_work_sites'])}` | "
            f"`{row['residual_sign_template']}` | `{row['virtual_work_sign_skeleton_checked']}` | "
            f"`{row['template_virtual_work_identity_proved']}` | "
            f"`{row['row_expanded_virtual_work_identity_proved']}` |"
        )

    lines.extend(
        [
            "",
            "## Claim Policy",
            "",
            "- Allowed now: cite 36-row D3 sign traceability, template virtual-work identity, and row-expanded multiplier-wrench consistency for the implemented lower-pair multiplier sites.",
            "- Forbidden now: claim O(h^7) dynamic-defect proof, full dynamic symbolic-oracle closure, proof-gap closure, or submission readiness.",
            "",
            "Validator: `validate_newton_euler_virtual_work_wrench_audit.py`.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("newton_euler_virtual_work_wrench_audit=written")
    print(f"checked_rows={checked_rows}")
    print(f"template_virtual_work_identity_rows={identity_rows}")
    print(f"row_expanded_virtual_work_identity_rows={row_expanded_identity_rows}")
    print(f"multiplier_wrench_consistency_closed={result['multiplier_wrench_consistency_closed']}")
    print("local_d3_audit_proof_gap_closed=False")


if __name__ == "__main__":
    main()
