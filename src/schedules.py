import uuid

from src import storage as st


class SchedMgm:
    def __init__(self):
        self.sstorage = st.FileStorage("schedules.conf")
        self.scheds = self.sstorage.getall()

    def all_scheds(self):
        return self.scheds

    def add_sched(self, sched):
        sched_id = str(uuid.uuid1())
        self.scheds = self.sstorage.add(sched_id, sched)
        return {
            "job_id": sched_id,
            "job": sched
        }

    def get_sched(self, sched_id):
        sched = self.scheds[sched_id]
        return sched

    def update_sched(self, sched_id, sched):
        self.scheds = self.sstorage.update(sched_id, sched)

    def del_sched(self, sched_id):
        self.scheds = self.sstorage.delete(sched_id)


