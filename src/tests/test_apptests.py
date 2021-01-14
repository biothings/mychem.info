import glob
import json
import os

import pytest
import elasticsearch
from biothings.tests.web import BiothingsWebAppTest


class TestMultiIndices(BiothingsWebAppTest):
    def test_000_null(self):
        pass


class TestMyChemWebAppConfigAnnotationIdRegex(BiothingsWebAppTest):
    def _process_es_data_dir(self, data_dir_path):
        if not os.path.exists(data_dir_path):
            yield
            return

        client = elasticsearch.Elasticsearch(self.settings.ES_HOST)
        server_major_version = client.info()['version']['number'].split('.')[0]
        client_major_version = str(elasticsearch.__version__[0])
        if server_major_version != client_major_version:
            pytest.exit('ES version does not match its python library.')

        # FIXME: this is broken
        default_doc_type = self.settings.ES_DOC_TYPE

        indices = []
        glob_json_pattern = os.path.join(data_dir_path, '*.json')
        # FIXME: wrap around in try-finally so the index is guaranteed to be
        #  cleaned up
        for index_mapping_path in glob.glob(glob_json_pattern):
            index_name = os.path.basename(index_mapping_path)
            index_name = os.path.splitext(index_name)[0]
            indices.append(index_name)
            if client.indices.exists(index_name):
                raise Exception(f"{index_name} already exists!")
            with open(index_mapping_path, 'r') as f:
                mapping = json.load(f)
            data_path = os.path.join(data_dir_path, index_name + '.ndjson')
            with open(data_path, 'r') as f:
                bulk_data = f.read()
            if elasticsearch.__version__[0] > 6:
                client.indices.create(index_name, mapping, include_type_name=True)
                client.bulk(bulk_data, index_name)
            else:
                client.indices.create(index_name, mapping)
                # FIXME: doc_type problem in ES6
                # client.bulk(bulk_data, index_name, default_doc_type)
                client.bulk(bulk_data, index_name, "drug")

            client.indices.refresh()
        yield
        for index_name in indices:
            client.indices.delete(index_name)

    @pytest.fixture(scope="class", autouse=True)
    def load_es_data_cls(self, request):
        data_dir = './test_data/' + request.cls.__name__

        yield from self._process_es_data_dir(data_dir)

    # reason why we do not want this is because this would screw up
    # the indices loaded for the class/session/module
    # @pytest.fixture(scope="function", autouse=True)
    # def load_es_data_fn(self, request):
    #     data_dir = './test_data/' + request.cls.__name__ + '/' + \
    #         request.function.__name__
    #     yield from self._process_es_data_dir(data_dir)

    def test_010_drugbank(self):
        q = 'db0'
        res = self.request("chem", method="POST", data={"ids": q})
        res = res.json()
        assert len(res) == 1
        assert res[0]['drugbank']['id'].lower() == q

    def test_011_chembl(self):
        q = 'chembl0'
        res = self.request("chem", method="POST", data={"ids": q})
        res = res.json()
        assert len(res) == 1
        assert res[0]['chembl']['molecule_chembl_id'].lower() == q

    def test_012_chebi(self):
        q = 'chebi:0'
        res = self.request("chem", method="POST", data={"ids": q})
        res = res.json()
        assert len(res) == 1
        assert res[0]['chebi']['id'].lower() == q

    def test_013_chebi_secondary(self):
        q = 'chebi:2'
        res = self.request("chem", method="POST", data={"ids": q})
        res = res.json()
        assert len(res) == 1
        assert res[0]['chebi']['secondary_chebi_id'].lower() == q

    def test_014_unii(self):
        q = 'MOCKUNII00'
        res = self.request("chem", method="POST", data={"ids": q})
        res = res.json()
        assert len(res) == 1
        assert res[0]['unii']['unii'] == q

    def test_015_pubchem(self):
        q = 'cid:0'
        res = self.request("chem", method="POST", data={"ids": q})
        res = res.json()
        assert len(res) == 1
        assert res[0]['pubchem']['cid'] == "0"

    def test_016_pubchem_noprefix(self):
        q = '0'
        res = self.request("chem", method="POST", data={"ids": q})
        res = res.json()
        assert len(res) == 1
        assert res[0]['pubchem']['cid'] == "0"

    def test_020_drugbank_ci(self):
        q = 'dB0'
        res = self.request("chem", method="POST", data={"ids": q})
        res = res.json()
        assert len(res) == 1
        assert res[0]['drugbank']['id'].lower() == q.lower()

    def test_021_chembl_ci(self):
        q = 'cHeMbL0'
        res = self.request("chem", method="POST", data={"ids": q})
        res = res.json()
        assert len(res) == 1
        assert res[0]['chembl']['molecule_chembl_id'].lower() == q.lower()

    def test_022_chebi_ci(self):
        q = 'ChEBI:0'
        res = self.request("chem", method="POST", data={"ids": q})
        res = res.json()
        assert len(res) == 1
        assert res[0]['chebi']['id'].lower() == q.lower()

    def test_023_cid_ci(self):
        q = 'Cid:0'
        res = self.request("chem", method="POST", data={"ids": q})
        res = res.json()
        assert len(res) == 1
        assert res[0]['pubchem']['cid'] == "0"

    def test_030_drugbank_db_in_default_scope(self):
        # by default it looks at _id, but the query below
        # matches the UNII regex, so nothing should be returned
        q = 'DEFAULTSCO'
        # FIXME: check response status code
        res = self.request(f"chem/{q}", method="GET", expect=404)