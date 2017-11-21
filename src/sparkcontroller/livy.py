import time

from src.sparkcontroller import webreq as wr


class Livy:
    LVURL = "http://localhost:8998"
    headers = {'Content-Type': 'application/json'}
    sessions = {}
    idles = set()

    def __init__(self):
        self.session = None

    @staticmethod
    def init_livy():
        if len(Livy.sessions) != 0:
            return
        r = wr.get_req(Livy.LVURL + '/sessions') #, data={"from": 0, "size": 30}
        sns = r.json()["sessions"]
        for session in sns:
            Livy.sessions[session["id"]] = session
            if session["state"] == "idle":
                Livy.idles.add(session["id"])

    @staticmethod
    def create_session():
        data = {'kind': 'spark'}
        r = wr.post_req(Livy.LVURL + '/sessions', data=None, json=data, header=Livy.headers)
        session = Livy.LVURL + r.headers['location']
        return session
        #self.session = "http://localhost:8998/sessions/0"

    @staticmethod
    def wait_session_idle(session):
        r = wr.get_req(session, header=Livy.headers).json()
        while r['state'] != 'idle':
            time.sleep(2)
            r = wr.get_req(session, header=Livy.headers).json()
        return r

    def get_free_session(self):
        if len(Livy.idles) != 0:
            session_id = Livy.idles.pop()
            session_url = Livy.LVURL + "/sessions/%d" % session_id
            session = Livy.sessions[session_id]
        else:
            session_url = Livy.create_session()
            session = Livy.wait_session_idle(session_url)
            Livy.sessions[session["id"]] = session
        self.session = session
        return session_url

    def post_query(self, search='spark.read.format("csv").option("header", "true").option("mode", "DROPMALFORMED").csv("hdfs://127.0.0.1:9000/indexes/test/*/*.csv").toJSON.collect()'):
        session_url = self.get_free_session()
        statements_url = session_url + '/statements'
        data = {'code': search}
        r = wr.post_req(statements_url, json=data, header=Livy.headers)
        return r.headers['location']

    def get_result(self, stmt_loc):
        statement_url = Livy.LVURL + stmt_loc
        r = wr.get_req(statement_url, header=Livy.headers)
        while r.json()['state'] != 'available':
            time.sleep(2)
            r = wr.get_req(statement_url, header=Livy.headers)
        return r.json()

    def delete_session(self, session_url):
        #session_url = Livy.LVURL + "/sessions/0"
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