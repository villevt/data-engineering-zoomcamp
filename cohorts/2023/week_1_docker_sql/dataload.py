from datetime import date
from sqlalchemy import create_engine
from sqlalchemy_utils import create_database, database_exists
import io
import os
import pandas as pd
import requests

def read_csv_from_url(url, gz = True):
    response = requests.get(url)
    content = response.content

    compression = "gzip" if gz else None

    data = pd.read_csv(io.BytesIO(content), compression=compression)
    data.columns = map(str.lower, data.columns)
    return data

if __name__ == "__main__":
    refresh_file = "dataload-refresh/dataload-last-refresh.txt"
    last_update = None
    if os.path.isfile(refresh_file):
        with open(refresh_file, "r") as f:
            last_update = date.fromisoformat(f.read())

    if last_update is None or date.today() > last_update:
        POSTGRES_USER = os.environ.get("POSTGRES_USER")
        POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD")

        print("DATALOAD: Data starting data loading ...")
        db = create_engine(f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@db:5432/trips")

        if not database_exists(db.url):
            create_database(db.url)

        with db.connect() as con:
            trip_data = read_csv_from_url("https://github.com/DataTalksClub/nyc-tlc-data/releases/download/green/green_tripdata_2019-01.csv.gz")
            trip_data.to_sql("trips", con)
            zones_data = read_csv_from_url("https://s3.amazonaws.com/nyc-tlc/misc/taxi+_zone_lookup.csv", gz = False)
            zones_data.to_sql("zones", con)
        db.dispose()

        with open(refresh_file, "w") as f:
            f.write(str(date.today()))

        print("DATALOAD: Finished loading data...")