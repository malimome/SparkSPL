import unittest

from src.sparkcontroller import livy


class TestLivy(unittest.TestCase):

    def test_post_query(self):
        search = 'spark.read.format("csv").option("header", "true").option("mode", "DROPMALFORMED").csv("hdfs://127.0.0.1:9000/indexes/test/*/*.csv").select("ctx","val").groupBy("ctx").agg(max("val")).toJSON.collect()'
        sc = livy.Livy()
        sc.init_livy()
        ret = sc.post_query(search)
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