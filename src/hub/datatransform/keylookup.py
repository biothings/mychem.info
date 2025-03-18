import networkx as nx
from biothings.hub.datatransform import DataTransformMDB, MongoDBEdge

graph_mychem = nx.DiGraph()

###############################################################################
# PharmGKB Nodes and Edges
###############################################################################
graph_mychem.add_node("chebi")
graph_mychem.add_node("unii")
graph_mychem.add_node("pubchem")
graph_mychem.add_node("chembl")
graph_mychem.add_node("drugbank")
graph_mychem.add_node("mesh")
graph_mychem.add_node("cas")
graph_mychem.add_node("drugcentral")
graph_mychem.add_node("pharmgkb")
graph_mychem.add_node("inchi")
graph_mychem.add_node("inchikey")
graph_mychem.add_node("umls")

graph_mychem.add_node("aeolus")
graph_mychem.add_node("fda_orphan_drug")
graph_mychem.add_node("ginas")
graph_mychem.add_node("gsrs")
graph_mychem.add_node("gtopdb")
graph_mychem.add_node("unichem")

# InChI-based edges
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
    "pubchem", "chebi",
    object=MongoDBEdge("chebi", "chebi.pubchem_database_links.cid", "pubchem")
)
graph_mychem.add_edge(
    "pubchem", "chebi",
    object=MongoDBEdge("chebi", "chebi.pubchem_database_links.sid", "pubchem")
)

# InChIKey-based edges
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

# Reverse edge to map external InChIKeys to CHEBI
graph_mychem.add_edge(
    "inchikey", "chebi",
    object=MongoDBEdge("chebi", "chebi.inchikey", "chebi.id")
)

# PharmGKB to DrugBank edge
graph_mychem.add_edge(
    "pharmgkb",
    "drugbank",
    object=MongoDBEdge("pharmgkb", "pharmgkb.id", "pharmgkb.xrefs.drugbank"),
)

# Self-loop on DrugBank to verify lookup values exist
graph_mychem.add_edge(
    "drugbank",
    "drugbank",
    object=MongoDBEdge("drugbank", "drugbank.id", "drugbank.id"),
)

# MeSH edges
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

# UMLS edges
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

# aeolus fields
graph_mychem.add_edge(
    "aeolus", "inchikey",
    object=MongoDBEdge("aeolus", "aeolus.inchikey", "inchikey")
)
graph_mychem.add_edge(
    "aeolus", "unii",
    object=MongoDBEdge("aeolus", "aeolus.unii", "unii")
)

# chebi new fields
graph_mychem.add_edge(
    "chebi", "inchi",
    object=MongoDBEdge("chebi", "chebi.inchi", "inchi")
)
graph_mychem.add_edge(
    "chebi", "cas",
    object=MongoDBEdge("chebi", "chebi.xrefs.cas", "cas")
)
graph_mychem.add_edge(
    "chebi", "drugbank",
    object=MongoDBEdge("chebi", "chebi.xrefs.drugbank", "drugbank")
)
graph_mychem.add_edge(
    "smiles", "chebi",
    object=MongoDBEdge("chebi", "chebi.smiles", "smiles")
)
# drugbank new field
graph_mychem.add_edge(
    "drugbank", "unii",
    object=MongoDBEdge("drugbank", "drugbank.unii", "unii")
)

# drugcentral new fields
graph_mychem.add_edge(
    "drugcentral", "chebi",
    object=MongoDBEdge("drugcentral", "drugcentral.xrefs.chebi", "chebi")
)
graph_mychem.add_edge(
    "drugcentral", "unii",
    object=MongoDBEdge("drugcentral", "drugcentral.xrefs.unii", "unii")
)

# fda_orphan_drug field
graph_mychem.add_edge(
    "fda_orphan_drug", "inchikey",
    object=MongoDBEdge("fda_orphan_drug",
                       "fda_orphan_drug.inchikey", "inchikey")
)

# ginas fields
graph_mychem.add_edge(
    "ginas", "inchikey",
    object=MongoDBEdge("ginas", "ginas.inchikey", "inchikey")
)
graph_mychem.add_edge(
    "ginas", "unii",
    object=MongoDBEdge("ginas", "ginas.unii", "unii")
)
graph_mychem.add_edge(
    "ginas", "cas",
    object=MongoDBEdge("ginas", "ginas.xrefs.CAS", "cas")
)

# gsrs field (adding intermediate node "smiles")
graph_mychem.add_node("smiles")
graph_mychem.add_node("gsrs")
graph_mychem.add_edge(
    "gsrs", "smiles",
    object=MongoDBEdge("gsrs", "gsrs.moieties.smiles", "smiles")
)

# gtopdb fields
graph_mychem.add_node("gtopdb")
graph_mychem.add_edge(
    "gtopdb", "inchi",
    object=MongoDBEdge("gtopdb", "gtopdb.inchi", "inchi")
)
graph_mychem.add_edge(
    "gtopdb", "inchikey",
    object=MongoDBEdge("gtopdb", "gtopdb.inchikey", "inchikey")
)
graph_mychem.add_edge(
    "gtopdb", "smiles",
    object=MongoDBEdge("gtopdb", "gtopdb.smiles", "smiles")
)
graph_mychem.add_edge(
    "gtopdb", "cas",
    object=MongoDBEdge("gtopdb", "gtopdb.xrefs.cas", "cas")
)
graph_mychem.add_edge(
    "gtopdb", "pubchem",
    object=MongoDBEdge("gtopdb", "gtopdb.xrefs.pubchem_cid", "pubchem")
)
graph_mychem.add_edge(
    "gtopdb", "pubchem",
    object=MongoDBEdge("gtopdb", "gtopdb.xrefs.pubchem_sid", "pubchem")
)

# pharmgkb new fields
graph_mychem.add_edge(
    "pharmgkb", "inchi",
    object=MongoDBEdge("pharmgkb", "pharmgkb.inchi", "inchi")
)
graph_mychem.add_edge(
    "pharmgkb", "smiles",
    object=MongoDBEdge("pharmgkb", "pharmgkb.smiles", "smiles")
)
graph_mychem.add_edge(
    "pharmgkb", "cas",
    object=MongoDBEdge("pharmgkb", "pharmgkb.xrefs.cas", "cas")
)
# pharmgkb -> ndc
graph_mychem.add_node("ndc")
graph_mychem.add_edge(
    "pharmgkb", "ndc",
    object=MongoDBEdge("pharmgkb", "pharmgkb.xrefs.ndc", "ndc")
)
graph_mychem.add_edge(
    "pharmgkb", "pubchem",
    object=MongoDBEdge("pharmgkb", "pharmgkb.xrefs.pubchem.cid", "pubchem")
)
graph_mychem.add_edge(
    "pharmgkb", "pubchem",
    object=MongoDBEdge("pharmgkb", "pharmgkb.xrefs.pubchem.sid", "pubchem")
)
graph_mychem.add_node("rxnorm")
graph_mychem.add_edge(
    "pharmgkb", "rxnorm",
    object=MongoDBEdge("pharmgkb", "pharmgkb.xrefs.rxnorm", "rxnorm")
)

# pubchem new field: smiles canonical
graph_mychem.add_edge(
    "pubchem", "smiles",
    object=MongoDBEdge("pubchem", "pubchem.smiles.canonical", "smiles")
)

# unichem fields
graph_mychem.add_node("unichem")
graph_mychem.add_edge(
    "unichem", "chebi",
    object=MongoDBEdge("unichem", "unichem.chebi", "chebi")
)
graph_mychem.add_edge(
    "unichem", "chembl",
    object=MongoDBEdge("unichem", "unichem.chembl", "chembl")
)
graph_mychem.add_edge(
    "unichem", "drugbank",
    object=MongoDBEdge("unichem", "unichem.drugbank", "drugbank")
)
graph_mychem.add_edge(
    "unichem", "drugcentral",
    object=MongoDBEdge("unichem", "unichem.drugcentral", "drugcentral")
)
graph_mychem.add_edge(
    "unichem", "pharmgkb",
    object=MongoDBEdge("unichem", "unichem.pharmgkb", "pharmgkb")
)
graph_mychem.add_edge(
    "unichem", "pubchem",
    object=MongoDBEdge("unichem", "unichem.pubchem", "pubchem")
)

# unii field to pubchem
graph_mychem.add_edge(
    "unii", "pubchem",
    object=MongoDBEdge("unii", "unii.pubchem", "pubchem")
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
            # skip_w_regex="^[A-Z]{14}-[A-Z]{10}-[A-Z]$",
            *args,
            **kwargs
        )
