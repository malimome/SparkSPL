import hmac
import logging

from flask import Flask, request
from flask_restx import Resource, Api as BaseApi, fields
from webargs import fields as wfields, validate
from webargs.flaskparser import use_kwargs

import settings
from src.core import jb, sc, dshb, sr, id, core_loop
from src.search import QueryExecutionError
from src.sparkcontroller.webreq import UpstreamError
from src.utils.validation import ValidationError, NotFoundError

logging.basicConfig(level=logging.DEBUG if settings.FLASK_DEBUG else logging.INFO)
log = logging.getLogger("sparkify")

PUBLIC_PATHS = ("/", "/doc/", "/swagger.json")
PUBLIC_PREFIXES = ("/swaggerui/",)


class Api(BaseApi):
    def _register_doc(self, app_or_blueprint):
        if self._add_specs and self._doc:
            app_or_blueprint.add_url_rule(self._doc, 'doc', self.render_doc)

    @property
    def base_path(self):
        return ''


app = Flask(__name__)
app.config["RESTX_MASK_SWAGGER"] = False
app.config["ERROR_404_HELP"] = False
app.config["MAX_CONTENT_LENGTH"] = 1024 * 1024
api = Api(app, version='1.3', title="Porseh", description="Porseh service.", doc='/doc/')

if not settings.DISABLE_AUTH and not settings.API_KEYS:
    log.warning("SPARKIFY_API_KEYS is empty: every API request will be rejected.")
core_loop()


def _authorized():
    supplied = request.headers.get("X-API-Key", "")
    return any(hmac.compare_digest(supplied.encode(), key.encode()) for key in settings.API_KEYS)


@app.before_request
def authenticate():
    if settings.DISABLE_AUTH or request.method == "OPTIONS":
        return None
    if request.path in PUBLIC_PATHS or request.path.startswith(PUBLIC_PREFIXES):
        return None
    if not _authorized():
        return {"message": "Unauthorized"}, 401, {"WWW-Authenticate": "API-Key"}
    return None


@app.after_request
def after_request(response):
    origin = request.headers.get("Origin")
    if origin and origin in settings.CORS_ORIGINS:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Headers"] = "Content-Type,X-API-Key"
        response.headers["Access-Control-Allow-Methods"] = "GET,PUT,POST,DELETE"
        response.headers.add("Vary", "Origin")
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Cache-Control"] = "no-store"
    return response


# Handlers are matched in registration order, so specific ones come first.
@api.errorhandler(ValidationError)
def handle_validation(ex):
    return {"message": str(ex)}, 400


@api.errorhandler(QueryExecutionError)
def handle_query_error(ex):
    return {"message": str(ex)}, 400


@api.errorhandler(NotFoundError)
def handle_not_found(ex):
    return {"message": str(ex)}, 404


@api.errorhandler(UpstreamError)
def handle_upstream(ex):
    log.error("Upstream failure: %s", ex)
    return {"message": "A backend service is unavailable"}, 502


@api.errorhandler(Exception)
def handle_unexpected(ex):
    log.exception("Unhandled error")
    return {"message": "Internal server error"}, 500


@api.route('/')
@api.response(200, 'App is successfully loaded')
class Home(Resource):
    @api.doc('project_info')
    def get(self):
        """ get app info """
        return {
            "project": "Porseh",
            "description": "Porseh service.",
            "version": 1.3,
            "docs": "goto /doc for the api documentation"
        }


def _run_blocking(job_post):
    job = jb.add_job(job_post)
    try:
        jb.post_job(job)
        return jb.get_job(job["job_id"], mode="blocking")
    finally:
        jb.delete_quietly(job["job_id"])


@api.route('/jobs/<string:query>/earliest/<string:earliest>/latest/<string:latest>')
class Search(Resource):
    @api.doc('Search Api, get result in blocking mode!')
    def post(self, query, earliest, latest):
        """ run a query in blocking mode and return the result """
        return _run_blocking({'query': query, 'earliest': earliest, 'latest': latest,
                              'mode': 'blocking', 'priority': 'normal'})


job_post = api.model('Job', {
    'query': fields.String(description="The query to run for this report", required=True),
    'earliest': fields.String(description="The earliest time to fetch data."),
    'latest': fields.String(description="The latest time to fetch data."),
    'priority': fields.String(required=False, enum=["normal", "low", "high"],
                              default="normal", description="low, normal or high."),
    'mode': fields.String(required=False, enum=["normal", "blocking"],
                          default="normal", description="blocking or normal"),
    'testing': fields.String(required=False, description='Set to y in debug mode only.')
})


@api.route('/jobs')
class Jobs(Resource):
    @api.doc('Get list of jobs')
    def get(self):
        """ get list of all jobs """
        return jb.get_jobs()

    @api.doc('Create a new search job.')
    @api.expect(job_post, validate=True)
    def post(self):
        """ run a query and add it as job """
        payload = api.payload
        if settings.FLASK_DEBUG and payload.get("testing") == "y":
            return jb.post_test_job()
        if payload.get("mode") == "blocking":
            return _run_blocking(payload)
        job = jb.add_job(payload)
        jb.post_job(job)
        return job


@api.route('/jobs/<string:job_id>')
@api.doc(params={'job_id': 'Job_id string'})
class JobId(Resource):
    args = {
        'mode': wfields.Str(load_default='normal', validate=validate.OneOf(['blocking', 'normal'])),
        'offset': wfields.Int(load_default=0, validate=validate.Range(0, 10 ** 12)),
        'count': wfields.Int(load_default=10000, validate=validate.Range(0, 100000)),
    }
    action = {
        'action': wfields.Str(required=True, validate=validate.OneOf(['cancel', 'log'])),
    }

    @use_kwargs(args, location="query")
    @api.doc('Get job id status and results')
    def get(self, job_id, mode, offset, count):
        """ Get job's status and result by id """
        return jb.get_job(job_id, mode, offset, count)

    @use_kwargs(action, location="query")
    @api.doc('Cancels a job')
    def put(self, job_id, action):
        """ Cancel a job """
        if action == "cancel":
            return jb.stop_job(job_id)
        return {"message": "Action %s is not implemented" % action}, 501

    def delete(self, job_id):
        """ Delete a job """
        jb.cancel_and_delete(job_id)
        return {"message": "success"}


index_post = api.model('Index', {
    'name': fields.String(description="The index name", required=True),
    'retention': fields.Integer(description="The number of retention days."),
    'retention_size': fields.Integer(description="The retention size of index in MB."),
    'readonly': fields.Boolean(description="If cannot be used to dump summary data.")
})


@api.route('/indexes')
class Indexes(Resource):
    @api.doc('Get list of indexes')
    def get(self):
        """ get list of all indexes """
        return id.get_indexes()

    @api.doc('Create a new index.')
    @api.expect(index_post, validate=True)
    def post(self):
        """ add a new index """
        id.add_index(api.payload)
        return {"message": "success"}, 201


@api.route('/indexes/<string:name>')
@api.doc(params={'name': 'index name'})
class IndexName(Resource):
    @api.doc('Get index by name')
    def get(self, name):
        """ Get index by name """
        return id.get_index(name)

    def delete(self, name):
        """ Delete an index """
        id.del_index(name)
        return {"message": "success"}


sched_post = api.model('Schedule', {
    'name': fields.String(description="Report name"),
    'description': fields.String(description="The description of the report"),
    'query': fields.String(description="The query to run for this report"),
    'cron': fields.String(description="Cron style scheduling trigger string"),
    'earliest': fields.String(description="The earliest time to fetch data."),
    'latest': fields.String(description="The latest time to fetch data."),
    'action_email': fields.String(description="List of emails (comma separated)"),
    'script': fields.String(description="script file name to run"),
    'throttling': fields.String(description="Throttling string"),
    'tags': fields.String(description="Comma seperated list of tags")
})


@api.route('/schedules')
class ScheduledJobs(Resource):
    @api.doc('Get list of Scheduled queries')
    def get(self):
        """ get list of all scheduled reports """
        return sc.all_scheds()

    @api.expect(sched_post, validate=True)
    def post(self):
        """ create a new scheduled report """
        return sc.add_sched(api.payload), 201


@api.route('/schedules/<string:sched_id>')
class SchedId(Resource):
    @api.doc('Get sched id')
    def get(self, sched_id):
        """ Get scheduled report by id """
        return sc.get_sched(sched_id)

    @api.expect(sched_post, validate=True)
    def put(self, sched_id):
        """ update a scheduled report """
        return sc.update_sched(sched_id, api.payload)

    def delete(self, sched_id):
        """ delete scheduled report"""
        sc.del_sched(sched_id)
        return {"message": "success"}


source_post = api.model('Source', {
    'name': fields.String(description="Source name", required=True),
    'description': fields.String(description="The description of the source"),
    'type': fields.String(description="default | elastic | hadoop | mysql | mssql | postgresql"),
    'connection': fields.String(description="index name in the default "),
    'query': fields.String(description="The query to get the raw data"),
    'index': fields.String(description="The index with wildcard name if it is daily index")
})


@api.route('/sources')
class Sources(Resource):
    @api.doc('Get list of sources')
    def get(self):
        """ get list of all sources """
        return sr.all_sources()

    @api.expect(source_post, validate=True)
    def post(self):
        """ create a new source """
        return sr.add_source(api.payload), 201


@api.route('/sources/<string:src_id>')
class SourceID(Resource):
    @api.doc('Get source by id')
    def get(self, src_id):
        """ Get source by id """
        return sr.get_public_source(src_id)

    @api.expect(source_post)
    def put(self, src_id):
        """ update a source """
        return sr.update_source(src_id, api.payload)

    def delete(self, src_id):
        """ delete a source """
        sr.del_source(src_id)
        return {"message": "success"}


dash_post = api.model('Dashboard', {
    'name': fields.String(description="Dashboard name"),
    'description': fields.String(description="The description of the dashboard"),
    'xml': fields.String(description="The xml to run for this dashboard")
})


@api.route('/dashboards')
class Dashboard(Resource):
    @api.doc('Get list of dashboards')
    def get(self):
        """ get list of all dashboards """
        return dshb.all_dashs()

    @api.expect(dash_post, validate=True)
    def post(self):
        """ create a new dashboard """
        return dshb.add_dash(api.payload), 201


@api.route('/dashboards/<string:dash_id>')
class DashboardId(Resource):
    @api.doc('Get dash id')
    def get(self, dash_id):
        """ Get dashboard by id """
        return dshb.get_dash(dash_id)

    @api.expect(dash_post, validate=True)
    def put(self, dash_id):
        """ update a dashboard """
        return dshb.update_dash(dash_id, api.payload)

    def delete(self, dash_id):
        """ delete dashboard"""
        dshb.del_dash(dash_id)
        return {"message": "success"}


if __name__ == '__main__':
    # Development server only; production runs under uwsgi (see sparkify.ini).
    app.run(host="127.0.0.1", debug=False)
