from src.jobs import Jobs
from src.utils.threader import threaded


jb = Jobs.init()


@threaded
def run_parallel_search(query, earliest, latest):
    result = None
    job_post = {
        'query': query,
        'earliest': earliest,
        'latest': latest,
        'mode': 'normal',
        'priority': 'normal'
    }
    try:
        job_ = jb.add_job(job_post)
        jb.post_job(job_)
        job, result = jb.get_job(job_["job_id"])
    except:
        raise
    return result


def main():
    queries = [
        "source=filebeat",
        "source=filebeat | eval rn=rand() | stats sum(rn) as srn by offset",
        "source=filebeat | eval rn=if(rand()>0.5, 1, 0) | stats min(offset) as moff by rn"
    ]
    th = []
    ret = []
    for query in queries:
        t, r = run_parallel_search(query, "now-d", "now")
        th.append(t)
        ret.append(r)

    for i in range(len(th)):
        th[i].join()
        print(ret[i].val["query"], ":\n", ret[i].val["data"][0])


main()


