# main.py
import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QMessageBox, QShortcut
from PyQt5.QtGui import QKeySequence
from PyQt5.QtCore import Qt
from database import Database
from gui.overview_tab import OverviewTab
from gui.detailed_view_tab import DetailedViewTab
from gui.completed_projects_tab import CompletedProjectsTab
from gui.finished_projects_tab import FinishedProjectsTab

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
        self.detailed_view_tab = DetailedViewTab(self.db)
        self.completed_projects_tab = CompletedProjectsTab(self.db)
        self.finished_projects_tab = FinishedProjectsTab(self.db)

        self.tabs.addTab(self.overview_tab, "Project Overview")
        self.tabs.addTab(self.detailed_view_tab, "Detailed Project View")
        self.tabs.addTab(self.completed_projects_tab, "Completed Projects")
        self.tabs.addTab(self.finished_projects_tab, "Finished Projects")

        self.setup_shortcuts()

    def setup_shortcuts(self):
        # Alt+1 to Alt+4 for tab navigation
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
