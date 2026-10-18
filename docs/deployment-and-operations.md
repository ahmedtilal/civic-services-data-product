# Deployment and Operations

## GCP foundation

The planned first deployment uses one GCP project and the London region, `europe-west2`, for the Cloud Run Job, raw Cloud Storage bucket, and BigQuery datasets. Terraform will manage the bucket, `civic_services_staging` and `civic_services_products` datasets, runtime service account, Artifact Registry repository, required APIs, and budget alert.

Do not place project IDs, billing account IDs, or user-specific email addresses in tracked configuration. Review `terraform plan` before applying. The Terraform state file records real resource identifiers and must remain out of Git.

## Identity and secrets

- Use Application Default Credentials for local Terraform and data access.
- Give the Cloud Run Job a dedicated service account. Scope bucket and BigQuery access to the individual resources where possible.
- The runtime must not use a broad project Editor role or a downloaded service-account key.
- Keep an optional Socrata application token in a local secret manager or environment variable. Do not commit it or log it.
- Avoid logging raw 311 records. Log run IDs, requested bounds, counts, duration, and outcome.

## Batch behavior

A run gets a unique run ID and reads a bounded date window. Fetch all requested pages before writing objects. Store each original response page separately with a checksum and row count. Write the manifest only after every page upload succeeds; downstream stages ignore prefixes without a manifest.

The live NYC dataset can change while it is fetched and can revise older records. The first tutorial demonstrates a repeatable bounded batch, not a complete change-data capture strategy or freshness guarantee. Reconcile source changes before scheduling a freshness SLA.

Make storage and BigQuery writes safe to retry. Cloud Scheduler delivery is at least once, so a duplicate trigger must not duplicate consumer records. Give Cloud Run bounded retries and a timeout.

## Cost controls

The architecture document estimates roughly **$0.20/month** for the first small batch if raw storage stays within 10 GiB, BigQuery storage within 10 GiB, scans within the monthly 1 TiB free allowance, and other free allowances remain available. These are approximate USD list-price estimates from the workspace architecture, checked in October 2026; free allowances are shared across a billing account and actual charges can be higher.

Use a monthly Cloud Billing budget with warning thresholds at $5 and $10. Budget alerts notify; they do not stop spending. Apply a BigQuery maximum-bytes-billed to tutorial queries, keep the bucket and datasets co-located, retain only useful replay history, and review actual billing after runs.

Cloud Logging and Cloud Monitoring remain the operational backends. Grafana Cloud may be added as an optional UI without forwarding telemetry. Keep Knowledge Catalog, Iceberg, Dataflow, Composer, GKE, Cloud NAT, and a cross-domain warehouse deferred until a later episode demonstrates a need.
