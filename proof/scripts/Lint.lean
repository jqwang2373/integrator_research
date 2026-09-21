import IntegratorOrderProof
/-!
Batteries linter over the whole library (`scripts/check.sh` runs it).  Fails the file when any
default linter (unused arguments, docstrings on definitions, simp-lemma hygiene, ...) reports.
-/
#lint in IntegratorOrderProof
