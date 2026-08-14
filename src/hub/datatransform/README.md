# MyChem DataTransform indexes

MongoDB-backed identifier transforms require an index on every lookup field.
Lookup edges are constructed during source-module import, so a missing index
fails source discovery and is visible immediately after a hub restart. This is
intentional: keylookup must never silently run an unbounded MongoDB query.

The owning uploaders create the SMILES indexes in `post_update_data` after new
uploads. Existing source collections need this one-time migration before the
next hub restart (replace the URI and database placeholders):

```shell
mongosh "<source MongoDB URI>/<source database>" --eval '
db.getCollection("chebi").createIndex({"chebi.smiles": 1});
db.getCollection("chembl").createIndex({"chembl.smiles": 1});
db.getCollection("drugcentral").createIndex({"drugcentral.structures.smiles": 1});
db.getCollection("unii").createIndex({"unii.smiles": 1});
'
```

This migration is required because the indexes are validated before an
uploader's next `post_update_data` hook can run.
