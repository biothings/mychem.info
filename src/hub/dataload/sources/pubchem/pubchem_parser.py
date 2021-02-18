import os
import xml.etree.ElementTree as ET
import gzip


def load_annotations(input_file):
    """Main function to load data from individual xml files"""

    ## keep track of tags, whereby these change to true the next item in the appropriate element
    ## will be the relevant value 

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

    ## use gzip to read the .gz file
    unzipped_file = gzip.open(input_file, 'rb')

    ## use ET.iterparse to loop through the xml line by line
    for event, elem in ET.iterparse(unzipped_file, events=("start","end")):
        prefix, has_namespace, postfix = elem.tag.partition('}')
        if has_namespace:
            elem.tag = postfix  # strip all namespaces
        ## all of the compound properties will be inside this element
        if((elem.tag == "PC-CompoundType_id_cid") & (event == 'start')):     
            current_compound = {}
            compound_data = {}
            current_compound["_id"] = elem.text
            compound_data["cid"] = elem.text
            compound_data["iupac"] = {}
            compound_data["smiles"] = {}
        elif((elem.tag == "PC-Compound") & (event == 'end')):
            current_compound["pubchem"] = compound_data
            ## rarely, some will be missing a cid. make sure this isn't the case
            if(current_compound["_id"]):
                ## yield the compound
                yield(current_compound)
            ## clear element from memory
            elem.clear()
        elif((elem.tag == "PC-Compound_charge") & (event == 'start')):
            if(elem.text):
                compound_data["formal_charge"] = elem.text
        elif((elem.tag == "PC-Count") & (event == 'start')):
            PC_count = True
        elif((elem.tag == "PC-Count") & (event == 'end')):
            PC_count = False
        elif(PC_count):
            if(elem.text):
                if((elem.tag == "PC-Count_heavy-atom") & (event == 'start')):
                    compound_data["heavy_atom_count"] = elem.text
                elif((elem.tag == "PC-Count_atom-chiral-def") & (event == 'start')):
                    compound_data["defined_chiral_atom_count"] = elem.text
                elif((elem.tag == "PC-Count_bond-chiral-def") & (event == 'start')):
                    compound_data["defined_chiral_bond_count"] = elem.text
                elif((elem.tag == "PC-Count_atom-chiral-undef") & (event == 'start')):
                    compound_data["undefined_chiral_atom_count"] = elem.text
                elif((elem.tag == "PC-Count_bond-chiral-undef") & (event == 'start')):
                    compound_data["undefined_chiral_bond_count"] = elem.text
                elif((elem.tag == "PC-Count_isotope-atom") & (event == 'start')):
                    compound_data["isotope_atom_count"] = elem.text
                elif((elem.tag == "PC-Count_covalent-unit") & (event == 'start')):
                    compound_data["covalent_unit_count"] = elem.text
                elif((elem.tag == "PC-Count_tautomers") & (event == 'start')):
                    compound_data["tautomers_count"] = elem.text
        elif((elem.tag == "PC-Count") & (event == 'start')):
            PC_count = True
        elif((elem.tag == "PC-Count") & (event == 'end')):
            PC_count = False
            
        elif((elem.tag == "PC-Urn_label") & (event == 'start')):
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

        elif((elem.tag == "PC-Urn_name") & (event == 'start')):
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

        elif((elem.tag == "PC-InfoData_value_sval") & (event == 'start')):
            if(inchi):
                if(elem.text):
                    compound_data["inchi"] = elem.text
                inchi = False  
            elif(inchikey):
                if(elem.text):
                    compound_data["inchikey"] = elem.text
                inchikey = False  
            elif(iupac):
                if(iupac_key):
                    if(elem.text):
                        compound_data['iupac'][iupac_key] = elem.text
                iupac = False
            elif(molecular_formula):
                if(elem.text):
                    compound_data["molecular_formula"] = elem.text
                molecular_formula = False
            elif(smiles):
                if(smiles_key):
                    if(elem.text):
                        compound_data['smiles'][smiles_key] = elem.text
                smiles = False
    
        elif((elem.tag == "PC-InfoData_value_ival") & (event == 'start')):
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
            
        elif((elem.tag == "PC-InfoData_value_fval") & (event == 'start')):
            if(logp):
                if(elem.text):
                    compound_data["xlogp"] = elem.text
                logp = False
            elif(mass):
                if(elem.text):
                    compound_data["exact_mass"] = elem.text
                mass = False
            elif(molecular_weight): 
                if(elem.text):
                    compound_data["molecular_weight"] = elem.text
                molecular_weight = False
            elif(topological):
                if(elem.text):
                    compound_data["topological_polar_surface_area"] = elem.text
                topological = False
            elif(monoisotopic_weight):
                if(elem.text):
                    compound_data["monoisotopic_weight"] = elem.text
                monoisotopic_weight = False
            elif(complexity):
                if(elem.text):
                    compound_data["complexity"] = elem.text
                complexity = False