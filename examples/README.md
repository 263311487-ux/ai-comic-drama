# Example workflow

The example manifest is intentionally small so it can run offline in CI and on a new machine.

```sh
python3 scripts/validate_manifest.py examples/episode.json
python3 scripts/run_mock.py examples/episode.json --state work/run_state.json
python3 scripts/make_srt.py examples/episode.json --out work/episode.srt
python3 scripts/assemble_plan.py examples/episode.json --out work/assembly.json
```

For a disposable local media check, run `scripts/offline_delivery.py`. It creates temporary fixture media and reports technical QA; it does not claim content or platform approval.

To adapt the example, preserve the manifest contract in [`references/manifest-schema.md`](../references/manifest-schema.md), then replace the mock provider with an explicitly approved provider adapter.
