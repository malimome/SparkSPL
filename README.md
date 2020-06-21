# Spark SPL Engine

A REST API that lets you search data with an SPL-style query language and runs it on Apache Spark.

```
source=filebeat | stats count by host | sort count desc
```

The server translates the query into Spark/Scala, runs it on an [Apache Livy](https://livy.apache.org/) session against an Elasticsearch index, and returns the result as JSON. It also manages sources, indexes, schedules and dashboards.

## Requirements

- Python 3.8+
- A running Apache Livy server with Spark
- Elasticsearch with the `elasticsearch-spark` connector available to Spark

## Run

```bash
pip install -r requirements.txt

export SPARKIFY_API_KEYS=choose-a-secret-key
export SPARKIFY_LIVY_URL=http://localhost:8998   # optional, see Configuration

python spl2spark_server.py          # dev server at http://127.0.0.1:5000
```

Try it:

```bash
curl -H "X-API-Key: choose-a-secret-key" http://127.0.0.1:5000/jobs
```

Interactive API docs are at `http://127.0.0.1:5000/doc/`.

For production use uwsgi (`sparkify.ini`) behind nginx (`server/sparkify.nginx`). Put the environment variables in `/etc/sparkify/env`, one `KEY=value` per line.

## Configuration

All settings are environment variables (see `settings.py`).

| Variable | Default | Purpose |
|---|---|---|
| `SPARKIFY_API_KEYS` | empty | Comma-separated keys accepted in the `X-API-Key` header. Empty rejects every request. |
| `SPARKIFY_LIVY_URL` | `http://localhost:8998` | Livy endpoint |
| `SPARKIFY_LIVY_PROXY_USER` | empty | Livy `proxyUser` |
| `SPARKIFY_ES_HOST` / `SPARKIFY_ES_PORT` | `localhost` / `9200` | Elasticsearch used by `source=` queries |
| `SPARKIFY_DATA_DIR` | `./static` | Storage for jobs, sources, schedules and results |
| `SPARKIFY_CORS_ORIGINS` | empty | Comma-separated allowed origins |
| `SPARKIFY_JOB_TTL` | `600` | Seconds before a job and its result expire |
| `SPARKIFY_DEBUG` | `false` | Debug logging; never enable in production |
| `SPARKIFY_DISABLE_AUTH` | `false` | Skip authentication (local development only) |

## Tests

```bash
python -m pytest src/tests/unit
```
