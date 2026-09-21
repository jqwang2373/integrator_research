# D5 P_lambda PL2 Geometric-Margin Audit

Status: **PL2 uniform inf-sup bound proved; P_lambda rate remains open**.

This read-only audit records the direct normal-force and axis-torque
multiplier-column geometry used to prove PL2 on the compact proof
tube. It uses finite solved-stage probes only as diagnostics; the
uniform proof uses symbolic structure, lower-pair chart transversality,
and compactness.

## Summary

- Probe stage rows: `9`.
- Full dynamic-lambda blocks full column rank: `True`.
- Translational normal-force subblocks full column rank: `True`.
- Rotational axis-torque subblocks full column rank: `True`.
- Direct-sum subblocks full column rank: `True`.
- Minimum full dynamic-lambda singular value: `6.1428038880360070e-01`.
- Minimum translational normal singular value: `6.3503477958884713e-01`.
- Minimum rotational axis-torque singular value: `6.1803398874884796e-01`.
- Minimum direct-sum singular value: `6.1803398874884796e-01`.
- Compact-tube reduction recorded: `True`.
- Symbolic structure certificate recorded: `True`.
- Normal-force margin proved: `True`.
- Smooth-friction orthogonal perturbation proved: `True`.
- Translational normal symbolic lower bound: `6.1803398874989490e-01`.
- Axis-torque compact axis-plane margin proved: `True`.
- Symbolic margin premise proved: `True`.
- Uniform compact-tube margin proved: `True`.
- PL2 uniform inf-sup bound proved: `True`.
- P_lambda primitive closed: `False`.
- Primitive/Taylor PC2 route closed: `False`.

## Symbolic Structure Certificate

The normal-force map has the exact form `B lambda_N + f(v,||B lambda_N||) a`,
where the normal basis columns are orthonormal and orthogonal to the
cylindrical axis. Its lambda Jacobian is `B + a c^T`, so the Gram
matrix is `I + c c^T`; the smooth-friction normal-load derivative is
an orthogonal rank-one update and cannot reduce the smallest singular
value. The two-joint translational action-reaction block therefore has
the symbolic lower bound `6.1803398874989490e-01`.

For the axis-torque columns, the certificate records the exact identity
`sigma_min([a x R^T b0, a x R^T b1]) = |(R a) . (b0 x b1)|`.
The compact-tube axis-plane margin is proved by the accepted lower-pair
chart transversality certificate, not by finite probes.

## Axis-Plane Margin Certificate

The margin functions `m_j(z)=|(R_j a_j).n_j|` are continuous on the
compact proof tube. If one vanished on the accepted branch, the two
axis-torque multiplier columns would lose rank and the fixed lower-pair
axis chart would be singular. Assumption `ass:regularity` keeps the
accepted branch inside a regular constant-rank lower-pair chart; after
shrinking the tube inside that chart, compactness gives
`chi_axis=min_K min_j m_j>0`. Finite probes are not used to establish
the margin.

## Compact-Tube Reduction

On a compact proof tube, the multiplier-column map is continuous. If a
symbolic lower bound on its smallest singular value is proved for every
stage state in the tube, then compactness gives a uniform PL2 inf-sup
constant. Here the symbolic margin premise is closed by the normal-force,
axis-plane, and block-triangular estimates; finite probes do not
establish that premise.

## Acceptance Boundary

- The source topology for normal-force and axis-torque lambda columns is recorded.
- Finite margin probes support the PL2 proof target.
- Finite margin probes do not prove the compact-tube transversality margin.
- PL2 is closed as a uniform inf-sup subproof.
- `P_lambda` remains open.
- Primitive/Taylor PC2 lane remains open.
