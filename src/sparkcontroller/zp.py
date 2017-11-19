from src import sparkcontroller as wr


class Zp:
    ZPURL = "http://localhost:8889/"

    UNOTEBOOK = ZPURL + "api/notebook"  #get, post
    UNOTEINFO = UNOTEBOOK + "/{noteid}" #get, delete, post,
    UCREATEPARAG = UNOTEINFO + "/paragraph"  #post
    UGPARAG = UCREATEPARAG + "/{paragid}" #get, delete
    USTATUSPARAG = UNOTEBOOK + "/job/{noteid}/{paragid}"  #get, post, delete
    URUNPARAM = UNOTEBOOK + "/run/{noteid}/{paragid}"

    def __init__(self, zpurl=""):
        self.notes = {}
        self.note = ""
        self.noteid= 0
        self.paragid = 0

    def get_notes(self):
        url = Zp.UNOTEBOOK
        resp = wr.get_req(url).json()
        for note in resp["body"]:
            self.notes[note["name"]] = note["id"]

    def set_note(self, note_name):
        if note_name not in self.notes:
            raise Exception("no notes")
        self.note = note_name
        self.noteid = self.notes[note_name]

    def get_note(self):
        url = Zp.UNOTEBOOK.format(noteid=self.noteid)
        resp = wr.get_req(url).json()
        return resp

    def create_note(self, note_name):
        url = Zp.UNOTEBOOK
        js = {"name": note_name}
        resp = wr.post_req(url, None, js).json()
        self.note = note_name
        self.noteid = resp["body"]

    def delete_note(self):
        url = Zp.UNOTEINFO.format(noteid=self.noteid)
        resp = wr.delete_req(url)

    def clone_note(self):
        pass

    def create_parag(self, name, content):
        url = Zp.UCREATEPARAG.format(noteid=self.noteid)
        js = {"title": name, "text": content}
        resp = wr.post_req(url, None, js).json()
        self.paragid = resp["body"]

    def delete_parag(self):
        url = Zp.USTATUSPARAG.format(noteid=self.noteid, paragid=self.paragid)
        resp = wr.delete_req(url)
        return

    def get_parag(self):
        url = Zp.UGPARAG.format(noteid=self.noteid, paragid=self.paragid)
        resp =wr.get_req(url).json()
        return resp["body"]

    def run_parag(self):
        url = Zp.URUNPARAM.format(noteid=self.noteid, paragid=self.paragid)
        resp = wr.post_req(url).json()
        return

