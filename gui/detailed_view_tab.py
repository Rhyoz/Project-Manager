# gui/detailed_view_tab.py
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QLineEdit, QDateEdit, QComboBox,
    QCheckBox, QSpinBox, QPushButton, QMessageBox, QHBoxLayout, QTextEdit
)
from PyQt5.QtCore import Qt, QDate, QThread
from gui.base_projects_tab import BaseProjectsTab
from project import Project
from utils import sanitize_filename, get_project_dir, open_docx_file
from pdf_converter import PDFConverter
from logger import get_logger
import os

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
        from gui.add_project_dialog import AddProjectDialog
        dialog = AddProjectDialog(self.db)
        if dialog.exec_():
            self.load_projects()
            logger.info("New project added via dialog.")

    def move_to_active(self, project):
        super().move_to_active(project)
        self.load_projects()

    def save_docx(self):
        super().save_docx()

    def open_docx(self):
        super().open_docx()

    def view_extra(self, project):
        super().view_extra(project)

    def view_docx(self, project, doc_type):
        super().view_docx(project, doc_type)

    def convert_to_pdf(self, project):
        from utils import get_docx_temp_dir
        excel_path = os.path.join(get_project_dir(), sanitize_filename(f"{project.name}_{project.number}"), f"{doc_type}.xlsx")
        pdf_path = os.path.join(get_docx_temp_dir(), f"{project.name}_{project.number}_{doc_type}.pdf")

        self.converter = PDFConverter(excel_path, pdf_path)
        self.thread = QThread()
        self.converter.moveToThread(self.thread)
        self.converter.conversion_complete.connect(self.on_conversion_complete)
        self.converter.conversion_failed.connect(self.on_conversion_failed)
        self.thread.started.connect(self.converter.run_conversion)
        self.converter.conversion_complete.connect(self.thread.quit)
        self.converter.conversion_failed.connect(self.thread.quit)
        self.thread.start()

    def on_conversion_complete(self, pdf_path):
        QMessageBox.information(self, "Conversion Complete", f"PDF saved at {pdf_path}")
        logger.info(f"PDF conversion completed: {pdf_path}")

    def on_conversion_failed(self, error_message):
        QMessageBox.critical(self, "Conversion Failed", f"Failed to convert PDF:\n{error_message}")
        logger.error(f"PDF conversion failed: {error_message}")
