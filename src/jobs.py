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
            Jobs.jstorage = st.JINIStorage("jobs.conf")
            Jobs.jobs = Jobs.jstorage.getall()
            Jobs.sch = Search().init()
        return Jobs

    @staticmethod
    def job_loop():
        pass

    @staticmethod
    def get_jobs():
        return Jobs.jobs

    @staticmethod
    def post_job(job):
        Jobs.sch.process_search(job)
        job["status"] = "started"
        Jobs.jobs[job["job_id"]] = job
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
    def get_test_job():
        import random
        test_jobs = []
        for job_id in Jobs.jobs:
            job = Jobs.jobs[job_id]
            if "testing" in job and job["testing"] == "y":
                test_jobs.append(job)
        tjob = dict(random.choice(test_jobs))
        tjob["status"] = "started"
        tjob["progress"] = 0
        return tjob

    @staticmethod
    def _get_job(job_id):
        Jobs.jobs = Jobs.jstorage.getall()
        if job_id in Jobs.jobs:
            return Jobs.jobs[job_id]
        else:
            raise Exception("Job %s does not exist" % job_id)

    @staticmethod
    def _check_job_dump(job, result, types):
        if job["status"] != "finished":
            Jobs.jobs[job["job_id"]] = job
            return None
        Jobs.jobs = Jobs.jstorage.update(job["job_id"], job)
        jfs = st.FileStorage("jout/%s" % job["job_id"])
        jfs.update("types", types)
        jfs.update("out", result)

    @staticmethod
    def _check_job_load(job):
        if job["status"] != "finished":
            return None, None
        jfs = st.FileStorage("jout/%s" % job["job_id"])
        all = jfs.getall()
        return all["out"], all["types"]

    @staticmethod
    def get_job(job_id, mode="normal", offset=0, count=100000):
        job = Jobs._get_job(job_id)
        if job["status"] == "cancelled":
            return job
        result, types = Jobs._check_job_load(job)
        if result is None:
            result, types = Jobs.sch.get_search_result(job, mode)
            Jobs._check_job_dump(job, result, types)
        final = Jobs.build_result_response(job, result, types, offset, count)
        return final

    @staticmethod
    def build_result_response(job, result, types, offset, count):
        jobres = dict(job)
        if job["status"] == "finished":
            jobres["result"] = result[offset:offset+count]
            jobres["end_time"] = int(time.time())
            jobres["result_summary"] = {
                "total_count": len(result),
                "return_count": len(jobres["result"]),
                "return_offset": offset,
                "fields": types,
            }
            jobres["visualization"] = {
            }
        else:
            jobres["result"] = None
        return jobres

    @staticmethod
    def stop_job(job_id):
        job = Jobs._get_job(job_id)
        if "testing" in job and job["testing"] == "y":
            tjob = dict(job)
            tjob["status"] = "cancelled"
            return tjob
        if job["status"] == "cancelled":
            return job
        result = Jobs.sch.cancel_job(job)
        if 'msg' not in result or result['msg'] != "canceled":
            raise Exception("Job cancellation failed.")
        else:
            job['status'] = 'cancelled'
        job["status"] = "cancelled"
        Jobs.jobs = Jobs.jstorage.update(job_id, job)
        return job

    @staticmethod
    def del_job(job_id):
        job = Jobs._get_job(job_id)
        if "testing" in job and job["testing"] == "y":
            return 0
        jfs = st.FileStorage("jout/%s" % job_id)
        jfs.hard_delete_file()
        Jobs.jobs = Jobs.jstorage.delete(job_id)
        return 0


