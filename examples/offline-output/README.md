# Synthetic offline example — The Signal

Captured on 2026-10-08 by running `python3 scripts/quickstart.py` against `examples/episode.json`. This is synthetic planning data, not AI-generated footage. No provider was contacted.

| Output | What to inspect |
|---|---|
| [Text storyboard](previz.html) | S01 = 5 seconds; S02 = 6 seconds; planned action, camera and end state |
| [Subtitles](episode.srt) | One Chinese dialogue cue in the first shot |
| [Assembly plan](assembly.json) | `blocked`, with S01 and S02 missing: no media created by the mock |
| [Content review](qa_result.json) | `PENDING_HUMAN_REVIEW`, both shots unreviewed, no publish approval |

The HTML is a text table, not a visual animatic. The committed files are the actual command outputs; `created_at` is a capture timestamp, not a promise of byte-for-byte reproducibility. The full local index and mock state contain machine paths/timestamps and are intentionally regenerated rather than committed.

To reproduce, run the quickstart from the repository root. To exercise encoding separately, install ffmpeg/ffprobe and run `python3 scripts/offline_delivery.py examples/episode.json --out work/delivery`. The current synthetic color/tone fixtures yield a technical PASS with `black_frame_detected_needs_review`; this warning remains reviewable. Content remains pending and platform compliance remains `REVIEW_REQUIRED`. Technical PASS does not authorize publishing.
