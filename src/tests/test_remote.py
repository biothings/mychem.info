"""
    Tests are grouped into three catagories

    - Data Integrity
    - Web Features
    - Special Cases

"""
import pytest
from biothings.tests.web import BiothingsDataTest


class MychemWebTest(BiothingsDataTest):

    host = 'mychem.info'

    inchikey_id = 'ZRALSGWEFCBTJO-UHFFFAOYSA-N'
    # drugbank_id = 'DB00551'
    chembl_id = 'CHEMBL1308'
    chebi_id = 'CHEBI:6431'
    unii_id = '7AXV542LZ4'
    pubchem_id = '60823'
    prefixed_pubchem_id = 'CID:60823'
    s = '基因'


class TestMychemDataIntegrity(MychemWebTest):

    # -----------
    # via Query
    # -----------

    def test_010(self):
        self.query(q='imatinib')

    @pytest.mark.skip("Drugbank has been removed")
    def test_011_drugbank_name(self):
        self.query(q='drugbank.name:imatinib')

    def test_012_chebi_name(self):
        # the assumption for this test is that it looks like the one
        # it is replacing (old 011 marked for skipping)
        self.query(q='chebi.name:caffeine')

    """ Drugbank was removed as a datasource on the 09/08/21 release
    def test_012(self):
        monobenzone = self.query(q='drugbank.name:monobenzone')
        assert 'drugbank' in monobenzone['hits'][0]
        assert 'name' in monobenzone['hits'][0]['drugbank']
        assert monobenzone['hits'][0]['drugbank']['name'].lower() == 'monobenzone'

    def test_013(self):
        P34981 = self.query(q='drugbank.targets.uniprot:P34981')
        assert 'drugbank' in P34981['hits'][0]
        assert 'targets' in P34981['hits'][0]['drugbank']
        assert 'uniprot' in P34981['hits'][0]['drugbank']['targets'][0]
        assert P34981['hits'][0]['drugbank']['targets'][0]['uniprot'] == 'P34981'

    def test_020(self):

        res = self.request("query", method='POST', data={
            'q': self.drugbank_id,
            'scopes': 'drugbank.id'
        }).json()

        assert len(res) == 1
        assert res[0]['_id'] == 'RRUDCFGSUDOHDG-UHFFFAOYSA-N'

    def test_021(self):

        res = self.request("query", method='POST', data={
            'q': self.drugbank_id + ',DB00441',
            'scopes': 'drugbank.id'
        }).json()

        assert len(res) == 2
        assert res[0]['_id'] == 'RRUDCFGSUDOHDG-UHFFFAOYSA-N'
        assert res[1]['_id'] == 'SDUQYLNIPVEERB-QPPQHZFASA-N'

    def test_022(self):

        res = self.request("query", method='POST', data={
            'q': self.drugbank_id,
            'scopes': 'drugbank.id',
            'fields': 'drugbank.id'
        }).json()

        assert len(res) == 1
        assert 'query' in res[0]
        assert 'drugbank' in res[0] and 'id' in res[0]['drugbank']
        assert res[0]['query'] == res[0]['drugbank']['id']

    def test_030(self):
        drugbank = self.request('drug/' + self.drugbank_id + '?fields=drugbank').json()
        assert 'drugbank' in drugbank
        assert 'id' in drugbank['drugbank']
        assert drugbank['drugbank']['id'] == self.drugbank_id
    """

    def test_031(self):
        chembl = self.request('drug/' + self.chembl_id + '?fields=chembl').json()
        assert 'chembl' in chembl
        assert 'molecule_chembl_id' in chembl['chembl']
        assert chembl['chembl']['molecule_chembl_id'] == self.chembl_id

    def test_032(self):
        unii = self.request('drug/' + self.unii_id + '?fields=unii').json()
        assert 'unii' in unii
        assert 'unii' in unii['unii']
        assert unii['unii']['unii'] == self.unii_id

    def test_033(self):
        chebi = self.request('drug/' + self.chebi_id + '?fields=chebi').json()
        assert 'chebi' in chebi
        assert 'id' in chebi['chebi']
        assert chebi['chebi']['id'] == self.chebi_id

    def test_034(self):
        pubchem = self.request('drug/' + self.pubchem_id + '?fields=pubchem').json()
        assert 'pubchem' in pubchem
        assert 'cid' in pubchem['pubchem']
        assert pubchem['pubchem']['cid'] == int(self.pubchem_id)

    def test_035(self):
        pubchem = self.request('drug/' + self.pubchem_id + '?fields=pubchem').json()
        prefixed_pubchem = self.request(
            'drug/' + self.prefixed_pubchem_id + '?fields=pubchem').json()
        assert prefixed_pubchem == pubchem

    def test_040(self):
        alls = [
            # {"q": "DB01076", "fields": "drugbank.id"},
            # {"q": "Siltuximab", "fields": "drugbank.name"},
            {"q": "IBUPROFEN", "fields": "ndc.substancename"},
            {"q": "fospropofol", "fields": "aeolus.drug_name"},
            {"q": "TOOSENDANIN", "fields": "chembl.pref_name"},
            {"q": "FLUPROPADINE", "fields": "ginas.preferred_name"},
            {"q": "IJT22X8U2Z", "fields": "unii.unii"},
        ]
        for d in alls:
            res = self.request('query?q=%(q)s&fields=%(fields)s&dotfield=true' % d).json()
            foundone = False
            for e in res["hits"]:
                if d["fields"] in e:
                    if d["q"] in e[d["fields"]]:
                        foundone = True
                        break
            assert foundone, "Expecting at least one result with q=%(q)s&fields=%(fields)s" % d

    def test_050(self):
        C0242339 = self.request(
            'query?q=drugcentral.drug_use.indication.umls_cui:C0242339').json()['hits'][0]
        assert 'drugcentral' in C0242339
        assert 'drug_use' in C0242339['drugcentral']
        assert 'indication' in C0242339['drugcentral']['drug_use']
        assert 'umls_cui' in C0242339['drugcentral']['drug_use']['indication']
        assert C0242339['drugcentral']['drug_use']['indication']['umls_cui'].lower() == 'c0242339'

    # ---------------
    # via Annotation
    # ---------------

    def test_100(self):
        res = self.request('drug/' + self.inchikey_id).json()
        assert '_id' in res

    def test_110(self):
        # test different endpoint aliases
        drug = self.request('drug/' + self.inchikey_id).json()
        chem = self.request('chem/' + self.inchikey_id).json()
        compound = self.request('compound/' + self.inchikey_id).json()

        assert drug == chem
        assert chem == compound

    def test_120(self):
        res = self.request("drug", method='POST', data={'ids': self.inchikey_id}).json()
        assert len(res) == 1
        assert res[0]['_id'] == self.inchikey_id

    def test_121(self):
        res = self.request("drug", method='POST', data={
                           'ids': self.inchikey_id + ',RRUDCFGSUDOHDG-UHFFFAOYSA-N'}).json()
        assert len(res) == 2
        assert res[0]['_id'] == self.inchikey_id
        assert res[1]['_id'] == 'RRUDCFGSUDOHDG-UHFFFAOYSA-N'

    def test_122(self):
        res = self.request("drug", method='POST',
                           data={'ids': self.inchikey_id + ',RRUDCFGSUDOHDG-UHFFFAOYSA-N',
                                 'fields': 'pubchem'}).json()
        assert len(res) == 2
        for _g in res:
            assert set(_g) == set(['_id', '_version', 'query', 'pubchem'])

    # -----------------
    # Metadata Related
    # -----------------

    def test_300(self):
        res = self.request('metadata/fields').json()
        # Check to see if there are enough keys
        assert len(res) > 490

        # Check some specific keys
        # assert 'drugbank' in res
        assert 'pubchem' in res
        assert 'ginas' in res
        assert 'aeolus' in res
        assert 'drugcentral' in res

    def test_310(self):
        # cadd license
        res = self.request('drug/' + self.inchikey_id).json()
        if 'aeolus' in res:
            assert '_license' in res['aeolus']
            assert res['aeolus']['_license']
        if 'chebi' in res:
            assert '_license' in res['chebi']
            assert res['chebi']['_license']
        if 'chembl' in res:
            assert '_license' in res['chembl']
            assert res['chembl']['_license']
        """
        if 'drugbank' in res:
            assert '_license' in res['drugbank']
            assert res['drugbank']['_license']
        """
        if 'drugcentral' in res:
            assert '_license' in res['drugcentral']
            assert res['drugcentral']['_license']
        if 'ginas' in res:
            assert '_license' in res['ginas']
            assert res['ginas']['_license']
        if 'pubchem' in res:
            assert '_license' in res['pubchem']
            assert res['pubchem']['_license']


class TestMychemWebFeatures(MychemWebTest):

    def test_fields(self):
        res = self.request('drug/{}?fields=pubchem'.format(self.inchikey_id)).json()
        assert set(res) == set(['_id', '_version', 'pubchem'])

    """
    def test_query_size_1(self):
        res = self.request('query?q=drugbank.name:acid&fields=drugbank.name').json()
        assert len(res['hits']) == 10  # default

    def test_query_size_2(self):
        res = self.request('query?q=drugbank.name:acid&fields=drugbank.name&size=1000').json()
        assert len(res['hits']) == 1000

    def test_query_size_3(self):
        self.request('query?q=drugbank.name:acid&fields=drugbank.name&size=1001', expect=400)

    def test_query_size_4(self):
        self.request('query?q=drugbank.name:acid&fields=drugbank.name&size=2000', expect=400)

    def test_facets(self):
        res = self.request(
            'query?q=drugbank.name:acid&size=0&facets=drugbank.weight.average').json()
        assert 'facets' in res and 'drugbank.weight.average' in res['facets']

    def test_fetch_all(self):
        q = 'drugbank.name:acid&fields=drugbank.name&fetch_all=TRUE'
        res = self.request('query?q=' + q).json()
        assert '_scroll_id' in res
        assert 'hits' in res
        # get one set of results
        res2 = self.request('query?scroll_id=' + res['_scroll_id']).json()
        assert 'hits' in res2


    def test_msgpack_2(self):
        res = self.request('query?q=drugbank.id:{}&size=1'.format(self.drugbank_id)).json()
        res2 = self.msgpack_ok(self.request(
            'query?q=drugbank.id:{}&size=1&format=msgpack'.format(self.drugbank_id)).content)
        assert res
        assert res2
    """
    def test_msgpack_1(self):
        res = self.request('drug/' + self.inchikey_id).json()
        res2 = self.msgpack_ok(self.request(
            'drug/{}?format=msgpack'.format(self.inchikey_id)).content)
        assert res
        assert res2

    def test_msgpack_3(self):
        res = self.request('metadata').json()
        res2 = self.msgpack_ok(self.request('metadata?format=msgpack').content)
        assert res
        assert res2

    def test_metadata(self):
        self.request('metadata')


class TestMychemSpecialInput(TestMychemWebFeatures):

    def test_01(self):
        res = self.request('query?q=\xef\xbf\xbd\xef\xbf\xbd').json()
        assert res['hits'] == []

    def test_02(self):
        # testing non-ascii character
        self.request('drug/' + self.inchikey_id +
                     '\xef\xbf\xbd\xef\xbf\xbdmouse', expect=404)

    def test_10(self):
        self.request("query")

    def test_11(self):
        self.request('drug', expect=400)

    def test_12(self):
        self.request('drug/', expect=400)

    def test_20_unicode(self):

        self.request('drug/' + self.s, expect=404)
        res = self.request("drug", method='POST', data={'ids': self.s}).json()
        assert res[0]['notfound']
        assert len(res) == 1

    def test_21_unicode(self):
        res = self.request("drug", method='POST', data={
                           'ids': self.inchikey_id + ',' + self.s}).json()
        assert res[1]['notfound']
        assert len(res) == 2

    def test_22_unicode(self):
        res = self.request('query?q=' + self.s).json()
        assert res['hits'] == []

    """
    def test_23_unicode(self):
        res = self.request("query", method='POST', data={
                           "q": self.s, "scopes": 'drugbank.id'}).json()
        assert res[0]['notfound']
        assert len(res) == 1

    def test_24_unicode(self):
        res = self.request("query", method='POST', data={
                           "q": self.drugbank_id + '+' + self.s, 'scopes': 'drugbank.id'}).json()
        assert res[1]['notfound']
        assert len(res) == 2
    """
