from src.crud import EntityStore
from src.utils import validation as v


class SchedMgm(EntityStore):
    LABEL = "schedule"
    FIELDS = ("name", "description", "query", "cron", "earliest", "latest",
              "action_email", "script", "throttling", "tags")

    def __init__(self):
        super(SchedMgm, self).__init__("schedules.conf")

    def _clean(self, payload):
        item = super(SchedMgm, self)._clean(payload)
        if "query" in item:
            v.query(item["query"])
        for f in ("earliest", "latest"):
            if f in item:
                v.time_expr(item[f], f)
        # The script field names a file to run; never accept paths.
        if "script" in item:
            v.name(item["script"], "script name")
        return item

    def all_scheds(self):
        return self.all()

    def add_sched(self, sched):
        sched_id, item = self.add(sched)
        return {"job_id": sched_id, "job": item}

    def get_sched(self, sched_id):
        return self.get(sched_id)

    def update_sched(self, sched_id, sched):
        return self.update(sched_id, sched)

    def del_sched(self, sched_id):
        self.delete(sched_id)
