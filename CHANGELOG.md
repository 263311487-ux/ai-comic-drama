# Changelog

## 1.7.0

Added security reporting and contributor conduct policies for safe community reuse. No runtime API changes.

## 1.6.0

Added structured issue templates for bugs, feature requests, and provider adapters, plus a pull-request checklist. No runtime API changes.

## 1.5.0

Extended CI to run strict manifest validation, offline doctor checks, and the one-command quickstart. No provider API changes.

## 1.4.0

Added strict manifest validation for production handoff fields and release metadata. The default validator remains backward compatible.

## 1.3.1

Made the environment doctor return a nonzero exit code when offline readiness or workdir write access is unavailable. No provider API changes.

## 1.3.0

Added `scripts/doctor.py` for offline environment diagnostics and optional provider/encoder availability checks. No paid calls are made.

## 1.2.0

Added `scripts/init_manifest.py` to scaffold an editable episode contract. No provider API changes.

## 1.1.1

Improved the quickstart artifact index and added regression coverage for the one-command workflow. No provider API changes.

## 1.1.0

Added `scripts/quickstart.py`, a one-command offline first-success workflow with an artifact index. No provider API is called.

## 1.0.6

Aligned the skill entrypoint version and release-boundary wording with the current public line. No runtime API changes.

## 1.0.5

Aligned citation metadata with the current public release line. No runtime API changes.

## 1.0.4

Aligned the skill entrypoint version and title with the current public release line. No runtime API changes.

## 1.0.3

Added standard citation metadata and an example workflow guide for reuse and indexing. No runtime API changes.

## 1.0.2

Improved skill discovery metadata, invocation copy, and README search keywords. No runtime API changes.

## 1.0.1

Refreshed public README positioning, installation guidance, and CI/release badges. No runtime API changes.

## 0.5.0

Added provider-neutral SRT generation and encoder-independent assembly plans.

## 0.6.0

Added optional ffmpeg encoding and disposable local fixture generation for offline media tests.

## 1.0.0

Added a provider-neutral content review record and CLI, with explicit PASS/PENDING/FAIL states before publish approval.

## 0.9.0

Added required release metadata, separate publish approval records, and approval invalidation when the content review report changes.

## 0.8.0

Separated technical readiness from content review and human publish approval. Delivery manifests now refuse to claim READY_FOR_PUBLISH without explicit approval.

## 0.7.0

Added an offline delivery gate that runs fixture generation, assembly, encoding, subtitles, and technical QA in one reproducible command.

## 0.3.0

Added an explicit Seedance CLI adapter and network-free command planning. Submission remains opt-in.

## 0.2.0

Added a dependency-free MockProvider, resumable shot runner, per-shot and episode budget gates, and provider contract implementation.

## 0.1.1-preview

Corrected preview scope and offline CI.
