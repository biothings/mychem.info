import csv
import re
import sys

from biothings.utils.dataload import dict_sweep, unlist

try:
    from biothings import config
    logging = config.logger
except ImportError:
    import logging
    LOG_LEVEL = logging.INFO
    logging.basicConfig(level=LOG_LEVEL, format='%(asctime)s: %(message)s')

csv.field_size_limit(sys.maxsize)


def load_data(tsv_file):
    _file = open(tsv_file)
    reader = csv.DictReader(_file, delimiter='\t')
    _dict = {}
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
            ('National Drug Code Directory', 'ndc'),
            ('Drugs Product Database (DPD)', 'dpd'),
            ('FDA Drug Label at DailyMed', 'dailymed.setid'),
        ]
        res = []
        for v in xrefs.split(','):
            for rf_orig, rf_new in rename_fields:
                if rf_orig in v:
                    v = v.replace(rf_orig, rf_new)
            # Multiple replacements on the 'Web Resource' field
            if 'Web Resource' in v:
                if 'http://en.wikipedia.org/wiki/' in v:
                    v = v.replace('Web Resource', 'wikipedia.url_stub').replace(
                        'http://en.wikipedia.org/wiki/', '')
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

    def extract_primary_id(value):
        # Here, we prioritize extracting the numeric value before any comma.
        # This function returns the first numeric sequence found in the string.
        matches = re.findall(r'\d+', value)
        return int(matches[0]) if matches else None

    for key, val in iter(d.items()):
        if key in _li:
            for ele in val:
                idx = ele.find(':')
                k = transform_xrefs_fieldnames(ele[0:idx])
                v = ele[idx+1:].strip()

                if k in ["pubchem.cid", "pubchem.sid"]:
                    try:
                        v = int(v)
                    except ValueError:
                        v = extract_primary_id(v)
                        if v is None:
                            logging.warning(
                                f"Failed to extract primary ID for {k}: {ele}. Skipping this entry.")
                            continue

                # Handle nested elements (ex: 'wikipedia.url_stub') here
                sub_d = sub_field(k, v)
                _d.update(sub_d)

    if 'external_vocabulary' in d.keys():
        d.pop('external_vocabulary')
    d.update({'xrefs': _d})
    return d


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
    fields = [
        ('Chemical Abstracts Service', 'cas'),
        ('Therapeutic Targets Database', 'ttd'),
        ('PubChem Substance', 'pubchem.sid'),
        ('PubChem Compound', 'pubchem.cid')
    ]
    for orig_f, new_f in fields:
        if orig_f in k:
            k = k.replace(orig_f, new_f)
            break
    k = k.lower().replace(' ', '_').replace('-', '_')
    return k
