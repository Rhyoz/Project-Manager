# gui/add_project_dialog.py
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QDateEdit,
    QComboBox, QCheckBox, QSpinBox, QPushButton, QMessageBox, QHBoxLayout, QTextEdit, QWidget, QGridLayout
)
from PyQt5.QtCore import Qt, QDate, QThread
from gui.base_projects_tab import BaseProjectsTab
from project import Project
from utils import (
    sanitize_filename,
    get_template_dir,
    check_template_files,
    open_docx_file,
    get_project_dir,
    load_main_contractors,
    add_main_contractor,
    get_docx_temp_dir
)
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
        self.units_input.valueChanged.connect(self.generate_unit_name_fields)
        self.form_layout.addRow("Number of Units:", self.units_input)

        # Residential Details (New Field)
        self.residential_details_input = QTextEdit()
        self.residential_details_input.setPlaceholderText("Enter residential details here...")
        self.residential_details_input.setEnabled(False)  # Enabled only if Residential Complex is checked
        self.form_layout.addRow("Residential Details:", self.residential_details_input)

        # Extra Field
        self.extra_input = QLineEdit()
        self.form_layout.addRow("Extra:", self.extra_input)

        # Main Contractor Checkbox
        self.main_contractor_checkbox = QCheckBox("Add Main Contractor")
        self.main_contractor_checkbox.stateChanged.connect(self.toggle_main_contractor)
        self.form_layout.addRow(self.main_contractor_checkbox)

        # Main Contractor ComboBox
        self.main_contractor_input = QComboBox()
        self.main_contractor_input.setEditable(True)
        self.main_contractor_input.addItems(load_main_contractors())
        self.main_contractor_input.setEnabled(False)
        self.main_contractor_input.lineEdit().setPlaceholderText("Select or enter Main Contractor")
        self.form_layout.addRow("Main Contractor:", self.main_contractor_input)

        # Unit Names Layout
        self.unit_names_widget = QWidget()
        self.unit_names_layout = QVBoxLayout()
        self.unit_names_widget.setLayout(self.unit_names_layout)
        self.unit_names_widget.setVisible(False)
        self.form_layout.addRow("Unit Names:", self.unit_names_widget)

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
        self.unit_names_widget.setVisible(is_checked)
        if not is_checked:
            # Clear unit names fields
            for i in reversed(range(self.unit_names_layout.count())):
                widget_to_remove = self.unit_names_layout.itemAt(i).widget()
                if widget_to_remove is not None:
                    widget_to_remove.setParent(None)

    def toggle_main_contractor(self, state):
        is_checked = state == Qt.Checked
        self.main_contractor_input.setEnabled(is_checked)

    def generate_unit_name_fields(self, value):
        # Clear existing fields
        for i in reversed(range(self.unit_names_layout.count())):
            widget_to_remove = self.unit_names_layout.itemAt(i).widget()
            if widget_to_remove is not None:
                widget_to_remove.setParent(None)
        # Generate new fields
        self.unit_line_edits = []
        for i in range(1, value + 1):
            line_edit = QLineEdit()
            line_edit.setText(str(i))
            self.unit_names_layout.addWidget(line_edit)
            self.unit_line_edits.append(line_edit)

    def save_project(self):
        # Gather data from input fields
        name = self.name_input.text().strip()
        number = self.number_input.text().strip()
        worker = self.worker_input.currentText().strip()
        start_date = self.start_date_input.date().toPyDate()
        end_date = self.end_date_input.date().toPyDate() if self.end_date_input.date().isValid() else None
        status = self.status_input.currentText()
        is_residential = self.residential_checkbox.isChecked()
        units = []
        if is_residential:
            for line_edit in self.unit_line_edits:
                unit_name = line_edit.text().strip()
                if unit_name:
                    units.append(unit_name)
        extra = self.extra_input.text().strip()

        # Main Contractor
        main_contractor = self.main_contractor_input.currentText().strip() if self.main_contractor_checkbox.isChecked() else None

        # Validation
        if not name and not number:
            QMessageBox.warning(self, "Validation Error", "At least one of Project Name or Project Number must be provided.")
            return

        if end_date and end_date < start_date:
            QMessageBox.warning(self, "Validation Error", "End Date cannot be earlier than Start Date.")
            return

        if is_residential:
            if not units:
                QMessageBox.warning(self, "Validation Error", "At least one unit name must be provided for a residential complex.")
                return
            if len(units) != self.units_input.value():
                QMessageBox.warning(self, "Validation Error", "Number of unit names does not match the number of units specified.")
                return
            if len(units) != len(set(units)):
                QMessageBox.warning(self, "Validation Error", "Unit names must be unique.")
                return

        if main_contractor:
            if main_contractor not in load_main_contractors():
                # Ask user to confirm adding a new contractor
                reply = QMessageBox.question(
                    self,
                    "Add New Contractor",
                    f"'{main_contractor}' is not in the existing list. Do you want to add it?",
                    QMessageBox.Yes | QMessageBox.No
                )
                if reply == QMessageBox.Yes:
                    try:
                        add_main_contractor(main_contractor)
                        QMessageBox.information(self, "Success", f"'{main_contractor}' has been added to the Main Contractors list.")
                        # Update the ComboBox with the new contractor
                        self.main_contractor_input.addItem(main_contractor)
                        logger.info(f"Added new main contractor: {main_contractor}")
                    except Exception as e:
                        QMessageBox.critical(self, "Error", f"Failed to add new contractor: {str(e)}")
                        logger.error(f"Failed to add main contractor '{main_contractor}': {e}")
                        return

        # Create Project instance without 'id'
        project = Project(
            name=name,
            number=number,
            start_date=start_date.strftime("%Y-%m-%d"),
            end_date=end_date.strftime("%Y-%m-%d") if end_date else None,
            status=status,
            is_residential_complex=is_residential,
            number_of_units=self.units_input.value() if is_residential else 0,
            worker=worker,
            residential_details=self.residential_details_input.toPlainText().strip() if is_residential else "",
            extra=extra,
            main_contractor=main_contractor,  # Set New Attribute
            units=units  # Set Unit Names
        )

        # Add project to database
        try:
            project_id = self.db.add_project(project)
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Failed to add project: {str(e)}")
            return

        # Create Project Folder
        folder_name = ""
        if main_contractor:
            folder_name = sanitize_filename(f"{main_contractor} - {name} - {number}") if (name or number) else f"{main_contractor} - Project_{project_id}"
        else:
            folder_name = sanitize_filename(f"{name}_{number}") if (name or number) else f"Project_{project_id}"
        project_folder = os.path.join(get_project_dir(), folder_name)
        try:
            os.makedirs(project_folder, exist_ok=True)
            logger.info(f"Created project folder at {project_folder}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create project folder:\n{str(e)}")
            logger.error(f"Failed to create project folder at {project_folder}: {e}")
            return

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
        pdf_path = os.path.join(get_docx_temp_dir(), f"{project.name}_{project.number}_Data.pdf")

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
