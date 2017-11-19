import unittest

from src.jobs import Jobs


class TestJob(unittest.TestCase):

    def test_postjob(self):
        jm = Jobs()
        ctx = jm.post_job("index")
        print(ctx)

if __name__ == '__main__':
    unittest.main()