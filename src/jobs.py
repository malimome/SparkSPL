import logging
import threading
import time
import uuid

import settings
import src.storage as st
from src.search import Search
from src.sparkcontroller.webreq import UpstreamError
from src.utils import validation as v
from src.utils.validation import NotFoundError

log = logging.getLogger(__name__)

PRIORITIES = ("normal", "low", "high")
MODES = ("normal", "blocking")


class Jobs:
    """Search job registry, persisted in jobs.conf; results are cached under jout/."""

    def __init__(self):
        self.jstorage = None
        self.sch = None
        self.lock = threading.RLock()

    def init(self):
        if self.jstorage is None:
            self.jstorage = st.JINIStorage("jobs.conf")
            self.get_alljobs()
            self.sch = Search().init()
        return self

    @property
    def jobs(self):
        return self.jstorage.items

    def get_alljobs(self):
        with self.lock:
            jobs = self.jstorage.getall()
            now = int(time.time())
            for job_id in list(jobs.keys()):
                if int(jobs[job_id].get("expiry_time", now + 1)) < now:
                    self._remove(job_id)
            return self.jstorage.items

    def get_jobs(self):
        return dict(self.get_alljobs())

    def _remove(self, job_id):
        st.FileStorage("jout/%s" % v.uuid_str(job_id)).hard_delete_file()
        self.jstorage.delete(job_id)

    @staticmethod
    def _int(job, key):
        try:
            return int(job.get(key, 0))
        except (TypeError, ValueError):
            return 0

    def add_job(self, job_post):
        mode = job_post.get("mode") or "normal"
        priority = job_post.get("priority") or "normal"
        if mode not in MODES or priority not in PRIORITIES:
            raise v.ValidationError("Invalid mode or priority")
        submit_time = int(time.time())
        job = {
            "query": v.query(job_post.get("query")),
            "earliest": v.time_expr(job_post.get("earliest") or "now-1d", "earliest"),
            "latest": v.time_expr(job_post.get("latest") or "now", "latest"),
            "mode": mode,
            "priority": priority,
            "submit_time": submit_time,
            "expiry_time": submit_time + settings.JOB_TTL_SECONDS,
            "status": "queued",
            "progress": 0,
            "job_id": str(uuid.uuid4()),
        }
        with self.lock:
            self.jstorage.getall()
            self.jstorage.add(job["job_id"], job)
        return job

    def post_job(self, job):
        try:
            self.sch.process_search(job)
        except (UpstreamError, v.ValidationError):
            self.delete_quietly(job["job_id"])
            raise
        except Exception as ex:
            # Anything else raised here comes from translating the query, i.e. user input.
            self.delete_quietly(job["job_id"])
            raise v.ValidationError(str(ex))
        job["status"] = "started"
        with self.lock:
            self.jstorage.update(job["job_id"], job)
        return 0

    def delete_quietly(self, job_id):
        try:
            self.del_job(job_id)
        except Exception:
            log.exception("Could not clean up job %s", job_id)

    def post_test_job(self):
        """Debug-only: replay one of the canned jobs flagged testing=y."""
        if not settings.FLASK_DEBUG:
            raise v.ValidationError("Test jobs are disabled")
        import random
        with self.lock:
            test_jobs = [j for j in self.jstorage.getall().values() if j.get("testing") == "y"]
            if not test_jobs:
                raise NotFoundError("No test jobs available")
            tjob = dict(random.choice(test_jobs))
            tjob["status"] = "started"
            tjob["progress"] = 0
            self.jstorage.update(tjob["job_id"], tjob)
        return tjob

    def _get_job(self, job_id):
        job_id = v.uuid_str(job_id, "job id")
        with self.lock:
            jobs = self.jstorage.getall()
            if job_id not in jobs:
                raise NotFoundError("Job %s does not exist" % job_id)
            return jobs[job_id]

    def _save_job(self, job, result, types):
        with self.lock:
            self.jstorage.update(job["job_id"], job)
        if job["status"] == "finished":
            jfs = st.FileStorage("jout/%s" % job["job_id"])
            jfs.update("types", types)
            jfs.update("out", result)

    def get_test_job(self, job):
        if settings.FLASK_DEBUG and job.get("testing") == "y":
            if self._int(job, "progress") == 0:
                job["progress"] = 50
                job["status"] = "running"
            else:
                job["progress"] = 100
                job["status"] = "finished"
            with self.lock:
                self.jstorage.update(job["job_id"], job)
            return True
        return False

    def _load_result(self, job):
        if job["status"] != "finished":
            return None, None
        jfs = st.FileStorage("jout/%s" % job["job_id"])
        stored = jfs.getall()
        return stored.get("out"), stored.get("types")

    def get_job(self, job_id, mode="normal", offset=0, count=100000):
        job = dict(self._get_job(job_id))
        if job["status"] in ("cancelled", "error"):
            return job
        test = self.get_test_job(job)
        if "internal_session" not in job and not test:
            return self.build_result_response(job, None, None, offset, count)
        result, types = self._load_result(job)
        if result is None and not test:
            result, types = self.sch.get_search_result(job, mode)
            self._save_job(job, result, types)
        return self.build_result_response(job, result, types, offset, count)

    def build_result_response(self, job, result, types, offset, count):
        jobres = dict(job)
        if job["status"] == "finished":
            jobres["result"] = result[offset:offset + count] if result is not None else []
            jobres["end_time"] = int(time.time())
            jobres["result_summary"] = {
                "total_count": len(result) if result is not None else 0,
                "return_count": len(jobres["result"]),
                "return_offset": offset,
                "fields": types,
            }
            jobres["visualization"] = {}
        else:
            jobres["result"] = None
        return jobres

    def stop_job(self, job_id):
        job = dict(self._get_job(job_id))
        if job.get("testing") == "y" and settings.FLASK_DEBUG:
            job["status"] = "cancelled"
            return job
        if job["status"] == "cancelled":
            return job
        result = self.sch.cancel_job(job)
        if result.get('msg') != "canceled":
            raise RuntimeError("Job cancellation failed.")
        job["status"] = "cancelled"
        with self.lock:
            self.jstorage.update(job["job_id"], job)
        return job

    def cancel_and_delete(self, job_id):
        job = self._get_job(job_id)
        if job["status"] in ("queued", "started", "running"):
            self.stop_job(job_id)
        self.del_job(job_id)

    def del_job(self, job_id):
        job = self._get_job(job_id)
        if job.get("testing") == "y":
            return 0
        with self.lock:
            self._remove(job["job_id"])
        return 0
