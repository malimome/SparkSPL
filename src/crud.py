import threading
import uuid

import src.storage as st
from src.utils import validation as v
from src.utils.validation import NotFoundError


class EntityStore:
    """CRUD over an INI file where each section is an entity.

    Only whitelisted string fields are persisted, so clients cannot inject arbitrary keys.
    """
    FIELDS = ()
    LABEL = "item"

    def __init__(self, filename):
        self.storage = st.INIStorage(filename)
        self.lock = threading.RLock()

    def _clean(self, payload):
        if not isinstance(payload, dict):
            raise v.ValidationError("Invalid %s body" % self.LABEL)
        return {f: str(payload[f]) for f in self.FIELDS if payload.get(f) is not None}

    def _all(self):
        return self.storage.getall()

    def _key(self, item_id):
        return v.uuid_str(item_id, "%s id" % self.LABEL)

    def all(self):
        with self.lock:
            return dict(self._all())

    def add(self, payload):
        item_id = str(uuid.uuid4())
        item = self._clean(payload)
        with self.lock:
            self._all()
            self.storage.add(item_id, item)
        return item_id, item

    def get(self, item_id):
        item_id = self._key(item_id)
        with self.lock:
            items = self._all()
            if item_id not in items:
                raise NotFoundError("%s %s does not exist" % (self.LABEL.capitalize(), item_id))
            return items[item_id]

    def update(self, item_id, payload):
        item_id = self._key(item_id)
        with self.lock:
            current = dict(self.get(item_id))
            current.update(self._clean(payload))
            self.storage.update(item_id, current)
        return current

    def delete(self, item_id):
        item_id = self._key(item_id)
        with self.lock:
            self.get(item_id)
            self.storage.delete(item_id)
