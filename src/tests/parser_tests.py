import unittest

from src.sparser.parser import MQL
from src.sparser.search_trans import transform_search


class TestParser(unittest.TestCase):

    def test_postjob(self):
        searches = {
            'source=filebeat("t")':
                'spark.read.format("org.elasticsearch.spark.sql").option("es.nodes", "localhost").option("es.port", "9200").option("es.read.field.empty.as.null","true").option("es.index.read.missing.as.empty","true").option("es.mapping.include", "beat.*, prospector.*, tags.*").option("es.read.field.exclude", "prospector,beat,tags").option("es.query","""{"query": {"match_all":{}},"filter": {"range":{"@timestamp": {"gte":"now-d", "lt":"now"}}}}""").load("filebeat-*").sort(desc("@timestamp"))',
            'table a1':
                'select("a1")',
            'stats max(b) as c, sum(f) as g by d':
                'groupBy("d").agg(max("b").alias("c"),sum("f").alias("g"))',
            'eval a5 = (r1)*(2.3+r2+if(1 - 1, if(10<1, 100+1, 8*1), 3))':
                'withColumn("a5",($"r1")*(lit(2.3)+$"r2"+when(lit(1)-lit(1), when(lit(10) < lit(1), lit(100)+lit(1)).otherwise(lit(8)*lit(1))).otherwise(lit(3))))',
            'eval a5 = "6trg", a6=5':
                'withColumn("a5",lit("6trg")).withColumn("a6",lit(5))',
            'eval a5 = rand()':
                'withColumn("a5",rand())',
            'where a5 == "6trg"':
                'filter($"a5" === lit("6trg"))',
            'table a1 | eval a6=sin(a1)':
                'select("a1").withColumn("a6",sin($"a1"))',
            #'eval a5=rand() | cache b2 | eval a1=rand()':
            #    'val b2 = df.withColumn("a5",rand())\nval df_out = b2.withColumn("a1",rand())\n',
            'rename a1 as a2, b1 as b2':
                'withColumnRename(%s, %s).withColumnRename(b1, b2)',
            'eval a=rand(), b=rand() | stats count, max(a) as a by b':
                'withColumn("a",rand()).withColumn("b",rand()).groupBy("b").agg(count(),max("a").alias("a"))'
        }
        #searches = {
        #    'source=a("t") | rename a1 as a2, b1 as b2': '.withColumnRename(%s, %s).withColumnRename(b1, b2)',
        #}

        #cl = MQL(earliest="now-d", latest="now")
        q = """
source=filebeat("t") 
| stats max(b) as c, sum(f) as g by d 
| eval a=rand(), b=rand()
| rename a1 as a2, b1 as b2
| where a5 == "6trg"
"""
        print(transform_search(q))
        return ""
        for s in searches:
            a = searches[s]
            spsearch = transform_search(s)
            print(spsearch)
            #print(s, ", ", spsearch)
            #self.assertEqual('a', cl.meta["source"])
            #self.assertEqual('"t"', cl.meta["src_param"])
            #self.assertEqual(a, spsearch)


if __name__ == '__main__':
    unittest.main()