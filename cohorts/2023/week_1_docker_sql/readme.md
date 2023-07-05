# Week 1 : Docker SQL

Mini project consisting of three distinct services, put together with docker-compose:
- PostgreSQL database
- pgAdmin administration panel for postgres
- Data loading utility to populate said database

## PostgreSQL database

Initializes a postgres database with default settings. Needs access credentials `POSTGRES_USER` and `POSTGRES_PASSWORD` defined as environment variables, e.g. in an .env-file.

## pgAdmin

Initializes pgAdmin administration panel for the postgres database with default settings. Needs access credentials `PGADMIN_DEFAULT_EMAIL` and `PGADMIN_DEFAULT_PASSWORD` defined as environment variables, e.g. in an .env-file.

The connection to the aforementioned postgres database can be defined by navigating to the admin panel located in <http://localhost:5050>, as per the docker-compose specification.

## Data loading utility

Load two datasets, taxi [trip data](https://github.com/DataTalksClub/nyc-tlc-data/releases/download/green/green_tripdata_2019-01.csv.gz) and [zone data](https://s3.amazonaws.com/nyc-tlc/misc/taxi+_zone_lookup.csv) into `trips` database in the aforementioned PostgreSQL database, into `trips` and `zones` tables of the default (public) schema. The only transformation to the original data is the conversion of column names into lowercase.

Needs access credentials `POSTGRES_USER` and `POSTGRES_PASSWORD` defined as environment variables, e.g. in an .env-file. The connection URL to postgreSQL is hardcoded as `db:5432/trips`.