import hashlib
import os
from datetime import datetime, timezone

import biothings
import config

biothings.config_for_app(config)

from biothings.hub.dataload.dumper import HTTPDumper
from config import DATA_ARCHIVE_ROOT


class FDAOrphanDrugDumper(HTTPDumper):
    """Download the complete FDA orphan-designation table."""

    SRC_NAME = "fda_orphan_drug"
    SRC_ROOT_FOLDER = os.path.join(DATA_ARCHIVE_ROOT, SRC_NAME)
    SCHEDULE = "0 12 * * *"

    SEARCH_URL = (
        "https://www.accessdata.fda.gov/scripts/opdlisting/oopd/OOPD_Results.cfm"
    )
    LOCAL_FILENAME = "fda_orphan_drug.xls"

    def get_form_data(self):
        """Return the form submission used by the FDA's Excel export option."""
        return {
            "Product_name": "",
            "sponsor_name": "",
            "Designation": "",
            "Designation_Start_Date": "01/01/1983",
            "Designation_End_Date": datetime.now(timezone.utc).strftime("%m/%d/%Y"),
            "Search_param": "DESDATE",
            "Output_Format": "Excel",
            "Sort_order": "GENERIC_NAME",
            "RecordsPerPage": "25",
            "newSearch": "Run Search",
        }

    def fetch_export(self):
        response = self.client.post(
            self.SEARCH_URL,
            data=self.get_form_data(),
            timeout=120,
        )
        response.raise_for_status()

        content_type = response.headers.get("Content-Type", "").lower()
        if "excel" not in content_type or b"Generic Name" not in response.content:
            raise ValueError(
                "FDA orphan-drug response is not the expected Excel export"
            )
        return response.content

    def create_todump_list(self, force=False, **kwargs):
        export_content = self.fetch_export()
        self.release = hashlib.sha256(export_content).hexdigest()
        current_release = (self.src_doc or {}).get("download", {}).get("release")

        if force or self.release != current_release:
            # Retain the checked response so the download phase stores exactly the
            # bytes whose digest was used as the release identifier.
            self._export_content = export_content
            self.to_dump.append(
                {
                    "remote": self.SEARCH_URL,
                    "local": os.path.join(self.new_data_folder, self.LOCAL_FILENAME),
                }
            )

    def download(self, remoteurl, localfile):
        export_content = getattr(self, "_export_content", None)
        if export_content is None:
            raise RuntimeError(
                "FDA export content was not retained during the release check"
            )
        if hashlib.sha256(export_content).hexdigest() != self.release:
            raise ValueError(
                "FDA orphan-drug export changed after its release was calculated"
            )

        self.prepare_local_folders(localfile)
        with open(localfile, "wb") as output:
            output.write(export_content)
