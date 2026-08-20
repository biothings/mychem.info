import csv
import re
import sys

from biothings.utils.dataload import dict_sweep, unlist

csv.field_size_limit(sys.maxsize)


def load_data(tsv_file):
    _file = open(tsv_file)
    reader = csv.DictReader(_file, delimiter='\t')
    for row in reader:
        _id = row["PharmGKB Accession Id"]
        _d = restr_dict(row)
        _d = clean_up(_d)
        _d = unlist(dict_sweep(_d))
        _dict = {'_id': _id, 'pharmgkb': _d}
        yield _dict


def restr_dict(d):
    def _restr_xrefs(xrefs):
        """Restructure field names related to the pharmgkb.xrefs field"""
        # Rename fields
        rename_fields = [
            ('FDA Drug Label at DailyMed', 'dailymed.setid'),
        ]
        res = []
        for v in xrefs.split(','):
            v = v.strip()
            for rf_orig, rf_new in rename_fields:
                if rf_orig in v:
                    v = v.replace(rf_orig, rf_new)
            # ClinPGx renamed the 'Web Resource' label to 'URL'.  Wikipedia
            # links are reduced to the page stub, everything else is kept as a
            # full URL under 'web_resource'.
            if v.startswith('URL:'):
                stub_match = re.match(
                    r'URL:https?://en\.wikipedia\.org/wiki/(.+)', v)
                if stub_match:
                    v = 'wikipedia.url_stub:' + stub_match.group(1)
                else:
                    v = v.replace('URL:', 'web_resource:', 1)
            # Add 'CHEBI:' prefix if not there already
            elif 'ChEBI:' in v and 'ChEBI:CHEBI' not in v:
                v = v.replace('ChEBI:', 'ChEBI:CHEBI:')
            elif 'ClinicalTrials.gov' in v:
                nct_match = re.search(r'ClinicalTrials\.gov:?\/?(NCT\d+)', v)
                if nct_match:
                    nct_number = nct_match.group(1)
                    v = f"clinicaltrials_gov:{nct_number}"
            res.append(v.strip())
        return res

    def _split_ingredients(ingredients_section):
        # This handles the splitting of ingredients, taking care of nested parentheses
        ingredients = []
        start = 0
        parenthesis_level = 0
        for i, char in enumerate(ingredients_section):
            if char == '(':
                parenthesis_level += 1
            elif char == ')':
                parenthesis_level -= 1
            elif char == '+' and parenthesis_level == 0:
                # Split at '+' only if we're not inside parentheses
                ingredients.append(ingredients_section[start:i].strip())
                start = i + 1
        # Add the last or only ingredient
        ingredients.append(ingredients_section[start:].strip())
        return ingredients

    def _parse_brand_mixtures(mixtures):
        parsed_mixtures = []
        for mixture in mixtures:
            if '(' in mixture and ')' in mixture:
                brand_name, ingredients_section = mixture.split('(', 1)
                brand_name = brand_name.strip()
                ingredients_section = ingredients_section.rsplit(
                    ')', 1)[0]
                ingredients = _split_ingredients(ingredients_section)
            else:
                brand_name = mixture.strip()
                ingredients = []

            parsed_mixtures.append(
                {"brand_name": brand_name, "mixture": ingredients})
        return parsed_mixtures
    _d = {}
    for key, val in iter(d.items()):
        if key in ["SMILES", "Name", "Type", "InChI"]:
            _d.update({key.lower(): val})
        elif key in ["Trade Names", "Generic Names"]:
            # Convert to list if not empty, otherwise default to empty list
            _d.update({key.lower().replace(" ", "_")
                      : val.split(', ') if val else []})
        elif key == "Dosing Guideline":
            # Convert to boolean
            _d.update({"dosing_guideline": True if val == "Yes" else False})
        elif key == "PharmGKB Accession Id":
            _d.update({'id': val})
        elif key == "Cross-references":
            _d.update({"xrefs": _restr_xrefs(val)})
        elif key == "External Vocabulary":
            # Process and remove parentheses if present
            val = [remove_paren(each.strip()) for each in val.split(',')]
            _d.update({"external_vocabulary": val})
        elif key == "Brand Mixtures":
            if val:
                _d.update(
                    {"brand_mixtures": _parse_brand_mixtures(val.split(', '))})
    return _d


def clean_up(d):
    _li = ['xrefs', 'external_vocabulary']
    _d = {}
    for key, val in iter(d.items()):
        if key in _li:
            for ele in val:
                idx = ele.find(':')
                # Note:  original pharmgkb keys do not have '.'
                k = transform_xrefs_fieldnames(ele[0:idx])
                v = ele[idx+1:]
                if k in ["pubchem.cid", "pubchem.sid"]:
                    v = int(v)
                elif k == "clinpgx_tags":
                    # Values arrive double-prefixed as 'pgkbTags:<id>'
                    v = v.replace("pgkbTags:", "", 1)
                # Handle nested elements (ex: 'wikipedia.url_stub') here
                sub_d = sub_field(k, v)
                merge_sub_field(_d, sub_d)
    # 'xrefs' and 'external_vocabulary' are merged
    if 'external_vocabulary' in d.keys():
        d.pop('external_vocabulary')
    d.update({'xrefs': _d})
    return d


def merge_sub_field(target, source):
    """Merge a nested field dict into target, keeping existing sub-fields.

    A plain dict.update() would replace a whole sub-document, dropping sibling
    keys parsed earlier (ex: 'PubChem Compound' discarding 'PubChem Substance').
    """
    for key, val in source.items():
        if isinstance(val, dict) and isinstance(target.get(key), dict):
            merge_sub_field(target[key], val)
        else:
            target[key] = val
    return target


def sub_field(k, v):
    """Return a nested dictionary with field keys k and value v."""
    res = {}
    field_d = res
    fields = k.split('.')
    for f in fields[:-1]:
        field_d[f] = {}
        field_d = field_d[f]
    field_d[fields[-1]] = v
    return res


def remove_paren(v):
    """remove first occurance of trailing parentheses from a string"""
    idx = v.find('(')
    if idx != -1:
        return v[0:idx]
    return v


def transform_xrefs_fieldnames(k):
    # ClinPGx labels that do not lowercase cleanly into the mychem field name
    # they have always been stored under.
    fields = [
        ('PubChem Substance', 'pubchem.sid'),
        ('PubChem Compound', 'pubchem.cid'),
        ('NDF-RT', 'ndfrt'),
        ('UniProt', 'uniprotkb'),
        # 2-3 character PDB chemical component (HET) codes
        ('PDB Ligand', 'het')
    ]
    for orig_f, new_f in fields:
        if orig_f in k:
            k = k.replace(orig_f, new_f)
            break
    k = k.lower().replace(' ', '_').replace('-', '_')
    return k
