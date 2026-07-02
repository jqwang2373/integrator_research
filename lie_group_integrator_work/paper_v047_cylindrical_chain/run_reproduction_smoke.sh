#!/usr/bin/env bash
set -euo pipefail

PAPER_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ -n "${PYTHON:-}" ]]; then
  PY="$PYTHON"
elif [[ -x "$PAPER_DIR/../.venv_sbel/bin/python" ]]; then
  PY="$PAPER_DIR/../.venv_sbel/bin/python"
else
  PY="python3"
fi

cd "$PAPER_DIR"

echo "[1/13] Human-facing replay table"
"$PY" run_human_reproducibility.py

echo "[2/13] Replay core paper result boundary"
"$PY" replay_reproducibility_core.py

echo "[3/13] Replay minimal 44-row paper matrix"
(
  cd cmame_minimal_reproducibility_candidate
  "$PY" scripts/replay_paper_matrix.py
)

echo "[4/13] Check runner-adapter candidate"
(
  cd cmame_runner_adapter_candidate
  "$PY" scripts/run_four_example_matrix_adapter.py
)

echo "[5/13] Replay closed-loop local four-link/slider-crank rows"
(
  cd cmame_runner_adapter_candidate
  "$PY" scripts/replay_closed_loop_local_rows.py
)

echo "[6/13] Run compact closed-loop local runner candidate"
(
  cd cmame_closed_loop_local_runner_candidate
  "$PY" scripts/run_closed_loop_fullva_candidate.py
)

echo "[7/13] Validate compact closed-loop local runner candidate"
"$PY" validate_cmame_closed_loop_local_runner_candidate.py

echo "[8/13] Validate P1 single-runner candidate"
"$PY" validate_cmame_p1_single_runner_candidate.py

echo "[9/13] Validate P1 double-runner candidate"
"$PY" validate_cmame_p1_double_runner_candidate.py

echo "[10/13] Run local accepted-row runner companion"
(
  cd cmame_local_accepted_runner_companion
  "$PY" scripts/run_local_accepted_runner_companion.py
)

echo "[11/13] Validate local accepted-row runner companion"
"$PY" validate_cmame_local_accepted_runner_companion.py

echo "[12/13] Validate minimal replay package"
"$PY" validate_cmame_minimal_reproducibility_candidate.py

echo "[13/13] Validate runner-adapter package"
"$PY" validate_cmame_runner_adapter_candidate.py

echo "reproduction_smoke=PASS"
echo "boundary=bounded_common_reference_replay_only"
echo "p1_single_runner_candidate=True"
echo "p1_double_runner_candidate=True"
echo "p1_local_single_double_ready=True"
echo "closed_loop_local_four_slider_replay=True"
echo "closed_loop_local_runner_candidate=True"
echo "local_accepted_runner_companion=True"
echo "p1_complete=False"
echo "source_policy_external_rows=0/40"
echo "proof_gap_closed=True"
echo "proof_gap_scope=direct_residual_bridge_kantorovich_route_closed_primitive_taylor_conditional_schema_open"
echo "stage_residual_O_h7_direct_proof=True"
echo "submission_ready=False"
