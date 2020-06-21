import unittest

from src.jobs import Jobs


class TestJob(unittest.TestCase):

    def test_postjob(self):
        jm = Jobs().init()
        job_desc = {"query": "source=filebeat-*", "earliest": "-5d", "latest": "-2d", "mode": "", "priority": ""}
        job = jm.add_job(job_desc)
        jm.post_job(job)
        print(job)


if __name__ == '__main__':
    unittest.main()