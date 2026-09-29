---
name: ai-comic-drama
description: Prepare shot manifests, text storyboard previews, cost estimates and review checklists for AI comic-drama production. Use for preproduction planning; this preview does not generate or assemble video.
metadata:
  version: 0.8.0
---
# AI Comic Drama — Planning Preview

Read README.md for executable commands and current limitations. Develop an approved script into shots with purpose, visible action, camera, dialogue and end state. Preserve the user's genre, duration, language and audio preferences.

Run scripts/validate_manifest.py on the example contract. Use scripts/run_mock.py to exercise the offline resumable runner and budget gates. Use scripts/seedance_plan.py only to inspect an explicit Seedance command; `--execute` is required before any network submission. Use scripts/make_srt.py and scripts/assemble_plan.py for provider-neutral subtitle and assembly planning. Use scripts/previz.py for a text storyboard, scripts/estimate_cost.py for per-second cost estimates, and scripts/qa_report.py for an unreviewed checklist. These commands do not invoke providers.

Keyword checks cannot certify compliance. Unreviewed reports cannot certify content. Legacy narrative, technical and delivery scripts remain experimental and are not integrated with this example schema. Never describe this preview as an end-to-end generator or declare content publishable based on a successful command.

The offline MockProvider and resumable runner are implemented in `ai_comic_drama/`. Real provider adapters remain opt-in and must follow references/providers.md.
