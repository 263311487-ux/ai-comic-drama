# Manifest contract

The repository uses one JSON manifest per episode. It is the source of truth for validation, planning, subtitles, QA, and delivery.

## Required public shape

The top level requires `schema_version`, `episode_id`, `title`, `ratio`, `delivery`, `provider`, `budget`, and `shots`. Each shot requires stable `id`, positive `duration`, `purpose`, `action`, `camera`, and `end_state`. Valid ratios are `9:16`, `16:9`, `1:1`, and `21:9`.

Use `validate_manifest.py --strict` before a production handoff. Strict mode additionally requires non-empty `release_metadata.platform`, `ai_disclosure`, `copyright_basis`, `cover`, and `description`.

`assets.characters` and `assets.scenes` may contain stable IDs referenced by shot `roles` and `scene`. `continuity_from` must point to an earlier shot ID; run `scripts/continuity_check.py --json` to verify links and asset references.

Optional shot fields include `dialogue`, `text`, `speaker`, `audio_policy`, `prompt`, and `ratio`. Keep one visible action per shot so providers can generate and reviewers can diagnose it.

Older private production manifests may use aliases such as `dur`, `img`, `motion`, or a top-level `scenes` map. Convert them into this public contract before running repository scripts.
