import argparse
from io import BytesIO
import pandas as pd
from prefect import flow, task
from prefect_gcp import GcsBucket, GcpCredentials
from prefect_gcp.bigquery import BigQueryWarehouse


@task(retries=3)
def extract(block_name: str, bucket_path: str) -> pd.DataFrame:
    gcs_block = GcsBucket.load(block_name)
    df = None
    with BytesIO() as buf:
        gcs_block.download_object_to_file_object(from_path = bucket_path, to_file_object = buf)
        df = pd.read_parquet(buf)
    return df


@task(log_prints=True)
def transform(df: pd.DataFrame) -> pd.DataFrame:
    numeric_cols = df.select_dtypes(include=["float64", "int64"]).columns

    # Note: in a real world setting, this kind of imputation would be bad!
    # This is because the end user would NOT have visibility into which values were missing
    # and there might be e.g. an underlying systematic reason for some observations being missing
    # which should be further investigated!!
    print(f"Missing observations per column before imputation :\n{df.isna().sum()}")
    df[numeric_cols] = df[numeric_cols].fillna(0)
    print(f"Missing observations per column post imputation:\n{df.isna().sum()}")

    return df

@task(retries=3)
def load(df: pd.DataFrame) -> None:
    gcp_credentials = GcpCredentials.load("gcp-credentials")

    df.to_gbq(
        destination_table="trips.rides",
        credentials=gcp_credentials.get_credentials_from_service_account(),
        chunksize=500_000,
        if_exists="replace"
    )

@flow
def etl_bq(color: str, year: int, month: int, block_name: str) -> None:
    bucket_path = f"tripdata/{color}_{year}-{month:02}.gz.parquet"

    dataset = extract(block_name, bucket_path)
    dataset = transform(dataset)
    load(dataset)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Uploads taxi data with specified parameters to a specified GCS bucket"
    )
    parser.add_argument("bucket", help="Name of the GCS bucket to download from")
    parser.add_argument("--color", default="yellow", choices=["yellow", "green"], required = False, help = "Cab color: can be green or yellow")
    parser.add_argument("--year", default=2021, choices=[2019, 2020, 2021], required = False, help = "Year to fetch cab rides for")
    parser.add_argument("--month", default = 1, choices=list(range(1, 13)), required = False, help = "Month (1-12) to fetch cab rides for")
    args = parser.parse_args()

    etl_bq(args.color, args.year, args.month, args.bucket)
