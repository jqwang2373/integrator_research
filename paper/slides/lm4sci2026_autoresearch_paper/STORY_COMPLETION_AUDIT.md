# Story Pipeline Completion Audit

This audit checks the user-requested story pipeline as an
integrator-discovery-method narrative, not submission readiness, not a paper
mainly describing the final integrator, and not completion of the underlying
numerical research pipeline.

## Scope

The requested story order is:

1. Explain why Lie-group constrained integrator discovery is hard.
2. Explain what prior/inherited work already existed and what each part did.
3. Explain how the verifier/research environment was set up.
4. Explain the four numerical examples as a test environment.
5. Explain how the work evolved into 48 versions.
6. Explain what all 48 versions mean.
7. Explain which technical turn produced the discovered integrator.
8. Explain the general discovery-method lesson: verifier-centered traces make
   integrator discovery auditable.
9. Keep the final claim boundary explicit while repeating/optimizing the story.

## Verdict

Status: achieved for the story-pipeline objective.

The current manuscript and control documents now tell the story in the
requested order. The paper is framed as a verifier-centered method for
discovering new integrators, not as automatic paper writing and not as a paper
mainly describing the final integrator. The root control file also includes a
repeated optimization loop so future shortening or template conversion can
preserve the same discovery chain.

This verdict does not mean:

- the paper is submission-ready;
- the paper is mainly a standalone description of the final integrator;
- all underlying numerical validation gates are complete;
- four-link or slider-crank have accepted asymptotic dynamic-order rows;
- full source-paper TFE replacement, sparse speed superiority, or external
  superiority is claimed.

## Requirement Evidence

| Requirement | Current authoritative evidence | Status |
| --- | --- | --- |
| Hard Lie-group integrator target | `main.tex:60-64` and `main.txt:6-8` open with manifold kinematics, index-3 constrained dynamics, lower-pair multipliers/friction, residual rows, endpoint repair, comparison policy, and one-step-map drift. `main.tex:89-100` and `main.txt:24-29` expand why the method is more than an update formula. `STORY_PIPELINE.md:53` records this as the first canonical story pass. | Proven. |
| Prior/inherited work and what it did | `main.tex:112-118`, `main.tex:176-185`, and `main.txt:77-86` describe inherited Lie kinematics, Gauss mechanics, ASME mechanisms, trapezoidal/BDF/Lobatto, TFE, friction, sparse/backend probes, and external harnesses as typed verifier questions, not a leaderboard. `DETAILED_DISCOVERY_STORY_PIPELINE_CN.md:96-135` gives the same prior-work role map in detail. | Proven. |
| Verifier/research environment setup | `main.tex:304-310` introduces MethodSpec, ProblemSpec, EvidenceSpec, ClaimSpec, ledgers, and typed next constraints before the examples. `main.tex:437-549` and `main.txt:252-309` define claim promotion checks, durable objects, verdict-to-next-constraint translation, sandbox levels, and claim states. `STORY_PIPELINE.md:142-181` provides the root environment contract. | Proven. |
| Four numerical examples as test environment | `main.tex:70-73`, `main.tex:126-129`, `main.tex:312-321`, and `main.txt:163-171` present the examples as an ordered ambiguity ladder: single pendulum and double pendulum are dynamic-order gates; four-link and slider-crank are coverage and reaction-consistency gates. `main.tex:638-708` and `main.txt:371-424` give the verifier ladder and claim boundary. | Proven. |
| Evolution to 48 versions | `main.tex:130-139` gives the five-block narrowing chain. `main.tex:323-340` and `main.txt:173-179` define a version as a state transition with candidate explanation, artifacts, verifier verdict, next constraint, and claim-state movement. `STORY_PIPELINE.md:57`, `STORY_PIPELINE.md:246-260`, and `48_VERSION_STORY_MAP_CN.md:107-125` provide reusable compressed forms. | Proven. |
| What all 48 versions mean | `main.tex:340-414` gives the discovery-spine figure and A-I role-coded table. `main.tex:784-1041` gives an expanded v001-v048 ledger, and `rg -n -F "\\paragraph{v" main.tex` confirms entries v001 through v048. `48_VERSION_STORY_MAP_CN.md:223-270` gives a version-by-version Chinese story map. | Proven. |
| Discovered-integrator technical turn | `main.tex:419-432`, `main.tex:561-612`, and `main.txt:320-329` explain the v023-v029 FullVA hinge: Lobatto node replacement and projection are rejected; stage-level lower-pair velocity/acceleration rows enter the same Gauss6 residual and survive off-axis/interbody checks. `STORY_PIPELINE.md:281-292` states the same three-gate reading. | Proven. |
| Discovery-method positioning | `main.tex` title, abstract, introduction contribution list, and conclusion now frame the paper as a verifier-centered method for discovering new integrators; `STORY_PIPELINE.md`, `ARGUMENT_BLUEPRINT.md`, `REVIEWER_STORY_QA.md`, `MAIN_TEXT_COMPRESSION_BLUEPRINT.md`, and `LM4SCI_DISCOVERY_REWRITE_PACKET.md` now state that `Gauss6/FullVA` is the bounded discovered outcome, not the sole subject of the paper. | Proven. |
| Claim boundary and nonclaims | `main.tex:696-710`, `main.tex:741-767`, and `main.txt:416-424` separate accepted, open, and unpromoted claims. `STORY_PIPELINE.md:296-317` records accepted local claim and open/forbidden claims. The boundary excludes full TFE replacement, sparse speed superiority, external superiority, seventh-order theorem, and all-four dynamic order. | Proven. |
| Repeated optimization support | `STORY_PIPELINE.md:45-63` defines the canonical story pass, and `STORY_PIPELINE.md:365-379` defines the repeated optimization loop. `STORY_REFINEMENT_AUDIT.md:93-97` names these as the root control points for future rewrites. | Proven. |

## Verification Commands

Current verification used:

```bash
cmd.exe /c pdflatex -interaction=nonstopmode main.tex
cmd.exe /c pdflatex -interaction=nonstopmode main.tex
cmd.exe /c pdftotext -layout main.pdf main.txt
cmd.exe /c pdfinfo main.pdf
rg -n "Warning|Undefined|Rerun|Overfull" main.log
rg conflict-marker scan over the story files
rg overclaim-phrase scan over the manuscript and story files
```

Observed state:

- `main.pdf` builds successfully and has 14 pages.
- `main.txt` is extracted from the current PDF.
- No conflict markers are present in the story files.
- The log scan only matches the `rerunfilecheck` package name, not an active
  rerun request, undefined reference, or overfull-box error.
- Risky terms found by the overclaim scan occur in guardrail contexts such as
  "do not say", "not accepted", "open", or "unpromoted".

## Remaining Non-Goals

The story-pipeline objective is complete, but separate work would be needed for
any of the following:

- compressing the manuscript to a strict 8-page workshop version;
- critical submission-readiness review against a target/reference PDF;
- closing pending numerical gates in the underlying v047/v048 research
  pipeline;
- promoting external source-policy superiority, sparse speed superiority, full
  TFE replacement, or all-four dynamic-order claims.
