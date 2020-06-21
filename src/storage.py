import configparser
import json
import os
import tempfile
import threading

import settings
from src.utils.validation import NotFoundError


class Storage(object):
    """Thread-safe key/value storage persisted to a file under settings.DATA_DIR."""

    def __init__(self, name):
        base = os.path.realpath(settings.DATA_DIR)
        path = os.path.realpath(os.path.join(base, name))
        if os.path.commonpath([base, path]) != base:
            raise ValueError("Storage path escapes the data directory")
        self.file = path
        self.items = {}
        self.lock = threading.RLock()

    def getall(self):
        raise NotImplementedError

    def get(self, id):
        with self.lock:
            if id not in self.items:
                raise NotFoundError("Item %s does not exist" % id)
            return self.items[id]

    def add(self, id, content):
        with self.lock:
            self.items[id] = content
            self._put(self.items)
            return self.items

    def update(self, id, content):
        return self.add(id, content)

    def delete(self, id):
        with self.lock:
            if id not in self.items:
                raise NotFoundError("Item %s does not exist" % id)
            del self.items[id]
            self._put(self.items)
            return self.items

    def _put(self, items):
        raise NotImplementedError

    def _write_atomic(self, writer):
        """Write to a private temp file and rename it, so readers never see partial data."""
        directory = os.path.dirname(self.file)
        os.makedirs(directory, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=directory, prefix=".tmp-")
        try:
            with os.fdopen(fd, "w") as fp:
                writer(fp)
            os.replace(tmp, self.file)
        except Exception:
            if os.path.exists(tmp):
                os.remove(tmp)
            raise

    def hard_delete_file(self):
        try:
            os.remove(self.file)
            return True
        except OSError:
            return False


class FileStorage(Storage):
    def getall(self):
        with self.lock:
            try:
                with open(self.file, "r") as fp:
                    self.items = json.load(fp)
            except (ValueError, FileNotFoundError):
                pass
            return self.items

    def _put(self, items):
        self._write_atomic(lambda fp: json.dump(items, fp, indent=2, sort_keys=True))


class INIStorage(Storage):
    def getall(self):
        with self.lock:
            config = configparser.RawConfigParser(allow_no_value=True)
            config.read(self.file)
            self.items = {s: dict(config.items(s)) for s in config.sections()}
            return self.items

    def _put(self, items):
        config = configparser.RawConfigParser()
        config.read_dict({k: {str(a): "" if b is None else str(b) for a, b in v.items()}
                          for k, v in items.items()})
        self._write_atomic(config.write)


class JINIStorage(INIStorage):
    """INI storage for jobs, which keeps the Livy session reference in sid/tid."""

    def getall(self):
        entries = super(JINIStorage, self).getall()
        for v in entries.values():
            if "sid" in v and "tid" in v:
                v["internal_session"] = {"sid": v.pop("sid"), "tid": v.pop("tid")}
        return entries

    def _put(self, items):
        entries = {}
        for i, item in items.items():
            c = dict(item)
            if "internal_session" in c:
                session = c.pop("internal_session")
                c["sid"] = session["sid"]
                c["tid"] = session["tid"]
            entries[i] = c
        super(JINIStorage, self)._put(entries)
