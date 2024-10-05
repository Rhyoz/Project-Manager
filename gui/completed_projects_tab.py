# File: gui/completed_projects_tab.py

from gui.base_projects_tab import BaseProjectsTab
from logger import get_logger
from controllers.project_controller import ProjectController

logger = get_logger(__name__)

class CompletedProjectsTab(BaseProjectsTab):
    def __init__(self, db):
        super().__init__(db, status_filter="Completed", title="Completed Projects")
        self.controller = ProjectController(self.db)
        self.db.project_updated.connect(self.load_projects)
        logger.info("CompletedProjectsTab initialized and connected to project_updated signal.")
