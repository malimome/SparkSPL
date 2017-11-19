import unittest

from src.job_mgm import JobMgm


class TestJob(unittest.TestCase):

    def test_postjob(self):
        jm = JobMgm()
        jm.post_job("index")

if __name__ == '__main__':
    unittest.main()