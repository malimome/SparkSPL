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
            error_msg = "Error: %s\n" % output['evalue'] if 'evalue' in output else "Error in query"
            error_msg += "Trace: %s" % "".join(output['traceback']) if 'traceback' in output else "No Trace!"
            raise Exception(error_msg)
        raw_result = output['data']['text/plain']
        # remove the last instance of vartypes!
        ind = raw_result.rfind("vartypes0001: String =")
        raw_result = raw_result[ind:].strip('\n')
        # remove the first line which is still vartypes!
        raw_result = raw_result[raw_result.find("\n") + 1:]
        # separate the first line as type and the rest as data
        data_ind = raw_result.find("\n")
        # types is a dict of types
        types = raw_result[:data_ind]
        # data is a list of dicts for each result
        raw_array = raw_result[data_ind + 1:].split("\n")
        # TODO validation?
        rdw = "[" + ", ".join(raw_array) + "]"
        #data = rdw
        # TODO skip json send string
        data = json.loads(rdw)
        #types = resp[0] if len(resp) > 0 else None
        #data = resp[1:] if len(resp) > 1 else None
        del output['data']
        return data, types
