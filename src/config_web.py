"""
    Mychem.info
    https://mychem.info/
    Chemical and Drug Annotation as a Service.
"""

import copy
import re

from biothings.web.settings.default import ANNOTATION_KWARGS, QUERY_KWARGS

# *****************************************************************************
# Elasticsearch variables
# *****************************************************************************
ES_HOST = 'http://localhost:9200'
ES_INDICES = {
    "chem": "index_test_20240612_3kwpduyw",
    "drug": "index_test_20240612_3kwpduyw",
    "compound": "index_test_20240612_3kwpduyw",
}
ES_SCROLL_TIME = "10m"

# *****************************************************************************
# Endpoint Specifics
# *****************************************************************************
# aoelus

# Essential fields
DEFAULT_FIELDS = [
    "aeolus.unii",
    "aeolus.drug_id",
    "aeolus.rxcui",
    "aeolus.drug_name",
    "aeolus.no_of_outcomes",
    "aeolus.outcomes.name",
    "aeolus.outcomes.ror",
    "aeolus.outcomes.case_count",

    "chebi.id",
    "chebi.name",
    "chebi.definition",
    "chebi.relationship.has_role",
    "chebi.relationship.is_enantiomer_of",
    "chebi.formulae",
    "chebi.monoisotopic_mass",
    "chebi.iupac",
    "chebi.synonyms",
    "chebi.pubchem_database_links.sid",
    "chebi.pubchem_database_links.cid",
    "chebi.last_modified",
    "chebi.xrefs",

    "chembl.pref_name",
    "chembl.molecule_chembl_id",
    "chembl.molecule_properties.full_molformula",
    "chembl.molecule_properties.full_mwt",
    "chembl.molecule_properties.mw_monoisotopic",
    "chembl.molecule_properties.alogp",
    "chembl.molecule_properties.cx_logd",
    "chembl.molecule_properties.cx_logp",
    "chembl.molecule_properties.cx_most_apka",
    "chembl.molecule_properties.psa",
    "chembl.molecule_properties.qed_weighted",
    "chembl.inchi_key",
    "chembl.smiles",
    "chembl.inchi",

    "drugbank.id",
    "drugbank.name",
    "drugbank.cas",
    "drugbank.unii",
    "drugbank.synonyms",
    "drugbank.inchi_key",
    "drugbank.accession_number"

    "drugcentral.pharmacology_class.chebi.description",
    "drugcentral.pharmacology_class.mesh_pa.description",
    "drugcentral.fda_adverse_event.meddra_term",
    "drugcentral.bioactivity.target_name",
    "drugcentral.bioactivity.act_value",
    "drugcentral.bioactivity.act_type",
    "drugcentral.bioactivity.organism",
    "drugcentral.drug_use.indication.concept_name",
    "drugcentral.approval.date",
    "drugcentral.approval.agency",
    "drugcentral.drug_dosage.dosage",
    "drugcentral.drug_dosage.unit",
    "drugcentral.drug_dosage.route",
    "drugcentral.synonyms",
    "drugcentral.structures.inchi",
    "drugcentral.structures.inchikey",
    "drugcentral.structures.smiles",
    "drugcentral.structures.cas_rn",
    "drugcentral.xrefs",

    "fda_orphan_drug.pubchem_sid",
    "fda_orphan_drug.generic_name",
    "fda_orphan_drug.designated_date",
    "fda_orphan_drug.designation_status",
    "fda_orphan_drug.approval_status",
    "fda_orphan_drug.sponsor",
    "fda_orphan_drug.orphan_designation.parsed_text",

    "ginas.preferred_name",
    "ginas.unii",
    "ginas.names_list",
    "ginas.moieties.formula",
    "ginas.moieties.mwt",
    "ginas.inchikey",
    "ginas.approved.$numberLong",
    "ginas.definitionLevel",
    "ginas.deprecated",
    "ginas.structure.formula",
    "ginas.structure.mwt",
    "ginas.cas_primary",
    "ginas.xrefs",

    "ndc.product_id",
    "ndc.productndc",
    "ndc.producttypename",
    "ndc.proprietaryname",
    "ndc.nonproprietaryname",
    "ndc.dosageformname",
    "ndc.routename",
    "ndc.startmarketingdate",
    "ndc.marketingcategoryname",
    "ndc.applicationnumber",
    "ndc.labelername",
    "ndc.substancename",
    "ndc.active_numerator_strength",
    "ndc.active_ingred_unit",
    "ndc.pharm_classes",
    "ndc.listing_record_certified_through",

    "pharmgkb.id",
    "pharmgkb.name",
    "pharmgkb.generic_names",
    "pharmgkb.type",
    "pharmgkb.smiles",
    "pharmgkb.inchi",
    "pharmgkb.xrefs",

    "pubchem.cid",
    "pubchem.iupac.preferred",
    "pubchem.smiles.canonical",
    "pubchem.inchi",
    "pubchem.inchikey",
    "pubchem.molecular_formula",
    "pubchem.molecular_weight",
    "pubchem.exact_mass",
    "pubchem.monoisotopic_weight",
    "pubchem.topological_polar_surface_area",
    "pubchem.xlogp",
    "pubchem.hydrogen_bond_acceptor_count",
    "pubchem.hydrogen_bond_donor_count",
    "pubchem.rotatable_bond_count",
    "pubchem.formal_charge",
    "pubchem.complexity",
    "pubchem.heavy_atom_count",

    "sider.stitch.flat",
    "sider.side_effect.placebo",
    "sider.meddra.type",
    "sider.meddra.umls_id",
    "sider.indication.method_of_detection",
    "sider.indication.name",

    "umls.cui",
    "umls.mesh",
    "umls.name",

    "unichem.actor",
    "unichem.atlas",
    "unichem.bindingdb",
    "unichem.brenda",
    "unichem.carotenoiddb",
    "unichem.chebi",
    "unichem.chembl",
    "unichem.chemicalbook",
    "unichem.clinicaltrials",
    "unichem.comptox",
    "unichem.dailymed",
    "unichem.drugbank",
    "unichem.drugcentral",
    "unichem.emolecules",
    "unichem.fdasrs",
    "unichem.gtopdb",
    "unichem.hmdb",
    "unichem.ibm",
    "unichem.kegg_ligand",
    "unichem.lincs",
    "unichem.lipidmaps",
    "unichem.mcule",
    "unichem.metabolights",
    "unichem.molport",
    "unichem.nih_ncc",
    "unichem.nikkaji",
    "unichem.nmrshiftdb2",
    "unichem.pdb",
    "unichem.pharmgkb",
    "unichem.pubchem",
    "unichem.pubchem_dotf",
    "unichem.pubchem_tpharma",
    "unichem.recon",
    "unichem.rhea",
    "unichem.selleck",
    "unichem.surechembl",
    "unichem.swisslipids",
    "unichem.zinc",

    "unii.unii",
    "unii.registry_number",
    "unii.pubchem",
    "unii.molecular_formula",
    "unii.inchikey",
    "unii.smiles",
    "unii.ingredient_type",
    "unii.substance_type",
    "unii.uuid",
    "unii.display_name"
]
[
    // Aeolus
    "aeolus.outcomes.ror_95_ci",
    "aeolus.outcomes.id",
    "aeolus.outcomes.prr",
    "aeolus.outcomes.meddra_code",
    "aeolus.outcomes.prr_95_ci",
    "aeolus.pt",

    // Chebi
    "chebi.secondary_chebi_id",
    "chebi.relationship",
    "chebi.num_children",
    "chebi.num_parents",
    "chebi.num_descendants",
    "chebi.num_ancestors",
    "chebi.parents",
    "chebi.ancestors",
    "chebi.inchi",
    "chebi.smiles",
    "chebi.charge",
    "chebi.star",
    "chebi.mass",
    "chebi.monoisotopic_mass",
    "chebi.citation",

    // Chembl
    "chembl.availability_type",
    "chembl.black_box_warning",
    "chembl.chemical_probe",
    "chembl.chirality",
    "chembl.dosed_ingredient",
    "chembl.first_in_class",
    "chembl.inorganic_flag",
    "chembl.molecule_hierarchy",
    "chembl.molecule_properties.aromatic_rings",
    "chembl.molecule_properties.hba",
    "chembl.molecule_properties.hba_lipinski",
    "chembl.molecule_properties.hbd",
    "chembl.molecule_properties.hbd_lipinski",
    "chembl.molecule_properties.heavy_atoms",
    "chembl.molecule_properties.molecular_species",
    "chembl.molecule_properties.mw_freebase",
    "chembl.molecule_properties.np_likeness_score",
    "chembl.molecule_properties.num_lipinski_ro5_violations",
    "chembl.molecule_properties.num_ro5_violations",
    "chembl.molecule_properties.ro3_pass",
    "chembl.molecule_properties.rtb",
    "chembl.molecule_type",
    "chembl.natural_product",
    "chembl.oral",
    "chembl.orphan",
    "chembl.parenteral",
    "chembl.polymer_flag",
    "chembl.prodrug",
    "chembl.structure_type",
    "chembl.therapeutic_flag",
    "chembl.topical",
    "chembl.withdrawn_flag",

    // DrugBank

    // DrugCentral
    "drugcentral.fda_adverse_event.level",
    "drugcentral.fda_adverse_event.llr",
    "drugcentral.fda_adverse_event.llr_threshold",
    "drugcentral.fda_adverse_event.drug_ae",
    "drugcentral.fda_adverse_event.drug_no_ae",
    "drugcentral.fda_adverse_event.no_drug_ae",
    "drugcentral.fda_adverse_event.no_drug_no_ar",
    "drugcentral.bioactivity.uniprot",
    "drugcentral.bioactivity.target_class",
    "drugcentral.bioactivity.act_source",
    "drugcentral.bioactivity.action_type",
    "drugcentral.bioactivity.moa",
    "drugcentral.bioactivity.moa_source",
    "drugcentral.drug_use.indication.umls_cui",
    "drugcentral.drug_use.indication.snomed_full_name",
    "drugcentral.drug_use.indication.cui_semantic_type",
    "drugcentral.drug_use.indication.snomed_concept_id",
    "drugcentral.structures.inchi_key",
    "drugcentral.structures.cas_rn",
    "drugcentral.xrefs",

    // FDA Orphan Drug
    "fda_orphan_drug.orphan_designation.original_text",
    "fda_orphan_drug.orphan_designation.umls",

    // Ginas
    "ginas.properties",
    "ginas.moieties",
    "ginas.relationships",
    "ginas.approved",
    "ginas.access",
    "ginas.xrefs",
    "ginas.references",
    "ginas.approvedBy",
    "ginas.substanceClass",
    "ginas.tags",
    "ginas.status",
    "ginas.codes",
    "ginas.names",
    "ginas.lastEditedBy",
    "ginas.notes",
    "ginas.structure",

    // NDC
    "ndc.ndc_exclude_flag",
    "ndc.package",

    // PharmGKB
    "pharmgkb.dosing_guideline",

    // PubChem
    "pubchem.iupac.allowed",
    "pubchem.iupac.cas_like_style",
    "pubchem.iupac.markup",
    "pubchem.iupac.systematic",
    "pubchem.iupac.traditional",
    "pubchem.smiles.isomeric",
    "pubchem.formal_charge",
    "pubchem.complexity",
    "pubchem.hydrogen_bond_acceptor_count",
    "pubchem.hydrogen_bond_donor_count",
    "pubchem.rotatable_bond_count",
    "pubchem.topological_polar_surface_area",
    "pubchem.heavy_atom_count",
    "pubchem.chiral_atom_count",
    "pubchem.defined_chiral_atom_count",
    "pubchem.undefined_chiral_atom_count",
    "pubchem.chiral_bond_count",
    "pubchem.defined_chiral_bond_count",
    "pubchem.undefined_chiral_bond_count",
    "pubchem.isotope_atom_count",
    "pubchem.covalent_unit_count",
    "pubchem.tautomers_count"
]
# *** NOTE ***
# The CHEBI prefix must have a regex_term_pattern without a named <term> grouping.
# example query: CHEBI:57966:
# code snippet location: <biothings.api/web/query/builder.py>
# With a named term grouping of <term>, we produce the following which will fail
#     named_groups = match.groupdict() -> {"term": 57966}
#     q = named_groups.get(self.gpname.term) or q -> "57966"
# Without a named term grouping of <term> we orduce the following which will pass
#     named_groups = match.groupdict() -> {}
#     q = named_groups.get(self.gpname.term) or q -> "CHEBI:57966"

BIOLINK_MODEL_PREFIX_BIOTHINGS_CHEM_MAPPING = {
    "INCHIKEY": {"type": "chem"},
    "CHEMBL.COMPOUND": {
        "type": "chem",
        "field": "chembl.molecule_chembl_id",
        "regex_term_pattern": "(?P<term>chembl[0-9]+)",
        # "converter": lambda x: x.replace("CHEMBL.COMPOUND:", "CHEMBL"),
    },
    "PUBCHEM.COMPOUND": {
        "type": "chem",
        "field": "pubchem.cid",
        "regex_term_pattern": "(?P<term>[0-9]+)",
    },
    "CHEBI": {
        "type": "chem",
        "field": ["chebi.id", "chebi.secondary_chebi_id"],
        "regex_term_pattern": "(?P<term>CHEBI:[0-9]+)",
    },
    "UNII": {
        "type": "chem",
        "field": "unii.unii",
        "regex_term_pattern": "(?P<term>[A-Z0-9]{10})",
    },
}

# CURIE ID support based on BioLink Model
biolink_curie_regex_list = []
for (
    biolink_prefix,
    mapping,
) in BIOLINK_MODEL_PREFIX_BIOTHINGS_CHEM_MAPPING.items():
    field_match = mapping.get("field", [])
    term_pattern = mapping.get("regex_term_pattern", None)
    if term_pattern is None:
        term_pattern = "(?P<term>[^:]+)"

    raw_expression = rf"({biolink_prefix}):{term_pattern}"
    compiled_expression = re.compile(raw_expression, re.I)

    pattern = (compiled_expression, field_match)
    biolink_curie_regex_list.append(pattern)

# Custom prefix handling for chem specific identifiers
chem_prefix_handling = [
    (
        re.compile(r"((chembl\:(?P<term>chembl[0-9]+))|(chembl[0-9]+))", re.I),
        "chembl.molecule_chembl_id",
    ),
    (re.compile(r"chebi\:[0-9]+", re.I),
     ["chebi.id", "chebi.secondary_chebi_id"]),
    (re.compile(
        r"((unii\:(?P<term>[A-Z0-9]{10}))|([A-Z0-9]{10}))", re.I), "unii.unii"),
    (
        re.compile(r"((drugbank\:(?P<term>db[0-9]+))|(db[0-9]+))", re.I),
        [
            "unichem.drugbank",
            "chebi.xrefs.drugbank",
            "drugcentral.xrefs.drugbank_id",
            "pharmgkb.xrefs.drugbank",
        ],
    ),
    (
        re.compile(r"((pharmgkb.drug\:(?P<term>pa[0-9]+))|(pa[0-9]+))", re.I),
        "pharmgkb.id",
    ),
    (
        re.compile(
            r"((((pubchem.compound\:)|(cid\:))(?P<term>[0-9]+))|([0-9]+))", re.I
        ),
        ["pubchem.cid"],
    ),
    (
        re.compile(
            r"((((sid\:)|(pubchem.substance\:))(?P<term>[0-9]+))|([0-9]+))", re.I
        ),
        ["fda_orphan_drug.pubchem_sid"],
    ),
]

default_chem_regex = re.compile(r"(?P<scope>[^:]+):(?P<term>[\W\w]+)")
default_chem_fields = ()
default_chem_regex_pattern = (default_chem_regex, default_chem_fields)


ANNOTATION_ID_REGEX_LIST = [
    *biolink_curie_regex_list,
    *chem_prefix_handling,
    default_chem_regex_pattern,
]


STATUS_CHECK = {
    "id": "USNINKBPBVKHHZ-CYUUQNCZSA-L",  # penicillin
    "index": "index_test_20240612_3kwpduyw",
}

_extra_kwargs = {"list_filter": {"type": str, "default": None}}
ANNOTATION_KWARGS = copy.deepcopy(ANNOTATION_KWARGS)
ANNOTATION_KWARGS["*"].update(_extra_kwargs)
QUERY_KWARGS = copy.deepcopy(QUERY_KWARGS)
QUERY_KWARGS["*"].update(_extra_kwargs)
ES_RESULT_TRANSFORM = "web.pipeline.MyChemESResultFormatter"

# Set default fields
QUERY_KWARGS["*"]["_source"]["default"] = DEFAULT_FIELDS
QUERY_KWARGS["*"]["_source"]["strict"] = False
