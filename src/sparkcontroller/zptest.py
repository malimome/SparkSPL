from src.sparkcontroller import SparkController

sc = SparkController()
ret = sc.post_search('val textFile = sc.textFile("hdfs://127.0.0.1:9000/indexes/test/*/*.csv")\ntextFile.collect().foreach(println)')
print(ret)

#zpi = Zp()
#zpi.get_notes()
