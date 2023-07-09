import json
from prefect_gcp import GcpCredentials

def save_service_account_info(info):
    service_account_info = {
        "type": "service_account",
        "client_id": "CLIENT_ID",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://accounts.google.com/o/oauth2/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/SERVICE_ACCOUNT_EMAIL"
    } 

    service_account_info.update(info)

    GcpCredentials(
        service_account_info=service_account_info
    ).save("gcp")

if __name__ == "__main__":
    with open("key.json") as f:
        info = json.loads(f.read())
        save_service_account_info(info)
