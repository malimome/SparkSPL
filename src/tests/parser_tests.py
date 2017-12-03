import unittest

from src.sparser.parser import MQL


class TestParser(unittest.TestCase):

    def test_postjob(self):
        searches = {
            'source=a': '',
            'source=a | table a1': '.select("a1")',
            'source=a | stats max(b) as c, sum(f) as g by d':
                '.groupBy("d").agg(max("b").alias("c"),sum("f").alias("g"))',
            'source=a | eval a5 = (r1)*(2.3+r2+if(1 - 1, if(10<1, 100+1, 8*1), 3))':
                '.withColumn("a5",($"r1")*(2.3+$"r2"+when(1-1, when(10 < 1, 100+1).otherwise(8*1)).otherwise(3)))',
            'source=a | eval a5 = "6trg", a6=5': '.withColumn("a5","6trg").withColumn("a6",5)',
            'source=a | eval a5 = rand()': '.withColumn("a5",rand())',
            'source=a | where a5 == "6trg"': '.filter($"a5" === "6trg")',
            'source=a | table a1 | eval a6=sin(a1)': '.select("a1").withColumn("a6",sin($"a1"))'
        }

        cl = MQL()
        for s in searches:
            a = searches[s]
            spsearch = cl.run(s)
            #print(s, ", ", spsearch)
            self.assertEqual('a', cl.meta["source"])
            self.assertEqual(a, spsearch)


if __name__ == '__main__':
    unittest.main()