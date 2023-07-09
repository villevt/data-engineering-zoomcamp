import argparse
import pandas as pd
from prefect import flow, task
from prefect_gcp import GcsBucket


@task(retries=3)
def extract(dataset_url: str) -> pd.DataFrame:
    df = pd.read_csv(dataset_url)
    return df


@task(log_prints=True)
def transform(df: pd.DataFrame, year: int, month: int) -> pd.DataFrame:
    df["tpep_pickup_datetime"] = pd.to_datetime(df["tpep_pickup_datetime"])
    df["tpep_dropoff_datetime"] = pd.to_datetime(df["tpep_dropoff_datetime"])
    print(df.head(5))
    print(f"Columns ({len(df.columns)})\n:{df.dtypes}")
    print(f"Rows: {len(df)}")
    print(f"Null observations per column\n:{df.isna().sum()}")

    original_rows = len(df)
    df = df[
        (
            (df["tpep_pickup_datetime"].dt.year == year) & (
                df["tpep_pickup_datetime"].dt.month == month)
        ) | (
            (df["tpep_dropoff_datetime"].dt.year == year) & (
                df["tpep_dropoff_datetime"].dt.month == month)
        )
    ]

    print(
        f"Filtered {original_rows - len(df)} rows falling outside the month {month:02}/{year}")

    min_date = df["tpep_pickup_datetime"].dt.date.min()
    max_date = df["tpep_pickup_datetime"].dt.date.max()
    date_range = set(pd.date_range(min_date, max_date))
    dates_not_found = [str(d) for d in sorted([ts.date() for ts in date_range.difference(set(df["tpep_pickup_datetime"]))])]
    print(f"Dates with no pickups: {dates_not_found}")
    return df

@task
def load(df: pd.DataFrame, bucket_path: str, block_name: str) -> None:
    gcs_block = GcsBucket.load(block_name)
    gcs_block.upload_from_dataframe(df = df, to_path = bucket_path, serialization_format='parquet_gzip')


@flow(retries=3)
def etl_gcs(color: str, year: int, month: int, block_name: str) -> None:
    dataset_file = f"{color}_tripdata_{year}-{month:02}"
    dataset_url = f"https://github.com/DataTalksClub/nyc-tlc-data/releases/download/{color}/{dataset_file}.csv.gz"

    dataset = extract(dataset_url)
    dataset = transform(dataset, year, month)

    bucket_path = f"tripdata/{color}_{year}-{month:02}"
    load(dataset, bucket_path, block_name)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Uploads taxi data with specified parameters to a specified GCP bucket"
    )
    parser.add_argument("bucket", help="Name of the GCP bucket to upload to")
    parser.add_argument("--color", default="yellow", choices=["yellow", "green"], required = False, help = "Cab color: can be green or yellow")
    parser.add_argument("--year", default=2021, choices=[2019, 2020, 2021], required = False, help = "Year to fetch cab rides for")
    parser.add_argument("--month", default = 1, choices=list(range(1, 13)), required = False, help = "Month (1-12) to fetch cab rides for")
    args = parser.parse_args()

    etl_gcs(args.color, args.year, args.month, args.bucket)
