from src.sparkcontroller.sparkcontroller import SparkControllerLivy
from src.sparser.parser import MQL
from src.sources import Source
import json


class Search:
    source_inits = {
        "elastic": "spark.read.format(\"org.elasticsearch.spark.sql\")"
                   ".option(\"es.nodes\", \"localhost\").option(\"es.port\", \"9200\")"
                   ".option(\"es.field.read.empty.as.null\",\"true\")"
                   ".option(\"es.index.read.missing.as.empty\",\"true\")"
                   ".option(\"es.mapping.include\", \"beat.*, prospector.*, tags.*\")"
                   ".option(\"es.read.field.exclude\", \"prospector,beat,tags\")"
    }

    def __init__(self):
        self.meta = None
        self.sc = SparkControllerLivy()

    @staticmethod
    def build_search_string(job, query_param): #spksearch, meta, start, end):
        meta = query_param["meta"]
        sr = Source()
        source_id = meta["source"]
        imports = meta["imports"]
        udfs = meta["udfs"]

        source = sr.get_source(source_id)
        source_query = ""
        if source["type"] == "elastic":
            source_query = Search.source_inits[source["type"]]
            source_query += ".option(\"es.query\",\"\"\"{\"query\": {\"match_all\":{}},"
            source_query += "\"filter\": {\"range\":{\"@timestamp\": {\"gte\":\"%s\", \"lt\":\"%s\"}}}}\"\"\")" \
                            % (job["start"], job["end"])
            source_query += ".load(\"{index}-*\").sort(desc(\"@timestamp\"))".format(index=source_id)

        search_template = """
{imports}
{udfs}

val df = {input}
val df1 = df{search}
df1.toJSON.collect().foreach(println)
"""
        search_str = search_template.format(imports=imports, udfs=udfs, input=source_query, search=query_param["spark_query"])
        return search_str

    def process_search(self, job):
        spl_search = job["search"]
        if not spl_search.startswith("source"):
            return ""
        mql = MQL()
        # TODO handle search language errors
        spark_query = mql.run(spl_search)
        meta = mql.meta
        query_param = {
            "spark_query": spark_query,
            "meta": meta
        }

        # Prepare the search string and convert it into full search
        end_query = Search.build_search_string(job, query_param)
        query_param["end_query"] = end_query

        r = self.sc.post_search(end_query)
        job["internal_session"] = r
        return 0

    def get_search_result(self, job):
        r = job["internal_session"]
        result = self.sc.get_result(r)
        data = Search.prepare_output(result)
        context = {
            'search': job["search"],
            'result': result,
            'data': data,
        }
        return context

    def get_search_result_async(self, job):
        r = job["internal_session"]
        result = self.sc.get_result_async(r)
        context = {
            'search': job["search"],
            'result': result
        }
        if result["state"] == "available":
            self.sc.cleanup()
            data = Search.prepare_output(result)
            context['data'] = data
        else:
            context['data'] = {}
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