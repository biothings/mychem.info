"""
Local tests for exercising the annotation regex pattern matching for
different types of queries one could expect for the mychem data sources
"""

import pytest
import requests

from biothings.tests.web import BiothingsWebAppTest


class TestMyChemWebAppConfigAnnotationIdRegex(BiothingsWebAppTest):
    TEST_DATA_DIR_NAME = "TestAnnotationRegex"

    """
    def test_010_drugbank(self):
        q = 'db03107'
        res = self.request("chem", method="POST", data={"ids": q})
        res = res.json()
        assert len(res) == 1
        assert self.value_in_result(q, res, 'drugbank.id', True)
    """

    def test_011_chembl(self):
        q = "chembl297569"
        res = self.request("chem", method="POST", data={"ids": q})
        res = res.json()
        assert len(res) == 1
        assert self.value_in_result(q, res, "chembl.molecule_chembl_id", True)

    def test_012_chebi(self):
        q = "chebi:57966"
        res = self.request("chem", method="POST", data={"ids": q})
        res = res.json()
        assert len(res) == 1
        assert self.value_in_result(q, res, "chebi.id", True)

    def test_013_chebi_secondary(self):
        q = "chebi:22821"
        res = self.request("chem", method="POST", data={"ids": q})
        res = res.json()
        assert len(res) == 1
        assert self.value_in_result(q, res, "chebi.secondary_chebi_id", True)

    def test_014_unii(self):
        q = "11P2JDE17B"
        res = self.request("chem", method="POST", data={"ids": q})
        res = res.json()
        assert len(res) == 1
        assert self.value_in_result(q, res, "unii.unii", False)

    def test_015_pubchem(self):
        q = "cid:120933777"
        res = self.request("chem", method="POST", data={"ids": q})
        res = res.json()
        assert len(res) == 1
        assert self.value_in_result("120933777", res, "pubchem.cid")

    def test_016_pubchem_noprefix(self):
        q = "120933777"
        res = self.request("chem", method="POST", data={"ids": q})
        res = res.json()
        assert len(res) == 1
        assert self.value_in_result(q, res, "pubchem.cid")

    """
    def test_020_drugbank_ci(self):
        q = 'dB03107'
        res = self.request("chem", method="POST", data={"ids": q})
        res = res.json()
        assert len(res) == 1
        assert self.value_in_result(q, res, 'drugbank.id', True)
    """

    def test_021_chembl_ci(self):
        q = "CHEMBL297569"
        res = self.request("chem", method="POST", data={"ids": q})
        res = res.json()
        assert len(res) == 1
        assert self.value_in_result(q, res, "chembl.molecule_chembl_id", True)

    def test_022_chebi_ci(self):
        q = "ChEBI:57966"
        res = self.request("chem", method="POST", data={"ids": q})
        res = res.json()
        assert len(res) == 1
        assert self.value_in_result(q, res, "chebi.id", True)

    def test_023_cid_ci(self):
        q = "Cid:120933777"
        res = self.request("chem", method="POST", data={"ids": q})
        res = res.json()
        assert len(res) == 1
        assert self.value_in_result("120933777", res, "pubchem.cid")


class TestMyChemWebAppConfigAnnotationRegexMockData(BiothingsWebAppTest):
    TEST_DATA_DIR_NAME = "TestAnnotationRegexMock"

    def test_001_drugbank_db_in_default_scope(self):
        # by default it looks at _id, but the query below
        # matches the UNII regex, so nothing should be returned
        q = "DEFAULTSCO"
        # FIXME: check response status code
        res = self.request(f"chem/{q}", method="GET", expect=404)
