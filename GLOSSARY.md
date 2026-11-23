# Civic Service Requests

One domain data product that publishes NYC 311 service requests for analysis. This glossary fixes the words used for landing source data.

## Language

**Batch**:
The bounded slice of source data requested, identified by a created-date window.
_Avoid_: Extract, load, pull

**Run**:
One attempt to land a batch, identified by a unique run ID. Several runs can target the same batch, and each keeps its own raw pages and manifest.
_Avoid_: Job, execution, extract

**Manifest**:
The record of what a run requested and received. It is written last, so its presence marks the run complete.
_Avoid_: Receipt, metadata file

**Complete run**:
A run whose pages were all written and recorded in a manifest. Only complete runs are read downstream.
_Avoid_: Successful run, finished run

**Incomplete run**:
A run with no manifest, usually because it stopped part-way. Downstream ignores it; its pages are kept for debugging.
_Avoid_: Failed run, partial run

**Latest complete run**:
For a given request, the complete run with the most recent retrieval time. Its version of the request replaces earlier ones, so a rerun picks up source corrections.
_Avoid_: Current run, newest run
