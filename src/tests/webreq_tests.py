from src.sparkcontroller import webreq as wr
import unittest


class TestWebReq(unittest.TestCase):

    def test_get(self):
        try:
            wr.get_req("http://10.10.10.10/test")
        except Exception as ex:
            print(ex)


if __name__ == '__main__':
    unittest.main()