"""Code paths changed to run the hub on free-threaded Python (3.14t), checked on any build."""
import csv
import importlib.util
import random
import shutil
import sys
import sysconfig

import pytest

from test_source_dumpers import SOURCE_ROOT, run_source_test

FREE_THREADED = bool(sysconfig.get_config_var("Py_GIL_DISABLED"))


def load_csvsort():
    path = SOURCE_ROOT / "hub/dataload/sources/unichem/csvsort/__init__.py"
    spec = importlib.util.spec_from_file_location("csvsort_under_test", path)
    module = importlib.util.module_from_spec(spec)
    # registered, so forked workers can unpickle memorysort
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("parallel", [False, True])
def test_csvsort_sorts_numeric_column(tmp_path, parallel):
    # parallel sorts the splits in threads on free-threaded Python, in forked processes otherwise
    csvsort = load_csvsort()
    rng = random.Random(0)
    rows = [["key%s" % i, str(rng.randrange(10**9))] for i in range(20_000)]
    input_file = tmp_path / "input.csv"
    with open(input_file, "w", newline="") as fp:
        writer = csv.writer(fp)
        writer.writerow(["key", "value"])
        writer.writerows(rows)

    # a small max_size (in MB) splits the file into a few dozen chunks
    csvsort.csvsort(str(input_file), [1], max_size=0.05, numeric_column=True, parallel=parallel)

    with open(input_file, newline="") as fp:
        reader = csv.reader(fp)
        assert next(reader) == ["key", "value"]
        sorted_rows = list(reader)
    assert sorted(sorted_rows) == sorted(rows)
    assert [int(row[1]) for row in sorted_rows] == sorted(int(row[1]) for row in rows)


def test_gtopdb_remove_tags_keeps_text_only():
    run_source_test(
        r"""
import biothings.hub  # sets biothings.config, as bin/hub.py does before loading plugins

path = source_root / "plugins/gtopdb/parser.py"
spec = importlib.util.spec_from_file_location("gtopdb_parser", path)
parser = importlib.util.module_from_spec(spec)
spec.loader.exec_module(parser)

assert parser.remove_tags("imatinib <i>mesylate</i>") == "imatinib mesylate"
assert parser.remove_tags("5-HT<sub>1A</sub> receptor") == "5-HT1A receptor"
assert parser.remove_tags("&alpha;-tocopherol &amp; more") == "α-tocopherol & more"
assert parser.remove_tags("no tags") == "no tags"
assert parser.remove_tags(42) == 42
assert "lxml" not in sys.modules
"""
    )


@pytest.mark.skipif(shutil.which("md5sum") is None, reason="needs md5sum (coreutils)")
def test_pubchem_md5_check_runs_in_data_folder_without_chdir():
    run_source_test(
        r"""
import hashlib

pubchem_module = load_source_module("pubchem", "pubchem_dump")


class Dumper(pubchem_module.PubChemDumper):
    ARCHIVE = True
    new_data_folder = None  # set per instance below, instead of computed from the release


folder = Path(tempfile.mkdtemp(prefix="pubchem-md5-"))
(folder / "compound.xml.gz").write_bytes(b"pubchem")
digest = hashlib.md5(b"pubchem").hexdigest()
(folder / "compound.xml.gz.md5").write_text(digest + "  compound.xml.gz\n")

dumper = Dumper.__new__(Dumper)
dumper._state = {"logger": logging.getLogger("pubchem-test")}
dumper.new_data_folder = str(folder)
cwd = os.getcwd()
dumper.post_dump()
assert os.getcwd() == cwd

(folder / "compound.xml.gz").write_bytes(b"corrupted")
try:
    dumper.post_dump()
except pubchem_module.DumperException:
    pass
else:
    raise AssertionError("A bad checksum was not reported")
assert os.getcwd() == cwd
assert (folder / "failed_dump.list").read_text() == "compound.xml.gz.md5"
"""
    )


def test_unii_id_falls_back_to_pubchem_then_unii():
    # with pandas 3's copy-on-write, a chained fillna(inplace=True) would leave these _ids empty
    run_source_test(
        r"""
unii_parser = load_source_module("unii", "unii_parser")
records = Path(tempfile.mkdtemp(prefix="unii-")) / "UNII_Records.txt"
records.write_text(
    "UNII\tDisplay Name\tINCHIKEY\tPUBCHEM\tNCIT\n"
    "AAA111\tWith inchikey\tKEY-ONE\t111\t\n"
    "BBB222\tPubchem only\t\t222\t\n"
    "CCC333\tUnii only\t\t\t\n"
)
docs = {doc["_id"]: doc["unii"] for doc in unii_parser.load_data(str(records))}
assert set(docs) == {"KEY-ONE", "222", "CCC333"}
assert docs["222"]["pubchem"] == 222
assert docs["CCC333"]["display_name"] == "Unii only"
"""
    )


@pytest.mark.skipif(not FREE_THREADED, reason="needs a free-threaded Python build")
def test_hub_imports_keep_the_gil_disabled():
    # one extension module without free-threading support (lxml, pandas<3...) re-enables the
    # GIL for the whole hub; Python names it in a RuntimeWarning
    # Uploaders and hub.datatransform.keylookup are skipped: they connect to the source database
    # when imported (MyChemKeyLookup class attributes, the key lookup graph's edges).
    run_source_test(
        r"""
import io
import warnings

gil_warnings = []
warnings.simplefilter("always")
warnings.showwarning = lambda message, *args, **kwargs: gil_warnings.append(str(message))

import biothings.hub.dataload.dumper
import biothings.hub.dataload.uploader
import biothings.hub.datatransform

failed = {}
for path in sorted((source_root / "hub/dataload/sources").glob("*/*.py")):
    if "upload" in path.stem or path.stem in ("__init__", "setup"):
        continue
    try:
        load_source_module(path.parent.name, path.stem)
    except Exception as exc:
        failed[path.parent.name + "/" + path.name] = repr(exc)

spec = importlib.util.spec_from_file_location("gtopdb_parser", source_root / "plugins/gtopdb/parser.py")
spec.loader.exec_module(importlib.util.module_from_spec(spec))

import bs4, numpy, pandas  # noqa: E401

# pandas only imports its HTML parser when read_html is called (fda_orphan_drug uses bs4 + html5lib)
pandas.read_html(io.StringIO("<table><tr><th>a</th></tr><tr><td>1</td></tr></table>"), flavor="bs4")

assert not sys._is_gil_enabled(), [w for w in gil_warnings if "GIL" in w] or failed
"""
    )
