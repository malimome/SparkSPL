import time

from src.sparkcontroller import webreq as wr


class Livy:
    LVURL = "http://localhost:8998"
    headers = {'Content-Type': 'application/json'}

    def __init__(self):
        self.session = None

    def create_session(self):
        data = {'kind': 'spark'}
        r = wr.post_req(Livy.LVURL + '/sessions', data=None, json=data, header=Livy.headers)
        self.session = Livy.LVURL + r.headers['location']
        #self.session = "http://localhost:8998/sessions/0"
        print(self.session)
        while r.json()['state'] != 'idle':
            time.sleep(2)
            r = wr.get_req(self.session, header=Livy.headers)

    def post_query(self, search='spark.read.format("csv").option("header", "true").option("mode", "DROPMALFORMED").csv("hdfs://127.0.0.1:9000/indexes/test/*/*.csv").toJSON.collect()'):
        if self.session is None:
            self.create_session()
        statements_url = self.session + '/statements'
        data = {'code': search}
        r = wr.post_req(statements_url, json=data, header=Livy.headers)
        return r

    def get_result(self, stmt_loc):
        statement_url = Livy.LVURL + stmt_loc
        r = wr.get_req(statement_url, header=self.headers)
        while r.json()['state'] != 'available':
            time.sleep(2)
            r = wr.get_req(statement_url, header=self.headers)
        return r.json()

    def delete_session(self):
        session_url = Livy.LVURL + "/sessions/0"
        wr.delete_req(session_url, header=Livy.headers)


if __name__ == '__main__':
    l = Livy()
    while 1:
        try:
            s = input('spark > ')
        except EOFError:
            break
        if not s:
            continue
        r = l.post_query(s)
        ret = l.get_result(r.headers['location'])
        print(ret)
    l.delete_session()