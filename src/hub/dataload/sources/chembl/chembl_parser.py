import json
import urllib.parse
from itertools import chain, groupby
from collections import defaultdict
from typing import List
from collections.abc import Iterator  # replacing typing.Iterable

from biothings.utils.dataload import dict_sweep, unlist, value_convert_to_number
from biothings.utils.dataload import boolean_convert


class ChemblJsonFileReader:
    @classmethod
    def read_file(cls, path: str, key: str, transform_func=None) -> Iterator[dict]:
        file_data = json.load(open(path))
        entries = file_data[key]
        if transform_func:
            entries = map(transform_func, entries)
        return entries

    @classmethod
    def read_multi_files(cls, paths: Iterator[str], key: str, transform_func=None) -> Iterator[dict]:
        entries = chain.from_iterable(cls.read_file(p, key, transform_func) for p in paths)
        return entries


class ReferenceUtil:
    """
    Used by DrugIndicationReferenceListUtil and MechanismReferenceListUtil
    to transform their reference objects.
    """

    @classmethod
    def create_clinical_trials_reference(cls, ref_id) -> dict:
        """
        Create a new ClinicalTrials from ref_id, used when splitting comma-separated ClinicalTrials references
        into multiple references.

        E.g. the following reference should be split into 2 objects:

        ```
        {'ref_id': 'NCT00375713,NCT02447393',
         'ref_type': 'ClinicalTrials',
         'ref_url': 'https://clinicaltrials.gov/search?id=%22NCT00375713%22OR%22NCT02447393%22'}
        ```

        and each ref_id will be used to create a new reference.
        """
        ref_type = "ClinicalTrials"
        ref_url = 'https://clinicaltrials.gov/search?id="{}"'.format(ref_id)
        # percent-encode the `ref_url`, skipping characters of "?", "=", "/", and ":"
        # basically it does only one thing -- encoding each double quote to "%22"
        ref_url = urllib.parse.quote(ref_url, safe="?=/:")

        ref = {
            "id": ref_id,
            'type': ref_type,
            'url': ref_url,
            ref_type: ref_id
        }

        return ref

    @classmethod
    def transform_reference(cls, ref: dict) -> dict:
        """
        For a downloaded reference object, transform in the following two ways:

        - Use shorter keys: `ref_id` => `id`, `ref_type` => `type`, `ref_url` => `url`
        - Add a new entry for each reference object with its `ref_type` value as key, its`ref_id` value as value

        E.g. The following reference object

        ```
        {"ref_id": "NCT01910259",
         "ref_type": "ClinicalTrials",
         "ref_url": "https://clinicaltrials.gov/search?id=%22NCT01910259%22"}
        ```

        will be transformed into:

        ```
        {"ClinicalTrials": "NCT01910259",
         "id": "NCT01910259",
         "type": "ClinicalTrials",
         "url": "https://clinicaltrials.gov/search?id=%22NCT01910259%22"}
        ```

        See https://github.com/biothings/mychem.info/issues/67#issuecomment-767744333
        """
        ref["id"] = ref.pop("ref_id")
        ref["type"] = ref.pop("ref_type")
        ref["url"] = ref.pop("ref_url")

        ref[ref["type"]] = ref["id"]

        return ref


class TargetReader(ChemblJsonFileReader):
    # Top key to the entry list in the JSON file
    CONTENT_KEY = "targets"

    # Keys to the preserved fields in each target entry
    ENTRY_PRIMARY_KEY = "target_chembl_id"
    ENTRY_PRESERVED_KEYS = {ENTRY_PRIMARY_KEY, "pref_name", "target_type", "organism"}

    # we need to rename some field keys indicated by the following map
    REKEYING_MAP = {
        # old_key: new_key
        "pref_name": "target_name",
        "organism": "target_organism"
    }

    @classmethod
    def transform_entry(cls, entry: dict):
        entry_keys = list(entry.keys())  # iterate over the copy of keys, otherwise "RuntimeError: dictionary changed size during iteration".
        for key in entry_keys:
            if key not in cls.ENTRY_PRESERVED_KEYS:
                del entry[key]

            if key in cls.REKEYING_MAP:
                new_key = cls.REKEYING_MAP[key]
                entry[new_key] = entry.pop(key)

        return entry

    @classmethod
    def to_dict(cls, entries: Iterator[dict]):
        """
        Transform the `entries` into one dict, each of whose entries has the 'target_chembl_id'
        as key and the rest of fields as value.

        E.g.
            entries = [
                {'target_chembl_id': 'CHEMBL3885640',
                 'target_name': 'Sodium/potassium-transporting ATPase subunit alpha-2/alpha-3',
                 'target_organism': 'Rattus norvegicus',
                 'target_type': 'PROTEIN COMPLEX'},

                {'target_chembl_id': 'CHEMBL2331043',
                 'target_name': 'Sodium channel alpha subunit',
                 'target_organism': 'Homo sapiens',
                 'target_type': 'PROTEIN FAMILY'}
            ]

        after transformation, we have:

            return_dict = {
                'CHEMBL3885640': {'target_name': 'Sodium/potassium-transporting ATPase subunit alpha-2/alpha-3',
                                  'target_organism': 'Rattus norvegicus',
                                  'target_type': 'PROTEIN COMPLEX'},
                'CHEMBL2331043': {'target_name': 'Sodium channel alpha subunit',
                                  'target_organism': 'Homo sapiens',
                                  'target_type': 'PROTEIN FAMILY'}
            }
        """
        ret_dict = {entry[cls.ENTRY_PRIMARY_KEY]: entry for entry in entries}
        for _, entry in ret_dict.items():
            del entry[cls.ENTRY_PRIMARY_KEY]

        return ret_dict


class BindingSiteReader(ChemblJsonFileReader):
    # Top key to the entry list in the JSON file
    CONTENT_KEY = "binding_sites"

    @classmethod
    def transform_entry(cls, entry: dict):
        entry_keys = list(entry.keys())  # iterate over the copy of keys, otherwise "RuntimeError: dictionary changed size during iteration".
        for key in entry_keys:
            if key not in {"site_id", "site_name"}:
                del entry[key]

        return entry

    @classmethod
    def to_dict(cls, entries: Iterator[dict]):
        """
        `entries` is a list-like of `<"site_id" : xxx, "site_name": yyy>` dictionaries,
        here we convert each into a `<xxx : yyy>` dictionary

        E.g.

            entries = [
                {'site_id': 10278, 'site_name': 'GABA-A receptor; alpha-5/beta-3/gamma-2, Neur_chan_LBD domain'},
                {'site_id': 10279, 'site_name': 'GABA-A receptor; alpha-5/beta-3/gamma-2, Neur_chan_LBD domain'}
            ]

        after transformation, we have:

            return_dict = {
                10278 : 'GABA-A receptor; alpha-5/beta-3/gamma-2, Neur_chan_LBD domain',
                10279 : 'GABA-A receptor; alpha-5/beta-3/gamma-2, Neur_chan_LBD domain'
            }
        """
        return {entry["site_id"]: entry["site_name"] for entry in entries}


class MechanismReader(ChemblJsonFileReader):
    # Top key to the entry list in the JSON file
    CONTENT_KEY = "mechanisms"

    # Keys to the preserved fields in each mechanism entry
    ENTRY_PRIMARY_KEY = "molecule_chembl_id"
    ENTRY_REFERENCE_KEY = "mechanism_refs"  # key to the reference list (which needs special transformation)
    ENTRY_PRESERVED_KEYS = {ENTRY_PRIMARY_KEY, ENTRY_REFERENCE_KEY,
                            "action_type", "site_id", "target_chembl_id"}

    @classmethod
    def transform_entry(cls, entry: dict):
        entry_keys = list(entry.keys())  # iterate over the copy of keys, otherwise "RuntimeError: dictionary changed size during iteration".
        for key in entry_keys:
            if key not in cls.ENTRY_PRESERVED_KEYS:
                del entry[key]

            if key == cls.ENTRY_REFERENCE_KEY:
                entry[key] = list(cls.transform_reference_list(entry[key]))

        return entry

    @classmethod
    def transform_reference_list(cls, ref_list: List[dict]) -> Iterator[dict]:
        """
        Iterate the input list of references, transform and yield each reference.

        Sixteen types of references are found in mechanism json objects:

            ref_types = [
                "ISBN", "PubMed", DailyMed", "Wikipedia", "Expert", "Other",
                "FDA", "DOI", "KEGG", "PubChem", "IUPHAR", "PMC", "InterPro",
                "ClinicalTrials", "Patent", "UniProt"
            ]

        Comma-separated references are not found in mechanisms json object so far.

        Args:
            ref_list (list): a list of reference json objects

        Returns:
            the transformed references
        """

        for ref in ref_list:
            yield ReferenceUtil.transform_reference(ref)

    @classmethod
    def to_dict(cls, entries: Iterator[dict]):
        def primary_key_fn(entry: dict): return entry[cls.ENTRY_PRIMARY_KEY]

        # Sorting is necessary here because `itertools.groupby()` does not combine non-consecutive groups
        #     E.g. `[1, 1, 2, 2, 1, 1]` will be split into 3 groups, `[1, 1], [2, 2], [1, 1]`
        # Another workaround is to use `pandas.DataFrame.groupby()`
        entries = sorted(entries, key=primary_key_fn)
        ret_dict = {key: list(group) for key, group in groupby(entries, key=primary_key_fn)}

        for _, mechanism_list in ret_dict.items():
            for mechanism in mechanism_list:
                del mechanism[cls.ENTRY_PRIMARY_KEY]

        return ret_dict


class DrugIndicationReader(ChemblJsonFileReader):
    # Top key to the entry list in the JSON file
    CONTENT_KEY = "drug_indications"

    ENTRY_PRIMARY_KEY = "molecule_chembl_id"
    ENTRY_SECONDARY_KEY = "mesh_id"
    ENTRY_REFERENCE_KEY = "indication_refs"  # key to the reference list (which needs special transformation)
    ENTRY_PRESERVED_KEYS = {ENTRY_PRIMARY_KEY, ENTRY_SECONDARY_KEY, ENTRY_REFERENCE_KEY,
                            "mesh_heading", "efo_id", "efo_term", "max_phase_for_ind"}

    @classmethod
    def transform_entry(cls, entry: dict):
        for key in list(entry):
            if key not in cls.ENTRY_PRESERVED_KEYS:
                del entry[key]

            if key == cls.ENTRY_REFERENCE_KEY:
                entry[key] = list(cls.transform_reference_list(entry[key]))

        return entry

    @classmethod
    def transform_reference_list(cls, ref_list: List[dict]) -> Iterator[dict]:
        """
        Iterate the input list of references, transform and yield each reference.

        Four types of references are found in drug indications:

            ref_types = ["ClinicalTrials", "ATC", "DailyMed", "FDA"]

        I only found comma-separated references in "ClinicalTrials" type, e.g.

            {
                'ref_id': 'NCT00375713,NCT02447393', 'ref_type': 'ClinicalTrials',
                'ref_url': 'https://clinicaltrials.gov/search?id=%22NCT00375713%22OR%22NCT02447393%22'
            }

        Commas are also found in some "FDA" references but serves as part of the file names, e.g.

            {
                'ref_id': 'label/2015/206352s003,021567s038lbl.pdf', 'ref_type': 'FDA',
                'ref_url': 'http://www.accessdata.fda.gov/drugsatfda_docs/label/2015/206352s003,021567s038lbl.pdf'
            }

        Commas are not found in the other two types of references.

        So here I only split comma-separated references in "ClinicalTrials"

        Args:
            ref_list (list): a list of reference json objects

        Returns:
            the transformed references
        """

        for ref in ref_list:
            if ref["ref_type"] == "ClinicalTrials" and "," in ref["ref_id"]:
                for ref_id in ref["ref_id"].split(","):
                    yield ReferenceUtil.create_clinical_trials_reference(ref_id)
            else:
                yield ReferenceUtil.transform_reference(ref)

    @classmethod
    def to_dict(cls, entries: Iterator[dict]):
        """
        First we need to transform `entries`, a list-like of dictionaries into one dictionary.

        E.g.
            entries = [
                {'mesh_id': 'D006967', ..., 'molecule_chembl_id': 'CHEMBL1000'},
                {'mesh_id': 'D020754', ..., 'molecule_chembl_id': 'CHEMBL744'},
                {'mesh_id': 'D020754', ..., 'molecule_chembl_id': 'CHEMBL744'}
            ]

        will be transformed (via `groupby` operation) to:

            ret_dict = {
                'CHEMBL744': [{'mesh_id': 'D020754', ...,}, {'mesh_id': 'D020754', ...,}]
                'CHEMBL1000': [{'mesh_id': 'D006967', ..., }]
            }

        Then Note that in each value list in the above dictionary, `efo_id`, `efo_term` and `indication_refs`
        can be further merged under the same `mesh_id` (to be consistent with the results shown on ChEMBL webpages,
        e.g https://www.ebi.ac.uk/chembl/compound_report_card/CHEMBL744/).

        E.g. values in

            ret_dict = {
                'CHEMBL744': [
                    {'mesh_id': 'D020754', 'efo_id': 'Orphanet:98756', 'max_phase_for_ind': 3, ...},
                    {'mesh_id': 'D020754', 'efo_id': 'Orphanet:94147', 'max_phase_for_ind': 3, ...},
                    ...
                ]
            }

        will be merged into:

            ret_dict = {
                'CHEMBL744': [
                    {
                        'mesh_id': 'D020754',
                        'efo_id': ['Orphanet:98756', 'Orphanet:94147'],
                        'max_phase_for_ind': 3, ...
                    },
                    ...
                ]
            }

        This can be done by grouping by `mesh_id` for each `molecule_chembl_id`. After grouping, we process other
        fields as following:

        - `mesh_heading`: use the unique value
            - because one-to-one (bijection) relationship is confirmed between `mesh_id` and `mesh_heading`
        - `efo_id` and `efo_terms`: put all valid values into lists
            - one-to-one (bijection) relationship is also confirmed between `efo_id` and `efo_terms`
        - `indication_refs`: concat all the reference lists into one
        - `max_phase_for_ind`: use the max value

        Uniqueness does not hold for just a couple `max_phase_for_ind` entries for certain
        `<molecule_chembl_id, mesh_id>` combinations, and we decide to use `max(max_phase_for_ind)` in these cases.
        A sample uniqueness test is like below:

        ```python
        import pandas as pd
        import glob

        drug_indication_json_files = glob.iglob(os.path.join(SRC_ROOT_FOLDER, "drug_indication.*.json"))
        entries = DrugIndicationReader.read_multi_files(drug_indication_json_files, ...)

        df = pd.DataFrame(entries)
        for _, group in df.groupby("molecule_chembl_id"):
            for __, subgroup in group.groupby("mesh_id"):
                if subgroup.shape[0] > 1:
                    if len(subgroup.loc[:, "max_phase_for_ind"].unique()) > 1:
                        print(subgroup.loc[:, ["molecule_chembl_id", "mesh_id", "max_phase_for_ind"]])
        ```

        Output will be like:

        ```
              molecule_chembl_id  mesh_id  max_phase_for_ind
        32263      CHEMBL1201610  D009103                  4
        34415      CHEMBL1201610  D009103                  3
              molecule_chembl_id  mesh_id  max_phase_for_ind
        16625      CHEMBL1201631  D003920                  3
        32505      CHEMBL1201631  D003920                  4
        32506      CHEMBL1201631  D003920                  3
              molecule_chembl_id  mesh_id  max_phase_for_ind
        16185      CHEMBL1201631  D003924                  3
        32512      CHEMBL1201631  D003924                  4
        32513      CHEMBL1201631  D003924                  3
        ```
        """

        def primary_key_fn(entry): return entry[cls.ENTRY_PRIMARY_KEY]
        def secondary_key_fn(entry): return entry[cls.ENTRY_SECONDARY_KEY]

        def merge_mesh_subgroups(_group):
            """
            Further group the input `group` by "mesh_id" and merge the subgroups
            """

            # Sorting is necessary here because `itertools.groupby()` does not combine non-consecutive groups
            #     E.g. `[1, 1, 2, 2, 1, 1]` will be split into 3 groups, `[1, 1], [2, 2], [1, 1]`
            # Another workaround is to use `pandas.DataFrame.groupby()`
            _group = list(_group)
            _group.sort(key=secondary_key_fn)

            for _, subgroup in groupby(_group, key=secondary_key_fn):
                # `subgroup` returned by `groupby` is an iterator; to reuse it below, save it as a list
                subgroup = list(subgroup)

                indication = dict()  # the dict to be returned

                # No matter whether `len(subgroup) > 1` or not, the following 2 fields are unique to each subgroup
                indication["mesh_id"] = subgroup[0]["mesh_id"]
                indication["mesh_heading"] = subgroup[0]["mesh_heading"]

                # if len(subgroup) == 1: ret_dict["max_phase_for_ind"] = subgroup[0]["max_phase_for_ind"]
                # `max` operation applies no matter if `len(subgroup) == 1`
                indication["max_phase_for_ind"] = max(entry["max_phase_for_ind"] for entry in subgroup)

                """
                Corner cases of `efo_id` and `efo_term`:

                1. We found some `mesh_id` mapped to None values of `efo_id` and `efo_term`.
                2. ChEMBL UI will merge duplicated `efo_id` and `efo_term` entries while keeping duplicated 
                references.

                --------------------------------------

                Example 1: 

                    molecule_chembl_id : 'CHEMBL1201631'
                    mesh_id : 'D007006'
                    efo_id : [None, None, None, 
                              'HP:0000044', 
                              'HP:0000044', 
                              'HP:0000044']
                    efo_term: [None, None, None, 
                               'Hypogonadotrophic hypogonadism \
                               {http://www.co-ode.org/patterns#createdBy=\
                               "http://www.ebi.ac.uk/ontology/webulous#OPPL_pattern"}',
                               'Hypogonadotrophic hypogonadism \
                               {http://www.co-ode.org/patterns#createdBy=\
                               "http://www.ebi.ac.uk/ontology/webulous#OPPL_pattern"}',
                               'Hypogonadotrophic hypogonadism 
                               {http://www.co-ode.org/patterns#createdBy=\
                               "http://www.ebi.ac.uk/ontology/webulous#OPPL_pattern"}']

                However, `indication_refs` exist for such None entries of `efo_id` and `efo_terms`.

                See https://www.ebi.ac.uk/chembl/compound_report_card/CHEMBL1201631/ "Drug Indications" panel 
                for more details.

                No idea why ChEMBL has data like this.

                --------------------------------------

                Example 2: 

                    molecule_chembl_id : 'CHEMBL1201631'
                    mesh_id : 'D020528',
                    efo_id: ['EFO:0003840', 'EFO:0003840', 'EFO:0003840'],
                    efo_term: ['chronic progressive multiple sclerosis',
                               'chronic progressive multiple sclerosis',
                               'chronic progressive multiple sclerosis']

                On https://www.ebi.ac.uk/chembl/compound_report_card/CHEMBL1201631/ "Drug Indications" panel, 
                mesh_id 'D020528' has 1 efo_ids, 1 efo_terms, but 3 duplicated references 
                """

                # I did not find a None `efo_id` mapped to a non-None `efo_term`, or vice versa
                efo_id_list = [entry["efo_id"] for entry in subgroup if entry["efo_id"] is not None]
                efo_term_list = [entry["efo_term"] for entry in subgroup if entry["efo_term"] is not None]

                """
                Addendum: Kevin suggested the following format for `efo_id` and `efo_term`:

                    efo: [{efo_id: 'EFO:0008520', efo_term: 'primary progressive multiple sclerosis'},
                          {efo_id: 'EFO:0008522', efo_term: 'secondary progressive multiple sclerosis'},
                          {efo_id: 'EFO:0003840', efo_term: 'chronic progressive multiple sclerosis'}]
                          
                Addendum: Chunlei suggested trim the "efo_" prefixes in the sub-field names:

                    efo: [{id: ..., term: ...}]
                """
                # ret_dict["efo"] = [{"efo_id": t[0], "efo_term": t[1]} for t in
                #                    {*zip(efo_id_list, efo_term_list)}]
                indication["efo"] = [{"id": t[0], "term": t[1]} for t in {*zip(efo_id_list, efo_term_list)}]

                indication_refs = chain.from_iterable([entry["indication_refs"] for entry in subgroup])
                # remove the duplicated references (dictionaries underlying) in the collection
                # see https://stackoverflow.com/a/9427216
                indication["indication_refs"] = [dict(t) for t in {tuple(sorted(ref.items())) for ref in indication_refs}]

                yield indication

        # Sorting is necessary here because `itertools.groupby()` does not combine non-consecutive groups
        #     E.g. `[1, 1, 2, 2, 1, 1]` will be split into 3 groups, `[1, 1], [2, 2], [1, 1]`
        # Another workaround is to use `pandas.DataFrame.groupby()`
        entries = sorted(entries, key=primary_key_fn)

        ret_dict = dict()
        for primary_key, indication_group in groupby(entries, key=primary_key_fn):
            indications = list(merge_mesh_subgroups(indication_group))
            ret_dict[primary_key] = indications

        return ret_dict


class MoleculeReader(ChemblJsonFileReader):
    # Top key to the entry list in the JSON file
    CONTENT_KEY = "molecules"

    @classmethod
    def transform_entry(cls, entry: dict):
        doc = dict()

        doc["_id"] = entry.get("molecule_chembl_id", None)
        if doc["_id"] is None:
            return None

        # Copy all the content in `molecule_entry` to the "chembl" field
        doc["chembl"] = entry

        # Preserve "inchi", "inchi_key", and "smile" values from the "molecule_structures" sub-field;
        # then discard the whole "molecule_structures" sub-field from the "chembl" field
        molecule_structures = entry.get("molecule_structures", None)
        if molecule_structures and type(molecule_structures) == dict:
            inchi_key = molecule_structures.get("standard_inchi_key", None)
            if inchi_key is not None:
                doc["chembl"]["inchi_key"] = inchi_key

            smiles = molecule_structures.get("canonical_smiles", None)
            if smiles is not None:
                doc["chembl"]["smiles"] = smiles

            inchi = molecule_structures.get("standard_inchi", None)
            if inchi is not None:
                doc["chembl"]["inchi"] = inchi
        doc["chembl"].pop("molecule_structures", None)

        # Convert "cross_references" field into "xrefs" field;
        # then discard "cross_references" field
        cross_references = entry.get("cross_references", None)
        if cross_references and type(cross_references) == list:
            doc["chembl"]["xrefs"] = cls.transform_cross_reference_list(cross_references)
        doc["chembl"].pop("cross_references", None)

        # Add "CHEBI:" prefix, standardize the way representing CHEBI IDs
        chebi_par_id = entry.get("chebi_par_id", None)
        if chebi_par_id:
            doc["chembl"]["chebi_par_id"] = "CHEBI:" + str(chebi_par_id)
        else:
            doc["chembl"].pop("chebi_par_id", None)  # clean, could be a None

        doc = unlist(doc)
        doc = value_convert_to_number(doc, skipped_keys=["chebi_par_id", "first_approval"])
        doc = boolean_convert(doc, ["topical", "oral", "parenteral", "dosed_ingredient", "polymer_flag",
                                    "therapeutic_flag", "med_chem_friendly", "molecule_properties.ro3_pass"])
        return doc

    @classmethod
    def transform_cross_reference_list(cls, xref_list: List[dict]) -> dict:
        """
        Group the cross-references field based on the source
        Also change the field name
        """
        xref_dict = defaultdict(list)
        for xref in xref_list:
            # note that the 'xref' field names are from the chembl datasource, not the parser
            if "xref_src" not in xref:
                continue

            xref_src = xref["xref_src"]
            if xref_src == 'PubChem':
                assert xref['xref_name'].startswith('SID: ')
                xref_dict['pubchem'].append({'sid': int(xref['xref_id'])})
            elif xref_src == 'Wikipedia':
                xref_dict['wikipedia'].append({'url_stub': xref['xref_id']})
            elif xref_src == 'TG-GATEs':
                xref_dict['tg-gates'].append({'name': xref['xref_name'], 'id': int(xref['xref_id'])})
            elif xref_src == 'DailyMed':
                xref_dict['dailymed'].append({'name': xref['xref_name']})
            elif xref_src == 'DrugCentral':
                xref_dict['drugcentral'].append({'name': xref['xref_name'], 'id': int(xref['xref_id'])})
        return xref_dict


class AuxiliaryDataLoader:
    def __init__(self,
                 drug_indication_filepaths,
                 mechanism_filepaths,
                 target_filepaths,
                 binding_site_filepaths):
        self.drug_indication_filepaths = drug_indication_filepaths
        self.mechanism_filepaths = mechanism_filepaths
        self.target_filepaths = target_filepaths
        self.binding_site_filepaths = binding_site_filepaths

        self.drug_indication_dict = None
        self.mechanism_dict = None
        self.target_dict = None
        self.binding_site_dict = None

    def load(self):
        drug_indications = DrugIndicationReader.read_multi_files(paths=self.drug_indication_filepaths,
                                                                 key=DrugIndicationReader.CONTENT_KEY,
                                                                 transform_func=DrugIndicationReader.transform_entry)
        self.drug_indication_dict = DrugIndicationReader.to_dict(drug_indications)

        mechanisms = MechanismReader.read_multi_files(paths=self.mechanism_filepaths,
                                                      key=MechanismReader.CONTENT_KEY,
                                                      transform_func=MechanismReader.transform_entry)
        self.mechanism_dict = MechanismReader.to_dict(mechanisms)

        targets = TargetReader.read_multi_files(paths=self.target_filepaths,
                                                key=TargetReader.CONTENT_KEY,
                                                transform_func=TargetReader.transform_entry)
        self.target_dict = TargetReader.to_dict(targets)

        binding_sites = BindingSiteReader.read_multi_files(paths=self.binding_site_filepaths,
                                                           key=BindingSiteReader.CONTENT_KEY,
                                                           transform_func=BindingSiteReader.transform_entry)
        self.binding_site_dict = BindingSiteReader.to_dict(binding_sites)

        # Join `binding_site::binding_site_name` to `mechanism`
        # Join `target::target_type`, `target::target_organism` and `target::target_name` to `mechanism`
        target_keys = ["target_type", 'target_organism', 'target_name']
        for _, mechanism_list in self.mechanism_dict.items():
            for mechanism in mechanism_list:
                mechanism["binding_site_name"] = self.binding_site_dict.get(mechanism["site_id"], None)
                del mechanism["site_id"]

                target = self.target_dict.get(mechanism["target_chembl_id"], defaultdict(lambda: None))
                for key in target_keys:
                    mechanism[key] = target[key]

    def get_drug_indication_map(self) -> dict:
        return self.drug_indication_dict

    def get_drug_mechanism_map(self) -> dict:
        return self.mechanism_dict


class MoleculeDataLoader:
    def __init__(self, molecule_filepath):
        self.molecule_filepath = molecule_filepath
        self.molecule_entries = None

    def load(self):
        self.molecule_entries = MoleculeReader.read_file(path=self.molecule_filepath,
                                                         key=MoleculeReader.CONTENT_KEY,
                                                         transform_func=MoleculeReader.transform_entry)

    def get_molecules(self) -> Iterator[dict]:
        return self.molecule_entries


def load_chembl_data(mol_data_loader: MoleculeDataLoader, aux_data_loader: AuxiliaryDataLoader):
    molecules = mol_data_loader.get_molecules()
    if molecules is None:
        mol_data_loader.load()
        molecules = mol_data_loader.get_molecules()

    drug_indication_map = aux_data_loader.get_drug_indication_map()
    drug_mechanism_map = aux_data_loader.get_drug_mechanism_map()
    if (drug_indication_map is None) or (drug_mechanism_map is None):
        aux_data_loader.load()
        drug_indication_map = aux_data_loader.get_drug_indication_map()
        drug_mechanism_map = aux_data_loader.get_drug_mechanism_map()

    for doc in molecules:
        chembl_id = doc["chembl"]["molecule_chembl_id"]
        drug_indications = drug_indication_map.get(chembl_id, None)
        drug_mechanisms = drug_mechanism_map.get(chembl_id, None)

        if drug_indications is not None:
            # Join `molecule::first_approval` to `drug_indication::first_approval`
            first_approval = doc["chembl"].get("first_approval", None)
            if first_approval:
                for indication in drug_indications:
                    indication["first_approval"] = first_approval

            doc["chembl"]["drug_indications"] = drug_indications

        if drug_mechanisms is not None:
            doc["chembl"]["drug_mechanisms"] = drug_mechanisms

        doc = dict_sweep(doc, vals=[None, ".", "-", "", "NA", "None", "none", " ", "Not Available", "unknown", "null", []])

        try:
            _id = doc["chembl"]["inchi_key"]
            doc["_id"] = _id
        except KeyError:
            """
            Ignore the error when the document has no "inchi_key". 
            
            We allow such a document to be uploaded, and `ChemblUploader.keylookup` will later set `doc["molecule_chembl_id"]` as its "_id".
            
            There are 2,331,593 documents in the `mychem_src.chembl` MongoDB collection, among which 24,289 (1.04%) have "_id" starting with "CHEMBL". 
            It can be verified on the EMBL-EBI site that those entities have no inchi representation.
            """
            pass

        yield doc
