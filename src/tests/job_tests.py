import unittest

from src.jobs import Jobs


class TestJob(unittest.TestCase):

    def test_postjob(self):
        jm = Jobs()
        job = jm.add_job("index", "-1d", "now")
        jm.post_job(job)
        print(job)

if __name__ == '__main__':
    unittest.main()