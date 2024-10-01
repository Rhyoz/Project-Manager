# File: gui/base_projects_tab.py
from PyQt5.QtWidgets import (
        QWidget, QVBoxLayout, QToolButton, QMenu, QAction, QTreeWidget, QTreeWidgetItem, QHBoxLayout, QMessageBox, QCheckBox, QPushButton, QFileDialog
    )
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt, QPoint
from datetime import datetime
import os
import sys
import subprocess
import shutil
import tempfile
from logger import get_logger
from utils import sanitize_filename, open_docx_file, get_project_dir, get_template_dir
from docx import Document
from docx.enum.section import WD_ORIENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches
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
            
            # View DOCX Split Button (default action is now View DOCX)
            self.view_docx_split_btn = QToolButton()
            self.view_docx_split_btn.setText("View DOCX")
            self.view_docx_split_btn.setToolTip(f"View {self.title} DOCX")
            self.view_docx_split_btn.setPopupMode(QToolButton.MenuButtonPopup)
    
            # Create menu with only "Save As..." option
            self.view_docx_menu = QMenu(self)
            self.save_as_action = QAction("Save As...", self)
            self.save_as_action.triggered.connect(self.save_docx_overview)
            self.view_docx_menu.addAction(self.save_as_action)
    
            # Set the default button click to trigger "View DOCX"
            self.view_docx_split_btn.clicked.connect(self.view_docx_overview)
            self.view_docx_split_btn.setMenu(self.view_docx_menu)
    
            self.buttons_layout.addWidget(self.view_docx_split_btn)
    
            self.layout.addLayout(self.buttons_layout)
    
            # Projects Tree
            self.tree = QTreeWidget()
            self.tree.setHeaderLabels([
                "Project Name",
                "Project Number",
                "Main Contractor",
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
            self.tree.setColumnCount(13)
            self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
            self.tree.customContextMenuRequested.connect(self.open_context_menu)
            self.layout.addWidget(self.tree)
    
            # Temporary DOCX path
            self.docx_path = os.path.join(tempfile.gettempdir(), f"{sanitize_filename(self.title)}_Projects.docx")
    
        def load_projects(self):
            self.tree.clear()
            projects = self.db.load_projects(status=self.status_filter)
            logger.info(f"Loading {len(projects)} projects into the '{self.title}' tab.")
            for project in projects:
                project_item = QTreeWidgetItem([
                    project.name,
                    project.number,
                    project.main_contractor if project.main_contractor else "",
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
                project_item.setData(0, Qt.UserRole, project.id)
                self.tree.addTopLevelItem(project_item)
                if project.is_residential_complex and project.units:
                    # Calculate completed units
                    completed = self.db.session.query(UnitModel).filter_by(project_id=project.id, is_done=True).count()
                    total = len(project.units)
                    project_item.setText(3, f"{completed}/{total}")
    
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
                            ""
                        ])
                        # Add a checkbox for done/undone
                        checkbox = QCheckBox()
                        # Retrieve the unit model to get its current status
                        unit_model = self.db.session.query(UnitModel).filter_by(project_id=project.id, name=unit_name).first()
                        if unit_model:
                            checkbox.setChecked(unit_model.is_done)
                        # Use a lambda with default arguments to capture current project and unit_name
                        checkbox.stateChanged.connect(lambda state, p=project, u=unit_name: self.toggle_unit_status(p, u, state))
                        self.tree.setItemWidget(unit_item, 0, checkbox)
                        project_item.addChild(unit_item)
    
                    # Expand the project item to show unit names by default
                    self.tree.expandItem(project_item)
                
                # Innregulering Split Button
                innregulering_split_btn = QToolButton()
                innregulering_split_btn.setText("View")
                innregulering_split_btn.setToolTip("View Innregulering DOCX")
                innregulering_split_btn.setPopupMode(QToolButton.MenuButtonPopup)
                innregulering_menu = QMenu(self)
                innregulering_save_as_action = QAction("Save As...", self)
                innregulering_save_as_action.triggered.connect(lambda checked, p=project: self.save_docx_as(p, "Innregulering"))
                innregulering_menu.addAction(innregulering_save_as_action)
                innregulering_split_btn.setMenu(innregulering_menu)
                innregulering_split_btn.clicked.connect(lambda checked, p=project: self.view_docx(p, "Innregulering"))
                self.tree.setItemWidget(project_item, 6, innregulering_split_btn)
    
                # Sjekkliste Split Button
                sjekkliste_split_btn = QToolButton()
                sjekkliste_split_btn.setText("View")
                sjekkliste_split_btn.setToolTip("View Sjekkliste DOCX")
                sjekkliste_split_btn.setPopupMode(QToolButton.MenuButtonPopup)
                sjekkliste_menu = QMenu(self)
                sjekkliste_save_as_action = QAction("Save As...", self)
                sjekkliste_save_as_action.triggered.connect(lambda checked, p=project: self.save_docx_as(p, "Sjekkliste"))
                sjekkliste_menu.addAction(sjekkliste_save_as_action)
                sjekkliste_split_btn.setMenu(sjekkliste_menu)
                sjekkliste_split_btn.clicked.connect(lambda checked, p=project: self.view_docx(p, "Sjekkliste"))
                self.tree.setItemWidget(project_item, 7, sjekkliste_split_btn)
    
                # Move(1) Button
                move1_btn = QPushButton("Active")
                move1_btn.setToolTip("Move Project to Active")
                move1_btn.setStyleSheet("background-color: yellow")
                move1_btn.clicked.connect(lambda checked, p=project: self.move_to_active(p))
                self.tree.setItemWidget(project_item, 8, move1_btn)
    
                # Move(2) Button
                move2_btn = QPushButton("Completed")
                move2_btn.setToolTip("Move Project to Completed")
                move2_btn.setStyleSheet("background-color: green")
                move2_btn.clicked.connect(lambda checked, p=project: self.move_to_completed(p))
                self.tree.setItemWidget(project_item, 9, move2_btn)
    
                if not project.is_residential_complex:
                    # Set Completed Units to N/A
                    project_item.setText(3, "N/A")
    
                logger.debug(f"Added project '{project.name}' with status '{project.status}' to the tree.")
            
            self.generate_docx()
    
        def open_context_menu(self, position: QPoint):
            item = self.tree.itemAt(position)
            if item and not item.parent():
                menu = QMenu(self)
                edit_action = QAction("Edit", self)
                delete_action = QAction("Delete", self)
                menu.addAction(edit_action)
                menu.addAction(delete_action)
                action = menu.exec_(self.tree.viewport().mapToGlobal(position))
                if action == edit_action:
                    # Placeholder for Edit functionality
                    pass
                elif action == delete_action:
                    project_id = item.data(0, Qt.UserRole)
                    project = self.db.get_project_by_id(project_id)
                    if project:
                        reply = QMessageBox.question(
                            self,
                            "Confirm Deletion",
                            f"Are you sure you want to delete project '{project.name}'?",
                            QMessageBox.Yes | QMessageBox.No
                        )
                        if reply == QMessageBox.Yes:
                            try:
                                # Delete project folder
                                folder_name = sanitize_filename(f"{project.main_contractor} - {project.name} - {project.number}") if project.main_contractor else sanitize_filename(f"{project.name}_{project.number}")
                                project_folder = os.path.join(get_project_dir(), folder_name)
                                if os.path.exists(project_folder):
                                    shutil.rmtree(project_folder)
                                    logger.info(f"Deleted project folder at {project_folder}")
                                # Delete project from database
                                self.db.delete_project(project.id)
                                self.load_projects()
                                QMessageBox.information(self, "Deleted", f"Project '{project.name}' has been deleted.")
                                logger.info(f"Deleted project '{project.name}' with ID {project.id}")
                            except Exception as e:
                                QMessageBox.critical(self, "Error", f"Failed to delete project: {str(e)}")
                                logger.error(f"Failed to delete project ID {project.id}: {e}")
    
        def view_docx_overview(self):
            # This method is called from the "View DOCX" action in the split button
            # Implement logic to open the current tab's DOCX file
            self.generate_docx()
            if not os.path.exists(self.docx_path):
                QMessageBox.warning(self, "DOCX Error", f"{self.title} DOCX does not exist.")
                logger.warning(f"{self.title} DOCX not found.")
                return
    
            success, message = open_docx_file(self.docx_path)
            if not success:
                QMessageBox.warning(self, "DOCX Error", message)
                logger.error(f"Failed to open {self.title} DOCX: {message}")
    
        def save_docx_overview(self):
            # This method is called from the "Save As..." action in the split button
            self.generate_docx()
            options = QFileDialog.Options()
            save_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save Overview As...",
                f"{sanitize_filename(self.title)}_Projects.docx",
                "Word Documents (*.docx)",
                options=options
            )
            if save_path:
                try:
                    shutil.copy(self.docx_path, save_path)
                    QMessageBox.information(self, "Success", f"Overview saved successfully at:\n{save_path}")
                    logger.info(f"Overview saved as {save_path}")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to save Overview:\n{str(e)}")
                    logger.error(f"Failed to save Overview DOCX: {e}")
    
        def generate_docx(self):
            try:
                document = Document()
                
                # Set page orientation to landscape
                section = document.sections[0]
                section.orientation = WD_ORIENT.LANDSCAPE
                new_width, new_height = section.page_height, section.page_width
                section.page_width = new_width
                section.page_height = new_height
    
                # Add header
                header = section.header
                header_para = header.paragraphs[0]
                header_para.text = self.title
                header_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
                # Add table
                projects = self.db.load_projects(status=self.status_filter)
                if not projects:
                    document.add_paragraph("No projects to display.")
                else:
                    table = document.add_table(rows=1, cols=8)
                    table.style = 'Light List Accent 1'
                    hdr_cells = table.rows[0].cells
                    hdr_cells[0].text = 'Project Name'
                    hdr_cells[1].text = 'Project Number'
                    hdr_cells[2].text = 'Main Contractor'
                    hdr_cells[3].text = 'Completed Units'
                    hdr_cells[4].text = 'Status'
                    hdr_cells[5].text = 'Start Date'
                    hdr_cells[6].text = 'End Date'
                    hdr_cells[7].text = 'Worker'
    
                    for project in projects:
                        row_cells = table.add_row().cells
                        row_cells[0].text = project.name
                        row_cells[1].text = project.number
                        row_cells[2].text = project.main_contractor if project.main_contractor else "N/A"
                        if project.is_residential_complex:
                            completed = self.db.session.query(UnitModel).filter_by(project_id=project.id, is_done=True).count()
                            total = len(project.units)
                            row_cells[3].text = f"{completed}/{total}"
                        else:
                            row_cells[3].text = "N/A"
                        row_cells[4].text = project.status
                        row_cells[5].text = self.format_date(project.start_date)
                        row_cells[6].text = self.format_date(project.end_date) if project.end_date else "N/A"
                        row_cells[7].text = project.worker
    
                    # Adjust column widths to fit the page
                    widths = [Inches(1.5), Inches(1.0), Inches(1.5), Inches(1.2), Inches(1.0), Inches(1.0), Inches(1.0), Inches(1.2)]
                    for row in table.rows:
                        for idx, width in enumerate(widths):
                            row.cells[idx].width = width
    
                # Add footer with current date
                footer = section.footer
                footer_para = footer.paragraphs[0]
                footer_para.text = datetime.now().strftime("%d-%m-%Y")
                footer_para.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    
                document.save(self.docx_path)
                logger.info(f"Generated DOCX at {self.docx_path}")
            except Exception as e:
                QMessageBox.critical(self, "DOCX Generation Error", f"Failed to generate DOCX:\n{str(e)}")
                logger.error(f"Failed to generate DOCX at {self.docx_path}: {e}")
    
        def save_docx_as(self, project, doc_type):
            options = QFileDialog.Options()
            save_path, _ = QFileDialog.getSaveFileName(
                self,
                f"Save {doc_type} As...",
                f"{sanitize_filename(project.name)}_{doc_type}.docx",
                "Word Documents (*.docx)",
                options=options
            )
            if save_path:
                try:
                    folder_name = sanitize_filename(f"{project.main_contractor} - {project.name} - {project.number}") if project.main_contractor else sanitize_filename(f"{project.name}_{project.number}")
                    project_folder = os.path.join(get_project_dir(), folder_name)
                    src_file = os.path.join(project_folder, f"{doc_type}.docx")
                    shutil.copy(src_file, save_path)
                    QMessageBox.information(self, "Success", f"{doc_type} saved successfully at:\n{save_path}")
                    logger.info(f"{doc_type} saved as {save_path}")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to save {doc_type}:\n{str(e)}")
                    logger.error(f"Failed to save {doc_type} for project ID {project.id}: {e}")
    
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
    
        def view_docx_overview(self):
            # This method is called from the "View DOCX" action in the split button
            # Implement logic to open the current tab's DOCX file
            self.generate_docx()
            if not os.path.exists(self.docx_path):
                QMessageBox.warning(self, "DOCX Error", f"{self.title} DOCX does not exist.")
                logger.warning(f"{self.title} DOCX not found.")
                return
    
            success, message = open_docx_file(self.docx_path)
            if not success:
                QMessageBox.warning(self, "DOCX Error", message)
                logger.error(f"Failed to open {self.title} DOCX: {message}")
    
        def save_docx_overview(self):
            # This method is called from the "Save As..." action in the split button
            self.generate_docx()
            options = QFileDialog.Options()
            save_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save Overview As...",
                f"{sanitize_filename(self.title)}_Projects.docx",
                "Word Documents (*.docx)",
                options=options
            )
            if save_path:
                try:
                    shutil.copy(self.docx_path, save_path)
                    QMessageBox.information(self, "Success", f"Overview saved successfully at:\n{save_path}")
                    logger.info(f"Overview saved as {save_path}")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to save Overview:\n{str(e)}")
                    logger.error(f"Failed to save Overview DOCX: {e}")
    
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
                    # Automatically set end_date for all projects
                    project.end_date = datetime.now().strftime("%Y-%m-%d")
                    self.db.update_project(project)
                    self.load_projects()
                    QMessageBox.information(self, "Status Updated", f"Project '{project.name}' moved to Completed.")
                    logger.info(f"Moved project ID {project.id} to Completed with end_date set to {project.end_date}.")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to move to Completed: {str(e)}")
                    logger.error(f"Failed to move project ID {project.id} to Completed: {e}")
