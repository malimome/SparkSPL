from src.sparkcontroller.webreq import *
import time
from timeit import default_timer as timer
from pprint import pprint


headers = {'Content-Type': 'application/json'}
#URL = "http://sparkify.novelsec.com"
URL = "http://127.0.0.1:5000"
JOBS_URL = "{URL}/jobs".format(URL=URL)


def nice_print(func):
   def func_wrapper(*args, **kwargs):
       s = timer()
       ret = func(*args, **kwargs)
       e = timer() - s
       print("### start {func} total {time} ###".format(func=func, time=e))
       pprint(ret)
       print("### end {func} total {time} ###".format(func=func, time=e))
       return ret
   return func_wrapper


@nice_print
def get_jobs():
    r = get_req(JOBS_URL)
    return r.json()


@nice_print
def post_jobs(query):
    r = post_req(JOBS_URL, data=None, json=query, header=headers)
    return r.json()


def jobid_url(job):
    jobid = job["job_id"]
    return "{URL}/{jobid}".format(URL=JOBS_URL, jobid=jobid)


@nice_print
def get_jobid(job):
    url = jobid_url(job)
    data = {"mode": "normal"}
    try:
        r = get_req(url, param=data, header=headers)
    except Exception as ex:
        return str(ex)
    return r.json()


@nice_print
def get_jobid_block(job):
    url = jobid_url(job)
    data = {"mode": "blocking"}
    r = get_req(url, param=data, header=headers)
    return r.json()


@nice_print
def cancel_jobid(job):
    url = jobid_url(job)
    url += "?action=cancel"
    r = put_req(url, data=None, json=None, header=headers)
    return r.json()


@nice_print
def del_jobid(job):
    url = jobid_url(job)
    r = delete_req(url)
    return r


def post_job_get(q, cancel=False):
    #jobs = get_jobs()
    # ----
    query = {
      "query": q,
      "mode": "normal",
      "earliest": "now-d",
      "priority": "normal",
      "latest": "now"
    }
    job = post_jobs(query)
    # ------
    jstat = get_jobid(job)
    while jstat["status"] != "finished":
        if cancel:
            r = cancel_jobid(job)
        else:
            time.sleep(2)
        jstat = get_jobid(job)
        if cancel: break
    # ------
    ret = get_jobid_block(job)
    del_jobid(job)


if __name__ == '__main__':
    q= """source=filebeat 
| eval group = offset % 20, rn = rand()
| sort group desc, @timestamp desc
| window first(rn) as c, last(rn) as g over group orderby @timestamp rows -1 to 1
| rename c as c2, g as g2 | head 5
"""
    #q = "source=filebeat | head 3"
    post_job_get(q, cancel=False)
    #job = {"job_id": "472b4ab2-17a3-11e8-a3fa-c8f733a41618"}
    #jstat = get_jobid(job)
    #print(jstat["out"]["result"][0])






