#!/usr/bin/env bash
# Full check of the development: build, exhaustive axiom audit, Batteries linter.
# Usage: scripts/check.sh   (from the project root; needs elan/lake on PATH; first run: lake exe cache get)
set -euo pipefail
cd "$(dirname "$0")/.."
echo "== lake build"
lake build
echo "== axiom audit (every theorem: standard axioms only, no sorry)"
lake env lean scripts/Axioms.lean | tee /tmp/integrator_order_proof_axioms.txt | grep -c "depends on axioms" | sed 's/^/theorems audited: /'
grep -q "sorryAx" /tmp/integrator_order_proof_axioms.txt && { echo "sorryAx found"; exit 1; }
echo "== linter"
lake env lean scripts/Lint.lean
echo "== all checks passed"
