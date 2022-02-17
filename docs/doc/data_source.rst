Data Sources
************

This page records the notes specific to each data source, regarding the ETL process when their data were integrated into `MyChem.info <http://mychem.info>`_:

.. note:: The structured metadata about all data sources can be accessed from `the metadata endpoint <http://mychem.info/v1/metadata>`_. The detailed information about the integrated data is described in this `data page <data.html>`_.


AEOLUS
------

The value of `aeolus.outcomes` field is a list of outcome objects. The list is sorted by the `aeolus.outcomes.case_count` field in the descending order. In some rare cases, the list can be a large list (up to ~10K). The large list is often associated with common chemicals (e.g. asprin, omeprazole). For the purpose of reducing the total size of a single chemical object, we truncated the `aeolus.outcomes` list up to 5000 items.

This truncation affects only 165 objects (as of 2018-11-28, `full list here <https://github.com/biothings/mychem.info/blob/master/src/hub/dataload/sources/aeolus/truncated_docs.tsv>`_), comparing to total 3,044 objects containing `aeolus` data (~5%).


ChEBI
------

The following `chebi.xrefs` fields are subject to truncation::

    chebi.xrefs.intenz
    chebi.xrefs.rhea
    chebi.xrefs.uniprot
    chebi.xrefs.sabio_rk
    chebi.xrefs.patent

The value of each fields above is a list. In some cases, the list can be very large (up to ~90K items). The large list is often associated with common chemicals (e.g. water, ATP). For the purpose of reducing the total size of a single chemical object, we removed the above fields if their values contain more than 1000 items.

This truncation affects only 143 objects (as of 2018-11-28, `full list here <https://github.com/biothings/mychem.info/blob/master/src/hub/dataload/sources/chebi/exclusion_ids.py>`_), comparing to total 98,511 objects containing `chebi` data (<0.15%).

ChEMBL
------

Data for `ChEMBL <https://www.ebi.ac.uk/chemb>`_ is pulled from 6 online json sources:

- `Molecule <https://www.ebi.ac.uk/chembl/api/data/molecule.json>`_, which serves as a root data source. Entries from other sources are attached molecule entries as new fields
- `Drug Indications <https://www.ebi.ac.uk/chembl/api/data/drug_indication.json>`_, which will parsed and attached to molecule entries, e.g. ``molecule["drug_indications"] = list_of_drug_indications``
- `Drug Mechanisms <https://www.ebi.ac.uk/chembl/api/data/mechanism.json>`_, which will parsed and attached to molecule entries, e.g. ``molecule["drug_mechanism"] = list_of_drug_mechanism``
- `Drug <https://www.ebi.ac.uk/chembl/api/data/drug.json>`_, used to augment ``first_approval`` field to drug indication entries
- `Target <https://www.ebi.ac.uk/chembl/api/data/target.json>`_, used to augment ``target_name`` and ``target_organism`` fields to drug mechanism entries
- `Binding Sites <https://www.ebi.ac.uk/chembl/api/data/binding_site.json>`_, used to augment ``binding_site_name`` field to drug mechanism entries

Dictionaries are created for each chemical based on their ``standardinchikey`` in the following format: 

``{_id: "standardinchikey", "chembl": {"<drug_indications>":"<...>", "<drug_mechanisms>":"<...>",..}}``

DrugBank
--------

Due to licensing restrictions, we removed DrugBank data from MyChem.info on 09/08/2021.

.. DrugCentral
.. -----------

FDA Orphan Drug Designations
----------------------------

This datasource was added to MyChem.info on 09/08/2020. The data comes from a JSON file `hosted here <https://raw.githubusercontent.com/r76941156/fda_orphan_drug/main/data.json>`_

.. ginas
.. -----

NDC
---

The value of `ndc` field is a list. In some rare cases, the list can be a large list (up to ~4K). The entire `ndc` field will be removed if the list contains more than 1000 items.

This truncation affects only 4 objects (as of 2018-11-28, `full list here <https://github.com/biothings/mychem.info/blob/master/src/hub/dataload/sources/ndc/exclusion_ids.py>`_), comparing to total 36,893 objects containing `ndc` data (~0.01%).

.. PharmGKB
.. --------

.. PubChem
.. -------

SIDER
------

The value of `sider` field is a list of side-effect objects. The list of side-effect objects are already sorted by the value of the `sider.side_effect.frequency` field in the descending order (e.g. "92.6%", "65%"). In the case of no `sider.side_effect.frequency` value or non-numeric values (e.g. "common", "rare", "post-marketing"), these side-effect objects are kept at the top of the list.

In some rare cases, the list can be very large (up to ~5K). We then truncated the list up to 2000.

This truncation affects only 26 objects (as of 2018-11-28, `full list here <https://github.com/biothings/mychem.info/blob/master/src/hub/dataload/sources/sider/truncated_docs.tsv>`_), comparing to total 1,507 objects containing `sider` data (~1.7%).


UniChem
------

Data for `UniChem <https://www.ebi.ac.uk/unichem>`_ is pulled from 3 files, including:


- ``UC_SOURCE.txt.gz``, which (once decompressed) supplies matching values for source ids (``src_id``) and source names. 
- ``UC_STRUCTURE.txt.gz``, which provides the UniChem entry identifies (``uci``) as well as the standardinchikey (``standardinchikey``)
- ``UC_XREF.txt.gz``, which provides a source id (``src_id``), the name used for the given source (``src_compound_id``), and the ``uci``

Using the above values from each of the 3 files, dictionaries are created for each chemical based on their ``standardinchikey`` in the following format: 

``{_id: "standardinchikey", "unichem": {"<source_name>":"<source_specific_id>", "<source_name>":"<source_specific_id>",..}}``

Directories containing file dumps can be found at: ftp://ftp.ebi.ac.uk/pub/databases/chembl/UniChem/data/oracleDumps/

.. UNII
.. ----

.. raw:: html

    <div id="spacer" style="height:300px"></div>
