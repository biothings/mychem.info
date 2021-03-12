import os
import json
import glob
import urllib.parse
from abc import ABC, abstractmethod
from itertools import chain, groupby
from collections import defaultdict

from biothings.utils.dataload import dict_sweep, unlist, value_convert_to_number
from biothings.utils.dataload import boolean_convert


class JsonListTransformer(ABC):
    @classmethod
    @abstractmethod
    def transform_to_dict(cls, entry_list):
        """
        Transform a list of json object into a dictionary
        """
        pass


class JsonFilesAdapter(JsonListTransformer, ABC):
    """
    Each adapter class extending JsonFilesAdapter should overwrite the following attribute/methods:

    - entry_list_key: a key in the raw json file to the desired collection of json objects
    - reformat(cls, entry): reformat a single json object and return it
    - transform_to_dict(cls, entry_list): transform the (reformatted) json list into a dictionary
    """
    entry_list_key: str  # type annotation to avoid the "unresolved reference" warning

    @classmethod
    @abstractmethod
    def reformat(cls, entry):
        """
        Reformat a json object from download to the desired structure, and return the new object.
        """
        pass

    @classmethod
    def read_files(cls, file_iter):
        """
        Read and reformat json objects from a collection of files, merge them into a list, and then transform the list
        of json objects into a dictionary.
        """
        def _read_file_and_reformat_content(file):
            if not cls.entry_list_key:
                raise ValueError("Class attribute `entry_list_key` not initialized")

            _entry_list = json.load(open(file))[cls.entry_list_key]
            _entry_list = [cls.reformat(entry) for entry in _entry_list]

            return _entry_list

        files = list(file_iter)
        if len(files) == 1:
            entry_list = _read_file_and_reformat_content(files[0])
        else:
            # merge the entry lists into one and return
            entry_list = list(chain.from_iterable(_read_file_and_reformat_content(f) for f in files))

        return cls.transform_to_dict(entry_list)


class MoleculeCrossReferenceListTransformer(JsonListTransformer):
    @classmethod
    def transform_to_dict(cls, xref_list):
        """
        Group the cross references field based on the source
        Also change the field name
        """
        xref_output = defaultdict(list)
        for _record in xref_list:
            # note that the 'xref' field names are from the chembl datasource, not the parser
            if 'xref_src' in _record and _record['xref_src'] == 'PubChem':
                assert _record['xref_name'].startswith('SID: ')
                xref_output['pubchem'].append({'sid': int(_record['xref_id'])})
            elif 'xref_src' in _record and _record['xref_src'] == 'Wikipedia':
                xref_output['wikipedia'].append({'url_stub': _record['xref_id']})
            elif 'xref_src' in _record and _record['xref_src'] == 'TG-GATEs':
                xref_output['tg-gates'].append({'name': _record['xref_name'], 'id': int(_record['xref_id'])})
            elif 'xref_src' in _record and _record['xref_src'] == 'DailyMed':
                xref_output['dailymed'].append({'name': _record['xref_name']})
            elif 'xref_src' in _record and _record['xref_src'] == 'DrugCentral':
                xref_output['drugcentral'].append({'name': _record['xref_name'], 'id': int(_record['xref_id'])})
        return xref_output


class ReferenceUtil:
    """
    Used by DrugIndicationReferenceListUtil and MechanismReferenceListUtil
    to transform their reference objects.
    """

    @classmethod
    def create_clinical_trials_reference(cls, ref_id):
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
    def reformat(cls, ref):
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


class DrugIndicationReferenceListUtil:
    @classmethod
    def iter_reformat(cls, ref_list):
        """
        Iterate the input list of references, transform and yield each reference.

        Four types of references found in drug indications are:

            ref_types = ["ClinicalTrials", "ATC", "DailyMed", "FDA"]

        I only found comma-separated references in "ClinicalTrials" type, e.g.

            {'ref_id': 'NCT00375713,NCT02447393', 'ref_type': 'ClinicalTrials',
             'ref_url': 'https://clinicaltrials.gov/search?id=%22NCT00375713%22OR%22NCT02447393%22'}

        Commas are also found in some "FDA" references but serves as part of the file names, e.g.

            {'ref_id': 'label/2015/206352s003,021567s038lbl.pdf', 'ref_type': 'FDA',
             'ref_url': 'http://www.accessdata.fda.gov/drugsatfda_docs/label/2015/206352s003,021567s038lbl.pdf'}

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
                yield ReferenceUtil.reformat(ref)


class MechanismReferenceListUtil:
    @classmethod
    def iter_reformat(cls, ref_list):
        """
        Iterate the input list of references, transform and yield each reference.

        Sixteen types of references found in mechanism json objects:

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
            yield ReferenceUtil.reformat(ref)


class TargetAdapter(JsonFilesAdapter):
    # key of the raw content to the entry list
    entry_list_key = "targets"

    # keys to preserve and group on for each entry in the entry list
    primary_key = "target_chembl_id"
    field_keys = ["pref_name", "target_type", "organism"]
    preserved_keys = set([primary_key] + field_keys)

    # we need to rename some field keys indicated by the following map
    rekeying_map = {
        # old_key: new_key
        "pref_name": "target_name",
        "organism": "target_organism"
    }

    @classmethod
    def reformat(cls, entry):
        for key in list(entry):
            if key not in cls.preserved_keys:
                del entry[key]

            if key in cls.rekeying_map:
                new_key = cls.rekeying_map[key]
                entry[new_key] = entry.pop(key)

        return entry

    @classmethod
    def transform_to_dict(cls, entry_list):
        """
        Transform the `entry_list` into one dict, each of whose entries has the 'target_chembl_id'
        as key and the rest of fields as value.

        E.g.
            entry_list = [
                {'target_chembl_id': 'CHEMBL3885640',
                 'target_name': 'Sodium/potassium-transporting ATPase subunit alpha-2/alpha-3',
                 'target_organism': 'Rattus norvegicus',
                 'target_type': 'PROTEIN COMPLEX'},

                {'target_chembl_id': 'CHEMBL2331043',
                 'target_name': 'Sodium channel alpha subunit',
                 'target_organism': 'Homo sapiens',
                 'target_type': 'PROTEIN FAMILY'}
            ]

        after transformation we have:

            return_dict = {
                'CHEMBL3885640': {'target_name': 'Sodium/potassium-transporting ATPase subunit alpha-2/alpha-3',
                                  'target_organism': 'Rattus norvegicus',
                                  'target_type': 'PROTEIN COMPLEX'},
                'CHEMBL2331043': {'target_name': 'Sodium channel alpha subunit',
                                  'target_organism': 'Homo sapiens',
                                  'target_type': 'PROTEIN FAMILY'}
            }
        """
        ret_dict = {entry[cls.primary_key]: entry for entry in entry_list}
        for _, entry in ret_dict.items():
            del entry[cls.primary_key]

        return ret_dict


class BindingSiteAdapter(JsonFilesAdapter):
    # key of the raw content to the entry list
    entry_list_key = "binding_sites"

    # keys to preserve and group on for each entry in the entry list
    primary_key = "site_id"
    field_key = "site_name"
    preserved_keys = {primary_key, field_key}

    @classmethod
    def reformat(cls, entry):
        for key in list(entry):
            if key not in cls.preserved_keys:
                del entry[key]

        return entry

    @classmethod
    def transform_to_dict(cls, entry_list):
        """
        `entry_list` is a list of `<"site_id" : xxx, "site_name": yyy>` dictionaries,
        here we convert it into a `<xxx : yyy>` dictionary

        E.g.

            entry_list = [
                {'site_id': 10278, 'site_name': 'GABA-A receptor; alpha-5/beta-3/gamma-2, Neur_chan_LBD domain'},
                {'site_id': 10279, 'site_name': 'GABA-A receptor; alpha-5/beta-3/gamma-2, Neur_chan_LBD domain'}
            ]

        after transformation we have:

            return_dict = {
                10278 : 'GABA-A receptor; alpha-5/beta-3/gamma-2, Neur_chan_LBD domain',
                10279 : 'GABA-A receptor; alpha-5/beta-3/gamma-2, Neur_chan_LBD domain'
            }
        """
        return {entry[cls.primary_key]: entry[cls.field_key] for entry in entry_list}


class MechanismAdapter(JsonFilesAdapter):
    # key of the raw content to the entry list
    entry_list_key = "mechanisms"

    # keys to preserve and group on for each entry in the entry list
    primary_key = "molecule_chembl_id"
    field_keys = ["action_type", "mechanism_refs", "site_id", "target_chembl_id"]
    preserved_keys = set([primary_key] + field_keys)

    @classmethod
    def reformat(cls, entry):
        for key in list(entry):
            if key not in cls.preserved_keys:
                del entry[key]

            if key == "mechanism_refs":
                entry[key] = list(MechanismReferenceListUtil.iter_reformat(entry[key]))

        return entry

    @classmethod
    def transform_to_dict(cls, entry_list):
        def primary_key_fn(entry): return entry[cls.primary_key]

        # Sorting is necessary here because `itertools.groupby()` does not combine non-consecutive groups
        #     E.g. `[1, 1, 2, 2, 1, 1]` will be split into 3 groups, `[1, 1], [2, 2], [1, 1]`
        # Another workaround is to use `pandas.DataFrame.groupby()`
        entry_list.sort(key=primary_key_fn)
        ret_dict = {key: list(group) for key, group in groupby(entry_list, key=primary_key_fn)}

        for _, mechanism_list in ret_dict.items():
            for mechanism in mechanism_list:
                del mechanism[cls.primary_key]

        return ret_dict


class DrugIndicationAdapter(JsonFilesAdapter):
    # key of the raw content to the entry list
    entry_list_key = "drug_indications"

    # keys to preserve and group on for each entry in the entry list
    primary_key, secondary_key = "molecule_chembl_id", "mesh_id"
    field_keys = ["mesh_heading", "efo_id", "efo_term", "max_phase_for_ind", "indication_refs"]
    preserved_keys = set([primary_key, secondary_key] + field_keys)

    # key to the reference list (which needs special transformation)
    reference_key = "indication_refs"

    @classmethod
    def reformat(cls, entry):
        for key in list(entry):
            if key not in cls.preserved_keys:
                del entry[key]

            if key == cls.reference_key:
                entry[key] = list(DrugIndicationReferenceListUtil.iter_reformat(entry[key]))

        return entry

    @classmethod
    def transform_to_dict(cls, entry_list):
        def extract_molecule_id_and_merge_mesh_subgroups():
            """
            First we need to transform `entry_list`, a list of dictionaries into one dictionary.

            E.g.
                entry_list = [
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
                    'CHEMBL744': [{'mesh_id': 'D020754', 'efo_id': 'Orphanet:98756', 'max_phase_for_ind': 3, ...},
                                  {'mesh_id': 'D020754', 'efo_id': 'Orphanet:94147', 'max_phase_for_ind': 3, ...},
                                  ...]
                }

            will be merged into:

                ret_dict = {
                    'CHEMBL744': [{'mesh_id': 'D020754',
                                   'efo_id': ['Orphanet:98756', 'Orphanet:94147'],
                                   'max_phase_for_ind': 3, ...},
                                  ...]
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
            Uniqueness tests be by running the following code:

            ```python
            import pandas as pd
            import glob

            drug_indication_json_files = glob.iglob(os.path.join(SRC_ROOT_FOLDER, "drug_indication.*.json"))
            entry_list = DrugIndicationAdapter.read_files_and_adapt_contents(drug_indication_json_files)

            df = pd.DataFrame(entry_list)
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

            def primary_key_fn(entry): return entry[cls.primary_key]
            def secondary_key_fn(entry): return entry[cls.secondary_key]

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

                    ret_dict = dict()  # the dict to be returned (actually yielded)

                    # No matter whether `len(subgroup) > 1` or not, the following 2 fields are unique to each subgroup
                    ret_dict["mesh_id"] = subgroup[0]["mesh_id"]
                    ret_dict["mesh_heading"] = subgroup[0]["mesh_heading"]

                    # if len(subgroup) == 1: ret_dict["max_phase_for_ind"] = subgroup[0]["max_phase_for_ind"]
                    # `max` operation applies no matter if `len(subgroup) == 1`
                    ret_dict["max_phase_for_ind"] = max(entry["max_phase_for_ind"] for entry in subgroup)

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
                    ret_dict["efo"] = [{"id": t[0], "term": t[1]} for t in
                                       {*zip(efo_id_list, efo_term_list)}]

                    indication_refs = chain.from_iterable([entry["indication_refs"] for entry in subgroup])
                    # remove the duplicated references (dictionaries underlying) in the collection
                    # see https://stackoverflow.com/a/9427216
                    ret_dict["indication_refs"] = [dict(t) for t in
                                                   {tuple(sorted(ref.items())) for ref in indication_refs}]

                    yield ret_dict

            # Sorting is necessary here because `itertools.groupby()` does not combine non-consecutive groups
            #     E.g. `[1, 1, 2, 2, 1, 1]` will be split into 3 groups, `[1, 1], [2, 2], [1, 1]`
            # Another workaround is to use `pandas.DataFrame.groupby()`
            entry_list.sort(key=primary_key_fn)
            for key, group in groupby(entry_list, key=primary_key_fn):
                drug_ind_list = list(merge_mesh_subgroups(group))
                yield key, drug_ind_list

        return dict(extract_molecule_id_and_merge_mesh_subgroups())


class MoleculeUtil:
    @classmethod
    def reformat(cls, dictionary):
        ret_dict = dict()
        _flag = 0
        for key in list(dictionary):
            if key == 'molecule_chembl_id':
                ret_dict['_id'] = dictionary[key]
            if key == 'molecule_structures' and type(dictionary['molecule_structures']) == dict:
                ret_dict['chembl'] = dictionary
                _flag = 1
                for x, y in iter(dictionary['molecule_structures'].items()):
                    if x == 'standard_inchi_key':
                        ret_dict['chembl'].update(dictionary)
                        ret_dict['chembl'].update({'inchi_key': y})
                    if x == 'canonical_smiles':
                        ret_dict['chembl']['smiles'] = y
                    if x == 'standard_inchi':
                        ret_dict['chembl']['inchi'] = y

        if _flag == 0:
            ret_dict['chembl'] = dictionary
        if 'cross_references' in ret_dict['chembl'] and ret_dict['chembl']['cross_references']:
            ret_dict['chembl']['xrefs'] = MoleculeCrossReferenceListTransformer.transform_to_dict(
                ret_dict['chembl']['cross_references'])

        del ret_dict['chembl']['molecule_structures']
        del ret_dict['chembl']['cross_references']

        ret_dict = unlist(ret_dict)

        # Add "CHEBI:" prefix, standardize the way representing CHEBI IDs
        if 'chebi_par_id' in ret_dict['chembl'] and ret_dict['chembl']['chebi_par_id']:
            ret_dict['chembl']['chebi_par_id'] = 'CHEBI:' + str(ret_dict['chembl']['chebi_par_id'])
        else:
            # clean, could be a None
            ret_dict['chembl'].pop("chebi_par_id", None)

        ret_dict = dict_sweep(ret_dict, vals=[None, ".", "-", "", "NA", "None", "none", " ", "Not Available",
                                              "unknown", "null"])
        ret_dict = value_convert_to_number(ret_dict, skipped_keys=["chebi_par_id", "first_approval"])
        ret_dict = boolean_convert(ret_dict, ["topical", "oral", "parenteral", "dosed_ingredient", "polymer_flag",
                                              "therapeutic_flag", "med_chem_friendly",
                                              "molecule_properties.ro3_pass"])
        return ret_dict


class LoadDataFunction:
    def __init__(self):
        self.drug_indication_dict = None
        self.mechanism_dict = None
        self.target_dict = None
        self.binding_site_dict = None

    def pre_read(self, data_folder):
        # if (self.drug_indication_dict is not None) or \
        #         (self.mechanism_dict is not None) or \
        #         (self.target_dict is not None) or \
        #         (self.binding_site_dict is not None):
        #     raise ValueError("LoadDataFunction already pre-read; should not call `pre_read()` again")

        drug_indication_json_files = glob.iglob(os.path.join(data_folder, "drug_indication.*.json"))
        mechanism_json_files = glob.iglob(os.path.join(data_folder, "mechanism.*.json"))
        target_json_files = glob.iglob(os.path.join(data_folder, "target.*.json"))
        binding_site_json_files = glob.iglob(os.path.join(data_folder, "binding_site.*.json"))

        self.drug_indication_dict = DrugIndicationAdapter.read_files(drug_indication_json_files)
        self.mechanism_dict = MechanismAdapter.read_files(mechanism_json_files)
        self.target_dict = TargetAdapter.read_files(target_json_files)
        self.binding_site_dict = BindingSiteAdapter.read_files(binding_site_json_files)

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

    def __call__(self, input_file):
        molecule_data = json.load(open(input_file))['molecules']
        molecule_list = [MoleculeUtil.reformat(entry) for entry in molecule_data]
        for molecule in molecule_list:
            drug_indications = self.drug_indication_dict.get(molecule["chembl"]["molecule_chembl_id"], None)
            drug_mechanisms = self.mechanism_dict.get(molecule["chembl"]["molecule_chembl_id"], None)

            if drug_indications is not None:
                # Join `molecule::first_approval` to `drug_indication::first_approval`
                first_approval = molecule["chembl"].get("first_approval", None)
                if first_approval:
                    for indication in drug_indications:
                        indication["first_approval"] = first_approval

                molecule["chembl"]["drug_indications"] = drug_indications

            if drug_mechanisms is not None:
                molecule["chembl"]["drug_mechanisms"] = drug_mechanisms

            try:
                _id = molecule["chembl"]['inchi_key']
                molecule["_id"] = _id
            except KeyError:
                pass

            yield molecule
