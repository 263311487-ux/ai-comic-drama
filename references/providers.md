# Provider adapter contract

The core contract is implemented in `ai_comic_drama/providers.py`. An adapter exposes `capabilities()`, `estimate(manifest)`, `submit_shot(shot, run_id)`, and `poll(job_id)`. The runner persists state after every shot in JSON and enforces `budget.max_attempts` and `budget.max_shot_attempts`.

Use idempotent run IDs, preserve provider evidence and timestamps, retry rate limits with backoff, stop at the manifest budget, and never print credentials. Planning and QA work offline without an adapter. The bundled MockProvider is the only fully runnable adapter in this release.
