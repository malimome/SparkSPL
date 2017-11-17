import unittest
from sparkcontroller import sparkcontroller

class TestLivy(unittest.TestCase):

    def test_postjob(self):
        sc = sparkcontroller.SparkControllerLivy()
        ret = sc.post_search("""val textFile = sc.textFile("hdfs://127.0.0.1:9000/indexes/test/*/*.csv")
                    textFile.collect().foreach(println)""")
        print(ret)

if __name__ == '__main__':
    unittest.main()