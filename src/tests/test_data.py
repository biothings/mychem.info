import logging

import pytest
import requests

from biothings.tests.web import BiothingsDataTest

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class TestMyChemCurieIdParsing(BiothingsDataTest):
    host = "mychem.info"
    prefix = "v1"

    def test_001_curie_id_annotation_endpoint_GET(self):
        """
        Tests the annotation endpoint support for the biolink CURIE ID.

        If support is enabled then we should retrieve the exact same document
        for all the provided queries

        A mirror copy of the tests we have in the biothings_client
        package (chem.py)
        """
        curie_id_testing_collection = [
            (
                "UCMIRNVEIXFBKS-UHFFFAOYSA-N",
                "CHEMBL297569",
                "CHEMBL.COMPOUND:CHEMBL297569",
                "chembl.compound:CHEMBL297569",
                "cHEmbl.ComPOUND:CHEMBL297569",
                "chembl.molecule_chembl_id:CHEMBL297569",
            ),
            (
                "AKUPVPKIFATOBM-UHFFFAOYSA-N",
                "120933777",
                120933777,
                "PUBCHEM.COMPOUND:120933777",
                "pubchem.compound:120933777",
                "PuBcHEm.COMPound:120933777",
                "pubchem.cid:120933777",
            ),
            (
                "UCMIRNVEIXFBKS-UHFFFAOYSA-N",
                "CHEBI:CHEBI:57966",
                "chebi:CHEBI:57966",
                "CheBi:CHEBI:57966",
                "chebi.id:CHEBI:57966",
            ),
            (
                "UCMIRNVEIXFBKS-UHFFFAOYSA-N",
                "11P2JDE17B",
                "UNII:11P2JDE17B",
                "unii:11P2JDE17B",
                "uNIi:11P2JDE17B",
                "unii.unii:11P2JDE17B",
            ),
            (
                "UCMIRNVEIXFBKS-UHFFFAOYSA-N",
                "dB03107",
                "DRUGBANK:dB03107",
                "drugbank:dB03107",
                "DrugBaNK:dB03107",
                "drugbank.id:dB03107",
            ),
        ]
        aggregation_query_groups = []
        endpoint = "chem"
        for query_collection in curie_id_testing_collection:
            query_result_storage = []
            for similar_query in query_collection:
                query_result = self.request(
                    f"{endpoint}/{similar_query}", expect=200)
                query_result = self.request(f"{endpoint}/{similar_query}")
                assert isinstance(query_result, requests.models.Response)
                assert query_result.url == self.get_url(
                    path=f"{endpoint}/{similar_query}"
                )
                query_result_storage.append(query_result.json())

            results_aggregation = [
                query == query_result_storage[0] for query in query_result_storage[1:]
            ]

            if all(results_aggregation):
                logger.info(f"Query group {query_collection} succeeded")
            else:
                logger.info(f"Query group {query_collection} failed")

            aggregation_query_groups.append(all(results_aggregation))
        assert all(aggregation_query_groups)

    def test_002_curie_id_annotation_endpoint_POST(self):
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
            (
                "UCMIRNVEIXFBKS-UHFFFAOYSA-N",
                "CHEMBL297569",
                "CHEMBL.COMPOUND:CHEMBL297569",
                "chembl.compound:CHEMBL297569",
                "cHEmbl.ComPOUND:CHEMBL297569",
                "chembl.molecule_chembl_id:CHEMBL297569",
            ),
            (
                "AKUPVPKIFATOBM-UHFFFAOYSA-N",
                "120933777",
                120933777,
                "PUBCHEM.COMPOUND:120933777",
                "pubchem.compound:120933777",
                "PuBcHEm.COMPound:120933777",
                "pubchem.cid:120933777",
            ),
            (
                "UCMIRNVEIXFBKS-UHFFFAOYSA-N",
                "CHEBI:CHEBI:57966",
                "chebi:CHEBI:57966",
                "CheBi:CHEBI:57966",
                "chebi.id:CHEBI:57966",
            ),
            (
                "UCMIRNVEIXFBKS-UHFFFAOYSA-N",
                "11P2JDE17B",
                "UNII:11P2JDE17B",
                "unii:11P2JDE17B",
                "uNIi:11P2JDE17B",
                "unii.unii:11P2JDE17B",
            ),
            (
                "UCMIRNVEIXFBKS-UHFFFAOYSA-N",
                "dB03107",
                "DRUGBANK:dB03107",
                "drugbank:dB03107",
                "DrugBaNK:dB03107",
                "drugbank.id:dB03107",
            ),
        ]

        results_aggregation = []
        endpoint = "chem"
        for query_collection in curie_id_testing_collection:
            base_result = self.request(
                f"{endpoint}/{query_collection[0]}", expect=200)

            delimiter = ","
            data_mapping = {
                "ids": delimiter.join([f'"{query}"' for query in query_collection])
            }

            query_results = self.request(
                endpoint, method="POST", data=data_mapping
            ).json()
            assert len(query_results) == len(query_collection)

            batch_result = []
            for query_result, query_entry in zip(query_results, query_collection):
                return_query_field = query_result.pop("query")
                assert return_query_field == str(query_entry)
                batch_result.append(base_result.json() == query_result)

            aggregate_result = all(results_aggregation)

            if aggregate_result:
                logger.info(f"Query group {query_collection} succeeded")
            else:
                logger.info(f"Query group {query_collection} failed")

            results_aggregation.append(aggregate_result)
        assert all(results_aggregation)
