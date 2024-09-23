# gui/finished_projects_tab.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QMessageBox
from PyQt5.QtCore import Qt
from utils import sanitize_filename
import sys
import subprocess
import os

class FinishedProjectsTab(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Projects Table
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "Project Name",
            "Project Number",
            "Start Date",
            "End Date",
            "Status",
            "Innregulering",
            "Sjekkliste",
            "Move to Active",
            "Move to Complete"
        ])
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.layout.addWidget(self.table)

        self.load_projects()

    def load_projects(self):
        self.table.setRowCount(0)
        projects = self.db.load_projects(status="Finished")
        for project in projects:
            row_position = self.table.rowCount()
            self.table.insertRow(row_position)

            self.table.setItem(row_position, 0, QTableWidgetItem(project.name))
            self.table.setItem(row_position, 1, QTableWidgetItem(project.number))
            self.table.setItem(row_position, 2, QTableWidgetItem(project.start_date))
            self.table.setItem(row_position, 3, QTableWidgetItem(project.end_date if project.end_date else ""))
            self.table.setItem(row_position, 4, QTableWidgetItem(project.status))

            # Innregulering Button
            innregulering_btn = QPushButton("View PDF")
            innregulering_btn.clicked.connect(lambda checked, p=project: self.view_pdf(p, "Innregulering"))
            self.table.setCellWidget(row_position, 5, innregulering_btn)

            # Sjekkliste Button
            sjekkliste_btn = QPushButton("View PDF")
            sjekkliste_btn.clicked.connect(lambda checked, p=project: self.view_pdf(p, "Sjekkliste"))
            self.table.setCellWidget(row_position, 6, sjekkliste_btn)

            # Move to Active Button
            move_active_btn = QPushButton("Active")
            move_active_btn.setStyleSheet("background-color: yellow")
            move_active_btn.clicked.connect(lambda checked, p=project: self.move_to_active(p))
            self.table.setCellWidget(row_position, 7, move_active_btn)

            # Move to Complete Button
            move_complete_btn = QPushButton("Complete")
            move_complete_btn.setStyleSheet("background-color: yellow")
            move_complete_btn.clicked.connect(lambda checked, p=project: self.move_to_complete(p))
            self.table.setCellWidget(row_position, 8, move_complete_btn)

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

    def move_to_active(self, project):
        project.status = "Active"
        self.db.update_project(project)
        self.load_projects()
        QMessageBox.information(self, "Status Updated", f"Project '{project.name}' moved to Active.")

    def move_to_complete(self, project):
        project.status = "Complete"
        self.db.update_project(project)
        self.load_projects()
        QMessageBox.information(self, "Status Updated", f"Project '{project.name}' moved to Complete.")
