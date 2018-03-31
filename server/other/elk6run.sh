~/elasticsearch-6.0.1/bin/elasticsearch &
# curl http://localhost:9200/

#~/kibana-6.0.1-linux-x86_64/bin/kibana &
#http://localhost:5601

~/logstash-6.0.0/bin/logstash -f ~/logstash-6.0.0/bfpipe.conf --config.reload.automatic &

sudo ./filebeat-6.0.0-linux-x86_64/filebeat -e -c ./filebeat-6.0.0-linux-x86_64/filebeat.yml &

