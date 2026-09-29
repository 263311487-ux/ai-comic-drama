# Mock provider

The mock adapter is offline and deterministic. It exercises manifest routing, resumable state, per-shot retry limits, and episode attempt budgets without generating media or spending credits.

```sh
python3 scripts/run_mock.py examples/episode.json --state work/run_state.json
python3 scripts/run_mock.py examples/episode.json --dry-run
```
