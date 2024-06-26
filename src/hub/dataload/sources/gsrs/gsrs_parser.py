import gzip
import json
from datetime import datetime, timezone
from typing import Tuple

from biothings import config
from biothings.utils.dataload import dict_convert, dict_sweep

logging = config.logger

process_key = lambda key: key.replace(" ", "_").lower()


def timestamp_to_date(d: dict, keys: Tuple[str]):
    for key in keys:
        if key in d.keys():
            date_obj = datetime.fromtimestamp(int(d[key]), tz=timezone.utc)
            d.update({key: date_obj.strftime("%Y-%m-%d")})
    return d


def load_substances(file_name: str):

    with gzip.GzipFile(file_name) as fd:
        for raw_line in fd:
            record = json.loads(raw_line.decode("utf-8").strip())
            record = dict_convert(record, keyfn=process_key)
            record = dict_sweep(record, vals=["", None], remove_invalid_list=True)
            record = timestamp_to_date(record, ("documentDate", "deprecatedDate"))

            _id = record.pop("uuid")
            yield {"_id": _id, "gsrs": record}
