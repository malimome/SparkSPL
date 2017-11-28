from src.sparkcontroller.sparkcontroller import SparkControllerLivy
from src.sparser.parser import MQL
from src.sources import Source
import json


class Search:
    def __init__(self):
        self.meta = None

    def process_search(self, search):
        if not search.startswith("source"):
            return ""
        mql = MQL()
        sr = Source()

        spsearch = mql.run(search)
        source_id = mql.meta["source"]
        imports = mql.meta["imports"]
        source = sr.get_source(source_id)["query"]
        # 'spark.read.format("csv").option("header", "true").option("mode", "DROPMALFORMED").csv("hdfs://127.0.0.1:9000/indexes/test/*/*.csv")'
        output = 'toJSON.collect().foreach(println)'
        sc = SparkControllerLivy()
        search = "%s\n%s%s.%s" % (imports, source, spsearch, output)
        result = sc.post_search(search)
        rdw = result['output']['data']['text/plain']
        rdw = "[" + rdw.replace("\n", ",") + "]"
        data = json.loads(rdw)
        #rdw = rdw[rdw.strip().find('\n') + 1:].strip()
        #data = csv.DictReader(StringIO(rdw))
        metadata = {"x": "ctx", "y1": "aval", "y2": "mxval"}
        context = {
            'search': search,
            'result': result,
            'data': data,
        }
        return context
