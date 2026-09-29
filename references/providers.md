# Provider adapter contract

Expose capabilities(), estimate(manifest), submit_shot(), poll(), download(), and repair(). Use idempotent run IDs, preserve provider evidence and timestamps, retry rate limits with backoff, stop at the manifest budget, and never print credentials. Planning and QA work offline without an adapter.
