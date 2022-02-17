Quick start
-----------

`MyChem.info <http://mychem.info>`_ provides two simple web services: one for querying chemical compound or drug objects and the other for chemical/drug annotation retrieval by common IDs (e.g. inchikey, chebiID, pubchem ID etc.). Both return results in `JSON <http://json.org>`_ format.

Chemical/drug query service
^^^^^^^^^^^^^^^^^^^^^^^

URL
"""""
::

    http://mychem.info/v1/query

Examples
""""""""
::

    http://mychem.info/v1/query?q=imatinib
    http://mychem.info/v1/query?q=_exists_:chebi
    http://mychem.info/v1/query?q=_exists_:drugcentral.bioactivity.uniprot.uniprot_id&fields=drugcentral.bioactivity.uniprot


.. Hint:: View nicely formatted JSON result in your browser with this handy add-on: `JSON formatter <https://chrome.google.com/webstore/detail/bcjindcccaagfpapjjmafapmmgkkhgoa>`_ for Chrome or `JSONView <https://addons.mozilla.org/en-US/firefox/addon/jsonview/>`_ for Firefox.


To learn more
"""""""""""""

* You can read `the full description of our query syntax here <doc/chem_query_service.html>`__.
* Try it live on `interactive API page <http://mychem.info/v1/api>`_.
* Batch queries? Yes, you can. do it with `a POST request <doc/chem_query_service.html#batch-queries-via-post>`__.


Chemical/drug annotation service
^^^^^^^^^^^^^^^^^^^^^^^^^^^

URL
"""""
::

    http://mychem.info/v1/chem/<chem_id>

``<chem_id>`` can be any one of the following common chemical/drug identifiers:

    * `InChIKey <https://en.wikipedia.org/wiki/International_Chemical_Identifier#InChIKey>`_,
    * `ChEMBLID <https://www.ebi.ac.uk/chembl/faq#faq40>`_,
    * `ChEBI identifier <http://www.ebi.ac.uk/chebi/aboutChebiForward.do>`_,
    * `PubChem CID <https://pubchem.ncbi.nlm.nih.gov/search/help_search.html#Cid>`_,
    * `UNII <https://www.fda.gov/ForIndustry/DataStandards/SubstanceRegistrationSystem-UniqueIngredientIdentifierUNII/>`_.

Examples
""""""""
::

    http://mychem.info/v1/chem/KTUFNOKKBVMGRW-UHFFFAOYSA-N
    http://mychem.info/v1/chem/CHEBI:45783?fields=chebi
    http://mychem.info/v1/chem/CHEMBL941?fields=chembl
    http://mychem.info/v1/chem/BKJ8M8G5HI?fields=unii


To learn more
"""""""""""""

* You can read `the full description of our query syntax here <doc/chem_annotation_service.html>`__.
* Try it live on `interactive API page <http://mychem.info/v1/api>`_.
* Yes, batch queries via `POST request <doc/chem_annotation_service.html#batch-queries-via-post>`__ as well.
