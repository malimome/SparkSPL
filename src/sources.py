import json
import time
import uuid

import src.storage as st


class Source:
    def __init__(self):
        self.jstorage = st.FileStorage("sources.conf")
        self.sources = self.jstorage.getall()

    def sources(self):
        return self.sources

    def post_source(self, search):
        pass

    def add_source(self, name, type, path):
        source_id = str(uuid.uuid1())
        submit_time = int(time.time())
        source = {
            "name": name,
            "type": type,
            "path": path,
            "submit_time": submit_time,
        }
        self.sources = self.jstorage.add(source_id, source)
        return {
            "source_id": source_id,
            "source": source
        }

    def get_source(self, source_id):
        source = self.sources[source_id]
        return source

    def del_job(self, source_id):
        return self.jstorage.delete(source_id)


