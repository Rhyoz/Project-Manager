# gui/completed_projects_tab.py
from gui.base_projects_tab import BaseProjectsTab
from logger import get_logger

logger = get_logger(__name__)

class CompletedProjectsTab(BaseProjectsTab):
    def __init__(self, db):
        super().__init__(db, status_filter="Completed", title="Completed Projects")
