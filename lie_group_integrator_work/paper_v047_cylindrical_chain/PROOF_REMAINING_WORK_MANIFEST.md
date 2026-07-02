# Proof Remaining Work Manifest

Status: **proof B1/B3 closed - submission gates remaining**.
Here `submission_ready=false` is scoped to proof remaining-work/global proof-package readiness,
not to the separate narrowed-claim package decision.

- Submission-ready scope: `proof_remaining_work_global_boundary_not_narrowed_claim_package_decision`.
- Proof remaining-work scope: `B1_B3_closed_remaining_global_submission_gates`.
- B4/B6/B7 narrowed-claim statuses: `closed/closed/closed`.
- Remaining global submission boundaries: `full_source_policy_package_ready,theorem_level_eta_h_solver_policy_evidence,closed_residual_to_error_theorem_for_mechanism_rows`.
- Direct PC2 proof gap closed: `True`.
- Direct PC2 proof-gap scope: `direct_residual_bridge_kantorovich_route_closed_primitive_taylor_conditional_schema_open`.
- Schema-compatibility note: legacy `proof_gap_closed` key retained for validators only: `True`; preferred reader key `direct_pc2_proof_gap_closed`.
- Schema-only compatibility reading rule: The schema-only compatibility boolean proof_gap_closed is a schema-compatible shorthand for direct_pc2_proof_gap_closed under the active direct PC2 residual-bridge/Kantorovich route. It does not close the primitive/Taylor route, P6 solver-policy evidence, P7 residual-to-error promotion, source-policy readiness, or full-TFE replacement.
- Dynamic symbolic oracle complete: `False`.
- Stage residual O(h^7) defect proved: `True`.
- Stage residual O(h^7) direct/symbolic-certificate proof: `True/False`.
- B1 symbolic oracle remaining: `False`.
- B3 closed by direct route: `True`.
- B1 AD-expanded symbolic oracle closure: `True`.
- PC4 residual-to-error closed/promoted: `False/False`.
- PC4 nonpromotion boundary retained: `True`.
- eta_h <= c_eta h^7 solver policy evidence: `False`.
- eta_h theorem condition retained: `True`.
- Residual-to-error blocking obligations: `7`.
- Residual-to-error route promoted: `False`.
- B4/B6/B7 closed elsewhere under narrowed claim: `True`.
- Active B1/B3 proof blockers remaining: `False`.
- Close requirements satisfied/unsatisfied: `4/0`.
- Unsatisfied close requirements: `[]`.
- Non-dynamic certified / symbolic-lane dynamic-open rows: `96/36`.
- Newton-Euler target rows translational/rotational: `36` / `18/18`.
- Newton-Euler row-obligation links: `180`.
- Newton-Euler symbolic defect certificate present/complete: `True/False`.
- Newton-Euler symbolic defect certificate expanded rows/C1 closed: `36/True`.
- Newton-Euler runtime expression structure checked/rows: `True/36`.
- Newton-Euler runtime template instantiation checked/rows: `True/36`.
- Newton-Euler body-specific wrench expansion checked/rows: `True/36`.
- Newton-Euler body0/body1 wrench expansion rows: `18/18`.
- Newton-Euler primitive/symbolic-lane certified/open rows: `0/36`.
- Active direct-route dynamic rows are closed separately by the D5 direct-substitution certificate; these open rows are not active PC2 open obligations.
- B1 independent residual symbolic row oracle closed/rows: `True/36`.
- B1 source-template identity/runtime-binding rows: `36/36`.
- B1 AD-expanded symbolic oracle closed rows/cells: `36/4752`.
- B1 AD-expanded symbolic oracle columns per row: `132`.
- Newton-Euler AD-expanded row oracle rows/columns: `36/132`.
- Runtime AD-expanded audit symbolic closure flag: `False`.
- Finite scaled trajectory rows/steps: `4/4` / `30`.
- Finite h-scaled tolerance-regime sweep rows/steps/velocity-order floor: `8` / `60` / `6.608089993735075`.
- Theorem-level scaled tolerance sweep recorded: `False`.
- Submission ready: `False`.

## Work Lanes

| lane | status | closes | traceable now | rows |
|---|---|---|---:|---:|
| `PC1_symbolic_row_oracle` | `closed_balance_identity_source_oracle` | `PC1` | `True` | `36` |
| `PC2_direct_dynamic_O_h7_defect_certificate` | `closed_by_direct_substitution_route` | `PC2` | `True` | `36` |
| `B1_AD_expanded_symbolic_oracle` | `closed_by_residual_identity_chain_rule_certificate` | `B1_symbolic_oracle` | `True` | `36` |
| `PC3_solver_eta_policy` | `condition_retained_not_empirical_closure` | `PC3` | `True` | `4` |
| `PC4_residual_to_error_boundary` | `nonpromotion_boundary_retained` | `PC4` | `nonpromotion_only` | `7` |

## Next Required Artifacts

- `no remaining B1/B3 proof-blocker artifact is required by this manifest`
- `keep validate_newton_euler_symbolic_defect_certificate.py passing without overclaiming O(h^7) via the symbolic-certificate route`
- `retain narrowed-claim B4/B6/B7 closure while keeping the global source-policy, eta_h, and residual-to-error boundaries explicit`

## Claim Policy

- Allowed now: direct-route O(h^7) proof closure, independent B1 residual-row symbolic oracle closure, AD-expanded B1 symbolic oracle closure, finite solver probes, explicit proof-boundary accounting, and AD-expanded runtime/formula binding coverage.
- Forbidden now: dynamic symbolic oracle completion, eta_h proof by finite probes, symbolic-certificate route O(h^7) proof, and global submission-ready proof/package readiness outside the narrowed-claim decision.
