import json
import time
import uuid

import src.storage as st

from src.sample_data import gen_data
from src.sparkcontroller.sparkcontroller import SparkControllerLivy
from src.sparser.parser import MQL


class Jobs:
    def __init__(self):
        self.jstorage = st.FileStorage("jobs.conf")
        self.jobs = self.jstorage.getall()

    def get_jobs(self):
        return self.jobs

    def post_job(self, search):
        if not search.startswith("index"):
            return ""
        mql = MQL()
        spsearch = mql.run(search)
        source = 'val df = spark.read.format("csv").option("header", "true").option("mode", "DROPMALFORMED").csv("hdfs://127.0.0.1:9000/indexes/test/*/*.csv")'
        output = 'toJSON.collect().foreach(println)'
        #sc = SparkController()
        sc = SparkControllerLivy()
        result = sc.post_search("%s\n%s.%s" % (source, spsearch, output))
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

    def add_job(self, search, start, end):
        job_id = str(uuid.uuid1())
        submit_time = int(time.time())
        expiry_time = submit_time + 600
        job = {
            "search": search,
            "start": start,
            "end": end,
            "submit_time": submit_time,
            "expiry_time": expiry_time,
            "status": "queued",
            "progress": 0,
            "log": "Queued the job!",
            "result": {}
        }
        self.jobs = self.jstorage.add(job_id, job)
        return {
            "job_id": job_id,
            "job": job
        }

    def get_job(self, job_id):
        job = self.jobs[job_id]
        if job["status"] == "queued":
            job["status"] = "started"
        else:
            job["status"] = "finished"
            job["progress"] = 100
        self.jstorage.update(job_id, job)
        return job

    def get_job_result(self, job_id):
        return {
            "errors": None,
            "data": gen_data(100)
        }

    def stop_job(self, job_id):
        pass

    def del_job(self, job_id):
        return self.jstorage.delete(job_id)


