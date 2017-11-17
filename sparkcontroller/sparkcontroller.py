from sparkcontroller.zp import Zp
from sparkcontroller.livy import Livy


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


class SparkControllerLivy(object):

    @staticmethod
    def post_search(search):
        l = Livy()
        r = l.post_query(search)
        return(l.get_result(r.headers['location']))

