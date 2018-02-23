import json
import time
import uuid

import src.storage as st


class Source:
    def __init__(self):
        self.sstorage = st.INIStorage("sources.conf")
        self.sources = self.sstorage.getall()

    def sources(self):
        return self.sources

    def add_source(self, payload):
        source_id = payload['name']
        submit_time = int(time.time())
        source = {
            "desc": payload['description'],
            "query": payload['query'],
            "submit_time": submit_time,
            "type": payload['type'],
            "host": "localhost",
            "port": "port",
            "connection_string": payload['connection'],
            "username": "username",
            "password": "pass"
        }
        self.sources = self.sstorage.add(source_id, source)
        return {
            "source_id": source_id,
            "source": source
        }

    def get_source(self, source_id):
        source = self.sources[source_id]
        return source

    def update_source(self, source_id, payload):
        self.sstorage.update(source_id, payload)

    def del_source(self, source_id):
        return self.sstorage.delete(source_id)


