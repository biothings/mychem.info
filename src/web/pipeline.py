from biothings.web.query.formatter import ESResultFormatter
from biothings.web.options import OptionError


class MyChemESResultFormatter(ESResultFormatter):
    """Subclass of ESResultFormatter to add list_filter transformation"""

    def transform_hit(self, path, doc, options):
        super().transform_hit(path, doc, options)
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
