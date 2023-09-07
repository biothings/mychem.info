import csv
import os

import biothings
import psycopg2

import config

biothings.config_for_app(config)

from biothings.hub.dataload.dumper import FilesystemDumper

from config import DATA_ARCHIVE_ROOT


class DrugCentralDumper(FilesystemDumper):
    FS_OP = "mv"

    SRC_NAME = "drugcentral"
    SRC_ROOT_FOLDER = os.path.join(DATA_ARCHIVE_ROOT, SRC_NAME)

    # More info about the public DrugCentral Postgres database https://drugcentral.org/download
    HOST = "unmtid-dbs.net"
    PORT = 5433
    DATABASE = "drugcentral"
    USER = "drugman"
    PASSWORD = "dosage"

    def prepare_client(self):
        # Connect to the database
        self.client = psycopg2.connect(
            database=self.DATABASE,
            user=self.USER,
            password=self.PASSWORD,
            host=self.HOST,
            port=self.PORT,
        )

    def release_client(self):
        # Disconnect from the database
        assert self.client
        self.client.close()
        self.client = None

    def get_data(self, cursor):
        def fetch_data_and_write_to_csv(table_name, columns=None, file_name=None):
            # Define the columns to select and the file name
            select_columns = columns if columns else "*"
            csv_file_name = file_name if file_name else f"{table_name}.csv"

            # Execute the query
            cursor.execute(f"SELECT {select_columns} FROM {table_name}")

            # Get the column names
            column_names = [desc[0] for desc in cursor.description]

            # Open the CSV file and write the column names
            with open(os.path.join(csv_file_name), "w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(column_names)

                # Write the rows one by one
                row = cursor.fetchone()
                while row:
                    writer.writerow(row)
                    row = cursor.fetchone()

        # List of tables and their corresponding CSV file names and columns to select
        tables = [
            {"table_name": "pharma_class"},
            {"table_name": "faers"},
            {"table_name": "act_table_full"},
            {"table_name": "omop_relationship"},
            {"table_name": "approval"},
            {"table_name": "atc_ddd", "file_name": "drug_dosage.csv"},
            {"table_name": "synonyms"},
            {
                "table_name": "structures",
                "columns": "id, inchi, inchikey, smiles, cas_reg_no, name",
                "file_name": "structures.smiles.csv",
            },
            {"table_name": "identifier", "file_name": "identifiers.csv"},
        ]

        # Fetch data from each table and write it to a CSV file
        for table in tables:
            fetch_data_and_write_to_csv(**table)

    def get_latest_release(self, cursor):
        cursor.execute("SELECT * FROM dbversion")
        # dbversion contains a tuple with the version number and the date, we only need the date
        _, version_date = cursor.fetchone()
        return version_date.strftime("%Y-%m-%d")

    def create_todump_list(self, force=False, **kwargs):
        cursor = self.client.cursor()
        # Fetch the latest release from the dbversion table
        self.release = self.get_latest_release(cursor)

        # Define the data directory
        data_dir = os.path.join(self.__class__.SRC_ROOT_FOLDER, self.release)

        # Check if a new release is available
        if force or not os.path.exists(data_dir):
            self.logger.info("New release '%s' found" % self.release)

            # Create the data directory
            if not os.path.exists(data_dir):
                os.makedirs(data_dir)

            # Fetch the data and write it to CSV files
            self.get_data(cursor)

            # List of file_names and their corresponding CSV file names
            file_names = [
                "pharma_class",
                "faers",
                "act_table_full",
                "omop_relationship",
                "approval",
                "drug_dosage",
                "synonyms",
                "structures.smiles",
                "identifiers",
            ]

            # Append each CSV file path to the self.to_dump list
            for file_name in file_names:
                remote_file = f"{file_name}.csv"
                local_file = os.path.join(data_dir, f"{file_name}.csv")
                self.to_dump.append(
                    {
                        "remote": remote_file,
                        "local": local_file,
                    }
                )

        else:
            self.logger.info("No new release found")
