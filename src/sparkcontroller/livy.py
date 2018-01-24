import time

from src.sparkcontroller import webreq as wr


class Livy:
    LVURL = "http://localhost:8998"
    headers = {'Content-Type': 'application/json'}
    sessions = {}
    idles = set()

    def __init__(self):
        self.session_url = ""
        self.session_id = None

    @staticmethod
    def init_livy():
        if len(Livy.sessions) != 0:
            return
        r = wr.get_req(Livy.session_url()) #, data={"from": 0, "size": 30}
        sns = r.json()["sessions"]
        for session in sns:
            Livy.sessions[session["id"]] = session
            if session["state"] == "idle":
                Livy.idles.add(session["id"])
        #print(Livy.sessions)
        #print(Livy.idles)

    @staticmethod
    def create_session():
        data = {
            'kind': 'spark', 'proxyUser': 'user',
            'driverCores': 2, 'executorCores': 2,
            #'driverMemory': '', 'executorMemory': ''
        }
        data = {}
        r = wr.post_req(Livy.session_url(), data=None, json=data, header=Livy.headers)
        session_id = r.json()["id"]
        return session_id

    @staticmethod
    def get_session(session_url):
        r = wr.get_req(session_url, header=Livy.headers)
        return r.json()

    @staticmethod
    def wait_session_idle(session_id):
        session_url = Livy.session_url_from_id(session_id)
        r = Livy.get_session(session_url)
        while r['state'] != 'idle':
            time.sleep(2)
            r = Livy.get_session(session_url)
        return r

    def get_free_session(self):
        if len(Livy.idles) != 0:
            session_id = Livy.idles.pop()
        else:
            session_id = Livy.create_session()
            session = Livy.wait_session_idle(session_id)
            Livy.sessions[session["id"]] = session
        self.session_id = session_id
        return session_id

    def post_query(self, search):
        session_id = self.get_free_session()
        statements_url = Livy.stmt_url_from_id(session_id)
        data = {'code': search}
        r = wr.post_req(statements_url, json=data, header=Livy.headers)
        stmt_pf = r.headers['location']
        stpos = stmt_pf.rfind("/")
        if stpos == -1:
            raise Exception("Fatal error!")
        stmt_id = stmt_pf[stpos+1:]
        return {"sid": session_id, "tid": stmt_id}

    def get_result_async(self, ssn_stmt):
        self.session_id = ssn_stmt["sid"]
        statement_url = Livy.stmtid_url_from_ids(self.session_id, ssn_stmt["tid"])
        r = wr.get_req(statement_url, header=Livy.headers)
        result = r.json()
        # TODO do this on a thread
        if result['state'] == "available":
            self.session_restore()
        return result

    def get_result(self, ssn_stmt):
        result = self.get_result_async(ssn_stmt)
        while result['state'] != 'available':
            time.sleep(2)
            result = self.get_result_async(ssn_stmt)
        self.session_restore()
        return result

    def session_restore(self):
        if self.session_id in Livy.idles:
            return 0
        session = self.wait_session_idle(self.session_id)
        Livy.idles.add(session["id"])
        Livy.sessions[session["id"]] = session
        return 0

    def delete_session(self):
        wr.delete_req(Livy.session_url_from_id(self.session_id), header=Livy.headers)

    @staticmethod
    def session_url():
        return "{base}/sessions".format(base=Livy.LVURL)

    @staticmethod
    def session_url_from_id(session_id):
        return "{base}/sessions/{session_id}".format(base=Livy.LVURL, session_id=session_id)

    @staticmethod
    def stmt_url_from_id(session_id):
        return "{base}/sessions/{session_id}/statements".format(base=Livy.LVURL, session_id=session_id)

    @staticmethod
    def stmtid_url_from_ids(session_id, stmt_id):
        return "{base}/sessions/{session_id}/statements/{stmt_id}".format(base=Livy.LVURL,
                                                    session_id=session_id, stmt_id=stmt_id)


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