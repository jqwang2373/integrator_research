# External Superiority Claim Demotion Audit

Status: **Route B applied to the claim boundary; external superiority demoted**.

This is a claim-boundary decision, not a numerical win.

- Claim after Route B: `formal_order_and_common_reference_diagnostics_only`.
- Route B ready/promoted to blocker gate: `True/True`.
- B2/B4 gate closed by this artifact: `False`.
- B2 closed by Route B claim demotion: `True`.
- B4 closed by Route B claim demotion: `False`.
- External superiority claim allowed after Route B: `False`.
- Source-policy execution rows closed: `0/40`.
- Source-policy flagged rows: `15`.
- Current demoted suites: `['hi2022_half_implicit', 'ra2021_absolute_coordinate', 'tfe2026_original_pendulum', 'vp2024_velocity_partitioning']`.
- Additional suites to demote: `[]`.
- Full demotion scope after Route B: `['hi2022_half_implicit', 'ra2021_absolute_coordinate', 'tfe2026_original_pendulum', 'vp2024_velocity_partitioning']`.
- No default 1e-4 run was required or invoked: `True`.

## Retained Claims

- Formal order claim retained: Gauss6/FullVA order `6` versus TFE formula target `5`.
- Common-reference diagnostics retained: `44` cells, `40/40` direct nonlocal order wins, `40/40` direct nonlocal error wins.
- Source-policy external superiority remains allowed: `False`.
- Paper direct error superiority remains allowed: `False`.

## Suite Decisions

| suite | Route B decision | retained evidence | source-policy rows closed |
|---|---|---|---:|
| `vp2024_velocity_partitioning` | `already_demoted_from_external_superiority_scope` | common-reference diagnostics | `0` |
| `hi2022_half_implicit` | `already_demoted_from_external_superiority_scope` | common-reference diagnostics | `0` |
| `ra2021_absolute_coordinate` | `already_demoted_from_external_superiority_scope` | common-reference diagnostics, public baseline diagnostics | `0` |
| `tfe2026_original_pendulum` | `already_demoted_from_external_superiority_scope` | common-reference diagnostics, formal order comparator | `0` |

Route B does not create source-policy rows.  It removes RA2021/TFE/VP2024/HI2022 from any external-superiority claim and keeps their values only as bounded diagnostics or formal comparators. B4 remains open for work/precision and numerical-evidence strength.

## Route B Application Contract

This contract is the guard against partially applying Route B.

- Contract schema: `route-b-application-contract-v1`.
- Ready to promote to blocker gate now: `True`.
- Safe to flip gate flags without other edits: `False`.
- Satisfied steps: `6/6`.
- Unsatisfied steps: `[]`.
- Route B creates numerical wins: `False`.

| step | satisfied | current evidence | required before promotion |
|---|---:|---|---|
| `RB1_manuscript_claim_boundary_synchronized` | `True` | main and flat TeX contain the non-superiority and 0/40 source-policy boundary | keep the abstract, claim-boundary section, and flat submission source synchronized |
| `RB2_no_source_policy_rows_promoted_to_wins` | `True` | source-policy rows closed/external-superiority-ready remain 0/0 | do not convert common-reference rows into source-policy wins |
| `RB3_all_external_suites_demoted_in_suite_ledger` | `True` | currently demoted suites are ['hi2022_half_implicit', 'ra2021_absolute_coordinate', 'tfe2026_original_pendulum', 'vp2024_velocity_partitioning'] | keep all external suites in the explicit demotion ledger unless a new source-policy evidence route is opened |
| `RB4_b2_remaining_manifest_has_no_active_external_rows` | `True` | active flagged rows/suites are 0/{} | keep B2 active rows at zero; reopen only with new public/source-code-equivalent evidence or an authorized source-policy execution route |
| `RB5_blocker_gate_and_validators_synchronized` | `True` | B2/B4 statuses are closed/closed; Route B closes the external-superiority claim gate only; B4 is closed separately by the narrowed-claim policy, with source-policy work/precision retained as future work | keep CMAME_BLOCKER_CLOSURE_GATE and read-only validators synchronized with Route B claim demotion |
| `RB6_downstream_reports_synchronized` | `True` | review/objective/PDF-style reports read source-policy rows as demoted diagnostics and do not list them as the first closeout gate | regenerate review agent, objective audit, PDF-style audit, reproducibility manifests, and package validators after any future claim-boundary edit |
