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

For local encoder testing, generate disposable fixtures with `python3 scripts/fixture_episode.py --manifest examples/episode.json --out work/fixture`; fixture media is intentionally not committed.

Run the full offline delivery gate with `python3 scripts/offline_delivery.py examples/episode.json --out work/delivery`. It creates disposable shots, an assembly plan, a master MP4, SRT, and technical QA. A PASS is technical evidence only; it is not a story or platform approval.

## Human content review and publish approval

Record an actual human review in `qa_result.json` (repeat `--shot` for each reviewed shot):

```sh
python3 scripts/record_content_review.py --out work/delivery/qa_result.json --status PASS --reviewer "Name" --basis "All shots reviewed" --shot S01 --shot S02
```

Use `PENDING_HUMAN_REVIEW` until review is complete, or `FAIL` when it fails. This records the review; it does not inspect video or grant publish approval. Only after content review PASS and independently verified compliance PASS may an authorized publisher create the separate, hash-bound approval:

```sh
python3 scripts/approve_publish.py --qa work/delivery/qa_result.json --approved-by "Publisher" --basis "Release approved"
```

Changing `qa_result.json` after approval invalidates that approval. The delivery manifest also requires technical QA PASS, compliance PASS, release metadata, subtitles, content review PASS, and separate human publish approval.

## Current boundaries

The Seedance adapter requires explicit execution opt-in; this repository does not claim automated story review or platform approval. Legacy narrative and compliance keyword gates are advisory and use a different manifest contract. Do not use them to certify release readiness.

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

Delivery status is intentionally staged: technical PASS does not equal content approval or publish approval.
