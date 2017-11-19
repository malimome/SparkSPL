from flask import Flask
from flask_restplus import Resource, Api as BaseApi, fields
from src.jobs import JobMgm
from src.schedules import SchedMgm

from src.sample_data import gen_data


class Api(BaseApi):
    def _register_doc(self, app_or_blueprint):
        if self._add_specs and self._doc:
            app_or_blueprint.add_url_rule(self._doc, 'doc', self.render_doc)

    @property
    def base_path(self):
        return ''


app = Flask(__name__)
api = Api(app, version='1.0', title="Splunk 2 Spark", description="Splunk 2 Spark Mock service.", doc='/doc/')
jb = JobMgm()
sc = SchedMgm()


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response


@api.route('/')
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


@api.route('/sample/count/<int:count>')
class Gen(Resource):
    @api.doc('Sample data')
    #@cors.crossdomain(origin='*')
    def get(self, count):
        return gen_data(count)


@api.route('/search/<string:search>/start/<int:start>/end/<int:end>')
class Search(Resource):
    @api.doc('Search Api')
    def get(self, search, start, end):
        """ run a query and add it as job """
        job = jb.add_job(search, start, end)
        return job


@api.route('/jobs')
class Jobs(Resource):
    @api.doc('Get list of jobs')
    def get(self):
        """ get list of all jobs """
        return jb.all_jobs()


@api.route('/jobs/<string:job_id>')
class JobId(Resource):
    @api.doc('Get job id status')
    def get(self, job_id):
        """ Get job's status and result by id """
        job = jb.get_job(job_id)
        jobres = dict(job)
        if job["status"] == "finished":
            jobres = dict(job)
            jobres["result"] = jb.get_job_result(job_id)
        return jobres

    def delete(self, job_id):
        """ Delete a job """
        jb.del_job(job_id)


sched_post = api.model('Resource', {
    'name': fields.String(description="Report name"),
    'description': fields.String(description="The description of the report"),
    'query': fields.String(description="The query to run for this report"),
    'cron': fields.String(description="Cron style scheduling trigger string"),
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

if __name__ == '__main__':
    app.run(debug=True)