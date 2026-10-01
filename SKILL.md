---
name: ai-comic-drama
description: "Manifest-first Codex Agent Skill for AI comic-drama production: shot planning, provider-neutral generation plans, cost gates, subtitles, assembly, technical QA, and auditable human review. Use when turning a script or shot list into a reproducible comic-drama production workflow; paid provider execution remains explicit opt-in."
metadata:
  version: 1.6.0
---
# AI Comic Drama

Read README.md for executable commands and current limitations. Develop an approved script into shots with purpose, visible action, camera, dialogue and end state. Preserve the user's genre, duration, language and audio preferences.

Run scripts/validate_manifest.py on the example contract. Use scripts/run_mock.py to exercise the offline resumable runner and budget gates. Use scripts/seedance_plan.py only to inspect an explicit Seedance command; `--execute` is required before any network submission. Use scripts/make_srt.py and scripts/assemble_plan.py for provider-neutral subtitle and assembly planning. Use scripts/previz.py for a text storyboard, scripts/estimate_cost.py for per-second cost estimates, and scripts/qa_report.py for an unreviewed checklist. These commands do not invoke providers.

For a first successful offline run, use `python3 scripts/quickstart.py`. It writes a reproducible artifact index under `work/quickstart/` without contacting a paid provider.
For a new episode, start with `python3 scripts/init_manifest.py --out work/episode.json --title "..."`, fill the required fields, then validate.
If installation is uncertain, run `python3 scripts/doctor.py`; it reports offline readiness and optional encoder/provider CLI availability without making paid calls.
Use `scripts/validate_manifest.py --strict` before a production handoff to require release metadata and complete shot fields.

Keyword checks cannot certify compliance. Unreviewed reports cannot certify content. Legacy narrative, technical and delivery scripts remain experimental and are not integrated with this example schema. Never describe this skill as an end-to-end generator or declare content publishable based on a successful command.

The offline MockProvider and resumable runner are implemented in `ai_comic_drama/`. Real provider adapters remain opt-in and must follow references/providers.md.
