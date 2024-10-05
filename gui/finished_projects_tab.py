# File: gui/finished_projects_tab.py

from gui.base_projects_tab import BaseProjectsTab
from logger import get_logger
from controllers.project_controller import ProjectController

logger = get_logger(__name__)

class FinishedProjectsTab(BaseProjectsTab):
    def __init__(self, db):
        super().__init__(db, status_filter="Finished", title="Finished Projects")
        self.controller = ProjectController(self.db)
        self.db.project_updated.connect(self.load_projects)
        logger.info("FinishedProjectsTab initialized and connected to project_updated signal.")
