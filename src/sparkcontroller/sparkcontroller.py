from src.sparkcontroller.zp import Zp

from src.sparkcontroller.livy import Livy


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
    def __init__(self):
        self.lv = Livy()
        self.lv.init_livy()

    def post_search(self, search):
        r = self.lv.post_query(search)
        return r

    def get_result(self, r):
        return self.lv.get_result(r)

