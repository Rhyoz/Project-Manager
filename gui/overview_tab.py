# File: gui/overview_tab.py

from gui.base_projects_tab import BaseProjectsTab
from gui.add_project_dialog import AddProjectDialog
from logger import get_logger
from PyQt5.QtWidgets import QPushButton, QHBoxLayout
from controllers.project_controller import ProjectController

logger = get_logger(__name__)

class OverviewTab(BaseProjectsTab):
    def __init__(self, db):
        super().__init__(db, status_filter="Active", title="Overview Projects")
        self.controller = ProjectController(self.db)
        self.setup_add_project_ui()
        self.db.project_updated.connect(self.load_projects)
        logger.info("OverviewTab initialized and connected to project_updated signal.")

    def setup_add_project_ui(self):
        # Add Project Button
        self.add_project_btn = QPushButton("Add New Project")
        self.add_project_btn.clicked.connect(self.open_add_project_dialog)
        
        # Add the button to the buttons_layout
        self.buttons_layout.addWidget(self.add_project_btn)

    def open_add_project_dialog(self):
        dialog = AddProjectDialog(self.db)
        if dialog.exec_():
            self.load_projects()
            logger.info("New project added via dialog.")
