import xmltodict
import json
import math
import collections
import logging

from biothings.utils.dataload import dict_sweep, boolean_convert
from biothings.utils.dataload import boolean_convert, to_int
from biothings.utils.dataload import float_convert, int_convert
from biothings.utils.dataload import unlist_incexcl as unlist


def load_data(xml_file):
    drug_list = []

    def handle(path, item):  # streaming mode of xmltodict
        doc = restructure_dict(item)
        # try to normalize to inchi key
        try:
            _id = doc["drugbank"]['inchi_key']
            doc["_id"] = _id
        except KeyError:
            pass
        drug_list.append(doc)
        return True
    with open(xml_file, 'rb') as f:
        xmltodict.parse(f, item_depth=2, item_callback=handle,
                        xml_attribs=True)
    for doc in drug_list:
        yield doc


def restr_protein_dict(dictionary):
    _li1 = ['id', 'name', 'organism']
    _dict = {}
    for x, y in iter(dictionary.items()):
        if x in _li1:
            _dict.update({x: y})
        elif x == 'actions' and y:
            for z in y:
                _dict.update({x: y[z]})
        elif x == 'known-action':
            x = x.replace('-', '_')
            _dict.update({x: dictionary['known-action']})
        elif x == 'polypeptide':
            _li2 = ['general-function', 'specific-function', 'gene-name']
            for i in y:
                if i == "@id":
                    _dict.update({'uniprot': y[i]})
                elif i == "@source":
                    _dict.update({'source': y[i]})
                elif i in _li2:
                    j = i.replace('-', '_')
                    _dict.update({j: y[i]})
        elif x == 'references' and y:
            # extract a list of pubmed-ids
            pubmed_lst = []
            try:
                articles = y['articles']['article']
            except (KeyError, TypeError):
                articles = []
            if isinstance(articles, list):
                for article in articles:
                    pubmed_lst.append(to_int(article['pubmed-id']))
            else:
                pubmed_lst.append(to_int(articles['pubmed-id']))
            _dict.update({'pmids': pubmed_lst})
    return _dict


def restructure_dict(dictionary):
    restr_dict = dict()
    d1 = dict()
    pred_properties_dict = {}
    exp_prop_dict = {}
    products_list = []
    categories_list = []
    enzymes_list = []
    targets_list = []
    carriers_list = []
    transporters_list = []
    atccode_list = []
    xrefs_dict = {}
    xrefs_pubchem_dict = {}

    for key, value in iter(dictionary.items()):
        if key == 'name' and value:
            d1[key] = value

        elif key == 'drugbank-id' and value:
            # NOTE: 'drugbank.drugbank_id' has been moved to 'drugbank.id'
            key = 'id'
            id_list = []
            if isinstance(value, list):
                for ele in value:
                    if isinstance(ele, collections.OrderedDict):
                        assert "@primary" in ele
                        for x, y in iter(ele.items()):
                            if x == '#text':
                                # make sure we always have DB ID as drugbank_id (now 'id')
                                d1.update({key: y})
                                restr_dict['_id'] = y

                    if isinstance(ele, str):
                        id_list.append(ele)
                        d1.update({'accession_number': id_list})

            elif isinstance(value, dict) or isinstance(value, collections.OrderedDict):
                for x, y in iter(value.items()):
                    if x == '#text':
                        id_list.append(y)
                        d1.update({key: id_list})
                        restr_dict['_id'] = y

        elif key == 'description':
            d1.update({'pharmacology': {key: value}})

        elif key == 'groups':
            for i, j in iter(value.items()):
                d1[key] = j

        elif key == 'general-references':
            pubmed_lst = []
            try:
                articles = value['articles']['article']
            except (KeyError, TypeError):
                articles = []
            if isinstance(articles, list):
                for article in articles:
                    pubmed_lst.append(to_int(article['pubmed-id']))
            else:
                pubmed_lst.append(to_int(articles['pubmed-id']))
            d1['pmids'] = pubmed_lst

        elif key == 'indication':
            d1['pharmacology'].update({key: value})

        elif key == 'pharmacodynamics':
            d1['pharmacology'].update({key: value})

        elif key == 'mechanism-of-action':
            key = key.replace('-', '_')
            d1['pharmacology'].update({key: value})

        elif key == 'toxicity':
            d1['pharmacology'].update({key: value})

        elif key == 'metabolism':
            d1['pharmacology'].update({key: value})

        elif key == 'absorption':
            d1['pharmacology'].update({key: value})

        elif key == 'half-life':
            key = key.replace('-', '_')
            d1['pharmacology'].update({key: value})

        elif key == 'protein-binding':
            key = key.replace('-', '_')
            d1['pharmacology'].update({key: value})

        elif key == 'route-of-elimination':
            key = key.replace('-', '_')
            d1['pharmacology'].update({key: value})

        elif key == 'volume-of-distribution':
            key = key.replace('-', '_')
            d1['pharmacology'].update({key: value})

        elif key == 'clearance':
            d1['pharmacology'].update({key: value})

        elif key == 'classification' and value:
            for m, n in iter(value.items()):
                m = m.lower().replace('-', '_')
                d1.update({'taxonomy': value})

        elif key == 'salts' and value:
            salts_list = []

            for m, n in iter(value.items()):
                if isinstance(n, list):
                    for ele in n:
                        salt_tmp = {}
                        for k in ele:
                            if k in ['name', 'unii', 'cas-number', 'inchikey', 'average-mass', 'monoisotopic-mass']:
                                salt_tmp[k] = ele[k]
                        salts_list.append(salt_tmp)
                    d1.update({key: salts_list})

                elif isinstance(n, dict) or isinstance(n, collections.OrderedDict):
                    salt_tmp = {}
                    for k in n:
                        if k in ['name', 'unii', 'cas-number', 'inchikey', 'average-mass', 'monoisotopic-mass']:
                            salt_tmp[k] = n[k]
                    d1.update({key: salt_tmp})

        elif key == 'synonyms' and value:
            synonym_list = []
            if isinstance(value, collections.OrderedDict):
                for x, y in iter(value.items()):
                    for ele in y:
                        for name in ele:
                            if name == '#text':
                                synonym_list.append(ele[name])
                                d1.update({key: synonym_list})

        elif key == 'products' and value:
            def restr_product_dict(dictionary):
                products_dict = {}
                for x in dictionary:
                    if x == 'name':
                        products_dict[x] = dictionary[x]
                    elif x == 'dosage-form':
                        products_dict['dosage_form'] = dictionary[x]
                    elif x == 'strength':
                        products_dict[x] = dictionary[x]
                    elif x == 'route':
                        products_dict[x] = dictionary[x]
                    elif x == 'over-the-counter':
                        products_dict['otc'] = dictionary[x]
                    elif x == 'generic':
                        products_dict[x] = dictionary[x]
                    elif x == 'ndc-id':
                        products_dict['ndc_id'] = dictionary[x]
                    elif x == 'ndc-product-code':
                        products_dict['ndc_product_code'] = dictionary[x]
                    elif x == 'dpd-id':
                        products_dict['dpd'] = dictionary[x]
                    elif x == 'started-marketing-on':
                        products_dict[x.replace('-', '_')] = dictionary[x]
                    elif x == 'ended-marketing-on':
                        products_dict[x.replace('-', '_')] = dictionary[x]
                    elif x == 'fda-application-number':
                        products_dict[x.replace('-', '_')] = dictionary[x]
                    elif x == 'approved':
                        products_dict[x] = dictionary[x]
                    elif x == 'country':
                        products_dict[x] = dictionary[x]
                    elif x == 'source':
                        products_dict[x] = dictionary[x]
                return products_dict

            for x, y in iter(value.items()):
                if isinstance(y, dict) or isinstance(y, collections.OrderedDict):
                    _d = restr_product_dict(y)
                    products_list.append(_d)

                elif isinstance(y, list):
                    for _d in y:
                        products_list.append(restr_product_dict(_d))

        elif key == 'packagers' and value:
            pack_list = []
            for pack in value:
                for pack1 in value[pack]:
                    for s in pack1:
                        if s == 'name' and pack1[s]:
                            pack_list.append(pack1[s])
                            d1.update({key: pack_list})

        elif key == 'manufacturers' and value:
            manuf_list = []
            for x, y in iter(value.items()):
                if isinstance(y, dict) or isinstance(y, collections.OrderedDict):
                    for i in y:
                        if i == '#text':
                            manuf_list.append(y[i])
                            d1.update({key: manuf_list})

                if isinstance(y, list):
                    for i in y:
                        for m, n in iter(i.items()):
                            if m == '#text':
                                manuf_list.append(n)
                                d1.update({key: manuf_list})

        elif key == 'categories' and value:
            for x, y in iter(value.items()):
                d1.update({key: y})

        elif key == "snp-effects" and value:
            key = key.replace('-', '_')
            d1['pharmacology'].update({key: value})
        elif key == "snp-adverse-drug-reactions" and value:
            key = key.replace('-', '_')
            d1['pharmacology'].update({key: value})

        elif key == 'affected-organisms' and value:
            for x, y in iter(value.items()):
                key = key.replace('-', '_')
                d1['pharmacology'].update({key: value["affected-organism"]})

        elif key == 'ahfs-codes' and value:
            for x in value:
                key = key.replace('-', '_')
                xrefs_dict.update({key: value[x]})

        elif key == 'food-interactions' and value:
            food_interaction_list = []
            for x, y in iter(value.items()):
                if isinstance(y, list):
                    key = key.replace('-', '_')
                    for i in y:
                        food_interaction_list.append(i)
                        d1.update({key: food_interaction_list})
                else:
                    d1.update({key: y})

        elif key == 'drug-interactions' and value:
            key = key.replace('-', '_')
            for x, y in iter(value.items()):
                d1.update({key: y})

        elif key == 'sequences' and value:
            for x, y in iter(value.items()):
                for i in y:
                    if i == '@format':
                        str1 = y[i]+'_sequences'
                        d1[str1] = y['#text'].replace('\n', ' ')

        elif key == 'experimental-properties' and value:
            key = 'experimental_properties'

            def restr_properties_dict(dictionary):
                # Note: the side effect of this function sets a global variable
                for x, y in iter(dictionary.items()):
                    k1 = dictionary['kind']
                    k1 = k1.lower().replace(' ', '_').replace('-', '_')
                    if k1 == "isoelectric_point":
                        # make sure value are floats, if intervals, then list(float)
                        try:
                            exp_prop_dict[k1] = float(dictionary['value'])
                        except ValueError:
                            # not a float, maybe a range ? "5.6 - 7.6"
                            vals = dictionary['value'].split("-")
                            try:
                                for i, val in enumerate([v for v in vals]):
                                    vals[i] = float(val)
                                logging.info("Document ID '%s' has a range " % restr_dict["_id"] +
                                             "as isoelectric_point: %s" % vals)
                                exp_prop_dict[k1] = vals
                            except ValueError as e:
                                # not something we can handle, skip it
                                logging.warning("Document ID '%s' has non-convertible " % restr_dict["_id"] +
                                                " value for isoelectric_point, field ignored: %s" % dictionary['value'])
                                continue
                    else:
                        exp_prop_dict[k1] = dictionary['value']

            for ele in value:
                if isinstance(value[ele], list):
                    for _d in value[ele]:
                        restr_properties_dict(_d)

                elif isinstance(value[ele], dict) or isinstance(value[ele], collections.OrderedDict):
                    restr_properties_dict(value[ele])

                else:
                    raise ValueError(
                        "Unexpted type for 'experimental-properties'")

        elif key == 'calculated-properties' and value:
            def restr_properties_dict(dictionary):
                for x in dictionary:
                    k = dictionary['kind']
                    k = k.lower().replace(' ', '_').replace('-', '_')
                    if dictionary['kind'] == "IUPAC Name":
                        d1.update({'iupac': dictionary['value']})
                    elif dictionary['kind'] == "Traditional IUPAC Name":
                        d1.update(
                            {'traditional_iupac_name': dictionary['value']})
                    elif dictionary['kind'] == "SMILES":
                        d1.update({'smiles': dictionary['value']})
                    elif dictionary['kind'] == "Molecular Formula":
                        d1.update({'formula': dictionary['value']})
                    elif dictionary['kind'] == "InChI":
                        d1.update({'inchi': dictionary['value']})
                    elif dictionary['kind'] == "InChIKey":
                        if dictionary['value'][0:9] == 'InChIKey=':
                            d1.update({'inchi_key': dictionary['value'][9:]})
                        else:
                            d1.update({'inchi_key': dictionary['value']})
                    elif dictionary['kind'] == "Molecular Weight":
                        d1.update({'weight': {'average': dictionary['value']}})
                    elif dictionary['kind'] == "Monoisotopic Weight":
                        d1['weight'].update(
                            {'monoisotopic': dictionary['value']})
                    else:
                        pred_properties_dict[k] = dictionary['value']

            for x, y in iter(value.items()):
                if isinstance(y, list):
                    for _d in y:
                        _d = restr_properties_dict(_d)

                if isinstance(y, dict) or isinstance(y, collections.OrderedDict):
                    _d = restr_properties_dict(y)

        elif key == 'external-identifiers' and value:
            kegg_dict = {}
            for ele in value['external-identifier']:
                for x in ele:
                    if x == 'resource':
                        if ele[x] == "Drugs Product Database (DPD)":
                            xrefs_dict['dpd'] = ele['identifier']
                        elif ele[x] == "KEGG Drug":
                            kegg_dict['did'] = ele['identifier']
                            xrefs_dict['kegg'] = kegg_dict
                        elif ele[x] == "KEGG Compound":
                            kegg_dict['cid'] = ele['identifier']
                            xrefs_dict['kegg'] = kegg_dict
                        elif ele[x] == "PharmGKB":
                            xrefs_dict['pharmgkb'] = ele['identifier']
                        elif ele[x] == "Wikipedia":
                            wiki_dict = {'url_stub': ele['identifier']}
                            xrefs_dict['wikipedia'] = wiki_dict
                        elif ele[x] == "ChemSpider":
                            xrefs_dict['chemspider'] = ele['identifier']
                        elif ele[x] == "ChEBI":
                            xrefs_dict['chebi'] = 'CHEBI:' + \
                                str(ele['identifier'])
                        elif ele[x] == "PubChem Compound":
                            xrefs_pubchem_dict['cid'] = ele['identifier']
                        elif ele[x] == "PubChem Substance":
                            xrefs_pubchem_dict['sid'] = ele['identifier']
                        else:
                            source = ele[x].lower().replace(
                                '-', '_').replace(' ', '_')
                            xrefs_dict[source] = ele['identifier']

        elif key == 'external-links' and value:
            if isinstance(value['external-link'], list):
                for ele in value['external-link']:
                    for x in ele:
                        try:
                            resource = ele['resource']
                            xrefs_dict[resource.lower().replace(
                                '.', '_')] = ele['url']
                        except:
                            pass
            else:
                try:
                    resource = ele['resource']
                    d1[resource.lower().replace('.', '_')] = ele['url']
                except:
                    pass

        elif key == 'patents' and value:
            if isinstance(value, dict):
                for x in value:
                    d1.update({key: value[x]})

        elif key == 'international-brands' and value:
            key = key.lower().replace('-', '_')
            d1.update({key: value['international-brand']})

        elif key == 'mixtures' and value:
            # only accept mixture entries that have more than 1 ingredient
            mixture_lst = []
            for mixture in value['mixture']:
                if isinstance(mixture, collections.OrderedDict):
                    if '+' in mixture['ingredients']:
                        ingredient_lst = mixture['ingredients'].split(" + ")
                        mixture['ingredients'] = ingredient_lst
                        mixture_lst.append(mixture)
            if mixture_lst:
                # remove duplicates from the mixture_lst
                # convert 'ingredients' to tuples
                for m in mixture_lst:
                    m['ingredients'] = tuple(m['ingredients'])
                # remove duplicates by converting each dict to key-value tuple
                unique_mix_lst = [
                    dict(t) for t in {tuple(d.items()) for d in mixture_lst}]
                # convert 'ingredients' back to list
                for m in unique_mix_lst:
                    m['ingredients'] = list(m['ingredients'])

                # save results
                d1.update({key: unique_mix_lst})

        elif key == 'pathways' and value:
            _li = []

            def restr_pathway_dict(dictionary):
                _dict = {}
                for x, y in iter(dictionary.items()):
                    if x == 'smpdb-id':
                        _dict.update({'smpdb_id': y})
                    elif x == 'name':
                        _dict.update({x: y})
                    elif x == 'drugs':
                        pass
                    elif x == 'enzymes':
                        pass
                return _dict

            if isinstance(value['pathway'], list):
                for ele in value['pathway']:
                    _dict = restr_pathway_dict(ele)
                    _li.append(_dict)
                    d1.update({key: _li})

            elif isinstance(value['pathway'], dict) or isinstance(value['pathway'], OrderedDict):
                _dict = restr_pathway_dict(value['pathway'])
                _li.append(_dict)
                d1.update({key: _li})

        elif key == 'reactions' and value:
            _li = []

            def restr_reaction_dict(dictionary):
                _dict = {
                    "product": {
                        "drugbank_id": dictionary['right-element']['drugbank-id'],
                        "name": dictionary['right-element']['name']
                    }
                }
                if dictionary.get("enzymes"):
                    if isinstance(dictionary["enzymes"]['enzyme'], list):
                        _dict["enzymes"] = [
                            dict(item) for item in dictionary["enzymes"]['enzyme']]
                    else:
                        _dict["enzymes"] = dict(
                            dictionary["enzymes"]['enzyme'])
                return _dict

            if isinstance(value['reaction'], list):
                for ele in value['reaction']:
                    _dict = restr_reaction_dict(ele)
                    _li.append(_dict)
                    d1.update({key: _li})

            elif isinstance(value['reaction'], dict) or isinstance(value['reaction'], OrderedDict):
                _dict = restr_reaction_dict(value['reaction'])
                _li.append(_dict)
                d1.update({key: _li})

        elif key == 'targets' and value:
            if isinstance(value['target'], list):
                for dictionary in value['target']:
                    _dict = restr_protein_dict(dictionary)
                    targets_list.append(_dict)

            elif isinstance(value['target'], dict) or isinstance(value['target'], OrderedDict):
                _dict = restr_protein_dict(value['target'])
                targets_list.append(_dict)

        elif key == 'enzymes' and value:
            if isinstance(value['enzyme'], list):
                for dictionary in value['enzyme']:
                    _dict = restr_protein_dict(dictionary)
                    enzymes_list.append(_dict)

            elif isinstance(value['enzyme'], dict) or isinstance(value['enzyme'], OrderedDict):
                _dict = restr_protein_dict(value['enzyme'])
                enzymes_list.append(_dict)

        elif key == 'transporters' and value:
            if isinstance(value['transporter'], list):
                for dictionary in value['transporter']:
                    _dict = restr_protein_dict(dictionary)
                    transporters_list.append(_dict)

            elif isinstance(value['transporter'], dict) or isinstance(value['transporter'], OrderedDict):
                _dict = restr_protein_dict(value['transporter'])
                transporters_list.append(_dict)

        elif key == 'carriers' and value:
            if isinstance(value['carrier'], list):
                for dictionary in value['carrier']:
                    _dict = restr_protein_dict(dictionary)
                    carriers_list.append(_dict)

            elif isinstance(value['carrier'], dict) or isinstance(value['carrier'], OrderedDict):
                _dict = restr_protein_dict(value['carrier'])
                carriers_list.append(_dict)

        elif key == 'atc-codes' and value:
            def restr_atccode_dict(dictionary):
                for x in dictionary:
                    if x == '@code':
                        atccode_list.append(dictionary[x])
                return atccode_list

            if isinstance(value['atc-code'], list):
                for _d in value['atc-code']:
                    restr_atccode_dict(_d)

            elif isinstance(value['atc-code'], dict) or isinstance(value['atc-code'], OrderedDict):
                restr_atccode_dict(value['atc-code'])

    xrefs_dict['atc_codes'] = atccode_list
    d1['targets'] = targets_list
    d1['carriers'] = carriers_list
    d1['enzymes'] = enzymes_list
    d1['transporters'] = transporters_list
    d1['predicted_properties'] = pred_properties_dict
    d1['experimental_properties'] = exp_prop_dict
    d1['products'] = products_list
    if xrefs_pubchem_dict:
        xrefs_dict['pubchem'] = xrefs_pubchem_dict
    d1['xrefs'] = xrefs_dict
    restr_dict['drugbank'] = d1
    restr_dict = unlist(restr_dict, [
        "drugbank.reactions",
        "drugbank.accession_number",
        "drugbank.id",
        "drugbank.chebi",
        "drugbank.inchi"
    ], [])
    restr_dict = boolean_convert(restr_dict, [
        "patents.pediatric-extension",
        "predicted_properties.mddr_like_rule",
        "predicted_properties.bioavailability",
        "predicted_properties.ghose_filter",
        "predicted_properties.rule_of_five",
        "products.generic",
        "products.otc",
        "products.approved",
        "products.pediatric-extension"
    ])
    # 'int' types
    restr_dict = int_convert(restr_dict,
                             include_keys=[
                                 "drugbank.pharmacology.snp_adverse_drug_reactions.reaction.pubmed-id",
                                 "drugbank.pharmacology.snp_effects.effect.pubmed-id",
                                 "drugbank.predicted_properties.physiological_charge",
                                 "drugbank.predicted_properties.rotatable_bond_count",
                                 "drugbank.predicted_properties.h_bond_acceptor_count",
                                 "drugbank.predicted_properties.h_bond_donor_count",
                                 "drugbank.predicted_properties.number_of_rings",
                                 "drugbank.xrefs.guide_to_pharmacology",
                                 "drugbank.xrefs.iuphar"])
    # 'float' types
    restr_dict = float_convert(restr_dict,
                               include_keys=[
                                   "drugbank.experimental_properties.caco2_permeability",
                                   "drugbank.experimental_properties.molecular_weight",
                                   "drugbank.experimental_properties.hydrophobicity",
                                   "drugbank.weight.monoisotopic",
                                   "drugbank.weight.average",
                                   "drugbank.predicted_properties.molecular_weight",
                                   "drugbank.predicted_properties.monoisotopic_weight"])
    # Mixed types coerced to floats
    restr_dict = float_convert(restr_dict,
                               include_keys=[
                                   "drugbank.salts.average-mass",
                                   "drugbank.salts.monoisotopic-mass",
                                   "drugbank.experimental_properties.logp",
                                   "drugbank.experimental_properties.logs",
                                   "drugbank.predicted_properties.logp",
                                   "drugbank.predicted_properties.logs",
                                   "drugbank.predicted_properties.pka_(strongest_basic)",
                                   "drugbank.predicted_properties.pka_(strongest_acidic)",
                                   "drugbank.predicted_properties.refractivity",
                                   "drugbank.predicted_properties.polarizability",
                                   "drugbank.predicted_properties.polar_surface_area_(psa)"])
    restr_dict = dict_sweep(restr_dict, vals=[None, math.inf, "INF", ".", "-", "", "NA", "none", " ",
                                              "Not Available", "unknown", "null", "None"])
    return restr_dict
