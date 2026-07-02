# Newton-Euler Virtual-Work Wrench Audit

Status: **OPEN - D3 row-expanded virtual-work identity checked, dynamic-defect proof open**.

- Row count: `36`.
- Virtual-work sign skeleton checked rows: `36`.
- Template virtual-work identity rows: `36`.
- Template virtual-work identity proved: `True`.
- Template identities proved: `2/2`.
- Row-expanded virtual-work identity rows: `36`.
- Row-expanded virtual-work identity proved: `True`.
- Row-expanded identities proved: `6/6`.
- Translational/rotational rows: `18/18`.
- Body0/body1 checked rows: `18/18`.
- Site summaries checked: `9/9`.
- Multiplier wrench consistency closed: `True`.
- Full row-expanded virtual-work identity proved: `True`.
- Stage residual O(h^7) implementation defect proved: `False`.
- Local D3 audit proof gap closed: `False`.
- Proof gap closed scope: `local_d3_virtual_work_audit_only; this audit is an input to the later direct D5/PC2 closure and does not by itself close the dynamic O(h^7) defect`.
- Submission ready: `False`.

## Runtime Source Sign Checks

| check | passed |
|---|---:|
| `body_force_initialized_from_local_joint` | `True` |
| `body0_distal_force_subtracted` | `True` |
| `proximal_moment_arm_uses_positive_joint_force` | `True` |
| `body0_distal_moment_arm_uses_negative_joint1_force` | `True` |
| `proximal_axis_torque_uses_positive_eta` | `True` |
| `body0_distal_axis_torque_uses_joint1_eta` | `True` |
| `rotational_residual_sign_pattern` | `True` |

## Template Virtual-Work Identities

| identity | proved | simplified difference |
|---|---:|---:|
| `point_or_axis_child_body` | `True` | `0` |
| `point_or_axis_parent_body` | `True` | `0` |

## Row-Expanded Virtual-Work Identities

| identity | kind | sign | proved | simplified difference |
|---|---|---:|---:|---:|
| `joint0_child_body0_point` | `point_multiplier_pair` | `1` | `True` | `0` |
| `joint1_child_body1_point` | `point_multiplier_pair` | `1` | `True` | `0` |
| `joint1_parent_body0_point` | `point_multiplier_pair` | `-1` | `True` | `0` |
| `joint0_child_body0_axis` | `axis_multiplier_pair` | `1` | `True` | `0` |
| `joint1_child_body1_axis` | `axis_multiplier_pair` | `1` | `True` | `0` |
| `joint1_parent_body0_axis` | `axis_multiplier_pair` | `-1` | `True` | `0` |

## Virtual-Work Sites

| site | rows | runtime term | virtual-work term |
|---|---:|---|---|
| `joint0_child_body0_force_plus` | `9` | joint_force[0] on body0 | +F0 dot delta r0 |
| `joint1_child_body1_force_plus` | `9` | joint_force[1] on body1 | +F1 dot delta r1 |
| `joint1_parent_body0_force_minus` | `9` | -joint_force[1] on body0 | -F1 dot delta r0 |
| `joint0_child_body0_moment_plus` | `9` | prox_torque on body0 | +(s_prev0 x R0^T F0) dot delta theta0 |
| `joint1_child_body1_moment_plus` | `9` | prox_torque on body1 | +(s_prev1 x R1^T F1) dot delta theta1 |
| `joint1_parent_body0_moment_minus` | `9` | distal_torque on body0 | +(s_next0 x R0^T(-F1)) dot delta theta0 |
| `joint0_child_body0_axis_torque_plus` | `9` | axis_torque on body0 | +eta0 axis-constraint virtual rotation on body0 |
| `joint1_child_body1_axis_torque_plus` | `9` | axis_torque on body1 | +eta1 axis-constraint virtual rotation on body1 |
| `joint1_parent_body0_axis_torque_minus` | `9` | dist_axis_torque appears with plus sign in residual after target-torque sign convention | -eta1 axis-constraint virtual rotation on body0 |

## Row Audit

| row | stage | body | comp. | block | sites | residual sign template | sign checked | template identity | row-expanded identity |
|---:|---:|---:|---|---|---|---|---:|---:|---:|
| `24` | `0` | `0` | `x` | `translational_newton_balance` | `joint0_child_body0_force_plus,joint1_parent_body0_force_minus` | `ma - mg - f_ext - (F0 - F1)` | `True` | `True` | `True` |
| `25` | `0` | `0` | `y` | `translational_newton_balance` | `joint0_child_body0_force_plus,joint1_parent_body0_force_minus` | `ma - mg - f_ext - (F0 - F1)` | `True` | `True` | `True` |
| `26` | `0` | `0` | `z` | `translational_newton_balance` | `joint0_child_body0_force_plus,joint1_parent_body0_force_minus` | `ma - mg - f_ext - (F0 - F1)` | `True` | `True` | `True` |
| `27` | `0` | `0` | `x` | `rotational_euler_balance` | `joint0_child_body0_moment_plus,joint1_parent_body0_moment_minus,joint0_child_body0_axis_torque_plus,joint1_parent_body0_axis_torque_minus` | `I - tau_ext - prox_torque - distal_torque - axis_torque + dist_axis_torque` | `True` | `True` | `True` |
| `28` | `0` | `0` | `y` | `rotational_euler_balance` | `joint0_child_body0_moment_plus,joint1_parent_body0_moment_minus,joint0_child_body0_axis_torque_plus,joint1_parent_body0_axis_torque_minus` | `I - tau_ext - prox_torque - distal_torque - axis_torque + dist_axis_torque` | `True` | `True` | `True` |
| `29` | `0` | `0` | `z` | `rotational_euler_balance` | `joint0_child_body0_moment_plus,joint1_parent_body0_moment_minus,joint0_child_body0_axis_torque_plus,joint1_parent_body0_axis_torque_minus` | `I - tau_ext - prox_torque - distal_torque - axis_torque + dist_axis_torque` | `True` | `True` | `True` |
| `30` | `0` | `1` | `x` | `translational_newton_balance` | `joint1_child_body1_force_plus` | `ma - mg - f_ext - F1` | `True` | `True` | `True` |
| `31` | `0` | `1` | `y` | `translational_newton_balance` | `joint1_child_body1_force_plus` | `ma - mg - f_ext - F1` | `True` | `True` | `True` |
| `32` | `0` | `1` | `z` | `translational_newton_balance` | `joint1_child_body1_force_plus` | `ma - mg - f_ext - F1` | `True` | `True` | `True` |
| `33` | `0` | `1` | `x` | `rotational_euler_balance` | `joint1_child_body1_moment_plus,joint1_child_body1_axis_torque_plus` | `I - tau_ext - prox_torque - axis_torque` | `True` | `True` | `True` |
| `34` | `0` | `1` | `y` | `rotational_euler_balance` | `joint1_child_body1_moment_plus,joint1_child_body1_axis_torque_plus` | `I - tau_ext - prox_torque - axis_torque` | `True` | `True` | `True` |
| `35` | `0` | `1` | `z` | `rotational_euler_balance` | `joint1_child_body1_moment_plus,joint1_child_body1_axis_torque_plus` | `I - tau_ext - prox_torque - axis_torque` | `True` | `True` | `True` |
| `68` | `1` | `0` | `x` | `translational_newton_balance` | `joint0_child_body0_force_plus,joint1_parent_body0_force_minus` | `ma - mg - f_ext - (F0 - F1)` | `True` | `True` | `True` |
| `69` | `1` | `0` | `y` | `translational_newton_balance` | `joint0_child_body0_force_plus,joint1_parent_body0_force_minus` | `ma - mg - f_ext - (F0 - F1)` | `True` | `True` | `True` |
| `70` | `1` | `0` | `z` | `translational_newton_balance` | `joint0_child_body0_force_plus,joint1_parent_body0_force_minus` | `ma - mg - f_ext - (F0 - F1)` | `True` | `True` | `True` |
| `71` | `1` | `0` | `x` | `rotational_euler_balance` | `joint0_child_body0_moment_plus,joint1_parent_body0_moment_minus,joint0_child_body0_axis_torque_plus,joint1_parent_body0_axis_torque_minus` | `I - tau_ext - prox_torque - distal_torque - axis_torque + dist_axis_torque` | `True` | `True` | `True` |
| `72` | `1` | `0` | `y` | `rotational_euler_balance` | `joint0_child_body0_moment_plus,joint1_parent_body0_moment_minus,joint0_child_body0_axis_torque_plus,joint1_parent_body0_axis_torque_minus` | `I - tau_ext - prox_torque - distal_torque - axis_torque + dist_axis_torque` | `True` | `True` | `True` |
| `73` | `1` | `0` | `z` | `rotational_euler_balance` | `joint0_child_body0_moment_plus,joint1_parent_body0_moment_minus,joint0_child_body0_axis_torque_plus,joint1_parent_body0_axis_torque_minus` | `I - tau_ext - prox_torque - distal_torque - axis_torque + dist_axis_torque` | `True` | `True` | `True` |
| `74` | `1` | `1` | `x` | `translational_newton_balance` | `joint1_child_body1_force_plus` | `ma - mg - f_ext - F1` | `True` | `True` | `True` |
| `75` | `1` | `1` | `y` | `translational_newton_balance` | `joint1_child_body1_force_plus` | `ma - mg - f_ext - F1` | `True` | `True` | `True` |
| `76` | `1` | `1` | `z` | `translational_newton_balance` | `joint1_child_body1_force_plus` | `ma - mg - f_ext - F1` | `True` | `True` | `True` |
| `77` | `1` | `1` | `x` | `rotational_euler_balance` | `joint1_child_body1_moment_plus,joint1_child_body1_axis_torque_plus` | `I - tau_ext - prox_torque - axis_torque` | `True` | `True` | `True` |
| `78` | `1` | `1` | `y` | `rotational_euler_balance` | `joint1_child_body1_moment_plus,joint1_child_body1_axis_torque_plus` | `I - tau_ext - prox_torque - axis_torque` | `True` | `True` | `True` |
| `79` | `1` | `1` | `z` | `rotational_euler_balance` | `joint1_child_body1_moment_plus,joint1_child_body1_axis_torque_plus` | `I - tau_ext - prox_torque - axis_torque` | `True` | `True` | `True` |
| `112` | `2` | `0` | `x` | `translational_newton_balance` | `joint0_child_body0_force_plus,joint1_parent_body0_force_minus` | `ma - mg - f_ext - (F0 - F1)` | `True` | `True` | `True` |
| `113` | `2` | `0` | `y` | `translational_newton_balance` | `joint0_child_body0_force_plus,joint1_parent_body0_force_minus` | `ma - mg - f_ext - (F0 - F1)` | `True` | `True` | `True` |
| `114` | `2` | `0` | `z` | `translational_newton_balance` | `joint0_child_body0_force_plus,joint1_parent_body0_force_minus` | `ma - mg - f_ext - (F0 - F1)` | `True` | `True` | `True` |
| `115` | `2` | `0` | `x` | `rotational_euler_balance` | `joint0_child_body0_moment_plus,joint1_parent_body0_moment_minus,joint0_child_body0_axis_torque_plus,joint1_parent_body0_axis_torque_minus` | `I - tau_ext - prox_torque - distal_torque - axis_torque + dist_axis_torque` | `True` | `True` | `True` |
| `116` | `2` | `0` | `y` | `rotational_euler_balance` | `joint0_child_body0_moment_plus,joint1_parent_body0_moment_minus,joint0_child_body0_axis_torque_plus,joint1_parent_body0_axis_torque_minus` | `I - tau_ext - prox_torque - distal_torque - axis_torque + dist_axis_torque` | `True` | `True` | `True` |
| `117` | `2` | `0` | `z` | `rotational_euler_balance` | `joint0_child_body0_moment_plus,joint1_parent_body0_moment_minus,joint0_child_body0_axis_torque_plus,joint1_parent_body0_axis_torque_minus` | `I - tau_ext - prox_torque - distal_torque - axis_torque + dist_axis_torque` | `True` | `True` | `True` |
| `118` | `2` | `1` | `x` | `translational_newton_balance` | `joint1_child_body1_force_plus` | `ma - mg - f_ext - F1` | `True` | `True` | `True` |
| `119` | `2` | `1` | `y` | `translational_newton_balance` | `joint1_child_body1_force_plus` | `ma - mg - f_ext - F1` | `True` | `True` | `True` |
| `120` | `2` | `1` | `z` | `translational_newton_balance` | `joint1_child_body1_force_plus` | `ma - mg - f_ext - F1` | `True` | `True` | `True` |
| `121` | `2` | `1` | `x` | `rotational_euler_balance` | `joint1_child_body1_moment_plus,joint1_child_body1_axis_torque_plus` | `I - tau_ext - prox_torque - axis_torque` | `True` | `True` | `True` |
| `122` | `2` | `1` | `y` | `rotational_euler_balance` | `joint1_child_body1_moment_plus,joint1_child_body1_axis_torque_plus` | `I - tau_ext - prox_torque - axis_torque` | `True` | `True` | `True` |
| `123` | `2` | `1` | `z` | `rotational_euler_balance` | `joint1_child_body1_moment_plus,joint1_child_body1_axis_torque_plus` | `I - tau_ext - prox_torque - axis_torque` | `True` | `True` | `True` |

## Claim Policy

- Allowed now: cite 36-row D3 sign traceability, template virtual-work identity, and row-expanded multiplier-wrench consistency for the implemented lower-pair multiplier sites.
- Forbidden now: claim O(h^7) dynamic-defect proof, full dynamic symbolic-oracle closure, proof-gap closure, or submission readiness.

Validator: `validate_newton_euler_virtual_work_wrench_audit.py`.
