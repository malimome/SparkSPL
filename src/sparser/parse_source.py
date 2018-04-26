from src.sources import Source

source_inits = {
    "elastic": "spark.read.format(\"org.elasticsearch.spark.sql\")"
               ".option(\"es.nodes\", \"localhost\").option(\"es.port\", \"9200\")"
               ".option(\"es.read.field.empty.as.null\",\"true\")"
               ".option(\"es.index.read.missing.as.empty\",\"true\")"
               ".option(\"es.mapping.include\", \"beat.*, prospector.*, tags.*\")"
               ".option(\"es.read.field.exclude\", \"prospector,beat,tags\")",
    "generative": "sqlContext.range(0, 10000)"
}


def source_query(source_id, earliest, latest):
    sr = Source()
    source = sr.get_source(source_id)
    sourceq = ""
    if source["type"] == "elastic":
        sourceq = source_inits[source["type"]]
        sourceq += ".option(\"es.query\",\"\"\"{\"query\": "
        sourceq += "{\"range\": {\"@timestamp\": {\"gte\":\"%s\", \"lt\":\"%s\"}}}}\"\"\")" \
                   % (earliest, latest)
        sourceq += ".load(\"{index}-*\")".format(index=source_id)
    else:
        sourceq = source_inits[source["type"]]
    return sourceq