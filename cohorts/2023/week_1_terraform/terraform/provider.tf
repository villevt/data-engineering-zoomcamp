provider "google" {
  project = "zoomcamp-392000"
  alias   = "impersonation"
  scopes = [
    "https://www.googleapis.com/auth/cloud-platform",
    "https://www.googleapis.com/auth/userinfo.email",
  ]
}

data "google_service_account_access_token" "default" {
  provider               = google.impersonation
  target_service_account = "zoomcamp-terraform@zoomcamp-392000.iam.gserviceaccount.com"
  scopes                 = ["userinfo-email", "cloud-platform"]
  lifetime               = "1200s"
}

provider "google" {
  project         = "zoomcamp-392000"
  access_token    = data.google_service_account_access_token.default.access_token
  request_timeout = "60s"
  zone            = "us-east1"
}