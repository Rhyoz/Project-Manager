# gui/detailed_view_tab.py
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton
)
from PyQt5.QtCore import Qt
from gui.base_projects_tab import BaseProjectsTab
from gui.add_project_dialog import AddProjectDialog
from logger import get_logger

logger = get_logger(__name__)

class DetailedViewTab(BaseProjectsTab):
    def __init__(self, db):
        super().__init__(db, status_filter=None, title="Detailed Project View")
        self.current_project = None
        self.setup_add_project_ui()

    def setup_add_project_ui(self):
        # Add Project Button
        self.add_project_btn = QPushButton("Add New Project")
        self.add_project_btn.clicked.connect(self.open_add_project_dialog)
        self.layout.addWidget(self.add_project_btn)

    def open_add_project_dialog(self):
        dialog = AddProjectDialog(self.db)
        if dialog.exec_():
            self.load_projects()
            logger.info("New project added via dialog.")
