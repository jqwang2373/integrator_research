# Folder Cleanup Plan

This plan separates safe organization from path-breaking refactors. The current
tree is validator-heavy, so the first cleanup pass should improve navigation
without moving required artifacts.

## Done In This Pass

- Added root workspace `README.md`.
- Added this cleanup plan.
- Added `FOLDER_MAP.md` for the research tree.

## Safe Immediate Cleanup

These actions should not change research evidence:

1. Remove Python cache directories after a validation pass:
   - `lie_group_integrator_work/__pycache__/`
   - `lie_group_integrator_work/v*/__pycache__/`
   - `lie_group_integrator_work/paper_v047_cylindrical_chain/__pycache__/`
2. Keep root reference PDFs and extracted text in place until source-paper
   validators are checked against any proposed new location.
3. Keep generated `results/` files inside their version directories.
4. Use `FOLDER_MAP.md` as the entry point instead of opening many ledgers at
   once.

## Needs A Dedicated Refactor

These changes can make the tree cleaner but require validator/source updates:

| Candidate change | Risk | Required follow-up |
| --- | --- | --- |
| Move root PDFs into a `literature/` directory. | Medium | Update source-paper comparison paths and any scripts that read `../*.pdf`. |
| Move old audit markdown in `paper_v047_cylindrical_chain/` into an `audits/` subdirectory. | High | Update validators, manuscript references, JSON source files, and submission inventory. |
| Move paper-generated submission files into a single `submission/` tree. | High | Update CMAME validators and flat-submission package builder. |
| Archive older `v001`-`v045` directories under `versions/`. | Very high | Update all ledger links, validators, progression scripts, and report references. |
| Rename or regroup v047/v048 artifacts. | Very high | Breaks current pipeline contract unless all gate files are patched together. |

## Recommended Next Pass

1. Run read-only validators to confirm this documentation-only pass did not
   affect gates.
2. Optionally remove `__pycache__/` directories.
3. Build a machine-readable path dependency report before any directory move.
4. If moving root PDFs, start with a small compatibility layer: copy or symlink
   into `literature/`, then update validators one at a time.

## Do Not Do During Routine Cleanup

- Do not run `v047_cylindrical_chain_pipeline/run_v047.py` just to check folder
  state.
- Do not make strict public-policy `1e-4` rows part of default cleanup checks.
- Do not promote `full_tfe_stage_replacement`, external superiority, or
  submission readiness while their gates remain open.
