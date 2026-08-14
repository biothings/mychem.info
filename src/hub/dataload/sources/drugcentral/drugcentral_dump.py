import csv
import os

import biothings

import config

biothings.config_for_app(config)

from biothings.hub.dataload.dumper import BaseDumper

from config import DATA_ARCHIVE_ROOT, DRUGCENTRAL_PASSWORD


class DrugCentralDumper(BaseDumper):
    SRC_NAME = "drugcentral"
    SRC_ROOT_FOLDER = os.path.join(DATA_ARCHIVE_ROOT, SRC_NAME)

    # The number of rows fetched at a time by the server-side cursor.
    CURSOR_ITERSIZE = 100
    CONNECT_TIMEOUT = 30

    # More info about the public DrugCentral Postgres database https://drugcentral.org/download
    HOST = "unmtid-dbs.net"
    PORT = 5433
    DATABASE = "drugcentral"
    USER = "drugman"
    PASSWORD = DRUGCENTRAL_PASSWORD

    def prepare_client(self):
        # Import the optional database driver only when a dump is requested.
        # A missing/broken libpq installation must not prevent source discovery.
        try:
            import psycopg
        except ImportError as exc:
            raise RuntimeError(
                "DrugCentral dumping requires the 'psycopg[binary]' package"
            ) from exc

        self.client = psycopg.connect(
            dbname=self.DATABASE,
            user=self.USER,
            password=self.PASSWORD,
            host=self.HOST,
            port=self.PORT,
            connect_timeout=self.CONNECT_TIMEOUT,
        )

    def get_client(self):
        """Return an active connection without hiding driver/connect errors."""
        if not self._state.get("client"):
            self.prepare_client()
        return self._state["client"]

    def release_client(self):
        # Disconnect from the database
        client = self._state.get("client")
        if client:
            client.close()
            self.client = None

    def download(self, remotefile, localfile):
        # Download the data from the database and write it to a CSV file

        # Create the local folders if they don't exist
        self.prepare_local_folders(localfile)

        table_name, columns = remotefile.get("table_name"), remotefile.get("columns")

        client = self.get_client()
        cursor_name = f"mychem_{table_name}"
        with client.cursor(name=cursor_name) as cursor:
            cursor.itersize = self.CURSOR_ITERSIZE
            cursor.execute(f"SELECT {columns} FROM {table_name}")

            column_names = [column.name for column in cursor.description]

            self.logger.debug(f"Retrieving data from table: {table_name}")

            with open(os.path.join(localfile), "w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(column_names)

                row_count = 0

                # A server-side cursor keeps large DrugCentral tables out of RAM.
                for row in cursor:
                    writer.writerow(row)
                    row_count += 1

        self.logger.debug(
            f"Retrieved {row_count} rows from table: {table_name} and saved to {localfile}"
        )

    def get_latest_release(self):
        # Get the latest release from the dbversion table
        with self.get_client().cursor() as cursor:
            cursor.execute("SELECT * FROM dbversion")
            # dbversion contains a version number and date; only the date is used.
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
