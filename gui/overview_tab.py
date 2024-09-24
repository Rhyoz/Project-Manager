# gui/overview_tab.py
from gui.base_projects_tab import BaseProjectsTab
from logger import get_logger

logger = get_logger(__name__)

class OverviewTab(BaseProjectsTab):
    def __init__(self, db):
        super().__init__(db, status_filter=None, title="Overview Projects")
