# gui/add_project_dialog.py
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QDateEdit, QComboBox, QCheckBox, QSpinBox, QPushButton, QMessageBox, QHBoxLayout
from PyQt5.QtCore import Qt, QDate
from project import Project
from utils import sanitize_filename
import os
import shutil

class AddProjectDialog(QDialog):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.setWindowTitle("Add New Project")
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.form_layout = QFormLayout()

        self.name_input = QLineEdit()
        self.form_layout.addRow("Project Name:", self.name_input)

        self.number_input = QLineEdit()
        self.form_layout.addRow("Project Number:", self.number_input)

        self.worker_input = QLineEdit()  # New input field
        self.form_layout.addRow("Worker:", self.worker_input)  # New row

        self.start_date_input = QDateEdit(calendarPopup=True)
        self.start_date_input.setDate(QDate.currentDate())
        self.form_layout.addRow("Start Date:", self.start_date_input)

        self.end_date_input = QDateEdit(calendarPopup=True)
        self.end_date_input.setDate(QDate.currentDate())
        self.end_date_input.setSpecialValueText("")
        self.end_date_input.setDateRange(QDate.currentDate(), QDate(9999, 12, 31))
        self.end_date_input.setDate(QDate())
        self.end_date_input.setDisplayFormat("yyyy-MM-dd")
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
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.save_project)
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        self.button_layout.addWidget(self.save_btn)
        self.button_layout.addWidget(self.cancel_btn)
        self.layout.addLayout(self.button_layout)

    def toggle_units(self, state):
        self.units_input.setEnabled(state == Qt.Checked)

    def save_project(self):
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

        project = Project(
            name=name,
            number=number,
            start_date=start_date,
            end_date=end_date,
            status=status,
            is_residential_complex=is_residential,
            number_of_units=units,
            worker=worker  # Set worker
        )

        project_id = self.db.add_project(project)

        # Create Project Folder
        folder_name = sanitize_filename(f"{name}_{number}") if name or number else f"Project_{project_id}"
        project_folder = os.path.join("Boligventilasjon - Prosjekter", folder_name)
        os.makedirs(project_folder, exist_ok=True)

        # Copy template files
        template_dir = "Template"
        for file in os.listdir(template_dir):
            if file.endswith(".xlsx"):
                shutil.copy(os.path.join(template_dir, file), project_folder)

        QMessageBox.information(self, "Success", "Project added successfully.")
        self.accept()
