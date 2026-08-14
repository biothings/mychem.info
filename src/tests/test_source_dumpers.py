import os
import subprocess
import sys
import textwrap
from pathlib import Path


SOURCE_ROOT = Path(__file__).parents[1]

HUB_TEST_SETUP = r"""
import importlib.util
import logging
import os
import sys
import tempfile
import types
from pathlib import Path

source_root = Path(os.environ["MYCHEM_TEST_SOURCE_ROOT"])
config = types.ModuleType("source_dumper_test_config")
config.__file__ = os.path.join(tempfile.gettempdir(), "source_dumper_test_config.py")
config.HUB_DB_BACKEND = {
    "module": "biothings.utils.sqlite3",
    "sqlite_db_folder": tempfile.mkdtemp(prefix="source-dumper-hubdb-"),
}
config.DATA_HUB_DB_DATABASE = "hubdb"
config.DATA_SRC_DATABASE = "srcdb"
config.DATA_SRC_SERVER = "unused"
config.DATA_SRC_PORT = 27017
config.DATA_ARCHIVE_ROOT = tempfile.mkdtemp(prefix="source-dumper-data-")
config.DRUGCENTRAL_PASSWORD = "dosage"
config.logger = logging.getLogger("source-dumper-test")
sys.modules[config.__name__] = config
sys.modules["config"] = config
os.environ["HUB_CONFIG"] = config.__name__


def load_source_module(source, module_name):
    path = source_root / "hub/dataload/sources" / source / (module_name + ".py")
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
"""


def run_source_test(script):
    env = os.environ.copy()
    env["MYCHEM_TEST_SOURCE_ROOT"] = str(SOURCE_ROOT)
    env["PYTHONPATH"] = os.pathsep.join(
        [str(SOURCE_ROOT), env.get("PYTHONPATH", "")]
    ).rstrip(os.pathsep)
    result = subprocess.run(
        [sys.executable, "-c", textwrap.dedent(HUB_TEST_SETUP + script)],
        check=False,
        capture_output=True,
        env=env,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_http_source_metadata_parsing():
    run_source_test(
        r"""
drugbank_module = load_source_module("drugbank_full", "drugbank_full_dump")
pharmgkb_module = load_source_module("pharmgkb", "pharmgkb_dump")
sider_module = load_source_module("sider", "sider_dump")


class Response:
    def __init__(self, *, url, text="", content=b"", headers=None):
        self.url = url
        self.text = text
        self.content = content
        self.headers = headers or {}

    def raise_for_status(self):
        return None


class DrugBankClient:
    def get(self, _url):
        return Response(
            url="https://go.drugbank.com/releases/latest",
            text='<a href="/releases/5-1-22">latest</a>',
        )


drugbank = drugbank_module.DrugBankFullDumper.__new__(
    drugbank_module.DrugBankFullDumper
)
drugbank._state = {"client": DrugBankClient()}
assert drugbank.get_version() == "5.1.22"
assert drugbank.version_key("5.1.22") > drugbank.version_key("5.1.9")

assert pharmgkb_module.PharmGkbDumper.SRC_URLS == [
    "https://api.clinpgx.org/v1/download/file/data/drugs.zip"
]


class SiderClient:
    def get(self, url):
        assert url == "https://sideeffects.embl.de/download/"
        body = b'''
            <a href="/media/download/meddra_freq.tsv.gz">frequency</a>
            <a href="/media/download/meddra_all_se.tsv.gz">side effects</a>
            <a href="/media/download/meddra_all_indications.tsv.gz">indications</a>
            <a href="/media/download/unrelated.tsv.gz">unrelated</a>
        '''
        return Response(url=url, content=body)

    def head(self, url, allow_redirects=False):
        assert allow_redirects is True
        assert url.startswith("https://sideeffects.embl.de/media/download/")
        return Response(
            url=url,
            headers={"Last-Modified": "Fri, 12 Jun 2026 15:42:56 GMT"},
        )


sider = sider_module.SiderDumper.__new__(sider_module.SiderDumper)
sider._state = {"client": SiderClient()}
links = sider.get_download_links()
assert {Path(link).name for link in links} == set(sider.FILES_TO_DUMP)
assert all(link.startswith("https://") for link in links)
assert sider.get_latest_release(links) == "20260612"
"""
    )


def test_drugcentral_driver_is_lazy_and_streams_rows(tmp_path):
    run_source_test(
        rf"""
import csv


class BlockPsycopgImport:
    def find_spec(self, fullname, path=None, target=None):
        if fullname == "psycopg" or fullname.startswith("psycopg."):
            raise ImportError("psycopg deliberately unavailable during discovery")
        return None


blocker = BlockPsycopgImport()
sys.meta_path.insert(0, blocker)
drugcentral_module = load_source_module("drugcentral", "drugcentral_dump")
assert "psycopg" not in drugcentral_module.__dict__

dumper = drugcentral_module.DrugCentralDumper.__new__(
    drugcentral_module.DrugCentralDumper
)
dumper._state = {{"client": None, "logger": logging.getLogger("drugcentral-test")}}
try:
    dumper.prepare_client()
except RuntimeError as exc:
    assert "psycopg[binary]" in str(exc)
else:
    raise AssertionError("Missing Psycopg did not produce an actionable dump error")

sys.meta_path.remove(blocker)


class Column:
    def __init__(self, name):
        self.name = name


class Cursor:
    def __init__(self, rows, names):
        self.rows = rows
        self.description = [Column(name) for name in names]
        self.itersize = None
        self.executed = None

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return None

    def execute(self, query):
        self.executed = query

    def fetchone(self):
        return self.rows[0]

    def __iter__(self):
        return iter(self.rows)


class Client:
    def __init__(self):
        self.server_cursor = Cursor([(1, "Example")], ["id", "name"])
        self.version_cursor = Cursor(
            [(54, __import__("datetime").datetime(2023, 11, 1))],
            ["version", "date"],
        )
        self.closed = False

    def cursor(self, name=None):
        if name is None:
            return self.version_cursor
        assert name == "mychem_structures"
        return self.server_cursor

    def close(self):
        self.closed = True


client = Client()
dumper._state["client"] = client
dumper.prepare_local_folders = lambda path: Path(path).parent.mkdir(
    parents=True, exist_ok=True
)
output = Path({str(tmp_path / 'structures.csv')!r})
dumper.download(
    {{"table_name": "structures", "columns": "id, name"}},
    str(output),
)
assert client.server_cursor.itersize == dumper.CURSOR_ITERSIZE
assert client.server_cursor.executed == "SELECT id, name FROM structures"
with output.open(newline="") as handle:
    assert list(csv.reader(handle)) == [["id", "name"], ["1", "Example"]]
assert dumper.get_latest_release() == "2023-11-01"
dumper.release_client()
assert client.closed is True
assert dumper._state["client"] is None
"""
    )
