import csv
import os

import biothings
import psycopg2

import config

biothings.config_for_app(config)

from biothings.hub.dataload.dumper import BaseDumper

from config import DATA_ARCHIVE_ROOT


class DrugCentralDumper(BaseDumper):
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
        # Create a cursor
        self._cursor = self.client.cursor()

    @property
    def cursor(self):
        # Return the cursor if it exists, otherwise create it
        if self.client:
            self._cursor = self.client.cursor()
        return self._cursor

    def unprepare(self):
        # Set the state of the cursor to None
        self._cursor = None
        return super().unprepare()

    def release_client(self):
        # Disconnect from the database
        assert self.client
        self.client.close()
        self.client = None

    def download(self, remotefile, localfile):
        # Download the data from the database and write it to a CSV file

        # Create the local folders if they don't exist
        self.prepare_local_folders(localfile)

        table_name, columns = remotefile.get("table_name"), remotefile.get("columns")

        cursor = self.cursor
        cursor.execute(f"SELECT {columns} FROM {table_name}")

        column_names = [desc[0] for desc in cursor.description]

        # Open the CSV file and write the column names
        with open(os.path.join(localfile), "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(column_names)

            # Write the rows one by one
            row = cursor.fetchone()
            while row:
                writer.writerow(row)
                row = cursor.fetchone()

    def get_latest_release(self):
        # Get the latest release from the dbversion table
        cursor = self.cursor
        cursor.execute("SELECT * FROM dbversion")
        # dbversion contains a tuple with the version number and the date, we only need the date
        _, version_date = cursor.fetchone()
        return version_date.strftime("%Y-%m-%d")

    def create_todump_list(self, force=False):
        # Create a list of tables to dump
        self.release = self.get_latest_release()

        data_dir = os.path.join(self.__class__.SRC_ROOT_FOLDER, self.release)

        if force or not os.path.exists(data_dir):
            self.logger.info("New release '%s' found" % self.release)

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

            for table in tables:
                remote_info = {
                    "table_name": table.get("table_name"),
                    "columns": table.get("columns", "*"),
                }
                local_file = os.path.join(
                    data_dir, table.get("file_name", f"{table['table_name']}.csv")
                )
                self.to_dump.append(
                    {
                        "remote": remote_info,
                        "local": local_file,
                    }
                )
        else:
            self.logger.debug("No new release found")
