#echo "stop hadoop"
#~/hadoop/sbin/stop-dfs.sh
echo "stop zep"
~/zeppelin-0.7.3/bin/zeppelin-daemon.sh stop
echo "stop spark"
~/spark-2.2.1/sbin/stop-master.sh
~/spark-2.2.1/sbin/stop-slaves.sh

