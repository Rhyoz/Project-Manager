# gui/completed_projects_tab.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QMessageBox
from PyQt5.QtCore import Qt
from utils import sanitize_filename
import os

class CompletedProjectsTab(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Projects Table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Project Name",
            "Project Number",
            "Start Date",
            "End Date",
            "Status",
            "Move to Active",
            "Move to Finished"
        ])
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.layout.addWidget(self.table)

        self.load_projects()

    def load_projects(self):
        self.table.setRowCount(0)
        projects = self.db.load_projects(status="Complete")
        for project in projects:
            row_position = self.table.rowCount()
            self.table.insertRow(row_position)

            self.table.setItem(row_position, 0, QTableWidgetItem(project.name))
            self.table.setItem(row_position, 1, QTableWidgetItem(project.number))
            self.table.setItem(row_position, 2, QTableWidgetItem(project.start_date))
            self.table.setItem(row_position, 3, QTableWidgetItem(project.end_date if project.end_date else ""))
            self.table.setItem(row_position, 4, QTableWidgetItem(project.status))

            # Move to Active Button
            move_active_btn = QPushButton("Active")
            move_active_btn.setStyleSheet("background-color: yellow")
            move_active_btn.clicked.connect(lambda checked, p=project: self.move_to_active(p))
            self.table.setCellWidget(row_position, 5, move_active_btn)

            # Move to Finished Button
            move_finished_btn = QPushButton("Finished")
            move_finished_btn.setStyleSheet("background-color: yellow")
            move_finished_btn.clicked.connect(lambda checked, p=project: self.move_to_finished(p))
            self.table.setCellWidget(row_position, 6, move_finished_btn)

    def move_to_active(self, project):
        project.status = "Active"
        self.db.update_project(project)
        self.load_projects()
        QMessageBox.information(self, "Status Updated", f"Project '{project.name}' moved to Active.")

    def move_to_finished(self, project):
        project.status = "Finished"
        self.db.update_project(project)
        self.load_projects()
        QMessageBox.information(self, "Status Updated", f"Project '{project.name}' moved to Finished.")
