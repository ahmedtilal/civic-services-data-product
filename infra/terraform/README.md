# Terraform Foundation

Terraform resources are introduced in Part 2 of the series. This directory reserves the infrastructure boundary; no cloud resources are declared or applied by the initial scaffold.

The planned configuration will create one regional raw bucket, two BigQuery datasets, a dedicated runtime identity, Artifact Registry, required APIs, and a billing budget alert. Project ID, billing account ID, and alert recipients must be supplied locally and must not be committed.

When Terraform is added:

1. Authenticate with Application Default Credentials.
2. Run `terraform init`.
3. Review `terraform plan` and its cost/resource changes.
4. Apply only the reviewed plan.
5. Keep state, `.tfvars`, credentials, and provider caches out of Git.

The initial tutorial uses local state. Move to a remote backend only when collaboration or automated deployments require it.
