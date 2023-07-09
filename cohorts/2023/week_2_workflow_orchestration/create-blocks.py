import argparse
import json
import os

from prefect import flow, task
from prefect_gcp import GcpCredentials
from prefect_gcp.bigquery import BigQueryWarehouse
from prefect_gcp.cloud_storage import GcsBucket


@task
def create_storage_block(bucket_name: str, gcp_credentials: GcpCredentials) -> None:
    storage_block = GcsBucket(bucket=bucket_name, gcp_credentials=gcp_credentials)
    storage_block.save(name=bucket_name, overwrite = True)


@task
def create_bq_warehouse(block_name: str, gcp_credentials: GcpCredentials) -> None:
    warehouse_block = BigQueryWarehouse(gcp_credentials=gcp_credentials)
    warehouse_block.save(name=block_name, overwrite = True)


@flow
def create_etl_blocks(bucket_name: str, gcp_credentials: GcpCredentials) -> None:
    create_storage_block.submit(bucket_name, gcp_credentials)
    create_bq_warehouse.submit("gcp-bigquery", gcp_credentials)


@task
def load_gcp_credentials(credentials_block_name: str) -> GcpCredentials | None:
    try:
        return GcpCredentials.load(credentials_block_name)
    except:
        return None


@task
def save_service_account_info(info: dict, credentials_block_name: str) -> None:
    service_account_info = {
        "type": "service_account",
        "client_id": "CLIENT_ID",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://accounts.google.com/o/oauth2/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/SERVICE_ACCOUNT_EMAIL",
    }

    service_account_info.update(info)

    GcpCredentials(service_account_info=service_account_info).save(
        credentials_block_name
    )


@task
def read_service_account_key_file(file_path: str) -> dict:
    if not os.path.isfile(file_path):
        raise ValueError(
            "No service acccount credentials supplied, and no pre-existing service account credential block was found on prefect. Please add service account credentials as key.json in the working directory."
        )
    else:
        with open(file_path) as f:
            return json.loads(f.read())


@flow
def create_credentials_block(
    credentials_block_name: str, keyfile_name: str
) -> GcpCredentials:
    gcp_credentials = load_gcp_credentials(credentials_block_name)

    if gcp_credentials is not None:
        return gcp_credentials
    else:
        service_account_info = read_service_account_key_file(keyfile_name)
        save_service_account_info(service_account_info, credentials_block_name)
        return load_gcp_credentials(credentials_block_name)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Creates a bucket block with specified name, and a big query warehouse for prefect"
    )
    parser.add_argument("bucket", help="Name of the gcp bucket to add a block for")
    parser.add_argument(
        "--keyfile",
        help="Name of the key file to upload service account credentials from.",
        default="key.json",
        required=False,
    )
    args = parser.parse_args()

    credentials_block_name = "gcp-credentials"

    gcp_credentials = create_credentials_block(credentials_block_name, args.keyfile)
    create_etl_blocks(args.bucket, gcp_credentials)
