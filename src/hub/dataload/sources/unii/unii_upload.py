import glob
import os

import biothings.hub.dataload.storage as storage
from biothings.hub.datatransform import IDStruct, nested_lookup

from hub.dataload.uploader import BaseDrugUploader
from hub.datatransform.keylookup import MyChemKeyLookup

from .unii_parser import load_data

SRC_META = {
    "url": 'https://precision.fda.gov/uniisearch',
    "license": "public domain",
    "license_url": "https://www.nlm.nih.gov/web_policies.html",
    "license_url_short": "http://bit.ly/2Pg8Oo9"
}


class UniiIDStruct(IDStruct):
    """Custom IDStruct to handle UNII data structures (dict or list)"""

    def _init_strct(self, field, doc_lst):
        """
        Initialize _id_tuple_lst with proper value extraction for UNII

        This handles both cases:
        - record['unii'] is a dict (single record)
        - record['unii'] is a list of dicts (multiple records with same ID)
        """
        for doc in doc_lst:
            value = nested_lookup(doc, field)
            if value:
                doc_id = doc.get('_id')

                # Handle the case where unii field contains list or dict
                if field.startswith('unii.'):
                    # Remove 'unii.' prefix to get the actual field name
                    field_name = field.split('.', 1)[1]
                    unii_data = doc.get('unii')

                    if isinstance(unii_data, list):
                        # Multiple UNII records - extract field from each
                        for unii_record in unii_data:
                            if isinstance(unii_record, dict):
                                extracted_value = unii_record.get(field_name)
                                if extracted_value is not None:
                                    self.add(doc_id, str(extracted_value))
                    elif isinstance(unii_data, dict):
                        # Single UNII record
                        extracted_value = unii_data.get(field_name)
                        if extracted_value is not None:
                            self.add(doc_id, str(extracted_value))
                else:
                    # Handle non-unii fields normally
                    self.add(doc_id, str(value))

    def find_right(self, ids):
        """
        Override find_right to handle unhashable types properly
        """
        if not ids:
            return []

        # Convert unhashable types to strings
        safe_ids = []
        if not isinstance(ids, (set, list, tuple)):
            ids = [ids]

        for id_val in ids:
            if isinstance(id_val, dict):
                # Convert dict to string representation for use as key
                # For UNII, we're mainly interested in the 'unii' value
                if 'unii' in id_val:
                    safe_ids.append(str(id_val['unii']))
                else:
                    # Fallback to string representation
                    safe_ids.append(str(id_val))
            elif isinstance(id_val, list):
                # Convert list to string
                safe_ids.append(str(id_val))
            else:
                safe_ids.append(id_val)

        # Use the parent's find method with safe IDs
        return self.find(self.inverse, safe_ids)


class UniiUploader(BaseDrugUploader):

    name = "unii"
    storage_class = storage.RootKeyMergerStorage
    __metadata__ = {"src_meta": SRC_META}

    keylookup = MyChemKeyLookup([('pubchem', 'unii.pubchem'),
                                 ('unii', 'unii.unii'),
                                 ('inchikey', 'unii.inchikey'),
                                 ('smiles', 'unii.smiles'),
                                 ('drugname', 'unii.preferred_term'),
                                 ('drugcentral', 'unii.drugcentral')],
                                copy_from_doc=True,
                                idstruct_class=UniiIDStruct,
                                )

    def load_data(self, data_folder):
        self.logger.info("Load data from '%s'" % data_folder)
        record_files = glob.glob(os.path.join(data_folder, "*Records*.txt"))
        if len(record_files) != 1:
            raise AssertionError(
                "Expecting one record.txt file, got %s" % repr(record_files))
        input_file = record_files.pop()
        if not os.path.exists(input_file):
            raise AssertionError("Can't find input file '%s'" % input_file)
        return self.keylookup(load_data)(input_file)

    def post_update_data(self, *args, **kwargs):
        """create indexes following upload"""
        # Key identifiers for UNII lookups based on the keylookup graph
        index_fields = [
            "unii.unii",                 # Primary UNII identifier
            "unii.preferred_term",       # Drug name lookup
            "unii.inchikey",             # Structural identifier
            "unii.smiles",               # Structural identifier
            "unii.pubchem",              # PubChem cross-reference
            "unii.drugcentral"           # DrugCentral cross-reference
        ]

        for field in index_fields:
            self.logger.info("Indexing '%s'" % field)
            self.collection.create_index(field, background=True)
