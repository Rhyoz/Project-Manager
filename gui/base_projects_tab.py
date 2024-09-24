# gui/base_projects_tab.py
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QHBoxLayout, QMessageBox
)
from PyQt5.QtGui import QColor
from datetime import datetime
import os
import sys
import subprocess
import tempfile
from logger import get_logger
from utils import sanitize_filename, open_docx_file
from docx import Document

logger = get_logger(__name__)

class BaseProjectsTab(QWidget):
    def __init__(self, db, status_filter=None, title=""):
        super().__init__()
        self.db = db
        self.status_filter = status_filter
        self.title = title
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.setup_ui()
        self.load_projects()
    
    def setup_ui(self):
        # Buttons Layout
        self.buttons_layout = QHBoxLayout()
        
        # Save to DOCX Button
        self.save_docx_btn = QPushButton("Save to DOCX")
        self.save_docx_btn.setToolTip(f"Save {self.title} to DOCX")
        self.save_docx_btn.clicked.connect(self.save_docx)
        self.buttons_layout.addWidget(self.save_docx_btn)

        # Open DOCX Button
        self.open_docx_btn = QPushButton("Open DOCX")
        self.open_docx_btn.setToolTip(f"Open {self.title} DOCX")
        self.open_docx_btn.clicked.connect(self.open_docx)
        self.buttons_layout.addWidget(self.open_docx_btn)

        self.layout.addLayout(self.buttons_layout)

        # Projects Table
        self.table = QTableWidget()
        self.table.setColumnCount(11)  # Adjust as needed
        self.table.setHorizontalHeaderLabels([
            "Project Name",
            "Project Number",
            "Complex",
            "Start Date",
            "End Date",
            "Status",
            "Worker",
            "Innregulering",
            "Sjekkliste",
            "Extra",
            "Move"
        ])
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.layout.addWidget(self.table)

        # Temporary DOCX path
        self.docx_path = os.path.join(tempfile.gettempdir(), f"{self.title.replace(' ', '_')}_Projects.docx")

    def load_projects(self):
        self.table.setRowCount(0)
        projects = self.db.load_projects(status=self.status_filter)
        for project in projects:
            self.add_project_row(project)

    def add_project_row(self, project):
        row_position = self.table.rowCount()
        self.table.insertRow(row_position)

        self.table.setItem(row_position, 0, QTableWidgetItem(project.name))
        self.table.setItem(row_position, 1, QTableWidgetItem(project.number))
        complex_text = "Yes" if project.is_residential_complex else "No"
        self.table.setItem(row_position, 2, QTableWidgetItem(complex_text))
        self.table.setItem(row_position, 3, QTableWidgetItem(self.format_date(project.start_date)))
        self.table.setItem(row_position, 4, QTableWidgetItem(self.format_date(project.end_date) if project.end_date else ""))
        self.table.setItem(row_position, 5, QTableWidgetItem(project.status))
        self.table.setItem(row_position, 6, QTableWidgetItem(project.worker))
        self.table.setItem(row_position, 9, QTableWidgetItem(project.extra if project.extra else ""))  # "Extra" field

        # Apply background color based on status
        if project.status in ["Awaiting Completion", "Paused"]:
            for col in range(11):  # Apply to entire row
                item = self.table.item(row_position, col)
                if item:
                    item.setBackground(QColor('yellow'))

        # Innregulering Button
        innregulering_btn = QPushButton("View DOCX")
        innregulering_btn.setToolTip("View Innregulering DOCX")
        innregulering_btn.clicked.connect(lambda checked, p=project: self.view_docx(p, "Innregulering"))
        self.table.setCellWidget(row_position, 7, innregulering_btn)

        # Sjekkliste Button
        sjekkliste_btn = QPushButton("View DOCX")
        sjekkliste_btn.setToolTip("View Sjekkliste DOCX")
        sjekkliste_btn.clicked.connect(lambda checked, p=project: self.view_docx(p, "Sjekkliste"))
        self.table.setCellWidget(row_position, 8, sjekkliste_btn)

        # Extra Button
        extra_btn = QPushButton("View")
        extra_btn.setToolTip("View Extra Details")
        if not project.extra:
            extra_btn.setEnabled(False)  # Gray out if "Extra" is empty
        else:
            extra_btn.clicked.connect(lambda checked, p=project: self.view_extra(p))
        self.table.setCellWidget(row_position, 9, extra_btn)

        # Move to Active Button
        move_active_btn = QPushButton("Active")
        move_active_btn.setToolTip("Move Project to Active")
        move_active_btn.setStyleSheet("background-color: yellow")
        move_active_btn.clicked.connect(lambda checked, p=project: self.move_to_active(p))
        self.table.setCellWidget(row_position, 10, move_active_btn)

    def format_date(self, date_str):
        try:
            return datetime.strptime(date_str, "%Y-%m-%d").strftime("%d-%m-%Y")
        except:
            return date_str

    def view_docx(self, project, doc_type):
        from utils import get_project_dir
        folder_name = sanitize_filename(f"{project.name}_{project.number}")
        project_folder = os.path.join(get_project_dir(), folder_name)
        docx_file = os.path.join(project_folder, f"{doc_type}.docx")

        if not os.path.exists(docx_file):
            QMessageBox.warning(self, "DOCX Error", f"{doc_type}.docx does not exist for this project.")
            logger.warning(f"{doc_type}.docx not found for project ID {project.id}")
            return

        success, message = open_docx_file(docx_file)
        if not success:
            QMessageBox.warning(self, "DOCX Error", message)
            logger.error(f"Failed to open {doc_type}.docx for project ID {project.id}: {message}")

    def view_extra(self, project):
        QMessageBox.information(self, "Extra Details", f"Extra Details:\n{project.extra}")

    def move_to_active(self, project):
        reply = QMessageBox.question(
            self,
            "Confirm Status Change",
            f"Are you sure you want to move project '{project.name}' to Active?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            try:
                project.status = "Active"
                project.end_date = None  # Clear end date when moving back to Active
                self.db.update_project(project)
                self.load_projects()
                QMessageBox.information(self, "Status Updated", f"Project '{project.name}' moved to Active.")
                logger.info(f"Moved project ID {project.id} to Active.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to move to Active: {str(e)}")
                logger.error(f"Failed to move project ID {project.id} to Active: {e}")

    def save_docx(self):
        try:
            document = Document()
            document.add_heading(f'{self.title}', 0)

            projects = self.db.load_projects(status=self.status_filter)
            if not projects:
                QMessageBox.information(self, "No Data", f"There are no {self.title.lower()} to export.")
                return

            headers = ["Project Name", "Project Number", "Complex", "Start Date", "End Date", "Status", "Worker", "Extra"]
            table = document.add_table(rows=1, cols=len(headers))
            table.style = 'Light List Accent 1'

            hdr_cells = table.rows[0].cells
            for idx, header in enumerate(headers):
                hdr_cells[idx].text = header

            for project in projects:
                row_cells = table.add_row().cells
                row_cells[0].text = project.name
                row_cells[1].text = project.number
                row_cells[2].text = "Yes" if project.is_residential_complex else "No"
                row_cells[3].text = self.format_date(project.start_date)
                row_cells[4].text = self.format_date(project.end_date) if project.end_date else ""
                row_cells[5].text = project.status
                row_cells[6].text = project.worker
                row_cells[7].text = project.extra if project.extra else ""

            document.add_paragraph(f"Generated on: {datetime.now().strftime('%d-%m-%Y')}", style='Intense Quote')
            document.save(self.docx_path)

            QMessageBox.information(self, "Success", f"DOCX saved successfully at {self.docx_path}")
            logger.info(f"DOCX saved at {self.docx_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save DOCX: {str(e)}")
            logger.error(f"Failed to save DOCX: {e}")

    def open_docx(self):
        if not os.path.exists(self.docx_path):
            QMessageBox.warning(self, "DOCX Not Found", "No DOCX has been saved yet.")
            logger.warning("Attempted to open DOCX but none exists.")
            return

        try:
            if sys.platform.startswith('darwin'):
                subprocess.call(['open', self.docx_path])
            elif os.name == 'nt':
                os.startfile(self.docx_path)
            elif os.name == 'posix':
                subprocess.call(['xdg-open', self.docx_path])
            QMessageBox.information(self, "Open DOCX", "The DOCX has been opened.")
            logger.info(f"Opened DOCX at {self.docx_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open DOCX: {str(e)}")
            logger.error(f"Failed to open DOCX: {e}")
