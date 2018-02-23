import uuid

from src import storage as st


class DashboardMgm:
    def __init__(self):
        self.sstorage = st.INIStorage("dashboards.conf")
        self.dashs = self.sstorage.getall()

    def all_dashs(self):
        return self.dashs

    def add_dash(self, dashboard):
        dash_id = str(uuid.uuid1())
        self.dashs = self.sstorage.add(dash_id, dashboard)
        return {
            "dash_id": dash_id,
            "dash": dashboard
        }

    def get_dash(self, dash_id):
        sched = self.dashs[dash_id]
        return sched

    def update_dash(self, dash_id, dashboard):
        self.dashs = self.sstorage.update(dash_id, dashboard)

    def del_dash(self, dash_id):
        self.dashs = self.sstorage.delete(dash_id)


