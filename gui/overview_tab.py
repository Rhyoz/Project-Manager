# gui/overview_tab.py
from gui.base_projects_tab import BaseProjectsTab
from logger import get_logger

logger = get_logger(__name__)

class OverviewTab(BaseProjectsTab):
    def __init__(self, db):
        super().__init__(db, status_filter="Active", title="Overview Projects")
        self.db.project_updated.connect(self.load_projects)