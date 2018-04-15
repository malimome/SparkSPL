import json
import os
import configparser


class Storage(object):
    CURDIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../static")

    def __init__(self, name):
        self.file = "%s/%s" % (Storage.CURDIR, name)
        self.items = {}

    def getall(self):
        pass

    def get(self, id):
        return self.items[id]

    def add(self, id, content):
        self.items[id] = content
        self._put(self.items)
        return self.items

    def update(self, id, content):
        return self.add(id, content)

    def delete(self, id):
        if id in self.items:
            del self.items[id]
        else:
            raise Exception("Item %d does not exists" % id)
        self._put(self.items)
        return self.items

    def _put(self, items):
        raise NotImplemented

    def hard_delete_file(self):
        try:
            os.remove(self.file)
            return True
        except:
            return False


class FileStorage(Storage):
    def __init__(self, name):
        super(FileStorage, self).__init__(name)

    def getall(self):
        try:
            with open(self.file, "r") as fp:
                self.items = json.load(fp)
        except ValueError as ex:
            print("Warning: reading empty config! %s" % self.file)
            return self.items
        except FileNotFoundError as ex:
            print("Warning: no config file found! %s" % self.file)
            return self.items
        return self.items

    def _put(self, items):
        try:
            with open(self.file, "w") as fp:
                json.dump(items, fp, indent=2, sort_keys=True)
        except:
            raise Exception("Error writing config file %s" % self.file)


class INIStorage(Storage):
    def __init__(self, name):
        super(INIStorage, self).__init__(name)

    def getall(self):
        config = configparser.RawConfigParser(allow_no_value=True)
        config.read(self.file)

        for section in config.sections():
            self.items[section] = {}
            for options in config.options(section):
                self.items[section][options] = config.get(section, options)
        return self.items

    def _put(self, items):
        config = configparser.ConfigParser()
        config.read_dict(items)
        try:
            with open(self.file, 'w') as configfile:
                config.write(configfile)
        except Exception as ex:
            raise Exception("Error in writing config file %s: %s" % (self.file, str(ex)))


class JINIStorage(INIStorage):
    def __init__(self, name):
        super(JINIStorage, self).__init__(name)

    def getall(self):
        entries = super(JINIStorage, self).getall()
        for e in entries:
            v = entries[e]
            v["query"] = v["query"].replace('%%', '%')
            if "sid" in v:
                v["internal_session"] = {
                    "sid": v["sid"],
                    "tid": v["tid"]
                }
                del v["sid"]
                del v["tid"]
        return entries

    def _put(self, items):
        entries = {}
        for i in items:
            c = dict(items[i])
            c["query"] = c["query"].replace('%', '%%')
            if "internal_session" in c:
                c["sid"] = c["internal_session"]["sid"]
                c["tid"] = c["internal_session"]["tid"]
            entries[i] = c
        super(JINIStorage, self)._put(entries)
