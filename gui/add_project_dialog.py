# gui/add_project_dialog.py
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QDateEdit,
    QComboBox, QCheckBox, QSpinBox, QPushButton, QMessageBox, QHBoxLayout, QTextEdit
)
from PyQt5.QtCore import Qt, QDate
from project import Project
from utils import sanitize_filename, get_template_dir, check_template_files, open_docx_file, get_project_dir
from logger import get_logger
from pdf_converter import PDFConverter
import os
import shutil
from datetime import datetime

logger = get_logger(__name__)

class AddProjectDialog(QDialog):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.setWindowTitle("Add New Project")
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.form_layout = QFormLayout()

        # Project Name
        self.name_input = QLineEdit()
        self.form_layout.addRow("Project Name:", self.name_input)

        # Project Number
        self.number_input = QLineEdit()
        self.form_layout.addRow("Project Number:", self.number_input)

        # Worker Selection
        self.worker_input = QComboBox()
        self.worker_input.addItems(["Alex", "William"])
        self.worker_input.setCurrentText("Alex")  # Default to "Alex"
        self.form_layout.addRow("Worker:", self.worker_input)

        # Start Date
        self.start_date_input = QDateEdit(calendarPopup=True)
        self.start_date_input.setDate(QDate.currentDate())
        self.start_date_input.setDisplayFormat("dd-MM-yyyy")
        self.form_layout.addRow("Start Date:", self.start_date_input)

        # End Date
        self.end_date_input = QDateEdit(calendarPopup=True)
        self.end_date_input.setSpecialValueText("")
        self.end_date_input.setDateRange(QDate.currentDate(), QDate(9999, 12, 31))
        self.end_date_input.setDate(QDate())  # Blank by default
        self.end_date_input.setDisplayFormat("dd-MM-yyyy")
        self.end_date_input.setEnabled(False)  # Not required to be filled in
        self.form_layout.addRow("End Date:", self.end_date_input)

        # Status Selection
        self.status_input = QComboBox()
        self.status_input.addItems(["Active", "Awaiting Completion", "Paused", "Completed", "Finished"])
        self.form_layout.addRow("Status:", self.status_input)

        # Residential Complex Checkbox
        self.residential_checkbox = QCheckBox("Residential Complex")
        self.residential_checkbox.stateChanged.connect(self.toggle_units)
        self.form_layout.addRow(self.residential_checkbox)

        # Number of Units
        self.units_input = QSpinBox()
        self.units_input.setRange(1, 1000)
        self.units_input.setEnabled(False)
        self.form_layout.addRow("Number of Units:", self.units_input)

        # Residential Details (New Field)
        self.residential_details_input = QTextEdit()
        self.residential_details_input.setPlaceholderText("Enter residential details here...")
        self.residential_details_input.setEnabled(False)  # Enabled only if Residential Complex is checked
        self.form_layout.addRow("Residential Details:", self.residential_details_input)

        # Extra Field
        self.extra_input = QLineEdit()
        self.form_layout.addRow("Extra:", self.extra_input)

        self.layout.addLayout(self.form_layout)

        # Buttons Layout
        self.button_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.save_project)
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        self.button_layout.addWidget(self.save_btn)
        self.button_layout.addWidget(self.cancel_btn)
        self.layout.addLayout(self.button_layout)

    def toggle_units(self, state):
        is_checked = state == Qt.Checked
        self.units_input.setEnabled(is_checked)
        self.residential_details_input.setEnabled(is_checked)  # Enable/disable residential details input

    def save_project(self):
        # Gather data from input fields
        name = self.name_input.text().strip()
        number = self.number_input.text().strip()
        worker = self.worker_input.currentText().strip()
        start_date = self.start_date_input.date().toPyDate()
        end_date = self.end_date_input.date().toPyDate() if self.end_date_input.date().isValid() else None
        status = self.status_input.currentText()
        is_residential = self.residential_checkbox.isChecked()
        units = self.units_input.value() if is_residential else 0
        residential_details = self.residential_details_input.toPlainText().strip() if is_residential else ""
        extra = self.extra_input.text().strip()

        # Validation
        if not name and not number:
            QMessageBox.warning(self, "Validation Error", "At least one of Project Name or Project Number must be provided.")
            return

        if end_date and end_date < start_date:
            QMessageBox.warning(self, "Validation Error", "End Date cannot be earlier than Start Date.")
            return

        if is_residential and not residential_details:
            QMessageBox.warning(self, "Validation Error", "Residential details must be provided for a residential complex.")
            return

        # Create Project instance without 'id'
        project = Project(
            name=name,
            number=number,
            start_date=start_date.strftime("%Y-%m-%d"),
            end_date=end_date.strftime("%Y-%m-%d") if end_date else None,
            status=status,
            is_residential_complex=is_residential,
            number_of_units=units,
            worker=worker,
            residential_details=residential_details,
            extra=extra
        )

        # Add project to database
        try:
            project_id = self.db.add_project(project)
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Failed to add project: {str(e)}")
            return

        # Create Project Folder
        folder_name = sanitize_filename(f"{name}_{number}") if name or number else f"Project_{project_id}"
        project_folder = os.path.join(get_project_dir(), folder_name)
        os.makedirs(project_folder, exist_ok=True)

        # Check for Template directory and required files
        valid, message = check_template_files()
        if not valid:
            QMessageBox.critical(self, "Template Error", message)
            logger.error(f"Template check failed: {message}")
            return

        # Define Template directory path
        template_dir = get_template_dir()

        # Copy the required template files into the project folder
        try:
            required_files = ["Innregulering.docx", "Sjekkliste.docx"]
            for file in required_files:
                shutil.copy(os.path.join(template_dir, file), project_folder)
            logger.info(f"Copied templates to {project_folder}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to copy template files:\n{str(e)}")
            logger.error(f"Failed to copy templates to {project_folder}: {e}")
            return

        # Optional: Initiate PDF conversion if needed
        # self.convert_pdf(project)

        QMessageBox.information(self, "Success", "Project added successfully.")
        logger.info(f"Project added successfully: {project.name} ({project.number})")
        self.accept()

    def convert_pdf(self, project):
        # Example method to convert a related Excel file to PDF
        excel_path = os.path.join(get_project_dir(), sanitize_filename(f"{project.name}_{project.number}"), "Data.xlsx")
        pdf_path = os.path.join(get_project_dir(), sanitize_filename(f"{project.name}_{project.number}"), "Data.pdf")

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
