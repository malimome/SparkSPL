import json
import time
import uuid

import src.storage as st
from src.search import Search


class Jobs:
    def __init__(self):
        self.jstorage = st.FileStorage("jobs.conf")
        self.jobs = self.jstorage.getall()
        self.sch = Search()

    def get_jobs(self):
        return self.jobs

    def post_job(self, job):
        self.sch.process_search(job)
        # some stuff added to job
        job["status"] = "started"
        self.jobs = self.jstorage.update(job["job_id"], job)
        return 0

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
            "job_id": job_id
        }
        self.jobs = self.jstorage.add(job_id, job)
        return job

    def get_job(self, job_id):
        job = self.jobs[job_id]
        result = self.sch.get_search_result(job)
        job["status"] = "finished"
        job["progress"] = 100
        self.jstorage.update(job_id, job)
        return job, result

    def get_job_async(self, job_id):
        job = self.jobs[job_id]
        result = self.sch.get_search_result_async(job)
        #if result["state"] == "available":
        #    job["progress"] = 100
        #else:
        #    job["progress"] = min(99, job["progress"] + 10)
        self.jstorage.update(job_id, job)
        return job, result

    def stop_job(self, job_id):
        pass

    def del_job(self, job_id):
        self.jobs = self.jstorage.delete(job_id)
        return 0


