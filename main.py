# File: main.py

import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QMessageBox, QFileDialog
from database import Database
from gui.overview_tab import OverviewTab
from gui.completed_projects_tab import CompletedProjectsTab
from gui.finished_projects_tab import FinishedProjectsTab
from gui.detailed_view_tab import DetailedViewTab
from logger import get_logger

logger = get_logger(__name__)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Boligventilasjon Project Management")
        self.resize(1200, 800)

        self.db = Database()

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Initialize tabs
        self.overview_tab = OverviewTab(self.db)
        self.completed_projects_tab = CompletedProjectsTab(self.db)
        self.finished_projects_tab = FinishedProjectsTab(self.db)
        self.detailed_view_tab = DetailedViewTab(self.db)

        self.tabs.addTab(self.overview_tab, "  Project Overview  ")
        self.tabs.addTab(self.completed_projects_tab, "  Completed Projects  ")
        self.tabs.addTab(self.finished_projects_tab, "  Finished Projects  ")
        self.tabs.addTab(self.detailed_view_tab, "  Detailed Project View  ")

        self.setup_menu_bar()
        self.apply_stylesheet()

    def setup_menu_bar(self):
        menu_bar = self.menuBar()

        # File Menu
        file_menu = menu_bar.addMenu("File")

        # Setup Template Action
        setup_template_action = file_menu.addAction("Setup Template")
        setup_template_action.triggered.connect(self.setup_template)

    def setup_template(self):
        """
        Handles the Setup Template functionality:
        - Creates the 'Template' folder if it doesn't exist.
        - Prompts the user to select 'Innregulering.docx' and 'Sjekkliste.docx' files.
        - Copies the selected files into the 'Template' folder.
        """
        from utils import get_template_dir
        from shutil import copy

        template_dir = get_template_dir()

        # Create 'Template' folder if it doesn't exist
        if not os.path.exists(template_dir):
            try:
                os.makedirs(template_dir)
                QMessageBox.information(self, "Template Folder Created", f"'Template' folder created at:\n{template_dir}")
                logger.info(f"Created template directory at {template_dir}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to create 'Template' folder:\n{str(e)}")
                logger.error(f"Failed to create template directory: {e}")
                return
        else:
            QMessageBox.information(self, "Template Folder Exists", f"'Template' folder already exists at:\n{template_dir}")
            logger.info(f"Template directory already exists at {template_dir}")

        # Prompt user to select 'Innregulering.docx'
        innregulering_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select 'Innregulering.docx' Template File",
            "",
            "Word Documents (*.docx)"
        )

        if not innregulering_path:
            QMessageBox.warning(self, "Operation Cancelled", "No 'Innregulering.docx' file selected.")
            logger.warning("User cancelled selecting 'Innregulering.docx'")
            return

        # Validate selected file name
        if os.path.basename(innregulering_path).lower() != "innregulering.docx":
            QMessageBox.warning(self, "Invalid File", "Please select a file named 'Innregulering.docx'.")
            logger.warning("User selected an invalid 'Innregulering.docx' file.")
            return

        # Prompt user to select 'Sjekkliste.docx'
        sjekkliste_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select 'Sjekkliste.docx' Template File",
            "",
            "Word Documents (*.docx)"
        )

        if not sjekkliste_path:
            QMessageBox.warning(self, "Operation Cancelled", "No 'Sjekkliste.docx' file selected.")
            logger.warning("User cancelled selecting 'Sjekkliste.docx'")
            return

        # Validate selected file name
        if os.path.basename(sjekkliste_path).lower() != "sjekkliste.docx":
            QMessageBox.warning(self, "Invalid File", "Please select a file named 'Sjekkliste.docx'.")
            logger.warning("User selected an invalid 'Sjekkliste.docx' file.")
            return

        # Copy the selected files into the 'Template' folder
        try:
            copy(innregulering_path, os.path.join(template_dir, "Innregulering.docx"))
            copy(sjekkliste_path, os.path.join(template_dir, "Sjekkliste.docx"))
            QMessageBox.information(self, "Success", f"Templates have been set up successfully in:\n{template_dir}")
            logger.info("Templates copied successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to copy template files:\n{str(e)}")
            logger.error(f"Failed to copy templates: {e}")

    def apply_stylesheet(self):
        """
        Applies a custom stylesheet to highlight the selected tab with a light blueish color
        and ensures bold text fits within the tab boundaries.
        Adds spacing only before the last tab.
        """
        stylesheet = """
        QTabWidget::pane { /* The tab widget frame */
            border-top: 2px solid #C2C7CB;
        }

        /* Style the tab using the tab selector */
        QTabBar::tab {
            background: lightgray;
            border: 1px solid #C4C4C3;
            padding: 10px;
            margin-right: 2px;
            min-width: 120px; /* Increased to accommodate bold text with spaces */
        }

        /* Style the selected tab */
        QTabBar::tab:selected {
            background: #ADD8E6; /* Light Blue */
            font-weight: bold;
        }

        /* Optional: Hover effect */
        QTabBar::tab:hover {
            background: #D3D3D3; /* Light Grey */
        }
        """
        self.tabs.setStyleSheet(stylesheet)

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
