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
graph_mychem.add_node("mesh")
graph_mychem.add_node("umls")

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
    weight=1.1,
)

graph_mychem.add_edge(
    "inchi",
    "pubchem",
    object=MongoDBEdge("pubchem", "pubchem.inchi", "pubchem.cid"),
    weight=1.2,
)

graph_mychem.add_edge(
    "inchikey",
    "chembl",
    object=MongoDBEdge("chembl", "chembl.inchikey",
                       "chembl.molecule_chembl_id"),
    weight=1.0,
)

graph_mychem.add_edge(
    "inchikey",
    "drugbank",
    object=MongoDBEdge("drugbank", "drugbank.inchi_key", "drugbank.id"),
    weight=1.1,
)

graph_mychem.add_edge(
    "inchikey",
    "pubchem",
    object=MongoDBEdge("pubchem", "pubchem.inchikey", "pubchem.cid"),
    weight=1.2,
)

graph_mychem.add_edge(
    "pharmgkb",
    "drugbank",
    object=MongoDBEdge("pharmgkb", "pharmgkb.id", "pharmgkb.xrefs.drugbank"),
)

# self-loop to check looked-up values exist in official collection
graph_mychem.add_edge(
    "drugbank",
    "drugbank",
    object=MongoDBEdge("drugbank", "drugbank.id", "drugbank.id"),
)

###############################################################################
# NDC Nodes and Edges
###############################################################################
graph_mychem.add_edge(
    "ndc",
    "inchikey",
    object=MongoDBEdge(
        "drugbank_full", "drugbank.products.ndc_product_code", "drugbank.inchi_key"),
)

###############################################################################
# Chebi Nodes and Edges
###############################################################################
graph_mychem.add_edge(
    "inchikey",
    "chebi",
    object=MongoDBEdge("chebi", "chebi.inchikey", "chebi.id"),
    weight=1.1,
)
graph_mychem.add_edge(
    "drugbank",
    "chebi",
    object=MongoDBEdge("drugbank", "drugbank.id", "drugbank.xrefs.chebi"),
    weight=1.0,
)
graph_mychem.add_edge(
    "chembl",
    "chebi",
    object=MongoDBEdge("chembl", "chembl.molecule_chembl_id",
                       "chembl.chebi_par_id"),
    weight=1.0,
)

###############################################################################
# Unii Edges
###############################################################################
graph_mychem.add_edge(
    "inchikey", "unii", object=MongoDBEdge("unii", "unii.inchikey", "unii.unii")
)
graph_mychem.add_edge(
    "pubchem", "unii", object=MongoDBEdge("unii", "unii.pubchem", "unii.unii")
)

###############################################################################
# Drug name Unii lookup
###############################################################################
graph_mychem.add_edge(
    "drugname",
    "unii",
    object=CIMongoDBEdge("unii", "unii.preferred_term", "unii.unii"),
    weight=3.0,
)

###############################################################################
# Edges for SMILES sources
###############################################################################
graph_mychem.add_edge(
    "smiles",
    "inchikey",
    object=MongoDBEdge("chebi", "chebi.smiles", "chebi.inchikey"),
)
graph_mychem.add_edge(
    "smiles",
    "inchikey",
    object=MongoDBEdge("chembl", "chembl.smiles", "chembl.inchikey"),
)
graph_mychem.add_edge(
    "smiles",
    "inchikey",
    object=MongoDBEdge("drugcentral", "drugcentral.structures.smiles",
                       "drugcentral.structures.inchikey"),
)
graph_mychem.add_edge(
    "smiles",
    "inchikey",
    object=MongoDBEdge("unii", "unii.smiles", "unii.inchikey"),
)

###############################################################################
# MeSH Edges
###############################################################################
graph_mychem.add_edge(
    "mesh",
    "drugcentral",
    object=MongoDBEdge(
        "drugcentral", "drugcentral.xrefs.mesh_supplemental_record_ui", "drugcentral.id")
)
graph_mychem.add_edge(
    "mesh",
    "ginas",
    object=MongoDBEdge("ginas", "ginas.xrefs.MESH", "ginas.id")
)
graph_mychem.add_edge(
    "mesh",
    "pharmgkb",
    object=MongoDBEdge("pharmgkb", "pharmgkb.xrefs.mesh", "pharmgkb.id")
)
graph_mychem.add_edge(
    "mesh",
    "umls",
    object=MongoDBEdge("umls", "umls.mesh", "umls.cui")
)

###############################################################################
# UMLS Edges
###############################################################################
graph_mychem.add_edge(
    "umls",
    "drugcentral",
    object=MongoDBEdge(
        "drugcentral", "drugcentral.xrefs.umlscui", "drugcentral.id")
)
graph_mychem.add_edge(
    "umls",
    "pharmgkb",
    object=MongoDBEdge("pharmgkb", "pharmgkb.xrefs.umls", "pharmgkb.id")
)
graph_mychem.add_edge(
    "umls",
    "umls",
    object=MongoDBEdge("umls", "umls.cui", "umls.cui")
)

###############################################################################
# MyChemKeyLookup Class
###############################################################################


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
                "mesh",
                "cas",
                "drugcentral",
                "pharmgkb",
                "inchi",
                "inchikey",
                "umls"
            ],
            id_priority_list=[
                "chebi",
                "unii",
                "pubchem",
                "chembl",
                "drugbank",
                "mesh",
                "cas",
                "drugcentral",
                "pharmgkb",
                "inchi",
                "inchikey",
                "umls"
            ],
            # skip keylookup for InChIKeys
            skip_w_regex="^[A-Z]{14}-[A-Z]{10}-[A-Z]$",
            *args,
            **kwargs
        )
