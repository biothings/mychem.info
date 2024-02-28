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


class TestMyChemCurieIdParsing(BiothingsWebAppTest):
    TEST_DATA_DIR_NAME = "TestCurieId"

    @pytest.mark.xfail(
        reason="CURIE ID SUPPORT NOT CURRENTLY ENABLED ON MYCHEM.INFO HOST",
        run=True,
        strict=True,
    )
    def test_001_curie_id_annotation_endpoint_GET(self):
        """
        Tests the annotation endpoint support for the biolink CURIE ID.

        If support is enabled then we should retrieve the exact same document
        for all the provided queries

        A mirror copy of the tests we have in the biothings_client
        package (chem.py)
        """
        curie_id_testing_collection = [
            ("57966", "CHEMBL.COMPOUND:57966", "chembl.molecule_chembl_id:57966"),
            (57966, "chembl.compound:57966", "chembl.molecule_chembl_id:57966"),
            (57966, "CheMBL.compOUND:57966", "chembl.molecule_chembl_id:57966"),
            ("120933777", "PUBCHEM.COMPOUND:120933777", "pubchem.cid:120933777"),
            (120933777, "pubchem.compound:120933777", "pubchem.cid:120933777"),
            ("120933777", "PuBcHEm.COMPound:120933777", "pubchem.cid:120933777"),
            (57966, "CHEBI:57966", "chebi.id:57966"),
            ("57966", "chebi:57966", "chebi.id:57966"),
            (57966, "CheBi:57966", "chebi.id:57966"),
            ("11P2JDE17B", "UNII:11P2JDE17B", "unii.unii:11P2JDE17B"),
            ("11P2JDE17B", "unii:11P2JDE17B", "unii.unii:11P2JDE17B"),
            ("11P2JDE17B", "uNIi:11P2JDE17B", "unii.unii:11P2JDE17B"),
            ("dB03107", "DRUGBANK:dB03107", "drugbank.id:dB03107"),
            ("dB03107", "drugbank:dB03107", "drugbank.id:dB03107"),
            ("dB03107", "DrugBaNK:dB03107", "drugbank.id:dB03107"),
        ]

        results_aggregation = []
        endpoint = "gene"
        for id_query, biothings_query, biolink_query in curie_id_testing_collection:
            id_query_result = self.request(f"{endpoint}/{id_query}", expect=200)
            assert isinstance(id_query_result, requests.models.Response)
            assert id_query_result.url == self.get_url(path=f"{endpoint}/{id_query}")

            biothings_term_query_result = self.request(
                f"{endpoint}/{biothings_query}", expect=200
            )
            assert isinstance(biothings_term_query_result, requests.models.Response)
            assert biothings_term_query_result.url == self.get_url(
                path=f"{endpoint}/{biothings_query}"
            )

            biolink_term_query_result = self.request(
                f"{endpoint}/{biolink_query}", expect=200
            )
            assert isinstance(biolink_term_query_result, requests.models.Response)
            assert biolink_term_query_result.url == self.get_url(
                path=f"{endpoint}/{biolink_query}"
            )

            results_aggregation.append(
                (
                    id_query_result.json() == biothings_term_query_result.json(),
                    id_query_result.json() == biolink_term_query_result.json(),
                    biothings_term_query_result.json()
                    == biolink_term_query_result.json(),
                )
            )

        results_validation = []
        failure_messages = []
        for result, test_query in zip(results_aggregation, curie_id_testing_collection):
            cumulative_result = all(result)
            if not cumulative_result:
                failure_messages.append(
                    f"Query Failure: {test_query} | Results: {result}"
                )
            results_validation.append(cumulative_result)

        assert all(results_validation), "\n".join(failure_messages)

    @pytest.mark.xfail(
        reason="CURIE ID SUPPORT NOT CURRENTLY ENABLED ON MYCHEM.INFO HOST",
        run=True,
        strict=True,
    )
    def test_156(self):
        """
        Tests the annotations endpoint support for the biolink CURIE ID.

        Batch query testing against the POST endpoint to verify that the CURIE ID can work with
        multiple

        If support is enabled then we should retrieve the exact same document for all the provided
        queries

        A mirror copy of the tests we have in the biothings_client
        package (chem.py)
        """
        curie_id_testing_collection = [
            ("57966", "CHEMBL.COMPOUND:57966", "chembl.molecule_chembl_id:57966"),
            (57966, "chembl.compound:57966", "chembl.molecule_chembl_id:57966"),
            (57966, "CheMBL.compOUND:57966", "chembl.molecule_chembl_id:57966"),
            ("120933777", "PUBCHEM.COMPOUND:120933777", "pubchem.cid:120933777"),
            (120933777, "pubchem.compound:120933777", "pubchem.cid:120933777"),
            ("120933777", "PuBcHEm.COMPound:120933777", "pubchem.cid:120933777"),
            (57966, "CHEBI:57966", "chebi.id:57966"),
            ("57966", "chebi:57966", "chebi.id:57966"),
            (57966, "CheBi:57966", "chebi.id:57966"),
            ("11P2JDE17B", "UNII:11P2JDE17B", "unii.unii:11P2JDE17B"),
            ("11P2JDE17B", "unii:11P2JDE17B", "unii.unii:11P2JDE17B"),
            ("11P2JDE17B", "uNIi:11P2JDE17B", "unii.unii:11P2JDE17B"),
            ("dB03107", "DRUGBANK:dB03107", "drugbank.id:dB03107"),
            ("dB03107", "drugbank:dB03107", "drugbank.id:dB03107"),
            ("dB03107", "DrugBaNK:dB03107", "drugbank.id:dB03107"),
        ]

        results_aggregation = []
        endpoint = "gene"
        for id_query, biothings_query, biolink_query in curie_id_testing_collection:
            base_result = self.request(f"{endpoint}/{id_query}", expect=200)

            query_collection = (id_query, biothings_query, biolink_query)
            delimiter = ","
            data_mapping = {
                "ids": delimiter.join([f'"{query}"' for query in query_collection])
            }
            header_mapping = {
                "user-agent": "biothings_client.py/0.3.1 (python:3.11.2 requests:2.31.0)"
            }
            query_results = self.request(
                endpoint, method="POST", data=data_mapping, headers=header_mapping
            ).json()
            assert len(query_results) == len(query_collection)

            batch_id_query = query_results[0]
            batch_biothings_query = query_results[1]
            batch_biolink_query = query_results[2]

            batch_id_query_return_value = batch_id_query.pop("query")
            assert batch_id_query_return_value == str(id_query)

            batch_biothings_query_return_value = batch_biothings_query.pop("query")
            assert batch_biothings_query_return_value == str(biothings_query)

            batch_biolink_query_return_value = batch_biolink_query.pop("query")
            assert batch_biolink_query_return_value == str(biolink_query)

            batch_result = (
                base_result.json() == batch_id_query,
                base_result.json() == batch_biothings_query,
                base_result.json() == batch_biolink_query,
            )
            results_aggregation.append(batch_result)

        results_validation = []
        failure_messages = []
        for result, test_query in zip(results_aggregation, curie_id_testing_collection):
            cumulative_result = all(result)
            if not cumulative_result:
                failure_messages.append(
                    f"Query Failure: {test_query} | Results: {result}"
                )
            results_validation.append(cumulative_result)

        assert all(results_validation), "\n".join(failure_messages)
        assert all(results_validation), "\n".join(failure_messages)
