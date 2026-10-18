# Series Roadmap

Each installment leaves the repository in a usable checkpoint that the next one extends.

| Part | Outcome | Repository change |
|---|---|---|
| 1. Design the first data product | Choose NYC 311, define the input, intermediate, and output boundaries, and set a small draft contract. | This scaffold, `product.yaml`, and the architecture and contract docs. |
| 2. Lay the low-cost GCP foundation | Configure one project, London locations, scoped runtime identity, budget alerts, Terraform, and the container/job skeleton. | Add reviewed Terraform resources and build/deployment configuration. |
| 3. Explore the source | Profile a bounded multi-day NYC 311 sample, types, nulls, and approximate batch volume. | Add a reproducible marimo notebook and record observed counts and extract size. |
| 4. Land source data safely | Fetch ordered CSV pages, retain source bytes in GCS, and write a run manifest. | Implement `civic-data land-raw` with Pydantic models and a Masoora pipeline. |
| 5. Build the intermediate layer | Validate and normalize records, report rejects, and make the BigQuery write retry-safe. | Implement `build-intermediate` and the staging schema. |
| 6. Publish a stable output port | Add quality assertions and publish the documented BigQuery output. | Implement `publish-product` and a consumer query. |
| 7. Schedule, observe, and debug | Schedule the daily job, inspect a failed run, and recover it. | Add the Cloud Run Job schedule, logs, alerts, and optional Grafana instructions. |
| 8. Review the platform | Compare measured costs and behavior with assumptions, recap limits, and identify extensions. | Update observed costs and decisions; keep Iceberg and a catalog as later work. |

The first series ends with one reliable, observable data product. A second format, Iceberg, catalog, and warehouse are extensions rather than prerequisites.
