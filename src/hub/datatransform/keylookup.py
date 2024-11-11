import networkx as nx
from biothings.hub.datatransform import CIMongoDBEdge, DataTransformMDB, MongoDBEdge

graph_mychem = nx.DiGraph()

###############################################################################
# PharmGKB Nodes and Edges
###############################################################################
graph_mychem.add_node("chebi")
graph_mychem.add_node("cas")
graph_mychem.add_node("chembl")
graph_mychem.add_node("drugbank")
graph_mychem.add_node("drugcentral")
graph_mychem.add_node("drugname")
graph_mychem.add_node("inchi")
graph_mychem.add_node("inchikey")
graph_mychem.add_node("ndc")
graph_mychem.add_node("pharmgkb")
graph_mychem.add_node("pubchem")
graph_mychem.add_node("rxnorm")
graph_mychem.add_node("smiles")
graph_mychem.add_node("unii")

graph_mychem.add_edge(
    "inchi",
    "chembl",
    object=MongoDBEdge("chembl", "chembl.inchi", "chembl.molecule_chembl_id"),
    weight=1.0,
)

graph_mychem.add_edge(
    "inchi",
    "drugbank",
    object=MongoDBEdge("drugbank_full", "drugbank.inchi", "drugbank.id"),
    # TODO
    #   object=MongoDBEdge(
    #       'drugbank_full', 'drugbank.inchi', 'drugbank.id'),
    weight=1.1,
)

graph_mychem.add_edge(
    "inchi",
    "pubchem",
    object=MongoDBEdge("pubchem", "pubchem.inchi", "pubchem.cid"),
    weight=1.2,
)

graph_mychem.add_edge(
    "chembl",
    "inchikey",
    object=MongoDBEdge("chembl", "chembl.molecule_chembl_id",
                       "chembl.inchi_key"),
    weight=1.0,
)

graph_mychem.add_edge(
    "drugbank",
    "inchikey",
    #   TODO drugbank_open
    object=MongoDBEdge("drugbank", "drugbank.id", "drugbank.inchi_key"),
    weight=1.1,
)

graph_mychem.add_edge(
    "pubchem",
    "inchikey",
    object=MongoDBEdge("pubchem", "pubchem.cid", "pubchem.inchikey"),
    weight=1.2,
)

graph_mychem.add_edge(
    "pharmgkb",
    "drugbank",
    object=MongoDBEdge("pharmgkb", "pharmgkb.id", "pharmgkb.xrefs.drugbank"),
)

# self-loops to check looked-up values exist in official collection
#   TODO drugbank_open
graph_mychem.add_edge(
    "drugbank",
    "drugbank",
    object=MongoDBEdge("drugbank", "drugbank.id", "drugbank.id"),
)

###############################################################################
# NDC Nodes and Edges
###############################################################################
# ndc -> drugbank -> inchikey
# shortcut edge, one lookup for ndc to inchikey by way of drugbank

graph_mychem.add_edge(
    "ndc",
    "inchikey",
    #   TODO drugbank_full
    object=MongoDBEdge(
        "drugbank_full", "drugbank.products.ndc_product_code", "drugbank.inchi_key"
    ),
)

###############################################################################
# Chebi Nodes and Edges
###############################################################################
# chebi -> drugbank -> inchikey
# chebi -> chembl -> inchikey
graph_mychem.add_edge(
    "chebi",
    "inchikey",
    object=MongoDBEdge("chebi", "chebi.id", "chebi.inchikey"),
    weight=1.1,
)
graph_mychem.add_edge(
    "chebi",
    "drugbank",
    object=MongoDBEdge("drugbank", "drugbank.xrefs.chebi", "drugbank.id"),
    weight=1.0,
)
graph_mychem.add_edge(
    "chebi",
    "chembl",
    object=MongoDBEdge("chembl", "chembl.chebi_par_id",
                       "chembl.molecule_chembl_id"),
    weight=1.0,
)

# graph_mychem.add_node('chebi-short')

# graph_mychem.add_edge('chebi', 'chebi-short',
#                      object=RegExEdge('^CHEBI:', ''))
# graph_mychem.add_edge('chebi-short', 'chebi',
#                      object=RegExEdge('^', 'CHEBI:'))
# graph_mychem.add_edge('chebi-short', 'drugbank',
#                      object=MongoDBEdge('drugbank', 'drugbank.chebi', 'drugbank.drugbank_id'))
# graph_mychem.add_edge('chebi-short', 'chembl',
#                      object=MongoDBEdge('chembl', 'chembl.chebi_par_id', 'chembl.molecule_chembl_id'))

###############################################################################
# Unii Edges
###############################################################################
graph_mychem.add_edge(
    "unii", "inchikey", object=MongoDBEdge("unii", "unii.unii", "unii.inchikey")
)
graph_mychem.add_edge(
    "unii", "pubchem", object=MongoDBEdge("unii", "unii.unii", "unii.pubchem")
)

###############################################################################
# Drug name Unii lookup
###############################################################################
# Converting to unii (and possibily Inchikey) should be done as a last resort,
# so we increase the weight of this edge
graph_mychem.add_edge(
    "drugname",
    "unii",
    object=CIMongoDBEdge("unii", "unii.preferred_term", "unii.unii"),
    weight=3.0,
)

###############################################################################
# Edges for SMILES sources
###############################################################################
# chebi.smiles -> inchikey
graph_mychem.add_edge(
    "smiles",
    "inchikey",
    object=MongoDBEdge("chebi", "chebi.smiles", "chebi.inchikey"),
)

# chembl.smiles -> inchikey
graph_mychem.add_edge(
    "smiles",
    "inchikey",
    object=MongoDBEdge("chembl", "chembl.smiles", "chembl.inchikey"),
)

# drugcentral.structures.smiles -> inchikey
graph_mychem.add_edge(
    "smiles",
    "inchikey",
    object=MongoDBEdge("drugcentral", "drugcentral.structures.smiles",
                       "drugcentral.structures.inchikey"),
)

# unii.smiles -> inchikey
graph_mychem.add_edge(
    "smiles",
    "inchikey",
    object=MongoDBEdge("unii", "unii.smiles", "unii.inchikey"),
)


class MyChemKeyLookup(DataTransformMDB):
    def __init__(self, input_types, *args, **kwargs):
        super(MyChemKeyLookup, self).__init__(
            graph_mychem,
            input_types,
            output_types=[
                "chebi",
                "unii",
                "pubchem",
                "chembl",
                "drugbank",
                "cas",
                "drugcentral",
                "pharmgkb",
                "inchi",
                "inchikey",
                # "mesh",
                # "gtopdb",
                # "hmdb",
                # "kegg_compound",
                # "chembank",
                # "pubchem_substance",
                # "sider_drug",
                # "bigg_metabolite",
                # "foodb_compound",
                # "kegg_glycan",
                # "kegg_drug",
                # "kegg_environ",
                # "kegg",
                # "umls",
            ],
            id_priority_list=[
                "chebi",
                "unii",
                "pubchem",
                "chembl",
                "drugbank",
                "cas",
                "drugcentral",
                "pharmgkb",
                "inchi",
                "inchikey",
                # "mesh",
                # "gtopdb",
                # "hmdb",
                # "kegg_compound",
                # "chembank",
                # "pubchem_substance",
                # "sider_drug",
                # "bigg_metabolite",
                # "foodb_compound",
                # "kegg_glycan",
                # "kegg_drug",
                # "kegg_environ",
                # "kegg",
                # "umls",
            ],
            # skip keylookup for InChIKeys
            skip_w_regex="^[A-Z]{14}-[A-Z]{10}-[A-Z]$",
            *args,
            **kwargs
        )
