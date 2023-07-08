locals {
    data_region = "us-east1"
}

resource "google_storage_bucket" "data_lake" {
    name    = "practice-zoomcamp-392000-data-lake"
    location = local.data_region
    storage_class = "STANDARD"

    uniform_bucket_level_access = true
    public_access_prevention = "enforced"

    versioning {
        enabled = true
    }

    lifecycle_rule {
      action {
        type = "Delete"
      }

      condition {
        age = 30
      }
    }

    force_destroy = true
}

resource "google_bigquery_dataset" "data-warehouse" {
    dataset_id = "trips_data"
    location = local.data_region
    description = "Trips data warehouse"
    delete_contents_on_destroy = true
}