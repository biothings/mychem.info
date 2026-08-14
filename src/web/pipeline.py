import re

from biothings.web.query.formatter import ESResultFormatter
from biothings.web.query.pipeline import AsyncESQueryPipeline
from biothings.web.options import OptionError


DRUGBANK_ID_PATTERN = re.compile(r"(?:drugbank:)?(?P<term>db[0-9]+)", re.I)


def _drugbank_id(value):
    if not isinstance(value, str):
        return None
    match = DRUGBANK_ID_PATTERN.fullmatch(value)
    return match.group("term").upper() if match else None


def _field_values(value, path):
    if not path:
        if isinstance(value, list):
            for item in value:
                yield from _field_values(item, ())
        elif value is not None:
            yield value
        return

    if isinstance(value, list):
        for item in value:
            yield from _field_values(item, path)
    elif isinstance(value, dict) and path[0] in value:
        yield from _field_values(value[path[0]], path[1:])


def _has_primary_drugbank_id(document, identifier):
    return any(
        str(value).upper() == identifier
        for value in _field_values(document, ("drugbank", "id"))
    )


class MyChemESQueryPipeline(AsyncESQueryPipeline):
    """Prefer authoritative DrugBank IDs while retaining xref fallbacks."""

    async def fetch(self, id, **options):
        result = await super().fetch(id, **options)

        if isinstance(id, list):
            primary_queries = set()
            primary_result_indexes = set()
            for index, document in enumerate(result):
                if not isinstance(document, dict):
                    continue
                query = document.get("query")
                identifier = _drugbank_id(query)
                if identifier and _has_primary_drugbank_id(document, identifier):
                    primary_queries.add(query)
                    primary_result_indexes.add(index)

            if not primary_queries:
                return result
            return [
                document
                for index, document in enumerate(result)
                if document.get("query") not in primary_queries
                or index in primary_result_indexes
            ]

        identifier = _drugbank_id(id)
        if not identifier or not isinstance(result, list):
            return result

        primary_matches = [
            document
            for document in result
            if _has_primary_drugbank_id(document, identifier)
        ]
        if len(primary_matches) == 1:
            return primary_matches[0]
        return primary_matches or result


class MyChemESResultFormatter(ESResultFormatter):
    """Subclass of ESResultFormatter to add list_filter transformation"""

    def transform_hit(self, path, doc, hit, options):
        super().transform_hit(path, doc, hit, options)
        # process list_filter, e.g. list_filter=aaa.bbb:sub_a=val_a,val_aa|sub_b=val_b
        if options.list_filter:
            try:
                list_field_path, sub_field_filters = options.list_filter.split(':')
            except ValueError as err:
                raise OptionError("Invalid value for list_filter parameter") from err
            parent_path, list_field = list_field_path.rsplit(".", maxsplit=1)
            if path == parent_path and list_field in doc:
                # we handle list_filter at its parent field level,
                # so that we can set a filtered list value
                _list = doc[list_field]
                if not isinstance(_list, list):
                    _list = [_list]
                sub_field_filters = [sub_field.split("=") for sub_field in sub_field_filters.split('|')]
                try:
                    sub_field_filters = [
                        (fld.strip(), [v.strip() for v in val.split(",")]) for fld, val in sub_field_filters
                    ]
                except ValueError as err:
                    raise OptionError("Invalid value for list_filter parameter") from err
                # list(_list) below creates a copy of _list for the loop,
                # because we will modify _list itself in the loop
                for item in list(_list):
                    if isinstance(item, dict):
                        for sub_field, val_list in sub_field_filters:
                            if str(item.get(sub_field, '')) not in val_list:
                                # cast the value to str, so we only compare its string value for numbers
                                _list.remove(item)
                                break
                    else:
                        _list.remove(item)
                doc[list_field] = _list
