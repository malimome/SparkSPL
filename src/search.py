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
    def search_loop(min_idle):
        Search.sc.manage_livy_session(min_idle)

    @staticmethod
    def process_search(job):
        spl_search = job["query"]
        earliest, latest = job["earliest"], job["latest"]
        spark_query = transform_search(spl_search, earliest, latest)
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
    def get_search_result(job, mode):
        r = job["internal_session"]
        data = None
        types = None
        if mode != "blocking":
            result = Search.sc.get_result_async(r)
            if result["state"] == "available":
                Search.sc.cleanup(r)
                data, types = Search.prepare_output(result)
        else:
            result = Search.sc.get_result(r)
            data, types = Search.prepare_output(result)
        Search.update_job(job, result)
        return data, types

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
        rdw = "[" + output['data']['text/plain'].replace("\n", ",") + "]"
        resp = json.loads(rdw)
        types = resp[0] if len(resp) > 0 else None
        data = resp[1:] if len(resp) > 1 else None
        del output['data']
        return data, types
