terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "4.51.0"
    }
  }

  backend "gcs" {
    bucket                      = "zoomcamp-392000-tf-state"
    prefix                      = "terraform/state"
    impersonate_service_account = "zoomcamp-terraform@zoomcamp-392000.iam.gserviceaccount.com"
  }
}