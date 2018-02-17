import unittest

from src.sparser.parser import MQL
from fnmatch import fnmatch


class TestParser(unittest.TestCase):

    def test_postjob(self):
        searches = {
            'source=filebeat("t")':
                'spark.read.format("org.elasticsearch.spark.sql").option("es.nodes", "localhost").option("es.port", "9200").option("es.read.field.empty.as.null","true").option("es.index.read.missing.as.empty","true").option("es.mapping.include", "beat.*, prospector.*, tags.*").option("es.read.field.exclude", "prospector,beat,tags").option("es.query","""{"query": {"match_all":{}},"filter": {"range":{"@timestamp": {"gte":"now-d", "lt":"now"}}}}""").load("filebeat-*").sort(desc("@timestamp"))',
            'table a1, a2, a3':
                'select("a1", "a2", "a3")',
            'drop a1, a2, a3':
                'drop("a1", "a2", "a3")',
            'head 5':
                'limit(5)',
            'sort a desc, b asc, c, +d, -f':
                'sort($"a".desc, $"b".asc, $"c".desc, $"d".asc, $"f".desc)',
            'stats max(b) as c, sum(f) as g by d':
                'groupBy("d").agg(max("b").alias("c"), sum("f").alias("g"))',
            'eval a5 = (r1)*(2.3+r2+if(1 - 1, if(10<1, 100+1, 8*1), 3))':
                'withColumn("a5",($"r1")*(lit(2.3)+$"r2"+when(lit(1)-lit(1), when(lit(10) < lit(1), lit(100)+lit(1)).otherwise(lit(8)*lit(1))).otherwise(lit(3))))',
            'eval a5 = "6trg", a6=5':
                'withColumn("a5",lit("6trg")).withColumn("a6",lit(5))',
            'eval a5 = rand()':
                'withColumn("a5",rand())',
            'where a5 == "6trg"':
                'filter($"a5" === lit("6trg"))',
            'rename a1 as a2, b1 as b2':
                'withColumnRename("a1", "a2").withColumnRename("b1", "b2")',
            'window max(b) as c, sum(f) as g over b orderby c range -1 to 1':
                'val wS*=Window.partitionBy("b").orderBy($"c".desc).rangeBetween(-1, 1);withColumn("c", max("b").over(wS*)).withColumn("g", sum("f").over(wS*))'
        }

        cl = MQL(earliest="now-d", latest="now")
        for s in searches:
            a = searches[s]
            spsearch = cl.run(s)
            before = ""
            after = ""
            if "before" in cl.meta:
                before = "%s;" % cl.meta["before"]
            if "after" in cl.meta:
                after = ";%s" % cl.meta["after"]
            final = before + spsearch + after
            #spsearch = transform_search(s)

            ret = fnmatch(final, a)
            if not ret:
                print("#", s, final, a)
            self.assertTrue(ret)
            #print(s, ", ", spsearch)
            #self.assertEqual(a, spsearch)


if __name__ == '__main__':
    unittest.main()