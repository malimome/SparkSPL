import logging
import threading

from src.dashboards import DashboardMgm
from src.indexes import Index
from src.jobs import Jobs
from src.schedules import SchedMgm
from src.sources import Source
from src.sparkcontroller.webreq import UpstreamError

log = logging.getLogger(__name__)

jb = Jobs().init()
sc = SchedMgm()
dshb = DashboardMgm()
sr = Source()
id = Index()

_stop = threading.Event()
_thread = None


def _core_loop(interval=5):
    while not _stop.is_set():
        try:
            # Keep a minimum number of idle Livy sessions ready.
            jb.sch.search_loop(min_idle=2)
        except UpstreamError as ex:
            log.warning("Livy unavailable: %s", ex)
        except Exception:
            log.exception("Core loop iteration failed")
        _stop.wait(interval)


def core_loop():
    """Start the background session manager once per process."""
    global _thread
    if _thread is None or not _thread.is_alive():
        _stop.clear()
        _thread = threading.Thread(target=_core_loop, name="sparkify-core", daemon=True)
        _thread.start()


def stop_core_loop():
    _stop.set()
