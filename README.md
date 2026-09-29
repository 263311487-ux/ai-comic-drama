# AI Comic Drama Skill

Manifest-first automation for repeatable AI comic-drama production: validate a shot list, estimate cost, preview continuity, route to a provider, assemble subtitles, run frame and technical QA, and produce a delivery manifest.

[![CI](https://github.com/263311487-ux/ai-comic-drama/actions/workflows/ci.yml/badge.svg)](https://github.com/263311487-ux/ai-comic-drama/actions/workflows/ci.yml)
[![GitHub stars](https://img.shields.io/github/stars/263311487-ux/ai-comic-drama?style=social)](https://github.com/263311487-ux/ai-comic-drama/stargazers)

This is an Agent Skill, not a hosted video service. Story decisions, provider execution, and release evidence remain separate.

## Quick start (offline)

    python3 scripts/validate_manifest.py examples/episode.json
    python3 scripts/check_compliance.py examples/episode.json
    python3 scripts/previz.py examples/episode.json --out work/previz.html
    python3 scripts/estimate_cost.py examples/episode.json --rate 0.35 --pass-rate 0.65 --versions 3
    python3 scripts/qa_report.py --manifest examples/episode.json --out work/qa.json

These commands do not call a paid provider.

## Install

Clone the repository into your Agent Skills directory, or use an Agent Skills installer that accepts GitHub repositories. The entrypoint is `SKILL.md`.

## License

Apache-2.0.
