import json
import os
import tempfile

import pytest

os.environ.setdefault("SPARKIFY_DATA_DIR", tempfile.mkdtemp())

import settings  # noqa: E402
from src import storage  # noqa: E402
from src.utils import validation as v  # noqa: E402


@pytest.fixture(autouse=True)
def data_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "DATA_DIR", str(tmp_path))
    return tmp_path


@pytest.mark.parametrize("value", ["now", "now-1h", "-5d", "now-d", "2024-01-31", "2024-01-31T10:00:00Z"])
def test_time_expr_accepts(value):
    assert v.time_expr(value) == value


@pytest.mark.parametrize("value", ['now"""); evil', "1; drop", "", None, "now\nx"])
def test_time_expr_rejects(value):
    with pytest.raises(v.ValidationError):
        v.time_expr(value)


@pytest.mark.parametrize("value", ['a"); x', "../x", "a b", "", "-lead"])
def test_name_rejects(value):
    with pytest.raises(v.ValidationError):
        v.name(value)


def test_index_pattern_allows_wildcard():
    assert v.index_pattern("filebeat-*") == "filebeat-*"


def test_storage_rejects_path_traversal():
    with pytest.raises(ValueError):
        storage.FileStorage("../outside")


def test_ini_roundtrip_keeps_percent_and_is_private(data_dir):
    s = storage.INIStorage("x.conf")
    s.add("a", {"query": "eval x = y % 10"})
    assert storage.INIStorage("x.conf").getall()["a"]["query"] == "eval x = y % 10"
    assert oct(os.stat(data_dir / "x.conf").st_mode & 0o777) == "0o600"


def test_delete_missing_raises_not_found():
    with pytest.raises(v.NotFoundError):
        storage.FileStorage("y.json").delete("nope")


def test_file_storage_atomic_json(data_dir):
    s = storage.FileStorage("jout/abc")
    s.update("out", [1, 2])
    assert json.load(open(data_dir / "jout" / "abc")) == {"out": [1, 2]}
