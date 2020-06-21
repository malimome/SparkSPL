import logging
import time

from src.sparkcontroller.livy import Livy
from src.sparkcontroller.webreq import UpstreamError

log = logging.getLogger(__name__)

SESSION_REFRESH_SECONDS = 240


class SparkControllerLivy(object):
    lv = None
    last_refresh = time.time()

    @staticmethod
    def init():
        SparkControllerLivy.lv = Livy()
        try:
            SparkControllerLivy.lv.init_livy()
        except UpstreamError as ex:
            log.warning("Livy is not reachable yet, will retry: %s", ex)
        return SparkControllerLivy

    @staticmethod
    def manage_livy_session(min_idle):
        if time.time() - SparkControllerLivy.last_refresh > SESSION_REFRESH_SECONDS:
            Livy.init_livy(force=True)
            SparkControllerLivy.last_refresh = time.time()
        with Livy.lock:
            if min_idle <= len(Livy.idles):
                return 0
        session = Livy.create_idle_session()
        with Livy.lock:
            Livy.sessions[session["id"]] = session
            Livy.idles.add(session["id"])

    @staticmethod
    def post_search(search):
        return SparkControllerLivy.lv.post_query(search)

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
