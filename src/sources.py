import threading
import time

import src.storage as st
from src.utils import validation as v
from src.utils.validation import NotFoundError

SECRET_FIELDS = ("password", "connection_string")


def _redact(source):
    return {k: ("***" if k in SECRET_FIELDS and val else val) for k, val in source.items()}


class Source:
    def __init__(self):
        self.sstorage = st.INIStorage("sources.conf")
        self.lock = threading.RLock()
        self.sources = self.sstorage.getall()

    def all_sources(self):
        with self.lock:
            self.sources = self.sstorage.getall()
            return {k: _redact(val) for k, val in self.sources.items()}

    def _clean(self, payload):
        return {
            "index": v.index_pattern(payload.get("index") or "*"),
            "desc": str(payload.get("description") or ""),
            "query": str(payload.get("query") or ""),
            "type": v.source_type(payload.get("type") or "default"),
            "connection_string": str(payload.get("connection") or ""),
        }

    def add_source(self, payload):
        source_id = v.name(payload.get("name"), "source name")
        with self.lock:
            self.sources = self.sstorage.getall()
            if source_id in self.sources:
                raise v.ValidationError("Source %s already exists" % source_id)
            source = self._clean(payload)
            source["submit_time"] = int(time.time())
            self.sources = self.sstorage.add(source_id, source)
        return {"source_id": source_id, "source": _redact(source)}

    def get_source(self, source_id):
        """Return the full source (including secrets) for internal use."""
        with self.lock:
            self.sources = self.sstorage.getall()
            if source_id not in self.sources:
                raise NotFoundError("Source %s does not exist" % source_id)
            return dict(self.sources[source_id])

    def get_public_source(self, source_id):
        return _redact(self.get_source(source_id))

    def update_source(self, source_id, payload):
        with self.lock:
            current = self.get_source(source_id)
            current.update(self._clean(dict(payload, name=source_id)))
            self.sources = self.sstorage.update(source_id, current)
        return _redact(current)

    def del_source(self, source_id):
        with self.lock:
            self.get_source(source_id)
            self.sources = self.sstorage.delete(source_id)
