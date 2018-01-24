import json
import os


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
        self._put()
        return self.items

    def update(self, id, content):
        return self.add(id, content)

    def delete(self, id):
        del self.items[id]
        self._put()
        return self.items

    def _put(self):
        pass


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

    def _put(self):
        try:
            with open(self.file, "w") as fp:
                json.dump(self.items, fp, indent=2, sort_keys=True)
        except:
            pass

"""
import ConfigParser
import io
class INIStorage(Storage):
    def __init__(self, name):
        super(INIStorage, self).__init__(name)

    def getall(self):
        with open(self.file) as f:
            sample_config = f.read()
        config = ConfigParser.RawConfigParser(allow_no_value=True)
        config.readfp(io.BytesIO(sample_config))

        # List all contents
        print("List all contents")
        for section in config.sections():
            print("Section: %s" % section)
            for options in config.options(section):
                print("x %s:::%s:::%s" % (options,
                                          config.get(section, options),
                                          str(type(options))))

        # Print some contents
        print("\nPrint some contents")
        print(config.get('other', 'use_anonymous'))  # Just get the value
        print(config.getboolean('other', 'use_anonymous'))  # You know the datatype?

    def _put(self):
        cfgfile = open(self.file, 'w')

        # Add content to the file
        Config = ConfigParser.ConfigParser()
        Config.add_section('mysql')
        Config.set('mysql', 'host', 'localhost')
        Config.set('mysql', 'user', 'root')
        Config.set('mysql', 'passwd', 'my secret password')
        Config.set('mysql', 'db', 'write-math')
        Config.add_section('other')
        Config.set('other',
                   'preprocessing_queue',
                   ['preprocessing.scale_and_center',
                    'preprocessing.dot_reduction',
                    'preprocessing.connect_lines'])
        Config.set('other', 'use_anonymous', True)
        Config.write(cfgfile)
        cfgfile.close()
        

import yaml       
class YMLStorage(Storage):
    def __init__(self, name):
        super(INIStorage, self).__init__(name)
        

    def get_all(self):
        with open("config.yml", 'r') as ymlfile:
            cfg = yaml.load(ymlfile)
"""
