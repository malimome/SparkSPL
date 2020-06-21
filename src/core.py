from src.jobs import Jobs
from src.schedules import SchedMgm
from src.dashboards import DashboardMgm
from src.sources import Source
from src.indexes import Index
from src.utils.threader import threaded
import signal
import time


jb = Jobs().init()
sc = SchedMgm()
dshb = DashboardMgm()
sr = Source()
id = Index()
stop = False
main_thread = None


def service_shutdown(signum, frame):
    global stop
    stop = True
    print("Service exiting ...")
    main_thread.join()
    exit(0)


signal.signal(signal.SIGTERM, service_shutdown)
signal.signal(signal.SIGINT, service_shutdown)


@threaded
def _core_loop():
    global stop
    while not stop:
        """ min_idle is the minimum number of idle sessions to maintain """
        jb.sch.search_loop(min_idle=2)
        time.sleep(5)  # TODO config this
    # Process jobs (get their results)
    # Delete old indexes
    # run scheduled reports


def core_loop():
    global main_thread
    main_thread, ret = _core_loop()
