import os
import xml.etree.ElementTree as ET
import gzip
import re

from biothings.utils.dataload import value_convert_to_number


def camel_to_snake(s):
    """Convert camelCase strings to snake_case"""
    s = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', s)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s).lower()


def dict_to_snake_case(d, skipped_keys=[]):
    """Recursively convert a dictionary's keys to snake_case, while removing spaces and '-'.
    We must iterate items twice, because modifying the key can change the order of items.
    The first pass freezes the items in their current order, and the second modifies them.
    """
    items = []
    for key, val in d.items():
        items.append((key, val))
    for key, val in items:
        if isinstance(val, dict):
            dict_to_snake_case(val, skipped_keys)
        if type(key) == str and key not in skipped_keys:
            new_key = key
            if not key.islower():
                new_key = camel_to_snake(key)
            if " " in key or "-" in key:
                new_key = new_key.replace("-", "_").replace(" _", "_").replace(" ", "_")
            if new_key != key:
                d[new_key] = val
                del d[key]
    return d


def load_annotations(input_file):
    """Main function to load data from individual xml files"""

    # use gzip to read the .gz file
    unzipped_file = gzip.open(input_file, 'rb')

    """ Keep track of tags, whereby these change to true the next item in the appropriate element
    will be the relevant value
    """
    PC_count = False
    inchi = False
    inchikey = False
    hydrogen_bond_acceptor = False
    hydrogen_bond_donor = False
    rotatable_bond = False
    iupac = False
    logp = False
    mass = False
    molecular_formula = False
    molecular_weight = False
    smiles = False
    topological = False
    monoisotopic_weight = False
    complexity = False

    """ Use ET.iterparse to loop through the xml line by line.
    Note:
    The 'end' events are used whenever we need to obtain elem.text field, because
    the text, tail, and children of an element are not necessarily present when receiving
    the start event. Only the end event guarantees that the Element has been parsed completely.
    """
    for event, elem in ET.iterparse(unzipped_file, events=("start", "end")):
        prefix, has_namespace, postfix = elem.tag.partition('}')
        if has_namespace:
            elem.tag = postfix  # strip all namespaces
        # Maximum one of these flags sould be activated at any given time
        flags = [PC_count, inchi, inchikey, hydrogen_bond_acceptor, hydrogen_bond_donor,
                 rotatable_bond, iupac, logp, mass, molecular_formula, molecular_weight,
                 smiles, topological, monoisotopic_weight, complexity]
        assert sum(flags) <= 1, "Bad parsing. Only one flag at most should be active."
        # all of the compound properties will be inside this element
        if((elem.tag == "PC-CompoundType_id_cid") & (event == 'end')):
            # Start a new compound record
            current_compound = {}
            compound_data = {}

            # Reset flags
            PC_count = False
            inchi = False
            inchikey = False
            hydrogen_bond_acceptor = False
            hydrogen_bond_donor = False
            rotatable_bond = False
            iupac = False
            logp = False
            mass = False
            molecular_formula = False
            molecular_weight = False
            smiles = False
            topological = False
            monoisotopic_weight = False
            complexity = False

            compound_data["cid"] = elem.text
            compound_data["iupac"] = {}
            compound_data["smiles"] = {}
            assert elem.text != None, "Every document must have a CID."

        elif((elem.tag == "PC-Compound") & (event == 'end')):
            # Document parsing is complete
            current_compound["pubchem"] = compound_data
            assert current_compound.get("_id"), "Document {} is missing an _id".format(current_compound)
            # Convert numeric values to float or integer
            current_compound = value_convert_to_number(current_compound)
            # Convert keys to snake_case
            current_compound = dict_to_snake_case(current_compound)
            # yield the compound
            yield(current_compound)
            # clear element from memory
            elem.clear()

        elif((elem.tag == "PC-Compound_charge") & (event == 'end')):
            if(elem.text):
                compound_data["formal_charge"] = elem.text
        elif((elem.tag == "PC-Count") & (event == 'start')):
            PC_count = True
        elif((elem.tag == "PC-Count") & (event == 'end')):
            PC_count = False
        elif(PC_count):
            if(elem.text):
                if((elem.tag == "PC-Count_heavy-atom") & (event == 'end')):
                    compound_data["heavy_atom_count"] = elem.text
                elif((elem.tag == "PC-Count_atom-chiral-def") & (event == 'end')):
                    compound_data["defined_chiral_atom_count"] = elem.text
                elif((elem.tag == "PC-Count_bond-chiral-def") & (event == 'end')):
                    compound_data["defined_chiral_bond_count"] = elem.text
                elif((elem.tag == "PC-Count_atom-chiral-undef") & (event == 'end')):
                    compound_data["undefined_chiral_atom_count"] = elem.text
                elif((elem.tag == "PC-Count_bond-chiral-undef") & (event == 'end')):
                    compound_data["undefined_chiral_bond_count"] = elem.text
                elif((elem.tag == "PC-Count_isotope-atom") & (event == 'end')):
                    compound_data["isotope_atom_count"] = elem.text
                elif((elem.tag == "PC-Count_covalent-unit") & (event == 'end')):
                    compound_data["covalent_unit_count"] = elem.text
                elif((elem.tag == "PC-Count_tautomers") & (event == 'end')):
                    compound_data["tautomers_count"] = elem.text
        elif((elem.tag == "PC-Count") & (event == 'start')):
            PC_count = True
        elif((elem.tag == "PC-Count") & (event == 'end')):
            PC_count = False

        elif((elem.tag == "PC-Urn_label") & (event == 'end')):
            if(elem.text == 'InChI'):
                inchi = True
            elif(elem.text == 'InChIKey'):
                inchikey = True
            elif(elem.text == 'IUPAC Name'):
                iupac = True
            elif(elem.text == "Log P"):
                logp = True
            elif(elem.text == "Mass"):
                mass = True
            elif(elem.text == "Molecular Formula"):
                molecular_formula = True
            elif(elem.text == "Molecular Weight"):
                molecular_weight = True
            elif(elem.text == "SMILES"):
                smiles = True
            elif(elem.text == "Topological"):
                topological = True
            elif(elem.text == "Weight"):
                monoisotopic_weight = True
            elif(elem.text == "Compound Complexity"):
                complexity = True

        elif((elem.tag == "PC-Urn_name") & (event == 'end')):
            if(elem.text == 'Hydrogen Bond Acceptor'):
                hydrogen_bond_acceptor = True
            elif(elem.text == 'Hydrogen Bond Donor'):
                hydrogen_bond_donor = True
            elif(elem.text == 'Rotatable Bond'):
                rotatable_bond = True
            elif(iupac):
                iupac_key = elem.text
            elif(smiles):
                smiles_key = elem.text

        elif((elem.tag == "PC-InfoData_value_sval") & (event == 'end')):
            if(inchi):
                if(elem.text):
                    compound_data["inchi"] = elem.text
                inchi = False
            elif(inchikey):
                if(elem.text):
                    current_compound["_id"] = elem.text
                    compound_data["inchikey"] = elem.text
                inchikey = False
            elif(iupac):
                if(iupac_key):
                    if(elem.text):
                        compound_data['iupac'][iupac_key] = elem.text
                iupac = False
            elif(molecular_weight):
                if(elem.text):
                    compound_data["molecular_weight"] = elem.text
                molecular_weight = False
            elif(monoisotopic_weight):
                if(elem.text):
                    compound_data["monoisotopic_weight"] = elem.text
                monoisotopic_weight = False
            elif(mass):
                if(elem.text):
                    compound_data["exact_mass"] = elem.text
                mass = False
            elif(molecular_formula):
                if(elem.text):
                    compound_data["molecular_formula"] = elem.text
                molecular_formula = False
            elif(smiles):
                if(smiles_key):
                    if(elem.text):
                        compound_data['smiles'][smiles_key] = elem.text
                smiles = False

        elif((elem.tag == "PC-InfoData_value_ival") & (event == 'end')):
            if(hydrogen_bond_acceptor):
                if(elem.text):
                    compound_data["hydrogen_bond_acceptor_count"] = elem.text
                hydrogen_bond_acceptor = False
            elif(hydrogen_bond_donor):
                if(elem.text):
                    compound_data["hydrogen_bond_donor_count"] = elem.text
                hydrogen_bond_donor = False
            elif(rotatable_bond):
                if(elem.text):
                    compound_data["rotatable_bond_count"] = elem.text
                rotatable_bond = False

        elif((elem.tag == "PC-InfoData_value_fval") & (event == 'end')):
            if(logp):
                if(elem.text):
                    compound_data["xlogp"] = elem.text
                logp = False
            elif(topological):
                if(elem.text):
                    compound_data["topological_polar_surface_area"] = elem.text
                topological = False
            elif(complexity):
                if(elem.text):
                    compound_data["complexity"] = elem.text
                complexity = False


if __name__ == "__main__":
    import json
    import sys

    annotations = load_annotations(sys.argv[1])
    for a in annotations:
        print(json.dumps(a, indent=2))
