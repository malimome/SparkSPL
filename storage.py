import json
import os


class Storage:
    pass


class FileStorage:
    CURDIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "static")

    def __init__(self, name):
        self.file = "%s/%s" % (FileStorage.CURDIR, name)
        self.items = {}

    def getall(self):
        try:
            with open(self.file, "r") as fp:
                self.items = json.load(fp)
        except:
            pass
        return self.items

    def get(self, id):
        return self.items[id]

    def add(self, id, content):
        self.items[id] = content
        self._put()
        return self.items

    def update(self, id, content):
        return self.add(id, content)

    def delete(self, id):
        del self.items[id]
        self._put()
        return self.items

    def _put(self):
        try:
            with open(self.file, "w") as fp:
                json.dump(self.items, fp)
        except:
            pass