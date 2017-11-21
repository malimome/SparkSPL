import unittest

from src.sparkcontroller import livy


class TestLivy(unittest.TestCase):

    def test_post_query(self):
        sc = livy.Livy()
        sc.init_livy()
        ret = sc.post_query()
        r = sc.get_result(ret)
        print(r)

    def test_initlivy(self):
        return
        sc = livy.Livy()
        #sc.create_session()
        ret = sc.init_livy()
        print(ret)

if __name__ == '__main__':
    unittest.main()