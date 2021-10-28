Chemical annotation service
*************************************

This page describes the reference for the MyChem.info chemical annotation web
service.  It's also recommended to try it live on our `interactive API page <http://mychem.info/v1/api>`_.


Service endpoint
=================
::

    http://mychem.info/v1/chem


GET request
==================

Obtaining the chemical annotation via our web service is as simple as calling this URL::

    http://mychem.info/v1/chem/<chemid>

**chemid** above is any one of several common chemical identifiers: `InChIKey <https://en.wikipedia.org/wiki/International_Chemical_Identifier#InChIKey>`_, `ChEMBLID <https://www.ebi.ac.uk/chembl/faq#faq40>`_, `ChEBI identifier <http://www.ebi.ac.uk/chebi/aboutChebiForward.do>`_, `PubChem CID <https://pubchem.ncbi.nlm.nih.gov/search/help_search.html#Cid>`_, `UNII <https://www.fda.gov/ForIndustry/DataStandards/SubstanceRegistrationSystem-UniqueIngredientIdentifierUNII/>`_.

By default, this will return the complete chemical annotation object in JSON format. See `here <#returned-object>`_ for an example and :ref:`here <chemical_object>` for more details. If the input **chemid** is not valid, 404 (NOT FOUND) will be returned.

Optionally, you can pass a "**fields**" parameter to return only the annotation you want (by filtering returned object fields)::

    http://mychem.info/v1/chem/KTUFNOKKBVMGRW-UHFFFAOYSA-N?fields=chembl

"**fields**" accepts any attributes (a.k.a fields) available from the chemical object. Multiple attributes should be separated by commas. If an attribute is not available for a specific chemical object, it will be ignored. Note that the attribute names are case-sensitive.

Just like the `chemical query service <chem_query_service.html>`_, you can also pass a "**callback**" parameter to make a `JSONP <http://ajaxian.com/archives/jsonp-json-with-padding>`_ call.


Query parameters
-----------------

fields
""""""""
    Optional, can be a comma-separated fields to limit the fields returned from the chemical object. If "fields=all", all available fields will be returned. Note that it supports dot notation as well, e.g., you can pass "chebi.name". Default: "fields=all".

callback
"""""""""
    Optional, you can pass a "**callback**" parameter to make a `JSONP <http://ajaxian.com/archives/jsonp-json-with-padding>`_ call.

filter
"""""""
    Alias for "fields" parameter.

email
""""""
    Optional, if you are regular users of our services, we encourage you to provide us an email, so that we can better track the usage or follow up with you.

-----------------

Returned object
---------------

A GET request like this::

    http://mychem.info/v1/chem/KTUFNOKKBVMGRW-UHFFFAOYSA-N?fields=pubchem

should return a chemical object below:

.. container :: chemical-object-container

    .. include :: chem_object.json


Batch queries via POST
======================

Although making simple GET requests above to our chemical query service is sufficient in most use cases,
there are some times you might find it's easier to batch query (e.g., retrieving chemical
annotations for multiple chemicals). Fortunately, you can also make batch queries via POST requests when you
need::


    URL: http://mychem.info/v1/chem
    HTTP method:  POST


Query parameters
----------------

ids
"""""
    Required. Accept multiple chemical ids separated by comma, e.g., "ids=SDUQYLNIPVEERB-QPPQHZFASA-N,SESFRYSPDFLNCH-UHFFFAOYSA-N,SHGAZHPCJJPHSC-ZVCIMWCZSA-N". Note that currently we only take the input ids up to **1000** maximum, the rest will be omitted.

fields
"""""""
    Optional, can be a comma-separated fields to limit the fields returned from the matching hits.
    If “fields=all”, all available fields will be returned. Note that it supports dot notation as well, e.g., you can pass "chembl" or "chebi.name". Default: "all".

email
""""""
    Optional, if you are regular users of our services, we encourage you to provide us an email, so that we can better track the usage or follow up with you.

Example code
------------

Unlike GET requests, you can easily test them from browser, make a POST request is often done via a
piece of code, still trivial of course. Here is a sample python snippe using `httplib2 <https://pypi.org/project/httplib2/>`_ modulet::

    import httplib2
    h = httplib2.Http()
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    params = 'ids=SDUQYLNIPVEERB-QPPQHZFASA-N,SESFRYSPDFLNCH-UHFFFAOYSA-N&fields=chebi.name'
    res, con = h.request('http://mychem.info/v1/chem', 'POST', params, headers=headers)

or this example using `requests <http://docs.python-requests.org>`_ module::

    import requests
    params = {'ids': 'SDUQYLNIPVEERB-QPPQHZFASA-N,SESFRYSPDFLNCH-UHFFFAOYSA-N', 'fields': 'chebi.name'}
    res = request.post('http://mychem.info/v1/chem', params)
    con = res.json()


Returned object
---------------

Returned result (the value of "con" variable above) from above example code should look like this:


.. code-block :: json

    [
        {
            "query": "SDUQYLNIPVEERB-QPPQHZFASA-N",
            "_id": "SDUQYLNIPVEERB-QPPQHZFASA-N",
            "_version": 1,
            "chebi": {
                "_license": "http://bit.ly/2KAUCAm",
                "name": "gemcitabine"
            }
        },
        {
            "query": "SESFRYSPDFLNCH-UHFFFAOYSA-N",
            "_id": "SESFRYSPDFLNCH-UHFFFAOYSA-N",
            "_version": 1,
            "chebi": {
                "_license": "http://bit.ly/2KAUCAm",
                "name": "benzyl benzoate"
            }
        }
    ]

.. raw:: html

    <div id="spacer" style="height:300px"></div>
