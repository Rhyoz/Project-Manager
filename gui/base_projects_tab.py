# File: gui/base_projects_tab.py
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QToolButton, QMenu, QAction, QTreeWidget, QTreeWidgetItem, 
    QHBoxLayout, QMessageBox, QCheckBox, QPushButton, QFileDialog
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
from utils import sanitize_filename, open_docx_file, get_project_dir, get_template_dir, get_project_folder_name
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
        self.template_dir = get_template_dir()  # Added this line
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
            "Floor Plan(s)",
            "Move(1)",
            "Move(2)",
            "Start Date",
            "End Date",
            "Worker"
        ])
        self.tree.setColumnCount(14)
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

                    # Innregulering Split Button for Unit
                    innregulering_split_btn = QToolButton()
                    innregulering_split_btn.setText("View")
                    innregulering_split_btn.setToolTip("View Innregulering DOCX")
                    innregulering_split_btn.setPopupMode(QToolButton.MenuButtonPopup)
                    innregulering_menu = QMenu(self)
                    innregulering_save_as_action = QAction("Save As...", self)
                    innregulering_save_as_action.triggered.connect(lambda checked, p=project, u=unit_name: self.save_docx_as(p, "Innregulering", u))
                    innregulering_menu.addAction(innregulering_save_as_action)
                    innregulering_split_btn.setMenu(innregulering_menu)
                    innregulering_split_btn.clicked.connect(lambda checked, p=project, u=unit_name: self.view_docx(p, "Innregulering", u))
                    self.tree.setItemWidget(unit_item, 6, innregulering_split_btn)

                    # Sjekkliste Split Button for Unit
                    sjekkliste_split_btn = QToolButton()
                    sjekkliste_split_btn.setText("View")
                    sjekkliste_split_btn.setToolTip("View Sjekkliste DOCX")
                    sjekkliste_split_btn.setPopupMode(QToolButton.MenuButtonPopup)
                    sjekkliste_menu = QMenu(self)
                    sjekkliste_save_as_action = QAction("Save As...", self)
                    sjekkliste_save_as_action.triggered.connect(lambda checked, p=project, u=unit_name: self.save_docx_as(p, "Sjekkliste", u))
                    sjekkliste_menu.addAction(sjekkliste_save_as_action)
                    sjekkliste_split_btn.setMenu(sjekkliste_menu)
                    sjekkliste_split_btn.clicked.connect(lambda checked, p=project, u=unit_name: self.view_docx(p, "Sjekkliste", u))
                    self.tree.setItemWidget(unit_item, 7, sjekkliste_split_btn)

                    # Floor Plan(s) Split Button for Unit
                    floor_plan_split_btn = QToolButton()
                    floor_plan_split_btn.setText("View")
                    floor_plan_split_btn.setToolTip("View Floor Plan(s)")
                    floor_plan_split_btn.setPopupMode(QToolButton.MenuButtonPopup)
                    floor_plan_menu = QMenu(self)
                    import_pdf_action = QAction("Import PDF", self)
                    import_pdf_action.triggered.connect(lambda checked, p=project, u=unit_name: self.import_floor_plan(p, u))
                    save_as_floor_plan_action = QAction("Save As...", self)
                    save_as_floor_plan_action.triggered.connect(lambda checked, p=project, u=unit_name: self.save_floor_plan_as(p, u))
                    floor_plan_menu.addAction(import_pdf_action)
                    floor_plan_menu.addAction(save_as_floor_plan_action)
                    floor_plan_split_btn.setMenu(floor_plan_menu)
                    floor_plan_split_btn.clicked.connect(lambda checked, p=project, u=unit_name: self.view_floor_plan(p, u))
                    self.tree.setItemWidget(unit_item, 8, floor_plan_split_btn)

                # Expand the project item to show unit names by default
                self.tree.expandItem(project_item)
                
                # Create project folder
                folder_name = get_project_folder_name(project)  # Changed here
                project_folder = os.path.join(get_project_dir(), folder_name)
                if not os.path.exists(project_folder):
                    os.makedirs(project_folder)
                    logger.info(f"Created project folder at {project_folder}")

                # Create subfolders for each unit with their own DOCX files
                for unit in project.units:
                    unit_folder = os.path.join(project_folder, sanitize_filename(unit))
                    if not os.path.exists(unit_folder):
                        os.makedirs(unit_folder)
                        logger.info(f"Created unit folder at {unit_folder}")
                    # Create "Floor plan" subfolder inside unit folder
                    floor_plan_subfolder = os.path.join(unit_folder, "Floor plan")
                    try:
                        os.makedirs(floor_plan_subfolder, exist_ok=True)
                        logger.info(f"Created 'Floor plan' subfolder at {floor_plan_subfolder}")
                    except Exception as e:
                        QMessageBox.critical(self, "Error", f"Failed to create 'Floor plan' subfolder for unit '{unit}':\n{str(e)}")
                        logger.error(f"Failed to create 'Floor plan' subfolder for unit '{unit}' at {floor_plan_subfolder}: {e}")
                        return
                    # Create DOCX files for the unit using templates
                    try:
                        innregulering_path = os.path.join(unit_folder, "Innregulering.docx")
                        sjekkliste_path = os.path.join(unit_folder, "Sjekkliste.docx")
                        shutil.copy(os.path.join(self.template_dir, "Innregulering.docx"), innregulering_path)
                        shutil.copy(os.path.join(self.template_dir, "Sjekkliste.docx"), sjekkliste_path)
                        logger.info(f"Copied Innregulering and Sjekkliste DOCX to {unit_folder}")
                    except Exception as e:
                        QMessageBox.critical(self, "Error", f"Failed to copy DOCX files for unit '{unit}':\n{str(e)}")
                        logger.error(f"Failed to copy DOCX files for unit '{unit}' in folder '{unit_folder}': {e}")
                        return

            else:
                # Create project folder
                folder_name = get_project_folder_name(project)  # Changed here
                project_folder = os.path.join(get_project_dir(), folder_name)
                if not os.path.exists(project_folder):
                    os.makedirs(project_folder)
                    logger.info(f"Created project folder at {project_folder}")

                # Create Innregulering and Sjekkliste DOCX in parent folder
                innregulering_path = os.path.join(project_folder, "Innregulering.docx")
                sjekkliste_path = os.path.join(project_folder, "Sjekkliste.docx")
                if not os.path.exists(innregulering_path):
                    Document().save(innregulering_path)
                    logger.info(f"Created Innregulering DOCX at {innregulering_path}")
                if not os.path.exists(sjekkliste_path):
                    Document().save(sjekkliste_path)
                    logger.info(f"Created Sjekkliste DOCX at {sjekkliste_path}")

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

                # Floor Plan(s) Split Button for Project
                floor_plan_split_btn = QToolButton()
                floor_plan_split_btn.setText("View")
                floor_plan_split_btn.setToolTip("View Floor Plan(s)")
                floor_plan_split_btn.setPopupMode(QToolButton.MenuButtonPopup)
                floor_plan_menu = QMenu(self)
                import_floor_plan_action = QAction("Import PDF", self)
                import_floor_plan_action.triggered.connect(lambda checked, p=project: self.import_floor_plan(p))
                save_as_floor_plan_action = QAction("Save As...", self)
                save_as_floor_plan_action.triggered.connect(lambda checked, p=project: self.save_floor_plan_as(p))
                floor_plan_menu.addAction(import_floor_plan_action)
                floor_plan_menu.addAction(save_as_floor_plan_action)
                floor_plan_split_btn.setMenu(floor_plan_menu)
                floor_plan_split_btn.clicked.connect(lambda checked, p=project: self.view_floor_plan(p))
                self.tree.setItemWidget(project_item, 8, floor_plan_split_btn)

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

                if not project.is_residential_complex:
                    # Set Completed Units to N/A
                    project_item.setText(3, "N/A")

                logger.debug(f"Added project '{project.name}' with status '{project.status}' to the tree.")

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
                            folder_name = get_project_folder_name(project)  # Changed here
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

    def save_docx_as(self, project, doc_type, unit_name=None):
        options = QFileDialog.Options()
        if unit_name:
            save_path, _ = QFileDialog.getSaveFileName(
                self,
                f"Save {doc_type} As for {unit_name}...",
                f"{sanitize_filename(project.name)}_{sanitize_filename(unit_name)}_{doc_type}.docx",
                "Word Documents (*.docx)",
                options=options
            )
        else:
            save_path, _ = QFileDialog.getSaveFileName(
                self,
                f"Save {doc_type} As...",
                f"{sanitize_filename(project.name)}_{doc_type}.docx",
                "Word Documents (*.docx)",
                options=options
            )
        if save_path:
            try:
                folder_name = get_project_folder_name(project)  # Changed here
                if unit_name:
                    floor_plan_file = os.path.join(get_project_dir(), folder_name, sanitize_filename(unit_name), f"{doc_type}.docx")
                else:
                    floor_plan_file = os.path.join(get_project_dir(), folder_name, f"{doc_type}.docx")
                if not os.path.exists(floor_plan_file):
                    QMessageBox.warning(self, "File Not Found", f"{doc_type}.docx does not exist.")
                    logger.warning(f"{doc_type}.docx not found for project '{project.name}'" + (f" and unit '{unit_name}'." if unit_name else "."))
                    return
                shutil.copy(floor_plan_file, save_path)
                QMessageBox.information(self, "Success", f"{doc_type} saved successfully at:\n{save_path}")
                logger.info(f"{doc_type} saved as {save_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save {doc_type}:\n{str(e)}")
                logger.error(f"Failed to save {doc_type} for project '{project.name}'" + (f" and unit '{unit_name}': {e}" if unit_name else f": {e}"))

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

    def view_docx(self, project, doc_type, unit_name=None):
        if unit_name:
            folder_name = get_project_folder_name(project)  # Changed here
            docx_file = os.path.join(get_project_dir(), folder_name, sanitize_filename(unit_name), f"{doc_type}.docx")
        else:
            folder_name = get_project_folder_name(project)  # Changed here
            docx_file = os.path.join(get_project_dir(), folder_name, f"{doc_type}.docx")

        if not os.path.exists(docx_file):
            QMessageBox.warning(self, "DOCX Error", f"{doc_type}.docx does not exist for this {'unit ' + unit_name if unit_name else 'project'}.")
            logger.warning(f"{doc_type}.docx not found for project '{project.name}'" + (f" and unit '{unit_name}'." if unit_name else "."))
            return

        success, message = open_docx_file(docx_file)
        if not success:
            QMessageBox.warning(self, "DOCX Error", message)
            logger.error(f"Failed to open {doc_type}.docx for project '{project.name}'" + (f" and unit '{unit_name}': {message}" if unit_name else f": {message}"))

    def import_floor_plan(self, project, unit_name=None):
        options = QFileDialog.Options()
        if unit_name:
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                f"Import Floor Plan PDF for {unit_name}",
                "",
                "PDF Files (*.pdf)",
                options=options
            )
            if file_path:
                try:
                    folder_name = get_project_folder_name(project)  # Changed here
                    unit_folder = os.path.join(get_project_dir(), folder_name, sanitize_filename(unit_name), "Floor plan")
                    target_file = os.path.join(unit_folder, "FloorPlan.pdf")
                    shutil.copy(file_path, target_file)
                    QMessageBox.information(self, "Success", f"Floor Plan imported successfully to '{target_file}'.")
                    logger.info(f"Imported Floor Plan PDF to {target_file}")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to import Floor Plan PDF:\n{str(e)}")
                    logger.error(f"Failed to import Floor Plan PDF for unit '{unit_name}' in project '{project.name}': {e}")
        else:
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Import Floor Plan PDF",
                "",
                "PDF Files (*.pdf)",
                options=options
            )
            if file_path:
                try:
                    folder_name = get_project_folder_name(project)  # Changed here
                    floor_plan_folder = os.path.join(get_project_dir(), folder_name, "Floor plan")
                    target_file = os.path.join(floor_plan_folder, "FloorPlan.pdf")
                    shutil.copy(file_path, target_file)
                    QMessageBox.information(self, "Success", f"Floor Plan imported successfully to '{target_file}'.")
                    logger.info(f"Imported Floor Plan PDF to {target_file}")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to import Floor Plan PDF:\n{str(e)}")
                    logger.error(f"Failed to import Floor Plan PDF for project '{project.name}': {e}")

    def view_floor_plan(self, project, unit_name=None):
        if project.is_residential_complex and not unit_name:
            QMessageBox.warning(self, "Floor Plan Error", "This project is a residential complex. Please select a unit to view its floor plan.")
            logger.warning(f"Attempted to view project-level floor plan for residential project '{project.name}'.")
            return

        try:
            folder_name = get_project_folder_name(project)  # Changed here

            if unit_name:
                floor_plan_file = os.path.join(
                    get_project_dir(),
                    folder_name,
                    sanitize_filename(unit_name),
                    "Floor plan",
                    "FloorPlan.pdf"
                )
            else:
                floor_plan_file = os.path.join(
                    get_project_dir(),
                    folder_name,
                    "Floor plan",
                    "FloorPlan.pdf"
                )

            if not os.path.exists(floor_plan_file):
                QMessageBox.warning(self, "Floor Plan Error", "Floor Plan PDF does not exist.")
                logger.warning(f"Floor Plan PDF not found for project '{project.name}'" + (f" and unit '{unit_name}'." if unit_name else "."))
                return

            try:
                if sys.platform == "win32":
                    os.startfile(floor_plan_file)
                elif sys.platform == "darwin":
                    subprocess.call(["open", floor_plan_file])
                else:
                    subprocess.call(["xdg-open", floor_plan_file])
                logger.info(f"Opened Floor Plan PDF: {floor_plan_file}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to open Floor Plan PDF:\n{str(e)}")
                logger.error(f"Failed to open Floor Plan PDF '{floor_plan_file}': {e}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while trying to view the Floor Plan:\n{str(e)}")
            logger.error(f"Error in view_floor_plan for project '{project.name}': {e}")

    def save_floor_plan_as(self, project, unit_name=None):
        options = QFileDialog.Options()
        if unit_name:
            save_path, _ = QFileDialog.getSaveFileName(
                self,
                f"Save Floor Plan As for {unit_name}...",
                f"{sanitize_filename(project.name)}_{sanitize_filename(unit_name)}_FloorPlan.pdf",
                "PDF Files (*.pdf)",
                options=options
            )
        else:
            save_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save Floor Plan As...",
                f"{sanitize_filename(project.name)}_FloorPlan.pdf",
                "PDF Files (*.pdf)",
                options=options
            )
        if save_path:
            try:
                folder_name = get_project_folder_name(project)  # Changed here
                if unit_name:
                    floor_plan_file = os.path.join(get_project_dir(), folder_name, sanitize_filename(unit_name), "Floor plan", "FloorPlan.pdf")
                else:
                    floor_plan_file = os.path.join(get_project_dir(), folder_name, "Floor plan", "FloorPlan.pdf")
                if not os.path.exists(floor_plan_file):
                    QMessageBox.warning(self, "File Not Found", "Floor Plan PDF does not exist.")
                    logger.warning(f"Floor Plan PDF not found for project '{project.name}'" + (f" and unit '{unit_name}'." if unit_name else "."))
                    return
                shutil.copy(floor_plan_file, save_path)
                QMessageBox.information(self, "Success", f"Floor Plan saved successfully at:\n{save_path}")
                logger.info(f"Floor Plan saved as {save_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save Floor Plan:\n{str(e)}")
                logger.error(f"Failed to save Floor Plan for project '{project.name}'" + (f" and unit '{unit_name}': {e}" if unit_name else f": {e}"))
