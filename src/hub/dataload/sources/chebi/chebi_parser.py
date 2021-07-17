from collections import defaultdict
import networkx as nx
import obonet
from biothings.utils.dataload import dict_sweep, unlist, value_convert_to_number


class CompoundReader:
    def __init__(self, sdf_file_path):
        self.sdf_file_path = sdf_file_path

    @classmethod
    def convert_comp_str_to_dict(cls, comp_str):
        # Trim the brackets around each `<tag>`, and split the SDF contents by new line characters,
        #   making `comp_attr_list` a list of attributes. Each attribute is a list of two strings. E.g.
        #   "<...> <ChEBI ID>\nCHEBI:90\n\n> <Star>\n3\n\n> <...>" will be converted to
        #   [["ChEBI ID", "CHEBI:90"], ["Star", "3"]]
        comp_attr_list = comp_str.split("\n> <")
        comp_attr_list = [attr.strip("\n").split('>\n', 1) for attr in comp_attr_list]

        # Remove molecule structure - Marvin
        del comp_attr_list[0]

        def convert_comp_attr_to_dict_entry(comp_attr):
            key = comp_attr[0].lower().replace(' ', '_').replace('-', '_')
            value = comp_attr[1].split("\n")
            return key, value

        return dict(convert_comp_attr_to_dict_entry(comp_attr) for comp_attr in comp_attr_list)

    @classmethod
    def restructure_comp_dict(cls, comp_dict):
        new_comp_dict = dict()
        xrefs_dict = dict()
        citation_dict = dict()

        for key, value in iter(comp_dict.items()):
            if key == "definition":
                value[0] = value[0].replace('<stereo>', '').replace('<ital>', '')
                value[0] = value[0].replace('</stereo>', '').replace('</ital>', '')
                new_comp_dict[key] = value
                continue

            # restructure the pubchem_database_links field
            if key == 'pubchem_database_links':
                new_pubchem_dict = {}
                for _value in value:
                    splitted_results = _value.split(':')
                    if len(splitted_results) == 2:
                        new_pubchem_dict[splitted_results[0].lower()] = splitted_results[1][1:]
                value = new_pubchem_dict

                new_comp_dict[key] = value
                continue

            if key == 'iupac_names':
                key = 'iupac'
                new_comp_dict[key] = value
                continue

            if key == 'chebi_id':
                key = 'id'
                new_comp_dict[key] = value
                continue

            if key == 'chebi_name':
                key = 'name'
                new_comp_dict[key] = value
                continue

            if key == 'wikipedia_database_links':
                key = 'wikipedia'
                value = {'url_stub': value}
                xrefs_dict[key] = value
                continue

            if key == 'beilstein_registry_numbers':
                key = 'beilstein'
                xrefs_dict[key] = value
                continue

            if '_database_links' in key:
                key = key.replace('_database_links', '')
                xrefs_dict[key] = value
                continue

            if '_registry_numbers' in key:
                key = key.replace('_registry_numbers', '')
                xrefs_dict[key] = value
                continue

            if '_citation_links' in key:
                key = key.replace('_citation_links', '')
                if key == 'pubmed_central':
                    key = 'pmc'
                citation_dict[key] = value
                continue

            # Put the rest of <key, value> into `new_comp_dict` as-is
            new_comp_dict[key] = value

        if xrefs_dict.keys():
            new_comp_dict['xrefs'] = xrefs_dict
        if citation_dict.keys():
            new_comp_dict['citation'] = citation_dict
        return new_comp_dict

    def iter_read_compounds(self):
        sdf_content = open(self.sdf_file_path, 'r').read()
        comp_str_list = sdf_content.split("$$$$")  # split the sdf content into a list of compounds
        del comp_str_list[-1]  # the last in the list is a "\n" character

        for comp_str in comp_str_list:
            comp_dict = self.convert_comp_str_to_dict(comp_str)
            comp_dict = self.restructure_comp_dict(comp_dict)
            yield comp_dict


class OntologyReader:
    """
    Class that reads an obo ontology file into a networkx graph, and further construct ontology document for each node
    in the graph
    """

    """
    We have some super-hub nodes in the ontology graph (e.g. CHEBI:50860, "organic molecular entity") that have
      up to 141,138 descendants and 7,336 successors.

    The 99.9% quantiles of numbers of successors/predecessors/descendants/ancestors are 224.92, 8, 2187.12, and 86.

    Here we limit the max number of successors/predecessors/descendants/ancestors nodes to be included in any 
      ontology document to 2000
    """
    NODE_FAMILY_CAPACITY = 2000

    def __init__(self, obo_file_path):
        self.obo_file_path = obo_file_path

        """
        The ontology graph obtained from `read_obo` is actually a reverse one whose directed edges point from low-level 
        to high-level entities, e.g. 

            CHEBI:25106 macrolide -> CHEBI:63944 macrocyclic lactone -> ... -> CHEBI:24431 chemical entity

        Reverse the graph to make it consistent with our understanding of successors/predecessors/descendants/ancestors
        """
        graph = obonet.read_obo(obo_file_path)
        graph = graph.reverse(copy=True)

        """
        `parents`, `children`, `ancestors`, and `descendants` must be searched only upon `is_a` edges. 
        See https://github.com/biothings/mychem.info/issues/83#issuecomment-876111289
        """
        # note that:
        #   method graph.edges() only returns (u, v) collection
        #   attribute graph.edges returns (u, v, data) collection
        unwanted_edges = [(u, v) for (u, v, data) in graph.edges if data != "is_a"]
        # Void, in-place operation. Copy the old graph if necessary.
        graph.remove_edges_from(unwanted_edges)

        self.ontology_graph = graph
        self.ontology_graph_node_view = graph.nodes()

    @classmethod
    def convert_subset_value(cls, value):
        """
        The 'subset' field of ontology nodes has 3 unique values, { ['1_STAR'], ['2_STAR'], ['3_STAR'] }
        This method will convert the a 'subset' value from string to integer correspondingly, i.e. {1, 2, 3}
        """
        if not value:
            return None

        return int(value[0].split("_")[0])

    @classmethod
    def convert_relationship_value(cls, value):
        """
        The 'relationship' field of ontology nodes is a list of space-separated strings. E.g.

          ['has_role CHEBI:68495', 'has_functional_parent CHEBI:28179', 'has_role CHEBI:38637', 'has_role CHEBI:35610']

        This method will convert the a 'relationship' value to a dict correspondingly. E.g.

          {'has_role': ['CHEBI:68495', 'CHEBI:38637', 'CHEBI:35610'], 'has_functional_parent': [CHEBI:28179']}
        """
        if not value:
            return None

        relationship_dict = defaultdict(list)
        for relationship_str in value:
            relationship_name, chebi_id = relationship_str.split(" ", 1)
            relationship_dict[relationship_name].append(chebi_id)

        return relationship_dict

    def read_ontology(self, node_id):
        """
        Read the node object in the ontology graph given `node_id` and convert it to an ontology document
        """
        """
        Each node_obj has 6 keys: {'alt_id', 'def', 'is_a', 'name', 'relationship', 'subset'}
        
        Key mapping:
        
          node_obj['alt_id']       -> ontology_dict['secondary_chebi_id']
          node_obj['def']          -> ontology_dict['definition']
          node_obj['is_a']         -> will be replaced by successors/predecessors/descendants/ancestors fields
          node_obj['name']         -> ontology_dict['name']
          node_obj['relationship'] -> ontology_dict['relationship']
          node_obj['subset']       -> ontology_dict['star']
          
        node_obj['subset'] has 3 values, {'1_STAR', '2_STAR', '3_STAR'}, and will be converted to {1, 2, 3}
        """
        node_obj = self.ontology_graph_node_view.get(node_id)
        if node_obj is None:
            return None

        successors = list(self.ontology_graph.successors(node_id))  # graph.predecessors(): iterator
        predecessors = list(self.ontology_graph.predecessors(node_id))  # graph.predecessors(): iterator
        descendants = list(nx.descendants(self.ontology_graph, node_id))  # nx.descendants(): set
        ancestors = list(nx.ancestors(self.ontology_graph, node_id))  # nx.ancestors(): set

        # Start construction of the ontology document
        ontology_dict = dict()
        ontology_dict["id"] = node_id

        ontology_dict["secondary_chebi_id"] = node_obj.get("alt_id")
        ontology_dict['definition'] = node_obj.get('def')
        ontology_dict['name'] = node_obj.get('name')
        ontology_dict['relationship'] = self.convert_relationship_value(node_obj.get('relationship'))
        ontology_dict['star'] = self.convert_subset_value(node_obj.get('subset'))

        # Use the same naming convention as in the Mondo parser
        #   See https://github.com/biothings/mydisease.info/blob/master/src/plugins/mondo/parser.py
        ontology_dict["num_children"] = len(successors)
        ontology_dict["num_parents"] = len(predecessors)
        ontology_dict["num_descendants"] = len(descendants)
        ontology_dict["num_ancestors"] = len(ancestors)

        ontology_dict["children"] = successors[:self.NODE_FAMILY_CAPACITY]
        ontology_dict["parents"] = predecessors[:self.NODE_FAMILY_CAPACITY]
        ontology_dict["descendants"] = descendants[:self.NODE_FAMILY_CAPACITY]
        ontology_dict["ancestors"] = ancestors[:self.NODE_FAMILY_CAPACITY]

        return ontology_dict


class ChebiParser:
    def __init__(self, compound_reader: CompoundReader, ontology_reader: OntologyReader):
        self.compound_reader = compound_reader
        self.ontology_reader = ontology_reader

    def generate_chebi_documents(self):
        """
        Generation Policy:

        1. Iterate with self.compound_reader. For every compound document, find its ontology document by its ChEBI id.
           Join the two documents into a comprehensive ChEBI document and return.
        2. For those ChEBI ids that only exist in the ontology network, return the their ontology documents as ChEBI
           documents.
        """
        used_chebi_ids = set()

        for compound_dict in self.compound_reader.iter_read_compounds():
            # Note that in CompoundReader.convert_comp_attr_to_dict_entry(), all fields of compound documents are
            #   converted to list of strings. And at this step, `unlist` is not executed yet, so `compound_dict["id"]`
            #   must be a list of one string at now.
            chebi_id = compound_dict["id"][0]

            ontology_dict = self.ontology_reader.read_ontology(chebi_id)
            if ontology_dict:
                ontology_dict.update(compound_dict)
                yield ontology_dict
            else:
                yield compound_dict

            used_chebi_ids.add(chebi_id)

        all_ontology_chebi_ids = set(self.ontology_reader.ontology_graph_node_view)
        unused_ontology_chebi_ids = all_ontology_chebi_ids - used_chebi_ids
        for chebi_id in unused_ontology_chebi_ids:
            ontology_dict = self.ontology_reader.read_ontology(chebi_id)
            yield ontology_dict

    @classmethod
    def transform_chebi_document(cls, chebi_dict):
        chebi_dict = dict_sweep(chebi_dict, vals=[None, ".", "-", "", "NA", "none", " ", "Not Available", "unknown",
                                                  "null", "None", "NaN"])
        chebi_dict = value_convert_to_number(unlist(chebi_dict), skipped_keys=["cid", "sid", "beilstein", "pubmed",
                                                                               "sabio_rk", "gmelin", "molbase",
                                                                               "synonyms", "wikipedia", "url_stub"])

        doc = dict()
        doc['_id'] = chebi_dict['id']
        doc['chebi'] = chebi_dict
        return doc

    def parse(self):
        for chebi_dict in self.generate_chebi_documents():
            yield self.transform_chebi_document(chebi_dict)
