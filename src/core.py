from src.jobs import Jobs
from src.schedules import SchedMgm
from src.dashboards import DashboardMgm
from src.sources import Source


jb = Jobs().init()
sc = SchedMgm()
dshb = DashboardMgm()
sr = Source()


def coreloop():
    pass
    # Process jobs
    # process Livy stuff
    # run scheduled reports
