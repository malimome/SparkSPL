import settings
from src.sources import Source
from src.utils import validation as v

# Source re-reads its storage on every lookup, so API changes are seen immediately.
_sources = Source()


def source_inits():
    return {
        "elastic": "spark.read.format(\"org.elasticsearch.spark.sql\")"
                   ".option(\"es.nodes\", \"%s\").option(\"es.port\", \"%s\")"
                   ".option(\"es.read.field.empty.as.null\",\"true\")"
                   ".option(\"es.index.read.missing.as.empty\",\"true\")"
                   ".option(\"es.mapping.include\", \"beat.*, prospector.*, tags.*\")"
                   ".option(\"es.read.field.exclude\", \"prospector,beat,tags\")"
                   % (settings.ES_HOST, settings.ES_PORT),
        "generative": "sqlContext.range(0, 10000)",
    }


def source_query(source_id, earliest, latest):
    # earliest/latest/index end up inside generated Scala code, so they must be validated here
    # no matter where the caller got them from.
    earliest = v.time_expr(earliest, "earliest")
    latest = v.time_expr(latest, "latest")
    source = _sources.get_source(source_id)
    inits = source_inits()
    if source["type"] not in inits:
        raise v.ValidationError("Source type %s cannot be queried" % source["type"])
    sourceq = inits[source["type"]]
    if source["type"] == "elastic":
        index = v.index_pattern(source["index"])
        sourceq += ".option(\"es.query\",\"\"\"{\"query\": "
        sourceq += "{\"range\": {\"@timestamp\": {\"gte\":\"%s\", \"lt\":\"%s\"}}}}\"\"\")" \
                   % (earliest, latest)
        sourceq += ".load(\"%s\")" % index
    return sourceq
