data "google_secret_manager_secret_version" "terraform_service_account_email" {
 secret   = "terraform_service_account_email"
}

provider "google" {
 alias = "impersonation"
 scopes = [
   "https://www.googleapis.com/auth/cloud-platform",
   "https://www.googleapis.com/auth/userinfo.email",
 ]
}

data "google_service_account_access_token" "default" {
 provider               	= google.impersonation
 target_service_account 	= data.google_secret_manager_secret_version.terraform_service_account_email.secret_data
 scopes                 	= ["userinfo-email", "cloud-platform"]
 lifetime               	= "1200s"
}

provider "google" {
 project 		    = "zoomcamp-392000"
 access_token	    = data.google_service_account_access_token.default.access_token
 request_timeout    = "60s"
 zone               = "us-east1"
}