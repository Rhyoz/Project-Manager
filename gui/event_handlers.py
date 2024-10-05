# File: gui/event_handlers.py

from PyQt5.QtWidgets import QMessageBox, QMenu, QAction, QFileDialog
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QIcon
import os
import shutil
import sys
import subprocess
from datetime import datetime

from utils import (
    sanitize_filename, open_docx_file, get_project_dir, get_template_dir, get_project_folder_name
)
from database import UnitModel, ProjectModel
from logger import get_logger
from docx import Document
from docx.enum.section import WD_ORIENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches

logger = get_logger(__name__)

def handle_project_delete(db, project_id, parent_widget):
    project = db.get_project_by_id(project_id)
    if project:
        reply = QMessageBox.question(
            parent_widget,
            "Confirm Deletion",
            f"Are you sure you want to delete project '{project.name}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            try:
                # Delete project folder
                folder_name = get_project_folder_name(project)
                project_folder = os.path.join(get_project_dir(), folder_name)
                if os.path.exists(project_folder):
                    shutil.rmtree(project_folder)
                    logger.info(f"Deleted project folder at {project_folder}")
                # Delete project from database
                db.delete_project(project.id)
                parent_widget.load_projects()
                QMessageBox.information(parent_widget, "Deleted", f"Project '{project.name}' has been deleted.")
                logger.info(f"Deleted project '{project.name}' with ID {project.id}")
            except Exception as e:
                QMessageBox.critical(parent_widget, "Error", f"Failed to delete project: {str(e)}")
                logger.error(f"Failed to delete project ID {project.id}: {e}")

def handle_toggle_unit_status(db, project, unit_name, state, parent_widget):
    is_done = state == Qt.Checked
    # Fetch unit by name and project
    unit = db.session.query(UnitModel).join(ProjectModel).filter(
        ProjectModel.id == project.id,
        UnitModel.name == unit_name
    ).first()
    if unit:
        try:
            db.toggle_unit_status(project.id, unit.id, is_done)
            parent_widget.load_projects()
        except Exception as e:
            QMessageBox.critical(parent_widget, "Error", f"Failed to update unit status: {str(e)}")
            logger.error(f"Failed to update unit status for Unit '{unit_name}' in Project ID {project.id}: {e}")

def handle_move_project(db, project, new_status, parent_widget):
    try:
        project.status = new_status
        if new_status == "Finished":
            project.end_date = datetime.now().strftime("%Y-%m-%d")
        else:
            project.end_date = None
        db.update_project(project)
        parent_widget.load_projects()
        QMessageBox.information(parent_widget, "Success", f"Project '{project.name}' moved to '{new_status}'.")
        logger.info(f"Project '{project.name}' moved to '{new_status}'.")
    except Exception as e:
        QMessageBox.critical(parent_widget, "Error", f"Failed to move project: {str(e)}")
        logger.error(f"Failed to move project '{project.name}' to '{new_status}': {e}")

def handle_import_floor_plan(project, unit_name, parent_widget):
    options = QFileDialog.Options()
    file_path, _ = QFileDialog.getOpenFileName(
        parent_widget,
        "Import Floor Plan PDF",
        "",
        "PDF Files (*.pdf)",
        options=options
    )
    if file_path:
        try:
            folder_name = get_project_folder_name(project)
            if unit_name:
                unit_folder = os.path.join(get_project_dir(), folder_name, sanitize_filename(unit_name), "Floor plan")
                target_file = os.path.join(unit_folder, "FloorPlan.pdf")
            else:
                floor_plan_folder = os.path.join(get_project_dir(), folder_name, "Floor plan")
                target_file = os.path.join(floor_plan_folder, "FloorPlan.pdf")
            shutil.copy(file_path, target_file)
            QMessageBox.information(parent_widget, "Success", f"Floor Plan imported successfully to '{target_file}'.")
            logger.info(f"Imported Floor Plan PDF to {target_file}")
        except Exception as e:
            QMessageBox.critical(parent_widget, "Error", f"Failed to import Floor Plan PDF:\n{str(e)}")
            logger.error(f"Failed to import Floor Plan PDF for project '{project.name}'" + (f" and unit '{unit_name}': {e}" if unit_name else f": {e}"))

def handle_import_master_floor_plan(project, parent_widget):
    options = QFileDialog.Options()
    file_path, _ = QFileDialog.getOpenFileName(
        parent_widget,
        "Import Master Floor Plan PDF",
        "",
        "PDF Files (*.pdf)",
        options=options
    )
    if file_path:
        try:
            folder_name = get_project_folder_name(project)
            master_folder = os.path.join(get_project_dir(), folder_name, "Master")
            target_file = os.path.join(master_folder, "MasterFloorPlan.pdf")
            shutil.copy(file_path, target_file)
            QMessageBox.information(parent_widget, "Success", f"Master Floor Plan imported successfully to '{target_file}'.")
            logger.info(f"Imported Master Floor Plan PDF to {target_file}")
        except Exception as e:
            QMessageBox.critical(parent_widget, "Error", f"Failed to import Master Floor Plan PDF:\n{str(e)}")
            logger.error(f"Failed to import Master Floor Plan PDF for project '{project.name}': {e}")

# Additional event handlers can be added here as needed

