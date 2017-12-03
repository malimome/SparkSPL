import json
import time
import uuid

import src.storage as st
from src.search import Search


class Jobs:
    def __init__(self):
        self.jstorage = st.FileStorage("jobs.conf")
        self.jobs = self.jstorage.getall()

    def get_jobs(self):
        return self.jobs

    def post_job(self, search):
        sch = Search()
        context = sch.process_search(search)
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
            "data": None #TODO
        }

    def stop_job(self, job_id):
        pass

    def del_job(self, job_id):
        return self.jstorage.delete(job_id)


