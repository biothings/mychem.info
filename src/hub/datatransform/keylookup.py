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
graph_mychem.add_node("mesh")
graph_mychem.add_node("ndc")
graph_mychem.add_node("omop")
graph_mychem.add_node("pharmgkb")
graph_mychem.add_node("pubchem")
graph_mychem.add_node("rxnorm")
graph_mychem.add_node("smiles")
graph_mychem.add_node("umls")
graph_mychem.add_node("unii")

graph_mychem.add_edge(
    "inchi",
    "chembl",
    object=MongoDBEdge("chembl", "chembl.inchi", "chembl.molecule_chembl_id"),
    weight=3.0,
)

graph_mychem.add_edge(
    "inchi",
    "drugbank",
    object=MongoDBEdge("drugbank_full", "drugbank.inchi", "drugbank.id"),
    weight=3.1,
)

graph_mychem.add_edge(
    "inchi",
    "pubchem",
    object=MongoDBEdge("pubchem", "pubchem.inchi", "pubchem.cid"),
    weight=3.2,
)

graph_mychem.add_edge(
    "chembl",
    "inchikey",
    object=MongoDBEdge("chembl", "chembl.molecule_chembl_id",
                       "chembl.inchi_key"),
    weight=3.0,
)

graph_mychem.add_edge(
    "drugbank",
    "inchikey",
    object=MongoDBEdge("drugbank", "drugbank.id", "drugbank.inchi_key"),
    weight=3.1,
)

graph_mychem.add_edge(
    "pubchem",
    "inchikey",
    object=MongoDBEdge("pubchem", "pubchem.cid", "pubchem.inchikey"),
    weight=3.2,
)

graph_mychem.add_edge(
    "pharmgkb",
    "drugbank",
    object=MongoDBEdge("pharmgkb", "pharmgkb.id", "pharmgkb.xrefs.drugbank"),
    weight=3.5,
)

# self-loops to check looked-up values exist in official collections
graph_mychem.add_edge(
    "drugbank",
    "drugbank",
    object=MongoDBEdge("drugbank", "drugbank.id", "drugbank.id"),
    weight=3.0,
)

graph_mychem.add_edge(
    "pubchem",
    "pubchem",
    object=MongoDBEdge("pubchem", "pubchem.cid", "pubchem.cid"),
    weight=3.0,
)

graph_mychem.add_edge(
    "chembl",
    "chembl",
    object=MongoDBEdge("chembl", "chembl.molecule_chembl_id",
                       "chembl.molecule_chembl_id"),
    weight=3.0,
)

graph_mychem.add_edge(
    "pharmgkb",
    "pharmgkb",
    object=MongoDBEdge("pharmgkb", "pharmgkb.id", "pharmgkb.id"),
    weight=3.0,
)

graph_mychem.add_edge(
    "drugcentral",
    "drugcentral",
    object=MongoDBEdge("drugcentral", "drugcentral.id", "drugcentral.id"),
    weight=3.0,
)

graph_mychem.add_edge(
    "unii",
    "unii",
    object=MongoDBEdge("unii", "unii.unii", "unii.unii"),
    weight=3.0,
)

###############################################################################
# NDC Nodes and Edges
###############################################################################
# NDC -> ChEBI (highest priority)
graph_mychem.add_edge(
    "ndc",
    "chebi",
    object=MongoDBEdge("chebi", "chebi.xrefs.drugbank", "chebi.id"),
    weight=0.9,
)

# NDC -> drugbank -> inchikey (fallback)
graph_mychem.add_edge(
    "ndc",
    "drugbank",
    object=MongoDBEdge("drugbank_full", "drugbank.products.ndc_product_code",
                       "drugbank.id"),
    weight=3.5,
)

# NDC -> inchikey (shortcut, lower priority)
graph_mychem.add_edge(
    "ndc",
    "inchikey",
    object=MongoDBEdge("drugbank_full", "drugbank.products.ndc_product_code",
                       "drugbank.inchi_key"),
    weight=4.0,
)

###############################################################################
# ChEBI Nodes and Edges - Primary mapping target
#
# This section prioritizes ChEBI as the primary identifier for chemical
# entities. The graph is structured to:
# 1. Map all chemical identifiers TO ChEBI when possible (low weights 0.5-0.9)
# 2. Provide fallback paths FROM ChEBI to other identifiers (weights 1.0-1.2)
# 3. Use higher weights (2.0+) for non-ChEBI mappings to deprioritize them
###############################################################################
# ChEBI self-loop to check looked-up values exist in official collection
graph_mychem.add_edge(
    "chebi",
    "chebi",
    object=MongoDBEdge("chebi", "chebi.id", "chebi.id"),
    weight=0.1,
)

# Direct mappings TO ChEBI from structural identifiers (highest priority)
graph_mychem.add_edge(
    "inchikey",
    "chebi",
    object=MongoDBEdge("chebi", "chebi.inchikey", "chebi.id"),
    weight=0.5,
)

graph_mychem.add_edge(
    "inchi",
    "chebi",
    object=MongoDBEdge("chebi", "chebi.inchi", "chebi.id"),
    weight=0.6,
)

graph_mychem.add_edge(
    "smiles",
    "chebi",
    object=MongoDBEdge("chebi", "chebi.smiles", "chebi.id"),
    weight=0.6,
)

# Direct mappings TO ChEBI from database cross-references
graph_mychem.add_edge(
    "drugbank",
    "chebi",
    object=MongoDBEdge("chebi", "chebi.xrefs.drugbank", "chebi.id"),
    weight=0.7,
)

graph_mychem.add_edge(
    "chembl",
    "chebi",
    object=MongoDBEdge("chebi", "chebi.xrefs.chembl", "chebi.id"),
    weight=0.7,
)

graph_mychem.add_edge(
    "pubchem",
    "chebi",
    object=MongoDBEdge("chebi", "chebi.xrefs.pubchem.cid", "chebi.id"),
    weight=0.7,
)

graph_mychem.add_edge(
    "pharmgkb",
    "chebi",
    object=MongoDBEdge("chebi", "chebi.xrefs.pharmgkb", "chebi.id"),
    weight=0.7,
)

graph_mychem.add_edge(
    "drugcentral",
    "chebi",
    object=MongoDBEdge("chebi", "chebi.xrefs.drugcentral", "chebi.id"),
    weight=0.7,
)

graph_mychem.add_edge(
    "cas",
    "chebi",
    object=MongoDBEdge("chebi", "chebi.xrefs.cas", "chebi.id"),
    weight=0.8,
)

# Reverse lookups FROM ChEBI to structural identifiers (for fallback paths)
graph_mychem.add_edge(
    "chebi",
    "inchikey",
    object=MongoDBEdge("chebi", "chebi.id", "chebi.inchikey"),
    weight=1.0,
)

graph_mychem.add_edge(
    "chebi",
    "inchi",
    object=MongoDBEdge("chebi", "chebi.id", "chebi.inchi"),
    weight=1.0,
)

graph_mychem.add_edge(
    "chebi",
    "smiles",
    object=MongoDBEdge("chebi", "chebi.id", "chebi.smiles"),
    weight=1.0,
)

# Reverse mappings: FROM ChEBI to other database identifiers
graph_mychem.add_edge(
    "chebi",
    "drugbank",
    object=MongoDBEdge("drugbank", "drugbank.xrefs.chebi", "drugbank.id"),
    weight=1.1,
)

graph_mychem.add_edge(
    "chebi",
    "chembl",
    object=MongoDBEdge("chembl", "chembl.chebi_par_id",
                       "chembl.molecule_chembl_id"),
    weight=1.1,
)

graph_mychem.add_edge(
    "chebi",
    "pubchem",
    object=MongoDBEdge("pubchem", "pubchem.cid", "pubchem.cid"),
    weight=1.1,
)

graph_mychem.add_edge(
    "chebi",
    "drugcentral",
    object=MongoDBEdge("drugcentral", "drugcentral.xrefs.chebi",
                       "drugcentral.id"),
    weight=1.1,
)

graph_mychem.add_edge(
    "chebi",
    "pharmgkb",
    object=MongoDBEdge("pharmgkb", "pharmgkb.xrefs.chebi", "pharmgkb.id"),
    weight=1.1,
)

###############################################################################
# Unii Edges (fallback mappings with higher weights)
###############################################################################
graph_mychem.add_edge(
    "unii", "inchikey",
    object=MongoDBEdge("unii", "unii.unii", "unii.inchikey"),
    weight=4.0,
)
graph_mychem.add_edge(
    "unii", "pubchem",
    object=MongoDBEdge("unii", "unii.unii", "unii.pubchem"),
    weight=4.0,
)

###############################################################################
# Drug name to UNII lookup (last resort with high weight)
###############################################################################
graph_mychem.add_edge(
    "drugname",
    "unii",
    object=CIMongoDBEdge("unii", "unii.preferred_term", "unii.unii"),
    weight=5.0,
)

# Drug name to ChEBI (if possible, higher priority than UNII)
graph_mychem.add_edge(
    "drugname",
    "chebi",
    object=CIMongoDBEdge("chebi", "chebi.name", "chebi.id"),
    weight=1.5,
)

###############################################################################
# Edges for SMILES sources - prioritize ChEBI (already handled above)
# Fallback SMILES mappings with higher weights
###############################################################################
# SMILES -> inchikey through various sources (fallback paths)
graph_mychem.add_edge(
    "smiles",
    "inchikey",
    object=MongoDBEdge("chebi", "chebi.smiles", "chebi.inchikey"),
    weight=4.0,
)

graph_mychem.add_edge(
    "smiles",
    "inchikey",
    object=MongoDBEdge("chembl", "chembl.smiles", "chembl.inchi_key"),
    weight=4.5,
)

graph_mychem.add_edge(
    "smiles",
    "inchikey",
    object=MongoDBEdge("drugcentral", "drugcentral.structures.smiles",
                       "drugcentral.structures.inchikey"),
    weight=4.6,
)

graph_mychem.add_edge(
    "smiles",
    "inchikey",
    object=MongoDBEdge("unii", "unii.smiles", "unii.inchikey"),
    weight=4.7,
)

###############################################################################
# Additional identifier mappings TO ChEBI
###############################################################################
# UNII to ChEBI mapping
graph_mychem.add_edge(
    "unii",
    "chebi",
    object=MongoDBEdge("chebi", "chebi.xrefs.unii", "chebi.id"),
    weight=0.8,
)

# Reverse UNII mapping
graph_mychem.add_edge(
    "chebi",
    "unii",
    object=MongoDBEdge("unii", "unii.unii", "unii.unii"),
    weight=1.1,
)

# MESH identifier mappings (if available in ChEBI)
graph_mychem.add_edge(
    "mesh",
    "chebi",
    object=MongoDBEdge("chebi", "chebi.xrefs.mesh", "chebi.id"),
    weight=0.8,
)

# UMLS identifier mappings
graph_mychem.add_edge(
    "umls",
    "chebi",
    object=MongoDBEdge("chebi", "chebi.xrefs.umls", "chebi.id"),
    weight=0.8,
)

# OMOP identifier mappings (indirect through other sources)
graph_mychem.add_edge(
    "omop",
    "chebi",
    object=MongoDBEdge("chebi", "chebi.xrefs.omop", "chebi.id"),
    weight=0.9,
)

###############################################################################
# Additional identifier mappings for complete coverage
###############################################################################
# MESH mappings
graph_mychem.add_edge(
    "mesh",
    "mesh",
    object=MongoDBEdge("umls", "umls.mesh", "umls.mesh"),
    weight=3.0,
)

# MESH -> UMLS -> ChEBI (indirect pathway)
graph_mychem.add_edge(
    "mesh",
    "umls",
    object=MongoDBEdge("umls", "umls.mesh", "umls.cui"),
    weight=3.5,
)

# UMLS self-loop
graph_mychem.add_edge(
    "umls",
    "umls",
    object=MongoDBEdge("umls", "umls.cui", "umls.cui"),
    weight=3.0,
)

# UMLS -> drugcentral (if available)
graph_mychem.add_edge(
    "umls",
    "drugcentral",
    object=MongoDBEdge("drugcentral", "drugcentral.xrefs.umlscui",
                       "drugcentral.id"),
    weight=3.5,
)

# OMOP mappings (if available)
graph_mychem.add_edge(
    "omop",
    "omop",
    object=MongoDBEdge("omop", "omop.omop", "omop.omop"),
    weight=3.0,
)

# CAS mappings (additional paths)
graph_mychem.add_edge(
    "cas",
    "cas",
    object=MongoDBEdge("drugcentral", "drugcentral.structures.cas_rn",
                       "drugcentral.structures.cas_rn"),
    weight=3.0,
)

graph_mychem.add_edge(
    "cas",
    "drugcentral",
    object=MongoDBEdge("drugcentral", "drugcentral.structures.cas_rn",
                       "drugcentral.id"),
    weight=3.5,
)

# RxNorm mappings
graph_mychem.add_edge(
    "rxnorm",
    "rxnorm",
    object=MongoDBEdge("drugcentral", "drugcentral.xrefs.rxnorm",
                       "drugcentral.xrefs.rxnorm"),
    weight=3.0,
)

graph_mychem.add_edge(
    "rxnorm",
    "drugcentral",
    object=MongoDBEdge("drugcentral", "drugcentral.xrefs.rxnorm",
                       "drugcentral.id"),
    weight=3.5,
)

# RxNorm -> ChEBI (if available through cross-references)
graph_mychem.add_edge(
    "rxnorm",
    "chebi",
    object=MongoDBEdge("chebi", "chebi.xrefs.rxnorm", "chebi.id"),
    weight=0.8,
)

# Additional UNII mappings
graph_mychem.add_edge(
    "unii",
    "drugcentral",
    object=MongoDBEdge("drugcentral", "drugcentral.xrefs.unii",
                       "drugcentral.id"),
    weight=3.5,
)

# Additional NDC mappings
graph_mychem.add_edge(
    "ndc",
    "ndc",
    object=MongoDBEdge("ndc", "ndc.productndc", "ndc.productndc"),
    weight=3.0,
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
                "mesh",
                "cas",
                "drugcentral",
                "pharmgkb",
                "inchi",
                "inchikey",
                "umls",
                "omop",
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
                "umls",
                "omop",
            ],
            # skip keylookup for InchiKeys
            skip_w_regex="^[A-Z]{14}-[A-Z]{10}-[A-Z]",
            *args,
            **kwargs
        )
