# v041 Triple Pattern Cache Refresh

This version follows v040.

v040 showed that triple-revolute sparse patterns can be obtained from a
generated block superset instead of a full dense superset. v041 turns that into
a cache policy: discover once, scan future trajectories inside the generated
block superset, union any new active entries, and then solve with the refreshed
cache.

Run:

```bash
../.venv_sbel/bin/python run_v041.py
```

Main outputs:

- `results/v041_report.md`
- `results/summary_v041.json`
- `results/triple_pattern_cache_refresh_runs.csv`
- `results/triple_pattern_cache_refresh_runtime.png`
- `results/triple_pattern_cache_refresh_patterns.png`
