import threading

import src.storage as st
from src.utils import validation as v
from src.utils.validation import NotFoundError


class Index:
    """Index registry. Instantiate once; all methods are thread-safe."""
    FIELDS = ("retention", "retention_size", "readonly")

    def __init__(self):
        self.istorage = st.INIStorage("indexes.conf")
        self.lock = threading.RLock()

    def get_indexes(self):
        with self.lock:
            return dict(self.istorage.getall())

    def _clean(self, index):
        return {f: index[f] for f in self.FIELDS if index.get(f) is not None}

    def add_index(self, index):
        name = v.name(index.get("name"), "index name")
        with self.lock:
            if name in self.istorage.getall():
                raise v.ValidationError("Index %s already exists" % name)
            self.istorage.add(name, self._clean(index))
        return index

    def get_index(self, name):
        with self.lock:
            indexes = self.istorage.getall()
            if name not in indexes:
                raise NotFoundError("Index %s does not exist" % name)
            return indexes[name]

    def del_index(self, name):
        with self.lock:
            self.get_index(name)
            self.istorage.delete(name)
