# main.py
import sys
import os
import shutil
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QMessageBox, QShortcut, QAction, QFileDialog
)
from PyQt5.QtGui import QKeySequence
from PyQt5.QtCore import Qt
from database import Database
from gui.overview_tab import OverviewTab
from gui.completed_projects_tab import CompletedProjectsTab
from gui.finished_projects_tab import FinishedProjectsTab
from gui.detailed_view_tab import DetailedViewTab

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Boligventilasjon Project Management")
        self.resize(1200, 800)

        self.db = Database()

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Initialize tabs in the new order
        self.overview_tab = OverviewTab(self.db)
        self.completed_projects_tab = CompletedProjectsTab(self.db)
        self.finished_projects_tab = FinishedProjectsTab(self.db)
        self.detailed_view_tab = DetailedViewTab(self.db)

        self.tabs.addTab(self.overview_tab, "Project Overview")
        self.tabs.addTab(self.completed_projects_tab, "Completed Projects")
        self.tabs.addTab(self.finished_projects_tab, "Finished Projects")
        self.tabs.addTab(self.detailed_view_tab, "Detailed Project View")

        self.setup_menu_bar()
        self.setup_shortcuts()

    def setup_menu_bar(self):
        menu_bar = self.menuBar()

        # File Menu
        file_menu = menu_bar.addMenu("File")

        # Setup Template Action
        setup_template_action = QAction("Setup Template", self)
        setup_template_action.triggered.connect(self.setup_template)
        file_menu.addAction(setup_template_action)

        # Shortcuts Menu
        shortcuts_menu = menu_bar.addMenu("Shortcuts")
        # You can add shortcut-related actions here if needed

    def setup_template(self):
        """
        Handles the Setup Template functionality:
        - Creates the 'Template' folder if it doesn't exist.
        - Prompts the user to select 'Innregulering.xlsx' and 'Sjekkliste.xlsx' files.
        - Copies the selected files into the 'Template' folder.
        """
        # Define the Template directory path
        script_dir = os.path.dirname(os.path.abspath(__file__))
        template_dir = os.path.join(script_dir, "gui", "Template")

        # Create 'Template' folder if it doesn't exist
        if not os.path.exists(template_dir):
            try:
                os.makedirs(template_dir)
                QMessageBox.information(self, "Template Folder Created", f"'Template' folder created at:\n{template_dir}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to create 'Template' folder:\n{str(e)}")
                return
        else:
            QMessageBox.information(self, "Template Folder Exists", f"'Template' folder already exists at:\n{template_dir}")

        # Prompt user to select 'Innregulering.xlsx'
        innregulering_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select 'Innregulering.xlsx' Template File",
            "",
            "Excel Files (*.xlsx)"
        )

        if not innregulering_path:
            QMessageBox.warning(self, "Operation Cancelled", "No 'Innregulering.xlsx' file selected.")
            return

        # Validate selected file name
        if os.path.basename(innregulering_path).lower() != "innregulering.xlsx":
            QMessageBox.warning(self, "Invalid File", "Please select a file named 'Innregulering.xlsx'.")
            return

        # Prompt user to select 'Sjekkliste.xlsx'
        sjekkliste_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select 'Sjekkliste.xlsx' Template File",
            "",
            "Excel Files (*.xlsx)"
        )

        if not sjekkliste_path:
            QMessageBox.warning(self, "Operation Cancelled", "No 'Sjekkliste.xlsx' file selected.")
            return

        # Validate selected file name
        if os.path.basename(sjekkliste_path).lower() != "sjekkliste.xlsx":
            QMessageBox.warning(self, "Invalid File", "Please select a file named 'Sjekkliste.xlsx'.")
            return

        # Copy the selected files into the 'Template' folder
        try:
            shutil.copy(innregulering_path, os.path.join(template_dir, "Innregulering.xlsx"))
            shutil.copy(sjekkliste_path, os.path.join(template_dir, "Sjekkliste.xlsx"))
            QMessageBox.information(self, "Success", f"Templates have been set up successfully in:\n{template_dir}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to copy template files:\n{str(e)}")

    def setup_shortcuts(self):
        # Update shortcuts to reflect new tab order
        shortcut1 = QShortcut(QKeySequence("Alt+1"), self)
        shortcut1.activated.connect(lambda: self.tabs.setCurrentIndex(0))

        shortcut2 = QShortcut(QKeySequence("Alt+2"), self)
        shortcut2.activated.connect(lambda: self.tabs.setCurrentIndex(1))

        shortcut3 = QShortcut(QKeySequence("Alt+3"), self)
        shortcut3.activated.connect(lambda: self.tabs.setCurrentIndex(2))

        shortcut4 = QShortcut(QKeySequence("Alt+4"), self)
        shortcut4.activated.connect(lambda: self.tabs.setCurrentIndex(3))

    def closeEvent(self, event):
        self.db.close()
        event.accept()

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
