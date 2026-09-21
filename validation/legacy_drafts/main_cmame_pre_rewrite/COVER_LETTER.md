# Cover Letter Draft

Status note: this is a bounded narrowed-claim cover-letter draft, not a
release authorization for the global package. Do not use it as a final global
submission letter until `OC4`, `OC6`, and `OC12` are closed or explicitly
demoted in the submission policy. The letter below excludes source-paper
external superiority, full source-policy reproduction, and full-TFE replacement
claims.

Reviewer-facing package boundary: the full source-policy runner archive is not
ready. Safe actions without B4 opt-in are `4`; opt-in-required actions are `1`;
source-policy execution allowed now is `False`; exact B4 opt-in required for
execution is `True`; opt-in commands/mapped external rows are `13/20`.
Command-row traceability covers unique RA/HI rows `20/20`, row refs `32/32`,
and mismatch/terminal/closed/promotion-ready counts `0/0/0/0`. Safe action ids
are `rebuild_read_only_audit_chain,rerun_read_only_validators,keep_narrowed_archive_provenance_only,monitor_reopen_conditions`;
opt-in action ids are `authorized_b4_ra_hi_source_policy_execution`. The guarded
driver is `run_b4_source_policy_after_opt_in.sh`, and the exact approval phrase
is `I explicitly approve running the B4 source-policy execution commands listed in B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json.`.
The narrowed archive boundary matches the reproducibility manifest: `True`.
Its status/source-policy/use/execution/exact tuple is
`narrowed_archive_ready_not_full_source_policy_runner_archive/0/40/False/False/True`,
with blocking ids/status `OC4,OC6,OC12` /
`OC4=open,OC6=partial,OC12=partial`. The current archive use is
`narrowed_claim_only`, not a full source-policy runner archive. The objective
completion blocker matrix remains
`blocker_open_by_id=OC4:True,OC6:True,OC12:True`,
`blocker_closure_decision_by_id=OC4:remain_open_ready_for_authorized_execution_not_executed_not_promoted,OC6:remain_open_no_positive_source_equivalent_artifact,OC12:remain_partial_narrowed_replay_ready_full_source_policy_archive_not_ready`,
and `blocker_closure_allowed_by_id=OC4:False,OC6:False,OC12:False`.

Dear Editor,

Please consider the manuscript `main_cmame.pdf`, titled
`A Conditional Sixth-Order Lie-Group FullVA Integrator for Lower-Pair Mechanisms`, for
review in Computer Methods in Applied Mechanics and Engineering. The paper
reports an artifact-backed integrator result for cylindrical lower-pair
mechanisms. The LaTeX source is `main_cmame.tex`, prepared with Elsevier's
`elsarticle` class, with `highlights_cmame.txt` and `declarations_cmame.md`
included as separate editable submission files.

The accepted formal-order claim is deliberately narrow. The production method
is `Gauss6/FullVA`, a conditional sixth-order Lie-group FullVA one-step
integrator under the branch, endpoint/stability, implementation-binding, and
solver-scale theorem conditions. On the
smooth cylindrical-chain benchmark, the generated evidence records observed
position/velocity orders `7.161/7.066`. The method-side dynamic-order evidence
is provided by `single_pendulum` and `double_pendulum`; `four_link` and
`slider_crank` are retained as lower-pair mechanism-coverage, constraint
closure, reaction-consistency, and coarse closed-loop diagnostic evidence
rather than standalone asymptotic dynamic-order rows. The comparator is the
local paper-style `m=3` Gauss-Lobatto TFE formula target with expected order
`5`, so the paper states a bounded formal-order comparison within the current
artifact scope, not implemented source-paper superiority.

The proof route is the direct 132-row residual-bridge/Kantorovich route. The
96 non-dynamic FullVA rows supply the \(O(h^7)\) lifted-stage defect block, and
the 36 Newton--Euler rows close with zero residual by direct substitution on
the accepted smooth branch. Endpoint/stability, implementation-binding,
solver-scale, and residual-to-error promotion clauses remain theorem-boundary
conditions and are not replaced by finite residual logs or source-policy
comparisons.

The submission does not claim complete source-paper residual reproduction. The
independent full-TFE stage replacement remains open and is recorded as
`full_tfe_stage_replacement=false`. The sparse AD speed comparison and the
practical coarse sharp-friction regime are also retained as explicit caveats.

The submission package includes:

- `main_cmame.pdf`: recommended CMAME/Elsevier manuscript;
- `main_cmame.tex`: `elsarticle` source manuscript;
- `highlights_cmame.txt`: separate editable highlights file;
- `declarations_cmame.md`: declaration statements;
- `CMAME_SUBMISSION_CHECKLIST.md`: CMAME/Elsevier format checklist;
- `SUBMISSION_PACKET.md`: submission-facing index;
- `SUBMISSION_ARTIFACT_MANIFEST.json`: machine-readable package manifest;
- `PROOF_EVIDENCE_MATRIX.md`: proof-obligation to evidence map;
- `ORDER_ACCEPTANCE_GATE.md`: example-level order boundary and no-default
  `1e-4` execution policy;
- `SOURCE_PAPER_COMPARISON.md`: source-paper versus v047 order and non-claim
  boundary;
- `CROSS_PAPER_BENCHMARK_SPEC.md` and
  `CROSS_PAPER_BENCHMARK_CASES.json`: extracted external benchmark policy and
  row-level run inventory;
- `CLAIM_BOUNDARY.json`: machine-readable claim boundary;
- `PAPER_CLAIM_LEDGER.md` and `REVIEWER_CHECKLIST.md`: supporting claim and
  review ledgers.

The package can be checked without running the full numerical generator:

```bash
../.venv_sbel/bin/python validate_cmame_submission.py
../.venv_sbel/bin/python validate_concise_paper.py
../.venv_sbel/bin/python validate_proof_evidence_matrix.py
../.venv_sbel/bin/python validate_order_acceptance_gate.py
../.venv_sbel/bin/python validate_source_paper_comparison.py
../.venv_sbel/bin/python validate_cross_paper_benchmark_spec.py
../.venv_sbel/bin/python validate_cross_paper_benchmark_cases.py
../.venv_sbel/bin/python validate_submission_bundle.py
../.venv_sbel/bin/python validate_paper_package.py
```

The broader repository gate is:

```bash
.venv_sbel/bin/python validate_pipeline_outputs.py
```

These validators read the existing artifacts and do not invoke `run_v047.py`.

Sincerely,

Jingquan Wang
