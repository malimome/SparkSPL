from src.sparkcontroller.sparkcontroller import SparkControllerLivy
from src.sparser.parser import MQL
from src.sources import Source
import json


class Search:
    def __init__(self):
        self.meta = None

    @staticmethod
    def build_search_string(spksearch, meta):
        sr = Source()
        source_id = meta["source"]
        imports = meta["imports"]
        udfs = meta["udfs"]

        source = sr.get_source(source_id)["query"]
        search = spksearch

        search_template = """
{imports}
{udfs}

val df = {input}
val df1 = df{search}
df1.toJSON.collect().foreach(println)
"""
        search_str = search_template.format(imports=imports, udfs=udfs, input=source, search=search)
        #search = "%s\n%s\nval df=%s\ndf%s.%s" % (imports, udfs, source, spksearch, output)
        return search_str

    def process_search(self, spl_search):
        if not spl_search.startswith("source"):
            return ""
        mql = MQL()
        # TODO handle search language errors
        spksearch = mql.run(spl_search)
        meta = mql.meta

        # Prepare the search string and convert it into full search
        mysearch = Search.build_search_string(spksearch, meta)

        sc = SparkControllerLivy()
        r = sc.post_search(mysearch)

        result = sc.get_result(r)
        data = Search.prepare_output(result)
        context = {
            'search': spl_search,
            'result': result,
            'data': data,
        }
        return context

    @staticmethod
    def prepare_output(result):
        if 'output' not in result:
            raise Exception("No data!")
        output = result['output']
        if output['status'] != 'ok':
            raise Exception("%s" % output['evalue'] if 'evalue' in output else "Error in query")
        rdw = output['data']['text/plain']
        rdw = "[" + rdw.replace("\n", ",") + "]"
        data = json.loads(rdw)
        del output['data']
        #rdw = rdw[rdw.strip().find('\n') + 1:].strip()
        #data = csv.DictReader(StringIO(rdw))
        metadata = {"x": "ctx", "y1": "aval", "y2": "mxval"}
        return data