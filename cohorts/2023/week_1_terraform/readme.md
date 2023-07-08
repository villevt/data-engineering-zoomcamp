# Week 1 : Terraform

A terraform configuration for setting up
- A data lake as a GCP Cloud Storage Bucket
- A dataset for "trips data" as a GCP BigQuery dataset (schema)

The setup uses [https://cloud.google.com/iam/docs/service-account-overview#impersonation](service account impersonation) for security reasons, so the end user committing changes with terraform does *not* have to store service account credentials locally on their computer.

The setup consists of the following pieces:

## main.tf

Sets up Google Cloud as a required provider, as well as a backend to securely store the Terraform .tfstate-file in.

## provider.tf

Sets up GCP as a provider, using aforementioned service account impersonation. Fetches service account access token, and uses that to access and modify the GCP project.

## storage.tf

Provisions the aforementioned resources, with a 30 day lifecycle deletion rule set on the storage bucket.