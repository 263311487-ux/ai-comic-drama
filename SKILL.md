---
name: ai-comic-drama
metadata:
  version: 0.1.0
  short-description: Manifest-first AI comic-drama production
  author: 263311487-ux
description: Plan, validate, produce, assemble, and quality-check AI comic-drama episodes from an approved script or storyboard manifest. Use for repeatable production, provider routing, shot repair, subtitles, technical delivery gates, and cost controls.
---
# AI Comic Drama Automation

This skill turns an approved script and shot manifest into a reproducible episode package. It separates story decisions from generation execution and keeps paid/provider-specific actions behind an explicit adapter and budget gate.

Workflow: script -> manifest -> validate -> compliance -> previz -> assets -> audio -> keyframes -> video -> assemble -> frame QA -> technical QA -> delivery.

Run offline checks with scripts/validate_manifest.py, scripts/check_compliance.py, scripts/previz.py, scripts/estimate_cost.py, and scripts/qa_report.py. Read references/providers.md for adapters and references/release-checklist.md before publishing.

Do not claim viral, cinematic, consistent, or publish-ready from API success alone. Do not submit paid generation without an estimate and explicit user approval. Never embed private names, account IDs, keys, or billing assumptions in reusable resources.
