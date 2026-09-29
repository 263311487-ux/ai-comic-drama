# AI Comic Drama — Preview

An early Agent Skill for planning comic-drama production. **This release is a planning prototype with an offline mock runner, not an end-to-end video generator.**

## Available now

- Offline shot-manifest checks.
- Text storyboard HTML (not a visual animatic).
- Cost estimates using user-supplied per-second rates.
- Unreviewed QA checklist creation (not automated video review).

## Offline runner

The mock provider exercises resumable state, shot-level attempts, and episode budgets without network access:

```sh
python3 scripts/run_mock.py examples/episode.json --state work/run_state.json
```

## Seedance plan (explicit opt-in)

The adapter can inspect capabilities and construct a command without submitting. `--execute` is required for network generation; never use it without a provider budget and user approval.

```sh
python3 scripts/seedance_plan.py examples/episode.json --shot S01
```

## Subtitles and assembly plan

Generate an SRT and an encoder-independent clip plan without media encoding:

```sh
python3 scripts/make_srt.py examples/episode.json --out work/episode.srt
python3 scripts/assemble_plan.py examples/episode.json --out work/assembly.json
```

The plan is blocked until every expected shot file exists. It does not claim that a video was assembled.

## Not yet integrated

Video provider execution, resumable production, audio/subtitle assembly, and validated end-to-end delivery gates. Legacy gate scripts are experimental and use a different manifest contract. Do not use them to certify release readiness.

## Offline quick start

```sh
python3 scripts/validate_manifest.py examples/episode.json
python3 scripts/previz.py examples/episode.json --out work/previz.html
python3 scripts/estimate_cost.py examples/episode.json --rate 0.35 --pass-rate 0.65 --versions 3
python3 scripts/qa_report.py --manifest examples/episode.json --out work/qa.json
python3 -m unittest discover -s tests
```

`--rate` means currency units per generated second. Estimates exclude image, audio, tax and provider-specific charges. Keyword scanning does not establish platform compliance.

## Installation

Copy the complete repository into your agent's skill directory. Entry point: `SKILL.md`. Python 3.11+; the offline commands use the standard library.

## License

Apache-2.0; see LICENSE. No third-party director skill or proprietary media is bundled.
