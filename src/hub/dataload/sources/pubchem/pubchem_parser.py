import gzip
import re

from biothings.utils.dataload import value_convert_to_number
from lxml import etree

CAMEL_RE_1 = re.compile(r'(.)([A-Z][a-z]+)')
CAMEL_RE_2 = re.compile(r'([a-z0-9])([A-Z])')


def camel_to_snake(s):
    """Convert camelCase strings to snake_case, keeping abbreviations together,
    and removing white space and dashes."""
    s = CAMEL_RE_1.sub(r'\1_\2', s)
    s = CAMEL_RE_2.sub(r'\1_\2', s).lower()
    s = s.replace("-", "_").replace(" _", "_").replace(" ", "_")
    return s


def load_annotations(input_file):
    """Load data from an XML file with error handling."""
    try:
        return parse_one_file(input_file)
    except etree.XMLSyntaxError:
        print("Error parsing file:", input_file)
        raise


def parse_one_file(input_file):
    """Parse one gzipped XML file using lxml.iterparse for speed."""
    unzipped_file = gzip.open(input_file, 'rb')

    # State flags for XML elements
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

    # Keys used when processing IUPAC and SMILES names
    iupac_key = None
    smiles_key = None

    current_compound = {}
    compound_data = {}

    # lxml iterparse (using "start" and "end" events)
    for event, elem in etree.iterparse(unzipped_file, events=("start", "end")):
        # Remove namespace if present
        if '}' in elem.tag:
            elem.tag = elem.tag.split('}', 1)[1]

        # Ensure that at most one flag is active at any given time.
        flags = [PC_count, inchi, inchikey, hydrogen_bond_acceptor, hydrogen_bond_donor,
                 rotatable_bond, iupac, logp, mass, molecular_formula, molecular_weight,
                 smiles, topological, monoisotopic_weight, complexity]
        assert sum(1 for flag in flags if flag) <= 1, \
            "Bad parsing on file {}, document {}. Only one flag should be active.".format(
                input_file, current_compound)

        # Start a new compound record.
        if elem.tag == "PC-CompoundType_id_cid" and event == 'end':
            current_compound = {}
            compound_data = {}
            # Reset all flags and keys
            PC_count = inchi = inchikey = hydrogen_bond_acceptor = hydrogen_bond_donor = \
                rotatable_bond = iupac = logp = mass = molecular_formula = molecular_weight = \
                smiles = topological = monoisotopic_weight = complexity = False
            iupac_key = None
            smiles_key = None

            compound_data["cid"] = elem.text
            compound_data["iupac"] = {}
            compound_data["smiles"] = {}
            assert elem.text is not None, \
                "File {} has document missing CID. Every document must have a CID.".format(
                    input_file)

        # Finish processing a compound record.
        elif elem.tag == "PC-Compound" and event == 'end':
            current_compound["pubchem"] = compound_data
            if current_compound.get("_id") is None:
                current_compound["_id"] = compound_data["cid"]
            assert current_compound.get("_id"), \
                "File {}, document {} is missing an _id".format(
                    input_file, current_compound)
            current_compound = value_convert_to_number(
                current_compound, skipped_keys=["_id", "pubchem.cid"])
            yield current_compound
            elem.clear()

        elif elem.tag == "PC-Compound_charge" and event == 'end':
            if elem.text:
                compound_data["formal_charge"] = elem.text

        # Manage PC-Count block
        elif elem.tag == "PC-Count":
            if event == 'start':
                PC_count = True
            elif event == 'end':
                PC_count = False

        elif PC_count and elem.text:
            if elem.tag == "PC-Count_heavy-atom" and event == 'end':
                compound_data["heavy_atom_count"] = elem.text
            elif elem.tag == "PC-Count_atom-chiral" and event == 'end':
                compound_data["chiral_atom_count"] = elem.text
            elif elem.tag == "PC-Count_bond-chiral" and event == 'end':
                compound_data["chiral_bond_count"] = elem.text
            elif elem.tag == "PC-Count_atom-chiral-def" and event == 'end':
                compound_data["defined_chiral_atom_count"] = elem.text
            elif elem.tag == "PC-Count_bond-chiral-def" and event == 'end':
                compound_data["defined_chiral_bond_count"] = elem.text
            elif elem.tag == "PC-Count_atom-chiral-undef" and event == 'end':
                compound_data["undefined_chiral_atom_count"] = elem.text
            elif elem.tag == "PC-Count_bond-chiral-undef" and event == 'end':
                compound_data["undefined_chiral_bond_count"] = elem.text
            elif elem.tag == "PC-Count_isotope-atom" and event == 'end':
                compound_data["isotope_atom_count"] = elem.text
            elif elem.tag == "PC-Count_covalent-unit" and event == 'end':
                compound_data["covalent_unit_count"] = elem.text
            elif elem.tag == "PC-Count_tautomers" and event == 'end':
                compound_data["tautomers_count"] = elem.text

        elif elem.tag == "PC-Urn_label" and event == 'end':
            text = elem.text
            if text == 'InChI':
                inchi = True
            elif text == 'InChIKey':
                inchikey = True
            elif text == 'IUPAC Name':
                iupac = True
            elif text == "Log P":
                logp = True
            elif text == "Mass":
                mass = True
            elif text == "Molecular Formula":
                molecular_formula = True
            elif text == "Molecular Weight":
                molecular_weight = True
            elif text == "SMILES":
                smiles = True
            elif text == "Topological":
                topological = True
            elif text == "Weight":
                monoisotopic_weight = True
            elif text == "Compound Complexity":
                complexity = True

        elif elem.tag == "PC-Urn_name" and event == 'end':
            text = elem.text
            if text == 'Hydrogen Bond Acceptor':
                hydrogen_bond_acceptor = True
            elif text == 'Hydrogen Bond Donor':
                hydrogen_bond_donor = True
            elif text == 'Rotatable Bond':
                rotatable_bond = True
            elif iupac:
                iupac_key = camel_to_snake(text)
            elif smiles:
                smiles_key = camel_to_snake(text)

        elif elem.tag == "PC-InfoData_value_sval" and event == 'end':
            if inchi:
                if elem.text:
                    compound_data["inchi"] = elem.text
                inchi = False
            elif inchikey:
                if elem.text:
                    current_compound["_id"] = elem.text
                    compound_data["inchikey"] = elem.text
                inchikey = False
            elif iupac:
                if iupac_key and elem.text:
                    compound_data['iupac'][iupac_key] = elem.text
                iupac = False
            elif molecular_weight:
                if elem.text:
                    compound_data["molecular_weight"] = elem.text
                molecular_weight = False
            elif monoisotopic_weight:
                if elem.text:
                    compound_data["monoisotopic_weight"] = elem.text
                monoisotopic_weight = False
            elif mass:
                if elem.text:
                    compound_data["exact_mass"] = elem.text
                mass = False
            elif molecular_formula:
                if elem.text:
                    compound_data["molecular_formula"] = elem.text
                molecular_formula = False
            elif smiles:
                if smiles_key and elem.text:
                    compound_data['smiles'][smiles_key] = elem.text
                smiles = False

        elif elem.tag == "PC-InfoData_value_ival" and event == 'end':
            if hydrogen_bond_acceptor:
                if elem.text:
                    compound_data["hydrogen_bond_acceptor_count"] = elem.text
                hydrogen_bond_acceptor = False
            elif hydrogen_bond_donor:
                if elem.text:
                    compound_data["hydrogen_bond_donor_count"] = elem.text
                hydrogen_bond_donor = False
            elif rotatable_bond:
                if elem.text:
                    compound_data["rotatable_bond_count"] = elem.text
                rotatable_bond = False

        elif elem.tag == "PC-InfoData_value_fval" and event == 'end':
            if logp:
                if elem.text:
                    compound_data["xlogp"] = elem.text
                logp = False
            elif topological:
                if elem.text:
                    compound_data["topological_polar_surface_area"] = elem.text
                topological = False
            elif molecular_weight:
                if elem.text:
                    compound_data["molecular_weight"] = elem.text
                molecular_weight = False
            elif monoisotopic_weight:
                if elem.text:
                    compound_data["monoisotopic_weight"] = elem.text
                monoisotopic_weight = False
            elif mass:
                if elem.text:
                    compound_data["exact_mass"] = elem.text
                mass = False
            elif complexity:
                if elem.text:
                    compound_data["complexity"] = elem.text
                complexity = False

    # End of iterparse loop


if __name__ == "__main__":
    import json
    import sys

    annotations = load_annotations(sys.argv[1])
    for a in annotations:
        print(json.dumps(a, indent=2))
