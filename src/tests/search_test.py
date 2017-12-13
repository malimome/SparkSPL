import unittest
from src import search


class TestLivy(unittest.TestCase):

    def test_post_query(self):
        sc = search.Search()
        ctx = sc.process_search("source=range1000")
        print(ctx)


if __name__ == '__main__':
    unittest.main()