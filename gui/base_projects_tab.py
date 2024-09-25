# gui/base_projects_tab.py
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QTreeWidget, QTreeWidgetItem, QHBoxLayout, QMessageBox, QCheckBox
)
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt
from datetime import datetime
import os
import sys
import subprocess
import tempfile
from logger import get_logger
from utils import sanitize_filename, open_docx_file, get_project_dir
from docx import Document
from database import UnitModel, ProjectModel  # Ensure ProjectModel is also imported

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

        # Projects Tree
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels([
            "Project Name",
            "Project Number",
            "Main Contractor",
            "Complex",
            "Completed Units",
            "Status",
            "Extra",
            "Innregulering",
            "Sjekkliste",
            "Move(1)",
            "Move(2)",
            "Start Date",
            "End Date",
            "Worker"
        ])
        self.tree.setColumnCount(14)
        self.layout.addWidget(self.tree)

        # Temporary DOCX path
        self.docx_path = os.path.join(tempfile.gettempdir(), f"{self.title.replace(' ', '_')}_Projects.docx")

    def load_projects(self):
        self.tree.clear()
        projects = self.db.load_projects(status=self.status_filter)
        for project in projects:
            project_item = QTreeWidgetItem([
                project.name,
                project.number,
                project.main_contractor if project.main_contractor else "",
                "Yes" if project.is_residential_complex else "No",
                "",
                project.status,
                project.extra if project.extra else "",
                "",
                "",
                "",
                "",
                self.format_date(project.start_date),
                self.format_date(project.end_date) if project.end_date else "",
                project.worker
            ])
            if project.is_residential_complex and project.units:
                # Calculate completed units
                completed = self.db.session.query(UnitModel).filter_by(project_id=project.id, is_done=True).count()
                total = len(project.units)
                project_item.setText(4, f"{completed}/{total}")
                
                self.tree.addTopLevelItem(project_item)
                for unit_name in project.units:
                    unit_item = QTreeWidgetItem([
                        unit_name,
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        ""
                    ])
                    # Add a checkbox for done/undone
                    checkbox = QCheckBox()
                    # Retrieve the unit model to get its current status
                    unit_model = self.db.session.query(UnitModel).filter_by(project_id=project.id, name=unit_name).first()
                    if unit_model:
                        checkbox.setChecked(unit_model.is_done)
                    checkbox.stateChanged.connect(lambda state, p=project, u=unit_name: self.toggle_unit_status(p, u, state))
                    self.tree.setItemWidget(unit_item, 0, checkbox)
                    project_item.addChild(unit_item)
                
                # Innregulering Button
                innregulering_btn = QPushButton("View DOCX")
                innregulering_btn.setToolTip("View Innregulering DOCX")
                innregulering_btn.clicked.connect(lambda checked, p=project: self.view_docx(p, "Innregulering"))
                self.tree.setItemWidget(project_item, 7, innregulering_btn)

                # Sjekkliste Button
                sjekkliste_btn = QPushButton("View DOCX")
                sjekkliste_btn.setToolTip("View Sjekkliste DOCX")
                sjekkliste_btn.clicked.connect(lambda checked, p=project: self.view_docx(p, "Sjekkliste"))
                self.tree.setItemWidget(project_item, 8, sjekkliste_btn)

                # Move(1) Button
                move1_btn = QPushButton("Active")
                move1_btn.setToolTip("Move Project to Active")
                move1_btn.setStyleSheet("background-color: yellow")
                move1_btn.clicked.connect(lambda checked, p=project: self.move_to_active(p))
                self.tree.setItemWidget(project_item, 9, move1_btn)

                # Move(2) Button
                move2_btn = QPushButton("Completed")
                move2_btn.setToolTip("Move Project to Completed")
                move2_btn.setStyleSheet("background-color: green")
                move2_btn.clicked.connect(lambda checked, p=project: self.move_to_completed(p))
                self.tree.setItemWidget(project_item, 10, move2_btn)

            else:
                # Innregulering Button
                innregulering_btn = QPushButton("View DOCX")
                innregulering_btn.setToolTip("View Innregulering DOCX")
                innregulering_btn.clicked.connect(lambda checked, p=project: self.view_docx(p, "Innregulering"))
                self.tree.setItemWidget(project_item, 7, innregulering_btn)

                # Sjekkliste Button
                sjekkliste_btn = QPushButton("View DOCX")
                sjekkliste_btn.setToolTip("View Sjekkliste DOCX")
                sjekkliste_btn.clicked.connect(lambda checked, p=project: self.view_docx(p, "Sjekkliste"))
                self.tree.setItemWidget(project_item, 8, sjekkliste_btn)

                # Move(1) Button
                move1_btn = QPushButton("Active")
                move1_btn.setToolTip("Move Project to Active")
                move1_btn.setStyleSheet("background-color: yellow")
                move1_btn.clicked.connect(lambda checked, p=project: self.move_to_active(p))
                self.tree.setItemWidget(project_item, 9, move1_btn)

                # Move(2) Button
                move2_btn = QPushButton("Completed")
                move2_btn.setToolTip("Move Project to Completed")
                move2_btn.setStyleSheet("background-color: green")
                move2_btn.clicked.connect(lambda checked, p=project: self.move_to_completed(p))
                self.tree.setItemWidget(project_item, 10, move2_btn)

                # Set Completed Units to N/A
                project_item.setText(4, "N/A")

    def move_to_completed(self, project):
        reply = QMessageBox.question(
            self,
            "Confirm Status Change",
            f"Are you sure you want to move project '{project.name}' to Completed?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            try:
                project.status = "Completed"
                if not project.is_residential_complex:
                    project.end_date = datetime.now().strftime("%Y-%m-%d")
                self.db.update_project(project)
                self.load_projects()
                QMessageBox.information(self, "Status Updated", f"Project '{project.name}' moved to Completed.")
                logger.info(f"Moved project ID {project.id} to Completed.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to move to Completed: {str(e)}")
                logger.error(f"Failed to move project ID {project.id} to Completed: {e}")

    def get_completed_units(self, project):
        if project.is_residential_complex:
            completed = self.db.session.query(UnitModel).filter_by(project_id=project.id, is_done=True).count()
            return completed
        return 0

    def toggle_unit_status(self, project, unit_name, state):
        is_done = state == Qt.Checked
        # Fetch unit by name and project
        unit = self.db.session.query(UnitModel).join(ProjectModel).filter(
            ProjectModel.id == project.id,
            UnitModel.name == unit_name
        ).first()
        if unit:
            try:
                self.db.toggle_unit_status(project.id, unit.id, is_done)
                self.load_projects()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to update unit status: {str(e)}")
                logger.error(f"Failed to update unit status for Unit '{unit_name}' in Project ID {project.id}: {e}")

    def format_date(self, date_str):
        try:
            return datetime.strptime(date_str, "%Y-%m-%d").strftime("%d-%m-%Y")
        except:
            return date_str

    def view_docx(self, project, doc_type):
        folder_name = sanitize_filename(f"{project.main_contractor} - {project.name} - {project.number}") if project.main_contractor else sanitize_filename(f"{project.name}_{project.number}")
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

            headers = ["Project Name", "Project Number", "Main Contractor", "Complex", "Completed Units", "Status", "Extra", "Innregulering", "Sjekkliste", "Move(1)", "Move(2)", "Start Date", "End Date", "Worker"]
            table = document.add_table(rows=1, cols=len(headers))
            table.style = 'Light List Accent 1'

            hdr_cells = table.rows[0].cells
            for idx, header in enumerate(headers):
                hdr_cells[idx].text = header

            for project in projects:
                row_cells = table.add_row().cells
                row_cells[0].text = project.name
                row_cells[1].text = project.number
                row_cells[2].text = project.main_contractor if project.main_contractor else ""
                row_cells[3].text = "Yes" if project.is_residential_complex else "No"
                if project.is_residential_complex:
                    completed = self.db.session.query(UnitModel).filter_by(project_id=project.id, is_done=True).count()
                    total = len(project.units)
                    row_cells[4].text = f"{completed}/{total}"
                else:
                    row_cells[4].text = "N/A"
                row_cells[5].text = project.status
                row_cells[6].text = project.extra if project.extra else ""
                row_cells[7].text = "View DOCX"
                row_cells[8].text = "View DOCX"
                row_cells[9].text = "Active"
                row_cells[10].text = "Completed"
                row_cells[11].text = self.format_date(project.start_date)
                row_cells[12].text = self.format_date(project.end_date) if project.end_date else ""
                row_cells[13].text = project.worker

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
