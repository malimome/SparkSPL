from src.sparkcontroller.zp import Zp
from src.sparkcontroller.livy import Livy
import time
import signal
from src.utils.threader import threaded


class SparkController(object):
    def __init__(self):
        pass

    @staticmethod
    def post_search(search):
        zp = Zp()
        zp.create_note('rapinote')
        zp.create_parag("1st parag", search)
        zp.run_parag()
        result = zp.get_parag()
        zp.delete_note()
        return result

    def get_result(self):
        pass


stop = False


def service_shutdown(signum, frame):
    global stop
    stop = True


signal.signal(signal.SIGTERM, service_shutdown)
signal.signal(signal.SIGINT, service_shutdown)
#signal.signal(signal.SIGKILL, service_shutdown)


@threaded
def get_x_idle_sessions(x):
    global stop
    i = 0
    while not stop:
        i += 1
        if i%4 == 0:
            Livy.init_livy(force=True)
        if x <= len(Livy.idles):
            time.sleep(30)
            continue
        session = Livy.create_idle_session()
        session_id = session["id"]
        Livy.sessions[session_id] = session
        Livy.idles.add(session_id)


class SparkControllerLivy(object):
    lv = None
    Ran = False

    @staticmethod
    def init():
        SparkControllerLivy.lv = Livy()
        SparkControllerLivy.lv.init_livy()
        if SparkControllerLivy.Ran is False:
            get_x_idle_sessions(2)
            SparkControllerLivy.Ran = True
        return SparkControllerLivy

    @staticmethod
    def post_search(search):
        ssn_stmt = SparkControllerLivy.lv.post_query(search)
        return ssn_stmt

    @staticmethod
    def get_result(ssn_stmt):
        return SparkControllerLivy.lv.get_result(ssn_stmt)

    @staticmethod
    def get_result_async(ssn_stmt):
        return SparkControllerLivy.lv.get_result_async(ssn_stmt)

    @staticmethod
    def cancel_search(ssn_stmt):
        return SparkControllerLivy.lv.cancel_query(ssn_stmt)

    @staticmethod
    def cleanup(ssn_stmt):
        return SparkControllerLivy.lv.session_restore(ssn_stmt)

