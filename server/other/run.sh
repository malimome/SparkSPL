#echo "start hadoop"
#~/hadoop/sbin/start-dfs.sh
echo "start spark 7077"
unset HADOOP_CONF_DIR
~/spark-2.2.1/sbin/start-master.sh
~/spark-2.2.1/sbin/start-slave.sh spark://spark-master.example.internal:7077
echo "start zeppelin 8998"
~/zeppelin-0.7.3/bin/zeppelin-daemon.sh start
echo "start Livy"
~/livy-server-0.4.0/bin/livy-server > /dev/null &
#echo "start zookeeper"
#~/zookeeper/bin/zkServer.sh start
#echo "start kafka"
#~/kafka_2.11/bin/kafka-server-start.sh ~/kafka_2.11/config/server.properties
#export PATH=$PATH:/home/user/kafka_2.11/bin


# create kafka topic
# ~/kafka_2.11/bin/kafka-topics.sh --create --zookeeper localhost:2181 --replication-factor 1 --partitions 1 --topic OryxInput
# ~/kafka_2.11/bin/kafka-topics.sh --create --zookeeper localhost:2181 --replication-factor 1 --partitions 1 --topic OryxUpdate
