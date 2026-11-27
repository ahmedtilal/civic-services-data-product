# 0001. Run completeness and reconciliation

Status: accepted (part 3)

## Context

Landing reads a live source in pages. The source can change while a run is paging, a run can stop part-way, and the same batch is landed more than once. Downstream stages need a simple rule for which raw data is safe to read, and landing must not fail for reasons outside its control.

## Decision

- **Manifest last.** A run writes its pages, then its manifest. The manifest's presence marks a **complete run**; a run without one is an **incomplete run**. The local store writes the manifest atomically (temporary file, then rename).
- **Source count is recorded, not enforced.** The manifest stores the source's own count for the window as an observation. A mismatch does not fail the run, because the live source can change between the count and the pages.
- **Duplicates are counted.** The manifest records how many surplus `unique_key` occurrences appeared across pages (a key seen three times counts as 2), which makes paging instability visible. Rows skipped at page boundaries cannot be counted; they are possible, and a later run of the same batch can pick them up.
- **Latest complete run wins.** For a batch, downstream reads the complete run with the most recent retrieval time, so a rerun's corrected data replaces earlier data.
- **Incomplete runs are kept and ignored.** Their pages stay on disk for debugging and are never read downstream or cleaned up automatically.
- **No resume.** A page that still fails after its retries (default 0) stops the run. A new run replaces it, so a run never mixes retrieval times.
- **Reruns never overwrite.** Each run has its own run ID and files; completed runs stay immutable.

## Consequences

- Landing is not a transactional snapshot of the source. Freshness and completeness claims must say so.
- Raw storage grows with each rerun. Cleanup is a later, deliberate decision.
- Part 4 builds the merge by `request_id` on top of the latest-complete-run lookup.
