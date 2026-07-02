# CMAME Minimal Reproducibility Candidate

Status: candidate replay package, not submission ready.

This directory is a shrink target for the current paper evidence. It
contains the 44-cell paper result matrix, traceability and proof-boundary
artifacts, and one replay script. It does not contain a full source-policy
runner and does not upgrade any external-superiority claim. It carries
the current direct-PC2 residual-bridge proof-closure artifact, while the symbolic
Newton-Euler defect certificate remains a provenance boundary.

Human-runnable quickstart:

```bash
python scripts/replay_paper_matrix.py
```

Expected terminal markers:

- `cmame_minimal_candidate_replay=PASS`.
- `rows=44`.
- `methods=11`.
- `examples=4`.
- `common_reference_order_error_wins=40/40,40/40`.
- `source_policy_apples_to_apples_external=0/40`.
- `direct_pc2_proof_gap_closed=True`.
- `schema_compat_legacy_key_retained=True`.
- `proof_gap_scope=direct_residual_bridge_kantorovich_route_closed_primitive_taylor_conditional_schema_open`.
- `stage_residual_O_h7_direct_proof=True`.
- `newton_euler_symbolic_defect_certificate_complete=False`.
- `objective_blockers_open=OC4,OC6,OC12`.
- `global_submission_decision=do_not_submit_global`.
- `submission_ready=False`.

Run:

```bash
python scripts/replay_paper_matrix.py
```

Expected boundary:

- common-reference order/error wins: `40/40` and `40/40`.
- source-policy apples-to-apples external rows: `0/40`.
- direct PC2 proof gap closed: `True`.
- legacy compatibility key retained only inside the manifest schema.
- Newton-Euler symbolic defect certificate complete: `False`.
- objective blockers open: `OC4,OC6,OC12`.
- global submission decision: `do_not_submit_global`.
- submission ready: `False`.
- reviewer-facing code status: size-ok replay package, not a runner-centered submission package.
