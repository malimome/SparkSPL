from src.sparkcontroller.sparkcontroller import SparkControllerLivy
from src.sparser.search_trans import transform_search
import json


class Search:
    sc = None

    @staticmethod
    def init():
        if Search.sc is None:
            Search.sc = SparkControllerLivy().init()
        return Search

    @staticmethod
    def process_search(job):
        spl_search = job["query"]
        spark_query = transform_search(spl_search)
        r = Search.sc.post_search(spark_query)
        job["internal_session"] = r
        return 0

    @staticmethod
    def get_search_result(job):
        r = job["internal_session"]
        result = Search.sc.get_result(r)
        data = Search.prepare_output(result)
        context = {
            'query': job["query"],
            'result': result,
            'data': data,
        }
        return context

    @staticmethod
    def get_search_result_async(job):
        r = job["internal_session"]
        result = Search.sc.get_result_async(r)
        context = {
            'search': job["search"],
            'result': result
        }
        if result["state"] == "available":
            Search.sc.cleanup(r)
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