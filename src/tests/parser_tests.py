import unittest

from src.sparser.parser import MQL


class TestParser(unittest.TestCase):

    def test_postjob(self):
        search = """index 
            | table a1
            | stats max(b) by d """
            #| eval a5 = ((r1))*(2.3+(r2)+if(1, if(10<1, 100+1, 8), 3)) """

        source = 'val df = spark.read.format("csv").option("header", "true").option("mode", "DROPMALFORMED").csv("hdfs://127.0.0.1:9000/indexes/test/*/*.csv")'
        output = 'toJSON.collect().foreach(println)'

        cl = MQL()
        spsearch = cl.run(search)
        ret = "%s\n%s.%s" % (source, spsearch, output)
        print(ret)

if __name__ == '__main__':
    unittest.main()