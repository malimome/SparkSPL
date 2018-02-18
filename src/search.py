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
    def update_job(job, result):
        mapping = {
            "waiting": "queued",
            "running": "running",
            "available": "finished",
            "error": "error",
            "cancelling": "cancelling",
            "cancelled": "cancelled"
        }
        job['status'] = mapping[result['state']]
        job['progress'] = int(result['progress'] * 100)

    @staticmethod
    def get_search_result(job):
        r = job["internal_session"]
        result = Search.sc.get_result(r)
        Search.update_job(job, result)
        data = Search.prepare_output(result)
        return data

    @staticmethod
    def get_search_result_async(job):
        r = job["internal_session"]
        result = Search.sc.get_result_async(r)
        Search.update_job(job, result)
        if result["state"] == "available":
            Search.sc.cleanup(r)
            data = Search.prepare_output(result)
        else:
            data = None
        return data

    @staticmethod
    def cancel_job(job):
        r = job["internal_session"]
        result = Search.sc.cancel_search(r)
        return result

    @staticmethod
    def prepare_output(result):
        if 'output' not in result:
            raise Exception("No data!")
        output = result['output']
        if output['status'] != 'ok':
            raise Exception("%s" % output['evalue'] if 'evalue' in output else "Error in query")
        rdw = output['data']['text/plain']
        rdw = "[" + rdw.replace("\n", ",") + "]"
        #TODO is this efficient
        data = json.loads(rdw)
        del output['data']
        return data