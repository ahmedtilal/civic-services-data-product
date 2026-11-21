# Series Roadmap

Each part is a branch. A branch is the previous branch plus one squashed commit, so the diff between two neighbouring branches is the change the matching article describes. The project is local first: parts 3–5 run on files and DuckDB with no cloud account, and part 6 moves storage to Google Cloud behind the same interfaces.

| Branch | Article | Outcome | Repository change |
|---|---|---|---|
| `part-01-design-and-requirements` | 1–2. Design the first data product; gather requirements | Choose NYC 311, state the consumer's questions, define the input, intermediate, and output boundaries, and set a small draft contract. | Package scaffold, `product.yaml`, and the architecture and contract docs. |
| `part-02-explore-source` | 3. Explore the source | Profile a bounded NYC 311 sample: types, nulls, and approximate batch volume. | Add a reproducible marimo notebook and record observed counts and extract size. |
| `part-03-land-raw-locally` | 4. Land the raw batch locally | Fetch ordered CSV pages, keep the source bytes on disk, and write a run manifest last. | Implement `civic-data land-raw` as a Masoora pipeline with a Pydantic context, a raw-store interface, and a local implementation. |
| `part-04-intermediate-layer` | 5. Build the intermediate layer | Validate and normalize records, report rejects, and merge into DuckDB so reruns are safe. | Implement `build-intermediate` and the `staging` schema. |
| `part-05-local-output-port` | 6. Publish a local output port | Add quality checks and publish the documented DuckDB view. | Implement `publish-product` and a consumer query. |
| `part-06-deploy-to-gcp` | 7. Deploy to GCP with Terraform | Move raw storage and the query interface to Cloud Storage and BigQuery in `europe-west2`. | Add reviewed Terraform, cloud implementations of the storage interfaces, and a container image. |
| `part-07-schedule-observe` | 8. Schedule, observe, and debug | Schedule the daily job, inspect a failed run, and recover it. | Add `run-daily`, the Cloud Run Job schedule, structured logs, alerts, and optional Grafana instructions. |
| `part-08-review` | 9. Review the platform | Compare measured costs and behavior with assumptions, recap limits, and identify extensions. | Update observed costs and decisions; keep Iceberg and a catalog as later work. |

`master` is the last branch plus an index of the parts. The first series ends with one reliable, observable data product. A second format, Iceberg, catalog, and warehouse are extensions rather than prerequisites.
