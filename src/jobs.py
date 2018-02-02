import json
import time
import uuid

import src.storage as st
from src.search import Search


class Jobs:
    jstorage = None
    jobs = None
    sch = None

    @staticmethod
    def init():
        if Jobs.jstorage is None:
            Jobs.jstorage = st.FileStorage("jobs.conf")
            Jobs.jobs = Jobs.jstorage.getall()
            Jobs.sch = Search().init()
        return Jobs

    @staticmethod
    def get_jobs():
        return Jobs.jobs

    @staticmethod
    def post_job(job):
        Jobs.sch.process_search(job)
        # some stuff added to job
        job["status"] = "started"
        Jobs.jobs = Jobs.jstorage.update(job["job_id"], job)
        return 0

    @staticmethod
    def add_job(job_post):
        job_id = str(uuid.uuid1())
        submit_time = int(time.time())
        expiry_time = submit_time + 600
        job = {
            "query": job_post['query'],
            "earliest": job_post['earliest'],
            "latest": job_post['latest'],
            "mode": job_post['mode'],
            "priority": job_post['priority'],
            "submit_time": submit_time,
            "expiry_time": expiry_time,
            "status": "queued",
            "progress": 0,
            "job_id": job_id
        }
        Jobs.jobs = Jobs.jstorage.add(job_id, job)
        return job

    @staticmethod
    def get_job(job_id):
        job = Jobs.jobs[job_id]
        result = Jobs.sch.get_search_result(job)
        job["status"] = "finished"
        job["progress"] = 100
        Jobs.jstorage.update(job_id, job)
        return job, result

    @staticmethod
    def get_job_async(job_id):
        job = Jobs.jobs[job_id]
        result = Jobs.sch.get_search_result_async(job)
        #if result["state"] == "available":
        #    job["progress"] = 100
        #else:
        #    job["progress"] = min(99, job["progress"] + 10)
        Jobs.jstorage.update(job_id, job)
        return job, result

    @staticmethod
    def stop_job(job_id):
        pass

    @staticmethod
    def del_job(job_id):
        Jobs.jobs = Jobs.jstorage.delete(job_id)
        return 0


