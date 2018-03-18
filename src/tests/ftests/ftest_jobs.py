from src.jobs import Jobs
from pprint import pprint
import time


def build_job(qind = 0, earliest='now-d', latest='now'):
    queries = [
        """
source=filebeat("t")
| eval group = offset % 5, rn = rand()
| sort group desc, @timestamp desc
| head 15
| stats count as c, values(@timestamp) as vt by group
"""
    ]
    a = """
    | window first(rn) as c, last(rn) as g over group orderby @timestamp rows -1 to 1
    | rename c as c2, g as g2
            """
    job_post = {
        'query': queries[qind],
        'earliest': earliest,
        'latest': latest,
        'priority': 'normal',
        'mode': 'normal'
    }
    return job_post


def nice_print(obj, message):
    print("############ Start {msg} #############".format(msg=message))
    pprint(obj)
    print("############ End   {msg} #############".format(msg=message))


def test_get_post_job():
    jb = Jobs().init()
    # ------- Get Jobs
    jobs = jb.get_jobs()
    nice_print(jobs, "All Jobs")
    # ------- Post Job
    job_post = build_job()
    job_ = jb.add_job(job_post)
    nice_print(job_, "added job")
    jb.post_job(job_)
    job = job_
    nice_print(job, "posted job")
    job_id = job['job_id']
    # ------- Check job status async
    i = 0
    while job["status"] != "finished":
        final = jb.get_job(job_id)
        nice_print(job, "job async %d" % i)
        i += 1
        if job["status"] != "finished":
            time.sleep(2)

    nice_print(final, "job full")
    print("RESULTS: %d" % final["result_summary"]["count"])
    # ------- Get job result again blocking
    #job, result = jb.get_job(job_id)
    #nice_print(job, "job blocking")
    #print("RESULTS: %d" % len(result))
    #jres = jb.build_result_response(job, result)
    # ------- Delete job
    ret = jb.del_job(job_id)
    nice_print(ret, "delete job")


def test_post_job_cancel():
    jb = Jobs().init()
    # ------- Post Job
    job_post = build_job(qind=0, earliest='now-15d', latest='now')
    job = jb.add_job(job_post)
    jb.post_job(job)
    nice_print(job, "job post")
    job_id = job['job_id']
    # ------- Check job status async
    job, result = jb.get_job_async(job_id)
    jres = jb.build_result_response(job, result)
    nice_print(jres, "job async")
    # ------- cancel job
    ret = jb.stop_job(job_id)
    nice_print(ret, "job stop")

    # ------- Check job status async once
    job, result = jb.get_job_async(job_id)
    jres = jb.build_result_response(job, result)
    nice_print(jres, "job async again")
    # ------- Delete job
    ret = jb.del_job(job_id)
    nice_print(ret, "job del")

if __name__ == '__main__':
    test_get_post_job()
    #test_post_job_cancel()