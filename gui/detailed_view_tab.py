# File: gui/detailed_view_tab.py

from gui.base_projects_tab import BaseProjectsTab
from logger import get_logger
from controllers.project_controller import ProjectController

logger = get_logger(__name__)

class DetailedViewTab(BaseProjectsTab):
    def __init__(self, db):
        super().__init__(db, status_filter=None, title="Detailed Project View")
        self.controller = ProjectController(self.db)
        self.current_project = None
        self.db.project_updated.connect(self.load_projects)
        logger.info("DetailedViewTab initialized and connected to project_updated signal.")
