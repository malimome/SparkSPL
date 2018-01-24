import unittest
from src import search


class TestLivy(unittest.TestCase):

    def test_post_query(self):
        sc = search.Search()
        job = {
            "search": "source=filebeat",
            "start": "-1d",
            "end": "now"
        }
        ctx = sc.process_search(job)
        print(ctx)


if __name__ == '__main__':
    unittest.main()