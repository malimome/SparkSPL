from flask import Flask
from flask_restplus import Resource, Api as BaseApi, fields
from src.jobs import Jobs
from src.schedules import SchedMgm
from src.dashboards import DashboardMgm
from src.sources import Source
import settings
#from flask_restplus_patched._http import HTTPStatus
#from src.utils import http_exceptions as he


class Api(BaseApi):
    def _register_doc(self, app_or_blueprint):
        if self._add_specs and self._doc:
            app_or_blueprint.add_url_rule(self._doc, 'doc', self.render_doc)

    @property
    def base_path(self):
        return ''


app = Flask(__name__)
#app.config['RESTPLUS_VALIDATE'] = settings.RESTPLUS_VALIDATE
#app.config['SERVER_NAME'] = settings.FLASK_SERVER_NAME
#app.config['SWAGGER_UI_DOC_EXPANSION'] = settings.RESTPLUS_SWAGGER_UI_DOC_EXPANSION
#app.config['RESTPLUS_MASK_SWAGGER'] = settings.RESTPLUS_MASK_SWAGGER
api = Api(app, version='1.0', title="Splunk 2 Spark", description="Splunk 2 Spark Mock service.", doc='/doc/')
jb = Jobs()
sc = SchedMgm()
dshb = DashboardMgm()
sr = Source()
# TODO create a user session and tie Livy sessions to it.


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    response.headers.add('server', 'MyApp')
    return response


@api.route('/')
@api.response(200, 'App is successfully loaded')
#@api.response(HTTPStatus.BAD_REQUEST, "BAD_REQUEST")
class Index(Resource):
    @api.doc('project_info')
    def get(self):
        """ get app info """
        result = {
            "project": "Splunk 2 Spark",
            "description": "Splunk 2 Spark Mock service.",
            "version": 1,
            "docs": "goto /doc for the api documentation"
        }
        return result


@api.route('/jobs/<string:search>/earliest/<string:start>/latest/<string:end>')
class Search(Resource):
    @api.doc('Search Api')
    def post(self, search, start, end):
        """ run a query and add it as job """
        ret = {}
        try:
            job = jb.add_job(search, start, end)
            jb.post_job(job)
        except Exception:
            raise
            #he.abort(HTTPStatus.INTERNAL_SERVER_ERROR)
        return job


@api.route('/jobs')
class Jobs(Resource):
    @api.doc('Get list of jobs')
    #@api.marshal_with(Job) bring job's model here
    def get(self):
        """ get list of all jobs """
        try:
            return jb.get_jobs()
        except Exception:
            raise
            #he.abort(HTTPStatus.INTERNAL_SERVER_ERROR)


@api.route('/jobs/<string:job_id>/async')
class JobIdAsync(Resource):
    @api.doc('Get job id status')
    def get(self, job_id):
        """ Get job's status and result by id """
        try:
            job, result = jb.get_job_async(job_id)
        except Exception:
            raise
            #he.abort(HTTPStatus.INTERNAL_SERVER_ERROR)
        jobres = dict(job)
        if job["status"] == "finished":
            jobres["result"] = result
        else:
            jobres["result"] = {}
        return jobres


@api.route('/jobs/<string:job_id>')
class JobId(Resource):
    @api.doc('Get job id status')
    def get(self, job_id):
        """ Get job's status and result by id """
        try:
            job, result = jb.get_job(job_id)
        except Exception:
            raise
            #he.abort(HTTPStatus.INTERNAL_SERVER_ERROR)
        jobres = dict(job)
        if job["status"] == "finished":
            jobres["result"] = result
        else:
            jobres["result"] = {}
        return jobres

    def delete(self, job_id):
        """ Delete a job """
        try:
            jb.del_job(job_id)
        except Exception:
            raise
            #he.abort(HTTPStatus.INTERNAL_SERVER_ERROR)


sched_post = api.model('Schedule', {
    'name': fields.String(description="Report name"),
    'description': fields.String(description="The description of the report"),
    'query': fields.String(description="The query to run for this report"),
    'cron': fields.String(description="Cron style scheduling trigger string"),
    'earliest': fields.String(description="The earliest time to fetch data."),
    'latest': fields.String(description="The latest time to fetch data."),
    'action_email': fields.String(description="List of emails (comma separated)"),
    'script': fields.String(description="script file name to run"),
    'throttling': fields.String(description="Throttling string")
})


@api.route('/schedules')
class ScheduledJobs(Resource):
    @api.doc('Get list of Scheduled queries')
    def get(self):
        """ get list of all scheduled reports """
        return sc.all_scheds()

    @api.expect(sched_post)
    def post(self):
        """ create a new scheduled report """
        return sc.add_sched(api.payload)


@api.route('/schedules/<string:sched_id>')
class SchedId(Resource):
    @api.doc('Get sched id')
    def get(self, sched_id):
        """ Get scheduled report by id """
        sched = sc.get_sched(sched_id)
        return sched

    @api.expect(sched_post)
    def update(self, sched_id):
        sc.update_sched(sched_id, api.payload)

    def delete(self, sched_id):
        """ delete scheduled report"""
        sc.del_sched(sched_id)


source_post = api.model('Source', {
    'name': fields.String(description="Source name"),
    'description': fields.String(description="The description of the source"),
    'type': fields.String(description="default | elastic | hadoop | mysql | mssql | postgresql"),
    'connection': fields.String(description="index name in the default "),
    'query': fields.String(description="The query to get the raw data")
})


@api.route('/sources')
class Sources(Resource):
    @api.doc('Get list of sources')
    def get(self):
        """ get list of all sources """
        return sr.sources

    @api.expect(source_post)
    def post(self):
        """ create a new source """
        return sr.add_source(api.payload)


@api.route('/sources/<string:src_id>')
class SourceID(Resource):
    @api.doc('Get source by id')
    def get(self, src_id):
        """ Get scheduled report by id """
        src = sr.get_source(src_id)
        return src

    @api.expect(source_post)
    def update(self, src_id):
        sr.update_source(src_id, api.payload)

    def delete(self, src_id):
        """ delete a source """
        sr.del_source(src_id)


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

    @api.expect(sched_post)
    def post(self):
        """ create a new dashboard """
        return dshb.add_dash(api.payload)


@api.route('/dashboards/<string:dash_id>')
class DashboardId(Resource):
    @api.doc('Get dash id')
    def get(self, dash_id):
        """ Get scheduled report by id """
        sched = dshb.get_dash(dash_id)
        return sched

    @api.expect(sched_post)
    def update(self, dash_id):
        dshb.update_dash(dash_id, api.payload)

    def delete(self, dash_id):
        """ delete dashboard"""
        dshb.del_dash(dash_id)


if __name__ == '__main__':
    app.run(debug=True)
