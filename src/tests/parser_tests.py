import unittest

from src.sparser.parser import MQL


class TestParser(unittest.TestCase):

    def test_postjob(self):
        searches = {
            'source=a("t")':
                '',
            'source=a("t") | table a1':
                '.select("a1")',
            'source=a("t") | stats max(b) as c, sum(f) as g by d':
                '.groupBy("d").agg(max("b").alias("c"),sum("f").alias("g"))',
            'source=a("t") | eval a5 = (r1)*(2.3+r2+if(1 - 1, if(10<1, 100+1, 8*1), 3))':
                '.withColumn("a5",($"r1")*(lit(2.3)+$"r2"+when(lit(1)-lit(1), when(lit(10) < lit(1), lit(100)+lit(1)).otherwise(lit(8)*lit(1))).otherwise(lit(3))))',
            'source=a("t") | eval a5 = "6trg", a6=5':
                '.withColumn("a5",lit("6trg")).withColumn("a6",lit(5))',
            'source=a("t") | eval a5 = rand()':
                '.withColumn("a5",rand())',
            'source=a("t") | where a5 == "6trg"':
                '.filter($"a5" === lit("6trg"))',
            'source=a("t") | table a1 | eval a6=sin(a1)':
                '.select("a1").withColumn("a6",sin($"a1"))',
            'source=a("t") | eval a5=rand() | cache b2 | eval a1=rand()': 'val b2 = df.withColumn("a5",rand())\nval df_out = b2.withColumn("a1",rand())\n',
            'source=a("t") | rename a1 as a2, b1 as b2':
                '.withColumnRename(%s, %s).withColumnRename(b1, b2)',
            'source=a("t") | eval a=rand(), b=rand() | stats count, max(a) as a by b':
                '.withColumn("a",rand()).withColumn("b",rand()).groupBy("b").agg(count(),max("a").alias("a"))'
        }
        #searches = {
        #    'source=a("t") | rename a1 as a2, b1 as b2': '.withColumnRename(%s, %s).withColumnRename(b1, b2)',
        #}

        cl = MQL()
        for s in searches:
            a = searches[s]
            spsearch = cl.run(s)
            #print(s, ", ", spsearch)
            self.assertEqual('a', cl.meta["source"])
            self.assertEqual('"t"', cl.meta["src_param"])
            self.assertEqual(a, spsearch)


if __name__ == '__main__':
    unittest.main()