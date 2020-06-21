from src.crud import EntityStore


class DashboardMgm(EntityStore):
    LABEL = "dashboard"
    FIELDS = ("name", "description", "xml")

    def __init__(self):
        super(DashboardMgm, self).__init__("dashboards.conf")

    def all_dashs(self):
        return self.all()

    def add_dash(self, dashboard):
        dash_id, item = self.add(dashboard)
        return {"dash_id": dash_id, "dash": item}

    def get_dash(self, dash_id):
        return self.get(dash_id)

    def update_dash(self, dash_id, dashboard):
        return self.update(dash_id, dashboard)

    def del_dash(self, dash_id):
        self.delete(dash_id)
