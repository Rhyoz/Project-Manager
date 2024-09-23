# gui/detailed_view_tab.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QFormLayout, QLineEdit, QDateEdit, QComboBox, QCheckBox, QSpinBox, QPushButton, QMessageBox, QHBoxLayout
from PyQt5.QtCore import Qt, QDate
from project import Project
from utils import sanitize_filename
import os
import shutil

class DetailedViewTab(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.current_project = None

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.form_layout = QFormLayout()

        self.project_selector = QComboBox()
        self.load_project_selector()
        self.project_selector.currentIndexChanged.connect(self.load_selected_project)
        self.form_layout.addRow("Select Project:", self.project_selector)

        self.name_input = QLineEdit()
        self.form_layout.addRow("Project Name:", self.name_input)

        self.number_input = QLineEdit()
        self.form_layout.addRow("Project Number:", self.number_input)

        self.worker_input = QLineEdit()  # New input field
        self.form_layout.addRow("Worker:", self.worker_input)  # New row

        self.start_date_input = QDateEdit(calendarPopup=True)
        self.start_date_input.setDisplayFormat("yyyy-MM-dd")
        self.form_layout.addRow("Start Date:", self.start_date_input)

        self.end_date_input = QDateEdit(calendarPopup=True)
        self.end_date_input.setDisplayFormat("yyyy-MM-dd")
        self.end_date_input.setSpecialValueText("")
        self.end_date_input.setDateRange(QDate(1900, 1, 1), QDate(9999, 12, 31))
        self.end_date_input.setDate(QDate())
        self.form_layout.addRow("End Date:", self.end_date_input)

        self.status_input = QComboBox()
        self.status_input.addItems(["Active", "On Hold", "Complete", "Finished"])
        self.form_layout.addRow("Status:", self.status_input)

        self.residential_checkbox = QCheckBox("Residential Complex")
        self.residential_checkbox.stateChanged.connect(self.toggle_units)
        self.form_layout.addRow(self.residential_checkbox)

        self.units_input = QSpinBox()
        self.units_input.setRange(1, 1000)
        self.units_input.setEnabled(False)
        self.form_layout.addRow("Number of Units:", self.units_input)

        self.layout.addLayout(self.form_layout)

        # Buttons
        self.button_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save Changes")
        self.save_btn.clicked.connect(self.save_changes)
        self.layout.addLayout(self.button_layout)

    def load_project_selector(self):
        self.project_selector.clear()
        projects = self.db.load_projects()
        for project in projects:
            display_text = f"{project.name} ({project.number})" if project.name and project.number else project.name or project.number
            self.project_selector.addItem(display_text, project.id)

    def load_selected_project(self):
        project_id = self.project_selector.currentData()
        if project_id is None:
            return
        project = self.db.get_project_by_id(project_id)
        if project:
            self.current_project = project
            self.name_input.setText(project.name)
            self.number_input.setText(project.number)
            self.worker_input.setText(project.worker)  # Set worker
            self.start_date_input.setDate(QDate.fromString(project.start_date, "yyyy-MM-dd"))
            if project.end_date:
                self.end_date_input.setDate(QDate.fromString(project.end_date, "yyyy-MM-dd"))
            else:
                self.end_date_input.setDate(QDate())
            self.status_input.setCurrentText(project.status)
            self.residential_checkbox.setChecked(project.is_residential_complex)
            self.units_input.setValue(project.number_of_units)
            self.units_input.setEnabled(project.is_residential_complex)

    def toggle_units(self, state):
        self.units_input.setEnabled(state == Qt.Checked)

    def save_changes(self):
        if not self.current_project:
            QMessageBox.warning(self, "No Project Selected", "Please select a project to edit.")
            return

        name = self.name_input.text().strip()
        number = self.number_input.text().strip()
        worker = self.worker_input.text().strip()  # Get worker input
        start_date = self.start_date_input.date().toPyDate()
        end_date = self.end_date_input.date().toPyDate() if self.end_date_input.date().isValid() else None
        status = self.status_input.currentText()
        is_residential = self.residential_checkbox.isChecked()
        units = self.units_input.value() if is_residential else 0

        # Validation
        if not name and not number:
            QMessageBox.warning(self, "Validation Error", "At least one of Project Name or Project Number must be provided.")
            return

        if end_date and end_date < start_date:
            QMessageBox.warning(self, "Validation Error", "End Date cannot be earlier than Start Date.")
            return

        old_folder_name = sanitize_filename(f"{self.current_project.name}_{self.current_project.number}")
        new_folder_name = sanitize_filename(f"{name}_{number}") if name or number else f"Project_{self.current_project.id}"
        old_project_folder = os.path.join("Boligventilasjon - Prosjekter", old_folder_name)
        new_project_folder = os.path.join("Boligventilasjon - Prosjekter", new_folder_name)

        # Update project details
        self.current_project.name = name
        self.current_project.number = number
        self.current_project.worker = worker  # Update worker
        self.current_project.start_date = start_date
        self.current_project.end_date = end_date
        self.current_project.status = status
        self.current_project.is_residential_complex = is_residential
        self.current_project.number_of_units = units

        self.db.update_project(self.current_project)

        # Rename project folder if name or number changed
        if old_folder_name != new_folder_name:
            if os.path.exists(old_project_folder):
                os.rename(old_project_folder, new_project_folder)

        QMessageBox.information(self, "Success", "Project details updated successfully.")
        self.load_project_selector()
