.. Data

Chemical annotation data
************************

.. _data_sources:

Data sources
------------

We currently obtain chemical annotation data from several data resources and
keep them up-to-date, so that you don't have to do it:

.. _AEOLUS: http://www.nature.com/articles/sdata201626
.. _ChEBI: https://www.ebi.ac.uk/chebi/
.. _ChEMBL: https://www.ebi.ac.uk/chembl/
.. _DrugCentral: http://drugcentral.org/
.. _FDA Orphan Drug Designations: https://www.accessdata.fda.gov/scripts/opdlisting/oopd/
.. _ginas: https://ginas.ncats.nih.gov
.. _NDC: http://www.fda.gov/Drugs/InformationOnDrugs/ucm142438.htm
.. _PharmGKB: https://www.pharmgkb.org/
.. _PubChem: https://pubchem.ncbi.nlm.nih.gov/
.. _SIDER: http://sideeffects.embl.de/
.. _UNII: https://fdasis.nlm.nih.gov/srs/


.. raw:: html

    <div class='metadata-table'>

Total Chemicals loaded: **N/A**

+---------------------------------+---------------+---------------------------+-----------------+------------------------------------------+
| Source                          | version       | # of chemicals            | key name*       |  data notes                              |
+=================================+===============+===========================+=================+==========================================+
| `AEOLUS`_                       | \-            | 0                         | aeolus          |  `notes <data_source.html#aeolus>`_      |
+---------------------------------+---------------+---------------------------+-----------------+------------------------------------------+
| `ChEBI`_                        | \-            | 0                         | chebi           |  `notes <data_source.html#chebi>`_       |
+---------------------------------+---------------+---------------------------+-----------------+------------------------------------------+
| `ChEMBL`_                       | \-            | 0                         | chembl          |                                          |
+---------------------------------+---------------+---------------------------+-----------------+------------------------------------------+
| `DrugCentral`_                  | \-            | 0                         | drugcentral     |                                          |
+---------------------------------+---------------+---------------------------+-----------------+------------------------------------------+
| `FDA Orphan Drug Designations`_ | \-            | 0                         | fda_orphan_drug |                                          |
+---------------------------------+---------------+---------------------------+-----------------+------------------------------------------+
| `ginas`_                        | \-            | 0                         | ginas           |                                          |
+---------------------------------+---------------+---------------------------+-----------------+------------------------------------------+
| `NDC`_                          | \-            | 0                         | ndc             |  `notes <data_source.html#ndc>`_         |
+---------------------------------+---------------+---------------------------+-----------------+------------------------------------------+
| `PharmGKB`_                     | \-            | 0                         | pharmgkb        |                                          |
+---------------------------------+---------------+---------------------------+-----------------+------------------------------------------+
| `PubChem`_                      | \-            | 0                         | pubchem         |                                          |
+---------------------------------+---------------+---------------------------+-----------------+------------------------------------------+
| `SIDER`_                        | \-            | 0                         | sider           |  `notes <data_source.html#sider>`_       |
+---------------------------------+---------------+---------------------------+-----------------+------------------------------------------+
| `UNII`_                         | \-            | 0                         | unii            |                                          |
+---------------------------------+---------------+---------------------------+-----------------+------------------------------------------+


.. raw:: html

    </div>

\* key name: this is the key for the specific annotation data in a chemical object.

The most updated information can be accessed `here <http://mychem.info/v1/metadata>`_.

.. note:: Each data source may have its own usage restrictions. Please refer to the data source pages above for their specific restrictions.


.. _chemical_object:

Chemical object
---------------

Chemical annotation data are both stored and returned as a chemical object, which
is essentially a collection of fields (attributes) and their values:

.. code-block:: json


    {
      "_id": "KTUFNOKKBVMGRW-UHFFFAOYSA-N",
      "unii": {
        "_license": "http://bit.ly/2Pg8Oo9",
        "inchikey": "KTUFNOKKBVMGRW-UHFFFAOYSA-N",
        "ingredient_type": "INGREDIENT SUBSTANCE",
        "inn_id": "8031",
        "molecular_formula": "C29H31N7O",
        "ncit": "C62035",
        "preferred_term": "IMATINIB",
        "pubchem": "5291",
        "registry_number": "152459-95-5",
        "rxcui": "282388",
        "smiles": "CN1CCN(CC2=CC=C(C=C2)C(=O)NC3=CC(NC4=NC=CC(=N4)C5=CC=CN=C5)=C(C)C=C3)CC1",
        "unii": "BKJ8M8G5HI"
      }
    }


The example above omits many of the available fields.  For a full example,
check out `this example chemical <http://mychem.info/v1/chem/KTUFNOKKBVMGRW-UHFFFAOYSA-N>`_, or try the `interactive API page <http://mychem.info/v1/api>`_.


_id field
---------

Each individual chemical object contains an "**_id**" field as the primary key.  Where possible, MyChem.info chemical objects use `InChIKey <https://en.wikipedia.org/wiki/International_Chemical_Identifier#InChIKey>`_ (a 27 character hash of the International Chemical Identifier) as their "**_id**".  If an InChIKey isn't available, any one of the following datasource IDs may be used:

    * `DrugBank accession number <https://www.drugbank.ca/documentation>`_,
    * `ChEMBLID <https://www.ebi.ac.uk/chembl/faq#faq40>`_,
    * `ChEBI identifier <http://www.ebi.ac.uk/chebi/aboutChebiForward.do>`_,
    * `PubChem CID <https://pubchem.ncbi.nlm.nih.gov/search/help_search.html#Cid>`_,
    * `UNII <https://www.fda.gov/ForIndustry/DataStandards/SubstanceRegistrationSystem-UniqueIngredientIdentifierUNII/>`__.

_score field
------------

You will often see a “_score” field in the returned chemical object, which is the internal score representing how well the query matches the returned chemical object. It probably does not mean much in `chemical annotation service <data.html>`_ when only one chemical object is returned. In `chemical query service <chem_query_service.html>`_, by default, the returned chemical hits are sorted by the scores in descending order.


.. _available_fields:

Available fields
----------------

The table below lists all of the possible fields that could be in a chemical object, as well as all of their parents (for nested fields).  If the field is indexed, it may also be directly queried.


.. raw:: html

    <table class='indexed-field-table stripe'>
        <thead>
            <tr>
                <th>Field</th>
                <th>Indexed</th>
                <th>Type</th>
                <th>Notes</th>
            </tr>
        </thead>
        <tbody>
        </tbody>
    </table>

    <div id="spacer" style="height:300px"></div>
