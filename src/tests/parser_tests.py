import unittest

from src.sparser.parser import MQL


class TestParser(unittest.TestCase):

    def test_postjob(self):
        searches = {
            'source=a': '',
            'source=a | table a1': '.select("a1")',
            'source=a | stats max(b) as c, sum(f) as g by d': '.groupBy("d").agg(max("b").alias("c"),sum("f").alias("g"))',
            'source=a | eval a5 = (r1)*(2.3+r2+if(1, if(10<1, 100+1, 8), 3))': '.withColumn("a5",(col("r1"))*(2.3+col("r2")+100+1))',
            'source=a | eval a5 = "6trg"': '.withColumn("a5","6trg")',
            'source=a | where a5 == "6trg"': '.filter(col("a5") == "6trg")',
        }

        cl = MQL()
        for s in searches:
            a = searches[s]
            spsearch = cl.run(s)
            #print(spsearch)
            self.assertEqual('a', cl.meta["source"])
            self.assertEqual(a, spsearch)


if __name__ == '__main__':
    unittest.main()