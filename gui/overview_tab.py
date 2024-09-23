# gui/overview_tab.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QHBoxLayout, QMessageBox
from PyQt5.QtCore import Qt
from gui.add_project_dialog import AddProjectDialog
from utils import sanitize_filename
import sys
import os
import shutil
import subprocess
from pdf_converter import PDFConverter
from PyQt5.QtCore import QThread

class OverviewTab(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Add New Project Button
        self.add_project_btn = QPushButton("Add New Project")
        self.add_project_btn.clicked.connect(self.open_add_project_dialog)
        self.layout.addWidget(self.add_project_btn)

        # Projects Table
        self.table = QTableWidget()
        self.table.setColumnCount(11)  # Updated column count
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
            "Move to Complete",
            "Move to Finished"
        ])
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.layout.addWidget(self.table)

        self.load_projects()

    def load_projects(self):
        self.table.setRowCount(0)
        projects = self.db.load_projects(status="Active")
        for project in projects:
            row_position = self.table.rowCount()
            self.table.insertRow(row_position)

            self.table.setItem(row_position, 0, QTableWidgetItem(project.name))
            self.table.setItem(row_position, 1, QTableWidgetItem(project.number))
            complex_text = "Yes" if project.is_residential_complex else "No"
            self.table.setItem(row_position, 2, QTableWidgetItem(complex_text))
            self.table.setItem(row_position, 3, QTableWidgetItem(project.start_date))
            self.table.setItem(row_position, 4, QTableWidgetItem(project.end_date if project.end_date else ""))
            self.table.setItem(row_position, 5, QTableWidgetItem(project.status))
            self.table.setItem(row_position, 6, QTableWidgetItem(project.worker))  # Set worker

            # Innregulering Button
            innregulering_btn = QPushButton("View PDF")
            innregulering_btn.clicked.connect(lambda checked, p=project: self.view_pdf(p, "Innregulering"))
            self.table.setCellWidget(row_position, 7, innregulering_btn)

            # Sjekkliste Button
            sjekkliste_btn = QPushButton("View PDF")
            sjekkliste_btn.clicked.connect(lambda checked, p=project: self.view_pdf(p, "Sjekkliste"))
            self.table.setCellWidget(row_position, 8, sjekkliste_btn)

            # Move to Complete Button
            move_complete_btn = QPushButton("Complete")
            move_complete_btn.setStyleSheet("background-color: yellow")
            move_complete_btn.clicked.connect(lambda checked, p=project: self.move_to_complete(p))
            self.table.setCellWidget(row_position, 9, move_complete_btn)

            # Move to Finished Button
            move_finished_btn = QPushButton("Finish")
            move_finished_btn.setStyleSheet("background-color: yellow")
            move_finished_btn.clicked.connect(lambda checked, p=project: self.move_to_finished(p))
            self.table.setCellWidget(row_position, 10, move_finished_btn)

    def open_add_project_dialog(self):
        dialog = AddProjectDialog(self.db)
        if dialog.exec_() == dialog.Accepted:
            self.load_projects()

    def view_pdf(self, project, doc_type):
        folder_name = sanitize_filename(f"{project.name}_{project.number}")
        project_folder = os.path.join("Boligventilasjon - Prosjekter", folder_name)
        pdf_file = os.path.join(project_folder, f"{doc_type}.pdf")

        if not os.path.exists(pdf_file):
            QMessageBox.warning(self, "PDF Not Found", f"The PDF for {doc_type} does not exist.")
            return

        try:
            if sys.platform.startswith('darwin'):
                subprocess.call(('open', pdf_file))
            elif os.name == 'nt':
                os.startfile(pdf_file)
            elif os.name == 'posix':
                subprocess.call(('xdg-open', pdf_file))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open PDF: {str(e)}")

    def move_to_complete(self, project):
        project.status = "Complete"
        self.db.update_project(project)
        self.load_projects()
        QMessageBox.information(self, "Status Updated", f"Project '{project.name}' moved to Complete.")

    def move_to_finished(self, project):
        project.status = "Finished"
        self.db.update_project(project)
        self.load_projects()
        QMessageBox.information(self, "Status Updated", f"Project '{project.name}' moved to Finished.")
